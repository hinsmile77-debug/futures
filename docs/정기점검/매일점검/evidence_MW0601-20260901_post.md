# 미륵이 증거 다이제스트 — 2026-09-01 / POST

- 생성 2026-09-01 16:17:30 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/loving-blissful-cannon/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260901` · `2026-09-01` · `260901` · `0901`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **31개** 파일 · 31개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260901.txt` | 28B | 09-01 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260901.txt` | 28B | 09-01 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260901.txt` | 209B | 09-01 15:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260901.log` | 445B | 09-01 15:12 |
| `freeze_sentinel_alert_{DATE}.txt` | 1 | `data/freeze_sentinel_alert_20260901.txt` | 636B | 09-01 15:45 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260901.log` | 21.9KB | 09-01 16:17 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260901.json` | 243B | 09-01 15:40 |
| `launcher_{DATE}_084002_20299.log` | 1 | `logs/Mireuk_batch/launcher_20260901_084002_20299.log` | 2.3MB | 09-01 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260901.log` | 5.7KB | 09-01 12:52 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260901.log` | 19.8KB | 09-01 15:48 |
| `retrain_intraday_20260716_10{DATE}.log` | 1 | `logs/retrain_intraday_20260716_100901.log` | 4.5KB | 07-16 10:09 |
| `retrain_intraday_20260807_{DATE}03.log` | 1 | `logs/retrain_intraday_20260807_090103.log` | 4.5KB | 08-07 09:01 |
| `retrain_intraday_{DATE}_092700.log` | 1 | `logs/retrain_intraday_20260901_092700.log` | 2.7KB | 09-01 09:27 |
| `retrain_intraday_{DATE}_102000.log` | 1 | `logs/retrain_intraday_20260901_102000.log` | 2.7KB | 09-01 10:20 |
| `retrain_intraday_{DATE}_111200.log` | 1 | `logs/retrain_intraday_20260901_111200.log` | 2.7KB | 09-01 11:12 |
| `retrain_intraday_{DATE}_124800.log` | 1 | `logs/retrain_intraday_20260901_124800.log` | 2.7KB | 09-01 12:48 |
| `retrain_intraday_{DATE}_134500.log` | 1 | `logs/retrain_intraday_20260901_134500.log` | 2.7KB | 09-01 13:45 |
| `retrain_intraday_{DATE}_142700.log` | 1 | `logs/retrain_intraday_20260901_142700.log` | 2.7KB | 09-01 14:27 |
| `retrain_intraday_{DATE}_150600.log` | 1 | `logs/retrain_intraday_20260901_150600.log` | 2.7KB | 09-01 15:06 |
| `strategy_report_{DATE}_154011.txt` | 1 | `data/daily_reports/strategy_report_20260901_154011.txt` | 2.1KB | 09-01 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260901_DATA.log` | 343.2KB | 09-01 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260901_DEBUG.log` | 239.6KB | 09-01 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260901_HEALTH.log` | 18.2KB | 09-01 15:09 |
| `{DATE}_HOGA.log` | 1 | `logs/20260901_HOGA.log` | 46.3MB | 09-01 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260901_LEARNING.log` | 288.8KB | 09-01 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260901_MICRO.log` | 938.3KB | 09-01 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260901_PROBE.log` | 96.5KB | 09-01 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260901_SIGNAL.log` | 546.9KB | 09-01 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260901_SYSTEM.log` | 1.1MB | 09-01 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260901_TRADE.log` | 77.3KB | 09-01 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260901_WARN.log` | 496.2KB | 09-01 15:40 |

## 2. 코드·커밋 상태

- HEAD `3f5781c` · 브랜치 `v9-dev` · 미커밋 516건 · 실질 변경 4건 · 코드(.py) 2건 · EOL 파생 511건 (추적변경 515 · 미추적 1 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `main.py`, `scripts/freeze_sentinel.py`
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
… 외 476건
```

**당일(2026-09-01) 커밋**
```
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
```

**최근 커밋 12건**
```
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
6dfe6d7 [MW0601] 504차: 8월 손실일 딥다이브 + 손익추이2(CREON 반사실)·거래 출처 필터
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

_본문 미열람(설정): `20260901_HOGA.log` 46.3MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260901.txt`** — 28B · 09-01 15:40:11
```
2026-09-01T15:40:11.175463
```

**`data/daily_close_started_20260901.txt`** — 28B · 09-01 15:40:07
```
2026-09-01T15:40:07.415731
```

