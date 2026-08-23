"""[MW0602 428차] A(방향 가치 대조) · B(청산 학습기) · C(정보원 트리거) 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
왜 이 세 개인가 — 0804가 도달한 결론
────────────────────────────────────────────────────────────────────────────
방향 축의 무력함이 네 갈래로 확인됐다:

  · 전 호라이즌 15거래일 적중률 33% 근방
  · [39] confidence 판별력 승/패 격차 -0.0008 (REJECTS_HYP)
  · [40] 무작위 대조 — 실제 -22.07pt vs 무작위 중앙 +4.88pt, p=0.790, 일자 8/16
  · 그런데 승률 63%, 캠페인 손익 양수

**돈이 방향에서 오지 않는다.** 그래서 세 갈래로 나눴다 —
A는 그 사실을 매주 재고, B는 돈이 실제로 나오는 축(청산)에 학습기를 놓고,
C는 새 정보원의 재검토 조건을 못 박는다.

────────────────────────────────────────────────────────────────────────────
지키려는 불변식
────────────────────────────────────────────────────────────────────────────
(A1) **시뮬레이터가 진입 봉을 포함하면 안 된다.** 진입 이전 구간의 고저가를
     쓰면 유령 청산이 된다(423차·425차가 라이브에서 겪은 바로 그 결함).
(A2) **두 팔이 같은 시뮬을 통과해야 한다.** 방향만 다르고 나머지가 같아야
     비교가 공정하다.
(A3) **재현 가능해야 한다.** seed 고정 — 매주 같은 난수열로 재계산한다.

(B1) **표본 미달이면 학습을 거부해야 한다.** 유효표본은 행이 아니라 **포지션**이다
     (포지션당 4.03행으로 강하게 상관). EPV 2.25는 기준 10의 1/5이다.
(B2) **거부 상태에서 DB를 오염시키면 안 된다.**
(B3) **학습이 열렸을 때 실제로 동작해야 한다** — 위음성 방지. 합성 데이터로 확인.
(B4) **GroupKFold를 써야 한다.** 같은 포지션의 행이 학습/검증에 갈리면 누출이다.
(B5) **라이브 청산에 배선되면 안 된다.**

(C1) 보류된 정보원 2종에 **재검토 트리거**가 등록돼 있어야 한다. 조건 없이
     열어두면 영원히 안 한다(CB②·FP-CRITICAL 전례).

실행: python tests/test_428_direction_value_and_exit_model.py   (COM/브로커 불필요)
"""
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


def _rec():
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    return importlib.import_module("random_entry_control")


def _rep():
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    return importlib.import_module("generate_validation_campaign_report")


# ══════════════ A — 무작위 진입 대조 ══════════════

def test_sim_excludes_entry_bar():
    """(A1) 진입 봉을 쓰면 안 된다 — 진입 이전 구간이 섞인다."""
    m = _rec()
    # 진입 봉(10:00)에 스톱을 관통하는 저가가 있지만 **진입 후** 봉은 평온하다.
    bars = {"2026-01-02": [
        ("2026-01-02 10:00:00", 100.5, 90.0, 100.0),   # 진입 봉 — 저가 90
        ("2026-01-02 10:01:00", 100.6, 99.9, 100.4),
        ("2026-01-02 10:02:00", 100.7, 99.8, 100.5),
    ]}
    v = m.simulate("2026-01-02 10:00:52", 100.0, 1, 2.0, bars)
    check("(A1) 진입 봉의 저가로 스톱이 터지지 않는다 (%.2f)" % v, v > -1.0)


def test_sim_arms_are_symmetric():
    """(A2) 방향만 뒤집으면 같은 봉에서 부호가 뒤집혀야 한다."""
    m = _rec()
    bars = {"2026-01-02": [
        ("2026-01-02 10:01:00", 100.2, 99.8, 100.0),
        ("2026-01-02 10:02:00", 100.3, 99.7, 100.1),
    ]}
    a = m.simulate("2026-01-02 10:00:52", 100.0, +1, 5.0, bars)
    b = m.simulate("2026-01-02 10:00:52", 100.0, -1, 5.0, bars)
    check("(A2) 두 팔이 대칭이다 (%+.4f / %+.4f)" % (a, b), abs(a + b) < 1e-9)


