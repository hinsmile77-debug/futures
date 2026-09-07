# -*- coding: utf-8 -*-
"""GP 교차 진입신호 검증 — 「GB가 0.5를 상향 돌파 + GS는 0에 수렴」.

사용자 관찰(2026-09-07 12:22 · 13:07 · 14:24): 그 순간 진입하면 수익 청산 확률이 높다.

⚠ **앞서 검정한 R5·R7과 다른 신호다.** 그것들은 「GB≥0.5 상태」(수천 분)였고
이것은 **교차 이벤트**(0.5를 아래에서 위로 통과하는 그 분)다. 상태 결과를 그대로
물려받는다고 가정하지 않고 독립 검정한다.

사전 고정(데이터 보기 전 — SOP §11):
  LONG  : GB20[t-1] < CROSS ≤ GB20[t]  AND  GS20[t] ≤ eps
  SHORT : GS20[t-1] < CROSS ≤ GS20[t]  AND  GB20[t] ≤ eps
  eps ∈ {0.00, 0.05, 0.10, 0.20} · CROSS = 0.5(기본) · 대조군 = eps 조건 없는 순수 교차

측정 축 3개 (사용자 주장은 ②다 — ①만 보고 기각하지 않는다):
  ① 경제성      : 브래킷 시뮬 건당 net (실측 요율)
  ② 수익청산확률: TP 선도달 비율 (여러 (스톱,TP) 격자)
  ③ MFE/MAE     : 청산규칙과 무관한 원 신호 품질

출력: gp_cross_report.md
"""
from __future__ import annotations
import os, sys, warnings, datetime
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gp_lib import PT_VALUE, RATE_LIVE, TICK
from gp_econ import bracket_sim, add_atr, SIM, FORCED_EXIT_HHMM
from rules_backtest import nonoverlap, sign_p

CROSS = 0.5
EPS_GRID = (0.00, 0.05, 0.10, 0.20)
NONOVERLAP_MIN = 3
OUT = []
def w(s=""): OUT.append(s)
def f(v, p="+,.0f"):
    return "—" if (v is None or v != v) else format(v, p)


# ───────────────────────── 패널 ─────────────────────────
def load():
    d = pd.read_pickle(os.path.join(HERE, "_snapshot", "rules_panel.pkl"))
    fe = pd.read_pickle(os.path.join(HERE, "_snapshot", "feats.pkl"))
    fe["dt"] = pd.to_datetime(fe["ts"]); fe = fe.drop_duplicates("dt").set_index("dt")
    for c in ["atr", "atr_ratio", "hurst", "trend_efficiency", "bb_position",
              "vwap_position", "micro_regime_code", "ofi_norm", "cvd_delta_norm",
              "toxicity_score", "spread_ticks", "vpin", "realized_vol_ann"]:
        if c in fe.columns:
            d["fe_" + c] = pd.to_numeric(fe[c], errors="coerce").reindex(d.index)
    for c in [x for x in d.columns if x.startswith("fe_")]:
        allz = d.groupby("session")[c].transform(lambda z: bool(z.fillna(0).eq(0).all()))
        d.loc[allz.astype(bool), c] = np.nan
    # 전봉값 (세션 리셋)
    for c in ("gb20", "gs20"):
        d[c + "_prev"] = d.groupby("session")[c].shift(1)
    return d


def events(d, eps=None, cross=CROSS, require_eps=True):
    """교차 이벤트. eps=None 이면 반대편 조건 없는 순수 교차(대조군)."""
    up_l = (d["gb20_prev"] < cross) & (d["gb20"] >= cross)
    up_s = (d["gs20_prev"] < cross) & (d["gs20"] >= cross)
    if require_eps and eps is not None:
        up_l = up_l & (d["gs20"] <= eps)
        up_s = up_s & (d["gb20"] <= eps)
    sig = pd.Series(np.where(up_l, 1, np.where(up_s, -1, 0)), index=d.index)
    # 동시 성립은 불가(GB·GS 둘 다 0.5 교차 + 반대편 0)이나 방어적으로 0 처리
    sig[up_l & up_s] = 0
    m = (sig != 0) & d["atr14"].notna() & (d["atr14"] > 1e-6) \
        & (d["hhmm"] >= "09:15") & (d["hhmm"] < FORCED_EXIT_HHMM)
    ev = d[m].copy(); ev["dir"] = sig[m].astype(int)
    if len(ev) == 0:
        return ev
    return ev[nonoverlap(list(zip(ev.index, ev["session"])))]


