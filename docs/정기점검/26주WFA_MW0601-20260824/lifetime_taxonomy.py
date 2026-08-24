# -*- coding: utf-8 -*-
"""[MW0601] 피처 유형 분류 + 데이터 정제 — tau 검정 **전에** 반드시 거치는 단계.

사용자 지시(2026-08-24): "우선 피쳐 분류가 필요하다. 상수형·누적형 등 decay에
의존하지 않는 피쳐는 분류해서 제외하고, 3종 데이터 제외 등 데이터 정제를 하고 진행."

## 왜 분류가 먼저인가

tau(ACF 반감기)는 **정상(stationary) 평균회귀 계열의 기억 길이**를 재는 양이다.
그 전제가 깨진 계열에 tau를 재면 숫자는 나오지만 **다른 것을 잰다**:

  · 상수형   -> ACF가 1에 붙어 tau=상한. "기억이 길다"가 아니라 "변하지 않는다".
  · 누적형   -> ACF가 천천히 감소. 재는 것은 기억이 아니라 **추세 기울기**.
  · 계단형   -> 재는 것은 시장 기억이 아니라 **원천 갱신 주기**.
  · 결정론형 -> 시각의 함수. 재는 것은 **격자 자체**.

초판(§14)은 이 분류 없이 86피처 전부에 tau를 매겼다. `institution_futures_net`
tau=47.8분, `foreign_futures_net` 47.8분이 상위에 올랐는데 둘 다 **일중 누적** 계열이다.

## 분류 규칙 (기계적 · 우선순위 순서대로 적용)

  D 결정론형   같은 hh:mm의 날짜간 sd / 전체 sd < 0.05
  B 이진/범주형 전체 고유값 <= 5
  C 상수/준상수 동률 >= 0.95  또는 일별 평균 고유값 <= 3
  S 계단/저빈도 값 변화 간격 중앙값 >= 5분
  I 누적/비정상 일중 추세 R^2 중앙값 >= 0.50  또는 ACF(1) >= 0.99  또는 VR(10) >= 2.0
  N 정상 연속형 위 어디에도 안 걸림  <- **decay 검정 적격**

## 3종 데이터 정제 (N 대상 — 26주 재검증 §13의 3종 취약점)

  ① 팻테일   초과첨도 · 최대 |z| · winsorize(1%) 전후 tau 변화
  ② 동률     tie 비율
  ③ 점질량   최빈값 질량 비율

정제는 **제외가 아니라 표기**를 기본으로 한다 — 어느 피처가 어떤 취약점을 갖는지
남겨야 tau 해석 시 붙일 수 있다. 단 극단(점질량 >= 0.50 등)은 적격에서 내린다.
"""
from __future__ import print_function

import io
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

_ROOT = r"C:\Users\82108\PycharmProjects\futures"
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from utils.dll_bootstrap import ensure_conda_dll_path

ensure_conda_dll_path()
from scripts.core_feature_discovery import build_matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_only import load_live
from lifetime_lib import (GRID_N, column_to_matrix, to_daily_grid, trend_r2,
                          acf_nan, variance_ratio)

# 분류 임계 (사전 고정 — 결과를 보고 조정하지 않는다)
TH_DET_SD = 0.05
TH_BIN_UNIQ = 5
TH_CONST_TIE = 0.95
TH_CONST_UNIQ = 3.0
TH_STEP_GAP = 5.0
TH_TREND_R2 = 0.50
TH_ACF1 = 0.99
TH_VR10 = 2.0
# 정제 임계
TH_POINTMASS = 0.50
TH_KURT = 20.0


