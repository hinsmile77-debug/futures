# 미륵이 증거 다이제스트 — 2026-09-16 / POST

- 생성 2026-09-16 16:17:28 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/gracious-eager-wright/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260916` · `2026-09-16` · `260916` · `0916`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **25개** 파일 · 25개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260916.txt` | 28B | 09-16 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260916.txt` | 28B | 09-16 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260916.txt` | 233B | 09-16 15:53 |
| `force_flat_alert_{DATE}.txt` | 1 | `data/force_flat_alert_20260916.txt` | 637B | 09-16 16:10 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260916.log` | 2.6KB | 09-16 16:10 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260916.log` | 434B | 09-16 16:10 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260916.json` | 245B | 09-16 16:17 |
| `launcher_{DATE}_084000_25418.log` | 1 | `logs/Mireuk_batch/launcher_20260916_084000_25418.log` | 9.3MB | 09-16 15:40 |
| `launcher_{DATE}_161033_15389.log` | 1 | `logs/Mireuk_batch/launcher_20260916_161033_15389.log` | 45.8KB | 09-16 16:13 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260916.log` | 11.5KB | 09-16 12:35 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260916.log` | 24.0KB | 09-16 15:53 |
| `retrain_intraday_{DATE}_143001.log` | 1 | `logs/retrain_intraday_20260916_143001.log` | 5.7KB | 09-16 14:30 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260916.txt` | 43B | 09-16 15:40 |
| `strategy_report_{DATE}_154012.txt` | 1 | `data/daily_reports/strategy_report_20260916_154012.txt` | 2.1KB | 09-16 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260916_DATA.log` | 343.2KB | 09-16 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260916_DEBUG.log` | 225.2KB | 09-16 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260916_HEALTH.log` | 3.8KB | 09-16 14:47 |
| `{DATE}_HOGA.log` | 1 | `logs/20260916_HOGA.log` | 53.7MB | 09-16 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260916_LEARNING.log` | 354.1KB | 09-16 16:11 |
| `{DATE}_MICRO.log` | 1 | `logs/20260916_MICRO.log` | 1000.5KB | 09-16 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260916_PROBE.log` | 96.6KB | 09-16 16:11 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260916_SIGNAL.log` | 570.0KB | 09-16 16:11 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260916_SYSTEM.log` | 776.8KB | 09-16 16:16 |
| `{DATE}_TRADE.log` | 1 | `logs/20260916_TRADE.log` | 1.0KB | 09-16 16:11 |
| `{DATE}_WARN.log` | 1 | `logs/20260916_WARN.log` | 7.9MB | 09-16 16:13 |

## 2. 코드·커밋 상태

- HEAD `5792dce` · 브랜치 `v9-dev` · 미커밋 651건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
… 외 611건
```

**당일(2026-09-16) 커밋**
```
5792dce [MW0601] 589차: 당일 차트를 15:45까지 — 가드가 화면까지 끊고 있었다
```

**최근 커밋 12건**
```
5792dce [MW0601] 589차: 당일 차트를 15:45까지 — 가드가 화면까지 끊고 있었다
3225cba [MW0601] 588차: 피터 지시를 그 분봉에 꽂는다 — 전폭 가로선 폐기 (표시 전용)
3739a54 [MW0601] 587차: 피터 지시 분봉 앵커 표시 구현계획 (문서)
7a286ab [MW0601] 588차: 587차 결함 — raw 버퍼가 live 와 다른 수명 규칙 아래 있었다 (섀도 정확도)
ea9d24f [MW0601] 587차: P1-1 Phase A — ConstOut 을 보정 전 GBM raw 로 재게 한다 (섀도, 동작 무변경)
7cb785f [MW0601] 564차 후속3: 배포 다음날 검증 — 두 기준 충족, 단 통과한 1건은 제3의 오탐
145c054 [MW0601] 586차: 사료를 넣었는데 화면이 조용한 문제 — 레이어 꺼짐을 말한다 (표시 전용)
a2d3d87 [MW0601] 585차: 롱 금지 구역 시인성 + 「거래 0」의 두 뜻 가르기 (표시 전용)
48da58f [MW0601] 584차: 피터 거래를 시안 박스 형태로 — 요소 3개 → 7개 (표시 전용)
3bea236 [MW0601] 583차: 피터 입력창 붙여넣기 시인성 + 계약 오프셋 기본 −4.00 (표시 전용)
646eac3 [MW0601] 582차 후속: 편집 스크립트가 남긴 홀로 CR 제거 (기능 무변경)
499eb64 [MW0601] 582차: 「잠정」에 실측 뒤집힘률을 붙인다 (표시 전용)
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

_본문 미열람(설정): `20260916_HOGA.log` 53.7MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260916.txt`** — 28B · 09-16 15:40:12
```
2026-09-16T15:40:12.482224
```

**`data/daily_close_started_20260916.txt`** — 28B · 09-16 15:40:07
```
2026-09-16T15:40:07.600674
```

