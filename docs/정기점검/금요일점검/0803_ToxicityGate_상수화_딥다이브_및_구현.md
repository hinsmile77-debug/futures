# ToxicityGate 상수화 딥다이브 + P0 재보정·P1 섀도 구현

- 작성: 2026-08-03 (MW0601, 419차)
- 발단: `strategy/risk/toxicity_gate.py:71`의 reduce 밴드 `size_multiplier`가 고정 상수로
  출력되는 흐름을 딥다이브하라는 지시
- 커밋: `2268913` [MW0601] 419차 — 9 files, +838/-6
- 결론: **그 상수는 표면이었다.** 아래에 더 큰 죽은 상수가 하나 더 있었고,
  그것이 게이트 전체를 상시 발동 상태로 만들고 있었다

---

## 0. 요약

| 발견 | 내용 | 조치 |
|---|---|---|
| ① | `tox_size`는 문자 그대로 상수 — 116건 전수 `distinct=[0.7]` | P1 섀도 |
| ② | reduce 밴드가 전 분봉의 **76.4%**, pass는 **0.27%** — "게이트"가 아니라 상시 헤어컷 | P0 |
| ③ | 근본원인: `cancel_stress`가 **100% 포화**, score에 상수 +0.20을 더하는 죽은 항 | **P0 실적용** |
| ④ | JointGateBlock은 tox축 정보가 0이라 meta 단일 임계와 **동치**(116/116) | P3 보류 |
| ⑤ | 사이징 체인의 8단 `max(1,round())`가 배수를 다시 뭉갬 | P2 보류 |
| ⑥ | 그럼에도 **밴드 내부에 유의한 단조 정보가 실재** (rho=+0.319, t=13.48) | P1 섀도 |

이번에 한 것은 **P0(실적용) + P1(섀도 전용)** 이고, P2·P3은 근거를 남기고 보류했다.

---

## 1. 흐름 딥다이브

### 1-1. 호출 경로

```
ToxicityCalculator.update()      features/technical/toxicity.py:37
   └ 5개 stress → 가중합 → toxicity_score / _ma / 성분값
        ↓ (raw_features JSON + features dict)
ToxicityGate.evaluate()          strategy/risk/toxicity_gate.py:38
   └ score/ma/spread_ticks → action + size_multiplier
        ↓ decision["toxicity_gate"]
main.py:7025   _qty_display = max(1, int(round(_qty_display * _tox_size)))
main.py:8106   _joint_mult  = _meta_size * _tox_size   → <0.50 이면 진입 차단
```

게이트는 `main.py:349`에서 생성되는데 `block_threshold`/`reduce_threshold`는
**settings에서 주입되지 않는다** — 코드 기본값 0.45/0.28 하드코딩이고, config에는
spread block 관련 2개만 있었다.

### 1-2. 발견 ① — 0.7은 문자 그대로 상수다

`joint_gate_shadow` 116건 전수 조회:

```
distinct tox_size = [0.7]      ← 116/116, 예외 0건
```

`docs/Ref/jointfateBlock.txt`와 `config/settings.py:1234`가 제기했던 "구조적 의문"은
의문이 아니라 **확정**이다.

### 1-3. 발견 ② — reduce 밴드가 "거의 전부"다

라이브 2026-07-24~07-31(380차 재보정 배포 이후, n=2,229분봉):

| 밴드 | 380차 설계목표 | **실측** |
|---|---|---|
| block | 0.7% | **23.3%** |
| reduce | 11.8% | **76.4%** |
| pass | 87.5% | **0.27%** |

일자별로도 일관됐다(pass가 0.0%인 날 5일). `[ToxicityGate]` 로그 10거래일 실측도
reduce 731건 / block 77건.

> **즉 `0.7`은 "독성 구간 축소"가 아니라 상시 적용되는 전역 사이즈 헤어컷이었다.**

### 1-4. 발견 ③ — 근본원인: cancel_stress 100% 포화 (P0)

성분 분해(`toxicity_*_stress` 저장값, 라이브 07-24~07-31):

