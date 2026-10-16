# 미륵이 증거 다이제스트 — 2026-10-13 / INTRA

- 생성 2026-10-13 12:27:02 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01pwe3lydpvkvwwiejadvm6x/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261013` · `2026-10-13` · `261013` · `1013`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **27개** 파일 · 27개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-pre-cowork-pre-{DATE}-0903.json` | 1 | `data/dailycheck_markers/claude-20261013-pre-cowork-pre-20261013-0903.json` | 175B | 10-13 09:03 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261013.log` | 125B | 10-13 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261013.log` | 140B | 10-13 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261013.json` | 242B | 10-13 12:26 |
| `launcher_{DATE}_084001_8417.log` | 1 | `logs/Mireuk_batch/launcher_20261013_084001_8417.log` | 1.5MB | 10-13 12:26 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261013.log` | 140B | 10-13 08:44 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261013.log` | 4.8KB | 10-13 09:32 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261013.log` | 29.0KB | 10-13 11:54 |
| `position_state.json.gen_{DATE}_094515` | 1 | `data/position_state.json.gen_20261013_094515` | 1.5KB | 10-13 09:44 |
| `position_state.json.gen_{DATE}_094834` | 1 | `data/position_state.json.gen_20261013_094834` | 1.5KB | 10-13 09:48 |
| `position_state.json.gen_{DATE}_095311` | 1 | `data/position_state.json.gen_20261013_095311` | 1.5KB | 10-13 09:48 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261013.log` | 44.9KB | 10-13 12:20 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-13.jsonl` | 6.4KB | 10-13 11:46 |
| `{DATE}_0917_D.xls` | 1 | `data/db/option_hts/261013_0917_D.xls` | 477.4KB | 10-13 09:17 |
| `{DATE}_1004_D.xls` | 1 | `data/db/option_hts/261013_1004_D.xls` | 477.5KB | 10-13 10:04 |
| `{DATE}_1204_D.xls` | 1 | `data/db/option_hts/261013_1204_D.xls` | 477.7KB | 10-13 12:03 |
| `{DATE}_DATA.log` | 1 | `logs/20261013_DATA.log` | 233.2KB | 10-13 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261013_DEBUG.log` | 143.1KB | 10-13 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261013_HEALTH.log` | 3.7KB | 10-13 11:36 |
| `{DATE}_HOGA.log` | 1 | `logs/20261013_HOGA.log` | 37.4MB | 10-13 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261013_LEARNING.log` | 174.3KB | 10-13 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20261013_MICRO.log` | 699.8KB | 10-13 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20261013_PROBE.log` | 55.5KB | 10-13 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261013_SIGNAL.log` | 401.3KB | 10-13 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261013_SYSTEM.log` | 655.2KB | 10-13 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20261013_TRADE.log` | 21.6KB | 10-13 11:49 |
| `{DATE}_WARN.log` | 1 | `logs/20261013_WARN.log` | 426.3KB | 10-13 12:27 |

## 2. 코드·커밋 상태

- HEAD `a42a7ba` · 브랜치 `v9-dev` · 미커밋 106건 · 실질 변경 3건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 3 · 미추적 103 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.7초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md
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
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261012.md
?? docs/미륵이고도화3/옵션_전일보유_맥점되돌림_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자흐름_맥점관계_MW0601-20261002.md
?? docs/미륵이고도화3/외인선물순매수_수집현황_조사_MW0601-20261002.md
?? docs/미륵이고도화3/위클리먼스리_선물추종_주체비중_일별_MW0601-20260921-20261002.md
?? docs/미륵이고도화3/피터2/live/
?? docs/미륵이고도화3/피터2/일일/
?? docs/미륵이고도화3/피터리_위로막힘_근거조사_MW0601-20261002.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261001.md
… 외 66건
```

**당일(2026-10-13) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
a42a7ba [MW0601] 686차 후속2 기록: 공유 생성 완료 · e2e 91건 · 체리픽 997d9c0→dev 93ab6ec
997d9c0 [MW0601] 686차 후속2: option_hts 미러 — 자기 IP 로 가리킨 원본도 거부
a63bfdf [MW0601] 686차 후속: option_hts 미러 기록 — DECISION_LOG(체리픽 3e72af1→dev 54026a3) · NEXT_TODO 686-1~4
3e72af1 [MW0601] 686차: option_hts [9842] 폴더 MW0602 단방향 미러 — sync_option_hts.py
d6b42a4 [MW0601] 685차: 거래주체 [신동] 실집행 — v9 규격(SD-2026-09-29-v2) 레그 분할 실행기
768afed [MW0602] 616차 체리픽: 거래주체 분리 — 미륵·피터 실거래 전환, 신동은 이 브랜치 비활성 (원 b44a9d6, dev)
9b5b6b2 [MW0601] 684차 후속: 장후 자동조치 기록 — 10-12 점검리포트(장전·장중·장후·제8부) + DECISION_LOG·NEXT_TODO
698cac7 [MW0601] 684차(682차 후속): 장후 자동조치 — F-18 재진단(X 버튼 종료 의도 로그 복구) · G-5 재기동 귀속 대사
eda0a0e [MW0601] 683차 후속3 후속: dev 배포 기록(9b05396)
90b365b [MW0601] 683차 후속3: 사다리 「신동2 해설」 패널 — 확률 시나리오 칩·표 렌더링·익일 계획 칸 보정
f2e8056 [MW0601] 615차 후속2 동기화 후속: write_offset_live 주석 갱신 — v9-dev 도 _replace_retry 보유
2a311c7 [MW0601] 683차 후속2: 683 파일 복원 — e0c3b58 이 동시 세션 stash 조작으로 683 변경을 되돌린 채 커밋됨
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

_본문 미열람(설정): `20261013_HOGA.log` 37.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `20261013_PROBE.log`, `launcher_20261013_084001_8417.log`, `20261013_DEBUG.log`, `shindong2_20261013.log`, `peter2_receiver_20261013.log`, `mainstall_traceback_20261013.log`, `freeze_sentinel_20261013.log`, `maekjeom_ladder_20261013.log`_

### `logs/20261013_TRADE.log` — 21.6KB · 141행 · 최종 11:49:00

- 형식 평문 · 시각 인식 141행 · WARNING=6, INFO=135

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-13 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-13 09:01:10 [INFO] TRADE: [Peter2] 진입 LONG 1계약 @973.04 손절 968.80 목표 - — limit LONG 지시 975(미니 972.8) 현재 973.04
2026-10-13 09:01:10 [INFO] TRADE: [Position] 진입 LONG 1계약 @ 973.04 | 손절=968.80 1차=10973.04(×1.00) 2차=10973.04
2026-10-13 09:01:10 [INFO] TRADE: [주문요청] LONG->LONG 1계약 @ 973.04 등급=P 역방향진입=OFF 체결대기
  …
2026-10-13 11:33:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi❌ fore❌ prev✅ time✅ risk❌ chas❌ coun✅ | conf=38.9%
2026-10-13 11:38:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=33,613,809) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-13 11:38:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi❌ fore❌ prev✅ time✅ risk❌ chas❌ coun✅ | conf=43.6%
2026-10-13 11:49:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=33,613,809) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-13 11:49:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi❌ fore❌ prev✅ time✅ risk❌ chas❌ coun✅ | conf=44.5%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 6 | 09:01:10 | 09:48:34 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=973.36 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×141

**컴포넌트 상위 15** — `Sizer`×34, `Chejan`×24, `Position`×19, `진입체크`×13, `주문요청`×12, `Peter2`×7, `PositionFallback`×6, `체결진입`×6, `TickStop-S0C`×6, `청산 완료`×6, `모드필터 차단`×5, `JointGateBlock 차단`×2, `ProfitGuard`×1

### `logs/20261013_WARN.log` — 426.3KB · 1923행 · 최종 12:27:01

- 형식 평문 · 시각 인식 1923행 · WARNING=1923

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-13 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-13 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-10-13 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-13 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-13 12:27:01 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 135.2ms | size=1041x876 candles=25 grid=31.1 spans=17.6 candles=10.0 dir=0.2 regime=0.1 markers=51.2 axes=24.3 cross=0.0 | slow_cnt=1444 total_cnt=1726 overlay_cnt=20672
2026-10-13 12:27:09 [WARNING] SYSTEM: [OptionFlowChart] 그리기 89.1ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287
2026-10-13 12:27:09 [WARNING] SYSTEM: [LiveDBG] _fetch_investor_data 지연 533ms — 메인 스레드 533ms 점유 (live 중단 원인 후보)
2026-10-13 12:27:09 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 124.4ms | size=1041x876 candles=25 grid=25.9 spans=15.8 candles=8.0 dir=0.2 regime=0.1 markers=47.4 axes=26.4 cross=0.0 | slow_cnt=1445 total_cnt=1727 overlay_cnt=20684
2026-10-13 12:27:13 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 143.1ms | size=1041x876 candles=25 grid=34.0 spans=22.3 candles=10.9 dir=0.2 regime=0.1 markers=43.1 axes=31.9 cross=0.0 | slow_cnt=1446 total_cnt=1728 overlay_cnt=20692
```

