# 미륵이 증거 다이제스트 — 2026-10-06 / PRE

- 생성 2026-10-06 08:59:32 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01bmaekx7tmyyi15cbhgppcc/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261006` · `2026-10-06` · `261006` · `1006`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **22개** 파일 · 22개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261006.log` | 136B | 10-06 07:22 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261006.log` | 125B | 10-06 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261006.log` | 140B | 10-06 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261006.json` | 244B | 10-06 08:59 |
| `launcher_{DATE}_084000_32243.log` | 1 | `logs/Mireuk_batch/launcher_20261006_084000_32243.log` | 57.7KB | 10-06 08:59 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261006.log` | 2.9KB | 10-06 08:58 |
| `retrain_intraday_20260702_{DATE}00.log` | 1 | `logs/retrain_intraday_20260702_100600.log` | 4.6KB | 07-02 10:06 |
| `retrain_intraday_20260703_{DATE}00.log` | 1 | `logs/retrain_intraday_20260703_100600.log` | 4.6KB | 07-03 10:06 |
| `retrain_intraday_20260706_{DATE}58.log` | 1 | `logs/retrain_intraday_20260706_100658.log` | 4.6KB | 07-06 10:07 |
| `retrain_intraday_20260812_{DATE}59.log` | 1 | `logs/retrain_intraday_20260812_100659.log` | 4.6KB | 08-12 10:07 |
| `{DATE}_DATA.log` | 1 | `logs/20261006_DATA.log` | 892B | 10-06 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261006_DEBUG.log` | 0B | 10-06 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261006_HEALTH.log` | 0B | 10-06 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261006_HOGA.log` | 1.1MB | 10-06 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261006_LEARNING.log` | 50.7KB | 10-06 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20261006_MICRO.log` | 30.3KB | 10-06 08:59 |
| `{DATE}_OPTION_BACKFILL.log` | 1 | `logs/20261006_OPTION_BACKFILL.log` | 372B | 10-06 07:24 |
| `{DATE}_PROBE.log` | 1 | `logs/20261006_PROBE.log` | 12.1KB | 10-06 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261006_SIGNAL.log` | 9.0KB | 10-06 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261006_SYSTEM.log` | 26.7KB | 10-06 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261006_TRADE.log` | 167B | 10-06 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261006_WARN.log` | 4.1KB | 10-06 08:59 |

## 2. 코드·커밋 상태

- HEAD `84bb350` · 브랜치 `v9-dev` · 미커밋 59건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 🔴 **인덱스락 잔존** 0바이트 · 0.0시간 · git 프로세스 0개 (판정 보류 — 3중 조건 미충족)
  - 락 주인 진단 `[ORPHAN]` 쥔 git 프로세스 없음 - 중단/강제종료된 명령의 잔재(갈래 1) (락 mtime 2026-10-06 00:00:25)
  - 🔴 **이 수집 실행 중 `.git/index.lock` 이 생겨 지금도 남아 있다** (시작 시점에는 없었다) — `run_git` 호출 구간(`git diff --numstat` → timeout)에 생겼다(동시 발생 — 인과 미확정). `scripts/git_lock_guard.py --check` 로 판정 후 회수할 것
  - git 호출 기록: 6회 · 타임아웃 2 · 실패 0 · 락 생성 구간 1 · 최장 25.0초(`git diff --numstat`)
    - `git diff --numstat` → timeout · 25.0초 · 락 없음→있음 · 🔴 **이 호출 구간에 락이 생겼다**(동시 발생 — 인과 미확정)
    - `git diff --numstat -w --ignore-cr-at-eol` → timeout · 25.0초 · 락 있음→있음
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
?? "C:\\Users\\82108\\PycharmProjects\\Peter\\트윗원문\\피터리_10월매매_20261002_1002.md"
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_20261002.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_전일보유_맥점되돌림_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자흐름_맥점관계_MW0601-20261002.md
?? docs/미륵이고도화3/외인선물순매수_수집현황_조사_MW0601-20261002.md
?? docs/미륵이고도화3/위클리먼스리_선물추종_주체비중_일별_MW0601-20260921-20261002.md
?? docs/미륵이고도화3/피터리_위로막힘_근거조사_MW0601-20261002.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261001.md
?? docs/신동거래/일일/신동_일일_MW0601_20261001.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261002.md
?? docs/신동거래/일일/신동_일일_MW0601_20261002.svg
?? docs/정기점검/_tmp_ledger_append_20261002.md
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261002.md
?? docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/featureset_health_report_20261002.md
?? docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261002.md
?? docs/정기점검/매일점검/MW0601-20260930-점검리포트.md
… 외 19건
```

