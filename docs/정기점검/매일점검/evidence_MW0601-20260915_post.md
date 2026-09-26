# 미륵이 증거 다이제스트 — 2026-09-15 / POST

- 생성 2026-09-15 16:19:00 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/hopeful-awesome-goldberg/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260915` · `2026-09-15` · `260915` · `0915`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **27개** 파일 · 27개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260915.txt` | 28B | 09-15 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260915.txt` | 28B | 09-15 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260915.txt` | 264B | 09-15 15:51 |
| `force_flat_alert_{DATE}.txt` | 1 | `data/force_flat_alert_20260915.txt` | 637B | 09-15 16:00 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260915.log` | 4.4KB | 09-15 16:00 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260915.log` | 650B | 09-15 16:00 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260915.json` | 245B | 09-15 16:18 |
| `launcher_{DATE}_084000_5416.log` | 1 | `logs/Mireuk_batch/launcher_20260915_084000_5416.log` | 8.0MB | 09-15 15:11 |
| `launcher_{DATE}_151405_17094.log` | 1 | `logs/Mireuk_batch/launcher_20260915_151405_17094.log` | 411.3KB | 09-15 15:40 |
| `launcher_{DATE}_155947_26045.log` | 1 | `logs/Mireuk_batch/launcher_20260915_155947_26045.log` | 141.8KB | 09-15 16:18 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260915.log` | 2.9KB | 09-15 08:41 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260915.log` | 20.8KB | 09-15 15:51 |
| `retrain_intraday_{DATE}_110001.log` | 1 | `logs/retrain_intraday_20260915_110001.log` | 3.2KB | 09-15 11:00 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260915.txt` | 43B | 09-15 15:40 |
| `strategy_report_{DATE}_154028.txt` | 1 | `data/daily_reports/strategy_report_20260915_154028.txt` | 2.1KB | 09-15 15:40 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260915_BACKFILL.log` | 0B | 09-15 16:08 |
| `{DATE}_DATA.log` | 1 | `logs/20260915_DATA.log` | 341.9KB | 09-15 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260915_DEBUG.log` | 231.2KB | 09-15 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260915_HEALTH.log` | 4.4KB | 09-15 15:06 |
| `{DATE}_HOGA.log` | 1 | `logs/20260915_HOGA.log` | 50.8MB | 09-15 15:36 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260915_LEARNING.log` | 457.9KB | 09-15 16:01 |
| `{DATE}_MICRO.log` | 1 | `logs/20260915_MICRO.log` | 960.2KB | 09-15 15:35 |
| `{DATE}_PROBE.log` | 1 | `logs/20260915_PROBE.log` | 110.6KB | 09-15 16:01 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260915_SIGNAL.log` | 472.5KB | 09-15 16:01 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260915_SYSTEM.log` | 780.4KB | 09-15 16:16 |
| `{DATE}_TRADE.log` | 1 | `logs/20260915_TRADE.log` | 4.8KB | 09-15 16:01 |
| `{DATE}_WARN.log` | 1 | `logs/20260915_WARN.log` | 7.2MB | 09-15 16:18 |

## 2. 코드·커밋 상태

- HEAD `ea9d24f` · 브랜치 `v9-dev` · 미커밋 645건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M config/secrets_example.py
 M config/settings.py
… 외 605건
```

**당일(2026-09-15) 커밋**
```
ea9d24f [MW0601] 587차: P1-1 Phase A — ConstOut 을 보정 전 GBM raw 로 재게 한다 (섀도, 동작 무변경)
7cb785f [MW0601] 564차 후속3: 배포 다음날 검증 — 두 기준 충족, 단 통과한 1건은 제3의 오탐
145c054 [MW0601] 586차: 사료를 넣었는데 화면이 조용한 문제 — 레이어 꺼짐을 말한다 (표시 전용)
a2d3d87 [MW0601] 585차: 롱 금지 구역 시인성 + 「거래 0」의 두 뜻 가르기 (표시 전용)
48da58f [MW0601] 584차: 피터 거래를 시안 박스 형태로 — 요소 3개 → 7개 (표시 전용)
3bea236 [MW0601] 583차: 피터 입력창 붙여넣기 시인성 + 계약 오프셋 기본 −4.00 (표시 전용)
646eac3 [MW0601] 582차 후속: 편집 스크립트가 남긴 홀로 CR 제거 (기능 무변경)
499eb64 [MW0601] 582차: 「잠정」에 실측 뒤집힘률을 붙인다 (표시 전용)
7bc79e7 [MW0601] 581차: 전환 세로선이 안 보이던 것 수정 — 실측 대비 Δ4 → Δ65~105 (표시 전용)
d1a19e6 [MW0601] 580차: 실시간 오버레이 미표시 수정 — 장중에 상태·배지를 다시 센다 (표시 전용)
```

**최근 커밋 12건**
```
ea9d24f [MW0601] 587차: P1-1 Phase A — ConstOut 을 보정 전 GBM raw 로 재게 한다 (섀도, 동작 무변경)
7cb785f [MW0601] 564차 후속3: 배포 다음날 검증 — 두 기준 충족, 단 통과한 1건은 제3의 오탐
145c054 [MW0601] 586차: 사료를 넣었는데 화면이 조용한 문제 — 레이어 꺼짐을 말한다 (표시 전용)
a2d3d87 [MW0601] 585차: 롱 금지 구역 시인성 + 「거래 0」의 두 뜻 가르기 (표시 전용)
48da58f [MW0601] 584차: 피터 거래를 시안 박스 형태로 — 요소 3개 → 7개 (표시 전용)
3bea236 [MW0601] 583차: 피터 입력창 붙여넣기 시인성 + 계약 오프셋 기본 −4.00 (표시 전용)
646eac3 [MW0601] 582차 후속: 편집 스크립트가 남긴 홀로 CR 제거 (기능 무변경)
499eb64 [MW0601] 582차: 「잠정」에 실측 뒤집힘률을 붙인다 (표시 전용)
7bc79e7 [MW0601] 581차: 전환 세로선이 안 보이던 것 수정 — 실측 대비 Δ4 → Δ65~105 (표시 전용)
d1a19e6 [MW0601] 580차: 실시간 오버레이 미표시 수정 — 장중에 상태·배지를 다시 센다 (표시 전용)
d1c17c8 [MW0601] 580차: 잔고 배지 2행 고정높이 — 캔들차트 세로 확보 (표시 전용)
632207f [MW0601] 579차: 보유 중 레벨선 — 진입·하드스톱·TP1/2/3·트레일링 (표시 전용)
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

