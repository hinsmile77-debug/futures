# -*- coding: utf-8 -*-
"""[MW0601 490차 / F-G] CB③ 「조건 성립」 축을 실제로 센다.

## 왜 필요한가 (2026-08-24 이상점 1-8)

그날 CB③ 발동 조건이 **30분 성립**했고 그 창 안에서 2포지션 -128,195원이 났다.
그런데 그 사실이 **운영 로그 어디에도 남지 않았다**:

  · `[DBG-CB]` — DEBUG 채널 한 줄뿐(사람이 손으로 재집계해야 했다)
  · `[CB③ 비활성]` — `logger.debug` × `LOG_LEVEL=INFO` 라 종일 **0건 출력**
  · 482차 G-1 `cb3_ready_minutes` — 「판정 **가능**했던 분」만 센다.
    「가용한데 임계 미달인 분」은 세지 않는다.

2026-08-28 에 CB② 복원 여부를 정해야 하는데, 그 결정 자료의 두 번째 열이 이것이다.

## 고정하는 것

1. `cb3_ready`(가용) 와 `cb3_would_halt`(조건 성립)는 **다른 질문**이다.
2. 표본이 없으면 `cb3_acc30m` 은 `None` — 0.0(정확도 0%)과 구분된다(계측 4원칙 ②).
3. 15:40 마감 로그가 **무조건** 한 줄 찍는다 — 다른 경보의 발화 여부에 종속되지 않는다.
4. 손익은 레그 **금액 합산**(= 포지션 단위)이다(계측 4원칙 ①).
5. 🔴 **HALT 경로는 손대지 않는다** — CB③ 차단은 한시예외로 비활성이며(절대원칙 §2)
   이 계측은 그 예외를 되돌리자는 제안이 아니다.
"""
import ast
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import CB_ACCURACY_MIN_30M, CB_ACC30M_MIN_SAMPLES  # noqa: E402
from safety.circuit_breaker import CircuitBreaker  # noqa: E402

_MAIN = io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()


def _cb_with(acc_values):
    cb = CircuitBreaker()
    cb._accuracy_buf.clear()
    for v in acc_values:
        cb._accuracy_buf.append(float(v))
    return cb


def test_표본_없으면_acc30m은_None이지_0이_아니다():
    """`status_dict()["accuracy_30m"]` 은 빈 버퍼에서 0.0 을 준다 — 그것을 판정에
    쓰면 「무정보」와 「정확도 0%」가 같은 값이 된다(457차 `recent_accuracy()` 사고)."""
    cb = _cb_with([])
    assert cb.cb3_acc30m is None
    assert cb.status_dict()["accuracy_30m"] == 0.0   # 종전 동작 — 바뀌지 않았다
    assert cb.status_dict()["accuracy_30m_measured"] is False


def test_표본_미달이면_조건_성립이_아니다():
    """정확도가 아무리 낮아도 판정 가능 표본이 없으면 CB③ 은 아무것도 하지 않는다."""
    cb = _cb_with([0.0] * (CB_ACC30M_MIN_SAMPLES - 1))
    assert cb.cb3_ready is False
    assert cb.cb3_would_halt is False, "표본 미달인데 조건 성립으로 셌다"
    assert cb.cb3_acc30m == 0.0, "표본은 있으므로 값 자체는 측정된다"


def test_가용_임계이상이면_조건_불성립():
    """`cb3_ready` 와 `cb3_would_halt` 는 다른 질문이다 — 가용해도 성립 안 할 수 있다."""
    cb = _cb_with([1.0] * CB_ACC30M_MIN_SAMPLES)
    assert cb.cb3_ready is True
    assert cb.cb3_would_halt is False


def test_가용_임계미달이면_조건_성립():
    cb = _cb_with([0.0] * CB_ACC30M_MIN_SAMPLES)
    assert cb.cb3_ready is True
    assert cb.cb3_would_halt is True
    assert cb.cb3_acc30m < CB_ACCURACY_MIN_30M


def test_임계_경계는_미만이다():
    """`< CB_ACCURACY_MIN_30M` — 정확히 임계면 성립하지 않는다(경계 무변경)."""
    n = CB_ACC30M_MIN_SAMPLES
    hits = int(round(CB_ACCURACY_MIN_30M * n))
    cb = _cb_with([1.0] * hits + [0.0] * (n - hits))
    if abs(cb.cb3_acc30m - CB_ACCURACY_MIN_30M) < 1e-9:
        assert cb.cb3_would_halt is False, "정확히 임계인데 성립으로 셌다"
    else:
        pytest.skip("표본 %d개로 임계 %.2f 를 정확히 재현할 수 없다" % (n, CB_ACCURACY_MIN_30M))


