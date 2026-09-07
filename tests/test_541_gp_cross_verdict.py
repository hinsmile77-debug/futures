# -*- coding: utf-8 -*-
"""[MW0601 541차] GP 교차 채널 **판정기** 회귀 테스트.

왜 필요한가
-----------
540차가 피처를 배선했고 541차가 리포트 판정기를 붙였다. 그런데 `data_start`가
2026-09-08이라 **당분간 실표본이 0건**이고, 판정기는 계속 `INSUFFICIENT`만 돌려준다.
그 상태로는 **로직이 옳은지 알 수 없다.**

이 프로젝트에는 그렇게 죽은 계측이 반복해서 있었다 —
  · FP-CRITICAL: 학습분포 저장 함수가 프로덕션에서 호출된 적 없어 2개월간 PSI=0.0 고정
  · TOX 섀도: `spread_extreme_shadow`를 매분 계산하고 **아무도 소비하지 않아** 한 달 방치
  · `_entry_horizon_pre`: 읽기 2곳·할당 0곳으로 영구 폴백
「표본이 없어서 판정이 안 나온다」와 「코드가 틀려서 판정이 안 나온다」는 겉보기가 같다.
그래서 합성 표본으로 **판정 경로 전체를 강제로 태운다.**

실행: pytest tests/test_541_gp_cross_verdict.py
"""
import importlib.util
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.environ.setdefault("MIREUK_TEST_MODE", "1")

import pytest  # noqa: E402

from config import settings  # noqa: E402
from features.feature_builder import compute_gp_cross_features  # noqa: E402

