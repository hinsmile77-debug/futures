# 미륵이 증거 다이제스트 — 2026-09-04 / POST

- 생성 2026-09-04 16:18:25 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/fervent-tender-dirac/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260904` · `2026-09-04` · `260904` · `0904`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260904.txt` | 28B | 09-04 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260904.txt` | 28B | 09-04 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260904.txt` | 209B | 09-04 15:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260904.log` | 1.4KB | 09-04 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260904.log` | 217B | 09-04 15:46 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260904.json` | 243B | 09-04 15:40 |
| `launcher_{DATE}_084000_14769.log` | 1 | `logs/Mireuk_batch/launcher_20260904_084000_14769.log` | 2.3MB | 09-04 15:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260904.log` | 39.5KB | 09-04 16:11 |
| `retrain_intraday_{DATE}_093900.log` | 1 | `logs/retrain_intraday_20260904_093900.log` | 2.7KB | 09-04 09:39 |
| `retrain_intraday_{DATE}_113500.log` | 1 | `logs/retrain_intraday_20260904_113500.log` | 2.7KB | 09-04 11:35 |
| `retrain_intraday_{DATE}_121300.log` | 1 | `logs/retrain_intraday_20260904_121300.log` | 2.7KB | 09-04 12:13 |
| `retrain_intraday_{DATE}_130601.log` | 1 | `logs/retrain_intraday_20260904_130601.log` | 2.7KB | 09-04 13:06 |
| `retrain_intraday_{DATE}_134500.log` | 1 | `logs/retrain_intraday_20260904_134500.log` | 2.7KB | 09-04 13:45 |
| `retrain_intraday_{DATE}_142400.log` | 1 | `logs/retrain_intraday_20260904_142400.log` | 2.7KB | 09-04 14:24 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260904.txt` | 43B | 09-04 15:40 |
| `strategy_report_{DATE}_154024.txt` | 1 | `data/daily_reports/strategy_report_20260904_154024.txt` | 2.2KB | 09-04 15:40 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260904_BACKFILL.log` | 0B | 09-04 07:57 |
| `{DATE}_DATA.log` | 1 | `logs/20260904_DATA.log` | 342.1KB | 09-04 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260904_DEBUG.log` | 236.5KB | 09-04 15:10 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260904_HEALTH.log` | 22.3KB | 09-04 15:09 |
| `{DATE}_HOGA.log` | 1 | `logs/20260904_HOGA.log` | 44.8MB | 09-04 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260904_LEARNING.log` | 296.4KB | 09-04 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260904_MICRO.log` | 912.7KB | 09-04 15:40 |
| `{DATE}_PROBE.log` | 1 | `logs/20260904_PROBE.log` | 97.3KB | 09-04 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260904_SIGNAL.log` | 495.8KB | 09-04 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260904_SYSTEM.log` | 1.2MB | 09-04 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260904_TRADE.log` | 81.4KB | 09-04 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260904_WARN.log` | 394.2KB | 09-04 15:40 |

## 2. 코드·커밋 상태

