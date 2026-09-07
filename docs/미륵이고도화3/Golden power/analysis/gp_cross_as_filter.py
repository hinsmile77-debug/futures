# -*- coding: utf-8 -*-
"""GP 교차를 **기존 미륵이 진입의 확증 필터**로 썼을 때의 손익.

두 가지를 함께 낸다.
  A. 단독 진입신호로 썼을 때 (요약 재게시)
  B. 확증 필터로 썼을 때 — 「진입 결정분 직전 k분 안에 정렬 GP 교차가 있었는가」로
     실체결을 갈라 반사실 손익을 계산한다.

정렬 정의: LONG 진입이면 GB20 이 0.5 를 상향 통과, SHORT 진입이면 GS20 이 상향 통과.
역행 정의: 그 반대.

출력: gp_cross_filter_report.md
"""
from __future__ import annotations
import os, sys, warnings, sqlite3, re, json
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = r"C:\Users\82108\PycharmProjects\futures"
from gp_lib import PT_VALUE, RATE_LIVE
from gp_econ import FORCED_EXIT_HHMM
from gp_cross_signal import load
from gp_cross_exitgrid import simple_bracket
from rules_backtest import sign_p, nonoverlap

OUT = []
def w(s=""): OUT.append(s)
def f(v, p="+,.0f"):
    return "—" if (v is None or v != v) else format(v, p)

CROSS = 0.5


def cross_flags(d, eps=None):
    """봉별 교차 플래그. eps=None 이면 반대편 조건 없음(사용자 문구 「GB 0.5 상방돌파」)."""
    up_b = (d["gb20_prev"] < CROSS) & (d["gb20"] >= CROSS)
    up_s = (d["gs20_prev"] < CROSS) & (d["gs20"] >= CROSS)
    if eps is not None:
        up_b = up_b & (d["gs20"] <= eps)
        up_s = up_s & (d["gb20"] <= eps)
    return up_b.astype(float), up_s.astype(float)


def positions():
    t = pd.read_pickle(os.path.join(HERE, "_snapshot", "trades.pkl"))
    t = t[t["exit_ts"].notna()].copy()
    t["src"] = t["entry_source"].fillna("NULL_PRE311")
    dirn = np.where(t["direction"] == "LONG", 1, -1)
    qty = t["quantity"].fillna(1).astype(float)
    gross = dirn * (t["exit_price"] - t["entry_price"]) * qty * PT_VALUE
    comm = (t["entry_price"] + t["exit_price"]) * qty * PT_VALUE * RATE_LIVE
    t["net_uni"] = gross - comm
    p = (t.groupby("entry_ts")
           .agg(day=("entry_ts", lambda s: s.iloc[0][:10]),
                direction=("direction", "first"), src=("src", "first"),
                grade=("grade", "first"), qty=("quantity", "sum"),
                entry_qty=("entry_qty", "first"), net=("net_uni", "sum"))
           .reset_index())
    p["dir"] = np.where(p["direction"] == "LONG", 1, -1)
    p["is_sys"] = p["src"].isin(["SYSTEM_AUTO", "NULL_PRE311"])
    return p


def attach(d, p, eps):
    """각 포지션에 「직전 k분 안에 정렬/역행 교차가 있었나」를 붙인다."""
    up_b, up_s = cross_flags(d, eps=eps)
    d = d.copy(); d["xb"] = up_b; d["xs"] = up_s
    # 세션 내 롤링 합 — 창 k 안에 교차가 1회라도 있으면 1
    out = {}
    for k in (0, 1, 2, 3, 5, 10, 15, 20, 30):
        win = k + 1
        d["xb_%d" % k] = d.groupby("session")["xb"].transform(
            lambda z: z.rolling(win, min_periods=1).max())
        d["xs_%d" % k] = d.groupby("session")["xs"].transform(
            lambda z: z.rolling(win, min_periods=1).max())
    dm = pd.DatetimeIndex((pd.to_datetime(p["entry_ts"]) - pd.Timedelta(minutes=1)).dt.floor("min"))
    src = d.reindex(dm)
    p = p.copy()
    for k in (0, 1, 2, 3, 5, 10, 15, 20, 30):
        b = src["xb_%d" % k].to_numpy(); s = src["xs_%d" % k].to_numpy()
        # 정렬 = LONG이면 GB교차, SHORT이면 GS교차
        p["align_%d" % k] = np.where(p["dir"] == 1, b, s)
        p["against_%d" % k] = np.where(p["dir"] == 1, s, b)
    for c in ("gb20", "gs20", "atr14", "close", "hhmm"):
        p[c] = src[c].to_numpy() if c in src.columns else np.nan
    p["atr_bp"] = p["atr14"] / p["close"] * 10000
    return p


