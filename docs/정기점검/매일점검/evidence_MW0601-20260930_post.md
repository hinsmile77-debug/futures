# 미륵이 증거 다이제스트 — 2026-09-30 / POST

- 생성 2026-09-30 16:17:42 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01temwngwwnknrmpywziab6o/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260930` · `2026-09-30` · `260930` · `0930`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20260930.log` | 137B | 09-30 07:22 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260930.txt` | 28B | 09-30 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260930.txt` | 28B | 09-30 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260930.txt` | 233B | 09-30 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260930.log` | 1.4KB | 09-30 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260930.log` | 216B | 09-30 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260930.json` | 245B | 09-30 15:46 |
| `launcher_{DATE}_084000_10534.log` | 1 | `logs/Mireuk_batch/launcher_20260930_084000_10534.log` | 2.4MB | 09-30 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260930.log` | 7.8KB | 09-30 09:02 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20260930.log` | 1.4KB | 09-30 16:10 |
| `position_state.json.gen_{DATE}_111701` | 1 | `data/position_state.json.gen_20260930_111701` | 1.5KB | 09-30 11:17 |
| `position_state.json.gen_{DATE}_111714` | 1 | `data/position_state.json.gen_20260930_111714` | 1.5KB | 09-30 11:17 |
| `position_state.json.gen_{DATE}_111954` | 1 | `data/position_state.json.gen_20260930_111954` | 1.6KB | 09-30 11:17 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260930.log` | 21.4KB | 09-30 15:53 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260930.txt` | 43B | 09-30 15:47 |
| `strategy_report_{DATE}_154018.txt` | 1 | `data/daily_reports/strategy_report_20260930_154018.txt` | 2.4KB | 09-30 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260930_DATA.log` | 436.7KB | 09-30 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260930_DEBUG.log` | 240.0KB | 09-30 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260930_HEALTH.log` | 4.9KB | 09-30 14:31 |
| `{DATE}_HOGA.log` | 1 | `logs/20260930_HOGA.log` | 52.0MB | 09-30 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260930_LEARNING.log` | 287.1KB | 09-30 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260930_MICRO.log` | 974.0KB | 09-30 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260930_PROBE.log` | 94.6KB | 09-30 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260930_REGULAR_COLLECT.log` | 6.6KB | 09-30 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260930_SIGNAL.log` | 600.9KB | 09-30 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260930_SYSTEM.log` | 979.4KB | 09-30 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20260930_TRADE.log` | 10.0KB | 09-30 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260930_WARN.log` | 766.5KB | 09-30 15:46 |

## 2. 코드·커밋 상태

- HEAD `89836e3` · 브랜치 `v9-dev` · 미커밋 10건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
?? dev_memory/_tmp_append_20260929.txt
?? dev_memory/_tmp_append_todo_20260929.txt
?? docs/신동거래/일일/신동_일일_MW0601_20260930.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.svg
?? docs/정기점검/매일점검/MW0601-20260930-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_pre.md
```

**당일(2026-09-30) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
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
1c4afed [MW0601] 636차 후속: 장후 자동조치 — 고도화 방안 2·3·4 (DB pruning 롤백 사실 기록 · 락 이름변경 우회 · md 제목 손상 경고)
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

_본문 미열람(설정): `20260930_HOGA.log` 52.0MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260930.txt`** — 28B · 09-30 15:40:18
```
2026-09-30T15:40:18.638845
```

**`data/daily_close_started_20260930.txt`** — 28B · 09-30 15:40:08
```
2026-09-30T15:40:08.441417
```

**`data/daily_reports/strategy_report_20260930_154018.txt`** — 2.4KB · 09-30 15:40:18
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-30 15:40
========================================================
  버전    : v1.0  (89일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-0.56  MDD(자본대비)=17.1%
  당일      : WR=0.0%  PF=0.00
  롤링20일: 누적 -1502198원  Sh=-0.56  MDD(자본대비)=17.1%  MDD(peak대비)=0.0%
  당일손익 : broker(gross) -310,000원  수수료 42,832원  net -352,832원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.001  vwap_position=0.042
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -16,484원  승률 40.0%  합계 -329,684원
  등급별 순EV(30일): A=+101,036원(62건,승55%)  BROKER=-2,574,591원(4건,승50%)  MANUAL=-27,752원(139건,승46%)
  호라이즌별 순EV(30일): 1m=-62원(9건)  3m=+8,712원(38건)  5m=-75,988원(13건)  ?=-49,892원(145건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 37분  5일평균 37분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 25.6pt(5일평균 25.6pt)  1분평균변동 0.65pt(5일평균 0.59pt)
--------------------------------------------------------
  진입 퍼널(2026-09-30, 총 370분):
    FLAT 171 → conf미달 137 → CoherenceGate 28 → 게이트차단 23 → 후보 11 → 진입 2
    게이트별: 콜드스타트/기타(DataAnomalyGate)=4  포지션보유중(평가생략)=4  체크리스트항목미달=4  모드필터=3  콜드스타트/기타(σ미수집)=2  쿨다운=2  ATR변동성=2  콜드스타트/기타(조건부구간)=1  콜드스타트/기타(RegimeOverride)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 9건
      └ 상세: JointGateBlock=9
      └ JointGateBlock 9건 (무정보폴백 9건 = 100.0%) [표본 11건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260930.txt`** — 233B · 09-30 15:53:33
```
completed: 2026-09-30 15:53:33
rows: 18002
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 25.1
t_retrain_s: 184.3
t_total_s: 210.0
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260930.txt`** — 43B · 09-30 15:47:14
```
auto_shutdown
2026-09-30T15:47:14.656200
```

