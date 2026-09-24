# utils/bar_gap.py — `raw_candles` 결손 판정 [MW0601 618차]
#
# 왜 필요한가
# -----------
# `raw_candles` 는 재기동 공백만큼 조용히 비는데, 그 사실이 **어디에도 남지
# 않았다.** 2026-09-22 점검 1차 진단이 "15:07 이후 38분 수집 공백"으로 잘못
# 읽었고 5거래일 비교로 뒤집혔다 — 절단선(15:08)이 코드 주석에만 있었기 때문이다.
#
# 실측(session_bars 보유 12거래일, 2026-09-07~09-22): 결손일 **3일 / 12일**,
# 총 12봉. 결손 ts 는 그날 재기동 시각과 **1:1 대응**한다(09-21 은 8회 재기동에
# 7봉 결손). 드문 사고가 아니라 상시 현상이다.
#
# 두 기준을 쓴다 — 시점이 다르면 정본이 다르다
# ---------------------------------------------
#   ① **분 그리드** (`gap_by_grid`) — 기동 직후용.
#      기동 시점에는 `session_bars` 에도 그 봉이 없다. 차트 TR 보충은 당일
#      15:46 / 익일 08:41 에만 돌기 때문이다. 그 시점에 `session_bars` 로
#      대조하면 **언제나 결손 0** 을 돌려주는 죽은 계측이 된다 — FP-CRITICAL
#      (학습분포 미저장 → PSI=0.0 2개월) · TOX 죽은 섀도와 같은 계열이다.
#   ② **session_bars 대조** (`gap_vs_session`) — 15:46 보충 직후용.
#      그때는 `session_bars` 가 정본이고, 결손봉이 거기 **보존돼 있는지**까지
#      말할 수 있다. 보존돼 있으면 데이터 손실이 아니다.
#
# 메우지 않는다 — 533차 원칙
# --------------------------
# `raw_candles` 소비처 다수가 "최근 N행"(`lookback_bars=30`·`limit=60`) 조회라
# 행을 더하면 창이 조용히 밀린다. 게다가 차트 TR 보충본은 OHLCV 만 있어
# (bid1·buy_vol·anchor_*·tick_count 전부 NULL) 24열 중 5열밖에 못 채우고,
# `raw_features` 는 틱이 없어 복원 자체가 불가능하다. **감지만 한다.**

import datetime
import os
import sqlite3

from utils.time_utils import (
    FORCE_EXIT_AT,
    expected_raw_candle_minutes,
    raw_candles_last_ts,
)

# 로그 한 줄에 나열할 ts 상한. 넘으면 "… 외 N개" 로 **잔여 개수를 명시**한다
# (계측 4원칙 ③ — 절단하면서 개수를 숨기면 운영자가 "전부"로 오독한다).
MAX_LIST = 12


def _fmt_list(mins):
    """정렬된 "HH:MM" 목록을 로그용 문자열로 — 절단 시 잔여 개수 명시."""
    mins = sorted(mins)
    if not mins:
        return "(없음)"
    if len(mins) <= MAX_LIST:
        return ", ".join(mins)
    return "%s … 외 %d개" % (", ".join(mins[:MAX_LIST]), len(mins) - MAX_LIST)


# ── 순수 로직 (DB 없이 테스트 가능) ────────────────────────────────────────

def gap_by_grid(present, upto=None):
    """분 그리드 기준 결손 — `present` 는 보유 "HH:MM" 집합.

    반환: {"window_end", "expected", "present", "missing"(정렬 list)}
    `raw_candles_last_ts()` 이후 봉은 애초에 그리드에 없으므로 결손으로 세지 않는다.
    """
    exp = expected_raw_candle_minutes(upto)
    return {
        "window_end": max(exp) if exp else None,
        "expected": len(exp),
        "present": len(exp & set(present)),
        "missing": sorted(exp - set(present)),
    }


