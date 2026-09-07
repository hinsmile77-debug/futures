# 미륵이 증거 다이제스트 — 2026-09-07 / POST

- 생성 2026-09-07 16:17:46 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/affectionate-nifty-cori/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260907` · `2026-09-07` · `260907` · `0907`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **30개** 파일 · 30개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260907.txt` | 28B | 09-07 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260907.txt` | 28B | 09-07 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260907.txt` | 209B | 09-07 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260907.log` | 1.4KB | 09-07 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260907.log` | 216B | 09-07 15:45 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260907.json` | 244B | 09-07 15:40 |
| `launcher_{DATE}_084001_9239.log` | 1 | `logs/Mireuk_batch/launcher_20260907_084001_9239.log` | 14.9MB | 09-07 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260907.log` | 11.4KB | 09-07 15:06 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260907.log` | 20.1KB | 09-07 15:53 |
| `retrain_intraday_{DATE}_095500.log` | 1 | `logs/retrain_intraday_20260907_095500.log` | 2.7KB | 09-07 09:55 |
| `retrain_intraday_{DATE}_111200.log` | 1 | `logs/retrain_intraday_20260907_111200.log` | 2.7KB | 09-07 11:12 |
| `retrain_intraday_{DATE}_115100.log` | 1 | `logs/retrain_intraday_20260907_115100.log` | 2.7KB | 09-07 11:51 |
| `retrain_intraday_{DATE}_123000.log` | 1 | `logs/retrain_intraday_20260907_123000.log` | 2.7KB | 09-07 12:30 |
| `retrain_intraday_{DATE}_132201.log` | 1 | `logs/retrain_intraday_20260907_132201.log` | 2.7KB | 09-07 13:22 |
| `retrain_intraday_{DATE}_141501.log` | 1 | `logs/retrain_intraday_20260907_141501.log` | 2.7KB | 09-07 14:15 |
| `retrain_intraday_{DATE}_145400.log` | 1 | `logs/retrain_intraday_20260907_145400.log` | 2.7KB | 09-07 14:54 |
| `retrain_intraday_{DATE}_161553.log` | 1 | `logs/retrain_intraday_20260907_161553.log` | 453B | 09-07 16:15 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260907.txt` | 43B | 09-07 15:40 |
| `strategy_report_{DATE}_154010.txt` | 1 | `data/daily_reports/strategy_report_20260907_154010.txt` | 2.2KB | 09-07 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260907_DATA.log` | 346.1KB | 09-07 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260907_DEBUG.log` | 233.6KB | 09-07 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260907_HEALTH.log` | 23.7KB | 09-07 14:56 |
| `{DATE}_HOGA.log` | 1 | `logs/20260907_HOGA.log` | 44.5MB | 09-07 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260907_LEARNING.log` | 287.2KB | 09-07 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260907_MICRO.log` | 908.6KB | 09-07 15:37 |
| `{DATE}_PROBE.log` | 1 | `logs/20260907_PROBE.log` | 96.6KB | 09-07 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260907_SIGNAL.log` | 467.0KB | 09-07 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260907_SYSTEM.log` | 14.0MB | 09-07 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260907_TRADE.log` | 49.8KB | 09-07 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260907_WARN.log` | 238.6KB | 09-07 15:40 |

## 2. 코드·커밋 상태

- HEAD `4bb2dd3` · 브랜치 `v9-dev` · 미커밋 529건 · 실질 변경 14건 · 코드(.py) 12건 · EOL 파생 507건 (추적변경 521 · 미추적 8 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 7.3시간 · git 프로세스 0개 → **커밋 불가 상태**
  - 실질 변경 파일: `dashboard/main_dashboard.py`, `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `features/levels/levels_store.py`, `features/levels/premarket_levels.py`, `main.py`, `retrain_intraday.py`, `scripts/core_feature_discovery.py`, `scripts/eod_retrain.py`, `scripts/feature_ablation_purged_cv.py`, `scripts/validate_feature_set_purged_cv.py`, `tests/test_534_premarket_levels.py` … 외 2개
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
… 외 489건
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

_본문 미열람(설정): `20260907_HOGA.log` 44.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260907.txt`** — 28B · 09-07 15:40:10
```
2026-09-07T15:40:10.791468
```

**`data/daily_close_started_20260907.txt`** — 28B · 09-07 15:40:06
```
2026-09-07T15:40:06.471280
```

**`data/daily_reports/strategy_report_20260907_154010.txt`** — 2.2KB · 09-07 15:40:10
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-07 15:40
========================================================
  버전    : v1.0  (74일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-5.46  MDD(자본대비)=29.8%
  당일      : WR=42.1%  PF=0.18
  롤링20일: 누적 -12885332원  Sh=-5.46  MDD(자본대비)=29.8%  MDD(peak대비)=743.4%
  당일손익 : broker(gross) -1,045,999원  수수료 386,575원  net -1,432,575원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.005 (CLEAR)
  PSI/feat: cvd_delta=0.005  ofi_pressure=0.001  vwap_position=0.104
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -10,462원  승률 50.0%  합계 -209,234원
  등급별 순EV(30일): A=-711원(100건,승62%)  BROKER=-5,380,798원(2건,승0%)  C=-2,922원(11건,승73%)  MANUAL=-19,418원(159건,승48%)
  호라이즌별 순EV(30일): 1m=-6,825원(19건)  3m=-10,839원(71건)  5m=+30,978원(19건)  ?=-83,691원(163건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 26분  5일평균 31분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 20.2pt(5일평균 29.5pt)  1분평균변동 0.51pt(5일평균 0.74pt)
--------------------------------------------------------
  진입 퍼널(2026-09-07, 총 370분):
    FLAT 277 → conf미달 61 → CoherenceGate 6 → 게이트차단 21 → 후보 5 → 진입 5
    └ 등급상향경로(앙상블X→체크리스트통과): 1건 [285차-P5]
    게이트별: 포지션보유중(평가생략)=7  ATR변동성=7  쿨다운=5  체크리스트항목미달=1  콜드스타트/기타(RegimeOverride)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260907.txt`** — 209B · 09-07 15:53:50
