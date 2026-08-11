# -*- coding: utf-8 -*-
"""457차 / G8 — 계측 4원칙 ④ "폴백 가시화" 자동 검출.

## 무엇을 잡는가

`getattr(self, "_x", 기본값)` 으로 **읽히기만 하고 어디에서도 `self._x = ` 로
할당되지 않는** 인스턴스 속성. 이 형태는 예외를 내지 않고 조용히 기본값을 반환하므로
결함이 로그·DB·대시보드에서 **정상값처럼 보인다.**

2026-08-11 하루에만 같은 패턴이 4건 나왔다:

    self._entry_horizon_pre   읽기 2곳 · 할당 0곳 → 영구 "1m"
                              → ensemble_decisions.meta_gate_horizon 370/370건 '1m'
                                (실제 진입은 3m·3m·5m). MetaGate가 3m 진입을 1m
                                스코어러로 심사했고, meta_labels 조인 키가 오염됐다.
    self._entry_horizon       읽기 1곳 · 할당 0곳 → SHAP 패널 CORE 그룹 영구 고정
    recent_accuracy()         빈 버퍼 → 조용히 0.5 (daily_stats 8거래일 연속)
    _verified_today           리셋 뒤 읽기 → 항상 0

규약 전문: `CLAUDE.md` "계측 4원칙" §④.

## 이 검사의 한계 (일부러 좁게 잡는다)

- **정적 검사**다. `setattr(self, name, ...)`이나 동적 이름 생성은 못 잡는다.
- 밑줄로 시작하는 속성(`_x`)만 본다 — 공개 속성은 외부 주입이 정상일 수 있다.
- 기본값이 **없는** `getattr(self, "_x")`(2인자)는 대상이 아니다 — 그건 AttributeError로
  터지므로 조용한 결함이 아니다.

**허용 목록(`_ALLOWED`)에 넣기 전에 반드시 근거를 주석으로 남길 것.** 이 검사를
통과시키려고 목록에 추가하는 것은 규약을 우회하는 것이다.
"""
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

#: 검사 대상 파일 — 런타임 상태를 들고 도는 큰 모듈부터.
_TARGETS = ["main.py"]

#: 할당부를 찾을 때 훑을 범위. 교차모듈 주입(`system._x = ...`)을 놓치지 않기 위해
#: 리포지토리 전체를 본다 — 좁게 보면 정상 주입을 결함으로 오탐한다.
_SCAN_DIRS = ("collection", "config", "dashboard", "features", "learning",
              "model", "safety", "strategy", "utils")

#: 의도적으로 할당하지 않는 속성. **근거를 반드시 적을 것.**
_ALLOWED = {
    # (파일, 속성): 사유
    # 예) ("main.py", "_debug_only_flag"): "개발자가 콘솔에서 수동 주입하는 디버그 훅",
}

#: **교차모듈 주입** — 읽는 파일 밖에서 할당된다. 결함은 아니지만 취약한 결합이라
#: 목록을 고정해 둔다. 새 항목이 조용히 늘어나면 아래 테스트가 알려준다.
#: 형식 — 속성: (할당하는 위치, 사유)
_CROSS_MODULE = {
    "_futures_code": (
        "strategy/runtime/broker_runtime_service.py:76  `system._futures_code = code`",
        "브로커 로그인 시 근월물 코드를 결정해 주입한다. main.py는 19곳에서 읽기만 "
        "하므로 정적으로는 '미할당'처럼 보이지만 실제로는 기동 시 반드시 세팅된다.",
    ),
}

#: `getattr(self, "_name", default)` — 3인자 형태만(기본값 있는 것만) 잡는다.
_RE_GETATTR = re.compile(r'getattr\(\s*self\s*,\s*["\'](_[A-Za-z0-9_]+)["\']\s*,')

#: `self._name = ` / `self._name: T = ` / `self._name +=` 등 모든 바인딩 형태.
_RE_ASSIGN_TMPL = (
    r'self\.%s\s*(?::[^=\n]+)?(?:=[^=]|\+=|-=|\*=|/=|\|=|&=)'
)

#: 교차모듈 주입 — `<무엇이든>._name = ` (self가 아닌 대상에 꽂는 형태).
_RE_XMOD_TMPL = r'\w+\.%s\s*(?::[^=\n]+)?=[^=]'


