# -*- coding: utf-8 -*-
"""[MW0602 554차 / 1-6 단계 1] 핀 해제 사전 관측 도구 — 회귀 테스트.

이 도구가 지키려는 것은 하나다: **핀을 해제하면 어느 채널의 verdict 가 뒤집히나.**
`--impact`(commission_rate_recon)는 왕복 비용이 얼마나 오르는지만 답하고, 461차
`mdd_pct` 사고가 가르친 것은 *"측정값 재정의가 판정을 뒤집었는데 아무도 몰랐다"* 였다.

🔴 **작성 중 이 도구 자신이 두 번 틀렸다. 그 둘을 여기 고정한다.**

  ① **가드가 공허하게 통과했다.** 쓰기 탐지 정규식이 `UPDATE\\s+\\w` 뒤에 `\\b` 를
     달아 **한 글자 테이블명만** 매치했다. `UPDATE signal_decay_exits` 가 안 걸려
     「쓰기 함수 0개」로 보였고, 그러면 위반 목록도 비어 **가드가 통과한다**.
     지켜야 할 것이 있는데 초록불이 켜지는 형태 — 488차 후속2가 잡아낸
     *"지킨다고 믿는 초록불"* 과 같다.
  ② **결정표에 구멍이 생겼다.** `eval_gp_cross_channels` 는 verdict 를 한 겹 아래
     (`out["tight"]["verdict"]`)에 넣는데 최상위만 읽어 `-` 로 비었다.
     하필 1-6 의 **당사자 채널**이라, 정작 물어야 할 행이 빈 채로 표가 나왔다.

⚠ 이 테스트는 라이브 DB 를 열지 않는다 — 정적 분석 함수만 검사한다.
"""
import io
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

_SCRIPT = os.path.join(_ROOT, "scripts", "cost_pin_release_preview.py")


def _code_only(path):
    """독스트링·주석을 걷어낸 코드 본문.

    ⚠ 원문 전체를 훑으면 **설명문 속 이름**이 코드로 오인된다. 이 도구의
      독스트링은 `_COST_CONSUMERS` 를 «그 사고의 원인»으로 인용하고 있어,
      단순 `in src` 검사는 그것을 잡는다(test_538 T6 에서 같은 실수를 했다).
    """
    import ast as _ast
    src = io.open(path, encoding="utf-8").read()
    tree = _ast.parse(src, filename=path)
    drop = set()
    for node in _ast.walk(tree):
        if not isinstance(node, (_ast.Module, _ast.FunctionDef,
                                 _ast.AsyncFunctionDef, _ast.ClassDef)):
            continue
        if _ast.get_docstring(node, clean=False) is None:
            continue
        first = node.body[0]
        end = getattr(first, "end_lineno", first.lineno)
        for ln in range(first.lineno, end + 1):
            drop.add(ln)
    return "\n".join("" if i in drop else ln.split("#", 1)[0]
                     for i, ln in enumerate(src.splitlines(), 1))


def _load():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_cppv_554", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    if not os.path.exists(_SCRIPT):
        pytest.skip("도구 없음: %s" % _SCRIPT)
    return _load()


# ── ① 가드가 공허하지 않은가 ────────────────────────────────────────────────
def test_t1_write_guard_actually_finds_writers(mod):
    """🔴 쓰기 함수를 **실제로** 찾아내는가.

    0건이면 위반 목록도 비어 가드가 통과한다 — 그 통과는 아무것도 보증하지 않는다.
    2026-09-09 실측 11개(`resolve_and_eval_*` 10 + `_backfill_shadow_mfe`).
    """
    writers, bad = mod._assert_no_unexpected_writes()
    assert len(writers) >= 10, (
        "쓰기 함수를 %d개밖에 못 찾았다 — 탐지가 죽었다(공허한 참). 찾은 것: %s"
        % (len(writers), writers))
    assert not bad, "TRADES_DB 밖으로 나가는 쓰기: %s" % bad


