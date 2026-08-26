# -*- coding: utf-8 -*-
"""[MW0601 498차 / G-6] 「대사」라고 말하는 로그의 전수 인벤토리.

왜 이 파일이 있는가
-------------------
2026-08-26 하루에 대사 관련 결함이 **두 건** 나왔고 **둘 다 로그 문구는 정상으로
보였다**:

  · 이상점 1-9  `[NetRecon]` 축의 입력이 기회 의존적이라 그날치가 통째로 비었다
  · 이상점 1-10 `[BrokerPnl] … (broker gross 대사 일치)` 가 **자기 자신과 대사**했다
                (같은 함수가 방금 써넣은 엔진 gross 를 "브로커 gross"로 되읽었다)

493차가 계측 4원칙 ⑤(*"대사는 모든 축을 걸어라 · 대사 성공 로그에 무엇을 비교했는지
쓴다"*)를 신설한 **직후**인데도 그렇다. 개별로 잡아 오고 있는데 **「도달 불가 분기 +
자기참조 대사」를 한 번에 훑는 도구가 없었다.**

이 테스트가 그 도구다. 대사 로그마다 세 가지를 **명시적으로 등록**시킨다:

  ① 무엇과 무엇을 비교하는가
  ② 두 값의 원천이 서로 **독립**인가 (자기참조 여부)
  ③ 한쪽이 없을 때 무엇을 찍는가 — **0인가 미측정인가**

새 대사 로그가 생기면 스캐너가 등록되지 않은 태그를 찾아 실패한다. 즉 이 표를
갱신하지 않고는 새 대사를 들일 수 없다.

⚠ 이것은 **정적 검사**다 — 런타임 동작을 보장하지 않는다.
  실제 값 대사는 `test_493_commission_rate_and_net_recon.py` ·
  `test_498_broker_net_eod_and_gross_recon.py` 가 맡는다.
"""
import io
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

#: 스캔 대상 — 프로덕션 코드만. 테스트·문서·아카이브는 뺀다.
_SCAN_FILES = ["main.py"]
_SCAN_DIRS = ["utils", "strategy", "model", "learning", "collection"]

#: 대사를 표방하는 문자열의 표지. `preconnect`·`reconfigure` 같은 우연한 부분일치를
#: 피하려고 한국어 「대사」와 `[…Recon…]` 태그만 본다.
_KEY = re.compile(r"대사")
_RECON_TAG = re.compile(r"\[(\w*Recon\w*)\]")
_ANY_TAG = re.compile(r"\[([A-Za-z][A-Za-z0-9_]*)\]")


# ── 인벤토리 ────────────────────────────────────────────────────────────────
# 키 = 로그 태그. 값 = 계측 4원칙 ⑤가 요구하는 3칸 + 회귀 고정용 근거 문자열.
RECON_INVENTORY = {
    "NetRecon": {
        "compares": "엔진 net(trades 합산, 요율 가정 포함) vs 브로커 net(익일가예탁현금 − 예탁현금)",
        "independent": True,
        "why_independent": "브로커 net 은 CpTd6197 헤더 2개의 차이라 엔진 가정이 개입하지 않는다",
        # ③ 한쪽이 없을 때 — **0이 아니라 미측정**이라고 말해야 한다.
        "missing_literal": "브로커 net 미수신 — 대사 불가(0이 아니라 미측정)",
        "owner": "main.py: daily_close() / utils.db_utils.reconcile_daily_net()",
        "note": "493차 F-2. 2026-08-26 첫 라이브 발화에서 이상점 1-9를 실제로 잡아냈다",
    },
    "BrokerPnl": {
        "compares": "브로커 gross(CpTd6197 실현손익, TR 수신) vs 엔진 gross(trades 합산)",
        "independent": True,
        "why_independent": (
            "498차 F-9부터 **쓰기 전에** 읽는다. 그 전에는 "
            "`update_daily_broker_pnl_net()` 이 행을 만든 직후 되읽어 "
            "자기가 써넣은 엔진 gross 를 브로커 gross 로 오인했다(자기참조)"),
        "missing_literal": "브로커 gross 미수신",
        "owner": "main.py: daily_close() / utils.db_utils.fetch_broker_gross_origin()",
        "note": "gross 0 인 행은 `net_only` 로 갈라 「브로커가 0원이라고 했다」로 읽지 않는다",
    },
}