_다이제스트 대상 8/18개 (중요도순). 제외: `20260930_DATA.log`, `20260930_PROBE.log`, `launcher_20260930_084000_10534.log`, `20260930_DEBUG.log`, `mainstall_traceback_20260930.log`, `20260930_REGULAR_COLLECT.log`, `peter_feed_push_20260930.log`, `force_flat_guard_20260930.log`_

### `logs/20260930_TRADE.log` — 10.0KB · 71행 · 최종 15:40:09

- 형식 평문 · 시각 인식 71행 · INFO=71

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-30 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-30 09:54:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,836,676) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-30 09:54:01 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd❌ ofi✅ fore✅ prev✅ time✅ risk✅ chas❌ coun✅ | conf=41.3%
2026-09-30 09:54:01 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 1095.04 | 손절=1097.12 1차=1094.07(×0.70) 2차=1092.95 horizon=5m hurst=neutral
  …
2026-09-30 14:27:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,483,814) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-30 14:27:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-09-30 14:29:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,483,814) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-09-30 14:29:00 [INFO] TRADE: [모드필터 차단] SHORT->SHORT 1계약 C급 (모드=hybrid, 허용=['A', 'B'])
2026-09-30 15:40:09 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×71

**컴포넌트 상위 15** — `Sizer`×16, `Chejan`×14, `Position`×9, `JointGateBlock 차단`×9, `주문요청`×6, `모드필터 차단`×3, `ProfitGuard`×2, `진입체크`×2, `체결진입`×2, `체결진입보정`×2, `손절1차 조기축소`×2, `TickStop-S0C`×2, `청산 완료`×2

### `logs/20260930_WARN.log` — 766.5KB · 3497행 · 최종 15:46:11

- 형식 평문 · 시각 인식 3490행 · WARNING=3490, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-30 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-30 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-30 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-30 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-30 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-30 11:17:00 cols=['open'] existing_source=rt
2026-09-30 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-30 11:21:00 cols=['open'] existing_source=rt
2026-09-30 15:46:08 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=410 inserted=1 open_fixed=1 mismatch=9
2026-09-30 15:46:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2229 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=2797 band=INFO since_pipe_s=2230.8
2026-09-30 15:46:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 142.4ms | size=1955x1124 candles=411 grid=49.5 spans=13.9 candles=21.4 dir=1.4 regime=8.0 markers=37.0 axes=0.7 cross=0.0 | slow_cnt=2938 total_cnt=3044 overlay_cnt=35189
```

</details>

**WARNING — 태그 32종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2938 | 08:59:47 | 15:46:11 | paintEvent slow 108.7ms | size=1955x1124 candles=15 grid=36.6 spans=0.5 candles=21.0 dir=0.0 regime=0.1 markers=0.2 axes=31.8 cross=0.0 | slow_cnt=1 total_cnt=1 overlay_cnt=0 |
| `LiveDBG` | 277 | 08:41:07 | 15:46:11 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 77 | 08:41:18 | 15:31:09 | 그리기 65.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `PipePerf` | 20 | 09:00:02 | 14:27:01 | total=2277ms | S0=3ms S1=14ms S2=0ms S3=0ms S4=348ms S5=996ms S6=790ms S7=100ms S8=24ms |
| `CB⑤` | 20 | 09:00:03 | 14:27:01 | 파이프라인 2277ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 18 | 09:00:02 | 14:30:00 | level=WARNING degraded=OFF | latency=2277ms | quality=1.00 | cache_age=53s | exceptions_10m=0 |
| `SHAP` | 18 | 11:27:01 | 14:53:01 | 슬로우 감지 956ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `ScalerRefresh` | 16 | 09:19:00 | 14:58:00 | 5분 누적 수익률 -0.383% (임계 ±0.312%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ChejanFlow` | 14 | 09:54:01 | 11:19:54 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1098' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:54:01.168' | positi… |
| `ChejanMatch` | 14 | 09:54:01 | 11:19:54 | order_no='1098' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1098 reason=진입 req_at=09:54:01.168' | pending_matched=True |
| `SessionBackfill` | 12 | 08:41:38 | 15:46:08 | OHLCV 불일치 ts=2026-09-29 09:57:00 cols=['open'] existing_source=rt |
| `PendingOrder` | 12 | 09:54:01 | 11:19:55 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1095.04, 'reason': '진입', 'hint_source': '', 'atr': 1.39, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |

**채널** — `SYSTEM`×3472, `HEALTH`×18

**컴포넌트 상위 15** — `ChartDBG`×2938, `LiveDBG`×277, `OptionFlowChart`×77, `PipePerf`×20, `CB⑤`×20, `Health`×18, `SHAP`×18, `ScalerRefresh`×16, `ChejanFlow`×14, `ChejanMatch`×14, `SessionBackfill`×12, `PendingOrder`×12, `CB③-P4`×10, `-`×7, `HealthPolicy`×4

### `logs/20260930_SYSTEM.log` — 979.4KB · 6628행 · 최종 15:47:14

- 형식 평문 · 시각 인식 6607행 · INFO=6607, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=29120 | 행감지=30s all_threads=True
2026-09-30 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.04s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-09-30 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-09-30 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-30 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-30 15:46:08 [INFO] SYSTEM: [SessionBackfill] 2026-09-30~2026-09-30 chart=411 existing=410 inserted=1 open_fixed=1 mismatch=9
2026-09-30 15:46:08 [INFO] SYSTEM: [BarGap] 당일 확정(2026-09-30) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-09-30 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-30 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-30 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6607

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1133, `PumpGuard`×768, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `System`×100, `MicroRegime`×92, `OptionChain`×81, `OptionBook`×79, `RegimeFingerprint`×68, `IntradayRegime`×35

