# 미륵이 증거 다이제스트 — 2026-09-08 / PRE

- 생성 2026-09-08 09:00:47 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/modest-sweet-hawking/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260908` · `2026-09-08` · `260908` · `0908`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260908.log` | 125B | 09-08 08:40 |
| `freeze_sentinel_alert_{DATE}.txt` | 1 | `data/freeze_sentinel_alert_20260908.txt` | 702B | 09-08 09:00 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260908.log` | 842B | 09-08 09:00 |
| `launcher_{DATE}_084002_29245.log` | 1 | `logs/Mireuk_batch/launcher_20260908_084002_29245.log` | 1.7KB | 09-08 08:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260908_DATA.log` | 0B | 09-08 08:40 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260908_DEBUG.log` | 0B | 09-08 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260908_HEALTH.log` | 0B | 09-08 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260908_HOGA.log` | 0B | 09-08 08:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260908_LEARNING.log` | 52.9KB | 09-08 08:41 |
| `{DATE}_MICRO.log` | 1 | `logs/20260908_MICRO.log` | 0B | 09-08 08:40 |
| `{DATE}_PROBE.log` | 1 | `logs/20260908_PROBE.log` | 0B | 09-08 08:40 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260908_SIGNAL.log` | 1.5KB | 09-08 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260908_SYSTEM.log` | 1.3KB | 09-08 08:41 |
| `{DATE}_TRADE.log` | 1 | `logs/20260908_TRADE.log` | 167B | 09-08 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260908_WARN.log` | 206B | 09-08 08:41 |

## 2. 코드·커밋 상태

- HEAD `698c4ae` · 브랜치 `v9-dev` · 미커밋 549건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
 M CLAUDE.md
 M INSTALL.bat
 M LAUNCH_API.bat
 M MIREUK_DAILYCHECK_HANDOFF.md
 M ROADMAP.md
 M SETUP_GUIDE.md
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M backtest/param_optimizer.py
 M backtest/slippage_simulator.py
 M backtest/transaction_cost.py
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
… 외 509건
```

**당일(2026-09-08) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
698c4ae [MW0601] 542차 후속: dev 적응 이식 완료 기록
8e04770 [MW0601] 542차 후속: dev 이식 판단 기록 — 수동 맥점 버튼은 보류
a21e270 [MW0601] 542차: 수동 맥점 산출 버튼 (관측 전용, 매매정책 무변경)
91d99da [MW0601] 534차 후속: 첫 라이브 맥점 산출 점검 — 계측 결손 5건 (매매정책 무변경)
3111e4b [MW0601] 542차 곁가지: 540차 GP 교차 피처 NameError — feature_builder 임포트 누락
f2343d8 [MW0601] 541차 후속: 판정기 테스트 — 런타임 DB 부재 시 스킵
3f2b3c6 [MW0601] 541차: GP 교차 채널 판정기 배선 (기록 전용, 매매정책 무변경)
5a5fec1 [MW0601] 540차: GOLDEN POWER 교차 — 사전등록 2채널 배선 (기록 전용, 매매정책 무변경)
050241e [MW0601] 539차: ATR 진입 하한(ATR_MIN_ENTRY) 26주 WFA 재검증 편입 (매매정책 무변경)
308a45a [MW0601] 538차 후속: 0907 장후 점검 산출물 + 자동조치 기록
631735c [MW0601] 538차: 장후 자동조치 — 날짜전환 계측(G-1 + F-1 보강) · SKILL.md 확정판정 정합성 게이트(G-3)
732953d [MW0601] 537차: py310_64 BLAS 즉사 — 부트스트랩 적용 누락 수정 (매매정책 무변경)
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
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
| `FUTURES_COMMISSION_RATE` | `_BROKER_SPEC["one_way_commission_rate"]` | `_BROKER_SPEC["one_way_commission_rate"]` | 일치 | 495차 후속 — 로그인 채널 감지로 **파생**. 숫자 리터럴로 되돌아가면 회귀(2026-05-11~08-25 6개월간 1/6.54 사고). 실제 요율은 채널… |
| `FUTURES_COMMISSION_RATE_EFFECTIVE_FROM` | `_BROKER_SPEC["effective_from"]` | `_BROKER_SPEC["effective_from"]` | 일치 | 시계열 불연속 경계 — 이 날짜 앞뒤 손익 직접 비교 금지의 근거(461차 mdd_pct 유형) |
| `COST_MODEL_COMMISSION_RATE` | `0.000015` | `0.000015` | 일치 | 캠페인·섀도 계측 전용 요율. 라이브와 **의도적으로 갈라져 있다**(493차 F-3 핀). 주간회의 승인 시 라이브와 같은 값으로 교체 — 그때 이 기대값도 … |
| `COST_MODEL_COMMISSION_RATE_PINNED` | `True` | `True` | 일치 | 라이브와 계측이 갈린 상태임을 매일 명시. 승인 교체 후에도 True면 그것이 이상 |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