- HEAD `9738080` · 브랜치 `v9-dev` · 미커밋 527건 · 실질 변경 8건 · 코드(.py) 0건 · EOL 파생 510건 (추적변경 518 · 미추적 9 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260810.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260810.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260807.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260807.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260810.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260810.md`
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
… 외 487건
```

**당일(2026-09-04) 커밋**
```
9738080 [MW0601] 527~529차: 탈진 레짐은 라벨 0건이었다 — 레그 위치를 새 축으로 계측(스윙 피처 + 채널 3종)
c9f76f8 [MW0601] 524~526차: 급변장 라벨의 82%가 z경고였다 — 라벨·게이트 분리(동작 불변) · P5-13 채널 · z경고 잡음 보정(모니터 전용)
```

**최근 커밋 12건**
```
9738080 [MW0601] 527~529차: 탈진 레짐은 라벨 0건이었다 — 레그 위치를 새 축으로 계측(스윙 피처 + 채널 3종)
c9f76f8 [MW0601] 524~526차: 급변장 라벨의 82%가 z경고였다 — 라벨·게이트 분리(동작 불변) · P5-13 채널 · z경고 잡음 보정(모니터 전용)
c26c513 [MW0601] 523차 후속: 리포트 제4부에 커밋 해시 기재
e1f063a [MW0601] 523차 후속: 장후 자동조치 — G-1(기동마커 게재) · G-2(ConfFloorGuard auc) · G-3(ExitStageRecon 인용)
8997136 [MW0601] 519차 기록: DECISION_LOG · NEXT_TODO · 리포트 제5부
d03b629 [MW0601] 519차: CB② 복원 · 메인스레드 정지 경보 · F-1 마감 잔여 자동청산 (사용자 지시)
7338611 [MW0601] 518차 후속: 장후 자동조치 — F-3(진입출처 라벨) · G-1(재기동 잔량 경보 문구) · G-4(이월손익 가시화)
a3f70ab [MW0601] 514차 후속: 장후 자동조치 — F-A(P1-3) · F-B(고도화①) · F-C(고도화②/P5-신규)
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
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

_본문 미열람(설정): `20260904_HOGA.log` 44.8MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260904.txt`** — 28B · 09-04 15:40:24
```
2026-09-04T15:40:24.176426
```

**`data/daily_close_started_20260904.txt`** — 28B · 09-04 15:40:17
```
2026-09-04T15:40:17.906183
```

**`data/daily_reports/strategy_report_20260904_154024.txt`** — 2.2KB · 09-04 15:40:24
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-04 15:40
========================================================
  버전    : v1.0  (73일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-4.85  MDD(자본대비)=26.9%
  당일      : WR=64.3%  PF=0.99
  롤링20일: 누적 -11426095원  Sh=-4.85  MDD(자본대비)=26.9%  MDD(peak대비)=663.1%
  당일손익 : broker(gross) +683,000원  수수료 700,690원  net -17,690원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.005 (CLEAR)
  PSI/feat: cvd_delta=0.005  ofi_pressure=0.001  vwap_position=0.078
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -527,973원  승률 50.0%  합계 -10,559,468원
  등급별 순EV(30일): A=+3,170원(131건,승66%)  BROKER=-5,380,798원(2건,승0%)  C=+9,768원(23건,승78%)  MANUAL=-12,300원(141건,승50%)
  호라이즌별 순EV(30일): 1m=+10,940원(26건)  3m=-6,135원(104건)  5m=+35,731원(22건)  ?=-84,749원(145건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 26분  5일평균 29분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 20.4pt(5일평균 29.7pt)  1분평균변동 0.54pt(5일평균 0.78pt)
--------------------------------------------------------
  진입 퍼널(2026-09-04, 총 370분):
    FLAT 263 → conf미달 73 → CoherenceGate 8 → 게이트차단 25 → 후보 1 → 진입 1
    게이트별: ATR변동성=9  포지션보유중(평가생략)=5  콜드스타트/기타(조건부구간)=4  콜드스타트/기타(RegimeOverride)=4  체크리스트항목미달=2  콜드스타트/기타(DataAnomalyGate)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260904.txt`** — 209B · 09-04 15:48:47
```
completed: 2026-09-04 15:48:47
rows: 40786
cols: 97
horizons_replaced: 6/6
t_load_s: 40.1
t_retrain_s: 183.6
t_total_s: 224.2
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260904.txt`** — 43B · 09-04 15:40:39
```
auto_shutdown
2026-09-04T15:40:39.174575
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260904_121300.log`, `retrain_intraday_20260904_130601.log`, `retrain_intraday_20260904_134500.log`, `retrain_intraday_20260904_142400.log`, `retrain_intraday_20260904_113500.log`, `20260904_MICRO.log`, `20260904_DATA.log`, `20260904_PROBE.log`_

### `logs/20260904_TRADE.log` — 81.4KB · 626행 · 최종 15:40:23

- 형식 평문 · 시각 인식 626행 · WARNING=53, INFO=573

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-04 09:42:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,166) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-04 09:42:00 [INFO] TRADE: [진입체크] LONG→LONG 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore✅ prev✅ time✅ risk✅ chas✅ coun✅ | conf=40.0%
2026-09-04 09:42:00 [INFO] TRADE: [Position] 진입 LONG 2계약 @ 1049.44 | 손절=1047.71 1차=1049.79(×0.26) 2차=1051.17 horizon=1m hurst=mean-revert
2026-09-04 09:42:00 [INFO] TRADE: [주문요청] LONG->LONG 2계약 @ 1049.44 등급=A 역방향진입=OFF 체결대기
  …
2026-09-04 15:10:00 [INFO] TRADE: [Chejan] 상태=접수 주문번호=4458 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-04 15:10:00 [INFO] TRADE: [Chejan] 상태=체결 주문번호=4458 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-04 15:10:00 [INFO] TRADE: [Position] 체결청산 SHORT @ 1053.72 | PnL=+1.97pt (+88,310원) | 15:10 강제청산
2026-09-04 15:10:00 [INFO] TRADE: [청산 완료] PnL=+1.97pt (+88,310원) | 포지션 합계 +178,930원 (레그 3)
2026-09-04 15:40:23 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 52 | 10:43:53 | 15:01:09 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1046.66 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `TimeExit` | 1 | 15:10:00 | 15:10:00 | 15:10 강제 청산 트리거 @ 15:10:00 |

**채널** — `TRADE`×626

**컴포넌트 상위 15** — `Chejan`×213, `Position`×133, `체결동기화`×62, `PositionFallback`×52, `주문요청`×49, `청산 완료`×28, `TickTP1`×18, `TickStop-S0C`×18, `체결청산-부분`×17, `TP1 부분청산`×16, `Sizer`×8, `TP2 부분청산`×6, `ProfitGuard`×2, `진입체크`×1, `체결진입`×1

### `logs/20260904_WARN.log` — 394.2KB · 1819행 · 최종 15:40:23

- 형식 평문 · 시각 인식 1812행 · CRITICAL=90, ERROR=63, WARNING=1659, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-09-04 08:40:50 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
2026-09-04 08:40:50 [WARNING] SYSTEM: [LiveDBG] _apply update_learning 15ms
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -17690원
════════════════════════════════════════════════════
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 90 | 10:46:00 | 15:08:00 | level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16 |
| ERROR | `ExternalEntry` | 63 | 10:43:53 | 15:40:17 | 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.66 (보유 1계약, 평균 1046.66). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
```

</details>

<details><summary>ERROR/ExternalEntry 원문 2건</summary>

```
2026-09-04 10:43:53 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.66 (보유 1계약, 평균 1046.66). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
2026-09-04 10:44:03 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.18 (보유 2계약, 평균 1046.42). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
```

</details>

**WARNING — 태그 39종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 605 | 08:40:48 | 15:10:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 213 | 09:42:00 | 15:10:00 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='974' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=09:42:00.619' | position… |
| `ChejanMatch` | 213 | 09:42:00 | 15:10:00 | order_no='974' | pending='ENTRY:LONG qty=2 filled=0 order_no=974 reason=진입 req_at=09:42:00.619' | pending_matched=True |
| `OrderSync` | 132 | 10:43:53 | 15:01:09 | 미추적 체결 감지 (pending_miss) order_no=1965 side=SHORT qty=1 price=1046.66 before=FLAT |
| `PendingOrder` | 98 | 09:42:00 | 15:10:00 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1049.44, 'reason': '진입', 'hint_source': '', 'atr': 1.3543, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `ExitCooldown` | 56 | 09:43:56 | 15:10:00 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:46:56) |
| `Health` | 55 | 09:00:01 | 15:09:00 | level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0 |
| `ExitFillFlow` | 41 | 09:43:56 | 15:10:00 | after='FLAT' | before='LONG 1계약 @ 1049.18' | fill_price=1049.18 | fill_qty=1 | mode='final' | pending='EXIT_FULL:LONG qty=1 filled=1 order_no=1008 reason=하드스톱(틱) req_at=09:43:55.864' | reason='하드스톱(틱)' |
| `PartialExitAttempt` | 30 | 09:42:03 | 15:06:00 | pending='NONE' | position='LONG 2계약 @ 1049.18' | price=1049.56 | stage=1 |
| `PartialExitSendOrderResult` | 28 | 09:42:04 | 15:06:00 | position='LONG 2계약 @ 1049.18' | reason='TP1 부분청산 33%' | ret=0 | send_qty=1 | stage=1 | stage_plan=(1, 1, 0) | target_qty=1 |
| `IntrabarTPSchedule` | 22 | 09:42:04 | 15:06:01 | EXIT_PARTIAL 해소 → 300ms 후 TP 재점검 스케줄 price=1049.56 pos=LONG p1=True p2=False p3=False |
| `ExitSendOrderResult` | 20 | 09:43:55 | 15:10:00 | ret=0 kind=하드스톱(틱) direction=LONG qty=1 |

**채널** — `SYSTEM`×1667, `HEALTH`×145

**컴포넌트 상위 15** — `LiveDBG`×605, `ChejanFlow`×213, `ChejanMatch`×213, `Health`×145, `OrderSync`×132, `PendingOrder`×98, `ExternalEntry`×63, `ExitCooldown`×56, `ExitFillFlow`×41, `PartialExitAttempt`×30, `PartialExitSendOrderResult`×28, `IntrabarTPSchedule`×22, `ExitSendOrderResult`×20, `TickTP1`×18, `TickStop`×18

### `logs/20260904_SYSTEM.log` — 1.2MB · 7259행 · 최종 15:40:39

- 형식 평문 · 시각 인식 7234행 · INFO=7234, PLAIN=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:30 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=11496 | 행감지=30s all_threads=True
2026-09-04 08:40:31 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-04 08:40:31 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-04 08:40:31 [INFO] SYSTEM: 미륵이 초기화
2026-09-04 08:40:31 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-03) 종가 버퍼 로드: 384봉
  …
2026-09-04 15:40:24 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-04 15:40:24 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-04 15:40:39 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-04 15:40:39 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-04 15:40:39 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×7234

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1004, `CybosEvent`×426, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×406, `CybosDailyPnl`×396, `S6Detail`×370, `PipePerf`×370, `BalanceUI`×365, `BalanceRefresh`×221, `CybosDailyPnlHeaders`×198, `System`×98, `MicroRegime`×79

### `logs/20260904_SIGNAL.log` — 495.8KB · 4422행 · 최종 15:40:23

- 형식 평문 · 시각 인식 4422행 · WARNING=1743, INFO=2679

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
  …
2026-09-04 15:10:12 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-04 15:40:23 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-04 15:40:23 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 83분(22.4%) / DN 22분(5.9%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-04 15:40:23 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-04 age=29m extreme=666 refresh=35 grade_x=50 cb3=0
2026-09-04 15:40:23 [INFO] SIGNAL: [ModelHealth] date=2026-09-04 앙상블유효가동률=75.4% | 파이프라인 370분 | ConstOut 6회/11분 {"3m": {"events": 5, "minutes": 9}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 80분 | 장중재학습 6회 | CB③ ready 140분/370분 (38%) (리셋 3회, 표본손실 90건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1020 | 09:00:00 | 14:50:01 | 1m 'macro_vix' scale=0.0206 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 259 | 09:00:00 | 15:02:00 | ts=08:59 horizon=1m age=1m max_z=+4.90(toxicity_flow_stress) extreme=2 adj=2 |
| `Model` | 218 | 09:00:00 | 15:02:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerRefresh` | 84 | 08:45:18 | 09:15:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0293) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 80 | 09:07:01 | 15:07:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 73 | 09:06:00 | 14:53:01 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `ConstOut` | 6 | 09:38:00 | 14:23:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 3 | 09:00:00 | 11:20:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4230 (conf_floor=0.330, min_conf=0.423, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4422

**컴포넌트 상위 15** — `ScalerFloor`×1068, `SIGNAL`×740, `Ensemble`×376, `FQAdj`×367, `ZeroDiag`×353, `Model`×260, `ScalerMonitor`×260, `MetaGate`×194, `ScalerRefresh`×125, `Checklist`×96, `WeightCollapse`×80, `MicroRegime`×79, `ATR-Horizon`×79, `차단`×49, `InstabilityGate`×48

### `logs/20260904_LEARNING.log` — 296.4KB · 2885행 · 최종 15:40:23

- 형식 평문 · 시각 인식 2875행 · WARNING=169, INFO=2706, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:33 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2630 < conf_floor=0.3300 (span=0.00096 auc=0.546 out_max=0.2630, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00019 auc=0.521 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-04 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00109 auc=0.539 out_max=0.4351 (n=145) → 보정 재적용
  …
2026-09-04 15:40:23 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-04 15:40:23 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-04 15:40:23 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-04 15:40:23 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-04 15:40:23 [INFO] LEARNING: [Sigma] EOD sigma_20=0.05531% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 168 | 08:40:33 | 13:47:00 | 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |
| `DriftAdjuster` | 1 | 15:40:18 | 15:40:18 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 7일) |

**채널** — `LEARNING`×2875

**컴포넌트 상위 15** — `LEARNING`×1219, `SGD`×370, `sigma`×357, `Calibration`×328, `Bias⚠`×229, `Bias`×116, `MetaConf`×76, `OnlineLearner`×62, `ScalerWarmup`×41, `BiasReset`×16, `SHAP`×12, `GBM-64`×12, `GBM`×12, `RF`×7, `UPDATE`×6

### `logs/20260904_HEALTH.log` — 22.3KB · 161행 · 최종 15:09:00

- 형식 평문 · 시각 인식 161행 · CRITICAL=90, WARNING=55, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0
2026-09-04 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=653ms | quality=0.86 | cache_age=124s | exceptions_10m=0
2026-09-04 09:02:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=428ms | quality=0.74 | cache_age=184s | exceptions_10m=0
2026-09-04 09:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=287ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-09-04 09:05:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=407ms | quality=1.00 | cache_age=180s | exceptions_10m=0
  …
2026-09-04 15:05:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=361ms | quality=1.00 | cache_age=114s | exceptions_10m=17
2026-09-04 15:06:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=438ms | quality=1.00 | cache_age=174s | exceptions_10m=17
2026-09-04 15:07:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=294ms | quality=1.00 | cache_age=51s | exceptions_10m=17
2026-09-04 15:08:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=314ms | quality=1.00 | cache_age=111s | exceptions_10m=16
2026-09-04 15:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=366ms | quality=1.00 | cache_age=171s | exceptions_10m=10
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 90 | 10:46:00 | 15:08:00 | level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 55 | 09:00:01 | 15:09:00 | level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0 |

**채널** — `HEALTH`×161

**컴포넌트 상위 15** — `Health`×160, `HealthTrend`×1

### `logs/retrain_eod_20260904.log` — 39.5KB · 370행 · 최종 16:11:25

- 형식 평문 · 시각 인식 176행 · WARNING=10, WARN=1, INFO=166, PLAIN=193

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 15:45:03,727 [INFO] EOD_RETRAIN: =======================================================
2026-09-04 15:45:03,728 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-04 15:45:03,728 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-04 15:45:03,728 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-04 15:45:03,728 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
[안내] DB 행 삭제는 비활성입니다. 켜기 전에 docs/정기점검/보관정책_MW0601-20260818.md 의 근거를 먼저 읽으세요.
2026-09-04 16:11:25,291 [INFO] EOD_RETRAIN: [검증 캠페인] 요약: 게이트 ablation 리포트=OK | 호라이즌 conf-층화 검정=OK | 검증 캠페인 판정 리포트=OK | 피처셋 건강 리포트=OK | CVD 앵커 대조 리포트=OK | 조기청산 반사실 [49]=OK | 라우팅 밴드 성과 [D9-B]=OK | 방향 처분 실험 [40-B]=OK | 섀도우 TB 재학습=OK | 분위 회귀 재학습=OK | 메타라벨 분류기 재학습=OK | MAE/MFE 분석=OK | 월간 로그 정리=OK
2026-09-04 16:11:25,317 [INFO] EOD_RETRAIN: 판정 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\validation_campaign_report_20260904.md
2026-09-04 16:11:25,318 [INFO] EOD_RETRAIN: 피처셋 건강 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\featureset_health_report_20260904.md
2026-09-04 16:11:25,318 [INFO] EOD_RETRAIN: =======================================================
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:51 | 15:47:38 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1501봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-03 14:38:00 ≥ 홀드아웃 시작=2026-08-28 12:59:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-03 14:38 >= holdout_start=2026-08-28 12:59 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-03 … |
| `GuardGhost` | 4 | 15:45:59 | 15:46:11 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-04 13:53:00까지)인데 acc.txt=0.3797는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `-` | 1 | ??:??:?? | ??:??:?? | ] 2개 파일 0.4MB -> 202608_WARN.zip |

**채널** — `LEARNING`×66, `SIGNAL`×43, `EOD_RETRAIN`×39, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×185, `ScalerFloor`×36, `Retrain`×21, `EOD_RETRAIN`×18, `검증 캠페인`×15, `RF`×9, `ShadowTB`×8, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `QuantileReg`×6

### `logs/retrain_intraday_20260904_093900.log` — 2.7KB · 21행 · 최종 09:39:20

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 09:39:00,561 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-04 09:39:00,562 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-04 09:39:00,562 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-04 09:39:00,562 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_9cce9847.json
2026-09-04 09:39:03,521 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-04 09:39:20,699 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-04 09:39:20,700 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-04 09:39:20,701 [INFO] LEARNING: [Retrain] 완료 | 17.2초 | 성공=1/1 호라이즌
2026-09-04 09:39:20,701 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 20.1s 데이터=4800행
2026-09-04 09:39:20,703 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_9cce9847.json
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
오늘 PnL: -17690원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 1 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 63 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 62 |
| 청산(`체결청산`) | 28 |
| 차단(`[차단]`) | 49 |
| 사이저 호출(`[Sizer]`) | 8 |

### 포지션 28건 · 승 13 (46%) · 합계 +13.70pt (-17,691원)  ※ 레그 67행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:42:00 | 엔진 | LONG | 2 | 1m | 2 | +0.34 | -3,586 | 하드스톱(틱) |
| 10:43:53 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -2.18 | -129,532 | 하드스톱(틱) |
| 10:45:17 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.57 | -2,787 | 하드스톱(틱) |
| 10:46:31 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.61 | +209 | 하드스톱(틱) |
| 10:49:42 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +1.97 | +68,245 | 하드스톱(틱) |
| 10:55:29 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -3.51 | -206,712 | 하드스톱(틱) |
| 11:08:03 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.38 | -11,807 | 하드스톱(틱) |
| 11:18:09 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +1.45 | +42,107 | 하드스톱(틱) |
| 11:31:56 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.44 | -8,870 | 하드스톱(틱) |
| 11:34:01 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +4.11 | +174,138 | TP3(전량) |
| 11:39:07 (추정귀속) | 외부 | LONG | 3 | — | 2 | +1.01 | +19,233 | 하드스톱(틱) |
| 11:43:24 (추정귀속) | 외부 | LONG | 2 | — | 2 | +1.50 | +54,476 | TP2(전량) |
| 11:49:14 (추정귀속) | 외부 | LONG | 1 | — | 1 | +1.28 | +53,721 | TP2(전량) |
| 11:52:12 (추정귀속) | 외부 | SHORT | 1 | — | 1 | -0.94 | -57,297 | 미추적체결(pending_miss) |
| 11:55:27 (추정귀속) | 외부 | LONG | 2 | — | 2 | -2.06 | -123,596 | 하드스톱(틱) |
| 11:57:46 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -2.28 | -134,574 | 하드스톱(틱) |
| 12:04:11 (추정귀속) | 외부 | SHORT | 1 | — | 1 | -0.46 | -33,301 | 하드스톱(틱) |
| 12:17:36 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -1.83 | -122,919 | 하드스톱(틱) |
| 12:19:38 (추정귀속) | 외부 | LONG | 3 | — | 3 | +0.37 | -12,940 | 하드스톱(틱) |
| 12:23:23 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +3.34 | +136,082 | TP3(전량) |
| 12:25:10 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -0.43 | -52,862 | 미추적체결(pending_miss) |
| 14:31:14 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +2.41 | +88,766 | 하드스톱 |
| 14:39:21 (추정귀속) | 외부 | SHORT | 2 | — | 2 | +2.14 | +86,200 | TP2(전량) |
| 14:44:51 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -1.96 | -118,768 | 하드스톱(틱) |
| 14:48:39 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +4.04 | +170,857 | TP3(전량) |
| 14:53:05 (추정귀속) | 외부 | SHORT | 1 | — | 1 | -1.30 | -75,360 | 하드스톱(틱) |
| 14:58:13 (추정귀속) | 외부 | LONG | 2 | — | 2 | +0.50 | +4,256 | 하드스톱(틱) |
| 15:01:09 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +4.19 | +178,930 | 15:10 강제청산 |

**출처별 소계** — 엔진 1건 -3,586원 · 외부 27건 -14,105원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 27건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 67행** (부분청산 39 · 전량청산 28)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:42:04 | 부분 | 1 | +0.34 | +6,707 | TP1 부분청산 33% |
| 09:43:56 | 전량 | 1 | +0.00 | -10,293 | 하드스톱(틱) |
| 10:44:53 | 부분 | 1 | -1.16 | -68,266 | 하드스톱(틱) |
| 10:44:54 | 전량 | 1 | -1.02 | -61,266 | 하드스톱(틱) |
| 10:45:37 | 부분 | 1 | +0.57 | +18,071 | TP1 부분청산 33% |
| 10:46:12 | 부분 | 1 | +0.01 | -9,929 | 하드스톱(틱) |
| 10:46:12 | 전량 | 1 | -0.01 | -10,929 | 하드스톱(틱) |
| 10:46:51 | 부분 | 1 | +0.59 | +19,403 | TP1 부분청산 33% |
| 10:47:42 | 부분 | 1 | +0.01 | -9,597 | 하드스톱(틱) |
| 10:47:43 | 전량 | 1 | +0.01 | -9,597 | 하드스톱(틱) |
| 10:50:10 | 부분 | 1 | +0.55 | +17,415 | TP1 부분청산 33% |
| 10:52:00 | 부분 | 1 | +1.49 | +64,415 | TP2 부분청산 33% |
| 10:52:50 | 전량 | 1 | -0.07 | -13,585 | 하드스톱(틱) |
| 10:56:10 | 부분 | 1 | -1.19 | -69,904 | 하드스톱(틱) |
| 10:56:10 | 부분 | 1 | -1.19 | -69,904 | 하드스톱(틱) |
| 10:56:10 | 전량 | 1 | -1.13 | -66,904 | 하드스톱(틱) |
| 11:09:10 | 부분 | 1 | +0.66 | +22,731 | TP1 부분청산 33% |
| 11:09:41 | 부분 | 1 | -0.12 | -16,269 | 하드스톱(틱) |
| 11:09:41 | 전량 | 1 | -0.16 | -18,269 | 하드스톱(틱) |
| 11:18:32 | 부분 | 1 | +0.61 | +20,369 | TP1 부분청산 33% |
| 11:20:01 | 부분 | 1 | +0.89 | +34,369 | TP2 부분청산 33% |
| 11:30:03 | 전량 | 1 | -0.05 | -12,631 | 하드스톱(틱) |
| 11:32:11 | 부분 | 1 | +0.56 | +17,710 | TP1 부분청산 33% |
| 11:32:55 | 부분 | 1 | -0.06 | -13,290 | 하드스톱(틱) |
| 11:32:55 | 전량 | 1 | -0.06 | -13,290 | 하드스톱(틱) |
| 11:34:28 | 부분 | 1 | +0.55 | +17,046 | TP1 부분청산 33% |
| 11:35:00 | 부분 | 1 | +1.39 | +59,046 | TP2 부분청산 33% |
| 11:37:01 | 전량 | 1 | +2.17 | +98,046 | TP3(전량) |
| 11:39:41 | 부분 | 1 | +0.63 | +21,078 | TP1 부분청산 33% |
| 11:42:35 | 전량 | 2 | +0.19 | -1,845 | 하드스톱(틱) |
| 11:48:01 | 부분 | 1 | +0.74 | +26,738 | TP2(전량) |
| 11:48:01 | 전량 | 1 | +0.76 | +27,738 | TP2(전량) |
| 11:51:01 | 전량 | 1 | +1.28 | +53,721 | TP2(전량) |
| 11:54:36 | 전량 | 1 | -0.94 | -57,297 | 미추적체결(pending_miss) |
| 11:57:23 | 부분 | 1 | -1.03 | -61,798 | 하드스톱(틱) |
| 11:57:24 | 전량 | 1 | -1.03 | -61,798 | 하드스톱(틱) |
| 11:59:44 | 부분 | 1 | -1.14 | -67,287 | 하드스톱(틱) |
| 11:59:44 | 전량 | 1 | -1.14 | -67,287 | 하드스톱(틱) |
| 12:15:57 | 전량 | 1 | -0.46 | -33,301 | 하드스톱(틱) |
| 12:19:07 | 부분 | 1 | -0.61 | -40,973 | 하드스톱(틱) |
| 12:19:07 | 부분 | 1 | -0.61 | -40,973 | 하드스톱(틱) |
| 12:19:07 | 전량 | 1 | -0.61 | -40,973 | 하드스톱(틱) |
| 12:21:02 | 부분 | 1 | +0.33 | +6,020 | TP1 부분청산 33% |
| 12:21:54 | 부분 | 1 | +0.01 | -9,980 | 하드스톱(틱) |
| 12:21:55 | 전량 | 1 | +0.03 | -8,980 | 하드스톱(틱) |
| 12:24:01 | 부분 | 1 | +0.52 | +15,694 | TP1 부분청산 33% |
| 12:25:01 | 부분 | 1 | +1.38 | +58,694 | TP2 부분청산 33% |
| 12:25:01 | 전량 | 1 | +1.44 | +61,694 | TP3(전량) |
| 12:26:35 | 부분 | 1 | -0.17 | -18,954 | 미추적체결(pending_miss) |
| 12:26:36 | 부분 | 1 | -0.13 | -16,954 | 미추적체결(pending_miss) |
| 12:26:37 | 전량 | 1 | -0.13 | -16,954 | 미추적체결(pending_miss) |
| 14:38:27 | 부분 | 1 | +0.69 | +23,922 | TP1 부분청산 33% |
| 14:39:00 | 부분 | 1 | +0.85 | +31,922 | 하드스톱 |
| 14:39:00 | 전량 | 1 | +0.87 | +32,922 | 하드스톱 |
| 14:39:37 | 부분 | 1 | +0.64 | +21,600 | TP1 부분청산 33% |
| 14:44:00 | 전량 | 1 | +1.50 | +64,600 | TP2(전량) |
| 14:47:17 | 부분 | 1 | -0.98 | -59,384 | 하드스톱(틱) |
| 14:47:17 | 전량 | 1 | -0.98 | -59,384 | 하드스톱(틱) |
| 14:49:22 | 부분 | 1 | +0.62 | +20,619 | TP1 부분청산 33% |
| 14:51:01 | 부분 | 1 | +1.40 | +59,619 | TP2 부분청산 33% |
| 14:52:00 | 전량 | 1 | +2.02 | +90,619 | TP3(전량) |
| 14:57:26 | 전량 | 1 | -1.30 | -75,360 | 하드스톱(틱) |
| 14:58:43 | 부분 | 1 | +0.60 | +19,628 | TP1 부분청산 33% |
| 14:59:28 | 전량 | 1 | -0.10 | -15,372 | 하드스톱(틱) |
| 15:02:01 | 부분 | 1 | +0.55 | +17,310 | TP1 부분청산 33% |
| 15:06:00 | 부분 | 1 | +1.67 | +73,310 | TP2 부분청산 33% |
| 15:10:00 | 전량 | 1 | +1.97 | +88,310 | 15:10 강제청산 |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×31, `TP1 부분청산 33%`×16, `TP2 부분청산 33%`×6, `TP2(전량)`×4, `미추적체결(pending_miss)`×4, `TP3(전량)`×3, `하드스톱`×2, `15:10 강제청산`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 19/28건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -17,691 = 포지션합 -17,691 → OK · `[청산 완료]` 28건 = 조립 포지션 28건 → OK

### CB③ 판정 가능 시간 — **140분 / 370분 (38%)**

acc30m 버퍼 리셋 3회 · 그때 버린 표본 90건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:42:00 | LONG | 2 | 1049.44 | 1m | mean-revert |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×8

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×8

### 차단 사유 49건 · 32종

| 건수 | 사유 |
|---|---|
| 14 | 등급X — 미통과 항목: 2_confidence |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.70pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 6.1pt > ATR×5.0=5.8pt (시가=1043.24 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 6.5pt > ATR×5.0=6.1pt (시가=1043.24 반등위험) |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 101초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 169초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 110초 후 재진입 가능 |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 청산 후 쿨다운 — 60초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 155초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 43초 후 재진입 가능 |
| 1 | ATR 0.72pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.56pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.65pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×14, `3_vwap`×2, `6_foreign`×2, `4_cvd`×1, `5_ofi`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 21건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×13
- `연속 손절 2회 (300초 창, 포지션 단위)` ×4
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-04 12:25:10, 현재 1…` ×2
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 6건 · 최대 3765ms · 5초 초과 0건

상위 — 3765ms, 3343ms, 3125ms, 3000ms, 2281ms, 2265ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260904_TRADE.log`
```
--- 강제청산 ×1(표본)
15:10:00 2026-09-04 15:10:00 [INFO] TRADE: [Position] 체결청산 SHORT @ 1053.72 | PnL=+1.97pt (+88,310원) | 15:10 강제청산
```

### `logs/20260904_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:23 2026-09-04 15:40:23 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 29분/일 < 하한 60분 — 금일 26분. | ConfFloorGuard 도달가능 26분 · 도달불가 101분 · 재지않음 243분
--- ConstOut ×6(표본)
09:38:00 2026-09-04 09:38:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:34:01 2026-09-04 11:34:01 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
12:12:01 2026-09-04 12:12:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
13:05:01 2026-09-04 13:05:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×8(표본)
09:43:56 2026-09-04 09:43:56 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:44:54 2026-09-04 10:44:54 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:46:12 2026-09-04 10:46:12 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:52:50 2026-09-04 10:52:50 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:43:56 2026-09-04 09:43:56 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:46:56)
09:43:56 2026-09-04 09:43:56 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:46:56)
10:44:54 2026-09-04 10:44:54 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:47:53)
10:44:54 2026-09-04 10:44:54 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:47:53)
--- [ExitStageRecon] ×1(표본)
15:40:23 2026-09-04 15:40:23 [WARNING] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 17레그 / 17포지션 중 TP 이벤트 대응 11 · 단일계약 보호전환(설계) 0 · 미대응 6 ⚠ 미대응 합계 -836,093원 (진입 10:43:53, 10:55:29, 11:55:27, 11:57:46, 12:17:36 외 1건). 이 레그들은 라벨상 「…
--- [ForceExitPass] ×1(표본)
15:10:00 2026-09-04 15:10:00 [WARNING] SYSTEM: [ForceExitPass] 15:10 경과 분봉 — STEP 8 청산 감시 평가 price=1053.82 status=SHORT engine=1ct broker_cached=0ct (예측·저장·시계리셋 없음)
--- [SHAP] 슬로우 ×3(표본)
11:51:01 2026-09-04 11:51:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 970ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:44:02 2026-09-04 13:44:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1079ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
13:55:01 2026-09-04 13:55:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 993ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
--- degraded=ON ×8(표본)
10:47:01 2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
10:48:02 2026-09-04 10:48:02 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=269ms | quality=1.00 | cache_age=120s | exceptions_10m=24
10:49:00 2026-09-04 10:49:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=341ms | quality=1.00 | cache_age=178s | exceptions_10m=24
10:50:00 2026-09-04 10:50:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=321ms | quality=1.00 | cache_age=55s | exceptions_10m=33
--- level=CRITICAL ×2(표본)
10:46:00 2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
12:20:00 2026-09-04 12:20:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=369ms | quality=1.00 | cache_age=130s | exceptions_10m=20
--- 강제청산 ×8(표본)
10:43:53 2026-09-04 10:43:53 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.66 (보유 1계약, 평균 1046.66). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
10:44:03 2026-09-04 10:44:03 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.18 (보유 2계약, 평균 1046.42). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
10:45:17 2026-09-04 10:45:17 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.08 (보유 1계약, 평균 1046.08). 오늘 누적 3건 / 3계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
10:45:18 2026-09-04 10:45:18 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.08 (보유 2계약, 평균 1046.08). 오늘 누적 4건 / 4계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
--- 메인 스레드 블로킹 ×6(표본)
09:00:01 2026-09-04 09:00:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2281 band=INFO since_pipe_s=0.1
12:06:03 2026-09-04 12:06:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3343ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3343 band=INFO since_pipe_s=0.1
12:14:03 2026-09-04 12:14:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3000ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3000 band=INFO since_pipe_s=0.0
13:07:02 2026-09-04 13:07:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2265ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2265 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260904_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:38:00 2026-09-04 09:38:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:40:00 (const_output)
09:38:00 2026-09-04 09:38:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:38:00 2026-09-04 09:38:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=86ms fit=75ms total=162ms
09:39:00 2026-09-04 09:39:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:23 2026-09-04 15:40:23 [INFO] SYSTEM: [CB③계측] 조건성립 97분 / 판정가능 140분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-04 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:05:00 2026-09-04 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:10:00 2026-09-04 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:15:00 2026-09-04 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
--- [CB] ×4(표본)
12:26:36 2026-09-04 12:26:36 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-04 12:25:10, 현재 1회)
12:26:37 2026-09-04 12:26:37 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-04 12:25:10, 현재 1회)
15:40:23 2026-09-04 15:40:23 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:23 2026-09-04 15:40:23 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:17 2026-09-04 15:11:17 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:24 2026-09-04 15:40:24 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:39 2026-09-04 15:40:39 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 강제청산 ×1(표본)
15:10:00 2026-09-04 15:10:00 [INFO] SYSTEM: [BalanceUI] force flat rows reason=final_exit:15:10 강제청산 cached_summary_nonblank=True
--- 자동 종료 ×5(표본)
15:40:24 2026-09-04 15:40:24 [INFO] SYSTEM: [Notify] ℹ️ [15:40:24] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:24 2026-09-04 15:40:24 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:39 2026-09-04 15:40:39 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260904_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:00:00 2026-09-04 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4230 (conf_floor=0.330, min_conf=0.423, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:42:00 2026-09-04 10:42:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3789 ≥ 필요 0.3720 (span=0.0185, auc=0.567)
10:55:00 2026-09-04 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3671 < 필요 0.3720 (conf_floor=0.330, min_conf=0.372, span=0.0149, auc=0.560). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:07:00 2026-09-04 11:07:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3764 ≥ 필요 0.3720 (span=0.0134, auc=0.547)
--- ConstOut ×8(표본)
09:38:00 2026-09-04 09:38:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:38:00 2026-09-04 09:38:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:39:00 2026-09-04 09:39:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:40:00 2026-09-04 09:40:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:01 2026-09-04 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-04 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-04 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.7% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-04 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.3% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
--- 안전망 ×8(표본)
09:07:01 2026-09-04 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-04 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-04 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-04 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260904_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2630 < conf_floor=0.3300 (span=0.00096 auc=0.546 out_max=0.2630, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00019 auc=0.521 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:33 2026-09-04 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00109 auc=0.539 out_max=0.4351 (n=145) → 보정 재적용
```

### `logs/20260904_HEALTH.log`
```
--- degraded=ON ×8(표본)
10:47:01 2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
10:48:02 2026-09-04 10:48:02 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=269ms | quality=1.00 | cache_age=120s | exceptions_10m=24
10:49:00 2026-09-04 10:49:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=341ms | quality=1.00 | cache_age=178s | exceptions_10m=24
10:50:00 2026-09-04 10:50:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=321ms | quality=1.00 | cache_age=55s | exceptions_10m=33
--- level=CRITICAL ×2(표본)
10:46:00 2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
12:20:00 2026-09-04 12:20:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=369ms | quality=1.00 | cache_age=130s | exceptions_10m=20
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260904_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 1 | 08:40:46 [INFO] 설정 업데이트 완료 |
| 12:00 | 장중 중간점 | 45 | 11:55:27 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1049.90 — 진입 경로가 파라미터를 넘기지 … |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 11 | 15:10:00 [WARNING] 15:10 강제 청산 트리거 @ 15:10:00 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:23 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260904_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 8 | 08:40:48 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 08:55:19 [WARNING] scaler 노후=0h  z경고피처=18개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:19 [WARNING] scaler 노후=0h  z경고피처=18개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1 | 09:57:00 [WARNING] level=WARNING degraded=OFF | latency=267ms | quality=1.00 | cache_age=180s | exceptions_10m=0 |
| 12:00 | 장중 중간점 | 139 | 11:54:00 [CRITICAL] level=CRITICAL degraded=ON | latency=260ms | quality=1.00 | cache_age=39s | exceptions_10m=14 |
| 14:00 | 장중 후반 · 장중 재학습 | 4 | 13:55:01 [WARNING] 슬로우 감지 993ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 36 | 15:04:01 [CRITICAL] level=CRITICAL degraded=ON | latency=334ms | quality=1.00 | cache_age=55s | exceptions_10m=17 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 7 | 15:40:17 [ERROR] 🔴 오늘 외부 진입 총 62건 / 66계약 — 미륵이가 내지 않은 진입이다. 발생원(HTS·MTS·타 프로그램)을 확인할 것 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260904_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 90 | 08:40:30 [INFO] 활성화 | file=logs\crash_fault.log PID=11496 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 127 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 184 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 182 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 315 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 165 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 193 | 15:04:01 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 132 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 45 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260904_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:18 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0293) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 123 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0254) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 227 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0272) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 105 | 09:54:00 [WARNING] 신뢰도 미달 36.1% < 38.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 159 | 11:55:00 [WARNING] 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 14:00 | 장중 후반 · 장중 재학습 | 107 | 13:55:00 [WARNING] 신뢰도 미달 32.1% < 36.3% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 43 | 15:04:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:23 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260903 | 15:40 | 로그 본문 |
| 20260902 | 15:40 | 로그 본문 |
| 20260901 | 15:40 | 로그 본문 |
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260904** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 1. 이상점 1-1 재발 — `session_state.json` P8/EOD 완료 마커 2일 연속 소실 → P2에서 P1로 격상
### 2. 병행 세션 확인 — 오늘 새벽 딥다이브 3건(527·528·529차) 역링크
### 3. 설정 불변식·게이트 인벤토리 — 전부 일치, 신규 이상 없음
### 4. 개장 준비 확인 — A절 체크리스트 전 항목 정상
## 2026-09-04 (MW0601 531차 — 장중 점검: 정체불명 외부 진입 오늘 47건/50계약 — ⚠즉시판단)
### 1. 이상점 1-2(P0, ⚠즉시판단) — 정체불명 외부 진입 대량 유입(47건/50계약, -348,986원), 근본 원인 여전히 미확정
### 2. 이상점 1-3(P1, 격상) — `[ConfFloorGuard]` 자동진입 하한 도달 불가 3거래일 연속 재발
### 3. 그 외 장중 관측 — 신규 이상점 아님 확인
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
.

