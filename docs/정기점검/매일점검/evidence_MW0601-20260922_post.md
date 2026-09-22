# 미륵이 증거 다이제스트 — 2026-09-22 / POST

- 생성 2026-09-22 16:21:09 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/pensive-gracious-ramanujan/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260922` · `2026-09-22` · `260922` · `0922`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **32개** 파일 · 32개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260922.txt` | 28B | 09-22 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260922.txt` | 28B | 09-22 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260922.txt` | 233B | 09-22 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260922.log` | 1.4KB | 09-22 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260922.log` | 216B | 09-22 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260922.json` | 245B | 09-22 15:47 |
| `launcher_{DATE}_084001_14358.log` | 1 | `logs/Mireuk_batch/launcher_20260922_084001_14358.log` | 8.9MB | 09-22 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260922.log` | 6.2KB | 09-22 12:44 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20260922.log` | 1.2KB | 09-22 16:20 |
| `position_state.json.gen_{DATE}_131602` | 1 | `data/position_state.json.gen_20260922_131602` | 1.5KB | 09-22 13:16 |
| `position_state.json.gen_{DATE}_131752` | 1 | `data/position_state.json.gen_20260922_131752` | 1.5KB | 09-22 13:16 |
| `position_state.json.gen_{DATE}_131801` | 1 | `data/position_state.json.gen_20260922_131801` | 1.5KB | 09-22 13:17 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260922.log` | 21.9KB | 09-22 15:53 |
| `retrain_intraday_{DATE}_094311.log` | 1 | `logs/retrain_intraday_20260922_094311.log` | 5.7KB | 09-22 09:43 |
| `retrain_intraday_{DATE}_130500.log` | 1 | `logs/retrain_intraday_20260922_130500.log` | 3.2KB | 09-22 13:05 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260922.txt` | 43B | 09-22 15:47 |
| `strategy_report_{DATE}_154015.txt` | 1 | `data/daily_reports/strategy_report_20260922_154015.txt` | 2.5KB | 09-22 15:40 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-09-22.jsonl` | 6.5KB | 09-22 16:11 |
| `{DATE}_DATA.log` | 1 | `logs/20260922_DATA.log` | 432.0KB | 09-22 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260922_DEBUG.log` | 222.3KB | 09-22 15:08 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260922_HEALTH.log` | 5.4KB | 09-22 14:45 |
| `{DATE}_HOGA.log` | 1 | `logs/20260922_HOGA.log` | 50.7MB | 09-22 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260922_LEARNING.log` | 406.4KB | 09-22 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260922_MICRO.log` | 964.9KB | 09-22 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260922_PROBE.log` | 124.2KB | 09-22 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260922_REGULAR_COLLECT.log` | 23.2KB | 09-22 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260922_SIGNAL.log` | 463.6KB | 09-22 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260922_SYSTEM.log` | 855.6KB | 09-22 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20260922_TRADE.log` | 7.2KB | 09-22 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260922_WARN.log` | 7.5MB | 09-22 15:46 |
| `{DATE}_lv.txt` | 1 | `data/peter_feed/2026-09-22_lv.txt` | 1.8KB | 09-22 16:12 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-09-22_tr.txt` | 35B | 09-22 16:11 |

## 2. 코드·커밋 상태

- HEAD `39d4af5` · 브랜치 `v9-dev` · 미커밋 745건 · 실질 변경 5건 · 코드(.py) 3건 · EOL 파생 618건 (추적변경 623 · 미추적 122 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 3.8시간 · git 프로세스 0개 → **커밋 불가 상태**
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `features/levels/levels_store.py`, `features/levels/premarket_levels.py`, `scripts/cybos_autologin.py`
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
 M config/dailycheck_targets.json
… 외 705건
```

**당일(2026-09-22) 커밋**
```
39d4af5 [MW0601] 617차 후속: dev_memory 기록 — 대시보드 크래시 원인·조치·남은 과제
e3e5d91 [MW0601] 617차 후속: 표시 위젯 한 줄이 엔진을 죽였다 — 폭 0 캔버스와 무가드 슬롯
c69e061 [MW0601] 611차 후속4: 데이터를 보기 전에 기준을 못 박는다 — [80] 사전등록
bad6454 [MW0602] 583차: 수급 오전이 비는 건 구조다 — 백필을 EOD 에 걸고, 미연결을 한도소진과 구분한다
f536354 [MW0601] 611차 후속3: 08:45 는 우리 결손이 아니었다 — 원천에 없다 (+ 시작 시각 여유)
```

**최근 커밋 12건**
```
39d4af5 [MW0601] 617차 후속: dev_memory 기록 — 대시보드 크래시 원인·조치·남은 과제
e3e5d91 [MW0601] 617차 후속: 표시 위젯 한 줄이 엔진을 죽였다 — 폭 0 캔버스와 무가드 슬롯
c69e061 [MW0601] 611차 후속4: 데이터를 보기 전에 기준을 못 박는다 — [80] 사전등록
bad6454 [MW0602] 583차: 수급 오전이 비는 건 구조다 — 백필을 EOD 에 걸고, 미연결을 한도소진과 구분한다
f536354 [MW0601] 611차 후속3: 08:45 는 우리 결손이 아니었다 — 원천에 없다 (+ 시작 시각 여유)
60d598c [MW0601] 616차: 사료는 올라가지 않고 있었다 — 푸시하는 손이 없었다
2e000b0 [MW0601] 615차: 걷어낸 세로가 차트로 가지 않고 빈칸으로 남아 있었다
7486034 [MW0601] 614차 후속: 주입이 조용히 사라졌다 — 워커 스레드의 QTimer 는 발화하지 않는다
25d595f [MW0601] 614차 기록: 세션 재생 — 결정 로그 + 다음 할 일
86173bf [MW0601] 614차: 화면이 비는 건 데이터가 없어서가 아니었다 — 세션 재생
f26eb87 [MW0601] 613차: 카드 6장을 시계열로 바꾸려다, 원값이 없다는 걸 알았다
c48c415 [MW0601] 612차 후속6: 장후 3건 실행 — 그중 하나는 카드가 거짓말하고 있었다
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

_본문 미열람(설정): `20260922_HOGA.log` 50.7MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260922.txt`** — 28B · 09-22 15:40:15
```
2026-09-22T15:40:15.172184
```

**`data/daily_close_started_20260922.txt`** — 28B · 09-22 15:40:13
```
2026-09-22T15:40:13.104328
```

