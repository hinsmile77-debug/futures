# 미륵이 증거 다이제스트 — 2026-10-16 / POST

- 생성 2026-10-16 16:19:00 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01jbtssrzquzkamhvoyxmpim/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261016` · `2026-10-16` · `261016` · `1016`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **49개** 파일 · 49개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-intra-cowork-intraday-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261016-intra-cowork-intraday-20261016.json` | 176B | 10-16 12:32 |
| `claude-{DATE}-post-cowork-post-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261016-post-cowork-post-20261016.json` | 172B | 10-16 16:18 |
| `claude-{DATE}-pre-cowork-premarket-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261016-pre-cowork-premarket-20261016.json` | 176B | 10-16 09:03 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261016.log` | 136B | 10-16 07:21 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261016.txt` | 28B | 10-16 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261016.txt` | 28B | 10-16 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261016.txt` | 233B | 10-16 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261016.log` | 1.4KB | 10-16 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261016.log` | 217B | 10-16 15:53 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261016.json` | 243B | 10-16 15:46 |
| `launcher_{DATE}_084001_2887.log` | 1 | `logs/Mireuk_batch/launcher_20261016_084001_2887.log` | 959B | 10-16 08:40 |
| `launcher_{DATE}_084533_3971.log` | 1 | `logs/Mireuk_batch/launcher_20261016_084533_3971.log` | 2.5MB | 10-16 15:47 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261016.log` | 173B | 10-16 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261016.log` | 71.3KB | 10-16 16:13 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261016.log` | 491B | 10-16 16:15 |
| `position_state.json.gen_{DATE}_135734` | 1 | `data/position_state.json.gen_20261016_135734` | 1.5KB | 10-16 13:07 |
| `position_state.json.gen_{DATE}_140029` | 1 | `data/position_state.json.gen_20261016_140029` | 1.5KB | 10-16 14:00 |
| `position_state.json.gen_{DATE}_140053` | 1 | `data/position_state.json.gen_20261016_140053` | 1.5KB | 10-16 14:00 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261016.log` | 34.5KB | 10-16 16:00 |
| `retrain_intraday_20260709_{DATE}00.log` | 1 | `logs/retrain_intraday_20260709_101600.log` | 4.6KB | 07-09 10:16 |
| `retrain_intraday_{DATE}_102500.log` | 1 | `logs/retrain_intraday_20261016_102500.log` | 5.7KB | 10-16 10:25 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261016.log` | 91.7KB | 10-16 16:06 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261016.txt` | 43B | 10-16 15:47 |
| `strategy_report_{DATE}_154028.txt` | 1 | `data/daily_reports/strategy_report_20261016_154028.txt` | 2.0KB | 10-16 15:40 |
| `trail_state_{DATE}.json` | 1 | `data/peter2_live/trail_state_2026-10-16.json` | 51B | 10-16 14:00 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-16.jsonl` | 8.4KB | 10-16 15:21 |
| `{DATE}_0910_D.xls` | 1 | `data/db/option_hts/261016_0910_D.xls` | 482.8KB | 10-16 09:10 |
| `{DATE}_0943_D.xls` | 1 | `data/db/option_hts/261016_0943_D.xls` | 482.9KB | 10-16 09:43 |
| `{DATE}_1017_D.xls` | 1 | `data/db/option_hts/261016_1017_D.xls` | 483.0KB | 10-16 10:17 |
| `{DATE}_1047_D.xls` | 1 | `data/db/option_hts/261016_1047_D.xls` | 483.0KB | 10-16 10:47 |
| `{DATE}_1120_D.xls` | 1 | `data/db/option_hts/261016_1120_D.xls` | 483.0KB | 10-16 11:20 |
| `{DATE}_1233_D.xls` | 1 | `data/db/option_hts/261016_1233_D.xls` | 483.1KB | 10-16 12:33 |
| `{DATE}_1401_D.xls` | 1 | `data/db/option_hts/261016_1401_D.xls` | 483.2KB | 10-16 14:01 |
| `{DATE}_D.xls` | 1 | `data/db/option_hts/261016_D.xls` | 483.3KB | 10-16 15:48 |
| `{DATE}_DATA.log` | 1 | `logs/20261016_DATA.log` | 435.6KB | 10-16 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261016_DEBUG.log` | 245.0KB | 10-16 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261016_HEALTH.log` | 6.0KB | 10-16 14:39 |
| `{DATE}_HOGA.log` | 1 | `logs/20261016_HOGA.log` | 59.0MB | 10-16 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261016_LEARNING.log` | 295.1KB | 10-16 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261016_MICRO.log` | 1.1MB | 10-16 15:38 |
| `{DATE}_P.xls` | 1 | `data/db/option_hts/261016_P.xls` | 484.0KB | 10-16 15:48 |
| `{DATE}_PROBE.log` | 1 | `logs/20261016_PROBE.log` | 94.6KB | 10-16 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261016_REGULAR_COLLECT.log` | 8.7KB | 10-16 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261016_SIGNAL.log` | 509.3KB | 10-16 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261016_SYSTEM.log` | 1.0MB | 10-16 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261016_TRADE.log` | 16.1KB | 10-16 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261016_WARN.log` | 838.6KB | 10-16 15:46 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-16_tr.draft.txt` | 136B | 10-16 15:40 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-10-16_tr.txt` | 136B | 10-16 15:40 |

## 2. 코드·커밋 상태

- HEAD `51d5de4` · 브랜치 `v9-dev` · 미커밋 161건 · 실질 변경 17건 · 코드(.py) 2건 · EOL 파생 0건 (추적변경 17 · 미추적 144 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260918.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260918.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260918.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260918.md` … 외 5개
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 6.0초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md
 M docs/미륵이고도화3/신동2/학습/lessons.json
 M docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md
 M docs/미륵이고도화3/신동2/학습/추이_MW0601.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260918.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260918.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260918.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260918.md
 M tools/peter2_live/extension/background.js
 M tools/peter2_live/extension/content.js
 M tools/peter2_live/extension/manifest.json
 M tools/peter2_live/latency_report.py
 M tools/peter2_live/receiver.py
?? "MAEKJEOM_LADDER.bat - 바로 가기.lnk"
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_20261002.md
?? dev_memory/_tmp_append_decisionlog_20261006_post.md
?? dev_memory/_tmp_append_decisionlog_20261007_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_pre.md
?? dev_memory/_tmp_append_decisionlog_20261009_intra.md
?? dev_memory/_tmp_append_decisionlog_20261009_post.md
?? dev_memory/_tmp_append_decisionlog_20261012_intra.md
?? dev_memory/_tmp_append_decisionlog_20261012_pre.md
?? dev_memory/_tmp_append_decisionlog_20261013_intra.md
?? dev_memory/_tmp_append_decisionlog_20261015_post.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_pre.md
?? dev_memory/_tmp_append_nexttodo_20261009_intra.md
?? dev_memory/_tmp_append_nexttodo_20261012_intra.md
?? dev_memory/_tmp_append_nexttodo_20261012_pre.md
… 외 121건
```

**당일(2026-10-16) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
51d5de4 [MW0601] 696차 후속: 장후 자동조치 — E-2 · F-X1
bd501c2 [MW0601] 692차 후속3: 피터2 — 도착 시점에 이미 만료된 지시는 대기로 열지 않는다
46d2e13 [MW0601] 692차 후속2: CREON 런처 기동흐름 — LAUNCH_API 파싱 즉사 · 계좌비밀번호 창 자동처리 · 사이드카 중복/자진종료
6118658 [MW0601] 692차 후속: 08:50 맥점 08:45 시가 당일 차트 보정 — 실시간 첫 틱 → 개장 체결가
57155d1 [MW0601] 692차: 장후 봉 정합 — 만기일 창(15:22–15:39)·종료 전 확정 판정 · raw_candles 창 안 보충(618차 번복, bar_recovered=2/3) · 따라잡기 · 부분 봉 교정
0ca2476 [MW0601] 691차: 08:50 맥점 전일 이력 경고 — 「전일 이력 없음」 깜박임 · 「전일 부분 결손」 주황 고정
fe22516 [MW0601] 690차: 10-14 장후 점검 리포트 · 피터2 트레일 결정 기록
0140c60 [MW0601] 690차 후속: 피터2 이익보호 트레일 실거래 적용 + 기존 규칙 섀도
acc5a13 [MW0602] 체리픽: ProfitGuard broker 추정 수수료 이중 차감 수정 · 8a5f782 설명 정정 (원 4d050d7, dev)
8a5f782 [MW0602] 체리픽: 실계좌 일일손익 TR 기준일자 재시도 · 브로커 손익 net 축 판별 · 잔고 기본값 미측정 표기 (원 a6ab8f2·c1ff742, dev)
74f1d4b [MW0601] 피터2: 진입 로그를 시도·접수·실패로 분리 — 브로커 거부도 TRADE 로그상 진입으로 읽히던 문제
271ddbd Merge remote-tracking branch 'origin/v9-dev' into v9-dev
```

