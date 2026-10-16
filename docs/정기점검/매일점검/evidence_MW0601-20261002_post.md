# 미륵이 증거 다이제스트 — 2026-10-02 / POST

- 생성 2026-10-02 16:19:28 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-015pk3xhsog6iyzyjgumhebx/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261002` · `2026-10-02` · `261002` · `1002`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **26개** 파일 · 26개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261002.log` | 269B | 10-02 07:21 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261002.txt` | 28B | 10-02 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261002.txt` | 28B | 10-02 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261002.txt` | 233B | 10-02 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261002.log` | 1.9KB | 10-02 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261002.log` | 217B | 10-02 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261002.json` | 245B | 10-02 15:46 |
| `launcher_{DATE}_084001_17771.log` | 1 | `logs/Mireuk_batch/launcher_20261002_084001_17771.log` | 2.0MB | 10-02 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261002.log` | 7.4KB | 10-02 12:20 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261002.log` | 2.2KB | 10-02 16:10 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261002.log` | 38.3KB | 10-02 16:19 |
| `retrain_intraday_20260707_{DATE}00.log` | 1 | `logs/retrain_intraday_20260707_100200.log` | 4.6KB | 07-07 10:02 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261002.txt` | 43B | 10-02 15:47 |
| `strategy_report_{DATE}_154026.txt` | 1 | `data/daily_reports/strategy_report_20261002_154026.txt` | 2.2KB | 10-02 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20261002_DATA.log` | 437.3KB | 10-02 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261002_DEBUG.log` | 231.9KB | 10-02 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261002_HEALTH.log` | 3.6KB | 10-02 14:58 |
| `{DATE}_HOGA.log` | 1 | `logs/20261002_HOGA.log` | 50.0MB | 10-02 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261002_LEARNING.log` | 290.3KB | 10-02 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261002_MICRO.log` | 941.2KB | 10-02 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20261002_PROBE.log` | 94.6KB | 10-02 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261002_REGULAR_COLLECT.log` | 6.6KB | 10-02 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261002_SIGNAL.log` | 584.6KB | 10-02 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261002_SYSTEM.log` | 828.8KB | 10-02 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261002_TRADE.log` | 1.2KB | 10-02 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261002_WARN.log` | 546.7KB | 10-02 15:40 |

## 2. 코드·커밋 상태

- HEAD `1e56ace` · 브랜치 `v9-dev` · 미커밋 42건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 6회 · 타임아웃 1 · 실패 0 · 락 생성 구간 1 · 최장 25.0초(`git diff --numstat`)
    - `git diff --numstat` → timeout · 25.0초 · 락 없음→있음 · 🔴 **이 호출 구간에 락이 생겼다**(동시 발생 — 인과 미확정)
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md
 M docs/정기점검/수익률향상_누적대장.md
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261001.md
?? docs/신동거래/일일/신동_일일_MW0601_20261001.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261002.md
?? docs/신동거래/일일/신동_일일_MW0601_20261002.svg
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261002.md
?? docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/featureset_health_report_20261002.md
?? docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261002.md
?? docs/정기점검/매일점검/MW0601-20260930-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261001-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261002-점검리포트.md
?? docs/정기점검/매일점검/_tmp_append_addendum_20261001.md
?? docs/정기점검/매일점검/_tmp_append_intra_20261001.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261002_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261002_pre.md
?? scripts/nasdaq_leadlag_probe.py
… 외 2건
```

**당일(2026-10-02) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
1e56ace [MW0601] 648차 후속: 장후 자동조치 — F-3
67cff42 [MW0601] 645차 후속: 장후 자동조치 — F-4 · G-1 · G-2 · F-1
89836e3 [MW0601] 639차 후속: 신동 목표 v1 vs v2 확대 비교 — 흐름 5일 + 75일 가격 대리(개정 문서 §8-4)
d9b4063 [MW0601] 637·638·640차 점검 산출물 + 639차 기록 — 9/28·9/29 장전·장중·장후
39f795a [MW0601] 639차: 신동 규격 v2 개정 — 1차 목표가 진입가 뒤에 놓이는 결함 수정
c03b55d [MW0602] 597차 체리픽: 맥점 08:45 결손 차트 TR 보충 — 런처 GUARD 는 보류 (원 2e46abc, dev)
558bd88 [MW0602] 598차 후속 체리픽: requirements.txt 에 markdown==3.4.4 (원 3edd93d, dev)
c561094 [MW0602] 598차 체리픽: 신동 섀도 SHADOW_X4NFA · 채점표 표시 3종 · RETRACTED 로그 · 09:00 봉 결손 내성 (원 6b71762, dev)
3ac32ef [MW0601] 641차 후속: 장후 자동조치 — 637-2 · 638-1
f1efe56 [MW0601] 632차 후속5: MW0602 적용가이드 §10 대응 — 신동 재현 테스트를 PC별로 가르고 불변식으로 보강 + §11 답변
b851e32 [MW0601] 632차 후속4: 신동 일일 리포트 — 파일명·제목·메일에 PC명 표기
b8e9047 [MW0601] 632차 후속: 신동 일일 리포트 — 거래 흐름+손익 vs 섀도 흐름+손익 · PDF · 메일 자동 발송
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

_본문 미열람(설정): `20261002_HOGA.log` 50.0MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261002.txt`** — 28B · 10-02 15:40:26
```
2026-10-02T15:40:26.135460
```

**`data/daily_close_started_20261002.txt`** — 28B · 10-02 15:40:08
```
2026-10-02T15:40:08.550305
```

**`data/daily_reports/strategy_report_20261002_154026.txt`** — 2.2KB · 10-02 15:40:26
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-02 15:40
========================================================
  버전    : v1.0  (91일차)
  판정    : OUTPERFORM
  Live(20일): Sh=2.48  MDD(자본대비)=3.4%
  당일      : WR=미측정(거래0건)  PF=미측정
  롤링20일: 누적 +5335916원  Sh=2.48  MDD(자본대비)=3.4%  MDD(peak대비)=28.7%
  당일손익 : broker(gross) +0원  수수료 0원  net +0원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.000  vwap_position=0.015
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 -35,071원  승률 30.0%  합계 -701,417원
  등급별 순EV(30일): A=+92,624원(67건,승54%)  BROKER=-1,612,145원(3건,승67%)  MANUAL=-17,323원(75건,승53%)
  호라이즌별 순EV(30일): 1m=-1,317원(10건)  3m=+8,285원(40건)  5m=-68,937원(15건)  ?=+9,824원(80건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 15분  5일평균 36분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 14.2pt(5일평균 27.3pt)  1분평균변동 0.57pt(5일평균 0.62pt)
--------------------------------------------------------
  진입 퍼널(2026-10-02, 총 370분):
    FLAT 216 → conf미달 133 → CoherenceGate 7 → 게이트차단 12 → 후보 2 → 진입 0
    게이트별: 체크리스트항목미달=6  콜드스타트/기타(조건부구간)=3  ATR변동성=2  모드필터=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 2건
      └ 상세: JointGateBlock=2
      └ JointGateBlock 2건 (무정보폴백 2건 = 100.0%) [표본 18건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261002.txt`** — 233B · 10-02 15:53:39
