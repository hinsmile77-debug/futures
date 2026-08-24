# 미륵이 증거 다이제스트 — 2026-08-14 / PRE

- 생성 2026-08-14 09:00:33 KST · PC **MW0601** (`DeskTop-MW0601`)
- 리포 `/sessions/brave-confident-einstein/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260814` · `2026-08-14` · `260814` · `0814`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **12개** 파일 · 12개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_20710.log` | 1 | `logs/Mireuk_batch/launcher_20260814_084001_20710.log` | 45.8KB | 08-14 09:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260814_DATA.log` | 914B | 08-14 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260814_DEBUG.log` | 0B | 08-14 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260814_HEALTH.log` | 0B | 08-14 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260814_HOGA.log` | 1.5MB | 08-14 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260814_LEARNING.log` | 49.1KB | 08-14 08:58 |
| `{DATE}_MICRO.log` | 1 | `logs/20260814_MICRO.log` | 38.6KB | 08-14 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260814_PROBE.log` | 1.7KB | 08-14 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260814_SIGNAL.log` | 13.7KB | 08-14 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260814_SYSTEM.log` | 25.9KB | 08-14 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260814_TRADE.log` | 167B | 08-14 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260814_WARN.log` | 1.1KB | 08-14 08:55 |

## 2. 코드·커밋 상태

- HEAD `e8a56ea` · 브랜치 `v9-dev` · 미커밋 433건
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
… 외 393건
```

**당일(2026-08-14) 커밋**
```
e8a56ea [MW0602] 459차: F1 승패 집계 단위(레그→포지션) + F2 SHS CORE 미측정 분리
fe88f93 [MW0602] 460차: 공용 헬퍼 _spearman 동률 처리 버그 — 사본 2벌 정정 + 회귀테스트
f75ae87 [MW0602] 458차 후속: [40-B]·[49] 채널 구현 + 기대값 지도 — 손익원천이전 3종
ab5a103 [MW0602] 458차: 손익 원천 이전 제안서 — P7 딥다이브 (미승인, 라이브 무변경)
68d31a6 [MW0602] 457차: 모델 메타 사이드카 + GuardFair 유효성 판정 + ConstOut 재학습 스코프
8ef8878 [MW0602] 456차: ZeroDiag 오진 수정 + min_conf 완화하한 + JointGate 폴백 섀도
a581231 [MW0602] 469차: 일일 점검 스킬 — 승패 사후검증 편입 + 313차 방법론 확정 + 불변식 감시 누락 수정
```

**최근 커밋 12건**
```
e8a56ea [MW0602] 459차: F1 승패 집계 단위(레그→포지션) + F2 SHS CORE 미측정 분리
fe88f93 [MW0602] 460차: 공용 헬퍼 _spearman 동률 처리 버그 — 사본 2벌 정정 + 회귀테스트
f75ae87 [MW0602] 458차 후속: [40-B]·[49] 채널 구현 + 기대값 지도 — 손익원천이전 3종
ab5a103 [MW0602] 458차: 손익 원천 이전 제안서 — P7 딥다이브 (미승인, 라이브 무변경)
68d31a6 [MW0602] 457차: 모델 메타 사이드카 + GuardFair 유효성 판정 + ConstOut 재학습 스코프
8ef8878 [MW0602] 456차: ZeroDiag 오진 수정 + min_conf 완화하한 + JointGate 폴백 섀도
a581231 [MW0602] 469차: 일일 점검 스킬 — 승패 사후검증 편입 + 313차 방법론 확정 + 불변식 감시 누락 수정
6aeccac [MW0601] 461차 고도화: 퍼널 자기검증 + DB폴백 자동검출 + JointGateBlock 폴백비율 집계
0424f64 [MW0601] 461차 문서: 한시예외 4번째 항목 등록 + CB③ 임계 문구 정정
c68e7b4 [MW0601] 461차 후속: Live MDD 분모 정합(자본대비) + 거래0건 폴백 미측정 표기
36d1687 [MW0601] 461차: 진입 퍼널 등급상향 경로 누락 수정 + 증거 다이제스트 덮어쓰기 방지
4fae03d [MW0601] 459차: 일일 점검 스킬 MW0601 실측 정밀조정 — 태그 파싱 수정 + 거래일 요약 신설
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

_본문 미열람(설정): `20260814_HOGA.log` 1.5MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/9개 (중요도순). 제외: `launcher_20260814_084001_20710.log`_

### `logs/20260814_TRADE.log` — 167B · 2행 · 최종 08:41:12

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-14 08:41:12 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-14 08:41:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-14 08:41:12 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260814_WARN.log` — 1.1KB · 8행 · 최종 08:55:16