**`data/daily_reports/strategy_report_20260901_154011.txt`** — 2.1KB · 09-01 15:40:11
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-01 15:40
========================================================
  버전    : v1.0  (70일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-3.14  MDD(자본대비)=16.0%
  당일      : WR=46.7%  PF=0.32
  롤링20일: 누적 -6040411원  Sh=-3.14  MDD(자본대비)=16.0%  MDD(peak대비)=407.3%
  당일손익 : broker(gross) -1,144,000원  수수료 472,733원  net -1,616,733원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.42)
  PSI     : 0.003 (CLEAR)
  PSI/feat: cvd_delta=0.003  ofi_pressure=0.002  vwap_position=0.066
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -247,566원  승률 70.0%  합계 -4,951,315원
  등급별 순EV(30일): A=+5,637원(135건,승67%)  BROKER=-5,461,928원(1건,승0%)  C=-1,490원(33건,승73%)  MANUAL=-18,904원(91건,승45%)
  호라이즌별 순EV(30일): 1m=+14,421원(23건)  3m=-7,677원(118건)  5m=+44,423원(24건)  ?=-73,287원(95건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 9분  5일평균 15분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 21.5pt(5일평균 35.5pt)  1분평균변동 0.73pt(5일평균 0.93pt)
--------------------------------------------------------
  진입 퍼널(2026-09-01, 총 370분):
    FLAT 254 → conf미달 98 → CoherenceGate 9 → 게이트차단 7 → 후보 2 → 진입 2
    게이트별: 쿨다운=3  ATR변동성=2  포지션보유중(평가생략)=2
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260901.txt`** — 209B · 09-01 15:48:50
```
completed: 2026-09-01 15:48:50
rows: 40731
cols: 97
horizons_replaced: 5/6
t_load_s: 42.8
t_retrain_s: 181.9
t_total_s: 225.2
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/freeze_sentinel_alert_20260901.txt`** — 636B · 09-01 15:45:28
```
[FreezeSentinel] 2026-09-01 15:45:28 CRITICAL
  라이브 프로세스 동결 — 측정 가능한 신호 3종이 전부 300s 이상 정체다. 프로세스는 살아 있을 수 있으나 아무 일도 하지 않는다 (런처 재기동도 걸리지 않는다)
  · heartbeat        309s 전 (임계 300s) — 정체
  · crash_fault[TS]  309s 전 (임계 300s) — 정체
  · SYSTEM.log       302s 전 (임계 300s) — 정체
  · _exit_normally   **미측정**(플래그 없음/읽기 실패) — 동결 판정 유지
  · daily_close_done 317s 전 — 정체 신호(302s)보다 **먼저**다(마감 뒤 정지가 아니다)
```

_다이제스트 대상 8/24개 (중요도순). 제외: `retrain_intraday_20260807_090103.log`, `retrain_intraday_20260901_092700.log`, `retrain_intraday_20260901_111200.log`, `retrain_intraday_20260901_124800.log`, `retrain_intraday_20260901_142700.log`, `retrain_intraday_20260901_150600.log`, `retrain_intraday_20260901_102000.log`, `retrain_intraday_20260901_134500.log`_

### `logs/20260901_TRADE.log` — 77.3KB · 598행 · 최종 15:40:08

- 형식 평문 · 시각 인식 598행 · WARNING=40, INFO=558

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-01 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-01 09:09:02 [INFO] TRADE: [Chejan] 상태=접수 주문번호=462 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-01 09:09:04 [INFO] TRADE: [Chejan] 상태=체결 주문번호=462 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-01 09:09:04 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1063.54 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
  …
2026-09-01 15:34:46 [INFO] TRADE: [체결동기화] 외부진입 LONG 1계약 @ 1076.0 | 평균=1076.0 보유=1계약
2026-09-01 15:34:46 [INFO] TRADE: [Chejan] 상태=체결 주문번호=5062 code=A0569 방향=LONG 체결=2 미체결=0
2026-09-01 15:34:46 [INFO] TRADE: [Position] 체결진입 LONG 2계약 @ 1076.0 | 평균=1076.00 보유=3계약
2026-09-01 15:34:46 [INFO] TRADE: [체결동기화] 외부진입 LONG 2계약 @ 1076.0 | 평균=1076.0 보유=3계약
2026-09-01 15:40:08 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 40 | 09:09:04 | 15:34:46 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1063.54 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×598

**컴포넌트 상위 15** — `TickStop-S0C`×173, `Chejan`×157, `Position`×102, `체결동기화`×43, `PositionFallback`×40, `청산 완료`×30, `주문요청`×17, `체결청산-부분`×13, `TickTP1`×11, `Sizer`×5, `ProfitGuard`×2, `진입체크`×2, `체결진입`×2, `TP1 부분청산`×1

### `logs/20260901_WARN.log` — 496.2KB · 2292행 · 최종 15:40:10

- 형식 평문 · 시각 인식 2285행 · CRITICAL=76, ERROR=329, WARNING=1880, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-01 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-09-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
2026-09-01 08:41:14 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3500ms — live 중단 원인 분석용
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -1616733원
════════════════════════════════════════════════════
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `CybosOrder` | 163 | 13:28:09 | 13:30:33 | 주문 실패 ret=0 status=-1 msg=94025모의투자 주문가능금액이 부족합니다.                                             (ordfs.cstdvtvord) account=333044256 code=A0569 side=매도 qty=2 |
| ERROR | `Exit` | 163 | 13:28:09 | 13:30:33 | 하드스톱(틱) 주문 실패 ret=-1 |
| CRITICAL | `Health` | 76 | 09:23:01 | 14:22:00 | level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13 |
| ERROR | `BrokerDirectExit` | 2 | 15:24:37 | 15:33:07 | 15:10 스케줄러 안전망 — broker LONG 3계약 → SELL 직접주문 |
| ERROR | `SchedForceExit` | 1 | 15:24:37 | 15:24:37 | 15:10 경과에도 미청산 — 피드 독립 안전망 발동 (시도 1회, status=LONG engine=3ct broker_cached=0ct price_hint=1075.48) |

<details><summary>ERROR/CybosOrder 원문 2건</summary>

```
2026-09-01 13:28:09 [ERROR] SYSTEM: [CybosOrder] 주문 실패 ret=0 status=-1 msg=94025모의투자 주문가능금액이 부족합니다.                                             (ordfs.cstdvtvord) account=333044256 code=A0569 side=매도 qty=2
2026-09-01 13:28:09 [ERROR] SYSTEM: [CybosOrder] 주문 실패 ret=0 status=-1 msg=94025모의투자 주문가능금액이 부족합니다.                                             (ordfs.cstdvtvord) account=333044256 code=A0569 side=매도 qty=2
```

</details>

<details><summary>ERROR/Exit 원문 2건</summary>

```
2026-09-01 13:28:09 [ERROR] SYSTEM: [Exit] 하드스톱(틱) 주문 실패 ret=-1
2026-09-01 13:28:09 [ERROR] SYSTEM: [Exit] 하드스톱(틱) 주문 실패 ret=-1
```

</details>

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
```

</details>

<details><summary>ERROR/BrokerDirectExit 원문 2건</summary>

```
2026-09-01 15:24:37 [ERROR] SYSTEM: [BrokerDirectExit] 15:10 스케줄러 안전망 — broker LONG 3계약 → SELL 직접주문
2026-09-01 15:33:07 [ERROR] SYSTEM: [BrokerDirectExit] 15:10 스케줄러 안전망 — broker LONG 3계약 → SELL 직접주문
```

</details>

**WARNING — 태그 38종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 429 | 08:41:07 | 15:35:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PendingOrder` | 360 | 09:10:49 | 14:55:28 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 1059.68, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `ExitSendOrderResult` | 175 | 09:10:49 | 14:55:28 | ret=0 kind=하드스톱(틱) direction=LONG qty=1 |
| `TickStop` | 174 | 09:10:49 | 14:55:28 | 스톱 히트 감지 (틱) LONG tick=1059.64 stop=1059.68 → 즉시 처리 예약 |
| `ChejanFlow` | 157 | 09:09:02 | 15:34:46 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1063.54 | fill_qty=1 | gubun='0' | order_no='462' | pending='NONE' | position='FLAT' | position_qty=0 | sell_balance=0 | side='LONG' | … |
| `ChejanMatch` | 157 | 09:09:03 | 15:34:46 | order_no='462' | pending='NONE' | pending_matched=False |
| `OrderSync` | 136 | 09:09:04 | 15:34:46 | 미추적 체결 감지 (pending_miss) order_no=462 side=LONG qty=1 price=1063.54 before=FLAT |
| `ExitCooldown` | 60 | 09:10:49 | 15:33:22 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:13:49) |
| `Health` | 42 | 09:00:01 | 15:09:00 | level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |
| `SHAP` | 21 | 11:40:01 | 15:06:01 | 슬로우 감지 912ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `CB` | 18 | 09:10:49 | 15:33:08 | 연속 손절 1회 (300초 창, 포지션 단위) |
| `ExitFillFlow` | 18 | 09:10:49 | 14:55:28 | after='FLAT' | before='LONG 1계약 @ 1063.54' | fill_price=1059.64 | fill_qty=1 | mode='final' | pending='EXIT_FULL:LONG qty=1 filled=1 order_no=504 reason=하드스톱(틱) req_at=09:10:49.779' | reason='하드스톱(틱)' |

**채널** — `SYSTEM`×2167, `HEALTH`×118

**컴포넌트 상위 15** — `LiveDBG`×429, `PendingOrder`×360, `ExitSendOrderResult`×175, `TickStop`×174, `CybosOrder`×163, `Exit`×163, `ChejanFlow`×157, `ChejanMatch`×157, `OrderSync`×136, `Health`×118, `ExitCooldown`×60, `SHAP`×21, `CB`×18, `ExitFillFlow`×18, `ScalerRefresh`×14

### `logs/20260901_SYSTEM.log` — 1.1MB · 6864행 · 최종 15:40:26

- 형식 평문 · 시각 인식 6843행 · INFO=6843, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=17924 | 행감지=30s all_threads=True
2026-09-01 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-01 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-01 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-01 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-31) 종가 버퍼 로드: 384봉
  …
2026-09-01 15:40:11 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-01 15:40:11 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-01 15:40:26 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-01 15:40:26 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-01 15:40:26 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×6843

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1074, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `CybosEvent`×314, `BalanceUI`×284, `CybosDailyPnl`×268, `BalanceRefresh`×190, `CybosDailyPnlHeaders`×134, `MicroRegime`×100, `System`×98

### `logs/20260901_SIGNAL.log` — 546.9KB · 4863행 · 최종 15:40:08

- 형식 평문 · 시각 인식 4863행 · WARNING=1959, INFO=2904

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.416
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
  …
2026-09-01 15:10:01 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-01 15:40:08 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-01 15:40:08 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 110분(29.7%) / DN 14분(3.8%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-01 15:40:08 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-01 age=28m extreme=452 refresh=37 grade_x=82 cb3=0
2026-09-01 15:40:08 [INFO] SIGNAL: [ModelHealth] date=2026-09-01 앙상블유효가동률=74.3% | 파이프라인 370분 | ConstOut 7회/13분 {"3m": {"events": 5, "minutes": 9}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 82분 | 장중재학습 7회 | CB③ ready 114분/370분 (31%) (리셋 4회, 표본손실 120건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1182 | 09:00:02 | 15:05:02 | 1m 'macro_sp500_chg' scale=0.0574 → floor=0.15 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 222 | 08:45:08 | 13:30:02 | 1m CORE 'ofi_norm' raw_std≈0(0.0205) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 184 | 09:00:00 | 14:55:01 | ts=08:59 horizon=1m age=1m max_z=-7.42(prev_day_same_hour_ret) extreme=1 |
| `Model` | 178 | 09:00:00 | 14:54:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 92 | 09:06:00 | 15:06:00 | 신뢰도 미달 34.3% < 38.6% → 강제 X등급 |
| `WeightCollapse` | 82 | 09:07:00 | 15:07:03 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 9 | 09:26:01 | 15:06:00 | 3m 상수 출력 5분 감지 (range=0.0040 dir=-1) → 앙상블 제외 |
| `MetaGate` | 7 | 09:30:00 | 09:43:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `ConfFloorGuard` | 3 | 09:00:01 | 11:20:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4863

**컴포넌트 상위 15** — `ScalerFloor`×1236, `SIGNAL`×740, `Ensemble`×377, `FQAdj`×367, `ZeroDiag`×361, `MetaGate`×349, `ScalerRefresh`×265, `Model`×226, `ScalerMonitor`×185, `ATR-Horizon`×106, `Checklist`×104, `MicroRegime`×100, `InstabilityGate`×89, `WeightCollapse`×82, `차단`×54

### `logs/20260901_LEARNING.log` — 288.8KB · 2812행 · 최종 15:40:08

- 형식 평문 · 시각 인식 2812행 · WARNING=167, INFO=2645

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.508 out_max=0.3054 (기준 auc<0.53 and span<0.020, 기저율=0.3053 n=95) → 보정 미적용, raw 통과
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.436 out_max=0.1126 (기준 auc<0.53 and span<0.020, 기저율=0.1125 n=80) → 보정 미적용, raw 통과
2026-09-01 08:40:51 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00058 auc=0.537 out_max=0.2913 (n=110) → 보정 재적용
  …
2026-09-01 15:40:08 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-01 15:40:08 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-01 15:40:08 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-01 15:40:08 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-01 15:40:08 [INFO] LEARNING: [Sigma] EOD sigma_20=0.06284% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 167 | 08:40:51 | 13:57:00 | 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×2812

**컴포넌트 상위 15** — `LEARNING`×1211, `SGD`×371, `sigma`×357, `Calibration`×328, `Bias⚠`×189, `Bias`×130, `MetaConf`×74, `ScalerWarmup`×43, `OnlineLearner`×35, `BiasReset`×14, `GBM-64`×14, `GBM`×14, `SHAP`×12, `RF`×8, `ExtremityCorrector`×5

### `logs/20260901_HEALTH.log` — 18.2KB · 130행 · 최종 15:09:00

- 형식 평문 · 시각 인식 130행 · CRITICAL=76, WARNING=42, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0
2026-09-01 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=744ms | quality=0.86 | cache_age=98s | exceptions_10m=0
2026-09-01 09:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=266ms | quality=1.00 | cache_age=184s | exceptions_10m=4
2026-09-01 09:22:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=316ms | quality=1.00 | cache_age=57s | exceptions_10m=7
2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
  …
2026-09-01 14:29:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=333ms | quality=1.00 | cache_age=176s | exceptions_10m=5
2026-09-01 15:06:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=460ms | quality=1.00 | cache_age=184s | exceptions_10m=1 [GBM재학습중→lat임계 5000/10000ms]
2026-09-01 15:07:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2713ms | quality=1.00 | cache_age=63s | exceptions_10m=2
2026-09-01 15:08:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=366ms | quality=1.00 | cache_age=120s | exceptions_10m=2
2026-09-01 15:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=356ms | quality=1.00 | cache_age=180s | exceptions_10m=2
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 76 | 09:23:01 | 14:22:00 | level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 42 | 09:00:01 | 15:09:00 | level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |

**채널** — `HEALTH`×130

**컴포넌트 상위 15** — `Health`×129, `HealthTrend`×1

### `logs/retrain_eod_20260901.log` — 19.8KB · 132행 · 최종 15:48:50

- 형식 평문 · 시각 인식 132행 · WARNING=11, INFO=121

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 15:45:04,791 [INFO] EOD_RETRAIN: =======================================================
2026-09-01 15:45:04,791 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-01 15:45:04,791 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-01 15:45:04,791 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-01 15:45:04,791 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-01 15:48:50,523 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0377 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-01 15:48:50,523 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1215 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-01 15:48:50,528 [INFO] SIGNAL: [ScalerRefresh] ts=15:48 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-09-01 15:48:50,528 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-01 15:48:50,528 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:55 | 15:47:39 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1500봉(81%)이 현행 학습구간 (현행 cutoff=2026-08-31 14:38:00 ≥ 홀드아웃 시작=2026-08-25 12:58:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-31 14:38 >= holdout_start=2026-08-25 12:58 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-31 … |
| `GuardGhost` | 4 | 15:46:05 | 15:46:17 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-01 14:35:00까지)인데 acc.txt=0.3882는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `Retrain` | 1 | 15:47:17 | 15:47:17 | 15m 교체 보류(EOD 모델가드) — acc 하락 0.0304 > 허용 0.0300 (new=0.4123 old=0.4427) — 참고용 저장, 구모델 유지 |

**채널** — `LEARNING`×67, `SIGNAL`×37, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×30, `Retrain`×22, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `GuardGhost`×4, `RegimeFingerprint`×3, `WaitDC`×2, `P8`×2

### `logs/retrain_intraday_20260716_100901.log` — 4.5KB · 39행 · 최종 10:09:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,736 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
2026-07-16 10:09:04,490 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-16 10:09:36,601 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.43s | old_acc=0.2874)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 완료 | 32.1초 | 성공=6/6 호라이즌
2026-07-16 10:09:36,606 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.9s 데이터=20000행
2026-07-16 10:09:36,607 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
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
오늘 PnL: -1616733원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) — **엔진** | 2 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 45 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 43 |
| 청산(`체결청산`) | 30 |
| 차단(`[차단]`) | 54 |
| 사이저 호출(`[Sizer]`) | 5 |

### 포지션 27건 · 승 10 (37%) · 합계 -22.42pt (-1,562,196원)  ※ 레그 41행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:09:04 (추정귀속) | 외부 | LONG | 1 | — | 1 | -3.90 | -205,434 | 하드스톱(틱) |
| 09:20:27 (추정귀속) | 외부 | LONG | 2 | — | 1 | -4.56 | -248,854 | 미추적체결(pending_miss) |
| 09:22:03 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -11.28 | -595,230 | 하드스톱(틱) |
| 09:25:03 (추정귀속) | 외부 | LONG | 2 | — | 2 | +5.82 | +270,110 | TP2(전량) |
| 09:28:00 (추정귀속) | 외부 | LONG | 1 | — | 1 | +3.20 | +149,541 | 미추적체결(pending_miss) |
| 09:32:24 (추정귀속) | 외부 | LONG | 1 | — | 1 | -3.54 | -187,477 | 하드스톱(틱) |
| 09:33:32 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -7.56 | -398,890 | 하드스톱(틱) |
| 11:38:01 | 엔진 | SHORT | 1 | 3m | 1 | +0.42 | +10,560 | 하드스톱(틱) |
| 13:03:07 (추정귀속) | 외부 | LONG | 1 | — | 1 | -0.18 | -19,539 | 미추적체결(pending_miss) |
| 13:05:34 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.03 | -30,606 | 미추적체결(pending_miss) |
| 13:09:49 (추정귀속) | 외부 | LONG | 1 | — | 1 | -1.20 | -70,537 | 미추적체결(pending_miss) |
| 13:22:05 (추정귀속) | 외부 | LONG | 2 | — | 2 | -0.30 | -36,080 | 미추적체결(pending_miss) |
| 13:31:40 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -2.72 | -157,068 | 하드스톱(틱) |
| 13:41:14 (추정귀속) | 외부 | LONG | 3 | — | 3 | -0.15 | -38,592 | 미추적체결(pending_miss) |
| 13:49:50 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +1.54 | +66,433 | 미추적체결(pending_miss) |
| 13:51:44 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +0.52 | +15,454 | 미추적체결(pending_miss) |
| 13:54:17 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +2.68 | +123,456 | TP2(전량) |
| 13:59:23 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +0.36 | +7,485 | 하드스톱(틱) |
| 14:02:56 (추정귀속) | 외부 | SHORT | 1 | — | 1 | -0.62 | -41,512 | 미추적체결(pending_miss) |
| 14:08:17 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +1.80 | +79,480 | 미추적체결(pending_miss) |
| 14:11:53 (추정귀속) | 외부 | LONG | 1 | — | 1 | -0.64 | -42,502 | 미추적체결(pending_miss) |
| 14:16:45 (추정귀속) | 외부 | LONG | 1 | — | 1 | -1.18 | -69,496 | 하드스톱(틱) |
| 14:20:40 (추정귀속) | 외부 | SHORT | 1 | — | 1 | -1.28 | -74,488 | 하드스톱(틱) |
| 14:33:01 | 엔진 | LONG | 1 | 1m | 1 | +0.28 | +3,472 | 하드스톱(틱) |
| 14:48:01 (추정귀속) | 외부 | SHORT | 1 | — | 1 | +0.22 | +427 | 하드스톱(틱) |
| 15:24:07 (추정귀속) | 외부 | LONG | 3 | — | 3 | -0.28 | -45,653 | 미추적체결(pending_miss) |
| 15:33:03 (추정귀속) | 외부 | LONG | 3 | — | 3 | +0.10 | -26,656 | 미추적체결(pending_miss) |
| 15:34:46 (추정귀속) | 외부 | LONG | 3 | — | 0 | +0.00 | +0 | **미청산(보유 중)** |

**출처별 소계** — 엔진 2건 +14,032원 · 외부 25건 -1,576,228원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 26건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 41행** (부분청산 14 · 전량청산 30)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:10:49 | 전량 | 1 | -3.90 | -205,434 | 하드스톱(틱) |
| 09:21:43 | 전량 | 2 | -2.28 | -248,854 | 미추적체결(pending_miss) |
| 09:25:02 | 부분 | 1 | -3.76 | -198,410 | 하드스톱(틱) |
| 09:25:02 | 부분 | 1 | -3.76 | -198,410 | 하드스톱(틱) |
| 09:25:02 | 전량 | 1 | -3.76 | -198,410 | 하드스톱(틱) |
| 09:26:23 | 부분 | 1 | +2.33 | +106,055 | TP1 부분청산 33% |
| 09:27:00 | 전량 | 1 | +3.49 | +164,055 | TP2(전량) |
| 09:31:34 | 전량 | 1 | +3.20 | +149,541 | 미추적체결(pending_miss) |
| 09:33:09 | 전량 | 1 | -3.54 | -187,477 | 하드스톱(틱) |
| 09:37:02 | 부분 | 1 | -3.78 | -199,445 | 하드스톱(틱) |
| 09:37:02 | 전량 | 1 | -3.78 | -199,445 | 하드스톱(틱) |
| 11:39:59 | 전량 | 1 | +0.42 | +10,560 | 하드스톱(틱) |
| 13:04:17 | 전량 | 1 | -0.18 | -19,539 | 미추적체결(pending_miss) |
| 13:09:25 | 부분 | 1 | +0.05 | -8,202 | 미추적체결(pending_miss) |
| 13:09:26 | 부분 | 1 | -0.05 | -13,202 | 미추적체결(pending_miss) |
| 13:09:27 | 전량 | 1 | +0.03 | -9,202 | 미추적체결(pending_miss) |
| 13:18:31 | 전량 | 1 | -1.20 | -70,537 | 미추적체결(pending_miss) |
| 13:30:50 | 부분 | 1 | -0.15 | -18,040 | 미추적체결(pending_miss) |
| 13:30:51 | 전량 | 1 | -0.15 | -18,040 | 미추적체결(pending_miss) |
| 13:39:17 | 부분 | 1 | -1.37 | -79,034 | 하드스톱(틱) |
| 13:39:18 | 전량 | 1 | -1.35 | -78,034 | 하드스톱(틱) |
| 13:44:42 | 부분 | 1 | -0.03 | -11,864 | 미추적체결(pending_miss) |
| 13:44:42 | 부분 | 1 | -0.03 | -11,864 | 미추적체결(pending_miss) |
| 13:44:43 | 전량 | 1 | -0.09 | -14,864 | 미추적체결(pending_miss) |
| 13:51:17 | 전량 | 1 | +1.54 | +66,433 | 미추적체결(pending_miss) |
| 13:53:27 | 전량 | 1 | +0.52 | +15,454 | 미추적체결(pending_miss) |
| 13:59:01 | 전량 | 1 | +2.68 | +123,456 | TP2(전량) |
| 14:02:31 | 전량 | 1 | +0.36 | +7,485 | 하드스톱(틱) |
| 14:04:17 | 전량 | 1 | -0.62 | -41,512 | 미추적체결(pending_miss) |
| 14:11:52 | 전량 | 1 | +1.80 | +79,480 | 미추적체결(pending_miss) |
| 14:12:17 | 전량 | 1 | -0.64 | -42,502 | 미추적체결(pending_miss) |
| 14:18:53 | 전량 | 1 | -1.18 | -69,496 | 하드스톱(틱) |
| 14:23:32 | 전량 | 1 | -1.28 | -74,488 | 하드스톱(틱) |
| 14:33:14 | 전량 | 1 | +0.28 | +3,472 | 하드스톱(틱) |
| 14:55:28 | 전량 | 1 | +0.22 | +427 | 하드스톱(틱) |
| 15:24:41 | 부분 | 1 | -0.06 | -13,551 | 미추적체결(pending_miss) |
| 15:24:41 | 부분 | 1 | -0.08 | -14,551 | 미추적체결(pending_miss) |
| 15:24:45 | 전량 | 1 | -0.14 | -17,551 | 미추적체결(pending_miss) |
| 15:33:08 | 부분 | 1 | -0.08 | -14,552 | 미추적체결(pending_miss) |
| 15:33:09 | 부분 | 1 | +0.10 | -5,552 | 미추적체결(pending_miss) |
| 15:33:22 | 전량 | 1 | +0.08 | -6,552 | 미추적체결(pending_miss) |

**청산 사유 분포(레그 단위)** — `미추적체결(pending_miss)`×23, `하드스톱(틱)`×15, `TP2(전량)`×2, `TP1 부분청산 33%`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 11/27건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -1,616,734 = 포지션합 -1,562,196 → **불일치 ⚠** · `[청산 완료]` 30건 = 조립 포지션 27건 → **불일치 ⚠** · **귀속 실패 레그 3행 ⚠**(진입 로그 없는 이월 포지션 가능)

### CB③ 판정 가능 시간 — **114분 / 370분 (31%)**

acc30m 버퍼 리셋 4회 · 그때 버린 표본 120건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:38:01 | SHORT | 1 | 1063.96 | 3m | neutral |
| 14:33:01 | LONG | 1 | 1073.34 | 1m | neutral |

계약수 분포 — 1계약×2

등급 분포 — `A급(원시C)`×2

**진입한 건들의 체크리스트 미통과 항목** — `fore`×2, `risk`×2, `cvd`×1, `prev`×1, `ofi`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×5

실제 진입 계약수 — **1계약**×2

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×5

### 차단 사유 54건 · 23종

| 건수 | 사유 |
|---|---|
| 26 | 등급X — 미통과 항목: 2_confidence |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 94초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 121초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 61초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 1초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 118초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 58초 후 재진입 가능 |
| 1 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 106초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 172초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 112초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×26

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 25건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×14
- `연속 손절 2회 (300초 창, 포지션 단위)` ×4
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-01 13:41:14, 현재 1…` ×2
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-01 15:24:07, 현재 1…` ×2
- `일간 리셋 완료` ×2
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-01 13:22:05, 현재 1…` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 15건 · 최대 6250ms · 5초 초과 2건

상위 — 6250ms, 5234ms, 4813ms, 4594ms, 4266ms, 4094ms, 3906ms, 3609ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6250ms | 1651ms | **4599ms (74%)** |
| 12:52:04 | 5234ms | 368ms | **4866ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260901_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:10 2026-09-01 15:40:10 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 9분 < 하한 25분 — 최근 5거래일 평균 15분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 25분 · 도달불가 133분 · 재지않음 212분
--- ConstOut ×7(표본)
09:26:01 2026-09-01 09:26:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:19:00 2026-09-01 10:19:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:11:00 2026-09-01 11:11:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:47:01 2026-09-01 12:47:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×2(표본)
09:00:06 2026-09-01 09:00:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260901.log
12:52:04 2026-09-01 12:52:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260901.log
--- [CB] ×8(표본)
09:10:49 2026-09-01 09:10:49 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:21:43 2026-09-01 09:21:43 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:25:02 2026-09-01 09:25:02 [WARNING] SYSTEM: [CB] 연속 손절 2회 (300초 창, 포지션 단위)
09:33:09 2026-09-01 09:33:09 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:10:49 2026-09-01 09:10:49 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:13:49)
09:10:49 2026-09-01 09:10:49 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:13:49)
09:21:43 2026-09-01 09:21:43 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 3분 재진입 금지 (until 09:24:43)
09:21:43 2026-09-01 09:21:43 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 3분 재진입 금지 (until 09:24:43)
--- [SHAP] 슬로우 ×8(표본)
11:40:01 2026-09-01 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 912ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:57:02 2026-09-01 11:57:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 920ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:29:02 2026-09-01 12:29:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1591ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:37:02 2026-09-01 12:37:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1030ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- [SchedForceExit] ×1(표본)
15:24:37 2026-09-01 15:24:37 [ERROR] SYSTEM: [SchedForceExit] 15:10 경과에도 미청산 — 피드 독립 안전망 발동 (시도 1회, status=LONG engine=3ct broker_cached=0ct price_hint=1075.48)
--- degraded=ON ×8(표본)
09:24:00 2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
09:25:00 2026-09-01 09:25:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=281ms | quality=1.00 | cache_age=51s | exceptions_10m=13
09:26:01 2026-09-01 09:26:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=419ms | quality=1.00 | cache_age=112s | exceptions_10m=18
09:27:00 2026-09-01 09:27:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=519ms | quality=1.00 | cache_age=171s | exceptions_10m=18 [GBM재학습중→lat임계 5000/10000ms]
--- level=CRITICAL ×1(표본)
09:23:01 2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
--- 메인 스레드 블로킹 ×8(표본)
08:41:11 2026-09-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
08:46:05 2026-09-01 08:46:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2891ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2891 band=INFO since_pipe_s=NA
09:00:06 2026-09-01 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6250 band=WARN since_pipe_s=0.1
09:01:01 2026-09-01 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.1
--- 안전망 ×4(표본)
15:24:37 2026-09-01 15:24:37 [ERROR] SYSTEM: [BrokerDirectExit] 15:10 스케줄러 안전망 — broker LONG 3계약 → SELL 직접주문
15:24:37 2026-09-01 15:24:37 [WARNING] SYSTEM: [BrokerDirectExit] send_market_order ret=0 LONG 3계약 reason=15:10 스케줄러 안전망
15:33:07 2026-09-01 15:33:07 [ERROR] SYSTEM: [BrokerDirectExit] 15:10 스케줄러 안전망 — broker LONG 3계약 → SELL 직접주문
15:33:07 2026-09-01 15:33:07 [WARNING] SYSTEM: [BrokerDirectExit] send_market_order ret=0 LONG 3계약 reason=15:10 스케줄러 안전망
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260901_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:26:01 2026-09-01 09:26:01 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:28:00 (const_output)
09:26:01 2026-09-01 09:26:01 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:26:01 2026-09-01 09:26:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=92ms fit=103ms total=197ms
09:27:00 2026-09-01 09:27:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:08 2026-09-01 15:40:08 [INFO] SYSTEM: [CB③계측] 조건성립 63분 / 판정가능 114분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-01 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-09-01 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:11:00 2026-09-01 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:16:00 2026-09-01 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
--- [CB] ×7(표본)
13:30:51 2026-09-01 13:30:51 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-01 13:22:05, 현재 1회)
13:44:42 2026-09-01 13:44:42 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-01 13:41:14, 현재 1회)
13:44:43 2026-09-01 13:44:43 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-01 13:41:14, 현재 1회)
15:24:41 2026-09-01 15:24:41 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-01 15:24:07, 현재 1회)
--- [SchedForceExit] ×1(표본)
15:11:07 2026-09-01 15:11:07 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:11 2026-09-01 15:40:11 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:26 2026-09-01 15:40:26 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 안전망 ×1(표본)
15:24:37 2026-09-01 15:24:37 [INFO] SYSTEM: [Notify] ℹ️ [15:24:37] [미륵이] 🚨 미륵이 시간청산 안전망 발동 — 파이프라인 미경유, 브로커 직접 청산 시도
--- 자동 종료 ×5(표본)
15:40:11 2026-09-01 15:40:11 [INFO] SYSTEM: [Notify] ℹ️ [15:40:11] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:11 2026-09-01 15:40:11 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:26 2026-09-01 15:40:26 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260901_SIGNAL.log`
```
--- ConfFloorGuard ×6(표본)
09:00:01 2026-09-01 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:42:00 2026-09-01 10:42:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3809 ≥ 필요 0.3780
10:55:00 2026-09-01 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3752 < 필요 0.3780 (conf_floor=0.330, min_conf=0.378, span=0.0109). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:13:00 2026-09-01 11:13:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3757 ≥ 필요 0.3720
--- ConstOut ×8(표본)
09:26:01 2026-09-01 09:26:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0040 dir=-1) → 앙상블 제외
09:27:00 2026-09-01 09:27:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:19:00 2026-09-01 10:19:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:21:00 2026-09-01 10:21:00 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-01 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-01 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.5% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-01 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.4% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-01 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.416
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
--- 안전망 ×8(표본)
09:07:00 2026-09-01 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-01 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-01 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-01 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260901_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.508 out_max=0.3054 (기준 auc<0.53 and span<0.020, 기저율=0.3053 n=95) → 보정 미적용, raw 통과
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.436 out_max=0.1126 (기준 auc<0.53 and span<0.020, 기저율=0.1125 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-01 08:40:51 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00058 auc=0.537 out_max=0.2913 (n=110) → 보정 재적용
```

### `logs/20260901_HEALTH.log`
```
--- degraded=ON ×8(표본)
09:24:00 2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
09:25:00 2026-09-01 09:25:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=281ms | quality=1.00 | cache_age=51s | exceptions_10m=13
09:26:01 2026-09-01 09:26:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=419ms | quality=1.00 | cache_age=112s | exceptions_10m=18
09:27:00 2026-09-01 09:27:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=519ms | quality=1.00 | cache_age=171s | exceptions_10m=18 [GBM재학습중→lat임계 5000/10000ms]
--- level=CRITICAL ×1(표본)
09:23:01 2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260901_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 14:00 | 장중 후반 · 장중 재학습 | 39 | 13:54:17 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1074.76 — 진입 경로가 파라미터를 넘기지… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 21 | 15:24:07 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1075.48 — 진입 경로가 파라미터를 넘기지 … |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 9 | 15:34:46 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1076.00 — 진입 경로가 파라미터를 넘기지 … |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260901_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 13 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 11 | 08:55:08 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 08:55:08 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 2 | 10:01:00 [WARNING] level=WARNING degraded=OFF | latency=304ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |
| 12:00 | 장중 중간점 | 5 | 11:54:00 [WARNING] acc30m 단계 전환: NORMAL → RESTRICTED (acc=16.7%) |
| 14:00 | 장중 후반 · 장중 재학습 | 119 | 13:54:00 [CRITICAL] level=CRITICAL degraded=ON | latency=311ms | quality=1.00 | cache_age=111s | exceptions_10m=19 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 11 | 15:05:01 [WARNING] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 61 | 15:24:06 [WARNING] account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1075.… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 21 | 15:34:45 [WARNING] account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1076.… |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260901_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 88 | 08:40:34 [INFO] 활성화 | file=logs\crash_fault.log PID=17924 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 124 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 183 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 212 | 09:54:01 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 169 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 286 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 154 | 15:04:00 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 186 | 15:12:01 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 60 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260901_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:08 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0205) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 142 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0170) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 234 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0274) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 197 | 09:54:01 [WARNING] 신뢰도 미달 33.8% < 38.6% → 강제 X등급 |
| 12:00 | 장중 중간점 | 186 | 11:55:00 [WARNING] 신뢰도 미달 35.0% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 85 | 13:57:00 [WARNING] ts=13:56 horizon=1m age=13m max_z=-4.52(queue_depletion_speed) extreme=2 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 79 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:08 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| 20260827 | 15:40 | 로그 본문 |
| 20260826 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260901** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [511차 후속 13:50] O-i1 부분 판정 — 재현되지 않았고, 가설을 지지한다
### [511차 후속 14:12] Fix 구현 — F-19·F-21·F-22·G-6 배선, F-17 ②는 섀도, F-18은 보류
## 2026-09-01 (MW0601 — dev 512차 체리픽: ProfitGuard 패널 입력 격자 재설정)
## 2026-09-01 (MW0601 513차 — FZ-2 가짜 동결 경보: 정상 종료의 증거가 지워지고 있었다)
### 🔴 오탐이 매일 나고 있었다 — 08-25부터 하루 45회
### 원인 — 판정 논리가 아니라 **증거 결손**이었다. 두 축이 각각 다르게 빗나갔다
### 조치 (사용자 선택 ⓑ) — 런처가 지우지 않는 **날짜본 종료 마커**
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
남긴 경고 — 하한이 50만→10만원으로 내려가 L2
「거래중단 임계」를 실수로 10만원에 두면 당일 수익 10만원에서 거래가 완전
중단(당일 영구 래치)된다. 값 입력 시 주의할 것.

