# 미륵이 증거 다이제스트 — 2026-09-21 / POST

- 생성 2026-09-21 16:18:42 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/peaceful-stoic-rubin/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260921` · `2026-09-21` · `260921` · `0921`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **34개** 파일 · 34개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260921.txt` | 28B | 09-21 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260921.txt` | 28B | 09-21 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260921.txt` | 233B | 09-21 15:53 |
| `force_flat_alert_{DATE}.txt` | 1 | `data/force_flat_alert_20260921.txt` | 1.2KB | 09-21 16:14 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260921.log` | 4.1KB | 09-21 16:14 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260921.log` | 651B | 09-21 16:14 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260921.json` | 244B | 09-21 16:18 |
| `launcher_{DATE}_084001_27124.log` | 1 | `logs/Mireuk_batch/launcher_20260921_084001_27124.log` | 6.8MB | 09-21 15:23 |
| `launcher_{DATE}_152615_8419.log` | 1 | `logs/Mireuk_batch/launcher_20260921_152615_8419.log` | 54.0KB | 09-21 15:47 |
| `launcher_{DATE}_161405_17788.log` | 1 | `logs/Mireuk_batch/launcher_20260921_161405_17788.log` | 9.8KB | 09-21 16:14 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260921.log` | 22.4KB | 09-21 15:46 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260921.log` | 23.4KB | 09-21 15:53 |
| `retrain_intraday_20260701_{DATE}01.log` | 1 | `logs/retrain_intraday_20260701_092101.log` | 4.6KB | 07-01 09:21 |
| `retrain_intraday_{DATE}_100011.log` | 1 | `logs/retrain_intraday_20260921_100011.log` | 5.7KB | 09-21 10:00 |
| `retrain_intraday_{DATE}_121621.log` | 1 | `logs/retrain_intraday_20260921_121621.log` | 5.7KB | 09-21 12:17 |
| `retrain_intraday_{DATE}_141600.log` | 1 | `logs/retrain_intraday_20260921_141600.log` | 3.2KB | 09-21 14:16 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260921.txt` | 43B | 09-21 15:47 |
| `strategy_report_{DATE}_154024.txt` | 1 | `data/daily_reports/strategy_report_20260921_154024.txt` | 2.3KB | 09-21 15:40 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-09-21.jsonl` | 3.6KB | 09-21 16:12 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260921_BACKFILL.log` | 0B | 09-21 16:06 |
| `{DATE}_DATA.log` | 1 | `logs/20260921_DATA.log` | 340.1KB | 09-21 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260921_DEBUG.log` | 222.1KB | 09-21 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260921_HEALTH.log` | 5.3KB | 09-21 14:45 |
| `{DATE}_HOGA.log` | 1 | `logs/20260921_HOGA.log` | 45.0MB | 09-21 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260921_LEARNING.log` | 786.4KB | 09-21 16:14 |
| `{DATE}_MICRO.log` | 1 | `logs/20260921_MICRO.log` | 912.1KB | 09-21 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260921_PROBE.log` | 194.4KB | 09-21 16:14 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260921_REGULAR_COLLECT.log` | 6.7KB | 09-21 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260921_SIGNAL.log` | 501.9KB | 09-21 16:14 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260921_SYSTEM.log` | 809.7KB | 09-21 16:14 |
| `{DATE}_TRADE.log` | 1 | `logs/20260921_TRADE.log` | 3.9KB | 09-21 16:14 |
| `{DATE}_WARN.log` | 1 | `logs/20260921_WARN.log` | 5.3MB | 09-21 16:14 |
| `{DATE}_lv.txt` | 1 | `data/peter_feed/2026-09-21_lv.txt` | 1.2KB | 09-21 16:15 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-09-21_tr.txt` | 35B | 09-21 16:13 |

## 2. 코드·커밋 상태

- HEAD `c48c415` · 브랜치 `v9-dev` · 미커밋 728건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
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
 M collection/cybos/weekly_option_flow.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/constants.py
 M config/dailycheck_targets.json
… 외 688건
```

**당일(2026-09-21) 커밋**
```
c48c415 [MW0601] 612차 후속6: 장후 3건 실행 — 그중 하나는 카드가 거짓말하고 있었다
d04c5d0 [MW0601] 612차: 다이버전스+포지션 탭 데이터 유효성 점검과 리모델링
13cd3c9 [MW0601] 611차 후속2: 돌고 있는지 로그로 못 봤다 + 오전이 통째로 비어 있었다
850cfad [MW0601] 611차 후속: 보조 수집의 오류가 핵심 경로를 막았다 — settings 이름 오류 + 호출 배치
da2506d [MW0601] 611차: 개인은 위클리에서 거래하는데 우리는 먼스리를 보고 있었다 — 7222 위클리 수급 수집
45938ef [MW0601] 610차: 색으로만 나뉘던 경계에 선을 긋는다 — 가격모델 50%·80% 띠 (표시 전용)
1a16a15 [MW0601] 609차: 09:30 이 올라오면 08:50 이 사라졌다 — 두 스테이지를 함께 그린다 (표시 전용)
```

**최근 커밋 12건**
```
c48c415 [MW0601] 612차 후속6: 장후 3건 실행 — 그중 하나는 카드가 거짓말하고 있었다
d04c5d0 [MW0601] 612차: 다이버전스+포지션 탭 데이터 유효성 점검과 리모델링
13cd3c9 [MW0601] 611차 후속2: 돌고 있는지 로그로 못 봤다 + 오전이 통째로 비어 있었다
850cfad [MW0601] 611차 후속: 보조 수집의 오류가 핵심 경로를 막았다 — settings 이름 오류 + 호출 배치
da2506d [MW0601] 611차: 개인은 위클리에서 거래하는데 우리는 먼스리를 보고 있었다 — 7222 위클리 수급 수집
45938ef [MW0601] 610차: 색으로만 나뉘던 경계에 선을 긋는다 — 가격모델 50%·80% 띠 (표시 전용)
1a16a15 [MW0601] 609차: 09:30 이 올라오면 08:50 이 사라졌다 — 두 스테이지를 함께 그린다 (표시 전용)
3067c8b [MW0601] 608차 후속: P7 .bat 이 한글 주석 때문에 안 돌았다 — cmd 는 바이트 오프셋으로 읽는다
79b4664 [MW0601] 608차: P7 홀딩 섀도 사전등록 — 피터리에게서 가져온 게 아니라 그를 보다가 발견한 것
32eb908 [MW0601] 607차: 8월 사료 백필 — 월간 요약이 DB 가 아니라 코드에 박혀 있었다
0b2b36f [MW0601] 606차 후속2: 장후 자동조치 기록 — 제10부 + dev_memory
6c204d2 [MW0601] 606차 후속: 장후 자동조치 — G-3 + F-16 대행
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

