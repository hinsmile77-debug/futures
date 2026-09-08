# 미륵이 증거 다이제스트 — 2026-09-08 / POST

- 생성 2026-09-08 16:17:52 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/affectionate-upbeat-goldberg/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260908` · `2026-09-08` · `260908` · `0908`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **31개** 파일 · 31개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260908.txt` | 28B | 09-08 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260908.txt` | 28B | 09-08 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260908.txt` | 209B | 09-08 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260908.log` | 1.4KB | 09-08 15:39 |
| `freeze_sentinel_alert_{DATE}.txt` | 1 | `data/freeze_sentinel_alert_20260908.txt` | 702B | 09-08 09:00 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260908.log` | 3.9KB | 09-08 15:46 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260908.json` | 244B | 09-08 15:40 |
| `launcher_{DATE}_084002_29245.log` | 1 | `logs/Mireuk_batch/launcher_20260908_084002_29245.log` | 17.8MB | 09-08 15:40 |
| `launcher_{DATE}_090400_1173.log` | 1 | `logs/Mireuk_batch/launcher_20260908_090400_1173.log` | 1.2KB | 09-08 09:04 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260908.log` | 11.4KB | 09-08 13:20 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260908.log` | 20.8KB | 09-08 15:53 |
| `retrain_intraday_{DATE}_090459.log` | 1 | `logs/retrain_intraday_20260908_090459.log` | 5.3KB | 09-08 09:05 |
| `retrain_intraday_{DATE}_100501.log` | 1 | `logs/retrain_intraday_20260908_100501.log` | 2.8KB | 09-08 10:05 |
| `retrain_intraday_{DATE}_111100.log` | 1 | `logs/retrain_intraday_20260908_111100.log` | 2.8KB | 09-08 11:11 |
| `retrain_intraday_{DATE}_115001.log` | 1 | `logs/retrain_intraday_20260908_115001.log` | 2.8KB | 09-08 11:50 |
| `retrain_intraday_{DATE}_123001.log` | 1 | `logs/retrain_intraday_20260908_123001.log` | 2.8KB | 09-08 12:30 |
| `retrain_intraday_{DATE}_130800.log` | 1 | `logs/retrain_intraday_20260908_130800.log` | 2.8KB | 09-08 13:08 |
| `retrain_intraday_{DATE}_142001.log` | 1 | `logs/retrain_intraday_20260908_142001.log` | 2.8KB | 09-08 14:20 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260908.txt` | 43B | 09-08 15:40 |
| `strategy_report_{DATE}_154030.txt` | 1 | `data/daily_reports/strategy_report_20260908_154030.txt` | 2.1KB | 09-08 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260908_DATA.log` | 340.1KB | 09-08 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260908_DEBUG.log` | 229.7KB | 09-08 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260908_HEALTH.log` | 8.9KB | 09-08 14:37 |
| `{DATE}_HOGA.log` | 1 | `logs/20260908_HOGA.log` | 48.9MB | 09-08 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260908_LEARNING.log` | 286.8KB | 09-08 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260908_MICRO.log` | 977.0KB | 09-08 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260908_PROBE.log` | 94.7KB | 09-08 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260908_SIGNAL.log` | 590.4KB | 09-08 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260908_SYSTEM.log` | 17.0MB | 09-08 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260908_TRADE.log` | 15.2KB | 09-08 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260908_WARN.log` | 61.9KB | 09-08 15:40 |

## 2. 코드·커밋 상태

- HEAD `96b0d61` · 브랜치 `v9-dev` · 미커밋 552건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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

**당일(2026-09-08) 커밋**
```
96b0d61 [MW0601] 546차 후속: dev 적응 이식 완료 기록
5a11474 [MW0601] 545·546차: ProfitGuard L1~L4 배지 복구 + 판정 손익을 시스템 자동매매 한정으로
```

**최근 커밋 12건**
```
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
050241e [MW0601] 539차: ATR 진입 하한(ATR_MIN_ENTRY) 26주 WFA 재검증 편입 (매매정책 무변경)
308a45a [MW0601] 538차 후속: 0907 장후 점검 산출물 + 자동조치 기록
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

_본문 미열람(설정): `20260908_HOGA.log` 48.9MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260908.txt`** — 28B · 09-08 15:40:30
```
2026-09-08T15:40:30.714837
```

**`data/daily_close_started_20260908.txt`** — 28B · 09-08 15:40:28
```
2026-09-08T15:40:28.500157
```

