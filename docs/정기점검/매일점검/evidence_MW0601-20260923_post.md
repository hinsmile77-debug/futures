# 미륵이 증거 다이제스트 — 2026-09-23 / POST

- 생성 2026-09-23 16:21:01 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/sweet-wonderful-tesla/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260923` · `2026-09-23` · `260923` · `0923`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **35개** 파일 · 35개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260923.txt` | 28B | 09-23 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260923.txt` | 28B | 09-23 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260923.txt` | 233B | 09-23 15:53 |
| `force_flat_alert_{DATE}.txt` | 1 | `data/force_flat_alert_20260923.txt` | 489B | 09-23 15:22 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260923.log` | 2.2KB | 09-23 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260923.log` | 433B | 09-23 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260923.json` | 245B | 09-23 15:46 |
| `launcher_{DATE}_084001_1592.log` | 1 | `logs/Mireuk_batch/launcher_20260923_084001_1592.log` | 5.5MB | 09-23 15:19 |
| `launcher_{DATE}_152208_14848.log` | 1 | `logs/Mireuk_batch/launcher_20260923_152208_14848.log` | 85.3KB | 09-23 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260923.log` | 19.1KB | 09-23 13:44 |
| `position_state.json.gen_{DATE}_103601` | 1 | `data/position_state.json.gen_20260923_103601` | 1.5KB | 09-23 10:36 |
| `position_state.json.gen_{DATE}_103613` | 1 | `data/position_state.json.gen_20260923_103613` | 1.5KB | 09-23 10:36 |
| `position_state.json.gen_{DATE}_103930` | 1 | `data/position_state.json.gen_20260923_103930` | 1.5KB | 09-23 10:36 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260923.log` | 38.7KB | 09-23 16:15 |
| `retrain_intraday_{DATE}_104702.log` | 1 | `logs/retrain_intraday_20260923_104702.log` | 5.7KB | 09-23 10:47 |
| `retrain_intraday_{DATE}_115350.log` | 1 | `logs/retrain_intraday_20260923_115350.log` | 5.7KB | 09-23 11:54 |
| `retrain_intraday_{DATE}_134243.log` | 1 | `logs/retrain_intraday_20260923_134243.log` | 5.7KB | 09-23 13:43 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260923.txt` | 43B | 09-23 15:47 |
| `strategy_report_{DATE}_154023.txt` | 1 | `data/daily_reports/strategy_report_20260923_154023.txt` | 2.4KB | 09-23 15:40 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-09-23.jsonl` | 3.0KB | 09-23 16:19 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260923_BACKFILL.log` | 0B | 09-23 14:50 |
| `{DATE}_DATA.log` | 1 | `logs/20260923_DATA.log` | 422.3KB | 09-23 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260923_DEBUG.log` | 220.6KB | 09-23 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260923_HEALTH.log` | 6.0KB | 09-23 14:58 |
| `{DATE}_HOGA.log` | 1 | `logs/20260923_HOGA.log` | 48.4MB | 09-23 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260923_LEARNING.log` | 861.3KB | 09-23 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260923_MICRO.log` | 987.5KB | 09-23 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260923_PROBE.log` | 248.0KB | 09-23 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260923_REGULAR_COLLECT.log` | 6.6KB | 09-23 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260923_SIGNAL.log` | 574.4KB | 09-23 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260923_SYSTEM.log` | 929.6KB | 09-23 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20260923_TRADE.log` | 9.2KB | 09-23 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260923_WARN.log` | 3.8MB | 09-23 15:46 |
| `{DATE}_lv.txt` | 1 | `data/peter_feed/2026-09-23_lv.txt` | 748B | 09-23 16:20 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-09-23_tr.txt` | 70B | 09-23 16:20 |

## 2. 코드·커밋 상태

- HEAD `645032e` · 브랜치 `v9-dev` · 미커밋 757건 · 실질 변경 13건 · 코드(.py) 3건 · EOL 파생 612건 (추적변경 625 · 미추적 132 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260828.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260828.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260828.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260828.md`, `docs/정기점검/수익률향상_누적대장.md`, `features/levels/levels_store.py`, `features/levels/premarket_levels.py` … 외 1개
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
 M COLLECT_REGULAR_EOD.bat
 M INSTALL.bat
 M LAUNCH_API.bat
 M MIREUK_DAILYCHECK_HANDOFF.md
 M P7_SHADOW_EOD.bat
 M ROADMAP.md
 M SETUP_GUIDE.md
 M TASK_CLAUDE_HIBERNATE_INSTALL.bat
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M TASK_OPTION_BACKFILL_INSTALL.bat
 M TASK_REGULAR_COLLECT_INSTALL.bat
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
… 외 717건
```

**당일(2026-09-23) 커밋**
```
645032e [MW0601] 623차 후속2: 만기북 수집 예산·다운로드 백오프 — dev 배포 검토에서 나온 공통 결함
0032862 [MW0601] 623차: 만기북 GEX·감마월 — 먼스리·목위클리·월위클리를 1분봉 차트에
a018da0 [MW0601] 622차 후속2: PumpGuard·중첩진입 로그를 INFO 로 — WARNING 은 Degraded 오발동
f159fe5 [MW0601] 622차 후속: PumpGuard 재시도 콜백도 Qt 진입점 가드(617차 원리)
c528b1a [MW0601] 621차 후속11: 래칫은 타이머만 센다 — 621차 Qt 진입점 18곳을 같은 원리로 가드
2f9b215 [MW0601] 622차: 장중 동결 — 메시지 펌프 안에서 Qt 타이머가 3중 재진입했다
4fd7129 [MW0602] 617차 래칫 복구 — 621차가 무가드 QTimer 슬롯을 새로 넣었다
029c24e [MW0601] 621차: 수급 증감 독립 창 — 그리고 1분봉 차트가 따로 놀던 이유는 그리기 횟수였다
1dbf49b [MW0601] 603차 후속4: 잔존물의 범인은 예약작업이 아니라 「지우지 못하는 git」이었다
9b63de5 [MW0601] 603차 후속3: MW0602 의 등록검증을 역이식 — 그리고 「자가진단은 선택」이 틀렸다
d9c852f [MW0601] Claude 세션 야간 유실 차단 - 최대절전 전환 + 인앱 업데이터 소화 창
```

**최근 커밋 12건**
```
645032e [MW0601] 623차 후속2: 만기북 수집 예산·다운로드 백오프 — dev 배포 검토에서 나온 공통 결함
0032862 [MW0601] 623차: 만기북 GEX·감마월 — 먼스리·목위클리·월위클리를 1분봉 차트에
a018da0 [MW0601] 622차 후속2: PumpGuard·중첩진입 로그를 INFO 로 — WARNING 은 Degraded 오발동
f159fe5 [MW0601] 622차 후속: PumpGuard 재시도 콜백도 Qt 진입점 가드(617차 원리)
c528b1a [MW0601] 621차 후속11: 래칫은 타이머만 센다 — 621차 Qt 진입점 18곳을 같은 원리로 가드
2f9b215 [MW0601] 622차: 장중 동결 — 메시지 펌프 안에서 Qt 타이머가 3중 재진입했다
4fd7129 [MW0602] 617차 래칫 복구 — 621차가 무가드 QTimer 슬롯을 새로 넣었다
029c24e [MW0601] 621차: 수급 증감 독립 창 — 그리고 1분봉 차트가 따로 놀던 이유는 그리기 횟수였다
1dbf49b [MW0601] 603차 후속4: 잔존물의 범인은 예약작업이 아니라 「지우지 못하는 git」이었다
9b63de5 [MW0601] 603차 후속3: MW0602 의 등록검증을 역이식 — 그리고 「자가진단은 선택」이 틀렸다
d9c852f [MW0601] Claude 세션 야간 유실 차단 - 최대절전 전환 + 인앱 업데이터 소화 창
421c2ce [MW0601] 620차 후속: 장후 자동조치 기록 — F-3 종결 · 오늘치 리포트·증거 커밋
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

