# -*- coding: utf-8 -*-
"""보강 — ① 레짐 축 전수(feats.pkl 포함) ② GP 횡보구역과 기존 차단 게이트의 중복도.

기존 게이트: HURST_RANGE_THRESHOLD=0.45(횡보 진입 차단) · ATR_MIN_ENTRY=1.0pt(변동성 부족 차단).
질문: GP 「둘 다 <0.5」가 그 둘이 이미 막는 것 위에 무엇을 더 막는가.
"""
from __future__ import annotations
import os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sideways_block_backtest import load, positions, block_cf, cf_row, CF_HDR, f, w, OUT
from gp_econ import FORCED_EXIT_HHMM
from rules_backtest import sign_p

HURST_RANGE = 0.45
ATR_MIN = 1.0

def main():
    d = load()
    # feats.pkl 병합 — 레짐 축(atr_ratio·hurst·trend_efficiency·va_bandwidth·realized_vol)
    fe = pd.read_pickle(os.path.join(HERE, "_snapshot", "feats.pkl"))
    fe["dt"] = pd.to_datetime(fe["ts"]); fe = fe.drop_duplicates("dt").set_index("dt")
    for c in ["atr_ratio", "hurst", "hurst_ready", "trend_efficiency", "trend_efficiency_ready",
              "va_bandwidth", "realized_vol_ann", "micro_regime_code", "atr"]:
        if c in fe.columns:
            d["fe_" + c] = pd.to_numeric(fe[c], errors="coerce").reindex(d.index)
    # 백필 구간 상수 0 마스킹 (계측 4원칙 ②)
    for c in ["fe_hurst", "fe_trend_efficiency", "fe_realized_vol_ann", "fe_atr_ratio", "fe_va_bandwidth"]:
        if c not in d.columns: continue
        allz = d.groupby("session")[c].transform(lambda z: bool(z.fillna(0).eq(0).all()))
        d.loc[allz.astype(bool), c] = np.nan
    p = positions(d)
    dm = pd.DatetimeIndex((pd.to_datetime(p["entry_ts"]) - pd.Timedelta(minutes=1)).dt.floor("min"))
    src = d.reindex(dm)
    for c in [c for c in d.columns if c.startswith("fe_")]:
        p[c] = src[c].to_numpy()
    sysp = p[p["is_sys"]].copy(); cur = p[p["src"] == "SYSTEM_AUTO"].copy()

    OUT.clear()
    w("# 보강 — 레짐 축 전수 검정 및 기존 게이트와의 중복도")
    w("")
    w("선행: `sideways_block_report.md`. 이 문서는 두 가지만 더 본다 —")
    w("① 「횡보에서 진다」가 GP 말고 **다른 레짐 축**으로는 성립하는가")
    w("② GP 「둘 다 <0.5」가 **이미 있는 차단 게이트**(Hurst<0.45 횡보차단 · ATR<1.0pt 변동성부족차단) 위에 무엇을 더하는가")
    w("")

    # ── 1. 레짐 축 전수
    w("## 1. 레짐 축별 진입 손익 (SYSTEM 248포지션, 결정분 = entry_ts−1분)")
    w("")
    w("| 레짐 축 | 유효 n | Q1(가장 횡보/저변동) | Q2 | Q3 | Q4(가장 추세/고변동) | Spearman | p |")
    w("|---|---|---|---|---|---|---|---|")
    axes = [("GP 레인지 GB+GS", "rg20"), ("GP max(GB,GS)", "mx20"),
            ("직전 30분 실현 레인지(pt)", "past_rng30"), ("ATR(pt)", "fe_atr"),
            ("ATR ratio", "fe_atr_ratio"), ("Hurst", "fe_hurst"),
            ("추세 효율 trend_efficiency", "fe_trend_efficiency"),
            ("실현변동성(연율)", "fe_realized_vol_ann"), ("VA 밴드폭", "fe_va_bandwidth")]
    for lab, col in axes:
        if col not in sysp.columns: w("| %s | 컬럼없음 | | | | | | |" % lab); continue
        g = sysp.dropna(subset=[col])
        g = g[g[col] != 0] if col.startswith("fe_") else g
        if len(g) < 40: w("| %s | %d (표본미달) | | | | | | |" % (lab, len(g))); continue
        q = pd.qcut(g[col], 4, labels=False, duplicates="drop")
        cells = ["%s (n=%d)" % (f(g[q == i]["net"].mean()), (q == i).sum()) if (q == i).sum() else "—" for i in range(4)]
        sp = stats.spearmanr(g[col], g["net"])
        w("| %s | %d | %s | %s | %s | %s | %+.3f | %.3f |" % (lab, len(g), cells[0], cells[1], cells[2], cells[3], sp.statistic, sp.pvalue))
    w("")
    w("일자단위로도 본다 — 그날의 평균 레짐과 그날 손익(관측단위 거래일, SYSTEM 248의 49일):")
    w("")
    w("| 레짐 축(일평균) | 일수 | Spearman(축, 그날 net) | p |")
    w("|---|---|---|---|")
    dayreg = d.groupby("session")[[c for c in ["rg20", "mx20", "fe_hurst", "fe_atr_ratio", "fe_trend_efficiency"] if c in d.columns]].mean()
    daypnl = sysp.groupby("day")["net"].sum()
    for col in dayreg.columns:
        j = pd.concat([dayreg[col], daypnl], axis=1).dropna()
        if len(j) < 15: w("| %s | %d | 표본미달 | |" % (col, len(j))); continue
        sp = stats.spearmanr(j[col], j["net"])
        w("| %s | %d | %+.3f | %.3f |" % (col, len(j), sp.statistic, sp.pvalue))
    w("")

    # ── 2. 기존 게이트와의 중복
    w("## 2. GP 횡보구역과 기존 차단 게이트의 중복도")
    w("")
    dd = d[(d["hhmm"] >= "09:15") & (d["hhmm"] < FORCED_EXIT_HHMM)].copy()
    dd = dd[dd["fe_hurst"].notna() & (dd["fe_hurst"] != 0)]
    dd["gate_hurst"] = (dd["fe_hurst"] < HURST_RANGE).astype(float)
    dd["gate_atr"] = (dd["atr14"] < ATR_MIN).astype(float)
    dd["gate_any"] = ((dd["gate_hurst"] > 0) | (dd["gate_atr"] > 0)).astype(float)
    w("분 단위(라이브 hurst 가용 구간 %s ~ %s, n=%d분):" % (dd["session"].min(), dd["session"].max(), len(dd)))
    w("")
    w("| | GP 구역 안(<0.5) | GP 구역 밖 | 계 |")
    w("|---|---|---|---|")
    for glab, gcol in (("Hurst<0.45 차단 대상", "gate_hurst"), ("ATR<1.0pt 차단 대상", "gate_atr"), ("둘 중 하나라도", "gate_any")):
        a = dd[(dd["z20_05"] == 1) & (dd[gcol] > 0)]; b = dd[(dd["z20_05"] == 0) & (dd[gcol] > 0)]
        za = (dd["z20_05"] == 1).sum(); zb = (dd["z20_05"] == 0).sum()
        w("| %s | %d (%.0f%%) | %d (%.0f%%) | %d |" % (glab, len(a), len(a)/max(za,1)*100, len(b), len(b)/max(zb,1)*100, len(a)+len(b)))
    w("| (분 수) | %d | %d | %d |" % ((dd["z20_05"] == 1).sum(), (dd["z20_05"] == 0).sum(), len(dd)))
    w("")
    ov = dd[(dd["z20_05"] == 1)]
    w("→ GP 구역 %d분 중 **%d분(%.0f%%)** 은 기존 게이트가 이미 막는다. 새로 막히는 것은 **%d분(%.0f%%)** 이다."
      % (len(ov), int((ov["gate_any"] > 0).sum()), (ov["gate_any"] > 0).mean()*100,
         int((ov["gate_any"] == 0).sum()), (ov["gate_any"] == 0).mean()*100))
    w("")
    w("실제 진입에서도 같은 것을 본다(SYSTEM 248 중 hurst 가용 %d건):" % int(sysp["fe_hurst"].notna().sum()))
    w("")
    s2 = sysp[sysp["fe_hurst"].notna() & (sysp["fe_hurst"] != 0)].copy()
    s2["gate_hurst"] = (s2["fe_hurst"] < HURST_RANGE).astype(float)
    w("| 구분 | n | 건당 net | 승률 |")
    w("|---|---|---|---|")
    for lab, m in (("GP구역 안 & Hurst<0.45 (이미 차단 대상)", (s2["z20_05"] == 1) & (s2["gate_hurst"] > 0)),
                   ("GP구역 안 & Hurst≥0.45 (**새로 막히는 것**)", (s2["z20_05"] == 1) & (s2["gate_hurst"] == 0)),
                   ("GP구역 밖 & Hurst<0.45", (s2["z20_05"] == 0) & (s2["gate_hurst"] > 0)),
                   ("GP구역 밖 & Hurst≥0.45", (s2["z20_05"] == 0) & (s2["gate_hurst"] == 0))):
        g = s2[m]
        w("| %s | %d | %s | %s |" % (lab, len(g), f(g["net"].mean()) if len(g) else "—",
                                     f((g["net"] > 0).mean()*100, "%.0f%%") if len(g) else "—"))
    w("")
    w("⚠ Hurst<0.45 진입이 존재하는 이유: 게이트에 예외가 있다 — `entry_mode=MEAN_REVERSION` · "
      "`REGIME_EXHAUSTION` 레짐 · `HURST_SOFT_BLOCK_ENABLED`(333차 후속, 하드차단 대신 사이징 축소).")
    w("")

    # ── 3. 새로 막히는 것만 차단하는 반사실
    w("## 3. 「기존 게이트가 안 막는 GP 구역」만 차단하면")
    w("")
    s2["z_new"] = ((s2["z20_05"] == 1) & (s2["gate_hurst"] == 0)).astype(float)
    cur2 = s2[s2["src"] == "SYSTEM_AUTO"].copy()
    w(CF_HDR)
    w(cf_row(block_cf(s2, "z_new", "GP구역 & Hurst≥0.45 (SYSTEM %d)" % len(s2))))
    if len(cur2) >= 30:
        w(cf_row(block_cf(cur2, "z_new", "GP구역 & Hurst≥0.45 (SYSTEM_AUTO %d)" % len(cur2))))
    w("")

    # ── 4. 최종 정리용 숫자
    w("## 4. 판정 요약 숫자")
    w("")
    z = sysp["z20_05"]
    w("- SYSTEM 248 중 GP 구역 진입: **%d건 / %d건 (%.1f%%)**, 같은 창 전 분 기저율 **%.1f%%**"
      % (int((z == 1).sum()), int(z.notna().sum()), (z == 1).mean()*100,
         d[(d["hhmm"] >= "09:15") & (d["hhmm"] < FORCED_EXIT_HHMM) & (d["session"] >= sysp["day"].min())]["z20_05"].mean()*100))
    w("- 그 %d건의 net 합: **%s원** (건당 %s)" % (int((z == 1).sum()), f(sysp.loc[z == 1, "net"].sum()), f(sysp.loc[z == 1, "net"].mean())))
    w("- SYSTEM_AUTO 186 중 GP 구역 진입: **%d건**, net 합 **%s원**"
      % (int((cur["z20_05"] == 1).sum()), f(cur.loc[cur["z20_05"] == 1, "net"].sum())))
    w("")
    open(os.path.join(HERE, "sideways_regime_axes_report.md"), "w", encoding="utf-8").write("\n".join(OUT))
    print("\n".join(OUT))

if __name__ == "__main__":
    main()