def gap_vs_session(present, session_present):
    """`session_bars` 정본 대조 — 절단선 **이하** 구간만 본다.

    반환 키:
      · `missing`   결손 ts (session 에 있고 raw 에 없다)
      · `preserved` 그중 `session_bars` 에 보존된 것 = `missing` 전체
      · `orphan`    raw 에 있는데 session 에 없는 ts (있으면 수집 경로 이상)
      · `over_cut`  절단선을 **넘겨** raw 에 들어온 ts — 있으면 중단선 미작동
      · `permanent` **양쪽 다 없는** ts — 차트 TR 보충도 못 메운 영구 결손

    🔴 `permanent` 를 따로 세는 이유(계측 4원칙 ⑤ — 대사는 모든 축을 걸어라):
    `session_bars` 만 정본으로 삼으면 **그것 자체가 짧은 날**을 못 본다. 실측
    2026-09-08 은 raw 365 / session 365 로 이 대조에서는 「결손 0」인데, 분
    그리드로는 19봉이 빈다(그날 차트 TR 보충이 돌지 않았다 — source 분포에
    `chart_backfill` 0건). 한 축만 맞춰보면 나머지가 사각지대가 된다.
    """
    last = raw_candles_last_ts().strftime("%H:%M")
    raw_in = set(m for m in present if m <= last)
    ses_in = set(m for m in session_present if m <= last)
    grid = expected_raw_candle_minutes()
    return {
        "cut": last,
        "raw_in_window": len(raw_in),
        "session_in_window": len(ses_in),
        "expected": len(grid),
        "missing": sorted(ses_in - raw_in),
        "preserved": sorted(ses_in - raw_in),
        "orphan": sorted(raw_in - ses_in),
        "over_cut": sorted(m for m in present if m > last),
        "permanent": sorted(grid - ses_in - raw_in),
    }


# ── DB 조회 (읽기 전용) ────────────────────────────────────────────────────

def _minutes(db_path, table, day):
    """`table` 의 그날 ts 를 "HH:MM" 집합으로 — 읽기 전용, 실패 시 None.

    ⚠ `None` 과 `set()` 을 구분한다: 전자는 **못 읽었다**(미측정), 후자는
    **읽었는데 0행**이다(계측 4원칙 ②).
    """
    if not os.path.exists(db_path):
        return None
    try:
        con = sqlite3.connect("file:%s?mode=ro" % db_path.replace("\\", "/"),
                              uri=True, timeout=5)
        try:
            rows = con.execute(
                "SELECT substr(ts, 12, 5) FROM %s WHERE ts >= ? AND ts < ?" % table,
                (day + " ", day + "Z"),
            ).fetchall()
        finally:
            con.close()
        return set(r[0] for r in rows if r[0])
    except Exception:
        return None


def raw_candle_minutes(db_path, day):
    return _minutes(db_path, "raw_candles", day)


def session_bar_minutes(db_path, day):
    return _minutes(db_path, "session_bars", day)


# ── 로그 한 줄 만들기 ──────────────────────────────────────────────────────

def startup_line(db_path, now=None):
    """기동 직후 한 줄. 결손 0 이어도 **반드시 찍는다**.

    🔴 "결손 0 이면 침묵"으로 두지 않는 이유: 침묵은 「결손이 없다」와
    「검사가 죽었다」를 구분해주지 않는다. FP-CRITICAL 이 2개월간 들키지 않은
    형태가 정확히 그것이다(계측 4원칙 ④).

    반환: (메시지, 레벨) 또는 거래일·시간대가 아니면 `None`.
    """
    now = now or datetime.datetime.now()
    # 상한은 `now − 1분`. 지금 비행 중인 봉을 결손으로 세면 매 기동마다 거짓양성이다.
    upto = (now - datetime.timedelta(minutes=1)).time()
    if upto < datetime.time(8, 45):
        return None

    present = raw_candle_minutes(db_path, now.date().isoformat())
    if present is None:
        return ("[BarGap] raw_candles 조회 실패 — 결손 **미측정**(0 아님)", "WARNING")

    g = gap_by_grid(present, upto)
    head = "[BarGap] 기동 시점 결손 %d봉 / 검사창 08:45~%s (분그리드 기준)" % (
        len(g["missing"]), g["window_end"])
    if not g["missing"]:
        return (head, "INFO")
    return ("%s — %s | session_bars 보존 여부는 15:46 확정 판정에서" % (
        head, _fmt_list(g["missing"])), "WARNING")


