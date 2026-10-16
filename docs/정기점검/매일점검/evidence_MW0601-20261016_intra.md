# 미륵이 증거 다이제스트 — 2026-10-16 / INTRA

- 생성 2026-10-16 12:26:32 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01dfp954gt5ur5pc2ulw7mzb/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261016` · `2026-10-16` · `261016` · `1016`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **33개** 파일 · 33개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-pre-cowork-premarket-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261016-pre-cowork-premarket-20261016.json` | 176B | 10-16 09:03 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261016.log` | 136B | 10-16 07:21 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261016.log` | 124B | 10-16 08:45 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261016.log` | 140B | 10-16 08:45 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261016.json` | 241B | 10-16 12:26 |
| `launcher_{DATE}_084001_2887.log` | 1 | `logs/Mireuk_batch/launcher_20261016_084001_2887.log` | 959B | 10-16 08:40 |
| `launcher_{DATE}_084533_3971.log` | 1 | `logs/Mireuk_batch/launcher_20261016_084533_3971.log` | 1.3MB | 10-16 12:26 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261016.log` | 173B | 10-16 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261016.log` | 40.0KB | 10-16 12:20 |
| `position_state.json.gen_{DATE}_101227` | 1 | `data/position_state.json.gen_20261016_101227` | 1.5KB | 10-16 09:56 |
| `position_state.json.gen_{DATE}_101955` | 1 | `data/position_state.json.gen_20261016_101955` | 1.5KB | 10-16 10:19 |
| `position_state.json.gen_{DATE}_111919` | 1 | `data/position_state.json.gen_20261016_111919` | 1.5KB | 10-16 11:03 |
| `retrain_intraday_20260709_{DATE}00.log` | 1 | `logs/retrain_intraday_20260709_101600.log` | 4.6KB | 07-09 10:16 |
| `retrain_intraday_{DATE}_102500.log` | 1 | `logs/retrain_intraday_20261016_102500.log` | 5.7KB | 10-16 10:25 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261016.log` | 49.7KB | 10-16 12:20 |
| `trail_state_{DATE}.json` | 1 | `data/peter2_live/trail_state_2026-10-16.json` | 336B | 10-16 11:19 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-16.jsonl` | 1.8KB | 10-16 10:20 |
| `{DATE}_0910_D.xls` | 1 | `data/db/option_hts/261016_0910_D.xls` | 482.8KB | 10-16 09:10 |
| `{DATE}_0943_D.xls` | 1 | `data/db/option_hts/261016_0943_D.xls` | 482.9KB | 10-16 09:43 |
| `{DATE}_1017_D.xls` | 1 | `data/db/option_hts/261016_1017_D.xls` | 483.0KB | 10-16 10:17 |
| `{DATE}_1047_D.xls` | 1 | `data/db/option_hts/261016_1047_D.xls` | 483.0KB | 10-16 10:47 |
| `{DATE}_1120_D.xls` | 1 | `data/db/option_hts/261016_1120_D.xls` | 483.0KB | 10-16 11:20 |
| `{DATE}_DATA.log` | 1 | `logs/20261016_DATA.log` | 229.8KB | 10-16 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261016_DEBUG.log` | 137.7KB | 10-16 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261016_HEALTH.log` | 1.7KB | 10-16 12:09 |
| `{DATE}_HOGA.log` | 1 | `logs/20261016_HOGA.log` | 32.0MB | 10-16 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261016_LEARNING.log` | 183.6KB | 10-16 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20261016_MICRO.log` | 609.3KB | 10-16 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20261016_PROBE.log` | 55.3KB | 10-16 12:25 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261016_SIGNAL.log` | 256.3KB | 10-16 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261016_SYSTEM.log` | 576.6KB | 10-16 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20261016_TRADE.log` | 10.4KB | 10-16 11:31 |
| `{DATE}_WARN.log` | 1 | `logs/20261016_WARN.log` | 407.6KB | 10-16 12:26 |

## 2. 코드·커밋 상태

- HEAD `51d5de4` · 브랜치 `v9-dev` · 미커밋 136건 · 실질 변경 6건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 6 · 미추적 130 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.9초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md
 M docs/미륵이고도화3/신동2/학습/lessons.json
 M docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md
 M docs/미륵이고도화3/신동2/학습/추이_MW0601.md
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
?? dev_memory/_tmp_append_nexttodo_20261013_intra.md
?? dev_memory/_tmp_append_nexttodo_20261015_post.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261014.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261015.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261016.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261012.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261013.md
… 외 96건
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

_본문 미열람(설정): `20261016_HOGA.log` 32.0MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/20개 (중요도순). 제외: `20261016_MICRO.log`, `20261016_DATA.log`, `20261016_PROBE.log`, `launcher_20261016_084533_3971.log`, `launcher_20261016_084001_2887.log`, `20261016_DEBUG.log`, `shindong2_20261016.log`, `peter2_receiver_20261016.log`_

### `logs/20261016_TRADE.log` — 10.4KB · 74행 · 최종 11:31:00

- 형식 평문 · 시각 인식 74행 · WARNING=7, INFO=67

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:26 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-16 08:46:31 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-16 09:02:36 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 875.72 | 손절=882.26 1차=-9124.28(×1.00) 2차=-9124.28
2026-10-16 09:02:36 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=875.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-10-16 09:02:36 [INFO] TRADE: [Virtual] 신동 가상진입 SHORT 1계약 @875.72 손절 882.26 목표 862.50 (principal)
  …