```
completed: 2026-10-02 15:53:39
rows: 18703
cols: 97
phase2_fallback: false
horizons_replaced: 5/6
t_load_s: 24.0
t_retrain_s: 191.6
t_total_s: 216.1
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20261002.txt`** — 43B · 10-02 15:47:15
```
auto_shutdown
2026-10-02T15:47:15.137792
```

_다이제스트 대상 8/19개 (중요도순). 제외: `20261002_MICRO.log`, `20261002_DATA.log`, `20261002_PROBE.log`, `launcher_20261002_084001_17771.log`, `20261002_DEBUG.log`, `mainstall_traceback_20261002.log`, `20261002_REGULAR_COLLECT.log`, `peter_feed_push_20261002.log`_

### `logs/20261002_TRADE.log` — 1.2KB · 9행 · 최종 15:40:22

- 형식 평문 · 시각 인식 9행 · INFO=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-02 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-02 10:38:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-02 10:38:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-02 10:41:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-10-02 10:41:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-02 10:41:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-02 11:11:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-02 11:11:00 [INFO] TRADE: [모드필터 차단] LONG->LONG 2계약 C급 (모드=hybrid, 허용=['A', 'B'])
2026-10-02 15:40:22 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×9

**컴포넌트 상위 15** — `Sizer`×3, `ProfitGuard`×2, `JointGateBlock 차단`×2, `Position`×1, `모드필터 차단`×1

### `logs/20261002_WARN.log` — 546.7KB · 2489행 · 최종 15:40:25

- 형식 평문 · 시각 인식 2489행 · WARNING=2489

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-02 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-10-02 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-10-02 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-02 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-02 15:40:18 [WARNING] SYSTEM: [ThresholdRecal] 경보 발생: {'1m': 'UPDATE', '3m': 'UPDATE', '5m': 'UPDATE', '10m': 'UPDATE', '15m': 'UPDATE', '30m': 'UPDATE'}  docs/정기점검/LABEL_THRESHOLD_RECALIBRATION_GUIDE.md 참조
2026-10-02 15:40:19 [WARNING] SYSTEM: [ATRCeilingRecal] UPDATE — floor 3.5→1.0pt (-71%), ceiling 6.0→2.0pt (-67%) — Slack 알림 발송, 수동 검토 필요
2026-10-02 15:40:21 [WARNING] SYSTEM: [EntryHorizonRecal] UPDATE — 경계 3.2/4.4 → 재계산 7.435/10.027 (δ+132%/+128%), 버킷비중(1m/3m/5m)=0%/1%/98% — 참고용 경보(판정 아님)
2026-10-02 15:40:22 [WARNING] SYSTEM: [BrokerNetEOD] net 축 EOD 보정 — 브로커 net +0원 (예탁현금 헤더 스냅샷 2026-10-02 08:41:08, 관측 시 포지션=FLAT, source=stale_snapshot). ⚠ 15:10 이전 스냅샷이라 그 뒤 현금흐름이 반영되지 않았을 수 있다 — 실측(live)과 같은 값으로 읽지 말 것
2026-10-02 15:40:25 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 15분 < 하한 25분 — 최근 5거래일 평균 36분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 19분 · 재지않음 351분
```

</details>

**WARNING — 태그 20종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2169 | 09:00:36 | 15:24:43 | paintEvent slow 82.6ms | size=1955x1124 candles=16 grid=47.1 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=33.5 cross=0.0 | slow_cnt=1 total_cnt=4 overlay_cnt=2 |
| `LiveDBG` | 154 | 08:41:08 | 15:28:09 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 73 | 08:41:18 | 15:24:08 | 그리기 75.9ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `ScalerRefresh` | 16 | 09:24:00 | 15:06:00 | 5분 누적 수익률 +0.426% (임계 ±0.242%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SHAP` | 16 | 11:37:01 | 15:02:01 | 슬로우 감지 934ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `Health` | 12 | 09:00:01 | 14:57:01 | level=WARNING degraded=OFF | latency=1749ms | quality=1.00 | cache_age=50s | exceptions_10m=0 |
| `PipePerf` | 10 | 09:00:01 | 14:57:01 | total=1749ms | S0=4ms S1=15ms S2=0ms S3=0ms S4=139ms S5=1150ms S6=376ms S7=56ms S8=9ms |
| `CB⑤` | 10 | 09:00:01 | 14:57:01 | 파이프라인 1749ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-10-01 10:02:00 cols=['open'] existing_source=rt |
| `CB③-P4` | 6 | 10:16:00 | 10:35:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=10.0%) |
| `HealthPolicy` | 4 | 09:01:00 | 14:27:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1749ms quality=1.00 cache=0s exc10m=0) | cause=S5(1150ms) |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |

**채널** — `SYSTEM`×2477, `HEALTH`×12

**컴포넌트 상위 15** — `ChartDBG`×2169, `LiveDBG`×154, `OptionFlowChart`×73, `ScalerRefresh`×16, `SHAP`×16, `Health`×12, `PipePerf`×10, `CB⑤`×10, `SessionBackfill`×6, `CB③-P4`×6, `HealthPolicy`×4, `출처축`×2, `SessionStateDrop`×2, `Canary`×2, `MainStallTrace`×2

### `logs/20261002_SYSTEM.log` — 828.8KB · 5721행 · 최종 15:47:15

- 형식 평문 · 시각 인식 5696행 · INFO=5696, PLAIN=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:44 [INFO] SYSTEM: [FaultHandler] 로테이션 — 9.2MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-10-02 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18204 | 행감지=30s all_threads=True
2026-10-02 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.49s | predictions=0.08s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.12s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-02 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-02 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
  …
2026-10-02 15:46:08 [INFO] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=410 inserted=1 open_fixed=1 mismatch=0
2026-10-02 15:46:08 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-02) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-02 15:47:15 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-02 15:47:15 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-02 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×5696

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1087, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `System`×100, `MicroRegime`×92, `OptionChain`×81, `OptionBook`×79, `RegimeFingerprint`×67, `IntradayRegime`×27, `PumpGuard`×26

