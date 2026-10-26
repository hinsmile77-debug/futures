# -*- coding: utf-8 -*-
"""트윗 한 건 → 피터의 **관점**(상자·맥점·편향·마감조건·대기·복기). **순수 함수**.

[MW0601 2026-10-27 · 피터의 방법] 매매 해석기(`parse.py`)와 **분리된 넓은 그물**이다.
  · `parse.py` 는 PETER 실거래의 주문 해석기라 좁아야 한다 — 여기는 **주문과 무관**하게
    신동2AI 의 입력·채점용으로 「그가 무엇을 봤는가」를 건진다. 이 모듈은 주문 경로에 쓰지 않는다.
  · 계기: 2026-10-26 「오늘은 870 850 싸움 … 870 아래서 풋만」이 `parse_tweet` 에서
    `ignore=None, facts=[]` 로 나와 `signals.jsonl` 에 흔적 없이 사라졌다(계측 4원칙 ③).
  · 근거 문서: `docs/미륵이고도화3/피터2/피터_870-850_장초판단근거_딥다이브_MW0601-20261026.md`

kind (우선순위 순 — 하나만 붙는다)
    recap       복기·자랑(「…했는데」「알려줬다」「= 17p」) — 채점 대상 아님, 레벨만 보존
    box         「870 850 싸움」「965 - 955 라인」 — 두 레벨 사이 공방
    bias        「870 아래서 풋만」「1105 밑에서 풋」「매수 단타만」 — 방향 편향(+선택 레벨)
    cond_close  「1095 이하 마감하면 …」「1050 위 안착후 마감」 — 마감 조건 시나리오
    wait        「1070 밑으로 떨어지면 매수 기회니 대기」 — 조건부 진입 대기
    pivot       「맥점은 1035」「1차 저항 1018」「1057 기준」 — 단일 기준선
    note        가격이 있는 그 밖의 말(「980 돌파함」「고점 1109.75」)
    none        가격 없음
"""
import re

_P = r'(?<![\d.])(\d{3,4}(?:\.\d{1,2})?)(?![\d])(?!\s*(?:페이지|쪽|배|분|시|일|명|만|억|%|원))'
_RECAP = re.compile(r'했는데|했지|알려줬|알려준|외친|외쳤|찍고|끝\.|=\s*\d|\d\s*[pP]\s*(손실|수익)|라고\s*했')
_BOX = re.compile(r'(?<![\d.])(\d{3,4})\s*(?:[-–~,]|\s)\s*(\d{3,4})(?![\d])\s*(?:부근\s*)?(싸움|라인|공방|박스|사이)')
_BIAS = re.compile(r'(풋|콜|숏|롱|매수|매도)\s*단타\s*만|(?<![가-힣])(풋|콜|숏|롱)\s*만')
_BIAS_LV = re.compile(r'(\d{3,4}(?:\.\d{1,2})?)\s*(아래|밑|위)\s*(?:에서|서)\s*(풋|콜|매도|매수|숏|롱)')
_CLOSE = re.compile(r'마감|끝나면|끝난다면|종가가')
_WAIT = re.compile(r'대기|기회')
_PIVOT = re.compile(r'맥점|기준|저항|지지|공방')
_OTHER = re.compile(r'코스닥|KOSDAQ|나스닥|NASDAQ|코스피\s*\d{4}\s*돌파')
_TOMORROW = re.compile(r'내일|다음\s*주|담주|월요일|월욜')
_SHORT = ('풋', '매도', '숏')


def _prices(s):
    return [float(x) for x in re.findall(_P, s)]


def _side(word):
    return 'short' if word in _SHORT else 'long'


def parse_view(text):
    """트윗 원문 → dict(kind, levels, box, bias, bias_level, bias_rel, horizon).

    가격은 **피터가(정규 선물)** 그대로다 — 미니 환산은 호출 쪽이 오프셋으로 한다.
    해석 못 한 숫자 트윗은 kind='note'(레벨만)로 남는다. 조용히 버리지 않는다."""
    raw = (text or '').strip()
    out = dict(kind='none', levels=[], box=None, bias=None, bias_level=None, bias_rel=None,
               horizon='tomorrow' if _TOMORROW.search(raw) else 'today')
    if not raw:
        return out
    flat = raw.replace('\n', ' ')
    lv = sorted({p for p in _prices(flat) if 300 <= p <= 3000})
    out['levels'] = lv
    if raw.startswith('[') or re.search(r'내역|브리핑|리포트', raw):
        out['kind'] = 'report'
        return out
    if _OTHER.search(flat) and not lv:
        return out
    if _RECAP.search(flat):
        out['kind'] = 'recap'
        return out
    m = _BOX.search(flat)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        out['kind'] = 'box'
        out['box'] = [min(a, b), max(a, b)]
    mb = _BIAS_LV.search(flat)
    if mb:
        out['bias'] = _side(mb.group(3))
        out['bias_level'] = float(mb.group(1))
        out['bias_rel'] = 'below' if mb.group(2) in ('아래', '밑') else 'above'
    else:
        mo = _BIAS.search(flat)
        if mo:
            out['bias'] = _side(mo.group(1) or mo.group(2))
    if out['kind'] == 'box':
        return out
    if out['bias']:
        out['kind'] = 'bias'
        return out
    if not lv:
        return out
    if _CLOSE.search(flat):
        out['kind'] = 'cond_close'
    elif _WAIT.search(flat):
        out['kind'] = 'wait'
    elif _PIVOT.search(flat):
        out['kind'] = 'pivot'
    else:
        out['kind'] = 'note'
    return out


SCORABLE = ('box', 'bias', 'pivot', 'cond_close')


def to_mini(view, offset):
    """피터가 → 미니가. offset 이 없으면 None(미측정 — 0 으로 메우지 않는다)."""
    if offset is None:
        return None
    f = lambda x: None if x is None else round(x + offset, 2)
    return dict(levels=[f(x) for x in view.get('levels') or []],
                box=[f(x) for x in view['box']] if view.get('box') else None,
                bias_level=f(view.get('bias_level')))
