# -*- coding: utf-8 -*-
"""[MW0602 492차 F-7] 학습률 조절기 상한 포화 · 도달 불가 하향 — 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
배경 (상세: dev_memory/DECISION_LOG.md 2026-08-24 492차 · 0824 리포트 1-13)
────────────────────────────────────────────────────────────────────────────
`DriftAdjuster` 는 정확도가 3일 연속 50% 미만이면 alpha 를 1.5배 올린다. 그런데
alpha 는 2026-08-11 이래 `ALPHA_MAX`(0.01)에 붙박여 있어 `min()` 이 같은 값을
돌려준다 — **무연산**이다. 그런데도 매일 `WARNING` 으로 "alpha 0.01000→0.01000"
을 찍어 최근 9일 중 6일이 **대응하고 있는 것처럼** 보였다.
반대 방향(하향)은 `RECOVERY_THRESHOLD=0.58` 이 최근 10일 acc 최댓값(0.4048)보다
높아 **분기 자체가 도달 불가**다. 즉 손잡이가 양방향으로 다 잠겨 있다.

🔴 이 Fix 는 **계측만** 붙인다. `ALPHA_MAX`·`ALPHA_UP_FACTOR`·`DRIFT_THRESHOLD`·
   `RECOVERY_THRESHOLD`·`MIN_SAMPLES_REQUIRED` 전부 **무변경**이다.
   임계를 관측값에서 역산하지 않는다(사전등록 ④).

지키는 불변식:
  T1  상수 5종 무변경.
  T2  `ALPHA_MAX` 에서 상향 조건이 성립하면 alpha 불변 + 액션 `DRIFT_UP_SATURATED`.
  T3  상한 미도달이면 종전대로 `DRIFT_UP` 이고 alpha 가 **실제로** 오른다.
  T4  🔴 **하향 경로 도달 가능성** — 라이브 상태파일의 최근 10일 acc 최댓값이
      `RECOVERY_THRESHOLD` 미만이다. **이 검사가 깨지는 날이 「하향 경로가
      살아난 날」이며, 그때 이 테스트와 1-13 을 함께 갱신해야 한다.**
  T5  `record_accuracy()` 로그에 `n=` · `src=` 병기(진짜 0% vs 미측정 0 구분).
  T6  소비부 — 대시보드 라벨 표에 `DRIFT_UP_SATURATED` 키가 있다.
  T7  수집기 §12 에 `sgd_alpha`(benign 아님) · `drift_action` 2행.

⚠ 상태파일 격리: `DriftAdjuster` 는 생성·조정마다 `data/drift_adjuster_state.json`
  에 **자동 저장**한다. 반드시 임시 경로를 넘긴다(라이브 상태 오염 방지).

실행: python tests/test_492_drift_adjuster_saturation.py   (COM/브로커 불필요)
"""

import io
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import learning.self_learning.drift_adjuster as DA  # noqa: E402