**`data/daily_reports/strategy_report_20260908_154030.txt`** — 2.1KB · 09-08 15:40:30
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-08 15:40
========================================================
  버전    : v1.0  (75일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-5.40  MDD(자본대비)=29.8%
  당일      : WR=83.3%  PF=1.40
  롤링20일: 누적 -12763539원  Sh=-5.40  MDD(자본대비)=29.8%  MDD(peak대비)=724.0%
  당일손익 : broker(gross) +591,000원  수수료 77,033원  net +67,967원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.005 (CLEAR)
  PSI/feat: cvd_delta=0.005  ofi_pressure=0.001  vwap_position=0.081
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -10,462원  승률 50.0%  합계 -209,234원
  등급별 순EV(30일): A=-711원(100건,승62%)  BROKER=-5,380,798원(2건,승0%)  C=-2,922원(11건,승73%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=-6,825원(19건)  3m=-10,839원(71건)  5m=+30,978원(19건)  ?=-79,845원(170건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 32분  5일평균 36분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 32.7pt(5일평균 24.9pt)  1분평균변동 0.72pt(5일평균 0.65pt)
--------------------------------------------------------
  진입 퍼널(2026-09-08, 총 365분):
    FLAT 244 → conf미달 83 → CoherenceGate 6 → 게이트차단 32 → 후보 0 → 진입 0
    게이트별: 게이트강등(기타)=13  체크리스트항목미달=8  시가갭(OPEN_VOLATILE)=7  ATR변동성=3  마감시간(신규진입금지)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260908.txt`** — 209B · 09-08 15:53:56
```
completed: 2026-09-08 15:53:56
rows: 40827
cols: 97
horizons_replaced: 6/6
t_load_s: 41.1
t_retrain_s: 190.6
t_total_s: 232.2
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

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

**`data/shutdown_normal_20260908.txt`** — 43B · 09-08 15:40:45
```
auto_shutdown
2026-09-08T15:40:45.712588
```

_다이제스트 대상 8/23개 (중요도순). 제외: `retrain_intraday_20260908_111100.log`, `retrain_intraday_20260908_115001.log`, `retrain_intraday_20260908_123001.log`, `retrain_intraday_20260908_130800.log`, `retrain_intraday_20260908_142001.log`, `retrain_intraday_20260908_100501.log`, `20260908_MICRO.log`, `20260908_DATA.log`_

### `logs/20260908_TRADE.log` — 15.2KB · 99행 · 최종 15:40:29

- 형식 평문 · 시각 인식 99행 · WARNING=10, INFO=89

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-08 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-08 09:18:50 [INFO] TRADE: [Chejan] 상태=접수 주문번호=681 code=A0569 방향=LONG 체결=2 미체결=0
2026-09-08 09:18:50 [INFO] TRADE: [Chejan] 상태=체결 주문번호=681 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-08 09:18:50 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1121.60 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
  …
2026-09-08 15:01:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-08 15:02:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-09-08 15:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-09-08 15:05:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-09-08 15:40:29 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 7 | 09:18:50 | 09:37:49 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1121.60 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `ProfitGuard-L1` | 2 | 09:40:00 | 13:53:42 | 트레일링 발동 — 피크 +684,928원 대비 10% 하락 (현재 +524,940원 < 보호선 +616,435원) |
| `ProfitGuard-L4` | 1 | 13:53:42 | 13:53:42 | 수익 보존 CB 발동 — 당일 수익 +400,000원 상태에서 2연속 손실 → 당일 진입 중단 |

**채널** — `TRADE`×99

**컴포넌트 상위 15** — `Sizer`×27, `Chejan`×23, `Position`×15, `PositionFallback`×7, `체결동기화`×7, `청산 완료`×6, `ProfitGuard`×4, `주문요청`×2, `ProfitGuard-L1`×2, `MarginCap`×2, `TickTP1`×1, `TP1 부분청산`×1, `TickStop-S0C`×1, `ProfitGuard-L4`×1

### `logs/20260908_WARN.log` — 61.9KB · 363행 · 최종 15:40:29

- 형식 평문 · 시각 인식 353행 · CRITICAL=11, ERROR=9, WARNING=333, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA
2026-09-08 09:04:57 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-08 09:04:57 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-08 09:04:58 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 235ms account=333044256
2026-09-08 09:04:59 [WARNING] SYSTEM: [RESTART] 장중 재시작 감지 09:04 — GapOffset=미설정(첫분봉 재설정 예정)  pre_market_scaler=False
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +67967원
════════════════════════════════════════════════════
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 11 | 09:06:05 | 09:30:00 | level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1 |
| ERROR | `ExternalEntry` | 8 | 09:18:50 | 15:40:28 | 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — LONG 1계약 @ 1121.6 (보유 1계약, 평균 1121.6). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다 |
| ERROR | `NetRecon` | 1 | 15:40:29 | 15:40:29 | 🔴 net 불일치 — 엔진 +67,967원 vs 브로커 +492,144원 (잔차 -424,177원, 허용 ±19,771) |

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

<details><summary>ERROR/NetRecon 원문 1건</summary>

```
2026-09-08 15:40:29 [ERROR] SYSTEM: [NetRecon] 🔴 net 불일치 — 엔진 +67,967원 vs 브로커 +492,144원 (잔차 -424,177원, 허용 ±19,771)
```

</details>

**WARNING — 태그 37종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 96 | 08:41:11 | 14:00:04 | _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band=INFO since_pipe_s=NA |
| `ChejanFlow` | 23 | 09:18:50 | 09:39:12 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1121.78 | fill_qty=2 | gubun='0' | order_no='681' | pending='NONE' | position='FLAT' | position_qty=0 | sell_balance=0 | side='LONG' | … |
| `ChejanMatch` | 23 | 09:18:50 | 09:39:12 | order_no='681' | pending='NONE' | pending_matched=False |
| `Health` | 23 | 09:19:00 | 14:36:00 | level=WARNING degraded=OFF | latency=373ms | quality=1.00 | cache_age=80s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2 |
| `OrderSync` | 22 | 09:18:50 | 09:37:49 | 미추적 체결 감지 (pending_miss) order_no=681 side=LONG qty=1 price=1121.6 before=FLAT |
| `PipePerf` | 18 | 09:05:01 | 13:20:03 | [GBM재학습중] total=1094ms | S0=2ms S1=62ms S2=0ms S3=0ms S4=120ms S5=570ms S6=323ms S7=14ms S8=3ms |
| `CB⑤` | 18 | 09:05:02 | 13:20:03 | 파이프라인 1094ms 경고 (기준 1000ms) [장시작 버스트] [GBM재학습중→임계×2] |
| `SHAP` | 18 | 11:42:01 | 15:06:01 | 슬로우 감지 921ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `ScalerRefresh` | 16 | 09:14:00 | 14:53:00 | 5분 누적 수익률 +0.381% (임계 ±0.246%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ExitCooldown` | 12 | 09:20:19 | 09:39:12 | 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:19) |
| `CB③-P4` | 12 | 10:55:00 | 13:55:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `HealthPolicy` | 10 | 09:07:00 | 13:21:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=5090ms quality=1.00 cache=0s exc10m=4) | cause=S0(4405ms) |

**채널** — `SYSTEM`×319, `HEALTH`×34

**컴포넌트 상위 15** — `LiveDBG`×96, `Health`×34, `ChejanFlow`×23, `ChejanMatch`×23, `OrderSync`×22, `PipePerf`×18, `CB⑤`×18, `SHAP`×18, `ScalerRefresh`×16, `ExitCooldown`×12, `CB③-P4`×12, `HealthPolicy`×10, `-`×9, `ExternalEntry`×8, `ConstOut`×6

### `logs/20260908_SYSTEM.log` — 17.0MB · 129093행 · 최종 15:40:45

- 형식 평문 · 시각 인식 129076행 · INFO=129076, PLAIN=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:35 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=23044 | 행감지=30s all_threads=True
2026-09-08 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-08 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-08 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-08 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-07) 종가 버퍼 로드: 384봉
  …
2026-09-08 15:40:30 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-08 15:40:30 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-08 15:40:45 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-08 15:40:45 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-08 15:40:45 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×129076

**컴포넌트 상위 15** — `CybosRT-AUCTION`×123288, `CybosInvestorRaw`×1564, `CybosRT-TICK`×1237, `CybosRT-ROLLOVER`×390, `BAR-CLOSE`×390, `CVD-ANCHOR`×390, `TickUI`×387, `S6Detail`×365, `PipePerf`×365, `System`×87, `MicroRegime`×82, `RegimeFingerprint`×66, `CybosEvent`×46, `CybosDailyPnl`×44, `BalanceUI`×43

### `logs/20260908_SIGNAL.log` — 590.4KB · 5012행 · 최종 15:40:29

- 형식 평문 · 시각 인식 5012행 · WARNING=1645, INFO=3367

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-08 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
  …
2026-09-08 15:26:57 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L2-Tier4] Tier 4: 중단 임계 500,000원 도달 → 당일 영구 중단 | src=engine(net·시스템진입만)
2026-09-08 15:40:29 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-08 15:40:29 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 365분 중 섀도만 활성 UP 114분(31.2%) / DN 18분(4.9%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-08 15:40:29 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-08 age=1031m extreme=800 refresh=45 grade_x=88 cb3=0
2026-09-08 15:40:29 [INFO] SIGNAL: [ModelHealth] date=2026-09-08 앙상블유효가동률=75.1% | 파이프라인 365분 | ConstOut 6회/11분 {"5m": {"events": 1, "minutes": 2}, "3m": {"events": 5, "minutes": 9}} | WeightCollapse 80분 | 장중재학습 7회 | CB③ ready 87분/365분 (24%) (리셋 3회, 표본손실 90건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1110 | 09:05:02 | 14:54:00 | 1m 'macro_krw_chg' scale=0.0979 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 196 | 09:05:01 | 14:51:00 | 1m 스케일러 1031분 미갱신 (≥90분) — 변동성 레짐 시프트 시 z-score 왜곡 가능 |
| `ScalerMonitor` | 156 | 09:05:01 | 14:53:00 | ts=09:04 horizon=1m age=1031m max_z=-30.99(queue_depletion_speed) extreme=8 adj=6 |
| `Checklist` | 91 | 09:16:00 | 15:00:00 | 신뢰도 미달 35.9% < 38.0% → 강제 X등급 |
| `WeightCollapse` | 81 | 09:06:04 | 15:09:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 6 | 10:04:00 | 14:19:00 | 5m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외 |
| `ConfFloorGuard` | 3 | 09:06:04 | 11:25:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3800 (conf_floor=0.330, min_conf=0.380, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `PCR-Dampen` | 2 | 09:18:00 | 09:31:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×5012

**컴포넌트 상위 15** — `ScalerFloor`×1110, `SIGNAL`×730, `ProfitGuard`×408, `MetaGate`×374, `Ensemble`×372, `FQAdj`×352, `ZeroDiag`×333, `Model`×244, `Checklist`×161, `ScalerMonitor`×157, `ATR-Horizon`×116, `차단`×91, `MicroRegime`×82, `WeightCollapse`×81, `InstabilityGate`×63

### `logs/20260908_LEARNING.log` — 286.8KB · 2801행 · 최종 15:40:29

- 형식 평문 · 시각 인식 2801행 · WARNING=164, INFO=2637

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2888 < conf_floor=0.3300 (span=0.00234 auc=0.639 out_max=0.2888, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00009 auc=0.506 out_max=0.2875 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
2026-09-08 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00011 auc=0.505 out_max=0.3218 (기준 auc<0.53 and span<0.020, 기저율=0.3217 n=115) → 보정 미적용, raw 통과
  …
2026-09-08 15:40:29 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-08 15:40:29 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-08 15:40:29 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-08 15:40:29 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-08 15:40:29 [INFO] LEARNING: [Sigma] EOD sigma_20=0.12716% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 162 | 08:40:52 | 13:20:02 | 축퇴 감지 — span=0.00035 auc=0.521 out_max=0.3476 (기준 auc<0.53 and span<0.020, 기저율=0.3474 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Buffer-Timing` | 1 | 13:20:02 | 13:20:02 | total=2723ms raw_fetch=1458ms pred_select=1112ms pred_update=29ms pred_insert=105ms verified=5 |
| `DriftAdjuster` | 1 | 15:40:29 | 15:40:29 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 9일) |

**채널** — `LEARNING`×2801

**컴포넌트 상위 15** — `LEARNING`×1195, `SGD`×365, `sigma`×352, `Calibration`×317, `Bias⚠`×161, `Bias`×122, `OnlineLearner`×89, `MetaConf`×78, `ScalerWarmup`×45, `BiasReset`×15, `GBM-64`×14, `GBM`×14, `SHAP`×11, `RF`×8, `ExtremityCorrector`×5

### `logs/20260908_HEALTH.log` — 8.9KB · 52행 · 최종 14:37:00

- 형식 평문 · 시각 인식 52행 · CRITICAL=11, WARNING=23, INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 09:06:05 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5090ms | quality=1.00 | cache_age=40s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
2026-09-08 09:07:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=524ms | quality=1.00 | cache_age=96s | exceptions_10m=4 | exc_tags=[LEVELS 수동]×3 [RESTART]×1
2026-09-08 09:19:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=373ms | quality=1.00 | cache_age=80s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2
2026-09-08 09:20:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=445ms | quality=1.00 | cache_age=140s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2
2026-09-08 09:21:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=516ms | quality=1.00 | cache_age=17s | exceptions_10m=25 | exc_tags=[OrderSync]×16 [ExternalEntry]×5 [ExitCooldown]×4
  …
2026-09-08 13:45:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=388ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-09-08 13:47:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=370ms | quality=1.00 | cache_age=180s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-08 13:48:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=333ms | quality=1.00 | cache_age=55s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-08 14:36:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=439ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-08 14:37:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=320ms | quality=1.00 | cache_age=58s | exceptions_10m=2 | exc_tags=[SHAP]×2
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
| `Health` | 23 | 09:19:00 | 14:36:00 | level=WARNING degraded=OFF | latency=373ms | quality=1.00 | cache_age=80s | exceptions_10m=6 | exc_tags=[OrderSync]×4 [ExternalEntry]×2 |

**채널** — `HEALTH`×52

**컴포넌트 상위 15** — `Health`×51, `HealthTrend`×1

### `logs/retrain_eod_20260908.log` — 20.8KB · 131행 · 최종 15:53:57

- 형식 평문 · 시각 인식 131행 · WARNING=18, INFO=113

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 15:50:03,756 [INFO] EOD_RETRAIN: =======================================================
2026-09-08 15:50:03,757 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-08 15:50:03,757 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-08 15:50:03,757 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-08 15:50:03,757 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-08 15:53:57,050 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0772 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-08 15:53:57,052 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1077 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-08 15:53:57,056 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-09-08 15:53:57,086 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-08 15:53:57,087 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:53 | 15:52:42 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-07 14:38:00까지)인데 acc.txt=0.3851는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:53 | 15:52:42 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1515봉(82%)이 현행 학습구간 (현행 cutoff=2026-09-07 14:38:00 ≥ 홀드아웃 시작=2026-09-01 12:44:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-07 14:38 >= holdout_start=2026-09-01 12:44 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-0… |

**채널** — `LEARNING`×74, `SIGNAL`×25, `EOD_RETRAIN`×24, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `ScalerFloor`×18, `EOD_RETRAIN`×14, `GuardGhost`×12, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×3, `WaitDC`×2

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

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +67967원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 7 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 7 |
| 청산(`체결청산`) | 6 |
| 차단(`[차단]`) | 91 |
| 사이저 호출(`[Sizer]`) | 27 |

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

### CB③ 판정 가능 시간 — **87분 / 365분 (24%)**

acc30m 버퍼 리셋 3회 · 그때 버린 표본 90건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×6, **2계약**×4, **3계약**×17

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×20, `conf=0.8 regime=0.8 safe=1.00`×5, `conf=1.2 regime=0.8 safe=1.00`×1, `conf=1.0 regime=0.8 safe=1.00`×1

### 차단 사유 91건 · 42종

| 건수 | 사유 |
|---|---|
| 29 | 등급X — 미통과 항목: 2_confidence |
| 13 | 게이트 강등 X — ProfitGuard 진입 차단 ([L1-Trail] 피크 +684,928원 대비 10% 하락 (현재 +524,940원 < 보호선 +616,… |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar, 10_chase |
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

**체크리스트 미통과 항목 누적** — `2_confidence`×29, `3_vwap`×7, `4_cvd`×5, `7_prev_bar`×5, `10_chase`×4, `5_ofi`×3, `6_foreign`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 3건

- `일간 리셋 완료` ×2
- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 23건 · 최대 9562ms · 5초 초과 5건

상위 — 9562ms, 8953ms, 7578ms, 6454ms, 5625ms, 4813ms, 4812ms, 4703ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:05:06 | 7578ms | **미측정** | — |
| 09:06:05 | 6454ms | 5090ms | **1364ms (21%)** |
| 09:30:05 | 5625ms | 432ms | **5193ms (92%)** |
| 12:24:08 | 9562ms | 373ms | **9189ms (96%)** |
| 13:20:08 | 8953ms | 3129ms | **5824ms (65%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260908_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:29 2026-09-08 15:40:29 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 36분/일 < 하한 60분 — 금일 32분. | ConfFloorGuard 도달가능 19분 · 도달불가 82분 · 재지않음 264분
--- ConstOut ×6(표본)
10:04:00 2026-09-08 10:04:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:10:01 2026-09-08 11:10:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:49:02 2026-09-08 11:49:02 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:29:00 2026-09-08 12:29:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×4(표본)
09:05:06 2026-09-08 09:05:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260908.log
09:30:05 2026-09-08 09:30:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260908.log
12:24:08 2026-09-08 12:24:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260908.log
13:20:08 2026-09-08 13:20:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260908.log
--- [Brier] 과신 ×1(표본)
14:33:00 2026-09-08 14:33:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.354 > 0.35
--- [CB] ×1(표본)
09:39:12 2026-09-08 09:39:12 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:20:19 2026-09-08 09:20:19 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:19)
09:20:19 2026-09-08 09:20:19 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:19)
09:20:27 2026-09-08 09:20:27 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:27)
09:20:27 2026-09-08 09:20:27 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:22:27)
--- [SHAP] 슬로우 ×8(표본)
11:42:01 2026-09-08 11:42:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 921ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:09:02 2026-09-08 12:09:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1018ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:26:03 2026-09-08 12:26:03 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1204ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:34:02 2026-09-08 12:34:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1104ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
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
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260908_SYSTEM.log`
```
--- ConstOut ×8(표본)
10:04:00 2026-09-08 10:04:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 10:06:00 (const_output)
10:04:00 2026-09-08 10:04:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['5m']
10:04:01 2026-09-08 10:04:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['5m'] load=110ms fit=82ms total=206ms
10:05:00 2026-09-08 10:05:00 [INFO] SYSTEM: [ConstOut] ['5m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:29 2026-09-08 15:40:29 [INFO] SYSTEM: [CB③계측] 조건성립 57분 / 판정가능 87분 / 파이프라인 365분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:05:00 2026-09-08 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:11:00 2026-09-08 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:17:00 2026-09-08 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:22:00 2026-09-08 09:22:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:29 2026-09-08 15:40:29 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:29 2026-09-08 15:40:29 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:28 2026-09-08 15:11:28 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:30 2026-09-08 15:40:30 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:45 2026-09-08 15:40:45 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:30 2026-09-08 15:40:30 [INFO] SYSTEM: [Notify] ℹ️ [15:40:30] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:30 2026-09-08 15:40:30 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:45 2026-09-08 15:40:45 [INFO] SYSTEM: [System] 자동 종료 실행
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
| 14:00 | 장중 후반 · 장중 재학습 | 4 | 13:56:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 2 | 15:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,477,106) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShad… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:29 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260908_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 1 | 08:41:11 [WARNING] _tick_header 간격 2219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2219 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 28 | 09:04:57 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 10:00 | 장중 초반 | 8 | 09:57:00 [WARNING] 5분 누적 수익률 +0.224% (임계 ±0.210%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 2 | 11:54:03 [WARNING] _tick_header 간격 3594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3594 band=… |
| 14:00 | 장중 후반 · 장중 재학습 | 7 | 13:54:01 [WARNING] 슬로우 감지 913ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1 | 15:06:01 [WARNING] 슬로우 감지 905ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 5 | 15:40:28 [ERROR] 🔴 오늘 외부 진입 총 7건 / 7계약 — 미륵이가 내지 않은 진입이다. 발생원(HTS·MTS·타 프로그램)을 확인할 것 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260908_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 12 | 08:40:35 [INFO] 활성화 | file=logs\crash_fault.log PID=23044 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 ⚠ | 0 | — |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 1237 | 09:04:57 [INFO] create begin progid=Dscbo1.CpFConclusion event=fill latest=False inputs={} |
| 10:00 | 장중 초반 | 4905 | 09:54:00 [INFO] code=A0569 raw_time=95359 price=1123.44 cum_vol=33472 auction_code=40 recv_type=50 |
| 12:00 | 장중 중간점 | 2734 | 11:54:00 [INFO] code=A0569 raw_time=115359 price=1128.08 cum_vol=69752 auction_code=40 recv_type=50 |
| 14:00 | 장중 후반 · 장중 재학습 | 5378 | 13:54:00 [INFO] code=A0569 raw_time=135400 price=1127.88 cum_vol=102994 auction_code=40 recv_type=50 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 5107 | 15:04:00 [INFO] code=A0569 raw_time=150359 price=1106.26 cum_vol=136411 auction_code=40 recv_type=49 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 3792 | 15:12:00 [INFO] code=A0569 raw_time=151159 price=1103.62 cum_vol=140144 auction_code=40 recv_type=50 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 170 | 15:34:00 [INFO] code=A0569 raw_time=153400 price=1099.42 cum_vol=146211 auction_code=40 recv_type=50 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 367/371분 (98.9%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 09:00 | 09:03 | 4 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260908_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:40:31 [INFO] 기동 복원: OPEN_VOLATILE  0.600 → 0.410 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:00:03 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 118 | 09:05:01 [WARNING] 1m 스케일러 1031분 미갱신 (≥90분) — 변동성 레짐 시프트 시 z-score 왜곡 가능 |
| 10:00 | 장중 초반 | 189 | 09:57:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 12:00 | 장중 중간점 | 130 | 11:54:00 [WARNING] 신뢰도 미달 33.4% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 239 | 13:54:00 [WARNING] 신뢰도 미달 36.3% < 44.8% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 60 | 15:06:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:29 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

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
| **오늘 20260908** | **15:40** | 로그 본문 |

- 델타 **-113분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.8MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 원인
### 결정
### Why
### How to apply
### 검증
### 부가 확인 — 이월 레그 1건 오버나이트 위반 여부
### 병행 세션
### 부가 발견 — `.git/index.lock` 세션 중 생성, 세션 내 회수 불가
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
하지 않는다 — `data/eod_retrain_done_20260907.txt`
`data/daily_close_done_20260907.txt` `data/shutdown_normal_20260907.txt` 세 마커 모두
09-07 15:40~15:53 정상 생성 확인(어제 EOD·P8은 성공, 오늘 마커만 유실됨).

### 병행 세션

이 세션이 도는 동안 병행 세션 없음(당일 커밋 0건, `docs/정기점검/매일점검/` 당일
산출물 이 리포트가 최초 — `git log --since` 및 `ls -lt` 로 확인).

## 2026-09-08 (MW0601 544차 — 장중 점검)

### 증상

09:18:50~09:39:12 사이 `[ExternalEntry]` ERROR 7건 재발(엔진 자체 진입은 0건). 그 사이
`[Health]` 레벨이 09:21:00~09:24:00 4회 `CRITICAL`로 올라감(`ExternalEntry`·`OrderSync`·
`ExitCooldown` 예외 누적). 포지션 5건(전량 「외부」 귀속) 합계 +72,991원, 이월 레그 1건
(-5,024원, 열림 로그 없어 귀속 불가)까지 포함하면 오늘 계좌 실제 손익 +67,967원.

### 원인

**신규 조사 불필요 — 이미 확정됨.** `NEXT_TODO.md` 531-1(09-01)→532-1(09-04)→536-1(09-07
장중)→**537-1(09-07 장후, ✅ 해소·P0 해제)**로 이어진 항목의 6거래일 연속 재발이다.
537-1이 "5거래일간(09-01·09-02·09-03·09-04·09-07) 전부 사용자 본인의 모의투자 병행
수동 테스트 거래"로 이미 원인을 확정했다. 오늘도 같은 시간대(09:18~09:39) 클러스터,
같은 패턴(`[PositionFallback]` TP1 배수 1.00 폴백 동반)으로 재현돼 같은 원인으로 판정한다.

### 결정

**이상점 번호만 부여(1-2)하고 원인 재조사는 하지 않는다.** 함정①(판정≠결정) 반대
방향 오류를 피하기 위해 — 이미 닫힌 항목을 신규로 다시 여는 것도, 재발 사실 자체를
기록하지 않는 것도 둘 다 오류다. 재발 사실만 남기고 심각도는 P2(원인 기지·오늘 이익
마감·15:10 훨씬 전 종결)로 낮춰 기록한다.

### Why

- 313차/함정① 원칙 — 이미 확정된 원인을 매번 "미규명"으로 되돌리면 다음 세션이 또
  조사 자원을 낭비한다.
- 그렇다고 재발 사실 자체를 누락하면 G-2(경보 격상)·G-4(알려진 활동 태깅) 정책이
  언제 발동 조건을 충족하는지(누적 건수·거래일수) 추적이 끊긴다.

### How to apply

- 코드 변경 없음. `dev_memory/NEXT_TODO.md`에 6거래일 연속 재발 사실만 기록.
- G-2·G-4는 여전히 주간회의/사용자 지시 대기 상태 그대로 둔다.

### 검증

- 다음 거래일 재발 여부는 그날 장중 점검이 같은 방식(원인 재조사 없이 재발 사실만
  기록)으로 이어받을 것.

### 부가 확인 — 이월 레그 1건 오버나이트 위반 여부

09:20:44 청산된 이월 레그(+0.12pt, -5,024원)는 오늘 열림 로그가 없어 조립 불가했다.
같은 시간대(09:20대) 클러스터에 속해 있고, 09-07 리포트가 15:10 시점 FLAT을
`[SchedForceExit] 15:11:06 status=FLAT engine=0ct broker_cached=0ct`로 이미 확인해뒀으므로
09-07 오버나이트(절대원칙 ① 위반)는 아니라고 판단한다. 확정을 원하면 `trades.db`에서
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

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-04 (MW0601 531차 — 장중 점검)
## 2026-09-04 (MW0601 532차 — 장후 점검)
## 2026-09-04 (MW0601 532차 후속 — 장후 자동조치)
## 2026-09-07 (MW0601 536차 — 장중 점검)
## 2026-09-07 (MW0601 537차 — 장후 점검, 종합 완성본)
## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)
## 2026-09-08 (MW0601 543차 — 장전 점검)
## 2026-09-08 (MW0601 544차 — 장중 점검)
```

미완료 체크박스 **2517건** (끝에서 30건)
```
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
- [ ] **544-2 (장후 확인 필요)** 09:20:44 청산 이월 레그 1건(-5,024원, 오늘 열림 로그
- [ ] **544-5 (사용자 조치)** `.git/index.lock` 12:27:38 생성 — 12:38 재판정 결과
- [ ] **544-6 (P2, 고도화 제안)** `collect_evidence.py`의 "이 수집 실행은 락을
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
MW0601 543차 — 장전 점검)

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

### `data/heartbeat_MW0601_20260908.json` — 244B · 09-08 15:40:42
```json
{
 "pid": 23044,
 "written_at": "2026-09-08T15:40:42",
 "beat_epoch": 1788849638.4867973,
 "beat_age_sec": 4.4,
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

- 파일 최종 기록: **09-08 15:53:57**

| 키 | 값 | 수집 대상일(2026-09-08)과 일치 |
|---|---|---|
| `date` | 2026-09-08 | 예 |
| `p8_last_success_date` | 2026-09-08 | 예 |
| `eod_retrain_ok_date` | 2026-09-08 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 118개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260908-점검리포트.md` | 31.5KB | 09-08 12:38 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_intra.md` | 76.5KB | 09-08 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_pre.md` | 43.0KB | 09-08 09:02 |
| `docs/정기점검/매일점검/MW0601-20260907-점검리포트.md` | 95.0KB | 09-07 17:42 |
| `docs/정기점검/매일점검/MW0601-20260907-BLAS즉사-딥다이브.md` | 13.2KB | 09-07 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_post.md` | 91.6KB | 09-07 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_intra.md` | 77.5KB | 09-07 12:27 |
| `docs/정기점검/매일점검/MW0601-20260907-맥점계측-딥다이브.md` | 10.1KB | 09-07 09:14 |

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

1. `logs/20260908_WARN.log`: ERROR 이상 20건
2. `logs/20260908_WARN.log`: **Traceback** 출현 4건 — 크래시/메모리 계열
3. `logs/20260908_SYSTEM.log`: 09:00~09:03 **연속 4분 매분 루프 기록 없음**
4. `logs/20260908_HEALTH.log`: ERROR 이상 11건
5. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
6. **엔진 진입 0건 / 계좌 진입 7건**(그중 외부표식 7건) — 차단 91건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
7. 다레그 포지션 **1건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
8. **SYSTEM 로그가 직전 5거래일 중앙값(17:33)보다 113분 이르게 끝났다** (오늘 15:40) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
9. 메인 스레드 정지 5초 초과 **5건** (최대 9562ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
10. `logs/20260908_WARN.log`: **[Brier] 과신** 1건(표본)
11. `logs/20260908_WARN.log`: **level=CRITICAL** 1건(표본)
12. `logs/20260908_WARN.log`: **ConstOut** 6건(표본)
13. `logs/20260908_SYSTEM.log`: **ConstOut** 8건(표본)
14. `logs/20260908_SIGNAL.log`: **WeightCollapse** 8건(표본)
15. `logs/20260908_SIGNAL.log`: **ConstOut** 8건(표본)
16. `logs/20260908_LEARNING.log`: **축퇴** 8건(표본)
17. `logs/20260908_HEALTH.log`: **level=CRITICAL** 1건(표본)
18. 미커밋 변경 552건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
19. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260908*.log` (Windows) / `grep 강제청산 logs/*20260908*.log`*