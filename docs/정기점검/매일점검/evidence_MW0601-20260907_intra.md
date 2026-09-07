# 미륵이 증거 다이제스트 — 2026-09-07 / INTRA

- 생성 2026-09-07 12:27:02 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/vibrant-sharp-davinci/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260907` · `2026-09-07` · `260907` · `0907`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260907.log` | 125B | 09-07 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260907.log` | 139B | 09-07 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260907.json` | 244B | 09-07 12:26 |
| `launcher_{DATE}_084001_9239.log` | 1 | `logs/Mireuk_batch/launcher_20260907_084001_9239.log` | 8.1MB | 09-07 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260907.log` | 2.9KB | 09-07 09:00 |
| `retrain_intraday_{DATE}_095500.log` | 1 | `logs/retrain_intraday_20260907_095500.log` | 2.7KB | 09-07 09:55 |
| `retrain_intraday_{DATE}_111200.log` | 1 | `logs/retrain_intraday_20260907_111200.log` | 2.7KB | 09-07 11:12 |
| `retrain_intraday_{DATE}_115100.log` | 1 | `logs/retrain_intraday_20260907_115100.log` | 2.7KB | 09-07 11:51 |
| `{DATE}_DATA.log` | 1 | `logs/20260907_DATA.log` | 183.8KB | 09-07 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260907_DEBUG.log` | 133.2KB | 09-07 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260907_HEALTH.log` | 11.4KB | 09-07 11:58 |
| `{DATE}_HOGA.log` | 1 | `logs/20260907_HOGA.log` | 24.0MB | 09-07 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260907_LEARNING.log` | 183.4KB | 09-07 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260907_MICRO.log` | 498.0KB | 09-07 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260907_PROBE.log` | 57.5KB | 09-07 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260907_SIGNAL.log` | 278.1KB | 09-07 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260907_SYSTEM.log` | 7.6MB | 09-07 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260907_TRADE.log` | 26.5KB | 09-07 12:24 |
| `{DATE}_WARN.log` | 1 | `logs/20260907_WARN.log` | 124.3KB | 09-07 12:24 |

## 2. 코드·커밋 상태

- HEAD `4bb2dd3` · 브랜치 `v9-dev` · 미커밋 522건 · 실질 변경 8건 · 코드(.py) 6건 · EOL 파생 511건 (추적변경 519 · 미추적 3 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 3.4시간 · git 프로세스 0개 → **커밋 불가 상태**
  - 실질 변경 파일: `dashboard/main_dashboard.py`, `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `features/levels/levels_store.py`, `features/levels/premarket_levels.py`, `main.py`, `tests/test_534_premarket_levels.py`, `utils/db_utils.py`
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
… 외 482건
```

**당일(2026-09-07) 커밋**
```
(당일 커밋 없음 — ⚠ 인덱스락 잔존으로 **커밋 불가 상태였음**. 미조치가 아니다)
```

**최근 커밋 12건**
```
4bb2dd3 [MW0601] 534차: 당일 맥점 예측 — 거리 모델·구조 모델 구현 + UI 관측 패널
af14682 [MW0601] 533차: 풀타임 수집 Phase 0·1 — session_bars 적재 + 헤더 28 체결유형코드 + 프로브 · MW0602 적용가이드
2b7e479 [MW0601] 532차 후속: 리포트 제8부 커밋해시 기재분 채움 (3a11cd9)
3a11cd9 [MW0601] 532차 후속: 리포트 제8부에 커밋 해시 기재 + 자가유발 결함 1건 기록
3c2f17c @ [MW0601] 532차 후속: 장후 자동조치 — G-1·G-2·G-3 계측 3종 + F-1 원인 특정
9738080 [MW0601] 527~529차: 탈진 레짐은 라벨 0건이었다 — 레그 위치를 새 축으로 계측(스윙 피처 + 채널 3종)
c9f76f8 [MW0601] 524~526차: 급변장 라벨의 82%가 z경고였다 — 라벨·게이트 분리(동작 불변) · P5-13 채널 · z경고 잡음 보정(모니터 전용)
c26c513 [MW0601] 523차 후속: 리포트 제4부에 커밋 해시 기재
e1f063a [MW0601] 523차 후속: 장후 자동조치 — G-1(기동마커 게재) · G-2(ConfFloorGuard auc) · G-3(ExitStageRecon 인용)
8997136 [MW0601] 519차 기록: DECISION_LOG · NEXT_TODO · 리포트 제5부
d03b629 [MW0601] 519차: CB② 복원 · 메인스레드 정지 경보 · F-1 마감 잔여 자동청산 (사용자 지시)
7338611 [MW0601] 518차 후속: 장후 자동조치 — F-3(진입출처 라벨) · G-1(재기동 잔량 경보 문구) · G-4(이월손익 가시화)
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

_본문 미열람(설정): `20260907_HOGA.log` 24.0MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `retrain_intraday_20260907_095500.log`, `20260907_MICRO.log`, `20260907_DATA.log`, `20260907_PROBE.log`, `launcher_20260907_084001_9239.log`, `20260907_DEBUG.log`, `mainstall_traceback_20260907.log`, `freeze_sentinel_20260907.log`_

### `logs/20260907_TRADE.log` — 26.5KB · 202행 · 최종 12:24:25

- 형식 평문 · 시각 인식 202행 · WARNING=14, INFO=188

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-07 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-07 09:23:20 [INFO] TRADE: [Chejan] 상태=접수 주문번호=720 code=A0569 방향=SHORT 체결=3 미체결=0
2026-09-07 09:23:21 [INFO] TRADE: [Chejan] 상태=체결 주문번호=720 code=A0569 방향=SHORT 체결=1 미체결=0
2026-09-07 09:23:21 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1089.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
  …
