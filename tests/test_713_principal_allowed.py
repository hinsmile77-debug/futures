# -*- coding: utf-8 -*-
"""[MW0601 713차 / 신동 주체 전환 P2] 거래주체 허용 집합(PRINCIPAL_ALLOWED · PRINCIPAL_DEFAULT).

Sindong-V4 는 주체를 하나로 **고정**(PRINCIPAL_LOCK)했지만 이 브랜치는 피터를 **선택 가능**으로 남긴다
(사용자 결정 2026-10-25). 지키는 불변식:
  A1  기본값(None·None)이면 종전과 같다 — 3주체 전부 · 파일 없음 → 미륵.
  A2  허용 밖 파일 주체는 기본 주체로 읽히고 그 사실이 남는다(fallback · file_principal). 파일은 그대로.
  A3  허용 밖 주체로는 저장할 수 없다(ValueError). 이력 prev 는 파일 기준.
  A4  알 수 없는 이름은 버리고, 남는 것이 없으면 3주체 전부. 기본 주체가 허용 밖이면 허용 집합의 첫 주체.
  A5  main 의 전환 요청과 대시보드 버튼이 같은 출처(trade_principal.allowed)를 본다.
"""
import ast
import io
import json
import os

import pytest

import config.settings as S
from strategy.runtime import trade_principal as TP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture()
def tp(tmp_path, monkeypatch):
    monkeypatch.setattr(TP, 'STATE_PATH', str(tmp_path / 'trade_principal.json'))
    monkeypatch.setattr(TP, 'LOG_PATH', str(tmp_path / 'trade_principal_log.jsonl'))
    monkeypatch.setattr(S, 'PRINCIPAL_ALLOWED', None, raising=False)
    monkeypatch.setattr(S, 'PRINCIPAL_DEFAULT', None, raising=False)

    def write(p):
        with io.open(TP.STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump({'principal': p, 'set_at': '2026-10-21T09:05:30', 'reason': 'dashboard'}, f)
    return monkeypatch, write


def _cutover(mp):
    mp.setattr(S, 'PRINCIPAL_ALLOWED', ('SHINDONG', 'PETER'))
    mp.setattr(S, 'PRINCIPAL_DEFAULT', 'SHINDONG')


def test_A1_defaults_are_legacy(tp):
    assert S.PRINCIPAL_ALLOWED is None and S.PRINCIPAL_DEFAULT is None
    assert TP.allowed() == TP.PRINCIPALS
    st = TP.load()
    assert st['principal'] == 'MIREUK' and st['measured'] is False and st['fallback'] is True


def test_A1_settings_ship_legacy_values():
    """배포값이 종전 동작이다 — 11-02 전환 전까지 바뀌면 안 된다."""
    import importlib
    src = io.open(os.path.join(ROOT, 'config', 'settings.py'), encoding='utf-8').read()
    assert '\nMIREUK_ENGINE = "full"\n' in src.replace('\r\n', '\n')
    assert '\nPRINCIPAL_ALLOWED = None\n' in src.replace('\r\n', '\n')
    assert '\nPRINCIPAL_DEFAULT = None\n' in src.replace('\r\n', '\n')
    assert '\nLIGHT_PASS_DRY_RUN = False\n' in src.replace('\r\n', '\n')


def test_A1_file_choice_kept_by_default(tp):
    mp, write = tp
    write('SHINDONG')
    st = TP.load()
    assert st['principal'] == 'SHINDONG' and st['measured'] is True and st['fallback'] is False


def test_A2_not_allowed_file_falls_back(tp):
    mp, write = tp
    _cutover(mp)
    write('MIREUK')
    st = TP.load()
    assert st['principal'] == 'SHINDONG'
    assert st['fallback'] is True and st['file_principal'] == 'MIREUK' and st['measured'] is True
    assert st['reason'] == 'not_allowed:MIREUK'
    assert json.load(io.open(TP.STATE_PATH, encoding='utf-8'))['principal'] == 'MIREUK'   # 파일 무변경


def test_A2_allowed_file_choice_kept(tp):
    mp, write = tp
    _cutover(mp)
    write('PETER')
    st = TP.load()
    assert st['principal'] == 'PETER' and st['fallback'] is False


def test_A2_no_file_uses_default(tp):
    mp, _ = tp
    _cutover(mp)
    st = TP.load()
    assert st['principal'] == 'SHINDONG' and st['measured'] is False


def test_A3_save_rejects_not_allowed(tp):
    mp, write = tp
    _cutover(mp)
    write('SHINDONG')
    with pytest.raises(ValueError):
        TP.save('MIREUK', reason='dashboard')
    rec = TP.save('PETER', reason='dashboard')
    assert rec['principal'] == 'PETER' and TP.load()['principal'] == 'PETER'
    last = io.open(TP.LOG_PATH, encoding='utf-8').read().strip().splitlines()[-1]
    assert json.loads(last)['prev'] == 'SHINDONG'


def test_A4_unknown_names_and_bad_default(tp):
    mp, _ = tp
    assert TP.allowed(('SHINDONG', 'typo')) == ('SHINDONG',)
    assert TP.allowed(('typo',)) == TP.PRINCIPALS
    assert TP.allowed('PETER') == ('PETER',)
    assert TP.default_principal('MIREUK', ('SHINDONG', 'PETER')) == 'SHINDONG'
    assert TP.default_principal(None, ('SHINDONG', 'PETER')) == 'SHINDONG'
    assert TP.default_principal('PETER', ('SHINDONG', 'PETER')) == 'PETER'


def _method_src(name):
    src = io.open(os.path.join(ROOT, 'main.py'), encoding='utf-8').read()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'TradingSystem':
            ms = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            for i, n in enumerate(ms):
                if n.name == name:
                    end = ms[i + 1].lineno - 1 if i + 1 < len(ms) else None
                    return '\n'.join(src.splitlines()[n.lineno - 1:end])
    raise AssertionError(name)


def test_A5_change_request_checks_allowed_before_save():
    body = _method_src('_on_principal_change_requested')
    assert body.index('principal_mod.allowed()') < body.index('principal_mod.save(')


def test_A5_dashboard_disables_not_allowed():
    src = io.open(os.path.join(ROOT, 'dashboard', 'main_dashboard.py'), encoding='utf-8').read()
    assert 'set(_tp.PRINCIPALS) - set(_tp.allowed())' in src
    assert 'self._principal_disabled = set(self._principal_disabled) | self._principal_not_allowed' in src