2026-10-16 11:27:00 [INFO] TRADE: [진입체크] LONG→LONG 1계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi❌ fore❌ prev❌ time✅ risk✅ chas❌ coun✅ | conf=51.5%
2026-10-16 11:27:00 [INFO] TRADE: [Position] 진입 LONG 1계약 @ 888.88 | 손절=886.39 1차=889.38(×0.30) 2차=891.37 horizon=1m hurst=neutral
2026-10-16 11:27:00 [INFO] TRADE: [Virtual] 미륵 가상진입 LONG 1계약 @888.88 손절 886.39 (principal)
2026-10-16 11:31:00 [INFO] TRADE: [Position] 청산 LONG @ 886.39435 | PnL=-2.49pt (-125,971원) 수수료=1,689원 | 가상:하드스톱
2026-10-16 11:31:00 [INFO] TRADE: [Virtual] 미륵 가상청산 LONG 1계약 @886.39 가상:하드스톱 | -2.49pt -125,971원 (포지션 종료)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 7 | 09:02:36 | 11:08:36 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=875.72 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×74

**컴포넌트 상위 15** — `Position`×19, `Virtual`×12, `Chejan`×12, `PositionFallback`×7, `Peter2Trail`×7, `Peter2`×4, `주문요청`×4, `체결진입`×2, `TickStop-S0C`×2, `청산 완료`×2, `ProfitGuard`×1, `Sizer`×1, `진입체크`×1

### `logs/20261016_WARN.log` — 407.6KB · 1827행 · 최종 12:26:32

- 형식 평문 · 시각 인식 1827행 · CRITICAL=1, WARNING=1826

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:11 [WARNING] SYSTEM: [BarGap] 기동 시점 결손 1봉 / 검사창 08:45~08:45 (분그리드 기준) — 08:45 | session_bars 보존 여부는 15:46 확정 판정에서
2026-10-16 08:46:34 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-16 08:46:34 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-10-16 08:46:34 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-16 08:46:34 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
  …
2026-10-16 12:26:21 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 89.2ms | size=1994x950 candles=220 grid=30.8 spans=1.3 candles=12.2 dir=0.8 regime=0.7 markers=28.8 axes=13.1 cross=0.0 | slow_cnt=1580 total_cnt=1802 overlay_cnt=22082
2026-10-16 12:26:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 115.3ms | size=1994x950 candles=220 grid=50.0 spans=1.2 candles=13.5 dir=0.9 regime=0.8 markers=35.5 axes=11.3 cross=0.0 | slow_cnt=1581 total_cnt=1803 overlay_cnt=22095
2026-10-16 12:26:36 [WARNING] SYSTEM: [LiveDBG] _fetch_investor_data 지연 523ms — 메인 스레드 523ms 점유 (live 중단 원인 후보)
2026-10-16 12:26:36 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 91.1ms | size=1994x950 candles=220 grid=31.4 spans=1.1 candles=12.4 dir=1.0 regime=0.8 markers=30.9 axes=11.9 cross=0.0 | slow_cnt=1582 total_cnt=1804 overlay_cnt=22101
2026-10-16 12:26:47 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 111.1ms | size=1994x950 candles=220 grid=38.6 spans=1.1 candles=13.6 dir=0.8 regime=0.7 markers=38.5 axes=16.2 cross=0.0 | slow_cnt=1583 total_cnt=1805 overlay_cnt=22111
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