_본문 미열람(설정): `20260915_HOGA.log` 50.8MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260915.txt`** — 28B · 09-15 15:40:28
```
2026-09-15T15:40:28.641791
```

**`data/daily_close_started_20260915.txt`** — 28B · 09-15 15:40:24
```
2026-09-15T15:40:24.493076
```

**`data/daily_reports/strategy_report_20260915_154028.txt`** — 2.1KB · 09-15 15:40:28
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-15 15:40
========================================================
  버전    : v1.0  (80일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-1.93  MDD(자본대비)=29.9%
  당일      : WR=미측정(거래0건)  PF=미측정
  롤링20일: 누적 -6301334원  Sh=-1.93  MDD(자본대비)=29.9%  MDD(peak대비)=1035.8%
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
  등급별 순EV(30일): A=+80,013원(81건,승62%)  BROKER=-2,574,591원(4건,승50%)  C=+10,973원(7건,승71%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=-8,067원(18건)  3m=-16,894원(51건)  5m=+29,046원(15건)  ?=-35,568원(174건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 27분  5일평균 25분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 22.4pt(5일평균 27.3pt)  1분평균변동 0.70pt(5일평균 0.69pt)
--------------------------------------------------------
  진입 퍼널(2026-09-15, 총 370분):
    FLAT 244 → conf미달 95 → CoherenceGate 4 → 게이트차단 27 → 후보 0 → 진입 0
    게이트별: 기타([차단] SHS-EKS 당일 관망 활성 — )=17  ATR변동성=6  모드필터=3  마감시간(신규진입금지)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260915.txt`** — 264B · 09-15 15:51:48
```
completed: 2026-09-15 15:51:48
rows: n/a(phase2_fallback)
cols: n/a(phase2_fallback)
phase2_fallback: true
horizons_replaced: 5/6
t_load_s: 11.7
t_retrain_s: 92.6
t_total_s: 104.7
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/force_flat_alert_20260915.txt`** — 637B · 09-15 16:00:02
```
[ForceFlatGuard] 2026-09-15 16:00:02 WARNING
  라이브 프로세스 정지(포지션은 FLAT) — 오늘 실손해는 없으나 15:40 일일마감·EOD 체인이 실행되지 않는다
  · 하트비트: 파일 1179s 전 기록 · 이벤트루프 나이 0s · pid=19784 · strikes=0
  · → 임계 180s 초과 — 라이브 프로세스가 멈춘 것으로 본다
  · 포지션: status=FLAT qty=0 · 최종갱신=2026-09-14T10:52:45.945817 (apply_exit_fill_final:하드스톱(틱))
  · → 파일 날짜가 오늘이 아니다(2026-09-14). FLAT이면 정상(오늘 진입 없음), FLAT이 아니면 전일 포지션 잔류다
```

**`data/shutdown_normal_20260915.txt`** — 43B · 09-15 15:40:43
```
auto_shutdown
2026-09-15T15:40:43.654792
```

_다이제스트 대상 8/18개 (중요도순). 제외: `20260915_MICRO.log`, `20260915_DATA.log`, `20260915_PROBE.log`, `launcher_20260915_084000_5416.log`, `launcher_20260915_151405_17094.log`, `launcher_20260915_155947_26045.log`, `20260915_DEBUG.log`, `force_flat_guard_20260915.log`_

### `logs/20260915_TRADE.log` — 4.8KB · 28행 · 최종 16:01:03

- 형식 평문 · 시각 인식 28행 · INFO=28

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:41:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-15 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-15 13:17:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-15 13:18:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-15 13:19:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-15 15:36:46 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-15 15:36:51 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-15 15:40:25 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
2026-09-15 16:00:57 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-15 16:01:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×28

**컴포넌트 상위 15** — `Sizer`×19, `ProfitGuard`×5, `Position`×4

### `logs/20260915_WARN.log` — 7.2MB · 35051행 · 최종 16:18:43

- 형식 평문 · 시각 인식 35045행 · CRITICAL=1, WARNING=35044, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-09-15 08:41:19 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-15 08:41:21 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-15 08:41:21 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-15 16:19:41 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.0ms | size=1533x900 candles=411 grid=15.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=32.0 axes=0.0 cross=0.0 | slow_cnt=664 total_cnt=664
2026-09-15 16:19:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 156.0ms | size=1533x900 candles=411 grid=31.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=78.0 axes=0.0 cross=0.0 | slow_cnt=665 total_cnt=665
2026-09-15 16:19:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 94.0ms | size=1533x900 candles=411 grid=15.0 spans=0.0 candles=32.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=666 total_cnt=666
2026-09-15 16:19:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 140.0ms | size=1533x900 candles=411 grid=31.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=78.0 axes=0.0 cross=0.0 | slow_cnt=667 total_cnt=667
2026-09-15 16:19:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 125.0ms | size=1533x900 candles=411 grid=16.0 spans=15.0 candles=16.0 dir=0.0 regime=16.0 markers=62.0 axes=0.0 cross=0.0 | slow_cnt=668 total_cnt=668
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `SHS-EKS` | 1 | 09:05:00 | 09:05:00 | Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |

<details><summary>CRITICAL/SHS-EKS 원문 1건</summary>

```
2026-09-15 09:05:00 [CRITICAL] SYSTEM: [SHS-EKS] Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)
```

</details>