⚠ **PC명 태그 누락 커밋 1건** (CLAUDE.md 멀티PC 컨벤션 위반):
```
271ddbd Merge remote-tracking branch 'origin/v9-dev' into v9-dev
```

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `1` | `3` | **불일치 ⚠** | 431차 10→3 인하. 실전 자본 확정 시 재산출 대상 |
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

### 차단 게이트 전수 인벤토리 — 41개 중 **9개 꺼짐**

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
| `PRINCIPAL_SHINDONG_ENABLED` | True | — |
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

_본문 미열람(설정): `20261016_HOGA.log` 59.0MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261016.txt`** — 28B · 10-16 15:40:28
```
2026-10-16T15:40:28.626566
```

**`data/daily_close_started_20261016.txt`** — 28B · 10-16 15:40:05
```
2026-10-16T15:40:05.666851
```

**`data/daily_reports/strategy_report_20261016_154028.txt`** — 2.0KB · 10-16 15:40:28
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-16 15:40
========================================================
  버전    : v1.0  (99일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-3.50  MDD(자본대비)=4.4%
  당일      : WR=25.0%  PF=0.24
  롤링20일: 누적 -1434050원  Sh=-3.50  MDD(자본대비)=4.4%  MDD(peak대비)=701.1%
  당일손익 : broker(gross) -426,788원  수수료 6,781원  net -426,781원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.66)
  PSI     : 0.003 (CLEAR)
  PSI/feat: cvd_delta=0.003  ofi_pressure=0.000  vwap_position=0.113
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -47,855원  승률 35.0%  합계 -957,092원
  등급별 순EV(30일): A=-6,062원(58건,승57%)  P=-67,655원(16건,승19%)
  호라이즌별 순EV(30일): 1m=+2,297원(7건)  3m=+15,483원(33건)  5m=-48,810원(18건)  ?=-67,655원(16건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 2분  5일평균 21분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 34.2pt(5일평균 40.6pt)  1분평균변동 0.90pt(5일평균 0.95pt)
--------------------------------------------------------
  진입 퍼널(2026-10-16, 총 370분):
    FLAT 261 → conf미달 103 → CoherenceGate 4 → 게이트차단 1 → 후보 1 → 진입 1
    게이트별: 체크리스트항목미달=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261016.txt`** — 233B · 10-16 15:53:33
```
completed: 2026-10-16 15:53:33
rows: 21399
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 25.9
t_retrain_s: 183.0
t_total_s: 209.4
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/peter_feed/2026-10-16_tr.draft.txt`** — 136B · 10-16 15:40:07
```
09:55 S 886 / 10:12 X 890 손절
10:20 S 892 / 13:00 X 898 손절
13:07 S 899 / 13:59 X 902 손절
14:00 S 901 / 14:01 X 904 손절
```

**`data/peter_feed/2026-10-16_tr.txt`** — 136B · 10-16 15:40:07
```
09:55 S 886 / 10:12 X 890 손절
10:20 S 892 / 13:00 X 898 손절
13:07 S 899 / 13:59 X 902 손절
14:00 S 901 / 14:01 X 904 손절
```

**`data/shutdown_normal_20261016.txt`** — 43B · 10-16 15:47:14
```
auto_shutdown
2026-10-16T15:47:14.636263
```

_다이제스트 대상 8/23개 (중요도순). 제외: `retrain_intraday_20260709_101600.log`, `20261016_MICRO.log`, `20261016_DATA.log`, `20261016_PROBE.log`, `launcher_20261016_084533_3971.log`, `launcher_20261016_084001_2887.log`, `20261016_DEBUG.log`, `shindong2_20261016.log`_

### `logs/20261016_TRADE.log` — 16.1KB · 117행 · 최종 15:40:24

- 형식 평문 · 시각 인식 117행 · WARNING=10, INFO=107

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:26 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-16 08:46:31 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-16 09:02:36 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 875.72 | 손절=882.26 1차=-9124.28(×1.00) 2차=-9124.28
2026-10-16 09:02:36 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=875.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-10-16 09:02:36 [INFO] TRADE: [Virtual] 신동 가상진입 SHORT 1계약 @875.72 손절 882.26 목표 862.50 (principal)
  …
2026-10-16 14:00:53 [INFO] TRADE: [Position] 체결청산 SHORT @ 902.38 | PnL=-2.74pt (-138,709원) | 하드스톱(틱)
2026-10-16 14:00:53 [INFO] TRADE: [청산 완료] PnL=-2.74pt (-138,709원) | 포지션 합계 -138,709원 (레그 1)
2026-10-16 15:05:01 [INFO] TRADE: [Position] 청산 LONG @ 885.5 | PnL=-3.24pt (-163,689원) 수수료=1,689원 | 가상:신동시간청산
2026-10-16 15:05:01 [INFO] TRADE: [Virtual] 신동 가상청산 LONG 1계약 @885.50 가상:신동시간청산 | -3.24pt -163,689원 (포지션 종료)
2026-10-16 15:40:24 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 10 | 09:02:36 | 14:00:29 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=875.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×117

**컴포넌트 상위 15** — `Position`×27, `Chejan`×24, `Virtual`×14, `PositionFallback`×10, `Peter2Trail`×9, `Peter2`×8, `주문요청`×8, `체결진입`×4, `TickStop-S0C`×4, `청산 완료`×4, `ProfitGuard`×2, `Sizer`×1, `진입체크`×1, `Peter2TrailShadow`×1

### `logs/20261016_WARN.log` — 838.6KB · 3798행 · 최종 15:46:09

- 형식 평문 · 시각 인식 3791행 · CRITICAL=1, WARNING=3790, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:11 [WARNING] SYSTEM: [BarGap] 기동 시점 결손 1봉 / 검사창 08:45~08:45 (분그리드 기준) — 08:45 | session_bars 보존 여부는 15:46 확정 판정에서
2026-10-16 08:46:34 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-16 08:46:34 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-10-16 08:46:34 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-16 08:46:34 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
  …
2026-10-16 15:40:45 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 78.7ms | size=1994x950 candles=408 grid=13.8 spans=1.3 candles=16.8 dir=1.4 regime=1.3 markers=30.6 axes=11.9 cross=0.0 | slow_cnt=3149 total_cnt=3371 overlay_cnt=40130
2026-10-16 15:40:45 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 79.0ms | size=1994x950 candles=408 grid=13.3 spans=1.4 candles=16.7 dir=1.4 regime=1.3 markers=30.5 axes=12.8 cross=0.0 | slow_cnt=3150 total_cnt=3372 overlay_cnt=40130
2026-10-16 15:40:45 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 84.6ms | size=1994x950 candles=408 grid=14.2 spans=1.4 candles=16.7 dir=1.4 regime=1.3 markers=34.4 axes=13.7 cross=0.0 | slow_cnt=3151 total_cnt=3373 overlay_cnt=40130
2026-10-16 15:45:46 [WARNING] SYSTEM: [OptionFlowChart] 그리기 78.6ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 761x999
2026-10-16 15:46:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3484ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2225 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=3484 band=INFO since_pipe_s=2228.9
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `SHS-EKS` | 1 | 09:05:00 | 09:05:00 | Early Kill Switch 발동 — 일시 관망 conf_max=35.0% bars=5 (delayed=0 policy=4 conf측정=1) → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |

<details><summary>CRITICAL/SHS-EKS 원문 1건</summary>

```
2026-10-16 09:05:00 [CRITICAL] SYSTEM: [SHS-EKS] Early Kill Switch 발동 — 일시 관망 conf_max=35.0% bars=5 (delayed=0 policy=4 conf측정=1) → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)
```

</details>