**당일(2026-10-06) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
84bb350 [MW0601] 656차 후속3: 사다리 당일 외인·개인 층에 전일 보유 그림자 + 현재 보유 눈금
9412bd3 [MW0601] 656차 후속2: 사다리 9842 시점 파일(YYMMDD_HHMM_D) — 30분 단위 외인·개인 증감
bf8b206 [MW0601] 656차 후속: 사다리 옵션층에 목위클리 OI 버튼 추가
11c6b5c [MW0601] 656차: 맥점 × 옵션 사다리 로컬 서버 — 실시간 분 단위 + 날짜별 복기 · 9842 _P 차분 · 메시아 OI 대체 원천
efa1c40 [MW0601] 655차: 옵션 흐름(7222) 장 마감 재수집 보강 — 8거래일 조용한 실패 복구
6fdfd91 [MW0601] 654차: 주문 취소율 — 호가 흐름 분해 섀도 적재 (B1–B5)
ff7178a [MW0601] 653차 후속: 장후 자동조치 — F-1 · G-1
1e56ace [MW0601] 648차 후속: 장후 자동조치 — F-3
67cff42 [MW0601] 645차 후속: 장후 자동조치 — F-4 · G-1 · G-2 · F-1
89836e3 [MW0601] 639차 후속: 신동 목표 v1 vs v2 확대 비교 — 흐름 5일 + 75일 가격 대리(개정 문서 §8-4)
d9b4063 [MW0601] 637·638·640차 점검 산출물 + 639차 기록 — 9/28·9/29 장전·장중·장후
39f795a [MW0601] 639차: 신동 규격 v2 개정 — 1차 목표가 진입가 뒤에 놓이는 결함 수정
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

_본문 미열람(설정): `20261006_HOGA.log` 1.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/18개 (중요도순). 제외: `retrain_intraday_20260812_100659.log`, `20261006_MICRO.log`, `20261006_DATA.log`, `20261006_PROBE.log`, `launcher_20261006_084000_32243.log`, `20261006_OPTION_BACKFILL.log`, `mainstall_traceback_20261006.log`, `freeze_sentinel_20261006.log`_

### `logs/20261006_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-06 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-06 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-06 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261006_WARN.log` — 4.1KB · 51행 · 최종 08:59:02

- 형식 평문 · 시각 인식 51행 · WARNING=51

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-06 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-10-06 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=333044256
2026-10-06 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-06 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-06 09:00:42 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 40.9ms | size=1955x1124 candles=16 grid=14.9 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=23.8 cross=0.0 | slow_cnt=24 total_cnt=63 overlay_cnt=385
2026-10-06 09:00:42 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 45.3ms | size=1955x1124 candles=16 grid=15.0 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=28.0 cross=0.0 | slow_cnt=25 total_cnt=64 overlay_cnt=385
2026-10-06 09:00:43 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 51.7ms | size=1955x1124 candles=16 grid=15.2 spans=0.0 candles=0.8 dir=0.0 regime=0.0 markers=0.0 axes=34.1 cross=0.0 | slow_cnt=26 total_cnt=65 overlay_cnt=385
2026-10-06 09:00:43 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 86.2ms | size=1955x1124 candles=16 grid=27.1 spans=0.0 candles=1.0 dir=0.0 regime=0.0 markers=0.0 axes=55.5 cross=0.0 | slow_cnt=27 total_cnt=67 overlay_cnt=385
2026-10-06 09:00:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 74.2ms | size=1955x1124 candles=16 grid=18.4 spans=0.0 candles=0.7 dir=0.1 regime=0.0 markers=0.0 axes=53.2 cross=0.0 | slow_cnt=28 total_cnt=68 overlay_cnt=386
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 28 | 08:49:59 | 09:00:44 | paintEvent slow 31.0ms | size=1955x1125 candles=5 grid=11.2 spans=0.5 candles=13.2 dir=0.0 regime=0.1 markers=0.0 axes=3.2 cross=0.0 | slow_cnt=1 total_cnt=1 overlay_cnt=0 |
| `LiveDBG` | 13 | 08:41:08 | 09:00:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `MainStallTrace` | 2 | 08:58:18 | 09:00:04 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20261006.log |
| `PipePerf` | 2 | 09:00:02 | 09:00:02 | total=2089ms | S0=7ms S1=14ms S2=0ms S3=0ms S4=133ms S5=1114ms S6=749ms S7=49ms S8=23ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 2089ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `OptionFlowChart` | 1 | 08:41:18 | 08:41:18 | 그리기 59.2ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 856x1001 |
| `Health` | 1 | 09:00:02 | 09:00:02 | level=WARNING degraded=OFF | latency=2089ms | quality=1.00 | cache_age=52s | exceptions_10m=0 |

**채널** — `SYSTEM`×50, `HEALTH`×1

**컴포넌트 상위 15** — `ChartDBG`×28, `LiveDBG`×13, `출처축`×2, `MainStallTrace`×2, `PipePerf`×2, `CB⑤`×2, `OptionFlowChart`×1, `Health`×1

