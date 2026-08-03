"""[MW0601 421차] `[31]` reduce 연속배수 앵커 재도출 — 419차 P0 반영 후.

왜 재도출인가: 419차가 `TOXICITY_CANCEL_CHURN_CEILING`을 0.08 → 0.42로 재보정하며
코드 주석에 **"이 앵커는 재보정 전(cancel_stress 포화) 분포로 도출됐다. P0가 라이브에
반영되면 밴드 분포가 이동하므로 반드시 재도출할 것"** 이라고 스스로 예고했다.
2026-08-03 라이브 첫날 실측에서 `shadow_mult_mean`이 0.70 설계목표 대비 **0.8205**로
이탈해 그 예고가 현실이 됐다.

앵커의 목적은 **노출 중립**이다 — reduce 밴드 전체의 평균 배수가 현행 상수 0.70과
같아야, 나중에 손익이 바뀌었을 때 그것이 *등급화(밴드 내 차등)* 덕인지 *노출 증가*
탓인지 분리할 수 있다. 따라서 재도출은 "등급화 강도(span)는 그대로, 수준(level)만
이동"이 원칙이다.

**모집단 주의** — 원 앵커는 `reduce 밴드 봉`(n=1,703)에서 도출됐다. 08-03 실측
0.8205는 `게이트 이벤트`(n=20, 진입 시도가 게이트에 닿은 분봉만) 기준이라 모집단이
다르다. 이 스크립트는 **원 앵커와 같은 봉 모집단**으로 재도출한다.

재생 방법: `raw_features`에 성분 stress가 전부 저장돼 있어 ceiling만 갈아끼우면
과거 분봉의 score를 정확히 재구성할 수 있다(P0에 영향받는 성분은 cancel 하나뿐).
    new_cancel_stress = min(|cancel_churn_ratio| / ceiling_new, 1.0)
    new_score = atr*0.25 + spread*0.20 + flow*0.20 + queue*0.15 + new_cancel*0.20
score_ma는 window=20 롤링이며 `reset_daily()`로 매 거래일 초기화되므로 일자별로
따로 굴린다.

⚠ 이 스크립트는 상수를 **자동으로 고치지 않는다** — 권고값만 출력한다(§9).

실행: python scripts/toxicity_reduce_mult_anchor_rederive.py
"""
import json
import os
import sqlite3
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    TOXICITY_CANCEL_CHURN_CEILING,
    TOXICITY_REDUCE_MULT_SHADOW_HI,
    TOXICITY_REDUCE_MULT_SHADOW_LO,
)

RAW_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "data", "db", "raw_data.db")

# toxicity_gate.py / toxicity.py 와 동일해야 하는 상수 — 여기서 바꾸지 말 것.
BLOCK_THR = 0.45
REDUCE_THR = 0.28
SEVERE_SPREAD_TICKS = 8.0
MA_WINDOW = 20
TARGET_MEAN = 0.70          # 현행 실적용 상수 = 노출중립 목표
SINCE = "2026-07-20"


def _pct(v, q):
    if not v:
        return float("nan")
    s = sorted(v)
    i = min(int(q * (len(s) - 1)), len(s) - 1)
    return s[i]


def _mean(v):
    return sum(v) / len(v) if v else float("nan")


def load_bars(since=SINCE):
    con = sqlite3.connect(RAW_DB)
    out = []
    for ts, fj in con.execute(
            "SELECT ts, features FROM raw_features WHERE ts >= ? ORDER BY ts", (since,)):
        d = json.loads(fj)
        ccr = d.get("cancel_churn_ratio")
        if ccr is None:
            continue
        out.append({
            "ts": ts,
            "day": ts[:10],
            "atr": float(d.get("toxicity_atr_stress") or 0.0),
            "spread": float(d.get("toxicity_spread_stress") or 0.0),
            "flow": float(d.get("toxicity_flow_stress") or 0.0),
            "queue": float(d.get("toxicity_queue_stress") or 0.0),
            "ccr": abs(float(ccr)),
            "spread_ticks": float(d.get("spread_ticks") or 0.0),
            "live_score": d.get("toxicity_score"),
            "live_cancel": d.get("toxicity_cancel_stress"),
        })
    return out