**`data/daily_reports/strategy_report_20260922_154015.txt`** — 2.5KB · 09-22 15:40:15
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-22 15:40
========================================================
  버전    : v1.0  (85일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-1.99  MDD(자본대비)=29.9%
  당일      : WR=100.0%  PF=999.00
  롤링20일: 누적 -6462808원  Sh=-1.99  MDD(자본대비)=29.9%  MDD(peak대비)=1258.4%
  당일손익 : broker(gross) +138,000원  수수료 44,192원  net +93,808원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)
  PSI/feat: 미측정
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +354,500원  승률 65.0%  합계 +7,090,005원
  등급별 순EV(30일): A=+110,357원(58건,승64%)  BROKER=-2,574,591원(4건,승50%)  C=+24,396원(1건,승100%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=+1,934원(11건)  3m=-7,402원(39건)  5m=-32,721원(7건)  ?=-37,188원(172건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 22분  5일평균 17분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 31.5pt(5일평균 19.2pt)  1분평균변동 0.59pt(5일평균 0.58pt)
--------------------------------------------------------
  진입 퍼널(2026-09-22, 총 367분):
    FLAT 260 → conf미달 80 → CoherenceGate 5 → 게이트차단 18 → 후보 4 → 진입 2
    게이트별: 체크리스트항목미달=5  콜드스타트/기타(DataAnomalyGate)=3  콜드스타트/기타(조건부구간)=3  모드필터=2  ATR변동성=2  Degraded신뢰도=1  콜드스타트/기타(RegimeOverride)=1  포지션보유중(평가생략)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 2건
      └ 상세: JointGateBlock=2
      └ JointGateBlock 2건 (무정보폴백 0건 = 0.0%) [표본 18건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260922.txt`** — 233B · 09-22 15:53:19
```
completed: 2026-09-22 15:53:19
rows: 16633
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 24.3
t_retrain_s: 171.1
t_total_s: 195.9
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/peter_feed/2026-09-22_lv.txt`** — 1.8KB · 09-22 16:12:49
```
1139 하방돌파시 매도로 수정 손절가 1143
9:13 AM · Sep 22, 2026

1139 매도체결. 청산가 1130
9:14 AM · Sep 22, 2026

1130 매도체결. 9P 수익!!!! ---------------------------- 저는 공개적으로 베팅을 할 때마다 뉴욕 양키즈 4번 타자가 9회말, 3-0으로 뒤진 상황 투아웃 만루에 타석에 오르는 심정으로 베팅을 합니다. 하지만. 뉴욕 양키즈의 4번 타자가 아무나 가는 자리는 아니지요 쏘리 질러!!!! 터리!
10:50 AM · Sep 22, 2026

[피터리 - 2026년 9월 22일 증권사 종목리포트 브리핑] 기준: 2026년 9월 21일 13:00 초과 ~ 9월 22일 13:00 KST ① 한눈에 보는 결론 오늘 리포트에서 가장 강하게 읽히는 변화는 네 축이다. 첫째, 반도체 업사이클의 지속기간이 길어질 가능성이다. 삼성전자는 단순 메모리 가격 상승을 넘어
1:55 PM · Sep 22, 2026

[피터리 - 2026년 9월 22일 증권사 산업분석 리포트 브리핑] 기준: 2026년 9월 21일 13:10 초과~2026년 9월 22일 13:10 KST ① 한눈에 보는 결론 오늘 산업리포트에서 가장 중요한 축은 반도체 초대형 팹 투자, K-방산의 해외 체계 편입, AI 데이터센터 건설, 통신장비 산업 재편이다. 첫째,
2:03 PM · Sep 22, 2026

피터리 - 2026년 9월 22일 증권사 종목리포트 브리핑_축약본
2:55 PM · Sep 22, 2026

피터리 - 2026년 9월 22일 증권사 산업분석 리포트 브리핑_축약본
2:57 PM · Sep 22, 2026

[피터리 - 2026년 9월 22일 국내 주식시장 마감 브리핑] 기준: 2026년 9월 22일 15:50 KST / 한국 정규장 마감 ① 한눈에 보는 결론 오늘 코스피는 7,017.91, +10.19포인트, +0.15%로 마감하며 이틀 연속 7,000선을 지켰다. 코스닥은 834.38, -1.89포인트, -0.23%로 하락했다. 숫자만 보면 코스피
4:01 PM · Sep 22, 2026
```

**`data/peter_feed/2026-09-22_tr.txt`** — 35B · 09-22 16:11:47
```
09:14 S 1139 / 10:50 X 1130 익절
```

**`data/shutdown_normal_20260922.txt`** — 43B · 09-22 15:47:15
```
auto_shutdown
2026-09-22T15:47:15.163996
```

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20260922_130500.log`, `20260922_MICRO.log`, `20260922_DATA.log`, `20260922_PROBE.log`, `launcher_20260922_084001_14358.log`, `20260922_DEBUG.log`, `20260922_REGULAR_COLLECT.log`, `mainstall_traceback_20260922.log`_

### `logs/20260922_TRADE.log` — 7.2KB · 57행 · 최종 15:40:14

- 형식 평문 · 시각 인식 57행 · INFO=57

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:41:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-22 08:41:10 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-22 09:30:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-22 09:30:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.58 tox=0.70 joint=0.407)
2026-09-22 09:43:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-09-22 13:18:01 [INFO] TRADE: [청산 완료] PnL=+1.18pt (+47,978원) | 포지션 합계 +69,956원 (레그 2)
2026-09-22 13:25:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,725,025) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-22 13:25:01 [INFO] TRADE: [모드필터 차단] SHORT->SHORT 2계약 C급 (모드=hybrid, 허용=['A', 'B'])
2026-09-22 15:09:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-22 15:40:14 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×57

**컴포넌트 상위 15** — `Chejan`×14, `Position`×10, `Sizer`×7, `주문요청`×6, `ProfitGuard`×4, `JointGateBlock 차단`×2, `모드필터 차단`×2, `진입체크`×2, `체결진입`×2, `체결진입보정`×2, `TickTP1`×2, `TP1 부분청산`×2, `청산 완료`×2

### `logs/20260922_WARN.log` — 7.5MB · 35962행 · 최종 15:46:16

- 형식 평문 · 시각 인식 35955행 · WARNING=35955, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-22 08:41:12 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=333044256
2026-09-22 08:41:13 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-22 08:41:13 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-22 15:46:13 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-22 11:05:00 cols=['open'] existing_source=rt
2026-09-22 15:46:13 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-22 13:16:00 cols=['open'] existing_source=rt
2026-09-22 15:46:13 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=407 inserted=4 open_fixed=1 mismatch=8
2026-09-22 15:46:16 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3703ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3703 band=INFO since_pipe_s=NA
2026-09-22 15:46:16 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 93.0ms | size=1799x832 candles=409 grid=15.0 spans=32.0 candles=0.0 dir=0.0 regime=15.0 markers=31.0 axes=0.0 cross=0.0 | slow_cnt=1674 total_cnt=1674
```

</details>

**WARNING — 태그 39종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 35621 | 09:03:27 | 15:46:16 | paintEvent slow 47.0ms | size=1886x916 candles=19 grid=15.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=32.0 cross=0.0 | slow_cnt=1 total_cnt=7 |
| `LiveDBG` | 129 | 08:41:12 | 15:46:16 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SHAP` | 28 | 11:27:01 | 15:07:02 | 슬로우 감지 1488ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `Health` | 17 | 09:00:01 | 14:44:01 | level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0 |
| `ScalerRefresh` | 15 | 09:09:00 | 14:47:00 | 5분 누적 수익률 -0.275% (임계 ±0.241%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ChejanFlow` | 14 | 11:02:01 | 13:18:01 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1894' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=11:02:00.708' | positio… |
| `ChejanMatch` | 14 | 11:02:01 | 13:18:01 | order_no='1894' | pending='ENTRY:LONG qty=2 filled=0 order_no=1894 reason=진입 req_at=11:02:00.708' | pending_matched=True |
| `SessionBackfill` | 12 | 08:41:43 | 15:46:13 | OHLCV 불일치 ts=2026-09-21 10:00:00 cols=['open', 'low', 'volume'] existing_source=rt |
| `PipePerf` | 12 | 09:00:01 | 13:25:01 | total=1386ms | S0=4ms S1=13ms S2=0ms S3=0ms S4=89ms S5=964ms S6=288ms S7=17ms S8=12ms |
| `CB⑤` | 12 | 09:00:01 | 13:25:01 | 파이프라인 1386ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `PendingOrder` | 12 | 11:02:00 | 13:18:01 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1128.64, 'reason': '진입', 'hint_source': '', 'atr': 1.1457, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `CB③-P4` | 10 | 11:10:00 | 15:00:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |

**채널** — `SYSTEM`×35938, `HEALTH`×17

**컴포넌트 상위 15** — `ChartDBG`×35621, `LiveDBG`×129, `SHAP`×28, `Health`×17, `ScalerRefresh`×15, `ChejanFlow`×14, `ChejanMatch`×14, `SessionBackfill`×12, `PipePerf`×12, `CB⑤`×12, `PendingOrder`×12, `CB③-P4`×10, `-`×7, `출처축`×6, `HealthPolicy`×5

### `logs/20260922_SYSTEM.log` — 855.6KB · 5920행 · 최종 15:47:15

- 형식 평문 · 시각 인식 5895행 · INFO=5895, PLAIN=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=22668 | 행감지=30s all_threads=True
2026-09-22 08:40:51 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-22 08:40:51 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-22 08:40:51 [INFO] SYSTEM: 미륵이 초기화
2026-09-22 08:40:51 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-21) 종가 버퍼 로드: 377봉
  …
2026-09-22 15:46:13 [INFO] SYSTEM: [SessionBackfill] 08:45 개장 체결 보정 ts=2026-09-22 08:45:00 rt O=1132.00/V=399 → chart O=1133.36/V=735
2026-09-22 15:46:13 [INFO] SYSTEM: [SessionBackfill] 2026-09-22~2026-09-22 chart=411 existing=407 inserted=4 open_fixed=1 mismatch=8
2026-09-22 15:47:15 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-22 15:47:15 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-22 15:47:15 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5895

**컴포넌트 상위 15** — `CybosInvestorRaw`×1566, `CybosRT-TICK`×1128, `BAR-CLOSE`×407, `CVD-ANCHOR`×407, `TickUI`×406, `CybosRT-ROLLOVER`×406, `S6Detail`×367, `PipePerf`×367, `System`×112, `MicroRegime`×85, `OptionChain`×84, `RegimeFingerprint`×67, `CybosSub`×63, `BalanceUI`×38, `CybosEvent`×28

### `logs/20260922_SIGNAL.log` — 463.6KB · 4160행 · 최종 15:40:14

- 형식 평문 · 시각 인식 4160행 · WARNING=1265, INFO=2895

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.436
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.424
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.415
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.411
2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.419
  …
2026-09-22 15:09:09 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
2026-09-22 15:10:02 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-22 15:40:14 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-22 15:40:14 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-22 age=37m extreme=752 refresh=33 grade_x=0 cb3=0
2026-09-22 15:40:14 [INFO] SIGNAL: [ModelHealth] date=2026-09-22 앙상블유효가동률=미측정 | 파이프라인 0분 | ConstOut 0회/0분 | WeightCollapse 0분 | 장중재학습 0회 | CB③ ready 0분/0분 (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 714 | 09:00:01 | 14:47:01 | 1m 'macro_vix' scale=0.0073 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 193 | 09:00:00 | 15:08:00 | ts=08:59 horizon=1m age=1m max_z=-9.03(ofi_reversal_speed) extreme=5 adj=4 |
| `Model` | 156 | 09:00:00 | 15:08:00 | 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 93 | 09:06:00 | 15:05:00 | CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+0.971 need <0 (SHORT) bull_exh=0.00 |
| `WeightCollapse` | 88 | 09:07:00 | 15:06:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 14 | 10:22:00 | 14:46:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 4 | 09:53:00 | 13:04:01 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `PCR-Dampen` | 2 | 13:53:01 | 13:58:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 1 | 11:12:01 | 11:12:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3320 < 필요 0.3730 (conf_floor=0.330, min_conf=0.373, span=0.0048, auc=0.542). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4160

**컴포넌트 상위 15** — `ScalerFloor`×786, `SIGNAL`×734, `Ensemble`×369, `ZeroDiag`×352, `MetaGate`×347, `FQAdj`×285, `ScalerMonitor`×194, `Model`×186, `Checklist`×119, `WeightCollapse`×88, `MicroRegime`×85, `ATR-Horizon`×73, `InstabilityGate`×68, `차단`×51, `ToxicityGate`×40

### `logs/20260922_LEARNING.log` — 406.4KB · 3469행 · 최종 15:40:14

- 형식 평문 · 시각 인식 3469행 · WARNING=478, INFO=2991

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 08:40:52 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-09-22 08:40:56 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00132 auc=0.540 out_max=0.3456 (n=145) → 보정 재적용
  …
2026-09-22 15:40:14 [INFO] LEARNING: [DriftAdjuster] 표본 부족(n=0 < 15) — acc=50.0% 반영 스킵, alpha=0.01000 유지
2026-09-22 15:40:14 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-22 15:40:14 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-22 15:40:14 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-22 15:40:14 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 191 | 08:40:56 | 15:09:00 | 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 148 | 08:40:56 | 15:09:00 | 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 43 | 08:40:56 | 15:09:00 | 축퇴 감지 — span=0.00169 auc=0.451 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 35 | 08:40:56 | 15:09:00 | 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 34 | 08:40:56 | 15:09:00 | 하한 도달불가 — out_max=0.3291 < conf_floor=0.3300 (span=0.00085 auc=0.556 out_max=0.3291, 기저율=0.3286 n=140) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 21 | 08:40:58 | 15:08:58 | 축퇴 감지 — span=0.00101 auc=0.527 out_max=0.3268 (기준 auc<0.53 and span<0.020, 기저율=0.3263 n=190) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 4 | 08:41:05 | 15:09:00 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 2 | 09:16:00 | 09:45:00 | total=693ms raw_fetch=436ms pred_select=5ms pred_update=3ms pred_insert=202ms verified=1 |

**채널** — `LEARNING`×3469

**컴포넌트 상위 15** — `LEARNING`×1178, `Calibration:1m`×378, `SGD`×366, `sigma`×341, `Calibration:30m`×294, `Bias⚠`×238, `Bias`×131, `OnlineLearner`×98, `Calibration:10m`×80, `MetaConf`×72, `Calibration:3m`×66, `Calibration:5m`×66, `Calibration:15m`×42, `ScalerWarmup`×39, `BiasReset`×27

### `logs/20260922_HEALTH.log` — 5.4KB · 35행 · 최종 14:45:00

- 형식 평문 · 시각 인식 35행 · WARNING=17, INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0
2026-09-22 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=564ms | quality=0.86 | cache_age=100s | exceptions_10m=0
2026-09-22 09:16:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2033ms | quality=1.00 | cache_age=80s | exceptions_10m=0
2026-09-22 09:17:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=573ms | quality=1.00 | cache_age=138s | exceptions_10m=0
2026-09-22 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 354ms (표본 20분)
  …
2026-09-22 14:02:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=277ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-22 14:04:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=329ms | quality=1.00 | cache_age=180s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-22 14:05:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=358ms | quality=1.00 | cache_age=55s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-22 14:44:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=361ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-22 14:45:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=361ms | quality=1.00 | cache_age=56s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 17 | 09:00:01 | 14:44:01 | level=WARNING degraded=OFF | latency=1386ms | quality=0.86 | cache_age=41s | exceptions_10m=0 |

**채널** — `HEALTH`×35

**컴포넌트 상위 15** — `Health`×33, `HealthTrend`×2

### `logs/retrain_eod_20260922.log` — 21.9KB · 135행 · 최종 15:53:20

- 형식 평문 · 시각 인식 135행 · WARNING=22, INFO=113

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 15:50:03,279 [INFO] EOD_RETRAIN: =======================================================
2026-09-22 15:50:03,280 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-22 15:50:03,280 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-22 15:50:03,280 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-22 15:50:03,281 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-22 15:53:20,266 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0512 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-22 15:53:20,268 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1478 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-22 15:53:20,270 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-09-22 15:53:20,276 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-22 15:53:20,277 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:39 | 15:52:34 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-22 09:10:00까지)인데 acc.txt=0.4565는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:39 | 15:52:34 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1527봉(83%)이 현행 학습구간 (현행 cutoff=2026-09-22 09:10:00 ≥ 홀드아웃 시작=2026-09-15 12:39:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-22 09:10 >= holdout_start=2026-09-15 12:39 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-0… |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-09-22 | 최신 2026-09-21 · 기준 7거래일. 복구: python scripts/collect_regular_futures.py --from 20260922 --to 20260922 |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25432/45603 제외 (418차 결정 1) — 남은 20171행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/20171행 제외 (559차 P1'-2) — 남은 18725행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:19 | 15:53:19 | 백필 0행 제외 — 필터가 무효일 수 있다. 16633행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×74, `EOD_RETRAIN`×26, `SIGNAL`×25, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `ScalerFloor`×18, `EOD_RETRAIN`×14, `GuardGhost`×12, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2

### `logs/retrain_intraday_20260922_094311.log` — 5.7KB · 43행 · 최종 09:43:57

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-22 09:43:11,818 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-22 09:43:11,819 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_09898289.json
  …
2026-09-22 09:43:57,824 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-22 09:43:57,824 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-22 09:43:57,825 [INFO] LEARNING: [Retrain] 완료 | 42.0초 | 성공=6/6 호라이즌
2026-09-22 09:43:57,826 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 46.0s 데이터=4800행
2026-09-22 09:43:57,827 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_09898289.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 09:43:28 | 09:43:28 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 25769/45615 제외 (418차 결정 1) — 남은 19846행 |
| `UnitMismatch` | 1 | 09:43:28 | 09:43:28 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/19846행 제외 (559차 P1'-2) — 남은 18400행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

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
오늘 PnL: +93808원
════════════════════════════════════════════════════
2026-09-22 15:46:13 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-22 09:30:00 cols=['open'] existing_source=rt
2026-09-22 15:46:13 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-22 09:43:00 cols=['open', 'low', 'volume'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) — **엔진** | 2 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 51 |
| 사이저 호출(`[Sizer]`) | 7 |

### 포지션 2건 · 승 2 (100%) · 합계 +2.76pt (+93,808원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 11:02:00 | 엔진 | LONG | 2 | 3m | 2 | +0.92 | +23,852 | 하드스톱 |
| 13:16:01 | 엔진 | SHORT | 2 | 3m | 2 | +1.84 | +69,956 | 하드스톱 |

**청산 레그 4행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 11:04:52 | 부분 | 1 | +0.56 | +16,926 | TP1 부분청산 33% |
| 11:05:00 | 전량 | 1 | +0.36 | +6,926 | 하드스톱 |
| 13:17:52 | 부분 | 1 | +0.66 | +21,978 | TP1 부분청산 33% |
| 13:18:01 | 전량 | 1 | +1.18 | +47,978 | 하드스톱 |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱`×2

> 최종 청산이 하드스톱·손절 계열인 포지션 2/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +93,808 = 포지션합 +93,808 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### CB③ 판정 가능 시간 — **0분 / 0분 (—)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:02:00 | LONG | 2 | 1128.64 | 3m | mean-revert |
| 13:16:01 | SHORT | 2 | 1123.36 | 3m | mean-revert |

계약수 분포 — 2계약×2

등급 분포 — `A급(원시C)`×2

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×2, `fore`×1, `prev`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×1, **3계약**×6

실제 진입 계약수 — **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×6, `conf=0.6 regime=1.0 safe=1.00`×1

### 차단 사유 51건 · 25종

| 건수 | 사유 |
|---|---|
| 24 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 2 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 1 | JointGateBlock — meta=0.58 tox=0.70 joint=0.407 < 0.50 |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar |
| 1 | JointGateBlock — meta=0.60 tox=0.70 joint=0.423 < 0.50 |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 10_chase |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.76pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.69pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.67pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.68pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.64pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×24, `3_vwap`×4, `6_foreign`×4, `7_prev_bar`×1, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 39건 · 최대 8156ms · 5초 초과 2건

상위 — 8156ms, 6313ms, 4906ms, 4641ms, 4328ms, 4063ms, 3985ms, 3984ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:44:06 | 6313ms | 3948ms | **2365ms (37%)** |
| 12:44:08 | 8156ms | 708ms | **7448ms (91%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260922_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:14 2026-09-22 15:40:14 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 22분 < 하한 25분 — 최근 5거래일 평균 17분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- ConstOut ×1(표본)
13:04:01 2026-09-22 13:04:01 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(5m=0.6588)
--- PSI ×1(표본)
15:40:13 2026-09-22 15:40:13 [WARNING] SYSTEM: [RegimeFingerprint] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerprint] 기준선 키 불일치` WARNING 이 기동 로그에 있는지 먼저 확인할 것
--- [Brier] 과신 ×1(표본)
10:36:00 2026-09-22 10:36:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.352 > 0.35
--- [ExitCooldown] ×6(표본)
11:05:00 2026-09-22 11:05:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:07:00)
11:05:00 2026-09-22 11:05:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:07:00)
11:09:00 2026-09-22 11:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=279ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitAttempt]×1 [ExitCooldown]×1
13:18:01 2026-09-22 13:18:01 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 13:20:01)
--- [SHAP] 슬로우 ×8(표본)
11:27:01 2026-09-22 11:27:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1488ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:41:02 2026-09-22 11:41:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1740ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:49:01 2026-09-22 11:49:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1029ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:16:02 2026-09-22 12:16:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1869ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- degraded=ON ×1(표본)
09:45:01 2026-09-22 09:45:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1827ms | quality=1.00 | cache_age=129s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
--- 메인 스레드 블로킹 ×8(표본)
08:41:15 2026-09-22 08:41:15 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3484ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3484 band=INFO since_pipe_s=NA
09:00:04 2026-09-22 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4063 band=INFO since_pipe_s=0.1
09:03:27 2026-09-22 09:03:27 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=24 watchdog_alerted=[] | [MainStall] stall_ms=3375 band=INFO since_pipe_s=26.7
09:05:02 2026-09-22 09:05:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2250 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260922_SYSTEM.log`
```
--- ConstOut ×8(표본)
10:22:00 2026-09-22 10:22:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5795) | 앙상블 제외는 유지
10:31:00 2026-09-22 10:31:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4918) | 앙상블 제외는 유지
11:13:00 2026-09-22 11:13:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4588) | 앙상블 제외는 유지
11:22:00 2026-09-22 11:22:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4873) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:14 2026-09-22 15:40:14 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 0분 / 파이프라인 0분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-22 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:06:00 2026-09-22 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-22 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:16:01 2026-09-22 09:16:01 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:14 2026-09-22 15:40:14 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:14 2026-09-22 15:40:14 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:14 2026-09-22 15:40:14 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 2레그 / 2포지션 중 TP 이벤트 대응 2 · 단일계약 보호전환(설계) 0 · 미대응 0
--- [SchedForceExit] ×1(표본)
15:11:15 2026-09-22 15:11:15 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:15 2026-09-22 15:40:15 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:47:15 2026-09-22 15:47:15 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×6(표본)
15:40:15 2026-09-22 15:40:15 [INFO] SYSTEM: [Notify] ℹ️ [15:40:15] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:15 2026-09-22 15:40:15 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 405초
15:40:15 2026-09-22 15:40:15 [INFO] SYSTEM: 자동 종료 예약 — 420초 후 Qt 이벤트 루프 종료
```

### `logs/20260922_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
11:12:01 2026-09-22 11:12:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3320 < 필요 0.3730 (conf_floor=0.330, min_conf=0.373, span=0.0048, auc=0.542). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
10:22:00 2026-09-22 10:22:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1240 dir=+0)
10:22:00 2026-09-22 10:22:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:22:00 2026-09-22 10:22:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
10:23:01 2026-09-22 10:23:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1240 dir=+0)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-22 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:07:00 2026-09-22 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-22 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-22 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.436
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.424
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.415
08:40:30 2026-09-22 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.411
--- 안전망 ×8(표본)
09:07:00 2026-09-22 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-09-22 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-22 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-22 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260922_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00083 auc=0.415 out_max=0.2004 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.523 out_max=0.3273 (기준 auc<0.53 and span<0.020, 기저율=0.3273 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:56 2026-09-22 08:40:56 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00145 auc=0.458 out_max=0.3381 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:56 2026-09-22 08:40:56 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00132 auc=0.540 out_max=0.3456 (n=145) → 보정 재적용
```

### `logs/20260922_HEALTH.log`
```
--- [ExitCooldown] ×5(표본)
11:09:00 2026-09-22 11:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=279ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitAttempt]×1 [ExitCooldown]×1
11:10:00 2026-09-22 11:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=281ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[CB③-P4]×1 [ExitAttempt]×1 [ExitCooldown]×1
13:19:00 2026-09-22 13:19:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=269ms | quality=1.00 | cache_age=57s | exceptions_10m=4 | exc_tags=[SHAP]×2 [ExitAttempt]×1 [ExitCooldown]×1
13:25:01 2026-09-22 13:25:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1126ms | quality=1.00 | cache_age=50s | exceptions_10m=4 | exc_tags=[SHAP]×2 [ExitAttempt]×1 [ExitCooldown]×1
--- degraded=ON ×2(표본)
09:45:01 2026-09-22 09:45:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=1827ms | quality=1.00 | cache_age=129s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
09:46:00 2026-09-22 09:46:00 [INFO] HEALTH: [Health] level=INFO degraded=ON | latency=426ms | quality=1.00 | cache_age=3s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260922_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:05 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1 | 15:09:06 [INFO] 설정 업데이트 완료 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:14 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260922_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:12 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:55:13 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 702 | 08:55:13 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1275 | 09:54:00 [WARNING] paintEvent slow 94.0ms | size=2848x1449 candles=68 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers… |
| 12:00 | 장중 중간점 | 673 | 11:54:02 [WARNING] paintEvent slow 219.0ms | size=2848x1449 candles=188 grid=78.0 spans=16.0 candles=0.0 dir=0.0 regime=15.0 mar… |
| 14:00 | 장중 후반 · 장중 재학습 | 1416 | 13:54:00 [WARNING] paintEvent slow 125.0ms | size=2848x1449 candles=307 grid=46.0 spans=16.0 candles=16.0 dir=0.0 regime=0.0 mar… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1223 | 15:04:00 [WARNING] paintEvent slow 156.0ms | size=2848x1449 candles=377 grid=63.0 spans=16.0 candles=15.0 dir=0.0 regime=0.0 mar… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 944 | 15:12:00 [WARNING] paintEvent slow 109.0ms | size=2717x1323 candles=384 grid=31.0 spans=16.0 candles=15.0 dir=0.0 regime=0.0 mar… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 92 | 15:34:00 [WARNING] paintEvent slow 109.0ms | size=1799x832 candles=407 grid=31.0 spans=16.0 candles=15.0 dir=0.0 regime=0.0 mark… |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:46:13 [WARNING] OHLCV 불일치 ts=2026-09-22 09:30:00 cols=['open'] existing_source=rt |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260922_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=22668 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 133 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 182 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 176 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 163 | 11:54:01 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 182 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 236 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 134 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 55 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 6 | 15:44:13 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:44:13 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260922_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:40:30 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.436 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 141 | 09:00:00 [WARNING] 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 224 | 09:00:00 [WARNING] 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 92 | 09:57:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 12:00 | 장중 중간점 | 133 | 11:56:01 [WARNING] 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 14:00 | 장중 후반 · 장중 재학습 | 142 | 13:55:00 [WARNING] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 77 | 15:04:00 [WARNING] 신뢰도 미달 40.2% < 100.0% → 강제 X등급 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:14 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260921 | 17:30 | 로그 본문 |
| 20260920 | 18:39 | 로그 본문 |
| 20260918 | 15:47 | 로그 본문 |
| 20260917 | 20:33 | 로그 본문 |
| 20260916 | 17:21 | 로그 본문 |
| **중앙값** | **17:30** | 기준선 |
| **오늘 20260922** | **15:47** | 로그 본문 |

