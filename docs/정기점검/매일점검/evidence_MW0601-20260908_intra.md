# 미륵이 증거 다이제스트 — 2026-09-08 / INTRA

- 생성 2026-09-08 12:26:47 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/peaceful-relaxed-gauss/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260908` · `2026-09-08` · `260908` · `0908`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **22개** 파일 · 22개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260908.log` | 125B | 09-08 08:40 |
| `freeze_sentinel_alert_{DATE}.txt` | 1 | `data/freeze_sentinel_alert_20260908.txt` | 702B | 09-08 09:00 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260908.log` | 3.8KB | 09-08 09:05 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260908.json` | 243B | 09-08 12:26 |
| `launcher_{DATE}_084002_29245.log` | 1 | `logs/Mireuk_batch/launcher_20260908_084002_29245.log` | 9.1MB | 09-08 12:26 |
| `launcher_{DATE}_090400_1173.log` | 1 | `logs/Mireuk_batch/launcher_20260908_090400_1173.log` | 1.2KB | 09-08 09:04 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260908.log` | 8.6KB | 09-08 12:24 |
| `retrain_intraday_{DATE}_090459.log` | 1 | `logs/retrain_intraday_20260908_090459.log` | 5.3KB | 09-08 09:05 |
| `retrain_intraday_{DATE}_100501.log` | 1 | `logs/retrain_intraday_20260908_100501.log` | 2.8KB | 09-08 10:05 |
| `retrain_intraday_{DATE}_111100.log` | 1 | `logs/retrain_intraday_20260908_111100.log` | 2.8KB | 09-08 11:11 |
| `retrain_intraday_{DATE}_115001.log` | 1 | `logs/retrain_intraday_20260908_115001.log` | 2.8KB | 09-08 11:50 |
| `{DATE}_DATA.log` | 1 | `logs/20260908_DATA.log` | 178.7KB | 09-08 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260908_DEBUG.log` | 126.0KB | 09-08 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260908_HEALTH.log` | 6.9KB | 09-08 12:07 |
| `{DATE}_HOGA.log` | 1 | `logs/20260908_HOGA.log` | 24.9MB | 09-08 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260908_LEARNING.log` | 180.1KB | 09-08 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260908_MICRO.log` | 506.1KB | 09-08 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260908_PROBE.log` | 55.4KB | 09-08 12:25 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260908_SIGNAL.log` | 337.4KB | 09-08 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260908_SYSTEM.log` | 8.7MB | 09-08 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260908_TRADE.log` | 11.3KB | 09-08 12:23 |
| `{DATE}_WARN.log` | 1 | `logs/20260908_WARN.log` | 50.0KB | 09-08 12:26 |

## 2. 코드·커밋 상태

- HEAD `698c4ae` · 브랜치 `v9-dev` · 미커밋 551건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
… 외 511건
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

_본문 미열람(설정): `20260908_HOGA.log` 24.9MB — 존재와 크기만 증거로 본다_

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

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20260908_115001.log`, `retrain_intraday_20260908_100501.log`, `20260908_MICRO.log`, `20260908_DATA.log`, `20260908_PROBE.log`, `launcher_20260908_084002_29245.log`, `launcher_20260908_090400_1173.log`, `20260908_DEBUG.log`_

### `logs/20260908_TRADE.log` — 11.3KB · 80행 · 최종 12:23:11

- 형식 평문 · 시각 인식 80행 · WARNING=8, INFO=72

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-08 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-08 09:18:50 [INFO] TRADE: [Chejan] 상태=접수 주문번호=681 code=A0569 방향=LONG 체결=2 미체결=0
2026-09-08 09:18:50 [INFO] TRADE: [Chejan] 상태=체결 주문번호=681 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-08 09:18:50 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1121.60 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
  …
2026-09-08 11:37:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-08 11:39:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-09-08 11:40:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-08 12:23:10 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-08 12:23:11 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 7 | 09:18:50 | 09:37:49 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1121.60 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `ProfitGuard-L1` | 1 | 09:40:00 | 09:40:00 | 트레일링 발동 — 피크 +684,928원 대비 10% 하락 (현재 +524,940원 < 보호선 +616,435원) |

**채널** — `TRADE`×80

**컴포넌트 상위 15** — `Chejan`×23, `Position`×15, `Sizer`×11, `PositionFallback`×7, `체결동기화`×7, `청산 완료`×6, `ProfitGuard`×3, `주문요청`×2, `MarginCap`×2, `TickTP1`×1, `TP1 부분청산`×1, `TickStop-S0C`×1, `ProfitGuard-L1`×1

### `logs/20260908_WARN.log` — 50.0KB · 277행 · 최종 12:26:03

- 형식 평문 · 시각 인식 277행 · CRITICAL=11, ERROR=7, WARNING=259

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA
2026-09-08 09:04:57 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-08 09:04:57 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-08 09:04:58 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 235ms account=333044256
2026-09-08 09:04:59 [WARNING] SYSTEM: [RESTART] 장중 재시작 감지 09:04 — GapOffset=미설정(첫분봉 재설정 예정)  pre_market_scaler=False
  …