- 형식 평문 · 시각 인식 8행 · WARNING=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:15 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-14 08:41:15 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-14 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 156ms account=333044256
2026-08-14 08:41:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-14 08:41:21 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3375ms — live 중단 원인 분석용
  …
2026-08-14 08:41:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-14 08:41:21 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3375ms — live 중단 원인 분석용
2026-08-14 08:41:21 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
2026-08-14 08:55:16 [WARNING] SYSTEM: [Canary] scaler 노후=0h  z경고피처=19개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증
2026-08-14 08:55:16 [WARNING] SYSTEM: [Canary] z경고 폭증(19개 ≥ 12개) → 장전 scaler 재적합 시도 (08:58 전)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 6 | 08:41:15 | 08:41:21 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Canary` | 2 | 08:55:16 | 08:55:16 | scaler 노후=0h  z경고피처=19개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

**채널** — `SYSTEM`×8

**컴포넌트 상위 15** — `LiveDBG`×6, `Canary`×2

### `logs/20260814_SYSTEM.log` — 25.9KB · 208행 · 최종 09:00:31

- 형식 평문 · 시각 인식 202행 · INFO=202, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:45 [INFO] SYSTEM: [FaultHandler] 로테이션 — 9.5MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-08-14 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=4232 | 행감지=30s all_threads=True
2026-08-14 08:40:58 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-14 08:40:58 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-14 08:40:58 [INFO] SYSTEM: 미륵이 초기화
  …
2026-08-14 09:00:25 [INFO] SYSTEM: [TickUI] alive ticks=2840 code=A0569 close=1102.64
2026-08-14 09:00:29 [INFO] SYSTEM: [CybosRT-TICK] #2900 code=A0569 raw_time=90030 parsed=09:00:30 price=1101.42 vol=1 bid1=1101.20 ask1=1101.44 flag=49 side=BUY anchor=1/0
2026-08-14 09:00:31 [INFO] SYSTEM: [CybosRT-TICK] #3000 code=A0569 raw_time=90032 parsed=09:00:32 price=1100.96 vol=1 bid1=1100.72 ask1=1100.96 flag=49 side=BUY anchor=1/0
2026-08-14 09:00:34 [INFO] SYSTEM: [CybosRT-TICK] #3100 code=A0569 raw_time=90035 parsed=09:00:35 price=1100.00 vol=1 bid1=1100.00 ask1=1100.18 flag=50 side=SELL anchor=0/1
2026-08-14 09:00:36 [INFO] SYSTEM: [CybosRT-TICK] #3200 code=A0569 raw_time=90037 parsed=09:00:37 price=1100.70 vol=1 bid1=1100.56 ask1=1100.70 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×202

**컴포넌트 상위 15** — `CybosRT-TICK`×37, `CybosSub`×21, `System`×17, `TickUI`×16, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `-`×3, `EarlyWarmup`×3

### `logs/20260814_SIGNAL.log` — 13.7KB · 109행 · 최종 09:00:10

- 형식 평문 · 시각 인식 109행 · WARNING=18, INFO=91

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.416
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.441
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.428
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.420
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.424
  …
2026-08-14 08:55:16 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0658 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-14 08:55:16 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1480 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-14 08:55:16 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP  n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-08-14 08:58:58 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-08-14 09:00:10 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 18 | 08:45:16 | 08:48:01 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×109

**컴포넌트 상위 15** — `ScalerFloor`×66, `ScalerRefresh`×24, `DynMC`×7, `Model`×6, `TimeRouter`×3, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1

### `logs/20260814_LEARNING.log` — 49.1KB · 274행 · 최종 08:58:58

- 형식 평문 · 시각 인식 274행 · WARNING=133, INFO=141

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:59 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00034 auc=0.510 out_max=0.3915 (기준 auc<0.53 and span<0.020, 기저율=0.3913 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00037 auc=0.520 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3281 < conf_floor=0.3300 (span=0.00315 auc=0.573 out_max=0.3281, 기저율=0.3263 n=95) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-14 08:40:59 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3619 < conf_floor=0.3300 (n=100) → 보정 재적용
  …
2026-08-14 08:49:59 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-14 08:54:58 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-14 08:55:16 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=6241, ver=5)
2026-08-14 08:55:16 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-14 08:58:58 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 133 | 08:40:59 | 08:41:08 | 축퇴 감지 — span=0.00034 auc=0.510 out_max=0.3915 (기준 auc<0.53 and span<0.020, 기저율=0.3913 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제] |

**채널** — `LEARNING`×274

**컴포넌트 상위 15** — `Calibration`×260, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20260814_MICRO.log` — 38.6KB · 106행 · 최종 09:00:32

