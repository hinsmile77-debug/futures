# -*- coding: utf-8 -*-
"""[MW0601 471차 후속7 / G-2] ConstOut 호라이즌 건강도 채널 — 주간 캠페인 편입용.

채널 번호 **[54]** — 구 [51]이 462차 저변동성 채널과 충돌해 2026-08-23 MW0602
487차(F-9)가 선착 우선으로 재배정했다. 채널 키 문자열은 불변(이력 식별자).
⚠ 이 브랜치(dev)에는 생산부(`scaler_daily.const_out_by_horizon` 컬럼, 457차 G5)가
없어 리포트가 NOT_AVAILABLE_ON_THIS_BRANCH 로 표기한다(487차 F-8(B), 0821 1-17).

## 왜 이 채널이 필요한가

2026-08-14에 3m이 하루 **4회** 상수출력(ConstOut)으로 앙상블에서 제외됐다 돌아왔다.
그 4회가 재학습 4회 → S0 스파이크(최대 2,570ms) → Degraded 선제차단 4회를 연쇄로
유발했고, **그날 유일한 진입의 호라이즌도 3m이었다.** 즉 특정 호라이즌의 불안정이
시스템 자원을 소모하면서 동시에 그 호라이즌으로 진입하고 있는데,
*"그런 날의 그 호라이즌 진입은 성적이 다른가"* 를 묻는 축이 시스템에 없었다.

## 이미 있는 것과 없는 것 (함정 ① 방지)

🔵 **일별 영속화는 이미 돼 있다** — 457차 G5가 `scaler_daily.const_out_by_horizon`
   (JSON `{hz: {events, minutes}}`)에 매일 EOD로 저장한다. 0814 점검 리포트 G-2는
   이것을 "영속화하자"고 적었으나 이미 반영된 사안이다. 중복 테이블을 만들지 않는다.
❌ 없던 것 — 그 집계를 **진입 성적과 결합**하는 부분. 이 모듈이 그것이다.

## 관측치

진입(포지션 단위)을 두 버킷으로 나눈다.

    heavy : 그날 그 entry_horizon의 ConstOut events >= heavy_events_min
    clean : 같은 날 같은 호라이즌 events < heavy_events_min

🔴 **`const_out_by_horizon`이 NULL인 날은 양쪽 어디에도 넣지 않는다.**
   457차 G5 배포(2026-08-12) 이전 행은 전부 NULL이고, 그것은 "ConstOut 0"이 아니라
   **미측정**이다. 미측정을 clean으로 세면 버킷이 오염된다(계측 4원칙 ②) —
   이 채널이 막으려는 가장 큰 함정이고, 하필 캠페인 구간 대부분이 그 구간이다.

## 차단 처방이 아니다

FLAG_DRAG는 "그 호라이즌을 막자"가 아니다. 316~318차가 HurstGate 하드차단이 진짜
추세 분봉의 72.3%를 오판 차단함을 확인한 뒤로, 이 프로젝트는 관측 채널의 처방을
**차단이 아닌 축**(라우터 선택 억제·재학습 스케줄·피처셋 조사)으로 기술한다.

사전등록: `config/settings.py:VALIDATION_CAMPAIGN["const_out_horizon_watch"]`
인터페이스: `compute(since) -> dict` / `summarize(out) -> dict`
  (generate_validation_campaign_report.py 의 `_safe_channel` 규약)

읽기 전용: scaler_monitor.db · trades.db.
"""
from __future__ import print_function

import json
import os
import sqlite3
import sys

_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import SCALER_MONITOR_DB, VALIDATION_CAMPAIGN  # noqa: E402

_CFG = VALIDATION_CAMPAIGN.get("const_out_horizon_watch", {}) or {}
HEAVY_MIN = int(_CFG.get("heavy_events_min", 3))
MIN_N = int(_CFG.get("min_samples_per_bucket", 20))
MIN_DAYS = int(_CFG.get("min_days", 5))
GAP_KRW = float(_CFG.get("pnl_gap_krw", 200_000))
DATA_START = str(_CFG.get("data_start", "") or "")


