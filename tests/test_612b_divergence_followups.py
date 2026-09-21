# tests/test_612b_divergence_followups.py
"""[MW0601 612차 후속] 다이버전스 탭 잔여 항목 회귀 가드.

1차(`test_612_divergence_panel_units.py`)가 단위·체인캐시·바이어스 3건을 고정했다.
이 파일은 그때 「미처리」로 남겼던 나머지를 고정한다:

  P0-A  GEX 100배 (OptionMst Greeks 는 백분율인데 ÷100 이 없었다)
  P0-B  「5분 폴링」이 실제로는 대개 10분이던 경계 레이스
  P0-C  수급 카드 age·stale 미표시 + 559차 `*_measured` 패널 미배선
  P1    라벨(체인 PCR 범위 · 순매수 비중 · 콜·풋 합계 · TR 오기 · 영문) · 중복 호출
  P2    죽은 임계 3종(감마 배지 · 다이버전스 중립대 · 역발상 데드밴드)
  P3-J  ATM 기준가를 선물가 → 현물지수

소스와 순수 로직만 검사한다 — PyQt 위젯을 띄우지 않는다(1차와 같은 이유).
"""
from __future__ import annotations

import datetime
import json
import math
import os

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DASH = os.path.join(_ROOT, "dashboard", "main_dashboard.py")
_SNAP = os.path.join(_ROOT, "collection", "options", "option_chain_snapshot.py")
_WORK = os.path.join(_ROOT, "collection", "options", "option_chain_worker.py")
_INV = os.path.join(_ROOT, "collection", "cybos", "investor_data.py")
_MAIN = os.path.join(_ROOT, "main.py")
_METRICS = os.path.join(_ROOT, "scripts", "collect_option_metrics.py")
_BACKFILL = os.path.join(_ROOT, "scripts", "gex_scale_backfill_612.py")