### `logs/20261006_SYSTEM.log` — 26.7KB · 227행 · 최종 08:59:30

- 형식 평문 · 시각 인식 220행 · INFO=220, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=11972 | 행감지=30s all_threads=True
2026-10-06 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-06 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-06 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-06 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-06 09:00:30 [INFO] SYSTEM: [TickUI] alive ticks=2170 code=A056A close=1115.84
2026-10-06 09:00:30 [INFO] SYSTEM: [CybosRT-TICK] #2200 code=A056A raw_time=90030 parsed=09:00:30 price=1115.36 vol=1 bid1=1115.10 ask1=1115.32 flag=49 side=BUY anchor=1/0
2026-10-06 09:00:34 [INFO] SYSTEM: [CybosRT-TICK] #2300 code=A056A raw_time=90034 parsed=09:00:34 price=1115.72 vol=1 bid1=1115.64 ask1=1115.72 flag=49 side=BUY anchor=1/0
2026-10-06 09:00:41 [INFO] SYSTEM: [CybosRT-TICK] #2400 code=A056A raw_time=90041 parsed=09:00:41 price=1114.50 vol=1 bid1=1114.50 ask1=1114.56 flag=50 side=SELL anchor=0/1
2026-10-06 09:00:46 [INFO] SYSTEM: [CybosRT-TICK] #2500 code=A056A raw_time=90046 parsed=09:00:46 price=1114.82 vol=1 bid1=1114.72 ask1=1114.84 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×220

**컴포넌트 상위 15** — `CybosRT-TICK`×30, `CybosSub`×21, `System`×17, `TickUI`×16, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20261006_SIGNAL.log` — 9.0KB · 149행 · 최종 08:59:02

- 형식 평문 · 시각 인식 149행 · WARNING=96, INFO=53

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-10-06 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.0447 → floor=0.50 적용 (z-score 폭발 방지)
2026-10-06 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0461 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-06 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0806 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-06 09:00:02 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.06s
2026-10-06 09:00:04 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 48 | 09:00:02 | 09:00:02 | 1m 'macro_vix' scale=0.0125 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 30 | 08:45:09 | 08:59:02 | 1m CORE 'cvd_divergence' raw_std≈0(0.0215) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 6개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:00:00 | 09:00:00 | ts=08:59 horizon=1m age=1m max_z=+7.65(institution_futures_net) extreme=6 adj=6 |

**채널** — `SIGNAL`×149

**컴포넌트 상위 15** — `ScalerFloor`×66, `ScalerRefresh`×36, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×3, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1, `AutoMasked`×1, `FQAdj`×1, `Ensemble`×1

### `logs/20261006_LEARNING.log` — 50.7KB · 282행 · 최종 08:59:02

- 형식 평문 · 시각 인식 282행 · WARNING=138, INFO=144

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
  …
2026-10-06 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-06 08:55:09 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=14698, ver=5)
2026-10-06 08:59:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-06 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1117.24
2026-10-06 09:00:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 50 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 47 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 15 | 08:40:50 | 08:40:57 | 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 12 | 08:40:51 | 08:40:58 | 축퇴 감지 — span=0.00068 auc=0.478 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 10 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 3 | 08:40:51 | 08:40:57 | 축퇴 감지 — span=0.00028 auc=0.502 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:59 | 08:40:59 | 복원한 보정기가 축퇴 상태 — span=0.00737 auc=0.453 out_max=0.3890 (n=2664) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×282

**컴포넌트 상위 15** — `Calibration:1m`×99, `Calibration:30m`×93, `Calibration:3m`×28, `Calibration:10m`×22, `Calibration:5m`×19, `ScalerWarmup`×6, `Calibration:15m`×5, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/retrain_intraday_20260703_100600.log` — 4.6KB · 39행 · 최종 10:06:31

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-03 10:06:00,612 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-03 10:06:00,612 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-03 10:06:00,612 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-03 10:06:00,612 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_fb587308.json
2026-07-03 10:06:02,039 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-03 10:06:31,721 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.43s | old_acc=nan)
2026-07-03 10:06:31,724 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-03 10:06:31,724 [INFO] LEARNING: [Retrain] 완료 | 29.7초 | 성공=6/6 호라이즌
2026-07-03 10:06:31,725 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 31.1s 데이터=20000행
2026-07-03 10:06:31,727 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_fb587308.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260706_100658.log` — 4.6KB · 39행 · 최종 10:07:31

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-06 10:06:58,474 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-06 10:06:58,474 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-06 10:06:58,474 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-06 10:06:58,474 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_85af766d.json
2026-07-06 10:07:00,273 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-06 10:07:31,822 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.40s | old_acc=nan)
2026-07-06 10:07:31,825 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-06 10:07:31,825 [INFO] LEARNING: [Retrain] 완료 | 31.6초 | 성공=6/6 호라이즌
2026-07-06 10:07:31,827 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 33.4s 데이터=20000행
2026-07-06 10:07:31,829 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_85af766d.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260702_100600.log` — 4.6KB · 39행 · 최종 10:06:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-02 10:06:00,688 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-02 10:06:00,689 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-02 10:06:00,689 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-02 10:06:00,689 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7926b354.json
2026-07-02 10:06:02,550 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-02 10:06:36,669 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.38s | old_acc=nan)
2026-07-02 10:06:36,672 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-02 10:06:36,672 [INFO] LEARNING: [Retrain] 완료 | 34.1초 | 성공=6/6 호라이즌
2026-07-02 10:06:36,673 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 36.0s 데이터=20000행
2026-07-02 10:06:36,675 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7926b354.json
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
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 5건 · 최대 6360ms · 5초 초과 2건

