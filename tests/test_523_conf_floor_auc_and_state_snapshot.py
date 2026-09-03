# -*- coding: utf-8 -*-
"""[MW0601 523차 / 장후 자동조치] G-1 · G-2 · G-3 회귀 고정.

세 항목 모두 **관측 축만** 바꾼다. 주문·수량·게이트·청산 트리거·진입 판정은 한 줄도
바뀌지 않으며, §4가 그 사실을 코드로 고정한다.

- **G-2** `[ConfFloorGuard]` 발동 로그에 보정기 순위판별력(`auc`)을 동봉한다.
  2026-09-03 이상점 1-2 조사가 `[ConfFloorGuard]`(출력상한·min_conf·span)와
  `[Calibration]`(auc)을 손으로 대조해야 원인 후보(레짐 vs 보정기 결함)를 좁힐 수
  있었다. ⚠ **`span` 은 이미 찍히고 있었다** — 리포트 G-2의 "출력상한·min_conf만
  있음"은 사실과 달랐고(함정①), 실제 결손은 `auc` 하나였다.
- **G-1** `data/session_state.json` 기동 마커 스냅샷을 다이제스트 §9에 싣는다.
  이 파일에는 **날짜 토큰이 없어** 인벤토리(§1)에 구조적으로 안 잡힌다. 그래서
  이상점 1-1(어제 기록된 `p8_last_success_date` 가 아침에 사라짐)이 사람이 우연히
  파일을 열어봐서 발견됐다.
- **G-3** `[ExitStageRecon]` 을 `always_quote_patterns` 에 넣는다. 매일 15:40에
  자동으로 도는 청산 라벨 자기대사인데 목록에 없어, 이상점 1-3(F-10 세 번째 사례)을
  **수동 grep** 으로 찾아야 했다.

⚠ F-10(라벨 자체를 고치는 일)은 여기 없다 — 청산 트리거 경로 변경이라 사용자·
  주간회의 결정 사항이다(누적대장 P5-06, 섀도 10거래일 선행조건).
"""
from __future__ import annotations

