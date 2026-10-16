# 미륵이 증거 다이제스트 — 2026-10-06 / INTRA

- 생성 2026-10-06 12:31:40 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01jvcm2uod99iqkfxkpkwgsw/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261006` · `2026-10-06` · `261006` · `1006`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **27개** 파일 · 27개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261006.log` | 136B | 10-06 07:22 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261006.log` | 125B | 10-06 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261006.log` | 140B | 10-06 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261006.json` | 244B | 10-06 12:31 |
| `launcher_{DATE}_084000_32243.log` | 1 | `logs/Mireuk_batch/launcher_20261006_084000_32243.log` | 1.2MB | 10-06 12:30 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261006.log` | 14.3KB | 10-06 12:16 |
| `retrain_intraday_20260702_{DATE}00.log` | 1 | `logs/retrain_intraday_20260702_100600.log` | 4.6KB | 07-02 10:06 |
| `retrain_intraday_20260703_{DATE}00.log` | 1 | `logs/retrain_intraday_20260703_100600.log` | 4.6KB | 07-03 10:06 |
| `retrain_intraday_20260706_{DATE}58.log` | 1 | `logs/retrain_intraday_20260706_100658.log` | 4.6KB | 07-06 10:07 |
| `retrain_intraday_20260812_{DATE}59.log` | 1 | `logs/retrain_intraday_20260812_100659.log` | 4.6KB | 08-12 10:07 |
| `retrain_intraday_{DATE}_105316.log` | 1 | `logs/retrain_intraday_20261006_105316.log` | 5.7KB | 10-06 10:54 |
| `retrain_intraday_{DATE}_115944.log` | 1 | `logs/retrain_intraday_20261006_115944.log` | 1.5KB | 10-06 11:59 |
| `{DATE}_0900_D.xls` | 1 | `data/db/option_hts/261006_0900_D.xls` | 480.2KB | 10-06 09:02 |
| `{DATE}_0930_D.xls` | 1 | `data/db/option_hts/261006_0930_D.xls` | 480.4KB | 10-06 09:28 |
| `{DATE}_1230_D.xls` | 1 | `data/db/option_hts/261006_1230_D.xls` | 480.8KB | 10-06 12:30 |
| `{DATE}_DATA.log` | 1 | `logs/20261006_DATA.log` | 237.3KB | 10-06 12:31 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261006_DEBUG.log` | 131.2KB | 10-06 12:31 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261006_HEALTH.log` | 2.7KB | 10-06 12:28 |
| `{DATE}_HOGA.log` | 1 | `logs/20261006_HOGA.log` | 28.6MB | 10-06 12:31 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261006_LEARNING.log` | 267.6KB | 10-06 12:31 |
| `{DATE}_MICRO.log` | 1 | `logs/20261006_MICRO.log` | 556.3KB | 10-06 12:31 |
| `{DATE}_OPTION_BACKFILL.log` | 1 | `logs/20261006_OPTION_BACKFILL.log` | 372B | 10-06 07:24 |
| `{DATE}_PROBE.log` | 1 | `logs/20261006_PROBE.log` | 84.2KB | 10-06 12:30 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261006_SIGNAL.log` | 347.5KB | 10-06 12:31 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261006_SYSTEM.log` | 532.1KB | 10-06 12:31 |
| `{DATE}_TRADE.log` | 1 | `logs/20261006_TRADE.log` | 4.1KB | 10-06 11:59 |
| `{DATE}_WARN.log` | 1 | `logs/20261006_WARN.log` | 209.3KB | 10-06 12:31 |

## 2. 코드·커밋 상태

- HEAD `84bb350` · 브랜치 `v9-dev` · 미커밋 61건 · 실질 변경 **미측정**(git diff 실패) — 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat` · 🔴 **인덱스락 잔존** 0바이트 · 0.0시간 · git 프로세스 0개 (판정 보류 — 3중 조건 미충족)
  - 락 주인 진단 `[ORPHAN]` 쥔 git 프로세스 없음 - 중단/강제종료된 명령의 잔재(갈래 1) (락 mtime 2026-10-06 03:32:29)
  - 🔴 **이 수집 실행 중 `.git/index.lock` 이 생겨 지금도 남아 있다** (시작 시점에는 없었다) — `run_git` 호출 구간(`git diff --numstat` → timeout)에 생겼다(동시 발생 — 인과 미확정). `scripts/git_lock_guard.py --check` 로 판정 후 회수할 것
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
… 외 21건
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

_본문 미열람(설정): `20261006_HOGA.log` 28.6MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/22개 (중요도순). 제외: `retrain_intraday_20260706_100658.log`, `retrain_intraday_20260702_100600.log`, `retrain_intraday_20260812_100659.log`, `retrain_intraday_20261006_115944.log`, `20261006_MICRO.log`, `20261006_DATA.log`, `20261006_PROBE.log`, `launcher_20261006_084000_32243.log`_

### `logs/20261006_TRADE.log` — 4.1KB · 25행 · 최종 11:59:41

- 형식 평문 · 시각 인식 25행 · INFO=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-06 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-06 09:57:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-06 10:23:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-06 10:24:02 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-10-06 11:32:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-06 11:35:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-06 11:36:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-06 11:59:37 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-06 11:59:41 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×25

