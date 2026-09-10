# 미륵이 증거 다이제스트 — 2026-09-09 / POST

- 생성 2026-09-09 16:17:32 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/modest-dreamy-shannon/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260909` · `2026-09-09` · `260909` · `0909`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **27개** 파일 · 27개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260909.txt` | 28B | 09-09 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260909.txt` | 28B | 09-09 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260909.txt` | 209B | 09-09 15:54 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260909.log` | 1.4KB | 09-09 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260909.log` | 217B | 09-09 15:45 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260909.json` | 244B | 09-09 15:40 |
| `launcher_{DATE}_084001_16479.log` | 1 | `logs/Mireuk_batch/launcher_20260909_084001_16479.log` | 18.1MB | 09-09 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260909.log` | 8.6KB | 09-09 12:02 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260909.log` | 21.7KB | 09-09 15:54 |
| `retrain_intraday_{DATE}_093600.log` | 1 | `logs/retrain_intraday_20260909_093600.log` | 2.8KB | 09-09 09:36 |
| `retrain_intraday_{DATE}_103000.log` | 1 | `logs/retrain_intraday_20260909_103000.log` | 2.8KB | 09-09 10:30 |
| `retrain_intraday_{DATE}_110900.log` | 1 | `logs/retrain_intraday_20260909_110900.log` | 2.8KB | 09-09 11:09 |
| `retrain_intraday_{DATE}_114800.log` | 1 | `logs/retrain_intraday_20260909_114800.log` | 2.8KB | 09-09 11:48 |
| `retrain_intraday_{DATE}_141600.log` | 1 | `logs/retrain_intraday_20260909_141600.log` | 2.8KB | 09-09 14:16 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260909.txt` | 43B | 09-09 15:40 |
| `strategy_report_{DATE}_154010.txt` | 1 | `data/daily_reports/strategy_report_20260909_154010.txt` | 2.4KB | 09-09 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260909_DATA.log` | 344.1KB | 09-09 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260909_DEBUG.log` | 234.6KB | 09-09 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260909_HEALTH.log` | 4.6KB | 09-09 14:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260909_HOGA.log` | 49.7MB | 09-09 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260909_LEARNING.log` | 283.1KB | 09-09 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260909_MICRO.log` | 998.8KB | 09-09 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260909_PROBE.log` | 94.6KB | 09-09 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260909_SIGNAL.log` | 602.8KB | 09-09 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260909_SYSTEM.log` | 17.3MB | 09-09 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260909_TRADE.log` | 10.0KB | 09-09 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260909_WARN.log` | 63.9KB | 09-09 15:40 |

## 2. 코드·커밋 상태

- HEAD `5969d44` · 브랜치 `v9-dev` · 미커밋 553건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 548건 (추적변경 550 · 미추적 3 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 3.8시간 · git 프로세스 0개 → **커밋 불가 상태**
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
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
… 외 513건
```

**당일(2026-09-09) 커밋**
```
(당일 커밋 없음 — ⚠ 인덱스락 잔존으로 **커밋 불가 상태였음**. 미조치가 아니다)
```

**최근 커밋 12건**
```
5969d44 [MW0601] 548차 후속: 리포트 제10부 커밋 해시·푸시 결과 기입
909d236 [MW0601] 548차: 장후 자동조치 — 09-08 점검 산출물 커밋 + 스테일 락 회수(코드 변경 없음)
96b0d61 [MW0601] 546차 후속: dev 적응 이식 완료 기록
5a11474 [MW0601] 545·546차: ProfitGuard L1~L4 배지 복구 + 판정 손익을 시스템 자동매매 한정으로
698c4ae [MW0601] 542차 후속: dev 적응 이식 완료 기록
8e04770 [MW0601] 542차 후속: dev 이식 판단 기록 — 수동 맥점 버튼은 보류
a21e270 [MW0601] 542차: 수동 맥점 산출 버튼 (관측 전용, 매매정책 무변경)
91d99da [MW0601] 534차 후속: 첫 라이브 맥점 산출 점검 — 계측 결손 5건 (매매정책 무변경)
3111e4b [MW0601] 542차 곁가지: 540차 GP 교차 피처 NameError — feature_builder 임포트 누락
f2343d8 [MW0601] 541차 후속: 판정기 테스트 — 런타임 DB 부재 시 스킵
3f2b3c6 [MW0601] 541차: GP 교차 채널 판정기 배선 (기록 전용, 매매정책 무변경)
5a5fec1 [MW0601] 540차: GOLDEN POWER 교차 — 사전등록 2채널 배선 (기록 전용, 매매정책 무변경)
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

_본문 미열람(설정): `20260909_HOGA.log` 49.7MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260909.txt`** — 28B · 09-09 15:40:10
```
2026-09-09T15:40:10.635439
```

**`data/daily_close_started_20260909.txt`** — 28B · 09-09 15:40:06
```
2026-09-09T15:40:06.392115
```

