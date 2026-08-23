"""[MW0602 425차] qty=1 손절 계단화 — 배선·판정 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
이 처방이 왜 유일하게 남았는가 (0804 4-3 딥다이브)
────────────────────────────────────────────────────────────────────────────
급행 풀스톱(손실 & 보유 ≤150초) 16건이 캠페인 총이익의 74%를 지운다
(-2,878,222원 vs 그 외 84건 +3,878,740원). 집행 축 후보를 전부 실측했다:

  · 진입 후 N초 손절 유예 / 스톱 확대 → **반증**. 16건 중 **14건이 청산 후 10분
    내 더 나빠졌다**(07-16 14:10은 -9.38 → -25.38pt). 스톱은 옳았다.
  · 손절 체결 슬리피지 개선     → 대상 아님. FAST 평균 -0.0157pt(미세 유리).
  · 지정가 진입                 → 미지지. 최선 변형도 일자단위 p=0.45,
                                  델타의 59%가 단일일, 4변형 중 최댓값 선택.
  · 진입 시점 판별자            → 421차 Phase A가 245피처 BH FDR 통과 0개.

"스톱이 옳았다"면 남는 레버는 **더 일찍 끊는 것**이고, 급행 16건 중 **13건
(-2,319,612원, 81%)이 qty=1**인데 qty=1은 `is_loss_tier1_hit()`가 "물리적 분할
불가"로 원천 제외해 전액이 풀스톱까지 노출된다.

────────────────────────────────────────────────────────────────────────────
지키려는 불변식
────────────────────────────────────────────────────────────────────────────
(A) **틱 배선이 `elif`가 아니라 독립 `if`여야 한다.**
    기존 체인은 "풀스톱이 잡히면 tier1은 평가 안 함"인 상호배타다. qty=1 경로를
    거기 끼우면 **같은 틱이 tier1과 풀스톱을 함께 뚫은 사건이 통째로 사라진다** —
    이 채널이 급행풀스톱 qty=1 10건 중 4건(-7.82pt)을 못 잡던 원인이 정확히
    그것(분당 파이프라인 전용 = 1분 스트로보 샘플링)이다.
    ⚠ 이 테스트가 깨졌다면 누군가 `if`를 `elif`로 바꾼 것이다. 되돌릴 것.

(B) **기본값이 꺼져 있어야 한다.** `LOSS_TIER1_QTY1_ENABLED`는 [11] 채널 판정
    전까지 False다. 켜는 것은 주간회의 수동 결정(§9 사전등록 원칙).

(C) **거래일 게이트가 살아 있어야 한다.** 일자단위 양측 부호검정의 최소 p는
    n=5에서 0.0625로 α=0.05를 **원리적으로** 통과할 수 없다. `min_days=6`이
    그래서 필요하다 — 425차 시점에 이미 5거래일 전부 양수(p=0.0625)로 그 바닥에
    닿아 있었고, 건수만 보는 게이트였다면 하루가 표본의 40%를 공급해도 통과했다.

(D) **판정 모집단이 오염되지 않아야 한다.** 실적용 이후 기록(live_active)과
    qty=2의 tier1 잔여계약(from_tier1_remainder)은 다른 모집단이다.

실행: python tests/test_425_loss_tier1_qty1.py   (COM/브로커 불필요)
"""
import ast
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN_PY = os.path.join(_ROOT, "main.py")

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _main_tree():
    return ast.parse(io.open(_MAIN_PY, encoding="utf-8").read())


