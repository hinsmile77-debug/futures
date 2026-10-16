# 미륵이 증거 다이제스트 — 2026-10-05 / PRE

- 생성 2026-10-05 08:59:43 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-019rcmkdwf1nbuxwmh3ifnpr/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261005` · `2026-10-05` · `261005` · `1005`
- 🟦 **휴장일** — KRX 휴장일(`config/krx_holidays.py` 등록). 매매·매분 파이프라인이 없는 것이 정상이므로 장중 로그 침묵(FZ-6)·장후 조기종료(480차) 적신호를 **끈다**. 목록이 틀렸을 수 있다(2026-09-28 오등록 전례) — 이 판정이 의심되면 파일을 확인하라.
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261005.log` | 136B | 10-05 07:22 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261005.json` | 245B | 10-05 08:59 |
| `launcher_{DATE}_084001_12241.log` | 1 | `logs/Mireuk_batch/launcher_20261005_084001_12241.log` | 13.7KB | 10-05 08:41 |
| `retrain_intraday_20260812_1{DATE}9.log` | 1 | `logs/retrain_intraday_20260812_110059.log` | 4.6KB | 08-12 11:01 |
| `retrain_intraday_20260908_{DATE}01.log` | 1 | `logs/retrain_intraday_20260908_100501.log` | 2.8KB | 09-08 10:05 |
| `{DATE}_DATA.log` | 1 | `logs/20261005_DATA.log` | 0B | 10-05 08:40 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261005_DEBUG.log` | 0B | 10-05 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261005_HEALTH.log` | 0B | 10-05 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261005_HOGA.log` | 0B | 10-05 08:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261005_LEARNING.log` | 50.1KB | 10-05 08:41 |
| `{DATE}_MICRO.log` | 1 | `logs/20261005_MICRO.log` | 0B | 10-05 08:40 |
| `{DATE}_PROBE.log` | 1 | `logs/20261005_PROBE.log` | 95B | 10-05 08:41 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261005_SIGNAL.log` | 1.5KB | 10-05 08:45 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261005_SYSTEM.log` | 8.6KB | 10-05 08:56 |
| `{DATE}_TRADE.log` | 1 | `logs/20261005_TRADE.log` | 167B | 10-05 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261005_WARN.log` | 1.8KB | 10-05 08:41 |

## 2. 코드·커밋 상태

- HEAD `84bb350` · 브랜치 `v9-dev` · 미커밋 55건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 🔴 **인덱스락 잔존** 0바이트 · 0.0시간 · git 프로세스 0개 (판정 보류 — 3중 조건 미충족)
  - 락 주인 진단 `[ORPHAN]` 쥔 git 프로세스 없음 - 중단/강제종료된 명령의 잔재(갈래 1) (락 mtime 2026-10-05 00:00:25)
  - 🔴 **이 수집 실행 중 `.git/index.lock` 이 생겨 지금도 남아 있다** (시작 시점에는 없었다) — `run_git` 호출 구간(`git diff --numstat` → timeout)에 생겼다(동시 발생 — 인과 미확정). `scripts/git_lock_guard.py --check` 로 판정 후 회수할 것
  - git 호출 기록: 6회 · 타임아웃 1 · 실패 0 · 락 생성 구간 1 · 최장 25.0초(`git diff --numstat`)
    - `git diff --numstat` → timeout · 25.0초 · 락 없음→있음 · 🔴 **이 호출 구간에 락이 생겼다**(동시 발생 — 인과 미확정)
```
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
?? docs/정기점검/매일점검/MW0601-20261001-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261002-점검리포트.md
… 외 15건
```

**당일(2026-10-05) 커밋**
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

_본문 미열람(설정): `20261005_HOGA.log` 0B — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/10개 (중요도순). 제외: `launcher_20261005_084001_12241.log`, `claude_resume_20261005.log`_

### `logs/20261005_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-05 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-05 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-05 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-05 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261005_WARN.log` — 1.8KB · 12행 · 최종 08:41:19

