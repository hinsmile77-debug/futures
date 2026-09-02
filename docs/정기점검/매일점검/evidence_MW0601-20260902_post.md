# 미륵이 증거 다이제스트 — 2026-09-02 / POST

- 생성 2026-09-02 16:17:01 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/zen-zealous-hypatia/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260902` · `2026-09-02` · `260902` · `0902`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **27개** 파일 · 27개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260902.txt` | 28B | 09-02 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260902.txt` | 28B | 09-02 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260902.txt` | 209B | 09-02 15:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260902.log` | 1.4KB | 09-02 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260902.log` | 217B | 09-02 15:46 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260902.json` | 243B | 09-02 15:40 |
| `launcher_{DATE}_084001_7533.log` | 1 | `logs/Mireuk_batch/launcher_20260902_084001_7533.log` | 1.6MB | 09-02 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260902.log` | 15.6KB | 09-02 14:12 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260902.log` | 20.8KB | 09-02 15:48 |
| `retrain_intraday_{DATE}_093600.log` | 1 | `logs/retrain_intraday_20260902_093600.log` | 2.7KB | 09-02 09:36 |
| `retrain_intraday_{DATE}_120001.log` | 1 | `logs/retrain_intraday_20260902_120001.log` | 2.7KB | 09-02 12:00 |
| `retrain_intraday_{DATE}_130300.log` | 1 | `logs/retrain_intraday_20260902_130300.log` | 2.7KB | 09-02 13:03 |
| `retrain_intraday_{DATE}_134300.log` | 1 | `logs/retrain_intraday_20260902_134300.log` | 2.7KB | 09-02 13:43 |
| `retrain_intraday_{DATE}_142700.log` | 1 | `logs/retrain_intraday_20260902_142700.log` | 2.7KB | 09-02 14:27 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260902.txt` | 43B | 09-02 15:40 |
| `strategy_report_{DATE}_154013.txt` | 1 | `data/daily_reports/strategy_report_20260902_154013.txt` | 2.4KB | 09-02 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260902_DATA.log` | 345.2KB | 09-02 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260902_DEBUG.log` | 231.1KB | 09-02 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260902_HEALTH.log` | 4.7KB | 09-02 14:56 |
| `{DATE}_HOGA.log` | 1 | `logs/20260902_HOGA.log` | 47.9MB | 09-02 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260902_LEARNING.log` | 293.2KB | 09-02 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260902_MICRO.log` | 966.3KB | 09-02 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260902_PROBE.log` | 96.6KB | 09-02 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260902_SIGNAL.log` | 582.4KB | 09-02 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260902_SYSTEM.log` | 796.1KB | 09-02 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260902_TRADE.log` | 12.6KB | 09-02 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260902_WARN.log` | 64.8KB | 09-02 15:40 |

## 2. 코드·커밋 상태

- HEAD `a3f70ab` · 브랜치 `v9-dev` · 미커밋 519건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
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
… 외 479건
```

**당일(2026-09-02) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
a3f70ab [MW0601] 514차 후속: 장후 자동조치 — F-A(P1-3) · F-B(고도화①) · F-C(고도화②/P5-신규)
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
db48586 [MW0601] 507차 후속: 리포트 제8부에 커밋 해시 기입
2d6a1bb [MW0601] 507차 후속: 장후 자동조치 — F-7·F-8·F-11·F-12·F-14 + G-4·G-5
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `9999` | `9999` | 일치 | 모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. 재검토 기한 2026-08-29 |
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

### 차단 게이트 전수 인벤토리 — 33개 중 **9개 꺼짐**

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

_본문 미열람(설정): `20260902_HOGA.log` 47.9MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260902.txt`** — 28B · 09-02 15:40:13
```
2026-09-02T15:40:13.157850
```

**`data/daily_close_started_20260902.txt`** — 28B · 09-02 15:40:08
```
2026-09-02T15:40:08.851494
```

