# 미륵이 증거 다이제스트 — 2026-09-11 / INTRA

- 생성 2026-09-11 12:28:00 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/wizardly-gifted-mayer/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260911` · `2026-09-11` · `260911` · `0911`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260911.log` | 125B | 09-11 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260911.log` | 139B | 09-11 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260911.json` | 243B | 09-11 12:27 |
| `launcher_{DATE}_084001_23715.log` | 1 | `logs/Mireuk_batch/launcher_20260911_084001_23715.log` | 865.7KB | 09-11 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260911.log` | 11.4KB | 09-11 09:58 |
| `retrain_intraday_{DATE}_093700.log` | 1 | `logs/retrain_intraday_20260911_093700.log` | 2.8KB | 09-11 09:37 |
| `retrain_intraday_{DATE}_114001.log` | 1 | `logs/retrain_intraday_20260911_114001.log` | 2.8KB | 09-11 11:40 |
| `retrain_intraday_{DATE}_122101.log` | 1 | `logs/retrain_intraday_20260911_122101.log` | 2.8KB | 09-11 12:21 |
| `{DATE}_DATA.log` | 1 | `logs/20260911_DATA.log` | 184.6KB | 09-11 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260911_DEBUG.log` | 126.3KB | 09-11 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260911_HEALTH.log` | 2.6KB | 09-11 12:23 |
| `{DATE}_HOGA.log` | 1 | `logs/20260911_HOGA.log` | 29.8MB | 09-11 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260911_LEARNING.log` | 191.2KB | 09-11 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260911_MICRO.log` | 560.2KB | 09-11 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260911_PROBE.log` | 57.8KB | 09-11 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260911_SIGNAL.log` | 339.7KB | 09-11 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260911_SYSTEM.log` | 434.9KB | 09-11 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260911_TRADE.log` | 167B | 09-11 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260911_WARN.log` | 14.3KB | 09-11 12:26 |

## 2. 코드·커밋 상태