def test_availability에_조건성립_필드가_실린다():
    cb = _cb_with([0.0] * CB_ACC30M_MIN_SAMPLES)
    av = cb.cb3_availability
    for k in ("acc30m", "would_halt", "threshold"):
        assert k in av, "cb3_availability 에 %s 가 없다 (490차 F-G 회귀)" % k
    assert av["would_halt"] is True
    assert av["threshold"] == CB_ACCURACY_MIN_30M


def test_HALT_경로는_손대지_않았다():
    """🔴 CB③ 재상정 금지 사안 — 이 계측이 판정을 바꾸면 안 된다.

    새 프로퍼티 셋은 전부 **읽기 전용**이어야 한다. 상태를 바꾸는 문
    (대입 · HALT 호출)이 들어오면 실패한다.
    """
    src = io.open(os.path.join(_ROOT, "safety", "circuit_breaker.py"),
                  encoding="utf-8").read()
    tree = ast.parse(src)
    for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        for fn in cls.body:
            if not isinstance(fn, ast.FunctionDef):
                continue
            if fn.name not in ("cb3_acc30m", "cb3_would_halt", "cb3_availability"):
                continue
            for node in ast.walk(fn):
                # 지역 변수 대입은 무해하다 — 막는 것은 **인스턴스 상태 변경**이다.
                targets = []
                if isinstance(node, ast.Assign):
                    targets = node.targets
                elif isinstance(node, ast.AugAssign):
                    targets = [node.target]
                for t in targets:
                    assert not (isinstance(t, ast.Attribute)
                                and isinstance(t.value, ast.Name)
                                and t.value.id == "self"), (
                        "%s 가 self 상태를 대입한다 — 읽기 전용이어야 한다 (490차 F-G)"
                        % fn.name
                    )
                if isinstance(node, ast.Call):
                    name = getattr(node.func, "attr", getattr(node.func, "id", ""))
                    assert "halt" not in str(name).lower(), (
                        "%s 가 HALT 경로를 부른다 — 재상정 금지 사안이다" % fn.name
                    )


def test_카운터_3종이_명시_초기화되고_리셋된다():
    """계측 4원칙 ④ — getattr 폴백으로 읽지 않는다. 그리고 일일 리셋에 등록돼야 한다."""
    for name in ("_mh_cb3_would_halt_minutes", "_mh_cb3_would_halt_entries",
                 "_mh_cb3_would_halt_pnl_krw"):
        assert ("self.%s: " % name) in _MAIN or ("self.%s:" % name) in _MAIN, (
            "%s 가 __init__ 에서 타입 주석과 함께 명시 초기화되지 않았다" % name
        )
        assert _MAIN.count("self.%s" % name) >= 3, (
            "%s 가 초기화·갱신·리셋 셋 중 하나에 없다" % name
        )


def test_마감_로그가_무조건_찍힌다():
    """mc-conf 경보(`_cfg_txt`)에 얹으면 **경보가 발화할 때만** 나온다 —
    계측은 사건이 없을 때 「0분」이라고 말할 수 있어야 한다(계측 4원칙 ②)."""
    assert "[CB③계측]" in _MAIN, "15:40 마감 CB③ 계측 로그가 없다 (490차 F-G 회귀)"
    i_log = _MAIN.index("[CB③계측]")
    i_gap = _MAIN.index("MC_CONF_GAP_ALERT_ENABLED")
    assert i_log < i_gap, (
        "CB③ 계측 로그가 mc-conf 경보 블록 안으로 들어갔다 — 그 경보가 발화하지 "
        "않는 날에는 찍히지 않는다"
    )
    # 리셋 뒤 지점이므로 반드시 스냅샷을 읽어야 한다(483차 P1-A).
    seg = _MAIN[i_log:i_log + 1200]
    assert "_mh_snap_eod" in seg, (
        "CB③ 계측 로그가 `self._mh_*` 를 직접 읽는다 — 그 지점은 리셋 **뒤**라 "
        "항상 0 이다 (483차 P1-A 와 같은 사고)"
    )


def test_손익은_레그_금액을_합산한다():
    """포지션 단위 = 레그 **금액** 합산이다. 레그 **개수**를 세면 417차 오류가 된다."""
    i = _MAIN.index("_mh_cb3_would_halt_pnl_krw +=")
    seg = _MAIN[i:i + 200]
    assert "net_pnl_krw" in seg, (
        "CB③ 창 손익이 순손익 금액이 아닌 값을 누산한다 (계측 4원칙 ①)"
    )