_이 브랜치(`v9-dev`) 범위 밖 **5건** — 표에서 제외했다(계측 4원칙 ③): `MODEL_LABEL_STATE_UNLOCK_ENABLED`(→dev), `PRE_RETRAIN_DONE_BY_EOD_ENABLED`(→dev), `ZONE_ENTRY_BAN_ENFORCE`(→dev), `ZONE_ENTRY_BAN_SHADOW_ENABLED`(→dev), `PIPE_LATENCY_EXCLUDE_MODEL_SWAP`(→dev)._
> 제외는 "없어도 된다"가 아니라 "이 브랜치에는 기능 자체가 없다"는 뜻이다. 이식 여부는 별개 안건이며 주간회의에서 정한다.

### 차단 게이트 전수 인벤토리 — 34개 중 **9개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FREEZE_SENTINEL_KILL_ENABLED` | False | 기능토글 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `TICKUI_TRACE_ENABLED` | False | 기능토글 |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | 기록됨 |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
| `DAILY_CLOSE_FORCE_EXIT_ENABLED` | True | — |
| `FORCE_FLAT_GUARD_ENABLED` | True | — |
| `FREEZE_SENTINEL_ENABLED` | True | — |
| `FREEZE_WATCHDOG_ENABLED` | True | — |
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
| `MAIN_STALL_TRACEBACK_ENABLED` | True | — |
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260908_HOGA.log` 0B — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/freeze_sentinel_alert_20260908.txt`** — 702B · 09-08 09:00:25
```
[FreezeSentinel] 2026-09-08 09:00:25 CRITICAL
  라이브 프로세스 동결 — 측정 가능한 신호 2종이 전부 300s 이상 정체다. 프로세스는 살아 있을 수 있으나 아무 일도 하지 않는다 (런처 재기동도 걸리지 않는다)
  · heartbeat        **미측정** (파일 없음 또는 파싱 실패)
  · crash_fault[TS]  39669s 전 (임계 300s) — 정체
  · SYSTEM.log       1157s 전 (임계 300s) — 정체
  · _exit_normally   **미측정**(플래그 없음/읽기 실패) — 동결 판정 유지
  · shutdown_normal  **미측정**(마커 없음) — 동결 판정 유지
  · daily_close_done **미측정**(마커 없음) — 동결 판정 유지
```

### `logs/20260908_TRADE.log` — 167B · 2행 · 최종 08:41:06

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-08 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-08 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-08 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260908_WARN.log` — 206B · 1행 · 최종 08:41:11

- 형식 평문 · 시각 인식 1행 · WARNING=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA
  …
2026-09-08 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 1 | 08:41:11 | 08:41:11 | _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA |

**채널** — `SYSTEM`×1

**컴포넌트 상위 15** — `LiveDBG`×1

### `logs/20260908_SYSTEM.log` — 1.3KB · 12행 · 최종 08:41:08

- 형식 평문 · 시각 인식 12행 · INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:35 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=23044 | 행감지=30s all_threads=True
2026-09-08 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-08 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-08 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-08 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-07) 종가 버퍼 로드: 384봉
  …
2026-09-08 08:41:07 [INFO] SYSTEM: [StateRecon] regime_fingerprint.json: 코드 CORE cvd_delta_norm,ofi_pressure,vwap_position 와 일치 (저장일=2026-09-07 15:53:50)
2026-09-08 08:41:07 [INFO] SYSTEM: [AnalysisRestore] live_corr=0 restored_corr=yes live_shap=240 live_ready=no shap_features=8 vp_bars=60 fp_live=5000
2026-09-08 08:41:08 [INFO] SYSTEM: ============================================================
2026-09-08 08:41:08 [INFO] SYSTEM: 미륵이 — KOSPI 200 선물 방향 예측 시스템 시작
2026-09-08 08:41:08 [INFO] SYSTEM: ============================================================
```

