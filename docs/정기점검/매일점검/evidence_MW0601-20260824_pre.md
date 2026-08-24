# 미륵이 증거 다이제스트 — 2026-08-24 / PRE

- 생성 2026-08-24 08:59:37 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/festive-cool-albattani/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260824` · `2026-08-24` · `260824` · `0824`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **14개** 파일 · 14개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260824.log` | 125B | 08-24 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260824.json` | 244B | 08-24 08:59 |
| `launcher_{DATE}_084001_24123.log` | 1 | `logs/Mireuk_batch/launcher_20260824_084001_24123.log` | 45.9KB | 08-24 08:58 |
| `{DATE}_DATA.log` | 1 | `logs/20260824_DATA.log` | 914B | 08-24 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260824_DEBUG.log` | 0B | 08-24 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260824_HEALTH.log` | 0B | 08-24 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260824_HOGA.log` | 1.2MB | 08-24 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260824_LEARNING.log` | 42.7KB | 08-24 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260824_MICRO.log` | 32.1KB | 08-24 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260824_PROBE.log` | 1.7KB | 08-24 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260824_SIGNAL.log` | 16.9KB | 08-24 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260824_SYSTEM.log` | 24.0KB | 08-24 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260824_TRADE.log` | 167B | 08-24 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260824_WARN.log` | 1.2KB | 08-24 08:55 |

## 2. 코드·커밋 상태

- HEAD `4dbdf80` · 브랜치 `v9-dev` · 미커밋 486건 · 인덱스락 없음
```
M .claude/commands/dailycheck.md
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
 M config/krx_holidays.py
… 외 446건
```

**당일(2026-08-24) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
4dbdf80 [MW0601] 489차: 주간회의 승인 6건 — ⑨ WFA 이관 · [46]③ 재등록+배선 · 좀비결정 7건 분류 · [8]② 계측 이식
10178cb [MW0601] 489차 A-1: CB② 카운트를 절대원칙 문구에 맞춘다 — 시간창 + 포지션 단위 (한도 무변경)
9acc983 [MW0601] 488차 후속: 라이브 데이터에 고정된 캠페인 테스트 4개 재설계 — FAIL 12건 해소
7e82dcd [MW0601] 488차: [35] 유령 하드스톱 — 439차 "모집단 소멸" 서술 MW0601 비적용 + drop-max 계측
7451a64 [MW0601] dev_memory: MW0601_이관_점검사항 7건 조사 결과 기록
f628b83 [MW0601] 멀티PC 정책 폐기 후속: 운영 문서 3건에 남은 상호조율 관행 정리
302c8b5 [MW0601] 487차 후속 cherry-pick 조정: ConstOut 채널 번호 [51] 유지 (F-9 재배정 미적용)
1c4c6d1 [MW0602] 487차 후속: F-8(B)+F-9 구현 — 채널 [50]/[54] 브랜치 미가용 표기(감지형) + ConstOut [51]→[54] 재배정
ed8b919 [MW0602] 487차: 멀티PC 정책 폐기(사용자 결정) — F-8 MW0602 한정 권고(B 확정·A 폐기) + MW0601 이관 점검사항 분리
dfe97e8 [MW0601] docs/Ref: entry_band_watch.py 설명서 신설 — 라우팅 밴드 감시 채널
b2f02db [MW0601] 483차 후속5: 진입 호라이즌 경계 동결 — 5주 경보에 대한 명시적 결정 3건
9fab78f [MW0601] 483차 후속4: 캠페인 스텝이 인쇄 때문에 죽지 않게 한다 — P2-H
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

_본문 미열람(설정): `20260824_HOGA.log` 1.2MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/10개 (중요도순). 제외: `launcher_20260824_084001_24123.log`, `force_flat_guard_20260824.log`_

### `logs/20260824_TRADE.log` — 167B · 2행 · 최종 08:41:17

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:12 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-24 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-24 08:41:12 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-24 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260824_WARN.log` — 1.2KB · 8행 · 최종 08:55:21

- 형식 평문 · 시각 인식 8행 · WARNING=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 32ms
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-24 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2859ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2859 band=INFO since_pipe_s=NA
2026-08-24 08:41:26 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3375ms — live 중단 원인 분석용
  …
