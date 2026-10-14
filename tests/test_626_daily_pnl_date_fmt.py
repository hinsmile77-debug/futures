# -*- coding: utf-8 -*-
"""[MW0602 626차] CpTd6197 기준일자 형식 재시도 — 실거래 계좌 「조회된 내용 없음」 대응.

배경(2026-10-14 실측): 실거래 계좌 783293269 에서 `[CybosDailyPnl] request failed …
status=-1 msg=12242 조회된 내용이 없습니다` 가 하루 종일 12건, 성공 0건. 모의계좌는
같은 입력(`yyMMdd`)으로 정상 응답해 왔다. 원인은 **미확정**(날짜 자릿수 가설)이라
기본 형식은 바꾸지 않고, `12242` 일 때만 다른 형식으로 1회 재시도한다.

고정하는 불변식:
  ① 기본 형식이 성공하면 요청은 1회뿐이다(모의계좌 정상 경로 무변경).
  ② `12242` → 대체 형식 성공이면 그 형식을 계좌별로 기억하고, 다음 호출은 처음부터 그 형식.
  ③ 두 형식 모두 실패하면 그날은 재시도하지 않는다(BlockRequest 낭비 방지)
     — 그리고 **빈 dict**(미수신)를 돌려준다. 0 을 지어내지 않는다(계측 4원칙 ②).
  ④ `12242` 가 아닌 실패(권한·연결 등)는 재시도하지 않는다 — 형식 문제가 아니다.
"""
import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import collection.cybos.api_connector as ac  # noqa: E402

_NO_DATA = "12242 조회된 내용이 없습니다. (ciisvr66)(cii.cif.cstpftrt.selfoaccptthdys)"
_HEADERS = {0: "783293269", 1: "100000000", 2: "99349340", 5: "0", 6: "-647000", 9: "99349340"}


def _api():
    api = object.__new__(ac.CybosAPI)
    api._daily_pnl_date_fmt = {}
    api._daily_pnl_both_failed = {}
    return api


def _install(monkeypatch, responder):
    calls = []

    def fake(progid, input_pairs, data_reader=None, timeout_sec=None):
        date_in = dict(input_pairs)[1]
        calls.append(date_in)
        return responder(date_in)

    monkeypatch.setattr(ac, "_run_block_request", fake)
    return calls


def test_기본형식_성공이면_1회만_요청(monkeypatch):
    calls = _install(monkeypatch, lambda d: (0, 0, "", dict(_HEADERS)))
    out = _api()._request_futures_daily_pnl_summary("777020696")
    assert calls == [time.strftime("%y%m%d")]
    assert out["실현손익"] == "-647000"


def test_12242면_8자리로_재시도하고_기억한다(monkeypatch):
    six, eight = time.strftime("%y%m%d"), time.strftime("%Y%m%d")
    calls = _install(monkeypatch, lambda d: (0, 0, "", dict(_HEADERS)) if d == eight
                     else (0, -1, _NO_DATA, {}))
    api = _api()
    out = api._request_futures_daily_pnl_summary("783293269")
    assert calls == [six, eight]
    assert out["총매매"] == "100000000"
    assert api._daily_pnl_date_fmt["783293269"] == "%Y%m%d"
    # 다음 호출은 처음부터 성공 형식 — 실패 요청을 다시 보내지 않는다
    del calls[:]
    api._request_futures_daily_pnl_summary("783293269")
    assert calls == [eight]


def test_두형식_모두_실패면_그날_재시도_생략_그리고_미수신(monkeypatch):
    calls = _install(monkeypatch, lambda d: (0, -1, _NO_DATA, {}))
    api = _api()
    assert api._request_futures_daily_pnl_summary("783293269") == {}
    assert len(calls) == 2
    del calls[:]
    assert api._request_futures_daily_pnl_summary("783293269") == {}
    assert len(calls) == 1


def test_12242_아닌_실패는_재시도하지_않는다(monkeypatch):
    calls = _install(monkeypatch, lambda d: (0, -1, "계좌 비밀번호 오류", {}))
    assert _api()._request_futures_daily_pnl_summary("783293269") == {}
    assert len(calls) == 1