### 차단 게이트 전수 인벤토리 — 36개 중 **9개 꺼짐**

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
| `OPTION_BOOK_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260923_HOGA.log` 48.4MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260923.txt`** — 28B · 09-23 15:40:23
```
2026-09-23T15:40:23.063958
```

**`data/daily_close_started_20260923.txt`** — 28B · 09-23 15:40:20
```
2026-09-23T15:40:20.942729
```

**`data/daily_reports/strategy_report_20260923_154023.txt`** — 2.4KB · 09-23 15:40:23
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-23 15:40
========================================================
  버전    : v1.0  (86일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-2.05  MDD(자본대비)=29.9%
  당일      : WR=100.0%  PF=1.55
  롤링20일: 누적 -6646666원  Sh=-2.05  MDD(자본대비)=29.9%  MDD(peak대비)=1497.9%
  당일손익 : broker(gross) +28,000원  수수료 21,956원  net +6,044원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)
  PSI/feat: 미측정
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +354,770원  승률 65.0%  합계 +7,095,402원
  등급별 순EV(30일): A=+106,780원(60건,승63%)  BROKER=-2,574,591원(4건,승50%)  C=+24,396원(1건,승100%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=+1,934원(11건)  3m=-6,894원(41건)  5m=-32,721원(7건)  ?=-37,188원(172건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 42분  5일평균 24분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 24.2pt(5일평균 21.0pt)  1분평균변동 0.52pt(5일평균 0.56pt)
--------------------------------------------------------
  진입 퍼널(2026-09-23, 총 355분):
    FLAT 249 → conf미달 55 → CoherenceGate 10 → 게이트차단 38 → 후보 3 → 진입 1
    게이트별: 시가갭(OPEN_VOLATILE)=10  콜드스타트/기타(조건부구간)=7  ATR변동성=7  콜드스타트/기타(σ미수집)=6  쿨다운=3  포지션보유중(평가생략)=2  모드필터=2  콜드스타트/기타(DataAnomalyGate)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 2건
      └ 상세: Degraded신뢰도=1  Hurst미계산(워밍업)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260923.txt`** — 233B · 09-23 15:53:32
```
completed: 2026-09-23 15:53:32
rows: 16955
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 22.5
t_retrain_s: 185.6
t_total_s: 208.6
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/force_flat_alert_20260923.txt`** — 489B · 09-23 15:22:24
```
[ForceFlatGuard] 2026-09-23 15:22:24 WARNING
  라이브 프로세스 정지(포지션은 FLAT) — 오늘 실손해는 없으나 15:40 일일마감·EOD 체인이 실행되지 않는다
  · 하트비트: 파일 209s 전 기록 · 이벤트루프 나이 3s · pid=9972 · strikes=0
  · → 임계 180s 초과 — 라이브 프로세스가 멈춘 것으로 본다
  · 포지션: status=FLAT qty=0 · 최종갱신=2026-09-23T10:39:30.335077 (apply_exit_fill_final:하드스톱(틱))
```

**`data/peter_feed/2026-09-23_lv.txt`** — 748B · 09-23 16:20:20
```
1130 밑으로 떨어지면 확인하고 매수 들어갈 예정이니 대기
9:07 AM · Sep 23, 2026

매수잖아
9:15 AM · Sep 23, 2026

1130 돌파시 매수.  손절가 1125
9:37 AM · Sep 23, 2026

1130 매수체결
9:38 AM · Sep 23, 2026

1125 손절
10:33 AM · Sep 23, 2026

1120 돌파시 매수로 변경. 손절가 1117
12:24 PM · Sep 23, 2026

1120 매수체결.
12:25 PM · Sep 23, 2026

피터리 - 2026년 9월 23일 증권사 산업분석 리포트 브리핑 - 축약본
2:25 PM · Sep 23, 2026

1125 청산가로 변경
3:11 PM · Sep 23, 2026

1125 청산체결 5p 수익 - 5p 손실 = 0 오늘 진빠지는 날이네요. 그래도 최대한 선방했습니다. 무패로도 만족하는 날입니다.
3:15 PM · Sep 23, 2026
```

**`data/peter_feed/2026-09-23_tr.txt`** — 70B · 09-23 16:20:09
```
09:38 L 1130 / 10:33 X 1125 손절
12:25 L 1120 / 15:15 X 1125 익절
```

**`data/shutdown_normal_20260923.txt`** — 43B · 09-23 15:47:15
```
auto_shutdown
2026-09-23T15:47:15.119523
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260923_115350.log`, `retrain_intraday_20260923_134243.log`, `20260923_MICRO.log`, `20260923_DATA.log`, `20260923_PROBE.log`, `launcher_20260923_084001_1592.log`, `launcher_20260923_152208_14848.log`, `20260923_DEBUG.log`_

### `logs/20260923_TRADE.log` — 9.2KB · 64행 · 최종 15:40:22

- 형식 평문 · 시각 인식 64행 · INFO=64

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:41:03 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-23 08:41:08 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 09:44:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-23 09:49:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-23 09:55:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-23 13:42:36 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 13:52:51 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 14:19:48 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 15:22:47 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-23 15:40:22 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×64

**컴포넌트 상위 15** — `Sizer`×24, `ProfitGuard`×13, `Chejan`×7, `Position`×5, `주문요청`×3, `모드필터 차단`×2, `자동진입 차단`×1, `진입체크`×1, `체결진입`×1, `체결진입보정`×1, `TickTP1`×1, `TP1 부분청산`×1, `TickStop-S0C`×1, `청산 완료`×1, `MarginCap`×1

### `logs/20260923_WARN.log` — 3.8MB · 18381행 · 최종 15:46:21

- 형식 평문 · 시각 인식 18374행 · CRITICAL=1, WARNING=18373, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-23 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2500 band=INFO since_pipe_s=NA
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 2422ms account=333044256
2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _ts_sync_position_from_broker BlockRequest 2419ms — 메인 스레드 2419ms 점유
  …