def test_sim_stop_wins_ties():
    """같은 봉에 스톱과 목표가 함께 닿으면 스톱 우선 — 낙관 편향 방지."""
    m = _rec()
    bars = {"2026-01-02": [("2026-01-02 10:01:00", 200.0, 1.0, 100.0)]}
    v = m.simulate("2026-01-02 10:00:52", 100.0, 1, 2.0, bars)
    check("동시 도달 시 스톱을 택한다 (%.2f < 0)" % v, v < 0)


def test_run_is_reproducible():
    """(A3) 같은 seed면 같은 결과여야 한다 — 매주 재계산의 전제."""
    m = _rec()
    a = m.run("2026-07-05 00:00:00", 40, 428)
    b = m.run("2026-07-05 00:00:00", 40, 428)
    check("(A3) seed 고정 시 재현된다",
          a.get("random_median_pt") == b.get("random_median_pt"))
    c = m.run("2026-07-05 00:00:00", 40, 999)
    check("(A3) seed가 다르면 결과도 다르다 (난수가 실제로 돈다)",
          c.get("random_median_pt") != a.get("random_median_pt"))
    check("실제 팔은 seed와 무관하다", a.get("actual_pt") == c.get("actual_pt"))


def test_channel_40():
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC.get("direction_value_watch")
    check("[40] 사전등록됨", isinstance(cr, dict))
    if not isinstance(cr, dict):
        return
    miss = [k for k in ("min_entries", "min_days", "alpha", "trials", "seed",
                        "min_day_win_share") if k not in cr]
    check("[40] 필수 키 전부 존재 (%s)" % (miss or "없음"), not miss)
    check("[40] min_days >= 6", int(cr.get("min_days", 0)) >= 6)
    out = _rep().eval_direction_value_watch()
    check("[40] 판정이 나온다", "verdict" in out)
    # [488차 재설계] REJECTS 핀 제거 — 방향 선택이 무작위를 이기기 시작하는 날
    # (SUPPORTS_HYP), 채널의 존재 이유가 실현되는 그 순간 테스트가 깨지면 안 된다.
    if out.get("verdict") == "INSUFFICIENT":
        check("[40] (④) INSUFFICIENT이면 사유가 남는다", bool(out.get("reason")))
    else:
        check("[40] (④) verdict 매핑 - SUPPORTS ↔ (perm_ok AND day_ok)",
              out.get("verdict") ==
              ("SUPPORTS_HYP" if (out.get("perm_ok") and out.get("day_ok"))
               else "REJECTS_HYP"))
        check("[40] 판정 2겹이 분리 보고된다",
              "perm_ok" in out and "day_ok" in out)
    check("[40] 실제·무작위 양쪽 수치가 남는다",
          "actual_pt" in out and "random_median_pt" in out)


# ══════════════ B — 청산 학습기 ══════════════

def _labels():
    from config.settings import (TRADES_DB, PREDICTIONS_DB, RAW_DATA_DB,
                                 ATR_STOP_MULT, ATR_TP1_MULT)
    from learning.exit_outcome_labeler import build_labels, summary, FEATURE_NAMES
    rows = build_labels(TRADES_DB, PREDICTIONS_DB, RAW_DATA_DB,
                        "2026-07-05 00:00:00", ATR_STOP_MULT, ATR_TP1_MULT)
    return rows, summary(rows), FEATURE_NAMES


def test_labeler():
    rows, s, names = _labels()
    check("라벨 행이 생성된다 (%s행)" % s.get("n_rows"), s.get("n_rows", 0) > 0)
    # [MW0601 488차 재설계] 98/16 핀은 428차 스냅샷 — 고정 시작(2026-07-05) 누적이라
    # 표본이 늘면 깨진다(08-23 실측 145/25, FAIL로 방치돼 있었다). 하한 + 정합으로 교체.
    check("(③) 포지션이 428차 하한(98) 이상 (%s)" % s.get("n_positions"),
          int(s.get("n_positions") or 0) >= 98)
    check("(③) 거래일이 428차 하한(16) 이상 (%s)" % s.get("n_days"),
          int(s.get("n_days") or 0) >= 16)
    check("(②) rows_per_position == n_rows / n_positions",
          abs(float(s["rows_per_position"])
              - round(s["n_rows"] / float(s["n_positions"]), 2)) < 1e-9)
    check("주 라벨과 보조 라벨이 둘 다 있다",
          "y_hold_better_rate" in s and "y_tp1_first_rate" in s)
    check("포지션당 행수가 기록된다 (유효표본 판단 재료)",
          s.get("rows_per_position", 0) > 1)
    if rows:
        r = rows[0]
        check("모든 피처가 행에 실린다", all(f in r for f in names))
        check("라벨이 0/1이다", r["y_hold_better"] in (0, 1)
              and r["y_tp1_first"] in (0, 1))
        check("포지션 상대 상태는 ATR 정규화라 가격 수준에 불변",
              abs(r["upnl_atr"]) < 50 and abs(r["dist_stop_atr"]) < 50)