- 델타 **-103분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 4. 회귀 가드
### 5. 남은 것 · 주의
## 2026-09-22 (MW0601 617차 후속2 — 장중 점검)
### 1. 증상 — 오늘 크래시(09:41:56)가 점검 세션 관점에서 재확인됨
### 2. 결정 — 이 점검은 새 Fix를 제안하지 않는다. "언제 재기동할지"만 사용자 조치로 올린다
### 3. 부가 관찰 — `.git/index.lock`이 장중에도 재발, 이번엔 병행 세션 가능성
### 4. Why
### 5. 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
(`_on_main_heartbeat`·`_effect_report_timer_tick`·
`_check_limit_entry_timeout`). 표시 슬롯은 삼켜도 화면이 빌 뿐이지만,
**엔진 슬롯을 삼키면 주문·청산 실패가 조용히 사라진다** — 이 사고의 교훈
(조용히 그럴듯한 값)을 그대로 재생산하는 꼴이다. 슬롯별 판단이 필요하며
주간회의 안건으로 남긴다.

### 5. 남은 것 · 주의

- **실행 중인 프로세스에는 재기동 전까지 반영되지 않는다.**
- 무가드 15건(표시 슬롯)은 손대는 김에 하나씩 가드하고 래칫 기준선에서 지울 것.
- 엔진 슬롯 3건의 처분은 미정(위 §4).
- 장중 커밋은 `v9-dev` 규약상 피하는 쪽이나, **사용자 지시로 진행**했다.
- 부수 확인: 어제(09-21) 12회 재기동에 섞여 있던
  `NameError: name 'settings' is not defined`(`main.py:4659`
  `_fetch_weekly_option_flow`)는 `ERR-DEGRADED` 로 **잡힌** 예외라 사망 원인이
  아니었고, 오늘 0건이다.
