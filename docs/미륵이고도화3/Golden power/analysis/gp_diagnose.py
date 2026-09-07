# -*- coding: utf-8 -*-
"""GP 진단 — SOP §9 1단계(정제) + §2 유형분류 + §3 중복 + §4 IC.

이 단계는 **explore**다. 채택 근거로 쓰지 않는다(SOP §11 K-1).
산출: gp_diagnose_report.md + CSV
"""
from __future__ import annotations

import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gp_lib import (GP_FEATS, PT_VALUE, RATE_LIVE, RATE_PINNED, bonferroni,
                    daily_ic, forward_returns, hour_profile, ic_verdict,
                    load_panel, mask_unmeasured, partial_daily_ic,
                    replay_swing, roundtrip_cost_pt, taxonomy)

HERE = os.path.dirname(os.path.abspath(__file__))
HORIZONS = [1, 3, 5, 10, 15, 30]
PERIOD = 25

# 기존 피처 — GP가 재는 축을 이미 재고 있는 후보 (중복 점검 대상)
EXISTING = ["atr", "atr_ratio", "realized_vol_ann", "va_bandwidth", "vkospi",
            "bb_position", "vwap_position", "poc_distance", "ema_cross",
            "dist_to_high_60m_atr", "dist_to_low_60m_atr",
            "bars_since_high_60m", "bars_since_low_60m",
            "price_extension_atr", "price_extension_atr_60m",
            "rp_dist_to_high_60m_atr", "rp_dist_to_low_60m_atr",
            "ret_1m", "ret_5m", "ret_15m", "hurst", "trend_efficiency",
            "ofi_norm", "cvd_delta_norm", "vpin", "toxicity_score",
            "microprice_bias", "mlofi_norm", "time_sin", "time_cos"]

OUT = []


def w(s=""):
    print(s)
    OUT.append(s)