```
completed: 2026-09-07 15:53:50
rows: 40843
cols: 97
horizons_replaced: 6/6
t_load_s: 34.4
t_retrain_s: 193.4
t_total_s: 228.3
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260907.txt`** — 43B · 09-07 15:40:25
```
auto_shutdown
2026-09-07T15:40:25.799229
```

_다이제스트 대상 8/23개 (중요도순). 제외: `retrain_intraday_20260907_115100.log`, `retrain_intraday_20260907_123000.log`, `retrain_intraday_20260907_132201.log`, `retrain_intraday_20260907_141501.log`, `retrain_intraday_20260907_145400.log`, `retrain_intraday_20260907_095500.log`, `retrain_intraday_20260907_161553.log`, `20260907_MICRO.log`_

### `logs/20260907_TRADE.log` — 49.8KB · 369행 · 최종 15:40:07

- 형식 평문 · 시각 인식 369행 · WARNING=29, INFO=340

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-07 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-07 09:23:20 [INFO] TRADE: [Chejan] 상태=접수 주문번호=720 code=A0569 방향=SHORT 체결=3 미체결=0
2026-09-07 09:23:21 [INFO] TRADE: [Chejan] 상태=체결 주문번호=720 code=A0569 방향=SHORT 체결=1 미체결=0
2026-09-07 09:23:21 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1089.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
  …
2026-09-07 14:44:16 [INFO] TRADE: [체결청산-부분] SHORT 1계약 @ 1103.60 | PnL=-0.88pt (-54,818원) | 잔여=1계약 | 사유=하드스톱(틱)
2026-09-07 14:44:17 [INFO] TRADE: [Chejan] 상태=체결 주문번호=4878 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-07 14:44:17 [INFO] TRADE: [Position] 체결청산 SHORT @ 1103.6 | PnL=-0.88pt (-54,818원) | 하드스톱(틱)
2026-09-07 14:44:17 [INFO] TRADE: [청산 완료] PnL=-0.88pt (-164,454원) | 포지션 합계 -164,454원 (레그 3)
2026-09-07 15:40:07 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 29 | 09:23:21 | 14:39:09 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1089.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×369

**컴포넌트 상위 15** — `Chejan`×114, `Position`×83, `체결동기화`×31, `PositionFallback`×29, `주문요청`×26, `청산 완료`×19, `TickStop-S0C`×17, `Sizer`×14, `체결청산-부분`×13, `TickTP1`×8, `진입체크`×5, `체결진입`×5, `ProfitGuard`×2, `TP1 부분청산`×2, `TP2 부분청산`×1

### `logs/20260907_WARN.log` — 238.6KB · 1114행 · 최종 15:40:10

- 형식 평문 · 시각 인식 1107행 · CRITICAL=39, ERROR=33, WARNING=1035, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-07 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-07 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 156ms account=333044256
2026-09-07 08:41:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3547 band=INFO since_pipe_s=NA
2026-09-07 08:41:10 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -1432575원
════════════════════════════════════════════════════
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 39 | 09:31:00 | 14:47:00 | level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1 |
| ERROR | `ExternalEntry` | 32 | 09:23:21 | 15:40:06 | 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.72 (보유 1계약, 평균 1089.72). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다 |
| ERROR | `LiveDBG` | 1 | 09:00:28 | 09:00:28 | _tick_header 간격 28797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=28797 band=ALERT since_pipe_s=0.3 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-07 09:31:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
2026-09-07 09:32:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=329ms | quality=1.00 | cache_age=126s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
```

</details>

<details><summary>ERROR/ExternalEntry 원문 2건</summary>

```
2026-09-07 09:23:21 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.72 (보유 1계약, 평균 1089.72). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
2026-09-07 09:23:21 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1089.76 (보유 2계약, 평균 1089.74). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-07 09:00:28 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 28797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=28797 band=ALERT since_pipe_s=0.3
```

</details>

**WARNING — 태그 36종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 326 | 08:41:06 | 15:06:06 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 114 | 09:23:20 | 14:44:17 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1089.62 | fill_qty=3 | gubun='0' | order_no='720' | pending='NONE' | position='FLAT' | position_qty=0 | sell_balance=0 | side='SHORT' |… |
| `ChejanMatch` | 114 | 09:23:20 | 14:44:17 | order_no='720' | pending='NONE' | pending_matched=False |
| `Health` | 66 | 09:00:05 | 14:55:10 | level=WARNING degraded=OFF | latency=4962ms | quality=0.86 | cache_age=49s | exceptions_10m=0 |
| `OrderSync` | 66 | 09:23:21 | 14:39:09 | 미추적 체결 감지 (pending_miss) order_no=720 side=SHORT qty=1 price=1089.72 before=FLAT |
| `PendingOrder` | 52 | 09:26:27 | 14:44:17 | set {'kind': 'EXIT_FULL', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1091.98, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no':… |
| `ExitCooldown` | 38 | 09:26:28 | 14:44:17 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:29:28) |
| `ExitFillFlow` | 30 | 09:26:28 | 14:44:17 | after='SHORT 2계약 @ 1089.75' | before='SHORT 3계약 @ 1089.75' | fill_price=1091.92 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:SHORT qty=3 filled=1 order_no=772 reason=하드스톱(틱) req_at=09:26:27.887' | reason='하드스톱(틱)' |
| `SHAP` | 27 | 11:33:01 | 15:03:02 | 슬로우 감지 965ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `PipePerf` | 20 | 09:00:05 | 14:55:10 | total=4962ms | S0=10ms S1=85ms S2=0ms S3=0ms S4=1313ms S5=1216ms S6=1996ms S7=308ms S8=34ms |
| `CB⑤` | 20 | 09:00:05 | 14:55:10 | 파이프라인 4962ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ExitSendOrderResult` | 18 | 09:26:27 | 14:44:16 | ret=0 kind=하드스톱(틱) direction=SHORT qty=3 |

