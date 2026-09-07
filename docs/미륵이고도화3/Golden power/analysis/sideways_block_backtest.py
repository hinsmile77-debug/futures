# -*- coding: utf-8 -*-
"""횡보 레짐(Golden Buy·Sell 둘 다 < 임계) 진입 금지 반사실 백테스트.

질문: 미륵이가 횡보에서 지는가, 그리고 그 구역 진입을 막으면 수익률이 오르는가.
입력: _snapshot/rules_panel.pkl (rules_backtest.py 산출) + _snapshot/trades.pkl
출력: sideways_block_report.md, out_sideways_*.csv
규약: 포지션 단위(계측 4원칙 ①), 단일 실측요율, 일자단위 부호검정 + 최악/최선 3일 제거(313차).
"""
from __future__ import annotations
import os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gp_lib import PT_VALUE, RATE_LIVE
from gp_econ import bracket_sim, FORCED_EXIT_HHMM
from rules_backtest import nonoverlap, sign_p

OUT = []
def w(s=""): OUT.append(s)
def f(v, p="%+,.0f"):
    if v is None or v != v: return "—"
    if p == "%+,.0f": return format(v, "+,.0f")
    return p % v

RNG = np.random.default_rng(20260907)

# ───────────────────────── 데이터 ─────────────────────────
def load():
    d = pd.read_pickle(os.path.join(HERE, "_snapshot", "rules_panel.pkl"))
    # 지속성·레짐 보조 컬럼
    parts = []
    for s, g in d.groupby("session"):
        g = g.copy()
        for per in (20, 25):
            gb, gs = g["gb%d" % per], g["gs%d" % per]
            g["mx%d" % per] = np.maximum(gb, gs)          # 둘 다 < thr  ==  max < thr
            g["rg%d" % per] = gb + gs                      # 20봉 종가 레인지(0.5% 단위)
        # 향후 30분 실현 레인지(횡보 여부의 사후 확인용)
        g["fut_rng30"] = (g["high"][::-1].rolling(30, min_periods=10).max()[::-1]
                          - g["low"][::-1].rolling(30, min_periods=10).min()[::-1])
        g["past_rng30"] = g["high"].rolling(30, min_periods=10).max() - g["low"].rolling(30, min_periods=10).min()
        parts.append(g)
    d = pd.concat(parts).sort_index()
    for per in (20, 25):
        for thr in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
            k = "z%d_%s" % (per, str(thr).replace(".", ""))
            d[k] = (d["mx%d" % per] < thr).astype(float).where(d["mx%d" % per].notna())
    # 지속성: 둘 다 <0.5 가 최근 k분 연속
    for k in (5, 10, 15):
        d["z20_05_run%d" % k] = (d.groupby("session")["z20_05"]
                                 .transform(lambda z: z.rolling(k, min_periods=k).min()))
    return d