**WARNING — 태그 34종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1583 | 08:55:36 | 12:26:47 | paintEvent slow 45.0ms | size=1994x950 candles=9 grid=24.8 spans=0.0 candles=0.3 dir=0.0 regime=0.0 markers=0.0 axes=18.7 cross=0.0 | slow_cnt=1 total_cnt=71 overlay_cnt=339 |
| `LiveDBG` | 67 | 08:46:34 | 12:26:36 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 40 | 09:03:59 | 12:24:36 | 그리기 59.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 790x1001 |
| `Peter2` | 29 | 09:12:25 | 12:20:41 | 수집기 하트비트 없음/지연(정상수집 91초 전 · X 페이지 오류: Top) — 신규 추종 진입 정지. Chrome 확장·수신기(tools/peter2_live) 확인 |
| `ChejanFlow` | 12 | 09:56:03 | 11:19:19 | account='783343908' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='453' | pending='ENTRY:SHORT qty=1 filled=0 order_no=? reason=진입 req_at=09:56:03.579' | positio… |
| `ChejanMatch` | 12 | 09:56:03 | 11:19:19 | order_no='453' | pending='ENTRY:SHORT qty=1 filled=0 order_no=453 reason=진입 req_at=09:56:03.579' | pending_matched=True |
| `ScalerRefresh` | 8 | 09:08:00 | 12:08:00 | 5분 누적 수익률 +0.517% (임계 ±0.489%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PendingOrder` | 8 | 09:56:03 | 11:19:19 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 882.88, 'reason': '진입', 'hint_source': '', 'atr': 2.0771, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qt… |
| `CB③-P4` | 8 | 10:50:00 | 11:54:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=20.0%) |
| `SHS-EKS` | 6 | 09:05:00 | 10:25:00 | Early Kill Switch 발동 conf_max=35.0% < 발동선=44.6%(mc=46.6%-margin2.0%p) core_pass=0/5봉(측정 0봉) | bars=5 (delayed=0 policy=4 conf측정=1) core측정=0봉 | 보정기 상한=34.3% auc=0.556 state=unreachable ⇒ 구조적 도달불가(상한<발동선 — 이 판정은 시장이 아니라 보정기를 잰 것) → 일시 관망 (09… |
| `Health` | 5 | 09:26:00 | 12:08:00 | level=WARNING degraded=OFF | latency=296ms | quality=1.00 | cache_age=183s | exceptions_10m=0 |
| `Peter2Offset` | 4 | 08:47:05 | 10:47:05 | A056B 실측=-2.29 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-2.29 | 직전일=-2.12(prev_day:2026-10-15, safe=True) 차=-0.17 | 57ms |

**채널** — `SYSTEM`×1822, `HEALTH`×5

**컴포넌트 상위 15** — `ChartDBG`×1583, `LiveDBG`×67, `OptionFlowChart`×40, `Peter2`×29, `ChejanFlow`×12, `ChejanMatch`×12, `ScalerRefresh`×8, `PendingOrder`×8, `CB③-P4`×8, `SHS-EKS`×7, `Health`×5, `Peter2Offset`×4, `ExitCooldown`×4, `SHAP`×4, `EntryAttempt`×3

### `logs/20261016_SYSTEM.log` — 576.6KB · 3912행 · 최종 12:26:12

- 형식 평문 · 시각 인식 3900행 · INFO=3900, PLAIN=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:11 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=3744 | 행감지=30s all_threads=True
2026-10-16 08:46:11 [INFO] SYSTEM: [DBInit] 합계 0.51s | predictions=0.06s trades=0.25s daily_stats=0.01s shap=0.02s raw_data=0.13s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-16 08:46:11 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-16 08:46:11 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-16 08:46:11 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-16 12:26:35 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-344,foreign:+41,institution:+310} amt_mn={individual:-76250,foreign:+5629,institution:+72083}
2026-10-16 12:26:35 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-344,foreign:+41,institution:+310} amt_mn={individual:-76250,foreign:+5629,institution:+72083}
2026-10-16 12:26:35 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-56266 nonarb=-114786
2026-10-16 12:26:35 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-56266 nonarb=-114786
2026-10-16 12:26:42 [INFO] SYSTEM: [TickUI] alive ticks=83708 code=A056B close=889.18
```

</details>

**채널** — `SYSTEM`×3900

**컴포넌트 상위 15** — `CybosRT-TICK`×842, `CybosInvestorRaw`×824, `PumpGuard`×381, `TickUI`×219, `CybosRT-ROLLOVER`×219, `BAR-CLOSE`×219, `CVD-ANCHOR`×219, `S6Detail`×207, `PipePerf`×207, `System`×58, `MicroRegime`×57, `OptionChain`×43, `OptionBook`×41, `RegimeFingerprint`×38, `Peter2`×30

### `logs/20261016_SIGNAL.log` — 256.3KB · 2334행 · 최종 12:26:00

- 형식 평문 · 시각 인식 2334행 · WARNING=655, INFO=1679

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.466
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.448
  …
2026-10-16 12:26:00 [INFO] SIGNAL: [MetaGate] 편향패널티: dir=1 buf=30 pen=0.039 blended 0.400→0.361
2026-10-16 12:26:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.1% grade=X regime=NEUTRAL
2026-10-16 12:26:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-10-16 12:26:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=34.1% grade=X micro=횡보장
2026-10-16 12:26:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.341<mc0.650)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 450 | 09:00:01 | 12:08:01 | 1m 'macro_vix' scale=0.0315 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 60 | 09:06:00 | 12:15:00 | 신뢰도 미달 33.9% < 42.2% → 강제 X등급 |
| `WeightCollapse` | 51 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `Model` | 48 | 09:00:00 | 11:23:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 36 | 09:00:00 | 11:23:00 | ts=08:59 horizon=1m age=3m max_z=+7.51(cancel_add_ratio) extreme=1 adj=1 |
| `ConstOut` | 9 | 09:36:00 | 12:14:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3519 < 필요 0.4360 (conf_floor=0.330, min_conf=0.436, span=0.0043, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×2334

**컴포넌트 상위 15** — `ScalerFloor`×498, `SIGNAL`×414, `MetaGate`×214, `Ensemble`×205, `ZeroDiag`×205, `FQAdj`×169, `InstabilityGate`×66, `Checklist`×63, `Model`×60, `MicroRegime`×57, `WeightCollapse`×51, `ATR-Horizon`×51, `ScalerMonitor`×36, `SHS-EKS`×34, `차단`×28

### `logs/20261016_LEARNING.log` — 183.6KB · 1698행 · 최종 12:26:00

- 형식 평문 · 시각 인식 1698행 · WARNING=148, INFO=1550

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:13 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:17 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00121 auc=0.532 out_max=0.4229 (n=135) → 보정 재적용
  …
2026-10-16 12:26:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0934% buf_n=20 nonzero=20 prev_p=889.34 cur_p=889.12
2026-10-16 12:26:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=33.3% 예측=UP 실제=FL)
2026-10-16 12:26:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=55.5% 예측=FL 실제=DN)
2026-10-16 12:26:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=37.4% 예측=DN 실제=FL)
2026-10-16 12:26:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=0.0%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 48 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 41 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 24 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 17 | 08:46:17 | 08:46:25 | 축퇴 감지 — span=0.00084 auc=0.529 out_max=0.2880 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 10 | 08:46:17 | 09:29:00 | 축퇴 감지 — span=0.00108 auc=0.453 out_max=0.3129 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 6 | 08:46:17 | 08:46:25 | 축퇴 감지 — span=0.00051 auc=0.520 out_max=0.3781 (기준 auc<0.53 and span<0.020, 기저율=0.3778 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 2 | 10:13:00 | 11:23:00 | 하한 도달불가 — out_max=0.3259 < conf_floor=0.3300 (span=0.01254 auc=0.572 out_max=0.3259, 기저율=0.3200 n=200) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×1698

**컴포넌트 상위 15** — `LEARNING`×647, `SGD`×206, `sigma`×194, `Bias⚠`×145, `Calibration:1m`×94, `Calibration:30m`×81, `Bias`×62, `OnlineLearner`×56, `Calibration:3m`×46, `MetaConf`×39, `Calibration:5m`×33, `BiasReset`×21, `ScalerWarmup`×20, `Calibration:10m`×19, `Calibration:15m`×12

### `logs/20261016_HEALTH.log` — 1.7KB · 11행 · 최종 12:09:00

- 형식 평문 · 시각 인식 11행 · WARNING=5, INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 09:26:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=296ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-10-16 09:27:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=296ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[Peter2]×1
2026-10-16 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 295ms (표본 20분)
2026-10-16 10:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=292ms | quality=1.00 | cache_age=181s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
2026-10-16 10:22:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=262ms | quality=1.00 | cache_age=58s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
  …
2026-10-16 10:27:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=498ms | quality=1.00 | cache_age=175s | exceptions_10m=1 | exc_tags=[SHS-EKS]×1
2026-10-16 11:13:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=286ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-10-16 11:14:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=307ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[Peter2]×1
2026-10-16 12:08:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=657ms | quality=1.00 | cache_age=181s | exceptions_10m=5 | exc_tags=[Peter2]×3 [SHAP]×2
2026-10-16 12:09:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=328ms | quality=1.00 | cache_age=57s | exceptions_10m=5 | exc_tags=[Peter2]×3 [SHAP]×2
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 5 | 09:26:00 | 12:08:00 | level=WARNING degraded=OFF | latency=296ms | quality=1.00 | cache_age=183s | exceptions_10m=0 |

**채널** — `HEALTH`×11

**컴포넌트 상위 15** — `Health`×10, `HealthTrend`×1

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

### `logs/retrain_intraday_20260709_101600.log` — 4.6KB · 39행 · 최종 10:16:34

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a8266270.json
2026-07-09 10:16:02,578 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-09 10:16:34,710 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.35s | old_acc=nan)
2026-07-09 10:16:34,714 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-09 10:16:34,714 [INFO] LEARNING: [Retrain] 완료 | 32.1초 | 성공=6/6 호라이즌
2026-07-09 10:16:34,716 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.0s 데이터=20000행
2026-07-09 10:16:34,719 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a8266270.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) | 8 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 2 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 6 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 28 |
| 사이저 호출(`[Sizer]`) | 1 |

