# 미륵이 증거 다이제스트 — 2026-08-19 / PRE

- 생성 2026-08-19 08:59:54 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/bold-cool-cerf/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260819` · `2026-08-19` · `260819` · `0819`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **12개** 파일 · 12개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_22417.log` | 1 | `logs/Mireuk_batch/launcher_20260819_084001_22417.log` | 41.8KB | 08-19 08:59 |
| `{DATE}_DATA.log` | 1 | `logs/20260819_DATA.log` | 914B | 08-19 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260819_DEBUG.log` | 0B | 08-19 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260819_HEALTH.log` | 0B | 08-19 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260819_HOGA.log` | 1.2MB | 08-19 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260819_LEARNING.log` | 45.9KB | 08-19 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260819_MICRO.log` | 33.3KB | 08-19 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260819_PROBE.log` | 1.7KB | 08-19 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260819_SIGNAL.log` | 12.1KB | 08-19 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260819_SYSTEM.log` | 23.9KB | 08-19 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260819_TRADE.log` | 167B | 08-19 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260819_WARN.log` | 862B | 08-19 08:41 |

## 2. 코드·커밋 상태

- HEAD `624a275` · 브랜치 `v9-dev` · 미커밋 459건
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
… 외 419건
```

**당일(2026-08-19) 커밋**
```
(당일 커밋 없음)
```

**최근 커밋 12건**
```
624a275 [MW0601] 477차 후속7: GR-3 — ProfitGuard 차단 로그에 일일손익 원천 토큰(gross/net)
389a3e5 [MW0601] 477차 후속6: GR-1 — ProfitGuard L1 래치 기회비용 소급 계측 스크립트 신설
108f940 [MW0601] 477차 후속5: 476차 §3 고도화 방안 구현이득 조사 — G-2 라이브 배선 기각, 한계 기회비용 0 실측
1863a43 [MW0601] 477차 후속4: 문서 정리 — 475~477차 점검 산출물 + dev_memory + 08-29 안건 2건
ae5c29b [MW0601] 477차 후속3: 476차 F-3 재설계 + G-1 — TP1 훅 qty>=2 확장(경로 분리) + 포지션 MFE 소급 계측
a5f4b4c [MW0601] 477차 후속2: 476차 F-4 — daily_broker_pnl 단위 명시(gross/수수료/net) + 휴장일 유령 행 가드
710c1c5 [MW0601] 477차 후속: 476차 F-1+F-5 — DriftAdjuster 포화 가시화 + RegimeFingerprint PSI 매분 영속
cf0f803 [MW0601] 477차: ModelLive DB 승격(n_eff·교차표·σ·clean 4열) + 방향정렬 edge + ghost_bypass clean 어긋남 관측
7dc14bc [MW0601] 474차: D9 딥다이브 — §3 정합화 + 라우팅 밴드 채널 + 30m 역필터 기각
68ff91c [MW0601] 473차: 구조적 교착 해소 — 테스트 오염 · F-8 배선/판정 · D9 도달성 · D8 인프라
e995764 [MW0601] 472차: UI 좌상단 "Phase 3 예정" 배지 → Phase 5 전환 게이트 자동 판정
f911e8d [MW0601] 471차 후속8: G-3 강제청산 리허설 26주 WFA 편입 + 로드맵 반영 + dev_memory
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

_본문 미열람(설정): `20260819_HOGA.log` 1.2MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/9개 (중요도순). 제외: `launcher_20260819_084001_22417.log`_