def positions(d):
    t = pd.read_pickle(os.path.join(HERE, "_snapshot", "trades.pkl"))
    t = t[t["exit_ts"].notna()].copy()
    t["src"] = t["entry_source"].fillna("NULL_PRE311")
    dirn = np.where(t["direction"] == "LONG", 1, -1); qty = t["quantity"].fillna(1).astype(float)
    gross = dirn * (t["exit_price"] - t["entry_price"]) * qty * PT_VALUE
    comm = (t["entry_price"] + t["exit_price"]) * qty * PT_VALUE * RATE_LIVE
    t["net_uni"] = gross - comm; t["gross_uni"] = gross
    p = (t.groupby("entry_ts")
           .agg(day=("entry_ts", lambda s: s.iloc[0][:10]), direction=("direction", "first"),
                src=("src", "first"), grade=("grade", "first"), qty=("quantity", "sum"),
                entry_qty=("entry_qty", "first"), entry_price=("entry_price", "first"),
                net=("net_uni", "sum"), gross=("gross_uni", "sum"),
                exit_reason=("exit_reason", "first"))
           .reset_index())
    p["dir"] = np.where(p["direction"] == "LONG", 1, -1)
    p["qty_entry"] = p["entry_qty"].fillna(p["qty"]).astype(float).clip(lower=1)
    p["net_per_contract"] = p["net"] / p["qty_entry"]
    dm = pd.DatetimeIndex((pd.to_datetime(p["entry_ts"]) - pd.Timedelta(minutes=1)).dt.floor("min"))
    src = d.reindex(dm)
    cols = ["gb20", "gs20", "mx20", "rg20", "mx25", "rg25", "atr14", "atr_ratio",
            "trend_efficiency", "hurst", "close", "hhmm", "fut_rng30", "past_rng30",
            "z20_05", "z20_05_run5", "z20_05_run10", "z20_05_run15", "for_d10", "obv_hist", "rsi14"]
    for c in cols:
        p[c] = src[c].to_numpy() if c in src.columns else np.nan
    for per in (20, 25):
        for thr in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
            k = "z%d_%s" % (per, str(thr).replace(".", ""))
            p[k] = src[k].to_numpy()
    p["is_sys"] = p["src"].isin(["SYSTEM_AUTO", "NULL_PRE311"])
    # 진입 방향으로 GP 가 이미 0.5 이상 연장돼 있었는가 (앞선 검증의 대조축)
    p["gp_align"] = np.where(p["dir"] == 1, (p["gb20"] >= 0.5), (p["gs20"] >= 0.5)).astype(float)
    p.loc[p["gb20"].isna(), "gp_align"] = np.nan
    return p

# ───────────────────────── 판정 도구 ─────────────────────────
def block_cf(p, zone_col, label):
    """zone_col==1 진입을 (a)전면 차단 (b)사이즈½ 했을 때의 반사실."""
    z = p[zone_col]
    blocked = p[z == 1]; kept = p[z == 0]; unknown = p[z.isna()]
    tot = p["net"].sum()
    d_all = p.groupby("day")["net"].sum()
    d_keep = kept.groupby("day")["net"].sum().reindex(d_all.index).fillna(0.0)
    pv, pp, nn = sign_p(blocked.groupby("day")["net"].sum()) if len(blocked) else (np.nan, 0, 0)
    r = {"label": label, "n_block": len(blocked), "n_keep": len(kept), "n_unknown": len(unknown),
         "block_days": blocked["day"].nunique() if len(blocked) else 0,
         "block_net": blocked["net"].sum() if len(blocked) else 0.0,
         "block_per": blocked["net"].mean() if len(blocked) else np.nan,
         "keep_per": kept["net"].mean() if len(kept) else np.nan,
         "block_per_ct": blocked["net_per_contract"].mean() if len(blocked) else np.nan,
         "keep_per_ct": kept["net_per_contract"].mean() if len(kept) else np.nan,
         "block_win": (blocked["net"] > 0).mean() if len(blocked) else np.nan,
         "keep_win": (kept["net"] > 0).mean() if len(kept) else np.nan,
         "sign_p": pv, "bd_pos": pp, "bd_neg": nn,
         "now": tot, "cf_block": tot - (blocked["net"].sum() if len(blocked) else 0.0),
         "cf_half": tot - 0.5 * (blocked["net"].sum() if len(blocked) else 0.0)}
    # 최악/최선 3일 제거 후에도 차단이 이득인가
    if len(blocked):
        bd = blocked.groupby("day")["net"].sum()
        r["block_net_wo_worst3"] = bd.sum() - bd.nsmallest(3).sum()
        r["block_net_wo_best3"] = bd.sum() - bd.nlargest(3).sum()
    else:
        r["block_net_wo_worst3"] = r["block_net_wo_best3"] = np.nan
    # 일자단위 Welch t (차단군 건당 vs 유지군 건당)
    if len(blocked) >= 5 and len(kept) >= 5:
        r["t_p"] = stats.ttest_ind(blocked["net"], kept["net"], equal_var=False).pvalue
        r["mw_p"] = stats.mannwhitneyu(blocked["net"], kept["net"]).pvalue
    else:
        r["t_p"] = r["mw_p"] = np.nan
    return r

