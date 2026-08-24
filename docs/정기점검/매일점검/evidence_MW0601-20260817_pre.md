# 미륵이 증거 다이제스트 — 2026-08-17 / PRE

- 생성 2026-08-17 16:48:00 KST · PC **UNKNOWN** (`claude`)
- 리포 `/sessions/determined-affectionate-lamport/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260817` · `2026-08-17` · `260817` · `0817`
- ⚠ 호스트명에서 `MW####` 를 못 뽑았다 — 커밋/DECISION_LOG 태그를 수동 확인할 것

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **14개** 파일 · 14개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_15180.log` | 1 | `logs/Mireuk_batch/launcher_20260817_084001_15180.log` | 22.7KB | 08-17 12:55 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260817.log` | 1.0KB | 08-17 15:46 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260817_BACKFILL.log` | 0B | 08-17 15:11 |
| `{DATE}_DATA.log` | 1 | `logs/20260817_DATA.log` | 0B | 08-17 08:40 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260817_DEBUG.log` | 0B | 08-17 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260817_HEALTH.log` | 0B | 08-17 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260817_HOGA.log` | 0B | 08-17 08:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260817_LEARNING.log` | 52.5KB | 08-17 08:41 |
| `{DATE}_MICRO.log` | 1 | `logs/20260817_MICRO.log` | 0B | 08-17 08:40 |
| `{DATE}_PROBE.log` | 1 | `logs/20260817_PROBE.log` | 95B | 08-17 08:41 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260817_SIGNAL.log` | 2.0KB | 08-17 11:50 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260817_SYSTEM.log` | 14.5KB | 08-17 12:51 |
| `{DATE}_TRADE.log` | 1 | `logs/20260817_TRADE.log` | 167B | 08-17 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260817_WARN.log` | 743B | 08-17 08:41 |

## 2. 코드·커밋 상태

- HEAD `e995764` · 브랜치 `v9-dev` · 미커밋 452건
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/RUN_ON_MW0602.md
 M .claude/skills/mireuk-daily-check/SKILL.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .claude/skills/mireuk-daily-check/scripts/collect_evidence.py
 M .gitignore
 M CLAUDE.md
 M INSTALL.bat
 M LAUNCH_API.bat
 M ROADMAP.md
 M SETUP_GUIDE.md
 M backtest/param_optimizer.py
 M backtest/walk_forward.py
 M challenger/challenger_db.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/base_challenger.py
 M challenger/variants/champion_tp1_skip_trail.py
 M collection/broker/base.py
 M collection/broker/cybos_broker.py
 M collection/broker/factory.py
 M collection/cybos/api_connector.py
 M collection/cybos/investor_data.py
 M collection/cybos/realtime_data.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/constants.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
