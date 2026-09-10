# 미륵이 증거 다이제스트 — 2026-09-10 / POST

- 생성 2026-09-10 16:19:04 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/jolly-wizardly-mayer/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260910` · `2026-09-10` · `260910` · `0910`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260910.txt` | 28B | 09-10 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260910.txt` | 28B | 09-10 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260910.txt` | 209B | 09-10 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260910.log` | 2.0KB | 09-10 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260910.log` | 433B | 09-10 15:45 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260910.json` | 244B | 09-10 15:40 |
| `launcher_{DATE}_084000_3710.log` | 1 | `logs/Mireuk_batch/launcher_20260910_084000_3710.log` | 1.7MB | 09-10 15:36 |
| `launcher_{DATE}_153720_19944.log` | 1 | `logs/Mireuk_batch/launcher_20260910_153720_19944.log` | 24.1KB | 09-10 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260910.log` | 5.7KB | 09-10 14:45 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260910.log` | 22.0KB | 09-10 15:53 |
| `retrain_intraday_20260629_{DATE}58.log` | 1 | `logs/retrain_intraday_20260629_091058.log` | 3.6KB | 06-29 09:11 |
| `retrain_intraday_{DATE}_093601.log` | 1 | `logs/retrain_intraday_20260910_093601.log` | 2.8KB | 09-10 09:36 |
| `retrain_intraday_{DATE}_102801.log` | 1 | `logs/retrain_intraday_20260910_102801.log` | 2.8KB | 09-10 10:28 |
| `retrain_intraday_{DATE}_113601.log` | 1 | `logs/retrain_intraday_20260910_113601.log` | 2.8KB | 09-10 11:36 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260910.txt` | 43B | 09-10 15:40 |
| `strategy_report_{DATE}_154004.txt` | 1 | `data/daily_reports/strategy_report_20260910_154004.txt` | 2.2KB | 09-10 15:40 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260910_BACKFILL.log` | 0B | 09-10 07:06 |
| `{DATE}_DATA.log` | 1 | `logs/20260910_DATA.log` | 335.2KB | 09-10 15:19 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260910_DEBUG.log` | 237.1KB | 09-10 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260910_HEALTH.log` | 6.7KB | 09-10 15:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20260910_HOGA.log` | 38.5MB | 09-10 15:20 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260910_LEARNING.log` | 467.5KB | 09-10 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260910_MICRO.log` | 769.8KB | 09-10 15:19 |
| `{DATE}_PROBE.log` | 1 | `logs/20260910_PROBE.log` | 121.8KB | 09-10 15:38 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260910_SIGNAL.log` | 742.9KB | 09-10 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260910_SYSTEM.log` | 692.1KB | 09-10 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260910_TRADE.log` | 13.8KB | 09-10 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260910_WARN.log` | 123.4KB | 09-10 15:40 |

## 2. 코드·커밋 상태

- HEAD `da66651` · 브랜치 `v9-dev` · 미커밋 559건 · 실질 변경 3건 · 코드(.py) 0건 · EOL 파생 546건 (추적변경 549 · 미추적 10 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/정기점검/수익률향상_누적대장.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
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
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/settings.py
 M config/strategy_params.py
 M config/strategy_registry.py
 M dashboard/main_dashboard.py
… 외 519건
```

**당일(2026-09-10) 커밋**
```
da66651 [MW0601] 555차 후속2: 출처축(P0)·차트 Y축(P1)·라벨 레지스트리(P2) + GP 마커 재지정
106f6e2 [MW0601] 555차 병합: GP 청산 패널 갱신 트리거 + 출처축 화이트리스트
c08128f [MW0601] 555차 후속: 손익 추이 「출처」축을 화이트리스트로 뒤집음 — 모르는 라벨은 auto 가 아니다
c91d591 [MW0601] 555차: GP 가상 청산이 손익 추이 패널을 갱신하지 않던 결함 — run_shadow 반환값 신설
bd33401 [MW0601] 554차: 테스트가 심은 유령 포지션 — 격리 2겹 + 복원 가드 + 대조 축 분리
f6ac416 [MW0601] 553차 후속4: GP 병행운용 Phase 4 — 수익 판넬 「GP(가상)」 구분
fec531c [MW0601] 553차 후속3: GP 병행운용 Phase 3 — 도전자 2종 배선 + 관측 개시(2026-09-10)
c384f8c [MW0601] 553차 후속2: ma_basis=cont 확정 + GP 병행운용 Phase 2(엔진 결함 5건)
a791389 [MW0601] 553차 후속: GP 병행운용 Phase 1 — MA20/MA60 배선 + 죽은 지표 교체
70ebd33 [MW0601] 553차: GP 규칙 병행운용 Phase 0 — 사전등록(비용 CYBOS·CREON 분리) + 차트 GP 마커
900edc0 [MW0601] 552차 후속: 호가깊이 검증·결함3건 + 중복축약(Phase 3-0) + 재시작이 지운 상태 2종(552-10·11)
```

**최근 커밋 12건**
```
da66651 [MW0601] 555차 후속2: 출처축(P0)·차트 Y축(P1)·라벨 레지스트리(P2) + GP 마커 재지정
106f6e2 [MW0601] 555차 병합: GP 청산 패널 갱신 트리거 + 출처축 화이트리스트
c08128f [MW0601] 555차 후속: 손익 추이 「출처」축을 화이트리스트로 뒤집음 — 모르는 라벨은 auto 가 아니다
c91d591 [MW0601] 555차: GP 가상 청산이 손익 추이 패널을 갱신하지 않던 결함 — run_shadow 반환값 신설
bd33401 [MW0601] 554차: 테스트가 심은 유령 포지션 — 격리 2겹 + 복원 가드 + 대조 축 분리
f6ac416 [MW0601] 553차 후속4: GP 병행운용 Phase 4 — 수익 판넬 「GP(가상)」 구분
fec531c [MW0601] 553차 후속3: GP 병행운용 Phase 3 — 도전자 2종 배선 + 관측 개시(2026-09-10)
c384f8c [MW0601] 553차 후속2: ma_basis=cont 확정 + GP 병행운용 Phase 2(엔진 결함 5건)
a791389 [MW0601] 553차 후속: GP 병행운용 Phase 1 — MA20/MA60 배선 + 죽은 지표 교체
70ebd33 [MW0601] 553차: GP 규칙 병행운용 Phase 0 — 사전등록(비용 CYBOS·CREON 분리) + 차트 GP 마커
900edc0 [MW0601] 552차 후속: 호가깊이 검증·결함3건 + 중복축약(Phase 3-0) + 재시작이 지운 상태 2종(552-10·11)
7d77377 [MW0601] 550차: 풀타임 수집 첫 3거래일 점검 — 헤더 28 코드 40 오판 정정 + 15:34 봉 시간 기준 플러시
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

_본문 미열람(설정): `20260910_HOGA.log` 38.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260910.txt`** — 28B · 09-10 15:40:04
```
2026-09-10T15:40:04.723929
```

**`data/daily_close_started_20260910.txt`** — 28B · 09-10 15:40:02
```
2026-09-10T15:40:02.975337
```

**`data/daily_reports/strategy_report_20260910_154004.txt`** — 2.2KB · 09-10 15:40:04
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-10 15:40
========================================================
  버전    : v1.0  (77일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-1.82  MDD(자본대비)=29.9%
  당일      : WR=100.0%  PF=999.00
  롤링20일: 누적 -5951093원  Sh=-1.82  MDD(자본대비)=29.9%  MDD(peak대비)=928.5%
  당일손익 : broker(gross) +485,000원  수수료 42,174원  net +7,384,826원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)
  PSI/feat: 미측정
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +359,020원  승률 60.0%  합계 +7,180,399원
  등급별 순EV(30일): A=+69,139원(98건,승61%)  BROKER=-2,574,591원(4건,승50%)  C=+20,159원(8건,승75%)  MANUAL=-18,190원(166건,승49%)
  호라이즌별 순EV(30일): 1m=-8,067원(18건)  3m=-9,501원(65건)  5m=+30,034원(19건)  ?=-35,568원(174건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 53분  5일평균 32분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 29.5pt(5일평균 28.4pt)  1분평균변동 0.71pt(5일평균 0.65pt)
--------------------------------------------------------
  진입 퍼널(2026-09-10, 총 369분):
    FLAT 209 → conf미달 95 → CoherenceGate 12 → 게이트차단 53 → 후보 0 → 진입 0
    게이트별: 게이트강등(기타)=18  시가갭(OPEN_VOLATILE)=14  체크리스트항목미달=9  ATR변동성=9  게이트강등(Toxicity)=2  Degraded신뢰도=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260910.txt`** — 209B · 09-10 15:53:44
```
completed: 2026-09-10 15:53:44
rows: 40819
cols: 97
horizons_replaced: 6/6
t_load_s: 35.1
t_retrain_s: 184.2
t_total_s: 219.8
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260910.txt`** — 43B · 09-10 15:40:19
```
auto_shutdown
2026-09-10T15:40:19.730588
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260910_093601.log`, `retrain_intraday_20260910_102801.log`, `retrain_intraday_20260910_113601.log`, `20260910_MICRO.log`, `20260910_DATA.log`, `20260910_PROBE.log`, `launcher_20260910_084000_3710.log`, `launcher_20260910_153720_19944.log`_

### `logs/20260910_TRADE.log` — 13.8KB · 91행 · 최종 15:40:04

- 형식 평문 · 시각 인식 91행 · WARNING=4, INFO=87

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:41 [WARNING] TRADE: [Position] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75)
2026-09-10 08:40:41 [WARNING] TRADE: [PositionDiag] restore source=open_position:LONG saved_at=2026-09-10T08:02:01.249426 last_update_ts=2026-09-10T08:02:01.249426
2026-09-10 08:40:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-10 08:45:21 [INFO] TRADE: [TickTP1] TP1 처리 (틱) LONG tick=1109.60 tp1=1041.50 qty=2
2026-09-10 08:45:21 [INFO] TRADE: [주문요청] TP1 청산 LONG 1계약 @ 1109.6 체결대기
  …