_SPEC = importlib.util.spec_from_file_location(
    "_gvcr", os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py"))
G = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(G)

SIM = dict(settings.VALIDATION_CAMPAIGN["gp_cross_highvol_watch"]["sim"])
CH1 = settings.VALIDATION_CAMPAIGN["gp_cross_highvol_watch"]
CH2 = settings.VALIDATION_CAMPAIGN["gp_cross_any_watch"]


def _bars(n, start=1000.0, step=0.0):
    hi = [start + i * step + 0.5 for i in range(n)]
    lo = [start + i * step - 0.5 for i in range(n)]
    cl = [start + i * step for i in range(n)]
    hh = ["10:%02d" % (i % 60) for i in range(n)]
    return hi, lo, cl, hh


# ───────────────────────── 1. 시뮬 ─────────────────────────
def test_sim_hits_tp():
    hi, lo, cl, hh = _bars(30)
    hi[5] = 1010.0                      # TP 도달(0.5ATR=1.0pt 위)
    g, net, out = G._gp_sim_one(0, hi, lo, cl, hh, 1, 2.0, SIM, cost_pt=0.0)
    assert out == "TP" and g == pytest.approx(1.0)


def test_sim_hits_stop():
    hi, lo, cl, hh = _bars(30)
    lo[5] = 990.0                       # 스톱 도달(1.5ATR=3.0pt 아래)
    g, net, out = G._gp_sim_one(0, hi, lo, cl, hh, 1, 2.0, SIM, cost_pt=0.0)
    assert out == "STOP" and g == pytest.approx(-3.0)


def test_stop_wins_when_both_hit_same_bar():
    """동시 도달 시 **스톱 우선**(보수) — 이 규약이 바뀌면 승률이 부풀려진다."""
    hi, lo, cl, hh = _bars(30)
    hi[5], lo[5] = 1010.0, 990.0
    g, net, out = G._gp_sim_one(0, hi, lo, cl, hh, 1, 2.0, SIM, cost_pt=0.0)
    assert out == "STOP"


def test_short_is_symmetric():
    hi, lo, cl, hh = _bars(30)
    lo[5] = 990.0                       # SHORT 에게는 TP
    g, net, out = G._gp_sim_one(0, hi, lo, cl, hh, -1, 2.0, SIM, cost_pt=0.0)
    assert out == "TP" and g == pytest.approx(1.0)


def test_force_exit_at_session_end():
    hi, lo, cl, hh = _bars(30)
    for i in range(10, 30):
        hh[i] = "15:10"                 # 절대원칙 §1 — 그 이후로 끌고 가지 않는다
    g, net, out = G._gp_sim_one(0, hi, lo, cl, hh, 1, 50.0, SIM, cost_pt=0.0)
    assert out == "FORCE"


def test_cost_is_subtracted():
    hi, lo, cl, hh = _bars(30)
    hi[5] = 1010.0
    g, net, out = G._gp_sim_one(0, hi, lo, cl, hh, 1, 2.0, SIM, cost_pt=0.25)
    assert net == pytest.approx(g - 0.25)


# ───────────────────── 2. 판정 게이트 ─────────────────────
def _rows(days, per_day, net_each):
    out = []
    for d in range(days):
        for k in range(per_day):
            out.append({"day": "2026-09-%02d" % (d + 1), "ts": "", "out": "TP",
                        "gross_krw": net_each + 1000.0, "net_krw": net_each})
    return out


def test_insufficient_when_sample_short():
    r = G._gp_day_verdict(_rows(5, 2, 10000.0), CH1, _rows(50, 4, -5000.0))
    assert r["verdict"] == "INSUFFICIENT" and "표본 미달" in r["reason"]


def test_fail_when_does_not_beat_random_control():
    """같은 고변동 구간에서 무작위가 더 좋으면 레짐 효과 — 반드시 FAIL."""
    rows = _rows(45, 2, 1000.0)                 # n=90, 45일 → 표본 충족
    ctrl = _rows(60, 4, 5000.0)                 # 대조가 더 좋다
    r = G._gp_day_verdict(rows, CH1, ctrl)
    assert r["verdict"] == "FAIL" and "무작위 대조" in r["reason"]


def test_fail_when_control_sample_short():
    r = G._gp_day_verdict(_rows(45, 2, 9000.0), CH1, _rows(3, 2, -1000.0))
    assert r["verdict"] == "INSUFFICIENT" and "대조군 표본 미달" in r["reason"]


def test_pass_requires_all_three():
    rows = _rows(45, 2, 9000.0)                 # 전 일자 흑자
    ctrl = _rows(60, 4, -5000.0)
    r = G._gp_day_verdict(rows, CH1, ctrl)
    assert r["verdict"] == "PASS"
    assert r["day_pos"] == 45 and r["day_neg"] == 0
    assert r["net_wo_best_days"] > 0


def test_fail_when_profit_concentrated_in_best_days():
    """최선 3일을 빼면 적자 — 며칠에 몰린 이익은 통과시키지 않는다(313차 ③ 역방향)."""
    rows = _rows(44, 2, -200.0)                 # 대부분 소폭 적자
    for k in range(3):                          # 3일에만 큰 이익
        rows.append({"day": "2026-10-%02d" % (k + 1), "ts": "", "out": "TP",
                     "gross_krw": 5e6, "net_krw": 5e6})
    r = G._gp_day_verdict(rows, CH1, _rows(60, 4, -5000.0))
    assert r["verdict"] == "FAIL"
    assert r["net_wo_best_days"] < 0


def test_fail_when_sign_test_not_significant():
    rows = _rows(23, 2, 5000.0) + _rows(22, 2, -5000.0)
    # 위 _rows 는 같은 날짜를 재사용하므로 날짜를 갈라준다
    for i, x in enumerate(rows):
        x["day"] = "2026-09-%02d" % (i // 2 + 1) if i < 46 else "2026-10-%02d" % (i // 2 - 22)
    r = G._gp_day_verdict(rows, CH1, _rows(60, 4, -9000.0))
    assert r["verdict"] in ("FAIL", "INSUFFICIENT")


# ───────────────── 3. 피처 ↔ 판정기 정합 ─────────────────
def test_evaluator_reads_the_keys_the_feature_writes():
    """피처가 쓰는 키 이름과 판정기가 읽는 키 이름이 어긋나면 조용히 표본 0이 된다."""
    f = compute_gp_cross_features([100.0] * 21, atr=0.16, period=settings.GP_CROSS_PERIOD)
    src = open(os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py"),
               encoding="utf-8").read()
    # 판정기는 period 를 포맷팅해 키를 만든다 — 실제 생성 키가 피처 출력에 있어야 한다
    p = settings.GP_CROSS_PERIOD
    for k in ("gp_cross_up_%d" % p, "gp_cross_dn_%d" % p,
              "gp_cross_tight_%d" % p, "gp_ready_%d" % p):
        assert k in f, "피처가 %s 를 내보내지 않는다" % k
    for k in ("gp_cross_up_%d", "gp_cross_dn_%d", "gp_cross_tight_%d", "gp_ready_%d"):
        assert k in src, "판정기가 %s 패턴을 쓰지 않는다" % k
    assert "atr_bp" in f and "atr_bp_measured" in f


def _fn_code(name):
    """함수 본문에서 **독스트링을 제외한 실제 코드**만 돌려준다.

    독스트링에 「~를 쓰지 않는다」고 적어 둔 설명 문구를 실제 호출로 오인하지 않기 위해서다.
    """
    import ast
    src = open(os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py"),
               encoding="utf-8").read()
    lines = src.splitlines()
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            body = list(node.body)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(getattr(body[0], "value", None), ast.Str)):
                body = body[1:]            # 독스트링 제거
            if not body:
                return ""
            start = body[0].lineno - 1
            end = max(getattr(n, "lineno", start) for n in ast.walk(node))
            return "\n".join(lines[start:end + 1])
    raise AssertionError("함수 %s 를 찾지 못했다" % name)


def test_evaluator_uses_live_rate_not_pinned():
    """🔴 사전등록이 실측 요율을 명시했다 — 핀값을 쓰면 판정이 조용히 낙관된다(493차)."""
    code = _fn_code("eval_gp_cross_channels")
    assert "FUTURES_COMMISSION_RATE" in code
    assert "_roundtrip_cost_pt(" not in code, (
        "이 채널은 핀값 비용모델을 쓰면 안 된다 — cost_source=BROKER_CHANNEL_SPECS")


def test_evaluator_is_prospective_only():
    """소급을 세면 사전등록이 무의미해진다 — data_start 를 그대로 써야 한다."""
    code = _fn_code("eval_gp_cross_channels")
    assert 'ch1["data_start"]' in code
    assert "ts >= ?" in code


def test_control_channel_verdict_is_not_pass():
    """[59]는 대조 전용 — PASS/FAIL 어휘로 승격 후보처럼 보이면 안 된다."""
    rows = _rows(45, 8, 9000.0)                 # n=360 → GP-2 min_samples 300 충족
    ctrl = _rows(60, 4, -5000.0)
    r = G._gp_day_verdict(rows, CH2, ctrl)
    assert r["verdict"] in ("PASS", "FAIL")     # 내부 계산은 그대로
    # 실제 채널 출력에서는 어휘가 바뀐다 — eval_gp_cross_channels 가 변환한다
    src = open(os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py"),
               encoding="utf-8").read()
    assert "SUPPORTS_HYP" in src and "REJECTS_HYP" in src


def test_channel_is_wired_into_report():
    src = open(os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py"),
               encoding="utf-8").read()
    assert "gpx = eval_gp_cross_channels()" in src, "build_report 가 호출하지 않는다"
    assert '"gp_cross_channels": gpx' in src, "metrics 에 실리지 않는다"
    assert "## [58] GOLDEN POWER" in src, "리포트 섹션이 없다"
    assert "[59] GP 교차" in src, "요약표 행이 없다"


def test_evaluator_runs_on_live_db_without_error():
    """실 DB 로 한 번 돌려 예외가 없고 진단 필드가 채워지는지 — 죽은 계측 방지.

    ⚠ DB 는 런타임 산출물이라 커밋되지 않는다(워크트리·CI 에는 없다).
    없으면 **건너뛴다** — 그건 환경 조건이지 로직 결함이 아니다.
    있으면 반드시 무예외로 돌아야 한다.
    """
    if not os.path.exists(settings.RAW_DATA_DB):
        pytest.skip("raw_data.db 없음 — 런타임 산출물이라 이 환경에는 없다")
    out = G.eval_gp_cross_channels()
    assert "error" not in out, out.get("error")
    for k in ("data_start", "atr_bp_min", "cost_rate", "n_feature_rows", "n_cross_raw"):
        assert k in out, k
    assert out["tight"]["verdict"] in (
        "INSUFFICIENT", "PASS", "FAIL", "NOT_AVAILABLE_ON_THIS_BRANCH")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
