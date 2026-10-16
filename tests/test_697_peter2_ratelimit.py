# -*- coding: utf-8 -*-
"""697차 — 피터2 수집기 X 검색 한도 소진(PAGE_ERROR 군집) 회귀 가드.

2026-10-12–10-16 수신기 로그에서 PAGE_ERROR 가 14–17분 주기로 4–8분씩 군집했다
(10-16 세션 분의 41%). 45초 새로고침 + 「새 게시물」 알약 자동 클릭 + X 자체 폴링이
같은 계정의 SearchTimeline 예산(15분 창)을 매 창 소진한 것으로 보았다.
그날 12:52 진입 지시가 13분 늦게 도착해 stale 로 기각됐다.

조치(F-1·F-2·F-3)
  F-1  ratelimit_hook.js(MAIN world)가 x-rate-limit-* 헤더를 재서 하트비트 meta.rl 로 싣는다
       → 수신기가 `RATE …` 로그와 collector.json `rl` 로 남긴다(추정 대신 실측).
  F-2  RELOAD_SEC 45 → 80 · 알약 자동 클릭 제거.
  F-3  오류 시 한도 헤더가 소진을 말하면 120초 고정 대신 reset 시각까지 물러난다.

611 과 같이 JS 를 실행하지 않고 소스 구조를 확인한다. 수신기는 실제로 돌려 본다.
문서: docs/피터2수집/
"""
import glob
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXT = os.path.join(_ROOT, 'tools', 'peter2_live', 'extension')


def _read(*parts):
    with io.open(os.path.join(*parts), encoding='utf-8') as f:
        return f.read()


