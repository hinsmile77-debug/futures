# 미륵이 증거 다이제스트 — 2026-09-18 / POST

- 생성 2026-09-18 16:17:12 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/exciting-adoring-clarke/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260918` · `2026-09-18` · `260918` · `0918`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **23개** 파일 · 23개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260918.txt` | 28B | 09-18 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260918.txt` | 28B | 09-18 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260918.txt` | 233B | 09-18 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260918.log` | 1.9KB | 09-18 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260918.log` | 216B | 09-18 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260918.json` | 245B | 09-18 15:46 |
| `launcher_{DATE}_084001_32654.log` | 1 | `logs/Mireuk_batch/launcher_20260918_084001_32654.log` | 7.7MB | 09-18 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260918.log` | 5.7KB | 09-18 11:03 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260918.log` | 38.2KB | 09-18 16:14 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260918.txt` | 43B | 09-18 15:47 |
| `strategy_report_{DATE}_154019.txt` | 1 | `data/daily_reports/strategy_report_20260918_154019.txt` | 2.0KB | 09-18 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260918_DATA.log` | 343.0KB | 09-18 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260918_DEBUG.log` | 224.1KB | 09-18 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260918_HEALTH.log` | 3.5KB | 09-18 14:56 |
| `{DATE}_HOGA.log` | 1 | `logs/20260918_HOGA.log` | 46.5MB | 09-18 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260918_LEARNING.log` | 311.3KB | 09-18 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260918_MICRO.log` | 885.0KB | 09-18 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260918_PROBE.log` | 94.6KB | 09-18 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260918_REGULAR_COLLECT.log` | 6.7KB | 09-18 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260918_SIGNAL.log` | 504.6KB | 09-18 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260918_SYSTEM.log` | 714.5KB | 09-18 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20260918_TRADE.log` | 3.0KB | 09-18 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260918_WARN.log` | 6.4MB | 09-18 15:46 |

## 2. 코드·커밋 상태

- HEAD `e808409` · 브랜치 `v9-dev` · 미커밋 673건 · 실질 변경 11건 · 코드(.py) 3건 · EOL 파생 591건 (추적변경 602 · 미추적 71 · 삭제 6 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 3.8시간 · git 프로세스 0개 → **커밋 불가 상태**
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260828.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md`, `features/levels/levels_store.py`, `features/levels/premarket_levels.py`, `scripts/cybos_autologin.py`
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
… 외 633건
```

**당일(2026-09-18) 커밋**
```
(당일 커밋 없음 — ⚠ 인덱스락 잔존으로 **커밋 불가 상태였음**. 미조치가 아니다)
```

**최근 커밋 12건**
```
e808409 [MW0601] 603차 후속2: .ps1/.bat BOM 을 정반대로 넣었다
5f4f94d [MW0601] 603차 후속: MW0602 수신 자동화 — 「푸시해두면 올라오나」의 답은 아니오다
5aa3138 [MW0601] 603차: 9월 초순 백필 — 그가 「맥점」이라 쓴 줄이 파서에 없었다
562f096 [MW0601] 602차 후속: peter-feed 고아 브랜치 — 사료를 코드와 다른 길로 보낸다
c114420 [MW0601] 602차: 피터 사료 수집 자동화 1단계 — 그리고 당일 실데이터가 드러낸 파서 결함 2건
1e17131 [MW0601] 601차 후속: 리포트 제10부 — 장후 자동조치 결과 기록
e14dd2e [MW0601] 601차 후속: 장후 자동조치 — F-3·F-6·F-14·F-15 + O-i6 확정
15c5ee2 [MW0601] 600차: 채점기가 35일 얼어붙어 있었다 — dev 픽스를 이식하고 로그에 출처를 붙인다
67c9e12 [MW0601] 599차: EKS 판정은 시장이 아니라 1초 경주를 재고 있었다 — 계측만 고친다
2cd4acb [MW0601] 598차: 「하루 전체」가 저절로 풀렸다 — 「줌 중인가」를 파생 조건으로 물었다 (표시 전용)
9233caa [MW0601] 597차 후속: 테스트가 592차의 회귀를 잡아냈다 — 「청산」은 낱말이 아니라 레벨로 가른다
8a32af6 [MW0601] 597차: 「끝이 손절로 끝나는 지시」가 통째로 사라졌다 — 8월 사료 13일치가 드러낸 구멍
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