| 성분 | 가중 | p50 | 포화(=1.0)율 | 0인 비율 | p50 가중기여 |
|---|---|---|---|---|---|
| atr_stress | 0.25 | 0.0000 | 0.6% | 56.4% | 0.0000 |
| spread_stress | 0.20 | 0.4209 | 4.5% | 3.1% | 0.0842 |
| flow_stress | 0.20 | 0.2182 | 0.6% | 0.1% | 0.0437 |
| queue_stress | 0.15 | 0.0000 | 0.8% | 73.9% | 0.0000 |
| **cancel_stress** | 0.20 | **1.0000** | **100.0%** | 0.0% | **0.2000** |

`cancel_churn_ratio` 실측 p50=**0.2649** 인데 ceiling이 **0.08** — 3.3배 초과라
**전 분봉이 1.0으로 포화**했다.

> 중앙값 score 0.3475 중 **0.20(58%)이 죽은 상수**이고, 실제 변동은
> spread_stress·flow_stress만 만들고 있었다. 임계선 전체가 +0.20 오프셋된
> 좌표계 위에 놓인 셈이다.

**이건 380차가 스스로 예고한 미완 작업이다.** `features/technical/toxicity.py`에
*"ceiling=0.08은 신규 피처라 과거 데이터로 재현검증 불가한 잠정치 — 라이브 섀도
관찰 몇 주 후 재보정 필요"* 라고 적혀 있었고, 그 재보정이 실행되지 않았다.

원인 구조까지 보면 더 분명하다 — 380차 백테스트는 07-14~23 데이터로 임계값
(0.45/0.28)을 골랐는데 **그 구간엔 `cancel_churn_ratio`가 아예 없었다**(신규 피처).
즉 임계값은 cancel_stress를 뺀 분포로 정해졌는데 라이브에선 그 항이 상수 +0.20으로
들어왔다.

### 1-5. 발견 ④ — JointGateBlock은 meta 단일 임계와 동치

`tox_size ≡ 0.7`이므로 `joint_mult < 0.50 ⟺ meta_size < 0.7143`. 실측:

```
meta_size < 0.7143  →  116/116 (100.0%)
```

2축 조건이 아니라 **meta 단일 임계**였다. 덤으로 `meta_size`도
**73/116(62.9%)이 정확히 0.500** 인데, 원인은 `learning/meta_confidence.py:264`가
conf<0.5에서 `size_mult=0.0`을 내고 `strategy/entry/meta_gate.py:206`의
`learned["size_multiplier"] or 0.5`가 falsy로 잡아 0.5로 **승격**시키기 때문이다
(약한 신호를 키우는 방향 — 의도와 반대).

→ `joint_mult`은 다수 케이스에서 `0.5 × 0.7 = 0.35` **이중 상수**다.

### 1-6. 발견 ⑤ — 양자화 체인이 배수를 다시 뭉갠다

`main.py`에 `max(1, int(round(q*m)))`가 **8단 연쇄**
(6974·6980·6993·7006·7026·7062·7076·7200)로 걸려 있고 각 단계가 독립 반올림한다.
`[SizerMatch]` 로그 실측:

```
sizer=3 → actual=1  (43건)      sizer=5 → actual=1  (5건)
sizer=2 → actual=1  (30건)      sizer=6 → actual=2  (2건)
sizer=4 → actual=1  (16건)
```

`×0.7`의 실효 절감률이 유입 수량에 따라 **0%(q=1) / 50%(q=2) / 33%(q=3) / 25%(q=4)**
로 비단조다. `sizer=2→1` 30건에서는 tox가 **아무 일도 하지 않았다**(meta가 이미 1로 만듦).

---

## 2. 그럼에도 버려지는 정보는 실재한다 (발견 ⑥)

상수화를 고칠 가치가 있는지 검증했다. **reduce 밴드 내부만** (n=1,614, 07-24~07-31):

| 5분위 | score 범위 | 15m 실현레인지(pt) | 향후 15m 평균스프레드(틱) |
|---|---|---|---|
| Q1 | 0.200~0.294 | 9.52 | 2.8 |
| Q2 | 0.294~0.321 | 10.66 | 3.1 |
| Q3 | 0.321~0.346 | 11.14 | 3.4 |
| Q4 | 0.347~0.382 | 12.14 | 3.4 |
| Q5 | 0.382~0.449 | **13.70** | **3.8** |