2026-09-08 12:11:00 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: NORMAL → RESTRICTED (acc=10.0%)
2026-09-08 12:11:00 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: NORMAL → RESTRICTED (acc=10.0%)
2026-09-08 12:24:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 9562ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9562 band=WARN since_pipe_s=0.1
2026-09-08 12:24:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260908.log
2026-09-08 12:26:03 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1204ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 11 | 09:06:05 | 09:30:00 | level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1 |
| ERROR | `ExternalEntry` | 7 | 09:18:50 | 09:37:49 | 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — LONG 1계약 @ 1121.6 (보유 1계약, 평균 1121.6). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-08 09:06:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
2026-09-08 09:21:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=516ms | quality=1.00 | cache_age=17s | exceptions_10m=25 | exc_tags=[OrderSync]×16 [ExternalEntry]×5 [ExitCooldown]×4
```

</details>

<details><summary>ERROR/ExternalEntry 원문 2건</summary>

```
2026-09-08 09:18:50 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — LONG 1계약 @ 1121.6 (보유 1계약, 평균 1121.6). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
2026-09-08 09:18:50 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — LONG 1계약 @ 1121.58 (보유 2계약, 평균 1121.59). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
```

</details>

**WARNING — 태그 32종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 83 | 08:41:11 | 12:24:08 | _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA |
| `ChejanFlow` | 23 | 09:18:50 | 09:39:12 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1121.78 | fill_qty=2 | gubun='0' | order_no='681' | pending='NONE' | position='FLAT' | position_qty=0 | sell_balance=0 | side='LONG' | … |
| `ChejanMatch` | 23 | 09:18:50 | 09:39:12 | order_no='681' | pending='NONE' | pending_matched=False |
| `OrderSync` | 22 | 09:18:50 | 09:37:49 | 미추적 체결 감지 (pending_miss) order_no=681 side=LONG qty=1 price=1121.6 before=FLAT |
| `Health` | 16 | 09:19:00 | 12:06:00 | level=WARNING degraded=OFF | latency=373ms | quality=1.00 | cache_age=80s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2 |
| `PipePerf` | 12 | 09:05:01 | 11:51:03 | [GBM재학습중] total=1094ms | S0=2ms S1=62ms S2=0ms S3=0ms S4=120ms S5=570ms S6=323ms S7=14ms S8=3ms |
| `CB⑤` | 12 | 09:05:02 | 11:51:03 | 파이프라인 1094ms 경고 (기준 1000ms) [장시작 버스트] [GBM재학습중→임계×2] |
| `ExitCooldown` | 12 | 09:20:19 | 09:39:12 | 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:19) |
| `ScalerRefresh` | 8 | 09:14:00 | 12:10:00 | 5분 누적 수익률 +0.381% (임계 ±0.246%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `HealthPolicy` | 7 | 09:07:00 | 11:52:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=5090ms quality=1.00 cache=0s exc10m=4) | cause=S0(4405ms) |
| `CB③-P4` | 6 | 10:55:00 | 12:11:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `MainStallTrace` | 4 | 09:05:06 | 12:24:08 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260908.log |

**채널** — `SYSTEM`×250, `HEALTH`×27

**컴포넌트 상위 15** — `LiveDBG`×83, `Health`×27, `ChejanFlow`×23, `ChejanMatch`×23, `OrderSync`×22, `PipePerf`×12, `CB⑤`×12, `ExitCooldown`×12, `ScalerRefresh`×8, `HealthPolicy`×7, `ExternalEntry`×7, `CB③-P4`×6, `MainStallTrace`×4, `PendingOrder`×4, `LEVELS 수동`×3

### `logs/20260908_SYSTEM.log` — 8.7MB · 66321행 · 최종 12:26:47

- 형식 평문 · 시각 인식 66318행 · INFO=66318, PLAIN=3

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:35 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=23044 | 행감지=30s all_threads=True
2026-09-08 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-08 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-08 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-08 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-07) 종가 버퍼 로드: 384봉
  …
2026-09-08 12:28:02 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122802 price=1135.82 cum_vol=78298 auction_code=40 recv_type=50
2026-09-08 12:28:02 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122802 price=1135.82 cum_vol=78302 auction_code=40 recv_type=49
2026-09-08 12:28:02 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122802 price=1135.82 cum_vol=78303 auction_code=40 recv_type=49
2026-09-08 12:28:02 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122802 price=1135.88 cum_vol=78304 auction_code=40 recv_type=50
2026-09-08 12:28:02 [INFO] SYSTEM: [CybosRT-AUCTION] code=A0569 raw_time=122802 price=1135.92 cum_vol=78305 auction_code=40 recv_type=50
```

</details>

**채널** — `SYSTEM`×66318