**`data/daily_reports/strategy_report_20260909_154010.txt`** — 2.4KB · 09-09 15:40:10
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-09 15:40
========================================================
  버전    : v1.0  (76일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-5.81  MDD(자본대비)=29.9%
  당일      : WR=66.7%  PF=0.33
  롤링20일: 누적 -13579986원  Sh=-5.81  MDD(자본대비)=29.9%  MDD(peak대비)=1094.5%
  당일손익 : broker(gross) -60,000원  수수료 65,600원  net -125,600원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.004 (CLEAR)
  PSI/feat: cvd_delta=0.004  ofi_pressure=0.001  vwap_position=0.053
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -13,500원  승률 50.0%  합계 -269,995원
  등급별 순EV(30일): A=-1,855원(106건,승61%)  BROKER=-5,380,798원(2건,승0%)  C=-2,922원(11건,승73%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=-6,825원(19건)  3m=-9,657원(75건)  5m=+19,891원(21건)  ?=-79,845원(170건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 23분  5일평균 36분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 27.6pt(5일평균 27.2pt)  1분평균변동 0.72pt(5일평균 0.65pt)
--------------------------------------------------------
  진입 퍼널(2026-09-09, 총 370분):
    FLAT 205 → conf미달 134 → CoherenceGate 9 → 게이트차단 16 → 후보 6 → 진입 3
    게이트별: 콜드스타트/기타(RegimeOverride)=4  쿨다운=3  체크리스트항목미달=3  포지션보유중(평가생략)=3  ATR변동성=2  모드필터=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 3건
      └ 상세: JointGateBlock=3
      └ JointGateBlock 3건 (무정보폴백 2건 = 66.7%) [표본 17건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260909.txt`** — 209B · 09-09 15:54:02
```
completed: 2026-09-09 15:54:02
rows: 40824
cols: 97
horizons_replaced: 6/6
t_load_s: 41.5
t_retrain_s: 196.9
t_total_s: 238.9
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260909.txt`** — 43B · 09-09 15:40:25
```
auto_shutdown
2026-09-09T15:40:25.635154
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260909_110900.log`, `retrain_intraday_20260909_114800.log`, `retrain_intraday_20260909_141600.log`, `retrain_intraday_20260909_103000.log`, `20260909_MICRO.log`, `20260909_DATA.log`, `20260909_PROBE.log`, `launcher_20260909_084001_16479.log`_

### `logs/20260909_TRADE.log` — 10.0KB · 78행 · 최종 15:40:07

- 형식 평문 · 시각 인식 78행 · INFO=78

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-09 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-09 13:11:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,114) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-09 13:11:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-09-09 13:18:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,477,114) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-09 14:54:29 [INFO] TRADE: [Chejan] 상태=체결 주문번호=4435 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-09 14:54:29 [INFO] TRADE: [Position] 체결청산 SHORT @ 1116.78 | PnL=-1.97pt (-109,437원) | 하드스톱(틱)
2026-09-09 14:54:29 [INFO] TRADE: [청산 완료] PnL=-1.97pt (-109,437원) | 포지션 합계 -170,873원 (레그 2)
2026-09-09 14:54:30 [INFO] TRADE: [주문요청] 하드스톱(틱) 청산 SHORT 1계약 @ 1116.83 체결대기
2026-09-09 15:40:07 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×78

**컴포넌트 상위 15** — `Chejan`×21, `Position`×13, `주문요청`×9, `Sizer`×8, `JointGateBlock 차단`×3, `진입체크`×3, `체결진입`×3, `체결진입보정`×3, `청산 완료`×3, `ProfitGuard`×2, `MarginCap`×2, `TickTP1`×2, `TP1 부분청산`×2, `TickStop-S0C`×2, `모드필터 차단`×1

### `logs/20260909_WARN.log` — 63.9KB · 321행 · 최종 15:40:09

- 형식 평문 · 시각 인식 314행 · WARNING=314, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-09 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-09-09 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-09-09 08:41:07 [WARNING] SYSTEM: [SessionStateDrop] 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-08 → 2026-09-09)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단이다
2026-09-09 08:41:07 [WARNING] SYSTEM: [SessionStateDrop] 완료 마커 소실 ['eod_retrain_ok_date', 'p8_last_success_date'] — 이 쓰기가 지웠다 (호출부=session_recovery_service.py:159 mtime=08:41:07 남은마커=없음). 호출부가 _read_session_state() 없이 dict 를 새로 만들었을 가능성
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -125600원
════════════════════════════════════════════════════
```

</details>

**WARNING — 태그 35종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 75 | 08:41:06 | 15:33:31 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `SHAP` | 27 | 11:02:01 | 15:02:01 | 슬로우 감지 905ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `ChejanFlow` | 21 | 13:18:01 | 14:54:29 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='3288' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=13:18:00.919' | positi… |
| `ChejanMatch` | 21 | 13:18:01 | 14:54:29 | order_no='3288' | pending='ENTRY:SHORT qty=2 filled=0 order_no=3288 reason=진입 req_at=13:18:00.919' | pending_matched=True |
| `PendingOrder` | 18 | 13:18:00 | 14:54:30 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1110.96, 'reason': '진입', 'hint_source': '', 'atr': 1.2557, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `ScalerRefresh` | 16 | 09:05:00 | 15:07:00 | 5분 누적 수익률 +0.372% (임계 ±0.263%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `CB③-P4` | 16 | 10:18:02 | 15:08:01 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=3.3%) |
| `Health` | 15 | 09:00:01 | 14:39:01 | level=WARNING degraded=OFF | latency=1397ms | quality=1.00 | cache_age=47s | exceptions_10m=0 |
| `PipePerf` | 14 | 09:00:01 | 14:17:04 | total=1397ms | S0=4ms S1=30ms S2=0ms S3=0ms S4=161ms S5=468ms S6=668ms S7=57ms S8=10ms |
| `CB⑤` | 14 | 09:00:01 | 14:17:04 | 파이프라인 1397ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `HealthPolicy` | 6 | 09:01:00 | 14:18:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1397ms quality=1.00 cache=0s exc10m=0) | cause=S6(668ms) |
| `Contrarian` | 6 | 09:58:00 | 15:01:00 | ACTIVE | acc30m=6.7% streak=12 regime=NEUTRAL 역베팅방향=LONG |

**채널** — `SYSTEM`×299, `HEALTH`×15

**컴포넌트 상위 15** — `LiveDBG`×75, `SHAP`×27, `ChejanFlow`×21, `ChejanMatch`×21, `PendingOrder`×18, `ScalerRefresh`×16, `CB③-P4`×16, `Health`×15, `PipePerf`×14, `CB⑤`×14, `-`×7, `HealthPolicy`×6, `Contrarian`×6, `Brier`×6, `EntryFillFlow`×6

### `logs/20260909_SYSTEM.log` — 17.3MB · 131193행 · 최종 15:40:25

- 형식 평문 · 시각 인식 131172행 · INFO=131172, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=24768 | 행감지=30s all_threads=True
2026-09-09 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-09 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-09 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-09 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-08) 종가 버퍼 로드: 365봉
  …
2026-09-09 15:40:10 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-09 15:40:10 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-09 15:40:25 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-09 15:40:25 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-09 15:40:25 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×131172

**컴포넌트 상위 15** — `CybosRT-AUCTION`×125237, `CybosInvestorRaw`×1576, `CybosRT-TICK`×1257, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `System`×98, `MicroRegime`×92, `RegimeFingerprint`×69, `OptionChain`×44, `BalanceUI`×42, `CybosEvent`×42

### `logs/20260909_SIGNAL.log` — 602.8KB · 5290행 · 최종 15:40:07

- 형식 평문 · 시각 인식 5290행 · WARNING=2290, INFO=3000

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
  …
2026-09-09 15:10:00 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-09 15:40:07 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-09 15:40:07 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 81분(21.9%) / DN 23분(6.2%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-09 15:40:07 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-09 age=28m extreme=479 refresh=37 grade_x=128 cb3=0
2026-09-09 15:40:07 [INFO] SIGNAL: [ModelHealth] date=2026-09-09 앙상블유효가동률=76.2% | 파이프라인 370분 | ConstOut 5회/9분 {"3m": {"events": 4, "minutes": 7}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 79분 | 장중재학습 5회 | CB③ ready 144분/370분 (39%) (리셋 2회, 표본손실 60건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1554 | 09:00:02 | 15:07:01 | 1m 'macro_vix' scale=0.0005 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 190 | 09:00:00 | 14:51:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 185 | 09:00:00 | 14:57:00 | ts=08:59 horizon=1m age=1m max_z=+12.77(institution_futures_net) extreme=1 adj=1 |
| `Checklist` | 149 | 09:06:00 | 15:09:00 | 신뢰도 미달 34.9% < 38.5% → 강제 X등급 |
| `ScalerRefresh` | 120 | 08:45:07 | 10:35:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0202) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 79 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 5 | 09:35:00 | 14:15:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 5 | 12:56:00 | 13:00:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `ConfFloorGuard` | 3 | 09:00:00 | 11:20:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3990 (conf_floor=0.330, min_conf=0.399, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5290

**컴포넌트 상위 15** — `ScalerFloor`×1578, `SIGNAL`×740, `Ensemble`×377, `FQAdj`×369, `MetaGate`×356, `ZeroDiag`×352, `Model`×226, `ScalerMonitor`×186, `Checklist`×174, `ScalerRefresh`×162, `ATR-Horizon`×142, `MicroRegime`×92, `차단`×82, `InstabilityGate`×82, `WeightCollapse`×79

### `logs/20260909_LEARNING.log` — 283.1KB · 2757행 · 최종 15:40:07

- 형식 평문 · 시각 인식 2757행 · WARNING=171, INFO=2586

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00194 auc=0.426 out_max=0.3634 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00160 auc=0.518 out_max=0.5009 (기준 auc<0.53 and span<0.020, 기저율=0.5000 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3299 < conf_floor=0.3300 (span=0.00223 auc=0.549 out_max=0.3299, 기저율=0.3286 n=140) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-09 08:40:50 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3394 < conf_floor=0.3300 (n=145) → 보정 재적용
  …
2026-09-09 15:40:07 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-09 15:40:07 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-09 15:40:07 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-09 15:40:07 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-09 15:40:07 [INFO] LEARNING: [Sigma] EOD sigma_20=0.05683% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 170 | 08:40:50 | 15:05:01 | 축퇴 감지 — span=0.00194 auc=0.426 out_max=0.3634 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 1 | 11:47:01 | 11:47:01 | total=976ms raw_fetch=8ms pred_select=33ms pred_update=51ms pred_insert=23ms verified=3 |

**채널** — `LEARNING`×2757

**컴포넌트 상위 15** — `LEARNING`×1215, `SGD`×370, `sigma`×357, `Calibration`×332, `Bias`×141, `Bias⚠`×125, `MetaConf`×78, `ScalerWarmup`×42, `OnlineLearner`×37, `SHAP`×12, `BiasReset`×11, `GBM-64`×10, `GBM`×10, `RF`×6, `ExtremityCorrector`×5

### `logs/20260909_HEALTH.log` — 4.6KB · 31행 · 최종 14:40:01

- 형식 평문 · 시각 인식 31행 · WARNING=15, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1397ms | quality=1.00 | cache_age=47s | exceptions_10m=0
2026-09-09 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=819ms | quality=1.00 | cache_age=106s | exceptions_10m=0
2026-09-09 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 336ms (표본 20분)
2026-09-09 09:37:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2572ms | quality=1.00 | cache_age=63s | exceptions_10m=0
2026-09-09 09:38:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=671ms | quality=1.00 | cache_age=122s | exceptions_10m=0
  …
2026-09-09 13:51:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=406ms | quality=1.00 | cache_age=57s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
2026-09-09 14:17:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3630ms | quality=1.00 | cache_age=151s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-09 14:18:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=420ms | quality=1.00 | cache_age=24s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-09 14:39:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=471ms | quality=1.00 | cache_age=183s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-09-09 14:40:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=584ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 15 | 09:00:01 | 14:39:01 | level=WARNING degraded=OFF | latency=1397ms | quality=1.00 | cache_age=47s | exceptions_10m=0 |

**채널** — `HEALTH`×31

**컴포넌트 상위 15** — `Health`×30, `HealthTrend`×1

### `logs/retrain_eod_20260909.log` — 21.7KB · 147행 · 최종 15:54:03

- 형식 평문 · 시각 인식 147행 · WARNING=10, INFO=137

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 15:50:03,302 [INFO] EOD_RETRAIN: =======================================================
2026-09-09 15:50:03,302 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-09 15:50:03,302 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-09 15:50:03,303 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-09 15:50:03,303 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-09 15:54:03,196 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0805 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-09 15:54:03,196 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1344 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-09 15:54:03,200 [INFO] SIGNAL: [ScalerRefresh] ts=15:54 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-09-09 15:54:03,205 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-09 15:54:03,206 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:52 | 15:52:47 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1502봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-08 14:38:00 ≥ 홀드아웃 시작=2026-09-02 12:41:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-08 14:38 >= holdout_start=2026-09-02 12:41 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-08 … |
| `GuardGhost` | 4 | 15:51:01 | 15:51:17 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-09 13:45:00까지)인데 acc.txt=0.3513는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×66, `SIGNAL`×49, `EOD_RETRAIN`×24, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `GuardGhost`×4, `RegimeFingerprint`×3, `WaitDC`×2

### `logs/retrain_intraday_20260909_093600.log` — 2.8KB · 22행 · 최종 09:36:23

- 형식 평문 · 시각 인식 22행 · INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-09 09:36:00,839 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-09 09:36:00,839 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-09 09:36:00,840 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-09 09:36:00,840 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-09 09:36:00,840 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_eaa5c913.json
  …
2026-09-09 09:36:23,212 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-09 09:36:23,213 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-09 09:36:23,213 [INFO] LEARNING: [Retrain] 완료 | 19.0초 | 성공=1/1 호라이즌
2026-09-09 09:36:23,214 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.4s 데이터=4800행
2026-09-09 09:36:23,216 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_eaa5c913.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -125600원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 3 |
| 진입 등록(`[Position] 진입`) — **엔진** | 3 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 3 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 3 |
| 차단(`[차단]`) | 82 |
| 사이저 호출(`[Sizer]`) | 8 |

### 포지션 3건 · 승 2 (67%) · 합계 -1.20pt (-125,600원)  ※ 레그 6행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 13:18:01 | 엔진 | SHORT | 2 | 3m | 2 | +0.56 | +6,204 | 하드스톱(틱) |
| 13:34:01 | 엔진 | LONG | 2 | 3m | 2 | +1.22 | +39,070 | 하드스톱 |
| 14:47:01 | 엔진 | SHORT | 2 | 5m | 2 | -2.98 | -170,874 | 하드스톱(틱) |

**청산 레그 6행** (부분청산 3 · 전량청산 3)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 13:18:43 | 부분 | 1 | +0.65 | +21,602 | TP1 부분청산 33% |
| 13:20:50 | 전량 | 1 | -0.09 | -15,398 | 하드스톱(틱) |
| 13:35:41 | 부분 | 1 | +0.89 | +33,535 | TP1 부분청산 33% |
| 13:36:00 | 전량 | 1 | +0.33 | +5,535 | 하드스톱 |
| 14:48:01 | 부분 | 1 | -1.01 | -61,437 | 손절1차 조기축소 |
| 14:54:29 | 전량 | 1 | -1.97 | -109,437 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱(틱)`×2, `하드스톱`×1, `손절1차 조기축소`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 3/3건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -125,600 = 포지션합 -125,600 → OK · `[청산 완료]` 3건 = 조립 포지션 3건 → OK

### CB③ 판정 가능 시간 — **144분 / 370분 (39%)**

acc30m 버퍼 리셋 2회 · 그때 버린 표본 60건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 3건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 13:18:01 | SHORT | 2 | 1110.96 | 3m | neutral |
| 13:34:01 | LONG | 2 | 1117.38 | 3m | neutral |
| 14:47:01 | SHORT | 2 | 1114.84 | 5m | neutral |

계약수 분포 — 2계약×3

등급 분포 — `A급(원시C)`×3

**진입한 건들의 체크리스트 미통과 항목** — `fore`×3, `ofi`×2, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×2, **3계약**×6

실제 진입 계약수 — **2계약**×3

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×8

### 차단 사유 82건 · 28종

| 건수 | 사유 |
|---|---|
| 49 | 등급X — 미통과 항목: 2_confidence |
| 3 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.4pt > ATR×5.0=9.4pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.7pt > ATR×5.0=7.5pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.4pt > ATR×5.0=8.0pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.1pt > ATR×5.0=8.0pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=7.8pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.5pt > ATR×5.0=7.3pt (시가=1102.28 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.7pt > ATR×5.0=7.2pt (시가=1102.28 반등위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 169초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 10_chase |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 청산 후 쿨다운 — 0초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×49, `3_vwap`×3, `5_ofi`×3, `4_cvd`×2, `6_foreign`×2, `10_chase`×1, `7_prev_bar`×1, `11_countertrend`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 22건 · 최대 7047ms · 5초 초과 3건

상위 — 7047ms, 5204ms, 5094ms, 4875ms, 4579ms, 4453ms, 4422ms, 4313ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 7047ms | 1397ms | **5650ms (80%)** |
| 11:39:04 | 5094ms | 510ms | **4584ms (90%)** |
| 12:02:04 | 5204ms | 375ms | **4829ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260909_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:09 2026-09-09 15:40:09 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 23분 < 하한 25분 — 최근 5거래일 평균 36분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 24분 · 도달불가 146분 · 재지않음 200분
--- ConstOut ×5(표본)
09:35:00 2026-09-09 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:29:00 2026-09-09 10:29:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:08:01 2026-09-09 11:08:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:47:02 2026-09-09 11:47:02 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×3(표본)
09:00:06 2026-09-09 09:00:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260909.log
11:39:04 2026-09-09 11:39:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260909.log
12:02:04 2026-09-09 12:02:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260909.log
--- [Brier] 과신 ×6(표본)
12:07:00 2026-09-09 12:07:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.356 > 0.35
12:08:00 2026-09-09 12:08:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.354 > 0.35
12:09:00 2026-09-09 12:09:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.350 > 0.35
13:52:00 2026-09-09 13:52:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.355 > 0.35
--- [CB] ×3(표본)
13:20:50 2026-09-09 13:20:50 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
14:48:01 2026-09-09 14:48:01 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
14:54:29 2026-09-09 14:54:29 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×6(표본)
13:20:50 2026-09-09 13:20:50 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:23:50)
13:20:50 2026-09-09 13:20:50 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:23:50)
13:36:00 2026-09-09 13:36:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 13:38:00)
13:36:00 2026-09-09 13:36:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 13:38:00)
--- [SHAP] 슬로우 ×8(표본)
11:02:01 2026-09-09 11:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 905ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:11:01 2026-09-09 11:11:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1134ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:28:01 2026-09-09 11:28:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 936ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:40:01 2026-09-09 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 929ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:10 2026-09-09 08:41:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
09:00:06 2026-09-09 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7047 band=WARN since_pipe_s=0.3
09:01:02 2026-09-09 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2531ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2531 band=INFO since_pipe_s=0.3
09:02:02 2026-09-09 09:02:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2375 band=INFO since_pipe_s=0.2
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260909_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-09 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-09-09 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-09-09 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=105ms fit=38ms total=164ms
09:36:00 2026-09-09 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:07 2026-09-09 15:40:07 [INFO] SYSTEM: [CB③계측] 조건성립 76분 / 판정가능 144분 / 파이프라인 370분 · 그 창 진입 3포지션 · 손익 +45,274원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-09 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:05:00 2026-09-09 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:11:00 2026-09-09 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
09:16:00 2026-09-09 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.005 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:07 2026-09-09 15:40:07 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:07 2026-09-09 15:40:07 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:07 2026-09-09 15:40:07 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 2레그 / 2포지션 중 TP 이벤트 대응 2 · 단일계약 보호전환(설계) 0 · 미대응 0
--- [SchedForceExit] ×1(표본)
15:11:06 2026-09-09 15:11:06 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:10 2026-09-09 15:40:10 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:25 2026-09-09 15:40:25 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:10 2026-09-09 15:40:10 [INFO] SYSTEM: [Notify] ℹ️ [15:40:10] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:10 2026-09-09 15:40:10 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:25 2026-09-09 15:40:25 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260909_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:00:00 2026-09-09 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.3990 (conf_floor=0.330, min_conf=0.399, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:49:00 2026-09-09 10:49:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3808 ≥ 필요 0.3780 (span=0.0120, auc=0.552)
10:55:00 2026-09-09 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3715 < 필요 0.3780 (conf_floor=0.330, min_conf=0.378, span=0.0135, auc=0.560). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:02:00 2026-09-09 11:02:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3787 ≥ 필요 0.3780 (span=0.0181, auc=0.573)
--- ConstOut ×8(표본)
09:35:00 2026-09-09 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-09 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-09 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:02 2026-09-09 09:37:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-09 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-09 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-09 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-09 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:30 2026-09-09 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
--- 안전망 ×8(표본)
09:07:00 2026-09-09 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-09 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-09 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-09 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260909_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00194 auc=0.426 out_max=0.3634 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00160 auc=0.518 out_max=0.5009 (기준 auc<0.53 and span<0.020, 기저율=0.5000 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:50 2026-09-09 08:40:50 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3299 < conf_floor=0.3300 (span=0.00223 auc=0.549 out_max=0.3299, 기저율=0.3286 n=140) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-09 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00184 auc=0.358 out_max=0.2508 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260909_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:07 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260909_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 11 | 08:41:06 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 09:00:01 [WARNING] total=1397ms | S0=4ms S1=30ms S2=0ms S3=0ms S4=161ms S5=468ms S6=668ms S7=57ms S8=10ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 09:00:01 [WARNING] total=1397ms | S0=4ms S1=30ms S2=0ms S3=0ms S4=161ms S5=468ms S6=668ms S7=57ms S8=10ms |
| 10:00 | 장중 초반 | 2 | 09:58:00 [WARNING] ACTIVE | acc30m=6.7% streak=12 regime=NEUTRAL 역베팅방향=LONG |
| 12:00 | 장중 중간점 | 3 | 12:01:01 [WARNING] 슬로우 감지 1060ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| 14:00 | 장중 후반 · 장중 재학습 | 3 | 13:54:02 [WARNING] 과신 경고 | 이동평균=0.351 > 0.35 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 5 | 15:06:00 [WARNING] acc30m 단계 전환: RESTRICTED → WATCH (acc=30.0%) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:40:09 [WARNING] mc-conf 괴리: 금일 진입후보(conf≥mc) 23분 < 하한 25분 — 최근 5거래일 평균 36분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가… |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260909_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 508 | 08:40:33 [INFO] 활성화 | file=logs\crash_fault.log PID=24768 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2911 | 08:49:00 [INFO] code=A0569 raw_time=84900 price=1101.46 cum_vol=1000 auction_code=40 recv_type=50 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5988 | 08:54:00 [INFO] code=A0569 raw_time=85359 price=1101.96 cum_vol=1562 auction_code=40 recv_type=49 |
| 10:00 | 장중 초반 | 4656 | 09:54:01 [INFO] code=A0569 raw_time=95401 price=1115.44 cum_vol=32720 auction_code=40 recv_type=49 |
| 12:00 | 장중 중간점 | 4132 | 11:54:00 [INFO] code=A0569 raw_time=115359 price=1123.42 cum_vol=75309 auction_code=40 recv_type=50 |
| 14:00 | 장중 후반 · 장중 재학습 | 3245 | 13:54:02 [INFO] code=A0569 raw_time=135402 price=1118.16 cum_vol=114339 auction_code=40 recv_type=50 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 2892 | 15:04:00 [INFO] code=A0569 raw_time=150359 price=1118.16 cum_vol=136818 auction_code=40 recv_type=50 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 2137 | 15:12:00 [INFO] code=A0569 raw_time=151200 price=1114.94 cum_vol=138714 auction_code=40 recv_type=49 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 147 | 15:34:00 [INFO] code=A0569 raw_time=153400 price=1117.82 cum_vol=142444 auction_code=40 recv_type=50 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260909_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:07 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0202) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 107 | 08:50:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 223 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0303) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 107 | 09:54:01 [WARNING] 신뢰도 미달 34.3% < 38.5% → 강제 X등급 |
| 12:00 | 장중 중간점 | 81 | 11:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 141 | 13:54:02 [WARNING] 신뢰도 미달 36.4% < 37.4% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 97 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:07 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260908 | 15:40 | 로그 본문 |
| 20260907 | 21:59 | 로그 본문 |
| 20260906 | 20:39 | 로그 본문 |
| 20260904 | 17:33 | 로그 본문 |
| 20260903 | 15:40 | 로그 본문 |
| **중앙값** | **17:33** | 기준선 |
| **오늘 20260909** | **15:40** | 로그 본문 |

- 델타 **-113분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.8MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-09 (MW0601 550차 — 장중 점검)
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
recovery_service.py) 적용은 여전히 사용자 승인 대기, 이 세션은 적용하지
  않음(장전 규약).
- G-1(수집기 git diff 재시도 로직)은 544-6과 통합해 이번 주 내 처리 권고.

### 검증

- 다음 거래일 아침 `[SessionStateDrop]` 재현 여부는 F-1 승인 전까지 계속 관측(O-p2로
  등록, 승인 시 해소 예정).
- TradeInit 무응답 재발 여부는 O-p3로 등록해 오늘 장중부터 관측.

### 병행 세션

이 세션이 도는 동안 병행 세션 없음(당일 커밋 0건, `docs/정기점검/매일점검/` 당일
산출물이 이 리포트가 최초 — `git --no-optional-locks log --since` 및 `ls -lt`로 확인).

## 2026-09-09 (MW0601 550차 — 장중 점검)

### 증상

1. 09:00~12:29 진입 0건 · 차단 46건. 차단 사유 70%(32건)가 `등급X — 2_confidence 미달`.
   `[ConfFloorGuard]`가 09:00 차단 → 10:49 복구 → 10:55 재차단 → 11:02 복구 → 11:20
   재차단, 12:29 기준 복구 로그 없이 차단 유지 중(오실레이션).
2. `.git/index.lock`(0바이트)이 12:28경 재생성. `git_lock_guard.py --check` 12:32:24
   재판정 결과 "판정보류"(나이 228초 ≤ 임계 600초). 세션 자체 git 명령은 전부
   `--no-optional-locks` 확인 완료 — 원인은 `collect_evidence.py` 내부 `git diff`
   호출 실패로 추정(1-2와 동일 계열).
3. 수집기 매분 루프 커버리지 표시가 "56.6%, 12:30~15:10 161분 공백"으로 나왔으나,
   수집 시각이 정오(12:27:51)였을 뿐이고 실제로는 그 시간이 아직 오지 않은 것 — 로그
   생존구간(08:40~12:29) 안에서는 10분 이상 공백 0건.
4. 정체불명 외부 진입(536-1) — 오늘 09:00~12:29 구간 0건(재현 안 됨).
5. TradeInit 무응답(543-1) — 09:00~09:10 구간 0건(재현 안 됨). 근본 원인 미수정이라
   543-1 자체는 닫지 않음.
6. `[SessionStateDrop]`(1-1) — 08:41:07 이후 낮 동안 추가 발생 없음(1회성 현상이라 정상).

### 원인

1은 이미 알려진 531-3(장후 DB 대조, "뚜렷한 이탈 없음, 판정 유보") 연장선 — 오늘
표본만으로 게이트 임계 이상 여부를 확정할 근거 없음(313차 원칙, 장중 라이브 DB 스캔
금지로 이 세션에서는 `predictions` 조회 안 함).
2는 544-5·544-6·1-2(오늘 장전)와 동일 계열 — 근본 원인 조사는 544-6에 이미 등록.
3은 이 스킬의 커버리지 계산 로직이 "경과 시간"이 아니라 "하루 전체(09:00~15:10)"를
분모로 고정해 생기는 계측 착시 — 코드 결함이 아니라 진단 스크립트의 설계 한계.

### 결정

- 1은 "확인 필요"로 기록(P1 아님 — 게이트가 설계대로 작동한 결과일 가능성이 높아
  기준 위반으로 단정하지 않음). 장후 531-3 절차를 이어서 실행하도록 이월.
- 2는 이상점 1-3(P2)으로 신규 번호 부여 — 재발 관측 자체가 새 정보이나 원인 조사는
  중복 등록하지 않음(함정①).
- 3은 이상점으로 올리지 않고 "확인 필요" 절에서 착시임을 명시 + G-2(고도화)로 계측
  개선 제안만 등록.
- 4·5·6은 "이미 반영된 사안"/이월 처리표에서 처분, 신규 조사 없음.
- 코드 변경 없음(장중 규약).

### Why

- 함정①(판정≠결정) — 진입 0건 원인을 성급하게 새 게이트 결함으로 단정하면 531-3의
  기존 유보 판정과 모순된다.
- 계측 4원칙 ③(탈락 가시화) — 매분 루프 "공백"이라는 표현이 실제로는 "아직 안 옴"과
  "정말 빠짐"을 구분하지 못해 정상을 이상으로 판정할 뻔했다.

### How to apply

- G-2(커버리지 계산 "경과 시간" 기준 전환)는 549-4·544-6과 함께 이번 주 내 통합 처리 권고.
- F-1(538-4) 적용은 여전히 사용자 승인 대기, 이 세션은 적용하지 않음(장중 규약).

### 검증

- O-i1: `[ConfFloorGuard]` 15:10까지 재차단/복구 이력 전수 확인 — 장후 판정.
- O-i2: `.git/index.lock` 스테일 확정·회수 여부 — 장후/세션 종료 시 판정.
- O-i3: 진입 0건이 15:10까지 이어지는지 — 장후 531-3 절차로 판정.
- O-i4: 외부 진입 미재현이 15:10까지 이어지는지 — 장후 판정.

### 병행 세션

이 세션이 도는 동안 병행 세션 없음(당일 커밋 0건, `git --no-optional-locks log --since`
및 `ls -lt docs/정기점검/매일점검/`로 재확인 — 이 리포트 파일 외 신규 산출물 없음).

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-04 (MW0601 532차 후속 — 장후 자동조치)
## 2026-09-07 (MW0601 536차 — 장중 점검)
## 2026-09-07 (MW0601 537차 — 장후 점검, 종합 완성본)
## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)
## 2026-09-08 (MW0601 543차 — 장전 점검)
## 2026-09-08 (MW0601 544차 — 장중 점검)
## 2026-09-09 (MW0601 549차 — 장전 점검)
## 2026-09-09 (MW0601 550차 — 장중 점검)
```

미완료 체크박스 **2526건** (끝에서 30건)
```
- [ ] **532-5 (P1 · 승인 대기 / F-1 수정안)** `session_recovery_service.py:120-129
- [ ] **532-6 (P1 · 회귀 테스트 복구)** `tests/test_477_f1_f5_saturation_psi.py::
- [ ] **532-7 (관측 예정 · 09-05 EOD)** `[DynMCDaily]` 가 실제 마감 경로에서 나오는지
- [ ] **532-8 (사용자 조치)** 미륵이 **재기동 필요** — G-1·G-2·G-3 전부 실행 중
- [ ] **532-9 (P2 · 재발방지 / 자가유발)** 커밋 `3c2f17c` 메시지 첫 줄·마지막 줄에
- [ ] **536-1 (P0, 최우선 지속)** 정체불명 외부 진입 — 09-01(47건/50계약)·09-04(최종
- [ ] **536-2 (P2, 고도화 제안)** G-2 — `[ExternalEntry]` 누적 건수 임계 초과 시
- [ ] **536-3 (사용자 조치)** `.git/index.lock` 여전히 미회수 — 이 세션도
- [ ] **537-2 (P2, 신규)** 이상점 1-4 — F-1("session_state 마커 유실") "확정" 판정이
- [ ] **537-3 (P2, 문서 개선 제안)** SKILL.md 함정①(판정≠결정) 게이트에 "사전등록된
- [ ] **537-6 (사용자 조치, 지속)** `.git/index.lock` 여전히 미회수(09:01 생성,
- [ ] **537-7 (참고, 이 세션 소관 아님)** 병행 세션이 오늘 저녁(15:54~16:14) py310_64
- [ ] **537-8 (P2, 정책 제안 — 사용자 지시 시)** G-4 — 모의투자 병행 수동거래를
- [ ] **538-3** (C등급 · 승인 대기) G-2 — 정체불명 외부 진입 누적 건수 단계적 경보 격상.
- [ ] **538-4** (승인 대기) F-1 본체 — `increment_session()` 이 완료 마커 2종을 이어받게
- [ ] **538-5** 09-08 장전 관측(O-t5 대응) — 기동 로그에 `[SessionRollover]` 한 줄이
- [ ] **538-6** 기존 실패 3건 잔존 — `test_477::test_step9_batch_placeholders_match_params`
- [ ] **538-7** 미륵이 재기동 필요 — 538-1 계측은 다음 기동부터 반영된다
- [ ] **543-1 (P0, 신규 / F-1)** `collection/cybos/api_connector.py:430`의 `TradeInit(0)`
- [ ] **543-2 (P2, 고도화 제안)** FZ-1 워치독(`utils/freeze_watchdog.py`)이 첫 하트비트
- [ ] **543-3 (관측 예정, O-p1)** 다음 거래일 `crash_fault.log`에서 `TradeInit`이 다시
- [ ] **543-4 (관측 예정, O-p2)** 다음 거래일 아침 `[SessionStateDrop]`이 재현되는가 —
- [ ] **544-2 (장후 확인 필요)** 09:20:44 청산 이월 레그 1건(-5,024원, 오늘 열림 로그
- [ ] **544-5 (사용자 조치)** `.git/index.lock` 12:27:38 생성 — 12:38 재판정 결과
- [ ] **544-6 (P2, 고도화 제안)** `collect_evidence.py`의 "이 수집 실행은 락을
- [ ] **549-4 (이번 주, G-1)** `collect_evidence.py`의 git diff 측정부에 1회 재시도
- [ ] **O-i1 (장후 판정)** `[ConfFloorGuard]` 12:29 재차단 상태가 15:10까지 어떻게
- [ ] **O-i2 (장후/세션종료 시 판정)** `.git/index.lock`(12:28 생성) 스테일 확정·회수
- [ ] **O-i3 (장후 판정)** 진입 0건이 15:10까지 이어지는가 — 531-3 절차로 `predictions`
- [ ] **O-i4 (장후 판정)** 정체불명 외부 진입(536-1) 미재현이 15:10까지 이어지는가.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 회수 실패(`Operation not permitted`). Windows PC에서 직접
      `del .git\index.lock` 필요. 이 세션의 `branch`/`status`/`log` 명령은 전부
      `--no-optional-locks`를 붙였음을 재확인했다 — 원인은 그쪽이 아니라 12:26:47
      `collect_evidence.py` 실행 중 「실질 변경 건수」 측정용 `git diff` 호출이 실패한
      것으로 추정(다이제스트 §2 "실질 변경 미측정(git diff 실패)"과 시간이 일치).
- [ ] **544-6 (P2, 고도화 제안)** `collect_evidence.py`의 "이 수집 실행은 락을
      만들지 않았다" 자가점검(490차 F-F②)이 544-5의 실패한 `git diff` 호출을 놓쳤을
      가능성 — 자가점검이 diff 실패 **이전** 시점에 판정을 끝내는 구조인지 장후/다음
      세션에서 스크립트 코드로 확인할 것. 급하지 않음.

## 2026-09-09 (MW0601 549차 — 장전 점검)

- [x] **549-1** 이상점 1-1 — `[SessionStateDrop]` 3거래일 연속 재발(09-07·09-08·09-09)
      확인. 신규 조사 없이 재발 사실만 기록(함정① 방지). F-1 본체 적용은 538-4 승계,
      사용자 승인 대기 그대로.
- [x] **549-2** 543-1(TradeInit 24분 무응답, P0) 재현 여부 확인 — 오늘 08:41:06
      `TradeInit 완료 0ms`로 **재현 안 됨**. 다만 근본 원인(타임아웃 가드 부재) 미수정
      상태이므로 543-1 자체는 닫지 않는다. O-p3로 장중 재관측 등록.
- [x] **549-3** 이상점 1-2 — 수집기 `git diff` 측정 실패 재발(544-5·544-6과 동일 계열).
      세션에서 수동 재실행 시 정상 작동 확인(550 files changed, insertions=deletions
      311117로 동일 — 대부분 EOL 차이로 추정, 실내용 변경 아닐 가능성 높음).
- [ ] **549-4 (이번 주, G-1)** `collect_evidence.py`의 git diff 측정부에 1회 재시도
      로직 + 실패 사유 구체화(현재 "git diff 실패"로만 뭉뚱그려짐) 추가. 544-6과
      통합 처리 권고.
- [x] **O-p1 (장중 판정)** `[ConfFloorGuard]` — 09:00 차단→10:49 복구→10:55 재차단→
      11:02 복구→11:20 재차단, 12:29 기준 복구 로그 없이 차단 유지. 완전 해소 아님 —
      오실레이션으로 판정, 지속 승계(O-i1로 장후 재관측 등록).
- [x] **O-p3 (543-1 재이월)** TradeInit 무응답 09:00~09:10 구간 — 재발 0건, 오늘
      구간 한정 해소. 543-1(근본원인 미수정) 자체는 안 닫음.

## 2026-09-09 (MW0601 550차 — 장중 점검)

- [x] **550-1** 09:00~12:29 진입 0건·차단 46건(70%가 confidence 미달) — 531-3 연장선으로
      "확인 필요" 기록, 장후 `predictions` 대조로 판정 이월(313차 원칙, 장중 DB 스캔 금지).
- [x] **550-2** 이상점 1-3(P2, 신규) — `.git/index.lock` 12:28 재생성, 12:32 재판정
      "판정보류"(나이 228초 < 임계 600초). 544-5·544-6과 동일 원인 계열, 신규 조사
      없음. **사용자 조치로 승계** — 세션 종료 시 남아 있으면 Windows에서 스테일 확정
      후(`git_lock_guard.py --check`) 회수 필요.
- [x] **550-3 (G-2, 고도화)** `collect_evidence.py` 매분 루프 커버리지 계산이 "하루
      전체(09:00~15:10)"를 고정 분모로 써서, 장중에 실행하면 "공백"으로 오판되는 착시
      발견(오늘 12:27 실행 시 56.6%·161분 공백으로 표시됐으나 실제 공백 0건). 549-4·
      544-6과 통합해 이번 주 내 "경과 시간만 분모" 로직 추가 권고.
- [ ] **O-i1 (장후 판정)** `[ConfFloorGuard]` 12:29 재차단 상태가 15:10까지 어떻게
      되는가 — 하루 종일 차단이면 P1 격상 검토.
- [ ] **O-i2 (장후/세션종료 시 판정)** `.git/index.lock`(12:28 생성) 스테일 확정·회수
      여부.
- [ ] **O-i3 (장후 판정)** 진입 0건이 15:10까지 이어지는가 — 531-3 절차로 `predictions`
      대조.
- [ ] **O-i4 (장후 판정)** 정체불명 외부 진입(536-1) 미재현이 15:10까지 이어지는가.

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

### `data/heartbeat_MW0601_20260909.json` — 244B · 09-09 15:40:18
```json
{
 "pid": 24768,
 "written_at": "2026-09-09T15:40:18",
 "beat_epoch": 1788936016.4066107,
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

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-09 15:54:03**

| 키 | 값 | 수집 대상일(2026-09-09)과 일치 |
|---|---|---|
| `date` | 2026-09-09 | 예 |
| `p8_last_success_date` | 2026-09-09 | 예 |
| `eod_retrain_ok_date` | 2026-09-09 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 122개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260909-점검리포트.md` | 30.0KB | 09-09 12:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_intra.md` | 62.0KB | 09-09 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_pre.md` | 53.9KB | 09-09 09:01 |
| `docs/정기점검/매일점검/MW0601-20260908-점검리포트.md` | 79.5KB | 09-08 17:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_post.md` | 88.8KB | 09-08 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_intra.md` | 76.5KB | 09-08 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260908_pre.md` | 43.0KB | 09-08 09:02 |
| `docs/정기점검/매일점검/MW0601-20260907-점검리포트.md` | 95.0KB | 09-07 17:42 |

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

1. `.git/index.lock` **스테일 잔존** (0바이트 · 3.8시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. `logs/20260909_WARN.log`: **Traceback** 출현 3건 — 크래시/메모리 계열
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. 포지션 3건 중 최종청산이 하드스톱·손절 계열 **3건(100%)** — 손절 준수율 확인 필요 (레그 6행)
5. 다레그 포지션 **3건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
6. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
7. **SYSTEM 로그가 직전 5거래일 중앙값(17:33)보다 113분 이르게 끝났다** (오늘 15:40) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
8. 메인 스레드 정지 5초 초과 **3건** (최대 7047ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
9. `logs/20260909_WARN.log`: **[Brier] 과신** 6건(표본)
10. `logs/20260909_WARN.log`: **ConstOut** 5건(표본)
11. `logs/20260909_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20260909_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20260909_SIGNAL.log`: **ConstOut** 8건(표본)
14. `logs/20260909_LEARNING.log`: **축퇴** 8건(표본)
15. 미커밋 변경 553건 (실질 2건 · 코드 0건 · EOL 파생 548건)
16. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260909*.log` (Windows) / `grep 강제청산 logs/*20260909*.log`*