**WARNING — 태그 21종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 34836 | 09:01:42 | 16:19:44 | paintEvent slow 31.0ms | size=1886x916 candles=17 grid=15.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 72 | 08:41:19 | 16:01:08 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SHAP` | 35 | 10:45:01 | 15:08:02 | 슬로우 감지 941ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `ScalerRefresh` | 16 | 09:22:00 | 14:58:03 | 5분 누적 수익률 +0.496% (임계 ±0.366%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `CB③-P4` | 16 | 10:16:00 | 14:49:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=23.3%) |
| `Health` | 14 | 09:01:01 | 15:05:00 | level=WARNING degraded=OFF | latency=1241ms | quality=0.86 | cache_age=98s | exceptions_10m=0 |
| `PipePerf` | 10 | 09:01:01 | 11:52:02 | total=1241ms | S0=2ms S1=64ms S2=10ms S3=0ms S4=97ms S5=945ms S6=88ms S7=29ms S8=7ms |
| `CB⑤` | 10 | 09:01:01 | 11:52:02 | 파이프라인 1241ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `출처축` | 8 | 08:41:21 | 16:01:06 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SHS-EKS` | 7 | 09:05:00 | 11:29:00 | Early Kill Switch 발동 conf_max=34.4% < 발동선=39.9%(mc=41.9%-margin2.0%p) core_pass=0/5봉(측정 0봉) → 일시 관망 (09:20부터 30분 간격 자동 회복 평가, 마감 11:30) |
| `SessionBackfill` | 4 | 08:41:51 | 08:41:51 | OHLCV 불일치 ts=2026-09-14 10:51:00 cols=['open'] existing_source=rt |
| `Contrarian` | 4 | 10:19:00 | 15:07:00 | ACTIVE | acc30m=23.3% streak=10 regime=NEUTRAL 역베팅방향=LONG |

**채널** — `SYSTEM`×35031, `HEALTH`×14

**컴포넌트 상위 15** — `ChartDBG`×34836, `LiveDBG`×72, `SHAP`×35, `ScalerRefresh`×16, `CB③-P4`×16, `Health`×14, `PipePerf`×10, `CB⑤`×10, `출처축`×8, `SHS-EKS`×8, `-`×6, `SessionBackfill`×4, `Contrarian`×4, `HealthPolicy`×3, `SessionStateDrop`×2

### `logs/20260915_SYSTEM.log` — 780.4KB · 5786행 · 최종 16:16:06

- 형식 평문 · 시각 인식 5756행 · INFO=5756, PLAIN=30

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=24544 | 행감지=30s all_threads=True
2026-09-15 08:40:53 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-15 08:40:53 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-15 08:40:53 [INFO] SYSTEM: 미륵이 초기화
2026-09-15 08:40:53 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-14) 종가 버퍼 로드: 384봉
  …
2026-09-15 16:01:07 [INFO] SYSTEM: [System] Qt 이벤트 루프 진입
2026-09-15 16:01:09 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:01:09
2026-09-15 16:06:06 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:06:06
2026-09-15 16:11:06 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:11:06
2026-09-15 16:16:06 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:16:06
```

</details>

**채널** — `SYSTEM`×5756

**컴포넌트 상위 15** — `CybosInvestorRaw`×1566, `CybosRT-TICK`×1169, `CybosRT-ROLLOVER`×406, `BAR-CLOSE`×406, `CVD-ANCHOR`×406, `TickUI`×404, `S6Detail`×370, `PipePerf`×370, `System`×119, `MicroRegime`×74, `RegimeFingerprint`×67, `CybosSub`×56, `OptionChain`×45, `SYSTEM`×25, `-`×24

### `logs/20260915_SIGNAL.log` — 472.5KB · 4296행 · 최종 16:01:06

- 형식 평문 · 시각 인식 4296행 · WARNING=1424, INFO=2872

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
  …
2026-09-15 16:00:40 [INFO] SIGNAL: [Model] 30m 로드 성공
2026-09-15 16:00:45 [INFO] SIGNAL: [EnsembleGater] 저장된 가중치 복원: C:\Users\82108\PycharmProjects\futures\data\ensemble_gater_weights.json
2026-09-15 16:00:57 [INFO] SIGNAL: [GapOffset] today_open=1039.48 | offset: {}
2026-09-15 16:00:59 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-15 16:01:06 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 942 | 09:00:02 | 14:58:04 | 1m 'macro_vix' scale=0.0340 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 124 | 09:00:00 | 13:42:00 | ts=08:59 horizon=1m age=1m max_z=-13.03(institution_futures_net) extreme=1 adj=1 |
| `Model` | 118 | 09:00:00 | 13:37:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 107 | 09:11:00 | 15:09:04 | 신뢰도 미달 34.5% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 78 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 48 | 08:45:21 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 5 | 09:54:00 | 13:06:00 | 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `MetaGate` | 1 | 11:46:00 | 11:46:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×4296

**컴포넌트 상위 15** — `ScalerFloor`×960, `SIGNAL`×740, `Ensemble`×370, `FQAdj`×357, `ZeroDiag`×343, `MetaGate`×247, `Checklist`×150, `Model`×148, `ScalerMonitor`×125, `ATR-Horizon`×121, `SHS-EKS`×121, `ScalerRefresh`×80, `WeightCollapse`×78, `MicroRegime`×74, `차단`×72

### `logs/20260915_LEARNING.log` — 457.9KB · 3748행 · 최종 16:01:04

- 형식 평문 · 시각 인식 3748행 · WARNING=649, INFO=3099

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 08:40:55 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00199 auc=0.409 out_max=0.3509 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-09-15 08:40:58 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00014 auc=0.532 out_max=0.2763 (n=105) → 보정 재적용
2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2763 < conf_floor=0.3300 (span=0.00014 auc=0.532 out_max=0.2763, 기저율=0.2762 n=105) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-15 16:00:57 [INFO] LEARNING: [Calibration] 보정기 복원 완료 (n=888 method=platt fitted=True degenerate=False unreachable=False span=0.00630 auc=0.550 out_max=0.3479)
2026-09-15 16:00:57 [INFO] LEARNING: [Consolidator] 구 포맷 이력 1개 구간 폐기(풀링 새로 시작)
2026-09-15 16:00:57 [INFO] LEARNING: [Consolidator] 패널티 이력 로드: {'CLOSE_VOLATILE': 0.0, 'OPEN_VOLATILE': 0.0, 'OTHER': 0.04, 'STABLE_TREND': 0.0, 'LUNCH_RECOVERY': 0.0, 'EXIT_ONLY': 0.0}
2026-09-15 16:00:57 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=SKIP_LOW_SAMPLE
2026-09-15 16:01:04 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=0개 | 교체후보=2개 | CORE안전=⚠️
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 648 | 08:40:58 | 16:00:57 | 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Consolidator` | 1 | 15:40:25 | 15:40:25 | 구간 'OTHER' 최근 3일 풀링(n=81) 기대손익 -0.347pt (CI상단 -0.012pt) < 0 → 패널티 +0.04 (참고 정확도 25.9%) |

