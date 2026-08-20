# -*- coding: utf-8 -*-
"""[MW0601 480차 / F-2·G-1] 프로세스 밖 FLAT 가드 + 생존 하트비트 파일 회귀 고정.

## 무엇을 지키는가

2026-08-19 13:41:21 동결에서 절대원칙 §1의 방어선 3개(STEP 8 → SchedForceExit →
15:18 안전망)가 **동시에** 죽었다. 전부 같은 프로세스 안에 있기 때문이다.
FZ-1 워치독은 15:10 **이전** 구간만 메운다 — 15:10 이후 발화는 런처가 재기동하지
않으므로(오버나이트 금지) 15:10~15:35가 비어 있다.

이 테스트가 고정하는 불변식은 셋이다:

  ① 판정 — "미청산"이 어떤 조합에서도 OK로 뭉개지지 않을 것
  ② 미측정 ≠ 0 — 하트비트 파일이 **없는** 것과 **낡은** 것이 다른 결론을 낼 것
     (계측 4원칙 ②. 없는 것을 "정상"으로 처리하면 가드가 있으나 마나가 된다)
  ③ 하트비트 파일이 실제로 쓰이고, 미시작 상태의 나이가 0이 아니라 null일 것
"""
import datetime
import json
import os
import sys
import tempfile

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.force_flat_guard import (  # noqa: E402
    RC_OK, RC_PROCESS_DEAD, RC_UNCLOSED, RC_UNKNOWN, judge,
)
from utils.freeze_watchdog import FreezeWatchdog  # noqa: E402

NOW = datetime.datetime(2026, 8, 19, 15, 12, 0)


def _hb(age_sec=5.0, loop_age=3.0, pid=1234):
    """age_sec 전에 기록된 하트비트 파일 내용."""
    written = NOW - datetime.timedelta(seconds=age_sec)
    return {
        "pid": pid,
        "written_at": written.isoformat(timespec="seconds"),
        "beat_epoch": 1.0,
        "beat_age_sec": loop_age,
        "watching": True,
        "strikes": 0,
    }


def _pos(status="FLAT", qty=0, saved="2026-08-19T13:23:31"):
    return {
        "status": status,
        "quantity": qty,
        "last_update_ts": saved,
        "last_update_reason": "테스트",
        "saved_at": saved,
    }


# ── ① 판정 ────────────────────────────────────────────────────────────────

def test_정상은_OK다():
    v = judge(NOW, _hb(), _pos())
    assert v["level"] == "OK" and v["rc"] == RC_OK


def test_미청산이면_프로세스가_살아_있어도_CRITICAL이다():
    # 15:12에 포지션이 남아 있다는 것 자체가 절대원칙 §1 위반 신호다.
    # 프로세스 생존은 "아직 닫을 수 있다"는 뜻일 뿐 위반을 지우지 않는다.
    v = judge(NOW, _hb(), _pos("LONG", 2))
    assert v["level"] == "CRITICAL" and v["rc"] == RC_UNCLOSED


def test_미청산_더하기_프로세스정지가_최악이다():
    v = judge(NOW, _hb(age_sec=4000, loop_age=4000), _pos("SHORT", 1))
    assert v["rc"] == RC_UNCLOSED
    assert "아무도 닫아줄 수 없다" in v["headline"]


def test_FLAT인데_프로세스만_멈추면_WARNING이다():
    # 2026-08-19가 정확히 이 경우였다 — 실손해 0이지만 구멍은 열려 있다.
    v = judge(NOW, _hb(age_sec=6000, loop_age=6000), _pos())
    assert v["level"] == "WARNING" and v["rc"] == RC_PROCESS_DEAD


def test_수량이_0이_아니면_status가_FLAT이어도_미청산이다():
    # 상태 전이 도중(청산 진행 중) 스냅샷이 저장될 수 있다. 둘 중 하나라도
    # 포지션을 가리키면 미청산으로 본다 — 안전측으로 틀리는 쪽을 고른다.
    v = judge(NOW, _hb(), _pos("FLAT", 3))
    assert v["rc"] == RC_UNCLOSED


