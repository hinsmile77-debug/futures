"""[MW0602 439차 P2] [17] 청산 체결 슬리피지 — 오염 제거 + 관찰→판정 승격 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
무엇이 고장나 있었나 — 채널이 자기 경보를 스스로 억제했다
────────────────────────────────────────────────────────────────────────────
[17]의 note 조건은 `풀링 평균 > 캠페인 가정(0.02pt)`이었다. 그런데 풀링 평균이
**봉중(stop_intrabar) 경로에 오염**돼 음수로 끌려가 조건이 성립할 수 없었다.
실측(2026-07-10~08-07):

    풀링            n=109  평균 **-0.1816**  → 가정 초과? 아니오  ← 경보 억제
    봉중(제외대상)   n= 13  평균 **-1.8854**  ← 이게 끌어내린 범인
    유효-hint       n= 96  평균 **+0.0492**  → 가정 초과? 예 (2.5배)

봉중은 `price_hint`가 봉 고저가에서 유도한 **허구의 스톱가**라 주문(시장가)과
무관하다 — 슬리피지 추정에서 빼는 것이 옳다(439차 P3 [48-T]에서 확정).

⚠ 그런데 오염을 걷어내도 **일자단위로는 미유의**다(평균 +0.0133, 초과일 6/10,
부호검정 p=0.7539). 이벤트단위(+0.0492)만 보고 `slippage_ticks_per_side`를
바꾸면 372차가 이상치로 PSI 임계를 바꿀 뻔한 것과 같은 함정에 빠진다.
→ 그래서 판정 단위는 **일자**이고, 현재 verdict는 PASS다.

────────────────────────────────────────────────────────────────────────────
439차 P2가 검증하는 불변식
────────────────────────────────────────────────────────────────────────────
    (1) 봉중 경로가 판정 표본에서 제외된다 (풀링과 유효-hint가 분리된다)
    (2) 경로 분류는 [48]과 **단일 소스**다 (`bar_stop_path_watch._path_of`)
    (3) note가 유효-hint 기준으로 발동한다 (풀링 오염에 억제되지 않는다)
    (4) 판정 단위는 **일자**다 — 이벤트가 가정을 초과해도 일자 부호검정이
        미유의면 PASS
    (5) 일자단위가 유의하게 초과하면 FAIL
    (6) `avg_slippage_pts`(풀링)의 **의미는 바뀌지 않는다** — metrics json
        소비처·과거 주차 대조가 이 키를 읽는다
    (7) 표본 미달이면 INSUFFICIENT (판정하지 않는다)

(6)이 깨지면 과거 주차 리포트와의 대조가 조용히 어긋난다.
(4)가 깨지면 소수 이상치로 왕복비용 상수를 바꾸게 된다.
"""

import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

