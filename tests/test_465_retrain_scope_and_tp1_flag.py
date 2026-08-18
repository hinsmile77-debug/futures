"""[MW0602 465차] 재학습 스코프 한정(P1·P5) + TP1 도달 계측(P4) 회귀 테스트.

지키려는 불변식:
  P1  DriftRetrain **단독** 트리거일 때만 교체 스코프를 판정 기준 호라이즌으로
      좁힌다. WarmupRetrain·weekly·monthly가 함께 성립하면 ALL(종전 동작)이다.
      판정 기준 호라이즌(DRIFT_RETRAIN_TRIGGER_HORIZON)은 main.py가 실제로 읽는
      `horizon_accuracy("5m")`와 **같은 값**이어야 한다 — 어긋나면 "5m으로 판정하고
      다른 호라이즌을 교체"가 된다.
  P5  재학습 완료 후 BiasReset 냉각 해제는 **교체된 호라이즌에만** 적용한다.
      스코프가 비어 있으면(ALL) 종전과 완전히 동일하게 전 호라이즌을 초기화한다.
      킬스위치 OFF 시에도 종전 동작 복원.
  P4  `exit_reason` 문자열은 **바꾸지 않는다**(사전등록 채널 [15]·[26]·[48]과
      bar_stop_path_watch·test_439가 `LIKE '%하드스톱%'`로 필터한다).
      대신 `tp1_reached` 관측 컬럼으로 보호 트레일과 진짜 손절을 구분한다.
      INSERT 컬럼수·플레이스홀더·값 튜플 길이가 일치해야 한다.

실행: python tests/test_465_retrain_scope_and_tp1_flag.py   (COM/브로커/DB 불필요)
"""
import ast
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

import config.settings as S
from config.settings import HORIZONS