- 형식 평문 · 시각 인식 106행 · DEBUG=106

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:45:16 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1103.02/1 ask1=1103.54/1 mp={'microprice_tick': 1103.28, 'midprice_tick': 1103.28, 'depth_bias_tick': -0.1412} mlofi_tick=None queue=None
2026-08-14 08:45:16 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1103.00/1 ask1=1103.54/1 mp={'microprice_tick': 1103.27, 'midprice_tick': 1103.27, 'depth_bias_tick': -0.1253} mlofi_tick=-2.5333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-14 08:45:16 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1102.82/1 ask1=1103.54/1 mp={'microprice_tick': 1103.18, 'midprice_tick': 1103.18, 'depth_bias_tick': -0.0949} mlofi_tick=-2.6167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-14 08:45:16 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1102.82/1 ask1=1103.54/1 mp={'microprice_tick': 1103.18, 'midprice_tick': 1103.18, 'depth_bias_tick': -0.0949} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-08-14 08:45:16 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1102.70/1 ask1=1103.50/1 mp={'microprice_tick': 1103.1, 'midprice_tick': 1103.1, 'depth_bias_tick': -0.4016} mlofi_tick=-8.6 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
  …
2026-08-14 09:00:25 [DEBUG] MICRO: [MICRO-TICK] #6700 bid1=1102.28/1 ask1=1102.64/1 mp={'microprice_tick': 1102.46, 'midprice_tick': 1102.46, 'depth_bias_tick': -0.1387} mlofi_tick=5.7667 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-08-14 09:00:29 [DEBUG] MICRO: [MICRO-TICK] #6800 bid1=1100.50/1 ask1=1100.92/1 mp={'microprice_tick': 1100.71, 'midprice_tick': 1100.71, 'depth_bias_tick': 0.0} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-08-14 09:00:32 [DEBUG] MICRO: [MICRO-TICK] #6900 bid1=1100.12/2 ask1=1100.28/2 mp={'microprice_tick': 1100.2, 'midprice_tick': 1100.2, 'depth_bias_tick': 0.0522} mlofi_tick=6.9 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -0.…
2026-08-14 09:00:35 [DEBUG] MICRO: [MICRO-TICK] #7000 bid1=1099.60/1 ask1=1099.84/1 mp={'microprice_tick': 1099.72, 'midprice_tick': 1099.72, 'depth_bias_tick': 0.0874} mlofi_tick=1.0333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-08-14 09:00:38 [DEBUG] MICRO: [MICRO-TICK] #7100 bid1=1099.90/10 ask1=1100.00/4 mp={'microprice_tick': 1099.9714, 'midprice_tick': 1099.95, 'depth_bias_tick': 0.1784} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
```

</details>

**채널** — `MICRO`×106

**컴포넌트 상위 15** — `MICRO-TICK`×91, `MICRO-MINUTE`×15

### `logs/20260814_DATA.log` — 914B · 4행 · 최종 08:58:49

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:58:19 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=157334 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-14 08:58:19 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-14 08:58:49 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=157310 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-14 08:58:49 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
  …
2026-08-14 08:58:19 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=157334 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-14 08:58:19 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-14 08:58:49 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=157310 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-14 08:58:49 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
```