- 부수 관찰: 크래시 재기동인데 `[Session] 재기동 #1 | cause=STARTUP` 으로
  기록된다 — 정상 기동과 구분이 안 된다(계측 4원칙 ② 계열, 미처리).

## 2026-09-22 (MW0601 617차 후속2 — 장중 점검)

### 1. 증상 — 오늘 크래시(09:41:56)가 점검 세션 관점에서 재확인됨

이 점검(장중, 12:34~12:37 실행)이 증거를 모으는 도중, 바로 위 617차 후속 항목이
다루는 크래시·재기동 사건을 라이브 로그(`launcher_20260922_084001_14358.log`,
`20260922_SYSTEM.log`, `20260922_HEALTH.log`)로 독립 재확인했다. 요지는 위
617차 후속과 동일하나, 점검 세션 관점에서 추가로 확인한 것 두 가지:

1. **크래시 시점(09:41:56)에 보유 포지션이 없었다** — 오늘 첫 진입은 11:02:00
   (`logs/20260922_TRADE.log`). 직접 금전 손실 0원, 매분 파이프라인도 3분 이상
   끊긴 구간 없음(`evidence_..._intra.md` §7).
2. **수정 커밋(`e3e5d91`·`39d4af5`)이 이 점검 세션의 증거 수집 시각(12:34:21)과
   거의 동시(12:34:02·12:34:33)에 올라왔다** — 병행 세션 확인(SKILL.md §0) 결과
   우연한 시간 겹침이며, 이 점검은 원인 재조사를 중복하지 않고 위 617차 후속
   항목을 그대로 인용·참조하는 쪽을 택했다.

