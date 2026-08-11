# -*- coding: utf-8 -*-
"""[MW0601 457차 / G4] 방향 편향 상시 감시 채널 — 주간 캠페인 편입용.

## 왜 이 채널이 필요한가

2026-08-11에 시장이 964.42 → 992.86(+2.9%) 오르는 동안 앙상블은 SHORT를 LONG의
**8배** 냈다(152:19). 그런데 **그 편향을 잡아낸 감시자가 하나도 없었다** —
DriftDetector는 pnl/wr/pf 3축만 보고 CLEAR를 냈고, Brier 경고는 확신도만,
CB③-P4는 30m 정확도만 본다. *"신호 방향 분포가 실현 방향 분포와 체계적으로
어긋나는가"* 를 재는 축이 시스템에 없었다.

이 모듈은 A1 진단 하네스(`scripts/direction_bias_diagnosis.py`)의 **상시화 버전**이다.
검정 로직은 그쪽에서 import해 재사용한다 — 두 벌로 복제하면 갈라진다.

## 관측치

    Δ(일자) = (예측 UP비 − DN비) − (실현 UP비 − DN비)

0이면 시장을 그대로 따라간 것. 음수로 유의하면 **시장 대비 SHORT 초과 발행**이다.
예측이 DN 쪽이어도 그날 시장이 정말 내렸다면 편향이 아니다 — 그래서 실현치를 뺀다.

## 두 가지 함정을 구조적으로 막는다

1. **신호단위 검정 금지.** 372차가 확인했듯 같은 분의 6개 호라이즌, 인접 분끼리
   전부 상관돼 있다. 신호단위로 세면 p가 무한정 작아져 아무 편향이나 "유의"해진다.
   → 일자단위 독립관측만 쓴다.
2. **"뒤집으면 되지 않나"의 자동 반박.** A1 실측에서 예측을 뒤집으면 적중률이
   **떨어졌다**(3m 0.347→0.337, 5m 0.348→0.340). 편향은 있는데 역방향 알파는 없다.
   → 판정문에 역방향 적중률을 **항상** 같이 찍어 다음 세션이 잘못된 처방으로
     가는 것을 막는다.

사전등록: `config/settings.py:VALIDATION_CAMPAIGN["direction_bias_watch"]`
인터페이스: `compute(since) -> dict` / `summarize(out) -> dict`
  (generate_validation_campaign_report.py 의 `_safe_channel` 규약)

읽기 전용: predictions.db.
"""
from __future__ import print_function

import os
import sys

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import HORIZONS, VALIDATION_CAMPAIGN  # noqa: E402
from scripts.direction_bias_diagnosis import (  # noqa: E402
    load_rows, group_by_day_hz, s1a_label_distribution, s1b_prob_intercept,
    s1c_bias_test, mean,
)

_CFG = VALIDATION_CAMPAIGN.get("direction_bias_watch", {}) or {}
MIN_DAYS = int(_CFG.get("min_days", 20))
T_TH = float(_CFG.get("t_threshold", 2.09))
ALERT_MIN_HZ = int(_CFG.get("alert_min_horizons", 2))
WINDOW_DAYS = int(_CFG.get("window_days", 60))
DATA_START = _CFG.get("data_start", "")


def compute(since=None):
    """롤링 창의 일자단위 편향 지표. since는 캠페인 시작일(리포트가 넘긴다)."""
    if not _CFG.get("enabled", True):
        return {"disabled": True}
    horizons = list(HORIZONS)
    try:
        rows, dates = load_rows(WINDOW_DAYS, horizons)
    except Exception as e:
        return {"error": "%s: %s" % (type(e).__name__, e)}

    # 캠페인 시작일 / 채널 data_start 중 늦은 쪽 이후만 본다.
    _floor = max([d for d in (since, DATA_START) if d] or [""])
    if _floor:
        keep = {d for d in dates if d >= _floor[:10]}
        rows = [r for r in rows if r[0] in keep]
        dates = sorted(keep)
    if not rows:
        return {"error": "표본 없음", "dates": []}

    g = group_by_day_hz(rows)
    return {
        "dates": dates,
        "horizons": horizons,
        "s1a": s1a_label_distribution(g, horizons),
        "s1b": s1b_prob_intercept(g, horizons),
        "s1c": s1c_bias_test(g, horizons),
    }