</details>

**채널** — `DATA`×4

**컴포넌트 상위 15** — `CybosInvestor`×4

### `logs/20260814_PROBE.log` — 1.7KB · 11행 · 최종 08:58:49

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:16 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-08-14 08:58:19 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-14 08:58:19 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-14 08:58:19 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-14 08:58:19 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-08-14 08:58:49 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-14 08:58:49 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-14 08:58:49 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-14 08:58:49 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-14 08:58:49 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:19 | 08:58:49 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

**채널** — `PROBE`×11

**컴포넌트 상위 15** — `CybosProbe`×10, `CybosInvestorProbe`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 1건 · 최대 2625ms · 5초 초과 0건

상위 — 2625ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260814_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:18 2026-08-14 08:41:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
```

### `logs/20260814_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.416
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.441
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.428
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.420
```

### `logs/20260814_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00034 auc=0.510 out_max=0.3915 (기준 auc<0.53 and span<0.020, 기저율=0.3913 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00037 auc=0.520 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3281 < conf_floor=0.3300 (span=0.00315 auc=0.573 out_max=0.3281, 기저율=0.3263 n=95) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3198 < conf_floor=0.3300 (span=0.00464 auc=0.631 out_max=0.3198, 기저율=0.3172 n=145) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260814_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:08 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:15 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:55:16 [WARNING] scaler 노후=0h  z경고피처=19개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:55:16 [WARNING] scaler 노후=0h  z경고피처=19개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 08:55

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:45 [INFO] 로테이션 — 9.5MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 102 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 72 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:16 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 47 | 08:49:59 [INFO] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 46 | 08:54:58 [INFO] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] ela… |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 🔴 [발견] 복원 조건이 구조적으로 충족 불가능하다 — 섀도가 배선돼 있지 않다 (신규)
### [갱신] 점검 인벤토리 — `documented_disabled_flags` 3 → 4
### [참고] 461차 3개 커밋 종료
## 2026-08-13 (MW0601 461차 고도화 — G-4 퍼널 자기검증 · G-5 DB폴백 자동검출 · G-6 폴백비율 집계)
### [신설] G-4 — 퍼널 자기검증. 같은 사실을 두 경로로 세서 어긋나면 그날 잡는다
### [신설] G-6 — JointGateBlock 무정보폴백 비율 자동 집계
### [신설] G-5 — 계측 4원칙 ④ 3번째 규약의 자동 검출 (DB 계층)
### [참고] 461차 커밋 4개
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
자동 집계

**File**: `utils/db_utils.py:fetch_daily_joint_gate_fallback()` · `daily_exporter.py`

460차 F-1이 *"매일 사람이 눈으로 세고 있다"* 고 지적한 값을 자동화했다. 출력:
`└ JointGateBlock 7건 (무정보폴백 6건 = 85.7%) [표본 13건 부족 — 판정보류]`

> 🔧 **[선행조건 정정] 460차 F-1을 기다릴 필요가 없었다 — 이미 배선돼 있다.**
> 리포트 §3 G-6은 선행 조건을 *"460차 F-1(`meta_fallback` 필드·컬럼 승격) 구현"* 으로
> 걸었으나, **420차가 `joint_gate_shadow.meta_size_fallback` 컬럼으로 이미 승격해뒀다**
> (1 = `learned["size_multiplier"] or 0.5` 폴백 발동). 리포트의 "함정 ①(이미 반영된
> 사안을 신규로 오인)"에 해당한다. F-1의 나머지(로그 문구·층화 판정)는 별개로 유효하다.

