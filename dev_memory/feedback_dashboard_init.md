# feedback: PredictionPanel dict 초기화 순서 — 3차 재발 방지

> 커밋 이력: d1f1cc3 → 8e353bb → 992557c → 2026-04-28 최종 수정

## 패턴 (재발 원인)

`__init__`에서 `self._build()` 호출 **이후**에 `self._hz_labels = {}` 등을 선언하면
`_build()`가 채운 값을 즉시 덮어쓴다. IDE가 자동으로 instance var 선언 블록을
`_build()` 뒤로 재정렬할 때마다 재발한다.

```python
# 잘못된 패턴 (IDE 재정렬 후 재발 형태)
def __init__(self):
    super().__init__()
    self._build()          # ← 여기서 dict 채움
    self._hz_labels = {}   # ← 즉시 빈 dict로 덮어씀 — BUG
```

## 올바른 패턴

```python
def __init__(self):
    super().__init__()
    self._hz_labels = {}   # 선언 먼저
    self._param_bars = {}
    self._param_vals = {}
    self._build()          # 그 다음 _build()가 채움
```

`_build()` 내부에 dict 재초기화 코드 없어야 한다 (혼용 금지).

**Why:** 이 버그가 발생하면 호라이즌 6개 카드와 SHAP 바가 영구적으로 "—"에 고착된다.
lbl_price/lbl_signal은 dict 우회로 접근하므로 정상 표시 → "부분 동작"처럼 보여 발견이 늦다.

**How to apply:** PredictionPanel 수정 시 반드시 dict 선언이 `_build()` 앞에 있는지 확인.
IDE 자동 포맷 후에도 순서 재확인.

## 시뮬레이션 타이머 조건부 시작

```python
# MireukDashboard.__init__
self._sim_timer = None
if kiwoom is None:           # ← kiwoom 미연결 시에만 시뮬레이션
    self._start_sim_timer()
```

`update_price()` 첫 호출 시 `_stop_sim_timer()` 자동 호출로 실제 데이터로 전환.

**Why:** 시뮬레이션 타이머가 항상 돌면 실제 API 데이터가 들어와도 3초마다 랜덤값으로 덮어쓴다.
로그에 "1분봉 수신"이 3초마다 찍히는 이상 현상도 동시 해결.
