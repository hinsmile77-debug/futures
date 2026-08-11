"""[MW0602 461차 P-A/P-B/P-C] 보정기 표본 위생 + 도달불가 판정 회귀 테스트.

지키려는 불변식 — **라이브 신호 경로는 이번 배포에서 바뀌지 않는다.**
새 플래그가 전부 기본값일 때 보정기의 학습 표본·판정·출력이 종전과 완전히
동일해야 한다. 섀도 계측만 추가된다.

세부:
  P-A  오염행(WeightCollapse 인위값 raw=1.0)은 clean 윈도에서만 빠진다.
       라이브 윈도는 `CAL_COLLAPSE_EXCLUDE_LIVE=True`일 때만 빠진다(기본 False).
  P-B  `_evaluate_unreachable()`은 기본값에서 정적 하한·히스테리시스 없음 —
       403차 원본과 동일. 실효 하한 모드는 플래그를 켜야만 동작한다.
  P-C  `cal_applied`는 보정 함수를 실제로 통과한 분에만 True.

실행: python tests/test_461_calibration_hygiene.py   (COM/브로커 불필요)
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

# py37_32 콘솔은 cp949라 em-dash(U+2014)에서 UnicodeEncodeError가 난다.
# (py37에는 sys.stdout.reconfigure가 없어 TextIOWrapper로 감싼다.)
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

import config.settings as S
from learning.calibration import PredictionCalibrator, MultiHorizonCalibrator

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


class _Flags(object):
    """settings 플래그 임시 변경 — 테스트 간 오염 방지."""

    def __init__(self, **kw):
        self.kw = kw
        self.old = {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.old[k] = getattr(S, k)
            setattr(S, k, v)
        return self

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(S, k, v)
        return False


def _feed(cal, n=120, artifact_n=0, seed=7):
    """순위 정보가 **뚜렷한** 표본 + 인위값 행을 섞어 넣는다.

    약한 신호를 쓰면 축퇴 가드(auc<0.53)에 걸려 fitted가 안 돼 save/load 등
    후속 검증의 사전조건이 무너진다 — 여기서 검증하려는 건 축퇴 가드가 아니라
    표본 위생이므로, 가드를 확실히 통과하는 강도로 만든다(기저율도 0.5 근방이라
    out_max가 정적 하한 0.33 위에 놓여 도달불가 폴백에도 걸리지 않는다).
    """
    import random
    rnd = random.Random(seed)
    for i in range(n):
        raw = 0.25 + 0.60 * rnd.random()               # 0.25 ~ 0.85
        p_ok = 0.10 + 0.80 * (raw - 0.25) / 0.60       # 0.10 ~ 0.90 (강한 단조)
        cal.record(raw, rnd.random() < p_ok, is_artifact=False)
    for i in range(artifact_n):
        # 인위값: raw=1.0인데 적중은 기저율 수준 = 무정보 (라이브 실측과 같은 형태)
        cal.record(1.0, rnd.random() < 0.50, is_artifact=True)


# ── P-A ────────────────────────────────────────────────────────────────────
def test_artifact_excluded_from_clean_only():
    """기본 플래그: 오염행은 라이브 윈도에 **남고** clean 윈도에서만 빠진다."""
    with _Flags(CAL_COLLAPSE_EXCLUDE_LIVE=False):
        cal = PredictionCalibrator()
        _feed(cal, n=100, artifact_n=30)
        check("라이브 윈도는 오염행 포함 (130건)", len(cal._probs) == 130)
        check("clean 윈도는 오염행 제외 (100건)", len(cal._clean_probs) == 100)
        check("오염행 카운터=30", cal.artifact_count == 30)
        check("clean 윈도에 raw=1.0 없음", all(p < 0.999 for p in cal._clean_probs))


def test_live_exclusion_only_when_flag_on():
    """🔴 라이브 제외는 플래그를 켰을 때만 — 기본 동작 회귀 방지."""
    with _Flags(CAL_COLLAPSE_EXCLUDE_LIVE=True):
        cal = PredictionCalibrator()
        _feed(cal, n=100, artifact_n=30)
        check("플래그 ON이면 라이브 윈도도 오염행 제외 (100건)", len(cal._probs) == 100)
        check("플래그 ON에서도 clean 윈도는 100건", len(cal._clean_probs) == 100)


def test_record_default_arg_is_backward_compatible():
    """기존 호출부(`record(p, c)`)는 종전과 완전히 동일하게 동작한다."""
    cal = PredictionCalibrator()
    cal.record(0.42, True)
    cal.record(0.38, False)
    check("is_artifact 생략 시 라이브 윈도 누적", len(cal._probs) == 2)
    check("is_artifact 생략 시 clean 윈도도 누적", len(cal._clean_probs) == 2)
    check("오염 카운터 0", cal.artifact_count == 0)


def test_shadow_diag_computed_and_live_untouched():
    """섀도 진단이 계산되지만 라이브 모델·출력은 건드리지 않는다."""
    with _Flags(CAL_COLLAPSE_SHADOW_ENABLED=True, CAL_COLLAPSE_EXCLUDE_LIVE=False):
        cal = PredictionCalibrator()
        _feed(cal, n=140, artifact_n=40)
        cal.fit()
        sd = cal.shadow_diag
        check("섀도 진단 생성됨", sd is not None)
        if sd:
            check("섀도 n은 clean 윈도 크기(140)", sd["n"] == 140)
            check("섀도 artifact_n=40", sd["artifact_n"] == 40)
            check("섀도 span/auc/out_max 존재",
                  all(k in sd for k in ("span", "auc", "out_max", "base")))
        # 라이브 출력이 섀도 모델로 오염되지 않았는지 — calibrate는 _model만 쓴다
        if cal.is_fitted:
            import numpy as np
            expect = float(np.clip(
                cal._model.predict_proba(np.array([[0.5]]))[0][1], 0.0, 1.0))
            got = cal.calibrate(0.5)
            # 전환 블렌딩(_transition_steps)이 걸릴 수 있어 raw와의 사이 값이면 통과
            lo, hi = min(expect, 0.5), max(expect, 0.5)
            check("calibrate()는 라이브 모델 기반", lo - 1e-9 <= got <= hi + 1e-9)


def test_shadow_disabled_returns_none():
    with _Flags(CAL_COLLAPSE_SHADOW_ENABLED=False):
        cal = PredictionCalibrator()
        _feed(cal, n=120, artifact_n=20)
        cal.fit()
        check("섀도 비활성이면 진단 None", cal.shadow_diag is None)


def test_save_load_roundtrip_and_legacy_pkl():
    """clean 윈도가 영속화되고, 구버전 저장본도 깨지지 않는다."""
    import tempfile
    import joblib
    cal = PredictionCalibrator()
    _feed(cal, n=120, artifact_n=25)
    cal.fit()
    if not cal.is_fitted:
        check("save/load 사전조건(fitted)", False)
        return
    d = tempfile.mkdtemp()
    p = os.path.join(d, "cal.pkl")
    check("save 성공", cal.save(p) is True)

    cal2 = PredictionCalibrator()
    cal2.load(p)
    check("복원 후 라이브 윈도 일치", len(cal2._probs) == len(cal._probs))
    check("복원 후 clean 윈도 일치", len(cal2._clean_probs) == len(cal._clean_probs))
    check("복원 후 오염 카운터 일치", cal2.artifact_count == cal.artifact_count)

    # 구버전 저장본(clean 키 없음) — 라이브는 정상, 섀도만 비어야 한다
    legacy = joblib.load(p)
    for k in ("clean_probs", "clean_labels", "artifact_n"):
        legacy.pop(k, None)
    lp = os.path.join(d, "legacy.pkl")
    joblib.dump(legacy, lp, protocol=4)
    cal3 = PredictionCalibrator()
    ok = cal3.load(lp)
    check("구버전 저장본 load 성공", ok is True)
    check("구버전 저장본: 라이브 윈도 복원됨", len(cal3._probs) == len(cal._probs))
    check("구버전 저장본: clean 윈도 비어 시작", len(cal3._clean_probs) == 0)


# ── P-B ────────────────────────────────────────────────────────────────────
def _cal_with_out_max(out_max):
    """_last_out_max를 직접 세팅한 보정기 — 판정 로직만 격리 검증."""
    cal = PredictionCalibrator()
    cal._last_out_max = out_max
    return cal


def test_unreachable_default_matches_403_original():
    """기본값에서는 정적 하한 단일 문턱 — 403차 원본과 동일(히스테리시스 없음)."""
    with _Flags(CAL_UNREACHABLE_FALLBACK_ENABLED=True,
                CAL_UNREACHABLE_USE_EFFECTIVE_FLOOR=False,
                ENS_CONF_FLOOR_FOR_AUTO=0.33):
        c = _cal_with_out_max(0.3299)
        c.update_effective_floor(0.50)          # 실효 하한이 높아도 무시돼야 한다
        v, _ = c._evaluate_unreachable()
        check("정적하한 미만 → 도달불가", v is True)

        c2 = _cal_with_out_max(0.3301)
        c2.update_effective_floor(0.50)
        v2, _ = c2._evaluate_unreachable()
        check("정적하한 이상 → 도달가능 (실효하한 무시)", v2 is False)


def test_floor_shadow_always_computed():
    """플래그가 꺼져 있어도 섀도 판정은 항상 남는다 — 켜기 전 영향 관측용."""
    with _Flags(CAL_UNREACHABLE_FALLBACK_ENABLED=True,
                CAL_UNREACHABLE_USE_EFFECTIVE_FLOOR=False,
                CAL_UNREACHABLE_HYSTERESIS=0.0,
                ENS_CONF_FLOOR_FOR_AUTO=0.33):
        c = _cal_with_out_max(0.383)
        c.update_effective_floor(0.389)         # 2026-08-11 오전 실측 상황
        live, _ = c._evaluate_unreachable()
        sh = c.floor_shadow
        check("라이브(정적) 판정 = 도달가능", live is False)
        check("섀도 판정 존재", sh is not None)
        if sh:
            check("섀도 need = 실효하한 0.389", abs(sh["need"] - 0.389) < 1e-9)
            check("섀도 판정 = 도달불가 (0811 오전 재현)", sh["verdict"] is True)


def test_effective_floor_mode_and_hysteresis():
    """실효 하한 모드: 기준선이 max(정적, 실효)이고 히스테리시스가 왕복을 막는다."""
    with _Flags(CAL_UNREACHABLE_FALLBACK_ENABLED=True,
                CAL_UNREACHABLE_USE_EFFECTIVE_FLOOR=True,
                CAL_UNREACHABLE_HYSTERESIS=0.01,
                ENS_CONF_FLOOR_FOR_AUTO=0.33):
        # 발동은 지연 없이 — 0811 오전 실측값(out_max 0.383 < need 0.389).
        # 🔴 양측 밴드였다면 0.383이 밴드 안(0.379~0.389)이라 발동하지 않는다.
        #    이 케이스가 초안 설계를 잡아낸 회귀다 — 완화 금지.
        c = _cal_with_out_max(0.383)
        c.update_effective_floor(0.389)
        v, _ = c._evaluate_unreachable()
        check("실효 모드: out_max<need면 즉시 발동 (0811 오전 재현)", v is True)

        # 도달불가 상태에서 need 바로 위(밴드 안)로 올라와도 아직 안 풀린다
        c._unreachable = True
        c._last_out_max = 0.3925           # need=0.389, h=0.01 → 0.399 넘어야 해소
        v2, _ = c._evaluate_unreachable()
        check("히스테리시스: 밴드 안 복귀는 미해소", v2 is True)

        c._last_out_max = 0.400            # 밴드 밖 → 해소
        v3, _ = c._evaluate_unreachable()
        check("히스테리시스: 밴드 밖 복귀는 해소", v3 is False)

        # 적용 중 상태에서 need 아래로 내려가면 밴드와 무관하게 즉시 발동
        c._unreachable = False
        c._last_out_max = 0.3825           # need-h(0.379)보다 위지만 need보단 아래
        v4, _ = c._evaluate_unreachable()
        check("히스테리시스는 편측 — 발동을 늦추지 않는다", v4 is True)


def test_effective_floor_never_lowers_bar():
    """실효 하한이 정적 하한보다 낮아도 기준선이 내려가면 안 된다."""
    with _Flags(CAL_UNREACHABLE_FALLBACK_ENABLED=True,
                CAL_UNREACHABLE_USE_EFFECTIVE_FLOOR=True,
                CAL_UNREACHABLE_HYSTERESIS=0.0,
                ENS_CONF_FLOOR_FOR_AUTO=0.33):
        c = _cal_with_out_max(0.32)
        c.update_effective_floor(0.25)      # 정적보다 낮음
        v, _ = c._evaluate_unreachable()
        check("기준선은 max(정적, 실효) — 완화되지 않음", v is True)


def test_update_effective_floor_rejects_bad_input():
    c = _cal_with_out_max(0.35)
    c.update_effective_floor(None)
    check("None은 무시", c._effective_floor is None)
    c.update_effective_floor(0.0)
    check("0.0은 무시(미설정과 구분)", c._effective_floor is None)
    c.update_effective_floor("x")
    check("비숫자는 무시", c._effective_floor is None)
    c.update_effective_floor(0.42)
    check("정상값 반영", abs(c._effective_floor - 0.42) < 1e-9)


def test_fallback_disabled_short_circuits():
    with _Flags(CAL_UNREACHABLE_FALLBACK_ENABLED=False):
        c = _cal_with_out_max(0.01)
        c.update_effective_floor(0.9)
        v, reason = c._evaluate_unreachable()
        check("폴백 비활성이면 항상 False", v is False and reason == "비활성")


# ── P-C ────────────────────────────────────────────────────────────────────
def test_multihorizon_is_fitted_accessor():
    m = MultiHorizonCalibrator(["1m", "3m"])
    check("미fit 호라이즌 False", m.is_fitted("3m") is False)
    check("없는 호라이즌 False", m.is_fitted("99m") is False)
    for i in range(200):
        m.record("3m", 0.3 + 0.002 * (i % 100), i % 3 == 0)
    m.fit_all()
    check("fit 후 True 또는 가드로 False (예외 없음)",
          m.is_fitted("3m") in (True, False))


def test_insert_arity_matches_columns():
    """[P-C] ensemble_decisions INSERT — 컬럼 수 = 플레이스홀더 수 = 튜플 길이."""
    import ast
    import re
    src = open(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "learning", "prediction_buffer.py"),
        encoding="utf-8").read()
    pat = r"INSERT OR IGNORE INTO ensemble_decisions \((.*?)\) VALUES \((.*?)\)"
    pairs = []
    for m in re.finditer(pat, src, re.S):
        cols = [c.strip() for c in m.group(1).replace("\n", " ").split(",") if c.strip()]
        pairs.append((len(cols), m.group(2).count("?")))
    check("INSERT 문 2개 발견", len(pairs) == 2)
    for i, (nc, nq) in enumerate(pairs):
        check("INSERT#%d 컬럼수==플레이스홀더 (%d)" % (i + 1, nc), nc == nq)
    col_lists = [m.group(1) for m in re.finditer(pat, src, re.S)]
    check("cal_applied가 두 INSERT 컬럼목록 모두에 있음",
          len(col_lists) == 2 and all("cal_applied" in c for c in col_lists))

    tree = ast.parse(src)
    lens = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "ens_row":
            lens.append(len(node.value.elts))
    # [MW0602 462차] 47 → 48: `min_conf_effective` 추가. 이 상수는 컬럼이 늘 때마다
    # 함께 갱신해야 한다 — 여기서 막고 싶은 것은 "튜플과 컬럼목록이 어긋나는 것"이고,
    # 그 검사는 바로 위 INSERT#n 컬럼수==플레이스홀더가 이미 하고 있다.
    check("ens_row 튜플 길이 = 48", lens and lens[0] == 48)


def test_cal_applied_column_registered():
    """[P-C] 마이그레이션 목록에 cal_applied가 있어야 한다(멱등 ALTER 대상)."""
    src = open(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "utils", "db_utils.py"),
        encoding="utf-8").read()
    check('마이그레이션에 "cal_applied": "INTEGER" 등록',
          '"cal_applied": "INTEGER"' in src)


def test_migration_is_idempotent_on_temp_db():
    """[P-C] 임시 DB에 ALTER를 두 번 돌려도 실패하지 않는다 (운영 DB 무접촉)."""
    import sqlite3
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE ensemble_decisions (id INTEGER PRIMARY KEY, ts TEXT)")
    con.commit()
    for _ in range(2):
        cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
        if "cal_applied" not in cols:
            con.execute("ALTER TABLE ensemble_decisions ADD COLUMN cal_applied INTEGER")
        con.commit()
    cols = {r[1] for r in con.execute("PRAGMA table_info(ensemble_decisions)")}
    check("멱등 ALTER 후 컬럼 1개만 존재", "cal_applied" in cols)
    con.close()


# ── 회귀: 라이브 경로 불변 ──────────────────────────────────────────────────
def test_live_calibration_output_unchanged_by_shadow():
    """섀도 ON/OFF가 라이브 calibrate() 출력을 바꾸지 않는다."""
    def _build(shadow):
        with _Flags(CAL_COLLAPSE_SHADOW_ENABLED=shadow, CAL_COLLAPSE_EXCLUDE_LIVE=False):
            c = PredictionCalibrator()
            _feed(c, n=140, artifact_n=40, seed=11)
            c.fit()
            c._transition_steps = 0        # 블렌딩 제거 — 순수 모델 출력 비교
            return [round(c.calibrate(x), 10) for x in (0.3, 0.4, 0.5, 0.7, 1.0)]
    check("섀도 ON/OFF에서 라이브 출력 동일", _build(True) == _build(False))


if __name__ == "__main__":
    print("=== P-A 표본 위생 ===")
    test_artifact_excluded_from_clean_only()
    test_live_exclusion_only_when_flag_on()
    test_record_default_arg_is_backward_compatible()
    test_shadow_diag_computed_and_live_untouched()
    test_shadow_disabled_returns_none()
    test_save_load_roundtrip_and_legacy_pkl()

    print("\n=== P-B 도달불가 판정 ===")
    test_unreachable_default_matches_403_original()
    test_floor_shadow_always_computed()
    test_effective_floor_mode_and_hysteresis()
    test_effective_floor_never_lowers_bar()
    test_update_effective_floor_rejects_bad_input()
    test_fallback_disabled_short_circuits()

    print("\n=== P-C 계측 ===")
    test_multihorizon_is_fitted_accessor()
    test_insert_arity_matches_columns()
    test_cal_applied_column_registered()
    test_migration_is_idempotent_on_temp_db()

    print("\n=== 회귀: 라이브 경로 불변 ===")
    test_live_calibration_output_unchanged_by_shadow()

    print()
    if FAILURES:
        print("FAILED %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  -", f)
        sys.exit(1)
    print("전부 통과 — 보정기 표본 위생(섀도) + 도달불가 실효하한(OFF) + cal_applied 계측")