def summarize(out):
    """사전등록 합격선으로 판정. **여기서 기준을 바꾸지 말 것** (캠페인 §9)."""
    if not out or out.get("disabled"):
        return {"verdict": "INSUFFICIENT", "reason": "채널 비활성", "no_data": True}
    if out.get("error"):
        return {"verdict": "INSUFFICIENT", "reason": "소스 없음 — %s" % out["error"],
                "no_data": True}

    dates = out.get("dates") or []
    c = out.get("s1c") or {}
    b = out.get("s1b") or {}
    a = out.get("s1a") or {}

    if len(dates) < MIN_DAYS:
        return {"verdict": "INSUFFICIENT", "n_days": len(dates),
                "reason": "거래일 %d < %d — 판정 보류" % (len(dates), MIN_DAYS)}

    # Bonferroni 생존 호라이즌 (부호별)
    surv_neg, surv_pos, per_hz = [], [], {}
    for hz, r in c.items():
        if not r:
            continue
        per_hz[hz] = {
            "delta": r["delta_mean"], "t": r["t"],
            "p_bonf": r["p_bonferroni"], "acc": r["acc_mean"],
            "rev_acc": r["rev_acc_mean"], "n_days": r["n_days"],
        }
        if not r.get("significant"):
            continue
        (surv_neg if r["delta_mean"] < 0 else surv_pos).append(hz)

    # 역방향이 실제로 나은지 — 판정문에 항상 붙인다(잘못된 처방 방어)
    _acc = [v["acc"] for v in per_hz.values() if v["acc"] == v["acc"]]
    _rev = [v["rev_acc"] for v in per_hz.values() if v["rev_acc"] == v["rev_acc"]]
    rev_better = bool(_acc and _rev and mean(_rev) > mean(_acc))
    rev_note = ("역방향 적중 %.4f %s 정방향 %.4f — %s"
                % (mean(_rev) if _rev else float("nan"),
                   ">" if rev_better else "≤",
                   mean(_acc) if _acc else float("nan"),
                   "⚠ 반전 검토 대상" if rev_better
                   else "**반전은 답이 아니다**")) if (_acc and _rev) else ""

    # 확률 절편이 같이 치우쳤는지 → 원인 축 힌트 (라벨 vs 모델)
    _lab_skewed = [hz for hz, r in a.items()
                   if r and r["p"] < 0.05 and r["skew_mean"] < 0]
    _prb_skewed = [hz for hz, r in b.items()
                   if r and r["p"] < 0.05 and r["gap_mean"] < 0]

    winners, side = (surv_neg, "SHORT") if len(surv_neg) >= len(surv_pos) \
        else (surv_pos, "LONG")
    if len(winners) >= ALERT_MIN_HZ:
        cause = ("레이블/학습창" if len(_lab_skewed) >= ALERT_MIN_HZ
                 else "**모델 절편**(라벨은 균형)")
        return {
            "verdict": "ALERT_BIAS", "n_days": len(dates),
            "side": side, "horizons": winners, "per_horizon": per_hz,
            "label_skewed": _lab_skewed, "prob_skewed": _prb_skewed,
            "rev_better": rev_better,
            "reason": ("%s 초과 발행 — %d개 호라이즌(%s)이 Bonferroni 생존 "
                       "(|t|>%.2f, %d거래일). 원인 후보 %s. %s"
                       % (side, len(winners), ",".join(sorted(winners)),
                          T_TH, len(dates), cause, rev_note)),
        }
    return {
        "verdict": "PASS", "n_days": len(dates), "per_horizon": per_hz,
        "label_skewed": _lab_skewed, "prob_skewed": _prb_skewed,
        "rev_better": rev_better,
        "reason": ("체계적 편향 미검출 — 생존 %d개 < %d (%d거래일). %s"
                   % (max(len(surv_neg), len(surv_pos)), ALERT_MIN_HZ,
                      len(dates), rev_note)),
    }


if __name__ == "__main__":
    from utils.analysis_db import guard_intraday
    guard_intraday("direction_bias_watch")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    _o = compute(VALIDATION_CAMPAIGN.get("start_date"))
    _s = summarize(_o)
    print("[G4 direction_bias_watch] %s — %s" % (_s.get("verdict"), _s.get("reason")))
    for _hz, _v in sorted((_s.get("per_horizon") or {}).items()):
        print("  %-4s Δ=%+.4f t=%+.2f p(Bonf)=%.4f  적중 %.4f / 반전 %.4f  (%d일)"
              % (_hz, _v["delta"], _v["t"], _v["p_bonf"],
                 _v["acc"], _v["rev_acc"], _v["n_days"]))
