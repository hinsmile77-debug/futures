# 미륵이 증거 다이제스트 — 2026-08-21 / PRE

- 생성 2026-08-21 08:59:50 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/serene-jolly-mayer/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260821` · `2026-08-21` · `260821` · `0821`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **14개** 파일 · 14개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260821.log` | 125B | 08-21 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260821.json` | 245B | 08-21 08:59 |
| `launcher_{DATE}_084001_29653.log` | 1 | `logs/Mireuk_batch/launcher_20260821_084001_29653.log` | 33.9KB | 08-21 08:58 |
| `{DATE}_DATA.log` | 1 | `logs/20260821_DATA.log` | 914B | 08-21 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260821_DEBUG.log` | 0B | 08-21 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260821_HEALTH.log` | 0B | 08-21 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260821_HOGA.log` | 1.3MB | 08-21 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260821_LEARNING.log` | 50.3KB | 08-21 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260821_MICRO.log` | 34.5KB | 08-21 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260821_PROBE.log` | 1.7KB | 08-21 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260821_SIGNAL.log` | 5.6KB | 08-21 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260821_SYSTEM.log` | 24.8KB | 08-21 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260821_TRADE.log` | 167B | 08-21 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260821_WARN.log` | 797B | 08-21 08:41 |

## 2. 코드·커밋 상태

- HEAD `0be0eaa` · 브랜치 `v9-dev` · 미커밋 463건
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
… 외 423건
```

**당일(2026-08-21) 커밋**
```
(당일 커밋 없음)
```

**최근 커밋 12건**
```
0be0eaa [MW0601] docs/프롬프트 신설: 점검 체계 이관 지침 + 스킬/템플릿 참고본
d1dd4fb [MW0601] 482차 후속6: 481차 점검 산출물 복원 + 리포트 md 추적 편입
ccfad20 [MW0601] 482차 후속5: DECISION_LOG 테스트 집계 정정 — 613 passed
ab44ecb [MW0601] 482차 후속4: dev_memory 기록 + 457차 테스트 문자열 매칭 정정
74191d6 [MW0601] 482차 후속3: ConfFloorGuard 3상태 — G-3의 전제를 먼저 복구한다
0d48be8 [MW0601] 482차 후속2: 메인 스레드 정지 섀도 계측 — CB5와 FZ-1 사이 무관측 구간
7c1412e [MW0601] 482차 후속: CB③ 가용성 계측 — 판정 가능 시간을 처음 시계열화
44e2652 [MW0602] 477차: 일일점검 스킬 개정 — 리포트 가독성 대원칙 + 하루 한 파일 append 규약
0215f6c [MW0602] 476차: 장전·장후 점검 (G-1 label_scheme 유실 + 등급 A/B 도달불가) + 이월분 정리
38a8312 [MW0601] 482차: 점검 수집기 — 포지션 단위 집계 + 브랜치 스코프 분리
7a59796 [MW0601] 480차 후속4: F-2 가드가 감시 개시를 파일에 남긴다 — 사이드카 자신의 생존 증거
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
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
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

_이 브랜치(`v9-dev`) 범위 밖 **5건** — 표에서 제외했다(계측 4원칙 ③): `MODEL_LABEL_STATE_UNLOCK_ENABLED`(→dev), `PRE_RETRAIN_DONE_BY_EOD_ENABLED`(→dev), `ZONE_ENTRY_BAN_ENFORCE`(→dev), `ZONE_ENTRY_BAN_SHADOW_ENABLED`(→dev), `PIPE_LATENCY_EXCLUDE_MODEL_SWAP`(→dev)._
> 제외는 "없어도 된다"가 아니라 "이 브랜치에는 기능 자체가 없다"는 뜻이다. 이식 여부는 별개 안건이며 주간회의에서 정한다.

### 차단 게이트 전수 인벤토리 — 30개 중 **8개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
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
| `FORCE_FLAT_GUARD_ENABLED` | True | — |
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
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260821_HOGA.log` 1.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/10개 (중요도순). 제외: `launcher_20260821_084001_29653.log`, `force_flat_guard_20260821.log`_