2026-09-07 12:27:42 [INFO] TRADE: [주문요청] 하드스톱(틱) 청산 LONG 1계약 @ 1091.74 체결대기
2026-09-07 12:27:42 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2930 code=A0569 방향=SHORT 체결=1 미체결=0
2026-09-07 12:27:42 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2930 code=A0569 방향=SHORT 체결=1 미체결=0
2026-09-07 12:27:42 [INFO] TRADE: [Position] 체결청산 LONG @ 1091.7 | PnL=-1.10pt (-65,721원) | 하드스톱(틱)
2026-09-07 12:27:42 [INFO] TRADE: [청산 완료] PnL=-1.10pt (-65,721원) | 포지션 합계 -65,721원 (레그 1)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 14 | 09:23:21 | 12:24:25 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1089.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×202

**컴포넌트 상위 15** — `Chejan`×62, `Position`×45, `주문요청`×16, `PositionFallback`×14, `체결동기화`×14, `청산 완료`×11, `TickStop-S0C`×10, `Sizer`×9, `체결청산-부분`×5, `TickTP1`×5, `진입체크`×4, `체결진입`×4, `ProfitGuard`×1, `TP1 부분청산`×1, `TP2 부분청산`×1

### `logs/20260907_WARN.log` — 124.3KB · 593행 · 최종 12:24:26

- 형식 평문 · 시각 인식 593행 · CRITICAL=10, ERROR=15, WARNING=568

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-07 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-07 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 156ms account=333044256
2026-09-07 08:41:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3547 band=INFO since_pipe_s=NA
2026-09-07 08:41:10 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
2026-09-07 12:27:43 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-09-07 12:27:43 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-09-07 12:27:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_in_flight", False): |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-07 12:27:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-09-07 12:27:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `ExternalEntry` | 14 | 09:23:21 | 12:24:25 | 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.72 (보유 1계약, 평균 1089.72). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다 |
| CRITICAL | `Health` | 10 | 09:31:00 | 09:58:00 | level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1 |
| ERROR | `LiveDBG` | 1 | 09:00:28 | 09:00:28 | _tick_header 간격 28797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=28797 band=ALERT since_pipe_s=0.3 |

<details><summary>ERROR/ExternalEntry 원문 2건</summary>

```
2026-09-07 09:23:21 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.72 (보유 1계약, 평균 1089.72). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
2026-09-07 09:23:21 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.76 (보유 2계약, 평균 1089.74). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
```

</details>

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-07 09:31:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
2026-09-07 09:32:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=329ms | quality=1.00 | cache_age=126s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-07 09:00:28 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 28797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=28797 band=ALERT since_pipe_s=0.3
```

</details>

**WARNING — 태그 32종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 179 | 08:41:06 | 12:27:44 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 62 | 09:23:20 | 12:27:42 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1089.62 | fill_qty=3 | gubun='0' | order_no='720' | pending='NONE' | position='FLAT' | position_qty=0 | sell_balance=0 | side='SHORT' |… |
| `ChejanMatch` | 62 | 09:23:20 | 12:27:42 | order_no='720' | pending='NONE' | pending_matched=False |
| `Health` | 40 | 09:00:05 | 11:57:00 | level=WARNING degraded=OFF | latency=4962ms | quality=0.86 | cache_age=49s | exceptions_10m=0 |
| `OrderSync` | 32 | 09:23:21 | 12:24:25 | 미추적 체결 감지 (pending_miss) order_no=720 side=SHORT qty=1 price=1089.72 before=FLAT |
| `PendingOrder` | 32 | 09:26:27 | 12:27:43 | set {'kind': 'EXIT_FULL', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1091.98, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no':… |
| `ExitCooldown` | 22 | 09:26:28 | 12:27:42 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:29:28) |
| `ExitFillFlow` | 14 | 09:26:28 | 12:27:43 | after='SHORT 2계약 @ 1089.75' | before='SHORT 3계약 @ 1089.75' | fill_price=1091.92 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:SHORT qty=3 filled=1 order_no=772 reason=하드스톱(틱) req_at=09:26:27.887' | reason='하드스톱(틱)' |
| `PipePerf` | 10 | 09:00:05 | 11:52:03 | total=4962ms | S0=10ms S1=85ms S2=0ms S3=0ms S4=1313ms S5=1216ms S6=1996ms S7=308ms S8=34ms |
| `CB⑤` | 10 | 09:00:05 | 11:52:03 | 파이프라인 4962ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `HealthPolicy` | 10 | 09:01:00 | 11:53:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=4962ms quality=0.86 cache=0s exc10m=0) | cause=S6(1996ms) |
| `TickStop` | 10 | 09:26:27 | 12:27:42 | 스톱 히트 감지 (틱) SHORT tick=1091.98 stop=1091.98 → 즉시 처리 예약 |

**채널** — `SYSTEM`×543, `HEALTH`×50

**컴포넌트 상위 15** — `LiveDBG`×180, `ChejanFlow`×62, `ChejanMatch`×62, `Health`×50, `OrderSync`×32, `PendingOrder`×32, `ExitCooldown`×22, `ExternalEntry`×14, `ExitFillFlow`×14, `PipePerf`×10, `CB⑤`×10, `HealthPolicy`×10, `TickStop`×10, `ExitSendOrderResult`×10, `ScalerRefresh`×8

### `logs/20260907_SYSTEM.log` — 7.6MB · 57453행 · 최종 12:27:01

- 형식 평문 · 시각 인식 57446행 · INFO=57446, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=11116 | 행감지=30s all_threads=True
2026-09-07 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-07 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-07 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-07 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-04) 종가 버퍼 로드: 384봉
  …
2026-09-07 12:27:46 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122746 price=1091.92 cum_vol=58949 auction_code=40 recv_type=50
2026-09-07 12:27:50 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122750 price=1091.88 cum_vol=58950 auction_code=40 recv_type=50
2026-09-07 12:27:51 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122750 price=1091.82 cum_vol=58951 auction_code=40 recv_type=50
2026-09-07 12:27:51 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122750 price=1091.82 cum_vol=58952 auction_code=40 recv_type=49
2026-09-07 12:27:51 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122751 price=1091.84 cum_vol=58953 auction_code=40 recv_type=50
```

