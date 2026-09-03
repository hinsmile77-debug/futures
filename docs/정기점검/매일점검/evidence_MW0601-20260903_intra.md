# 미륵이 증거 다이제스트 — 2026-09-03 / INTRA

- 생성 2026-09-03 12:26:27 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/loving-jolly-wright/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260903` · `2026-09-03` · `260903` · `0903`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260903.log` | 125B | 09-03 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260903.log` | 140B | 09-03 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260903.json` | 244B | 09-03 12:26 |
| `launcher_{DATE}_084001_27535.log` | 1 | `logs/Mireuk_batch/launcher_20260903_084001_27535.log` | 977.7KB | 09-03 12:26 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260903.log` | 7.4KB | 09-03 11:34 |
| `strategy_report_20260508_18{DATE}.txt` | 1 | `data/daily_reports/strategy_report_20260508_180903.txt` | 708B | 05-08 18:09 |
| `{DATE}_DATA.log` | 1 | `logs/20260903_DATA.log` | 182.2KB | 09-03 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260903_DEBUG.log` | 137.8KB | 09-03 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260903_HEALTH.log` | 2.0KB | 09-03 12:10 |
| `{DATE}_HOGA.log` | 1 | `logs/20260903_HOGA.log` | 27.5MB | 09-03 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260903_LEARNING.log` | 182.3KB | 09-03 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260903_MICRO.log` | 557.5KB | 09-03 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260903_PROBE.log` | 57.4KB | 09-03 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260903_SIGNAL.log` | 293.5KB | 09-03 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260903_SYSTEM.log` | 499.0KB | 09-03 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260903_TRADE.log` | 20.4KB | 09-03 12:04 |
| `{DATE}_WARN.log` | 1 | `logs/20260903_WARN.log` | 86.3KB | 09-03 12:25 |

## 2. 코드·커밋 상태

- HEAD `8997136` · 브랜치 `v9-dev` · 미커밋 519건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 515건 (추적변경 517 · 미추적 2 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
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
… 외 479건
```

**당일(2026-09-03) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
8997136 [MW0601] 519차 기록: DECISION_LOG · NEXT_TODO · 리포트 제5부
d03b629 [MW0601] 519차: CB② 복원 · 메인스레드 정지 경보 · F-1 마감 잔여 자동청산 (사용자 지시)
7338611 [MW0601] 518차 후속: 장후 자동조치 — F-3(진입출처 라벨) · G-1(재기동 잔량 경보 문구) · G-4(이월손익 가시화)
a3f70ab [MW0601] 514차 후속: 장후 자동조치 — F-A(P1-3) · F-B(고도화①) · F-C(고도화②/P5-신규)
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
db48586 [MW0601] 507차 후속: 리포트 제8부에 커밋 해시 기입
2d6a1bb [MW0601] 507차 후속: 장후 자동조치 — F-7·F-8·F-11·F-12·F-14 + G-4·G-5
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
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

_본문 미열람(설정): `20260903_HOGA.log` 27.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_reports/strategy_report_20260508_180903.txt`** — 708B · 05-08 18:09:03
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-05-08 18:09
========================================================
  버전    : v1.2  (1일차)
  판정    : INSUFFICIENT
  롤링20일: 누적 +0원  Sh=0.00  MDD=0.0%
--------------------------------------------------------
  CUSUM   : CRITICAL (1618766.50)
  PSI     : 0.000 (CLEAR)
  PSI/feat: cvd=0.000  vwap_position=0.000  ofi=0.000
--------------------------------------------------------
  권고    : ⛔ 롤백 검토
  사유    : CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요.
========================================================
```

_다이제스트 대상 8/14개 (중요도순). 제외: `20260903_PROBE.log`, `launcher_20260903_084001_27535.log`, `20260903_DEBUG.log`, `mainstall_traceback_20260903.log`, `freeze_sentinel_20260903.log`, `force_flat_guard_20260903.log`_

### `logs/20260903_TRADE.log` — 20.4KB · 150행 · 최종 12:04:00

