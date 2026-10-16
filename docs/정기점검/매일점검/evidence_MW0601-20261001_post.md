# 미륵이 증거 다이제스트 — 2026-10-01 / POST

- 생성 2026-10-01 16:18:08 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01racwriaj7jcxau9wtpnr8j/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261001` · `2026-10-01` · `261001` · `1001`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **32개** 파일 · 32개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261001.log` | 271B | 10-01 07:48 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261001.txt` | 28B | 10-01 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261001.txt` | 28B | 10-01 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261001.txt` | 233B | 10-01 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261001.log` | 1.4KB | 10-01 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261001.log` | 217B | 10-01 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261001.json` | 244B | 10-01 15:46 |
| `launcher_{DATE}_084001_30537.log` | 1 | `logs/Mireuk_batch/launcher_20261001_084001_30537.log` | 2.4MB | 10-01 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261001.log` | 2.9KB | 10-01 15:11 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261001.log` | 1.4KB | 10-01 16:10 |
| `position_state.json.gen_{DATE}_130401` | 1 | `data/position_state.json.gen_20261001_130401` | 1.3KB | 10-01 11:26 |
| `position_state.json.gen_{DATE}_130402` | 1 | `data/position_state.json.gen_20261001_130402` | 1.5KB | 10-01 13:04 |
| `position_state.json.gen_{DATE}_130524` | 1 | `data/position_state.json.gen_20261001_130524` | 1.5KB | 10-01 13:05 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261001.log` | 21.4KB | 10-01 15:53 |
| `retrain_intraday_20260701_13{DATE}.log` | 1 | `logs/retrain_intraday_20260701_131001.log` | 4.6KB | 07-01 13:10 |
| `retrain_intraday_20260703_13{DATE}.log` | 1 | `logs/retrain_intraday_20260703_131001.log` | 4.6KB | 07-03 13:10 |
| `retrain_intraday_20260731_13{DATE}.log` | 1 | `logs/retrain_intraday_20260731_131001.log` | 4.5KB | 07-31 13:10 |
| `retrain_intraday_20260819_10{DATE}.log` | 1 | `logs/retrain_intraday_20260819_101001.log` | 2.4KB | 08-19 10:10 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261001.txt` | 43B | 10-01 15:47 |
| `strategy_report_{DATE}_154019.txt` | 1 | `data/daily_reports/strategy_report_20261001_154019.txt` | 2.5KB | 10-01 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20261001_DATA.log` | 436.1KB | 10-01 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261001_DEBUG.log` | 235.3KB | 10-01 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261001_HEALTH.log` | 4.4KB | 10-01 15:09 |
| `{DATE}_HOGA.log` | 1 | `logs/20261001_HOGA.log` | 52.4MB | 10-01 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261001_LEARNING.log` | 294.0KB | 10-01 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261001_MICRO.log` | 980.1KB | 10-01 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20261001_PROBE.log` | 94.5KB | 10-01 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261001_REGULAR_COLLECT.log` | 6.6KB | 10-01 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261001_SIGNAL.log` | 566.1KB | 10-01 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261001_SYSTEM.log` | 1005.5KB | 10-01 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261001_TRADE.log` | 13.6KB | 10-01 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261001_WARN.log` | 719.6KB | 10-01 15:46 |

## 2. 코드·커밋 상태

- HEAD `67cff42` · 브랜치 `v9-dev` · 미커밋 20건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
 M docs/정기점검/수익률향상_누적대장.md
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261001.md
?? docs/신동거래/일일/신동_일일_MW0601_20261001.svg
?? docs/정기점검/매일점검/MW0601-20260930-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261001-점검리포트.md
?? docs/정기점검/매일점검/_tmp_append_addendum_20261001.md
?? docs/정기점검/매일점검/_tmp_append_intra_20261001.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_pre.md
```

**당일(2026-10-01) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
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
ba09d5a [MW0602] 적용가이드 §8~§10: MW0602 실행 결과 + 별건 확인요청
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

_본문 미열람(설정): `20261001_HOGA.log` 52.4MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261001.txt`** — 28B · 10-01 15:40:19
```
2026-10-01T15:40:19.739106
```

**`data/daily_close_started_20261001.txt`** — 28B · 10-01 15:40:08
```
2026-10-01T15:40:08.597738
```

**`data/daily_reports/strategy_report_20261001_154019.txt`** — 2.5KB · 10-01 15:40:19
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-01 15:40
========================================================
  버전    : v1.0  (90일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=0.03  MDD(자본대비)=13.9%
  당일      : WR=75.0%  PF=0.41
  롤링20일: 누적 +70113원  Sh=0.03  MDD(자본대비)=13.9%  MDD(peak대비)=1208.2%
  당일손익 : broker(gross) +30,000원  수수료 74,422원  net -44,422원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.001  vwap_position=0.012
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -35,071원  승률 30.0%  합계 -701,417원
  등급별 순EV(30일): A=+90,142원(69건,승55%)  BROKER=-1,612,145원(3건,승67%)  MANUAL=-25,929원(113건,승44%)
  호라이즌별 순EV(30일): 1m=-882원(11건)  3m=+8,341원(41건)  5m=-68,937원(15건)  ?=-7,160원(118건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 45분  5일평균 41분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 34.7pt(5일평균 26.7pt)  1분평균변동 0.63pt(5일평균 0.62pt)
--------------------------------------------------------
  진입 퍼널(2026-10-01, 총 370분):
    FLAT 206 → conf미달 114 → CoherenceGate 4 → 게이트차단 38 → 후보 8 → 진입 4
    └ 등급상향경로(앙상블X→체크리스트통과): 3건 [285차-P5]
    게이트별: 체크리스트항목미달=14  콜드스타트/기타(σ미수집)=8  ATR변동성=4  콜드스타트/기타(조건부구간)=3  쿨다운=3  모드필터=2  포지션보유중(평가생략)=2  콜드스타트/기타(DataAnomalyGate)=1  콜드스타트/기타(RegimeOverride)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 4건
      └ 상세: JointGateBlock=4
      └ JointGateBlock 4건 (무정보폴백 4건 = 100.0%) [표본 16건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261001.txt`** — 233B · 10-01 15:53:26
```
completed: 2026-10-01 15:53:26
rows: 18352
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 23.8
t_retrain_s: 178.9
t_total_s: 203.2
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20261001.txt`** — 43B · 10-01 15:47:14
```
auto_shutdown
2026-10-01T15:47:14.772951
```

_다이제스트 대상 8/22개 (중요도순). 제외: `retrain_intraday_20260703_131001.log`, `retrain_intraday_20260731_131001.log`, `retrain_intraday_20260819_101001.log`, `20261001_MICRO.log`, `20261001_DATA.log`, `20261001_PROBE.log`, `launcher_20261001_084001_30537.log`, `20261001_DEBUG.log`_

