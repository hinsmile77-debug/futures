# -*- coding: utf-8 -*-
"""[MW0601 507차 후속 / F-14] `[NetRecon]` 진단문을 **실제 축 분해**로 바꾼다.

종전 ERROR 는 *"gross가 일치하는데 net만 어긋나면 원인은 수수료율이다"* 라는
**고정 문구**를 조건 없이 붙였다. 2026-08-31 실측에서 그것이 틀렸다 —
잔차 −91,461원 중 gross 축이 −70,000원(77%)이었고, 같은 초에
`[BrokerPnl] gross 불일치` WARNING 이 따로 떠 있었다. 두 로그가 서로 다른 결론을
말한 것이다(계측 4원칙 ⑤).

⚠ `scripts/commission_rate_recon.py --verify` 의 **판정식은 건드리지 않는다**
  (사전등록 유지). 바뀌는 것은 로그 문자열뿐이다.
"""
from __future__ import annotations

import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.db_utils import (                        # noqa: E402
    decompose_net_residual, format_net_recon_mismatch,
)

# ── 2026-08-31 실측값 ────────────────────────────────────────────────────────
REC_0831 = {
    "status": "MISMATCH",
    "engine_gross": -5_976_000.0,
    "broker_gross": -5_906_000.0,
    "engine_commission": 413_508.0,
    "broker_commission": 392_047.0,
    "commission_ratio": 392_047.0 / 413_508.0,
    "engine_net": -6_389_508.0,
    "broker_net": -6_298_047.0,
    "residual": -91_461.0,
    "tolerance": 78_409.0,
}


def test_a_axes_sum_to_residual_exactly():
    """ⓐ 두 축의 합이 잔차와 **정확히** 같다 — 항등식이므로 반올림 오차가 없다."""
    d = decompose_net_residual(REC_0831, broker_gross_measured=True)
    assert d["gross_axis"] + d["comm_axis"] == pytest.approx(d["residual"], abs=1e-6)


def test_b_gross_dominates_on_0831():
    """ⓑ 08-31 값으로 「지배 축 = gross」가 나온다 — 고정 문구가 틀렸던 그 날."""
    d = decompose_net_residual(REC_0831, broker_gross_measured=True)
    assert d["gross_axis"] == pytest.approx(-70_000.0)
    assert d["comm_axis"] == pytest.approx(-21_461.0)
    assert d["dominant"] == "gross"
    assert d["gross_share"] == pytest.approx(76.5, abs=0.5)

    msg = format_net_recon_mismatch(REC_0831, True)
    assert "지배 축 = gross" in msg
    assert "체결 대사를 먼저 볼 것" in msg


def test_c_commission_dominates_when_gross_matches():
    """ⓒ gross 가 실제로 일치하는 합성 케이스에서는 「지배 축 = 수수료」다.

    493차가 잡은 수수료율 6.54배 사고의 형태 — 그 진단문은 **그 때만** 나와야 한다.
    """
    rec = dict(REC_0831)
    rec["broker_gross"] = rec["engine_gross"]          # gross 축 0
    rec["broker_commission"] = 2_705_000.0
    rec["commission_ratio"] = 6.54
    rec["residual"] = ((rec["engine_gross"] - rec["engine_commission"])
                       - (rec["broker_gross"] - rec["broker_commission"]))
    rec["engine_net"] = rec["engine_gross"] - rec["engine_commission"]
    rec["broker_net"] = rec["broker_gross"] - rec["broker_commission"]

    d = decompose_net_residual(rec, broker_gross_measured=True)
    assert d["gross_axis"] == 0.0
    assert d["dominant"] == "commission"

    msg = format_net_recon_mismatch(rec, True)
    assert "지배 축 = 수수료" in msg
    assert "commission_rate_recon.py --verify" in msg


def test_d_fixed_phrase_is_never_unconditional():
    """ⓓ 종전 **고정 문구**가 조건 없이 등장하지 않는다.

    이것이 F-14 의 핵심이다 — 문구 자체는 사라져도 되고 남아도 되지만,
    gross 축이 지배하는 날에 나오면 안 된다.
    """
    msg = format_net_recon_mismatch(REC_0831, True)
    assert "gross가 일치하는데" not in msg
    # 그리고 어떤 경우에도 두 진단이 동시에 나오지 않는다.
    assert not ("지배 축 = gross" in msg and "지배 축 = 수수료" in msg)


def test_e_unmeasured_gross_is_not_zero():
    """ⓔ 브로커 gross 미수신은 **미측정**이다 — 0 으로 읽으면 자기참조 대사가 된다.

    `update_daily_broker_pnl_net()` 이 행이 없을 때 엔진 gross 로 행을 만든다
    (498차 F-9). 그 값을 브로커로 읽으면 항상 "gross 일치"가 되어버린다.
    """
    d = decompose_net_residual(REC_0831, broker_gross_measured=False)
    assert d["gross_axis"] is None
    assert d["dominant"] is None

    msg = format_net_recon_mismatch(REC_0831, False)
    assert "미측정" in msg
    assert "지배 축 판정 불가" in msg
    assert "지배 축 = gross" not in msg


def test_f_message_shape_is_three_axes_plus_verdict():
    """ⓕ 로그가 「잔차 → gross 축 → 수수료 축 → 판정」 네 줄로 나온다."""
    msg = format_net_recon_mismatch(REC_0831, True)
    lines = msg.split("\n")
    assert len(lines) == 4
    assert lines[0].startswith("[NetRecon]")
    assert "gross 축" in lines[1]
    assert "수수료 축" in lines[2]
    assert lines[3].strip().startswith("⇒")


def test_g_main_uses_the_helper():
    """ⓖ `main.py` 가 인라인 문자열이 아니라 이 헬퍼를 쓴다(회귀).

    인라인으로 되돌아가면 테스트가 못 보는 곳으로 진단문이 다시 숨는다.
    """
    src = open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
    assert "format_net_recon_mismatch" in src
    assert re.search(r"gross가 일치하는데.*수수료율", src) is None, \
        "고정 진단문이 main.py 에 되살아났다"