2026-08-24 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2859ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2859 band=INFO since_pipe_s=NA
2026-08-24 08:41:26 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3375ms — live 중단 원인 분석용
2026-08-24 08:41:26 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
2026-08-24 08:55:21 [WARNING] SYSTEM: [Canary] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증
2026-08-24 08:55:21 [WARNING] SYSTEM: [Canary] z경고 폭증(12개 ≥ 12개) → 장전 scaler 재적합 시도 (08:58 전)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 6 | 08:41:20 | 08:41:26 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Canary` | 2 | 08:55:21 | 08:55:21 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

**채널** — `SYSTEM`×8

**컴포넌트 상위 15** — `LiveDBG`×6, `Canary`×2

### `logs/20260824_SYSTEM.log` — 24.0KB · 193행 · 최종 08:59:34

- 형식 평문 · 시각 인식 187행 · INFO=187, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:40:48 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=25592 | 행감지=30s all_threads=True
2026-08-24 08:41:02 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-24 08:41:02 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-24 08:41:02 [INFO] SYSTEM: 미륵이 초기화
2026-08-24 08:41:02 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-21) 종가 버퍼 로드: 384봉
  …
2026-08-24 08:59:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=08:58 O=1093.58 H=1093.74 L=1092.92 C=1093.56 V=80
2026-08-24 08:59:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:58 vol=80 | live_buy=47 shadow_buy=42 anchor_buy=42 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-08-24 08:59:00 [INFO] SYSTEM: [PreMarket] Phase4 refit 기동 (14봉 z경고=4개)
2026-08-24 08:59:00 [INFO] SYSTEM: [PreMarket] Phase4 refit 완료 n=30봉 z경고 4→2개 | 잔존=atr,avg_volume
2026-08-24 08:59:34 [INFO] SYSTEM: [TickUI] alive ticks=2172 code=A0569 close=1092.34
```

</details>

**채널** — `SYSTEM`×187

**컴포넌트 상위 15** — `CybosRT-TICK`×26, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `-`×3, `EarlyWarmup`×3

### `logs/20260824_SIGNAL.log` — 16.9KB · 132행 · 최종 08:59:00

- 형식 평문 · 시각 인식 132행 · WARNING=48, INFO=84

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.419
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-08-24 08:59:00 [WARNING] SIGNAL: [ScalerRefresh] 5m CORE 'ofi_norm' raw_std≈0(0.0309) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-24 08:59:00 [WARNING] SIGNAL: [ScalerRefresh] 10m CORE 'ofi_norm' raw_std≈0(0.0309) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-24 08:59:00 [WARNING] SIGNAL: [ScalerRefresh] 15m CORE 'ofi_norm' raw_std≈0(0.0309) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-24 08:59:00 [WARNING] SIGNAL: [ScalerRefresh] 30m CORE 'ofi_norm' raw_std≈0(0.0309) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-24 08:59:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 48 | 08:45:20 | 08:59:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0118) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×132

**컴포넌트 상위 15** — `ScalerFloor`×60, `ScalerRefresh`×54, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1

### `logs/20260824_LEARNING.log` — 42.7KB · 242행 · 최종 08:59:00

- 형식 평문 · 시각 인식 242행 · WARNING=118, INFO=124

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:04 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00129 auc=0.498 out_max=0.5673 (기준 auc<0.53 and span<0.020, 기저율=0.5667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00055 auc=0.550 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00038 auc=0.529 out_max=0.3296 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
  …
2026-08-24 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-24 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-24 08:55:20 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=11203, ver=5)
2026-08-24 08:55:21 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-24 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 118 | 08:41:04 | 08:41:12 | 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×242