### `logs/20260930_SIGNAL.log` — 600.9KB · 5259행 · 최종 15:40:10

- 형식 평문 · 시각 인식 5259행 · WARNING=2077, INFO=3182

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-09-30 15:10:00 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-30 15:40:09 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-30 15:40:10 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 0분(0.0%) / DN 118분(31.9%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-30 15:40:10 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-30 age=27m extreme=720 refresh=34 grade_x=158 cb3=0
2026-09-30 15:40:10 [INFO] SIGNAL: [ModelHealth] date=2026-09-30 앙상블유효가동률=73.0% | 파이프라인 370분 | ConstOut 9회/17분 {"3m": {"events": 8, "minutes": 15}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 83분 | 장중재학습 0회 | CB③ ready 269분/370분 (73%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1326 | 09:00:03 | 14:58:01 | 1m 'macro_vix' scale=0.0208 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 180 | 09:00:00 | 14:53:00 | ts=08:59 horizon=1m age=1m max_z=-5.73(institution_futures_net) extreme=2 adj=2 |
| `Checklist` | 173 | 09:06:00 | 15:09:00 | 신뢰도 미달 36.7% < 41.1% → 강제 X등급 |
| `Model` | 168 | 09:00:00 | 14:52:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerRefresh` | 138 | 08:45:08 | 13:01:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0082) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 83 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 9 | 09:35:00 | 13:34:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |

**채널** — `SIGNAL`×5259

**컴포넌트 상위 15** — `ScalerFloor`×1344, `SIGNAL`×740, `Ensemble`×396, `MetaGate`×375, `FQAdj`×369, `ZeroDiag`×344, `Checklist`×221, `ScalerMonitor`×181, `ATR-Horizon`×179, `ScalerRefresh`×177, `Model`×174, `ToxicityGate`×111, `MicroRegime`×92, `차단`×91, `WeightCollapse`×83

### `logs/20260930_LEARNING.log` — 287.1KB · 2814행 · 최종 15:40:10

- 형식 평문 · 시각 인식 2814행 · WARNING=155, INFO=2659

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00142 auc=0.408 out_max=0.2382 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00033 auc=0.441 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-30 08:40:50 [WARNING] LEARNING: [Calibration:5m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00041 auc=0.608 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-09-30 15:40:09 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-30 15:40:09 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-30 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-30 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-30 15:40:10 [INFO] LEARNING: [Sigma] EOD sigma_20=0.06812% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 53 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 48 | 08:40:49 | 13:23:00 | 축퇴 감지 — span=0.00142 auc=0.408 out_max=0.2382 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 17 | 08:40:49 | 08:40:57 | 축퇴 감지 — span=0.00033 auc=0.441 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 10 | 08:40:50 | 08:40:57 | 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00041 auc=0.608 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 8 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00064 auc=0.510 out_max=0.4253 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 8 | 08:40:52 | 09:29:00 | 축퇴 감지 — span=0.00041 auc=0.510 out_max=0.4552 (기준 auc<0.53 and span<0.020, 기저율=0.4550 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 7 | 08:40:58 | 14:42:00 | 복원한 보정기가 하한 도달불가 — out_max=0.3070 < conf_floor=0.3300 (span=0.00442 auc=0.539 out_max=0.3070, n=1776) → 보정 미적용으로 시작, raw 통과. 축퇴(auc/span)와 별개 사유이며, 표본이 쌓여 출력상한이 하한 위로 올라오면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 3 | 09:02:00 | 10:34:00 | total=712ms raw_fetch=296ms pred_select=4ms pred_update=5ms pred_insert=53ms verified=1 |
| `DriftAdjuster` | 1 | 15:40:09 | 15:40:09 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 16일) |

**채널** — `LEARNING`×2814

**컴포넌트 상위 15** — `LEARNING`×1211, `SGD`×369, `sigma`×357, `Bias⚠`×223, `Bias`×151, `Calibration:1m`×104, `Calibration:30m`×95, `MetaConf`×78, `OnlineLearner`×45, `ScalerWarmup`×39, `Calibration:3m`×32, `BiasReset`×20, `Calibration:5m`×19, `Calibration:15m`×16, `Calibration:10m`×15

### `logs/20260930_HEALTH.log` — 4.9KB · 34행 · 최종 14:31:00

- 형식 평문 · 시각 인식 34행 · WARNING=18, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2277ms | quality=1.00 | cache_age=53s | exceptions_10m=0
2026-09-30 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=833ms | quality=1.00 | cache_age=111s | exceptions_10m=0
2026-09-30 09:02:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2440ms | quality=0.88 | cache_age=173s | exceptions_10m=0
2026-09-30 09:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=474ms | quality=1.00 | cache_age=45s | exceptions_10m=0
2026-09-30 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 377ms (표본 20분)
  …
2026-09-30 14:26:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1143ms | quality=1.00 | cache_age=126s | exceptions_10m=0
2026-09-30 14:27:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1129ms | quality=1.00 | cache_age=2s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-30 14:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=331ms | quality=1.00 | cache_age=61s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-30 14:30:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=403ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-30 14:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=323ms | quality=1.00 | cache_age=57s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 18 | 09:00:02 | 14:30:00 | level=WARNING degraded=OFF | latency=2277ms | quality=1.00 | cache_age=53s | exceptions_10m=0 |

**채널** — `HEALTH`×34

**컴포넌트 상위 15** — `Health`×33, `HealthTrend`×1

### `logs/retrain_eod_20260930.log` — 21.4KB · 147행 · 최종 15:53:34

- 형식 평문 · 시각 인식 147행 · WARNING=10, INFO=137

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 15:50:02,964 [INFO] EOD_RETRAIN: =======================================================
2026-09-30 15:50:02,964 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-30 15:50:02,965 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-30 15:50:02,965 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-30 15:50:02,965 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-30 15:53:34,101 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0363 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-30 15:53:34,104 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0984 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-30 15:53:34,107 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-09-30 15:53:34,111 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-30 15:53:34,113 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:40 | 15:52:44 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-29 14:38:00 ≥ 홀드아웃 시작=2026-09-21 12:18:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-29 14:38 >= holdout_start=2026-09-21 12:18 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-29 … |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-09-30 | 최신 2026-09-29 · 기준 6거래일. 복구: python scripts/collect_regular_futures.py --from 20260930 --to 20260930 |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 23146/44836 제외 (418차 결정 1) — 남은 21690행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/21690행 제외 (559차 P1'-2) — 남은 20244행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:33 | 15:53:33 | 백필 0행 제외 — 필터가 무효일 수 있다. 18002행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×62, `SIGNAL`×49, `EOD_RETRAIN`×26, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2, `P8`×2

### `logs/20260930_MICRO.log` — 974.0KB · 2595행 · 최종 15:38:32

- 형식 평문 · 시각 인식 2595행 · DEBUG=2595

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1099.14/2 ask1=1099.52/1 mp={'microprice_tick': 1099.3934, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.3472} mlofi_tick=None queue=None
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1099.14/1 ask1=1099.52/2 mp={'microprice_tick': 1099.2667, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.4645} mlofi_tick=-4.4333 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio'…
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1099.14/1 ask1=1099.52/2 mp={'microprice_tick': 1099.2667, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.3971} mlofi_tick=-2.5167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-30 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1099.16/1 ask1=1099.54/1 mp={'microprice_tick': 1099.35, 'midprice_tick': 1099.35, 'depth_bias_tick': -0.4758} mlofi_tick=13.1333 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-30 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1099.18/1 ask1=1099.48/1 mp={'microprice_tick': 1099.33, 'midprice_tick': 1099.33, 'depth_bias_tick': -0.4691} mlofi_tick=-5.1833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
  …
2026-09-30 15:34:44 [DEBUG] MICRO: [MICRO-TICK] #218700 bid1=1084.78/3 ask1=1085.00/2 mp={'microprice_tick': 1084.912, 'midprice_tick': 1084.89, 'depth_bias_tick': -0.0446} mlofi_tick=-5.7167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_r…
2026-09-30 15:35:06 [DEBUG] MICRO: [MICRO-TICK] #218800 bid1=1084.82/3 ask1=1084.86/1 mp={'microprice_tick': 1084.85, 'midprice_tick': 1084.84, 'depth_bias_tick': 0.5417} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-30 15:35:35 [DEBUG] MICRO: [MICRO-TICK] #218900 bid1=1084.72/10 ask1=1084.88/1 mp={'microprice_tick': 1084.8655, 'midprice_tick': 1084.8, 'depth_bias_tick': 0.6429} mlofi_tick=9.0 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 9.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-09-30 15:36:11 [DEBUG] MICRO: [MICRO-TICK] #219000 bid1=1085.86/1 ask1=1085.98/1 mp={'microprice_tick': 1085.92, 'midprice_tick': 1085.92, 'depth_bias_tick': -0.2903} mlofi_tick=-3.3333 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-30 15:38:32 [DEBUG] MICRO: [MICRO-TICK] #219100 bid1=1086.12/1 ask1=1086.40/3 mp={'microprice_tick': 1086.19, 'midprice_tick': 1086.26, 'depth_bias_tick': -0.3889} mlofi_tick=-1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio…
```

</details>

**채널** — `MICRO`×2595

**컴포넌트 상위 15** — `MICRO-TICK`×2211, `MICRO-MINUTE`×384

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -352832원
════════════════════════════════════════════════════
2026-09-30 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-30 10:39:00 cols=['open'] existing_source=rt
2026-09-30 15:46:08 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-30 10:40:00 cols=['open'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) — **엔진** | 2 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 91 |
| 사이저 호출(`[Sizer]`) | 16 |

### 포지션 2건 · 승 0 (0%) · 합계 -6.20pt (-352,834원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:54:01 | 엔진 | SHORT | 2 | 5m | 2 | -2.98 | -170,486 | 하드스톱(틱) |
| 11:17:01 | 엔진 | SHORT | 2 | 5m | 2 | -3.22 | -182,348 | 하드스톱(틱) |

**청산 레그 4행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:55:36 | 부분 | 1 | -0.91 | -56,243 | 손절1차 조기축소 |
| 09:57:19 | 전량 | 1 | -2.07 | -114,243 | 하드스톱(틱) |
| 11:17:14 | 부분 | 1 | -1.14 | -67,674 | 손절1차 조기축소 |
| 11:19:54 | 전량 | 1 | -2.08 | -114,674 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `손절1차 조기축소`×2, `하드스톱(틱)`×2

> 최종 청산이 하드스톱·손절 계열인 포지션 2/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -352,834 = 포지션합 -352,834 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### CB③ 판정 가능 시간 — **269분 / 370분 (73%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:54:01 | SHORT | 2 | 1095.04 | 5m | neutral |
| 11:17:01 | SHORT | 2 | 1088.04 | 5m | trend |

계약수 분포 — 2계약×2

등급 분포 — `A급(원시C)`×2

**진입한 건들의 체크리스트 미통과 항목** — `chas`×2, `cvd`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×2, **3계약**×14

실제 진입 계약수 — **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×16

### 차단 사유 91건 · 22종

| 건수 | 사유 |
|---|---|
| 54 | 등급X — 미통과 항목: 2_confidence |
| 5 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 3 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 3 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 18초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign |
| 1 | 청산 후 쿨다운 — 173초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 113초 후 재진입 가능 |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.89pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×54, `3_vwap`×6, `6_foreign`×6, `4_cvd`×4, `5_ofi`×3, `7_prev_bar`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 6건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×2
- `일간 리셋 완료` ×2
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-30 09:54:01, 현재 1…` ×1
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-30 11:17:01, 현재 1…` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 27건 · 최대 6359ms · 5초 초과 2건

상위 — 6359ms, 5156ms, 4718ms, 4094ms, 3938ms, 3438ms, 3156ms, 3110ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6359ms | 2277ms | **4082ms (64%)** |
| 09:02:05 | 5156ms | 2440ms | **2716ms (53%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260930_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:17 2026-09-30 15:40:17 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 37분/일 < 하한 60분 — 금일 37분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 370분
--- [CB] ×2(표본)
09:55:36 2026-09-30 09:55:36 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:17:14 2026-09-30 11:17:14 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×5(표본)
09:57:19 2026-09-30 09:57:19 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:00:19)
09:57:19 2026-09-30 09:57:19 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:00:19)
11:19:54 2026-09-30 11:19:54 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:22:54)
11:19:54 2026-09-30 11:19:54 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:22:54)
--- [SHAP] 슬로우 ×8(표본)
11:27:01 2026-09-30 11:27:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 956ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:36:01 2026-09-30 11:36:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 924ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:44:01 2026-09-30 11:44:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 906ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:55:01 2026-09-30 11:55:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 945ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:11 2026-09-30 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3438ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3438 band=INFO since_pipe_s=NA
08:59:50 2026-09-30 08:59:50 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2891ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2891 band=INFO since_pipe_s=NA
09:00:06 2026-09-30 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6359ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6359 band=WARN since_pipe_s=0.3
09:01:02 2026-09-30 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2109ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2109 band=INFO since_pipe_s=0.3
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260930_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-30 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4701) | 앙상블 제외는 유지
09:44:00 2026-09-30 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4166) | 앙상블 제외는 유지
10:39:00 2026-09-30 10:39:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4252) | 앙상블 제외는 유지
10:47:00 2026-09-30 10:47:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4720) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:10 2026-09-30 15:40:10 [INFO] SYSTEM: [CB③계측] 조건성립 180분 / 판정가능 269분 / 파이프라인 370분 · 그 창 진입 5포지션 · 손익 -182,348원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-30 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:06:00 2026-09-30 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:12:00 2026-09-30 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-30 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×4(표본)
09:57:19 2026-09-30 09:57:19 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-30 09:54:01, 현재 1회)
11:19:54 2026-09-30 11:19:54 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-30 11:17:01, 현재 1회)
15:40:09 2026-09-30 15:40:09 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:09 2026-09-30 15:40:09 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:08 2026-09-30 15:11:08 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:18 2026-09-30 15:40:18 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-09-30 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:18 2026-09-30 15:40:18 [INFO] SYSTEM: [Notify] ℹ️ [15:40:18] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:18 2026-09-30 15:40:18 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 401초
15:40:18 2026-09-30 15:40:18 [INFO] SYSTEM: 자동 종료 예약 — 416초 후 Qt 이벤트 루프 종료
```

### `logs/20260930_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-30 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0890 dir=-1)
09:35:00 2026-09-30 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-30 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-30 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0890 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-09-30 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-30 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-30 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-30 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:41 2026-09-30 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
--- 안전망 ×8(표본)
09:07:00 2026-09-30 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-30 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-30 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-30 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260930_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00142 auc=0.408 out_max=0.2382 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-30 08:40:49 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00033 auc=0.441 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-09-30 08:40:50 [WARNING] LEARNING: [Calibration:5m] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00041 auc=0.608 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