---

## 2026-09-01 (MW0601 513차 — FZ-2 가짜 동결 경보: 정상 종료의 증거가 지워지고 있었다)

사용자가 **팝업 스크린샷**을 들고 물었다 — `[Mireuk] 동결 센티넬 FZ-2` CRITICAL.
그날은 15:40:11 마감 완료 → 15:40:26 자동 종료로 **완전히 정상**인 날이었다.

### 🔴 오탐이 매일 나고 있었다 — 08-25부터 하루 45회

| 날짜 | FZ-2 CRITICAL |
|---|---|
| 08-25 · 08-26 · 08-27 · 08-31 | 각 **45회** |
| 08-28 | **93회** |
| 09-01 | 45회 예상(15:45~16:30) + **팝업 1회** |

전부 정상 마감한 날이다. **이 형태가 가장 나쁘다** — 경보 피로가 쌓이면
2026-08-19 13:41 의 **진짜 동결**(15:10 강제청산이 통째로 지나갔고 FLAT 이었던 것은
운)이 같은 문구에 묻힌다. 감시자가 양치기 소년이 됐다.

### 원인 — 판정 논리가 아니라 **증거 결손**이었다. 두 축이 각각 다르게 빗나갔다

| 축 | 왜 못 썼나 |
|---|---|
| `_exit_normally` | 런처가 읽은 **직후 지운다**(`start_mireuk.bat:597~598`). 센티넬이 판정할 때는 **항상 없다** → 영구 「미측정」 → 규약대로 동결 판정 유지 |
| `daily_close_done` | 마커는 15:40:11 인데 마감 뒤 **15초의 종료 로그**(`[System] 자동 종료 실행`)가 15:40:26 에 남는다. 498차 F-10 은 마커가 **가장 최근** 신호보다 뒤여야 한다고 봤으므로 **15초 차이로 매번 실패** |