**컴포넌트 상위 15** — `Calibration`×228, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20260824_MICRO.log` — 32.1KB · 87행 · 최종 08:59:31

- 형식 평문 · 시각 인식 87행 · DEBUG=87

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:45:20 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1087.28/3 ask1=1087.62/2 mp={'microprice_tick': 1087.484, 'midprice_tick': 1087.45, 'depth_bias_tick': 0.323} mlofi_tick=None queue=None
2026-08-24 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1087.30/1 ask1=1087.62/2 mp={'microprice_tick': 1087.4067, 'midprice_tick': 1087.46, 'depth_bias_tick': 0.1322} mlofi_tick=4.2833 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-08-24 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1087.30/1 ask1=1087.62/2 mp={'microprice_tick': 1087.4067, 'midprice_tick': 1087.46, 'depth_bias_tick': 0.1322} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-08-24 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1087.28/3 ask1=1087.62/2 mp={'microprice_tick': 1087.484, 'midprice_tick': 1087.45, 'depth_bias_tick': 0.323} mlofi_tick=-4.2833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-24 08:45:21 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1087.60/4 ask1=1087.62/2 mp={'microprice_tick': 1087.6133, 'midprice_tick': 1087.61, 'depth_bias_tick': 0.3785} mlofi_tick=7.2833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-08-24 08:58:29 [DEBUG] MICRO: [MICRO-TICK] #5000 bid1=1093.28/1 ask1=1093.46/1 mp={'microprice_tick': 1093.37, 'midprice_tick': 1093.37, 'depth_bias_tick': 0.1329} mlofi_tick=0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-24 08:58:51 [DEBUG] MICRO: [MICRO-TICK] #5100 bid1=1093.12/1 ask1=1093.32/1 mp={'microprice_tick': 1093.22, 'midprice_tick': 1093.22, 'depth_bias_tick': -0.1133} mlofi_tick=1.2 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-24 08:59:00 [DEBUG] MICRO: [MICRO-MINUTE] #14 ts=2026-08-24 08:58:00 close=1093.56 bias=0.008253 slope=0.654079 depth_bias=0.0988 mlofi_norm=-0.016449 mlofi_pressure=-1 mlofi_slope=6.390000 queue_signal=-0.0513 queue_ma=-0.0092 queue_momentum=-0.0486 depletion=0.5051 refill=0.4949 imbalance…
2026-08-24 08:59:14 [DEBUG] MICRO: [MICRO-TICK] #5200 bid1=1093.50/1 ask1=1093.84/1 mp={'microprice_tick': 1093.67, 'midprice_tick': 1093.67, 'depth_bias_tick': -0.2761} mlofi_tick=-1.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-08-24 08:59:31 [DEBUG] MICRO: [MICRO-TICK] #5300 bid1=1092.14/1 ask1=1092.36/2 mp={'microprice_tick': 1092.2133, 'midprice_tick': 1092.25, 'depth_bias_tick': -0.0198} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
```

</details>

**채널** — `MICRO`×87

**컴포넌트 상위 15** — `MICRO-TICK`×73, `MICRO-MINUTE`×14

### `logs/20260824_DATA.log` — 914B · 4행 · 최종 08:58:54

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:58:24 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152835 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-24 08:58:24 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-24 08:58:54 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152837 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-24 08:58:54 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
  …
2026-08-24 08:58:24 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152835 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-24 08:58:24 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-24 08:58:54 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=152837 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-24 08:58:54 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
```

</details>

**채널** — `DATA`×4

**컴포넌트 상위 15** — `CybosInvestor`×4

### `logs/20260824_PROBE.log` — 1.7KB · 11행 · 최종 08:58:54

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:20 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-08-24 08:58:24 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-24 08:58:24 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-24 08:58:24 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-24 08:58:24 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-08-24 08:58:54 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-24 08:58:54 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-24 08:58:54 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-24 08:58:54 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-08-24 08:58:54 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:24 | 08:58:54 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

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

### 메인 스레드 블로킹 1건 · 최대 2859ms · 5초 초과 0건

상위 — 2859ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260824_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:23 2026-08-24 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2859ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2859 band=INFO since_pipe_s=NA
```

### `logs/20260824_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.419
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
```

### `logs/20260824_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00129 auc=0.498 out_max=0.5673 (기준 auc<0.53 and span<0.020, 기저율=0.5667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00055 auc=0.550 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00038 auc=0.529 out_max=0.3296 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260824_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:12 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260824_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:20 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 08:55

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260824_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:48 [INFO] 활성화 | file=logs\crash_fault.log PID=25592 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 88 | 08:49:02 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 57 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260824_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:20 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0118) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 64 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0311) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 57 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0285) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| 20260817 | 17:58 | 로그 본문 |
| **중앙값** | **17:02** | 기준선 |
| **오늘 20260824** | **08:59** | 로그 본문 |

- 델타 **-483분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.2MB · 마지막 갱신 2026-08-23 22:20

