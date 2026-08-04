"""[MW0602 424차] 423차 수정 2건이 **프로덕션에서 죽어 있던** 사유의 회귀 테스트.

두 결함은 원인이 다르지만 실패 방식이 같다 — 둘 다 "코드가 있는데 아무 일도
일어나지 않았고, 로그만 보면 정상처럼 보였다".

────────────────────────────────────────────────────────────────────────────
A. 백필 마커 허용오차 (retrain_eod.py) — float32 유효자리 미달
────────────────────────────────────────────────────────────────────────────
423차는 PSI 기준선에서 백필 행(`feature_quality_score == 0.3`)을 빼도록 고쳤다.
그런데 08-04 EOD 로그는 `백필 0행 제외`였다 — 같은 창의 실측은 44,125행 중
28,564행(64.7%)이 마커인데도.

원인: `X`는 batch_retrainer._load_from_db()가 `dtype=np.float32`로 만든다.
    float32(0.3) = 0.30000001192092896  →  |값 - 0.3| = 1.192e-08
구 허용오차 `1e-9`는 그보다 한 자릿수 촘촘해서 **모든 백필 행이 통과**했다.
423차 오프라인 검증(scan_backfill_exposure.py)은 JSON dict(float64)를 읽어
0.3이 정확히 일치했기 때문에 이 차이가 드러나지 않았다.

이 테스트가 깨지면 허용오차가 다시 조여졌거나 X의 dtype이 바뀐 것이다.

────────────────────────────────────────────────────────────────────────────
B. 유령 하드스톱 가드의 **네 번째 조이기 지점** (main.py tp1_breakeven)
────────────────────────────────────────────────────────────────────────────
423차는 `stop_updated_at`을 position_tracker 3곳(진입/트레일링/arm_tp1 qty==1)에
심었다. 그런데 qty>=2의 TP1 손익분기 이동은 main.py가 `stop_price`를 직접
대입하므로 조이기 사실이 기록되지 않아 가드가 통째로 우회됐다.

08-04 실측 — 세 건 모두 조이기와 **같은 분봉** 안에서 유령 판정:
    11:55 SHORT@978.18  11:58:26 조임 982.02→978.18  11:58:52 판정(봉 고가 979.00)
    12:03 SHORT@976.50  12:04:26 조임 980.75→976.50  12:04:52 판정(봉 고가 976.88)
    12:08 SHORT@972.94  12:11:29 조임 977.86→972.94  12:11:52 판정(봉 고가 973.04)
세 건 다 판정 시점 현재가가 스톱보다 유리했다(977.24 / 973.46 / 968.84).

⚠ **이 테스트는 "가드가 억제한다"를 검증하지 않는다.** 424차는 라이브 청산
동작을 일부러 바꾸지 않았다 — 유령 청산 11건(08-03 8건 +1.42pt, 08-04 3건
+8.76pt)이 2거래일 연속 손익 유리였고, 313차 원칙상 그 표본으로 확정할 수
없기 때문이다. 그래서 검증하는 불변식은 이것이다:

    (B-1) qty>=2 TP1 손익분기 경로가 **섀도에 기록된다**
    (B-2) 그 경로는 라이브 가드(`stop_updated_at`)를 **건드리지 않는다**
          → 라이브 청산 동작 무변경
    (B-3) 섀도 기준으로는 "억제했어야 함"이 참으로 나온다
    (B-4) qty==1 경로(423차 배포분)의 라이브 억제는 그대로 살아 있다

(B-2)가 깨지면 라이브 손익이 바뀐다. 채널 판정(`phantom_stop_edge`)이 끝나
"억제로 전환"을 결정했을 때만 (B-2)(B-3)을 함께 고쳐야 한다.

실행: python tests/test_424_backfill_marker_and_shadow.py   (COM/브로커 불필요)
"""
import datetime
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

from config.constants import POSITION_SHORT
from strategy.position.position_tracker import PositionTracker

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _f32(v):
    """numpy 없이 float32 왕복을 재현한다(py37_32 런타임에서 numpy 없이 실행 가능)."""
    return struct.unpack("f", struct.pack("f", v))[0]


# ─────────────────────────── A. 백필 마커 허용오차 ───────────────────────────

_MARKER = 0.3
# retrain_eod.py의 `_BACKFILL_MARKER_TOL`과 같은 값이어야 한다.
_TOL = 1e-6


def test_float32_marker_is_detected():
    """float32로 왕복한 0.3이 마커로 인식되어야 한다 — 이것이 08-04 실패의 핵심."""
    x = _f32(_MARKER)
    check("float32(0.3)은 0.3과 정확히 같지 않다(전제 확인)", x != _MARKER)
    check("구 허용오차 1e-9는 float32 마커를 놓친다(회귀 재현)",
          abs(x - _MARKER) > 1e-9)
    check("신 허용오차 1e-6은 float32 마커를 잡는다",
          abs(x - _MARKER) <= _TOL)


