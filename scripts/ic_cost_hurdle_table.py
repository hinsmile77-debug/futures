# -*- coding: utf-8 -*-
"""[MW0601 455차 / N1] 비용 문턱 IC*(h) 표 — "이 호라이즌에서 IC가 얼마여야 비용을 넘나".

⚠ **advisory 전용 — 판정 효력 없음.** 이 표는 어떤 채널의 합격선도 바꾸지 않는다.
   근사 가정(신호 비례 포지션·정규 신호 분포)이 미륵이의 실제 구조(게이트형 진입 +
   ATR 손절/TP)와 다르므로, 판정은 여전히 L2 거래성 시뮬(사후 실측)이 한다.
   [1] TB 채널 IC 합격선(0.03/0.05)·atb_v2 사전등록값과의 대비는 참고 각주일 뿐이다.

산식 (검토보고 §3-N1):
  IC*(h) = c / (E[z | top q] · σ_h),   E[z | z > z_q] = φ(z_q) / q  (표준정규 절단평균)
  σ_h: ① √h 스케일링(σ₁√h)  ② 실측(비중복 h-간격 Δclose의 일자 std 중앙값) — 둘 다 출력.
       일중 평균회귀로 실측 σ_h < σ₁√h 이면 √h 가정이 얼마나 낙관인지 그대로 보인다.
  σ₁: 일자별 "당일 1분 Δclose(pt) std"의 중앙값 (이상치 견고).
  c : 캠페인 정본 산식(2×price×수수료율 + 2×슬리피지틱×TICK_SIZE) + 394차 구 가정
      0.133pt 병기 — 구현계획 §0-3의 괴리 규명 참조(구 가정은 일반선물 틱 0.05 기준).

읽기 전용: raw_data.db만 읽는다. 출력: stdout + data/ic_hurdle_latest.json.
실행: 수동/월간(Phase C 편입 예정). py37_32 호환 문법, numpy 전용.
"""
from __future__ import print_function

import argparse
import datetime
import io
import json
import math
import os
import sqlite3
import sys
from collections import defaultdict

import numpy as np

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# [448차 패턴] BLAS DLL 경로 보장 — 반드시 numpy 첫 사용 전. conda 미활성 직접 실행 시
# MKL 지연로드가 0xC06D007F로 프로세스를 즉사시킨다 (455차 재확인: np.polyfit).
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

def _utf8_console():
    """cp949 콘솔 인코딩 가드 — CLI 실행 시에만 (import 시 래핑하면 중첩 래퍼로 출력 유실)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config.settings import RAW_DATA_DB  # noqa: E402
from scripts.horizon_signal_tradability import roundtrip_cost_pt, LEGACY_COST_PT  # noqa: E402

GRID = [1, 3, 5, 10, 15, 30]   # h=60 제외 — 15:10 강제청산·30m 퇴역 이력 (검토보고 §4)
TOP_QS = [0.05, 0.10, 0.20]
DEFAULT_OUT = os.path.join(_ROOT, "data", "ic_hurdle_latest.json")


def phi(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def norm_ppf(p):
    """표준정규 분위수 — Acklam 근사(절대오차 ~1e-9, scipy 회피)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def ez_top(q):
    """E[z | z > z_q] = φ(z_q)/q."""
    zq = norm_ppf(1.0 - q)
    return phi(zq) / q


def load_closes(days):
    con = sqlite3.connect(RAW_DATA_DB)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_candles ORDER BY d DESC LIMIT ?",
                (days,))
    dates = sorted(r[0] for r in cur.fetchall())
    cur.execute("SELECT ts, close FROM raw_candles WHERE substr(ts,1,10) >= ? ORDER BY ts",
                (dates[0],))
    rows = [(ts, float(c)) for ts, c in cur.fetchall() if c is not None]
    con.close()
    by_day = defaultdict(list)
    for ts, c in rows:
        by_day[ts[:10]].append(c)
    return by_day, dates


def sigma_stats(by_day, grid):
    """σ₁(일자 std 중앙값)과 h별 실측 σ_h(비중복 간격)."""
    s1_days = []
    sh_days = {h: [] for h in grid}
    for d, closes in sorted(by_day.items()):
        arr = np.asarray(closes, dtype=np.float64)
        if arr.size < 90:
            continue
        d1 = np.diff(arr)
        if d1.size >= 30:
            s1_days.append(float(d1.std(ddof=1)))
        for h in grid:
            # 비중복 h-간격 차분
            idx = np.arange(0, arr.size - h, h)
            dh = arr[idx + h] - arr[idx]
            if dh.size >= 5:
                sh_days[h].append(float(dh.std(ddof=1)))
    sigma1 = float(np.median(s1_days)) if s1_days else float("nan")
    sigma_h_meas = {h: (float(np.median(v)) if v else float("nan")) for h, v in sh_days.items()}
    return sigma1, sigma_h_meas, len(s1_days)