def _calls_named(node, fname):
    """node 하위에 `....fname(...)` 호출이 있는가."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            f = sub.func
            nm = getattr(f, "attr", None) or getattr(f, "id", None)
            if nm == fname:
                return True
    return False


# ══════════════ (A) 틱 배선이 독립 if인가 — 설계 불변식 ══════════════

def test_tick_wiring_is_independent_if():
    """`is_loss_tier1_qty1_shadow_hit` 분기가 elif 체인 안에 있으면 안 된다.

    AST에서 elif는 "부모 If의 orelse가 길이 1이고 그 원소가 If"인 형태다.
    """
    tree = _main_tree()
    elif_nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and len(node.orelse) == 1 \
                and isinstance(node.orelse[0], ast.If):
            elif_nodes.add(id(node.orelse[0]))

    found, in_elif = 0, 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if not _calls_named(node.test, "is_loss_tier1_qty1_shadow_hit"):
            continue
        found += 1
        if id(node) in elif_nodes:
            in_elif += 1
    check("qty=1 섀도 분기가 존재한다 (틱 + 분당 2곳)", found >= 2)
    check("그 분기 중 elif 체인에 들어간 것이 없다 (%d건)" % in_elif, in_elif == 0)


def test_tick_handler_defers_via_singleshot():
    """COM 콜백(§4) 준수 — 콜백 안에서 직접 주문/기록하지 않고 예약만 한다."""
    src = io.open(_MAIN_PY, encoding="utf-8").read()
    i = src.find("def _on_tick_price_update")
    j = src.find("\n    def _process_tick_stop", i)
    body = src[i:j] if i >= 0 and j > i else ""
    check("틱 핸들러에 qty=1 분기가 있다",
          "is_loss_tier1_qty1_shadow_hit" in body)
    check("§4 준수 - singleShot으로 예약한다",
          "QTimer.singleShot(0, self._process_tick_loss_tier1_qty1)" in body)
    check("§4 준수 - 콜백 안에서 직접 기록하지 않는다",
          "_record_loss_tier1_qty1_shadow" not in body)
    check("중복 예약 방지 플래그를 쓴다", "_tick_lt1_q1_pending" in body)


def test_processor_records_before_acting():
    """지연 처리기: 기록이 먼저, 액션은 플래그가 켜졌을 때만."""
    src = io.open(_MAIN_PY, encoding="utf-8").read()
    i = src.find("def _process_tick_loss_tier1_qty1")
    j = src.find("def _process_tick_tp1", i)
    body = src[i:j] if i >= 0 and j > i else ""
    check("처리기가 존재한다", bool(body))
    check("멱등 - 최상단에서 pending 플래그를 즉시 해제한다",
          "self._tick_lt1_q1_pending = False" in body)
    check("예약~실행 사이 상태 변화를 재확인한다",
          "is_loss_tier1_qty1_shadow_hit(price)" in body)
    ri = body.find("_record_loss_tier1_qty1_shadow")
    ai = body.find("_execute_loss_tier1_qty1_exit")
    check("기록이 액션보다 먼저다 (계측이 실적용에 종속되면 안 된다)",
          ri > 0 and ai > ri)
    check("액션은 두 킬스위치 AND로만 열린다",
          "LOSS_TIER1_QTY1_ENABLED and LOSS_TIER1_QTY1_TICK_ENABLED" in body)


def test_executor_is_full_exit():
    """qty=1은 쪼갤 수 없다 — 부분청산이 아니라 전량청산이어야 한다."""
    src = io.open(_MAIN_PY, encoding="utf-8").read()
    i = src.find("def _ts_execute_loss_tier1_qty1_exit")
    j = src.find("def _ts_record_loss_tier1_qty1_shadow", i)
    body = src[i:j] if i >= 0 and j > i else ""
    check("전량청산 실행기가 존재한다", bool(body))
    check("kind=EXIT_FULL (하드스톱과 같은 경로로 close_position까지 간다)",
          'kind="EXIT_FULL"' in body)
    # ⚠ 바로 위 독스트링이 "부분청산(EXIT_LOSS_TIER1)이 아니라"라고 설명하고 있으므로
    #   토큰 단순검색은 자기 설명문에 걸린다. **kind 대입만** 본다.
    check("kind로 EXIT_LOSS_TIER1(부분청산)을 쓰지 않는다",
          'kind="EXIT_LOSS_TIER1"' not in body)
    check("quantity != 1이면 빠져나온다 (잔여계약 오적용 방지)",
          "self.position.quantity != 1" in body)
    check("pending 중복 주문 가드", "_has_pending_order()" in body)
    check("§17 슬리피지 채널에서 하드스톱과 섞이지 않게 태깅한다",
          'hint_source="stop_tier1_qty1"' in body)


# ══════════════ (B) 기본값 — 판정 전 자동 전환 금지 ══════════════

def test_defaults_are_off():
    from config import settings as S
    check("(B) LOSS_TIER1_QTY1_ENABLED 기본값 False", S.LOSS_TIER1_QTY1_ENABLED is False)
    check("(B) 전환일이 비어 있다", S.LOSS_TIER1_QTY1_EFFECTIVE_DATE is None)
    check("틱 확장분 킬스위치가 별도로 존재한다",
          isinstance(S.LOSS_TIER1_QTY1_TICK_ENABLED, bool))
    check("기존 qty>=2 경로는 무변경(True 유지)", S.LOSS_TIER1_ENABLED is True)


# ══════════════ (C) 거래일 게이트 — 수학적 근거 ══════════════

def test_min_days_is_six_and_why():
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC["loss_tier1_qty1_shadow"]
    check("(C) min_days가 등록돼 있다", "min_days" in cr)
    check("(C) min_days >= 6", int(cr.get("min_days", 0)) >= 6)
    check("(C) alpha가 등록돼 있다", "alpha" in cr)

    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    m = importlib.import_module("generate_validation_campaign_report")
    # 부호검정으로 얻을 수 있는 최소 p — 전부 같은 부호일 때
    p5 = m._sign_test_p(0, 5)
    p6 = m._sign_test_p(0, 6)
    check("(C) n=5의 최소 p=0.0625 - α=0.05를 원리적으로 못 넘는다",
          abs(p5 - 0.0625) < 1e-9 and p5 > float(cr["alpha"]))
    check("(C) n=6의 최소 p=0.03125 - 여기서부터 기각 가능",
          abs(p6 - 0.03125) < 1e-9 and p6 < float(cr["alpha"]))


def test_day_summary_reproduces_425_state():
    """425차 등록 시점 실측 — 5거래일 전부 양수인데 유의하지 않다."""
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    m = importlib.import_module("generate_validation_campaign_report")
    # 일자별 평균 hyp_pnl_pts (07-22 / 07-28 / 07-30 / 08-03 / 08-04)
    day_means = [0.2971, 2.0314, 4.5483, 0.5885, 2.6682]
    out = m._paired_day_summary(day_means, 0.05)
    check("5일 전부 양수", out["days_positive"] == 5)
    check("부호검정 p=0.0625 (바닥)", abs(out["sign_p"] - 0.0625) < 1e-9)
    check("그럼에도 significant=False - 이것이 게이트의 요점",
          out["significant"] is False)


# ══════════════ (D) 판정 모집단 정제 ══════════════

def test_shadow_table_has_regime_columns():
    from utils.db_utils import fetchall
    from config.settings import TRADES_DB
    cols = {r[1] for r in fetchall(
        TRADES_DB, "PRAGMA table_info(loss_tier1_qty1_shadow)")}
    check("(D) live_active 컬럼 존재", "live_active" in cols)
    check("(D) from_tier1_remainder 컬럼 존재", "from_tier1_remainder" in cols)


def test_record_writes_regime_flags():
    src = io.open(_MAIN_PY, encoding="utf-8").read()
    i = src.find("def _ts_record_loss_tier1_qty1_shadow")
    j = src.find("def _ts_record_loss_tier2_shadow", i)
    body = src[i:j] if i >= 0 and j > i else ""
    check("(D) 기록 함수가 live_active를 받는다", "live_active: bool = False" in body)
    check("(D) INSERT에 두 컬럼이 포함된다",
          "live_active, from_tier1_remainder" in body)
    check("(D) 잔여계약 판별에 loss_tier1_done을 쓴다",
          "loss_tier1_done" in body)
    check("초 단위 ts를 남긴다 (분 절단이면 tier1↔풀스톱 순서 복원 불가)",
          '"%Y-%m-%d %H:%M:%S"' in body and '"%Y-%m-%d %H:%M:00"' not in body)


def test_eval_excludes_contaminated_rows():
    """실 DB로 판정 함수를 돌려 모집단 정제가 실제로 걸리는지 본다."""
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    m = importlib.import_module("generate_validation_campaign_report")
    out = m.resolve_and_eval_loss_tier1_qty1_shadow()
    check("(D) 판정이 dict를 반환한다", isinstance(out, dict) and "verdict" in out)
    check("(D) 제외 건수를 보고한다",
          "n_live_excluded" in out and "n_remainder_excluded" in out)
    check("(D) 425차 실측 - 잔여계약 1건(08-04 12:21)이 제외된다",
          int(out.get("n_remainder_excluded", 0)) >= 1)
    check("판정 2겹이 분리 보고된다 (미달 시엔 미노출)",
          out.get("verdict") == "INSUFFICIENT" or
          ("econ_ok" in out and "repro_ok" in out))
    # [MW0601 488차 재설계] 종전 핀 `verdict == "INSUFFICIENT"`(425차 시점 스냅샷)은
    # 표본이 차서 판정이 나오는 순간 깨진다 — 실제로 [11]이 PASS를 내기 시작한 뒤
    # FAIL 상태로 방치됐다(2026-08-23 발견). 캠페인 시작이 고정(2026-07-05)이라
    # 표본은 누적만 되므로, 실 DB에는 ② 내부 정합 · ③ 단조 하한 · ④ 판정 매핑만
    # 건다(test_424의 4축 표준 처방. 근거: DECISION_LOG 2026-08-23 MW0601 488차).
    from config.settings import VALIDATION_CAMPAIGN as _VC
    _cr = _VC["loss_tier1_qty1_shadow"]
    _n = int(out.get("n_resolved") or 0)
    _d = int(out.get("days") or 0)
    if out.get("verdict") == "INSUFFICIENT":
        check("(④) INSUFFICIENT이면 표본 관문 미달이 사유다 (n=%d/%s · 일=%d/%s)"
              % (_n, _cr["min_samples"], _d, _cr["min_days"]),
              _n < int(_cr["min_samples"]) or _d < int(_cr["min_days"]))
    else:
        check("(④) 판정이 나왔으면 표본 관문을 넘었다 (n=%d · 일=%d)" % (_n, _d),
              _n >= int(_cr["min_samples"]) and _d >= int(_cr["min_days"]))
        check("(④) verdict 매핑 - FAIL ↔ (econ_ok AND repro_ok), 아니면 PASS",
              out.get("verdict") ==
              ("FAIL" if (out.get("econ_ok") and out.get("repro_ok")) else "PASS"))
        check("(②) repro_ok == significant (일자단위 부호검정)",
              bool(out.get("repro_ok")) == bool(out.get("significant")))
    if out.get("paired_days"):
        check("(②) sign_p가 자기 (days_positive, paired_days)로 재계산된다",
              abs(out["sign_p"] - round(m._sign_test_p(
                  out["days_positive"], out["paired_days"]), 4)) < 1e-4)
    check("(③) 단조 하한 - 표본이 0821 실측(28건/10일) 아래로 줄 수 없다 "
          "(고정 시작 누적. 줄면 정제 규칙이 바뀐 것이다) (n=%d · 일=%d)" % (_n, _d),
          _n >= 28 and _d >= 10)


# ══════════════ position_tracker 판정 semantics ══════════════

def test_shadow_hit_semantics():
    from config.constants import POSITION_SHORT, POSITION_LONG
    from strategy.position.position_tracker import PositionTracker

    def _open(qty, direction=POSITION_SHORT, price=1000.0, atr=2.0):
        pt = PositionTracker(pt_value=50_000)
        pt._save_state = lambda *a, **k: None
        pt.open_position(direction=direction, price=price, quantity=qty,
                         atr=atr, grade="A", regime="RISK_ON")
        return pt

    pt2 = _open(qty=2)
    check("qty=2에서는 qty1 섀도가 뜨지 않는다 ([14]의 영역)",
          pt2.is_loss_tier1_qty1_shadow_hit(pt2.loss_tier1_price) is False)

    pt1 = _open(qty=1)
    check("qty=1 tier1 도달 시 True (SHORT: 가격 상승)",
          pt1.is_loss_tier1_qty1_shadow_hit(pt1.loss_tier1_price) is True)
    check("tier1 미달이면 False",
          pt1.is_loss_tier1_qty1_shadow_hit(pt1.entry_price) is False)
    pt1.loss_tier1_qty1_shadow_logged = True
    check("포지션당 1회만 - 기록 후엔 False",
          pt1.is_loss_tier1_qty1_shadow_hit(pt1.loss_tier1_price) is False)

    ptl = _open(qty=1, direction=POSITION_LONG)
    check("LONG도 대칭으로 동작한다 (가격 하락)",
          ptl.is_loss_tier1_qty1_shadow_hit(ptl.loss_tier1_price) is True)
    check("qty>=2 실적용 경로는 qty=1을 여전히 배제한다 (무변경)",
          pt1.is_loss_tier1_hit(pt1.loss_tier1_price) is False)


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 425차] qty=1 손절 계단화 - 배선·판정 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_tick_wiring_is_independent_if,
        test_tick_handler_defers_via_singleshot,
        test_processor_records_before_acting,
        test_executor_is_full_exit,
        test_defaults_are_off,
        test_min_days_is_six_and_why,
        test_day_summary_reproduces_425_state,
        test_shadow_table_has_regime_columns,
        test_record_writes_regime_flags,
        test_eval_excludes_contaminated_rows,
        test_shadow_hit_semantics,
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