**컴포넌트 상위 15** — `CybosRT-AUCTION`×63150, `CybosInvestorRaw`×816, `CybosRT-TICK`×636, `CybosRT-ROLLOVER`×204, `BAR-CLOSE`×204, `CVD-ANCHOR`×204, `S6Detail`×204, `PipePerf`×204, `TickUI`×202, `System`×47, `CybosEvent`×46, `MicroRegime`×45, `CybosDailyPnl`×44, `BalanceUI`×43, `RegimeFingerprint`×37

### `logs/20260908_SIGNAL.log` — 337.4KB · 2887행 · 최종 12:26:02

- 형식 평문 · 시각 인식 2887행 · WARNING=1076, INFO=1811

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
  …
2026-09-08 12:28:00 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=3m tf=3.75 → TP1×0.5
2026-09-08 12:28:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.341<mc0.620)
2026-09-08 12:28:00 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=44.2% size_mult=1.00 reason=meta_skip
2026-09-08 12:28:00 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L1-Trail] 피크 +684,928원 대비 10% 하락 (현재 +524,940원 < 보호선 +616,435원) | src=broker_net_est
2026-09-08 12:28:00 [INFO] SIGNAL: [차단] ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 750 | 09:05:02 | 12:20:01 | 1m 'macro_krw_chg' scale=0.0979 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 124 | 09:05:01 | 12:15:00 | 1m 스케일러 1031분 미갱신 (≥90분) — 변동성 레짐 시프트 시 z-score 왜곡 가능 |
| `ScalerMonitor` | 96 | 09:05:01 | 12:16:00 | ts=09:04 horizon=1m age=1031m max_z=-30.99(queue_depletion_speed) extreme=8 adj=6 |
| `Checklist` | 52 | 09:16:00 | 12:28:00 | 신뢰도 미달 35.9% < 38.0% → 강제 X등급 |
| `WeightCollapse` | 46 | 09:06:04 | 12:27:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConfFloorGuard` | 3 | 09:06:04 | 11:25:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3800 (conf_floor=0.330, min_conf=0.380, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `ConstOut` | 3 | 10:04:00 | 11:49:02 | 5m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외 |
| `PCR-Dampen` | 2 | 09:18:00 | 09:31:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×2887

**컴포넌트 상위 15** — `ScalerFloor`×750, `SIGNAL`×408, `ProfitGuard`×210, `Ensemble`×209, `FQAdj`×204, `ZeroDiag`×191, `MetaGate`×159, `Model`×154, `ScalerMonitor`×96, `Checklist`×79, `ATR-Horizon`×61, `차단`×51, `WeightCollapse`×46, `MicroRegime`×45, `IntradayRegime`×36

### `logs/20260908_LEARNING.log` — 180.1KB · 1661행 · 최종 12:26:02

- 형식 평문 · 시각 인식 1661행 · WARNING=159, INFO=1502

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2888 < conf_floor=0.3300 (span=0.00234 auc=0.639 out_max=0.2888, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00009 auc=0.506 out_max=0.2875 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00011 auc=0.505 out_max=0.3218 (기준 auc<0.53 and span<0.020, 기저율=0.3217 n=115) → 보정 미적용, raw 통과
  …
2026-09-08 12:28:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0474% buf_n=20 nonzero=19 prev_p=1135.32 cur_p=1135.86
2026-09-08 12:28:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=33.3% UP)
2026-09-08 12:28:00 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=33.3% UP)
2026-09-08 12:28:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=63.6% 예측=FL 실제=UP)
2026-09-08 12:28:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=15.3%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 159 | 08:40:52 | 12:23:00 | 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제] |

**채널** — `LEARNING`×1661

**컴포넌트 상위 15** — `LEARNING`×650, `Calibration`×309, `SGD`×204, `sigma`×191, `Bias⚠`×96, `Bias`×65, `MetaConf`×41, `OnlineLearner`×39, `ScalerWarmup`×25, `GBM-64`×8, `GBM`×8, `BiasReset`×8, `SHAP`×7, `RF`×5, `ExtremityCorrector`×2

### `logs/20260908_HEALTH.log` — 6.9KB · 38행 · 최종 12:07:00

- 형식 평문 · 시각 인식 38행 · CRITICAL=11, WARNING=16, INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 09:06:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
2026-09-08 09:07:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=524ms | quality=1.00 | cache_age=96s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
2026-09-08 09:19:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=373ms | quality=1.00 | cache_age=80s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2
2026-09-08 09:20:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=445ms | quality=1.00 | cache_age=140s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2
2026-09-08 09:21:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=516ms | quality=1.00 | cache_age=17s | exceptions_10m=25 | exc_tags=[OrderSync]×16 [ExternalEntry]×5 [ExitCooldown]×4
  …
2026-09-08 11:15:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=316ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[Contrarian]×1
2026-09-08 11:51:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2534ms | quality=1.00 | cache_age=18s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-08 11:52:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=322ms | quality=1.00 | cache_age=75s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-08 12:06:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=280ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-09-08 12:07:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=261ms | quality=1.00 | cache_age=57s | exceptions_10m=0
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 11 | 09:06:05 | 09:30:00 | level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-08 09:06:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
2026-09-08 09:21:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=516ms | quality=1.00 | cache_age=17s | exceptions_10m=25 | exc_tags=[OrderSync]×16 [ExternalEntry]×5 [ExitCooldown]×4
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 16 | 09:19:00 | 12:06:00 | level=WARNING degraded=OFF | latency=373ms | quality=1.00 | cache_age=80s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2 |

**채널** — `HEALTH`×38

**컴포넌트 상위 15** — `Health`×37, `HealthTrend`×1

### `logs/retrain_intraday_20260908_090459.log` — 5.3KB · 41행 · 최종 09:05:47

- 형식 평문 · 시각 인식 41행 · INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 09:04:59,262 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-08 09:04:59,262 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-08 09:04:59,262 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-08 09:04:59,262 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-08 09:04:59,263 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_26653f03.json
  …
2026-09-08 09:05:47,920 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-08 09:05:47,921 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-08 09:05:47,921 [INFO] LEARNING: [Retrain] 완료 | 43.5초 | 성공=6/6 호라이즌
2026-09-08 09:05:47,922 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 48.7s 데이터=4800행
2026-09-08 09:05:47,924 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_26653f03.json
```