```
밴드내 Spearman(score, 향후 스프레드) rho=+0.319  t=13.48
밴드내 Spearman(score, 15m 레인지)    rho=+0.260  t=10.81
```

완전 단조이고 강하게 유의하다. **밴드 전체를 0.7 하나로 뭉개는 것은 이 정보를
전량 폐기하는 것이다.**

> ⚠ **정직한 단서**: ATR로 정규화하면 레인지 상관은 **rho=-0.08로 소멸**한다.
> 레인지 정보는 상당 부분 "변동성 수준"이고 ATR에 이미 들어 있다.
> 반면 **스프레드 관계는 정규화 대상이 아니며 살아남는다** — 연속화의 근거는
> 레인지가 아니라 **스프레드(집행비용) 축**으로 잡아야 한다.

---

## 3. 구현

### 3-1. P0 — cancel_stress ceiling 재보정 (**유일한 라이브 동작 변경**)

```python
# config/settings.py
TOXICITY_CANCEL_CHURN_CEILING = 0.42   # 실측 p99

# features/technical/toxicity.py:66
cancel_stress = min(abs(float(cancel_churn_ratio)) / self.cancel_churn_ceiling, 1.0)
```

`cancel_churn_ratio` 실측: p90=0.3412 / p95=0.3675 / **p99=0.4241** / max=0.5121.
380차가 다른 4개 성분에 쓴 **"p90~p99 실측 기준" 관례를 그대로** 따랐다.

**재생 검증** — 실제 `ToxicityCalculator`에 라이브 원입력을 다시 흘려보냈다.
먼저 **구값 재생이 저장된 실측과 일치**하는지 확인해 재생 경로 신뢰성을 세운 뒤 신값을 쟀다:

| ceiling | score p50 | block | reduce | pass | cancel포화 |
|---|---|---|---|---|---|
| 0.08 (구값) | 0.3475 | 23.5% | 76.4% | 0.2% | 100.0% |
| **0.42 (419차)** | 0.2760 | **8.6%** | 73.7% | **17.7%** | **1.2%** |
| *(참고) 저장된 실측* | *0.3475* | *23.3%* | *76.4%* | *0.27%* | *100.0%* |

**임계값(block 0.45 / reduce 0.28)과 나머지 4개 성분·가중치는 일절 건드리지 않았다.**
임계값 재선정은 재보정 후 이동한 분포를 라이브로 관찰한 뒤 결정할 사안이라
`[30]` 채널로 사전등록했다.

### 3-2. P1 — reduce 밴드 연속 배수 (**섀도 전용, 실배수 무변경**)

```python
# strategy/risk/toxicity_gate.py
def _reduce_mult_shadow(self, score, score_ma):
    span = self.block_threshold - self.reduce_threshold
    pos  = max(score, score_ma)          # 밴드 진입이 OR 조건이므로 큰 쪽
    t    = (clip(pos, lo, hi) - self.reduce_threshold) / span
    return round(hi_mult + (lo_mult - hi_mult) * t, 4)
```

- `size_multiplier`(실배수)는 **상수 0.7 그대로** — 실거래 사이징 무변경
- `size_multiplier_shadow` 키로 병기만 한다 (block=0.0 / pass=1.0은 실배수와 동일)
- 밴드 내 위치를 `max(score, score_ma)`로 잡는 이유: reduce 진입 조건이 둘의 OR이라
  ma로만 진입한 분봉을 score 기준으로 보간하면 밴드 하단에 잘못 붙는다

**앵커는 노출 중립으로 골랐다** (`HI=0.90` @reduce_thr, `LO=0.45` @block_thr):

| 앵커 (m@0.28, m@0.45) | 평균배수 | 현행 0.70 대비 |
|---|---|---|
| (1.00, 0.55) | 0.7932 | +13.3% |
| (0.95, 0.50) | 0.7432 | +6.2% |
| **(0.90, 0.45)** | **0.6932** | **-1.0%** ← 채택 |
| (0.85, 0.40) | 0.6432 | -8.1% |