</details>

**채널** — `SYSTEM`×57446

**컴포넌트 상위 15** — `CybosRT-AUCTION`×53863, `CybosInvestorRaw`×826, `CybosRT-TICK`×543, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `BalanceUI`×137, `CybosEvent`×124, `CybosDailyPnl`×110, `BalanceRefresh`×92, `MicroRegime`×83, `System`×59

### `logs/20260907_SIGNAL.log` — 278.1KB · 2479행 · 최종 12:27:00

- 형식 평문 · 시각 인식 2479행 · WARNING=830, INFO=1649

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.418
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-09-07 12:27:00 [INFO] SIGNAL: [Ensemble] dir=+1 conf=39.5% grade=X regime=RISK_ON
2026-09-07 12:27:00 [INFO] SIGNAL: [TrendGate] UP 추세 지속 13분 — min_conf 0.62→0.44
2026-09-07 12:27:00 [INFO] SIGNAL: 앙상블: dir=+1 conf=39.5% grade=X micro=추세장
2026-09-07 12:27:00 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=3m tf=3.95 → TP1×0.5
2026-09-07 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.395<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 588 | 09:00:06 | 12:16:01 | 1m 'macro_vix' scale=0.0036 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 86 | 09:01:00 | 12:17:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 68 | 09:01:00 | 12:17:00 | ts=09:00 horizon=1m age=1m max_z=+5.71(volume_acceleration) extreme=2 adj=1 |
| `WeightCollapse` | 45 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 27 | 09:06:00 | 12:24:00 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `ScalerRefresh` | 12 | 08:45:07 | 08:45:07 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 3 | 09:54:00 | 11:50:00 | 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:02 | 09:00:02 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×2479

**컴포넌트 상위 15** — `ScalerFloor`×636, `SIGNAL`×416, `Ensemble`×210, `FQAdj`×205, `ZeroDiag`×192, `MetaGate`×151, `InstabilityGate`×113, `Model`×110, `MicroRegime`×83, `ScalerMonitor`×68, `ATR-Horizon`×47, `WeightCollapse`×45, `Checklist`×41, `ScalerRefresh`×38, `차단`×21

### `logs/20260907_LEARNING.log` — 183.4KB · 1687행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1687행 · WARNING=163, INFO=1524

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.500 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.395 out_max=0.1252 (기준 auc<0.53 and span<0.020, 기저율=0.1250 n=80) → 보정 미적용, raw 통과
2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.513 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
2026-09-07 08:40:50 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00048 auc=0.543 out_max=0.1288 (n=140) → 보정 재적용
  …
2026-09-07 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0461% buf_n=20 nonzero=20 prev_p=1092.12 cur_p=1092.30
2026-09-07 12:27:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=33.3% 예측=UP 실제=FL)
2026-09-07 12:27:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=33.3% 예측=UP 실제=FL)
2026-09-07 12:27:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=43.6% UP)
2026-09-07 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=19.4%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 163 | 08:40:50 | 12:13:00 | 축퇴 감지 — span=0.00021 auc=0.500 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1687

**컴포넌트 상위 15** — `LEARNING`×663, `Calibration`×317, `SGD`×208, `sigma`×195, `Bias⚠`×97, `Bias`×67, `MetaConf`×41, `OnlineLearner`×35, `ScalerWarmup`×26, `BiasReset`×10, `SHAP`×7, `GBM-64`×6, `GBM`×6, `RF`×4, `ExtremityCorrector`×2

### `logs/20260907_HEALTH.log` — 11.4KB · 62행 · 최종 11:58:00

- 형식 평문 · 시각 인식 62행 · CRITICAL=10, WARNING=40, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 09:00:05 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=4962ms | quality=0.86 | cache_age=49s | exceptions_10m=0
2026-09-07 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=620ms | quality=0.86 | cache_age=104s | exceptions_10m=0
2026-09-07 09:24:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=319ms | quality=1.00 | cache_age=13s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
2026-09-07 09:25:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=399ms | quality=1.00 | cache_age=74s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
2026-09-07 09:26:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=330ms | quality=1.00 | cache_age=133s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
  …
2026-09-07 11:14:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=388ms | quality=1.00 | cache_age=177s | exceptions_10m=0
2026-09-07 11:52:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2373ms | quality=1.00 | cache_age=69s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-07 11:53:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=344ms | quality=1.00 | cache_age=127s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-07 11:57:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=374ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-07 11:58:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=349ms | quality=1.00 | cache_age=59s | exceptions_10m=2 | exc_tags=[SHAP]×2
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 10 | 09:31:00 | 09:58:00 | level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-07 09:31:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
2026-09-07 09:32:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=329ms | quality=1.00 | cache_age=126s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 40 | 09:00:05 | 11:57:00 | level=WARNING degraded=OFF | latency=4962ms | quality=0.86 | cache_age=49s | exceptions_10m=0 |

**채널** — `HEALTH`×62

**컴포넌트 상위 15** — `Health`×61, `HealthTrend`×1

