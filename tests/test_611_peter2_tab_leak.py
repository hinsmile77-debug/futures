# -*- coding: utf-8 -*-
"""611차 후속3 — 피터2 수집기 확장의 탭 증식·출처 오염 회귀 가드.

2026-10-08 장중에 Chrome 탭이 계속 늘어났다. 원인은 두 겹이었고 둘 다 「조용히 그럴듯한
값」 계열이다(CLAUDE.md 계측 4원칙 머리말).

  ① background.js 가 자기 탭을 **URL 로** 찾았다. X 는 SPA 라 페이지를 새로 읽지 않고
     주소만 `/home` 으로 바꾸는 일이 있는데, 그러면 `tabs.query({url:".../search*"})` 에
     안 잡힌다 → 「탭이 없다」 → **새로 만든다**. 닫는 코드는 없었으므로 틱(15~30초)마다
     한 장씩 쌓였다.
  ② content.js 의 자격 검사가 **주입 시점 1회뿐**이라, 주소가 밀린 뒤에도 계속 살아서
     **홈 타임라인을 검색 결과인 양** 보냈다. 실측 하트비트 `url=https://x.com/home`.
     홈은 알고리즘 정렬이라 장중 전수 보장이 없다 — 표본이 조용히 비는 길이다.

이 테스트는 JS 를 실행하지 않는다(이 저장소에 JS 런타임이 없다). 대신 **고쳐 넣은 구조가
도로 빠지지 않는지**를 소스에서 확인한다. 함수 하나를 지우면 여기서 깨진다.
"""
import io
import os
import re
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXT = os.path.join(_ROOT, 'tools', 'peter2_live', 'extension')


def _read(*parts):
    with io.open(os.path.join(*parts), encoding='utf-8') as f:
        return f.read()


class TestPeter2TabLeak(unittest.TestCase):

    def setUp(self):
        self.bg = _read(_EXT, 'background.js')
        self.ct = _read(_EXT, 'content.js')
        self.rc = _read(_ROOT, 'tools', 'peter2_live', 'receiver.py')

    # ── ① 탭 증식 ────────────────────────────────────────────────
    def test_1_tab_is_tracked_by_id_not_url(self):
        """탭을 id 로 들고 있어야 한다 — URL 로만 찾으면 주소가 밀리는 순간 놓친다."""
        self.assertIn('chrome.tabs.get(', self.bg, 'tabs.get 으로 id 추적이 없다')
        self.assertTrue(re.search(r'storage\.local\.(get|set)\(\s*[{"\']?tabId', self.bg),
                        'tabId 를 storage 에 보존하지 않는다 — 워커가 재시작하면 잃는다')

    def test_2_drifted_tab_is_restored_not_duplicated(self):
        """주소가 밀리면 **되돌려야** 한다. 새로 만들면 거기서 증식이 시작된다."""
        self.assertIn('chrome.tabs.update(', self.bg, '복귀 경로(tabs.update)가 없다')
        self.assertEqual(1, self.bg.count('chrome.tabs.create('),
                         'tabs.create 호출이 1곳을 넘는다 — 증식 경로가 늘었다')
        # create 는 「탭이 아예 없을 때」만이어야 한다 — update 보다 뒤에 조건 없이 서면 안 된다
        self.assertLess(self.bg.index('chrome.tabs.create('), self.bg.index('chrome.tabs.update('),
                        'create 와 update 의 분기 순서가 뒤집혔다')

    def test_3_strays_are_reaped(self):
        """이미 생긴 여분 탭을 거두는 경로가 있어야 한다."""
        self.assertIn('chrome.tabs.remove(', self.bg, '여분 탭 수거(tabs.remove)가 없다')

    def test_4_reaper_spares_human_tabs(self):
        """사람이 직접 연 X 검색 탭을 닫으면 안 된다 — 소유 표식으로 가른다."""
        self.assertIn('isOurUrl', self.bg, '소유 판별 함수가 없다')
        m = re.search(r'async function reapStrays\(\)\s*\{(.+?)\n\}', self.bg, re.S)
        self.assertIsNotNone(m, 'reapStrays 를 찾지 못했다')
        self.assertIn('isOurUrl', m.group(1),
                      'reapStrays 가 소유를 확인하지 않고 닫는다 — 사람 탭을 닫을 수 있다')

    # ── ② 출처 오염 ──────────────────────────────────────────────
    def test_5_eligibility_is_rechecked_every_send(self):
        """자격 검사가 주입 시점 1회면 안 된다 — send 안에서 매번 물어야 한다."""
        self.assertIn('function offSearch(', self.ct, 'offSearch() 가 없다')
        m = re.search(r'function send\(force\)\s*\{(.+?)\n  \}', self.ct, re.S)
        self.assertIsNotNone(m, 'send() 를 찾지 못했다')
        self.assertIn('offSearch()', m.group(1),
                      'send() 가 자격을 다시 묻지 않는다 — 홈 타임라인을 검색 결과로 보낼 수 있다')

    def test_6_off_search_sends_no_tweets(self):
        """이탈 중에는 긁어 보내지 않는다 — 미측정을 수집으로 위장하지 않는다(계측 4원칙 ②)."""
        m = re.search(r'if \(offSearch\(\)\) \{(.+?)\n      return;', self.ct, re.S)
        self.assertIsNotNone(m, '이탈 분기를 찾지 못했다')
        self.assertIn('tweets: []', m.group(1), '이탈 중에도 트윗을 실어 보낸다')
        self.assertIn('off_search: true', m.group(1), '이탈 사실을 신고하지 않는다')

    def test_7_off_search_is_not_an_error(self):
        """이탈은 오류가 아니다 — 물러나면(backoff) 영영 안 돌아온다. 되돌려야 한다."""
        self.assertTrue(re.search(r'off_search\)\s*\{(?:.|\n)*?ensureTab\(\)', self.bg),
                        '이탈 신고를 받고도 복귀시키지 않는다')
        self.assertTrue(re.search(r'\}\s*else if \(msg\.meta && msg\.meta\.error\)', self.bg),
                        'off_search 가 error 분기로 흘러 15분 backoff 를 유발한다')

    def test_8_page_error_is_scoped_to_main_column(self):
        """오른쪽 트렌드 패널의 「다시 시도」가 본문 오류로 오인되면 안 된다(그날 PAGE_ERROR 다발)."""
        m = re.search(r'function pageError\(\)\s*\{(.+?)\n  \}', self.ct, re.S)
        self.assertIsNotNone(m, 'pageError() 를 찾지 못했다')
        self.assertIn('primaryColumn', m.group(1),
                      'pageError 가 본문 칸이 아니라 페이지 전체를 본다 — 오탐이 돌아온다')

    # ── ③ 가시화 ────────────────────────────────────────────────
    def test_9_receiver_records_off_search(self):
        """하트비트에 이탈 여부가 남아야 한다 — 「정상 수집」과 같은 모양이면 안 된다."""
        self.assertIn("'off_search'", self.rc, '수신기 하트비트에 off_search 가 없다')
        self.assertIn('OFF_SEARCH', self.rc, '이탈 전환이 로그에 남지 않는다')


if __name__ == '__main__':
    unittest.main()
