# SGD·GBM 레이블 구간·Threshold 파라미터 — 검토 주기·재설정 가이드

> 작성: 2026-07-03 (288차 세션 — SGD 호라이즌별 미학습 딥다이브 → P0/P1/P4 구현)
> 목적: 레이블 정의(HORIZON_THRESHOLDS·SIGMA_K_PER_HORIZON)가 조용히 레짐과 어긋나는 것을
> 정기적으로 잡아내기 위한 점검 절차. 이번 세션에서 **고정 threshold가 5주 만에 FLAT
> 18.6~25.5%까지 드리프트**한 것을 실측으로 확인하고 재보정한 경험이 원본 사례.

---

## 1. 배경 — 이 시스템에는 레이블 정의가 2개 존재한다

| 축 | 사용처 | 정의 방식 | 특성 |
|---|---|---|---|
| **A. 고정 threshold** | GBM 배치 학습 레이블 (`USE_FIXED_LABEL_THRESHOLD=True`) | `HORIZON_THRESHOLDS` 딕셔너리 (절대 수익률 %, 정적 값) | 사람이 주기적으로 재산출해야 함 — **레짐 변화에 자동 추종 안 함** |
| **B. rolling σ** | 실시간 예측 검증·SGD 온라인 학습 레이블 (`learning/prediction_buffer.py:333`) | `threshold = sigma_20봉 × SIGMA_K_PER_HORIZON[hz] × sqrt(h_min)` | 매분 20봉 윈도우로 σ 재계산 — **레짐 변화에 자연 추종** |

두 축이 분리된 이유(`config/settings.py:153-157` 주석): GBM 훈련 세트 내부에서 rolling σ를 쓰면 저변동성 날과 고변동성 날의 레이블 "크기 기준"이 달라져 **훈련셋 내부 드리프트**가 생긴다. 그래서 훈련은 고정값으로 일관성을 주고, 실전 검증은 그날그날 변동성에 맞춰 rolling σ를 쓴다.

**문제는 여기서 발생한다**: A축(고정값)은 아무도 안 건드리면 몇 주 지나서 변동성 레짐이 바뀌어도 그대로 남아있는다. B축(rolling σ)은 자연 추종하므로 A·B가 서서히 벌어진다 — GBM은 "이 정도면 UP"이라고 학습했는데, 실시간 채점은 다른 기준으로 "그건 FLAT이야"라고 판정하는 상황. 2026-07-03 실측으로 정확히 이 상태가 확인됨 (§6 참조).

---

## 2. 파라미터 지도

| 파라미터 | 파일:라인 | 역할 |
|---|---|---|
| `HORIZON_THRESHOLDS` | `config/settings.py:111-118` | GBM 학습 레이블 임계값 (고정, 호라이즌별 절대 수익률) |
| `HORIZON_THRESHOLDS_BASE` | `config/settings.py:122` | `HORIZON_THRESHOLDS`의 참조용 사본 (ThresholdRecalibrator가 drift 비교 기준으로 사용) |
| `SIGMA_K_PER_HORIZON` | `config/settings.py:139-146` | rolling σ 배수 k (호라이즌별) — `threshold = σ×k×√h_min` |
| `SIGMA_W` / `SIGMA_W_MIN` | `config/settings.py:151-152` | rolling σ 계산 윈도우(20봉) / 최소 유효 봉 수(5봉) |
| `USE_FIXED_LABEL_THRESHOLD` | `config/settings.py:163` | `True`=GBM 학습에 고정값 사용 (기본, 변경 금지 — 훈련셋 내부 드리프트 방지 근거는 §1) |
| `USE_ROLLING_SIGMA_THRESHOLD` | `config/settings.py:157` | `True`=실시간 검증에 rolling σ 사용 (기본) |
| `SGD_FULL_RESET_PENDING` | `config/settings.py:130` | `True`로 세팅 시 **다음 GBM 재학습 완료 때 1회** `online_learner.reset_full()` 실행 후 자동 `False` 복귀 |
| `_min_conf_sgd` | `main.py:6746` | SGD 온라인학습 진입 게이트 — 검증된 예측이라도 conf<0.52면 `learn()` 스킵 (P2-D) |
| `HZ_DEPLOY_POLICY` | `config/settings.py:97-104` | 호라이즌별 예측 저장(=학습기회) 빈도 제한 — `always`(1m)/`bar_only`(3m·5m)/`bar_plus1`(10m·15m)/`filter_only`(30m) |
| `_sgd_learn_last_ts` | `main.py:579` | [P1, 288차] 호라이즌별 자기 봉 길이(N분) 미만 간격 학습 dedup — 같은 봉 재탕 학습 방지 |
| `LOOKBACK_TRADING_DAYS` | `learning/threshold_recalibrator.py:41` | [P4, 288차] 자동 재보정 모니터가 참조하는 최근 거래일 수 (21) |

