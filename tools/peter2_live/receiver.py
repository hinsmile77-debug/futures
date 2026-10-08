# -*- coding: utf-8 -*-
"""피터2 수신기 — Chrome 확장이 보낸 트윗을 `_raw/<날짜>.jsonl` 에 받아 적는다.

    Chrome(로그인된 X) ── 확장 content.js ── background.js ──POST──▶ 127.0.0.1:8766/peter
                                                                   │
                                     tools/peter_capture.append(src='live')   ← 기존 함수(멱등)
                                     data/peter2_live/<날짜>/collector.json    ← 하트비트

원칙
    ⛔ 127.0.0.1 에만 묶는다 — 밖에서 들어올 수 없다.
    ⛔ 해석하지 않는다. 주문하지 않는다. 미륵이 DB 를 열지 않는다(append-only 파일만).
    ⛔ 같은 id 를 두 번 쓰지 않는다(peter_capture 가 id 로 거른다).
    · 이미 떠 있으면(포트 사용 중) 조용히 끝난다 — start_mireuk.bat 재기동 루프에서 여러 번 불려도 하나만 산다.

실행(py37_32 · 표준 라이브러리만)
    python tools/peter2_live/receiver.py            # 상주
    python tools/peter2_live/receiver.py --check    # 떠 있는지 확인(GET /health)
"""
import datetime
import io
import json
import os
import sys
import threading

try:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
except ImportError:                       # pragma: no cover
    from http.server import BaseHTTPRequestHandler, HTTPServer as ThreadingHTTPServer

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_ROOT, os.path.join(_ROOT, 'tools')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import peter_capture as pc          # noqa: E402

PORT = 8766
try:
    from config.settings import PETER2_RECEIVER_PORT as PORT   # noqa
except Exception:
    pass

LIVE_DIR = os.path.join(_ROOT, 'data', 'peter2_live')
LOG_DIR = os.path.join(_ROOT, 'logs')
_lock = threading.Lock()
_stat = {'started': datetime.datetime.now().isoformat(timespec='seconds'),
         'posts': 0, 'new_total': 0, 'last_post': None}


def _log(msg):
    try:
        if not os.path.isdir(LOG_DIR):
            os.makedirs(LOG_DIR)
        p = os.path.join(LOG_DIR, 'peter2_receiver_%s.log' % datetime.date.today().strftime('%Y%m%d'))
        with io.open(p, 'a', encoding='utf-8') as f:
            f.write('%s %s\n' % (datetime.datetime.now().strftime('%H:%M:%S'), msg))
    except Exception:
        pass


def _kst_date(dt_iso):
    try:
        t = datetime.datetime.strptime((dt_iso or '')[:19], '%Y-%m-%dT%H:%M:%S')
        return (t + datetime.timedelta(hours=9)).date().isoformat()
    except Exception:
        return None


def _heartbeat(meta, n_new):
    today = datetime.date.today().isoformat()
    d = os.path.join(LIVE_DIR, today)
    if not os.path.isdir(d):
        os.makedirs(d)
    info = {
        'last_post': datetime.datetime.now().isoformat(timespec='seconds'),
        'articles': meta.get('articles'),
        'error': meta.get('error'),
        'url': (meta.get('url') or '')[:200],
        'cycle': meta.get('cycle'),
        'posts': _stat['posts'],
        'new_total': _stat['new_total'],
        'new_last': n_new,
    }
    tmp = os.path.join(d, 'collector.json.tmp')
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False)
    os.replace(tmp, os.path.join(d, 'collector.json'))


def ingest(payload):
    tweets = payload.get('tweets') or []
    meta = payload.get('meta') or {}
    seen_at = datetime.datetime.now().replace(microsecond=0).isoformat() + '+09:00'
    by_date = {}
    for t in tweets:
        if not isinstance(t, dict) or not t.get('id'):
            continue
        d = _kst_date(t.get('dt'))
        if d:
            by_date.setdefault(d, []).append({'id': str(t['id']), 'dt': t.get('dt'),
                                              'text': t.get('text') or ''})
    n_new = 0
    with _lock:
        for d, tw in by_date.items():
            # 로그에는 실제로 새로 들어간 글을 적는다 — 종전 `tw[-n:]` 은 받은 묶음의 끝 n개라
            # 옛 글(예: 09:09 「1070 부근에서 반등」)이 NEW 로 반복 찍혔다(데이터 자체는 정상)
            have, _ = pc.load(d)
            fresh = [x for x in tw if x['id'] not in have]
            n, dup, total = pc.append(d, tw, src='live', seen_at=seen_at)
            n_new += n
            if n:
                _log('NEW %s +%d (누적 %d) %s' % (d, n, total,
                                                 ' | '.join((x['text'] or '(이미지)')[:30].replace('\n', ' ')
                                                            for x in fresh)))
        _stat['posts'] += 1
        _stat['new_total'] += n_new
        _stat['last_post'] = seen_at
        _heartbeat(meta, n_new)
    if meta.get('error'):
        _log('PAGE_ERROR %s' % meta.get('error'))
    return n_new


class H(BaseHTTPRequestHandler):
    def _cors(self):
        origin = self.headers.get('Origin') or ''
        if origin.startswith('chrome-extension://') or origin in ('https://x.com', 'https://twitter.com'):
            self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Private-Network', 'true')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith('/health'):
            return self._json(200, dict(_stat, ok=True, port=PORT))
        return self._json(404, {'ok': False})

    def do_POST(self):
        if not self.path.startswith('/peter'):
            return self._json(404, {'ok': False})
        try:
            n = int(self.headers.get('Content-Length') or 0)
            raw = self.rfile.read(n)
            try:
                txt = raw.decode('utf-8')
            except UnicodeDecodeError:
                txt = raw.decode('cp949', 'replace')     # 수동 시험(curl·콘솔) 대비
            payload = json.loads(txt or '{}')
            n_new = ingest(payload)
            return self._json(200, {'ok': True, 'new': n_new})
        except Exception as e:
            _log('ERROR %s' % e)
            return self._json(500, {'ok': False, 'error': str(e)})

    def log_message(self, *a):          # 표준 접근 로그는 끈다(2초마다 쌓인다)
        pass


class _Server(ThreadingHTTPServer):
    """🔴 Windows 에서 SO_REUSEADDR 는 **같은 포트 중복 바인딩을 허용**한다(2026-10-07 실측:
    두 번째 수신기가 「사용 중」으로 끝나지 않고 함께 떴다). 배타 바인딩으로 하나만 살린다."""
    allow_reuse_address = False
    daemon_threads = True

    def server_bind(self):
        import socket
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        ThreadingHTTPServer.server_bind(self)


def main():
    if '--check' in sys.argv:
        try:
            from urllib.request import urlopen
            print(urlopen('http://127.0.0.1:%d/health' % PORT, timeout=3).read().decode('utf-8'))
        except Exception as e:
            print('receiver not responding: %s' % e)
            sys.exit(1)
        return
    try:
        srv = _Server(('127.0.0.1', PORT), H)
    except OSError as e:
        # 콘솔이 cp949 일 수 있다 — 출력은 ASCII 로만(로그 파일은 UTF-8)
        print('[peter2-receiver] port %d in use - already running, exit (%s)' % (PORT, e.__class__.__name__))
        _log('SKIP already running: %s' % e)
        return
    _log('START port=%d pid=%d' % (PORT, os.getpid()))
    print('[peter2-receiver] listening 127.0.0.1:%d' % PORT)
    try:
        srv.serve_forever()
    finally:
        _log('STOP')


if __name__ == '__main__':
    main()
