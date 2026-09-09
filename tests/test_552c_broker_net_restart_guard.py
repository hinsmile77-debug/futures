# -*- coding: utf-8 -*-
"""[MW0601 552-10] 롤오버 가드가 **세션 재시작을 넘어서** 살아 있는가.

무엇이 뚫렸나 — 가드가 아니라 **기준점**이었다
------------------------------------------------
501차(D1/D2)는 「예탁현금은 당일 시가 고정」 불변식으로 롤오버를 판별하도록
파서와 라이브 저장부 양쪽에 가드를 넣었다. 그 가드는 정상 동작한다.
그런데 라이브 쪽 기준점 `_broker_dep_base_today` 는 **프로세스 인스턴스 상태**라
재시작이 지운다. 2026-09-07 실측:

    15:40:07  [DailyClose] → [BrokerNetEOD] net 축 이미 실측 기입됨 (-1,432,630)
    21:58:29  [System] DB 초기화 완료                  ← **새 프로세스**
    21:58:44  미륵이 — ... 시작
    21:58:45  첫 [CybosDailyPnl] = 롤오버 판독
              총매매(예탁) 34,984,962 / 총평가수익률(익일가) 34,598,332
              → 그 프로세스에겐 「그날 첫 판독」이라 불변식이 성립
              → _rolled=False → upsert_broker_net() 이 -386,630(= -수수료)로 덮어씀

그날 장중 판독은 예탁 36,417,563 고정 · 익일가 34,984,933 이므로 참값은
**-1,432,630** 이다. 엔진 net(-1,432,580)이 오히려 50원 차이로 맞는다.

⚠ `broker_net_krw` 는 **실전 전환기준 ① 의 판정 원천**이다(493차 F-1).
  이 결함은 「조용히 그럴듯한 값」이고, 틀린 방향이 **낙관**이다.

고친 방식 — 상태를 프로세스 밖에 둔다
--------------------------------------
① `fetch_broker_dep_base(date)` 로 그날 이미 기록된 `deposit_cash_krw`(당일 시가)를
   **DB 에서 승계**한다. 저녁 세션도 참 기준점을 얻는다.
② 승계도 못 하고 `BROKER_NET_SESSION_END`(15:35) 이후면 **저장하지 않는다** —
   그 판독이 시가인지 롤오버인지 알 방법이 없다. 모르면 쓰지 않는다(계측 4원칙 ②).

`entry_source` 가 재시작으로 `SYSTEM_AUTO` 로 되돌아가는 552-11 과 **같은 계열**이다:
포지션·값은 복원되는데 그것을 해석할 기준이 복원되지 않는다.
"""
from __future__ import print_function

import datetime
import io
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2026-09-07 실측값
DEP_OPEN = 36417563.0        # 장중 예탁현금(당일 시가, 08:41~14:44 고정)
NXT_OPEN = 34984933.0        # 장중 익일가예탁현금
TRUE_NET = NXT_OPEN - DEP_OPEN                      # -1,432,630
DEP_ROLL = 34984962.0        # 21:58 정산 후 롤오버된 예탁현금
NXT_ROLL = 34598332.0
BAD_NET = NXT_ROLL - DEP_ROLL                       # -386,630 (= -수수료)


# 🔴 [MW0602 552차 후속 체리픽 조정] 원본은 `upsert_broker_net(..., source="live")`
#   로 부른다. **이 브랜치의 시그니처에는 `source` 가 없다** — 그 인자는 552차가
#   아니라 MW0601 **498차**가 넣은 것이고 dev 는 498차를 이관하지 않았다.
#   `source="live"` 는 v9-dev 에서도 **기본값과 동일**하고, 이 브랜치 프로덕션
#   (`main.py` · `commission_rate_recon.py`)도 3인자로만 부른다 — 즉 이 검사가
#   보려는 것(기준점 없는 롤오버 판독이 net 을 −수수료로 뒤집는다)에 영향이 없다.
#   ⚠ 498차를 나중에 이관하면 이 인자를 되살릴 것.


def _tmp_db(monkeypatch):
    """격리된 trades.db 를 만들고 db_utils 를 그쪽으로 돌린다."""
    import utils.db_utils as D
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "trades.db")
    monkeypatch.setattr(D, "TRADES_DB", path, raising=False)
    monkeypatch.setattr(D, "is_krx_trading_date", lambda d: True, raising=False)
    D.init_daily_broker_pnl_db()
    return D, path


