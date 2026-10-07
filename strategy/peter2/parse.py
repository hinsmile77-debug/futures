# -*- coding: utf-8 -*-
"""트윗 한 건 → 매매 사실(fact) 목록. **순수 함수**(Qt·DB·시계 의존 없음).

왜 대시보드 파서(`PETER_RULES`)를 쓰지 않나
    그쪽은 **차트에 그리기** 위한 넓은 그물이다 — 맥점·예고·잡담 속 숫자까지 건져서
    선으로 남긴다. 여기는 **주문을 내기** 위한 좁은 그물이어야 한다. 진입 하나를
    잘못 읽으면 실제 주문이 나간다. 그래서 문장 단위로, 가격이 먼저 오고 그 뒤에
    매수/매도가 오는 꼴만 진입으로 인정한다. 놓친 것은 `_raw` 와 장후 사료에 그대로
    남으므로 잃는 것은 없다.

실측 표본(2026-08-03 ~ 10-07 `_raw` 393줄)에서 뽑은 문형
    진입    「1096 하방 돌파시 매도. 손절가 1100」「1050까지 내려오면 매수」
            「1035-36에서 매수」「1079 지금 매도 손절가 1085」「1094매수 1088 손절」
    체결    「1096 매도 체결.」「1010체결됨」「1085-7에서 매수 체결」「늦어도 1087에 모두 매도 체결」
    손절가  「손절가 1111로 변경」「손절가 다시 변경 1113」「손절가 1116 입니다」
    청산가  「청산가 1096」「1024 청산가로 변경」「1056 청산으로 변경」「청산은 1097에서」
            「그냥 1082에 청산하자」「1000오면 수익실현으로 수정」「목표가 1005」
    조건청산 「만약 995 이탈하면 청산해」「1063이탈하면 바로 청산」 → 손절 끌어올림
    청산완료 「1100 손절.」「1083 청산체결」「1081 청산완료」「995 수익 청산」「1000 도달! 수익 실현」
    취소    「…매수금지」「매수하면 안됨」
    무시    「코스닥150 …」 — 다른 상품
"""
import re

# 가격: 3–4자리 정수 + 선택 소수 1–2자리. 앞뒤가 숫자가 아니어야 한다.
_P = r'(?<![\d.])(\d{3,4}(?:\.\d{1,2})?)(?![\d])'
# 범위 표기 「1085-7」「1035-36」「1072-73」
_RANGE = re.compile(r'(?<![\d.])(\d{3,4})\s*-\s*(\d{1,2})(?![\d])')

_OTHER_PRODUCT = re.compile(r'코스닥|KOSDAQ|kosdaq|나스닥|NASDAQ|삼전|하닉|닉스')
# 계획·조건·가정 — 진입으로 읽지 않는다(문장 단위)
_NOT_ORDER = re.compile(
    r'금지|하면\s*안|말고|관망|대기|예정|생각|가능|싶은|위험|조심|'
    r'못\s|했지|했잖|라고|였|이었|할\s*사람|하는\s*사람|분할|외쳤|외친|'
    r'(매수|매도)분|(매수|매도)를|(매수|매도)세')
# 결산·복기 트윗(「6P 수익 - 5P 손실」「= 11p」) — 진입으로 읽지 않는다(청산 보고는 살린다)
_RECAP = re.compile(r'\d\s*[pP](?![a-zA-Z])|포인트|=')
_CANCEL = re.compile(r'(매수|매도)\s*금지|(매수|매도)하면\s*안|취소')
_SIDE = re.compile(r'(재)?(매수|매도)')
_FILL = re.compile(r'체결')
_EXIT_WORD = re.compile(r'청산|수익\s*실현|손절')


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _expand_range(sentence):
    """「1085-7」→ (1085, 1087). 없으면 None."""
    m = _RANGE.search(sentence)
    if not m:
        return None
    a, tail = m.group(1), m.group(2)
    b = a[:len(a) - len(tail)] + tail
    lo, hi = float(a), float(b)
    if hi < lo or hi - lo > 5:
        return None
    return lo, hi