### `logs/20260821_TRADE.log` — 167B · 2행 · 최종 08:41:14

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:10 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-21 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-21 08:41:10 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-21 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260821_WARN.log` — 797B · 5행 · 최종 08:41:21

- 형식 평문 · 시각 인식 5행 · WARNING=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-21 08:41:20 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=NA
2026-08-21 08:41:21 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-21 08:41:20 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=NA
2026-08-21 08:41:21 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 5 | 08:41:18 | 08:41:21 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |

**채널** — `SYSTEM`×5

**컴포넌트 상위 15** — `LiveDBG`×5

### `logs/20260821_SYSTEM.log` — 24.8KB · 198행 · 최종 08:59:35

- 형식 평문 · 시각 인식 192행 · INFO=192, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.4MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-08-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18348 | 행감지=30s all_threads=True
2026-08-21 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-21 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-21 08:41:00 [INFO] SYSTEM: 미륵이 초기화
  …
2026-08-21 08:59:01 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:58 vol=64 | live_buy=31 shadow_buy=23 anchor_buy=23 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-08-21 08:59:01 [INFO] SYSTEM: [PreMarket] Phase4 refit 기동 (14봉 z경고=5개)
2026-08-21 08:59:01 [INFO] SYSTEM: [PreMarket] Phase4 refit 완료 n=30봉 z경고 5→5개 | 잔존=atr,avg_volume,queue_depletion_speed,queue_refill_rate,toxicity_queue_stress
2026-08-21 08:59:24 [INFO] SYSTEM: [CybosRT-TICK] #2500 code=A0569 raw_time=85924 parsed=08:59:24 price=1065.20 vol=1 bid1=1065.18 ask1=1065.24 flag=50 side=SELL anchor=0/1
2026-08-21 08:59:35 [INFO] SYSTEM: [TickUI] alive ticks=2543 code=A0569 close=1065.18
```

</details>

**채널** — `SYSTEM`×192

**컴포넌트 상위 15** — `CybosRT-TICK`×30, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `-`×3, `EarlyWarmup`×3

### `logs/20260821_SIGNAL.log` — 5.6KB · 47행 · 최종 08:59:01

- 형식 평문 · 시각 인식 47행 · WARNING=6, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
  …
2026-08-21 08:45:59 [INFO] SIGNAL: [GapOffset] today_open=1068.40 | offset: {}
2026-08-21 08:48:05 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase1_3bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-08-21 08:49:59 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.01s
2026-08-21 08:54:59 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.01s
2026-08-21 08:59:01 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.01s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 6 | 08:45:18 | 08:45:18 | 1m CORE 'cvd_divergence' raw_std≈0(0.0225) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×47

**컴포넌트 상위 15** — `ScalerFloor`×18, `ScalerRefresh`×11, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1

### `logs/20260821_LEARNING.log` — 50.3KB · 281행 · 최종 08:59:01

- 형식 평문 · 시각 인식 281행 · WARNING=137, INFO=144

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:01 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.529 out_max=0.4002 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2754 < conf_floor=0.3300 (span=0.00060 auc=0.568 out_max=0.2754, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.501 out_max=0.1502 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=100) → 보정 미적용, raw 통과
  …
2026-08-21 08:48:05 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-21 08:49:59 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-21 08:54:59 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-21 08:55:18 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=9960, ver=5)
2026-08-21 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 137 | 08:41:02 | 08:41:10 | 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×281

