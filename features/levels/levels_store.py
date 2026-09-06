# -*- coding: utf-8 -*-
"""당일 맥점 예측의 **데이터 계층** — `raw_candles` 이력 → 캐시 → 파라미터 → 단계 산출 → DB 굳히기.

[MW0601 534차] 근거 문서:
`docs/미륵이고도화3/당일맥점예측_거리모델_구조모델_구현가이드_2026-09-06.md` §6.
순수 계산은 `features/levels/premarket_levels.py`, 저장은 `utils/db_utils.py`.

## 🔴 장중 DB 전수 스캔 금지 (CLAUDE.md / 가이드 §6-4·§11-6)

2026-08-10 13:47 에 468MB `raw_data.db` 전수 스캔이 파이프라인을 7,619ms 로 늘려
CB⑤ 를 발동시켰다. 그래서 이 모듈은 **이력을 장중에 읽지 않는다**:

  · 이력(256세션 요약 + 최근 7세션 봉)은 **EOD 에 캐시**(`data/premarket_levels_history.json`)
    로 굳힌다. `refresh_history_cache()` 는 `last_date` 이후 날짜만 증분 조회한다.
  · 08:50 / 09:30 산출은 그 캐시 + **당일 봉**만 쓴다. 당일 봉은 호출측(main.py)이
    메모리 버퍼로 넘겨주는 것이 기본이고, 없을 때만 `ts >= 오늘` PK 범위 조회
    (~50행)로 폴백한다 — 이것은 전수 스캔이 아니다.

## 굳히기(freeze) — 가이드 §4

한 번 산출한 단계는 다시 계산하지 않는다. `INSERT OR IGNORE` 로 스키마 수준에서
지키고, 저장 후 **DB에서 되읽은 값**을 로그·UI 에 쓴다 — 화면·로그·장후 채점이
같은 수를 보게 하기 위해서다.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import sqlite3
from typing import Dict, List, Optional, Sequence, Tuple

from config.settings import DATA_DIR, RAW_DATA_DB
from features.levels import premarket_levels as PL

logger = logging.getLogger(__name__)

HISTORY_CACHE_PATH = os.path.join(DATA_DIR, "premarket_levels_history.json")

# 이력 시작일 — 이보다 앞은 읽지 않는다(캐시 최초 생성 시 1회만 유효).
HISTORY_SINCE = "2025-08-01"

# ── 품질 제외 규칙 (가이드 §6-2 — 검증 스크립트와 동일하게 적용할 것) ──────
MIN_BARS_PER_SESSION = 300      # 수집 결손 세션
MAX_RANGE_RATIO = 0.20          # 일중 범위 > 시가의 20%
MAX_GAP_RATIO = 0.15            # 전일 종가 대비 갭 > 15% (2026-05-13 +752pt 오류)

STAGE_CUT = {"0850": "08:45", "0930": PL.STAGE2_TIME}
STAGE_DUE = {"0850": datetime.time(8, 50), "0930": datetime.time(9, 30)}
STAGE0930_MIN_BARS = 5          # 09:30 이전 봉이 이보다 적으면 미산출


# ---------------------------------------------------------------- DB 읽기

def _ro_conn(db_path=None):
    """읽기전용 연결 — 쓰기 사고 방지용(지연 대책이 아니다, CLAUDE.md 참조)."""
    path = db_path or RAW_DATA_DB
    try:
        return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True,
                               timeout=5.0)
    except Exception:
        return sqlite3.connect(path, timeout=5.0)


def load_sessions(since=HISTORY_SINCE, until=None, db_path=None, prev_close=None):
    # type: (str, Optional[str], Optional[str], Optional[float]) -> Tuple[List[Tuple[str, List[PL.Bar]]], Dict[str, str]]
    """`raw_candles` 에서 날짜별 1분봉을 읽어 **품질 제외 규칙 적용 후** 돌려준다.

    반환: ([(날짜, [Bar])], {제외날짜: 사유}). 날짜 오름차순.
    ⚠ 전 구간 조회는 장중에 부르지 말 것 — EOD 캐시 갱신 경로 전용.
    """
    sql = "SELECT ts, open, high, low, close, volume FROM raw_candles WHERE ts >= ?"
    params = [since]
    if until:
        sql += " AND ts < ?"
        params.append(until)
    sql += " ORDER BY ts"
    con = _ro_conn(db_path)
    try:
        rows = con.execute(sql, tuple(params)).fetchall()
    finally:
        con.close()
    by_day = {}   # type: Dict[str, List[PL.Bar]]
    order = []    # type: List[str]
    for ts, o, h, l, c, v in rows:
        d = ts[:10]
        if d not in by_day:
            by_day[d] = []
            order.append(d)
        by_day[d].append(PL.Bar(t=ts[11:16], o=float(o), h=float(h), l=float(l),
                                c=float(c), v=int(v or 0)))
    clean = []      # type: List[Tuple[str, List[PL.Bar]]]
    excluded = {}   # type: Dict[str, str]
    pc = prev_close
    for d in sorted(order):
        b = by_day[d]
        hi = max(x.h for x in b)
        lo = min(x.l for x in b)
        op = b[0].o
        reason = None
        if len(b) < MIN_BARS_PER_SESSION:
            reason = "봉 %d개(<%d)" % (len(b), MIN_BARS_PER_SESSION)
        elif op > 0 and (hi - lo) > MAX_RANGE_RATIO * op:
            reason = "일중 범위 %.1f%%(>%.0f%%)" % ((hi - lo) / op * 100, MAX_RANGE_RATIO * 100)
        elif pc is not None and pc > 0 and abs(op - pc) > MAX_GAP_RATIO * pc:
            reason = "갭 %.1f%%(>%.0f%%)" % (abs(op - pc) / pc * 100, MAX_GAP_RATIO * 100)
        if reason is None:
            clean.append((d, b))
        else:
            excluded[d] = reason
        pc = b[-1].c
    return clean, excluded


def load_today_bars(date_str, until=None, db_path=None):
    # type: (str, Optional[str], Optional[str]) -> List[PL.Bar]
    """당일 봉만 PK 범위 조회(~50행). 장중 폴백 경로 — 전수 스캔이 아니다."""
    con = _ro_conn(db_path)
    try:
        rows = con.execute(
            "SELECT ts, open, high, low, close, volume FROM raw_candles "
            "WHERE ts >= ? AND ts < ? ORDER BY ts",
            (date_str + " 00:00:00", date_str + " 23:59:59")).fetchall()
    finally:
        con.close()
    bars = [PL.Bar(t=ts[11:16], o=float(o), h=float(h), l=float(l), c=float(c),
                   v=int(v or 0)) for ts, o, h, l, c, v in rows]
    if until:
        bars = [b for b in bars if b.t <= until]
    return bars


def bars_from_candles(candles, until=None):
    # type: (Sequence[dict], Optional[str]) -> List[PL.Bar]
    """main.py 의 candle dict 리스트(메모리 버퍼)를 Bar 로 변환.

    ⚠ `candle["ts"]` 는 **datetime 객체**다(`collection/cybos/realtime_data.py`).
      문자열로 가정하고 슬라이스하면 TypeError 로 봉이 전부 조용히 사라진다 —
      `db_utils.candle_ts_str()` 과 같은 방식으로 다룬다.
    ⚠ 값을 지어내지 않는다 — OHLC 가 없으면 그 봉은 버린다(계측 4원칙 ②).
    """
    out = []
    for c in candles or []:
        ts = c.get("ts")
        if ts is None:
            ts = c.get("time")
        if hasattr(ts, "strftime"):
            t = ts.strftime("%H:%M")
        else:
            ts = str(ts or "")
            t = ts[11:16] if len(ts) >= 16 else ts[:5]
        if len(t) != 5 or ":" not in t:
            continue
        try:
            bar = PL.Bar(t=t, o=float(c["open"]), h=float(c["high"]),
                         l=float(c["low"]), c=float(c["close"]),
                         v=int(c.get("volume") or 0))
        except (KeyError, TypeError, ValueError):
            continue
        if until and bar.t > until:
            continue
        out.append(bar)
    out.sort(key=lambda b: b.t)
    return out


# ---------------------------------------------------------------- 이력 캐시

def load_history_cache(path=None):
    # type: (Optional[str]) -> dict
    p = path or HISTORY_CACHE_PATH
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.warning("[LEVELS] 이력 캐시를 읽지 못했다 — %s", p, exc_info=True)
        return {}


def save_history_cache(payload, path=None):
    # type: (dict, Optional[str]) -> None
    p = path or HISTORY_CACHE_PATH
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    if os.path.exists(p):
        os.remove(p)
    os.rename(tmp, p)


def refresh_history_cache(db_path=None, path=None, force_full=False):
    # type: (Optional[str], Optional[str], bool) -> dict
    """EOD 전용 — `raw_candles` 를 읽어 이력 캐시를 갱신한다(증분).

    반환: {"sessions": n, "added": [...], "excluded": {...}, "last_date": "..."}.
    🔴 장중에 부르지 말 것(가이드 §11-6).
    """
    cache = {} if force_full else load_history_cache(path)
    summaries = [PL.summary_from_dict(s) for s in cache.get("summaries", [])]
    bars_by_day = dict((d, [PL.bar_from_dict(b) for b in bs])
                       for d, bs in (cache.get("bars") or {}).items())
    last_date = cache.get("last_date")
    since = HISTORY_SINCE if not last_date else last_date
    prev_close = None
    if summaries and last_date:
        # 증분 시작점의 갭 판정 기준 = 마지막으로 채택한 세션의 종가
        prev_close = summaries[-1].c
    sessions, excluded = load_sessions(since=since, db_path=db_path, prev_close=prev_close)
    added = []
    for d, bars in sessions:
        if last_date and d <= last_date:
            continue
        summaries = [x for x in summaries if x.d != d]
        summaries.append(PL.summarize_session(d, bars))
        bars_by_day[d] = bars
        added.append(d)
    summaries.sort(key=lambda x: x.d)
    PL.fill_derived(summaries)
    keep = set(x.d for x in summaries[-(PL.LOOKBACK + 1):])
    bars_by_day = dict((k, v) for k, v in bars_by_day.items() if k in keep)
    payload = dict(
        updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        last_date=summaries[-1].d if summaries else None,
        summaries=[PL.summary_to_dict(s) for s in summaries],
        bars=dict((d, [PL.bar_to_dict(b) for b in bs]) for d, bs in bars_by_day.items()),
        excluded=dict(list(cache.get("excluded", {}).items()) + list(excluded.items())),
    )
    save_history_cache(payload, path)
    return dict(sessions=len(summaries), added=added, excluded=excluded,
                last_date=payload["last_date"])


def history_from_cache(path=None):
    # type: (Optional[str]) -> Tuple[List[PL.SessionSummary], Dict[str, List[PL.Bar]]]
    cache = load_history_cache(path)
    summaries = [PL.summary_from_dict(s) for s in cache.get("summaries", [])]
    bars = dict((d, [PL.bar_from_dict(b) for b in bs])
                for d, bs in (cache.get("bars") or {}).items())
    return summaries, bars


# ---------------------------------------------------------------- 파라미터

def prepare_params(summaries, bars_by_day, target_date):
    # type: (List[PL.SessionSummary], Dict[str, List[PL.Bar]], str) -> Optional[dict]
    """target_date **이전** 세션만으로 거리 모델 파라미터와 구조 후보를 만든다.

    반환 None = ATR 을 낼 이력조차 없음. p1/p2/rhat* 는 개별적으로 None 일 수 있으며
    그 경우 해당 모델을 **내지 않는다**(지어내지 않는다).
    """
    past = [s for s in summaries if s.d < target_date]
    if not past:
        return None
    prev = past[-1]
    atr = PL.atr_of(past, len(past))
    if not atr:
        return None
    p1 = PL.fit_stage1(past[-PL.TRAIN_SESSIONS:])
    p2 = PL.fit_stage2(past, len(past))
    rhat1 = PL.fit_rhat(past, len(past), with_path=False)
    rhat2 = PL.fit_rhat(past, len(past), with_path=True)
    atr5 = PL.atr_of(past, len(past), 5)
    hist_bars = [(s.d, bars_by_day[s.d]) for s in past[-PL.LOOKBACK:] if s.d in bars_by_day]
    cands = PL.structural_candidates(hist_bars)
    warnings = []
    if len(hist_bars) < PL.LOOKBACK:
        warnings.append("구조 후보 이력 %d세션(%d 필요)" % (len(hist_bars), PL.LOOKBACK))
    try:
        tgt = datetime.date(*[int(x) for x in target_date.split("-")])
        if PL.is_quarterly_expiry_window(tgt, [d for d, _ in hist_bars]):
            warnings.append("분기 만기 창 — 구조 후보 롤 오염 가능")
    except Exception:
        pass
    # 옵션 OI 원천은 미륵에 체인 스냅샷이 없어 미사용(가이드 §3-1(d) — 검증에서도
    # 넣으면 극값 안착이 44.3%→41.8% 로 내려갔다). "없다"는 사실을 남긴다.
    warnings.append("옵션 OI 원천 없음(설계상 제외)")
    if p1 is None:
        warnings.append("M1 미산출 — 훈련 세션 %d(<%d)" % (len(past), PL.MIN_TRAIN_SESSIONS))
    return dict(prev=prev, atr=atr, atr5=atr5, p1=p1, p2=p2, rhat1=rhat1, rhat2=rhat2,
                candidates=cands, warnings=warnings, history_sessions=len(past),
                history_last=prev.d)


# ---------------------------------------------------------------- 단계 산출

def compute_stage(stage, target_date, today_bars, params):
    # type: (str, str, List[PL.Bar], dict) -> dict
    """단계 산출 + 미산출 사유. 반환: {"out": dict|None, "note": str|None, "bars": int}."""
    cut = STAGE_CUT[stage]
    bars = [b for b in today_bars if b.t <= cut]
    if not bars:
        return dict(out=None, note="당일 봉 0개 — 미산출", bars=0)
    if bars[0].t > "08:50":
        return dict(out=None, note="첫 봉 %s (08:45 시가 결손) — 미산출" % bars[0].t,
                    bars=len(bars))
    if stage == "0930" and len(bars) < STAGE0930_MIN_BARS:
        return dict(out=None, note="09:30 이전 봉 %d개(<%d) — 미산출"
                    % (len(bars), STAGE0930_MIN_BARS), bars=len(bars))
    try:
        out = PL.compute_stage(stage, bars, params["prev"], params["atr"],
                               params.get("p1"), params.get("p2"), params["candidates"],
                               params.get("rhat1"), params.get("rhat2"), params.get("atr5"))
    except Exception as e:
        return dict(out=None, note="산출 실패: %s" % e, bars=len(bars))
    out["date"] = target_date
    out["bars"] = len(bars)
    out["train_n"] = (params.get("p1") or {}).get("n") if stage == "0850" \
        else (params.get("p2") or {}).get("n")
    out["warnings"] = list(params.get("warnings") or [])
    return dict(out=out, note=None, bars=len(bars))


# ---------------------------------------------------------------- 포맷

def format_distance(dist):
    # type: (Optional[dict]) -> str
    if not dist:
        return "거리 미산출 — 훈련 세션 부족(30 필요)"
    sc = " R̂×%.2f" % dist["scale"] if dist.get("scale") else ""
    return ("거리 고 %.1f (50%% %.0f~%.0f · 80%% %.0f~%.0f)"
            " 저 %.1f (50%% %.0f~%.0f · 80%% %.0f~%.0f)%s"
            % (dist["high"], dist["high50"][0], dist["high50"][1],
               dist["high80"][0], dist["high80"][1],
               dist["low"], dist["low50"][0], dist["low50"][1],
               dist["low80"][0], dist["low80"][1], sc))


def format_structure(struct):
    # type: (dict) -> str
    def side(items):
        return " ".join("%d(%d)" % (k, len(v)) for k, v in items) if items else "없음"
    return ("구조 상방 %s | 하방 %s  ※참고용 — 검증상 무작위와 구분 안 됨"
            % (side(struct["up"]), side(struct["down"])))


def format_log_lines(out):
    # type: (dict) -> List[str]
    """가이드 §6-6 로그 형식 2줄."""
    stage = out["stage"]
    head = "[LEVELS %s:%s] ref=%.2f ATR=%.1f | " % (stage[:2], stage[2:],
                                                    out["ref"], out["atr"])
    return [head + format_distance(out.get("distance")),
            head.split("|")[0] + "| " + format_structure(out["structure"])]


# ---------------------------------------------------------------- 오케스트레이션

def ensure_stage(stage, now=None, today_candles=None, db_path=None, cache_path=None):
    # type: (str, Optional[datetime.datetime], Optional[Sequence[dict]], Optional[str], Optional[str]) -> Optional[dict]
    """때가 됐고 아직 안 굳혔으면 단계를 산출해 DB에 굳히고, **DB에서 되읽어** 돌려준다.

    today_candles: main.py 메모리 버퍼(candle dict 리스트). 없거나 부족하면 당일 봉을
    PK 범위 조회로 폴백한다(전수 스캔 아님).
    반환: 굳힌 행 dict (미산출이면 note 가 채워진 행), 때가 안 됐으면 None.
    """
    from utils import db_utils

    now = now or datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    if now.time() < STAGE_DUE[stage]:
        return None
    existing = db_utils.fetch_premarket_levels(date_str).get(stage)
    if existing:
        return existing   # 굳히기 — 다시 계산하지 않는다

    cut = STAGE_CUT[stage]
    bars = bars_from_candles(today_candles, until=cut)
    if not bars or bars[0].t > "08:50":
        bars = load_today_bars(date_str, until=cut, db_path=db_path)

    summaries, bars_by_day = history_from_cache(cache_path)
    params = prepare_params(summaries, bars_by_day, date_str)
    computed_at = now.strftime("%H:%M:%S")
    if params is None:
        db_utils.save_premarket_levels(
            date_str, stage, computed_at, None,
            note="이력 캐시 없음 — EOD refresh_history_cache() 미실행", bars=len(bars))
        return db_utils.fetch_premarket_levels(date_str).get(stage)

    res = compute_stage(stage, date_str, bars, params)
    db_utils.save_premarket_levels(date_str, stage, computed_at, res["out"],
                                   note=res["note"], warnings=params.get("warnings"),
                                   bars=res["bars"])
    return db_utils.fetch_premarket_levels(date_str).get(stage)


# ---------------------------------------------------------------- 장후 채점

def _inside(v, band):
    return bool(band and band[0] <= v <= band[1])


def score_day(date_str, db_path=None):
    # type: (str, Optional[str]) -> dict
    """그날 실제 고·저로 두 단계를 채점해 DB에 적재한다(가이드 §8).

    실제 고·저는 `raw_candles` 당일 전 봉에서 낸다(현재 08:45~15:08). 반환:
    {"actual_high":..,"actual_low":..,"bars":n,"stages":{stage: row}} 또는 사유 dict.
    """
    from utils import db_utils

    stages = db_utils.fetch_premarket_levels(date_str)
    if not stages:
        return dict(error="산출 행 없음", date=date_str)
    bars = load_today_bars(date_str, db_path=db_path)
    if len(bars) < MIN_BARS_PER_SESSION:
        return dict(error="당일 봉 %d개(<%d) — 채점 보류" % (len(bars), MIN_BARS_PER_SESSION),
                    date=date_str)
    hi = max(b.h for b in bars)
    lo = min(b.l for b in bars)
    scored_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out = dict(actual_high=hi, actual_low=lo, bars=len(bars), date=date_str, stages={})
    for stage, s in sorted(stages.items()):
        dist = s.get("distance")
        row = dict(scored_at=scored_at, actual_high=hi, actual_low=lo, bars=len(bars))
        if dist:
            raw = dist.get("raw") or {}
            row.update(
                err_high=dist["high"] - hi, err_low=dist["low"] - lo,
                in50_high=int(_inside(hi, dist.get("high50"))),
                in50_low=int(_inside(lo, dist.get("low50"))),
                in80_high=int(_inside(hi, dist.get("high80"))),
                in80_low=int(_inside(lo, dist.get("low80"))),
                rhat_scale=dist.get("scale"))
            if raw.get("high80") and raw.get("low80"):
                row["in80raw_high"] = int(_inside(hi, raw["high80"]))
                row["in80raw_low"] = int(_inside(lo, raw["low80"]))
        ups = [k for k, _ in (s["structure"]["up"] or [])]
        dns = [k for k, _ in (s["structure"]["down"] or [])]
        tol = 0.005 * (s.get("ref") or 0.0)
        if ups:
            row["struct_near_high"] = min(abs(k - hi) for k in ups)
            row["struct_hit_high"] = int(row["struct_near_high"] <= tol)
        if dns:
            row["struct_near_low"] = min(abs(k - lo) for k in dns)
            row["struct_hit_low"] = int(row["struct_near_low"] <= tol)
        db_utils.save_premarket_levels_score(date_str, stage, row)
        out["stages"][stage] = row
    return out


def cumulative_scores(days=60):
    # type: (int) -> Dict[str, dict]
    """누적 집계 — {stage: {n, mae, in50, in80, in80raw, nraw, s_hit, s_n}}.

    ⚠ 80% 안착은 R̂ 스케일 구간, in80raw 는 스케일 전이다 — **두 열의 차이가 §5
    채택의 손익**이며, 60일 넘게 쌓이면 그 실측으로 채택을 재판정한다(가이드 §8).
    """
    from utils import db_utils

    agg = {}
    for r in db_utils.fetch_premarket_levels_scores(days):
        a = agg.setdefault(r["stage"], dict(n=0, abs_err=0.0, in50=0, in80=0,
                                            in80raw=0, nraw=0, s_hit=0, s_n=0, days=0))
        a["days"] += 1
        if r["err_high"] is not None and r["err_low"] is not None:
            a["n"] += 2
            a["abs_err"] += abs(r["err_high"]) + abs(r["err_low"])
            a["in50"] += (r["in50_high"] or 0) + (r["in50_low"] or 0)
            a["in80"] += (r["in80_high"] or 0) + (r["in80_low"] or 0)
            if r["in80raw_high"] is not None and r["in80raw_low"] is not None:
                a["nraw"] += 2
                a["in80raw"] += (r["in80raw_high"] or 0) + (r["in80raw_low"] or 0)
        if r["struct_near_high"] is not None and r["struct_near_low"] is not None:
            a["s_n"] += 2
            a["s_hit"] += (r["struct_hit_high"] or 0) + (r["struct_hit_low"] or 0)
    for a in agg.values():
        a["mae"] = a["abs_err"] / a["n"] if a["n"] else None
    return agg