</details>

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `CUSUM`×1

### `logs/retrain_intraday_20260908_111100.log` — 2.8KB · 22행 · 최종 11:11:21

- 형식 평문 · 시각 인식 22행 · INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 11:11:00,579 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-08 11:11:00,580 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-08 11:11:00,580 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-08 11:11:00,580 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-08 11:11:00,580 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_62f24b22.json
  …
2026-09-08 11:11:21,425 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-08 11:11:21,426 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-08 11:11:21,426 [INFO] LEARNING: [Retrain] 완료 | 18.7초 | 성공=1/1 호라이즌
2026-09-08 11:11:21,427 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 20.8s 데이터=4800행
2026-09-08 11:11:21,429 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_62f24b22.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 7 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 7 |
| 청산(`체결청산`) | 6 |
| 차단(`[차단]`) | 51 |
| 사이저 호출(`[Sizer]`) | 11 |

> 🔴 **엔진 진입 0건인데 계좌 체결 7건** — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.

### 포지션 5건 · 승 3 (60%) · 합계 +2.78pt (+72,991원)  ※ 레그 6행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:18:50 (추정귀속) | 외부 | LONG | 2 | — | 2 | +3.76 | +165,994 | 미추적체결(pending_miss) |
| 09:20:27 (추정귀속) | 외부 | LONG | 1 | — | 1 | +0.10 | -6,022 | 미추적체결(pending_miss) |
| 09:20:36 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +0.34 | +5,980 | 미추적체결(pending_miss) |
| 09:23:21 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +1.56 | +67,012 | 미추적체결(pending_miss) |
| 09:37:49 (추정귀속) | 외부 | LONG | 1 | — | 1 | -2.98 | -159,973 | 하드스톱(틱) |

**출처별 소계** — 외부 5건 +72,991원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**이월 포지션(전일 이전 진입) 추정 — 청산 레그 1행 · +0.12pt · -5,024원**

> 🔴 **위 포지션 표 합계(+72,991원)에 이 금액은 들어 있지 않다.** 오늘 로그에 여는 이벤트(`[Position] 진입` 또는 FLAT→보유 체결)가 없는 청산 레그라 포지션으로 조립되지 않는다 — **데이터 손실이 아니라 귀속 불가**이며, 금액 자체는 체결 실측이라 정확하다.
>
> **오늘 계좌에서 실제로 오간 돈 = +67,967원** (오늘 연 포지션 +72,991원 + 이월분 -5,024원). 판정 원천은 여전히 브로커 실측 net 이다(493차 F-1) — 이 줄은 로그 축의 교차확인용이다.
>
> ⚠ 이월분이 있다는 것은 **전 거래일이 FLAT 으로 끝나지 않았다는 뜻**이다 — 절대원칙 §1(15:10 강제청산) 위반 여부를 전일 리포트로 확인할 것.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:20:44 | 이월 | 1 | +0.12 | -5,024 | 미추적체결(pending_miss) |