### 차단 게이트 전수 인벤토리 — 35개 중 **9개 꺼짐**

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
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260921_HOGA.log` 45.0MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260921.txt`** — 28B · 09-21 15:40:24
```
2026-09-21T15:40:24.865057
```

**`data/daily_close_started_20260921.txt`** — 28B · 09-21 15:40:20
```
2026-09-21T15:40:20.184108
```

**`data/daily_reports/strategy_report_20260921_154024.txt`** — 2.3KB · 09-21 15:40:24
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-21 15:40
========================================================
  버전    : v1.0  (84일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-2.08  MDD(자본대비)=29.9%
  당일      : WR=미측정(거래0건)  PF=미측정
  롤링20일: 누적 -6736500원  Sh=-2.08  MDD(자본대비)=29.9%  MDD(peak대비)=1483.0%
  당일손익 : broker(gross) +0원  수수료 0원  net +0원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)
  PSI/feat: 미측정
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +349,905원  승률 60.0%  합계 +6,998,101원
  등급별 순EV(30일): A=+116,795원(54건,승61%)  BROKER=-2,574,591원(4건,승50%)  C=+24,396원(1건,승100%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=+1,934원(11건)  3m=-10,929원(35건)  5m=-32,721원(7건)  ?=-37,188원(172건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 20분  5일평균 18분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 19.9pt(5일평균 19.4pt)  1분평균변동 0.53pt(5일평균 0.60pt)
--------------------------------------------------------
  진입 퍼널(2026-09-21, 총 363분):
    FLAT 266 → conf미달 72 → CoherenceGate 6 → 게이트차단 18 → 후보 1 → 진입 0
    게이트별: ATR변동성=9  콜드스타트/기타(σ미수집)=3  체크리스트항목미달=3  콜드스타트/기타(DataAnomalyGate)=2  콜드스타트/기타(조건부구간)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 1건
      └ 상세: Hurst미계산(워밍업)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260921.txt`** — 233B · 09-21 15:53:28
```
completed: 2026-09-21 15:53:28
rows: 16288
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 18.3
t_retrain_s: 185.5
t_total_s: 204.3
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/force_flat_alert_20260921.txt`** — 1.2KB · 09-21 16:14:20
```
[ForceFlatGuard] 2026-09-21 15:26:30 WARNING
  라이브 프로세스 정지(포지션은 FLAT) — 오늘 실손해는 없으나 15:40 일일마감·EOD 체인이 실행되지 않는다
  · 하트비트: 파일 194s 전 기록 · 이벤트루프 나이 1s · pid=27876 · strikes=0
  · → 임계 180s 초과 — 라이브 프로세스가 멈춘 것으로 본다
  · 포지션: status=FLAT qty=0 · 최종갱신=2026-09-14T10:52:45.945817 (apply_exit_fill_final:하드스톱(틱))
  · → 파일 날짜가 오늘이 아니다(2026-09-14). FLAT이면 정상(오늘 진입 없음), FLAT이 아니면 전일 포지션 잔류다
[ForceFlatGuard] 2026-09-21 16:14:20 WARNING
  라이브 프로세스 정지(포지션은 FLAT) — 오늘 실손해는 없으나 15:40 일일마감·EOD 체인이 실행되지 않는다
  · 하트비트: 파일 1649s 전 기록 · 이벤트루프 나이 1s · pid=25536 · strikes=0
  · → 임계 180s 초과 — 라이브 프로세스가 멈춘 것으로 본다
  · 포지션: status=FLAT qty=0 · 최종갱신=2026-09-14T10:52:45.945817 (apply_exit_fill_final:하드스톱(틱))
  · → 파일 날짜가 오늘이 아니다(2026-09-14). FLAT이면 정상(오늘 진입 없음), FLAT이 아니면 전일 포지션 잔류다
```

**`data/peter_feed/2026-09-21_lv.txt`** — 1.2KB · 09-21 16:15:25
```
1102 돌파시 매수. 손절가 1099
9:18 AM · Sep 21, 2026

1102 매수체결. 청산가 1109
9:20 AM · Sep 21, 2026

1107 청산가로 변경
9:43 AM · Sep 21, 2026

1107 청산체결 5p 수익.
10:01 AM · Sep 21, 2026

[피터리 - 2026년 9월 21일 증권사 종목리포트 브리핑] 기준: 2026년 9월 18일 13:00 초과 ~ 2026년 9월 21일 13:00 KST ① 한눈에 보는 결론 오늘 리포트에서 가장 강하게 읽히는 변화는 AI 인프라 → 전력·ESS → 반도체 후공정, 그리고 LNG·에너지 인프라, 해외 소비재 현지화다.
1:31 PM · Sep 21, 2026

피터리 - 2026년 9월 21일 증권사 종목리포트 브리핑 ㅡ 축약본
2:06 PM · Sep 21, 2026

[피터리 - 2026년 9월 21일 증권사 산업분석 리포트 브리핑] 기준: 2026년 9월 18일 13:10 초과~2026년 9월 21일 13:10 KST 신규 산업리포트: 9건 발행 증권사: 3곳 분석 산업: 7개 ① 한눈에 보는 결론 오늘 리포트에서 가장 중요한 변화는 LNG 공급 부족, 미국 ESS 후공정 병목, 메모리 가격
2:54 PM · Sep 21, 2026

피터리 - 2026년 9월 21일 증권사 산업분석 리포트 브리핑 ㅡ 축약본
3:27 PM · Sep 21, 2026
```

**`data/peter_feed/2026-09-21_tr.txt`** — 35B · 09-21 16:13:02
```
09:20 L 1102 / 10:01 X 1107 익절
```

**`data/shutdown_normal_20260921.txt`** — 43B · 09-21 15:47:14
```
auto_shutdown
2026-09-21T15:47:14.866352
```

_다이제스트 대상 8/22개 (중요도순). 제외: `retrain_intraday_20260921_121621.log`, `retrain_intraday_20260701_092101.log`, `retrain_intraday_20260921_141600.log`, `20260921_MICRO.log`, `20260921_DATA.log`, `20260921_PROBE.log`, `launcher_20260921_084001_27124.log`, `launcher_20260921_152615_8419.log`_

### `logs/20260921_TRADE.log` — 3.9KB · 32행 · 최종 16:14:48

- 형식 평문 · 시각 인식 32행 · INFO=32

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-21 10:00:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 10:00:07 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-21 10:21:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-09-21 15:27:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 15:27:13 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-21 15:40:21 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
2026-09-21 16:14:42 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-21 16:14:48 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×32

**컴포넌트 상위 15** — `ProfitGuard`×11, `Position`×10, `Sizer`×10, `Hurst 미계산 차단`×1

### `logs/20260921_WARN.log` — 5.3MB · 26004행 · 최종 16:14:52

- 형식 평문 · 시각 인식 25950행 · ERROR=1, WARNING=25949, PLAIN=54

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-09-21 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-21 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-21 16:14:52 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
2026-09-21 16:14:52 [WARNING] SYSTEM: [LiveDBG] _apply update_learning 0ms
2026-09-21 16:14:52 [WARNING] SYSTEM: [LiveDBG] _apply update_efficacy 0ms
2026-09-21 16:14:52 [WARNING] SYSTEM: [LiveDBG] _apply update_trend 47ms
2026-09-21 16:14:52 [WARNING] SYSTEM: [LiveDBG] _apply pnl_history 63ms 총344ms
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `LiveDBG` | 1 | 09:07:14 | 09:07:14 | _tick_header 간격 15531ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=15531 band=ALERT since_pipe_s=0.2 |

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-21 09:07:14 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 15531ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=15531 band=ALERT since_pipe_s=0.2
```

</details>

**WARNING — 태그 22종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 25637 | 08:59:05 | 15:23:34 | paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=31.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 159 | 08:41:09 | 16:14:52 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `출처축` | 20 | 08:41:09 | 16:14:51 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `Health` | 19 | 09:00:02 | 14:44:00 | level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |
| `ERR-DEGRADED` | 16 | 12:16:24 | 12:23:24 | investor_timer_fetch: name 'settings' is not defined |
| `ScalerRefresh` | 14 | 09:05:00 | 14:56:00 | 5분 누적 수익률 +0.678% (임계 ±0.611%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PipePerf` | 12 | 09:00:02 | 14:17:04 | total=2169ms | S0=3ms S1=33ms S2=1ms S3=0ms S4=152ms S5=753ms S6=1155ms S7=49ms S8=23ms |
| `CB⑤` | 12 | 09:00:02 | 14:17:04 | 파이프라인 2169ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `SessionBackfill` | 11 | 08:41:39 | 15:46:21 | OHLCV 불일치 ts=2026-09-18 09:45:00 cols=['open'] existing_source=rt |
| `RESTART` | 8 | 10:00:15 | 15:27:20 | 장중 재시작 감지 10:00 — GapOffset=복원됨  pre_market_scaler=False |
| `MainStallTrace` | 7 | 09:00:06 | 15:46:29 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260921.log |
| `LEVELS` | 7 | 10:01:00 | 15:09:00 | 08:50 훅 미발화(프리장 봉 없음) — 09:30에 소급 산출 |

**채널** — `SYSTEM`×25931, `HEALTH`×19

**컴포넌트 상위 15** — `ChartDBG`×25637, `LiveDBG`×160, `-`×54, `출처축`×20, `Health`×19, `ERR-DEGRADED`×16, `ScalerRefresh`×14, `PipePerf`×12, `CB⑤`×12, `SessionBackfill`×11, `RESTART`×8, `MainStallTrace`×7, `LEVELS`×7, `Contrarian`×6, `HealthPolicy`×5

### `logs/20260921_SYSTEM.log` — 809.7KB · 6068행 · 최종 16:14:53

- 형식 평문 · 시각 인식 6029행 · INFO=6029, PLAIN=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=3604 | 행감지=30s all_threads=True
2026-09-21 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-21 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-21 08:40:50 [INFO] SYSTEM: 미륵이 초기화
2026-09-21 08:40:50 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-18) 종가 버퍼 로드: 384봉
  …
2026-09-21 16:14:51 [INFO] SYSTEM: [Notify] 슬랙 알림 비활성화
2026-09-21 16:14:51 [INFO] SYSTEM: [FreezeWatchdog] 기동 — 하트비트 180s 정체 ×2회 연속 시 os._exit(43) → 런처 재기동 (2026-08-19 동결 사고 대응) | 하트비트파일=data/heartbeat_MW0601_20260921.json
2026-09-21 16:14:51 [INFO] SYSTEM: [System] Qt 이벤트 루프 진입
2026-09-21 16:14:53 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:14:53
2026-09-21 16:19:51 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:19:51
```

</details>

**채널** — `SYSTEM`×6029

**컴포넌트 상위 15** — `CybosInvestorRaw`×1554, `CybosRT-TICK`×916, `TickUI`×399, `BAR-CLOSE`×399, `CVD-ANCHOR`×399, `CybosRT-ROLLOVER`×398, `S6Detail`×363, `PipePerf`×363, `CybosSub`×196, `System`×157, `MicroRegime`×89, `RegimeFingerprint`×68, `OptionChain`×59, `CybosRT-START`×54, `SYSTEM`×50

### `logs/20260921_SIGNAL.log` — 501.9KB · 4529행 · 최종 16:14:50

- 형식 평문 · 시각 인식 4529행 · WARNING=1496, INFO=3033

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-21 16:14:30 [INFO] SIGNAL: [Model] 30m 로드 성공
2026-09-21 16:14:31 [INFO] SIGNAL: [EnsembleGater] 저장된 가중치 복원: C:\Users\82108\PycharmProjects\futures\data\ensemble_gater_weights.json
2026-09-21 16:14:42 [INFO] SIGNAL: [GapOffset] today_open=1094.06 | offset: {}
2026-09-21 16:14:44 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-21 16:14:50 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 924 | 09:00:02 | 15:09:01 | 1m 'macro_vix' scale=0.0412 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 192 | 09:00:00 | 15:09:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 163 | 09:00:00 | 15:09:00 | ts=08:59 horizon=1m age=1m max_z=+13.83(institution_futures_net) extreme=1 adj=1 |
| `WeightCollapse` | 82 | 09:07:01 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 80 | 09:06:00 | 15:01:01 | 신뢰도 미달 36.7% < 37.9% → 강제 X등급 |
| `ScalerRefresh` | 42 | 08:45:09 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 8 | 11:01:00 | 14:15:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 3 | 09:44:00 | 14:43:01 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `PCR-Dampen` | 1 | 09:12:01 | 09:12:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 1 | 13:15:00 | 13:15:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3532 < 필요 0.3810 (conf_floor=0.330, min_conf=0.381, span=0.0077, auc=0.537). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4529

**컴포넌트 상위 15** — `ScalerFloor`×942, `SIGNAL`×726, `MetaGate`×381, `Ensemble`×369, `FQAdj`×359, `ZeroDiag`×350, `Model`×270, `ScalerMonitor`×164, `Checklist`×104, `MicroRegime`×89, `ATR-Horizon`×87, `ScalerRefresh`×82, `WeightCollapse`×82, `DynMC`×76, `InstabilityGate`×67

### `logs/20260921_LEARNING.log` — 786.4KB · 5489행 · 최종 16:14:49

- 형식 평문 · 시각 인식 5489행 · WARNING=1551, INFO=3938

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
2026-09-21 08:40:52 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00030 auc=0.538 out_max=0.2708 (n=85) → 보정 재적용
2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2708 < conf_floor=0.3300 (span=0.00030 auc=0.538 out_max=0.2708, 기저율=0.2706 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-21 16:14:42 [WARNING] LEARNING: [Calibration:ensemble] 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다.
2026-09-21 16:14:42 [INFO] LEARNING: [Calibration:ensemble] 보정기 복원 완료 (n=1184 method=platt fitted=False degenerate=True unreachable=False span=0.00163 auc=0.497 out_max=0.3407)
2026-09-21 16:14:42 [INFO] LEARNING: [Consolidator] 패널티 이력 로드: {'GAP_OPEN': 0.0, 'OTHER': 0.0, 'EXIT_ONLY': 0.0, 'OPEN_VOLATILE': 0.0, 'LUNCH_RECOVERY': 0.0, 'CLOSE_VOLATILE': 0.0, 'STABLE_TREND': 0.0}
2026-09-21 16:14:42 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=SKIP_LOW_SAMPLE
2026-09-21 16:14:49 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=0개 | 교체후보=3개 | CORE안전=⚠️
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 585 | 08:40:52 | 16:14:42 | 축퇴 감지 — span=0.00163 auc=0.527 out_max=0.3610 (기준 auc<0.53 and span<0.020, 기저율=0.3600 n=150) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 508 | 08:40:52 | 16:14:42 | 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 139 | 08:40:52 | 16:14:42 | 축퇴 감지 — span=0.00116 auc=0.367 out_max=0.3379 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 128 | 08:40:52 | 16:14:41 | 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00147 auc=0.600 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 106 | 08:40:52 | 16:14:41 | 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 70 | 08:40:53 | 16:14:39 | 하한 도달불가 — out_max=0.3299 < conf_floor=0.3300 (span=0.00369 auc=0.582 out_max=0.3299, 기저율=0.3280 n=125) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 13 | 08:41:01 | 16:14:42 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 11:41:00 | 11:41:00 | total=386ms raw_fetch=3ms pred_select=3ms pred_update=21ms pred_insert=0ms verified=3 |
| `Retrain` | 1 | 15:40:21 | 15:40:21 | DB pruning 실패: database table is locked |

**채널** — `LEARNING`×5489

**컴포넌트 상위 15** — `Calibration:1m`×1158, `LEARNING`×1158, `Calibration:30m`×1006, `SGD`×365, `sigma`×297, `Calibration:5m`×269, `Calibration:10m`×238, `Bias⚠`×227, `Calibration:3m`×202, `Calibration:15m`×140, `Bias`×119, `OnlineLearner`×69, `MetaConf`×60, `ScalerWarmup`×40, `Calibration:ensemble`×26

### `logs/20260921_HEALTH.log` — 5.3KB · 37행 · 최종 14:45:00

- 형식 평문 · 시각 인식 37행 · WARNING=19, INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0
2026-09-21 09:01:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1044ms | quality=0.86 | cache_age=103s | exceptions_10m=0
2026-09-21 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1085ms | quality=0.74 | cache_age=163s | exceptions_10m=0
2026-09-21 09:03:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=534ms | quality=0.94 | cache_age=39s | exceptions_10m=0
2026-09-21 09:07:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2728ms | quality=1.00 | cache_age=97s | exceptions_10m=0
  …
2026-09-21 14:17:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3926ms | quality=1.00 | cache_age=149s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-21 14:18:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=711ms | quality=1.00 | cache_age=21s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-21 14:44:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=351ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-09-21 14:45:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 310ms (표본 20분)
2026-09-21 14:45:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=471ms | quality=1.00 | cache_age=58s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 19 | 09:00:02 | 14:44:00 | level=WARNING degraded=OFF | latency=2169ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |

**채널** — `HEALTH`×37

**컴포넌트 상위 15** — `Health`×32, `HealthTrend`×5

### `logs/retrain_eod_20260921.log` — 23.4KB · 147행 · 최종 15:53:28

- 형식 평문 · 시각 인식 147행 · WARNING=22, INFO=125

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 15:50:03,564 [INFO] EOD_RETRAIN: =======================================================
2026-09-21 15:50:03,564 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-21 15:50:03,564 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-21 15:50:03,565 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-21 15:50:03,565 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-21 15:53:28,959 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0574 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-21 15:53:28,960 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1167 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-21 15:53:28,963 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-09-21 15:53:28,967 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-21 15:53:28,969 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:35 | 15:52:43 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-21 11:44:00까지)인데 acc.txt=0.4516는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:35 | 15:52:43 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1684봉(91%)이 현행 학습구간 (현행 cutoff=2026-09-21 11:44:00 ≥ 홀드아웃 시작=2026-09-14 12:42:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-21 11:44 >= holdout_start=2026-09-14 12:42 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-0… |
| `RegularFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-09-21 | 최신 2026-09-18 · 기준 7거래일. 복구: python scripts/collect_regular_futures.py --from 20260921 --to 20260921 |
| `BackfillFilter` | 1 | 15:50:08 | 15:50:08 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25813/45604 제외 (418차 결정 1) — 남은 19791행 |
| `UnitMismatch` | 1 | 15:50:08 | 15:50:08 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19791행 제외 (559차 P1'-2) — 남은 18345행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:28 | 15:53:28 | 백필 0행 제외 — 필터가 무효일 수 있다. 16288행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×74, `SIGNAL`×37, `EOD_RETRAIN`×26, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×30, `Retrain`×21, `EOD_RETRAIN`×14, `GuardGhost`×12, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2

### `logs/retrain_intraday_20260921_100011.log` — 5.7KB · 43행 · 최종 10:00:57

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-21 10:00:11,923 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-21 10:00:11,924 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d87c865f.json
  …
2026-09-21 10:00:57,308 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-21 10:00:57,309 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-21 10:00:57,310 [INFO] LEARNING: [Retrain] 완료 | 41.8초 | 성공=6/6 호라이즌
2026-09-21 10:00:57,311 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 45.4s 데이터=4800행
2026-09-21 10:00:57,313 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d87c865f.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:00:25 | 10:00:25 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 26133/45621 제외 (418차 결정 1) — 남은 19488행 |
| `UnitMismatch` | 1 | 10:00:25 | 10:00:25 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19488행 제외 (559차 P1'-2) — 남은 18042행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

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
════════════════════════════════════════════════════
2026-09-21 15:46:11 [WARNING] SYSTEM: [LiveDBG] DynMCPanel.refresh slow 297ms
2026-09-21 15:46:21 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-21 10:00:00 cols=['open', 'low', 'volume'] existing_source=rt
2026-09-21 15:46:21 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-21 10:22:00 cols=['open', 'high', 'volume'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 66 |
| 사이저 호출(`[Sizer]`) | 10 |

### CB③ 판정 가능 시간 — **0분 / 0분 (—)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×10

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×10

### 차단 사유 66건 · 38종

| 건수 | 사유 |
|---|---|
| 14 | 등급X — 미통과 항목: 2_confidence |
| 3 | ATR 0.71pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.69pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.73pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.66pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.64pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.68pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.65pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.52pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.70pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.74pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — StartupWarmup 재가동 초기화 대기(약 2분 남음) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | Hurst 미계산 — 워밍업 중 자동진입 차단 (hurst=0.500) |
| 1 | Hurst 미계산 — 워밍업 중 (hurst=0.500) |
| 1 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×14, `3_vwap`×3, `6_foreign`×3, `4_cvd`×1, `5_ofi`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 60건 · 최대 15531ms · 5초 초과 7건

상위 — 15531ms, 10875ms, 9282ms, 6797ms, 6188ms, 5875ms, 5750ms, 4703ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6797ms | 2169ms | **4628ms (68%)** |
| 09:07:14 | 15531ms | 2728ms | **12803ms (82%)** |
| 09:45:06 | 6188ms | 1000ms | **5188ms (84%)** |
| 09:55:11 | 10875ms | 836ms | **10039ms (92%)** |
| 12:22:09 | 9282ms | 480ms | **8802ms (95%)** |
| 14:00:05 | 5875ms | 932ms | **4943ms (84%)** |
| 15:46:29 | 5750ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260921_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:24 2026-09-21 15:40:24 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 20분 < 하한 25분 — 최근 5거래일 평균 18분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- ConstOut ×1(표본)
14:15:00 2026-09-21 14:15:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(5m=0.3954)
--- PSI ×1(표본)
15:40:20 2026-09-21 15:40:20 [WARNING] SYSTEM: [RegimeFingerprint] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerprint] 기준선 키 불일치` WARNING 이 기동 로그에 있는지 먼저 확인할 것
--- Traceback ×8(표본)
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
--- [SHAP] 슬로우 ×3(표본)
12:08:01 2026-09-21 12:08:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 927ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
14:07:01 2026-09-21 14:07:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1019ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
14:15:01 2026-09-21 14:15:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1308ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-21 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3453ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3453 band=INFO since_pipe_s=NA
08:59:08 2026-09-21 08:59:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3031ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3031 band=INFO since_pipe_s=NA
09:00:06 2026-09-21 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6797 band=WARN since_pipe_s=0.2
09:01:02 2026-09-21 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=0.2
--- 자동 종료 ×1(표본)
16:14:48 2026-09-21 16:14:48 [WARNING] SYSTEM: [System] 오늘 자동 종료 이력이 있어 재시작 후 자동 종료/일일 마감 재실행을 건너뜁니다.
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260921_SYSTEM.log`
```
--- ConstOut ×8(표본)
10:01:00 2026-09-21 10:01:00 [INFO] SYSTEM: [DynMC] ConstOut 고착 conf 제외: [0.34] → 386건 제거 (잔여 1858건)
11:01:00 2026-09-21 11:01:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3846) | 앙상블 제외는 유지
11:10:00 2026-09-21 11:10:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3749) | 앙상블 제외는 유지
12:13:01 2026-09-21 12:13:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4274) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:21 2026-09-21 15:40:21 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 0분 / 파이프라인 0분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-21 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-09-21 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-21 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-21 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:21 2026-09-21 15:40:21 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:21 2026-09-21 15:40:21 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×2(표본)
15:11:15 2026-09-21 15:11:15 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
15:27:50 2026-09-21 15:27:50 [INFO] SYSTEM: [SchedForceExit] 15:27 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=0회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:24 2026-09-21 15:40:24 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:47:14 2026-09-21 15:47:14 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×6(표본)
15:40:24 2026-09-21 15:40:24 [INFO] SYSTEM: [Notify] ℹ️ [15:40:24] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:24 2026-09-21 15:40:24 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 395초
15:40:24 2026-09-21 15:40:24 [INFO] SYSTEM: 자동 종료 예약 — 410초 후 Qt 이벤트 루프 종료
```

### `logs/20260921_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
13:15:00 2026-09-21 13:15:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3532 < 필요 0.3810 (conf_floor=0.330, min_conf=0.381, span=0.0077, auc=0.537). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:44:00 2026-09-21 09:44:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=- raw=STUCK | live(range=0.0150 dir=+1) raw(range=0.0010 dir=+1)
09:45:01 2026-09-21 09:45:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=- raw=STUCK | live(range=0.0190 dir=+1) raw(range=0.0010 dir=+1)
11:01:00 2026-09-21 11:01:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0100 dir=+0)
11:01:00 2026-09-21 11:01:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:01 2026-09-21 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-21 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-21 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-21 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:30 2026-09-21 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
--- 안전망 ×8(표본)
09:07:01 2026-09-21 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-21 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-21 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-21 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260921_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.454 out_max=0.3630 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00014 auc=0.514 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-21 08:40:52 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00030 auc=0.538 out_max=0.2708 (n=85) → 보정 재적용
08:40:52 2026-09-21 08:40:52 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2708 < conf_floor=0.3300 (span=0.00030 auc=0.538 out_max=0.2708, 기저율=0.2706 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260921_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 2 | 10:00:01 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 2 | 15:08:34 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:21 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 16:14

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260921_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 367 | 08:59:05 [WARNING] paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 674 | 08:59:05 [WARNING] paintEvent slow 63.0ms | size=1886x916 candles=15 grid=32.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 10:00 | 장중 초반 | 1247 | 09:54:01 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=70 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 665 | 11:54:01 [WARNING] paintEvent slow 93.0ms | size=1886x1167 candles=188 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marke… |
| 14:00 | 장중 후반 · 장중 재학습 | 956 | 13:54:00 [WARNING] paintEvent slow 93.0ms | size=1988x916 candles=306 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 97 | 15:04:01 [WARNING] _tick_header 간격 2063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2063 band=… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 483 | 15:16:13 [WARNING] paintEvent slow 172.0ms | size=1886x916 candles=385 grid=32.0 spans=0.0 candles=15.0 dir=0.0 regime=16.0 mark… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 14 | 15:40:20 [WARNING] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerp… |
| 15:47 | EOD 재학습(py310_64) 완료 | 11 | 15:46:11 [WARNING] DynMCPanel.refresh slow 297ms |

- 이 로그 생존구간: 08:41 ~ 16:14

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260921_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 91 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=3604 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 200 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 269 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 158 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 167 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 228 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 112 | 15:12:01 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 52 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 6 | 15:42:20 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:42:20 |

- 이 로그 생존구간: 08:40 ~ 16:19

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260921_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:09 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 95 | 08:50:02 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0413) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 225 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0403) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 151 | 09:54:00 [WARNING] 신뢰도 미달 31.9% < 37.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 135 | 11:54:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 121 | 13:54:00 [WARNING] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 102 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:21 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 16:14

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| 20260916 | 17:21 | 로그 본문 |
| 20260915 | 17:41 | 로그 본문 |
| **중앙값** | **17:41** | 기준선 |
| **오늘 20260921** | **16:19** | 로그 본문 |