**`data/daily_reports/strategy_report_20260916_154012.txt`** — 2.1KB · 09-16 15:40:12
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-16 15:40
========================================================
  버전    : v1.0  (81일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-1.94  MDD(자본대비)=29.9%
  당일      : WR=미측정(거래0건)  PF=미측정
  롤링20일: 누적 -6330064원  Sh=-1.94  MDD(자본대비)=29.9%  MDD(peak대비)=1056.8%
  당일손익 : broker(gross) +0원  수수료 0원  net +0원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.001  vwap_position=0.112
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
  진입후보(conf≥mc): 금일 9분  5일평균 22분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 20.9pt(5일평균 25.2pt)  1분평균변동 0.60pt(5일평균 0.69pt)
--------------------------------------------------------
  진입 퍼널(2026-09-16, 총 370분):
    FLAT 260 → conf미달 96 → CoherenceGate 5 → 게이트차단 9 → 후보 0 → 진입 0
    게이트별: 기타([차단] SHS-EKS 당일 관망 활성 — )=4  모드필터=2  콜드스타트/기타(DataAnomalyGate)=2  ATR변동성=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260916.txt`** — 233B · 09-16 15:53:16
```
completed: 2026-09-16 15:53:16
rows: 15251
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 22.1
t_retrain_s: 170.6
t_total_s: 193.1
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/force_flat_alert_20260916.txt`** — 637B · 09-16 16:10:47
```
[ForceFlatGuard] 2026-09-16 16:10:47 WARNING
  라이브 프로세스 정지(포지션은 FLAT) — 오늘 실손해는 없으나 15:40 일일마감·EOD 체인이 실행되지 않는다
  · 하트비트: 파일 1820s 전 기록 · 이벤트루프 나이 4s · pid=15196 · strikes=0
  · → 임계 180s 초과 — 라이브 프로세스가 멈춘 것으로 본다
  · 포지션: status=FLAT qty=0 · 최종갱신=2026-09-14T10:52:45.945817 (apply_exit_fill_final:하드스톱(틱))
  · → 파일 날짜가 오늘이 아니다(2026-09-14). FLAT이면 정상(오늘 진입 없음), FLAT이 아니면 전일 포지션 잔류다
```

**`data/shutdown_normal_20260916.txt`** — 43B · 09-16 15:40:27
```
auto_shutdown
2026-09-16T15:40:27.492883
```

_다이제스트 대상 8/17개 (중요도순). 제외: `20260916_MICRO.log`, `20260916_DATA.log`, `20260916_PROBE.log`, `launcher_20260916_084000_25418.log`, `launcher_20260916_161033_15389.log`, `20260916_DEBUG.log`, `mainstall_traceback_20260916.log`, `force_flat_guard_20260916.log`_

### `logs/20260916_TRADE.log` — 1.0KB · 8행 · 최종 16:11:14

- 형식 평문 · 시각 인식 8행 · INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-16 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-16 11:02:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-16 11:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-16 14:19:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-16 11:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-16 14:19:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,211) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-16 15:40:08 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
2026-09-16 16:11:09 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-16 16:11:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×8

**컴포넌트 상위 15** — `ProfitGuard`×3, `Sizer`×3, `Position`×2

### `logs/20260916_WARN.log` — 7.9MB · 38109행 · 최종 16:13:53

- 형식 평문 · 시각 인식 38103행 · CRITICAL=1, ERROR=1, WARNING=38101, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-09-16 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=333044256
2026-09-16 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-16 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-16 16:13:34 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 109.0ms | size=1924x1055 candles=410 grid=31.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=150 total_cnt=150
2026-09-16 16:13:52 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 125.0ms | size=1924x1055 candles=410 grid=47.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=47.0 axes=0.0 cross=0.0 | slow_cnt=151 total_cnt=151
2026-09-16 16:13:52 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 125.0ms | size=1924x1055 candles=410 grid=31.0 spans=0.0 candles=31.0 dir=0.0 regime=0.0 markers=47.0 axes=16.0 cross=0.0 | slow_cnt=152 total_cnt=152
2026-09-16 16:13:53 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 188.0ms | size=1924x1055 candles=410 grid=47.0 spans=0.0 candles=32.0 dir=0.0 regime=15.0 markers=78.0 axes=16.0 cross=0.0 | slow_cnt=153 total_cnt=153
2026-09-16 16:13:53 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 156.0ms | size=1924x1055 candles=410 grid=62.0 spans=0.0 candles=32.0 dir=0.0 regime=0.0 markers=62.0 axes=0.0 cross=0.0 | slow_cnt=154 total_cnt=154
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `SHS-EKS` | 1 | 09:05:02 | 09:05:02 | Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |
| ERROR | `LiveDBG` | 1 | 09:05:23 | 09:05:23 | _tick_header 간격 23578ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23578 band=ALERT since_pipe_s=0.1 |

<details><summary>CRITICAL/SHS-EKS 원문 1건</summary>

```
2026-09-16 09:05:02 [CRITICAL] SYSTEM: [SHS-EKS] Early Kill Switch 발동 — 일시 관망 conf_max=34.4% bars=5 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-16 09:05:23 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 23578ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23578 band=ALERT since_pipe_s=0.1
```

</details>

**WARNING — 태그 20종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 37920 | 08:50:13 | 16:13:53 | paintEvent 거대 캔버스 차단: 3006x1425 candles=5 |
| `LiveDBG` | 49 | 08:41:08 | 16:11:20 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SHAP` | 37 | 10:45:01 | 15:05:02 | 슬로우 감지 939ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `ScalerRefresh` | 17 | 09:11:01 | 15:09:00 | 5분 누적 수익률 -0.470% (임계 ±0.366%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 12 | 09:05:03 | 14:46:00 | level=WARNING degraded=OFF | latency=3403ms | quality=1.00 | cache_age=162s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2 |
| `CB③-P4` | 12 | 12:26:00 | 15:02:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `PipePerf` | 10 | 09:05:03 | 14:31:03 | total=3403ms | S0=3ms S1=78ms S2=16ms S3=0ms S4=125ms S5=811ms S6=856ms S7=1512ms S8=2ms |
| `CB⑤` | 10 | 09:05:05 | 14:31:03 | 파이프라인 3403ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `SHS-EKS` | 7 | 09:05:02 | 11:29:00 | Early Kill Switch 발동 conf_max=34.4% < 발동선=41.1%(mc=43.1%-margin2.0%p) core_pass=0/5봉(측정 0봉) → 일시 관망 (09:20부터 30분 간격 자동 회복 평가, 마감 11:30) |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-09-15 13:18:00 cols=['open'] existing_source=rt |
| `출처축` | 4 | 08:41:08 | 16:11:19 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `HealthPolicy` | 4 | 09:06:00 | 14:32:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=3403ms quality=1.00 cache=0s exc10m=2) | cause=S7(1512ms) |

**채널** — `SYSTEM`×38091, `HEALTH`×12

**컴포넌트 상위 15** — `ChartDBG`×37920, `LiveDBG`×50, `SHAP`×37, `ScalerRefresh`×17, `Health`×12, `CB③-P4`×12, `PipePerf`×10, `CB⑤`×10, `SHS-EKS`×8, `SessionBackfill`×6, `-`×6, `출처축`×4, `HealthPolicy`×4, `MainStallTrace`×3, `Brier`×3

### `logs/20260916_SYSTEM.log` — 776.8KB · 5759행 · 최종 16:16:19

- 형식 평문 · 시각 인식 5733행 · INFO=5733, PLAIN=26

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:32 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15196 | 행감지=30s all_threads=True
2026-09-16 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-16 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-16 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-16 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-15) 종가 버퍼 로드: 384봉
  …
