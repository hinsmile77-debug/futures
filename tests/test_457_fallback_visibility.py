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


# ═════════════════════════════════════════════════════════════════════════
# [461차 / G-5] 계측 4원칙 ④ 3번째 규약의 자동 검출 — DB 계층
#
#   "DB 컬럼에 폴백값을 쓸 때는 폴백 여부 플래그를 같은 행에 써라."
#
# 이 규약은 457차부터 CLAUDE.md에 **문장으로는** 있었으나 자동 검출이 없었다.
# 위 검사는 런타임 상태(`getattr` 폴백)만 겨냥한다 — 스키마 계층은 사각지대였다.
#
# 실제로 그 사각지대에서 사고가 났다: 거래 0건인 날 `strategy_live_snapshots`에
# `win_rate=0.0` · `profit_factor=1.0`이 저장돼 EOD 리포트가 `WR=0.0% PF=1.00`을
# 찍었다. "승률 0%"와 "표본 없음"이 같은 숫자가 된 것이다(461차 F-7에서 수정 —
# `metrics_measured` 컬럼 신설 + WR/PF NULL 저장).
#
# ## 무엇을 잡는가
#
# 컬럼을 명시한 INSERT의 파라미터에 폴백 리터럴(`x or 0.5`, `d.get("k", 0)`)이
# 들어가는데, **컬럼 목록에 폴백/측정 여부 플래그가 없는** 경우.
#
# ## 한계 (좁게 잡는다)
#
# - SQL과 파라미터가 **같은 execute() 호출**에 리터럴로 있어야 본다. 파라미터를
#   변수로 미리 조립하면 못 잡는다.
# - `or None` / `or False` 는 제외 — 그건 "값 없음"을 지우지 않는다.
# - 플래그 컬럼 인식은 이름 규칙(`*_measured` / `*_fallback` / `*_unmeasured`)에
#   의존한다. 다른 이름의 판별자(예: `trade_count`)는 못 알아보므로 핀 목록에
#   근거를 적고 넣는다.
#
# ## 왜 "고치기"가 아니라 "핀 고정"인가
#
# 기존 4곳은 전부 검토했고(아래 근거) 지금 고칠 결함이 아니다. 이 검사의 값어치는
# **새로 생기는 것**을 막는 데 있다 — `_CROSS_MODULE` 핀과 같은 취지다.
# ═════════════════════════════════════════════════════════════════════════

import ast
import warnings

#: 폴백 리터럴을 DB에 쓰지만 플래그 컬럼이 없는 기존 지점. **근거를 반드시 적을 것.**
#: 키 = (파일경로, 테이블명)
_DB_FALLBACK_PINNED = {
    ("config/strategy_registry.py", "strategy_param_changes"):
        "val_from/val_to의 `.get(..,'')`. 빈 문자열은 눈에 보이는 '없음'이고, 행의 "
        "존재 자체가 '이 파라미터가 바뀌었다'는 사실이다. 0/0.5처럼 값으로 위장하지 않는다.",
    ("config/strategy_registry.py", "strategy_regime_matrix"):
        "trade_count 0 · win_rate/avg_pnl/expectancy 0.0. **같은 행의 trade_count가 "
        "판별자 역할을 한다** — trade_count=0이면 나머지는 무의미함이 자명하다. "
        "이름이 `*_measured`가 아닐 뿐 규약의 취지는 충족. 이름 통일은 별도 안건.",
    ("model/scaler_monitor_db.py", "scaler_daily"):
        "457차 G5가 `health` 계열은 이미 '미측정을 0으로 위장하지 않는다'로 고쳤다"
        "(docstring 명시). 남은 `stats.get(..,0)`은 당일 집계 카운터라 '관측 0회'와 "
        "'미측정'이 실질적으로 같다(집계 자체가 그날 돌았다는 뜻).",
    ("utils/db_utils.py", "raw_candles"):
        "OHLCV의 `.get(..,0.0)`. 452차가 bid1/ask1/oi/buy_vol/sell_vol은 이미 "
        "기본값 없이 읽도록 고쳤고(수집 계층 스키마 폴백 금지, 451차 program_* 전례), "
        "OHLC는 '없으면 봉이 아니다'라 상류가 보장한다. 같은 행에 bar_recovered 플래그도 있다.",
}

#: 폴백 여부를 같은 행에 남기는 컬럼의 이름 규칙.
_RE_FLAG_COL = re.compile(r"(_measured|_fallback|_unmeasured|_is_default)", re.I)

#: 컬럼을 명시한 INSERT.
_RE_INSERT = re.compile(
    r"INSERT\s+(?:OR\s+\w+\s+)?INTO\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", re.I | re.S)

#: DB 계층 검사 범위 — scripts 포함(리포트 생성기도 DB에 쓴다).
_DB_SCAN_DIRS = _SCAN_DIRS + ("scripts",)

_SENTINEL = object()


def _ast_str(node):
    """py3.7(ast.Str)·py3.8+(ast.Constant) 양쪽에서 문자열 리터럴을 꺼낸다.

    런타임이 py37_32라 `ast.Constant`만 보면 **아무것도 매치하지 않는다** —
    이 검사를 처음 짤 때 실제로 0건이 나와 검출기가 죽은 줄 알았다.
    """
    if isinstance(node, ast.Str):
        return node.s
    if hasattr(ast, "Constant") and isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    return None