def test_파일이_최신이어도_이벤트루프가_낡았으면_정지로_본다():
    # 워치독 스레드는 살아서 파일을 계속 쓰지만 메인 이벤트 루프만 죽은 상태.
    # 파일 mtime만 보면 정상으로 보인다 — 그것이 08-19에 session_state.json이
    # 16:08로 갱신돼 있던 것과 같은 착시다.
    v = judge(NOW, _hb(age_sec=5, loop_age=900), _pos())
    assert v["rc"] == RC_PROCESS_DEAD


# ── ② 미측정 ≠ 0 (계측 4원칙 ②) ───────────────────────────────────────────

def test_하트비트_파일이_없으면_OK가_아니라_UNKNOWN이다():
    v = judge(NOW, None, _pos())
    assert v["level"] == "UNKNOWN" and v["rc"] == RC_UNKNOWN


def test_포지션_파일이_없으면_UNKNOWN이다():
    v = judge(NOW, _hb(), None)
    assert v["rc"] == RC_UNKNOWN


def test_입력이_없어도_미청산이_확인되면_CRITICAL이_이긴다():
    v = judge(NOW, None, _pos("LONG", 1))
    assert v["rc"] == RC_UNCLOSED


# ── ③ 하트비트 파일 (G-1) ────────────────────────────────────────────────

