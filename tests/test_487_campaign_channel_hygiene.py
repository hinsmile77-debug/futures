# -*- coding: utf-8 -*-
"""[MW0602 487차 / F-8(B)·F-9] 캠페인 채널 위생 불변식.

배경 (0821 이상점 1-17·1-18, 2026-08-23 멀티PC 정책 폐기)
--------------------------------------------------------
① 채널 [50]·[54]는 소비부만 `dev`에 들어오고 생산부(커밋 080c982)는 `v9-dev`에만
   있어 태어날 때부터 죽어 있었는데, 리포트가 `INSUFFICIENT`로 표기해 "표본이
   쌓이는 중"으로 매주 오독됐다. → F-8(B): 생산부 존재를 감지해 없으면
   `NOT_AVAILABLE_ON_THIS_BRANCH`로 분리 표기(생산부가 생기면 자동 복귀).
② 채널 번호 [51]이 두 채널(462차 저변동성 / 471차 후속7 ConstOut)에 중복 배정돼
   같은 번호가 다른 것을 가리켰다. → F-9: 선착 우선 — 저변동성이 [51] 유지,
   ConstOut은 [54]로 재배정(채널 키 문자열은 불변 — 이력 식별자다).

이 파일이 고정하는 불변식 3종
-----------------------------
1. 요약표 채널 번호 유일성 — 같은 번호가 두 행에 붙으면 깨진다
2. F-9 재배정 상태 — [54] ConstOut 존재 · [51] ConstOut 부재 · 저변동성 [51] 유지
3. F-8(B) 배선 — NOT_AVAILABLE 어휘 등록 + 두 채널 모두 생산부 감지로 가드

실행:
    pytest tests/test_487_campaign_channel_hygiene.py
"""
import io
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEN = os.path.join(_ROOT, "scripts", "generate_validation_campaign_report.py")


def _src():
    with io.open(_GEN, encoding="utf-8") as f:
        return f.read()


def _R():
    """리포트 생성기 모듈 — 유일성 검사의 **단일 출처**를 여기서 가져온다."""
    import sys
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    import scripts.generate_validation_campaign_report as R
    return R


def test_1_summary_channel_numbers_unique():
    """요약표에서 같은 채널 번호가 두 행에 붙으면 안 된다 (0821 1-18의 재발 방지).

    🔴 [MW0602 564차 후속4 / R2] 검사를 **생성기의 함수로 일원화**했다.
    종전에는 이 테스트가 자체 정규식을 들고 있었다. 그러면 런타임(리포트 생성)과
    테스트가 서로 다른 정의를 보게 되어 한쪽만 느슨해질 수 있다.

    ⚠ **이 테스트는 더 이상 유일한 경보가 아니다.** 같은 함수를 `build_report()`
    진입부가 부르므로, 스위트가 죽어 있어도 EOD 체인이 리포트를 **쓰기 전에**
    멈춘다 — 2026-09-07 충돌이 6일간 묻힌 경로를 막은 것이 그 변경의 요점이다.
    """
    R = _R()
    try:
        R.assert_channel_numbers_unique()
    except R.ChannelNumberCollision as e:
        raise AssertionError(str(e))


def test_2_f9_renumbering_holds():
    """[54]=ConstOut · [51]=저변동성(462차 선착 유지)이 뒤집히면 깨진다."""
    src = _src()
    assert "| [54] ConstOut" in src, "[54] ConstOut 요약행이 없다 — F-9 재배정이 풀렸다"
    assert "| [51] ConstOut" not in src, "[51] ConstOut 행 재출현 — 0821 1-18 중복 재발"
    assert "_row_462(51," in src, "저변동성 채널의 [51]이 사라졌다 — 선착 우선 원칙 위반"


def test_3_f8b_branch_gating_wired():
    """생산부 부재 채널의 분리 표기 배선이 살아 있는가.

    어휘 등록이 빠지면 _fmt_verdict가 조용히 INSUFFICIENT로 표시해(생성기 주석의
    경고 그대로) F-8(B)가 소리 없이 무효가 된다 — 그래서 소스 불변식으로 고정한다.
    ⚠ 생산부가 dev에 생기는 것은 이 테스트를 깨지 않는다 — 감지가 참이 되어
    채널이 되살아나는 것이 설계된 동작이다.
    """
    src = _src()
    assert '"NOT_AVAILABLE_ON_THIS_BRANCH":' in src, "_fmt_verdict 어휘 미등록"
    assert src.count("_branch_unavailable(") >= 3, "정의 1 + [50]/[54] 호출 2가 있어야 한다"
    assert '_has_module("scripts.direction_bias_watch")' in src, "[50] 생산부 감지 배선 소실"
    assert "_has_const_out_column()" in src, "[54] 생산부(컬럼) 감지 배선 소실"


# ── 4. PC 대역 [2026-09-13 564차 후속2] ──────────────────────────────────────
#
# 단일 출처 — CLAUDE.md 「캠페인 채널 번호 — PC별 대역 분할」 표와 같은 값이어야 한다.
# 한쪽만 고치면 규약과 코드가 갈린다(461차 `mdd_pct` 계열).
_CHANNEL_BANDS = {
    "MW0602": (62, 79),
    "MW0601": (80, 159),
}
_LEGACY_MAX = 61          # 채택 시점(2026-09-13) 양 브랜치가 이미 소진한 구간