### `logs/20260930_HEALTH.log`
```
--- [ExitCooldown] ×2(표본)
11:23:00 2026-09-30 11:23:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=559ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
11:24:00 2026-09-30 11:24:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=452ms | quality=1.00 | cache_age=57s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260930_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 21 | 09:54:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,836,676) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 14:00 | 장중 후반 · 장중 재학습 | 1 | 13:57:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,483,814) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:09 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260930_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 18 | 08:59:47 [WARNING] paintEvent slow 108.7ms | size=1955x1124 candles=15 grid=36.6 spans=0.5 candles=21.0 dir=0.0 regime=0.1 marke… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 36 | 08:59:47 [WARNING] paintEvent slow 108.7ms | size=1955x1124 candles=15 grid=36.6 spans=0.5 candles=21.0 dir=0.0 regime=0.1 marke… |
| 10:00 | 장중 초반 | 159 | 09:54:01 [WARNING] paintEvent slow 96.5ms | size=1955x1124 candles=70 grid=32.5 spans=0.0 candles=3.6 dir=0.3 regime=4.1 markers… |
| 12:00 | 장중 중간점 | 107 | 11:54:01 [WARNING] paintEvent slow 157.3ms | size=1955x1096 candles=58 grid=51.8 spans=13.8 candles=4.2 dir=0.4 regime=10.5 mark… |
| 14:00 | 장중 후반 · 장중 재학습 | 104 | 13:54:00 [WARNING] 5분 누적 수익률 -0.138% (임계 ±0.113%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 97 | 15:04:01 [WARNING] paintEvent slow 150.1ms | size=1955x1124 candles=380 grid=48.3 spans=10.3 candles=19.6 dir=2.2 regime=10.8 ma… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 97 | 15:12:00 [WARNING] paintEvent slow 90.0ms | size=1955x1124 candles=388 grid=20.4 spans=6.5 candles=15.1 dir=1.6 regime=7.3 marke… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 18 | 15:34:00 [WARNING] paintEvent slow 138.0ms | size=1955x1124 candles=410 grid=37.0 spans=15.7 candles=16.9 dir=1.6 regime=14.2 ma… |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:46:08 [WARNING] OHLCV 불일치 ts=2026-09-30 10:39:00 cols=['open'] existing_source=rt |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260930_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=29120 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 138 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 197 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 272 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 201 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 203 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 178 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 154 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 60 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:41:08 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:08 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260930_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0082) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 78 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 158 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 162 | 09:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 12:00 | 장중 중간점 | 160 | 11:54:00 [WARNING] 신뢰도 미달 39.2% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 152 | 13:54:00 [WARNING] 신뢰도 미달 33.1% < 39.5% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 55 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:09 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260929 | 15:47 | 로그 본문 |
| 20260928 | 15:47 | 로그 본문 |
| 20260926 | 16:50 | 로그 본문 |
| 20260924 | 10:58 | 로그 본문 |
| 20260923 | 18:44 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20260930** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-29 (MW0601 637ì°¨ â ì¥ì  ì ê²)
## 2026-09-29 (MW0601 638ì°¨ â ì¥ì¤ ì ê²)
## 2026-09-29 (MW0601 639ì°¨ â ì ë ê·ê²© v2 ê°ì : 1ì°¨ ëª©íê° ì§ì
## 2026-09-29 (MW0601 640ì°¨ â ì¥í ì ê²)
## 2026-09-29 (MW0601 641ì°¨ â ì¥í ìëì¡°ì¹: 637-2 crash_fault.log ë¤ì´í°ë¸ ì¤ë¥ ì§ê³ + 638-1 git ì¤í¨ ì§ë¨Â·ì´ì¤ ë°©ì´)
## 2026-09-30 (MW0601 642ì°¨ â ì¥ì  ì ê²)
## 2026-09-30 (MW0601 642ì°¨ íì â ì¥ì  ì ê² ëì¤ `.git/index.lock` ì¤ì¸¡ ë°ìÂ·íì)
## 2026-09-30 (MW0601 643ì°¨ â ì¥ì¤ ì ê²)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 ì°¨(HOLD ëê¸° â STALE íì  â `--reclaim`)ë¥¼ ê·¸ëë¡ ë°ë¼ ìì íê² íìíë¤ â íì ë³´ë¥ ìíìì ì§ì°ì§ ìë ìì¹ì ë¤ì íë² ì¤ì.
2. ì¥ì ì´ "ìí(mitigation)ì´ì§ ë´ì(prevention)ê° ìëë¤"ë¡ ì¬ë¶ë¥í ê°ì¤ì´ íë³¸ 2ê±´(ì¤ë íë£¨ ìììë§)ì¼ë¡ ê°íëë¤. ì ê· Fixë¡ F-4(ì§ë¨ ë¡ê¹ ê°í, `GIT_TRACE` ë±ì¼ë¡ ì´ë íìëªë ¹ì´ ì¸ë±ì¤ë¥¼ ì°ëì§ í¹ì )ë¥¼ ë±ë¡íë¤.
3. ì ê· ê³ ëí G-2(ì ê² ì¸ìì git í¸ì¶ì `git status --porcelain=v2 --branch` í ë²ì¼ë¡ íµí©íë ì í¸ ì ì)ë¥¼ ë±ë¡íë¤ â ì¤ë ë ë² ë¤ "ì¬ë¬ ëªë ¹ì ì°ë¬ì ì¤í"íë ìì ì ë°ìíë¤ë ê³µíµì ìì ì°©ì.
4. ì ë¶ì¤ë¬ê¸° íì¼(`index.lock.stale_20260930033834_6`)ì ì¬ì©ì ì¡°ì¹ë¡ ìë´(Windows íê²½ììë§ ì­ì  ê°ë¥). ê¸°ì¡´ 1-6(ë¶ì¤ë¬ê¸°)ì ê±´ìë§ ê°±ì , ì ë²í¸ë ë¶ì¬íì§ ìëë¤.
5. O-i1(ë¤ì ê±°ëì¼ìë ì¬íëëì§ ê´ì°°) ì ê· ë±ë¡ â íì  ìì  2026-10-01.
6. ë¦¬í¬í¸ íì¼ appendë device_bashë¡ ì§ì  í¸ì§íë ëì , ìë³¸ì ê·¸ëë¡ ê°ì ¸ì(ì¤íì´ì§) ì ì ì ê·¸ ë¤ì ì íí ì´ì´ë¶ì¸ ë¤ íì¼ ì ì²´ë¥¼ ë¤ì ê°ì ê²½ë¡ì ì¨ë£ë ë°©ì(ì¤íì´ì§âë³í©âì»¤ë°, mtime ê°ë í¬í¨)ì ì¼ë¤ â ì½ì ì¸ìì´ íê¸ì´ ìì¸ ê¸´ ë§í¬ë¤ì´ì ì¸ ëªë ¹ ì¸ìë¡ ì§ì  íì´ííë¤ ì¸ì½ë©ì´ ê¹¨ì§ ì ë¡(ì´ íì¼ì 642ì°¨ íì í­ëª© ë³¸ë¬¸ ì°¸ì¡°)ë¥¼ ë°ë³µíì§ ìê¸° ìí¨ì´ë¤.

**Why**: ê³ì¸¡ 4ìì¹ â "ì ë³´ì´ë ìíì´ ì¤ì ë¡ ë°ìíì ë ì¡°ì©í ëì´ê°ì§ ìëë¤." ê°ì ë  ë ë²ì§¸ ì¬íì ì°ì°ì¼ë¡ ì¹ë¶íê¸°ì ë¹ëê° ëë¤.

**How to apply**: F-4ë ë¤ì ì¸ì(ì¥í ëë ë³ë)ìì `scripts/git_lock_guard.py`Â·`scripts/collect_evidence.py`ì git í¸ì¶ë¶ì ì§ë¨ ë¡ê¹ì ì¶ê°. G-2ë ì F-4ë¡ ìì¸ì ë¨¼ì  í¹ì í ë¤ ì¤ê³.

**ê²ì¦**: íì í `git --no-optional-locks status --short` ì ì ëì íì¸, `.git/index.lock` ìë©¸ íì¸. ë¦¬í¬í¸ íì¼(ì¥ì +ì¥ì¤ ë³í©ë³¸) ë°ì´í¸ ì ëì¡°ë¡ ë³í© ê²°ê³¼ ë¬´ê²°ì± íì¸(ìë³¸ 28,041ë°ì´í¸ + ì ê· ì  20,885ë°ì´í¸ = 48,926ë°ì´í¸ ì¼ì¹).

â  **ì½ë ë³ê²½ ìì(ì¼ë° ì¥ì¤ ì ê² ì¸ì).** `git commit`Â·`git push` íì§ ììì â ì¬ì©ìê° ì§ì  íì¸ í ì»¤ë°íë¤. **ë¼ì´ë¸ DB ë¶ì ì¿¼ë¦¬ ì¤í ì í¨**(ë¡ê·¸ ì ì© ì ê² ì ì§).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-28 (MW0601 636차 — 장후 자동조치)
## 2026-09-29 (MW0601 637차 — 장전 점검)
## 2026-09-29 (MW0601 638차 — 장중 점검)
## 2026-09-29 (MW0601 640차 — 장후 점검)
## 2026-09-29 (MW0601 641차 — 장후 자동조치)
## 2026-09-30 (MW0601 642차 — 장전 점검)
## 2026-09-30 (MW0601 642차 후속 — 장전 점검 도중 `.git/index.lock` 실측·회수)
## 2026-09-30 (MW0601 643차 — 장중 점검) 신규 항목
```