- 델타 **-82분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 4. 후속 — 이 점검 세션 자신이 `.git/index.lock`을 남겼다 (사용자 조치 1번으로 격상)
### 자가 점검 (갱신)
## 2026-09-21 (MW0601 609차 후속 — 장중 점검)
### 0. 이월 처리 — 장전 이상점 4건 전부 처분
### 1. 신규 발견 — 장중 라이브 배포 3회 중 1회가 8분간 보조 데이터 수집을 막았다
### 2. 오늘 장중재학습 2회 — 정상(30분 주기 아님, WarmupRetrain 이벤트 트리거)
### 3. 자동 적신호 오탐 확인 — "매분 루프 커버리지 56.6%"·"12:30~15:10 공백"은 결함 아님
### 자가유발 여부
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
`/`main` 미접촉 · 작업 종료 시 `.git/index.lock` **존재함**
(STALE 확정, 사용자 조치 1번으로 리포트 최상단에 반영). 리포트는 신규 생성(장전 첫
파일) — append 규약 위반 없음.


## 2026-09-21 (MW0601 609차 후속 — 장중 점검)

**근거**: `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` 장중(intra) 절,
`docs/정기점검/매일점검/evidence_MW0601-20260921_intra.md`.

### 0. 이월 처리 — 장전 이상점 4건 전부 처분

1-1(`.git/index.lock`) ✅해소(재확인 시 락 없음, 회수 주체 미상) · 1-2(`SessionStateDrop`)
🔄지속(오늘 재현 0건이나 마커 자체 부재로 드롭이 애초에 불가능했을 뿐, 근본원인 미해결) ·
1-3(HealthPolicy 선제차단) 🔄지속(11:42 추가 발생 — 개장버스트 한정 아님, 장후 최종판정) ·
1-4(미커밋 3파일) 🔄지속(변경 없음). 미처분 0건.

### 1. 신규 발견 — 장중 라이브 배포 3회 중 1회가 8분간 보조 데이터 수집을 막았다

**증상**: 이 점검 세션과 무관한 별도 작업 세션이 정규장 중(09:56·10:19·12:13)
커밋 3건을 올리고 그때마다 라이브 프로세스를 재기동했다(오늘 총 재기동 5회).
세 번째(`da2506d`, 611차 — 옵션 위클리 수급 수집 신설)가 12:16:24 재기동 이후
`main.py:_fetch_weekly_option_flow()` 내부 `NameError`(`settings` 미정의 —
올바른 별칭은 `runtime_settings`)를 냈고, 이 호출이 OI(미결제약정) 동기화 코드보다
앞에 있어 그 뒤 로직까지 실행되지 못했다. 8분간(12:16:24~12:23:24) 분당 2회,
총 16회 반복.

**원인**: `main.py:4659` 부근 `_fetch_weekly_option_flow()`의
`getattr(settings, "WEEKLY_OPTION_FLOW_ENABLED", False)`가 존재하지 않는
이름(`settings`)을 참조. 게다가 이 NameError가 함수 자체 try 블록 밖에 있어
`[OptionFlow]` 실패 로그 대신 상위 `except`의 `ERR-DEGRADED investor_timer_fetch`
라벨로만 드러나 진단이 늦어졌다.

**결정**: 해당 세션이 12:23:03 커밋(`850cfad`)으로 자체 발견·수정 완료 —
① `settings`→`runtime_settings` 정정 ② 함수 전체를 자체 try로 감싸 실패를
`[OptionFlow]` 이름으로 드러나게 함 ③ 호출 순서를 OI 동기화 뒤로 이동.
회귀 가드 `tests/test_611_option_flow_wiring.py`(5건) 신설. 12:24:07 재기동으로
반영, 이후 재발 0건(12:35 재확인), `option_flow.db` 12:29 갱신 재개 확인.

**Why**: 이 점검 세션은 사후 관측만 했다 — 발생·수정 모두 별도 세션 소관.
다만 국면 체크리스트 B-7("장중 코드 배포·재기동 흔적 없는가")에 해당하는
사건이라 이상점 1-5로 기록해 두는 것이 맞다고 판단했다(장중 배포 자체를
금지하는 것은 이 점검 세션의 행동 규칙이지, 실사용자의 라이브 운영 결정을
평가하는 것은 아니다).

**How to apply**: 조치 불필요(이미 완료). 재발 방지 관행 제안은 리포트 G-1.

**검증**: `grep -n "ERR-DEGRADED" logs/20260921_WARN.log` → 12:23:24 이후 0건.
`ls -la data/db/option_flow.db` → mtime 12:29(수정 후 갱신 재개).
`session_state.json.count=5`로 오늘 재기동 총 5회 교차 확인.

### 2. 오늘 장중재학습 2회 — 정상(30분 주기 아님, WarmupRetrain 이벤트 트리거)

10:00:11(10:00 재기동 직후)·12:16:21(12:16 재기동 직후) 각 6/6 호라이즌 성공.
10:22 재기동 직후에는 재학습 로그 없음 — 직전 재학습(10:00)이 22분 전이라
스킵 조건에 해당하는 것으로 판단(483차 정정 문구와 일치, CLAUDE.md STEP 3).

### 3. 자동 적신호 오탐 확인 — "매분 루프 커버리지 56.6%"·"12:30~15:10 공백"은 결함 아님

증거 수집(12:27)이 장마감(15:10) 전에 실행됐을 뿐이다. 08:55~15:12 구간
"10분 이상 공백 0건"으로 실제 루프 생존은 별도 확인됨.

### 자가유발 여부

이 세션은 라이브 DB를 조회하지 않았다(수집기는 로그·설정·git 전용). 코드 변경
없음. 커밋 없음(장중 규칙). 작업 종료 시 `.git/index.lock` 신규 생성 없음
(`git_lock_guard.py --check` → `OK 정상 — 락 없음`, 종료 직전 재확인).

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 신규 — 606차 후속이 발견 (오늘 거래와 무관)
### 완료 (606차 후속이 닫음)
## 2026-09-21 (MW0601 609차 — 장전 점검)
### 신규 등록
### 확인 완료 (609차가 재확인, 신규 아님)
## 2026-09-21 (MW0601 609차 후속 — 장중 점검)
### 신규 등록
### 확인 완료 (609차 후속이 재확인, 신규 아님)
```

