# -*- coding: utf-8 -*-
"""맥점 × 옵션 사다리 — 로컬 서버 (실시간 분 단위 + 날짜별 복기).

[MW0601 656차 / 2026-10-04]

왜 로컬 서버인가
  claude.ai 에 게시한 페이지는 이 PC 의 SQLite DB 를 읽을 수 없다. 장중 매분 갱신을
  하려면 DB 옆에서 도는 것이 필요하다. 표준 라이브러리만 쓴다.

실행
  conda run -n py310_64 python tools/maekjeom_ladder/server.py          # http://127.0.0.1:8765
  conda run -n py310_64 python tools/maekjeom_ladder/server.py --open   # 브라우저까지 연다
  (또는 MAEKJEOM_LADDER.bat)

안전
  · 127.0.0.1 에만 묶는다 — 다른 PC 에서 접속할 수 없다.
  · 모든 DB 는 `mode=ro`. 쓰기 없음. 주문·COM 없음.
  · 장중 raw_data.db 접근은 오늘 봉 ts 범위 증분 조회 하나뿐(456차, ladder_data.py 머리말).
  · 오늘 데이터는 20초 캐시 — 브라우저 여러 개가 열려도 DB 조회는 20초에 한 번.

API
  GET /                 화면
  GET /api/dates        달력용 날짜·원천 가용 목록
  GET /api/day?date=    하루치 JSON (live=true 면 화면이 60초마다 다시 부른다)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ladder_data as L  # noqa: E402

LIVE_TTL_SEC = 20
_cache = {}                 # date -> (built_at_epoch, json_bytes, live)
_cache_lock = threading.Lock()
_DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _day_json(day):
    now = time.time()
    with _cache_lock:
        hit = _cache.get(day)
        if hit and (not hit[2] or now - hit[0] < LIVE_TTL_SEC):
            return hit[1]
    payload = L.build_day(day)
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    with _cache_lock:
        # 오늘이 아직 장 전·중이면 「live」로 캐시해 TTL 이 지나면 다시 짓는다.
        # 지난 날짜는 영구 캐시 — 단 오늘 날짜는 장 마감 뒤에도 장후 재수집(16:20)이
        # 값을 바꾸므로 TTL 을 적용한다.
        is_today = day == _dt.date.today().isoformat()
        _cache[day] = (now, body, payload["live"] or is_today)
    return body


class H(BaseHTTPRequestHandler):
    server_version = "MaekjeomLadder/1.0"

    def log_message(self, fmt, *args):      # 매분 요청이 콘솔을 덮지 않게 오류만 찍는다
        if args and str(args[1]).startswith(("4", "5")):
            sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path in ("/", "/index.html"):
                with open(os.path.join(HERE, "ladder.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif u.path == "/api/dates":
                self._send(200, json.dumps(L.list_dates(), ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            elif u.path == "/api/day":
                day = (parse_qs(u.query).get("date") or [""])[0]
                if not _DATE_RX.match(day):
                    self._send(400, b'{"error":"date=YYYY-MM-DD"}', "application/json")
                    return
                self._send(200, _day_json(day), "application/json; charset=utf-8")
            else:
                self._send(404, b"not found", "text/plain")
        except Exception as e:      # 화면이 원인을 보여줄 수 있게 메시지를 돌려준다
            traceback.print_exc()
            self._send(500, json.dumps({"error": repr(e)}, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="기동 후 브라우저를 연다")
    a = ap.parse_args()
    for s in ("stdout", "stderr"):
        try:
            getattr(sys, s).reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    # 피터 파서 준비는 첫 요청을 6초 막는다 — 기동 때 뒤에서 미리 데운다.
    threading.Thread(target=L._peter_parser, daemon=True).start()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    url = "http://127.0.0.1:%d/" % a.port
    print("맥점 × 옵션 사다리 — %s  (Ctrl+C 로 종료)" % url)
    if a.open:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