def test_t2_write_regex_matches_real_multichar_tables(mod):
    """원 결함 재현 — 여러 글자 테이블명이 걸려야 한다."""
    writers, _ = mod._assert_no_unexpected_writes()
    # 실측으로 확인된 대표 쓰기 함수들
    for fn in ("resolve_and_eval_signal_decay", "resolve_and_eval_hurst_gate"):
        assert fn in writers, "%s 가 쓰기 함수로 안 잡힌다" % fn


def test_t3_docstring_mentions_are_not_counted_as_sql(mod):
    """`_conn()` 은 독스트링에 `UPDATE` 를 적을 뿐 쓰지 않는다 — 오탐 금지.

    주석·설명문까지 SQL 로 세면 안전한 함수가 위반으로 올라오고, 그러면 가드가
    늑대소년이 되어 곧 무시된다.
    """
    writers, _ = mod._assert_no_unexpected_writes()
    assert "_conn" not in writers, (
        "`_conn` 이 쓰기 함수로 잡혔다 — 독스트링을 SQL 로 세고 있다")


def test_t4_guard_is_db_based_not_name_based(mod):
    """이름 규약이 아니라 **쓰기 대상 DB** 로 판정하는가.

    `_backfill_shadow_mfe` 는 `resolve_and_eval_*` 이름 규약 밖이지만
    `_conn(TRADES_DB)` 로 쓰므로 **안전**하다. 이름으로 가르면 이것이 위반으로
    올라온다(초안이 실제로 그랬다).
    """
    writers, bad = mod._assert_no_unexpected_writes()
    assert "_backfill_shadow_mfe" in writers, "이 함수는 쓰기 함수로 잡혀야 한다"
    assert "_backfill_shadow_mfe" not in bad, (
        "이름 규약 밖이라는 이유로 위반 처리됐다 — 판정은 DB 대상으로 할 것")


# ── ② 대상 함수 자동 식별 ───────────────────────────────────────────────────
def test_t5_cost_funcs_are_auto_discovered(mod):
    """손 목록을 두지 않는다 — `_COST_CONSUMERS`(파일 목록)가 뚫린 것이 이 사고다."""
    funcs = mod.discover_cost_dependent_funcs()
    assert len(funcs) >= 10, "비용 의존 함수 %d개 — 탐지가 죽었다" % len(funcs)
    # 1-6 의 당사자와 대표 채널이 반드시 들어 있어야 한다
    for fn in ("eval_gp_cross_channels", "eval_meta_gate_channel",
               "resolve_and_eval_hurst_gate"):
        assert fn in funcs, "%s 가 비용 의존 목록에서 빠졌다" % fn
    assert "_COST_CONSUMERS" not in _code_only(_SCRIPT), (
        "손 목록을 도입하지 말 것(이 사고의 원인)")


def test_t6_no_hardcoded_function_list(mod):
    """자동 식별을 우회하는 하드코딩 목록이 생기지 않았는가."""
    # 채널 이름이 코드에 리터럴로 박히면 자동 식별이 무의미해진다.
    # (독스트링의 예시 언급은 허용 — `_code_only` 가 걷어낸다)
    assert "resolve_and_eval_hurst_gate" not in _code_only(_SCRIPT), (
        "채널명이 코드에 하드코딩됐다 — 자동 식별이 무의미해진다")