**채널** — `SYSTEM`×1002, `HEALTH`×105

**컴포넌트 상위 15** — `LiveDBG`×327, `ChejanFlow`×114, `ChejanMatch`×114, `Health`×105, `OrderSync`×66, `PendingOrder`×52, `ExitCooldown`×38, `ExternalEntry`×32, `ExitFillFlow`×30, `SHAP`×27, `PipePerf`×20, `CB⑤`×20, `ExitSendOrderResult`×18, `HealthPolicy`×17, `TickStop`×17

### `logs/20260907_SYSTEM.log` — 14.0MB · 105536행 · 최종 15:40:25

- 형식 평문 · 시각 인식 105515행 · INFO=105515, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=11116 | 행감지=30s all_threads=True
2026-09-07 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-07 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-07 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-07 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-04) 종가 버퍼 로드: 384봉
  …
2026-09-07 15:40:10 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-07 15:40:10 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-07 15:40:25 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-07 15:40:25 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-07 15:40:25 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×105515

**컴포넌트 상위 15** — `CybosRT-AUCTION`×99018, `CybosInvestorRaw`×1574, `CybosRT-TICK`×995, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `BalanceUI`×232, `CybosEvent`×228, `CybosDailyPnl`×196, `BalanceRefresh`×158, `MicroRegime`×119, `System`×98

### `logs/20260907_SIGNAL.log` — 467.0KB · 4203행 · 최종 15:40:07