🔴 **498차 F-10 은 실전에서 한 번도 성립한 적이 없다.** 08-26 오탐을 막으려고 만든
축인데, 임계나 표본의 문제가 아니라 **기준 선택(`min`)이 구조적으로 성립 불가**였다.
FP-CRITICAL 죽은 게이트·TOX 죽은 섀도와 같은 계열이다 — 배선은 됐는데 발화 조건이
현실에서 도달 불가.

### 조치 (사용자 선택 ⓑ) — 런처가 지우지 않는 **날짜본 종료 마커**

- `main.py:_write_exit_normally_flag()` 가 `_exit_normally` 와 **함께**
  `data/shutdown_normal_<YYYYMMDD>.txt` 를 쓴다. 같은 함수에 넣은 것이 핵심이다 —
  `_auto_shutdown()` 이 이 함수를 다시 부르므로 마커가 **종료 시점**(15:40:26)을 갖는다.
  마감 완료 시점(15:40:11)만 담으면 2026-09-01 형이 그대로 재발한다.
- `scripts/freeze_sentinel.py` 에 4번째 증거축 `shutdown_marker_age()` 신설.

⚠ **비교 기준이 기존 축과 다르다 — `max`(가장 오래된 정체 신호)다.**
이 마커는 「프로세스가 종료한 시각」이므로, 가장 오래된 신호보다 뒤이기만 하면
「정체 신호 전부가 이 종료 이전의 것」이 성립한다. `min`(가장 최근 신호)을 쓰면
종료 직후 로그 한 줄에 다시 걸린다 — F-10 과 같은 함정이다.