**WARNING — 태그 41종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 3151 | 08:55:36 | 15:40:45 | paintEvent slow 45.0ms | size=1994x950 candles=9 grid=24.8 spans=0.0 candles=0.3 dir=0.0 regime=0.0 markers=0.0 axes=18.7 cross=0.0 | slow_cnt=1 total_cnt=71 overlay_cnt=339 |
| `LiveDBG` | 272 | 08:46:34 | 15:46:09 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 77 | 09:03:59 | 15:45:46 | 그리기 59.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 790x1001 |
| `Peter2` | 51 | 09:12:25 | 14:22:11 | 수집기 하트비트 없음/지연(정상수집 91초 전 · X 페이지 오류: Top) — 신규 추종 진입 정지. Chrome 확장·수신기(tools/peter2_live) 확인 |
| `ChejanFlow` | 24 | 09:56:03 | 14:00:53 | account='783343908' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='453' | pending='ENTRY:SHORT qty=1 filled=0 order_no=? reason=진입 req_at=09:56:03.579' | positio… |
| `ChejanMatch` | 24 | 09:56:03 | 14:00:53 | order_no='453' | pending='ENTRY:SHORT qty=1 filled=0 order_no=453 reason=진입 req_at=09:56:03.579' | pending_matched=True |
| `SHAP` | 23 | 11:40:01 | 15:07:01 | 슬로우 감지 903ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `CB③-P4` | 22 | 10:50:00 | 14:41:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=20.0%) |
| `Health` | 19 | 09:26:00 | 14:38:00 | level=WARNING degraded=OFF | latency=296ms | quality=1.00 | cache_age=183s | exceptions_10m=0 |
| `ScalerRefresh` | 16 | 09:08:00 | 15:03:00 | 5분 누적 수익률 +0.517% (임계 ±0.489%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PendingOrder` | 16 | 09:56:03 | 14:00:54 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 882.88, 'reason': '진입', 'hint_source': '', 'atr': 2.0771, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qt… |
| `ExitCooldown` | 8 | 10:12:27 | 14:00:53 | 하드스톱(틱) 후 3분 재진입 금지 (until 10:15:27) |

**채널** — `SYSTEM`×3772, `HEALTH`×19

**컴포넌트 상위 15** — `ChartDBG`×3151, `LiveDBG`×272, `OptionFlowChart`×77, `Peter2`×51, `ChejanFlow`×24, `ChejanMatch`×24, `SHAP`×23, `CB③-P4`×22, `Health`×19, `ScalerRefresh`×16, `PendingOrder`×16, `ExitCooldown`×8, `PipePerf`×8, `CB⑤`×8, `SHS-EKS`×7

### `logs/20261016_SYSTEM.log` — 1.0MB · 7223행 · 최종 15:47:14

- 형식 평문 · 시각 인식 7193행 · INFO=7193, PLAIN=30

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:11 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=3744 | 행감지=30s all_threads=True
2026-10-16 08:46:11 [INFO] SYSTEM: [DBInit] 합계 0.51s | predictions=0.06s trades=0.25s daily_stats=0.01s shap=0.02s raw_data=0.13s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-16 08:46:11 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-16 08:46:11 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-16 08:46:11 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-16 15:46:05 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-16) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-16 15:46:35 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:46:35
2026-10-16 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-16 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-16 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×7193

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1540, `PumpGuard`×757, `BAR-CLOSE`×408, `CVD-ANCHOR`×408, `CybosRT-ROLLOVER`×407, `TickUI`×405, `S6Detail`×370, `PipePerf`×370, `System`×99, `MicroRegime`×97, `OptionChain`×81, `OptionBook`×79, `RegimeFingerprint`×68, `Peter2`×51

### `logs/20261016_SIGNAL.log` — 509.3KB · 4552행 · 최종 15:40:24

- 형식 평문 · 시각 인식 4552행 · WARNING=1499, INFO=3053

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.466
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.448
  …
2026-10-16 15:10:28 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-16 15:40:24 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-16 15:40:24 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 132분(35.7%) / DN 17분(4.6%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-16 15:40:24 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-16 age=24m extreme=414 refresh=33 grade_x=94 cb3=0
2026-10-16 15:40:24 [INFO] SIGNAL: [ModelHealth] date=2026-10-16 앙상블유효가동률=66.5% | 파이프라인 370분 | ConstOut 17회/30분 {"3m": {"events": 13, "minutes": 22}, "5m": {"events": 4, "minutes": 8}} | WeightCollapse 94분 | 장중재학습 1회 | CB③ ready 260분/370분 (70%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 984 | 09:00:01 | 15:03:00 | 1m 'macro_vix' scale=0.0315 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 168 | 09:00:00 | 15:08:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 120 | 09:00:00 | 15:08:00 | ts=08:59 horizon=1m age=3m max_z=+7.51(cancel_add_ratio) extreme=1 adj=1 |
| `Checklist` | 107 | 09:06:00 | 15:03:00 | 신뢰도 미달 33.9% < 42.2% → 강제 X등급 |
| `WeightCollapse` | 94 | 09:07:00 | 15:09:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 18 | 09:36:00 | 15:08:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 6 | 14:24:00 | 14:49:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3519 < 필요 0.4360 (conf_floor=0.330, min_conf=0.436, span=0.0043, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `MetaGate` | 1 | 12:47:00 | 12:47:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×4552

**컴포넌트 상위 15** — `ScalerFloor`×1032, `SIGNAL`×740, `MetaGate`×467, `Ensemble`×369, `ZeroDiag`×368, `FQAdj`×289, `Model`×180, `ScalerMonitor`×121, `Checklist`×113, `InstabilityGate`×113, `MicroRegime`×97, `ATR-Horizon`×95, `WeightCollapse`×94, `차단`×50, `ToxicityGate`×49

### `logs/20261016_LEARNING.log` — 295.1KB · 2880행 · 최종 15:40:24

- 형식 평문 · 시각 인식 2870행 · WARNING=157, INFO=2713, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:13 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:17 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00121 auc=0.532 out_max=0.4229 (n=135) → 보정 재적용
  …
2026-10-16 15:40:24 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-16 15:40:24 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-16 15:40:24 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-16 15:40:24 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-16 15:40:24 [INFO] LEARNING: [Sigma] EOD sigma_20=0.10269% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 48 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 43 | 08:46:16 | 14:27:00 | 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 24 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 17 | 08:46:17 | 08:46:25 | 축퇴 감지 — span=0.00084 auc=0.529 out_max=0.2880 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 10 | 08:46:17 | 09:29:00 | 축퇴 감지 — span=0.00108 auc=0.453 out_max=0.3129 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 6 | 08:46:17 | 08:46:25 | 축퇴 감지 — span=0.00051 auc=0.520 out_max=0.3781 (기준 auc<0.53 and span<0.020, 기저율=0.3778 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 5 | 10:13:00 | 13:34:00 | 하한 도달불가 — out_max=0.3259 < conf_floor=0.3300 (span=0.01254 auc=0.572 out_max=0.3259, 기저율=0.3200 n=200) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Buffer-Timing` | 3 | 12:33:00 | 14:07:00 | total=561ms raw_fetch=3ms pred_select=53ms pred_update=46ms pred_insert=13ms verified=3 |
| `DriftAdjuster` | 1 | 15:40:07 | 15:40:07 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 23일) |

**채널** — `LEARNING`×2870

**컴포넌트 상위 15** — `LEARNING`×1191, `SGD`×369, `sigma`×357, `Bias⚠`×247, `Bias`×114, `OnlineLearner`×106, `Calibration:1m`×94, `Calibration:30m`×84, `MetaConf`×74, `Calibration:3m`×46, `BiasReset`×40, `ScalerWarmup`×38, `Calibration:5m`×33, `Calibration:10m`×19, `Calibration:15m`×12

### `logs/20261016_HEALTH.log` — 6.0KB · 35행 · 최종 14:39:00

- 형식 평문 · 시각 인식 35행 · WARNING=19, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 09:26:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=296ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-10-16 09:27:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=296ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[Peter2]×1
2026-10-16 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 295ms (표본 20분)
2026-10-16 10:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=292ms | quality=1.00 | cache_age=181s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
2026-10-16 10:22:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=262ms | quality=1.00 | cache_age=58s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
  …
2026-10-16 14:06:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=348ms | quality=1.00 | cache_age=96s | exceptions_10m=5 | exc_tags=[ExitCooldown]×2 [SHAP]×2 [Peter2]×1
2026-10-16 14:07:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1515ms | quality=1.00 | cache_age=156s | exceptions_10m=4 | exc_tags=[ExitCooldown]×2 [Peter2]×1 [SHAP]×1
2026-10-16 14:08:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=270ms | quality=1.00 | cache_age=32s | exceptions_10m=4 | exc_tags=[Peter2]×2 [ExitCooldown]×1 [SHAP]×1
2026-10-16 14:38:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=361ms | quality=1.00 | cache_age=180s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-16 14:39:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=309ms | quality=1.00 | cache_age=57s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 19 | 09:26:00 | 14:38:00 | level=WARNING degraded=OFF | latency=296ms | quality=1.00 | cache_age=183s | exceptions_10m=0 |

