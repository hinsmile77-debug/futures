"""[MW0601 453차 / QDQ Phase 2] CVD 앵커 대조 리포트 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
이 리포트가 답하는 단 하나의 질문
────────────────────────────────────────────────────────────────────────────
    anchor_buy_share가 0.50 근방인가, 0.63 근방인가?
      0.50 근방 → 발견 A(체결구분 파싱 결함) 라이브 확정 → Phase 3 착수 가능
      0.63 근방 → 매수 편향이 시장 실체 → 진단이 틀렸다 → Phase 3 취소

그래서 이 테스트의 절반은 **판정 분기**를 잠근다. 나머지 절반은 "못 재는데 잰 척"을
막는다 — 계측 0행에서 0%를 계산해 통과시키면 toxicity_block_shadow가 자기모순
조건으로 3개월간 0건인 채 방치된 402차 후속3과 같은 사고가 된다.

  R1 계측 0행 → ⏳ 판정 + 종료코드 0 (조용한 0% 통과 금지)
  R2 발견 A 재현(legacy 63% / anchor 50%) → ✅ 확정
  R3 반증(둘 다 63%) → ❌ Phase 3 취소
  R4 ①-순 vs ①-절대 — 상쇄 케이스에서 순=0, 절대>0  ← anchor_diff 취지
  R5 I1 위반율 초과 → ⚠ 앵커 신뢰 불가 (비중 판정보다 우선)
  R6 I2 음수 잔차(이중 집계) 검출
  R7 I3 위반을 452차 이전/이후로 분리 (오진 방지)
  R8 md/json 산출 + FIFO stem 분리
  R9 섀도-앵커 괴리가 크면 ✅ 안에서 "앵커 직접 사용" 경고

실행: python tests/test_453_cvd_anchor_report.py   (COM/브로커 불필요)
"""

import json
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import scripts.generate_cvd_anchor_report as R  # noqa: E402

FAILURES = []


def check(name, cond):
    print("[%s] %s" % ("OK" if cond else "FAIL", name))
    if not cond:
        FAILURES.append(name)


# ── 픽스처 ──────────────────────────────────────────────────────────────────

_COLS = ("ts", "volume", "buy_vol", "sell_vol", "anchor_buy", "anchor_sell",
         "buy_vol_flag", "sell_vol_flag", "bar_recovered")


def _make_db(rows):
    """raw_candles만 있는 임시 DB. rows = _COLS 순서의 튜플 리스트."""
    tmp = tempfile.mkdtemp(prefix="qdq_p2_")
    path = os.path.join(tmp, "raw_data.db")
    con = sqlite3.connect(path)
    con.execute("""
        CREATE TABLE raw_candles (
            ts TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL,
            volume INTEGER, bid1 REAL, ask1 REAL, oi INTEGER,
            buy_vol INTEGER, sell_vol INTEGER,
            anchor_buy INTEGER, anchor_sell INTEGER,
            buy_vol_flag INTEGER, sell_vol_flag INTEGER,
            bar_recovered INTEGER, created_at TEXT)""")
    con.executemany(
        "INSERT INTO raw_candles (%s) VALUES (%s)"
        % (",".join(_COLS), ",".join("?" * len(_COLS))), rows)
    con.commit(); con.close()
    return path


def _bars(n, vol, legacy_buy, anchor_buy, flag_buy=None, day="2026-08-10",
          recovered=0):
    """n개 봉을 같은 값으로. flag_buy 생략 시 anchor와 동일(정상 섀도)."""
    fb = anchor_buy if flag_buy is None else flag_buy
    return [("%s 09:%02d:00" % (day, i), vol,
             legacy_buy, vol - legacy_buy,
             anchor_buy, vol - anchor_buy,
             fb, vol - fb, recovered) for i in range(n)]


def _run(rows, days=5):
    """임시 DB로 build_report 실행 → metrics 반환."""
    path = _make_db(rows) if rows else _make_db(
        [("2026-08-10 09:00:00", 0, 0, 0, None, None, None, None, 0)])
    orig = R.RAW_DB
    try:
        R.RAW_DB = path
        _md, metrics = R.build_report(days)
        return metrics
    finally:
        R.RAW_DB = orig


