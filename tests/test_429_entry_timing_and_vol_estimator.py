"""[MW0602 429차] [42] 타점의 가치 · [43] 변동성 추정량 회귀 테스트.

────────────────────────────────────────────────────────────────────────────
왜 이 둘인가
────────────────────────────────────────────────────────────────────────────
428차 결론을 "체크리스트와 청산의 기술로 수익"으로 읽으려 했는데, 그 전제의
**절반이 미검증**이었다. [40]은 진입 **시각을 고정**한 채 방향만 뒤집어 방향 축만
격리했고, "체크리스트가 고른 타점"의 가치는 재지 않았다. → [42]가 그 축이다.

그리고 "변동성 피처를 진입에 도입하자"는 제안을 검토하다 발견한 것 —
**사이저는 이미 ATR로 변동성 스케일링을 하고 있다**
(`stop_risk = atr × ATR_STOP_MULT × pt_value`). 그러니 질문은 "변동성을 넣자"가
아니라 **"어느 추정량이 더 나은가"** 이고, 답은 부분상관으로 나온다. → [43].

429차 실측:
  [42] A -22.07 / B중앙 +7.33 / C중앙 +8.00 · 타점 기여 **-0.67pt**
       짝지은 부호검정 B>C **49.0%, p=0.726**  → 타점에도 가치 없음
  [43] 공선성 **0.956** · ATR 통제 후 부분상관 **+0.021 (t=0.17)**
       → ATR 위에 추가 정보 없음. 단 `int()` 절단 때문에 qty는 **58.8%에서 갈린다**
         (= 근거 없는 사이즈 변동 주입 → 무해가 아니라 유해)

────────────────────────────────────────────────────────────────────────────
지키려는 불변식
────────────────────────────────────────────────────────────────────────────
(A) **3팔 검정은 짝지어야 한다.** 같은 시행에서 B·C를 뽑아 부호를 센다 — 두 팔이
    같은 시장 데이터를 공유해 양의 상관을 가지므로, 독립 표본으로 다루면 p가
    낙관적으로 나온다.
(B) **C의 후보 분봉은 09:05~14:49로 제한한다.** 라이브도 14:50부터 신규진입
    금지(345차)라 그 밖에서 뽑으면 실제로 불가능한 진입과 비교하게 된다.
    거래일별 건수도 실제와 맞춰 일중 빈도를 보존한다.
(C) **[43] 판정은 상관이 아니라 부분상관으로 한다.** 공선성이 높다는 사실만으로
    기각하면 잔차에 정보가 있는 경우를 놓친다.
(D) **qty 경계 통과를 함께 재야 한다.** 연속값이 거의 같아도 이산화 후 계약수가
    갈릴 수 있다. 이 수가 크면서 부분상관이 0이면 **교체는 유해**다.

실행: python tests/test_429_entry_timing_and_vol_estimator.py   (COM/브로커 불필요)
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


# ══════════════ [42] 타점의 가치 ══════════════

def test_binom_helper():
    m = _rec()
    check("양측 이항 k=0,n=5 → 0.0625", abs(m._binom_two_sided(0, 5) - 0.0625) < 1e-9)
    check("양측 이항 k=2,n=7 → 0.4531",
          abs(m._binom_two_sided(2, 7) - 0.453125) < 1e-9)
    check("양측 이항 k=200,n=400 → 1.0 (완전 무작위)",
          abs(m._binom_two_sided(200, 400) - 1.0) < 1e-6)
    check("n=0 방어", m._binom_two_sided(0, 0) == 1.0)


def test_three_arm_shape():
    m = _rec()
    r = m.run_three_arm("2026-07-05 00:00:00", 60, 429)
    for k in ("arm_a_pt", "arm_b_median_pt", "arm_c_median_pt", "timing_gain_pt",
              "b_over_c_share", "sign_p", "n_candidate_bars", "entry_window"):
        if k not in r:
            check("3팔 결과에 %s가 있다" % k, False)
            return
    check("3팔 결과 키가 전부 있다", True)
    check("(B) 후보 분봉 창이 09:05~14:49다 (345차 신규진입 금지 반영)",
          list(r["entry_window"]) == ["09:05", "14:49"])
    check("(B) 후보 분봉이 실제 진입보다 훨씬 많다 (%s개)" % r["n_candidate_bars"],
          r["n_candidate_bars"] > r["n_usable"] * 10)
    check("타점 기여가 B-C로 계산된다",
          abs(r["timing_gain_pt"] - (r["arm_b_median_pt"] - r["arm_c_median_pt"]))
          < 1e-6)
    # [MW0601 488차 재설계] A팔 값 핀(-22.0683, 429차 실측)은 고정 시작 누적이라
    # 표본과 함께 움직인다(08-23 실측 +25.09). "무작위와 무관"의 정직한 형태는
    # **seed 불변성**이다 — test_three_arm_reproducible이 그 축을 잰다.
    check("A팔이 유한한 pt 값이다 (%.2f)" % r["arm_a_pt"],
          isinstance(r["arm_a_pt"], float)
          and r["arm_a_pt"] == r["arm_a_pt"])   # NaN 방어


def test_three_arm_is_paired():
    """(A) 짝지은 검정인가 — 시행 수와 부호 카운트가 대응해야 한다."""
    m = _rec()
    r = m.run_three_arm("2026-07-05 00:00:00", 80, 429)
    check("(A) B>C 시행수가 trials를 넘지 않는다",
          0 <= r["trials_b_over_c"] <= r["trials"])
    check("(A) 비율이 시행수/trials와 일치한다",
          abs(r["b_over_c_share"] - r["trials_b_over_c"] / float(r["trials"])) < 1e-6)
    src = io.open(os.path.join(_ROOT, "scripts", "random_entry_control.py"),
                  encoding="utf-8").read()
    check("(A) diff = b - c 를 시행마다 쌓는다 (짝지음)",
          "diff.append(b - c)" in src)


def test_three_arm_reproducible():
    m = _rec()
    a = m.run_three_arm("2026-07-05 00:00:00", 60, 429)
    b = m.run_three_arm("2026-07-05 00:00:00", 60, 429)
    check("같은 seed면 재현된다",
          a["arm_c_median_pt"] == b["arm_c_median_pt"]
          and a["sign_p"] == b["sign_p"])
    c = m.run_three_arm("2026-07-05 00:00:00", 60, 777)
    check("seed가 다르면 C팔이 달라진다 (난수가 실제로 돈다)",
          c["arm_c_median_pt"] != a["arm_c_median_pt"])
    # [488차] A팔은 실제 진입 재생이므로 seed와 무관해야 한다 — 무작위가 A에
    # 새는 순간 3팔 비교 전체가 무효가 된다(종전 값 핀이 지키려던 실제 불변식).
    check("A팔은 seed와 무관하다 (%.4f == %.4f)"
          % (a["arm_a_pt"], c["arm_a_pt"]), a["arm_a_pt"] == c["arm_a_pt"])


def test_channel_42():
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC.get("entry_timing_value_watch")
    check("[42] 사전등록됨", isinstance(cr, dict))
    if not isinstance(cr, dict):
        return
    miss = [k for k in ("min_entries", "min_days", "alpha", "trials", "seed",
                        "entry_window") if k not in cr]
    check("[42] 필수 키 전부 존재 (%s)" % (miss or "없음"), not miss)
    check("[42] min_days >= 6", int(cr.get("min_days", 0)) >= 6)
    out = _rep().eval_entry_timing_value_watch()
    # [488차 재설계] REJECTS 핀 → ④ 매핑. 권고 문구도 갈래별로 다르므로("얹지 말라"는
    # 비유의 갈래 전용) 무조건 검사하지 않는다 — [35] 무조건 프로즈와 같은 유형.
    _sig = float(out.get("sign_p", 1.0)) < float(cr["alpha"])
    if out.get("verdict") == "INSUFFICIENT":
        check("[42] (④) INSUFFICIENT이면 사유가 남는다", bool(out.get("reason")))
    else:
        _exp = ("SUPPORTS_HYP"
                if (_sig and float(out.get("timing_gain_pt", 0.0)) > 0)
                else "REJECTS_HYP")
        check("[42] (④) verdict 매핑 - SUPPORTS ↔ (p<α AND 기여>0), 실제 %s"
              % out.get("verdict"), out.get("verdict") == _exp)
        if not _sig:
            check("[42] 비유의 갈래 권고가 '전제 위에 얹지 말라'를 말한다",
                  "얹지" in (out.get("recommendation") or ""))
    check("[42] 짝지은 p가 보고된다 (%s)" % out.get("sign_p"), "sign_p" in out)
    check("[42] 세 팔이 전부 보고된다",
          all(k in out for k in ("arm_a_pt", "arm_b_median_pt", "arm_c_median_pt")))


# ══════════════ [43] 변동성 추정량 ══════════════

def test_channel_43():
    from config.settings import VALIDATION_CAMPAIGN as VC
    cr = VC.get("vol_estimator_watch")
    check("[43] 사전등록됨", isinstance(cr, dict))
    if not isinstance(cr, dict):
        return
    miss = [k for k in ("min_samples", "min_days", "alpha", "horizon_min",
                        "min_partial_t", "collinearity_warn",
                        "report_qty_boundary") if k not in cr]
    check("[43] 필수 키 전부 존재 (%s)" % (miss or "없음"), not miss)
    out = _rep().eval_vol_estimator_watch()
    # [488차 재설계] 실측 핀 3개(REJECTS·공선성 0.956·부분상관 +0.021)와
    # `|t| < 2.0` 단언은 전부 현재 데이터의 스냅샷이다 — 공선성은 이미 0.821로
    # 움직여 FAIL로 방치돼 있었고, t 단언은 잔차에 정보가 나타나는 날(SUPPORTS)
    # 깨진다. ② 범위 · ③ 하한 · ④ 매핑으로 교체한다.
    if out.get("verdict") == "INSUFFICIENT":
        check("[43] (④) INSUFFICIENT이면 표본 관문 미달이 사유다",
              int(out.get("n", 0)) < int(cr["min_samples"])
              or int(out.get("n_days", 0)) < int(cr["min_days"]))
    else:
        check("[43] (④) (C) 판정 매핑 - SUPPORTS ↔ |partial_t| >= %s (t=%s)"
              % (cr["min_partial_t"], out.get("partial_t")),
              out.get("verdict") ==
              ("SUPPORTS_HYP"
               if abs(float(out.get("partial_t") or 0.0))
               >= float(cr["min_partial_t"]) else "REJECTS_HYP"))
        check("[43] (③) 표본이 0821 실측 하한(151건) 이상 (%s)" % out.get("n"),
              int(out.get("n", 0)) >= 151)
    check("[43] (②) 공선성이 상관 범위 안이다 (%s)" % out.get("collinearity"),
          -1.0 <= float(out.get("collinearity", 9.0)) <= 1.0)
    check("[43] (②) 부분상관이 범위 안이다 (%s)" % out.get("partial_corr"),
          -1.0 <= float(out.get("partial_corr", 9.0)) <= 1.0)
    check("[43] ATR 자체의 예측력도 함께 보고된다 (r=%s)"
          % out.get("corr_atr_realized"), "corr_atr_realized" in out)


def test_qty_boundary_computed():
    """(D) qty 경계 통과가 실제로 계산돼야 한다.

    초판은 `MINI_FUTURES_PT_VALUE`를 `config.settings`에서 import해
    ImportError로 **조용히 건너뛰었다**(리포트에 '—'로만 표시). 상수는
    `config.constants`에 있다.
    """
    out = _rep().eval_vol_estimator_watch()
    check("(D) qty 경계 계산이 실패하지 않는다 (%s)"
          % out.get("qty_boundary_error", "정상"),
          "qty_boundary_error" not in out)
    check("(D) 경계 통과 건수가 보고된다 (%s건)" % out.get("qty_boundary_cross"),
          out.get("qty_boundary_cross") is not None)
    check("(D) 정규화 계수가 남는다 (수준차를 효과로 오인 방지)",
          out.get("norm_k") is not None)
    # 공선성이 높은데 경계 통과가 많다 = 교체는 무해가 아니라 유해
    if out.get("qty_boundary_share") is not None:
        # [488차 재설계] 58.8% 핀(429차 실측)은 정규화 계수가 전체 표본으로 매번
        # 재산출돼 과거 행의 경계 판정까지 함께 움직인다(08-23 실측 70.9%) —
        # 단조도 아니다. 정의 정합(share == cross/n)으로 교체.
        check("(②) share == cross / n (%.1f%% = %s/%s)"
              % (float(out["qty_boundary_share"]) * 100,
                 out.get("qty_boundary_cross"), out.get("n")),
              abs(float(out["qty_boundary_share"])
                  - round(int(out["qty_boundary_cross"])
                          / float(out["n"]), 4)) < 1e-9)
        if out.get("verdict") == "REJECTS_HYP":
            check("(D) REJECTS 갈래 권고가 '유해' 논지를 담는다",
                  "유해" in (out.get("recommendation") or ""))


def test_constants_import_path():
    """MINI_FUTURES_PT_VALUE는 constants에 있고 settings에는 없다 — 회귀 고정."""
    from config import constants as C
    check("config.constants에 MINI_FUTURES_PT_VALUE가 있다",
          hasattr(C, "MINI_FUTURES_PT_VALUE"))
    from config import settings as S
    check("config.settings에는 없다 (초판 ImportError의 원인)",
          not hasattr(S, "MINI_FUTURES_PT_VALUE"))


def test_renders_in_report():
    m = _rep()
    md, metrics = m.build_report(28)
    for k in ("entry_timing_value_watch", "vol_estimator_watch"):
        check("metrics에 %s가 실린다" % k, k in metrics)
    check("요약표에 [42] 행", "| [42] 타점의 가치" in md)
    check("요약표에 [43] 행", "| [43] 변동성 추정량 교체" in md)
    check("[42] 상세섹션", "## [42] 타점(진입 시각)의 가치" in md)
    check("[43] 상세섹션", "## [43] 변동성 추정량 교체 가치" in md)
    check("3팔 표가 렌더된다", "무작위시각" in md)
    # [488차 재설계] 공선성 경보는 |collinearity| >= collinearity_warn일 때만
    # 렌더된다(0821 실측 0.821 < 0.90 → 미렌더가 정상). 무조건 존재 검사는 [35]
    # 무조건 프로즈와 같은 유형 — 조건과 묶어 검사한다.
    from config.settings import VALIDATION_CAMPAIGN as _VC
    _vw = metrics.get("vol_estimator_watch") or {}
    _cw = float((_VC.get("vol_estimator_watch") or {})
                .get("collinearity_warn", 0.90))
    _col = abs(float(_vw.get("collinearity") or 0.0))
    check("공선성 경보가 조건대로 렌더된다 (|col|=%.3f vs warn %.2f → %s)"
          % (_col, _cw, "출현" if _col >= _cw else "미출현"),
          ("사실상 같은 변수" in md) == (_col >= _cw))


if __name__ == "__main__":
    print("=" * 72)
    print("[MW0602 429차] 타점의 가치 + 변동성 추정량 교체 가치")
    print("=" * 72)
    for fn in (
        test_binom_helper,
        test_three_arm_shape,
        test_three_arm_is_paired,
        test_three_arm_reproducible,
        test_channel_42,
        test_channel_43,
        test_qty_boundary_computed,
        test_constants_import_path,
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