def main():
    d = load_panel(period=PERIOD)
    d["gp_buy"] = d["golden_buy"]
    d["gp_sell"] = d["golden_sell"]
    fwd = forward_returns(d["close"], d["session"], HORIZONS)
    d = pd.concat([d, fwd, replay_swing(d)], axis=1)
    # 시각 통제용 — 개장 후 경과 분(일중 단조 증가)
    d["mins_open"] = d.groupby("session").cumcount()
    mask_info = mask_unmeasured(d)

    sess = d["session"]
    days = sorted(sess.unique())

    # ---- A. 관찰창 ----
    w("# GOLDEN POWER 실측 진단 (explore)")
    w("")
    w("> SOP `피처_재검증_및_호라이즌배정_원칙.md` 준수. 이 문서는 **구조 확인**이며")
    w("> 채택 근거가 아니다(§11 K-1). 판정은 사전등록 후 홀드아웃 1회.")
    w("")
    w("## A. 관찰창")
    w("")
    w("| 항목 | 값 |")
    w("|---|---|")
    w("| 분봉 수 | %d |" % len(d))
    w("| 거래일 수 | %d |" % len(days))
    w("| 구간 | %s ~ %s |" % (days[0], days[-1]))
    rec = d["bar_recovered"] if "bar_recovered" in d.columns else None
    if rec is not None:
        w("| 복구봉(bar_recovered=1) | %d (%.1f%%) |"
          % (int((rec == 1).sum()), 100.0 * (rec == 1).mean()))
    if "feature_quality_score" in d.columns:
        fq = d["feature_quality_score"]
        w("| raw_features 조인 성공 | %d (%.1f%%) |"
          % (int(fq.notna().sum()), 100.0 * fq.notna().mean()))
    w("| GP 워밍업 결측(gp_range NaN) | %d (%.1f%%) |"
      % (int(d["gp_range"].isna().sum()), 100.0 * d["gp_range"].isna().mean()))
    w("")
    w("🔴 **계측 4원칙 ② 적용 — 미측정을 0으로 두지 않는다.**")
    w("추출은 원천이 안 주는 키를 그대로 담았고, 백필 구간의 미시구조 피처 값은 0이다.")
    w("**세션 내내 상수 0인 날**을 미측정으로 보고 NaN 으로 되돌렸다. 이 보정 없이는")
    w("무정보 구간이 분모에 섞여 상관이 조용히 희석된다.")
    w("")
    w("| 피처 | 미측정 거래일 | 전체 | 비율 |")
    w("|---|---|---|---|")
    for _, r in mask_info.sort_values("masked_days", ascending=False).iterrows():
        if r["masked_days"] == 0:
            continue
        w("| `%s` | %d | %d | %.1f%% |" % (r["feature"], r["masked_days"],
                                           r["total_days"],
                                           100.0 * r["masked_days"] / r["total_days"]))
    w("")
    w("⇒ 비교는 두 계층으로 나눠 읽는다. **백필 재계산 가능**(전 257일 유효)과")
    w("**라이브 전용**(2026-06/07 이후만 유효). 상관은 쌍별 완전관측으로 계산하므로")
    w("계층마다 유효 표본 수가 다르다 — 표의 n 을 함께 볼 것.")
    px = float(d["close"].median())
    w("")
    w("**왕복 비용 기준선** (미니선물 1pt=%s원, 중앙가 %.2f):" % (f"{PT_VALUE:,}", px))
    w("")
    w("| 요율 | 왕복 pt | 왕복 원/계약 | 로그수익 bp |")
    w("|---|---|---|---|")
    for nm, rt in (("실측 CYBOS 0.0098104%", RATE_LIVE),
                   ("캠페인 핀값 0.0015%", RATE_PINNED)):
        c = roundtrip_cost_pt(px, rt)
        w("| %s | %.4f | %s | %.2f |" % (nm, c, f"{c * PT_VALUE:,.0f}", 1e4 * c / px))
    c_slip = roundtrip_cost_pt(px, RATE_LIVE, slip_ticks=1.0)
    w("| 실측 + 편도 1틱 슬리피지 | %.4f | %s | %.2f |"
      % (c_slip, f"{c_slip * PT_VALUE:,.0f}", 1e4 * c_slip / px))

    # ---- B. 산식 재현 ----
    w("")
    w("## B. 산식 독립 재현 (명세서 검증점 대조)")
    w("")
    for day in ("2026-09-04", "2026-09-07"):
        g = d[d["session"] == day]
        if g.empty:
            w("- %s: 데이터 없음" % day)
            continue
        seg = g.between_time("11:20", "11:44")
        nz_b = int((seg["gp_buy"].abs() < 1e-9).sum())
        nz_s = int((seg["gp_sell"].abs() < 1e-9).sum())
        w("- **%s** 11:20~11:44 %d봉 — GB=0 %d봉 / GS=0 %d봉 / gp_range %.3f~%.3f"
          % (day, len(seg), nz_b, nz_s, seg["gp_range"].min(), seg["gp_range"].max()))
    w("")
    w("> 명세서 검증점: 09/04는 GB=0 3연속(11:36~38), 09/07은 GS=0 3연속(11:29·31·32).")

    # ---- C. 유형 분류 ----
    w("")
    w("## C. SOP §2 유형 분류 — 측정 전에 분류한다")
    w("")
    tax_rows = []
    for c in GP_FEATS + ["gp_buy", "gp_sell"]:
        r = taxonomy(d[c], sess, d["hhmm"])
        r["feature"] = c
        tax_rows.append(r)
    for c in ["cvd_delta_norm", "cvd_divergence", "atr", "bb_position"]:
        if c in d.columns and d[c].notna().sum() > 100:
            r = taxonomy(d[c], sess, d["hhmm"])
            r["feature"] = c + " (대조군)"
            tax_rows.append(r)
    tax = pd.DataFrame(tax_rows).set_index("feature")
    tax.to_csv(os.path.join(HERE, "out_taxonomy.csv"), encoding="utf-8-sig")
    w("| 피처 | shape | det_ratio | tie | uniq | 갱신간격 | 일중R2 | ACF1 |")
    w("|---|---|---|---|---|---|---|---|")
    for k, r in tax.iterrows():
        w("| %s | **%s** | %.3f | %.3f | %s | %.1f | %.3f | %.3f |"
          % (k, r.get("shape"), r.get("det_ratio", np.nan), r.get("tie_rate", np.nan),
             r.get("n_unique", ""), r.get("upd_gap_med", np.nan),
             r.get("intraday_r2", np.nan), r.get("acf1", np.nan)))
    w("")
    w("> det_ratio < 0.05 = 결정론형(시계). 건강 대조군 `cvd_delta_norm`(500차 실측 0.970),")
    w("> 오염 사례 `cvd_divergence`(0.554)와 나란히 읽을 것.")

    w("")
    w("### C-2. 시각별 평균 — cvd_divergence 28배 단조감소 교훈")
    w("")
    cols = [c for c in ["gp_range", "gp_dir", "gp_pos", "gp_break_hi", "gp_break_lo",
                        "atr", "cvd_divergence"] if c in d.columns]
    hp = pd.DataFrame({c: hour_profile(d[c], d.index) for c in cols})
    hp.to_csv(os.path.join(HERE, "out_hour_profile.csv"), encoding="utf-8-sig")
    w("| 시 | " + " | ".join(hp.columns) + " |")
    w("|---|" + "---|" * len(hp.columns))
    for h, r in hp.iterrows():
        w("| %02d | " % h + " | ".join("%.4f" % v for v in r) + " |")
    w("")
    w("> `gp_range` 시각별 최대/최소 배율 = **%.2f배** (cvd_divergence 28배 대비)."
      % (hp["gp_range"].max() / max(hp["gp_range"].min(), 1e-9)))

    # ---- D. 중복 ----
    w("")
    w("## D. SOP §3 중복 — GP는 무엇을 새로 재는가")
    w("")
    ex = [c for c in EXISTING if c in d.columns and d[c].notna().sum() > 1000]
    w("대조 대상 기존 피처 %d개: %s" % (len(ex), ", ".join("`%s`" % c for c in ex)))
    w("")
    dup_rows = []
    for g in GP_FEATS + ["gp_buy", "gp_sell"]:
        if d[g].notna().sum() < 1000:
            continue
        # 쌍별 완전관측(pairwise) — 전체 dropna는 결측 많은 한 피처가 표본을 몰살시킨다
        for nm, meth in (("pearson", "pearson"), ("spearman", "spearman")):
            ser = d[ex].corrwith(d[g], method=meth).abs().dropna().sort_values(ascending=False)
            if len(ser) < 3:
                continue
            nb = int((d[g].notna() & d[ser.index[0]].notna()).sum())
            dup_rows.append({"gp": g, "metric": nm, "n": int(d[g].notna().sum()),
                             "n_best": nb,
                             "best": ser.index[0], "r1": ser.iloc[0],
                             "2nd": ser.index[1], "r2": ser.iloc[1],
                             "3rd": ser.index[2], "r3": ser.iloc[2]})
    dup = pd.DataFrame(dup_rows)
    dup.to_csv(os.path.join(HERE, "out_dup.csv"), index=False, encoding="utf-8-sig")
    w("| GP 피처 | 지표 | 최근접 기존피처 | abs r | n(쌍) | 2위 | abs r | 3위 | abs r |")
    w("|---|---|---|---|---|---|---|---|---|")
    for _, r in dup.iterrows():
        w("| %s | %s | `%s` | **%.3f** | %s | `%s` | %.3f | `%s` | %.3f |"
          % (r["gp"], r["metric"], r["best"], r["r1"], f"{int(r['n_best']):,}",
             r["2nd"], r["r2"], r["3rd"], r["r3"]))

    w("")
    w("### D-2. 구성적 중복 (§3 B-5-1 — 상관 이전에 소스에서)")
    w("")
    need = ["gp_sell", "gp_buy", "rp_dist_to_high_60m_atr", "rp_dist_to_low_60m_atr",
            "atr", "close"]
    if all(c in d.columns for c in need):
        sub = d[need].dropna()
        sub = sub[sub["atr"] > 1e-6]
        if len(sub) > 500:
            scale = sub["atr"] / (sub["close"] * 0.005)
            w("- `gp_sell` = (25봉 최고**종가** - 종가) / (종가 x 0.5%%)")
            w("- `rp_dist_to_high_60m_atr` = (60봉 최**고가** - 종가) / ATR  [529차 산식을 전 구간 재계산 — 라이브 배선분은 99.2%% 결측]")
            w("- 두 자의 환산비 `ATR/(종가x0.5%%)` 중앙값 = **%.3f** (IQR %.3f~%.3f), n=%d"
              % (scale.median(), scale.quantile(.25), scale.quantile(.75), len(sub)))
            for a, b in (("gp_sell", "rp_dist_to_high_60m_atr"),
                         ("gp_buy", "rp_dist_to_low_60m_atr")):
                conv = sub[b] * scale
                rs = stats.spearmanr(conv, sub[a]).statistic
                rr = stats.spearmanr(sub[b], sub[a]).statistic
                w("- `%s` vs `%s`: 원본 Spearman **%.3f** / 같은 자로 환산 후 **%.3f**"
                  % (a, b, rr, rs))

    # ---- E. IC ----
    w("")
    w("## E. SOP §4 C-2 일자단위 IC — 관측단위 = 거래일")
    w("")
    cand = ["gp_dir", "gp_range", "gp_pos", "gp_range_drop", "gp_squeeze",
            "gp_break_hi", "gp_break_lo"]
    n_tests = len(cand) * len(HORIZONS)
    ic_rows = []
    for c in cand:
        for h in HORIZONS:
            v = ic_verdict(daily_ic(d[c], d["fwd_%dm" % h], sess))
            v.update(feature=c, horizon=h)
            ic_rows.append(v)
    ic = pd.DataFrame(ic_rows)
    ic["bonf"] = [bonferroni(p, n_tests) for p in ic["p"]]
    ic.to_csv(os.path.join(HERE, "out_ic.csv"), index=False, encoding="utf-8-sig")
    w("검정 수 = %d (피처 %d x 호라이즌 %d) -> Bonferroni a=0.05 임계 p < %.2e"
      % (n_tests, len(cand), len(HORIZONS), 0.05 / n_tests))
    w("")
    w("| 피처 | h | 일수 | IC평균 | t | p | 부호일치 | 전반 | 후반 | 안정 | Bonf |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in ic.sort_values("p").iterrows():
        w("| %s | %dm | %d | %+.4f | %+.2f | %.2e | %.2f | %+.4f | %+.4f | %s | %s |"
          % (r["feature"], r["horizon"], r["n_days"], r["ic_mean"], r["t"], r["p"],
             r["pos_ratio"], r["h1_ic"], r["h2_ic"],
             "O" if r.get("stable") else "X", "**PASS**" if r["bonf"] else "-"))

    w("")
    w("### E-2. 증분 IC — 최근접 기존피처를 통제한 뒤에도 남는가")
    w("")
    best_ctrl = dup[dup["metric"] == "spearman"].set_index("gp")["best"].to_dict()
    w("🔴 **시각(개장 후 경과분)을 함께 통제한다.** `gp_range`는 09시 → 15시로 단조 감소하고")
    w("(§C-2), 일중 수익률에 시각 구조가 있으면 IC가 그것을 대신 잡는다 —")
    w("`cvd_divergence` 28배 사건과 같은 함정이다. 시각 통제 후에도 남아야 진짜다.")
    w("")
    inc_rows = []
    for c in cand:
        ctrl = best_ctrl.get(c)
        if ctrl is None or ctrl not in d.columns:
            continue
        for h in HORIZONS:
            y = d["fwd_%dm" % h]
            raw = ic_verdict(daily_ic(d[c], y, sess))
            p1 = ic_verdict(partial_daily_ic(d[c], y, d[ctrl], sess))
            p2 = ic_verdict(partial_daily_ic(d[c], y, d["mins_open"], sess))
            p3 = ic_verdict(partial_daily_ic(d[c], y, [d[ctrl], d["mins_open"]], sess))
            ret = (abs(p3["ic_mean"]) / abs(raw["ic_mean"])
                   if raw["ic_mean"] == raw["ic_mean"] and raw["ic_mean"] else np.nan)
            inc_rows.append({"feature": c, "ctrl": ctrl, "horizon": h,
                             "ic_raw": raw["ic_mean"], "ic_ctrl": p1["ic_mean"],
                             "ic_time": p2["ic_mean"], "ic_both": p3["ic_mean"],
                             "t_both": p3["t"], "p_both": p3["p"],
                             "n_days": p3["n_days"], "retained": ret,
                             "stable": p3.get("stable")})
    inc = pd.DataFrame(inc_rows)
    inc["bonf"] = [bonferroni(p, len(inc)) for p in inc["p_both"]]
    inc.to_csv(os.path.join(HERE, "out_ic_partial.csv"), index=False, encoding="utf-8-sig")
    w("| 피처 | 최근접 통제 | h | 원 IC | ①피처통제 | ②시각통제 | ③둘다 | 잔존율 | t | p | 안정 | Bonf |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in inc.sort_values("p_both").iterrows():
        w("| %s | `%s` | %dm | %+.4f | %+.4f | %+.4f | **%+.4f** | %.2f | %+.2f | %.2e | %s | %s |"
          % (r["feature"], r["ctrl"], r["horizon"], r["ic_raw"], r["ic_ctrl"],
             r["ic_time"], r["ic_both"], r["retained"], r["t_both"], r["p_both"],
             "O" if r.get("stable") else "X", "**PASS**" if r["bonf"] else "-"))

    # ---- F. 돌파 발생률 ----
    w("")
    w("## F. 돌파 이벤트 발생률 (랜덤워크 기준선 대조)")
    w("")
    valid = d["gp_break_lo"].notna()
    w("| 이벤트 | 건수 | 발생률 | 랜덤워크 기준선 |")
    w("|---|---|---|---|")
    w("| gp_break_lo (25봉 신저종가) | %d | %.1f%% | 12.0%% |"
      % (int(d.loc[valid, "gp_break_lo"].sum()), 100 * d.loc[valid, "gp_break_lo"].mean()))
    w("| gp_break_hi (25봉 신고종가) | %d | %.1f%% | 10.9%% |"
      % (int(d.loc[valid, "gp_break_hi"].sum()), 100 * d.loc[valid, "gp_break_hi"].mean()))

    p = os.path.join(HERE, "gp_diagnose_report.md")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(OUT) + "\n")
    print("\n[saved] %s" % p)
    d.to_pickle(os.path.join(HERE, "_snapshot", "panel.pkl"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