### `logs/20260819_TRADE.log` — 167B · 2행 · 최종 08:41:18

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-19 08:41:18 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-19 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-19 08:41:18 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260819_WARN.log` — 862B · 6행 · 최종 08:41:27

- 형식 평문 · 시각 인식 6행 · WARNING=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-19 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-19 08:41:27 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3594ms — live 중단 원인 분석용
  …
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-19 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-19 08:41:27 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3594ms — live 중단 원인 분석용
2026-08-19 08:41:27 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 6 | 08:41:21 | 08:41:27 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |

**채널** — `SYSTEM`×6

**컴포넌트 상위 15** — `LiveDBG`×6

### `logs/20260819_SYSTEM.log` — 23.9KB · 193행 · 최종 08:59:31

- 형식 평문 · 시각 인식 187행 · INFO=187, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21612 | 행감지=30s all_threads=True
2026-08-19 08:40:59 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-19 08:40:59 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-19 08:40:59 [INFO] SYSTEM: 미륵이 초기화
2026-08-19 08:40:59 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-18) 종가 버퍼 로드: 385봉
  …
2026-08-19 08:59:01 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:58 vol=109 | live_buy=61 shadow_buy=37 anchor_buy=37 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-08-19 08:59:01 [INFO] SYSTEM: [PreMarket] Phase4 refit 기동 (14봉 z경고=6개)
2026-08-19 08:59:01 [INFO] SYSTEM: [PreMarket] Phase4 refit 완료 n=30봉 z경고 6→4개 | 잔존=atr,avg_volume,cancel_add_ratio,toxicity_queue_stress
2026-08-19 08:59:13 [INFO] SYSTEM: [CybosRT-TICK] #2200 code=A0569 raw_time=85912 parsed=08:59:12 price=1023.98 vol=1 bid1=1023.94 ask1=1024.14 flag=49 side=BUY anchor=1/0
2026-08-19 08:59:31 [INFO] SYSTEM: [TickUI] alive ticks=2242 code=A0569 close=1023.92
```

</details>

**채널** — `SYSTEM`×187

**컴포넌트 상위 15** — `CybosRT-TICK`×27, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `-`×3, `EarlyWarmup`×3

### `logs/20260819_SIGNAL.log` — 12.1KB · 95행 · 최종 08:59:01

- 형식 평문 · 시각 인식 95행 · WARNING=54, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.403
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.395
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.391
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.399
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
  …
2026-08-19 08:59:01 [WARNING] SIGNAL: [ScalerRefresh] 5m CORE 'ofi_norm' raw_std≈0(0.0441) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-19 08:59:01 [WARNING] SIGNAL: [ScalerRefresh] 10m CORE 'ofi_norm' raw_std≈0(0.0441) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-19 08:59:01 [WARNING] SIGNAL: [ScalerRefresh] 15m CORE 'ofi_norm' raw_std≈0(0.0441) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-19 08:59:01 [WARNING] SIGNAL: [ScalerRefresh] 30m CORE 'ofi_norm' raw_std≈0(0.0441) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-19 08:59:01 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 54 | 08:45:21 | 08:59:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0280) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×95

**컴포넌트 상위 15** — `ScalerRefresh`×59, `ScalerFloor`×18, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1

### `logs/20260819_LEARNING.log` — 45.9KB · 259행 · 최종 08:59:01

- 형식 평문 · 시각 인식 259행 · WARNING=125, INFO=134

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00024 auc=0.524 out_max=0.3178 (기준 auc<0.53 and span<0.020, 기저율=0.3176 n=85) → 보정 미적용, raw 통과
2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00035 auc=0.536 out_max=0.3336 (n=90) → 보정 재적용
2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3336 < conf_floor=0.3300 (n=90) → 보정 재적용
  …
2026-08-19 08:48:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-19 08:50:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-19 08:55:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-19 08:55:21 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=8718, ver=5)
2026-08-19 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 125 | 08:41:05 | 08:41:13 | 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×259