import datetime
import importlib.util
import io
import json
import logging
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_COLLECTOR = os.path.join(
    _ROOT, ".claude", "skills", "mireuk-daily-check", "scripts", "collect_evidence.py"
)
_ENS_SRC = os.path.join(_ROOT, "model", "ensemble_decision.py")


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def collector():
    spec = importlib.util.spec_from_file_location("_collect_evidence_523", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────────
# §1. G-2 — ConfFloorGuard 발동 로그가 auc 를 함께 찍는다
# ─────────────────────────────────────────────────────────────────────────────

class _Cal(object):
    """보정기 스텁. `has_auc=False` 면 `rank_auc` 속성 자체가 없다."""

    def __init__(self, fitted=True, out_max=0.30, span=0.05,
                 auc=0.61, has_auc=True):
        self.is_fitted = fitted
        self.output_max = out_max
        self.output_span = span
        if has_auc:
            self.rank_auc = auc


def _guard(**kw):
    from model.ensemble_decision import EnsembleDecision
    obj = EnsembleDecision.__new__(EnsembleDecision)
    obj._conf_floor_reachable = None
    obj.conf_floor_state = "unmeasured:init"
    obj.ensemble_calibrator = _Cal(**kw)
    return obj


class _Capture(logging.Handler):
    """모듈 로거에 직접 붙는 수집기.

    ⚠ **`caplog` 를 쓰지 않는다.** `SIGNAL` 로거는 다른 테스트가 핸들러·propagate 를
    재구성하므로, caplog(루트에 붙는다)로 보면 **단독 실행만 통과하고 전체 실행에서
    깨진다** — 이 파일도 개발 중 실제로 그랬다(480차·493차가 남긴 같은 교훈).
    """

    def __init__(self):
        logging.Handler.__init__(self)
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def _capture(fn):
    """`fn()` 이 도는 동안 SIGNAL 로거로 나간 메시지를 모아 돌려준다."""
    lg = logging.getLogger("SIGNAL")
    cap = _Capture()
    old_level, old_disabled = lg.level, lg.disabled
    lg.addHandler(cap)
    lg.setLevel(logging.INFO)
    lg.disabled = False
    try:
        fn()
    finally:
        lg.removeHandler(cap)
        lg.setLevel(old_level)
        lg.disabled = old_disabled
    return "\n".join(cap.lines)


def _fire(**kw):
    """도달불가 판정을 한 번 일으키고 그 로그 텍스트를 돌려준다."""
    g = _guard(**kw)
    txt = _capture(lambda: g._check_conf_floor_consistency(0.50, zone_allows_entry=True))
    return g, txt


def test_g2_unreachable_warning_carries_auc():
    """발동(도달 불가) 로그에 `auc=` 가 실제 값으로 들어간다."""
    g, txt = _fire(out_max=0.30, auc=0.612)
    assert g.conf_floor_state == "unreachable"
    assert "자동진입 하한 도달 불가" in txt
    assert "auc=0.612" in txt, txt
    # span 은 종전부터 있었다 — 회귀로 함께 고정한다.
    assert "span=0.0500" in txt, txt


def test_g2_recovery_info_carries_auc():
    """복구(도달 가능) 로그에도 같은 두 값을 실어 앞뒤를 비교 가능하게 한다."""
    g = _guard(out_max=0.30, auc=0.612)
    g._check_conf_floor_consistency(0.50, zone_allows_entry=True)   # 먼저 unreachable
    assert g.conf_floor_state == "unreachable"
    # 보정기가 회복한 상황. ⚠ min_conf 만 낮춰서는 복구되지 않는다 —
    # `_need = max(ENS_CONF_FLOOR_FOR_AUTO, min_conf)` 라 정적 하한(0.33)이 남는다.
    g.ensemble_calibrator.output_max = 0.90
    txt = _capture(lambda: g._check_conf_floor_consistency(0.20, zone_allows_entry=True))
    assert g.conf_floor_state == "reachable"
    assert "하한 도달 가능 복구" in txt
    assert "auc=0.612" in txt and "span=0.0500" in txt, txt


def test_g2_three_auc_states_are_written_differently():
    """계측 4원칙 ②·④ — 「속성 없음」·「못 쟀음」·「값」이 서로 다른 문자열이다.

    셋을 `0` 이나 `N/A` 하나로 뭉치면, 정확히 이 로그로 가르려던 원인 후보
    (레짐 vs 보정기 결함)를 다시 못 가른다.
    """
    _, t_val = _fire(auc=0.55)
    _, t_none = _fire(auc=None)
    _, t_absent = _fire(has_auc=False)

    assert "auc=0.550" in t_val, t_val
    assert "auc=미측정" in t_none, t_none
    assert "auc=미보유" in t_absent, t_absent
    assert "auc=0.000" not in t_none and "auc=0.000" not in t_absent


# ─────────────────────────────────────────────────────────────────────────────
# §2. G-1 — 기동 마커 스냅샷 렌더러
# ─────────────────────────────────────────────────────────────────────────────

def _render(collector, tmp_path, payload, day="2026-09-03", write=True):
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "data"))
    if write:
        with io.open(os.path.join(root, "data", "session_state.json"),
                     "w", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False))
    cfg = {"state_snapshot_path": "data/session_state.json",
           "state_snapshot_keys": ["date", "p8_last_success_date",
                                   "eod_retrain_ok_date"]}
    out = []
    d = datetime.datetime.strptime(day, "%Y-%m-%d").date()
    collector.state_snapshot_section(root, cfg, d, out)
    return "\n".join(out)


def test_g1_all_keys_fresh_reads_as_match(collector, tmp_path):
    txt = _render(collector, tmp_path, {
        "date": "2026-09-03",
        "p8_last_success_date": "2026-09-03",
        "eod_retrain_ok_date": "2026-09-03",
    })
    assert "`p8_last_success_date` | 2026-09-03 | 예" in txt, txt
    # 표 행만 본다 — 절 끝의 안내 문단은 「아니오」라는 낱말을 설명용으로 쓴다.
    rows = [ln for ln in txt.splitlines() if ln.startswith("| `")]
    assert rows and all("**아니오**" not in ln for ln in rows), rows