### 1. 이상점 1-2(P0, ⚠즉시판단) — 정체불명 외부 진입 대량 유입(47건/50계약, -348,986원), 근본 원인 여전히 미확정

- **증상**: 10:43:53~12:25:11 사이 `[체결동기화] 외부진입`(엔진이 등록하지 않은 pending 없이
  들어온 체결)이 47건 발생, 누적 50계약. 오늘 포지션 21건 중 20건이 "외부" 출처
  (-348,986원)이고 엔진 자체 진입은 1건(-3,586원)뿐이다. 12:27 현재 포지션은 FLAT이나
  12:23~12:25에도 신규 유입이 있었다 — 진행 중인 사안이다.
- **원인**: 미확정. 프로그램 후보(미륵이 중복 실행)는 이미 배제됨. 남은 두 가설 — ⓐ HTS/MTS
  등 다른 경로의 실제 수동 거래, ⓑ Chejan 체결과 엔진 pending 등록 사이 레이스(423차 유령
  하드스톱과 같은 계열). 오늘 새로 관찰: 외부진입 20건 전부 계약수 ≤3(MAX_CONTRACTS 이내,
  4계약 이상 0건) — ⓑ 쪽 정황이나 확정 아님. `[Health] level=CRITICAL degraded=ON`
  (58건, 최초 10:46:00)·`exceptions_10m`(0→최대 44) 급증이 외부진입 시작(10:43:53) 직후부터
  겹친다 — 두 현상이 같은 근본 원인을 공유할 가능성(계측 4원칙 ⑤, 아직 인과 미확정).
