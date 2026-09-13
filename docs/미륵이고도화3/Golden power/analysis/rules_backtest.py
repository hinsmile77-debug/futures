# -*- coding: utf-8 -*-
"""사용자 발견 규칙 10종 검증 백테스트 (2026-09-07, MW0601).

입력: _snapshot/{candles,investor,trades}.pkl + raw_candles(buy/sell_vol 1회 추출) + premarket_levels.db(122행)
출력: rules_backtest_report.md, out_rules_*.csv
규약: 관측단위=거래일(부호검정·t), 3분 비중첩, 실측 CYBOS 요율, 15:10 강제청산, 세션 리셋.
"""
from __future__ import annotations
import os, sys, json, sqlite3, warnings, datetime
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gp_lib import PT_VALUE, RATE_LIVE, TICK, golden_power           # noqa
from gp_econ import bracket_sim, add_atr, SIM, FORCED_EXIT_HHMM, NONOVERLAP_MIN  # noqa
from inv_unit_guard import invert_investor_log1p  # noqa  [559차 P0-2] 단위 불일치 가드
ROOT = r"C:\Users\82108\PycharmProjects\futures"
SNAP = os.path.join(HERE, "_snapshot")
OUT = []
def w(s=""): OUT.append(s)

def fmt(v, f="%+.0f"):
    return (f % v) if (v == v and v is not None) else "—"

# ───────────────────────── 1. 패널 ─────────────────────────
def load_bs():
    p = os.path.join(SNAP, "buysell.pkl")
    if os.path.exists(p): return pd.read_pickle(p)
    now = datetime.datetime.now().time()
    assert not (datetime.time(8,45) <= now <= datetime.time(15,35)), "장중 라이브 DB 분석 금지"
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT,"data","db","raw_data.db").replace("\\","/"), uri=True)
    b = pd.read_sql("select ts,buy_vol,sell_vol from raw_candles where buy_vol is not null order by ts", con); con.close()
    b.to_pickle(p); return b

def load_levels():
    con = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT,"data","db","premarket_levels.db").replace("\\","/"), uri=True)
    L = pd.read_sql("select date,stage,dist_high,dist_low,atr14,struct_up,struct_down from premarket_levels", con); con.close()
    def first(js):
        try:
            v = json.loads(js) if js else []
            return float(v[0][0]) if v else np.nan
        except Exception: return np.nan
    L["su1"] = L["struct_up"].map(first); L["sd1"] = L["struct_down"].map(first)
    return L

def rsi_simple(c, n=14):
    d = c.diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
    au = up.rolling(n, min_periods=n).mean(); ad = dn.rolling(n, min_periods=n).mean()
    return 100 - 100/(1 + au/ad.replace(0, np.nan))

