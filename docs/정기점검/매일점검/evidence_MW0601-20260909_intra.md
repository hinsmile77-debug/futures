# 미륵이 증거 다이제스트 — 2026-09-09 / INTRA

- 생성 2026-09-09 12:27:51 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/zen-upbeat-franklin/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260909` · `2026-09-09` · `260909` · `0909`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **20개** 파일 · 20개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260909.log` | 125B | 09-09 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260909.log` | 140B | 09-09 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260909.json` | 244B | 09-09 12:27 |
| `launcher_{DATE}_084001_16479.log` | 1 | `logs/Mireuk_batch/launcher_20260909_084001_16479.log` | 10.9MB | 09-09 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260909.log` | 8.6KB | 09-09 12:02 |
| `retrain_intraday_{DATE}_093600.log` | 1 | `logs/retrain_intraday_20260909_093600.log` | 2.8KB | 09-09 09:36 |
| `retrain_intraday_{DATE}_103000.log` | 1 | `logs/retrain_intraday_20260909_103000.log` | 2.8KB | 09-09 10:30 |
| `retrain_intraday_{DATE}_110900.log` | 1 | `logs/retrain_intraday_20260909_110900.log` | 2.8KB | 09-09 11:09 |
| `retrain_intraday_{DATE}_114800.log` | 1 | `logs/retrain_intraday_20260909_114800.log` | 2.8KB | 09-09 11:48 |
| `{DATE}_DATA.log` | 1 | `logs/20260909_DATA.log` | 184.0KB | 09-09 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260909_DEBUG.log` | 131.2KB | 09-09 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260909_HEALTH.log` | 3.4KB | 09-09 12:10 |
| `{DATE}_HOGA.log` | 1 | `logs/20260909_HOGA.log` | 28.7MB | 09-09 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260909_LEARNING.log` | 178.8KB | 09-09 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260909_MICRO.log` | 578.6KB | 09-09 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260909_PROBE.log` | 55.7KB | 09-09 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260909_SIGNAL.log` | 376.3KB | 09-09 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260909_SYSTEM.log` | 10.4MB | 09-09 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260909_TRADE.log` | 167B | 09-09 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260909_WARN.log` | 15.1KB | 09-09 12:20 |

## 2. 코드·커밋 상태

- HEAD `5969d44` · 브랜치 `v9-dev` · 미커밋 552건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
… 외 512건
```

**당일(2026-09-09) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
5969d44 [MW0601] 548차 후속: 리포트 제10부 커밋 해시·푸시 결과 기입
909d236 [MW0601] 548차: 장후 자동조치 — 09-08 점검 산출물 커밋 + 스테일 락 회수(코드 변경 없음)
96b0d61 [MW0601] 546차 후속: dev 적응 이식 완료 기록
5a11474 [MW0601] 545·546차: ProfitGuard L1~L4 배지 복구 + 판정 손익을 시스템 자동매매 한정으로
698c4ae [MW0601] 542차 후속: dev 적응 이식 완료 기록
8e04770 [MW0601] 542차 후속: dev 이식 판단 기록 — 수동 맥점 버튼은 보류
a21e270 [MW0601] 542차: 수동 맥점 산출 버튼 (관측 전용, 매매정책 무변경)
91d99da [MW0601] 534차 후속: 첫 라이브 맥점 산출 점검 — 계측 결손 5건 (매매정책 무변경)
3111e4b [MW0601] 542차 곁가지: 540차 GP 교차 피처 NameError — feature_builder 임포트 누락
f2343d8 [MW0601] 541차 후속: 판정기 테스트 — 런타임 DB 부재 시 스킵
3f2b3c6 [MW0601] 541차: GP 교차 채널 판정기 배선 (기록 전용, 매매정책 무변경)
5a5fec1 [MW0601] 540차: GOLDEN POWER 교차 — 사전등록 2채널 배선 (기록 전용, 매매정책 무변경)
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

_본문 미열람(설정): `20260909_HOGA.log` 28.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/18개 (중요도순). 제외: `retrain_intraday_20260909_114800.log`, `retrain_intraday_20260909_103000.log`, `20260909_MICRO.log`, `20260909_DATA.log`, `20260909_PROBE.log`, `launcher_20260909_084001_16479.log`, `20260909_DEBUG.log`, `mainstall_traceback_20260909.log`_

### `logs/20260909_TRADE.log` — 167B · 2행 · 최종 08:41:03

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-09 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-09 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-09 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260909_WARN.log` — 15.1KB · 104행 · 최종 12:20:02