2026-09-16 16:11:19 [INFO] SYSTEM: [Notify] 슬랙 알림 비활성화
2026-09-16 16:11:19 [INFO] SYSTEM: [FreezeWatchdog] 기동 — 하트비트 180s 정체 ×2회 연속 시 os._exit(43) → 런처 재기동 (2026-08-19 동결 사고 대응) | 하트비트파일=data/heartbeat_MW0601_20260916.json
2026-09-16 16:11:19 [INFO] SYSTEM: [System] Qt 이벤트 루프 진입
2026-09-16 16:11:21 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:11:21
2026-09-16 16:16:19 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 16:16:19
```

</details>

**채널** — `SYSTEM`×5733

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1204, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `System`×105, `MicroRegime`×96, `RegimeFingerprint`×67, `IntradayRegime`×47, `OptionChain`×44, `CybosSub`×28, `-`×22

### `logs/20260916_SIGNAL.log` — 570.0KB · 4981행 · 최종 16:11:16

- 형식 평문 · 시각 인식 4981행 · WARNING=2142, INFO=2839

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.418
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.414
  …
2026-09-16 16:10:58 [INFO] SIGNAL: [Model] 30m 로드 성공
2026-09-16 16:10:58 [INFO] SIGNAL: [EnsembleGater] 저장된 가중치 복원: C:\Users\82108\PycharmProjects\futures\data\ensemble_gater_weights.json
2026-09-16 16:11:09 [INFO] SIGNAL: [GapOffset] today_open=1038.50 | offset: {}
2026-09-16 16:11:10 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-16 16:11:16 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1518 | 09:00:00 | 15:09:01 | 1m 'macro_vix' scale=0.0272 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 198 | 09:00:00 | 14:41:00 | ts=08:59 horizon=1m age=1m max_z=-13.42(institution_futures_net) extreme=1 adj=1 |
| `Model` | 180 | 09:00:00 | 14:41:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 105 | 09:06:00 | 15:08:00 | 신뢰도 미달 34.4% < 38.8% → 강제 X등급 |
| `WeightCollapse` | 84 | 09:07:00 | 15:09:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 42 | 08:45:08 | 08:59:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0324) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 12 | 09:44:00 | 15:08:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 3 | 09:00:00 | 10:55:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4981

**컴포넌트 상위 15** — `ScalerFloor`×1536, `SIGNAL`×740, `Ensemble`×374, `ZeroDiag`×363, `FQAdj`×297, `MetaGate`×273, `ScalerMonitor`×199, `Model`×198, `Checklist`×114, `MicroRegime`×96, `ATR-Horizon`×95, `SHS-EKS`×95, `InstabilityGate`×92, `ScalerRefresh`×87, `WeightCollapse`×84

### `logs/20260916_LEARNING.log` — 354.1KB · 3204행 · 최종 16:11:14

- 형식 평문 · 시각 인식 3204행 · WARNING=335, INFO=2869

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-16 08:40:51 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3377 < conf_floor=0.3300 (n=95) → 보정 재적용
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3004 < conf_floor=0.3300 (span=0.00075 auc=0.685 out_max=0.3004, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3251 < conf_floor=0.3300 (span=0.00015 auc=0.544 out_max=0.3251, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-16 16:11:09 [INFO] LEARNING: [Calibration] 보정기 복원 완료 (n=888 method=platt fitted=True degenerate=False unreachable=False span=0.00630 auc=0.550 out_max=0.3479)
2026-09-16 16:11:09 [INFO] LEARNING: [Consolidator] 구 포맷 이력 7개 구간 폐기(풀링 새로 시작)
2026-09-16 16:11:09 [INFO] LEARNING: [Consolidator] 패널티 이력 로드: {'CLOSE_VOLATILE': 0.0, 'OPEN_VOLATILE': 0.0, 'OTHER': 0.0, 'STABLE_TREND': 0.0, 'LUNCH_RECOVERY': 0.0, 'EXIT_ONLY': 0.0, 'GAP_OPEN': 0.0, 'PRE_MARKET': 0.0}
2026-09-16 16:11:09 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=SKIP_LOW_SAMPLE
2026-09-16 16:11:14 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=0개 | 교체후보=3개 | CORE안전=⚠️
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 334 | 08:40:51 | 16:11:09 | 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Buffer-Timing` | 1 | 11:31:00 | 11:31:00 | total=308ms raw_fetch=148ms pred_select=44ms pred_update=63ms pred_insert=29ms verified=2 |