def build_panel():
    c = pd.read_pickle(os.path.join(SNAP,"candles.pkl"))
    inv = pd.read_pickle(os.path.join(SNAP,"investor.pkl"))
    bs = load_bs()
    d = c.merge(inv, on="ts", how="left").merge(bs, on="ts", how="left")
    d["dt"] = pd.to_datetime(d["ts"]); d = d.sort_values("dt").drop_duplicates("dt").reset_index(drop=True)
    d["session"] = d["dt"].dt.strftime("%Y-%m-%d"); d["hhmm"] = d["dt"].dt.strftime("%H:%M")
    d = d[(d["hhmm"] >= "09:00") & (d["hhmm"] <= "15:35")].copy()
    d = d.set_index("dt")
    # [559차 P0-2] 역변환은 가드를 통해서만 — 압축 이전 단위 4일(2026-06-02·04·05·08)에
    # 그냥 걸면 inf 가 된다(클립 구현에서는 1.0686e+16). `inv_unit_guard` 참조.
    sup = pd.to_numeric(d["quality_investor_futures_supported"], errors="coerce").fillna(0)
    for k in ["foreign_futures_net","retail_futures_net","institution_futures_net"]:
        v = pd.to_numeric(d[k], errors="coerce")
        d[k+"_raw"] = invert_investor_log1p(v.values, (sup > 0).astype(float).values,
                                            d.index.astype(str), name=k)
    parts = []
    L = load_levels()
    for s, g in d.groupby("session"):
        g = g.copy(); cl = g["close"].astype(float)
        for n in (20, 25):
            gp = golden_power(cl, n); g["gb%d"%n] = gp["golden_buy"]; g["gs%d"%n] = gp["golden_sell"]
        g["gb_d3"] = g["gb20"].diff(3); g["gs_d3"] = g["gs20"].diff(3)
        g["obv"] = (np.sign(cl.diff()).fillna(0) * g["volume"].astype(float)).cumsum()
        g["obv_sig"] = g["obv"].ewm(span=9, adjust=False).mean(); g["obv_hist"] = g["obv"] - g["obv_sig"]
        g["obv_d5"] = g["obv"].diff(5)
        g["rsi14"] = rsi_simple(cl, 14)
        bv = pd.to_numeric(g["buy_vol"], errors="coerce"); sv = pd.to_numeric(g["sell_vol"], errors="coerce")
        ok = bv.notna() & sv.notna() & ((bv + sv) > 0)
        cb = bv.where(ok).fillna(0).cumsum(); cs = sv.where(ok).fillna(0).cumsum()
        strength = cb / cs.replace(0, np.nan) * 100
        strength[ok.cumsum() == 0] = np.nan
        g["strength"] = strength
        g["str_d5"] = g["strength"].diff(5); g["str_ma20"] = g["strength"].rolling(20, min_periods=5).mean()
        g["str_vs_ma"] = g["strength"] - g["str_ma20"]
        for k in ["foreign","retail","institution"]:
            r = g[k+"_futures_net_raw"]; g[k[:3]+"_d10"] = r - r.shift(10); g[k[:3]+"_d30"] = r - r.shift(30)
        g["sofar_high"] = g["high"].cummax(); g["sofar_low"] = g["low"].cummin()
        for col in ["dist_high","dist_low","su1","sd1","atr14_day"]: g[col] = np.nan
        for stage, m in (("0850", g["hhmm"] <= "09:30"), ("0930", g["hhmm"] > "09:30")):
            row_ = L[(L["date"] == s) & (L["stage"] == stage)]
            if len(row_):
                r = row_.iloc[0]
                g.loc[m, "dist_high"] = r["dist_high"]; g.loc[m, "dist_low"] = r["dist_low"]
                g.loc[m, "su1"] = r["su1"]; g.loc[m, "sd1"] = r["sd1"]; g.loc[m, "atr14_day"] = r["atr14"]
        parts.append(g)
    d = pd.concat(parts).sort_index()
    d["atr14"] = add_atr(d)
    for h in (5, 15, 30):
        same = d["session"].shift(-h) == d["session"]
        d["fwd%d"%h] = (d["close"].shift(-h) - d["close"]).where(same)
    return d