**`data/daily_reports/strategy_report_20260902_154013.txt`** — 2.4KB · 09-02 15:40:13
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-02 15:40
========================================================
  버전    : v1.0  (71일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-4.76  MDD(자본대비)=26.5%
  당일      : WR=75.0%  PF=0.01
  롤링20일: 누적 -11306214원  Sh=-4.76  MDD(자본대비)=26.5%  MDD(peak대비)=675.1%
  당일손익 : broker(gross) -5,498,000원  수수료 82,803원  net -5,265,803원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : WATCHLIST (2.75)
  PSI     : 0.003 (CLEAR)
  PSI/feat: cvd_delta=0.003  ofi_pressure=0.002  vwap_position=0.046
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -495,994원  승률 65.0%  합계 -9,919,879원
  등급별 순EV(30일): A=+5,678원(140건,승67%)  BROKER=-5,380,798원(2건,승0%)  C=-1,490원(33건,승73%)  MANUAL=-18,904원(91건,승45%)
  호라이즌별 순EV(30일): 1m=+13,044원(25건)  3m=-7,161원(121건)  5m=+44,423원(24건)  ?=-127,728원(96건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 23분  5일평균 14분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 21.5pt(5일평균 29.1pt)  1분평균변동 0.71pt(5일평균 0.85pt)
--------------------------------------------------------
  진입 퍼널(2026-09-02, 총 370분):
    FLAT 243 → conf미달 97 → CoherenceGate 7 → 게이트차단 16 → 후보 7 → 진입 3
    └ 등급상향경로(앙상블X→체크리스트통과): 1건 [285차-P5]
    게이트별: 체크리스트항목미달=5  ATR변동성=4  포지션보유중(평가생략)=3  쿨다운=2  콜드스타트/기타(RegimeOverride)=1  모드필터=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 4건
      └ 상세: JointGateBlock=4
      └ JointGateBlock 4건 (무정보폴백 3건 = 75.0%) [표본 16건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260902.txt`** — 209B · 09-02 15:48:53
```
completed: 2026-09-02 15:48:53
rows: 40789
cols: 97
horizons_replaced: 5/6
t_load_s: 43.0
t_retrain_s: 185.6
t_total_s: 229.2
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260902.txt`** — 43B · 09-02 15:40:28
```
auto_shutdown
2026-09-02T15:40:28.166997
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260902_120001.log`, `retrain_intraday_20260902_130300.log`, `retrain_intraday_20260902_134300.log`, `retrain_intraday_20260902_142700.log`, `20260902_MICRO.log`, `20260902_DATA.log`, `20260902_PROBE.log`, `launcher_20260902_084001_7533.log`_

### `logs/20260902_TRADE.log` — 12.6KB · 93행 · 최종 15:40:09

- 형식 평문 · 시각 인식 93행 · WARNING=2, INFO=91

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-02 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-02 08:41:09 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-09-02 08:41:09 [WARNING] TRADE: [Position] 브로커 기준 동기화: LONG 3계약 @ 1076.0 | 손절=1075.25
2026-09-02 08:45:09 [INFO] TRADE: [TickStop-S0C] 하드스톱(틱) LONG 3ct tick=1041.44 stop=1075.25 → 주문 전송
  …
2026-09-02 14:41:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,608,281) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdvisedSkip]
2026-09-02 14:41:00 [INFO] TRADE: [모드필터 차단] SHORT->SHORT 1계약 C급 (모드=hybrid, 허용=['A', 'B'])
2026-09-02 14:42:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,608,281) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
2026-09-02 14:42:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 1계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-09-02 15:40:09 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 1 | 08:41:09 | 08:41:09 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `Position` | 1 | 08:41:09 | 08:41:09 | 브로커 기준 동기화: LONG 3계약 @ 1076.0 | 손절=1075.25 |

**채널** — `TRADE`×93

**컴포넌트 상위 15** — `Chejan`×22, `Position`×17, `Sizer`×13, `주문요청`×9, `ProfitGuard`×4, `청산 완료`×4, `JointGateBlock 차단`×4, `TickStop-S0C`×3, `진입체크`×3, `체결진입`×3, `TickTP1`×3, `체결청산-부분`×2, `체결진입보정`×2, `TP1 부분청산`×2, `PositionFallback`×1

### `logs/20260902_WARN.log` — 64.8KB · 316행 · 최종 15:40:12

- 형식 평문 · 시각 인식 306행 · CRITICAL=1, ERROR=2, WARNING=303, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-09-02 08:41:09 [WARNING] SYSTEM: [BrokerSync] balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '42172727', '총평가손익': '42172727', '실현손익': '0', '총평가': '0.00', '총평가수익률': '42172727', '추정자산': '-1144000'}
2026-09-02 08:41:09 [WARNING] SYSTEM: [BrokerSync] startup sync raw rows=1 nonempty_rows=1 all_blank_rows=False record_name='CpTd0723' prev_next='' rows=[{'종목코드': 'A0569', '종목명': '¹Ì´ÏÄÚ½ºÇÇ F 202609', '구분': '매수', '매매구분': '매수', '잔고수량': '3', '청산가능': '3', '평균가': '1076.0', '매입단가': '1076.0', '현재가': '',…
  …
드리프트: WATCHLIST (Lv.1)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -5265803원
════════════════════════════════════════════════════
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `BrokerSync` | 1 | 08:41:09 | 08:41:09 | startup sync 완료: FLAT -> LONG 3계약 @ 1076.00 |
| ERROR | `LiveDBG` | 1 | 11:28:57 | 11:28:57 | _tick_header 간격 56875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=56875 band=ALERT since_pipe_s=0.1 |
| ERROR | `NetRecon` | 1 | 15:40:09 | 15:40:09 | 🔴 net 불일치 — 엔진 -5,265,803원 vs 브로커 -5,564,446원 (잔차 +298,643원, 허용 ±13,289) |

<details><summary>CRITICAL/BrokerSync 원문 1건</summary>

```
2026-09-02 08:41:09 [CRITICAL] SYSTEM: [BrokerSync] startup sync 완료: FLAT -> LONG 3계약 @ 1076.00
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-02 11:28:57 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 56875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=56875 band=ALERT since_pipe_s=0.1
```

</details>

<details><summary>ERROR/NetRecon 원문 1건</summary>

```
2026-09-02 15:40:09 [ERROR] SYSTEM: [NetRecon] 🔴 net 불일치 — 엔진 -5,265,803원 vs 브로커 -5,564,446원 (잔차 +298,643원, 허용 ±13,289)
```

</details>

**WARNING — 태그 38종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 78 | 08:41:09 | 15:33:35 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 22 | 08:45:10 | 13:35:34 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='101' | pending='EXIT_FULL:LONG qty=3 filled=0 order_no=? reason=하드스톱(틱) req_at=08:45:09.952' |… |
| `ChejanMatch` | 22 | 08:45:10 | 13:35:34 | order_no='101' | pending='EXIT_FULL:LONG qty=3 filled=0 order_no=101 reason=하드스톱(틱) req_at=08:45:09.952' | pending_matched=True |
| `PendingOrder` | 18 | 08:45:09 | 13:35:34 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1075.25, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `PipePerf` | 18 | 09:00:02 | 14:28:03 | total=2491ms | S0=3ms S1=10ms S2=0ms S3=0ms S4=92ms S5=863ms S6=1347ms S7=153ms S8=24ms |
| `Health` | 18 | 09:00:02 | 14:55:01 | level=WARNING degraded=OFF | latency=2491ms | quality=0.86 | cache_age=46s | exceptions_10m=1 |
| `CB⑤` | 18 | 09:00:03 | 14:28:03 | 파이프라인 2491ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 14 | 09:11:00 | 14:57:01 | 5분 누적 수익률 +0.367% (임계 ±0.367%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ExitCooldown` | 8 | 08:45:10 | 13:35:34 | 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10) |
| `HealthPolicy` | 8 | 09:01:02 | 14:29:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2491ms quality=0.86 cache=0s exc10m=1) | cause=S6(1347ms) |
| `MainStallTrace` | 7 | 09:00:10 | 14:12:06 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260902.log |
| `SHAP` | 7 | 13:20:01 | 14:57:02 | 슬로우 감지 914ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림) |

