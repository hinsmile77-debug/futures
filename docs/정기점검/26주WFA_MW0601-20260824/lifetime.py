# -*- coding: utf-8 -*-
"""[MW0601] 피처 수명(persistence) 산출 — 순수 라이브 전용, 읽기 전용 진단.

사용자 지시(2026-08-24): "라이브 데이터만으로 피처별 수명을 산출. 장시작 후 시간대별로
각 피처가 매분 상승 후 상승 지속시간, 하락 후 하락 지속시간을 뽑는다."
목적: 피처를 호라이즌별로 나눌 수 있는가 + 그것이 이득인가에 대한 통계적 근거.

## 척도 3종 (하나로는 왜곡된다)

L_raw  분 단위 방향 런 길이 — 사용자가 요청한 그대로. delta=0(동률)은 런을 끊는다.
       주의: 동률 비율이 높은 피처(macro_* 99.9%)는 구조적으로 1에 붙는다. 그래서 ->
L_chg  변화 이벤트 압축 런 — 동률을 제거하고 "값이 바뀔 때 같은 방향으로 계속
       바뀌는가"를 잰다. 단위는 분이 아니라 **변화 횟수**다. 저빈도 피처 공정 비교용.
tau    자기상관 반감기 — 레벨 ACF가 1/e 아래로 내려가는 첫 lag(분). 부호가 아니라
       값의 연속적 기억을 잰다. 셋 중 노이즈에 가장 둔감.

## 널(null) 2종 — 필수

455차 N3 방법론. Hurst 사례(진짜 랜덤워크도 H=0.33으로 읽힘)가 보여주듯 절대값만으로는
아무 말도 못 한다. iid에서도 평균 상승런은 약 1.5분이다.
  널A shuffle         시간구조 완전 파괴 -> "시간 구조가 있는가"
  널B phase_randomize 진폭스펙트럼(=선형 자기상관) 보존, 위상만 파괴
                      -> "선형 자기상관을 넘는 방향성 구조인가"

## 경계 규약
· 일 경계에서 런을 끊는다(오버나이트 갭).
· 일내 1분이 아닌 간격에서도 끊는다(실측 55건). 안 끊으면 구멍 건너 런이 이어진다.
· NaN 증분은 런을 끊는다 — 미측정을 0으로 만들지 않는다(계측 4원칙 2).
· 런의 시간대 버킷은 **시작 시각** 기준.
"""
from __future__ import print_function
import io
import json
import math
import os
import sys
from collections import defaultdict, OrderedDict
from datetime import datetime

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix
from scripts.noise_benchmark import phase_randomize, shuffle_column

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live

BUCKETS = [("09:00-09:30", "09:00", "09:30"), ("09:30-10:30", "09:30", "10:30"),
           ("10:30-11:30", "10:30", "11:30"), ("11:30-13:00", "11:30", "13:00"),
           ("13:00-14:00", "13:00", "14:00"), ("14:00-15:10", "14:00", "15:10")]
N_NULL = 20
MAX_LAG = 90


def segments(ts_list):
    """연속 1분 구간으로 분할 -> ([(date, [행인덱스...])], datetime목록)"""
    tt = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in ts_list]
    segs, cur = [], [0]
    for i in range(1, len(tt)):
        same_day = tt[i].date() == tt[i - 1].date()
        contig = (tt[i] - tt[i - 1]).total_seconds() == 60
        if same_day and contig:
            cur.append(i)
        else:
            segs.append(cur)
            cur = [i]
    segs.append(cur)
    return [(ts_list[s[0]][:10], s) for s in segs if len(s) >= 2], tt


def run_lengths(sign):
    """부호 배열(-1/0/+1, nan 포함) -> ((상승런길이, 시작위치), (하락런길이, 시작위치))"""
    up_len, up_pos, dn_len, dn_pos = [], [], [], []
    cur, n, start = 0, 0, 0

    def flush():
        if n > 0:
            if cur > 0:
                up_len.append(n)
                up_pos.append(start)
            else:
                dn_len.append(n)
                dn_pos.append(start)

    for i, s in enumerate(sign):
        if not np.isfinite(s) or s == 0:
            flush()
            cur, n = 0, 0
            continue
        if s == cur:
            n += 1
        else:
            flush()
            cur, n, start = s, 1, i
    flush()
    return (np.array(up_len), np.array(up_pos)), (np.array(dn_len), np.array(dn_pos))


def bucket_of(dt):
    hm = dt.strftime("%H:%M")
    for nm, a, b in BUCKETS:
        if a <= hm < b:
            return nm
    return None


def collect_runs(col, segs, tt, compress=False):
    """세그먼트별 런 수집 -> {(date, bucket, dir): [길이...]}"""
    out = defaultdict(list)
    for d, idxs in segs:
        v = col[idxs]
        if compress:
            ok = np.isfinite(v)
            if ok.sum() < 3:
                continue
            vi = np.array(idxs)[ok]
            vv = v[ok]
            keep = np.concatenate(([True], np.diff(vv) != 0))
            vv, vi = vv[keep], vi[keep]
            if vv.size < 3:
                continue
            dv = np.diff(vv)
            pos_idx = vi[1:]
        else:
            dv = np.diff(v)
            pos_idx = np.array(idxs[1:])
        (ul, up), (dl, dp) = run_lengths(np.sign(dv))
        for lens, poss, tag in ((ul, up, "up"), (dl, dp, "dn")):
            for L, p in zip(lens, poss):
                b = bucket_of(tt[pos_idx[p]])
                if b:
                    out[(d, b, tag)].append(int(L))
    return out