# ───────────────────────── 2. 규칙 신호 ─────────────────────────
def rule_signals(d):
    S = {}
    sgn = lambda x: np.sign(x).fillna(0)
    S["R1R2_외인Δ10"] = sgn(d["for_d10"])
    S["R1R2_외인Δ30"] = sgn(d["for_d30"])
    S["R1R2_외인Δ10≥300계약"] = sgn(d["for_d10"]).where(d["for_d10"].abs() >= 300, 0).fillna(0)
    S["R3_체결강도Δ5"] = sgn(d["str_d5"])
    S["R3b_체결강도vsMA20"] = sgn(d["str_vs_ma"])
    S["R4_GS≥0.5&상향→SHORT"] = pd.Series(np.where((d["gs20"] >= 0.5) & (d["gs_d3"] > 0), -1, 0), index=d.index)
    S["R5_GB≥0.5&상향→LONG"] = pd.Series(np.where((d["gb20"] >= 0.5) & (d["gb_d3"] > 0), 1, 0), index=d.index)
    S["R4R5_합"] = S["R4_GS≥0.5&상향→SHORT"] + S["R5_GB≥0.5&상향→LONG"]
    both_low = (d["gb20"] < 0.5) & (d["gs20"] < 0.5)
    S["R6_둘다<0.5(금지구역)"] = both_low.astype(int)
    r7l = (d["gs20"] <= 0.1) & (d["gb20"] >= 0.5) & (d["gb_d3"] >= 0.3)
    r7s = (d["gb20"] <= 0.1) & (d["gs20"] >= 0.5) & (d["gs_d3"] >= 0.3)
    S["R7_한쪽≈0&반대급등"] = pd.Series(np.where(r7l, 1, np.where(r7s, -1, 0)), index=d.index)
    S["R8_OBV>시그널"] = sgn(d["obv_hist"])
    S["R8b_OBVΔ5"] = sgn(d["obv_d5"])
    def states(hi, lo):
        brk_up = d["close"] > hi; brk_dn = d["close"] < lo
        ret_hi = (d["sofar_high"] >= hi) & (d["close"] <= hi); ret_lo = (d["sofar_low"] <= lo) & (d["close"] >= lo)
        r9 = pd.Series(np.where(ret_hi & ~ret_lo, -1, np.where(ret_lo & ~ret_hi, 1, 0)), index=d.index)
        r10 = pd.Series(np.where(brk_up, 1, np.where(brk_dn, -1, 0)), index=d.index)
        return r9, r10
    r9d, r10d = states(d["dist_high"], d["dist_low"]); r9s, r10s = states(d["su1"], d["sd1"])
    S["R9_거리모델_되돌림"] = r9d; S["R10_거리모델_돌파"] = r10d
    S["R9_구조모델_되돌림"] = r9s; S["R10_구조모델_돌파"] = r10s
    S["RSI_과매수매도역행"] = pd.Series(np.where(d["rsi14"] >= 70, -1, np.where(d["rsi14"] <= 30, 1, 0)), index=d.index)
    return S

# ───────────────────────── 3. 평가 ─────────────────────────
def nonoverlap(idx_sessions, mins=NONOVERLAP_MIN):
    keep, last = [], {}
    for ts, s in idx_sessions:
        p = last.get(s)
        if p is None or (ts - p).total_seconds() >= mins*60: keep.append(True); last[s] = ts
        else: keep.append(False)
    return np.array(keep, dtype=bool)

def sign_p(daily):
    pos = int((daily > 0).sum()); neg = int((daily < 0).sum())
    return (stats.binomtest(pos, pos+neg, 0.5).pvalue if pos+neg > 0 else np.nan), pos, neg

def evaluate(d, sig, label, window=None, filt=None):
    m = (sig != 0) & d["atr14"].notna() & (d["atr14"] > 1e-6) & (d["hhmm"] < FORCED_EXIT_HHMM) & (d["hhmm"] >= "09:15")
    if window is not None: m &= (d["session"] >= window[0]) & (d["session"] <= window[1])
    if filt is not None: m &= filt.fillna(False)
    ev = d[m].copy(); ev["dir"] = sig[m].astype(int)
    if len(ev) == 0: return {"label": label, "n": 0}
    ev = ev[nonoverlap(list(zip(ev.index, ev["session"])))]
    if len(ev) < 30: return {"label": label, "n": len(ev)}
    by_day = {s: g for s, g in d.groupby("session")}
    pos = {s: {t: i for i, t in enumerate(g.index)} for s, g in by_day.items()}
    nets, reasons = [], []
    for ts, r in ev.iterrows():
        g = by_day[r["session"]]; i = pos[r["session"]][ts]
        net, reason, bars = bracket_sim(g, i, int(r["dir"]), float(r["atr14"]))
        nets.append(net); reasons.append(reason)
    ev["net"] = nets; ev["reason"] = reasons
    for h in (5, 15, 30): ev["sf%d"%h] = ev["dir"] * ev["fwd%d"%h]
    daily = ev.groupby("session")["net"].sum(); dm = ev.groupby("session")["net"].mean()
    p, pp, nn = sign_p(daily)
    t = stats.ttest_1samp(dm.dropna(), 0).pvalue if len(dm) > 3 else np.nan
    d30 = ev.groupby("session")["sf30"].mean().dropna()
    p30 = stats.ttest_1samp(d30, 0).pvalue if len(d30) > 3 else np.nan
    return {"label": label, "n": len(ev), "days": ev["session"].nunique(), "long_share": float((ev["dir"] > 0).mean()),
            "net_per": float(ev["net"].mean()), "net_sum": float(ev["net"].sum()), "day_pos": pp, "day_neg": nn, "sign_p": p, "t_p": t,
            "sf5": float(ev["sf5"].mean()), "sf15": float(ev["sf15"].mean()), "sf30": float(ev["sf30"].mean()), "sf30_p": p30,
            "hit30": float((ev["sf30"] > 0).mean()), "stop_rate": float((ev["reason"] == "stop").mean()),
            "first": ev["session"].min(), "last": ev["session"].max()}