def _ast_const(node):
    """리터럴 값 또는 _SENTINEL(리터럴이 아님)."""
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.NameConstant):
        return node.value
    if hasattr(ast, "Constant") and isinstance(node, ast.Constant):
        return node.value
    return _SENTINEL


def _fallback_literals(node):
    """`x or <리터럴>` / `d.get(k, <리터럴>)` 형태를 모은다.

    `or None` / `or False`는 제외 — 값을 만들어내지 않으므로 위장이 아니다.
    """
    found = []
    for n in ast.walk(node):
        if isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or):
            v = _ast_const(n.values[-1])
            if v is not _SENTINEL and v is not None and v is not False:
                found.append("or %r" % (v,))
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "get" and len(n.args) == 2):
            v = _ast_const(n.args[1])
            if v is not _SENTINEL and v is not None:
                found.append(".get(..., %r)" % (v,))
    return found


def _scan_db_fallbacks():
    """(파일, 테이블) → 폴백 리터럴 목록. 플래그 컬럼이 있는 INSERT는 뺀다."""
    files = list(_TARGETS)
    for d in _DB_SCAN_DIRS:
        root = os.path.join(_ROOT, d)
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, fs in os.walk(root):
            if "__pycache__" in dirpath:
                continue
            files += [os.path.relpath(os.path.join(dirpath, f), _ROOT)
                      for f in fs if f.endswith(".py")]

    hits, n_inserts = {}, 0
    for rel in files:
        try:
            # 스캔 대상 파일에 이미 있는 `\p` 같은 escape 경고가 이 검사의 출력으로
            # 새어 나오지 않게 한다 — 우리가 만든 문제가 아니고, 14건이 매 실행 찍힌다.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(_read(rel))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for n in ast.walk(tree):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ("execute", "executemany") and n.args):
                continue
            sql = _ast_str(n.args[0])
            if not sql:
                continue
            m = _RE_INSERT.search(sql)
            if not m:
                continue
            n_inserts += 1
            if len(n.args) < 2 or _RE_FLAG_COL.search(m.group(2)):
                continue
            fb = _fallback_literals(n.args[1])
            if fb:
                key = (rel.replace("\\", "/"), m.group(1))
                hits.setdefault(key, []).extend(fb)
    return hits, n_inserts


def test_db_fallback_columns_have_measured_flag():
    """DB에 폴백 리터럴을 쓰면서 같은 행에 플래그가 없는 **새** 지점이 없는가."""
    hits, n_inserts = _scan_db_fallbacks()
    assert n_inserts >= 10, (
        "INSERT 탐지가 %d건뿐이다 — 검출기가 죽었을 가능성이 높다 "
        "(py3.7 ast.Str 처리 확인)" % n_inserts)

    new = {k: v for k, v in hits.items() if k not in _DB_FALLBACK_PINNED}
    assert not new, (
        "DB 컬럼에 폴백값을 쓰는데 같은 행에 폴백 플래그가 없다 "
        "(계측 4원칙 4번째 규약):\n" +
        "\n".join("  %s -> %s : %s" % (f, t, ", ".join(sorted(set(v))))
                  for (f, t), v in sorted(new.items())) +
        "\n\n폴백 여부 컬럼(`*_measured`/`*_fallback`)을 같은 INSERT에 추가하거나, "
        "정말 문제없다면 `_DB_FALLBACK_PINNED`에 **근거와 함께** 등록할 것. "
        "근거 없이 등록하는 것은 규약 우회다.")


def test_db_fallback_pin_list_is_not_stale():
    """핀 목록에 남았으나 이미 고쳐진 항목이 없는가 — 목록이 굳는 것을 막는다."""
    hits, _ = _scan_db_fallbacks()
    stale = [k for k in _DB_FALLBACK_PINNED if k not in hits]
    assert not stale, (
        "`_DB_FALLBACK_PINNED`에 남아 있으나 더 이상 검출되지 않는 항목: %s "
        "(플래그가 추가됐거나 폴백이 제거됐다면 목록에서 지울 것)"
        % ", ".join("%s->%s" % k for k in stale))


def test_db_detector_actually_detects():
    """검출기가 살아 있는지 — F-7 이전의 `record_live_snapshot`을 재현해 확인한다."""
    bad = (
        'def f(cur, m):\n'
        '    cur.execute("INSERT INTO snap (a, win_rate) VALUES (?,?)",\n'
        '                (1, m.get("win_rate", 0.0)))\n'
    )
    good = (
        'def f(cur, m):\n'
        '    cur.execute("INSERT INTO snap (a, win_rate, metrics_measured) '
        'VALUES (?,?,?)", (1, m.get("win_rate", 0.0), 0))\n'
    )

    def _probe(src):
        tree = ast.parse(src)
        out = []
        for n in ast.walk(tree):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "execute" and len(n.args) >= 2):
                continue
            sql = _ast_str(n.args[0])
            m = _RE_INSERT.search(sql or "")
            if not m or _RE_FLAG_COL.search(m.group(2)):
                continue
            out += _fallback_literals(n.args[1])
        return out

    assert _probe(bad), "폴백 INSERT를 놓친다 — 검출기가 죽었다"
    assert not _probe(good), "플래그 컬럼이 있는데도 결함으로 잡는다 — 오탐"