**채널** — `SYSTEM`×288, `HEALTH`×18

**컴포넌트 상위 15** — `LiveDBG`×79, `ChejanFlow`×22, `ChejanMatch`×22, `PendingOrder`×18, `PipePerf`×18, `Health`×18, `CB⑤`×18, `ScalerRefresh`×14, `-`×9, `ExitCooldown`×8, `HealthPolicy`×8, `MainStallTrace`×7, `SHAP`×7, `ExitFillFlow`×6, `BrokerSync`×5

### `logs/20260902_SYSTEM.log` — 796.1KB · 5824행 · 최종 15:40:28

- 형식 평문 · 시각 인식 5803행 · INFO=5803, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:33 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.9MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-09-02 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=2768 | 행감지=30s all_threads=True
2026-09-02 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-02 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-02 08:40:49 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-02 15:40:13 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-02 15:40:13 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-02 15:40:28 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-02 15:40:28 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-02 15:40:28 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5803

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1126, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `MicroRegime`×122, `System`×98, `RegimeFingerprint`×68, `CybosEvent`×44, `BalanceUI`×42, `OptionChain`×41, `IntradayRegime`×28

### `logs/20260902_SIGNAL.log` — 582.4KB · 5091행 · 최종 15:40:09

- 형식 평문 · 시각 인식 5091행 · WARNING=2196, INFO=2895

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
  …