**채널** — `HEALTH`×35

**컴포넌트 상위 15** — `Health`×34, `HealthTrend`×1

### `logs/retrain_eod_20261016.log` — 34.5KB · 276행 · 최종 16:00:03

- 형식 평문 · 시각 인식 163행 · WARNING=23, INFO=140, PLAIN=113

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 15:50:03,388 [INFO] EOD_RETRAIN: =======================================================
2026-10-16 15:50:03,388 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-16 15:50:03,389 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-16 15:50:03,389 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-16 15:50:03,389 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-16 16:00:03,387 [INFO] EOD_RETRAIN: [검증 캠페인] 섀도우 TB 재학습 → 실패 (rc=3221225786)
2026-10-16 15:58:01,707 INFO [ShadowTB] 1m raw_features 폴백 — 백필행 18574/43972 제외 (미시구조 0.0, 418차) → 학습 가용 25398행
2026-10-16 15:58:01,884 INFO [ShadowTB] 1m raw_features_horizon 데이터 없음 — raw_features 폴백 사용
2026-10-16 15:58:33,579 INFO [ShadowTB] 1m cv_acc=0.5678 n=25398 레이블분포={-1: 764, 0: 10041, 1: 14593} (champion cv_acc=0.4635)
2026-10-16 15:59:19,006 INFO [ShadowTB] 3m cv_acc=0.5084 n=14197 레이블분포={-1: 681, 0: 7570, 1: 5946} (champion cv_acc=0.3761)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:38 | 15:52:36 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-10-16 09:54:00까지)인데 acc.txt=0.4714는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:38 | 15:52:36 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1566봉(85%)이 현행 학습구간 (현행 cutoff=2026-10-16 09:54:00 ≥ 홀드아웃 시작=2026-10-08 10:59:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-16 09:54 >= holdout_start=2026-10-08 10:59 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-1… |
| `RegularFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-16 | 최신 2026-10-15 · 기준 8거래일. 복구: python scripts/collect_regular_futures.py --from 20261016 --to 20261016 |
| `OptionFlowFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-13(최신봉 15:33) | 기준 7거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\<YYYYMMDD>_OPTION_BACKFILL.log |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 18574/43972 제외 (418차 결정 1) — 남은 25398행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/25398행 제외 (559차 P1'-2) — 남은 23952행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:33 | 15:53:33 | 백필 0행 제외 — 필터가 무효일 수 있다. 21399행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×74, `EOD_RETRAIN`×38, `SIGNAL`×37, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×112, `ScalerFloor`×30, `Retrain`×21, `EOD_RETRAIN`×15, `GuardGhost`×12, `검증 캠페인`×10, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4

### `logs/retrain_intraday_20261016_102500.log` — 5.7KB · 43행 · 최종 10:25:43

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 10:25:00,878 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-16 10:25:00,878 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-16 10:25:00,879 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-16 10:25:00,879 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-16 10:25:00,879 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ce4939aa.json
  …
2026-10-16 10:25:43,756 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-16 10:25:43,757 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-16 10:25:43,758 [INFO] LEARNING: [Retrain] 완료 | 39.6초 | 성공=6/6 호라이즌
2026-10-16 10:25:43,759 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 42.9s 데이터=4800행
2026-10-16 10:25:43,761 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ce4939aa.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:25:15 | 10:25:15 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 18869/43983 제외 (418차 결정 1) — 남은 25114행 |
| `UnitMismatch` | 1 | 10:25:15 | 10:25:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/25114행 제외 (559차 P1'-2) — 남은 23668행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -426781원
════════════════════════════════════════════════════
2026-10-16 15:40:31 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 75.5ms | size=1994x922 candles=223 grid=9.4 spans=0.1 candles=10.7 dir=0.8 regime=8.5 markers=29.1 axes=15.6 cross=0.0 | slow_cnt=3133…
2026-10-16 15:40:33 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 71.3ms | size=1994x922 candles=182 grid=9.1 spans=0.1 candles=9.0 dir=0.7 regime=7.5 markers=27.0 axes=16.7 cross=0.0 | slow_cnt=3134 …
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) | 11 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 4 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 7 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 4 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 4 |
| 차단(`[차단]`) | 50 |
| 사이저 호출(`[Sizer]`) | 1 |

> 🔴 **엔진 진입 0건인데 계좌 체결 4건**(외부표식 0 · 피터2 4 · 판별불가 0) — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.
>
> 별도로 **가상 장부 진입 7건**이 `[Position] 진입` 에 섞여 있다 — 실주문이 없으므로 계좌 체결·손익과 무관하다(아래 「가상 장부」 표).

### 포지션 4건 · 승 1 (25%) · 합계 -8.40pt (-426,781원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:56:03 | 피터2 | SHORT | 1 | — | 1 | -4.94 | -248,677 | 하드스톱(틱) |
| 10:19:55 | 피터2 | SHORT | 1 | — | 1 | +2.66 | +131,309 | 하드스톱(틱) |
| 13:07:59 | 피터2 | SHORT | 1 | — | 1 | -3.38 | -170,704 | 하드스톱(틱) |
| 14:00:29 | 피터2 | SHORT | 1 | — | 1 | -2.74 | -138,709 | 하드스톱(틱) |

**출처별 소계** — 피터2 4건 -426,781원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「피터2」는 `[Peter2] 진입`이 동반된 보조 로직 자리로 역시 엔진 성적이 아니다. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**가상 장부 7건(청산 7 · 합계 -573,050원) — 실주문 없음, 엔진·계좌 손익 아님**

| 진입 | 주체 | 방향 | 수량 | hz | 가상 pt | 가상 net(원) | 가상 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:02:36 | 신동 | SHORT | 1 | — | +3.26 | +161,336 | 가상:신동1차 |
| 09:55:36 | 신동 | LONG | 1 | — | -2.12 | -107,678 | 가상:하드스톱 |
| 10:07:36 | 신동 | LONG | 1 | — | -4.10 | -206,683 | 가상:하드스톱 |
| 10:33:36 | 신동 | LONG | 1 | — | -6.54 | -328,687 | 가상:하드스톱 |
| 11:08:36 | 신동 | LONG | 1 | — | +4.00 | +198,322 | 가상:신동1차 |
| 11:27:00 | 미륵 | LONG | 1 | 1m | -2.49 | -125,971 | 가상:하드스톱 |
| 12:46:36 | 신동 | LONG | 1 | — | -3.24 | -163,689 | 가상:신동시간청산 |

> ⚠ 이 표는 `[Virtual] … 가상진입`/`가상청산` 로그로 조립한 **가상 장부**다. 같은 초에 `[Position] 진입` 이 찍혀 진입 건수에는 잡히지만 체결이 없다 — 3원 대사(로그·DB·브로커)에서 로그 쪽이 더 많아 보이면 먼저 이 표를 뺄 것.

**청산 레그 4행** (부분청산 0 · 전량청산 4)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:12:27 | 전량 | 1 | -4.94 | -248,677 | 하드스톱(틱) |
| 11:19:19 | 전량 | 1 | +2.66 | +131,309 | 하드스톱(틱) |
| 13:57:34 | 전량 | 1 | -3.38 | -170,704 | 하드스톱(틱) |
| 14:00:53 | 전량 | 1 | -2.74 | -138,709 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×4

> 최종 청산이 하드스톱·손절 계열인 포지션 4/4건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -426,781 = 포지션합 -426,781 → OK · `[청산 완료]` 4건 = 조립 포지션 4건 → OK

### CB③ 판정 가능 시간 — **260분 / 370분 (70%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 11건

| 시각 | 출처 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|---|
| 09:02:36 | 가상 | SHORT | 1 | 875.72 | — | — |
| 09:55:36 | 가상 | LONG | 1 | 883.02 | — | — |
| 09:56:03 | 피터2 | SHORT | 1 | 882.88 | — | — |
| 10:07:36 | 가상 | LONG | 1 | 885.6 | — | — |
| 10:19:55 | 피터2 | SHORT | 1 | 890.02 | — | — |
| 10:33:36 | 가상 | LONG | 1 | 888.04 | — | — |
| 11:08:36 | 가상 | LONG | 1 | 883.18 | — | — |
| 11:27:00 | 가상 | LONG | 1 | 888.88 | 1m | neutral |
| 12:46:36 | 가상 | LONG | 1 | 888.74 | — | — |
| 13:07:59 | 피터2 | SHORT | 1 | 896.72 | — | — |
| 14:00:29 | 피터2 | SHORT | 1 | 899.74 | — | — |

계약수 분포 — 1계약×11

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `ofi`×1, `fore`×1, `prev`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1

실제 진입 계약수 — **1계약**×11

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×1

### 차단 사유 50건 · 7종

| 건수 | 사유 |
|---|---|
| 27 | 등급X — 미통과 항목: 2_confidence |
| 16 | SHS-EKS 당일 관망 활성 — conf35%미달 |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 1 | 청산 후 쿨다운 — 87초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 27초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | 청산 후 쿨다운 — 113초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×27, `3_vwap`×1, `4_cvd`×1, `5_ofi`×1, `6_foreign`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×2
- `일간 리셋 완료` ×2
- `연속 손절 2회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 15건 · 최대 4469ms · 5초 초과 0건

상위 — 4469ms, 4468ms, 4407ms, 3922ms, 3765ms, 3484ms, 3328ms, 2890ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261016_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:27 2026-10-16 15:40:27 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 2분 < 하한 25분 — 최근 5거래일 평균 21분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 101분 · 재지않음 269분
--- [Brier] 과신 ×2(표본)
10:01:00 2026-10-16 10:01:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.350 > 0.35
10:02:00 2026-10-16 10:02:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.361 > 0.35
--- [CB] ×3(표본)
10:12:27 2026-10-16 10:12:27 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:57:34 2026-10-16 13:57:34 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
14:00:53 2026-10-16 14:00:53 [WARNING] SYSTEM: [CB] 연속 손절 2회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
10:12:27 2026-10-16 10:12:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:15:27)
10:12:27 2026-10-16 10:12:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:15:27)
10:21:00 2026-10-16 10:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=292ms | quality=1.00 | cache_age=181s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
11:19:19 2026-10-16 11:19:19 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:21:19)
--- [SHAP] 슬로우 ×8(표본)
11:40:01 2026-10-16 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 903ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:00:01 2026-10-16 12:00:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1031ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:06:01 2026-10-16 12:06:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1062ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:20:01 2026-10-16 12:20:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1036ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:46:39 2026-10-16 08:46:39 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4407ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4407 band=INFO since_pipe_s=NA
08:46:42 2026-10-16 08:46:42 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3765ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3765 band=INFO since_pipe_s=NA
09:00:03 2026-10-16 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3922 band=INFO since_pipe_s=0.1
09:02:01 2026-10-16 09:02:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2063 band=INFO since_pipe_s=0.0
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20261016_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:00 2026-10-16 09:36:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4151) | 앙상블 제외는 유지
09:44:00 2026-10-16 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4189) | 앙상블 제외는 유지
09:59:00 2026-10-16 09:59:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4637) | 앙상블 제외는 유지
10:23:00 2026-10-16 10:23:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4036) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:24 2026-10-16 15:40:24 [INFO] SYSTEM: [CB③계측] 조건성립 66분 / 판정가능 260분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-16 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:06:00 2026-10-16 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-10-16 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:17:00 2026-10-16 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:24 2026-10-16 15:40:24 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:24 2026-10-16 15:40:24 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:05 2026-10-16 15:11:05 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:28 2026-10-16 15:40:28 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-10-16 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:28 2026-10-16 15:40:28 [INFO] SYSTEM: [Notify] ℹ️ [15:40:28] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:28 2026-10-16 15:40:28 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 391초
15:40:28 2026-10-16 15:40:28 [INFO] SYSTEM: 자동 종료 예약 — 406초 후 Qt 이벤트 루프 종료
```

### `logs/20261016_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-10-16 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3519 < 필요 0.4360 (conf_floor=0.330, min_conf=0.436, span=0.0043, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:32:00 2026-10-16 09:32:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=- raw=STUCK | live(range=0.0610 dir=+1) raw(range=0.0040 dir=-1)
09:33:00 2026-10-16 09:33:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=- raw=STUCK | live(range=0.0610 dir=+1) raw(range=0.0040 dir=-1)
09:36:00 2026-10-16 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0000 dir=+1)
09:36:00 2026-10-16 09:36:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:00 2026-10-16 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-10-16 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.3% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-10-16 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-16 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.466
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
--- 안전망 ×8(표본)
09:07:00 2026-10-16 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-16 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-16 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-16 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261016_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:46:16 2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:46:16 2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과
08:46:16 2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과
08:46:17 2026-10-16 08:46:17 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00121 auc=0.532 out_max=0.4229 (n=135) → 보정 재적용
```

### `logs/20261016_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
10:21:00 2026-10-16 10:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=292ms | quality=1.00 | cache_age=181s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
10:22:00 2026-10-16 10:22:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=262ms | quality=1.00 | cache_age=58s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
14:00:00 2026-10-16 14:00:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=362ms | quality=1.00 | cache_age=102s | exceptions_10m=6 | exc_tags=[CB③-P4]×2 [SHAP]×2 [ExitCooldown]×1 외 1종
14:01:00 2026-10-16 14:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=334ms | quality=1.00 | cache_age=162s | exceptions_10m=5 | exc_tags=[ExitCooldown]×2 [CB③-P4]×1 [Peter2]×1 외 1종
```

### `logs/retrain_eod_20261016.log`
```
--- ConstOut ×1(표본)
??:??:?? | `[51]` | `아직 미확인` | ConstOut 호라이즌 건강도 |
--- 축퇴 ×1(표본)
??:??:?? | `[45]` | `cal_guard_flap_watch` | 축퇴 가드 플래핑 (게이지) |
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261016_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:46:26 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5 | 09:02:36 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=875.72 — 진입 경로가 파라미터를 넘기지 … |
| 10:00 | 장중 초반 | 16 | 09:55:36 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=883.02 — 진입 경로가 파라미터를 넘기지 않… |
| 14:00 | 장중 후반 · 장중 재학습 | 25 | 14:00:29 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=899.64 — 진입 경로가 파라미터를 넘기지 … |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 2 | 15:05:01 [INFO] 청산 LONG @ 885.5 | PnL=-3.24pt (-163,689원) 수수료=1,689원 | 가상:신동시간청산 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:24 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:46 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261016_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:46:11 [WARNING] 기동 시점 결손 1봉 / 검사창 08:45~08:45 (분그리드 기준) — 08:45 | session_bars 보존 여부는 15:46 확정 판정에서 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 20 | 08:50:05 [WARNING] 봉원천=db_fallback(버퍼 0봉)+chart(1봉) 1봉 · 기준봉=08:45 · 구독지연=125.7s |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 39 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 206 | 09:54:00 [WARNING] paintEvent slow 81.5ms | size=1994x950 candles=68 grid=33.1 spans=0.1 candles=2.8 dir=0.3 regime=4.4 markers=… |
| 12:00 | 장중 중간점 | 101 | 11:54:00 [WARNING] acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| 14:00 | 장중 후반 · 장중 재학습 | 214 | 13:54:00 [WARNING] paintEvent slow 106.4ms | size=1994x950 candles=308 grid=32.3 spans=2.3 candles=24.3 dir=1.4 regime=1.1 marke… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 108 | 15:04:00 [WARNING] paintEvent slow 156.6ms | size=1994x950 candles=378 grid=43.6 spans=4.1 candles=40.2 dir=2.3 regime=1.9 marke… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 106 | 15:12:00 [WARNING] paintEvent slow 115.3ms | size=1994x950 candles=386 grid=28.0 spans=3.6 candles=35.9 dir=1.3 regime=1.3 marke… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 140 | 15:34:00 [WARNING] paintEvent slow 105.4ms | size=1994x950 candles=408 grid=20.8 spans=3.7 candles=32.8 dir=1.4 regime=1.3 marke… |
| 15:47 | EOD 재학습(py310_64) 완료 | 2 | 15:45:46 [WARNING] 그리기 78.6ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 761x999 |

- 이 로그 생존구간: 08:46 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261016_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:46:11 [INFO] 활성화 | file=logs\crash_fault.log PID=3744 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 132 | 08:49:03 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 208 | 08:54:09 [INFO] #800 code=A056B raw_time=85409 parsed=08:54:09 price=881.66 vol=1 bid1=881.70 ask1=881.74 flag=49 side=BUY an… |
| 10:00 | 장중 초반 | 271 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 201 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 300 | 13:54:00 [INFO] code=A056B from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 211 | 15:04:00 [INFO] code=A056B from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 182 | 15:12:00 [INFO] code=A056B from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 67 | 15:34:00 [INFO] code=A056B from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 12 | 15:41:35 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:35 |

- 이 로그 생존구간: 08:46 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261016_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:46:07 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.466 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 104 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 172 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 146 | 09:54:00 [WARNING] 신뢰도 미달 34.4% < 42.2% → 강제 X등급 |
| 12:00 | 장중 중간점 | 100 | 11:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 229 | 13:54:00 [WARNING] 신뢰도 미달 35.8% < 46.0% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 60 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:24 [INFO] daily reset complete |

- 이 로그 생존구간: 08:46 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261015 | 15:47 | 로그 본문 |
| 20261014 | 17:41 | 로그 본문 |
| 20261013 | 19:02 | 로그 본문 |
| 20261012 | 18:35 | 로그 본문 |
| 20261009 | 18:33 | 로그 본문 |
| **중앙값** | **18:33** | 기준선 |
| **오늘 20261016** | **15:47** | 로그 본문 |

- 델타 **-166분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 원인
### 결정
### Why
### How to apply
### 검증
### 이상점 1-4 — 피터2 SNS 수신기 오류 재발
### 기타 — 점검 인프라 메모
## 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도 소진: 한도 헤더 계측 · 80초 · reset 백오프) — 🟡 **구현 · 수신기 재기동 완료 · 확장 재로드(사용자) 대기 · 라이브 미검증**
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 n=58 평균순EV=-6062원) · ChaseForeignComboGuard(섀도, C강등후보) 두 섀도 가드가 동시에 걸린 것을 366차 "다음 A등급 신호 라이브 확인" 항목의 실측 데이터 포인트로 추가했다 — 섀도 가드 자체의 활성화 여부는 이번 점검 범위 밖(주간회의 안건).