**채널** — `LEARNING`×3748

**컴포넌트 상위 15** — `Calibration`×1268, `LEARNING`×1187, `SGD`×370, `sigma`×357, `Bias`×160, `Bias⚠`×146, `OnlineLearner`×86, `MetaConf`×73, `ScalerWarmup`×32, `BiasReset`×20, `SHAP`×13, `ExtremityCorrector`×11, `Consolidator`×10, `RF`×5, `DriftAdjuster`×5

### `logs/20260915_HEALTH.log` — 4.4KB · 29행 · 최종 15:06:01

- 형식 평문 · 시각 인식 29행 · WARNING=14, INFO=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 09:01:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1241ms | quality=0.86 | cache_age=98s | exceptions_10m=0
2026-09-15 09:02:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=854ms | quality=0.74 | cache_age=158s | exceptions_10m=0
2026-09-15 09:08:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1009ms | quality=1.00 | cache_age=149s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-15 09:09:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=495ms | quality=1.00 | cache_age=24s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-15 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 348ms (표본 20분)
  …
2026-09-15 13:40:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=455ms | quality=1.00 | cache_age=58s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-15 14:22:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=355ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-15 14:23:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=445ms | quality=1.00 | cache_age=57s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-15 15:05:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=514ms | quality=1.00 | cache_age=183s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-15 15:06:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=401ms | quality=1.00 | cache_age=59s | exceptions_10m=2 | exc_tags=[SHAP]×2
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 14 | 09:01:01 | 15:05:00 | level=WARNING degraded=OFF | latency=1241ms | quality=0.86 | cache_age=98s | exceptions_10m=0 |

**채널** — `HEALTH`×29

**컴포넌트 상위 15** — `Health`×28, `HealthTrend`×1

### `logs/retrain_eod_20260915.log` — 20.8KB · 146행 · 최종 15:51:49

- 형식 평문 · 시각 인식 146행 · WARNING=18, INFO=128

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 15:50:03,516 [INFO] EOD_RETRAIN: =======================================================
2026-09-15 15:50:03,516 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-15 15:50:03,517 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-15 15:50:03,517 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-15 15:50:03,517 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-15 15:51:49,327 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0375 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-15 15:51:49,329 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0873 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-15 15:51:49,333 [INFO] SIGNAL: [ScalerRefresh] ts=15:51 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-09-15 15:51:49,338 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-15 15:51:49,340 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 5 | 15:50:36 | 15:51:45 | 3m 판정 불가 — 홀드아웃 후 학습표본 부족 (5000-1853=3147 < 10000) |
| `UnitMismatch` | 4 | 15:50:14 | 15:51:32 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/18266행 제외 (559차 P1'-2) — 남은 16820행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `EODFallback` | 3 | 15:50:16 | 15:51:48 | Phase 1 로드 미달(MIN_TRAIN_BARS) — Phase 2(호라이즌별 게이트)로 전환한다. 임계를 낮춘 것이 아니라 경로를 바꾼 것이다. (563차 후속) |
| `GuardGhost` | 2 | 15:50:36 | 15:50:36 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-15 10:29:00까지)인데 acc.txt=0.5384는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 27337/45603 제외 (418차 결정 1) — 남은 18266행 |
| `Retrain` | 1 | 15:50:16 | 15:50:16 | 학습 데이터 부족 (미래가격 제거 후 14903 < 15000, intraday=False) |
| `Retrain-P2` | 1 | 15:50:16 | 15:50:16 | 1m 데이터 부족 0 < 15000 -- 건너뜀 |
| `RegimeFingerprint` | 1 | 15:51:48 | 15:51:48 | 학습분포 갱신 실패 (무해): Phase 2 폴백 — 전역 X 없음. FP-CRITICAL 은 현재 섀도라 매매 영향은 없으나 PSI 기준선이 그날치만큼 낡는다. Phase 1 복구 시 자동 재개 |

**채널** — `LEARNING`×57, `SIGNAL`×43, `EOD_RETRAIN`×26, `FEAT_REG`×5

**컴포넌트 상위 15** — `ScalerFloor`×36, `Retrain-P2`×14, `EOD_RETRAIN`×13, `Retrain`×10, `Model`×6, `CUSUM`×5, `FeatureEpoch`×5, `InvestorMeasured`×5, `FeatureReg`×5, `Retrain-Timing`×5, `GuardShadow`×5, `GuardFair`×5, `GuardClean`×5, `ModelLive`×5, `LEVELS`×4

### `logs/retrain_intraday_20260915_110001.log` — 3.2KB · 24행 · 최종 11:00:18

- 형식 평문 · 시각 인식 24행 · WARNING=2, INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-15 11:00:01,094 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-15 11:00:01,095 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_63bd0243.json
  …
