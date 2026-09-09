# -*- coding: utf-8 -*-
"""[MW0601 553차 / Phase 3] GP 규칙 섀도 도전자 2종의 집행 불변식.

무엇을 고정하나
---------------
`challenger/variants/gp_rule.py` 는 사전등록(`VALIDATION_CAMPAIGN["gp_rule_*"]`)을
**집행**할 뿐이고 파라미터를 스스로 갖지 않는다. 이 파일은 그 관계와, 원문서가
「절대 하지 말라」고 못박은 것들을 고정한다.

  · 롱 = GB 0.5 상향돌파 · 90분 · **추가조건 없음**
    🔴 압축·수렴 필터를 붙이면 신호 2,620 → 1,099 로 줄면서 **300pt 를 파괴**한다.
  · 숏 = 압축(10봉 내) → GS 0.5 상향돌파 & GB≤0.10 & **MA20<MA60** · 60분 / GS≥1.2 · 당일 1회
    🔴 국면필터를 빼면 −186.7pt(t=−2.71) — 전략이 마이너스로 뒤집힌다.
    따라서 **필터를 읽을 수 없으면 진입하지 않는다**(계측 4원칙 ②).

실행:
    conda run -n py37_32 python -m pytest tests/test_553_gp_rule_challengers.py -v
"""
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ["MIREUK_TEST_MODE"] = "1"

import pytest  # noqa: E402

from challenger.challenger_registry import REGIME_POOLS  # noqa: E402
from challenger.variants.base_challenger import ExitReason  # noqa: E402
from challenger.variants.gp_rule import (  # noqa: E402
    GpLongGb90Challenger, GpShortSqz60Challenger,
)
from config.settings import GP_CROSS_PERIOD, VALIDATION_CAMPAIGN  # noqa: E402

_LONG_CFG = VALIDATION_CAMPAIGN["gp_rule_long_watch"]
_SHORT_CFG = VALIDATION_CAMPAIGN["gp_rule_short_watch"]
_IDS = VALIDATION_CAMPAIGN["gp_rule_challenger_ids"]
_P = GP_CROSS_PERIOD


def _feat(gb=0.3, gs=0.3, up=0.0, dn=0.0, ready=True,
          ma_ready=True, ma_down=0.0):
    return {
        "gp_buy_%d" % _P: gb,
        "gp_sell_%d" % _P: gs,
        "gp_cross_up_%d" % _P: up,
        "gp_cross_dn_%d" % _P: dn,
        "gp_ready_%d" % _P: ready,
        "ma_cont_ready": ma_ready,
        "ma_regime_down_cont": ma_down,
        "ma_sess_ready": ma_ready,
        "ma_regime_down_sess": ma_down,
    }


def _ctx(hhmm, day="2026-09-10"):
    return {"ts": "%s %s:00" % (day, hhmm), "atr": 3.0, "regime": "혼합"}


def _step(ch, hhmm, feats, day="2026-09-10"):
    """엔진과 **같은 순서**로 한 봉을 먹인다 — observe 가 먼저다."""
    c = _ctx(hhmm, day)
    ch.observe(feats, c)
    return ch.generate_signal(feats, c)


class _Trade(object):
    def __init__(self, entry_ts, direction=1, entry_price=1100.0):
        self.entry_ts = entry_ts
        self.direction = direction
        self.entry_price = entry_price
        self.atr_at_entry = 3.0


# ── 사전등록 ↔ 구현 일치 ────────────────────────────────────────────────────

def test_ids_match_preregistration():
    assert GpLongGb90Challenger.challenger_id == _IDS["long"]
    assert GpShortSqz60Challenger.challenger_id == _IDS["short"]


def test_long_params_come_from_preregistration():
    assert GpLongGb90Challenger.HOLD_MINUTES == _LONG_CFG["hold_minutes"]
    assert GpLongGb90Challenger.SESSION_START == _LONG_CFG["session_start"]
    assert GpLongGb90Challenger.SESSION_END == _LONG_CFG["session_end"]
    assert GpLongGb90Challenger.FORCE_EXIT_TIME == _LONG_CFG["force_exit"]


def test_short_params_come_from_preregistration():
    c = GpShortSqz60Challenger
    assert c.HOLD_MINUTES == _SHORT_CFG["hold_minutes"]
    assert c.EXIT_GS == _SHORT_CFG["exit_gs_target"]
    assert c.SQZ_VALID_BARS == _SHORT_CFG["squeeze_valid_bars"]
    assert c.TRIGGER_GB_MAX == _SHORT_CFG["trigger_gb_max"]
    assert c.MAX_PER_DAY == _SHORT_CFG["max_per_day"]
    assert c.MA_BASIS == _SHORT_CFG["ma_basis"] == "cont"
    assert c.K_MA_DOWN == "ma_regime_down_cont"


