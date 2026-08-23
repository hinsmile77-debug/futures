# -*- coding: utf-8 -*-
"""[MW0602 487차 / F-8(B)·F-9, v9-dev 갈래 적용] 캠페인 채널 위생 불변식.

배경 (0821 이상점 1-17·1-18, 2026-08-23 멀티PC 정책 폐기)
--------------------------------------------------------
① dev 쪽 문제: 채널 [50]·[51]은 소비부만 `dev`에 들어오고 생산부(커밋 080c982)는
   `v9-dev`에만 있어 태어날 때부터 죽어 있었는데, 리포트가 `INSUFFICIENT`로
   표기해 "표본이 쌓이는 중"으로 매주 오독됐다. → F-8(B): 생산부 존재를 감지해
   없으면 `NOT_AVAILABLE_ON_THIS_BRANCH`로 분리 표기(생산부가 생기면 자동 복귀).
   **v9-dev는 생산부가 둘 다 있으므로 이 감지는 상시 정상 경로를 탄다** — 그래도
   방어 로직 자체는 해가 없어 그대로 가져왔다.
② dev 쪽 문제: 채널 번호 [51]이 두 채널(462차 저변동성 / 471차 후속7 ConstOut)에
   중복 배정돼 dev의 F-9가 ConstOut을 [54]로 재배정했다. **v9-dev에는 462차
   저변동성 채널이 없어 애초에 충돌이 없다** — 번호 체계는 각자 관리한다는
   정책 폐기 원칙(MW0601_이관_점검사항_20260823.md §2)에 따라 v9-dev는 ConstOut을
   원래 번호 [51]로 유지한다. F-9 재배정 자체는 cherry-pick하지 않았다.

이 파일이 고정하는 불변식 3종 (v9-dev 갈래)
-------------------------------------------
1. 요약표 채널 번호 유일성 — 같은 번호가 두 행에 붙으면 깨진다
2. ConstOut 채널 번호 — v9-dev는 [51] 유지(재배정 없음), [54]는 쓰지 않는다
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


def test_1_summary_channel_numbers_unique():
    """요약표에서 같은 채널 번호가 두 행에 붙으면 안 된다 (0821 1-18의 재발 방지).

    수집 대상: ① `L.append("| [NN] …` 리터럴 행 ② `_row_462(NN, …)` 포맷 행.
    [47-B]류 접미 라벨은 별개 채널이라 숫자 패턴에 안 걸린다(의도된 제외).
    """
    src = _src()
    nums = re.findall(r'L\.append\("\| \[(\d+)\]', src)
    nums += re.findall(r"_row_462\((\d+),", src)
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    assert not dupes, "요약표 채널 번호 중복: %s — 새 채널 등록 시 번호를 확인하라" % dupes


def test_2_constout_stays_at_51():
    """v9-dev는 462차 저변동성 채널이 없어 [51] 충돌이 없다 — ConstOut은 [51] 유지.

    dev 쪽 F-9([51]→[54] 재배정)는 v9-dev에는 적용하지 않았다(근거 없는 번호
    변경이 되므로). [54]가 다시 등장하면 그 재배정을 실수로 되가져온 것이다.
    """
    src = _src()
    assert "| [51] ConstOut" in src, "[51] ConstOut 요약행이 없다"
    assert "[54] ConstOut" not in src, "[54] ConstOut 재출현 — dev 전용 F-9 재배정이 잘못 반영됐다"


def test_3_f8b_branch_gating_wired():
    """생산부 부재 채널의 분리 표기 배선이 살아 있는가.

    어휘 등록이 빠지면 _fmt_verdict가 조용히 INSUFFICIENT로 표시해(생성기 주석의
    경고 그대로) F-8(B)가 소리 없이 무효가 된다 — 그래서 소스 불변식으로 고정한다.
    ⚠ 생산부가 dev에 생기는 것은 이 테스트를 깨지 않는다 — 감지가 참이 되어
    채널이 되살아나는 것이 설계된 동작이다.
    """
    src = _src()
    assert '"NOT_AVAILABLE_ON_THIS_BRANCH":' in src, "_fmt_verdict 어휘 미등록"
    assert src.count("_branch_unavailable(") >= 3, "정의 1 + [50]/[51] 호출 2가 있어야 한다"
    assert '_has_module("scripts.direction_bias_watch")' in src, "[50] 생산부 감지 배선 소실"
    assert "_has_const_out_column()" in src, "[51] 생산부(컬럼) 감지 배선 소실"