def acf_halflife(col, segs, max_lag=MAX_LAG):
    """일자별 ACF 반감기(1/e 교차 lag). 상수/표본미달 세그먼트는 제외."""
    per_day = defaultdict(list)
    for d, idxs in segs:
        v = col[idxs]
        ok = np.isfinite(v)
        if ok.sum() < max_lag + 30:
            continue
        v = v[ok]
        v = v - v.mean()
        sd = v.std()
        if sd <= 0 or not np.isfinite(sd):
            continue
        n = v.size
        thr = 1.0 / math.e
        denom = float(np.dot(v, v))
        if denom <= 0:
            continue
        hl = None
        for k in range(1, min(max_lag, n - 10) + 1):
            if float(np.dot(v[:-k], v[k:])) / denom < thr:
                hl = k
                break
        per_day[d].append(float(hl) if hl is not None else float(max_lag))
    vals = [np.mean(x) for x in per_day.values() if x]
    return (float(np.mean(vals)), len(vals)) if vals else (float("nan"), 0)


def daily_mean_table(runs, tag):
    """{(date,bucket,dir):[len]} -> {bucket: 일자평균배열}"""
    by = defaultdict(lambda: defaultdict(list))
    for (d, b, t), v in runs.items():
        if t == tag:
            by[b][d].extend(v)
    return {b: np.array([np.mean(v) for v in dd.values() if v]) for b, dd in by.items()}


def main():
    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    segs, tt = segments(ts_list)
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    P("=" * 104)
    P("[MW0601] 피처 수명(persistence) 산출 — 순수 라이브 전용")
    P("=" * 104)
    P("관찰창 %s ~ %s · %d거래일 · %d행 · 피처 %d개 · 연속세그먼트 %d개"
      % (dates[0], dates[-1], len(dates), len(ts_list), len(names), len(segs)))
    P("세그먼트 길이 중앙값 %d분 (일 경계 + 일내 1분 아닌 간격에서 분할)"
      % int(np.median([len(s) for _, s in segs])))
    P("널 %d회 x 2종(shuffle / phase_randomize) · ACF 최대 lag %d분" % (N_NULL, MAX_LAG))

    rng = np.random.RandomState(20260824)
    result = OrderedDict()

    P("")
    for j, nm in enumerate(names):
        col = X[:, j].astype(np.float64)
        fin = np.isfinite(col)
        dv_all = np.diff(col[fin]) if fin.sum() > 1 else np.array([])
        tie = float(np.mean(dv_all == 0)) if dv_all.size else 1.0

        raw = collect_runs(col, segs, tt, compress=False)
        chg = collect_runs(col, segs, tt, compress=True)
        tau, tau_n = acf_halflife(col, segs)

        null_s, null_p = [], []
        for _ in range(N_NULL):
            for fn, acc in ((shuffle_column, null_s), (phase_randomize, null_p)):
                r = collect_runs(fn(col, rng), segs, tt, compress=False)
                allv = [x for _k, v in r.items() for x in v]
                acc.append(np.mean(allv) if allv else np.nan)

        allraw = [x for _k, v in raw.items() for x in v]
        allchg = [x for _k, v in chg.items() for x in v]
        up, dn = daily_mean_table(raw, "up"), daily_mean_table(raw, "dn")
        cup, cdn = daily_mean_table(chg, "up"), daily_mean_table(chg, "dn")

        result[nm] = dict(
            tie=tie, tau=tau, tau_n=tau_n,
            L_raw=float(np.mean(allraw)) if allraw else float("nan"),
            L_chg=float(np.mean(allchg)) if allchg else float("nan"),
            n_runs=len(allraw), n_runs_chg=len(allchg),
            null_shuf=float(np.nanmean(null_s)), null_shuf_sd=float(np.nanstd(null_s)),
            null_phase=float(np.nanmean(null_p)), null_phase_sd=float(np.nanstd(null_p)),
            up={b: [float(np.mean(a)), int(len(a))] for b, a in up.items() if len(a)},
            dn={b: [float(np.mean(a)), int(len(a))] for b, a in dn.items() if len(a)},
            cup={b: [float(np.mean(a)), int(len(a))] for b, a in cup.items() if len(a)},
            cdn={b: [float(np.mean(a)), int(len(a))] for b, a in cdn.items() if len(a)},
            up_daily={b: [float(x) for x in a] for b, a in up.items() if len(a)},
            dn_daily={b: [float(x) for x in a] for b, a in dn.items() if len(a)},
        )
        if (j + 1) % 20 == 0:
            P("  ... %d/%d 피처 완료" % (j + 1, len(names)))

    def _ser(o):
        if isinstance(o, float) and math.isnan(o):
            return None
        if isinstance(o, (np.floating,)):
            v = float(o)
            return None if math.isnan(v) else v
        if isinstance(o, (np.integer,)):
            return int(o)
        raise TypeError(repr(type(o)))

    with open("lifetime_raw.json", "w", encoding="utf-8") as f:
        json.dump({"dates": dates, "n_rows": len(ts_list), "result": result},
                  f, ensure_ascii=False, default=_ser)
    P("\n산출 완료 -> lifetime_raw.json (%d피처)" % len(result))
    with open("lifetime_stage1.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())


if __name__ == "__main__":
    main()
