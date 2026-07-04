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

## 2. mode_filter_ok — 버그 아님, 사용자가 실시간 조작하는 `entry_mode` 토글 그대로 반영

### 코드 경로

`main.py:6139-6150`: `entry_mode = self.dashboard.get_entry_mode()`(대시보드 UI 드롭다운,
`ui_prefs.json`에 영속화), `allowed_grades = {"auto":[A], "hybrid":[A,B], "manual":[A,B,C]}`,
`mode_filter_passed = _final_grade in allowed_grades[entry_mode]`.

### DB 실측 — grade='C' 신호의 mode_filter_ok 통과율, 날짜별

```
06-17: 27%   06-18: 17%   06-19: 7%   06-22: 31%   06-23: 41%   06-24: 17%
06-25: 19%   06-26: 31%   06-29: 48%   06-30: 0%    07-01: 54%   07-02: 58%   07-03: 48%
```

현재 `ui_prefs.json`의 `entry_mode`는 `manual`(C 허용)인데, manual이 계속 유지됐다면
C등급은 항상 통과해야 한다(100%). 그런데 날짜마다, **같은 날 안에서도** 들쭉날쭉하다 —
이는 사용자가 장중 대시보드에서 `hybrid`(C 차단)와 `manual`(C 허용)을 실시간으로
직접 전환하고 있다는 뜻이다. "자동 주축 + 수동 override" 설계 의도 그대로 작동 중.

### 결론

`mode_filter_ok`는 **사용자가 의도적으로 쓰는 실시간 컨트롤**이다. §13 재설계 대상에서
제외를 권장 — 손봐야 할 로직 결함이 아니라 운영자의 판단이 반영된 정상 신호다.

---

## 3. 부수 발견 2가지

1. **`entry_gate_json`은 2026-06-17부터만 존재**한다(그 이전 13일은 스냅샷 자체가 없음 —
   최근 배포에서 추가된 컬럼으로 추정). `gate_blocking_report.md`(290차)의 "30일 게이트
   집계"는 실제로는 최근 약 17일치(2026-06-17~07-03)만 반영된 것 — 리포트 캡션에
   이 사실을 명시할 필요 있음(다음 재실행 시 반영 권장).
2. `grade='X'`인데 스냅샷 시점 `mode_filter_ok=True`로 찍힌 행이 113건(전체 스냅샷의
   2.5%) 있다 — `_final_grade`가 mode_filter_ok 평가 시점(`main.py:6150`)과 최종
   `grade` 컬럼 저장 시점(`main.py:6363`) 사이에 한 번 더 하향 조정된다는 뜻. 영향은
   작지만(2.5%) 두 시점의 `_final_grade` 스냅샷이 어긋난다는 것 자체는 코드 정리 후보로
   남겨둔다(이번 조사 범위 밖).

---

## §13(다중게이트 재설계) 우선순위에 대한 영향

- **qty_ok는 제거/재정의 대상 아님** — 다만 그 뒤에 숨어있던 Degraded Mode·
  ExecutionGovernor·MetaGate·ToxicityGate 4종을 L3 소프트 게이트 점수 항목에
  명시적으로 포함시켜야 한다(기존 v9 설계안 §13은 Hurst·ATR·시가이격·체크리스트만
  다뤘음 — 범위 확대 필요).
- **mode_filter_ok는 재설계 대상에서 제외** — 사용자 조작 신호이므로 그대로 유지.
- **gate_blocking_report.md의 "30일" 표현은 실제로 ~17일**임을 인지하고 해석할 것.

⚠️ 본 문서는 시스템 설계 프로세스를 돕기 위한 것이며, 수익률을 보장하거나 투자 자문을 제공하지 않습니다.