**컴포넌트 상위 15** — `Calibration`×247, `ScalerWarmup`×5, `ExtremityCorrector`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20260819_MICRO.log` — 33.3KB · 90행 · 최종 08:59:44

- 형식 평문 · 시각 인식 90행 · DEBUG=90

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1027.52/1 ask1=1027.84/1 mp={'microprice_tick': 1027.68, 'midprice_tick': 1027.68, 'depth_bias_tick': 0.0} mlofi_tick=None queue=None
2026-08-19 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1027.52/1 ask1=1027.76/1 mp={'microprice_tick': 1027.64, 'midprice_tick': 1027.64, 'depth_bias_tick': -0.0987} mlofi_tick=-4.0667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-19 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1027.52/1 ask1=1027.76/1 mp={'microprice_tick': 1027.64, 'midprice_tick': 1027.64, 'depth_bias_tick': 0.0} mlofi_tick=0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0, …
2026-08-19 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1027.52/2 ask1=1027.96/1 mp={'microprice_tick': 1027.8133, 'midprice_tick': 1027.74, 'depth_bias_tick': 0.113} mlofi_tick=4.5667 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-19 08:45:22 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1027.66/2 ask1=1028.00/1 mp={'microprice_tick': 1027.8867, 'midprice_tick': 1027.83, 'depth_bias_tick': -0.3529} mlofi_tick=6.1 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
  …
2026-08-19 08:58:52 [DEBUG] MICRO: [MICRO-TICK] #5300 bid1=1024.20/3 ask1=1024.42/1 mp={'microprice_tick': 1024.365, 'midprice_tick': 1024.31, 'depth_bias_tick': 0.211} mlofi_tick=-5.9 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-19 08:59:01 [DEBUG] MICRO: [MICRO-MINUTE] #14 ts=2026-08-19 08:58:00 close=1023.84 bias=0.005882 slope=-0.709676 depth_bias=0.1168 mlofi_norm=-0.039675 mlofi_pressure=-1 mlofi_slope=-43.206667 queue_signal=-0.0656 queue_ma=-0.0228 queue_momentum=-0.0238 depletion=0.5000 refill=0.5000 imbala…
2026-08-19 08:59:11 [DEBUG] MICRO: [MICRO-TICK] #5400 bid1=1023.70/1 ask1=1023.84/1 mp={'microprice_tick': 1023.77, 'midprice_tick': 1023.77, 'depth_bias_tick': 0.042} mlofi_tick=2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-19 08:59:24 [DEBUG] MICRO: [MICRO-TICK] #5500 bid1=1023.74/2 ask1=1023.98/1 mp={'microprice_tick': 1023.9, 'midprice_tick': 1023.86, 'depth_bias_tick': 0.1272} mlofi_tick=0.9167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-19 08:59:44 [DEBUG] MICRO: [MICRO-TICK] #5600 bid1=1023.88/1 ask1=1024.10/1 mp={'microprice_tick': 1023.99, 'midprice_tick': 1023.99, 'depth_bias_tick': 0.1161} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
```

</details>

**채널** — `MICRO`×90

**컴포넌트 상위 15** — `MICRO-TICK`×76, `MICRO-MINUTE`×14

### `logs/20260819_DATA.log` — 914B · 4행 · 최종 08:58:55

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:58:25 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149194 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-19 08:58:25 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-19 08:58:55 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149178 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-19 08:58:55 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
  …
2026-08-19 08:58:25 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149194 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-19 08:58:25 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-19 08:58:55 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149178 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-19 08:58:55 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
```

</details>

**채널** — `DATA`×4

**컴포넌트 상위 15** — `CybosInvestor`×4

### `logs/20260819_PROBE.log` — 1.7KB · 11행 · 최종 08:58:55

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:21 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-08-19 08:58:25 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-19 08:58:25 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-19 08:58:25 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-19 08:58:25 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-08-19 08:58:55 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-19 08:58:55 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-19 08:58:55 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-19 08:58:55 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-19 08:58:55 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:25 | 08:58:55 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

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

### 메인 스레드 블로킹 1건 · 최대 2797ms · 5초 초과 0건

상위 — 2797ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260819_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:23 2026-08-19 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
```

### `logs/20260819_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.403
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.395
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.391
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.399
```

### `logs/20260819_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:05 2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:05 2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00024 auc=0.524 out_max=0.3178 (기준 auc<0.53 and span<0.020, 기저율=0.3176 n=85) → 보정 미적용, raw 통과
08:41:05 2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00035 auc=0.536 out_max=0.3336 (n=90) → 보정 재적용
08:41:05 2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.513 out_max=0.3369 (기준 auc<0.53 and span<0.020, 기저율=0.3368 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제]
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260819_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:13 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260819_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260819_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=21612 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 88 | 08:49:03 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 58 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260819_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:21 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0280) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 21 | 08:50:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0344) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 14 | 08:55:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0434) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.9MB · 마지막 갱신 2026-08-18 23:16