_본문 미열람(설정): `20260918_HOGA.log` 46.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260918.txt`** — 28B · 09-18 15:40:19
```
2026-09-18T15:40:19.123024
```

**`data/daily_close_started_20260918.txt`** — 28B · 09-18 15:40:08
```
2026-09-18T15:40:08.719984
```

**`data/daily_reports/strategy_report_20260918_154019.txt`** — 2.0KB · 09-18 15:40:19
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-18 15:40
========================================================
  버전    : v1.0  (83일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-2.18  MDD(자본대비)=29.9%
  당일      : WR=미측정(거래0건)  PF=미측정
  롤링20일: 누적 -7084517원  Sh=-2.18  MDD(자본대비)=29.9%  MDD(peak대비)=2265.2%
  당일손익 : broker(gross) +0원  수수료 0원  net +0원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.001  vwap_position=0.056
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +349,905원  승률 60.0%  합계 +6,998,101원
  등급별 순EV(30일): A=+86,857원(67건,승57%)  BROKER=-2,574,591원(4건,승50%)  C=+10,973원(7건,승71%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=-16,801원(16건)  3m=-15,637원(47건)  5m=-32,721원(7건)  ?=-35,568원(174건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 14분  5일평균 16분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 15.1pt(5일평균 21.5pt)  1분평균변동 0.44pt(5일평균 0.64pt)
--------------------------------------------------------
  진입 퍼널(2026-09-18, 총 370분):
    FLAT 270 → conf미달 76 → CoherenceGate 11 → 게이트차단 13 → 후보 0 → 진입 0
    게이트별: ATR변동성=13
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260918.txt`** — 233B · 09-18 15:53:03
```
completed: 2026-09-18 15:53:03
rows: 15950
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 23.4
t_retrain_s: 156.1
t_total_s: 180.0
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260918.txt`** — 43B · 09-18 15:47:15
```
auto_shutdown
2026-09-18T15:47:15.116351
```

_다이제스트 대상 8/16개 (중요도순). 제외: `20260918_DATA.log`, `20260918_PROBE.log`, `launcher_20260918_084001_32654.log`, `20260918_DEBUG.log`, `20260918_REGULAR_COLLECT.log`, `mainstall_traceback_20260918.log`, `force_flat_guard_20260918.log`, `freeze_sentinel_20260918.log`_

### `logs/20260918_TRADE.log` — 3.0KB · 16행 · 최종 15:40:15

- 형식 평문 · 시각 인식 16행 · INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-18 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-18 09:44:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 09:45:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 13:02:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-18 13:55:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 14:00:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 14:04:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 14:05:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-18 15:40:15 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×16

**컴포넌트 상위 15** — `Sizer`×13, `ProfitGuard`×2, `Position`×1

### `logs/20260918_WARN.log` — 6.4MB · 30828행 · 최종 15:46:32