### 2. 결정 — 이 점검은 새 Fix를 제안하지 않는다. "언제 재기동할지"만 사용자 조치로 올린다

원인 규명과 코드 수정은 이미 완료됐으므로, 이 점검이 보탤 것은 "지금 도는
프로세스는 그 수정 이전 코드로 돈다"는 배포 상태 확인과, 재기동 시점을 사용자가
판단하도록 옵션(지금 vs 15:10 이후)을 정리해 제시하는 것뿐이다.
`docs/정기점검/매일점검/MW0601-20260922-점검리포트.md` 장중 절 1-5·F-2·사용자
조치 4번 참조.

### 3. 부가 관찰 — `.git/index.lock`이 장중에도 재발, 이번엔 병행 세션 가능성

장전 절이 이미 등록한 F-1(잠금 반복 재발 원인 규명, 이 문서 위쪽 항목)에 새
가설을 추가한다. 12:34:21(이 세션의 증거 수집 완료 시점)에는 잠금이 없었는데,
12:35경 다시 생겼다 — 이번엔 병행 세션의 커밋 시각(12:34:33)과 더 가깝다.
**두 세션이 거의 동시에 같은 저장소에 git 명령을 실행했을 가능성**을 F-1의
가설 목록에 추가한다(기존 가설 (a)(b)(c)에 (d) 동시 다중 세션 접근 추가).
현재 상태는 HOLD(판정보류, 나이 199초) — STALE이 아니므로 이 세션은 회수를
시도하지 않았다(규약 준수).

