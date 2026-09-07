# -*- coding: utf-8 -*-
"""규칙 검증 보강 — 드리프트 중립 스프레드 · 당일 레짐(규칙 1·2) · 가격대리 여부 · 집중도 · GP25 강건성.
입력: _snapshot/rules_panel.pkl (rules_backtest.py 산출)  출력: rules_backtest2_report.md
"""
from __future__ import annotations
import os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from rules_backtest import rule_signals, evaluate, row, HDR, sign_p, nonoverlap, spear
from gp_econ import bracket_sim, FORCED_EXIT_HHMM
OUT = []
def w(s=""): OUT.append(s)

def main():
    d = pd.read_pickle(os.path.join(HERE, "_snapshot", "rules_panel.pkl")); S = rule_signals(d)
    inv_days = sorted(d.loc[d["foreign_futures_net_raw"].notna(), "session"].unique()); win = (inv_days[0], inv_days[-1])
    w("# 규칙 검증 보강 (rules_backtest2.py)"); w("")
    # ── 1. 드리프트 중립 롱-숏 스프레드
    w("## 1. 드리프트 중립 검정 — 같은 날 LONG신호 분 vs SHORT신호 분의 fwd30 차이 (관측단위 거래일)"); w("")
    w("창의 기준선이 LONG −0.54pt / SHORT +0.54pt(30분)로 치우쳐 있어, 방향 규칙의 정보량은 「LONG신호 뒤 수익 − SHORT신호 뒤 수익」으로 재야 한다. 양수면 규칙 방향에 정보가 있다."); w("")
    w("| 규칙 | 일수 | 스프레드 평균(pt/30m) | t | p | 양수일 | 5m 스프레드 | 15m 스프레드 |"); w("|---|---|---|---|---|---|---|---|")
    for k, s in S.items():
        if k.startswith("R6"): continue
        df = pd.DataFrame({"s": s, "f30": d["fwd30"], "f5": d["fwd5"], "f15": d["fwd15"], "day": d["session"], "hh": d["hhmm"]})
        df = df[(df["hh"] >= "09:15") & (df["hh"] < FORCED_EXIT_HHMM)]
        rows = []
        for day, g in df.groupby("day"):
            L = g[g["s"] > 0]; Sh = g[g["s"] < 0]
            if len(L) >= 5 and len(Sh) >= 5:
                rows.append({"d30": L["f30"].mean() - Sh["f30"].mean(), "d5": L["f5"].mean() - Sh["f5"].mean(), "d15": L["f15"].mean() - Sh["f15"].mean()})
        r = pd.DataFrame(rows).dropna()
        if len(r) < 10: w("| %s | %d | 표본미달 | | | | | |" % (k, len(r))); continue
        tt = stats.ttest_1samp(r["d30"], 0)
        w("| %s | %d | %+.3f | %+.2f | %.4f | %.0f%% | %+.3f | %+.3f |" % (k, len(r), r["d30"].mean(), tt.statistic, tt.pvalue, (r["d30"] > 0).mean()*100, r["d5"].mean(), r["d15"].mean()))
    w("")
    # ── 2. 당일 레짐 검정 (규칙 1·2의 원래 뜻)
    w("## 2. 규칙 1·2를 「당일 레짐」으로 재검정 — 시각 t의 외인 누계 부호 → 잔여 장(t→15:09) 방향"); w("")
    w("| 판정 시각 | 축 | 일수 | 누계>0 일수 / 잔여장 평균(pt) / 상승일 | 누계<0 일수 / 잔여장 평균 / 상승일 | 차이 t-p | Spearman(누계, 잔여) p |"); w("|---|---|---|---|---|---|---|")
    for hh in ("10:00", "11:00", "12:00", "13:00", "14:00"):
        rows = []
        for day, g in d.groupby("session"):
            if day < win[0]: continue
            a = g[g["hhmm"] == hh]; e = g[g["hhmm"] == "15:09"]
            if len(a) == 0 or len(e) == 0: continue
            a = a.iloc[0]
            rows.append({"day": day, "for": a["foreign_futures_net_raw"], "ins": a["institution_futures_net_raw"], "ret": a["retail_futures_net_raw"],
                         "for_slope": a["for_d30"], "rem": float(e["close"].iloc[0] - a["close"]), "sofar": float(a["close"] - g["open"].iloc[0])})
        r = pd.DataFrame(rows).dropna(subset=["for", "rem"])
        for ax, col in (("외인 누계", "for"), ("외인 Δ30", "for_slope"), ("기관 누계", "ins"), ("개인 누계", "ret"), ("(대조) 시가대비 등락", "sofar")):
            x = r.dropna(subset=[col])
            p_ = x[x[col] > 0]; n_ = x[x[col] < 0]
            if len(p_) < 3 or len(n_) < 3: w("| %s | %s | %d | 표본미달 | | | |" % (hh, ax, len(x))); continue
            tp = stats.ttest_ind(p_["rem"], n_["rem"], equal_var=False).pvalue
            sp = stats.spearmanr(x[col], x["rem"])
            w("| %s | %s | %d | %d / %+.2f / %.0f%% | %d / %+.2f / %.0f%% | %.3f | %+.3f (p=%.3f) |" % (hh, ax, len(x), len(p_), p_["rem"].mean(), (p_["rem"] > 0).mean()*100, len(n_), n_["rem"].mean(), (n_["rem"] > 0).mean()*100, tp, sp.statistic, sp.pvalue))
    w("")
    # ── 3. 가격 대리 여부
    w("## 3. 지표가 「최근 가격변화의 대리」인가 — 일자단위 Spearman 평균 (창: 각 축 가용 전 구간)"); w("")
    d["ret10"] = d.groupby("session")["close"].diff(10); d["ret5"] = d.groupby("session")["close"].diff(5); d["ret30"] = d.groupby("session")["close"].diff(30)
    w("| 축 | vs 직전10분 등락 | vs 직전30분 등락 | vs 직전5분 등락 | 일수 |"); w("|---|---|---|---|---|")
    for k, col in [("외인Δ10", "for_d10"), ("외인Δ30", "for_d30"), ("기관Δ10", "ins_d10"), ("개인Δ10", "ret_d10"), ("체결강도Δ5", "str_d5"), ("OBV−sig", "obv_hist"), ("GB20−GS20", None), ("RSI14", "rsi14")]:
        x = (d["gb20"] - d["gs20"]) if col is None else d[col]
        vals = {c: [] for c in ("ret10", "ret30", "ret5")}
        for day, g in pd.DataFrame({"x": x, "ret10": d["ret10"], "ret30": d["ret30"], "ret5": d["ret5"], "s": d["session"]}).dropna().groupby("s"):
            if len(g) < 60 or g["x"].nunique() < 3: continue
            for c in vals: vals[c].append(stats.spearmanr(g["x"], g[c]).statistic)
        w("| %s | %+.3f | %+.3f | %+.3f | %d |" % (k, np.nanmean(vals["ret10"]), np.nanmean(vals["ret30"]), np.nanmean(vals["ret5"]), len(vals["ret10"])))
    w("")
    # ── 3b. 외인Δ10 IC를 직전 등락으로 통제(부분상관)
    w("직전 30분 등락을 통제한 뒤의 일자단위 부분 IC(→fwd30):"); w("")
    w("| 축 | 원 IC | ret30 통제 후 | 잔존율 | p(통제후) | 일수 |"); w("|---|---|---|---|---|---|")
    for k, col in [("외인Δ10", "for_d10"), ("기관Δ10", "ins_d10"), ("OBV−sig", "obv_hist"), ("GB20−GS20", None), ("RSI14", "rsi14"), ("체결강도Δ5", "str_d5")]:
        x = (d["gb20"] - d["gs20"]) if col is None else d[col]
        raw, part = [], []
        for day, g in pd.DataFrame({"x": x, "y": d["fwd30"], "c": d["ret30"], "s": d["session"]}).dropna().groupby("s"):
            if len(g) < 60 or g["x"].nunique() < 3: continue
            rx, ry, rc = g["x"].rank(), g["y"].rank(), g["c"].rank()
            raw.append(stats.spearmanr(g["x"], g["y"]).statistic)
            ex = rx - np.polyval(np.polyfit(rc, rx, 1), rc); ey = ry - np.polyval(np.polyfit(rc, ry, 1), rc)
            part.append(np.corrcoef(ex, ey)[0, 1])
        raw, part = np.array(raw), np.array(part)
        tt = stats.ttest_1samp(part, 0)
        w("| %s | %+.4f | %+.4f | %.2f | %.4f | %d |" % (k, raw.mean(), part.mean(), part.mean()/raw.mean() if raw.mean() != 0 else np.nan, tt.pvalue, len(part)))
    w("")
    # ── 4. R9 거리모델 SHORT 집중도
    w("## 4. 유일한 양수 규칙 「R9 거리모델 고점 되돌림 → SHORT」의 강건성"); w("")
    s = S["R9_거리모델_되돌림"]; sig = s.where(s < 0, 0)
    res = evaluate(d, sig, "R9거리 SHORT", window=win)
    m = (sig != 0) & d["atr14"].notna() & (d["atr14"] > 1e-6) & (d["hhmm"] < FORCED_EXIT_HHMM) & (d["hhmm"] >= "09:15")
    ev = d[m].copy(); ev["dir"] = -1; ev = ev[nonoverlap(list(zip(ev.index, ev["session"])))]
    by_day = {k_: g for k_, g in d.groupby("session")}; pos = {k_: {t: i for i, t in enumerate(g.index)} for k_, g in by_day.items()}
    ev["net"] = [bracket_sim(by_day[r["session"]], pos[r["session"]][ts], -1, float(r["atr14"]))[0] for ts, r in ev.iterrows()]
    daily = ev.groupby("session")["net"].agg(["sum", "count"]).sort_values("sum")
    w("- n=%d, 일수=%d, 건당 %+.0f원, 합 %+.0f원" % (len(ev), len(daily), ev["net"].mean(), ev["net"].sum()))
    w("- 일자별 net 합(오름차순): " + ", ".join("%s %+.0f(%d)" % (i, r_["sum"], r_["count"]) for i, r_ in daily.iterrows()))
    top3 = daily["sum"].nlargest(3).sum(); w("- 상위 3일 기여 %+.0f (합의 %.0f%%) · 상위 3일 제거 후 합 %+.0f · 최악 3일 제거 후 합 %+.0f" % (top3, top3/ev["net"].sum()*100 if ev["net"].sum() else np.nan, ev["net"].sum() - top3, ev["net"].sum() - daily["sum"].nsmallest(3).sum()))
    # 시각대별 / 진입 시 sofar_high 대비
    ev["hour"] = ev.index.hour
    w("- 시각대별 건당 net: " + ", ".join("%02d시 %+.0f(n=%d)" % (h, g["net"].mean(), len(g)) for h, g in ev.groupby("hour")))
    # 전반/후반
    days_sorted = sorted(daily.index); half = len(days_sorted)//2
    w("- 전반 %d일 합 %+.0f / 후반 %d일 합 %+.0f" % (half, daily.loc[days_sorted[:half], "sum"].sum(), len(days_sorted)-half, daily.loc[days_sorted[half:], "sum"].sum()))
    # LONG 대칭(저점 되돌림) 비교 및 0850 단계 사용 여부
    w("- 대칭 LONG(저점 되돌림→LONG): " + row(evaluate(d, s.where(s > 0, 0), "R9거리 LONG", window=win)).replace("|", "·"))
    w("")
    # 구조모델 R9 SHORT 도 같은 절차
    s2 = S["R9_구조모델_되돌림"]; sig2 = s2.where(s2 < 0, 0)
    m2 = (sig2 != 0) & d["atr14"].notna() & (d["atr14"] > 1e-6) & (d["hhmm"] < FORCED_EXIT_HHMM) & (d["hhmm"] >= "09:15")
    ev2 = d[m2].copy(); ev2 = ev2[nonoverlap(list(zip(ev2.index, ev2["session"])))]
    ev2["net"] = [bracket_sim(by_day[r["session"]], pos[r["session"]][ts], -1, float(r["atr14"]))[0] for ts, r in ev2.iterrows()]
    d2 = ev2.groupby("session")["net"].sum()
    w("- 구조모델 고점 되돌림 SHORT: n=%d 일수=%d 건당 %+.0f 합 %+.0f · 상위3일 제거 후 %+.0f · 최악3일 제거 후 %+.0f" % (len(ev2), len(d2), ev2["net"].mean(), ev2["net"].sum(), ev2["net"].sum() - d2.nlargest(3).sum(), ev2["net"].sum() - d2.nsmallest(3).sum()))
    w("")
    # ── 5. GP25 강건성 + 임계 민감도
    w("## 5. GP 규칙 4·5 강건성 — 기간 25 · 임계 0.3/0.7 · 기울기 창 5 (같은 창)"); w(""); w(HDR)
    for per in (20, 25):
        gb, gs = d["gb%d" % per], d["gs%d" % per]
        for thr in (0.3, 0.5, 0.7):
            for k_ in (3, 5):
                gbd = d.groupby("session")["gb%d" % per].diff(k_); gsd = d.groupby("session")["gs%d" % per].diff(k_)
                sig = pd.Series(np.where((gs >= thr) & (gsd > 0), -1, np.where((gb >= thr) & (gbd > 0), 1, 0)), index=d.index)
                w(row(evaluate(d, sig, "GP%d thr%.1f 기울기%d" % (per, thr, k_), window=win)))
    w("")
    # ── 6. 역방향(페이드) 판
    w("## 6. 규칙을 뒤집으면(페이드) 어떻게 되는가 — 같은 창"); w(""); w(HDR)
    for k in ["R1R2_외인Δ10", "R3_체결강도Δ5", "R4R5_합", "R7_한쪽≈0&반대급등", "R8_OBV>시그널", "RSI_과매수매도역행"]:
        w(row(evaluate(d, -S[k], k + " [페이드]", window=win)))
    w("")
    open(os.path.join(HERE, "rules_backtest2_report.md"), "w", encoding="utf-8").write("\n".join(OUT)); print("\n".join(OUT))

if __name__ == "__main__":
    main()