def test_train_gate_and_no_pollution():
    """(B1)(B2) 학습 관문 — 미달이면 거부·무오염, 충족이면 실제로 학습한다.

    [MW0601 488차 재설계] 종전 이름은 `test_refuses_to_train`이고 `trained is
    False`와 `EPV == 2.25`(428차 실측)를 핀했다. EPV는 포지션 누적으로 올라가므로
    (08-23 실측 3.73) 데이터가 쌓이기만 해도 깨졌고, 표본이 차서 학습이 열리는
    날에는 `trained is False` 자체가 뒤집힌다 — 그날 이 테스트는 "학습 경로가
    열렸다"는 좋은 소식을 FAIL로 알리게 돼 있었다. 갈래를 미리 갈라 두고, EPV는
    값 핀 대신 **정의 항등식**(n_pos × rate / n_features)으로 고정한다.
    """
    import sqlite3
    from config.settings import TRADES_DB
    from learning.exit_classifier import (
        train_or_defer, ensure_table, MIN_EVENTS_PER_VARIABLE, MIN_DAYS)
    rows, s, names = _labels()
    ensure_table(TRADES_DB)
    with sqlite3.connect(TRADES_DB) as c:
        before = c.execute("SELECT COUNT(*) FROM exit_model_shadow").fetchone()[0]

    # 관문 판정과 지표는 persist=False 프로브로 얻는다 — 충족 갈래에서 persist=True를
    # 쓰면 테스트가 섀도 테이블에 실제로 쓴다(그건 EOD 체인의 몫이다).
    probe = train_or_defer(rows, s, names, None, persist=False)
    rd = probe.get("readiness") or {}
    check("(B1) EPV가 계산된다 (%s)" % rd.get("epv"), "epv" in rd)
    check("(②) EPV 정의 항등식 - n_pos × rate / n_features",
          abs(float(rd.get("epv", -1)) - round(
              int(rd["n_positions"]) * float(rd["pos_rate"])
              / float(rd["n_features"]), 3)) < 2e-3)
    check("(②) ready == (EPV >= %.0f AND 거래일 >= %d)"
          % (MIN_EVENTS_PER_VARIABLE, MIN_DAYS),
          bool(rd.get("ready"))
          == (float(rd.get("epv") or 0) >= MIN_EVENTS_PER_VARIABLE
              and int(rd.get("n_days") or 0) >= MIN_DAYS))
    check("(③) 포지션이 428차 하한(98) 이상 (%s)" % rd.get("n_positions"),
          int(rd.get("n_positions") or 0) >= 98)

    if not rd.get("ready"):
        out = train_or_defer(rows, s, names, TRADES_DB, persist=True)
        check("(B1) 미달이면 학습을 거부한다", out.get("trained") is False)
        check("(B1) 얼마나 부족한지 알려준다 (%s건)" % rd.get("positions_short"),
              int(rd.get("positions_short", 0)) > 0)
        with sqlite3.connect(TRADES_DB) as c:
            after = c.execute(
                "SELECT COUNT(*) FROM exit_model_shadow").fetchone()[0]
        check("(B2) 거부 시 DB를 오염시키지 않는다 (%d → %d)" % (before, after),
              after == before)
    else:
        check("(B1') 표본이 찼으면 학습한다 - [41] 게이지 해제의 실체",
              probe.get("trained") is True)
        check("(B1') OOF 지표가 나온다 (auc=%s)" % probe.get("oof_auc"),
              probe.get("oof_auc") is not None and "baseline_acc" in probe)
        with sqlite3.connect(TRADES_DB) as c:
            after = c.execute(
                "SELECT COUNT(*) FROM exit_model_shadow").fetchone()[0]
        check("(B2) persist=False 프로브는 DB에 쓰지 않는다 (%d → %d)"
              % (before, after), after == before)


