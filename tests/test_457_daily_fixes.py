# -*- coding: utf-8 -*-
"""457차 — 0811 일일점검 Fix 회귀 테스트 (W-A ~ W-E).

배경: `docs/정기점검/매일점검/MW0601-20260811-점검리포트.md` §2,
      실행 파동 W-A(C5·C6) / W-B(B1·B2) / W-C(C1·C2) / W-E(C3·C4).

여기서 검증하는 것은 **"폴백이 정상값처럼 보이던 결함"** 4종과 모델 로드
스테이징 분리다. 라이브 파이프라인 전체를 띄우지 않고 각 단위의 불변식만 본다.
"""
import json
import os
import pickle
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── C6: FeatureReg 미가용 목록 무표식 절단 ──────────────────────────────────

def test_featurereg_logs_all_missing_features(caplog):
    """30m 실측 재현 — "7개 미가용"인데 5개만 출력되던 결함.

    2026-08-11 EOD 로그:
        [FeatureReg] 30m: 7개 피처 미가용 → 제외: [5개만]
    30m desired 18개 중 11개 선택 = 정확히 7개 missing. `missing[:5]` 절단이
    유일한 원인이었고, 은닉된 2개 중에 심사 중인 CORE 후보가 섞일 수 있었다.
    """
    import logging
    from features.horizon_feature_registry import get_available_feature_set, get_feature_set

    desired = get_feature_set("30m")
    if not desired or len(desired) < 8:
        pytest.skip("30m 레지스트리 미구성 — 이 PC에서는 검증 불가")

    # 앞 2개만 가용 → missing = len(desired) - 2 (≥6개)
    available = list(desired[:2])
    with caplog.at_level(logging.INFO, logger="FEAT_REG"):
        get_available_feature_set("30m", available)

    msgs = [r.getMessage() for r in caplog.records if "미가용" in r.getMessage()]
    assert msgs, "미가용 로그가 없다"
    msg = msgs[-1]
    n_missing = len(desired) - 2
    assert "%d개 피처 미가용" % n_missing in msg

    # 절단됐다면 반드시 잔여 개수를 명시해야 한다("외 N개").
    listed = msg.count("'")  // 2  # 따옴표 쌍 = 나열된 이름 수
    if listed < n_missing:
        assert "외 %d개" % (n_missing - listed) in msg, (
            "절단했으면서 표식이 없다 — 운영자가 개수를 오독한다: %s" % msg)


# ── C1: F6 학습행 타임스탬프 — 주입 X 행수 일치 시 보존 ─────────────────────

class _TSKeeper(object):
    """batch_retrainer.retrain()의 ts 처리 분기만 떼어낸 최소 재현.

    실제 retrain()은 DB·모델을 요구해 단위 테스트에 부적합하다. 여기서는 457차 C1이
    바꾼 **분기 조건 자체**를 같은 형태로 재현해 회귀를 잡는다.
    """
    def __init__(self, ts_list):
        self._train_row_ts = ts_list

    def decide(self, X):
        # batch_retrainer.py:541-563 과 동일한 조건
        if not (self._train_row_ts is not None
                and X is not None
                and len(self._train_row_ts) == len(X)):
            self._train_row_ts = None
        return self._train_row_ts


def test_f6_keeps_ts_when_row_count_matches():
    """retrain_eod.py 경로 재현 — _load_from_db 직후 그대로 주입하면 ts가 살아야 한다.

    2026-08-11 EOD 실측: 6/6 호라이즌이 "학습행 타임스탬프 미상(외부 주입 X 경로)"로
    판정 보류. 같은 인스턴스가 방금 채운 ts를 스스로 버린 것이 원인이었다.
    """
    ts = ["2026-08-11 09:0%d:00" % i for i in range(5)]
    k = _TSKeeper(list(ts))
    assert k.decide(list(range(5))) == ts, "행 수가 같은데 ts를 버렸다 (F6 무력화)"