미완료 체크박스 **2904건** (끝에서 30건)
```
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
- [ ] **640-1** P5-17(5m 호라이즌 TIER1_EARLY→INITIAL_STOP 연쇄 손절 관찰) — 오늘 CASE4·5·8 3건/1거래일, 합계 −380,476원. 신규 채널(`horizon_5m_early_stop_watch` 가칭) 신설 여부는 사용자 판단 — 우선은 다음 장후들이 5m 호라이즌 진입 결과를 계속 케이스로 기록해 표…
- [ ] **640-2** `docs/정기점검/수익률향상_누적대장.md` P5-03에 0928 CASE-01 표본이 아직 반영되지 않음(635-1 계승, 2회째 미처리 확인) — 다음 세션이 직접 대장 파일을 열어 반영할 것.
- [ ] **640-3 (사용자, 참고)** 신동(별도 매매 모듈) v2 개정(639차, 별도 세션) — 내일(09-30) 자동 기동 시 라이브 반영 예정. 규격 준수 근거로 개정됐으나 과거 5거래일 재현에서는 v1(결함 버전)이 오히려 손실이 적었다는 상반된 실측 기록 있음 — 사용자가 `docs/신동거래/신동_개정_v2_1차목표역전_20260929.…
- [ ] **O-t1** 09-30 장전 부팅 구간 access violation 재현 여부(3일 연속 뒤 4일째 확인) — 606-4 우선순위 결정 참고자료 계속 축적.
- [ ] **O-t2** 09-30 장전 거래일 전환 시 SessionStateDrop 재현 여부 확인(근본원인 606-2 미해결로 재현 예상, 예상대로면 지속 기록만).
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
해 수집기 §9 표·§11 적신호에 올린다(`utils/wer_crash.py` `fatal`/`fatal_total`, `collect_evidence.py:fatal_exception_lines`). 검증: 09-28 4건 · 09-29 3건 재현. `tests/test_641_*`.
- [x] **638-1 완료** — `run_git()` 에 `GIT_OPTIONAL_LOCKS=0` 환경변수 이중 전달 + `git_change_profile()` `fail_reason`(실패 명령·rc·stderr) 을 §2·§11 에 표기. ⚠ 락 생성 원인 확정이 아니다 — 다음 `git diff` 실패 때 §2 「실패 명령:」 으로 원인을 좁혀 이 항목을 재평가할 것.
- [ ] **641-1 (G-2, 보류)** 부팅 구간 access violation 경고 **문턱** 신설 여부 — 관측일 3건(09-17·09-28·09-29)뿐이라 313차 가드 미통과. 지금 §11 은 문턱 없이 1건부터 건수만 올린다. 관측일이 더 쌓이면(예: 10거래일) 분포를 보고 문턱을 정할 것. 606-4(원인 조사 우선순위, 사용자 결정 대기)와 함께 볼 것.