class TestPeter2RateLimitSource(unittest.TestCase):

    def setUp(self):
        self.bg = _read(_EXT, 'background.js')
        self.ct = _read(_EXT, 'content.js')
        self.hk = _read(_EXT, 'ratelimit_hook.js')
        self.mf = json.loads(_read(_EXT, 'manifest.json'))

    # ── F-2 ────────────────────────────────────────────────────
    def test_1_reload_interval_within_budget(self):
        """45초는 창당 약 20회로 예산(실측 추정 ≈12회)을 넘었다. 75초 미만으로 돌아가면 안 된다."""
        m = re.search(r'const RELOAD_SEC = (\d+);', self.bg)
        self.assertIsNotNone(m, 'RELOAD_SEC 를 찾지 못했다')
        self.assertGreaterEqual(int(m.group(1)), 75,
                                'RELOAD_SEC 가 다시 짧아졌다 — 한도 소진 군집이 돌아온다')

    def test_2_pill_is_not_clicked(self):
        """알약 클릭은 새로고침과 겹쳐 예산만 먹는다."""
        self.assertNotIn('pillLabel', self.ct, '「새 게시물」 알약 자동 클릭이 돌아왔다')
        self.assertNotIn('.click()', self.ct, 'content.js 가 페이지 요소를 클릭한다 — 읽기 전용이어야 한다')

    # ── F-1 ────────────────────────────────────────────────────
    def test_3_hook_runs_in_main_world_before_page(self):
        """응답 헤더는 페이지 world 의 fetch/XHR 에서만 보인다 — 페이지 스크립트보다 먼저 붙어야 한다."""
        hooks = [c for c in self.mf['content_scripts'] if 'ratelimit_hook.js' in c.get('js', [])]
        self.assertEqual(1, len(hooks), 'manifest 에 ratelimit_hook.js 등록이 없다')
        self.assertEqual('MAIN', hooks[0].get('world'), '훅이 격리 world 에서 돈다 — 페이지 요청을 못 본다')
        self.assertEqual('document_start', hooks[0].get('run_at'), '훅이 늦게 붙어 첫 요청을 놓친다')

    def test_4_hook_reads_headers_and_both_transports(self):
        for h in ('x-rate-limit-limit', 'x-rate-limit-remaining', 'x-rate-limit-reset'):
            self.assertIn(h, self.hk, '%s 헤더를 읽지 않는다' % h)
        self.assertIn('window.fetch =', self.hk, 'fetch 를 감싸지 않는다')
        self.assertIn('XMLHttpRequest.prototype.send', self.hk, 'XHR 을 감싸지 않는다')
        self.assertIn('SearchTimeline', self.hk, '검색 타임라인을 대상으로 하지 않는다')

    def test_5_hook_is_read_only(self):
        """훅은 원래 응답을 그대로 돌려줘야 한다 — 요청을 막거나 바꾸면 안 된다."""
        self.assertIn('return p;', self.hk, 'fetch 래퍼가 원래 promise 를 돌려주지 않는다')
        self.assertIn('return XS.apply(this, arguments);', self.hk, 'XHR send 를 원래대로 부르지 않는다')
        self.assertNotIn('.abort(', self.hk, '훅이 요청을 중단한다')

    def test_6_early_response_is_not_lost(self):
        """content.js(document_idle)보다 먼저 온 응답은 DOM 속성으로 넘어와야 한다."""
        self.assertIn('data-peter2-rl', self.hk, '훅이 DOM 에 마지막 값을 남기지 않는다')
        self.assertIn('data-peter2-rl', self.ct, 'content.js 가 붙기 전 관측을 읽지 않는다')

    def test_7_rl_rides_heartbeat_and_null_means_unmeasured(self):
        self.assertIn('rl: rl', self.ct, '하트비트 meta 에 rl 이 실리지 않는다')
        self.assertIn('let rl = null', self.ct, 'rl 기본값이 null 이 아니다 — 미측정이 0 으로 위장된다')

    # ── F-3 ────────────────────────────────────────────────────
    def test_8_backoff_follows_reset_when_spent(self):
        m = re.search(r'function backoffMsFor\(meta, now\)\s*\{(.+?)\n\}', self.bg, re.S)
        self.assertIsNotNone(m, 'backoffMsFor 가 없다')
        body = m.group(1)
        self.assertIn('rl.reset', body, 'reset 시각을 쓰지 않는다')
        self.assertIn('429', body, '429 를 소진으로 보지 않는다')
        self.assertIn('BACKOFF_MAX_SEC', body, '대기 상한이 없다 — 이상한 reset 값에 하루를 날린다')
        self.assertIn('BACKOFF_SEC * 1000', body, '헤더가 없을 때 종전 120초로 돌아가지 않는다')
        self.assertIn('backoffMsFor(msg.meta', self.bg, '오류 분기가 backoffMsFor 를 쓰지 않는다')