def _src(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ── P0-A: GEX ÷100 ────────────────────────────────────────────────────────

def test_1_gamma_divided_by_percent_scale():
    """OptionMst Greeks 는 백분율 — 249차 이래 ÷100 이 빠져 GEX 가 100배였다."""
    src = _src(_WORK)
    assert "_GREEK_PCT = 100.0" in src
    assert "GetHeaderValue(_HV_GAMMA)) / _GREEK_PCT" in src, (
        "gamma 를 백분율에서 환산하지 않는다 — GEX 가 100배가 된다"
    )


def test_2_reference_script_matches_production_scale():
    """진단 스크립트가 프로덕션과 다른 스케일이면 대조가 무의미해진다."""
    src = _src(_METRICS)
    assert "GREEK_PCT = 100.0" in src
    for hv in ("HV_DELTA", "HV_GAMMA"):
        assert "GetHeaderValue(%s)) / GREEK_PCT" % hv in src, (
            "%s 가 백분율 환산 없이 저장된다" % hv
        )


def test_3_percent_scale_evidence_still_holds():
    """근거 재계산 — `data/option_metrics.json`(정정 전 세대)이 증거 파일이다.

    delta 범위가 0~100 축이면 Greeks 는 백분율이고, ATM gamma 는 BS 이론의 약 100배여야
    한다. 파일이 없거나 이미 정정 후 세대로 교체됐으면 skip.
    """
    p = os.path.join(_ROOT, "data", "option_metrics.json")
    if not os.path.exists(p):
        pytest.skip("option_metrics.json 없음 (증거 파일)")
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    sn = d.get("snapshots") or []
    if not sn:
        pytest.skip("스냅샷 없음")
    if max(abs(s.get("delta", 0)) for s in sn) <= 1.5:
        pytest.skip("정정 후 세대 파일 — 백분율 증거 대상 아님")

    spot = d["result"]["atm"]["atm_spot"]
    atm = min(sn, key=lambda x: abs(x.get("strike", 0) - spot))
    T = atm["dte"] / 365.0
    sigma = atm["iv"] / 100.0
    theory = 1.0 / (spot * sigma * math.sqrt(2 * math.pi * T))
    ratio = atm["gamma"] / theory
    assert 50 < ratio < 200, (
        "ATM gamma/이론 비율이 %.1f — 100배 가설과 맞지 않는다. ÷100 근거 재검토" % ratio
    )


def test_4_divide_is_linear_so_rank_metrics_unchanged():
    """오해 방지를 코드로 — ÷100 은 순위상관을 바꾸지 않는다.

    「GEX IC 0.198 → 0.013 재현 실패(F4)의 원인이 이 버그」라고 쓰면 틀린다.
    """
    xs = [0.15, 3.7, 288.0, 3718.0, 0.0015, 92.5]
    ys = [x / 100.0 for x in xs]
    assert [sorted(xs).index(v) for v in xs] == [sorted(ys).index(v) for v in ys]


# ── P0-B: 폴링 주기 ───────────────────────────────────────────────────────

def test_5_is_due_uses_monotonic_with_tolerance():
    src = _src(_SNAP)
    assert "time.monotonic()" in src, "시스템 시계(time.time)는 NTP 보정에 흔들린다"
    assert "_DUE_TOLERANCE_SEC" in src, (
        "여유 없는 `>= interval` 비교는 타이머 지터로 한 틱을 통째로 버린다 "
        "— 실측 2026-09-21 간격 31개 중 10분이 16개였다"
    )
    assert "self._last_refresh = time.monotonic()" in src, (
        "mark_refresh_started 와 is_due 가 다른 시계를 쓰면 경과시간이 어긋난다"
    )


def test_6_is_due_fires_on_slightly_early_tick():
    """경계 레이스 재현 — 299.99초에 스킵하면 다음 기회가 300초 뒤다."""
    import time as _t

    from collection.options.option_chain_snapshot import OptionChainSnapshot

    snap = OptionChainSnapshot(chain_cache_path=os.devnull)
    snap._ready = True
    snap._last_refresh = _t.monotonic() - 299.99
    assert snap.is_due(1110.0) is True
    snap._last_refresh = _t.monotonic() - 10.0
    assert snap.is_due(1110.0) is False, "10초 만에 재기동하면 안 된다"
    snap._last_refresh = 0.0
    assert snap.is_due(1110.0) is True, "한 번도 안 돌았으면 즉시 떠야 한다"
    assert snap.is_due(0.0) is False, "spot 미확정이면 뜨면 안 된다"


def test_7_panel_interval_injected_not_hardcoded():
    assert "def set_chain_interval" in _src(_DASH)
    assert "def set_option_chain_interval" in _src(_DASH)
    assert "self.option_chain_snap.interval_sec" in _src(_MAIN), (
        "main 이 실제 주기를 패널에 주지 않는다 — 게이지가 300초를 계속 가정한다"
    )


def test_8_poll_skip_is_visible_in_logs():
    """어느 분기가 반환했는지 로그로 판정되게 한다(계측 4원칙 ③)."""
    body = _src(_MAIN).split("def _poll_option_chain", 1)[1][:2600]
    assert "optchain_not_due" in body, "폴링 스킵이 여전히 보이지 않는다"
    assert "logger.debug(\"[OptionChain] 이전 워커 실행 중" not in body, (
        "워커 중복 스킵이 debug 라 파일에 안 남는다"
    )


# ── P0-C: age·stale·measured ──────────────────────────────────────────────

def test_9_panel_data_carries_freshness_and_measured():
    src = _src(_INV)
    for key in ('"age_sec"', '"stale"',
                '"foreign_futures_net_measured"',
                '"retail_futures_net_measured"',
                '"institution_futures_net_measured"'):
        assert key in src, "get_panel_data 가 %s 를 싣지 않는다" % key


def test_10_panel_renders_age_and_waits_on_unmeasured():
    src = _src(_DASH)
    assert "fut_age_lbl" in src, "신선도 칩이 없다 — 멈춘 값이 살아 있는 값으로 보인다"
    assert 'div.get("age_sec")' in src
    assert 'div.get(key + "_measured")' in src, (
        "559차 measured 플래그가 패널에 배선되지 않았다 — "
        "프리장 미수신과 실측 0계약이 구분되지 않는다"
    )


# ── P2: 죽은 임계 3종 ─────────────────────────────────────────────────────

def test_11_gamma_badge_is_adaptive_not_fixed_bn():
    src = _src(_DASH)
    assert "_GEX_FLIP_THRESHOLD" not in src, (
        "고정 B값 임계가 되살아났다 — GEX 는 만기 잔존일에 따라 수천 배 변한다 "
        "(실측 09-10 만기일 37B vs 09-15 0.0015B)"
    )
    for k in ("_GEX_FLIP_MEDIAN_RATIO", "_GEX_FLIP_MIN_SAMPLES", "_GEX_FLIP_BOOTSTRAP_BN"):
        assert k in src, "%s 가 없다" % k
    assert "_GEX_FLIP_PCTL" not in src, (
        "분위수(p25) 규칙이 되살아났다 — 정의상 매일 25%가 플립이 된다. "
        "test_12b 참조"
    )


def test_12_gamma_flip_threshold_tracks_today_distribution():
    from dashboard.main_dashboard import DashboardAdapter

    a = DashboardAdapter.__new__(DashboardAdapter)
    thr, n, boot = a._gex_flip_threshold(2.0)
    assert boot is True and n == 1
    assert thr == DashboardAdapter._GEX_FLIP_BOOTSTRAP_BN
    # 평탄한 날(전부 3B 근방) — 경계는 그날 중앙값의 25% 로 내려간다
    for v in (2.88, 3.26, 2.98, 3.20, 3.19, 3.03, 2.99):
        thr, n, boot = a._gex_flip_threshold(v)
    assert boot is False, "표본이 쌓였는데도 부트스트랩에 머문다"
    assert thr == pytest.approx(0.25 * 3.03, abs=0.05), (
        "경계가 당일 중앙값의 25%%가 아니다 (thr=%.3f)" % thr
    )
    assert 2.98 > thr, "평탄한 날의 전형값이 감마플립으로 잡히면 안 된다"


def test_12b_percentile_rule_is_rejected_by_measurement():
    """왜 분위수(p25)를 쓰지 않는가 — 정의상 매일 25%가 플립이 된다.

    33거래일 실측에서 p25 규칙의 일별 플립 비율은 25.5~32.4%로 고정됐고,
    2026-09-10 월물 만기일(중앙값 25.7B)에는 **19.0B 를 「중립선 근접」**이라
    불렀다. 분포의 하위 25%와 "0 에 가깝다"는 다른 말이다.
    """
    from dashboard.main_dashboard import DashboardAdapter

    a = DashboardAdapter.__new__(DashboardAdapter)
    expiry_day = [25.7, 26.1, 24.9, 19.0, 28.3, 22.4, 27.0, 25.1]
    for v in expiry_day:
        thr, _n, _boot = a._gex_flip_threshold(v)
    assert 19.0 > thr, (
        "만기일 19.0B 가 감마플립으로 잡힌다 — p25 규칙의 실패 양상이다 (thr=%.3f)" % thr
    )
    assert sum(1 for v in expiry_day if v <= thr) == 0, "평탄한 날 플립은 0건이어야 한다"


def test_12c_flip_fires_when_gex_actually_collapses():
    """GEX 가 실제로 0 으로 붕괴한 날은 발화해야 한다 — 2026-09-15 실측 형태."""
    from dashboard.main_dashboard import DashboardAdapter

    a = DashboardAdapter.__new__(DashboardAdapter)
    day = [0.60, 0.42, 0.31, 0.17, 0.064, 0.02, 0.0015, 0.21]
    for v in day:
        thr, _n, _boot = a._gex_flip_threshold(v)
    fired = [v for v in day if v <= thr]
    assert fired, "GEX 가 붕괴한 날인데 플립이 한 번도 안 뜬다 (thr=%.4f)" % thr
    assert 0.0015 in fired


def test_13_gamma_sample_buffer_resets_on_new_day():
    from dashboard.main_dashboard import DashboardAdapter

    a = DashboardAdapter.__new__(DashboardAdapter)
    for v in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
        a._gex_flip_threshold(v)
    a._gex_day = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    _thr, n, boot = a._gex_flip_threshold(3.0)
    assert n == 1 and boot is True, "거래일이 바뀌면 표본을 다시 모아야 한다"


def test_14_gamma_buffer_is_not_read_via_getattr_default():
    """계측 4원칙 ④ / test_457 — 런타임 상태를 getattr 기본값으로 읽지 않는다."""
    from dashboard.main_dashboard import DashboardAdapter

    assert hasattr(DashboardAdapter, "_gex_day")
    assert hasattr(DashboardAdapter, "_gex_samples")
    src = _src(_DASH)
    assert 'getattr(self, "_gex_samples"' not in src
    assert 'getattr(self, "_gex_day"' not in src


def test_15_div_neutral_band_removed_with_its_card():
    """[612차 후속3] 「다이버전스」 카드 제거 → 중립대 상수도 함께 없앤다.

    카드 없는 임계는 죽은 코드다(451차 계열). 카드를 되살릴 일이 생기면
    612차 후속의 실측 근거(39거래일 n=12,031, |div| p25=1,059)를 다시 쓴다.
    """
    from dashboard.main_dashboard import DivergencePanel

    assert not hasattr(DivergencePanel, "_DIV_NEUTRAL_BAND"), (
        "카드가 없는데 임계 상수만 남았다"
    )
    src = _src(_DASH)
    assert "score > 10 " not in src and "score < -10 " not in src


def test_16_contrarian_has_deadband():
    from collection.cybos.investor_data import CONTRARIAN_DEADBAND_CONTRACTS

    assert CONTRARIAN_DEADBAND_CONTRACTS == 200
    src = _src(_INV)
    assert "retail_fut > CONTRARIAN_DEADBAND_CONTRACTS" in src
    assert "retail_fut < -CONTRARIAN_DEADBAND_CONTRACTS" in src


def test_17_deadband_suppresses_observed_noise_flips():
    """실측 노이즈 대역(09-21 개인 선물 −213~+228)에서 중립이 나와야 한다."""
    from collection.cybos.investor_data import CONTRARIAN_DEADBAND_CONTRACTS as DB

    def verdict(rt):
        if rt > DB:
            return "개인 매수 우위"
        if rt < -DB:
            return "개인 매도 우위"
        return "중립"

    assert verdict(150) == "중립"
    assert verdict(-180) == "중립"
    assert verdict(893) == "개인 매수 우위"      # 09-18 실측 최대
    assert verdict(-1187) == "개인 매도 우위"    # 09-15 실측 최소


# ── P1: 라벨 · 중복 호출 ──────────────────────────────────────────────────

def test_18_straddle_language_never_returns():
    """[612차 후속3] 「양매수/양매도」 카드는 매트릭스와 함께 제거됐다.

    되살아나더라도 그 이름으로는 안 된다 — `|콜 net| + |풋 net|` 는
    스트래들/스트랭글 포지션이 아니고 gross 거래대금도 아니다.
    """
    src = _src(_DASH)
    assert '"개인 양매수"' not in src and '"외인 양매도"' not in src


def test_19_chain_pcr_label_states_actual_scope():
    src = _src(_DASH)
    assert "근월 ATM±30pt PCR" in src, (
        "'체인 PCR' 은 전체 체인이 아니라 _filter_atm 후 24종목의 PCR 이다"
    )
    assert '"옵션 구간별 거래량 (ITM·ATM·OTM)"' not in src, (
        "값은 거래량이 아니라 투자자별 순매수 절대값 비중이다"
    )


def test_20_tr_name_typo_fixed():
    for p in (_DASH, _INV):
        assert "CpSvrNew7212" not in _src(p), (
            "%s 에 TR 오기가 남아 있다 — 운영 TR 은 CpSvrNew7221 이다" % os.path.basename(p)
        )


def test_21_divergence_pushed_once_per_minute():
    """중복 호출 제거 — 첫 dict 가 즉시 덮어써지며 한 프레임 오표시를 만들었다."""
    body = _src(_MAIN).split("# 다이버전스 패널 갱신", 1)[1][:3000]
    assert body.count("self.dashboard.update_divergence(") == 2, (
        "호출이 2개(정상 경로 + get_panel_data 없는 폴백)가 아니다"
    )
    assert 'if hasattr(_inv, "get_panel_data"):' in body
    assert "\n        else:" in body, "폴백은 else 분기여야 한다 — 둘 다 보내면 종전과 같다"


def test_22_status_text_is_korean():
    src = _src(_INV)
    assert "Cybos futures/program investor flow live" not in src
    assert "선물·프로그램·옵션 수급 정상 수신 중" in src


# ── P3-J: ATM 기준가 ──────────────────────────────────────────────────────

def test_23_option_chain_uses_index_spot_with_visible_fallback():
    body = _src(_MAIN).split("def _poll_option_chain", 1)[1][:2600]
    assert "spot = self._last_kospi200_spot" in body, (
        "ATM 기준가가 선물 종가로 되돌아갔다 — 행사가는 현물지수 기준이다"
    )
    assert "optchain_spot_fallback" in body, (
        "폴백이 쓰였는지 로그로 알 수 없다 — 계측 4원칙 ④"
    )


# ── 백필 스크립트 ─────────────────────────────────────────────────────────

def test_24_backfill_guards_intraday_and_backs_up():
    src = _src(_BACKFILL)
    assert "guard_intraday(" in src, "장중 전수 스캔은 CB⑤ 자가유발이다(456차)"
    assert "shutil.copy2" in src, "백업 없이 소급 UPDATE 하면 안 된다"
    assert "METRIC_REDEFINITION" in src, "불연속 마커가 없다(461차 교훈)"
    assert "opt_gex_sign" in src, "부호 키는 건드리지 않는다는 명시가 필요하다"


def test_25_backfill_only_touches_gex_key():
    """JSON 블롭을 되쓰는 스크립트다 — 다른 키를 건드리면 안 된다."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("_bf612", _BACKFILL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.KEY == "opt_gex_bn"
    assert mod.FACTOR == 100.0

    row = {"opt_gex_bn": 288.26, "opt_gex_sign": 1.0,
           "opt_chain_pcr": 0.376, "atr": 1.03}
    fixed = dict(row)
    fixed[mod.KEY] = round(float(fixed[mod.KEY]) / mod.FACTOR, 6)
    assert fixed["opt_gex_bn"] == pytest.approx(2.8826)
    for k in ("opt_gex_sign", "opt_chain_pcr", "atr"):
        assert fixed[k] == row[k], "%s 가 바뀌었다" % k


# ── [612차 후속2] 선물 수급 금액(억원) 축 ─────────────────────────────────

_API = os.path.join(_ROOT, "collection", "cybos", "api_connector.py")


def test_26_api_extracts_amount_columns():
    """7221 선물 행 열 30/31/32 = 개인/외인/기관 순매수 금액(백만원)."""
    src = _src(_API)
    # [612차 후속4] `r.get(col, 0)` → 열 존재 확인 후 대입으로 바뀌었다.
    # 없는 열을 0 으로 지어내면 `*_measured` 가 True 로 위장된다.
    assert '(("individual", 30), ("foreign", 31),' in src
    assert '("institution", 32))' in src
    assert "if _col in r:" in src
    assert '"net_amounts": net_amounts,' in src, "반환 dict 에 안 실렸다"


def test_27_amount_axis_has_its_own_measured_flag():
    """7221 이외 후보는 이 열을 안 준다 — 계약수 플래그와 뭉뚱그리면 안 된다."""
    src = _src(_INV)
    assert "_futures_amt_seen" in src
    assert "def _is_amt_measured" in src
    for k in ('"foreign_futures_amt_mn"', '"retail_futures_amt_mn"',
              '"institution_futures_amt_mn"', '"foreign_futures_amt_measured"'):
        assert k in src, "get_panel_data 가 %s 를 싣지 않는다" % k


def test_28_panel_cards_show_eok_not_contracts():
    src = _src(_DASH)
    for t in ("외인 선물 순매수 (억원)", "개인 선물 순매수 (억원)",
              "기관 선물 순매수 (억원)"):
        assert t in src, "카드 제목이 억원 축이 아니다: %s" % t
    assert "def _fmt_eok" in src
    assert '_fmt_eok(fi_amt) if _measured("foreign_futures_amt")' in src, (
        "금액 미측정 시 계약수로 대체하면 축이 섞인다"
    )
    # [612차 후속3] 다이버전스 카드는 제거됐다 — 축 혼동 대상 자체가 사라졌다.
    assert "다이버전스 (계약)" not in src


def test_29_amount_axis_roundtrip_matches_source():
    """실측 RAW(2026-09-21 14:25:58 선물 행)를 그대로 태워 화면값까지 확인한다."""
    from collection.cybos.investor_data import CybosInvestorData

    class _Api(object):
        def request_investor_futures(self):
            return {"supported": True, "source": "CpSysDib.CpSvrNew7221",
                    "reason": "probe ok",
                    "nets": {"individual": -185, "foreign": 4654,
                             "institution": -4531},
                    "net_amounts": {"individual": -51528, "foreign": 1294497,
                                    "institution": -1260062},
                    "call_nets": {}, "put_nets": {}, "raw": {"open_interest": 0}}

    inv = CybosInvestorData(_Api())
    inv.fetch_futures_investor()
    d = inv.get_panel_data()
    assert d["foreign_futures_amt_mn"] == 1294497
    assert d["foreign_futures_net"] == 4654, "계약수 키는 그대로 남아야 한다"
    assert d["foreign_futures_amt_measured"] is True
    # 백만원 → 억원
    assert round(d["foreign_futures_amt_mn"] / 100.0) == 12945


def test_30_amount_consistency_recon_passes_on_real_data():
    """금액 ÷ 계약 ≈ 지수 × 250,000 (정규 승수) — 열 매핑 대사."""
    from collection.cybos.investor_data import CybosInvestorData

    inv = CybosInvestorData()
    inv._futures_supported = True
    inv._futures.update({"foreign": 4654, "individual": -185,
                         "institution": -4531})
    inv._futures_amt.update({"foreign": 1294497, "individual": -51528,
                             "institution": -1260062})
    mult = inv.check_amount_consistency(1110.0)
    assert mult == pytest.approx(277.5, abs=3.0), (
        "실측 배수 %.1f 가 지수×250,000(=277.5 백만원)과 어긋난다" % mult
    )


def test_31_amount_consistency_recon_warns_on_broken_mapping():
    """열이 밀리면 조용히 틀린 억원이 나가지 않고 경고가 떠야 한다.

    ⚠ `utils/logger.py` 의 레이어 로거는 `propagate=False` 라 pytest `caplog` 가
    못 잡는다. 핸들러를 직접 붙여 받는다.
    """
    import logging

    from collection.cybos import investor_data as _m
    from collection.cybos.investor_data import CybosInvestorData

    records = []

    class _Cap(logging.Handler):
        def emit(self, rec):
            records.append(rec.getMessage())

    h = _Cap(level=logging.WARNING)
    _m.logger.addHandler(h)
    try:
        inv = CybosInvestorData()
        inv._futures_supported = True
        inv._futures.update({"foreign": 4654})
        inv._futures_amt.update({"foreign": 1294497 // 7})   # 엉뚱한 열
        bad = inv.check_amount_consistency(1110.0)
        # 정상 매핑이면 경고가 없어야 한다 (오탐 확인)
        inv._futures_amt.update({"foreign": 1294497})
        ok = inv.check_amount_consistency(1110.0)
    finally:
        _m.logger.removeHandler(h)

    assert bad == pytest.approx(39.7, abs=1.0)
    assert ok == pytest.approx(278.1, abs=1.0)
    assert any("금액축 대사 실패" in m for m in records), (
        "열 매핑이 깨졌는데 경고가 없다 — 계측 4원칙 ⑤"
    )
    assert sum(1 for m in records if "금액축 대사 실패" in m) == 1, (
        "정상 매핑에서도 경고가 떴다 — 오탐"
    )


def test_32_regular_multiplier_not_our_mini_contract():
    """🔴 7221 선물 행은 시장 전체(정규 250,000)다 — 우리 미니 50,000 이 아니다."""
    from collection.cybos.investor_data import CybosInvestorData

    assert CybosInvestorData._REGULAR_FUT_PT_VALUE == 250_000, (
        "우리 매매 종목(미니 A05·50,000)의 승수로 '고치면' 5배 틀린다. "
        "이 행은 우리 포지션이 아니라 시장 수급이다"
    )
    # 실제 '호출'만 잡는다 — 주석 속 백틱 언급(`active_contract_spec()`)은 설명이다.
    import re
    src = _src(_INV)
    code_only = "\n".join(
        ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
    assert "active_contract_spec" not in code_only, (
        "미니 승수 조회 경로를 실제로 호출한다 — 위 이유로 여기서는 쓰면 안 된다"
    )
    # 미니 승수 50,000 이 상수로 들어오면 안 된다.
    # (`250_000` 안의 부분문자열에 걸리지 않도록 경계를 준다)
    assert not re.search(r"(?<![\d_])50_?000(?![\d_])", code_only), (
        "미니 승수가 코드에 등장한다 — 시장 수급 행에는 정규 250,000 만 쓴다"
    )


def test_33_amount_axis_resets_daily():
    from collection.cybos.investor_data import CybosInvestorData

    inv = CybosInvestorData()
    inv._futures_amt["foreign"] = 1294497
    inv._futures_amt_seen.add("foreign")
    inv.reset_daily()
    assert inv._futures_amt["foreign"] == 0, "어제 금액이 오늘 화면에 남는다"
    assert not inv._futures_amt_seen


def test_34_main_wires_amount_recon():
    body = _src(_MAIN).split("def _fetch_investor_data", 1)[1][:2500]
    assert "check_amount_consistency" in body, (
        "대사가 호출되지 않는다 — 배선 없는 계측은 죽은 코드다"
    )
