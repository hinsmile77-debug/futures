"""[MW0601 489차 / A-1 스테이지1] CB② 카운트 정합 — 시간창 + 포지션 단위.

────────────────────────────────────────────────────────────────────────────
무엇이 어긋나 있었나
────────────────────────────────────────────────────────────────────────────
CLAUDE.md 절대원칙 ②는 *"**5분 내** 손절 **3연속** → 당일 정지"* 인데 코드는
둘 다 달랐다:

  ① **시간창이 없었다** — `record_stop_loss()`가 정수를 올리고 승리 레그로만
     리셋했다. 오전 손절과 오후 손절이 "연속"으로 합산됐다.
  ② **레그 단위로 셌다** — 호출부가 청산 레그 단위 4곳
     (`_post_partial_exit` / `_post_loss_tier1_exit` / `_post_exit` /
     `_ts_record_nonfinal_exit`)이라 **한 포지션의 계단식 손절이 2카운트**를
     만들었다(2026-08-19 11:11 SHORT 3계약이 실례).

한도가 9999(모의투자 한시 예외)라 드러나지 않았을 뿐, **2~3으로 복원하는 순간
단일 포지션 하나의 계단식 손절만으로 당일 정지**가 성립한다. 계측 4원칙 ①의
CB② 판이며, 복원(기한 2026-08-29) **전에** 고쳐야 하는 이유가 그것이다.

⚠ 489차(2026-08-23) 세션은 **라이브 상수를 바꾸지 않았다** — 그때
  `CB_CONSEC_STOP_LIMIT`은 9999 그대로였고, 고친 것은 "센다"의 정의뿐이었다.
  한도 복원은 그 다음 단계였다(2단계 조건부 복원, 사용자 승인 2026-08-23).

🔵 **그 다음 단계가 끝났다 — 2026-09-02(519차) 사용자 지시로 9999 → 3 복원.**
  재검토 기한 08-29를 5일 초과한 상태였다. 아래 (H)가 그 결정을 고정한다.
  이 파일의 나머지 불변식(A~G)은 **복원 이후 더 중요해졌다** — 계측이 틀린 채
  한도만 3이면 포지션 하나로 당일 정지가 성립하기 때문이다.

────────────────────────────────────────────────────────────────────────────
고정하는 불변식
────────────────────────────────────────────────────────────────────────────
(A) 같은 포지션 키의 추가 레그는 카운트하지 않는다
(B) 다른 포지션은 각각 1회로 센다
(C) 시간창 밖 사건은 만료된다
(D) 승리는 창을 비운다
(E) 한도 도달 시 HALT — 한도는 settings에서 읽는다(테스트가 값을 만들지 않는다)
(F) 재기동 영속화: 사건 목록이 왕복하고, 복원 직후 창이 적용된다
(G) 라이브 호출부 4곳이 전부 포지션 키를 넘긴다
(H) `CB_CONSEC_STOP_LIMIT`은 3이다 (2026-09-02 복원, 2~3 범위 안)

실행: python tests/test_489_cb2_window_and_position_unit.py   (COM/브로커 불필요)
"""
import ast
import datetime
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _cb():
    from safety.circuit_breaker import CircuitBreaker
    return CircuitBreaker(emergency_exit_callback=lambda *a, **k: None)


def test_position_unit_dedupe():
    """(A)(B) 레그가 아니라 포지션을 센다."""
    cb = _cb()
    cb.record_stop_loss("2026-08-19 11:11:00")
    cb.record_stop_loss("2026-08-19 11:11:00")   # 같은 포지션의 최종청산 레그
    cb.record_stop_loss("2026-08-19 11:11:00")
    check("(A) 같은 포지션 3레그 → 1회 (실측 %d)" % cb.status_dict()["consec_stops"],
          cb.status_dict()["consec_stops"] == 1)
    cb.record_stop_loss("2026-08-19 13:20:00")
    check("(B) 다른 포지션은 별도 1회 → 2회 (실측 %d)"
          % cb.status_dict()["consec_stops"],
          cb.status_dict()["consec_stops"] == 2)


def test_window_expiry():
    """(C) 창 밖 사건은 만료된다 — 시계를 직접 밀어 넣어 검사."""
    from config.settings import CB_CONSEC_STOP_WINDOW_SEC as W
    cb = _cb()
    now = datetime.datetime(2026, 8, 19, 13, 0, 0)
    # 창보다 오래된 사건 2건을 직접 주입(공개 API는 now_kst를 쓰므로)
    cb._stop_events.append((now - datetime.timedelta(seconds=W + 60), "old1"))
    cb._stop_events.append((now - datetime.timedelta(seconds=W + 30), "old2"))
    cb._stop_events.append((now - datetime.timedelta(seconds=10), "fresh"))
    cb._prune_stop_events(now)
    check("(C) 창(%ds) 밖 2건이 만료되고 1건만 남는다 (실측 %d)"
          % (W, cb._consec_stops), cb._consec_stops == 1)
    check("(C) 남은 것이 최신 사건이다",
          [k for _, k in cb._stop_events] == ["fresh"])


def test_win_clears():
    """(D) 승리는 창을 비운다 — '연속'의 의미."""
    cb = _cb()
    cb.record_stop_loss("p1")
    cb.record_stop_loss("p2")
    cb.record_win()
    check("(D) 승리 후 0회", cb.status_dict()["consec_stops"] == 0)
    check("(D) 사건 목록도 비었다", len(cb._stop_events) == 0)


