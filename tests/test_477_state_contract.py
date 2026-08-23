# -*- coding: utf-8 -*-
"""[MW0602 477차 G-1 / 488차 계획 E] `session_state.json` 키 계약 불변식.

무엇을 막는가
-------------
477차가 규명한 결함: `data/session_state.json` 이 전일 EOD 기록(`eod_retrain_ok_date`
· `p8_last_success_date`)을 잃어 다음날 08:55 PreRetrain 이 스킵 판단을 못 하고
매일 fallback(마커 파일 직접 확인)에 의존했다. 원인 후보는 읽기-수정-쓰기 경합이었지만,
**같은 계열의 더 조용한 실패**가 하나 더 있다 —

    아무도 쓰지 않는 키를 누군가 읽는다.

그 경우 `state.get("key", "")` 는 조용히 빈 값을 돌려주고, 호출부는 "그런 일이 없었다"로
읽는다. 예외도 로그도 나지 않는다. 468차 G-2 가 정리한 *"안전장치가 죽어 있는데 매번
사람이 뒤늦게 발견"* 과 같은 형태이며, 실제로 그런 키가 생기는 경로는 흔하다 —
쓰는 쪽 파일을 리팩터링하면서 키 이름만 바뀌면 된다.

이 파일이 고정하는 불변식
------------------------
① **읽는 키 ⊆ 쓰는 키.** 어느 소스에서도 쓰지 않는 키를 읽으면 실패한다.
② 477차가 지목한 3키(`eod_retrain_ok_date` · `p8_last_success_date` ·
   `gbm_total_retrain_count`)가 **쓰는 쪽과 읽는 쪽 양쪽에** 살아 있다.
③ **스캐너 자체가 눈멀지 않았는지**를 먼저 본다(가드) — 쓰기 관용구
   `state["k"] = ` / `_ss["k"] = ` 로 잡히는 키가 충분히 있어야 한다. 관용구가 바뀌면
   ①이 "위반 0건"으로 공허하게 통과하기 때문이다.

왜 정적 스캔인가
----------------
`main.py` 는 PyQt/COM 의존이라 테스트에서 import 할 수 없다(`learning/model_meta.py`
가 별도 모듈로 떨어져 나온 것과 같은 이유). 소스를 텍스트로 읽어 키 집합만 뽑는다.
⚠ **라인 번호를 박지 않는다** — 477차 등록문은 `main.py:4553-4554` 식으로 위치를
적었지만, 그 숫자를 테스트에 넣으면 무관한 편집 한 줄에 깨져 규약이 미움받는다.

실행:
    pytest tests/test_477_state_contract.py -v
"""
import io
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# session_state 를 다루는 소스 전부. 새 파일이 생기면 여기 추가한다.
SOURCES = ("main.py", "retrain_eod.py")

# 쓰기: `state["key"] = ` / `_ss["key"] = ` / `data["key"] = ` …
# 변수 이름을 **열거**한다. 종전에는 `\w*(?:ss|state|data)\w*` 로 느슨하게 잡았는데
# `replace_state`(전략 교체 상태)·`replace_allowed` 같은 무관한 dict 가 딸려 들어와
# `reason`·`cooldown_progress` 를 session_state 키로 오인했다. 계약 테스트가 오탐을
# 내면 다음 세션이 NOT_SESSION_KEYS 에 아무거나 등록하며 무력화한다 — 좁게 잡는다.
# ⚠ 새 변수명으로 session_state 를 다루면 여기 추가할 것. 안 하면 `test_scanner_is_not_blind`
#   가 먼저 깨져 알려준다(그것이 그 가드의 존재 이유다).
# 실측 열거(2026-08-23 `grep -oE` 전수): `_ss` `_ss2` `_ss4` `_ss_eks` `_pre_ss`
# `_pm_ss` `_gap_ss` `_eod_ss` + `state`/`data`(메서드 지역변수).
# 접미/접두가 제각각인 것은 세션마다 새 지역변수를 만들어 써 왔기 때문이다.
# 🔴 **열거로 둔다 — 와일드카드로 넓히지 않는다.** `\w*ss\w*` 로 넓히면
#    `replace_state`(전략 교체)·`pass_*` 같은 무관한 dict 가 딸려 들어와
#    `reason`·`cooldown_progress` 를 세션 키로 오인한다(구현 중 실제로 겪었다).
#    오탐이 나면 다음 세션이 NOT_SESSION_KEYS 에 아무거나 넣으며 무력화한다.
_SS_VARS = (r"(?:_ss|_ss2|_ss4|_ss_eks|_pre_ss|_pm_ss|_gap_ss|_eod_ss"
            r"|state|_state|data)")