### 4. Why

- 함정 ① 방지: 617차 후속이 이미 끝낸 조사를 다시 벌이지 않기 위해 재확인
  결과만 남기고 결론은 인용으로 대체했다.
- 계측 4원칙 ①: 오늘 유일한 진입(11:02, LONG 2계약)의 최종 청산이 로그상
  "하드스톱"이나 TP1 부분청산(33%, +16,926원) 이후 남은 1계약이 이익
  (+6,926원)으로 정리된 것 — `postmortem.md`가 경고한 "하드스톱=손절"
  오독 패턴의 실사례. 포지션 합계 +23,852원(+0.92pt)으로 이미 이익 확정,
  장후 승패 집계 시 손절로 세지 않을 것.

### 5. 검증

- O-i1(크래시 수정의 라이브 반영 여부)·O-i2(sizing_inversion_watch 표본 축적)를
  다음 점검 관측 항목으로 등록. 장후 점검에서 재기동 여부와 함께 판정.
- git lock 최종 상태는 이 리포트 작성 종료 시점에 재확인해 사용자 조치에 반영.
  기록된다 — 정상 기동과 구분이 안 된다(계측 4원칙 ② 계열, 미처리).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 확인 완료 (609차 후속이 재확인, 신규 아님)
## 2026-09-22 (MW0601 617차 — 장전 점검)
### 신규 등록
### 확인 완료 (617차가 재확인, 신규 아님)
## 2026-09-22 (MW0601 617차 후속 — 대시보드 크래시 조치 후속)
## 2026-09-22 (MW0601 617차 후속2 — 장중 점검)
### 신규 등록
### 확인 완료 (617차 후속2가 재확인, 신규 아님)
```

미완료 체크박스 **2807건** (끝에서 30건)
```
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
인할 것.

