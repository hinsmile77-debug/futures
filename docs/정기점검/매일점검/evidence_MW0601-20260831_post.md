# 미륵이 증거 다이제스트 — 2026-08-31 / POST

- 생성 2026-08-31 16:17:06 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/stoic-festive-wozniak/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260831` · `2026-08-31` · `260831` · `0831`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **30개** 파일 · 30개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260831.txt` | 28B | 08-31 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260831.txt` | 28B | 08-31 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260831.txt` | 209B | 08-31 15:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260831.log` | 818B | 08-31 15:12 |
| `freeze_sentinel_alert_{DATE}.txt` | 1 | `data/freeze_sentinel_alert_20260831.txt` | 636B | 08-31 15:45 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260831.log` | 21.6KB | 08-31 16:16 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260831.json` | 244B | 08-31 15:40 |
| `launcher_{DATE}_004147_4902.log` | 1 | `logs/Mireuk_batch/launcher_20260831_004147_4902.log` | 16.9KB | 08-31 01:02 |
| `launcher_{DATE}_012504_13379.log` | 1 | `logs/Mireuk_batch/launcher_20260831_012504_13379.log` | 16.5KB | 08-31 01:30 |
| `launcher_{DATE}_013454_15309.log` | 1 | `logs/Mireuk_batch/launcher_20260831_013454_15309.log` | 16.8KB | 08-31 01:41 |
| `launcher_{DATE}_084001_297.log` | 1 | `logs/Mireuk_batch/launcher_20260831_084001_297.log` | 2.0MB | 08-31 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260831.log` | 12.0KB | 08-31 14:02 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260831.log` | 21.6KB | 08-31 15:48 |
| `retrain_intraday_{DATE}_093701.log` | 1 | `logs/retrain_intraday_20260831_093701.log` | 2.7KB | 08-31 09:37 |
| `retrain_intraday_{DATE}_124000.log` | 1 | `logs/retrain_intraday_20260831_124000.log` | 2.7KB | 08-31 12:40 |
| `retrain_intraday_{DATE}_131800.log` | 1 | `logs/retrain_intraday_20260831_131800.log` | 2.7KB | 08-31 13:18 |
| `retrain_intraday_{DATE}_135700.log` | 1 | `logs/retrain_intraday_20260831_135700.log` | 2.7KB | 08-31 13:57 |
| `retrain_intraday_{DATE}_150300.log` | 1 | `logs/retrain_intraday_20260831_150300.log` | 2.7KB | 08-31 15:03 |
| `strategy_report_{DATE}_154009.txt` | 1 | `data/daily_reports/strategy_report_20260831_154009.txt` | 2.2KB | 08-31 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260831_DATA.log` | 343.0KB | 08-31 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260831_DEBUG.log` | 240.1KB | 08-31 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260831_HEALTH.log` | 15.1KB | 08-31 15:09 |
| `{DATE}_HOGA.log` | 1 | `logs/20260831_HOGA.log` | 51.1MB | 08-31 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260831_LEARNING.log` | 432.4KB | 08-31 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260831_MICRO.log` | 1020.8KB | 08-31 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260831_PROBE.log` | 96.9KB | 08-31 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260831_SIGNAL.log` | 583.3KB | 08-31 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260831_SYSTEM.log` | 1.1MB | 08-31 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260831_TRADE.log` | 51.0KB | 08-31 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260831_WARN.log` | 227.8KB | 08-31 15:40 |

## 2. 코드·커밋 상태

- HEAD `f01080b` · 브랜치 `v9-dev` · 미커밋 516건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 511건 (추적변경 513 · 미추적 3 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
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

**당일(2026-08-31) 커밋**
```
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
6dfe6d7 [MW0601] 504차: 8월 손실일 딥다이브 + 손익추이2(CREON 반사실)·거래 출처 필터
```

**최근 커밋 12건**
```
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
6dfe6d7 [MW0601] 504차: 8월 손실일 딥다이브 + 손익추이2(CREON 반사실)·거래 출처 필터
fc05088 [MW0601] test_479 오탐 정정: broker_net_chain_audit.py를 _COMPRESSED_AWARE에 등록
1c51249 [MW0601] dev 502차 후속 체리픽: U-1 te ready 플래그 + U-2 [57] 게이트 섀도 배선
614eda2 [MW0601] dev 501차 D1 정정 실행 완료 — daily_broker_pnl 브로커net 재산출
9bf94dd [MW0601] dev 501차 체리픽: 브로커 net 예탁금 체인 결함 3종(D1/D2/D3) 수정
b2f94eb [MW0601] 500차 4단계: 구성적 중복 검출 + CORE 우선 시계 스크린 (SOP §3 B-5 / §2 A-6)
3f6f7bf [MW0601] 500차 3단계: 주간회의 결정 1·2·3 집행 (사용자 승인)
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

_본문 미열람(설정): `20260831_HOGA.log` 51.1MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260831.txt`** — 28B · 08-31 15:40:09
```
2026-08-31T15:40:09.817517
```

**`data/daily_close_started_20260831.txt`** — 28B · 08-31 15:40:05
```
2026-08-31T15:40:05.178033
```

**`data/daily_reports/strategy_report_20260831_154009.txt`** — 2.2KB · 08-31 15:40:09
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-08-31 15:40
========================================================
  버전    : v1.0  (69일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-2.54  MDD(자본대비)=12.8%
  당일      : WR=60.0%  PF=0.14
  롤링20일: 누적 -4780302원  Sh=-2.54  MDD(자본대비)=12.8%  MDD(peak대비)=397.1%
  당일손익 : broker(gross) -5,906,000원  수수료 413,508원  net -6,389,508원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CRITICAL (16.16)
  PSI     : 0.000 (CLEAR)
  PSI/feat: cvd_delta=0.000  ofi_pressure=0.000  vwap_position=0.000
--------------------------------------------------------
  권고    : ⛔ 롤백 검토
  사유    : CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요.
--------------------------------------------------------
  최근20건 순EV: 평균 -247,566원  승률 70.0%  합계 -4,951,315원
  등급별 순EV(30일): A=+5,616원(133건,승67%)  BROKER=-5,461,928원(1건,승0%)  C=-1,490원(33건,승73%)  MANUAL=-1,689원(53건,승58%)
  호라이즌별 순EV(30일): 1m=+14,918원(22건)  3m=-7,833원(117건)  5m=+44,423원(24건)  ?=-93,535원(57건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 16분  5일평균 19분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 42.9pt(5일평균 35.7pt)  1분평균변동 0.96pt(5일평균 0.93pt)
--------------------------------------------------------
  진입 퍼널(2026-08-31, 총 370분):
    FLAT 230 → conf미달 114 → CoherenceGate 10 → 게이트차단 16 → 후보 0 → 진입 0
    게이트별: 재시작유예=7  콜드스타트/기타(RegimeOverride)=3  CB정지=3  콜드스타트/기타(σ미수집)=1  콜드스타트/기타(조건부구간)=1  포지션보유중(평가생략)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260831.txt`** — 209B · 08-31 15:48:42