### `logs/retrain_intraday_20260907_111200.log` — 2.7KB · 21행 · 최종 11:12:22

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 11:12:00,857 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-07 11:12:00,857 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-07 11:12:00,857 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-07 11:12:00,857 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ea467ff8.json
2026-09-07 11:12:03,796 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-07 11:12:22,781 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-07 11:12:22,782 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-07 11:12:22,782 [INFO] LEARNING: [Retrain] 완료 | 19.0초 | 성공=1/1 호라이즌
2026-09-07 11:12:22,783 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.9s 데이터=4800행
2026-09-07 11:12:22,784 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ea467ff8.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260907_115100.log` — 2.7KB · 21행 · 최종 11:51:21

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 11:51:00,647 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-07 11:51:00,647 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-07 11:51:00,647 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-07 11:51:00,647 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_25f4d10f.json
2026-09-07 11:51:03,181 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-07 11:51:21,734 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-07 11:51:21,735 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-07 11:51:21,735 [INFO] LEARNING: [Retrain] 완료 | 18.6초 | 성공=1/1 호라이즌
2026-09-07 11:51:21,736 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.1s 데이터=4800행
2026-09-07 11:51:21,738 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_25f4d10f.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 4 |
| 진입 등록(`[Position] 진입`) — **엔진** | 4 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 18 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 14 |
| 청산(`체결청산`) | 11 |
| 차단(`[차단]`) | 21 |
| 사이저 호출(`[Sizer]`) | 9 |

### 포지션 11건 · 승 4 (36%) · 합계 -11.60pt (-771,280원)  ※ 레그 18행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:23:21 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -6.47 | -355,072 | 하드스톱(틱) |
| 09:30:17 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +5.95 | +265,877 | 하드스톱(틱) |
| 09:41:56 (추정귀속) | 외부 | LONG | 1 | — | 1 | -1.84 | -102,691 | 하드스톱(틱) |
| 09:48:24 (추정귀속) | 외부 | SHORT | 2 | — | 2 | +0.54 | +5,668 | 미추적체결(pending_miss) |
| 10:02:42 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -6.70 | -366,959 | 하드스톱(틱) |
| 10:18:01 | 엔진 | SHORT | 1 | 3m | 1 | +0.32 | +5,325 | 하드스톱(틱) |
| 10:39:01 | 엔진 | SHORT | 1 | 1m | 1 | +0.12 | -4,678 | 하드스톱(틱) |
| 10:49:02 | 엔진 | SHORT | 1 | 1m | 1 | +0.30 | +4,322 | 하드스톱(틱) |
| 11:08:01 | 엔진 | SHORT | 1 | 5m | 1 | -1.46 | -83,660 | 하드스톱(틱) |
| 11:29:44 (추정귀속) | 외부 | LONG | 1 | — | 1 | -1.26 | -73,691 | 하드스톱(틱) |
| 12:24:25 (추정귀속) | 외부 | LONG | 1 | — | 1 | -1.10 | -65,721 | 하드스톱(틱) |

**출처별 소계** — 엔진 4건 -78,691원 · 외부 7건 -692,589원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 7건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 18행** (부분청산 7 · 전량청산 11)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:26:28 | 부분 | 1 | -2.17 | -119,024 | 하드스톱(틱) |
| 09:26:28 | 부분 | 1 | -2.15 | -118,024 | 하드스톱(틱) |
| 09:26:28 | 전량 | 1 | -2.15 | -118,024 | 하드스톱(틱) |
| 09:33:09 | 부분 | 1 | +1.59 | +68,959 | TP1 부분청산 33% |
| 09:39:01 | 부분 | 1 | +2.61 | +119,959 | TP2 부분청산 33% |
| 09:41:08 | 전량 | 1 | +1.75 | +76,959 | 하드스톱(틱) |
| 09:48:10 | 전량 | 1 | -1.84 | -102,691 | 하드스톱(틱) |
| 09:51:43 | 부분 | 1 | +0.29 | +3,834 | 미추적체결(pending_miss) |
| 09:51:43 | 전량 | 1 | +0.25 | +1,834 | 미추적체결(pending_miss) |
| 10:14:23 | 부분 | 1 | -2.28 | -124,653 | 하드스톱(틱) |
| 10:14:23 | 부분 | 1 | -2.22 | -121,653 | 하드스톱(틱) |
| 10:14:23 | 전량 | 1 | -2.20 | -120,653 | 하드스톱(틱) |
| 10:19:22 | 전량 | 1 | +0.32 | +5,325 | 하드스톱(틱) |
| 10:39:34 | 전량 | 1 | +0.12 | -4,678 | 하드스톱(틱) |
| 10:51:00 | 전량 | 1 | +0.30 | +4,322 | 하드스톱(틱) |
| 11:15:02 | 전량 | 1 | -1.46 | -83,660 | 하드스톱(틱) |
| 11:34:18 | 전량 | 1 | -1.26 | -73,691 | 하드스톱(틱) |
| 12:27:42 | 전량 | 1 | -1.10 | -65,721 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×14, `미추적체결(pending_miss)`×2, `TP1 부분청산 33%`×1, `TP2 부분청산 33%`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 10/11건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -771,280 = 포지션합 -771,280 → OK · `[청산 완료]` 11건 = 조립 포지션 11건 → OK

### 진입 4건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:18:01 | SHORT | 1 | 1087.84 | 3m | mean-revert |
| 10:39:01 | SHORT | 1 | 1088.5 | 1m | mean-revert |
| 10:49:02 | SHORT | 1 | 1088.56 | 1m | mean-revert |
| 11:08:01 | SHORT | 1 | 1086.5 | 5m | mean-revert |

계약수 분포 — 1계약×4

등급 분포 — `A급(원시C)`×3, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×4, `ofi`×2, `cvd`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×8, **2계약**×1

실제 진입 계약수 — **1계약**×4

> ⚠ 사이저는 최대 **2계약**을 냈는데 실제 진입 최대는 **1계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×9

### 차단 사유 21건 · 16종

| 건수 | 사유 |
|---|---|
| 4 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | ATR 1.00pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.86pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 27초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 42초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 142초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 22초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 2_confidence |
| 1 | 청산 후 쿨다운 — 93초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 59초 후 재진입 가능 |
| 1 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 75초 후 재진입 가능 |
| 1 | ATR 0.70pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.80pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `3_vwap`×1, `4_cvd`×1, `7_prev_bar`×1, `2_confidence`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 6건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×6

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 7건 · 최대 28797ms · 5초 초과 1건

상위 — 28797ms, 3969ms, 3750ms, 3547ms, 3203ms, 3016ms, 2954ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:28 | 28797ms | 4962ms | **23835ms (83%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260907_WARN.log`
```
--- ConstOut ×3(표본)
09:54:00 2026-09-07 09:54:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:11:01 2026-09-07 11:11:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:50:00 2026-09-07 11:50:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×1(표본)
09:00:28 2026-09-07 09:00:28 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260907.log
--- [CB] ×6(표본)
09:26:28 2026-09-07 09:26:28 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:48:10 2026-09-07 09:48:10 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:14:23 2026-09-07 10:14:23 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:15:02 2026-09-07 11:15:02 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:26:28 2026-09-07 09:26:28 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:29:28)
09:26:28 2026-09-07 09:26:28 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:29:28)
09:27:00 2026-09-07 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=401ms | quality=1.00 | cache_age=10s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
09:28:00 2026-09-07 09:28:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=310ms | quality=1.00 | cache_age=70s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
--- [SHAP] 슬로우 ×7(표본)
11:33:01 2026-09-07 11:33:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 965ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:41:01 2026-09-07 11:41:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1095ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:48:01 2026-09-07 11:48:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 971ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:54:01 2026-09-07 11:54:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1050ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- degraded=ON ×8(표본)
09:37:01 2026-09-07 09:37:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=341ms | quality=1.00 | cache_age=58s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
09:38:00 2026-09-07 09:38:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=352ms | quality=1.00 | cache_age=118s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
09:39:00 2026-09-07 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=478ms | quality=1.00 | cache_age=177s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
09:40:00 2026-09-07 09:40:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=340ms | quality=1.00 | cache_age=53s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
--- 강제청산 ×8(표본)
09:23:21 2026-09-07 09:23:21 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.72 (보유 1계약, 평균 1089.72). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
09:23:21 2026-09-07 09:23:21 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.76 (보유 2계약, 평균 1089.74). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
09:23:21 2026-09-07 09:23:21 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.78 (보유 3계약, 평균 1089.7533). 오늘 누적 3건 / 3계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로…
09:30:17 2026-09-07 09:30:17 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1091.38 (보유 1계약, 평균 1091.38). 오늘 누적 4건 / 4계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
--- 메인 스레드 블로킹 ×7(표본)
08:41:10 2026-09-07 08:41:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3547 band=INFO since_pipe_s=NA
09:00:28 2026-09-07 09:00:28 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 28797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=28797 band=ALERT since_pipe_s=0.3
09:05:03 2026-09-07 09:05:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3750 band=INFO since_pipe_s=0.2
09:15:04 2026-09-07 09:15:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3969ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3969 band=INFO since_pipe_s=0.2
```