2026-09-15 11:00:18,838 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-15 11:00:18,840 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-15 11:00:18,840 [INFO] LEARNING: [Retrain] 완료 | 14.6초 | 성공=1/1 호라이즌
2026-09-15 11:00:18,840 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 17.7s 데이터=4800행
2026-09-15 11:00:18,842 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_63bd0243.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 11:00:10 | 11:00:10 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 27597/45614 제외 (418차 결정 1) — 남은 18017행 |
| `UnitMismatch` | 1 | 11:00:10 | 11:00:10 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/18017행 제외 (559차 P1'-2) — 남은 16571행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
════════════════════════════════════════════════════
2026-09-15 16:01:03 [WARNING] SYSTEM: [System] 오늘 자동 종료 이력이 있어 재시작 후 자동 종료/일일 마감 재실행을 건너뜁니다.
2026-09-15 16:01:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_brok…
2026-09-15 16:01:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 72 |
| 사이저 호출(`[Sizer]`) | 19 |

### CB③ 판정 가능 시간 — **0분 / 0분 (—)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×1, **3계약**×18

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×19

### 차단 사유 72건 · 19종

| 건수 | 사유 |
|---|---|
| 43 | SHS-EKS 당일 관망 활성 — z경고11개+conf34%미달 |
| 5 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 3 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 2 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.8pt > ATR×5.0=8.0pt (시가=1039.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.3pt > ATR×5.0=7.8pt (시가=1039.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.9pt > ATR×5.0=6.7pt (시가=1039.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.1pt > ATR×5.0=6.7pt (시가=1039.48 반등위험) |
| 1 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.86pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.75pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 36건 · 최대 6047ms · 5초 초과 1건

상위 — 6047ms, 4719ms, 4547ms, 4437ms, 4343ms, 3953ms, 3922ms, 3687ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:41:25 | 6047ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260915_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:27 2026-09-15 15:40:27 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 25분/일 < 하한 60분 — 금일 27분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- ConstOut ×1(표본)
10:59:00 2026-09-15 10:59:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(3m=0.3623)
--- PSI ×1(표본)
15:40:24 2026-09-15 15:40:24 [WARNING] SYSTEM: [RegimeFingerprint] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerprint] 기준선 키 불일치` WARNING 이 기동 로그에 있는지 먼저 확인할 것
--- Traceback ×1(표본)
08:41:25 2026-09-15 08:41:25 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260915.log
--- [SHAP] 슬로우 ×8(표본)
10:45:01 2026-09-15 10:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 941ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
10:56:01 2026-09-15 10:56:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 983ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:22:01 2026-09-15 11:22:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 926ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:30:01 2026-09-15 11:30:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1088ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:25 2026-09-15 08:41:25 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6047 band=WARN since_pipe_s=NA
09:00:04 2026-09-15 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=INFO since_pipe_s=0.1
09:01:02 2026-09-15 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2391 band=INFO since_pipe_s=0.1
09:01:46 2026-09-15 09:01:46 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=41 watchdog_alerted=[] | [MainStall] stall_ms=4547 band=INFO since_pipe_s=44.3
--- 자동 종료 ×1(표본)
16:01:03 2026-09-15 16:01:03 [WARNING] SYSTEM: [System] 오늘 자동 종료 이력이 있어 재시작 후 자동 종료/일일 마감 재실행을 건너뜁니다.
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260915_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:54:00 2026-09-15 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.6488) | 앙상블 제외는 유지
10:59:00 2026-09-15 10:59:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 11:01:00 (const_output)
10:59:00 2026-09-15 10:59:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
10:59:00 2026-09-15 10:59:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=121ms fit=53ms total=177ms
--- HALT ×1(표본)
15:40:25 2026-09-15 15:40:25 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 0분 / 파이프라인 0분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-15 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-09-15 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-09-15 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:17:00 2026-09-15 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:25 2026-09-15 15:40:25 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:25 2026-09-15 15:40:25 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×2(표본)
15:11:21 2026-09-15 15:11:21 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
15:15:22 2026-09-15 15:15:22 [INFO] SYSTEM: [SchedForceExit] 15:15 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=1회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:28 2026-09-15 15:40:28 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:43 2026-09-15 15:40:43 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:28 2026-09-15 15:40:28 [INFO] SYSTEM: [Notify] ℹ️ [15:40:28] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:28 2026-09-15 15:40:28 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:43 2026-09-15 15:40:43 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260915_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-15 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:54:00 2026-09-15 09:54:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:56:00 2026-09-15 09:56:00 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
10:59:00 2026-09-15 10:59:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외
11:01:03 2026-09-15 11:01:03 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-15 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-15 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-15 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-15 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
08:40:31 2026-09-15 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
--- 안전망 ×8(표본)
09:07:00 2026-09-15 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-15 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-15 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-15 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260915_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:58 2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00152 auc=0.458 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:58 2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00199 auc=0.409 out_max=0.3509 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
08:40:58 2026-09-15 08:40:58 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00014 auc=0.532 out_max=0.2763 (n=105) → 보정 재적용
08:40:58 2026-09-15 08:40:58 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2763 < conf_floor=0.3300 (span=0.00014 auc=0.532 out_max=0.2763, 기저율=0.2762 n=105) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

### `logs/retrain_eod_20260915.log`
```
--- PSI ×1(표본)
15:51:48 2026-09-15 15:51:48,767 [WARNING] EOD_RETRAIN: [RegimeFingerprint] 학습분포 갱신 실패 (무해): Phase 2 폴백 — 전역 X 없음. FP-CRITICAL 은 현재 섀도라 매매 영향은 없으나 PSI 기준선이 그날치만큼 낡는다. Phase 1 복구 시 자동 재개
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260915_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:08 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 14:00 | 장중 후반 · 장중 재학습 | 4 | 13:59:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 2 | 15:14:41 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 2 | 15:14:41 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:36:46 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 16:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260915_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:19 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 09:00:04 [WARNING] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 14 | 09:00:04 [WARNING] _tick_header 간격 4719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4719 band=… |
| 10:00 | 장중 초반 | 1558 | 09:54:00 [WARNING] paintEvent slow 47.0ms | size=1533x900 candles=56 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 12:00 | 장중 중간점 | 1084 | 11:54:01 [WARNING] paintEvent slow 47.0ms | size=1533x900 candles=56 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 14:00 | 장중 후반 · 장중 재학습 | 1126 | 13:54:00 [WARNING] paintEvent slow 78.0ms | size=1533x900 candles=219 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1150 | 15:04:01 [WARNING] paintEvent slow 125.0ms | size=1533x900 candles=242 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=15.0 marke… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 806 | 15:14:49 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 297 | 15:34:00 [WARNING] paintEvent slow 125.0ms | size=1533x900 candles=397 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marke… |

- 이 로그 생존구간: 08:41 ~ 16:19

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260915_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:34 [INFO] 활성화 | file=logs\crash_fault.log PID=24544 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 136 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 187 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 194 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 173 | 11:54:01 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 170 | 13:54:01 [INFO] #91800 code=A056A raw_time=135400 parsed=13:54:00 price=1038.40 vol=1 bid1=1038.44 ask1=1038.50 flag=50 side=… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 200 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 179 | 15:14:29 [INFO] 활성화 | file=logs\crash_fault.log PID=9396 | 행감지=30s all_threads=True |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 98 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 ⚠ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 16:16

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260915_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:21 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 87 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0320) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 158 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 146 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 176 | 11:56:00 [WARNING] 신뢰도 미달 34.7% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 106 | 13:54:01 [WARNING] 신뢰도 미달 37.5% < 37.6% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 69 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 17 | 15:14:26 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.431 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 20 | 15:36:19 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.431 |

- 이 로그 생존구간: 08:40 ~ 16:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| 20260910 | 15:40 | 로그 본문 |
| 20260909 | 15:40 | 로그 본문 |
| 20260908 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260915** | **16:16** | 로그 본문 |

- 델타 **+36분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
`conf_hits=0/10`, 필요 3, 임계 37~39%).
- `safety/system_health.py:39` `EKS_RECOVERY_DEADLINE = datetime.time(11, 30)`
  — 이 시각 이후 재평가 없음(코드 확정, 가설 아님). 12:06:01 이후에도
  `[차단] SHS-EKS 당일 관망 활성` 상태 유지 확인(그 뒤로는 dir≠0 신호 자체가
  드물어 명시적 차단 로그가 안 남을 뿐).
- 결과: 오늘 09:00~12:35 `[진입체크]` 통과 0건·진입 0건·체결 0건·사이저 호출
  0건. 앙상블 결정 212건 전부 grade=X. 12:29에는 conf=72.5%까지 일시 회복됐지만
  EKS는 자동으로 풀리지 않았다(11:30 마감 이후 재평가 루틴 자체가 없어서).
- 별건: `[ChartDBG] paintEvent slow`(30ms 임계) 오늘 반나절(09:01~12:28)
  16,440건 — 09-08·09-09·09-11 0건, 09-10 335건, 09-14 3,200건 대비 급증.
  전체 paint 시도(22,809건)의 72%. `dashboard/main_dashboard.py:9367`
  `if _elapsed_ms > 30:`. 최근 커밋(574~582차, 오늘 새벽 580~582차 포함)이
  전부 "표시 전용" UI 요소 추가(레벨선·배너·실시간 오버레이)와 시기가 겹친다
  (인과관계는 미확인 — 관측만).

### 원인

- EKS 발동·미해제는 **설계된 안전장치의 정상 동작**이다. 2026-06-04(110차)에
  "고정 해제 임계 0.50이 나쁜 날엔 영구 관망을 유발"하는 문제가 있어
  `max(current_mc, 0.42)` 동적 임계로 고쳤는데, 오늘은 그 동적 임계(38~39%)를
  쓰고도 5번 모두 미달이었다 — 즉 임계 설계 문제가 아니라 **오늘 실제로 신뢰도가
  계속 낮았다.** 원인 후보로 `institution_futures_net` z=-13.03(09:00 직후) 등
  스케일러 극단값이 있으나 z경고 11개 구성 피처 전수는 미확인.
- ChartDBG paintEvent slow 급증의 근본 원인은 미조사 — 이번 세션은 관측만 함.

### 결정

- 장중이므로 코드 변경 없음(라이브 프로세스 가동 중). EKS는 고칠 대상이 아니라
  기록 대상(설계대로 동작).
- 신규 이상점 1-4(EKS 종일 관망, P1)·1-5(ChartDBG 급증, P1)·1-6(`.git/index.lock`
  재생성, P1) 등록. 이상점 1-1·1-2는 지속, 1-3은 정정(장전 종료 시점엔 락 없었음,
  이 장중 세션이 새 락을 다시 만듦).
- G-2(EKS 종일 미해제 시 대시보드 배지 상시 표시) 고도화 제안 등록 — 장후 적용 검토.

### Why

- P1 분류 근거: 절대원칙 위반은 아니나(설계된 안전장치), 오늘 하루 매매 기회가
  사실상 소멸한 사실은 사용자가 반드시 인지해야 할 만큼 영향이 크다.
- ChartDBG는 계측 4원칙과 직접 연관은 없으나 급증 추세(0→335→3,200→16,440)
  자체가 근거 있는 이상점.

### How to apply

- 이번 세션은 코드를 변경하지 않았다. G-2(대시보드 배지)와 ChartDBG 원인 조사는
  다음 장후 세션 후보.

### 검증

- `safety/system_health.py` 코드 직접 읽어 11:30 마감 이후 재평가 없음을 확정.
- `logs/20260915_WARN.log`·`_SYSTEM.log`·`_SIGNAL.log` grep으로 EKS 발동~5회
  재평가 실패~12:06 이후 상태 유지를 시계열로 확인.
- `dashboard/main_dashboard.py:9367` 코드 확인 + 5거래일 `paintEvent slow`
  건수 대조(0/0/335/0/3200/16440).
- `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md` grep으로 "ChartDBG" 관련 기존
  등록 사안 없음 확인(함정① 준수).

### 병행 세션

- 이 세션 시작 시 당일 커밋 4건 전부 00:38~00:55(새벽, 장 시작 전) 확인 —
  이 점검 세션과 겹치지 않음. 다른 딥다이브 파일 신규 생성 없음.
- `.git/index.lock`이 이 세션 진행 중(12:27) 다시 생성됨 — 12:44 재확인 시
  스테일 확정으로 전환, `--reclaim` 시도했으나 `Operation not permitted`로
  세션 내 회수 실패(샌드박스 구조적 제약, 장전 1-3과 동일 패턴 재발). 사용자
  조치 3번으로 이관.

산출물: `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md`(장중 절 append),
`docs/정기점검/매일점검/evidence_MW0601-20260915_intra.md`(수집기 자동 생성).
커밋 대기: 위 2개 파일 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-11 (MW0601 558차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖 — 변경 없음)
### 다음 세션 관측
## 2026-09-14 (MW0601 560차 — 장전 점검)
## 2026-09-14 (MW0601 562차 — 장중 점검)
## 2026-09-14 (MW0601 563차 — 장후 점검, 종합 완성본)
## 2026-09-15 (MW0601 568차 — 장전 점검)
## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)
```

미완료 체크박스 **2675건** (끝에서 30건)
```
- [ ] **O-t2′·O-t6·O-t7** (556차 후속 F-5·G-4·G-1 라이브 검증) — 변경 없이 유지.
- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 4거래일 연속 재현)** `[SessionStateDrop]` 완료
- [ ] 신규 Fix/고도화 없음 — 549-4(수집기 git diff 재시도)는 기존 승인·처리 대기 상태
- [ ] **O-p1 (오늘 장후 판정)** 2026-09-13(559차) 배포 `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED=True`가
- [ ] **O-p2 (장중~장후 판정)** `[ConfFloorGuard]` 09:00:00 1회 발동이 오늘 오실레이션으로
- [ ] **O-p3 (다음 거래일 09-15 장전 판정)** `[SessionStateDrop]` 5거래일 연속 재현 여부.
- [ ] 신규 Fix/고도화 없음 — 09:36 장중 재학습 실패는 병행 세션(`d9bdea6`)이 이미
- [ ] ↩️ **O-p1 전제 정정** — `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED` 소비 지점이
- [ ] **O-i1 (신규, 장후 판정)** 10:51:01 SHORT 2계약 진입이 `[Position] 진입`
- [ ] **1-4 (P2, 저우선)** 병합 커밋 `19c4076`에 PC명 태그(`[MW0601]`) 없음 —
- [ ] **O-p3 (변경 없음)** `[SessionStateDrop]` 5거래일 연속 재현 여부 — 다음
- [ ] 🔴 **F-1 (P0, 신규, 승인 대기) EOD 재학습 학습 데이터 풀 부족 조사·조치** —
- [ ] 🔴 **F-2 (P0, 신규, 저위험·즉시 적용 가능) `log_manager.signal()` printf
- [ ] **G-1 (P2, 신규)** `BackfillFilter`의 `feature_quality_score==0.3` 마커
- [ ] **O-t1 (다음 EOD 성공일 또는 F-1 승인 후 판정)** 병행 개발 세션의
- [ ] **O-t2 (F-1 조사 완료 시 판정)** `BackfillFilter` 마커가 광범위한 초기
- [ ] **O-t3 (다음 거래일 09-15 장후 판정)** 내일 EOD 재학습이 정상 완료되는지 —
- [ ] **1-8 (P1, 신규, 다음 세션 코드 추적)** `[Position] 진입` 로그 한 줄이
- [ ] P5-06(누적대장) 표본 갱신 — 오늘 1건 -183,558원 추가(20건/6거래일,
- [ ] 🔴 **F-1 (538-4) — 오늘 증거 보강, 승인 대기 지속.** `session_recovery_service.py:
- [ ] ↩️ **09-14 563차 판정 정정** — "SessionStateDrop 09-14 발생분은 EOD 실패 결과라 5거래일
- [ ] **G-1 (P2, 신규)** `_log_session_rollover()` 경고 로그에 `eod_retrain_done_{prev_date}.txt`
- [ ] 신규 Fix/고도화 없음 — 그 외는 전부 기존 등록 사안 재확인만: `[CybosProbe]` 10건(F-3,
- [ ] **O-p1 (다음 거래일 09-16 장전 판정)** `[SessionStateDrop]` 09-16 아침 재현 여부
- [ ] **O-p2 (다음 장후 판정)** 08:41:25 메인 스레드 블로킹 6047ms가 개장 준비 시간대
- [ ] **O-i1 (오늘 장후 판정)** EKS가 15:10까지 결국 미해제로 끝났는지 —
- [ ] **G-2 (P2, 신규)** EKS가 11:30 마감을 넘겨 미해제 확정되면 대시보드에
- [ ] **O-i2 (오늘 장후 판정, P1 후보)** `[ChartDBG] paintEvent slow` 급증
- [ ] **O-i3 (이 세션 종료 직전 판정)** `.git/index.lock`(12:27 재생성분)
- [ ] 확인 필요(장후 전달) — MetaGate `meta_conf` 5회 연속 과소(11:46:00, streak=5)가
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
.
- [ ] P5-06(누적대장) 표본 갱신 — 오늘 1건 -183,558원 추가(20건/6거래일,
      누계 -14,707,793원). F-10 승인 여부 여전히 사용자 결정 대기.

## 2026-09-15 (MW0601 568차 — 장전 점검)

- [ ] 🔴 **F-1 (538-4) — 오늘 증거 보강, 승인 대기 지속.** `session_recovery_service.py:
      increment_session()` 날짜 전환 시 EOD/P8 완료 마커(`p8_last_success_date`·
      `eod_retrain_ok_date`) 이어받기. 오늘 09-14 EOD 성공(`logs/retrain_eod_20260914.log`
      17:15:37 확인) 뒤에도 09-15 아침 마커가 소실됨을 확인해, 이 결함이 "EOD 실패 시에만"이
      아니라 **날짜 전환마다 항상 발생**하는 구조적 문제임을 코드로 확정(`increment_session`이
      새 딕셔너리를 5개 키로만 구성). 근거: `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md`
      이상점 1-1.
- [ ] ↩️ **09-14 563차 판정 정정** — "SessionStateDrop 09-14 발생분은 EOD 실패 결과라 5거래일
      연속 재현 집계에서 제외" 판정은 전제가 틀렸다(09-14 EOD는 성공했다). 재현일 재계산:
      09-08·09-09·09-10·09-11·09-14·09-15 = 6거래일 연속(09-07 0건). 09-14 절 본문은 수정하지
      않음(append 규약), 정정은 09-15 DECISION_LOG 항목에 기록.
- [ ] **G-1 (P2, 신규)** `_log_session_rollover()` 경고 로그에 `eod_retrain_done_{prev_date}.txt`
      존재 여부(=전날 EOD 성공 여부)를 함께 찍어, 다음에 같은 경고가 뜰 때 "구조적 버그 때문인지
      진짜 EOD 실패 때문인지"를 로그 한 줄로 즉시 구분 가능하게 한다. F-1과 독립 적용 가능.
- [ ] 신규 Fix/고도화 없음 — 그 외는 전부 기존 등록 사안 재확인만: `[CybosProbe]` 10건(F-3,
      0819 종결, 재상정 금지), `joblib=1.1.0` vs 문서 1.1.1(491차 기지), `[ConfFloorGuard]`
      09:00:00 1회(09-14와 동일 패턴, 09-14 563차가 이미 지속-종결 판정), 수집기 `git diff`
      실패·미커밋 640건 실질변경 미측정(기존 544-6/549-4 재현).
- [ ] **O-p1 (다음 거래일 09-16 장전 판정)** `[SessionStateDrop]` 09-16 아침 재현 여부
      (F-1 미적용 유지 시 재현 확실시 — 구조적 버그이므로). 재현되면 "7거래일 연속"으로 갱신.
- [ ] **O-p2 (다음 장후 판정)** 08:41:25 메인 스레드 블로킹 6047ms가 개장 준비 시간대
      (08:40~08:42)의 정상 패턴인지 — 최근 5거래일 같은 시간대 블로킹 분포와 비교 필요
      (이번 세션은 시간 관계상 비교하지 않음). 482차 F-3 섀도 계측 대상 구간.

## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)

- [ ] **O-i1 (오늘 장후 판정)** EKS가 15:10까지 결국 미해제로 끝났는지 —
      `[SHS-EKS]` 해제 로그 유무로 확인. 없으면 "오늘 종일 관망 확정"으로 최종 기록.
- [ ] **G-2 (P2, 신규)** EKS가 11:30 마감을 넘겨 미해제 확정되면 대시보드에
      "오늘 자동 재개 없음 — 수동 진입만 가능" 배지를 상시 표시. 근거:
      `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` 이상점 1-4.
- [ ] **O-i2 (오늘 장후 판정, P1 후보)** `[ChartDBG] paintEvent slow` 급증
      (0→335→3200→16440건, 최근 5거래일) 원인 조사 — 574~582차 커밋(표시 전용 UI
      추가)과의 인과 여부. `dashboard/main_dashboard.py:9367` 임계 30ms.
- [ ] **O-i3 (이 세션 종료 직전 판정)** `.git/index.lock`(12:27 재생성분)
      스테일 확정 여부 — `git_lock_guard.py --check` 재실행 후 스테일이면
      사용자 조치로 삭제 요청, 판정보류면 절대 지우지 말 것.
- [ ] 확인 필요(장후 전달) — MetaGate `meta_conf` 5회 연속 과소(11:46:00, streak=5)가
      오늘 EKS·저신뢰도 환경과 같은 원인 계열인지, `institution_futures_net` z=-13.03
      등 z경고 11개 구성 피처 전수 목록 확인.

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

### `data/heartbeat_MW0601_20260915.json` — 245B · 09-15 16:18:37
```json
{
 "pid": 10652,
 "written_at": "2026-09-15T16:19:37",
 "beat_epoch": 1789456776.8888805,
 "beat_age_sec": 0.8,
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

- 파일 최종 기록: **09-15 16:01:07**

| 키 | 값 | 수집 대상일(2026-09-15)과 일치 |
|---|---|---|
| `date` | 2026-09-15 | 예 |
| `p8_last_success_date` | 2026-09-15 | 예 |
| `eod_retrain_ok_date` | 2026-09-15 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 139개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` | 39.4KB | 09-15 16:10 |
| `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` | 45.8KB | 09-15 12:38 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_intra.md` | 62.0KB | 09-15 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_pre.md` | 55.3KB | 09-15 09:02 |
| `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md` | 77.8KB | 09-14 16:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_post.md` | 77.8KB | 09-14 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_intra.md` | 65.8KB | 09-14 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_pre.md` | 51.2KB | 09-14 09:01 |

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

1. `logs/20260915_WARN.log`: ERROR 이상 1건
2. `logs/20260915_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건) — 차단 72건. 최다 차단 사유: `SHS-EKS 당일 관망 활성 — z경고11개+conf34%미달` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
5. 메인 스레드 정지 5초 초과 **1건** (최대 6047ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260915_WARN.log`: **ConstOut** 1건(표본)
7. `logs/20260915_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20260915_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260915_SIGNAL.log`: **ConstOut** 8건(표본)
10. `logs/20260915_LEARNING.log`: **축퇴** 8건(표본)
11. 미커밋 변경 645건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260915*.log` (Windows) / `grep 강제청산 logs/*20260915*.log`*