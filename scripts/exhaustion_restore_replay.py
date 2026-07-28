# -*- coding: utf-8 -*-
"""소진(exhaustion) 피처 복구 — 적용 전 영향 실측 하네스 (Phase 1 사전검증).

Phase 0 결론(`docs/미륵이고도화2/Phase0_검증결과_2026-07-27.md` §2-1): 소진 6종이
2026-05~07 전 기간 0인 원인은 `features/feature_builder.py:229-231`이 계산기에
누적 CVD 레벨 대신 정규화값(`cvd_norm`, 98.8%가 +1.0 포화)을 넘기기 때문이다.

이 스크립트는 **라이브 코드를 고치기 전에** 수정의 실제 효과를 원천 분봉으로
재현 측정한다. 측정 항목:

  M1. 소진 피처 발화율      — 현행 vs 수정안(입력만 교체) vs 수정안+마진
  M2. 탈진 레짐 발생 분수   — MicroRegimeClassifier 재현 (진입 차단 위험 계량)
  M3. MEAN_REVERSION 자격   — checklist 3_vwap MR 분기 충족 분수
  M4. 소진 발화 시점의 사후 수익률 — 신호에 실제 정보가 있는지 (방향성 검증)

**왜 M2가 중요한가**: 탈진 레짐이 켜지면 `main.py:5890-5903` RegimeChampGate가
챔피언 미승격을 이유로 진입을 차단한다(direction=0, grade=X). 즉 복구는 MR 진입을
열어주는 동시에 탈진 레짐 구간의 진입을 막는 양방향 효과를 가진다 — 배포 전 반드시
정량화해야 한다.

읽기 전용 — DB·설정·모델 어디에도 쓰지 않는다.

실행:
  python scripts/exhaustion_restore_replay.py            # 최근 60거래일
  python scripts/exhaustion_restore_replay.py --days 120
"""
from __future__ import print_function

import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict, deque

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from features.technical.cvd import CVDCalculator                      # noqa: E402
from features.technical.cvd_exhaustion import CvdExhaustionCalculator  # noqa: E402
from collection.macro.micro_regime import (                            # noqa: E402
    MicroRegimeClassifier, REGIME_EXHAUSTION,
)

RAW_DB = os.path.join(_ROOT, "data", "db", "raw_data.db")

MR_EXHAUSTION_MIN_WEAK = 0.60   # config/settings.py:1591
MR_EXHAUSTION_MIN = 0.70        # config/settings.py:1585


class MarginExhaustionCalculator(CvdExhaustionCalculator):
    """2순위 보완안: strict 비교를 분위 기반 마진으로 교체한 변형.

    포화 입력이 아니더라도 신저점/신고점의 strict 갱신은 드문 사건이라 발화가
    희소해질 수 있다. 최근 20봉의 하위/상위 분위를 문턱으로 쓰면 "극단 근처"까지
    포착 범위가 넓어진다. 1순위(입력 교체)만으로 발화율이 충분하면 불필요하다.
    """

    PCTL = 0.10

    def compute(self, cvd_raw, cvd_slope, volume):
        self._cvd_buf.append(float(cvd_raw))
        self._vol_buf.append(float(volume))
        bear = bull = 0.0
        if len(self._cvd_buf) >= self.CVD_WIN and len(self._vol_buf) >= 5:
            prev = list(self._cvd_buf)[:-1]
            avg_vol = sum(self._vol_buf) / len(self._vol_buf)
            prev_slope = self._slope_prev if self._slope_prev is not None else float(cvd_slope)
            accel = float(cvd_slope) - prev_slope
            surge = avg_vol > 0 and volume > avg_vol * self.VOL_MULT
            exh_val = min(volume / (avg_vol * 3.0), 1.0) if avg_vol > 0 else 0.5
            s = sorted(prev)
            k = max(0, int(len(s) * self.PCTL) - 1)
            lo, hi = s[k], s[len(s) - 1 - k]
            if cvd_raw <= lo and accel > 0 and surge:
                bear = exh_val
            if cvd_raw >= hi and accel < 0 and surge:
                bull = exh_val
        self._slope_prev = float(cvd_slope)
        return {
            "bear_exhaustion": round(bear, 4), "bull_exhaustion": round(bull, 4),
            "bear_exhaustion_signal": 1 if bear > 0 else 0,
            "bull_exhaustion_signal": 1 if bull > 0 else 0,
            "exhaustion": round(bear, 4), "exhaustion_signal": 1 if bear > 0 else 0,
        }