def test_no_hardcoded_rule_numbers_in_module():
    """파라미터 사본은 드리프트한다 — 사전등록에서 읽어야 한다."""
    src = io.open(os.path.join(_ROOT, "challenger", "variants", "gp_rule.py"),
                  encoding="utf-8").read()
    assert "_LONG_CFG[" in src and "_SHORT_CFG[" in src
    for lit in ("= 90", "= 60\n", "= 1.2", "= 0.10"):
        assert ("HOLD_MINUTES %s" % lit) not in src


# ── 절대원칙·거버넌스 ────────────────────────────────────────────────────────

def test_gp_challengers_are_not_in_regime_pools():
    """🔴 레짐 풀에 들어가면 순위·자동 승격 경로가 생긴다(절대원칙 §6)."""
    pooled = set(sum(REGIME_POOLS.values(), []))
    assert _IDS["long"] not in pooled
    assert _IDS["short"] not in pooled


@pytest.mark.parametrize("cls", [GpLongGb90Challenger, GpShortSqz60Challenger])
def test_force_exit_is_stricter_than_absolute_rule(cls):
    assert cls.FORCE_EXIT_TIME == "15:05" <= "15:10"


@pytest.mark.parametrize("cls", [GpLongGb90Challenger, GpShortSqz60Challenger])
def test_grade_is_not_faked(cls):
    """등급 개념이 없다 — `grade="A"` 를 지어내지 않는다(계측 4원칙 ④)."""
    assert cls.GRADE_NA is True
    ch = cls()
    sig = _step(ch, "10:00", _feat())
    assert sig.grade == "-"
    assert sig.signal_meta.get("grade_na") is True
    assert sig.signal_meta.get("confidence_na") is True


# ── 롱 ──────────────────────────────────────────────────────────────────────

def test_long_enters_on_cross_up():
    ch = GpLongGb90Challenger()
    assert _step(ch, "10:00", _feat(up=1.0)).direction == 1


def test_long_needs_no_other_condition():
    """🔴 압축·수렴이 아니어도 진입한다 — 필터를 붙이면 300pt 가 사라진다."""
    ch = GpLongGb90Challenger()
    # 압축 아님(스프레드 큼) · 반대선 0 수렴 아님 → 그래도 진입해야 한다
    sig = _step(ch, "10:00", _feat(gb=0.9, gs=2.5, up=1.0))
    assert sig.direction == 1, "롱에 추가 필터가 생겼다(원문서 기각 목록)"


def test_long_blocks_outside_window():
    ch = GpLongGb90Challenger()
    for hhmm in ("09:19", "14:51"):
        sig = _step(ch, hhmm, _feat(up=1.0))
        assert sig.direction == 0
        assert sig.signal_meta["block"] == "out_of_window"


@pytest.mark.parametrize("hhmm", ["09:20", "14:50"])
def test_long_window_boundaries_are_inclusive(hhmm):
    ch = GpLongGb90Challenger()
    assert _step(ch, hhmm, _feat(up=1.0)).direction == 1


def test_long_warmup_is_unmeasured_not_no_signal():
    ch = GpLongGb90Challenger()
    sig = _step(ch, "10:00", _feat(up=1.0, ready=False))
    assert sig.direction == 0
    assert sig.signal_meta["block"] == "gp_unready"
    assert sig.signal_meta["unmeasured"] is True


def test_long_exits_at_90_minutes():
    ch = GpLongGb90Challenger()
    t = _Trade("2026-09-10 10:00:00")
    assert ch.should_exit(t, 1100.0, "2026-09-10 11:29:00") is None
    assert ch.should_exit(t, 1100.0, "2026-09-10 11:30:00") == ExitReason.TIME


def test_long_has_no_stop_loss():
    """손절 없음 — 90분 시간손절이 그 역할이다(사전등록 stop_loss=None)."""
    assert _LONG_CFG["stop_loss"] is None
    ch = GpLongGb90Challenger()
    t = _Trade("2026-09-10 10:00:00", entry_price=1100.0)
    assert ch.should_exit(t, 1000.0, "2026-09-10 10:30:00") is None


def test_long_unparsable_ts_does_not_close_or_pretend():
    ch = GpLongGb90Challenger()
    assert ch.should_exit(_Trade("bad-ts"), 1100.0, "2026-09-10 12:00:00") is None


# ── 숏 ──────────────────────────────────────────────────────────────────────