미완료 체크박스 **2788건** (끝에서 30건)
```
- [ ] **F-3 형제 1건 (P2)** `main.py:14880` `logger.critical("[System] 키움 연결 실패 — 종료")`
- [ ] **F-1(538-4) 승인 대기 — 10거래일째 재현** (09-04 532차 최초 등록). 오늘 08:41:09 재현 확인,
- [ ] **O-t4 1일차 관측 완료** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, F-10(600차)
- [ ] **1-2(09-17 access violation) 우선순위 결정 — 여전히 사용자 몫** (2026-09-17 601차 9p-3
- [ ] **미커밋 3파일 지속** — `features/levels/levels_store.py`·`premarket_levels.py`(롤 정책
- [ ] 🔴 **O-i1 (신규, P1) `.git/index.lock` 원인불명 생성 — 12:37 이후 재판정 필요.** 12:27:27
- [ ] **F-1(538-4) 승인 대기 — 11거래일째 재현** (09-04 532차 최초 등록). 09-18 장중에도
- [ ] **O-t4 1일차 관측 지속** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, 장중에도
- [ ] **미커밋 3파일 지속 + dev_memory 2파일 추가 미커밋** — 실질 변경 5파일
- [ ] **G-2 (P2, 신규)** 증거수집기가 실행 "시작 시점"만 락 유무를 자가점검하는데, 수집 종료
- [ ] 🔴 **F-16 (P1, 신규 · 사용자 몫) `.git/index.lock` 회수 필요** — 16:14·16:22 재확인
- [ ] **F-17 (P2, 신규) F-16 완료 후 미커밋 코드 3건 + 오늘 산출물 커밋** — 경로 명시해
- [ ] **P-1 (신규, 사용자 결정) 캠페인 표본 기아 완화 사다리 2단계 적용 여부** — 09-18
- [ ] **O-t7 (2026-09-21 08:41)** `[SessionStateDrop]` 12거래일째 재현 여부 — F-1(538-4)
- [ ] **O-t8 (2026-09-21 09:00, 구 O-t4 2일차)** `[ConfFloorGuard] out_max` — 09-18 저녁
- [ ] **1-2 정정 기록** — 장전 절 "10거래일째"는 영업일 계산 오류(09-04~09-18 실제
- [ ] **606-1 표본 기아 사다리 2단계 — `MetaGate take_ceil 0.570 → 0.52` 적용 여부**
- [ ] **606-2 F-1(538-4) `SessionStateDrop` 완료 마커 캐리오버 수정 승인 여부**
- [ ] **606-3 미커밋 코드 3건 diff 검토 후 커밋** — `features/levels/levels_store.py`
- [ ] **606-4 09-17 access violation 원인 조사 우선순위 결정** — 09-17 이후 라이브
- [ ] **606-5 (P2) `scripts/git_lock_guard.py` 정본/사본 드리프트 — 어느 쪽을 살릴지 결정**
- [ ] **606-6 (P2) 전체 테스트 스위트 access violation 은 teardown 에서 난다 — 재분류**
- [ ] **606-7 화면 코드 세션 — `dashboard/main_dashboard.py` 작업 마친 뒤 실패 5건 재확인**
- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단` 09:01:01·
- [ ] **O-p2 (다음 SessionStateDrop 재현 시)** F-1(538-4) 재현이 정규 거래일 08:41
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
- [ ] **O-i1 (오늘 장후 판정)** `[OptionFlow]` 실패 태그 재발 여부·`option_flow.db`
- [ ] **O-i2 (오늘 장후·내일 판정)** `[LiveDBG] _fetch_investor_data 지연` 경고
- [ ] **G-1 (P2, 저우선, 이 점검 세션 제안)** 장중 라이브 배포 시 "재기동 직후
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
rt_template.md` §9p-3.
      ⚠ **MW0602 는 브랜치가 갈라져 `git pull` 로 못 받는다**(함정 ③) — 필요하면 파일 전달.

## 2026-09-21 (MW0601 609차 — 장전 점검)

**근거**: `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` 장전(pre) 절,
`dev_memory/DECISION_LOG.md` 2026-09-21(609차).

### 신규 등록

- [ ] **O-p1 (오늘 장중·장후 판정)** `[HealthPolicy] Degraded 선제차단` 09:01:01·
      09:03:01 2건 관측(개장 버스트 구간, cause=S6(1155ms)·S5(534ms) — 기존 F-1p류
      S0(모델 리로드) 원인과 다르다). 하루 종일 소수·개장구간 한정이면 정상 판정,
      장중 지속되거나 실제 자동진입 차단으로 이어지면 P1 격상.
- [ ] **O-p2 (다음 SessionStateDrop 재현 시)** F-1(538-4) 재현이 정규 거래일 08:41
      기동인지 비거래일(주말 등) 기동인지 구분해 기록할 것 — 09-21 08:41 로그에는
      경고가 없었으나, 이는 해소가 아니라 **09-20(일, 휴장일) 14:09:42에 이미
      재현되어 넘길 마커가 남아있지 않았기 때문**(609차 확인, 상세는 DECISION_LOG
      2026-09-21 609차 항목 1). 다음 세션은 이 사실을 놓치고 "해소"로 오판하지 말 것.
- [ ] **P2 (신규, 저우선)** `joblib` 버전 문서 불일치 — `CLAUDE.md`는 "1.1.1"로
      적고 있으나 실측 런타임은 최소 8개 이상 일자에 걸쳐 일관되게 `joblib=1.1.0`
      (609차 확인). 운영 영향 없음(장기간 이 값으로 정상 동작 중) — CLAUDE.md
      문구 정정만 필요. 우선순위 낮음.
- [ ] **P2 (신규)** `collect_evidence.py` 자체 실행에서 `git diff` 호출이 실패해
      §2가 "실질 변경 미측정"으로 판정 보류됨(609차, 오늘 pre 실행). 세션이 수동으로
      `git --no-optional-locks diff --numstat -w`를 돌려 우회 확인은 했으나(3파일만
      실질 변경), 수집기 자체의 git diff 호출 방식(타임아웃·인자 등)을 점검해
      재발을 막을 것.

### 확인 완료 (609차가 재확인, 신규 아님)

- [x] `[출처축] PHANTOM_STATE_ARTIFACT` 08:41:09 2건 — 554차 기존 등록 라벨, 신규 아님.
- [x] `[ChartDBG] paintEvent slow` 09:00~09:02 386건 — 기존 F-1p 추적 중, 오늘 건수는
      최근 며칠 대비 낮은 수준.
- [x] 미커밋 707건 중 실질 변경은 606-3 항목의 그 3파일뿐(`levels_store.py`·
      `premarket_levels.py`·`cybos_autologin.py`) — `git diff --stat -w`로 재확인,
      나머지는 EOL 파생.

## 2026-09-21 (MW0601 609차 후속 — 장중 점검)

**근거**: `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` 장중(intra) 절,
`dev_memory/DECISION_LOG.md` 2026-09-21(609차 후속 — 장중 점검).

### 신규 등록

- [ ] **O-i1 (오늘 장후 판정)** `[OptionFlow]` 실패 태그 재발 여부·`option_flow.db`
      적재 지속성 확인 — 12:24 재기동 이후 재발 0건·12:29 갱신 재개 확인했으나
      장후까지 안정적인지 최종 확인 필요.
- [ ] **O-i2 (오늘 장후·내일 판정)** `[LiveDBG] _fetch_investor_data 지연` 경고
      증가 여부 — 611차 커밋이 스스로 예고한 관찰 항목(메인 스레드 약 131ms 추가
      예상). 늘어나면 스레드 분리나 더 긴 스로틀 검토 필요(해당 세션 소관).
- [ ] **G-1 (P2, 저우선, 이 점검 세션 제안)** 장중 라이브 배포 시 "재기동 직후
      신규 경로 로그 실제 출력 확인" 체크리스트를 dev_memory나 별도 문서로
      표준화 — 오늘 1-5(옵션 위클리 수급 NameError)는 회귀 테스트를 갖췄음에도
      런타임 이름공간 문제를 못 잡았다. 예방적 제안이며 급하지 않음.

### 확인 완료 (609차 후속이 재확인, 신규 아님)

- [x] 장전 이상점 1-1~1-4 전부 이월 처리표로 처분 완료(1-1 해소, 1-2·1-3·1-4 지속).
- [x] 오늘 장중재학습 2회(10:00·12:16)는 30분 주기가 아니라 WarmupRetrain
      이벤트(재기동 직후) 트리거 — 정상.

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

### `data/heartbeat_MW0601_20260921.json` — 244B · 09-21 16:18:21
```json
{
 "pid": 14172,
 "written_at": "2026-09-21T16:19:51",
 "beat_epoch": 1789975191.3200762,
 "beat_age_sec": 0.4,
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

### `data/peter_feed/_raw/2026-09-21.jsonl` — 3.6KB · 09-21 16:12:42
```json
JSONL 21행 ⏎ 첫: {"id": "2101828479180489128", "dt": "2026-09-21T00:18:54.000Z", "text": "1102 돌파시 매수. 손절가 1099", "seen_at": "2026-09-21T07:12:43"} | {"id": "2101828910170411378", "dt": "2026-09-21T00:20:36.000Z", "text": "1102 매수체결. 청산가 1109", "seen_at": "2026-09-21T07:12:43"} | {"id": "2101834774499442906", "dt": "2026-09-21T00:43:55.000Z", "text": "1107 청산가로 변경", "seen_at": "2026-09-21T07:12:43"} ⏎ 끝: {"id": "2101921448332017888", "dt": "2026-09-21T06:28:19.000Z", "text": "", "seen_at": "2026-09-21T07:12:43"} | {"id": "2101921538807366062", "dt": "2026-09-21T06:28:41.000Z", "text": "", "seen_at": "2026-09-21T07:12:43"} | {"id": "2101921636379513287", "dt": "2026-09-21T06:29:04.000Z", "text": "", "seen_at": "2026-09-21T07:12:43"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-21 16:14:51**

| 키 | 값 | 수집 대상일(2026-09-21)과 일치 |
|---|---|---|
| `date` | 2026-09-21 | 예 |
| `p8_last_success_date` | 2026-09-21 | 예 |
| `eod_retrain_ok_date` | 2026-09-21 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 156개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 35.9KB | 09-21 12:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_intra.md` | 64.9KB | 09-21 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_pre.md` | 54.1KB | 09-21 09:02 |
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 70.0KB | 09-18 17:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_post.md` | 78.3KB | 09-18 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_intra.md` | 64.9KB | 09-18 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_pre.md` | 56.5KB | 09-18 09:03 |
| `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` | 158.1KB | 09-17 18:05 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json` | 3.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md` | 5.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260918.json` | 38.8KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260918.md` | 32.4KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260918.json` | 118.7KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260918.md` | 194.6KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json` | 3.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md` | 5.0KB | 09-13 14:43 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260921_WARN.log`: ERROR 이상 1건
2. `logs/20260921_WARN.log`: **Traceback** 출현 8건 — 크래시/메모리 계열
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건) — 차단 66건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
5. **SYSTEM 로그가 직전 5거래일 중앙값(17:41)보다 82분 이르게 끝났다** (오늘 16:19) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
6. 메인 스레드 정지 5초 초과 **7건** (최대 15531ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260921_WARN.log`: **ConstOut** 1건(표본)
8. `logs/20260921_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20260921_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260921_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260921_LEARNING.log`: **축퇴** 8건(표본)
12. 미커밋 변경 728건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
13. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260921*.log` (Windows) / `grep 강제청산 logs/*20260921*.log`*