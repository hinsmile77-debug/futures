# -*- coding: utf-8 -*-
"""[MW0602 494차] F-8 회귀 — GuardFair 공정홀드아웃의 **측정 가능성** 복구.

**무엇이 문제였나.** `holdout_bars=1850`(≈5거래일)인데 현행 모델은 매일(때로 하루
두 번) 재학습된다. `_fair_validity()`의 조건 `train_end < holdout_start` 가 **산술적으로
성립 불가**라 8거래일 내내 6/6 무효였고, 그럼에도 캠페인 [23]은 `✅ PASS`로 렌더된다 —
*"판정이 살아 있는 것처럼 보이는 죽은 채널"* 이다(0825 이상점 1-11).

**여기서 고치는 것은 진단값뿐이다.** `holdout_bars` 를 오늘 관측으로 고르면
313차 ④(관측 후 기준 수립) 위반이다. 그래서 고정하는 불변식:

① **판정 로직 무변경** — 같은 입력에 같은 bool 을 돌려준다.
② `gap_bars` 가 홀드아웃 중 현행이 **이미 학습한 봉 수**를 정확히 센다.
③ 유효한 날에도 값을 남긴다 — 무효율만 보면 분모가 사라진다.
④ 호라이즌마다 **리셋된다** — 리셋 안 하면 측정 불가 경로에서 직전 값이 오귀속된다.
⑤ DB 컬럼이 존재하고 왕복한다.

실행:
    py37_32\\python.exe tests/test_494_guardfair_gap_bars.py
"""
import io
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def _read(rel):
    with io.open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


class _Stub(object):
    """`_fair_validity` 만 떼어 쓰기 위한 최소 스텁 — 재학습 전체를 돌리지 않는다."""

    def __init__(self, meta, ts_list):
        self._meta = meta
        self._last_train_ts = ts_list
        self._last_fair_diag = "STALE"      # ④ 리셋 확인용 오염값

    def _read_model_meta(self, horizon_key):
        return self._meta

    from learning.batch_retrainer import BatchRetrainer as _BR
    _fair_validity = _BR._fair_validity