### `logs/20261001_TRADE.log` — 13.6KB · 102행 · 최종 15:40:10

- 형식 평문 · 시각 인식 102행 · INFO=102

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-01 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-01 10:02:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,483,818) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-01 10:02:00 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-01 10:49:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,483,818) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-10-01 13:06:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,395) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-01 13:34:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,395) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-01 14:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,395) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-01 14:27:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,395) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-01 15:40:10 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×102

**컴포넌트 상위 15** — `Chejan`×25, `Position`×18, `Sizer`×14, `주문요청`×11, `JointGateBlock 차단`×4, `진입체크`×4, `체결진입`×4, `TickTP1`×4, `TickStop-S0C`×4, `청산 완료`×4, `체결진입보정`×3, `ProfitGuard`×2, `TP1 부분청산`×2, `모드필터 차단`×2, `손절1차 조기축소`×1

### `logs/20261001_WARN.log` — 719.6KB · 3268행 · 최종 15:46:11

- 형식 평문 · 시각 인식 3261행 · ERROR=2, WARNING=3259, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-10-01 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-10-01 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-01 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-01 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-10-01 11:33:00 cols=['open'] existing_source=rt
2026-10-01 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-10-01 13:02:00 cols=['open'] existing_source=rt
2026-10-01 15:46:08 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=410 inserted=1 open_fixed=1 mismatch=10
2026-10-01 15:46:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2178 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=3250 band=INFO since_pipe_s=2230.0
2026-10-01 15:46:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 67.3ms | size=1955x1124 candles=411 grid=9.3 spans=0.1 candles=15.7 dir=1.5 regime=9.1 markers=28.6 axes=0.9 cross=0.0 | slow_cnt=2652 total_cnt=2750 overlay_cnt=32935
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `LiveDBG` | 2 | 15:11:09 | 15:11:37 | _tick_header 간격 26579ms — 메인 스레드 블로킹 발생 | pipe_elapsed=96 watchdog_alerted=[90] | [MainStall] stall_ms=26579 band=ALERT since_pipe_s=128.4 |

<details><summary>ERROR/LiveDBG 원문 2건</summary>

```
2026-10-01 15:11:09 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 26579ms — 메인 스레드 블로킹 발생 | pipe_elapsed=96 watchdog_alerted=[90] | [MainStall] stall_ms=26579 band=ALERT since_pipe_s=128.4
2026-10-01 15:11:37 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 15297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=109 watchdog_alerted=[90] | [MainStall] stall_ms=15297 band=ALERT since_pipe_s=156.1
```

</details>

**WARNING — 태그 39종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2652 | 08:59:41 | 15:46:11 | paintEvent slow 56.0ms | size=1955x1124 candles=15 grid=36.0 spans=0.4 candles=1.1 dir=0.0 regime=0.0 markers=0.4 axes=1.9 cross=0.0 | slow_cnt=1 total_cnt=1 overlay_cnt=0 |
| `LiveDBG` | 288 | 08:41:07 | 15:46:11 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 79 | 08:41:18 | 15:33:08 | 그리기 68.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 874x1001 |
| `SHAP` | 35 | 10:42:01 | 15:03:01 | 슬로우 감지 989ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `ChejanFlow` | 25 | 10:49:01 | 13:05:24 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='2581' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=10:49:01.155' | positi… |
| `ChejanMatch` | 25 | 10:49:01 | 13:05:24 | order_no='2581' | pending='ENTRY:SHORT qty=2 filled=0 order_no=2581 reason=진입 req_at=10:49:01.155' | pending_matched=True |
| `PendingOrder` | 22 | 10:49:01 | 13:05:24 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1077.64, 'reason': '진입', 'hint_source': '', 'atr': 1.4843, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `ScalerRefresh` | 15 | 09:11:00 | 14:40:00 | 5분 누적 수익률 +0.259% (임계 ±0.253%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 14 | 09:00:02 | 15:08:00 | level=WARNING degraded=OFF | latency=2063ms | quality=1.00 | cache_age=45s | exceptions_10m=0 |
| `SessionBackfill` | 12 | 08:41:38 | 15:46:08 | OHLCV 불일치 ts=2026-09-30 10:39:00 cols=['open'] existing_source=rt |
| `ExitCooldown` | 8 | 10:49:16 | 13:05:24 | 하드스톱(틱) 후 3분 재진입 금지 (until 10:52:16) |
| `EntryFillFlow` | 7 | 10:49:01 | 13:04:02 | actual_side='SHORT' | after='SHORT 2계약 @ 1077.60' | applied_side='SHORT' | before='SHORT 2계약 @ 1077.64' | fill_no='' | fill_price=1077.6 | fill_qty=1 | order_no='2581' | pending='ENTRY:SHORT qty=2 filled=1 order_no=2581 reason=진입 req_at=10… |

**채널** — `SYSTEM`×3247, `HEALTH`×14

**컴포넌트 상위 15** — `ChartDBG`×2652, `LiveDBG`×290, `OptionFlowChart`×79, `SHAP`×35, `ChejanFlow`×25, `ChejanMatch`×25, `PendingOrder`×22, `ScalerRefresh`×15, `Health`×14, `SessionBackfill`×12, `ExitCooldown`×8, `EntryFillFlow`×7, `-`×7, `PipePerf`×6, `CB⑤`×6

### `logs/20261001_SYSTEM.log` — 1005.5KB · 6740행 · 최종 15:47:14

- 형식 평문 · 시각 인식 6719행 · INFO=6719, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=4436 | 행감지=30s all_threads=True
2026-10-01 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.47s | predictions=0.05s trades=0.23s daily_stats=0.01s shap=0.02s raw_data=0.12s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-01 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-01 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-01 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-01 15:46:08 [INFO] SYSTEM: [SessionBackfill] 2026-10-01~2026-10-01 chart=411 existing=410 inserted=1 open_fixed=1 mismatch=10
2026-10-01 15:46:08 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-01) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-01 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-01 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-01 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6719

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1163, `PumpGuard`×768, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `System`×100, `MicroRegime`×82, `OptionChain`×81, `OptionBook`×78, `RegimeFingerprint`×67, `CybosEvent`×50

### `logs/20261001_SIGNAL.log` — 566.1KB · 5013행 · 최종 15:40:10