🔴 **08-19형 미탐은 세 겹으로 막았다.**
① 그날은 프로세스가 살아 있었으므로 마커 **자체가 없다** → 미측정 → CRITICAL 유지
② **존재만으로 판정하지 않는다** — 오전에 정상 종료(마커 기록)한 뒤 재기동한 세션이
   오후에 얼어붙으면 마커가 신호들보다 **먼저**라 기각된다
③ CRITICAL 판정문에 종료 마커 축의 상태가 **반드시 한 줄** 남는다(계측 4원칙 ②·③)

### 검증

- `tests/test_513_sentinel_shutdown_marker.py` **14 passed** — 09-01 재현(EXITED) ·
  08-19형(FROZEN) · 오전종료→오후동결(FROZEN) · `max` 기준 고정 · 판정문 축 노출 ·
  `main.py` 가 실제로 마커를 쓰는지 · 두 호출 경로 입력 일치 · 하드 종료 미승격.
- 기존 센티넬 스위트 회귀 없음(490·493·498차 + 457차 폴백 가시성 = 55 passed).
- 임시 루트에 09-01 상황을 재현해 `--once` 실측: 마커 있음 → `rc=6` EXITED /
  마커 없음 → `rc=3` CRITICAL.

⚠ **라이브 미검증** — 마커는 다음 정상 종료(2026-09-02 15:40)부터 생긴다.
오늘 돌고 있는 센티넬은 구코드라 16:30까지 CRITICAL 을 계속 남긴다(무해).