def test_g1_missing_key_is_not_missing_value(collector, tmp_path):
    """1-1의 지문 — 키가 **통째로 사라진** 상태. 빈칸으로 쓰면 안 된다."""
    txt = _render(collector, tmp_path, {"date": "2026-09-03"})
    assert "`p8_last_success_date` | **(키 없음 — 미측정)**" in txt, txt
    assert "`eod_retrain_ok_date` | **(키 없음 — 미측정)**" in txt, txt


def test_g1_stale_date_is_flagged(collector, tmp_path):
    """어제 값이 남아 있는 경우 — 「예」로 조용히 넘어가면 안 된다."""
    txt = _render(collector, tmp_path, {
        "date": "2026-09-03",
        "p8_last_success_date": "2026-09-02",
        "eod_retrain_ok_date": None,
    })
    assert "`p8_last_success_date` | 2026-09-02 | **아니오**" in txt, txt
    assert "`eod_retrain_ok_date` | (null — 미측정)" in txt, txt


def test_g1_absent_file_says_unmeasured_not_zero(collector, tmp_path):
    txt = _render(collector, tmp_path, None, write=False)
    assert "파일 없음 — 미측정" in txt, txt


def test_g1_day_is_compared_as_text_not_date_object(collector, tmp_path):
    """`day` 는 `datetime.date` 다 — 문자열과 직접 비교하면 **항상 불일치**가 된다.

    그 버그는 크래시 없이 "매일 전부 아니오"라는 조용한 오보로만 나타난다.
    """
    txt = _render(collector, tmp_path, {"date": "2026-09-03",
                                        "p8_last_success_date": "2026-09-03",
                                        "eod_retrain_ok_date": "2026-09-03"})
    assert txt.count("| 예 |") == 3, txt


def test_g1_section_is_wired_into_the_digest():
    """렌더러가 정의만 되고 §9에서 호출되지 않으면 죽은 계측이다.

    FP-CRITICAL(2개월 PSI=0.0)·TOX 섀도(한 달)와 같은 계열의 사고를 막는다.
    """
    src = _read(_COLLECTOR)
    assert "state_snapshot_section(root, cfg, day, L)" in src, (
        "§9 본문에서 state_snapshot_section() 을 부르지 않는다 — 죽은 계측"
    )


# ─────────────────────────────────────────────────────────────────────────────
# §3. G-3 — ExitStageRecon 이 항상 인용된다
# ─────────────────────────────────────────────────────────────────────────────

def test_g3_pattern_registered(collector):
    pats = collector.DEFAULT_CONFIG["always_quote_patterns"]
    assert "[ExitStageRecon]" in pats, pats


def test_g3_pattern_precedes_generic_exit_tokens(collector):
    """한 줄당 첫 매치만 채택(break)한다 — 일반 토큰 뒤에 두면 삼켜질 수 있다."""
    pats = collector.DEFAULT_CONFIG["always_quote_patterns"]
    i = pats.index("[ExitStageRecon]")
    for generic in ("안전망", "FORCED"):
        assert i < pats.index(generic), (
            "[ExitStageRecon] 이 %r 뒤에 있다 — 문구가 바뀌면 다른 버킷에 삼켜진다"
            % generic
        )


def test_g3_real_log_line_lands_in_its_own_bucket(collector):
    """2026-09-03 실제 로그 한 줄이 다른 패턴에 가로채이지 않는다."""
    line = ("2026-09-03 15:40:06 [WARNING] SYSTEM: [ExitStageRecon] 오늘 "
            "TRAIL_AFTER_TP1 4레그 / 4포지션 중 TP 이벤트 대응 0 · 단일계약 "
            "보호전환(설계) 3 · 미대응 1 ⚠ 미대응 합계 -47,496원 (진입 10:03:01). "
            "이 레그들은 라벨상 「TP1 뒤 트레일(이익 청산)」이지만 그 포지션에 TP가 "
            "난 적이 없다 — 손절률 분모·분자가 오염된다")
    up = line.upper()
    first = None
    for pat in collector.DEFAULT_CONFIG["always_quote_patterns"]:
        if pat.upper() in up:
            first = pat
            break
    assert first == "[ExitStageRecon]", "먼저 잡힌 패턴: %r" % first