- HEAD `ac042a0` · 브랜치 `v9-dev` · 미커밋 559건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 549건 (추적변경 551 · 미추적 8 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 3.4시간 · git 프로세스 0개 → **커밋 불가 상태**
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
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
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/champion_tp1_skip_trail.py
 M collection/broker/base.py
 M collection/broker/cybos_broker.py
 M collection/broker/factory.py
 M collection/cybos/api_connector.py
 M collection/cybos/investor_data.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/settings.py
 M config/strategy_params.py
 M config/strategy_registry.py
 M dashboard/main_dashboard.py
… 외 519건
```

**당일(2026-09-11) 커밋**
```
(당일 커밋 없음 — ⚠ 인덱스락 잔존으로 **커밋 불가 상태였음**. 미조치가 아니다)
```

**최근 커밋 12건**
```
ac042a0 [MW0601] 556차 후속: 장후 자동조치 기록 — 리포트 제4부 + dev_memory + 09-09·09-10 점검 산출물
5f8e40e [MW0601] 556차 후속: 장후 자동조치 — F-5(Armistice 고착 오탐)·G-4(래치 스냅샷)·G-1(상태파일 회전)
da66651 [MW0601] 555차 후속2: 출처축(P0)·차트 Y축(P1)·라벨 레지스트리(P2) + GP 마커 재지정
106f6e2 [MW0601] 555차 병합: GP 청산 패널 갱신 트리거 + 출처축 화이트리스트
c08128f [MW0601] 555차 후속: 손익 추이 「출처」축을 화이트리스트로 뒤집음 — 모르는 라벨은 auto 가 아니다
c91d591 [MW0601] 555차: GP 가상 청산이 손익 추이 패널을 갱신하지 않던 결함 — run_shadow 반환값 신설
bd33401 [MW0601] 554차: 테스트가 심은 유령 포지션 — 격리 2겹 + 복원 가드 + 대조 축 분리
f6ac416 [MW0601] 553차 후속4: GP 병행운용 Phase 4 — 수익 판넬 「GP(가상)」 구분
fec531c [MW0601] 553차 후속3: GP 병행운용 Phase 3 — 도전자 2종 배선 + 관측 개시(2026-09-10)
c384f8c [MW0601] 553차 후속2: ma_basis=cont 확정 + GP 병행운용 Phase 2(엔진 결함 5건)
a791389 [MW0601] 553차 후속: GP 병행운용 Phase 1 — MA20/MA60 배선 + 죽은 지표 교체
70ebd33 [MW0601] 553차: GP 규칙 병행운용 Phase 0 — 사전등록(비용 CYBOS·CREON 분리) + 차트 GP 마커
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

_본문 미열람(설정): `20260911_HOGA.log` 29.8MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `retrain_intraday_20260911_122101.log`, `20260911_MICRO.log`, `20260911_DATA.log`, `20260911_PROBE.log`, `launcher_20260911_084001_23715.log`, `20260911_DEBUG.log`, `mainstall_traceback_20260911.log`, `freeze_sentinel_20260911.log`_

### `logs/20260911_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-11 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-11 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-11 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260911_WARN.log` — 14.3KB · 94행 · 최종 12:26:00

- 형식 평문 · 시각 인식 94행 · ERROR=1, WARNING=93

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-11 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-11 08:41:10 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 2031ms account=333044256
2026-09-11 08:41:10 [WARNING] SYSTEM: [LiveDBG] _ts_sync_position_from_broker BlockRequest 2034ms — 메인 스레드 2034ms 점유
2026-09-11 08:41:10 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-11 12:22:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 2552ms 경고 (기준 1000ms)
2026-09-11 12:22:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2735ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2735 band=INFO since_pipe_s=0.1
2026-09-11 12:23:00 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2552ms quality=1.00 cache=0s exc10m=1) | cause=S0(2257ms)
2026-09-11 12:23:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 988ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-09-11 12:26:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.220% (임계 ±0.134%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `LiveDBG` | 1 | 09:53:19 | 09:53:19 | _tick_header 간격 19390ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=19390 band=ALERT since_pipe_s=0.2 |

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-11 09:53:19 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 19390ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=19390 band=ALERT since_pipe_s=0.2
```

</details>

**WARNING — 태그 13종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 29 | 08:41:08 | 12:22:03 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 10 | 09:00:01 | 12:22:03 | total=1810ms | S0=5ms S1=15ms S2=0ms S3=0ms S4=121ms S5=908ms S6=734ms S7=18ms S8=9ms |
| `CB⑤` | 10 | 09:00:02 | 12:22:03 | 파이프라인 1810ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 10 | 09:05:00 | 12:26:00 | 5분 누적 수익률 +0.557% (임계 ±0.398%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 9 | 09:00:01 | 12:22:03 | level=WARNING degraded=OFF | latency=1810ms | quality=0.86 | cache_age=34s | exceptions_10m=0 |
| `SHAP` | 6 | 11:45:01 | 12:23:01 | 슬로우 감지 1102ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `MainStallTrace` | 4 | 09:00:05 | 09:58:06 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260911.log |
| `HealthPolicy` | 4 | 09:01:00 | 12:23:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1810ms quality=0.86 cache=0s exc10m=0) | cause=S5(908ms) |
| `ConstOut` | 3 | 09:36:00 | 12:20:01 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| `출처축` | 2 | 08:41:10 | 08:41:10 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:10 | 08:41:10 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-10 → 2026-09-11)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Canary` | 2 | 08:55:10 | 08:55:10 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

**채널** — `SYSTEM`×85, `HEALTH`×9

**컴포넌트 상위 15** — `LiveDBG`×30, `PipePerf`×10, `CB⑤`×10, `ScalerRefresh`×10, `Health`×9, `SHAP`×6, `MainStallTrace`×4, `HealthPolicy`×4, `ConstOut`×3, `출처축`×2, `SessionStateDrop`×2, `Canary`×2, `CB③-P4`×2

### `logs/20260911_SYSTEM.log` — 434.9KB · 3221행 · 최종 12:27:52

- 형식 평문 · 시각 인식 3214행 · INFO=3214, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=6780 | 행감지=30s all_threads=True
2026-09-11 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-11 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-11 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-11 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-10) 종가 버퍼 로드: 383봉
  …