- 형식 평문 · 시각 인식 12행 · WARNING=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-05 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-05 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-10-05 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=333044256
2026-10-05 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-05 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-05 08:41:14 [WARNING] SYSTEM: [LiveDBG] _apply update_learning 0ms
2026-10-05 08:41:14 [WARNING] SYSTEM: [LiveDBG] _apply update_efficacy 16ms
2026-10-05 08:41:14 [WARNING] SYSTEM: [LiveDBG] _apply update_trend 47ms
2026-10-05 08:41:14 [WARNING] SYSTEM: [LiveDBG] _apply pnl_history 47ms 총1109ms
2026-10-05 08:41:19 [WARNING] SYSTEM: [OptionFlowChart] 그리기 57.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 874x1001
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 9 | 08:41:09 | 08:41:14 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `OptionFlowChart` | 1 | 08:41:19 | 08:41:19 | 그리기 57.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 874x1001 |

**채널** — `SYSTEM`×12

**컴포넌트 상위 15** — `LiveDBG`×9, `출처축`×2, `OptionFlowChart`×1

### `logs/20261005_SYSTEM.log` — 8.6KB · 58행 · 최종 08:56:10

- 형식 평문 · 시각 인식 56행 · INFO=56, PLAIN=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-05 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=31924 | 행감지=30s all_threads=True
2026-10-05 08:40:46 [INFO] SYSTEM: [DBInit] 합계 0.48s | predictions=0.05s trades=0.21s daily_stats=0.01s shap=0.05s raw_data=0.13s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-05 08:40:46 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-05 08:40:46 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-05 08:40:46 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-05 08:41:19 [INFO] SYSTEM: [Replay] post_market 2026-10-02 — 6패널 수집, 메인 스레드로 넘긴다 [futures_flow option_chain option_flow prediction price rv_iv]
2026-10-05 08:41:19 [INFO] SYSTEM: [Replay] post_market 2026-10-02 — 6패널 주입 [price 15:08 · prediction 15:08 · rv_iv 15:08 · option_chain 15:08 · option_flow 15:34 · futures_flow 15:34]
2026-10-05 08:46:10 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 08:46:10
2026-10-05 08:51:10 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 08:51:10
2026-10-05 08:56:10 [INFO] SYSTEM: [System] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 08:56:10
```

</details>

**채널** — `SYSTEM`×56

**컴포넌트 상위 15** — `System`×9, `CybosSub`×7, `SYSTEM`×4, `BrokerSync`×4, `BalanceUI`×4, `Account`×2, `CybosDailyPnl`×2, `WarmupRetrain`×2, `Notify`×2, `Capital`×2, `Runtime`×2, `Replay`×2, `FaultHandler`×1, `DBInit`×1, `FeatureBuilder`×1

### `logs/20261005_SIGNAL.log` — 1.5KB · 18행 · 최종 08:45:02

- 형식 평문 · 시각 인식 18행 · INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-10-05 08:40:48 [INFO] SIGNAL: [EnsembleGater] 저장된 가중치 복원: C:\Users\82108\PycharmProjects\futures\data\ensemble_gater_weights.json
2026-10-05 08:41:02 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-05 08:41:09 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
2026-10-05 08:45:02 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → PRE_MARKET: 선물 프리장 — 진입 불허, scaler warmup 전용
2026-10-05 09:00:02 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**채널** — `SIGNAL`×18

**컴포넌트 상위 15** — `DynMC`×7, `Model`×6, `TimeRouter`×3, `EnsembleGater`×1, `FeatureBuilder`×1

### `logs/20261005_LEARNING.log` — 50.1KB · 274행 · 최종 08:41:07

- 형식 평문 · 시각 인식 274행 · WARNING=138, INFO=136

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-05 08:40:48 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과
2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
  …
2026-10-05 08:41:00 [WARNING] LEARNING: [Calibration:ensemble] 복원한 보정기가 축퇴 상태 — span=0.00737 auc=0.453 out_max=0.3890 (n=2664) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다.
2026-10-05 08:41:00 [INFO] LEARNING: [Calibration:ensemble] 보정기 복원 완료 (n=2664 method=platt fitted=False degenerate=True unreachable=False span=0.00737 auc=0.453 out_max=0.3890)
2026-10-05 08:41:00 [INFO] LEARNING: [Consolidator] 패널티 이력 로드: {'GAP_OPEN': 0.0, 'EXIT_ONLY': 0.0, 'STABLE_TREND': 0.04, 'OTHER': 0.0, 'CLOSE_VOLATILE': 0.0, 'OPEN_VOLATILE': 0.0, 'LUNCH_RECOVERY': 0.0}
2026-10-05 08:41:00 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=SATURATED_MAX
2026-10-05 08:41:07 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=0개 | 교체후보=3개 | CORE안전=⚠️
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 50 | 08:40:51 | 08:41:00 | 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 47 | 08:40:51 | 08:41:00 | 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 15 | 08:40:51 | 08:40:58 | 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 12 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00068 auc=0.478 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 10 | 08:40:51 | 08:40:58 | 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 3 | 08:40:52 | 08:40:57 | 축퇴 감지 — span=0.00028 auc=0.502 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:41:00 | 08:41:00 | 복원한 보정기가 축퇴 상태 — span=0.00737 auc=0.453 out_max=0.3890 (n=2664) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×274

**컴포넌트 상위 15** — `Calibration:1m`×99, `Calibration:30m`×93, `Calibration:3m`×28, `Calibration:10m`×22, `Calibration:5m`×19, `Calibration:15m`×5, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1

### `logs/retrain_intraday_20260812_110059.log` — 4.6KB · 39행 · 최종 11:01:42

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 11:00:59,761 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-12 11:00:59,761 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-12 11:00:59,762 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-12 11:00:59,762 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_3874a3f1.json
2026-08-12 11:01:02,695 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-12 11:01:42,055 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.37s | old_acc=0.4269)
2026-08-12 11:01:42,102 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-12 11:01:42,102 [INFO] LEARNING: [Retrain] 완료 | 39.4초 | 성공=6/6 호라이즌
2026-08-12 11:01:42,103 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 42.3s 데이터=4800행
2026-08-12 11:01:42,104 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_3874a3f1.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260908_100501.log` — 2.8KB · 22행 · 최종 10:05:23