2026-09-02 15:10:02 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-02 15:40:09 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-02 15:40:09 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 26분(7.0%) / DN 135분(36.5%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-02 15:40:09 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-02 age=38m extreme=671 refresh=41 grade_x=97 cb3=0
2026-09-02 15:40:09 [INFO] SIGNAL: [ModelHealth] date=2026-09-02 앙상블유효가동률=74.6% | 파이프라인 370분 | ConstOut 6회/12분 {"3m": {"events": 5, "minutes": 10}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 82분 | 장중재학습 5회 | CB③ ready 65분/370분 (18%) (리셋 2회, 표본손실 60건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1608 | 09:00:04 | 14:57:01 | 1m 'macro_krw_chg' scale=0.0502 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 180 | 09:01:01 | 14:15:00 | 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 162 | 09:01:01 | 14:15:00 | ts=09:00 horizon=1m age=1m max_z=+7.79(va_bandwidth) extreme=4 |
| `Checklist` | 108 | 09:06:00 | 15:04:00 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `WeightCollapse` | 82 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 48 | 08:45:09 | 08:59:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0327) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 6 | 09:35:00 | 14:26:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 2 | 09:00:01 | 10:55:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5091

**컴포넌트 상위 15** — `ScalerFloor`×1668, `SIGNAL`×740, `Ensemble`×374, `FQAdj`×367, `ZeroDiag`×349, `Model`×216, `MetaGate`×211, `ScalerMonitor`×163, `Checklist`×139, `InstabilityGate`×133, `MicroRegime`×122, `ATR-Horizon`×115, `ScalerRefresh`×95, `WeightCollapse`×82, `차단`×74

### `logs/20260902_LEARNING.log` — 293.2KB · 2862행 · 최종 15:40:09

- 형식 평문 · 시각 인식 2862행 · WARNING=166, INFO=2696

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00008 auc=0.274 out_max=0.0875 (기준 auc<0.53 and span<0.020, 기저율=0.0875 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00217 auc=0.298 out_max=0.2759 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00111 auc=0.595 out_max=0.1796 (n=95) → 보정 재적용
  …
2026-09-02 15:40:09 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-02 15:40:09 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-02 15:40:09 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-02 15:40:09 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-02 15:40:09 [INFO] LEARNING: [Sigma] EOD sigma_20=0.05603% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 164 | 08:40:52 | 14:42:00 | 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |
| `Consolidator` | 1 | 15:40:09 | 15:40:09 | 구간 'OPEN_VOLATILE' 최근 4일 풀링(n=246) 기대손익 -0.351pt (CI상단 -0.001pt) < 0 → 패널티 +0.04 (참고 정확도 25.2%) |
| `DriftAdjuster` | 1 | 15:40:09 | 15:40:09 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 5일) |

**채널** — `LEARNING`×2862

**컴포넌트 상위 15** — `LEARNING`×1211, `SGD`×370, `sigma`×357, `Calibration`×323, `Bias⚠`×218, `Bias`×122, `MetaConf`×78, `OnlineLearner`×65, `ScalerWarmup`×47, `BiasReset`×19, `SHAP`×12, `GBM-64`×10, `GBM`×10, `RF`×6, `ExtremityCorrector`×5

### `logs/20260902_HEALTH.log` — 4.7KB · 34행 · 최종 14:56:01

- 형식 평문 · 시각 인식 34행 · WARNING=18, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2491ms | quality=0.86 | cache_age=46s | exceptions_10m=1
2026-09-02 09:01:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2157ms | quality=0.86 | cache_age=106s | exceptions_10m=1
2026-09-02 09:02:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=447ms | quality=0.74 | cache_age=164s | exceptions_10m=1
2026-09-02 09:22:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1163ms | quality=1.00 | cache_age=78s | exceptions_10m=0
2026-09-02 09:23:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=348ms | quality=1.00 | cache_age=137s | exceptions_10m=0
  …
2026-09-02 14:20:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=355ms | quality=1.00 | cache_age=104s | exceptions_10m=1
2026-09-02 14:28:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2977ms | quality=1.00 | cache_age=35s | exceptions_10m=1
2026-09-02 14:29:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=441ms | quality=1.00 | cache_age=92s | exceptions_10m=1
2026-09-02 14:55:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=680ms | quality=1.00 | cache_age=181s | exceptions_10m=2
2026-09-02 14:56:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=340ms | quality=1.00 | cache_age=58s | exceptions_10m=2
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 18 | 09:00:02 | 14:55:01 | level=WARNING degraded=OFF | latency=2491ms | quality=0.86 | cache_age=46s | exceptions_10m=1 |

**채널** — `HEALTH`×34

**컴포넌트 상위 15** — `Health`×33, `HealthTrend`×1

### `logs/retrain_eod_20260902.log` — 20.8KB · 142행 · 최종 15:48:54

- 형식 평문 · 시각 인식 142행 · WARNING=9, INFO=133

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 15:45:04,592 [INFO] EOD_RETRAIN: =======================================================
2026-09-02 15:45:04,593 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-02 15:45:04,593 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-02 15:45:04,593 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-02 15:45:04,594 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-02 15:48:54,288 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0370 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-02 15:48:54,289 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0907 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-02 15:48:54,291 [INFO] SIGNAL: [ScalerRefresh] ts=15:48 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-09-02 15:48:54,296 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-02 15:48:54,298 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:55 | 15:47:42 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-01 14:38:00 ≥ 홀드아웃 시작=2026-08-26 13:01:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-01 14:38 >= holdout_start=2026-08-26 13:01 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-01 … |
| `GuardGhost` | 2 | 15:46:07 | 15:46:07 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-02 13:56:00까지)인데 acc.txt=0.3776는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `Retrain` | 1 | 15:47:19 | 15:47:19 | 15m 교체 보류(EOD 모델가드) — acc 하락 0.0449 > 허용 0.0300 (new=0.3978 old=0.4427) — 참고용 저장, 구모델 유지 |

**채널** — `LEARNING`×65, `SIGNAL`×49, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×22, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `RegimeFingerprint`×3, `WaitDC`×2, `GuardGhost`×2, `P8`×2

### `logs/retrain_intraday_20260902_093600.log` — 2.7KB · 21행 · 최종 09:36:22

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_1ca1a6d7.json
2026-09-02 09:36:03,859 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-02 09:36:22,309 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-02 09:36:22,310 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-02 09:36:22,310 [INFO] LEARNING: [Retrain] 완료 | 18.5초 | 성공=1/1 호라이즌
2026-09-02 09:36:22,311 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.5s 데이터=4800행
2026-09-02 09:36:22,312 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_1ca1a6d7.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: WATCHLIST (Lv.1)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -5265803원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 3 |
| 진입 등록(`[Position] 진입`) — **엔진** | 3 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 3 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 4 |
| 차단(`[차단]`) | 74 |
| 사이저 호출(`[Sizer]`) | 13 |

### 포지션 3건 · 승 1 (33%) · 합계 +1.70pt (+33,864원)  ※ 레그 5행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:19:00 | 엔진 | LONG | 2 | 1m | 2 | +0.30 | -5,576 | 하드스톱(틱) |
| 10:49:00 | 엔진 | SHORT | 2 | 3m | 2 | +1.24 | +41,590 | 하드스톱 |
| 13:34:01 | 엔진 | SHORT | 1 | 3m | 1 | +0.16 | -2,150 | 하드스톱(틱) |

**청산 레그 5행** (부분청산 4 · 전량청산 4)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:21:08 | 부분 | 1 | +0.33 | +6,212 | TP1 부분청산 33% |
| 10:21:18 | 전량 | 1 | -0.03 | -11,788 | 하드스톱(틱) |
| 10:50:16 | 부분 | 1 | +0.79 | +29,295 | TP1 부분청산 33% |
| 10:51:02 | 전량 | 1 | +0.45 | +12,295 | 하드스톱 |
| 13:35:34 | 전량 | 1 | +0.16 | -2,150 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱(틱)`×2, `하드스톱`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 3/3건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -5,265,804 = 포지션합 +33,864 → **불일치 ⚠** · `[청산 완료]` 4건 = 조립 포지션 3건 → **불일치 ⚠** · **귀속 실패 레그 3행 ⚠**(진입 로그 없는 이월 포지션 가능)

### CB③ 판정 가능 시간 — **65분 / 370분 (18%)**

acc30m 버퍼 리셋 2회 · 그때 버린 표본 60건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 3건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:19:00 | LONG | 2 | 1048.54 | 1m | mean-revert |
| 10:49:00 | SHORT | 2 | 1040.2 | 3m | mean-revert |
| 13:34:01 | SHORT | 1 | 1034.72 | 3m | mean-revert |

계약수 분포 — 1계약×1, 2계약×2

등급 분포 — `A급(원시C)`×2, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `risk`×3, `cvd`×1, `fore`×1, `prev`×1, `ofi`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×10, **3계약**×3

실제 진입 계약수 — **1계약**×1, **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×13

### 차단 사유 74건 · 28종

| 건수 | 사유 |
|---|---|
| 35 | 등급X — 미통과 항목: 2_confidence |
| 3 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 9_risk |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 9_risk |
| 2 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.86pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.3pt > ATR×5.0=10.1pt (시가=1040.10 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.0pt > ATR×5.0=11.0pt (시가=1040.10 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.1pt > ATR×5.0=10.2pt (시가=1040.10 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar, 9_risk |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.0pt > ATR×5.0=9.8pt (시가=1040.10 반등위험) |
| 1 | 청산 후 쿨다운 — 77초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 17초 후 재진입 가능 |
| 1 | JointGateBlock — meta=0.50 tox=0.70 joint=0.352 < 0.50 |
| 1 | 청산 후 쿨다운 — 1초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×35, `3_vwap`×5, `9_risk`×5, `5_ofi`×3, `4_cvd`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 4건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×2
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 28건 · 최대 56875ms · 5초 초과 7건

상위 — 56875ms, 10953ms, 7375ms, 6875ms, 5562ms, 5047ms, 5031ms, 4953ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:10 | 10953ms | 2491ms | **8462ms (77%)** |
| 09:01:05 | 5562ms | 2491ms | **3071ms (55%)** |
| 11:26:07 | 7375ms | 713ms | **6662ms (90%)** |
| 11:27:04 | 5047ms | 713ms | **4334ms (86%)** |
| 11:28:57 | 56875ms | 573ms | **56302ms (99%)** |
| 11:33:05 | 5031ms | 339ms | **4692ms (93%)** |
| 14:12:06 | 6875ms | 402ms | **6473ms (94%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260902_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:12 2026-09-02 15:40:12 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 23분 < 하한 25분 — 최근 5거래일 평균 14분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 6분 · 도달불가 171분 · 재지않음 193분
--- ConstOut ×5(표본)
09:35:00 2026-09-02 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:59:00 2026-09-02 11:59:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
13:02:00 2026-09-02 13:02:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
13:42:00 2026-09-02 13:42:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×5(표본)
09:00:10 2026-09-02 09:00:10 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260902.log
11:26:07 2026-09-02 11:26:07 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260902.log
11:28:57 2026-09-02 11:28:57 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260902.log
11:33:05 2026-09-02 11:33:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260902.log
--- [CB] ×2(표본)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:21:18 2026-09-02 10:21:18 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10)
10:21:18 2026-09-02 10:21:18 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:24:18)
10:21:18 2026-09-02 10:21:18 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:24:18)
--- [SHAP] 슬로우 ×7(표본)
13:20:01 2026-09-02 13:20:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 914ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
14:08:01 2026-09-02 14:08:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 904ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
14:16:01 2026-09-02 14:16:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 975ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
14:30:02 2026-09-02 14:30:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 953ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-02 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3250 band=INFO since_pipe_s=NA
09:00:10 2026-09-02 09:00:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 10953ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=10953 band=WARN since_pipe_s=0.2
09:01:05 2026-09-02 09:01:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5562ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5562 band=WARN since_pipe_s=0.1
09:01:36 2026-09-02 09:01:36 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2640ms — 메인 스레드 블로킹 발생 | pipe_elapsed=30 watchdog_alerted=[] | [MainStall] stall_ms=2640 band=INFO since_pipe_s=31.4
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260902_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-02 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-09-02 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-09-02 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=90ms fit=39ms total=150ms
09:36:00 2026-09-02 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:09 2026-09-02 15:40:09 [INFO] SYSTEM: [CB③계측] 조건성립 2분 / 판정가능 65분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-02 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-09-02 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:11:00 2026-09-02 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:17:00 2026-09-02 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:09 2026-09-02 15:40:09 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:09 2026-09-02 15:40:09 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:08 2026-09-02 15:11:08 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:13 2026-09-02 15:40:13 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:28 2026-09-02 15:40:28 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:13 2026-09-02 15:40:13 [INFO] SYSTEM: [Notify] ℹ️ [15:40:13] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:13 2026-09-02 15:40:13 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:28 2026-09-02 15:40:28 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260902_SIGNAL.log`
```
--- ConfFloorGuard ×3(표본)
09:00:01 2026-09-02 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:49:00 2026-09-02 10:49:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3807 ≥ 필요 0.3720
10:55:00 2026-09-02 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3715 < 필요 0.3720 (conf_floor=0.330, min_conf=0.372, span=0.0135). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-09-02 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-02 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-02 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:02 2026-09-02 09:37:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-02 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-02 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-02 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-02 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.2% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
--- 안전망 ×8(표본)
09:07:00 2026-09-02 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-02 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-02 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-02 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260902_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00008 auc=0.274 out_max=0.0875 (기준 auc<0.53 and span<0.020, 기저율=0.0875 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00217 auc=0.298 out_max=0.2759 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-02 08:40:52 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00111 auc=0.595 out_max=0.1796 (n=95) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260902_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:09 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 … |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:52:19 [INFO] 설정 업데이트 완료 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:09 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260902_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 33 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 22 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 24 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 12:00 | 장중 중간점 | 12 | 11:54:00 [WARNING] 5분 누적 수익률 -0.240% (임계 ±0.166%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 14:00 | 장중 후반 · 장중 재학습 | 1 | 14:04:00 [WARNING] 5분 누적 수익률 -0.198% (임계 ±0.136%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 5 | 15:40:09 [WARNING] gross 불일치 — broker -5,498,000원[TR수신 2026-09-02 13:35:36] vs engine -5,183,000원 (차 -315,000원). 체결 누락 또는 브로커 미정… |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260902_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:33 [INFO] 로테이션 — 8.9MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 130 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 187 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 199 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 184 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 174 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 150 | 15:04:00 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 130 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 44 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260902_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:09 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0327) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 124 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0456) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0446) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 116 | 09:55:01 [WARNING] 신뢰도 미달 31.7% < 38.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 229 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=24m max_z=+4.88(cancel_add_ratio) extreme=1 |
| 14:00 | 장중 후반 · 장중 재학습 | 209 | 13:55:00 [WARNING] 신뢰도 미달 31.5% < 36.8% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 39 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:09 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260901 | 15:40 | 로그 본문 |
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| 20260827 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260902** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 원인 — 둘 다 미확정, 원인 규명에 DB 조회 필요
### 결정 — 코드를 바꾸지 않는다(장중 세션 규약), 관측만 등록
### Why
### How to apply
### 계측 4원칙 적용
### 최근 2주 메인 스레드 정지 최대치 대조 (계측 델타)
### 라이브 미검증 / 이월
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
증

이 세션은 로그·설정·git만 읽었다(DB 조회 없음 — 규약 준수). 테스트 실행 없음(코드
변경 없음).

전문: `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` 장전(pre) 절.

---

## 2026-09-02 (MW0601 516차 — 장중 점검: 메인 스레드 57초 정지·ConfFloorGuard 장기지속)

**계기**: 예약 장중 점검(12:26 KST, 09:00~12:27 구간 커버). 장전 절(515차)의 이상점
1-1~1-4, 관측 O-p1~O-p4를 전부 이월 처리표로 처분한 뒤 장중 자체 관측 2건을 신규 등록.

### 증상

1. **메인 스레드 56,875ms(57초) 완전 정지** — `2026-09-02 11:28:57 [ERROR] SYSTEM:
   [LiveDBG] _tick_header 간격 56875ms — 메인 스레드 블로킹 발생 | band=ALERT`.
   스택 스냅샷(`logs/mainstall_traceback_20260902.log:84`)에서 메인 스레드가
   `collection/cybos/api_connector.py:1595 _pump_messages`(Cybos COM 메시지 펌프) 안에
   머물러 있었다 — Python 레벨 무한루프가 아니라 COM API 대기로 추정.
2. **`ConfFloorGuard` 장기 지속** — `09:00:01` 최초 발동(보정기 출력상한 0.3479 <
   필요 0.4240) → `10:49:00` 잠깐 복구(6분) → `10:55:00` 재발동 → 수집 시점(12:26)까지
   복구 로그 없음. 09-01 이전 리포트가 특성화한 "개장 첫 분 워밍업, 이후 복귀. 상시
   아님" 패턴과 지속시간이 명백히 다르다.

### 원인 — 둘 다 미확정, 원인 규명에 DB 조회 필요

1(메인 스레드 정지)은 COM API 레벨 블로킹으로 추정되나 Python 스택만으로는 근본 원인
특정 불가. 2(ConfFloorGuard)는 오늘 레짐이 `regime=NEUTRAL` 207/207(100%), 평균
신호 확신도 40.6%(n=501), 체크리스트 차단 44건 중 28건(63.6%)이 `2_confidence` 단일
사유 — 시장 자체의 저신호 국면일 가능성이 높으나, 보정기(Calibration) 쪽 결함 가능성도
배제 못 한다. **08:45 이후 정규장 중 라이브 DB 분석 금지(CLAUDE.md) 구간이라 이 세션에서는
`predictions` 테이블로 보정기 출력 분포를 확인할 수 없었다.**

### 결정 — 코드를 바꾸지 않는다(장중 세션 규약), 관측만 등록

신규 Fix 없음. G-2(메인 스레드 정지 실시간 경보)를 고도화 방안으로 등록했으나 표본
1건뿐이라 임계값 결정은 26주 WFA 주기로 미룬다.

### Why

- 장중 예약은 라이브 프로세스가 돌고 있는 중간에 실행되므로 코드 변경·재기동 금지
  (CLAUDE.md 스케줄 지시문).
- DB 조회 시점 제약(장중 라이브 DB 분석 금지, CLAUDE.md 절대원칙 인접 규약) 때문에
  ConfFloorGuard 원인 규명은 장후로 이월.

### How to apply

- O-i1: 장후 세션에서 `predictions` 테이블 보정기 출력 분포를 오늘 vs 최근 5거래일로
  비교해 원인(시장 vs 보정기) 판정.
- O-i2: 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`) 누적치에 오늘 56,875ms를 새 데이터
  포인트로 반영, 26주 WFA 주기에서 재검토.