**컴포넌트 상위 15** — `Sizer`×15, `Position`×3, `ProfitGuard`×3, `모드필터 차단`×2, `JointGateBlock 차단`×2

### `logs/20261006_WARN.log` — 209.3KB · 1026행 · 최종 12:31:32

- 형식 평문 · 시각 인식 1002행 · CRITICAL=1, ERROR=1, WARNING=1000, PLAIN=24

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-06 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-10-06 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=333044256
2026-10-06 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-06 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-06 12:32:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 81.2ms | size=1955x1124 candles=227 grid=24.7 spans=0.1 candles=12.0 dir=0.7 regime=4.3 markers=37.5 axes=0.6 cross=0.0 | slow_cnt=21 total_cnt=21 overlay_cnt=147
2026-10-06 12:32:24 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 75.3ms | size=1955x1124 candles=227 grid=22.7 spans=0.0 candles=11.6 dir=0.7 regime=3.7 markers=34.6 axes=0.6 cross=0.0 | slow_cnt=22 total_cnt=22 overlay_cnt=160
2026-10-06 12:32:34 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 83.3ms | size=1955x1124 candles=227 grid=25.7 spans=0.0 candles=11.8 dir=1.1 regime=4.0 markers=38.0 axes=1.2 cross=0.0 | slow_cnt=23 total_cnt=23 overlay_cnt=181
2026-10-06 12:32:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.5ms | size=1955x1124 candles=227 grid=23.6 spans=0.0 candles=11.5 dir=0.7 regime=4.0 markers=36.5 axes=0.7 cross=0.0 | slow_cnt=24 total_cnt=24 overlay_cnt=201
2026-10-06 12:32:45 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 82.8ms | size=1955x1124 candles=227 grid=24.7 spans=0.0 candles=12.8 dir=0.8 regime=8.4 markers=33.5 axes=1.2 cross=0.0 | slow_cnt=25 total_cnt=25 overlay_cnt=203
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 09:03:06 | 09:03:06 | level=CRITICAL degraded=OFF | latency=6050ms | quality=1.00 | cache_age=52s | exceptions_10m=0 |
| ERROR | `LiveDBG` | 1 | 09:03:18 | 09:03:18 | _tick_header 간격 18266ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=18266 band=ALERT since_pipe_s=0.3 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-10-06 09:03:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6050ms | quality=1.00 | cache_age=52s | exceptions_10m=0
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-10-06 09:03:18 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 18266ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=18266 band=ALERT since_pipe_s=0.3
```

</details>

**WARNING — 태그 18종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 789 | 08:49:59 | 12:32:45 | paintEvent slow 31.0ms | size=1955x1125 candles=5 grid=11.2 spans=0.5 candles=13.2 dir=0.0 regime=0.1 markers=0.0 axes=3.2 cross=0.0 | slow_cnt=1 total_cnt=1 overlay_cnt=0 |
| `LiveDBG` | 93 | 08:41:08 | 12:30:45 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 43 | 08:41:18 | 12:31:45 | 그리기 59.2ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 856x1001 |
| `PipePerf` | 10 | 09:00:02 | 09:05:02 | total=2089ms | S0=7ms S1=14ms S2=0ms S3=0ms S4=133ms S5=1114ms S6=749ms S7=49ms S8=23ms |
| `CB⑤` | 10 | 09:00:02 | 09:05:02 | 파이프라인 2089ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 10 | 09:05:01 | 12:30:00 | 5분 누적 수익률 -0.763% (임계 ±0.233%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 9 | 09:00:02 | 12:27:00 | level=WARNING degraded=OFF | latency=2089ms | quality=1.00 | cache_age=52s | exceptions_10m=0 |
| `EffectReports` | 9 | 09:32:32 | 12:01:02 | run_microstructure_ab_backtest.py rc=3221225477 stdout= stderr= |
| `출처축` | 6 | 08:41:09 | 11:59:44 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `MainStallTrace` | 5 | 08:58:18 | 12:16:21 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20261006.log |
| `HealthPolicy` | 5 | 09:01:01 | 09:06:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2089ms quality=1.00 cache=0s exc10m=0) | cause=S5(1114ms) |
| `CB③-P4` | 2 | 10:47:00 | 10:47:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=6.7%) |

**채널** — `SYSTEM`×992, `HEALTH`×10

**컴포넌트 상위 15** — `ChartDBG`×789, `LiveDBG`×94, `OptionFlowChart`×43, `-`×24, `PipePerf`×10, `Health`×10, `CB⑤`×10, `ScalerRefresh`×10, `EffectReports`×9, `출처축`×6, `MainStallTrace`×5, `HealthPolicy`×5, `CB③-P4`×2, `OptionChain`×2, `RESTART`×2

### `logs/20261006_SYSTEM.log` — 532.1KB · 3692행 · 최종 12:31:35

- 형식 평문 · 시각 인식 3681행 · INFO=3681, PLAIN=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=11972 | 행감지=30s all_threads=True
2026-10-06 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-06 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-06 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-06 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-06 12:32:45 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+1242,foreign:-2603,institution:+1404} amt_mn={individual:+344580,foreign:-719267,institution:+386486}
2026-10-06 12:32:45 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+1242,foreign:-2603,institution:+1404} amt_mn={individual:+344580,foreign:-719267,institution:+386486}
2026-10-06 12:32:45 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+57087 nonarb=-854826
2026-10-06 12:32:45 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+57087 nonarb=-854826
2026-10-06 12:32:51 [INFO] SYSTEM: [CybosRT-TICK] #6100 code=A056A raw_time=123251 parsed=12:32:51 price=1096.16 vol=1 bid1=1096.14 ask1=1096.20 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×3681

**컴포넌트 상위 15** — `CybosInvestorRaw`×848, `CybosRT-TICK`×634, `PumpGuard`×282, `TickUI`×226, `CybosRT-ROLLOVER`×226, `BAR-CLOSE`×226, `CVD-ANCHOR`×226, `S6Detail`×212, `PipePerf`×212, `System`×73, `CybosSub`×63, `MicroRegime`×50, `OptionChain`×48, `OptionBook`×43, `RegimeFingerprint`×39

### `logs/20261006_SIGNAL.log` — 347.5KB · 3025행 · 최종 12:31:00

- 형식 평문 · 시각 인식 3025행 · WARNING=1309, INFO=1716

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.441
  …
2026-10-06 12:32:00 [INFO] SIGNAL: [MetaGate] 편향패널티: dir=1 buf=15 pen=0.017 blended 0.325→0.308
2026-10-06 12:32:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-10-06 12:32:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=53.6% grade=X regime=NEUTRAL
2026-10-06 12:32:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=53.6% grade=X micro=추세장
2026-10-06 12:32:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.536<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 978 | 09:00:02 | 12:30:01 | 1m 'macro_vix' scale=0.0125 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 108 | 09:00:00 | 12:02:00 | ts=08:59 horizon=1m age=1m max_z=+7.65(institution_futures_net) extreme=6 adj=6 |
| `Model` | 94 | 09:00:00 | 12:00:00 | 1m 극단 z-score 6개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `WeightCollapse` | 48 | 09:06:00 | 12:31:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Checklist` | 46 | 09:11:00 | 12:21:00 | 신뢰도 미달 37.9% < 41.1% → 강제 X등급 |
| `ScalerRefresh` | 30 | 08:45:09 | 08:59:02 | 1m CORE 'cvd_divergence' raw_std≈0(0.0215) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 3 | 09:59:01 | 11:41:01 | 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 2 | 11:07:00 | 11:13:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×3025