2026-09-11 12:29:01 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=12:28 O=1074.26 H=1074.86 L=1074.22 C=1074.36 V=224
2026-09-11 12:29:01 [INFO] SYSTEM: [CVD-ANCHOR] ts=12:28 vol=224 | live_buy=155 shadow_buy=105 anchor_buy=105 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-11 12:29:01 [INFO] SYSTEM: [MicroRegime] 혼합 → 횡보장 (ADX=15.4, ATR=0.880, ratio=1.06, 근거=none, z=0)
2026-09-11 12:29:01 [INFO] SYSTEM: [S6Detail] ensemble=5ms checklist_pre=19ms meta_gate=37ms gates=0ms imp=0ms shap=2ms corr=6ms dash_ui=0ms tail=18ms
2026-09-11 12:29:01 [INFO] SYSTEM: [PipePerf][DBG] total=563ms | S0=2ms S1=47ms S2=32ms S3=0ms S4=92ms S5=284ms S6=87ms S7=15ms S8=3ms
```

</details>

**채널** — `SYSTEM`×3214

**컴포넌트 상위 15** — `CybosInvestorRaw`×830, `CybosRT-TICK`×729, `CybosRT-ROLLOVER`×224, `BAR-CLOSE`×224, `CVD-ANCHOR`×224, `TickUI`×223, `S6Detail`×210, `PipePerf`×210, `System`×59, `MicroRegime`×50, `RegimeFingerprint`×38, `OptionChain`×22, `CybosSub`×21, `IntradayRegime`×20, `ConstOut`×15

### `logs/20260911_SIGNAL.log` — 339.7KB · 2978행 · 최종 12:27:01

- 형식 평문 · 시각 인식 2978행 · WARNING=1316, INFO=1662

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
  …
2026-09-11 12:29:01 [INFO] SIGNAL: [MicroRegime] 레짐 변경 → 횡보장 (ADX=15.4 ATR비=1.06 지속=1분 근거=none z=0)
2026-09-11 12:29:01 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-09-11 12:29:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=50.4% grade=X regime=NEUTRAL
2026-09-11 12:29:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=50.4% grade=X micro=횡보장
2026-09-11 12:29:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.504<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 894 | 09:00:02 | 12:26:01 | 1m 'macro_vix' scale=0.0172 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 127 | 09:00:00 | 12:26:00 | ts=08:59 horizon=1m age=1m max_z=+4.32(cancel_add_ratio) extreme=2 adj=2 |
| `Model` | 98 | 09:00:00 | 12:26:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerRefresh` | 84 | 08:45:10 | 09:45:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0234) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Checklist` | 65 | 09:06:00 | 12:25:01 | 신뢰도 미달 34.4% < 38.5% → 강제 X등급 |
| `WeightCollapse` | 44 | 09:07:00 | 12:28:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 3 | 09:36:00 | 12:20:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×2978

**컴포넌트 상위 15** — `ScalerFloor`×978, `SIGNAL`×420, `Ensemble`×213, `ZeroDiag`×209, `FQAdj`×207, `MetaGate`×146, `ScalerMonitor`×127, `Model`×122, `ScalerRefresh`×116, `Checklist`×66, `ATR-Horizon`×52, `MicroRegime`×50, `WeightCollapse`×44, `InstabilityGate`×40, `차단`×36

### `logs/20260911_LEARNING.log` — 191.2KB · 1768행 · 최종 12:27:01

- 형식 평문 · 시각 인식 1768행 · WARNING=173, INFO=1595

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 08:40:51 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00039 auc=0.462 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2377 < conf_floor=0.3300 (span=0.00047 auc=0.579 out_max=0.2377, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00166 auc=0.413 out_max=0.3257 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00004 auc=0.518 out_max=0.2174 (기준 auc<0.53 and span<0.020, 기저율=0.2174 n=115) → 보정 미적용, raw 통과
  …
2026-09-11 12:29:01 [INFO] LEARNING: ✓ 15m 예측 적중 (conf=52.7% UP)
2026-09-11 12:29:01 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=35.6% DN)
2026-09-11 12:29:01 [INFO] LEARNING: [OnlineLearner] 3m 초기 학습 완료
2026-09-11 12:29:01 [INFO] LEARNING: [OnlineLearner] 15m 초기 학습 완료
2026-09-11 12:29:01 [INFO] LEARNING: [SGD] 6건 학습 | SGD비중=30% 50분정확도=5.6%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 173 | 08:40:51 | 12:28:00 | 축퇴 감지 — span=0.00039 auc=0.462 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1768

**컴포넌트 상위 15** — `LEARNING`×663, `Calibration`×342, `SGD`×209, `sigma`×197, `Bias⚠`×149, `Bias`×65, `MetaConf`×41, `OnlineLearner`×33, `ScalerWarmup`×32, `BiasReset`×9, `SHAP`×6, `GBM-64`×6, `GBM`×6, `RF`×4, `ExtremityCorrector`×2

### `logs/20260911_HEALTH.log` — 2.6KB · 19행 · 최종 12:23:00

- 형식 평문 · 시각 인식 19행 · WARNING=9, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1810ms | quality=0.86 | cache_age=34s | exceptions_10m=0
2026-09-11 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=668ms | quality=0.86 | cache_age=92s | exceptions_10m=0
2026-09-11 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1264ms | quality=0.74 | cache_age=153s | exceptions_10m=0
2026-09-11 09:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=436ms | quality=1.00 | cache_age=28s | exceptions_10m=0
2026-09-11 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=591ms | quality=1.00 | cache_age=181s | exceptions_10m=0
  …
2026-09-11 11:42:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=379ms | quality=1.00 | cache_age=5s | exceptions_10m=0
2026-09-11 11:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=327ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-11 11:49:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=377ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-11 12:22:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2552ms | quality=1.00 | cache_age=19s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-11 12:23:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=408ms | quality=1.00 | cache_age=76s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:01 | 12:22:03 | level=WARNING degraded=OFF | latency=1810ms | quality=0.86 | cache_age=34s | exceptions_10m=0 |

**채널** — `HEALTH`×19

**컴포넌트 상위 15** — `Health`×18, `HealthTrend`×1

### `logs/retrain_intraday_20260911_093700.log` — 2.8KB · 22행 · 최종 09:37:20

- 형식 평문 · 시각 인식 22행 · INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 09:37:00,469 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-11 09:37:00,469 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-11 09:37:00,469 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-11 09:37:00,469 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-11 09:37:00,470 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_efc35d3c.json
  …
2026-09-11 09:37:20,890 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-11 09:37:20,890 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-11 09:37:20,891 [INFO] LEARNING: [Retrain] 완료 | 18.1초 | 성공=1/1 호라이즌
2026-09-11 09:37:20,891 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 20.4s 데이터=4800행
2026-09-11 09:37:20,892 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_efc35d3c.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260911_114001.log` — 2.8KB · 22행 · 최종 11:40:22