2026-09-10 13:37:02 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,814,783) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-10 13:39:02 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,814,783) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-10 14:41:20 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-10 15:38:00 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-10 15:40:04 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Position` | 2 | 08:40:41 | 12:17:52 | 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75) |
| `PositionDiag` | 1 | 08:40:41 | 08:40:41 | restore source=open_position:LONG saved_at=2026-09-10T08:02:01.249426 last_update_ts=2026-09-10T08:02:01.249426 |
| `PositionFallback` | 1 | 12:17:52 | 12:17:52 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=2 entry=1109.42 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×91

**컴포넌트 상위 15** — `Sizer`×37, `증거금부족 차단`×23, `Chejan`×8, `Position`×6, `ProfitGuard`×5, `주문요청`×4, `TickTP1`×2, `TP1 부분청산`×2, `청산 완료`×2, `PositionDiag`×1, `PositionFallback`×1

### `logs/20260910_WARN.log` — 123.4KB · 637행 · 최종 15:40:04

- 형식 평문 · 시각 인식 627행 · CRITICAL=2, ERROR=4, WARNING=621, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:41 [WARNING] SYSTEM: [Position] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75)
2026-09-10 08:40:41 [WARNING] SYSTEM: [Position] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75)
2026-09-10 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-10 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-10 08:40:50 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 2031ms account=333044256
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +7384826원
════════════════════════════════════════════════════
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `Armistice` | 2 | 12:18:01 | 14:42:02 | 🔴 개장 30분 초과 고착 — 자동진입 전면 차단 중 (time_ok=False sync=0/2 broker_verified=True block_new_entries=False) — 2026-08-31 47분 전 구간 차단 사고와 동일 양식 |
| CRITICAL | `BrokerSync` | 1 | 12:17:52 | 12:17:52 | startup sync 완료: FLAT -> SHORT 2계약 @ 1109.42 |
| ERROR | `BrokerSync` | 1 | 12:17:52 | 12:17:52 | 🔴 재기동해 보니 계좌에 포지션이 남아 있다 — SHORT 2계약 @ 1109.42 (재기동 전 엔진 상태: FLAT). 미륵이가 이번 세션에 낸 자리가 아니다. 전일 미청산이거나 HTS·MTS 등 다른 경로에서 들어온 자리다. 지금 계좌를 직접 확인할 것 — 손절선은 참조 ATR 로 임시 배정돼 있고, 의도한 자리가 아니면 수동 청산이 자동 손절보다 빠르다 |
| CRITICAL | `Health` | 1 | 14:24:09 | 14:24:09 | level=CRITICAL degraded=OFF | latency=8109ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[Contrarian]×1 |
| ERROR | `NetRecon` | 1 | 15:40:04 | 15:40:04 | 🔴 net 불일치 — 엔진 +7,384,826원 vs 브로커 +463,281원 (잔차 +6,921,545원, 허용 ±5,000) |

<details><summary>ERROR/Armistice 원문 2건</summary>

```
2026-09-10 12:18:01 [ERROR] SYSTEM: [Armistice] 🔴 개장 30분 초과 고착 — 자동진입 전면 차단 중 (time_ok=False sync=0/2 broker_verified=True block_new_entries=False) — 2026-08-31 47분 전 구간 차단 사고와 동일 양식
2026-09-10 14:42:02 [ERROR] SYSTEM: [Armistice] 🔴 개장 30분 초과 고착 — 자동진입 전면 차단 중 (time_ok=False sync=2/2 broker_verified=True block_new_entries=False) — 2026-08-31 47분 전 구간 차단 사고와 동일 양식
```

</details>

<details><summary>CRITICAL/BrokerSync 원문 1건</summary>

```
2026-09-10 12:17:52 [CRITICAL] SYSTEM: [BrokerSync] startup sync 완료: FLAT -> SHORT 2계약 @ 1109.42
```

</details>

<details><summary>ERROR/BrokerSync 원문 1건</summary>

```
2026-09-10 12:17:52 [ERROR] SYSTEM: [BrokerSync] 🔴 재기동해 보니 계좌에 포지션이 남아 있다 — SHORT 2계약 @ 1109.42 (재기동 전 엔진 상태: FLAT). 미륵이가 이번 세션에 낸 자리가 아니다. 전일 미청산이거나 HTS·MTS 등 다른 경로에서 들어온 자리다. 지금 계좌를 직접 확인할 것 — 손절선은 참조 ATR 로 임시 배정돼 있고, 의도한 자리가 아니면 수동 청산이 자동 손절보다 빠르다
```

</details>

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-09-10 14:24:09 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=8109ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[Contrarian]×1
```