def split_sentences(text):
    """문장 단위로 자른다. 소수점은 자르지 않는다(「1087.5」)."""
    t = (text or '').replace('\r', '\n')
    parts = re.split(r'\n+|(?<!\d)\.(?!\d)|\.(?=\s)|!+|\?+|/', t)
    return [p.strip() for p in parts if p and p.strip()]


def _prices(sentence):
    return [float(x) for x in re.findall(_P, sentence)]


def parse_tweet(text):
    """트윗 원문 → {'ignore': reason|None, 'facts': [...]}

    fact 종류
        entry   {side:'L'|'S', level, lo, hi, mode:'brk_up'|'brk_dn'|'limit', amend:bool}
        fill    {side:'L'|'S'|None, level|None}
        stop    {level, ctx:'entry'|'set'|'same'}
        tighten {level}                       조건부 청산(「N 이탈하면 청산」) — 손절 끌어올림
        target  {level}
        exit    {level|None, kind:'stop'|'take'}  그가 이미 나갔다
        cancel  {}
    """
    raw = (text or '').strip()
    if not raw:
        return {'ignore': 'empty', 'facts': []}
    if _OTHER_PRODUCT.search(raw):
        return {'ignore': 'other_product', 'facts': []}
    # 「[피터리 - 8월 선물매매 내역]」「…브리핑」 — 보고서다. 지난 숫자가 손절가로 읽힌다(08-31 실측).
    if raw.startswith('[') or re.search(r'내역|브리핑|리포트', raw):
        return {'ignore': 'report', 'facts': []}

    facts = []
    has_entry = False
    for si, s in enumerate(split_sentences(raw)):
        for f in _parse_sentence(s, facts):
            f['_si'] = si
            facts.append(f)
    recap = bool(_RECAP.search(raw))
    if recap:
        # 결산 트윗에서는 **이미 일어난 일**(체결·청산)만 살린다. 지난 진입가·손절가가
        # 새 지시로 읽히면 보유 포지션의 손절선이 엉뚱하게 움직인다.
        facts = [f for f in facts if f['type'] in ('exit', 'fill')]
    _ent = [f['_si'] for f in facts if f['type'] == 'entry']
    ent_si = min(_ent) if _ent else None
    if ent_si is not None:
        # 진입 **뒤** 문장의 「N 손절」은 손절선이다(「982.5 매수 / 977.5 손절」).
        # 진입 **앞** 문장의 「N 손절」은 앞 포지션의 손절 보고다 — 청산으로 남긴다
        # (「1047 손절. / 1049 돌파시 매수. 손절 1046」, 09-14 실측: 버리면 그의 손절 1건이 사라진다).
        has_stop_after = any(x['type'] == 'stop' and x['_si'] >= ent_si for x in facts)
        conv = []
        for f in facts:
            if f['type'] == 'exit' and f['_si'] < ent_si:
                conv.append(f)
            elif (f['type'] == 'exit' and f.get('kind') == 'stop'
                  and f.get('level') is not None and not has_stop_after):
                conv.append({'type': 'stop', 'level': f['level'], 'ctx': 'entry', '_si': f['_si']})
                has_stop_after = True
            elif f['type'] == 'exit':
                continue
            else:
                conv.append(f)
        facts = conv
        for f in facts:
            if f['type'] == 'stop' and f['ctx'] == 'set' and f['_si'] >= ent_si:
                f['ctx'] = 'entry'
    for f in facts:
        f.pop('_si', None)
    return {'ignore': None, 'facts': facts, 'recap': recap}