### 계측 4원칙 적용

- ④ **폴백 가시화**(확장 적용) — 두 이상점 모두 "원인 불명"을 확정된 것처럼 쓰지 않고
  "미확정, 무엇을 더 보면 판정되는지" 명시(313차 원칙과 결합).

### 최근 2주 메인 스레드 정지 최대치 대조 (계측 델타)

| 일자 | 최대(ms) |
|---|---|
| 08-20 | 4,750 |
| 08-21 | 9,922 |
| 08-24 | 20,985(종전 최대) |
| 08-25 | 8,625 |
| 08-26 | 8,141 |
| 08-27 | 12,500 |
| 08-31 | 7,718 |
| 09-01 | 6,250 |
| **09-02** | **56,875(신규 최대, 종전 대비 2.7배)** |

### 라이브 미검증 / 이월

- O-i1(ConfFloorGuard 원인): 장후 DB 조회 필요.
- O-i2(메인 스레드 정지 재발): 다음 거래일 이후 누적 관찰.
- O-p2(1-1 발생원): 장전부터 이월, 여전히 미확정 — 장후 필수.
- O-p4(사용자 정리 시도 여부): 사용자 응답 대기, 여전히 미확정.

### 검증

이 세션은 로그·설정·git만 읽었다(DB 조회 없음 — 규약 준수, 08:45 이후 라이브 DB
분석 금지 구간이라 애초에 시도하지 않았다). 테스트 실행 없음(코드 변경 없음).