- 형식 평문 · 시각 인식 5013행 · WARNING=1908, INFO=3105

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-10-01 15:10:01 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-01 15:40:10 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-01 15:40:10 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 85분(23.0%) / DN 16분(4.3%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-01 15:40:10 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-01 age=29m extreme=534 refresh=31 grade_x=126 cb3=0
2026-10-01 15:40:10 [INFO] SIGNAL: [ModelHealth] date=2026-10-01 앙상블유효가동률=69.2% | 파이프라인 370분 | ConstOut 15회/27분 {"3m": {"events": 13, "minutes": 23}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 87분 | 장중재학습 0회 | CB③ ready 258분/370분 (70%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1302 | 09:00:02 | 15:06:02 | 1m 'macro_vix' scale=0.0094 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 180 | 09:00:00 | 15:05:01 | ts=08:59 horizon=1m age=1m max_z=-11.19(institution_futures_net) extreme=4 adj=4 |
| `Model` | 168 | 09:00:00 | 15:05:01 | 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 139 | 09:11:00 | 15:06:01 | CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+0.027 need <0 (SHORT) bull_exh=0.00 |
| `WeightCollapse` | 87 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 17 | 09:33:00 | 15:06:01 | 3m 상수 출력 5분 감지 (range=0.0040 dir=+1) → 앙상블 제외 |
| `ScalerRefresh` | 12 | 08:45:08 | 08:45:08 | 1m CORE 'cvd_divergence' raw_std≈0(0.0354) → identity(0,1) 강제 (FLAT 100% 방지) |
| `PCR-Dampen` | 3 | 10:02:00 | 11:29:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×5013

**컴포넌트 상위 15** — `ScalerFloor`×1320, `SIGNAL`×740, `Ensemble`×370, `FQAdj`×369, `MetaGate`×366, `ZeroDiag`×340, `Checklist`×193, `ScalerMonitor`×181, `Model`×174, `ATR-Horizon`×142, `차단`×97, `ToxicityGate`×93, `WeightCollapse`×87, `MicroRegime`×82, `InstabilityGate`×75

### `logs/20261001_LEARNING.log` — 294.0KB · 2859행 · 최종 15:40:10

- 형식 평문 · 시각 인식 2859행 · WARNING=164, INFO=2695

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00023 auc=0.498 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과
2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00133 auc=0.314 out_max=0.1882 (기준 auc<0.53 and span<0.020, 기저율=0.1875 n=80) → 보정 미적용, raw 통과
2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00023 auc=0.451 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-10-01 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00291 auc=0.531 out_max=0.2765 (n=160) → 보정 재적용
  …
2026-10-01 15:40:10 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-01 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-01 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-01 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-01 15:40:10 [INFO] LEARNING: [Sigma] EOD sigma_20=0.06097% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 60 | 08:40:50 | 10:14:00 | 축퇴 감지 — span=0.00023 auc=0.498 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 47 | 08:40:50 | 12:49:00 | 축퇴 감지 — span=0.00133 auc=0.314 out_max=0.1882 (기준 auc<0.53 and span<0.020, 기저율=0.1875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 20 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00023 auc=0.451 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 12 | 08:40:50 | 08:40:57 | 축퇴 감지 — span=0.00066 auc=0.479 out_max=0.2628 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 11 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00029 auc=0.518 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 9 | 08:40:50 | 12:59:01 | 축퇴 감지 — span=0.00191 auc=0.467 out_max=0.3884 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 4 | 08:40:59 | 13:38:00 | 복원한 보정기가 축퇴 상태 — span=0.00282 auc=0.515 out_max=0.2963 (n=2072) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `DriftAdjuster` | 1 | 15:40:10 | 15:40:10 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 17일) |

**채널** — `LEARNING`×2859

**컴포넌트 상위 15** — `LEARNING`×1215, `SGD`×369, `sigma`×357, `Bias⚠`×228, `Bias`×138, `Calibration:1m`×118, `Calibration:30m`×93, `MetaConf`×76, `OnlineLearner`×69, `Calibration:3m`×38, `ScalerWarmup`×36, `BiasReset`×32, `Calibration:10m`×22, `Calibration:5m`×21, `Calibration:15m`×16

### `logs/20261001_HEALTH.log` — 4.4KB · 28행 · 최종 15:09:01

- 형식 평문 · 시각 인식 28행 · WARNING=14, INFO=14

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2063ms | quality=1.00 | cache_age=45s | exceptions_10m=0
2026-10-01 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=555ms | quality=1.00 | cache_age=103s | exceptions_10m=0
2026-10-01 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=347ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-10-01 09:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=275ms | quality=1.00 | cache_age=57s | exceptions_10m=0
2026-10-01 09:29:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 346ms (표본 20분)
  …
2026-10-01 13:46:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=352ms | quality=1.00 | cache_age=56s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-01 14:25:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=373ms | quality=1.00 | cache_age=183s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-01 14:26:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=397ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-01 15:08:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=454ms | quality=1.00 | cache_age=183s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-01 15:09:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=427ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 14 | 09:00:02 | 15:08:00 | level=WARNING degraded=OFF | latency=2063ms | quality=1.00 | cache_age=45s | exceptions_10m=0 |

**채널** — `HEALTH`×28

**컴포넌트 상위 15** — `Health`×27, `HealthTrend`×1

### `logs/retrain_eod_20261001.log` — 21.4KB · 147행 · 최종 15:53:27

- 형식 평문 · 시각 인식 147행 · WARNING=10, INFO=137

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-01 15:50:03,095 [INFO] EOD_RETRAIN: =======================================================
2026-10-01 15:50:03,095 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-01 15:50:03,095 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-01 15:50:03,095 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-01 15:50:03,096 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-01 15:53:27,382 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0363 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-01 15:53:27,384 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1000 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-01 15:53:27,388 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.07s
2026-10-01 15:53:27,395 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.07s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-01 15:53:27,396 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:38 | 15:52:37 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1500봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-30 14:38:00 ≥ 홀드아웃 시작=2026-09-22 12:27:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-30 14:38 >= holdout_start=2026-09-22 12:27 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-30 … |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-01 | 최신 2026-09-30 · 기준 7거래일. 복구: python scripts/collect_regular_futures.py --from 20261001 --to 20261001 |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 22765/44838 제외 (418차 결정 1) — 남은 22073행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/22073행 제외 (559차 P1'-2) — 남은 20627행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:26 | 15:53:26 | 백필 0행 제외 — 필터가 무효일 수 있다. 18352행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×62, `SIGNAL`×49, `EOD_RETRAIN`×26, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2, `P8`×2

### `logs/retrain_intraday_20260701_131001.log` — 4.6KB · 39행 · 최종 13:10:32

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 13:10:01,542 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b5fe16cc.json
2026-07-01 13:10:02,960 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-01 13:10:32,209 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.41s | old_acc=nan)
2026-07-01 13:10:32,213 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-01 13:10:32,214 [INFO] LEARNING: [Retrain] 완료 | 29.3초 | 성공=6/6 호라이즌
2026-07-01 13:10:32,215 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 30.7s 데이터=20000행
2026-07-01 13:10:32,217 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b5fe16cc.json
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
오늘 PnL: -44422원
════════════════════════════════════════════════════
2026-10-01 15:45:00 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 203.0ms | size=1955x1124 candles=410 grid=17.5 spans=0.2 candles=18.7 dir=2.1 regime=24.8 markers=135.8 axes=2.0 cross=0.0 | slow_cnt=…
2026-10-01 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-10-01 10:02:00 cols=['open'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 4 |
| 진입 등록(`[Position] 진입`) — **엔진** | 4 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 4 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 4 |
| 차단(`[차단]`) | 97 |
| 사이저 호출(`[Sizer]`) | 14 |

### 포지션 4건 · 승 1 (25%) · 합계 +0.60pt (-44,423원)  ※ 레그 7행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:49:01 | 엔진 | SHORT | 2 | 1m | 2 | +0.24 | -9,144 | 하드스톱(틱) |
| 11:12:03 | 엔진 | LONG | 2 | 5m | 2 | -0.50 | -46,210 | 하드스톱(틱) |
| 11:25:01 | 엔진 | LONG | 2 | 3m | 2 | +0.42 | -294 | 하드스톱(틱) |
| 13:04:01 | 엔진 | LONG | 1 | 3m | 1 | +0.44 | +11,225 | 하드스톱(틱) |

**청산 레그 7행** (부분청산 3 · 전량청산 4)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:49:03 | 부분 | 1 | +0.30 | +4,428 | TP1 부분청산 33% |
| 10:49:16 | 전량 | 1 | -0.06 | -13,572 | 하드스톱(틱) |
| 11:12:52 | 부분 | 1 | -0.74 | -47,605 | 손절1차 조기축소 |
| 11:18:21 | 전량 | 1 | +0.24 | +1,395 | 하드스톱(틱) |
| 11:25:29 | 부분 | 1 | +0.50 | +14,353 | TP1 부분청산 33% |
| 11:26:37 | 전량 | 1 | -0.08 | -14,647 | 하드스톱(틱) |
| 13:05:24 | 전량 | 1 | +0.44 | +11,225 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×4, `TP1 부분청산 33%`×2, `손절1차 조기축소`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 4/4건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -44,423 = 포지션합 -44,423 → OK · `[청산 완료]` 4건 = 조립 포지션 4건 → OK

### CB③ 판정 가능 시간 — **258분 / 370분 (70%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 4건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:49:01 | SHORT | 2 | 1077.64 | 1m | mean-revert |
| 11:12:03 | LONG | 2 | 1081.14 | 5m | mean-revert |
| 11:25:01 | LONG | 2 | 1085.4 | 3m | mean-revert |
| 13:04:01 | LONG | 1 | 1098.36 | 3m | neutral |

계약수 분포 — 1계약×1, 2계약×3

등급 분포 — `A급(원시C)`×2, `A급(원시X)`×2

**진입한 건들의 체크리스트 미통과 항목** — `chas`×3, `ofi`×2, `fore`×2, `prev`×2, `cvd`×2

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×5, **2계약**×1, **3계약**×8

실제 진입 계약수 — **1계약**×1, **2계약**×3

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×14

### 차단 사유 97건 · 35종

| 건수 | 사유 |
|---|---|
| 26 | 등급X — 미통과 항목: 2_confidence |
| 6 | ATR 0.89pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 5 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.92pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 4 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 3 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 3 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 2 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×26, `3_vwap`×12, `6_foreign`×12, `5_ofi`×8, `7_prev_bar`×6, `4_cvd`×5, `11_countertrend`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 17건 · 최대 26579ms · 5초 초과 2건

상위 — 26579ms, 15297ms, 4969ms, 4922ms, 4016ms, 3968ms, 3954ms, 3829ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 15:11:09 | 26579ms | **미측정** | — |
| 15:11:37 | 15297ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261001_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:18 2026-10-01 15:40:18 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 41분/일 < 하한 60분 — 금일 45분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 370분
--- [Brier] 과신 ×1(표본)
14:56:00 2026-10-01 14:56:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.350 > 0.35
--- [CB] ×3(표본)
10:49:16 2026-10-01 10:49:16 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:12:52 2026-10-01 11:12:52 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:26:37 2026-10-01 11:26:37 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
10:49:16 2026-10-01 10:49:16 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:52:16)
10:49:16 2026-10-01 10:49:16 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:52:16)
11:18:21 2026-10-01 11:18:21 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:20:21)
11:18:21 2026-10-01 11:18:21 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:20:21)
--- [ExitStageRecon] ×1(표본)
15:40:10 2026-10-01 15:40:10 [WARNING] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 4레그 / 4포지션 중 TP 이벤트 대응 2 · 단일계약 보호전환(설계) 1 · 미대응 1 ⚠ 미대응 합계 -46,210원 (진입 11:12:04). 이 레그들은 라벨상 「TP1 뒤 트레일(이익 청산)」이지만 그 포지션에 TP가 난 적이 없다 — 손절률 분모·…
--- [SHAP] 슬로우 ×8(표본)
10:42:01 2026-10-01 10:42:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 989ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
10:50:01 2026-10-01 10:50:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 933ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:01:01 2026-10-01 11:01:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 953ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:15:02 2026-10-01 11:15:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1109ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:11 2026-10-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4016 band=INFO since_pipe_s=NA
08:59:45 2026-10-01 08:59:45 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3532ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3532 band=INFO since_pipe_s=NA
09:00:04 2026-10-01 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4922 band=INFO since_pipe_s=0.1
09:05:01 2026-10-01 09:05:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2094ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2094 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20261001_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:33:00 2026-10-01 09:33:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4386) | 앙상블 제외는 유지
09:41:00 2026-10-01 09:41:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3836) | 앙상블 제외는 유지
09:59:00 2026-10-01 09:59:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5008) | 앙상블 제외는 유지
10:21:00 2026-10-01 10:21:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4375) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:10 2026-10-01 15:40:10 [INFO] SYSTEM: [CB③계측] 조건성립 119분 / 판정가능 258분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-01 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:06:00 2026-10-01 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:12:00 2026-10-01 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-10-01 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:10 2026-10-01 15:40:10 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:10 2026-10-01 15:40:10 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:10 2026-10-01 15:11:10 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=1회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:19 2026-10-01 15:40:19 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-10-01 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:19 2026-10-01 15:40:19 [INFO] SYSTEM: [Notify] ℹ️ [15:40:19] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:19 2026-10-01 15:40:19 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 400초
15:40:19 2026-10-01 15:40:19 [INFO] SYSTEM: 자동 종료 예약 — 415초 후 Qt 이벤트 루프 종료
```

### `logs/20261001_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:33:00 2026-10-01 09:33:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0040 dir=+1) raw(range=0.0860 dir=+1)
09:33:00 2026-10-01 09:33:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0040 dir=+1) → 앙상블 제외
09:33:00 2026-10-01 09:33:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:34:01 2026-10-01 09:34:01 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-10-01 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-10-01 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-10-01 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-01 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:42 2026-10-01 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
--- 안전망 ×8(표본)
09:07:00 2026-10-01 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-01 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-01 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-01 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261001_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00023 auc=0.498 out_max=0.2501 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00133 auc=0.314 out_max=0.1882 (기준 auc<0.53 and span<0.020, 기저율=0.1875 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-01 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00023 auc=0.451 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-01 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00291 auc=0.531 out_max=0.2765 (n=160) → 보정 재적용
```

### `logs/20261001_HEALTH.log`
```
--- [ExitCooldown] ×7(표본)
11:30:00 2026-10-01 11:30:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=605ms | quality=1.00 | cache_age=184s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
11:31:00 2026-10-01 11:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=451ms | quality=1.00 | cache_age=59s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
11:32:01 2026-10-01 11:32:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1150ms | quality=1.00 | cache_age=120s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
11:33:00 2026-10-01 11:33:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=612ms | quality=1.00 | cache_age=179s | exceptions_10m=3 | exc_tags=[SHAP]×2 [ExitCooldown]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261001_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 2 | 10:02:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,483,818) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 14:00 | 장중 후반 · 장중 재학습 | 1 | 14:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,439,395) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:10 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261001_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 29 | 08:57:33 [WARNING] 그리기 99.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 40 | 08:57:33 [WARNING] 그리기 99.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |
| 10:00 | 장중 초반 | 87 | 09:54:00 [WARNING] paintEvent slow 89.6ms | size=1955x1124 candles=70 grid=25.2 spans=0.1 candles=2.7 dir=0.2 regime=4.7 markers… |
| 12:00 | 장중 중간점 | 135 | 11:54:01 [WARNING] paintEvent slow 190.4ms | size=1955x1124 candles=190 grid=51.8 spans=20.6 candles=12.6 dir=1.2 regime=15.4 ma… |
| 14:00 | 장중 후반 · 장중 재학습 | 159 | 13:54:01 [WARNING] paintEvent slow 106.9ms | size=1955x1124 candles=310 grid=28.9 spans=0.2 candles=16.2 dir=1.7 regime=12.1 mar… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 78 | 15:04:01 [WARNING] paintEvent slow 108.2ms | size=1955x1124 candles=380 grid=30.1 spans=0.2 candles=14.3 dir=1.4 regime=10.6 mar… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 17 | 15:12:09 [WARNING] _fetch_investor_data 지연 614ms — 메인 스레드 614ms 점유 (live 중단 원인 후보) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 21 | 15:34:00 [WARNING] paintEvent slow 97.0ms | size=1955x1124 candles=410 grid=10.7 spans=0.1 candles=18.1 dir=2.1 regime=10.7 mark… |
| 15:47 | EOD 재학습(py310_64) 완료 | 9 | 15:45:00 [WARNING] paintEvent slow 203.0ms | size=1955x1124 candles=410 grid=17.5 spans=0.2 candles=18.7 dir=2.1 regime=24.8 mar… |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261001_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=4436 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 139 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 193 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 227 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 208 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 230 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 178 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 157 | 15:12:01 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 60 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:41:08 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:08 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261001_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0354) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 86 | 09:00:00 [WARNING] 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 183 | 09:00:00 [WARNING] 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 244 | 09:54:00 [WARNING] 신뢰도 미달 40.7% < 41.1% → 강제 X등급 |
| 12:00 | 장중 중간점 | 172 | 11:54:01 [WARNING] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 14:00 | 장중 후반 · 장중 재학습 | 123 | 13:54:00 [WARNING] ts=13:53 horizon=1m age=4m max_z=+5.62(ofi_imbalance) extreme=3 adj=2 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 111 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:10 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260930 | 15:47 | 로그 본문 |
| 20260929 | 15:47 | 로그 본문 |
| 20260928 | 15:47 | 로그 본문 |
| 20260926 | 16:50 | 로그 본문 |
| 20260924 | 10:58 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261001** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-29 (MW0601 641ì°¨ â ì¥í ìëì¡°ì¹: 637-2 crash_fault.log ë¤ì´í°ë¸ ì¤ë¥ ì§ê³ + 638-1 git ì¤í¨ ì§ë¨Â·ì´ì¤ ë°©ì´)
## 2026-09-30 (MW0601 642ì°¨ â ì¥ì  ì ê²)
## 2026-09-30 (MW0601 642ì°¨ íì â ì¥ì  ì ê² ëì¤ `.git/index.lock` ì¤ì¸¡ ë°ìÂ·íì)
## 2026-09-30 (MW0601 643ì°¨ â ì¥ì¤ ì ê²)
## 2026-09-30 (MW0601 644ì°¨ â ì¥í ì ê²)
## 2026-09-30 (MW0601 645ì°¨ â ì¥í ìëì¡°ì¹: F-4 ë½ ì£¼ì¸ ì§ë¨ Â· G-1 PreRetrain ì°í íì Â· G-2 git 1í ì¤ë
## 2026-10-01 (MW0601 646ì°¨ â ì¥ì  ì ê²)
## 2026-10-01 (MW0601 647ì°¨ â ì¥ì¤ ì ê²)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
ì§ê¸°ì `run_git()` íììì ì²ë¦¬ ë°©ì)ì ìì§ ì½ëë¡ íì¸ ì  â **ê°ì¤ ë¨ê³**.