- 형식 평문 · 시각 인식 22행 · INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-08 10:05:01,099 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-08 10:05:01,099 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-08 10:05:01,099 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-08 10:05:01,100 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-08 10:05:01,100 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['5m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b0fc4cbb.json
  …
2026-09-08 10:05:23,756 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-08 10:05:23,757 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-08 10:05:23,757 [INFO] LEARNING: [Retrain] 완료 | 19.7초 | 성공=1/1 호라이즌
2026-09-08 10:05:23,758 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.7s 데이터=4800행
2026-09-08 10:05:23,760 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b0fc4cbb.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/20261005_PROBE.log` — 95B · 1행 · 최종 08:41:10

- 형식 평문 · 시각 인식 1행 · INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-05 08:41:10 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
  …
2026-10-05 08:41:10 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
```

</details>

**채널** — `PROBE`×1

**컴포넌트 상위 15** — `CybosInvestorProbe`×1

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

### 메인 스레드 블로킹 1건 · 최대 4172ms · 5초 초과 0건

상위 — 4172ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261005_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:13 2026-10-05 08:41:13 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4172ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4172 band=INFO since_pipe_s=NA
```

### `logs/20261005_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:43 2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:43 2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:43 2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:43 2026-10-05 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
```

### `logs/20261005_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-05 08:40:51 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261005_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261005_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 12 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261005_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 54 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=31924 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:51:10 [INFO] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 08:51:10 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 1 | 08:56:10 [INFO] 대기 중 | 공휴일·휴장일 — 다음 KRX 거래일 08:45 재개 | 레짐=NEUTRAL | 포지션=FLAT | 08:56:10 |

- 이 로그 생존구간: 08:40 ~ 08:56

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261005_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:40:43 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.451 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:00:02 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 1 | 09:00:02 [INFO] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261003 | 18:32 | 로그 본문 |
| 20261002 | 19:02 | 로그 본문 |
| 20261001 | 15:47 | 로그 본문 |
| 20260930 | 15:47 | 로그 본문 |
| 20260929 | 15:47 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261005** | **08:56** | 로그 본문 |

- 델타 **-411분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · 마지막 갱신 2026-10-04 15:19

최근 헤딩 8개:
```
## 2026-10-01 (MW0601 649차 — 648차 후속 장후 자동조치: F-3 수집기 git 호출 기록)
## 2026-10-02 (MW0601 650차 — 장전 점검)
## 2026-10-02 (MW0601 651차 — 장중 점검)
## 2026-10-02 (MW0601 652차 — 장후 점검)
## 2026-10-02 (MW0601 653차 — 652차 후속 장후 자동조치: F-1 락 자가점검 상충 수정 · G-1 since 시간대)
## 2026-10-02 (MW0601 654차 — 주문 취소율 수집: 호가 흐름 분해 섀도 적재 B1–B5)
## 2026-10-04 (MW0601 655차 — 옵션 흐름(7222) 장 마감 재수집 보강: 8거래일 조용한 실패 복구)
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버: 실시간 분 단위 + 날짜별 복기 · 9842 _P 차분 · 메시아 체인 대체 원천)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
신설(신선도 8 · 백필 6 · 등록 3 · EOD 배선 1). 관련 회귀 14파일 165 passed(424·457·476·479·480·490·537·563·566·595·611·612c·626·655). 실데이터 `option_flow_freshness.py --days 20` → 결손 8일(전부 최신봉 15:34) 정확 검출.

## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버: 실시간 분 단위 + 날짜별 복기 · 9842 _P 차분 · 메시아 체인 대체 원천)

**계기**: 사용자가 claude.ai 에 게시한 10/2 정적 사다리(구조·거리·피터맥점 × 행사가별 옵션 분포)를 「실시간 분 단위 업데이트 + 일별 복기 달력」으로 요청. 이어 9842 당일치(_D) 부재·9/23 이전 OI 공백을 지적.

**결정**:
1. **claude.ai 게시 페이지가 아니라 로컬 서버**(`tools/maekjeom_ladder/server.py`, 127.0.0.1:8765, `MAEKJEOM_LADDER.bat`). 게시 페이지는 이 PC 의 SQLite 를 못 읽는다(`files` 기능은 클라우드 프로젝트 ID 필요 — 로컬 VS Code 세션엔 없음). 표준 라이브러리만(numpy 없음 → BLAS 즉사 경로 무관), 모든 DB `mode=ro`, 쓰기·주문·COM 없음.
2. **456차 준수**: 장중 raw_data.db 접근은 오늘 봉 ts 범위 **증분** 조회 하나(5ms) + 20초 캐시. 개발 중 증분 캐시 키 버그(384봉→2봉)를 잡아 테스트로 고정.
3. 가로축 시각 기준(08:45–15:45 고정) — 장중 봉이 늘어도 차트가 매분 늘지 않는다. 판정 창 미완 터치는 「진행중」(「정거장」과 구분). 10/2 하드코딩(가격축·행사가 범위·「1118」 문구·「09:01 대비」) 제거.
4. **9842 폴더 = `data/db/option_hts`**(사용자 지정, gitignore `data/*`). 파일명 `YYMMDD_D`(당일 순매수)·`YYMMDD_P`(기간 보유). 표시 없는 새 파일은 모드 「미확인」(추측 금지).
5. **새 HTS 내보내기 형식이 바뀌었다**(10/4): 첫·끝 열 투신 → **기관계**, 값 금액(십만원, 소수) → **계약**(정수). 위치로 읽으면 기관 이중 계산·계약을 억원으로 표시 → **머리행 이름으로 열을 찾고, 값이 전부 정수면 계약**으로 판정. 화면 단위도 파일을 따른다.
6. **_D = 당일 _P − 직전 거래일 _P** — 10/2 실측 **2,728/2,728칸 정확 일치**(계약 단위). `derive_9842_daily.py` 가 생성: 진짜 _D 날은 덮어쓰지 않고 **자기검증**에 쓰며 1칸이라도 어긋나면 아무것도 안 쓴다 · 직전 거래일은 KRX 달력, 그날 _P 없으면 건너뜀(여러 날 합이 하루치로 위장 방지) · 생성 표시를 파일 주석과 `_derived_D.json` 에 남김 · 인코딩 후 임시파일→rename(0바이트 _D 가 「진짜」로 오인되는 사고가 실제로 났다). 결과 8/31–10/1, 연쇄 검증 Σ D == P(10/2) − P(8/28) 2,728/2,728.
   ⚠ **8/31–9/10 _D 는 10월물(당시 차근월) 기준** — _P 24개가 전부 10/4 내보내기라 현재가·행사가 열이 동일, 외인 보유 합 1,539(8/28)→29,260(10/2). 그 기간을 9월물 분포로 읽지 말 것.
7. **행사가 OI 대체 원천**: 미륵이 option_book 은 2026-09-23 14:34 시작. 메시아(fuoption) KIS 체인 parquet(2026-08-05~, 5분)을 `import_fuoption_chain.py`(streamlit_env_modern, pyarrow)로 `data/db/option_book_fuo.db` 에 변환(111 상품·일). 벽 정의는 option_book.py 와 같게(γ·OI 최대). 상품별로 **미륵이 ≥20스냅샷이면 미륵이, 아니면 메시아**, 상품마다 자기 시각축. 메시아 지수는 10/2 중첩에서 미륵이와 0.1–0.4pt 일치. 9/22 베이시스 −4.04 는 실제(급락장 선물 선행).

**Why**: 「조용히 그럴듯한 값」 방지 — 형식이 바뀐 파일을 위치로 읽었으면 기관 이중 계산·단위 둔갑이 화면에 그대로 나갔다(계측 4원칙 ①·④). 생성 데이터는 원천과 검증을 남긴다.

**How to apply**: 매일 장후 `_P` 하나만 저장해도 `python tools/maekjeom_ladder/derive_9842_daily.py` 로 그날 `_D` 생성. 메시아 변환은 필요 시 수동. 서버는 세션 프로세스에 붙지 않게 배치로 띄울 것.

**검증**: `tests/test_656_maekjeom_ladder.py` 26건(+537 감사) 28 passed. Edge 헤드리스로 10/2 복기 · 10/2 장중 가정(실시간 칩·「지금」 선·라이브 봉) · 9/22(메시아 원천) 화면 확인.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-10-04 15:19

최근 헤딩 8개:
```
## 2026-10-01 (MW0601 649차 — 648차 후속 장후 자동조치)
## 2026-10-02 (MW0601 650차 — 장전 점검)
## 2026-10-02 (MW0601 651차 — 장중 점검)
## 2026-10-02 (MW0601 652차 — 장후 점검)
## 2026-10-02 (MW0601 653차 — 652차 후속 장후 자동조치)
## 2026-10-02 (MW0601 654차 — 호가 흐름 분해 섀도 적재)
## 2026-10-04 (MW0601 655차 — 옵션 흐름 장 마감 재수집 보강)
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버)
```

미완료 체크박스 **2981건** (끝에서 30건)
```
- [ ] **§11 자동 적신호 해석 교정 메모 (651차)** 매분 루프 커버리지 56.3%·162분 공백은 장중 수집 시점(12:27 KST, 거래일 진행 중)이 분모(09:00~15:10)를 다 못 채워서 생기는 집계 특성이며 실결손이 아님(08:55~15:12 10분 이상 공백 0건으로 확인). 향후 장중 점검 세션은 이 해석을 기본값으로 삼을 …
- [ ] **651-1 (신규, 참고)** 장중 마무리 재확인(12:38 KST) 중 `scripts/probe_cybos_nasdaq_mirror.py`(신규 미추적, 나스닥 선물 Cybos 경로 탐색용, 장중 실행 금지 주석 포함) 발견 — 실행 로그·프로세스 없음, 작성만 됨, 커밋 없음. 이 점검 세션 외 다른 작업이 동시 진행 중이었다는 뜻. …
- [ ] **651-2 (신규, 운영 메모)** `git log --since`에 시간대 미표기 타임스탬프를 쓰면 git이 UTC로 해석해 KST 00:00~09:00 구간 커밋을 놓칠 수 있음을 651차에서 발견(오늘은 그 구간 커밋 0건이라 실질 영향 없음). 다음 점검부터 `--since="<날짜> 00:00:00 +0900"`처럼 시간대 명시 권…
- [ ] **F-1 (지속, P1 — 3번째 표본, 오늘로 통산 세 번째 재현)** 증거수집기 "락 자가점검" 오판정 문구가 오늘 장후에도 재현 여부 재확인 — §2 self-check 줄과 호출별 추적 줄이 이번에도 상충. 가설 단계 → 재현 패턴으로 격상. 수정 계획은 650차와 동일(`scripts/collect_evidence.py:2507~25…
- [ ] **F-3 (지속, P1 — 오늘 하루 3회, 통산 7번째 재현)** `.git/index.lock` 재발 — 장후 자신의 증거수집 중(16:19:28 KST 발생). 나이 34→118→254초 HOLD 거쳐 최종 재확인 시 0.2시간 STALE 확정, `--reclaim`(이름변경 우회)으로 자력 회수 완료. 오늘 세 번 전부 각 세션 안에서…
- [ ] **1-6 (신규, P2)** 저장소 `futures` 루트에 이 프로젝트와 무관한 기형 파일 발견(16:22:18 KST) — 파일명이 `C:\Users\82108\PycharmProjects\Peter\트윗원문\피터리_10월매매_20261002_1002.md`(윈도우 절대경로 전체가 파일명으로 결합). `.claude/skills/peter…
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 `realtime_data.py` 확장 헤더 14개 · `book_flow_bars` 테이블 · `scripts/book_flow_recon.py` · `tests/test_654_book_flow.py`. 상세 `docs/미륵이고도화3/호가깊이/주문취소율_수집가능성_조사_MW0601-20261002.md` §7.
- [ ] **654-1 (다음 거래일 장후, P1)** `python scripts/book_flow_recon.py` — 적재율 ≈100% · 항등식 위반 0 · 체결 커버리지 ≤1.05 · 건수 가용률. SYSTEM 로그에 `[BOOKFLOW][EXT-FAIL]`/`[CNT-INVALID]` 경고 여부. HOGA 로그 `[BOOKFLOW]` 줄의 `unmatched`·`dropped`·`broken` 크기.
- [ ] **654-2 (다음 거래일 장후, P1)** 부하 — `[PipePerf]` 분포를 654차 이전 5거래일과 비교. 악화 시 `_book_flow_step` 비활성 스위치부터 넣을 것(현재 없음).
- [ ] **654-3 (섀도 10거래일 후)** 「두꺼운 매도벽(`book_ask_max` 상위) 감소분의 `ask_exec_qty` vs `ask_cancel_qty_lb` 비중 + 이후 가격 경로」 — 표본 보기 전 판정 기준 사전등록.
- [ ] **654-4 (보류)** B6 일반선물 `A016C` 호가 추가 구독 — 654-2 부하 확인 후 판단. 미니는 단당 1–2계약이라 건수 정보가 얇다.
- [ ] **654-5 (별건, P2)** `test_457::test_db_fallback_columns_have_measured_flag` 실패 — `dashboard/main_dashboard.py → peter_paste` INSERT의 `or ''`/`or 0.0` 폴백(632차 커밋분). 플래그 추가 또는 근거와 함께 `_DB_FALLBACK_PINNED` 등록.

## 2026-10-04 (MW0601 655차 — 옵션 흐름 장 마감 재수집 보강)

- [x] **655-0 완료** 7222 장후 재수집 8거래일 실패 원인(예약작업 RunLevel Highest × Cybos 비승격) 수정 · 재등록(Limited · 16:20) · 백필 로그/진단/마감판정/날짜거부/휴장일 · `[OptionFlowFresh]` EOD 배선 · `tests/test_655_*` 18건.
- [ ] **655-1 (10/6 화 장후, P1)** 첫 실거래일 확인 — `(Get-ScheduledTaskInfo -TaskName Mireuk_OptionFlowBackfill_1605 -TaskPath '\Mireuk\').LastTaskResult` = 0 · `logs\20261006_OPTION_BACKFILL.log` 의 「마감 구간 확보 — 옵션 최신봉 16:0x」 · DB `max(bar_time)` ≥ 15:45 · 15:34 행이 HTS 와 일치하는지 HTS [7222] 1개 상품으로 대조.
- [ ] **655-2 (10/7 수 EOD)** `[OptionFlowFresh]` 가 10/6 을 「확보」로 판정하는지 EOD 로그 확인(9/21–10/2 8일은 영구 결손으로 계속 뜬다 — `DEFAULT_DAYS=10` 창을 벗어나면 사라진다).
- [ ] **655-3 (10/8 목 만기일)** 만기일 7222 마지막 행 시각 실측 → `CLOSE_OK_EXPIRY`(현재 15:20 보수값) 확정. 근월물 만기 후에도 먼스리(E/F)·위클리 상품이 15:45 까지 찍히면 만기일 기준을 15:40 으로 올릴 것.
- [ ] **655-4 (MW0602, 선택)** 이 커밋 체리픽 시 그 PC 는 BROKER=creon → Highest 유지. 재등록은 불필요하나 시각 16:20 을 원하면 관리자 PowerShell 에서 `TASK_OPTION_BACKFILL_INSTALL.bat` 재실행.

## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버)

- [x] **656-0 완료** 로컬 서버(실시간·달력) · 9842 머리행/단위 파서 · `_P` 차분 `_D` 생성 · 메시아 체인 OI 대체 원천 · `tests/test_656_*`.
- [ ] **656-1 (10/6 화 장중)** 실제 장중 실시간 갱신 확인 — 상태칩 「다음 n초」·「지금」 선 · `[PipePerf]` 에 서버 영향 없는지(raw_data.db 증분 조회 20초 1회).
- [ ] **656-2 (10/8 만기일)** 목위클리 부재·먼스리 D0 화면 · 메시아 목위클리 만기 표기(9/24 vs 실제 9/23 — 추석 이동분) 같은 원천 표기 차이 정리 여부.
- [ ] **656-3 (선택)** 장중 베이시스 변동이 큰 날(9/22 −4pt) 행사가 위치를 하루 중앙값 대신 **스냅샷 시각별 베이시스**로 옮길지.
- [ ] **656-4 (선택)** 9842 장중 30분 내보내기(`YYMMDD_HHMM_D`) 인식 → 행사가 × 주체 × 시간 히트맵.

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

### `data/heartbeat_MW0601_20261005.json` — 245B · 10-05 08:59:40
```json
{
 "pid": 31924,
 "written_at": "2026-10-05T09:00:40",
 "beat_epoch": 1791158440.0262454,
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

- 파일 최종 기록: **10-05 08:41:10**

| 키 | 값 | 수집 대상일(2026-10-05)과 일치 |
|---|---|---|
| `date` | 2026-10-05 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: — PreRetrain 로그 없음 — **미측정** (08:55 이전 수집이거나 그날 미기동)

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **(없음)** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **행 없음** — 그날 파이프라인이 한 번도 안 돌았다 |
| `raw_candles` 당일 행수 | 0 |
| `session_bars` 당일 행수 | 0 (기대 411) |

- 라이브 로그 대조: `logs/20261005_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 31924: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:46 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 31924 | 08:40:46 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 192개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` | 91.4KB | 10-02 17:29 |
| `docs/정기점검/매일점검/_tmp_append_post_20261002.md` | 0B | 10-02 16:31 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_post.md` | 85.1KB | 10-02 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_intra.md` | 73.4KB | 10-02 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_pre.md` | 65.2KB | 10-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20261001-점검리포트.md` | 74.1KB | 10-01 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20261001_post.md` | 89.7KB | 10-01 16:19 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261001.md` | 0B | 10-01 12:44 |

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

1. (관측) 휴장일 — 거래일 전제 적신호(당일 파일 0개·매분 루프 커버리지·15:10 청산 흔적·완료 마커·진입 0건·장후 조기종료·장중 로그 침묵·dev_memory 갱신·상태 파일)를 생략했다. 인프라 적신호는 그대로 본다
2. `.git/index.lock` 존재 (0바이트 · 0.4분 · git 프로세스 0) — 실행 중인 git 일 수 있으니 **지우지 말 것**. 몇 분 뒤에도 남아 있으면 재판정
3. (관측) 휴장일인데 미륵이 기동 **1회** — 의도한 점검·리허설인지 확인 (적신호 아님)
4. `logs/20261005_LEARNING.log`: **축퇴** 8건(표본)
5. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
6. 미커밋 변경 55건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`
7. 🔴 **이 수집 실행이 `.git/index.lock` 을 남겼다** — 시작 시점에는 없었다(생긴 구간은 §2 「git 호출 기록」 참조 — 653차). 방치하면 그날 dev_memory·리포트가 커밋되지 않은 채로 끝난다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261005*.log` (Windows) / `grep 강제청산 logs/*20261005*.log`*