def row(r):
    if r.get("n", 0) < 30: return "| %s | %d | 표본미달 | | | | | | | | | | |" % (r["label"], r.get("n", 0))
    return "| %s | %d | %d | %.0f%% | **%+.0f** | %+.0f | %d/%d | %.3f | %.3f | %+.3f | %+.3f | %.1f%% | %.0f%% |" % (
        r["label"], r["n"], r["days"], r["long_share"]*100, r["net_per"], r["net_sum"], r["day_pos"], r["day_neg"], r["sign_p"], r["t_p"], r["sf5"], r["sf30"], r["hit30"]*100, r["stop_rate"]*100)
HDR = ("| 규칙 | n | 일수 | LONG비중 | 건당 net(원) | net 합 | 일자 +/- | 부호p | t-p | fwd5(pt) | fwd30(pt) | 30m적중 | 스톱률 |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|---|")

# ───────────────────────── 4. 실체결 오버레이 ─────────────────────────
def trade_overlay(d, S):
    t = pd.read_pickle(os.path.join(SNAP, "trades.pkl"))
    t = t[t["exit_ts"].notna()].copy(); t["day"] = t["entry_ts"].str[:10]
    dirn = np.where(t["direction"] == "LONG", 1, -1); qty = t["quantity"].fillna(1).astype(float)
    gross = dirn * (t["exit_price"] - t["entry_price"]) * qty * PT_VALUE
    comm = (t["entry_price"] + t["exit_price"]) * qty * PT_VALUE * RATE_LIVE
    t["net_uni"] = gross - comm
    pos = (t.groupby("entry_ts").agg(day=("day","first"), direction=("direction","first"), src=("entry_source","first"),
           grade=("grade","first"), qty=("quantity","sum"), net_uni=("net_uni","sum")).reset_index())
    pos["dir"] = np.where(pos["direction"] == "LONG", 1, -1)
    dm = pd.DatetimeIndex((pd.to_datetime(pos["entry_ts"]) - pd.Timedelta(minutes=1)).dt.floor("min"))
    for k, s in S.items():
        v = s.reindex(dm).to_numpy(dtype=float)
        pos["al_"+k] = pos["dir"] * v if not k.startswith("R6") else v
    src = d.reindex(dm)
    for c in ["gb20","gs20","for_d10","str_d5","obv_hist","rsi14","hhmm"]: pos[c] = src[c].to_numpy()
    return pos

def overlay_table(pos, keys, title):
    w("### %s (n=%d 포지션, %d일, 단일 실측요율 net 합 %+.0f원)" % (title, len(pos), pos["day"].nunique(), pos["net_uni"].sum()))
    w(""); w("| 규칙 | 일치 n / 건당 / 일자+- / p | 불일치 n / 건당 / 일자+- / p | 무신호 n / 건당 | 일치−불일치 건당 |"); w("|---|---|---|---|---|")
    for k in keys:
        a = pos["al_"+k]
        def cell(mask):
            g = pos[mask]
            if len(g) == 0: return "0", np.nan
            dly = g.groupby("day")["net_uni"].sum(); p, pp, nn = sign_p(dly)
            return "%d / %+.0f / %d-%d / %.2f" % (len(g), g["net_uni"].mean(), pp, nn, p), g["net_uni"].mean()
        c1, m1 = cell(a > 0); c2, m2 = cell(a < 0); g0 = pos[a.fillna(0) == 0]
        c0 = "%d / %+.0f" % (len(g0), g0["net_uni"].mean()) if len(g0) else "0"
        diff = (m1 - m2) if (m1 == m1 and m2 == m2) else np.nan
        w("| %s | %s | %s | %s | %s |" % (k, c1, c2, c0, fmt(diff)))
    w("")