def load_bars(days):
    con = sqlite3.connect(RAW_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_candles ORDER BY d DESC LIMIT ?", (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    if not dates:
        return [], {}
    cur.execute(
        "SELECT ts, open, high, low, close, volume, buy_vol, sell_vol FROM raw_candles "
        "WHERE substr(ts,1,10) >= ? ORDER BY ts", (dates[0],))
    bars = cur.fetchall()
    cur.execute(
        "SELECT ts, features FROM raw_features WHERE substr(ts,1,10) >= ?", (dates[0],))
    feats = {}
    for ts, fj in cur.fetchall():
        try:
            feats[ts] = json.loads(fj)
        except Exception:
            pass
    con.close()
    return bars, feats


def run(days):
    bars, feats = load_bars(days)
    if not bars:
        print("raw_candles 데이터 없음")
        return 1
    print("분봉 %d개 (%s ~ %s), raw_features 조인 가능 %d개"
          % (len(bars), bars[0][0], bars[-1][0], len(feats)))
    bv_ok = sum(1 for b in bars if b[6] is not None and b[7] is not None)
    print("buy_vol/sell_vol 실측 보유 %d개 (%.1f%%) — 나머지는 바 기하학 프록시"
          % (bv_ok, 100.0 * bv_ok / len(bars)))

    variants = {
        "현행(cvd_norm 입력)":   {"calc": CvdExhaustionCalculator(), "raw_input": False, "cls": None},
        "①원시 CVD 입력만":      {"calc": CvdExhaustionCalculator(), "raw_input": True,  "cls": None},
        "②원시+분위마진":        {"calc": MarginExhaustionCalculator(), "raw_input": True, "cls": None},
        # ③ = 실제 배포판(features/technical/cvd_exhaustion.py detrend=True).
        #     EXHAUSTION_RESTORE_MODE="live" 전환 시 라이브에 적용될 바로 그 계산이다.
        "③배포판(원시+추세제거)": {"calc": CvdExhaustionCalculator(detrend=True),
                              "raw_input": True, "cls": None},
    }
    for v in variants.values():
        v["cls"] = MicroRegimeClassifier()
        v["fire"] = {"bear": 0, "bull": 0}
        v["vals"] = []
        v["regime"] = defaultdict(int)
        v["mr"] = 0
        v["mr_strong"] = 0
        v["fwd"] = []      # (방향, 사후수익률)

    cvd = CVDCalculator()
    cur_day = None
    closes = [float(b[4]) for b in bars]
    n_eval = 0

    for i, (ts, o, h, l, c, vol, bvol, svol) in enumerate(bars):
        day = ts[:10]
        if day != cur_day:
            cur_day = day
            cvd.reset_daily()
            for v in variants.values():
                v["calc"].reset_daily()
        c = float(c or 0.0); h = float(h or c); l = float(l or c); vol = float(vol or 0.0)
        if bvol is not None and svol is not None:
            buy_vol, sell_vol = float(bvol), float(svol)
        else:
            rng = max(h - l, 1e-9)
            buy_vol = vol * max(c - l, 0.0) / rng
            sell_vol = vol * max(h - c, 0.0) / rng

        cr = cvd.update_from_bar(close=c, buy_vol=buy_vol, sell_vol=sell_vol)
        norm_in = (float(cr.get("cvd_norm", 0.0)), float(cr.get("cvd_slope_norm", 0.0)))
        raw_in = (float(cr.get("cvd", 0.0)), float(cr.get("cvd_slope", 0.0)))

        f = feats.get(ts, {})
        vwap_pos = float(f.get("vwap_position", 0.0) or 0.0)
        n_eval += 1

        # 사후 수익률(10분) — 소진 신호의 방향성 검증용
        fwd = (closes[i + 10] - c) if i + 10 < len(closes) else None

        for name, v in variants.items():
            ci, si = (raw_in if v["raw_input"] else norm_in)
            r = v["calc"].compute(cvd_raw=ci, cvd_slope=si, volume=vol)
            be = float(r["bear_exhaustion"]); bu = float(r["bull_exhaustion"])
            if be > 0:
                v["fire"]["bear"] += 1
                v["vals"].append(be)
                if fwd is not None:
                    v["fwd"].append((+1, fwd))      # bear소진 → LONG MR 기대
            if bu > 0:
                v["fire"]["bull"] += 1
                v["vals"].append(bu)
                if fwd is not None:
                    v["fwd"].append((-1, fwd))      # bull소진 → SHORT MR 기대
            reg = v["cls"].push_1m_candle(
                high=h, low=l, close=c,
                bear_exhaustion=be, bull_exhaustion=bu, vwap_position=vwap_pos,
            )
            v["regime"][reg.get("regime")] += 1
            # checklist 3_vwap MR 분기 자격
            if (vwap_pos < -1.5 and be >= MR_EXHAUSTION_MIN_WEAK) or \
               (vwap_pos > 1.5 and bu >= MR_EXHAUSTION_MIN_WEAK):
                v["mr"] += 1
                if max(be, bu) >= MR_EXHAUSTION_MIN:
                    v["mr_strong"] += 1

    print()
    print("=" * 84)
    print("M1. 소진 피처 발화율 (전체 %d분봉)" % n_eval)
    print("=" * 84)
    print("  %-24s %10s %10s %10s %12s" % ("변형", "bear발화", "bull발화", "합계율", "값 중앙"))
    for name, v in variants.items():
        tot = v["fire"]["bear"] + v["fire"]["bull"]
        vals = sorted(v["vals"])
        med = vals[len(vals) // 2] if vals else float("nan")
        print("  %-24s %10d %10d %9.3f%% %12.4f"
              % (name, v["fire"]["bear"], v["fire"]["bull"], 100.0 * tot / n_eval, med))

    print()
    print("=" * 84)
    print("M2. 탈진 레짐 발생 분수 — RegimeChampGate 진입차단 위험 계량")
    print("=" * 84)
    for name, v in variants.items():
        tot = sum(v["regime"].values())
        ex = v["regime"].get(REGIME_EXHAUSTION, 0)
        dist = " ".join("%s=%.1f%%" % (k, 100.0 * n / tot)
                        for k, n in sorted(v["regime"].items(), key=lambda x: -x[1]))
        print("  %-24s 탈진 %d분 (%.3f%%)  | %s" % (name, ex, 100.0 * ex / tot, dist))

    print()
    print("=" * 84)
    print("M3. MEAN_REVERSION 자격 충족 분수 (checklist 3_vwap MR 분기)")
    print("=" * 84)
    for name, v in variants.items():
        print("  %-24s MR자격 %d분 (%.3f%%)  그중 강한MR(>=0.70) %d분"
              % (name, v["mr"], 100.0 * v["mr"] / n_eval, v["mr_strong"]))

    print()
    print("=" * 84)
    print("M4. 소진 발화 시점의 사후 10분 수익률 — 신호 방향성 검증")
    print("=" * 84)
    print("  (bear소진→LONG기대, bull소진→SHORT기대. 평균>0 이면 기대방향과 일치)")
    for name, v in variants.items():
        if not v["fwd"]:
            print("  %-24s 표본 없음" % name)
            continue
        pnl = [d * m for d, m in v["fwd"]]
        avg = sum(pnl) / len(pnl)
        win = sum(1 for x in pnl if x > 0) / float(len(pnl))
        print("  %-24s n=%-5d 평균 %+.4f pt  승률 %.3f" % (name, len(pnl), avg, win))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=60)
    args = ap.parse_args()
    sys.exit(run(args.days))