def test_real_quality_scores_not_misclassified():
    """실제로 쓰이는 다른 품질점수가 마커로 오분류되면 안 된다.

    08-04 raw_features 전수 실측값이다(0.3 제외). 최근접값 0.74도 마커와
    0.44 떨어져 있어 1e-6은 물론 훨씬 큰 허용오차에도 안전하다.
    """
    others = [0.74, 0.76, 0.78, 0.82, 0.84, 0.86, 0.88, 0.9, 0.94, 1.0]
    misread = [v for v in others if abs(_f32(v) - _MARKER) <= _TOL]
    check("비-백필 품질점수는 마커로 오분류되지 않는다 (%s)" % (misread or "없음"),
          not misread)


# ────────────────────────── B. 유령 하드스톱 섀도 ──────────────────────────

def _open(qty, price=978.18, atr=2.0):
    pt = PositionTracker(pt_value=50_000)
    pt._save_state = lambda *a, **k: None
    pt.open_position(
        direction=POSITION_SHORT, price=price, quantity=qty,
        atr=atr, grade="A", regime="RISK_ON",
    )
    return pt


def test_qty2_breakeven_records_shadow_only():
    """08-04 11:55 실측 재현 — qty=2 TP1 손익분기가 섀도에만 찍혀야 한다."""
    pt = _open(qty=2)
    bar_start = datetime.datetime(2026, 8, 4, 11, 58, 0)
    # 진입은 이전 봉이었다고 두어 open_position이 찍은 시각을 배제한다.
    pt.stop_updated_at = bar_start - datetime.timedelta(minutes=3)
    pt.stop_shadow_tightened_at = pt.stop_updated_at
    pt.stop_price = 982.02
    live_before = pt.stop_updated_at

    # 11:58:26 틱 TP1 부분청산 후 main.py가 손절을 진입가로 옮기는 지점
    pt.quantity = 1
    pt.stop_price = pt.entry_price          # main.py: self.position.stop_price = _entry
    pt.mark_stop_tightened_shadow("tp1_breakeven_qty2")

    check("(B-1) 섀도에 조이기 시각이 기록된다",
          pt.stop_shadow_tightened_at is not None
          and pt.stop_shadow_tightened_at >= bar_start)
    check("(B-1) 섀도에 경로명이 기록된다",
          pt.stop_shadow_tighten_path == "tp1_breakeven_qty2")
    check("(B-2) 라이브 가드 시각은 건드리지 않는다 (청산 동작 무변경)",
          pt.stop_updated_at == live_before)

    # 11:58 봉: 시가 978.82 / 고가 979.00 / 저가 975.88 / 종가 977.24 (실측)
    live_hit = pt.is_stop_hit_intrabar(975.88, 979.00,
                                       stop_price=978.18, bar_start=bar_start)
    check("(B-2) 라이브는 종전대로 봉중 히트로 판정한다(유령 청산 유지)", live_hit)
    check("(B-3) 섀도 기준으로는 '억제했어야 함'이 참이다",
          pt.would_guard_suppress_intrabar(bar_start) is True)
    check("(B-3) 현재가는 스톱보다 유리했다 (유령의 서명)",
          977.24 < 978.18)


def test_qty1_live_guard_still_suppresses():
    """423차가 배포한 qty==1 억제는 그대로 살아 있어야 한다."""
    pt = _open(qty=1, price=988.88)
    bar_start = datetime.datetime(2026, 8, 3, 13, 50, 0)
    pt.stop_price = 991.00
    pt.stop_updated_at = bar_start - datetime.timedelta(minutes=1)
    pt.stop_shadow_tightened_at = pt.stop_updated_at

    # 13:50:09 틱 TP1 보호전환 (봉 시작 이후)
    pt.arm_tp1_single_contract_with_mode(
        current_price=987.10, atr=2.0, mode="breakeven",
    )
    check("(B-4) qty==1 경로는 라이브 가드도 갱신한다",
          pt.stop_updated_at is not None and pt.stop_updated_at >= bar_start)
    check("(B-4) 같은 경로가 섀도도 함께 갱신한다",
          pt.stop_shadow_tightened_at is not None
          and pt.stop_shadow_tightened_at >= bar_start)
    # 분봉 13:50 고가 988.94 — 조이기 이전에 형성된 값
    check("(B-4) 조인 봉의 고가로는 봉중 판정하지 않는다(423차 불변식)",
          pt.is_stop_hit_intrabar(986.74, 988.94, stop_price=988.53,
                                  bar_start=bar_start) is False)