관련 실행 스크립트:

| 스크립트 | 용도 |
|---|---|
| `scripts/optimize_sigma_k.py` | rolling σ의 `SIGMA_K_PER_HORIZON` 탐색 (`--weeks N`, `--apply`로 settings.py 자동 갱신) |
| `learning/threshold_recalibrator.py` (`ThresholdRecalibrator`) | 고정 `HORIZON_THRESHOLDS`용 자동 주간 모니터 — **자동 반영 안 함, 권고만** |

---

## 3. 정기 점검 주기

```
매주 금요일 15:40 (자동, main.py:7827)
  → ThresholdRecalibrator.run() 자동 실행 → threshold_monitor.db 기록 + 경보 로그
  → 사람이 로그/DB 확인만 하면 됨 (반영은 수동)

매월 1주차 (수동, 권장)
  → §5 절차로 HORIZON_THRESHOLDS·SIGMA_K_PER_HORIZON 동시 재보정 검토
  → 자동 모니터가 WATCHLIST 이상을 3주 연속 띄우면 대기 없이 즉시 실행 (§4 트리거 참조)

분기 1회 (수동)
  → HZ_DEPLOY_POLICY·_min_conf_sgd 재검토 (§7) — 이건 레이블 "크기"가 아니라
    "학습 기회 빈도/품질 게이트"라 변동성보다 느리게 변하는 구조적 파라미터
```

---

## 4. 재보정 트리거 조건 (아래 중 하나라도 해당하면 §5 실행)

| 조건 | 확인 방법 |
|---|---|
| `threshold_monitor.db`에 동일 호라이즌 **"UPDATE" 2주 연속** | §6-A SQL |
| 최근 1개월 실측 FLAT 비율이 목표 34%에서 **±8%p 이상** 이탈 | §6-B 스크립트 |
| 대시보드 SGD 카드가 여러 호라이즌 동시에 "미학습 0건"으로 장시간 고정 | 육안 (다만 §의 근본 원인은 conf 게이트·dedup 등 다른 요인일 수 있음 — 먼저 LEARNING 로그로 conf 분포부터 확인) |
| GBM `gbm_{hz}_acc.txt` 정확도가 전 호라이즌 동시에 급락 | `model/horizons/gbm_*_acc.txt` |
| 옵션시장 급변·연휴 복귀 등 **알려진 변동성 레짐 전환 이벤트** 직후 | 뉴스/일정 기반 판단 |

**WATCHLIST**는 정보성(관찰만), **UPDATE**는 실제 δ≥15% 또는 FLAT drift≥6%p — 재보정을 미루지 말 것.

---

## 5. 재보정 절차

### 5-A. 고정 `HORIZON_THRESHOLDS` 재보정 (GBM 학습 레이블)

세션 내 임시 스크립트로 실행했던 방식(재사용 가능하도록 정리):

```python
import sqlite3, datetime

HZ_MIN = {"1m":1,"3m":3,"5m":5,"10m":10,"15m":15,"30m":30}
N_TRADING_DAYS = 21          # 직전 재보정과 동일 윈도우 유지 (비교 가능하도록)

con = sqlite3.connect("data/db/raw_data.db")
cur = con.cursor()
cur.execute("SELECT DISTINCT substr(ts,1,10) d FROM raw_candles ORDER BY d DESC")
all_days = [r[0] for r in cur.fetchall()]
trading_days = all_days[1:1+N_TRADING_DAYS]      # [0]=오늘(장중 미완료)은 제외
since = min(trading_days)

cur.execute("SELECT ts, close FROM raw_candles WHERE ts >= ? ORDER BY ts", (since+" 00:00:00",))
closes = {ts: c for ts, c in cur.fetchall()}

def fut_ret(ts, h_min):
    t0 = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    t1 = t0 + datetime.timedelta(minutes=h_min)
    if t1.date() != t0.date() or t1.hour > 15 or (t1.hour == 15 and t1.minute > 35):
        return None                              # 세션 경계(장마감 15:35) 넘어가면 제외
    c0, c1 = closes.get(ts), closes.get(t1.strftime("%Y-%m-%d %H:%M:%S"))
    if c0 is None or c1 is None or c0 <= 0:
        return None
    return (c1 - c0) / c0

for h, hm in HZ_MIN.items():
    rets = [r for ts in sorted(closes) if ts >= since+" 00:00:00"
            for r in [fut_ret(ts, hm)] if r is not None]
    n = len(rets)
    sr = sorted(rets)
    p33, p67 = sr[int(n*0.33)], sr[int(n*0.67)]
    recalc_sym = (abs(p33) + p67) / 2.0
    up = sum(1 for r in rets if r > recalc_sym) / n
    dn = sum(1 for r in rets if r < -recalc_sym) / n
    print(f"{h}: n={n} thr={recalc_sym*100:.4f}%  UP={up:.1%} FL={1-up-dn:.1%} DN={dn:.1%}")
```