- 형식 평문 · 시각 인식 150행 · INFO=150

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-03 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-03 10:02:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,600,786) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-03 10:02:01 [INFO] TRADE: [모드필터 차단] LONG->LONG 2계약 C급 (모드=hybrid, 허용=['A', 'B'])
2026-09-03 10:03:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,600,786) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-03 11:31:19 [INFO] TRADE: [Position] 체결청산 LONG @ 1046.2 | PnL=+0.24pt (+1,739원) | 하드스톱(틱)
2026-09-03 11:31:19 [INFO] TRADE: [청산 완료] PnL=+0.24pt (+1,739원) | 포지션 합계 +1,739원 (레그 1)
2026-09-03 11:32:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 0.8→2계약]
2026-09-03 11:33:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 0.8→2계약]
2026-09-03 12:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→3계약]
```

</details>

**채널** — `TRADE`×150

**컴포넌트 상위 15** — `Chejan`×37, `Position`×29, `Sizer`×22, `주문요청`×17, `진입체크`×7, `체결진입`×7, `청산 완료`×7, `TickStop-S0C`×6, `TickTP1`×5, `모드필터 차단`×3, `체결진입보정`×3, `JointGateBlock 차단`×3, `손절1차 조기축소`×2, `ProfitGuard`×1, `TP1 부분청산`×1

### `logs/20260903_WARN.log` — 86.3KB · 355행 · 최종 12:25:04

- 형식 평문 · 시각 인식 355행 · WARNING=355

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-03 08:41:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
2026-09-03 08:41:12 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3343ms — live 중단 원인 분석용
  …
2026-09-03 12:17:21 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1756x917 candles=213 grid=0.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=16.0 axes=0.0 cross=0.0 | slow_cnt=3 total_cnt=25
2026-09-03 12:17:21 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1756x917 candles=213 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=16.0 cross=0.0 | slow_cnt=4 total_cnt=32
2026-09-03 12:17:23 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1756x917 candles=213 grid=0.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=16.0 | slow_cnt=5 total_cnt=43
2026-09-03 12:20:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4375 band=INFO since_pipe_s=0.1
2026-09-03 12:25:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3797 band=INFO since_pipe_s=0.1
```