import scripts.generate_validation_campaign_report as R  # noqa: E402

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _run_with(rows):
    """임시 trades.db에 rows를 넣고 eval을 돌린다 — 실거래 DB 격리.

    rows: (ts, reason, hint_source, slippage_pts)
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    c = sqlite3.connect(path)
    c.execute("""CREATE TABLE exit_fill_slippage (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, entry_ts TEXT,
        direction TEXT, reason TEXT, price_hint REAL, fill_price REAL,
        slippage_pts REAL, created_at TEXT, hint_source TEXT)""")
    c.executemany("INSERT INTO exit_fill_slippage (ts, reason, hint_source, "
                  "slippage_pts) VALUES (?,?,?,?)", rows)
    c.commit(); c.close()
    orig = R.TRADES_DB
    try:
        R.TRADES_DB = path
        return R.eval_exit_fill_slippage_watch(3650)
    finally:
        R.TRADES_DB = orig
        os.unlink(path)


def _mk(days, per_day, slip, reason="하드스톱(틱)", hs="stop_tick", start=3):
    out = []
    for i in range(days):
        d = "2026-08-%02d" % (start + i)
        for j in range(per_day):
            out.append(("%s 10:%02d:00" % (d, j), reason, hs, slip))
    return out


def test_bar_path_excluded():
    """(1)(2) 봉중은 판정 표본에서 빠지고, 풀링과 분리 보고된다."""
    rows = _mk(10, 9, 0.05) + [
        ("2026-08-%02d 11:00:00" % (3 + i), "하드스톱", "stop_intrabar", -2.0)
        for i in range(10)]
    r = _run_with(rows)
    check("(1) 전체 n=100", r["n"] == 100)
    check("(1) 봉중 10건 제외", r["n_bar_excluded"] == 10)
    check("(1) 유효 90건", r["n_valid"] == 90)
    check("(1) 봉중 평균 -2.0", abs(r["avg_bar_pts"] + 2.0) < 1e-6)
    check("(1) 유효 평균 +0.05", abs(r["avg_valid_pts"] - 0.05) < 1e-6)
    check("(1) 풀링은 오염된 채 그대로", r["avg_slippage_pts"] < 0)


def test_single_source_classification():
    """(2) 분류가 [48]의 `_path_of`와 동일 결과여야 한다."""
    from scripts.bar_stop_path_watch import _path_of, BAR
    check("(2) stop_intrabar → BAR", _path_of("stop_intrabar", "하드스톱")[0] == BAR)
    check("(2) stop_tick → BAR 아님", _path_of("stop_tick", "하드스톱(틱)")[0] != BAR)
    # 태깅 이전 행(hint_source NULL)도 reason으로 BAR 재분류되어 제외돼야 한다
    rows = _mk(10, 9, 0.05) + [
        ("2026-08-%02d 11:00:00" % (3 + i), "하드스톱", None, -2.0) for i in range(10)]
    r = _run_with(rows)
    check("(2) 미태깅 '하드스톱'도 봉중으로 제외", r["n_bar_excluded"] == 10)


def test_note_fires_on_valid_not_pooled():
    """(3) 🔴 핵심 — 풀링이 음수여도 유효-hint가 가정을 넘으면 note가 뜬다."""
    rows = _mk(10, 9, 0.05) + [
        ("2026-08-%02d 11:00:00" % (3 + i), "하드스톱", "stop_intrabar", -2.0)
        for i in range(10)]
    r = _run_with(rows)
    check("(3) 풀링 평균은 음수(구 조건이면 억제됨)", r["avg_slippage_pts"] < 0.02)
    check("(3) 그래도 note 발동", bool(r.get("note")))
    check("(3) note에 오염 사실 명시", "오염" in (r.get("note") or ""))


def test_day_level_is_the_unit():
    """(4) 이벤트는 가정 초과인데 일자 부호검정이 미유의면 PASS.

    9일은 가정 미만(0.01), 1일만 크게 초과(1.0) → 이벤트 평균은 초과하지만
    초과일은 1/10이라 부호검정 미유의 → PASS 여야 한다.
    """
    rows = _mk(9, 10, 0.01) + _mk(1, 10, 1.0, start=12)
    r = _run_with(rows)
    check("(4) 이벤트 평균 > 가정", r["avg_valid_pts"] > r["assumed_slippage_pts_per_side"])
    check("(4) 초과일 1/10", r["days_over_assumed"] == 1)
    check("(4) 판정 PASS (일자 미유의)", r["verdict"] == "PASS")
    check("(4) 이벤트/일자 부호 갈림 플래그", r.get("event_day_split") is True)


def test_fail_when_consistent():
    """(5) 전 거래일이 일관되게 가정을 크게 넘으면 FAIL."""
    r = _run_with(_mk(10, 10, 0.50))
    check("(5) 초과일 10/10", r["days_over_assumed"] == 10)
    check("(5) 판정 FAIL", r["verdict"] == "FAIL")
    check("(5) 사유에 '자동 변경 금지' 경고", "자동 변경 금지" in r.get("reason", ""))


def test_pass_when_below_assumption():
    """(5') 가정보다 낮으면 PASS이고 note도 뜨지 않는다."""
    r = _run_with(_mk(10, 10, -0.10))
    check("(5') 판정 PASS", r["verdict"] == "PASS")
    check("(5') note 없음", not r.get("note"))
    check("(5') PASS 사유에 '구분되지 않는다'", "구분되지 않는다" in r.get("reason", ""))


def test_pooled_key_meaning_unchanged():
    """(6) `avg_slippage_pts`는 **전체 행 평균** 그대로여야 한다(호환)."""
    rows = [("2026-08-03 10:00:00", "하드스톱(틱)", "stop_tick", 1.0),
            ("2026-08-03 10:01:00", "하드스톱", "stop_intrabar", -3.0)]
    r = _run_with(rows)
    check("(6) 풀링 = (1.0 + -3.0)/2 = -1.0", abs(r["avg_slippage_pts"] + 1.0) < 1e-6)


def test_insufficient():
    """(7) 표본 미달이면 판정하지 않는다."""
    r = _run_with(_mk(3, 5, 0.05))
    check("(7) INSUFFICIENT", r["verdict"] == "INSUFFICIENT")
    check("(7) 사유에 '판정 보류'", "판정 보류" in r.get("reason", ""))


def test_live_channel():
    """실 DB 스모크 — 키가 채워지고 verdict가 사전등록 어휘인지."""
    r = R.eval_exit_fill_slippage_watch(28)
    if r.get("error"):
        check("실 DB 오류 — 스킵: %s" % r["error"], True)
        return
    for k in ("n_valid", "n_bar_excluded", "avg_valid_pts", "avg_valid_day_pts",
              "days_over_assumed", "sign_p", "event_day_split"):
        check("실 DB: %s 존재" % k, k in r)
    check("실 DB: verdict 어휘", r.get("verdict") in ("PASS", "FAIL", "INSUFFICIENT"))


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 439차 P2] [17] 슬리피지 오염 제거 + 판정 승격 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_bar_path_excluded,
        test_single_source_classification,
        test_note_fires_on_valid_not_pooled,
        test_day_level_is_the_unit,
        test_fail_when_consistent,
        test_pass_when_below_assumption,
        test_pooled_key_meaning_unchanged,
        test_insufficient,
        test_live_channel,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
