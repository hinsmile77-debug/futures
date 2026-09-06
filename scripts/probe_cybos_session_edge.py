# -*- coding: utf-8 -*-
# scripts/probe_cybos_session_edge.py — 세션 경계(개장·마감 단일가) 실시간 원천 프로브
"""[MW0601 533차 / 풀타임 수집 Phase 0] 개장 08:45 · 마감 15:35~15:45 구간에
`Dscbo1.FutureCurOnly` / `CpSysDib.FutureJpBid` 가 **무엇을 보내는지** 실측한다.

왜 프로브가 필요한가
--------------------
설계 전제 4개가 문서(2014년 스냅샷)만으로는 확정되지 않는다:

  P0-1  15:35~15:45 마감 단일가 중 체결틱이 오는가 / 15:45 체결틱에 헤더 28=30이 찍히는가
  P0-2  08:44:30 구독 시 08:45:00 개장 체결틱(헤더 28=10)이 오는가, 누적거래량 점프 크기
  P0-3  `CpSysDib.FutOptChart` 분봉이 08:45 봉에 개장 체결을 포함하고 15:45 봉을 따로 주는가
  P0-4  메인이 도는 동안 **두 번째 프로세스**가 같은 코드를 구독할 수 있는가(안 C 전제)

이 스크립트는 **DB를 열지 않는다** — 456차 규약(장중 라이브 DB 분석 금지)의 IO 압박
유형이 아니다. 출력은 `logs/session_edge_<날짜>_<시각>.jsonl` 과 요약 `.txt` 뿐이다.
주문·계좌 TR 도 호출하지 않는다.

사용법 (py37_32 · Cybos Plus 로그인 · 관리자 권한)
--------------------------------------------------
  P0-1  15:30 기동:  python scripts/probe_cybos_session_edge.py --until 15:47
  P0-2  08:43 기동:  python scripts/probe_cybos_session_edge.py --until 08:48
  P0-4  장중 5분:    python scripts/probe_cybos_session_edge.py --until +5m --coexist
  P0-3  장후/주말:   python scripts/probe_cybos_session_edge.py --chart 20260904

`--code` 를 주지 않으면 `data/ui_prefs.json:symbol_code` 의 앞 5자(A0569000 → A0569)를
쓴다 — 메인이 구독하는 코드와 같은 규칙(`broker_runtime_service._normalize_ui_code`).

판정 가이드 (요약 파일에 그대로 찍힌다)
---------------------------------------
  · 15:45:xx 틱 1건 이상 + auction_code=30  → Phase 2(프로세스 수명 +6분)로 마감 체결 회수 가능
  · 15:35~15:44 틱 0건 + 호가 이벤트만 변동 → 예상체결가는 호가 원천. 봉 0행이 정상
  · 08:45:00 틱에 auction_code=10          → 08:44:30 구독으로 개장 체결 회수 가능
  · --coexist 에서 subscribe 성공 + 틱 수신 → 별도 수집 프로세스(안 C) 기술적 가능

⚠ 자동으로 아무것도 확정하지 않는다. 사람이 요약을 읽고 결정한다(9/8 종료 후 안건).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

TICK_FIELDS = list(range(0, 32))          # FutureCurOnly 헤더 0~31 전량
HOGA_FIELDS = list(range(0, 41))          # FutureJpBid 헤더 — 예상가 후보 탐색용 상한
EDGE_WINDOWS = (                           # 이 창 안에서는 틱 전량·호가 30초마다 덤프
    (_dt.time(8, 30), _dt.time(9, 1)),
    (_dt.time(15, 30), _dt.time(15, 50)),
)
AUCTION_NAMES = {10: "시가단일가", 11: "시가단일가연장", 20: "장중단일가", 30: "종가단일가"}


def _in_edge(t: _dt.time) -> bool:
    return any(a <= t < b for a, b in EDGE_WINDOWS)


def _default_code() -> str:
    try:
        with open(os.path.join(_ROOT, "data", "ui_prefs.json"), encoding="utf-8") as f:
            raw = str(json.load(f).get("symbol_code", "")).strip()
        if len(raw) == 8 and raw.endswith("000"):
            return raw[:-3]
        return raw
    except Exception:
        return ""


def _parse_until(spec: str) -> _dt.datetime:
    now = _dt.datetime.now()
    if spec.startswith("+") and spec.endswith("m"):
        return now + _dt.timedelta(minutes=int(spec[1:-1]))
    hh, mm = spec.split(":")[:2]
    tgt = now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
    if tgt <= now:
        tgt += _dt.timedelta(days=1)
    return tgt


class EdgeProbe(object):
    """`CybosAPI.create_subscription` 의 owner — 콜백에서는 읽기·기록만 한다(§4)."""

    def __init__(self, api, code: str, out_path: str):
        self.api = api
        self.code = code
        self.out = open(out_path, "a", encoding="utf-8")
        self.tick_sub = None
        self.hoga_sub = None
        self.n_tick = 0
        self.n_hoga = 0
        self.per_min_ticks = {}
        self.auction_ticks = []          # (raw_time, price, cum_vol, auction_code, recv_type)
        self.first_tick = None
        self.last_tick = None
        self._last_hoga_dump = 0.0
        self._last_hoga_vals = None
        self.hoga_changes_in_close_auction = 0
        self.last_cum_vol = None
        self.cum_vol_jumps = []          # (raw_time, from, to) — 개장 체결 수량 추정

    # ── 구독 ──────────────────────────────────────────────────────────────
    def start(self):
        self.tick_sub = self.api.create_subscription(
            progid="Dscbo1.FutureCurOnly", input_values={0: self.code},
            owner=self, event_name="tick", latest=False)
        self.hoga_sub = self.api.create_subscription(
            progid="CpSysDib.FutureJpBid", input_values={0: self.code},
            owner=self, event_name="hoga", latest=False)

    def stop(self):
        for s in (self.tick_sub, self.hoga_sub):
            if s is not None:
                try:
                    s.unsubscribe()
                except Exception:
                    pass
        self.out.close()

    # ── 콜백 ──────────────────────────────────────────────────────────────
    def _handle_subscription_event(self, event_name, sink):
        try:
            if event_name == "tick" and self.tick_sub is not None:
                self._on_tick(self.tick_sub.com_object)
            elif event_name == "hoga" and self.hoga_sub is not None:
                self._on_hoga(self.hoga_sub.com_object)
        except Exception as e:      # 콜백 안에서 예외를 밖으로 내지 않는다
            self._write({"kind": "error", "event": event_name, "err": repr(e)})

    @staticmethod
    def _dump(obj, fields):
        out = {}
        for i in fields:
            try:
                out[str(i)] = obj.GetHeaderValue(i)
            except Exception:
                out[str(i)] = None       # 미정의 인덱스 — None 으로 구분(0 아님)
        return out

    def _write(self, rec):
        rec["wall"] = _dt.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.out.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        self.out.flush()

    def _on_tick(self, obj):
        self.n_tick += 1
        now_t = _dt.datetime.now().time()
        edge = _in_edge(now_t)
        d = self._dump(obj, TICK_FIELDS) if (edge or self.n_tick <= 5) else self._dump(obj, [1, 13, 15, 28, 30])
        raw_time = str(d.get("15", ""))
        price = d.get("1")
        cum_vol = d.get("13")
        ac = d.get("28")
        try:
            ac_i = int(ac) if ac not in (None, "") else None
        except Exception:
            ac_i = None
        rec = {"kind": "tick", "n": self.n_tick, "edge": edge, "raw_time": raw_time,
               "price": price, "cum_vol": cum_vol, "auction_code": ac_i,
               "recv_type": d.get("30")}
        if edge or self.n_tick <= 5 or (ac_i not in (None, 0)):
            rec["fields"] = d
        self._write(rec)

        key = raw_time[:-2] if len(raw_time) >= 5 else raw_time
        self.per_min_ticks[key] = self.per_min_ticks.get(key, 0) + 1
        if self.first_tick is None:
            self.first_tick = (raw_time, price, cum_vol)
        self.last_tick = (raw_time, price, cum_vol)
        if ac_i not in (None, 0):
            self.auction_ticks.append((raw_time, price, cum_vol, ac_i, d.get("30")))
            print("  ★ 단일가 체결틱 raw_time=%s price=%s cum_vol=%s auction_code=%s(%s)" % (
                raw_time, price, cum_vol, ac_i, AUCTION_NAMES.get(ac_i, "?")), flush=True)
        try:
            cv = int(cum_vol)
            if self.last_cum_vol is not None and cv - self.last_cum_vol >= 50:
                self.cum_vol_jumps.append((raw_time, self.last_cum_vol, cv))
            self.last_cum_vol = cv
        except Exception:
            pass
        if edge or self.n_tick % 100 == 0:
            print("  tick #%d raw_time=%s price=%s cum_vol=%s ac=%s" % (
                self.n_tick, raw_time, price, cum_vol, ac_i), flush=True)

    def _on_hoga(self, obj):
        self.n_hoga += 1
        now = time.time()
        now_t = _dt.datetime.now().time()
        if not _in_edge(now_t):
            if self.n_hoga <= 3:
                self._write({"kind": "hoga", "n": self.n_hoga, "fields": self._dump(obj, HOGA_FIELDS)})
            return
        vals = self._dump(obj, HOGA_FIELDS)
        # 마감 단일가(15:35~15:45) 동안 체결틱 없이 호가 필드가 변하면 그 필드가 예상가 후보다.
        if _dt.time(15, 35) <= now_t < _dt.time(15, 45) and self._last_hoga_vals is not None:
            changed = [k for k in vals if vals[k] != self._last_hoga_vals.get(k)]
            if changed:
                self.hoga_changes_in_close_auction += 1
                self._write({"kind": "hoga_change", "n": self.n_hoga, "changed": changed,
                             "vals": {k: vals[k] for k in changed}})
        self._last_hoga_vals = vals
        if now - self._last_hoga_dump >= 30.0:
            self._last_hoga_dump = now
            self._write({"kind": "hoga", "n": self.n_hoga, "fields": vals})

    # ── 요약 ──────────────────────────────────────────────────────────────
    def summary(self, coexist: bool) -> str:
        lines = []
        lines.append("code=%s  ticks=%d  hoga_events=%d" % (self.code, self.n_tick, self.n_hoga))
        lines.append("first_tick=%s  last_tick=%s" % (self.first_tick, self.last_tick))
        edge_keys = sorted(k for k in self.per_min_ticks
                           if k[:4] in ("0844", "0845", "0846", "0847", "1533", "1534", "1535",
                                        "1536", "1537", "1538", "1539", "1540", "1541", "1542",
                                        "1543", "1544", "1545", "1546", "1547")
                           or k[:3] in ("844", "845", "846", "847"))
        lines.append("edge per-minute ticks: " + ", ".join("%s=%d" % (k, self.per_min_ticks[k]) for k in edge_keys))
        lines.append("auction ticks (헤더28≠0): %d" % len(self.auction_ticks))
        for t in self.auction_ticks[:20]:
            lines.append("   raw_time=%s price=%s cum_vol=%s code=%s(%s) recv=%s" % (
                t[0], t[1], t[2], t[3], AUCTION_NAMES.get(t[3], "?"), t[4]))
        lines.append("cum_vol jumps ≥50 in one tick: %s" % (self.cum_vol_jumps[:10],))
        lines.append("hoga field changes during 15:35~15:45 (예상가 후보 신호): %d" % self.hoga_changes_in_close_auction)
        lines.append("")
        lines.append("판정 가이드:")
        has_close = any(str(t[0]).startswith("1545") and t[3] == 30 for t in self.auction_ticks)
        has_open = any(str(t[0]).startswith("845") or str(t[0]).startswith("0845") for t in self.auction_ticks
                       if t[3] in (10, 11))
        lines.append("  P0-1 15:45 종가단일가 체결틱(28=30): %s" % ("관측됨 → Phase 2 진행 근거" if has_close else "미관측(시간창 밖이면 무의미)"))
        lines.append("  P0-2 08:45 시가단일가 체결틱(28=10/11): %s" % ("관측됨 → 08:44:30 구독으로 회수 가능" if has_open else "미관측(시간창 밖이면 무의미)"))
        if coexist:
            lines.append("  P0-4 병행 구독: %s" % ("성공(틱 %d건) → 안 C 기술적 가능" % self.n_tick if self.n_tick > 0 else "틱 0건 — 구독 실패 또는 장외"))
        return "\n".join(lines)


def run_chart(api_mod, code: str, ymd: str) -> int:
    """P0-3: FutOptChart 분봉 TR 1회 — 해당 날짜 봉의 첫/끝·개장·마감 봉을 출력."""
    fields = [0, 1, 2, 3, 4, 5, 8, 27]
    ext_fields = fields + [10, 11]       # 누적매도/매수 — 분·틱에서만 제공(문서)

    def _reader(obj):
        n = api_mod._safe_int(obj.GetHeaderValue(3))
        rows = []
        for i in range(n):
            rows.append([obj.GetDataValue(c, i) for c in range(len(_reader.fields))])
        return rows

    for flist in (ext_fields, fields):
        _reader.fields = flist
        inputs = [(0, code), (1, ord("2")), (4, 900), (5, flist), (6, ord("m")), (7, 1), (8, ord("0"))]
        try:
            ret, status, msg, data = api_mod._run_block_request(
                "CpSysDib.FutOptChart", inputs, data_reader=_reader, timeout_sec=30)
        except Exception as e:
            print("[chart] 요청 예외 fields=%s: %r" % (flist, e))
            continue
        if ret not in (0, None) or status != 0 or not data:
            print("[chart] 실패 fields=%s ret=%s status=%s msg=%s rows=%s" % (flist, ret, status, msg, len(data or [])))
            continue
        print("[chart] fields=%s rows=%d" % (flist, len(data)))
        day_rows = [r for r in data if str(r[0]) == ymd]
        day_rows.sort(key=lambda r: int(r[1]))
        print("  %s 봉 수=%d" % (ymd, len(day_rows)))
        if not day_rows:
            print("  (해당 날짜 없음 — 최근 3행: %s)" % data[:3])
            return 1
        hdr = "  " + " ".join("%10s" % f for f in ("date", "time", "open", "high", "low", "close", "vol", "oi", "cum_sell", "cum_buy")[:len(flist)])
        print(hdr)
        def _p(r):
            print("  " + " ".join("%10s" % v for v in r))
        for r in day_rows[:3]:
            _p(r)
        print("  ...")
        for r in day_rows[-4:]:
            _p(r)
        times = [int(r[1]) for r in day_rows]
        print("  first_time=%s last_time=%s" % (times[0], times[-1]))
        print("  08:45 봉 존재=%s  15:45 봉 존재=%s  15:35~15:44 봉 수=%d" % (
            845 in times or 84500 in times, 1545 in times or 154500 in times,
            sum(1 for t in times if 1535 <= (t if t < 10000 else t // 100) <= 1544)))
        return 0
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--code", default="", help="실시간 코드(예: A0569). 기본: ui_prefs.json symbol_code 앞 5자")
    ap.add_argument("--until", default="", help="HH:MM 또는 +Nm. 이 시각까지 구독 유지")
    ap.add_argument("--coexist", action="store_true", help="메인 실행 중 병행 구독 시험(P0-4) — 요약에 표기만")
    ap.add_argument("--chart", default="", help="YYYYMMDD — FutOptChart 분봉 TR 1회(P0-3). 구독 안 함")
    args = ap.parse_args()

    if platform.architecture()[0] != "32bit":
        print("[중단] 32-bit Python(py37_32)에서 실행할 것 — Cybos COM 요구사항")
        return 2
    try:
        import pythoncom
        import win32com.client as win32
    except ImportError:
        print("[중단] pywin32(32-bit) 없음")
        return 2

    from collection.cybos import api_connector as api_mod

    cyb = win32.Dispatch("CpUtil.CpCybos")
    if not cyb.IsConnect:
        print("[중단] Cybos Plus 미연결(IsConnect=0). 로그인 + 관리자 권한으로 실행할 것.")
        return 1

    code = (args.code or _default_code()).strip()
    if not code:
        print("[중단] 코드를 정하지 못했다 — --code A0569 형태로 지정")
        return 1
    print("code=%s  now=%s  coexist=%s" % (code, _dt.datetime.now().strftime("%H:%M:%S"), args.coexist))

    if args.chart:
        return run_chart(api_mod, code, args.chart)

    if not args.until:
        print("[중단] --until HH:MM 또는 +Nm 필요 (--chart 모드가 아니면)")
        return 1
    until = _parse_until(args.until)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M")
    os.makedirs(os.path.join(_ROOT, "logs"), exist_ok=True)
    out_path = os.path.join(_ROOT, "logs", "session_edge_%s.jsonl" % stamp)
    sum_path = os.path.join(_ROOT, "logs", "session_edge_%s_summary.txt" % stamp)

    api = api_mod.CybosAPI()          # CoInitialize 만. connect()/TradeInit 은 호출하지 않는다
    probe = EdgeProbe(api, code, out_path)
    print("구독 시작 → %s 까지 유지. 기록: %s" % (until.strftime("%H:%M:%S"), out_path))
    try:
        probe.start()
    except Exception as e:
        print("[중단] 구독 실패: %r  (coexist=%s — 병행 구독이 막혔다면 안 C 전제가 깨진다)" % (e, args.coexist))
        probe.stop()
        return 1
    try:
        while _dt.datetime.now() < until:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("중단(Ctrl+C) — 요약 작성")
    finally:
        probe.stop()
    text = probe.summary(args.coexist)
    with open(sum_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print("\n=== 요약 (%s) ===\n%s" % (sum_path, text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