# ───────────────── MFE/MAE + TP선도달 ─────────────────
def excursions(d, ev, horizon=60):
    by_day = {s: g for s, g in d.groupby("session")}
    pos = {s: {t: i for i, t in enumerate(g.index)} for s, g in by_day.items()}
    rows = []
    for ts, r in ev.iterrows():
        g = by_day[r["session"]]; i = pos[r["session"]][ts]
        dr = int(r["dir"]); c0 = float(r["close"]); atr = float(r["atr14"])
        hh = g["high"].to_numpy(float); ll = g["low"].to_numpy(float)
        hhmm = g["hhmm"].to_numpy()
        n = len(g); mfe = 0.0; mae = 0.0
        for j in range(i + 1, min(i + 1 + horizon, n)):
            if hhmm[j] >= FORCED_EXIT_HHMM:
                break
            up = hh[j] - c0; dn = ll[j] - c0
            fav = up if dr > 0 else -dn
            adv = -dn if dr > 0 else up
            mfe = max(mfe, fav); mae = max(mae, adv)
        rows.append({"ts": ts, "session": r["session"], "dir": dr, "atr": atr,
                     "close": c0, "mfe": mfe, "mae": mae,
                     "mfe_atr": mfe / atr, "mae_atr": mae / atr,
                     "hhmm": r["hhmm"]})
    return pd.DataFrame(rows)


def tp_before_stop(d, ev, stop_atr, tp_atr, horizon=60):
    """TP 선도달 비율. 동시 도달 시 스톱 우선(보수)."""
    by_day = {s: g for s, g in d.groupby("session")}
    pos = {s: {t: i for i, t in enumerate(g.index)} for s, g in by_day.items()}
    res = []
    for ts, r in ev.iterrows():
        g = by_day[r["session"]]; i = pos[r["session"]][ts]
        dr = int(r["dir"]); c0 = float(r["close"]); atr = float(r["atr14"])
        stop = c0 - dr * stop_atr * atr; tp = c0 + dr * tp_atr * atr
        hh = g["high"].to_numpy(float); ll = g["low"].to_numpy(float)
        hhmm = g["hhmm"].to_numpy(); n = len(g)
        out = "NEITHER"
        for j in range(i + 1, min(i + 1 + horizon, n)):
            if hhmm[j] >= FORCED_EXIT_HHMM:
                break
            hs = (ll[j] <= stop) if dr > 0 else (hh[j] >= stop)
            ht = (hh[j] >= tp) if dr > 0 else (ll[j] <= tp)
            if hs:
                out = "STOP"; break
            if ht:
                out = "TP"; break
        res.append(out)
    s = pd.Series(res)
    n = len(s)
    return {"n": n, "tp": int((s == "TP").sum()), "stop": int((s == "STOP").sum()),
            "neither": int((s == "NEITHER").sum()),
            "tp_rate": (s == "TP").mean() if n else np.nan,
            "tp_vs_stop": ((s == "TP").sum() / float(max((s == "TP").sum() + (s == "STOP").sum(), 1)))}


def run_sim(d, ev, rate=RATE_LIVE, slip=0.0):
    by_day = {s: g for s, g in d.groupby("session")}
    pos = {s: {t: i for i, t in enumerate(g.index)} for s, g in by_day.items()}
    nets, reasons = [], []
    for ts, r in ev.iterrows():
        g = by_day[r["session"]]; i = pos[r["session"]][ts]
        net, reason, _ = bracket_sim(g, i, int(r["dir"]), float(r["atr14"]),
                                     rate=rate, slip_ticks=slip)
        nets.append(net); reasons.append(reason)
    e = ev.copy(); e["net"] = nets; e["reason"] = reasons
    return e


def summarize(e, label):
    if len(e) < 10:
        return "| %s | %d | 표본미달 | | | | | | |" % (label, len(e))
    daily = e.groupby("session")["net"].sum()
    p, pp, nn = sign_p(daily)
    d3 = daily.sum() - daily.nsmallest(3).sum()
    b3 = daily.sum() - daily.nlargest(3).sum()
    return "| %s | %d | %d | %.0f%% | **%s** | %s | %d/%d | %.3f | %s | %s |" % (
        label, len(e), e["session"].nunique(), (e["dir"] > 0).mean() * 100,
        f(e["net"].mean()), f(e["net"].sum()), pp, nn, p, f(d3), f(b3))

HDR = ("| 신호 | n | 일수 | LONG비중 | 건당 net | net 합 | 일자 +/- | 부호p | 최악3일제거 | 최선3일제거 |\n"
       "|---|---|---|---|---|---|---|---|---|---|")