</details>

**WARNING — 태그 36종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 337 | 09:47:36 | 15:38:28 | paintEvent slow 31.0ms | size=1756x917 candles=20 grid=16.0 spans=0.0 candles=15.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `LiveDBG` | 96 | 08:40:48 | 15:38:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Health` | 23 | 09:00:01 | 14:23:07 | level=WARNING degraded=OFF | latency=1753ms | quality=0.86 | cache_age=64s | exceptions_10m=1 | exc_tags=[Armistice]×1 |
| `MarginBlock` | 23 | 10:04:00 | 11:34:02 | SHORT 신규주문가능수량=0 — 증거금 부족 추정, 진입 차단 (산출수량=1) |
| `HealthPolicy` | 17 | 09:01:01 | 15:09:06 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1753ms quality=0.86 cache=0s exc10m=1) | cause=S6(886ms) |
| `ScalerRefresh` | 14 | 09:05:00 | 14:50:03 | 5분 누적 수익률 +0.504% (임계 ±0.224%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PipePerf` | 12 | 09:00:01 | 14:24:09 | total=1753ms | S0=4ms S1=15ms S2=0ms S3=0ms S4=90ms S5=709ms S6=886ms S7=45ms S8=5ms |
| `CB⑤` | 10 | 09:00:01 | 11:37:03 | 파이프라인 1753ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `BrokerSync` | 8 | 08:40:50 | 12:17:52 | balance result rows=0 nonempty=0 summary_nonblank=True probe_nonblank=True summary={'총매매': '35351502', '총평가손익': '35351502', '실현손익': '0', '총평가': '0.00', '총평가수익률': '35351502', '추정자산': '-60000'} |
| `PendingOrder` | 8 | 08:45:21 | 12:18:00 | set {'kind': 'EXIT_PARTIAL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 1109.6, 'reason': 'TP1 부분청산 33%', 'hint_source': '', 'atr': 0.0, 'grade': '', 'stage': 1, 'order_no': '', 'f… |
| `ChejanFlow` | 8 | 08:45:21 | 12:18:00 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='37' | pending='EXIT_PARTIAL:LONG qty=1 filled=0 order_no=? reason=TP1 부분청산 33% req_at=08:45:21… |
| `ChejanMatch` | 8 | 08:45:21 | 12:18:00 | order_no='37' | pending='EXIT_PARTIAL:LONG qty=1 filled=0 order_no=37 reason=TP1 부분청산 33% req_at=08:45:21.749' | pending_matched=True |

**채널** — `SYSTEM`×603, `HEALTH`×24

**컴포넌트 상위 15** — `ChartDBG`×337, `LiveDBG`×96, `Health`×24, `MarginBlock`×23, `HealthPolicy`×17, `ScalerRefresh`×14, `PipePerf`×12, `BrokerSync`×10, `CB⑤`×10, `-`×9, `PendingOrder`×8, `ChejanFlow`×8, `ChejanMatch`×8, `CB③-P4`×6, `PartialExitAttempt`×4

### `logs/20260910_SYSTEM.log` — 692.1KB · 5215행 · 최종 15:40:19

- 형식 평문 · 시각 인식 5181행 · INFO=5181, PLAIN=34

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:30 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=20116 | 행감지=30s all_threads=True
2026-09-10 08:40:31 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-10 08:40:31 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-10 08:40:31 [INFO] SYSTEM: 미륵이 초기화
2026-09-10 08:40:31 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-09) 종가 버퍼 로드: 384봉
  …
2026-09-10 15:40:04 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-10 15:40:04 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-10 15:40:19 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-10 15:40:19 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-10 15:40:19 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5181

**컴포넌트 상위 15** — `CybosInvestorRaw`×1510, `CybosRT-TICK`×509, `BAR-CLOSE`×394, `CVD-ANCHOR`×394, `CybosRT-ROLLOVER`×393, `TickUI`×386, `S6Detail`×369, `PipePerf`×369, `System`×117, `MicroRegime`×85, `CybosSub`×70, `RegimeFingerprint`×68, `BalanceUI`×48, `OptionChain`×45, `CybosDailyPnl`×32

### `logs/20260910_SIGNAL.log` — 742.9KB · 6215행 · 최종 15:40:04

- 형식 평문 · 시각 인식 6215행 · WARNING=2482, INFO=3733

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
  …