def _load_const_out_daily(since_date):
    """{date: {hz: {"events": n, "minutes": m}}} — **NULL 날짜는 담지 않는다.**

    담지 않는 것이 핵심이다. 키가 없으면 그 날의 진입은 양 버킷 어디에도 못 들어가고,
    그것이 "미측정"의 올바른 취급이다(계측 4원칙 ②).
    """
    out = {}
    if not os.path.exists(SCALER_MONITOR_DB):
        return out
    con = sqlite3.connect(SCALER_MONITOR_DB, timeout=10)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(scaler_daily)")}
        if "const_out_by_horizon" not in cols:
            return out
        for date_s, raw in con.execute(
            "SELECT date, const_out_by_horizon FROM scaler_daily "
            " WHERE date >= ? AND const_out_by_horizon IS NOT NULL ORDER BY date",
            (since_date,),
        ):
            try:
                parsed = json.loads(raw) if raw else None
            except Exception:
                continue
            if parsed is None:
                continue
            # `{}`(빈 dict)는 **측정했고 ConstOut이 없었다**는 뜻이다 — NULL과 다르다.
            out[str(date_s)[:10]] = parsed
    finally:
        con.close()
    return out


def _load_positions():
    """캠페인 공통 병합 규칙을 그대로 쓴다(재구현 금지 — 규칙이 갈리면 수치가 갈린다).

    지연 import: 리포트 본체가 `_safe_channel`로 이 모듈을 부르는 구조라
    모듈 최상단에서 가져오면 import 순환이 된다.
    """
    from scripts.generate_validation_campaign_report import _merged_positions
    return _merged_positions(extra_cols="entry_horizon")


def _stats(pnls):
    if not pnls:
        return None
    n = len(pnls)
    tot = float(sum(pnls))
    return {
        "n": n,
        "avg_pnl_krw": round(tot / n, 0),
        "total_pnl_krw": round(tot, 0),
        "win_rate": round(sum(1 for p in pnls if p > 0) / float(n), 4),
    }


def compute(since=None):
    """since: 캠페인 시작일(리포트가 넘긴다). data_start와 늦은 쪽을 바닥으로 쓴다."""
    if not _CFG.get("enabled", True):
        return {"disabled": True}

    floor = max([str(x)[:10] for x in (since, DATA_START) if x] or ["0000-00-00"])
    co = _load_const_out_daily(floor)
    if not co:
        return {"error": "ConstOut 일별 집계 없음 (scaler_daily.const_out_by_horizon)",
                "floor": floor, "measured_days": 0}

    try:
        pos = _load_positions()
    except Exception as e:
        return {"error": "포지션 조회 실패 — %s: %s" % (type(e).__name__, e),
                "floor": floor, "measured_days": len(co)}

    heavy, clean = [], []
    per_hz = {}
    n_excluded_unmeasured = 0
    for p in pos:
        day = str(p.get("entry_ts", ""))[:10]
        hz = (p.get("entry_horizon") or "").strip()
        if not day or not hz:
            continue
        if day < floor or day not in co:
            n_excluded_unmeasured += 1      # 🔴 미측정일 — clean으로 세지 않는다
            continue
        ev = int(((co[day].get(hz) or {}).get("events")) or 0)
        pnl = float(p.get("pnl") or 0.0)
        (heavy if ev >= HEAVY_MIN else clean).append(pnl)
        b = per_hz.setdefault(hz, {"heavy": [], "clean": []})
        b["heavy" if ev >= HEAVY_MIN else "clean"].append(pnl)

    # 진입과 무관한 관측 — 표본이 차기 전에도 매주 볼 수 있는 유일한 값이다.
    hz_events = {}
    for day, m in co.items():
        for hz, v in (m or {}).items():
            t = hz_events.setdefault(hz, {"events": 0, "minutes": 0, "days": 0})
            t["events"] += int((v or {}).get("events") or 0)
            t["minutes"] += int((v or {}).get("minutes") or 0)
            t["days"] += 1

    return {
        "floor": floor,
        "measured_days": len(co),
        "measured_range": [min(co), max(co)] if co else [],
        "n_positions_measured": len(heavy) + len(clean),
        "n_positions_excluded_unmeasured": n_excluded_unmeasured,
        "n_days_measured_with_entries": len({
            str(p.get("entry_ts", ""))[:10] for p in pos
            if str(p.get("entry_ts", ""))[:10] in co}),
        "heavy": _stats(heavy),
        "clean": _stats(clean),
        "by_horizon": {
            hz: {"heavy": _stats(v["heavy"]), "clean": _stats(v["clean"])}
            for hz, v in sorted(per_hz.items())
        },
        "const_out_by_horizon_totals": dict(sorted(
            hz_events.items(), key=lambda kv: -kv[1]["events"])),
    }