def confirm_line(db_path, day):
    """15:46 차트 TR 보충 직후의 **당일 확정** 한 줄.

    반환: (메시지, 레벨). 조회 실패도 한 줄로 남긴다(미측정 표기).
    """
    raw = raw_candle_minutes(db_path, day)
    ses = session_bar_minutes(db_path, day)
    if raw is None or ses is None:
        return ("[BarGap] 당일 확정 실패 — raw=%s session=%s (미측정)" % (
            "None" if raw is None else len(raw),
            "None" if ses is None else len(ses)), "WARNING")

    r = gap_vs_session(raw, ses)
    parts = ["[BarGap] 당일 확정(%s) — raw_candles %d봉 / session_bars %d봉 "
             "(절단선 %s 이하)" % (day, r["raw_in_window"], r["session_in_window"], r["cut"])]
    level = "INFO"
    if r["missing"]:
        parts.append("결손 %d봉 (%s) — 전부 session_bars 에 보존됨, 백필 안 함(533차)"
                     % (len(r["missing"]), _fmt_list(r["missing"])))
        level = "WARNING"
    else:
        parts.append("결손 0봉")
    if r["permanent"]:
        parts.append("⚠ 영구 결손 %d봉 (%s) — session_bars 에도 없다(차트 TR 보충 미수행/거부). "
                     "기대 %d봉" % (len(r["permanent"]), _fmt_list(r["permanent"]), r["expected"]))
        level = "WARNING"
    if r["orphan"]:
        parts.append("⚠ session_bars 에 없는 raw 봉 %d개 (%s) — 수집 경로 이상"
                     % (len(r["orphan"]), _fmt_list(r["orphan"])))
        level = "ERROR"
    if r["over_cut"]:
        parts.append("⚠ 절단선 초과 %d봉 (%s) — 15:10 파이프라인 중단선 미작동"
                     % (len(r["over_cut"]), _fmt_list(r["over_cut"])))
        level = "ERROR"
    return (" | ".join(parts), level)


# ── 절단선 경계 봉 도착시각 진단 [MW0602 588차 후속] ─────────────────────────
#
# 2026-09-23 이 PC 첫 라이브일에 `confirm_line` 이 「절단선 초과 1봉(15:09)」을
# ERROR 로 찍었다. 같은 날 SYSTEM 로그:
#   15:09:01 [BAR-CLOSE][CYBOS] ts=15:08   ← 정상(다음 분 +1초)
#   15:09:59 [BAR-CLOSE][CYBOS] ts=15:09   ← PC 시각 15:10 **이전**에 마감
# 봉 롤오버는 **브로커 체결시각**으로, `main.py` force-exit 가드는 **PC 시각**으로
# 판정한다. 브로커 시계가 PC 보다 앞서면 ts=15:09 봉의 콜백이 PC 15:09:59.x 에
# 도착해 가드를 통과한다 — `raw_candles_last_ts()` 유도의 전제가 깨지는 경로다.
# n=1 이라 결론이 아니다. 이 함수는 그 한 줄을 **매일** 남겨 판정 근거를 쌓는다.
# 🔴 **로그만 만든다** — 가드·저장·판단 경로는 이 함수를 읽지 않는다.

def cutoff_timing_line(bar_ts, now, broker_offset_s=None):
    """경계 봉(절단선 봉·그 다음 봉) 콜백 도착 한 줄. 경계 봉이 아니면 `None`.

    `bar_ts`  봉 ts (`datetime` — realtime_data 가 그렇게 만든다)
    `now`     콜백 도착 PC 시각
    `broker_offset_s`  브로커 시각 − PC 시각(초). `None` 은 **미측정**이지 0 이 아니다
                       (계측 4원칙 ②) — 그대로 「미측정」으로 찍는다.

    반환: (메시지, 레벨). 기대와 다르면 WARNING.
    """
    if not hasattr(bar_ts, "strftime") or not hasattr(now, "time"):
        return None
    last = raw_candles_last_ts()
    _base = datetime.datetime.combine(datetime.date(2000, 1, 1), last)
    first_cut = (_base + datetime.timedelta(minutes=1)).time()
    hm = bar_ts.strftime("%H:%M")
    if hm == last.strftime("%H:%M"):
        expect_stop = False       # 절단선 봉 — 저장돼야 정상
    elif hm == first_cut.strftime("%H:%M"):
        expect_stop = True        # 첫 초과 봉 — 가드가 멈춰야 정상
    else:
        return None

    fe = datetime.datetime.combine(now.date(), FORCE_EXIT_AT)
    delta_s = (now - fe).total_seconds()
    guard_stop = now.time() >= FORCE_EXIT_AT
    off = ("미측정" if broker_offset_s is None
           else "%+.2fs" % float(broker_offset_s))
    ok = (guard_stop == expect_stop)
    msg = ("[BarGapTiming] ts=%s 콜백 도착 PC %s (15:10 대비 %+.3fs) | "
           "가드=%s (기대 %s) | 브로커−PC 시계=%s%s" % (
               hm, now.strftime("%H:%M:%S.%f")[:-3], delta_s,
               "중단" if guard_stop else "통과",
               "중단" if expect_stop else "통과",
               off,
               "" if ok else " | ⚠ 경계 역전 — 이 봉이 raw_candles 절단선을 넘는다"))
    return (msg, "INFO" if ok else "WARNING")