def replay(bars, ceiling):
    """ceiling을 갈아끼워 score/score_ma를 재구성. reset_daily를 일자별로 반영."""
    hist, cur_day = deque(maxlen=MA_WINDOW), None
    for b in bars:
        if b["day"] != cur_day:
            hist.clear()
            cur_day = b["day"]
        cs = min(b["ccr"] / ceiling, 1.0)
        sc = (b["atr"] * 0.25 + b["spread"] * 0.20 + b["flow"] * 0.20
              + b["queue"] * 0.15 + cs * 0.20)
        sc = min(max(sc, 0.0), 1.0)
        hist.append(sc)
        b["cancel_stress"] = cs
        b["score"] = sc
        b["score_ma"] = sum(hist) / len(hist)
    return bars


def band_of(b):
    s, ma = b["score"], b["score_ma"]
    if s >= BLOCK_THR or ma >= (BLOCK_THR - 0.05):
        return "block"
    if s >= REDUCE_THR or ma >= (REDUCE_THR - 0.03) or b["spread_ticks"] >= SEVERE_SPREAD_TICKS:
        return "reduce"
    return "pass"


def t_of(b):
    """_reduce_mult_shadow의 밴드 내 위치 t — 코드와 동일 정의."""
    span = BLOCK_THR - REDUCE_THR
    pos = max(b["score"], b["score_ma"])
    return (min(max(pos, REDUCE_THR), BLOCK_THR) - REDUCE_THR) / span


def mult(t, hi, lo):
    return hi + (lo - hi) * t


def verify_replay(bars):
    """재생 정확성 자체검증 — P0가 이미 라이브인 날은 저장값과 일치해야 한다."""
    live_days = [b for b in bars if b["live_score"] is not None
                 and b["day"] >= "2026-08-03"]
    if not live_days:
        return None
    errs = [abs(b["score"] - float(b["live_score"])) for b in live_days]
    return len(live_days), max(errs), _mean(errs)