… 외 412건
```

**당일(2026-08-17) 커밋**
```
e995764 [MW0601] 472차: UI 좌상단 "Phase 3 예정" 배지 → Phase 5 전환 게이트 자동 판정
```

**최근 커밋 12건**
```
e995764 [MW0601] 472차: UI 좌상단 "Phase 3 예정" 배지 → Phase 5 전환 게이트 자동 판정
f911e8d [MW0601] 471차 후속8: G-3 강제청산 리허설 26주 WFA 편입 + 로드맵 반영 + dev_memory
211246d [MW0601] 471차 후속7: G-2 ConstOut 호라이즌 건강도 채널 [51] 신설
ca954b8 [MW0601] 471차 후속6: G-1 사이징 계보 구조체 저장 + [28] 사이저 압력 실측화
cdb7462 [MW0601] 471차 후속5: dev_memory 반영 — F-9 구현 기록
7284b95 [MW0601] 471차 후속4: entry_mode 예외 폴백 가시화 (F-9)
fc889ff [MW0601] 471차 후속3: dev_memory 반영 — 471차 구현 기록 + 잔여/후속 항목
82e7554 [MW0601] 471차 후속2: 차단사유 정합 — 동시 성립 축 전량 + 선제차단 플래그 (스키마)
8be4048 [MW0601] 471차 후속: [SizerMatch] binding 게이트 명시 + 품질군 전량 출력
76211c3 [MW0601] 471차: 15:10 강제청산 1차 경로 도달성 복구 + 안전망 하트비트
e8a56ea [MW0602] 459차: F1 승패 집계 단위(레그→포지션) + F2 SHS CORE 미측정 분리
fe88f93 [MW0602] 460차: 공용 헬퍼 _spearman 동률 처리 버그 — 사본 2벌 정정 + 회귀테스트
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `9999` | `9999` | 일치 | 모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. 재검토 기한 2026-08-29 |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `3` | `3` | 일치 | 431차 10→3 인하. 실전 자본 확정 시 재산출 대상 |
| `SIZING_TARGET_CAPITAL_ENABLED` | `True` | `True` | 일치 | 모의투자 한정. False 전환은 단독 지시로 읽지 말 것 (손실 구간 복원 위험) |
| `SIZING_TARGET_CAPITAL_KRW` | `50_000_000` | — | 값 확인 | 현행 5천만원. 실전 전환 기준 ⑧의 남은 해제 조건 |
| `HURST_WINDOW_N` | `90` | `90` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `HURST_MAX_LAG` | `9` | `9` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `VALIDATION_REPORT_KEEP_WEEKS` | `4` | `4` | 일치 | 주간 리포트 FIFO 보관 |
| `CB_ACCURACY_MIN_30M` | `0.28` | `0.28` | 일치 | CB③ 임계. 98차(2026-06-02) FLAT 예측 제외 + 0.35→0.28. CLAUDE.md 문구 정정 완료(461차 F-3) |
| `CB_ACC_RESTRICTED_MIN` | `0.30` | `0.30` | 일치 | WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인 |
| `CB_ACCURACY_MIN_30M_STRICT` | `0.42` | `0.42` | 일치 | 과신 연속 시 강화 임계 (0.50→0.42 완화) |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | `False` | `False` | 일치 | 311차 후속4가 처음부터 False로 신설(섀도). CLAUDE.md 한시예외 4번째 + 실전 전환 기준 ⑨ 등재(461차 F-4). ⚠ 복원 선행조건: sp… |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | `True` | `True` | 일치 | 호가 상하한 핀 진입 차단 — 켜져 있어야 정상 |
| `HURST_SOFT_BLOCK_ENABLED` | `True` | `True` | 일치 | Hurst 소프트 차단(사이즈 0.5배). 316~318차 재보정 계열 |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | `True` | `True` | 일치 | Degraded 상태 자동진입 차단 — 켜져 있어야 정상 |
| `CB_PIPE_PAUSE_MS` | `5_000` | `5_000` | 일치 | CB⑤ 실질 구현. `CB_API_LATENCY_LIMIT` 은 Kiwoom 레거시로 Cybos에서 미사용 |
| `ENTRY_HORIZON_B1` | `3.2` | `3.2` | 일치 | 1m/3m 경계 [374차 1.5→3.5, 387차 3.5→3.2] — 드리프트 항목 |
| `ENTRY_HORIZON_B2` | `4.4` | `4.4` | 일치 | 3m/5m 경계 [374차 2.5→4.0, 387차 4.0→4.4] — 드리프트 항목 |
| `CB_DAILY_HALT_FULL_BLOCK` | `3` | `3` | 일치 | HALT 3회 → 완전 관망 |
| `MODEL_LABEL_STATE_UNLOCK_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지 |
| `PRE_RETRAIN_DONE_BY_EOD_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치 |
| `ZONE_ENTRY_BAN_ENFORCE` | `—` | `False` | **미발견 ⚠** | 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지 |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | `—` | `True` | **미발견 ⚠** | 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다 |
| `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` | `—` | `True` | **미발견 ⚠** | 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치) |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

### 차단 게이트 전수 인벤토리 — 27개 중 **7개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `TICKUI_TRACE_ENABLED` | False | 기능토글 |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | 기록됨 |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | True | — |
| `HEALTH_DEGRADED_ENABLED` | True | — |
| `HEALTH_LATENCY_TREND_ENABLED` | True | — |
| `HEALTH_POLICY_HOT_RELOAD_ENABLED` | True | — |
| `HEALTH_RETRAIN_RELAX_ENABLED` | True | — |
| `HURST_REGIME_ATR_MULT_ENABLED` | True | — |
| `HURST_SOFT_BLOCK_ENABLED` | True | — |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | True | — |
| `LOSS_TIER1_ENABLED` | True | — |
| `LOSS_TIER1_QTY1_TICK_ENABLED` | True | — |
| `LOSS_TIER1_TICK_ENABLED` | True | — |
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260817_HOGA.log` 0B — 존재와 크기만 증거로 본다_

### `logs/20260817_TRADE.log` — 167B · 2행 · 최종 08:41:13

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-17 08:41:09 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-17 08:41:13 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-17 08:41:09 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-17 08:41:13 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260817_WARN.log` — 743B · 5행 · 최종 08:41:19

- 형식 평문 · 시각 인식 5행 · WARNING=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-17 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-17 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-08-17 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-08-17 08:41:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-17 08:41:19 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
2026-08-17 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-17 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-08-17 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-08-17 08:41:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-17 08:41:19 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 5 | 08:41:16 | 08:41:19 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |

