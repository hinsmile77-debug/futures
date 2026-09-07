# -*- coding: utf-8 -*-
"""GP 교차 신호 — 청산 규칙 격자 탐색.

§2에서 「TP 선도달 75.6%」가 나왔으나 스톱1.5/TP0.5 의 **손익분기 승률이 정확히 75%**다
(1.5/(1.5+0.5)). 즉 그 승률은 신호 품질이 아니라 **비대칭 격자의 산술**일 수 있다.

이 스크립트가 답하는 질문: **어떤 청산 규칙으로든 이 신호가 비용을 넘는가.**
스톱·TP 격자를 전수로 돌려 gross 기댓값과 net 기댓값을 함께 낸다.
"""
from __future__ import annotations
import os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gp_lib import PT_VALUE, RATE_LIVE, TICK
from gp_econ import FORCED_EXIT_HHMM
from gp_cross_signal import load, events
from rules_backtest import sign_p, nonoverlap

OUT = []
def w(s=""): OUT.append(s)
def f(v, p="+,.0f"):
    return "—" if (v is None or v != v) else format(v, p)


def simple_bracket(d, ev, stop_atr, tp_atr, horizon=60):
    """단일 TP·단일 스톱. 반환: 건별 gross_pt · net_krw · 결과."""
    by_day = {s: g for s, g in d.groupby("session")}
    pos = {s: {t: i for i, t in enumerate(g.index)} for s, g in by_day.items()}
    rows = []
    for ts, r in ev.iterrows():
        g = by_day[r["session"]]; i = pos[r["session"]][ts]
        dr = int(r["dir"]); c0 = float(r["close"]); atr = float(r["atr14"])
        stop = c0 - dr * stop_atr * atr; tp = c0 + dr * tp_atr * atr
        hh = g["high"].to_numpy(float); ll = g["low"].to_numpy(float)
        cc = g["close"].to_numpy(float); hhmm = g["hhmm"].to_numpy(); n = len(g)
        out, px = "TIME", cc[min(i + horizon, n - 1)]
        for j in range(i + 1, min(i + 1 + horizon, n)):
            if hhmm[j] >= FORCED_EXIT_HHMM:
                out, px = "FORCE", cc[j]; break
            hs = (ll[j] <= stop) if dr > 0 else (hh[j] >= stop)
            ht = (hh[j] >= tp) if dr > 0 else (ll[j] <= tp)
            if hs:
                out, px = "STOP", stop; break
            if ht:
                out, px = "TP", tp; break
        gross_pt = dr * (px - c0)
        comm_pt = 2.0 * c0 * RATE_LIVE
        rows.append({"session": r["session"], "dir": dr, "atr": atr, "out": out,
                     "gross_pt": gross_pt, "net_krw": (gross_pt - comm_pt) * PT_VALUE,
                     "gross_krw": gross_pt * PT_VALUE, "comm_krw": comm_pt * PT_VALUE})
    return pd.DataFrame(rows)