- 형식 평문 · 시각 인식 104행 · WARNING=104

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-09 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-09-09 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-09-09 08:41:07 [WARNING] SYSTEM: [SessionStateDrop] 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-08 → 2026-09-09)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단이다
2026-09-09 08:41:07 [WARNING] SYSTEM: [SessionStateDrop] 완료 마커 소실 ['eod_retrain_ok_date', 'p8_last_success_date'] — 이 쓰기가 지웠다 (호출부=session_recovery_service.py:159 mtime=08:41:07 남은마커=없음). 호출부가 _read_session_state() 없이 dict 를 새로 만들었을 가능성
  …
2026-09-09 12:12:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2094ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2094 band=INFO since_pipe_s=0.3
2026-09-09 12:12:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1320ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-09-09 12:18:01 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 +0.247% (임계 ±0.227%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-09-09 12:20:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1064ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-09-09 12:28:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1227ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
```

</details>

**WARNING — 태그 13종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 29 | 08:41:06 | 12:12:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 12 | 09:00:01 | 11:49:05 | total=1397ms | S0=4ms S1=30ms S2=0ms S3=0ms S4=161ms S5=468ms S6=668ms S7=57ms S8=10ms |
| `CB⑤` | 12 | 09:00:01 | 11:49:05 | 파이프라인 1397ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 11 | 09:00:01 | 12:09:01 | level=WARNING degraded=OFF | latency=1397ms | quality=1.00 | cache_age=47s | exceptions_10m=0 |
| `SHAP` | 10 | 11:02:01 | 12:28:02 | 슬로우 감지 905ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `ScalerRefresh` | 9 | 09:05:00 | 12:18:01 | 5분 누적 수익률 +0.372% (임계 ±0.263%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `HealthPolicy` | 5 | 09:01:00 | 11:50:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1397ms quality=1.00 cache=0s exc10m=0) | cause=S6(668ms) |
| `ConstOut` | 4 | 09:35:00 | 11:47:02 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| `MainStallTrace` | 3 | 09:00:06 | 12:02:04 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260909.log |
| `Brier` | 3 | 12:07:00 | 12:09:00 | 과신 경고 | 이동평균=0.356 > 0.35 |
| `SessionStateDrop` | 2 | 08:41:07 | 08:41:07 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-08 → 2026-09-09)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Contrarian` | 2 | 09:58:00 | 09:58:00 | ACTIVE | acc30m=6.7% streak=12 regime=NEUTRAL 역베팅방향=LONG |

**채널** — `SYSTEM`×93, `HEALTH`×11

**컴포넌트 상위 15** — `LiveDBG`×29, `PipePerf`×12, `CB⑤`×12, `Health`×11, `SHAP`×10, `ScalerRefresh`×9, `HealthPolicy`×5, `ConstOut`×4, `MainStallTrace`×3, `Brier`×3, `SessionStateDrop`×2, `Contrarian`×2, `CB③-P4`×2

### `logs/20260909_SYSTEM.log` — 10.4MB · 79886행 · 최종 12:27:51

- 형식 평문 · 시각 인식 79879행 · INFO=79879, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=24768 | 행감지=30s all_threads=True
2026-09-09 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-09 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-09 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-09 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-08) 종가 버퍼 로드: 365봉
  …