상위 — 6360ms, 5469ms, 4937ms, 4594ms, 3375ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:58:18 | 6360ms | **미측정** | — |
| 09:00:04 | 5469ms | 2089ms | **3380ms (62%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261006_WARN.log`
```
--- 메인 스레드 블로킹 ×5(표본)
08:41:13 2026-10-06 08:41:13 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4594 band=INFO since_pipe_s=NA
08:50:04 2026-10-06 08:50:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4937ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4937 band=INFO since_pipe_s=NA
08:50:09 2026-10-06 08:50:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3375 band=INFO since_pipe_s=NA
08:58:18 2026-10-06 08:58:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6360ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6360 band=WARN since_pipe_s=NA
```

### `logs/20261006_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-10-06 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20261006_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
```

### `logs/20261006_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261006_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261006_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 12 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 39 | 08:49:59 [WARNING] paintEvent slow 31.0ms | size=1955x1125 candles=5 grid=11.2 spans=0.5 candles=13.2 dir=0.0 regime=0.1 markers… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 35 | 08:55:41 [WARNING] paintEvent slow 35.4ms | size=1955x1124 candles=11 grid=12.1 spans=0.0 candles=0.4 dir=0.0 regime=0.0 markers… |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261006_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 95 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=11972 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 112 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 79 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261006_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0215) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 98 | 08:50:04 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 91 | 08:55:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261005 | 09:41 | 로그 본문 |
| 20261003 | 18:32 | 로그 본문 |
| 20261002 | 19:02 | 로그 본문 |
| 20261001 | 15:47 | 로그 본문 |
| 20260930 | 15:47 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261006** | **09:00** | 로그 본문 |