⚠ **폴백 여부를 meta 값으로 추정하지 않는다.** `meta_size == 0.50`으로 세면 "학습값이
우연히 0.50인 행"과 구분이 안 된다. 컬럼을 그대로 읽는다 — 2026-08-13 실측 7건 중 6건
**85.7%** 로 리포트의 수동 집계와 정확히 일치.
420차 이전 행은 NULL이라 **미계측으로 따로 센다**(계측 4원칙 ②).
`verdict_ready`(min_samples=20)가 False면 **판정문을 내지 않는다**(313차 소표본 원칙).

일자별 실측: 08-03 76.9%(n=26) · 08-06 77.8%(9) · 08-07 73.7%(19) · 08-11 100%(1) ·
**08-13 85.7%(7)**. 판정 표본(20)에 도달한 날은 08-03뿐이다.

### [신설] G-5 — 계측 4원칙 ④ 3번째 규약의 자동 검출 (DB 계층)

**File**: `tests/test_457_fallback_visibility.py`(3개 테스트 추가)

*"DB 컬럼에 폴백값을 쓸 때는 폴백 여부 플래그를 같은 행에 써라"* 는 457차부터
CLAUDE.md에 **문장으로는** 있었으나 자동 검출이 없었다. 기존 검사는 런타임 상태
(`getattr` 폴백)만 겨냥해 **스키마 계층이 사각지대**였고, 실제로 거기서 F-7 사고가 났다.

AST로 "컬럼 명시 INSERT + 파라미터의 폴백 리터럴(`x or 0.5` / `d.get(k, 0)`) +
플래그 컬럼 없음"을 잡는다. 전 리포 21건의 INSERT 중 **4건** 검출.

> 🔴 **함정: 런타임이 py37_32라 `ast.Constant`만 보면 0건이 나온다.**
> 처음 짰을 때 실제로 전 리포 0건이 나와 검출기가 죽은 줄 알았다. 3.7은 `ast.Str`·
> `ast.Num`·`ast.NameConstant`를 낸다. 양쪽 호환 헬퍼(`_ast_str`/`_ast_const`)를 뒀고,
> `n_inserts >= 10` 하한 assert로 **검출기가 다시 죽으면 테스트가 실패**하게 했다.

검출된 4건은 전부 검토 후 **고치지 않고 핀 고정**했다(`_DB_FALLBACK_PINNED`, 근거 필수).
이 검사의 값어치는 **새로 생기는 것**을 막는 데 있다 — `_CROSS_MODULE` 핀과 같은 취지:

| 지점 | 판단 근거 |
|---|---|
| `strategy_param_changes` | `.get(..,'')` — 빈 문자열은 눈에 보이는 '없음'. 행 존재 자체가 사실 |
| `strategy_regime_matrix` | **같은 행의 `trade_count`가 판별자** — 0이면 나머지 무의미함이 자명. 이름만 `*_measured`가 아님 |
| `scaler_daily` | 457차 G5가 `health` 계열은 이미 수정(docstring 명시). 남은 건 당일 집계 카운터 |
| `raw_candles` | 452차가 bid1/ask1/oi/buy_vol/sell_vol은 이미 무기본값화(451차 `program_*` 전례). OHLC는 '없으면 봉이 아니다' + 같은 행에 `bar_recovered` |

`test_db_fallback_pin_list_is_not_stale`이 **핀 목록이 굳는 것**도 막는다 —
고쳐진 항목이 목록에 남아 있으면 실패한다.

### [참고] 461차 커밋 4개

| 커밋 | 내용 | 해시 |
|---|---|---|
| ① | F-5 퍼널 등급상향 누락 + F-6 다이제스트 덮어쓰기 방지 | `36d1687` |
| ② | F-7 Live MDD 분모 정합 + 거래0건 폴백 가시화 | `c68e7b4` |
| ③ | F-4 한시예외 4번째 등재 + F-3 CB③ 문구 정정 | `0424f64` |
| ④ | G-4 퍼널 자기검증 + G-5 DB폴백 자동검출 + G-6 폴백비율 집계 | (본 커밋) |