def test_f6_drops_ts_when_row_count_differs():
    """진짜 외부 데이터(행 수 불일치)는 종전대로 폐기 — "모름"을 "깨끗함"으로 읽지 않는다."""
    k = _TSKeeper(["a", "b", "c"])
    assert k.decide(list(range(7))) is None, "정렬 미상인데 ts를 유지했다 (F6 원칙 위반)"


def test_f6_drops_ts_when_none():
    k = _TSKeeper(None)
    assert k.decide(list(range(3))) is None


# ── C2: F7 유령 기준선 정책 ─────────────────────────────────────────────────

def test_ghost_policy_is_replace():
    """0811 사용자 결정 = ⑤안(교체 허용). 되돌리려면 이 테스트도 함께 고칠 것."""
    from config.settings import EOD_GUARD_GHOST_POLICY
    assert EOD_GUARD_GHOST_POLICY in ("replace", "hold")
    assert EOD_GUARD_GHOST_POLICY == "replace", (
        "457차 결정은 ⑤안(replace)이다. 'hold'로 되돌리면 3m 교체가 다시 막힌다 "
        "(2026-08-03~08-11 7거래일 연속 보류 실적)")


def test_ghost_bypass_branch_is_after_guard_fair():
    """분기 순서 불변식 — guard_fair가 유령 우회보다 **먼저** 와야 한다.

    guard_fair는 배포본을 직접 채점하므로 유령 문제 자체가 성립하지 않는다.
    순서가 뒤집히면 더 정확한 판정이 있는데도 가드를 건너뛰게 된다.
    """
    src = open(os.path.join(_ROOT, "learning", "batch_retrainer.py"),
               encoding="utf-8").read()
    i_fair = src.find('_verdict_src = "guard_fair"')
    i_ghost = src.find('_verdict_src = "ghost_bypass"')
    i_acc = src.find('_verdict_src = "acc_txt"')
    assert -1 not in (i_fair, i_ghost, i_acc), "판정 소스 분기가 사라졌다"
    assert i_fair < i_ghost < i_acc, (
        "분기 순서가 guard_fair → ghost_bypass → acc_txt 여야 한다")


# ── B1: 모델 로드 스테이징 분리 ─────────────────────────────────────────────

def test_multi_horizon_stage_reload_does_not_mutate(tmp_path, monkeypatch):
    """stage_reload()는 self를 건드리지 않아야 한다 (워커 스레드에서 호출되므로)."""
    import model.multi_horizon_model as mm

    monkeypatch.setattr(mm, "HORIZON_DIR", str(tmp_path))
    monkeypatch.setattr(mm, "SCALER_DIR", str(tmp_path))
    monkeypatch.setattr(mm, "HORIZONS", {"1m": 1})

    m = mm.MultiHorizonModel.__new__(mm.MultiHorizonModel)
    m.models, m.scalers, m._is_fitted = {}, {}, {}
    m._scaler_fitted_at, m.horizon_feature_names = {}, {}
    m.feature_names = ["keep_me"]

    # 공유 피처명 pkl만 둔다 — 모델/스케일러 pkl은 없음
    import joblib
    joblib.dump(["a", "b"], os.path.join(str(tmp_path), "feature_names.pkl"))

    staged = m.stage_reload()

    assert staged["feature_names"] == ["a", "b"]
    assert m.feature_names == ["keep_me"], "stage_reload()가 self를 변경했다"
    assert m.models == {}, "stage_reload()가 self.models를 변경했다"


def test_rf_stage_load_does_not_mutate(tmp_path, monkeypatch):
    import model.rf_horizon_model as rm

    r = rm.RFHorizonModel.__new__(rm.RFHorizonModel)
    r._dir = str(tmp_path)
    r._models, r._oob, r.feature_names, r._ready = {}, {}, ["old"], False

    payload = {"models": {"1m": object()}, "oob": {"1m": 0.5},
               "feature_names": ["new"]}
    with open(os.path.join(str(tmp_path), rm.RFHorizonModel.MODEL_FILE), "wb") as f:
        pickle.dump(payload, f)

    got = r.stage_load()
    assert got["feature_names"] == ["new"]
    assert r.feature_names == ["old"], "stage_load()가 self를 변경했다"