2026-09-10 15:37:57 [INFO] SIGNAL: [TimeRouter] 월물 만기 당일 — 신뢰도↑ 사이즈×0.6
2026-09-10 15:38:02 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
2026-09-10 15:40:04 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-10 15:40:04 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-10 age=30m extreme=961 refresh=42 grade_x=0 cb3=0
2026-09-10 15:40:04 [INFO] SIGNAL: [ModelHealth] date=2026-09-10 앙상블유효가동률=미측정 | 파이프라인 0분 | ConstOut 0회/0분 | WeightCollapse 0분 | 장중재학습 0회 | CB③ ready 0분/0분 (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1764 | 09:00:01 | 14:50:03 | 1m 'macro_vix' scale=0.0126 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 230 | 09:01:00 | 14:42:02 | 1m 극단 z-score 9개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 191 | 09:01:00 | 14:52:00 | ts=09:00 horizon=1m age=1m max_z=+4.70(microprice_bias) extreme=9 adj=3 |
| `Checklist` | 122 | 09:06:00 | 15:07:00 | 신뢰도 미달 34.9% < 38.5% → 강제 X등급 |
| `WeightCollapse` | 79 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 78 | 08:45:21 | 14:50:03 | 1m CORE 'cvd_divergence' raw_std≈0(0.0108) → identity(0,1) 강제 (FLAT 100% 방지) |
| `MetaGate` | 6 | 12:23:01 | 14:51:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `ConfFloorGuard` | 5 | 09:00:00 | 14:42:02 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `PCR-Dampen` | 4 | 09:14:01 | 09:29:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConstOut` | 3 | 09:35:00 | 11:35:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |

**채널** — `SIGNAL`×6215

**컴포넌트 상위 15** — `ScalerFloor`×1818, `SIGNAL`×738, `MetaGate`×527, `ProfitGuard`×397, `Ensemble`×378, `FQAdj`×366, `ZeroDiag`×316, `Model`×272, `Checklist`×196, `ScalerMonitor`×192, `ATR-Horizon`×147, `ToxicityGate`×147, `ScalerRefresh`×126, `차단`×105, `MicroRegime`×85

### `logs/20260910_LEARNING.log` — 467.5KB · 3813행 · 최종 15:40:04

- 형식 평문 · 시각 인식 3813행 · WARNING=673, INFO=3140

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 08:40:32 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.485 out_max=0.2626 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과
2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00278 auc=0.280 out_max=0.4636 (기준 auc<0.53 and span<0.020, 기저율=0.4625 n=80) → 보정 미적용, raw 통과
2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2881 < conf_floor=0.3300 (span=0.00101 auc=0.573 out_max=0.2881, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-10 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00020 auc=0.530 out_max=0.2716 (n=140) → 보정 재적용
  …
2026-09-10 15:40:04 [INFO] LEARNING: [DriftAdjuster] 표본 부족(n=0 < 15) — acc=50.0% 반영 스킵, alpha=0.01000 유지
2026-09-10 15:40:04 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-10 15:40:04 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-10 15:40:04 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-10 15:40:04 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 671 | 08:40:33 | 15:37:55 | 축퇴 감지 — span=0.00013 auc=0.485 out_max=0.2626 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 2 | 14:24:05 | 14:50:02 | total=4905ms raw_fetch=2114ms pred_select=3ms pred_update=1633ms pred_insert=0ms verified=3 |

**채널** — `LEARNING`×3813

**컴포넌트 상위 15** — `Calibration`×1320, `LEARNING`×1193, `SGD`×369, `sigma`×330, `Bias⚠`×218, `Bias`×126, `MetaConf`×71, `OnlineLearner`×67, `ScalerWarmup`×48, `SHAP`×13, `BiasReset`×12, `ExtremityCorrector`×11, `Consolidator`×9, `RF`×7, `GBM-64`×6

### `logs/20260910_HEALTH.log` — 6.7KB · 41행 · 최종 15:01:01

- 형식 평문 · 시각 인식 41행 · CRITICAL=1, WARNING=23, INFO=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1753ms | quality=0.86 | cache_age=64s | exceptions_10m=1 | exc_tags=[Armistice]×1
2026-09-10 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=884ms | quality=0.86 | cache_age=123s | exceptions_10m=1 | exc_tags=[Armistice]×1
2026-09-10 09:02:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=619ms | quality=0.74 | cache_age=183s | exceptions_10m=1 | exc_tags=[Armistice]×1
2026-09-10 09:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=524ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[Armistice]×1
2026-09-10 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 388ms (표본 20분)
  …
2026-09-10 14:18:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=389ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[Contrarian]×1
2026-09-10 14:23:07 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=349ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[Contrarian]×1
2026-09-10 14:24:09 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=8109ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[Contrarian]×1
2026-09-10 14:25:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=627ms | quality=1.00 | cache_age=112s | exceptions_10m=2 | exc_tags=[CB]×1 [Contrarian]×1
2026-09-10 15:01:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 398ms (표본 20분)
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 14:24:09 | 14:24:09 | level=CRITICAL degraded=OFF | latency=8109ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[Contrarian]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-09-10 14:24:09 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=8109ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[Contrarian]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 23 | 09:00:01 | 14:23:07 | level=WARNING degraded=OFF | latency=1753ms | quality=0.86 | cache_age=64s | exceptions_10m=1 | exc_tags=[Armistice]×1 |

**채널** — `HEALTH`×41

**컴포넌트 상위 15** — `Health`×38, `HealthTrend`×3

### `logs/retrain_eod_20260910.log` — 22.0KB · 151행 · 최종 15:53:44

- 형식 평문 · 시각 인식 151행 · WARNING=14, INFO=137

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-10 15:50:03,872 [INFO] EOD_RETRAIN: =======================================================
2026-09-10 15:50:03,873 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-10 15:50:03,873 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-10 15:50:03,873 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-10 15:50:03,873 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-10 15:53:44,888 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0699 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-10 15:53:44,889 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1235 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-10 15:53:44,892 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.07s
2026-09-10 15:53:44,896 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.07s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-10 15:53:44,897 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:46 | 15:52:31 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1504봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-09 14:38:00 ≥ 홀드아웃 시작=2026-09-03 12:37:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-09 14:38 >= holdout_start=2026-09-03 12:37 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-09 … |
| `ScalerRefresh` | 6 | 15:53:44 | 15:53:44 | 1m CORE 'ofi_norm' raw_std≈0(0.0308) → identity(0,1) 강제 (FLAT 100% 방지) |
| `GuardGhost` | 2 | 15:50:53 | 15:50:53 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-10 11:05:00까지)인데 acc.txt=0.3579는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×64, `SIGNAL`×55, `EOD_RETRAIN`×24, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `ScalerRefresh`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×3, `WaitDC`×2

### `logs/retrain_intraday_20260629_091058.log` — 3.6KB · 33행 · 최종 09:11:32

- 형식 평문 · 시각 인식 33행 · INFO=33

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-06-29 09:10:58,464 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-29 09:10:58,465 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-06-29 09:10:58,465 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-29 09:10:58,465 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_825a7e04.json
2026-06-29 09:11:01,245 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-06-29 09:11:31,997 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.54s | old_acc=0.0000)
2026-06-29 09:11:32,000 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-06-29 09:11:32,000 [INFO] LEARNING: [Retrain] 완료 | 30.8초 | 성공=6/6 호라이즌
2026-06-29 09:11:32,001 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 33.5s 데이터=20000행
2026-06-29 09:11:32,002 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_825a7e04.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +7384826원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 105 |
| 사이저 호출(`[Sizer]`) | 37 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|

**출처별 소계** — 

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**이월 포지션(전일 이전 진입) 추정 — 청산 레그 4행 · +148.54pt · +7,384,826원**

> 🔴 **위 포지션 표 합계(+0원)에 이 금액은 들어 있지 않다.** 오늘 로그에 여는 이벤트(`[Position] 진입` 또는 FLAT→보유 체결)가 없는 청산 레그라 포지션으로 조립되지 않는다 — **데이터 손실이 아니라 귀속 불가**이며, 금액 자체는 체결 실측이라 정확하다.
>
> **오늘 계좌에서 실제로 오간 돈 = +7,384,826원** (오늘 연 포지션 +0원 + 이월분 +7,384,826원). 판정 원천은 여전히 브로커 실측 net 이다(493차 F-1) — 이 줄은 로그 축의 교차확인용이다.
>
> ⚠ 이월분이 있다는 것은 **전 거래일이 FLAT 으로 끝나지 않았다는 뜻**이다 — 절대원칙 §1(15:10 강제청산) 위반 여부를 전일 리포트로 확인할 것.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 08:45:22 | 이월 | 1 | +69.60 | +3,469,797 | TP1 부분청산 33% |
| 08:45:22 | 이월 | 1 | +69.24 | +3,451,797 | TP2(전량) |
| 12:17:53 | 이월 | 1 | +4.78 | +228,116 | TP1 부분청산 33% |
| 12:18:00 | 이월 | 1 | +4.92 | +235,116 | TP2(전량) |

**청산 레그 0행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 +7,384,826 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 2건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패(이월 추정) 레그 4행 · +7,384,826원 ⚠** — 위 「이월 포지션」 블록 참조, **헤드라인 합계에 미포함**

### CB③ 판정 가능 시간 — **0분 / 0분 (—)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×6, **2계약**×6, **3계약**×25

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×36, `conf=0.8 regime=0.8 safe=1.00`×1

### 차단 사유 105건 · 42종

| 건수 | 사유 |
|---|---|
| 33 | 등급X — 미통과 항목: 2_confidence |
| 9 | 게이트 강등 X — ProfitGuard 진입 차단 ([L2-Tier4] Tier 4: 중단 임계 500,000원 도달로 당일 영구 중단) (체크리스트 등급=A… |
| 6 | 게이트 강등 X — ProfitGuard 진입 차단 ([L2-Tier4] Tier 4: 중단 임계 500,000원 도달로 당일 영구 중단) (체크리스트 등급=C… |
| 4 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 4 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 4 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.1pt > ATR×5.0=10.7pt (시가=1108.92 반등위험) |
| 1 | 게이트 강등 X — ToxicityGate action=block (score=0.60 ma=0.36) (체크리스트 등급=A, 통과 11개) |
| 1 | 게이트 강등 X — ToxicityGate action=block (score=0.52 ma=0.37) (체크리스트 등급=C, 통과 8개) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.6pt > ATR×5.0=12.0pt (시가=1108.92 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.5pt > ATR×5.0=11.9pt (시가=1108.92 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.2pt > ATR×5.0=12.0pt (시가=1108.92 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.5pt > ATR×5.0=13.1pt (시가=1108.92 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.2pt > ATR×5.0=12.8pt (시가=1108.92 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×33, `3_vwap`×9, `4_cvd`×5, `7_prev_bar`×5, `5_ofi`×3, `6_foreign`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 7건

- `5분 진입 정지 | 파이프라인 8109ms — 처리 지연 (임계=5000ms)` ×2
- `일시 정지 해제 — 정상 복귀` ×2
- `일간 리셋 완료` ×2
- `×1 [Contrarian]×1` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 22건 · 최대 9469ms · 5초 초과 2건

상위 — 9469ms, 5344ms, 4344ms, 4219ms, 4187ms, 4140ms, 4094ms, 4063ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 14:24:09 | 9469ms | 8109ms | **1360ms (14%)** |
| 14:45:13 | 5344ms | 483ms | **4861ms (91%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260910_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:04 2026-09-10 15:40:04 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 32분/일 < 하한 60분 — 금일 53분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- ConstOut ×3(표본)
09:35:00 2026-09-10 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:27:01 2026-09-10 10:27:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:35:00 2026-09-10 11:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- PSI ×1(표본)
15:40:02 2026-09-10 15:40:02 [WARNING] SYSTEM: [RegimeFingerprint] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerprint] 기준선 키 불일치` WARNING 이 기동 로그에 있는지 먼저 확인할 것
--- Traceback ×2(표본)
14:24:09 2026-09-10 14:24:09 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260910.log
14:45:13 2026-09-10 14:45:13 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260910.log
--- [CB] ×2(표본)
14:24:09 2026-09-10 14:24:09 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 8109ms — 처리 지연 (임계=5000ms)
14:24:09 2026-09-10 14:24:09 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 8109ms — 처리 지연 (임계=5000ms)
--- [ExitCooldown] ×8(표본)
08:45:22 2026-09-10 08:45:22 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 08:47:22)
08:45:22 2026-09-10 08:45:22 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 08:47:22)
12:18:00 2026-09-10 12:18:00 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 12:20:00)
12:18:00 2026-09-10 12:18:00 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 12:20:00)
--- [SHAP] 슬로우 ×1(표본)
12:10:02 2026-09-10 12:10:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1011ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- level=CRITICAL ×1(표본)
14:24:09 2026-09-10 14:24:09 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=8109ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[Contrarian]×1
--- 메인 스레드 블로킹 ×8(표본)
09:00:02 2026-09-10 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.2
09:37:03 2026-09-10 09:37:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4094ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4094 band=INFO since_pipe_s=0.0
10:03:02 2026-09-10 10:03:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2329ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2329 band=INFO since_pipe_s=0.0
10:29:04 2026-09-10 10:29:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4344ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4344 band=INFO since_pipe_s=0.0
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260910_SYSTEM.log`
```
--- CIRCUIT ×2(표본)
14:24:09 2026-09-10 14:24:09 [INFO] SYSTEM: [Notify] 🚨 [14:24:09] [미륵이] Circuit Breaker 발동!
14:24:09 2026-09-10 14:24:09 [INFO] SYSTEM: [Notify] 🚨 [14:24:09] [미륵이] Circuit Breaker 발동!
--- ConstOut ×8(표본)
09:35:00 2026-09-10 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-09-10 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-09-10 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=110ms fit=90ms total=220ms
09:36:01 2026-09-10 09:36:01 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:04 2026-09-10 15:40:04 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 0분 / 파이프라인 0분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-10 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:06:00 2026-09-10 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:12:00 2026-09-10 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:17:01 2026-09-10 09:17:01 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
--- [CB] ×4(표본)
14:30:01 2026-09-10 14:30:01 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
14:30:01 2026-09-10 14:30:01 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
15:40:04 2026-09-10 15:40:04 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:04 2026-09-10 15:40:04 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:26 2026-09-10 15:11:26 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:04 2026-09-10 15:40:04 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:19 2026-09-10 15:40:19 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:04 2026-09-10 15:40:04 [INFO] SYSTEM: [Notify] ℹ️ [15:40:04] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:04 2026-09-10 15:40:04 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:19 2026-09-10 15:40:19 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260910_SIGNAL.log`
```
--- CIRCUIT ×1(표본)
14:28:01 2026-09-10 14:28:01 [INFO] SIGNAL: [차단] Circuit Breaker PAUSED — 진입 불가 (CB 해제까지 대기)
--- ConfFloorGuard ×8(표본)
09:00:00 2026-09-10 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4290 (conf_floor=0.330, min_conf=0.429, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:36:00 2026-09-10 10:36:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3884 ≥ 필요 0.3780 (span=0.0074, auc=0.545)
13:00:08 2026-09-10 13:00:08 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3588 < 필요 0.3740 (conf_floor=0.330, min_conf=0.374, span=0.0081, auc=0.557). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
13:11:08 2026-09-10 13:11:08 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3822 ≥ 필요 0.3740 (span=0.0048, auc=0.535)
--- ConstOut ×7(표본)
09:35:00 2026-09-10 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:37:03 2026-09-10 09:37:03 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:27:01 2026-09-10 10:27:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:27:01 2026-09-10 10:27:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-10 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-10 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-10 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-10 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.415
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.429
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:28 2026-09-10 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
--- 안전망 ×8(표본)
09:07:00 2026-09-10 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-10 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-10 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-10 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260910_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:33 2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.485 out_max=0.2626 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과
08:40:33 2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00278 auc=0.280 out_max=0.4636 (기준 auc<0.53 and span<0.020, 기저율=0.4625 n=80) → 보정 미적용, raw 통과
08:40:33 2026-09-10 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2881 < conf_floor=0.3300 (span=0.00101 auc=0.573 out_max=0.2881, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:33 2026-09-10 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00020 auc=0.530 out_max=0.2716 (n=140) → 보정 재적용
```

### `logs/20260910_HEALTH.log`
```
--- [CB] ×1(표본)
14:25:01 2026-09-10 14:25:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=627ms | quality=1.00 | cache_age=112s | exceptions_10m=2 | exc_tags=[CB]×1 [Contrarian]×1
--- [ExitCooldown] ×8(표본)
12:18:02 2026-09-10 12:18:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=757ms | quality=1.00 | cache_age=25s | exceptions_10m=6 | exc_tags=[BrokerSync]×2 [Armistice]×1 [ExitCooldown]×1 외 2종
12:19:00 2026-09-10 12:19:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=428ms | quality=1.00 | cache_age=83s | exceptions_10m=6 | exc_tags=[BrokerSync]×2 [Armistice]×1 [ExitCooldown]×1 외 2종
12:20:01 2026-09-10 12:20:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=415ms | quality=1.00 | cache_age=144s | exceptions_10m=7 | exc_tags=[Armistice]×2 [BrokerSync]×2 [ExitCooldown]×1 외 2종
12:21:00 2026-09-10 12:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=320ms | quality=1.00 | cache_age=20s | exceptions_10m=7 | exc_tags=[Armistice]×2 [BrokerSync]×2 [ExitCooldown]×1 외 2종
--- level=CRITICAL ×1(표본)
14:24:09 2026-09-10 14:24:09 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=8109ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[Contrarian]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260910_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 14 | 08:40:41 [WARNING] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75) |
| 10:00 | 장중 초반 | 8 | 10:02:01 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,351,502) 기본리스크=1,500,000 신뢰도배수=0.8 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:38:00 [INFO] 설정 업데이트 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260910_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 40 | 08:40:41 [WARNING] 이전 포지션 복원: LONG 2계약 @ 1040.0 (손절=1037.75) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 11 | 09:54:00 [WARNING] level=WARNING degraded=OFF | latency=452ms | quality=1.00 | cache_age=180s | exceptions_10m=0 |
| 12:00 | 장중 중간점 | 1 | 11:59:01 [WARNING] 5분 누적 수익률 -0.228% (임계 ±0.141%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 14:00 | 장중 후반 · 장중 재학습 | 5 | 13:55:43 [WARNING] paintEvent slow 31.0ms | size=1558x996 candles=271 grid=0.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 69 | 15:04:01 [WARNING] settings.py 핫리로드 실패: cannot import name 'SYSTEM_ENTRY_SOURCES' from 'config.constants' (C:\Users\82108\Pychar… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 44 | 15:12:32 [WARNING] paintEvent slow 32.0ms | size=1886x996 candles=363 grid=16.0 spans=0.0 candles=0.0 dir=0.0 regime=16.0 marker… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 24 | 15:38:02 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260910_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:30 [INFO] 활성화 | file=logs\crash_fault.log PID=20116 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 116 | 08:49:02 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 159 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 172 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 155 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 152 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 136 | 15:04:01 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 77 | 15:12:01 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 90 | 15:36:26 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:36:26 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260910_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:45:21 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0108) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 132 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0342) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 266 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0393) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 291 | 09:54:00 [WARNING] 신뢰도 미달 37.9% < 38.5% → 강제 X등급 |
| 12:00 | 장중 중간점 | 199 | 11:55:01 [WARNING] 신뢰도 미달 44.0% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 165 | 13:54:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=8, group=short) | VWAP pos=+2.000 need <0 (SHORT) bull_exh=0.00 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 48 | 15:04:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 21 | 15:37:41 [INFO] 기동 복원: OPEN_VOLATILE  0.600 → 0.415 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260909 | 15:40 | 로그 본문 |
| 20260908 | 15:40 | 로그 본문 |
| 20260907 | 21:59 | 로그 본문 |
| 20260906 | 20:39 | 로그 본문 |
| 20260904 | 17:33 | 로그 본문 |
| **중앙값** | **17:33** | 기준선 |
| **오늘 20260910** | **15:40** | 로그 본문 |