def main():
    d = load()
    ev = events(d, eps=0.05)
    ev_pure = events(d, eps=None, require_eps=False)
    rng = np.random.default_rng(20260907)
    base = d[(d["hhmm"] >= "09:15") & (d["hhmm"] < FORCED_EXIT_HHMM)
             & d["atr14"].notna() & (d["atr14"] > 1e-6)]
    rnd = base.sample(n=4000, random_state=7).copy()
    rnd["dir"] = rng.choice([1, -1], size=len(rnd))

    w("# GP 교차 신호 — 청산 규칙 격자 전수 탐색")
    w("")
    w("질문: **어떤 청산 규칙으로든 이 신호가 왕복 비용을 넘는가.**")
    w("신호 = 교차+GS≤0.05 (n=%d, %d거래일). 단일 TP·단일 스톱 · 60분 창 · 동시도달 시 스톱 우선."
      % (len(ev), ev["session"].nunique()))
    w("")

    w("## 1. 손익분기 승률과 실측 승률")
    w("")
    w("스톱 S·TP T 격자의 손익분기 승률은 **S/(S+T)** 다(비용 전). 실측이 그 위에 있어야 gross 흑자다.")
    w("")
    w("| 스톱 | TP | 손익분기 승률 | 실측 TP선도달 | 초과 | **gross 건당** | 왕복수수료 | **net 건당** | 일자 +/- | 부호p |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    best = None
    grid = [(1.5, 0.5), (1.5, 0.75), (1.5, 1.0), (1.5, 1.5), (1.5, 2.0),
            (1.0, 0.5), (1.0, 0.75), (1.0, 1.0), (1.0, 1.5), (1.0, 2.0),
            (0.75, 0.5), (0.75, 1.0), (0.5, 0.5), (0.5, 1.0), (0.5, 1.5),
            (2.0, 0.5), (2.0, 1.0), (2.0, 2.0), (3.0, 1.0)]
    rows = []
    for s_, t_ in grid:
        r = simple_bracket(d, ev, s_, t_)
        tp_rate = (r["out"] == "TP").mean()
        be = s_ / (s_ + t_)
        dly = r.groupby("session")["net_krw"].sum(); p, pp, nn = sign_p(dly)
        rows.append({"stop": s_, "tp": t_, "be": be, "tp_rate": tp_rate,
                     "gross": r["gross_krw"].mean(), "comm": r["comm_krw"].mean(),
                     "net": r["net_krw"].mean(), "p": p, "pp": pp, "nn": nn})
        w("| %.2f | %.2f | %.1f%% | %.1f%% | %+.1f%%p | %s | %s | **%s** | %d/%d | %.3f |"
          % (s_, t_, be * 100, tp_rate * 100, (tp_rate - be) * 100,
             f(r["gross_krw"].mean()), f(-r["comm_krw"].mean()), f(r["net_krw"].mean()),
             pp, nn, p))
        if best is None or r["net_krw"].mean() > best[0]:
            best = (r["net_krw"].mean(), s_, t_, r)
    w("")
    G = pd.DataFrame(rows)
    w("- 격자 %d개 중 **net 흑자는 %d개**, gross 흑자는 %d개."
      % (len(G), int((G["net"] > 0).sum()), int((G["gross"] > 0).sum())))
    w("- 최선 net: 스톱 %.2f / TP %.2f → **%s원/건** (gross %s · 수수료 %s)"
      % (best[1], best[2], f(best[0]), f(best[3]["gross_krw"].mean()),
         f(-best[3]["comm_krw"].mean())))
    w("- gross 최대: 스톱 %.2f / TP %.2f → %s원/건"
      % (G.loc[G["gross"].idxmax(), "stop"], G.loc[G["gross"].idxmax(), "tp"],
         f(G["gross"].max())))
    w("")

    w("## 2. 같은 격자에서 무작위 진입과 비교 — 신호가 더하는 것")
    w("")
    w("| 스톱 | TP | 신호 gross | 무작위 gross | **차이(신호 엣지)** | 왕복수수료 | 엣지÷비용 |")
    w("|---|---|---|---|---|---|---|")
    for s_, t_ in [(1.5, 0.5), (1.5, 1.0), (1.0, 1.0), (1.0, 0.5), (2.0, 1.0)]:
        a = simple_bracket(d, ev, s_, t_)
        b = simple_bracket(d, rnd, s_, t_)
        edge = a["gross_krw"].mean() - b["gross_krw"].mean()
        cost = a["comm_krw"].mean()
        w("| %.1f | %.1f | %s | %s | **%s** | %s | %.2f |"
          % (s_, t_, f(a["gross_krw"].mean()), f(b["gross_krw"].mean()), f(edge),
             f(-cost), edge / cost if cost else np.nan))
    w("")

    w("## 3. 「승률이 높다」는 관찰의 정체")
    w("")
    r15 = simple_bracket(d, ev, 1.5, 0.5)
    rr = simple_bracket(d, rnd, 1.5, 0.5)
    w("스톱1.5/TP0.5 에서:")
    w("")
    w("| | 신호 | 무작위 | 손익분기 |")
    w("|---|---|---|---|")
    w("| TP 선도달 | **%.1f%%** | %.1f%% | **75.0%%** |"
      % ((r15["out"] == "TP").mean() * 100, (rr["out"] == "TP").mean() * 100))
    w("| STOP | %.1f%% | %.1f%% | — |"
      % ((r15["out"] == "STOP").mean() * 100, (rr["out"] == "STOP").mean() * 100))
    w("| 시간종료·강제 | %.1f%% | %.1f%% | — |"
      % ((r15["out"].isin(["TIME", "FORCE"])).mean() * 100,
         (rr["out"].isin(["TIME", "FORCE"])).mean() * 100))
    w("| gross 건당 | %s | %s | 0 |"
      % (f(r15["gross_krw"].mean()), f(rr["gross_krw"].mean())))
    w("")
    w("**무작위 진입도 %.1f%% 를 얻는다.** 승률이 높아 보이는 것의 대부분은 스톱이 TP의 3배라는"
      % ((rr["out"] == "TP").mean() * 100))
    w("격자 구조에서 나온다 — 신호가 더하는 것은 **%+.1f%%p** 다."
      % (((r15["out"] == "TP").mean() - (rr["out"] == "TP").mean()) * 100))
    w("")

    w("## 4. 2026-09-07 그날만 — 사용자가 본 날은 특별했는가")
    w("")
    for lab, s_, t_ in (("스톱1.5/TP0.5", 1.5, 0.5), ("스톱1.5/TP1.0", 1.5, 1.0)):
        r = simple_bracket(d, ev, s_, t_)
        day = r[r["session"] == "2026-09-07"]
        w("- %s · 09-07 신호 %d건: TP %d · STOP %d · 기타 %d → net 합 **%s원** (건당 %s)"
          % (lab, len(day), int((day["out"] == "TP").sum()), int((day["out"] == "STOP").sum()),
             int((~day["out"].isin(["TP", "STOP"])).sum()), f(day["net_krw"].sum()),
             f(day["net_krw"].mean())))
    r = simple_bracket(d, ev, 1.5, 0.5)
    dly = r.groupby("session")["net_krw"].sum().sort_values()
    d97 = dly.get("2026-09-07", np.nan)
    w("- 09-07 일자 net %s원은 전체 %d일 중 **%d위**(오름차순), 상위 %.0f%% 구간이다."
      % (f(d97), len(dly), int((dly < d97).sum()) + 1, (dly < d97).mean() * 100))
    w("- 전체 일자 net 중앙값 %s · 평균 %s" % (f(dly.median()), f(dly.mean())))
    w("")

    w("## 5. 신호를 더 좁히면 살아나는가 (사후탐색 — 참고용)")
    w("")
    w("⚠ 아래는 **데이터를 본 뒤의 탐색**이다. 흑자 칸이 나와도 그 자체로는 근거가 아니다(SOP §11).")
    w("")
    w("| 추가 조건 | n | gross 건당 | net 건당 | 일자 +/- | 부호p |")
    w("|---|---|---|---|---|---|")
    ev2 = ev.copy()
    ev2["gb_jump"] = ev2["gb20"] - ev2["gb20_prev"]
    ev2["gs_exact0"] = (ev2["gs20"] <= 1e-9) | (ev2["gb20"] <= 1e-9)
    conds = [
        ("전체", pd.Series(True, index=ev2.index)),
        ("교차 점프 ≥0.2", ev2["gb_jump"].abs() >= 0.2),
        ("교차 점프 ≥0.3", ev2["gb_jump"].abs() >= 0.3),
        ("반대편 정확히 0", ev2["gs_exact0"]),
        ("GB 최종 ≥0.7", (ev2["gb20"] >= 0.7) | (ev2["gs20"] >= 0.7)),
        ("ATR ≥ 2.0pt", ev2["atr14"] >= 2.0),
        ("11:00~14:00", (ev2["hhmm"] >= "11:00") & (ev2["hhmm"] < "14:00")),
    ]
    for lab, m in conds:
        sub = ev2[m.fillna(False)]
        if len(sub) < 30:
            w("| %s | %d | 표본미달 | | | |" % (lab, len(sub))); continue
        r = simple_bracket(d, sub, 1.5, 0.5)
        dly2 = r.groupby("session")["net_krw"].sum(); p, pp, nn = sign_p(dly2)
        w("| %s | %d | %s | **%s** | %d/%d | %.3f |"
          % (lab, len(sub), f(r["gross_krw"].mean()), f(r["net_krw"].mean()), pp, nn, p))
    w("")
    open(os.path.join(HERE, "gp_cross_exitgrid.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