CF_HDR = ("| 컷 | 차단 n(일) | 차단군 건당 | 유지군 건당 | 차단군 승률 | 유지군 승률 | 차단군 net 합 | 최악3일제거 | 최선3일제거 | 일자 +/- | 부호p | MWU p | 전면차단 후 통산 | 사이즈½ 후 |\n"
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
def cf_row(r):
    return "| %s | %d(%d) | %s | %s | %s | %s | %s | %s | %s | %d/%d | %s | %s | **%s** | %s |" % (
        r["label"], r["n_block"], r["block_days"], f(r["block_per"]), f(r["keep_per"]),
        f(r["block_win"]*100, "%.0f%%") if r["block_win"] == r["block_win"] else "—",
        f(r["keep_win"]*100, "%.0f%%") if r["keep_win"] == r["keep_win"] else "—",
        f(r["block_net"]), f(r["block_net_wo_worst3"]), f(r["block_net_wo_best3"]),
        r["bd_pos"], r["bd_neg"], f(r["sign_p"], "%.3f"), f(r["mw_p"], "%.3f"),
        f(r["cf_block"]), f(r["cf_half"]))

def bootstrap_days(p, zone_col, n_boot=5000):
    """거래일 부트스트랩 — 차단 시 통산 개선폭의 신뢰구간."""
    days = p["day"].unique()
    by_day = {dd: g for dd, g in p.groupby("day")}
    gains = []
    for _ in range(n_boot):
        pick = RNG.choice(days, size=len(days), replace=True)
        g = 0.0
        for dd in pick:
            gg = by_day[dd]
            g -= gg.loc[gg[zone_col] == 1, "net"].sum()
        gains.append(g)
    a = np.array(gains)
    return float(a.mean()), float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)), float((a > 0).mean())