- 델타 **-407분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-02 (MW0601 651차 — 장중 점검)
## 2026-10-02 (MW0601 652차 — 장후 점검)
## 2026-10-02 (MW0601 653차 — 652차 후속 장후 자동조치: F-1 락 자가점검 상충 수정 · G-1 since 시간대)
## 2026-10-02 (MW0601 654차 — 주문 취소율 수집: 호가 흐름 분해 섀도 적재 B1–B5)
## 2026-10-04 (MW0601 655차 — 옵션 흐름(7222) 장 마감 재수집 보강: 8거래일 조용한 실패 복구)
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버: 실시간 분 단위 + 날짜별 복기 · 9842 _P 차분 · 메시아 체인 대체 원천)
## 2026-10-05 (MW0601 657차 — 장전 점검)
## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
N EXIT] PID=31924`로 정상 종료. `data/shutdown_normal_20261005.txt` 원인 코드 `user_close` — 사용자가 직접 종료한 것으로 확인됨(크래시·워치독 발동 아님. 종료 직전 하트비트 `beat_age=2s strikes=0`로 정상). 거래(`TRADE.log`)는 "저장 상태가 어제 데이터 — 무시" · "ProfitGuard 설정 업데이트" 2줄뿐 — 진입·청산 0건. ② `data/session_state.json`의 `auto_shutdown_done_date`가 오늘도 빈 문자열("")로 남음 — 휴장일 자동종료 기능이 있다면(해당 키 존재가 그 근거) 오늘도 발동하지 않았고, 사용자가 수동으로 먼저 종료함(1-5 신규 등록). ③ **이 Cowork 세션 자체의 인프라 문제** — `device_bash`(사용자 PC 로컬 셸 다리)가 세션 시작부터 약 30분간 "Workspace still starting"만 반환, 끝내 가동되지 않음. 그 결과 `collect_evidence.py --phase post` · `git --no-optional-locks` 계열 명령 · `predictions.db`/`trades.db` 직접 조회를 이번 장후에서 실행하지 못함(1-6 신규 등록). 대체 수단(`device_list_dir`/`device_stage_files`로 개별 파일 직접 읽기 — git 명령 미실행이라 `.git/index.lock` 재발 위험 없음)으로 브랜치(`v9-dev`, `.git/HEAD`)·인덱스락 부재(`.git` 디렉터리 목록)·금일 커밋 0건(`.git/COMMIT_EDITMSG`·`.git/index`·`.git/logs/HEAD` 수정시각 전부 2026-10-04 16:18 KST)·오늘자 로그 6종·`data/` 마커 파일을 직접 확인해 대체함. ④ 이 장후 점검 트리거 자체가 예약 시각(10/5 16:15 KST 추정, UTC 07:15)보다 약 15시간 11분 늦은 10/6 07:26 KST(UTC 22:26:56)에 발동함 — `logs/claude_resume_20261005.log`에는 오늘 아침(07:21~07:22 KST, 장전 직전)의 데스크톱 앱 깨우기 기록만 있고 이번 지연 발동 시각에 대응하는 기록은 없음(가설: 야간에는 깨우기 자동화가 안 돌아 디바이스 다리가 잠들어 있었을 가능성 — 표본 1건, 미확정).

**원인**: ①②는 휴장일 설계대로 정상 — 신규 결함 아님. ③④는 미륵이 코드가 아니라 이 Cowork 점검 세션/디바이스 브리지 인프라 쪽 문제로 추정(미확정, 1건 표본).

**결정**: 1-1(장전 `.git/index.lock`)은 장전 세션 내 이미 해소 확인. 1-2~1-4(부팅 예외·문서 제목 손상·joblib 문서 오기)는 오늘 변동 없이 지속만 재확인(함정① — 신규 Fix 등록 없음). 1-5(자동 휴장일 종료 미발동)는 신규 관측으로만 등록, 결함 단정 안 함. 1-6(디바이스 셸 미가동)은 미륵이 쪽 TODO가 아니라 이 Cowork 운영 쪽 참고사항으로 기록 — 다음 세션이 디바이스 다리가 정상일 때 오늘자 `evidence_MW0601-20261005_post.md`를 보강 실행할 것을 권장(658-1).

**Why**: 313차 원칙(표본 1건 — access violation 외 나머지는 전부 1건 표본) 적용해 1-5·④ 모두 확정 결론 내지 않음. 함정①(판정≠결정) 방지 — 기존 F-3·606-4·633-1·491-F-3 전부 지속으로만 기록, 신규 중복등록 없음. 함정④(ERROR 아닌 INFO/WARNING 중심 판독) 적용 — 오늘 WARN.log 13줄 전부 08:41 부팅 구간 한정, 09:00 정규장 개시 이후 0건.

**How to apply**: 658-1 — 디바이스 셸이 정상일 때 `python scripts/collect_evidence.py --phase post --out docs/정기점검/매일점검/evidence_MW0601-20261005_post.md` 1회 보강 실행해 공식 다이제스트 공백을 메울 것. 658-2(선택) — `main.py`의 종료 핸들러에서 `auto_shutdown_done_date`를 쓰는 코드 경로를 `grep`으로 확인해, 휴장일 자동종료 기능이 실제로 구현돼 있는지(설계 문서에만 있고 미구현인지) 확정할 것 — 급하지 않음(사람이 대신 꺼도 안전하므로).

**검증**: 다음 휴장일에 `auto_shutdown_done_date`가 그날 날짜로 채워지는지, 아니면 오늘처럼 빈 문자열로 남는지 재관측(표본 2건째). 디바이스 셸 가동 여부는 다음 장전/장중/장후 세션에서 재확인(658-1 보강 실행 시도 포함).

**추가**: 오늘 신규 커밋 0건 · 미커밋 55건 변동 없음(장전 그대로) — `git add .` 금지 권고 유지(CRLF/LF 분해 미확인, 디바이스 셸 제약으로 수집기 §2를 돌리지 못해 이번엔 실질변경/EOL파생 분해를 못 냄 — 다음 세션이 보강).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-02 (MW0601 651차 — 장중 점검)
## 2026-10-02 (MW0601 652차 — 장후 점검)
## 2026-10-02 (MW0601 653차 — 652차 후속 장후 자동조치)
## 2026-10-02 (MW0601 654차 — 호가 흐름 분해 섀도 적재)
## 2026-10-04 (MW0601 655차 — 옵션 흐름 장 마감 재수집 보강)
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버)
## 2026-10-05 (MW0601 657차 — 장전 점검, 휴장일)
## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)
```