2026-09-09 12:29:01 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122901 price=1117.96 cum_vol=87317 auction_code=40 recv_type=50
2026-09-09 12:29:01 [INFO] SYSTEM: [CybosRT-TICK] #76600 code=A0569 raw_time=122901 parsed=12:29:01 price=1117.96 vol=4 bid1=1117.92 ask1=1117.96 flag=49 side=BUY anchor=4/0
2026-09-09 12:29:01 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122901 price=1117.96 cum_vol=87318 auction_code=40 recv_type=50
2026-09-09 12:29:01 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122901 price=1117.96 cum_vol=87322 auction_code=40 recv_type=50
2026-09-09 12:29:02 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122901 price=1118.00 cum_vol=87323 auction_code=40 recv_type=50
```

</details>

**채널** — `SYSTEM`×79879

**컴포넌트 상위 15** — `CybosRT-AUCTION`×76603, `CybosInvestorRaw`×832, `CybosRT-TICK`×771, `CybosRT-ROLLOVER`×224, `BAR-CLOSE`×224, `CVD-ANCHOR`×224, `TickUI`×223, `S6Detail`×210, `PipePerf`×210, `System`×59, `MicroRegime`×45, `RegimeFingerprint`×38, `IntradayRegime`×25, `OptionChain`×24, `CybosSub`×21

### `logs/20260909_SIGNAL.log` — 376.3KB · 3273행 · 최종 12:27:00

- 형식 평문 · 시각 인식 3273행 · WARNING=1594, INFO=1679

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
  …
2026-09-09 12:29:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-09-09 12:29:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=49.6% grade=X regime=NEUTRAL
2026-09-09 12:29:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-09-09 12:29:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=49.6% grade=X micro=추세장
2026-09-09 12:29:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.496<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1050 | 09:00:02 | 12:18:01 | 1m 'macro_vix' scale=0.0005 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 144 | 09:00:00 | 11:53:00 | ts=08:59 horizon=1m age=1m max_z=+12.77(institution_futures_net) extreme=1 adj=1 |
| `Model` | 132 | 09:00:00 | 11:49:05 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerRefresh` | 120 | 08:45:07 | 10:35:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0202) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Checklist` | 95 | 09:06:00 | 12:27:00 | 신뢰도 미달 34.9% < 38.5% → 강제 X등급 |
| `WeightCollapse` | 46 | 09:07:00 | 12:28:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 4 | 09:35:00 | 11:47:02 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 3 | 09:00:00 | 11:20:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3990 (conf_floor=0.330, min_conf=0.399, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3273

**컴포넌트 상위 15** — `ScalerFloor`×1074, `SIGNAL`×420, `Ensemble`×210, `ZeroDiag`×210, `FQAdj`×209, `MetaGate`×180, `Model`×162, `ScalerRefresh`×150, `ScalerMonitor`×144, `Checklist`×95, `ATR-Horizon`×84, `WeightCollapse`×46, `차단`×46, `MicroRegime`×45, `ToxicityGate`×41

### `logs/20260909_LEARNING.log` — 178.8KB · 1657행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1657행 · WARNING=159, INFO=1498

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00194 auc=0.426 out_max=0.3634 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00160 auc=0.518 out_max=0.5009 (기준 auc<0.53 and span<0.020, 기저율=0.5000 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3299 < conf_floor=0.3300 (span=0.00223 auc=0.549 out_max=0.3299, 기저율=0.3286 n=140) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-09 08:40:50 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3394 < conf_floor=0.3300 (n=145) → 보정 재적용
  …
2026-09-09 12:29:00 [INFO] LEARNING: ✗ 10m 예측 실패 (conf=34.5% 예측=FL 실제=DN)
2026-09-09 12:29:00 [INFO] LEARNING: ✓ 15m 예측 적중 (conf=65.5% FL)
2026-09-09 12:29:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=64.0% 예측=FL 실제=DN)
2026-09-09 12:29:01 [INFO] LEARNING: [OnlineLearner] 30m 초기 학습 완료
2026-09-09 12:29:01 [INFO] LEARNING: [SGD] 6건 학습 | SGD비중=30% 50분정확도=25.0%
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 158 | 08:40:50 | 12:04:00 | 축퇴 감지 — span=0.00194 auc=0.426 out_max=0.3634 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 1 | 11:47:01 | 11:47:01 | total=976ms raw_fetch=8ms pred_select=33ms pred_update=51ms pred_insert=23ms verified=3 |

**채널** — `LEARNING`×1657

**컴포넌트 상위 15** — `LEARNING`×671, `Calibration`×311, `SGD`×210, `sigma`×197, `Bias⚠`×70, `Bias`×62, `MetaConf`×41, `ScalerWarmup`×30, `OnlineLearner`×24, `BiasReset`×8, `GBM-64`×8, `GBM`×8, `SHAP`×7, `RF`×5, `ExtremityCorrector`×2

### `logs/20260909_HEALTH.log` — 3.4KB · 23행 · 최종 12:10:00

- 형식 평문 · 시각 인식 23행 · WARNING=11, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1397ms | quality=1.00 | cache_age=47s | exceptions_10m=0
2026-09-09 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=819ms | quality=1.00 | cache_age=106s | exceptions_10m=0
2026-09-09 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 336ms (표본 20분)
2026-09-09 09:37:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2572ms | quality=1.00 | cache_age=63s | exceptions_10m=0
2026-09-09 09:38:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=671ms | quality=1.00 | cache_age=122s | exceptions_10m=0
  …
2026-09-09 11:48:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=468ms | quality=1.00 | cache_age=22s | exceptions_10m=2 | exc_tags=[SHAP]×2 [GBM재학습중→lat임계 5000/10000ms]
2026-09-09 11:49:05 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2783ms | quality=1.00 | cache_age=87s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-09 11:50:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=411ms | quality=1.00 | cache_age=142s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-09 12:09:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=390ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-09 12:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=304ms | quality=1.00 | cache_age=56s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 11 | 09:00:01 | 12:09:01 | level=WARNING degraded=OFF | latency=1397ms | quality=1.00 | cache_age=47s | exceptions_10m=0 |

**채널** — `HEALTH`×23

**컴포넌트 상위 15** — `Health`×22, `HealthTrend`×1

### `logs/retrain_intraday_20260909_093600.log` — 2.8KB · 22행 · 최종 09:36:23

- 형식 평문 · 시각 인식 22행 · INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 09:36:00,839 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-09 09:36:00,839 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-09 09:36:00,840 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-09 09:36:00,840 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-09 09:36:00,840 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_eaa5c913.json
  …
2026-09-09 09:36:23,212 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-09 09:36:23,213 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-09 09:36:23,213 [INFO] LEARNING: [Retrain] 완료 | 19.0초 | 성공=1/1 호라이즌
2026-09-09 09:36:23,214 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.4s 데이터=4800행
2026-09-09 09:36:23,216 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_eaa5c913.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260909_110900.log` — 2.8KB · 22행 · 최종 11:09:22

