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

# [MW0602 538차 / F-2] 이력 신선도 경고의 머리말. 호출측(main.py)이 이 경고만
# WARNING 으로 승격한다 — 나머지 단계 경고(R̂ 절단은 실측 25~27% 일)는 INFO 로 둔다.
# 매일 뜨는 WARNING 은 333차 후속5 가 대시보드에서 걷어낸 그 노이즈가 된다.
STALE_HISTORY_MARK = "이력 캐시 낡음"


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


def latest_session_before(date_str, db_path=None, hops=5, skip=()):
    # type: (str, Optional[str], int, Sequence[str]) -> Optional[str]
    """`raw_candles` 에 있는 **date_str 직전 세션 날짜**. 없으면 None.

    🔴 전수 스캔이 아니다 — `ts` 가 PRIMARY KEY 라 `ORDER BY ts DESC LIMIT 1` 은
    인덱스 역방향 seek 1행이다(MW0602 실측 0.0ms). `skip` 에 든 날짜(품질 제외)는
    건너뛰며 최대 `hops` 번만 되짚는다 — 무한 되짚기를 만들지 않는다.
    """
    con = _ro_conn(db_path)
    try:
        cur = date_str
        for _ in range(max(1, hops)):
            row = con.execute(
                "SELECT ts FROM raw_candles WHERE ts < ? ORDER BY ts DESC LIMIT 1",
                (cur + " 00:00:00",)).fetchone()
            if not row:
                return None
            d = row[0][:10]
            if d not in skip:
                return d
            cur = d
        return None
    finally:
        con.close()


def history_freshness_warning(summaries, target_date, excluded=None, db_path=None):
    # type: (Sequence[PL.SessionSummary], str, Optional[dict], Optional[str]) -> Optional[str]
    """[MW0602 538차 / F-2] 이력 캐시가 낡았으면 그 사실을 문자열로 돌려준다.

    🔴 **왜 필요한가.** 08:50 산출의 유일한 입력은 EOD 가 굳힌 이력 캐시다. EOD 가
    실패하거나 안 돌면 `prev`(전일 종가·전일 고·저)·ATR·구조 후보가 전부 하루 이상
    낡은 채로 **아무 경고 없이** 산출된다 — 결과는 그럴듯한 수라서 눈으로 안 잡힌다.
    534차 원본은 `prepare_params()` 가 `history_last`/`history_sessions` 를 반환하는데
    **코드베이스 어디서도 읽지 않았다**(2026-09-07 전수 grep). 계측 4원칙 ④ 그대로다.

    판정 방식: `raw_candles` 의 직전 세션 날짜와 캐시의 마지막 세션을 맞대본다.
    품질 제외된 날(`excluded`)은 캐시가 옳으므로 건너뛴다. 프로브가 실패하면
    **경고하지 않는다** — 없는 사실을 지어내지 않는다(계측 4원칙 ②).
    """
    past = [x for x in summaries if x.d < target_date]
    if not past:
        return None
    try:
        latest = latest_session_before(target_date, db_path=db_path,
                                       skip=tuple(excluded or ()))
    except Exception:
        logger.debug("[LEVELS] 이력 신선도 프로브 실패 — 경고 생략", exc_info=True)
        return None
    if not latest or latest <= past[-1].d:
        return None
    return ("%s — 마지막 세션 %s 인데 raw_candles 에 %s 가 있다"
            "(EOD refresh_history_cache() 누락 의심)"
            % (STALE_HISTORY_MARK, past[-1].d, latest))


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
    # [MW0601 542차 이식] 경로 격자 세대가 다르면 **전량 재생성**한다. 증분으로는
    # 과거 세션의 격자 경로를 채울 수 없다 — 캐시가 보관하는 봉은 최근 7세션뿐이고,
    # 수동 산출의 재적합은 60세션 경로를 요구한다. 전량 재생성 실측 0.8초(EOD 전용).
    rebuilt = bool(force_full)
    if cache and cache.get("path_grid") != PL.PATH_GRID_ID:
        logger.info("[LEVELS] 경로 격자 세대 변경(%s → %s) — 이력 캐시 전량 재생성",
                    cache.get("path_grid"), PL.PATH_GRID_ID)
        cache = {}
        rebuilt = True
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
        path_grid=PL.PATH_GRID_ID,      # [542차] 격자 세대 — 다르면 다음 EOD 가 재생성
        last_date=summaries[-1].d if summaries else None,
        summaries=[PL.summary_to_dict(s) for s in summaries],
        bars=dict((d, [PL.bar_to_dict(b) for b in bs]) for d, bs in bars_by_day.items()),
        excluded=dict(list(cache.get("excluded", {}).items()) + list(excluded.items())),
    )
    save_history_cache(payload, path)
    _grid_n = sum(1 for s in summaries if s.paths)
    return dict(sessions=len(summaries), added=added, excluded=excluded,
                last_date=payload["last_date"], rebuilt=rebuilt, grid_sessions=_grid_n)