> **이게 설계의 핵심이다.** 총 노출이 함께 움직이면 나중에 손익이 바뀌었을 때
> 그게 *등급화* 덕인지 *노출 증가* 탓인지 분리할 수 없다. 중립 앵커로 가면
> 변한 변수는 "배수의 분산" 하나뿐이라 인과 귀속이 가능하다.

### 3-3. 섀도 기록 — `toxicity_reduce_shadow` 테이블

`exec_1m_shadow`와 동일 계열(실체결 진입에 태그만 붙임)이라 counterfactual 가격
시뮬레이션이 불필요하다 — `ts`로 `trades.entry_ts` 조인.

기록 컬럼: `tox_size_applied`(0.7) / `tox_size_shadow`(연속) /
`qty_before_tox` / `qty_after_applied` / `qty_after_shadow` / `qty_entered`

> ⚠ `qty_after_*`는 **tox 스테이지 국소값**이다 — 하류(L2·Hurst·Degraded·상한)를
> 재시뮬레이션하지 않는다. 두 값이 같으면 최종 수량도 같지만(입력 동일),
> 다르다고 최종 수량이 반드시 달라지는 것은 아니다.

### 3-4. 하지 않은 것

| | 내용 | 왜 보류했나 |
|---|---|---|
| **P2** | 양자화 체인 8단 → 단일 라운딩 | 사이징 축 전체를 건드려 CLAUDE.md 실전전환기준 ⑧ 미해제 상태에선 별도 승인 대상. 단 **P1은 P2 없이는 반올림에 대부분 흡수**돼 둘은 사실상 한 세트 |
| **P3** | JointGateBlock 임계 0.50 재선정 + meta falsy 폴백 수정 | `joint_gate_shadow`가 현재 **PASS(존치)** — 116건 resolved, 누적 hyp_pnl **-13.16pt**, TP1 도달 69.8%로 차단이 실제로 손실을 회피 중. 완화를 서두를 근거가 없다 |
| — | 임계값(0.45/0.28) 재선정 | `[30]` 표본 축적 전엔 금지. 전 채널 왕복비용·판정에 영향을 주므로 §3 원칙대로 주간회의 결정 + DECISION_LOG 기록이 선행돼야 한다 |

---

## 4. 사전등록 캠페인 채널 2종

합격선을 **배포 전에** 확정했다(§9 사전등록 원칙).

### [30] `toxicity_recalib_watch` — P0 결과 감시

| | |
|---|---|
| **PASS** | pass ∈ [15%, 92%] ∧ block ≤ 12% ∧ cancel포화 ≤ 30% |
| **FAIL** | 위를 벗어남 → 임계값 재선정을 **주간회의 안건으로** (자동 변경 금지) |
| 표본 | `min_bars=1500` (약 4거래일) 미달 시 판정 보류 |
| 기준일 | `effective_date=2026-08-03` 이후 분봉만, 백필 행 제외(418차) |

> ⚠ 재생 기준으론 세 조건 다 통과(17.7% / 8.6% / 1.2%)하나 **pass 하한 15%까지
> 여유가 2.7%p뿐**이다. 라이브가 그 아래로 내려가면 FAIL인데, 그건 오탐이 아니라
> **재생과 라이브가 다르다는 의미 있는 신호**다. 사후에 하한을 낮추지 말 것.

### [31] `toxicity_reduce_mult_shadow` — P1 실효성 판정

이 채널의 1차 질문은 손익이 아니라 **실효성**이다.

| | |
|---|---|
| **PASS** | 수량 상이 < 20% → "양자화에 흡수되니 **현행 상수 유지**" |
| **FAIL** | 수량 상이 ≥ 20% → 실적용 검토 (단 앵커 재도출 + P2 동반 안건화) |
| 표본 | `min_samples=20` |

> **PASS가 "좋다"는 뜻이 아니다.** 상수 0.7이 정보를 폐기하는 것은 §2에서 실측으로
> 확정됐다. 다만 사이징 체인이 8단 양자화하고 실체결이 1~2계약에 묶여 있어 그 정보를
> 살릴 여지 자체가 없을 수 있고, 그렇다면 **복잡도만 늘리는 변경이므로 하지 않는 것이 맞다.**

