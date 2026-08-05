# scripts/payoff_geometry_watch.py
"""[MW0602 435차, 캠페인 49] 페이오프 기하 상시 감시 — 읽기 전용. **시뮬레이터 무관.**

무엇을 묻는가
--------------
**현행 청산 기하가 애초에 이길 수 있는 구조인가.**

지금까지 이걸 보는 채널이 하나도 없었다 — [24]는 반납만, [25]는 보호 offset만,
[23-B]는 대안 기하만 본다. 정작 "현행이 구조적으로 흑자를 낼 수 있나"는 무계측이었다.

0805 실측(설정·로그 직독):

    하드스톱      = ATR × 1.50
    보호스톱(qty=1) = ATR × 0.25      ← 호라이즌 무관 상수(main.py 정본은 settings)
    → 보호전환에 걸린 "승리" 0.25 : "패배" 1.50 = **1:6** → 손익분기 승률 **85.7%**

TP1은 374/387차에 호라이즌별로 분화됐는데(0.3/0.5/0.7) 보호 lock은 339차 상수
그대로 남아, **TP1 대비 유지율이 호라이즌에 반비례**한다(1m 83% / 3m 50% / 5m 36%).

왜 시뮬레이터를 안 쓰나
-----------------------
432차 후속2에서 기하 A/B 채널 4종이 공유하는 재생기가 **실제를 재현하지 못한다**는
것이 드러났다(§47 게이트가 그걸 잡는다). 이 채널은 `trades` 실측만 쓰므로 그 오염과
**구조적으로 무관**하다 — 게이트가 SUSPEND여도 계속 돈다.

이중지표를 쓰는 이유
--------------------
두 기준이 갈리고, **그 갈림 자체가 정보**다:

    원화(pt)    — 실제 돈. 고변동일의 큰 이익이 그대로 반영된다.
    위험조정(R) — 각 진입의 하드스톱 거리로 정규화. 변동성 체제 차이를 제거한다.

둘이 크게 갈리면 "결과가 소수 고변동일에 집중"이라는 뜻이고, 리포트가 경고한다.

⚠ **포지션 단위로 집계한다 — 417차 교훈**
------------------------------------------
`trades` 한 행은 **청산 레그**다(TP1 부분청산 / 잔량이 별도 행). 레그로 세면 이익
포지션이 여러 작은 행으로 쪼개져 승률이 뜨고 손익비가 왜곡된다.
실측(07-14~08-05): 레그 119건 vs 포지션 109건 — 다중레그 10건이 **+12.60pt**를
품고 있다. 반드시 `GROUP BY entry_ts`로 병합할 것.

판정 (사전등록: config/settings.py VALIDATION_CAMPAIGN["payoff_geometry_watch"])
-------------------------------------------------------------------------------
  PASS : edge_gap = 실제승률 − 손익분기승률 > 0 이 **두 기준 모두**에서 성립
  FAIL : 어느 한 기준이라도 edge_gap <= 0 → 기하 재설계 검토(주간회의 수동, §9)
  INSUFFICIENT : min_days / min_samples 미달

⚠ 자동 적용 없음. 이 채널의 목적은 조치가 아니라 **문제의 존재를 계속 보이게 하는 것**이다.

실행:
    py310_64\python.exe scripts/payoff_geometry_watch.py [--since 2026-07-05]
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config.settings import TRADES_DB, VALIDATION_CAMPAIGN  # noqa: E402

_CR = VALIDATION_CAMPAIGN.get("payoff_geometry_watch", {})


def _stats(vals):
    """승률·손익비·손익분기승률·edge_gap. 표본이 한쪽뿐이면 None."""
    w = [v for v in vals if v > 0]
    l = [v for v in vals if v <= 0]
    if not w or not l:
        return None
    aw, al = statistics.mean(w), abs(statistics.mean(l))
    if aw + al <= 0:
        return None
    wr = len(w) / len(vals)
    be = al / (aw + al)
    return {"n": len(vals), "n_win": len(w), "win_rate": wr,
            "avg_win": aw, "avg_loss": -al, "payoff": aw / al,
            "breakeven_wr": be, "edge_gap": wr - be, "total": sum(vals)}


def compute(since: str = "2026-07-05") -> dict:
    src = _CR.get("entry_source", "SYSTEM_AUTO")
    # ⚠ 417차 — 포지션 단위 병합 필수
    with sqlite3.connect(TRADES_DB) as c:
        rows = c.execute(
            "SELECT entry_ts, SUM(pnl_pts), COUNT(*), MAX(entry_horizon), MAX(hurst_bucket) "
            "FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL AND entry_source = ? "
            "GROUP BY entry_ts ORDER BY entry_ts", (since, src)).fetchall()
        n_legs = c.execute(
            "SELECT COUNT(*) FROM trades WHERE entry_ts >= ? AND exit_ts IS NOT NULL "
            "AND entry_source = ?", (since, src)).fetchone()[0]

    # R(하드스톱 거리) — [23-B]와 같은 산식·같은 소스를 쓴다.
    try:
        from scripts.tp1_geometry_shadow import _load_atr_map, _geometry
        atr_map = _load_atr_map(since)
    except Exception:
        atr_map, _geometry = {}, None

    pos = []
    for ets, pnl, k, hz, hb in rows:
        rec = {"ts": ets, "pt": float(pnl or 0.0), "legs": int(k), "day": ets[:10]}
        if _geometry is not None:
            atr = atr_map.get(ets[:17] + "00") or atr_map.get(ets)
            if atr:
                R = _geometry(hz, hb, float(atr), None, None)[0]
                if R and R > 0:
                    rec["R"] = float(R)
                    rec["r_mult"] = rec["pt"] / float(R)
        pos.append(rec)

    return {"since": since, "positions": pos, "n_legs": n_legs,
            "n_days": len({p["day"] for p in pos})}


def summarize(out: dict) -> dict:
    pos = out.get("positions") or []
    min_n = int(_CR.get("min_samples", 40))
    min_d = int(_CR.get("min_days", 10))
    n, nd = len(pos), int(out.get("n_days") or 0)
    base = {"n": n, "n_days": nd, "n_legs": out.get("n_legs"),
            "n_multileg": sum(1 for p in pos if p["legs"] > 1)}

    if n < min_n or nd < min_d:
        base.update(verdict="INSUFFICIENT",
                    reason="표본 부족 (포지션=%d<%d 또는 거래일=%d<%d)"
                           % (n, min_n, nd, min_d))
        return base

    krw = _stats([p["pt"] for p in pos])
    rr = _stats([p["r_mult"] for p in pos if "r_mult" in p])
    base["krw"] = krw
    base["risk"] = rr
    base["n_with_R"] = sum(1 for p in pos if "r_mult" in p)

    if krw is None:
        base.update(verdict="INSUFFICIENT", reason="승 또는 패 표본이 한쪽뿐이라 판정 불가")
        return base

    gaps = [("원화", krw["edge_gap"])]
    if rr is not None:
        gaps.append(("위험조정", rr["edge_gap"]))

    fails = [nm for nm, g in gaps if g <= 0]
    verdict = "FAIL" if fails else "PASS"
    if fails:
        reason = ("edge_gap ≤ 0 — %s 기준 (%s)"
                  % ("/".join(fails),
                     " · ".join("%s %+.2f%%p" % (nm, 100 * g) for nm, g in gaps)))
    else:
        reason = ("edge_gap > 0 (%s)"
                  % " · ".join("%s %+.2f%%p" % (nm, 100 * g) for nm, g in gaps))

    # 두 기준 격차 경고 — 결과가 소수 고변동일에 집중돼 있다는 신호
    if rr is not None:
        div = abs(krw["edge_gap"] - rr["edge_gap"]) * 100.0
        base["dual_divergence_pp"] = round(div, 3)
        lim = float(_CR.get("dual_metric_divergence_pp", 3.0))
        if div > lim:
            reason += (" ⚠ 두 기준 격차 %.2f%%p > %.1f — 결과가 소수 고변동일에 "
                       "집중됐을 가능성" % (div, lim))
    base.update(verdict=verdict, reason=reason)
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None)
    args = ap.parse_args()
    since = args.since or VALIDATION_CAMPAIGN.get("start_date", "2026-07-05")
    out = compute(since)
    s = summarize(out)

    print("=" * 92)
    print("[49] 페이오프 기하 상시 감시   기간 %s~   (시뮬레이터 무관 · trades 실측)" % since)
    print("사전등록: config/settings.py VALIDATION_CAMPAIGN['payoff_geometry_watch']")
    print("=" * 92)
    print("포지션 %s건 / 거래일 %s   (청산레그 %s건, 다중레그 포지션 %s건)"
          % (s.get("n"), s.get("n_days"), s.get("n_legs"), s.get("n_multileg")))
    print("⚠ 417차 — 레그가 아니라 **포지션 단위**로 병합해 계산한다.")
    print()
    if s.get("krw"):
        print("%-10s %6s %8s %9s %9s %9s %12s %11s"
              % ("기준", "n", "승률", "평균승", "평균패", "손익비", "손익분기승률", "edge_gap"))
        print("-" * 84)
        for nm, d, unit in (("원화(pt)", s.get("krw"), "pt"),
                            ("위험조정(R)", s.get("risk"), "R")):
            if not d:
                print("%-10s (R 산출 불가 — atr 결측)" % nm)
                continue
            print("%-10s %6d %7.1f%% %+8.3f %+9.3f %9.3f %11.1f%% %+10.2f%%p"
                  % (nm, d["n"], 100 * d["win_rate"], d["avg_win"], d["avg_loss"],
                     d["payoff"], 100 * d["breakeven_wr"], 100 * d["edge_gap"]))
        if s.get("dual_divergence_pp") is not None:
            print()
            print("두 기준 edge_gap 격차: %.2f%%p" % s["dual_divergence_pp"])
    print()
    print("판정: %s — %s" % (s["verdict"], s["reason"]))
    print()
    print("§9: 자동 적용 없음. 이 채널의 목적은 조치가 아니라 **문제를 계속 보이게 하는 것**이다.")
    print("⚠ 설계 기하 자체(설정 직독): 하드스톱 ATR×1.50 / 보호스톱 ATR×0.25 = 1:6")
    print("  → 보호전환에 걸린 승리만 놓고 보면 손익분기 승률 85.7%. 러너가 그 격차를 메운다.")


if __name__ == "__main__":
    main()
