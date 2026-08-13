# 증거 지도 — 미륵이

> **2026-08-12 MW0602 실측 확인됨.** 아래 표는 `--discover` 결과로 채운 것이다.
> 로그 구성이 바뀌면 `--discover` 를 다시 돌려 이 표와 `config/dailycheck_targets.json` 을 갱신하라.

`{d}` = `YYYYMMDD`, `{D}` = `YYYY-MM-DD` (KST)

---

## 1. 로그 — 실측 레이아웃

미륵이는 **채널별로 파일을 나눈다**(메시아는 프로세스별로 나눈다). 날짜가 **앞에** 온다.

| 파일 | 채널 | 무엇을 말해주는가 | 크기 감각 | 우선순위 |
|---|---|---|---|---|
| `logs/{d}_TRADE.log` | 체결·주문 | **진입/청산/강제청산.** 작지만 가장 중요하다 | 15KB | 1 |
| `logs/{d}_WARN.log` | 경고 모음 | 게이트 차단·이상 징후가 모인다 | 74KB | 2 |
| `logs/{d}_SYSTEM.log` | 시스템·루프 | 매분 9단계 골격. **매분 루프 커버리지 판정 대상** | 815KB | 3 |
| `logs/{d}_SIGNAL.log` | 예측·판단 | 호라이즌별 예측, 등급 산출 | 551KB | 4 |
| `logs/{d}_LEARNING.log` | 자가학습 | SGD 온라인, GBM 배치, SHAP | 353KB | 5 |
| `logs/{d}_HEALTH.log` | 헬스체크 | 프로세스 생존 | 3.3KB | 6 |
| `logs/retrain_eod_{d}.log` | EOD 재학습 | **py310_64.** `Python 3.10.20 64-bit` 가 정상 | 18KB | 7 |
| `logs/retrain_intraday_{d}_{HHMMSS}.log` | 장중 재학습 | 30분 배치 | 4KB | 8 |
| `logs/{d}_MICRO.log` | 미시구조 | | 1.0MB | 9 |
| `logs/{d}_DATA.log` | 수집 | Cybos 수신, OPT50029 | 345KB | 10 |
| `logs/{d}_PROBE.log` | 프로브 | | 97KB | 11 |
| `logs/Mireuk_batch/launcher_{d}_{HHMMSS}_{pid}.log` | 런처 | **08:40 기동.** 파일명에 PID 포함 | 1.6MB | 12 |
| `logs/{d}_DEBUG.log` | 디버그 | | 223KB | 13 |
| `logs/{d}_BACKFILL.log` | 백필 | 0B면 백필 없었다는 뜻 | 0B | 14 |
| `logs/{d}_HOGA.log` | **호가 원본** | **51MB.** 본문은 안 읽는다 — 존재와 크기만 증거 | 51MB | 미열람 |

> **HOGA를 열지 않는 이유**: 원시 호가 스트림이라 하루 51MB다. 여기서 이상을 찾는 건
> 도서관 전체를 읽어 오탈자를 찾는 격이다. 크기가 평소와 크게 다르면 그때 들어간다.

## 1-A. 브랜치 규약 — **두 PC가 서로 다른 브랜치로 돈다** ⚠

2026-08-12 실측. 이걸 모르면 체리픽이 엉뚱한 브랜치로 간다(실제로 갔다).

| PC | 운영 브랜치 | 최근 |
|---|---|---|
| **MW0601** | **`v9-dev`** | `[MW0601] 458차 후속` |
| **MW0602** | **`dev`** | `[MW0602] 466차` |

그 밖에 `DEV-samefeature`(174차 스냅샷), `maitreya_dist`(MW0601 배포용)가 있다.

**MW0601의 로컬 `dev` 는 `origin/dev` 보다 289커밋 뒤처져 있다.** `config/settings.py` 가
**5,476줄 짧다** — `CB3_P4_GRADE_BLOCK_ENABLED`·`TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED`·
`HURST_SOFT_BLOCK_ENABLED` 같은 상수가 아예 없다.
**그 상태로 미륵이를 기동하면 289커밋 전 코드로 돈다.**

→ MW0601에서 작업할 때는 **반드시 `git branch --show-current` 로 `v9-dev` 를 확인**하고 시작하라.
→ 점검 중 브랜치가 다르면 그 자체를 P0로 보고하라. 수집기 §2가 브랜치를 첫 줄에 찍는다.

## 1-B. 완료 마커 · 리포트

`.txt` 이면서 8KB 이하면 수집기가 **전문을 싣는다.** 마커는 "그 단계가 끝났다"는 도장이다.