FAILURES = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _read(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


def _fresh(tmp, alpha, history):
    """라이브 상태파일과 격리된 조절기 — 임시 경로 전용."""
    adj = DA.DriftAdjuster(path=os.path.join(tmp, "state.json"))
    adj._alpha = alpha
    adj._acc_history.clear()
    for a in history:
        adj._acc_history.append(a)
    return adj


def test_t1_constants_unchanged():
    for name, want in (("ALPHA_MAX", 0.01), ("ALPHA_UP_FACTOR", 1.5),
                       ("DRIFT_THRESHOLD", 0.50), ("RECOVERY_THRESHOLD", 0.58),
                       ("MIN_SAMPLES_REQUIRED", 15)):
        got = getattr(DA, name)
        check("T1: %s == %s (got=%s)" % (name, want, got), got == want)


def test_t2_saturated_is_a_noop():
    tmp = tempfile.mkdtemp(prefix="drift492_")
    try:
        adj = _fresh(tmp, DA.ALPHA_MAX, [0.26, 0.39, 0.11])
        action = adj._adjust_alpha()
        check("T2: alpha 불변 (got=%.5f)" % adj._alpha, adj._alpha == DA.ALPHA_MAX)
        check("T2: 액션 DRIFT_UP_SATURATED (got=%r)" % action,
              action == "DRIFT_UP_SATURATED")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_t3_real_up_unchanged():
    tmp = tempfile.mkdtemp(prefix="drift492_")
    try:
        adj = _fresh(tmp, 0.001, [0.26, 0.39, 0.11])
        action = adj._adjust_alpha()
        check("T3: 액션 DRIFT_UP (got=%r)" % action, action == "DRIFT_UP")
        check("T3: alpha 실제 상향 0.001→%.5f" % adj._alpha,
              abs(adj._alpha - 0.0015) < 1e-9)
        # 상한을 넘지 않는다
        adj2 = _fresh(tmp, 0.009, [0.26, 0.39, 0.11])
        adj2._adjust_alpha()
        check("T3: 상한 클램프 유지 (got=%.5f)" % adj2._alpha,
              adj2._alpha == DA.ALPHA_MAX)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_t4_recovery_branch_is_unreachable():
    """🔴 깨지는 날 = 하향 경로가 살아난 날. 그때 1-13 과 함께 갱신할 것."""
    p = os.path.join(ROOT, "data", "drift_adjuster_state.json")
    if not os.path.exists(p):
        check("T4: 라이브 상태파일 없음 — 판정 보류(미측정)", True)
        return
    hist = (json.loads(io.open(p, encoding="utf-8").read()) or {}).get("acc_history") or []
    if not hist:
        check("T4: 이력 비어 있음 — 판정 보류(미측정)", True)
        return
    mx = max(float(a) for a in hist)
    check("T4: 최근 %d일 acc 최댓값 %.4f < RECOVERY_THRESHOLD %.2f "
          "(하향 분기 도달 불가 — 0824 1-13)" % (len(hist), mx, DA.RECOVERY_THRESHOLD),
          mx < DA.RECOVERY_THRESHOLD)


def test_t5_source_and_samples_in_log():
    src = _read("learning/self_learning/drift_adjuster.py")
    check("T5: n= 병기", "acc=%.1f%% n=%s src=online_learner.recent_accuracy" in src)
    check("T5: 미측정은 NA", '("NA" if n_samples is None else n_samples)' in src)
    check("T5: 포화 로그 문구", "상한 포화 — 무연산" in src)
    check("T5: 포화는 WARNING 아님", "return \"DRIFT_UP_SATURATED\"" in src)


def test_t6_dashboard_label():
    dash = _read("dashboard/main_dashboard.py")
    check("T6: 라벨 표 키", '"DRIFT_UP_SATURATED": (' in dash)
    check("T6: 툴팁 설명", "DRIFT_UP_SATURATED: 하락은 계속인데" in dash)


def test_t7_collector_rows():
    col = _read(".claude/skills/mireuk-daily-check/scripts/collect_evidence.py")
    check("T7: sgd_alpha 행", '"sgd_alpha": {' in col)
    check("T7: drift_action 행", '"drift_action": {' in col)
    # sgd_alpha 는 benign 이 아니어야 한다 — 상한 고착이 정상이라는 판단이 없다
    blk = col[col.find('"sgd_alpha": {'):]
    blk = blk[:blk.find('"drift_action"')]
    check("T7: sgd_alpha 는 benign 아님", '"benign"' not in blk)


def test_t8_prune_failure_returns_zero():
    """[F-8] 커밋 실패분을 성공으로 세지 않는다 — 0824 1-14 의 실체.

    ⚠ `learning.batch_retrainer` 는 numpy/sklearn 을 끌어와 COM 없는 환경에서
      import 가 무겁다 — 원문 검사로 계약만 고정한다.
    """
    src = _read("learning/batch_retrainer.py")
    check("T8: 실패 시 반환 0", "deleted = 0                  # 🔴 커밋 실패분을" in src)
    check("T8: 재시도는 1회뿐(루프 금지)", "for _attempt in (1, 2):" in src)
    check("T8: 재시도 간 집계 이월 금지",
          "deleted, detail = 0, []          # 재시도 시 1차 집계를 이월하지 않는다" in src)
    check("T8: 실패 로그에 cutoff·keep·대상",
          "실패(2회, 반환=0행)" in src and "대상=%s" in src)
    check("T8: 테이블 없음과 락을 구분", '"no such table" in _msg' in src)
    check("T8: 태그 무변경(과거 로그 대조 유지)",
          '"[Retrain] DB pruning 완료' in src)
    main = _read("main.py")
    check("T8: [GBM] 0행도 말한다", "[GBM] DB pruning: 0행" in main)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_t1_constants_unchanged, test_t2_saturated_is_a_noop,
               test_t3_real_up_unchanged, test_t4_recovery_branch_is_unreachable,
               test_t5_source_and_samples_in_log, test_t6_dashboard_label,
               test_t7_collector_rows, test_t8_prune_failure_returns_zero):
        try:
            fn()
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
