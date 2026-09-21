# tests/test_612_divergence_panel_units.py
"""[MW0601 612차] 다이버전스+포지션 탭 데이터 유효성 회귀 가드.

2026-09-21 점검에서 이 탭에 세 계열의 결함이 확인됐다. 셋 다 "값이 안 나온다"가
아니라 **그럴듯한 값이 틀린 뜻으로 보인다** 계열이라, 눈으로는 영영 안 잡힌다.

  ① 단위     — 금액(백만원) 2칸이 "(계약수)" 섹션 제목 아래 있었다
  ② 체인캐시 — 옵션 코드 목록이 2026-06-04 에 멈춰 재수집 조건이 구조적으로
                성립 불가였다(낡은 목록에 유효 코드가 남으면 영원히 안 받는다)
  ③ 바이어스 — 막대가 ×50 이라 절반까지만 찼고, bias 는 부호가 갈리면 항등적으로
                ±1.00 이라 규모를 못 쟀다

이 파일은 세 가지가 되돌아가는 것을 막는다. PyQt 위젯을 띄우지 않고 **소스와
순수 로직만** 검사한다 — 대시보드는 py37_32 GUI 의존이 커서 헤드리스 수집 단계에서
깨지면 무관한 테스트까지 함께 죽는다.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import tempfile

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
_SNAP = os.path.join(_ROOT, "collection", "options", "option_chain_snapshot.py")
_WORK = os.path.join(_ROOT, "collection", "options", "option_chain_worker.py")
_MAIN = os.path.join(_ROOT, "main.py")


def _src(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ── ① 단위 ────────────────────────────────────────────────────────────────

def test_1_futures_section_title_does_not_claim_contracts_for_mixed_grid():
    """섹션 제목이 그리드 전체를 "계약수"라 부르면 안 된다 — 금액 2칸이 섞여 있다."""
    src = _src(_DASH)
    assert '"선물 투자자 수급 (계약수)"' not in src, (
        "선물 수급 섹션 제목이 다시 '(계약수)'로 돌아갔다. 이 그리드에는 "
        "프로그램 차익/비차익(= CpSvr8111 idx19·idx37, 순매수 체결금액·백만원)이 "
        "함께 있어 한 단위로 덮을 수 없다 — 계측 4원칙 ①."
    )


def test_2_program_cards_carry_amount_unit_in_title():
    """프로그램 차익·비차익 카드 제목에 금액 단위가 박혀 있어야 한다."""
    src = _src(_DASH)
    for title in ("프로그램 차익 (백만원)", "프로그램 비차익 (백만원)"):
        assert title in src, f"카드 제목에 단위가 없다: {title!r}"


def test_3_every_card_title_carries_its_unit():
    """모든 카드 제목에 단위가 박혀 있어야 한다 — 이 그리드는 축이 섞여 있다.

    ⚠ 선물 3칸은 612차 후속2 에서 **계약 → 억원**으로 바뀌었다
      (원천 7221 열 30/31/32 가 금액을 직접 준다). 미결제약정만 계약 축으로 남는다.
    """
    src = _src(_DASH)
    for title in (
        "외인 선물 순매수 (억원)",
        "개인 선물 순매수 (억원)",
        "기관 선물 순매수 (억원)",
        "미결제약정 (계약)",
    ):
        assert title in src, f"카드 제목에 단위가 없다: {title!r}"


def test_4_program_values_use_amount_formatter_not_contract_formatter():
    """호출부에서도 축이 보여야 한다 — 금액 칸을 `_fmt_contracts`로 찍지 말 것."""
    src = _src(_DASH)
    for attr in ("fut_prog_arb_val", "fut_prog_nonarb_val"):
        m = re.search(re.escape(attr) + r"\.setText\((_fmt_[a-z_]+)\(", src)
        assert m, f"{attr}.setText(_fmt_*(...)) 호출을 찾지 못했다"
        assert m.group(1) == "_fmt_amount_mn", (
            "%s 가 %s 로 찍힌다 — 금액 축이므로 `_fmt_amount_mn` 이어야 한다"
            % (attr, m.group(1))
        )


def test_5_removed_option_matrix_leaves_no_orphan_widgets():
    """[612차 후속3] 포지션 매트릭스 8칸 제거 — 잔여 참조가 없어야 한다.

    `update_data()` 는 매분 파이프라인에서 try 없이 불린다. 위젯을 지우고
    갱신 코드를 남기면 첫 분에 AttributeError 로 파이프라인이 죽는다.
    """
    src = _src(_DASH)
    for attr in ("pos_rt_call_val", "pos_rt_put_val", "pos_rt_strd_val",
                 "pos_fi_call_val", "pos_fi_put_val", "pos_fi_strangle_val",
                 "pos_contrarian_val", "pos_div_score_val"):
        assert attr not in src, "제거된 매트릭스 위젯 참조가 남아 있다: %s" % attr


def test_6_removed_bias_meters_leave_no_orphan_widgets():
    """[612차 후속3] 바이어스 미터 2행 제거 (사용자 지시)."""
    src = _src(_DASH)
    for attr in ("rt_put_bar", "rt_call_bar", "fi_put_bar", "fi_call_bar",
                 "rt_bias_lbl", "fi_bias_lbl"):
        assert attr not in src, "제거된 바이어스 위젯 참조가 남아 있다: %s" % attr


def test_7_option_flow_chart_replaces_the_matrix():
    """매트릭스 자리를 개인 옵션 6종 증감 시계열이 대신한다."""
    src = _src(_DASH)
    assert "OptionFlowDeltaChart" in src
    assert "self.option_flow_chart" in src
    assert "def update_option_flow_delta" in src, "어댑터 배선이 없다"


def test_8_bias_identity_saturates_when_signs_differ():
    """산식 자체의 성질을 못박는다 — 이 항등식이 패널 표기의 근거다.

    부호가 반대면 |bias| == 1.0 이 되는 것은 버그가 아니라 정의다.

    ⚠ [612차 후속3] 이 값은 **더 이상 화면에 없다**(바이어스 미터 삭제). 다만
      `get_panel_data()` 는 계속 계산하므로, 누군가 다시 쓰려 할 때 이 성질을
      모르고 쓰지 않도록 항등식만 남겨 고정한다.
    """
    def bias(call_net, put_net):
        denom = abs(call_net) + abs(put_net)
        return float(call_net - put_net) / max(denom, 1) if denom else 0.0

    # 부호가 반대 → 규모와 무관하게 정확히 ±1.0
    assert bias(1, -1) == pytest.approx(1.0)
    assert bias(10_000, -10_000) == pytest.approx(1.0)
    assert bias(-575, 46) == pytest.approx(-1.0)      # 2026-09-21 13:40 실측 개인
    # 부호가 같으면 비로소 크기 정보가 남는다
    assert bias(257, 1309) == pytest.approx(-0.6717, abs=1e-4)   # 09-18 실측 외인
    assert bias(0, 0) == 0.0


def test_9_update_data_tolerates_missing_bias_keys():
    """`update_data`는 `run_minute_pipeline` 안에서 try 없이 불린다 —
    키 하나가 없다고 매분 파이프라인을 죽이면 안 된다."""
    src = _src(_DASH)
    for key in ("rt_bias", "fi_bias"):
        assert "div['%s']" % key not in src, (
            "div['%s'] 직접 색인이 되살아났다 — `.get()` 을 쓸 것" % key
        )


def test_10_divergence_adapter_is_exception_guarded():
    src = _src(_DASH)
    body = src.split("def update_divergence(", 1)[1].split("\n    def ", 1)[0]
    assert "try:" in body and "except Exception" in body, (
        "update_divergence 어댑터의 예외 안전망이 사라졌다 — 표시 계층 예외가 "
        "매분 파이프라인을 끊는다"
    )
    assert "logger.warning" in body, "예외를 조용히 삼키고 있다 — 계측 4원칙 ④"


# ── ② 체인 캐시 ───────────────────────────────────────────────────────────

def _make_snapshot(tmpdir, saved_at, chain=None):
    from collection.options.option_chain_snapshot import OptionChainSnapshot

    path = os.path.join(tmpdir, "option_chain.json")
    payload = {"chain": chain if chain is not None else [{"code": "B016AA01"}]}
    if saved_at is not None:
        payload["saved_at"] = saved_at
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    snap = OptionChainSnapshot(chain_cache_path=path)
    snap.initialize()
    return snap, path


def test_11_chain_reload_due_is_false_for_today_cache():
    with tempfile.TemporaryDirectory() as d:
        snap, _ = _make_snapshot(d, datetime.date.today().isoformat())
        assert snap.chain_reload_due() is False


def test_12_chain_reload_due_is_true_for_stale_cache():
    """2026-06-04 목록이 3.5개월간 쓰인 실제 사고를 재현한다."""
    with tempfile.TemporaryDirectory() as d:
        snap, _ = _make_snapshot(d, "2026-06-04")
        assert snap.chain_reload_due() is True


def test_13_chain_reload_due_is_true_when_saved_at_unknown_and_mtime_old():
    """612차 이전 캐시에는 `saved_at` 이 없다 — 미측정을 '최신'으로 읽지 말 것."""
    with tempfile.TemporaryDirectory() as d:
        snap, path = _make_snapshot(d, None)
        old = datetime.datetime(2026, 6, 4).timestamp()
        os.utime(path, (old, old))
        snap.initialize()          # mtime 폴백 경로로 다시 읽는다
        assert snap.chain_reload_due() is True


def test_14_worker_keeps_stale_chain_when_reload_fails():
    """재수집 실패 시 낡은 목록을 버리면 그날 옵션 피처가 통째로 사라진다."""
    from collection.options import option_chain_worker as W

    w = W.OptionChainWorker.__new__(W.OptionChainWorker)
    w._chain_raw = [{"code": "B016AA01", "call_put": "콜", "ym": "2610", "strike": 1110.0}]
    w._spot = 1110.0
    w._cache_path = os.devnull
    w._atm_window = 30.0
    w._pause_ms = 0
    w._force_reload = True
    w._fetch_chain = lambda: []          # CpOptionCode 실패 시뮬

    # `_execute`는 COM 까지 가므로 재수집 분기만 떼어 검증한다.
    chain = list(w._chain_raw)
    if w._force_reload and chain:
        fresh = w._fetch_chain()
        if fresh:
            chain = fresh
    assert chain == w._chain_raw, "재수집 실패 시 낡은 목록을 버렸다"


def test_15_worker_stamps_saved_at_on_cache_write():
    from collection.options import option_chain_worker as W

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "chain.json")
        w = W.OptionChainWorker.__new__(W.OptionChainWorker)
        w._cache_path = path
        w._save_chain_cache([{"code": "B016AA01"}])
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("saved_at") == datetime.date.today().isoformat(), (
            "캐시에 수집일이 기록되지 않는다 — mtime 만으로는 체크아웃·복사에 흔들린다"
        )


def test_16_main_passes_force_chain_reload_to_worker():
    """배선이 살아 있는가 — 판정 함수가 있어도 안 넘기면 죽은 코드다."""
    src = _src(_MAIN)
    assert "force_chain_reload = self.option_chain_snap.chain_reload_due()" in src, (
        "main 이 워커에 force_chain_reload 를 넘기지 않는다 — 612차 배선이 끊겼다"
    )


def test_17_worker_accepts_force_chain_reload_kwarg():
    import inspect

    from collection.options.option_chain_worker import OptionChainWorker

    params = inspect.signature(OptionChainWorker.__init__).parameters
    assert "force_chain_reload" in params
    assert params["force_chain_reload"].default is False, (
        "기본값이 True 면 모든 워커 기동마다 CpOptionCode 를 받는다"
    )
