# -*- coding: utf-8 -*-
"""[MW0601 697차 후속2 / 10-19 장후 G-1] 점검 지침서의 「거래주체 먼저 확인」 문단이
가리키는 코드·파일 이름이 실제로 존재하는지 고정한다.

문서만 바뀐 항목이지만, 문서가 인용하는 이름(`trade_principal.json`·`_ts_vbook_open`·
`[Virtual] … 가상진입`)이 코드에서 바뀌면 다음 장후 점검이 또 엉뚱한 곳을 찾는다.
그때 이 테스트가 깨져 지침서 갱신을 강제한다.
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, '.claude', 'skills', 'mireuk-daily-check', 'references')


def _read(*parts):
    with io.open(os.path.join(ROOT, *parts), encoding='utf-8') as f:
        return f.read()


def test_postmortem_has_principal_guard():
    t = _read('.claude', 'skills', 'mireuk-daily-check', 'references', 'postmortem.md')
    assert 'data/trade_principal.json' in t
    assert '분모에서 뺀다' in t


def test_evidence_map_points_to_postmortem():
    t = _read('.claude', 'skills', 'mireuk-daily-check', 'references', 'evidence_map.md')
    assert 'data/trade_principal.json' in t
    assert 'postmortem.md' in t


def test_cited_code_names_exist():
    tp = _read('strategy', 'runtime', 'trade_principal.py')
    assert "'trade_principal.json'" in tp
    assert "'MIREUK', 'SHINDONG', 'PETER'" in tp
    assert "'measured': False" in tp
    main = _read('main.py')
    assert 'def _ts_vbook_open(' in main
    assert '가상진입' in main