- **결정**: 코드 변경 없음(장중 규약). F-2로 재상정 — 원인은 좁히지 못했으므로 수정하지
  않는다. 사용자에게 "오늘 계좌를 HTS/MTS 등으로 직접 조작했는지" 재확인을 리포트
  ⚠즉시판단으로 올렸다(O-i4/O-p5 계열, 2026-08 하순부터 미답변 지속).
- **Why**: 2026-09-01 같은 패턴(38건/-1,630,766원)이 15:34:46 마지막 1건에서 오버나이트
  포지션으로 이어져 다음날 -5,299,668원 실현손실을 냈다(절대원칙① 위반). 514차가
  `daily_close()` 잔여포지션 경보(F-A)·FLAT가드 추가시각(F-B)·외부진입 실시간 경보(F-C)를
  배포했지만 **차단은 설계상 하지 않는다**(이미 체결된 사실을 반영하는 지점). 주문 실행
  경로 변경(P0-2: 마감 시 자동 강제청산)은 여전히 주간회의 승인 대기 중이라, 오늘도 같은
  구조적 취약점이 열려 있다.
- **How to apply**: 장후 `ensemble_decisions`/`trades`에서 오늘 10:43~12:25 구간 엔진
  pending 등록 시각과 Chejan 체결 시각을 대조해 ⓑ 가설 직접 검증(F-2). `HealthPolicy`의
  `exceptions_10m` 집계에 예외 유형 태그를 추가하면(G-2) 다음 재발 시 이 상관관계를
  로그만으로 확정할 수 있다.