**반영**: 출력된 값을 `config/settings.py:111-118` `HORIZON_THRESHOLDS`에 직접 기입. 반드시:
1. 변경 사유·이전값·변화율을 주석으로 남길 것 (기존 컨벤션 준수)
2. `HORIZON_THRESHOLDS_BASE`는 `dict(HORIZON_THRESHOLDS)`로 자동 파생되므로 별도 수정 불필요
3. **`SGD_FULL_RESET_PENDING = True`로 설정** (`config/settings.py:130`) — 레이블 체계가 바뀌므로 다음 GBM 재학습 때 SGD 전체 리셋 필요 (189차 선례)

### 5-B. rolling σ `SIGMA_K_PER_HORIZON` 재보정 (실시간·SGD 레이블)

```bash
python scripts/optimize_sigma_k.py --weeks 5      # 21거래일 ≈ 5주(달력 기준, 여유있게)
python scripts/optimize_sigma_k.py --weeks 5 --apply   # 검토 후 자동 반영
```

- `--apply`는 `settings.py`의 `SIGMA_K_PER_HORIZON` 블록을 정규식으로 찾아 교체한다 (`scripts/optimize_sigma_k.py:167-193`) — 실행 전 git diff로 결과를 반드시 검토할 것.
- 2026-07-03 실측 경험: 대부분 호라이즌은 몇 주가 지나도 기존 k가 그대로 최적으로 나옴(자연 추종 덕분). **변화가 있는 호라이즌만 선별 반영**하고, 나머지는 굳이 건드리지 않는 편이 안전(불필요한 SGD 재적응 최소화).

### 5-C. 두 축을 반드시 같은 윈도우로

A(고정)와 B(rolling)를 다른 시기에, 다른 윈도우 길이로 재보정하면 "정의 통일"의 의미가 없어진다. **같은 날, 같은 거래일 수(기본 21일)로 A·B를 함께 재보정**하는 것을 원칙으로 한다.

---

## 6. 자동 모니터(`ThresholdRecalibrator`) 해석 가이드

### 6-A. 최근 결과 조회

```python
import sqlite3
con = sqlite3.connect("data/db/threshold_monitor.db")
cur = con.cursor()
cur.execute("""SELECT date, horizon, current_base, recalc_sym, flat_actual,
                      flat_drift, threshold_delta, alert_level, n_bars
               FROM threshold_log ORDER BY date DESC, horizon LIMIT 30""")
for r in cur.fetchall():
    print(r)
```

### 6-B. 경보 수준

| alert_level | 조건 | 의미 | 조치 |
|---|---|---|---|
| `CLEAR` | 모두 정상 | 그대로 유지 | 없음 |
| `WATCHLIST` | \|FLAT drift\|≥6%p 또는 ATR ratio 대역 이탈 | 관찰 필요 | 다음 주 재확인, 2주 연속이면 §5 실행 |
| `UPDATE` | \|threshold δ\|≥15% | 재보정 강력 권고 | **자동 반영 안 됨** — §5 수동 실행 |

### 6-C. [중요] 2026-07-03 이전 데이터 해석 시 주의

`_load_returns()`가 **2026-07-03 이전에는 `raw_candles` 전체(2025-08-19~, 11개월치) 평균**으로 재산출했다. 이 기간엔 최근 레짐(변동성 확대)이 11개월 평균에 희석되어, **실제로는 threshold를 올려야 하는 상황에서 오히려 "낮춰라"는 반대 방향 UPDATE 경보**가 6/12·6/19·6/26 3주 연속 발생한 이력이 있다(`threshold_monitor.db` 확인 가능). 288차에서 `LOOKBACK_TRADING_DAYS=21`로 윈도우를 제한해 수정했으므로 **2026-07-03 이후 기록은 신뢰 가능**하지만, 과거(7/3 이전) 로그를 참조할 때는 방향이 뒤집혀 있었을 수 있음을 감안할 것.