**컴포넌트 상위 15** — `ScalerFloor`×996, `SIGNAL`×424, `Ensemble`×214, `FQAdj`×202, `ZeroDiag`×189, `MetaGate`×155, `Model`×118, `ScalerMonitor`×108, `Checklist`×81, `ScalerRefresh`×58, `ATR-Horizon`×57, `MicroRegime`×50, `WeightCollapse`×48, `ToxicityGate`×46, `차단`×45

### `logs/20261006_LEARNING.log` — 267.6KB · 2131행 · 최종 12:31:00

- 형식 평문 · 시각 인식 2131행 · WARNING=400, INFO=1731

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
  …
2026-10-06 12:32:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0393% buf_n=20 nonzero=20 prev_p=1094.88 cur_p=1095.26
2026-10-06 12:32:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=33.3% UP)
2026-10-06 12:32:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=68.2% 예측=FL 실제=DN)
2026-10-06 12:32:00 [INFO] LEARNING: [Bias⚠] 3m 적중=48%(10/21) UP=1 DN=0 FL=20 [FL편향⚠ 95%]
2026-10-06 12:32:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=0.0%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 140 | 08:40:50 | 11:59:36 | 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 137 | 08:40:50 | 11:59:36 | 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 50 | 08:40:50 | 11:59:35 | 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 34 | 08:40:51 | 11:59:36 | 축퇴 감지 — span=0.00068 auc=0.478 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 28 | 08:40:50 | 11:59:35 | 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 8 | 08:40:51 | 11:59:34 | 축퇴 감지 — span=0.00028 auc=0.502 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 3 | 08:40:59 | 11:59:37 | 복원한 보정기가 축퇴 상태 — span=0.00737 auc=0.453 out_max=0.3890 (n=2664) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×2131

**컴포넌트 상위 15** — `LEARNING`×641, `Calibration:30m`×276, `Calibration:1m`×271, `SGD`×212, `sigma`×173, `Calibration:3m`×95, `Bias⚠`×95, `Bias`×77, `Calibration:10m`×62, `OnlineLearner`×57, `Calibration:5m`×53, `MetaConf`×35, `ScalerWarmup`×28, `Calibration:15m`×13, `BiasReset`×8

### `logs/20261006_HEALTH.log` — 2.7KB · 20행 · 최종 12:28:00