def main():
    ap = argparse.ArgumentParser(description="비용 문턱 IC*(h) 표 (advisory, 읽기 전용)")
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    by_day, dates = load_closes(args.days)
    sigma1, sigma_h_meas, n_days = sigma_stats(by_day, GRID)
    all_closes = [c for v in by_day.values() for c in v]
    avg_price = float(np.mean(all_closes))
    cost = roundtrip_cost_pt(avg_price)

    print("=" * 100)
    print("비용 문턱 IC*(h) 표 — advisory, 판정 효력 없음 (검토보고 §3-N1)")
    print("=" * 100)
    print("관찰: %d거래일 (%s ~ %s) | 평균가 %.2fpt | σ₁(1분 Δclose 일자 std 중앙값) = %.4fpt"
          % (n_days, dates[0], dates[-1], avg_price, sigma1))
    print("왕복비용 c: 정본 산식 %.4fpt | 병기(394차 구 가정, 일반선물 틱 0.05) %.3fpt"
          % (cost, LEGACY_COST_PT))
    print("E[z|top q]: " + " / ".join("q=%d%%: %.3f" % (int(q * 100), ez_top(q))
                                      for q in TOP_QS))
    print()

    header = ("%4s %10s %10s" % ("h", "σ₁√h", "σ_h실측")) + "".join(
        "  |q=%02d%% IC*√h IC*실측" % int(q * 100) for q in TOP_QS)
    print(header + "   (c=정본)")
    rows_json = []
    for h in GRID:
        s_scale = sigma1 * math.sqrt(h)
        s_meas = sigma_h_meas.get(h, float("nan"))
        line = "%4d %10.4f %10.4f" % (h, s_scale, s_meas)
        row = {"h": h, "sigma_sqrt_h": s_scale, "sigma_measured": s_meas, "hurdles": {}}
        for q in TOP_QS:
            ez = ez_top(q)
            ic_scale = cost / (ez * s_scale) if s_scale > 0 else float("nan")
            ic_meas = cost / (ez * s_meas) if s_meas and s_meas > 0 else float("nan")
            line += "  |      %6.3f %7.3f" % (ic_scale, ic_meas)
            row["hurdles"]["q%02d" % int(q * 100)] = {
                "ic_star_sqrt_h": ic_scale, "ic_star_measured": ic_meas,
                "ic_star_legacy_cost": LEGACY_COST_PT / (ez * s_meas)
                if s_meas and s_meas > 0 else float("nan"),
            }
        print(line)
        rows_json.append(row)

    print()
    print("읽는 법:")
    print(" · IC*실측 < IC*√h 이면 일중 평균회귀로 √h 가정이 낙관 — 실측 열을 볼 것.")
    print(" · [1] TB 채널 IC 합격선 0.03(3m 등)/0.05 · atb_v2 동일 — 위 표와 대비하면")
    print("   그 합격선이 어떤 실행 가정(top q·비용)에서 경제성을 갖는지 보인다. 단 이")
    print("   대비는 참고 각주일 뿐 합격선 변경 근거가 아니다(§9 사전등록).")
    print(" · 미륵이는 게이트형 진입 + ATR 청산이라 이 근사는 방향 신호의 하한 감각용이다.")

    payload = {
        "generated": datetime.date.today().isoformat(),
        "days": n_days, "window": [dates[0], dates[-1]],
        "avg_price": avg_price, "sigma1": sigma1,
        "cost_pt": cost, "cost_pt_legacy": LEGACY_COST_PT,
        "ez_top": {("q%02d" % int(q * 100)): ez_top(q) for q in TOP_QS},
        "rows": rows_json,
        "advisory": "판정 효력 없음 — L2 거래성 시뮬이 판정을 담당 (검토보고 §3-N1)",
    }
    out_dir = os.path.dirname(args.out)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    tmp = args.out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))
    os.replace(tmp, args.out)
    print("JSON: %s" % args.out)
    return 0


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
