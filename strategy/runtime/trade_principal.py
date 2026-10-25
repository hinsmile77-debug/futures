# -*- coding: utf-8 -*-
"""[MW0602 거래주체분리] 거래주체(미륵 · 신동 · 피터) — 계좌에서 실거래하는 주체는 하나다.

선택된 주체의 진입만 실주문으로 나가고, 나머지는 섀도로 기록한다
(`docs/거래주체분리/거래주체분리_구현계획_MW0602-20261012.md`).

사용자 결정(2026-10-12)
    · 전환은 장중이라도 **FLAT(보유·대기주문 없음)이면 언제든**.
    · 다음 날에는 **전날 선택을 유지**한다(파일이 날짜를 넘어 남는다).

어디에 무엇이 남나
    data/trade_principal.json          현재 주체 {principal, set_at, reason}
    data/trade_principal_log.jsonl     전환 이력(append-only)

🔴 주체를 모르는 출처(운영·복구 경로)는 **항상 실주문을 허용**한다 — 수동 진입·브로커 동기화
   복구를 섀도로 돌리면 실계좌와 엔진 상태가 갈라진다.
"""
import datetime
import io
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_PATH = os.path.join(_ROOT, 'data', 'trade_principal.json')
LOG_PATH = os.path.join(_ROOT, 'data', 'trade_principal_log.jsonl')

MIREUK, SHINDONG, PETER = 'MIREUK', 'SHINDONG', 'PETER'
PRINCIPALS = (MIREUK, SHINDONG, PETER)
DEFAULT = MIREUK
LABEL = {MIREUK: '미륵', SHINDONG: '신동', PETER: '피터'}

# 진입 출처 → 판단 주체. 여기 없는 출처(OPERATOR_MANUAL · BROKER_SYNC_RECOVERY ·
# GHOST_PENDING_MISS · OPERATOR_RESTORE …)는 주체와 무관하게 통과한다.
from config.constants import PETER2_ENTRY_SOURCE, SHINDONG_ENTRY_SOURCE   # noqa: E402
SOURCE_PRINCIPAL = {'SYSTEM_AUTO': MIREUK, SHINDONG_ENTRY_SOURCE: SHINDONG,
                    PETER2_ENTRY_SOURCE: PETER}
PRINCIPAL_SOURCE = {v: k for k, v in SOURCE_PRINCIPAL.items()}


def _cfg(name):
    try:
        from config import settings as _s
        return getattr(_s, name, None)
    except Exception:
        return None


def allowed(cfg=None):
    """[MW0601 713차 / 신동 주체 전환 P2] 선택 가능한 거래주체 → tuple(PRINCIPALS 순서).

    `config.settings.PRINCIPAL_ALLOWED`(None = 3주체 전부, 종전). cfg 를 주면 설정 대신 그 값(테스트).
    알 수 없는 이름은 버리고, 남는 것이 없으면 3주체 전부다 — 오타로 아무도 못 고르는 것보다 안전.
    """
    if cfg is None:
        cfg = _cfg('PRINCIPAL_ALLOWED')
    if cfg is None:
        return PRINCIPALS
    if isinstance(cfg, str):
        cfg = (cfg,)
    try:
        want = {str(x or '').upper() for x in cfg}
    except TypeError:
        return PRINCIPALS
    out = tuple(p for p in PRINCIPALS if p in want)
    return out or PRINCIPALS


def default_principal(cfg=None, allowed_set=None):
    """파일 없음·깨짐·허용 밖일 때의 주체. `PRINCIPAL_DEFAULT`(None = 미륵, 종전)가 허용 집합 밖이면
    허용 집합의 첫 주체(미륵 → 신동 → 피터 순)."""
    al = allowed_set if allowed_set is not None else allowed()
    if cfg is None:
        cfg = _cfg('PRINCIPAL_DEFAULT')
    p = str(cfg or DEFAULT).upper()
    return p if p in al else al[0]


def load_file():
    """파일(data/trade_principal.json)의 선택만 — 허용 집합을 보지 않는다. → dict 또는 None(없음·깨짐).
    `save()` 의 이력 `prev` 가 이것이다."""
    try:
        with io.open(STATE_PATH, encoding='utf-8') as f:
            d = json.load(f)
        p = str(d.get('principal') or '').upper()
        if p in PRINCIPALS:
            return {'principal': p, 'set_at': d.get('set_at'), 'reason': d.get('reason'),
                    'measured': True}
    except (OSError, IOError, ValueError, TypeError, AttributeError):
        pass
    return None