- **검증**: 라이브 미검증(조사 단계, 코드 변경 없음). 15:10~15:18 구간 재발 여부는 오늘
  장후 점검에서 1차 확인.

### 2. 이상점 1-3(P1, 격상) — `[ConfFloorGuard]` 자동진입 하한 도달 불가 3거래일 연속 재발

- **증상**: 09:00·10:55·11:20 세 차례 발동, 12:27 기준 66분 이상 미복구. 09-02(1-6)→
  09-03(1-2)→오늘로 이어지는 **3거래일 연속** 패턴 — 09-03 리포트가 세운 "3거래일째도
  같은 패턴이면 주간회의 안건 상정 검토" 기준 충족.
- **원인**: 미확정 — 장중은 `predictions` 테이블 조회 금지 구간이라 확인 불가(313차 원칙).
- **결정**: O-p1을 판정 종료하고 이상점 1-3으로 격상. 09-03 리포트가 이미 등록한 F-2
  절차(장후 `predictions` 09:00~12:28 출력 분포 vs 최근 5거래일 비교)를 오늘도 적용.
- **검증**: 오늘 장후 1차 확인, 뚜렷한 이탈이면 주간회의 상정 권고.

### 3. 그 외 장중 관측 — 신규 이상점 아님 확인

- `[PositionFallback]` 40건(외부진입 20건에 딸림) — 기존 F-5 대상, 재상정 안 함.
- 사이저 3계약 vs 실제 2계약 눌림(엔진 진입 1건) — 기존 `sizing_inversion_watch` 표본,
  신규 안건 아님.