def test_can_train_when_ready():
    """(B3)(B4) 위음성 방지 — 표본이 차면 실제로 학습하고 GroupKFold를 쓴다.

    이 테스트가 없으면 학습 경로가 깨져도 영원히 "표본 부족"으로만 보인다.
    """
    import random
    from learning.exit_classifier import train_or_defer
    rnd = random.Random(428)
    names = ["f1", "f2"]
    rows = []
    # 600포지션 × 3행. f1이 라벨과 연동되게 만들어 학습이 되는지 본다.
    for p in range(600):
        y = 1 if rnd.random() < 0.4 else 0
        for k in range(3):
            rows.append({
                "entry_ts": "P%04d" % p, "ts": "P%04d-%d" % (p, k),
                "day": "2026-01-%02d" % (1 + p % 25), "held_min": float(k + 1),
                "f1": y + rnd.gauss(0, 0.6), "f2": rnd.gauss(0, 1),
                "y_hold_better": y,
            })
    s = {"n_positions": 600, "n_days": 25, "y_hold_better_rate": 0.4}
    out = train_or_defer(rows, s, names, None, persist=False)
    check("(B3) 표본이 차면 학습한다", out.get("trained") is True)
    if out.get("trained"):
        check("(B3) OOF AUC가 계산된다 (%s)" % out.get("oof_auc"),
              out.get("oof_auc") is not None)
        check("(B3) 정보 있는 합성표본에서 AUC > 0.6 (%s)" % out.get("oof_auc"),
              float(out.get("oof_auc") or 0) > 0.6)
        check("(B3) 기준선 정확도를 함께 낸다 (AUC만 보면 오독)",
              "baseline_acc" in out)
    src = io.open(os.path.join(_ROOT, "learning", "exit_classifier.py"),
                  encoding="utf-8").read()
    check("(B4) GroupKFold를 쓴다", "GroupKFold" in src)
    check("(B4) 행 단위 KFold를 쓰지 않는다",
          "KFold(" not in src.replace("GroupKFold(", ""))


def test_not_wired_to_live():
    """(B5) 라이브 청산 경로가 청산 학습기를 호출하면 안 된다."""
    main_src = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    for name in ("exit_classifier", "exit_outcome_labeler", "exit_model_shadow"):
        check("(B5) main.py가 `%s`를 참조하지 않는다" % name, name not in main_src)


def test_channel_41():
    from config.settings import VALIDATION_CAMPAIGN as VC
    from learning.exit_classifier import MIN_EVENTS_PER_VARIABLE, MIN_DAYS
    cr = VC.get("exit_model_watch")
    check("[41] 사전등록됨", isinstance(cr, dict))
    if not isinstance(cr, dict):
        return
    check("[41] settings와 코드 상수가 일치한다 (EPV)",
          abs(float(cr["min_events_per_variable"]) - MIN_EVENTS_PER_VARIABLE) < 1e-9)
    check("[41] settings와 코드 상수가 일치한다 (min_days)",
          int(cr["min_days"]) == int(MIN_DAYS))
    out = _rep().eval_exit_model_watch()
    check("[41] 게이지가 나온다", out.get("verdict") == "OBSERVE")
    check("[41] 설정 표류가 없다", not out.get("config_drift"))
    check("[41] 잔여 거래일 추정이 나온다 (%s일)" % out.get("eta_trading_days"),
          out.get("eta_trading_days") is not None)


# ══════════════ C — 정보원 재검토 트리거 ══════════════

def test_c1_triggers_registered():
    from config.settings import FEATURE_SET_DECISIONS as FSD
    for key in ("opt_trade_flow_realtime", "constituent_lead_top_n"):
        d = FSD.get(key)
        check("(C1) `%s` 등록됨" % key, isinstance(d, dict))
        if not isinstance(d, dict):
            continue
        check("(C1) `%s` 기각이 아니라 조건부 대기(suppress=False)" % key,
              d.get("suppress") is False)
        check("(C1) `%s` 재검토 조건이 비어 있지 않다" % key,
              bool(d.get("re_eval")) and len(str(d["re_eval"])) > 30)
        check("(C1) `%s` 출처가 명시된다" % key, bool(d.get("source")))


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 428차] 방향가치 대조 + 청산 학습기 + 정보원 트리거")
    print("=" * 72)
    for fn in (
        test_sim_excludes_entry_bar,
        test_sim_arms_are_symmetric,
        test_sim_stop_wins_ties,
        test_run_is_reproducible,
        test_channel_40,
        test_labeler,
        test_train_gate_and_no_pollution,
        test_can_train_when_ready,
        test_not_wired_to_live,
        test_channel_41,
        test_c1_triggers_registered,
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