def _parse_sentence(s, prior):
    out = []
    ps = _prices(s)

    # ── 취소 ─────────────────────────────────────────────
    if _CANCEL.search(s):
        out.append({'type': 'cancel'})
        return out

    # ── 체결 보고 ─────────────────────────────────────────
    if _FILL.search(s):
        if re.search(r'청산\s*체결|청산체결', s):
            out.append({'type': 'exit', 'level': ps[0] if ps else None, 'kind': 'take'})
        elif re.search(r'손절\s*체결', s):
            out.append({'type': 'exit', 'level': ps[0] if ps else None, 'kind': 'stop'})
        else:
            sm = _SIDE.search(s)
            side = None
            if sm:
                side = 'L' if sm.group(2) == '매수' else 'S'
            rg = _expand_range(s)
            lvl = ((rg[0] + rg[1]) / 2.0) if rg else (ps[0] if ps else None)
            out.append({'type': 'fill', 'side': side, 'level': lvl})
        # 체결 문장 뒤에 붙은 손절가·청산가(「1080 매수 체결. 청산가 1090」은 문장이 갈린다)
        out.extend(_mgmt(s, skip_first_price=True))
        return out

    # ── 청산 완료 보고 ────────────────────────────────────
    #   「1100 손절.」「1023 청산.」「1081 청산완료」「995 수익 청산」「1000 도달! 수익 실현」
    m = re.match(r'^\D{0,6}' + _P + r'\s*(?:수익\s*)?(손절|청산)\s*(완료|했|함)?\s*$', s)
    if m and not re.search(r'청산가|손절가|으로|로\s*변경|이탈|오면|하면', s):
        out.append({'type': 'exit', 'level': float(m.group(1)),
                    'kind': 'stop' if m.group(2) == '손절' else 'take'})
        return out
    # 「만약 여기서 밀리면 985에 수익실현」은 조건부 — 아래 _mgmt 가 손절 끌어올림으로 읽는다.
    if re.search(r'청산\s*완료|수익\s*실현\s*$|^수익\s*실현', s) \
            and not re.search(r'면|만약|으로\s*수정|로\s*수정', s):
        out.append({'type': 'exit', 'level': ps[0] if ps else None, 'kind': 'take'})
        return out
    if re.match(r'^\D{0,8}(\d+차\s*)?손절\s*(했|완료|체결)?\s*$', s) and not ps:
        # 「3차 손절」「2차 손절」 — 가격 없는 손절 보고
        out.append({'type': 'exit', 'level': None, 'kind': 'stop'})
        return out

    # ── 진입 지시 ─────────────────────────────────────────
    ent = _entry(s, ps)
    if ent:
        out.append(ent)
        out.extend(_mgmt(s, skip_level=ent['level'], entry_ctx=True))
        return out

    # ── 관리(손절가·청산가·조건청산) ───────────────────────
    out.extend(_mgmt(s))
    return out


