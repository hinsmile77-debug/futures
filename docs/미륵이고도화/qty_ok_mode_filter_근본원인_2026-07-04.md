# qty_ok / mode_filter_ok 근본원인 딥다이브

작성일: 2026-07-04
관련: `NEXT_TODO.md` 290차 "qty_ok/mode_filter_ok 근본원인 조사" 후속 (v9-dev 브랜치 작업 —
[[project_v9_dev_branch_split]] 규칙에 따라 dev_memory 4개 파일은 건드리지 않고 여기에 기록)

배경: `gate_blocking_report.md`(290차)에서 18개 진입 게이트 중 마지널 통과율 최저 2개가
`qty_ok`(9.6%)·`mode_filter_ok`(11.4%)였고, 특히 `qty_ok`는 운영 대시보드의
`entry_block_reason` 문구에 아예 등장하지 않아 "지금까지 안 보이던 병목"으로 지목됐다.
버그인지 의도된 설계인지에 따라 §13(다중게이트 재설계) 우선순위가 갈리므로 코드 추적 +
실제 DB 교차분석으로 규명했다.

---

## 1. qty_ok — 독립 게이트가 아니라 "최종 결과 스코어보드"

### 코드 경로

`main.py:5501` `_qty_display = 0` 초기화 → `direction != 0 and position.status == "FLAT"`
분기 안에서만(:5504~) Sizer가 값을 채움(:5717) → 이후 4개의 독립적인 하위 오버라이드가
각자 `_qty_display = 0`으로 되돌릴 수 있음:

- Degraded Mode 저신뢰 차단 (:5862~)
- ExecutionGovernor `action == "block"` (:5882~)
- MetaGate `action == "skip"` (:5892~)
- ToxicityGate `action == "block"` (:5902~)

### DB 실측 (최근 30일, `entry_gate_json` 보유 4,540행)

```
direction=0(무신호):         1,244건 → qty_ok=False 100% (설계상 당연 — 신호 자체가 없음)
direction≠0(방향신호 있음):   3,296건 → qty_ok=True 겨우 13.3%
grade=C(체크리스트는 통과)인데도 qty_ok=False: 1,153/1,394건 (82.7%)
```

### 결론

`qty_ok`는 체크리스트 9항목 + 하위 오버라이드 4종 **전체가 실패한 결과가 모이는 지표**다.
"18개 게이트 중 최악의 단일 병목"이라는 이전 프레이밍은 부정확 — qty_ok 자체를 손보는
게 아니라, **Degraded Mode·ExecutionGovernor·MetaGate·ToxicityGate 4종을 §13 L3
소프트 게이트의 점수 항목에 포함**시키는 것이 맞는 방향이다. 이 4종은 지금까지 v9
설계안(§13)에서 명시적으로 다루지 않았던 항목들이라, L3 재설계 범위를 넓혀야 한다.

---

## 2. mode_filter_ok — [2026-07-04 정정] 사용자 토글 아님. `grade`(원본) vs `_final_grade`(체크리스트 후) 혼동이 근본원인

> **최초 진단(아래 취소선)은 틀렸음이 DB 직접조회로 확인돼 정정한다.** 사용자가 "거의 조작하지
> 않는다"고 반박한 것이 계기 — `ensemble_decisions.entry_mode` 컬럼을 직접 조회해 검증했다.

~~현재 `ui_prefs.json`의 `entry_mode`는 `manual`인데... 사용자가 장중 대시보드에서
hybrid/manual을 실시간으로 직접 전환하고 있다는 뜻이다.~~

### DB 실측 — entry_mode 컬럼 직접 조회

```
entry_mode 분포 (최근 30일, 4,540건): manual 4,505건(99.2%), hybrid 35건(0.8%, 전부 07-03 하루)
```

**거의 전 기간 `manual` 그대로였다.** 모드 토글 이론은 기각.

### 진짜 원인 — `grade`(DB 저장값)와 `_final_grade`(게이트 판정 기준값)는 다른 변수다

```
main.py:5033   grade = decision["grade"]      ← 앙상블이 매긴 원본 등급 (체크리스트 실행 전)
main.py:5614   _final_grade = _cr["grade"]    ← 9항목 체크리스트 평가 결과로 교체
main.py:5862~  Degraded/ExecutionGovernor/MetaGate/ToxicityGate가 추가로 "X" 강등 가능
main.py:6150   mode_filter_passed = _final_grade in allowed_grades[entry_mode]
```