def _iter_sources():
    for rel in _SCAN_FILES:
        p = os.path.join(_ROOT, rel)
        if os.path.exists(p):
            yield rel.replace("\\", "/"), p
    for d in _SCAN_DIRS:
        base = os.path.join(_ROOT, d)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x != "__pycache__"]
            for fn in filenames:
                if fn.endswith(".py"):
                    p = os.path.join(dirpath, fn)
                    yield os.path.relpath(p, _ROOT).replace("\\", "/"), p


def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _owning_tag(lines, idx):
    """그 줄이 속한 로그 태그. 같은 줄에 없으면 위로 40줄까지 거슬러 찾는다.

    f-string 이 여러 줄로 쪼개져 꼬리 조각에는 태그가 없는 경우가 흔하다
    (`_f4_tail` 같은 조립 변수). 태그를 못 찾으면 None — 호출부가 실패로 다룬다.
    """
    for j in range(idx, max(-1, idx - 40), -1):
        m = _ANY_TAG.search(lines[j])
        if m:
            return m.group(1)
    return None


def _docstring_lines(lines):
    """docstring 안의 줄 번호 집합(0-based).

    docstring 은 **설명이지 로그가 아니다.** 주석과 같은 이유로 제외한다 —
    포함하면 이 프로젝트처럼 주석이 두꺼운 코드에서 스캐너가 설명문으로 가득 찬다.
    삼중따옴표 상태만 추적하는 휴리스틱이며, 그것으로 충분하다(로그 문자열은
    삼중따옴표로 쓰지 않는다).
    """
    inside = set()
    delim = None
    for i, ln in enumerate(lines):
        rest = ln
        while True:
            if delim is None:
                m = re.search(r'"""|\'\'\'', rest)
                if not m:
                    break
                delim = m.group(0)
                rest = rest[m.end():]
                inside.add(i)
                # 같은 줄에서 닫히면 한 줄짜리 docstring
                m2 = re.search(re.escape(delim), rest)
                if m2:
                    delim = None
                    rest = rest[m2.end():]
                    continue
                break
            else:
                inside.add(i)
                m2 = re.search(re.escape(delim), rest)
                if not m2:
                    break
                delim = None
                rest = rest[m2.end():]
        if delim is not None:
            inside.add(i)
    return inside


def _scan_hits():
    hits = []
    for rel, path in _iter_sources():
        lines = _read(path).splitlines()
        doc = _docstring_lines(lines)
        for i, ln in enumerate(lines):
            if i in doc:
                continue           # docstring 은 설명이지 로그가 아니다
            if ln.lstrip().startswith("#"):
                continue           # 주석도 마찬가지
            if not (_KEY.search(ln) or _RECON_TAG.search(ln)):
                continue
            if '"' not in ln and "'" not in ln:
                continue           # 문자열 리터럴이 아닌 줄(변수명 등)은 제외
            hits.append((rel, i + 1, ln.strip(), _owning_tag(lines, i)))
    return hits


# ── ① 등록되지 않은 대사 로그가 없다 ────────────────────────────────────────
def test_every_recon_log_is_registered():
    hits = _scan_hits()
    assert hits, "스캐너가 아무것도 못 찾았다 — 공허하게 통과하고 있다"
    unknown = sorted({(h[0], h[3] or "<태그없음>") for h in hits
                      if h[3] not in RECON_INVENTORY})
    assert not unknown, (
        "인벤토리에 없는 대사 로그가 있다. RECON_INVENTORY 에 "
        "①무엇과 비교 ②원천 독립 여부 ③한쪽 없을 때 무엇을 찍는가 를 등록할 것: %s"
        % unknown)