def _prime_squeeze(ch, start_min=0, bars=12):
    """압축 상태를 만들고 워밍업을 채운다."""
    for i in range(bars):
        m = 9 * 60 + 25 + start_min + i
        _step(ch, "%02d:%02d" % (m // 60, m % 60), _feat(gb=0.2, gs=0.2))


def test_short_full_condition_enters():
    ch = GpShortSqz60Challenger()
    _prime_squeeze(ch)
    sig = _step(ch, "09:40", _feat(gb=0.05, gs=0.6, dn=1.0, ma_down=1.0))
    assert sig.direction == -1, sig.signal_meta


def test_short_requires_regime_filter():
    """🔴 MA20<MA60 이 아니면 진입 금지 — 빼면 −186.7pt."""
    ch = GpShortSqz60Challenger()
    _prime_squeeze(ch)
    sig = _step(ch, "09:40", _feat(gb=0.05, gs=0.6, dn=1.0, ma_down=0.0))
    assert sig.direction == 0
    assert sig.signal_meta["block"] == "regime_not_down"


def test_short_blocks_when_regime_filter_unmeasured():
    """🔴 필터를 **읽을 수 없으면** 진입하지 않는다 — 그건 「필터 통과」가 아니다."""
    ch = GpShortSqz60Challenger()
    _prime_squeeze(ch)
    sig = _step(ch, "09:40", _feat(gb=0.05, gs=0.6, dn=1.0,
                                   ma_ready=False, ma_down=0.0))
    assert sig.direction == 0
    assert sig.signal_meta["block"] == "ma_unready"
    assert sig.signal_meta["unmeasured"] is True


def test_short_requires_opposite_line_convergence():
    ch = GpShortSqz60Challenger()
    _prime_squeeze(ch)
    sig = _step(ch, "09:40", _feat(gb=0.5, gs=0.6, dn=1.0, ma_down=1.0))
    assert sig.direction == 0
    assert sig.signal_meta["block"] == "gb_not_converged"


def test_short_requires_recent_squeeze():
    """압축이 10봉을 넘으면 무효."""
    ch = GpShortSqz60Challenger()
    _prime_squeeze(ch, bars=1)                       # 압축 1회
    for i in range(12):                              # 압축 아닌 봉 12개
        m = 9 * 60 + 26 + i
        _step(ch, "%02d:%02d" % (m // 60, m % 60), _feat(gb=0.9, gs=1.5))
    sig = _step(ch, "09:40", _feat(gb=0.05, gs=0.6, dn=1.0, ma_down=1.0))
    assert sig.direction == 0
    assert sig.signal_meta["block"] == "no_recent_squeeze"


def test_short_restart_squeeze_state_is_unmeasured_not_absent():
    """🔴 재기동이 압축 이력을 지운다 — 「압축 없었음」이 아니라 **모른다**이다."""
    ch = GpShortSqz60Challenger()          # 방금 기동한 상태
    sig = _step(ch, "10:00", _feat(gb=0.05, gs=0.6, dn=1.0, ma_down=1.0))
    assert sig.direction == 0
    assert sig.signal_meta["block"] == "sqz_state_unknown"
    assert sig.signal_meta["unmeasured"] is True


def test_short_exits_on_gs_target():
    ch = GpShortSqz60Challenger()
    _step(ch, "10:00", _feat(gs=1.2))
    t = _Trade("2026-09-10 09:50:00", direction=-1)
    assert ch.should_exit(t, 1100.0, "2026-09-10 10:00:00") == ExitReason.TP1


def test_short_gs_below_target_does_not_exit():
    ch = GpShortSqz60Challenger()
    _step(ch, "10:00", _feat(gs=1.19))
    t = _Trade("2026-09-10 09:50:00", direction=-1)
    assert ch.should_exit(t, 1100.0, "2026-09-10 10:00:00") is None


def test_short_exits_at_60_minutes():
    ch = GpShortSqz60Challenger()
    _step(ch, "10:50", _feat(gs=0.5))
    t = _Trade("2026-09-10 09:50:00", direction=-1)
    assert ch.should_exit(t, 1100.0, "2026-09-10 10:50:00") == ExitReason.TIME


def test_short_does_not_use_opposite_line_stop():
    """반대선(GB) 손절 미사용 — 1.5 는 너무 멀어 손실만 키웠다."""
    assert _SHORT_CFG["opposite_line_stop"] is None
    ch = GpShortSqz60Challenger()
    _step(ch, "10:00", _feat(gb=3.0, gs=0.1))       # GB 폭등해도
    t = _Trade("2026-09-10 09:55:00", direction=-1)
    assert ch.should_exit(t, 1100.0, "2026-09-10 10:00:00") is None


def test_short_day_cap_is_enforced_by_engine_not_memory():
    """🔴 당일 1회는 **DB 기준**이다 — 인메모리 플래그는 재시작이 지운다."""
    assert GpShortSqz60Challenger.MAX_PER_DAY == 1
    src = io.open(os.path.join(_ROOT, "challenger", "variants", "gp_rule.py"),
                  encoding="utf-8").read()
    assert "_entered_today" not in src, "인메모리 당일 플래그가 되살아났다"


# ── 일자 롤오버 ──────────────────────────────────────────────────────────────

def test_squeeze_state_resets_across_days():
    ch = GpShortSqz60Challenger()
    _prime_squeeze(ch)
    assert ch._sqz_bar is not None
    _step(ch, "09:20", _feat(gb=0.9, gs=1.5), day="2026-09-11")
    assert ch._sqz_bar is None, "전일 압축이 다음 날로 넘어왔다"
    assert ch._bar_no == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