**컴포넌트 상위 15** — `Calibration`×268, `ScalerWarmup`×5, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20260821_MICRO.log` — 34.5KB · 93행 · 최종 08:59:40

- 형식 평문 · 시각 인식 93행 · DEBUG=93

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:45:18 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1069.20/1 ask1=1069.68/1 mp={'microprice_tick': 1069.44, 'midprice_tick': 1069.44, 'depth_bias_tick': 0.0484} mlofi_tick=None queue=None
2026-08-21 08:45:18 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1069.20/1 ask1=1069.70/2 mp={'microprice_tick': 1069.3666, 'midprice_tick': 1069.45, 'depth_bias_tick': -0.0341} mlofi_tick=2.7833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio'…
2026-08-21 08:45:18 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1069.20/1 ask1=1069.70/1 mp={'microprice_tick': 1069.45, 'midprice_tick': 1069.45, 'depth_bias_tick': 0.1464} mlofi_tick=2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-08-21 08:45:18 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1069.12/1 ask1=1069.70/1 mp={'microprice_tick': 1069.41, 'midprice_tick': 1069.41, 'depth_bias_tick': 0.2452} mlofi_tick=-3.0667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-21 08:45:18 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1069.12/1 ask1=1069.70/1 mp={'microprice_tick': 1069.41, 'midprice_tick': 1069.41, 'depth_bias_tick': 0.2693} mlofi_tick=0.2 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
  …
2026-08-21 08:58:49 [DEBUG] MICRO: [MICRO-TICK] #5600 bid1=1064.56/1 ask1=1064.74/1 mp={'microprice_tick': 1064.65, 'midprice_tick': 1064.65, 'depth_bias_tick': 0.0483} mlofi_tick=3.3333 queue={'depletion_bid': 4.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-21 08:59:01 [DEBUG] MICRO: [MICRO-MINUTE] #14 ts=2026-08-21 08:58:00 close=1064.50 bias=-0.006165 slope=0.153178 depth_bias=0.0013 mlofi_norm=-0.026907 mlofi_pressure=-1 mlofi_slope=9.081667 queue_signal=0.0654 queue_ma=0.0262 queue_momentum=0.0194 depletion=0.5111 refill=0.4889 imbalance_s…
2026-08-21 08:59:12 [DEBUG] MICRO: [MICRO-TICK] #5700 bid1=1064.70/1 ask1=1064.84/1 mp={'microprice_tick': 1064.77, 'midprice_tick': 1064.77, 'depth_bias_tick': -0.1246} mlofi_tick=-2.9333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-08-21 08:59:25 [DEBUG] MICRO: [MICRO-TICK] #5800 bid1=1064.78/1 ask1=1064.94/2 mp={'microprice_tick': 1064.8333, 'midprice_tick': 1064.86, 'depth_bias_tick': -0.0119} mlofi_tick=3.6167 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_rati…
2026-08-21 08:59:40 [DEBUG] MICRO: [MICRO-TICK] #5900 bid1=1065.16/1 ask1=1065.38/1 mp={'microprice_tick': 1065.27, 'midprice_tick': 1065.27, 'depth_bias_tick': -0.0021} mlofi_tick=0.3333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
```

</details>

**채널** — `MICRO`×93

**컴포넌트 상위 15** — `MICRO-TICK`×79, `MICRO-MINUTE`×14

### `logs/20260821_DATA.log` — 914B · 4행 · 최종 08:58:51

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:58:21 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152502 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-21 08:58:21 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-21 08:58:51 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152505 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-21 08:58:51 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
  …
2026-08-21 08:58:21 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152502 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-21 08:58:21 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-21 08:58:51 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152505 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-21 08:58:51 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
```

</details>

**채널** — `DATA`×4

**컴포넌트 상위 15** — `CybosInvestor`×4

### `logs/20260821_PROBE.log` — 1.7KB · 11행 · 최종 08:58:51

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:18 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-08-21 08:58:21 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-21 08:58:21 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-21 08:58:21 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-21 08:58:21 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-08-21 08:58:51 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-21 08:58:51 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-21 08:58:51 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-21 08:58:51 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-21 08:58:51 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:21 | 08:58:51 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

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

### 메인 스레드 블로킹 1건 · 최대 2844ms · 5초 초과 0건

상위 — 2844ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260821_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:20 2026-08-21 08:41:20 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=NA
```

### `logs/20260821_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
```

### `logs/20260821_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.529 out_max=0.4002 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2754 < conf_floor=0.3300 (span=0.00060 auc=0.568 out_max=0.2754, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.501 out_max=0.1502 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=100) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260821_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:10 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260821_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 5 | 08:41:18 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260821_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:46 [INFO] 로테이션 — 8.4MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 89 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 55 | 08:54:01 [INFO] #2000 code=A0569 raw_time=85402 parsed=08:54:02 price=1064.06 vol=2 bid1=1063.80 ask1=1064.04 flag=49 side=BU… |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260821_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 43 | 08:45:18 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0225) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 3 | 08:49:59 [INFO] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:54:59 [INFO] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] ela… |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| 20260817 | 17:58 | 로그 본문 |
| 20260814 | 15:40 | 로그 본문 |
| **중앙값** | **17:02** | 기준선 |
| **오늘 20260821** | **08:59** | 로그 본문 |