# ── R1 ──────────────────────────────────────────────────────────────────────

def test_r1_no_data_is_reported_not_passed():
    # 앵커·섀도 전부 NULL (Phase 0 배포 직후 = 현재 실제 상태)
    rows = [("2026-08-10 09:%02d:00" % i, 100, 63, 37, None, None, None, None, 0)
            for i in range(400)]
    m = _run(rows)
    check("R1: 판정 = 계측 미개시", m["verdict"] == R.V_NO_DATA)
    check("R1: 앵커 계측 0봉", m["coverage"]["anchor_bars"] == 0)
    check("R1: 앵커 비중 None (0.0으로 뭉개지 않음)",
          m["shares"]["anchor"] is None)
    check("R1: legacy는 계산됨(63%)", abs(m["shares"]["legacy"] - 0.63) < 1e-9)
    check("R1: 사유에 UNAVAIL 로그 안내 포함", "UNAVAIL" in m["reason"] + m["next_action"])

    # 계측은 됐지만 MIN_BARS 미달
    rows2 = _bars(10, 100, 63, 50)
    m2 = _run(rows2)
    check("R1b: MIN_BARS 미달 → 계측 부족 판정", m2["verdict"] == R.V_NO_DATA)
    check("R1b: 사유에 최소치 명시", str(R.MIN_BARS) in m2["reason"])


# ── R2 · R3 · R9 — 판정 분기 ────────────────────────────────────────────────

def test_r2_finding_a_confirmed():
    """발견 A 재현: legacy 63% / 앵커 50% / 섀도는 앵커와 일치."""
    m = _run(_bars(400, 100, legacy_buy=63, anchor_buy=50))
    check("R2: 판정 = 발견 A 확정", m["verdict"] == R.V_CONFIRMED)
    check("R2: 앵커 비중 50%", abs(m["shares"]["anchor"] - 0.50) < 1e-9)
    check("R2: 섀도 비중 50% (앵커와 일치)",
          abs(m["shares"]["shadow"] - 0.50) < 1e-9)
    check("R2: legacy vs 앵커 절대괴리 13% (=63-50)",
          abs(m["axis_legacy_vs_anchor"]["mag_abs"] - 0.13) < 1e-9)
    check("R2: 섀도 vs 앵커 절대괴리 0",
          m["axis_shadow_vs_anchor"]["mag_abs"] == 0.0)
    check("R2: 다음 조치에 정규화 포화 동시 수정 경고",
          "cvd.py:104" in m["next_action"])
    check("R2: 다음 조치에 백필 불가 명시", "백필 불가" in m["next_action"])


def test_r3_refuted_cancels_phase3():
    """반증: 앵커도 63% — 편향이 시장 실체."""
    m = _run(_bars(400, 100, legacy_buy=63, anchor_buy=63))
    check("R3: 판정 = 진단 오류", m["verdict"] == R.V_REFUTED)
    check("R3: 다음 조치에 Phase 3 취소", "취소" in m["next_action"])
    check("R3: DECISION_LOG 정정 지시", "DECISION_LOG" in m["next_action"])


def test_r3b_ambiguous():
    """중간값(57%) — 균형도 편향도 아니다."""
    m = _run(_bars(400, 100, legacy_buy=63, anchor_buy=57))
    check("R3b: 판정 = 애매", m["verdict"] == R.V_AMBIGUOUS)


def test_r9_shadow_mismatch_warns_inside_confirmed():
    """앵커는 50%인데 섀도가 58% — 체결구분 분류 자체의 한계."""
    m = _run(_bars(400, 100, legacy_buy=63, anchor_buy=50, flag_buy=58))
    check("R9: 여전히 발견 A 확정", m["verdict"] == R.V_CONFIRMED)
    check("R9: 섀도 괴리 8% > 허용 2%",
          m["axis_shadow_vs_anchor"]["mag_abs"] > R.SHADOW_MATCH_MAX)
    check("R9: 사유에 '앵커 직접 사용' 재설계 경고",
          "앵커 직접 사용" in m["reason"])


# ── R4 — anchor_diff (순 vs 절대) ──────────────────────────────────────────