</details>

**채널** — `SYSTEM`×12

**컴포넌트 상위 15** — `SYSTEM`×4, `System`×2, `FaultHandler`×1, `FeatureBuilder`×1, `Calib`×1, `Calibration`×1, `StateRecon`×1, `AnalysisRestore`×1

### `logs/20260908_SIGNAL.log` — 1.5KB · 17행 · 최종 09:00:03

- 형식 평문 · 시각 인식 17행 · INFO=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
  …
2026-09-08 08:40:51 [INFO] SIGNAL: [Model] 30m 로드 성공
2026-09-08 08:40:52 [INFO] SIGNAL: [EnsembleGater] 저장된 가중치 복원: C:\Users\82108\PycharmProjects\futures\data\ensemble_gater_weights.json
2026-09-08 08:41:03 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-08 08:45:03 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → PRE_MARKET: 선물 프리장 — 진입 불허, scaler warmup 전용
2026-09-08 09:00:03 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**채널** — `SIGNAL`×17

**컴포넌트 상위 15** — `DynMC`×7, `Model`×6, `TimeRouter`×3, `EnsembleGater`×1

### `logs/20260908_LEARNING.log` — 52.9KB · 296행 · 최종 08:41:07

- 형식 평문 · 시각 인식 296행 · WARNING=147, INFO=149

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2888 < conf_floor=0.3300 (span=0.00234 auc=0.639 out_max=0.2888, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00009 auc=0.506 out_max=0.2875 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00011 auc=0.505 out_max=0.3218 (기준 auc<0.53 and span<0.020, 기저율=0.3217 n=115) → 보정 미적용, raw 통과
  …
2026-09-08 08:41:01 [INFO] LEARNING: [Calibration] 보정기 복원 완료 (n=888 method=platt fitted=True degenerate=False unreachable=False span=0.00630 auc=0.550 out_max=0.3479)
2026-09-08 08:41:01 [INFO] LEARNING: [Consolidator] 구 포맷 이력 1개 구간 폐기(풀링 새로 시작)
2026-09-08 08:41:01 [INFO] LEARNING: [Consolidator] 패널티 이력 로드: {'CLOSE_VOLATILE': 0.0, 'OPEN_VOLATILE': 0.0, 'GAP_OPEN': 0.0, 'OTHER': 0.0, 'STABLE_TREND': 0.0, 'LUNCH_RECOVERY': 0.0, 'PRE_MARKET': 0.0}
2026-09-08 08:41:01 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=SATURATED_MAX
2026-09-08 08:41:07 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=0개 | 교체후보=2개 | CORE안전=⚠️
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 147 | 08:40:52 | 08:41:01 | 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제] |

**채널** — `LEARNING`×296

**컴포넌트 상위 15** — `Calibration`×289, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1

### `logs/Mireuk_batch/launcher_20260908_084002_29245.log` — 1.7KB · 28행 · 최종 08:40:25

- 형식 평문 · 시각 인식 0행 · INFO=11, PLAIN=17

<details><summary>첫 5행 / 끝 5행</summary>

```
============================================================
Mireuk (KOSPI 200 Futures Auto Trader)
Broker : cybos
Launch : 20260908_084002
Log    : C:\Users\82108\PycharmProjects\futures\logs\Mireuk_batch\launcher_20260908_084002_29245.log
  …
[GUARD] 기존 main.py 프로세스 체크...
[GUARD] 기존 main.py 없음 -- 단일 인스턴스 확인.
[GUARD-FLAT] 15:12 FLAT 가드 사이드카 기동 (별도 프로세스, 알림 전용)
[SENTINEL] 동결 센티넬 FZ-2 사이드카 기동 (별도 프로세스, 알림 전용)
[INFO] WORKDIR=C:\Users\82108\PycharmProjects\futures  PY32=C:\Users\82108\anaconda3\envs\py37_32\python.exe  BROKER=cybos
```

