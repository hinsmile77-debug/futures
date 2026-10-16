# 미륵이 증거 다이제스트 — 2026-10-02 / INTRA

- 생성 2026-10-02 12:27:28 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01qjog8y1hztc1qggrhrapve/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261002` · `2026-10-02` · `261002` · `1002`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **18개** 파일 · 18개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261002.log` | 269B | 10-02 07:21 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261002.log` | 125B | 10-02 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261002.log` | 140B | 10-02 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261002.json` | 244B | 10-02 12:27 |
| `launcher_{DATE}_084001_17771.log` | 1 | `logs/Mireuk_batch/launcher_20261002_084001_17771.log` | 1.2MB | 10-02 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261002.log` | 7.4KB | 10-02 12:20 |
| `retrain_intraday_20260707_{DATE}00.log` | 1 | `logs/retrain_intraday_20260707_100200.log` | 4.6KB | 07-07 10:02 |
| `{DATE}_DATA.log` | 1 | `logs/20261002_DATA.log` | 231.5KB | 10-02 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261002_DEBUG.log` | 130.9KB | 10-02 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261002_HEALTH.log` | 1.8KB | 10-02 12:21 |
| `{DATE}_HOGA.log` | 1 | `logs/20261002_HOGA.log` | 29.3MB | 10-02 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261002_LEARNING.log` | 177.0KB | 10-02 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20261002_MICRO.log` | 552.8KB | 10-02 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20261002_PROBE.log` | 55.7KB | 10-02 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261002_SIGNAL.log` | 382.9KB | 10-02 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261002_SYSTEM.log` | 467.4KB | 10-02 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20261002_TRADE.log` | 1.1KB | 10-02 11:11 |
| `{DATE}_WARN.log` | 1 | `logs/20261002_WARN.log` | 291.0KB | 10-02 12:26 |

## 2. 코드·커밋 상태

- HEAD `1e56ace` · 브랜치 `v9-dev` · 미커밋 23건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 6회 · 타임아웃 1 · 실패 0 · 락 생성 구간 1 · 최장 25.0초(`git diff --numstat`)
    - `git diff --numstat` → timeout · 25.0초 · 락 없음→있음 · 🔴 **이 호출 구간에 락이 생겼다**(동시 발생 — 인과 미확정)
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
?? docs/정기점검/매일점검/MW0601-20261002-점검리포트.md
?? docs/정기점검/매일점검/_tmp_append_addendum_20261001.md
?? docs/정기점검/매일점검/_tmp_append_intra_20261001.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20260930_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261001_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261002_pre.md
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

_본문 미열람(설정): `20261002_HOGA.log` 29.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `20261002_DATA.log`, `20261002_PROBE.log`, `launcher_20261002_084001_17771.log`, `20261002_DEBUG.log`, `mainstall_traceback_20261002.log`, `claude_resume_20261002.log`, `freeze_sentinel_20261002.log`, `force_flat_guard_20261002.log`_

### `logs/20261002_TRADE.log` — 1.1KB · 8행 · 최종 11:11:00

- 형식 평문 · 시각 인식 8행 · INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-02 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-02 10:38:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-02 10:38:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-02 10:41:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-10-02 10:38:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-02 10:41:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-02 10:41:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-02 11:11:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-02 11:11:00 [INFO] TRADE: [모드필터 차단] LONG->LONG 2계약 C급 (모드=hybrid, 허용=['A', 'B'])
```

</details>

**채널** — `TRADE`×8

**컴포넌트 상위 15** — `Sizer`×3, `JointGateBlock 차단`×2, `Position`×1, `ProfitGuard`×1, `모드필터 차단`×1

### `logs/20261002_WARN.log` — 291.0KB · 1324행 · 최종 12:26:08

- 형식 평문 · 시각 인식 1324행 · WARNING=1324

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-02 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-10-02 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-10-02 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-02 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-02 12:21:00 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2769ms quality=1.00 cache=0s exc10m=0) | cause=S5(877ms)
2026-10-02 12:24:32 [WARNING] SYSTEM: [LiveDBG] ChallengerPanel.refresh slow 234ms
2026-10-02 12:25:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2516 band=INFO since_pipe_s=0.0
2026-10-02 12:26:08 [WARNING] SYSTEM: [OptionFlowChart] 그리기 107.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 922x1001
2026-10-02 12:28:09 [WARNING] SYSTEM: [LiveDBG] _fetch_investor_data 지연 527ms — 메인 스레드 527ms 점유 (live 중단 원인 후보)
```

