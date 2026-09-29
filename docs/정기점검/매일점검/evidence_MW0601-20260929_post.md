# 미륵이 증거 다이제스트 — 2026-09-29 / POST

- 생성 2026-09-29 16:17:57 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01ptvbpvc7odnaoh6gy55ol2/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260929` · `2026-09-29` · `260929` · `0929`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20260929.log` | 137B | 09-29 07:22 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260929.txt` | 28B | 09-29 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260929.txt` | 28B | 09-29 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260929.txt` | 233B | 09-29 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260929.log` | 1.4KB | 09-29 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260929.log` | 217B | 09-29 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260929.json` | 245B | 09-29 15:46 |
| `launcher_{DATE}_084000_23300.log` | 1 | `logs/Mireuk_batch/launcher_20260929_084000_23300.log` | 2.2MB | 09-29 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260929.log` | 3.1KB | 09-29 14:05 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20260929.log` | 1.3KB | 09-29 16:10 |
| `position_state.json.gen_{DATE}_143900` | 1 | `data/position_state.json.gen_20260929_143900` | 1.5KB | 09-29 14:39 |
| `position_state.json.gen_{DATE}_143911` | 1 | `data/position_state.json.gen_20260929_143911` | 1.5KB | 09-29 14:39 |
| `position_state.json.gen_{DATE}_143922` | 1 | `data/position_state.json.gen_20260929_143922` | 1.6KB | 09-29 14:39 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260929.log` | 20.6KB | 09-29 15:53 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260929.txt` | 43B | 09-29 15:47 |
| `strategy_report_{DATE}_154020.txt` | 1 | `data/daily_reports/strategy_report_20260929_154020.txt` | 2.4KB | 09-29 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260929_DATA.log` | 436.4KB | 09-29 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260929_DEBUG.log` | 242.5KB | 09-29 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260929_HEALTH.log` | 5.7KB | 09-29 14:41 |
| `{DATE}_HOGA.log` | 1 | `logs/20260929_HOGA.log` | 51.7MB | 09-29 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260929_LEARNING.log` | 297.8KB | 09-29 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260929_MICRO.log` | 968.4KB | 09-29 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260929_PROBE.log` | 94.6KB | 09-29 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260929_REGULAR_COLLECT.log` | 6.6KB | 09-29 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260929_SIGNAL.log` | 533.7KB | 09-29 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260929_SYSTEM.log` | 956.1KB | 09-29 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20260929_TRADE.log` | 25.0KB | 09-29 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260929_WARN.log` | 598.2KB | 09-29 15:46 |

## 2. 코드·커밋 상태

- HEAD `f1efe56` · 브랜치 `v9-dev` · 미커밋 23건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
 M docs/신동거래/신동_사전등록_20260924.md
 M scripts/shindong_scorecard.py
 M strategy/shindong/daily_report.py
 M strategy/shindong/engine.py
 M strategy/shindong/mireuk_runner.py
 M strategy/shindong/spec.py
 M tests/test_626_shindong.py
 M tests/test_632_shindong_x4nf.py
?? dev_memory/_tmp_append_20260929.txt
?? dev_memory/_tmp_append_todo_20260929.txt
?? docs/신동거래/신동_개정_v2_1차목표역전_20260929.md
?? docs/신동거래/일일/신동_일일_MW0601_20260929.md
?? docs/신동거래/일일/신동_일일_MW0601_20260929.svg
?? docs/정기점검/매일점검/MW0601-20260929-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20260929_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260929_pre.md
?? tests/test_639_shindong_v2_target_inversion.py
```

**당일(2026-09-29) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
f1efe56 [MW0601] 632차 후속5: MW0602 적용가이드 §10 대응 — 신동 재현 테스트를 PC별로 가르고 불변식으로 보강 + §11 답변
b851e32 [MW0601] 632차 후속4: 신동 일일 리포트 — 파일명·제목·메일에 PC명 표기
b8e9047 [MW0601] 632차 후속: 신동 일일 리포트 — 거래 흐름+손익 vs 섀도 흐름+손익 · PDF · 메일 자동 발송
ba09d5a [MW0602] 적용가이드 §8~§10: MW0602 실행 결과 + 별건 확인요청
1c4afed [MW0601] 636차 후속: 장후 자동조치 — 고도화 방안 2·3·4 (DB pruning 롤백 사실 기록 · 락 이름변경 우회 · md 제목 손상 경고)
ff07de8 [MW0601] 632차: 신동 R3 레슨런 딥다이브 → 섀도 SHADOW_X4NF · SHADOW_TR44 + 채점표 R1 적중률
c2d5eee [MW0601] 631차: Claude 앱 — 19:20 업데이트 창이 VS Code Claude Code 까지 죽이던 것 수정 + 절전 해제 시 앱 자동 복구
91f5afe [MW0601] 631차: PC 종료→절전 해제→Cybos Plus→미륵이 실전 흐름 확인 기록 (1차 로그인 37초·DB 초기화 0.4초)
ddcddef [MW0601] 631차 딥다이브2 후속: Cybos 연결 확인을 매번 새 프로세스로 — 자동로그인이 성공을 실패로 오판해 세션을 끊던 원인
b7b274b [MW0601] 631차 딥다이브2: 15:58 기동 실패 — 금요일 종료 작업이 최대 절전이라 Cybos 세션만 끊긴 채 CpStart 생존
da5a604 [MW0601] 631차 후속: GP 분석 캐시를 GP_test/ 로 분리 — 파일은 남기고 미추적 목록에서만 숨김
3d68065 [MW0601] 631차 후속: git 밖 작업 코드 6개 — 섀도 게이트·피터 수집기·롤 정책 대조 (라이브 미배선)
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

### 차단 게이트 전수 인벤토리 — 40개 중 **9개 꺼짐**

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
| `OPTION_BOOK_ENABLED` | True | — |
| `SHINDONG_DAILY_REPORT_ENABLED` | True | — |
| `SHINDONG_ENABLED` | True | — |
| `SHINDONG_REPORT_MAIL_ENABLED` | True | — |
| `SHINDONG_RUNNER_SHADOW_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260929_HOGA.log` 51.7MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260929.txt`** — 28B · 09-29 15:40:20
```
2026-09-29T15:40:20.386604
```

**`data/daily_close_started_20260929.txt`** — 28B · 09-29 15:40:09
```
2026-09-29T15:40:09.307640
```

**`data/daily_reports/strategy_report_20260929_154020.txt`** — 2.4KB · 09-29 15:40:20
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-29 15:40
========================================================
  버전    : v1.0  (88일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-2.33  MDD(자본대비)=29.9%
  당일      : WR=62.5%  PF=0.74
  롤링20일: 누적 -7538874원  Sh=-2.33  MDD(자본대비)=29.9%  MDD(peak대비)=0.0%
  당일손익 : broker(gross) +52,000원  수수료 159,000원  net -107,000원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.000  vwap_position=0.025
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +4,729원  승률 55.0%  합계 +94,588원
  등급별 순EV(30일): A=+114,088원(58건,승59%)  BROKER=-2,574,591원(4건,승50%)  MANUAL=-27,752원(139건,승46%)
  호라이즌별 순EV(30일): 1m=-62원(9건)  3m=+8,712원(38건)  5m=-70,557원(9건)  ?=-49,892원(145건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 60분  5일평균 33분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 19.2pt(5일평균 24.7pt)  1분평균변동 0.69pt(5일평균 0.54pt)
--------------------------------------------------------
  진입 퍼널(2026-09-29, 총 370분):
    FLAT 178 → conf미달 123 → CoherenceGate 9 → 게이트차단 51 → 후보 9 → 진입 8
    게이트별: 체크리스트항목미달=14  콜드스타트/기타(DataAnomalyGate)=11  포지션보유중(평가생략)=11  쿨다운=10  모드필터=3  ATR변동성=1  마감시간(신규진입금지)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 1건
      └ 상세: JointGateBlock=1
      └ JointGateBlock 1건 (무정보폴백 0건 = 0.0%) [표본 19건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260929.txt`** — 233B · 09-29 15:53:31