> 🔴 **엔진 진입 0건인데 계좌 체결 2건**(외부표식 0 · 피터2 2 · 판별불가 0) — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.
>
> 별도로 **가상 장부 진입 6건**이 `[Position] 진입` 에 섞여 있다 — 실주문이 없으므로 계좌 체결·손익과 무관하다(아래 「가상 장부」 표).

### 포지션 2건 · 승 1 (50%) · 합계 -2.28pt (-117,368원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:56:03 | 피터2 | SHORT | 1 | — | 1 | -4.94 | -248,677 | 하드스톱(틱) |
| 10:19:55 | 피터2 | SHORT | 1 | — | 1 | +2.66 | +131,309 | 하드스톱(틱) |

**출처별 소계** — 피터2 2건 -117,368원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「피터2」는 `[Peter2] 진입`이 동반된 보조 로직 자리로 역시 엔진 성적이 아니다. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**가상 장부 6건(청산 6 · 합계 -409,361원) — 실주문 없음, 엔진·계좌 손익 아님**

| 진입 | 주체 | 방향 | 수량 | hz | 가상 pt | 가상 net(원) | 가상 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:02:36 | 신동 | SHORT | 1 | — | +3.26 | +161,336 | 가상:신동1차 |
| 09:55:36 | 신동 | LONG | 1 | — | -2.12 | -107,678 | 가상:하드스톱 |
| 10:07:36 | 신동 | LONG | 1 | — | -4.10 | -206,683 | 가상:하드스톱 |
| 10:33:36 | 신동 | LONG | 1 | — | -6.54 | -328,687 | 가상:하드스톱 |
| 11:08:36 | 신동 | LONG | 1 | — | +4.00 | +198,322 | 가상:신동1차 |
| 11:27:00 | 미륵 | LONG | 1 | 1m | -2.49 | -125,971 | 가상:하드스톱 |

> ⚠ 이 표는 `[Virtual] … 가상진입`/`가상청산` 로그로 조립한 **가상 장부**다. 같은 초에 `[Position] 진입` 이 찍혀 진입 건수에는 잡히지만 체결이 없다 — 3원 대사(로그·DB·브로커)에서 로그 쪽이 더 많아 보이면 먼저 이 표를 뺄 것.

