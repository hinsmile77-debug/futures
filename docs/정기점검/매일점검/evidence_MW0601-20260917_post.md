# 미륵이 증거 다이제스트 — 2026-09-17 / POST

- 생성 2026-09-17 16:18:21 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/friendly-funny-mendel/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260917` · `2026-09-17` · `260917` · `0917`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260917.txt` | 28B | 09-17 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260917.txt` | 28B | 09-17 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260917.txt` | 233B | 09-17 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260917.log` | 2.1KB | 09-17 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260917.log` | 356B | 09-17 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260917.json` | 245B | 09-17 15:46 |
| `launcher_{DATE}_053851_9923.log` | 1 | `logs/Mireuk_batch/launcher_20260917_053851_9923.log` | 28.1KB | 09-17 05:46 |
| `launcher_{DATE}_060401_14857.log` | 1 | `logs/Mireuk_batch/launcher_20260917_060401_14857.log` | 868B | 09-17 06:04 |
| `launcher_{DATE}_060438_14978.log` | 1 | `logs/Mireuk_batch/launcher_20260917_060438_14978.log` | 868B | 09-17 06:04 |
| `launcher_{DATE}_060518_15106.log` | 1 | `logs/Mireuk_batch/launcher_20260917_060518_15106.log` | 1.3KB | 09-17 06:10 |
| `launcher_{DATE}_061535_17120.log` | 1 | `logs/Mireuk_batch/launcher_20260917_061535_17120.log` | 8.7MB | 09-17 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260917.log` | 22.5KB | 09-17 14:00 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260917.log` | 21.4KB | 09-17 15:53 |
| `retrain_intraday_20260729_{DATE}50.log` | 1 | `logs/retrain_intraday_20260729_091750.log` | 4.5KB | 07-29 09:18 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260917.txt` | 43B | 09-17 15:47 |
| `strategy_report_{DATE}_154015.txt` | 1 | `data/daily_reports/strategy_report_20260917_154015.txt` | 2.2KB | 09-17 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260917_DATA.log` | 342.6KB | 09-17 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260917_DEBUG.log` | 236.2KB | 09-17 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260917_HEALTH.log` | 3.7KB | 09-17 14:47 |
| `{DATE}_HOGA.log` | 1 | `logs/20260917_HOGA.log` | 51.5MB | 09-17 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260917_LEARNING.log` | 530.8KB | 09-17 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260917_MICRO.log` | 971.6KB | 09-17 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260917_PROBE.log` | 97.0KB | 09-17 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260917_REGULAR_COLLECT.log` | 28.2KB | 09-17 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260917_SIGNAL.log` | 605.2KB | 09-17 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260917_SYSTEM.log` | 790.8KB | 09-17 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20260917_TRADE.log` | 5.0KB | 09-17 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260917_WARN.log` | 7.2MB | 09-17 15:46 |

## 2. 코드·커밋 상태

- HEAD `15c5ee2` · 브랜치 `v9-dev` · 미커밋 661건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
… 외 621건
```

**당일(2026-09-17) 커밋**
```
15c5ee2 [MW0601] 600차: 채점기가 35일 얼어붙어 있었다 — dev 픽스를 이식하고 로그에 출처를 붙인다
67c9e12 [MW0601] 599차: EKS 판정은 시장이 아니라 1초 경주를 재고 있었다 — 계측만 고친다
2cd4acb [MW0601] 598차: 「하루 전체」가 저절로 풀렸다 — 「줌 중인가」를 파생 조건으로 물었다 (표시 전용)
9233caa [MW0601] 597차 후속: 테스트가 592차의 회귀를 잡아냈다 — 「청산」은 낱말이 아니라 레벨로 가른다
8a32af6 [MW0601] 597차: 「끝이 손절로 끝나는 지시」가 통째로 사라졌다 — 8월 사료 13일치가 드러낸 구멍
3507853 [MW0601] 596차 후속: 기록 정정 — 테스트 18건 전부 통과 확인
623ff11 [MW0601] 596차: 오프셋은 하루 안에서도 움직인다 — 오전 창으로 재고, 실측을 기본값으로
c1e9ec3 [MW0601] 문서: DECISION_LOG 592~594차 등록 + 미커밋 점검 기록 누적분
ad63265 [MW0601] 592~594차: 피터 사료 3건 — 목표선 실종 · 레이어 잔상 · 예고 갈래 · 오프셋 실측
73decd2 [MW0601] 595차 후속: 기록 정정 — 라이브 미확인 범위를 실측에 맞게 좁힌다
17be54d [MW0601] 595차: 정규 10100 수집이 엿새 멈춰 있었다 — 트리거 + 감시를 한 쌍으로
```

**최근 커밋 12건**
```
15c5ee2 [MW0601] 600차: 채점기가 35일 얼어붙어 있었다 — dev 픽스를 이식하고 로그에 출처를 붙인다
67c9e12 [MW0601] 599차: EKS 판정은 시장이 아니라 1초 경주를 재고 있었다 — 계측만 고친다
2cd4acb [MW0601] 598차: 「하루 전체」가 저절로 풀렸다 — 「줌 중인가」를 파생 조건으로 물었다 (표시 전용)
9233caa [MW0601] 597차 후속: 테스트가 592차의 회귀를 잡아냈다 — 「청산」은 낱말이 아니라 레벨로 가른다
8a32af6 [MW0601] 597차: 「끝이 손절로 끝나는 지시」가 통째로 사라졌다 — 8월 사료 13일치가 드러낸 구멍
3507853 [MW0601] 596차 후속: 기록 정정 — 테스트 18건 전부 통과 확인
623ff11 [MW0601] 596차: 오프셋은 하루 안에서도 움직인다 — 오전 창으로 재고, 실측을 기본값으로
c1e9ec3 [MW0601] 문서: DECISION_LOG 592~594차 등록 + 미커밋 점검 기록 누적분
ad63265 [MW0601] 592~594차: 피터 사료 3건 — 목표선 실종 · 레이어 잔상 · 예고 갈래 · 오프셋 실측
73decd2 [MW0601] 595차 후속: 기록 정정 — 라이브 미확인 범위를 실측에 맞게 좁힌다
17be54d [MW0601] 595차: 정규 10100 수집이 엿새 멈춰 있었다 — 트리거 + 감시를 한 쌍으로
d9e6a34 [MW0601] 589차 후속2: EOD 가드가 브랜치를 타지 않게 — 상수 없으면 실측값으로
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

_본문 미열람(설정): `20260917_HOGA.log` 51.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260917.txt`** — 28B · 09-17 15:40:15
```
2026-09-17T15:40:15.883936
```