def main():
    d = load()
    days = sorted(d["session"].unique())
    split = days[int(len(days) * 0.7)]
    w("# GP 교차 신호 검증 — 「GB 0.5 상향돌파 + GS≈0」")
    w("")
    w("생성: %s · 스크립트 `gp_cross_signal.py`" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    w("")
    w("사전 고정 정의: `GB20[t-1] < 0.5 ≤ GB20[t]` **그리고** `GS20[t] ≤ eps` (LONG).")
    w("SHORT 는 대칭. 3분 비중첩 · 09:15~15:09 · 세션 리셋 GP20.")
    w("구간 %s ~ %s (%d거래일). explore/holdout 경계 = **%s**(앞 70%%)."
      % (days[0], days[-1], len(days), split))
    w("")

    # ── 0. 사용자 지목 3시점
    w("## 0. 사용자가 지목한 3시점 — 신호 정의가 그 순간을 잡는가")
    w("")
    g97 = d[d["session"] == "2026-09-07"]
    ev97 = events(d[d["session"] == "2026-09-07"], eps=0.05)
    w("2026-09-07 에 이 정의(eps=0.05)가 잡아낸 LONG 이벤트: **%s**"
      % (", ".join(ev97["hhmm"].tolist()) if len(ev97) else "없음"))
    w("")
    w("| 시각 | 종가 | GB20 | GS20 | 이후 60분 MFE | MAE | fwd30 |")
    w("|---|---|---|---|---|---|---|")
    for t in ("12:22", "13:07", "14:24"):
        rr = g97[g97["hhmm"] == t]
        if not len(rr):
            continue
        r = rr.iloc[0]
        i = g97.index.get_loc(rr.index[0]); fut = g97.iloc[i + 1:i + 61]
        c0 = r["close"]
        w("| %s | %.2f | %.3f | %.3f | %+.2f | %+.2f | %s |"
          % (t, c0, r["gb20"], r["gs20"],
             (fut["high"].max() - c0) if len(fut) else np.nan,
             (fut["low"].min() - c0) if len(fut) else np.nan,
             f(r["fwd30"], "+.2f")))
    w("")

    # ── 1. 이벤트 수와 기본 경제성
    w("## 1. 신호 빈도와 경제성 (전 구간 257일)")
    w("")
    w("시뮬: 스톱 1.5ATR / TP1 0.5ATR(⅓) / TP2 1.5ATR / 최대 30봉 / 15:10 청산 / 실측요율 왕복 / 슬리피지 0.")
    w("")
    w(HDR)
    store = {}
    for eps in EPS_GRID:
        ev = events(d, eps=eps)
        if len(ev) == 0:
            continue
        e = run_sim(d, ev); store[eps] = e
        w(summarize(e, "교차+GS≤%.2f" % eps))
    ev_pure = events(d, eps=None, require_eps=False)
    e_pure = run_sim(d, ev_pure); store["pure"] = e_pure
    w(summarize(e_pure, "**대조** 순수 교차(반대편 조건 없음)"))
    # 방향 분해
    for eps in (0.05,):
        e = store[eps]
        w(summarize(e[e["dir"] > 0], "교차+GS≤%.2f [LONG만]" % eps))
        w(summarize(e[e["dir"] < 0], "교차+GB≤%.2f [SHORT만]" % eps))
    w("")

    # ── 2. 사용자 주장 축: 수익 청산 확률
    w("## 2. 사용자 주장 축 — 「수익 청산 확률」")
    w("")
    w("⚠ 이것은 §1의 건당 net 과 **다른 질문**이다. 스톱이 넓고 TP가 좁으면 승률은 높고 기댓값은 음수일 수 있다.")
    w("아래는 청산 격자별 **TP 선도달 비율**(동시 도달 시 스톱 우선, 60분 창).")
    w("")
    ev05 = events(d, eps=0.05)
    w("| 스톱 | TP | 신호(교차+GS≤0.05) TP선도달 | 대조(순수교차) | 대조(전 분 무작위) | 차이 |")
    w("|---|---|---|---|---|---|")
    # 무작위 대조군 — 같은 시각분포에서 뽑는다
    rng = np.random.default_rng(20260907)
    base = d[(d["hhmm"] >= "09:15") & (d["hhmm"] < FORCED_EXIT_HHMM) & d["atr14"].notna()
             & (d["atr14"] > 1e-6)]
    pick = base.sample(n=min(4000, len(base)), random_state=7).copy()
    pick["dir"] = rng.choice([1, -1], size=len(pick))
    pick = pick[nonoverlap(list(zip(pick.sort_index().index, pick.sort_index()["session"])))] \
        if False else pick
    for stop_atr, tp_atr in ((1.5, 0.5), (1.5, 1.0), (1.0, 1.0), (1.0, 0.5), (2.0, 1.0), (0.5, 0.5)):
        a = tp_before_stop(d, ev05, stop_atr, tp_atr)
        b = tp_before_stop(d, ev_pure, stop_atr, tp_atr)
        c = tp_before_stop(d, pick, stop_atr, tp_atr)
        w("| %.1fATR | %.1fATR | **%.1f%%** (n=%d) | %.1f%% | %.1f%% | %+.1f%%p |"
          % (stop_atr, tp_atr, a["tp_rate"] * 100, a["n"], b["tp_rate"] * 100,
             c["tp_rate"] * 100, (a["tp_rate"] - c["tp_rate"]) * 100))
    w("")
    # 유의성
    a = tp_before_stop(d, ev05, 1.5, 0.5); c = tp_before_stop(d, pick, 1.5, 0.5)
    k1, n1, k2, n2 = a["tp"], a["n"], c["tp"], c["n"]
    p1, p2 = k1 / n1, k2 / n2
    pp = (k1 + k2) / float(n1 + n2)
    se = np.sqrt(pp * (1 - pp) * (1.0 / n1 + 1.0 / n2))
    z = (p1 - p2) / se if se > 0 else np.nan
    pv = 2 * stats.norm.sf(abs(z))
    w("스톱1.5/TP0.5 기준 신호 vs 무작위: **%.1f%% vs %.1f%%**, z=%+.2f, **p=%.4f**"
      % (p1 * 100, p2 * 100, z, pv))
    w("")

    # ── 3. MFE/MAE (청산규칙 무관)
    w("## 3. MFE / MAE — 청산 규칙과 무관한 원 신호 품질")
    w("")
    ex_sig = excursions(d, ev05); ex_pure = excursions(d, ev_pure); ex_rnd = excursions(d, pick)
    w("| 군 | n | MFE 중앙(ATR) | MAE 중앙(ATR) | MFE/MAE 비 | MFE>MAE 비율 |")
    w("|---|---|---|---|---|---|")
    for lab, x in (("교차+GS≤0.05", ex_sig), ("순수 교차", ex_pure), ("무작위 대조", ex_rnd)):
        if not len(x):
            continue
        w("| %s | %d | %.3f | %.3f | %.2f | %.1f%% |"
          % (lab, len(x), x["mfe_atr"].median(), x["mae_atr"].median(),
             x["mfe_atr"].median() / max(x["mae_atr"].median(), 1e-9),
             (x["mfe_atr"] > x["mae_atr"]).mean() * 100))
    if len(ex_sig) and len(ex_rnd):
        u = stats.mannwhitneyu(ex_sig["mfe_atr"] - ex_sig["mae_atr"],
                               ex_rnd["mfe_atr"] - ex_rnd["mae_atr"])
        w("")
        w("(MFE−MAE) 신호 vs 무작위 Mann-Whitney **p=%.4f** — 중앙값 %+.3f vs %+.3f ATR"
          % (u.pvalue, (ex_sig["mfe_atr"] - ex_sig["mae_atr"]).median(),
             (ex_rnd["mfe_atr"] - ex_rnd["mae_atr"]).median()))
    w("")

    # ── 4. explore / holdout
    w("## 4. explore / holdout 분리 (앞 70%% / 뒤 30%%)")
    w("")
    w(HDR)
    for eps in (0.00, 0.05, 0.10):
        e = store.get(eps)
        if e is None:
            continue
        w(summarize(e[e["session"] < split], "교차+GS≤%.2f [explore]" % eps))
        w(summarize(e[e["session"] >= split], "교차+GS≤%.2f [holdout]" % eps))
    w(summarize(e_pure[e_pure["session"] < split], "순수교차 [explore]"))
    w(summarize(e_pure[e_pure["session"] >= split], "순수교차 [holdout]"))
    w("")

    # ── 5. 기존 피처 연동
    w("## 5. 기존 피처와 연동 — 어떤 조건에서 살아나는가")
    w("")
    e = store[0.05].copy()
    for c in ["fe_hurst", "fe_atr", "fe_trend_efficiency", "fe_bb_position",
              "fe_vwap_position", "fe_ofi_norm", "fe_cvd_delta_norm", "fe_toxicity_score",
              "obv_hist", "rsi14", "for_d10", "str_d5", "fe_micro_regime_code"]:
        if c in d.columns:
            e[c] = d[c].reindex(e.index).to_numpy()
    e["obv_align"] = np.sign(e["obv_hist"]) * e["dir"]
    e["ofi_align"] = np.sign(e["fe_ofi_norm"]) * e["dir"]
    w("| 조건 | n | 건당 net | 일자 +/- | 부호p | TP선도달(1.5/0.5) |")
    w("|---|---|---|---|---|---|")

    def cond_row(lab, mask):
        g = e[mask.fillna(False)]
        if len(g) < 15:
            w("| %s | %d | 표본미달 | | | |" % (lab, len(g))); return
        dly = g.groupby("session")["net"].sum(); p, pp, nn = sign_p(dly)
        t = tp_before_stop(d, g, 1.5, 0.5)
        w("| %s | %d | **%s** | %d/%d | %.3f | %.1f%% |"
          % (lab, len(g), f(g["net"].mean()), pp, nn, p, t["tp_rate"] * 100))

    cond_row("전체", pd.Series(True, index=e.index))
    cond_row("OBV 일치", e["obv_align"] > 0)
    cond_row("OBV 불일치", e["obv_align"] < 0)
    cond_row("OFI 일치", e["ofi_align"] > 0)
    cond_row("OFI 불일치", e["ofi_align"] < 0)
    if "fe_hurst" in e:
        cond_row("Hurst ≥0.45 (추세)", e["fe_hurst"] >= 0.45)
        cond_row("Hurst <0.45 (횡보)", e["fe_hurst"] < 0.45)
    cond_row("ATR ≥ 중앙", e["fe_atr"] >= e["fe_atr"].median())
    cond_row("ATR < 중앙", e["fe_atr"] < e["fe_atr"].median())
    cond_row("RSI < 70", e["rsi14"] < 70)
    cond_row("RSI ≥ 70 (과열)", e["rsi14"] >= 70)
    cond_row("오전 (~11:59)", e["hhmm"] < "12:00")
    cond_row("오후 (12:00~)", e["hhmm"] >= "12:00")
    cond_row("외인Δ10 일치", np.sign(e["for_d10"]) * e["dir"] > 0)
    cond_row("체결강도Δ5 일치", np.sign(e["str_d5"]) * e["dir"] > 0)
    w("")

    # ── 6. 실체결 겹침
    w("## 6. 미륵이가 이 순간에 실제로 진입했는가")
    w("")
    t = pd.read_pickle(os.path.join(HERE, "_snapshot", "trades.pkl"))
    t = t[t["exit_ts"].notna()].copy()
    dirn = np.where(t["direction"] == "LONG", 1, -1); qty = t["quantity"].fillna(1).astype(float)
    t["net_uni"] = dirn * (t["exit_price"] - t["entry_price"]) * qty * PT_VALUE \
        - (t["entry_price"] + t["exit_price"]) * qty * PT_VALUE * RATE_LIVE
    p = t.groupby("entry_ts").agg(direction=("direction", "first"), src=("entry_source", "first"),
                                  net=("net_uni", "sum")).reset_index()
    p["dir"] = np.where(p["direction"] == "LONG", 1, -1)
    dm = pd.DatetimeIndex((pd.to_datetime(p["entry_ts"]) - pd.Timedelta(minutes=1)).dt.floor("min"))
    ev_idx = set(store[0.05].index)
    p["on_signal"] = [ts in ev_idx for ts in dm]
    ps = p[p["src"] == "SYSTEM_AUTO"]
    w("- SYSTEM_AUTO %d포지션 중 이 신호분(결정분 기준)에 진입한 것: **%d건**"
      % (len(ps), int(ps["on_signal"].sum())))
    w("- 전체 %d포지션 중: **%d건**" % (len(p), int(p["on_signal"].sum())))
    if int(p["on_signal"].sum()):
        w("- 그 건들의 net 합: %s원" % f(p.loc[p["on_signal"], "net"].sum()))
    w("")
    w("신호 %d건 중 미륵이가 실제로 진입한 비율: **%.1f%%**"
      % (len(store[0.05]), p["on_signal"].sum() / float(len(store[0.05])) * 100))
    w("")

    # 저장
    store[0.05].to_csv(os.path.join(HERE, "out_gp_cross_events.csv"),
                       encoding="utf-8-sig")
    open(os.path.join(HERE, "gp_cross_report.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