def test_4_channel_numbers_respect_pc_bands():
    """새 채널 번호가 **선언된 대역 안**에 있는가.

    2026-09-07 에 두 PC 가 각자 「다음 빈 번호」를 뽑아 `[58]`·`[59]` 가 겹쳤다.
    대역을 나누면 그 충돌이 **애초에 생기지 않는다** — 상대를 보지 않아도 된다.

    ⚠ **한계**: 이 검사는 누가 배정했는지 모른다. 상대 대역을 침범한 배정은 그
    브랜치에서는 통과하고, 합류 시점에 `test_1` 이 중복으로 잡는다.
    발생 억제(대역) + 사후 탐지(중복)의 조합이지 완전한 차단이 아니다.
    """
    nums = set(int(n) for n in _R().channel_numbers())
    assert nums, "채널 번호를 하나도 못 읽었다 — 정규식이 생성기와 어긋났다"

    lo = min(b[0] for b in _CHANNEL_BANDS.values())
    assert lo == _LEGACY_MAX + 1, (
        "레거시 상한과 대역 시작 사이에 빈 구간이 있다 — 그 구간 번호는 아무도 "
        "책임지지 않는다: legacy<=%d, 최저 대역 시작=%d" % (_LEGACY_MAX, lo))

    spans = sorted(_CHANNEL_BANDS.items(), key=lambda kv: kv[1])
    for (n1, (a1, b1)), (n2, (a2, _)) in zip(spans, spans[1:]):
        assert b1 < a2, "대역이 겹친다: %s%s vs %s%s" % (n1, (a1, b1), n2, (a2, _))

    hi = max(b[1] for b in _CHANNEL_BANDS.values())
    stray = sorted(n for n in nums
                   if n > _LEGACY_MAX
                   and not any(a <= n <= b for a, b in _CHANNEL_BANDS.values()))
    assert not stray, (
        "선언된 대역 밖의 채널 번호: %s (레거시<=%d · 대역 %s · 상한 %d). "
        "CLAUDE.md 「캠페인 채널 번호 — PC별 대역 분할」 표를 먼저 고치고 커밋할 것"
        % (stray, _LEGACY_MAX, dict(_CHANNEL_BANDS), hi))


def test_5_collision_check_is_not_vacuous():
    """검사가 **실제로 중복을 잡는가** — 단일 출처가 조용히 느슨해지는 것을 막는다.

    `test_1` 은 "지금 중복이 없다"만 말한다. 검사 자체가 망가져 아무것도 못 잡게
    되어도 `test_1` 은 그대로 초록이다 — 488차가 잡아낸 *"지킨다고 믿는 초록불"* 이
    정확히 그 형태다. 그래서 인공 충돌을 먹여 **예외가 나는지** 본다.

    두 등록 관용구(직접 렌더 · `_row_462` 헬퍼)를 각각 시험한다 — 한쪽 패턴만
    살아 있어도 나머지는 사각지대가 된다.
    """
    R = _R()
    nl = chr(10)
    cases = {
        "직접 렌더": nl.join(['L.append("| [58] A |")', 'L.append("| [58] B |")']),
        "_row_462 헬퍼": nl.join(["_row_462(59, x)", "_row_462(59, y)"]),
    }
    for label, src in sorted(cases.items()):
        try:
            R.assert_channel_numbers_unique(src)
        except R.ChannelNumberCollision:
            continue
        raise AssertionError(
            "%s 관용구의 인공 중복을 잡지 못했다 — 유일성 검사가 무력화됐다" % label)

    # 과탐도 막는다 — 정상 소스에서 멈추면 EOD 체인이 매번 죽는다.
    ok_src = nl.join(['L.append("| [62] A |")', "_row_462(63, x)"])
    R.assert_channel_numbers_unique(ok_src)


def test_6_check_is_wired_into_report_generation():
    """검사가 **리포트 생성 경로에 실제로 걸려 있는가** — R2 의 요점.

    함수가 옳게 동작해도(`test_5`) 아무도 부르지 않으면 의미가 없다. 이 저장소가
    반복해서 당한 형태가 정확히 그것이다 — FP-CRITICAL 은 학습분포 저장 함수가
    프로덕션에서 호출된 적이 없어 2개월간 PSI=0.0 이었고, TOX 섀도는 계산만 하고
    아무도 소비하지 않아 한 달 넘게 죽어 있었다.

    ⚠ 호출 위치는 `build_report()` **진입부**여야 한다. 뒤에 있으면 이미 무거운
    집계가 끝난 뒤이고, 더 뒤면 오염된 리포트가 이미 파일로 나간다.
    """
    import inspect
    src = inspect.getsource(_R().build_report)
    assert "assert_channel_numbers_unique()" in src, (
        "build_report 가 유일성 검사를 부르지 않는다 — 검사가 테스트 안에서만 "
        "살아 있으면 스위트가 죽는 순간 다시 안 들린다(O-77 이 그랬다)")
    body = [l for l in src.splitlines()[1:] if l.strip()
            and not l.strip().startswith("#")]
    assert body and "assert_channel_numbers_unique()" in body[0], (
        "검사가 build_report 진입부가 아니다 — 실제 첫 문장: %r" % (body[:1],))