- CB② 카운터 최대 2회에서 300초 창 리셋 — 당일정지 미발동, 정상. 실전 전환 기준 ⑤
  미충족 지속(상시 관측).
- GBM 장중 재학습 2회(09:39·12:13, `[ConstOut]` 후속 트리거) — 정상.
- 매분 루프 커버리지 56.3%·12:29~15:10 공백 162분 — **오진**(수집 시각 12:27이 아직
  15:10 이전이라 미래 시간이 공백으로 잡힘). 09-03 521차가 이미 확인한 같은 패턴.
- 메인 스레드 블로킹 3건(최대 3,343ms) — CB⑤ 임계(5,000ms) 미달, 정상.

**세션 헤더**: MW0601 531차. 리포트: `docs/정기점검/매일점검/MW0601-20260904-점검리포트.md`(장중 절).


```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 관측 예정
## 2026-09-04 (MW0601 527·528차 — 탈진 레짐 조사 · C1~C4 사전감지 조사) — 승인 대기
### 관측 예정
## 2026-09-04 (MW0601 529차 — 스윙 피처 착수 · 3_vwap×TrendGate 최적안)
## 2026-09-04 (MW0601 529차 후속 — 채널 3종 구현 완료)
### 남은 것
## 2026-09-04 (MW0601 530차 — 장전 점검)
## 2026-09-04 (MW0601 531차 — 장중 점검)
```