- 델타 **-113분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.9MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### B. 🔴 급소는 브로커 net 대사였다 — 분리 합성으로 해결
### C. 가시화 (계측 4원칙 ④)
### D. 반사실 탭에는 GP 를 넣지 않는다
### E. 데이터 공급
### F. 검증
### G. 553차 전체 완료 — 남은 것은 관측뿐
## 2026-09-10 (MW0601 554차 — 장전 점검)
### 그 외 이상점 (P1·P2)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
.0" logs/*_TRADE.log`(2026-05-02~
2026-09-10 전체 로그 보유 범위) = 0건, `grep "손절=1037\.75"` = 0건 — 엔진이 이 포지션을
스스로 진입 기록한 적이 단 한 번도 없다. 청산 시 `[Chejan] 상태=체결`(주문번호 37·38)은
실재하므로 브로커 계좌에 실제로 존재했던 포지션이며 표시 오류·데이터 조작은 아니다.
`data/position_state.json`은 청산 직후 값(FLAT)으로 이미 덮어써져 있어 이전 세대 스냅샷이
없다 — 원인 규명에 필요한 "언제 이 포지션이 열렸는가" 증거가 소실된 상태.

**후보 가설 (미확정, 우선순위 순)**:
1. 2026-09-07(536-1)~537-1과 같은 성격 — 사용자 본인의 모의투자 병행 수동 테스트 거래.
   다만 그때는 엔진이 살아있는 동안 `[체결동기화] 외부진입`으로 실시간 감지됐던 반면,
   오늘은 엔진 기동 **이전**에 이미 존재하던 포지션이라 그 감지 경로 자체를 타지 않았다
   (감지 사각지대 — G-2로 등록).