`decision["grade"]`는 **한 번도 `_final_grade`로 재대입되지 않는다.** 즉 DB의 `grade`
컬럼(1번 절·290차 리포트에서 "X:5848, C:1912"로 집계한 값)은 **체크리스트가 돌기 전
앙상블의 원본 등급**이고, `mode_filter_ok`는 **체크리스트+4종 오버라이드를 다 거친 뒤의
`_final_grade`**를 기준으로 판정한다 — 애초에 서로 다른 두 변수를 비교하고 있었다.

manual 모드는 A/B/C를 전부 허용하므로, `mode_filter_ok`는 사실상
**"`_final_grade`가 체크리스트+오버라이드를 통과해 X를 면했는가"**만 재는 지표가 된다.
그렇다면 1번 절의 `qty_ok`(역시 `_final_grade`/오버라이드에 의존)와 거의 같이 움직여야
하는데, 실측 교차표:

```
qty_ok=False & mode_filter_ok=False: 3,895건 (85.8%) — 같이 실패
qty_ok=True  & mode_filter_ok=True:    309건 (6.8%)  — 같이 통과
불일치:                                 336건 (7.4%)  — 포지션 상태 등 자잘한 타이밍차
```

**92.6% 일치** — `qty_ok`와 `mode_filter_ok`는 사실상 같은 사건(체크리스트+4종 오버라이드를
뚫고 `_final_grade`가 X를 면했는가)을 사이즈>0 / 등급 필터 통과라는 다른 각도에서 재는
**거의 중복된 지표**였다.

### 결론 (정정본)

`mode_filter_ok`도 `entry_mode` 설정 문제가 아니라 **1번 절과 동일한 근본원인**
(9항목 체크리스트 + Degraded Mode/ExecutionGovernor/MetaGate/ToxicityGate 캐스케이드)이다.
버그는 아니지만, "사용자 조작 신호라 재설계 제외"라는 최초 결론도 틀렸다 — qty_ok와
묶어서 같이 다뤄야 한다.

---

## 3. 부수 발견

1. **`entry_gate_json`은 2026-06-17부터만 존재**한다(그 이전 13일은 스냅샷 자체가 없음 —
   최근 배포에서 추가된 컬럼으로 추정). `gate_blocking_report.md`(290차)의 "30일 게이트
   집계"는 실제로는 최근 약 17일치(2026-06-17~07-03)만 반영된 것 — 리포트 캡션에
   이 사실을 명시할 필요 있음(다음 재실행 시 반영 권장).
2. **`decision["grade"]`가 `_final_grade`로 갱신되지 않는 것 자체가 코드 정리 후보**다 —
   같은 "등급"이라는 이름으로 서로 다른 두 시점의 값(체크리스트 전/후)이 DB 한 컬럼과
   실시간 게이트 판정에 각각 쓰이고 있어, 이번처럼 분석할 때 혼동을 유발한다. 이번
   조사 범위 밖이지만 §13 리팩토링 시 "저장용 등급"과 "판정용 등급"을 명시적으로
   분리(또는 통일)하는 것을 권장.
3. 이전에 남겼던 "grade='X'인데 mode_filter_ok=True 113건" 관찰은 이번 정정으로 설명된다 —
   `decision["grade"]`(원본, 이 경우 X)와 `_final_grade`(체크리스트 후, 이 경우 X가 아니었을
   수 있음)가 애초에 다른 변수이므로 발생 가능한 정상적인 불일치였다.

---

## §13(다중게이트 재설계) 우선순위에 대한 영향 (정정본)

- **qty_ok·mode_filter_ok 둘 다 제거/재정의 대상 아님** — 대신 **같은 근본원인의 두 얼굴**로
  묶어서 취급한다. 손볼 대상은 **9항목 체크리스트 + Degraded Mode·ExecutionGovernor·
  MetaGate·ToxicityGate 4종 오버라이드**이며, 이 4종은 기존 v9 설계안(§13)이 명시적으로
  다루지 않았던 항목이라 L3 소프트 게이트 점수화 범위에 반드시 포함해야 한다.
- **entry_mode(auto/hybrid/manual) 토글은 이번 병목과 무관**하다 — 재설계 우선순위에서 빠진다
  (최초 진단에서 잘못 포함시켰던 항목).
- **`grade` vs `_final_grade` 명명 정리**는 §13 리팩토링의 부수 과제로 등록.
- **gate_blocking_report.md의 "30일" 표현은 실제로 ~17일**임을 인지하고 해석할 것.

⚠️ 본 문서는 시스템 설계 프로세스를 돕기 위한 것이며, 수익률을 보장하거나 투자 자문을 제공하지 않습니다.