**채널** — `SYSTEM`×5

**컴포넌트 상위 15** — `LiveDBG`×5

### `logs/20260817_SYSTEM.log` — 14.5KB · 97행 · 최종 12:51:16

- 형식 평문 · 시각 인식 95행 · INFO=95, PLAIN=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-17 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=22184 | 행감지=30s all_threads=True
2026-08-17 08:40:59 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-17 08:40:59 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-17 08:40:59 [INFO] SYSTEM: 미륵이 초기화
2026-08-17 08:40:59 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-14) 종가 버퍼 로드: 384봉
  …
2026-08-17 12:31:16 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 12:31:16
2026-08-17 12:36:16 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 12:36:16
2026-08-17 12:41:16 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 12:41:16
2026-08-17 12:46:16 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 12:46:16
2026-08-17 12:51:16 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 12:51:16
```

</details>

**채널** — `SYSTEM`×95

**컴포넌트 상위 15** — `System`×56, `CybosSub`×7, `SYSTEM`×4, `BrokerSync`×4, `BalanceUI`×4, `Account`×2, `CybosDailyPnl`×2, `WarmupRetrain`×2, `Notify`×2, `Capital`×2, `FaultHandler`×1, `FeatureBuilder`×1, `Calib`×1, `Calibration`×1, `AnalysisRestore`×1

### `logs/20260817_SIGNAL.log` — 2.0KB · 21행 · 최종 11:50:11

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.434
2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.413
2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.409
2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.417
  …
2026-08-17 08:45:11 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → PRE_MARKET: 선물 프리장 — 진입 불허, scaler warmup 전용
2026-08-17 09:00:11 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
2026-08-17 09:05:11 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OPEN_VOLATILE: 개장 변동성 — 추세추종, 신뢰도↑
2026-08-17 10:30:11 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → STABLE_TREND: 안정 추세 — 표준 앙상블
2026-08-17 11:50:11 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
```

</details>

**채널** — `SIGNAL`×21

**컴포넌트 상위 15** — `DynMC`×7, `Model`×6, `TimeRouter`×6, `EnsembleGater`×1, `FeatureBuilder`×1

### `logs/20260817_LEARNING.log` — 52.5KB · 288행 · 최종 08:41:14

- 형식 평문 · 시각 인식 288행 · WARNING=143, INFO=145

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-17 08:41:00 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-17 08:41:00 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-17 08:41:00 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2002 < conf_floor=0.3300 (span=0.00040 auc=0.536 out_max=0.2002, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-17 08:41:00 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00033 auc=0.529 out_max=0.2002 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=85) → 보정 미적용, raw 통과
2026-08-17 08:41:00 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00064 auc=0.556 out_max=0.2004 (n=90) → 보정 재적용
  …
2026-08-17 08:41:09 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-17 08:41:09 [INFO] LEARNING: [Calibration] 보정기 복원 완료 (n=888 method=platt fitted=True degenerate=False unreachable=False span=0.00630 auc=0.550 out_max=0.3479)
2026-08-17 08:41:09 [INFO] LEARNING: [Consolidator] 패널티 이력 로드: {'CLOSE_VOLATILE': 0.0, 'LUNCH_RECOVERY': 0.0, 'OTHER': 0.0, 'OPEN_VOLATILE': 0.0, 'STABLE_TREND': 0.0, 'EXIT_ONLY': 0.0, 'GAP_OPEN': 0.0}
2026-08-17 08:41:09 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=DRIFT_UP
2026-08-17 08:41:14 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=1개 | 교체후보=3개 | CORE안전=⚠️
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 143 | 08:41:00 | 08:41:09 | 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×288

**컴포넌트 상위 15** — `Calibration`×282, `ExtremityCorrector`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1

### `logs/retrain_eod_20260817.log` — 1.0KB · 11행 · 최종 15:46:34