def cell(g):
    if len(g) == 0:
        return "0", np.nan
    dly = g.groupby("day")["net"].sum()
    pv, pp, nn = sign_p(dly)
    return "%d / %s / %d-%d / %.2f" % (len(g), f(g["net"].mean()), pp, nn, pv), g["net"].mean()


def main():
    d = load()
    p = positions()
    sysp_all = p[p["is_sys"]]
    cur_all = p[p["src"] == "SYSTEM_AUTO"]

    w("# GP 교차 — 단독 진입신호 vs 기존 진입의 확증 필터")
    w("")
    w("정렬 = LONG 진입이면 `GB20` 이 0.5 상향통과 · SHORT 진입이면 `GS20` 상향통과.")
    w("판정 기준분 = `entry_ts − 1분`(결정분). 창 k = 결정분 포함 직전 k분 안에 1회라도 교차.")
    w("손익은 전 구간 **단일 실측요율 net**(2026-08-25 요율 세대 불연속 제거).")
    w("")

    # ── A. 단독
    w("## A. 단독 진입신호로 썼을 때 (요약)")
    w("")
    w("상세는 `GP교차신호_검증_MW0601-20260907.md`. 핵심만 재게시한다.")
    w("")
    w("| 사용법 | n | 건당 net | 판정 |")
    w("|---|---|---|---|")
    w("| 무조건 (교차+반대편≤0.05, 스톱1.5/TP0.5) | 1,954 | **−6,141** | 🔴 청산격자 19개 전부 net 음수 |")
    w("| 상대ATR ≥16bp 로 좁힘 | 116 | **+6,513** | 🟢 일자 54/18 p=0.0003 (사후발견) |")
    w("")
    w("승률 75.6%는 무작위 73.2% 대비 유의하나(p=0.044), 그 격자의 **손익분기 승률이 정확히 75.0%**라")
    w("초과분은 +0.6%p뿐이다. 엣지(+3,026원/건)가 왕복 비용(7,596원)의 40%에 그친다.")
    w("")

    # ── B. 확증 필터
    for eps, epslab in ((None, "순수 교차 — 「GB 0.5 상방돌파」 그대로"),
                        (0.05, "교차 + 반대편 ≤0.05")):
        pa = attach(d, p, eps)
        sysp = pa[pa["is_sys"]]
        cur = pa[pa["src"] == "SYSTEM_AUTO"]
        w("## B%s. 확증 필터로 썼을 때 — %s" % ("1" if eps is None else "2", epslab))
        w("")
        for lab, g in (("SYSTEM_AUTO %d포지션 (2026-07-14~09-07, 31일)" % len(cur), cur),
                       ("SYSTEM %d포지션 (NULL 62건 포함, 2026-06-10~, 49일)" % len(sysp), sysp)):
            w("### %s — 통산 %s원" % (lab, f(g["net"].sum())))
            w("")
            w("| 창 | 정렬교차 동반 n / 건당 / 일자+- / p | 미동반 n / 건당 / 일자+- / p | 차이 | **동반만 남기면 통산** | 미동반 사이즈½ |")
            w("|---|---|---|---|---|---|---|")
            tot = g["net"].sum()
            for k in (0, 1, 2, 3, 5, 10, 15, 20, 30):
                a = g[g["align_%d" % k] == 1]
                b = g[g["align_%d" % k] == 0]
                c1, m1 = cell(a); c2, m2 = cell(b)
                diff = (m1 - m2) if (m1 == m1 and m2 == m2) else np.nan
                keep = a["net"].sum()
                half = a["net"].sum() + 0.5 * b["net"].sum()
                w("| %d분 | %s | %s | %s | **%s** | %s |"
                  % (k, c1, c2, f(diff), f(keep), f(half)))
            w("")
        # 역행 교차 경고 (창 5분 고정)
        w("**역행 교차(진입 반대방향으로 교차)가 직전 5분에 있었던 진입** — SYSTEM %d포지션:" % len(sysp))
        w("")
        w("| 구분 | n | 건당 net | 일자 +/- | p |")
        w("|---|---|---|---|---|")
        for lab2, m in (("역행 교차 있음", sysp["against_5"] == 1),
                        ("역행 교차 없음", sysp["against_5"] == 0)):
            gg = sysp[m.fillna(False)]
            c, _ = cell(gg)
            w("| %s | %s |" % (lab2, c.replace(" / ", " | ")))
        w("")

    # ── C. 고변동 결합
    pa = attach(d, p, 0.05)
    sysp = pa[pa["is_sys"]]
    w("## C. 고변동(상대ATR ≥16bp) 조건과 결합")
    w("")
    w("단독 사용에서 유일하게 흑자였던 컷을 필터에도 걸어본다.")
    w("")
    w("| 조건 (SYSTEM %d포지션) | n | 건당 net | net 합 | 일자 +/- | p |" % len(sysp))
    w("|---|---|---|---|---|---|")
    for lab, m in (("전체", pd.Series(True, index=sysp.index)),
                   ("상대ATR ≥16bp", sysp["atr_bp"] >= 16),
                   ("상대ATR <16bp", sysp["atr_bp"] < 16),
                   ("정렬교차(5분) 동반", sysp["align_5"] == 1),
                   ("정렬교차 동반 & ≥16bp", (sysp["align_5"] == 1) & (sysp["atr_bp"] >= 16)),
                   ("정렬교차 동반 & <16bp", (sysp["align_5"] == 1) & (sysp["atr_bp"] < 16)),
                   ("정렬교차 없음 & ≥16bp", (sysp["align_5"] == 0) & (sysp["atr_bp"] >= 16))):
        gg = sysp[m.fillna(False)]
        if len(gg) == 0:
            w("| %s | 0 | | | | |" % lab); continue
        dly = gg.groupby("day")["net"].sum(); pv, pp, nn = sign_p(dly)
        w("| %s | %d | %s | %s | %d/%d | %.3f |"
          % (lab, len(gg), f(gg["net"].mean()), f(gg["net"].sum()), pp, nn, pv))
    w("")

    # ── D. 왜 교집합이 거의 없나 — 신호분의 차단 사유
    w("## D. 왜 겹치지 않는가 — 신호가 뜬 분에 미륵이는 무엇을 하고 있었나")
    w("")
    try:
        con = sqlite3.connect("file:%s?mode=ro"
                              % os.path.join(ROOT, "data", "db", "predictions.db").replace("\\", "/"),
                              uri=True)
        ed = pd.read_sql_query(
            "SELECT ts, entry_block_reason, entry_final_ok, entry_executed, grade, auto_entry "
            "FROM ensemble_decisions", con)
        con.close()
        ed["dt"] = pd.to_datetime(ed["ts"])
        ed = ed.drop_duplicates("dt").set_index("dt")
        up_b, up_s = cross_flags(d, eps=0.05)
        sig_idx = d.index[(up_b > 0) | (up_s > 0)]
        sig_idx = sig_idx[(sig_idx >= ed.index.min()) & (sig_idx <= ed.index.max())]
        j = ed.reindex(sig_idx).dropna(subset=["ts"])
        w("`ensemble_decisions` 가 있는 구간(2026-05-08~)에서 이 신호가 뜬 분 **%d개**를 대조했다." % len(j))
        w("")
        w("| 그 분의 상태 | 건수 | 비중 |")
        w("|---|---|---|")
        def short(r):
            r = r or ""
            if not r.strip():
                return "차단사유 없음"
            m = re.match(r"\[차단\]\s*([^\d]{0,18})", r)
            return (m.group(1).strip() if m else r[:18])
        vc = j["entry_block_reason"].map(short).value_counts()
        for k2, v2 in vc.head(12).items():
            w("| %s | %d | %.1f%% |" % (k2, v2, v2 / len(j) * 100))
        w("")
        w("- 그 분에 **실제 진입 집행**된 것: **%d건** (`entry_executed`)"
          % int(pd.to_numeric(j["entry_executed"], errors="coerce").fillna(0).sum()))
        w("- 등급 분포: %s"
          % ", ".join("%s %d" % (a, b) for a, b in j["grade"].value_counts().head(6).items()))
    except Exception as exc:
        w("(ensemble_decisions 대조 실패: %s)" % exc)
    w("")
    pa.to_csv(os.path.join(HERE, "out_gp_cross_filter.csv"), index=False, encoding="utf-8-sig")
    open(os.path.join(HERE, "gp_cross_filter_report.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