def load():
    """→ dict(principal, set_at, reason, measured, fallback). 파일이 없거나 깨졌으면 기본값이고
    `measured=False` 로 그 사실을 남긴다(계측 4원칙 ②·④ — 기본값을 선택값처럼 보이지 않게).

    [713차] 파일의 주체가 허용 집합(`PRINCIPAL_ALLOWED`) 밖이면 기본값으로 읽고 `fallback=True` ·
    `file_principal` 로 남긴다. **파일은 고치지 않는다** — 허용 집합을 되돌리면 파일 선택으로 돌아간다.
    """
    al = allowed()
    rec = load_file()
    if rec is not None and rec['principal'] in al:
        return dict(rec, fallback=False)
    dp = default_principal(allowed_set=al)
    if rec is not None:
        return {'principal': dp, 'set_at': rec['set_at'], 'measured': True, 'fallback': True,
                'reason': 'not_allowed:%s' % rec['principal'], 'file_principal': rec['principal']}
    return {'principal': dp, 'set_at': None, 'reason': 'default(파일 없음)', 'measured': False,
            'fallback': True}


def current():
    return load()['principal']


def can_switch(pos_status, has_pending):
    """→ (ok, reason). FLAT 이고 대기주문이 없을 때만 바꿀 수 있다(사용자 결정 2026-10-12)."""
    if str(pos_status or '').upper() != 'FLAT':
        return False, '포지션 보유 중(%s) — 청산 뒤 전환' % pos_status
    if has_pending:
        return False, '대기 주문 있음 — 체결·취소 뒤 전환'
    return True, 'ok'


def save(principal, reason='', now=None):
    """현재 주체를 쓰고 이력에 한 줄 남긴다. 알 수 없는 값·허용 밖 값([713차])은 ValueError."""
    p = str(principal or '').upper()
    if p not in PRINCIPALS:
        raise ValueError('unknown principal: %r' % (principal,))
    if p not in allowed():
        raise ValueError('principal not allowed: %r (PRINCIPAL_ALLOWED=%r)' % (p, allowed()))
    now = now or datetime.datetime.now()
    prev = load_file() or {'principal': DEFAULT, 'measured': False}
    rec = {'principal': p, 'set_at': now.isoformat(timespec='seconds'), 'reason': reason}
    d = os.path.dirname(STATE_PATH)
    if not os.path.isdir(d):
        os.makedirs(d)
    tmp = STATE_PATH + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(rec, f, ensure_ascii=False)
    os.replace(tmp, STATE_PATH)
    with io.open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(dict(rec, prev=prev['principal'], prev_measured=prev['measured']),
                           ensure_ascii=False) + '\n')
    return rec


def principal_of(entry_source):
    """진입 출처의 판단 주체. 주체 무관 출처면 None."""
    return SOURCE_PRINCIPAL.get(str(entry_source or ''))


def is_live_source(entry_source, principal):
    """이 출처의 진입이 지금 실주문으로 나가도 되는가."""
    owner = principal_of(entry_source)
    return owner is None or owner == principal


def label(principal):
    return LABEL.get(principal, str(principal))


# ── 섀도·집행 기록 ─────────────────────────────────────────────
DAY_ROOT = os.path.join(_ROOT, 'data', 'principal')


def day_path(date, name):
    """data/principal/<날짜>/<name> — 폴더가 없으면 만든다."""
    d = os.path.join(DAY_ROOT, date)
    if not os.path.isdir(d):
        os.makedirs(d)
    return os.path.join(d, name)


def append_shadow(date, name, rec):
    """섀도 기록 한 줄(append-only JSONL). 실패는 호출부가 로그로 남긴다."""
    with io.open(day_path(date, name), 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def read_jsonl(date, name):
    p = os.path.join(DAY_ROOT, date, name)
    out = []
    try:
        with io.open(p, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        continue
    except (OSError, IOError):
        pass
    return out


def read_json(date, name, default=None):
    try:
        with io.open(os.path.join(DAY_ROOT, date, name), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, IOError, ValueError):
        return default


def write_json(date, name, obj):
    p = day_path(date, name)
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)