최근 헤딩 8개:
```
### [12] 스킬 템플릿 정합성
## 2026-08-23 (MW0602 487차 — 멀티PC 정책 폐기 + F-8 MW0602 한정 권고 + MW0601 이관 기록)
### [결정 — 사용자] 멀티PC 정책 폐기 (2026-08-23부)
### [권고 — MW0602 한정] F-8 캠페인 채널 [50]·[51] 생산부 결손 (0821 이상점 1-17)
### [파생 권고] F-9 채널 번호 [51] 중복 — `dev` 단독 재배정
### [기록] MW0601 이관 점검사항 분리
### [구현 — 같은 세션 후속] F-8(B) + F-9 집행 (사용자 승인: "남은 결정사항 1, 2 구현해")
## 2026-08-23 (MW0601 — `MW0601_이관_점검사항_20260823.md` 7건 조사)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
사전등록 블록 주석([54] 명기 +
  [55] 블록의 예약 주석을 배정 완료로)·모듈 docstring 4곳. **채널 키 문자열 불변**
  (`const_out_horizon_watch` — 이력 식별자, 461차 mdd_pct 교훈).
**검증**:
- `py_compile` py310_64 전부 + settings는 py37_32 병행 통과.
- 불변식 3종 `tests/test_487_campaign_channel_hygiene.py` **3/3 PASS** —
  ① 요약표 채널 번호 유일성(리터럴 행 + `_row_462` 포맷 행 수집) ② F-9 재배정
  유지([54] 존재·[51] ConstOut 부재·저변동성 [51] 유지) ③ F-8(B) 배선 생존.
- **실생성 검증**(py310_64, `--out-dir` 스크래치패드 — 금요일점검 폴더 오염 방지):
  요약표 [50]/[54] 둘 다 `🚫 NOT_AVAILABLE(브랜치 생산부 없음)` · `[51]` 요약행
  1개(저변동성) · metrics json `direction_bias_watch`/`const_out_horizon_watch`에서
  `error`/`no_data` 필드 **소멸**, `NOT_AVAILABLE_ON_THIS_BRANCH` **명시** —
  **O-21(08-28 금 EOD) 기대값 사전 충족 확인.** 정식 판정은 08-28 자동 생성본으로.
⚠ 판정식·합격선·`VALIDATION_CAMPAIGN` 사전등록 값은 일절 무변경 — 바뀐 것은
표기 층(번호·어휘)과 실행 가드뿐이다.

---

## 2026-08-23 (MW0601 — `MW0601_이관_점검사항_20260823.md` 7건 조사)

**요청**: 487차 멀티PC 정책 폐기 시점에 dev(MW0602)가 남긴 "MW0601 몫" 확인사항
7건을 조사하고 수정할 사항을 제안.

**결과 — 6건 조치 불필요, 1건에서 실제 운영 문서 3개 드리프트 발견**:

1. 채널 [50]·[51] 소비부·생산부 정합 — `build_report(days=7)` 직접 실행해 확인.
   [50]=`ALERT_BIAS`(SHORT 초과 발행, 3m·5m Bonferroni 생존), [51]=`INSUFFICIENT`
   (버킷 15/10, 각 20 필요 — `data_start=2026-08-12` 이후 정상적인 표본 부족 상태,
   `error`/`NOT_AVAILABLE` 아님). 둘 다 정상 동작.
2. 채널 번호 [51] 중복 — v9-dev에는 dev의 462차 저변동성 채널이 없어 애초에 충돌
   없음(전 세션에서 이미 [54] 재배정 미적용으로 처리·확정 — `302c8b5`).
3. `phases.md` B-1·B-2 — v9-dev는 **483차**가 이미 독립적으로 동일 취지 정정
   완료(`T-30 채점 유지` / `GBM 조건부 트리거 3종`). dev의 486차 정정과 세션
   번호만 다를 뿐 조치 완료 상태 동일.
4. `utils/analysis_db.py` — v9-dev 네이티브 모듈(479차), import 정상,
   `monthly_cleanup.py`의 `guard_intraday()` 경로 정상 배선 확인.
5. **🔴 실제 조치 필요했음** — 주간 PC 대조 의무 종료는 `DECISION_LOG`/`NEXT_TODO`
   에는 반영됐지만, 실제 운영 문서 3개가 여전히 폐기된 관행을 지시하고 있었다:
   - `docs/정기점검/금요일점검/weekly_prompt.txt`: MW0602 폴더 대조·
     `cmp_summary`/`cmp_metrics` 실행 지시 잔존
   - `.claude/skills/mireuk-daily-check/SKILL.md` §6: "세션 차수는 원격(git)
     기준으로 맞춘다(392차 관행)" 잔존(항목 ⑥의 "각자 관리" 원칙과 불일치)
   - `.claude/skills/mireuk-daily-check/RUN_ON_MW0602.md`: dev 브랜치 전용
     실행 지시서가 이전 체리픽(469차)에 얹혀 v9-dev로 잘못 들어옴(기능적
     무해 — 자체 `branch=="dev"` 가드로 v9-dev에서는 즉시 중단됨. 그래도 잔재)
   → 3건 모두 사용자 승인 받아 수정(`f628b83`).
6. dev_memory 세션 차수 — PC명 병기 유지 권고와 v9-dev의 기존 관행이 이미 일치.
7. `dev` push/pull 의무 없음 — 순수 정책 항목, 코드·문서 조치 대상 아님.

**Why 이 발견이 중요한가**: "결정을 DECISION_LOG에 적었다"와 "그 결정이 실제
운영 절차에 반영됐다"는 별개다 — CLAUDE.md 캠페인 절이 경고하는 것과 같은
계열의 함정("판정과 결정은 별개", 404차 후속11)이 여기서는 "정책과 실제 운영
문서" 축으로 재현됐다. 앞으로 정책성 결정을 기록할 때는 **그 정책을 실행하는
운영 문서(prompt/skill 파일)까지 함께 확인**할 것.

```