최근 헤딩 8개:
```
### 실측 (4개 발동일 소급, 즉시 적용)
### 🔴 조사 단계 임시 추정치 정정 — 재인용 금지
### 검증
## 2026-08-18 (MW0601 477차 후속7 — GR-3 ProfitGuard 손익 원천 토큰)
### 증상
### 원인 — 기존 계측이 있었지만 커버리지가 23%였다
### 결정
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
하므로 **어느 값도 손익 추정으로 쓸 수 없다.**
→ 후속5의 결론(라이브 배선 기각 · 소급 스크립트 채택 · 완화 근거 없음)은 유지되며,
"표본이 이 정도로 얇다"는 근거는 오히려 강해졌다.

### 검증

- `tests/test_477_gr1_profit_guard_latch.py` **10건** — 로그 파싱(피크/보호선/차단분) ·
  다른 게이트 선행 시 binding 제외 · conf 미달 제외 · 래치 이전 분 무시 ·
  `entry_mode=auto`가 C를 거르는지 · 클러스터 묶음/첫분 값 · **verdict 고정** ·
  렌더 필수 문구(깔때기·313차).
- 전체 487 passed. 산출물 1종 생성(`profit_guard_latch_20260818.md/json`).
- ⚠ `ALLOWED_GRADES`는 `main.py:8396`의 **리터럴 사본**이다 — main이 바뀌면 함께 고칠 것
  (주석에 명시).


## 2026-08-18 (MW0601 477차 후속7 — GR-3 ProfitGuard 손익 원천 토큰)

> 상위: `docs/정기점검/매일점검/MW0601-20260818-고도화방안검토.md` §3-1.
> 전체 스위트 487 → **496 passed**(신규 9건). 집행 무변경 — 로그 문자열 1개 추가.

### 증상

ProfitGuard가 보는 `daily_pnl_krw`는 호출부(`main.py:8313~8328`)에서 두 원천을 오간다 —
Cybos 캐시가 있으면 **broker(gross, 수수료 차감 전)**, 없으면 엔진
`daily_stats()["pnl_krw"]`(**net**) 폴백. 2026-08-18 실측 차이 **23,332원**(net의 3.5%).
피크·현재가 같은 원천이면 비율 판정(`trail_ratio`)은 내부 일관적이라 오작동은 아니지만,
**활성화 임계 `trail_activation_krw`는 절대 원화**라 폴백 여부로 발동 시점이 달라진다.
그런데 그 원천이 차단 로그 어디에도 남지 않아 **사후 복원이 불가능**했다.

### 원인 — 기존 계측이 있었지만 커버리지가 23%였다

`main.py`에 `[ProfitGuard][DebugPnL] source=...` 줄이 이미 있으나
**`if not _pg_allowed and _final_grade not in ("X",)`** 안에 있어 **등급이 이미 X면
찍히지 않는다.** 실측 커버리지: 08-18 **37/160(23%)** · 06-19 25 · 06-25 38 · 06-30 87.
차단의 대부분이 이미 X 등급 상태에서 일어나므로 정작 필요한 구간이 비어 있었다.

### 결정

- `strategy/profit_guard.py`
  - `is_entry_allowed(..., pnl_source=None)` 인자 신설 → `self._pnl_source`에 보관.
    `__init__`에서 **명시 초기화**(`None`) — `getattr` 폴백 금지(계측 4원칙 ④).
  - `_block()`이 모든 차단 줄에 **`| src=<label>`** 을 붙인다. 레이어 무관 전량.
  - `_PNL_SRC_LABEL = {"broker": "broker(gross)", "engine": "engine(net)"}` —
    **단위를 이름에 박는다**(계측 4원칙 ①). 미지정은 **`미상`**(0·임의값 금지, ②).
- `main.py` 호출부가 `pnl_source=_daily_pnl_source` 전달.
- ⚠ **`_block_log` 튜플은 3원소 그대로 둔다** — `dashboard/panels/profit_guard_panel.py:764`가
  `for ts, layer, reason in ...`로 언팩한다. 반환 `reason` 문자열에도 토큰을 넣지 않는다
  (`_grade_x_source`로 흘러들어 차단사유 분류기를 오염시킨다).
- `scripts/profit_guard_latch_watch.py`(GR-1)가 `_RE_SRC`로 토큰을 집계해 리포트에
  일자별 원천 분포를 찍는다. **토큰 이전 로그는 빈 dict = 미측정**으로 남기고
  "engine이었다"로 추정하지 않는다(②).

### 검증

- `tests/test_477_gr3_pnl_source_token.py` **9건** — broker/engine 라벨 · 미지정 시 `미상`
  (engine·broker 문자열이 아예 없어야 함) · 미지 라벨 통과 · 호출마다 갱신 ·
  **block_log arity 3 유지** · reason에 토큰 미유출 · GR-1 토큰 집계 · 레거시 로그 미측정.
- 기존 `test_426_profit_guard_l1.py` 무영향. 전체 496 passed.
- 라이브 확인(다음 L1 발동일): 차단 줄이 `... | src=broker(gross)` 형태인지.
  ⚠ 평시에는 L1이 안 터지므로 **L2/L3/L4 차단 줄**에서 먼저 보이게 된다(레이어 무관).

```