def test_워치독이_하트비트_파일을_쓴다():
    d = tempfile.mkdtemp()
    hb = os.path.join(d, "heartbeat_MW0601_20260819.json")
    w = FreezeWatchdog(
        beat_fn=lambda: __import__("time").time(),
        fault_log_path=os.path.join(d, "fault.log"),
        ts_heartbeat=False,
        heartbeat_path=hb,
        on_fire=lambda: None,
    )
    w.check_once(now=datetime.datetime(2026, 8, 19, 10, 0, 0))
    with open(hb, encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["pid"] == os.getpid()
    assert payload["beat_age_sec"] is not None
    assert payload["watching"] is True


def test_하트비트_미시작이면_나이가_0이_아니라_null이다():
    # `if not beat`(epoch 0.0 falsy) 계열 혼동의 파일 출력 판. 0으로 쓰면
    # 밖에서 읽는 F-2 가드가 "방금 갱신됨"으로 오독한다.
    d = tempfile.mkdtemp()
    hb = os.path.join(d, "hb.json")
    w = FreezeWatchdog(
        beat_fn=lambda: None,
        fault_log_path=os.path.join(d, "fault.log"),
        ts_heartbeat=False,
        heartbeat_path=hb,
        on_fire=lambda: None,
    )
    w.check_once(now=datetime.datetime(2026, 8, 19, 10, 0, 0))
    with open(hb, encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["beat_age_sec"] is None
    assert payload["beat_epoch"] is None


def test_하트비트_경로가_None이면_아무것도_쓰지_않는다():
    d = tempfile.mkdtemp()
    w = FreezeWatchdog(
        beat_fn=lambda: __import__("time").time(),
        fault_log_path=os.path.join(d, "fault.log"),
        ts_heartbeat=False,
        heartbeat_path=None,
        on_fire=lambda: None,
    )
    w.check_once(now=datetime.datetime(2026, 8, 19, 10, 0, 0))
    assert not [f for f in os.listdir(d) if f.endswith(".json")]


# ── ④ 배선 ────────────────────────────────────────────────────────────────

def test_런처가_사이드카를_띄운다():
    """`start_mireuk.bat`이 가드를 별도 프로세스로 기동하는지 — 배선이 빠지면
    스크립트가 있어도 아무도 부르지 않는다(FP-CRITICAL·TOX-SEVERE-SPREAD 전례)."""
    with open(os.path.join(_ROOT, "start_mireuk.bat"), encoding="utf-8") as f:
        bat = f.read()
    assert "force_flat_guard.py" in bat
    assert "START" in bat.split("force_flat_guard.py")[0][-400:]


def test_2단계_주문_경로는_아직_없다():
    """1단계는 알림 전용이다. 브로커 주문 코드가 섞여 들어오면 즉시 깨진다."""
    from config.settings import FORCE_FLAT_GUARD_ORDER_ENABLED
    assert FORCE_FLAT_GUARD_ORDER_ENABLED is False
    with open(os.path.join(_ROOT, "scripts", "force_flat_guard.py"), encoding="utf-8") as f:
        src = f.read()
    for banned in ("send_order", "SendOrder", "CpTd0311", "broker."):
        assert banned not in src, "가드가 주문 경로에 손대고 있다: %s" % banned


def test_수동_실행은_마커를_남기지_않는다():
    """`--once` 진단이 다음날 증거 인벤토리에 "경보"로 섞이면 진짜 15:12 발화와
    구분되지 않는다 — 개발 중 실제로 운영 `data/`를 그렇게 오염시켰다."""
    import tempfile
    from scripts.force_flat_guard import emit
    d = tempfile.mkdtemp()
    v = {"level": "CRITICAL", "rc": RC_UNCLOSED, "headline": "테스트", "details": []}
    emit(d, datetime.date(2026, 8, 19), v, popup=False, manual=True)
    assert not os.path.exists(os.path.join(d, "data", "force_flat_alert_20260819.txt"))
    # 로그에는 남는다 — 정보가 사라지는 것이 아니라 마커만 안 만드는 것이다
    assert os.path.exists(os.path.join(d, "logs", "force_flat_guard_20260819.log"))


def test_예약_실행은_마커를_남긴다():
    import tempfile
    from scripts.force_flat_guard import emit
    d = tempfile.mkdtemp()
    v = {"level": "CRITICAL", "rc": RC_UNCLOSED, "headline": "테스트", "details": []}
    emit(d, datetime.date(2026, 8, 19), v, popup=False, manual=False)
    assert os.path.exists(os.path.join(d, "data", "force_flat_alert_20260819.txt"))


# ── ⑤ 감시 개시 기록 (480차 후속4) ────────────────────────────────────────

def test_감시_개시가_파일에_남는다():
    """가드의 콘솔은 START /MIN 최소화 창이라 아무도 보지 않는다. 기동 줄이
    파일에 없으면 "사이드카가 장중에 죽었다"와 "런처가 아예 안 띄웠다"를
    구분할 수 없다 — 감시자가 스스로 조용한 부재에 빠지는 형태다."""
    import tempfile
    from scripts.force_flat_guard import log_armed
    d = tempfile.mkdtemp()
    assert log_armed(d, datetime.date(2026, 8, 20), "15:12", 180.0, pid=4242) is True
    with open(os.path.join(d, "logs", "force_flat_guard_20260820.log"),
              encoding="utf-8") as f:
        line = f.read()
    assert "ARMED" in line
    assert "pid=4242" in line
    assert "15:12" in line
    assert "주문 없음" in line


def test_대기_경로가_ARMED를_부른다():
    """호출 배선이 빠지면 헬퍼만 있고 아무도 안 부르는 죽은 코드가 된다."""
    import ast as _ast
    with open(os.path.join(_ROOT, "scripts", "force_flat_guard.py"),
              encoding="utf-8") as f:
        tree = _ast.parse(f.read())
    called = [n for n in _ast.walk(tree)
              if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
              and n.func.id == "log_armed"]
    assert called, "log_armed() 호출부가 없다 — 기동 기록이 죽은 코드다"


def test_ARMED_기록은_마커가_아니다():
    """기동 사실은 `logs/`에만 남는다. `data/`에 남기면 일일 점검이 매일
    '경보'로 읽는다 — 마커는 이상이 있을 때만 만든다."""
    import tempfile
    from scripts.force_flat_guard import log_armed
    d = tempfile.mkdtemp()
    log_armed(d, datetime.date(2026, 8, 20), "15:12", 180.0)
    assert not os.path.isdir(os.path.join(d, "data")) or         not os.listdir(os.path.join(d, "data"))
