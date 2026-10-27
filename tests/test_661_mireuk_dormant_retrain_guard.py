"""[MW0602 661차 후속7] 미륵 휴면 중 앱 밖 재학습 진입점 차단.

  G1  off 면 차단 · full 이면 통과 · --allow-dormant / 환경변수면 통과(의도적) · 설정을 못 읽으면 통과(종전 동작)
  G2  세 진입점이 무거운 단계(완료 마커·맥점·BatchRetrainer)보다 **먼저** 판정한다
  G3  판정 모듈은 numpy 등 무거운 모듈을 import 하지 않는다(DLL 부트스트랩 규약)
  G4  로그 문구에 cp949 로 못 찍는 문자가 없다(Windows 콘솔 logging 오류 방지)
"""
import inspect
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from utils import mireuk_dormant as MD  # noqa: E402


class _Log(object):
    def __init__(self):
        self.lines = []

    def warning(self, m):
        self.lines.append(m)

    info = warning


def _mode(monkeypatch, mode, why=None):
    monkeypatch.setattr(MD, "engine_mode", lambda: (mode, why))
    monkeypatch.delenv(MD.ALLOW_ENV, raising=False)


def test_G1_rules(monkeypatch):
    _mode(monkeypatch, "off")
    lg = _Log()
    assert MD.should_block("x", lg, argv=["x"]) is True and "재학습하지 않는다" in lg.lines[0]
    assert MD.should_block("x", _Log(), argv=["x", MD.ALLOW_ARG]) is False
    monkeypatch.setenv(MD.ALLOW_ENV, "1")
    assert MD.should_block("x", _Log(), argv=["x"]) is False
    _mode(monkeypatch, "full")
    lg = _Log()
    assert MD.should_block("x", lg, argv=["x"]) is False and not lg.lines
    _mode(monkeypatch, None, "ImportError")
    lg = _Log()
    assert MD.should_block("x", lg, argv=["x"]) is False and "읽지 못해" in lg.lines[0]


def test_G1_reads_real_setting():
    from config import settings as S
    assert MD.engine_mode()[0] == str(S.MIREUK_ENGINE).lower()


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


def test_G2_guard_precedes_heavy_steps():
    s = _src("retrain_eod.py")
    body = s[s.index("def main():"):]
    g = body.index('_dormant_block("retrain_eod.py"')
    assert g < body.index("_MARKER_PATH") and g < body.index("premarket_levels_eod") and g < body.index("BatchRetrainer")
    s = _src("retrain_intraday.py")
    body = s[s.index("def main():"):]
    g = body.index('_dormant_block("retrain_intraday.py"')
    assert g < body.index("BatchRetrainer") and '"mireuk_dormant"' in body
    s = _src(os.path.join("scripts", "eod_retrain.py"))
    body = s[s.index("def main():"):]
    g = body.index('_dormant_block("scripts/eod_retrain.py"')
    assert g < body.index("premarket_levels_eod") and "--allow-dormant" in body


def test_G3_no_heavy_imports():
    s = _src(os.path.join("utils", "mireuk_dormant.py"))
    for mod in ("numpy", "pandas", "sklearn", "scipy"):
        assert "import %s" % mod not in s


def test_G4_messages_cp949_safe():
    src = inspect.getsource(MD.should_block)
    for line in src.splitlines():
        if "say(" in line or line.strip().startswith('"'):
            line.encode("cp949")
