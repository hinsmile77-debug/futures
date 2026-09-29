# 미륵이 증거 다이제스트 — 2026-09-29 / INTRA

- 생성 2026-09-29 12:26:27 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01ye5morgbnjlsrcublnsuxb/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260929` · `2026-09-29` · `260929` · `0929`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20260929.log` | 137B | 09-29 07:22 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260929.log` | 125B | 09-29 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260929.log` | 140B | 09-29 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260929.json` | 244B | 09-29 12:26 |
| `launcher_{DATE}_084000_23300.log` | 1 | `logs/Mireuk_batch/launcher_20260929_084000_23300.log` | 1.3MB | 09-29 12:26 |
| `position_state.json.gen_{DATE}_110902` | 1 | `data/position_state.json.gen_20260929_110902` | 1.5KB | 09-29 11:09 |
| `position_state.json.gen_{DATE}_111237` | 1 | `data/position_state.json.gen_20260929_111237` | 1.5KB | 09-29 11:09 |
| `position_state.json.gen_{DATE}_111300` | 1 | `data/position_state.json.gen_20260929_111300` | 1.5KB | 09-29 11:12 |
| `{DATE}_DATA.log` | 1 | `logs/20260929_DATA.log` | 230.1KB | 09-29 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260929_DEBUG.log` | 134.1KB | 09-29 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260929_HEALTH.log` | 1.8KB | 09-29 12:02 |
| `{DATE}_HOGA.log` | 1 | `logs/20260929_HOGA.log` | 29.9MB | 09-29 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260929_LEARNING.log` | 184.9KB | 09-29 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260929_MICRO.log` | 562.5KB | 09-29 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260929_PROBE.log` | 55.5KB | 09-29 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260929_SIGNAL.log` | 332.0KB | 09-29 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260929_SYSTEM.log` | 516.9KB | 09-29 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260929_TRADE.log` | 6.3KB | 09-29 11:53 |
| `{DATE}_WARN.log` | 1 | `logs/20260929_WARN.log` | 373.0KB | 09-29 12:26 |

## 2. 코드·커밋 상태

- HEAD `f1efe56` · 브랜치 `v9-dev` · 미커밋 10건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
?? dev_memory/_tmp_append_20260929.txt
?? dev_memory/_tmp_append_todo_20260929.txt
?? docs/정기점검/매일점검/MW0601-20260929-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20260929_pre.md
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

_본문 미열람(설정): `20260929_HOGA.log` 29.9MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260929_PROBE.log`, `launcher_20260929_084000_23300.log`, `20260929_DEBUG.log`, `freeze_sentinel_20260929.log`, `claude_resume_20260929.log`, `force_flat_guard_20260929.log`_

### `logs/20260929_TRADE.log` — 6.3KB · 50행 · 최종 11:53:00

- 형식 평문 · 시각 인식 50행 · INFO=50

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-29 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-29 09:57:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,943,671) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-29 09:57:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas❌ coun✅ | conf=45.1%
2026-09-29 09:57:00 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 1084.1 | 손절=1086.07 1차=1083.44(×0.42) 2차=1082.13 horizon=3m hurst=mean-revert
  …
2026-09-29 11:13:00 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2333 code=A056A 방향=SHORT 체결=1 미체결=0
2026-09-29 11:13:00 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2333 code=A056A 방향=SHORT 체결=1 미체결=0
2026-09-29 11:13:00 [INFO] TRADE: [Position] 체결청산 LONG @ 1089.38 | PnL=+1.17pt (+47,824원) | 하드스톱
2026-09-29 11:13:00 [INFO] TRADE: [청산 완료] PnL=+1.17pt (+47,824원) | 포지션 합계 +66,648원 (레그 2)
2026-09-29 11:53:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,027,049) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
```

</details>

**채널** — `TRADE`×50

**컴포넌트 상위 15** — `Chejan`×14, `Position`×9, `주문요청`×6, `Sizer`×5, `진입체크`×2, `체결진입`×2, `체결진입보정`×2, `TickTP1`×2, `TP1 부분청산`×2, `청산 완료`×2, `ProfitGuard`×1, `TickStop-S0C`×1, `모드필터 차단`×1, `JointGateBlock 차단`×1

### `logs/20260929_WARN.log` — 373.0KB · 1665행 · 최종 12:26:20

- 형식 평문 · 시각 인식 1665행 · WARNING=1665

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-29 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-29 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-29 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-29 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-29 12:27:09 [WARNING] SYSTEM: [OptionFlowChart] 그리기 129.9ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 847x1001
2026-09-29 12:27:09 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 165.2ms | size=1955x1124 candles=223 grid=55.8 spans=15.9 candles=10.7 dir=0.9 regime=10.5 markers=48.3 axes=21.5 cross=0.0 | slow_cnt=1439 total_cnt=1514 overlay_cnt=18973
2026-09-29 12:27:13 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 201.0ms | size=1955x1124 candles=223 grid=74.5 spans=16.4 candles=9.1 dir=1.0 regime=13.8 markers=60.3 axes=23.8 cross=0.0 | slow_cnt=1440 total_cnt=1515 overlay_cnt=18978
2026-09-29 12:27:23 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 226.8ms | size=1955x1124 candles=223 grid=68.4 spans=18.4 candles=12.6 dir=1.1 regime=12.3 markers=82.5 axes=29.5 cross=0.0 | slow_cnt=1441 total_cnt=1516 overlay_cnt=18990
2026-09-29 12:27:33 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 205.6ms | size=1955x1124 candles=223 grid=91.4 spans=17.3 candles=12.0 dir=0.9 regime=11.0 markers=45.4 axes=25.4 cross=0.0 | slow_cnt=1442 total_cnt=1517 overlay_cnt=19000
```