</details>

**컴포넌트 상위 15** — `-`×17, `OK`×3, `GUARD`×2, `Broker`×1, `Launch`×1, `Log`×1, `RECHECK`×1, `GUARD-FLAT`×1, `SENTINEL`×1

### `logs/freeze_sentinel_20260908.log` — 842B · 17행 · 최종 09:00:25

- 형식 평문 · 시각 인식 3행 · CRITICAL=2, PLAIN=15

<details><summary>첫 5행 / 끝 5행</summary>

```
[FreezeSentinel] 2026-09-08 08:40:25 ARMED pid=26852 창=09:00~16:30 정지임계=300s 주기=60s (알림 전용 — 하드 종료 없음)
[FreezeSentinel] 2026-09-08 09:00:25 CRITICAL
라이브 프로세스 동결 — 측정 가능한 신호 2종이 전부 300s 이상 정체다. 프로세스는 살아 있을 수 있으나 아무 일도 하지 않는다 (런처 재기동도 걸리지 않는다)
· heartbeat        **미측정** (파일 없음 또는 파싱 실패)
· crash_fault[TS]  39669s 전 (임계 300s) — 정체
  …
· crash_fault[TS]  39729s 전 (임계 300s) — 정체
· SYSTEM.log       1217s 전 (임계 300s) — 정체
· _exit_normally   **미측정**(플래그 없음/읽기 실패) — 동결 판정 유지
· shutdown_normal  **미측정**(마커 없음) — 동결 판정 유지
· daily_close_done **미측정**(마커 없음) — 동결 판정 유지
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `FreezeSentinel` | 2 | 09:00:25 | 09:01:25 | [FreezeSentinel] 2026-09-08 09:00:25 CRITICAL |

<details><summary>CRITICAL/FreezeSentinel 원문 2건</summary>

```
[FreezeSentinel] 2026-09-08 09:00:25 CRITICAL
[FreezeSentinel] 2026-09-08 09:01:25 CRITICAL (수동 실행 — 마커 미기록)
```

</details>

**컴포넌트 상위 15** — `-`×12, `FreezeSentinel`×3, `TS`×2

### `logs/force_flat_guard_20260908.log` — 125B · 1행 · 최종 08:40:25

- 형식 평문 · 시각 인식 1행 · PLAIN=1

<details><summary>첫 5행 / 끝 5행</summary>

```
[ForceFlatGuard] 2026-09-08 08:40:25 ARMED pid=23064 판정예정=15:12 정지임계=180s (알림 전용 — 주문 없음)
  …
[ForceFlatGuard] 2026-09-08 08:40:25 ARMED pid=23064 판정예정=15:12 정지임계=180s (알림 전용 — 주문 없음)
```

</details>

**컴포넌트 상위 15** — `ForceFlatGuard`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 1건 · 최대 2219ms · 5초 초과 0건

상위 — 2219ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260908_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:11 2026-09-08 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA
```