- 형식 평문 · 시각 인식 22행 · INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 11:09:00,823 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-09 11:09:00,824 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-09 11:09:00,824 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-09 11:09:00,824 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-09 11:09:00,825 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_5b9410f0.json
  …
2026-09-09 11:09:22,498 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-09 11:09:22,499 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-09 11:09:22,499 [INFO] LEARNING: [Retrain] 완료 | 18.8초 | 성공=1/1 호라이즌
2026-09-09 11:09:22,500 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.7s 데이터=4800행
2026-09-09 11:09:22,502 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_5b9410f0.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 46 |
| 사이저 호출(`[Sizer]`) | 0 |

### 차단 사유 46건 · 13종

| 건수 | 사유 |
|---|---|
| 32 | 등급X — 미통과 항목: 2_confidence |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.4pt > ATR×5.0=9.4pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.7pt > ATR×5.0=7.5pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.4pt > ATR×5.0=8.0pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.1pt > ATR×5.0=8.0pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=7.8pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.5pt > ATR×5.0=7.3pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.7pt > ATR×5.0=7.2pt (시가=1102.28 반등위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×32

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 19건 · 최대 7047ms · 5초 초과 3건

상위 — 7047ms, 5204ms, 5094ms, 4875ms, 4579ms, 4453ms, 4313ms, 4235ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 7047ms | 1397ms | **5650ms (80%)** |
| 11:39:04 | 5094ms | 510ms | **4584ms (90%)** |
| 12:02:04 | 5204ms | 375ms | **4829ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260909_WARN.log`
```
--- ConstOut ×4(표본)
09:35:00 2026-09-09 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:29:00 2026-09-09 10:29:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:08:01 2026-09-09 11:08:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:47:02 2026-09-09 11:47:02 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×3(표본)
09:00:06 2026-09-09 09:00:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260909.log
11:39:04 2026-09-09 11:39:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260909.log
12:02:04 2026-09-09 12:02:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260909.log
--- [Brier] 과신 ×3(표본)
12:07:00 2026-09-09 12:07:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.356 > 0.35
12:08:00 2026-09-09 12:08:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.354 > 0.35
12:09:00 2026-09-09 12:09:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.350 > 0.35
--- [SHAP] 슬로우 ×8(표본)
11:02:01 2026-09-09 11:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 905ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:11:01 2026-09-09 11:11:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1134ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:28:01 2026-09-09 11:28:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 936ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:40:01 2026-09-09 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 929ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:10 2026-09-09 08:41:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
09:00:06 2026-09-09 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7047 band=WARN since_pipe_s=0.3
09:01:02 2026-09-09 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2531ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2531 band=INFO since_pipe_s=0.3
09:02:02 2026-09-09 09:02:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2375 band=INFO since_pipe_s=0.2
```

### `logs/20260909_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-09 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-09-09 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-09-09 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=105ms fit=38ms total=164ms
09:36:00 2026-09-09 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-09-09 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:05:00 2026-09-09 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:11:00 2026-09-09 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:16:00 2026-09-09 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
```

### `logs/20260909_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:00:00 2026-09-09 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3990 (conf_floor=0.330, min_conf=0.399, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:49:00 2026-09-09 10:49:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3808 ≥ 필요 0.3780 (span=0.0120, auc=0.552)
10:55:00 2026-09-09 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3715 < 필요 0.3780 (conf_floor=0.330, min_conf=0.378, span=0.0135, auc=0.560). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:02:00 2026-09-09 11:02:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3787 ≥ 필요 0.3780 (span=0.0181, auc=0.573)
--- ConstOut ×8(표본)
09:35:00 2026-09-09 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-09 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-09 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:02 2026-09-09 09:37:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-09 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-09 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-09 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-09 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
--- 안전망 ×8(표본)
09:07:00 2026-09-09 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-09 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-09 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-09 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260909_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00194 auc=0.426 out_max=0.3634 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00160 auc=0.518 out_max=0.5009 (기준 auc<0.53 and span<0.020, 기저율=0.5000 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:50 2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3299 < conf_floor=0.3300 (span=0.00223 auc=0.549 out_max=0.3299, 기저율=0.3286 n=140) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-09 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00184 auc=0.358 out_max=0.2508 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260909_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260909_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 11 | 08:41:06 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 09:00:01 [WARNING] total=1397ms | S0=4ms S1=30ms S2=0ms S3=0ms S4=161ms S5=468ms S6=668ms S7=57ms S8=10ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 09:00:01 [WARNING] total=1397ms | S0=4ms S1=30ms S2=0ms S3=0ms S4=161ms S5=468ms S6=668ms S7=57ms S8=10ms |
| 10:00 | 장중 초반 | 2 | 09:58:00 [WARNING] ACTIVE | acc30m=6.7% streak=12 regime=NEUTRAL 역베팅방향=LONG |
| 12:00 | 장중 중간점 | 3 | 12:01:01 [WARNING] 슬로우 감지 1060ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |

- 이 로그 생존구간: 08:41 ~ 12:28

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260909_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 508 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=24768 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2911 | 08:49:00 [INFO] code=A0569 raw_time=84900 price=1101.46 cum_vol=1000 auction_code=40 recv_type=50 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5988 | 08:54:00 [INFO] code=A0569 raw_time=85359 price=1101.96 cum_vol=1562 auction_code=40 recv_type=49 |
| 10:00 | 장중 초반 | 4656 | 09:54:01 [INFO] code=A0569 raw_time=95401 price=1115.44 cum_vol=32720 auction_code=40 recv_type=49 |
| 12:00 | 장중 중간점 | 4132 | 11:54:00 [INFO] code=A0569 raw_time=115359 price=1123.42 cum_vol=75309 auction_code=40 recv_type=50 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:29

**매분 루프 커버리지 09:00~15:10: 210/371분 (56.6%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:30 | 15:10 | 161 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260909_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:07 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0202) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 107 | 08:50:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 223 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0303) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 107 | 09:54:01 [WARNING] 신뢰도 미달 34.3% < 38.5% → 강제 X등급 |
| 12:00 | 장중 중간점 | 81 | 11:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:29

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260908 | 15:40 | 로그 본문 |
| 20260907 | 21:59 | 로그 본문 |
| 20260906 | 20:39 | 로그 본문 |
| 20260904 | 17:33 | 로그 본문 |
| 20260903 | 15:40 | 로그 본문 |
| **중앙값** | **17:33** | 기준선 |
| **오늘 20260909** | **12:29** | 로그 본문 |

- 델타 **-304분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.8MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-09 (MW0601 549차 — 장전 점검)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 위반)는 아니라고 판단한다. 확정을 원하면 `trades.db`에서
이 레그의 정확한 진입 시각을 장후에 조회할 것(장중 라이브 DB 스캔 금지 원칙 때문에
이번 세션에서는 조회하지 않았다).

### 병행 세션

이 세션이 도는 동안 병행 세션 없음(당일 커밋 0건, 장전 리포트 확인 이후 신규
산출물 없음 — `git log --since` 및 `ls -lt` 로 재확인).

### 부가 발견 — `.git/index.lock` 세션 중 생성, 세션 내 회수 불가

12:27:38에 0바이트 `.git/index.lock`이 생겼다(이 세션의 `branch`/`status`/`log` 명령은
전부 `--no-optional-locks`를 붙였음을 재확인 — 그쪽 원인 아님). 12:38 `git_lock_guard.py
--check` 재판정 결과 "스테일 확정(0바이트·git 프로세스 0개)"이었으나 `--reclaim`이
`Operation not permitted`로 실패했다(SKILL.md가 이미 기록한 리눅스 샌드박스 마운트
`unlink` 거부 문제, 2026-08-26 실측과 동일 계열). 시간대가 12:26:47 `collect_evidence.py`
실행과 겹치고, 그 다이제스트 §2가 "실질 변경 미측정(git diff 실패)"라고 자백하고 있어
그 실패한 `git diff` 호출이 원인일 가능성이 높다고 판단(확정 아님 — 544-6으로 후속 조사
등록). 사용자 조치로 올림(544-5), 코드 변경 없음.

## 2026-09-09 (MW0601 549차 — 장전 점검)

### 증상

1. `[SessionStateDrop]` 완료 마커(`p8_last_success_date`·`eod_retrain_ok_date`) 소실이
   08:41:07 오늘도 재발했다(`logs/20260909_WARN.log`). 09-07(이상점1-4)·09-08(로그 직접
   확인) 이어 **최소 3거래일 연속**.
2. 어제(543-1, P0) 24분간 이어졌던 `TradeInit` 무응답이 오늘은 재현되지 않음
   (`request_futures_balance TradeInit 완료 0ms`, 08:41:06).
3. 수집기(`collect_evidence.py`)의 `git diff` 측정이 오늘도 실패("실질 변경
   미측정") — 세션에서 수동으로 같은 명령을 돌리면 정상 작동(550 files changed,
   insertions=deletions 311117로 정확히 같아 대부분 EOL 차이로 추정).
4. `.git/index.lock` 세션 시작·종료 시점 모두 없음(정상).

### 원인

1은 이미 538-5에서 확정된 가설(`session_recovery_service.increment_session()`이
`_read_session_state()` 없이 새 딕셔너리를 만들어 두 키를 이어받지 못함) 그대로라
재조사하지 않았다(함정① 방지).
2는 원인 불명(재현 안 됨 자체가 정보). 근본 원인(타임아웃 가드 부재)은 미수정 상태로
남아 있어 낙관 판단은 보류.
3은 544-6에서 이미 등록된 조사 대상과 동일 패턴 재발.

### 결정

- 1(SessionStateDrop)은 이상점 1-1로 P1 기록, 신규 조사 없이 재발 사실만 추가. F-1
  본체 적용(538-4)은 여전히 사용자 승인 대기 — 이 세션에서 결정 변경 없음.
- 2(TradeInit)는 "이미 반영된 사안"으로 기록하고 543-1(P0) 자체는 닫지 않음 — 근본
  원인 미수정 상태이므로 오늘 안 일어났다고 낙관하지 않는다.
- 3(수집기 git diff 실패)은 이상점 1-2로 P2 기록, G-1(재시도 로직 + 실패 사유 구체화)
  고도화 제안 추가.
- 코드 변경 없음(장전 규약).

### Why

- 함정①(판정≠결정) — 이미 확정된 원인을 매번 "미규명"으로 되돌리면 다음 세션이 조사
  자원을 낭비한다.
- 계측 4원칙 — "표시 소실"과 "실제 실패"는 다른 사건이다. `data/eod_retrain_done_20260908.txt`
  등 완료 파일 실측으로 09-08 마감 자체는 정상이었음을 직접 확인했다.

### How to apply

- F-1(session_recovery_service.py) 적용은 여전히 사용자 승인 대기, 이 세션은 적용하지
  않음(장전 규약).
- G-1(수집기 git diff 재시도 로직)은 544-6과 통합해 이번 주 내 처리 권고.

### 검증

- 다음 거래일 아침 `[SessionStateDrop]` 재현 여부는 F-1 승인 전까지 계속 관측(O-p2로
  등록, 승인 시 해소 예정).
- TradeInit 무응답 재발 여부는 O-p3로 등록해 오늘 장중부터 관측.

### 병행 세션

이 세션이 도는 동안 병행 세션 없음(당일 커밋 0건, `docs/정기점검/매일점검/` 당일
산출물이 이 리포트가 최초 — `git --no-optional-locks log --since` 및 `ls -lt`로 확인).

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-04 (MW0601 532차 — 장후 점검)
## 2026-09-04 (MW0601 532차 후속 — 장후 자동조치)
## 2026-09-07 (MW0601 536차 — 장중 점검)
## 2026-09-07 (MW0601 537차 — 장후 점검, 종합 완성본)
## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)
## 2026-09-08 (MW0601 543차 — 장전 점검)
## 2026-09-08 (MW0601 544차 — 장중 점검)
## 2026-09-09 (MW0601 549차 — 장전 점검)
```

미완료 체크박스 **2524건** (끝에서 30건)
```
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
- [ ] **543-1 (P0, 신규 / F-1)** `collection/cybos/api_connector.py:430`의 `TradeInit(0)`
- [ ] **543-2 (P2, 고도화 제안)** FZ-1 워치독(`utils/freeze_watchdog.py`)이 첫 하트비트
- [ ] **543-3 (관측 예정, O-p1)** 다음 거래일 `crash_fault.log`에서 `TradeInit`이 다시
- [ ] **543-4 (관측 예정, O-p2)** 다음 거래일 아침 `[SessionStateDrop]`이 재현되는가 —
- [ ] **544-2 (장후 확인 필요)** 09:20:44 청산 이월 레그 1건(-5,024원, 오늘 열림 로그
- [ ] **544-5 (사용자 조치)** `.git/index.lock` 12:27:38 생성 — 12:38 재판정 결과
- [ ] **544-6 (P2, 고도화 제안)** `collect_evidence.py`의 "이 수집 실행은 락을
- [ ] **549-4 (이번 주, G-1)** `collect_evidence.py`의 git diff 측정부에 1회 재시도
- [ ] **O-p1 (오늘 장중 판정)** `[ConfFloorGuard]` 09:00:00 1건 — 장중 로그에서 복구
- [ ] **O-p3 (오늘 장중 판정, 543-1 재이월)** TradeInit 무응답 오늘 09:00~09:10 구간
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
확정**.
      538-4(F-1 본체 적용)로 승계.

## 2026-09-08 (MW0601 544차 — 장중 점검)

- [x] **544-1** 정체불명 외부 진입 — **6거래일 연속 재발**(09-01·09-04·09-07 장중·
      09-07 장후·09-08). 원인은 537-1에서 이미 확정(사용자 본인 모의투자 병행 수동
      테스트) — 재조사하지 않음. 오늘 7건/7계약, +72,991원(이월 레그 포함 시 계좌
      실손익 +67,967원), 09:39:12까지 전량 종결(15:10 훨씬 이전). 이상점 1-2로 P2
      기록(원인 기지·이익 마감이라 심각도 하향). G-2·G-4는 계속 승인/주간회의 대기.
- [ ] **544-2 (장후 확인 필요)** 09:20:44 청산 이월 레그 1건(-5,024원, 오늘 열림 로그
      없음)의 정확한 진입 시각을 `trades.db`에서 조회해 09-07 오버나이트(절대원칙 ①)
      위반이 아님을 확정할 것 — 장중 세션은 라이브 DB 스캔 금지 원칙 때문에 조회하지
      않았고, 정황상(같은 09:20대 외부 클러스터 + 09-07 15:11:06 FLAT 확인 기록) 위반
      아닐 것으로 잠정 판단만 해둠.
- [x] **544-3** 이월 처리표 — 장전 1-1 ✅해소(그대로 유지), O-p1·O-p2는 판정 시점이
      다음 거래일 장전이라 오늘 장중은 "판정 보류" 그대로 승계.
- [x] **544-4** 메인 스레드 블로킹 5초 초과 4건(최대 9,562ms, 12:24:08) — 482차 F-3
      섀도 계측 범위 내 정상 관측(스택 스냅샷 확인 결과 원인 전부 Qt/COM 메시지 펌프
      대기, 다른 스레드 정상). 신규 아님, 별도 조치 없음.
- [ ] **544-5 (사용자 조치)** `.git/index.lock` 12:27:38 생성 — 12:38 재판정 결과
      "스테일 확정"(0바이트·실행 중인 git 프로세스 0개)이나 리눅스 샌드박스 마운트
      제약으로 세션 내 회수 실패(`Operation not permitted`). Windows PC에서 직접
      `del .git\index.lock` 필요. 이 세션의 `branch`/`status`/`log` 명령은 전부
      `--no-optional-locks`를 붙였음을 재확인했다 — 원인은 그쪽이 아니라 12:26:47
      `collect_evidence.py` 실행 중 「실질 변경 건수」 측정용 `git diff` 호출이 실패한
      것으로 추정(다이제스트 §2 "실질 변경 미측정(git diff 실패)"과 시간이 일치).
- [ ] **544-6 (P2, 고도화 제안)** `collect_evidence.py`의 "이 수집 실행은 락을
      만들지 않았다" 자가점검(490차 F-F②)이 544-5의 실패한 `git diff` 호출을 놓쳤을
      가능성 — 자가점검이 diff 실패 **이전** 시점에 판정을 끝내는 구조인지 장후/다음
      세션에서 스크립트 코드로 확인할 것. 급하지 않음.

## 2026-09-09 (MW0601 549차 — 장전 점검)

- [x] **549-1** 이상점 1-1 — `[SessionStateDrop]` 3거래일 연속 재발(09-07·09-08·09-09)
      확인. 신규 조사 없이 재발 사실만 기록(함정① 방지). F-1 본체 적용은 538-4 승계,
      사용자 승인 대기 그대로.
- [x] **549-2** 543-1(TradeInit 24분 무응답, P0) 재현 여부 확인 — 오늘 08:41:06
      `TradeInit 완료 0ms`로 **재현 안 됨**. 다만 근본 원인(타임아웃 가드 부재) 미수정
      상태이므로 543-1 자체는 닫지 않는다. O-p3로 장중 재관측 등록.
- [x] **549-3** 이상점 1-2 — 수집기 `git diff` 측정 실패 재발(544-5·544-6과 동일 계열).
      세션에서 수동 재실행 시 정상 작동 확인(550 files changed, insertions=deletions
      311117로 동일 — 대부분 EOL 차이로 추정, 실내용 변경 아닐 가능성 높음).
- [ ] **549-4 (이번 주, G-1)** `collect_evidence.py`의 git diff 측정부에 1회 재시도
      로직 + 실패 사유 구체화(현재 "git diff 실패"로만 뭉뚱그려짐) 추가. 544-6과
      통합 처리 권고.
- [ ] **O-p1 (오늘 장중 판정)** `[ConfFloorGuard]` 09:00:00 1건 — 장중 로그에서 복구
      메시지 확인 여부로 해소/지속 판정.
- [ ] **O-p3 (오늘 장중 판정, 543-1 재이월)** TradeInit 무응답 오늘 09:00~09:10 구간
      재발 여부 — 없으면 "오늘도 미재현" 누적, 있으면 즉시 P0 격상.

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

### `data/heartbeat_MW0601_20260909.json` — 244B · 09-09 12:27:43
```json
{
 "pid": 24768,
 "written_at": "2026-09-09T12:28:43",
 "beat_epoch": 1788924521.821331,
 "beat_age_sec": 2.2,
 "watching": true,
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

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-09 11:49:05**

| 키 | 값 | 수집 대상일(2026-09-09)과 일치 |
|---|---|---|
| `date` | 2026-09-09 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 121개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260909-점검리포트.md` | 15.0KB | 09-09 09:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_pre.md` | 53.9KB | 09-09 09:01 |
| `docs/정기점검/매일점검/MW0601-20260908-점검리포트.md` | 79.5KB | 09-08 17:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_post.md` | 88.8KB | 09-08 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_intra.md` | 76.5KB | 09-08 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_pre.md` | 43.0KB | 09-08 09:02 |
| `docs/정기점검/매일점검/MW0601-20260907-점검리포트.md` | 95.0KB | 09-07 17:42 |
| `docs/정기점검/매일점검/MW0601-20260907-BLAS즉사-딥다이브.md` | 13.2KB | 09-07 16:30 |

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

1. `logs/20260909_WARN.log`: **Traceback** 출현 3건 — 크래시/메모리 계열
2. `logs/20260909_SYSTEM.log`: 매분 루프 커버리지 210/371분 (56.6%) — 루프가 빠진 구간이 있다
3. `logs/20260909_SYSTEM.log`: 12:30~15:10 **연속 161분 매분 루프 기록 없음**
4. 메인 스레드 정지 5초 초과 **3건** (최대 7047ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
5. `logs/20260909_WARN.log`: **[Brier] 과신** 3건(표본)
6. `logs/20260909_WARN.log`: **ConstOut** 4건(표본)
7. `logs/20260909_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20260909_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260909_SIGNAL.log`: **ConstOut** 8건(표본)
10. `logs/20260909_LEARNING.log`: **축퇴** 8건(표본)
11. 미커밋 변경 552건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260909*.log` (Windows) / `grep 강제청산 logs/*20260909*.log`*