전문: `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` 장중(intra) 절.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 위 09-01 항목 처리 — 완료(자동, 손실 확정)
### 신규 — P0 후속
### 판정 완료 (09-01 이월 항목)
### 사용자 몫 (자동조치 범위 밖 — 손 작업, 오늘 리포트 "사용자 조치" 절과 동일)
## 2026-09-02 (MW0601 516차 — 장중 점검 결과)
### 위 장전 항목 처리 — 이월 처분 완료
### 신규 — 장중 관측 2건
### 재이월 (장전부터 미확정 지속)
```

미완료 체크박스 **2292건** (끝에서 30건)
```
- [ ] **O-p3** — 511차 Fix(F-19·F-21·F-22·G-6) 재기동 후 라이브 동작 확인.
- [ ] **O-p4** — 오늘 밤새 보유된 LONG 3계약(또는 사용자 수동 정리 결과)의 내일
- [ ] **O-p5** — O-i4(외부 진입 발생원) 사용자 답변 반영.
- [ ] O-i5(이월) — `[BalanceUI]` 키 매핑, `dashboard/main_dashboard.py` 확인 필요.
- [ ] O-t4(지속) — 15m EOD 교체 보류 반복, 실거래 영향 없음 계속 확인.
- [ ] **지금 즉시 — 대신증권 계좌에 LONG 3계약(평균 1076.00)이 남아있는지 확인,
- [ ] **오늘 정체불명 매매 38건(-163만원)이 사용자 본인 것인지 확인** — O-i4/O-p5.
- [ ] **O-514a F-A 발화 확인** — 정상 마감일에 `[DailyCloseResidual] 마감 진입 시
- [ ] **O-514b F-B 발화 확인** — `logs/force_flat_guard_<date>.log` 에 판정이
- [ ] **O-514c F-C 발화 확인** — 외부 진입이 다시 들어오면 경보 탭에
- [ ] **P0-2 `daily_close()` 자동 청산 통합** — 🔴 주간회의 안건. 주문·청산 실행
- [ ] **P2-2 `TRAIL_AFTER_TP1` 라벨 수정** — 🔴 **전제 정정**: 섀도 대사는 이미
- [ ] **CB② 복원 재검토** — 기한 2026-08-29 경과, 계속 미결. 이번 주 중.
- [ ] **주간회의 안건 6건** — 승률 정의 축 · F-15/F-16 외부진입 손익 통합 ·
- [ ] **🔴 대신증권 계좌 LONG 3계약(평균 1076.00) 확인·정리** — 리포트 사용자 조치 1.
- [ ] **정체불명 매매 38건(-163만원) 본인 여부 확인** — O-i4/O-p5.
- [ ] **재기동** — 511차·513차·514차 코드는 재기동 전까지 적용되지 않는다.
- [ ] **전체 테스트 실행 시 `--ignore` 목록 갱신** — `tests/test_511_exit_order_reject.py`
- [ ] **F-1 = P0-2 승인 촉구** — `daily_close()` 진입 전 잔여 포지션 강제청산 통합.
- [ ] **F-2 코드 확인** — `entry_horizon` 미전달이 엔진 진입 경로뿐 아니라 브로커
- [ ] **O-p2** — 오늘 손실 포지션(09-01 15:34:46 진입)의 `grade`·발생원을
- [ ] **이상점 1-4** — 증거 다이제스트 정합성 불일치(귀속 실패 레그) 규모가 -54,538원
- [ ] **어제 저녁 "즉시 매도" 요청을 실행하려 했는지, 왜 반영되지 않았는지 확인**
- [ ] **정체불명 매매 38건(-163만원) + 오늘 손실 포지션 본인 여부 확인** (O-i4)
- [ ] **대신증권 계좌 상태 재확인** — 시스템상 현재 FLAT(포지션 없음)이나 08-31 전례상
- [ ] **O-i1** — `ConfFloorGuard` 장기지속(1-6)의 원인 규명. `predictions` 테이블
- [ ] **O-i2** — 메인 스레드 56,875ms(57초) 정지(1-5) 재발 여부·규모 추이 관찰.
- [ ] **G-2** — 메인 스레드 정지 실시간 경보(고도화 방안, 표본 1건이라 임계값은
- [ ] **O-p2** — 1-1 손실 포지션(09-01 15:34:46 진입)의 발생원·`grade`. 장중에도
- [ ] **O-p4** — 사용자가 09-01 저녁 지시대로 포지션을 정리하려 시도했는지. 응답
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
균 1076.00) 확인·정리** — ✅ **자동 처리됨(사용자
      조치 아님)**: 09-02 08:45 하드스톱으로 시스템이 자동 청산했다. 결과는 손실
      -5,299,668원(자본대비 -10.60%). "정리됨"이지 "문제없이 정리됨"이 아니다 —
      사용자가 그 사이 직접 정리를 시도했는지는 미확인(아래 신규 항목).

### 신규 — P0 후속

- [ ] **F-1 = P0-2 승인 촉구** — `daily_close()` 진입 전 잔여 포지션 강제청산 통합.
      09-01부터 계획은 있으나 자동조치 C등급이라 미승인. 오늘 사고(-530만원 실현손실)를
      근거로 주간회의 우선순위 상향 권고.
- [ ] **F-2 코드 확인** — `entry_horizon` 미전달이 엔진 진입 경로뿐 아니라 브로커
      동기화(이월 포지션 인식) 경로에서도 재현됨(오늘 08:41:09 PositionFallback).
      `grep -n "PositionFallback" main.py`로 호출 지점 확인 후 F-5 범위 확장 필요
      여부 판단 — 장후 이월.
- [ ] **O-p2** — 오늘 손실 포지션(09-01 15:34:46 진입)의 `grade`·발생원을
      `trades`/`ensemble_decisions`에서 조회(O-i4 연장). 08:45 이후 라이브 DB 분석
      금지 구간이라 장전엔 불가 — **장후 필수 확인**.
- [ ] **이상점 1-4** — 증거 다이제스트 정합성 불일치(귀속 실패 레그) 규모가 -54,538원
      (09-01)에서 -5,299,668원(09-02, 전액)으로 확대 재현. DB 3원 대사로 보완 가능한지
      장후에 확인.

### 판정 완료 (09-01 이월 항목)

- [x] **O-p3** — 511차 Fix(F-19·F-21·F-22·G-6) 재기동 후 라이브 동작 확인 → **정상**.
      오늘 08:45:09~11 청산 주문 3계약 전량 거부 없이 체결(09-01 163건 거부와 대조).
      단 "외부 미체결 주문과의 청산가능수량 경합" 조건은 오늘 재현되지 않아 그 조건은
      미검증으로 남는다.

### 사용자 몫 (자동조치 범위 밖 — 손 작업, 오늘 리포트 "사용자 조치" 절과 동일)

- [ ] **어제 저녁 "즉시 매도" 요청을 실행하려 했는지, 왜 반영되지 않았는지 확인**
- [ ] **정체불명 매매 38건(-163만원) + 오늘 손실 포지션 본인 여부 확인** (O-i4)
- [ ] **대신증권 계좌 상태 재확인** — 시스템상 현재 FLAT(포지션 없음)이나 08-31 전례상
      시스템·실계좌 불일치 가능성을 배제하지 않음

## 2026-09-02 (MW0601 516차 — 장중 점검 결과)

> 상세: `DECISION_LOG.md` 2026-09-02(516차). 리포트
> `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` 장중(intra) 절.

### 위 장전 항목 처리 — 이월 처분 완료

- [x] **O-p1** — `ConfFloorGuard` 축퇴 해소 여부 → **판정 완료**: 과거 "개장 첫 분
      한정" 패턴과 다르게 09:00~10:49·10:55~12:26 두 구간, 총 3시간 넘게 자동진입
      하한 미달 지속. 원인(시장 저신호 vs 보정기 결함)은 미확정 — O-i1로 이관.
- [x] **1-2 재확인** — 오늘 정상 엔진 진입 2건(10:19·10:49)은 `entry_horizon`이
      정확히 찍혔다 — PositionFallback 결함은 **브로커 동기화 경로 한정**으로 범위가
      좁혀졌다. F-2 구현 시 이 범위로 한정할 것.

### 신규 — 장중 관측 2건

- [ ] **O-i1** — `ConfFloorGuard` 장기지속(1-6)의 원인 규명. `predictions` 테이블
      보정기 출력 분포를 오늘 vs 최근 5거래일로 비교(장후 DB 조회 가능 시점에 필수).
- [ ] **O-i2** — 메인 스레드 56,875ms(57초) 정지(1-5) 재발 여부·규모 추이 관찰.
      최근 2주 최대치 2.7배 경신(종전 20,985ms, 08-24). 482차 F-3 섀도 계측
      (`MAIN_THREAD_STALL_*`)에 새 데이터 포인트로 반영, 26주 WFA 주기 재검토 대상.
- [ ] **G-2** — 메인 스레드 정지 실시간 경보(고도화 방안, 표본 1건이라 임계값은
      26주 WFA 주기 검토로 보류).

### 재이월 (장전부터 미확정 지속)

- [ ] **O-p2** — 1-1 손실 포지션(09-01 15:34:46 진입)의 발생원·`grade`. 장중에도
      라이브 DB 분석 금지 구간이라 확인 불가 — **장후 필수**.
- [ ] **O-p4** — 사용자가 09-01 저녁 지시대로 포지션을 정리하려 시도했는지. 응답
      대기 중.

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

### `data/heartbeat_MW0601_20260902.json` — 243B · 09-02 15:40:22
```json
{
 "pid": 2768,
 "written_at": "2026-09-02T15:40:22",
 "beat_epoch": 1788331219.1694076,
 "beat_age_sec": 3.1,
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

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 93개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` | 40.6KB | 09-02 12:33 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_intra.md` | 66.8KB | 09-02 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_pre.md` | 58.1KB | 09-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-01 18:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_post.md` | 89.7KB | 09-01 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_intra.md` | 68.8KB | 09-01 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_pre.md` | 49.8KB | 09-01 09:01 |
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 203.4KB | 08-31 18:13 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260828.md` | 4.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260828.md` | 28.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260828.json` | 35.2KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260828.md` | 178.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260828.json` | 97.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260902_WARN.log`: ERROR 이상 3건
2. `logs/20260902_WARN.log`: **Traceback** 출현 5건 — 크래시/메모리 계열
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. 포지션 3건 중 최종청산이 하드스톱·손절 계열 **3건(100%)** — 손절 준수율 확인 필요 (레그 5행)
5. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
6. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
7. 메인 스레드 정지 5초 초과 **7건** (최대 56875ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
8. `logs/20260902_WARN.log`: **ConstOut** 5건(표본)
9. `logs/20260902_SYSTEM.log`: **ConstOut** 8건(표본)
10. `logs/20260902_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20260902_SIGNAL.log`: **ConstOut** 8건(표본)
12. `logs/20260902_LEARNING.log`: **축퇴** 8건(표본)
13. 미커밋 변경 519건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
14. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260902*.log` (Windows) / `grep 강제청산 logs/*20260902*.log`*