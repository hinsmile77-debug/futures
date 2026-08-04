"""[MW0602 426차] [38] ProfitGuard-L1 캠페인 채널 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
이 채널이 왜 필요한가 — 0804 점검의 과장을 잡았기 때문이다
────────────────────────────────────────────────────────────────────────────
0804 일일점검이 ProfitGuard-L1을 "오늘 최대의 손실 방어"로 적었다. 검증 결과
**과장이었다**:

  · 캠페인 16거래일 중 피크가 발동금액(100만원)에 닿은 날 **3일**,
    L1이 발동한 날 **2일**, 그중 실제로 진입을 막은 날 **1일**.
    07-20은 14:56 발동 — 마지막 진입 14:33·14:50 신규금지 이후라 무해무익.
  · 유일하게 구속력이 있던 08-04 차단 40건의 30분창 반사실은
    **TP1 24 / STOP 16, 누적 -1.87pt(-93,492원)** — 박빙이지 "최대 방어"가 아니다.

즉 **단일일 인상이 정책 근거가 될 뻔했다.** 이 채널은 그 재발을 막는 장치다.

────────────────────────────────────────────────────────────────────────────
지키려는 불변식
────────────────────────────────────────────────────────────────────────────
(A) **구속(binding) 판정의 순환논리 금지.**
    "발동 후 실제 진입이 있었는가"로만 세면, 가드가 **라이브로 실제 발동한 날**은
    그 진입이 애초에 없으므로(가드가 막았다) 구속이 아닌 것으로 잡힌다 —
    유일한 진짜 구속 사건이 사라진다. 08-04이 정확히 그 케이스였다.
    라이브 차단 기록이 있으면 구속으로 인정해야 한다.

(B) **운영 파라미터의 출처를 표기해야 한다.**
    라이브 값은 `data/profit_guard_prefs.json`(gitignore, **대시보드에서 장중
    변경 가능**)에서 오고 코드 기본값과 다르다(운영 100만/20% vs 코드 200만/35%).
    코드만 보고 판정하면 전혀 다른 임계를 재게 된다 — 419·420차 `tox_regime_date`
    교훈의 더 나쁜 버전이다.

(C) **재개 축은 두 조각을 함께 내야 한다.**
    "재개 후 손익"만 보면 재개가 항상 이득처럼 보인다. 막은 구간의 손익을 나란히
    놓아야 (-,+) 조합인 지연을 고를 수 있다.

(D) **판정을 서두르지 않는다.** 실측 발동빈도로 min_activations=5는 약 4개월
    스케일이다. verdict는 그때까지 OBSERVE여야 한다.

실행: python tests/test_426_profit_guard_l1.py   (COM/브로커 불필요)
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


def _mod():
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    import importlib
    return importlib.import_module("generate_validation_campaign_report")


# ══════════════ 사전등록 ══════════════

def test_channel_registered():
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC.get("profit_guard_l1_watch")
    check("[38] 채널이 사전등록돼 있다", isinstance(cr, dict))
    if not isinstance(cr, dict):
        return
    need = ("min_activations", "min_days", "alpha", "cf_window_min",
            "sweep_activation_krw", "sweep_ratio", "resume_delay_min",
            "live_prefs_path")
    miss = [k for k in need if k not in cr]
    check("필수 키 전부 존재 (%s)" % (miss or "없음"), not miss)
    check("(D) min_days >= 5 (313차 단일일 판정 금지)",
          int(cr.get("min_days", 0)) >= 5)
    check("스윕 격자에 현행 운영값(1,000,000 / 0.20)이 포함된다",
          1_000_000 in cr.get("sweep_activation_krw", [])
          and 0.20 in cr.get("sweep_ratio", []))
    check("재개 후보에 0(=현행 유지)이 있다 - 기준선 없이 비교 불가",
          0 in cr.get("resume_delay_min", []))


# ══════════════ (B) 설정 출처 ══════════════

def test_live_config_provenance():
    m = _mod()
    lc = m._pg_live_config()
    check("(B) 운영 설정을 읽어낸다", "activation_krw" in lc and "ratio" in lc)
    check("(B) 코드 기본값도 함께 보고한다",
          "code_activation_krw" in lc and "code_ratio" in lc)
    check("(B) prefs 파일 경로를 명시한다", bool(lc.get("prefs_path")))
    if lc.get("prefs_exists"):
        check("(B) 출처가 prefs_json으로 표기된다", lc.get("source") == "prefs_json")
        check("(B) 코드 기본값과의 불일치를 감지한다 (운영 100만/20% vs 코드 200만/35%)",
              lc.get("diverged") is True)
        check("(B) 운영값 실측 - 발동 1,000,000원",
              abs(float(lc["activation_krw"]) - 1_000_000) < 1e-6)
        check("(B) 운영값 실측 - 비율 20%",
              abs(float(lc["ratio"]) - 0.20) < 1e-9)
    else:
        check("(B) prefs 없으면 코드 기본값으로 폴백한다",
              lc.get("source") == "code_default")


# ══════════════ _pg_replay 역학 ══════════════

def test_replay_mechanics():
    m = _mod()
    days = ["2026-01-02"]
    # 실현손익 경로: +120만 → +80만 (피크 대비 33% 하락)
    legs = {"2026-01-02": [
        {"exit_ts": "2026-01-02 10:00:00", "k": 1_200_000.0},
        {"exit_ts": "2026-01-02 11:00:00", "k": -400_000.0},
    ]}
    pos = {"2026-01-02": [
        {"entry_ts": "2026-01-02 09:30:00", "k": 1_200_000.0},
        {"entry_ts": "2026-01-02 12:00:00", "k": -300_000.0},   # 발동 후 진입
    ]}
    f = m._pg_replay(1_000_000, 0.20, days, legs, pos)
    check("발동금액·비율을 넘기면 발동한다", len(f) == 1)
    if f:
        check("발동 시각이 하락 레그 시각이다", f[0]["halt_ts"] == "2026-01-02 11:00:00")
        check("피크를 정확히 기록한다", abs(f[0]["peak_krw"] - 1_200_000) < 1e-6)
        check("발동 후 진입 1건을 잡는다", f[0]["n_after"] == 1)
        check("그 손익을 합산한다", abs(f[0]["after_pnl_krw"] + 300_000) < 1e-6)
        check("진입이 있었으므로 구속이다", f[0]["binding"] is True)

    # 피크가 발동금액에 못 미치면 발동하지 않는다
    f2 = m._pg_replay(2_000_000, 0.20, days, legs, pos)
    check("피크 < 발동금액이면 발동하지 않는다", len(f2) == 0)
    # 비율이 넉넉하면 발동하지 않는다
    f3 = m._pg_replay(1_000_000, 0.50, days, legs, pos)
    check("하락폭 < 비율이면 발동하지 않는다", len(f3) == 0)

    # 발동 후 진입이 없으면 replay 단계에선 비구속
    pos2 = {"2026-01-02": [{"entry_ts": "2026-01-02 09:30:00", "k": 1_200_000.0}]}
    f4 = m._pg_replay(1_000_000, 0.20, days, legs, pos2)
    check("발동 후 진입이 없으면 replay는 비구속으로 본다",
          f4 and f4[0]["binding"] is False)


# ══════════════ (A) 구속 판정 순환논리 교정 ══════════════

def test_binding_not_circular():
    """실 DB — 08-04은 라이브 차단이 있었으므로 반드시 구속이어야 한다."""
    m = _mod()
    out = m.eval_profit_guard_l1_watch()
    fires = {f["day"]: f for f in (out.get("fires") or [])}
    check("(A) 08-04 발동이 잡힌다", "2026-08-04" in fires)
    if "2026-08-04" in fires:
        f = fires["2026-08-04"]
        check("(A) 발동 후 실제 진입은 0건이다 (가드가 막았으므로)",
              f["n_after"] == 0)
        check("(A) 그럼에도 라이브 차단 기록으로 **구속** 판정된다",
              f["binding"] is True and f.get("n_live_blocked", 0) > 0)
    if "2026-07-20" in fires:
        check("(A) 07-20은 무해무익 - 비구속 (14:56 발동, 마지막 진입 14:33)",
              fires["2026-07-20"]["binding"] is False)
    check("(A) 구속 발동 = 1건 (426차 실측)", out.get("n_binding") == 1)
    check("(A) 구속 거래일 = 1일", out.get("n_binding_days") == 1)


# ══════════════ 반사실·재개·스윕 ══════════════

def test_counterfactual_matches_measurement():
    """426차 실측 재현 — 0804 과장을 잡아낸 바로 그 수치."""
    m = _mod()
    out = m.eval_profit_guard_l1_watch()
    check("차단 신호 40건", out.get("n_blocked_signals") == 40)
    o = out.get("cf_outcome") or {}
    check("반사실 결과 TP1 24 / STOP 16", o.get("TP1") == 24 and o.get("STOP") == 16)
    check("누적 -1.87pt - '최대 방어'가 아니라 박빙",
          abs(float(out.get("cf_total_pt", 0)) + 1.87) < 0.05)
    check("건당 평균이 함께 보고된다", "cf_avg_pt" in out)


def test_resume_reports_both_sides():
    m = _mod()
    out = m.eval_profit_guard_l1_watch()
    rd = out.get("resume_delay") or {}
    check("(C) 재개 지연 축이 존재한다", bool(rd))
    if not rd:
        return
    for k, v in rd.items():
        if not all(x in v for x in ("n", "pt", "n_kept", "kept_pt")):
            check("(C) 모든 지연에 두 조각이 다 있다 (%s)" % k, False)
            return
    check("(C) 모든 지연에 차단유지/재개후 두 조각이 다 있다", True)
    z = rd.get("0")
    check("(C) 지연 0분은 차단 유지분이 0건이다 (기준선)",
          z and z["n_kept"] == 0)
    f15 = rd.get("15")
    if f15:
        check("(C) 426차 실측 - 15분 지연이 (차단 -22.25pt / 재개 +20.38pt)",
              abs(f15["kept_pt"] + 22.25) < 0.1 and abs(f15["pt"] - 20.38) < 0.1)


def test_sweep_grid():
    m = _mod()
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC["profit_guard_l1_watch"]
    out = m.eval_profit_guard_l1_watch()
    sw = out.get("sweep") or []
    check("스윕이 격자 전체를 돈다",
          len(sw) == len(cr["sweep_activation_krw"]) * len(cr["sweep_ratio"]))
    check("각 행이 발동/구속/차단건/지킨금액을 낸다",
          all(all(k in s for k in
                  ("n_fire", "n_binding", "n_blocked_pos", "saved_krw")) for s in sw))
    hi = [s for s in sw if s["activation_krw"] >= 1_500_000]
    check("발동금액 150만+ 격자는 전부 무발동 (피크가 닿은 적 없다)",
          all(s["n_fire"] == 0 for s in hi))


# ══════════════ (D) 판정 유예 ══════════════

def test_verdict_is_observe():
    m = _mod()
    out = m.eval_profit_guard_l1_watch()
    check("(D) verdict가 OBSERVE다 - 표본 미달", out.get("verdict") == "OBSERVE")
    check("(D) 사유에 필요 표본이 명시된다", "필요" in (out.get("reason") or ""))
    check("(D) 4개월 스케일임을 명시한다", "4개월" in (out.get("reason") or ""))


def test_renders_in_report():
    """리포트에 [38] 요약행과 상세섹션이 실제로 나오는가."""
    m = _mod()
    md, metrics = m.build_report(28)
    check("metrics에 채널이 실린다", "profit_guard_l1_watch" in metrics)
    check("요약표에 [38] 행이 있다", "| [38] ProfitGuard-L1" in md)
    check("상세섹션이 있다", "## [38] ProfitGuard-L1" in md)
    check("설정 출처 경고가 렌더된다", "profit_guard_prefs.json" in md)
    check("재개 표가 렌더된다", "재개 지연" in md)
    check("스윕 표가 렌더된다", "임계 스윕" in md)


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 426차] [38] ProfitGuard-L1 캠페인 채널 회귀 테스트")
    print("=" * 72)
    for fn in (
        test_channel_registered,
        test_live_config_provenance,
        test_replay_mechanics,
        test_binding_not_circular,
        test_counterfactual_matches_measurement,
        test_resume_reports_both_sides,
        test_sweep_grid,
        test_verdict_is_observe,
        test_renders_in_report,
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