</details>

**WARNING — 태그 15종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1189 | 09:00:36 | 12:04:46 | paintEvent slow 82.6ms | size=1955x1124 candles=16 grid=47.1 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=33.5 cross=0.0 | slow_cnt=1 total_cnt=4 overlay_cnt=2 |
| `LiveDBG` | 48 | 08:41:08 | 12:28:09 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 39 | 08:41:18 | 12:26:08 | 그리기 75.9ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 861x1001 |
| `ScalerRefresh` | 9 | 09:24:00 | 12:20:02 | 5분 누적 수익률 +0.426% (임계 ±0.242%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-10-01 10:02:00 cols=['open'] existing_source=rt |
| `Health` | 6 | 09:00:01 | 12:20:03 | level=WARNING degraded=OFF | latency=1749ms | quality=1.00 | cache_age=50s | exceptions_10m=0 |
| `CB③-P4` | 6 | 10:16:00 | 10:35:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=10.0%) |
| `PipePerf` | 4 | 09:00:01 | 12:20:03 | total=1749ms | S0=4ms S1=15ms S2=0ms S3=0ms S4=139ms S5=1150ms S6=376ms S7=56ms S8=9ms |
| `CB⑤` | 4 | 09:00:01 | 12:20:04 | 파이프라인 1749ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `SHAP` | 3 | 11:37:01 | 12:02:01 | 슬로우 감지 934ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:08 | 08:41:08 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-10-01 → 2026-10-02)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |

**채널** — `SYSTEM`×1318, `HEALTH`×6

**컴포넌트 상위 15** — `ChartDBG`×1189, `LiveDBG`×48, `OptionFlowChart`×39, `ScalerRefresh`×9, `SessionBackfill`×6, `Health`×6, `CB③-P4`×6, `PipePerf`×4, `CB⑤`×4, `SHAP`×3, `출처축`×2, `SessionStateDrop`×2, `Canary`×2, `MainStallTrace`×2, `HealthPolicy`×2

### `logs/20261002_SYSTEM.log` — 467.4KB · 3229행 · 최종 12:27:23

- 형식 평문 · 시각 인식 3222행 · INFO=3222, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:44 [INFO] SYSTEM: [FaultHandler] 로테이션 — 9.2MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-10-02 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18204 | 행감지=30s all_threads=True
2026-10-02 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.49s | predictions=0.08s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.12s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-02 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-02 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
  …