def test_r4_net_vs_abs_magnitude():
    """오전 +10 / 오후 −10 상쇄 — 순은 0, 절대는 10%."""
    rows = []
    for i in range(200):      # 자체가 앵커보다 10 많음
        rows.append(("2026-08-10 09:%02d:00" % i, 100, 60, 40, 50, 50, 50, 50, 0))
    for i in range(200):      # 자체가 앵커보다 10 적음
        rows.append(("2026-08-10 13:%02d:00" % i, 100, 40, 60, 50, 50, 50, 50, 0))
    m = _run(rows)
    ax = m["axis_legacy_vs_anchor"]
    check("R4: ①-순 = 0 (봉끼리 상쇄)", abs(ax["mag_net"]) < 1e-12)
    check("R4: ①-절대 = 10% (상쇄 없음)", abs(ax["mag_abs"] - 0.10) < 1e-9)
    check("R4: 부호편향 0.5 (절반은 과대, 절반은 과소)",
          abs(ax["sign_bias"] - 0.5) < 1e-9)
    check("R4: 집중도 100% (전 봉 불일치)", abs(ax["concentration"] - 1.0) < 1e-9)
    # 앵커 비중은 정확히 50% → 확정 판정. 단 legacy도 50%라 BIASED_MIN 미달 → 애매
    check("R4: legacy 50%라 확정 아님(애매)", m["verdict"] == R.V_AMBIGUOUS)


def test_r4b_concentration_detects_localized_damage():
    """오차가 소수 봉에만 몰린 경우 — 집중도가 낮게 나와야 한다."""
    rows = _bars(396, 100, legacy_buy=50, anchor_buy=50)
    # 4봉만 크게 틀림
    rows += [("2026-08-10 14:%02d:00" % i, 100, 100, 0, 50, 50, 50, 50, 0)
             for i in range(4)]
    m = _run(rows)
    ax = m["axis_legacy_vs_anchor"]
    check("R4b: 집중도 1% (4/400)", abs(ax["concentration"] - 0.01) < 1e-9)
    check("R4b: 부호편향 0.0 (전부 자체가 과대)", ax["sign_bias"] == 0.0)
    check("R4b: 최대 단일봉 괴리 50계약", ax["max_abs_bar"] == 50.0)


# ── R5 · R6 · R7 — 항등식 ──────────────────────────────────────────────────

def test_r5_identity_violation_blocks_verdict():
    """I1이 깨지면 비중 판정보다 먼저 '앵커 신뢰 불가'가 나와야 한다."""
    rows = _bars(300, 100, legacy_buy=63, anchor_buy=50)
    # 100봉에서 앵커 합이 거래량과 안 맞게 만든다 (위반율 25% > 1%)
    rows += [("2026-08-10 14:%02d:00" % i, 100, 63, 37, 30, 30, 50, 50, 0)
             for i in range(100)]
    m = _run(rows)
    check("R5: 판정 = 앵커 신뢰 불가", m["verdict"] == R.V_ANCHOR_BAD)
    check("R5: I1 위반 100봉", m["identities"]["i1_bad"] == 100)
    check("R5: 다음 조치에 필드 인덱스 재확인", "22" in m["next_action"])


def test_r6_negative_residual_is_double_counting():
    """섀도 합 > 거래량 → 미분류가 아니라 이중 집계 버그."""
    rows = _bars(400, 100, legacy_buy=63, anchor_buy=50, flag_buy=80)
    # flag_buy=80, sell=20 → 합 100 = volume. 이중 집계를 직접 주입한다.
    rows = [(r[0], r[1], r[2], r[3], r[4], r[5], 80, 40, r[8]) for r in rows]
    m = _run(rows)
    check("R6: I2 음수 잔차 봉 400개 검출",
          m["identities"]["i2_negative_bars"] == 400)