</details>

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 101 | 08:41:06 | 12:25:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 37 | 10:03:01 | 11:31:19 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1384' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=10:03:01.118' | positio… |
| `ChejanMatch` | 37 | 10:03:01 | 11:31:19 | order_no='1384' | pending='ENTRY:LONG qty=2 filled=0 order_no=1384 reason=진입 req_at=10:03:01.118' | pending_matched=True |
| `PendingOrder` | 34 | 10:03:01 | 11:31:19 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1044.72, 'reason': '진입', 'hint_source': '', 'atr': 1.3571, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `ExitCooldown` | 14 | 10:05:27 | 11:31:19 | 하드스톱(틱) 후 2분 재진입 금지 (until 10:07:27) |
| `EntryFillFlow` | 10 | 10:03:01 | 11:30:02 | actual_side='LONG' | after='LONG 2계약 @ 1044.64' | applied_side='LONG' | before='LONG 2계약 @ 1044.72' | fill_no='' | fill_price=1044.64 | fill_qty=1 | order_no='1384' | pending='ENTRY:LONG qty=2 filled=1 order_no=1384 reason=진입 req_at=10:03:… |
| `ScalerRefresh` | 9 | 09:10:00 | 12:12:00 | 5분 누적 수익률 -0.362% (임계 ±0.251%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ExitSendOrderResult` | 8 | 10:03:20 | 11:31:18 | ret=0 kind=손절1차 direction=LONG qty=1 |
| `Health` | 7 | 09:00:01 | 12:09:03 | level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0 |
| `EntryAttempt` | 7 | 10:03:01 | 11:30:01 | atr=1.3571 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='LONG' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='A' | pending='NONE' | … |
| `EntrySendOrderResult` | 7 | 10:03:01 | 11:30:01 | code='A0569' | direction='LONG' | pending='ENTRY:LONG qty=2 filled=0 order_no=1384 reason=진입 req_at=10:03:01.118' | position='FLAT' | quantity=2 | raw_direction='LONG' | ret=0 | reverse_entry_enabled=False |
| `FixB` | 7 | 10:03:01 | 11:30:01 | 낙관적 오픈 완료 direction=LONG status=LONG qty=2 optimistic=True |

**채널** — `SYSTEM`×348, `HEALTH`×7

**컴포넌트 상위 15** — `LiveDBG`×101, `ChejanFlow`×37, `ChejanMatch`×37, `PendingOrder`×34, `ExitCooldown`×14, `EntryFillFlow`×10, `ScalerRefresh`×9, `ExitSendOrderResult`×8, `Health`×7, `EntryAttempt`×7, `EntrySendOrderResult`×7, `FixB`×7, `EntryPendingCreated`×7, `ExitFillFlow`×7, `ChartDBG`×7

### `logs/20260903_SYSTEM.log` — 499.0KB · 3449행 · 최종 12:26:24

- 형식 평문 · 시각 인식 3442행 · INFO=3442, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:32 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21356 | 행감지=30s all_threads=True
2026-09-03 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-03 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-03 08:40:48 [INFO] SYSTEM: 미륵이 초기화
2026-09-03 08:40:48 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-02) 종가 버퍼 로드: 384봉
  …
2026-09-03 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-690,foreign:+1968,institution:-1066}
2026-09-03 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-690,foreign:+1968,institution:-1066}
2026-09-03 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+111172 nonarb=-355733
2026-09-03 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+111172 nonarb=-355733
2026-09-03 12:27:11 [INFO] SYSTEM: [CybosRT-TICK] #72000 code=A0569 raw_time=122711 parsed=12:27:11 price=1048.82 vol=1 bid1=1048.78 ask1=1048.84 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3442

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×725, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `BalanceUI`×76, `CybosEvent`×74, `System`×59, `BalanceRefresh`×56, `CybosDailyPnl`×52, `MicroRegime`×45, `RegimeFingerprint`×38

### `logs/20260903_SIGNAL.log` — 293.5KB · 2611행 · 최종 12:26:00

- 형식 평문 · 시각 인식 2611행 · WARNING=941, INFO=1670

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.418
  …
2026-09-03 12:27:00 [INFO] SIGNAL: 앙상블: dir=+1 conf=31.4% grade=X micro=추세장
2026-09-03 12:27:00 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=3m tf=3.49 → TP1×0.5
2026-09-03 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.314<mc0.620)
2026-09-03 12:27:00 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=37.7% size_mult=1.00 reason=meta_skip
2026-09-03 12:27:00 [INFO] SIGNAL: [차단] ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 702 | 09:00:02 | 12:12:01 | 1m 'macro_vix' scale=0.0251 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 76 | 09:06:00 | 12:27:00 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `ScalerRefresh` | 42 | 08:45:06 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 42 | 09:00:00 | 09:30:00 | ts=08:59 horizon=1m age=1m max_z=-15.19(institution_futures_net) extreme=1 |
| `WeightCollapse` | 41 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Model` | 36 | 09:00:00 | 09:24:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ConfFloorGuard` | 2 | 09:00:00 | 11:38:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×2611

**컴포넌트 상위 15** — `ScalerFloor`×726, `SIGNAL`×416, `Ensemble`×212, `FQAdj`×205, `MetaGate`×162, `ZeroDiag`×155, `Checklist`×118, `ATR-Horizon`×100, `차단`×69, `ScalerRefresh`×65, `ToxicityGate`×47, `MicroRegime`×45, `Model`×42, `ScalerMonitor`×42, `WeightCollapse`×41

### `logs/20260903_LEARNING.log` — 182.3KB · 1709행 · 최종 12:26:00

- 형식 평문 · 시각 인식 1709행 · WARNING=144, INFO=1565

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3009 < conf_floor=0.3300 (span=0.00172 auc=0.604 out_max=0.3009, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-03 08:40:49 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3464 < conf_floor=0.3300 (n=90) → 보정 재적용
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00081 auc=0.459 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
  …
2026-09-03 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0546% buf_n=20 nonzero=20 prev_p=1047.60 cur_p=1048.50
2026-09-03 12:27:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=33.3% UP)
2026-09-03 12:27:00 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=33.3% UP)
2026-09-03 12:27:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=43.4% 예측=DN 실제=UP)
2026-09-03 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=16.7%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 144 | 08:40:49 | 11:57:00 | 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×1709

**컴포넌트 상위 15** — `LEARNING`×667, `Calibration`×279, `SGD`×207, `sigma`×195, `Bias⚠`×171, `Bias`×73, `MetaConf`×39, `OnlineLearner`×29, `ScalerWarmup`×23, `BiasReset`×14, `SHAP`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1

### `logs/20260903_HEALTH.log` — 2.0KB · 15행 · 최종 12:10:00

- 형식 평문 · 시각 인식 15행 · WARNING=7, INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0
2026-09-03 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=408ms | quality=0.86 | cache_age=107s | exceptions_10m=0
2026-09-03 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 281ms (표본 20분)
2026-09-03 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=322ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-03 09:40:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=294ms | quality=1.00 | cache_age=58s | exceptions_10m=0
  …
2026-09-03 11:35:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=394ms | quality=1.00 | cache_age=161s | exceptions_10m=5
2026-09-03 12:06:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=318ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-09-03 12:07:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=261ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-09-03 12:09:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=330ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-03 12:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=546ms | quality=1.00 | cache_age=54s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 7 | 09:00:01 | 12:09:03 | level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0 |

**채널** — `HEALTH`×15

**컴포넌트 상위 15** — `Health`×14, `HealthTrend`×1

### `logs/20260903_MICRO.log` — 557.5KB · 1493행 · 최종 12:26:19

- 형식 평문 · 시각 인식 1493행 · DEBUG=1493

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1044.78/1 ask1=1045.72/3 mp={'microprice_tick': 1045.015, 'midprice_tick': 1045.25, 'depth_bias_tick': -0.2849} mlofi_tick=None queue=None
2026-09-03 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1044.78/1 ask1=1045.70/1 mp={'microprice_tick': 1045.24, 'midprice_tick': 1045.24, 'depth_bias_tick': -0.136} mlofi_tick=-4.3167 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-03 08:45:07 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1044.78/1 ask1=1045.64/3 mp={'microprice_tick': 1044.995, 'midprice_tick': 1045.21, 'depth_bias_tick': -0.258} mlofi_tick=-5.5667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio':…
2026-09-03 08:45:07 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1044.78/1 ask1=1045.64/2 mp={'microprice_tick': 1045.0667, 'midprice_tick': 1045.21, 'depth_bias_tick': -0.1635} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-09-03 08:45:07 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1044.80/1 ask1=1045.64/2 mp={'microprice_tick': 1045.08, 'midprice_tick': 1045.22, 'depth_bias_tick': -0.2715} mlofi_tick=2.6167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-09-03 12:26:30 [DEBUG] MICRO: [MICRO-TICK] #124800 bid1=1048.56/2 ask1=1048.64/1 mp={'microprice_tick': 1048.6134, 'midprice_tick': 1048.6, 'depth_bias_tick': 0.0818} mlofi_tick=-3.6667 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-03 12:26:43 [DEBUG] MICRO: [MICRO-TICK] #124900 bid1=1048.80/3 ask1=1048.82/1 mp={'microprice_tick': 1048.815, 'midprice_tick': 1048.81, 'depth_bias_tick': 0.2645} mlofi_tick=-8.5333 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-09-03 12:26:55 [DEBUG] MICRO: [MICRO-TICK] #125000 bid1=1048.60/2 ask1=1048.68/1 mp={'microprice_tick': 1048.6534, 'midprice_tick': 1048.64, 'depth_bias_tick': 0.0912} mlofi_tick=-0.5833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_…
2026-09-03 12:27:00 [DEBUG] MICRO: [MICRO-MINUTE] #222 ts=2026-09-03 12:26:00 close=1048.50 bias=-0.000013 slope=0.205536 depth_bias=-0.0021 mlofi_norm=0.000144 mlofi_pressure=1 mlofi_slope=67.828333 queue_signal=0.0021 queue_ma=-0.0150 queue_momentum=-0.0055 depletion=0.5000 refill=0.5000 imbalanc…
2026-09-03 12:27:07 [DEBUG] MICRO: [MICRO-TICK] #125100 bid1=1048.82/1 ask1=1048.86/1 mp={'microprice_tick': 1048.84, 'midprice_tick': 1048.84, 'depth_bias_tick': -0.12} mlofi_tick=-1.7 queue={'depletion_bid': 1.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
```

</details>

**채널** — `MICRO`×1493

**컴포넌트 상위 15** — `MICRO-TICK`×1271, `MICRO-MINUTE`×222

### `logs/20260903_DATA.log` — 182.2KB · 830행 · 최종 12:26:06

- 형식 평문 · 시각 인식 830행 · INFO=830

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:58:10 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=151308 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-03 08:58:10 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-03 08:58:41 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=151309 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-03 08:58:41 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-03 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-03 12:26:06 [INFO] DATA: [CybosInvestor] fetch#207 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-09-03 12:27:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+2603 futures(fi=+1929 rt=-674 inst=-1043) call(fi=-798 rt=-593) put(fi=+515 rt=-599) bias(fi=-1.00 rt=0.01) program(arb=+105003 nonarb=-353093 total=-248090)
2026-09-03 12:27:06 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+1968 individual=-690 institution=-1066 oi=47260 call_foreign=-792 put_foreign=+508 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-03 12:27:06 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=+111172 nonarb=-355733 total=-244561 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-09-03 12:27:06 [INFO] DATA: [CybosInvestor] fetch#208 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
```

</details>

**채널** — `DATA`×830

**컴포넌트 상위 15** — `CybosInvestor`×622, `DivergencePanel`×208

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 7 |
| 진입 등록(`[Position] 진입`) — **엔진** | 7 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 7 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 7 |
| 차단(`[차단]`) | 69 |
| 사이저 호출(`[Sizer]`) | 22 |

### 포지션 7건 · 승 3 (43%) · 합계 -1.26pt (-165,617원)  ※ 레그 10행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:03:01 | 엔진 | LONG | 2 | 3m | 2 | -0.54 | -47,496 | 하드스톱(틱) |
| 10:24:00 | 엔진 | LONG | 2 | 3m | 2 | -2.96 | -168,566 | 하드스톱(틱) |
| 10:33:00 | 엔진 | LONG | 2 | 3m | 2 | +3.62 | +160,424 | TP2(전량) |
| 11:02:00 | 엔진 | SHORT | 1 | 3m | 1 | -2.08 | -114,209 | 하드스톱(틱) |
| 11:18:00 | 엔진 | LONG | 1 | 3m | 1 | +0.18 | -1,260 | 하드스톱(틱) |
| 11:25:01 | 엔진 | LONG | 1 | 1m | 1 | +0.28 | +3,751 | 하드스톱(틱) |
| 11:30:01 | 엔진 | LONG | 1 | 1m | 1 | +0.24 | +1,739 | 하드스톱(틱) |

**청산 레그 10행** (부분청산 3 · 전량청산 7)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:03:20 | 부분 | 1 | -0.81 | -50,748 | 손절1차 조기축소 |
| 10:05:27 | 전량 | 1 | +0.27 | +3,252 | 하드스톱(틱) |
| 10:24:10 | 부분 | 1 | -0.93 | -56,783 | 손절1차 조기축소 |
| 10:25:09 | 전량 | 1 | -2.03 | -111,783 | 하드스톱(틱) |
| 10:33:16 | 부분 | 1 | +0.93 | +36,212 | TP1 부분청산 33% |
| 10:35:04 | 전량 | 1 | +2.69 | +124,212 | TP2(전량) |
| 11:07:51 | 전량 | 1 | -2.08 | -114,209 | 하드스톱(틱) |
| 11:19:06 | 전량 | 1 | +0.18 | -1,260 | 하드스톱(틱) |
| 11:27:15 | 전량 | 1 | +0.28 | +3,751 | 하드스톱(틱) |
| 11:31:19 | 전량 | 1 | +0.24 | +1,739 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×6, `손절1차 조기축소`×2, `TP1 부분청산 33%`×1, `TP2(전량)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 6/7건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -165,617 = 포지션합 -165,617 → OK · `[청산 완료]` 7건 = 조립 포지션 7건 → OK

### 진입 7건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:03:01 | LONG | 2 | 1044.72 | 3m | neutral |
| 10:24:00 | LONG | 2 | 1048.3 | 3m | neutral |
| 10:33:00 | LONG | 2 | 1048.66 | 3m | neutral |
| 11:02:00 | SHORT | 1 | 1040.74 | 3m | neutral |
| 11:18:00 | LONG | 1 | 1045.64 | 3m | neutral |
| 11:25:01 | LONG | 1 | 1044.88 | 1m | neutral |
| 11:30:01 | LONG | 1 | 1046.08 | 1m | neutral |

계약수 분포 — 1계약×4, 2계약×3

등급 분포 — `A급(원시C)`×6, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×6, `chas`×2, `prev`×1, `ofi`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×14, **3계약**×8

실제 진입 계약수 — **1계약**×4, **2계약**×3

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×22

### 차단 사유 69건 · 43종

| 건수 | 사유 |
|---|---|
| 7 | 등급X — 미통과 항목: 2_confidence |
| 6 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 4 | 등급X — 미통과 항목: 3_vwap |
| 4 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 3 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 3 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi |
| 2 | 등급X — 미통과 항목: 3_vwap, 10_chase |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.75pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.7pt > ATR×5.0=7.9pt (시가=1045.56 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.8pt > ATR×5.0=7.5pt (시가=1045.56 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=7.8pt (시가=1045.56 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.6pt > ATR×5.0=8.2pt (시가=1045.56 반등위험) |
| 1 | 청산 후 쿨다운 — 86초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 128초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 63초 후 재진입 가능 |
| 1 | 게이트 강등 X — CoherenceGate+체크리스트C 동시발생 (체크리스트 등급=C, 통과 7개) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |

**체크리스트 미통과 항목 누적** — `3_vwap`×22, `4_cvd`×13, `7_prev_bar`×13, `5_ofi`×12, `2_confidence`×7, `10_chase`×2, `6_foreign`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 4건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-03 10:24:01, 현재 1…` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 17건 · 최대 8734ms · 5초 초과 3건

상위 — 8734ms, 5140ms, 5015ms, 4672ms, 4516ms, 4406ms, 4375ms, 4234ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8734ms | 1486ms | **7248ms (83%)** |
| 11:34:06 | 5015ms | 1835ms | **3180ms (63%)** |
| 11:35:04 | 5140ms | 1835ms | **3305ms (64%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260903_WARN.log`
```
--- Traceback ×2(표본)
09:00:08 2026-09-03 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260903.log
11:34:06 2026-09-03 11:34:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260903.log
--- [CB] ×3(표본)
10:03:20 2026-09-03 10:03:20 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:24:10 2026-09-03 10:24:10 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:07:51 2026-09-03 11:07:51 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
10:05:27 2026-09-03 10:05:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:07:27)
10:05:27 2026-09-03 10:05:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:07:27)
10:25:09 2026-09-03 10:25:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:28:09)
10:25:09 2026-09-03 10:25:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:28:09)
--- [SHAP] 슬로우 ×1(표본)
11:34:05 2026-09-03 11:34:05 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1658ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:09 2026-09-03 08:41:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
09:00:08 2026-09-03 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8734ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8734 band=WARN since_pipe_s=0.2
09:05:04 2026-09-03 09:05:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4203 band=INFO since_pipe_s=0.1
09:50:04 2026-09-03 09:50:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4234 band=INFO since_pipe_s=0.1
```

### `logs/20260903_SYSTEM.log`
```
--- PSI ×8(표본)
09:00:00 2026-09-03 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-09-03 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:11:00 2026-09-03 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:16:00 2026-09-03 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
--- [CB] ×1(표본)
10:25:09 2026-09-03 10:25:09 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-03 10:24:01, 현재 1회)
```

### `logs/20260903_SIGNAL.log`
```
--- ConfFloorGuard ×3(표본)
09:00:00 2026-09-03 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
09:47:00 2026-09-03 09:47:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3857 ≥ 필요 0.3800
11:38:01 2026-09-03 11:38:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3714 < 필요 0.3720 (conf_floor=0.330, min_conf=0.372, span=0.0132). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- WeightCollapse ×8(표본)
09:07:00 2026-09-03 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-03 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-03 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-03 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.7% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
--- 안전망 ×8(표본)
09:07:00 2026-09-03 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-03 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-03 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-03 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260903_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3009 < conf_floor=0.3300 (span=0.00172 auc=0.604 out_max=0.3009, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00081 auc=0.459 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3179 < conf_floor=0.3300 (span=0.00233 auc=0.559 out_max=0.3179, 기저율=0.3167 n=120) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260903_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 26 | 10:02:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=36,600,786) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |
| 12:00 | 장중 중간점 | 1 | 12:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShad… |

- 이 로그 생존구간: 08:40 ~ 12:04

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260903_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 10 | 08:41:06 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 09:00:01 [WARNING] total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 09:00:01 [WARNING] total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |
| 10:00 | 장중 초반 | 53 | 09:58:00 [WARNING] 5분 누적 수익률 -0.228% (임계 ±0.221%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1 | 12:06:01 [WARNING] level=WARNING degraded=OFF | latency=318ms | quality=1.00 | cache_age=182s | exceptions_10m=0 |

- 이 로그 생존구간: 08:41 ~ 12:25

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260903_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=21356 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 126 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 179 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 245 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 165 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260903_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:06 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 104 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0384) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 189 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0390) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 133 | 09:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 12:00 | 장중 중간점 | 107 | 11:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260902 | 15:40 | 로그 본문 |
| 20260901 | 15:40 | 로그 본문 |
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260903** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2. `[MainStall]` ALERT(≥15초) → 대시보드 「2 경보」 탭
### 3. F-1 — `daily_close()` 진입 시 잔여 포지션 자동청산
### 부수: `test_514` 토글 가드의 **범위**를 옮겼다(삭제가 아니다)
### 검증 총계
## 2026-09-03 (MW0601 520차 — 장전 점검)
### 1. CB② 복원(519차) 라이브 반영 확인 — 재기동 완료
### 2. `session_state.json`의 P8 완료 마커가 다음날 아침 사라짐 — 설계된 폴백으로 실피해 없음
### 3. 오늘 장전 관측 요약 (신규 이상점 없음 확인)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
기동이다.
  증거 다이제스트 §3 설정 불변식 표에서 `CB_CONSEC_STOP_LIMIT=3` `일치` 확인.
- **결정**: NEXT_TODO "🔴 재기동 필요" 항목을 완료 처리한다.
- **Why**: 재기동이 됐는지 여부를 수동으로 매일 추적하는 대신, 런처 로그 시각과
  최근 커밋 시각을 대조하는 것으로 자동 판정 가능함을 오늘 확인했다.
- **How to apply**: 해당 없음(관측만).
- **검증**: 설정 불변식 표 `일치` — 완료.

### 2. `session_state.json`의 P8 완료 마커가 다음날 아침 사라짐 — 설계된 폴백으로 실피해 없음

- **증상**: 어제(09-02) EOD 재학습 후 P8 스케일러 재적합이 15:48:54에 성공했고
  `retrain_eod.py`가 `session_state.json`에 `p8_last_success_date`·`eod_retrain_ok_date`를
  기록 완료했다는 로그(`logs/retrain_eod_20260902.log:142`)가 있다. 그런데 오늘(09-03)
  08:46 시점 `data/session_state.json`에는 두 키가 모두 없다
  (`{"date": "2026-09-03", "count": 1, "reverse_entry_enabled": false,
  "tp1_single_contract_mode": "atr_profit", "auto_shutdown_done_date": "", "today_open": 1045.56}`).
- **원인**: 미확정. `main.py`의 모든 `_write_session_state()` 호출부(3382, 3395, 4757,
  4968, 12031, 13030)는 read-modify-write 병합 패턴이라 단일 호출로 다른 키를 지우지
  않는다 — 여러 기동 시점 쓰기(BrokerSync 08:41:06 / PreMarket GapOffset 08:45:06 등)의
  경합(lost update) 가능성이 있으나 오늘 조사로는 특정하지 못했다.
- **결정**: P0/P1 아님 — `main.py:5525` 부근 `[PreRetrain]` 로직이 session_state가
  비어있으면 `eod_retrain_done_{date}.txt` 마커 파일을 직접 읽는 폴백으로 자동
  대체하도록 이미 설계돼 있고(계측 4원칙 ④ 폴백 가시화 요건 충족 — 로그에
  "session_state 미기록 보완" 문구로 폴백 사용 사실이 남는다), 오늘도 정상 작동해
  08:55 사전 재학습이 올바르게 스킵됐다(`logs/20260903_SYSTEM.log:151-152`).
  이 폴백 자체는 신규 발견이 아니다 — 기존 기록에 "설계된 폴백"으로 이미 등재돼 있다.
- **Why**: `retrain_eod.py:180` 주석이 이 구조("daily_close()는 EOD 완료 전 체크라
  마커가 없어 eod_retrain_ok_date를 기록 못함 → PreRetrain이 매일 fallback에 의존")를
  이미 설계 의도로 명시하고 있다. 다만 그 문구는 daily_close()가 못 쓰는 이유를
  설명할 뿐, 15:48:54에 성공적으로 쓰인 값이 다음날 아침 왜 사라지는지는 설명하지
  않는다 — 이 부분이 신규로 확인이 필요한 질문이다.
- **How to apply**: F-1(리포트 §2)로 등록 — 다음 며칠 아침 08:45~08:50 시점
  `session_state.json` 스냅샷을 비교해 매일 재발하는지 확인. 재발하면 각
  `_write_session_state()` 호출 시각·내용을 임시 디버그 로그로 추적해 어느 호출이
  키를 지우는지 특정한다.
- **검증**: 표본 1일(2026-09-03 아침)뿐 — 313차 원칙에 따라 확정 결론 보류.
  내일(09-04) 장전 점검에서 재확인 예정(리포트 §6 O-1 참조).

### 3. 오늘 장전 관측 요약 (신규 이상점 없음 확인)

- CybosProbe 기동 실패 10건(08:58) — 기존 등록 P2(F-3, 0819 이후 "종결 사안, 재상정
  금지"), 매일 동일 패턴, 재보고 안 함(함정 ① 회피).
- `joblib=1.1.0` vs CLAUDE.md `1.1.1` — 491차 기존 발견, 재보고 안 함.
- 메인 스레드 정지 8,734ms(09:00:08, 개장 버스트) — 최근치(0821 11,016 / 0824 20,985 /
  0825 21,781ms)보다 낮음, 15초 미만이라 519차 신규 ALERT 미발화, 정상 범위.
- `[ConfFloorGuard]` 09:00:00 1건 — 기존 반복 패턴(O-p1로 등록, 장중 판정 예정).
- 설정 불변식 28행 전부 `일치`. 브랜치 `v9-dev` 정상. `.git/index.lock` 없음.
  당일 동시 세션 없음(오늘 첫 세션).

**세션 헤더**: MW0601 520차. 리포트: `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 이월 (미해결, 517·518차에서 승계)
### 사용자 몫
## 2026-09-03 (MW0601 520차 — 장전 점검)
### 완료 처리
### 신규 등록
### 관측 예정
### 이월 (09-02 519차 장후에서 승계, 미해결)
### 사용자 몫 (자동조치가 할 수 없음, 09-02에서 이월)
```

미완료 체크박스 **2349건** (끝에서 30건)
```
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 오늘 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
- [ ] **미륵이 재기동** — 셋 다 `config/settings.py`·`main.py`·`dashboard/` 변경이라
- [ ] **CB② 발동 1회 관측** — 🔴 **실전 전환 기준 ⑤의 남은 조건.** 값 복원만으로는
- [ ] **CB② 부작용 관측** — 발동 시 그날 신규 진입이 전부 사라진다. 장후 점검에서
- [ ] **정지 경보 실물 확인** — 다음 ALERT(≥15초) 발생 시 「2 경보」 탭에 뜨는지.
- [ ] **F-1 왕복 확인** — 마감 시각에 잔량이 있는 날 `[DailyCloseForceExit]` 로그로
- [ ] **F-1 마감 지연 관측** — 청산이 붙은 날 마감 소요시간이 12초 이상 늘지 않는지,
- [ ] **`FORCE_FLAT_GUARD_ORDER_ENABLED`(현재 False·미구현) 승격 논의는 F-1과 한 묶음.**
- [ ] **`MAIN_THREAD_STALL_ALERT_MS`(15초) 재보정** — 26주 WFA 항목(482차 F-3 섀도
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔(F-3은 미래만 고침)
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **G-2 잔여** 정지 경보의 **임계 근거** — 이번엔 화면 노출만 했고 임계는 무변경
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
- [ ] **F-1** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`가
- [ ] **G-1** `collect_evidence.py` §9에 `session_state.json`의 `p8_last_success_date`·
- [ ] **O-p1** `[ConfFloorGuard]` 09:00:00 발동 — 오전 중 자연 복귀 여부를 장중에 확인
- [ ] **CB② 발동 1회 관측** — 실전 전환 기준 ⑤의 남은 조건. 인위적으로 만들지 말 것
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
족되지 않는다(게이트가 `UNMEASURED` 반환). 5분 내 서로 다른 3포지션 손절이
      나면 당일 정지가 걸린다. ⚠ **인위적으로 만들지 말 것** — 관측될 때까지 열어둔다
- [ ] **CB② 부작용 관측** — 발동 시 그날 신규 진입이 전부 사라진다. 장후 점검에서
      ⓐ 발동 로그 ⓑ min_samples 미달 채널 적립 속도 를 함께 볼 것.
      적립이 눈에 띄게 느려지면 2~3 사이 재조정 또는 재유예를 주간회의에 상정
- [ ] **정지 경보 실물 확인** — 다음 ALERT(≥15초) 발생 시 「2 경보」 탭에 뜨는지.
      ⚠ ALERT는 5거래일에 1건꼴이라 **며칠 안 뜨는 것이 정상**이다
- [ ] **F-1 왕복 확인** — 마감 시각에 잔량이 있는 날 `[DailyCloseForceExit]` 로그로
      청산 완료까지 확인. ⚠ 잔량 없는 날은 **조용한 것이 정상**
- [ ] **F-1 마감 지연 관측** — 청산이 붙은 날 마감 소요시간이 12초 이상 늘지 않는지,
      `[MainStall]` ALERT가 마감 때문에 발화하지 않는지

### 함께 재검토해야 하는 것 (묶여 있음)

- [ ] **`FORCE_FLAT_GUARD_ORDER_ENABLED`(현재 False·미구현) 승격 논의는 F-1과 한 묶음.**
      둘 다 켜면 15:39 외부 가드와 15:40 마감이 **같은 잔량에 두 번 주문**한다.
      `tests/test_519_*.py:test_f1_no_double_exit_with_external_guard` 가 고정 중
- [ ] **`MAIN_THREAD_STALL_ALERT_MS`(15초) 재보정** — 26주 WFA 항목(482차 F-3 섀도
      관찰 종료와 함께). WARN(5~15초) 승격 여부도 그때 판단(현재 일부러 제외)

### 이월 (미해결, 517·518차에서 승계)

- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔(F-3은 미래만 고침)
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **G-2 잔여** 정지 경보의 **임계 근거** — 이번엔 화면 노출만 했고 임계는 무변경

### 사용자 몫

- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인

## 2026-09-03 (MW0601 520차 — 장전 점검)

### 완료 처리

- [x] **미륵이 재기동**(519차 CB②·정지경보·F-1 반영) — 오늘 08:40:01 기동(PID 21356,
      커밋 `8997136` 이후 첫 기동) 확인. 설정 불변식 `CB_CONSEC_STOP_LIMIT=3` `일치` 확인됨

### 신규 등록

- [ ] **F-1** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`가
      다음날 아침 사라지는 경로 규명 — 어제 15:48:54 정상 기록 확인(`retrain_eod_20260902.log:142`)
      됐으나 오늘 08:46 파일에 없음. 폴백(마커 파일 직접확인)이 정상 작동해 실피해는 없었음.
      표본 1일, 내일(09-04) 장전에 재확인 필요
- [ ] **G-1** `collect_evidence.py` §9에 `session_state.json`의 `p8_last_success_date`·
      `eod_retrain_ok_date`·`date` 3키 자동 게재 — 수동 발견 대신 매일 자동 추적

### 관측 예정

- [ ] **O-p1** `[ConfFloorGuard]` 09:00:00 발동 — 오전 중 자연 복귀 여부를 장중에 확인
      (기존 반복 패턴과 일치하는지)

### 이월 (09-02 519차 장후에서 승계, 미해결)

- [ ] **CB② 발동 1회 관측** — 실전 전환 기준 ⑤의 남은 조건. 인위적으로 만들지 말 것
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건

### 사용자 몫 (자동조치가 할 수 없음, 09-02에서 이월)

- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인

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

### `data/heartbeat_MW0601_20260903.json` — 244B · 09-03 12:26:13
```json
{
 "pid": 21356,
 "written_at": "2026-09-03T12:27:13",
 "beat_epoch": 1788406031.142797,
 "beat_age_sec": 2.1,
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

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 96개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md` | 14.9KB | 09-03 09:05 |
| `docs/정기점검/매일점검/evidence_MW0601-20260903_pre.md` | 54.0KB | 09-03 09:00 |
| `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` | 114.3KB | 09-02 19:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_post.md` | 78.0KB | 09-02 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_intra.md` | 66.8KB | 09-02 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_pre.md` | 58.1KB | 09-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-01 18:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_post.md` | 89.7KB | 09-01 16:18 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260828.md` | 4.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260828.md` | 28.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260828.json` | 35.2KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260828.md` | 178.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260828.json` | 97.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260903_WARN.log`: **Traceback** 출현 2건 — 크래시/메모리 계열
2. `logs/20260903_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
3. `logs/20260903_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. 메인 스레드 정지 5초 초과 **3건** (최대 8734ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260903_SIGNAL.log`: **WeightCollapse** 8건(표본)
7. `logs/20260903_LEARNING.log`: **축퇴** 8건(표본)
8. 미커밋 변경 519건 (실질 2건 · 코드 0건 · EOL 파생 515건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260903*.log` (Windows) / `grep 강제청산 logs/*20260903*.log`*