</details>

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1442 | 09:05:12 | 12:27:33 | paintEvent slow 66.9ms | size=1955x1124 candles=21 grid=30.3 spans=0.0 candles=1.0 dir=0.0 regime=0.0 markers=0.0 axes=34.2 cross=0.0 | slow_cnt=1 total_cnt=5 overlay_cnt=2 |
| `LiveDBG` | 70 | 08:41:08 | 12:27:09 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 41 | 08:41:18 | 12:27:09 | 그리기 73.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `ChejanFlow` | 14 | 09:57:01 | 11:13:00 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1257' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:57:00.822' | positi… |
| `ChejanMatch` | 14 | 09:57:01 | 11:13:00 | order_no='1257' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1257 reason=진입 req_at=09:57:00.822' | pending_matched=True |
| `PendingOrder` | 12 | 09:57:00 | 11:13:01 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1084.1, 'reason': '진입', 'hint_source': '', 'atr': 1.5414, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qt… |
| `ScalerRefresh` | 9 | 09:11:00 | 12:12:00 | 5분 누적 수익률 +0.555% (임계 ±0.454%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SessionBackfill` | 6 | 08:41:39 | 08:41:39 | OHLCV 불일치 ts=2026-09-28 09:34:00 cols=['open'] existing_source=rt |
| `Health` | 6 | 09:00:01 | 12:01:00 | level=WARNING degraded=OFF | latency=1862ms | quality=1.00 | cache_age=44s | exceptions_10m=0 |
| `PipePerf` | 4 | 09:00:01 | 09:12:03 | total=1862ms | S0=5ms S1=71ms S2=0ms S3=0ms S4=132ms S5=752ms S6=858ms S7=37ms S8=7ms |
| `CB⑤` | 4 | 09:00:02 | 09:12:03 | 파이프라인 1862ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `EntryFillFlow` | 4 | 09:57:01 | 11:09:02 | actual_side='SHORT' | after='SHORT 2계약 @ 1083.86' | applied_side='SHORT' | before='SHORT 2계약 @ 1084.10' | fill_no='' | fill_price=1083.86 | fill_qty=1 | order_no='1257' | pending='ENTRY:SHORT qty=2 filled=1 order_no=1257 reason=진입 req_at=0… |

**채널** — `SYSTEM`×1659, `HEALTH`×6

**컴포넌트 상위 15** — `ChartDBG`×1442, `LiveDBG`×70, `OptionFlowChart`×41, `ChejanFlow`×14, `ChejanMatch`×14, `PendingOrder`×12, `ScalerRefresh`×9, `SessionBackfill`×6, `Health`×6, `PipePerf`×4, `CB⑤`×4, `EntryFillFlow`×4, `ExitCooldown`×4, `SHAP`×4, `출처축`×2

### `logs/20260929_SYSTEM.log` — 516.9KB · 3471행 · 최종 12:26:09

- 형식 평문 · 시각 인식 3464행 · INFO=3464, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=29344 | 행감지=30s all_threads=True
2026-09-29 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.45s | predictions=0.05s trades=0.22s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-09-29 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-09-29 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-29 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-29 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-523,foreign:-407,institution:+966} amt_mn={individual:-143138,foreign:-109949,institution:+262734}
2026-09-29 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-5045 nonarb=-1020859
2026-09-29 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-5045 nonarb=-1020859
2026-09-29 12:27:12 [INFO] SYSTEM: [OptionBook] 완료 43789ms master=cache | 먼스리 2610 n=48/48 GEX=2.31B 콜월=1100.0 풋월=1100.0 | 목위클리 2610W1 n=48/48 GEX=15.23B 콜월=1097.5 풋월=1080.0 | 월위클리 2610W1 n=48/48 GEX=0.01B 콜월=1100.0 풋월=1075.0
2026-09-29 12:27:34 [INFO] SYSTEM: [CybosRT-TICK] #70500 code=A056A raw_time=122734 parsed=12:27:34 price=1085.70 vol=1 bid1=1085.66 ask1=1085.74 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3464

**컴포넌트 상위 15** — `CybosInvestorRaw`×828, `CybosRT-TICK`×710, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `PumpGuard`×120, `System`×59, `MicroRegime`×55, `OptionChain`×44, `OptionBook`×42, `RegimeFingerprint`×38, `CybosEvent`×28

### `logs/20260929_SIGNAL.log` — 332.0KB · 2896행 · 최종 12:26:01

- 형식 평문 · 시각 인식 2896행 · WARNING=1024, INFO=1872

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-09-29 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-09-29 12:27:01 [INFO] SIGNAL: [MetaGate][LIVE] skip: blended=0.332 reduce_thr=0.465 take_thr=0.570 (grade=X min_conf=0.620 ens=0.315 meta_raw=0.357 ens_w=0.60)
2026-09-29 12:27:01 [INFO] SIGNAL: 앙상블: dir=-1 conf=31.5% grade=X micro=추세장
2026-09-29 12:27:01 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=5m tf=4.49 → TP1×0.7
2026-09-29 12:27:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.315<mc0.620)
2026-09-29 12:27:01 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=33.2% size_mult=1.00 reason=meta_skip
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 654 | 09:00:02 | 12:12:01 | 1m 'macro_sp500_chg' scale=0.1418 → floor=0.15 적용 (z-score 폭발 방지) |
| `Checklist` | 108 | 09:06:00 | 12:27:01 | 신뢰도 미달 32.8% < 41.1% → 강제 X등급 |
| `Model` | 84 | 09:00:00 | 11:43:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 72 | 09:00:00 | 11:43:00 | ts=08:59 horizon=1m age=1m max_z=-7.04(vwap_momentum) extreme=1 adj=1 |
| `ScalerRefresh` | 48 | 08:45:09 | 08:55:09 | 1m CORE 'ofi_norm' raw_std≈0(0.0279) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 48 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 6 | 09:35:00 | 11:19:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 4 | 09:07:00 | 09:51:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×2896

**컴포넌트 상위 15** — `ScalerFloor`×708, `SIGNAL`×416, `MetaGate`×224, `Ensemble`×208, `FQAdj`×207, `ZeroDiag`×189, `Checklist`×127, `ATR-Horizon`×98, `Model`×90, `ScalerRefresh`×78, `ScalerMonitor`×72, `차단`×65, `InstabilityGate`×58, `ToxicityGate`×57, `MicroRegime`×55

### `logs/20260929_LEARNING.log` — 184.9KB · 1710행 · 최종 12:26:01

- 형식 평문 · 시각 인식 1710행 · WARNING=157, INFO=1553

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00111 auc=0.410 out_max=0.3504 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00104 auc=0.387 out_max=0.1755 (기준 auc<0.53 and span<0.020, 기저율=0.1750 n=80) → 보정 미적용, raw 통과
2026-09-29 08:40:49 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.492 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-09-29 08:40:49 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00057 auc=0.540 out_max=0.3448 (n=90) → 보정 재적용
  …
2026-09-29 12:27:01 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=34.4% 예측=UP 실제=FL)
2026-09-29 12:27:01 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=37.6% 예측=UP 실제=FL)
2026-09-29 12:27:01 [INFO] LEARNING: [BiasReset] 1m uniform fallback 자동 해제 (20분 경과)
2026-09-29 12:27:01 [INFO] LEARNING: [Bias⚠] 5m 적중=30%(7/23) UP=15 DN=4 FL=4 [UP편향⚠ 65%]
2026-09-29 12:27:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=8.3%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 53 | 08:40:49 | 12:21:01 | 축퇴 감지 — span=0.00111 auc=0.410 out_max=0.3504 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 51 | 08:40:49 | 10:54:00 | 축퇴 감지 — span=0.00104 auc=0.387 out_max=0.1755 (기준 auc<0.53 and span<0.020, 기저율=0.1750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 18 | 08:40:49 | 08:40:56 | 축퇴 감지 — span=0.00040 auc=0.492 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 14 | 08:40:49 | 08:40:56 | 축퇴 감지 — span=0.00002 auc=0.383 out_max=0.3875 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 12 | 08:40:51 | 11:59:00 | 축퇴 감지 — span=0.00058 auc=0.511 out_max=0.4503 (기준 auc<0.53 and span<0.020, 기저율=0.4500 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:15m` | 8 | 08:40:53 | 08:40:58 | 축퇴 감지 — span=0.00011 auc=0.508 out_max=0.3351 (기준 auc<0.53 and span<0.020, 기저율=0.3350 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 1 | 08:40:58 | 08:40:58 | 복원한 보정기가 축퇴 상태 — span=0.00644 auc=0.495 out_max=0.3628 (n=1480) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×1710

**컴포넌트 상위 15** — `LEARNING`×663, `SGD`×207, `sigma`×195, `Bias⚠`×126, `Calibration:1m`×104, `Calibration:30m`×101, `Bias`×82, `MetaConf`×41, `Calibration:3m`×35, `OnlineLearner`×33, `ScalerWarmup`×30, `Calibration:5m`×27, `Calibration:10m`×23, `Calibration:15m`×16, `BiasReset`×12

### `logs/20260929_HEALTH.log` — 1.8KB · 13행 · 최종 12:02:00

- 형식 평문 · 시각 인식 13행 · WARNING=6, INFO=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1862ms | quality=1.00 | cache_age=44s | exceptions_10m=0
2026-09-29 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=707ms | quality=1.00 | cache_age=103s | exceptions_10m=0
2026-09-29 09:12:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2865ms | quality=1.00 | cache_age=27s | exceptions_10m=0
2026-09-29 09:13:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=777ms | quality=1.00 | cache_age=85s | exceptions_10m=0
2026-09-29 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 596ms (표본 20분)
  …
2026-09-29 10:08:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=434ms | quality=1.00 | cache_age=51s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
2026-09-29 10:44:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=412ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-29 10:45:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=442ms | quality=1.00 | cache_age=57s | exceptions_10m=0
2026-09-29 12:01:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=363ms | quality=1.00 | cache_age=183s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-29 12:02:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=339ms | quality=1.00 | cache_age=54s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 6 | 09:00:01 | 12:01:00 | level=WARNING degraded=OFF | latency=1862ms | quality=1.00 | cache_age=44s | exceptions_10m=0 |

**채널** — `HEALTH`×13

**컴포넌트 상위 15** — `Health`×12, `HealthTrend`×1

### `logs/20260929_MICRO.log` — 562.5KB · 1506행 · 최종 12:26:18

- 형식 평문 · 시각 인식 1506행 · DEBUG=1506

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1084.46/4 ask1=1084.48/1 mp={'microprice_tick': 1084.476, 'midprice_tick': 1084.47, 'depth_bias_tick': 0.2711} mlofi_tick=None queue=None
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1084.46/2 ask1=1084.48/1 mp={'microprice_tick': 1084.4733, 'midprice_tick': 1084.47, 'depth_bias_tick': 0.0657} mlofi_tick=-2.0 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1…
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1083.72/1 ask1=1084.48/1 mp={'microprice_tick': 1084.1, 'midprice_tick': 1084.1, 'depth_bias_tick': -0.0347} mlofi_tick=-1.6667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1083.72/1 ask1=1084.48/1 mp={'microprice_tick': 1084.1, 'midprice_tick': 1084.1, 'depth_bias_tick': -0.0347} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-09-29 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1084.00/2 ask1=1084.48/2 mp={'microprice_tick': 1084.24, 'midprice_tick': 1084.24, 'depth_bias_tick': -0.0042} mlofi_tick=2.95 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 1.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -0.…
  …
2026-09-29 12:26:48 [DEBUG] MICRO: [MICRO-TICK] #126100 bid1=1086.54/1 ask1=1086.60/2 mp={'microprice_tick': 1086.56, 'midprice_tick': 1086.57, 'depth_bias_tick': -0.1079} mlofi_tick=4.0167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_rat…
2026-09-29 12:27:01 [DEBUG] MICRO: [MICRO-MINUTE] #222 ts=2026-09-29 12:26:00 close=1086.04 bias=0.000727 slope=0.260228 depth_bias=-0.0114 mlofi_norm=0.003417 mlofi_pressure=1 mlofi_slope=-0.276667 queue_signal=-0.0288 queue_ma=-0.0150 queue_momentum=-0.0024 depletion=0.5000 refill=0.5000 imbalanc…
2026-09-29 12:27:03 [DEBUG] MICRO: [MICRO-TICK] #126200 bid1=1085.94/1 ask1=1086.02/2 mp={'microprice_tick': 1085.9666, 'midprice_tick': 1085.98, 'depth_bias_tick': 0.0786} mlofi_tick=-0.6667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_r…
2026-09-29 12:27:18 [DEBUG] MICRO: [MICRO-TICK] #126300 bid1=1085.88/1 ask1=1085.96/1 mp={'microprice_tick': 1085.92, 'midprice_tick': 1085.92, 'depth_bias_tick': -0.1694} mlofi_tick=3.0667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-29 12:27:32 [DEBUG] MICRO: [MICRO-TICK] #126400 bid1=1085.64/1 ask1=1085.66/1 mp={'microprice_tick': 1085.65, 'midprice_tick': 1085.65, 'depth_bias_tick': 0.0987} mlofi_tick=-2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
```

</details>

**채널** — `MICRO`×1506

**컴포넌트 상위 15** — `MICRO-TICK`×1284, `MICRO-MINUTE`×222

### `logs/20260929_DATA.log` — 230.1KB · 1043행 · 최종 12:26:09

- 형식 평문 · 시각 인식 1043행 · INFO=1043

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-29 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+15 individual=-158 institution=+161 oi=0 call_foreign=+54 put_foreign=-340 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-29 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-29 08:58:44 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+20 individual=-157 institution=+161 oi=0 call_foreign=+89 put_foreign=-343 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-29 08:58:44 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-09-29 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+177 futures(fi=+20 rt=-157 inst=+161) call(fi=+89 rt=-89) put(fi=-343 rt=+344) bias(fi=1.00 rt=-1.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-29 12:27:01 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+98 futures(fi=-423 rt=-521 inst=+979) call(fi=-303 rt=-450) put(fi=-921 rt=+852) bias(fi=0.50 rt=-1.00) program(arb=-5214 nonarb=-1015033 total=-1020247)
2026-09-29 12:27:09 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-407 individual=-523 institution=+966 oi=62653 call_foreign=-300 put_foreign=-921 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-09-29 12:27:09 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=-5045 nonarb=-1020859 total=-1025904 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-09-29 12:27:09 [INFO] DATA: [CybosInvestor] fetch#208 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-09-29 12:27:09 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+116 futures(fi=-407 rt=-523 inst=+966) call(fi=-300 rt=-449) put(fi=-921 rt=+854) bias(fi=0.51 rt=-1.00) program(arb=-5045 nonarb=-1020859 total=-1025904)
```

</details>

**채널** — `DATA`×1043

**컴포넌트 상위 15** — `CybosInvestor`×622, `DivergencePanel`×414, `OptionFlow`×7

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) — **엔진** | 2 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 65 |
| 사이저 호출(`[Sizer]`) | 5 |

### 포지션 2건 · 승 2 (100%) · 합계 +2.52pt (+83,382원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:57:00 | 엔진 | SHORT | 2 | 3m | 2 | +0.76 | +16,734 | 하드스톱(틱) |
| 11:09:02 | 엔진 | LONG | 2 | 3m | 2 | +1.76 | +66,648 | 하드스톱 |

**청산 레그 4행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:57:16 | 부분 | 1 | +0.80 | +29,367 | TP1 부분청산 33% |
| 09:58:35 | 전량 | 1 | -0.04 | -12,633 | 하드스톱(틱) |
| 11:12:37 | 부분 | 1 | +0.59 | +18,824 | TP1 부분청산 33% |
| 11:13:00 | 전량 | 1 | +1.17 | +47,824 | 하드스톱 |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱(틱)`×1, `하드스톱`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 2/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +83,382 = 포지션합 +83,382 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:57:00 | SHORT | 2 | 1084.1 | 3m | mean-revert |
| 11:09:02 | LONG | 2 | 1088.26 | 3m | neutral |

계약수 분포 — 2계약×2

등급 분포 — `A급(원시C)`×2

**진입한 건들의 체크리스트 미통과 항목** — `fore`×2, `chas`×1, `ofi`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×1, **3계약**×4

실제 진입 계약수 — **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×5

### 차단 사유 65건 · 24종

| 건수 | 사유 |
|---|---|
| 32 | 등급X — 미통과 항목: 2_confidence |
| 4 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 3 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign |
| 2 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.5pt > ATR×5.0=9.8pt (시가=1082.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.5pt > ATR×5.0=8.8pt (시가=1082.04 반등위험) |
| 1 | 청산 후 쿨다운 — 154초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 94초 후 재진입 가능 |
| 1 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 1 | JointGateBlock — meta=0.52 tox=0.70 joint=0.361 < 0.50 |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 10_chase |
| 1 | 청산 후 쿨다운 — 0초 후 재진입 가능 |
| 1 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.89pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×32, `3_vwap`×14, `6_foreign`×14, `4_cvd`×10, `7_prev_bar`×9, `5_ofi`×8, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 8건 · 최대 4375ms · 5초 초과 0건

상위 — 4375ms, 4281ms, 4015ms, 3500ms, 2453ms, 2218ms, 2093ms, 2047ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260929_WARN.log`
```
--- [CB] ×1(표본)
09:58:35 2026-09-29 09:58:35 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×5(표본)
09:58:35 2026-09-29 09:58:35 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:01:35)
09:58:35 2026-09-29 09:58:35 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:01:35)
10:07:00 2026-09-29 10:07:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=356ms | quality=1.00 | cache_age=185s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
11:13:00 2026-09-29 11:13:00 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:15:00)
--- [SHAP] 슬로우 ×4(표본)
11:43:02 2026-09-29 11:43:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1434ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:00:02 2026-09-29 12:00:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1372ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:08:02 2026-09-29 12:08:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 932ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:22:01 2026-09-29 12:22:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1401ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-29 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4015ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4015 band=INFO since_pipe_s=NA
09:00:04 2026-09-29 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4281 band=INFO since_pipe_s=0.2
09:05:12 2026-09-29 09:05:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=9 watchdog_alerted=[] | [MainStall] stall_ms=3500 band=INFO since_pipe_s=10.7
09:12:04 2026-09-29 09:12:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4375 band=INFO since_pipe_s=0.2
```

### `logs/20260929_SYSTEM.log`
```
--- ConstOut ×6(표본)
09:35:00 2026-09-29 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5252) | 앙상블 제외는 유지
09:44:00 2026-09-29 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4633) | 앙상블 제외는 유지
09:54:00 2026-09-29 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4922) | 앙상블 제외는 유지
11:03:01 2026-09-29 11:03:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3710) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-09-29 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-09-29 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-09-29 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-09-29 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
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
--- [ExitCooldown] ×2(표본)
10:07:00 2026-09-29 10:07:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=356ms | quality=1.00 | cache_age=185s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
10:08:00 2026-09-29 10:08:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=434ms | quality=1.00 | cache_age=51s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260929_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 22 | 09:57:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,943,671) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |

- 이 로그 생존구간: 08:40 ~ 11:53

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260929_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 18 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 166 | 09:54:00 [WARNING] paintEvent slow 143.8ms | size=1955x1096 candles=36 grid=42.7 spans=0.0 candles=2.0 dir=0.2 regime=5.5 marker… |
| 12:00 | 장중 중간점 | 103 | 11:54:01 [WARNING] paintEvent slow 151.1ms | size=1955x1096 candles=36 grid=47.7 spans=13.8 candles=2.3 dir=0.2 regime=10.0 mark… |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260929_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 93 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=29344 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 137 | 08:49:02 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 203 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 290 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 177 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260929_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:09 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0279) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 133 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0290) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 207 | 08:55:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0417) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 154 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 119 | 11:54:00 [WARNING] 신뢰도 미달 40.4% < 44.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:27

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
| **오늘 20260929** | **12:27** | 로그 본문 |

- 델타 **-200분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-26 (MW0601 631차 — 휴장일 점검: 부팅 직후 DB 초기화가 3분 넘게 안 끝났다)
## 2026-09-26 (MW0601 632차 — 장중 재점검, 10:44 절로부터 27분 뒤: 무변화 확인 + 수집기 자가점검 사례)
## 2026-09-26 (MW0601 631차 후속 — 장후: 휴장일 상황 동결 확인 + F-4 범위 확장)
## 2026-09-28 (MW0601 633차 — 장전 점검)
## 2026-09-28 (MW0601 634차 — 장중 점검)
## 2026-09-28 (MW0601 635차 — 장후 점검)
## 2026-09-28 (MW0601 636차 — 장후 자동조치: 고도화 방안 2·3·4 구현 + DB pruning 「삭제 성공」 판단 정정)
## 2026-09-29 (MW0601 637차 — 장전 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
시계는 UTC라 겉보기 날짜가 9/28로 보였으나 UTC 23:58(9/28)=KST 08:58(9/29)로 환산해 정확한 대상일(2026-09-29 장전)을 확정하고 진행했다. 모든 git 명령에 `--no-optional-locks` 부착, 병행 세션 없음 확인(당일 커밋 0건, docs/정기점검/매일점검 최신 산출물이 이 세션 이전 것뿐), 세션 종료 시점 `.git/index.lock` 없음(`git_lock_guard.py --check` OK).

**증상**: (1) `logs/crash_fault.log`에서 오늘(09-29) 부팅 구간(08:40:44~08:41:39, 정규장 개시 전)에 `Windows fatal exception: access violation` 3건 확인. 스택은 `dashboard/main_dashboard.py` 위젯 생성 스레드 + `collection/macro/macro_fetcher.py:99 _loop` 대기 스레드 조합, 09-17(601차) 최초 발견 사례와 동일 계열. 09:00 정규장 개시 후 재현 0건. (2) 같은 파일을 09-28(PID 19608) 구간으로 소급 확인한 결과 4건 추가 확인 — 그런데 `docs/정기점검/매일점검/MW0601-20260928-점검리포트.md` 전문 검색 결과 "access violation" 언급 0건, 즉 어제 장전 점검이 이 재현을 놓쳤다. (3) 원인: `scripts/collect_evidence.py` §1 당일 파일 인벤토리는 파일명의 날짜 토큰으로 "오늘 파일"을 가리므로 `crash_fault.log`(날짜 토큰 없는 누적 파일)는 인벤토리·§11 자동 적신호 어디에도 안 걸린다. `crash_fault_events()`(§9)가 이 파일을 열람은 하지만 "정상종료 기록 여부" 판정용이지 "access violation 건수 집계"용이 아니다. (4) O-p1(`SessionStateDrop`) — 0928 장후가 예정해 둔 대로 오늘 장전이 거래일 전환(0928→0929) 재현 여부를 최종 확인 — `data/session_state.json`에 `p8_last_success_date`·`eod_retrain_ok_date` 키 소실 재현 확정(`[SessionStateDrop]` 08:41:09). 어제 EOD 자체(`data/eod_retrain_done_20260928.txt`, horizons_replaced=6/6)는 정상 종료 재확인 — 계측 4원칙② 사례 그대로, 실질 영향 없음.

**결정**:
1. (신규 등록, P1) access violation(1-1)은 신규 조사 아님 — 기존 606-4("09-17 access violation 원인 조사 우선순위 결정 — 여전히 사용자 몫")에 09-28(4건)·09-29(3건) 두 관측일을 추가해 근거를 보강한다. 새 Fix 등록하지 않음(함정①).
2. (신규 등록, P2) `crash_fault.log`가 수집기 §1/§11에서 구조적으로 빠지는 문제를 F-1로 신규 등록(아래 NEXT_TODO 참조) — `crash_fault_events()` 호출부 근처에 "오늘 [START] 구간 내 access violation 건수" 집계를 추가하는 안. 점검 도구 자체 개선이라 사용자 승인 없이 다음 세션에서 구현 가능.
3. O-p1(`SessionStateDrop`) — 종결(예정된 최종 판정 완료, 재현 확정). 근본수정 606-2는 계속 사용자 승인 대기, 새 Fix 등록하지 않음.
4. 문서 제목 손상(633-1/634-2)·`opt_chain_pcr` 미확인(633-4)·joblib 1.1.0 vs 문서 1.1.1 불일치 — 전부 기존 항목 지속 확인만, 신규 등록 없음(함정①).

**Why**: 함정①(판정≠결정) 방지 — 기존 606-4·606-2·633-1·633-4·joblib 항목을 grep으로 먼저 확인한 뒤 신규가 아님을 검증하고 지속으로만 기록했다. crash_fault.log 인벤토리 누락은 grep으로 기존 등록 여부를 확인했으나 걸리는 기록이 없어 신규로 등록했다(계측 4원칙④ 폴백 가시화 — "기록이 없으면 이상이 없다"가 아니라 "기록할 경로 자체가 없었다"는 것을 명시).

**How to apply**: F-1(crash_fault.log 인벤토리 편입)은 다음 세션(장중/장후 또는 별도)에서 `scripts/collect_evidence.py`에 구현. 606-4 우선순위 결정은 사용자 몫 — 이번 세션이 추가한 09-28·09-29 두 관측일 근거를 참고해 판단할 수 있다.

**검증**: F-1 구현 후 09-29 재실행 시 access violation 3건, 09-28 재실행 시 4건이 각각 집계되는지 확인. 606-4는 사용자 결정 이후 조사 착수 시 별도 검증 계획.

⚠ **코드 변경 없음(장전 점검 세션 — 라이브 프로세스 실행 중, 08:57 KST경 예약 실행).** 라이브 DB 스캔 없음(08:45 이후 금지 구간과 무관하게 애초에 로그·설정·git만 사용).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-26 (MW0601 631차 — 휴장일 점검)
## 2026-09-26 (MW0601 632차 — 장중 재점검)
## 2026-09-26 (MW0601 631차 후속 — 장후)
## 2026-09-28 (MW0601 633차 — 장전 점검)
## 2026-09-28 (MW0601 634차 — 장중 점검)
## 2026-09-28 (MW0601 635차 — 장후 점검)
## 2026-09-28 (MW0601 636차 — 장후 자동조치)
## 2026-09-29 (MW0601 637차 — 장전 점검)
```

미완료 체크박스 **2874건** (끝에서 30건)
```
- [ ] **631-10 (F-1a, 1순위)** `_migrate_predictions_db()` 역채움 UPDATE 앞에 부분 인덱스 `idx_pred_prob_null`(WHERE 세 확률 IS NULL) — 복사본 실측 UPDATE 0.6s→0.0000s, 생성 1회 6.3s. 631-2(user_version 마커안)를 대체.
- [ ] **631-11 (F-5)** 초기화 중 런처 콘솔에 `[BOOT] DB 초기화 중…` 진행 표시 — 0926 사용자가 "안 올라온다"고 판단해 수동 종료.
- [ ] **631-12 (F-6/F-7/F-8)** 자동로그인: 재시도 직전 `_is_connected()` 재확인 · kill 실패 가시화 · diag 줄별 시각. F-6은 모의 리허설 1회 후.
- [ ] **631-13 (F-3/F-3b)** 런처 STEP 4: autologin 락 대기 + IsConnect 연속 10초 유지 판정.
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
`..\fuoption\scripts\git_lock_guard.py`)에 복사 — 자동조치 세션의 덮어쓰기가 권한 거부됨. 복사 전까지 `test_483::test_sibling_copy_matches_canonical[fuoption]` FAIL. fuoption 쪽 커밋도 필요.
- [ ] **636-2 (승인 대기, P2)** `prune_raw_data_db()` 실제 삭제 수정 — DELETE 루프 뒤 `conn.commit()`, `PRAGMA wal_checkpoint(PASSIVE)`는 별도 try(실패해도 삭제는 유지, 로그 `완료(체크포인트 보류)`). 현재는 자기 트랜잭션 안 체크포인트 → `database table is locked` → **전량 롤백, 도입 이래 삭제 0행**(636차 재현). 승인 전 확인: ① 52주 초과분 실제 행수·기간(09-28 시도 22,860행) ② 그 구간을 읽는 분석 스크립트 유무(ATR 월별표 2026-03~ 등은 52주 이내) ③ 첫 실행 뒤 raw_data.db 크기(VACUUM 없으면 파일은 안 줄어든다). 회귀 가드 `test_636::test_prune_return_equals_rows_actually_removed`는 수정 후에도 그대로 통과해야 한다. 기존 항목 「DB pruning 6주 연속 실패」·635-3 을 이 항목이 대체한다.
- [ ] **636-3 (C — 사용자 지시 필요)** 고도화 방안 1: `[PreRetrain]` 판정에서 마커 파일(`data/eod_retrain_done_{날짜}.txt`)을 1차 경로로 격상. main.py 재학습 스킵 순서 변경이라 자동조치 범위 밖. 606-2 근본수정과 함께 판단.
- [x] **634-1** 종결 — `git_lock_guard.py` 이름변경 우회 구현(`_sideline`, `.git` 최상위 파일 한정 — ref 락은 가짜 브랜치가 되므로 제외).
- [x] **633-3** 종결 — `scripts/md_title_guard.py` 신설(경고 전용, rc=2). 실물(633-1 파일)에서 탐지 확인.
- [x] **635-3** 종결(판단 정정) — 로그 문구 분리가 아니라 **롤백 사실 기록**으로 구현. 「삭제 성공」 전제가 틀렸다(재현). 실삭제는 636-2.
- [ ] **636-4 (정리)** DECISION_LOG 636차 항목은 작업본에 append 만 됐고 **미커밋** — 같은 파일에 다른 세션(신동 R3 딥다이브)의 미커밋 변경(전 파일 줄바꿈 변경 + 중간 삽입)이 있어 골라 커밋할 수 없었다. 그 세션 커밋 때 함께 들어가면 된다.
- [ ] **636-5 (정리)** `md_title_guard.py`를 SKILL.md 커밋 전 프리플라이트(`git_lock_guard.py --check` 옆)에 한 줄 추가할지 결정.

## 2026-09-29 (MW0601 637차 — 장전 점검)

- [ ] **637-1 (P1)** `dev_memory/NEXT_TODO.md` 606-4(09-17 access violation 원인 조사 우선순위 결정)에 09-28(4건)·09-29(3건) 재현을 근거로 추가 — 사용자가 우선순위를 정할 때 참고. 전부 부팅 구간(정규장 개시 전) 한정, 정규장 개시 후 재현 0건. 새 조사 착수는 사용자 결정 대기, 이 항목은 606-4에 흡수(중복 등록 아님).
- [ ] **637-2 (P2, 신규)** `scripts/collect_evidence.py` §1 당일 파일 인벤토리·§11 자동 적신호가 `logs/crash_fault.log`(날짜 토큰 없는 누적 로그)를 구조적으로 못 본다 — `crash_fault_events()`(§9)는 "정상종료 기록" 판정용이지 "access violation 건수 집계"용이 아님. 09-28 access violation 4건이 0928 장전 리포트에서 완전히 누락된 것으로 실증됨(리포트 전문 검색 "access violation" 0건). 제안: `crash_fault_events()` 호출부 근처에 "오늘 `[START]` 구간 내 `Windows fatal exception` 건수" 집계를 §5 또는 §11에 추가. 점검 도구 자체 개선이라 사용자 승인 없이 구현 가능. 근거: 0929 장전 이상점 1-2.
- [x] **O-p1 (SessionStateDrop) 최종 판정 완료** — 09-28→09-29 거래일 전환 재현 확정(`[SessionStateDrop]` 08:41:09, `session_state.json` 두 키 부재). 어제(0928) EOD 자체는 정상 종료 재확인(`eod_retrain_done_20260928.txt`, 6/6). 근본수정 606-2는 계속 사용자 승인 대기. 신규 Fix 없음(함정①).
- [ ] **633-1 (P2)** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 0929 장전에도 미확인·미커밋 상태 지속(3번째 날).

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

### `data/heartbeat_MW0601_20260929.json` — 244B · 09-29 12:26:16
```json
{
 "pid": 29344,
 "written_at": "2026-09-29T12:27:16",
 "beat_epoch": 1790652434.3419552,
 "beat_age_sec": 2.2,
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

- 파일 최종 기록: **09-29 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-29)과 일치 |
|---|---|---|
| `date` | 2026-09-29 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:26** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 222 |
| `session_bars` 당일 행수 | 222 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 162봉** (`session_bars` 에도 없음): 12:27, 12:28, 12:29, 12:30, 12:31, 12:32, 12:33, 12:34, 12:35, 12:36, 12:37, 12:38, 12:39, 12:40, 12:41, 12:42, 12:43, 12:44, 12:45, 12:46

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
| 29344 | 08:40:44 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 175개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260929-점검리포트.md` | 31.1KB | 09-29 09:11 |
| `docs/정기점검/매일점검/evidence_MW0601-20260929_pre.md` | 59.0KB | 09-29 09:00 |
| `docs/정기점검/매일점검/MW0601-20260928-점검리포트.md` | 81.3KB | 09-28 17:47 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_post.md` | 84.8KB | 09-28 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_intra.md` | 74.0KB | 09-28 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md` | 56.8KB | 09-28 09:00 |
| `docs/정기점검/매일점검/MW0601-20260926-점검리포트.md` | 67.5KB | 09-26 16:43 |
| `docs/정기점검/매일점검/evidence_MW0601-20260926_intra_1107.md` | 41.3KB | 09-26 11:07 |

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

1. `logs/20260929_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
2. `logs/20260929_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
3. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
4. `logs/20260929_SYSTEM.log`: **ConstOut** 6건(표본)
5. `logs/20260929_SIGNAL.log`: **WeightCollapse** 8건(표본)
6. `logs/20260929_SIGNAL.log`: **ConstOut** 8건(표본)
7. `logs/20260929_LEARNING.log`: **축퇴** 8건(표본)
8. 미커밋 변경 10건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260929*.log` (Windows) / `grep 강제청산 logs/*20260929*.log`*