def _ts(i):
    return "2026-08-%02d %02d:%02d:00" % (10 + i // 400, 9 + (i % 400) // 60, (i % 60))


def test_gap_bars_counts_contaminated_bars():
    """홀드아웃 100봉 중 현행이 40봉을 이미 학습했다면 gap_bars=40."""
    ts = ["2026-08-25 %02d:%02d:00" % (9 + i // 60, i % 60) for i in range(300)]
    holdout = 100
    ho_start = ts[-holdout]              # ts[200]
    train_end = ts[-holdout + 39]        # ts[239] — 홀드아웃 40번째 봉까지 학습
    st = _Stub({"train_end_ts": train_end, "source": "intraday"}, ts)

    valid, note = st._fair_validity("3m", holdout)
    assert valid is False, "현행이 홀드아웃을 학습했으므로 무효여야 한다"
    assert st._last_fair_diag["gap_bars"] == 40, st._last_fair_diag
    assert st._last_fair_diag["holdout_start_ts"].startswith(ho_start[:16])
    assert st._last_fair_diag["train_end_ts"].startswith(train_end[:16])
    # 성립에 필요한 최대 홀드아웃
    assert holdout - st._last_fair_diag["gap_bars"] == 60


def test_valid_case_still_records_zero_gap():
    """③ 유효한 날에도 남긴다 — 그날의 gap_bars=0 이 분모다."""
    ts = ["2026-08-25 %02d:%02d:00" % (9 + i // 60, i % 60) for i in range(300)]
    st = _Stub({"train_end_ts": "2026-08-24 15:40:00", "source": "eod"}, ts)
    valid, note = st._fair_validity("3m", 100)
    assert valid is True, note
    assert st._last_fair_diag["gap_bars"] == 0, st._last_fair_diag


def test_full_contamination_equals_holdout_bars():
    """현행이 홀드아웃 전체를 학습 = 라이브 실제 상태(매일 재학습)."""
    ts = ["2026-08-25 %02d:%02d:00" % (9 + i // 60, i % 60) for i in range(300)]
    st = _Stub({"train_end_ts": ts[-1], "source": "intraday"}, ts)
    st._fair_validity("3m", 100)
    assert st._last_fair_diag["gap_bars"] == 100


def test_diag_is_reset_on_early_returns():
    """④ 측정 불가 경로에서 직전 값이 남으면 오귀속이 된다."""
    st = _Stub(None, ["2026-08-25 09:00:00"] * 300)
    valid, note = st._fair_validity("3m", 100)
    assert valid is False and "메타 없음" in note
    assert st._last_fair_diag is None, "리셋되지 않았다: %r" % (st._last_fair_diag,)

    st2 = _Stub({"train_end_ts": None}, ["x"] * 300)
    st2._fair_validity("3m", 100)
    assert st2._last_fair_diag is None

    st3 = _Stub({"train_end_ts": "2026-08-24 15:40:00"}, ["x"] * 50)   # ts 부족
    st3._fair_validity("3m", 100)
    assert st3._last_fair_diag is None


def test_verdict_logic_unchanged():
    """① 판정 bool 은 종전과 동일 — 이 커밋은 진단만 넣는다."""
    src = _read(os.path.join("learning", "batch_retrainer.py"))
    i = src.find("def _fair_validity(")
    body = src[i:i + 4200]
    # 종전 3개 조기반환 + 2개 결론 반환이 그대로인가
    for frag in ("현행 메타 없음(457차 이전 모델)",
                 "현행 train_end_ts 없음",
                 "홀드아웃 경계 ts 불명",
                 'if str(_end) >= str(_ho_start):',
                 'return True, ("유효 — 현행 train_end='):
        assert frag in body, frag
    assert "판정 로직 무변경" in body


def test_db_column_exists_and_roundtrips():
    """⑤ 컬럼 존재 + 왕복. 스키마 변경은 464차 선례대로 ALTER + NULL 허용."""
    from config.settings import TRADES_DB
    import utils.db_utils as db
    db.init_trades_db()
    with sqlite3.connect(TRADES_DB, timeout=10) as c:
        cols = {r[1] for r in c.execute("PRAGMA table_info(guard_shadow_log)").fetchall()}
    assert "fair_gap_bars" in cols, cols

    # 저장 함수 시그니처가 새 인자를 받는가 (실제 INSERT 는 하지 않는다 —
    # 검증 스크립트가 실거래 DB 를 오염시키면 안 된다: feedback_isolate_stateful_verification)
    import inspect
    sig = inspect.signature(db.save_guard_shadow)
    assert "fair_gap_bars" in sig.parameters
    assert sig.parameters["fair_gap_bars"].default is None, "기본 None 이어야 구버전 호출부가 산다"

    src = _read(os.path.join("utils", "db_utils.py"))
    ins = src[src.find("INSERT INTO guard_shadow_log"):][:900]
    assert ins.count("?") == 18, "플레이스홀더 수와 컬럼 수가 어긋났다"


def test_holdout_setting_is_untouched():
    """🔴 값 변경은 이번 범위 밖 — 주간회의 2026-08-28 안건 ⑦."""
    s = _read(os.path.join("config", "settings.py"))
    i = s.find("EOD_GUARD_FAIR_HOLDOUT")
    assert i > 0
    assert '"holdout_bars": 1850' in s[i:i + 1500], "holdout_bars 가 1850 이 아니다"


def test_collector_indicator_registered():
    src = _read(os.path.join(".claude", "skills", "mireuk-daily-check", "scripts",
                             "collect_evidence.py"))
    i = src.find('"GuardFair_gap_bars"')
    assert i > 0, "수집기 §12 에 GuardFair_gap_bars 가 없다"
    block = src[i:i + 1600]
    assert '"measured_since": "2026-08-26"' in block
    assert "benign" not in block.split('"why"')[0], "🔴 benign 으로 등록하면 안 된다"


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for fn in (test_gap_bars_counts_contaminated_bars,
               test_valid_case_still_records_zero_gap,
               test_full_contamination_equals_holdout_bars,
               test_diag_is_reset_on_early_returns,
               test_verdict_logic_unchanged,
               test_db_column_exists_and_roundtrips,
               test_holdout_setting_is_untouched,
               test_collector_indicator_registered):
        try:
            fn()
            print("[ok]   %s" % fn.__name__)
        except Exception as e:
            print("[FAIL] %s: %r" % (fn.__name__, e))
            FAILURES.append(fn.__name__)
    print("-" * 60)
    print("전부 통과" if not FAILURES else "실패 %d건: %s" % (len(FAILURES), FAILURES))
    sys.exit(1 if FAILURES else 0)