미완료 체크박스 **2987건** (끝에서 30건)
```
- [ ] **633-1 (P2, 지속 — 오늘로 8일째)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상, 미확인·미커밋 지속.
- [ ] **646-1 계열 (지속, 커밋 대기)** 미커밋 44건(16:21 KST 기준) — 장 마감 자동 산출물(EOD 재학습 모델·DB·일일 리포트 등) 자연 증가 + 1-6 기형 파일 1건 포함. 경로 명시해 `git add` 후 커밋 권고.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` 부스러기 — 오늘 장후 재현분 8건 + 이름변경된 index.lock 잔재 1건 추가(누계 17건). Windows에서 `--reclaim` 필요.
- [ ] **648-3 (P2, 지속 — 참고)** `DECISION_LOG.md` 09-30(642차) 구간 한글 인코딩 손상 1글자 — 변화 없음, 긴급성 낮음.
- [ ] **G-1 (신규, 저위험)** SKILL.md §0 "병행 세션 확인" 예시 명령에 시간대(`+0900`) 명시 반영 검토(651-2 계승) — 매 세션의 UTC/KST 환산 암산 오류 가능성을 구조적으로 제거.
- [ ] **O-u1 (신규, 다음 거래일)** access violation 재현 여부 — 6관측일째 여부.
- [ ] **O-u2 (신규, 다음 거래일)** `.git/index.lock` 재현 및 자가점검 문구 상충 지속 여부.
- [ ] **O-u3 (신규, 2주 누적 중)** 메인스레드 5초 초과 정지 추가 표본(482차 F-3 섀도) — 현재 누적 2건.
- [ ] **O-u4 (신규, 다음 거래일)** 문서 제목(633-1) 수정·커밋 여부 확인.
- [ ] **O-u5 (신규, 다음 거래일)** 1-6 기형 파일 삭제/이동 여부, 재발 여부 확인.
- [ ] **O-u2 보강** 다음 재현 시 §2 자가점검 줄이 호출 기록과 같은 구간을 가리키는지 실측 확인(653차 수정의 라이브 검증). F-3(타임아웃→락 생성 원인)은 미해결 — 관찰 계속.
- [ ] **654-1 (다음 거래일 장후, P1)** `python scripts/book_flow_recon.py` — 적재율 ≈100% · 항등식 위반 0 · 체결 커버리지 ≤1.05 · 건수 가용률. SYSTEM 로그에 `[BOOKFLOW][EXT-FAIL]`/`[CNT-INVALID]` 경고 여부. HOGA 로그 `[BOOKFLOW]` 줄의 `…
- [ ] **654-2 (다음 거래일 장후, P1)** 부하 — `[PipePerf]` 분포를 654차 이전 5거래일과 비교. 악화 시 `_book_flow_step` 비활성 스위치부터 넣을 것(현재 없음).
- [ ] **654-3 (섀도 10거래일 후)** 「두꺼운 매도벽(`book_ask_max` 상위) 감소분의 `ask_exec_qty` vs `ask_cancel_qty_lb` 비중 + 이후 가격 경로」 — 표본 보기 전 판정 기준 사전등록.
- [ ] **654-4 (보류)** B6 일반선물 `A016C` 호가 추가 구독 — 654-2 부하 확인 후 판단. 미니는 단당 1–2계약이라 건수 정보가 얇다.
- [ ] **654-5 (별건, P2)** `test_457::test_db_fallback_columns_have_measured_flag` 실패 — `dashboard/main_dashboard.py → peter_paste` INSERT의 `or ''`/`or 0.0` 폴백(632차 커밋분). 플래그 추가 또는 근거와 함께 `_DB_FALLBACK…
- [ ] **655-1 (10/6 화 장후, P1)** 첫 실거래일 확인 — `(Get-ScheduledTaskInfo -TaskName Mireuk_OptionFlowBackfill_1605 -TaskPath '\Mireuk\').LastTaskResult` = 0 · `logs\20261006_OPTION_BACKFILL.log` 의 「마감 구간 확…
- [ ] **655-2 (10/7 수 EOD)** `[OptionFlowFresh]` 가 10/6 을 「확보」로 판정하는지 EOD 로그 확인(9/21–10/2 8일은 영구 결손으로 계속 뜬다 — `DEFAULT_DAYS=10` 창을 벗어나면 사라진다).
- [ ] **655-3 (10/8 목 만기일)** 만기일 7222 마지막 행 시각 실측 → `CLOSE_OK_EXPIRY`(현재 15:20 보수값) 확정. 근월물 만기 후에도 먼스리(E/F)·위클리 상품이 15:45 까지 찍히면 만기일 기준을 15:40 으로 올릴 것.
- [ ] **655-4 (MW0602, 선택)** 이 커밋 체리픽 시 그 PC 는 BROKER=creon → Highest 유지. 재등록은 불필요하나 시각 16:20 을 원하면 관리자 PowerShell 에서 `TASK_OPTION_BACKFILL_INSTALL.bat` 재실행.
- [ ] **656-1 (10/6 화 장중)** 실제 장중 실시간 갱신 확인 — 상태칩 「다음 n초」·「지금」 선 · `[PipePerf]` 에 서버 영향 없는지(raw_data.db 증분 조회 20초 1회).
- [ ] **656-2 (10/8 만기일)** 목위클리 부재·먼스리 D0 화면 · 메시아 목위클리 만기 표기(9/24 vs 실제 9/23 — 추석 이동분) 같은 원천 표기 차이 정리 여부.
- [ ] **656-3 (선택)** 장중 베이시스 변동이 큰 날(9/22 −4pt) 행사가 위치를 하루 중앙값 대신 **스냅샷 시각별 베이시스**로 옮길지.
- [ ] **656-4 (선택)** 9842 장중 30분 내보내기(`YYMMDD_HHMM_D`) 인식 → 행사가 × 주체 × 시간 히트맵.
- [ ] **O-u6 (신규, 10/6 화 장전)** `data/session_state.json` 날짜 전환 시 `p8_last_success_date`·`eod_retrain_ok_date` 키 부재 — 10/5(휴장일)에는 `[SessionStateDrop]` 경고 로그 자체가 뜨지 않았음(10/1→10/2 전환 때와 다른 점). 휴장일이라 Pre…
- [ ] **O-u1 (지속)** 부팅구간 access violation — 10/5로 7관측일째(9/17·9/28·9/29·9/30·10/1·10/2·10/5), 다음 실거래일(10/6)에 8관측일째 재현 여부 확인.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` + 이름변경된 index.lock 부스러기 — 10/5 장전분 1건 추가. Windows에서 `--reclaim` 필요.
- [ ] **658-1 (P2, 다음 디바이스 셸 가동 시)** `python scripts/collect_evidence.py --phase post --out docs/정기점검/매일점검/evidence_MW0601-20261005_post.md` 보강 실행 — 이번 장후는 `device_bash` 미가동으로 공식 증거 다이제스트를 생성하지 못함. 급…
- [ ] **658-2 (P2, 선택)** `main.py` 종료 핸들러에서 `auto_shutdown_done_date` 쓰기 경로를 `grep`으로 확인 — 휴장일 자동종료 기능이 실제 구현돼 있는지, 오늘(10/5)처럼 사용자가 먼저 종료하는 경우에 그 경로를 아예 안 타는지 확정. 다음 휴장일 1회 더 관측 후(표본 2건) 판단해도 됨.
- [ ] **O-u6-참고** 10/5는 휴장일이라 PreRetrain 미가동으로 `p8_last_success_date`·`eod_retrain_ok_date` 날짜 전환 판정 불가 — 10/6(화) 실거래일 장전에서 그대로 판정.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
wBackfill_1605 -TaskPath '\Mireuk\').LastTaskResult` = 0 · `logs\20261006_OPTION_BACKFILL.log` 의 「마감 구간 확보 — 옵션 최신봉 16:0x」 · DB `max(bar_time)` ≥ 15:45 · 15:34 행이 HTS 와 일치하는지 HTS [7222] 1개 상품으로 대조.
- [ ] **655-2 (10/7 수 EOD)** `[OptionFlowFresh]` 가 10/6 을 「확보」로 판정하는지 EOD 로그 확인(9/21–10/2 8일은 영구 결손으로 계속 뜬다 — `DEFAULT_DAYS=10` 창을 벗어나면 사라진다).
- [ ] **655-3 (10/8 목 만기일)** 만기일 7222 마지막 행 시각 실측 → `CLOSE_OK_EXPIRY`(현재 15:20 보수값) 확정. 근월물 만기 후에도 먼스리(E/F)·위클리 상품이 15:45 까지 찍히면 만기일 기준을 15:40 으로 올릴 것.
- [ ] **655-4 (MW0602, 선택)** 이 커밋 체리픽 시 그 PC 는 BROKER=creon → Highest 유지. 재등록은 불필요하나 시각 16:20 을 원하면 관리자 PowerShell 에서 `TASK_OPTION_BACKFILL_INSTALL.bat` 재실행.

## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버)

- [x] **656-0 완료** 로컬 서버(실시간·달력) · 9842 머리행/단위 파서 · `_P` 차분 `_D` 생성 · 메시아 체인 OI 대체 원천 · `tests/test_656_*`.
- [ ] **656-1 (10/6 화 장중)** 실제 장중 실시간 갱신 확인 — 상태칩 「다음 n초」·「지금」 선 · `[PipePerf]` 에 서버 영향 없는지(raw_data.db 증분 조회 20초 1회).
- [ ] **656-2 (10/8 만기일)** 목위클리 부재·먼스리 D0 화면 · 메시아 목위클리 만기 표기(9/24 vs 실제 9/23 — 추석 이동분) 같은 원천 표기 차이 정리 여부.
- [ ] **656-3 (선택)** 장중 베이시스 변동이 큰 날(9/22 −4pt) 행사가 위치를 하루 중앙값 대신 **스냅샷 시각별 베이시스**로 옮길지.
- [ ] **656-4 (선택)** 9842 장중 30분 내보내기(`YYMMDD_HHMM_D`) 인식 → 행사가 × 주체 × 시간 히트맵.

## 2026-10-05 (MW0601 657차 — 장전 점검, 휴장일)

- [ ] **O-u6 (신규, 10/6 화 장전)** `data/session_state.json` 날짜 전환 시 `p8_last_success_date`·`eod_retrain_ok_date` 키 부재 — 10/5(휴장일)에는 `[SessionStateDrop]` 경고 로그 자체가 뜨지 않았음(10/1→10/2 전환 때와 다른 점). 휴장일이라 PreRetrain이 안 돌아서 생긴 정상 공백인지 606-2 계열의 변종인지 다음 실거래일 장전에서 판정.
- [ ] **O-u1 (지속)** 부팅구간 access violation — 10/5로 7관측일째(9/17·9/28·9/29·9/30·10/1·10/2·10/5), 다음 실거래일(10/6)에 8관측일째 재현 여부 확인.
- [x] **O-u2 판정 완료 (같은 세션 내)** `.git/index.lock`(10/5 장전 수집분) 스테일 확정 후 `--reclaim`으로 장전 세션 안에서 자력 회수 완료 — 다음 세션 이월 불필요. 이름변경된 부스러기 1건 추가, 648-2가 계속 추적.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` + 이름변경된 index.lock 부스러기 — 10/5 장전분 1건 추가. Windows에서 `--reclaim` 필요.


## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)

- [ ] **658-1 (P2, 다음 디바이스 셸 가동 시)** `python scripts/collect_evidence.py --phase post --out docs/정기점검/매일점검/evidence_MW0601-20261005_post.md` 보강 실행 — 이번 장후는 `device_bash` 미가동으로 공식 증거 다이제스트를 생성하지 못함. 급하지 않음(오늘은 거래 0건이라 판정에 영향 없음).
- [ ] **658-2 (P2, 선택)** `main.py` 종료 핸들러에서 `auto_shutdown_done_date` 쓰기 경로를 `grep`으로 확인 — 휴장일 자동종료 기능이 실제 구현돼 있는지, 오늘(10/5)처럼 사용자가 먼저 종료하는 경우에 그 경로를 아예 안 타는지 확정. 다음 휴장일 1회 더 관측 후(표본 2건) 판단해도 됨.
- [ ] **O-u6-참고** 10/5는 휴장일이라 PreRetrain 미가동으로 `p8_last_success_date`·`eod_retrain_ok_date` 날짜 전환 판정 불가 — 10/6(화) 실거래일 장전에서 그대로 판정.

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

### `data/heartbeat_MW0601_20261006.json` — 244B · 10-06 08:59:09
```json
{
 "pid": 11972,
 "written_at": "2026-10-06T09:00:39",
 "beat_epoch": 1791244839.1501157,
 "beat_age_sec": 0.8,
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

- 파일 최종 기록: **10-06 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-06)과 일치 |
|---|---|---|
| `date` | 2026-10-06 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-06 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (4일 전: 2026-10-02) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-06 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-02) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **08:59** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 15 |
| `session_bars` 당일 행수 | 15 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 369봉** (`session_bars` 에도 없음): 09:00, 09:01, 09:02, 09:03, 09:04, 09:05, 09:06, 09:07, 09:08, 09:09, 09:10, 09:11, 09:12, 09:13, 09:14, 09:15, 09:16, 09:17, 09:18, 09:19