미착수: F-1·F-2·F-8, 고도화 G-1·G-2·G-3·G-7~G-9.

```

</details>

### dev_memory/NEXT_TODO.md — 868.9KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### NEXT (고도화)
### 다음 거래일 관측 (판정 근거)
### 충족 근거 확보(완료 표기는 사용자 확인 후)
## 2026-08-13 (MW0601 461차 — 장후 점검) 신규 항목
### Fix
### 고도화
### 문서·운영
### 다음 거래일(2026-08-14) 관측 예정
```

미완료 체크박스 **1224건** (끝에서 30건)
```
- [ ] **SHAP 탭 호라이즌별 확장** — Phase C 호라이즌별 SHAP 계산 (현재 1m 기준만)
- [ ] `raw_features` DB 조회: `opt_chain_pcr`, `opt_gex_bn` 키 존재 여부 (미확인)
- [ ] **Phase D 재검증**: opt_chain_pcr/gex_bn/atm_* 4주 축적 확인 후 Walk-Forward 재실행
- [ ] **GBM retrain**: opt 피처 포함 첫 retrain → per-horizon pkl 생성 → 호라이즌별 모델 전환
- [ ] **Phase E**: SHAP Tracker 6개 호라이즌 확장 (shap_tracker.py horizon 컬럼 추가)
- [ ] **feat=118 vs managed=97 불일치** 해소: shap_feature_registry.json active_features 갱신 (opt_chain 포함)
- [ ] **Cybos Chejan `status` 필드 실측**
- [ ] **F-0 예약작업 `mireuk-postmarket-check` 트리거를 15:50 KST로 변경** — 현재 13:13에
- [ ] **F-1 JointGateBlock 무정보 폴백 플래그 분리 계측 (P1)** — MetaGate가
- [ ] **F-2 ConfFloorGuard 축퇴-우회 축 오탐 억제 (P1)** —
- [ ] **F-8 `spread_extreme_shadow` 섀도 계측 배선 (P2, 461차 신규 — F-4 복원의 선행조건)** —
- [ ] **G-1 `ReachabilityGuard` — "산술적 도달 불가" 조합을 게이트 체인 전체로 일반화** —
- [ ] **G-2 `HEALTH_DEGRADED_MIN_CONF = 0.62`의 현행 conf 스케일 정합성 재확인** —
- [ ] **G-3 수집기 적신호에서 `_tick_header` 블로킹과 `PipePerf total`을 분리** —
- [ ] **O-1 오늘 15:35 이후 장후 재점검** — `강제청산`·`daily_close_done`·`eod_retrain_done`
- [ ] **O-2 `[JointGateBlock 차단]` 건수와 `meta=` 분포** — 폴백(0.50) 비중이 오늘처럼 6/7이면
- [ ] **O-3 진입 건수 회복 여부** — 0건 2거래일 연속이면 진입0 딥다이브 절차 착수
- [ ] **O-4 `[ConfFloorGuard]` 경보 건수 vs out_max 초과 분봉 수** — 오늘 괴리(1 vs 140)가
- [ ] **O-5 `[Bias⚠] 5m` 종가 최종값 · SGD 50분 정확도** — 오늘 13:13 적중 23%(DN편향 63%) /
- [ ] **O-6 `WeightCollapse / Ensemble` 종가 비율** — 13:16 기준 106/268 = 39.6%로 CLAUDE.md
- [ ] **O-7 `_tick_header` 5초 초과 건수** — 오늘 9건(최대 11,625ms). 증가면 G-3 상향
- [ ] **404차 후속4 검증항목 "11:50~13:00 ConfFloorGuard WARNING 없음"** — 2026-08-13 실측
- [ ] **N-1 `[JointGateBlock 차단]` 중 `meta=0.50` 비율** — 3거래일 연속 80% 초과면 게이트 원인 확정.
- [ ] **N-2 진입 건수** — 0건이면 **2거래일 연속** → 진입0 딥다이브 절차 착수(460차 O-3 승계)
- [ ] **N-3 퍼널 `JointGateBlock=N` vs `TRADE.log` grep** — F-5 적용 후 정확히 일치해야 함
- [ ] **N-4 `_tick_header ≥5000ms` 건수** — 오늘 10건(460차 9건). 15건 초과면 G-3 상향
- [ ] **N-5 `[FeatureReg] 5m … 제외: ['opt_chain_pcr']` 만성도** — `최초관측` → `만성` 승격 여부.
- [ ] **N-6 `eod_retrain_done_*.txt` 의 `horizons_replaced`** — `6/6` 유지. 미달이면 익일 CB③ HALT 위험
- [ ] **N-7 `[ConfFloorGuard]` 경보 vs `conf > out_max` 분봉 수** — 오늘 1 vs 210(붕괴행 제외).
- [ ] **N-8 예약작업 `mireuk-postmarket-check` 트리거 시각** — **15:50 KST** 변경 여부(460차 F-0).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
ensemble_decisions` 6컬럼 전례와 동일 패턴). `tests/test_457_fallback_visibility.py`의
  검사 범위를 **"DB 컬럼에 폴백값을 쓸 때 같은 행에 플래그가 있는가"** 로 확장 —
  계측 4원칙 ④ 3번째 규약이 문장으로만 있고 자동 검출이 없다.
  **근거**: 오늘 하루에만 미측정이 정상값으로 위장한 사례 2건.
  ⚠ 기존 96행은 `NULL`(미상)로 남아 소급 판정 불가 — 주석 명기. F-7과 동시 작업 권장.