**청산 레그 2행** (부분청산 0 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:12:27 | 전량 | 1 | -4.94 | -248,677 | 하드스톱(틱) |
| 11:19:19 | 전량 | 1 | +2.66 | +131,309 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×2

> 최종 청산이 하드스톱·손절 계열인 포지션 2/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -117,368 = 포지션합 -117,368 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### 진입 8건

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

계약수 분포 — 1계약×8

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `ofi`×1, `fore`×1, `prev`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1

실제 진입 계약수 — **1계약**×8

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×1

### 차단 사유 28건 · 5종

| 건수 | 사유 |
|---|---|
| 16 | SHS-EKS 당일 관망 활성 — conf35%미달 |
| 9 | 등급X — 미통과 항목: 2_confidence |
| 1 | 청산 후 쿨다운 — 87초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 27초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |

**체크리스트 미통과 항목 누적** — `2_confidence`×9, `3_vwap`×1, `4_cvd`×1, `5_ofi`×1, `6_foreign`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 6건 · 최대 4468ms · 5초 초과 0건

상위 — 4468ms, 4407ms, 3922ms, 3765ms, 2344ms, 2063ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261016_WARN.log`
```
--- [Brier] 과신 ×2(표본)
10:01:00 2026-10-16 10:01:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.350 > 0.35
10:02:00 2026-10-16 10:02:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.361 > 0.35
--- [CB] ×1(표본)
10:12:27 2026-10-16 10:12:27 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×5(표본)
10:12:27 2026-10-16 10:12:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:15:27)
10:12:27 2026-10-16 10:12:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:15:27)
10:21:00 2026-10-16 10:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=292ms | quality=1.00 | cache_age=181s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
11:19:19 2026-10-16 11:19:19 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:21:19)
--- [SHAP] 슬로우 ×4(표본)
11:40:01 2026-10-16 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 903ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:00:01 2026-10-16 12:00:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1031ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:06:01 2026-10-16 12:06:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1062ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:20:01 2026-10-16 12:20:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1036ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×6(표본)
08:46:39 2026-10-16 08:46:39 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4407ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4407 band=INFO since_pipe_s=NA
08:46:42 2026-10-16 08:46:42 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3765ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3765 band=INFO since_pipe_s=NA
09:00:03 2026-10-16 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3922 band=INFO since_pipe_s=0.1
09:02:01 2026-10-16 09:02:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2063 band=INFO since_pipe_s=0.0
```

### `logs/20261016_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:00 2026-10-16 09:36:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4151) | 앙상블 제외는 유지
09:44:00 2026-10-16 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4189) | 앙상블 제외는 유지
09:59:00 2026-10-16 09:59:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4637) | 앙상블 제외는 유지
10:23:00 2026-10-16 10:23:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4036) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-10-16 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:06:00 2026-10-16 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-10-16 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:17:00 2026-10-16 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
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
--- [ExitCooldown] ×2(표본)
10:21:00 2026-10-16 10:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=292ms | quality=1.00 | cache_age=181s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
10:22:00 2026-10-16 10:22:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=262ms | quality=1.00 | cache_age=58s | exceptions_10m=3 | exc_tags=[Peter2]×2 [ExitCooldown]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261016_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:46:26 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5 | 09:02:36 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=875.72 — 진입 경로가 파라미터를 넘기지 … |
| 10:00 | 장중 초반 | 16 | 09:55:36 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=883.02 — 진입 경로가 파라미터를 넘기지 않… |

- 이 로그 생존구간: 08:46 ~ 11:31

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261016_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:46:11 [WARNING] 기동 시점 결손 1봉 / 검사창 08:45~08:45 (분그리드 기준) — 08:45 | session_bars 보존 여부는 15:46 확정 판정에서 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 20 | 08:50:05 [WARNING] 봉원천=db_fallback(버퍼 0봉)+chart(1봉) 1봉 · 기준봉=08:45 · 구독지연=125.7s |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 39 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 206 | 09:54:00 [WARNING] paintEvent slow 81.5ms | size=1994x950 candles=68 grid=33.1 spans=0.1 candles=2.8 dir=0.3 regime=4.4 markers=… |
| 12:00 | 장중 중간점 | 101 | 11:54:00 [WARNING] acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |

- 이 로그 생존구간: 08:46 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261016_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:46:11 [INFO] 활성화 | file=logs\crash_fault.log PID=3744 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 132 | 08:49:03 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 208 | 08:54:09 [INFO] #800 code=A056B raw_time=85409 parsed=08:54:09 price=881.66 vol=1 bid1=881.70 ask1=881.74 flag=49 side=BUY an… |
| 10:00 | 장중 초반 | 271 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 201 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:46 ~ 12:26

**매분 루프 커버리지 09:00~12:26: 207/207분 (100.0%)**

_장중 수집 — 분모를 수집 시각 12:26 까지로 줄였다. 이후 164분(~15:10)은 **미도래**라 제외(결손 아님)._

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261016_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:46:07 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.466 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 104 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 172 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 146 | 09:54:00 [WARNING] 신뢰도 미달 34.4% < 42.2% → 강제 X등급 |
| 12:00 | 장중 중간점 | 100 | 11:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:46 ~ 12:26

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
| **오늘 20261016** | **12:26** | 로그 본문 |

- 델타 **-367분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-15 (MW0601 694차 — 장전 점검, 지연 발화)
## 2026-10-15 (MW0601 695차 — 694차 후속: 「장후」 예약작업도 같은 지연/오발화 폭풍에 포함)
## 2026-10-15 (MW0601 696차 — 장후 점검: 종합 완성본)
## 2026-10-15 (MW0601 696차 후속 — 장후 자동조치: E-2 가상 장부 분리 · F-X1 종료 로그 직전 정지 꼬리) — 🟢 **구현 · 계측/도구 한정 · 매매 경로 무변경**
### E-2 — 점검 수집기가 가상 장부 진입을 「가상」으로 분리
### F-X1 — X 버튼 종료 로그에 직전 메인 스레드 정지 동반 기록
### 이월(C·사용자 몫)
## 2026-10-16 (MW0601 — 장전 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 closeEvent(X 버튼 경로의 실제 위치, 618/684차) ② 「60초 내」 창 대신 **경과초 상시 기록 + 300초 창 플래그** — 10-15 사례가 129초라 60초 창이면 흔적이 안 남았다.
- **회귀 위험**: 로그 문자열 꼬리만 추가. 앞머리 `[Shutdown] intent=(\w+)`는 그대로라 수집기 의도 파서·test_684 무영향. daily_close/auto_shutdown(extra 없음)은 바이트 동일. 꼬리 계산 실패는 try로 흡수(종료 경로를 막지 않음). `_last_stall_*`는 종료 로그 외 읽는 곳 0(테스트 고정).
- **검증**: 단위 테스트만. **라이브 미검증** — 다음 사용자 X 종료 시 SYSTEM 로그에 꼬리가 붙는지 확인(기한: 다음 수동 종료 발생일).

### 이월(C·사용자 몫)
- L-2·L-3·L-5·L-6·L-7: 이미 NEXT_TODO 등록(696차 장후 점검). 사용자 결정 대기 — 자동조치 미구현.
- P5-18: 6칸 미완 → 구현 금지, 표본 축적(O-t3).
- 사용자 조치 1(12:14 종료 의도 확인)·2(트리거 3종 확인)·4(신동2 문서 등 커밋) — 손대지 않음.

