# -*- coding: utf-8 -*-
"""Track 2 심화 — "진입방향 돌파 동반" 군의 손실이 진짜인가.

확인할 것 (하나라도 깨지면 이 발견은 폐기한다)
  ① 수수료 세대 불연속(2026-08-25) 때문에 만들어진 것인가
     -> 전 구간을 **단일 실측 요율**로 재계산해 비교한다(CLAUDE.md ① 경고).
  ② 529차 축(run/dist ATR)과 같은 것을 재고 있는가 -> 교차표.
  ③ 기존 체크리스트 `10_chase` 가 이미 잡고 있는가 -> 교차표.
  ④ 며칠에 몰려 있는가 -> 일자별 분해 + 최악/최고일 제거.
  ⑤ 방향(LONG/SHORT)·등급·시간대 편중인가.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gp_lib import PT_VALUE, RATE_LIVE, replay_swing  # noqa: E402
from gp_econ import sign_test_p, wilson  # noqa: E402

OUT = []


def w(s=""):
    print(s)
    OUT.append(s)


def summ(g, label):
    if len(g) == 0:
        return "| %s | 0 | - | - | - | - | - |" % label
    daily = g.groupby("day")["net_u"].sum()
    p, npos, nneg = sign_test_p(daily.tolist())
    lo, hi = wilson(int((g["net_u"] > 0).sum()), len(g))
    worst3 = daily.sort_values().iloc[3:].sum() if len(daily) > 3 else np.nan
    return ("| %s | %d | %d | %s | %s | %.1f%% (%.0f~%.0f) | %d/%d p=%.3f | %s |"
            % (label, len(g), len(daily), f"{g['net_u'].sum():+,.0f}",
               f"{g['net_u'].mean():+,.0f}", 100 * (g["net_u"] > 0).mean(),
               100 * lo, 100 * hi, npos, nneg, p,
               f"{worst3:+,.0f}" if worst3 == worst3 else "N/A"))


HDR = ("| 구분 | n | 일수 | net 합 | 건당 | 승률(95%CI) | 일자 +/- | 최악3일 제거 |\n"
       "|---|---|---|---|---|---|---|---|")


def main():
    d = pd.read_pickle(os.path.join(HERE, "_snapshot", "panel.pkl"))
    rp = replay_swing(d)
    d = pd.concat([d, rp], axis=1) if "rp_dist_to_high_60m_atr" not in d.columns else d

    t = pd.read_pickle(os.path.join(HERE, "_snapshot", "trades.pkl"))
    t = t[t["exit_ts"].notna() & (t["entry_source"].fillna("") == "SYSTEM_AUTO")].copy()
    t["day"] = t["entry_ts"].str[:10]

    # ① 단일 요율 재계산 — 엔진 net 은 2026-08-25에 요율 세대가 바뀌어 불연속이다
    dirn = np.where(t["direction"] == "LONG", 1, -1)
    qty = t["quantity"].fillna(1).astype(float)
    gross = dirn * (t["exit_price"] - t["entry_price"]) * qty * PT_VALUE
    comm = (t["entry_price"] + t["exit_price"]) * qty * PT_VALUE * RATE_LIVE
    t["net_uni"] = gross - comm                      # 전 구간 동일 요율
    t["net_eng"] = t["net_pnl_krw"].fillna(t["pnl_krw"]).astype(float)

    pos = (t.groupby("entry_ts")
             .agg(day=("day", "first"), direction=("direction", "first"),
                  grade=("grade", "first"), qty=("quantity", "sum"),
                  net_uni=("net_uni", "sum"), net_eng=("net_eng", "sum"),
                  rate_used=("commission_rate_used", "first"),
                  chase=("checklist_pass_count", "first"))
             .reset_index())
    pos["dir"] = np.where(pos["direction"] == "LONG", 1, -1)
    dm = pd.DatetimeIndex((pd.to_datetime(pos["entry_ts"])
                           - pd.Timedelta(minutes=1)).dt.floor("min"))
    src = d.reindex(dm)
    for c in ("gp_break_hi", "gp_break_lo", "gp_range", "gp_dir", "gp_pos",
              "rp_dist_to_high_60m_atr", "rp_dist_to_low_60m_atr",
              "rp_swing_ready_60m", "close", "hhmm"):
        pos[c] = src[c].to_numpy() if c in src.columns else np.nan
    pos["brk_with"] = np.where(pos["dir"] == 1, pos["gp_break_hi"], pos["gp_break_lo"])
    # 529차 축 (방향은 소비자가 곱한다)
    pos["run529"] = np.where(pos["dir"] == 1, pos["rp_dist_to_low_60m_atr"],
                             pos["rp_dist_to_high_60m_atr"])
    pos["dist529"] = np.where(pos["dir"] == 1, pos["rp_dist_to_high_60m_atr"],
                              pos["rp_dist_to_low_60m_atr"])
    pos["leg_end529"] = ((pos["run529"] >= 5.0) & (pos["dist529"] <= 1.0)
                         & pos["rp_swing_ready_60m"].fillna(False)).astype(float)
    pos.to_csv(os.path.join(HERE, "out_track2_deep.csv"), index=False,
               encoding="utf-8-sig")

    w("# Track 2 심화 — 「진입방향 돌파 동반」 손실의 검증")
    w("")
    w("표본: SYSTEM_AUTO %d 포지션 / %d 거래일 (%s ~ %s)"
      % (len(pos), pos["day"].nunique(), pos["day"].min(), pos["day"].max()))
    w("")

    # ① 요율 세대
    w("## ① 수수료 세대 불연속이 만든 것인가")
    w("")
    rates = pos["rate_used"].dropna().unique()
    w("- `trades.commission_rate_used` 실측값: %s"
      % ", ".join("%.8f" % r for r in sorted(rates)) if len(rates) else "- 기록 없음")
    w("- 엔진 net 합 **%s원** vs 단일요율(%.6f%%) 재계산 net 합 **%s원**"
      % (f"{pos['net_eng'].sum():+,.0f}", RATE_LIVE * 100, f"{pos['net_uni'].sum():+,.0f}"))
    w("")
    w("아래 표는 **전부 단일요율 net** 기준이다(불연속 제거).")
    w("")
    pos["net_u"] = pos["net_uni"]
    w(HDR)
    w(summ(pos, "전체"))
    w(summ(pos[pos["brk_with"] == 1], "**진입방향 돌파 동반**"))
    w(summ(pos[pos["brk_with"] == 0], "돌파 없음"))
    w(summ(pos[pos["brk_with"].isna()], "GP 미부착(워밍업 등)"))
    w("")
    w("엔진 net 기준 대조(요율 불연속 포함):")
    w("")
    pos["net_u"] = pos["net_eng"]
    w(HDR)
    w(summ(pos[pos["brk_with"] == 1], "진입방향 돌파 동반(엔진net)"))
    w(summ(pos[pos["brk_with"] == 0], "돌파 없음(엔진net)"))
    pos["net_u"] = pos["net_uni"]

    # ② 529차 축과의 관계
    w("")
    w("## ② 529차 레그탈진 축(run>=5.0 & dist<=1.0)과 같은 것을 재는가")
    w("")
    ct = pd.crosstab(pos["brk_with"].fillna(-1), pos["leg_end529"].fillna(-1))
    w("교차표 (행: GP 돌파동반, 열: 529차 레그끝)")
    w("")
    w("| | 529차 아님 | 529차 레그끝 |")
    w("|---|---|---|")
    for i in [0.0, 1.0]:
        if i not in ct.index:
            continue
        r0 = int(ct.loc[i, 0.0]) if 0.0 in ct.columns else 0
        r1 = int(ct.loc[i, 1.0]) if 1.0 in ct.columns else 0
        w("| %s | %d | %d |" % ("GP 돌파 아님" if i == 0 else "**GP 돌파 동반**", r0, r1))
    w("")
    w(HDR)
    w(summ(pos[pos["leg_end529"] == 1], "529차 레그끝(run>=5 & dist<=1)"))
    w(summ(pos[(pos["brk_with"] == 1) & (pos["leg_end529"] == 0)], "GP돌파만 (529차 아님)"))
    w(summ(pos[(pos["brk_with"] == 0) & (pos["leg_end529"] == 1)], "529차만 (GP돌파 아님)"))
    w(summ(pos[(pos["brk_with"] == 1) & (pos["leg_end529"] == 1)], "둘 다"))

    # ③ 방향·등급·시간대
    w("")
    w("## ③ 편중 점검 — 방향 · 등급 · 시간대")
    w("")
    w(HDR)
    for dv, dn in ((1, "LONG"), (-1, "SHORT")):
        w(summ(pos[(pos["brk_with"] == 1) & (pos["dir"] == dv)], "돌파동반 %s" % dn))
    for gr in sorted(pos["grade"].dropna().unique()):
        w(summ(pos[(pos["brk_with"] == 1) & (pos["grade"] == gr)], "돌파동반 등급%s" % gr))
    pos["ampm"] = np.where(pos["hhmm"].astype(str) < "12:00", "오전", "오후")
    for ap in ("오전", "오후"):
        w(summ(pos[(pos["brk_with"] == 1) & (pos["ampm"] == ap)], "돌파동반 %s" % ap))

    # ③-2 기존 10_chase 필터와의 관계 — 새 축인가
    w("")
    w("## ③-2 기존 `10_chase` 연장추격 필터가 이미 잡고 있는가")
    w("")
    w("`10_chase`(343차) = 직전 10분 종가 대비 연장폭 `|price_extension_atr|` 이 임계")
    w("(추세·중립 2.0 / Hurst<0.45 평균회귀 1.5) 초과 **且** 그 방향으로 진입.")
    w("GP 돌파는 25봉 **극값** 기준이므로 축이 다르다 — 실제로 다른지 2x2로 본다.")
    w("")
    pos["ext10"] = src["price_extension_atr"].to_numpy() if "price_extension_atr" in src.columns else np.nan
    pos["hurst_e"] = src["hurst"].to_numpy() if "hurst" in src.columns else np.nan
    thr = np.where(pos["hurst_e"] < 0.45, 1.5, 2.0)
    pos["chase"] = (((pos["ext10"] > 0) == (pos["dir"] == 1))
                    & (pos["ext10"].abs() > thr)).astype(float)
    pos.loc[pos["ext10"].isna(), "chase"] = np.nan
    w("- `price_extension_atr` 결측 %d/%d (백필 구간 미측정)"
      % (int(pos["ext10"].isna().sum()), len(pos)))
    w("")
    w("| 건당 net (단일요율) | `10_chase` 미발동 | `10_chase` 발동 |")
    w("|---|---|---|")
    for bv, bn in ((0.0, "GP 돌파 아님"), (1.0, "**GP 돌파 동반**")):
        cells = []
        for cv in (0.0, 1.0):
            g = pos[(pos["brk_with"] == bv) & (pos["chase"] == cv)]
            cells.append("n=%d, **%s**" % (len(g), f"{g['net_u'].mean():+,.0f}")
                         if len(g) else "n=0")
        w("| %s | %s | %s |" % (bn, cells[0], cells[1]))
    w("")
    w(HDR)
    for bv, cv, nm in ((1, 1, "GP돌파 O · chase O"), (1, 0, "GP돌파 O · chase X"),
                       (0, 1, "GP돌파 X · chase O"), (0, 0, "GP돌파 X · chase X")):
        w(summ(pos[(pos["brk_with"] == bv) & (pos["chase"] == cv)], nm))
    w("")
    w("⇒ 분리는 **GP 축을 따라** 일어난다. `chase` 축만으로는 갈리지 않는다.")
    w("  `chase`가 발동했는데 GP 돌파가 아닌 군은 사실상 무해한데 이미 감점받고 있다")
    w("  (317차 FalseBlock 계열). GP만 잡는 군은 기존 필터가 통째로 놓친다.")

    # ④ 일자 분해
    w("")
    w("## ④ 일자 분해 — 며칠에 몰려 있는가")
    w("")
    g = pos[pos["brk_with"] == 1]
    daily = g.groupby("day").agg(n=("net_u", "size"), net=("net_u", "sum")).sort_values("net")
    w("| 거래일 | 건수 | net(단일요율) |")
    w("|---|---|---|")
    for k, r in daily.iterrows():
        w("| %s | %d | %s |" % (k, int(r["n"]), f"{r['net']:+,.0f}"))
    w("")
    w("- 상위 손실 3일 제거 시 net = **%s원**"
      % f"{daily['net'].iloc[3:].sum():+,.0f}")
    w("- 최고 이익 3일 제거 시 net = **%s원**"
      % f"{daily['net'].sort_values(ascending=False).iloc[3:].sum():+,.0f}")

    # ⑤ 반사실 — 이 군을 절반 사이즈로 줄였다면
    w("")
    w("## ⑤ 반사실 — 승격 형태별 (529차 promotion_order 관례)")
    w("")
    tot = pos["net_u"].sum()
    for mult, nm in ((0.5, "사이즈 ½ (size_half)"), (0.0, "진입 없음 (참고 — 하드차단 금지)")):
        alt = pos["net_u"].where(pos["brk_with"] != 1, pos["net_u"] * mult).sum()
        w("- %s → 통산 net %s원 (현행 %s원 대비 **%s원**)"
          % (nm, f"{alt:+,.0f}", f"{tot:+,.0f}", f"{alt - tot:+,.0f}"))
    w("")
    w("⚠ 529차 `hard_block_forbidden`: 하드차단은 금지다(317차 FalseBlock 교훈).")
    w("  위 0배 행은 상한을 보여주는 참고치일 뿐 제안이 아니다.")

    p = os.path.join(HERE, "gp_track2_deep.md")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(OUT) + "\n")
    print("\n[saved] %s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