- [x] **G-6 JointGateBlock 폴백 비율 일일 자동 집계** — ✅ **2026-08-13 구현·검증 완료(커밋 ④)**.
  `fetch_daily_joint_gate_fallback()` 신설. 출력
  `└ JointGateBlock 7건 (무정보폴백 6건 = 85.7%) [표본 13건 부족 — 판정보류]`.
  🔧 **[선행조건 정정] 460차 F-1을 기다릴 필요가 없었다** — **420차가 `joint_gate_shadow.meta_size_fallback`
  컬럼으로 이미 승격**해뒀다(리포트 "함정 ①"에 해당). 값(`meta_size==0.50`) 추정이 아니라 컬럼을 읽는다 —
  학습값이 우연히 0.50인 행과 구분되기 때문. 실측 85.7%로 수동 집계와 정확히 일치.
  일자별: 08-03 76.9%(n=26) · 08-06 77.8%(9) · 08-07 73.7%(19) · 08-11 100%(1) · 08-13 85.7%(7).
  **판정 표본 20 도달은 08-03뿐** — `verdict_ready=False`면 판정문 미출력(313차).
  ~~아래 원안~~ —
  15:40 리포트 퍼널 섹션에 `└ JointGateBlock N건 (무정보폴백 M건 = P%) [min_samples=20까지 K건]`.
  **근거**: 오늘 7건 중 6건(85.7%) `meta=0.50`. 같은 창 건수가 08-11 0 · 08-12 0 · 08-13 7로 급변.
  "3거래일 연속 폴백비율 80% 초과" 판정 조건이 사람 손 없이 채워진다.
  ⚠ **min_samples=20 도달 전까지 판정문은 출력하지 않는다**(313차).

### 문서·운영

- [x] **`TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` 를 실전 전환 기준 ⑨로 승격 (F-4 확장)** —
  ✅ **2026-08-13 완료(커밋 ③)**. 승격 완료. 단 ⑨는 **F-8(섀도 배선) 없이는 판정 불가**임을
  기준 본문에 명시했다.

- [x] **실전 전환 기준 ③ "MDD ≤ 15%" 문구에 분모 명시** — ✅ **2026-08-13 완료(커밋 ②, F-7 동시)**.
  `자본 대비` 확정 + `mdd_pct`(peak 별칭)를 판정에 쓰지 말라는 경고,
  2026-08-13 이전 시계열 불연속 경고까지 함께 기재.