## 2026-10-16 (MW0601 — 장전 점검)
- **증상**: 08:35경 전일(10-15) 세션이 내리지 않고 남긴 CpStart/DibServer 좀비 프로세스가 당일 첫 COM 접속과 충돌해 DibServer가 즉시 다운(ACCESS_VIOLATION)되고, coStarter가 "이미 실행중→예" 처리 중 동반 크래시했다(08:35:51~54, 팝업 발생). 자동로그인 240초 재시도 2회(08:39:44·08:39:59)가 크래시 팝업에 막혀 전부 헛돌았다. 08:43~08:45 사람이 직접 로그인해 복구(세션 783343908), 08:47 예약된 CREON_AutoStart가 그 세션을 이어받아 마무리. 09:00 개장 전 "장전 준비 완료" 정상 확인.
- **원인**: 전날 `auto_shutdown`이 API 세션(CpStart/DibServer)을 내리지 않고 남김 → 서버 쪽 연결만 밤새 끊겨 프로세스는 좀비(IsConnect=0)로 생존 → LAUNCH_API 최초 COM 판독이 그 좀비를 깨우는 순간 DibServer 다운 → coStarter의 '이미 실행중→예' 분기가 좀비 정리 중 DibServer와 동반 크래시(2026-10-16 딥다이브 `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` 실측, 60일 Application 로그 대조로 매일 08:35:1x 재현 확인, 3/3 상관 확인). 어제 배포된 F-E1(`PlusDisconnect()` 선행호출)은 IsConnect==1 조건부라 좀비에는 미적용 — 그래서 오늘도 재발.
- **결정**: 근본 차단은 **CREON-M1(장후 API 세션 정리 — main.py 미실행 시 PlusDisconnect() 선행호출)**. 보완은 CREON-M2(좀비 감지 시 '예' 자동클릭 금지 + 좀비 정리 시도)·CREON-M3(크래시 팝업 자동감지로 240초 대기 생략). CREON-M4는 CREON-M1 적용 후 재평가(관찰 전용). ⚠ **이 딥다이브의 제안 ID(M-1~M-4)가 `NEXT_TODO.md`의 기존 M-1~M-4(라인 1364~1374, EOD NetRecon·섀도전략 손익 — 전혀 다른 안건)와 충돌한다** — 오늘 장전 점검이 `CREON-M1`~`CREON-M4`로 재명명해 등록했다. 기존 M-1~M-4는 변경하지 않았다.
- **Why**: 좀비 생성 자체(장후 세션 미정리)를 막는 것이 사후 대응(자동로그인 재시도 로직 보강)보다 근본적이다. 사후 대응만 고치면 크래시는 계속 나되 복구만 빨라지는 수준에 머문다.
- **How to apply**: `CREON-M1` — 장후 API 사용 작업(15:52 RegularCollect·16:05/16:20 OptionFlowBackfill) 종료 후, main.py 미실행 조건에서만 `PlusDisconnect()` 호출하는 정리 스텝 추가(저녁 수동 세션과 겹치지 않을 시간 조건 필요 — 사용자 결정 대기). `CREON-M2`/`CREON-M3`는 자동로그인 스크립트(`cybos_autologin.py` 계열)에 좀비 감지·팝업 감지 분기 추가. 라이브 미검증 — 전부 다음 재현일 확인 대상.
- **검증**: CREON-M1 적용 후 다음 거래일 08:35대 `logs/crash_fault.log`·Application 이벤트 로그에 DIBSERVER.EXE 크래시 재현 여부로 확인. 기한: 다음 거래일 장전 점검.
- **이월(기존)**: L-2·L-3·L-5·L-6·L-7(2026-10-15 CREON 딥다이브 승계, 변경 없음 — 그대로 NEXT_TODO 유지). F-1(session_state 마커 유실)·F-24(MAX_CONTRACTS 1 vs 수집기 기대값 3) — 오늘도 재확인, 신규 아님.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### MW0601 691차 — 맥점 전일 이력 경고 (2026-10-15)
### MW0601 692차 — 장후 봉 정합 (2026-10-15)
### MW0601 693차 — 장중 점검 (2026-10-15)
### MW0601 694차 — 장전 점검, 지연 발화 (2026-10-15)
### MW0601 695차 — 장후 트리거, 조기(12:50 KST) 오발화 (2026-10-15)
### MW0601 696차 — 장후 점검, 종합 완성본 (2026-10-15)
### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
### 2026-10-16 (MW0601 — 장전 점검)
```

미완료 체크박스 **3209건** (끝에서 30건)
```
- [ ] **695-1 (사용자 확인 필요)** "Mireuk postmarket check"(예정 16:15 KST)가 694차가 보고한
- [ ] **695-2** 이 발화는 장이 열려 있는 시점(12:50 KST)이라 정식 「장후」 종합 완성본을 쓰지
- [ ] 693-1(엔진 12:14 종료 후 미재기동) — 이 세션 작성 시각(약 12:52 KST)까지도 **미해소**.
- [ ] **693-1 (사용자 확인 필요, 이월)** 12:14:13 `user_close` 종료 — 의도적인지 사용자
- [ ] **693-2 (판정보류, 이월)** 12:12:04 MainStall(7750ms)과 12:14 종료 인과관계 —
- [ ] **694-1 (사용자 확인 필요, 이월)** "Mireuk premarket check" 3시간53분 지연 발화
- [ ] **695-1 (사용자 확인 필요, 이월)** 트리거 3종 동시 오발화 원인 — 16:15 장후 재발
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
- [ ] **O-p1 (관측예정)** CanaryShadow z-경고 변동(08:50 13개→08:55/08:57 6개→08:59 10개) — 프리마켓 웜업 단계의 정상 요동인지, 09:00 이후 매분 루프에서 수렴하는지 장중 점검이 판정.
- [ ] **O-p2 (관측예정)** 메인 스레드 블로킹 2건(4407ms·3765ms, 둘 다 기동 직후 08:46:39~42 몰림, 5초 미만이라 경보 대상 아님) — 반복되면 원인(DB 초기화·브로커 잔고 조회 동시성 추정) 조사.
- [ ] **O-p3 (확인 필요, P2)** 커밋 `271ddbd`(머지 커밋) PC명 태그 누락 — 과거 머지 커밋이 태그 예외로 다뤄진 전례가 있는지 미조사. 반복 관측되면 컨벤션 명문화 검토.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 승계, P2)** `cybos_autologin.py` 전일 잔존 세션 kill 실패 시
      "이미 실행중" 자동 '예' 대신 즉시 실패+경보.