- 델타 **-483분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.0MB · 마지막 갱신 2026-08-20 22:26

최근 헤딩 8개:
```
## 2026-08-20 (MW0601 481차 후속2 — 장후 점검 · 분석만, 코드 0건)
### [1] CB③ 판정 가능 여부를 로그로 재구성할 수 없다 (P1, 기존 TODO G-3의 근거 확정)
### [2] 수집기 §5 부분청산 레그 누락 — 장후 국면에서도 재발 (P1, 2일차)
### [3] 설정 불변식 5건 `미발견`은 브랜치 스코프 문제 — 8일차 (P1 승격 권고)
### [4] 메인 스레드 정지 5초 초과 4건이 어떤 안전장치 사정권에도 없다 (P2, 기전 신규)
### [5] 등급 인플레(원시 C → 최종 A)는 손익 축에서 R-후보가 **아니다** — O-12 반증
### [6] R-1 신규 — 3m 호라이즌은 승률이 아니라 **손익비**가 문제다
### [7] 정상 확인 (이상점 아님 — 재상정 방지용 기록)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
역은 앙상블 가중과 라우터 경계
(`ENTRY_HORIZON_B1/B2`)를 동시에 바꾸는 **매매 정책 변경**이며, 474차가 라우터 경계 변경의
실측 전제가 약함을 이미 경고했다.

### [7] 정상 확인 (이상점 아님 — 재상정 방지용 기록)

1. **EOD 재학습 성공** — `horizons_replaced: 6/6` · `rows 40395` · `cols 97` ·
   `t_total_s 237.0` · `daily_close_seen true` · `wait_dc_timeout false` ·
   `Python : 3.10.20 64-bit`(py310_64 정상, 191차 결정 — 재거론 금지).
2. **15:10 강제청산** — 14:01:35 이후 FLAT. `15:11:03 [SchedForceExit] status=FLAT
   engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)`.
   안전망 ERROR 미출현. **⚠ 전환기준 ② ⓐ 실집행은 여전히 누적 0회.**
3. **F-2 프로세스 밖 FLAT 가드 라이브 첫 확인** — `[ForceFlatGuard] 2026-08-20 15:12:00 OK`.
   480차 후속4(`7a59796`)의 "감시 개시를 파일에 남긴다"가 라이브에서 동작.
4. **FZ-1 워치독 오탐 0건** — `heartbeat_MW0601_20260820.json` `strikes:0` `fired:false`.
5. **매분 루프 371/371분(100.0%)** · 10분 이상 공백 0건 · 로그 종료 15:40 = 5거래일 중앙값 **+0분**.
6. **1계약 TP1은 부분청산이 아니라 보호전환이 설계다 — 결함 아님.**
   `14:00:52 [SingleContractTP1] 1계약 TP1 도달 -> 보호전환 LONG mode=atr_profit
   price=1079.36 stop=1075.86->1078.87` → 최종 +0.48pt 확보(CASE-04).
7. **`손절1차 조기축소`가 손실을 줄였다** — CASE-01에서 2계약을 1084.23에 정리한 덕에
   gross −265,000원(전량 하드스톱 시 −438,000원). **약 173,000원 절감.**
8. **F-8 Phase B 3거래일차 무결** — 진입 4건 `spread_ticks` 5.9998/3.0029/3.9978/5.9998,
   전부 8틱 미만, `spread_extreme_shadow` 발화 0건, NULL 0건. ⑨ 표본 증가 없음.
9. **3원 대사 일치** — 로그 `[Position] 진입` 4 = `ensemble_decisions.entry_executed=1` 4
   = `trades COUNT(DISTINCT entry_ts)` 4. 레그 7 > 포지션 4는 불일치 아님.
   `weight_collapsed=1` 79행(21.4%) — CLAUDE.md 기술 범위 내.
10. **CB② 연속 손절 4회 · 정지 없음** — `CB_CONSEC_STOP_LIMIT=9999` 모의 한정 예외.
    재검토 2026-08-29. **재상정 금지.**
11. **`MAX_CONTRACTS=3`** — 431차 배포분. **재상정 금지.**
12. **전략 상태 경보 UNDERPERFORM** — 판정 ≠ 결정(함정 ①). MDD **자본 대비 3.0%**(기준 15% 내).
    `MDD(peak대비)=274.2%`는 461차 재인용 금지 값 — **인용하지 않았다.**
13. **미커밋 461건은 CRLF 착시** — `git diff --ignore-cr-at-eol --shortstat` = **2 files
    +416** (오늘 dev_memory append분). 작업 트리는 깨끗하다. NEXT_TODO F-5 근거.
14. **`ConstOut` 6회** — O-11 임계 도달했으나 직전 밴드(08-12 8회 / 08-18 6회) 내이고
    유효가동률 76.2%도 밴드(75.1~78.4%) 내. **강도 상향 근거 약함 — 관찰 유지.**
15. **`institution_futures_net` σ_floor 0.15 실적용 확인**(08:45:03 6호라이즌, O-3 충족).
    그럼에도 09:00 봉 `max_z=-15.07` 발생했고 **09:01:00 한 시점 한정, 재발 없음**(O-2 충족)
    → G-2(개장 첫봉 z 프로파일 상설 계측) 근거 보강. 단일 관측이라 임계 재설계 보류.
16. **`[IntradayRegime]` 전이 11회**(O-1 답) — 09:01:59 `NORMAL→CRASH` 이후
    `DAY_RISK_OFF ↔ NORMAL` 왕복.
17. **`[8] KellySkip` 표본 +1건(승)** — CASE-04 `kelly_advised_skip=1`에서 1계약 진입 후
    +22,382원. **여전히 min_samples 미달 — 판정 금지, 문턱 인하 금지(458차 D6).**

```