# ── ② 중첩 verdict 수집 ─────────────────────────────────────────────────────
def test_t9_nested_verdicts_are_collected(mod):
    """🔴 한 함수가 채널 여럿을 내면 **각각** 행이 되어야 한다.

    `eval_gp_cross_channels` 는 `out["tight"]["verdict"]` / `out["any"]["verdict"]`
    로 두 채널을 낸다. 최상위 `verdict` 만 읽으면 그 행이 `-` 로 비고, 하필
    그 채널이 1-6 의 **당사자**라 정작 물어야 할 칸이 빈 표가 나온다.

    ⚠ 이 검사가 없으면 초안의 ② 결함이 그대로 되살아난다 — 실제로 변이시험에서
      「중첩 수집 제거」가 **아무 테스트도 깨뜨리지 않았다**(그래서 이 검사를 넣었다).
    """
    class _Stub(object):
        COST_MODEL_COMMISSION_RATE = 0.000015
        TRADES_DB = ":memory:"

        @staticmethod
        def eval_nested():
            return {"tight": {"verdict": "PASS"}, "any": {"verdict": "FAIL"}}

        @staticmethod
        def eval_flat():
            return {"verdict": "INSUFFICIENT"}

    got = mod._run_pass(_Stub, ["eval_nested", "eval_flat"], 0.000019,
                        ":memory:", 28)
    assert got.get("eval_nested[tight]", {}).get("verdict") == "PASS", got
    assert got.get("eval_nested[any]", {}).get("verdict") == "FAIL", got
    assert got.get("eval_flat", {}).get("verdict") == "INSUFFICIENT", got
    assert "eval_nested" not in got, "중첩인데 최상위 행이 남았다(빈 행이 된다)"


def test_t10_unparseable_result_is_unmeasured_not_equal(mod):
    """verdict 를 못 구한 것은 **미측정**이지 '동일'이 아니다(계측 4원칙 ②)."""
    class _Stub(object):
        COST_MODEL_COMMISSION_RATE = 0.000015
        TRADES_DB = ":memory:"

        @staticmethod
        def eval_broken():
            return {"n": 3}          # verdict 도 중첩도 없다

        @staticmethod
        def eval_raises():
            raise RuntimeError("boom")

    got = mod._run_pass(_Stub, ["eval_broken", "eval_raises"], 0.000019,
                        ":memory:", 28)
    assert got["eval_broken"]["verdict"] is None
    assert got["eval_broken"]["error"], "사유 없이 조용히 None 이면 안 된다"
    assert "boom" in (got["eval_raises"]["error"] or "")


def test_t11_run_pass_restores_globals(mod):
    """요율·DB 전역을 반드시 원복한다 — 흘리면 다음 패스가 오염된다."""
    class _Stub(object):
        COST_MODEL_COMMISSION_RATE = 0.000015
        TRADES_DB = "LIVE"

        @staticmethod
        def eval_x():
            return {"verdict": "PASS"}

    mod._run_pass(_Stub, ["eval_x"], 0.000019, "COPY", 28)
    assert _Stub.COST_MODEL_COMMISSION_RATE == 0.000015, "요율이 흘렀다"
    assert _Stub.TRADES_DB == "LIVE", "🔴 DB 경로가 흘렀다 — 라이브를 열 수 있다"


# ── 안전 계약 ───────────────────────────────────────────────────────────────
def test_t7_tool_never_writes_live_db(mod):
    """도구 자신은 라이브 DB 에 쓰지 않는다 — 복사본에서만 돈다."""
    code = _code_only(_SCRIPT)
    # 라이브 경로는 읽기 전용(uri mode=ro)으로만 연다
    assert "mode=ro" in code, "라이브 trades.db 를 읽기 전용으로 열어야 한다"
    # ⚠ `UPDATE` 는 제외한다 — 이 도구는 쓰기 **탐지 정규식**에 그 단어를 갖고 있고
    #   그것은 SQL 이 아니다. 실제로 실행될 수 있는 두 형태만 본다.
    for kw in ("INSERT INTO", "DELETE FROM"):
        assert kw not in code.upper(), (
            "도구가 직접 쓰기 SQL 을 갖고 있다: %s" % kw)


def test_t8_declares_verdict_neutrality(mod):
    """관측 전용임을 문서가 직접 말하는가 — 다음 세션이 판정 근거로 쓰지 않도록."""
    src = io.open(_SCRIPT, encoding="utf-8").read()
    assert "판정 무영향" in src or "관측 전용" in src  # 여기는 독스트링이 대상이다
    assert "사전등록 합격선은 무변경" in src