_WRITE_RE = re.compile(r"""(?:^|[^.\w])""" + _SS_VARS + r"""\s*\[\s*["'](\w+)["']\s*\]\s*=""",
                       re.MULTILINE)
# 읽기: `state.get("key"` / `_ss.get("key"` …
_READ_RE = re.compile(r"""(?:^|[^.\w])""" + _SS_VARS + r"""\s*\.get\(\s*["'](\w+)["']""")
# `pop("key", None)` 도 소비다 — 있는지 묻고 지운다.
_POP_RE = re.compile(r"""(?:^|[^.\w])""" + _SS_VARS + r"""\s*\.pop\(\s*["'](\w+)["']""")

# 세션 상태 키가 아닌 것들(같은 관용구를 쓰는 다른 dict). 이름이 아니라 **용도**로
# 제외하며, 제외 사유를 함께 적는다 — 목록이 커지면 그만큼 ①의 힘이 빠진다.
NOT_SESSION_KEYS = frozenset([
    # `_read_session_state()` 폴백이 만드는 기본 키. 계약 밖(항상 존재).
    "date", "count",
    # `_write_session_state()` 가 저장 직전에 **직접 만들어 넣는** 파생 상태.
    # 쓰기·읽기가 같은 함수 안에 있어 계약 위반이 될 수 없다.
    "profit_guard_state", "circuit_breaker_state",
])

# 477차가 지목한 3키 — 이것들이 사라지면 그때 그 사고가 재발한 것이다.
CRITICAL_KEYS = ("eod_retrain_ok_date", "p8_last_success_date",
                 "gbm_total_retrain_count")


def _scan():
    """(쓰는 키, 읽는 키, 소스별 쓰기 건수)를 소스에서 정적 추출한다."""
    writes, reads, per_file = set(), set(), {}
    for rel in SOURCES:
        path = os.path.join(_ROOT, rel)
        assert os.path.exists(path), "소스가 없다: %s" % rel
        src = io.open(path, encoding="utf-8", errors="replace").read()
        w = set(m.group(1) for m in _WRITE_RE.finditer(src))
        r = set(m.group(1) for m in _READ_RE.finditer(src))
        r |= set(m.group(1) for m in _POP_RE.finditer(src))
        per_file[rel] = len(w)
        writes |= w
        reads |= r
    return writes - NOT_SESSION_KEYS, reads - NOT_SESSION_KEYS, per_file


def test_scanner_is_not_blind():
    """③ 가드 — 스캐너가 실제로 무언가를 잡고 있는가.

    이 테스트가 없으면, 쓰기 관용구가 바뀌었을 때 ①이 **"위반 0건"으로 통과**한다.
    빈 집합은 언제나 부분집합이기 때문이다. 계측이 죽었는데 초록불이 켜지는 것 —
    이 프로젝트가 반복해서 당한 바로 그 형태다(468차 G-2).
    """
    writes, reads, per_file = _scan()
    # 하한 6 은 실측(2026-08-23: 쓰기 8키)에서 여유 2 를 뺀 값이다. 실측보다 높게 잡으면
    # 키 하나를 정당하게 지울 때마다 테스트가 깨지고, 0 이면 가드가 아무 일도 안 한다.
    assert len(writes) >= 6, (
        "쓰기 키를 %d개밖에 못 잡았다 — 관용구가 바뀌었을 수 있다. "
        "정규식을 현행 코드에 맞춰 갱신할 것: %s" % (len(writes), sorted(writes)))
    assert len(reads) >= 6, (
        "읽기 키를 %d개밖에 못 잡았다: %s" % (len(reads), sorted(reads)))
    for rel in SOURCES:
        assert per_file[rel] >= 1, "%s 에서 쓰기 키를 하나도 못 잡았다" % rel