미완료 체크박스 **2427건** (끝에서 30건)
```
- [ ] **526-5 (P2)** P5-13이 `min_days=10`·`min_samples=30`을 **gate 표본만으로** 채우는 시점 재판정
- [ ] **526-6 (P2)** `raw_features_horizon.regime`·`regime_history`가 **③ 제외 라벨**을 저장하는지 확인
- [ ] **525-4 (P2, 유지)** 349차 `VolatilityBurstGuard` 0회 발동 — 임계 재측정.
- [ ] **O-t9** 위 526-4 5항목. 미달이면 배선 결함으로 즉시 격상.
- [ ] **527-A (P1 계측)** 교정판 소진 신호 bear 0건 원인 규명 — `cvd_exhaustion.py` detrend 오실레이터가 단조증가 계열에서
- [ ] **527-B (P2 문서)** 탈진 레짐을 "예약(도달 불가)"로 CLAUDE.md/CORE.md에 명기 + 83차 후속("0회면 하한 1.1") **철회**(병목은 c2) +
- [ ] **528-A [18b]** `RegimeExhaustionGate` hurst<0.45 전제 해제 변형 섀도 — 별도 테이블/컬럼으로 카운터팩추얼. C2형 포착 여부 + 79건 부호 유지 확인.
- [ ] **528-B [16]** `chase_foreign_combo_watch` 판정식 사전등록 — `min_samples=20`(현 23) 且 `min_days=10` 且 일자 p<0.05 且 drop-worst 유지
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
- [ ] **O-i(15:10 재확인)** 오늘 15:10~15:18 구간에 외부진입이 재발하는지 — 재발 시
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
, 재확인)** 첫 거래일 스윙 피처 적재 — `swing_ready_60m` True 비율 · `dist_to_*` 분포 ·
      `[FeatureBuilder] 스윙 피처 오류` 0건. 추가로 `leg_position_watch.py`의 `source_crosscheck`가
      **db vs replay_proxy 불일치 0**인지(배선 검증의 유일 수단).
- [ ] **529-F (P2)** 캠페인 주간 리포트에 P5-14/15/16 렌더링 연결 — 현재는 `leg_position_watch.py` 단독 실행이다
      (`spread_extreme_watch`와 같은 상태). EOD 체인 편입 여부는 주간회의.
- [ ] **529-G (P2)** C 채널 원천 취약성 — TrendGate 활성 상태를 `ensemble_decisions`에 컬럼으로 남길지 검토
      (지금은 로그 파싱이라 `LOG_KEEP_DAYS`가 표본 상한). 계측 4원칙 ②(미측정≠0) 적용 대상.
- [ ] **529-H** 처리군 거래일 25일 도달 시 A 재판정 → `SOFT_DEMOTE_CANDIDATE`면 주간회의 상정(승격 형태는 확정됨).

## 2026-09-04 (MW0601 530차 — 장전 점검)

- [ ] **530-1 / F-1 (P1, 격상)** `data/session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`
      마커가 2일 연속(09-03→09-04) 아침에 소실 — 원인 미규명. 내일(09-05) 아침 재확인해 3일 연속이면
      확정 구조적 결함으로 보고 `main.py:_write_session_state()`/`_read_session_state()` 호출부
      (09-03 기준 3382/3395/4757/4968/12031/13030행 — 재확인 필요)에 진단 로그 추가 착수.
- [ ] **530-2 / G-1 (P2)** `_write_session_state()`가 실제로 기록하는 키 목록 + 파일 mtime을 매 호출마다
      DEBUG 로그로 남긴다 — 530-1 재발 시 어느 호출이 두 키를 지웠는지 로그만으로 특정하기 위한 선행 계측.
      장후 이후 적용.
- [ ] **O-p1** `[ConfFloorGuard] 자동진입 하한 도달 불가`(09:00:00, 보정기 출력상한 0.3479 < 필요 0.4230)
      — 기존 반복 패턴, 오전 중 자연 복귀 여부를 오늘 장중·장후에 판정.
- [ ] **529-2 재확인(오늘 장후)** 스윙 위치 피처 7키 첫 라이브 적재 — `swing_ready_60m` True 비율(개장
      60분 후 ~100% 기대) · `dist_to_*` 분포가 오프라인 재현(179건 run p50 5.7 ATR)과 같은 자릿수인지 ·
      `[FeatureBuilder] 스윙 피처 오류` 로그 0건 · `leg_position_watch.py`의 `source_crosscheck`
      db vs replay_proxy 불일치 0.

## 2026-09-04 (MW0601 531차 — 장중 점검)

- [x] **O-p1** — 판정 종료, 1-3으로 격상(아래 531-2 참조). 오전 중 자연 복귀하지 않고
      66분 이상(11:20~12:27) 미복구, 3거래일 연속 재발 확인.
- [ ] **531-1 / F-2 (P0, 최우선)** 정체불명 외부 진입 오늘 47건/50계약(-348,986원), 20/21
      포지션이 "외부" 출처. 사용자에게 "오늘 계좌를 HTS/MTS 등으로 직접 조작했는지" 확인
      요청(O-i4/O-p5 계열, 2026-08 하순부터 미답변). 장후 `ensemble_decisions`/`trades`에서
      10:43~12:25 구간 엔진 pending 등록 시각 vs Chejan 체결 시각 대조해 레이스 가설(ⓑ) 검증.
- [ ] **531-2 (P2, 고도화)** `HealthPolicy`의 `exceptions_10m` 집계에 예외 유형 태그 추가
      (G-2) — 오늘 외부진입 시작(10:43:53) 직후부터 `[Health] level=CRITICAL degraded=ON`이
      겹쳤는데 정확히 어떤 예외를 세는지 로그로 알 수 없다. 다음 재발 시 상관관계를 로그만
      으로 확정하기 위한 선행 계측.
- [ ] **531-3 (P1)** 1-3(ConfFloorGuard 3거래일 연속) — 장후 `predictions` 테이블 09:00~12:28
      보정기 출력 분포를 최근 5거래일(08-28~09-02)과 비교(09-03 F-2 절차 재사용). 뚜렷한
      이탈이면 주간회의 상정 검토.
- [ ] **O-i(15:10 재확인)** 오늘 15:10~15:18 구간에 외부진입이 재발하는지 — 재발 시
      오버나이트 포지션 위험(절대원칙① 저촉 가능), 장후 최우선 확인 대상.


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

### `data/heartbeat_MW0601_20260904.json` — 243B · 09-04 15:40:30
```json
{
 "pid": 11496,
 "written_at": "2026-09-04T15:40:30",
 "beat_epoch": 1788504027.919165,
 "beat_age_sec": 3.0,
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

- 파일 최종 기록: **09-04 15:48:48**

| 키 | 값 | 수집 대상일(2026-09-04)과 일치 |
|---|---|---|
| `date` | 2026-09-04 | 예 |
| `p8_last_success_date` | 2026-09-04 | 예 |
| `eod_retrain_ok_date` | 2026-09-04 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 108개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260904-점검리포트.md` | 38.9KB | 09-04 12:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_intra.md` | 78.0KB | 09-04 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_pre.md` | 51.1KB | 09-04 09:01 |
| `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md` | 85.0KB | 09-04 07:51 |
| `docs/정기점검/매일점검/MW0601-20260904-스윙피처도입과-3vwap-TrendGate-손익최적안.md` | 10.9KB | 09-04 07:38 |
| `docs/정기점검/매일점검/MW0601-20260904-탈진위치진입-C1C4-사전감지게이트-조사.md` | 17.4KB | 09-04 06:41 |
| `docs/정기점검/매일점검/MW0601-20260904-탈진레짐-보유현황과작동이력-조사.md` | 15.6KB | 09-04 06:23 |
| `docs/정기점검/매일점검/MW0601-20260903-급변장라벨fix-손익과제안-딥다이브.md` | 20.3KB | 09-04 05:50 |

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

1. `logs/20260904_WARN.log`: ERROR 이상 153건
2. `logs/20260904_HEALTH.log`: ERROR 이상 90건
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. 포지션 28건 중 최종청산이 하드스톱·손절 계열 **19건(68%)** — 손절 준수율 확인 필요 (레그 67행)
5. 다레그 포지션 **24건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
6. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
7. `logs/20260904_WARN.log`: **degraded=ON** 8건(표본)
8. `logs/20260904_WARN.log`: **level=CRITICAL** 2건(표본)
9. `logs/20260904_WARN.log`: **ConstOut** 6건(표본)
10. `logs/20260904_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260904_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260904_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260904_LEARNING.log`: **축퇴** 8건(표본)
14. `logs/20260904_HEALTH.log`: **degraded=ON** 8건(표본)
15. `logs/20260904_HEALTH.log`: **level=CRITICAL** 2건(표본)
16. 미커밋 변경 527건 (실질 8건 · 코드 0건 · EOL 파생 510건)
17. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260904*.log` (Windows) / `grep 강제청산 logs/*20260904*.log`*