> ⚠ **(추정귀속) 5건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 6행** (부분청산 1 · 전량청산 6)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:20:18 | 부분 | 1 | +1.85 | +81,497 | TP1 부분청산 33% |
| 09:20:19 | 전량 | 1 | +1.91 | +84,497 | 미추적체결(pending_miss) |
| 09:20:27 | 전량 | 1 | +0.10 | -6,022 | 미추적체결(pending_miss) |
| 09:20:36 | 전량 | 1 | +0.34 | +5,980 | 미추적체결(pending_miss) |
| 09:23:58 | 전량 | 1 | +1.56 | +67,012 | 미추적체결(pending_miss) |
| 09:39:12 | 전량 | 1 | -2.98 | -159,973 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `미추적체결(pending_miss)`×4, `TP1 부분청산 33%`×1, `하드스톱(틱)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/5건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +67,967 = 포지션합 +72,991 → **불일치 ⚠** · `[청산 완료]` 6건 = 조립 포지션 5건 → **불일치 ⚠** · **귀속 실패(이월 추정) 레그 1행 · -5,024원 ⚠** — 위 「이월 포지션」 블록 참조, **헤드라인 합계에 미포함**

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×5, **2계약**×2, **3계약**×4

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×11

### 차단 사유 51건 · 34종

| 건수 | 사유 |
|---|---|
| 15 | 등급X — 미통과 항목: 2_confidence |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 게이트 강등 X — ProfitGuard 진입 차단 ([L1-Trail] 피크 +684,928원 대비 10% 하락 (현재 +524,940원 < 보호선 +616,… |
| 1 | 청산 후 쿨다운 — 57초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 131초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 71초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.0pt > ATR×5.0=8.0pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.9pt > ATR×5.0=7.5pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.2pt > ATR×5.0=7.6pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.7pt > ATR×5.0=7.7pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.0pt > ATR×5.0=7.4pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.5pt > ATR×5.0=7.1pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.3pt > ATR×5.0=6.8pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.2pt > ATR×5.0=7.0pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.4pt > ATR×5.0=7.0pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.1pt > ATR×5.0=7.3pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.4pt > ATR×5.0=7.5pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.5pt > ATR×5.0=7.5pt (시가=1110.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.5pt > ATR×5.0=7.7pt (시가=1110.52 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×15, `3_vwap`×1, `4_cvd`×1, `5_ofi`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 12건 · 최대 9562ms · 5초 초과 4건

상위 — 9562ms, 7578ms, 6454ms, 5625ms, 4813ms, 3594ms, 3235ms, 2735ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:05:06 | 7578ms | **미측정** | — |
| 09:06:05 | 6454ms | 5090ms | **1364ms (21%)** |
| 09:30:05 | 5625ms | 432ms | **5193ms (92%)** |
| 12:24:08 | 9562ms | 373ms | **9189ms (96%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260908_WARN.log`
```
--- ConstOut ×3(표본)
10:04:00 2026-09-08 10:04:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:10:01 2026-09-08 11:10:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:49:02 2026-09-08 11:49:02 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×3(표본)
09:05:06 2026-09-08 09:05:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260908.log
09:30:05 2026-09-08 09:30:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260908.log
12:24:08 2026-09-08 12:24:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260908.log
--- [CB] ×1(표본)
09:39:12 2026-09-08 09:39:12 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:20:19 2026-09-08 09:20:19 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:19)
09:20:19 2026-09-08 09:20:19 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:19)
09:20:27 2026-09-08 09:20:27 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:27)
09:20:27 2026-09-08 09:20:27 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:27)
--- [SHAP] 슬로우 ×3(표본)
11:42:01 2026-09-08 11:42:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 921ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:09:02 2026-09-08 12:09:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1018ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:26:03 2026-09-08 12:26:03 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1204ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- level=CRITICAL ×1(표본)
09:06:05 2026-09-08 09:06:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
--- 강제청산 ×7(표본)
09:18:50 2026-09-08 09:18:50 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — LONG 1계약 @ 1121.6 (보유 1계약, 평균 1121.6). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 …
09:18:50 2026-09-08 09:18:50 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — LONG 1계약 @ 1121.58 (보유 2계약, 평균 1121.59). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히…
09:20:19 2026-09-08 09:20:19 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1123.5 (보유 1계약, 평균 1123.5). 오늘 누적 3건 / 3계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지…
09:20:27 2026-09-08 09:20:27 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — LONG 1계약 @ 1123.34 (보유 1계약, 평균 1123.34). 오늘 누적 4건 / 4계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히…
--- 메인 스레드 블로킹 ×8(표본)
08:41:11 2026-09-08 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA
09:05:06 2026-09-08 09:05:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7578ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7578 band=WARN since_pipe_s=0.1
09:06:05 2026-09-08 09:06:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6454ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6454 band=WARN since_pipe_s=0.1
09:30:05 2026-09-08 09:30:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5625 band=WARN since_pipe_s=0.1
```

### `logs/20260908_SYSTEM.log`
```
--- ConstOut ×8(표본)
10:04:00 2026-09-08 10:04:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 10:06:00 (const_output)
10:04:00 2026-09-08 10:04:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['5m']
10:04:01 2026-09-08 10:04:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['5m'] load=110ms fit=82ms total=206ms
10:05:00 2026-09-08 10:05:00 [INFO] SYSTEM: [ConstOut] ['5m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:05:00 2026-09-08 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:11:00 2026-09-08 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:17:00 2026-09-08 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:22:00 2026-09-08 09:22:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
```