def _entry(s, ps):
    """가격이 앞서고 매수/매도가 뒤따르는 짧은 지시문만 진입으로 인정한다."""
    if not ps:
        return None
    sm = _SIDE.search(s)
    if not sm:
        return None
    if _NOT_ORDER.search(s) or _FILL.search(s) or re.search(r'청산', s):
        return None
    # 인용(「'1110 갈거니까 매도할거면…'」 — 댓글 인용, 09-07 실측)
    if re.search(u"['\"‘’“”]", s):
        return None
    if len(s) > 48:
        return None
    # 첫 가격이 매수/매도보다 앞에 있어야 한다(「매수 맥점 변경 965돌파시 매수」는 두 번째 매수 기준)
    side_pos = [mm.start() for mm in _SIDE.finditer(s)]
    m_first = re.search(_P, s)
    if not m_first:
        return None
    after = [p for p in side_pos if p > m_first.start()]
    if not after:
        return None
    # 가격 앞 군더더기는 숫자 없는 8자 이내 또는 알려진 서두
    pre = s[:m_first.start()]
    if len(pre) > 14 and not re.search(r'(변경|재도전|다시|한게임|오면\s*$)', pre):
        return None
    sidem = None
    for mm in _SIDE.finditer(s):
        if mm.start() > m_first.start():
            sidem = mm
            break
    side = 'L' if sidem.group(2) == '매수' else 'S'
    seg = s[m_first.start():sidem.end()]
    rg = _expand_range(seg)
    lvl = float(m_first.group(1))
    lo = hi = lvl
    if rg:
        lo, hi = rg
    # 「1045나 46에서」
    m_or = re.search(r'(\d{3,4})\s*(?:나|또는)\s*(\d{2,4})\s*에서', seg)
    if m_or:
        a = float(m_or.group(1))
        bt = m_or.group(2)
        b = float(m_or.group(1)[:len(m_or.group(1)) - len(bt)] + bt) if len(bt) < 3 else float(bt)
        lo, hi = min(a, b), max(a, b)
    if '돌파' in seg or '돌파' in s[:sidem.start()]:
        if re.search(r'하방|하향|아래|밑', seg):
            mode = 'brk_dn'
        elif re.search(r'상향|위로', seg):
            mode = 'brk_up'
        else:
            mode = 'brk_up' if side == 'L' else 'brk_dn'
    else:
        mode = 'limit'
    # 기준 가격은 「유리한 쪽 끝」이 아니라 범위의 중간 — 오프셋 오차를 범위가 흡수한다.
    level = round((lo + hi) / 2.0, 2)
    return {'type': 'entry', 'side': side, 'level': level, 'lo': lo, 'hi': hi,
            'mode': mode, 'amend': bool(re.search(r'변경|수정', s))}


def _mgmt(s, skip_level=None, entry_ctx=False, skip_first_price=False):
    out = []
    # 손절가
    if re.search(r'손절가?\s*동일', s):
        out.append({'type': 'stop', 'level': None, 'ctx': 'same'})
    else:
        lv = None
        m = re.search(r'손절가?\s*(?:를|은|는|:)?\s*(?:다시\s*)?(?:변경\s*)?' + _P, s)
        if m:
            lv = float(m.group(1))
        else:
            m = re.search(_P + r'\s*(?:이탈시|이탈하면|밑으로\s*가면)?\s*(?:다시\s*)?손절(?!한)', s)
            if m and (skip_level is None or abs(float(m.group(1)) - skip_level) > 1e-9):
                lv = float(m.group(1))
        if lv is not None and (skip_level is None or abs(lv - skip_level) > 1e-9):
            out.append({'type': 'stop', 'level': lv, 'ctx': 'entry' if entry_ctx else 'set'})
    # 청산가 / 목표가
    t = None
    for pat in (r'청산가\s*(?:를|은|는|:)?\s*(?:다시\s*)?' + _P,
                _P + r'\s*(?:로|으로)?\s*청산가',
                _P + r'\s*(?:로|으로)?\s*청산\s*(?:으로|로)?\s*(?:다시\s*)?(?:변경|수정)',
                r'청산은\s*' + _P,
                r'그냥\s*' + _P + r'\s*(?:에|에서)\s*청산',
                r'^\D{0,4}' + _P + r'\s*에\s*청산\s*$',
                r'목표가?\s*' + _P,
                _P + r'\s*목표가',
                _P + r'\s*(?:오면|도달시|가면)\s*(?:그냥\s*)?(?:수익\s*실현|청산)'):
        m = re.search(pat, s)
        if m:
            t = float(m.group(1))
            break
    if t is not None and not (skip_level is not None and abs(t - skip_level) < 1e-9 and not re.search(r'청산', s)):
        out.append({'type': 'target', 'level': t})
    # 조건부 청산 → 손절 끌어올림
    m = re.search(_P + r'\s*(?:을|를)?\s*(?:이탈하면|이탈시|깨지면|밑으로\s*내려가면)\s*.{0,10}?(?:청산|수익\s*실현|정리)', s) \
        or re.search(r'밀리면\s*' + _P + r'\s*에\s*(?:수익\s*실현|청산)', s)
    if m:
        out.append({'type': 'tighten', 'level': float(m.group(1))})
    return out