**채널** — `LEARNING`×3204

**컴포넌트 상위 15** — `LEARNING`×1177, `Calibration`×654, `SGD`×369, `sigma`×357, `Bias⚠`×203, `Bias`×134, `OnlineLearner`×128, `MetaConf`×74, `ScalerWarmup`×45, `BiasReset`×27, `SHAP`×11, `ExtremityCorrector`×7, `Consolidator`×5, `RF`×3, `DriftAdjuster`×3

### `logs/20260916_HEALTH.log` — 3.8KB · 25행 · 최종 14:47:01

- 형식 평문 · 시각 인식 25행 · WARNING=12, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 09:05:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3403ms | quality=1.00 | cache_age=162s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-16 09:06:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=565ms | quality=1.00 | cache_age=30s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2
2026-09-16 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 408ms (표본 20분)
2026-09-16 09:30:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=811ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-09-16 09:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=468ms | quality=1.00 | cache_age=59s | exceptions_10m=0
  …
2026-09-16 14:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=399ms | quality=1.00 | cache_age=57s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-16 14:31:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2761ms | quality=1.00 | cache_age=19s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-16 14:32:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=442ms | quality=1.00 | cache_age=77s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-16 14:46:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=295ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
2026-09-16 14:47:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=362ms | quality=1.00 | cache_age=58s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 12 | 09:05:03 | 14:46:00 | level=WARNING degraded=OFF | latency=3403ms | quality=1.00 | cache_age=162s | exceptions_10m=2 | exc_tags=[SHS-EKS]×2 |

**채널** — `HEALTH`×25

**컴포넌트 상위 15** — `Health`×24, `HealthTrend`×1

### `logs/retrain_eod_20260916.log` — 24.0KB · 152행 · 최종 15:53:16