</details>

**WARNING — 태그 30종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1448 | 09:01:08 | 12:27:13 | paintEvent slow 58.9ms | size=1793x950 candles=17 grid=6.0 spans=2.7 candles=47.0 dir=0.1 regime=0.0 markers=0.0 axes=0.9 cross=0.0 | slow_cnt=1 total_cnt=97 overlay_cnt=933 |
| `LiveDBG` | 178 | 08:41:08 | 12:27:09 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 40 | 08:41:18 | 12:27:09 | 그리기 73.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 869x1001 |
| `PendingOrder` | 24 | 09:01:10 | 09:53:12 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 973.04, 'reason': '진입', 'hint_source': '', 'atr': 1.8886, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qty'… |
| `ChejanFlow` | 24 | 09:01:10 | 09:53:11 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='203' | pending='ENTRY:LONG qty=1 filled=0 order_no=? reason=진입 req_at=09:01:10.668' | position… |
| `ChejanMatch` | 24 | 09:01:10 | 09:53:11 | order_no='203' | pending='ENTRY:LONG qty=1 filled=0 order_no=203 reason=진입 req_at=09:01:10.668' | pending_matched=True |
| `EntryAttempt` | 19 | 09:01:10 | 11:49:00 | atr=1.8886 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='LONG' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='P' | pending='NONE' | … |
| `Peter2` | 13 | 09:12:20 | 11:54:20 | 수집기 하트비트 없음/지연(정상수집 92초 전 · X 페이지 오류: Top) — 신규 추종 진입 정지. Chrome 확장·수신기(tools/peter2_live) 확인 |
| `PipePerf` | 12 | 09:00:01 | 11:15:02 | total=1550ms | S0=2ms S1=14ms S2=0ms S3=0ms S4=102ms S5=944ms S6=470ms S7=12ms S8=5ms |
| `CB⑤` | 12 | 09:00:01 | 11:15:02 | 파이프라인 1550ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ExitCooldown` | 12 | 09:05:20 | 09:53:11 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:08:20) |
| `Health` | 11 | 09:00:01 | 11:35:01 | level=WARNING degraded=OFF | latency=1550ms | quality=1.00 | cache_age=53s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |

**채널** — `SYSTEM`×1912, `HEALTH`×11

**컴포넌트 상위 15** — `ChartDBG`×1448, `LiveDBG`×178, `OptionFlowChart`×40, `PendingOrder`×24, `ChejanFlow`×24, `ChejanMatch`×24, `EntryAttempt`×19, `Peter2`×13, `PipePerf`×12, `CB⑤`×12, `ExitCooldown`×12, `Health`×11, `Peter2Offset`×10, `Brier`×10, `SHAP`×9

### `logs/20261013_SYSTEM.log` — 655.2KB · 4281행 · 최종 12:27:01

- 형식 평문 · 시각 인식 4274행 · INFO=4274, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=14192 | 행감지=30s all_threads=True
2026-10-13 08:40:46 [INFO] SYSTEM: [DBInit] 합계 0.50s | predictions=0.05s trades=0.22s daily_stats=0.01s shap=0.02s raw_data=0.14s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-13 08:40:46 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-13 08:40:46 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-13 08:40:46 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-13 12:27:09 [INFO] SYSTEM: [TickUI] alive ticks=109478 code=A056B close=939.88
2026-10-13 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+90012 nonarb=-1886037
2026-10-13 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+90012 nonarb=-1886037
2026-10-13 12:27:13 [INFO] SYSTEM: [OptionBook] 완료 44015ms master=cache | 먼스리 2611 n=48/48 GEX=-1.87B 콜월=940.0 풋월=950.0 | 목위클리 2610W3 n=48/48 GEX=-2.49B 콜월=960.0 풋월=925.0 | 월위클리 2610W3 n=48/48 GEX=-0.02B 콜월=950.0 풋월=925.0
2026-10-13 12:27:15 [INFO] SYSTEM: [CybosRT-TICK] #109500 code=A056B raw_time=122715 parsed=12:27:15 price=939.98 vol=1 bid1=939.90 ask1=939.98 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×4274

**컴포넌트 상위 15** — `CybosRT-TICK`×1100, `CybosInvestorRaw`×828, `PumpGuard`×393, `TickUI`×222, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `S6Detail`×208, `PipePerf`×208, `BalanceUI`×67, `System`×59, `CybosEvent`×48, `BalanceRefresh`×45, `OptionChain`×44, `OptionBook`×42

### `logs/20261013_SIGNAL.log` — 401.3KB · 3398행 · 최종 12:27:01

- 형식 평문 · 시각 인식 3398행 · WARNING=1382, INFO=2016

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.433
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.412
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.408
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.416
  …
2026-10-13 12:27:01 [INFO] SIGNAL: 앙상블: dir=-1 conf=38.0% grade=X micro=추세장
2026-10-13 12:27:01 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=3m tf=3.24 → TP1×0.5
2026-10-13 12:27:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.380<mc0.620)
2026-10-13 12:27:01 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=43.6% size_mult=1.00 reason=meta_skip
2026-10-13 12:27:01 [INFO] SIGNAL: [ToxicityGate] action=reduce score=0.25 ma=0.27 size_mult=0.70 reason=toxicity_reduce
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1020 | 09:00:01 | 12:22:01 | 1m 'macro_vix' scale=0.0013 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 120 | 09:01:00 | 11:46:00 | 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 108 | 09:01:00 | 11:54:00 | ts=09:00 horizon=1m age=1m max_z=+10.68(prev_day_same_hour_ret) extreme=5 adj=4 |
| `Checklist` | 76 | 09:20:00 | 12:27:01 | 신뢰도 미달 34.2% < 39.0% → 강제 X등급 |
| `WeightCollapse` | 45 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 6 | 08:45:09 | 08:45:09 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 4 | 09:35:00 | 11:05:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 3 | 09:08:00 | 09:12:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×3398

**컴포넌트 상위 15** — `ScalerFloor`×1032, `SIGNAL`×416, `MetaGate`×259, `Ensemble`×217, `FQAdj`×207, `ZeroDiag`×169, `Checklist`×167, `Model`×126, `ATR-Horizon`×122, `ScalerMonitor`×108, `차단`×76, `ToxicityGate`×49, `WeightCollapse`×45, `EntryGate`×41, `MicroRegime`×41

### `logs/20261013_LEARNING.log` — 174.3KB · 1630행 · 최종 12:27:01

- 형식 평문 · 시각 인식 1630행 · WARNING=145, INFO=1485

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.2757 < conf_floor=0.3300 (span=0.00114 auc=0.539 out_max=0.2757, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00037 auc=0.516 out_max=0.2708 (기준 auc<0.53 and span<0.020, 기저율=0.2706 n=85) → 보정 미적용, raw 통과
2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00010 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-13 08:40:51 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00100 auc=0.548 out_max=0.3698 (n=130) → 보정 재적용
  …
2026-10-13 12:27:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=46.1% 예측=DN 실제=UP)
2026-10-13 12:27:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=57.2% UP)
2026-10-13 12:27:00 [INFO] LEARNING: [Bias⚠] 10m 적중=28%(5/18) UP=2 DN=12 FL=4 [DN편향⚠ 67%]
2026-10-13 12:27:00 [INFO] LEARNING: [Bias⚠] 3m 적중=43%(13/30) UP=7 DN=18 FL=5 [DN편향⚠ 60%]
2026-10-13 12:27:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=31.7%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 49 | 08:40:51 | 09:35:00 | 축퇴 감지 — span=0.00010 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 43 | 08:40:51 | 12:21:00 | 하한 도달불가 — out_max=0.2757 < conf_floor=0.3300 (span=0.00114 auc=0.539 out_max=0.2757, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 16 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00021 auc=0.530 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:10m` | 15 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00150 auc=0.562 out_max=0.3258, 기저율=0.3250 n=120) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 13 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00154 auc=0.403 out_max=0.2257 (기준 auc<0.53 and span<0.020, 기저율=0.2250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 7 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00007 auc=0.500 out_max=0.2625 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:59 | 08:40:59 | 복원한 보정기가 축퇴 상태 — span=0.00342 auc=0.529 out_max=0.2615 (n=3295) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 09:32:00 | 09:32:00 | total=412ms raw_fetch=11ms pred_select=368ms pred_update=27ms pred_insert=0ms verified=3 |

**채널** — `LEARNING`×1630

**컴포넌트 상위 15** — `LEARNING`×667, `SGD`×207, `sigma`×195, `Calibration:30m`×97, `Bias`×92, `Calibration:1m`×85, `Bias⚠`×79, `MetaConf`×43, `Calibration:3m`×31, `Calibration:10m`×29, `ScalerWarmup`×27, `Calibration:5m`×24, `OnlineLearner`×20, `Calibration:15m`×13, `SHAP`×6

### `logs/20261013_HEALTH.log` — 3.7KB · 22행 · 최종 11:36:00

- 형식 평문 · 시각 인식 22행 · WARNING=11, INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1550ms | quality=1.00 | cache_age=53s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1
2026-10-13 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=673ms | quality=1.00 | cache_age=112s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1
2026-10-13 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 392ms (표본 20분)
2026-10-13 09:31:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=525ms | quality=1.00 | cache_age=78s | exceptions_10m=6 | exc_tags=[ExitCooldown]×2 [Peter2Offset]×2 [Peter2]×2
2026-10-13 09:32:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2175ms | quality=1.00 | cache_age=139s | exceptions_10m=6 | exc_tags=[ExitCooldown]×2 [Peter2Offset]×2 [Peter2]×2
  …
2026-10-13 11:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=340ms | quality=1.00 | cache_age=157s | exceptions_10m=3 | exc_tags=[CB③-P4]×1 [Peter2]×1 [SHAP]×1
2026-10-13 11:15:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2246ms | quality=1.00 | cache_age=81s | exceptions_10m=1 | exc_tags=[Peter2]×1
2026-10-13 11:16:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=346ms | quality=1.00 | cache_age=139s | exceptions_10m=1 | exc_tags=[Peter2]×1
2026-10-13 11:35:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=355ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [SHAP]×1
2026-10-13 11:36:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=377ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[SHAP]×2 [Peter2Offset]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 11 | 09:00:01 | 11:35:01 | level=WARNING degraded=OFF | latency=1550ms | quality=1.00 | cache_age=53s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |

**채널** — `HEALTH`×22

**컴포넌트 상위 15** — `Health`×21, `HealthTrend`×1

### `logs/20261013_MICRO.log` — 699.8KB · 1883행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1883행 · DEBUG=1883

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=975.90/2 ask1=976.62/3 mp={'microprice_tick': 976.188, 'midprice_tick': 976.26, 'depth_bias_tick': -0.5403} mlofi_tick=None queue=None
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=975.90/2 ask1=976.62/3 mp={'microprice_tick': 976.188, 'midprice_tick': 976.26, 'depth_bias_tick': -0.5386} mlofi_tick=-2.45 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=975.90/3 ask1=976.60/2 mp={'microprice_tick': 976.32, 'midprice_tick': 976.25, 'depth_bias_tick': -0.3316} mlofi_tick=-7.5333 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.6…
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=975.90/1 ask1=976.60/2 mp={'microprice_tick': 976.1333, 'midprice_tick': 976.25, 'depth_bias_tick': -0.5778} mlofi_tick=-2.0 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1.09…
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=975.68/1 ask1=976.40/1 mp={'microprice_tick': 976.04, 'midprice_tick': 976.04, 'depth_bias_tick': -0.0914} mlofi_tick=-5.5667 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
  …
2026-10-13 12:26:46 [DEBUG] MICRO: [MICRO-TICK] #163800 bid1=939.90/1 ask1=939.98/1 mp={'microprice_tick': 939.94, 'midprice_tick': 939.94, 'depth_bias_tick': -0.0553} mlofi_tick=7.5333 queue={'depletion_bid': 4.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-10-13 12:26:57 [DEBUG] MICRO: [MICRO-TICK] #163900 bid1=939.80/1 ask1=939.88/1 mp={'microprice_tick': 939.84, 'midprice_tick': 939.84, 'depth_bias_tick': 0.0088} mlofi_tick=-5.8 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-10-13 12:27:00 [DEBUG] MICRO: [MICRO-MINUTE] #222 ts=2026-10-13 12:26:00 close=939.76 bias=0.002239 slope=1.930423 depth_bias=0.0528 mlofi_norm=0.001587 mlofi_pressure=1 mlofi_slope=-13.390000 queue_signal=-0.0698 queue_ma=-0.0195 queue_momentum=-0.0287 depletion=0.5000 refill=0.5000 imbalance…
2026-10-13 12:27:09 [DEBUG] MICRO: [MICRO-TICK] #164000 bid1=939.84/1 ask1=939.92/1 mp={'microprice_tick': 939.88, 'midprice_tick': 939.88, 'depth_bias_tick': -0.1161} mlofi_tick=0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-10-13 12:27:20 [DEBUG] MICRO: [MICRO-TICK] #164100 bid1=939.68/1 ask1=939.78/1 mp={'microprice_tick': 939.73, 'midprice_tick': 939.73, 'depth_bias_tick': 0.1646} mlofi_tick=-5.15 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
```

</details>

**채널** — `MICRO`×1883

**컴포넌트 상위 15** — `MICRO-TICK`×1661, `MICRO-MINUTE`×222

### `logs/20261013_DATA.log` — 233.2KB · 1043행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1043행 · INFO=1043

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:58:12 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+36 individual=-3 institution=-41 oi=0 call_foreign=-104 put_foreign=-564 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-13 08:58:12 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-13 08:58:42 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+49 individual=+0 institution=-57 oi=0 call_foreign=-113 put_foreign=-593 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-13 08:58:42 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-13 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=+49 futures(fi=+49 rt=+0 inst=-57) call(fi=-113 rt=+156) put(fi=-593 rt=+442) bias(fi=0.68 rt=-0.48) program(arb=+0 nonarb=+0 total=+0)
  …
2026-10-13 12:27:00 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-1431 futures(fi=-1516 rt=-85 inst=+1540) call(fi=-640 rt=+84) put(fi=-7120 rt=+5095) bias(fi=0.84 rt=-0.97) program(arb=+84861 nonarb=-1888564 total=-1803703)
2026-10-13 12:27:09 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-1513 individual=-88 institution=+1540 oi=51802 call_foreign=-619 put_foreign=-7110 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-13 12:27:09 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=+90012 nonarb=-1886037 total=-1796025 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-10-13 12:27:09 [INFO] DATA: [CybosInvestor] fetch#208 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-10-13 12:27:09 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-1425 futures(fi=-1513 rt=-88 inst=+1540) call(fi=-619 rt=+72) put(fi=-7110 rt=+5085) bias(fi=0.84 rt=-0.97) program(arb=+90012 nonarb=-1886037 total=-1796025)
```

</details>

**채널** — `DATA`×1043

**컴포넌트 상위 15** — `CybosInvestor`×622, `DivergencePanel`×414, `OptionFlow`×7

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 13 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 6 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 6 |
| 차단(`[차단]`) | 76 |
| 사이저 호출(`[Sizer]`) | 34 |

### 포지션 6건 · 승 0 (0%) · 합계 -19.68pt (-1,040,578원)  ※ 레그 6행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:01:10 (추정귀속) | 추정 | LONG | 1 | — | 1 | -4.62 | -240,549 | 하드스톱(틱) |
| 09:17:38 (추정귀속) | 추정 | LONG | 1 | — | 1 | -0.60 | -39,391 | 하드스톱(틱) |
| 09:20:11 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.72 | -195,422 | 하드스톱(틱) |
| 09:26:33 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.76 | -197,423 | 하드스톱(틱) |
| 09:37:06 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.14 | -166,397 | 하드스톱(틱) |
| 09:48:34 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.84 | -201,396 | 하드스톱(틱) |

**출처별 소계** — 추정 6건 -1,040,578원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 6건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 6행** (부분청산 0 · 전량청산 6)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:05:20 | 전량 | 1 | -4.62 | -240,549 | 하드스톱(틱) |
| 09:19:21 | 전량 | 1 | -0.60 | -39,391 | 하드스톱(틱) |
| 09:22:29 | 전량 | 1 | -3.72 | -195,422 | 하드스톱(틱) |
| 09:30:32 | 전량 | 1 | -3.76 | -197,423 | 하드스톱(틱) |
| 09:45:15 | 전량 | 1 | -3.14 | -166,397 | 하드스톱(틱) |
| 09:53:11 | 전량 | 1 | -3.84 | -201,396 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×6

> 최종 청산이 하드스톱·손절 계열인 포지션 6/6건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -1,040,578 = 포지션합 -1,040,578 → OK · `[청산 완료]` 6건 = 조립 포지션 6건 → OK

등급 분포 — `A급(원시C)`×11, `A급(원시X)`×2

**진입한 건들의 체크리스트 미통과 항목** — `fore`×13, `risk`×13, `chas`×7, `prev`×4, `ofi`×4, `cvd`×2

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×9, **2계약**×1, **3계약**×24

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×34

### 차단 사유 76건 · 40종

| 건수 | 사유 |
|---|---|
| 32 | 등급X — 미통과 항목: 2_confidence |
| 5 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 1 | 청산 후 쿨다운 — 140초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 148초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 88초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 89초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 31초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.3pt > ATR×5.0=14.2pt (시가=974.66 반등위험) |
| 1 | 청산 후 쿨다운 — 74초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 14초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 131초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 71초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 11초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 9_risk |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.7pt > ATR×5.0=12.6pt (시가=974.66 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.6pt > ATR×5.0=12.3pt (시가=974.66 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 9_risk |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 24.1pt > ATR×5.0=10.0pt (시가=974.66 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 25.0pt > ATR×5.0=9.8pt (시가=974.66 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×32, `3_vwap`×5, `6_foreign`×5, `9_risk`×5, `4_cvd`×2, `7_prev_bar`×2, `5_ofi`×2, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 6건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×5
- `연속 손절 2회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 18건 · 최대 13844ms · 5초 초과 1건

상위 — 13844ms, 4187ms, 3781ms, 3750ms, 3547ms, 3391ms, 3156ms, 2953ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:32:13 | 13844ms | 2175ms | **11669ms (84%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261013_WARN.log`
```
--- [Brier] 과신 ×8(표본)
11:49:00 2026-10-13 11:49:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.355 > 0.35
11:50:00 2026-10-13 11:50:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.352 > 0.35
11:51:00 2026-10-13 11:51:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.350 > 0.35
11:52:00 2026-10-13 11:52:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.353 > 0.35
--- [CB] ×6(표본)
09:05:20 2026-10-13 09:05:20 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:19:21 2026-10-13 09:19:21 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:22:29 2026-10-13 09:22:29 [WARNING] SYSTEM: [CB] 연속 손절 2회 (300초 창, 포지션 단위)
09:30:32 2026-10-13 09:30:32 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:05:20 2026-10-13 09:05:20 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:08:20)
09:05:20 2026-10-13 09:05:20 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:08:20)
09:19:21 2026-10-13 09:19:21 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:22:21)
09:19:21 2026-10-13 09:19:21 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:22:21)
--- [SHAP] 슬로우 ×8(표본)
11:00:01 2026-10-13 11:00:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1171ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:29:02 2026-10-13 11:29:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1088ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:35:02 2026-10-13 11:35:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1114ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:46:01 2026-10-13 11:46:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 902ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-13 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4187ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4187 band=INFO since_pipe_s=NA
09:00:02 2026-10-13 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3750 band=INFO since_pipe_s=0.0
09:05:01 2026-10-13 09:05:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2734ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2734 band=INFO since_pipe_s=0.0
09:30:02 2026-10-13 09:30:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2859ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2859 band=INFO since_pipe_s=0.0
```

### `logs/20261013_SYSTEM.log`
```
--- ConstOut ×4(표본)
09:35:00 2026-10-13 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3917) | 앙상블 제외는 유지
09:44:00 2026-10-13 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3578) | 앙상블 제외는 유지
10:56:00 2026-10-13 10:56:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3945) | 앙상블 제외는 유지
11:05:00 2026-10-13 11:05:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4252) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-10-13 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-10-13 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-10-13 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:16:00 2026-10-13 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
```

### `logs/20261013_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-13 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0270 dir=+1)
09:35:00 2026-10-13 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:36:00 2026-10-13 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0270 dir=+1)
09:37:00 2026-10-13 09:37:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- HALT ×5(표본)
10:10:08 2026-10-13 10:10:08 [INFO] SIGNAL: [Peter2] HALT {'hm': '10:10', 'why': 'daily_max_entries'}
10:10:14 2026-10-13 10:10:14 [INFO] SIGNAL: [Peter2] DISARM {'hm': '10:10', 'sig': '2109813909125538094', 'why': 'halted:daily_max_entries'}
10:32:10 2026-10-13 10:32:10 [INFO] SIGNAL: [Peter2] DISARM {'hm': '10:32', 'sig': '2109819007725662276', 'why': 'halted:daily_max_entries'}
10:38:38 2026-10-13 10:38:38 [INFO] SIGNAL: [Peter2] DISARM {'hm': '10:38', 'sig': '2109820636701077585', 'why': 'halted:daily_max_entries'}
--- WeightCollapse ×8(표본)
09:07:00 2026-10-13 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-10-13 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-10-13 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-10-13 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:42 2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.433
08:40:42 2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
08:40:42 2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.412
08:40:42 2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.408
--- 안전망 ×8(표본)
09:07:00 2026-10-13 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-13 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-13 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-13 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261013_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.2757 < conf_floor=0.3300 (span=0.00114 auc=0.539 out_max=0.2757, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00037 auc=0.516 out_max=0.2708 (기준 auc<0.53 and span<0.020, 기저율=0.2706 n=85) → 보정 미적용, raw 통과
08:40:51 2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00010 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-13 08:40:51 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00100 auc=0.548 out_max=0.3698 (n=130) → 보정 재적용
```

### `logs/20261013_HEALTH.log`
```
--- [ExitCooldown] ×7(표본)
09:31:00 2026-10-13 09:31:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=525ms | quality=1.00 | cache_age=78s | exceptions_10m=6 | exc_tags=[ExitCooldown]×2 [Peter2Offset]×2 [Peter2]×2
09:32:02 2026-10-13 09:32:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2175ms | quality=1.00 | cache_age=139s | exceptions_10m=6 | exc_tags=[ExitCooldown]×2 [Peter2Offset]×2 [Peter2]×2
09:33:00 2026-10-13 09:33:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=609ms | quality=1.00 | cache_age=15s | exceptions_10m=5 | exc_tags=[Peter2Offset]×2 [Peter2]×2 [ExitCooldown]×1
09:34:00 2026-10-13 09:34:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=450ms | quality=1.00 | cache_age=74s | exceptions_10m=6 | exc_tags=[Peter2]×3 [Peter2Offset]×2 [ExitCooldown]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261013_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 09:01:10 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=973.36 — 진입 경로가 파라미터를 넘기지 않… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 14 | 09:01:10 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=973.36 — 진입 경로가 파라미터를 넘기지 않… |
| 10:00 | 장중 초반 | 3 | 10:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=33,613,809) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShad… |

- 이 로그 생존구간: 08:41 ~ 11:49

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261013_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 24 | 08:52:39 [WARNING] A056B 실측=-1.9 n=7 spread=0.09 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.9 | 직전일=-2.2(prev_day:2026-10-12, … |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 69 | 09:00:01 [WARNING] total=1550ms | S0=2ms S1=14ms S2=0ms S3=0ms S4=102ms S5=944ms S6=470ms S7=12ms S8=5ms |
| 10:00 | 장중 초반 | 159 | 09:54:47 [WARNING] paintEvent slow 126.3ms | size=1793x950 candles=70 grid=33.9 spans=21.7 candles=19.5 dir=0.3 regime=0.2 marke… |
| 12:00 | 장중 중간점 | 107 | 11:54:00 [WARNING] 과신 경고 | 이동평균=0.359 > 0.35 |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261013_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 97 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=14192 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 171 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 270 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 234 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 227 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~12:27: 208/208분 (100.0%)**

_장중 수집 — 분모를 수집 시각 12:27 까지로 줄였다. 이후 163분(~15:10)은 **미도래**라 제외(결손 아님)._

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261013_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 38 | 08:45:09 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 89 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0013 → floor=0.10 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 240 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0013 → floor=0.10 적용 (z-score 폭발 방지) |
| 10:00 | 장중 초반 | 140 | 09:54:00 [WARNING] ts=09:53 horizon=1m age=3m max_z=-4.21(mlofi_slope) extreme=1 adj=1 |
| 12:00 | 장중 중간점 | 167 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=7m max_z=+4.13(volume_acceleration) extreme=1 adj=1 |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261012 | 18:35 | 로그 본문 |
| 20261009 | 18:33 | 로그 본문 |
| 20261008 | 15:43 | 로그 본문 |
| 20261007 | 20:26 | 로그 본문 |
| 20261006 | 15:47 | 로그 본문 |
| **중앙값** | **18:33** | 기준선 |
| **오늘 20261013** | **12:27** | 로그 본문 |

- 델타 **-366분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-12 (MW0601 683차 — 신동2 외인 동향 보고 + 확률 시나리오 자가학습 사이클)
## 2026-10-12 (MW0601 684차 — 682차 후속 장후 자동조치: F-18 재진단 · G-5 재기동 귀속 대사)
### F-18 재진단 — 618차 종료 의도 로그가 X 버튼 경로에서 죽어 있었다 (`698cac7`)
### G-5 — 수집기 「재기동 귀속 대사」 (`698cac7`)
### 처리하지 않은 것
## 2026-10-12 (MW0601 685차 — 거래주체 [신동] 실집행: v9 규격 레그 분할 실행기)
## 2026-10-12 (MW0601 686차 — option_hts [9842] 폴더 MW0602 단방향 미러)
## 2026-10-13 (MW0601 687차 — 장전 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
로 넘기지 않는 이유**: 체크아웃이 mtime을 바꾼다. `scripts/foreign_flow_pit_review.py`가
  파일 mtime ≤ T로 시점 존재를 판정하므로 PIT가 조용히 깨진다. 런타임 산출물 커밋 금지 원칙과도 충돌.
- **경로를 UNC로 직접 가리키지 않는 이유**: MW0601이 꺼지면 MW0602 사다리가 같이 죽는다. 로컬 사본을 읽는다.
- `scripts/sync_option_hts.py`: copy2(mtime 보존) · `.part`→`os.replace` 원자 교체 · 정착 대기 5초 ·
  삭제 비전파 · `_sync_arrivals.json`(원본 mtime vs 도착 시각 — MW0602 라이브에서 「mtime≤T면 T에 있었다」를
  그대로 쓰지 않도록, 계측 4원칙 ②·④) · 원본 PC에서 실행 시 거부(rc=2) · 원본 불가 rc=3.
- **단일 기록자**: 사본 폴더에 `_MIRROR_OF_<호스트>.txt` 표식. `derive_9842_daily.py`는 표식이 있으면 거부(rc=2).
  파생본은 MW0601에서만 만들고 미러로 넘어간다.
- 실행: MW0602에서 `OPTION_HTS_SYNC.bat`(08:40–16:30 루프). 예약작업 설치 스크립트와 공유 생성은
  자동모드 권한 분류기가 거부해 **사용자 수동 단계로 남김**(NEXT_TODO 686-1·686-2).
- 실측: 두 PC 같은 LAN(MW0602=192.168.0.12, ping 0ms) · MW0601 NTP(time.google.com) 동기 · 네트워크 프로필 Private.
- 회귀 가드: `tests/test_686_option_hts_sync.py`(7건 통과, py37_32).
- 관찰(무관·기존): `derive_9842_daily.py --dry-run`이 MW0601 원본에서 「머리행 다름」(투신 vs 기관계 열 구성)으로 예외 — 686차 변경과 무관.
- **체리픽 기록**: 원 커밋 `3e72af1`(v9-dev) · 원 PC **MW0601** → dev `54026a3`(push 완료).
  이유: 미러를 **받는 쪽이 MW0602(dev)** 라 스크립트·bat·derive 가드가 dev에 있어야 실행된다.
  체리픽 전 `derive_9842_daily.py`는 dev·v9-dev 동일(diff 0) → 충돌 없음, dev 트리에서 테스트 7건 통과.
- **[686차 후속2] e2e 실측 + 자기 IP 거부**: MW0601 공유 생성(사용자 실행, Everyone Read) 후
  `\192.168.0.70\option_hts` → 임시 폴더 동기화 91건 · mtime 불일치 0 · 재실행 unchanged=91.
  그 과정에서 IP 경로는 원본 PC 거부를 통과함을 발견 → 127.*·자기 IP 거부 추가.
  체리픽: 원 `997d9c0`(v9-dev, MW0601) → dev `93ab6ec`. 이유: 미러 실행 주체가 MW0602(dev).

## 2026-10-13 (MW0601 687차 — 장전 점검)

**증상**: 장전 점검(코웍 예약, 08:59 KST 증거수집) 결과 P0 없음. 부팅 구간(08:40:45) access violation 3건 재현(`collection/macro/macro_fetcher.py:99`), SessionStateDrop 재현(`p8_last_success_date`·`eod_retrain_ok_date` 키 소실) — 둘 다 기존 등록 항목(1-1, F-1(538-4))이라 신규 Fix로 다시 올리지 않음(함정① 확인).

**원인**: 1-1은 근본원인 미확인(사람의 PC 직접 확인 필요, 여러 차수째 미착수). SessionStateDrop은 F-1(538-4) 미적용 상태의 기존 동작.

**결정**: 오늘 장전은 코드 변경 없음(장전 규약). 설정 불변식 24개 전부 일치, CB②/TOX-SEVERE-SPREAD 등 한시예외 재검토 기한 전부 해소/이관 확인(CLAUDE.md §2). 브랜치 `v9-dev` 일치, 인덱스락 없음, 당일 병행 세션 없음(`report_append_marker.py acquire` 통과).

**Why**: 함정①(이미 아는 문제를 신규로 재보고) 방지 — NEXT_TODO.md의 기존 항목과 대조 후 지속 처분만 함.

**How to apply**: 해당 없음(관측만).

**검증**: 다음 장후 점검에서 — ① F-15(수수료 채널 고정, 10-12 `9e88005`) 오늘 첫 체결의 `commission_rate_used=9.8104e-05` 확인 ② F-18(종료사유 로그, 10-12 `698cac7`) 라이브 검증은 오늘 X 버튼 재시작 발생 시에만 가능(오늘 기동 1회·재시작 0건으로 아직 표본 없음) ③ 09:33·11:22(10/12) 재기동 의도 — 사용자 확인 대기 지속.

**라이브 미검증 항목 기한**: F-18 라이브 검증은 다음 X 버튼 재시작 발생 시까지 무기한 대기(기한 없음, 발생 즉시 판정).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치)
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2)
## 2026-10-12 (MW0601 680차 — 장전 점검)
## 2026-10-12 (MW0601 681차 — 장중 점검)
## 2026-10-12 (MW0601 682차 — 장후 점검)
## 2026-10-12 (MW0601 684차 — 682차 후속 장후 자동조치)
## 2026-10-12 (MW0601 686차 — option_hts MW0602 미러)
## 2026-10-13 (MW0601 687차 — 장전 점검)
```

미완료 체크박스 **3124건** (끝에서 30건)
```
- [ ] **1-2(신규)** 09:33·11:22 장중 재기동 2건이 사용자 의도적 조치였는지 확인 — 장후 점검에서 사용자에게 직접 질문. 확인되면 O-t2 "해소(설명됨)"로 닫고, 안 되면 "지속(진짜 원인불명)"으로 유지.
- [ ] **O-t1(4차 재이월 — 더 이상 이월 금지)**: 오늘 체결 2건 발생. 장후 점검에서 `trades.db`의 `commission_rate_used`가 CYBOS(`9.8104e-05`)인지 반드시 확정.
- [ ] **F-18(신규 제안, 비승인)**: 런처/엔진 종료 경로에 `[Shutdown] intent=user_close|watchdog|crash` 구분 로그 추가 — 1-2·O-t2류 재발 시 원인 구분을 로그만으로 가능하게. 적용 전 기존(618차 등)에 같은 제안이 이미 있는지 grep 확인 필요(미확인 상태).
- [ ] **G-5(신규, 고도화 제안)**: 수집기 §2(병행 세션 확인)에 "재기동 시각 ±5분 이내 당일 커밋 존재 여부" 자동 대사 열 추가 — O-t2류 오탐(의도적 재시작을 원인불명으로 오판) 감소.
- [ ] **1-1 범위 확장 확인**: 오늘 재기동 2회의 부팅 구간 모두에서 access violation 3건씩 재현(종전엔 "그날 첫 부팅만"으로 알려짐) — 표본 1일, 다음 재기동 발생일에 "매 재기동마다 재현"인지 재확인 필요.
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·F-15·F-16·G-3 — 전부 지속, 변화 없음(680차 DECISION_LOG 참조, 중복 기재 생략).
- [ ] **F-16(사람, 승인 필요)**: `scripts/commission_rate_recon.py --backfill`로 10-08(9행)·10-12(7행) `trades.commission_rate_used`·`commission_krw`·`net_pnl_krw` CYBOS 요율(`9.8104e-05`)로 소급 정정. 적용 전 `data/db…
- [ ] F-15 라이브 반영 확인(장전/장중 점검 소관): 다음 재기동 후 첫 체결에서 `commission_rate_used=9.8104e-05`인지 확인.
- [ ] 1-2/O-t3 이월: 09:33·11:22 재기동이 사용자 의도였는지 — 사용자 직접 확인 전까지 판정 보류, 매 장후가 같은 질문을 반복한다(의도된 설계).
- [ ] **F-18(신규 제안, 비승인)**: 런처/엔진 종료 경로에 `[Shutdown] intent=user_close|watchdog|crash` 구분 로그 추가 — 적용 전 618차 등에 이미 같은 제안이 있는지 grep 확인 필요(미확인 상태 지속).
- [ ] **G-5(신규, 고도화 제안 보강)**: 수집기 §2에 "재기동 시각 ±5분 이내 당일 커밋 존재 여부" 자동 대사 추가 — 오늘 실측으로 ±5분 밖 커밋(15:30대)을 원인으로 오인할 위험을 확인, ±5분 창 조건을 판정식에 반영할 것.
- [ ] 1-1(원인조사, 지속 — 오늘 기동 3회 전부 재현 확인): 사람이 PC에서 Windows 이벤트 뷰어/작업 관리자 직접 확인 필요. 오늘도 미착수.
- [ ] 미커밋 변경 120건(실질 18건) 정리 확인 — `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 정본 `rev: 2026-09-07`(538차) 대비 앱 사본 낡음(673차부터 등록, 변화 없음).
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·G-3 — 전부 지속, 변화 없음(680·681·682차 DECISION_LOG 참조, 중복 기재 생략).
- [ ] 668차 후속11(`74b7d3c`, 피터2 자연어 오독 보강) 효과 관찰: 유사 오독 재발 0건 — 최소 3거래일 관찰 필요(1-3류 CASE-04와 같은 패턴 재현 여부).
- [ ] **F-18 라이브 검증** — 다음 X 버튼 재시작 시 SYSTEM 로그에 `[Shutdown] intent=user_restart` 출현 확인. 출현하지 않으면 `logging_system.log_manager` 임포트 폴백(None)으로 떨어진 것.
- [ ] **1-2/O-t3 재질문 문구 갱신** — 684차 조사로 09:33·11:22는 X 버튼 재시작(user_restart)이 가장 유력(atexit 경로 중 무로그는 그것뿐). 사용자 확인 시 「해소(설명됨)」로 닫을 것.
- [ ] **(신규, 관찰) 레거시 `[Shutdown] 정상 종료 플래그 기록` 문구가 로그 파일에 안 남는다** — 같은 모듈 로거 경로. NEXT_TODO가 「정상 마감일엔 정확히 2회」를 건강 신호로 적고 있으나 실측 0회 → 점검 기준이 측정 불가. 처분 선택지: (a) `write_exit_flags`가 `log_fn`에도 이 줄을 보내게 함…
- [ ] F-16(소급 정정)·F-1(538-4)·F-2·663-1(F-5)·663-2(F-7) — 승인 대기 지속(682차 항목 참조).
- [ ] **686-2 (사용자, MW0602)** `git pull`(dev `54026a3` 포함) → 자격증명 저장 `cmdkey /add:DeskTop-MW0601 /user:DeskTop-MW0601\mw0601 /pass`
- [ ] **686-3** MW0602 첫 동기화 후 `logs\<날짜>_OPTION_HTS_SYNC.log`의 copied 수 · `_sync_arrivals.json` lag_sec 분포 확인(장중 1분 이내 기대).
- [ ] **686-4 (관찰)** `derive_9842_daily.py --dry-run` 「머리행 다름(투신 vs 기관계)」 예외 — 내보내기 열 구성 변경 추정, 별도 조사.
- [ ] 1-1(원인조사, 지속 — 오늘도 부팅 구간 3건 재현): 사람이 PC에서 Windows 이벤트 뷰어/작업 관리자 직접 확인 필요. 오늘도 미착수.
- [ ] (이월) 09:33·11:22(10/12) 재기동이 사용자 의도였는지 — 10/12 684차 조사로 "X 버튼 재시작"이 가장 유력하나 사용자 확인 전까지 판정 보류. 오늘(10/13)은 해당 재기동 없음 — 매 장후가 같은 질문을 반복한다(의도된 설계).
- [ ] F-18 라이브 검증(지속) — 다음 X 버튼 재시작 시 SYSTEM 로그에 `[Shutdown] intent=user_restart` 출현 확인. 오늘 기동 1회·재시작 0건으로 아직 검증 기회 없음.
- [ ] F-16(소급 정정)·F-1(538-4)·F-2·663-1(F-5)·663-2(F-7) — 전부 지속, 변화 없음(680~686차 DECISION_LOG 참조, 중복 기재 생략).
- [ ] 미커밋 변경 102건(실질 1건) 정리 확인 — `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 정본 `rev: 2026-09-07`(538차) 대비 앱 사본 `rev: 2026-08-26e`(499차)로 낡음(10/9 673차부터 등록, 변화 없음). `save_skill overwrite: true` 필요(이 PC 한정).
- [ ] F-15 반영 확인(장후 소관) — 오늘 첫 체결에서 `commission_rate_used=9.8104e-05`인지 확인.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
자연어 오독 보강) 효과 관찰: 유사 오독 재발 0건 — 최소 3거래일 관찰 필요(1-3류 CASE-04와 같은 패턴 재현 여부).

## 2026-10-12 (MW0601 684차 — 682차 후속 장후 자동조치)

- [x] **F-18 재진단·수정** — 618차 종료 의도 로그는 있었으나 X 버튼 경로가 파일에 안 남았다(`log_fn` 미전달). `698cac7`에서 `log_manager.system` 전달로 복구.
- [ ] **F-18 라이브 검증** — 다음 X 버튼 재시작 시 SYSTEM 로그에 `[Shutdown] intent=user_restart` 출현 확인. 출현하지 않으면 `logging_system.log_manager` 임포트 폴백(None)으로 떨어진 것.
- [x] **G-5** 수집기 재기동 귀속 대사표(종료 의도 −3~+1분 · 커밋 ±5분) — `698cac7`.
- [ ] **1-2/O-t3 재질문 문구 갱신** — 684차 조사로 09:33·11:22는 X 버튼 재시작(user_restart)이 가장 유력(atexit 경로 중 무로그는 그것뿐). 사용자 확인 시 「해소(설명됨)」로 닫을 것.
- [ ] **(신규, 관찰) 레거시 `[Shutdown] 정상 종료 플래그 기록` 문구가 로그 파일에 안 남는다** — 같은 모듈 로거 경로. NEXT_TODO가 「정상 마감일엔 정확히 2회」를 건강 신호로 적고 있으나 실측 0회 → 점검 기준이 측정 불가. 처분 선택지: (a) `write_exit_flags`가 `log_fn`에도 이 줄을 보내게 함 (b) 건강 신호를 `intent=daily_close`/`auto_shutdown` 2줄로 교체. 계측 전용(A등급)이나 「건강 신호 정의」 변경이라 사람 확인 후 진행.
- [ ] F-16(소급 정정)·F-1(538-4)·F-2·663-1(F-5)·663-2(F-7) — 승인 대기 지속(682차 항목 참조).

## 2026-10-12 (MW0601 686차 — option_hts MW0602 미러)

- [x] **686-1 (사용자, MW0601 관리자 PowerShell — 2026-10-12 완료, Everyone Read 확인)** 읽기전용 공유 생성:
  `New-SmbShare -Name option_hts -Path "C:\Users\82108\PycharmProjects\futures\data\db\option_hts" -ReadAccess Everyone`
- [ ] **686-2 (사용자, MW0602)** `git pull`(dev `54026a3` 포함) → 자격증명 저장 `cmdkey /add:DeskTop-MW0601 /user:DeskTop-MW0601\mw0601 /pass`
  → 1회 리허설 `python scripts\sync_option_hts.py` → 상시 `OPTION_HTS_SYNC.bat`(또는 작업 스케줄러에 08:40 등록).
- [ ] **686-3** MW0602 첫 동기화 후 `logs\<날짜>_OPTION_HTS_SYNC.log`의 copied 수 · `_sync_arrivals.json` lag_sec 분포 확인(장중 1분 이내 기대).
- [ ] **686-4 (관찰)** `derive_9842_daily.py --dry-run` 「머리행 다름(투신 vs 기관계)」 예외 — 내보내기 열 구성 변경 추정, 별도 조사.

## 2026-10-13 (MW0601 687차 — 장전 점검)

- [ ] 1-1(원인조사, 지속 — 오늘도 부팅 구간 3건 재현): 사람이 PC에서 Windows 이벤트 뷰어/작업 관리자 직접 확인 필요. 오늘도 미착수.
- [ ] (이월) 09:33·11:22(10/12) 재기동이 사용자 의도였는지 — 10/12 684차 조사로 "X 버튼 재시작"이 가장 유력하나 사용자 확인 전까지 판정 보류. 오늘(10/13)은 해당 재기동 없음 — 매 장후가 같은 질문을 반복한다(의도된 설계).
- [ ] F-18 라이브 검증(지속) — 다음 X 버튼 재시작 시 SYSTEM 로그에 `[Shutdown] intent=user_restart` 출현 확인. 오늘 기동 1회·재시작 0건으로 아직 검증 기회 없음.
- [ ] F-16(소급 정정)·F-1(538-4)·F-2·663-1(F-5)·663-2(F-7) — 전부 지속, 변화 없음(680~686차 DECISION_LOG 참조, 중복 기재 생략).
- [ ] 미커밋 변경 102건(실질 1건) 정리 확인 — `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 정본 `rev: 2026-09-07`(538차) 대비 앱 사본 `rev: 2026-08-26e`(499차)로 낡음(10/9 673차부터 등록, 변화 없음). `save_skill overwrite: true` 필요(이 PC 한정).
- [ ] F-15 반영 확인(장후 소관) — 오늘 첫 체결에서 `commission_rate_used=9.8104e-05`인지 확인.

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

### `data/dailycheck_markers/claude-20261013-pre-cowork-pre-20261013-0903.json` — 175B · 10-13 09:03:16
```json
{
 "pc": "claude",
 "date": "20261013",
 "phase": "pre",
 "session": "cowork-pre-20261013-0903",
 "pid": 6,
 "started_epoch": 1791849796.1838899,
 "started_at": "2026-10-13 00:03:16"
}
```

### `data/heartbeat_MW0601_20261013.json` — 242B · 10-13 12:26:48
```json
{
 "pid": 14192,
 "written_at": "2026-10-13T12:27:18",
 "beat_epoch": 1791862034.076987,
 "beat_age_sec": 3.9,
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

### `data/peter_feed/_raw/2026-10-13.jsonl` — 6.4KB · 10-13 11:46:12
```json
JSONL 34행 ⏎ 첫: {"id": "2109792714858664353", "dt": "2026-10-12T23:45:55.000Z", "text": "제가 방송에서 제시한 종목중 손절가에 도달해서 손절된 종목들이 있다면.\n\n손절 가격에서 5-10프로 더 떨어진 가격에서 재매수 가능합니다.\n단, 그 가격에서 7프로 이하를 다시 손절가 잡으면 됩니다.\n\n만약 코스피 추가하락이 예상되어 기다리고 싶으면\n\n차라리 다시 제가 제시한 매수가 올때까지", "seen_at": "2026-10-13T08:46:07+09:00", "src": "live"} | {"id": "2109794316357079252", "dt": "2026-10-12T23:52:17.000Z", "text": "오늘도 매수 단타만 할 예정.\n\n975 아래로 떨어지면 기회 보고 장초부터 들어갈 예정", "seen_at": "2026-10-13T08:52:52+09:00", "src": "live"} | {"id": "2109796086886093222", "dt": "2026-10-12T23:59:19.000Z", "text": "975 매수체결.", "seen_at": "2026-10-13T09:01:08+09:00", "src": "live"} ⏎ 끝: {"id": "2109821881453080919", "dt": "2026-10-13T01:41:49.000Z", "text": "942 손절.\n\n오늘 바닥에서 빗자루질 하네요.", "seen_at": "2026-10-13T10:42:22+09:00", "src": "live"} | {"id": "2109822582572884138", "dt": "2026-10-13T01:44:36.000Z", "text": "저는 개인적으로 940에서 마지막 매수 합니다.\n\n이건 손절없이 그냥 장 끝날때 가지고 갑니다.", "seen_at": "2026-10-13T10:44:42+09:00", "src": "live"} | {"id": "2109838047869317290", "dt": "2026-10-13T02:46:04.000Z", "text": "옵션하는 분은\n\n위클리 목요일 1000\n\n현재가 1.9 부근\n\n소액 매수 노려볼 만합니다.", "seen_at": "2026-10-13T11:46:12+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-13 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-13)과 일치 |
|---|---|---|
| `date` | 2026-10-13 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-13 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-12) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-13 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-12) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:26** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 12:27 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 222 |
| `session_bars` 당일 행수 | 222 (기대 411) |

- 미도래 **162봉** (12:27~15:08) — 수집 시각 12:27 이후라 결손·영구결손에서 제외
- 결손 **0봉**

- 라이브 로그 대조: `logs/20261013_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 14192: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 14192 | 08:40:45 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 220개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261013-점검리포트.md` | 13.8KB | 10-13 09:04 |
| `docs/정기점검/매일점검/evidence_MW0601-20261013_pre.md` | 61.3KB | 10-13 08:59 |
| `docs/정기점검/매일점검/MW0601-20261012-점검리포트.md` | 79.2KB | 10-12 17:32 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_post.md` | 99.1KB | 10-12 16:18 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261012.md` | 18.0KB | 10-12 12:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_intra.md` | 84.1KB | 10-12 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_pre.md` | 62.0KB | 10-12 09:01 |
| `docs/정기점검/매일점검/MW0601-20261009-점검리포트.md` | 51.1KB | 10-09 17:29 |

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

1. 메인 스레드 정지 5초 초과 **1건** (최대 13844ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
2. `logs/20261013_WARN.log`: **[Brier] 과신** 8건(표본)
3. `logs/20261013_SYSTEM.log`: **ConstOut** 4건(표본)
4. `logs/20261013_SIGNAL.log`: **WeightCollapse** 8건(표본)
5. `logs/20261013_SIGNAL.log`: **ConstOut** 8건(표본)
6. `logs/20261013_LEARNING.log`: **축퇴** 8건(표본)
7. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
8. 미커밋 변경 106건 (실질 3건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261013*.log` (Windows) / `grep 강제청산 logs/*20261013*.log`*