**ê²°ì **: ì ê· Fix ì°©ì ìì(ì¥ì¤ ì½ë ë³ê²½ ê¸ì§ ê·ì½). `F-3`(ê°ì¤: ìì§ê¸° `git diff` íììì ê²½ë¡ ê°ì )ì ì ì¤í´ `NEXT_TODO.md`ì ë±ë¡íê³ , ê¸°ì¡´ `645-1`ì "ì¡°ê±´ ì¶©ì¡± â ìì¸ ê°ì¤ ì¬ê²í  íì"ë¡ ê°±ì . 1-1Â·1-2Â·1-3ì ë²í¸ ê³ì¹, ì ê· ë²í¸(1-4)ë O-i1ì 4ë²ì§¸ ì¬íìë§ ë¶ì¬(í¨ì â  íì¸ â ê¸°ì¡´ TODO ì¬ë°ì´ì§ ì ê· ê²°í¨ ìë).

**Why**: ì¤í¬ Â§0 git í¸ì¶ ê·ì½ì´ ë§ì¼ë ¤ë íìì´ `--no-optional-locks`ë¥¼ ì´ë¯¸ ì ì©í ìì§ê¸° ë´ë¶ììë ì¬íëë¤ë ì ìì, ë¨ì "ìµì ë¯¸ë¶ì°©" ë¬¸ì ê° ìëë¼ íìììÂ·ê°ì ì¢ë£ ê²½ë¡ ê³ ì ì ë¬¸ì ì¼ ê°ë¥ì±ì´ ìë¤(ê³ì¸¡ 4ìì¹ â¡ â ë¯¸ì¸¡ì  ìíë¥¼ "ìì¸ ìì"ì¼ë¡ ì½ì§ ìê¸° ìí´ ê°ì¤ë¡ë§ ê¸°ë¡). 313ì°¨ ìì¹ â 1í ì¶ê° ê´ì¸¡(ì´ë²ì´ 4ë²ì§¸)ë§ì¼ë¡ F-3ì ìì¸ ì¤ê³ê¹ì§ íì íì§ ìì, ìì¸ ì¡°ì¬ë ë³ë ì¸ì ëª«.