- 라이브 로그 대조: `logs/20261006_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 11972: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 11972 | 08:40:45 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 194개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261005-점검리포트.md` | 36.6KB | 10-06 08:01 |
| `docs/정기점검/매일점검/evidence_MW0601-20261005_pre.md` | 57.6KB | 10-05 09:00 |
| `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` | 91.4KB | 10-02 17:29 |
| `docs/정기점검/매일점검/_tmp_append_post_20261002.md` | 0B | 10-02 16:31 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_post.md` | 85.1KB | 10-02 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_intra.md` | 73.4KB | 10-02 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_pre.md` | 65.2KB | 10-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20261001-점검리포트.md` | 74.1KB | 10-01 17:30 |

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

1. `.git/index.lock` 존재 (0바이트 · 0.4분 · git 프로세스 0) — 실행 중인 git 일 수 있으니 **지우지 말 것**. 몇 분 뒤에도 남아 있으면 재판정
2. 메인 스레드 정지 5초 초과 **2건** (최대 6360ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20261006_LEARNING.log`: **축퇴** 8건(표본)
4. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
5. 미커밋 변경 59건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`
6. 🔴 **이 수집 실행이 `.git/index.lock` 을 남겼다** — 시작 시점에는 없었다(생긴 구간은 §2 「git 호출 기록」 참조 — 653차). 방치하면 그날 dev_memory·리포트가 커밋되지 않은 채로 끝난다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261006*.log` (Windows) / `grep 강제청산 logs/*20261006*.log`*