```
completed: 2026-09-29 15:53:31
rows: 17651
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 23.6
t_retrain_s: 183.9
t_total_s: 208.0
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260929.txt`** — 43B · 09-29 15:47:15
```
auto_shutdown
2026-09-29T15:47:15.408097
```

_다이제스트 대상 8/18개 (중요도순). 제외: `20260929_DATA.log`, `20260929_PROBE.log`, `launcher_20260929_084000_23300.log`, `20260929_DEBUG.log`, `20260929_REGULAR_COLLECT.log`, `mainstall_traceback_20260929.log`, `force_flat_guard_20260929.log`, `peter_feed_push_20260929.log`_

### `logs/20260929_TRADE.log` — 25.0KB · 188행 · 최종 15:40:10

- 형식 평문 · 시각 인식 188행 · INFO=188

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-29 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-29 09:57:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,943,671) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-29 09:57:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas❌ coun✅ | conf=45.1%
2026-09-29 09:57:00 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 1084.1 | 손절=1086.07 1차=1083.44(×0.42) 2차=1082.13 horizon=3m hurst=mean-revert
  …
2026-09-29 14:39:22 [INFO] TRADE: [Position] 체결청산 SHORT @ 1076.2 | PnL=-1.51pt (-86,043원) | 하드스톱(틱)
2026-09-29 14:39:22 [INFO] TRADE: [청산 완료] PnL=-1.51pt (-86,043원) | 포지션 합계 -139,086원 (레그 2)
2026-09-29 14:41:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,836,660) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-09-29 14:53:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,836,660) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
2026-09-29 15:40:10 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×188

**컴포넌트 상위 15** — `Chejan`×53, `Position`×33, `Sizer`×25, `주문요청`×23, `진입체크`×8, `체결진입`×8, `청산 완료`×8, `체결진입보정`×7, `TickTP1`×5, `TickStop-S0C`×5, `TP1 부분청산`×4, `모드필터 차단`×3, `손절1차 조기축소`×3, `ProfitGuard`×2, `JointGateBlock 차단`×1

### `logs/20260929_WARN.log` — 598.2KB · 2654행 · 최종 15:46:12

- 형식 평문 · 시각 인식 2647행 · WARNING=2647, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-29 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-29 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-29 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-29 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-29 15:46:09 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-29 10:18:00 cols=['open'] existing_source=rt
2026-09-29 15:46:09 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-29 11:09:00 cols=['open'] existing_source=rt
2026-09-29 15:46:09 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-29 11:53:00 cols=['open'] existing_source=rt
2026-09-29 15:46:09 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=410 inserted=1 open_fixed=1 mismatch=19
2026-09-29 15:46:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3031ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2229 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=3031 band=INFO since_pipe_s=2231.1
```

</details>

**WARNING — 태그 38종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1962 | 09:05:12 | 15:10:09 | paintEvent slow 66.9ms | size=1955x1124 candles=21 grid=30.3 spans=0.0 candles=1.0 dir=0.0 regime=0.0 markers=0.0 axes=34.2 cross=0.0 | slow_cnt=1 total_cnt=5 overlay_cnt=2 |
| `LiveDBG` | 214 | 08:41:08 | 15:46:12 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 76 | 08:41:18 | 15:30:09 | 그리기 73.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `ChejanFlow` | 53 | 09:57:01 | 14:39:22 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1257' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:57:00.822' | positi… |
| `ChejanMatch` | 53 | 09:57:01 | 14:39:22 | order_no='1257' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1257 reason=진입 req_at=09:57:00.822' | pending_matched=True |
| `PendingOrder` | 46 | 09:57:00 | 14:39:22 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1084.1, 'reason': '진입', 'hint_source': '', 'atr': 1.5414, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qt… |
| `SHAP` | 21 | 11:43:02 | 15:09:02 | 슬로우 감지 1434ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `PipePerf` | 20 | 09:00:01 | 14:35:01 | total=1862ms | S0=5ms S1=71ms S2=0ms S3=0ms S4=132ms S5=752ms S6=858ms S7=37ms S8=7ms |
| `CB⑤` | 20 | 09:00:02 | 14:35:02 | 파이프라인 1862ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 18 | 09:00:01 | 14:40:00 | level=WARNING degraded=OFF | latency=1862ms | quality=1.00 | cache_age=44s | exceptions_10m=0 |
| `ScalerRefresh` | 16 | 09:11:00 | 14:51:00 | 5분 누적 수익률 +0.555% (임계 ±0.454%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ExitCooldown` | 16 | 09:58:35 | 14:39:22 | 하드스톱(틱) 후 3분 재진입 금지 (until 10:01:35) |

**채널** — `SYSTEM`×2629, `HEALTH`×18

**컴포넌트 상위 15** — `ChartDBG`×1962, `LiveDBG`×214, `OptionFlowChart`×76, `ChejanFlow`×53, `ChejanMatch`×53, `PendingOrder`×46, `SHAP`×21, `PipePerf`×20, `CB⑤`×20, `Health`×18, `ScalerRefresh`×16, `ExitCooldown`×16, `EntryFillFlow`×15, `SessionBackfill`×12, `ExitSendOrderResult`×9

### `logs/20260929_SYSTEM.log` — 956.1KB · 6272행 · 최종 15:47:15

- 형식 평문 · 시각 인식 6251행 · INFO=6251, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=29344 | 행감지=30s all_threads=True
2026-09-29 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.45s | predictions=0.05s trades=0.22s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-09-29 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-09-29 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-29 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-29 15:46:09 [INFO] SYSTEM: [SessionBackfill] 2026-09-29~2026-09-29 chart=411 existing=410 inserted=1 open_fixed=1 mismatch=19
2026-09-29 15:46:09 [INFO] SYSTEM: [BarGap] 당일 확정(2026-09-29) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-09-29 15:47:15 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-29 15:47:15 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-29 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6251

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1134, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `PumpGuard`×120, `CybosEvent`×106, `System`×100, `MicroRegime`×93, `BalanceUI`×89, `OptionChain`×81, `OptionBook`×79

### `logs/20260929_SIGNAL.log` — 533.7KB · 4707행 · 최종 15:40:10