def main():
    L = io.StringIO()

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        L.write(s + "\n")

    feats, closes, dates = load_live()
    names, X, ts_list = build_matrix(feats, verbose=False)
    days, di, gi = to_daily_grid(ts_list)
    nd = len(days)

    P("=" * 112)
    P("[MW0601] 피처 유형 분류 + 데이터 정제 — 순수 라이브 %d거래일 (%s ~ %s)"
      % (nd, days[0], days[-1]))
    P("=" * 112)
    P("대상 %d피처 · 격자 09:00~15:30 (%d분) · 하루 단위 정렬, 구멍은 NaN 유지"
      % (len(names), GRID_N))

    rec = {}
    for j, nm in enumerate(names):
        M = column_to_matrix(X[:, j].astype(np.float64), di, gi, nd)
        finite = M[np.isfinite(M)]
        if finite.size < 100:
            rec[nm] = dict(kind="X", why="유효 관측 %d개 < 100" % finite.size)
            continue

        # --- 기술 통계 -------------------------------------------------
        uniq_all = int(np.unique(finite).size)
        uniq_day = float(np.mean([np.unique(r[np.isfinite(r)]).size
                                  for r in M if np.isfinite(r).sum() >= 10] or [0]))
        d1 = np.concatenate([np.diff(r[np.isfinite(r)]) for r in M
                             if np.isfinite(r).sum() >= 2]) if nd else np.array([])
        tie = float(np.mean(d1 == 0)) if d1.size else 1.0

        # 값 변화 간격(분) 중앙값 — 계단/저빈도 갱신 탐지
        gaps = []
        for r in M:
            ok = np.isfinite(r)
            if ok.sum() < 10:
                continue
            pos = np.where(ok)[0]
            v = r[ok]
            ch = pos[1:][np.diff(v) != 0]
            if ch.size >= 2:
                gaps.append(np.median(np.diff(ch)))
        gap_med = float(np.median(gaps)) if gaps else float("inf")

        # 결정론성 — 같은 시각의 날짜간 변동
        with np.errstate(invalid="ignore"):
            col_sd = np.nanstd(M, axis=0)
        cnt = np.isfinite(M).sum(axis=0)
        col_sd = col_sd[cnt >= max(5, nd // 3)]
        tot_sd = float(np.nanstd(finite))
        det_ratio = (float(np.nanmean(col_sd)) / tot_sd) if tot_sd > 0 and col_sd.size else float("nan")

        # 비정상성 3종
        r2 = [trend_r2(r) for r in M]
        r2 = float(np.nanmedian([x for x in r2 if np.isfinite(x)])) if any(
            np.isfinite(x) for x in r2) else float("nan")
        a1 = []
        for r in M:
            a = acf_nan(r, max_lag=2)
            if np.isfinite(a[1]):
                a1.append(a[1])
        acf1 = float(np.median(a1)) if a1 else float("nan")
        vr = [variance_ratio(r, 10) for r in M]
        vr = float(np.nanmedian([x for x in vr if np.isfinite(x)])) if any(
            np.isfinite(x) for x in vr) else float("nan")

        # 정제 3종
        z = (finite - finite.mean()) / finite.std() if finite.std() > 0 else finite * 0
        kurt = float(((z ** 4).mean() - 3.0)) if finite.std() > 0 else float("nan")
        maxz = float(np.abs(z).max()) if finite.std() > 0 else float("nan")
        vals, cts = np.unique(finite, return_counts=True)
        pmass = float(cts.max() / finite.size)

        # --- 분류 (우선순위) -------------------------------------------
        if np.isfinite(det_ratio) and det_ratio < TH_DET_SD:
            kind, why = "D", "결정론형 (날짜간sd/전체sd=%.3f)" % det_ratio
        elif uniq_all <= TH_BIN_UNIQ:
            kind, why = "B", "이진/범주형 (고유값 %d)" % uniq_all
        elif tie >= TH_CONST_TIE or uniq_day <= TH_CONST_UNIQ:
            kind, why = "C", "상수/준상수 (동률 %.1f%%, 일평균 고유값 %.1f)" % (tie * 100, uniq_day)
        elif gap_med >= TH_STEP_GAP:
            kind, why = "S", "계단/저빈도갱신 (변화간격 중앙값 %.1f분)" % gap_med
        elif (np.isfinite(r2) and r2 >= TH_TREND_R2) or \
             (np.isfinite(acf1) and acf1 >= TH_ACF1) or \
             (np.isfinite(vr) and vr >= TH_VR10):
            bits = []
            if np.isfinite(r2) and r2 >= TH_TREND_R2:
                bits.append("추세R2=%.2f" % r2)
            if np.isfinite(acf1) and acf1 >= TH_ACF1:
                bits.append("ACF1=%.4f" % acf1)
            if np.isfinite(vr) and vr >= TH_VR10:
                bits.append("VR10=%.1f" % vr)
            kind, why = "I", "누적/비정상 (%s)" % ", ".join(bits)
        else:
            kind, why = "N", "정상 연속형"

        rec[nm] = dict(kind=kind, why=why, tie=tie, uniq_all=uniq_all,
                       uniq_day=uniq_day, gap_med=gap_med, det_ratio=det_ratio,
                       trend_r2=r2, acf1=acf1, vr10=vr,
                       kurt=kurt, maxz=maxz, pmass=pmass)

    # ── 분류 결과 ────────────────────────────────────────────────
    LABEL = {"D": "결정론형", "B": "이진/범주형", "C": "상수/준상수",
             "S": "계단/저빈도갱신", "I": "누적/비정상", "N": "정상 연속형",
             "X": "표본 미달"}
    P("\n" + "=" * 112)
    P("[1] 유형 분류 결과")
    P("=" * 112)
    for k in ("D", "B", "C", "S", "I", "N", "X"):
        ns = [n for n in names if rec.get(n, {}).get("kind") == k]
        if not ns:
            continue
        mark = "  <== decay 검정 적격" if k == "N" else "  (제외)"
        P("\n%s %s — %d개%s" % (k, LABEL[k], len(ns), mark))
        for n in sorted(ns):
            P("    %-34s %s" % (n[:34], rec[n]["why"]))

    elig = [n for n in names if rec.get(n, {}).get("kind") == "N"]
    P("\n" + "-" * 112)
    P("적격(N) %d / %d — 나머지 %d개는 tau가 '기억'이 아닌 다른 양을 재므로 제외"
      % (len(elig), len(names), len(names) - len(elig)))

    # ── 초판(§14) 상위 피처가 어디로 갔나 ─────────────────────────
    P("\n" + "=" * 112)
    P("[2] §14 초판에서 tau 상위였던 피처의 재분류 — 무엇이 걸러졌나")
    P("=" * 112)
    try:
        old = json.load(open("lifetime_raw.json", encoding="utf-8"))["result"]
        top = sorted([(v.get("tau") or -1, n) for n, v in old.items()], reverse=True)[:15]
        P("%-34s %8s  %s" % ("피처", "§14 tau", "재분류"))
        P("-" * 112)
        for t, n in top:
            k = rec.get(n, {}).get("kind", "?")
            P("%-34s %8.1f  %s %s" % (n[:34], t, k, LABEL.get(k, "?")))
    except Exception as e:
        P("   (초판 대조 생략: %s)" % e)

    # ── 3종 정제 ─────────────────────────────────────────────────
    P("\n" + "=" * 112)
    P("[3] 데이터 정제 3종 — 적격(N) %d개 대상 (§13 취약점)" % len(elig))
    P("=" * 112)
    P("%-34s %9s %8s %9s  %s" % ("피처", "초과첨도", "최대|z|", "점질량", "플래그"))
    P("-" * 112)
    drop_clean, flags = [], {}
    for n in sorted(elig, key=lambda x: -rec[x]["pmass"]):
        r = rec[n]
        f = []
        if np.isfinite(r["kurt"]) and r["kurt"] >= TH_KURT:
            f.append("팻테일")
        if r["tie"] >= 0.30:
            f.append("동률%.0f%%" % (r["tie"] * 100))
        if r["pmass"] >= TH_POINTMASS:
            f.append("점질량%.0f%%" % (r["pmass"] * 100))
        flags[n] = f
        hard = r["pmass"] >= TH_POINTMASS
        if hard:
            drop_clean.append(n)
        P("%-34s %9.1f %8.1f %8.1f%%  %s%s"
          % (n[:34], r["kurt"], r["maxz"], r["pmass"] * 100,
             ", ".join(f) or "-", "  <== 제외" if hard else ""))

    final = [n for n in elig if n not in drop_clean]
    P("\n" + "-" * 112)
    P("정제 후 최종 적격 **%d개** (점질량>=%.0f%% 로 %d개 추가 제외)"
      % (len(final), TH_POINTMASS * 100, len(drop_clean)))
    P("팻테일·동률 플래그는 **제외하지 않고 표기**한다 — tau 해석 시 함께 읽을 것.")
    P("\n최종 적격 목록:")
    for i in range(0, len(final), 3):
        P("   " + "".join("%-36s" % x for x in sorted(final)[i:i + 3]))

    json.dump(dict(days=[days[0], days[-1]], n_days=nd,
                   record={n: {k: (None if isinstance(v, float) and not np.isfinite(v) else v)
                               for k, v in rec[n].items()} for n in rec},
                   eligible=sorted(final), eligible_pre_clean=sorted(elig),
                   dropped_clean=sorted(drop_clean), flags=flags),
              open("lifetime_taxonomy.json", "w", encoding="utf-8"),
              ensure_ascii=False, default=float)
    with open("lifetime_taxonomy.txt", "w", encoding="utf-8") as f:
        f.write(L.getvalue())
    P("\n저장 -> lifetime_taxonomy.json / .txt")


if __name__ == "__main__":
    main()