# ── ① DB 기준점 승계 ────────────────────────────────────────────────────────
def test_dep_base_survives_process_restart(monkeypatch):
    """장중 판독이 남긴 예탁현금을 새 프로세스가 DB 에서 승계한다."""
    D, _ = _tmp_db(monkeypatch)
    assert D.fetch_broker_dep_base("2026-09-07") is None, "행이 없으면 None(미측정)"

    D.upsert_broker_net("2026-09-07", DEP_OPEN, NXT_OPEN)
    assert D.fetch_broker_net("2026-09-07")["net_krw"] == TRUE_NET

    # 새 프로세스가 얻는 기준점 = 장중 시가여야 한다
    base = D.fetch_broker_dep_base("2026-09-07")
    assert base == DEP_OPEN, base

    # 그 기준점으로 21:58 판독을 재면 롤오버로 판별된다
    assert abs(DEP_ROLL - base) > 1.0, "롤오버 판독이 기준점과 같아 보인다"


def test_dep_base_none_is_not_zero(monkeypatch):
    """미측정은 None 이다 — 0 을 돌려주면 `if base:` 가 조용히 갈린다(계측 4원칙 ②)."""
    D, path = _tmp_db(monkeypatch)
    con = sqlite3.connect(path)
    con.execute("INSERT INTO daily_broker_pnl (date, pnl_krw, updated_at)"
                " VALUES ('2026-09-07', 0, '2026-09-07 15:40:00')")
    con.commit()
    con.close()
    assert D.fetch_broker_dep_base("2026-09-07") is None
    assert D.fetch_broker_dep_base("2026-01-01") is None


# ── ② 라이브 경로 배선 ──────────────────────────────────────────────────────
def _main_src():
    return io.open(os.path.join(_ROOT, "main.py"), encoding="utf-8").read()


def test_live_path_inherits_base_from_db():
    """라이브 저장부가 기준점을 DB 에서 승계하는지 소스로 고정한다.

    이 배선이 사라지면 저녁 세션이 다시 그날 net 을 수수료로 덮어쓴다 —
    2026-09-07 이 그렇게 오염됐다.
    """
    src = _main_src()
    assert "fetch_broker_dep_base" in src, "DB 기준점 승계가 배선돼 있지 않다"
    assert "BASE_FROM_DB" in src, "승계 사실을 로그로 남겨야 한다(계측 4원칙 ④)"
    assert "SKIP_NO_BASE" in src, "기준점 없는 마감 후 판독의 스킵 경로가 없다"
    # 501차 가드는 그대로 살아 있어야 한다
    assert "SKIP_ROLLOVER" in src
    assert 'getattr(self, "_broker_dep_base_today"' not in src


def test_session_end_boundary_parses_and_falls_back():
    """`BROKER_NET_SESSION_END` 파싱 + 폴백."""
    from config.settings import BROKER_NET_SESSION_END
    h, m = str(BROKER_NET_SESSION_END).split(":")
    end = datetime.time(int(h), int(m))
    assert end >= datetime.time(15, 20), (
        "만기일 마감 15:20 보다 이르면 정상 장중 판독을 버린다")
    # 21:58 은 경계 밖(= 기준점 없으면 저장 금지 구간)
    assert datetime.time(21, 58) >= end
    # 14:44 은 경계 안(= 정상 장중 판독)
    assert datetime.time(14, 44) < end


# ── ③ 사건 재현 — 가드가 없으면 어떻게 되는가 ────────────────────────────────
def test_rollover_write_would_flip_the_day_verdict(monkeypatch):
    """기준점을 못 얻은 채 롤오버 판독을 쓰면 그날 net 이 -수수료로 바뀐다.

    이 테스트는 **결함의 크기**를 고정한다 — 가드가 다시 약해졌을 때
    "얼마나 틀리는가"를 숫자로 보여 준다.
    """
    D, _ = _tmp_db(monkeypatch)
    D.upsert_broker_net("2026-09-07", DEP_OPEN, NXT_OPEN)
    assert D.fetch_broker_net("2026-09-07")["net_krw"] == TRUE_NET

    # 가드가 없었던 세계: 저녁 세션이 롤오버 판독을 그대로 쓴다
    D.upsert_broker_net("2026-09-07", DEP_ROLL, NXT_ROLL)
    assert D.fetch_broker_net("2026-09-07")["net_krw"] == BAD_NET
    assert BAD_NET - TRUE_NET == 1046000.0, "오차 크기가 바뀌었다 — 사건 재현 실패"
    assert BAD_NET > TRUE_NET, "틀린 방향이 낙관이라는 사실이 이 결함의 핵심이다"
