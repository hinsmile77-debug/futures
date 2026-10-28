# -*- coding: utf-8 -*-
"""727차 후속(장후 자동조치 G-10) — 피터2 확장 판(ext_ver)을 수신기 로그에 남긴다.

10-28 장후 점검 V-1028-9: 확장 1.2.0(탭 중복 거두기)이 Chrome 에 실제로 재로드됐는지
로그로 알 길이 없어 「미측정」으로만 이월했다. 이제 확장이 하트비트에 판을 실어 보내고,
수신기가 판이 바뀔 때만 `EXT ver=…` 한 줄을 남긴다. 판을 안 보내는 구판은 `미보고` 로 적는다
(계측 4원칙 ② — 미측정을 다른 값으로 위장하지 않는다).

동작 무변경 불변식: 수집·탭 관리·백오프 경로는 건드리지 않는다 — 판은 meta 에 덧붙는 키 하나다.
"""
import io
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXT = os.path.join(_ROOT, 'tools', 'peter2_live', 'extension')
sys.path.insert(0, os.path.join(_ROOT, 'tests'))

import test_725_peter2_restored_pinned_tab as T725   # noqa: E402  (하네스 재사용)


def _manifest_ver():
    with io.open(os.path.join(_EXT, 'manifest.json'), encoding='utf-8') as f:
        return json.load(f)['version']


def _rcv():
    for p in (os.path.join(_ROOT, 'tools', 'peter2_live'), os.path.join(_ROOT, 'tools'), _ROOT):
        if p not in sys.path:
            sys.path.insert(0, p)
    import receiver
    return receiver


class TestExtVerStructure(unittest.TestCase):

    def test_1_manifest_bumped_past_120(self):
        """판을 보내는 첫 판은 1.2.1 — 1.2.0 과 같은 번호면 로그만 보고 재로드 여부를 못 가른다."""
        self.assertNotEqual('1.2.0', _manifest_ver())

    def test_2_background_sends_manifest_version(self):
        with io.open(os.path.join(_EXT, 'background.js'), encoding='utf-8') as f:
            bg = f.read()
        self.assertIn('ext_ver: chrome.runtime.getManifest().version', bg)

    def test_3_heartbeat_records_none_when_absent(self):
        with io.open(os.path.join(_ROOT, 'tools', 'peter2_live', 'receiver.py'), encoding='utf-8') as f:
            rc = f.read()
        self.assertIn("'ext_ver': meta.get('ext_ver') or None", rc)
        self.assertIn("_log_ext_ver(meta.get('ext_ver'))", rc)


class TestExtVerLog(unittest.TestCase):

    def run_log(self, seq):
        rcv = _rcv()
        got = []
        orig = rcv._log
        rcv._log = got.append
        try:
            rcv._stat.pop('_ext_ver_key', None)
            for v in seq:
                rcv._log_ext_ver(v)
        finally:
            rcv._log = orig
        return got

    def test_4_logs_once_per_change(self):
        got = self.run_log(['1.2.1', '1.2.1', '1.2.1'])
        self.assertEqual(['EXT ver=1.2.1'], got)

    def test_5_old_extension_is_unreported_not_blank(self):
        """구판(판 미전송)은 첫 게시에 `미보고` 한 줄 — 아무것도 안 적으면 「아직 안 붙었다」와 구분이 안 된다."""
        got = self.run_log([None, None, '', '1.2.1'])
        self.assertEqual(2, len(got), got)
        self.assertIn('미보고', got[0])
        self.assertEqual('EXT ver=1.2.1', got[1])


@T725.unittest.skipUnless(T725._node(), 'node 없음 — 동작 테스트 건너뜀')
class TestExtVerBehavior(unittest.TestCase):

    def test_6_heartbeat_carries_ext_ver_and_keeps_tabs(self):
        runner = T725.TestPeter2RestoredTabBehavior('test_8_tab_census_rides_heartbeat')
        r = runner.run_scen({'now': T725._T_SESSION, 'storage': {'tabId': 5}, 'ext_ver': '9.9.9',
                             'tabs': [{'id': 5, 'url': T725._search(T725._SINCE_1028), 'pinned': True}],
                             'steps': [{'op': 'msg'}]})
        meta = r['posted']['meta']
        self.assertEqual('9.9.9', meta['ext_ver'])
        self.assertEqual({'x': 1, 'x_pinned': 1, 'peter_pinned': 1}, meta['tabs'])
        self.assertEqual('x', meta['url'], '원래 meta 키가 덮였다')


if __name__ == '__main__':
    unittest.main()