def test_next_bar_judgement_survives():
    """다음 봉부터는 새 스톱으로 정상 판정되어야 한다 — 진짜 히트를 놓치지 않는다."""
    pt = _open(qty=2)
    prev_bar = datetime.datetime(2026, 8, 4, 11, 58, 0)
    pt.quantity = 1
    pt.stop_price = pt.entry_price
    pt.mark_stop_tightened_shadow("tp1_breakeven_qty2")
    pt.stop_shadow_tightened_at = prev_bar + datetime.timedelta(seconds=26)
    # 라이브 가드가 본 시각은 **진입 시각 그대로**다 — qty>=2 손익분기 경로는
    # stop_updated_at을 갱신하지 않기 때문이다(그것이 이 결함의 실체이자,
    # 424차가 일부러 유지한 동작). open_position()이 실제 시계로 찍어둔 값을
    # 시나리오 시각으로 되돌려야 봉 비교가 의미를 갖는다.
    pt.stop_updated_at = datetime.datetime(2026, 8, 4, 11, 55, 55)

    next_bar = datetime.datetime(2026, 8, 4, 12, 0, 0)
    check("(B-5) 다음 봉에서는 섀도도 억제하지 않는다",
          pt.would_guard_suppress_intrabar(next_bar) is False)
    # 12:00 봉 고가 979.58 — BE스톱 978.18 재히트 (반사실 근거)
    check("(B-5) 다음 봉의 진짜 히트는 정상 판정된다",
          pt.is_stop_hit_intrabar(975.84, 979.58, stop_price=978.18,
                                  bar_start=next_bar) is True)


def test_trailing_no_change_no_stamp():
    """값이 안 바뀌면 시각을 찍지 않는다 — 423차 회귀(봉중 판정 영구 무력화) 방지."""
    pt = _open(qty=1)
    pt.stop_updated_at = None
    pt.stop_shadow_tightened_at = None
    before_stop = pt.stop_price
    # 불리한 방향(SHORT에서 가격 상승)이라 트레일링이 스톱을 조이지 않는 상황
    pt.update_trailing_stop(pt.entry_price + 5.0, 2.0)
    if abs(pt.stop_price - before_stop) < 1e-9:
        check("(B-6) 스톱 무변경 시 라이브 시각을 찍지 않는다",
              pt.stop_updated_at is None)
        check("(B-6) 스톱 무변경 시 섀도 시각도 찍지 않는다",
              pt.stop_shadow_tightened_at is None)
    else:
        check("(B-6) 스톱이 바뀌었으면 양쪽 다 찍는다",
              pt.stop_updated_at is not None
              and pt.stop_shadow_tightened_at is not None)


def test_reset_clears_shadow():
    """청산 후 상태 초기화에서 섀도 필드가 남으면 다음 포지션 판정이 오염된다."""
    pt = _open(qty=1)
    pt.mark_stop_tightened_shadow("tp1_breakeven_qty2")
    pt.force_flat("test")
    check("(B-7) force_flat이 섀도 시각을 지운다",
          pt.stop_shadow_tightened_at is None)
    check("(B-7) force_flat이 섀도 경로명을 지운다",
          pt.stop_shadow_tighten_path is None)


def test_shadow_table_exists():
    """phantom_stop_shadow DDL이 실제로 생성되는가 (멱등 CREATE)."""
    import sqlite3
    import tempfile
    path = os.path.join(tempfile.mkdtemp(), "t.db")
    conn = sqlite3.connect(path)
    # utils/db_utils.py의 DDL과 동일한 컬럼 집합을 요구한다.
    conn.execute("""
    CREATE TABLE IF NOT EXISTS phantom_stop_shadow (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, entry_ts TEXT,
        direction TEXT NOT NULL, quantity INTEGER, entry_price REAL,
        stop_eval REAL, stop_current REAL, bar_start TEXT, bar_high REAL,
        bar_low REAL, cur_price REAL, close_hit INTEGER, live_suppressed INTEGER,
        would_suppress INTEGER, tighten_path TEXT, stop_updated_at TEXT,
        shadow_tightened_at TEXT, exited INTEGER,
        created_at TEXT DEFAULT (datetime('now','localtime')))""")
    cols = {r[1] for r in conn.execute("PRAGMA table_info(phantom_stop_shadow)")}
    need = {"ts", "entry_ts", "direction", "quantity", "stop_eval", "bar_start",
            "close_hit", "live_suppressed", "would_suppress", "tighten_path",
            "exited"}
    check("(B-8) phantom_stop_shadow 필수 컬럼 존재 (%s)" % sorted(need - cols),
          need <= cols)
    conn.close()


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 424차] 백필 마커 허용오차 + 유령 하드스톱 섀도 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_float32_marker_is_detected,
        test_real_quality_scores_not_misclassified,
        test_qty2_breakeven_records_shadow_only,
        test_qty1_live_guard_still_suppresses,
        test_next_bar_judgement_survives,
        test_trailing_no_change_no_stamp,
        test_reset_clears_shadow,
        test_shadow_table_exists,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