def test_halt_fires_at_limit():
    """(E) 한도 도달 시 HALT — 한도 값은 settings에서 읽는다.

    ⚠ 테스트가 임계를 **고정값으로 덮어쓴다**(3). 2026-09-02 복원으로 운영값도
      3이 됐지만, 여기서 모듈 상수를 명시적으로 세우는 관례는 유지한다 — 운영값이
      다시 바뀌어도 이 테스트가 재는 것(「한도에 닿으면 HALT 되는가」)은 그대로여야
      하기 때문이다. 운영값 자체는 (H)가 따로 고정한다.
    """
    from config.constants import CB_STATE_HALTED
    import safety.circuit_breaker as M
    orig = M.CB_CONSEC_STOP_LIMIT
    try:
        M.CB_CONSEC_STOP_LIMIT = 3
        cb = _cb()
        for i in range(2):
            cb.record_stop_loss("p%d" % i)
        check("(E) 한도 직전에는 정상", cb.state != CB_STATE_HALTED)
        cb.record_stop_loss("p2")
        check("(E) 서로 다른 3포지션이 창 안에 들면 HALT", cb.state == CB_STATE_HALTED)

        cb2 = _cb()
        for _ in range(5):
            cb2.record_stop_loss("same-position")
        check("(E') 같은 포지션 5레그로는 HALT되지 않는다 - 이 수정의 요점",
              cb2.state != CB_STATE_HALTED)
    finally:
        M.CB_CONSEC_STOP_LIMIT = orig


def test_state_roundtrip():
    """(F) 재기동 영속화 — 사건 목록이 왕복하고 복원 직후 창이 걸린다."""
    from config.settings import CB_CONSEC_STOP_WINDOW_SEC as W
    cb = _cb()
    cb.record_stop_loss("p1")
    cb.record_stop_loss("p2")
    d = cb.to_state_dict()
    check("(F) stop_events가 직렬화된다 (%d건)" % len(d.get("stop_events") or []),
          len(d.get("stop_events") or []) == 2)

    cb2 = _cb()
    cb2.from_state_dict(d)
    check("(F) 복원 후 2회", cb2.status_dict()["consec_stops"] == 2)
    check("(F) 복원 후에도 포지션 키가 살아 있다 (중복 제거가 이어진다)",
          [k for _, k in cb2._stop_events] == ["p1", "p2"])
    cb2.record_stop_loss("p1")
    check("(F) 복원된 키의 추가 레그는 여전히 무시된다",
          cb2.status_dict()["consec_stops"] == 2)

    # 창보다 오래된 상태로 복원하면 만료돼야 한다
    old_iso = (datetime.datetime.now()
               - datetime.timedelta(seconds=W + 600)).isoformat()
    cb3 = _cb()
    cb3.from_state_dict({"stop_events": [[old_iso, "stale"]], "consec_stops": 1})
    check("(F) 창 지난 상태는 복원 즉시 만료된다",
          cb3.status_dict()["consec_stops"] == 0)

    # 구버전 상태(목록 없음)도 죽지 않는다
    cb4 = _cb()
    cb4.from_state_dict({"consec_stops": 2})
    check("(F) 구버전 상태(stop_events 없음)에서도 죽지 않는다",
          cb4.status_dict()["consec_stops"] == 2)


def test_call_sites_pass_key():
    """(G) 라이브 호출부 4곳이 전부 포지션 키를 넘기는가 — AST로 확인.

    인자 없이 호출하면 레그 단위로 세는 폴백 경로가 되고, 그 순간 이 수정이
    무력해진다. 문자열 검색이 아니라 호출 노드의 인자 수를 본다.
    """
    tree = ast.parse(io.open(os.path.join(_ROOT, "main.py"),
                             encoding="utf-8").read())
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call)
             and getattr(n.func, "attr", None) == "record_stop_loss"]
    check("(G) 호출부가 4곳이다 (실측 %d)" % len(calls), len(calls) == 4)
    bare = [c for c in calls if not c.args and not c.keywords]
    check("(G) 인자 없이 부르는 곳이 없다 (%d곳)" % len(bare), not bare)


def test_limit_restored():
    """(H) 한도가 복원됐다 — 스테이지2 완료.

    ⚠ **원래 이 테스트는 "여전히 9999"를 고정했다.** 489차(2026-08-23) 시점에는
    한도 복원이 별도 결정이라 라이브 상수를 건드리지 않았기 때문이다. 그 결정은
    **2026-09-02(519차) 사용자 지시로 종결**됐다 — 재검토 기한 08-29를 5일 초과한
    상태였다. 이 절의 취지(*"스테이지1 계측만 바뀌었고 한도는 의도한 값이다"*)는
    그대로 두고, 고정 대상만 현행 결정으로 옮긴다.

    절대원칙 ②의 문구가 "3연속"이고 실전 전환 게이트 판정기
    (`phase5_gate_status._CB2_RESTORED_MAX`)도 3 이하를 「복원됨」으로 본다.
    """
    from config.settings import CB_CONSEC_STOP_LIMIT, CB_CONSEC_STOP_WINDOW_SEC
    check("(H) CB_CONSEC_STOP_LIMIT은 3 (2026-09-02 복원, 절대원칙 ② 문구와 일치)",
          CB_CONSEC_STOP_LIMIT == 3)
    check("(H) 한도가 2~3 범위 안이다 (복원 허용 구간)",
          2 <= CB_CONSEC_STOP_LIMIT <= 3)
    check("(H) 창은 절대원칙 ② 문구와 같은 300초",
          CB_CONSEC_STOP_WINDOW_SEC == 300)


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0601 489차] CB2 카운트 정합 - 시간창 + 포지션 단위")
    print("=" * 72)
    for fn in (
        test_position_unit_dedupe,
        test_window_expiry,
        test_win_clears,
        test_halt_fires_at_limit,
        test_state_roundtrip,
        test_call_sites_pass_key,
        test_limit_still_dormant,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        sys.exit(1)
    print("전부 통과")