2. 552-11(entry_source 오귀속 수정, 오늘 00:45 `900edc0` 배포)이 다루지 않은 변종.
   552-11은 "엔진이 한 번은 진입을 기록했는데 재시작이 라벨을 지운" 경우를 고쳤다.
   오늘 사례는 "엔진이 애초에 진입 자체를 기록한 적이 없는" 경우라 수정 범위 밖일
   가능성.
3. 야간 선물시장(KRX night session) 거래 — 미검증.

**결정**: 장중 라이브 DB 분석 금지 구간(CLAUDE.md)이라 이번 세션에서는 `trades.db`·
`predictions.db` 조회로 원인을 좁히지 않았다. 장후 세션에서 ① `trades.entry_source`·
`entry_ts`(552-11 수정 후 정상 승계됐다면 유의미) ② 브로커 실측 이력(`CpTd6197`) 대조
③ 사용자 확인(536-1 방식과 동일) 순으로 원인을 좁힐 것.

**Why**: 이 사건은 「출처를 모르는 손익이 안전장치(ProfitGuard) 판정 축에 섞여
안전장치 자체를 오작동시킨」 사례로, FP-CRITICAL 죽은 게이트·TOX 죽은 섀도·552-10
브로커 net 롤오버 오염과 같은 계열("아무도 안 본 축"·"기준점을 잃음")이다. 다만 이번
것은 **판정 결과가 낙관이 아니라 비관 방향**(거래를 더 해야 하는데 못 하게 막힘)이라는
점에서 앞선 사례들과 다르다 — 항상 낙관 방향으로만 틀어진다는 552-10/11 표의 패턴이
깨진 최초 사례일 수 있다(추가 관찰 필요).