def history_from_cache(path=None):
    # type: (Optional[str]) -> Tuple[List[PL.SessionSummary], Dict[str, List[PL.Bar]]]
    cache = load_history_cache(path)
    summaries = [PL.summary_from_dict(s) for s in cache.get("summaries", [])]
    bars = dict((d, [PL.bar_from_dict(b) for b in bs])
                for d, bs in (cache.get("bars") or {}).items())
    return summaries, bars


# ---------------------------------------------------------------- 파라미터

def prepare_params(summaries, bars_by_day, target_date, db_path=None, excluded=None,
                   at_key=None):
    # type: (List[PL.SessionSummary], Dict[str, List[PL.Bar]], str, Optional[str], Optional[dict], Optional[str]) -> Optional[dict]
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
    # 🔴 [MW0602 538차 / F-5] 경고는 **변수 먼저, 상수 마지막**이다.
    #   534차 원본은 상수 1건("옵션 OI 원천 없음")이 항상 먼저 나와 로그의 「주의」
    #   줄이 121행 전부 같은 문자열이었다 — 468차 G-2 가 잡으려던 고착 지표 그대로다.
    #   상수를 지우지는 않는다(그 사실도 기록이다). 순서만 바꿔 그날 달라진 것이
    #   앞에 오게 한다.
    warnings = []
    stale = history_freshness_warning(summaries, target_date, excluded=excluded,
                                      db_path=db_path)
    if stale:
        warnings.append(stale)
    if len(hist_bars) < PL.LOOKBACK:
        warnings.append("구조 후보 이력 %d세션(%d 필요)" % (len(hist_bars), PL.LOOKBACK))
    try:
        tgt = datetime.date(*[int(x) for x in target_date.split("-")])
        if PL.is_quarterly_expiry_window(tgt, [d for d, _ in hist_bars]):
            warnings.append("분기 만기 창 — 구조 후보 롤 오염 가능")
    except Exception:
        pass
    if p1 is None:
        warnings.append("M1 미산출 — 훈련 세션 %d(<%d)" % (len(past), PL.MIN_TRAIN_SESSIONS))
    # 옵션 OI 원천은 미륵에 체인 스냅샷이 없어 미사용(가이드 §3-1(d) — 검증에서도
    # 넣으면 극값 안착이 44.3%→41.8% 로 내려갔다). "없다"는 사실을 남긴다.
    # ⚠ **상수다.** 매일 같은 문구이므로 항상 마지막에 둔다(위 F-5).
    # [MW0601 542차 이식] 수동 산출 전용 — 클릭 시각으로 재적합한 P1·R̂.
    # 08:50/09:30 경로는 at_key=None 이라 **무영향**이다.
    p_at = rhat_at = None
    if at_key:
        p_at = PL.fit_stage2_at(past, len(past), at_key)
        rhat_at = PL.fit_rhat(past, len(past), True, at_key)
        if p_at is None:
            # 왜 못 냈는지 남긴다 — 「거리 미산출」만 보면 훈련 부족인지 캐시
            # 세대 문제인지 구분할 수 없다(계측 4원칙 ③).
            _gn = sum(1 for s in past[-PL.TRAIN_SESSIONS:] if (s.paths or {}).get(at_key))
            warnings.append("%s 격자 경로 %d세션(<%d) — EOD 이력 캐시 재생성 필요"
                            % (at_key, _gn, PL.MIN_TRAIN_SESSIONS))
    warnings.append("옵션 OI 원천 없음(설계상 제외)")
    return dict(prev=prev, atr=atr, atr5=atr5, p1=p1, p2=p2, rhat1=rhat1, rhat2=rhat2,
                p_at=p_at, rhat_at=rhat_at, at_key=at_key,
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
    # [MW0602 538차 / F-3·F-5] 그날 달라진 것을 앞에 세운다. `params["warnings"]` 는
    # 이미 「변수 … 상수」 순이므로 단계 경고를 앞에 붙이면 상수는 계속 마지막이다.
    out["warnings"] = stage_warnings(out) + list(params.get("warnings") or [])
    return dict(out=out, note=None, bars=len(bars))


def stage_warnings(out):
    # type: (dict) -> List[str]
    """산출 1건에서 **그날에만 해당하는** 주의사항. 값을 바꾸지 않는다 — 기록만 한다.

    셋을 낸다.
      ① 구조 후보가 한쪽에 0개 — 「없음」은 *측정했는데 없다*이지 미측정이 아니다.
         2026-09-07 08:50 이 그 경우다(시가가 6세션 후보 전부보다 위). 이 사실이
         남아야 장후 채점의 측면 탈락(F-1)과 대조된다.
      ② R̂ 절단 — 절단됐다면 그날 구간폭을 정한 것은 회귀가 아니라 **상수**다.
         MW0602 백필 실측으로 하한 절단은 25~27%, 상한은 5회 발생한다.
      ③ R̂ 외삽 — 산출일 x 가 훈련 지지구간 밖. 2026-09-07 08:50 이 그 경우로,
         `log(ATR/O)` 가 훈련 60세션 최솟값 아래였다(시가만 하룻밤 +3.31% 뛰고
         ATR 은 그대로라 상대변동성이 창 최저가 됐다). 계수가 7열 중 최대(+0.804)라
         가장 크게 외삽되는 열이기도 하다.
    """
    w = []
    st = out.get("structure") or {}
    if not st.get("up"):
        w.append("구조 상방 후보 0개 — 기준가가 후보 전부보다 위(측정됨, 미측정 아님)")
    if not st.get("down"):
        w.append("구조 하방 후보 0개 — 기준가가 후보 전부보다 아래(측정됨, 미측정 아님)")
    rd = out.get("rhat") or {}
    if rd.get("clip") and rd["clip"] != "none":
        w.append("R̂ %s 절단 — 원비 %.3f → %.2f (구간폭을 회귀가 아니라 상수가 정했다)"
                 % ("하한" if rd["clip"] == "floor" else "상한",
                    rd.get("raw") or float("nan"), rd.get("scale") or float("nan")))
    if rd.get("extrap"):
        w.append("R̂ 외삽 — 훈련 지지구간 밖: %s" % ", ".join(rd["extrap"]))
    return w


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


def format_manual_log_lines(row):
    # type: (dict) -> List[str]
    """[MW0601 542차 이식] 수동 산출 로그 2줄 — 화면과 같은 수·같은 사유를 남긴다."""
    if row.get("note"):
        return ["[LEVELS 수동 %s] 미산출 — %s" % (row.get("computed_at"), row["note"])]
    head = ("[LEVELS 수동 %s] 컷=%s 모델=%s ref=%.2f ATR=%.1f | "
            % (row.get("computed_at"), row.get("at") or "—", row.get("model"),
               row.get("ref") or 0.0, row.get("atr") or 0.0))
    dist = row.get("distance")
    d_txt = format_distance(dist) if dist else (row.get("distance_note")
                                                or "거리 미산출")
    return [head + d_txt,
            head.split("|")[0] + "| " + format_structure(row["structure"])]


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
    # [538차 F-2] 품질 제외 목록을 함께 넘긴다 — 제외된 날 때문에 캐시가 낡아
    # 보이는 오탐을 막는다.
    params = prepare_params(summaries, bars_by_day, date_str, db_path=db_path,
                            excluded=load_history_cache(cache_path).get("excluded"))
    computed_at = now.strftime("%H:%M:%S")
    if params is None:
        db_utils.save_premarket_levels(
            date_str, stage, computed_at, None,
            note="이력 캐시 없음 — EOD refresh_history_cache() 미실행", bars=len(bars))
        return db_utils.fetch_premarket_levels(date_str).get(stage)

    res = compute_stage(stage, date_str, bars, params)
    # 🔴 [538차] `res["out"]["warnings"]` 를 먼저 쓴다 — 그쪽에만 단계 경고
    #   (구조 후보 0개 · R̂ 절단 · 외삽)가 들어 있다. `params["warnings"]` 를
    #   그대로 넘기면 truthy 라서 `save_premarket_levels` 의 폴백이 안 걸리고
    #   단계 경고가 **조용히 사라진다** — 2026-09-07 py37_32 스모크에서 실제로
    #   그렇게 사라지는 것을 보고 잡았다. 미산출(out=None)일 때만 params 를 쓴다.
    db_utils.save_premarket_levels(
        date_str, stage, computed_at, res["out"], note=res["note"],
        warnings=(res["out"] or {}).get("warnings") or params.get("warnings"),
        bars=res["bars"])
    return db_utils.fetch_premarket_levels(date_str).get(stage)


def compute_manual(now=None, today_candles=None, db_path=None, cache_path=None,
                   persist=True):
    # type: (Optional[datetime.datetime], Optional[Sequence[dict]], Optional[str], Optional[str], bool) -> dict
    """[MW0601 542차 이식] **수동 산출** — 클릭 시각 기준 거리·구조 맥점.

    08:50/09:30 과 다른 점은 셋뿐이다.

      ① **굳히지 않는다.** 같은 날 여러 번 눌릴 수 있고 그때마다 경로가 다르므로
         매번 새 관측이다. 기록은 별도 테이블에 append-only 로 남긴다
         (`premarket_levels` 를 건드리면 장후 채점·60일 누적 창이 오염된다).
      ② **거리 모델을 클릭 시각으로 재적합한다**(`p_at`). 09:30 모델을 임의 시각에
         적용하는 것은 훈련 시점 밖 외삽이라 하지 않는다.
      ③ 09:00 이전이면 시점 조건부 모델이 없으므로 **M1(시가 기준)만** 낸다.

    그날 경고는 `stage_warnings()` 를 그대로 태운다 — 정시 행과 **같은 어휘**로
    같은 상태를 설명하기 위해서다(구조 후보 0개 · R̂ 절단 · 외삽).

    반환: UI·로그가 그대로 쓰는 dict. 미산출도 **사유를 담아** 돌려준다(예외를 던지지
    않는다) — 관측 전용이라 호출측 파이프라인을 막을 이유가 없다.
    """
    from utils import db_utils

    now = now or datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    hhmm = now.strftime("%H:%M")
    clicked_at = now.strftime("%H:%M:%S")
    at = PL.snap_to_grid(hhmm)                      # None = 09:00 이전
    at_key = PL.grid_key(at) if at else None
    cut = at or hhmm

    def _row(out=None, note=None, bars=0, bars_source=None):
        r = dict(out or {})
        r.update(date=date_str, stage="MANUAL", computed_at=clicked_at, at=at,
                 clicked_hhmm=hhmm, note=note, bars=bars, bars_source=bars_source)
        r.setdefault("model", None)
        r["warnings"] = list((out or {}).get("warnings") or [])
        if persist:
            try:
                db_utils.save_premarket_levels_manual(date_str, clicked_at, r)
            except Exception:
                logger.warning("[LEVELS] 수동 산출 기록 실패 (무해)", exc_info=True)
        return r

    # 봉 원천 — dev 의 굳힌 테이블에는 이 컬럼이 없으므로 **수동 테이블에만** 남긴다.
    # 폴백이 상시화되면 「장중 DB를 읽지 않는다」는 설계 전제가 조용히 무너진다.
    bars = bars_from_candles(today_candles, until=cut)
    buf_n = len(bars)
    bars_source = "buffer"
    if not bars or bars[0].t > "08:50":
        # 정시 산출과 달리 이 경로는 **사용자가 아무 때나 누른다** — DB 가 아직
        # 없거나 잠긴 순간도 포함된다. 예외를 밖으로 내보내면 화면이 「산출 중…」에
        # 멈춘다(계측 4원칙 ④). 실패도 사유가 있는 결과로 돌려준다.
        try:
            bars = load_today_bars(date_str, until=cut, db_path=db_path)
            bars_source = ("db_fallback(버퍼 0봉)" if buf_n == 0
                           else "db_fallback(버퍼 %d봉 첫봉부적합)" % buf_n)
        except Exception as e:
            return _row(note="당일 봉 조회 실패: %s" % e, bars=0,
                        bars_source="db_fallback(실패)")
    if not bars:
        return _row(note="당일 봉 0개 — 미산출", bars=0, bars_source=bars_source)
    if bars[0].t > "08:50":
        return _row(note="첫 봉 %s (08:45 시가 결손) — 미산출" % bars[0].t,
                    bars=len(bars), bars_source=bars_source)

    summaries, bars_by_day = history_from_cache(cache_path)
    params = prepare_params(summaries, bars_by_day, date_str, db_path=db_path,
                            excluded=load_history_cache(cache_path).get("excluded"),
                            at_key=at_key)
    if params is None:
        return _row(note="이력 캐시 없음 — EOD refresh_history_cache() 미실행",
                    bars=len(bars), bars_source=bars_source)
    try:
        out = PL.compute_manual(at, bars, params["prev"], params["atr"],
                                params.get("p1"), params.get("p_at"),
                                params["candidates"], params.get("rhat1"),
                                params.get("rhat_at"), params.get("atr5"))
    except Exception as e:
        return _row(note="산출 실패: %s" % e, bars=len(bars), bars_source=bars_source)
    out["date"] = date_str
    out["bars"] = len(bars)
    out["train_n"] = ((params.get("p_at") or {}).get("n") if at
                      else (params.get("p1") or {}).get("n"))
    out["warnings"] = stage_warnings(out) + list(params.get("warnings") or [])
    if at is None:
        out["warnings"].insert(
            0, "09:00 이전 — 시점 조건부 모델 없음, M1(시가 기준) 사용")
    if out.get("distance") is None:
        # 「거리 미산출」만 두면 훈련 부족인지 캐시 세대 문제인지 화면에서 구분이
        # 안 된다 — 사유를 값 옆에 붙인다(계측 4원칙 ③).
        _why = [w for w in out["warnings"] if "격자" in w or "미산출" in w]
        out["distance_note"] = ("거리 미산출 — %s"
                                % (_why[0] if _why else "훈련 표본 부족"))
    return _row(out=out, bars=len(bars), bars_source=bars_source)


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
    """누적 집계 — {stage: {n, mae, in50, in80, in80raw, nraw, s_hit, s_n, s_skip, days}}.

    ⚠ 80% 안착은 R̂ 스케일 구간, in80raw 는 스케일 전이다 — **두 열의 차이가 §5
    채택의 손익**이며, 60일 넘게 쌓이면 그 실측으로 채택을 재판정한다(가이드 §8).

    🔴 **[MW0602 538차 / F-1] 구조 안착은 측면(상방·하방) 단위로 센다.**
    534차 원본은 `struct_near_high is not None **and** struct_near_low is not None`
    이라 **한쪽 후보가 0개면 반대쪽의 측정된 결과까지 버렸다.** 그 조건은 구조
    후보가 한쪽에만 없는 날 — 즉 시가가 6세션 후보 범위를 벗어난 갭 데이 — 을
    골라서 탈락시키므로 단순한 표본 손실이 아니라 **선택 편향**이다.

    MW0602 실측(2026-09-07, 채점 120행): **12행(10%)이 그렇게 통째로 탈락**했고
    그 안에서 측정된 쪽은 5적중 / 7미적중이었다. 2026-09-07 08:50 산출도 상방
    후보 0개라 같은 경로였다.

    바뀐 것은 **집계 방식뿐이며 `premarket_levels_score` 행은 그대로다** — 과거
    행을 다시 세면 값이 달라진다. 가이드 §8 의 기대치(무작위 ~47%)는 측면 단위
    비율이라 그대로 비교할 수 있다. 이 지표는 아직 어떤 리포트에도 게시된 적이
    없으므로(`cumulative_markdown` 은 `--markdown` 수동 경로 전용, EOD 맥점 체인은
    MW0602 에서 미실행) 끊어질 시계열이 없다.

    미측정은 0 이 아니다(계측 4원칙 ②) — 후보가 없어 못 잰 측면은 `s_skip` 으로
    따로 센다. 분모(`s_n`)에 넣으면 "안 맞았다"로 위장된다.
    """
    from utils import db_utils

    agg = {}
    for r in db_utils.fetch_premarket_levels_scores(days):
        a = agg.setdefault(r["stage"], dict(n=0, abs_err=0.0, in50=0, in80=0,
                                            in80raw=0, nraw=0, s_hit=0, s_n=0,
                                            s_skip=0, days=0, rows=0))
        a["rows"] += 1
        if r["err_high"] is not None and r["err_low"] is not None:
            a["n"] += 2
            a["abs_err"] += abs(r["err_high"]) + abs(r["err_low"])
            a["in50"] += (r["in50_high"] or 0) + (r["in50_low"] or 0)
            a["in80"] += (r["in80_high"] or 0) + (r["in80_low"] or 0)
            if r["in80raw_high"] is not None and r["in80raw_low"] is not None:
                a["nraw"] += 2
                a["in80raw"] += (r["in80raw_high"] or 0) + (r["in80raw_low"] or 0)
        # 「산출이 아예 없던 행(미산출)」과 「산출은 했는데 그 측면 후보가 0개」를
        # 가른다. 전자는 구조 통계와 무관하고(세지 않는다), 후자만 s_skip 이다.
        computed = (r["err_high"] is not None
                    or r["struct_near_high"] is not None
                    or r["struct_near_low"] is not None)
        if computed:
            a["days"] += 1
            for near, hit in (("struct_near_high", "struct_hit_high"),
                              ("struct_near_low", "struct_hit_low")):
                if r[near] is None:
                    a["s_skip"] += 1
                else:
                    a["s_n"] += 1
                    a["s_hit"] += (r[hit] or 0)
    for a in agg.values():
        a["mae"] = a["abs_err"] / a["n"] if a["n"] else None
    return agg