def test_read_keys_are_written_somewhere():
    """① 읽는 키 ⊆ 쓰는 키 — 아무도 안 쓰는 키를 읽으면 조용한 빈 값이 된다."""
    writes, reads, _ = _scan()
    orphans = sorted(reads - writes)
    assert not orphans, (
        "읽기만 하고 아무도 쓰지 않는 session_state 키 %d개: %s\n"
        "→ 이 키들은 항상 기본값으로 읽힌다(예외도 로그도 없다). "
        "쓰는 쪽이 지워졌거나 키 이름이 갈라진 것이다. "
        "세션 상태 키가 아니라면 NOT_SESSION_KEYS 에 **사유와 함께** 등록할 것."
        % (len(orphans), orphans))


def test_477_critical_keys_survive():
    """② 477차가 지목한 3키가 쓰기·읽기 양쪽에 살아 있다."""
    writes, reads, _ = _scan()
    for key in CRITICAL_KEYS:
        assert key in writes, (
            "`%s` 를 쓰는 코드가 사라졌다 — 477차 결함(전일 EOD 기록 유실) 재발 경로다"
            % key)
        assert key in reads, (
            "`%s` 를 읽는 코드가 사라졌다 — 기록은 하는데 아무도 안 보면 죽은 계측이다"
            % key)


def test_eod_writer_and_main_reader_agree():
    """②-보강 — EOD 가 쓰는 키를 `main.py` 가 읽는지 **파일을 건너** 확인한다.

    ①은 전 소스 합집합이라, 두 키가 같은 파일 안에서만 쓰이고 읽혀도 통과한다.
    477차 사고는 **파일 경계를 넘는** 계약이 끊긴 것이었다(retrain_eod → main).
    """
    eod = io.open(os.path.join(_ROOT, "retrain_eod.py"),
                  encoding="utf-8", errors="replace").read()
    main = io.open(os.path.join(_ROOT, "main.py"),
                   encoding="utf-8", errors="replace").read()
    eod_writes = set(m.group(1) for m in _WRITE_RE.finditer(eod)) - NOT_SESSION_KEYS
    main_reads = set(m.group(1) for m in _READ_RE.finditer(main)) - NOT_SESSION_KEYS
    crossing = eod_writes & main_reads
    assert crossing, (
        "`retrain_eod.py` 가 쓰고 `main.py` 가 읽는 키가 하나도 없다 — "
        "EOD → 다음날 장전 계약이 끊겼다. 실측 기대: %s" % (sorted(eod_writes),))
    for key in ("eod_retrain_ok_date", "p8_last_success_date"):
        assert key in eod_writes, "EOD 가 `%s` 를 더는 쓰지 않는다" % key


if __name__ == "__main__":
    # pytest 가 없는 환경(py37_32 런타임 venv)에서도 돌도록 단독 러너를 둔다 —
    # AGENTS.md 「테스트」 절이 인정하는 혼재 스타일이다.
    # cp949 콘솔(Windows 기본)에서 —·× 같은 문자가 UnicodeEncodeError 를 낸다.
    # 테스트가 **실패를 보고하다가** 죽으면 실패 내용을 못 본다.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _fails = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        try:
            _fn()
            print("PASS %s" % _name)
        except AssertionError as _e:
            _fails += 1
            print("FAIL %s\n  %s" % (_name, _e))
    print("-" * 60)
    print("%s (%d fail)" % ("ALL PASS" if not _fails else "FAILED", _fails))
    sys.exit(1 if _fails else 0)