2026-10-02 12:28:03 [INFO] SYSTEM: [CybosRT-TICK] #68200 code=A056A raw_time=122803 parsed=12:28:03 price=1108.46 vol=1 bid1=1108.44 ask1=1108.50 flag=50 side=SELL anchor=0/1
2026-10-02 12:28:08 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-375,foreign:+1929,institution:-1495} amt_mn={individual:-103319,foreign:+536830,institution:-417111}
2026-10-02 12:28:08 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-375,foreign:+1929,institution:-1495} amt_mn={individual:-103319,foreign:+536830,institution:-417111}
2026-10-02 12:28:08 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+143735 nonarb=-240008
2026-10-02 12:28:08 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+143735 nonarb=-240008
```

</details>

**채널** — `SYSTEM`×3222

**컴포넌트 상위 15** — `CybosInvestorRaw`×832, `CybosRT-TICK`×687, `CybosRT-ROLLOVER`×223, `BAR-CLOSE`×223, `CVD-ANCHOR`×223, `TickUI`×222, `S6Detail`×209, `PipePerf`×209, `System`×59, `MicroRegime`×48, `OptionChain`×44, `OptionBook`×42, `RegimeFingerprint`×38, `IntradayRegime`×22, `CybosSub`×21

### `logs/20261002_SIGNAL.log` — 382.9KB · 3317행 · 최종 12:27:00

- 형식 평문 · 시각 인식 3317행 · WARNING=1503, INFO=1814

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-10-02 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-10-02 12:28:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-10-02 12:28:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=None)
2026-10-02 12:28:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
2026-10-02 12:28:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=35.2% grade=X micro=추세장
2026-10-02 12:28:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.352<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1044 | 09:00:02 | 12:20:07 | 1m 'macro_vix' scale=0.0122 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 156 | 09:00:00 | 12:12:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 138 | 09:00:00 | 12:19:00 | ts=08:59 horizon=1m age=1m max_z=-14.76(retail_futures_net) extreme=1 adj=1 |
| `Checklist` | 90 | 09:06:01 | 12:25:00 | 신뢰도 미달 33.3% < 41.1% → 강제 X등급 |
| `WeightCollapse` | 46 | 09:07:00 | 12:28:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 18 | 08:45:08 | 08:45:08 | 1m CORE 'cvd_divergence' raw_std≈0(0.0159) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 7 | 09:35:00 | 12:14:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 4 | 09:07:00 | 09:22:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×3317

**컴포넌트 상위 15** — `ScalerFloor`×1104, `SIGNAL`×418, `MetaGate`×239, `FQAdj`×208, `Ensemble`×208, `ZeroDiag`×200, `Model`×162, `ScalerMonitor`×138, `Checklist`×97, `ATR-Horizon`×80, `ToxicityGate`×67, `차단`×56, `ScalerRefresh`×49, `MicroRegime`×48, `WeightCollapse`×46

### `logs/20261002_LEARNING.log` — 177.0KB · 1664행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1664행 · WARNING=141, INFO=1523

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3127 < conf_floor=0.3300 (span=0.00029 auc=0.539 out_max=0.3127, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.514 out_max=0.3295 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
2026-10-02 08:40:50 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00008 auc=0.532 out_max=0.3238 (n=105) → 보정 재적용
2026-10-02 08:40:50 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.1379 < conf_floor=0.3300 (span=0.00091 auc=0.675 out_max=0.1379, 기저율=0.1375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-02 12:28:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0491% buf_n=20 nonzero=20 prev_p=1108.14 cur_p=1108.40
2026-10-02 12:28:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=45.4% 예측=FL 실제=UP)
2026-10-02 12:28:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=45.8% 예측=UP 실제=FL)
2026-10-02 12:28:00 [INFO] LEARNING: [Bias⚠] 1m 적중=48%(11/23) UP=3 DN=0 FL=20 [FL편향⚠ 87%]
2026-10-02 12:28:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=25.0%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 50 | 08:40:50 | 11:51:00 | 하한 도달불가 — out_max=0.3127 < conf_floor=0.3300 (span=0.00029 auc=0.539 out_max=0.3127, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:30m` | 44 | 08:40:50 | 10:34:00 | 하한 도달불가 — out_max=0.1379 < conf_floor=0.3300 (span=0.00091 auc=0.675 out_max=0.1379, 기저율=0.1375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 20 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00076 auc=0.456 out_max=0.3253 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 11 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00039 auc=0.444 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 10 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00009 auc=0.482 out_max=0.2500 (기준 auc<0.53 and span<0.020, 기저율=0.2500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 4 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00312 auc=0.353 out_max=0.3140 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:59 | 08:40:59 | 복원한 보정기가 축퇴 상태 — span=0.00765 auc=0.512 out_max=0.3385 (n=2368) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 12:20:00 | 12:20:00 | total=311ms raw_fetch=10ms pred_select=36ms pred_update=60ms pred_insert=1ms verified=5 |

**채널** — `LEARNING`×1664

**컴포넌트 상위 15** — `LEARNING`×669, `SGD`×208, `sigma`×196, `Bias⚠`×107, `Calibration:1m`×98, `Calibration:30m`×88, `Bias`×80, `MetaConf`×41, `Calibration:3m`×38, `OnlineLearner`×33, `ScalerWarmup`×31, `Calibration:5m`×21, `Calibration:10m`×18, `BiasReset`×12, `Calibration:15m`×7

### `logs/20261002_HEALTH.log` — 1.8KB · 13행 · 최종 12:21:00

- 형식 평문 · 시각 인식 13행 · WARNING=6, INFO=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1749ms | quality=1.00 | cache_age=50s | exceptions_10m=0
2026-10-02 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=504ms | quality=1.00 | cache_age=109s | exceptions_10m=0
2026-10-02 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 389ms (표본 20분)
2026-10-02 09:39:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=395ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-10-02 09:40:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=325ms | quality=1.00 | cache_age=57s | exceptions_10m=0
  …
2026-10-02 11:18:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=319ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-10-02 12:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=496ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-02 12:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=476ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-02 12:20:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2769ms | quality=1.00 | cache_age=111s | exceptions_10m=0
2026-10-02 12:21:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=368ms | quality=1.00 | cache_age=168s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 6 | 09:00:01 | 12:20:03 | level=WARNING degraded=OFF | latency=1749ms | quality=1.00 | cache_age=50s | exceptions_10m=0 |

**채널** — `HEALTH`×13

**컴포넌트 상위 15** — `Health`×12, `HealthTrend`×1

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

### `logs/20261002_MICRO.log` — 552.8KB · 1482행 · 최종 12:27:16

- 형식 평문 · 시각 인식 1482행 · DEBUG=1482

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-02 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1099.96/3 ask1=1100.28/4 mp={'microprice_tick': 1100.0971, 'midprice_tick': 1100.12, 'depth_bias_tick': -0.0088} mlofi_tick=None queue=None
2026-10-02 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1099.96/3 ask1=1100.28/4 mp={'microprice_tick': 1100.0971, 'midprice_tick': 1100.12, 'depth_bias_tick': 0.0161} mlofi_tick=-1.9833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-10-02 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1099.76/5 ask1=1099.96/1 mp={'microprice_tick': 1099.9266, 'midprice_tick': 1099.86, 'depth_bias_tick': 0.1361} mlofi_tick=-13.3667 queue={'depletion_bid': 0.0, 'depletion_ask': 3.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-10-02 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1099.90/5 ask1=1099.96/1 mp={'microprice_tick': 1099.95, 'midprice_tick': 1099.93, 'depth_bias_tick': 0.374} mlofi_tick=5.8 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-10-02 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1099.76/5 ask1=1099.96/1 mp={'microprice_tick': 1099.9266, 'midprice_tick': 1099.86, 'depth_bias_tick': 0.2859} mlofi_tick=-8.8167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
  …
2026-10-02 12:27:57 [DEBUG] MICRO: [MICRO-TICK] #123600 bid1=1108.30/1 ask1=1108.36/2 mp={'microprice_tick': 1108.32, 'midprice_tick': 1108.33, 'depth_bias_tick': -0.3004} mlofi_tick=-5.45 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-10-02 12:28:00 [DEBUG] MICRO: [MICRO-MINUTE] #223 ts=2026-10-02 12:27:00 close=1108.40 bias=0.000519 slope=-0.165806 depth_bias=0.0639 mlofi_norm=-0.014609 mlofi_pressure=-1 mlofi_slope=-63.001667 queue_signal=0.0220 queue_ma=-0.0516 queue_momentum=0.0319 depletion=0.5010 refill=0.4990 imbalan…
2026-10-02 12:28:12 [DEBUG] MICRO: [MICRO-TICK] #123700 bid1=1108.64/1 ask1=1108.68/2 mp={'microprice_tick': 1108.6534, 'midprice_tick': 1108.66, 'depth_bias_tick': -0.2818} mlofi_tick=6.85 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_rat…
2026-10-02 12:28:28 [DEBUG] MICRO: [MICRO-TICK] #123800 bid1=1108.40/1 ask1=1108.46/2 mp={'microprice_tick': 1108.42, 'midprice_tick': 1108.43, 'depth_bias_tick': -0.1095} mlofi_tick=1.9 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-10-02 12:28:44 [DEBUG] MICRO: [MICRO-TICK] #123900 bid1=1108.30/2 ask1=1108.34/1 mp={'microprice_tick': 1108.3267, 'midprice_tick': 1108.32, 'depth_bias_tick': 0.0591} mlofi_tick=-1.9833 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
```

</details>

**채널** — `MICRO`×1482

**컴포넌트 상위 15** — `MICRO-TICK`×1259, `MICRO-MINUTE`×223

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 56 |
| 사이저 호출(`[Sizer]`) | 3 |

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×3

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×3

### 차단 사유 56건 · 26종

| 건수 | 사유 |
|---|---|
| 26 | 등급X — 미통과 항목: 2_confidence |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | ATR 0.89pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.7pt > ATR×5.0=6.9pt (시가=1098.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.2pt > ATR×5.0=7.1pt (시가=1098.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=6.0pt (시가=1098.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.0pt > ATR×5.0=6.1pt (시가=1098.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.2pt > ATR×5.0=6.4pt (시가=1098.52 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 6.8pt > ATR×5.0=6.6pt (시가=1098.52 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×26, `3_vwap`×7, `6_foreign`×7, `5_ofi`×4, `4_cvd`×3, `7_prev_bar`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 10건 · 최대 12016ms · 5초 초과 2건

상위 — 12016ms, 5250ms, 4000ms, 3907ms, 3656ms, 2704ms, 2516ms, 2391ms

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
--- [SHAP] 슬로우 ×3(표본)
11:37:01 2026-10-02 11:37:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 934ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:45:01 2026-10-02 11:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 946ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:02:01 2026-10-02 12:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 961ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-02 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4000ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4000 band=INFO since_pipe_s=NA
09:00:03 2026-10-02 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3907ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3907 band=INFO since_pipe_s=0.1
09:00:36 2026-10-02 09:00:36 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=29 watchdog_alerted=[] | [MainStall] stall_ms=5250 band=WARN since_pipe_s=32.8
09:02:10 2026-10-02 09:02:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=9 watchdog_alerted=[] | [MainStall] stall_ms=2391 band=INFO since_pipe_s=9.9
```

### `logs/20261002_SYSTEM.log`
```
--- ConstOut ×7(표본)
09:35:00 2026-10-02 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4548) | 앙상블 제외는 유지
09:44:01 2026-10-02 09:44:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4298) | 앙상블 제외는 유지
09:54:00 2026-10-02 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3884) | 앙상블 제외는 유지
11:14:00 2026-10-02 11:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3953) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-10-02 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-02 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-10-02 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-10-02 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20261002_SIGNAL.log`
```
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

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261002_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 11:11

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261002_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 21 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 33 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 42 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 91 | 09:54:00 [WARNING] paintEvent slow 98.7ms | size=1955x1124 candles=70 grid=37.6 spans=0.0 candles=2.8 dir=0.3 regime=3.9 markers… |
| 12:00 | 장중 중간점 | 112 | 11:54:01 [WARNING] paintEvent slow 96.3ms | size=1955x1124 candles=190 grid=28.8 spans=2.0 candles=7.7 dir=0.7 regime=4.5 marker… |

- 이 로그 생존구간: 08:41 ~ 12:28

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261002_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 96 | 08:40:44 [INFO] 로테이션 — 9.2MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 141 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 189 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 197 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 172 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:28

**매분 루프 커버리지 09:00~15:10: 209/371분 (56.3%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:29 | 15:10 | 162 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261002_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0159) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 127 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 223 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 174 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 153 | 11:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:28

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
| **오늘 20261002** | **12:28** | 로그 본문 |

- 델타 **-199분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-30 (MW0601 643ì°¨ â ì¥ì¤ ì ê²)
## 2026-09-30 (MW0601 644ì°¨ â ì¥í ì ê²)
## 2026-09-30 (MW0601 645ì°¨ â ì¥í ìëì¡°ì¹: F-4 ë½ ì£¼ì¸ ì§ë¨ Â· G-1 PreRetrain ì°í íì Â· G-2 git 1í ì¤ë
## 2026-10-01 (MW0601 646ì°¨ â ì¥ì  ì ê²)
## 2026-10-01 (MW0601 647ì°¨ â ì¥ì¤ ì ê²)
## 2026-10-01 (MW0601 648ì°¨ â ì¥í ì ê²)
## 2026-10-01 (MW0601 649ì°¨ â 648ì°¨ íì ì¥í ìëì¡°ì¹: F-3 ìì§ê¸° git í¸ì¶ ê¸°ë¡)
## 2026-10-02 (MW0601 650ì°¨ â ì¥ì  ì ê²)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
600ì´ ë¯¸ë¬, HOLD ì ì§), access violationì 5/10ì¼ íë³¸ì¼ë¡ ìì§ ê²½ë³´ ì¤ê³ë¥¼ ì§ííì§ ììë¤.

**How to apply**: F-1 ì ì©ì ì¥í ì´í ë³ë ì¸ììì `scripts/collect_evidence.py:2507~2520` ìì  â `tests/test_648_git_call_trace.py`ë¥ì "self-checkì call-trace ìì¶© ì call-trace ì°ì " ì¼ì´ì¤ ì¶ê° â ë¤ì ì½ì íê²½ ì¬í ì Â§2 ë ë¬¸êµ¬ ì¼ì¹ ì¬ë¶ë¡ ê²ì¦. ê·¸ ì ê¹ì§ë Â§2ì "ë½ ìê°ì ê²" í ì¤ë³´ë¤ "git í¸ì¶ ê¸°ë¡"ì í¸ì¶ë³ ì¶ì ì ì ë¢°í  ê².

**ê²ì¦**: `python scripts/collect_evidence.py --phase pre --pc MW0601 --out-auto` ì ì ì¤í(65.2KB ë¤ì´ì ì¤í¸ ìì±). `git --no-optional-locks branch/status/log` ì ì ì¤í(branch=`v9-dev`, ë¹ì¼ ì»¤ë° 0ê±´, ë³í ì¸ì ìì íì¸). `python scripts/git_lock_guard.py --check` 3í(ëì´ 52ì´Â·174ì´Â·352ì´) ì ë¶ HOLD íì ë³´ë¥ â ì¸ì ì¢ë£ ìì ê¹ì§ ì¤íì¼ ë¯¸íì , **íì ìë ì í¨**(Â§0-â¡ ê·ì½). ì¥ì  ê·ì½ì ì½ë ë³ê²½Â·ë¼ì´ë¸ DB ì¤ìº ìì.

**ì¤ë ì´ì íì¸(ì¥ì )**: py37_32 ë°íì íì¸(`Python 3.7.13 32bit | scipy=1.5.4 | sklearn=1.0.2 | joblib=1.1.0 | numpy=1.21.6` â joblib 1.1.0 vs CLAUDE.md íê¸° 1.1.1ì 491ì°¨ ê¸°ì§ ì¬ì, ì¬ìì  ì í¨). Cybos ì ì íì¸(request_futures_balance account=333044256 ìë£ 187ms). 08:55 ë§¤í¬ë¡/ë ì§ íì  ì ì(Canary zê²½ê³ í¼ì²=14ê°, ê³¼ê±° 2ì£¼ í¨í´ ë²ì ë´ â ì ê· ìë). ì¤ìê° êµ¬ë ì¬ì  ìì(CybosRT-START 08:45:08, ê°ì¥ ì ). ìµìì²´ì¸ ì´ê¸°í + 09:01:25~28 ì¬ìì§ ì ì(PCR=0.567, ATM_PCR=1.115). ì¤ì  ë¶ë³ì ì ì²´ ì¼ì¹(ë¶ì¼ì¹ 0ê±´), ì°¨ë¨ ê²ì´í¸ 40ê° ì¤ 9ê° êº¼ì§ ì ë¶ ê¸°ë¡ë ê²°ì ê³¼ ì¼ì¹.


**[09:13 KST íì] 650ì°¨ F-3/O-p1 ìë ¥ í´ì** `.git/index.lock`ì´ ëì´ ìê³(600ì´, 0.2ìê°)ë¥¼ ëê²¨ ì¥ git íë¡ì¸ì¤ 0ê°ë¡ STALE íì ëê³ , `git_lock_guard.py --reclaim`ì¼ë¡ ì¦ì íì(ì´ë¦ë³ê²½ ì°í ì±ê³µ â `.git/index.lock.stale_20261002001316_6`ë¡ ì´ë, ë¶ì¤ë¬ê¸° ìì²´ ì­ì ë ì½ì ë§ì´í¸ unlink ì ì½ì¼ë¡ ì¤í¨í´ T2 ë¶ì¤ë¬ê¸°ê° 8â9ê±´ì¼ë¡ ì¦ê° â Windows ìª½ ìë ì ë¦¬ íì, ì»¤ë°ì ë§ì§ ìì). íì ì§í `git_lock_guard.py --check` â `OK index.lock ìì` íì¸. ì¥ì  ììì ìë ¥ í´ìë¼ ì¥ì¤ì¼ë¡ ëê¸¸ íì ìì â O-p1ì ì¥ì  ì  ììì íì  ìë£ë¡ ë«ëë¤. ë¦¬í¬í¸ 1-1ì ì ì  í¬ì¸í°(â©ï¸ 09:13 KST) ì¶ê°í¨.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-30 (MW0601 643차 — 장중 점검) 신규 항목
## 2026-09-30 (MW0601 644차 — 장후 점검)
## 2026-09-30 (MW0601 645차 — 장후 자동조치)
## 2026-10-01 (MW0601 646차 — 장전 점검)
## 2026-10-01 (MW0601 647차 — 장중 점검)
## 2026-10-01 (MW0601 648차 — 장후 점검)
## 2026-10-01 (MW0601 649차 — 648차 후속 장후 자동조치)
## 2026-10-02 (MW0601 650차 — 장전 점검)
```

미완료 체크박스 **2941건** (끝에서 30건)
```
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
- [ ] **F-3 (지속, P1, 가설 보강)** 증거수집기 `git diff --numstat` 25초 타임아웃이 오늘 장중·장후 두 번 모두 재현됐으나 락 생성은 1회만(장중). "타임아웃=락"이 1:1이 아님을 확인 — 다음 재현 시 락 생성 여부와 작업트리 상태를 함께 기록할 것. 변경 파일 후보는 `scripts/collect_evidence…
- [ ] **648-1 (P2, 신규)** 장 마감 직후(15:11:09·15:11:37) 메인 스레드 26,579ms·15,297ms 정지 — `collection/cybos/api_connector.py:_pump_messages`(COM 메시지 펌프) 내부에서 발생, 같은 구간에 PumpGuard rollover 연기·OptionBook 57,38…
- [ ] **637-1/606-4/641-1 (지속, 4관측일째, 변화 없음)** 부팅 구간 access violation — 오늘도 정규장 이후 재발 0건. 사용자 결정 대기 그대로. 313차 원칙상 10거래일 표본 필요(현재 4일).
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
rror 유발) — 이번 세션 작성분은 정상 확인. 다음에 파일을 열 때 수동 교정 권장, 긴급성 낮음.

## 2026-10-01 (MW0601 649차 — 648차 후속 장후 자동조치)

- [x] **F-3 계측분 구현** 수집기 `run_git()` 호출 기록(`_GIT_CALL_TRACE`) + §2 `git 호출 기록` 줄 — 동작 무변경. 테스트 `tests/test_648_git_call_trace.py`. Windows 실측 최장 0.2초 → 타임아웃은 코웍 마운트 한정으로 좁혀짐.
- [ ] **F-3 판정 (지속)** 다음 코웍 수집 타임아웃 재현 시 §2 `git 호출 기록`에서 「락 생성 구간」이 타임아웃 호출과 겹치는지 기록. 3회 쌓이면 원인 판정(겹침 → kill 경로 / 비겹침 → 세션 임시 git 호출). 648-2(tmp_obj)와 같은 환경 축인지 함께 볼 것.
- [ ] **F-1·사용자 조치 1·2 (사용자 몫, 이월)** 문서 제목 확인(7일째 예정) · `docs/정기점검/수익률향상_누적대장.md`·`docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 커밋 — 자동조치는 dev_memory 2건만 커밋했다.


## 2026-10-02 (MW0601 650차 — 장전 점검)

- [x] **650-0(오늘 장전 판정 완료)** P0 없음. 기동·Cybos접속·08:55 매크로/레짐·실시간구독·옵션체인·설정 불변식 전부 정상. 상세는 `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` 장전 절 참조.
- [ ] **F-3 (지속, P1 — 5번째 재현)** `.git/index.lock` 재발(10/2 장전, 09:00 KST경). 9/30(x3)+10/1 장중(x1)에 이어 5번째. 타임아웃=락 생성이 1:1이 아님(648차 관측 그대로 유지). 다음 재현 시 §2 「git 호출 기록」에서 락 생성 구간이 타임아웃 호출과 겹치는지 계속 기록할 것.
- [ ] **F-1 (P1, 신규)** 증거수집기(`scripts/collect_evidence.py:2507~2520`)의 "락 자가점검" 한 줄이 같은 다이제스트의 「git 호출 기록」(호출별 추적, 573·591·508행)과 상충하는 것을 10/2 장전에 처음 확인(§2가 "이 수집 실행은 락을 만들지 않았다"라고 적었지만, 바로 아래 호출별 추적은 같은 실행에서 락이 생겼다고 적음 — 직접 `ls`·`git_lock_guard.py --check`로도 락 존재 확인됨). 원인 가설: self-check 분기가 참조하는 `lk` 값이 `_GIT_CALL_TRACE`의 최종 갱신보다 앞선 시점의 상태일 가능성(가설 — 코드 정독만으로 실행 순서 미확정). 변경 파일 후보: `collect_evidence.py` 2507~2520행 self-check 분기 — 그 지점에서 즉시 재조회하거나 call-trace의 마지막 전환을 우선 반영. 적용은 장후 이후 별도 세션.
- [ ] **637-1/606-4/641-1 (지속, 5관측일째)** 부팅 구간 access violation — 오늘도 PID 18204에서 3건, 정규장 이후 재발 0건. 313차 원칙상 10거래일 표본 필요(현재 5일, 6일째부터 과반). 사용자 결정 대기 그대로.
- [ ] **606-2/O-t2 최종 판정 — 재현함** SessionStateDrop이 10/1→10/2 날짜 전환 시 재현(08:41:08). EOD 마커 파일 우회 성공으로 실질 피해 없음. F-1(날짜전환 마커 승계, 「F-1」이 위 증거수집기 F-1과 이름이 겹치므로 — 이쪽은 **"SessionStateDrop F-1"**로 구분해 부른다) 미적용 그대로. 10/5(다음 거래일 전환) 재현 여부로 이월.
- [ ] **646-1 (지속, 커밋 대기)** 미커밋 19건(실질 변경 2건 M + 미추적 17건) — 10/2 08:58 기준 동일. 오늘은 수집기 git diff 실패(F-3 재현)로 실질/EOL 파생 분해를 못 받음 — 필요하면 수동 `git --no-optional-locks diff --numstat <경로 한정>`으로 재측정할 것.
- [ ] **633-1 (P2, 지속 — 오늘로 7일째)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 미확인·미커밋 지속.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` 부스러기 8건, 16.7시간 스테일 — 변화 없음. Windows에서 `--reclaim` 필요.
- [ ] **648-3 (P2, 지속 — 참고)** `DECISION_LOG.md` 09-30(642차) 구간 한글 인코딩 손상 1글자 — 변화 없음, 긴급성 낮음.
- [ ] **O-p1 (신규 발급)** `.git/index.lock` 최종 판정(스테일 확정 여부) — 장전 종료 시점 나이 352초(임계 600초 미달, HOLD). 장중 점검이 재확인해 판정/보류/이월 중 하나로 닫을 것.

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

### `data/heartbeat_MW0601_20261002.json` — 244B · 10-02 12:27:16
```json
{
 "pid": 18204,
 "written_at": "2026-10-02T12:28:16",
 "beat_epoch": 1790911693.6230414,
 "beat_age_sec": 2.7,
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

- 파일 최종 기록: **10-02 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-02)과 일치 |
|---|---|---|
| `date` | 2026-10-02 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-02 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-01) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-02 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-01) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:27** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 223 |
| `session_bars` 당일 행수 | 223 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 161봉** (`session_bars` 에도 없음): 12:28, 12:29, 12:30, 12:31, 12:32, 12:33, 12:34, 12:35, 12:36, 12:37, 12:38, 12:39, 12:40, 12:41, 12:42, 12:43, 12:44, 12:45, 12:46, 12:47

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
| 18204 | 08:40:44 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 189개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` | 22.5KB | 10-02 09:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_pre.md` | 65.2KB | 10-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20261001-점검리포트.md` | 74.1KB | 10-01 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_post.md` | 89.7KB | 10-01 16:19 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261001.md` | 0B | 10-01 12:44 |
| `docs/정기점검/매일점검/_tmp_append_addendum_20261001.md` | 0B | 10-01 12:44 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_intra.md` | 74.9KB | 10-01 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_pre.md` | 57.5KB | 10-01 09:00 |

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

1. `logs/20261002_SYSTEM.log`: 매분 루프 커버리지 209/371분 (56.3%) — 루프가 빠진 구간이 있다
2. `logs/20261002_SYSTEM.log`: 12:29~15:10 **연속 162분 매분 루프 기록 없음**
3. 메인 스레드 정지 5초 초과 **2건** (최대 12016ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20261002_SYSTEM.log`: **ConstOut** 7건(표본)
5. `logs/20261002_SIGNAL.log`: **WeightCollapse** 8건(표본)
6. `logs/20261002_SIGNAL.log`: **ConstOut** 8건(표본)
7. `logs/20261002_LEARNING.log`: **축퇴** 8건(표본)
8. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
9. 미커밋 변경 23건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261002*.log` (Windows) / `grep 강제청산 logs/*20261002*.log`*