- [x] **`docs/정기점검/매일점검/evidence_UNKNOWN-20260813_post.md` 수동 삭제** —
  ✅ **2026-08-13 확인 — 해당 파일이 존재하지 않는다.** 폴더에 남은 건
  `evidence_MW0601-20260813_post.md`(+ 08-12분)뿐이고, 커밋된 적도 없다.
  461차 세션 실측(`ls | grep -i unknown` → 0건). 조치 불필요.

### 다음 거래일(2026-08-14) 관측 예정

- [ ] **N-1 `[JointGateBlock 차단]` 중 `meta=0.50` 비율** — 3거래일 연속 80% 초과면 게이트 원인 확정.
  **오늘 85.7%(6/7), 1일차.** 판정 예정 08-18
- [ ] **N-2 진입 건수** — 0건이면 **2거래일 연속** → 진입0 딥다이브 절차 착수(460차 O-3 승계)
- [ ] **N-3 퍼널 `JointGateBlock=N` vs `TRADE.log` grep** — F-5 적용 후 정확히 일치해야 함
- [ ] **N-4 `_tick_header ≥5000ms` 건수** — 오늘 10건(460차 9건). 15건 초과면 G-3 상향
- [ ] **N-5 `[FeatureReg] 5m … 제외: ['opt_chain_pcr']` 만성도** — `최초관측` → `만성` 승격 여부.
  458차 §C(97개 동결 슈퍼셋)와 같은 계열로 보이나 이번엔 5m. 5거래일 누적 필요. 판정 예정 08-20
- [ ] **N-6 `eod_retrain_done_*.txt` 의 `horizons_replaced`** — `6/6` 유지. 미달이면 익일 CB③ HALT 위험
- [ ] **N-7 `[ConfFloorGuard]` 경보 vs `conf > out_max` 분봉 수** — 오늘 1 vs 210(붕괴행 제외).
  F-2 적용 후 괴리 해소 확인
- [ ] **N-8 예약작업 `mireuk-postmarket-check` 트리거 시각** — **15:50 KST** 변경 여부(460차 F-0).
  오늘도 16:2x 실행이었다

```

</details>

### dev_memory/CURRENT_STATE.md — 519.4KB · 마지막 갱신 2026-08-12 18:40

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

### `docs/정기점검/매일점검` — 22개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 12.2KB | 08-14 07:39 |
| `docs/정기점검/매일점검/MW0601-20260813-점검리포트-post.md` | 40.6KB | 08-13 16:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20260813_post.md` | 62.3KB | 08-13 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260812_post.md` | 67.0KB | 08-12 19:35 |
| `docs/정기점검/매일점검/MW0602-20260808-점검리포트.md` | 20.8KB | 08-12 18:40 |
| `docs/정기점검/매일점검/MW0602-20260806-점검리포트.md` | 21.2KB | 08-12 18:40 |
| `docs/정기점검/매일점검/MW0602-20260805-점검리포트.md` | 35.0KB | 08-12 18:40 |
| `docs/정기점검/매일점검/MW0602-20260731-점검리포트.md` | 27.4KB | 08-12 18:40 |

### `docs/정기점검/금요일점검` — 45개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0602/exit_expectancy_map_20260810.md` | 1.8KB | 08-14 07:47 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_report_20260810.md` | 4.6KB | 08-14 07:39 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_metrics_20260810.json` | 2.0KB | 08-14 07:39 |
| `docs/정기점검/금요일점검/주간회의.txt` | 2.2KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.7KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/validation capain.txt` | 4.7KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/Validation/validation.txt` | 158B | 08-12 18:40 |
| `docs/정기점검/금요일점검/MW0602/validation_campaign_report_20260807.md` | 128.0KB | 08-12 18:40 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. `logs/20260814_LEARNING.log`: **축퇴** 8건(표본)
7. 미커밋 변경 433건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260814*.log` (Windows) / `grep 강제청산 logs/*20260814*.log`*