**How to apply**: í´ë¹ ìì(ì¥ì¤ ê·ì½ì ì½ë ë³ê²½Â·ì»¤ë° ê¸ì§). ì¥í ì ê²ì´ `.git/index.lock` ìì° ìë©¸ ì¬ë¶ë¥¼ ì¬íì¸íê³ , íì ì `git_lock_guard.py --check` ì¬íì (ìê³ 600ì´ ê²½ê³¼ í)ì¼ë¡ ì¤íì¼ ì¬ë¶ë¥¼ ê°ë¥¸ë¤.

**ê²ì¦**: `python scripts/collect_evidence.py --phase intra --pc MW0601 --out-auto` ì ì ì¤í(74.9KB ë¤ì´ì ì¤í¸ ìì±, Â§2ê° git diff ì¤í¨ë¥¼ ìë ê¸°ì¬í¨). ìëì¼ë¡ ì¢ì ë²ì `git --no-optional-locks diff --numstat`(4ê° íì¼ íì )ì 0.4ì´ ë§ì ì ì ìë£í´ ì¤ì§ ë³ê²½ 4ê±´(DECISION_LOG.md +105/-0, NEXT_TODO.md +39/-2, ë¯¸ë¥µì´ê³ ëí3 ë¬¸ì +2/-1, ììµë¥ í¥ì_ëì ëì¥ +3/-2)ì ì§ì  ì¬ì¸¡ì í¨. `python scripts/git_lock_guard.py --check`(12:29Â·12:35 KST 2í) ë° `python scripts/git_lock_diag.py --recheck 30`(12:32ê²½)ì¼ë¡ ORPHAN ê°ë 1 íì¸. ì¥ì¤ ì½ë ë³ê²½Â·ë¼ì´ë¸ DB ì¤ìº ìì(ê·ì½ ì¤ì).