- 형식 평문 · 시각 인식 30822행 · WARNING=30822, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-18 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-18 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-09-18 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-18 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-18 15:46:08 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=410 inserted=1 open_fixed=1 mismatch=4
2026-09-18 15:46:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2937ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2228 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=2937 band=INFO since_pipe_s=2230.3
2026-09-18 15:46:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.0ms | size=1886x916 candles=411 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=15.0 markers=16.0 axes=0.0 cross=0.0 | slow_cnt=30708 total_cnt=31215
2026-09-18 15:46:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=411 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=31.0 axes=0.0 cross=0.0 | slow_cnt=30709 total_cnt=31216
2026-09-18 15:46:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 47.0ms | size=1886x916 candles=411 grid=15.0 spans=0.0 candles=0.0 dir=16.0 regime=0.0 markers=16.0 axes=0.0 cross=0.0 | slow_cnt=30710 total_cnt=31217
```

</details>

**WARNING — 태그 20종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 30710 | 09:00:40 | 15:46:32 | paintEvent slow 109.0ms | size=1886x916 candles=16 grid=62.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=47.0 cross=0.0 | slow_cnt=1 total_cnt=266 |
| `LiveDBG` | 33 | 08:41:08 | 15:46:11 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 16 | 09:05:00 | 14:50:00 | 5분 누적 수익률 -0.397% (임계 ±0.193%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `CB③-P4` | 14 | 10:49:00 | 15:09:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=23.3%) |
| `Health` | 13 | 09:00:01 | 14:55:01 | level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |
| `SessionBackfill` | 11 | 08:41:39 | 15:46:08 | OHLCV 불일치 ts=2026-09-17 08:57:00 cols=['open', 'high', 'volume'] existing_source=rt |
| `PipePerf` | 4 | 09:00:01 | 11:03:03 | total=1713ms | S0=5ms S1=11ms S2=0ms S3=0ms S4=87ms S5=446ms S6=1112ms S7=43ms S8=9ms |
| `CB⑤` | 4 | 09:00:01 | 11:03:03 | 파이프라인 1713ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:09 | 08:41:09 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-17 → 2026-09-18)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `MainStallTrace` | 2 | 09:00:05 | 11:03:07 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260918.log |
| `HealthPolicy` | 2 | 09:01:00 | 11:04:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1713ms quality=1.00 cache=0s exc10m=0) | cause=S6(1112ms) |

**채널** — `SYSTEM`×30809, `HEALTH`×13

**컴포넌트 상위 15** — `ChartDBG`×30710, `LiveDBG`×33, `ScalerRefresh`×16, `CB③-P4`×14, `Health`×13, `SessionBackfill`×11, `-`×6, `PipePerf`×4, `CB⑤`×4, `출처축`×2, `SessionStateDrop`×2, `MainStallTrace`×2, `HealthPolicy`×2, `Brier`×2, `SHAP`×1

### `logs/20260918_SYSTEM.log` — 714.5KB · 5364행 · 최종 15:47:15

- 형식 평문 · 시각 인식 5339행 · INFO=5339, PLAIN=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18848 | 행감지=30s all_threads=True
2026-09-18 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-18 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-18 08:40:50 [INFO] SYSTEM: 미륵이 초기화
2026-09-18 08:40:50 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-17) 종가 버퍼 로드: 382봉
  …
2026-09-18 15:46:08 [INFO] SYSTEM: [SessionBackfill] 08:45 개장 체결 보정 ts=2026-09-18 08:45:00 rt O=1087.28/V=451 → chart O=1087.92/V=832
2026-09-18 15:46:08 [INFO] SYSTEM: [SessionBackfill] 2026-09-18~2026-09-18 chart=411 existing=410 inserted=1 open_fixed=1 mismatch=4
2026-09-18 15:47:15 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-18 15:47:15 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-18 15:47:15 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5339

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×921, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×405, `S6Detail`×370, `PipePerf`×370, `System`×100, `MicroRegime`×77, `RegimeFingerprint`×67, `OptionChain`×43, `-`×22, `CybosSub`×21, `SYSTEM`×14

### `logs/20260918_SIGNAL.log` — 504.6KB · 4437행 · 최종 15:40:16

- 형식 평문 · 시각 인식 4437행 · WARNING=1727, INFO=2710

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-18 15:10:01 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-18 15:40:15 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-18 15:40:15 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 91분(24.6%) / DN 69분(18.6%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-18 15:40:16 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-18 age=23m extreme=810 refresh=35 grade_x=66 cb3=0
2026-09-18 15:40:16 [INFO] SIGNAL: [ModelHealth] date=2026-09-18 앙상블유효가동률=68.9% | 파이프라인 370분 | ConstOut 13회/26분 {"3m": {"events": 10, "minutes": 20}, "5m": {"events": 3, "minutes": 6}} | WeightCollapse 89분 | 장중재학습 0회 | CB③ ready 261분/370분 (71%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1302 | 09:00:02 | 14:50:01 | 1m 'macro_vix' scale=0.0241 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 120 | 09:01:00 | 12:57:01 | ts=09:00 horizon=1m age=1m max_z=+7.35(va_bandwidth) extreme=7 adj=5 |
| `Model` | 96 | 09:01:00 | 12:57:01 | 1m 극단 z-score 7개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `WeightCollapse` | 92 | 09:07:01 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 85 | 09:06:00 | 14:55:01 | 신뢰도 미달 34.4% < 37.9% → 강제 X등급 |
| `ScalerRefresh` | 18 | 08:45:09 | 08:48:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0197) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 13 | 09:35:01 | 14:59:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4437

**컴포넌트 상위 15** — `ScalerFloor`×1320, `SIGNAL`×740, `Ensemble`×379, `FQAdj`×369, `ZeroDiag`×357, `MetaGate`×231, `ScalerMonitor`×121, `Checklist`×117, `Model`×102, `WeightCollapse`×92, `ATR-Horizon`×79, `MicroRegime`×77, `차단`×67, `ScalerRefresh`×58, `InstabilityGate`×48

### `logs/20260918_LEARNING.log` — 311.3KB · 2993행 · 최종 15:40:15

- 형식 평문 · 시각 인식 2983행 · WARNING=182, INFO=2801, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:40:51 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-18 08:40:51 [INFO] LEARNING: [Calibration:3m] 도달불가 해소 — out_max=0.3414 < conf_floor=0.3300 (n=85) → 보정 재적용
2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00005 auc=0.509 out_max=0.3445 (기준 auc<0.53 and span<0.020, 기저율=0.3444 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-09-18 15:40:15 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-18 15:40:15 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-18 15:40:15 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-18 15:40:15 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-18 15:40:15 [INFO] LEARNING: [Sigma] EOD sigma_20=0.04972% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 57 | 08:40:51 | 10:25:00 | 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 57 | 08:40:51 | 12:48:00 | 하한 도달불가 — out_max=0.3217 < conf_floor=0.3300 (span=0.00569 auc=0.660 out_max=0.3217, 기저율=0.3187 n=160) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 19 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.3008 < conf_floor=0.3300 (span=0.00132 auc=0.564 out_max=0.3008, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 17 | 08:40:51 | 11:02:00 | 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 15 | 08:40:52 | 08:40:58 | 축퇴 감지 — span=0.00011 auc=0.527 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 9 | 08:40:52 | 08:40:59 | 하한 도달불가 — out_max=0.2388 < conf_floor=0.3300 (span=0.00259 auc=0.614 out_max=0.2388, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 7 | 09:39:00 | 13:19:00 | 하한 도달불가 — out_max=0.3205 < conf_floor=0.3300 (span=0.01146 auc=0.576 out_max=0.3205, 기저율=0.3150 n=200) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `DriftAdjuster` | 1 | 15:40:09 | 15:40:09 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 13일) |

**채널** — `LEARNING`×2983

**컴포넌트 상위 15** — `LEARNING`×1199, `SGD`×369, `sigma`×357, `Bias⚠`×336, `Bias`×125, `Calibration:1m`×112, `Calibration:30m`×112, `MetaConf`×78, `OnlineLearner`×60, `ScalerWarmup`×40, `Calibration:5m`×37, `BiasReset`×35, `Calibration:3m`×33, `Calibration:10m`×30, `Calibration:15m`×18

### `logs/20260918_HEALTH.log` — 3.5KB · 26행 · 최종 14:56:00

- 형식 평문 · 시각 인식 26행 · WARNING=13, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0
2026-09-18 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=682ms | quality=1.00 | cache_age=102s | exceptions_10m=0
2026-09-18 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 364ms (표본 20분)
2026-09-18 09:33:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=362ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-09-18 09:34:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=289ms | quality=1.00 | cache_age=59s | exceptions_10m=0
  …
2026-09-18 13:21:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=318ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-09-18 14:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=377ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-18 14:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=314ms | quality=1.00 | cache_age=57s | exceptions_10m=0
2026-09-18 14:55:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=339ms | quality=1.00 | cache_age=184s | exceptions_10m=0
2026-09-18 14:56:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=303ms | quality=1.00 | cache_age=58s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 13 | 09:00:01 | 14:55:01 | level=WARNING degraded=OFF | latency=1713ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |

**채널** — `HEALTH`×26

**컴포넌트 상위 15** — `Health`×25, `HealthTrend`×1

### `logs/retrain_eod_20260918.log` — 38.2KB · 355행 · 최종 16:14:20

- 형식 평문 · 시각 인식 181행 · WARNING=14, INFO=167, PLAIN=174

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 15:50:03,236 [INFO] EOD_RETRAIN: =======================================================
2026-09-18 15:50:03,237 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-18 15:50:03,237 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-18 15:50:03,237 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-18 15:50:03,237 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
리포트 저장: C:\Users\82108\PycharmProjects\futures\data\mae_mfe_report.txt
2026-09-18 16:14:20,017 [INFO] EOD_RETRAIN: [검증 캠페인] 요약: 게이트 ablation 리포트=OK | 호라이즌 conf-층화 검정=OK | 검증 캠페인 판정 리포트=OK | 피처셋 건강 리포트=OK | CVD 앵커 대조 리포트=OK | 조기청산 반사실 [49]=OK | 라우팅 밴드 성과 [D9-B]=OK | 방향 처분 실험 [40-B]=OK | 섀도우 TB 재학습=OK | 분위 회귀 재학습=OK | 메타라벨 분류기 재학습=OK | MAE/MFE 분석=OK
2026-09-18 16:14:20,121 [INFO] EOD_RETRAIN: 판정 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\validation_campaign_report_20260918.md
2026-09-18 16:14:20,124 [INFO] EOD_RETRAIN: 피처셋 건강 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\featureset_health_report_20260918.md
2026-09-18 16:14:20,125 [INFO] EOD_RETRAIN: =======================================================
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:37 | 15:52:21 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1501봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-17 14:38:00 ≥ 홀드아웃 시작=2026-09-11 12:54:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-17 14:38 >= holdout_start=2026-09-11 12:54 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-17 … |
| `UnitMismatch` | 4 | 15:50:14 | 16:07:33 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19415행 제외 (559차 P1'-2) — 남은 17969행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `BackfillFilter` | 2 | 15:50:14 | 16:07:36 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 26194/45609 제외 (418차 결정 1) — 남은 19415행 |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-09-18 | 최신 2026-09-17 · 기준 9거래일. 복구: python scripts/collect_regular_futures.py --from 20260918 --to 20260918 |
| `RegimeFingerprint` | 1 | 15:53:03 | 15:53:03 | 백필 0행 제외 — 필터가 무효일 수 있다. 15950행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×62, `EOD_RETRAIN`×44, `SIGNAL`×43, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×173, `ScalerFloor`×36, `Retrain`×21, `EOD_RETRAIN`×18, `검증 캠페인`×14, `RF`×9, `ShadowTB`×8, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `MetaLabelClf`×6

### `logs/20260918_MICRO.log` — 885.0KB · 2362행 · 최종 15:38:41

- 형식 평문 · 시각 인식 2362행 · DEBUG=2362

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-18 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1087.40/1 ask1=1088.08/3 mp={'microprice_tick': 1087.57, 'midprice_tick': 1087.74, 'depth_bias_tick': -0.2209} mlofi_tick=None queue=None
2026-09-18 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1087.30/2 ask1=1088.08/3 mp={'microprice_tick': 1087.612, 'midprice_tick': 1087.69, 'depth_bias_tick': -0.0576} mlofi_tick=-2.3333 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1087.28/1 ask1=1088.08/3 mp={'microprice_tick': 1087.48, 'midprice_tick': 1087.68, 'depth_bias_tick': -0.1708} mlofi_tick=-3.8167 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1087.28/1 ask1=1088.08/3 mp={'microprice_tick': 1087.48, 'midprice_tick': 1087.68, 'depth_bias_tick': -0.1708} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-18 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1087.30/2 ask1=1088.08/3 mp={'microprice_tick': 1087.612, 'midprice_tick': 1087.69, 'depth_bias_tick': -0.0321} mlofi_tick=4.0167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-09-18 15:34:50 [DEBUG] MICRO: [MICRO-TICK] #195400 bid1=1086.80/1 ask1=1087.04/2 mp={'microprice_tick': 1086.88, 'midprice_tick': 1086.92, 'depth_bias_tick': -0.1289} mlofi_tick=2.5333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-18 15:35:08 [DEBUG] MICRO: [MICRO-TICK] #195500 bid1=1085.28/1 ask1=1086.76/1 mp={'microprice_tick': 1086.02, 'midprice_tick': 1086.02, 'depth_bias_tick': -0.0323} mlofi_tick=-1.8333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_r…
2026-09-18 15:35:46 [DEBUG] MICRO: [MICRO-TICK] #195600 bid1=1084.80/2 ask1=1085.00/1 mp={'microprice_tick': 1084.9333, 'midprice_tick': 1084.9, 'depth_bias_tick': 0.2903} mlofi_tick=1.0 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-18 15:36:42 [DEBUG] MICRO: [MICRO-TICK] #195700 bid1=1083.52/1 ask1=1084.30/1 mp={'microprice_tick': 1083.91, 'midprice_tick': 1083.91, 'depth_bias_tick': 0.551} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-18 15:38:41 [DEBUG] MICRO: [MICRO-TICK] #195800 bid1=1084.00/2 ask1=1084.28/1 mp={'microprice_tick': 1084.1867, 'midprice_tick': 1084.14, 'depth_bias_tick': 0.2143} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
```