| 파일 | 시각 | 의미 | 없으면 |
|---|---|---|---|
| `data/daily_close_done_{d}.txt` | 15:40 | 일일 마감 완료 | 마감이 안 끝났다 |
| `data/eod_retrain_done_{d}.txt` | 15:47 | EOD 재학습 완료 | **모델 미교체 → 다음날 CB③ HALT 위험** |
| `data/daily_reports/strategy_report_{d}_{HHMMSS}.txt` | 15:40 | 일일 전략 리포트 | 리포트 생성 실패 |
| `model/horizons/gbm_{hz}_acc.txt.bak_{d}_{차수}` | 재학습 시 | 호라이즌별 정확도 백업 | 그 호라이즌 미재학습 |

`gbm_*_acc.txt.bak_*` 는 파일명의 **차수**(예: `_465`)로 어느 세션의 산물인지 알 수 있다.
수집기는 이것을 `exclude_patterns` 로 걸러 인벤토리에서 뺀다 — 필요하면 직접 보라.

## 1-C. 설치할 설정

리포 루트에 `config/dailycheck_targets.json` 을 두면 위 정책이 적용된다.
스킬 폴더의 `config_dailycheck_targets.json` 이 그 원본이다.

### 로그 형식 (2026-08-12 MW0601 실측)

```
2026-08-12 08:40:48 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=17492
└─ 날짜 시각        └ 레벨  └ 채널   └ 컴포넌트   └ 본문
```

**첫 대괄호는 레벨이지 태그가 아니다.** 컴포넌트는 `채널:` 뒤의 대괄호다.
수집기는 `MIREUK_LINE_RE` 로 이 넷을 정확히 가른다 — 이걸 틀리면 태그 히스토그램이
전부 `INFO`가 되어 쓸모없어진다.

채널은 파일명과 대체로 같지만 **`WARN.log` 에는 `SYSTEM:`·`HEALTH:` 가 섞여 들어온다**
(경고만 모아 놓은 파일이지 별도 채널이 아니다).

인코딩은 `utf-8-sig` → `cp949` 순으로 시도한다.

### 레벨 분포의 함정 — ERROR 를 찾지 마라

2026-08-12 하루 전체에서 **ERROR·CRITICAL 이 0건**이다(08-10에 HEALTH CRITICAL 1건이 마지막).
레벨만 보면 아무 일도 없었던 것처럼 보인다. 실제 신호는 이렇게 흩어져 있다.

| 무엇 | 어디에 | 레벨 |
|---|---|---|
| 진입·청산·손익 | `[Position] 진입` / `체결청산` | **INFO** |
| 게이트 차단 | `[차단]` | INFO |
| 사이징 | `[Sizer]` | INFO |
| 그날의 판정 | `전략 상태 경보` 배너 | WARNING |
| 성능 저하 | `메인 스레드 블로킹` | WARNING |
| 모델 열화 | `축퇴` `WeightCollapse` `ConstOut` | WARNING |

→ 그래서 수집기 **§5 거래일 요약**이 있다. 레벨 집계(§4)만으로 판단하지 마라.

### 거래일 요약이 파싱하는 토큰

`day_summary_patterns` (config로 덮어쓸 수 있다). 로그 문구가 바뀌면 여기만 고친다.

| 키 | 실제 라인 예시 |
|---|---|
| `entry_check` | `[진입체크] LONG→LONG 2계약 A급(원시C) \| sign✅ conf✅ vwap✅ cvd✅ ofi✅ … \| conf=40.5%` |
| `entry` | `[Position] 진입 LONG 2계약 @ 1026.8 \| 손절=1024.66 1차=1027.80(×0.59) 2차=1028.94 horizon=5m hurst=mean-revert` |
| `fill_entry` | `[체결진입] LONG 1계약 @ 1026.6 \| 평균=1026.6 보유=2계약` |
| `exit` | `[Position] 체결청산 LONG @ 1026.4 \| PnL=+1.72pt (+84,463원) \| TP2(전량)` |
| `exit`(손절 계열) | `… \| 하드스톱 [TP1보호]` / `… \| 하드스톱(틱) [TP1미도달]` — **468차 태그** |
| `block` | `[차단] 등급X — 미통과 항목: 2_confidence` |
| `sizer` | `[Sizer] 미니선물 실효잔고=50,000,000(…) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)` |
| `cb` | `[CB] 연속 손절 2회` |
| `block_ms` | `[LiveDBG] _tick_header 간격 6172ms — 메인 스레드 블로킹 발생` |