def test_rf_stage_load_missing_file_returns_none(tmp_path):
    import model.rf_horizon_model as rm
    r = rm.RFHorizonModel.__new__(rm.RFHorizonModel)
    r._dir = str(tmp_path)
    assert r.stage_load() is None
    # apply_staged(None)은 조용히 False — 라이브 상태를 지우면 안 된다
    r._models, r._oob, r.feature_names, r._ready = {"1m": 1}, {}, ["x"], True
    assert r.apply_staged(None) is False
    assert r._models == {"1m": 1}, "빈 payload로 라이브 모델을 지웠다"


# ── B1/B2: 비동기 토글이 config에 존재하고 롤백 가능한가 ────────────────────

@pytest.mark.parametrize("name", ["SHAP_ASYNC_ENABLED", "MODEL_RELOAD_ASYNC_ENABLED"])
def test_async_toggles_exist(name):
    import config.settings as S
    assert isinstance(getattr(S, name), bool), (
        "%s 는 롤백 스위치다 — bool로 유지할 것" % name)


# ── C3·C4: 진입 호라이즌 속성이 실제로 할당되는가 ───────────────────────────

def test_entry_horizon_attrs_are_assigned_somewhere():
    """`getattr(self, "_entry_horizon*", "1m")` 폴백이 영구 고정되지 않도록.

    2026-08-11 실측: `ensemble_decisions.meta_gate_horizon` 370/370건이 '1m'인데
    실제 진입은 3m·3m·5m. 읽는 곳만 있고 **할당부가 0개**였던 것이 원인이다.
    """
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    for attr in ("_entry_horizon_pre", "_entry_horizon"):
        assigns = src.count("self.%s = " % attr)
        assert assigns >= 1, (
            "self.%s 에 할당하는 코드가 없다 — getattr 폴백 '1m'이 영구 고정된다" % attr)


def test_entry_horizon_pre_uses_selector():
    """선행값이 select_entry_horizon()에서 나와야 한다 (하드코딩 금지)."""
    src = open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()
    i = src.find("self._entry_horizon_pre = select_entry_horizon(")
    assert i != -1, "선행 호라이즌이 라우터를 거치지 않는다"


# ── A3 전제 검증: 수수료는 레그 분할과 무관하다 ─────────────────────────────

def test_commission_is_leg_split_invariant():
    """0811 리포트 §2 A3의 전제("부분청산이 수수료를 2배화")가 **거짓**임을 고정한다.

    수수료 = entry_price × quantity × pt_value × RATE × 2 이므로 계약수에만
    비례한다. 이 불변식이 깨지면(예: 레그당 고정비 도입) cost_edge_watch 채널의
    설계 전제가 바뀌므로 여기서 잡는다.
    """
    from utils.db_utils import normalize_trade_pnl

    px, pv = 966.07, 50_000
    split = sum(normalize_trade_pnl(entry_price=px, quantity=1, pnl_pts=0.0,
                                    pt_value=pv)["commission_krw"] for _ in range(2))
    single = normalize_trade_pnl(entry_price=px, quantity=2, pnl_pts=0.0,
                                 pt_value=pv)["commission_krw"]
    assert abs(split - single) < 1.0, (
        "레그 분할이 수수료를 바꾼다 — cost_edge_watch 전제 재검토 필요 "
        "(split=%.0f single=%.0f)" % (split, single))


# ── A3: 사전등록 채널이 존재하고 필수 키를 갖췄는가 ─────────────────────────

def test_cost_edge_watch_preregistered():
    from config.settings import VALIDATION_CAMPAIGN
    cfg = VALIDATION_CAMPAIGN.get("cost_edge_watch")
    assert cfg, "cost_edge_watch 채널이 사라졌다"
    for k in ("min_samples", "min_days", "rho_threshold", "t_threshold",
              "tercile_gap_pp_supports", "tercile_gap_pp_rejects", "data_start"):
        assert k in cfg, "사전등록 키 누락: %s" % k
    assert cfg["tercile_gap_pp_rejects"] < cfg["tercile_gap_pp_supports"], (
        "REJECTS 문턱이 SUPPORTS보다 크면 두 판정이 동시에 성립한다")
