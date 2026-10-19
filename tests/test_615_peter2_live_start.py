# -*- coding: utf-8 -*-
"""[MW0602 615차] 피터2 실거래 개시일 관문 — 사용자 결정 2026-10-09.

10/12 부터 live(모의 주문), 그 이전은 백필 DB(가상). 날짜 하나가 두 경계를 쥔다:
  · 주문 시작      — store.effective_mode(): live 라도 date < PETER2_LIVE_START 면 shadow
  · 백필 끝(배타)  — PETER2_BACKFILL_UNTIL = PETER2_LIVE_START
둘이 갈라지면 하루가 이중계상되거나(백필+실거래) 빠진다(어느 쪽에도 없음).
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strategy.peter2.store import effective_mode   # noqa: E402


def test_live_before_start_is_shadow():
    assert effective_mode('live', '2026-10-09', '2026-10-12') == 'shadow'
    assert effective_mode('live', '2026-10-11', '2026-10-12') == 'shadow'


def test_live_on_and_after_start_is_live():
    assert effective_mode('live', '2026-10-12', '2026-10-12') == 'live'
    assert effective_mode('LIVE', '2026-10-13', '2026-10-12') == 'live'


def test_off_and_shadow_untouched_by_gate():
    for m in ('off', 'shadow'):
        assert effective_mode(m, '2026-10-09', '2026-10-12') == m
        assert effective_mode(m, '2026-10-20', '2026-10-12') == m
    assert effective_mode(None, '2026-10-20', '2026-10-12') == 'off'


def test_no_start_means_no_gate():
    assert effective_mode('live', '2026-10-09', None) == 'live'
    assert effective_mode('live', '2026-10-09', '') == 'live'


def test_settings_single_boundary():
    import config.settings as s
    # [2026-10-20 MW0602] 실시간 수집 정지로 live → off. 두 값은 한 쌍이다 — test_700 이 고정한다.
    assert s.PETER2_FOLLOW_MODE in ('live', 'off')
    if s.PETER2_COLLECT_MODE == 'eod':
        assert s.PETER2_FOLLOW_MODE == 'off'
    assert s.PETER2_LIVE_START == '2026-10-12'
    assert s.PETER2_BACKFILL_UNTIL == s.PETER2_LIVE_START, \
        '백필 끝과 실거래 시작이 갈렸다 — 그 사이 날짜가 이중계상되거나 빠진다'


def _src(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def test_engine_and_panel_share_effective_mode():
    """엔진 폴링과 패널 배너가 같은 함수로 실효 모드를 읽는다(배너가 live 라 하는데 주문이 안 나가는 일 방지)."""
    m = _src('main.py')
    body = m[m.index('    def _peter2_tick_body(self)'):m.index('    def _peter2_update_button')]
    assert 'peter2_store.effective_mode(' in body and 'PETER2_LIVE_START' in body
    d = _src('dashboard/main_dashboard.py')
    pm = d[d.index('    def _peter2_mode()'):]
    pm = pm[:pm.index('\n    def ')]
    assert 'effective_mode(' in pm and 'PETER2_LIVE_START' in pm


def test_collector_reload_is_rate_limit_safe():
    """[4b94f9f 이식] 45초 고정 · 오류 백오프 120초 · 백오프 중 재연장 금지."""
    js = _src('tools/peter2_live/extension/background.js')
    assert 'const RELOAD_SEC = 45;' in js and 'const BACKOFF_SEC = 120;' in js
    assert 'RELOAD_SEC_FAST' not in js and 'BACKOFF_MIN' not in js
    err = js[js.index('msg.meta.error'):]
    assert err.index('if (Date.now() >= backoffUntil)') < err.index('backoffUntil: Date.now() + BACKOFF_SEC')