## 2026-09-30 (MW0601 642차 — 장전 점검)

- [ ] **642-1 (P2)** `dev_memory/_tmp_append_20260929.txt`·`_tmp_append_todo_20260929.txt` 정리 — 0바이트 미추적 스크래치 파일 2건 발견. 라이브 프로세스 미참조 재확인 후 삭제. 근거: 0930 장전 이상점 1-3.
- [ ] **642-2 (G-1, 고도화 제안)** `scripts/collect_evidence.py` §9에 `[PreRetrain]` "EOD 마커 파일 직접 확인" 우회 성공 여부를 자동 표시 — 현재는 로그 직접 grep 필요. 근거: 0930 장전 SessionStateDrop 재현 시 우회 확인에 수동 grep 소요.
- [x] **O-t1 판정 완료** — 부팅 구간 access violation 재현 여부, 0930 장전 3건 재현(4일째: 09-17·09-28·09-29·09-30). 641-1로 계속 이월(문턱 신설은 표본 부족으로 보류 유지).
- [x] **O-t2 판정 완료** — SessionStateDrop 재현 여부, 0930 장전 08:41:08 재현 확인. 606-2(근본원인)·532차 F-1(수정 미착수)로 계속 이월. `[PreRetrain]` 우회 확인은 정상 작동.
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — 문서 제목 "재" 글자 손상, 0930 장전에도 미확인·미커밋 지속(**5일째**, 변화 없음).