- [ ] **L-6 (CREON 딥다이브 승계, P2)** autologin 단일 인스턴스 락(`data/_autologin.lock`).
- [ ] **L-7 (CREON 딥다이브 승계, P2)** 계좌 불일치 실패 후 잘못된 ID 세션 정리 +
      원인(D, CYBOS 경로 저장ID) 추가 실측.
- [ ] **O-t1** 10-16 08:35 무인 기동이 L-1 수정 후 "두 번째 날"에도 끝까지 완주하는지.
- [ ] **O-t2** CREON 로그인 창 "아이디 저장" 값이 프로젝트(cp/dcybos)별 독립인지 —
      10-16 08:35 계좌가 바로 783343908로 붙는지(표본 2일차).
- [ ] **O-t3** `ConfFloorGuard`(오후 보정기 출력상한<자동진입하한) 재발 여부 — P5-18
      표본 축적.
- [ ] **O-t4** "장전 점검" 예약작업이 10-16 08:57 KST 근처(±수 분)에 정상 발화하는지.
- [ ] **P5-18 (신규, 판정보류)** 오후 `ConfFloorGuard` 발동(14:55, 보정기 출력상한
      0.3313 < 필요 0.4180) — n=1, 관측일 1일. 반복되면 `docs/정기점검/수익률향상_누적대장.md`에
      정식 등록.

### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
- [x] **E-2** 수집기 가상 장부 분리 — 구현(696차 후속 커밋). `[Virtual] … 가상진입` 동반 진입을 「가상」으로 분류·병기.
- [x] **F-X1** `[Shutdown] intent=` 줄에 `recent_stall_ms/stall_age_s/within_window` 꼬리 — 구현(`dashboard/main_dashboard.py` closeEvent · `utils/exit_flags.py`).
- [ ] **F-X1 라이브 확인** 다음 사용자 X 종료 시 SYSTEM 로그 `[Shutdown] intent=user_* … recent_stall…` 꼬리 출현 확인.
- [ ] **E-2 후속(선택)** 실청산 0·가상만 있는 날은 수집기 §5 포지션 블록(`if ex or pe:`)이 안 그려져 가상 장부 표도 안 나온다 — 그런 날이 생기면 블록 조건 확장 검토(A등급).
- [ ] **(C 이월) L-2·L-3·L-5·L-6·L-7** — 위 696차 항목 그대로. 기동·로그인 흐름 변경이라 사용자 결정 후 별도 세션.
- [ ] **(C 이월) P5-18** — 6칸 미완(변경대상·기대효과·회귀위험 미정). O-t3 표본 축적 후 재평가.

### 2026-10-16 (MW0601 — 장전 점검)
- [ ] **CREON-M1 (신규, P0)** 장후 API 세션 정리 — main.py 미실행 시에만 `PlusDisconnect()` 선행호출. 좀비 CpStart/DibServer 생성을 장후에 차단한다(10-16 딥다이브 근본원인). 저녁 수동 세션과 겹치지 않을 시간 조건 — 사용자 결정 필요.
- [ ] **CREON-M2 (신규, P1)** 자동로그인: 좀비(`CpStart` 생존 && `IsConnect=0`) 감지 시 "이미 실행중→예" 자동클릭 금지, 대신 좀비 정리 시도(`PlusDisconnect()` IsConnect 무관 1회 + CpStart 창 WM_CLOSE) → 실패 시 즉시 실패+사유 로그. 정리 수단 실효성 미검증 — 다음 좀비 재현일 1회 시험 필요.
- [ ] **CREON-M3 (신규, P1)** 자동로그인: coStarter "Unhandled exception" 팝업 자동감지 → 확인클릭 → 크래시 사실 로그 → 240초 대기 생략.
- [ ] **CREON-M4 (관찰 전용)** CREON-M1 적용 후 LAUNCH_API 증상 재평가. 별도 조치 불필요 시 종료.
  ⚠ 위 4개는 본 파일 기존 M-1~M-4(라인 1364 부근, EOD NetRecon·섀도전략 손익 — 무관한 안건)와 ID가 겹쳐 `CREON-` 접두로 구분했다. 기존 M-1~M-4는 변경 없음.
- [ ] **O-p1 (관측예정)** CanaryShadow z-경고 변동(08:50 13개→08:55/08:57 6개→08:59 10개) — 프리마켓 웜업 단계의 정상 요동인지, 09:00 이후 매분 루프에서 수렴하는지 장중 점검이 판정.
- [ ] **O-p2 (관측예정)** 메인 스레드 블로킹 2건(4407ms·3765ms, 둘 다 기동 직후 08:46:39~42 몰림, 5초 미만이라 경보 대상 아님) — 반복되면 원인(DB 초기화·브로커 잔고 조회 동시성 추정) 조사.
- [ ] **O-p3 (확인 필요, P2)** 커밋 `271ddbd`(머지 커밋) PC명 태그 누락 — 과거 머지 커밋이 태그 예외로 다뤄진 전례가 있는지 미조사. 반복 관측되면 컨벤션 명문화 검토.

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