def test_r7_i3_split_by_era():
    """I3 위반을 452차 이전/이후로 나눠야 오진하지 않는다."""
    rows = _bars(300, 100, legacy_buy=63, anchor_buy=50)
    # 452차 이전 파괴 봉 (bar_recovered IS NULL) — 알려진 사안
    rows += [("2026-08-10 14:%02d:00" % i, 100, 0, 0, 50, 50, 50, 50, None)
             for i in range(10)]
    # 452차 이후 신규 위반 (bar_recovered=0) — 진짜 새 결함
    rows += [("2026-08-10 15:%02d:00" % i, 100, 0, 0, 50, 50, 50, 50, 0)
             for i in range(3)]
    m = _run(rows)
    idt = m["identities"]
    check("R7: I3 위반 총 13봉", idt["i3_bad"] == 13)
    check("R7: 452차 이전 10봉으로 분류", idt["i3_bad_legacy_era"] == 10)
    check("R7: 신규 3봉은 별도 (13-10)", idt["i3_bad"] - idt["i3_bad_legacy_era"] == 3)


def test_r7b_recovered_bars_flagged():
    """bar_recovered=1이 있으면 453차 D1 회귀 경고."""
    rows = _bars(400, 100, legacy_buy=63, anchor_buy=50, recovered=1)
    m = _run(rows)
    check("R7b: 복구 봉 400개 집계", m["coverage"]["recovered_bars"] == 400)


# ── R8 — 산출물 ────────────────────────────────────────────────────────────

def test_r8_outputs_and_fifo_stem_isolation():
    rows = _bars(400, 100, legacy_buy=63, anchor_buy=50)
    path = _make_db(rows)
    out = tempfile.mkdtemp(prefix="qdq_p2_out_")
    orig_db, orig_argv = R.RAW_DB, sys.argv
    try:
        R.RAW_DB = path
        sys.argv = ["x", "--days", "5", "--out-dir", out, "--no-prune"]
        rc = R.main()
    finally:
        R.RAW_DB, sys.argv = orig_db, orig_argv

    check("R8: 종료코드 0 (게이팅 없음)", rc == 0)
    names = sorted(os.listdir(out))
    check("R8: md + json 산출", len(names) == 2
          and any(n.endswith(".md") for n in names)
          and any(n.endswith(".json") for n in names))
    md = [n for n in names if n.endswith(".md")][0]
    check("R8: 파일명 규약 cvd_anchor_report_YYYYMMDD.md",
          md.startswith("cvd_anchor_report_") and len(md) == len("cvd_anchor_report_20260809.md"))
    with open(os.path.join(out, [n for n in names if n.endswith(".json")][0]),
              encoding="utf-8") as f:
        j = json.load(f)
    check("R8: json에 판정·임계 포함",
          j["verdict"] == R.V_CONFIRMED and j["thresholds"]["calibrated"] is False)

    # FIFO stem 분리 — 다른 계열 파일을 지우면 안 된다
    from scripts.campaign_report_paths import prune, _strict_re
    check("R8: strict 정규식이 cvd_anchor 계열만 매칭",
          bool(_strict_re("cvd_anchor").match("cvd_anchor_report_20260809.md"))
          and not _strict_re("cvd_anchor").match(
              "validation_campaign_report_20260809.md"))

    # 계열 힌트 등록 확인 (파일 부재 시 어느 스크립트를 돌릴지 안내)
    from scripts.campaign_report_paths import _GENERATOR_HINT
    check("R8: 생성기 힌트 등록",
          _GENERATOR_HINT.get("cvd_anchor") == "scripts/generate_cvd_anchor_report.py")


def test_r8b_registered_in_eod_chain():
    """EOD 주간 체인에 편입됐는지 — 리포트 뒤·재학습 앞."""
    import inspect
    from scripts import campaign_steps
    src = inspect.getsource(campaign_steps.run_campaign_steps)
    check("R8b: 체인에 등록", "generate_cvd_anchor_report.py" in src)
    check("R8b: 섀도우 TB 재학습보다 앞",
          src.index("generate_cvd_anchor_report.py")
          < src.index("run_shadow_triple_barrier_retrain.py"))


if __name__ == "__main__":
    _fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in _fns:
        try:
            fn()
        except Exception as e:
            FAILURES.append("%s: %r" % (fn.__name__, e))
            print("[FAIL] %s: %r" % (fn.__name__, e))
    print("-" * 60)
    if FAILURES:
        print("실패 %d건: %s" % (len(FAILURES), FAILURES))
        sys.exit(1)
    print("전부 통과")