## 2026-09-30 (MW0601 642차 후속 — 장전 점검 도중 `.git/index.lock` 실측·회수)

- [ ] **642-3 (사용자, Windows 환경)** `.git/index.lock.stale_20260930001115_6` 삭제 — 이 세션(device_bash 리눅스 VM)에서는 `Operation not permitted`로 불가. 2026-08-21 `index.lock.stale_20260929033733_6`와 함께 정리 권장.
- [ ] **642-4 (조건부 고도화)** `git --no-optional-locks diff`가 오늘 실제로 `.git/index.lock`을 남긴 사례 확인(09-30 09:00:35 KST) — 다음에 같은 현상이 또 재현되면(장전·장중·장후 무관) G-1급 고도화로 "세션 종료 직전 `git_lock_guard.py --check` 자동 실행"을 검토할 것. 1회 관측만으로는 313차 원칙상 결론 보류.

## 2026-09-30 (MW0601 643차 — 장중 점검) 신규 항목

- [ ] **F-4** `scripts/git_lock_guard.py`·`scripts/collect_evidence.py:run_git()`에 진단 로깅 추가 — `.git/index.lock`이 `--no-optional-locks` 부착 상태에서도 생성될 때, 직전 실행된 git 하위명령을 특정할 수 있도록(`GIT_TRACE` 등). 근거: 2026-09-30 하루에 장전·장중 두 번 재현(둘 다 원인 미상).
- [ ] **G-2** 점검 세션의 git 상태 확인을 `git status --porcelain=v2 --branch` 한 번으로 통합하는 헬퍼 제안 — `branch`·`status`·`log`를 연달아 실행하는 시점에 두 번 다 락이 발생한 공통점에서 착안. F-4로 원인 특정 후 설계.
- [ ] **O-i1** 다음 거래일(2026-10-01) 점검에서도 `.git/index.lock` 현상이 재현되는지 관찰 — 재현되면 "구조적 현상"으로 격상, 아니면 완화 검토.
- [ ] `.git/index.lock.stale_20260930033834_6` 삭제(Windows 환경에서만 가능, 코웍 세션은 EPERM으로 불가) — 장중 643차 회수 부스러기.

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