⚠ **하드 종료 승격은 여전히 하지 않았다**(`FREEZE_SENTINEL_KILL_ENABLED` 미구현 유지).
이 fix 는 알림 전용 성격을 바꾸지 않는다 — 승격은 주간회의 안건.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### P0
### P1
### P2
### 고도화 (섀도 → 승격 절차 준수)
### 판정 기준 갱신 (문서)
### 장후로 이월된 확인 (관측)
## 2026-09-01 (MW0601 511차 후속 14:12 — Fix 구현) 상태 갱신
## 2026-09-01 (MW0601 513차 — FZ-2 가짜 동결 경보 fix)
```

미완료 체크박스 **2254건** (끝에서 30건)
```
- [ ] 주간회의 안건 3건(승률 정의·F-15 외부진입 손익·F-13 이식) — 계속 미결.
- [ ] O-t3 — exception 축(`update_live` 0건)은 확인 완료. **DB 축(`ensemble_decisions.fp_psi`
- [ ] O-t1·O-t4 — 정의대로 장후 판정 대상, 변동 없음.
- [ ] O-p2(08-31 이월) `[CybosOrder] ret=` 코드 의미 — 오늘도 미발생, 발생 시 판정.
- [ ] **F-16(신규, P1) 🔴 주간회의 안건 — 09:09~09:33 원인불명 외부진입 7건
- [ ] **P2 — `[Health]` 로그에 `auto_entry_blocked` 필드 추가** —
- [ ] 1-2(PositionFallback 12건)는 1-1 파생 — 별도 Fix 불필요, 1-1 해소 후
- [ ] CB② 복원 여부 — 재검토 기한 2026-08-29 경과, 계속 미결(4일째).
- [ ] 주간회의 안건 **4건**(승률 정의·F-15/F-16 외부진입 손익(통합)·F-13 이식) — 계속 미결.
- [ ] **F-17 청산 주문 실패에 단계적 대응 핸들러** — 2026-09-01 13:28~13:30 하드스톱
- [ ] **F-18 (🔴 주간회의 안건 — 자동조치 C등급) 청산 거부 시 미체결 주문 자동 취소
- [ ] **F-19 청산 주문 실패를 TRADE 로그에 남긴다** — 현재 은닉률 97.6%(163/167).
- [ ] **F-20 `[TickStop-S0C] … → 주문 전송` 문구를 결과 기준으로** — 전송 **전** 로그는
- [ ] **F-21 실패 후 재무장 쿨다운** — `_process_tick_stop()` else 분기가 쿨다운 없이
- [ ] **F-22 BlockRequest 반환코드 매핑 상수** — `collection/cybos/api_connector.py`에
- [ ] **G-6 `closable_qty` 상태 승격** — `[ChejanFlow]`가 매 체결마다 이미 실어 보내는데
- [ ] **G-7 외부 미체결 주문 경보 채널** — `[ChejanMatch] pending_matched=False`로
- [ ] **F-1R 리허설 판정 기준에 "주문 거부"를 추가** — 현행 기준은
- [ ] **O-i1** 현재 SHORT 2계약 하드스톱 발동 시 94025 재현 여부
- [ ] **O-i2** 15:10 강제청산 실제 체결 여부 — `ret=0 kind=시간청산` 출현 + `[FinalClose]` 미출현
- [ ] **O-i3** 원인 가설 확정 — 13:26:41~13:30:50 구간 주문가능금액·청산가능수량
- [ ] **O-i4** 외부 주문 22레그 발생원 — 프로그램 후보 배제 완료(미륵이 1프로세스 ·
- [ ] **O-i5** `[BalanceUI]` summary 키 매핑 의심(`총평가`/`총평가수익률`/`추정자산`) —
- [ ] **F-17 청산 주문 실패 단계적 대응 핸들러** — **부분 이행**.
- [ ] **F-18 (🔴 주간회의) 청산 거부 시 미체결 주문 자동 취소 허용 여부** — 변동 없음.
- [ ] **배포(재기동)** — 장 마감 후. 지금 재기동하면 포지션·세션 복원 경로를 장중에
- [ ] **커밋 대기**: `main.py` · `config/settings.py` · `tests/test_511_exit_order_reject.py`
- [ ] **F-23R 라이브 확인 (2026-09-02 장후)** — 재기동 후 정상 마감한 날에
- [ ] **배포(재기동)** — 장 마감 후. 재기동 전까지 구코드가 돈다.
- [ ] **F-25 (참고) 498차 F-10 축 처분** — `daily_close_done` 축은 그대로 뒀다
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
BalanceUI]` summary 키 매핑 의심(`총평가`/`총평가수익률`/`추정자산`) —
      `dashboard/main_dashboard.py` 확인. **버그로 단정하지 말 것**(의도적 재사용 가능)

## 2026-09-01 (MW0601 511차 후속 14:12 — Fix 구현) 상태 갱신

- [x] **F-19 청산 주문 실패를 TRADE 로그에 남긴다** — ✅ 구현·테스트 완료
      (`main.py` 청산 실패 8곳 전부 `_ts_on_exit_order_reject` 훅).
      ⚠ **라이브 미검증** — 재기동 전까지 구코드가 돈다.
- [x] **F-21 실패 후 재무장 쿨다운(백오프·상한·경보)** — ✅ 구현·테스트 완료.
      `EXIT_REJECT_BACKOFF_SEC=[1,2,4,8]` · 경보 연속 3회 1번 · 15:10 경로는 면제.
- [x] **F-22 BlockRequest 반환코드 매핑 상수** — ✅ `EXIT_ORDER_RET_MEANING` 신설.
      ⚠ 양수 1~4는 **「⚠미검증」 표기**로 넣었고 **제어 흐름에 쓰지 않는다**(테스트 T8c가 고정).
      **대신 API 공식 문서 확인 후 표기를 확정할 것** — 이 항목은 아직 닫히지 않았다.
- [x] **G-6 `closable_qty` 상태 승격** — ✅ 잔고 Chejan에서 스냅샷 보관.
      `_ts_closable_qty_snapshot()`이 미측정/낡음을 `None`으로 구분(계측 4원칙 ②).
- [ ] **F-17 청산 주문 실패 단계적 대응 핸들러** — **부분 이행**.
      ①기록 ③백오프·상한 ⑤경보 = 완료 / **②수량 축소 재시도 = 섀도만**
      (`[ExitRejectShadow]` INFO 1줄/에피소드) / ④미체결 취소 = F-18 승인 대기.
      ② 승격 조건: `[ExitRejectShadow]`가 실제 거부 국면에서 남긴 후보 수량이
      브로커 잔고와 일치하는지 **최소 3에피소드** 확인. 그 전에는 과소청산 위험
      (2026-09-01 13:26:41 `closable_qty=0` vs 실제 LONG 2계약).
- [ ] **F-18 (🔴 주간회의) 청산 거부 시 미체결 주문 자동 취소 허용 여부** — 변동 없음.
- [x] ~~F-20 `→ 주문 전송` 문구 변경~~ — **보류 결정**. F-19가 해소했고, 문자열을 바꾸면
      과거 리포트·증거 다이제스트 8개 문서의 대조 문자열이 어긋나 이력 비교가 깨진다.
      재론 시 이 근거를 먼저 볼 것.
- [ ] **배포(재기동)** — 장 마감 후. 지금 재기동하면 포지션·세션 복원 경로를 장중에
      태우게 되고 그것이 더 큰 위험이다. 배포 후 다음 거래일 O-i1으로 라이브 확인.
- [ ] **커밋 대기**: `main.py` · `config/settings.py` · `tests/test_511_exit_order_reject.py`
      + 리포트·dev_memory 3종.

## 2026-09-01 (MW0601 513차 — FZ-2 가짜 동결 경보 fix)

> 상세: `DECISION_LOG.md` 2026-09-01(513차). 사용자 선택 ⓑ(날짜본 종료 마커).

- [x] **F-23 `data/shutdown_normal_<date>.txt` 신설** — ✅ `main.py:_write_exit_normally_flag()`.
      런처가 지우는 `_exit_normally` 와 달리 판정 시점에 남는다.
- [x] **F-24 센티넬 4번째 증거축 + `max` 기준** — ✅ `scripts/freeze_sentinel.py`.
      08-19형 미탐 방지 3겹 유지.
- [ ] **F-23R 라이브 확인 (2026-09-02 장후)** — 재기동 후 정상 마감한 날에
      ① `data/shutdown_normal_20260902.txt` 존재 ② `logs/freeze_sentinel_20260902.log` 에
      `정상 종료 확인(종료 마커) — 감시 종료` **1줄**, 그 뒤 CRITICAL **0건**
      ③ `data/freeze_sentinel_alert_20260902.txt` 미생성.
      ⚠ 셋 중 하나라도 어긋나면 되돌리지 말고 **어느 축이 어떻게 어긋났는지**부터
      판정문에서 읽을 것 — 이 결함은 두 번 다 「조건이 도달 불가」였다.
- [ ] **배포(재기동)** — 장 마감 후. 재기동 전까지 구코드가 돈다.
- [ ] **F-25 (참고) 498차 F-10 축 처분** — `daily_close_done` 축은 그대로 뒀다
      (마감은 끝났고 프로세스는 떠 있는 구간용). 종료 마커가 라이브 검증되면
      **두 축이 겹치는지** 확인하고, 겹치기만 하면 F-10 축은 유지하되 판정문에서
      혼동되지 않는지만 볼 것. **삭제 안건 아님.**

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

### `data/heartbeat_MW0601_20260901.json` — 243B · 09-01 15:40:19
```json
{
 "pid": 17924,
 "written_at": "2026-09-01T15:40:19",
 "beat_epoch": 1788244817.417344,
 "beat_age_sec": 2.5,
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

### `docs/정기점검/매일점검` — 89개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 67.8KB | 09-01 14:12 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_intra.md` | 68.8KB | 09-01 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_pre.md` | 49.8KB | 09-01 09:01 |
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 203.4KB | 08-31 18:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_post.md` | 79.5KB | 08-31 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_intra.md` | 65.5KB | 08-31 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` | 57.8KB | 08-31 09:00 |
| `docs/정기점검/매일점검/MW0601-20260831-8월손실일-딥다이브.md` | 22.2KB | 08-31 00:18 |

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

1. `logs/20260901_WARN.log`: ERROR 이상 405건
2. `logs/20260901_WARN.log`: **Traceback** 출현 2건 — 크래시/메모리 계열
3. `logs/20260901_HEALTH.log`: ERROR 이상 76건
4. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
5. 다레그 포지션 **9건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
6. 메인 스레드 정지 5초 초과 **2건** (최대 6250ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260901_WARN.log`: **degraded=ON** 8건(표본)
8. `logs/20260901_WARN.log`: **level=CRITICAL** 1건(표본)
9. `logs/20260901_WARN.log`: **ConstOut** 7건(표본)
10. `logs/20260901_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260901_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260901_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260901_LEARNING.log`: **축퇴** 8건(표본)
14. `logs/20260901_HEALTH.log`: **degraded=ON** 8건(표본)
15. `logs/20260901_HEALTH.log`: **level=CRITICAL** 1건(표본)
16. 미커밋 변경 516건 (실질 4건 · **코드(.py) 2건**) — 코드 변경이 커밋되지 않았다
17. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260901*.log` (Windows) / `grep 강제청산 logs/*20260901*.log`*