</details>

### dev_memory/NEXT_TODO.md — 970.5KB · 마지막 갱신 2026-08-18 23:16

최근 헤딩 8개:
```
### 기한
### 커밋 대기 (476차 — 본 세션은 커밋하지 않았다)
### 477차 — post 확인필요 3건 딥다이브 후속 (MW0601, 2026-08-18 분석만·코드 0건)
### 477차 후속2 — 476차 Fix 계획 검토 결과 (MW0601, 2026-08-18 · 검토만, 코드 0건)
### 477차 후속1~3 — 476차 Fix 구현 완료 (MW0601, 2026-08-18 · 커밋 3건)
### 477차 후속5 — 476차 §3 고도화 방안 조사 결과 (MW0601, 2026-08-18 · 조사만)
### 477차 후속6 — GR-1 구현 완료 (MW0601, 2026-08-18)
### 477차 후속7 — GR-3 구현 완료 (MW0601, 2026-08-18)
```

미완료 체크박스 **1420건** (끝에서 30건)
```
- [ ] **O-H 장전 점검 08:57±5분 복귀** — 오늘 13:44:15(4시간 47분 지연, 리포트 부재). 미복귀면 G-3 승격
- [ ] **DriftAdjuster 7일차** — F-1 미적용이면 `alpha 0.01000→0.01000` 7번째 출현
- [ ] **`tp1_trail_shadow` 0행 3일차** — qty=1 진입이 다시 나오는가(사이징 분포)
- [ ] **`[ModelLive]` 10m·15m 4일차** — 오늘 20.8%/21.3%(직전 2일 35.2/37.1, 29.8/32.6).
- [ ] **O-E ProfitGuard L1 차단 반사실 2일차** — 오늘 133건 적립
- [ ] **O-G IntradayRegime 전이 3일차** — 08-14 19회 / 08-18 18회
- [ ] **[9] 실전전환 ⑨ TOX-SEVERE-SPREAD** — 오늘 `spread_ticks ≥ 20` **1분 / 진입 0건**(최대 28.0틱).
- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **11일** 남음. 오늘 `9999` 유지 확인.
- [ ] `docs/정기점검/매일점검/MW0601-20260818-점검리포트-post.md` (신규)
- [ ] `docs/정기점검/매일점검/evidence_MW0601-20260818_post.md` (신규)
- [ ] `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md` (append)
- [ ] **DD-3 (D6 안건 편입 — 2026-08-26 주간회의, CB② 복원과 동일 회차)** —
- [ ] **DD-5 (10m/15m 5거래일 관측 계속)** — 476차 §6 항목 그대로. 08-18 라이브 20.8%와
- [ ] **FR-2 (F-2 안건 문안)** — "DriftAdjuster 입력 = 롤링 100분×6호라이즌(블렌드
- [ ] **G-A (F-5 하트비트)** — `logs/*_SYSTEM.log`에
- [ ] **G-B (F-5 영속)** — `ensemble_decisions.fp_psi` 비-NULL이 당일 행수만큼.
- [ ] **G-C (F-1 포화)** — 15:40 `[DriftAdjuster]` 로그가
- [ ] **G-D (F-4 EOD)** — 15:40 `[BrokerPnl] EOD 확정 — gross ... − 수수료 ... = net ...`
- [ ] **G-E (F-3 훅)** — TP1 도달 시 `synthetic_partial_exits`에
- [ ] **[안건] F-2 SGD 학습률 정책** — `ALPHA_MAX`(0.01) 상향 또는
- [ ] **[안건] 진입모드(`entry_mode`) 실전 목표값** — 476차 §1-5. 최소 08-03 이래
- [ ] **[안건] DD-3 ghost_bypass 범위** (477차 등록, 재확인) — D6 clean 판정 전환이
- [ ] **GR-1 `scripts/profit_guard_latch_watch.py` 신설 (이번 주)** — 읽기 전용 소급.
- [ ] **GR-2 [08-29 주간회의] ProfitGuard 래치 판정문 재등록 승인** —
- [ ] **GR-3 ProfitGuard 손익 원천 토큰 (소, 저위험)** — `strategy/profit_guard.py:_block()`
- [ ] **GR-4 재인용 금지 등재** — 476차 §3의 "L1 차단 133건 · 세션의 29.6%"를
- [ ] **GR-1R 다음 L1 발동일에 재실행** — L1은 2.5개월 4회라 다음 발동이 언제일지
- [ ] **GR-4 재인용 금지 갱신** — 476차 §3 "133건·29.6%"(로그 콜 수)에 더해,
- [ ] **GR-3V 다음 거래일 라이브 확인** — SIGNAL 로그의 `[ProfitGuard] 진입 차단` 줄에
- [ ] **GR-3F (후속 판단, 서두르지 말 것)** — 토큰이 며칠 쌓여 **broker/engine 혼재가
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
    ⓐ 대상을 **A/B → 자동진입 자격(등급 ∈ entry_mode 허용 & conf ≥ min_conf)** 으로.
        근거: 4일 816 차단분 전체 **A/B 0분**, binding 20분 전부 C.
      ⓑ `min_days` **10거래일 → L1 발동일 5일**(문턱 완화가 아니라 **단위 교체** —
        원 정의는 L1 미발동일까지 세어 도달 불가였다). `min_binding_minutes=40`.
      ⓒ 판정문: *"binding 반사실 합계 > 왕복비용×2 **且** 일자단위 부호검정 p<0.05 이면
        `trail_ratio` 완화를 안건화, 아니면 현행 래치 유지."*
      ⚠ 점검 세션 단독 변경 금지(§9, 458차 D6). 현 실측(binding 20분, 반사실 ≈0.00pt,
        1거래일)은 **판정 불가**이며 그대로 보고할 것.
- [ ] **GR-3 ProfitGuard 손익 원천 토큰 (소, 저위험)** — `strategy/profit_guard.py:_block()`
      로그에 `src=broker(gross)` / `src=engine(net)` 1토큰 추가. 근거: `main.py:8313~8328`이
      Cybos 캐시 유무로 gross/net을 오가는데 **사후 복원 불가**(4원칙 ①·④). 08-18 두 값
      차이 23,332원. 집행 무변경 · GR-1이 이 토큰으로 단위를 구분한다.
- [ ] **GR-4 재인용 금지 등재** — 476차 §3의 "L1 차단 133건 · 세션의 29.6%"를
      **한계효과로 인용 금지**(로그 콜 수). 한계 모집단은 **binding 20분/1거래일**이다.
      다음 점검 세션이 같은 수치로 완화를 재제안하는 것을 막는다.


### 477차 후속6 — GR-1 구현 완료 (MW0601, 2026-08-18)

- [x] ~~**GR-1 `scripts/profit_guard_latch_watch.py` 신설**~~ **[DONE 2026-08-18]**
      읽기 전용 소급 · 깔때기 · 클러스터 병기 · verdict `NOT_JUDGED` 고정.
      4개 발동일 즉시 산출: binding **17분(전부 08-18) / 3자리**,
      반사실 +1.08pt(분) / +4.27pt(자리). 테스트 10건, 전체 487 passed.
      산출물: `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.{md,json}`.
- [ ] **GR-1R 다음 L1 발동일에 재실행** — L1은 2.5개월 4회라 다음 발동이 언제일지
      모른다. `[ProfitGuard-L1] 트레일링 발동`이 로그에 뜬 날의 장후 점검에서
      `python scripts/profit_guard_latch_watch.py --write` 1회 실행할 것.
      ⚠ 자동 스케줄에 넣지 않는다 — 발동일에만 의미가 있고, 매일 돌리면 같은 4일치가
      매번 재계산돼 "적립 중"으로 오독된다.
- [ ] **GR-4 재인용 금지 갱신** — 476차 §3 "133건·29.6%"(로그 콜 수)에 더해,
      **477차 후속5 §1-5의 "binding 20분 · ≈+0.00pt" 임시 추정도 재인용 금지**.
      정본은 GR-1 스크립트 출력(17분/3자리/+1.08·+4.27pt)이다.


### 477차 후속7 — GR-3 구현 완료 (MW0601, 2026-08-18)

- [x] ~~**GR-3 ProfitGuard 손익 원천 토큰**~~ **[DONE 2026-08-18]**
      `_block()` 전 차단 줄에 `| src=broker(gross)|engine(net)|미상`.
      기존 `[DebugPnL]`은 등급 X면 안 찍혀 커버리지 23%(08-18 37/160)였다 — 이제 전량.
      `_block_log` 3튜플·reason 문자열은 무변경(대시보드·차단사유 분류기 보호).
      GR-1이 토큰을 집계하며 토큰 이전 로그는 **미측정**으로 남긴다. 테스트 9건, 전체 496 passed.
- [ ] **GR-3V 다음 거래일 라이브 확인** — SIGNAL 로그의 `[ProfitGuard] 진입 차단` 줄에
      `| src=` 가 붙는지. ⚠ L1은 드무므로 **L2-Tier/L3-Afternoon 차단 줄**에서 먼저 확인될 것.
      `src=미상`이 나오면 호출부가 인자를 안 넘기고 있다는 뜻이다(main.py:8333 확인).
- [ ] **GR-3F (후속 판단, 서두르지 말 것)** — 토큰이 며칠 쌓여 **broker/engine 혼재가
      실제로 관측되면**, `trail_activation_krw`를 어느 단위 기준으로 볼지 결정한다.
      ⚠ 지금 바꾸지 않는다 — 혼재 빈도조차 아직 미측정이다(사전등록 없는 임계 변경 금지).

```

</details>

### dev_memory/CURRENT_STATE.md — 529.4KB · 마지막 갱신 2026-08-17 17:53

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

### `docs/정기점검/매일점검` — 44개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260818-고도화방안검토.md` | 16.3KB | 08-18 23:04 |
| `docs/정기점검/매일점검/MW0601-20260818-Fix계획검토.md` | 13.8KB | 08-18 19:28 |
| `docs/정기점검/매일점검/MW0601-20260818-확인필요3건-딥다이브.md` | 15.5KB | 08-18 18:33 |
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-post.md` | 45.0KB | 08-18 16:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260818_post.md` | 69.3KB | 08-18 16:22 |
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-intra.md` | 39.4KB | 08-18 14:00 |
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-pre.md` | 45.5KB | 08-18 13:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260818_intra.md` | 61.8KB | 08-18 13:49 |

### `docs/정기점검/금요일점검` — 53개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.json` | 7.6KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.md` | 3.8KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260814.md` | 163.4KB | 08-14 15:49 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. `logs/20260819_LEARNING.log`: **축퇴** 8건(표본)
7. 미커밋 변경 459건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260819*.log` (Windows) / `grep 강제청산 logs/*20260819*.log`*