---

## 7. 재보정과 별개로 관리해야 하는 SGD 학습 게이트 3종

레이블 "크기"(threshold) 문제와 별개로, SGD가 학습 신호를 충분히 받는지는 아래 3개 게이트가 결정한다. 이들은 변동성 레짐보다 느리게 변하므로 분기 1회 정도로 충분:

1. **`_min_conf_sgd=0.52`** (`main.py:6746`) — 검증된 예측의 confidence가 이 값 미만이면 학습에서 제외. 호라이즌별 실측 confidence 분포(p50/p90/max)가 이 값에 못 미치면 해당 호라이즌은 사실상 영구 미학습 상태가 된다. 점검: `logs/{날짜}_LEARNING.log`에서 `✓|✗ {hz} 예측 (적중|실패) (conf=` 라인을 파싱해 호라이즌별 conf 분포 확인.
2. **`HZ_DEPLOY_POLICY`** (`config/settings.py:97-104`) — `bar_only`/`bar_plus1` 호라이즌(3m·5m·10m·15m)은 애초에 저장(=학습 기회) 빈도가 1m·30m보다 훨씬 낮다. 이 정책은 앙상블 신선도 보호가 목적이라 함부로 완화하면 안 되지만, "왜 학습이 안 되나"를 진단할 때 반드시 1차로 확인해야 하는 항목.
3. **`_sgd_learn_last_ts` dedup** (`main.py:579`, 288차 P1) — 호라이즌 자기 봉 길이 미만 간격이면 학습을 건너뛴다. 정상 동작이며 `_horizon_counts`(대시보드 "누적 N건")가 이제 "독립 표본 수"를 의미하게 됐다는 점을 오인하지 말 것 — 예전 기준(매분 학습)보다 절대 건수가 줄어드는 게 정상이다.

---

## 8. 재보정 후 체크리스트

```
[ ] HORIZON_THRESHOLDS / SIGMA_K_PER_HORIZON 변경 주석에 이전값·근거·변화율 기록
[ ] SGD_FULL_RESET_PENDING = True 로 세팅 (threshold 변경 시에만, k 조정만이면 불필요)
[ ] git diff로 config/settings.py 변경분 재검토 (특히 --apply 스크립트 사용 시)
[ ] python -m py_compile config/settings.py 로 문법 확인
[ ] 다음 GBM 재학습 로그에서 "[SGD] threshold 교체 후 완전 리셋 완료" 확인
[ ] 재보정 익일 대시보드 SGD 카드 육안 확인 — 학습됨/리셋됨 비율이 급격히 나빠지지 않는지
[ ] dev_memory/SESSION_LOG.md에 이번 재보정 기록 (차수·날짜·이전값→신값·근거 데이터 기간)
```

---

## 9. 이력 — 2026-07-03 (288차) 재보정 기록

| 항목 | 이전 | 변경 후 | 근거 |
|---|---|---|---|
| `HORIZON_THRESHOLDS` (전 호라이즌) | 2026-05-30 재보정값 | 2026-07-03 재보정 (+40~+85%) | 최근 21거래일(6/4~7/2) FLAT 18.6~25.5% 확인, 33/34/33 재정렬 |
| `SIGMA_K_PER_HORIZON["10m"]` | 0.38 | 0.41 | 같은 윈도우 재탐색, FL 31.0%→33.0% 개선 |
| `SGD_FULL_RESET_PENDING` | False | True (1회성) | threshold 교체 후 SGD 재적응 필요 |
| `ThresholdRecalibrator.LOOKBACK_TRADING_DAYS` | 없음(전체 이력 사용) | 21 | 전체 이력 평균 사용 시 최근 레짐 희석 → 반대 방향 오경보 확인 (6/12·6/19·6/26 3주 연속) |
| `main.py:3100` GBM 재학습 완료 시 `online_learner.reset_daily()` | 매 재학습(하루 최대 23회)마다 호출 | 호출 제거, EOD 1일 1회만 | SGD acc_buf가 매번 초기화되어 `_MIN_SAMPLES=15` 문턱 영구 미달 (영구 콜드스타트 루프) |
| SGD 학습 dedup (`_sgd_learn_last_ts`) | 없음(매분 검증마다 학습) | 호라이즌 자기 봉 길이 미만 간격 스킵 | 30m 하루 48건 학습 중 대부분이 같은 30분봉 재탕(29/30 중복) → 단방향 붕괴 유발 |

관련 세션 로그: `dev_memory/SESSION_LOG.md` 288차 항목 참조.
