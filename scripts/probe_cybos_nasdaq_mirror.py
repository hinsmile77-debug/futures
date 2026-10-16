"""
Cybos Plus 로 나스닥 선물(MNQ/NQ)을 대신할 수 있는 시세 경로 프로브 — 읽기 전용, 주문 없음.

배경: Cybos Plus 공식 문서에는 해외선물 시세·차트 객체가 없다. 그러나 로컬 코드 마스터
(CpUtil.CpUsCode, 서버 TR 없음)에 `ENXH | E-Mini Nasdaq 100`(UsType 3) 이 있다.
이것이 KST 장중에 움직이는 선물 시세인지, 지연인지, 분 단위 이력을 주는지를 확인한다.
함께 국내 상장 「거울상」 ETF(KRX)의 1분봉이 StockChart 로 나오는지도 본다.

⚠ 장중(08:45–15:35)에 돌리지 말 것 — 라이브 엔진과 Cybos 요청 한도를 나눠 쓴다.
   CME Globex 는 KST 15:35 이후에도 거래 중이라 장후 실행으로도 판별된다.

사용:
    conda run -n py37_32 python -X utf8 scripts/probe_cybos_nasdaq_mirror.py [--watch-sec 120]
출력: 콘솔 + logs/YYYYMMDD_NASDAQ_MIRROR_PROBE.log
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys
import time

import pythoncom
import win32com.client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from utils.analysis_db import guard_intraday  # noqa: E402  (장중 차단 관례 재사용)

WORLD_CODES = ["ENXH", "NDX", "COMP", "SPX"]          # CpUsCode 실측 코드
MIRROR_ETFS = [                                       # CpStockCode 실측 코드
    ("A304940", "KODEX 미국나스닥100선물(H)"),        # 정방향 · 선물 기반 · 환헤지
    ("A409810", "KODEX 미국나스닥100선물인버스(H)"),  # 거울상(역방향)
    ("A409820", "KODEX 미국나스닥100레버리지(합성 H)"),
    ("A133690", "TIGER 미국나스닥100"),               # 환노출 — 환율 성분 섞임
]

_lines = []


def out(msg: str) -> None:
    print(msg)
    _lines.append(msg)


def dump_obj(obj, label: str, max_hdr: int = 20, max_fld: int = 12, max_rows: int = 15) -> None:
    hdr = []
    for i in range(max_hdr):
        try:
            hdr.append((i, obj.GetHeaderValue(i)))
        except Exception:
            break
    out("[%s] header %s" % (label, hdr))
    try:
        n = int(obj.GetHeaderValue(0) or 0)
    except Exception:
        n = 0
    rows = 0
    for r in range(max_rows):
        vals = []
        for f in range(max_fld):
            try:
                vals.append(obj.GetDataValue(f, r))
            except Exception:
                break
        if not vals or all(v in (None, "", 0) for v in vals):
            break
        rows += 1
        out("[%s] row%02d %s" % (label, r, vals))
    out("[%s] rows_shown=%d (header0=%s)" % (label, rows, n))


def probe_8312(code: str) -> None:
    """CpFore8312(문서명 CpSvr8312): 1=시간대별 — 분 단위 시계열인지(간격·최신 시각) 확인."""
    o = win32com.client.Dispatch("Dscbo1.CpFore8312")
    o.SetInputValue(0, code)
    o.SetInputValue(1, ord("1"))
    o.SetInputValue(2, 30)
    o.BlockRequest()
    out("[8312 %s] status=%s msg=%s" % (code, o.GetDibStatus(), o.GetDibMsg1()))
    dump_obj(o, "8312 " + code)


class _WorldHandler:
    """COM 콜백: 상태 저장만 (절대원칙 §4 — dynamicCall/emit 금지)."""
    ticks = []

    def OnReceived(self):
        try:
            self.ticks.append((time.time(), [self.client.GetHeaderValue(i) for i in range(13)]))
        except Exception as e:  # 저장 실패도 남긴다(계측 4원칙 ④)
            self.ticks.append((time.time(), "ERR %s" % e))


def watch_worldcur(code: str, sec: int) -> None:
    obj = win32com.client.Dispatch("CpSysDib.WorldCur")
    h = win32com.client.WithEvents(obj, _WorldHandler)
    h.client = obj
    h.ticks = []
    obj.SetInputValue(0, code)
    obj.Subscribe()
    t0 = time.time()
    while time.time() - t0 < sec:
        pythoncom.PumpWaitingMessages()
        time.sleep(0.05)
    obj.Unsubscribe()
    n = len(h.ticks)
    out("[WorldCur %s] %d틱 / %ds" % (code, n, sec))
    for t, v in h.ticks[:5] + (h.ticks[-3:] if n > 8 else []):
        out("  %s %s" % (datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S"), v))
    # 판정 힌트: 0틱 = 실시간 아님(또는 미지원) / 현지시각(11) 과 수신시각 차 = 지연 추정치


def probe_etf_minutes(code: str, name: str) -> None:
    o = win32com.client.Dispatch("CpSysDib.StockChart")
    o.SetInputValue(0, code)
    o.SetInputValue(1, ord("2"))          # 개수 기준
    o.SetInputValue(4, 10)
    o.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 날짜 시간 시 고 저 종 거래량
    o.SetInputValue(6, ord("m"))
    o.SetInputValue(7, 1)
    o.SetInputValue(9, ord("1"))
    o.BlockRequest()
    n = o.GetHeaderValue(3)
    out("[ETF %s %s] status=%s n=%s" % (code, name, o.GetDibStatus(), n))
    for r in range(min(int(n or 0), 5)):
        out("  " + str([o.GetDataValue(f, r) for f in range(7)]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch-sec", type=int, default=120)
    a = ap.parse_args()
    guard_intraday("probe_cybos_nasdaq_mirror")

    cyb = win32com.client.Dispatch("CpUtil.CpCybos")
    out("connect=%s  %s" % (cyb.IsConnect, datetime.datetime.now()))
    if not cyb.IsConnect:
        out("Cybos 미연결 — 종료")
        return 1
    uc = win32com.client.Dispatch("CpUtil.CpUsCode")
    for c in WORLD_CODES:
        out("[CpUsCode] %s = %s" % (c, uc.GetNameByUsCode(c)))
    for c in WORLD_CODES:
        probe_8312(c)
        time.sleep(0.5)
    for c in ("ENXH", "NDX"):
        watch_worldcur(c, a.watch_sec)
    for c, nm in MIRROR_ETFS:
        probe_etf_minutes(c, nm)
        time.sleep(0.5)

    path = os.path.join(ROOT, "logs", datetime.date.today().strftime("%Y%m%d") + "_NASDAQ_MIRROR_PROBE.log")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(str(x) for x in _lines))
    out("saved: " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