**How to apply**: 리포트 §2 F-1(ProfitGuard Tier 판정에서 entry_source 미상 포지션
제외)·F-2(entry_source 없는 포지션 복원 시 경고 로그 신설) 참조. 장후 원인 확정 후
세부 설계.

**검증**: 오늘 이월 포지션 사례를 회귀 테스트 픽스처로 등록 예정(장후). 원인 확정
전까지는 코드 변경 없음 — 관찰만.

### 그 외 이상점 (P1·P2)

- `[SessionStateDrop]` 08:40:51 재발(538-4 미승인 지속) — 09-09 O-t1 판정: 재발 확인.
  어제 EOD·P8은 `logs/retrain_eod_20260909.log` 15:54:03 원본으로 정상 성공 직접
  확인(마커 소실이 실제 실패를 의미하지 않음, 계측 4원칙 ②).
- `.git/index.lock` 09:01 생성, 09:10 재확인 시점 나이 543초로 판정보류 지속
  (임계 600초). 이 세션의 git 명령은 전부 `--no-optional-locks` 사용 확인, 수집기
  자가진단도 "이 수집 실행은 락을 만들지 않았다" — 원인 세션 밖(라이브 launcher 또는
  병행 프로세스) 추정. 549-4(git diff 측정 실패, 이번 회차도 재현: 미커밋 548건 실질
  변경 미측정)와 시간대 겹침 — 직접 인과는 미확정.
- `[ConfFloorGuard]` 09:00:00 재현(O-t3 대응) — 09-09 관측대로 간헐 패턴 지속.
  오늘은 1-1로 인해 ProfitGuard Tier4가 이미 전면 차단 중이라 실질 영향은 이중차단
  상태로 없음.

**신규 조사 불필요 항목(함정① 확인 완료)**: 552-11(entry_source 오귀속)·536-1/537-1
(정체불명 외부 진입 원인 규명)·CB② 값 복원(519차)·TOX-SEVERE-SPREAD 26주 이관(489차)
전부 이미 반영 확인 — grep으로 실물 코드/커밋 확인 후 리포트 "이미 반영된 사안" 절에
등재, 신규 Fix로 올리지 않았다.

**설정 불변식**: 24개 항목 전부 `일치`. 차단 게이트 34개 중 9개 꺼짐 — 전부 CLAUDE.md
등재 한시예외와 일치. 신규 이탈 없음.

산출물: `docs/정기점검/매일점검/MW0601-20260910-점검리포트.md`(신규),
`docs/정기점검/매일점검/evidence_MW0601-20260910_pre.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-07 (MW0601 538차 후속 — 장후 자동조치)
## 2026-09-08 (MW0601 543차 — 장전 점검)
## 2026-09-08 (MW0601 544차 — 장중 점검)
## 2026-09-09 (MW0601 549차 — 장전 점검)
## 2026-09-09 (MW0601 550차 — 장중 점검)
## 2026-09-09 (MW0601 551차 — 장후 점검, 종합 완성본)
## 2026-09-10 (MW0601 554차 — 장전 점검)
## 2026-09-10 (MW0601 — 장중 점검)
```