> ⚠ 현행 앵커는 **재보정 전** 분포로 도출됐다 — `[30]`이 새 분포를 확정하면
> 반드시 재도출할 것. 리포트 상세절의 `shadow_mult_mean`이 그 감시 지표다
> (0.70에서 크게 벗어나면 노출 중립 설계가 깨진 것).

---

## 5. 변경 파일

| 파일 | 내용 |
|---|---|
| `features/technical/toxicity.py` | ceiling 파라미터화(기본 0.42) + 근거 주석 |
| `features/feature_builder.py` | config 주입 |
| `strategy/risk/toxicity_gate.py` | `_reduce_mult_shadow()` + 3개 분기 병기 (**실배수 무변경**) |
| `config/settings.py` | `TOXICITY_CANCEL_CHURN_CEILING`, `..._SHADOW_HI/LO`, 캠페인 채널 2종 |
| `utils/db_utils.py` | `toxicity_reduce_shadow` 테이블 |
| `main.py` | `_log_toxicity_reduce_shadow()` + 진입 2경로 배선 |
| `scripts/generate_validation_campaign_report.py` | `[30]`/`[31]` 평가함수·요약행·상세절 |

---

## 6. 검증

전부 **py37_32(실제 런타임)** 에서 실행:

- 성분 역산 오차 **max=6e-07** — 저장 성분값으로 저장 score가 재현됨(역산 신뢰 확보)
- 실제 `ToxicityCalculator` 신구 재생 대조 — 구값 재생이 저장 실측과 일치
- 게이트 스모크 — **reduce 실배수가 전 구간 0.7 불변**을 assert로 확인
- 섀도 기록→평가 왕복 (합성 21건, FAIL 경로 포함)
- 1200행 청크 조인 (SQLite 999 변수 한계 대응)
- 전체 리포트 빌드 + `[30]`/`[31]` 렌더링 확인
- `pytest tests/` — **10 passed**

### 배선 직후 NO-DATA 오탐 방지

신설 채널은 배선 당일 정의상 표본이 0이라, 그대로 두면 첫 주 리포트가
🔴 NO-DATA("계측 점검 필요")를 띄운다. 5일 유예를 넣어 그 안에서는
⏳ INSUFFICIENT로만 표시한다 — 유예가 지나도 0건이면 그때는 진짜 배선 문제다.

### ⚠ 한계

**전부 오프라인 검증이다.** 다음은 미검증:

- P0가 라이브에서 실제로 밴드를 옮기는지
- `_log_toxicity_reduce_shadow`가 실거래에서 기록되는지 (417차 `entry_qty`와 같은 성격)
- 08-07 EOD 체인에서 `[30]`/`[31]`이 생성되는지 (수동 실행만 검증)

확인 쿼리는 `dev_memory/NEXT_TODO.md` 419차 후속 항목에 등록했다.

---

## 7. 주의사항 (인용 시 함께 읽을 것)

1. **P0은 진입을 늘리는 방향이다** (block 23.5%→8.6%, pass 0.2%→17.7%).
   CLAUDE.md 실전전환기준 ⑧("현행 흑자는 사이즈가 우발적으로 1~2계약에 묶인 결과")과
   함께 읽어야 한다.

2. **`[30]` pass 하한 여유는 2.7%p뿐** — 라이브가 하회해도 사후에 하한을 낮추지 말 것
   (사전등록 훼손).

3. **`[31]`의 PASS는 "현행 유지" 판정이지 "문제 없음"이 아니다** — 상수가 정보를
   폐기한다는 사실 자체는 변하지 않는다.

4. **P1 연속화는 P2 없이 단독으로 효과가 거의 없다** — `[31]` FAIL 시 둘을 함께
   올릴 것.

---

## 8. 근거 문서

- `dev_memory/DECISION_LOG.md` 2026-08-03 (MW0601 419차) — 전체 실측·결정 기록
- `dev_memory/NEXT_TODO.md` 419차 후속 — 라이브 검증 항목 + "하지 않기로 한 것"
- `docs/Ref/jointfateBlock.txt` — 07-14 최초 문제 제기(이번에 확정됨)
- `config/settings.py` `VALIDATION_CAMPAIGN["toxicity_recalib_watch"]` /
  `["toxicity_reduce_mult_shadow"]` — 사전등록 합격선
