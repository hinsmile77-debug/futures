# -*- coding: utf-8 -*-
"""[MW0601 684차] 장후 자동조치 — F-18 재진단 · G-5 재기동 귀속 대사.

발단 — 2026-10-12
-----------------
09:33·11:22 두 재기동이 `crash_fault.log` 엔 `[CLEAN EXIT]` 인데 런처는 「일시적 크래시」,
SYSTEM 로그엔 `[Shutdown] intent=` 이 **없어** 장중·장후 점검이 「원인불명」으로 남겼다.

F-18("종료 사유 구분 로그 추가")은 618차에 이미 있었다. 그런데 대시보드 X 버튼 경로는
`write_exit_flags()` 에 `log_fn` 을 넘기지 않아 **모듈 로거로만** 찍혔고, 그 로거는 어떤 파일
핸들러에도 붙어 있지 않았다. 실측: 618차 이후 전 SYSTEM 로그에서 `intent=daily_close`·
`auto_shutdown` 각 10건, **`intent=user_*` 0건**. test_618 은 caplog 로 모듈 로거를 직접
잡아 이 결손을 보지 못했다 — 죽은 계측(FP-CRITICAL·TOX 섀도) 계열이다.

이 파일이 고정하는 것
---------------------
 ① 대시보드 두 분기가 **`log_fn` 을 넘긴다** — 다시 모듈 로거로만 찍히면 깨진다
 ② `log_fn` 으로 의도 줄이 실제로 전달된다(재시작도)
 ③ G-5 귀속 대사 — ±5분 창 · 창 밖은 후보 아님 · 미측정(None) ≠ 0건
 ④ 매매 경로 무변경 — 이 fix 는 로그 축만 건드린다
"""

import io
import os
import runpy
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.exit_flags import write_exit_flags

_BODY = os.path.join(_ROOT, ".claude", "skills", "mireuk-daily-check",
                     "scripts", "collect_evidence.py")


def _close_event_block():
    src = io.open(os.path.join(_ROOT, "dashboard", "main_dashboard.py"),
                  encoding="utf-8").read()
    return src.split('"종료 방법을 선택하세요."')[1].split("\n    def ")[0]


# ── ① 대시보드가 로그 경로를 명시한다 ────────────────────────────────────────

def test_dashboard_passes_log_fn_on_both_branches():
    ce = _close_event_block()
    assert 'log_manager import log_manager' in ce, \
        "X 버튼 종료가 SYSTEM 로그로 가려면 log_manager.system 을 넘겨야 한다"
    calls = [ln for ln in ce.splitlines() if "_wef(" in ln]
    assert len(calls) == 2, calls
    for ln in calls:
        assert "log_fn=" in ln, "모듈 로거만으로는 파일에 안 남는다(684차): %s" % ln.strip()


# ── ② log_fn 전달 ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("reason,keep", [("user_restart", True), ("user_close", False)])
def test_log_fn_receives_intent_line(tmp_path, reason, keep):
    (tmp_path / "data").mkdir()
    got = []
    write_exit_flags(reason, keep_alive=keep, root=str(tmp_path),
                     log_fn=lambda msg, lvl: got.append((msg, lvl)))
    assert any(("intent=%s" % reason) in m for m, _ in got), got


# ── ③ G-5 귀속 대사 ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ce():
    if not os.path.exists(_BODY):
        pytest.skip("수집기 본체 없음")
    return runpy.run_path(_BODY, run_name="_ce_684")


def _c(hm, sha="abc1234", subj="x"):
    h, m = hm.split(":")
    return {"min": int(h) * 60 + int(m), "hm": hm, "sha": sha, "subj": subj}


def test_attribution_window(ce):
    restarts = [{"at": "09:33", "kind": "일시적 크래시"},
                {"at": "11:22", "kind": "일시적 크래시"}]
    commits = [_c("09:46"), _c("11:27"), _c("15:30")]
    intents = [{"min": 11 * 60 + 21, "hm": "11:21", "intent": "user_restart"}]
    rows = ce["restart_attribution"](restarts, intents, commits)
    # 09:33 — 09:46 은 13분 밖이라 후보가 아니다
    assert rows[0]["near"] == [] and rows[0]["far"] == 3
    assert rows[0]["intents"] == []
    # 11:22 — 11:27 은 ±5분 안, 의도 줄은 −3~+1분 안
    assert [c["hm"] for c in rows[1]["near"]] == ["11:27"]
    assert rows[1]["far"] == 2
    assert rows[1]["intents"][0]["intent"] == "user_restart"


def test_unmeasured_is_not_zero(ce):
    """로그·git 이 없으면 None — 「0건」으로 위장하지 않는다(계측 4원칙 ②)."""
    rows = ce["restart_attribution"]([{"at": "09:33", "kind": "k"}], None, None)
    assert rows[0]["intents"] is None and rows[0]["near"] is None
    txt = "\n".join(ce["restart_attribution_lines"](rows, "SYSTEM 로그 없음", "git 실패"))
    assert "미측정" in txt and "SYSTEM 로그 없음" in txt


def test_read_shutdown_intents_parses_system_log(ce, tmp_path):
    import datetime
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "20261012_SYSTEM.log").write_text(
        "2026-10-12 15:40:20 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2\n"
        "2026-10-12 15:41:00 [INFO] SYSTEM: 다른 줄\n", encoding="utf-8")
    rows, why = ce["read_shutdown_intents"](str(tmp_path), datetime.date(2026, 10, 12))
    assert why == "" and rows == [{"min": 940, "hm": "15:40", "intent": "daily_close"}]
    none, why2 = ce["read_shutdown_intents"](str(tmp_path), datetime.date(2026, 10, 13))
    assert none is None and "없음" in why2


# ── ④ 매매 경로 무변경 ───────────────────────────────────────────────────────

def test_change_is_log_only():
    """closeEvent 의 파일 규약(keep_alive 분기)·quit 호출은 그대로다."""
    ce = _close_event_block()
    assert '_wef("user_close", keep_alive=False' in ce
    assert '_wef("user_restart", keep_alive=True' in ce
    assert "_QApp.instance().quit()" in ce
