# -*- coding: utf-8 -*-
"""GP 경제성 백테스트 — 두 트랙.

Track 1 (신호단위, 큰 n)  봉 단위 브래킷 시뮬레이션. 미륵이 사전등록 시뮬 파라미터
                          (VALIDATION_CAMPAIGN[...]["sim"]) 를 그대로 쓴다 — 내가 고른
                          값이 아니라 프로젝트가 이미 고정해 둔 값이다.
Track 2 (체결단위, 작은 n) trades.db 실제 포지션에 GP를 붙여 필터의 반사실 손익.
                          포지션 병합(계측 4원칙 ①) · 일자단위 부호검정(313차 ①).

    python gp_econ.py --phase explore    # 앞 70% 거래일. 가설 생성 전용
    python gp_econ.py --phase confirm    # 뒤 30% 거래일. 사전등록 가설 1회 평가

⚠ explore 결과로 confirm 가설을 정하는 것은 허용되나, 홀드아웃은 겹치면 안 된다.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gp_lib import PT_VALUE, RATE_LIVE, RATE_PINNED, TICK  # noqa: E402

# 미륵이 사전등록 시뮬 파라미터 (config/settings.py VALIDATION_CAMPAIGN 내 "sim")
SIM = {"stop_atr": 1.5, "tp1_atr": 0.5, "tp2_atr": 1.5,
       "tp1_fraction": 0.3333, "max_bars": 30, "atr_window": 14}
NONOVERLAP_MIN = 3          # 313차 ② — 3분 내 중복 신호는 첫 건만
FORCED_EXIT_HHMM = "15:10"  # 절대원칙 §1

OUT = []


def w(s=""):
    print(s)
    OUT.append(s)


def sign_test_p(diffs):
    """일자단위 부호검정(양측). 313차 ①."""
    pos = sum(1 for x in diffs if x > 0)
    neg = sum(1 for x in diffs if x < 0)
    n = pos + neg
    if n == 0:
        return 1.0, 0, 0
    k = min(pos, neg)
    if n > 300:
        mu, sd = n / 2.0, math.sqrt(n / 4.0)
        z = (abs(k - mu) - 0.5) / sd if sd > 0 else 0.0
        return min(1.0, math.erfc(z / math.sqrt(2.0))), pos, neg
    tail = sum(math.comb(n, i) for i in range(0, k + 1))
    return min(1.0, 2.0 * tail / float(2 ** n)), pos, neg


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def true_range(h, l, c_prev):
    return np.maximum(h - l, np.maximum(np.abs(h - c_prev), np.abs(l - c_prev)))


def add_atr(d, win=14):
    out = []
    for _, g in d.groupby("session"):
        tr = true_range(g["high"].to_numpy(float), g["low"].to_numpy(float),
                        np.r_[g["close"].to_numpy(float)[0], g["close"].to_numpy(float)[:-1]])
        out.append(pd.Series(pd.Series(tr, index=g.index).rolling(win, min_periods=win).mean(),
                             index=g.index))
    return pd.concat(out).sort_index()


def bracket_sim(g, i, direction, atr, rate=RATE_LIVE, slip_ticks=0.0,
                stop_dist=None):
    """t=i 봉 종가 진입 → 스톱/TP/최대보유/15:10 중 먼저 오는 것으로 청산.

    보수적 규약: 같은 봉에서 스톱과 TP가 모두 닿으면 **스톱 우선**.
    stop_dist를 주면 스톱 폭만 그 값으로 대체한다(TP는 ATR 기준 유지) —
    Track 3에서 "스톱 규칙만" 바꿔 비교하기 위한 것이다.
    반환: 계약 1개 기준 net 원, 청산 사유, 보유 봉수.
    """
    o = g["open"].to_numpy(float)
    h = g["high"].to_numpy(float)
    l = g["low"].to_numpy(float)
    c = g["close"].to_numpy(float)
    hhmm = g["hhmm"].to_numpy()
    n = len(c)
    entry = c[i] + direction * slip_ticks * TICK
    sd = SIM["stop_atr"] * atr if stop_dist is None else float(stop_dist)
    stop = entry - direction * sd
    tp1 = entry + direction * SIM["tp1_atr"] * atr
    tp2 = entry + direction * SIM["tp2_atr"] * atr
    f1 = SIM["tp1_fraction"]

    gross_pt = 0.0
    remain = 1.0
    reason = "max_bars"
    j = i
    for j in range(i + 1, min(i + 1 + SIM["max_bars"], n)):
        if hhmm[j] >= FORCED_EXIT_HHMM:
            gross_pt += remain * direction * (c[j] - entry)
            remain = 0.0
            reason = "force_1510"
            break
        hit_stop = (l[j] <= stop) if direction > 0 else (h[j] >= stop)
        if hit_stop:
            gross_pt += remain * direction * (stop - entry)
            remain = 0.0
            reason = "stop"
            break
        if remain > 1.0 - f1 + 1e-9:
            hit1 = (h[j] >= tp1) if direction > 0 else (l[j] <= tp1)
            if hit1:
                gross_pt += f1 * direction * (tp1 - entry)
                remain -= f1
                reason = "tp1"
        hit2 = (h[j] >= tp2) if direction > 0 else (l[j] <= tp2)
        if hit2 and remain > 1e-9:
            gross_pt += remain * direction * (tp2 - entry)
            remain = 0.0
            reason = "tp2"
            break
    if remain > 1e-9:
        gross_pt += remain * direction * (c[j] - entry)
    # 수수료: 약정금액 x 요율 x 2(왕복). 슬리피지는 진입가에 이미 반영, 청산분 1틱 추가.
    comm_pt = 2.0 * entry * rate + slip_ticks * TICK
    return (gross_pt - comm_pt) * PT_VALUE, reason, j - i


def build_events(d, kind, ofi_col="ofi_norm", fade=False):
    """돌파 이벤트 목록.

    kind='hi' -> 25봉 신고종가, 'lo' -> 신저종가.
    fade=False 는 추종(돌파 방향), True 는 역방향.
    🔴 양방향을 **둘 다** 돌린다 — 진단 E-2가 `gp_break_lo` 에 +IC(반등),
    `gp_dir`/`gp_pos` 에 -IC(평균회귀)를 보였으므로 추종만 보면 부호를 놓친다.
    검정 수는 이벤트 2 x 방향 2 = 4 이며 아래 표에 전부 표기한다.
    """
    flag = "gp_break_hi" if kind == "hi" else "gp_break_lo"
    direction = (1 if kind == "hi" else -1) * (-1 if fade else 1)
    m = (d[flag] == 1) & d["atr14"].notna() & (d["atr14"] > 1e-6)
    m &= d["hhmm"] < FORCED_EXIT_HHMM
    ev = d[m].copy()
    ev["direction"] = direction
    ev["ofi_signed"] = ev[ofi_col] * direction        # 돌파 방향과 같은 부호면 양수
    # 비중첩 (313차 ②)
    keep, last = [], {}
    for ts in ev.index:
        day = ts.strftime("%Y-%m-%d")
        prev = last.get(day)
        if prev is None or (ts - prev).total_seconds() >= NONOVERLAP_MIN * 60:
            keep.append(True)
            last[day] = ts
        else:
            keep.append(False)
    return ev[pd.Series(keep, index=ev.index)]


def run_events(d, ev, rate=RATE_LIVE, slip=0.0, stop_col=None):
    by_day = {s: g for s, g in d.groupby("session")}
    pos = {s: {t: i for i, t in enumerate(g.index)} for s, g in by_day.items()}
    rows = []
    for ts, r in ev.iterrows():
        s = r["session"]
        g, idx = by_day[s], pos[s]
        i = idx[ts]
        sd = float(r[stop_col]) if (stop_col and r.get(stop_col) == r.get(stop_col)) else None
        net, reason, bars = bracket_sim(g, i, int(r["direction"]), float(r["atr14"]),
                                        rate=rate, slip_ticks=slip, stop_dist=sd)
        rows.append({"ts": ts, "session": s, "direction": int(r["direction"]),
                     "net": net, "reason": reason, "bars": bars,
                     "ofi_signed": r["ofi_signed"], "gp_range": r["gp_range"],
                     "gp_squeeze": r["gp_squeeze"], "atr14": r["atr14"],
                     "cvd_delta_norm": r.get("cvd_delta_norm"),
                     "vpin": r.get("vpin"), "hurst": r.get("hurst")})
    return pd.DataFrame(rows)


def summarize(res, label):
    if len(res) == 0:
        return {"label": label, "n": 0}
    daily = res.groupby("session")["net"].sum()
    p, npos, nneg = sign_test_p(daily.tolist())
    lo, hi = wilson(int((res["net"] > 0).sum()), len(res))
    return {"label": label, "n": len(res), "days": len(daily),
            "net_sum": res["net"].sum(), "net_mean": res["net"].mean(),
            "win_rate": (res["net"] > 0).mean(), "win_lo": lo, "win_hi": hi,
            "day_pos": npos, "day_neg": nneg, "sign_p": p,
            "drop_best3": daily.sort_values(ascending=False).iloc[3:].sum()
            if len(daily) > 3 else np.nan}


def paired_spread(res, cut_col="ofi_signed"):
    """A안의 실제 가설: 확증군 − 비확증군 스프레드가 0보다 큰가.

    같은 거래일 안에서 두 군의 건당 평균을 짝지어 일자단위로 검정한다
    (일별 시장 상황을 통제 — 313차 ① 관측단위 규약).
    """
    r = res[res[cut_col].notna()].copy()
    if len(r) < 40:
        return None
    cut = r[cut_col].median()
    r["grp"] = np.where(r[cut_col] > cut, "conf", "unconf")
    piv = r.pivot_table(index="session", columns="grp", values="net", aggfunc="mean")
    if "conf" not in piv.columns or "unconf" not in piv.columns:
        return None                       # 하루에 한 군만 있으면 짝을 못 짓는다
    piv = piv.dropna()
    if len(piv) < 10:
        return None
    diff = (piv["conf"] - piv["unconf"]).tolist()
    p, npos, nneg = sign_test_p(diff)
    return {"days_paired": len(piv), "spread_mean": float(np.mean(diff)),
            "spread_median": float(np.median(diff)), "day_pos": npos,
            "day_neg": nneg, "sign_p": p, "cut": float(cut)}


def gross_net_split(res, price=1090.0, rate=RATE_LIVE):
    """비용이 엣지를 얼마나 먹는지. gross = net + 왕복수수료."""
    comm = 2.0 * price * rate * PT_VALUE
    return {"gross_mean": res["net"].mean() + comm, "comm_per_trade": comm,
            "net_mean": res["net"].mean()}


def table(rows, cols=None):
    hdr = ["구분", "n", "일수", "net 합(원)", "건당 평균", "승률", "승률 95%CI",
           "일자 +/-", "부호검정 p", "최고3일 제거 net"]
    w("| " + " | ".join(hdr) + " |")
    w("|" + "---|" * len(hdr))
    for r in rows:
        if r.get("n", 0) == 0:
            w("| %s | 0 | - | - | - | - | - | - | - | - |" % r["label"])
            continue
        w("| %s | %d | %d | %s | %s | %.1f%% | %.0f~%.0f%% | %d/%d | %.3f | %s |"
          % (r["label"], r["n"], r["days"], f"{r['net_sum']:+,.0f}",
             f"{r['net_mean']:+,.0f}", 100 * r["win_rate"],
             100 * r["win_lo"], 100 * r["win_hi"], r["day_pos"], r["day_neg"],
             r["sign_p"], f"{r['drop_best3']:+,.0f}" if r["drop_best3"] == r["drop_best3"] else "N/A"))


# ─────────────────────────────────────────────────────────────── Track 2
def track2(d, day_set, ofi_cut, tag):
    """실제 체결 포지션 반사실. 포지션 병합 · 결정분 = entry_ts - 1분."""
    t = pd.read_pickle(os.path.join(HERE, "_snapshot", "trades.pkl"))
    t = t[t["exit_ts"].notna()].copy()
    if "entry_source" in t.columns:
        t = t[t["entry_source"].fillna("") == "SYSTEM_AUTO"]
    t["net"] = t["net_pnl_krw"].fillna(t["pnl_krw"]).astype(float)
    t["day"] = t["entry_ts"].str[:10]
    t = t[t["day"].isin(day_set)]
    if t.empty:
        w("- Track 2 %s: 해당 구간 SYSTEM_AUTO 체결 없음" % tag)
        return None
    pos = (t.groupby("entry_ts")
             .agg(day=("day", "first"), direction=("direction", "first"),
                  net=("net", "sum"), qty=("quantity", "sum"))
             .reset_index())
    pos["dir"] = np.where(pos["direction"] == "LONG", 1, -1)
    dm = pd.DatetimeIndex((pd.to_datetime(pos["entry_ts"])
                           - pd.Timedelta(minutes=1)).dt.floor("min"))
    src = d.reindex(dm)
    for c in ("gp_break_hi", "gp_break_lo", "gp_range", "gp_squeeze", "gp_dir",
              "gp_pos", "ofi_norm", "atr14", "close"):
        pos[c] = src[c].to_numpy() if c in src.columns else np.nan
    pos["gp_break_with"] = np.where(pos["dir"] == 1, pos["gp_break_hi"], pos["gp_break_lo"])
    pos["gp_break_against"] = np.where(pos["dir"] == 1, pos["gp_break_lo"], pos["gp_break_hi"])
    pos["ofi_signed"] = pos["ofi_norm"] * pos["dir"]
    pos["gp_dir_signed"] = pos["gp_dir"] * pos["dir"]
    pos.to_csv(os.path.join(HERE, "out_track2_%s.csv" % tag), index=False, encoding="utf-8-sig")

    w("")
    w("**Track 2 — 실제 체결 포지션 (%s)**  n=%d 포지션 / %d 거래일 / net %s원"
      % (tag, len(pos), pos["day"].nunique(), f"{pos['net'].sum():+,.0f}"))
    w("")
    matched = pos["gp_range"].notna().sum()
    w("- GP 부착 성공: %d/%d (%.0f%%)  ※ 결정분 = entry_ts − 1분(529차 관례)"
      % (matched, len(pos), 100 * matched / len(pos)))
    w("")
    rows = [summarize(pos.rename(columns={"day": "session"}), "전체")]
    sub = pos[pos["gp_range"].notna()].rename(columns={"day": "session"})
    if len(sub):
        q = sub["gp_range"].quantile([0.33, 0.67]).tolist()
        rows += [summarize(sub[sub["gp_range"] <= q[0]], "gp_range 하위⅓(압축)"),
                 summarize(sub[(sub["gp_range"] > q[0]) & (sub["gp_range"] <= q[1])], "gp_range 중위⅓"),
                 summarize(sub[sub["gp_range"] > q[1]], "gp_range 상위⅓(확장)"),
                 summarize(sub[sub["gp_break_with"] == 1], "진입방향 돌파 동반"),
                 summarize(sub[sub["gp_break_with"] != 1], "돌파 없음"),
                 summarize(sub[sub["gp_dir_signed"] > 0], "gp_dir 순방향(레그 끝쪽)"),
                 summarize(sub[sub["gp_dir_signed"] <= 0], "gp_dir 역방향(레그 초입쪽)")]
    table(rows)
    return pos



def track3(dd, phase, k_gp=None):
    """Track 3 — 스톱 **폭 규칙**만 교체해 비교한다.

    현행:  stop = 1.5 x ATR14            (ATR = 봉별 트루레인지의 평균 — 매끄럽다)
    대안:  stop = k x (25봉 종가 엔벨로프) (GP = 극값 기반 — 계단형)

    🔴 k는 **두 규칙의 스톱폭 중앙값이 같아지도록** 보정한다. 보정하지 않으면
       "넓은 스톱 vs 좁은 스톱"을 비교하게 되어 규칙의 우열이 아니라 폭의 효과만 잰다.
       k는 explore에서 정하고 confirm에서는 그 값을 고정해 쓴다.
    """
    ev = dd[(dd["atr14"].notna()) & (dd["atr14"] > 1e-6) & (dd["gp_range"].notna())
            & (dd["hhmm"] < FORCED_EXIT_HHMM) & (dd.index.minute % 15 == 0)].copy()
    if len(ev) < 200:
        w("- Track 3: 표본 부족(%d)" % len(ev))
        return None
    ev["envelope"] = ev["gp_range"] * ev["close"] * 0.005      # 25봉 종가 레인지(pt)
    ev["stop_atr"] = SIM["stop_atr"] * ev["atr14"]
    if k_gp is None:
        k_gp = float(ev["stop_atr"].median() / ev["envelope"].median())
    ev["stop_gp"] = k_gp * ev["envelope"]

    w("")
    w("- 보정계수 k = **%.4f** (스톱폭 중앙값 일치: ATR규칙 %.3f pt vs GP규칙 %.3f pt)"
      % (k_gp, ev["stop_atr"].median(), ev["stop_gp"].median()))
    w("- 두 규칙 스톱폭의 Spearman 상관 = **%.3f** (1.0이면 같은 것을 재는 것)"
      % ev[["stop_atr", "stop_gp"]].corr(method="spearman").iloc[0, 1])
    w("")
    rows = []
    for dirn, dnm in ((1, "LONG"), (-1, "SHORT")):
        ev["direction"] = dirn
        ev["ofi_signed"] = np.nan
        for col, rnm in ((None, "현행 1.5xATR"), ("stop_gp", "GP 엔벨로프 %.3fx" % k_gp)):
            r = run_events(dd, ev.assign(**{"stop_gp": ev["stop_gp"]}), slip=0.0,
                           stop_col=col)
            rows.append(summarize(r, "%s / %s" % (dnm, rnm)))
    table(rows)
    return k_gp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["explore", "confirm"], default="explore")
    ap.add_argument("--holdout-frac", type=float, default=0.30)
    a = ap.parse_args()

    d = pd.read_pickle(os.path.join(HERE, "_snapshot", "panel.pkl"))
    d["atr14"] = add_atr(d, SIM["atr_window"])
    days = sorted(d["session"].unique())
    n_hold = max(1, int(round(len(days) * a.holdout_frac)))
    explore_days, holdout_days = set(days[:-n_hold]), set(days[-n_hold:])
    use = explore_days if a.phase == "explore" else holdout_days
    dd = d[d["session"].isin(use)].copy()

    w("# GP 경제성 백테스트 — %s" % a.phase.upper())
    w("")
    w("- 전체 %d거래일 (%s ~ %s) → explore %d일 / holdout %d일"
      % (len(days), days[0], days[-1], len(explore_days), len(holdout_days)))
    w("- 이번 실행 구간: **%s ~ %s** (%d거래일, %d분봉)"
      % (min(use), max(use), len(use), len(dd)))
    w("- 시뮬 파라미터(미륵이 사전등록값 그대로): %s" % json.dumps(SIM, ensure_ascii=False))
    w("- 비용: 실측 CYBOS 편도 %.6f%% × 왕복. 슬리피지 0틱/1틱 두 버전."
      % (RATE_LIVE * 100))
    w("- 청산: 스톱 1.5ATR / TP1 0.5ATR(⅓) / TP2 1.5ATR / 최대 30봉 / 15:10 강제")
    w("- 동봉 규약: 같은 봉에서 스톱·TP 동시 도달 시 **스톱 우선**(보수적)")

    # ── Track 1 ──
    w("")
    w("## Track 1 — 신호단위 브래킷 시뮬레이션")
    for slip in (0.0, 1.0):
        w("")
        w("### 슬리피지 %d틱 (편도)" % int(slip))
        w("")
        allrows = []
        spreads = []
        for kind, fade, nm in (("hi", False, "신고종가 돌파 → LONG 추종"),
                               ("hi", True,  "신고종가 돌파 → SHORT 페이드"),
                               ("lo", False, "신저종가 돌파 → SHORT 추종"),
                               ("lo", True,  "신저종가 돌파 → LONG 페이드")):
            ev = build_events(dd, kind, fade=fade)
            if ev.empty:
                w("- %s: 이벤트 없음" % nm)
                continue
            res = run_events(dd, ev, slip=slip)
            allrows.append(summarize(res, nm))
            sub = res[res["ofi_signed"].notna()]
            if len(sub) >= 40:
                cut = sub["ofi_signed"].median()
                allrows.append(summarize(sub[sub["ofi_signed"] > cut],
                                         "  └ OFI 확증(상위½)"))
                allrows.append(summarize(sub[sub["ofi_signed"] <= cut],
                                         "  └ OFI 비확증(하위½)"))
            res.to_csv(os.path.join(HERE, "out_track1_%s_%s%s_slip%d.csv"
                                    % (a.phase, kind, "_fade" if fade else "", int(slip))),
                       index=False, encoding="utf-8-sig")
            ps = paired_spread(res)
            gn = gross_net_split(res, price=float(dd["close"].median()))
            spreads.append((nm, ps, gn, len(res)))
        # 기준선: 돌파와 무관한 임의 분(매 15분 격자) 양방향
        base = dd[(dd["atr14"].notna()) & (dd["atr14"] > 1e-6) &
                  (dd["hhmm"] < FORCED_EXIT_HHMM) & (dd.index.minute % 15 == 0)].copy()
        for dirn, nm in ((1, "기준선 LONG(15분 격자)"), (-1, "기준선 SHORT(15분 격자)")):
            base["direction"] = dirn
            base["ofi_signed"] = np.nan
            allrows.append(summarize(run_events(dd, base, slip=slip), nm))
        table(allrows)
        w("")
        w("**A안 핵심 검정 — 확증군 − 비확증군 (같은 거래일 안에서 짝지음)**")
        w("")
        w("| 이벤트 | n | 짝지은 일수 | 스프레드 평균(원/건) | 중앙값 | 일자 +/- | 부호검정 p |")
        w("|---|---|---|---|---|---|---|")
        for nm, ps, gn, nres in spreads:
            if ps is None:
                w("| %s | %d | - | 표본부족 | - | - | - |" % (nm, nres))
                continue
            w("| %s | %d | %d | %s | %s | %d/%d | %.3f |"
              % (nm, nres, ps["days_paired"], f"{ps['spread_mean']:+,.0f}",
                 f"{ps['spread_median']:+,.0f}", ps["day_pos"], ps["day_neg"],
                 ps["sign_p"]))
        w("")
        w("**비용이 먹는 몫** (gross = net + 왕복수수료)")
        w("")
        w("| 이벤트 | gross 평균(원/건) | 왕복수수료 | net 평균 |")
        w("|---|---|---|---|")
        for nm, ps, gn, nres in spreads:
            w("| %s | %s | %s | %s |"
              % (nm, f"{gn['gross_mean']:+,.0f}", f"{gn['comm_per_trade']:,.0f}",
                 f"{gn['net_mean']:+,.0f}"))

    # ── Track 3 ──
    w("")
    w("## Track 3 — 스톱 폭 규칙 비교 (ATR vs GP 엔벨로프, 폭 중앙값 일치 보정)")
    k_path = os.path.join(HERE, "_k_gp.json")
    k_prev = None
    if a.phase == "confirm" and os.path.exists(k_path):
        k_prev = json.load(open(k_path))["k_gp"]
        w("")
        w("- explore에서 고정한 k를 그대로 사용: **%.4f** (사후 재보정 금지)" % k_prev)
    k_used = track3(dd, a.phase, k_gp=k_prev)
    if a.phase == "explore" and k_used:
        json.dump({"k_gp": k_used, "window": [min(use), max(use)]},
                  open(k_path, "w"))

    # ── Track 2 ──
    w("")
    w("## Track 2 — 실제 체결 포지션 반사실")
    track2(d, use, None, a.phase)

    p = os.path.join(HERE, "gp_econ_%s.md" % a.phase)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(OUT) + "\n")
    print("\n[saved] %s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