- 형식 평문 · 시각 인식 20행 · CRITICAL=1, WARNING=9, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2089ms | quality=1.00 | cache_age=52s | exceptions_10m=0
2026-10-06 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=959ms | quality=1.00 | cache_age=111s | exceptions_10m=0
2026-10-06 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1015ms | quality=0.88 | cache_age=171s | exceptions_10m=0
2026-10-06 09:03:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6050ms | quality=1.00 | cache_age=52s | exceptions_10m=0
2026-10-06 09:04:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1056ms | quality=1.00 | cache_age=107s | exceptions_10m=0
  …
2026-10-06 11:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=411ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-10-06 11:49:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=274ms | quality=1.00 | cache_age=56s | exceptions_10m=0
2026-10-06 12:19:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 303ms (표본 20분)
2026-10-06 12:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=263ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-10-06 12:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=224ms | quality=1.00 | cache_age=58s | exceptions_10m=0
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 09:03:06 | 09:03:06 | level=CRITICAL degraded=OFF | latency=6050ms | quality=1.00 | cache_age=52s | exceptions_10m=0 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-10-06 09:03:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6050ms | quality=1.00 | cache_age=52s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:02 | 12:27:00 | level=WARNING degraded=OFF | latency=2089ms | quality=1.00 | cache_age=52s | exceptions_10m=0 |

**채널** — `HEALTH`×20

**컴포넌트 상위 15** — `Health`×17, `HealthTrend`×3

### `logs/retrain_intraday_20261006_105316.log` — 5.7KB · 43행 · 최종 10:54:01

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-06 10:53:16,544 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-06 10:53:16,544 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-06 10:53:16,544 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-06 10:53:16,544 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-06 10:53:16,544 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d4368ae2.json
  …