- 형식 평문 · 시각 인식 152행 · WARNING=21, INFO=131

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 15:50:02,733 [INFO] EOD_RETRAIN: =======================================================
2026-09-16 15:50:02,733 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-16 15:50:02,733 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-16 15:50:02,734 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-16 15:50:02,734 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-16 15:53:16,913 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0409 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-16 15:53:16,914 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0731 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-16 15:53:16,917 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.07s
2026-09-16 15:53:16,923 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.07s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-16 15:53:16,926 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:36 | 15:52:31 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-16 13:59:00까지)인데 acc.txt=0.3845는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:36 | 15:52:31 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1811봉(98%)이 현행 학습구간 (현행 cutoff=2026-09-16 13:59:00 ≥ 홀드아웃 시작=2026-09-09 12:51:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-16 13:59 >= holdout_start=2026-09-09 12:51 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-0… |
| `BackfillFilter` | 1 | 15:50:13 | 15:50:13 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 26956/45606 제외 (418차 결정 1) — 남은 18650행 |
| `UnitMismatch` | 1 | 15:50:13 | 15:50:13 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/18650행 제외 (559차 P1'-2) — 남은 17204행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:16 | 15:53:16 | 백필 0행 제외 — 필터가 무효일 수 있다. 15251행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×74, `SIGNAL`×43, `EOD_RETRAIN`×25, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×36, `Retrain`×21, `EOD_RETRAIN`×14, `GuardGhost`×12, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2

### `logs/retrain_intraday_20260916_143001.log` — 5.7KB · 43행 · 최종 14:30:45

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-16 14:30:01,163 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-16 14:30:01,163 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-16 14:30:01,163 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-16 14:30:01,163 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-16 14:30:01,163 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_c8f2ded4.json
  …
2026-09-16 14:30:45,310 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-16 14:30:45,311 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-16 14:30:45,311 [INFO] LEARNING: [Retrain] 완료 | 40.4초 | 성공=6/6 호라이즌
2026-09-16 14:30:45,312 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 44.2s 데이터=4800행
2026-09-16 14:30:45,314 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_c8f2ded4.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 14:30:15 | 14:30:15 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 27006/45617 제외 (418차 결정 1) — 남은 18611행 |
| `UnitMismatch` | 1 | 14:30:15 | 14:30:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/18611행 제외 (559차 P1'-2) — 남은 17165행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

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
2026-09-16 16:11:14 [WARNING] SYSTEM: [System] 오늘 자동 종료 이력이 있어 재시작 후 자동 종료/일일 마감 재실행을 건너뜁니다.
2026-09-16 16:11:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_brok…
2026-09-16 16:11:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 69 |
| 사이저 호출(`[Sizer]`) | 3 |

### CB③ 판정 가능 시간 — **164분 / 370분 (44%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×3

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×3

### 차단 사유 69건 · 31종

| 건수 | 사유 |
|---|---|
| 20 | SHS-EKS 당일 관망 활성 — z경고10개+conf34%미달 |
| 4 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.86pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.77pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.76pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.74pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.0pt > ATR×5.0=7.7pt (시가=1038.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.5pt > ATR×5.0=8.1pt (시가=1038.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=7.2pt (시가=1038.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.1pt > ATR×5.0=7.4pt (시가=1038.50 반등위험) |

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 25건 · 최대 23578ms · 5초 초과 3건

상위 — 23578ms, 5921ms, 5734ms, 4578ms, 4172ms, 4172ms, 3843ms, 3687ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:05:23 | 23578ms | 3403ms | **20175ms (86%)** |
| 11:31:05 | 5734ms | 2112ms | **3622ms (63%)** |
| 12:35:06 | 5921ms | 573ms | **5348ms (90%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260916_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:11 2026-09-16 15:40:11 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 9분 < 하한 25분 — 최근 5거래일 평균 22분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 20분 · 도달불가 145분 · 재지않음 205분
--- Traceback ×3(표본)
09:05:23 2026-09-16 09:05:23 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260916.log
11:31:05 2026-09-16 11:31:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260916.log
12:35:06 2026-09-16 12:35:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260916.log
--- [Brier] 과신 ×3(표본)
13:24:00 2026-09-16 13:24:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.358 > 0.35
13:25:00 2026-09-16 13:25:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.366 > 0.35
13:26:00 2026-09-16 13:26:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.366 > 0.35
--- [SHAP] 슬로우 ×8(표본)
10:45:01 2026-09-16 10:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 939ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:02:01 2026-09-16 11:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 945ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:19:01 2026-09-16 11:19:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1000ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:27:02 2026-09-16 11:27:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1395ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:11 2026-09-16 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3297 band=INFO since_pipe_s=NA
09:05:23 2026-09-16 09:05:23 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 23578ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23578 band=ALERT since_pipe_s=0.1
09:05:27 2026-09-16 09:05:27 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4172ms — 메인 스레드 블로킹 발생 | pipe_elapsed=1 watchdog_alerted=[] | [MainStall] stall_ms=4172 band=INFO since_pipe_s=4.3
09:14:43 2026-09-16 09:14:43 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2407ms — 메인 스레드 블로킹 발생 | pipe_elapsed=40 watchdog_alerted=[] | [MainStall] stall_ms=2407 band=INFO since_pipe_s=41.8
--- 자동 종료 ×1(표본)
16:11:14 2026-09-16 16:11:14 [WARNING] SYSTEM: [System] 오늘 자동 종료 이력이 있어 재시작 후 자동 종료/일일 마감 재실행을 건너뜁니다.
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260916_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:44:00 2026-09-16 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5588) | 앙상블 제외는 유지
09:53:00 2026-09-16 09:53:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.6512) | 앙상블 제외는 유지
09:54:00 2026-09-16 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4453) | 앙상블 제외는 유지
10:36:00 2026-09-16 10:36:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5626) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:09 2026-09-16 15:40:09 [INFO] SYSTEM: [CB③계측] 조건성립 44분 / 판정가능 164분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-16 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-09-16 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-09-16 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:17:00 2026-09-16 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:08 2026-09-16 15:40:08 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:08 2026-09-16 15:40:08 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:07 2026-09-16 15:11:07 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:12 2026-09-16 15:40:12 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:27 2026-09-16 15:40:27 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:12 2026-09-16 15:40:12 [INFO] SYSTEM: [Notify] ℹ️ [15:40:12] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:12 2026-09-16 15:40:12 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:27 2026-09-16 15:40:27 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260916_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:00:00 2026-09-16 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:11:00 2026-09-16 10:11:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3909 ≥ 필요 0.3880 (span=0.0127, auc=0.568)
10:18:01 2026-09-16 10:18:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3860 < 필요 0.3880 (conf_floor=0.330, min_conf=0.388, span=0.0128, auc=0.565). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:42:00 2026-09-16 10:42:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3861 ≥ 필요 0.3800 (span=0.0132, auc=0.547)
--- ConstOut ×8(표본)
09:44:00 2026-09-16 09:44:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1390 dir=-1)
09:44:00 2026-09-16 09:44:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:44:00 2026-09-16 09:44:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:45:00 2026-09-16 09:45:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1390 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-16 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-16 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.5% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-16 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.5% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-16 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.418
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
08:40:30 2026-09-16 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
--- 안전망 ×8(표본)
09:07:00 2026-09-16 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-16 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-16 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-16 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260916_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3230 < conf_floor=0.3300 (span=0.00128 auc=0.601 out_max=0.3230, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3004 < conf_floor=0.3300 (span=0.00075 auc=0.685 out_max=0.3004, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3251 < conf_floor=0.3300 (span=0.00015 auc=0.544 out_max=0.3251, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-16 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3291 < conf_floor=0.3300 (span=0.00178 auc=0.607 out_max=0.3291, 기저율=0.3280 n=125) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260916_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:08 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 16:11

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260916_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 19 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 13 | 08:50:13 [WARNING] paintEvent 거대 캔버스 차단: 3006x1425 candles=5 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 15 | 09:05:02 [WARNING] Early Kill Switch 발동 conf_max=34.4% < 발동선=41.1%(mc=43.1%-margin2.0%p) core_pass=0/5봉(측정 0봉) → 일시 관망 (09:20부터 … |
| 10:00 | 장중 초반 | 1361 | 09:54:00 [WARNING] 5분 누적 수익률 -0.418% (임계 ±0.251%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1394 | 11:54:01 [WARNING] paintEvent slow 78.0ms | size=1440x683 candles=164 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |
| 14:00 | 장중 후반 · 장중 재학습 | 1271 | 13:54:00 [WARNING] paintEvent slow 78.0ms | size=1440x683 candles=276 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1464 | 15:04:00 [WARNING] paintEvent slow 78.0ms | size=1440x683 candles=334 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 1258 | 15:12:00 [WARNING] paintEvent slow 78.0ms | size=1440x683 candles=334 grid=31.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 marker… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 116 | 15:34:00 [WARNING] paintEvent slow 78.0ms | size=1886x916 candles=404 grid=16.0 spans=0.0 candles=15.0 dir=0.0 regime=16.0 marke… |

- 이 로그 생존구간: 08:41 ~ 16:13

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260916_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=15196 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 124 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 183 | 08:54:03 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 182 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 194 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 174 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 170 | 15:04:01 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 139 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 50 | 15:34:01 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 ⚠ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 16:16

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260916_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:08 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0324) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 94 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0346) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 172 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0375) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 262 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 213 | 11:55:00 [WARNING] 신뢰도 미달 37.9% < 65.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 133 | 13:55:00 [WARNING] 1m 'macro_vix' scale=0.0143 → floor=0.10 적용 (z-score 폭발 방지) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 100 | 15:04:02 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:08 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 16:11

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260915 | 17:41 | 로그 본문 |
| 20260914 | 21:21 | 로그 본문 |
| 20260911 | 15:40 | 로그 본문 |
| 20260910 | 15:40 | 로그 본문 |
| 20260909 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260916** | **16:16** | 로그 본문 |

- 델타 **+36분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
### 12:37 후속 갱신 — index.lock 스테일 확정, 그러나 회수 실패
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```

  연속 재현"이라는 사실만 근거로 추가해 기존 항목의 승인 우선순위를 재요청했다.
- index.lock을 지우지 않은 이유: SKILL.md·git_lock_guard.py 모두 "판정보류면
  절대 지우지 말 것"을 명시한다 — 실행 중인 git의 인덱스를 깨뜨릴 위험이 지우지
  않아 생기는 위험(커밋 지연)보다 크다고 판단.

### How to apply

- F-4(G-2 승인 시): 09-15 원 등록 내용대로 대시보드 배지 구현 — 이번 세션은 신규
  구현계획 없음.
- F-5(신규, 조사 전용): 장후 이후 `logs/20260916_SYSTEM.log`의 `[PipePerf]`
  S0~S8 세부 구간을 09:05:00~09:05:30 구간에서 대조해 EKS↔메인스톨 상관 가설을
  확정/기각.
- F-6(F-1p 승인 시): 09-15 원 등록 절차(`git log --oneline 632207f..ea9d24f --
  dashboard/main_dashboard.py`) 그대로 진행 — 이번 세션은 신규 절차 없음.
- index.lock: 다음 세션이 `python scripts/git_lock_guard.py --check` 재실행 —
  나이가 600초를 넘겨 스테일로 판정되면 `--reclaim`, 여전히 판정보류면 지우지 않고
  다시 이월.

### 검증

- `grep -n "SHS-EKS" logs/20260916_WARN.log logs/20260916_SIGNAL.log` — 발동
  1회(09:05:02), 회복시도 5회(09:21~11:29) 전부 실패, 12:27까지 활성 지속 확인.
  "시도 #6" 이상 로그 없음(11:30 마감 이후 재시도 중단 확인).
- `logs/20260916_SIGNAL.log` 1976~1986행·2012~2024행 — 11:02·11:04 체크리스트
  등급 A + 사이저 3계약 산출에도 SHS-EKS로 최종 차단됨을 직접 확인.
- `logs/20260916_WARN.log`에서 `ChartDBG` 카운트 20,902건(08:50:13~12:27:45) —
  09-10(335)·09-15(35,085) 대조.
- `python scripts/git_lock_guard.py --check` — 판정보류(나이 443초 ≤ 임계 600초),
  exit=3. 지우지 않음.
- `python scripts/collect_evidence.py --phase intra --pc MW0601 --out-auto` 정상
  실행, 매분 루프 커버리지 56.1%(208/371분)는 장중 조기 점검으로 인한 표기상
  착시임을 확인(09:00~12:27 구간 자체는 10분 이상 공백 0건).

### 병행 세션

- 장전 절 이후 당일 신규 커밋 0건, 별도 산출물 없음(`ls -lt docs/정기점검/
  매일점검/` 확인 — 최신 파일이 이번 세션이 만든 intra 증거 파일).

산출물: `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md`(장중 절 추가),
`docs/정기점검/매일점검/evidence_MW0601-20260916_intra.md`(수집기 자동 생성).
커밋 대기: 위 2개 파일 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`.

### 12:37 후속 갱신 — index.lock 스테일 확정, 그러나 회수 실패

- 위 "검증" 절의 12:27 판정(판정보류, 나이 443초)은 세션 종료 전 12:37에 재판정했다:
  `python scripts/git_lock_guard.py --check` → 「STALE 스테일 확정 — 0바이트·0.2시간·
  git 프로세스 0개 → 이 저장소는 커밋 불가 상태다」(exit=2).
- 스테일 확정에 따라 `python scripts/git_lock_guard.py --reclaim` 실행 →
  **`STALE 회수 실패: [Errno 1] Operation not permitted:
  '/sessions/.../futures/.git/index.lock'`** (exit=2).
- SKILL.md가 사전에 경고한 "리눅스 샌드박스 마운트 경유 시 unlink가 EPERM으로
  실패해 세션 안에서는 회수조차 못 한다"가 그대로 재현된 사례. `--reclaim`이
  스테일 판정 로직 자체는 정확했으나(0바이트·프로세스 0개·나이 임계 초과),
  삭제 실행 단계에서 OS 권한 문제로 막혔다 — 판정 로직과 삭제 실행 권한은
  별개 문제임을 실측으로 재확인.
- **결정**: 이 세션에서는 더 시도하지 않는다. 사용자가 실제 컴퓨터(Windows)에서
  직접 `C:\Users\82108\PycharmProjects\futures\.git\index.lock` 파일을 지워야
  한다 — 리포트 「사용자 조치」 5번으로 등록.
- 이 저장소는 이 세션이 만든 문서(리포트·증거·DECISION_LOG·NEXT_TODO)가
  전부 미커밋 상태로 남는다 — 사용자가 락 제거 후 직접 커밋해야 한다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-14 (MW0601 562차 — 장중 점검)
## 2026-09-14 (MW0601 563차 — 장후 점검, 종합 완성본)
## 2026-09-15 (MW0601 568차 — 장전 점검)
## 2026-09-15 (MW0601 장중 점검 — 세션 583차 추정)
## 2026-09-15 (MW0601 장후 점검 — 예약작업)
## 2026-09-16 (MW0601 장전 점검 — 예약작업)
## 2026-09-16 (MW0601 장중 점검 — 예약작업)
### 12:37 후속 갱신
```

미완료 체크박스 **2694건** (끝에서 30건)
```
- [ ] 🔴 **F-1 (538-4) — 오늘 증거 보강, 승인 대기 지속.** `session_recovery_service.py:
- [ ] ↩️ **09-14 563차 판정 정정** — "SessionStateDrop 09-14 발생분은 EOD 실패 결과라 5거래일
- [ ] **G-1 (P2, 신규)** `_log_session_rollover()` 경고 로그에 `eod_retrain_done_{prev_date}.txt`
- [ ] 신규 Fix/고도화 없음 — 그 외는 전부 기존 등록 사안 재확인만: `[CybosProbe]` 10건(F-3,
- [ ] **O-p1 (다음 거래일 09-16 장전 판정)** `[SessionStateDrop]` 09-16 아침 재현 여부
- [ ] **O-p2 (다음 장후 판정)** 08:41:25 메인 스레드 블로킹 6047ms가 개장 준비 시간대
- [ ] **G-2 (P2, 신규)** EKS가 11:30 마감을 넘겨 미해제 확정되면 대시보드에
- [ ] `institution_futures_net` z=-13.03 등 z경고 11개 구성 피처 전수 — 장후에도
- [ ] **F-1p (P1, 신규)** `[ChartDBG] paintEvent slow` 급증 원인 조사 —
- [ ] **F-2p (P2, 신규)** 대시보드/main.py 종료 사유 구분 로깅 — `closeEvent`
- [ ] **O-t1 (다음 세션 판정)** `[ChartDBG] paintEvent slow` 09-16 발생 건수 추이 —
- [ ] **O-t2 (사용자 확인 또는 정황 판단)** 오늘 1-7의 재기동(15:14:05·15:59:47,
- [ ] O-p1(장전 등록, 이월) — `[SessionStateDrop]` 09-16 아침 재현 여부, 변경 없음.
- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 7거래일 연속 재현)** `[SessionStateDrop]`
- [ ] **F-2 (P1, 신규, 사용자 결정 대기)** `features/levels/levels_store.py`·
- [ ] **F-3 (P2, 신규, 문서 전용)** `CLAUDE.md` 운영환경 표 "joblib 1.1.1" →
- [ ] **O-p5 (신규, 다음 장후 판정)** F-2 사용자 결정 이후 `features/levels/` 두
- [ ] O-p2(기존, 09-15 등록, 다음 장후 판정 이어받음) `[EODFallback]` 재발 여부 +
- [ ] O-p3(기존, 09-15 등록, 다음 장후 판정 이어받음) `[SessionBackfill]
- [ ] O-p4(기존, 09-14 등록, 다음 장후 판정 이어받음) T-BOOK-1 인수 판정
- [ ] **F-4 = G-2 승인 재요청 (P2, 09-15 등록 사안 재확인)** `[SHS-EKS]` Early Kill
- [ ] **F-5 (P2, 신규, 조사 전용)** EKS 발동(09:05:02)과 메인 스레드 23,578ms 정지
- [ ] **F-6 = F-1p 착수 재확인 (P1, 09-15 등록 사안 재확인)** `[ChartDBG]
- [ ] **O-i1 (다음 장후 판정)** `[ChartDBG]` 09-16 하루 총합 건수 확정 — 09-15
- [ ] **O-i2 (다음 장후 판정)** 12:27 이후~15:10까지 EKS 추가 회복 시도 로그가
- [ ] 🔴 **O-i3 (다음 점검 세션 재판정)** `.git/index.lock`(12:27 생성, 0바이트) —
- [ ] O-p1(장전 등록, 이월) — `[SessionStateDrop]` 재현 자체는 1-1로 확인 완료,
- [ ] O-p2~O-p4(장전 등록, 이월) — 장중 라이브 DB 분석 금지 규칙으로 미확인,
- [ ] O-p5(장전 등록, 이월) — F-2 사용자 결정 전이라 상태 변화 없음.
- [ ] 🔴 **O-i3 갱신 — index.lock 스테일 확정, 회수 실패(사용자 조치 필요)**
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
20260915.txt`).
      F2-2 산술(약 1.3거래일 후 15,000행 초과 예상)대로 오늘~내일 1m 교체되는지.
- [ ] O-p3(기존, 09-15 등록, 다음 장후 판정 이어받음) `[SessionBackfill]
      2026-09-15 차트 보충` 로그의 `inserted`·`open_fixed` — 09-16부터 `inserted=1`
      (15:45)·`open_fixed=1` 정상 여부.
- [ ] O-p4(기존, 09-14 등록, 다음 장후 판정 이어받음) T-BOOK-1 인수 판정
      (566-1~566-4) — `python scripts/defect3_collection_check.py` 실행 결과.
      선행조건 566-0(본체가 09-14 17:32 이후 재기동됐는지) 먼저 확인.
- 미커밋 646건 중 641건은 CRLF/LF 표기 차이일 뿐 내용 변경 없음(`git diff -w`로
  확인) — 이상점으로 올리지 않음. 실질 변경 5건 중 3건(`DECISION_LOG.md`·
  `NEXT_TODO.md`·`docs/정기점검/수익률향상_누적대장.md`)은 정기점검 자체 산출물.

## 2026-09-16 (MW0601 장중 점검 — 예약작업)

- [ ] **F-4 = G-2 승인 재요청 (P2, 09-15 등록 사안 재확인)** `[SHS-EKS]` Early Kill
      Switch가 09:05 발동 후 09:20~11:29 5회 회복 시도 전부 실패, 11:30 마감 이후
      재시도 없이 12:27 현재까지 자동진입 차단 지속(이틀 연속: 09-15 종일·09-16
      09:05~). 대시보드에 "오늘 자동 재개 없음 — 수동 진입만 가능" 배지 표시(G-2)
      승인 여부 결정 필요. 근거: `docs/정기점검/매일점검/
      MW0601-20260916-점검리포트.md` 이상점 1-4.
- [ ] **F-5 (P2, 신규, 조사 전용)** EKS 발동(09:05:02)과 메인 스레드 23,578ms 정지
      (09:05:23)의 상관관계 확인 — `logs/20260916_SYSTEM.log` `[PipePerf]` S0~S8
      세부 구간 대조. 코드 변경 없음. 근거: 위 리포트 이상점 1-5.
- [ ] **F-6 = F-1p 착수 재확인 (P1, 09-15 등록 사안 재확인)** `[ChartDBG]
      paintEvent slow` 12:27 시점 이미 20,902건(09-15 하루 35,085건에 이은 이틀째
      급증). `git log --oneline 632207f..ea9d24f -- dashboard/main_dashboard.py`
      착수 권고. 근거: 위 리포트 이상점 1-6.
- [ ] **O-i1 (다음 장후 판정)** `[ChartDBG]` 09-16 하루 총합 건수 확정 — 09-15
      리포트 O-t1과 함께 닫는다.
- [ ] **O-i2 (다음 장후 판정)** 12:27 이후~15:10까지 EKS 추가 회복 시도 로그가
      실제로 없는지(설계상 없어야 정상) 재확인.
- [ ] 🔴 **O-i3 (다음 점검 세션 재판정)** `.git/index.lock`(12:27 생성, 0바이트) —
      `git_lock_guard.py --check` 판정보류(나이 443초 ≤ 임계 600초)로 이번
      세션에서는 지우지 않음. 다음 세션이 재실행해 스테일이면 `--reclaim`,
      여전히 판정보류면 다시 이월.
- [ ] O-p1(장전 등록, 이월) — `[SessionStateDrop]` 재현 자체는 1-1로 확인 완료,
      최종 종결은 F-1(538-4) 승인 시점까지 열어둠. 변경 없음.
- [ ] O-p2~O-p4(장전 등록, 이월) — 장중 라이브 DB 분석 금지 규칙으로 미확인,
      다음 장후 판정 그대로 이어받음(변경 없음).
- [ ] O-p5(장전 등록, 이월) — F-2 사용자 결정 전이라 상태 변화 없음.
- 신규 Fix 없음(F-1(538-4)·F-2(1-2, features/levels)는 기존 승인/결정 대기
  그대로) — 오늘 장중도 진입 0건이라 제4·5부 대상 없음.

### 12:37 후속 갱신
- [ ] 🔴 **O-i3 갱신 — index.lock 스테일 확정, 회수 실패(사용자 조치 필요)**
      `git_lock_guard.py --check` 12:37 재판정: 「STALE 확정 — 0바이트·0.2시간·
      git 프로세스 0개」. `--reclaim` 시도 결과 `Operation not permitted`로
      삭제 실패(리눅스 샌드박스 권한 문제, SKILL.md 사전 경고와 일치). **사용자가
      직접 `C:\Users\82108\PycharmProjects\futures\.git\index.lock` 삭제 필요**
      — 삭제 전까지 이 저장소는 이 세션 권한으로 커밋 불가.

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

### `data/heartbeat_MW0601_20260916.json` — 245B · 09-16 16:17:19
```json
{
 "pid": 24324,
 "written_at": "2026-09-16T16:18:19",
 "beat_epoch": 1789543099.300808,
 "beat_age_sec": 0.5,
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

- 파일 최종 기록: **09-16 16:11:19**

| 키 | 값 | 수집 대상일(2026-09-16)과 일치 |
|---|---|---|
| `date` | 2026-09-16 | 예 |
| `p8_last_success_date` | 2026-09-16 | 예 |
| `eod_retrain_ok_date` | 2026-09-16 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 143개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260916-점검리포트.md` | 40.6KB | 09-16 12:38 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_intra.md` | 65.2KB | 09-16 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260916_pre.md` | 52.4KB | 09-16 09:01 |
| `docs/정기점검/매일점검/MW0601-20260915-점검리포트.md` | 86.6KB | 09-15 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_post.md` | 76.9KB | 09-15 16:20 |
| `docs/정기점검/매일점검/MW0601-20260914-3m호라이즌_ConstOut루프-딥다이브.md` | 39.4KB | 09-15 16:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_intra.md` | 62.0KB | 09-15 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260915_pre.md` | 55.3KB | 09-15 09:02 |

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

1. `logs/20260916_WARN.log`: ERROR 이상 2건
2. `logs/20260916_WARN.log`: **Traceback** 출현 3건 — 크래시/메모리 계열
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건) — 차단 69건. 최다 차단 사유: `SHS-EKS 당일 관망 활성 — z경고10개+conf34%미달` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
5. 메인 스레드 정지 5초 초과 **3건** (최대 23578ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260916_WARN.log`: **[Brier] 과신** 3건(표본)
7. `logs/20260916_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20260916_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260916_SIGNAL.log`: **ConstOut** 8건(표본)
10. `logs/20260916_LEARNING.log`: **축퇴** 8건(표본)
11. 미커밋 변경 651건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260916*.log` (Windows) / `grep 강제청산 logs/*20260916*.log`*