**`data/daily_close_started_20260917.txt`** — 28B · 09-17 15:40:10
```
2026-09-17T15:40:10.087384
```

**`data/daily_reports/strategy_report_20260917_154015.txt`** — 2.2KB · 09-17 15:40:15
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-17 15:40
========================================================
  버전    : v1.0  (82일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-2.15  MDD(자본대비)=29.9%
  당일      : WR=미측정(거래0건)  PF=미측정
  롤링20일: 누적 -6991732원  Sh=-2.15  MDD(자본대비)=29.9%  MDD(peak대비)=1986.0%
  당일손익 : broker(gross) +0원  수수료 0원  net +0원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.002 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.002  vwap_position=0.068
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +349,905원  승률 60.0%  합계 +6,998,101원
  등급별 순EV(30일): A=+80,013원(81건,승62%)  BROKER=-2,574,591원(4건,승50%)  C=+10,973원(7건,승71%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=-8,067원(18건)  3m=-16,894원(51건)  5m=+29,046원(15건)  ?=-35,568원(174건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 21분  5일평균 15분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 17.4pt(5일평균 23.9pt)  1분평균변동 0.63pt(5일평균 0.66pt)
--------------------------------------------------------
  진입 퍼널(2026-09-17, 총 370분):
    FLAT 202 → conf미달 133 → CoherenceGate 14 → 게이트차단 21 → 후보 0 → 진입 0
    게이트별: 기타([차단] SHS-EKS 당일 관망 활성 — )=8  ATR변동성=5  모드필터=4  콜드스타트/기타(DataAnomalyGate)=2  마감시간(신규진입금지)=2
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260917.txt`** — 233B · 09-17 15:53:37
```
completed: 2026-09-17 15:53:37
rows: 15601
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 24.2
t_retrain_s: 188.6
t_total_s: 213.3
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260917.txt`** — 43B · 09-17 15:47:14
```
auto_shutdown
2026-09-17T15:47:14.880698
```

_다이제스트 대상 8/21개 (중요도순). 제외: `20260917_MICRO.log`, `20260917_DATA.log`, `20260917_PROBE.log`, `launcher_20260917_061535_17120.log`, `launcher_20260917_053851_9923.log`, `launcher_20260917_060518_15106.log`, `launcher_20260917_060401_14857.log`, `launcher_20260917_060438_14978.log`_

### `logs/20260917_TRADE.log` — 5.0KB · 30행 · 최종 15:40:11

- 형식 평문 · 시각 인식 30행 · INFO=30

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:40 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-17 05:39:44 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-17 06:16:28 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-17 06:16:33 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-17 07:02:41 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-09-17 14:47:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-17 14:53:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-17 14:54:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-17 14:56:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-17 15:40:11 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×30

**컴포넌트 상위 15** — `Sizer`×19, `ProfitGuard`×6, `Position`×5

### `logs/20260917_WARN.log` — 7.2MB · 34813행 · 최종 15:46:19

- 형식 평문 · 시각 인식 34807행 · CRITICAL=1, ERROR=1, WARNING=34805, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-17 05:39:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-17 05:39:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-09-17 05:39:48 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-17 05:39:48 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-17 15:46:19 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 62.0ms | size=1886x888 candles=310 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=31.0 axes=0.0 cross=0.0 | slow_cnt=33789 total_cnt=35686
2026-09-17 15:46:19 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.0ms | size=1886x888 candles=310 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=16.0 markers=31.0 axes=0.0 cross=0.0 | slow_cnt=33790 total_cnt=35687
2026-09-17 15:46:19 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 109.0ms | size=1886x888 candles=310 grid=47.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=31.0 axes=15.0 cross=0.0 | slow_cnt=33791 total_cnt=35688
2026-09-17 15:46:19 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 188.0ms | size=1886x888 candles=310 grid=78.0 spans=0.0 candles=32.0 dir=0.0 regime=15.0 markers=63.0 axes=0.0 cross=0.0 | slow_cnt=33792 total_cnt=35689
2026-09-17 15:46:19 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 140.0ms | size=1886x888 candles=310 grid=47.0 spans=0.0 candles=15.0 dir=0.0 regime=16.0 markers=62.0 axes=0.0 cross=0.0 | slow_cnt=33793 total_cnt=35690
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `System` | 1 | 05:45:18 | 05:45:18 | 키움 연결 끊김 — 재연결 시도 |
| CRITICAL | `SHS-EKS` | 1 | 09:05:00 | 09:05:00 | Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |

<details><summary>ERROR/System 원문 1건</summary>

```
2026-09-17 05:45:18 [ERROR] SYSTEM: [System] 키움 연결 끊김 — 재연결 시도
```

</details>

<details><summary>CRITICAL/SHS-EKS 원문 1건</summary>

```
2026-09-17 09:05:00 [CRITICAL] SYSTEM: [SHS-EKS] Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)
```

</details>

**WARNING — 태그 19종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 34596 | 05:40:02 | 15:46:19 | paintEvent slow 125.0ms | size=1886x916 candles=411 grid=62.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=31.0 axes=16.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 103 | 05:39:48 | 15:46:13 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 16 | 09:07:00 | 15:01:00 | 5분 누적 수익률 -0.826% (임계 ±0.547%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `CB③-P4` | 14 | 10:24:00 | 13:17:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=16.7%) |
| `Health` | 12 | 09:40:03 | 14:46:01 | level=WARNING degraded=OFF | latency=2996ms | quality=0.94 | cache_age=63s | exceptions_10m=1 | exc_tags=[LEVELS 09:30]×1 |
| `출처축` | 10 | 05:39:48 | 08:56:40 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SHAP` | 9 | 12:13:01 | 15:00:01 | 슬로우 감지 1183ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `SessionBackfill` | 8 | 08:41:08 | 15:46:10 | OHLCV 불일치 ts=2026-09-16 11:02:00 cols=['open'] existing_source=rt |
| `MainStallTrace` | 7 | 07:30:51 | 14:00:04 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260917.log |
| `SHS-EKS` | 7 | 09:05:00 | 11:29:00 | Early Kill Switch 발동 conf_max=34.4% < 발동선=40.1%(mc=42.1%-margin2.0%p) core_pass=0/5봉(측정 0봉) → 일시 관망 (09:20부터 30분 간격 자동 회복 평가, 마감 11:30) |
| `PipePerf` | 6 | 09:40:03 | 13:55:01 | total=2996ms | S0=3ms S1=82ms S2=749ms S3=0ms S4=193ms S5=1895ms S6=37ms S7=33ms S8=5ms |
| `CB⑤` | 6 | 09:40:03 | 13:55:01 | 파이프라인 2996ms 경고 (기준 1000ms) |

**채널** — `SYSTEM`×34795, `HEALTH`×12

**컴포넌트 상위 15** — `ChartDBG`×34596, `LiveDBG`×103, `ScalerRefresh`×16, `CB③-P4`×14, `Health`×12, `출처축`×10, `SHAP`×9, `SessionBackfill`×8, `SHS-EKS`×8, `MainStallTrace`×7, `PipePerf`×6, `CB⑤`×6, `-`×6, `HealthPolicy`×3, `SessionStateDrop`×2

### `logs/20260917_SYSTEM.log` — 790.8KB · 5875행 · 최종 15:47:14

- 형식 평문 · 시각 인식 5843행 · INFO=5843, PLAIN=32

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:13 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18780 | 행감지=30s all_threads=True
2026-09-17 05:39:30 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-17 05:39:30 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-17 05:39:30 [INFO] SYSTEM: 미륵이 초기화
2026-09-17 05:39:30 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-16) 종가 버퍼 로드: 384봉
  …
2026-09-17 15:46:10 [INFO] SYSTEM: [SessionBackfill] 2026-09-17~2026-09-17 chart=411 existing=408 inserted=3 open_fixed=1 mismatch=11
2026-09-17 15:46:40 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:46:40
2026-09-17 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-17 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-17 15:47:14 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5843

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1125, `BAR-CLOSE`×408, `CVD-ANCHOR`×408, `CybosRT-ROLLOVER`×407, `TickUI`×405, `S6Detail`×370, `PipePerf`×370, `System`×154, `MicroRegime`×98, `RegimeFingerprint`×67, `CybosSub`×63, `OptionChain`×49, `IntradayRegime`×41, `SYSTEM`×31

### `logs/20260917_SIGNAL.log` — 605.2KB · 5378행 · 최종 15:40:12

- 형식 평문 · 시각 인식 5378행 · WARNING=1940, INFO=3438

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-17 15:10:17 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-17 15:40:11 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-17 15:40:11 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 46분(12.4%) / DN 86분(23.2%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-17 15:40:12 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-17 age=26m extreme=816 refresh=33 grade_x=135 cb3=0
2026-09-17 15:40:12 [INFO] SIGNAL: [ModelHealth] date=2026-09-17 앙상블유효가동률=68.6% | 파이프라인 370분 | ConstOut 15회/26분 {"3m": {"events": 13, "minutes": 22}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 90분 | 장중재학습 0회 | CB③ ready 286분/370분 (77%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1332 | 09:00:01 | 15:01:01 | 1m 'macro_vix' scale=0.0190 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 156 | 09:00:00 | 14:55:00 | 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 150 | 09:00:00 | 15:02:00 | ts=08:59 horizon=1m age=3m max_z=+4.71(atr_ratio) extreme=3 adj=3 |
| `Checklist` | 146 | 09:06:00 | 15:09:02 | 신뢰도 미달 34.9% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 91 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 42 | 08:45:08 | 08:57:11 | 1m CORE 'cvd_divergence' raw_std≈0(0.0184) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 16 | 09:35:00 | 15:03:02 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 5 | 09:00:00 | 13:56:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4210 (conf_floor=0.330, min_conf=0.421, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `PCR-Dampen` | 2 | 09:17:01 | 10:12:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×5378

**컴포넌트 상위 15** — `ScalerFloor`×1380, `SIGNAL`×740, `MetaGate`×500, `Ensemble`×380, `FQAdj`×367, `ZeroDiag`×351, `Checklist`×192, `Model`×186, `ATR-Horizon`×154, `SHS-EKS`×154, `ScalerMonitor`×151, `MicroRegime`×98, `WeightCollapse`×91, `차단`×91, `InstabilityGate`×81

### `logs/20260917_LEARNING.log` — 530.8KB · 4227행 · 최종 15:40:11

- 형식 평문 · 시각 인식 4227행 · WARNING=814, INFO=3413

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 05:39:31 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00016 auc=0.510 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00089 auc=0.424 out_max=0.3254 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00070 auc=0.473 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.488 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
  …
2026-09-17 15:40:11 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-17 15:40:11 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-17 15:40:11 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-17 15:40:11 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-17 15:40:11 [INFO] LEARNING: [Sigma] EOD sigma_20=0.05832% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 811 | 05:39:31 | 14:27:00 | 축퇴 감지 — span=0.00016 auc=0.510 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 2 | 13:42:00 | 13:55:00 | total=403ms raw_fetch=19ms pred_select=377ms pred_update=2ms pred_insert=1ms verified=3 |
| `DriftAdjuster` | 1 | 15:40:11 | 15:40:11 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 12일) |

**채널** — `LEARNING`×4227

**컴포넌트 상위 15** — `Calibration`×1596, `LEARNING`×1219, `SGD`×369, `sigma`×357, `Bias⚠`×305, `Bias`×130, `MetaConf`×79, `OnlineLearner`×48, `ScalerWarmup`×38, `BiasReset`×32, `SHAP`×15, `ExtremityCorrector`×13, `Consolidator`×11, `DriftAdjuster`×7, `RF`×5

### `logs/20260917_HEALTH.log` — 3.7KB · 25행 · 최종 14:47:00

- 형식 평문 · 시각 인식 25행 · WARNING=12, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 428ms (표본 20분)
2026-09-17 09:40:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2996ms | quality=0.94 | cache_age=63s | exceptions_10m=1 | exc_tags=[LEVELS 09:30]×1
2026-09-17 09:41:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=394ms | quality=0.94 | cache_age=120s | exceptions_10m=0
2026-09-17 09:42:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=429ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-09-17 09:43:02 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=360ms | quality=1.00 | cache_age=58s | exceptions_10m=0
  …
2026-09-17 13:56:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=439ms | quality=1.00 | cache_age=132s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-17 14:06:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=404ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-17 14:07:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=360ms | quality=1.00 | cache_age=57s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-17 14:46:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=415ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-17 14:47:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=514ms | quality=1.00 | cache_age=57s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 12 | 09:40:03 | 14:46:01 | level=WARNING degraded=OFF | latency=2996ms | quality=0.94 | cache_age=63s | exceptions_10m=1 | exc_tags=[LEVELS 09:30]×1 |

**채널** — `HEALTH`×25

**컴포넌트 상위 15** — `Health`×24, `HealthTrend`×1

### `logs/retrain_eod_20260917.log` — 21.4KB · 147행 · 최종 15:53:38

- 형식 평문 · 시각 인식 147행 · WARNING=10, INFO=137

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-17 15:50:03,562 [INFO] EOD_RETRAIN: =======================================================
2026-09-17 15:50:03,563 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-17 15:50:03,564 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-17 15:50:03,565 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-17 15:50:03,565 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-17 15:53:38,103 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0562 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-17 15:53:38,104 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1008 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-17 15:53:38,107 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-09-17 15:53:38,112 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-17 15:53:38,114 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:43 | 15:52:53 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1500봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-16 14:38:00 ≥ 홀드아웃 시작=2026-09-10 12:54:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-16 14:38 >= holdout_start=2026-09-10 12:54 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-16 … |
| `RegularFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-09-17 | 최신 2026-09-16 · 기준 9거래일. 복구: python scripts/collect_regular_futures.py --from 20260917 --to 20260917 |
| `BackfillFilter` | 1 | 15:50:15 | 15:50:15 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 26575/45606 제외 (418차 결정 1) — 남은 19031행 |
| `UnitMismatch` | 1 | 15:50:15 | 15:50:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19031행 제외 (559차 P1'-2) — 남은 17585행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:37 | 15:53:37 | 백필 0행 제외 — 필터가 무효일 수 있다. 15601행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×62, `SIGNAL`×49, `EOD_RETRAIN`×26, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2, `P8`×2

### `logs/retrain_intraday_20260729_091750.log` — 4.5KB · 39행 · 최종 09:18:25

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-29 09:17:50,140 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_117218f1.json
2026-07-29 09:17:52,966 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-29 09:18:25,813 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.39s | old_acc=0.3355)
2026-07-29 09:18:25,816 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-29 09:18:25,816 [INFO] LEARNING: [Retrain] 완료 | 32.8초 | 성공=6/6 호라이즌
2026-07-29 09:18:25,817 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 35.7s 데이터=20000행
2026-07-29 09:18:25,819 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_117218f1.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
════════════════════════════════════════════════════
2026-09-17 15:45:52 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 140.0ms | size=1886x888 candles=310 grid=78.0 spans=0.0 candles=0.0 dir=0.0 regime=15.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=337…
2026-09-17 15:45:52 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 94.0ms | size=1886x888 candles=310 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=3378…
2026-09-17 15:46:10 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-17 08:57:00 cols=['open', 'high', 'volume'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 91 |
| 사이저 호출(`[Sizer]`) | 19 |

### CB③ 판정 가능 시간 — **286분 / 370분 (77%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×3, **3계약**×16

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×19

### 차단 사유 91건 · 25종

| 건수 | 사유 |
|---|---|
| 38 | SHS-EKS 당일 관망 활성 — conf34%미달 |
| 4 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.81pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.80pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 3 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.89pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.2pt > ATR×5.0=9.8pt (시가=1065.76 반등위험) |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.2pt > ATR×5.0=9.6pt (시가=1065.76 반등위험) |

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 51건 · 최대 12625ms · 5초 초과 7건

상위 — 12625ms, 11735ms, 7734ms, 6735ms, 5500ms, 5360ms, 5250ms, 4938ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 07:30:51 | 12625ms | **미측정** | — |
| 08:56:40 | 11735ms | **미측정** | — |
| 09:40:07 | 7734ms | 2996ms | **4738ms (61%)** |
| 12:30:05 | 5360ms | 459ms | **4901ms (91%)** |
| 12:40:05 | 5250ms | 606ms | **4644ms (88%)** |
| 13:55:06 | 6735ms | 1319ms | **5416ms (80%)** |
| 14:00:04 | 5500ms | 756ms | **4744ms (86%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260917_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:14 2026-09-17 15:40:14 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 21분 < 하한 25분 — 최근 5거래일 평균 15분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 42분 · 도달불가 215분 · 재지않음 113분
--- Traceback ×7(표본)
07:30:51 2026-09-17 07:30:51 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260917.log
08:56:40 2026-09-17 08:56:40 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260917.log
09:40:07 2026-09-17 09:40:07 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260917.log
12:30:05 2026-09-17 12:30:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260917.log
--- [SHAP] 슬로우 ×8(표본)
12:13:01 2026-09-17 12:13:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1183ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:44:02 2026-09-17 12:44:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 908ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:13:01 2026-09-17 13:13:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 995ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:48:01 2026-09-17 13:48:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1038ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
05:39:51 2026-09-17 05:39:51 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3297 band=INFO since_pipe_s=NA
06:16:38 2026-09-17 06:16:38 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2312ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2312 band=INFO since_pipe_s=NA
06:16:47 2026-09-17 06:16:47 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2047 band=INFO since_pipe_s=NA
06:16:51 2026-09-17 06:16:51 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=NA
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260917_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-17 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5012) | 앙상블 제외는 유지
09:44:00 2026-09-17 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3552) | 앙상블 제외는 유지
10:34:00 2026-09-17 10:34:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4673) | 앙상블 제외는 유지
10:35:00 2026-09-17 10:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3483) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:12 2026-09-17 15:40:12 [INFO] SYSTEM: [CB③계측] 조건성립 42분 / 판정가능 286분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-17 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:06:00 2026-09-17 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-17 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-17 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:11 2026-09-17 15:40:11 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:11 2026-09-17 15:40:11 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:10 2026-09-17 15:11:10 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:15 2026-09-17 15:40:15 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:47:14 2026-09-17 15:47:14 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×6(표본)
15:40:15 2026-09-17 15:40:15 [INFO] SYSTEM: [Notify] ℹ️ [15:40:15] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:15 2026-09-17 15:40:15 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 404초
15:40:15 2026-09-17 15:40:15 [INFO] SYSTEM: 자동 종료 예약 — 419초 후 Qt 이벤트 루프 종료
```

### `logs/20260917_SIGNAL.log`
```
--- ConfFloorGuard ×8(표본)
09:00:00 2026-09-17 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4210 (conf_floor=0.330, min_conf=0.421, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:49:01 2026-09-17 10:49:01 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3750 ≥ 필요 0.3710 (span=0.0210, auc=0.601)
10:55:00 2026-09-17 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3705 < 필요 0.3710 (conf_floor=0.330, min_conf=0.371, span=0.0221, auc=0.609). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:07:00 2026-09-17 11:07:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3853 ≥ 필요 0.3710 (span=0.0219, auc=0.617)
--- ConstOut ×8(표본)
09:35:00 2026-09-17 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1270 dir=-1)
09:35:00 2026-09-17 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-17 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-17 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1270 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-17 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:07:00 2026-09-17 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-17 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-17 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×8(표본)
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
05:39:10 2026-09-17 05:39:10 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
--- 안전망 ×8(표본)
09:07:00 2026-09-17 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-09-17 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-17 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-17 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260917_LEARNING.log`
```
--- 축퇴 ×8(표본)
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00016 auc=0.510 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00089 auc=0.424 out_max=0.3254 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00070 auc=0.473 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
05:39:31 2026-09-17 05:39:31 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.488 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260917_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:56:16 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:56:16 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:11 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 05:39 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260917_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:08 [WARNING] OHLCV 불일치 ts=2026-09-16 11:02:00 cols=['open'] existing_source=rt |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 347 | 08:53:31 [WARNING] paintEvent slow 93.0ms | size=1886x916 candles=411 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=15.0 marke… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 319 | 08:54:02 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=411 grid=16.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 marker… |
| 10:00 | 장중 초반 | 1426 | 09:54:00 [WARNING] paintEvent slow 125.0ms | size=1886x888 candles=49 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers… |
| 12:00 | 장중 중간점 | 980 | 11:54:00 [WARNING] paintEvent slow 94.0ms | size=1886x888 candles=67 grid=16.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 markers… |
| 14:00 | 장중 후반 · 장중 재학습 | 1304 | 13:54:00 [WARNING] paintEvent slow 79.0ms | size=1886x888 candles=223 grid=16.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 967 | 15:04:00 [WARNING] paintEvent slow 110.0ms | size=1886x888 candles=310 grid=63.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 marker… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 649 | 15:12:00 [WARNING] paintEvent slow 63.0ms | size=1886x888 candles=310 grid=16.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 marker… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 75 | 15:34:00 [WARNING] paintEvent slow 109.0ms | size=1886x888 candles=310 grid=31.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 marke… |
| 15:47 | EOD 재학습(py310_64) 완료 | 16 | 15:45:52 [WARNING] paintEvent slow 140.0ms | size=1886x888 candles=310 grid=78.0 spans=0.0 candles=0.0 dir=0.0 regime=15.0 marke… |

- 이 로그 생존구간: 05:39 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260917_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 46 | 08:36:08 [INFO] 대기 중 | 장 전 — 매크로 수집 대기 (08:45 자동 시작) | 레짐=NEUTRAL | 포지션=FLAT | 08:36:08 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 212 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 264 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 192 | 09:54:01 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 165 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 168 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 150 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 122 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 52 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 7 | 15:41:40 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:40 |

- 이 로그 생존구간: 05:39 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260917_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 40 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0184) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 178 | 08:50:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 265 | 08:55:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 200 | 09:54:01 [WARNING] 신뢰도 미달 35.8% < 37.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 140 | 11:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 155 | 13:54:00 [WARNING] 신뢰도 미달 36.2% < 36.7% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 54 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:11 [INFO] daily reset complete |

- 이 로그 생존구간: 05:39 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260916 | 17:21 | 로그 본문 |
| 20260915 | 17:41 | 로그 본문 |
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| 20260910 | 15:40 | 로그 본문 |
| **중앙값** | **17:21** | 기준선 |
| **오늘 20260917** | **15:47** | 로그 본문 |

- 델타 **-94분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-17 (MW0601 600차 — 보정기 영속화 이식 F-10 + 로그 출처 식별 F-11)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 남은 것 (O-t2, 사용자 지시로 매일 점검 편입)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
`out_max` 가 진입 하한(≈0.42)보다 낮아 매일 아침이 구조적 진입 불가로 시작하고,
그것이 EKS 발동 3조건 중 첫째를 상시 참으로 만들었다(같은 날 이상점 1-4 → 1-9).

### 원인

`save()` 가 `_fitted=False`(축퇴/도달불가 시 해제)에서 **조용히 False** 를 돌려주고
호출부가 `if save():` 로 **성공만** 로깅. 마감 시각에 축퇴면 그날 학습이 통째로 버려지고
로그에 흔적이 없다(계측 4원칙 ④).

🔴 **MW0602 가 2026-08-21 에 같은 것을 발견해 2026-08-23 `2356820`(485차)으로 고쳤고,
그 커밋이 v9-dev 에 오지 않았다.** 다른 원인이 아니라 **동일 버그·미전파**다.

### 결정

**F-10 — 체리픽이 아니라 「이식」으로 한다.**
격리 worktree 시험 적용에서 `learning/calibration.py` 충돌 1건이 났고, 원 커밋 payload 의
`clean_probs`/`clean_labels`/`artifact_n`(MW0602 461차 산물)이 **이 브랜치에 없는 속성**임을
확인했다 — 그대로 넣으면 저장 시 `AttributeError` 로 죽는다. 그 3키만 빼고
상태 3키(`fitted`/`degenerate`/`unreachable`)와 게이트·load·else 분기를 이식했다.

**F-11 — 로그 문구를 고치지 않고 LoggerAdapter 로 접두만 갈아끼운다.**
`_TaggedCalibLogger.process()` 가 선두 `[Calibration]` 토큰만 치환한다. 호출부 15곳의
메시지는 **한 글자도 안 고쳤다** — 15곳을 직접 수정하면 `%` 인자 정렬이 깨질 위험이 있고,
그 실패는 logging 이 조용히 삼킨다(599차에서 겪은 계열).

**G-5(조율 예외 조항) 종료** — 사용자 결정. 전파는 건별 체리픽으로 한다. 재론 금지.

### Why

ⓐ **이식 > 체리픽**: 두 브랜치가 500커밋 넘게 갈라져 같은 파일의 전제가 다르다.
   "붙는다"와 "맞다"는 다르며, 이번엔 붙어도 런타임에 죽었을 것이다.
ⓑ **판정식은 이번에도 안 건드린다**: 축퇴 임계(`DEGENERATE_AUC_MIN=0.53` /
   `SPAN_MIN=0.02`)는 매매 정책이라 주간회의 몫이다. 테스트가 그 불변을 고정한다.
ⓒ **F-11 이 없으면 진단이 또 틀린다**: 같은 날 §3 이 축퇴 전이 1,591회를 앙상블 보정기
   단독인 것처럼 집계하는 오류를 냈다(제2부-E §7 자체 정정). 출처 미식별은 계측 결함이다.

### How to apply

- 실반영은 **다음 정규 재기동**부터다(장 마감 후 파일 수정 — 라이브 무영향).
- 다음 거래일 15:40 에 `저장 완료` **또는** `저장 건너뜀` 중 하나가 반드시 나와야 한다(O-t3).
- 이식 시 `dev` 원 커밋을 다시 가져올 일이 있으면 **461차 3키를 반드시 제외**할 것 —
  `test_600::test_payload_has_no_dev_only_keys` 가 재발을 막는다.

### 검증

`tests/test_600_calibrator_log_identity.py` **14건 신설**, 인접 포함 **80건 전부 통과**
(`test_484`(이식본) · `test_599` · `test_482` · `test_523`).
실측 확인:
- 축퇴 상태 저장 **False → True**, 복원 시 `fitted=False` 보존(1-7 동시 해소).
- 로그 접두 `[Calibration:ensemble]` · `[Calibration:3m]` · 이름 없으면 종전과 동일.
- 같은 입력에서 이름 유무와 무관하게 `calibrate()` 출력 **1e-12 이내 동일**.

🔴 **테스트가 이번에도 두 번 잡았다 — 둘 다 이 세션의 실수다.**
① `dev` 전용 키 검사가 **내 주석**을 코드로 오인해 실패(599차 대시보드 테스트와 **같은
   실수 반복**). → 주석 제거 후 검사. **이 패턴을 다음에도 조심할 것.**
② legacy 폴백 테스트가 난수 표본을 써서 실패했는데, 알고 보니 **가드의 정상 동작**이었다
   (load 직후 축퇴 재평가가 `fitted` 를 내린다 — 이식 코드 주석이 명시한 계약).
   순위 정보가 있는 표본(`_trained_informative`)으로 교체.

### 남은 것 (O-t2, 사용자 지시로 매일 점검 편입)

**F-10 이 1-4(EKS)를 해소한다는 보장은 없다.** `dev` 는 같은 픽스 이틀 뒤에도
`out_max=0.3479 < 0.4420` 을 관측했다. 그래서 **2026-09-24 장후(배포 후 5거래일)** 에
사전등록 기준으로 판정한다 — 5거래일 내내 `out_max` 가 0.35 이하 고착이면
**Platt 축퇴 자체가 별개 문제로 확정**되고 보정기 함수형 교체(주간회의)로 넘어간다.
기준 전문은 `NEXT_TODO.md` O-t2.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-17 (MW0601 장중 점검 — 예약작업, 병행 세션 후속)
## 2026-09-17 (MW0601 599차 — F-4·F-5·G-2 구현 완료, 미커밋)
### 이 세션이 지킨 제약 (다음 세션이 확인할 것)
### 테스트 작성 교훈 (재발 방지)
### 15:45 후속 — 병행 세션 번호 충돌
### 16:20 채점기 딥다이브 (사용자 지시, 장 마감 후)
### 16:40 브랜치 대조 — 왜 v9-dev 에만 발생하는가 (사용자 지시)
### 17:0x 600차 — F-10·F-11 구현 완료 + O-t2 기한 등록 (사용자 지시)
```

미완료 체크박스 **2752건** (끝에서 30건)
```
- [ ] **O-i1 (오늘 장후 판정)** 15:10까지 `[SHS-EKS]` 해제 로그 출현 여부 —
- [ ] **O-i2 (오늘 장후 판정)** 15:10까지 진입 0건 유지 여부 — 자동 0건 예상.
- [ ] **O-i3 (오늘 장후 판정)** `[ConfFloorGuard]` 오후 도달가능/불가 전환 횟수 —
- [ ] **O-i4 (다음 장중 판정 — 1-4의 반증 가능한 예측)** 다음 거래일 09:00
- [ ] **O-i5 (오늘 장후 판정)** `MainStallTrace` 스냅샷 누적(12:31 현재 3/20) —
- [ ] 1-3 (브로커 접속 끊김 로그 "키움" 오표기) — 지속. F-3 계획 유효.
- [ ] F-1 후속 / F-2 후속 — 장중 미재현. 판정 예정일 "다음 장전" 유지.
- [ ] **F-4·F-5 적용 승인** (장후) — 매매 정책·임계 무변경, 로그·계상만. 미적용 시
- [ ] **G-2 승인** (2026-09-15 등록, **3일째 대기**) — EKS 미해제 확정 시 대시보드
- [ ] `.git/index.lock` — 12:28 생성분은 **HOLD(판정보류)**. **지우지 말 것.**
- [ ] **기준 ⑤(CB② 발동 1회 관측)** — 진입 0건 3일 연속이라 **관측 기회 자체가 생기지
- [ ] **기준 ①(4주 통산 수익률 양수)** — 거래 없는 날이 4주 창에 누적되면 분자·분모가
- [ ] **(장후 확인)** 이 세션의 1-5(09:40:07 메인 스레드 7,734ms 정지, CB⑤ 사각 4,738ms/61%)
- [ ] **(장후 확인)** `.git/index.lock`(12:28 생성) 최종 처리 여부 — 이 세션 종료 시점
- [ ] 🔴 **사용자 조치: 커밋** — 이 세션은 커밋하지 않았다(SKILL.md §6).
- [ ] **599-A (P1) 재기동 후 라이브 확인** — 장 마감 후 정규 재기동으로 반영된다.
- [ ] **599-B (P2) `_is_cold_start` 판정식 재설계 — 표본 대기** (459차 F2 연장선)
- [ ] **F-7 (P1, 신규) `peter_paste` DB 폴백에 `*_measured`/`*_fallback` 동반 컬럼** —
- [ ] **O-i6 (장후 판정, 신규)** `test_456_wave1_stats_and_shs::
- [ ] 🔴 **이 저장소에서 로그 검증에 `caplog` 를 쓰지 말 것** — 프로젝트 로거가 루트로
- [ ] 🔴 **F-9 (P1, 신규) 앙상블 보정기 35일 동결 — 저장 실패가 조용하다**
- [ ] **F-9-A (P1) 저장 실패 가시화** — `save()` 가 실패 사유(`not fitted` / `sklearn 없음` /
- [ ] **G-4 보강 (주간회의 안건에 정량 근거 첨부)** — EKS 회복 창(09:20~11:30)이
- [ ] **O-t1 (다음 거래일)** F-9-A 배포 전이라면, 15:40 에 저장 성공 로그가 뜨는지만
- [ ] 🔴 **F-10 (P1, 신규) `2356820` 체리픽 — 보정기 영속화 복구 (dev → v9-dev)**
- [ ] **O-t2 (F-10 적용 후 관측, 사전등록)** **F-10 이 1-4(EKS)를 자동 해소한다고 쓰지 말 것.**
- [ ] **F-11 (P2, 신규) `[Calibration]` 로그에 보정기 인스턴스 이름 접두**
- [ ] **G-5 (주간회의 안건 — 결정 아님) 멀티PC 조율 폐기 결정에 「안전·계측 결함 픽스」 예외 신설 검토**
- [ ] 🔴 **O-t2 (기한: 2026-09-24 장후 — 배포 후 5거래일) Platt 축퇴가 별개 문제인지 확정**
- [ ] **O-t3 (다음 거래일 15:40)** `[Calibration:ensemble] 앙상블 보정기 저장 완료` **또는**
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
rep=XFIX` 한 번 훑기**. 상시 조율이 아니라 **주 1회 단방향 조회**다.

**근거**: 리포트 「제2부-E. 왜 v9-dev 에서만 발생하는가 — dev 브랜치 대조」.
핵심: 다른 원인이 아니라 **동일 버그 · 미전파**. 두 PC 의 동결 아티팩트가 똑같이
3,008B 에서 출발했고, MW0602 는 수정 다음 날 5,299B 로 갱신 재개, **MW0601 은 아직 3,008B**.
⚠ MW0602 의 로그·DB 는 이 PC 에 없어(런타임 산출물 미커밋) **코드 대조 + MW0602 자신의
기록**에 근거했다. MW0602 라이브 재현은 하지 않았다.

### 17:0x 600차 — F-10·F-11 구현 완료 + O-t2 기한 등록 (사용자 지시)

- [x] **F-10 완료** — `dev 2356820` 영속화 복구를 v9-dev 로 **이식**(맹목 체리픽 아님).
      ⚠ **원 커밋 그대로는 못 쓴다**: payload 의 `clean_probs`/`clean_labels`/`artifact_n`
      (MW0602 461차 산물)이 **이 브랜치에 없는 속성**이라 넣으면 저장 시 AttributeError.
      격리 worktree 시험 적용에서 `learning/calibration.py` 충돌 1건 확인 → 그 3키만 빼고
      상태 3키(`fitted`/`degenerate`/`unreachable`)만 이식. `main.py` 는 자동 병합.
      실측 검증: 축퇴(fitted=False) 상태 저장 **False → True**, 복원 시 `fitted=False` 보존
      (축퇴 저장본 부활 위험 1-7 동시 해소).
- [x] **F-11 완료** — `_TaggedCalibLogger`(LoggerAdapter)로 `[Calibration]` 선두 토큰만
      인스턴스 이름으로 치환. **호출부 메시지 15곳을 한 글자도 안 고쳤다**(회귀 위험 최소).
      이름 없으면 출력이 종전과 **바이트 단위 동일**. 실측: `[Calibration:ensemble]` ·
      `[Calibration:3m]` · (이름 없음) `[Calibration]`.
- [x] **G-5 종료** — [2026-09-17 사용자 결정] *"조율 폐기 결정 문제는 내가 지금 필요사항
      건건히 체리픽으로 진행하므로 필요 없음."* ⇒ **멀티PC 조율 예외 조항 신설은 하지
      않는다.** 전파는 사용자가 건별 체리픽으로 수행한다. 재론 금지.

- [ ] 🔴 **O-t2 (기한: 2026-09-24 장후 — 배포 후 5거래일) Platt 축퇴가 별개 문제인지 확정**
      **사용자 지시로 매일 점검에서 확인 후 거론할 항목이다.**
      관측 대상: 매 거래일 09:00 `[ConfFloorGuard]` 의 `out_max` 와 `[Calibration:ensemble]
      보정기 복원 완료` 의 `n=` .
      **사전등록 판정 기준**
      ⓐ `n=` 이 매일 증가 → F-10 정상 동작 확인(영속화 복구). 안 늘면 F-10 실패이므로
         **먼저 그것부터 본다**(판정 전제).
      ⓑ 09:00 `out_max` 가 상승해 그날 `min_conf`(≈0.37~0.44)를 **1회라도 넘으면**
         → 「동결이 원인」 확정, 이상점 1-4(EKS)·1-9 해소 경로 확보.
      ⓒ 5거래일 내내 `out_max` 가 **0.35 이하 고착**이면
         → **Platt 축퇴 자체가 별개 문제로 확정**. 영속화는 원인이 아니었다는 뜻이며,
           보정기 **함수형 교체**(Isotonic/구간별) 또는 진입 하한 재설계로 넘어간다
           (= 제2부-D §5 의 C갈래). 그 경우 매매 정책이므로 주간회의 안건.
      ⓓ 중간(오르긴 하는데 min_conf 미달)이면 **판정 보류 + 5거래일 연장**, 추세 기울기를
         함께 기록한다.
      ⚠ **근거**: `dev` 는 같은 픽스 **이틀 뒤(2026-08-25)에도** `out_max=0.3479 < 필요
        0.4420` 을 관측했다(그쪽 O-4). 즉 ⓒ 가 실현될 가능성이 실재한다.
      ⚠ 휴장일이 있으면 기한은 그만큼 밀린다 — **거래일 5일**이 기준이다.
      ⚠ 표본 5일이다. ⓒ 확정 시에도 **함수형 교체를 바로 하지 말 것** — 297차
        `hurst_gate_shadow` 순서대로 섀도 선행.

- [ ] **O-t3 (다음 거래일 15:40)** `[Calibration:ensemble] 앙상블 보정기 저장 완료` **또는**
      `저장 건너뜀` 중 **하나가 반드시** 나오는지. 둘 다 없으면 F-10 배선이 끊긴 것이다
      (종전에는 성공 시에만 찍혀 부재를 읽어야 알 수 있었다 — 그 결함을 닫은 것이 F-10).

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

### `data/heartbeat_MW0601_20260917.json` — 245B · 09-17 15:46:59
```json
{
 "pid": 20064,
 "written_at": "2026-09-17T15:46:59",
 "beat_epoch": 1789627615.0648847,
 "beat_age_sec": 4.3,
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

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-17 15:53:38**

| 키 | 값 | 수집 대상일(2026-09-17)과 일치 |
|---|---|---|
| `date` | 2026-09-17 | 예 |
| `p8_last_success_date` | 2026-09-17 | 예 |
| `eod_retrain_ok_date` | 2026-09-17 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 148개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` | 113.4KB | 09-17 16:09 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra_1228.md` | 64.7KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra.md` | 67.4KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_pre.md` | 55.9KB | 09-17 09:02 |
| `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md` | 93.3KB | 09-16 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_post.md` | 76.2KB | 09-16 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_intra.md` | 65.2KB | 09-16 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_pre.md` | 52.4KB | 09-16 09:01 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json` | 3.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md` | 5.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json` | 2.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md` | 4.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json` | 38.8KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md` | 32.1KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json` | 115.4KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260911.md` | 189.4KB | 09-11 15:56 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260917_WARN.log`: ERROR 이상 2건
2. `logs/20260917_WARN.log`: **Traceback** 출현 7건 — 크래시/메모리 계열
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건) — 차단 91건. 최다 차단 사유: `SHS-EKS 당일 관망 활성 — conf34%미달` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
5. **SYSTEM 로그가 직전 5거래일 중앙값(17:21)보다 94분 이르게 끝났다** (오늘 15:47) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
6. 메인 스레드 정지 5초 초과 **7건** (최대 12625ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260917_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20260917_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260917_SIGNAL.log`: **ConstOut** 8건(표본)
10. `logs/20260917_LEARNING.log`: **축퇴** 8건(표본)
11. 미커밋 변경 661건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260917*.log` (Windows) / `grep 강제청산 logs/*20260917*.log`*