def test_no_untagged_recon_line():
    """태그 없는 대사 문구를 금지한다 — 어느 대사인지 특정할 수 없다."""
    orphan = [(h[0], h[1], h[2][:80]) for h in _scan_hits() if h[3] is None]
    assert not orphan, "로그 태그를 특정할 수 없는 대사 문구: %s" % orphan


# ── ② 3칸이 다 찼다 ────────────────────────────────────────────────────────
@pytest.mark.parametrize("tag", sorted(RECON_INVENTORY))
def test_inventory_entry_is_complete(tag):
    e = RECON_INVENTORY[tag]
    for k in ("compares", "independent", "why_independent", "missing_literal", "owner"):
        assert e.get(k) not in (None, ""), "%s: %s 칸이 비었다" % (tag, k)
    assert " vs " in e["compares"], \
        "%s: 「무엇과 무엇을」이 드러나지 않는다 — 'A vs B' 로 쓸 것" % tag
    assert e["independent"] is True, (
        "%s: 원천이 독립이 아니면 그것은 대사가 아니라 자기참조다. "
        "독립으로 만들거나 로그에서 「대사」라는 말을 빼라" % tag)


# ── ③ 「한쪽이 없을 때」 문구가 실제로 소스에 있다 ──────────────────────────
@pytest.mark.parametrize("tag", sorted(RECON_INVENTORY))
def test_missing_side_literal_exists_in_source(tag):
    """표가 낡는 것을 막는다 — 등록한 문구가 코드에서 사라지면 실패한다."""
    lit = RECON_INVENTORY[tag]["missing_literal"]
    found = any(lit in _read(p) for _, p in _iter_sources())
    assert found, (
        "%s: 등록된 「미측정」 문구가 소스에 없다 — 인벤토리가 낡았거나 "
        "폴백 가시화가 사라졌다: %r" % (tag, lit))


def test_missing_side_says_unmeasured_not_zero():
    """0과 미측정을 같은 말로 쓰지 않는다(계측 4원칙 ②)."""
    for tag, e in RECON_INVENTORY.items():
        lit = e["missing_literal"]
        assert ("미수신" in lit or "미측정" in lit or "없음" in lit), \
            "%s: 한쪽 결손을 「미측정」으로 표현하지 않는다: %r" % (tag, lit)


# ── ④ 🔴 자기참조 회귀 고정 — 읽기가 쓰기보다 앞선다 ────────────────────────
def test_gross_recon_reads_before_it_writes():
    """이상점 1-10 의 지문을 코드 순서로 고정한다.

    `fetch_broker_gross_origin()`(읽기)이 `update_daily_broker_pnl_net()`(쓰기)보다
    **앞**에 있어야 한다. 순서가 뒤집히면 「대사 일치」가 다시 0% 검증력이 된다.
    """
    src = _read(os.path.join(_ROOT, "main.py"))
    i_read = src.find("fetch_broker_gross_origin(today_str)")
    i_write = src.find("update_daily_broker_pnl_net(today_str")
    assert i_read > 0 and i_write > 0, "gross 대사 블록을 찾지 못했다"
    assert i_read < i_write, (
        "쓰기 뒤에 읽으면 방금 만든 엔진 gross 를 '브로커 gross'로 되읽는다 — "
        "이상점 1-10 이 재발했다")


def test_gross_recon_log_names_its_axes():
    """계측 4원칙 ⑤ — 「일치」만 찍지 않고 무엇을 비교했는지 쓴다."""
    src = _read(os.path.join(_ROOT, "main.py"))
    assert "vs engine gross 대사 일치" in src, \
        "gross 대사 성공 문구에 비교 축이 없다"
    assert "TR수신" in src, "브로커 쪽 원천·시각 표기가 없다"


def test_net_recon_log_names_broker_source():
    """[498차 F-8] net 「일치」가 실측인지 EOD 스냅샷 보정인지 밝힌다."""
    src = _read(os.path.join(_ROOT, "main.py"))
    assert "엔진 net vs 브로커 net" in src
    assert "broker_net_source" in src, \
        "브로커 net 의 출처를 로그가 말하지 않으면 「일치」의 무게를 알 수 없다"