class TestPeter2RateLimitReceiver(unittest.TestCase):

    def setUp(self):
        for p in (os.path.join(_ROOT, 'tools', 'peter2_live'), os.path.join(_ROOT, 'tools'), _ROOT):
            if p not in sys.path:
                sys.path.insert(0, p)
        import receiver
        import peter_capture
        self.r, self.pc = receiver, peter_capture
        self.tmp = tempfile.mkdtemp()
        self._saved = (receiver.LOG_DIR, receiver.LIVE_DIR, peter_capture.RAW_DIR, dict(receiver._stat))
        receiver.LOG_DIR = self.tmp
        receiver.LIVE_DIR = os.path.join(self.tmp, 'live')
        peter_capture.RAW_DIR = os.path.join(self.tmp, 'raw')
        receiver._stat.pop('rl_key', None)

    def tearDown(self):
        self.r.LOG_DIR, self.r.LIVE_DIR, self.pc.RAW_DIR, st = self._saved
        self.r._stat.clear()
        self.r._stat.update(st)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _log(self):
        return io.open(glob.glob(os.path.join(self.tmp, 'peter2_receiver_*.log'))[0], encoding='utf-8').read()

    def _hb(self):
        return json.load(io.open(glob.glob(os.path.join(self.tmp, 'live', '*', 'collector.json'))[0],
                                 encoding='utf-8'))

    def test_9_rate_line_once_per_observation(self):
        rl = {'op': 'SearchTimeline', 'status': 200, 'lim': 50, 'rem': 7, 'reset': 1792130000,
              'phase': 'load', 'at': 1, 'n_page': 1}
        self.r.ingest({'tweets': [], 'meta': {'rl': rl}})
        self.r.ingest({'tweets': [], 'meta': {'rl': rl}})       # 같은 관측 — 다시 적지 않는다
        self.r.ingest({'tweets': [], 'meta': {'rl': dict(rl, rem=0, status=429, at=2, n_page=2)}})
        lines = [l for l in self._log().splitlines() if ' RATE ' in l]
        self.assertEqual(2, len(lines), lines)
        self.assertIn('st=200 rem=7/50', lines[0])
        self.assertIn('st=429 rem=0/50', lines[1])
        self.assertEqual(0, self._hb()['rl']['rem'])

    def test_10_missing_rl_is_none_not_zero(self):
        self.r.ingest({'tweets': [], 'meta': {}})
        self.assertIsNone(self._hb()['rl'], '한도 미측정이 None 이 아니다(계측 4원칙 ②)')
        self.assertNotIn(' RATE ', self._log())

    def test_11_page_error_is_one_line(self):
        self.r.ingest({'tweets': [], 'meta': {'error': 'Top\nLatest\nSomething went wrong.'}})
        log = self._log()
        self.assertIn('PAGE_ERROR Top Latest Something went wrong.', log)
        # 줄마다 시각으로 시작해야 한다 — 오류 문구의 줄바꿈이 새 줄을 만들면 `Latest` 같은 잔해가 남는다
        for l in log.splitlines():
            self.assertTrue(re.match(r'\d\d:\d\d:\d\d ', l), '시각 없는 잔해 줄: %r' % l)


class TestLatencyReportRate(unittest.TestCase):
    """latency_report.py(615차)가 RATE 줄을 창별로 묶고, 없으면 「미측정」이라 말한다."""

    def setUp(self):
        if _ROOT not in sys.path:
            sys.path.insert(0, _ROOT)
        from tools.peter2_live import latency_report as LR
        self.LR = LR
        self.tmp = tempfile.mkdtemp()
        self._root = LR.ROOT
        LR.ROOT = self.tmp
        os.makedirs(os.path.join(self.tmp, 'logs'))

    def tearDown(self):
        self.LR.ROOT = self._root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, lines):
        with io.open(os.path.join(self.tmp, 'logs', 'peter2_receiver_20261019.log'), 'w',
                     encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

    def test_12_windows_grouped_by_reset(self):
        self._write([
            '09:00:10 RATE SearchTimeline st=200 rem=49/50 reset=09:15:00 phase=load n=1',
            '09:00:50 RATE SearchTimeline st=200 rem=47/50 reset=09:15:00 phase=poll n=2',
            '09:15:20 RATE SearchTimeline st=429 rem=0/50 reset=09:30:00 phase=load n=1',
            '09:15:21 PAGE_ERROR Top Latest',
        ])
        r = self.LR.build('2026-10-19')
        w = r['rate']['windows']
        self.assertEqual(2, len(w))
        self.assertEqual((2, 1, 1, 49, 47), (w[0]['n'], w[0]['load'], w[0]['poll'], w[0]['rem_max'], w[0]['rem_min']))
        self.assertEqual(1, r['rate']['n429'])
        self.assertEqual(1, r['error_minutes'])
        self.assertIn('rem 최대→최소', self.LR.render(r))

    def test_13_no_rate_lines_is_unmeasured(self):
        self._write(['09:15:21 PAGE_ERROR Top'])
        r = self.LR.build('2026-10-19')
        self.assertIsNone(r['rate'])
        self.assertIn('미측정', self.LR.render(r))


if __name__ == '__main__':
    unittest.main()