2026-09-23 15:46:21 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-23 09:56:00 cols=['open'] existing_source=rt
2026-09-23 15:46:21 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-23 09:57:00 cols=['open'] existing_source=rt
2026-09-23 15:46:21 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=392 inserted=19 open_fixed=1 mismatch=30
2026-09-23 15:46:21 [WARNING] SYSTEM: [BarGap] 당일 확정(2026-09-23) — raw_candles 369봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 15봉 (10:45, 10:46, 11:29, 11:52, 12:09, 12:22, 12:30, 12:36, 12:37, 13:38, 13:39, 13:40 … 외 3개) — 전부 session_bars 에 보존됨, 백필 안 함(533차)
2026-09-23 15:46:21 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 92.4ms | size=2097x1154 candles=396 grid=21.1 spans=8.6 candles=15.1 dir=1.1 regime=5.3 markers=39.0 axes=0.6 cross=0.0 | slow_cnt=93 total_cnt=93 overlay_cnt=784
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 11:55:05 | 11:55:05 | level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 38종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 17788 | 09:00:49 | 15:46:21 | paintEvent slow 94.0ms | size=1799x832 candles=16 grid=31.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=0.0 axes=32.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 319 | 08:41:12 | 15:34:51 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 58 | 10:47:12 | 15:45:48 | 그리기 88.2ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `출처축` | 24 | 08:41:14 | 15:22:50 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `PipePerf` | 18 | 09:00:02 | 14:45:02 | total=1967ms | S0=5ms S1=39ms S2=0ms S3=0ms S4=186ms S5=629ms S6=1017ms S7=77ms S8=13ms |
| `Health` | 18 | 09:00:02 | 14:57:00 | level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0 |
| `CB⑤` | 16 | 09:00:02 | 14:45:02 | 파이프라인 1967ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 16 | 09:08:00 | 14:48:00 | 5분 누적 수익률 -0.274% (임계 ±0.255%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SessionBackfill` | 12 | 08:41:44 | 15:46:21 | OHLCV 불일치 ts=2026-09-22 09:30:00 cols=['open'] existing_source=rt |
| `BarGap` | 12 | 10:46:30 | 15:46:21 | 기동 시점 결손 1봉 / 검사창 08:45~10:45 (분그리드 기준) — 10:45 | session_bars 보존 여부는 15:46 확정 판정에서 |
| `OptionChain` | 11 | 10:47:02 | 15:22:50 | 현물지수 미수신 — 선물 종가(0.00)로 ATM 기준가 폴백. 베이시스만큼 ATM 행사가가 어긋날 수 있다(612차) |
| `RESTART` | 11 | 10:47:02 | 15:22:50 | 장중 재시작 감지 10:47 — GapOffset=복원됨  pre_market_scaler=False |

**채널** — `SYSTEM`×18355, `HEALTH`×19

**컴포넌트 상위 15** — `ChartDBG`×17788, `LiveDBG`×319, `OptionFlowChart`×58, `출처축`×24, `Health`×19, `PipePerf`×18, `CB⑤`×16, `ScalerRefresh`×16, `SessionBackfill`×12, `BarGap`×12, `OptionChain`×11, `RESTART`×11, `LEVELS`×10, `HealthPolicy`×8, `ChejanFlow`×7

### `logs/20260923_SYSTEM.log` — 929.6KB · 6565행 · 최종 15:47:15

- 형식 평문 · 시각 인식 6518행 · INFO=6518, PLAIN=47

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=23656 | 행감지=30s all_threads=True
2026-09-23 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-23 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-23 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-23 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-22) 종가 버퍼 로드: 381봉
  …
2026-09-23 15:46:21 [INFO] SYSTEM: [SessionBackfill] 08:45 개장 체결 보정 ts=2026-09-23 08:45:00 rt O=1133.62/V=331 → chart O=1133.10/V=571
2026-09-23 15:46:21 [INFO] SYSTEM: [SessionBackfill] 2026-09-23~2026-09-23 chart=411 existing=392 inserted=19 open_fixed=1 mismatch=30
2026-09-23 15:47:15 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-23 15:47:15 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-23 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6518

**컴포넌트 상위 15** — `CybosInvestorRaw`×1526, `CybosRT-TICK`×1091, `TickUI`×395, `BAR-CLOSE`×392, `CVD-ANCHOR`×392, `CybosRT-ROLLOVER`×391, `S6Detail`×355, `PipePerf`×355, `CybosSub`×252, `System`×168, `OptionChain`×94, `MicroRegime`×84, `CybosRT-START`×72, `SYSTEM`×69, `RegimeFingerprint`×66

### `logs/20260923_SIGNAL.log` — 574.4KB · 5073행 · 최종 15:40:22

- 형식 평문 · 시각 인식 5073행 · WARNING=1865, INFO=3208

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.435
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.414
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.410
2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.418
  …
2026-09-23 15:22:44 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-23 15:22:50 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
2026-09-23 15:40:22 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-23 15:40:22 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-23 age=29m extreme=948 refresh=47 grade_x=0 cb3=0
2026-09-23 15:40:22 [INFO] SIGNAL: [ModelHealth] date=2026-09-23 앙상블유효가동률=미측정 | 파이프라인 0분 | ConstOut 0회/0분 | WeightCollapse 0분 | 장중재학습 0회 | CB③ ready 0분/0분 (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1218 | 09:00:02 | 14:48:00 | 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| `Model` | 252 | 09:01:00 | 15:01:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 216 | 09:01:00 | 15:02:00 | ts=09:00 horizon=1m age=1m max_z=+4.19(quality_investor_reason_code) extreme=2 adj=1 |
| `WeightCollapse` | 77 | 09:07:00 | 15:09:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 65 | 09:06:00 | 15:08:00 | 신뢰도 미달 35.6% < 39.2% → 강제 X등급 |
| `ScalerRefresh` | 18 | 08:45:14 | 08:45:14 | 1m CORE 'cvd_divergence' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| `MetaGate` | 8 | 10:55:00 | 14:33:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `ConstOut` | 6 | 10:14:00 | 15:05:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 5 | 09:10:00 | 09:44:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×5073

**컴포넌트 상위 15** — `ScalerFloor`×1260, `SIGNAL`×710, `Ensemble`×376, `MetaGate`×355, `FQAdj`×352, `Model`×342, `ZeroDiag`×328, `ScalerMonitor`×217, `Checklist`×146, `DynMC`×91, `ATR-Horizon`×89, `MicroRegime`×84, `WeightCollapse`×77, `차단`×77, `InstabilityGate`×75

### `logs/20260923_LEARNING.log` — 861.3KB · 5795행 · 최종 15:40:22

- 형식 평문 · 시각 인식 5795행 · WARNING=1824, INFO=3971

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 08:40:53 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-23 08:40:54 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00136 auc=0.573 out_max=0.1248 (n=145) → 보정 재적용
  …
2026-09-23 15:40:22 [INFO] LEARNING: [DriftAdjuster] 표본 부족(n=0 < 15) — acc=50.0% 반영 스킵, alpha=0.01000 유지
2026-09-23 15:40:22 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-23 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-23 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-23 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 689 | 08:40:54 | 15:22:43 | 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 564 | 08:40:54 | 15:22:42 | 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 173 | 08:40:54 | 15:22:43 | 축퇴 감지 — span=0.00021 auc=0.509 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:3m` | 166 | 08:40:54 | 15:22:43 | 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 116 | 08:40:55 | 15:22:41 | 축퇴 감지 — span=0.00144 auc=0.527 out_max=0.3758 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 100 | 08:40:55 | 15:22:40 | 축퇴 감지 — span=0.00049 auc=0.514 out_max=0.3353 (기준 auc<0.53 and span<0.020, 기저율=0.3350 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 14 | 08:41:03 | 15:22:43 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 2 | 11:56:01 | 14:45:01 | total=371ms raw_fetch=3ms pred_select=4ms pred_update=7ms pred_insert=1ms verified=3 |

**채널** — `LEARNING`×5795

**컴포넌트 상위 15** — `Calibration:1m`×1372, `Calibration:30m`×1120, `LEARNING`×1062, `SGD`×356, `Calibration:10m`×326, `Calibration:3m`×320, `sigma`×259, `Calibration:15m`×232, `Calibration:5m`×191, `Bias⚠`×127, `Bias`×100, `OnlineLearner`×87, `ScalerWarmup`×53, `MetaConf`×49, `Calibration:ensemble`×28

### `logs/20260923_HEALTH.log` — 6.0KB · 43행 · 최종 14:58:00

- 형식 평문 · 시각 인식 43행 · CRITICAL=1, WARNING=18, INFO=24

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0
2026-09-23 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=759ms | quality=0.86 | cache_age=97s | exceptions_10m=0
2026-09-23 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=321ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-23 09:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=342ms | quality=1.00 | cache_age=57s | exceptions_10m=0
2026-09-23 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 327ms (표본 20분)
  …
2026-09-23 14:46:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=300ms | quality=1.00 | cache_age=83s | exceptions_10m=0
2026-09-23 14:54:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=655ms | quality=1.00 | cache_age=188s | exceptions_10m=0
2026-09-23 14:55:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=293ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-09-23 14:57:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=328ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-09-23 14:58:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=413ms | quality=1.00 | cache_age=52s | exceptions_10m=0
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 11:55:05 | 11:55:05 | level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 18 | 09:00:02 | 14:57:00 | level=WARNING degraded=OFF | latency=1967ms | quality=0.86 | cache_age=38s | exceptions_10m=0 |

**채널** — `HEALTH`×43

**컴포넌트 상위 15** — `Health`×37, `HealthTrend`×6

### `logs/retrain_eod_20260923.log` — 38.7KB · 319행 · 최종 16:15:12

- 형식 평문 · 시각 인식 180행 · WARNING=26, INFO=154, PLAIN=139

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 15:50:03,141 [INFO] EOD_RETRAIN: =======================================================
2026-09-23 15:50:03,142 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-23 15:50:03,142 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-23 15:50:03,142 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-23 15:50:03,142 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
30m    성공       0.5026    30196   0.1896
2026-09-23 16:15:12,784 [INFO] EOD_RETRAIN: [검증 캠페인] 요약: 게이트 ablation 리포트=OK | 호라이즌 conf-층화 검정=OK | 검증 캠페인 판정 리포트=OK | 피처셋 건강 리포트=OK | CVD 앵커 대조 리포트=OK | 조기청산 반사실 [49]=OK | 라우팅 밴드 성과 [D9-B]=OK | 방향 처분 실험 [40-B]=OK | 섀도우 TB 재학습=OK | 분위 회귀 재학습=OK | 메타라벨 분류기 재학습=OK
2026-09-23 16:15:12,804 [INFO] EOD_RETRAIN: 판정 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\validation_campaign_report_20260923.md
2026-09-23 16:15:12,805 [INFO] EOD_RETRAIN: 피처셋 건강 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\featureset_health_report_20260923.md
2026-09-23 16:15:12,805 [INFO] EOD_RETRAIN: =======================================================
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:38 | 15:52:43 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-23 13:07:00까지)인데 acc.txt=0.4561는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:38 | 15:52:43 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1771봉(96%)이 현행 학습구간 (현행 cutoff=2026-09-23 13:07:00 ≥ 홀드아웃 시작=2026-09-16 12:13:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-23 13:07 >= holdout_start=2026-09-16 12:13 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-0… |
| `UnitMismatch` | 4 | 15:50:13 | 16:08:41 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/20540행 제외 (559차 P1'-2) — 남은 19094행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `BackfillFilter` | 2 | 15:50:13 | 16:08:43 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25051/45591 제외 (418차 결정 1) — 남은 20540행 |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-09-23 | 최신 2026-09-22 · 기준 8거래일. 복구: python scripts/collect_regular_futures.py --from 20260923 --to 20260923 |
| `RegimeFingerprint` | 1 | 15:53:32 | 15:53:32 | 백필 0행 제외 — 필터가 무효일 수 있다. 16955행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×74, `EOD_RETRAIN`×43, `SIGNAL`×31, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×138, `ScalerFloor`×24, `Retrain`×21, `EOD_RETRAIN`×18, `검증 캠페인`×13, `GuardGhost`×12, `RF`×9, `ShadowTB`×8, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6

### `logs/retrain_intraday_20260923_104702.log` — 5.7KB · 43행 · 최종 10:47:49

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-23 10:47:02,095 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_abb64ad3.json
  …
2026-09-23 10:47:49,395 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-23 10:47:49,396 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-23 10:47:49,396 [INFO] LEARNING: [Retrain] 완료 | 43.1초 | 성공=6/6 호라이즌
2026-09-23 10:47:49,397 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 47.3s 데이터=4800행
2026-09-23 10:47:49,399 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_abb64ad3.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:47:17 | 10:47:17 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25324/45615 제외 (418차 결정 1) — 남은 20291행 |
| `UnitMismatch` | 1 | 10:47:17 | 10:47:17 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/20291행 제외 (559차 P1'-2) — 남은 18845행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +6044원
════════════════════════════════════════════════════
2026-09-23 15:45:42 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 109.7ms | size=2097x1154 candles=392 grid=24.6 spans=8.4 candles=14.8 dir=1.2 regime=9.2 markers=48.6 axes=0.6 cross=0.0 | slow_cnt=92…
2026-09-23 15:45:48 [WARNING] SYSTEM: [OptionFlowChart] 그리기 60.0ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 1 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 1 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 77 |
| 사이저 호출(`[Sizer]`) | 24 |

### 포지션 1건 · 승 1 (100%) · 합계 +0.56pt (+6,044원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:36:00 | 엔진 | SHORT | 2 | 3m | 2 | +0.56 | +6,044 | 하드스톱(틱) |

**청산 레그 2행** (부분청산 1 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:36:13 | 부분 | 1 | +0.56 | +17,022 | TP1 부분청산 33% |
| 10:39:30 | 전량 | 1 | -0.00 | -10,978 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×1, `하드스톱(틱)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +6,044 = 포지션합 +6,044 → OK · `[청산 완료]` 1건 = 조립 포지션 1건 → OK

### CB③ 판정 가능 시간 — **0분 / 0분 (—)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:36:00 | SHORT | 2 | 1119.02 | 3m | neutral |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×2, **3계약**×22

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×19, `conf=0.6 regime=0.8 safe=1.00`×5

### 차단 사유 77건 · 57종

| 건수 | 사유 |
|---|---|
| 9 | 등급X — 미통과 항목: 2_confidence |
| 4 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.70pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.3pt > ATR×5.0=7.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.4pt > ATR×5.0=6.9pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.6pt > ATR×5.0=7.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.5pt > ATR×5.0=6.8pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.1pt > ATR×5.0=6.9pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.0pt > ATR×5.0=6.9pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.4pt > ATR×5.0=6.6pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=6.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.1pt > ATR×5.0=6.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.3pt > ATR×5.0=6.0pt (시가=1133.30 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.8pt > ATR×5.0=6.1pt (시가=1133.30 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×9

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 10건

- `×1 [LEVELS]×1 외 1종` ×3
- `5분 진입 정지 | 파이프라인 5214ms — 처리 지연 (임계=5000ms)` ×2
- `일시 정지 해제 — 정상 복귀` ×2
- `일간 리셋 완료` ×2
- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 67건 · 최대 7234ms · 5초 초과 5건

상위 — 7234ms, 6594ms, 6156ms, 5609ms, 5015ms, 4907ms, 4906ms, 4813ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5609ms | 1967ms | **3642ms (65%)** |
| 09:05:06 | 7234ms | 453ms | **6781ms (94%)** |
| 10:48:06 | 6156ms | 3950ms | **2206ms (36%)** |
| 11:55:05 | 6594ms | 5214ms | **1380ms (21%)** |
| 13:44:07 | 5015ms | 4680ms | **335ms (7%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260923_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:22 2026-09-23 15:40:22 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 24분/일 < 하한 60분 — 금일 42분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- PSI ×1(표본)
15:40:20 2026-09-23 15:40:20 [WARNING] SYSTEM: [RegimeFingerprint] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerprint] 기준선 키 불일치` WARNING 이 기동 로그에 있는지 먼저 확인할 것
--- [CB] ×4(표본)
10:39:30 2026-09-23 10:39:30 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:55:05 2026-09-23 11:55:05 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5214ms — 처리 지연 (임계=5000ms)
11:55:05 2026-09-23 11:55:05 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5214ms — 처리 지연 (임계=5000ms)
11:56:01 2026-09-23 11:56:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1484ms | quality=1.00 | cache_age=150s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
--- [ExitCooldown] ×2(표본)
10:39:30 2026-09-23 10:39:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:42:30)
10:39:30 2026-09-23 10:39:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:42:30)
--- level=CRITICAL ×1(표본)
11:55:05 2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
--- 메인 스레드 블로킹 ×8(표본)
08:41:14 2026-09-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2500 band=INFO since_pipe_s=NA
09:00:05 2026-09-23 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5609ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5609 band=WARN since_pipe_s=0.1
09:00:53 2026-09-23 09:00:53 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=45 watchdog_alerted=[] | [MainStall] stall_ms=4516 band=INFO since_pipe_s=48.5
09:05:06 2026-09-23 09:05:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7234 band=WARN since_pipe_s=0.2
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260923_SYSTEM.log`
```
--- CIRCUIT ×2(표본)
11:55:05 2026-09-23 11:55:05 [INFO] SYSTEM: [Notify] 🚨 [11:55:05] [미륵이] Circuit Breaker 발동!
11:55:05 2026-09-23 11:55:05 [INFO] SYSTEM: [Notify] 🚨 [11:55:05] [미륵이] Circuit Breaker 발동!
--- ConstOut ×6(표본)
10:14:00 2026-09-23 10:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3545) | 앙상블 제외는 유지
10:23:00 2026-09-23 10:23:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3999) | 앙상블 제외는 유지
11:26:00 2026-09-23 11:26:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5547) | 앙상블 제외는 유지
13:20:00 2026-09-23 13:20:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5358) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:22 2026-09-23 15:40:22 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 0분 / 파이프라인 0분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-23 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:06:00 2026-09-23 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-23 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-23 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×4(표본)
12:01:01 2026-09-23 12:01:01 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
12:01:01 2026-09-23 12:01:01 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
15:40:22 2026-09-23 15:40:22 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:22 2026-09-23 15:40:22 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:22 2026-09-23 15:40:22 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 1레그 / 1포지션 중 TP 이벤트 대응 1 · 단일계약 보호전환(설계) 0 · 미대응 0
--- [SchedForceExit] ×2(표본)
15:11:22 2026-09-23 15:11:22 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
15:23:20 2026-09-23 15:23:20 [INFO] SYSTEM: [SchedForceExit] 15:23 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=1회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:23 2026-09-23 15:40:23 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:15 2026-09-23 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:23 2026-09-23 15:40:23 [INFO] SYSTEM: [Notify] ℹ️ [15:40:23] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:23 2026-09-23 15:40:23 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 397초
15:40:23 2026-09-23 15:40:23 [INFO] SYSTEM: 자동 종료 예약 — 412초 후 Qt 이벤트 루프 종료
```

### `logs/20260923_SIGNAL.log`
```
--- CIRCUIT ×1(표본)
11:58:01 2026-09-23 11:58:01 [INFO] SIGNAL: [차단] Circuit Breaker PAUSED — 진입 불가 (CB 해제까지 대기)
--- ConstOut ×8(표본)
10:14:00 2026-09-23 10:14:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0470 dir=-1)
10:14:00 2026-09-23 10:14:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:14:00 2026-09-23 10:14:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
10:15:00 2026-09-23 10:15:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0470 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-23 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-23 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-23 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-23 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.435
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.414
08:40:30 2026-09-23 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.410
--- 안전망 ×8(표본)
09:07:00 2026-09-23 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-23 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-23 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-23 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260923_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00004 auc=0.481 out_max=0.3375 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00022 auc=0.453 out_max=0.1501 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00147 auc=0.452 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:54 2026-09-23 08:40:54 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00136 auc=0.573 out_max=0.1248 (n=145) → 보정 재적용
```

### `logs/20260923_HEALTH.log`
```
--- [CB] ×2(표본)
11:56:01 2026-09-23 11:56:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1484ms | quality=1.00 | cache_age=150s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
11:57:00 2026-09-23 11:57:00 [INFO] HEALTH: [Health] level=INFO degraded=ON | latency=280ms | quality=1.00 | cache_age=24s | exceptions_10m=4 | exc_tags=[BarGap]×1 [CB]×1 [LEVELS]×1 외 1종
--- level=CRITICAL ×1(표본)
11:55:05 2026-09-23 11:55:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5214ms | quality=1.00 | cache_age=93s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS]×1 [RESTART]×1
```

### `logs/retrain_eod_20260923.log`
```
--- ConstOut ×1(표본)
??:??:?? | `[51]` | `아직 미확인` | ConstOut 호라이즌 건강도 |
--- 축퇴 ×1(표본)
??:??:?? | `[45]` | `cal_guard_flap_watch` | 축퇴 가드 플래핑 (게이지) |
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260923_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:03 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 9 | 09:55:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,725,029) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 1 | 15:22:47 [INFO] 설정 업데이트 완료 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:22 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260923_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:12 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 221 | 08:55:15 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 799 | 08:55:15 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1562 | 09:54:00 [WARNING] paintEvent slow 78.0ms | size=1663x832 candles=70 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 432 | 11:54:00 [WARNING] 그리기 102.2ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| 14:00 | 장중 후반 · 장중 재학습 | 39 | 13:54:57 [WARNING] _fetch_investor_data 지연 623ms — 메인 스레드 623ms 점유 (live 중단 원인 후보) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 83 | 15:04:00 [WARNING] paintEvent slow 100.1ms | size=1814x928 candles=365 grid=34.5 spans=6.1 candles=13.7 dir=1.1 regime=4.6 marke… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 86 | 15:12:00 [WARNING] paintEvent slow 100.6ms | size=1814x928 candles=373 grid=24.2 spans=12.7 candles=13.9 dir=1.1 regime=4.5 mark… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 21 | 15:34:00 [WARNING] paintEvent slow 143.3ms | size=2097x1154 candles=392 grid=24.1 spans=10.2 candles=15.7 dir=1.1 regime=8.1 mar… |
| 15:47 | EOD 재학습(py310_64) 완료 | 10 | 15:45:42 [WARNING] paintEvent slow 109.7ms | size=2097x1154 candles=392 grid=24.6 spans=8.4 candles=14.8 dir=1.2 regime=9.2 mark… |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260923_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=23656 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 132 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 198 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 202 | 11:54:00 [INFO] intraday 2026-09-23 — 6패널 수집, 메인 스레드로 넘긴다 [futures_flow option_chain option_flow prediction price rv_iv] |
| 14:00 | 장중 후반 · 장중 재학습 | 168 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 146 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 186 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 53 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 6 | 15:42:50 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:42:50 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 369/371분 (99.5%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260923_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:14 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 76 | 09:00:02 [WARNING] 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 147 | 09:00:02 [WARNING] 1m 'macro_risk_on' scale=0.4440 → floor=0.50 적용 (z-score 폭발 방지) |
| 10:00 | 장중 초반 | 212 | 09:54:00 [WARNING] 신뢰도 미달 31.7% < 39.2% → 강제 X등급 |
| 12:00 | 장중 중간점 | 203 | 11:54:00 [WARNING] 1m 극단 z-score 6개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 14:00 | 장중 후반 · 장중 재학습 | 139 | 13:54:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 65 | 15:04:00 [WARNING] 실질 가중합 0 (2연속) — 활성기대=['1m', '3m'] 중 미배포=['1m', '3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 17 | 15:22:29 [INFO] 기동 복원: OPEN_VOLATILE  0.600 → 0.434 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:22 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260922 | 15:47 | 로그 본문 |
| 20260921 | 17:30 | 로그 본문 |
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| **중앙값** | **17:30** | 기준선 |
| **오늘 20260923** | **15:47** | 로그 본문 |

- 델타 **-103분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 6. 자가유발 여부
## 2026-09-23 (MW0601 604차 후속 — 장중 점검: 재기동 생존시간이 매번 절반 가까이 줄고 있는데, 안전망은 못 본다)
### 증상
### 원인 (확정 아님 — 장후·후속 조사 필요)
### 결정
### Why
### How to apply
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 후속 — 장중 점검: 재기동 생존시간이 매번 절반 가까이 줄고 있는데, 안전망은 못 본다)

### 증상

08:40:33 최초 기동 이후 12:39 현재까지 `main.py`가 **7번 재기동**했다(`[CLEAN EXIT]` →
자동 재시작). 생존시간이 매회 짧아지는 추세다: **125분 → 43분 → 23분 → 16분 → 12분 →
8분 → 7분**(`logs/Mireuk_batch/launcher_20260923_084001_1592.log` `Runtime=` 실측).
전부 `[CLEAN EXIT]` 마커를 남겼고(`Fatal Python error` 0건), `crash_fault.log`에
실제 예외 트레이스백은 하나도 안 남아 있다.

### 원인 (확정 아님 — 장후·후속 조사 필요)

두 가지를 실측으로 확인했고, 원인 자체(무엇이 재기동을 유발하는가)는 **미확정**이다.

1. **`[CLEAN EXIT]` 라벨의 한계는 기존에 이미 알려진 문제다.** `main.py:20596`의
   `_fault_atexit()`는 `atexit.register()`로 등록되므로 정상 종료뿐 아니라
   **처리되지 않은 예외로 인터프리터가 죽을 때도 동일하게 실행된다** — os._exit()가
   아닌 이상 atexit 핸들러는 항상 돈다. 이 한계는 09-21 15:11:37 CLEAN EXIT 건에서
   이미 지적됐고(`NEXT_TODO.md` F-3·G-3: 무흔적 즉사 원인 규명, `[CLEAN EXIT
   reason=...]` 확장 제안 — 미착수), 오늘 7회 연속 재현으로 방치 비용이 커지고 있음을
   보여준다.
2. **신규 발견 — 런처의 "재시작 5회 초과 시 수동확인" 안전망(`start_mireuk.bat:631`)이
   오늘 패턴에서 완전히 무력화됐다.** 이 안전망은 `_RESTART_CNT`를 누적하는데,
   `start_mireuk.bat:585` `IF !_RUNTIME_MIN! GTR 5 SET "_RESTART_CNT=0"` 로직 때문에
   **생존시간이 5분을 넘기면 카운터가 매번 0으로 리셋된다.** 오늘의 7회는 전부 생존시간이
   5분을 넘었으므로(7~125분) 카운터가 한 번도 쌓이지 못했고, "재시작 5회 초과" 팝업은
   한 번도 뜨지 않았다. **이 안전망은 "짧은 간격의 크래시 루프"(수 분 이내 반복)만
   잡도록 설계됐고, "천천히 가속되는 크래시"(각 구간은 5분을 넘지만 그 구간 자체가
   매번 짧아지는 패턴)는 설계상 완전한 사각지대다.**

### 결정

- 이번 세션(장중 점검)은 코드를 수정하지 않는다(라이브 프로세스 운영 중, 스킬 규약).
- 원인 규명과 런처 안전망 보강을 **P0으로 장후 최우선 항목 등록**한다(F-4, F-5 —
  아래 NEXT_TODO 참조).
- 오늘 실거래 손실은 0원(모든 재기동 시점에 포지션 FLAT, 세션 복원 시 누적손익·GapOffset
  정확 복구 확인). 즉시 개입 필요한 P0는 아니지만, 추세가 이어지면 15:10 강제청산
  집행 시점에 프로세스가 마침 꺼져 있을 위험이 배제되지 않아 **관측 우선순위는 최고**로
  둔다.

### Why

- 실전 전환 기준 ②-ⓑ(동결 감시→하드종료→재기동 왕복 라이브 실측)와 절대원칙
  ①(15:10 강제청산)이 전제하는 "장 마감까지 프로세스가 살아있다"가 위협받을 수 있는
  패턴이라, 정상 손익 결과와 무관하게 별도로 추적할 가치가 있다.
- 계측 4원칙 ④(폴백 가시화)의 연장 — "CLEAN EXIT"라는 이름이 실제로는 "예외로 죽었다"를
  가리는 폴백 라벨로 오용될 수 있음을 재확인한 사례.

### How to apply

- 장후 점검에서 `crash_fault.log`·런처 로그 7건 전체를 재대조하고, 가능하면
  `main.py:20639`(`system.run()` 호출부) 주변에 최상위 예외 핸들러를 씌워 예외
  트레이스백을 `crash_fault.log`에 강제 기록하는 방안을 설계한다(현재는 예외가 나도
  atexit만 남고 원인 텍스트가 전혀 안 남는다).
- 런처 안전망 보강안(직전 대비 생존시간이 감소 추세인지 보는 로직)은 매매 정책이 아니라
  운영 인프라 변경이므로 주간회의 안건으로 올린다.
- `dashboard/main_dashboard.py`의 `ChartDBG` 렌더링 부하(오늘 09:00~12:36 slow paint
  16,858건, `overlay_cnt` 증가 추세 관측)가 재기동 가속과 상관이 있는지 장후에 우선
  확인한다(G-2, 상관 조사 — 인과 주장 아님).

### 검증

- **라이브 미검증** — 원인 미확정 상태. 장후 점검(오늘) 및 다음 거래일까지 재기동
  패턴이 지속/악화/해소되는지로 판단한다. O-i1로 등록.

근거: `docs/정기점검/매일점검/MW0601-20260923-점검리포트.md` §장중 1-4,
`docs/정기점검/매일점검/evidence_MW0601-20260923_intra.md` §7-8.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 신규 등록
### 확인 완료 (617차 후속3이 재확인·최종판정, 신규 아님)
## 2026-09-23 (MW0601 604차 — 장전 점검)
### 신규 등록
### 확인 완료 (604차가 재확인, 신규 아님)
## 2026-09-23 (MW0601 604차 후속 — 장중 점검)
### 신규 등록
### 확인 완료 (604차 후속이 재확인·재분류, 신규 아님)
```

미완료 체크박스 **2819건** (끝에서 30건)
```
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
- [ ] **O-i1 (오늘 장후 판정)** `[OptionFlow]` 실패 태그 재발 여부·`option_flow.db`
- [ ] **O-i2 (오늘 장후·내일 판정)** `[LiveDBG] _fetch_investor_data 지연` 경고
- [ ] **G-1 (P2, 저우선, 이 점검 세션 제안)** 장중 라이브 배포 시 "재기동 직후
- [ ] **F-1 (P2, 신규) `.git/index.lock` 반복 재발 원인 규명** — 이 세션도
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단`
- [ ] **O-p2 (5거래일 후 판정 — 313차 원칙, 표본 부족 상태 결론 금지)**
- [ ] **O-p3 (오늘 세션 종료 시 판정)** `.git/index.lock` 최종 상태
- [ ] **O-p4 (다음 점검)** `collect_evidence.py`의 `git diff` 실패
- [ ] **무가드 표시 슬롯 15건 가드** — `python scripts/audit_qtimer_slot_guards.py`
- [ ] **엔진 슬롯 3건 처분 결정(주간회의)** — `main.py:TradingSystem` 의
- [ ] **재기동 원인 표기** — 크래시 재기동이 `cause=STARTUP` 으로 남아 정상
- [ ] 반영 확인 — 다음 재기동 후 좌측 스플리터를 끝까지 끌어 **접히지 않는지**
- [ ] **O-i1 (오늘 장후 또는 다음 재기동 시 판정)** 크래시 수정(커밋 `e3e5d91`)의
- [ ] **O-i2 (26주 WFA 주기, 기존 채널에 표본만 추가)** `sizing_inversion_watch`
- [ ] **F-1(지속) git lock 원인 가설 추가** — 장중 12:35경 재발 시각이 병행
- [ ] **[사용자 판단 필요] 크래시 수정 재기동 시점** — 지금(포지션 FLAT, 재기동
- [ ] **F-3 (P1, 신규) 2차 무흔적 크래시(1-7) 원인 규명** — 15:08:06경
- [ ] **G-3 (P2, 신규) 런처의 "무흔적 즉사" vs "행 멈춤" 구분 계측** —
- [ ] **O-t1 (다음 거래일부터 상시)** 1-7과 같은 무흔적 즉사 재현 여부 —
- [ ] **O-t3 (5거래일 누적 후 판정)** CB③ 판정가능시간 0분 재현 빈도(1-8) —
- [ ] **O-t4 (26주 WFA 주기, O-i2 계승)** `sizing_inversion_watch`([28])
- [ ] **[권고, 급하지 않음] Windows 이벤트 뷰어에서 15:08:06~08 오류 이벤트
- [ ] **O-p1 (오늘 장중 판정)** `raw_candles`/`session_bars` "영구결손 367봉"(09:02~09:21) 표시 —
- [ ] **O-p2 (다음 세션 시작 시 판정)** `.git/index.lock` 회수 여부 — 사용자가 Windows에서
- [ ] **F-4 (P0, 신규, 장후 최우선) 재기동 생존시간 가속 감소 원인 규명** — 08:40:33
- [ ] **F-5 (P1, 신규, 주간회의 안건) 런처 5회 재시작 안전망의 설계 사각지대** —
- [ ] **G-2 (P1, 신규) `ChartDBG` 렌더링 부하 — 재기동 가속 상관 조사** — 오늘
- [ ] **O-i1 (오늘 장후 판정)** F-4 재기동 패턴 — 8번째 재기동 발생 여부·15:10까지
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
mupRetrain)로 평소보다 잦아 경고 횟수만 늘었을 뿐.
- [x] 오늘 진입 2건 "A급(원시C)" 상향, 체크리스트 미통과(`cvd`·`fore`·
      `prev`·`chas`) — 전부 등급 하락 사유일 뿐 VWAP 강제X 위반 없음.
      절대원칙 ③ 준수 확인.

## 2026-09-23 (MW0601 604차 — 장전 점검)

### 신규 등록
- [ ] **O-p1 (오늘 장중 판정)** `raw_candles`/`session_bars` "영구결손 367봉"(09:02~09:21) 표시 —
      09:01 시점 조기 집계로 인한 artifact로 추정(당일 예상 총 411봉 중 아직 17봉만
      경과). 장중·장후 재수집 시 정상적으로 채워지는지 확인, 실제 결손이면 새 이상점으로 등록.
- [ ] **O-p2 (다음 세션 시작 시 판정)** `.git/index.lock` 회수 여부 — 사용자가 Windows에서
      `python scripts/git_lock_guard.py --reclaim` 실행 후 `--check`가 OK 반환하는지 확인.

### 확인 완료 (604차가 재확인, 신규 아님)
- [x] F-1(538-4) `SessionStateDrop` — 09-23도 재현(08:41:15). 근본 원인 미해결 상태 지속.
      실제 EOD/P8은 `retrain_eod_20260922.log`로 정상 완료 확인(계측 4원칙 ② 사례).
- [x] 606-3 미커밋 3파일 — diff 크기 재확인(1,332/1,433/4,247줄), 사용자 검토 대기 지속.
- [x] `.git/index.lock` STALE — 09-22 장후부터 미회수 지속, 오늘도 리눅스 세션에서 회수 불가.

## 2026-09-23 (MW0601 604차 후속 — 장중 점검)

### 신규 등록
- [ ] **F-4 (P0, 신규, 장후 최우선) 재기동 생존시간 가속 감소 원인 규명** — 08:40:33
      이후 12:39까지 `main.py` 7회 재기동, 생존시간 125→43→23→16→12→8→7분으로 단조
      감소. 전부 `[CLEAN EXIT]`(atexit 마커)만 남고 예외 트레이스백 0건 — 원인 미상.
      `main.py:20639`(`system.run()`) 최상위에 예외 핸들러를 씌워 트레이스백을
      `crash_fault.log`에 강제 기록하는 방안부터 검토. 15:10 강제청산 전제(프로세스
      생존)와 실전 전환 기준 ②-ⓑ에 잠재 위험.
- [ ] **F-5 (P1, 신규, 주간회의 안건) 런처 5회 재시작 안전망의 설계 사각지대** —
      `start_mireuk.bat:585` `IF !_RUNTIME_MIN! GTR 5 SET "_RESTART_CNT=0"` 때문에
      생존시간이 매번 5분을 넘기기만 하면(오늘처럼 7~125분) 재시작 카운터가 계속
      리셋되어 "5회 초과 시 수동확인" 팝업(`:631`)이 절대 안 뜬다. "짧은 간격 크래시
      루프"만 잡고 "천천히 가속되는 크래시"는 못 잡는 구조 — 직전 대비 생존시간 감소
      추세를 보는 로직으로 보강 검토(운영 인프라 변경, 매매 정책 아님).
- [ ] **G-2 (P1, 신규) `ChartDBG` 렌더링 부하 — 재기동 가속 상관 조사** — 오늘
      09:00~12:36 `paintEvent slow` 16,858건, `overlay_cnt` 증가 추세(275→305→324→354)
      관측이 F-4의 재기동 가속 시점과 겹치는지 상관관계만 조사(인과 주장 아님).
      `dashboard/main_dashboard.py` 우선 확인.
- [ ] **O-i1 (오늘 장후 판정)** F-4 재기동 패턴 — 8번째 재기동 발생 여부·15:10까지
      생존 지속 및 강제청산 정상 집행 여부.

### 확인 완료 (604차 후속이 재확인·재분류, 신규 아님)
- [x] O-p1(`raw_candles`/`session_bars` 09:02~09:21 "영구결손 367봉") — **판정 완료:
      해소.** 장중 재수집 결과 해당 구간 결손 0봉 확인. 영구결손은 10:45 이후
      시각대에서 재기동과 1:1 대응해 발생하는 별개 패턴(F-4로 재분류).
- [x] 1-1(`.git/index.lock`)·1-2(`SessionStateDrop`)·1-3(미커밋 3파일) — 장중 재확인,
      전부 지속(변화 없음), 사용자 조치 대기.
- [x] CB② 카운터 1회(300초 창, 3회 미만 정지 안 함)·CB⑤ 2회 발동(11:55:05, 파이프라인
      5214ms→5분 정지→12:01:01 정상 복귀) — 둘 다 설계대로 정상 동작.
- [x] O-i2(계승, `sizing_inversion_watch`[28]) — 오늘 qty≥3 표본 2건 추가(사이저
      3계약→실제 최대 2계약). 26주 WFA 판정 대기 지속.

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

### `data/heartbeat_MW0601_20260923.json` — 245B · 09-23 15:46:52
```json
{
 "pid": 15688,
 "written_at": "2026-09-23T15:46:52",
 "beat_epoch": 1790146010.9371586,
 "beat_age_sec": 1.3,
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

### `data/peter_feed/_raw/2026-09-23.jsonl` — 3.0KB · 09-23 16:19:52
```json
JSONL 19행 ⏎ 첫: {"id": "2102550476013420990", "dt": "2026-09-23T00:07:51.000Z", "text": "1130 밑으로 떨어지면 \n\n확인하고 매수 들어갈 예정이니 대기", "seen_at": "2026-09-23T07:19:52"} | {"id": "2102552493167411647", "dt": "2026-09-23T00:15:52.000Z", "text": "매수잖아", "seen_at": "2026-09-23T07:19:52"} | {"id": "2102557947884937464", "dt": "2026-09-23T00:37:33.000Z", "text": "1130 돌파시 매수.  손절가 1125", "seen_at": "2026-09-23T07:19:52"} ⏎ 끝: {"id": "2102641885710094600", "dt": "2026-09-23T06:11:05.000Z", "text": "1125 청산가로 변경", "seen_at": "2026-09-23T07:19:52"} | {"id": "2102642912752545824", "dt": "2026-09-23T06:15:10.000Z", "text": "1125 청산체결\n\n5p 수익 - 5p 손실 = 0\n\n오늘 진빠지는 날이네요.\n\n그래도 최대한 선방했습니다. \n\n무패로도 만족하는 날입니다.", "seen_at": "2026-09-23T07:19:52"} | {"id": "2102644207970390137", "dt": "2026-09-23T06:20:19.000Z", "text": "저의 공개 매매를 보고\n\n리딩을 하고 있다는 제보가 계속 접수되고 있습니다.\n\n재주는 제가 부리고 돈은 엄한 리빙방주들이 벌고 있습니다.\n\n심지어 올려드리는 리포트도 다 카피에서 뿌리고 있다고 합니다.\n\n제가 어떻게 했으면 좋겠습니까?\n\n댓글 남겨주시면 고민해 보겠습니다.", "seen_at": "2026-09-23T07:19:52"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-23 15:53:32**

| 키 | 값 | 수집 대상일(2026-09-23)과 일치 |
|---|---|---|
| `date` | 2026-09-23 | 예 |
| `p8_last_success_date` | 2026-09-23 | 예 |
| `eod_retrain_ok_date` | 2026-09-23 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 369 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **15봉**: 10:45, 10:46, 11:29, 11:52, 12:09, 12:22, 12:30, 12:36, 12:37, 13:38, 13:39, 13:40, 13:41, 13:51, 14:18
  - 전부 `session_bars` 에 보존됨 → **데이터 손실 아님**. 백필하지 않는다(533차 — 최근 N행 창이 밀린다).

- 라이브 로그 대조: `logs/20260923_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 12회 · 재시작 10회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 12개 |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 23656 | 08:40:33 | 10:45:48 | 없음 | 판정불가 — WER **미측정** |
| 23860 | 10:46:11 | 11:29:20 | 없음 | 판정불가 — WER **미측정** |
| 21744 | 11:29:42 | 11:52:46 | 없음 | 판정불가 — WER **미측정** |
| 8124 | 11:53:08 | 12:09:50 | 없음 | 판정불가 — WER **미측정** |
| 10340 | 12:10:11 | 12:22:06 | 없음 | 판정불가 — WER **미측정** |
| 20224 | 12:22:27 | 12:30:33 | 없음 | 판정불가 — WER **미측정** |
| 6512 | 12:30:54 | 12:37:01 | 없음 | 판정불가 — WER **미측정** |
| 11272 | 12:37:22 | 없음 | 없음 | 판정불가 — WER **미측정** |
| 22160 | 13:41:58 | 없음 | 없음 | 판정불가 — WER **미측정** |
| 5964 | 13:52:16 | 14:18:55 | 없음 | 판정불가 — WER **미측정** |
| 9972 | 14:19:15 | 15:19:22 | 없음 | 판정불가 — WER **미측정** |
| 15688 | 15:22:31 | 15:47:15 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 164개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260923-점검리포트.md` | 31.3KB | 09-23 12:42 |
| `docs/정기점검/매일점검/evidence_MW0601-20260923_intra.md` | 73.9KB | 09-23 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20260923_pre.md` | 57.2KB | 09-23 09:02 |
| `docs/정기점검/매일점검/MW0601-20260922-점검리포트.md` | 99.0KB | 09-22 17:46 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_post.md` | 86.9KB | 09-22 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_intra.md` | 70.4KB | 09-22 12:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_pre.md` | 54.0KB | 09-22 09:00 |
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 73.2KB | 09-21 16:30 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260923.json` | 3.0KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260923.md` | 4.9KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260923.json` | 38.8KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260923.md` | 32.3KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260923.json` | 121.3KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260923.md` | 195.2KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json` | 3.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md` | 5.0KB | 09-18 15:55 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260923_WARN.log`: ERROR 이상 1건
2. `logs/20260923_HEALTH.log`: ERROR 이상 1건
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. 포지션 1건 중 최종청산이 하드스톱·손절 계열 **1건(100%)** — 손절 준수율 확인 필요 (레그 2행)
5. 다레그 포지션 **1건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
6. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
7. **SYSTEM 로그가 직전 5거래일 중앙값(17:30)보다 103분 이르게 끝났다** (오늘 15:47) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
8. 메인 스레드 정지 5초 초과 **5건** (최대 7234ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
9. `logs/20260923_WARN.log`: **level=CRITICAL** 1건(표본)
10. `logs/20260923_SYSTEM.log`: **ConstOut** 6건(표본)
11. `logs/20260923_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260923_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260923_LEARNING.log`: **축퇴** 8건(표본)
14. `logs/20260923_HEALTH.log`: **level=CRITICAL** 1건(표본)
15. `logs/retrain_eod_20260923.log`: **축퇴** 1건(표본)
16. `logs/retrain_eod_20260923.log`: **ConstOut** 1건(표본)
17. 미커밋 변경 757건 (실질 13건 · **코드(.py) 3건**) — 코드 변경이 커밋되지 않았다
18. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260923*.log` (Windows) / `grep 강제청산 logs/*20260923*.log`*