def test_g3_json_config_must_not_shadow_the_pattern_list():
    """🔴 `load_config()` 는 `cfg.update(user)` — **키 단위 통째 교체**다.

    JSON 에 `always_quote_patterns` 를 한 줄이라도 쓰면 코드 기본값 30여 개가
    통째로 사라지고, 안전장치·크래시 패턴이 조용히 인용되지 않게 된다.
    리포트 G-3은 JSON 쪽에도 추가하라고 적었으나 그 경로는 회귀다.
    """
    for rel in ("config/dailycheck_targets.json",
                ".claude/skills/mireuk-daily-check/config_dailycheck_targets.json"):
        p = os.path.join(_ROOT, rel)
        if not os.path.exists(p):
            continue
        obj = json.loads(_read(p))
        assert "always_quote_patterns" not in obj, (
            "%s 가 always_quote_patterns 를 정의한다 — 코드 기본값을 통째로 덮는다" % rel
        )


# ─────────────────────────────────────────────────────────────────────────────
# §4. 라이브 반영 0 — 매매 경로는 한 줄도 바뀌지 않았다
# ─────────────────────────────────────────────────────────────────────────────

def test_no_trading_side_effect_in_conf_floor_guard():
    """가드 본문은 여전히 `conf_floor_state` 래치와 로그만 만진다.

    수량·게이트·주문 관련 이름이 이 함수에 들어오면 관측이 매매를 바꾼 것이다.
    """
    src = _read(_ENS_SRC)
    i = src.index("def _check_conf_floor_consistency")
    body = src[i:src.index("\n    def ", i + 10)]
    for banned in ("order", "quantity", "size_multiplier", "MAX_CONTRACTS",
                   "place_", "entry_qty"):
        assert banned not in body, (
            "_check_conf_floor_consistency 안에 %r 이 생겼다 — "
            "판정만 남기기로 한 가드다(§9 사전등록 원칙)" % banned
        )


def test_auc_read_cannot_change_the_verdict():
    """auc 조회가 실패해도 도달가능/불가 판정은 그대로다.

    `rank_auc` 접근이 예외를 내면 try/except 가 삼켜 `unmeasured:error` 로 떨어지고,
    그 순간 가드가 눈을 감는다 — 관측 추가가 관측을 죽이는 형태다.
    """
    class _Boom(_Cal):
        @property
        def rank_auc(self):
            raise RuntimeError("auc 계산 실패")

    for out_max, expect in ((0.30, "unreachable"), (0.90, "reachable")):
        plain = _guard(out_max=out_max, has_auc=False)
        plain._check_conf_floor_consistency(0.50, zone_allows_entry=True)
        assert plain.conf_floor_state == expect

        from model.ensemble_decision import EnsembleDecision
        boom = EnsembleDecision.__new__(EnsembleDecision)
        boom._conf_floor_reachable = None
        boom.conf_floor_state = "unmeasured:init"
        boom.ensemble_calibrator = _Boom(out_max=out_max, has_auc=False)
        boom._check_conf_floor_consistency(0.50, zone_allows_entry=True)
        assert boom.conf_floor_state == expect, (
            "auc 조회 예외가 판정을 %r 로 바꿨다 — 관측이 가드를 죽였다"
            % boom.conf_floor_state
        )


def test_state_snapshot_is_read_only():
    """수집기는 상태 파일을 **쓰지 않는다** — 장중에 돌아도 안전해야 한다."""
    src = _read(_COLLECTOR)
    i = src.index("def state_snapshot_section")
    body = src[i:src.index("\ndef ", i + 10)]
    for banned in ('"w"', "'w'", "json.dump", "os.remove", "shutil"):
        assert banned not in body, (
            "state_snapshot_section 이 쓰기를 한다: %r" % banned
        )