def summarize(out):
    """사전등록 합격선으로 판정. **여기서 기준을 바꾸지 말 것** (캠페인 §9)."""
    if not out or out.get("disabled"):
        return {"verdict": "INSUFFICIENT", "reason": "채널 비활성", "no_data": True}
    if out.get("error"):
        return {"verdict": "INSUFFICIENT", "no_data": True,
                "reason": "소스 없음 — %s" % out["error"]}

    h, c = out.get("heavy"), out.get("clean")
    tot = out.get("const_out_by_horizon_totals") or {}
    ctx = ("측정 %d거래일(%s) · ConstOut 호라이즌별 %s · 미측정 제외 %d포지션"
           % (out.get("measured_days", 0),
              "~".join(out.get("measured_range") or []),
              json.dumps(tot, ensure_ascii=False) if tot else "없음",
              out.get("n_positions_excluded_unmeasured", 0)))
    base = {"heavy": h, "clean": c, "by_horizon": out.get("by_horizon"),
            "const_out_by_horizon_totals": tot,
            "measured_days": out.get("measured_days", 0),
            "n_excluded_unmeasured": out.get("n_positions_excluded_unmeasured", 0)}

    n_days = int(out.get("n_days_measured_with_entries") or 0)
    if n_days < MIN_DAYS:
        base.update(verdict="INSUFFICIENT",
                    reason=("측정구간 진입 거래일 %d < %d — 판정 보류. %s"
                            % (n_days, MIN_DAYS, ctx)))
        return base
    if not h or not c or h["n"] < MIN_N or c["n"] < MIN_N:
        base.update(verdict="INSUFFICIENT",
                    reason=("버킷 표본 부족 (heavy=%d, clean=%d, 각 %d 필요) — 판정 보류. %s"
                            % ((h or {}).get("n", 0), (c or {}).get("n", 0), MIN_N, ctx)))
        return base

    gap = c["avg_pnl_krw"] - h["avg_pnl_krw"]
    base["gap_krw"] = round(gap, 0)
    if gap >= GAP_KRW:
        base.update(
            verdict="FLAG_DRAG",
            reason=("ConstOut 잦은 날(events≥%d) 같은 호라이즌 진입이 평균 %s원 낮다 "
                    "(heavy %s원 n=%d / clean %s원 n=%d). **차단 처방이 아니다** — "
                    "라우터 선택 억제·재학습 스케줄·피처셋 조사 축으로 주간회의 안건. %s"
                    % (HEAVY_MIN, format(gap, ",.0f"),
                       format(h["avg_pnl_krw"], ",.0f"), h["n"],
                       format(c["avg_pnl_krw"], ",.0f"), c["n"], ctx)))
    else:
        base.update(
            verdict="PASS",
            reason=("격차 %s원 < 기준 %s원 — ConstOut 빈발일의 동일 호라이즌 진입에 "
                    "체계적 열위 미검출. %s"
                    % (format(gap, ",.0f"), format(GAP_KRW, ",.0f"), ctx)))
    return base


if __name__ == "__main__":
    from utils.analysis_db import guard_intraday
    guard_intraday("const_out_horizon_watch")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    _o = compute(VALIDATION_CAMPAIGN.get("start_date"))
    _s = summarize(_o)
    print("[G-2 const_out_horizon_watch] %s — %s" % (_s.get("verdict"), _s.get("reason")))
    for _hz, _v in sorted((_s.get("by_horizon") or {}).items()):
        print("  %-4s heavy=%s clean=%s" % (_hz, _v.get("heavy"), _v.get("clean")))
