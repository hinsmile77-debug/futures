"""[MW0602 439차] [35] 유령 하드스톱 채널의 **미러 서브표본** 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
무엇이 고장나 있었나
────────────────────────────────────────────────────────────────────────────
[35] 주판정의 대상은 "유령 청산이 실제로 난 건"이다:

    would_suppress=1  AND  live_suppressed=0  AND  exited=1

`live_suppressed=0`은 "423차 라이브 가드가 못 막은 경로" — 실질적으로 qty>=2의
TP1 손익분기 이동(main.py `tp1_breakeven`)뿐이었다. 그런데 431차가
MAX_CONTRACTS를 10→3으로 내리고 게이트 체인을 재구성하면서 **qty>=2 진입 자체가
사라졌다.** 그 결과 2026-08-05 계측 시작 이후 적재된 행은 전부
`arm_tp1_qty1_mode`(가드가 정상 배선된 경로)라 `live_suppressed=1`이고,
주판정 필터를 통과하는 행이 **영구히 0건**이다.

리포트는 이걸 🔴 NO-DATA("계측 시작일이 지났는데 0건 — 배선 확인 필요")로 띄웠다.
배선은 멀쩡한데 배선을 의심하게 만드는 오경보였고, 357차가 막으려던 "빨간불을
무시하는 습관"을 정확히 되살리는 실패 방식이다.

────────────────────────────────────────────────────────────────────────────
439차가 검증하는 불변식
────────────────────────────────────────────────────────────────────────────
    (1) 적재는 되는데 주판정 모집단이 0  → `structural_block`, `no_data`는 **끄기**
    (2) 적재 자체가 0                    → 기존대로 `no_data`(🔴) **유지**
    (3) 미러 Δ의 부호 규약이 주판정과 같다 ((+)=유령 유리)
    (4) 미러는 `live_suppressed=1`만 담는다 (주판정 모집단과 교집합 없음)
    (5) 평균·중앙값 부호가 갈리면 `mean_median_split` 플래그가 선다 (313차)
    (6) 미러는 verdict를 만들지 않는다 — 합격선 신설 금지(사후 기준 이동 방지)

(1)이 깨지면 오경보가 돌아온다. (6)이 깨지면 313차 위반이다.
"""

import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MIREUK_TEST_MODE"] = "1"  # [422차] 프로덕션 로그·Slack 오염 차단

from scripts.generate_validation_campaign_report import (  # noqa: E402
    _phantom_mirror_subsample, eval_phantom_stop_edge,
)

FAILURES = []
EFF = "2026-08-05 00:00:00"


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