</details>

### dev_memory/NEXT_TODO.md — 1.1MB · 마지막 갱신 2026-08-20 22:26

최근 헤딩 8개:
```
### 🟢 고도화
### 📄 문서 정정 (근거 오류 — 다음 세션이 오독한다)
### 🔵 기한 — 주간회의(2026-08-22 금) 상정
### 다음 거래일(08-21)~ 관측
### ✅ 완료·종결 처리 (477차 장전·장중 등록분)
### 481차 — 장전 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 481차 후속 — 장중 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 481차 후속2 — 장후 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
```

미완료 체크박스 **1719건** (끝에서 30건)
```
- [ ] **[16] `chase_foreign_combo_watch` 표본 갱신 보고** — 오늘 A급 패 1건 추가
- [ ] **O-7 (장후) 15:10 강제청산 경로** — 12:31 현재 FLAT이라 **미발생이 정상**.
- [ ] **O-8 (장후) 잔고 델타 잔차 27,034원** — 레그 합 -269,884 vs 잔고 델타 -296,918.
- [ ] **O-9 (장후) `[CB③]` acc30m 종일 리셋/스킵 횟수와 ready 구간** —
- [ ] **O-10 (장후) `_tick_header` 블로킹 종일 분포** — 오전 최대 4,750ms(임계의 95%),
- [ ] **O-11 (장후) `ConstOut ['3m']` 종일 횟수** — 오전 4회(08-19와 동수).
- [ ] **O-12 (08-21) 등급 인플레 R-후보 3일차** — 오늘 2일차 누적 3건 승1 패2,
- [ ] **F-1 (P1, 승격 — 선행 O-9 해소) `[DBG-CB]`에 표본 수·판정가능 여부 병기** —
- [ ] **F-2 (P1, 승격 · 8일차) 수집기 설정 불변식 표를 브랜치별로 분기** —
- [ ] **F-3 (P2, 신규) 메인 스레드 정지 전용 섀도 계측** —
- [ ] **F-4 (P1, 기등록 유지 · 2일차) 수집기 §5 포지션 단위 집계 + 정합성 등식** —
- [ ] **F-5 (P2, 기등록 유지) 수집기 CRLF 내성** — 코웍 리눅스 샌드박스에서 `461건` 착시.
- [ ] **G-1 (이번 주, 선행 F-1) CB③ 판정 가능 시간을 일일 지표로 승격** —
- [ ] **G-2 (다음 주, 선행 G-1) 스케일러 재적합 ↔ CB③ 버퍼 상호작용 계측** —
- [ ] **G-3 (다음 주) 진입 후보 시간에서 `ConfFloorGuard` 구간 분리 카운트** —
- [ ] **R-1 (섀도 2주 선행) 3m 호라이즌 손익비 비대칭** —
- [ ] ~~**O-12 등급 인플레 R-후보**~~ → **강등(반증)**. `raw_grade` 기록 시작(07-30) 이후
- [ ] **`ZONE_ENTRY_BAN_SHADOW_ENABLED` 양 PC 배선** — 462차 P1-a는 "집행과 무관하게 위반
- [ ] **전환기준 ⑥에 "CB③ ready 시간 ≥ 장중 50%"를 판정 전제로 추가** 검토 —
- [ ] **NEXT_TODO O-10 문언 폐기 승인** — "5,000ms 초과 1건이라도 나오면 CB⑤ 실발동"은
- [ ] **계측 4원칙 ① 적용범위(기등록 유지)** — 오늘 근거 2건 추가: §5 재발(F-4)과
- [ ] **O-1 (장후) 수집기 §5 포지션 단위 재현** — F-4 미적용이면 3자 차이 재기록.
- [ ] **O-2 (장중) `_tick_header` 5초 초과 건수와 `pipe_elapsed`** —
- [ ] **O-3 (장후) 3m 라이브 적중률·ConstOut 집중도** — 오늘 3m 0.2828(전 호라이즌 최저),
- [ ] **O-4 `ZONE_ENTRY_BAN_SHADOW_ENABLED` 실효 확인** — 채널 `[53]` 표본 적립 주체를
- [ ] **O-5 (장후) `[GuardGhost] 3m` 재발 여부** — 오늘 1회(457차 F7 ⑤안으로 정상 처리).
- [ ] **O-6 등급 인플레 4일차** — R-후보 아님(위 반증). 일자단위 누적만.
- [ ] **O-7 (장후) 15:10 강제청산 실집행** — 누적 **0회**. 진입이 15:05 이후까지 열린 날이
- [ ] **O-8 로컬 커밋 push** — `origin/v9-dev` 대비 **ahead 8**(어제 7 → 오늘 8).
- [ ] **O-9 (장전) 미커밋 건수 표기** — 수집기 CRLF 착시(`461건`). F-5 적용 전까지
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
] **R-1 (섀도 2주 선행) 3m 호라이즌 손익비 비대칭** —
      포지션 단위·계약당 정규화(07-21~, n=145): **3m 80포지션 승률 65.0% 인데 −702,359원**
      (평균이익 77,965 / 평균손실 −169,877 / **손익비 0.46** / 평균 −1,492원/계약).
      5m 1.13(+489,250/계약), 1m 0.39이나 평균 +28,594원/계약.
      08-05~(431차 이후)로 좁혀도 3m 51포지션 70.6% **−363,655원** — 부호 동일(313차 ⑤ 통과).
      전략 리포트 30일 순EV도 `3m=−6,753원(104건)`이 유일한 음수.
      **대상**: `ATR_HORIZON_TP1_MULT['3m']`(0.5) 후보 0.6/0.7 병행 섀도 기록 + 3m 손절폭 산출부.
      ⚠ **라이브 변경 금지 · 판정 기준 사전등록 필수 · 청산 파라미터 축에 한정.**
      ⚠ **"3m을 끄자"는 근거가 아니다** — 라우터 경계 변경은 매매 정책 변경이고
      474차가 실측 전제 약함을 이미 경고했다.
- [ ] ~~**O-12 등급 인플레 R-후보**~~ → **강등(반증)**. `raw_grade` 기록 시작(07-30) 이후
      전량 포지션 단위: **C→A 62포지션 43승(69.4%) +801,999원** vs 대조군 C→C 28포지션
      **−154,625원**. 3거래일 연속 적자는 소표본 변동. **확정 결론 금지(313차).**
      단순 관찰 항목으로 되돌리고 **일자단위로만** 누적 기록한다.
      ⚠ 481차 후속 [2]의 **기전 주장**(CB③-P4 사정권 공동화)은 손익과 독립 — **유지.**

#### 주간회의 상정

- [ ] **`ZONE_ENTRY_BAN_SHADOW_ENABLED` 양 PC 배선** — 462차 P1-a는 "집행과 무관하게 위반
      계측은 항상 켜져 있어야 한다"인데 `v9-dev`에 상수 자체가 없다. 캠페인 채널 `[53]`이
      MW0602 단독 적립일 가능성. **확인 후 판정.**
- [ ] **전환기준 ⑥에 "CB③ ready 시간 ≥ 장중 50%"를 판정 전제로 추가** 검토 —
      판정 입력이 존재하지 않는 시간에 임계만 논하는 것은 무의미(F-1·G-1 결과 확인 후).
- [ ] **NEXT_TODO O-10 문언 폐기 승인** — "5,000ms 초과 1건이라도 나오면 CB⑤ 실발동"은
      **전제가 틀렸다**(단위 불일치). F-3으로 대체.
- [ ] **계측 4원칙 ① 적용범위(기등록 유지)** — 오늘 근거 2건 추가: §5 재발(F-4)과
      O-10 전제 오류(F-3). 둘 다 "단위 불일치"다.

#### 다음 국면(08-21) 관측 항목

- [ ] **O-1 (장후) 수집기 §5 포지션 단위 재현** — F-4 미적용이면 3자 차이 재기록.
      **3일 연속이면 P1 유지 근거 확정.**
- [ ] **O-2 (장중) `_tick_header` 5초 초과 건수와 `pipe_elapsed`** —
      `pipe_elapsed≠0`인 5초 초과가 **1건이라도** 나오면 CB⑤ 실발동 가능성 → 즉시 추적.
      오늘은 4/4가 `pipe_elapsed=0`.
- [ ] **O-3 (장후) 3m 라이브 적중률·ConstOut 집중도** — 오늘 3m 0.2828(전 호라이즌 최저),
      ConstOut 6/6 전량 3m. **2일 연속 3m 단독 집중이면 R-1 우선순위를 "이번 주"로.**
- [ ] **O-4 `ZONE_ENTRY_BAN_SHADOW_ENABLED` 실효 확인** — 채널 `[53]` 표본 적립 주체를
      금요일점검 MW0601×MW0602 대조로 확인.
- [ ] **O-5 (장후) `[GuardGhost] 3m` 재발 여부** — 오늘 1회(457차 F7 ⑤안으로 정상 처리).
      **3일 연속이면 "장중 재학습 → EOD 비교기준 소실"을 구조적 문제로 별도 등록.**
- [ ] **O-6 등급 인플레 4일차** — R-후보 아님(위 반증). 일자단위 누적만.
- [ ] **O-7 (장후) 15:10 강제청산 실집행** — 누적 **0회**. 진입이 15:05 이후까지 열린 날이
      오면 `[ForceExitPass] → [TimeExit] → [ExitAttempt]` 순서 확인.
      **`[SchedForceExit] … 안전망 발동`(ERROR)이 뜨면 P0.**
- [ ] **O-8 로컬 커밋 push** — `origin/v9-dev` 대비 **ahead 8**(어제 7 → 오늘 8).
      MW0602가 480차 후속·473차 검증분을 못 본다.
- [ ] **O-9 (장전) 미커밋 건수 표기** — 수집기 CRLF 착시(`461건`). F-5 적용 전까지
      `--ignore-cr-at-eol` 실측치로 매 리포트 정정.

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

### `data/heartbeat_MW0601_20260821.json` — 245B · 08-21 08:59:49
```json
{
 "pid": 18348,
 "written_at": "2026-08-21T08:59:49",
 "beat_epoch": 1787270388.3011916,
 "beat_age_sec": 0.9,
 "watching": false,
 "strikes": 0,
 "stall_sec": 180.0,
 "strikes_needed": 2,
 "check_sec": 30.0,
 "window": [
  "09:00",
  "15:45"
 ],
 "fired": false
}
```

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/evidence_MW0601-20260820_pre.md` | 49.0KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_post.md` | 70.5KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_intra.md` | 61.3KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_pre.md` | 46.2KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_post.md` | 63.9KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_intra.md` | 59.8KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260818_pre.md` | 60.5KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260818_post.md` | 69.3KB | 08-20 22:24 |

### `docs/정기점검/금요일점검` — 54개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.json` | 7.6KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.md` | 3.8KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260821_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 463건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260821*.log` (Windows) / `grep 강제청산 logs/*20260821*.log`*