def main():
    bars = load_bars()
    if not bars:
        print("raw_features 데이터 없음")
        return 1

    print("=" * 84)
    print("[31] reduce 연속배수 앵커 재도출 — 421차")
    print("기간 %s ~ %s / 분봉 %d개 / 거래일 %d일"
          % (bars[0]["ts"][:10], bars[-1]["ts"][:10], len(bars),
             len({b["day"] for b in bars})))
    print("=" * 84)

    # ── 0. 재생 정확성 자체검증 ───────────────────────────────────────────
    replay(bars, TOXICITY_CANCEL_CHURN_CEILING)
    v = verify_replay(bars)
    if v:
        n, mx, av = v
        ok = mx < 1e-4
        print("\n[0] 재생 자체검증 (P0 라이브 반영일 저장값과 대조)")
        print("    n=%d  최대오차=%.2e  평균오차=%.2e  → %s"
              % (n, mx, av, "OK 재생 정확" if ok else "⚠ 불일치 — 아래 결과 신뢰 불가"))
        if not ok:
            print("    재생식이 라이브와 다르다. 성분/가중치 변경 여부를 먼저 확인할 것.")
            return 1

    # ── 1. 구/신 ceiling 밴드 분포 비교 ──────────────────────────────────
    print("\n[1] ceiling 변경에 따른 밴드 분포 이동 (봉 모집단)")
    print("    %-10s %8s %8s %8s   %s" % ("ceiling", "block", "reduce", "pass", "cancel포화"))
    dists = {}
    for name, ceil in (("0.08(구)", 0.08), ("%.2f(현행)" % TOXICITY_CANCEL_CHURN_CEILING,
                                            TOXICITY_CANCEL_CHURN_CEILING)):
        replay(bars, ceil)
        cnt = {"block": 0, "reduce": 0, "pass": 0}
        for b in bars:
            cnt[band_of(b)] += 1
        sat = sum(1 for b in bars if b["cancel_stress"] >= 0.999)
        n = len(bars)
        print("    %-10s %7.1f%% %7.1f%% %7.1f%%   %6.1f%%"
              % (name, 100 * cnt["block"] / n, 100 * cnt["reduce"] / n,
                 100 * cnt["pass"] / n, 100 * sat / n))
        dists[name] = cnt

    # 이후 계산은 현행 ceiling 기준
    replay(bars, TOXICITY_CANCEL_CHURN_CEILING)
    red = [b for b in bars if band_of(b) == "reduce"]
    if not red:
        print("\nreduce 밴드 표본 없음 — 재도출 불가")
        return 1

    # ── 2. 현행 앵커의 이탈 ──────────────────────────────────────────────
    hi0, lo0 = TOXICITY_REDUCE_MULT_SHADOW_HI, TOXICITY_REDUCE_MULT_SHADOW_LO
    ts = [t_of(b) for b in red]
    cur = [mult(t, hi0, lo0) for t in ts]
    print("\n[2] 현행 앵커 HI=%.2f / LO=%.2f 의 reduce 밴드 평균배수" % (hi0, lo0))
    print("    n=%d  평균=%.4f  (목표 %.2f, 이탈 %+.4f = %+.1f%%)"
          % (len(red), _mean(cur), TARGET_MEAN, _mean(cur) - TARGET_MEAN,
             100 * (_mean(cur) - TARGET_MEAN) / TARGET_MEAN))
    print("    p10=%.4f  p50=%.4f  p90=%.4f   E[t]=%.4f"
          % (_pct(cur, .10), _pct(cur, .50), _pct(cur, .90), _mean(ts)))

    # ── 3. 재도출 — 등급화 강도(span) 고정, 수준만 이동 ─────────────────
    span0 = hi0 - lo0
    et = _mean(ts)
    hi_new = TARGET_MEAN + span0 * et
    lo_new = hi_new - span0
    print("\n[3] 권고 — span(등급화 강도) %.2f 고정, 수준만 이동" % span0)
    print("    HI = 목표 + span×E[t] = %.2f + %.2f×%.4f = %.4f" % (TARGET_MEAN, span0, et, hi_new))
    print("    LO = HI - span                          = %.4f" % lo_new)
    chk = _mean([mult(t, hi_new, lo_new) for t in ts])
    print("    검산: 평균배수 = %.4f (목표 %.2f, 오차 %+.5f)" % (chk, TARGET_MEAN, chk - TARGET_MEAN))
    print("    권고 반올림값:  HI=%.2f  LO=%.2f" % (round(hi_new, 2), round(lo_new, 2)))
    chk_r = _mean([mult(t, round(hi_new, 2), round(lo_new, 2)) for t in ts])
    print("    반올림 후 평균 = %.4f (오차 %+.5f)" % (chk_r, chk_r - TARGET_MEAN))
    if round(hi_new, 2) > 1.0:
        print("    ⚠ HI > 1.0 — 밴드 하단에서 사이즈를 base보다 키우게 된다. 아래 대안 검토 필요.")

    # ── 4. 대안 — LO 고정 / HI 상한 1.0 ─────────────────────────────────
    print("\n[4] 대안 (선택지 비교)")
    hi_lofix = (TARGET_MEAN - lo0 * et) / (1 - et) if et < 1 else float("nan")
    print("    (a) LO=%.2f 고정, HI만 해 → HI=%.4f (span %.3f, 등급화 %s)"
          % (lo0, hi_lofix, hi_lofix - lo0,
             "강화" if hi_lofix - lo0 > span0 else "약화"))
    lo_hicap = (TARGET_MEAN - 1.0 * (1 - et)) / et if et > 0 else float("nan")
    print("    (b) HI=1.00 상한, LO만 해 → LO=%.4f (span %.3f)" % (lo_hicap, 1.0 - lo_hicap))

    # ── 5. 일자별 안정성 (313차 — 단일일 판정 금지) ─────────────────────
    print("\n[5] 일자별 E[t] 안정성 — 특정일 의존 여부 (313차)")
    days = sorted({b["day"] for b in red})
    per = []
    for d in days:
        sub = [t_of(b) for b in red if b["day"] == d]
        h = TARGET_MEAN + span0 * _mean(sub)
        per.append((d, len(sub), _mean(sub), h))
        print("    %s  n=%4d  E[t]=%.4f  → HI=%.4f" % (d, len(sub), _mean(sub), h))
    his = [p[3] for p in per]
    print("    일자별 HI 범위 %.4f ~ %.4f (폭 %.4f)" % (min(his), max(his), max(his) - min(his)))
    lo_o, hi_o = min(his), max(his)
    print("    → 전체표본 권고 HI=%.4f 가 일자범위 %s"
          % (hi_new, "안에 있음(안정)" if lo_o <= hi_new <= hi_o else "밖 — 재검토 필요"))

    # drop-max: 최다 기여일 제외
    worst = max(per, key=lambda p: p[1])
    sub = [t_of(b) for b in red if b["day"] != worst[0]]
    print("    drop-max(%s, n=%d 제외) → HI=%.4f (전체 대비 %+.4f)"
          % (worst[0], worst[1], TARGET_MEAN + span0 * _mean(sub),
             (TARGET_MEAN + span0 * _mean(sub)) - hi_new))

    print("\n" + "=" * 84)
    print("§9: 이 스크립트는 상수를 자동 적용하지 않는다. 위 권고값을 수동 반영할 것.")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