미완료 체크박스 **2563건** (끝에서 30건)
```
- [ ] **543-4 (관측 예정, O-p2)** 다음 거래일 아침 `[SessionStateDrop]`이 재현되는가 —
- [ ] **544-2 (장후 확인 필요)** 09:20:44 청산 이월 레그 1건(-5,024원, 오늘 열림 로그
- [ ] **544-5 (사용자 조치)** `.git/index.lock` 12:27:38 생성 — 12:38 재판정 결과
- [ ] **544-6 (P2, 고도화 제안)** `collect_evidence.py`의 "이 수집 실행은 락을
- [ ] **549-4 (이번 주, G-1)** `collect_evidence.py`의 git diff 측정부에 1회 재시도
- [ ] **O-i1 (장후 판정)** `[ConfFloorGuard]` 12:29 재차단 상태가 15:10까지 어떻게
- [ ] **O-i2 (장후/세션종료 시 판정)** `.git/index.lock`(12:28 생성) 스테일 확정·회수
- [ ] **O-i3 (장후 판정)** 진입 0건이 15:10까지 이어지는가 — 531-3 절차로 `predictions`
- [ ] **O-i4 (장후 판정)** 정체불명 외부 진입(536-1) 미재현이 15:10까지 이어지는가.
- [ ] **O-t1 (내일 장전 판정)** `[SessionStateDrop]` 재발 여부 + F-1(538-4) 승인 여부.
- [ ] **O-t2 (다음 세션 시작 시 판정)** `.git/index.lock` 사용자 조치 완료 여부 —
- [ ] **O-t3 (내일 장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부.
- [ ] **O-t4 (5거래일 누적 또는 26주 WFA 판정)** 오늘 케이스3 유형(conf가 min_conf 근소
- [ ] **554-1 (P0, 신규 / F-1)** ProfitGuard Tier4 판정에서 `entry_source`가 없거나
- [ ] **554-2 (P1, 신규 / F-2)** 포지션 복원 시 `entry_source is None`이면
- [ ] **554-3 (확인 필요, 장후)** 554-1 이월 포지션의 실제 출처 규명 — 장중 라이브 DB
- [ ] **554-4 (P2, 고도화 제안 / G-1)** `position_state.json` 덮어쓰기 전 회전 백업
- [ ] **554-5 (P2, 고도화 제안 / G-2)** `[ExternalEntry]`류 외부 진입 감지를 "엔진
- [ ] **O-p2 (장후 판정)** ProfitGuard Tier4 당일 영구 중단이 15:10까지 유지되는가
- [ ] **O-p3 (다음 세션 장전 판정)** `[SessionStateDrop]` 재발 지속 여부 + F-1(538-4)
- [ ] **O-p4 (오늘 중 재확인)** `.git/index.lock`(09:01 생성) 스테일 확정·회수 여부 —
- [ ] **O-p5 (장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부(09:00:00 재현
- [ ] **F-3 (P0, 신규)** 장중 브로커 잔고 주기적 재대사(5~10분 간격) 신설 — 기동 시
- [ ] **F-4 (P1, 신규)** `[UnreconciledExit]`(554차 신설) 발동 조건 재검토 — 오늘
- [ ] **G-3 (고도화)** 재기동 시 엔진-브로커 상태 불일치 발견 이벤트를 별도 카운터로
- [ ] **O-i1 (장후 판정)** 12:17 재기동의 실제 원인(사용자 수동 재시작 여부) 확인.
- [ ] **O-i2 (장후 판정)** `trades.db`의 08:45 허구 2레그(+6,921,594원) + 12:17~12:18
- [ ] **O-i3 (장후 판정)** ProfitGuard Tier4 당일 영구 중단 15:10까지 유지 확정(O-p2 계승).
- [ ] **O-i4 (장후 판정)** `[UnreconciledExit]`이 12:17~12:18 청산에서 실제로 평가됐는지
- [ ] **O-i5 (장후 재확인)** 매분 루프 커버리지 12:30~15:10 공백은 이번 점검이 15:10
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 554차 후속.
- [ ] **554-4 (P2, 고도화 제안 / G-1)** `position_state.json` 덮어쓰기 전 회전 백업
      (`position_state_prev.json` 등) 도입 — 오늘 원인 조사 시 이전 세대 스냅샷이
      전혀 없어 진입 시점을 특정할 수 없었다. 552-10·552-11과 같은 "재시작이 상태를
      지운다" 계열.
- [ ] **554-5 (P2, 고도화 제안 / G-2)** `[ExternalEntry]`류 외부 진입 감지를 "엔진
      기동 전 이미 존재하던 포지션"까지 확장 — 현재 감지 경로는 엔진이 살아있는 동안의
      실시간 체결만 보므로, 오늘처럼 기동 전 포지션은 사각지대. 536-2(기존 제안)와
      통합 검토.
- [x] **O-p1 판정 예정 등록** 554-3과 동일(이월 포지션 원출처) — 장후.
- [ ] **O-p2 (장후 판정)** ProfitGuard Tier4 당일 영구 중단이 15:10까지 유지되는가
      — `[진입체크]`·`[Position] 진입` 로그 15:10까지 0건이면 "하루 종일 차단" 확정.
      ⚠ **[554-D 이후] 관측 조건이 바뀌었다** — 12:28 장부 정정으로 `sys=+0원` 이 돼 재시동하면 Tier4 래치가 풀린다. "15:10까지 유지" 를 그대로 판정하지 말 것 — 재시동 시각을 명시해 전/후로 나눠 읽을 것.
- [ ] **O-p3 (다음 세션 장전 판정)** `[SessionStateDrop]` 재발 지속 여부 + F-1(538-4)
      승인 여부.
- [ ] **O-p4 (오늘 중 재확인)** `.git/index.lock`(09:01 생성) 스테일 확정·회수 여부 —
      `git_lock_guard.py --check` 나이 600초 초과 후 재판정.
- [ ] **O-p5 (장후 판정)** `[ConfFloorGuard]` 오실레이션 패턴 지속 여부(09:00:00 재현
      확인됨).

## 2026-09-10 (MW0601 — 장중 점검)

- [x] **O-p1 조기 해소** 이월 포지션 원출처 — 09:38 `bd33401` 커밋으로 규명 완료(테스트
      오염). 아래는 그 후속 발견.
- [ ] **F-3 (P0, 신규)** 장중 브로커 잔고 주기적 재대사(5~10분 간격) 신설 — 기동 시
      1회 동기화만으로는 엔진-브로커 상태 불일치를 놓친다. 오늘(1-5) 3시간32분간
      미인식 SHORT 2계약이 무방비로 방치됐다가 우연한 재기동으로만 발견됨.
      `collection/broker/cybos_broker.py` · `strategy/runtime/broker_runtime_service.py`
      후보. 섀도(로그만) 선행 후 경보 승격.
- [ ] **F-4 (P1, 신규)** `[UnreconciledExit]`(554차 신설) 발동 조건 재검토 — 오늘
      12:17~12:18 청산에서 로그 미발견. "즉시 verified=True로 대조된 뒤 청산" 경로가
      이 경보를 우회하는지 코드 확인 필요.
- [ ] **G-3 (고도화)** 재기동 시 엔진-브로커 상태 불일치 발견 이벤트를 별도 카운터로
      누적 기록 — F-3 적용 전 임시 안전판.
- [ ] **O-i1 (장후 판정)** 12:17 재기동의 실제 원인(사용자 수동 재시작 여부) 확인.
- [ ] **O-i2 (장후 판정)** `trades.db`의 08:45 허구 2레그(+6,921,594원) + 12:17~12:18
      실제 SHORT 청산 2레그(+463,232원) 정리·표시 방식 확정.
- [ ] **O-i3 (장후 판정)** ProfitGuard Tier4 당일 영구 중단 15:10까지 유지 확정(O-p2 계승).
- [ ] **O-i4 (장후 판정)** `[UnreconciledExit]`이 12:17~12:18 청산에서 실제로 평가됐는지
      코드 확인(F-4와 연계).
- [ ] **O-i5 (장후 재확인)** 매분 루프 커버리지 12:30~15:10 공백은 이번 점검이 15:10
      이전(12:34)에 실행된 데 따른 것 — 장후 재집계로 정상 확인.
- [x] **O-i6** `.git/index.lock`(12:28 재생성, 이상점 1-7) — STALE 확정됨(재확인 시
      나이 0.2시간·git 프로세스 0개). 단 `--reclaim` 시도 시 `Operation not permitted`로
      회수 실패(샌드박스 마운트 권한 제약, 2026-08-26 SKILL.md 기록과 동일 계열) —
      **사용자가 Windows에서 직접 삭제 필요**(장중 리포트 사용자 조치 7번).
      `collect_evidence.py --phase intra` 실행 시각(12:28:14)과 정확히 겹침 — 549-4
      (git diff 측정 실패)와 인과 확인 필요(장후로 이월).

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

### `data/heartbeat_MW0601_20260910.json` — 244B · 09-10 15:40:03
```json
{
 "pid": 13780,
 "written_at": "2026-09-10T15:40:03",
 "beat_epoch": 1789022402.9753375,
 "beat_age_sec": 0.4,
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

- 파일 최종 기록: **09-10 15:53:44**

| 키 | 값 | 수집 대상일(2026-09-10)과 일치 |
|---|---|---|
| `date` | 2026-09-10 | 예 |
| `p8_last_success_date` | 2026-09-10 | 예 |
| `eod_retrain_ok_date` | 2026-09-10 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 126개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260910-점검리포트.md` | 52.5KB | 09-10 12:40 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_intra.md` | 69.2KB | 09-10 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_pre.md` | 56.9KB | 09-10 09:01 |
| `docs/정기점검/매일점검/MW0601-20260909-점검리포트.md` | 62.1KB | 09-09 16:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_post.md` | 78.6KB | 09-09 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_intra.md` | 62.0KB | 09-09 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260909_pre.md` | 53.9KB | 09-09 09:01 |
| `docs/정기점검/매일점검/MW0601-20260908-점검리포트.md` | 79.5KB | 09-08 17:35 |

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

1. `logs/20260910_WARN.log`: ERROR 이상 6건
2. `logs/20260910_WARN.log`: **Traceback** 출현 2건 — 크래시/메모리 계열
3. `logs/20260910_HEALTH.log`: ERROR 이상 1건
4. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
5. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건) — 차단 105건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
6. **SYSTEM 로그가 직전 5거래일 중앙값(17:33)보다 113분 이르게 끝났다** (오늘 15:40) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
7. 메인 스레드 정지 5초 초과 **2건** (최대 9469ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
8. `logs/20260910_WARN.log`: **level=CRITICAL** 1건(표본)
9. `logs/20260910_WARN.log`: **ConstOut** 3건(표본)
10. `logs/20260910_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260910_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260910_SIGNAL.log`: **ConstOut** 7건(표본)
13. `logs/20260910_LEARNING.log`: **축퇴** 8건(표본)
14. `logs/20260910_HEALTH.log`: **level=CRITICAL** 1건(표본)
15. 미커밋 변경 559건 (실질 3건 · 코드 0건 · EOL 파생 546건)
16. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260910*.log` (Windows) / `grep 강제청산 logs/*20260910*.log`*