</details>

### dev_memory/NEXT_TODO.md — 1.1MB · 마지막 갱신 2026-08-23 22:21

최근 헤딩 8개:
```
### 481차 후속2 — 장후 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 483차 — 장전 점검 (MW0601, 2026-08-21 금 · 분석만, 코드 0건)
### 483차 후속 — 장중 점검 (MW0601, 2026-08-21 금 · 분석만, 코드 0건)
### 483차 후속2 — 장후 점검 (MW0601, 2026-08-21 금 · 분석만, 코드 0건)
## 2026-08-23 (MW0602 487차 — 멀티PC 정책 폐기 + F-8 MW0602 한정 권고)
### 사용자 승인 대기 — 승인 시 즉시 구현 가능 → ✅ **같은 날 사용자 승인으로 구현 완료**
### 백로그 (P3 — 기한 없음)
### 폐기 처리
```

미완료 체크박스 **1810건** (끝에서 30건)
```
- [ ] **O-15 (장후) CB③ 판정 가능 시간 종일 비율** — 12:28 현재 24.4%(51/209분).
- [ ] **O-16 (장후) 오늘 최종 진입 0건 여부** — 13:00 `OTHER`→`LUNCH_RECOVERY` 전환 후 진입 발생 여부.
- [ ] **`references/report_template.md` 갱신 (P2)** — 아직 `-pre`/`-intra`/`-post` 3파일 형식을
- [ ] **P1-A `ConfFloorGuard` 3상태 카운터를 리셋 전에 읽는다 (P1 · 이상점 1-9)** —
- [ ] **P2-H `monthly_cleanup.py` 표준출력 UTF-8 강제 (P2 · 이상점 1-10)** —
- [ ] **P2-I `trades.exit_stage` 컬럼 신설 — 손절과 TP1-후 트레일을 가른다 (P2 · 이상점 1-11 · 계측 4원칙 ①)** —
- [ ] **P2-K 수집기 §2에 실질 변경 파일 수·파일명 병기 (P2 · 이상점 1-14 · F-5/P2-B 강화)** —
- [ ] **고도화 ⑦ CORE 피처 건강도 일별 1행 (`core_feature_health`)** —
- [ ] **고도화 ⑧ 캠페인 [28]에 `binding_gate` 빈도표 추가 (판정 미관여 게이지)** —
- [ ] **고도화 ⑨ `RECALIBRATOR_DECISIONS` 레지스트리 신설** —
- [ ] **고도화 ⑩ `[MainStall]` 섀도 분석에 판별 질의 2개 **사전등록**** —
- [ ] ~~**① 진입 호라이즌 경계 `ENTRY_HORIZON_B1/B2` — 갱신 / 동결 / 재검토 중 하나를 명시 결정하고 기록**~~ —
- [ ] **② 캠페인 [46] HurstGate 임계 위치 — 첫 FAIL 판정에 대한 결정 등록** —
- [ ] **③ `ATRCeilingRecal` 첫 UPDATE 격상 처분** —
- [ ] **N-1 (다음 장후) `ConfFloorGuard` 3상태** — P1-A 미적용이면 또 `0분·0분·0분`인지
- [ ] **N-2 (다음 장후) 메인 스레드 정지** — 5초 초과 건수·최대·`band=WARN` 비율.
- [ ] **N-3 (다음 장후) CB③ ready 종일 비율** — 3거래일 연속 50% 미만이면
- [ ] **N-4 (다음 장후) `cvd_divergence` 이중 축** — ①`identity 강제` 건수·피처 구성
- [ ] **N-5 (다음 장후) 3m 호라이즌 / R-1** — `model_live_daily` 3m `live_acc`와 `ConstOut`
- [ ] **N-6 (2026-08-28 금) `[EntryHorizonRecal]` 6주차** — 하락 추세 지속이면
- [ ] **N-7 (2026-08-28 금) 월간 로그 정리** — P2-H 미적용이면 **또 `FAIL(rc=1)`이 나와야
- [ ] **N-8 (2026-08-28 금) 캠페인 [9]** — 오늘 차단 10건 resolve 후 n=37→47 근처에서
- [ ] **N-9 (2026-08-28 금) 캠페인 [46]** — 2주 연속 FAIL인지, OOS 표본 증가 시
- [ ] **N-10 (매 장후 누적) 15:10 강제청산 실집행** — 누적 **0회** 유지.
- [ ] **N-11 (다음 장후) 등급 인플레 일자단위** — 오늘 원시C→최종A **3건**
- [ ] **N-12 (다음 장전) `py37_32` 런타임 버전 (O-5 재이월)** — scipy 1.5.4 / joblib 1.1.1.
- [ ] **N-13 (다음 장전) 미커밋 실질 변경** — `git diff -w --stat` 실측치 병기.
- [ ] **O-21 (08-28 금 EOD) — 정식 판정은 자동 생성본으로.** 오늘 생성본은 스크래치
- [ ] **[50]/[51] 생산부 `dev` 자체 재구현 여부** — 소비자가 생기면(O-19 판정 필요
- [ ] **`monthly_cleanup` 장중 가드 자체 구현 여부** — `utils/analysis_db.py` 체리픽
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
) / C 유지 1건(1승 +5,355원). **손익 결론 재론 금지** —
      481차 후속 [5] R-후보 강등(반증) · 캠페인 [13] 📌 부결 확정. **일자단위 누적만.**
- [ ] **N-12 (다음 장전) `py37_32` 런타임 버전 (O-5 재이월)** — scipy 1.5.4 / joblib 1.1.1.
      **점검 세션이 리눅스 샌드박스면 확인 불가**하다는 사실이 오늘 드러났다(사유 변경).
      영구 해결책: **「기동 시 1회 버전 로그」 고도화** 또는 사용자 콘솔 1회 확인.
      EOD(`py310_64`)는 `Python 3.10.20 64-bit` / `sklearn 1.0.2` / `numpy 1.26.4` 확인됨.
- [ ] **N-13 (다음 장전) 미커밋 실질 변경** — `git diff -w --stat` 실측치 병기.
      실질 변경에 **코드 파일이 섞이면 즉시 보고**.

**⚠ 기한 임박 — CB② 재검토 2026-08-29는 토요일이다** (기등록 항목 재확인).
실무 판정 가능일은 **2026-08-28(금)** 또는 **2026-08-31(월)**. 오늘 기준 8일 남음.
`CB_CONSEC_STOP_LIMIT` 9999 → 2~3 복원 여부는 실전 전환 기준 ⑤이며, CB②가 9999인 동안
조건 ②는 CB③~⑤로만 충족해야 한다.

---

## 2026-08-23 (MW0602 487차 — 멀티PC 정책 폐기 + F-8 MW0602 한정 권고)

> 사용자 결정: **멀티PC 정책 2026-08-23부 폐기.** `dev` = MW0602 단독 운영.
> 상세·범위는 `DECISION_LOG.md` 487차, MW0601 몫은
> `docs/정기점검/MW0601_이관_점검사항_20260823.md`(스냅샷, 이후 갱신 없음).

### 사용자 승인 대기 — 승인 시 즉시 구현 가능 → ✅ **같은 날 사용자 승인으로 구현 완료**

- [x] **F-8(B) — 채널 [50]·[54] `NOT_AVAILABLE_ON_THIS_BRANCH` 표기** (권고 확정안).
  `generate_validation_campaign_report.py` 소비부 분리 표기. (A) 체리픽은 **선택지에서
  제거**(정책 폐기로 근거 소멸). 검증 O-21(08-28 금 EOD).
  ⚠ O-19(방향 편향)는 [50] 재구현 전까지 **기록만** — 판정 불가 상태를 표기할 것.
  ✅ **구현 완료(487차 후속)** — 생산부 **존재 감지형**으로 배선(모듈 spec /
  `PRAGMA table_info`): 생산부가 dev에 생기면 자동 복귀, 코드 재수정 불요.
  실생성 검증(스크래치 --out-dir): 요약표 [50]/[54] 🚫 표기 + metrics json에서
  `error`/`no_data` 소멸·`NOT_AVAILABLE_ON_THIS_BRANCH` 명시 — **O-21 조건 사전 충족**.
- [x] **F-9 — ConstOut 채널 번호 `[51]` → `[54]` 단독 재배정** (양 PC 합의 요건 소멸).
  [55]는 486차 선점 · settings.py 주석이 [54]를 예약함. 키 문자열 불변.
  F-8(B)와 **한 커밋** 권장. ✅ **구현 완료(487차 후속, F-8(B)와 한 커밋)** —
  요약행·상세절 헤더·settings 주석·모듈 docstring 4곳 갱신, `구 [51]` 병기.
  실생성 검증: `[51]`로 시작하는 요약행 **1개**(저변동성)뿐.
  불변식 고정: `tests/test_487_campaign_channel_hygiene.py` 3종
  (요약표 채널 번호 유일성 / F-9 재배정 유지 / F-8(B) 배선 생존) **3/3 PASS**.

- [ ] **O-21 (08-28 금 EOD) — 정식 판정은 자동 생성본으로.** 오늘 생성본은 스크래치
  검증용이며 금요일점검 폴더에 넣지 않았다. 기대값: [50]/[54] 두 채널
  `NOT_AVAILABLE_ON_THIS_BRANCH` 표기 + `[51]` 요약행 1개.

### 백로그 (P3 — 기한 없음)

- [ ] **[50]/[51] 생산부 `dev` 자체 재구현 여부** — 소비자가 생기면(O-19 판정 필요
  시점 등) 재론. 그전에는 `NOT_AVAILABLE` 유지.
- [ ] **`monthly_cleanup` 장중 가드 자체 구현 여부** — `utils/analysis_db.py` 체리픽
  안 함. 현행(경고 후 진행) 유지, EOD 체인 한정 발화라 실위험 낮음.

### 폐기 처리

- [x] **주간회의 안건 (4) 「멀티PC 컨벤션 보강」 폐기** — 체리픽 관행 종료로 목적 상실.
- [x] **주간 PC 대조(`cmp_summary`/`cmp_metrics`) 정기 절차 제외** — 스크립트는
  과거 주차 소급용으로 보존.
- ⚠ **CB② 복원(기한 2026-08-29, 남은 거래일 5)은 정책 폐기와 무관 — 그대로 유효.**

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

### `data/heartbeat_MW0601_20260824.json` — 244B · 08-24 08:59:21
```json
{
 "pid": 25592,
 "written_at": "2026-08-24T08:59:21",
 "beat_epoch": 1787529560.721075,
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

### `docs/정기점검/매일점검` — 64개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.0KB | 08-23 16:51 |
| `docs/정기점검/매일점검/MW0601-20260821-점검리포트.md` | 208.7KB | 08-21 16:54 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_post.md` | 74.4KB | 08-21 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_intra.md` | 57.0KB | 08-21 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_pre.md` | 46.8KB | 08-21 08:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_pre.md` | 49.0KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_post.md` | 70.5KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_intra.md` | 61.3KB | 08-20 22:24 |

### `docs/정기점검/금요일점검` — 58개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.2KB | 08-23 22:09 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260821.md` | 4.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260821.json` | 2.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md` | 26.2KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json` | 34.4KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json` | 91.9KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260824_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 486건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260824*.log` (Windows) / `grep 강제청산 logs/*20260824*.log`*