### 검증
다음 저확신 구간(보정기 출력상한이 발동선 밑으로 떨어지는 날) 재발 시에도 같은 패턴(2회 실패 후 3번째 평가 성공, 또는 11:30 마감까지 미해제)으로 완결되는지 비교 — 라이브 미검증, 표본 1일.

### 이상점 1-4 — 피터2 SNS 수신기 오류 재발
09:12:25~(점검 시각까지 계속) `[Peter2] 수집기 하트비트 없음/지연 … X 페이지 오류: Top` 28회+ — 10-12(39회, 후속8 `4631654`)와 동일 계열 재발. 신규 추종 진입만 간헐 정지, 기존 포지션·실제 체결(09:56·10:19) 영향 없음. P2로 신규 등록, G-2(피터2 수신기 재시도·캐시 보강)로 고도화 제안.

### 기타 — 점검 인프라 메모
`scripts/report_append_marker.py release`가 코웍 리눅스 마운트에서 `os.remove()`로 마커 파일을 못 지웠다(마운트 삭제 권한 미승인 상태 — `.git/index.lock`과 같은 계열의 샌드박스 제약, 치명적이지 않음: `--max-age-sec` 경과 후 다음 acquire가 스테일로 자동 정리). 마커 파일: `data/dailycheck_markers/claude-20261016-intra-cowork-intraday-20261016.json`. 장후 세션이 이 마커를 스테일로 인지하지 못하고 "병행 세션"으로 오판하지 않도록 참고용으로 남긴다.