- 형식 평문 · 시각 인식 11행 · INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-17 15:45:04,154 [INFO] EOD_RETRAIN: =======================================================
2026-08-17 15:45:04,154 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-17 15:45:04,154 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-17 15:45:04,154 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-17 15:45:04,154 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-17 15:45:04,154 [INFO] EOD_RETRAIN: [WaitDC] daily_close() 완료 대기 시작 (최대 20분, 16:05:04까지)
2026-08-17 15:45:04,154 [INFO] EOD_RETRAIN: [WaitDC] daily_close() 대기 중 — 잔여 20분 (16:05:04까지)
2026-08-17 15:45:34,161 [INFO] EOD_RETRAIN: [WaitDC] daily_close() 대기 중 — 잔여 19분 (16:05:04까지)
2026-08-17 15:46:04,174 [INFO] EOD_RETRAIN: [WaitDC] daily_close() 대기 중 — 잔여 18분 (16:05:04까지)
2026-08-17 15:46:34,175 [INFO] EOD_RETRAIN: [WaitDC] daily_close() 대기 중 — 잔여 18분 (16:05:04까지)
```

</details>

**채널** — `EOD_RETRAIN`×11

**컴포넌트 상위 15** — `EOD_RETRAIN`×6, `WaitDC`×5

### `logs/20260817_PROBE.log` — 95B · 1행 · 최종 08:41:16

- 형식 평문 · 시각 인식 1행 · INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-17 08:41:16 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
  …
2026-08-17 08:41:16 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
```

</details>

**채널** — `PROBE`×1

**컴포넌트 상위 15** — `CybosInvestorProbe`×1

### `logs/Mireuk_batch/launcher_20260817_084001_15180.log` — 22.7KB · 209행 · 최종 12:55:01

- 형식 평문 · 시각 인식 124행 · WARNING=5, WARN=2, INFO=130, PLAIN=72

<details><summary>첫 5행 / 끝 5행</summary>

```
============================================================
Mireuk (KOSPI 200 Futures Auto Trader)
Broker : cybos
Launch : 20260817_084001
Log    : C:\Users\82108\PycharmProjects\futures\logs\Mireuk_batch\launcher_20260817_084001_15180.log
  …
============================================================
Mireuk 종료. RestartCnt=0 Runtime=255min Log=C:\Users\82108\PycharmProjects\futures\logs\Mireuk_batch\launcher_20260817_084001_15180.log
============================================================
[AUTO-RESTART] 정상 종료 감지 -- 이유: user_close -- 재시작 안 함
[AUTO-RESTART] 재시작이 필요하면 start_mireuk.bat 를 다시 실행하세요.
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 5 | 08:41:16 | 08:41:19 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `-` | 2 | ??:??:?? | ??:??:?? | ] 이미 실행 중인 main.py 프로세스가 감지됐습니다. |

**채널** — `SYSTEM`×100, `SIGNAL`×21, `TRADE`×2, `PROBE`×1

**컴포넌트 상위 15** — `-`×69, `System`×56, `DynMC`×7, `CybosSub`×7, `Model`×6, `TimeRouter`×6, `LiveDBG`×5, `GUARD`×4, `SYSTEM`×4, `BrokerSync`×4, `BalanceUI`×4, `OK`×3, `AUTO-RESTART`×3, `FeatureBuilder`×2, `Account`×2

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 2건 · 최대 2781ms · 5초 초과 0건

상위 — 2781ms, 2781ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260817_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:19 2026-08-17 08:41:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
```

### `logs/20260817_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.434
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.413
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.409
```

### `logs/20260817_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:00 2026-08-17 08:41:00 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:41:00 2026-08-17 08:41:00 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2002 < conf_floor=0.3300 (span=0.00040 auc=0.536 out_max=0.2002, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:00 2026-08-17 08:41:00 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00033 auc=0.529 out_max=0.2002 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=85) → 보정 미적용, raw 통과
08:41:00 2026-08-17 08:41:00 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00064 auc=0.556 out_max=0.2004 (n=90) → 보정 재적용
```

### `logs/Mireuk_batch/launcher_20260817_084001_15180.log`
```
--- 기동 복원 ×7(표본)
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.434
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.413
08:40:43 2026-08-17 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.409
--- 메인 스레드 블로킹 ×1(표본)
08:41:19 2026-08-17 08:41:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260817_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:09 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260817_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 5 | 08:41:16 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260817_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 46 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=22184 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 3 | 08:51:16 [INFO] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 08:51:16 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 3 | 08:56:16 [INFO] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 08:56:16 |

- 이 로그 생존구간: 08:40 ~ 12:51

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260817_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:40:43 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.434 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:00:11 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 09:00:11 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |

- 이 로그 생존구간: 08:40 ~ 11:50

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.8MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 커밋 ① `76211c3` — F-1 + F-2 (15:10 강제청산 도달성 복구 + 안전망 하트비트)
### 커밋 ② `8be4048` — F-3 (`[SizerMatch]` binding 명시 + 품질군 전량 출력)
### 커밋 ③ `82e7554` — F-4 (차단사유 정합, 스키마 동반)
### [검증] 회귀 전량
### [참고] 스테일 `.git/index.lock` 제거
### [미구현] 본 세션이 손대지 않은 것
### [2026-08-14 471차 후속4] F-9 `entry_mode` 폴백 가시화 — 커밋 `7284b95`
### [2026-08-14 471차 후속6~8] 고도화 G-1·G-2·G-3 구현 — 커밋 `ca954b8` · `211246d` · (문서)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
]`를 고쳤지만 게이트가 하나 늘 때마다
  같은 오귀속이 재발한다. 실전 전환 기준 ⑧의 근거 채널이 읽는 값이라 근거 무결성 문제다.
- **부수 효과가 더 컸다**: [28]의 `structural_reason`이 **417차에 TRADE 로그로 한 번
  센 수치**(379건 중 86건, 2026-07-14~07-31)를 매주 그대로 재인용하고 있었다 —
  "수치가 낡았는지 의심되면 재집계할 것"이라 스스로 적어둔 채로. `_sizer_pressure_from_trace()`가
  이를 **매주 실측**으로 대체한다(사이저 출력/최종 수량 분포, 3계약+ 출력 비율,
  binding 게이트 빈도, 3계약+ 체결 수).
- 🔴 **판정에는 관여하지 않는다** — 합격선 사전등록 불변(§9). 테스트가 "판정 구간이
  `sizer_pressure`를 읽지 않는다"를 소스 수준으로 못 박는다.
- ⚠ 사이저가 돌지 않은 분은 **NULL**(0 아님). 2026-08-14 이전 구간도 전부 NULL이며
  **미측정**이다 — 417차 수치와 직접 비교 금지(집계 원천이 로그 vs DB로 다르다).

#### G-2 — ConstOut 호라이즌 건강도 채널 [51] (`211246d`)

🔵 **함정 ① 정정 — 리포트 G-2의 절반은 이미 구현돼 있었다.**
"ConstOut {호라이즌: {events, minutes}}를 DB 일별 테이블로 영속화"는 **457차 G5**가
이미 했다(`scaler_daily.const_out_by_horizon`). 실데이터도 2026-08-12부터 쌓여 있다
(08-12 `{3m:3회/5분, 5m:5회/9분}` · 08-13 · 08-14 `{3m:5회/7분}`). 리포트 문구를 그대로
믿고 구현했으면 **중복 테이블을 만들 뻔했다.** 남은 절반(진입 성적 결합)만 만들었다.
**Why**: 매일 점검 리포트의 제안은 "이미 있는지"를 코드로 확인한 뒤 착수해야 한다 —
CLAUDE.md 검증 캠페인 절의 "판정과 결정은 별개" 함정과 같은 계열이다.

- 사전등록 `VALIDATION_CAMPAIGN["const_out_horizon_watch"]`:
  heavy_events_min=3(0814 O-3 관측기준과 **같은 값** — 임계를 둘로 나누면 두 문서가 갈린다),
  min_samples_per_bucket=20 · min_days=5 · pnl_gap_krw=200,000([28]·[29]와 동일),
  data_start=2026-08-12(457차 G5 배포일).
- 🔴 **핵심 불변식**: `const_out_by_horizon`이 NULL인 날의 진입은 heavy·clean
  **어디에도 넣지 않는다.** 미측정을 "ConstOut 0"으로 읽으면 clean 버킷이 오염되는데
  하필 캠페인 구간 대부분이 그 구간이다 — 실측 제외 **138포지션**.
  `{}`(빈 dict)는 "측정했고 무발생"이라 clean으로 센다. **둘은 다른 사실이다.**
- `FLAG_DRAG`는 **차단 처방이 아니다**(라우터 억제·재학습 스케줄·피처셋 조사 축).
  FAIL 어휘를 쓰면 316~318차 HurstGate FalseBlock을 반복한다.
- ⚠ `_fmt_verdict` 미등록 verdict는 **조용히 INSUFFICIENT로 표시된다** — 새 채널
  추가 시 이 등록을 빠뜨리면 판정이 사라진 것처럼 보인다. 주석으로 못 박았다.
- 라이브 실행: `INSUFFICIENT — 측정구간 진입 거래일 2 < 5 … 미측정 제외 138포지션`.
  **당분간 INSUFFICIENT가 정상이다.** 지금 등록하는 이유는 사전등록 원칙(313차 ④).

#### G-3 — 15:10 강제청산 리허설의 26주 WFA 편입 (문서)

`CLAUDE.md` "주기적 재검증 항목"에 등재 + 실전 전환 기준 **②에 선행 확인사항** 추가.
- **왜 별도 캘린더를 만들지 않는가**: 관리 포인트가 늘면 CB②·CB③-P4·FP-CRITICAL처럼
  "재검토하기로 했는데 안 함"이 된다(317차 사용자 원칙).
- 판정 기준을 문서에 박았다: 정상 = `[ForceExitPass]`→`[TimeExit]`→`[ExitAttempt]`가
  15:10:00~05에 출현하고 `[SchedForceExit]` ERROR **미출현**. 15:11 ERROR면 1차 경로 재사망.
- ⚠ **1회차 리허설 자체는 미실시** — `NEXT_TODO` F-1R이 실행 항목이다. 문서 등재만으로
  ②가 충족된 것으로 읽지 말 것.

#### 검증

`tests/test_471_sizing_trace.py`(37) · `tests/test_471_const_out_horizon_watch.py`(23) 신설.
471차 기존 4종 + 453·457·458 회귀 전부 통과. py37_32 컴파일 확인
(main.py · prediction_buffer.py · db_utils.py · settings.py · 캠페인 리포트 · 신규 채널).

```

