# -*- coding: utf-8 -*-
"""725차 후속 — 피터2 수집기: Chrome 이 복원한 어제 고정 탭 때문에 X 고정 탭이 둘이 된 사고.

2026-10-28 실측(Chrome History · 세션 파일):
  10-27 19:21  장 마감 뒤 수집 탭에서 트윗 클릭 → `/PeterLeejoa/status/2114962787437047871` 로 이동.
               확장은 장중(08:30–15:45)에만 되돌리므로 그대로 밤새 종료.
  10-28 08:44:17  Chrome 첫 기동(사다리 작업 webbrowser.open) → 고정 탭은 설정과 무관하게 복원된다.
  10-28 08:45:37  확장이 그 탭을 못 알아보고(id 는 재시작으로 바뀜 · URL 조회는 search* 만)
                  새 고정 탭을 만듦 → **X 고정 탭 2개**(09:41 사람이 닫을 때까지).

대책 A(거두기) · B(클릭 넘겨주기) · C(탭 계수)를 **실제로 실행해** 확인한다 — Node 가 있으면
background.js 를 가짜 chrome API 위에서 돌린다(없으면 동작 테스트는 건너뛰고 구조 검사만 한다).
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXT = os.path.join(_ROOT, 'tools', 'peter2_live', 'extension')
_BG = os.path.join(_EXT, 'background.js')

# 2026-10-28(수) 10:00 KST — 장중
_T_SESSION = 1793149200000
# 2026-10-27(화) 19:21 KST — 장 밖
_T_EVENING = 1793096460000

_HARNESS = r"""
const fs = require('fs'), vm = require('vm');
const [bgPath, scenPath] = process.argv.slice(2);
const scen = JSON.parse(fs.readFileSync(scenPath, 'utf8'));
let nextId = 100;
const tabs = scen.tabs.map((t) => Object.assign({ status: 'complete', index: 0 }, t));
const store = Object.assign({}, scen.storage || {});
const calls = [];
const L = { alarm: [], updated: [], msg: [] };
function match(t, q) {
  if (q.pinned !== undefined && !!t.pinned !== q.pinned) return false;
  if (q.url) { const p = q.url.replace(/\*$/, ''); if ((t.url || '').indexOf(p) !== 0) return false; }
  return true;
}
const chrome = {
  storage: { local: {
    get: async (k) => (typeof k === 'string' ? { [k]: store[k] } : Object.assign({}, store)),
    set: async (o) => { Object.assign(store, o); } } },
  tabs: {
    get: async (id) => { const t = tabs.find((x) => x.id === id); if (!t) throw new Error('no tab'); return t; },
    query: async (q) => tabs.filter((t) => match(t, q || {})),
    create: async (o) => { const t = Object.assign({ id: nextId++, status: 'loading', index: tabs.length }, o);
                           tabs.push(t); calls.push(['create', o]); return t; },
    update: async (id, o) => { const t = tabs.find((x) => x.id === id); if (!t) throw new Error('no tab');
                               Object.assign(t, o); calls.push(['update', id, o]); return t; },
    remove: async (id) => { const i = tabs.findIndex((x) => x.id === id); if (i >= 0) tabs.splice(i, 1);
                            calls.push(['remove', id]); },
    reload: async (id) => { calls.push(['reload', id]); },
    onUpdated: { addListener: (f) => L.updated.push(f) } },
  alarms: { create: () => {}, onAlarm: { addListener: (f) => L.alarm.push(f) } },
  runtime: { onInstalled: { addListener: () => {} }, onStartup: { addListener: () => {} },
             onMessage: { addListener: (f) => L.msg.push(f) },
             getManifest: () => ({ version: scen.ext_ver || '0.0.0-test' }) },
};
let now = scen.now;
const RealDate = Date;
class FakeDate extends RealDate { constructor(...a) { if (a.length) super(...a); else super(now); }
                                   static now() { return now; } }
let posted = null;
const ctx = { chrome, Date: FakeDate, console,
              fetch: async (u, o) => { posted = JSON.parse(o.body); return { ok: true, status: 200 }; } };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(bgPath, 'utf8'), ctx);