### `data/heartbeat_MW0601_20260930.json` — 245B · 09-30 15:46:54
```json
{
 "pid": 29120,
 "written_at": "2026-09-30T15:46:54",
 "beat_epoch": 1790750813.4414067,
 "beat_age_sec": 0.7,
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

- 파일 최종 기록: **09-30 15:53:34**

| 키 | 값 | 수집 대상일(2026-09-30)과 일치 |
|---|---|---|
| `date` | 2026-09-30 | 예 |
| `p8_last_success_date` | 2026-09-30 | 예 |
| `eod_retrain_ok_date` | 2026-09-30 | 예 |

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

- 라이브 로그 대조: `logs/20260930_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 29120: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:44 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 29120 | 08:40:44 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 180개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260930-점검리포트.md` | 47.8KB | 09-30 12:45 |
| `docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md` | 77.7KB | 09-30 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260930_pre.md` | 62.7KB | 09-30 09:01 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_pre.md` | 59.0KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_post.md` | 90.0KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_intra.md` | 74.7KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md` | 56.8KB | 09-29 18:50 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_post.md` | 84.8KB | 09-29 18:50 |

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
2. 포지션 2건 중 최종청산이 하드스톱·손절 계열 **2건(100%)** — 손절 준수율 확인 필요 (레그 4행)
3. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. 메인 스레드 정지 5초 초과 **2건** (최대 6359ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260930_SYSTEM.log`: **ConstOut** 8건(표본)
7. `logs/20260930_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20260930_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20260930_LEARNING.log`: **축퇴** 8건(표본)
10. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
11. 미커밋 변경 10건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260930*.log` (Windows) / `grep 강제청산 logs/*20260930*.log`*