# -*- coding: utf-8 -*-
"""당일 맥점 예측 — **EOD 단계**: 이력 캐시 갱신 + 당일 채점 + 누적 표 (가이드 §8·§9 Phase 3).

[MW0601 534차] 두 가지를 한다.

  ① `refresh_history_cache()` — `raw_candles` 의 오늘치를 이력 캐시에 증분 반영한다.
     **내일 08:50 산출이 이 캐시만 읽는다.** 장중에 468MB DB를 스캔하지 않기 위한
     구조이므로(2026-08-10 CB⑤ 자가유발), 이 단계가 매일 도는 것이 전제다.
  ② `score_day()` — 그날 실제 고·저로 08:50 / 09:30 두 단계를 채점해 적재하고
     누적 표를 찍는다.

⚠ 장중에는 돌지 않는다(`guard_intraday`). 정규 EOD(15:50)는 마감 후라 걸리지 않는다.

실행:
    python scripts/premarket_levels_eod.py               # 오늘
    python scripts/premarket_levels_eod.py --date 2026-09-04
    python scripts/premarket_levels_eod.py --no-refresh  # 채점만
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import db_utils
from features.levels import levels_store as LS


def run_eod(date_str=None, refresh=True, log=None):
    """EOD 단계 본체 — retrain_eod.py 가 in-process 로 부른다.

    반환: {"refreshed":…, "scored":…, "cumulative":…}. 예외를 밖으로 던지지 않는다 —
    맥점은 관측 전용이라 EOD 체인을 죽일 이유가 없다.
    """
    def say(fmt, *args):
        if log is not None:
            log.info(fmt, *args)
        else:
            print(fmt % args if args else fmt)

    out = {}
    date_str = date_str or datetime.date.today().isoformat()
    db_utils.init_premarket_levels_db()
    if refresh:
        try:
            r = LS.refresh_history_cache()
            out["refreshed"] = r
            say("[LEVELS] 이력 캐시 갱신 — %d세션(~%s), 신규 %d일",
                r["sessions"], r["last_date"], len(r["added"]))
            if r["excluded"]:
                say("[LEVELS] 품질 제외 %d일: %s", len(r["excluded"]),
                    ", ".join("%s(%s)" % kv for kv in sorted(r["excluded"].items())))
        except Exception as e:
            say("[LEVELS] 이력 캐시 갱신 실패 (무해): %s", e)
    try:
        sc = LS.score_day(date_str)
        out["scored"] = sc
        if sc.get("error"):
            say("[LEVELS] %s 채점 없음 — %s", date_str, sc["error"])
        else:
            say("[LEVELS] %s 채점 — 실제 고 %.2f 저 %.2f (봉 %d)",
                date_str, sc["actual_high"], sc["actual_low"], sc["bars"])
            stages_meta = db_utils.fetch_premarket_levels(date_str)
            for stage, row in sorted(sc["stages"].items()):
                if row.get("err_high") is None:
                    say("[LEVELS]   %s:%s 거리 미산출", stage[:2], stage[2:])
                    continue
                say("[LEVELS]   %s:%s 고오차 %+.1f 저오차 %+.1f · 50%% %s · 80%% %s"
                    " · 80%%원 %s · R̂ %s · 구조최근접 %s",
                    stage[:2], stage[2:], row["err_high"], row["err_low"],
                    _mark(row.get("in50_high"), row.get("in50_low")),
                    _mark(row.get("in80_high"), row.get("in80_low")),
                    _mark(row.get("in80raw_high"), row.get("in80raw_low")),
                    ("%.2f" % row["rhat_scale"]) if row.get("rhat_scale") else "—",
                    _near(row))
            # [538차 F-3] 그날 구간폭을 회귀가 정했는지 상수가 정했는지 남긴다.
            _rd = (stages_meta.get(stage) or {}).get("rhat") or {}
            if _rd.get("clip", "none") != "none" or _rd.get("extrap"):
                say("[LEVELS]   %s:%s R̂ 진단 — 원비 %.3f · 절단 %s · 외삽 %s",
                    stage[:2], stage[2:], _rd.get("raw") or float("nan"),
                    _rd.get("clip") or "—",
                    ", ".join(_rd.get("extrap") or []) or "없음")
    except Exception as e:
        say("[LEVELS] 채점 실패 (무해): %s", e)
    try:
        out["cumulative"] = LS.cumulative_scores()
    except Exception:
        out["cumulative"] = {}
    return out


def _mark(a, b):
    def m(x):
        return "—" if x is None else ("○" if x else "×")
    return "%s/%s" % (m(a), m(b))


def _near(row):
    nh, nl = row.get("struct_near_high"), row.get("struct_near_low")
    if nh is None or nl is None:
        return "—"
    return "%.1f/%.1f" % (nh, nl)


def cumulative_markdown(days=60):
    """장후 점검 리포트에 붙일 절 (가이드 §8)."""
    agg = LS.cumulative_scores(days)
    lines = ["## 당일 맥점 예측 채점 — 08:50 / 09:30 × 거리모델 / 구조모델", ""]
    if not agg:
        lines.append("> 채점 없음 — `premarket_levels_score` 가 비어 있다.")
        return "\n".join(lines) + "\n"
    lines.append("| 단계 | n(일) | 거리 MAE pt | 50% | 80%(R̂) | 80% 원구간 "
                 "| 구조 ±0.5% | 구조 n(측면) | 후보0 측면 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for stage in sorted(agg):
        a = agg[stage]
        mae = "%.1f" % a["mae"] if a["mae"] is not None else "—"
        c50 = "%.0f%%" % (a["in50"] / a["n"] * 100) if a["n"] else "—"
        c80 = "%.0f%%" % (a["in80"] / a["n"] * 100) if a["n"] else "—"
        craw = "%.0f%%" % (a["in80raw"] / a["nraw"] * 100) if a["nraw"] else "—"
        sh = "%.0f%%" % (a["s_hit"] / a["s_n"] * 100) if a["s_n"] else "—"
        lines.append("| %s:%s | %d | %s | %s | %s | %s | %s | %d | %d |"
                     % (stage[:2], stage[2:], a["n"] // 2, mae, c50, c80, craw, sh,
                        a.get("s_n", 0), a.get("s_skip", 0)))
    lines.append("")
    lines.append("> **구조 ±0.5% 의 분모는 「측면」이다** — 상방·하방을 따로 센다"
                 "([MW0602 538차 F-1]). 534차까지는 한쪽 후보가 0개면 반대쪽의 "
                 "측정된 결과까지 버렸고, 그 조건이 갭 데이를 골라 탈락시켜 "
                 "**선택 편향**이 됐다(당시 실측 120행 중 12행 탈락). "
                 "「후보0 측면」은 후보가 없어 못 잰 측면 수이며 **분모에 넣지 않는다** "
                 "— 미측정은 0 이 아니다(계측 4원칙 ②).")
    lines.append("> 80% 안착은 R̂ 스케일 구간, 「원구간」은 스케일 전 — **두 열의 차이가 "
                 "R̂ 채택(가이드 §5)의 손익**이며, 60일 넘게 쌓이면 그 실측으로 채택을 "
                 "재판정한다. 기대치(144세션 검증): 08:50 83% vs 78%, 09:30 81% vs 74%.")
    lines.append("> 구조 ±0.5% 의 기대치는 **무작위와 같은 ~47%** — 그보다 유의하게 높지 "
                 "않은 것이 정상이며 결함이 아니다(가이드 §8).")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="맥점 EOD — 이력 캐시 갱신 + 당일 채점")
    ap.add_argument("--date", default=None)
    ap.add_argument("--no-refresh", action="store_true")
    ap.add_argument("--markdown", action="store_true", help="누적 표를 마크다운으로 출력")
    a = ap.parse_args(argv)
    from utils.analysis_db import guard_intraday
    guard_intraday("premarket_levels_eod")
    run_eod(a.date, refresh=not a.no_refresh)
    if a.markdown:
        print("")
        print(cumulative_markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