def _read(path):
    with open(os.path.join(_ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def _repo_sources():
    """검사 범위의 .py 원문 목록 (테스트 자신은 제외 — 문자열 예시가 오탐을 만든다)."""
    srcs = [_read(p) for p in _TARGETS]
    for d in _SCAN_DIRS:
        root = os.path.join(_ROOT, d)
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, files in os.walk(root):
            if "__pycache__" in dirpath:
                continue
            for f in files:
                if not f.endswith(".py"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, f), _ROOT)
                try:
                    srcs.append(_read(rel))
                except (OSError, UnicodeDecodeError):
                    pass
    return srcs


def _classify(path):
    """(never_assigned, cross_module) — 속성명 → 읽기 횟수.

    never_assigned : 리포지토리 어디에서도 할당되지 않는다 → **결함**
    cross_module   : 읽는 파일 밖에서만 할당된다 → 취약하지만 동작한다
    """
    local = _read(path)
    all_srcs = _repo_sources()
    reads = {}
    for m in _RE_GETATTR.finditer(local):
        reads[m.group(1)] = reads.get(m.group(1), 0) + 1

    never, xmod = {}, {}
    for name, n in sorted(reads.items()):
        if (path, name) in _ALLOWED:
            continue
        esc = re.escape(name)
        if (re.search(_RE_ASSIGN_TMPL % esc, local)
                or re.search(r'setattr\(\s*self\s*,\s*["\']%s["\']' % esc, local)):
            continue   # 같은 파일에서 할당 — 정상
        if any(re.search(_RE_XMOD_TMPL % esc, s) for s in all_srcs):
            xmod[name] = n
        else:
            never[name] = n
    return never, xmod


@pytest.mark.parametrize("path", _TARGETS)
def test_no_unassigned_getattr_fallback(path):
    """계측 4원칙 ④ — 리포지토리 어디에서도 할당되지 않는 폴백 읽기는 조용한 결함이다."""
    never, _ = _classify(path)
    assert not never, (
        "%s: `getattr(self, \"…\", 기본값)`으로 읽히지만 **리포지토리 어디에서도 할당되지 "
        "않는** 속성 %d개.\n"
        "  → 폴백이 영구 고정된다(2026-08-11 _entry_horizon_pre 사고와 동일 패턴:\n"
        "     meta_gate_horizon 370/370건이 '1m'으로 굳었다).\n"
        "  → __init__에서 명시 초기화하고 실제로 갱신하거나, 미설정을 None으로 두고\n"
        "     폴백 시점에 로그를 남길 것. 상세: CLAUDE.md '계측 4원칙' §④\n"
        "  목록: %s"
        % (path, len(never),
           ", ".join("%s(읽기 %d회)" % (n, c) for n, c in sorted(never.items()))))


@pytest.mark.parametrize("path", _TARGETS)
def test_cross_module_injection_list_is_pinned(path):
    """교차모듈 주입은 결함이 아니지만 **조용히 늘어나면 안 된다**.

    읽는 곳과 쓰는 곳이 다른 파일이면 정적으로 추적이 끊긴다. 그 취약성을 목록으로
    고정해, 새로 생길 때 근거를 적도록 강제한다.
    """
    _, xmod = _classify(path)
    unknown = sorted(set(xmod) - set(_CROSS_MODULE))
    assert not unknown, (
        "%s: 새 교차모듈 주입 속성 %d개 — `_CROSS_MODULE`에 **할당 위치와 근거를 적고** "
        "추가할 것.\n  목록: %s"
        % (path, len(unknown),
           ", ".join("%s(읽기 %d회)" % (n, xmod[n]) for n in unknown)))
    stale = sorted(set(_CROSS_MODULE) - set(xmod))
    assert not stale, (
        "`_CROSS_MODULE`에 남아 있으나 더 이상 해당 없는 항목: %s "
        "(같은 파일에서 할당되도록 고쳐졌다면 목록에서 지울 것)" % ", ".join(stale))


def test_detector_actually_detects():
    """검출기 자체가 살아 있는지 — 457차 이전 상태를 인위적으로 재현해 확인한다.

    이 테스트가 없으면 정규식이 조용히 아무것도 매치하지 않게 되어도
    위 테스트가 통과해버린다(검출기가 죽었는데 "깨끗하다"고 보고하는 상태).
    """
    src = (
        'class X:\n'
        '    def a(self):\n'
        '        return getattr(self, "_never_set", "1m")\n'
        '    def b(self):\n'
        '        self._is_set = 3\n'
        '        return getattr(self, "_is_set", 0)\n'
    )
    names = {m.group(1) for m in _RE_GETATTR.finditer(src)}
    assert names == {"_never_set", "_is_set"}, "getattr 정규식이 깨졌다"
    assert not re.search(_RE_ASSIGN_TMPL % "_never_set", src), "할당 정규식 오탐"
    assert re.search(_RE_ASSIGN_TMPL % "_is_set", src), "할당 정규식이 할당을 놓친다"


def test_annotated_assignment_counts():
    """`self._x: bool = False` 형태(457차가 추가한 초기화)를 할당으로 인정하는가."""
    src = 'self._entry_horizon_pre: str = "1m"\n'
    assert re.search(_RE_ASSIGN_TMPL % "_entry_horizon_pre", src), (
        "타입 주석 있는 할당을 놓치면 457차 수정이 미할당으로 오탐된다")