```
completed: 2026-08-31 15:48:42
rows: 40732
cols: 97
horizons_replaced: 5/6
t_load_s: 43.1
t_retrain_s: 175.0
t_total_s: 218.5
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/freeze_sentinel_alert_20260831.txt`** — 636B · 08-31 15:45:27
```
[FreezeSentinel] 2026-08-31 15:45:27 CRITICAL
  라이브 프로세스 동결 — 측정 가능한 신호 3종이 전부 300s 이상 정체다. 프로세스는 살아 있을 수 있으나 아무 일도 하지 않는다 (런처 재기동도 걸리지 않는다)
  · heartbeat        309s 전 (임계 300s) — 정체
  · crash_fault[TS]  309s 전 (임계 300s) — 정체
  · SYSTEM.log       303s 전 (임계 300s) — 정체
  · _exit_normally   **미측정**(플래그 없음/읽기 실패) — 동결 판정 유지
  · daily_close_done 318s 전 — 정체 신호(303s)보다 **먼저**다(마감 뒤 정지가 아니다)
```

_다이제스트 대상 8/23개 (중요도순). 제외: `retrain_intraday_20260831_124000.log`, `retrain_intraday_20260831_131800.log`, `retrain_intraday_20260831_135700.log`, `retrain_intraday_20260831_150300.log`, `20260831_MICRO.log`, `20260831_DATA.log`, `20260831_PROBE.log`, `launcher_20260831_084001_297.log`_

### `logs/20260831_TRADE.log` — 51.0KB · 380행 · 최종 15:40:06

- 형식 평문 · 시각 인식 380행 · WARNING=50, INFO=330

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:18 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-31 00:42:22 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-31 00:42:24 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=4 entry=1068.47 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-08-31 00:42:24 [WARNING] TRADE: [Position] 브로커 기준 동기화: LONG 4계약 @ 1068.47 | 손절=1067.72
2026-08-31 01:25:35 [WARNING] TRADE: [Position] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72)
  …
2026-08-31 15:05:09 [INFO] TRADE: [체결청산-부분] SHORT 1계약 @ 1063.28 | PnL=-1.96pt (-108,412원) | 잔여=1계약 | 사유=하드스톱(틱)
2026-08-31 15:05:09 [INFO] TRADE: [Chejan] 상태=체결 주문번호=4865 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-31 15:05:09 [INFO] TRADE: [Position] 체결청산 SHORT @ 1063.26 | PnL=-1.94pt (-107,412원) | 하드스톱(틱)
2026-08-31 15:05:09 [INFO] TRADE: [청산 완료] PnL=-1.95pt (-215,824원) | 포지션 합계 -215,824원 (레그 2)
2026-08-31 15:40:06 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 40 | 00:42:24 | 15:03:12 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=4 entry=1068.47 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `Position` | 7 | 00:42:24 | 08:41:05 | 브로커 기준 동기화: LONG 4계약 @ 1068.47 | 손절=1067.72 |
| `PositionDiag` | 3 | 01:25:35 | 08:40:57 | restore source=sync_from_broker:LONG saved_at=2026-08-31T00:42:24.750030 last_update_ts=2026-08-31T00:42:24.750030 |

**채널** — `TRADE`×380

**컴포넌트 상위 15** — `Chejan`×122, `Position`×85, `PositionFallback`×40, `체결동기화`×36, `주문요청`×23, `청산 완료`×20, `TickStop-S0C`×14, `체결청산-부분`×11, `TickTP1`×9, `Sizer`×6, `ProfitGuard`×5, `TP1 부분청산`×5, `PositionDiag`×3, `TP2 부분청산`×1

### `logs/20260831_WARN.log` — 227.8KB · 1168행 · 최종 15:40:09