FAILURES = []
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _read(rel):
    with open(os.path.join(BASE, rel), "r", encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════
# P1 — DriftRetrain 스코프 한정
# ══════════════════════════════════════════════════════════════════
def test_p1_settings():
    check("DRIFT_RETRAIN_SCOPE_LIMIT 등록 + 기본 True",
          getattr(S, "DRIFT_RETRAIN_SCOPE_LIMIT", None) is True)
    check("DRIFT_RETRAIN_TRIGGER_HORIZON 등록",
          hasattr(S, "DRIFT_RETRAIN_TRIGGER_HORIZON"))
    check("트리거 호라이즌이 유효한 HORIZONS 원소",
          getattr(S, "DRIFT_RETRAIN_TRIGGER_HORIZON", None) in HORIZONS)


def test_p1_trigger_horizon_matches_judgment():
    """판정에 쓰는 호라이즌과 교체 스코프가 같은지 — 어긋나면 처방이 빗나간다."""
    src = _read("main.py")
    # main.py가 DriftRetrain 판정에 쓰는 호라이즌 (horizon_accuracy("...") 호출)
    m = re.search(r'_dr_acc5m\s*=\s*self\.online_learner\.horizon_accuracy\(\s*"([^"]+)"\s*\)', src)
    check("DriftRetrain 판정 호라이즌 추출 성공", m is not None)
    if m:
        check("판정 호라이즌 == DRIFT_RETRAIN_TRIGGER_HORIZON (%s)" % m.group(1),
              m.group(1) == getattr(S, "DRIFT_RETRAIN_TRIGGER_HORIZON", None))


def test_p1_scope_conditions():
    """스코프 축소 조건 4개(drift · not warmup · not weekly · not monthly)가 모두 있어야."""
    src = _read("main.py")
    i = src.index("_rt_scope = None")
    blk = src[i:i + 900]
    check("킬스위치 게이트 존재", 'DRIFT_RETRAIN_SCOPE_LIMIT' in blk)
    check("조건: _drift_trigger", "and _drift_trigger" in blk)
    check("조건: not _warmup_forced", "not _warmup_forced" in blk)
    check("조건: not _weekly_needed", "not _weekly_needed" in blk)
    check("조건: not _monthly_needed", "not _monthly_needed" in blk)
    check("horizons= 인자로 전달", "horizons=_rt_scope" in blk)
    check("기본값 None(=ALL) — 다른 트리거는 종전 동작",
          blk.startswith("_rt_scope = None"))


def test_p1_monthly_evaluated_once():
    """분 경계 레이스 방지 — should_retrain_monthly()는 한 번만 호출한다."""
    src = _read("main.py")
    i = src.index("_monthly_needed = self.batch_retrainer.should_retrain_monthly()")
    blk = src[i:i + 1400]
    check("should_retrain_monthly 재호출 없음 (스코프 판정 구간)",
          blk.count("should_retrain_monthly()") == 1)


def test_p1_scope_logic_simulation():
    """조건 조합별 스코프 산출을 순수 함수로 재현 — 진리표 검증."""
    def scope(limit, drift, warmup, weekly, monthly, hz="5m"):
        if limit and drift and not warmup and not weekly and not monthly:
            return [hz]
        return None
    check("Drift 단독 → ['5m']",
          scope(True, True, False, False, False) == ["5m"])
    check("Drift + Warmup → ALL",
          scope(True, True, True, False, False) is None)
    check("Drift + weekly → ALL",
          scope(True, True, False, True, False) is None)
    check("Drift + monthly → ALL",
          scope(True, True, False, False, True) is None)
    check("Warmup 단독 → ALL",
          scope(True, False, True, False, False) is None)
    check("킬스위치 OFF → 항상 ALL (종전 동작)",
          scope(False, True, False, False, False) is None)


# ══════════════════════════════════════════════════════════════════
# P5 — BiasReset 냉각 해제 스코프 한정
# ══════════════════════════════════════════════════════════════════
def test_p5_settings_and_wiring():
    check("BIAS_RESET_CLEAR_SCOPED 등록 + 기본 True",
          getattr(S, "BIAS_RESET_CLEAR_SCOPED", None) is True)
    src = _read("main.py")
    check("_retrain_subproc_scope __init__ 초기화",
          "self._retrain_subproc_scope: list = []" in src)
    check("_start_gbm_retrain_subprocess가 스코프 보관",
          "self._retrain_subproc_scope       = list(horizons or [])" in src)
    check("set.difference_update 사용 (clear() 아님)",
          "self._bias_override_horizons.difference_update(_bias_scope)" in src)
    # 재학습 완료 콜백 **구간 안에만** 무조건 clear()가 없어야 한다.
    # 일일 리셋(reset_daily)의 clear()는 정당하다 — 하루가 끝나면 전 호라이즌의
    # 편향 판정이 무효이므로 그쪽까지 스코프화하면 오히려 상태가 새 날로 샌다.
    i = src.index("_bias_scope = [")
    cb = src[i - 1500:i + 1500]
    check("재학습 콜백 구간에 무조건 clear() 없음",
          "self._bias_override_horizons.clear()" not in cb)
    check("일일 리셋 경로의 clear()는 보존 (전 호라이즌 초기화가 정당)",
          "self._bias_override_horizons.clear()" in src)


def test_p5_scope_semantics():
    """스코프 해석을 순수 함수로 재현 — ALL 폴백이 종전과 동일한지."""
    def resolve(raw_scope, flag, horizons=tuple(HORIZONS)):
        s = [h for h in (raw_scope or []) if h in horizons]
        if not (s and flag):
            s = list(horizons)
        return s
    check("스코프 ['5m'] + 플래그 ON → ['5m']",
          resolve(["5m"], True) == ["5m"])
    check("스코프 없음(ALL 교체) → 전 호라이즌 (종전 동작)",
          resolve([], True) == list(HORIZONS))
    check("스코프 None → 전 호라이즌",
          resolve(None, True) == list(HORIZONS))
    check("킬스위치 OFF → 전 호라이즌 (종전 동작)",
          resolve(["5m"], False) == list(HORIZONS))
    check("미등록 호라이즌만 담긴 스코프 → 전 호라이즌 (안전 폴백)",
          resolve(["99m"], True) == list(HORIZONS))
    check("혼합 스코프에서 유효분만 남음",
          resolve(["5m", "99m"], True) == ["5m"])


def test_p5_state_mutation_equivalence():
    """스코프==전체일 때 상태 변화가 종전(clear + 재할당)과 완전히 같은지."""
    horizons = list(HORIZONS)
    # 종전 동작
    old_over = set(["3m", "10m"])
    old_streak = {h: 7 for h in horizons}
    old_timer = {h: 5 for h in horizons}
    old_over.clear()
    old_streak = {h: 0 for h in horizons}
    old_timer = {h: 0 for h in horizons}
    # 신규 동작 (스코프=전체)
    new_over = set(["3m", "10m"])
    new_streak = {h: 7 for h in horizons}
    new_timer = {h: 5 for h in horizons}
    new_over.difference_update(horizons)
    for h in horizons:
        new_streak[h] = 0
        new_timer[h] = 0
    check("override set 동일", old_over == new_over)
    check("fl_streak 동일", old_streak == new_streak)
    check("override_timer 동일", old_timer == new_timer)

    # 스코프=['5m'] 이면 나머지 호라이즌 냉각이 보존되어야 한다
    p_over = set(["3m", "5m"])
    p_timer = {h: 5 for h in horizons}
    p_over.difference_update(["5m"])
    p_timer["5m"] = 0
    check("부분 스코프: 5m만 해제", "5m" not in p_over)
    check("부분 스코프: 3m 냉각 보존", "3m" in p_over)
    check("부분 스코프: 3m 타이머 보존", p_timer["3m"] == 5)


# ══════════════════════════════════════════════════════════════════
# P4 — tp1_reached 관측 컬럼
# ══════════════════════════════════════════════════════════════════
def test_p4_exit_reason_labels_unchanged():
    """라벨을 바꾸면 사전등록 채널 판정이 조용히 뒤집힌다 — 절대 불변."""
    src = _read("main.py")
    check('exit_reason "하드스톱(틱)" 유지', 'reason="하드스톱(틱)"' in src)
    check('exit_reason "하드스톱" 유지', 'reason="하드스톱"' in src)
    for tok in ("보호트레일", "보호스톱"):
        check('exit_reason에 신규 라벨 "%s" 도입 안 함' % tok,
              ('reason="%s"' % tok) not in src)


def test_p4_migration_and_result_field():
    dbu = _read("utils/db_utils.py")
    check("trades 마이그레이션에 tp1_reached 등록",
          '"tp1_reached": "INTEGER"' in dbu)
    check("소급 백필 안 함 (추정치 혼입 금지)",
          "UPDATE trades SET tp1_reached" not in dbu)
    pt = _read("strategy/position/position_tracker.py")
    check("_build_exit_result가 tp1_reached 제공",
          '"tp1_reached": 1 if self.partial_1_done else 0,' in pt)


def test_p4_insert_arity():
    """컬럼수 == 플레이스홀더수 == 값 튜플 길이. 하나만 어긋나도 청산 기록이 통째로 실패한다."""
    src = _read("main.py")
    i = src.index("INSERT INTO trades")
    blk = src[i:i + 1200]
    cols = blk[blk.index("(") + 1:blk.index(")")]
    names = [c.strip() for c in cols.replace("\n", " ").split(",") if c.strip()]
    vp = blk.index("VALUES")
    n_q = blk[vp:blk.index('"""', vp)].count("?")

    tup_len = None
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "execute":
            for a in node.args:
                v = getattr(a, "value", getattr(a, "s", None))
                if isinstance(v, str) and "INSERT INTO trades" in v:
                    if len(node.args) >= 3 and isinstance(node.args[2], ast.Tuple):
                        tup_len = len(node.args[2].elts)

    check("컬럼수(%d) == 플레이스홀더수(%d)" % (len(names), n_q), len(names) == n_q)
    check("값 튜플 길이(%s) == 컬럼수(%d)" % (tup_len, len(names)), tup_len == len(names))
    # [468차 G-3 정정] 원 단정은 `names[-1] == "tp1_reached"`(맨 끝)였다. 그건 **컬럼이
    # 하나라도 추가되면 깨지는** 형태이고, 실제로 468차가 exit_trigger/exit_outcome을
    # 뒤에 붙이자 깨졌다. 지키려는 불변식은 "위치"가 아니라 **"컬럼 목록에 있고 값 튜플과
    # 자릿수가 맞는다"**이며 그것은 바로 위 두 단정이 이미 보장한다.
    check("tp1_reached가 컬럼 목록에 있다", "tp1_reached" in names)
    check("값 누락 시 0이 아니라 NULL",
          'if result.get("tp1_reached") is not None else None' in src)


# [MW0602 468차] P4 배선이 라이브에 처음 반영된 거래일. 이 날짜 **이전** 청산 행은
# tp1_reached가 NULL이어야 한다(소급 백필 금지 — 추정치를 실측 컬럼에 섞지 않는다는
# 465차 결정). 이 날짜 이후 행은 반대로 채워져 있어야 배선이 살아 있는 것이다.
P4_LIVE_SINCE = "2026-08-13"


def test_p4_live_db_column():
    """마이그레이션이 실제 DB에 반영됐는지 (있을 때만 검사)."""
    import sqlite3
    p = os.path.join(BASE, "data", "db", "trades.db")
    if not os.path.exists(p):
        print("[SKIP] trades.db 없음")
        return
    conn = sqlite3.connect(p)
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(trades)")]
        check("라이브 trades.tp1_reached 존재", "tp1_reached" in cols)
        if "tp1_reached" in cols:
            # [MW0602 468차 정정] 원 단정은 `count(*) where tp1_reached is not null == 0`
            # 이었다. 그건 **배선이 동작하는 순간 반드시 깨진다** — 465차 배포 다음
            # 거래일(2026-08-13)에 라이브가 6행을 채우자 그대로 실패했다.
            # 지키려던 불변식은 "백필을 하지 않는다"이지 "아무도 안 채운다"가 아니다.
            # → **배포 이전 청산 행만** NULL이어야 한다로 정확히 다시 쓴다.
            n_old_filled = conn.execute(
                "select count(*) from trades "
                "where tp1_reached is not null and exit_ts < ?", (P4_LIVE_SINCE,)
            ).fetchone()[0]
            check("구버전 행은 NULL 유지 (백필 없음)", n_old_filled == 0)
            # 배선이 살아 있는지도 함께 본다 — 위 단정만 남기면 "컬럼만 있고 아무도
            # 안 쓰는 상태"가 영구히 통과한다(292·303차가 반복한 실패 형태).
            n_new_filled = conn.execute(
                "select count(*) from trades "
                "where tp1_reached is not null and exit_ts >= ?", (P4_LIVE_SINCE,)
            ).fetchone()[0]
            n_new_rows = conn.execute(
                "select count(*) from trades where exit_ts >= ?", (P4_LIVE_SINCE,)
            ).fetchone()[0]
            if n_new_rows:
                check("배포 이후 행은 실제로 채워진다 (%d/%d)" % (n_new_filled, n_new_rows),
                      n_new_filled > 0)
            else:
                print("[SKIP] 배포 이후 청산 행 없음 — 배선 확인 보류")
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════
# P6-b — MDD 분모 표기
# ══════════════════════════════════════════════════════════════════
def test_p6b_mdd_label():
    reg = _read("config/strategy_registry.py")
    check("get_rolling_metrics가 mdd_krw 반환", '"mdd_krw":' in reg)
    check("mdd_pct 계산식 무변경 (WFA 합격선 보호)",
          "mdd_pct = mdd_krw / abs(peak) if abs(peak) > 0 else 0.0" in reg)
    exp = _read("strategy/ops/daily_exporter.py")
    # [MW0602 475차 후속] 배너를 **자본 대비 우선 + peak 대비 병기**로 바꿨다.
    # 461차가 "판정·리포트 배너·대시보드는 mdd_pct_of_capital 만 쓴다"고 정했는데
    # 이 배너만 peak 대비 단독이었다(0818 실측 143.3% vs 자본대비 2.89%).
    # 검사 취지는 그대로다 — **분모를 반드시 라벨에 박는다.**
    check("자본 대비 표기(461차 규약)", "%.2f%%(자본대비)" in exp)
    check("peak 대비 병기 유지(계측 4원칙 ③ 탈락 가시화)", "peak대비 %.1f%%" in exp)
    check("분모 정의를 복제하지 않고 registry 단일 헬퍼 사용",
          "_live_mdd_vs_capital" in exp)
    check("자본 미상 시 0 으로 쓰지 않는다(계측 4원칙 ②)", "자본미상" in exp)
    check("원화 포맷은 str.format 사용 ('%,.0f'는 Python에서 ValueError)",
          "{:,.0f}원\".format(" in exp)
    check("printf 스타일 천단위 구분자 미사용",
          "%,.0f" not in exp)


if __name__ == "__main__":
    for fn in sorted(
        [v for k, v in list(globals().items()) if k.startswith("test_")],
        key=lambda f: f.__code__.co_firstlineno,
    ):
        print("\n── %s" % fn.__name__)
        fn()
    print("\n" + "=" * 60)
    if FAILURES:
        print("실패 %d건:" % len(FAILURES))
        for f in FAILURES:
            print("  - %s" % f)
        sys.exit(1)
    print("465차 회귀 테스트 전부 통과")