2026-10-06 10:54:01,715 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-06 10:54:01,716 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-06 10:54:01,716 [INFO] LEARNING: [Retrain] 완료 | 41.5초 | 성공=6/6 호라이즌
2026-10-06 10:54:01,717 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 45.2s 데이터=4800행
2026-10-06 10:54:01,720 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d4368ae2.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:53:29 | 10:53:29 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 21889/44472 제외 (418차 결정 1) — 남은 22583행 |
| `UnitMismatch` | 1 | 10:53:29 | 10:53:29 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/22583행 제외 (559차 P1'-2) — 남은 21137행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

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

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 45 |
| 사이저 호출(`[Sizer]`) | 15 |

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×15

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×9, `conf=0.6 regime=0.8 safe=1.00`×6

### 차단 사유 45건 · 30종

| 건수 | 사유 |
|---|---|
| 12 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 2 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — 미통과 항목: 3_vwap |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.9pt > ATR×5.0=5.8pt (시가=1116.42 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.0pt > ATR×5.0=6.0pt (시가=1116.42 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.5pt > ATR×5.0=6.1pt (시가=1116.42 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.8pt > ATR×5.0=6.0pt (시가=1116.42 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.9pt > ATR×5.0=6.5pt (시가=1116.42 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.1pt > ATR×5.0=6.3pt (시가=1116.42 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.1pt > ATR×5.0=6.4pt (시가=1116.42 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.5pt > ATR×5.0=6.4pt (시가=1116.42 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.2pt > ATR×5.0=6.6pt (시가=1116.42 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.9pt > ATR×5.0=6.3pt (시가=1116.42 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 7_prev_bar |

**체크리스트 미통과 항목 누적** — `2_confidence`×12, `3_vwap`×8, `6_foreign`×7, `5_ofi`×4, `7_prev_bar`×4, `4_cvd`×3, `11_countertrend`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 17건 · 최대 18266ms · 5초 초과 5건

상위 — 18266ms, 10781ms, 6360ms, 6094ms, 5469ms, 4937ms, 4688ms, 4594ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:58:18 | 6360ms | **미측정** | — |
| 09:00:04 | 5469ms | 2089ms | **3380ms (62%)** |
| 09:03:18 | 18266ms | 6050ms | **12216ms (67%)** |
| 09:05:10 | 10781ms | 2281ms | **8500ms (79%)** |
| 12:16:21 | 6094ms | 316ms | **5778ms (95%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261006_WARN.log`
```
--- level=CRITICAL ×1(표본)
09:03:06 2026-10-06 09:03:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6050ms | quality=1.00 | cache_age=52s | exceptions_10m=0
--- 메인 스레드 블로킹 ×8(표본)
08:41:13 2026-10-06 08:41:13 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4594 band=INFO since_pipe_s=NA
08:50:04 2026-10-06 08:50:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4937ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4937 band=INFO since_pipe_s=NA
08:50:09 2026-10-06 08:50:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3375ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3375 band=INFO since_pipe_s=NA
08:58:18 2026-10-06 08:58:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6360ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6360 band=WARN since_pipe_s=NA
```

### `logs/20261006_SYSTEM.log`
```
--- ConstOut ×4(표본)
09:59:01 2026-10-06 09:59:01 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5083) | 앙상블 제외는 유지
10:55:00 2026-10-06 10:55:00 [INFO] SYSTEM: [DynMC] ConstOut 고착 conf 제외: [0.85] → 300건 제거 (잔여 1634건)
11:33:00 2026-10-06 11:33:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.6570) | 앙상블 제외는 유지
11:41:01 2026-10-06 11:41:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.7444) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-10-06 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:01 2026-10-06 09:05:01 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-10-06 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:17:00 2026-10-06 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20261006_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:59:01 2026-10-06 09:59:01 [INFO] SIGNAL: [ConstOutShadow] 5m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1560 dir=-1)
09:59:01 2026-10-06 09:59:01 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:00:00 2026-10-06 10:00:00 [INFO] SIGNAL: [ConstOutShadow] 5m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1560 dir=-1)
10:01:00 2026-10-06 10:01:00 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:06:00 2026-10-06 09:06:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:07:00 2026-10-06 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:07:00 2026-10-06 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-10-06 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
08:40:42 2026-10-06 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
--- 안전망 ×8(표본)
09:06:00 2026-10-06 09:06:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-10-06 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-10-06 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (3연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-06 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
```

### `logs/20261006_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00017 auc=0.475 out_max=0.3876 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00158 auc=0.393 out_max=0.4759 (기준 auc<0.53 and span<0.020, 기저율=0.4750 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00046 auc=0.432 out_max=0.3627 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-06 08:40:50 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00009 auc=0.514 out_max=0.3251 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
```

### `logs/20261006_HEALTH.log`
```
--- level=CRITICAL ×1(표본)
09:03:06 2026-10-06 09:03:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6050ms | quality=1.00 | cache_age=52s | exceptions_10m=0
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261006_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 1 | 09:57:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |
| 12:00 | 장중 중간점 | 2 | 11:59:37 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 11:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261006_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 12 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 54 | 08:49:59 [WARNING] paintEvent slow 31.0ms | size=1955x1125 candles=5 grid=11.2 spans=0.5 candles=13.2 dir=0.0 regime=0.1 markers… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 116 | 08:55:41 [WARNING] paintEvent slow 35.4ms | size=1955x1124 candles=11 grid=12.1 spans=0.0 candles=0.4 dir=0.0 regime=0.0 markers… |
| 10:00 | 장중 초반 | 89 | 09:54:02 [WARNING] paintEvent slow 72.4ms | size=1955x1124 candles=70 grid=21.4 spans=0.0 candles=3.0 dir=0.2 regime=7.6 markers… |
| 12:00 | 장중 중간점 | 24 | 11:54:25 [WARNING] run_microstructure_ab_backtest.py rc=1 stdout= stderr=, in <module> |

- 이 로그 생존구간: 08:41 ~ 12:32

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261006_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 95 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=11972 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:01 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 191 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 218 | 09:54:02 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 278 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:32

**매분 루프 커버리지 09:00~15:10: 213/371분 (57.4%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:33 | 15:10 | 158 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261006_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0215) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 161 | 08:50:04 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 315 | 08:55:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 176 | 09:56:00 [WARNING] 신뢰도 미달 40.9% < 41.1% → 강제 X등급 |
| 12:00 | 장중 중간점 | 282 | 11:54:00 [WARNING] 1m 'macro_vix' scale=0.0197 → floor=0.10 적용 (z-score 폭발 방지) |

- 이 로그 생존구간: 08:40 ~ 12:32

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
| **오늘 20261006** | **12:32** | 로그 본문 |

- 델타 **-195분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-02 (MW0601 653차 — 652차 후속 장후 자동조치: F-1 락 자가점검 상충 수정 · G-1 since 시간대)
## 2026-10-02 (MW0601 654차 — 주문 취소율 수집: 호가 흐름 분해 섀도 적재 B1–B5)
## 2026-10-04 (MW0601 655차 — 옵션 흐름(7222) 장 마감 재수집 보강: 8거래일 조용한 실패 복구)
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버: 실시간 분 단위 + 날짜별 복기 · 9842 _P 차분 · 메시아 체인 대체 원천)
## 2026-10-05 (MW0601 657차 — 장전 점검)
## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)
## 2026-10-06 (MW0601 659차 — 장전 점검)
### 2026-10-06 (MW0601 659차 후속 — 장전 세션 내 인덱스락 해소)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
344행에 "F-3: 문서 1줄 수정" **결정은 이미 났으나 실제 커밋에는 반영된 적이 없음**을 이번에 재확인(함정① 반대방향 — "결정됐다고 실행된 것은 아니다"). ⑦ 리포 루트의 기형 파일(`C:\Users\82108\PycharmProjects\Peter\트윗원문\피터리_10월매매_20261002_1002.md`, 윈도우 절대경로가 파일명으로 들어간 것) 10/2 이후 변동 없이 미커밋 지속(O-u5 계승). ⑧ 설정 불변식 전체 일치(불일치 0건), 차단 게이트 40개 중 9개 꺼짐 전부 기록된 결정과 일치. CB②(모의한정 예외)는 2026-09-02(519차)에 이미 복원 완료, 재검토 기한 초과 아님. ⑨ 미커밋 60건(미분류 50·삭제 6·수정 4) — `git diff --numstat` 타임아웃으로 실질변경/EOL파생 분해는 이번에도 못 냄(②와 동일 원인). ⑩ 앱 저장 스킬 사본이 `rev: 2026-08-26e`로 저장소 정본(`rev: 2026-09-07`, 538차)보다 낡음을 발견 — 이번 점검은 정본 기준으로 수행(둘 다 Read로 직접 대조).

**원인**: ①⑧은 정상(실거래일 개시 상태 양호). ②⑨는 코웍 샌드박스가 윈도우 저장소를 마운트 경유로 보는 구조에서 `git diff --numstat`이 느린 것이 반복 원인으로 추정(미확정 — 호스트 성능과 diff 대상 건수 양쪽 다 원인일 수 있음). ③은 원인 미상(8일째 동일 스택, 특정 위젯 식별까지는 안 됨). ④는 "매일 아침 세션 상태가 날짜 전환되며 어제 값이 안 남는 설계"인지 "SessionStateDrop(606-2) 변종"인지 표본 1건으로 미확정. ⑤⑥⑦은 전부 운영 위생 문제로 실제 매매 로직과 무관.

**결정**: 1-1(인덱스락)은 판정보류 유지, 지우지 않음 — 장중 세션이 재판정. 1-2(부팅 access violation)는 8번째 관측일로 지속만 갱신, 신규 Fix 미등록(함정①). 1-3(문서제목)·1-4(joblib)·1-5(기형파일)는 전부 지속 확인만, 장후에 F-2~F-4로 적용 예정(장전·장중 커밋 금지 규약). O-p1(session_state 키 공백)은 신규 관측으로만 등록, 결함 단정 안 함 — 오늘 밤 장후가 판정. 앱 저장 스킬은 정본으로 갱신 필요(사용자 조치 1번).

**Why**: 313차 원칙(표본 부족 시 확정 금지) 적용 — O-p1·1-1(인덱스락 판정보류) 모두 확정 결론 내지 않음. 함정①(판정≠결정) 양방향 적용 — 1-2~1-5는 기존 항목 재등록 금지, 1-4는 "결정 났는데 미반영"이라는 반대 방향 사례로 명시. 함정④(ERROR 아닌 INFO/WARNING 판독) 적용 — §5 거래일 요약(진입·청산·차단·사이저 전부 0건, 아직 장 시작 직후라 정상) 확인 완료.

**How to apply**: F-1(2-F-1) — `collect_evidence.py`의 git diff 호출부를 수정해 타임아웃 시 2차 변형 호출을 생략하거나 코웍 마운트 환경에서 `--numstat`을 건너뛰도록. F-2 — `재시작_종료사유분류_봉결손_구현계획_20260922.md` 2행에 "재" 1글자 추가. F-3 — `CLAUDE.md:24` "joblib 1.1.1"→"1.1.0". F-4 — 기형 파일을 올바른 위치로 이동 또는 삭제. 전부 장후 적용 권고(장전 규약상 금지).

**검증**: 1-1은 다음 점검(장중)에서 `git_lock_guard.py --check` 재실행. 1-2는 다음 거래일 9번째 관측 여부. O-p1은 오늘 밤 EOD 이후 `session_state.json` 재확인(두 키가 2026-10-06으로 채워지는지). F-2~F-4는 장후 적용 후 `git status`로 반영 확인.

**추가**: 오늘 신규 커밋 0건. 앱 저장 스킬 사본(`rev: 2026-08-26e`)이 정본(`rev: 2026-09-07`)보다 낡아 사본 드리프트 — 이번 점검은 정본으로 수행했고, 다음 기회에 `save_skill overwrite:true`로 이 PC 사본을 갱신할 것(658-1 계열과 별개 TODO로 NEXT_TODO에 등록).

### 2026-10-06 (MW0601 659차 후속 — 장전 세션 내 인덱스락 해소)

09:05까지 `git_lock_guard.py --check`가 HOLD(판정보류, 나이 400초 ≤ 임계 600초)였던 인덱스락이 09:11 재판정에서 STALE(나이 12분, 임계 10분 초과)로 바뀌어 `--reclaim` 실행 — 삭제는 `Operation not permitted`로 거부됐으나 스크립트의 rename 우회로 회수 성공(`index.lock` → `index.lock.stale_20261006001310_6`). 재확인 결과 `OK index.lock 없음` — 저장소 커밋 가능 상태로 복귀. 1-1·O-p2는 장전 세션 안에서 해소 처리, 장중으로 이월하지 않음. 이름변경된 T2 잔재는 2건(10/5분 24.2시간 + 10/6분 0.2시간)으로 648-2에 누적.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-02 (MW0601 652차 — 장후 점검)
## 2026-10-02 (MW0601 653차 — 652차 후속 장후 자동조치)
## 2026-10-02 (MW0601 654차 — 호가 흐름 분해 섀도 적재)
## 2026-10-04 (MW0601 655차 — 옵션 흐름 장 마감 재수집 보강)
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버)
## 2026-10-05 (MW0601 657차 — 장전 점검, 휴장일)
## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)
## 2026-10-06 (MW0601 659차 — 장전 점검)
```

미완료 체크박스 **2996건** (끝에서 30건)
```
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
- [ ] **659-1 (P1, 장후 적용)** `collect_evidence.py`의 `git diff --numstat` 타임아웃 2회 연속 재발(인덱스락 유발) — 두 번째 변형 호출 생략 또는 코웍 마운트 환경에서 numstat 스킵 분기 추가.
- [ ] **659-2 (P2, 장후 적용)** `재시작_종료사유분류_봉결손_구현계획_20260922.md` 2행 "재" 1글자 추가(633-1 종결).
- [ ] **659-3 (P2, 장후 적용)** `CLAUDE.md:24` joblib "1.1.1"→"1.1.0" 정정 — ⚠ 과거(538차 F-3)에도 "결정"만 나고 실제 커밋 안 됨, 이번엔 적용 후 커밋까지 확인할 것.
- [ ] **659-4 (P2, 장후 적용)** 리포 루트 기형 파일(`C:\Users\82108\PycharmProjects\Peter\트윗원문\피터리_10월매매_20261002_1002.md`) 올바른 위치로 이동/삭제.
- [ ] **659-5 (P2, 선택)** 이 PC 앱 저장 스킬(`mireuk-daily-check`) 사본이 `rev: 2026-08-26e`로 정본(`rev: 2026-09-07`) 대비 낡음 — `save_skill overwrite:true`로 갱신.
- [ ] **O-p1 (신규, 오늘 밤 장후 판정)** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date` 키 공백 — 10/2 EOD 성공에도 불구 오늘 아침 비어 있었음(PreRetrain 폴백으로 실거래 영향 없음 확인). 오늘 밤 EOD 이후 이 키들이 2026-10-06으로 채…
- [ ] **O-u1 (지속, 다음 거래일)** 부팅구간 access violation — 10/6로 8관측일째(9/17·9/28·9/29·9/30·10/1·10/2·10/5·10/6). 다음 실거래일(10/7 수)에 9관측일째 재현 여부 확인.
- [ ] **O-u5 (지속)** 기형 파일 — 10/6에도 변동 없이 그대로.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` + 이름변경된 index.lock 부스러기 — T2 `.git/index.lock.stale_20261005001120_6`(24.1시간, 스테일 확정) 포함. Windows에서 `--reclaim` 필요.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
tateDrop]` 경고 로그 자체가 뜨지 않았음(10/1→10/2 전환 때와 다른 점). 휴장일이라 PreRetrain이 안 돌아서 생긴 정상 공백인지 606-2 계열의 변종인지 다음 실거래일 장전에서 판정.
- [ ] **O-u1 (지속)** 부팅구간 access violation — 10/5로 7관측일째(9/17·9/28·9/29·9/30·10/1·10/2·10/5), 다음 실거래일(10/6)에 8관측일째 재현 여부 확인.
- [x] **O-u2 판정 완료 (같은 세션 내)** `.git/index.lock`(10/5 장전 수집분) 스테일 확정 후 `--reclaim`으로 장전 세션 안에서 자력 회수 완료 — 다음 세션 이월 불필요. 이름변경된 부스러기 1건 추가, 648-2가 계속 추적.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` + 이름변경된 index.lock 부스러기 — 10/5 장전분 1건 추가. Windows에서 `--reclaim` 필요.


## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)

- [ ] **658-1 (P2, 다음 디바이스 셸 가동 시)** `python scripts/collect_evidence.py --phase post --out docs/정기점검/매일점검/evidence_MW0601-20261005_post.md` 보강 실행 — 이번 장후는 `device_bash` 미가동으로 공식 증거 다이제스트를 생성하지 못함. 급하지 않음(오늘은 거래 0건이라 판정에 영향 없음).
- [ ] **658-2 (P2, 선택)** `main.py` 종료 핸들러에서 `auto_shutdown_done_date` 쓰기 경로를 `grep`으로 확인 — 휴장일 자동종료 기능이 실제 구현돼 있는지, 오늘(10/5)처럼 사용자가 먼저 종료하는 경우에 그 경로를 아예 안 타는지 확정. 다음 휴장일 1회 더 관측 후(표본 2건) 판단해도 됨.
- [ ] **O-u6-참고** 10/5는 휴장일이라 PreRetrain 미가동으로 `p8_last_success_date`·`eod_retrain_ok_date` 날짜 전환 판정 불가 — 10/6(화) 실거래일 장전에서 그대로 판정.

## 2026-10-06 (MW0601 659차 — 장전 점검)

- [ ] **659-1 (P1, 장후 적용)** `collect_evidence.py`의 `git diff --numstat` 타임아웃 2회 연속 재발(인덱스락 유발) — 두 번째 변형 호출 생략 또는 코웍 마운트 환경에서 numstat 스킵 분기 추가.
- [ ] **659-2 (P2, 장후 적용)** `재시작_종료사유분류_봉결손_구현계획_20260922.md` 2행 "재" 1글자 추가(633-1 종결).
- [ ] **659-3 (P2, 장후 적용)** `CLAUDE.md:24` joblib "1.1.1"→"1.1.0" 정정 — ⚠ 과거(538차 F-3)에도 "결정"만 나고 실제 커밋 안 됨, 이번엔 적용 후 커밋까지 확인할 것.
- [ ] **659-4 (P2, 장후 적용)** 리포 루트 기형 파일(`C:\Users\82108\PycharmProjects\Peter\트윗원문\피터리_10월매매_20261002_1002.md`) 올바른 위치로 이동/삭제.
- [ ] **659-5 (P2, 선택)** 이 PC 앱 저장 스킬(`mireuk-daily-check`) 사본이 `rev: 2026-08-26e`로 정본(`rev: 2026-09-07`) 대비 낡음 — `save_skill overwrite:true`로 갱신.
- [ ] **O-p1 (신규, 오늘 밤 장후 판정)** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date` 키 공백 — 10/2 EOD 성공에도 불구 오늘 아침 비어 있었음(PreRetrain 폴백으로 실거래 영향 없음 확인). 오늘 밤 EOD 이후 이 키들이 2026-10-06으로 채워지는지 확인.
- [ ] **O-u1 (지속, 다음 거래일)** 부팅구간 access violation — 10/6로 8관측일째(9/17·9/28·9/29·9/30·10/1·10/2·10/5·10/6). 다음 실거래일(10/7 수)에 9관측일째 재현 여부 확인.
- [x] **O-u2 판정 완료 (같은 세션 내)** `.git/index.lock`(10/6 장전 수집분) 스테일 확정 후 `--reclaim`으로 장전 세션 안에서 자력 회수 완료 — 장중 세션 이월 불필요. 이름변경된 부스러기 1건 추가(648-2 계속 추적).
- [ ] **O-u5 (지속)** 기형 파일 — 10/6에도 변동 없이 그대로.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` + 이름변경된 index.lock 부스러기 — T2 `.git/index.lock.stale_20261005001120_6`(24.1시간, 스테일 확정) 포함. Windows에서 `--reclaim` 필요.

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

### `data/heartbeat_MW0601_20261006.json` — 244B · 10-06 12:31:16
```json
{
 "pid": 31176,
 "written_at": "2026-10-06T12:32:46",
 "beat_epoch": 1791257565.2360966,
 "beat_age_sec": 1.4,
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

- 파일 최종 기록: **10-06 11:59:45**

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
| `raw_candles` 당일 max ts | **12:31** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 226 |
| `session_bars` 당일 행수 | 226 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 158봉** (`session_bars` 에도 없음): 10:52, 12:32, 12:33, 12:34, 12:35, 12:36, 12:37, 12:38, 12:39, 12:40, 12:41, 12:42, 12:43, 12:44, 12:45, 12:46, 12:47, 12:48, 12:49, 12:50

- 라이브 로그 대조: `logs/20261006_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 3회 · 재시작 2회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 3개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **10건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 8928: `Windows fatal exception` **4건** (access violation 4) — 직전 표식 시각 10:52:55, 11:58:49 · 정규장(09:00) 이후 **4건**
- PID 11972: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
- PID 31176: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 11:59:26 · 정규장(09:00) 이후 **3건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 11972 | 08:40:45 | 없음 | 없음 | 판정불가 — WER **미측정** |
| 8928 | 10:52:55 | 없음 | 없음 | 판정불가 — WER **미측정** |
| 31176 | 11:59:26 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 196개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261006-점검리포트.md` | 23.6KB | 10-06 09:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_pre.md` | 63.0KB | 10-06 09:00 |
| `docs/정기점검/매일점검/MW0601-20261005-점검리포트.md` | 36.6KB | 10-06 08:01 |
| `docs/정기점검/매일점검/evidence_MW0601-20261005_pre.md` | 57.6KB | 10-05 09:00 |
| `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` | 91.4KB | 10-02 17:29 |
| `docs/정기점검/매일점검/_tmp_append_post_20261002.md` | 0B | 10-02 16:31 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_post.md` | 85.1KB | 10-02 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20261002_intra.md` | 73.4KB | 10-02 12:28 |

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
2. `logs/20261006_WARN.log`: ERROR 이상 2건
3. `logs/20261006_SYSTEM.log`: 매분 루프 커버리지 213/371분 (57.4%) — 루프가 빠진 구간이 있다
4. `logs/20261006_SYSTEM.log`: 12:33~15:10 **연속 158분 매분 루프 기록 없음**
5. `logs/20261006_HEALTH.log`: ERROR 이상 1건
6. 메인 스레드 정지 5초 초과 **5건** (최대 18266ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20261006_WARN.log`: **level=CRITICAL** 1건(표본)
8. `logs/20261006_SYSTEM.log`: **ConstOut** 4건(표본)
9. `logs/20261006_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20261006_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20261006_LEARNING.log`: **축퇴** 8건(표본)
12. `logs/20261006_HEALTH.log`: **level=CRITICAL** 1건(표본)
13. `logs/crash_fault.log`: `Windows fatal exception` **10건** (정규장 09:00 이후 7건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
14. 미커밋 변경 61건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다 · 실패 명령: `git diff --numstat → (git 타임아웃 25s — 자식 종료함) git diff --numstat`
15. 🔴 **이 수집 실행이 `.git/index.lock` 을 남겼다** — 시작 시점에는 없었다(생긴 구간은 §2 「git 호출 기록」 참조 — 653차). 방치하면 그날 dev_memory·리포트가 커밋되지 않은 채로 끝난다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261006*.log` (Windows) / `grep 강제청산 logs/*20261006*.log`*