## 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도 소진: 한도 헤더 계측 · 80초 · reset 백오프) — 🟡 **구현 · 수신기 재기동 완료 · 확장 재로드(사용자) 대기 · 라이브 미검증**

- **사용자 지시**: 「A 수집 장애 조사 → 수정안 구현, 피터2 수집 개선은 `docs/피터2수집/`에 정리」. 장중 점검 1-4 / G-2 의 후속.
- **실측**(`tools/peter2_live/latency_report.py`): 사전등록 합격선 p90 ≤ 90초가 **10-12–10-16 5일 연속 FAIL**(10-16 p50 35초 · p90 383초 · 최대 854초, 오류 있는 분 155/380 = 41%). 오류 군집 14–17분 주기로 4–8분, 15분 창별 PAGE_ERROR 24–30건으로 하루 내내 일정 — 구조적 한도 소진. 10-16 12:52 진입 지시가 13분 늦게 도착해 stale 기각(피터는 −6p, 결과적으로 이득이었지만 운).
- **원인 가설**: 45초 새로고침 + 「새 게시물」 알약 자동 클릭 + X 자체 폴링이 SearchTimeline 15분 창을 소진. 🔴 **10-12 계획서 §B2-① 에 「MW0601·MW0602 같은 X 로그인」(사용자 확인)** — 두 PC 가 예산을 나눠 쓸 가능성. **미확인**.
- **구현**: ① `extension/ratelimit_hook.js` 신규(MAIN world·document_start, fetch/XHR 응답의 `x-rate-limit-*` 읽기 전용 계측 → `meta.rl`) ② `content.js` 알약 클릭 제거·`rl` 하트비트(`null`=미측정) ③ `background.js` `RELOAD_SEC` 45 → 80, 소진(rem=0·429) 시 `reset`+5초까지 대기(30초–16분), 헤더 없으면 종전 120초 ④ `receiver.py` `RATE` 로그(관측 변화 시 1줄)·`collector.json rl`·PAGE_ERROR 한 줄 ⑤ `latency_report.py` 오류분 비율·X 한도 창별 표 ⑥ manifest 1.1.0.
- **의도적으로 안 한 것**: F-4 프로필 폴백(답글형 지시 누락 위험) · F-5 계정 분리(사용자 결정) — F-1 실측으로 「다른 소비자 유무」를 먼저 가린다(`docs/피터2수집/03_다음단계_판정절차.md`). 합격선 무변경.
- **운영 조치**: 구수신기(PID 23328, **10-15 13:43 기동 이래 생존** — 다음 날 `SKIP already running` 으로 옛 코드가 계속 돈 함정) 16:13 종료 → 신버전 PID 9504.
- **검증**: `tests/test_697_peter2_ratelimit.py` 13건 + 611·612·615·668·692 stale·690 trail = **105 passed**(py37_32), `node --check` 3파일. 라이브(X 가 헤더를 노출하는지·경로 정규식 일치)는 확장 재로드 후 첫 거래일에만 확인된다.
- **문서**: `docs/피터2수집/`(README · 01 조사 · 02 구현기록 · 03 판정절차). 01 은 이 세션에 `docs/미륵이고도화3/피터2/` 에서 옮겼다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### MW0601 693차 — 장중 점검 (2026-10-15)
### MW0601 694차 — 장전 점검, 지연 발화 (2026-10-15)
### MW0601 695차 — 장후 트리거, 조기(12:50 KST) 오발화 (2026-10-15)
### MW0601 696차 — 장후 점검, 종합 완성본 (2026-10-15)
### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
### 2026-10-16 (MW0601 — 장전 점검)
### 2026-10-16 (MW0601 — 장중 점검)
### 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도) — 장중 1-4 / G-2 후속
```

미완료 체크박스 **3216건** (끝에서 30건)
```
- [ ] **F-X1 (제안, 미승인)** 종료 핸들러(`main.py`)가 직전 60초 내 MainStall 이력을
- [ ] **F-19 연장 (690차 P1 유지)** 신동/미륵 가상 레그 분리 — 오늘 표본(3원 대사
- [ ] **L-2 (CREON 딥다이브 승계, P1)** `LAUNCH_API.bat:288` "이미 연결됨" 분기 —
- [ ] **L-3 (CREON 딥다이브 승계, P1)** 08:35→08:40 기동 간격 — STEP4 대기를 로그인
- [ ] **L-5 (CREON 딥다이브 승계, P2)** `cybos_autologin.py` 전일 잔존 세션 kill 실패 시
- [ ] **L-6 (CREON 딥다이브 승계, P2)** autologin 단일 인스턴스 락(`data/_autologin.lock`).
- [ ] **L-7 (CREON 딥다이브 승계, P2)** 계좌 불일치 실패 후 잘못된 ID 세션 정리 +
- [ ] **O-t1** 10-16 08:35 무인 기동이 L-1 수정 후 "두 번째 날"에도 끝까지 완주하는지.
- [ ] **O-t2** CREON 로그인 창 "아이디 저장" 값이 프로젝트(cp/dcybos)별 독립인지 —
- [ ] **O-t3** `ConfFloorGuard`(오후 보정기 출력상한<자동진입하한) 재발 여부 — P5-18
- [ ] **O-t4** "장전 점검" 예약작업이 10-16 08:57 KST 근처(±수 분)에 정상 발화하는지.
- [ ] **P5-18 (신규, 판정보류)** 오후 `ConfFloorGuard` 발동(14:55, 보정기 출력상한
- [ ] **F-X1 라이브 확인** 다음 사용자 X 종료 시 SYSTEM 로그 `[Shutdown] intent=user_* … recent_stall…` 꼬리 출현 확인.
- [ ] **E-2 후속(선택)** 실청산 0·가상만 있는 날은 수집기 §5 포지션 블록(`if ex or pe:`)이 안 그려져 가상 장부 표도 안 나온다 — 그런 날이 생기면 블록 조건 확장 검토(A등급).
- [ ] **(C 이월) L-2·L-3·L-5·L-6·L-7** — 위 696차 항목 그대로. 기동·로그인 흐름 변경이라 사용자 결정 후 별도 세션.
- [ ] **(C 이월) P5-18** — 6칸 미완(변경대상·기대효과·회귀위험 미정). O-t3 표본 축적 후 재평가.
- [ ] **CREON-M1 (신규, P0)** 장후 API 세션 정리 — main.py 미실행 시에만 `PlusDisconnect()` 선행호출. 좀비 CpStart/DibServer 생성을 장후에 차단한다(10-16 딥다이브 근본원인). 저녁 수동 세션과 겹치지 않을 시간 조건 — 사용자 결정 필요.
- [ ] **CREON-M2 (신규, P1)** 자동로그인: 좀비(`CpStart` 생존 && `IsConnect=0`) 감지 시 "이미 실행중→예" 자동클릭 금지, 대신 좀비 정리 시도(`PlusDisconnect()` IsConnect 무관 1회 + CpStart 창 WM_CLOSE) → 실패 시 즉시 실패+사유 로그. 정리 수단 실효성 미검증 — …
- [ ] **CREON-M3 (신규, P1)** 자동로그인: coStarter "Unhandled exception" 팝업 자동감지 → 확인클릭 → 크래시 사실 로그 → 240초 대기 생략.
- [ ] **CREON-M4 (관찰 전용)** CREON-M1 적용 후 LAUNCH_API 증상 재평가. 별도 조치 불필요 시 종료.
- [ ] **O-p2 (장중 지속, 격상 없음)** 메인 스레드 블로킹 — 장중에도 4건 추가(09:00:03 3922ms·09:02:01 2063ms 등, 최대 4468ms), 당일 합계 6건. 전부 CB⑤ 실질 임계(5,000ms) 미달이라 경보 대상 아니지만 반복 중 — 장후까지 계속 관찰.
- [ ] **O-p3 (확인 필요, P2)** 커밋 `271ddbd`(머지 커밋) PC명 태그 누락 — 과거 머지 커밋이 태그 예외로 다뤄진 전례가 있는지 미조사. 반복 관측되면 컨벤션 명문화 검토.
- [ ] (O-p2 지속) 메인 스레드 블로킹 당일 합계 6건(최대 4468ms) — 장후 누계로 재평가.
- [ ] **1-4 / G-2 (신규, P2)** 피터2(`tools/peter2_live/receiver.py`) X 페이지 'Top' 탭 조회 실패 재발(오늘 28회+, 10-12 39회와 동일 계열) — 마지막 성공 응답 짧은 캐시 + 재시도, 장시간(예: 5분) 지속 시만 별도 경보로 전환 제안. 적용은 장후 이후 사용자 승인 필요.
- [ ] **O-i1 참고 (366차 연계)** 11:27:00 A급(원시C) 신호에서 GradeEVGuard(A등급 n=58 평균순EV=-6062원)·ChaseForeignComboGuard 섀도 동시 트리거 — 366차 "다음 A등급 라이브 확인" 데이터 포인트 1건 추가. 섀도 가드 활성화 여부는 별개 안건(주간회의).
- [ ] (참고) `report_append_marker.py release`가 코웍 마운트에서 마커 파일을 못 지움(`os.remove` 거부) — 다음 국면(장후) 세션이 이 마커를 "병행 세션"으로 오인하지 않도록 유의. 삭제 권한 요청은 하지 않음(경미, max-age 경과로 자연 정리됨).
- [ ] **697-1 (사용자, 10-19 장전까지)** `chrome://extensions` → Mireuk Peter2 Collector 새로고침, 버전 **1.1.0** 확인. 안 하면 F-1–F-3 미적용.
- [ ] **697-2 (10-19 장후)** `python tools/peter2_live/latency_report.py 2026-10-19` — ① `RATE` 줄 존재(없으면 `docs/피터2수집/02` §5) ② 사전등록 p90 ≤ 90초 판정 ③ 창별 rem 감소폭 vs 우리 관측 수 → 다른 소비자 유무. 판정 나무: `docs/피터2수집/…
- [ ] **697-3 (조건부, 사용자 결정)** 697-2 가 공유 소비를 보이면 F-5 계정 분리(MW0601 전용 X 계정 — 조율 불필요). 혼자 소진이면 RELOAD_SEC 역산, 그래도 FAIL 이면 F-4 프로필 폴백(답글형 지시 비율 선측정).
- [ ] **697-4 (장전 점검 항목)** `python tools/peter2_live/receiver.py --check` 의 `started` 가 당일 아침인지 — 10-15 13:43 수신기가 10-16 장 마감까지 살아 옛 코드로 돌았다.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
— main.py 미실행 시에만 `PlusDisconnect()` 선행호출. 좀비 CpStart/DibServer 생성을 장후에 차단한다(10-16 딥다이브 근본원인). 저녁 수동 세션과 겹치지 않을 시간 조건 — 사용자 결정 필요.
- [ ] **CREON-M2 (신규, P1)** 자동로그인: 좀비(`CpStart` 생존 && `IsConnect=0`) 감지 시 "이미 실행중→예" 자동클릭 금지, 대신 좀비 정리 시도(`PlusDisconnect()` IsConnect 무관 1회 + CpStart 창 WM_CLOSE) → 실패 시 즉시 실패+사유 로그. 정리 수단 실효성 미검증 — 다음 좀비 재현일 1회 시험 필요.
- [ ] **CREON-M3 (신규, P1)** 자동로그인: coStarter "Unhandled exception" 팝업 자동감지 → 확인클릭 → 크래시 사실 로그 → 240초 대기 생략.
- [ ] **CREON-M4 (관찰 전용)** CREON-M1 적용 후 LAUNCH_API 증상 재평가. 별도 조치 불필요 시 종료.
  ⚠ 위 4개는 본 파일 기존 M-1~M-4(라인 1364 부근, EOD NetRecon·섀도전략 손익 — 무관한 안건)와 ID가 겹쳐 `CREON-` 접두로 구분했다. 기존 M-1~M-4는 변경 없음.
- [x] **O-p1 — 장중 판정 완료: 해소.** 10-16 10:25:00 `[SHS-EKS] EKS 자동 해제 … z_warn=0` 로그로 09:00 이후 매분 루프에서 경고 피처 수가 0개로 완전 수렴 확인 — 프리마켓 웜업 단계의 정상 요동이었음.
- [ ] **O-p2 (장중 지속, 격상 없음)** 메인 스레드 블로킹 — 장중에도 4건 추가(09:00:03 3922ms·09:02:01 2063ms 등, 최대 4468ms), 당일 합계 6건. 전부 CB⑤ 실질 임계(5,000ms) 미달이라 경보 대상 아니지만 반복 중 — 장후까지 계속 관찰.
- [ ] **O-p3 (확인 필요, P2)** 커밋 `271ddbd`(머지 커밋) PC명 태그 누락 — 과거 머지 커밋이 태그 예외로 다뤄진 전례가 있는지 미조사. 반복 관측되면 컨벤션 명문화 검토.


### 2026-10-16 (MW0601 — 장중 점검)
- [x] (O-p1 해소) CanaryShadow z-경고 변동 — 10:25 `z_warn=0`로 수렴 확인(위 NEXT_TODO O-p1 항목에 직접 반영).
- [ ] (O-p2 지속) 메인 스레드 블로킹 당일 합계 6건(최대 4468ms) — 장후 누계로 재평가.
- [ ] **1-4 / G-2 (신규, P2)** 피터2(`tools/peter2_live/receiver.py`) X 페이지 'Top' 탭 조회 실패 재발(오늘 28회+, 10-12 39회와 동일 계열) — 마지막 성공 응답 짧은 캐시 + 재시도, 장시간(예: 5분) 지속 시만 별도 경보로 전환 제안. 적용은 장후 이후 사용자 승인 필요.
- [ ] **O-i1 참고 (366차 연계)** 11:27:00 A급(원시C) 신호에서 GradeEVGuard(A등급 n=58 평균순EV=-6062원)·ChaseForeignComboGuard 섀도 동시 트리거 — 366차 "다음 A등급 라이브 확인" 데이터 포인트 1건 추가. 섀도 가드 활성화 여부는 별개 안건(주간회의).
- [ ] (참고) `report_append_marker.py release`가 코웍 마운트에서 마커 파일을 못 지움(`os.remove` 거부) — 다음 국면(장후) 세션이 이 마커를 "병행 세션"으로 오인하지 않도록 유의. 삭제 권한 요청은 하지 않음(경미, max-age 경과로 자연 정리됨).

### 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도) — 장중 1-4 / G-2 후속
- [ ] **697-1 (사용자, 10-19 장전까지)** `chrome://extensions` → Mireuk Peter2 Collector 새로고침, 버전 **1.1.0** 확인. 안 하면 F-1–F-3 미적용.
- [ ] **697-2 (10-19 장후)** `python tools/peter2_live/latency_report.py 2026-10-19` — ① `RATE` 줄 존재(없으면 `docs/피터2수집/02` §5) ② 사전등록 p90 ≤ 90초 판정 ③ 창별 rem 감소폭 vs 우리 관측 수 → 다른 소비자 유무. 판정 나무: `docs/피터2수집/03_다음단계_판정절차.md`.
- [ ] **697-3 (조건부, 사용자 결정)** 697-2 가 공유 소비를 보이면 F-5 계정 분리(MW0601 전용 X 계정 — 조율 불필요). 혼자 소진이면 RELOAD_SEC 역산, 그래도 FAIL 이면 F-4 프로필 폴백(답글형 지시 비율 선측정).
- [ ] **697-4 (장전 점검 항목)** `python tools/peter2_live/receiver.py --check` 의 `started` 가 당일 아침인지 — 10-15 13:43 수신기가 10-16 장 마감까지 살아 옛 코드로 돌았다.

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

### `data/dailycheck_markers/claude-20261016-intra-cowork-intraday-20261016.json` — 176B · 10-16 12:32:56
```json
{
 "pc": "claude",
 "date": "20261016",
 "phase": "intra",
 "session": "cowork-intraday-20261016",
 "pid": 5,
 "started_epoch": 1792121576.178322,
 "started_at": "2026-10-16 03:32:56"
}
```

### `data/dailycheck_markers/claude-20261016-post-cowork-post-20261016.json` — 172B · 10-16 16:18:59
```json
{
 "pc": "claude",
 "date": "20261016",
 "phase": "post",
 "session": "cowork-post-20261016",
 "pid": 6,
 "started_epoch": 1792135138.7896242,
 "started_at": "2026-10-16 07:18:58"
}
```

### `data/dailycheck_markers/claude-20261016-pre-cowork-premarket-20261016.json` — 176B · 10-16 09:03:44
```json
{
 "pc": "claude",
 "date": "20261016",
 "phase": "pre",
 "session": "cowork-premarket-20261016",
 "pid": 7,
 "started_epoch": 1792109024.4614692,
 "started_at": "2026-10-16 00:03:44"
}
```

### `data/heartbeat_MW0601_20261016.json` — 243B · 10-16 15:46:48
```json
{
 "pid": 3744,
 "written_at": "2026-10-16T15:46:48",
 "beat_epoch": 1792133205.654178,
 "beat_age_sec": 2.8,
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

### `data/peter2_live/trail_state_2026-10-16.json` — 51B · 10-16 14:00:53
```json
{
 "date": "2026-10-16",
 "trail": null,
 "ghosts": []
}
```

### `data/peter_feed/_raw/2026-10-16.jsonl` — 8.4KB · 10-16 15:21:28
```json
JSONL 38행 ⏎ 첫: {"id": "2110884042296139904", "dt": "2026-10-16T00:02:28.000Z", "text": "장 시작 세팅은 상방 세팅 아닙니다.\n\n중간에 바뀔 수 있으니 바뀌면 전달합니다.", "seen_at": "2026-10-16T09:02:44+09:00", "src": "live"} | {"id": "2110890967062728954", "dt": "2026-10-16T00:29:59.000Z", "text": "오늘 삼전닉스 시세 나는 건 힘들고.\n\n일부 소부장과\n그동안 눌렸던 다른 종목들 움직이는 종목장세.\n----------------------------------------\n\n어제 방송보고 오전에 눌렸다고 바로 매수 들어갈까봐\n\n8시 9분에 1차 메세지\n\n9시 2분에 2차 메세지.\n-------------------------------------------", "seen_at": "2026-10-16T09:34:13+09:00", "src": "live"} | {"id": "2110893046778953914", "dt": "2026-10-16T00:38:15.000Z", "text": "은혼식 해야되요 ㅋ", "seen_at": "2026-10-16T09:38:43+09:00", "src": "live"} ⏎ 끝: {"id": "2110971194883424353", "dt": "2026-10-16T05:48:47.000Z", "text": "", "seen_at": "2026-10-16T14:49:13+09:00", "kind": "empty", "src": "live"} | {"id": "2110971107700592842", "dt": "2026-10-16T05:48:26.000Z", "text": "", "seen_at": "2026-10-16T14:49:13+09:00", "kind": "empty", "src": "live"} | {"id": "2110979338598568036", "dt": "2026-10-16T06:21:09.000Z", "text": "875 아니면 880인데. 둘다 맥점입니다.\n\n이 이하에서 끝나면 다음주에 \n\n최소 하방 한방 더 남았다고 생각하고 매매 시나리오 짜시는게 좋습니다.\n\n오늘 방송에서 뵙겠습니다.\n\n저는 여러분의 사랑을 먹고 삽니다.", "seen_at": "2026-10-16T15:21:28+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-16 15:53:34**

| 키 | 값 | 수집 대상일(2026-10-16)과 일치 |
|---|---|---|
| `date` | 2026-10-16 | 예 |
| `p8_last_success_date` | 2026-10-16 | 예 |
| `eod_retrain_ok_date` | 2026-10-16 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-16 08:55:06 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-15) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-16 08:55:06 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-15) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261016_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 3744: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:46:11 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 3744 | 08:46:11 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 234개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261016-점검리포트.md` | 35.4KB | 10-16 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_intra.md` | 80.4KB | 10-16 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_pre.md` | 59.8KB | 10-16 08:59 |
| `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` | 6.5KB | 10-16 08:51 |
| `docs/정기점검/매일점검/MW0601-20261015-점검리포트.md` | 69.1KB | 10-15 17:48 |
| `docs/정기점검/매일점검/_tmp_append_post_20261015.md` | 33.9KB | 10-15 16:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261015_post.md` | 105.6KB | 10-15 16:18 |
| `docs/정기점검/매일점검/MW0601-20261015-CREON런처기동흐름-딥다이브.md` | 23.4KB | 10-15 14:22 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261016.json` | 3.1KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261016.md` | 5.4KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261016.json` | 38.9KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20261016.md` | 32.1KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261016.json` | 127.6KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261016.md` | 193.6KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261008.json` | 3.0KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261008.md` | 5.0KB | 10-08 15:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MAX_CONTRACTS` = `1` (기대 `3`) — 431차 10→3 인하. 실전 자본 확정 시 재산출 대상
2. `logs/20261016_WARN.log`: ERROR 이상 1건
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. **엔진 진입 0건 / 계좌 진입 4건**(그중 외부표식 0건 · 피터2 4건 · 판별불가 0건 · 별도 가상 장부 7건) — 차단 50건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
5. 포지션 4건 중 최종청산이 하드스톱·손절 계열 **4건(100%)** — 손절 준수율 확인 필요 (레그 4행)
6. **SYSTEM 로그가 직전 5거래일 중앙값(18:33)보다 166분 이르게 끝났다** (오늘 15:47) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
7. `logs/20261016_WARN.log`: **[Brier] 과신** 2건(표본)
8. `logs/20261016_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20261016_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20261016_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20261016_LEARNING.log`: **축퇴** 8건(표본)
12. `logs/retrain_eod_20261016.log`: **축퇴** 1건(표본)
13. `logs/retrain_eod_20261016.log`: **ConstOut** 1건(표본)
14. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
15. PC명 태그 누락 커밋 1건 — 멀티PC 컨벤션 위반
16. 미커밋 변경 161건 (실질 17건 · **코드(.py) 2건**) — 코드 변경이 커밋되지 않았다
17. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261016*.log` (Windows) / `grep 강제청산 logs/*20261016*.log`*