- 형식 평문 · 시각 인식 4707행 · WARNING=1476, INFO=3231

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-09-29 15:10:01 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-29 15:40:10 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-29 15:40:10 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 57분(15.4%) / DN 86분(23.2%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-29 15:40:10 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-29 age=25m extreme=984 refresh=34 grade_x=138 cb3=0
2026-09-29 15:40:10 [INFO] SIGNAL: [ModelHealth] date=2026-09-29 앙상블유효가동률=75.4% | 파이프라인 370분 | ConstOut 6회/11분 {"3m": {"events": 4, "minutes": 7}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 80분 | 장중재학습 0회 | CB③ ready 247분/370분 (67%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 918 | 09:00:02 | 14:51:01 | 1m 'macro_sp500_chg' scale=0.1418 → floor=0.15 적용 (z-score 폭발 방지) |
| `Checklist` | 154 | 09:06:00 | 15:09:00 | 신뢰도 미달 32.8% < 41.1% → 강제 X등급 |
| `Model` | 132 | 09:00:00 | 15:09:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 102 | 09:00:00 | 15:09:00 | ts=08:59 horizon=1m age=1m max_z=-7.04(vwap_momentum) extreme=1 adj=1 |
| `WeightCollapse` | 82 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 78 | 08:45:09 | 14:51:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0279) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 6 | 09:35:00 | 11:19:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 4 | 09:07:00 | 09:51:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×4707

**컴포넌트 상위 15** — `ScalerFloor`×972, `SIGNAL`×740, `MetaGate`×420, `Ensemble`×376, `FQAdj`×369, `ZeroDiag`×321, `Checklist`×221, `ATR-Horizon`×174, `Model`×138, `ScalerRefresh`×118, `차단`×111, `ScalerMonitor`×103, `InstabilityGate`×94, `MicroRegime`×93, `WeightCollapse`×82

### `logs/20260929_LEARNING.log` — 297.8KB · 2910행 · 최종 15:40:10

- 형식 평문 · 시각 인식 2910행 · WARNING=163, INFO=2747

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00111 auc=0.410 out_max=0.3504 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.387 out_max=0.1755 (기준 auc<0.53 and span<0.020, 기저율=0.1750 n=80) → 보정 미적용, raw 통과
2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.492 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-29 08:40:49 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00057 auc=0.540 out_max=0.3448 (n=90) → 보정 재적용
  …
2026-09-29 15:40:10 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-29 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-29 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-29 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-29 15:40:10 [INFO] LEARNING: [Sigma] EOD sigma_20=0.04518% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 54 | 08:40:49 | 14:13:00 | 축퇴 감지 — span=0.00111 auc=0.410 out_max=0.3504 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 51 | 08:40:49 | 10:54:00 | 축퇴 감지 — span=0.00104 auc=0.387 out_max=0.1755 (기준 auc<0.53 and span<0.020, 기저율=0.1750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 19 | 08:40:49 | 12:29:01 | 축퇴 감지 — span=0.00040 auc=0.492 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 14 | 08:40:49 | 08:40:56 | 축퇴 감지 — span=0.00002 auc=0.383 out_max=0.3875 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 13 | 08:40:51 | 14:10:00 | 축퇴 감지 — span=0.00058 auc=0.511 out_max=0.4503 (기준 auc<0.53 and span<0.020, 기저율=0.4500 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:15m` | 8 | 08:40:53 | 08:40:58 | 축퇴 감지 — span=0.00011 auc=0.508 out_max=0.3351 (기준 auc<0.53 and span<0.020, 기저율=0.3350 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 3 | 08:40:58 | 14:50:00 | 복원한 보정기가 축퇴 상태 — span=0.00644 auc=0.495 out_max=0.3628 (n=1480) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `DriftAdjuster` | 1 | 15:40:10 | 15:40:10 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 15일) |

**채널** — `LEARNING`×2910

**컴포넌트 상위 15** — `LEARNING`×1207, `SGD`×369, `sigma`×357, `Bias⚠`×297, `Bias`×147, `Calibration:1m`×106, `Calibration:30m`×101, `MetaConf`×76, `OnlineLearner`×53, `ScalerWarmup`×40, `Calibration:3m`×36, `Calibration:5m`×27, `Calibration:10m`×26, `BiasReset`×22, `Calibration:15m`×16

### `logs/20260929_HEALTH.log` — 5.7KB · 36행 · 최종 14:41:00

- 형식 평문 · 시각 인식 36행 · WARNING=18, INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1862ms | quality=1.00 | cache_age=44s | exceptions_10m=0
2026-09-29 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=707ms | quality=1.00 | cache_age=103s | exceptions_10m=0
2026-09-29 09:12:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2865ms | quality=1.00 | cache_age=27s | exceptions_10m=0
2026-09-29 09:13:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=777ms | quality=1.00 | cache_age=85s | exceptions_10m=0
2026-09-29 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 596ms (표본 20분)
  …
2026-09-29 14:36:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=499ms | quality=1.00 | cache_age=65s | exceptions_10m=4 | exc_tags=[ExitCooldown]×2 [SHAP]×1 [SingleContractTP1]×1
2026-09-29 14:38:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=454ms | quality=1.00 | cache_age=184s | exceptions_10m=5 | exc_tags=[ExitCooldown]×2 [SHAP]×2 [SingleContractTP1]×1
2026-09-29 14:39:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=576ms | quality=1.00 | cache_age=59s | exceptions_10m=5 | exc_tags=[ExitCooldown]×2 [SHAP]×2 [SingleContractTP1]×1
2026-09-29 14:40:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=578ms | quality=1.00 | cache_age=119s | exceptions_10m=6 | exc_tags=[ExitCooldown]×3 [SHAP]×2 [SingleContractTP1]×1
2026-09-29 14:41:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=450ms | quality=1.00 | cache_age=179s | exceptions_10m=4 | exc_tags=[ExitCooldown]×3 [SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 18 | 09:00:01 | 14:40:00 | level=WARNING degraded=OFF | latency=1862ms | quality=1.00 | cache_age=44s | exceptions_10m=0 |

**채널** — `HEALTH`×36

**컴포넌트 상위 15** — `Health`×35, `HealthTrend`×1

### `logs/retrain_eod_20260929.log` — 20.6KB · 141행 · 최종 15:53:32

- 형식 평문 · 시각 인식 141행 · WARNING=16, INFO=125

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 15:50:02,962 [INFO] EOD_RETRAIN: =======================================================
2026-09-29 15:50:02,962 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-29 15:50:02,963 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-29 15:50:02,963 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-29 15:50:02,963 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-29 15:53:32,014 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0360 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-29 15:53:32,014 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0847 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-29 15:53:32,019 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.06s
2026-09-29 15:53:32,023 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.06s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-29 15:53:32,025 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:38 | 15:52:43 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1504봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-28 14:38:00 ≥ 홀드아웃 시작=2026-09-18 12:10:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-28 14:38 >= holdout_start=2026-09-18 12:10 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-28 … |
| `ScalerRefresh` | 6 | 15:53:31 | 15:53:32 | 1m CORE 'ofi_norm' raw_std≈0(0.0445) → identity(0,1) 강제 (FLAT 100% 방지) |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-09-29 | 최신 2026-09-28 · 기준 5거래일. 복구: python scripts/collect_regular_futures.py --from 20260929 --to 20260929 |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 23527/44834 제외 (418차 결정 1) — 남은 21307행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/21307행 제외 (559차 P1'-2) — 남은 19861행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:31 | 15:53:31 | 백필 0행 제외 — 필터가 무효일 수 있다. 17651행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×62, `SIGNAL`×43, `EOD_RETRAIN`×26, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×30, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `ScalerRefresh`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2

### `logs/20260929_MICRO.log` — 968.4KB · 2581행 · 최종 15:39:12

- 형식 평문 · 시각 인식 2581행 · DEBUG=2581

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1084.46/4 ask1=1084.48/1 mp={'microprice_tick': 1084.476, 'midprice_tick': 1084.47, 'depth_bias_tick': 0.2711} mlofi_tick=None queue=None
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1084.46/2 ask1=1084.48/1 mp={'microprice_tick': 1084.4733, 'midprice_tick': 1084.47, 'depth_bias_tick': 0.0657} mlofi_tick=-2.0 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1…
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1083.72/1 ask1=1084.48/1 mp={'microprice_tick': 1084.1, 'midprice_tick': 1084.1, 'depth_bias_tick': -0.0347} mlofi_tick=-1.6667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1083.72/1 ask1=1084.48/1 mp={'microprice_tick': 1084.1, 'midprice_tick': 1084.1, 'depth_bias_tick': -0.0347} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1084.00/2 ask1=1084.48/2 mp={'microprice_tick': 1084.24, 'midprice_tick': 1084.24, 'depth_bias_tick': -0.0042} mlofi_tick=2.95 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 1.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -0.…
  …
2026-09-29 15:34:41 [DEBUG] MICRO: [MICRO-TICK] #217300 bid1=1090.06/3 ask1=1090.14/5 mp={'microprice_tick': 1090.09, 'midprice_tick': 1090.1, 'depth_bias_tick': 0.071} mlofi_tick=0.25 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-29 15:35:00 [DEBUG] MICRO: [MICRO-TICK] #217400 bid1=1089.92/3 ask1=1090.54/2 mp={'microprice_tick': 1090.292, 'midprice_tick': 1090.23, 'depth_bias_tick': 0.2609} mlofi_tick=1.0 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-29 15:35:43 [DEBUG] MICRO: [MICRO-TICK] #217500 bid1=1091.38/1 ask1=1091.88/1 mp={'microprice_tick': 1091.63, 'midprice_tick': 1091.63, 'depth_bias_tick': -0.5254} mlofi_tick=1.8333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-29 15:37:03 [DEBUG] MICRO: [MICRO-TICK] #217600 bid1=1093.00/1 ask1=1094.00/11 mp={'microprice_tick': 1093.0833, 'midprice_tick': 1093.5, 'depth_bias_tick': -0.7292} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-09-29 15:39:12 [DEBUG] MICRO: [MICRO-TICK] #217700 bid1=1093.00/1 ask1=1093.30/1 mp={'microprice_tick': 1093.15, 'midprice_tick': 1093.15, 'depth_bias_tick': 0.0} mlofi_tick=-1.8333 queue={'depletion_bid': -0.0, 'depletion_ask': 5.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
```

</details>

**채널** — `MICRO`×2581

**컴포넌트 상위 15** — `MICRO-TICK`×2197, `MICRO-MINUTE`×384

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -107000원
════════════════════════════════════════════════════
2026-09-29 15:46:09 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-29 09:57:00 cols=['open'] existing_source=rt
2026-09-29 15:46:09 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-29 10:17:00 cols=['open'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 8 |
| 진입 등록(`[Position] 진입`) — **엔진** | 8 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 8 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 8 |
| 차단(`[차단]`) | 111 |
| 사이저 호출(`[Sizer]`) | 25 |

### 포지션 8건 · 승 4 (50%) · 합계 +1.04pt (-107,000원)  ※ 레그 15행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:57:00 | 엔진 | SHORT | 2 | 3m | 2 | +0.76 | +16,734 | 하드스톱(틱) |
| 11:09:02 | 엔진 | LONG | 2 | 3m | 2 | +1.76 | +66,648 | 하드스톱 |
| 13:02:01 | 엔진 | SHORT | 2 | 3m | 2 | +2.70 | +113,778 | TP2(전량) |
| 13:08:00 | 엔진 | SHORT | 2 | 5m | 2 | -1.54 | -98,182 | 하드스톱(틱) |
| 13:24:01 | 엔진 | SHORT | 2 | 5m | 2 | -2.44 | -143,208 | 하드스톱(틱) |
| 14:30:01 | 엔진 | SHORT | 1 | 3m | 1 | +1.74 | +76,424 | TP2(전량) |
| 14:35:01 | 엔진 | SHORT | 2 | 3m | 2 | +0.42 | -108 | 하드스톱(틱) |
| 14:39:00 | 엔진 | SHORT | 2 | 5m | 2 | -2.36 | -139,086 | 하드스톱(틱) |

**청산 레그 15행** (부분청산 7 · 전량청산 8)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:57:16 | 부분 | 1 | +0.80 | +29,367 | TP1 부분청산 33% |
| 09:58:35 | 전량 | 1 | -0.04 | -12,633 | 하드스톱(틱) |
| 11:12:37 | 부분 | 1 | +0.59 | +18,824 | TP1 부분청산 33% |
| 11:13:00 | 전량 | 1 | +1.17 | +47,824 | 하드스톱 |
| 13:02:22 | 부분 | 1 | +0.63 | +20,889 | TP1 부분청산 33% |
| 13:04:01 | 전량 | 1 | +2.07 | +92,889 | TP2(전량) |
| 13:11:03 | 부분 | 1 | -0.81 | -51,091 | 손절1차 조기축소 |
| 13:17:46 | 전량 | 1 | -0.73 | -47,091 | 하드스톱(틱) |
| 13:24:24 | 부분 | 1 | -0.81 | -51,104 | 손절1차 조기축소 |
| 13:24:54 | 전량 | 1 | -1.63 | -92,104 | 하드스톱(틱) |
| 14:32:01 | 전량 | 1 | +1.74 | +76,424 | TP2(전량) |
| 14:35:13 | 부분 | 1 | +0.46 | +12,446 | TP1 부분청산 33% |
| 14:35:21 | 전량 | 1 | -0.04 | -12,554 | 하드스톱(틱) |
| 14:39:11 | 부분 | 1 | -0.85 | -53,043 | 손절1차 조기축소 |
| 14:39:22 | 전량 | 1 | -1.51 | -86,043 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×5, `TP1 부분청산 33%`×4, `손절1차 조기축소`×3, `TP2(전량)`×2, `하드스톱`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 6/8건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -107,000 = 포지션합 -107,000 → OK · `[청산 완료]` 8건 = 조립 포지션 8건 → OK

### CB③ 판정 가능 시간 — **247분 / 370분 (67%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 8건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:57:00 | SHORT | 2 | 1084.1 | 3m | mean-revert |
| 11:09:02 | LONG | 2 | 1088.26 | 3m | neutral |
| 13:02:01 | SHORT | 2 | 1081.38 | 3m | trend |
| 13:08:00 | SHORT | 2 | 1079.5 | 5m | trend |
| 13:24:01 | SHORT | 2 | 1080.82 | 5m | neutral |
| 14:30:01 | SHORT | 1 | 1078.08 | 3m | mean-revert |
| 14:35:01 | SHORT | 2 | 1075.68 | 3m | mean-revert |
| 14:39:00 | SHORT | 2 | 1074.8 | 5m | mean-revert |

계약수 분포 — 1계약×1, 2계약×7

등급 분포 — `A급(원시C)`×8

**진입한 건들의 체크리스트 미통과 항목** — `fore`×8, `chas`×6, `ofi`×2, `cvd`×2, `prev`×2

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×6, **2계약**×3, **3계약**×16

실제 진입 계약수 — **1계약**×1, **2계약**×7

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×25

### 차단 사유 111건 · 43종

| 건수 | 사유 |
|---|---|
| 48 | 등급X — 미통과 항목: 2_confidence |
| 4 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 3 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign |
| 2 | 청산 후 쿨다운 — 0초 후 재진입 가능 |
| 2 | ATR 0.89pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 청산 후 쿨다운 — 60초 후 재진입 가능 |
| 2 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.5pt > ATR×5.0=9.8pt (시가=1082.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.5pt > ATR×5.0=8.8pt (시가=1082.04 반등위험) |
| 1 | 청산 후 쿨다운 — 154초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 94초 후 재진입 가능 |
| 1 | JointGateBlock — meta=0.52 tox=0.70 joint=0.361 < 0.50 |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign |

**체크리스트 미통과 항목 누적** — `2_confidence`×48, `3_vwap`×14, `6_foreign`×14, `4_cvd`×10, `7_prev_bar`×9, `5_ofi`×8, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 10건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×5
- `일간 리셋 완료` ×2
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-29 13:24:02, 현재 1…` ×1
- `연속 손절 2회 (300초 창, 포지션 단위)` ×1
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-29 14:39:00, 현재 2…` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 13건 · 최대 5094ms · 5초 초과 1건

상위 — 5094ms, 4375ms, 4281ms, 4015ms, 3875ms, 3500ms, 3031ms, 2578ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 14:05:05 | 5094ms | 4239ms | **855ms (17%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260929_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:18 2026-09-29 15:40:18 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 33분/일 < 하한 60분 — 금일 60분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 370분
--- [CB] ×6(표본)
09:58:35 2026-09-29 09:58:35 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:11:03 2026-09-29 13:11:03 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:17:46 2026-09-29 13:17:46 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:24:24 2026-09-29 13:24:24 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:58:35 2026-09-29 09:58:35 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:01:35)
09:58:35 2026-09-29 09:58:35 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:01:35)
10:07:00 2026-09-29 10:07:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=356ms | quality=1.00 | cache_age=185s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
11:13:00 2026-09-29 11:13:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:15:00)
--- [SHAP] 슬로우 ×8(표본)
11:43:02 2026-09-29 11:43:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1434ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:00:02 2026-09-29 12:00:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1372ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:08:02 2026-09-29 12:08:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 932ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:22:01 2026-09-29 12:22:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1401ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-29 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4015ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4015 band=INFO since_pipe_s=NA
09:00:04 2026-09-29 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4281 band=INFO since_pipe_s=0.2
09:05:12 2026-09-29 09:05:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=9 watchdog_alerted=[] | [MainStall] stall_ms=3500 band=INFO since_pipe_s=10.7
09:12:04 2026-09-29 09:12:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4375 band=INFO since_pipe_s=0.2
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260929_SYSTEM.log`
```
--- ConstOut ×6(표본)
09:35:00 2026-09-29 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5252) | 앙상블 제외는 유지
09:44:00 2026-09-29 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4633) | 앙상블 제외는 유지
09:54:00 2026-09-29 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4922) | 앙상블 제외는 유지
11:03:01 2026-09-29 11:03:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3710) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:10 2026-09-29 15:40:10 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 247분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-29 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-09-29 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-29 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-29 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×4(표본)
13:24:54 2026-09-29 13:24:54 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-29 13:24:02, 현재 1회)
14:39:22 2026-09-29 14:39:22 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-29 14:39:00, 현재 2회)
15:40:10 2026-09-29 15:40:10 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:10 2026-09-29 15:40:10 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:10 2026-09-29 15:40:10 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 3레그 / 3포지션 중 TP 이벤트 대응 3 · 단일계약 보호전환(설계) 0 · 미대응 0
--- [SchedForceExit] ×1(표본)
15:11:09 2026-09-29 15:11:09 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:20 2026-09-29 15:40:20 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:15 2026-09-29 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:20 2026-09-29 15:40:20 [INFO] SYSTEM: [Notify] ℹ️ [15:40:20] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:20 2026-09-29 15:40:20 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 400초
15:40:20 2026-09-29 15:40:20 [INFO] SYSTEM: 자동 종료 예약 — 415초 후 Qt 이벤트 루프 종료
```

### `logs/20260929_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-29 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0570 dir=-1)
09:35:00 2026-09-29 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-29 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-29 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0570 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-29 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:07:00 2026-09-29 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-29 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-29 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:41 2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:41 2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:41 2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:41 2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
--- 안전망 ×8(표본)
09:07:00 2026-09-29 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-09-29 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-29 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-29 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260929_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00111 auc=0.410 out_max=0.3504 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.387 out_max=0.1755 (기준 auc<0.53 and span<0.020, 기저율=0.1750 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.492 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-29 08:40:49 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00057 auc=0.540 out_max=0.3448 (n=90) → 보정 재적용
```

### `logs/20260929_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
10:07:00 2026-09-29 10:07:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=356ms | quality=1.00 | cache_age=185s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
10:08:00 2026-09-29 10:08:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=434ms | quality=1.00 | cache_age=51s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
13:04:02 2026-09-29 13:04:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1572ms | quality=1.00 | cache_age=85s | exceptions_10m=3 | exc_tags=[SHAP]×2 [ExitCooldown]×1
13:05:01 2026-09-29 13:05:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1297ms | quality=1.00 | cache_age=144s | exceptions_10m=3 | exc_tags=[SHAP]×2 [ExitCooldown]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260929_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 22 | 09:57:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,943,671) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:10 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260929_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 18 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 166 | 09:54:00 [WARNING] paintEvent slow 143.8ms | size=1955x1096 candles=36 grid=42.7 spans=0.0 candles=2.0 dir=0.2 regime=5.5 marker… |
| 12:00 | 장중 중간점 | 103 | 11:54:01 [WARNING] paintEvent slow 151.1ms | size=1955x1096 candles=36 grid=47.7 spans=13.8 candles=2.3 dir=0.2 regime=10.0 mark… |
| 14:00 | 장중 후반 · 장중 재학습 | 20 | 13:55:09 [WARNING] 그리기 88.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 847x1001 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 145 | 15:04:09 [WARNING] 그리기 129.6ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 847x1001 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 10 | 15:15:09 [WARNING] 그리기 117.0ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 847x1001 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 9 | 15:40:18 [WARNING] mc-conf 괴리: 최근 5거래일 평균 진입후보 33분/일 < 하한 60분 — 금일 60분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 370분 |
| 15:47 | EOD 재학습(py310_64) 완료 | 7 | 15:46:09 [WARNING] OHLCV 불일치 ts=2026-09-29 09:57:00 cols=['open'] existing_source=rt |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260929_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=29344 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 137 | 08:49:02 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 203 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 290 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 177 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 170 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 180 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 142 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 59 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:41:09 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:09 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260929_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:09 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0279) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 133 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0290) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 207 | 08:55:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0417) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 154 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 119 | 11:54:00 [WARNING] 신뢰도 미달 40.4% < 44.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 128 | 13:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 74 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:10 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260928 | 15:47 | 로그 본문 |
| 20260926 | 16:50 | 로그 본문 |
| 20260924 | 10:58 | 로그 본문 |
| 20260923 | 18:44 | 로그 본문 |
| 20260922 | 15:47 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20260929** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-26 (MW0601 631차 후속 — 장후: 휴장일 상황 동결 확인 + F-4 범위 확장)
## 2026-09-28 (MW0601 633차 — 장전 점검)
## 2026-09-28 (MW0601 634차 — 장중 점검)
## 2026-09-28 (MW0601 635차 — 장후 점검)
## 2026-09-28 (MW0601 636차 — 장후 자동조치: 고도화 방안 2·3·4 구현 + DB pruning 「삭제 성공」 판단 정정)
## 2026-09-29 (MW0601 637차 — 장전 점검)
## 2026-09-29 (MW0601 638차 — 장중 점검)
## 2026-09-29 (MW0601 639차 — 신동 규격 v2 개정: 1차 목표가 진입가 뒤에 놓이는 결함) — 🟡 **구현 · 커밋 전 사용자 확인 대기**
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
`의 git subprocess 호출부에 실패 시 정확한 명령·stderr 로깅 강화 + `GIT_OPTIONAL_LOCKS=0` 환경변수 이중 방어 추가(계획만, 장후 적용 대상).
2. 633-4(opt_chain_pcr) — 해소 처분, NEXT_TODO에서 종결 표시.
3. 1-1·1-2·633-1/634-2 — 전부 지속, 새 Fix 등록 없음(함정①).

**Why**: 함정①(판정≠결정) 방지 — sizing_inversion_watch·등급 인플레·WeightCollapse/ConstOut은 전부 이미 추적 중인 채널/항목임을 grep으로 먼저 확인한 뒤 신규로 올리지 않았다. index.lock 신규 발생은 grep으로 걸리는 기존 등록이 없어 신규로 등록했다.

**How to apply**: Fix 1(git subprocess 로깅 강화)은 다음 세션(장후 또는 별도)에서 구현. index.lock 자체는 사용자가 본인 컴퓨터에서 `git_lock_guard.py --check`로 600초 경과 후 재판정 — 스테일이면 `--reclaim`, 여전히 판정보류면 대기.

**검증**: Fix 1 구현 후 동일 환경(코웍 마운트)에서 재실행 시 `git diff` 실패가 재현되는지, 재현된다면 로깅이 정확한 하위 명령을 잡아내는지 확인. index.lock은 사용자 재확인 결과로 검증.

⚠ **코드 변경 없음(장중 점검 세션 — 라이브 프로세스 실행 중).** 라이브 DB 스캔 없음(수집기는 로그·설정·git 전용, predictions.db/trades.db 미접근).

**후속 (12:37, 같은 638차 세션)**: 1-3의 `.git/index.lock`을 재판정한 결과 스테일 확정(0바이트·0.2시간·프로세스 0개)됐고, `scripts/git_lock_guard.py --reclaim`으로 정상 회수했다(이름변경 방식, 실제 락 제거 확인 — `git status` 정상 복귀). 이름 바뀐 부스러기 1개(`index.lock.stale_20260929033733_6`)는 이 환경의 삭제 권한 부재로 못 지웠으나 커밋을 막지 않는다(스크립트 확인 문구). **1-3 최종 처분: ✅ 해소.**

## 2026-09-29 (MW0601 639차 — 신동 규격 v2 개정: 1차 목표가 진입가 뒤에 놓이는 결함) — 🟡 **구현 · 커밋 전 사용자 확인 대기**

**증상**: 9/29 MAIN R3 매수 4건(10:37·10:43·10:59·11:19, 진입 1091.04–1091.90)의 1차 목표가 전부 1091.50. 매수인데 1차가 진입가보다 낮은 건이 2건이다. 4건 모두 1차 즉시 본전(−97,664원).
**원인**: `engine.targets` 최종 후보(08:50 가장 먼 구조맥점)를 `side*(x−e) > 0`로만 거르고, `TP_BUF`를 **검사 뒤에** 뺐다. 1차·최종 맞바꿈이 그 값을 1차 자리에 넣어 `T1_MIN_DIST`(2pt)를 우회했다. 가격이 맥점 목록의 끝(1092)에 붙은 날에만 발생한다.
**결정(사용자 지시 — 사전등록 §6 개정 절차)**: 최종 후보에도 `T1_MIN_DIST` 적용(값 무변경). `SPEC_VERSION` → `SD-2026-09-29-v2`, 채점(MAIN·섀도 전부, R3 중단 판정 시계 포함) **9/30 재시작**. v1 기록은 DB에 그대로 두고 채점표·리포트 누적이 `spec_version`으로 거른다. 조건부 러너 섀도는 별도 사전등록(`RUNNER_VERSION`)이라 **동결 함수 `targets_v1`에 고정**했다.
**🔴 불리한 사실(재생 실측)**: 결함 경로는 9/22(TR44 1건)·9/29에만 있었고, **두 날 모두 v2가 더 나쁘다** — 9/29 MAIN −27.6만 → −103.8만, TR44 −16.1만 → −171.6만, 9/22 TR44 −10.3만. 결함이 「맥점 끝 진입 즉시 본전」으로 작동해 손실을 막고 있었다. 표본 5거래라 v1 옹호 근거가 아니며, 그런 규칙을 원하면 새 사전등록이 필요하다(결과를 본 뒤의 규칙).
**Why**: v1 동작은 규격 문구(§2-5 1차 ≥ 2pt)를 어긴 우연이다. 규격 준수가 개정 근거이고 성과는 근거가 아니다.
**How to apply**: 워킹트리 파일이 바뀌어 있으므로 **내일 자동 기동 시 v2가 라이브에 올라간다**(커밋 여부와 무관). 되돌리려면 기동 전에 되돌릴 것. MW0602는 같은 엔진이면 같은 결함이 있다(반영은 그 PC 몫).
**검증**: `tests/test_639_shindong_v2_target_inversion.py` 17건(재현·수정·무작위 불변식 3,000·결함 경로 밖 v1과 동일·러너 v1 고정·버전 필터). `test_626/629/632/632b/632c/627` 통과, `test_632` 9/22 TR44 기대값 v2로 갱신. `test_628` 1 실패는 기존 `ui_prefs` 건. 근거 문서 `docs/신동거래/신동_개정_v2_1차목표역전_20260929.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-26 (MW0601 632차 — 장중 재점검)
## 2026-09-26 (MW0601 631차 후속 — 장후)
## 2026-09-28 (MW0601 633차 — 장전 점검)
## 2026-09-28 (MW0601 634차 — 장중 점검)
## 2026-09-28 (MW0601 635차 — 장후 점검)
## 2026-09-28 (MW0601 636차 — 장후 자동조치)
## 2026-09-29 (MW0601 637차 — 장전 점검)
## 2026-09-29 (MW0601 638차 — 장중 점검)
```

미완료 체크박스 **2878건** (끝에서 30건)
```
- [ ] **631-14 (F-4/G-1)** 스킬 폴더 `collect_evidence.py`에 `config/krx_holidays.py`(파일경로 로드) 휴장일 판정 — FZ-6·480차 규칙 스킵 + 배너.
- [ ] **631-15** `tests/test_458_p0_quiet_window.py:163` 이 운영 DB 경로로 `init_all_dbs()` 를 호출한다 — 임시 DB_DIR 로 격리할 것(2026-09-26 이 테스트가 운영 predictions.db 에 색인을 만들었다; 이번엔 무해).
- [ ] **631-16 (S-1, 권고)** `auto_trader_kiwoom/scripts/shutdown_friday.bat`(한량이 저장소): `shutdown /h` 직전 CpStart·ncStarter·DibServer·미륵이 main.py 종료 — 절전 해제 후 끊긴 세션을 든 CpStart 가 남아 LAUNCH_API 가 "Already…
- [ ] **631-17 (S-2/S-3)** `LAUNCH_API.bat`: CpStart 시작 < 마지막 절전 해제면 연결 불신 → 자동로그인 / `[CHECK] IsConnect` 값을 로그 파일에도 기록.
- [ ] **631-18 (S-4)** `start_mireuk.bat` STEP 4 실패 시 "CpStart 생존·미연결 = 절전 해제 후 끊김" 힌트.
- [ ] **631-19** 옛 Cybos 생존 상태 자동로그인 1차 성공 여부 — 다음 절전 해제 아침 diag 로그로 확인(새 프로세스 IsConnect 확인 라이브 검증)
- [ ] **631-17 (S-2/S-3)** 여전히 미구현 확인 — `logs/Mireuk_batch/launcher_20260928_084001_3298.log`에 `[CHECK] IsConnect` 값이 파일로 기록되지 않음(grep 0건). 변경 없음, 계속 열어둠.
- [ ] **633-1 (P2, 신규)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 1행 마크다운 제목(`# 재시작...`) 손상 상태로 미커밋 — 사용자에게 의도한 편집인지 확인 후, 아니라면 `git checkout --`로 복원. 근거: 0928 장전 리포트 이상점 1-1.
- [ ] **633-2 (고도화, P2)** `[PreRetrain]` 판정에서 `data/eod_retrain_done_{d}.txt` 마커 파일 직접 확인 경로를 "미기록 보완"이 아니라 1차 확인 경로로 격상 검토 — 근거: `SessionStateDrop`(606-2 근본원인 미해결) 발생 시마다(09-14·09-17·09-21·09-22·09-…
- [ ] **633-3 (고도화, P2)** 커밋 전 프리플라이트(`scripts/git_lock_guard.py` 또는 별도 스크립트)에 "마크다운 파일 첫 줄이 `# `로 시작하다가 사라졌는가" 같은 가벼운 문서 손상 탐지 경고 추가 검토 — 근거: 0928 이상점 1-1(재현 1건, 원인 미상).
- [ ] **633-4** `opt_chain_pcr`(옵션체인 → 30m CORE 피처 입력) 로드 로그가 0928 장전(08:40~09:00) 구간에 미확인 — 장중 점검에서 재확인.
- [ ] **633-5 (P1, 신규)** `.git/index.lock`(0바이트) 스테일 확정 후에도 `--reclaim`이 `EPERM`으로 실패 — 코웍 마운트 경유 세션의 구조적 한계(SKILL.md 예고대로 재현). 사용자가 로컬에서 직접 삭제하거나 `--reclaim` 재시도 필요. 근거: 0928 장전 리포트 이상점 1-2.
- [ ] **634-1 (P2, 고도화)** `scripts/git_lock_guard.py --reclaim`이 `unlink` 실패(`EPERM`) 시 `os.rename()`으로 `<파일>.stale.<pid>` 우회를 자동 시도하도록 — 단 "스테일 확정" 판정 후에만 동작하고 "판정보류"에서는 지금처럼 손대지 않아야 함. 근거: 0928 장전·…
- [ ] **634-2** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상(633-1 계승). 잠금 해소로 이제 언제든 `git checkout --`로 되돌릴 수 있음, 의도한 편집인지 확인 먼저.
- [ ] **635-1** `docs/정기점검/수익률향상_누적대장.md`의 P5-03(TP1 비중·보호 트레일 오프셋)에 09-28 CASE-01을 표본으로 추가(3m, TP1 33%→TRAIL_AFTER_TP1, 발동가 1107.22, 발동 직후 저가 1106.26, 미실현 추가폭 약 0.96pt) — 다음 장후가 대장 파일에 직접 반영할 것.
- [ ] **635-2** `.claude/skills/mireuk-daily-check/references/evidence_map.md` §8-3 갱신 — v9-dev `trades` 테이블에 `tp1_reached`·`exit_trigger`·`exit_outcome` 컬럼이 이미 존재함(2026-09-28 `PRAGMA table_info` 실측,…
- [ ] **635-3 (고도화, P2)** `learning/batch_retrainer.py:prune_raw_data_db()` — "DB pruning 실패: database table is locked" 경고가 실제로는 4개 테이블 DELETE 성공(오늘 22,860행) 후 `PRAGMA wal_checkpoint(PASSIVE)` 단계에서만 …
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상(633-1/634-2 계승, 0928 장후에도 미확인 상태 지속).
- [ ] **636-1 (사용자, 1분)** `scripts/git_lock_guard.py` 정본을 fuoption 사본(`..\fuoption\scripts\git_lock_guard.py`)에 복사 — 자동조치 세션의 덮어쓰기가 권한 거부됨. 복사 전까지 `test_483::test_sibling_copy_matches_canonical[fuopt…
- [ ] **636-2 (승인 대기, P2)** `prune_raw_data_db()` 실제 삭제 수정 — DELETE 루프 뒤 `conn.commit()`, `PRAGMA wal_checkpoint(PASSIVE)`는 별도 try(실패해도 삭제는 유지, 로그 `완료(체크포인트 보류)`). 현재는 자기 트랜잭션 안 체크포인트 → `database tab…
- [ ] **636-3 (C — 사용자 지시 필요)** 고도화 방안 1: `[PreRetrain]` 판정에서 마커 파일(`data/eod_retrain_done_{날짜}.txt`)을 1차 경로로 격상. main.py 재학습 스킵 순서 변경이라 자동조치 범위 밖. 606-2 근본수정과 함께 판단.
- [ ] **636-4 (정리)** DECISION_LOG 636차 항목은 작업본에 append 만 됐고 **미커밋** — 같은 파일에 다른 세션(신동 R3 딥다이브)의 미커밋 변경(전 파일 줄바꿈 변경 + 중간 삽입)이 있어 골라 커밋할 수 없었다. 그 세션 커밋 때 함께 들어가면 된다.
- [ ] **636-5 (정리)** `md_title_guard.py`를 SKILL.md 커밋 전 프리플라이트(`git_lock_guard.py --check` 옆)에 한 줄 추가할지 결정.
- [ ] **637-1 (P1)** `dev_memory/NEXT_TODO.md` 606-4(09-17 access violation 원인 조사 우선순위 결정)에 09-28(4건)·09-29(3건) 재현을 근거로 추가 — 사용자가 우선순위를 정할 때 참고. 전부 부팅 구간(정규장 개시 전) 한정, 정규장 개시 후 재현 0건. 새 조사 착수는 사용자 결정…
- [ ] **637-2 (P2, 신규)** `scripts/collect_evidence.py` §1 당일 파일 인벤토리·§11 자동 적신호가 `logs/crash_fault.log`(날짜 토큰 없는 누적 로그)를 구조적으로 못 본다 — `crash_fault_events()`(§9)는 "정상종료 기록" 판정용이지 "access violation 건수 …
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장전에도 미확인·미커밋 상태 지속(3번째 날).
- [ ] **638-1 (P1, 신규)** `scripts/collect_evidence.py`의 `git diff`(미커밋 변경량 측정) subprocess 호출부 — 실패 시 정확한 명령·종료코드·stderr를 다이제스트에 로깅하도록 강화 + `GIT_OPTIONAL_LOCKS=0` 환경변수를 `--no-optional-locks` 플래그와 함께 이…
- [ ] **638-2 (사용자, 대기)** `.git/index.lock`(2026-09-29 12:27:19 생성) 판정보류 지속 중(12:32 기준 나이 338초, 임계 600초 미도달) — 600초 경과 후 사용자가 본인 컴퓨터에서 직접 `python scripts/git_lock_guard.py --check` 재실행, 스테일이면 `--recl…
- [ ] **606-4 (참고 보강)** 09-28 소급 access violation 4건 중 1건이 부팅 구간이 아니라 11:33경(장중)에도 발생했음을 추가 확인 — 조사 우선순위 결정은 여전히 사용자 몫.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장중에도 미확인·미커밋 지속(3번째 날, 변화 없음).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
은 작업본에 append 만 됐고 **미커밋** — 같은 파일에 다른 세션(신동 R3 딥다이브)의 미커밋 변경(전 파일 줄바꿈 변경 + 중간 삽입)이 있어 골라 커밋할 수 없었다. 그 세션 커밋 때 함께 들어가면 된다.
- [ ] **636-5 (정리)** `md_title_guard.py`를 SKILL.md 커밋 전 프리플라이트(`git_lock_guard.py --check` 옆)에 한 줄 추가할지 결정.

## 2026-09-29 (MW0601 637차 — 장전 점검)

- [ ] **637-1 (P1)** `dev_memory/NEXT_TODO.md` 606-4(09-17 access violation 원인 조사 우선순위 결정)에 09-28(4건)·09-29(3건) 재현을 근거로 추가 — 사용자가 우선순위를 정할 때 참고. 전부 부팅 구간(정규장 개시 전) 한정, 정규장 개시 후 재현 0건. 새 조사 착수는 사용자 결정 대기, 이 항목은 606-4에 흡수(중복 등록 아님).
- [ ] **637-2 (P2, 신규)** `scripts/collect_evidence.py` §1 당일 파일 인벤토리·§11 자동 적신호가 `logs/crash_fault.log`(날짜 토큰 없는 누적 로그)를 구조적으로 못 본다 — `crash_fault_events()`(§9)는 "정상종료 기록" 판정용이지 "access violation 건수 집계"용이 아님. 09-28 access violation 4건이 0928 장전 리포트에서 완전히 누락된 것으로 실증됨(리포트 전문 검색 "access violation" 0건). 제안: `crash_fault_events()` 호출부 근처에 "오늘 `[START]` 구간 내 `Windows fatal exception` 건수" 집계를 §5 또는 §11에 추가. 점검 도구 자체 개선이라 사용자 승인 없이 구현 가능. 근거: 0929 장전 이상점 1-2.
- [x] **O-p1 (SessionStateDrop) 최종 판정 완료** — 09-28→09-29 거래일 전환 재현 확정(`[SessionStateDrop]` 08:41:09, `session_state.json` 두 키 부재). 어제(0928) EOD 자체는 정상 종료 재확인(`eod_retrain_done_20260928.txt`, 6/6). 근본수정 606-2는 계속 사용자 승인 대기. 신규 Fix 없음(함정①).
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장전에도 미확인·미커밋 상태 지속(3번째 날).

## 2026-09-29 (MW0601 638차 — 장중 점검)

- [ ] **638-1 (P1, 신규)** `scripts/collect_evidence.py`의 `git diff`(미커밋 변경량 측정) subprocess 호출부 — 실패 시 정확한 명령·종료코드·stderr를 다이제스트에 로깅하도록 강화 + `GIT_OPTIONAL_LOCKS=0` 환경변수를 `--no-optional-locks` 플래그와 함께 이중으로 전달(코웍 마운트 경유 환경에서 플래그만으로 락 생성을 못 막은 것으로 추정되는 사례 실측, 2026-09-29 12:27:19 `.git/index.lock` 생성). 근거: 0929 장중 이상점 1-3.
- [ ] **638-2 (사용자, 대기)** `.git/index.lock`(2026-09-29 12:27:19 생성) 판정보류 지속 중(12:32 기준 나이 338초, 임계 600초 미도달) — 600초 경과 후 사용자가 본인 컴퓨터에서 직접 `python scripts/git_lock_guard.py --check` 재실행, 스테일이면 `--reclaim`, 여전히 판정보류면 대기. 절대 원격 세션에서 지우지 말 것(EPERM 위험).
- [x] **633-4 종결** — `opt_chain_pcr` 로드 로그 미확인 항목, 0929 장중에 `[OptionChain][Worker]`/`[OptionBook]` 09:01:29~09:42:13 반복 정상 완료로 해소 확인.
- [ ] **606-4 (참고 보강)** 09-28 소급 access violation 4건 중 1건이 부팅 구간이 아니라 11:33경(장중)에도 발생했음을 추가 확인 — 조사 우선순위 결정은 여전히 사용자 몫.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장중에도 미확인·미커밋 지속(3번째 날, 변화 없음).

- [x] **638-2 갱신 — 종결(주 이슈)** `.git/index.lock` 12:37 스테일 확정 → `git_lock_guard.py --reclaim`으로 정상 회수, 커밋 가능 상태 복귀 확인. 잔여 부스러기(`index.lock.stale_20260929033733_6`) 정리만 선택사항으로 남김(급하지 않음, 사용자 한가할 때).

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

### `data/heartbeat_MW0601_20260929.json` — 245B · 09-29 15:46:52
```json
{
 "pid": 29344,
 "written_at": "2026-09-29T15:46:52",
 "beat_epoch": 1790664409.3201654,
 "beat_age_sec": 3.4,
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

- 파일 최종 기록: **09-29 15:53:32**

| 키 | 값 | 수집 대상일(2026-09-29)과 일치 |
|---|---|---|
| `date` | 2026-09-29 | 예 |
| `p8_last_success_date` | 2026-09-29 | 예 |
| `eod_retrain_ok_date` | 2026-09-29 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20260929_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 29344 | 08:40:44 | 15:47:15 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 176개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260929-점검리포트.md` | 48.4KB | 09-29 12:38 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_intra.md` | 74.7KB | 09-29 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_pre.md` | 59.0KB | 09-29 09:00 |
| `docs/정기점검/매일점검/MW0601-20260928-점검리포트.md` | 81.3KB | 09-28 17:47 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_post.md` | 84.8KB | 09-28 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_intra.md` | 74.0KB | 09-28 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md` | 56.8KB | 09-28 09:00 |
| `docs/정기점검/매일점검/MW0601-20260926-점검리포트.md` | 67.5KB | 09-26 16:43 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260923.json` | 3.0KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260923.md` | 4.9KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260923.json` | 38.8KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260923.md` | 32.3KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260923.json` | 121.3KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260923.md` | 195.2KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json` | 3.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md` | 5.0KB | 09-18 15:55 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
2. 포지션 8건 중 최종청산이 하드스톱·손절 계열 **6건(75%)** — 손절 준수율 확인 필요 (레그 15행)
3. 다레그 포지션 **7건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. 메인 스레드 정지 5초 초과 **1건** (최대 5094ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260929_SYSTEM.log`: **ConstOut** 6건(표본)
7. `logs/20260929_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20260929_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20260929_LEARNING.log`: **축퇴** 8건(표본)
10. 미커밋 변경 23건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
11. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260929*.log` (Windows) / `grep 강제청산 logs/*20260929*.log`*