</details>

**채널** — `MICRO`×2362

**컴포넌트 상위 15** — `MICRO-TICK`×1978, `MICRO-MINUTE`×384

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
════════════════════════════════════════════════════
2026-09-18 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-18 09:45:00 cols=['open'] existing_source=rt
2026-09-18 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-18 13:45:00 cols=['open'] existing_source=rt
2026-09-18 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-18 14:00:00 cols=['open'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 67 |
| 사이저 호출(`[Sizer]`) | 13 |

### CB③ 판정 가능 시간 — **261분 / 370분 (71%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×13

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×13

### 차단 사유 67건 · 40종

| 건수 | 사유 |
|---|---|
| 10 | 등급X — 미통과 항목: 2_confidence |
| 5 | ATR 0.73pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.69pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.68pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.72pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.74pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.71pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 6.2pt > ATR×5.0=5.1pt (시가=1085.80 반등위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=5.7pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=5.3pt (시가=1085.80 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.7pt > ATR×5.0=5.5pt (시가=1085.80 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×10

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 21건 · 최대 8437ms · 5초 초과 2건

상위 — 8437ms, 5157ms, 4078ms, 4046ms, 3843ms, 3703ms, 3672ms, 3671ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:05 | 5157ms | 1713ms | **3444ms (67%)** |
| 11:03:07 | 8437ms | 2965ms | **5472ms (65%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260918_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:18 2026-09-18 15:40:18 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 14분 < 하한 25분 — 최근 5거래일 평균 16분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 140분 · 재지않음 230분
--- [Brier] 과신 ×2(표본)
13:45:00 2026-09-18 13:45:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.354 > 0.35
13:46:00 2026-09-18 13:46:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.351 > 0.35
--- [SHAP] 슬로우 ×1(표본)
12:09:01 2026-09-18 12:09:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1143ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-18 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3485ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3485 band=INFO since_pipe_s=NA
08:59:27 2026-09-18 08:59:27 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band=INFO since_pipe_s=NA
09:00:05 2026-09-18 09:00:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5157 band=WARN since_pipe_s=0.1
09:01:01 2026-09-18 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2282ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2282 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260918_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:01 2026-09-18 09:35:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3801) | 앙상블 제외는 유지
09:44:00 2026-09-18 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3988) | 앙상블 제외는 유지
11:38:00 2026-09-18 11:38:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3664) | 앙상블 제외는 유지
11:47:01 2026-09-18 11:47:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3562) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:16 2026-09-18 15:40:16 [INFO] SYSTEM: [CB③계측] 조건성립 205분 / 판정가능 261분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-18 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-09-18 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-09-18 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:16:00 2026-09-18 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:15 2026-09-18 15:40:15 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:15 2026-09-18 15:40:15 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:08 2026-09-18 15:11:08 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:19 2026-09-18 15:40:19 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:47:15 2026-09-18 15:47:15 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×6(표본)
15:40:19 2026-09-18 15:40:19 [INFO] SYSTEM: [Notify] ℹ️ [15:40:19] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:19 2026-09-18 15:40:19 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 401초
15:40:19 2026-09-18 15:40:19 [INFO] SYSTEM: 자동 종료 예약 — 416초 후 Qt 이벤트 루프 종료
```

### `logs/20260918_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-18 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:01 2026-09-18 09:35:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0160 dir=-1)
09:35:01 2026-09-18 09:35:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:01 2026-09-18 09:35:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:02 2026-09-18 09:36:02 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0160 dir=-1)
--- WeightCollapse ×8(표본)
09:07:01 2026-09-18 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-18 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-18 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-18 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.421
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:30 2026-09-18 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
--- 안전망 ×8(표본)
09:07:01 2026-09-18 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-18 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-18 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-18 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260918_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00008 auc=0.509 out_max=0.2375 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00051 auc=0.565 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00005 auc=0.509 out_max=0.3445 (기준 auc<0.53 and span<0.020, 기저율=0.3444 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:51 2026-09-18 08:40:51 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3217 < conf_floor=0.3300 (span=0.00569 auc=0.660 out_max=0.3217, 기저율=0.3187 n=160) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

### `logs/retrain_eod_20260918.log`
```
--- ConstOut ×1(표본)
??:??:?? | `[51]` | `아직 미확인` | ConstOut 호라이즌 건강도 |
--- 축퇴 ×1(표본)
??:??:?? | `[45]` | `cal_guard_flap_watch` | 축퇴 가드 플래핑 (게이지) |
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260918_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 14:00 | 장중 후반 · 장중 재학습 | 5 | 13:54:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:15 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260918_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 278 | 08:59:27 [WARNING] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 931 | 08:59:27 [WARNING] _tick_header 간격 2719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2719 band… |
| 10:00 | 장중 초반 | 1011 | 09:54:00 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=70 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 832 | 11:54:01 [WARNING] paintEvent slow 109.0ms | size=1886x916 candles=190 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 marker… |
| 14:00 | 장중 후반 · 장중 재학습 | 910 | 13:54:00 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=310 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 941 | 15:04:00 [WARNING] acc30m 단계 전환: RESTRICTED → WATCH (acc=30.0%) |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 705 | 15:12:00 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=388 grid=31.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 95 | 15:34:00 [WARNING] paintEvent slow 62.0ms | size=1886x916 candles=409 grid=0.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers… |
| 15:47 | EOD 재학습(py310_64) 완료 | 9 | 15:46:08 [WARNING] OHLCV 불일치 ts=2026-09-18 09:45:00 cols=['open'] existing_source=rt |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260918_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=18848 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 131 | 08:49:12 [INFO] alive ticks=963 code=A056A close=1086.18 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 186 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 167 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 168 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 168 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 147 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 121 | 15:12:00 [INFO] #89000 code=A056A raw_time=151200 parsed=15:12:00 price=1083.88 vol=1 bid1=1083.86 ask1=1083.98 flag=50 side=… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 55 | 15:34:01 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 7 | 15:41:08 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:08 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260918_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0197) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 85 | 09:00:00 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 232 | 09:00:00 [WARNING] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3910 (conf_floor=0.330, min_conf=0.391, span=0.0063, auc=0.550). 이 상태에… |
| 10:00 | 장중 초반 | 125 | 09:54:00 [WARNING] 신뢰도 미달 32.1% < 37.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 113 | 11:57:01 [WARNING] 1m 'macro_vix' scale=0.0430 → floor=0.10 적용 (z-score 폭발 방지) |
| 14:00 | 장중 후반 · 장중 재학습 | 130 | 13:56:01 [WARNING] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 38 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:15 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260917 | 20:33 | 로그 본문 |
| 20260916 | 17:21 | 로그 본문 |
| 20260915 | 17:41 | 로그 본문 |
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| **중앙값** | **17:41** | 기준선 |
| **오늘 20260918** | **15:47** | 로그 본문 |

- 델타 **-114분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-18 (MW0601 605차 — 장중 점검)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 자가유발 여부
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
찰.

1. **진입 0건 — 원인은 게이트 정상 차단**. 차단 37건(26종): 신뢰도 미달(등급X) 10건, ATR<1.0pt(변동성 부족) 11건, OPEN_VOLATILE(시가이격 과다) 8건, 기타 8건. 압도적 단일 사유 없음 — 확정 결론 보류(313차, 표본 반나절).
2. **장전 이상점 1-1~1-3 전부 지속 재현, 새 변화 없음** — SessionStateDrop 11거래일째, ConfFloorGuard out_max=0.3479 동일값 재확인(1일차 관찰), 미커밋 3파일 그대로(+dev_memory 2파일 append로 미커밋 5건 실질 변경).
3. **신규 — `.git/index.lock` 원인불명 생성**. 12:26:45 증거수집 완료 시점엔 없었음(수집기 자가점검 "락을 만들지 않았다" 확인). 12:27:27 0바이트 락 발견. `scripts/git_lock_guard.py --check`를 12:27·12:30 두 차례 실행 — 둘 다 `HOLD 판정보류`(나이 103초/160초 ≤ 임계 600초). 이 세션의 git 명령은 전부 `--no-optional-locks` 읽기전용(`branch`/`status`/`log`)뿐이라 이 세션이 만든 락이 아님을 확인. 원인 미상 — STALE 재판정은 12:37 이후로 이월.
4. **매분 루프 커버리지 자동경보 오독 방지** — 수집기가 "12:28~15:10 163분 공백"을 자동 적신호로 냈으나, 이는 증거수집 시각(12:26)이 낮이라 미래 시간이 아직 로그에 없는 것일 뿐 실제 파이프라인 정지가 아님. 실제 경과구간(09:00~12:27)엔 10분 이상 공백 0건.
5. **STEP3 GBM 재학습 0회 — 정상**. `[WarmupRetrain]`(08:41:09) 예약 → `[PreRetrain]`(08:55:10)이 "전일 EOD 성공, 중복 학습 불필요"로 스킵. 이후 `[ConstOut]` 재학습 트리거 5회(3m×4, 5m×1) 전부 "BiasReset uniform fallback 구간, GBM 출력 아님"으로 억제. CLAUDE.md 483차 문서정정("30분마다"는 코드에 없음)과 일치하는 정상 패턴.
6. **메인 스레드 정지 5초 초과 2건(09:00:05 5,157ms · 11:03:07 8,437ms)** — CB⑤ 사각 잔차 65~67%. 482차 F-3 섀도 계측 대상, 신규 아님.
7. **CB③-P4(30분 정확도 기준, 차단 비활성) 10:49 NORMAL→RESTRICTED(acc=23.3%)** — 차단 기능은 설정상 꺼져 있어 오늘 진입에 영향 없음. 계측만 정상 동작.

### 원인

1: STEP6(체크리스트·등급 판정)에서 신뢰도·변동성·시가이격 게이트가 정상 작동해 걸러진 것. 2: 이미 규명된 사안(F-1 승인 대기, F-10 5거래일 관찰 진행중) 재현. 3: 미상 — 이 세션의 명령은 배제됨. 후보: 사용자 PC의 IDE/Git 클라이언트 백그라운드 작업, 또는 리눅스 샌드박스 마운트 경유 특성(단 이번엔 세션이 원인이 아님이 확인된 점이 기존 사례와 다름). 4·5·6·7: 전부 이미 알려진 정상 동작 패턴이거나 기존 관찰 대상.

### 결정

새 Fix 제안 없음. 3(`.git/index.lock`)에 대해서만 "12:37 이후 `git_lock_guard.py --check` 재판정" 관찰 항목(O-i1)을 등록. 그 외 전부 관찰만 이어감 — 함정①(이미 등록된 사안 재제안) 방지를 위해 1-1~1-3은 재등록하지 않음.

### Why

장중 규정상 코드 변경·커밋·배포·재기동 금지, 라이브 DB 분석 금지를 준수. 계측 4원칙 ②(미측정≠0)에 따라 "재학습 0회"·"매분루프 공백 163분"을 자동경보 문구 그대로 옮기지 않고 원인(트리거 조건 미충족/미래 시각)을 확인한 뒤 정상으로 판정.

### How to apply

해당 없음(장중 — 코드 변경 금지, 관찰·기록만).

### 검증

- 브랜치 `v9-dev` 재확인(HEAD `e808409`, 당일 커밋 0건 — 장전과 동일).
- `git --no-optional-locks diff --ignore-space-at-eol --stat` 재확인 — 실질 변경 5파일(코드 3 + dev_memory 2).
- 설정 불변식 전 항목 `일치` 재확인(장전과 동일).
- 매분 루프 커버리지 09:00~12:27 구간 10분 이상 공백 0건(수집기 §7).
- 리포트: `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md`(장중 절, `## 0i-C`~`## 8i`). 증거: `evidence_MW0601-20260918_intra.md`.

### 자가유발 여부

`.git/index.lock`(신규 이상점 1-4)에 대해서만 **미상 — 이 세션이 자가유발했다는 근거는 없다**(이 세션의 git 명령 전량 확인, 락 생성 시각과 겹치는 쓰기성 명령 없음). 그 외 항목은 자가유발 없음 — 라이브 DB 미접촉, 코드 미변경, `dev`·`main` 미접촉.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 15:45 후속 — 병행 세션 번호 충돌
### 16:20 채점기 딥다이브 (사용자 지시, 장 마감 후)
### 16:40 브랜치 대조 — 왜 v9-dev 에만 발생하는가 (사용자 지시)
### 17:0x 600차 — F-10·F-11 구현 완료 + O-t2 기한 등록 (사용자 지시)
### 2026-09-17 601차 장후 — 신규 등록 (F-14·F-15, 관측 재정리)
### 2026-09-17 601차 후속 — 장후 자동조치 결과 (17:3x~18:0x)
### 2026-09-18 604차 장전 — 기존 항목 진행상황만 갱신 (신규 없음)
### 2026-09-18 605차 장중 — 신규 1건 + 기존 항목 진행상황 갱신
```

미완료 체크박스 **2768건** (끝에서 30건)
```
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
- [ ] **O-t4 (다음 거래일 09:00)** `[ConfFloorGuard]`의 `out_max`(보정기 출력상한)가
- [ ] **O-t5 (구 O-t2, 기한 2026-09-24 장후 — 배포 후 5거래일)** Platt 축퇴가 별개 문제인지
- [ ] **O-t6 (구 O-t3, 다음 거래일 15:40)** `[Calibration:ensemble] 저장 완료`/
- [ ] **A-1 (P1, 신규)** `tests/test_dashboard_smoke.py::test_main_dashboard_builds` 가
- [ ] **A-2 (P2, 신규 · 문서 정정)** 「pytest 재실행은 conda 부재로 실패」는 **오진**이다.
- [ ] **A-3 (P2, 신규 · 사용자 몫)** 09:37:33 에 뜰 `conda run … pytest tests/test_597_order_v…`
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
UnicodeEncodeError` 로 죽는 것**이다(conda/cli/main_run.py:42). 테스트는 멀줦히 돌았다.
      ⇒ 앞으로 점검·자동조치 세션은 **`PYTHONIOENCODING=utf-8 PYTHONUTF8=1` 을 붙여** 호출할 것.
      이 한 줄이 없어서 O-i6 가 「환경 제약」으로 하루 밀렸다.
- [ ] **A-3 (P2, 신규 · 사용자 몫)** 09:37:33 에 뜰 `conda run … pytest tests/test_597_order_v…`
      프로세스(PID 24080)가 **8시간째 살아있다**. 좀비 프로세스로 보이며 py37_32
      인터프리터를 잡고 있다. 정리 여부 판단 필요(수 초).
- [ ] **F-3 형제 1건 (P2)** `main.py:14880` `logger.critical("[System] 키움 연결 실패 — 종료")`
      가 **같은 결함**이다. 이번엔 손대지 않았다 — 리포트 F-3 이 지명한 범위가
      아니고, 그 지점은 로그인 **실패** 경로라 `self.broker` 상태 가정이 다를 수 있어
      별도 확인이 필요하다. 다음 세션이 같은 패턴으로 닫을 것.

### 2026-09-18 604차 장전 — 기존 항목 진행상황만 갱신 (신규 없음)

- [ ] **F-1(538-4) 승인 대기 — 10거래일째 재현** (09-04 532차 최초 등록). 오늘 08:41:09 재현 확인,
      `data/eod_retrain_done_20260917.txt` 존재로 어제 EOD 자체는 정상 완료했음을 재확인(표시
      버그이지 재학습 실패 아님). 사용자 승인 여부 결정 필요 — 급하지 않음.
- [ ] **O-t4 1일차 관측 완료** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, F-10(600차)
      배포 전과 동일값. O-t5 판정(2026-09-24, 5거래일째)까지 계속 관찰. 아직 결론 아님.
- [ ] **1-2(09-17 access violation) 우선순위 결정 — 여전히 사용자 몫** (2026-09-17 601차 9p-3
      #4에서 이월). 09-18 오늘도 재발 없음.
- [ ] **미커밋 3파일 지속** — `features/levels/levels_store.py`·`premarket_levels.py`(롤 정책
      신설)·`scripts/cybos_autologin.py`(다이얼로그 판별 통합). 사용자 커밋 검토 필요, 경로
      명시해 `git add`(`git add .` 금지 — CRLF 파생 597건 혼입).

**근거**: `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` 장전(pre) 절.

### 2026-09-18 605차 장중 — 신규 1건 + 기존 항목 진행상황 갱신

- [ ] 🔴 **O-i1 (신규, P1) `.git/index.lock` 원인불명 생성 — 12:37 이후 재판정 필요.** 12:27:27
      0바이트 락 발견, 이 세션 명령으로는 설명 안 됨(`git_lock_guard.py --check` 12:27·12:30
      둘 다 `HOLD 판정보류`, 나이 103초/160초 ≤ 임계 600초). **지우지 말 것** — 600초(12:37)
      넘겨서 재판정: `STALE`이면 `--reclaim`, 계속 `HOLD`면 사용자에게 저장소를 만지는
      다른 프로그램(IDE·Git 클라이언트) 확인 요청.
- [ ] **F-1(538-4) 승인 대기 — 11거래일째 재현** (09-04 532차 최초 등록). 09-18 장중에도
      08:41:09 로그 그대로 재확인(장전과 동일 사건, 새 재현 아님).
- [ ] **O-t4 1일차 관측 지속** — 09-18 09:00:00 `[ConfFloorGuard]` out_max=0.3479, 장중에도
      같은 값 재확인. O-t5 판정(2026-09-24)까지 계속 관찰.
- [ ] **미커밋 3파일 지속 + dev_memory 2파일 추가 미커밋** — 실질 변경 5파일
      (`features/levels/levels_store.py`·`premarket_levels.py`·`scripts/cybos_autologin.py`
      + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`). 사용자 커밋 검토 필요, 경로 명시해
      `git add`(`git add .` 금지).