- 형식 평문 · 시각 인식 4203행 · WARNING=1349, INFO=2854

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.418
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-09-07 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-09-07 15:10:00 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-07 15:40:07 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-07 15:40:07 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 101분(27.3%) / DN 68분(18.4%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-07 15:40:07 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-07 age=27m extreme=320 refresh=35 grade_x=40 cb3=0
2026-09-07 15:40:07 [INFO] SIGNAL: [ModelHealth] date=2026-09-07 앙상블유효가동률=74.6% | 파이프라인 370분 | ConstOut 7회/13분 {"5m": {"events": 1, "minutes": 2}, "3m": {"events": 6, "minutes": 11}} | WeightCollapse 81분 | 장중재학습 7회 | CB③ ready 107분/370분 (29%) (리셋 3회, 표본손실 90건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 948 | 09:00:06 | 14:53:01 | 1m 'macro_vix' scale=0.0036 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 146 | 09:01:00 | 14:36:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 104 | 09:01:00 | 14:36:00 | ts=09:00 horizon=1m age=1m max_z=+5.71(volume_acceleration) extreme=2 adj=1 |
| `WeightCollapse` | 81 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 50 | 09:06:00 | 14:47:00 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `ScalerRefresh` | 12 | 08:45:07 | 08:45:07 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 7 | 09:54:00 | 14:53:00 | 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:02 | 09:00:02 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4203

**컴포넌트 상위 15** — `ScalerFloor`×996, `SIGNAL`×740, `Ensemble`×373, `FQAdj`×357, `ZeroDiag`×346, `MetaGate`×287, `Model`×194, `InstabilityGate`×143, `MicroRegime`×119, `ScalerMonitor`×105, `ATR-Horizon`×82, `WeightCollapse`×81, `Checklist`×80, `ScalerRefresh`×53, `차단`×46

### `logs/20260907_LEARNING.log` — 287.2KB · 2808행 · 최종 15:40:07

- 형식 평문 · 시각 인식 2808행 · WARNING=165, INFO=2643

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.500 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.395 out_max=0.1252 (기준 auc<0.53 and span<0.020, 기저율=0.1250 n=80) → 보정 미적용, raw 통과
2026-09-07 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.513 out_max=0.2751 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
2026-09-07 08:40:50 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00048 auc=0.543 out_max=0.1288 (n=140) → 보정 재적용
  …
2026-09-07 15:40:07 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-07 15:40:07 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-07 15:40:07 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-07 15:40:07 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-07 15:40:07 [INFO] LEARNING: [Sigma] EOD sigma_20=0.04386% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 163 | 08:40:50 | 12:13:00 | 축퇴 감지 — span=0.00021 auc=0.500 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Retrain` | 1 | 15:40:07 | 15:40:07 | DB pruning 실패: database table is locked |
| `DriftAdjuster` | 1 | 15:40:07 | 15:40:07 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 8일) |

**채널** — `LEARNING`×2808

**컴포넌트 상위 15** — `LEARNING`×1207, `SGD`×370, `sigma`×357, `Calibration`×317, `Bias⚠`×173, `Bias`×118, `MetaConf`×76, `OnlineLearner`×68, `ScalerWarmup`×41, `BiasReset`×18, `GBM`×15, `GBM-64`×14, `SHAP`×11, `RF`×8, `ExtremityCorrector`×5

### `logs/20260907_HEALTH.log` — 23.7KB · 124행 · 최종 14:56:00

- 형식 평문 · 시각 인식 124행 · CRITICAL=39, WARNING=66, INFO=19

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 09:00:05 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=4962ms | quality=0.86 | cache_age=49s | exceptions_10m=0
2026-09-07 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=620ms | quality=0.86 | cache_age=104s | exceptions_10m=0
2026-09-07 09:24:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=319ms | quality=1.00 | cache_age=13s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
2026-09-07 09:25:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=399ms | quality=1.00 | cache_age=74s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
2026-09-07 09:26:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=330ms | quality=1.00 | cache_age=133s | exceptions_10m=9 | exc_tags=[OrderSync]×6 [ExternalEntry]×3
  …
2026-09-07 14:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=476ms | quality=1.00 | cache_age=159s | exceptions_10m=11 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1 외 1종
2026-09-07 14:49:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=383ms | quality=1.00 | cache_age=35s | exceptions_10m=11 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1 외 1종
2026-09-07 14:50:00 [INFO] HEALTH: [Health] level=INFO degraded=ON | latency=515ms | quality=1.00 | cache_age=96s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
2026-09-07 14:55:10 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2588ms | quality=1.00 | cache_age=38s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-07 14:56:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=652ms | quality=1.00 | cache_age=88s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 39 | 09:31:00 | 14:47:00 | level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-07 09:31:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=393ms | quality=1.00 | cache_age=66s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
2026-09-07 09:32:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=329ms | quality=1.00 | cache_age=126s | exceptions_10m=19 | exc_tags=[OrderSync]×12 [ExternalEntry]×6 [ExitCooldown]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 66 | 09:00:05 | 14:55:10 | level=WARNING degraded=OFF | latency=4962ms | quality=0.86 | cache_age=49s | exceptions_10m=0 |

**채널** — `HEALTH`×124

**컴포넌트 상위 15** — `Health`×123, `HealthTrend`×1

### `logs/retrain_eod_20260907.log` — 20.1KB · 135행 · 최종 15:53:51

- 형식 평문 · 시각 인식 135행 · WARNING=10, INFO=125

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-07 15:50:02,083 [INFO] EOD_RETRAIN: =======================================================
2026-09-07 15:50:02,083 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-07 15:50:02,083 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-07 15:50:02,083 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-07 15:50:02,084 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-07 15:53:51,117 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0676 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-07 15:53:51,118 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0876 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-07 15:53:51,120 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-09-07 15:53:51,125 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-07 15:53:51,126 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:43 | 15:52:35 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1500봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-04 14:38:00 ≥ 홀드아웃 시작=2026-08-31 12:59:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-04 14:38 >= holdout_start=2026-08-31 12:59 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-04 … |
| `GuardGhost` | 4 | 15:50:54 | 15:51:06 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-07 14:23:00까지)인데 acc.txt=0.3717는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×66, `SIGNAL`×37, `EOD_RETRAIN`×24, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×30, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `GuardGhost`×4, `RegimeFingerprint`×3, `WaitDC`×2

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

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -1432575원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 5 |
| 진입 등록(`[Position] 진입`) — **엔진** | 5 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 36 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 31 |
| 청산(`체결청산`) | 19 |
| 차단(`[차단]`) | 46 |
| 사이저 호출(`[Sizer]`) | 14 |

### 포지션 19건 · 승 5 (26%) · 합계 -20.92pt (-1,432,578원)  ※ 레그 35행

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
| 12:30:03 (추정귀속) | 외부 | LONG | 1 | — | 1 | +0.08 | -6,721 | 하드스톱(틱) |
| 13:09:56 (추정귀속) | 외부 | LONG | 1 | — | 1 | -0.86 | -53,754 | 하드스톱(틱) |
| 13:38:01 | 엔진 | LONG | 1 | 3m | 1 | +0.20 | -780 | 하드스톱(틱) |
| 14:08:18 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -2.27 | -146,338 | 하드스톱(틱) |
| 14:16:53 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -2.73 | -169,341 | 하드스톱(틱) |
| 14:23:53 (추정귀속) | 외부 | SHORT | 3 | — | 2 | -2.58 | -161,423 | 하드스톱(틱) |
| 14:33:42 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +1.48 | +41,513 | 하드스톱 |
| 14:39:09 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -2.64 | -164,454 | 하드스톱(틱) |

**출처별 소계** — 엔진 5건 -79,471원 · 외부 14건 -1,353,107원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 14건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 35행** (부분청산 16 · 전량청산 19)

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
| 12:33:55 | 전량 | 1 | +0.08 | -6,721 | 하드스톱(틱) |
| 13:12:07 | 전량 | 1 | -0.86 | -53,754 | 하드스톱(틱) |
| 13:39:20 | 전량 | 1 | +0.20 | -780 | 하드스톱(틱) |
| 14:10:22 | 부분 | 1 | -0.81 | -51,446 | 하드스톱(틱) |
| 14:10:22 | 부분 | 1 | -0.75 | -48,446 | 하드스톱(틱) |
| 14:10:22 | 전량 | 1 | -0.71 | -46,446 | 하드스톱(틱) |
| 14:17:25 | 부분 | 1 | -0.85 | -53,447 | 하드스톱(틱) |
| 14:17:25 | 부분 | 1 | -0.91 | -56,447 | 하드스톱(틱) |
| 14:17:25 | 전량 | 1 | -0.97 | -59,447 | 하드스톱(틱) |
| 14:25:01 | 부분 | 1 | -0.86 | -53,808 | 하드스톱(틱) |
| 14:25:01 | 전량 | 2 | -0.86 | -107,615 | 하드스톱(틱) |
| 14:34:55 | 부분 | 1 | +0.56 | +17,171 | TP1 부분청산 33% |
| 14:35:00 | 부분 | 1 | +0.46 | +12,171 | 하드스톱 |
| 14:35:00 | 전량 | 1 | +0.46 | +12,171 | 하드스톱 |
| 14:44:16 | 부분 | 1 | -0.88 | -54,818 | 하드스톱(틱) |
| 14:44:16 | 부분 | 1 | -0.88 | -54,818 | 하드스톱(틱) |
| 14:44:17 | 전량 | 1 | -0.88 | -54,818 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×28, `TP1 부분청산 33%`×2, `미추적체결(pending_miss)`×2, `하드스톱`×2, `TP2 부분청산 33%`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 18/19건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -1,432,578 = 포지션합 -1,432,578 → OK · `[청산 완료]` 19건 = 조립 포지션 19건 → OK

### CB③ 판정 가능 시간 — **107분 / 370분 (29%)**

acc30m 버퍼 리셋 3회 · 그때 버린 표본 90건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 5건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:18:01 | SHORT | 1 | 1087.84 | 3m | mean-revert |
| 10:39:01 | SHORT | 1 | 1088.5 | 1m | mean-revert |
| 10:49:02 | SHORT | 1 | 1088.56 | 1m | mean-revert |
| 11:08:01 | SHORT | 1 | 1086.5 | 5m | mean-revert |
| 13:38:01 | LONG | 1 | 1098.88 | 3m | mean-revert |

계약수 분포 — 1계약×5

등급 분포 — `A급(원시C)`×4, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×4, `ofi`×3, `prev`×2, `cvd`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×10, **2계약**×4

실제 진입 계약수 — **1계약**×5

> ⚠ 사이저는 최대 **2계약**을 냈는데 실제 진입 최대는 **1계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×14

### 차단 사유 46건 · 36종

| 건수 | 사유 |
|---|---|
| 4 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 3 | ATR 0.71pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 청산 후 쿨다운 — 42초 후 재진입 가능 |
| 2 | 등급X — 미통과 항목: 2_confidence |
| 2 | ATR 1.00pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.86pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 27초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 142초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 22초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 1 | 청산 후 쿨다운 — 93초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 59초 후 재진입 가능 |
| 1 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 75초 후 재진입 가능 |
| 1 | ATR 0.70pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.80pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 102초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 114초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×2, `3_vwap`×1, `4_cvd`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 13건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×11
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 24건 · 최대 28797ms · 5초 초과 4건

상위 — 28797ms, 6203ms, 5375ms, 5344ms, 4562ms, 4484ms, 4375ms, 4359ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:28 | 28797ms | 4962ms | **23835ms (83%)** |
| 14:48:04 | 5375ms | 476ms | **4899ms (91%)** |
| 14:56:04 | 5344ms | 2588ms | **2756ms (52%)** |
| 15:06:06 | 6203ms | 455ms | **5748ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260907_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:09 2026-09-07 15:40:09 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 31분/일 < 하한 60분 — 금일 26분. | ConfFloorGuard 도달가능 0분 · 도달불가 84분 · 재지않음 286분
--- ConstOut ×7(표본)
09:54:00 2026-09-07 09:54:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:11:01 2026-09-07 11:11:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:50:00 2026-09-07 11:50:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:29:00 2026-09-07 12:29:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×4(표본)
09:00:28 2026-09-07 09:00:28 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260907.log
14:48:04 2026-09-07 14:48:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260907.log
14:56:04 2026-09-07 14:56:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260907.log
15:06:06 2026-09-07 15:06:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260907.log
--- [CB] ×8(표본)
09:26:28 2026-09-07 09:26:28 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:48:10 2026-09-07 09:48:10 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:14:23 2026-09-07 10:14:23 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:15:02 2026-09-07 11:15:02 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:26:28 2026-09-07 09:26:28 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:29:28)
09:26:28 2026-09-07 09:26:28 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:29:28)
09:27:00 2026-09-07 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=401ms | quality=1.00 | cache_age=10s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
09:28:00 2026-09-07 09:28:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=310ms | quality=1.00 | cache_age=70s | exceptions_10m=10 | exc_tags=[OrderSync]×6 [ExternalEntry]×3 [ExitCooldown]×1
--- [ExitStageRecon] ×1(표본)
15:40:07 2026-09-07 15:40:07 [WARNING] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 13레그 / 13포지션 중 TP 이벤트 대응 2 · 단일계약 보호전환(설계) 5 · 미대응 6 ⚠ 미대응 합계 -1,363,587원 (진입 09:23:21, 10:02:42, 14:08:18, 14:16:53, 14:23:53 외 1건). 이 레그들은 라벨상 …
--- [SHAP] 슬로우 ×8(표본)
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
--- 메인 스레드 블로킹 ×8(표본)
08:41:10 2026-09-07 08:41:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3547 band=INFO since_pipe_s=NA
09:00:28 2026-09-07 09:00:28 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 28797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=28797 band=ALERT since_pipe_s=0.3
09:05:03 2026-09-07 09:05:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3750 band=INFO since_pipe_s=0.2
09:15:04 2026-09-07 09:15:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3969ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3969 band=INFO since_pipe_s=0.2
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260907_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:54:00 2026-09-07 09:54:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:56:00 (const_output)
09:54:00 2026-09-07 09:54:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['5m']
09:54:01 2026-09-07 09:54:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['5m'] load=95ms fit=71ms total=168ms
09:55:00 2026-09-07 09:55:00 [INFO] SYSTEM: [ConstOut] ['5m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:07 2026-09-07 15:40:07 [INFO] SYSTEM: [CB③계측] 조건성립 64분 / 판정가능 107분 / 파이프라인 370분 · 그 창 진입 3포지션 · 손익 -283,903원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-07 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:06:00 2026-09-07 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:12:00 2026-09-07 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:18:00 2026-09-07 09:18:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:07 2026-09-07 15:40:07 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:07 2026-09-07 15:40:07 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:06 2026-09-07 15:11:06 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:10 2026-09-07 15:40:10 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:25 2026-09-07 15:40:25 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:10 2026-09-07 15:40:10 [INFO] SYSTEM: [Notify] ℹ️ [15:40:10] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:10 2026-09-07 15:40:10 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:25 2026-09-07 15:40:25 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260907_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:02 2026-09-07 09:00:02 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
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
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:07 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260907_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 9 | 08:41:06 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:07 [WARNING] scaler 노후=0h  z경고피처=16개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:07 [WARNING] scaler 노후=0h  z경고피처=16개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 43 | 09:54:00 [WARNING] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| 12:00 | 장중 중간점 | 3 | 11:54:01 [WARNING] 슬로우 감지 1050ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| 14:00 | 장중 후반 · 장중 재학습 | 4 | 13:59:01 [WARNING] 슬로우 감지 1073ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 2 | 15:06:06 [WARNING] _tick_header 간격 6203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6203 band=… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:06 [ERROR] 🔴 오늘 외부 진입 총 31건 / 31계약 — 미륵이가 내지 않은 진입이다. 발생원(HTS·MTS·타 프로그램)을 확인할 것 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260907_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 837 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=11116 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2972 | 08:49:00 [INFO] code=A0569 raw_time=84859 price=1089.08 cum_vol=1399 auction_code=40 recv_type=50 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5119 | 08:54:00 [INFO] code=A0569 raw_time=85400 price=1090.16 cum_vol=2198 auction_code=40 recv_type=49 |
| 10:00 | 장중 초반 | 5094 | 09:54:00 [INFO] code=A0569 raw_time=95400 price=1088.58 cum_vol=24783 auction_code=40 recv_type=49 |
| 12:00 | 장중 중간점 | 2456 | 11:54:00 [INFO] code=A0569 raw_time=115359 price=1088.76 cum_vol=51625 auction_code=40 recv_type=50 |
| 14:00 | 장중 후반 · 장중 재학습 | 3716 | 13:54:00 [INFO] code=A0569 raw_time=135400 price=1101.86 cum_vol=83373 auction_code=40 recv_type=49 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 2477 | 15:04:00 [INFO] code=A0569 raw_time=150359 price=1103.64 cum_vol=102612 auction_code=40 recv_type=50 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 2357 | 15:12:00 [INFO] code=A0569 raw_time=151200 price=1104.00 cum_vol=104356 auction_code=40 recv_type=50 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 228 | 15:34:00 [INFO] code=A0569 raw_time=153400 price=1106.16 cum_vol=108772 auction_code=40 recv_type=50 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260907_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:07 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 87 | 09:00:02 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 160 | 09:00:02 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063, auc=0.550). 이 상태에… |
| 10:00 | 장중 초반 | 237 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 148 | 11:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 70 | 13:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 34 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:07 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

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
| **오늘 20260907** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 5. ⚠ 회귀 발견 — `test_477::test_step9_batch_placeholders_match_params` 가 오늘 깨졌다
### 6. 테스트·검증 총괄
### 7. 함정① 점검 결과
### 8. 🔴 자가유발 결함 1건 — 커밋 메시지에 `@` 혼입 (`3c2f17c`)
## 2026-09-07 (MW0601 536차 — 장중 점검)
### 1. 🔴 P0 — 정체불명 외부 진입 5거래일 연속 재발, 오늘 15건/15계약(12:30 시점), 실현손실 692,589원 + 미결제 1건 진행 중
### 2. STEP 3(GBM 배치 재학습) 트리거 검증 — `[ConstOut]` 후속 3건 전부 정상 매칭 확인
### 3. `.git/index.lock` 회수 재시도 — 여전히 `Operation not permitted`
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
러는 온전.
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

## 2026-09-07 (MW0601 536차 — 장중 점검)

### 1. 🔴 P0 — 정체불명 외부 진입 5거래일 연속 재발, 오늘 15건/15계약(12:30 시점), 실현손실 692,589원 + 미결제 1건 진행 중

- **증상**: `[ExternalEntry]` ERROR가 09:23:21~12:30:03 사이 15건 발생. 7개 포지션 청산 완료
  (실현 -692,589원), 1개(12:30:03 LONG 1계약 @1092.78)는 이 세션 종료 시점까지도 미결제.
- **근거**: `logs/20260907_WARN.log` ERROR/ExternalEntry 14건 + Health CRITICAL 10건
  (exc_tags에 ExternalEntry·OrderSync 동반), `logs/20260907_TRADE.log` 12:30:03 이후
  청산 로그 없음. 거래일 요약(수집기 §5): 엔진 4건 -78,691원 vs 외부 7건 -692,589원.
- **원인**: 미규명(09-04 리포트 F-2 승계, 09-01·09-04에 이어 3번째 관측 세션).
- **결정**: 이번 세션은 코드를 고치지 않는다(장중 라이브 프로세스 운용 중 + 원인이
  코드가 아니라 계좌 접근 경로 바깥일 가능성). 리포트 최상단에 `⚠ 즉시판단` 블록으로
  올려 사용자에게 계좌 보안 확인을 요청했다.
- **Why**: 실전 전환 기준·절대원칙 어느 것도 직접 위반하지 않지만, 15:10 이후 같은 일이
  벌어지면 절대원칙 ①(오버나이트 금지)이 실질적으로 무력화된다. 청산 안전망 자체는
  origin과 무관하게 정상 작동함을 오늘도 재확인했다(14건 전부 정상 청산 절차를 탐).
- **How to apply**: 근본 차단(주문 실행 경로 변경)은 C등급(자동조치 금지, 주간회의
  승인 필요)으로 이미 분류돼 있다. 이번 세션은 G-2(누적 건수 기반 경보 격상, 계측
  계층)만 신규 제안했다 — 매매 로직 무변경.
- **검증**: 장후 리포트에서 오늘 최종 건수/계약수(09-04의 62건/66계약과 비교) 및
  12:30:03 미결제 포지션의 청산 경로(하드스톱/TP1~3/15:10강제청산 중 무엇인지) 확인.
  관측 예정 O-i1·O-i2 등록.

### 2. STEP 3(GBM 배치 재학습) 트리거 검증 — `[ConstOut]` 후속 3건 전부 정상 매칭 확인

- **증상 아님, 정상 확인**: 09:55·11:12·11:51 세 차례 장중 재학습이 각각 09:54(5m)·
  11:11(3m)·11:50(3m) `[ConstOut]` 상수출력 확정 이벤트와 1:1로 짝지어짐을 로그로 대조.
  "30분마다"라는 문구(코드에 없음, 483차 문서정정)로 오독하지 않도록 대조 결과를 기록.
- **결정**: 이상점으로 올리지 않음(이미 반영된 사안).

### 3. `.git/index.lock` 회수 재시도 — 여전히 `Operation not permitted`

- **증상**: 장전 세션이 남긴 0바이트 인덱스락(09:01 생성)이 12:30에도 그대로 존재.
  `python scripts/git_lock_guard.py --reclaim` 재시도 → 동일 오류로 실패.
- **원인**: 리눅스 샌드박스 마운트 경유 실행이라 `unlink` 자체가 거부됨(SKILL.md
  기지 결함, 483차 이후로 알려진 제약과 동일).
- **결정**: 사용자 조치 1번 항목으로 재게시. 세션 안에서는 회수 불가능.

이 세션이 발급한 dev_memory 항목: 위 3건. 코드 변경 없음(계획만 유지, F-1은 장전과 동일).

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-04 (MW0601 529차 — 스윙 피처 착수 · 3_vwap×TrendGate 최적안)
## 2026-09-04 (MW0601 529차 후속 — 채널 3종 구현 완료)
### 남은 것
## 2026-09-04 (MW0601 530차 — 장전 점검)
## 2026-09-04 (MW0601 531차 — 장중 점검)
## 2026-09-04 (MW0601 532차 — 장후 점검)
## 2026-09-04 (MW0601 532차 후속 — 장후 자동조치)
## 2026-09-07 (MW0601 536차 — 장중 점검)
```

미완료 체크박스 **2463건** (끝에서 30건)
```
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
- [ ] **536-1 (P0, 최우선 지속)** 정체불명 외부 진입 — 09-01(47건/50계약)·09-04(최종
- [ ] **536-2 (P2, 고도화 제안)** G-2 — `[ExternalEntry]` 누적 건수 임계 초과 시
- [ ] **536-3 (사용자 조치)** `.git/index.lock` 여전히 미회수 — 이 세션도
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
ion()` 이 날짜 전환 시 5키 dict 로 상태를 통째 교체해
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

## 2026-09-07 (MW0601 536차 — 장중 점검)

- [ ] **536-1 (P0, 최우선 지속)** 정체불명 외부 진입 — 09-01(47건/50계약)·09-04(최종
      62건/66계약)에 이어 오늘(09-07) 12:30 시점 15건/15계약(실현 -692,589원 + 미결제
      1건 진행 중), **5거래일 연속**. 원인 여전히 미규명. 사용자에게 계좌 보안(HTS·MTS
      직접거래 여부, 비밀번호·공동인증서·API 키)을 다시 요청함. 장후 최종 건수 집계
      필요(O-i1) + 12:30:03 미결제 포지션 청산 경로 확인 필요(O-i2).
- [ ] **536-2 (P2, 고도화 제안)** G-2 — `[ExternalEntry]` 누적 건수 임계 초과 시
      로그 레벨을 CRITICAL로 격상 + 대시보드 배너. 임계값은 313차 원칙에 따라
      과거 5거래일 분포로 사전등록 후 확정(지금은 표본 부족, 로깅 격상만 우선 검토).
- [ ] **536-3 (사용자 조치)** `.git/index.lock` 여전히 미회수 — 이 세션도
      `--reclaim` 실패(`Operation not permitted`, 리눅스 샌드박스 제약). 실제
      Windows PC에서 `del .git\index.lock` 직접 삭제 필요. 3.4시간+ 경과, 스테일 확정.
- [x] **536-4** O-p1(정체불명 외부 진입 재발 여부, 장전 등록) → **판정 완료: 재발
      확인**. 536-1로 승계.

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

### `data/heartbeat_MW0601_20260907.json` — 244B · 09-07 15:40:20
```json
{
 "pid": 11116,
 "written_at": "2026-09-07T15:40:20",
 "beat_epoch": 1788763216.5147996,
 "beat_age_sec": 3.9,
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

- 파일 최종 기록: **09-07 15:53:51**

| 키 | 값 | 수집 대상일(2026-09-07)과 일치 |
|---|---|---|
| `date` | 2026-09-07 | 예 |
| `p8_last_success_date` | 2026-09-07 | 예 |
| `eod_retrain_ok_date` | 2026-09-07 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 114개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260907-BLAS즉사-딥다이브.md` | 10.2KB | 09-07 16:08 |
| `docs/정기점검/매일점검/MW0601-20260907-점검리포트.md` | 42.7KB | 09-07 12:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_intra.md` | 77.5KB | 09-07 12:27 |
| `docs/정기점검/매일점검/MW0601-20260907-맥점계측-딥다이브.md` | 10.1KB | 09-07 09:14 |
| `docs/정기점검/매일점검/evidence_MW0601-20260907_pre.md` | 54.6KB | 09-07 09:01 |
| `docs/정기점검/매일점검/MW0601-20260904-점검리포트.md` | 83.0KB | 09-04 17:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_post.md` | 92.5KB | 09-04 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_intra.md` | 78.0KB | 09-04 12:28 |

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

1. `.git/index.lock` **스테일 잔존** (0바이트 · 7.3시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. `logs/20260907_WARN.log`: ERROR 이상 72건
3. `logs/20260907_WARN.log`: **Traceback** 출현 4건 — 크래시/메모리 계열
4. `logs/20260907_HEALTH.log`: ERROR 이상 39건
5. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
6. 포지션 19건 중 최종청산이 하드스톱·손절 계열 **18건(95%)** — 손절 준수율 확인 필요 (레그 35행)
7. 다레그 포지션 **9건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
8. 사이저 최대 2계약 → 실제 진입 최대 1계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
9. 메인 스레드 정지 5초 초과 **4건** (최대 28797ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
10. `logs/20260907_WARN.log`: **degraded=ON** 8건(표본)
11. `logs/20260907_WARN.log`: **ConstOut** 7건(표본)
12. `logs/20260907_SYSTEM.log`: **ConstOut** 8건(표본)
13. `logs/20260907_SIGNAL.log`: **WeightCollapse** 8건(표본)
14. `logs/20260907_SIGNAL.log`: **ConstOut** 8건(표본)
15. `logs/20260907_LEARNING.log`: **축퇴** 8건(표본)
16. `logs/20260907_HEALTH.log`: **degraded=ON** 8건(표본)
17. 미커밋 변경 529건 (실질 14건 · **코드(.py) 12건**) — 코드 변경이 커밋되지 않았다
18. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260907*.log` (Windows) / `grep 강제청산 logs/*20260907*.log`*