### `logs/20261002_SIGNAL.log` — 584.6KB · 5138행 · 최종 15:40:22

- 형식 평문 · 시각 인식 5138행 · WARNING=2108, INFO=3030

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-10-02 15:10:01 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-02 15:40:22 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-02 15:40:22 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 105분(28.4%) / DN 10분(2.7%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-02 15:40:22 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-02 age=36m extreme=648 refresh=36 grade_x=137 cb3=0
2026-10-02 15:40:22 [INFO] SIGNAL: [ModelHealth] date=2026-10-02 앙상블유효가동률=72.4% | 파이프라인 370분 | ConstOut 10회/20분 {"3m": {"events": 8, "minutes": 16}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 82분 | 장중재학습 0회 | CB③ ready 294분/370분 (79%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1458 | 09:00:02 | 15:06:01 | 1m 'macro_vix' scale=0.0122 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 204 | 09:00:00 | 14:55:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 180 | 09:00:00 | 15:04:00 | ts=08:59 horizon=1m age=1m max_z=-14.76(retail_futures_net) extreme=1 adj=1 |
| `Checklist` | 151 | 09:06:01 | 15:09:00 | 신뢰도 미달 33.3% < 41.1% → 강제 X등급 |
| `WeightCollapse` | 82 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 18 | 08:45:08 | 08:45:08 | 1m CORE 'cvd_divergence' raw_std≈0(0.0159) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 10 | 09:35:00 | 14:02:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 4 | 09:07:00 | 09:22:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 1 | 13:00:00 | 13:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3419 < 필요 0.3950 (conf_floor=0.330, min_conf=0.395, span=0.0041, auc=0.542). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5138

**컴포넌트 상위 15** — `ScalerFloor`×1518, `SIGNAL`×740, `Ensemble`×372, `FQAdj`×369, `MetaGate`×368, `ZeroDiag`×359, `Model`×210, `ScalerMonitor`×181, `Checklist`×158, `ATR-Horizon`×140, `차단`×111, `ToxicityGate`×98, `MicroRegime`×92, `WeightCollapse`×82, `InstabilityGate`×75

### `logs/20261002_LEARNING.log` — 290.3KB · 2872행 · 최종 15:40:22

- 형식 평문 · 시각 인식 2862행 · WARNING=147, INFO=2715, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3127 < conf_floor=0.3300 (span=0.00029 auc=0.539 out_max=0.3127, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.514 out_max=0.3295 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
2026-10-02 08:40:50 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00008 auc=0.532 out_max=0.3238 (n=105) → 보정 재적용
2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.1379 < conf_floor=0.3300 (span=0.00091 auc=0.675 out_max=0.1379, 기저율=0.1375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-02 15:40:22 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-02 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-02 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-02 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-02 15:40:22 [INFO] LEARNING: [Sigma] EOD sigma_20=0.02920% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 50 | 08:40:50 | 11:51:00 | 하한 도달불가 — out_max=0.3127 < conf_floor=0.3300 (span=0.00029 auc=0.539 out_max=0.3127, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:30m` | 45 | 08:40:50 | 14:49:00 | 하한 도달불가 — out_max=0.1379 < conf_floor=0.3300 (span=0.00091 auc=0.675 out_max=0.1379, 기저율=0.1375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 20 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00076 auc=0.456 out_max=0.3253 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 11 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 10 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00009 auc=0.482 out_max=0.2500 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 5 | 08:40:51 | 12:45:00 | 축퇴 감지 — span=0.00312 auc=0.353 out_max=0.3140 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 2 | 08:40:59 | 13:19:00 | 복원한 보정기가 축퇴 상태 — span=0.00765 auc=0.512 out_max=0.3385 (n=2368) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 2 | 12:20:00 | 14:26:00 | total=311ms raw_fetch=10ms pred_select=36ms pred_update=60ms pred_insert=1ms verified=5 |
| `Consolidator` | 1 | 15:40:09 | 15:40:09 | 구간 'STABLE_TREND' 최근 3일 풀링(n=210) 기대손익 -0.353pt (CI상단 -0.147pt) < 0 → 패널티 +0.04 (참고 정확도 23.3%) |
| `DriftAdjuster` | 1 | 15:40:09 | 15:40:09 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 18일) |

**채널** — `LEARNING`×2862

**컴포넌트 상위 15** — `LEARNING`×1213, `SGD`×369, `sigma`×357, `Bias⚠`×261, `Bias`×138, `Calibration:1m`×98, `Calibration:30m`×89, `MetaConf`×78, `OnlineLearner`×68, `ScalerWarmup`×42, `Calibration:3m`×38, `BiasReset`×27, `Calibration:5m`×21, `Calibration:10m`×18, `SHAP`×11

### `logs/20261002_HEALTH.log` — 3.6KB · 25행 · 최종 14:58:00

- 형식 평문 · 시각 인식 25행 · WARNING=12, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1749ms | quality=1.00 | cache_age=50s | exceptions_10m=0
2026-10-02 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=504ms | quality=1.00 | cache_age=109s | exceptions_10m=0
2026-10-02 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 389ms (표본 20분)
2026-10-02 09:39:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=395ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-10-02 09:40:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=325ms | quality=1.00 | cache_age=57s | exceptions_10m=0
  …
2026-10-02 14:27:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=334ms | quality=1.00 | cache_age=14s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-02 14:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=419ms | quality=1.00 | cache_age=184s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-02 14:40:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=474ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-02 14:57:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1130ms | quality=1.00 | cache_age=164s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-02 14:58:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=562ms | quality=1.00 | cache_age=39s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 12 | 09:00:01 | 14:57:01 | level=WARNING degraded=OFF | latency=1749ms | quality=1.00 | cache_age=50s | exceptions_10m=0 |

**채널** — `HEALTH`×25

**컴포넌트 상위 15** — `Health`×24, `HealthTrend`×1

### `logs/retrain_eod_20261002.log` — 38.3KB · 394행 · 최종 16:19:21

- 형식 평문 · 시각 인식 189행 · WARNING=15, WARN=1, INFO=174, PLAIN=204

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 15:50:02,672 [INFO] EOD_RETRAIN: =======================================================
2026-10-02 15:50:02,673 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-02 15:50:02,673 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-02 15:50:02,673 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-02 15:50:02,673 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
[안내] DB 행 삭제는 비활성입니다. 켜기 전에 docs/정기점검/보관정책_MW0601-20260818.md 의 근거를 먼저 읽으세요.
2026-10-02 16:20:10,801 [INFO] EOD_RETRAIN: [검증 캠페인] 요약: 게이트 ablation 리포트=OK | 호라이즌 conf-층화 검정=OK | 검증 캠페인 판정 리포트=OK | 피처셋 건강 리포트=OK | CVD 앵커 대조 리포트=OK | 조기청산 반사실 [49]=OK | 라우팅 밴드 성과 [D9-B]=OK | 방향 처분 실험 [40-B]=OK | 섀도우 TB 재학습=OK | 분위 회귀 재학습=OK | 메타라벨 분류기 재학습=OK | MAE/MFE 분석=OK | 월간 로그 정리=OK
2026-10-02 16:20:10,905 [INFO] EOD_RETRAIN: 판정 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\validation_campaign_report_20261002.md
2026-10-02 16:20:10,908 [INFO] EOD_RETRAIN: 피처셋 건강 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\featureset_health_report_20261002.md
2026-10-02 16:20:10,908 [INFO] EOD_RETRAIN: =======================================================
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:39 | 15:52:47 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-10-01 14:38:00 ≥ 홀드아웃 시작=2026-09-23 12:45:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-01 14:38 >= holdout_start=2026-09-23 12:45 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-01 … |
| `UnitMismatch` | 4 | 15:50:13 | 16:11:17 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/22456행 제외 (559차 P1'-2) — 남은 21010행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `BackfillFilter` | 2 | 15:50:13 | 16:11:26 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 22384/44840 제외 (418차 결정 1) — 남은 22456행 |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-02 | 최신 2026-10-01 · 기준 7거래일. 복구: python scripts/collect_regular_futures.py --from 20261002 --to 20261002 |
| `Retrain` | 1 | 15:50:55 | 15:50:55 | 3m 교체 보류(EOD 모델가드) — acc 하락 0.0378 > 허용 0.0250 (new=0.3882 old=0.4260) — 참고용 저장, 구모델 유지 |
| `RegimeFingerprint` | 1 | 15:53:39 | 15:53:39 | 백필 0행 제외 — 필터가 무효일 수 있다. 18703행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |
| `-` | 1 | ??:??:?? | ??:??:?? | ] 1개 파일 0.5MB -> 202609_WARN.zip |

**채널** — `LEARNING`×63, `SIGNAL`×49, `EOD_RETRAIN`×45, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×196, `ScalerFloor`×42, `Retrain`×22, `EOD_RETRAIN`×18, `검증 캠페인`×15, `RF`×9, `ShadowTB`×8, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `MetaLabelClf`×6

### `logs/retrain_intraday_20260707_100200.log` — 4.6KB · 39행 · 최종 10:02:34

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-07 10:02:00,162 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-07 10:02:00,162 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-07 10:02:00,163 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-07 10:02:00,163 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_1855d783.json
2026-07-07 10:02:03,012 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-07 10:02:34,551 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.41s | old_acc=0.3805)
2026-07-07 10:02:34,554 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-07 10:02:34,555 [INFO] LEARNING: [Retrain] 완료 | 31.5초 | 성공=6/6 호라이즌
2026-07-07 10:02:34,556 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.4s 데이터=20000행
2026-07-07 10:02:34,558 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_1855d783.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 111 |
| 사이저 호출(`[Sizer]`) | 3 |

### CB③ 판정 가능 시간 — **294분 / 370분 (79%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×3

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×3

### 차단 사유 111건 · 41종

| 건수 | 사유 |
|---|---|
| 26 | 등급X — 미통과 항목: 2_confidence |
| 6 | ATR 0.78pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 6 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 5 | ATR 0.81pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 5 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.80pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.89pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.72pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.77pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.76pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.74pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×26, `3_vwap`×7, `6_foreign`×7, `5_ofi`×4, `4_cvd`×3, `7_prev_bar`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 30건 · 최대 12016ms · 5초 초과 2건

상위 — 12016ms, 5250ms, 4687ms, 4172ms, 4000ms, 3922ms, 3907ms, 3782ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:36 | 5250ms | 1749ms | **3501ms (67%)** |
| 12:20:11 | 12016ms | 2769ms | **9247ms (77%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261002_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:25 2026-10-02 15:40:25 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 15분 < 하한 25분 — 최근 5거래일 평균 36분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 19분 · 재지않음 351분
--- [SHAP] 슬로우 ×8(표본)
11:37:01 2026-10-02 11:37:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 934ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:45:01 2026-10-02 11:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 946ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:02:01 2026-10-02 12:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 961ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:55:02 2026-10-02 12:55:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 913ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-02 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4000ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4000 band=INFO since_pipe_s=NA
09:00:03 2026-10-02 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3907ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3907 band=INFO since_pipe_s=0.1
09:00:36 2026-10-02 09:00:36 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=29 watchdog_alerted=[] | [MainStall] stall_ms=5250 band=WARN since_pipe_s=32.8
09:02:10 2026-10-02 09:02:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=9 watchdog_alerted=[] | [MainStall] stall_ms=2391 band=INFO since_pipe_s=9.9
```

### `logs/20261002_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-02 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4548) | 앙상블 제외는 유지
09:44:01 2026-10-02 09:44:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4298) | 앙상블 제외는 유지
09:54:00 2026-10-02 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3884) | 앙상블 제외는 유지
11:14:00 2026-10-02 11:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3953) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:22 2026-10-02 15:40:22 [INFO] SYSTEM: [CB③계측] 조건성립 17분 / 판정가능 294분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-02 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-02 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-10-02 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-10-02 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:22 2026-10-02 15:40:22 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:22 2026-10-02 15:40:22 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:08 2026-10-02 15:11:08 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:26 2026-10-02 15:40:26 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:15 2026-10-02 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:26 2026-10-02 15:40:26 [INFO] SYSTEM: [Notify] ℹ️ [15:40:26] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:26 2026-10-02 15:40:26 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 394초
15:40:26 2026-10-02 15:40:26 [INFO] SYSTEM: 자동 종료 예약 — 409초 후 Qt 이벤트 루프 종료
```

### `logs/20261002_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
13:00:00 2026-10-02 13:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3419 < 필요 0.3950 (conf_floor=0.330, min_conf=0.395, span=0.0041, auc=0.542). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-10-02 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0270 dir=-1)
09:35:00 2026-10-02 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-10-02 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-10-02 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0270 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-10-02 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-10-02 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-10-02 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-02 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:42 2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:42 2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:42 2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:42 2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
--- 안전망 ×8(표본)
09:07:00 2026-10-02 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-02 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-02 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-02 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261002_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3127 < conf_floor=0.3300 (span=0.00029 auc=0.539 out_max=0.3127, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:50 2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.514 out_max=0.3295 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
08:40:50 2026-10-02 08:40:50 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00008 auc=0.532 out_max=0.3238 (n=105) → 보정 재적용
08:40:50 2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.1379 < conf_floor=0.3300 (span=0.00091 auc=0.675 out_max=0.1379, 기저율=0.1375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

### `logs/retrain_eod_20261002.log`
```
--- ConstOut ×1(표본)
??:??:?? | `[51]` | `아직 미확인` | ConstOut 호라이즌 건강도 |
--- 축퇴 ×1(표본)
??:??:?? | `[45]` | `cal_guard_flap_watch` | 축퇴 가드 플래핑 (게이지) |
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261002_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:22 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261002_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 21 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 33 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 42 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 91 | 09:54:00 [WARNING] paintEvent slow 98.7ms | size=1955x1124 candles=70 grid=37.6 spans=0.0 candles=2.8 dir=0.3 regime=3.9 markers… |
| 12:00 | 장중 중간점 | 112 | 11:54:01 [WARNING] paintEvent slow 96.3ms | size=1955x1124 candles=190 grid=28.8 spans=2.0 candles=7.7 dir=0.7 regime=4.5 marker… |
| 14:00 | 장중 후반 · 장중 재학습 | 95 | 13:54:02 [WARNING] _tick_header 간격 2188ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2188 band=… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 109 | 15:04:00 [WARNING] paintEvent slow 157.7ms | size=1955x1124 candles=380 grid=38.4 spans=3.8 candles=18.7 dir=2.0 regime=7.5 mark… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 108 | 15:12:00 [WARNING] paintEvent slow 127.1ms | size=1955x1124 candles=387 grid=26.8 spans=5.8 candles=19.3 dir=1.4 regime=7.0 mark… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 5 | 15:40:18 [WARNING] 경보 발생: {'1m': 'UPDATE', '3m': 'UPDATE', '5m': 'UPDATE', '10m': 'UPDATE', '15m': 'UPDATE', '30m': 'UPDATE'}  d… |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261002_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 96 | 08:40:44 [INFO] 로테이션 — 9.2MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 141 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 189 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 197 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 172 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 181 | 13:54:01 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 169 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 135 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 59 | 15:34:01 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 9 | 15:41:08 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:08 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261002_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0159) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 127 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 223 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 174 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 153 | 11:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 162 | 13:54:01 [WARNING] 신뢰도 미달 32.5% < 39.5% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 99 | 15:04:00 [WARNING] ts=15:03 horizon=1m age=34m max_z=+7.84(is_close_volatile) extreme=1 adj=1 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:22 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261001 | 15:47 | 로그 본문 |
| 20260930 | 15:47 | 로그 본문 |
| 20260929 | 15:47 | 로그 본문 |
| 20260928 | 15:47 | 로그 본문 |
| 20260926 | 16:50 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261002** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-30 (MW0601 644ì°¨ â ì¥í ì ê²)
## 2026-09-30 (MW0601 645ì°¨ â ì¥í ìëì¡°ì¹: F-4 ë½ ì£¼ì¸ ì§ë¨ Â· G-1 PreRetrain ì°í íì Â· G-2 git 1í ì¤ë
## 2026-10-01 (MW0601 646ì°¨ â ì¥ì  ì ê²)
## 2026-10-01 (MW0601 647ì°¨ â ì¥ì¤ ì ê²)
## 2026-10-01 (MW0601 648ì°¨ â ì¥í ì ê²)
## 2026-10-01 (MW0601 649ì°¨ â 648ì°¨ íì ì¥í ìëì¡°ì¹: F-3 ìì§ê¸° git í¸ì¶ ê¸°ë¡)
## 2026-10-02 (MW0601 650ì°¨ â ì¥ì  ì ê²)
## 2026-10-02 (MW0601 651ì°¨ â ì¥ì¤ ì ê²)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 F-3 ìë ê³ì¸¡ íë³¸ì í¸ì, íë³¸ 1ê±´ì´ë¼ íì  ê²°ë¡  ë³´ë¥. â¢ ë³í ìì, ê´ì¸¡ì¼ 5ì¼ ì ì§. â£ Â§11 ìë ì ì í¸ #1Â·#2ë¥¼ ë¦¬í¬í¸ìì "ë¯¸ë°ì êµ¬ê° ì§ê³ í¹ì±"ì¼ë¡ ëªì ì ì (ì´ìì ì¼ë¡ ì¬ë¦¬ì§ ìì) â í¥í ì¥ì¤ ì ê² ì¸ìë¤ë ê°ì í´ìì ì ì©í  ê².

**Why**: â ì í¨ì â (ì¬ì¸ì© ì  ì´ë¯¸ ìë ë¬¸ì ì¸ì§ íì¸) ì¤ì + 313ì°¨ ìì¹(ì¤íì¼ ë¯¸íì  ì ì­ì  ê¸ì§). â¡ë íë³¸ 1ê±´ì¼ë¡ í¨í´ ë¨ì  ê¸ì§(313ì°¨). â£ë ì¥ì¤ ì ê² í¹ì ì ì§ê³ ìí°í©í¸ë¥¼ ì´ìì ì¼ë¡ ìëª» ì¬ë¦¬ë©´ ë§¤ ì¥ì¤ ì ê²ë§ë¤ "ë£¨í 56% ì»¤ë²ë¦¬ì§"ê° ë°ë³µ ì¤ë³´ë  ìíì´ ìì´ ëªìì ì¼ë¡ êµì í´ ëë¤.

**How to apply**: F-1 ì ì© ì ë³ë ì¸ììì `scripts/collect_evidence.py:2507~2520` ìì (ì¥ì  650ì°¨ ê³íê³¼ ëì¼, ë´ì© ì¤ë³µ ìëµ). 482ì°¨ F-3 ìë ê³ì¸¡ì ê³ì ìë ìì§ ì¤(ì½ë ë³ê²½ ë¶íì). Â§11 í´ì êµì ì ì´ ì¤í¬ì í¥í ì¥ì¤ ì ê² ìµê´ì ë°ì â SKILL.md ìì²´ ìì ì ì´ë² ì¸ììì íì§ ìì(í¨í´ì´ ë°ë³µëë©´ B-0 ì²´í¬ë¦¬ì¤í¸ì "ìì§ ìì ì´ ê±°ëì¼ ì¤ì´ë©´ ë¶ëª¨ë¥¼ '09:00~ìì§ìê°'ì¼ë¡ ì½ëë¤" ì£¼ì ì¶ê°ë¥¼ ê³ ë ¤í  ê², ì§ê¸ì ê°ì¤ ìì¤).

**ê²ì¦**: `git --no-optional-locks log --since="2026-10-02 00:00:00"` ì¬íì¸(ë¹ì¼ ì»¤ë° 0ê±´, ë³í ì¸ì ìì). `python scripts/git_lock_guard.py --check`(ëì´ 86ì´, HOLD). `python scripts/collect_evidence.py --phase intra --pc MW0601 --out-auto` ì ì ì¤í(75.2KB ë¤ì´ì ì¤í¸ ìì±). ë§¤ë¶ ë£¨í ì»¤ë²ë¦¬ì§ Â§7 "08:55~15:12 êµ¬ê° 10ë¶ ì´ì ê³µë°±: 0ê±´" ìì¹ë¡ â£ í´ì êµì°¨ê²ì¦.

**[12:41 KST ì¶ê°] 651ì°¨ O-i1 ìë ¥ í´ì**: `.git/index.lock`(12:28 KST ë°ìë¶)ì´ ëì´ 0.2ìê°Â·ì¥ git íë¡ì¸ì¤ 0ê°ë¡ STALE íì ëì´ `git_lock_guard.py --reclaim`ì¼ë¡ ì¦ì íì(ì´ë¦ë³ê²½ ì°í: `index.lock.stale_20261002034126_6`, ë¶ì¤ë¬ê¸° ìì²´ë 648-2ì í©ë¥, Windows ìª½ ì ë¦¬ íìíë ì»¤ë°ì ë§ì§ ìì). íì í `--check` â `OK index.lock ìì` íì¸. O-i1ì ì¥ì¤ ì  ììì ë«ëë¤. ì¶ê°ë¡ `scripts/probe_cybos_nasdaq_mirror.py`(ë¯¸ì¶ì , ì¥ì¤ ì¤í ê¸ì§ ì£¼ì í¬í¨, ë¯¸ì¤í) ë°ê²¬ â ì´ ì ê² ì¸ìê³¼ ë¬´ê´í ë³í ìì íì , íì  ìí¥ ìì(651-1 ì°¸ì¡°). `git log --since` ìê°ë ë¯¸íê¸° ì UTCë¡ í´ìëë ì ë íì¸(651-2 ì°¸ì¡°, ì¤ëì ìí¥ ìì).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-30 (MW0601 644차 — 장후 점검)
## 2026-09-30 (MW0601 645차 — 장후 자동조치)
## 2026-10-01 (MW0601 646차 — 장전 점검)
## 2026-10-01 (MW0601 647차 — 장중 점검)
## 2026-10-01 (MW0601 648차 — 장후 점검)
## 2026-10-01 (MW0601 649차 — 648차 후속 장후 자동조치)
## 2026-10-02 (MW0601 650차 — 장전 점검)
## 2026-10-02 (MW0601 651차 — 장중 점검)
```

미완료 체크박스 **2954건** (끝에서 30건)
```
- [ ] **606-2/O-t2계열 (지속, 변화 없음)** SessionStateDrop — 10-01 거래일 전환 시 재현, 우회 성공으로 실질 피해 없음. F-1 미적용 그대로. 10/2 거래일 전환 재현 여부 O-t2로 이월.
- [ ] **633-1 (P2, 지속 — 오늘로 6일째, 변화 없음)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 미확인·미커밋 지속.
- [ ] **646-1 (사용자, 커밋 대기 — 지속)** 9/30분 미커밋 실질 변경 4건(`dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`·`docs/정기점검/수익률향상_누적대장.md`·문서제목손상문서) — 16:20 KST 기준 동일하게 미커밋 확인(이번 세션이 추가한 변경 포함). 경로 명시해 `git add` 후 커…
- [ ] **O-t1~O-t5 (신규 발급)** O-t1(access violation 재현 여부, 5관측일째) · O-t2(SessionStateDrop 10/2 재현 여부) · O-t3(git diff 타임아웃 재재현 시 락 생성 패턴) · O-t4(메인스레드 정지 482차F-3 섀도 추가표본) · O-t5(문서제목 손상 사용자 확인 여부). 다음 …
- [ ] **648-2 (P2, 신규)** `.git/objects/**/tmp_obj_*` 임시 블롭 부스러기 8건(코웍 마운트의 unlink 제한, index.lock과 동일 구조) — F-3(git diff 타임아웃 가설)의 범위를 "타임아웃 경로"에서 "코웍 마운트 경유 git diff 전반"으로 넓힐지 검토. Windows에서 `--reclai…
- [ ] **648-3 (P2, 참고— 오늘 발생 아님)** `dev_memory/DECISION_LOG.md` 09-30(642차) 작성 구간에 한글 1글자 인코딩 손상 발견(파일 내 바이트 3,478,123 부근, UnicodeDecodeError 유발) — 이번 세션 작성분은 정상 확인. 다음에 파일을 열 때 수동 교정 권장, 긴급성 낮음.
- [ ] **F-3 판정 (지속)** 다음 코웍 수집 타임아웃 재현 시 §2 `git 호출 기록`에서 「락 생성 구간」이 타임아웃 호출과 겹치는지 기록. 3회 쌓이면 원인 판정(겹침 → kill 경로 / 비겹침 → 세션 임시 git 호출). 648-2(tmp_obj)와 같은 환경 축인지 함께 볼 것.
- [ ] **F-1·사용자 조치 1·2 (사용자 몫, 이월)** 문서 제목 확인(7일째 예정) · `docs/정기점검/수익률향상_누적대장.md`·`docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 커밋 — 자동조치는 dev_memory 2건만 커밋했다.
- [ ] **F-3 (지속, P1 — 5번째 재현)** `.git/index.lock` 재발(10/2 장전, 09:00 KST경). 9/30(x3)+10/1 장중(x1)에 이어 5번째. 타임아웃=락 생성이 1:1이 아님(648차 관측 그대로 유지). 다음 재현 시 §2 「git 호출 기록」에서 락 생성 구간이 타임아웃 호출과 겹치는지 계속 기록할 것.
- [ ] **F-1 (P1, 신규)** 증거수집기(`scripts/collect_evidence.py:2507~2520`)의 "락 자가점검" 한 줄이 같은 다이제스트의 「git 호출 기록」(호출별 추적, 573·591·508행)과 상충하는 것을 10/2 장전에 처음 확인(§2가 "이 수집 실행은 락을 만들지 않았다"라고 적었지만, 바로 아래 호출별 추적…
- [ ] **637-1/606-4/641-1 (지속, 5관측일째)** 부팅 구간 access violation — 오늘도 PID 18204에서 3건, 정규장 이후 재발 0건. 313차 원칙상 10거래일 표본 필요(현재 5일, 6일째부터 과반). 사용자 결정 대기 그대로.
- [ ] **606-2/O-t2 최종 판정 — 재현함** SessionStateDrop이 10/1→10/2 날짜 전환 시 재현(08:41:08). EOD 마커 파일 우회 성공으로 실질 피해 없음. F-1(날짜전환 마커 승계, 「F-1」이 위 증거수집기 F-1과 이름이 겹치므로 — 이쪽은 **"SessionStateDrop F-1"**로 구분해 부른다) …
- [ ] **646-1 (지속, 커밋 대기)** 미커밋 19건(실질 변경 2건 M + 미추적 17건) — 10/2 08:58 기준 동일. 오늘은 수집기 git diff 실패(F-3 재현)로 실질/EOL 파생 분해를 못 받음 — 필요하면 수동 `git --no-optional-locks diff --numstat <경로 한정>`으로 재측정할 것.
- [ ] **633-1 (P2, 지속 — 오늘로 7일째)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 미확인·미커밋 지속.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` 부스러기 8건, 16.7시간 스테일 — 변화 없음. Windows에서 `--reclaim` 필요.
- [ ] **648-3 (P2, 지속 — 참고)** `DECISION_LOG.md` 09-30(642차) 구간 한글 인코딩 손상 1글자 — 변화 없음, 긴급성 낮음.
- [ ] **O-p1 (신규 발급)** `.git/index.lock` 최종 판정(스테일 확정 여부) — 장전 종료 시점 나이 352초(임계 600초 미달, HOLD). 장중 점검이 재확인해 판정/보류/이월 중 하나로 닫을 것.
- [ ] **F-3 (지속, P1 — 통산 6번째 재현, 오늘 2번째)** `.git/index.lock` 재발 — 이번엔 장중 자신의 증거수집 중(12:28 KST). 나이 86초, HOLD. 장후가 재확인해 판정/보류/이월 중 하나로 닫을 것.
- [ ] **F-1 (지속, P1 — 2번째 표본 확인)** 증거수집기 "락 자가점검" 오판정 문구가 오늘 장중에도 재현(§2 "이 수집 실행은 락을 만들지 않았다" vs 같은 다이제스트의 「락 없음→있음」 기록 상충). 가설 단계 → 재현 패턴으로 격상 가능. 수정 계획은 650차와 동일, 적용은 장후 이후.
- [ ] **O-i1 (신규 발급)** `.git/index.lock` 최종 판정(스테일 확정 여부, 12:28 KST 발생) — 장중 종료 시점 나이 86초(임계 600초 크게 미달, HOLD). 장후 점검이 재확인해 판정/보류/이월 중 하나로 닫을 것.
- [ ] **1-5 (신규, 확인 필요 — 표본 1건)** 12:20:11 메인 스레드 12,016ms 정지(오늘 최대), CB⑤ 사각(잔차) 9247ms(77%). 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`) 표본에 편입. 12:21:00 HealthPolicy Degraded 선제차단 1회, 1분 내 정상 복귀. 확정 결론 금…
- [ ] **637-1/606-4/641-1 (지속, 5관측일째, 변화 없음)** 부팅 구간 access violation — 장중 추가 재발 0건(09:00 개장 이후). 313차 원칙상 10거래일 표본 필요(현재 5일). 사용자 결정 대기 그대로.
- [ ] **606-2/O-t2계열 (지속, 변화 없음)** SessionStateDrop — 장중에는 해당 이벤트 재발 여지 없음(거래일 전환 1회성). 10/2 재현은 장전이 이미 "판정: 재현함"으로 닫음.
- [ ] **633-1 (P2, 지속 — 오늘로 8일째)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 미확인·미커밋 지속.
- [ ] **646-1 계열 (지속, 커밋 대기)** 미커밋 24건(M 4건 + 미추적 20건, 12:30 KST 기준) — 전부 기존 패턴의 자연 누적, 신규 실질 변경 없음. 경로 명시해 `git add` 후 커밋 권고.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` 부스러기 8건, 20.1시간 스테일 — 변화 없음. Windows에서 `--reclaim` 필요.
- [ ] **648-3 (P2, 지속 — 참고)** `DECISION_LOG.md` 09-30(642차) 구간 한글 인코딩 손상 1글자 — 변화 없음, 긴급성 낮음.
- [ ] **§11 자동 적신호 해석 교정 메모 (651차)** 매분 루프 커버리지 56.3%·162분 공백은 장중 수집 시점(12:27 KST, 거래일 진행 중)이 분모(09:00~15:10)를 다 못 채워서 생기는 집계 특성이며 실결손이 아님(08:55~15:12 10분 이상 공백 0건으로 확인). 향후 장중 점검 세션은 이 해석을 기본값으로 삼을 …
- [ ] **651-1 (신규, 참고)** 장중 마무리 재확인(12:38 KST) 중 `scripts/probe_cybos_nasdaq_mirror.py`(신규 미추적, 나스닥 선물 Cybos 경로 탐색용, 장중 실행 금지 주석 포함) 발견 — 실행 로그·프로세스 없음, 작성만 됨, 커밋 없음. 이 점검 세션 외 다른 작업이 동시 진행 중이었다는 뜻. …
- [ ] **651-2 (신규, 운영 메모)** `git log --since`에 시간대 미표기 타임스탬프를 쓰면 git이 UTC로 해석해 KST 00:00~09:00 구간 커밋을 놓칠 수 있음을 651차에서 발견(오늘은 그 구간 커밋 0건이라 실질 영향 없음). 다음 점검부터 `--since="<날짜> 00:00:00 +0900"`처럼 시간대 명시 권…
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 판정/보류/이월 중 하나로 닫을 것.

## 2026-10-02 (MW0601 651차 — 장중 점검)

- [x] **651-0(오늘 장중 판정 완료)** P0 없음. 매분 파이프라인 09:00~12:28 구간 10분 이상 공백 0건(정상). 진입 0건은 저신호 장세(차단 사유 분해로 확인, 2_confidence 26/56건=46%). 상세는 `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` 장중 절 참조.
- [ ] **F-3 (지속, P1 — 통산 6번째 재현, 오늘 2번째)** `.git/index.lock` 재발 — 이번엔 장중 자신의 증거수집 중(12:28 KST). 나이 86초, HOLD. 장후가 재확인해 판정/보류/이월 중 하나로 닫을 것.
- [ ] **F-1 (지속, P1 — 2번째 표본 확인)** 증거수집기 "락 자가점검" 오판정 문구가 오늘 장중에도 재현(§2 "이 수집 실행은 락을 만들지 않았다" vs 같은 다이제스트의 「락 없음→있음」 기록 상충). 가설 단계 → 재현 패턴으로 격상 가능. 수정 계획은 650차와 동일, 적용은 장후 이후.
- [ ] **O-i1 (신규 발급)** `.git/index.lock` 최종 판정(스테일 확정 여부, 12:28 KST 발생) — 장중 종료 시점 나이 86초(임계 600초 크게 미달, HOLD). 장후 점검이 재확인해 판정/보류/이월 중 하나로 닫을 것.
- [ ] **1-5 (신규, 확인 필요 — 표본 1건)** 12:20:11 메인 스레드 12,016ms 정지(오늘 최대), CB⑤ 사각(잔차) 9247ms(77%). 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`) 표본에 편입. 12:21:00 HealthPolicy Degraded 선제차단 1회, 1분 내 정상 복귀. 확정 결론 금지(313차) — 다음 거래일 이후 누적 관찰.
- [ ] **637-1/606-4/641-1 (지속, 5관측일째, 변화 없음)** 부팅 구간 access violation — 장중 추가 재발 0건(09:00 개장 이후). 313차 원칙상 10거래일 표본 필요(현재 5일). 사용자 결정 대기 그대로.
- [ ] **606-2/O-t2계열 (지속, 변화 없음)** SessionStateDrop — 장중에는 해당 이벤트 재발 여지 없음(거래일 전환 1회성). 10/2 재현은 장전이 이미 "판정: 재현함"으로 닫음.
- [ ] **633-1 (P2, 지속 — 오늘로 8일째)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 미확인·미커밋 지속.
- [ ] **646-1 계열 (지속, 커밋 대기)** 미커밋 24건(M 4건 + 미추적 20건, 12:30 KST 기준) — 전부 기존 패턴의 자연 누적, 신규 실질 변경 없음. 경로 명시해 `git add` 후 커밋 권고.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` 부스러기 8건, 20.1시간 스테일 — 변화 없음. Windows에서 `--reclaim` 필요.
- [ ] **648-3 (P2, 지속 — 참고)** `DECISION_LOG.md` 09-30(642차) 구간 한글 인코딩 손상 1글자 — 변화 없음, 긴급성 낮음.
- [ ] **§11 자동 적신호 해석 교정 메모 (651차)** 매분 루프 커버리지 56.3%·162분 공백은 장중 수집 시점(12:27 KST, 거래일 진행 중)이 분모(09:00~15:10)를 다 못 채워서 생기는 집계 특성이며 실결손이 아님(08:55~15:12 10분 이상 공백 0건으로 확인). 향후 장중 점검 세션은 이 해석을 기본값으로 삼을 것 — 패턴이 반복되면 B-0 체크리스트에 명시 주석 추가를 검토.
- [ ] **651-1 (신규, 참고)** 장중 마무리 재확인(12:38 KST) 중 `scripts/probe_cybos_nasdaq_mirror.py`(신규 미추적, 나스닥 선물 Cybos 경로 탐색용, 장중 실행 금지 주석 포함) 발견 — 실행 로그·프로세스 없음, 작성만 됨, 커밋 없음. 이 점검 세션 외 다른 작업이 동시 진행 중이었다는 뜻. 판정 영향 없음. 장후가 커밋 여부·내용 변화 재확인할 것. 미커밋 건수 24→25.
- [ ] **651-2 (신규, 운영 메모)** `git log --since`에 시간대 미표기 타임스탬프를 쓰면 git이 UTC로 해석해 KST 00:00~09:00 구간 커밋을 놓칠 수 있음을 651차에서 발견(오늘은 그 구간 커밋 0건이라 실질 영향 없음). 다음 점검부터 `--since="<날짜> 00:00:00 +0900"`처럼 시간대 명시 권고. 필요시 SKILL.md §0-③ 예시 명령에 반영 검토.
- [x] **O-i1 판정 완료 (12:41 KST)** `.git/index.lock`(12:28 KST 발생분) 스테일 확정 후 `--reclaim`으로 장중 세션 안에서 자력 회수 완료. 장후 이월 불필요. 부스러기(T2) 10건으로 1건 증가, 648-2가 계속 추적.

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

### `data/heartbeat_MW0601_20261002.json` — 245B · 10-02 15:46:53
```json
{
 "pid": 18204,
 "written_at": "2026-10-02T15:46:53",
 "beat_epoch": 1790923608.5923064,
 "beat_age_sec": 4.5,
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

- 파일 최종 기록: **10-02 15:53:40**

| 키 | 값 | 수집 대상일(2026-10-02)과 일치 |
|---|---|---|
| `date` | 2026-10-02 | 예 |
| `p8_last_success_date` | 2026-10-02 | 예 |
| `eod_retrain_ok_date` | 2026-10-02 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-02 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-01) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-02 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-01) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261002_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 18204: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:44 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 18204 | 08:40:44 | 15:47:15 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 190개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` | 45.4KB | 10-02 12:42 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_intra.md` | 73.4KB | 10-02 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_pre.md` | 65.2KB | 10-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20261001-점검리포트.md` | 74.1KB | 10-01 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_post.md` | 89.7KB | 10-01 16:19 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261001.md` | 0B | 10-01 12:44 |
| `docs/정기점검/매일점검/_tmp_append_addendum_20261001.md` | 0B | 10-01 12:44 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_intra.md` | 74.9KB | 10-01 12:27 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261002.json` | 3.0KB | 10-02 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261002.md` | 5.0KB | 10-02 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261002.json` | 38.9KB | 10-02 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20261002.md` | 32.5KB | 10-02 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261002.json` | 123.1KB | 10-02 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261002.md` | 194.2KB | 10-02 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260923.json` | 3.0KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260923.md` | 4.9KB | 09-23 15:56 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건) — 차단 111건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
2. 메인 스레드 정지 5초 초과 **2건** (최대 12016ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20261002_SYSTEM.log`: **ConstOut** 8건(표본)
4. `logs/20261002_SIGNAL.log`: **WeightCollapse** 8건(표본)
5. `logs/20261002_SIGNAL.log`: **ConstOut** 8건(표본)
6. `logs/20261002_LEARNING.log`: **축퇴** 8건(표본)
7. `logs/retrain_eod_20261002.log`: **축퇴** 1건(표본)
8. `logs/retrain_eod_20261002.log`: **ConstOut** 1건(표본)
9. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
10. 미커밋 변경 42건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`
11. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261002*.log` (Windows) / `grep 강제청산 logs/*20261002*.log`*