- 형식 평문 · 시각 인식 1161행 · CRITICAL=25, ERROR=2, WARNING=1136, PLAIN=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-08-31 00:42:24 [WARNING] SYSTEM: [BrokerSync] balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '49756819', '총평가손익': '45412818', '실현손익': '0', '총평가': '-8.73', '총평가수익률': '45412818', '추정자산': '296000'}
2026-08-31 00:42:24 [WARNING] SYSTEM: [BrokerSync] startup sync raw rows=1 nonempty_rows=1 all_blank_rows=False record_name='CpTd0723' prev_next='' rows=[{'종목코드': 'A0569', '종목명': '¹Ì´ÏÄÚ½ºÇÇ F 202609', '구분': '매수', '매매구분': '매수', '잔고수량': '4', '청산가능': '4', '평균가': '1068.47', '매입단가': '1068.47', '현재가': '…
  …
드리프트: CRITICAL (Lv.3)
액션  : ⛔ 롤백 검토
사유  : CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요.
오늘 PnL: -6389508원
════════════════════════════════════════════════════
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 22 | 09:45:00 | 15:04:03 | level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13 |
| CRITICAL | `-` | 2 | ??:??:?? | ??:??:?? | (Lv.3) |
| CRITICAL | `BrokerSync` | 1 | 00:42:24 | 00:42:24 | startup sync 완료: FLAT -> LONG 4계약 @ 1068.47 |
| ERROR | `LiveDBG` | 1 | 13:58:15 | 13:58:15 | _tick_header 간격 15157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=15157 band=ALERT since_pipe_s=0.3 |
| ERROR | `NetRecon` | 1 | 15:40:06 | 15:40:06 | 🔴 net 불일치 — 엔진 -6,389,508원 vs 브로커 -6,298,047원 (잔차 -91,461원, 허용 ±78,409). 수수료: 엔진 413,508 vs 브로커 실측 392,047원 (배수 0.95). gross가 일치하는데 net만 어긋나면 원인은 **수수료율**이다 — scripts/commission_rate_recon.py --verify 로 재보정할 것 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-08-31 09:45:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13
2026-08-31 09:51:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=271ms | quality=1.00 | cache_age=163s | exceptions_10m=15
```

</details>

<details><summary>CRITICAL/- 원문 2건</summary>

```
드리프트: CRITICAL (Lv.3)
사유  : CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요.
```

</details>

<details><summary>CRITICAL/BrokerSync 원문 1건</summary>

```
2026-08-31 00:42:24 [CRITICAL] SYSTEM: [BrokerSync] startup sync 완료: FLAT -> LONG 4계약 @ 1068.47
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-08-31 13:58:15 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 15157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=15157 band=ALERT since_pipe_s=0.3
```

</details>

**WARNING — 태그 33종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 374 | 00:42:24 | 15:05:11 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 122 | 08:45:06 | 15:05:09 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=4 | gubun='0' | order_no='53' | pending='EXIT_FULL:LONG qty=4 filled=0 order_no=? reason=하드스톱(틱) req_at=08:45:06.058' | … |
| `ChejanMatch` | 122 | 08:45:06 | 15:05:09 | order_no='53' | pending='EXIT_FULL:LONG qty=4 filled=0 order_no=53 reason=하드스톱(틱) req_at=08:45:06.058' | pending_matched=True |
| `OrderSync` | 80 | 09:28:47 | 15:03:12 | 미추적 체결 감지 (pending_miss) order_no=700 side=SHORT qty=1 price=1047.14 before=FLAT |
| `Health` | 71 | 09:00:01 | 15:09:01 | level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0 |
| `RegimeFingerprint` | 67 | 09:00:00 | 15:08:00 | update_live 예외 (5분 스로틀): 'cvd_divergence' |
| `PendingOrder` | 46 | 08:45:06 | 15:05:10 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 4, 'price_hint': 1067.72, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `ExitCooldown` | 40 | 08:45:06 | 15:05:09 | 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06) |
| `ExitFillFlow` | 27 | 08:45:06 | 15:05:10 | after='LONG 3계약 @ 1068.47' | before='LONG 4계약 @ 1068.47' | fill_price=1041.5 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:LONG qty=4 filled=1 order_no=53 reason=하드스톱(틱) req_at=08:45:06.058' | reason='하드스톱(틱)' |
| `BrokerSync` | 16 | 00:42:24 | 08:41:05 | balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '49756819', '총평가손익': '45412818', '실현손익': '0', '총평가': '-8.73', '총평가수익률': '45412818', '추정자산': '296000'} |
| `ExitSendOrderResult` | 16 | 08:45:06 | 15:05:09 | ret=0 kind=하드스톱(틱) direction=LONG qty=4 |
| `ScalerRefresh` | 16 | 09:05:00 | 14:54:00 | 5분 누적 수익률 -0.825% (임계 ±0.670%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |

**채널** — `SYSTEM`×1068, `HEALTH`×93

**컴포넌트 상위 15** — `LiveDBG`×375, `ChejanFlow`×122, `ChejanMatch`×122, `Health`×93, `OrderSync`×80, `RegimeFingerprint`×67, `PendingOrder`×46, `ExitCooldown`×40, `ExitFillFlow`×27, `BrokerSync`×17, `ExitSendOrderResult`×16, `ScalerRefresh`×16, `TickStop`×14, `HealthPolicy`×14, `PipePerf`×12

### `logs/20260831_SYSTEM.log` — 1.1MB · 6875행 · 최종 15:40:24

- 형식 평문 · 시각 인식 6844행 · INFO=6844, PLAIN=31

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:08 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=9328 | 행감지=30s all_threads=True
2026-08-31 00:42:08 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-31 00:42:08 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-31 00:42:08 [INFO] SYSTEM: 미륵이 초기화
2026-08-31 00:42:08 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-28) 종가 버퍼 로드: 384봉
  …
2026-08-31 15:40:09 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-08-31 15:40:09 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-31 15:40:24 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-31 15:40:24 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-31 15:40:24 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×6844

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1234, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `BalanceUI`×267, `CybosEvent`×244, `CybosDailyPnl`×226, `BalanceRefresh`×158, `System`×121, `CybosDailyPnlHeaders`×113, `MicroRegime`×97

### `logs/20260831_SIGNAL.log` — 583.3KB · 5160행 · 최종 15:40:06

- 형식 평문 · 시각 인식 5160행 · WARNING=2134, INFO=3026

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.429
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.425
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.437
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.416
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.412
  …
2026-08-31 15:10:29 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-31 15:40:06 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-31 15:40:06 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 83분(22.4%) / DN 12분(3.2%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-08-31 15:40:06 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-31 age=40m extreme=503 refresh=35 grade_x=90 cb3=0
2026-08-31 15:40:06 [INFO] SIGNAL: [ModelHealth] date=2026-08-31 앙상블유효가동률=76.2% | 파이프라인 370분 | ConstOut 5회/8분 {"3m": {"events": 5, "minutes": 8}} | WeightCollapse 80분 | 장중재학습 5회 | CB③ ready 158분/370분 (43%) (리셋 2회, 표본손실 60건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1494 | 09:00:02 | 15:02:00 | 1m 'macro_vix' scale=0.0037 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 270 | 08:45:05 | 15:02:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0148) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 106 | 09:01:00 | 14:24:02 | 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 104 | 09:06:00 | 15:08:00 | 신뢰도 미달 34.9% < 39.9% → 강제 X등급 |
| `WeightCollapse` | 80 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerMonitor` | 71 | 09:01:00 | 14:24:02 | ts=09:00 horizon=1m age=1m max_z=+8.71(va_bandwidth) extreme=5 |
| `ConstOut` | 7 | 09:36:00 | 15:03:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4370 (conf_floor=0.330, min_conf=0.437, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `MetaGate` | 1 | 14:25:00 | 14:25:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×5160

**컴포넌트 상위 15** — `ScalerFloor`×1554, `SIGNAL`×740, `Ensemble`×375, `MetaGate`×370, `FQAdj`×367, `ZeroDiag`×359, `ScalerRefresh`×311, `Model`×160, `Checklist`×125, `ATR-Horizon`×123, `InstabilityGate`×99, `MicroRegime`×97, `WeightCollapse`×80, `ScalerMonitor`×72, `ToxicityGate`×52

### `logs/20260831_LEARNING.log` — 432.4KB · 3600행 · 최종 15:40:06

- 형식 평문 · 시각 인식 3600행 · WARNING=579, INFO=3021

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:10 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00067 auc=0.357 out_max=0.1503 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00060 auc=0.490 out_max=0.3002 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00056 auc=0.537 out_max=0.2447 (n=135) → 보정 재적용
  …
2026-08-31 15:40:06 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-31 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-31 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-31 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-31 15:40:06 [INFO] LEARNING: [Sigma] EOD sigma_20=0.06813% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 577 | 00:42:10 | 15:05:00 | 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Retrain` | 1 | 15:40:06 | 15:40:06 | DB pruning 실패: database table is locked |
| `DriftAdjuster` | 1 | 15:40:06 | 15:40:06 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 4일) |

**채널** — `LEARNING`×3600

**컴포넌트 상위 15** — `LEARNING`×1219, `Calibration`×1127, `SGD`×370, `sigma`×357, `Bias`×145, `Bias⚠`×136, `MetaConf`×77, `OnlineLearner`×44, `ScalerWarmup`×41, `SHAP`×15, `BiasReset`×13, `ExtremityCorrector`×11, `GBM`×11, `GBM-64`×10, `RF`×9

### `logs/20260831_HEALTH.log` — 15.1KB · 109행 · 최종 15:09:01

- 형식 평문 · 시각 인식 109행 · CRITICAL=22, WARNING=71, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0
2026-08-31 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=485ms | quality=0.86 | cache_age=106s | exceptions_10m=0
2026-08-31 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 284ms (표본 20분)
2026-08-31 09:36:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=323ms | quality=0.94 | cache_age=182s | exceptions_10m=9
2026-08-31 09:37:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=432ms | quality=1.00 | cache_age=59s | exceptions_10m=9 [GBM재학습중→lat임계 5000/10000ms]
  …
2026-08-31 15:05:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=350ms | quality=1.00 | cache_age=46s | exceptions_10m=7
2026-08-31 15:06:03 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=295ms | quality=1.00 | cache_age=109s | exceptions_10m=9
2026-08-31 15:07:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=293ms | quality=1.00 | cache_age=166s | exceptions_10m=7
2026-08-31 15:08:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=325ms | quality=1.00 | cache_age=42s | exceptions_10m=7
2026-08-31 15:09:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=320ms | quality=1.00 | cache_age=102s | exceptions_10m=7
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 22 | 09:45:00 | 15:04:03 | level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-08-31 09:45:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13
2026-08-31 09:51:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=271ms | quality=1.00 | cache_age=163s | exceptions_10m=15
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 71 | 09:00:01 | 15:09:01 | level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0 |

**채널** — `HEALTH`×109

**컴포넌트 상위 15** — `Health`×108, `HealthTrend`×1

### `logs/retrain_eod_20260831.log` — 21.6KB · 148행 · 최종 15:48:43

- 형식 평문 · 시각 인식 148행 · WARNING=15, INFO=133

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 15:45:04,151 [INFO] EOD_RETRAIN: =======================================================
2026-08-31 15:45:04,151 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-31 15:45:04,151 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-31 15:45:04,151 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-31 15:45:04,151 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-31 15:48:43,124 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0374 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-31 15:48:43,124 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0973 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-31 15:48:43,140 [INFO] SIGNAL: [ScalerRefresh] ts=15:48 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.06s
2026-08-31 15:48:43,140 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.06s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-31 15:48:43,140 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:54 | 15:47:33 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1500봉(81%)이 현행 학습구간 (현행 cutoff=2026-08-28 14:38:00 ≥ 홀드아웃 시작=2026-08-24 12:59:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-28 14:38 >= holdout_start=2026-08-24 12:59 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-28 … |
| `ScalerRefresh` | 6 | 15:48:43 | 15:48:43 | 1m CORE 'ofi_norm' raw_std≈0(0.0310) → identity(0,1) 강제 (FLAT 100% 방지) |
| `GuardGhost` | 2 | 15:46:03 | 15:46:03 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-31 14:32:00까지)인데 acc.txt=0.4045는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `Retrain` | 1 | 15:47:12 | 15:47:12 | 15m 교체 보류(EOD 모델가드) — acc 하락 0.0372 > 허용 0.0300 (new=0.4055 old=0.4427) — 참고용 저장, 구모델 유지 |

**채널** — `LEARNING`×65, `SIGNAL`×55, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×22, `EOD_RETRAIN`×14, `RF`×9, `ScalerRefresh`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `RegimeFingerprint`×3, `WaitDC`×2, `GuardGhost`×2

### `logs/retrain_intraday_20260831_093701.log` — 2.7KB · 21행 · 최종 09:37:23

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dcb44c89.json
2026-08-31 09:37:04,317 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-31 09:37:23,485 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-08-31 09:37:23,485 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-31 09:37:23,486 [INFO] LEARNING: [Retrain] 완료 | 19.2초 | 성공=1/1 호라이즌
2026-08-31 09:37:23,486 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.3s 데이터=4800행
2026-08-31 09:37:23,488 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dcb44c89.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CRITICAL (Lv.3)
액션  : ⛔ 롤백 검토
사유  : CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요.
오늘 PnL: -6389508원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 20 |
| 차단(`[차단]`) | 49 |
| 사이저 호출(`[Sizer]`) | 6 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|

**청산 레그 0행** (부분청산 17 · 전량청산 20)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 -6,389,507 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 20건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패 레그 37행 ⚠**(진입 로그 없는 이월 포지션 가능)

### CB③ 판정 가능 시간 — **158분 / 370분 (43%)**

acc30m 버퍼 리셋 2회 · 그때 버린 표본 60건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×5, **2계약**×1

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×6

### 차단 사유 49건 · 2종

| 건수 | 사유 |
|---|---|
| 47 | Restart Armistice — 재시작 유예 중 (time_ok=True sync=0/2) |
| 2 | Circuit Breaker PAUSED — 진입 불가 (CB 해제까지 대기) |

### Circuit Breaker 이벤트 15건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×7
- `연속 손절 2회 (300초 창, 포지션 단위)` ×2
- `5분 진입 정지 | 파이프라인 14080ms — 처리 지연 (임계=5000ms)` ×2
- `일시 정지 해제 — 정상 복귀` ×2
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 21건 · 최대 15157ms · 5초 초과 4건

상위 — 15157ms, 7718ms, 5281ms, 5000ms, 4859ms, 4813ms, 4796ms, 4532ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:07 | 7718ms | 1376ms | **6342ms (82%)** |
| 12:38:04 | 5000ms | 363ms | **4637ms (93%)** |
| 13:58:15 | 15157ms | 14080ms | **1077ms (7%)** |
| 14:02:04 | 5281ms | 421ms | **4860ms (92%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260831_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:08 2026-08-31 15:40:08 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 16분 < 하한 25분 — 최근 5거래일 평균 19분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 20분 · 재지않음 350분
--- ConstOut ×5(표본)
09:36:00 2026-08-31 09:36:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:39:00 2026-08-31 12:39:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
13:17:01 2026-08-31 13:17:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
13:56:00 2026-08-31 13:56:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×4(표본)
09:00:07 2026-08-31 09:00:07 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260831.log
12:38:04 2026-08-31 12:38:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260831.log
13:58:15 2026-08-31 13:58:15 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260831.log
14:02:04 2026-08-31 14:02:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260831.log
--- [CB] ×8(표본)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:30:37 2026-08-31 09:30:37 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:42:52 2026-08-31 09:42:52 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:52:39 2026-08-31 09:52:39 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06)
09:30:37 2026-08-31 09:30:37 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:33:37)
09:30:37 2026-08-31 09:30:37 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:33:37)
--- [SHAP] 슬로우 ×7(표본)
12:35:02 2026-08-31 12:35:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 980ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:24:01 2026-08-31 13:24:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 915ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:39:01 2026-08-31 13:39:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 922ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
13:52:01 2026-08-31 13:52:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1082ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- degraded=ON ×8(표본)
09:39:00 2026-08-31 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=494ms | quality=1.00 | cache_age=178s | exceptions_10m=7
09:40:00 2026-08-31 09:40:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=368ms | quality=1.00 | cache_age=55s | exceptions_10m=7
09:41:00 2026-08-31 09:41:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=404ms | quality=1.00 | cache_age=115s | exceptions_10m=6
09:42:00 2026-08-31 09:42:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=340ms | quality=1.00 | cache_age=175s | exceptions_10m=6
--- level=CRITICAL ×2(표본)
13:58:14 2026-08-31 13:58:14 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=14080ms | quality=1.00 | cache_age=93s | exceptions_10m=2
14:34:00 2026-08-31 14:34:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=422ms | quality=1.00 | cache_age=29s | exceptions_10m=15
--- 메인 스레드 블로킹 ×8(표본)
01:30:03 2026-08-31 01:30:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2328 band=INFO since_pipe_s=NA
08:41:08 2026-08-31 08:41:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3046ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3046 band=INFO since_pipe_s=NA
09:00:07 2026-08-31 09:00:07 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7718ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7718 band=WARN since_pipe_s=0.1
09:01:01 2026-08-31 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2109ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2109 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260831_SYSTEM.log`
```
--- CIRCUIT ×2(표본)
13:58:15 2026-08-31 13:58:15 [INFO] SYSTEM: [Notify] 🚨 [13:58:15] [미륵이] Circuit Breaker 발동!
13:58:15 2026-08-31 13:58:15 [INFO] SYSTEM: [Notify] 🚨 [13:58:15] [미륵이] Circuit Breaker 발동!
--- ConstOut ×8(표본)
09:36:00 2026-08-31 09:36:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:38:00 (const_output)
09:36:00 2026-08-31 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:00 2026-08-31 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=376ms fit=61ms total=440ms
09:37:00 2026-08-31 09:37:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:06 2026-08-31 15:40:06 [INFO] SYSTEM: [CB③계측] 조건성립 56분 / 판정가능 158분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- [CB] ×4(표본)
14:04:00 2026-08-31 14:04:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
14:04:00 2026-08-31 14:04:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
15:40:06 2026-08-31 15:40:06 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:06 2026-08-31 15:40:06 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:05 2026-08-31 15:11:05 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:09 2026-08-31 15:40:09 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:24 2026-08-31 15:40:24 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:09 2026-08-31 15:40:09 [INFO] SYSTEM: [Notify] ℹ️ [15:40:09] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:09 2026-08-31 15:40:09 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:24 2026-08-31 15:40:24 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260831_SIGNAL.log`
```
--- CIRCUIT ×2(표본)
13:59:00 2026-08-31 13:59:00 [INFO] SIGNAL: [차단] Circuit Breaker PAUSED — 진입 불가 (CB 해제까지 대기)
14:02:00 2026-08-31 14:02:00 [INFO] SIGNAL: [차단] Circuit Breaker PAUSED — 진입 불가 (CB 해제까지 대기)
--- ConfFloorGuard ×1(표본)
09:00:00 2026-08-31 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4370 (conf_floor=0.330, min_conf=0.437, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:36:00 2026-08-31 09:36:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외
09:37:01 2026-08-31 09:37:01 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
12:39:00 2026-08-31 12:39:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
12:40:00 2026-08-31 12:40:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-08-31 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-08-31 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=74.4% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-08-31 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=70.4% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-08-31 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=53.6% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.429
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.425
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.437
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.416
--- 안전망 ×8(표본)
09:07:00 2026-08-31 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-31 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-08-31 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-08-31 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260831_LEARNING.log`
```
--- 축퇴 ×8(표본)
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00067 auc=0.357 out_max=0.1503 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00060 auc=0.490 out_max=0.3002 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00056 auc=0.537 out_max=0.2447 (n=135) → 보정 재적용
```

### `logs/20260831_HEALTH.log`
```
--- degraded=ON ×8(표본)
09:39:00 2026-08-31 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=494ms | quality=1.00 | cache_age=178s | exceptions_10m=7
09:40:00 2026-08-31 09:40:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=368ms | quality=1.00 | cache_age=55s | exceptions_10m=7
09:41:00 2026-08-31 09:41:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=404ms | quality=1.00 | cache_age=115s | exceptions_10m=6
09:42:00 2026-08-31 09:42:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=340ms | quality=1.00 | cache_age=175s | exceptions_10m=6
--- level=CRITICAL ×2(표본)
13:58:14 2026-08-31 13:58:14 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=14080ms | quality=1.00 | cache_age=93s | exceptions_10m=2
14:34:00 2026-08-31 14:34:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=422ms | quality=1.00 | cache_age=29s | exceptions_10m=15
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260831_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:40:57 [WARNING] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72) |
| 10:00 | 장중 초반 | 11 | 09:56:09 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1045.82 — 진입 경로가 파라미터를 넘기지… |
| 14:00 | 장중 후반 · 장중 재학습 | 1 | 14:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=43,378,038) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdv… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 9 | 15:05:09 [INFO] 하드스톱(틱) SHORT 2ct tick=1063.18 stop=1063.10 → 주문 전송 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:06 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 00:42 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260831_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 34 | 08:40:57 [WARNING] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 14 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 18 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 42 | 09:54:00 [WARNING] update_live 예외 (5분 스로틀): 'cvd_divergence' |
| 12:00 | 장중 중간점 | 6 | 11:54:00 [WARNING] acc30m 단계 전환: WATCH → RESTRICTED (acc=26.7%) |
| 14:00 | 장중 후반 · 장중 재학습 | 15 | 13:55:00 [WARNING] update_live 예외 (5분 스로틀): 'cvd_divergence' |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 39 | 15:04:03 [WARNING] total=3033ms | S0=2790ms S1=29ms S2=0ms S3=0ms S4=28ms S5=143ms S6=31ms S7=9ms S8=3ms |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:06 [WARNING] gross 불일치 — broker -5,906,000원[TR수신 2026-08-31 15:05:11] vs engine -5,976,000원 (차 +70,000원). 체결 누락 또는 브로커 미정산… |

- 이 로그 생존구간: 00:42 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260831_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=24976 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 193 | 08:54:02 [INFO] #2100 code=A0569 raw_time=85402 parsed=08:54:02 price=1043.10 vol=1 bid1=1042.88 ask1=1043.34 flag=49 side=BU… |
| 10:00 | 장중 초반 | 254 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 176 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 200 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 188 | 15:04:00 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 128 | 15:12:01 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 42 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 00:42 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260831_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:05 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0148) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 142 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0449) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 275 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0392) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 138 | 09:54:01 [WARNING] 신뢰도 미달 34.0% < 38.6% → 강제 X등급 |
| 12:00 | 장중 중간점 | 171 | 11:54:00 [WARNING] 신뢰도 미달 34.5% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 175 | 13:54:00 [WARNING] 신뢰도 미달 31.0% < 37.4% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 52 | 15:04:03 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:06 [INFO] daily reset complete |

- 이 로그 생존구간: 00:42 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| 20260827 | 15:40 | 로그 본문 |
| 20260826 | 15:40 | 로그 본문 |
| 20260825 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260831** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 증상
### 원인
### 결정 (오늘은 계획만 — 코드 변경 0, 커밋 0)
### Why
### How to apply
### 검증 (전부 미실시 — 장후 예정)
### 고도화 (섀도만 — 차단 아님)
### 오늘 상태 (장중 12:31 시점)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 요약을 **입력으로 쓴다**.
  고치지 않으면 사후검증을 시작할 수 없다.
- F-7은 **오늘 EOD가 자가 치유해도 그대로 적용한다** — 치유는 「이번 한 번」이고
  F-7은 「다음 집합 교체」를 막는다. EOD 직후 O-i3으로 치유 여부부터 확인할 것.
- F-6은 라이브 진입 경로를 여는 변경이라 **가장 마지막**. 회귀 5종 재실행 필수.
- ⚠ 505차 F-1~F-5가 먼저다(그쪽이 P0 손실 경로). F-6~F-8은 그 뒤.

### 검증 (전부 미실시 — 장후 예정)

- `tests/test_506_armistice_release.py` — ⓐ FLAT 재시작 + 브로커 sync 정상 → 90초 후
  해제 ⓑ 브로커 sync 미검증 → 시간이 지나도 **미해제**(역방향) ⓒ 오늘 09:21~12:26
  로그 리플레이로 30분 고착 ERROR 발화.
- `tests/test_506_fingerprint_key_mismatch.py` — ⓐ **08-28자 실제 파일**
  (`cvd_divergence`/`ofi_norm` 포함)을 픽스처로 고정해 이 사고의 지문을 회귀로 박는다
  ⓑ 로드 후 `update_live()` 무예외 ⓒ 필터로 전부 비면 `get_psi() is None`.
- `tests/test_506_collector_fill_entry_regex.py` — ⓐ 오늘 TRADE 로그 픽스처로
  **포지션 14건 · 레그 25행 · -6,477,882원** 재현 ⓑ `[체결진입보정]` **미매칭**
  ⓒ 08-27 로그(두 형식 혼재) 이중 계상 0.

### 고도화 (섀도만 — 차단 아님)

- **G-3 `entry_gate_stuck_shadow`** — 진입 차단 사유별 **연속 지속시간**을 매분
  `predictions.db` 적재, 개장 후 30분 이상 연속이면 경보 등급 상향.
  `_entry_block_reason`(`main.py:9210~9250`)이 이미 문자열을 만들고 있어 **새 계산 0회**.
  근거: 오늘 Armistice 3시간 5분 연속 차단이 INFO 한 줄로만 남았다.
- **G-4 `[StateRecon]` 기동 시 상태파일 세대 대사** — `regime_fingerprint.json` ·
  `model/horizons/feature_names.pkl` · 스케일러 pkl의 **키 집합**을 코드 상수와 대조해
  1줄 요약. ⚠ `feature_names.pkl` 97개 동결 슈퍼셋은 **의도된 설계**(절대원칙 §3, 458차)
  이므로 대사에는 넣되 **불일치를 이상으로 판정하지 않는다** — 보고만 한다.
- 둘 다 오늘 표본 n=1(계열은 n=3) — **313차 원칙, 확정 결론 금지.** 승격 최소 4주 뒤.

### 오늘 상태 (장중 12:31 시점)

매분 9단계 전 STEP 실행 확인 — `분봉 파이프라인 시작` **211회**(09:00~12:30 = 210분,
누락 0분). STEP1 채점 449건 · STEP2 SGD 매분 · STEP3 재학습 **1회**(09:36 `ConstOut`
후속 → 09:37:23 `성공=1/1`, `py310_64` 정상 — **이벤트 구동이므로 정상**, 483차 문서정정) ·
STEP7 **0건**(위 ②) · STEP8 14포지션 청산.
메인 스레드 블로킹 12건 · 최대 7,718ms(09:00:07 개장) · **5초 초과 1건** ·
09:01 이후 최대 4,859ms. CB⑤ 미발동 정상(단위 상이).
CB②(9999) 카운터 7회 상승 — **11:06:09에 「2회」 도달**(복원값 2였다면 그 시점 당일 정지).
CB③-P4 11:52 `NORMAL→WATCH(33.3%)` → 11:54 `WATCH→RESTRICTED(26.7%)` —
차단 비활성이라 무영향. FZ-1 `fired:false strikes:0 beat_age 2.2s`.
Health 09:45~10:00 `CRITICAL degraded=ON` 8건 → 11:55 INFO 복귀.

🔴 **다이제스트 §7의 「12:28~15:10 연속 163분 기록 없음」·「커버리지 56.1%」·
「종료시각 델타 -193분」은 이상이 아니다** — 수집기가 12:26:52에 실행돼 그 이후를
못 본 것이다. 12:28:01·12:29:00·12:30:00 `[PipePerf][DBG]` 직접 확인.
**장중 수집의 구조적 성질이므로 장후에 이상점으로 승계하지 말 것.**

**커밋하지 않았다.** 대기:
`docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` ·
`docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` ·
`docs/정기점검/매일점검/evidence_MW0601-20260831_intra.md` ·
`dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md`.
⚠ `git add .` 금지 — 미커밋 515건 중 실질 2건 · 코드 0건 · EOL 파생 511건.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### MW0601 494차 후속 (2026-08-26 15:10) — F-1′ 적용 완료
### MW0601 494차 후속2 (2026-08-26 15:30) — 커밋으로는 동기화가 안 된다 (실측 확정)
### MW0601 494차 후속3 (2026-08-26 16:40 — 장후 점검)
### 498차 — 장후 자동조치 (MW0601, 2026-08-26 17:30~19:0x · `mireuk-postmarket-autofix` 첫 실행)
### MW0601 499차 (2026-08-27 08:57~09:1x — 장전 점검)
### MW0601 500차 (2026-08-30 — CVD·OFI 유효성 조사 · 5단계 집행)
### MW0601 505차 (2026-08-31 08:57~09:2x — 장전 점검)
### MW0601 506차 (2026-08-31 12:26~12:3x — 장중 점검)
```

미완료 체크박스 **2159건** (끝에서 30건)
```
- [ ] **O-p1 (장중→장후)** `[ConfFloorGuard]`(09:00:00, 출력상한 0.3479 < 필요 0.4370)
- [ ] **O-p2 (장후)** `[CybosOrder] ret=4` 의미 — 일시적/구조적. 과거 로그 전수
- [ ] **O-p3 (장후)** 08-28 주문번호 3639 주체(사람/엔진) — `ensemble_decisions`
- [ ] **O-p4 (장후)** `[Canary] z경고피처=12개`가 임계 12와 **정확히 같다**(경계 접촉).
- [ ] **O-p5 (장후)** 개장 버스트 메인 정지 — 오늘 **7,718ms**(0827 9,500ms 대비).
- [ ] **O-p6 (장후)** `session_state.json`에 `p8_last_success_date`·
- [ ] 🔴 **오늘 15:45~16:00 증권사 화면에서 선물 잔고 0 직접 확인** — 프로그램
- [ ] 🔴 **CB② 복원 재검토 기한 2026-08-29 경과** — `CB_CONSEC_STOP_LIMIT=9999` 유지.
- [ ] **2026-08-28(금) 매일점검 미실행 원인 확인** — 리포트·증거 다이제스트 둘 다
- [ ] **커밋 대기 (이 세션은 커밋하지 않았다)** — ⚠ `git add .` 금지
- [ ] **F-6 (P0) Restart Armistice 고착 해소** `main.py:8537~8556`
- [ ] **F-6 테스트** `tests/test_506_armistice_release.py` — 정방향/역방향/오늘 로그 리플레이
- [ ] **F-7 (P1) PSI 기준선 키 불일치 흡수** `strategy/regime_fingerprint.py`
- [ ] **F-7 테스트** `tests/test_506_fingerprint_key_mismatch.py` — 08-28자 실제 파일
- [ ] **F-8 (P1) 수집기 진입 정규식** `scripts/collect_evidence.py:133` +
- [ ] **F-8 테스트** `tests/test_506_collector_fill_entry_regex.py` — 오늘 TRADE 로그로
- [ ] **F-9 (P2) 외부 진입 표기·격리** 🔴 **주간회의 안건 · 자동조치 등급 밖 ·
- [ ] **G-3 `entry_gate_stuck_shadow`** — 진입 차단 사유별 **연속 지속시간** 매분
- [ ] **G-4 `[StateRecon]` 기동 시 상태파일 세대 대사** — `regime_fingerprint.json` ·
- [ ] **O-i1 (장후)** 오늘 25체결·13포지션의 **주체**(사람/다른 프로그램) —
- [ ] **O-i2 (장후)** Armistice `sync_count`가 과거에도 0에 머물렀는가 —
- [ ] **O-i3 (장후 · 최우선)** 오늘 EOD(15:45~) 후 `data/regime_fingerprint.json` 이
- [ ] **O-i4 (장후)** 수집기 §5 공백이 **08-28에도** 있었는가 — 08-28 로그로
- [ ] **O-i5 (장후)** `entry_horizon` 폴백 1.00이 하드스톱 편중(포지션 단위 78.6% =
- [ ] 🔴 **오늘 09:28~12:27에 증권사 화면에서 직접 매매했는지 확인** — 예이면
- [ ] 🔴 **오늘 15:08~15:12 「15:10 강제청산」 실행 관측** — 12:31 현재 SHORT 1계약
- [ ] **오늘 15:45~16:00 증권사 화면 선물 잔고 직접 확인**(505차 조치 2 — 유지·중요도 상승)
- [ ] **커밋 대기 (506차도 커밋하지 않았다)** — ⚠ `git add .` 금지
- [ ] **O-p1 잔여** — `ConfFloorGuard`가 매일 뜨는가(과거 5거래일 대조). 주질문
- [ ] **1-12(CB② 기한) 새 실측 근거** — 오늘 연속 손절 카운터 7회 상승,
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
k_reason`(`main.py:9210~9250`) 재사용 → **새 계산 0회**.
      근거: 오늘 Armistice **3시간 5분** 연속 차단이 INFO 한 줄로만 남았다(함정 ④)
- [ ] **G-4 `[StateRecon]` 기동 시 상태파일 세대 대사** — `regime_fingerprint.json` ·
      `model/horizons/feature_names.pkl` · 스케일러 pkl **키 집합** vs 코드 상수, 1줄 요약.
      ⚠ `feature_names.pkl` 97개 동결 슈퍼셋은 **의도된 설계**(절대원칙 §3, 458차) —
      대사에는 넣되 **불일치를 이상으로 판정하지 않는다**(보고만)

**관측 (장후가 판정/보류/이월 중 하나로 닫는다 — 미처분 금지)**

- [ ] **O-i1 (장후)** 오늘 25체결·13포지션의 **주체**(사람/다른 프로그램) —
      `predictions.db:ensemble_decisions` 09:28~12:27 대응 행 유무 + `trades` 귀속.
      **O-p3과 한 묶음**(08-28 주문 3639 1건 → 표본 26건으로 확대)
- [ ] **O-i2 (장후)** Armistice `sync_count`가 과거에도 0에 머물렀는가 —
      최근 5거래일 `[차단] Restart Armistice` 건수·지속시간·`sync=` 값 분포
- [ ] **O-i3 (장후 · 최우선)** 오늘 EOD(15:45~) 후 `data/regime_fingerprint.json` 이
      **새 CORE 3종**(`cvd_delta_norm`/`vwap_position`/`ofi_pressure`)으로 재생성되는가.
      `retrain_eod.py:538` `save_training_fingerprint()` 가 자가 치유할 가능성이 높다.
      ⚠ **부분 저장(빈/불완전 기준선) 여부도 함께** — `len(vals) >= _N_BINS*2=20` 미달
      피처는 조용히 스킵되고, 그러면 PSI가 **0.0 고정**으로 위장된다(4원칙 ②)
- [ ] **O-i4 (장후)** 수집기 §5 공백이 **08-28에도** 있었는가 — 08-28 로그로
      `collect_evidence.py --phase post` 재실행 후 §5 대사(그날 점검 미실행이라 미확인)
- [ ] **O-i5 (장후)** `entry_horizon` 폴백 1.00이 하드스톱 편중(포지션 단위 78.6% =
      11/14)에 **인과인가** — `trades.stop_price` 대 실현손실 / 의도 손절폭(ATR×1.5)
      초과 비율, 417차 재분해 방법론. ⚠ 표본 13건 — **313차 원칙, 확정 결론 금지**

**사용자 조치 (리포트 §사용자 조치(장중 추가분)와 동일)**

- [ ] 🔴 **오늘 09:28~12:27에 증권사 화면에서 직접 매매했는지 확인** — 예이면
      시스템 결함 아님(단 오늘 손익을 시스템 성적으로 집계 금지, F-9).
      **아니오이면 즉시 프로그램 정지 + 계좌 확인**
- [ ] 🔴 **오늘 15:08~15:12 「15:10 강제청산」 실행 관측** — 12:31 현재 SHORT 1계약
      보유. 505차 1-3(주문 실패 시 재시도 없음)이 **오늘 실제로 쓰인다**.
      15:11에 「안전망 발동」 ERROR가 뜨면 1차 경로 실패
- [ ] **오늘 15:45~16:00 증권사 화면 선물 잔고 직접 확인**(505차 조치 2 — 유지·중요도 상승)
- [ ] **커밋 대기 (506차도 커밋하지 않았다)** — ⚠ `git add .` 금지
      (실질 변경 2건 · 코드 0건 · EOL 파생 511건). 경로 명시:
      `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` ·
      `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` ·
      `docs/정기점검/매일점검/evidence_MW0601-20260831_intra.md` ·
      `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md`

**505차 항목 갱신 (새 번호 부여 금지 — 원 항목에 근거만 추가)**

- [ ] **O-p1 잔여** — `ConfFloorGuard`가 매일 뜨는가(과거 5거래일 대조). 주질문
      (자동 진입 0건 · 원인 귀속)은 506차가 판정 완료:
      **0건 확인 / 원인은 ConfFloorGuard 단독이 아니라 Armistice 병행**
- [ ] **1-12(CB② 기한) 새 실측 근거** — 오늘 연속 손절 카운터 7회 상승,
      **11:06:09에 「2회」 도달**. 복원값이 2였다면 그 시점 당일 정지
      (이후 3자리: -138,222 / -253 / +93,658원). 주간회의 자료로 쓸 것

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

### `data/heartbeat_MW0601_20260831.json` — 244B · 08-31 15:40:18
```json
{
 "pid": 24976,
 "written_at": "2026-08-31T15:40:18",
 "beat_epoch": 1788158415.1970782,
 "beat_age_sec": 3.2,
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

### `docs/정기점검/매일점검` — 85개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 97.9KB | 08-31 12:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_intra.md` | 65.5KB | 08-31 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` | 57.8KB | 08-31 09:00 |
| `docs/정기점검/매일점검/MW0601-20260831-8월손실일-딥다이브.md` | 22.2KB | 08-31 00:18 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.2KB | 08-31 00:05 |
| `docs/정기점검/매일점검/MW0601-20260827-점검리포트.md` | 90.4KB | 08-27 12:43 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_intra.md` | 66.2KB | 08-27 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_pre.md` | 52.6KB | 08-27 09:00 |

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

1. `logs/20260831_WARN.log`: ERROR 이상 27건
2. `logs/20260831_WARN.log`: **Traceback** 출현 4건 — 크래시/메모리 계열
3. `logs/20260831_HEALTH.log`: ERROR 이상 22건
4. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
5. 메인 스레드 정지 5초 초과 **4건** (최대 15157ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260831_WARN.log`: **degraded=ON** 8건(표본)
7. `logs/20260831_WARN.log`: **level=CRITICAL** 2건(표본)
8. `logs/20260831_WARN.log`: **ConstOut** 5건(표본)
9. `logs/20260831_SYSTEM.log`: **ConstOut** 8건(표본)
10. `logs/20260831_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20260831_SIGNAL.log`: **ConstOut** 8건(표본)
12. `logs/20260831_LEARNING.log`: **축퇴** 8건(표본)
13. `logs/20260831_HEALTH.log`: **degraded=ON** 8건(표본)
14. `logs/20260831_HEALTH.log`: **level=CRITICAL** 2건(표본)
15. 미커밋 변경 516건 (실질 2건 · 코드 0건 · EOL 파생 511건)
16. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260831*.log` (Windows) / `grep 강제청산 logs/*20260831*.log`*