### 확인 완료 (617차가 재확인, 신규 아님)

- [x] `SessionStateDrop`(F-1/538-4) 재현 — 오늘도 재현됐으나 `[PreRetrain]`의
      EOD 마커 파일 직접 확인 우회 로직이 정상 작동해 실질 기능 장애 없음을
      재확인. 기존 등록 사안, 새 발견 아님.
- [x] `collect_evidence.py` git diff 실패(P2, 09-21 등록) — 오늘도 재현,
      수동 재확인 결과 실질 변경은 기존 3파일과 동일(변경 없음).
- [x] 미커밋 3파일(`levels_store.py`·`premarket_levels.py`·`cybos_autologin.py`)
      — 09-18·09-21과 동일, 변경 없음.
- [x] `joblib=1.1.0` 문서 불일치 — 09-21(609차) 등록 사안 재확인, 새 발견 아님.
- [x] `CB_CONSEC_STOP_LIMIT=3`·`CB3_P4_GRADE_BLOCK_ENABLED=False`·
      `FP_CRITICAL_GRADE_BLOCK_ENABLED=False`·`TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED=False`
      전부 `references/invariants.md` §2 기대값과 일치 — 이상 없음.
- [x] 전일(09-21) EOD 재학습 + P8 성공 — `eod_retrain_done_20260921.txt` +
      `logs/retrain_eod_20260921.log` 이중 확인.

## 2026-09-22 (MW0601 617차 후속 — 대시보드 크래시 조치 후속)

- [ ] **무가드 표시 슬롯 15건 가드** — `python scripts/audit_qtimer_slot_guards.py`
      로 목록 확인. 하나 고칠 때마다 `tests/test_617_qt_slot_guard_ratchet.py`
      의 `BASELINE` 에서 그 줄을 지운다(래칫은 한 방향).
- [ ] **엔진 슬롯 3건 처분 결정(주간회의)** — `main.py:TradingSystem` 의
      `_on_main_heartbeat`·`_effect_report_timer_tick`·`_check_limit_entry_timeout`.
      삼키면 프로세스는 살지만 **주문·청산 실패가 조용히 사라진다.** 삼키기가
      아니라 "잡아서 크게 알리고 안전상태로 전이" 쪽이 맞는지 판단할 것.
- [ ] **재기동 원인 표기** — 크래시 재기동이 `cause=STARTUP` 으로 남아 정상
      기동과 구분되지 않는다(계측 4원칙 ②). 런처가 넘겨주는 값으로 구분할 것.
- [ ] 반영 확인 — 다음 재기동 후 좌측 스플리터를 끝까지 끌어 **접히지 않는지**
      육안 확인(폭이 최소값에서 멈춰야 한다).

## 2026-09-22 (MW0601 617차 후속2 — 장중 점검)

### 신규 등록

- [ ] **O-i1 (오늘 장후 또는 다음 재기동 시 판정)** 크래시 수정(커밋 `e3e5d91`)의
      라이브 반영 여부 — 다음 재기동 후 `[Session] 재기동` 로그 직후 구간에서
      동일 `LinAlgError`/`axhline` 크래시 미재현 확인.
- [ ] **O-i2 (26주 WFA 주기, 기존 채널에 표본만 추가)** `sizing_inversion_watch`
      ([28]) qty≥3 표본 — 오늘 사이저 3계약 출력 vs 실제 진입 2계약 1건 추가.