> ⚠ **`하드스톱` 라벨 하나에 정반대 두 사건이 들어 있다** — 진짜 손절과 TP1 도달 후
> 보호 스톱(**이익** 청산)이다. 0813 실측에서 `하드스톱` 2건이 둘 다 보호 트레일인데
> 이 수집기가 "하드스톱·손절 계열 2/3건(67%)"이라는 오독을 자동 생산했다.
> 465차가 `trades.tp1_reached` 컬럼을, 468차가 위 **로그 태그**를 넣어 구분한다
> (`exit_reason` 문자열 자체는 사전등록 채널 필터라 **바꾸지 않는다**).
> §5·§11은 `exit_stop_kind()`로 손절/보호/불명을 갈라 센다 — **태그 없는 468차 이전
> 로그는 '불명'이며 손절로도 보호로도 세지 않는다.**

배너는 `banner_start="전략 상태 경보"` 부터 8줄을 통째로 담는다.

```
[전략 상태 경보] v1.0
  판정  : UNDERPERFORM
  드리프트: CLEAR (Lv.0)
  액션  : 🔄 교체 후보 탐색
  사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약.
  오늘 PnL: +170443원
```

### 컴포넌트 상위 (2026-08-12 실측)

`CybosInvestorRaw`(1574) · `ScalerFloor`(1452) · `CybosRT-TICK`(1209) · `MetaGate`(590) ·
`CybosRT-ROLLOVER`(409) · `CVD-ANCHOR`(409) · `BAR-CLOSE`(409) · `PipePerf`(384) ·
`Ensemble`(377) · `Checklist`(231) · `ATR-Horizon`(202) · `MicroRegime`(172) ·
`차단`(115) · `InstabilityGate`(78) · `WeightCollapse`(78) · `ToxicityGate`(50)

> `ScalerFloor` 는 SIGNAL WARNING 1946건 중 1386건을 차지한다. **압도적 다수라고 해서
> 중요한 것은 아니다** — 배경 소음으로 보고, 나머지 560건에서 신호를 찾아라.

### 항상 인용되는 패턴

`always_quote_patterns` — 추상적 키워드가 아니라 **실제로 찍히는 문자열**이다.

| 계열 | 패턴 |
|---|---|
| 안전장치 | `[CB]` `연속 손절` `HALT` `CIRCUIT` |
| 청산 | `강제청산` `[ExitCooldown]` `안전망` `FORCED` |
| 크래시 | `0xC0000409` `STACK_BUFFER` `Traceback` `MemoryError` |
| 성능 | `메인 스레드 블로킹` `[Brier] 과신` `[SHAP] 슬로우` |
| 상태 | `degraded=ON` `level=CRITICAL` |
| 모델 열화 | `축퇴` `WeightCollapse` `ConstOut` `ConfFloorGuard` |
| 판정 | `전략 상태 경보` `판정  :` |
| 생명주기 | `[Shutdown]` `자동 종료` `기동 복원` |

> 맨 `OOM` 은 **뺐다** — `장중 경량 모드(DB): 39799 → 4800행 사전 제한 (OOM 방지)` 같은
> **예방 문구**가 잡혀 매일 가짜 적신호를 냈다. `MemoryError`·`OutOfMemory`·`메모리 부족`만 본다.

---

## 2. 설정 — 불변식의 원천

| 파일 | 무엇이 있는가 |
|---|---|
| `config/settings.py` | **한시 예외 3종**, `MAX_CONTRACTS`, `SIZING_*`, `HURST_*`, `HORIZON_CORE_GROUP`, `CORE_FEATURES_BY_GROUP`, `VALIDATION_CAMPAIGN`, `VALIDATION_CAMPAIGN_DECISIONS`, `VALIDATION_REPORT_KEEP_WEEKS` |

수집기는 이 파일을 **import 하지 않고 정규식으로 읽는다.** import 하면 py37_32 전용 모듈이
딸려 들어와 터진다. 값만 알면 되므로 텍스트 읽기가 안전하고 빠르다.

`VALIDATION_CAMPAIGN_DECISIONS` 는 **확정 결정 레지스트리**다. 리포트가 요약표에 📌 인라인
마커 + 하단 섹션으로 렌더링한다. 결정을 바꾸면 여기와 `DECISION_LOG.md` 둘 다 갱신한다.

---

## 3. 기준 문서