### `logs/20260907_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:54:00 2026-09-07 09:54:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:56:00 (const_output)
09:54:00 2026-09-07 09:54:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['5m']
09:54:01 2026-09-07 09:54:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['5m'] load=95ms fit=71ms total=168ms
09:55:00 2026-09-07 09:55:00 [INFO] SYSTEM: [ConstOut] ['5m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-09-07 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:06:00 2026-09-07 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:12:00 2026-09-07 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:18:00 2026-09-07 09:18:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
```

### `logs/20260907_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:02 2026-09-07 09:00:02 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×6(표본)
09:54:00 2026-09-07 09:54:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:56:02 2026-09-07 09:56:02 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
11:11:01 2026-09-07 11:11:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
11:13:05 2026-09-07 11:13:05 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-07 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-07 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-07 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-07 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.7% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:30 2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.418
08:40:30 2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
08:40:30 2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
--- 안전망 ×8(표본)
09:07:00 2026-09-07 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-07 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-07 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-07 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260907_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.500 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
08:40:50 2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.395 out_max=0.1252 (기준 auc<0.53 and span<0.020, 기저율=0.1250 n=80) → 보정 미적용, raw 통과
08:40:50 2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.513 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
08:40:50 2026-09-07 08:40:50 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00048 auc=0.543 out_max=0.1288 (n=140) → 보정 재적용
```

### `logs/20260907_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
09:27:00 2026-09-07 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=401ms | quality=1.00 | cache_age=10s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
09:28:00 2026-09-07 09:28:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=310ms | quality=1.00 | cache_age=70s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
09:29:00 2026-09-07 09:29:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=376ms | quality=1.00 | cache_age=130s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
09:30:00 2026-09-07 09:30:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=466ms | quality=1.00 | cache_age=6s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
--- degraded=ON ×8(표본)
09:37:01 2026-09-07 09:37:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=341ms | quality=1.00 | cache_age=58s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
09:38:00 2026-09-07 09:38:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=352ms | quality=1.00 | cache_age=118s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
09:39:00 2026-09-07 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=478ms | quality=1.00 | cache_age=177s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
09:40:00 2026-09-07 09:40:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=340ms | quality=1.00 | cache_age=53s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260907_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 9 | 10:02:42 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1085.58 — 진입 경로가 파라미터를 넘기지… |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260907_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 9 | 08:41:06 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:07 [WARNING] scaler 노후=0h  z경고피처=16개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:07 [WARNING] scaler 노후=0h  z경고피처=16개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 43 | 09:54:00 [WARNING] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| 12:00 | 장중 중간점 | 3 | 11:54:01 [WARNING] 슬로우 감지 1050ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260907_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 837 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=11116 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2972 | 08:49:00 [INFO] code=A0569 raw_time=84859 price=1089.08 cum_vol=1399 auction_code=40 recv_type=50 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5119 | 08:54:00 [INFO] code=A0569 raw_time=85400 price=1090.16 cum_vol=2198 auction_code=40 recv_type=49 |
| 10:00 | 장중 초반 | 5094 | 09:54:00 [INFO] code=A0569 raw_time=95400 price=1088.58 cum_vol=24783 auction_code=40 recv_type=49 |
| 12:00 | 장중 중간점 | 2456 | 11:54:00 [INFO] code=A0569 raw_time=115359 price=1088.76 cum_vol=51625 auction_code=40 recv_type=50 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260907_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:07 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 87 | 09:00:02 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 160 | 09:00:02 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에… |
| 10:00 | 장중 초반 | 237 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 148 | 11:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260906 | 20:39 | 로그 본문 |
| 20260904 | 17:33 | 로그 본문 |
| 20260903 | 15:40 | 로그 본문 |
| 20260902 | 15:40 | 로그 본문 |
| 20260901 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260907** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 1. G-1 — `_write_session_state()` 완료 마커 소실 계측
### 2. 🔵 F-1 원인 특정 — `increment_session()` 이 날짜 전환 시 상태를 통째로 갈아끼운다
### 3. G-2 — 예외밀도(`exceptions_10m`)의 태그별 소계
### 4. G-3 — EOD 마감 로그에 일별 `min_conf` 요약
### 5. ⚠ 회귀 발견 — `test_477::test_step9_batch_placeholders_match_params` 가 오늘 깨졌다
### 6. 테스트·검증 총괄
### 7. 함정① 점검 결과
### 8. 🔴 자가유발 결함 1건 — 커밋 메시지에 `@` 혼입 (`3c2f17c`)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
ensemble_decisions` INSERT 에
  `micro_regime_source`·`data_anomaly`·`micro_regime_legacy` 3컬럼을 추가해
  **위치 인덱스가 밀렸다.** 같은 테스트의 개수 일치 검사 3종(`sql.count("?")` ==
  `len(params)`, 컬럼수 == 파라미터수, `fp_psi`/`fp_level` 존재)은 전부 통과 —
  저장 동작이 깨진 것이 아니라 **검사 방식(위치 단정)이 낡았다**.
- **결정**: 이번 자동조치에서 **고치지 않는다.** 다른 세션의 변경이고, 자동조치는
  자기 항목 밖의 코드를 임의로 손대지 않는다. `NEXT_TODO.md` 532-6 등록.
- **Why**: 그래도 방치하면 안 된다 — 이 테스트는 STEP 9 DB 저장 경로를 지키는 감시
  장치이고, 깨진 감시는 없는 감시보다 나쁘다(경보 불감증).
- **How to apply**: 위치 인덱스 대신 컬럼명→인덱스 매핑으로 단정하도록 고치면
  같은 사고가 재발하지 않는다.
- **검증**: HEAD(작업트리 변경 제외) 상태에서도 동일 실패함을 확인 —
  `git --no-optional-locks diff --name-only HEAD -- learning/prediction_buffer.py
  tests/test_477_f1_f5_saturation_psi.py` 가 빈 출력.

### 6. 테스트·검증 총괄

- 신규 23건 전부 통과(`tests/test_532_state_markers_health_tags_dynmc_daily.py`).
  이 중 **4건이 「라이브 반영 0」 불변식** — ⓐ 헬스 판정 함수 시그니처·호출 인자에
  태그 소계가 없음 ⓑ 마커 계측이 `data` 를 수정하지 않음 ⓒ G-3 블록이 `update_dynamic_mc`·
  `insert_mc_change`·`min_confidence` 대입을 하지 않음 ⓓ `git diff --name-only HEAD` 로
  `strategy/entry`(읽기 전용 접근자 1개 예외)·`strategy/exit`·`strategy/risk`·`broker`·
  `config/settings.py` 무변경 확인.
- 전체 스위트 `1,183 passed · 3 failed · 1 skipped · 4 xfailed` (507초).
  실패 3건 = 기존 2건(`test_483` fuoption 사본 대조, `test_504` broker measurement)
  + 위 §5 신규 1건. **전부 이번 변경과 무관**(해당 3파일 전부 미변경, HEAD 에서도 실패).
- 별도 실행 6파일(`test_500_*` 5 · `test_511_exit_order_reject`) 단독 실행 rc=0.

### 7. 함정① 점검 결과

세 항목 모두 구현 전 실물 확인 — G-1 `_write_session_state()` 에 로깅 0줄,
G-2 `exceptions_10m` 태그 분해 함수 부재(`get_level_counts` 만 존재),
G-3 `[DynMCDaily]`/일별 min_conf 요약 검색 0건. **오적발 없음**(전일 523차는 2건 적발).
오늘 06:10·08:03 커밋(524~529차)과의 변경 파일 중복도 없음.

### 8. 🔴 자가유발 결함 1건 — 커밋 메시지에 `@` 혼입 (`3c2f17c`)

- **증상**: 커밋 `3c2f17c` 의 메시지 첫 줄이 `@`, 마지막 줄도 `@`. `%s` 로 뽑으면
  제목이 `@ [MW0601] 532차 후속: …` 이 된다. 본문·트레일러는 온전.
- **원인**: PowerShell here-string 문법 `git commit -m @'…'@` 을 **Bash** 에서 실행.
  Bash 는 `@` 를 리터럴로 붙이고 나머지를 작은따옴표 문자열로 읽는다.
- **결정**: **되쓰기 금지**(자동조치 지시문 「절대 하지 말 것」에 `git push --force`).
  이미 원격에 올라갔으므로 정정하지 않고 기록으로 남긴다. 정정 여부는 사용자 판단.
- **Why**: 규약을 어겨 얻는 미관상 이득보다, 자동 예약작업이 원격 이력을 임의로
  되쓰는 선례를 만드는 비용이 훨씬 크다. 병행 세션이 그 사이 fetch 했다면
  되쓰기는 그쪽 작업트리를 깨뜨린다(멀티 세션 git 조작 위험).
- **How to apply**: 앞으로 자동조치 커밋 메시지는 **Bash 히어독**
  (`git commit -F - <<'MSG'`)으로만 작성한다. 셸별 문자열 문법을 섞지 않는다.
  ⚠ `CLAUDE.md` 「멀티PC 작업 컨벤션」이 기록한 `f6ade3e`("커밋 메시지 첫 줄이 `@`")
  와 **같은 형태의 재발**이다 — 그때는 푸시 전이라 amend 로 정정됐다.
- **검증**: `git --no-optional-locks log -1 --format=%B | cat -A` 로 `@$` 2줄 확인.
  `NEXT_TODO.md` 532-9 등록.

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 관측 예정
## 2026-09-04 (MW0601 529차 — 스윙 피처 착수 · 3_vwap×TrendGate 최적안)
## 2026-09-04 (MW0601 529차 후속 — 채널 3종 구현 완료)
### 남은 것
## 2026-09-04 (MW0601 530차 — 장전 점검)
## 2026-09-04 (MW0601 531차 — 장중 점검)
## 2026-09-04 (MW0601 532차 — 장후 점검)
## 2026-09-04 (MW0601 532차 후속 — 장후 자동조치)
```

미완료 체크박스 **2460건** (끝에서 30건)
```
- [ ] **528-C** 채널 `leg_exhaustion_entry_watch` 사전등록 — `run≥5 ATR 且 60분 극단≤1 ATR 순방향`, `min_days=25` 且 일자 p<0.05 且
- [ ] **528-D (주간회의 안건)** CORE 3_vwap 순방향 요구 + TrendGate streak≥10 완화가 진입을 연장 쪽으로 미는 구조 — "레그 길이"를
- [ ] **O-t10** CFCG "강등 후보" 뒤 진입 손익 누적(현 23건 −248,263) — 528-B 판정 표본.
- [ ] **O-t11** streak≥10 ON 분 순방향 진입(524차 O-t5 승계, 현 13건 avg −25,376) — 5건 이상 추가 시 집계.
- [ ] **529-2 (P1 라이브 검증)** 첫 거래일: `raw_features`에 `swing_ready_60m` True 비율(개장 60분 후 ~100%) · `dist_to_*` 분포가 오프라인
- [ ] **529-A** 채널 `leg_exhaustion_entry_watch` 사전등록(승인 대기) — 모집단 순방향 진입 且 run≥5 ATR 且 극단≤1.0 ATR 且 ready.
- [ ] **529-B** 승격 형태 사전 확정(감점 `12_leg_position` vs 사이저 ×0.5) — 판정 전에 채널 판정문에 박는다.
- [ ] **529-C** 채널 `streak_leg_end_watch` — TrendGate 완화 적용 분 且 레그 끝 진입(현 35건 −243k / 완화-필수 5건 5승) `min_samples=20`.
- [ ] **529-E** 관측 `leg_entry_early_watch` — 초입(run≤2) 12건 10/2 +532k · 이탈≥1.5σ 且 초입 15건 12/3 +675k.
- [ ] **529-D** 3_vwap **무변경** 확정 기록(실측: 상한 감점 시 +675k 군 손상).
- [ ] **529-2 (P1 라이브 검증, 재확인)** 첫 거래일 스윙 피처 적재 — `swing_ready_60m` True 비율 · `dist_to_*` 분포 ·
- [ ] **529-F (P2)** 캠페인 주간 리포트에 P5-14/15/16 렌더링 연결 — 현재는 `leg_position_watch.py` 단독 실행이다
- [ ] **529-G (P2)** C 채널 원천 취약성 — TrendGate 활성 상태를 `ensemble_decisions`에 컬럼으로 남길지 검토
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
-2 / G-1** — `_write_session_state()` 쓰기 계측 구현 완료.
      쓰기 전 마커 스냅샷 → 성공 시(`else`) `_log_session_state_write()` 대조 →
      소실 시 `[SessionStateDrop]` WARNING(호출부 파일:행 포함), 정상은 DEBUG.
      모듈 로거 전용(`log_manager` 금지 — `exceptions_10m` 자체 유발 방지, F-17 전례).
- [x] **531-2 / G-2** — `exceptions_10m` 태그별 소계 구현 완료.
      `log_manager.get_exception_tag_counts()` 신설 + `[Health]` 줄에
      `exc_tags=[A]×n … 외 K종` 동봉. `get_level_counts()`·`_classify_health_level()`
      **무변경**(판정 무영향). 소계 총합 = 예외밀도 대사를 테스트가 고정.
- [x] **532-2 / G-3** — EOD `[DynMCDaily]` 일별 min_conf 요약 구현 완료.
      `time_strategy_router.get_zone_min_conf_snapshot()`(읽기 전용 사본) +
      `daily_close()` 한 줄. mc_history 0행과 미측정을 구분해 표기.
- [ ] **532-5 (P1 · 승인 대기 / F-1 수정안)** `session_recovery_service.py:120-129
      increment_session()` 이 날짜 전환 시 5키 dict 로 상태를 통째 교체해
      `p8_last_success_date`·`eod_retrain_ok_date` 를 지운다 — **원인 특정됨**(532차 후속 §2).
      🔴 **아직 고치지 말 것.** 리포트 F-1 이 "3일 연속 재현 시 확정"을 사전등록했고
      원인 후보 특정 ≠ 확정이다(사전등록 기준 사후 완화 금지 — 458차 D6).
      **판정 수단은 이미 배선됨**: 09-05 첫 기동 로그에
      `[SessionStateDrop] … 호출부=session_recovery_service.py:135` 가 나오면 확정.
      확정 시 수정안 = 새 dict 구성에 두 마커를 `data` 에서 이어받는 항목 추가(한 곳).
      안전성 확인 완료 — 두 마커는 자기 날짜를 값으로 갖고 소비처(`main.py:5640`
      `[PreRetrain]`, `main.py:8493` EKS)가 날짜를 비교하므로 역방향 사고 없음.
- [ ] **532-6 (P1 · 회귀 테스트 복구)** `tests/test_477_f1_f5_saturation_psi.py::
      test_step9_batch_placeholders_match_params` 가 오늘 06:10 커밋 `c9f76f8`
      (524~526차, `ensemble_decisions` 3컬럼 추가)로 깨졌다. `params[-2] == fp_psi`
      **위치 단정**이 밀린 것이며 저장 동작 자체는 정상(개수 일치 검사 3종 통과).
      → 위치 인덱스 대신 **컬럼명→인덱스 매핑**으로 단정하도록 수정할 것.
      깨진 감시는 없는 감시보다 나쁘다(STEP 9 DB 저장 경로 감시 장치).
- [ ] **532-7 (관측 예정 · 09-05 EOD)** `[DynMCDaily]` 가 실제 마감 경로에서 나오는지
      확인. 오늘은 오프라인 실데이터 재현으로만 확인했다(라이브 미검증).
- [ ] **532-8 (사용자 조치)** 미륵이 **재기동 필요** — G-1·G-2·G-3 전부 실행 중
      프로세스에는 미반영. 특히 G-1 은 **09-05 첫 기동 전에** 반영돼 있어야
      532-5 판정 로그가 남는다.
- [ ] **532-9 (P2 · 재발방지 / 자가유발)** 커밋 `3c2f17c` 메시지 첫 줄·마지막 줄에
      `@` 가 섞였다. PowerShell here-string(`@'…'@`)을 Bash 에서 그대로 쓴 실수다.
      본문은 온전하나 `git log --oneline` 제목이 `@ [MW0601] …` 로 보여 PC 태그 규약
      (제목이 `[MW0601]` 로 시작) 기계 검사가 위반으로 읽을 수 있다.
      **되쓰기(force push)는 자동조치 금지 항목**이라 고치지 않았다 — 정정 여부는
      사용자 판단(`git commit --amend` + `git push --force origin v9-dev`).
      ⚠ `CLAUDE.md` 가 기록한 `f6ade3e` 와 **같은 형태의 재발**이다(그때는 푸시 전이라
      amend 로 정정). 앞으로 자동조치 커밋 메시지는 **Bash 히어독**
      (`git commit -F - <<'MSG'`)으로만 쓸 것 — 셸별 문자열 문법을 섞지 않는다.

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

### `data/heartbeat_MW0601_20260907.json` — 244B · 09-07 12:26:44
```json
{
 "pid": 11116,
 "written_at": "2026-09-07T12:27:44",
 "beat_epoch": 1788751661.8954,
 "beat_age_sec": 2.6,
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

- 파일 최종 기록: **09-07 11:52:03**

| 키 | 값 | 수집 대상일(2026-09-07)과 일치 |
|---|---|---|
| `date` | 2026-09-07 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 112개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260907-맥점계측-딥다이브.md` | 10.1KB | 09-07 09:14 |
| `docs/정기점검/매일점검/MW0601-20260907-점검리포트.md` | 22.8KB | 09-07 09:11 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_pre.md` | 54.6KB | 09-07 09:01 |
| `docs/정기점검/매일점검/MW0601-20260904-점검리포트.md` | 83.0KB | 09-04 17:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_post.md` | 92.5KB | 09-04 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_intra.md` | 78.0KB | 09-04 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_pre.md` | 51.1KB | 09-04 09:01 |
| `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md` | 85.0KB | 09-04 07:51 |

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
2. `logs/20260907_WARN.log`: ERROR 이상 25건
3. `logs/20260907_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
4. `logs/20260907_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
5. `logs/20260907_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
6. `logs/20260907_HEALTH.log`: ERROR 이상 10건
7. 사이저 최대 2계약 → 실제 진입 최대 1계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
8. 메인 스레드 정지 5초 초과 **1건** (최대 28797ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
9. `logs/20260907_WARN.log`: **degraded=ON** 8건(표본)
10. `logs/20260907_WARN.log`: **ConstOut** 3건(표본)
11. `logs/20260907_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20260907_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20260907_SIGNAL.log`: **ConstOut** 6건(표본)
14. `logs/20260907_LEARNING.log`: **축퇴** 8건(표본)
15. `logs/20260907_HEALTH.log`: **degraded=ON** 8건(표본)
16. 미커밋 변경 522건 (실질 8건 · **코드(.py) 6건**) — 코드 변경이 커밋되지 않았다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260907*.log` (Windows) / `grep 강제청산 logs/*20260907*.log`*