def _mkdb(shadow_rows, trade_rows):
    """임시 trades.db — 실거래 DB를 건드리지 않는다.

    [feedback_isolate_stateful_verification] 검증 스크립트가 실거래 앱과 파일을
    공유해 진입가를 오염시킨 사고가 있었다. 여기서는 tempfile로 완전 격리한다.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    c = sqlite3.connect(path)
    c.execute("""CREATE TABLE phantom_stop_shadow (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, entry_ts TEXT,
        direction TEXT, quantity INTEGER, entry_price REAL, stop_eval REAL,
        stop_current REAL, bar_start TEXT, bar_high REAL, bar_low REAL,
        cur_price REAL, close_hit INTEGER, live_suppressed INTEGER,
        would_suppress INTEGER, tighten_path TEXT, stop_updated_at TEXT,
        shadow_tightened_at TEXT, exited INTEGER, created_at TEXT)""")
    c.execute("""CREATE TABLE trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT, entry_ts TEXT, exit_ts TEXT,
        pnl_pts REAL, quantity INTEGER)""")
    c.executemany(
        "INSERT INTO phantom_stop_shadow (ts, entry_ts, direction, quantity, "
        "entry_price, stop_eval, cur_price, live_suppressed, would_suppress, "
        "tighten_path, exited) VALUES (?,?,?,?,?,?,?,?,?,?,?)", shadow_rows)
    c.executemany(
        "INSERT INTO trades (entry_ts, exit_ts, pnl_pts, quantity) "
        "VALUES (?,?,?,?)", trade_rows)
    c.commit()
    c.row_factory = sqlite3.Row
    return c, path


def test_mirror_sign_matches_primary():
    """(3) SHORT에서 cur_price가 진입가보다 낮으면 유령 청산은 이익 → Δ 부호 확인.

    진입 1000.0 / cur 998.0 → 유령 +2.0pt.  버틴 실제 +0.5pt.
    Δ = 유령 − 버팀 = +1.5  →  (+)면 유령 유리 (주판정과 동일 규약).
    """
    c, p = _mkdb(
        [("2026-08-05 10:00:00", "2026-08-05 09:58:00", "SHORT", 1,
          1000.0, 999.0, 998.0, 1, 1, "arm_tp1_qty1_mode", 0)],
        [("2026-08-05 09:58:00", "2026-08-05 10:05:00", 0.5, 1)])
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(3) 미러 n=1", m.get("n") == 1)
        check("(3) 유령 +2.0pt", abs(m["ghost_pt_sum"] - 2.0) < 1e-6)
        check("(3) 버팀 +0.5pt", abs(m["held_pt_sum"] - 0.5) < 1e-6)
        check("(3) Δ=+1.5 — (+)면 유령 유리", abs(m["delta_pt_sum"] - 1.5) < 1e-6)
        check("(3) 유령 손익 양수 카운트=1", m.get("ghost_positive_n") == 1)
    finally:
        c.close(); os.unlink(p)


def test_mirror_long_direction():
    """(3') LONG은 부호가 뒤집힌다 — 진입 1000 / cur 1002 → 유령 +2.0pt."""
    c, p = _mkdb(
        [("2026-08-05 10:00:00", "2026-08-05 09:58:00", "LONG", 1,
          1000.0, 1001.0, 1002.0, 1, 1, "arm_tp1_qty1_mode", 0)],
        [("2026-08-05 09:58:00", "2026-08-05 10:05:00", 3.0, 1)])
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(3') LONG 유령 +2.0pt", abs(m["ghost_pt_sum"] - 2.0) < 1e-6)
        check("(3') Δ=-1.0 — 버팀 우세", abs(m["delta_pt_sum"] + 1.0) < 1e-6)
    finally:
        c.close(); os.unlink(p)


def test_mirror_excludes_primary_population():
    """(4) `live_suppressed=0` 행은 미러에 들어가면 안 된다 — 이중계상 방지."""
    c, p = _mkdb(
        [("2026-08-05 10:00:00", "2026-08-05 09:58:00", "SHORT", 1,
          1000.0, 999.0, 998.0, 1, 1, "arm_tp1_qty1_mode", 0),
         ("2026-08-05 11:00:00", "2026-08-05 10:58:00", "SHORT", 2,
          1000.0, 999.0, 998.0, 0, 1, "tp1_breakeven_qty2", 1),   # 주판정 모집단
         ("2026-08-05 12:00:00", "2026-08-05 11:58:00", "SHORT", 1,
          1000.0, 999.0, 998.0, 1, 0, "arm_tp1_qty1_mode", 0)],   # would_suppress=0
        [("2026-08-05 09:58:00", "2026-08-05 10:05:00", 0.5, 1),
         ("2026-08-05 10:58:00", "2026-08-05 11:05:00", 0.5, 2),
         ("2026-08-05 11:58:00", "2026-08-05 12:05:00", 0.5, 1)])
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(4) 미러는 억제행 1건만 (주판정·would_suppress=0 제외)", m.get("n") == 1)
        check("(4) 적재 총행은 3으로 보고", m.get("n_rows_total") == 3)
    finally:
        c.close(); os.unlink(p)


def test_multi_leg_counted():
    """(4') 억제 후 TP1 부분청산→TP2로 쪼개지면 레그 합산 + 다중레그 카운트."""
    c, p = _mkdb(
        [("2026-08-05 10:00:00", "2026-08-05 09:58:00", "SHORT", 2,
          1000.0, 999.0, 998.0, 1, 1, "arm_tp1_qty1_mode", 0)],
        [("2026-08-05 09:58:00", "2026-08-05 10:05:00", 1.0, 1),
         ("2026-08-05 09:58:00", "2026-08-05 10:09:00", 4.0, 1)])
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(4') 레그 합산 +5.0pt", abs(m["held_pt_sum"] - 5.0) < 1e-6)
        check("(4') 다중레그 1건으로 노출", m.get("n_multi_leg") == 1)
    finally:
        c.close(); os.unlink(p)


def test_pre_judgement_legs_excluded():
    """(4'') 판정 **이전**에 이미 닫힌 레그는 억제 결과가 아니다 — 제외돼야 한다."""
    c, p = _mkdb(
        [("2026-08-05 10:00:00", "2026-08-05 09:58:00", "SHORT", 2,
          1000.0, 999.0, 998.0, 1, 1, "arm_tp1_qty1_mode", 0)],
        [("2026-08-05 09:58:00", "2026-08-05 09:59:00", 9.9, 1),   # 판정 전 — 제외
         ("2026-08-05 09:58:00", "2026-08-05 10:05:00", 1.0, 1)])
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(4'') 판정 이전 레그 제외 → 버팀 +1.0pt",
              abs(m["held_pt_sum"] - 1.0) < 1e-6)
    finally:
        c.close(); os.unlink(p)


def test_mean_median_split_flag():
    """(5) 평균은 음수인데 중앙값은 양수 → 소수 관측이 끌고 있다는 플래그."""
    # Δ: +1, +1, +1, -9  → 평균 -1.5 / 중앙값 +1.0
    rows, trades = [], []
    for i, (ghost_gap, held) in enumerate(
            [(1.0, 0.0), (1.0, 0.0), (1.0, 0.0), (1.0, 10.0)]):
        ets = "2026-08-05 09:%02d:00" % (10 + i)
        ts = "2026-08-05 10:%02d:00" % (10 + i)
        rows.append((ts, ets, "SHORT", 1, 1000.0, 999.5, 1000.0 - ghost_gap,
                     1, 1, "arm_tp1_qty1_mode", 0))
        trades.append((ets, "2026-08-05 11:00:00", held, 1))
    c, p = _mkdb(rows, trades)
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(5) 평균 음수", m["delta_pt_avg"] < 0)
        check("(5) 중앙값 양수", m["delta_pt_median"] > 0)
        check("(5) mean_median_split 플래그 True", m.get("mean_median_split") is True)
    finally:
        c.close(); os.unlink(p)


def test_no_mirror_no_flag():
    """(5') 부호가 일치하면 플래그가 서면 안 된다 — 상시 경보 방지."""
    rows, trades = [], []
    for i in range(3):
        ets = "2026-08-05 09:%02d:00" % (10 + i)
        rows.append(("2026-08-05 10:%02d:00" % (10 + i), ets, "SHORT", 1,
                     1000.0, 999.5, 998.0, 1, 1, "arm_tp1_qty1_mode", 0))
        trades.append((ets, "2026-08-05 11:00:00", 0.5, 1))
    c, p = _mkdb(rows, trades)
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(5') 부호 일치 시 플래그 False",
              m.get("mean_median_split") is False)
    finally:
        c.close(); os.unlink(p)


def test_mirror_emits_no_verdict():
    """(6) 미러는 verdict/합격선을 만들지 않는다 — 사후 기준 이동 금지(313차)."""
    c, p = _mkdb(
        [("2026-08-05 10:00:00", "2026-08-05 09:58:00", "SHORT", 1,
          1000.0, 999.0, 998.0, 1, 1, "arm_tp1_qty1_mode", 0)],
        [("2026-08-05 09:58:00", "2026-08-05 10:05:00", 0.5, 1)])
    try:
        m = _phantom_mirror_subsample(c, EFF, 0.05)
        check("(6) 미러에 verdict 키 없음", "verdict" not in m)
        check("(6) 미러에 recommendation 키 없음", "recommendation" not in m)
    finally:
        c.close(); os.unlink(p)


def test_live_channel_structural_not_nodata():
    """(1)(2) 실 DB — 적재는 있고 주판정 0건이므로 구조적판정불가, 빨간불 금지."""
    out = eval_phantom_stop_edge()
    if out.get("error"):
        check("(1) 실 DB 조회 실패 — 스킵: %s" % out["error"], True)
        return
    mir = out.get("mirror") or {}
    if mir.get("n"):
        check("(1) 주판정 0건 + 미러 존재 → structural_block",
              out.get("structural_block") is True)
        check("(1) 🔴 no_data 는 꺼져 있어야 한다", not out.get("no_data"))
        check("(1) 판정 어휘는 INSUFFICIENT 유지(합격선 무변경)",
              out.get("verdict") == "INSUFFICIENT")
        check("(1) structural_reason 문구 존재",
              bool(out.get("structural_reason")))
    else:
        # 미러도 0이면 (2) 경로 — 적재 자체가 없다는 뜻이라 빨간불이 맞다.
        check("(2) 미러도 0건이면 no_data 유지", bool(out.get("no_data")))


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 439차] [35] 유령 하드스톱 미러 서브표본 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_mirror_sign_matches_primary,
        test_mirror_long_direction,
        test_mirror_excludes_primary_population,
        test_multi_leg_counted,
        test_pre_judgement_legs_excluded,
        test_mean_median_split_flag,
        test_no_mirror_no_flag,
        test_mirror_emits_no_verdict,
        test_live_channel_structural_not_nodata,
    ):
        print("\n-- %s" % fn.__name__)
        fn()
    print("\n" + "=" * 72)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