# ───────────────────────── 5. 9/4 · 9/7 당일 대조 ─────────────────────────
def day_dump(d, S, day):
    g = d[d["session"] == day]
    w("### %s — 15분 격자 관측 (값은 그 분 종가 기준, fwd30 = 이후 30분 종가변화 pt)" % day); w("")
    w("| 시각 | 종가 | 외인누계(계약) | 외인Δ10 | 체결강도 | Δ5 | GB20 | GS20 | OBV−sig | RSI | 거리모델 H/L | 구조 up1/dn1 | R9거리 | R10거리 | fwd30 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for ts, r in g.iterrows():
        if ts.minute % 15 != 0: continue
        w("| %s | %.2f | %s | %s | %s | %s | %.2f | %.2f | %s | %s | %.1f/%.1f | %s/%s | %+d | %+d | %s |" % (
            r["hhmm"], r["close"], fmt(r["foreign_futures_net_raw"]), fmt(r["for_d10"]), fmt(r["strength"], "%.2f"), fmt(r["str_d5"], "%+.2f"),
            np.nan_to_num(r["gb20"]), np.nan_to_num(r["gs20"]), fmt(r["obv_hist"]), fmt(r["rsi14"], "%.0f"),
            r["dist_high"], r["dist_low"], fmt(r["su1"], "%.0f"), fmt(r["sd1"], "%.0f"),
            int(S["R9_거리모델_되돌림"][ts]), int(S["R10_거리모델_돌파"][ts]), fmt(r["fwd30"], "%+.2f")))
    w("")
    w("그날 규칙별 30분 방향 적중(신호분 기준, 비중첩 없이 전 분):"); w("")
    w("| 규칙 | 신호 분수 | LONG비중 | 30m 적중 | 평균 fwd30(pt, 방향가중) |"); w("|---|---|---|---|---|")
    for k, s in S.items():
        if k.startswith("R6"): continue
        sg = s.reindex(g.index); m = (sg != 0) & g["fwd30"].notna()
        if m.sum() == 0: w("| %s | 0 | | | |" % k); continue
        sf = sg[m] * g.loc[m, "fwd30"]
        w("| %s | %d | %.0f%% | %.0f%% | %+.2f |" % (k, m.sum(), (sg[m] > 0).mean()*100, (sf > 0).mean()*100, sf.mean()))
    w("")

def spear(a, b):
    m = a.notna() & b.notna()
    if m.sum() < 10: return np.nan
    return stats.spearmanr(a[m], b[m]).statistic

# ───────────────────────── main ─────────────────────────
def main():
    d = build_panel(); S = rule_signals(d)
    d.to_pickle(os.path.join(SNAP, "rules_panel.pkl"))
    days_all = sorted(d["session"].unique())
    inv_days = sorted(d.loc[d["foreign_futures_net_raw"].notna(), "session"].unique())
    str_days = sorted(d.loc[d["strength"].notna(), "session"].unique())
    lvl_days = sorted(d.loc[d["dist_high"].notna(), "session"].unique())
    w("# 발견 규칙 10종 — 미륵이 데이터 백테스트 (원 산출물)"); w("")
    w("생성: %s · 스크립트 `rules_backtest.py`" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")); w("")
    w("## 0. 데이터 가용 범위"); w("")
    w("| 축 | 거래일 | 구간 |"); w("|---|---|---|")
    w("| 분봉(GP·OBV·RSI) | %d | %s ~ %s |" % (len(days_all), days_all[0], days_all[-1]))
    w("| 수급(외인·개인·기관 선물 계약수, 3분 갱신) | %d | %s ~ %s |" % (len(inv_days), inv_days[0], inv_days[-1]))
    w("| 체결강도(buy_vol/sell_vol) | %d | %s ~ %s |" % (len(str_days), str_days[0], str_days[-1]))
    w("| 맥점 레벨(거리·구조 모델) | %d | %s ~ %s |" % (len(lvl_days), lvl_days[0], lvl_days[-1]))
    w("")
    w("시뮬 규약: 신호분 종가 진입 · 스톱 1.5ATR · TP1 0.5ATR(⅓) · TP2 1.5ATR · 최대 30봉 · 15:10 강제청산 · 3분 비중첩 · 왕복수수료 실측 CYBOS %.6f%% · 슬리피지 0 · 09:15 이후 신호만." % (RATE_LIVE*100)); w("")

    w("## A. 신호단위 브래킷 시뮬 — 규칙별 (각 규칙의 가용 전 구간)"); w("")
    w(HDR)
    results = {}
    one = pd.Series(1, index=d.index); mone = pd.Series(-1, index=d.index)
    base_long = evaluate(d, one, "기준선 LONG(전 분)")
    base_short = evaluate(d, mone, "기준선 SHORT(전 분)")
    for k, s in S.items():
        if k.startswith("R6"): continue
        results[k] = evaluate(d, s, k); w(row(results[k]))
    w(row(base_long)); w(row(base_short)); w("")
    win = (inv_days[0], inv_days[-1])
    w("## A2. 같은 창(%s ~ %s, 수급 가용 구간)에서 재비교" % win); w(""); w(HDR)
    resw = {}
    for k, s in S.items():
        if k.startswith("R6"): continue
        resw[k] = evaluate(d, s, k, window=win); w(row(resw[k]))
    w(row(evaluate(d, one, "기준선 LONG", window=win)))
    w(row(evaluate(d, mone, "기준선 SHORT", window=win))); w("")
    w("## A3. 방향별 분해 (같은 창) — LONG 신호만 / SHORT 신호만"); w(""); w(HDR)
    for k in ["R1R2_외인Δ10","R3_체결강도Δ5","R4R5_합","R7_한쪽≈0&반대급등","R8_OBV>시그널","R9_거리모델_되돌림","R10_거리모델_돌파","R9_구조모델_되돌림","R10_구조모델_돌파"]:
        s = S[k]
        w(row(evaluate(d, s.where(s > 0, 0), k+" [LONG만]", window=win)))
        w(row(evaluate(d, s.where(s < 0, 0), k+" [SHORT만]", window=win)))
    w("")
    w("## B. 필터·확증 규칙 — 다른 규칙 신호를 층화"); w("")
    w("### B1. R6 「GB·GS 둘 다 <0.5」 구역이 진입 금지구역인가 (같은 창)"); w(""); w(HDR)
    both = S["R6_둘다<0.5(금지구역)"].astype(bool)
    for k in ["R1R2_외인Δ10","R3_체결강도Δ5","R8_OBV>시그널","R10_거리모델_돌파","R9_거리모델_되돌림"]:
        w(row(evaluate(d, S[k], k+" · R6구역 안", window=win, filt=both)))
        w(row(evaluate(d, S[k], k+" · R6구역 밖", window=win, filt=~both)))
    w(row(evaluate(d, one, "기준선 LONG · R6구역 안", window=win, filt=both)))
    w(row(evaluate(d, one, "기준선 LONG · R6구역 밖", window=win, filt=~both)))
    w(row(evaluate(d, mone, "기준선 SHORT · R6구역 안", window=win, filt=both)))
    w(row(evaluate(d, mone, "기준선 SHORT · R6구역 밖", window=win, filt=~both)))
    w("")
    w("### B2. R8 OBV 확증 — 신호 방향과 OBV(>시그널) 방향 일치 vs 불일치"); w(""); w(HDR)
    obv = S["R8_OBV>시그널"]
    for k in ["R1R2_외인Δ10","R3_체결강도Δ5","R4R5_합","R7_한쪽≈0&반대급등","R10_거리모델_돌파","R9_거리모델_되돌림"]:
        s = S[k]; w(row(evaluate(d, s, k+" · OBV일치", window=win, filt=(s*obv > 0)))); w(row(evaluate(d, s, k+" · OBV불일치", window=win, filt=(s*obv < 0))))
    w("")
    w("### B3. R1/R2 외인 확증 — 신호 방향과 외인Δ10 방향 일치 vs 불일치"); w(""); w(HDR)
    fo = S["R1R2_외인Δ10"]
    for k in ["R3_체결강도Δ5","R4R5_합","R7_한쪽≈0&반대급등","R8_OBV>시그널","R10_거리모델_돌파","R9_거리모델_되돌림"]:
        s = S[k]; w(row(evaluate(d, s, k+" · 외인일치", window=win, filt=(s*fo > 0)))); w(row(evaluate(d, s, k+" · 외인불일치", window=win, filt=(s*fo < 0))))
    w("")
    w("### B4. 다중 합의 — 방향 규칙 5축(외인Δ10·체결강도Δ5·GP R4R5·OBV·거리모델돌파) 합의 수별"); w(""); w(HDR)
    axes = ["R1R2_외인Δ10","R3_체결강도Δ5","R4R5_합","R8_OBV>시그널","R10_거리모델_돌파"]
    vote = sum(S[k] for k in axes)
    for thr in (2, 3, 4, 5):
        sig = pd.Series(np.where(vote >= thr, 1, np.where(vote <= -thr, -1, 0)), index=d.index)
        w(row(evaluate(d, sig, "합의 ≥%d축" % thr, window=win)))
    w("")
    w("## C. 실체결 오버레이 — 진입 결정분(entry_ts−1분)의 규칙 일치/불일치별 손익"); w("")
    pos = trade_overlay(d, S); pos.to_csv(os.path.join(HERE, "out_rules_trades.csv"), index=False, encoding="utf-8-sig")
    keys = [k for k in S if not k.startswith("R6")]
    overlay_table(pos[pos["src"] == "SYSTEM_AUTO"], keys, "SYSTEM_AUTO")
    overlay_table(pos, keys, "전체 진입원(수동·고스트 포함)")
    pa = pos[pos["src"] == "SYSTEM_AUTO"].copy()
    for lab, m in (("R6구역 안(GB·GS<0.5)", pa["al_R6_둘다<0.5(금지구역)"] == 1), ("R6구역 밖", pa["al_R6_둘다<0.5(금지구역)"] == 0)):
        g = pa[m]
        if len(g):
            dly = g.groupby("day")["net_uni"].sum(); p, pp, nn = sign_p(dly)
            w("- SYSTEM_AUTO · %s: n=%d, 건당 %+.0f원, 합 %+.0f, 일자 %d/%d, p=%.2f" % (lab, len(g), g["net_uni"].mean(), g["net_uni"].sum(), pp, nn, p))
    w("")
    w("### C2. SYSTEM_AUTO — 5축 합의 점수(일치 +1 / 불일치 −1)별 손익"); w("")
    pa["score"] = sum(pa["al_"+k].fillna(0) for k in axes)
    w("| 점수 | n | 건당 net | 합 | 일자 +/- | p |"); w("|---|---|---|---|---|---|")
    for v, g in pa.groupby("score"):
        dly = g.groupby("day")["net_uni"].sum(); p, pp, nn = sign_p(dly)
        w("| %+d | %d | %+.0f | %+.0f | %d/%d | %.2f |" % (v, len(g), g["net_uni"].mean(), g["net_uni"].sum(), pp, nn, p))
    w("")
    for cut in (-2, -1, 0, 1):
        lo = pa[pa["score"] <= cut]; hi = pa[pa["score"] > cut]
        w("- 점수 ≤%+d: n=%d 합 %+.0f / >%+d: n=%d 합 %+.0f → ≤%+d 사이즈½ 반사실 통산 %+.0f (현행 %+.0f)" % (
            cut, len(lo), lo["net_uni"].sum(), cut, len(hi), hi["net_uni"].sum(), cut, hi["net_uni"].sum() + lo["net_uni"].sum()*0.5, pa["net_uni"].sum()))
    w("")
    w("## D. 2026-09-04 · 09-07 당일 대조"); w("")
    for day in ("2026-09-04", "2026-09-07"):
        day_dump(d, S, day)
        g = d[d["session"] == day]
        w("- %s 외인누계 vs 종가 상관(분 단위 Spearman): %.3f · 개인: %.3f · 기관: %.3f" % (day,
            spear(g["foreign_futures_net_raw"], g["close"]), spear(g["retail_futures_net_raw"], g["close"]), spear(g["institution_futures_net_raw"], g["close"])))
        w("- %s 외인Δ10 vs fwd30 Spearman: %.3f · 체결강도Δ5 vs fwd30: %.3f · OBV−sig vs fwd30: %.3f · GB−GS vs fwd30: %.3f" % (day,
            spear(g["for_d10"], g["fwd30"]), spear(g["str_d5"], g["fwd30"]), spear(g["obv_hist"], g["fwd30"]), spear(g["gb20"]-g["gs20"], g["fwd30"])))
        tp = pos[pos["day"] == day]
        if len(tp):
            w("- %s 실체결 %d포지션 (SYSTEM_AUTO %d): net 합 %+.0f" % (day, len(tp), int((tp["src"]=="SYSTEM_AUTO").sum()), tp["net_uni"].sum()))
            w(""); w("| 진입 | 방향 | 원천 | net | 외인Δ10 | 체결Δ5 | GB20 | GS20 | OBV−sig | RSI | 일치축(외인·체결·GP·OBV·거리돌파) |"); w("|---|---|---|---|---|---|---|---|---|---|---|")
            for _, r in tp.iterrows():
                al = "".join("+" if r["al_"+k] > 0 else "−" if r["al_"+k] < 0 else "0" for k in axes)
                w("| %s | %s | %s | %+.0f | %s | %s | %.2f | %.2f | %s | %s | %s |" % (r["entry_ts"][11:19], r["direction"], r["src"], r["net_uni"],
                    fmt(r["for_d10"]), fmt(r["str_d5"], "%+.2f"), np.nan_to_num(r["gb20"]), np.nan_to_num(r["gs20"]), fmt(r["obv_hist"]), fmt(r["rsi14"], "%.0f"), al))
        w("")
    w("## E. 일자단위 Spearman IC (연속 축 → fwd30) — 관측단위 거래일"); w("")
    w("| 축 | 일수 | IC 평균 | t | p | 양수일 비율 | 전반/후반 |"); w("|---|---|---|---|---|---|---|")
    for k, col in [("외인Δ10","for_d10"),("외인Δ30","for_d30"),("개인Δ10","ret_d10"),("기관Δ10","ins_d10"),("체결강도Δ5","str_d5"),("체결강도−MA20","str_vs_ma"),("GB20−GS20","gp_dir20"),("GB20","gb20"),("GS20(부호반전)","gs20n"),("OBV−sig","obv_hist"),("OBVΔ5","obv_d5"),("RSI14","rsi14")]:
        if col == "gp_dir20": x = d["gb20"] - d["gs20"]
        elif col == "gs20n": x = -d["gs20"]
        else: x = d[col]
        ics = {}
        for s, g in pd.DataFrame({"x": x, "y": d["fwd30"], "s": d["session"]}).dropna().groupby("s"):
            if len(g) >= 60 and g["x"].nunique() > 2: ics[s] = stats.spearmanr(g["x"], g["y"]).statistic
        ics = pd.Series(ics, dtype=float).dropna()
        if len(ics) < 10: w("| %s | %d | 표본미달 | | | | |" % (k, len(ics))); continue
        tt = stats.ttest_1samp(ics, 0); half = len(ics)//2; srt = ics.sort_index()
        w("| %s | %d | %+.4f | %+.2f | %.4f | %.0f%% | %+.3f / %+.3f |" % (k, len(ics), ics.mean(), tt.statistic, tt.pvalue, (ics > 0).mean()*100, srt.iloc[:half].mean(), srt.iloc[half:].mean()))
    w("")
    rows = list(results.values()) + list(resw.values())
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_rules_signal.csv"), index=False, encoding="utf-8-sig")
    open(os.path.join(HERE, "rules_backtest_report.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))

if __name__ == "__main__":
    main()