</details>

### dev_memory/NEXT_TODO.md — 902.8KB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-08-14 (MW0601 470차 후속 — 장후 점검) 신규 항목
### Fix — 전부 **다음 기동 전(장 마감 후)** 적용
### 고도화
### 문서·운영
### 다음 관측 (판정 근거)
## 2026-08-14 (MW0601 471차 — 장후 Fix 구현) 신규/잔여 항목
### 🔴 최우선 — 다음 거래일
### 잔여 — 계획 범위 밖이라 이번에 손대지 않은 것
```

미완료 체크박스 **1284건** (끝에서 30건)
```
- [ ] **F-6 안전장치 로그 이중기록 제거 (P2)** — 호출부를 `log_manager` 단일 경로로 통일.
- [ ] **F-7 CB③-P4 상태 전이 양방향 기록 (P2)** — `RESTRICTED → NORMAL` 복귀도 같은 형식으로 로그.
- [ ] **F-8 STEP 3 재학습 주기 문서 정정 (P2)** — `CLAUDE.md` 매분 파이프라인
- [ ] **G-4 사이징 축소 원인을 구조체로 저장 (이번 주)** — 진입 시점 `_quality_mults` 전량 +
- [ ] **G-5 IntradayRegime 히스테리시스 (섀도 먼저)** — 진입/이탈 임계 분리
- [ ] **G-6 `3m ConstOut` 재발을 호라이즌 건강지표로 승격 (이번 주)** — 일별 `ConstOut(호라이즌)`
- [ ] **실전 전환 기준 ⑧에 "[28] 채널 근거 무결성 확인"을 선행 확인사항으로 명시** — F-5 미적용 상태의
- [ ] **실전 전환 기준 ⑥에 "RESTRICTED 지속시간 계측 배선"을 선행조건으로 추가** — ⑨의
- [ ] **O-1 `WeightCollapse` 종가 비율** — 오늘 12:32 기준 90/206 = **43.7%**(NEXT_TODO O-6 승계).
- [ ] **O-2 `_tick_header ≥5,000ms` 종가 건수** — 12:00 기준 **5건**(최대 9,125ms). 15건 초과면 G-3 상향.
- [ ] **O-3 Degraded 선제차단 3건(09:39 / 10:39:59 / 11:24)의 해당 분봉 `ensemble_decisions`** —
- [ ] **O-4 `3m ConstOut` 종가 횟수와 전일 대비** — 오늘 3회(09:35:59 / 10:36:59 / 11:20:59).
- [ ] **O-5 `OPEN_VOLATILE 시가이격 과다` 차단 18건(09:53~10:24)의 반사실** — 같은 구간
- [ ] **O-6 `IntradayRegime` 종가 총 전이 횟수** — 오늘 1일차 **19회**. 5거래일 누적 후 G-5 판정
- [ ] **O-7 FP-CRITICAL PSI 오늘 값** — 채널 로그 출력 0건. 333차 후속5의 file 로그 전용 구조
- [ ] **O-8 CASE-01 포지션 단위 손익 3원 대사** — 로그 / `ensemble_decisions` / `trades`.
- [ ] **`evidence_MW0601-20260814_pre_1622.md` 수동 삭제** — 수집기 `--pc` 부재로 생긴 부수 산출물.
- [ ] **CB② 복원 8/29 주간회의 상정** — 기한 15일 남음. 오늘 캠페인 `[0] 표본 기아 = OK(주간 32건)`
- [ ] **O-1 EOD `[GuardFair]` `사이드카=현행 train_end_ts 없음` 건수** — 오늘 **6/6**.
- [ ] **O-2 `WeightCollapse` 분봉 단위 비율** — 오늘 **79/369=21.4%**(`[ModelHealth]` 라인 사용).
- [ ] **O-3 `3m ConstOut` 확정 횟수** — 오늘 **4회**. 3거래일 연속 3회 이상이면 3m 피처셋 딥다이브
- [ ] **O-4 `IntradayRegime` 일일 전이 횟수** — 오늘 **32회**(NORMAL↔DAY_RISK_OFF 18 ·
- [ ] **O-5 Degraded 선제차단 분봉의 `conf` vs `min_conf`** — 오늘 **4/4 모두 `conf < min_conf`**
- [ ] **O-6 `_tick_header ≥ 5,000ms` 일일 건수** — 오늘 **6건**(최대 9,125ms @09:01:07 장시작 버스트).
- [ ] **O-7 RegimeFingerprint `PSI`·`PSI/feat`** — 오늘 **0.007 CLEAR**(cvd=0.151 / vwap=0.007 /
- [ ] **O-8 `[50]` 방향 편향** — 오늘 앙상블 방향 **SHORT 142 / LONG 33 / FLAT 194**(4.3:1).
- [ ] **F-1R 15:10 강제청산 리허설(모의 1계약) — 사용자 실행 필요.**
- [ ] **F-1H 하트비트 1일차 확인** — 다음 거래일 `logs/*_SYSTEM.log`에
- [ ] **F-4M 스키마 마이그레이션 1일차 확인** — 다음 기동 후
- [ ] **G-1 사이징 축소 원인을 구조체로 저장** — **선행 F-3 충족됨**(`8be4048`).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
거래일 연속 3:1 초과면 레이블/학습창 딥다이브

---

## 2026-08-14 (MW0601 471차 — 장후 Fix 구현) 신규/잔여 항목

> 위 470차 후속 F-1~F-4는 **전부 구현 완료**(커밋 `76211c3` · `8be4048` · `82e7554`).
> 아래는 그 구현이 **새로 만든 후속 항목**과 계획 범위 밖이라 남은 것뿐이다.

### 🔴 최우선 — 다음 거래일

- [ ] **F-1R 15:10 강제청산 리허설(모의 1계약) — 사용자 실행 필요.**
  F-1의 "결정 필요 사항"을 **권고대로 '한다'로 확정**했다(2026-08-14 사용자 지시).
  코드 리뷰·유닛테스트만으로는 끝나지 않는다 — 이 경로는 6개월간 라이브 0회 실행이다.
  **절차**: 15:05~15:09 사이 수동 1계약 진입 → 15:10 관측.
  **정상 판정**: `[ForceExitPass] 15:10 경과 분봉 — STEP 8 청산 감시 평가` →
  `[TimeExit] 15:10 강제 청산 트리거` → `[ExitAttempt] 시간청산` 이 **15:10:00~15:10:05**에 출현하고,
  `[SchedForceExit] … 안전망 발동`(ERROR)은 **미출현**. `trades.exit_reason='15:10 강제청산'` 1행 생성.
  **실패 판정**: 15:11에 `[SchedForceExit]` ERROR가 뜨면 1차 경로가 여전히 죽은 것 → 즉시 재조사.
  **비용**: 왕복 수수료 1계약 약 1,600원(2026-08-14 실측 2계약 3,270원 기준).
  ⚠ 15:10까지 포지션을 들고 가는 것이므로 **모의투자 계좌에서만.**

- [ ] **F-1H 하트비트 1일차 확인** — 다음 거래일 `logs/*_SYSTEM.log`에
  `[SchedForceExit] 15:11 점검 … bar_pass=N회 → 청산 대상 없음(정상)` **1건** 출현 확인.
  `bar_pass=0`이면 F-1 경로가 호출되지 않은 것(회귀) — 유닛테스트가 통과해도 라이브에서
  `_on_candle_closed`가 15:10 이후 아예 안 불릴 가능성(봉 공급 중단)이 남는다.
  같은 날 수집기 §11 적신호 6번이 **사라졌는지**도 함께 확인(F-2 판정 교체 검증).

- [ ] **F-4M 스키마 마이그레이션 1일차 확인** — 다음 기동 후
  `PRAGMA table_info(ensemble_decisions)`에 `entry_block_axes`·`health_preblock` 존재 확인 +
  당일 행에 값이 실제로 채워지는지(전 행 NULL이면 배선 실패).
  ⚠ **471차 이전 행의 NULL은 "미측정"** — 0(미발화)으로 읽지 말 것(계측 4원칙 ②).

### 잔여 — 계획 범위 밖이라 이번에 손대지 않은 것

- [x] **F-9 `entry_mode` 예외 폴백이 가장 관대한 값으로 조용히 떨어진다 (P2)** —
  ✅ **2026-08-14 471차 후속4 커밋 `7284b95`.** `_read_entry_mode()` 헬퍼로 분리 +
  `ensemble_decisions.entry_mode_fallback INTEGER` 추가. 로그는 **상태 변화 시에만**
  (폴백 진입 WARNING 1회 / 복구 INFO 1회 — 매분 찍으면 370줄/일).
  대시보드 부재와 조회 예외를 **다른 사유**로 구분한다.
  `tests/test_471_entry_mode_fallback.py`(24항목) 통과.
  ⚠ 다음 기동 후 **F-4M에 이 컬럼도 함께 확인**할 것 — 전 행 0이 정상(폴백 미발생),
  전 행 NULL이면 배선 실패다.
  ~~(원 등록 내용)~~
  `main.py:8277~8287`(471차 이후 행번 이동). 대시보드 조회 실패 시 `entry_mode="manual"`
  (= A·B·C 전 등급 허용)로 폴백하는데 **로그가 없고**, 정상 설정값도 `manual`이라
  폴백 발생분과 구분이 불가능하다(DB 실측 2026-07-01~: manual 11,590행 / hybrid 35행).
  **근거**: 리포트 P2 1-5. 계측 4원칙 ④(폴백 가시화).
  **조치**: ① 예외 시 WARNING 1줄 + ② `ensemble_decisions.entry_mode_fallback`(0/1) 또는
  기존 `entry_block_axes`에 `entry_mode_fallback` 축 추가(F-4 인프라 재사용이 더 싸다).
  ⚠ 리포트 §2 Fix 계획(F-1~F-4)에 없어 471차 범위 밖이었다 — **누락이 아니라 미착수.**

- [ ] **G-1 사이징 축소 원인을 구조체로 저장** — **선행 F-3 충족됨**(`8be4048`).
  이제 착수 가능하다. `binding_gate` 키 이름은 F-3이 로그에 쓴 것과 동일하게 맞출 것
  (`_quality_mults`의 키 그대로 — meta/tox/exec/hurst/pre_retrain).

```

</details>

### dev_memory/CURRENT_STATE.md — 521.7KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 3. 재시작 직후 restored/live 분리
### 4. 중패널 `동적 피처 (SHAP)` 상태
### 5. 오늘 확인된 startup 이슈와 현재 최종 블로커
## 2026-05-22 (82차) — Micro Regime Warmup UI
### 배경
### 현재 상태
### 구현 파일 (82차)
### 다음 확인 사항
```

_(참고용 — 필요하면 직접 열 것)_

### dev_memory/SESSION_LOG.md — 576.7KB · 마지막 갱신 2026-08-12 18:40

최근 헤딩 8개:
```
## 2026-07-08 (304차 — 진입관리 탭 UI 정리: 원신호/실행신호 폭 축소+차단사유/레짐 이전, 상태스트립·자격현황 카드 제거, 방향인디케이터 카드 축소)
### 구현
### 검증
## 2026-07-08 (304차 후속 — daily_close() 백그라운드 스레드 Qt 위젯 직접조작으로 인한 access violation 크래시 루프 수정)
### 실측한 증상
### 원인 규명
### 구현
### 검증
```

_(참고용 — 필요하면 직접 열 것)_

## 9. 당일 JSON/JSONL 산출물

(없음)

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 29개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260814-점검리포트-post.md` | 46.0KB | 08-14 16:37 |
| `docs/정기점검/매일점검/evidence_MW0601-20260814_post.md` | 68.9KB | 08-14 16:23 |
| `docs/정기점검/매일점검/evidence_MW0601-20260814_pre_1622.md` | 65.8KB | 08-14 16:22 |
| `docs/정기점검/매일점검/MW0601-20260814-점검리포트-intra.md` | 41.2KB | 08-14 12:40 |
| `docs/정기점검/매일점검/evidence_MW0601-20260814_intra.md` | 61.2KB | 08-14 12:27 |
| `docs/정기점검/매일점검/MW0601-20260814-점검리포트-pre.md` | 31.4KB | 08-14 09:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260814_pre.md` | 47.8KB | 08-14 09:00 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 12.2KB | 08-14 07:39 |

### `docs/정기점검/금요일점검` — 51개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260814.md` | 163.4KB | 08-14 15:49 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260814.json` | 83.5KB | 08-14 15:49 |
| `docs/정기점검/금요일점검/MW0602/exit_expectancy_map_20260810.md` | 1.8KB | 08-14 07:47 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. `logs/20260817_LEARNING.log`: **축퇴** 8건(표본)
7. 미커밋 변경 452건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260817*.log` (Windows) / `grep 강제청산 logs/*20260817*.log`*