const settle = () => new Promise((r) => setTimeout(r, 20));
(async () => {
  for (const st of scen.steps) {
    if (st.at) now = st.at;
    if (st.op === 'alarm') for (const f of L.alarm) f({ name: 'peter2' });
    if (st.op === 'nav') {
      const t = tabs.find((x) => x.id === st.id); t.url = st.url;
      for (const f of L.updated) f(st.id, { url: st.url }, t);
    }
    if (st.op === 'msg') for (const f of L.msg) f({ type: 'peter2_tweets', tweets: [], meta: { url: 'x' } },
                                                  { tab: null }, () => {});
    await settle();
  }
  process.stdout.write(JSON.stringify({ tabs, store, calls, posted }));
})();
"""


def _node():
    return shutil.which('node') or shutil.which('node.exe')


def _search(since):
    return ('https://x.com/search?q=from%%3APeterLeejoa%%20since_time%%3A%d%%20until_time%%3A%d'
            '&src=typed_query&f=live' % (since, since + 26100))


_SINCE_1028 = 1793143800       # 2026-10-28 08:30 KST
_SINCE_1027 = 1793057400
_STATUS = 'https://x.com/PeterLeejoa/status/2114962787437047871'
_LADDER = 'http://127.0.0.1:8765/'


@unittest.skipUnless(_node(), 'node 없음 — 동작 테스트 건너뜀(구조 검사는 아래 클래스)')
class TestPeter2RestoredTabBehavior(unittest.TestCase):

    def run_scen(self, scen):
        d = tempfile.mkdtemp()
        try:
            h, s = os.path.join(d, 'h.js'), os.path.join(d, 's.json')
            with io.open(h, 'w', encoding='utf-8') as f:
                f.write(_HARNESS)
            with io.open(s, 'w', encoding='utf-8') as f:
                json.dump(scen, f)
            out = subprocess.check_output([_node(), h, _BG, s], timeout=30)
            return json.loads(out.decode('utf-8'))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    @staticmethod
    def pinned_x(r):
        return [t for t in r['tabs'] if t.get('pinned') and (t.get('url') or '').startswith('https://x.com/')]

    def test_1_restored_status_tab_is_adopted_not_duplicated(self):
        """10-28 08:44 재현 — 복원된 `/status/` 고정 탭 + 낡은 tabId. 새 고정 탭을 만들면 안 된다."""
        r = self.run_scen({'now': _T_SESSION, 'storage': {'tabId': 999},
                           'tabs': [{'id': 4, 'url': _LADDER}, {'id': 5, 'url': _STATUS, 'pinned': True}],
                           'steps': [{'op': 'alarm'}, {'op': 'alarm'}]})
        self.assertFalse([c for c in r['calls'] if c[0] == 'create'], '새 탭을 만들었다: %r' % r['calls'])
        px = self.pinned_x(r)
        self.assertEqual(1, len(px), 'X 고정 탭이 %d개' % len(px))
        self.assertEqual(5, r['store']['tabId'], '복원 탭을 거두지 않았다')
        self.assertIn('since_time%%3A%d' % _SINCE_1028, px[0]['url'], '오늘 검색으로 되돌리지 않았다')

    def test_2_restored_yesterday_search_is_reused(self):
        """어제 검색 URL 로 복원된 고정 탭 — 닫고 새로 만들지 말고(헛 교체) 그 탭을 되돌린다."""
        r = self.run_scen({'now': _T_SESSION, 'storage': {'tabId': 999},
                           'tabs': [{'id': 7, 'url': _search(_SINCE_1027), 'pinned': True}],
                           'steps': [{'op': 'alarm'}]})
        self.assertFalse([c for c in r['calls'] if c[0] in ('create', 'remove')], r['calls'])
        self.assertEqual(7, r['store']['tabId'])

    def test_3_two_restored_pinned_peter_tabs_reaped_to_one(self):
        r = self.run_scen({'now': _T_SESSION, 'storage': {},
                           'tabs': [{'id': 5, 'url': _STATUS, 'pinned': True},
                                    {'id': 6, 'url': 'https://x.com/PeterLeejoa', 'pinned': True}],
                           'steps': [{'op': 'alarm'}]})
        self.assertEqual(1, len(self.pinned_x(r)), r['tabs'])

    def test_4_human_pinned_non_peter_tab_untouched(self):
        """사람이 고정한 X 홈 탭은 거두지도 닫지도 않는다 — 우리 탭은 따로 만든다."""
        r = self.run_scen({'now': _T_SESSION, 'storage': {},
                           'tabs': [{'id': 8, 'url': 'https://x.com/home', 'pinned': True}],
                           'steps': [{'op': 'alarm'}]})
        t8 = [t for t in r['tabs'] if t['id'] == 8]
        self.assertTrue(t8 and t8[0]['url'] == 'https://x.com/home', '사람 탭을 건드렸다')
        self.assertEqual(1, len([c for c in r['calls'] if c[0] == 'create' and c[1].get('pinned')]))

    def test_5_evening_click_is_handed_off_and_tab_returns(self):
        """10-27 19:21 재현 — 장 밖 클릭. 누른 트윗은 일반 탭으로, 수집 탭은 검색으로 돌아와야 한다."""
        r = self.run_scen({'now': _T_EVENING, 'storage': {'tabId': 5},
                           'tabs': [{'id': 5, 'url': _search(_SINCE_1027), 'pinned': True, 'index': 0}],
                           'steps': [{'op': 'nav', 'id': 5, 'url': _STATUS}]})
        cr = [c for c in r['calls'] if c[0] == 'create']
        self.assertEqual(1, len(cr), r['calls'])
        self.assertEqual(_STATUS, cr[0][1]['url'])
        self.assertIs(False, cr[0][1]['pinned'], '넘겨준 탭이 고정이면 내일 또 복원된다')
        t5 = [t for t in r['tabs'] if t['id'] == 5][0]
        self.assertIn('/search?', t5['url'], '수집 탭이 상세 화면에 남았다 — 내일 복원 중복의 씨앗')

    def test_6_home_drift_no_new_tab_and_throttled(self):
        """X SPA 의 `/home` 밀림은 새 탭 금지(10-08 증식) · 되돌리기는 30초에 한 번."""
        r = self.run_scen({'now': _T_SESSION, 'storage': {'tabId': 5},
                           'tabs': [{'id': 5, 'url': _search(_SINCE_1028), 'pinned': True}],
                           'steps': [{'op': 'nav', 'id': 5, 'url': 'https://x.com/home'},
                                     {'op': 'nav', 'id': 5, 'url': 'https://x.com/home', 'at': _T_SESSION + 5000}]})
        self.assertFalse([c for c in r['calls'] if c[0] == 'create'], r['calls'])
        self.assertEqual(1, len([c for c in r['calls'] if c[0] == 'update']), r['calls'])

    def test_7_unpinned_tab_is_released(self):
        """사람이 고정을 풀면 그 탭은 사람 것 — 클릭을 가로채지 않는다."""
        r = self.run_scen({'now': _T_SESSION, 'storage': {'tabId': 5},
                           'tabs': [{'id': 5, 'url': _search(_SINCE_1028), 'pinned': False}],
                           'steps': [{'op': 'nav', 'id': 5, 'url': _STATUS}]})
        self.assertFalse(r['calls'], r['calls'])

    def test_8_tab_census_rides_heartbeat(self):
        r = self.run_scen({'now': _T_SESSION, 'storage': {'tabId': 5},
                           'tabs': [{'id': 5, 'url': _search(_SINCE_1028), 'pinned': True},
                                    {'id': 6, 'url': _STATUS, 'pinned': True},
                                    {'id': 9, 'url': 'https://x.com/home'}],
                           'steps': [{'op': 'msg'}]})
        self.assertEqual({'x': 3, 'x_pinned': 2, 'peter_pinned': 2}, r['posted']['meta']['tabs'])


class TestPeter2RestoredTabStructure(unittest.TestCase):

    def setUp(self):
        with io.open(_BG, encoding='utf-8') as f:
            self.bg = f.read()
        with io.open(os.path.join(_ROOT, 'tools', 'peter2_live', 'receiver.py'), encoding='utf-8') as f:
            self.rc = f.read()

    def test_9_adopt_before_reap(self):
        """거두기가 정리보다 먼저 — 순서가 뒤집히면 복원된 어제 검색 탭을 닫고 새로 만든다."""
        m = re.search(r'async function ensureTab\(\)\s*\{(.+?)\n\}', self.bg, re.S)
        self.assertIsNotNone(m)
        body = m.group(1)
        self.assertLess(body.index('ourTab()'), body.index('reapStrays()'))

    def test_10_receiver_records_tabs_none_when_absent(self):
        self.assertIn("'tabs': meta.get('tabs') if isinstance(meta.get('tabs'), dict) else None", self.rc)
        self.assertIn('def _log_tabs(', self.rc)

    def test_11_receiver_logs_tabs_once_per_change(self):
        import sys
        sys.path.insert(0, os.path.join(_ROOT, 'tools', 'peter2_live'))
        sys.path.insert(0, os.path.join(_ROOT, 'tools'))
        import receiver as rcv
        got = []
        orig = rcv._log
        rcv._log = got.append
        try:
            rcv._stat.pop('tabs_key', None)
            rcv._log_tabs({'x': 2, 'x_pinned': 2, 'peter_pinned': 2})
            rcv._log_tabs({'x': 2, 'x_pinned': 2, 'peter_pinned': 2})
            rcv._log_tabs(None)
            rcv._log_tabs({'x': 1, 'x_pinned': 1, 'peter_pinned': 1})
        finally:
            rcv._log = orig
        self.assertEqual(2, len(got), got)
        self.assertIn('중복', got[0])
        self.assertNotIn('중복', got[1])


if __name__ == '__main__':
    unittest.main()