### `logs/20260908_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
```

### `logs/20260908_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2888 < conf_floor=0.3300 (span=0.00234 auc=0.639 out_max=0.2888, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00009 auc=0.506 out_max=0.2875 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00011 auc=0.505 out_max=0.3218 (기준 auc<0.53 and span<0.020, 기저율=0.3217 n=115) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260908_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260908_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 1 | 08:41:11 [WARNING] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band… |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260908_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 12 | 08:40:35 [INFO] 활성화 | file=logs\crash_fault.log PID=23044 | 행감지=30s all_threads=True |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260908_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:40:31 [INFO] 기동 복원: OPEN_VOLATILE  0.600 → 0.410 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:00:03 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 1 | 09:00:03 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260907 | 21:59 | 로그 본문 |
| 20260906 | 20:39 | 로그 본문 |
| 20260904 | 17:33 | 로그 본문 |
| 20260903 | 15:40 | 로그 본문 |
| 20260902 | 15:40 | 로그 본문 |
| **중앙값** | **17:33** | 기준선 |
| **오늘 20260908** | **08:41** | 로그 본문 |

- 델타 **-532분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.8MB · 마지막 갱신 2026-09-07 20:32

최근 헤딩 8개:
```
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 자동조치 범위 밖으로 남긴 것
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 걸려야 하는데 걸리지 않았다.
왜 안 걸리는지는 **아직 미확정**이다(디스크에 이미 마커가 없었을 가능성 · 로그 레벨 ·
프로세스 간 파일 경합 등). 즉 "계측이 이 경로를 못 잡는다"는 535차의 설명 자체가
코드로 확인된 적이 없다.

### 결정

**원인을 고치지 않고 계측만 넣는다.** F-1 본체(마커 이어받기)는 사용자 승인 대기
(0907 리포트 사용자 조치 3)이므로 자동조치 범위 밖이다.

`strategy/runtime/session_recovery_service.py`:
- `_MARKER_KEYS` 클래스 상수 신설(`main.py:_SESSION_STATE_MARKER_KEYS` 와 동일해야 하며
  테스트가 소스 대조로 고정)
- `increment_session()` 날짜 전환 분기에서 전환 전 dict 를 `prev` 로 잡고
  `_log_session_rollover(prev, data)` 호출
- `_log_session_rollover()` 신설 — `[SessionRollover]` INFO(이어받은 키·버려진 키 **양쪽**)
  + 마커가 버려지면 `[SessionStateDrop]` WARNING(호출부 명시)

`.claude/skills/mireuk-daily-check/SKILL.md` 함정①에 절 추가(G-3) —
「확정 판정은 사전등록된 확인 수단을 **전부** 충족해야 한다」. rev 갱신.

### Why

- **계측 4원칙 ⑤(대사는 모든 축)**: 사라진 키만 남기면 "무엇이 살아남았는가"를 알 수 없다.
  이어받은 키와 버려진 키를 같은 줄에 둬야 다음 아침 로그 한 줄로 판정이 갈린다.
- **계측 4원칙 ④(폴백 가시화)**: `_read_session_state()` 가 읽기에 실패하면 **오늘 날짜**를
  담은 기본 dict 를 돌려줘 이 분기 자체를 타지 않는다 — 그 사각지대는 코드 주석에
  명시했다. 읽기 폴백을 바꾸는 것은 **동작 변경**이라 이번 범위 밖이다(미해소 잔여분).
- **F-17 전례**: 로그는 모듈 로거(`logger`)로만 낸다. `log_manager` 로 WARNING 을 내면
  `exceptions_10m` 에 합산돼 헬스 degraded 를 자체 유발한다. 테스트가 **호출 형태**로
  검사한다(주석·독스트링의 언급은 통과시킨다).
- **313차 원칙의 확장**: G-3 는 "사전등록 기준을 사후에 임의로 재해석하지 않는다"를
  표본 크기 축뿐 아니라 **판정 수단 정합성** 축으로 넓힌 것이다.

### How to apply

- 다음 기동(09-08 아침)부터 `[SessionRollover]` 가 매일 한 줄 남는다.
  「새로 초기화된 키」에 `p8_last_success_date`·`eod_retrain_ok_date` 가 있으면
  **F-1 가설 확정**, 없으면 원인은 다른 곳이다.
- `[SessionStateDrop]` 이 이 경로에서 나오기 시작하면 532차 계측의 사각지대가
  실증된 것이므로, 그 사실을 1-4 판정에 반영하고 F-1 적용 승인을 받는다.
- 매매 정책·게이트·주문 경로 **무변경**. 쓰는 dict 가 계측 도입 전과 완전 동일함을
  `tests/test_538_*::test_written_state_is_unchanged_by_instrumentation` 이 고정한다
  — 이 테스트가 깨지면 F-1 이 승인 없이 배포된 것이다.

### 검증

- `tests/test_538_session_rollover_instrumentation.py` 9건 전부 통과
  (라이브 반영 0 불변식 2건 · 소스 규약 2건 포함)
- 전체 스위트 1,241 passed · 3 failed · 1 skipped · 4 xfailed (542s).
  실패 3건은 전량 기존 실패(`test_477 step9 placeholders` · `test_483 fuoption 사본 대조` ·
  `test_504 unfiltered_view`)로 09-04 자동조치 기록의 목록과 동일하며 이번 변경 무관.
- 커밋 `631735c`.

### 자동조치 범위 밖으로 남긴 것

- **F-1 본체** — 사용자 승인 대기(리포트 사용자 조치 3)
- **F-2**(정체불명 외부 진입 원인) — 조사 전용, 변경 파일 없음, 사용자 확인 대기 5거래일째
- **G-2**(외부 진입 경보 격상) — 리포트가 "등급 분류는 주간회의에서 확인" + 임계는
  "다음 26주 주기에 확정"으로 유보. C등급 처리, `NEXT_TODO` 538-3 등록
- 사용자 조치 2(git lock)·4(BLAS 커밋)는 0t-E 시점에 이미 해소·완료

### 병행 세션

이 세션이 도는 동안 **539차 세션(ATR 진입 하한 26주 WFA 편입)**이 같은 저장소에서
작업 중이었다(`CLAUDE.md`·`scripts/atr_min_entry_recalibration.py`·`tests/test_539_*`).
그 경로들은 건드리지 않았고 커밋에도 넣지 않았다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · 마지막 갱신 2026-09-07 21:26

최근 헤딩 8개:
```
### 남은 것
## 2026-09-04 (MW0601 530차 — 장전 점검)
## 2026-09-04 (MW0601 531차 — 장중 점검)
## 2026-09-04 (MW0601 532차 — 장후 점검)
## 2026-09-04 (MW0601 532차 후속 — 장후 자동조치)
## 2026-09-07 (MW0601 536차 — 장중 점검)
## 2026-09-07 (MW0601 537차 — 장후 점검, 종합 완성본)
## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)
```

미완료 체크박스 **2494건** (끝에서 30건)
```
- [ ] **529-H** 처리군 거래일 25일 도달 시 A 재판정 → `SOFT_DEMOTE_CANDIDATE`면 주간회의 상정(승격 형태는 확정됨).
- [ ] **530-1 / F-1 (P1, 격상)** `data/session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`
- [ ] **530-2 / G-1 (P2)** `_write_session_state()`가 실제로 기록하는 키 목록 + 파일 mtime을 매 호출마다
- [ ] **O-p1** `[ConfFloorGuard] 자동진입 하한 도달 불가`(09:00:00, 보정기 출력상한 0.3479 < 필요 0.4230)
- [ ] **529-2 재확인(오늘 장후)** 스윙 위치 피처 7키 첫 라이브 적재 — `swing_ready_60m` True 비율(개장
- [ ] **531-1 / F-2 (P0, 최우선)** 정체불명 외부 진입 오늘 47건/50계약(-348,986원), 20/21
- [ ] **531-2 (P2, 고도화)** `HealthPolicy`의 `exceptions_10m` 집계에 예외 유형 태그 추가
- [ ] **531-3 (P1)** 1-3(ConfFloorGuard 3거래일 연속) — 장후 `predictions` 테이블 09:00~12:28
- [ ] **532-1 (P0, 최우선 지속)** 정체불명 외부 진입 — 오늘 최종 62건/66계약. 사용자에게
- [ ] **532-2 (P2, 고도화)** G-3 — EOD 마감 로그에 그날 `min_conf`(DynMC 산출) 시간대별
- [ ] **532-3 (C등급, 사용자 승인 필요)** F-10 적용 승인 여부 — 사전등록 기준(10거래일 중
- [ ] **532-4 (P2)** F-15(외부진입을 브로커 net 판정 경로에서 분리, 주간회의 안건) 재확인
- [ ] **532-5 (P1 · 승인 대기 / F-1 수정안)** `session_recovery_service.py:120-129
- [ ] **532-6 (P1 · 회귀 테스트 복구)** `tests/test_477_f1_f5_saturation_psi.py::
- [ ] **532-7 (관측 예정 · 09-05 EOD)** `[DynMCDaily]` 가 실제 마감 경로에서 나오는지
- [ ] **532-8 (사용자 조치)** 미륵이 **재기동 필요** — G-1·G-2·G-3 전부 실행 중
- [ ] **532-9 (P2 · 재발방지 / 자가유발)** 커밋 `3c2f17c` 메시지 첫 줄·마지막 줄에
- [ ] **536-1 (P0, 최우선 지속)** 정체불명 외부 진입 — 09-01(47건/50계약)·09-04(최종
- [ ] **536-2 (P2, 고도화 제안)** G-2 — `[ExternalEntry]` 누적 건수 임계 초과 시
- [ ] **536-3 (사용자 조치)** `.git/index.lock` 여전히 미회수 — 이 세션도
- [ ] **537-2 (P2, 신규)** 이상점 1-4 — F-1("session_state 마커 유실") "확정" 판정이
- [ ] **537-3 (P2, 문서 개선 제안)** SKILL.md 함정①(판정≠결정) 게이트에 "사전등록된
- [ ] **537-6 (사용자 조치, 지속)** `.git/index.lock` 여전히 미회수(09:01 생성,
- [ ] **537-7 (참고, 이 세션 소관 아님)** 병행 세션이 오늘 저녁(15:54~16:14) py310_64
- [ ] **537-8 (P2, 정책 제안 — 사용자 지시 시)** G-4 — 모의투자 병행 수동거래를
- [ ] **538-3** (C등급 · 승인 대기) G-2 — 정체불명 외부 진입 누적 건수 단계적 경보 격상.
- [ ] **538-4** (승인 대기) F-1 본체 — `increment_session()` 이 완료 마커 2종을 이어받게
- [ ] **538-5** 09-08 장전 관측(O-t5 대응) — 기동 로그에 `[SessionRollover]` 한 줄이
- [ ] **538-6** 기존 실패 3건 잔존 — `test_477::test_step9_batch_placeholders_match_params`
- [ ] **538-7** 미륵이 재기동 필요 — 538-1 계측은 다음 기동부터 반영된다
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 `increment_session()` 새
      딕셔너리 구성 분기에 계측을 직접 추가한 뒤(G-3), 09-08 기동에서 발동 확인 후
      적용하는 순서로 변경 제안. 상세: `DECISION_LOG.md` 2026-09-07(537차) 항목 1.
- [ ] **537-3 (P2, 문서 개선 제안)** SKILL.md 함정①(판정≠결정) 게이트에 "사전등록된
      확인 수단이 여러 개면 전부 충족 확인, 하나라도 불일치면 '확정'이 아니라
      '유력 가설(정합성 미확인)'로 낮춰 쓴다" 문구 추가 — 다음 SKILL.md 개정 시 반영.
- [x] **537-4** P5-06·P5-07(누적대장) 표본 갱신 완료 — P5-06 19포지션/5거래일
      (누계 −14,524,235원), P5-07 6건/3거래일. 둘 다 판정 보류(표본 미달) 상태 유지.
- [x] **537-5** O-i1·O-i2(장중 등록) → 판정 완료. O-t1~O-t5 신규 등록(리포트 §6 참조).
- [ ] **537-6 (사용자 조치, 지속)** `.git/index.lock` 여전히 미회수(09:01 생성,
      7.4시간+ 경과, 스테일 확정, 세션 내 회수 불가 재확인). Windows PC에서 직접
      `del .git\index.lock` 필요 — 3거래일째(535·536·537차 전부) 동일 요청.
- [ ] **537-7 (참고, 이 세션 소관 아님)** 병행 세션이 오늘 저녁(15:54~16:14) py310_64
      BLAS DLL 부트스트랩 결손(딥다이브: `MW0601-20260907-BLAS즉사-딥다이브.md`)을 찾아
      `main.py`·`retrain_intraday.py`·`utils/dll_bootstrap.py` 등에 예방 조치를 적용,
      16:32:40 `732953d`로 커밋 완료. 다음 장중 재학습에서 `[DLL]` 로그와 정상 완료
      확인 필요(O-t4).
- [ ] **537-8 (P2, 정책 제안 — 사용자 지시 시)** G-4 — 모의투자 병행 수동거래를
      "알려진 활동"으로 태깅해 `[ExternalEntry]` 심각도(현재 ERROR + Health CRITICAL)를
      낮추는 플래그(`MIREUK_MANUAL_TESTING_MODE`류) 검토. P5-09(외부/MANUAL 진입 실시간
      경보)와 겹치는 부분 있음 — 통합 여부는 다음 세션에서 정리. **실전 전환 전 반드시
      해제 확인**을 전환 체크리스트에 추가할 것. 선행조건: 사용자가 병행 테스트 종료
      예정 시점을 알려줘야 함.

## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)

- [x] **538-1** G-1 + F-1 보강 계측 — `increment_session()` 날짜 전환에
      `[SessionRollover]` INFO + 마커 소실 시 `[SessionStateDrop]` WARNING. 동작 무변경.
      (`strategy/runtime/session_recovery_service.py`, 커밋 `631735c`)
- [x] **538-2** G-3 — `SKILL.md` 함정①에 「확정 판정은 사전등록 확인 수단을 전부
      충족해야 한다」 절 추가 + rev 갱신
- [ ] **538-3** (C등급 · 승인 대기) G-2 — 정체불명 외부 진입 누적 건수 단계적 경보 격상.
      리포트가 "등급 분류는 주간회의에서 확인"이라 유보했고 임계는 "표본 5거래일로는
      확정 금지, 다음 26주 주기에 확정"이라 못박았다. **주간회의 안건**
- [ ] **538-4** (승인 대기) F-1 본체 — `increment_session()` 이 완료 마커 2종을 이어받게
      수정. **538-1 계측이 09-08 아침에 실제로 발동하는지 먼저 확인한 뒤** 적용할 것
      (0907 리포트 1-4 · 사용자 조치 3). 사후 완화 금지(458차 D6)
- [ ] **538-5** 09-08 장전 관측(O-t5 대응) — 기동 로그에 `[SessionRollover]` 한 줄이
      나오는지, 「새로 초기화된 키」에 `p8_last_success_date`·`eod_retrain_ok_date` 가
      있는지. **있으면 F-1 가설 확정 / 없으면 원인은 다른 곳**
- [ ] **538-6** 기존 실패 3건 잔존 — `test_477::test_step9_batch_placeholders_match_params`
      (532-6 승계) · `test_483::test_sibling_copy_matches_canonical[fuoption]` ·
      `test_504::test_unfiltered_view_keeps_broker_measurement`. 전부 이번 변경 무관
- [ ] **538-7** 미륵이 재기동 필요 — 538-1 계측은 다음 기동부터 반영된다

```

</details>

### dev_memory/CURRENT_STATE.md — 529.7KB · 마지막 갱신 2026-08-19 17:43

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

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-07 21:58:46**

| 키 | 값 | 수집 대상일(2026-09-08)과 일치 |
|---|---|---|
| `date` | 2026-09-07 | **아니오** |
| `p8_last_success_date` | 2026-09-07 | **아니오** |
| `eod_retrain_ok_date` | 2026-09-07 | **아니오** |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 115개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260907-점검리포트.md` | 95.0KB | 09-07 17:42 |
| `docs/정기점검/매일점검/MW0601-20260907-BLAS즉사-딥다이브.md` | 13.2KB | 09-07 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_post.md` | 91.6KB | 09-07 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_intra.md` | 77.5KB | 09-07 12:27 |
| `docs/정기점검/매일점검/MW0601-20260907-맥점계측-딥다이브.md` | 10.1KB | 09-07 09:14 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_pre.md` | 54.6KB | 09-07 09:01 |
| `docs/정기점검/매일점검/MW0601-20260904-점검리포트.md` | 83.0KB | 09-04 17:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_post.md` | 92.5KB | 09-04 16:19 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260904.json` | 2.9KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260904.md` | 4.9KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json` | 38.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md` | 31.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json` | 105.4KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md` | 185.3KB | 09-04 15:50 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/freeze_sentinel_20260908.log`: ERROR 이상 2건
2. `logs/20260908_LEARNING.log`: **축퇴** 8건(표본)
3. 미커밋 변경 549건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260908*.log` (Windows) / `grep 강제청산 logs/*20260908*.log`*