# ───────────────────────── main ─────────────────────────
def main():
    d = load(); p = positions(d)
    sysp = p[p["is_sys"]].copy()
    cur = p[p["src"] == "SYSTEM_AUTO"].copy()
    allp = p.copy()

    w("# 횡보 구역(Golden Buy·Sell 둘 다 < 0.5) 진입 금지 — 반사실 백테스트")
    w("")
    w("질문: ① 미륵이가 횡보에서 지는가 ② 그 구역 진입을 막으면 수익률이 오르는가.")
    w("생성: 2026-09-07 · 스크립트 `sideways_block_backtest.py` · 원 산출물 `out_sideways_*.csv`")
    w("")
    w("## 0. 표본")
    w("")
    w("| 군 | 포지션 | 거래일 | 구간 | 단일요율 net 합 | 비고 |")
    w("|---|---|---|---|---|---|")
    for lab, g in (("SYSTEM_AUTO (현행 사이징 체제)", cur),
                   ("+ entry_source NULL (311차 이전 시스템 진입)", sysp),
                   ("전체 진입원 (외부·유령 포함)", allp)):
        w("| %s | %d | %d | %s ~ %s | %s | %s |" % (
            lab, len(g), g["day"].nunique(), g["day"].min(), g["day"].max(), f(g["net"].sum()),
            "MAX_CONTRACTS=3 이후" if lab.startswith("SYSTEM_AUTO") else
            ("06-10~07-10 은 3~10계약 체제 — 사이징 세대 혼재" if lab.startswith("+") else "GHOST 122·MANUAL 3·SYNC 5 포함")))
    w("")
    w("⚠ `entry_source` NULL 62건은 **미측정**이지 외부 진입이 아니다(311차 이전 행, 등급 A/B/C 부여됨 = 시스템 체크리스트 통과). "
      "다만 2026-07-10 이전은 최대 10계약 체제라 손익 규모가 다르므로 **계약당 net** 을 함께 본다(계측 4원칙 ①).")
    w("")

    # ── 1. 횡보 레짐 가설 자체 검증
    w("## 1. 미륵이는 정말 횡보에서 지는가")
    w("")
    w("### 1-1. 진입 결정분의 레짐 축별 4분위 손익 (SYSTEM 248포지션)")
    w("")
    w("| 레짐 축 | Q1(가장 횡보) | Q2 | Q3 | Q4(가장 추세) | Spearman(축, net) | p |")
    w("|---|---|---|---|---|---|---|")
    for lab, col, invert in (("GP 레인지 gp_range20 = GB+GS", "rg20", False),
                             ("GP max(GB,GS)", "mx20", False),
                             ("직전 30분 실현 레인지(pt)", "past_rng30", False),
                             ("ATR ratio", "atr_ratio", False),
                             ("추세 효율 trend_efficiency", "trend_efficiency", False),
                             ("Hurst", "hurst", False)):
        g = sysp.dropna(subset=[col])
        if len(g) < 40:
            w("| %s | 표본미달 n=%d | | | | | |" % (lab, len(g))); continue
        q = pd.qcut(g[col], 4, labels=False, duplicates="drop")
        cells = []
        for i in range(4):
            gg = g[q == i]
            cells.append("%s (n=%d)" % (f(gg["net"].mean()), len(gg)) if len(gg) else "—")
        sp = stats.spearmanr(g[col], g["net"])
        w("| %s | %s | %s | %s | %s | %+.3f | %.3f |" % (lab, cells[0], cells[1], cells[2], cells[3], sp.statistic, sp.pvalue))
    w("")
    w("### 1-2. 「둘 다 < 0.5」 구역 자체의 손익 (군별)")
    w("")
    w("| 군 | 구역 안 n / 건당 / 승률 | 구역 밖 n / 건당 / 승률 | 계약당 net 안 vs 밖 | MWU p |")
    w("|---|---|---|---|---|")
    for lab, g in (("SYSTEM_AUTO", cur), ("SYSTEM 248", sysp), ("전체", allp)):
        a = g[g["z20_05"] == 1]; b = g[g["z20_05"] == 0]
        mw = stats.mannwhitneyu(a["net"], b["net"]).pvalue if len(a) >= 5 and len(b) >= 5 else np.nan
        w("| %s | %d / %s / %s | %d / %s / %s | %s vs %s | %s |" % (
            lab, len(a), f(a["net"].mean()), f((a["net"] > 0).mean()*100, "%.0f%%") if len(a) else "—",
            len(b), f(b["net"].mean()), f((b["net"] > 0).mean()*100, "%.0f%%") if len(b) else "—",
            f(a["net_per_contract"].mean()), f(b["net_per_contract"].mean()), f(mw, "%.3f")))
    w("")
    w("### 1-3. 미륵이가 횡보 구역에 과도하게 진입하는가 (기저율 대조)")
    w("")
    w("| 구역 정의 | 전 분 중 비율 | 진입 결정분 중 비율(SYSTEM 248) | 이항 p | 판정 |")
    w("|---|---|---|---|---|")
    dd = d[(d["hhmm"] >= "09:15") & (d["hhmm"] < FORCED_EXIT_HHMM)]
    dd = dd[(dd["session"] >= sysp["day"].min()) & (dd["session"] <= sysp["day"].max())]
    for thr in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        k = "z20_%s" % str(thr).replace(".", "")
        base = dd[k].mean(); obs = sysp[k].dropna()
        if len(obs) < 20: continue
        kk = int(obs.sum()); nn = len(obs)
        pv = stats.binomtest(kk, nn, base).pvalue
        w("| 둘 다 < %.1f | %.1f%% | %.1f%% (%d/%d) | %.3f | %s |" % (
            thr, base*100, obs.mean()*100, kk, nn, pv,
            "과다진입" if (obs.mean() > base and pv < 0.05) else ("과소진입" if (obs.mean() < base and pv < 0.05) else "차이없음")))
    w("")

    # ── 2. 구역이 실제로 횡보인가
    w("## 2. 그 구역이 실제로 「강력한 횡보」인가 — 사후 확인")
    w("")
    w("| 구역 | 분 수 | 이후 30분 실현 레인지 중앙값(pt) | 구역 밖 중앙값 | 비 | MWU p |")
    w("|---|---|---|---|---|---|")
    for thr in (0.3, 0.5, 0.8):
        k = "z20_%s" % str(thr).replace(".", "")
        a = dd.loc[dd[k] == 1, "fut_rng30"].dropna(); b = dd.loc[dd[k] == 0, "fut_rng30"].dropna()
        mw = stats.mannwhitneyu(a, b).pvalue
        w("| 둘 다 < %.1f | %d | %.2f | %.2f | %.2f배 | %.1e |" % (thr, len(a), a.median(), b.median(), a.median()/b.median(), mw))
    w("")
    w("→ 구역 판정 자체는 맞다(이후 변동성이 실제로 작다). 문제는 **그것이 손익으로 이어지는가**이다.")
    w("")

    # ── 3. 차단 반사실 스윕
    w("## 3. 진입 금지 반사실 — 임계·기간·지속성 스윕")
    w("")
    w("### 3-1. SYSTEM_AUTO 186포지션 (현행 사이징 체제, 2026-07-14~09-07)")
    w("")
    w(CF_HDR)
    rows = []
    for per in (20, 25):
        for thr in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
            k = "z%d_%s" % (per, str(thr).replace(".", ""))
            r = block_cf(cur, k, "GP%d 둘 다 <%.1f" % (per, thr)); rows.append(r); w(cf_row(r))
    for k, lab in (("z20_05_run5", "둘 다 <0.5 가 5분 연속"), ("z20_05_run10", "10분 연속"), ("z20_05_run15", "15분 연속")):
        r = block_cf(cur, k, lab); rows.append(r); w(cf_row(r))
    w("")
    w("### 3-2. SYSTEM 248포지션 (NULL 62건 포함, 2026-06-10~09-07 · 49거래일)")
    w("")
    w(CF_HDR)
    rows2 = []
    for per in (20, 25):
        for thr in (0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
            k = "z%d_%s" % (per, str(thr).replace(".", ""))
            r = block_cf(sysp, k, "GP%d 둘 다 <%.1f" % (per, thr)); rows2.append(r); w(cf_row(r))
    for k, lab in (("z20_05_run5", "둘 다 <0.5 가 5분 연속"), ("z20_05_run10", "10분 연속"), ("z20_05_run15", "15분 연속")):
        r = block_cf(sysp, k, lab); rows2.append(r); w(cf_row(r))
    w("")
    w("### 3-3. 전체 진입원 378포지션 (외부·유령 포함 — 참고)")
    w("")
    w(CF_HDR)
    for per in (20,):
        for thr in (0.3, 0.5, 0.8, 1.0):
            k = "z%d_%s" % (per, str(thr).replace(".", ""))
            w(cf_row(block_cf(allp, k, "GP%d 둘 다 <%.1f" % (per, thr))))
    w("")
    pd.DataFrame(rows + rows2).to_csv(os.path.join(HERE, "out_sideways_cf.csv"), index=False, encoding="utf-8-sig")

    # ── 4. 부트스트랩
    w("## 4. 거래일 부트스트랩 — 차단 개선폭의 불확실성 (5,000회, 거래일 복원추출)")
    w("")
    w("| 군 | 컷 | 개선폭 평균 | 95% CI | 개선>0 확률 |")
    w("|---|---|---|---|---|")
    for lab, g in (("SYSTEM_AUTO 186", cur), ("SYSTEM 248", sysp)):
        for thr in (0.5, 0.8):
            k = "z20_%s" % str(thr).replace(".", "")
            m, lo, hi, pr = bootstrap_days(g, k)
            w("| %s | 둘 다 <%.1f | %s | %s ~ %s | %.0f%% |" % (lab, thr, f(m), f(lo), f(hi), pr*100))
    w("")

    # ── 5. 신호단위 (큰 n) — 구역 안/밖 기준선
    w("## 5. 신호단위 대조 (n 수만) — 구역 안에서 진입하면 정말 나쁜가")
    w("")
    w("체결 표본이 작으므로 같은 질문을 봉 단위 브래킷 시뮬로 다시 묻는다. 매 분 LONG/SHORT 를 넣고 구역 안/밖을 가른다.")
    w("(스톱 1.5ATR / TP1 0.5ATR ⅓ / TP2 1.5ATR / 30봉 / 15:10 청산 / 3분 비중첩 / 실측요율 왕복)")
    w("")
    w("| 창 | 구역 | 방향 | n | 건당 net | 30분 방향가중(pt) | 승률 | 스톱률 | 보유봉 중앙값 |")
    w("|---|---|---|---|---|---|---|---|---|")
    by_day = {s: g for s, g in d.groupby("session")}
    posidx = {s: {t: i for i, t in enumerate(g.index)} for s, g in by_day.items()}
    win_cur = (cur["day"].min(), cur["day"].max())
    for wlab, wrange in (("전 구간 257일", (d["session"].min(), d["session"].max())),
                         ("SYSTEM_AUTO 창 31일", win_cur)):
        base = dd if wlab.startswith("전") else d[(d["hhmm"] >= "09:15") & (d["hhmm"] < FORCED_EXIT_HHMM)]
        base = base[(base["session"] >= wrange[0]) & (base["session"] <= wrange[1])]
        base = base[base["atr14"].notna() & (base["atr14"] > 1e-6)]
        for zlab, mask in (("구역 안(<0.5)", base["z20_05"] == 1), ("구역 밖", base["z20_05"] == 0)):
            ev0 = base[mask]
            ev0 = ev0[nonoverlap(list(zip(ev0.index, ev0["session"])))]
            for dr, dlab in ((1, "LONG"), (-1, "SHORT")):
                nets, reasons, bars = [], [], []
                for ts, r in ev0.iterrows():
                    n_, rs_, b_ = bracket_sim(by_day[r["session"]], posidx[r["session"]][ts], dr, float(r["atr14"]))
                    nets.append(n_); reasons.append(rs_); bars.append(b_)
                nets = np.array(nets); sf = dr * ev0["fwd30"].to_numpy()
                w("| %s | %s | %s | %d | %s | %+.3f | %.1f%% | %.0f%% | %d |" % (
                    wlab, zlab, dlab, len(nets), f(nets.mean()), np.nanmean(sf),
                    (nets > 0).mean()*100, np.mean(np.array(reasons) == "stop")*100, int(np.median(bars))))
    w("")

    # ── 6. 손실 집중 위치 — 횡보가 아니면 어디인가
    w("## 6. 그러면 미륵이 손실은 어디에 몰려 있는가 (SYSTEM 248, 계약당 net)")
    w("")
    w("| 분류 축 | 구간 | n | 건당 net | 계약당 net | 승률 |")
    w("|---|---|---|---|---|---|")
    sysp["hour"] = pd.to_datetime(sysp["entry_ts"]).dt.hour
    for ax, col, bins in (("시각", "hour", None), ("등급", "grade", None), ("방향", "direction", None),
                          ("청산사유", "exit_reason", None), ("진입수량", "qty_entry", None)):
        g = sysp.dropna(subset=[col])
        for v, gg in g.groupby(col):
            if len(gg) < 8: continue
            w("| %s | %s | %d | %s | %s | %.0f%% |" % (ax, v, len(gg), f(gg["net"].mean()),
              f(gg["net_per_contract"].mean()), (gg["net"] > 0).mean()*100))
    w("")
    # GP 모멘텀 정렬(앞선 검증의 확정 발견)과 비교
    w("**대조 — 앞선 검증에서 나온 축(진입 방향으로 GP ≥0.5, 즉 「이미 연장된 쪽으로 진입」):**")
    w("")
    w(CF_HDR)
    w(cf_row(block_cf(sysp, "gp_align", "진입방향 GP20 ≥0.5 (SYSTEM 248)")))
    w(cf_row(block_cf(cur, "gp_align", "진입방향 GP20 ≥0.5 (SYSTEM_AUTO 186)")))
    w("")
    sysp.to_csv(os.path.join(HERE, "out_sideways_positions.csv"), index=False, encoding="utf-8-sig")
    open(os.path.join(HERE, "sideways_block_report.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))

if __name__ == "__main__":
    main()