- 형식 평문 · 시각 인식 22행 · INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-11 11:40:01,385 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-11 11:40:01,385 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-11 11:40:01,385 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-11 11:40:01,385 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-11 11:40:01,386 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a2cca190.json
  …
2026-09-11 11:40:22,948 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-11 11:40:22,949 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-11 11:40:22,949 [INFO] LEARNING: [Retrain] 완료 | 18.8초 | 성공=1/1 호라이즌
2026-09-11 11:40:22,950 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.6s 데이터=4800행
2026-09-11 11:40:22,952 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a2cca190.json
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
| 차단(`[차단]`) | 36 |
| 사이저 호출(`[Sizer]`) | 0 |

### 차단 사유 36건 · 10종

| 건수 | 사유 |
|---|---|
| 25 | 등급X — 미통과 항목: 2_confidence |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.1pt > ATR×5.0=6.7pt (시가=1070.50 반등위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.80pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×25, `3_vwap`×1, `4_cvd`×1, `5_ofi`×1, `6_foreign`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 17건 · 최대 19390ms · 5초 초과 4건

상위 — 19390ms, 6187ms, 5890ms, 5109ms, 4344ms, 3937ms, 3718ms, 3547ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5109ms | 1810ms | **3299ms (65%)** |
| 09:49:51 | 6187ms | 445ms | **5742ms (93%)** |
| 09:53:19 | 19390ms | 545ms | **18845ms (97%)** |
| 09:58:06 | 5890ms | 664ms | **5226ms (89%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260911_WARN.log`
```
--- ConstOut ×3(표본)
09:36:00 2026-09-11 09:36:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:39:01 2026-09-11 11:39:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:20:01 2026-09-11 12:20:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×4(표본)
09:00:05 2026-09-11 09:00:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260911.log
09:49:51 2026-09-11 09:49:51 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260911.log
09:53:19 2026-09-11 09:53:19 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260911.log
09:58:06 2026-09-11 09:58:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260911.log
--- [SHAP] 슬로우 ×6(표본)
11:45:01 2026-09-11 11:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1102ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:53:02 2026-09-11 11:53:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 996ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:00:01 2026-09-11 12:00:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1069ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:06:01 2026-09-11 12:06:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1081ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
09:00:05 2026-09-11 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5109ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5109 band=WARN since_pipe_s=0.1
09:05:03 2026-09-11 09:05:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3937ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3937 band=INFO since_pipe_s=0.1
09:38:03 2026-09-11 09:38:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3718ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3718 band=INFO since_pipe_s=0.1
09:43:03 2026-09-11 09:43:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3359ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3359 band=INFO since_pipe_s=0.1
```

### `logs/20260911_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:00 2026-09-11 09:36:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:38:00 (const_output)
09:36:00 2026-09-11 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:01 2026-09-11 09:36:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=104ms fit=57ms total=164ms
09:37:00 2026-09-11 09:37:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-09-11 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:05:00 2026-09-11 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:11:00 2026-09-11 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:16:00 2026-09-11 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
```

### `logs/20260911_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-09-11 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:36:00 2026-09-11 09:36:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:36:00 2026-09-11 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:00 2026-09-11 09:37:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
11:39:01 2026-09-11 11:39:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:00 2026-09-11 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-11 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-11 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-11 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:30 2026-09-11 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
--- 안전망 ×8(표본)
09:07:00 2026-09-11 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-11 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-11 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-11 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260911_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00039 auc=0.462 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2377 < conf_floor=0.3300 (span=0.00047 auc=0.579 out_max=0.2377, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00166 auc=0.413 out_max=0.3257 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-11 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00004 auc=0.518 out_max=0.2174 (기준 auc<0.53 and span<0.020, 기저율=0.2174 n=115) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260911_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260911_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 13 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 17 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 8 | 09:56:02 [WARNING] _tick_header 간격 2312ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2312 band=… |
| 12:00 | 장중 중간점 | 3 | 12:00:01 [WARNING] 슬로우 감지 1069ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |

- 이 로그 생존구간: 08:41 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260911_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 90 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=6780 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 126 | 08:49:02 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 180 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 191 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 161 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:29

**매분 루프 커버리지 09:00~15:10: 210/371분 (56.6%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:30 | 15:10 | 161 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260911_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 68 | 08:45:10 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0234) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 136 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0275) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 263 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 108 | 09:56:00 [WARNING] 신뢰도 미달 34.4% < 38.5% → 강제 X등급 |
| 12:00 | 장중 중간점 | 108 | 11:58:05 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:29

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260910 | 15:40 | 로그 본문 |
| 20260909 | 15:40 | 로그 본문 |
| 20260908 | 15:40 | 로그 본문 |
| 20260907 | 21:59 | 로그 본문 |
| 20260906 | 20:39 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260911** | **12:29** | 로그 본문 |

- 델타 **-191분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.9MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### F-5. Armistice 「고착」 ERROR 는 장중 재기동의 정상 워밍업을 오탐하고 있었다
### G-4. ProfitGuard L2 래치가 「무엇 때문에 잠갔는지」를 남기지 않았다
### G-1. `position_state.json` 이 덮어써지기 전 세대를 남기지 않았다
### 🔴 장후 리포트 제3부 결론 정정 2건
### 🔴 부수 발견 — `state_persist_enabled=False` 는 모든 차단 래치를 재기동으로 초기화한다
### 자동조치가 하지 않은 것
### 테스트
## 2026-09-11 (MW0601 557차 — 장전 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
라 여전히 사용자 승인 대기 — 오늘
   재상정하지 않음. **Why**: 09-10 장후 리포트가 `O-t1`로 이 재발 여부를 다음 장전
   관측 예정으로 등록했고, 오늘 재현이 그 관측을 확정함. **검증**: 다음 거래일
   장전(`O-p1`)에서 재발 여부 계속 관측.

2. **`[ConfFloorGuard]` 자동진입 하한 도달 불가 — 오실레이션 패턴 지속**.
   09:00:01 보정기 출력상한(0.3479) < 필요 min_conf(0.4290), AUC=0.550/span=0.0063로
   거의 무정보(워밍업 표본 n=80 수준의 정상 초기 현상). 09-09·09-10에도 동일 패턴,
   09-10 장후가 "간헐 오실레이션"으로 재확인해 `O-t3`로 계승한 항목. **결정**: 신규
   판정 없음, 관측만 지속(`O-p2`). 오늘 진입 시도 0건이라 실제 차단 영향은 미확인 —
   장중 점검에서 `[차단]` 로그로 추가 확인 필요.

3. **미커밋 557건 — 수집기 `git diff` 실질변경 계측 실패, 전량 EOL 파생 직접 검증**.
   `evidence_MW0601-20260911_pre.md` §2 "실질 변경 미측정(git diff 실패)". 직접
   `git --no-optional-locks diff --shortstat` 재현: `551 files changed, 326794
   insertions(+), 326794 deletions(-)` — 삽입=삭제로 정확히 일치, 실제 코드 변경
   0건 확인(`config/settings.py` 단독도 `7430/7430` 동일 패턴). **결정**: 기존
   NEXT_TODO 544-6/G-1(재시도 로직 + 실패 사유 구체화) 그대로 유지, 신규 등록 안 함
   (함정 ① — 이미 등록된 것을 재상정하지 않는다).

**그 외 확인(이상 없음)**:
- 브랜치 `v9-dev` 확인, origin 대비 0/0(완전 동기화). HEAD `ac042a0`.
- 런타임 `Python 3.7.13 32bit | scipy=1.5.4 | sklearn=1.0.2 | joblib=1.1.0 | numpy=1.21.6`
  (joblib 1.1.0 vs CLAUDE.md 1.1.1 — 491차 기지 사안, 재상정 안 함).
- 모델 로드 `[RF] 로드 완료: 6호라이즌 ready=True`(08:40:51). Cybos 접속·잔고조회 정상
  (2031ms). 실시간 구독 사전시작 08:45:10(개장보다 +10.7s 이르게 시작 완료 — 정상).
  옵션체인 초기화 5242종목(08:41:10) → PCR Worker 09:01:28 `PCR=0.581 ATM_PCR=2.588
  GEX=99.93B`. 매크로 레짐 확정 08:58:14 `NEUTRAL(점수=-1)`.
- 오늘 브로커=Cybos라 OPT50029/OPT10080 TR 판정 해당 없음 — 실시간 틱+`[BAR-CLOSE]`
  자체 집계로 대체 확인(정상).
- `[HealthPolicy] Degraded 선제차단`(09:01:00, latency=1810ms)·`[MainStallTrace]`
  5109ms 스택 스냅샷(09:00:05, `_tick_header`→`_pump_messages`) — 둘 다 09-01·09-07·
  09-09·09-10에도 매일 개장 직후 관측되는 정상적 개장 버스트 패턴. 후자는 482차 F-3
  섀도 계측이 설계대로 캡처한 것(장애 아님).
- 설정 불변식 25개 항목 전부 일치. 차단 게이트 34개 중 9개 비활성 — 전부 문서화된
  한시예외·기능토글과 일치, 미기록 신규 없음.
- 인덱스락 없음. 병행 세션 없음(오늘 커밋 0건, 같은 날 산출물 없음).

**Fix/고도화**: 신규 없음. 기존 F-1·F-3·544-6/G-1 승인 대기 그대로 유지.

4. **`.git/index.lock` 09:02 생성 — 판정보류, 신규(오늘 첫 발생)**. 증거 수집 시작
   시점(09:01:16) 락 자가점검은 "이 실행이 만들지 않았다"였으나 그 직후 09:02에
   0바이트 락이 생성됨. 09:09 확인 시점 `git_lock_guard.py --check` → `HOLD 판정보류
   — 나이 433초 <= 임계 600초`. **판정보류라 이 세션은 삭제하지 않았다**(SKILL §0
   경고 — 실행 중인 git일 수 있어 지우면 인덱스가 깨질 위험). 09-10의 1-3·1-7과
   같은 유형(모든 git 호출에 `--no-optional-locks`를 붙였음에도 발생). 리포트 §7·
   사용자 조치에 재확인 지시 등록. 오늘 점검 산출물은 이 락 때문에 커밋 대기 상태.

산출물: `docs/정기점검/매일점검/MW0601-20260911-점검리포트.md`(신규, 제1부),
`docs/정기점검/매일점검/evidence_MW0601-20260911_pre.md`(신규). 커밋 없음(장전 규약 +
`.git/index.lock` 판정보류로 물리적으로도 불가).

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-09 (MW0601 550차 — 장중 점검)
## 2026-09-09 (MW0601 551차 — 장후 점검, 종합 완성본)
## 2026-09-10 (MW0601 554차 — 장전 점검)
## 2026-09-10 (MW0601 — 장중 점검)
## 2026-09-10 (MW0601 556차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖)
### 다음 세션 관측
## 2026-09-11 (MW0601 557차 — 장전 점검)
```

미완료 체크박스 **2590건** (끝에서 30건)
```
- [ ] **554-3 (확인 필요, 장후)** 554-1 이월 포지션의 실제 출처 규명 — 장중 라이브 DB
- [ ] **554-4 (P2, 고도화 제안 / G-1)** `position_state.json` 덮어쓰기 전 회전 백업
- [ ] **554-5 (P2, 고도화 제안 / G-2)** `[ExternalEntry]`류 외부 진입 감지를 "엔진
- [ ] **O-p2 (장후 판정)** ProfitGuard Tier4 당일 영구 중단이 15:10까지 유지되는가
- [ ] **O-p3 (다음 세션 장전 판정)** `[SessionStateDrop]` 재발 지속 여부 + F-1(538-4)
- [ ] **O-p4 (오늘 중 재확인)** `.git/index.lock`(09:01 생성) 스테일 확정·회수 여부 —
- [ ] **O-p5 (장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부(09:00:00 재현
- [ ] **F-3 (P0, 신규)** 장중 브로커 잔고 주기적 재대사(5~10분 간격) 신설 — 기동 시
- [ ] **F-4 (P1, 신규)** `[UnreconciledExit]`(554차 신설) 발동 조건 재검토 — 오늘
- [ ] **G-3 (고도화)** 재기동 시 엔진-브로커 상태 불일치 발견 이벤트를 별도 카운터로
- [ ] **O-i1 (장후 판정)** 12:17 재기동의 실제 원인(사용자 수동 재시작 여부) 확인.
- [ ] **O-i2 (장후 판정)** `trades.db`의 08:45 허구 2레그(+6,921,594원) + 12:17~12:18
- [ ] **O-i3 (장후 판정)** ProfitGuard Tier4 당일 영구 중단 15:10까지 유지 확정(O-p2 계승).
- [ ] **O-i4 (장후 판정)** `[UnreconciledExit]`이 12:17~12:18 청산에서 실제로 평가됐는지
- [ ] **O-i5 (장후 재확인)** 매분 루프 커버리지 12:30~15:10 공백은 이번 점검이 15:10
- [ ] 🔴 **556-4 (신규 · C등급)** `data/ui_prefs.json:state_persist_enabled = False`
- [ ] **556-5 (기록 결손)** `DECISION_LOG.md` 에 **555차·556차 본문 항목이 없다.**
- [ ] **556-6 (G-3 이월 · A등급)** 재기동 시 엔진↔브로커 상태 불일치 발견 이벤트를
- [ ] **556-7 (테스트 인프라)** `pytest tests/` 전체 실행이 **수집 단계에서**
- [ ] **556-8 (기존 실패 8건 대장)** 아래는 HEAD 에서도 동일하게 실패하는 **기존**
- [ ] **F-1 (승인 대기, 리포트 제3부 §2)** ProfitGuard Tier4 래치를 「정정 가능한
- [ ] **F-3 (P0, 승인 대기)** 장중 브로커 잔고 주기 재대사 — 09-10 이월 그대로.
- [ ] **G-2 (주간회의)** 외부 진입 감지를 「엔진 기동 전 포지션」까지 확장 — 536-2와 통합.
- [ ] **O-t2′** 내일 장중 재기동이 있으면 `[Armistice] … 고착[sync]` / `[time]` 중
- [ ] **O-t6** ProfitGuard 래치가 실제로 걸리는 날 `[ProfitGuard][LatchSnapshot]` 이
- [ ] **O-t7** 포지션이 열리고 닫히는 날 `data/position_state.json.gen_*` 이 최대
- [ ] **O-p1 (다음 거래일 장전 판정, 구 O-t1 계승)** `[SessionStateDrop]` 완료 마커
- [ ] **O-p2 (오늘 장중·장후 판정, 구 O-t3 계승)** `[ConfFloorGuard]` 자동진입 하한
- [ ] 신규 Fix/고도화 없음 — F-1·F-3·544-6(git diff 실패 재시도, G-1)은 기존 승인
- [ ] **O-p3 (오늘 중 재확인)** `.git/index.lock`(09:02 생성) 스테일 확정·회수 여부 —
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
ytest tests/` 전체 실행이 **수집 단계에서**
      `ValueError: I/O operation on closed file` 로 죽는다(`test_497_*`~`test_529_*`
      구간). 이번 변경 이전부터 존재. 원인 모듈 특정 필요 — 그전까지는 배치 실행.
      ⚠ `conda run` 에 `-s` 를 주면 conda 자체가 크래시 리포트로 멈춘다.
- [ ] **556-8 (기존 실패 8건 대장)** 아래는 HEAD 에서도 동일하게 실패하는 **기존**
      실패다. 이번 변경과 무관하나 누적 방치 중 — 별건 처리 필요.
      `test_456_wave1_stats_and_shs::test_trend_sql_counts_positions_not_legs` ·
      `test_477_f1_f5_saturation_psi::test_step9_batch_placeholders_match_params` ·
      `test_483_git_lock_guard::test_sibling_copy_matches_canonical[fuoption]` ·
      `test_493_commission_rate_and_net_recon::test_cost_formulas_do_not_use_live_rate` ·
      `test_553_gp_chart_markers::test_loader_is_safe_before_phase3` ·
      `test_553_gp_pnl_panel::test_gp_uses_mini_futures_multiplier` ·
      `test_553_gp_pnl_panel::test_gp_defaults_off_when_unset` ·
      `test_554_position_state_isolation::test_missing_reference_skips_check_but_is_not_silent`
      (단독 실행은 통과 — 테스트 순서 간섭)
- [ ] **F-1 (승인 대기, 리포트 제3부 §2)** ProfitGuard Tier4 래치를 「정정 가능한
      재평가」로 바꿀지 — **여전히 필요하다.** 09-10 에 래치가 풀린 것은 재기동이
      우연히 입력을 다시 만들어 준 결과이지 설계가 정정을 반영한 것이 아니다
      (`_TierGate.check()` 첫 줄 `if self._halted: return True` 는 그대로).
      ⚠ 안전장치를 **여는** 방향이라 섀도 선행 + 사용자 승인 필수.
- [ ] **F-3 (P0, 승인 대기)** 장중 브로커 잔고 주기 재대사 — 09-10 이월 그대로.
- [ ] **G-2 (주간회의)** 외부 진입 감지를 「엔진 기동 전 포지션」까지 확장 — 536-2와 통합.

### 다음 세션 관측

- [ ] **O-t2′** 내일 장중 재기동이 있으면 `[Armistice] … 고착[sync]` / `[time]` 중
      어느 쪽도 **뜨지 않는지** 확인(F-5 라이브 검증). 워밍업 90초 구간에 ERROR 가
      뜨면 이번 수정이 안 먹은 것이다.
- [ ] **O-t6** ProfitGuard 래치가 실제로 걸리는 날 `[ProfitGuard][LatchSnapshot]` 이
      **1줄** 남고 구성 레그가 실리는지(G-4 라이브 검증).
- [ ] **O-t7** 포지션이 열리고 닫히는 날 `data/position_state.json.gen_*` 이 최대
      3개까지만 쌓이는지, 손절 조정으로 링이 소모되지 않는지(G-1 라이브 검증).

## 2026-09-11 (MW0601 557차 — 장전 점검)

- [ ] **O-p1 (다음 거래일 장전 판정, 구 O-t1 계승)** `[SessionStateDrop]` 완료 마커
      소실이 09-12 장전에도 재현되는지 확인. 09-09·09-10·09-11 3거래일 연속 재현 —
      F-1(538-4) 승인 필요성이 계속 누적되는 중이니 재현 지속 시 승인 우선순위를
      다시 사용자에게 물을 것.
- [ ] **O-p2 (오늘 장중·장후 판정, 구 O-t3 계승)** `[ConfFloorGuard]` 자동진입 하한
      도달 불가 오실레이션 패턴이 오늘도 나타났다(09:00:01). 장중 점검에서 이 구간
      `[차단]` 로그로 실제 진입 차단 건수가 있었는지 확인할 것.
- [ ] 신규 Fix/고도화 없음 — F-1·F-3·544-6(git diff 실패 재시도, G-1)은 기존 승인
      대기 상태 그대로 유지(재상정 안 함, 함정 ① 준수).
- [ ] **O-p3 (오늘 중 재확인)** `.git/index.lock`(09:02 생성) 스테일 확정·회수 여부 —
      `python scripts/git_lock_guard.py --check` 나이 600초 초과 후 재판정. 판정보류면
      절대 지우지 말 것. 이 락이 남아있는 동안 오늘 점검 산출물 커밋 불가.

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

### `data/heartbeat_MW0601_20260911.json` — 243B · 09-11 12:27:47
```json
{
 "pid": 6780,
 "written_at": "2026-09-11T12:28:47",
 "beat_epoch": 1789097325.1145697,
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

- 파일 최종 기록: **09-11 12:22:02**

| 키 | 값 | 수집 대상일(2026-09-11)과 일치 |
|---|---|---|
| `date` | 2026-09-11 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 129개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260911-점검리포트.md` | 18.5KB | 09-11 09:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_pre.md` | 53.7KB | 09-11 09:02 |
| `docs/정기점검/매일점검/MW0601-20260910-점검리포트.md` | 103.5KB | 09-10 18:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_post.md` | 84.6KB | 09-10 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_intra.md` | 69.2KB | 09-10 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_pre.md` | 56.9KB | 09-10 09:01 |
| `docs/정기점검/매일점검/MW0601-20260909-점검리포트.md` | 62.1KB | 09-09 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_post.md` | 78.6KB | 09-09 16:18 |

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

1. `.git/index.lock` **스테일 잔존** (0바이트 · 3.4시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. `logs/20260911_WARN.log`: ERROR 이상 1건
3. `logs/20260911_WARN.log`: **Traceback** 출현 4건 — 크래시/메모리 계열
4. `logs/20260911_SYSTEM.log`: 매분 루프 커버리지 210/371분 (56.6%) — 루프가 빠진 구간이 있다
5. `logs/20260911_SYSTEM.log`: 12:30~15:10 **연속 161분 매분 루프 기록 없음**
6. 메인 스레드 정지 5초 초과 **4건** (최대 19390ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260911_WARN.log`: **ConstOut** 3건(표본)
8. `logs/20260911_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20260911_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260911_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260911_LEARNING.log`: **축퇴** 8건(표본)
12. 미커밋 변경 559건 (실질 2건 · 코드 0건 · EOL 파생 549건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260911*.log` (Windows) / `grep 강제청산 logs/*20260911*.log`*