**[12:43 KST íì]** ì 647ì°¨ ê¸°ë¡ ì§í `.git/index.lock`ì´ ëì´ ìê³(600ì´)ë¥¼ ëê²¨ STALE íì ì¼ë¡ ì íëê³ , `git_lock_guard.py --reclaim`ì¼ë¡ ì¦ì íì ìë£(ì´ë¦ë³ê²½ ì°í ì±ê³µ, `.git/index.lock.stale_20261001034310_6`ë¡ ì´ë â ì´ ë¶ì¤ë¬ê¸°ë§ Windows ìª½ ìë ì ë¦¬ íì, ì»¤ë°ì ë§ì§ ìì). ì¥ì¤ ì¤ ìë ¥ì¼ë¡ í´ìë¼ ì¥íë¡ ëê¸¸ íì ìì. ë¦¬í¬í¸ì ì ì  í¬ì¸í°(â©ï¸ 12:43 KST ê°±ì ) ì¶ê°í¨.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-29 (MW0601 641차 — 장후 자동조치)
## 2026-09-30 (MW0601 642차 — 장전 점검)
## 2026-09-30 (MW0601 642차 후속 — 장전 점검 도중 `.git/index.lock` 실측·회수)
## 2026-09-30 (MW0601 643차 — 장중 점검) 신규 항목
## 2026-09-30 (MW0601 644차 — 장후 점검)
## 2026-09-30 (MW0601 645차 — 장후 자동조치)
## 2026-10-01 (MW0601 646차 — 장전 점검)
## 2026-10-01 (MW0601 647차 — 장중 점검)
```

미완료 체크박스 **2921건** (끝에서 30건)
```
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — 문서 제목 손상, 0929 장후에도 미확인·미커밋 지속(4일째).
- [ ] **641-1 (G-2, 보류)** 부팅 구간 access violation 경고 **문턱** 신설 여부 — 관측일 3건(09-17·09-28·09-29)뿐이라 313차 가드 미통과. 지금 §11 은 문턱 없이 1건부터 건수만 올린다. 관측일이 더 쌓이면(예: 10거래일) 분포를 보고 문턱을 정할 것. 606-4(원인 조사 우선순위, 사용자 결…
- [ ] **642-1 (P2)** `dev_memory/_tmp_append_20260929.txt`·`_tmp_append_todo_20260929.txt` 정리 — 0바이트 미추적 스크래치 파일 2건 발견. 라이브 프로세스 미참조 재확인 후 삭제. 근거: 0930 장전 이상점 1-3.
- [ ] **642-2 (G-1, 고도화 제안)** `scripts/collect_evidence.py` §9에 `[PreRetrain]` "EOD 마커 파일 직접 확인" 우회 성공 여부를 자동 표시 — 현재는 로그 직접 grep 필요. 근거: 0930 장전 SessionStateDrop 재현 시 우회 확인에 수동 grep 소요.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — 문서 제목 "재" 글자 손상, 0930 장전에도 미확인·미커밋 지속(**5일째**, 변화 없음).
- [ ] **642-3 (사용자, Windows 환경)** `.git/index.lock.stale_20260930001115_6` 삭제 — 이 세션(device_bash 리눅스 VM)에서는 `Operation not permitted`로 불가. 2026-08-21 `index.lock.stale_20260929033733_6`와 함께 정리 권장.
- [ ] **642-4 (조건부 고도화)** `git --no-optional-locks diff`가 오늘 실제로 `.git/index.lock`을 남긴 사례 확인(09-30 09:00:35 KST) — 다음에 같은 현상이 또 재현되면(장전·장중·장후 무관) G-1급 고도화로 "세션 종료 직전 `git_lock_guard.py --check` 자동 실행…
- [ ] **F-4** `scripts/git_lock_guard.py`·`scripts/collect_evidence.py:run_git()`에 진단 로깅 추가 — `.git/index.lock`이 `--no-optional-locks` 부착 상태에서도 생성될 때, 직전 실행된 git 하위명령을 특정할 수 있도록(`GIT_TRACE` 등). 근거: 2…
- [ ] **G-2** 점검 세션의 git 상태 확인을 `git status --porcelain=v2 --branch` 한 번으로 통합하는 헬퍼 제안 — `branch`·`status`·`log`를 연달아 실행하는 시점에 두 번 다 락이 발생한 공통점에서 착안. F-4로 원인 특정 후 설계.
- [ ] **O-i1** 다음 거래일(2026-10-01) 점검에서도 `.git/index.lock` 현상이 재현되는지 관찰 — 재현되면 "구조적 현상"으로 격상, 아니면 완화 검토.
- [ ] `.git/index.lock.stale_20260930033834_6` 삭제(Windows 환경에서만 가능, 코웍 세션은 EPERM으로 불가) — 장중 643차 회수 부스러기.
- [ ] **644-1 (F-4, P1로 상향)** `.git/index.lock`이 오늘 하루 세 번(장전·장중·장후) 재현됨. 장후는 STALE 없이 4분 만에 자연 소멸 — 앞의 두 번(둘 다 STALE→`--reclaim`)과 성격이 다름. `scripts/git_lock_guard.py`에 락 생성 전후 프로세스 스냅샷 진단 로깅 추가 검토. …
- [ ] **644-2 (G-3, 고도화 제안)** 점검 세션이 보고서를 다 쓰기 직전 `git_lock_guard.py --check`를 자동으로 한 번 더 실행해 결과를 보고서에 자동 기재하는 방안 — 642-4가 조건부 등록한 것을 오늘 재발 3회로 정식 승격. 근거: 0930 장후 제3부.
- [ ] **644-3 (F-5, P2)** `.claude/skills/mireuk-daily-check/references/evidence_map.md` §8의 DB 스키마 서술이 `v9-dev` 최신 실측과 어긋남 — `trades`에 `tp1_reached`·`exit_trigger`·`exit_outcome` 컬럼이 이미 있음(문서엔 없음), …
- [ ] **O-t1(10-01 판정)** P5-17(오후장 5m SHORT `TIER1_EARLY`→`INITIAL_STOP` 연쇄손절)이 09-29·09-30 이틀 연속 재현(5건/2거래일, 누계 -733,310원). 3일째도 재현되면 채널 신설(`horizon_5m_early_stop_watch`) 여부를 사용자에게 공식 상정. 근거: 0930 장…
- [ ] **645-1 (O-i1 보강)** 다음 `.git/index.lock` 재현 시 `python scripts/git_lock_diag.py --recheck 30` 결과(갈래 1/2)를 리포트에 기록 — 3건 이상 쌓이면 원인 가설 재검토.
- [ ] **645-2 (사용자/별도 세션, fuoption 저장소)** `fuoption/scripts/git_lock_guard.py` 사본을 정본(futures, 636차 `_sideline` 반영본)과 재통일 — `test_483::test_sibling_copy_matches_canonical` 이 636차 이후 계속 실패 중. 다른 저장소라 …
- [ ] **645-3 (사용자 확인, 스킬 개정)** SKILL.md §0-③·§7 에 ① 「상태 확인은 `scripts/git_snapshot.py` 한 번으로」 ② 「보고서 마무리 직전 `git_lock_diag.py --recheck 30` 실행 결과를 자동 기재」(G-3) 추가 여부 — 저장소 정본 + 앱 저장본 동시 수정 필요라 자동조치에서 …
- [ ] **644-3 / F-5 유지(C — 사용자 승인 대기)** evidence_map.md §8 스키마 갱신 — 리포트가 「사용자 승인 후 별도 세션」 지정.
- [ ] **637-1/606-4/641-1 (지속, 4관측일째)** 부팅 구간 access violation 3건 재현(09-17·09-28·09-29·10-01). 정규장 이후 0건 유지. 근본원인 조사 우선순위는 여전히 사용자 결정 대기. 경보 문턱은 313차 원칙상 10거래일 표본 필요(현재 4일, 6일 부족).
- [ ] **606-2/O-t2계열 (지속)** 10-01 거래일 전환 시 SessionStateDrop 재현(p8_last_success_date·eod_retrain_ok_date 키 소실) — PreRetrain 우회(EOD 마커 파일 직접 확인)로 실질 피해 없음. F-1(마커 승계 로직) 미적용 상태 그대로.
- [ ] **633-1 (P2, 지속 — 오늘로 6일째)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상("재" 글자), 미확인·미커밋 지속.
- [ ] **646-1 (사용자, 커밋 대기)** 9/30분 미커밋 실질 변경 3건 — `dev_memory/DECISION_LOG.md`·`dev_memory/NEXT_TODO.md`·`docs/정기점검/수익률향상_누적대장.md`. 경로 명시해 `git add` 후 커밋 권고(`git add .` 금지 — CRLF/LF 왜곡 주의, 단 오늘 실측은 E…
- [ ] **O-i1(계승, 10-01 장중·장후가 판정)** `.git/index.lock` 재현 여부 — 장전 기준 미재현(branch·status·diff·log 전수 실행 후 확인). 장중·장후에서 계속 관찰.
- [ ] **637-1/606-4/641-1 (지속, 변화 없음)** 부팅 구간 access violation — 장중 추가 재발 0건(정규장 이후 그대로 0건 유지). 사용자 결정 대기 그대로.
- [ ] **606-2/O-t2계열 (지속, 변화 없음)** SessionStateDrop — 장중에는 해당 이벤트 자체가 재발할 여지가 없음(거래일 전환 1회성 이벤트). 근본원인 F-1 미적용 그대로.
- [ ] **633-1 (P2, 지속 — 오늘로 6일째, 변화 없음)** 문서 제목 손상, 미확인·미커밋 지속.
- [ ] **646-1 (지속, 변화 없음)** 9/30분 미커밋 변경 4건 — 12:34 KST 기준 동일하게 미커밋 확인.
- [ ] **645-1 갱신 — 조건 충족** O-i1이 9/30 세 번 + 10/1 장중 1번으로 **4번째 재현**, `645-1`이 걸어둔 "3건 이상 쌓이면 원인 가설 재검토" 조건을 충족했다. 다음 세션(장후 또는 별도)이 `F-3`(아래) 착수 여부를 판단할 것.
- [ ] **F-3 (P1, 신규 — 가설 단계)** 증거수집기(`scripts/collect_evidence.py`)가 내부적으로 호출하는 `git diff --numstat`가 25초 타임아웃으로 강제종료될 때 `.git/index.lock`을 남기는 것으로 추정(10/1 장중 실측: 타임아웃 직후 락 생성, 수동으로 좁은 범위 diff는 0.4초에…
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
공(PreRetrain 우회 확인) · py37_32 런타임 정상 · Cybos 접속 정상 · 08:55 매크로/레짐 판정·실시간 구독 사전 시작 정상 · 한시예외(CB②) 재검토 기한 문제 없음(2026-09-02 519차 기 해결). 상세는 `docs/정기점검/매일점검/MW0601-20261001-점검리포트.md` 참조.
- [ ] **637-1/606-4/641-1 (지속, 4관측일째)** 부팅 구간 access violation 3건 재현(09-17·09-28·09-29·10-01). 정규장 이후 0건 유지. 근본원인 조사 우선순위는 여전히 사용자 결정 대기. 경보 문턱은 313차 원칙상 10거래일 표본 필요(현재 4일, 6일 부족).
- [ ] **606-2/O-t2계열 (지속)** 10-01 거래일 전환 시 SessionStateDrop 재현(p8_last_success_date·eod_retrain_ok_date 키 소실) — PreRetrain 우회(EOD 마커 파일 직접 확인)로 실질 피해 없음. F-1(마커 승계 로직) 미적용 상태 그대로.
- [ ] **633-1 (P2, 지속 — 오늘로 6일째)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상("재" 글자), 미확인·미커밋 지속.
- [ ] **646-1 (사용자, 커밋 대기)** 9/30분 미커밋 실질 변경 3건 — `dev_memory/DECISION_LOG.md`·`dev_memory/NEXT_TODO.md`·`docs/정기점검/수익률향상_누적대장.md`. 경로 명시해 `git add` 후 커밋 권고(`git add .` 금지 — CRLF/LF 왜곡 주의, 단 오늘 실측은 EOL 파생 0건).
- [ ] **O-i1(계승, 10-01 장중·장후가 판정)** `.git/index.lock` 재현 여부 — 장전 기준 미재현(branch·status·diff·log 전수 실행 후 확인). 장중·장후에서 계속 관찰.

## 2026-10-01 (MW0601 647차 — 장중 점검)

- [x] **647-0(오늘 장중 판정 완료)** P0 없음. 매분 루프 정상(09:00~12:27 10분 이상 공백 0건) · 진입 3건 전부 vwap 통과 후 하드스톱 청산(절대원칙 3 위반 없음) · CB②~⑤ 실제 HALT 없음. 상세는 `docs/정기점검/매일점검/MW0601-20261001-점검리포트.md` 장중 절 참조.
- [ ] **637-1/606-4/641-1 (지속, 변화 없음)** 부팅 구간 access violation — 장중 추가 재발 0건(정규장 이후 그대로 0건 유지). 사용자 결정 대기 그대로.
- [ ] **606-2/O-t2계열 (지속, 변화 없음)** SessionStateDrop — 장중에는 해당 이벤트 자체가 재발할 여지가 없음(거래일 전환 1회성 이벤트). 근본원인 F-1 미적용 그대로.
- [ ] **633-1 (P2, 지속 — 오늘로 6일째, 변화 없음)** 문서 제목 손상, 미확인·미커밋 지속.
- [ ] **646-1 (지속, 변화 없음)** 9/30분 미커밋 변경 4건 — 12:34 KST 기준 동일하게 미커밋 확인.
- [x] **O-i1 판정 완료(4번째 재현)** `.git/index.lock`이 12:27:11 KST(UTC 03:27:11) 재발. `git_lock_guard.py --check` 2회(나이 127초·349초) 모두 HOLD 판정보류. `git_lock_diag.py --recheck 30` → 갈래 1 ORPHAN(쥔 프로세스 없음, 재관측에도 존재). 완전판정(스테일 확정)은 임계 600초 미달로 장후로 이월.
- [ ] **645-1 갱신 — 조건 충족** O-i1이 9/30 세 번 + 10/1 장중 1번으로 **4번째 재현**, `645-1`이 걸어둔 "3건 이상 쌓이면 원인 가설 재검토" 조건을 충족했다. 다음 세션(장후 또는 별도)이 `F-3`(아래) 착수 여부를 판단할 것.
- [ ] **F-3 (P1, 신규 — 가설 단계)** 증거수집기(`scripts/collect_evidence.py`)가 내부적으로 호출하는 `git diff --numstat`가 25초 타임아웃으로 강제종료될 때 `.git/index.lock`을 남기는 것으로 추정(10/1 장중 실측: 타임아웃 직후 락 생성, 수동으로 좁은 범위 diff는 0.4초에 정상 완료해 "잠금이 모든 git 명령을 막는 것은 아님"도 확인). `638-1`(`GIT_OPTIONAL_LOCKS=0` 이중 전달)이 이미 배포돼 있음에도 재현된 것으로 보아, 타임아웃·강제종료 경로 고유의 문제일 가능성. **코드로 확인 전 — 가설 단계.** 변경 파일(후보): `scripts/collect_evidence.py`의 `run_git()`(또는 그 안에서 `git diff`를 호출하는 지점) — 타임아웃 시 자식 프로세스 정리 방식 개선, 또는 `git diff --numstat` 호출 범위를 좁혀 타임아웃 자체를 줄이는 방향. 적용은 장후 이후 별도 세션.

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

### `data/heartbeat_MW0601_20261001.json` — 244B · 10-01 15:46:54
```json
{
 "pid": 4436,
 "written_at": "2026-10-01T15:46:54",
 "beat_epoch": 1790837213.5953174,
 "beat_age_sec": 1.0,
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

- 파일 최종 기록: **10-01 15:53:27**

| 키 | 값 | 수집 대상일(2026-10-01)과 일치 |
|---|---|---|
| `date` | 2026-10-01 | 예 |
| `p8_last_success_date` | 2026-10-01 | 예 |
| `eod_retrain_ok_date` | 2026-10-01 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-01 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-09-30) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-01 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-09-30) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261001_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 4436: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 4436 | 08:40:45 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 186개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/_tmp_append_intra_20261001.md` | 0B | 10-01 12:44 |
| `docs/정기점검/매일점검/_tmp_append_addendum_20261001.md` | 0B | 10-01 12:44 |
| `docs/정기점검/매일점검/MW0601-20261001-점검리포트.md` | 31.9KB | 10-01 12:44 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_intra.md` | 74.9KB | 10-01 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_pre.md` | 57.5KB | 10-01 09:00 |
| `docs/정기점검/매일점검/MW0601-20260930-점검리포트.md` | 96.5KB | 09-30 17:45 |
| `docs/정기점검/매일점검/evidence_MW0601-20260930_post.md` | 87.8KB | 09-30 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md` | 77.7KB | 09-30 12:28 |

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

1. `logs/20261001_WARN.log`: ERROR 이상 2건
2. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
3. 포지션 4건 중 최종청산이 하드스톱·손절 계열 **4건(100%)** — 손절 준수율 확인 필요 (레그 7행)
4. 다레그 포지션 **3건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. 메인 스레드 정지 5초 초과 **2건** (최대 26579ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20261001_WARN.log`: **[Brier] 과신** 1건(표본)
8. `logs/20261001_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20261001_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20261001_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20261001_LEARNING.log`: **축퇴** 8건(표본)
12. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
13. 미커밋 변경 20건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`
14. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261001*.log` (Windows) / `grep 강제청산 logs/*20261001*.log`*