- [ ] **F-1(지속) git lock 원인 가설 추가** — 장중 12:35경 재발 시각이 병행
      세션 커밋(12:34:33)과 가깝다. 기존 가설 (a)(b)(c)에 **(d) 동시 다중 세션
      git 접근**을 추가해 다음 점검에서 계속 조사.
- [ ] **[사용자 판단 필요] 크래시 수정 재기동 시점** — 지금(포지션 FLAT, 재기동
      위험 낮음) vs 15:10 이후. 미반영 상태에서는 같은 크래시 재발 위험이
      남아 있음(포지션 보유 중 재발 시 청산 로직 정지 위험).

### 확인 완료 (617차 후속2가 재확인, 신규 아님)

- [x] O-p1(`[HealthPolicy] Degraded 선제차단` 빈도) — 장중 4건 전부 개장구간·
      재기동 직후 국한, 자동진입 실차단 근거 없음 → **정상 판정 완료**.
- [x] `SessionStateDrop`(1-2) — 장중 추가 재현 0건(날짜전환 시점에만 발동하는
      구조이므로 장중엔 재현 조건 자체가 없음). 근본 원인 F-1(538-4) 그대로 미해결.
- [x] `collect_evidence.py` git diff 실패(1-3) — 장중 수집에서도 동일 재현
      (3일 연속: 09-21 장전·09-22 장전·09-22 장중).
- [x] 미커밋 3파일(1-4) — 오늘 신규 커밋 2건과 무관, 3파일 자체 변경 없음.

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

### `data/heartbeat_MW0601_20260922.json` — 245B · 09-22 15:47:15
```json
{
 "pid": 28960,
 "written_at": "2026-09-22T15:47:15",
 "beat_epoch": 1790059633.0851092,
 "beat_age_sec": 2.0,
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

### `data/peter_feed/_raw/2026-09-22.jsonl` — 6.5KB · 09-22 16:11:29
```json
JSONL 27행 ⏎ 첫: {"id": "2102180719430963560", "dt": "2026-09-21T23:38:34.000Z", "text": "어제 방송 올리고 퇴근했는데\n\n에러나서 지금 올라갔음....\n\n늦었지만 도움되는 내용 꽤 있으니\n\n시간 있는 칭구들은 시청~~~", "seen_at": "2026-09-22T07:11:30"} | {"id": "2102183668307660831", "dt": "2026-09-21T23:50:17.000Z", "text": "[어제 방송에서 언급한 파생포지션 설명]\n\n국장은 외놈들이 좌지우지.\n\n월마다 옵션만기일이 있는데\n\n보통 절반정도 지나면 어느정도 윤곽이 나옴.\n\n보통 위아래 그 안에서 만기일까지 지수가 결정됨.\n\n지금 세팅상 상방으로 가면 어디까지 갈 수 있다고 세팅해놨다는 뜻이지 \n\n무조건 거기 간다는", "seen_at": "2026-09-22T07:11:30"} | {"id": "2102184086945353824", "dt": "2026-09-21T23:51:57.000Z", "text": "종목 언급하는 전문가는 수도없이 많지만\n\n파생전문가는 극히 드물고(유투브, SNS 뒤져보면 알거임)\n\n나정도급은 그냥 없다고 보면 됨.\n\n나는 희귀템이니 \n\n있을때 잘 이용하시길.", "seen_at": "2026-09-22T07:11:30"} ⏎ 끝: {"id": "2102276386270695834", "dt": "2026-09-22T05:58:43.000Z", "text": "", "seen_at": "2026-09-22T07:11:30"} | {"id": "2102276432697385193", "dt": "2026-09-22T05:58:54.000Z", "text": "", "seen_at": "2026-09-22T07:11:30"} | {"id": "2102292289494409625", "dt": "2026-09-22T07:01:55.000Z", "text": "[피터리 - 2026년 9월 22일 국내 주식시장 마감 브리핑]\n\n기준: 2026년 9월 22일 15:50 KST / 한국 정규장 마감\n\n① 한눈에 보는 결론\n\n오늘 코스피는 7,017.91, +10.19포인트, +0.15%로 마감하며 이틀 연속 7,000선을 지켰다. \n코스닥은 834.38, -1.89포인트, -0.23%로 하락했다. \n숫자만 보면 코스피", "seen_at": "2026-09-22T07:11:30"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-22 15:53:20**

| 키 | 값 | 수집 대상일(2026-09-22)과 일치 |
|---|---|---|
| `date` | 2026-09-22 | 예 |
| `p8_last_success_date` | 2026-09-22 | 예 |
| `eod_retrain_ok_date` | 2026-09-22 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 160개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260922-점검리포트.md` | 46.0KB | 09-22 12:46 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_intra.md` | 70.4KB | 09-22 12:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260922_pre.md` | 54.0KB | 09-22 09:00 |
| `docs/정기점검/매일점검/MW0601-20260921-점검리포트.md` | 73.2KB | 09-21 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_post.md` | 82.1KB | 09-21 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_intra.md` | 64.9KB | 09-21 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260921_pre.md` | 54.1KB | 09-21 09:02 |
| `docs/정기점검/매일점검/MW0601-20260918-점검리포트.md` | 70.0KB | 09-18 17:59 |

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
3. 포지션 2건 중 최종청산이 하드스톱·손절 계열 **2건(100%)** — 손절 준수율 확인 필요 (레그 4행)
4. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. **SYSTEM 로그가 직전 5거래일 중앙값(17:30)보다 103분 이르게 끝났다** (오늘 15:47) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
7. 메인 스레드 정지 5초 초과 **2건** (최대 8156ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
8. `logs/20260922_WARN.log`: **[Brier] 과신** 1건(표본)
9. `logs/20260922_WARN.log`: **degraded=ON** 1건(표본)
10. `logs/20260922_WARN.log`: **ConstOut** 1건(표본)
11. `logs/20260922_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20260922_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20260922_SIGNAL.log`: **ConstOut** 8건(표본)
14. `logs/20260922_LEARNING.log`: **축퇴** 8건(표본)
15. `logs/20260922_HEALTH.log`: **degraded=ON** 2건(표본)
16. 미커밋 변경 745건 (실질 5건 · **코드(.py) 3건**) — 코드 변경이 커밋되지 않았다
17. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260922*.log` (Windows) / `grep 강제청산 logs/*20260922*.log`*