| 파일 | 역할 | 주의 |
|---|---|---|
| `CLAUDE.md` | **최우선 SSOT.** 절대원칙 6종, 9단계, 실전 전환 기준, 26주 재검증 | |
| `CORE.md` | 핵심 판단 규칙 — 코딩 전 필수 | |
| `ROADMAP.md` | Phase별 계획 + 마일스톤 | |
| `_archive/plans/PROJECT_DESIGN.md` | 2026-04 브레인스토밍 | **30m 등 구식 내용 포함. 근거로 인용 금지** |
| `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` | CB② 예외 근거 §7-1 | |
| `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md` | 4주 검증 캠페인 설계 → 상시 전환됨 | "W4에 확정" 전제는 폐기됨 |

---

## 4. dev_memory

| 파일 | 크기 | 읽는 법 |
|---|---|---|
| `dev_memory/DECISION_LOG.md` | ~315KB | 통째로 읽지 않는다. 헤딩 목록 + 꼬리 몇 KB. 증상→원인→결정→Why→How to apply→검증 |
| `dev_memory/NEXT_TODO.md` | ~280KB | 미완료 체크박스 `- [ ]` 만 뽑는다 |

세션 헤더 형식: `## 2026-07-29 (MW0602 402차 — …)` — **PC명 병기 필수**.

---

## 5. 정기점검 산출물

```
docs/정기점검/매일점검/
    <PC명>-<YYYYMMDD>-점검리포트.md          ← 이 스킬의 산출 위치

docs/정기점검/금요일점검/<PC명>/              ← MW0601 / MW0602
    validation_campaign_report_YYYYMMDD.md    (코드 생성 — EOD 체인)
    validation_campaign_metrics_YYYYMMDD.json (코드 생성 — EOD 체인)
    MMDD_주간회의_검토보고_<PC명>.md           (주간회의 세션에서 작성)
```

- PC명은 `utils/db_utils.py:pc_id()` 가 호스트명에서 뽑는다 (`DeskTop-MW0601` → `MW0601`)
- 폴더가 PC를 나타내므로 **파일명에는 날짜만**
- **날짜본으로 절대 덮어쓰지 않는다** — 지난주 리포트를 잃은 사고가 실제로 있었다
- 이 위치는 gitignore의 **의도적 예외**다. 두 PC가 서로를 보는 유일한 통로이므로 되돌리지 마라
- 대조 스크립트: `scripts/cmp_summary.py` / `cmp_metrics.py` (`--date1/--date2`로 주차 지정)
- ⚠ 대조는 **같은 코드 세대로 생성된 리포트끼리** — 출력 상단 "only" 줄이 비지 않으면 코드 세대 차이다

---

## 6. 주요 코드 경로

| 경로 | 역할 |
|---|---|
| `config/settings.py` | 전 설정 |
| `model/multi_horizon_model.py` | 멀티 호라이즌 예측, `_CORE_MASK_EXEMPT_BY_HZ` |
| `strategy/entry/checklist.py` | 진입 체크리스트, `entry_horizon` 그룹 판정 |
| `strategy/regime_fingerprint.py` | PSI 계산, `_PSI_WATCH/_ALARM/_CRIT` |
| `features/technical/cvd.py` · `vwap.py` · `ofi.py` | 단기·중기 CORE 피처 |
| `collection/option/option_chain.py` | `opt_chain_pcr` (장기 CORE) |
| `utils/db_utils.py` | `pc_id()` |
| `scripts/retrain_eod.py` · `retrain_intraday.py` | **py310_64 전용** |
| `EOD_RETRAIN.bat` · `scripts/eod_retrain.py` | **py310_64 전용** (191차). py37_32 언급은 구버전 잔재 |
| `scripts/hurst_oos_validation.py` · `hurst_stability_check.py` | Hurst 재검증 |
| `scripts/core_feature_discovery.py` · `validate_feature_set_purged_cv.py` · `feature_ablation_purged_cv.py` · `horizon_signal_tradability.py` · `ic_decay_catalog.py` | 피처셋 재검증 L1~L3 |

---

## 7. 원본 조회 명령

```powershell
# Windows (PowerShell / cmd)
findstr /C:"강제청산" logs\*20260812*.log
findstr /R /C:"ERROR" /C:"CRITICAL" logs\*20260812*.log
findstr /C:"[Sizer]" logs\*20260812*.log
```

```bash
# Git Bash / WSL
grep -n "강제청산\|안전망" logs/*20260812*.log
grep -cE "ERROR|CRITICAL" logs/*20260812*.log
grep -o '\[[A-Za-z]*\]' logs/*20260812*.log | sort | uniq -c | sort -rn | head -30
```

```bash
# git
git log --oneline --since="2026-08-12 00:00" --until="2026-08-13 00:00"
git log --oneline -12 | grep -v "\[MW"      # PC명 태그 누락 커밋
git status --porcelain
```