- [ ] **G-2 (P2, 신규)** 증거수집기가 실행 "시작 시점"만 락 유무를 자가점검하는데, 수집 종료
      수십 초 뒤 생기는 락(오늘 사례)은 못 잡는다. 수집 종료 후 1~2분 뒤 재확인 단계를
      추가하는 것을 다음 자동조치 세션에서 검토 제안.

**근거**: `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` 장중(intra) 절.

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

### `data/heartbeat_MW0601_20260918.json` — 245B · 09-18 15:46:56
```json
{
 "pid": 18848,
 "written_at": "2026-09-18T15:46:56",
 "beat_epoch": 1789714013.7554421,
 "beat_age_sec": 2.5,
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

- 파일 최종 기록: **09-18 15:53:04**

| 키 | 값 | 수집 대상일(2026-09-18)과 일치 |
|---|---|---|
| `date` | 2026-09-18 | 예 |
| `p8_last_success_date` | 2026-09-18 | 예 |
| `eod_retrain_ok_date` | 2026-09-18 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 152개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 30.5KB | 09-18 12:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_intra.md` | 64.9KB | 09-18 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260918_pre.md` | 56.5KB | 09-18 09:03 |
| `docs/정기점검/매일점검/MW0601-20260917-점검리포트.md` | 158.1KB | 09-17 18:05 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_post.md` | 77.3KB | 09-17 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra_1228.md` | 64.7KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_intra.md` | 67.4KB | 09-17 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260917_pre.md` | 55.9KB | 09-17 09:02 |

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

1. `.git/index.lock` **스테일 잔존** (0바이트 · 3.8시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
3. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건) — 차단 67건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
4. **SYSTEM 로그가 직전 5거래일 중앙값(17:41)보다 114분 이르게 끝났다** (오늘 15:47) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
5. 메인 스레드 정지 5초 초과 **2건** (최대 8437ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260918_WARN.log`: **[Brier] 과신** 2건(표본)
7. `logs/20260918_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20260918_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260918_SIGNAL.log`: **ConstOut** 8건(표본)
10. `logs/20260918_LEARNING.log`: **축퇴** 8건(표본)
11. `logs/retrain_eod_20260918.log`: **축퇴** 1건(표본)
12. `logs/retrain_eod_20260918.log`: **ConstOut** 1건(표본)
13. 미커밋 변경 673건 (실질 11건 · **코드(.py) 3건**) — 코드 변경이 커밋되지 않았다
14. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260918*.log` (Windows) / `grep 강제청산 logs/*20260918*.log`*