### `data/heartbeat_MW0601_20261016.json` — 241B · 10-16 12:26:12
```json
{
 "pid": 3744,
 "written_at": "2026-10-16T12:26:42",
 "beat_epoch": 1792121200.6909084,
 "beat_age_sec": 1.9,
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

### `data/peter2_live/trail_state_2026-10-16.json` — 336B · 10-16 11:19:19
```json
{
 "date": "2026-10-16",
 "trail": null,
 "ghosts": [
  {
   "pos_key": "2026-10-16 10:19:55|SHORT",
   "side": "S",
   "entry": 890.02,
   "stop": 892.88,
   "target": null,
   "start_hm": "11:19",
   "real_exit_px": 887.36,
   "real_pnl_pts": 2.66,
   "atr": 2.03,
   "peak_px": 880.22,
   "done": false,
   "exit_px": null,
   "exit_hm": null,
   "exit_why": null,
   "last_px": null
  }
 ]
}
```

### `data/peter_feed/_raw/2026-10-16.jsonl` — 1.8KB · 10-16 10:20:43
```json
JSONL 9행 ⏎ 첫: {"id": "2110884042296139904", "dt": "2026-10-16T00:02:28.000Z", "text": "장 시작 세팅은 상방 세팅 아닙니다.\n\n중간에 바뀔 수 있으니 바뀌면 전달합니다.", "seen_at": "2026-10-16T09:02:44+09:00", "src": "live"} | {"id": "2110890967062728954", "dt": "2026-10-16T00:29:59.000Z", "text": "오늘 삼전닉스 시세 나는 건 힘들고.\n\n일부 소부장과\n그동안 눌렸던 다른 종목들 움직이는 종목장세.\n----------------------------------------\n\n어제 방송보고 오전에 눌렸다고 바로 매수 들어갈까봐\n\n8시 9분에 1차 메세지\n\n9시 2분에 2차 메세지.\n-------------------------------------------", "seen_at": "2026-10-16T09:34:13+09:00", "src": "live"} | {"id": "2110893046778953914", "dt": "2026-10-16T00:38:15.000Z", "text": "은혼식 해야되요 ㅋ", "seen_at": "2026-10-16T09:38:43+09:00", "src": "live"} ⏎ 끝: {"id": "2110903140027605387", "dt": "2026-10-16T01:18:21.000Z", "text": "892 하방돌파시 매도. 손절 895", "seen_at": "2026-10-16T10:19:13+09:00", "src": "live"} | {"id": "2110901741122380159", "dt": "2026-10-16T01:12:48.000Z", "text": "890 손절.", "seen_at": "2026-10-16T10:19:13+09:00", "src": "live"} | {"id": "2110903607868674166", "dt": "2026-10-16T01:20:13.000Z", "text": "892 매도체결.", "seen_at": "2026-10-16T10:20:43+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-16 10:26:03**

| 키 | 값 | 수집 대상일(2026-10-16)과 일치 |
|---|---|---|
| `date` | 2026-10-16 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-16 08:55:06 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-15) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-16 08:55:06 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-15) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:25** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 12:26 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 219 |
| `session_bars` 당일 행수 | 219 (기대 411) |

- 미도래 **163봉** (12:26~15:08) — 수집 시각 12:26 이후라 결손·영구결손에서 제외
- 결손 **0봉**
- ⚠ **영구 결손 2봉** (`session_bars` 에도 없음): 08:45, 08:46

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
| 3744 | 08:46:11 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 233개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261016-점검리포트.md` | 21.0KB | 10-16 09:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_pre.md` | 59.8KB | 10-16 08:59 |
| `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` | 6.5KB | 10-16 08:51 |
| `docs/정기점검/매일점검/MW0601-20261015-점검리포트.md` | 69.1KB | 10-15 17:48 |
| `docs/정기점검/매일점검/_tmp_append_post_20261015.md` | 33.9KB | 10-15 16:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261015_post.md` | 105.6KB | 10-15 16:18 |
| `docs/정기점검/매일점검/MW0601-20261015-CREON런처기동흐름-딥다이브.md` | 23.4KB | 10-15 14:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20261015_intra.md` | 83.1KB | 10-15 12:27 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261008.json` | 3.0KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261008.md` | 5.0KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261008.json` | 38.9KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20261008.md` | 32.5KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261008.json` | 125.0KB | 10-08 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261008.md` | 194.1KB | 10-08 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261002.json` | 3.0KB | 10-02 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261002.md` | 5.0KB | 10-02 15:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MAX_CONTRACTS` = `1` (기대 `3`) — 431차 10→3 인하. 실전 자본 확정 시 재산출 대상
2. `logs/20261016_WARN.log`: ERROR 이상 1건
3. `logs/20261016_WARN.log`: **[Brier] 과신** 2건(표본)
4. `logs/20261016_SYSTEM.log`: **ConstOut** 8건(표본)
5. `logs/20261016_SIGNAL.log`: **WeightCollapse** 8건(표본)
6. `logs/20261016_SIGNAL.log`: **ConstOut** 8건(표본)
7. `logs/20261016_LEARNING.log`: **축퇴** 8건(표본)
8. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
9. PC명 태그 누락 커밋 1건 — 멀티PC 컨벤션 위반
10. 미커밋 변경 136건 (실질 6건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261016*.log` (Windows) / `grep 강제청산 logs/*20261016*.log`*