### `logs/20260908_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:06:04 2026-09-08 09:06:04 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3800 (conf_floor=0.330, min_conf=0.380, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:47:00 2026-09-08 10:47:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3795 ≥ 필요 0.3720 (span=0.0097, auc=0.543)
11:00:00 2026-09-08 11:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3633 < 필요 0.3720 (conf_floor=0.330, min_conf=0.372, span=0.0073, auc=0.530). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:12:03 2026-09-08 11:12:03 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3745 ≥ 필요 0.3720 (span=0.0099, auc=0.531)
--- ConstOut ×8(표본)
10:04:00 2026-09-08 10:04:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외
10:06:03 2026-09-08 10:06:03 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
11:10:01 2026-09-08 11:10:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
11:10:01 2026-09-08 11:10:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
--- WeightCollapse ×8(표본)
09:06:04 2026-09-08 09:06:04 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
09:09:00 2026-09-08 09:09:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
09:12:00 2026-09-08 09:12:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
09:15:00 2026-09-08 09:15:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:31 2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
--- 안전망 ×8(표본)
09:06:04 2026-09-08 09:06:04 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:09:00 2026-09-08 09:09:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:12:00 2026-09-08 09:12:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:15:00 2026-09-08 09:15:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260908_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2888 < conf_floor=0.3300 (span=0.00234 auc=0.639 out_max=0.2888, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00009 auc=0.506 out_max=0.2875 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00011 auc=0.505 out_max=0.3218 (기준 auc<0.53 and span<0.020, 기저율=0.3217 n=115) → 보정 미적용, raw 통과
```

### `logs/20260908_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
09:21:00 2026-09-08 09:21:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=516ms | quality=1.00 | cache_age=17s | exceptions_10m=25 | exc_tags=[OrderSync]×16 [ExternalEntry]×5 [ExitCooldown]×4
09:22:00 2026-09-08 09:22:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=517ms | quality=1.00 | cache_age=77s | exceptions_10m=25 | exc_tags=[OrderSync]×16 [ExternalEntry]×5 [ExitCooldown]×4
09:23:00 2026-09-08 09:23:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=351ms | quality=1.00 | cache_age=137s | exceptions_10m=25 | exc_tags=[OrderSync]×16 [ExternalEntry]×5 [ExitCooldown]×4
09:24:00 2026-09-08 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=389ms | quality=1.00 | cache_age=13s | exceptions_10m=31 | exc_tags=[OrderSync]×20 [ExternalEntry]×6 [ExitCooldown]×5
--- level=CRITICAL ×1(표본)
09:06:05 2026-09-08 09:06:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260908_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 5 | 09:54:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |

- 이 로그 생존구간: 08:41 ~ 12:23

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260908_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 1 | 08:41:11 [WARNING] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 28 | 09:04:57 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 10:00 | 장중 초반 | 8 | 09:57:00 [WARNING] 5분 누적 수익률 +0.224% (임계 ±0.210%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 2 | 11:54:03 [WARNING] _tick_header 간격 3594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3594 band=… |

- 이 로그 생존구간: 08:41 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260908_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 12 | 08:40:35 [INFO] 활성화 | file=logs\crash_fault.log PID=23044 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 ⚠ | 0 | — |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 1237 | 09:04:57 [INFO] create begin progid=Dscbo1.CpFConclusion event=fill latest=False inputs={} |
| 10:00 | 장중 초반 | 4905 | 09:54:00 [INFO] code=A0569 raw_time=95359 price=1123.44 cum_vol=33472 auction_code=40 recv_type=50 |
| 12:00 | 장중 중간점 | 2734 | 11:54:00 [INFO] code=A0569 raw_time=115359 price=1128.08 cum_vol=69752 auction_code=40 recv_type=50 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:28

**매분 루프 커버리지 09:00~15:10: 205/371분 (55.3%)**

연속 3분 이상 기록 없는 구간 2개:

| 시작 | 끝 | 분 |
|---|---|---|
| 09:00 | 09:03 | 4 |
| 12:29 | 15:10 | 162 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260908_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:40:31 [INFO] 기동 복원: OPEN_VOLATILE  0.600 → 0.410 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:00:03 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 118 | 09:05:01 [WARNING] 1m 스케일러 1031분 미갱신 (≥90분) — 변동성 레짐 시프트 시 z-score 왜곡 가능 |
| 10:00 | 장중 초반 | 189 | 09:57:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 12:00 | 장중 중간점 | 130 | 11:54:00 [WARNING] 신뢰도 미달 33.4% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:28

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
| **오늘 20260908** | **12:28** | 로그 본문 |

- 델타 **-305분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.8MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 부가 확인 — F-1(session_state 마커 유실) 가설 확정 [538차 승계]
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
og`의 30초 주기 전체 스레드 스냅샷 47회가 전부 메인 스레드를
`TradeInit`(COMObject `CpTrade.CpTdUtil`) 안에 고정한다. `TradeInit` 자체는 복구 후
47ms만에 완료됐다(`[LiveDBG] request_futures_balance TradeInit 완료 47ms`, 09:04:57) —
즉 호출 자체가 느린 게 아니라 **그 시점까지 실행 기회를 얻지 못한 것**이다.
서버 종류는 `Cybos 모의투자`(`[DBG CK-2b]`)로 실서버 오접속은 아니다.

436차(2026-08 어느 시점, DECISION_LOG 상단 위치 확인 필요)에 등록된 동일 계열 사고
("TradeInit(0)=-1" + "CPTRADE — 주문오브젝트 사용 동의를 하지 않으셨습니다" 모달 무한 대기)와
증상이 유사하나, 오늘 로그에는 그 모달 텍스트나 `ret=-1`이 남지 않아 **"확정"이 아니라
"유력 가설(정합성 미확인)"**로만 기록한다(SKILL.md 함정① G-3 규약).

436차 조치(`scripts/check_cybos_account.py`의 20초 워치독)는 launcher가 main.py 실행
**전에** 별도 프로세스로 도는 프리플라이트이며, 오늘도 `[OK] cybos preflight 통과`로
정상 종료됐다. 즉 그 워치독은 main.py **자신의** `connect()` 내부 `TradeInit()` 호출을
보호하지 않는다 — 서로 다른 COM 세션이다.

**추가 발견**: 인프로세스 동결 워치독 FZ-1(`utils/freeze_watchdog.py:evaluate()`)은
`beat_age_sec is None`(첫 하트비트 이전)이면 판정을 보류하도록 설계돼 있다(계측 4원칙
② 미측정≠0). 오늘처럼 첫 하트비트 **이전** 단계(로그인 단계)에서 멈추면 FZ-1은 아무리
길게 멈춰도 발화하지 않는다 — 실제로 `[TS]` 하트비트 줄이 08:41~09:05 사이 전무했다.
프로세스 밖 센티넬 FZ-2(`freeze_sentinel.py`)만 09:00:25·09:01:25에 `CRITICAL`을 정확히
잡았으나, FZ-2는 설계상 알림 전용(하드 종료 미구현)이라 조치가 없었다. "기동 단계
동결은 아무도 하드 종료를 못 한다"는 사각지대는 이번에 처음 등록되는 관측이다
(`DECISION_LOG`·`NEXT_TODO` 전수 검색 결과 선행 기록 없음).

### 결정

**원인을 코드로 고치지 않고 이번 세션은 계측·기록만 한다** — 장전 예약은 코드 변경 금지
(SKILL.md 규칙). F-1(TradeInit 타임아웃/섀도 계측)은 구현계획만 세워 장후로 넘긴다.

### Why

- 계측 4원칙 ④(폴백 가시화)와 같은 취지 — "느린 것"과 "실행 기회를 못 얻은 것"을
  구분하지 않으면 다음에 또 47ms 완료 로그만 보고 "정상이었다"고 오판할 수 있다.
- 313차/함정① 원칙 — 근거(모달 텍스트·ret 값)가 없는 상태에서 436차와 "같은 사고"라고
  확정하지 않고 유력 가설로만 남긴다.

### How to apply

- `collection/cybos/api_connector.py:connect()`의 `TradeInit(0)` 호출 경로에 소요시간
  로깅(섀도)을 먼저 붙이고, 사용자 승인 후 타임아웃 예외 승격을 적용한다
  (`config/settings.py:CYBOS_TRADE_INIT_TIMEOUT_SEC` 신설 제안, 30~60초).
- 다음 재발 시 화면 상태(모달 유무)를 확인할 수 있으면 436차형 원인을 확정할 수 있다.

### 검증

- 다음 거래일 `crash_fault.log`에서 `TradeInit` 반복 출현 여부 관측(O-p1).
- `[SessionStateDrop]` 재현 여부 관측(O-p2, 아래 별도 항목 참조).

### 부가 확인 — F-1(session_state 마커 유실) 가설 확정 [538차 승계]

09:04:59에 `[SessionRollover]`·`[SessionStateDrop]`이 실제로 발동, 새로 초기화된 키에
`p8_last_success_date`·`eod_retrain_ok_date`가 포함됨을 확인 — `NEXT_TODO.md` 538-5가
요구한 판정 기준을 정확히 충족해 **F-1 가설 확정**. 538-4(F-1 본체 적용)로 승계한다.
단, 이는 어제(09-07) EOD·P8 실패를 의미하지 않는다 — `data/eod_retrain_done_20260907.txt`
`data/daily_close_done_20260907.txt` `data/shutdown_normal_20260907.txt` 세 마커 모두
09-07 15:40~15:53 정상 생성 확인(어제 EOD·P8은 성공, 오늘 마커만 유실됨).

### 병행 세션

이 세션이 도는 동안 병행 세션 없음(당일 커밋 0건, `docs/정기점검/매일점검/` 당일
산출물 이 리포트가 최초 — `git log --since` 및 `ls -lt` 로 확인).

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-04 (MW0601 530차 — 장전 점검)
## 2026-09-04 (MW0601 531차 — 장중 점검)
## 2026-09-04 (MW0601 532차 — 장후 점검)
## 2026-09-04 (MW0601 532차 후속 — 장후 자동조치)
## 2026-09-07 (MW0601 536차 — 장중 점검)
## 2026-09-07 (MW0601 537차 — 장후 점검, 종합 완성본)
## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)
## 2026-09-08 (MW0601 543차 — 장전 점검)
```

미완료 체크박스 **2498건** (끝에서 30건)
```
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
- [ ] **543-1 (P0, 신규 / F-1)** `collection/cybos/api_connector.py:430`의 `TradeInit(0)`
- [ ] **543-2 (P2, 고도화 제안)** FZ-1 워치독(`utils/freeze_watchdog.py`)이 첫 하트비트
- [ ] **543-3 (관측 예정, O-p1)** 다음 거래일 `crash_fault.log`에서 `TradeInit`이 다시
- [ ] **543-4 (관측 예정, O-p2)** 다음 거래일 아침 `[SessionStateDrop]`이 재현되는가 —
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
완료
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

## 2026-09-08 (MW0601 543차 — 장전 점검)

- [ ] **543-1 (P0, 신규 / F-1)** `collection/cybos/api_connector.py:430`의 `TradeInit(0)`
      호출에 타임아웃/워치독이 없다 — 오늘 08:41:08~09:04:57(약 24분) 응답 없이 멈춰
      개장 후 약 5분간 무데이터·무매매 상태(09:00~09:03 분봉 4개 결측). 1단계로 소요시간
      섀도 로깅 추가 → 사용자 승인 후 `config/settings.py:CYBOS_TRADE_INIT_TIMEOUT_SEC`
      타임아웃 예외 승격. 상세: `DECISION_LOG.md` 2026-09-08(543차).
- [ ] **543-2 (P2, 고도화 제안)** FZ-1 워치독(`utils/freeze_watchdog.py`)이 첫 하트비트
      이전(기동/로그인 단계) 동결을 원천적으로 감지 못하는 사각지대 확인 — 26주 재검증
      또는 전환기준 ②에 "기동 단계 동결" 시나리오 추가 검토(주간회의 안건).
- [ ] **543-3 (관측 예정, O-p1)** 다음 거래일 `crash_fault.log`에서 `TradeInit`이 다시
      30초 이상 스택 최상단에 반복 출현하는가 — 반복되면 436차형 원인 가설 강화.
- [ ] **543-4 (관측 예정, O-p2)** 다음 거래일 아침 `[SessionStateDrop]`이 재현되는가 —
      재현되면 538-4(F-1 본체 적용) 승인 근거로 사용.
- [x] **538-5 판정 완료** 09-08 기동 로그에 `[SessionRollover]`(09:04:59) 확인, 새로
      초기화된 키에 `p8_last_success_date`·`eod_retrain_ok_date` 포함 → **F-1 가설 확정**.
      538-4(F-1 본체 적용)로 승계.

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

### `data/heartbeat_MW0601_20260908.json` — 243B · 09-08 12:26:36
```json
{
 "pid": 23044,
 "written_at": "2026-09-08T12:27:36",
 "beat_epoch": 1788838053.9254625,
 "beat_age_sec": 2.3,
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

- 파일 최종 기록: **09-08 11:51:02**

| 키 | 값 | 수집 대상일(2026-09-08)과 일치 |
|---|---|---|
| `date` | 2026-09-08 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 117개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260908-점검리포트.md` | 17.6KB | 09-08 09:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_pre.md` | 43.0KB | 09-08 09:02 |
| `docs/정기점검/매일점검/MW0601-20260907-점검리포트.md` | 95.0KB | 09-07 17:42 |
| `docs/정기점검/매일점검/MW0601-20260907-BLAS즉사-딥다이브.md` | 13.2KB | 09-07 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_post.md` | 91.6KB | 09-07 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_intra.md` | 77.5KB | 09-07 12:27 |
| `docs/정기점검/매일점검/MW0601-20260907-맥점계측-딥다이브.md` | 10.1KB | 09-07 09:14 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_pre.md` | 54.6KB | 09-07 09:01 |

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

1. `logs/20260908_WARN.log`: ERROR 이상 18건
2. `logs/20260908_WARN.log`: **Traceback** 출현 3건 — 크래시/메모리 계열
3. `logs/20260908_SYSTEM.log`: 매분 루프 커버리지 205/371분 (55.3%) — 루프가 빠진 구간이 있다
4. `logs/20260908_SYSTEM.log`: 09:00~09:03 **연속 4분 매분 루프 기록 없음**
5. `logs/20260908_SYSTEM.log`: 12:29~15:10 **연속 162분 매분 루프 기록 없음**
6. `logs/20260908_HEALTH.log`: ERROR 이상 11건
7. 메인 스레드 정지 5초 초과 **4건** (최대 9562ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
8. `logs/20260908_WARN.log`: **level=CRITICAL** 1건(표본)
9. `logs/20260908_WARN.log`: **ConstOut** 3건(표본)
10. `logs/20260908_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260908_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260908_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260908_LEARNING.log`: **축퇴** 8건(표본)
14. `logs/20260908_HEALTH.log`: **level=CRITICAL** 1건(표본)
15. 미커밋 변경 551건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260908*.log` (Windows) / `grep 강제청산 logs/*20260908*.log`*