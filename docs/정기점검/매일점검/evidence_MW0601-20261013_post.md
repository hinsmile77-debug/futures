# 미륵이 증거 다이제스트 — 2026-10-13 / POST

- 생성 2026-10-13 16:17:36 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-012ffykvubauwgy4pnxweruy/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261013` · `2026-10-13` · `261013` · `1013`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **43개** 파일 · 43개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `MW0601-{DATE}-intra-pid7.json` | 1 | `data/dailycheck_markers/MW0601-20261013-intra-pid7.json` | 157B | 10-13 12:35 |
| `claude-{DATE}-post-cowork-post-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261013-post-cowork-post-20261013.json` | 171B | 10-13 16:17 |
| `claude-{DATE}-pre-cowork-pre-{DATE}-0903.json` | 1 | `data/dailycheck_markers/claude-20261013-pre-cowork-pre-20261013-0903.json` | 175B | 10-13 09:03 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261013.log` | 137B | 10-13 15:35 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261013.txt` | 28B | 10-13 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261013.txt` | 28B | 10-13 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261013.txt` | 233B | 10-13 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261013.log` | 2.0KB | 10-13 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261013.log` | 433B | 10-13 15:53 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261013.json` | 245B | 10-13 15:47 |
| `launcher_{DATE}_084001_8417.log` | 1 | `logs/Mireuk_batch/launcher_20261013_084001_8417.log` | 2.6MB | 10-13 15:33 |
| `launcher_{DATE}_153442_24135.log` | 1 | `logs/Mireuk_batch/launcher_20261013_153442_24135.log` | 44.3KB | 10-13 15:47 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261013.log` | 140B | 10-13 08:44 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261013.log` | 4.8KB | 10-13 09:32 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261013.log` | 39.2KB | 10-13 15:35 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261013.log` | 491B | 10-13 16:15 |
| `position_state.json.gen_{DATE}_094515` | 1 | `data/position_state.json.gen_20261013_094515` | 1.5KB | 10-13 09:44 |
| `position_state.json.gen_{DATE}_094834` | 1 | `data/position_state.json.gen_20261013_094834` | 1.5KB | 10-13 09:48 |
| `position_state.json.gen_{DATE}_095311` | 1 | `data/position_state.json.gen_20261013_095311` | 1.5KB | 10-13 09:48 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261013.log` | 21.8KB | 10-13 15:53 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261013.log` | 82.2KB | 10-13 16:04 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261013.txt` | 43B | 10-13 15:47 |
| `strategy_report_{DATE}_154007.txt` | 1 | `data/daily_reports/strategy_report_20261013_154007.txt` | 2.4KB | 10-13 15:40 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-13.jsonl` | 9.9KB | 10-13 15:13 |
| `{DATE}_0917_D.xls` | 1 | `data/db/option_hts/261013_0917_D.xls` | 477.4KB | 10-13 09:17 |
| `{DATE}_1004_D.xls` | 1 | `data/db/option_hts/261013_1004_D.xls` | 477.5KB | 10-13 10:04 |
| `{DATE}_1204_D.xls` | 1 | `data/db/option_hts/261013_1204_D.xls` | 477.7KB | 10-13 12:03 |
| `{DATE}_1305_D.xls` | 1 | `data/db/option_hts/261013_1305_D.xls` | 477.8KB | 10-13 13:05 |
| `{DATE}_DATA.log` | 1 | `logs/20261013_DATA.log` | 439.6KB | 10-13 15:33 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261013_DEBUG.log` | 249.8KB | 10-13 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261013_HEALTH.log` | 5.9KB | 10-13 14:58 |
| `{DATE}_HOGA.log` | 1 | `logs/20261013_HOGA.log` | 63.7MB | 10-13 15:33 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261013_LEARNING.log` | 379.7KB | 10-13 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261013_MICRO.log` | 1.2MB | 10-13 15:33 |
| `{DATE}_PROBE.log` | 1 | `logs/20261013_PROBE.log` | 94.6KB | 10-13 15:37 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261013_REGULAR_COLLECT.log` | 8.3KB | 10-13 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261013_SIGNAL.log` | 616.2KB | 10-13 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261013_SYSTEM.log` | 1.1MB | 10-13 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261013_TRADE.log` | 30.2KB | 10-13 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261013_WARN.log` | 779.8KB | 10-13 15:46 |
| `{DATE}_lv.txt` | 1 | `data/peter_feed/2026-10-13_lv.txt` | 3.8KB | 10-13 16:17 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-13_tr.draft.txt` | 170B | 10-13 15:40 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-10-13_tr.txt` | 264B | 10-13 16:15 |

## 2. 코드·커밋 상태

- HEAD `6ef35d0` · 브랜치 `v9-dev` · 미커밋 117건 · 실질 변경 6건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 6 · 미추적 111 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.5초(`git status --porcelain`)
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
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261014.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261012.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261013.md
?? docs/미륵이고도화3/옵션_전일보유_맥점되돌림_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자흐름_맥점관계_MW0601-20261002.md
?? docs/미륵이고도화3/외인선물순매수_수집현황_조사_MW0601-20261002.md
… 외 77건
```

**당일(2026-10-13) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
6ef35d0 [MW0602] UI: 메인 분할(3열 폭·좌측 세로) 크기를 저장해 다음 기동에 복원
9777e2b [MW0602] UI: 진입단계 추적 카드를 좌측 하단 → 신뢰도 게이트 탭 중단으로 이동
```

**최근 커밋 12건**
```
6ef35d0 [MW0602] UI: 메인 분할(3열 폭·좌측 세로) 크기를 저장해 다음 기동에 복원
9777e2b [MW0602] UI: 진입단계 추적 카드를 좌측 하단 → 신뢰도 게이트 탭 중단으로 이동
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

_본문 미열람(설정): `20261013_HOGA.log` 63.7MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261013.txt`** — 28B · 10-13 15:40:07
```
2026-10-13T15:40:07.702591
```

**`data/daily_close_started_20261013.txt`** — 28B · 10-13 15:40:03
```
2026-10-13T15:40:03.632342
```

**`data/daily_reports/strategy_report_20261013_154007.txt`** — 2.4KB · 10-13 15:40:07
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-13 15:40
========================================================
  버전    : v1.0  (96일차)
  판정    : OUTPERFORM
  Live(20일): Sh=2.49  MDD(자본대비)=4.4%
  당일      : WR=0.0%  PF=0.00
  롤링20일: 누적 +5323312원  Sh=2.49  MDD(자본대비)=4.4%  MDD(peak대비)=29.1%
  당일손익 : broker(gross) -984,000원  수수료 56,578원  net -1,040,578원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.31)
  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)
  PSI/feat: 미측정
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 -76,803원  승률 40.0%  합계 -1,536,055원
  등급별 순EV(30일): A=-9,070원(59건,승56%)  P=-169,598원(9건,승0%)
  호라이즌별 순EV(30일): 1m=+2,297원(7건)  3m=+9,628원(34건)  5m=-48,810원(18건)  ?=-169,598원(9건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 83분  5일평균 52분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 49.5pt(5일평균 26.9pt)  1분평균변동 1.17pt(5일평균 0.65pt)
--------------------------------------------------------
  진입 퍼널(2026-10-13, 총 370분):
    FLAT 155 → conf미달 119 → CoherenceGate 14 → 게이트차단 52 → 후보 30 → 진입 28
    └ 등급상향경로(앙상블X→체크리스트통과): 2건 [285차-P5]
    게이트별: 체크리스트항목미달=16  시가갭(OPEN_VOLATILE)=13  모드필터=12  콜드스타트/기타(σ미수집)=4  콜드스타트/기타(DataAnomalyGate)=4  포지션보유중(평가생략)=2  쿨다운=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 2건
      └ 상세: JointGateBlock=2
      └ JointGateBlock 2건 (무정보폴백 2건 = 100.0%) [표본 18건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261013.txt`** — 233B · 10-13 15:53:41
```
completed: 2026-10-13 15:53:41
rows: 20440
cols: 97
phase2_fallback: false
horizons_replaced: 5/6
t_load_s: 25.7
t_retrain_s: 191.6
t_total_s: 217.8
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/peter_feed/2026-10-13_lv.txt`** — 3.8KB · 10-13 16:17:11
```
제가 방송에서 제시한 종목중 손절가에 도달해서 손절된 종목들이 있다면. 손절 가격에서 5-10프로 더 떨어진 가격에서 재매수 가능합니다. 단, 그 가격에서 7프로 이하를 다시 손절가 잡으면 됩니다. 만약 코스피 추가하락이 예상되어 기다리고 싶으면 차라리 다시 제가 제시한 매수가 올때까지
8:45 AM · Oct 13, 2026

오늘도 매수 단타만 할 예정. 975 아래로 떨어지면 기회 보고 장초부터 들어갈 예정
8:52 AM · Oct 13, 2026

975 상방돌파시 매수. 손절 971
8:58 AM · Oct 13, 2026

975 매수체결.
8:59 AM · Oct 13, 2026

971 손절
9:05 AM · Oct 13, 2026

965상방돌파시 매수. 손절가 962
9:10 AM · Oct 13, 2026

965 매수체결
9:13 AM · Oct 13, 2026

962 손절된 분은 다시 962부근에 매수하고 손절가 959
9:16 AM · Oct 13, 2026

962 매수체결
9:19 AM · Oct 13, 2026

손절된분은 다시 962 상방돌파시 매수하고 손절가 959
9:23 AM · Oct 13, 2026

다시 962 매수체결
9:23 AM · Oct 13, 2026

현재 최대 4+3+3 = 10 p 손실중 962 매수 체결중.
9:25 AM · Oct 13, 2026

코스닥 소부장들부터 먼저 돌고 있습니다. 다시 밀릴 수 있지만 지금 가격은 매수로 대응하는게 맞습니다.
9:26 AM · Oct 13, 2026

손절가 958로 변경
9:29 AM · Oct 13, 2026

만약 손절된 분은 962 상방 돌파시 재매수 손절가 958
9:32 AM · Oct 13, 2026

962 매수체결 - 2번째
9:36 AM · Oct 13, 2026

손절가 957로 변경
9:44 AM · Oct 13, 2026

957 손절. 960 상방 돌파시 다시 재매수. 손절가 956
9:46 AM · Oct 13, 2026

손절한 다음에 바로 재매수하면 안됩니다. 제시한 가격 상방 돌파시 매수해야 합니다. 그냥 죽 밀려버릴 수 있습니다.
9:48 AM · Oct 13, 2026

960 매수체결
9:48 AM · Oct 13, 2026

956 손절.
9:53 AM · Oct 13, 2026

954 상방 돌파시 매수. 손절가 951
10:06 AM · Oct 13, 2026

951 상방돌파시 매수로 수정. 손절가 948
10:09 AM · Oct 13, 2026

951 매수체결
10:10 AM · Oct 13, 2026

손절가 947로 변경
10:20 AM · Oct 13, 2026

947 손절.
10:21 AM · Oct 13, 2026

947 상방돌파시 매수. 손절가 943
10:30 AM · Oct 13, 2026

947 매수체결
10:36 AM · Oct 13, 2026

손절가 942로 변경
10:39 AM · Oct 13, 2026

942 손절. 오늘 바닥에서 빗자루질 하네요.
10:41 AM · Oct 13, 2026

저는 개인적으로 940에서 마지막 매수 합니다. 이건 손절없이 그냥 장 끝날때 가지고 갑니다.
10:44 AM · Oct 13, 2026

옵션하는 분은 위클리 목요일 1000 현재가 1.9 부근 소액 매수 노려볼 만합니다.
11:46 AM · Oct 13, 2026

[피터리 - 2026년 10월 13일 증권사 산업분석 리포트 브리핑] 기준: 2026년 10월 12일 13:10 초과 ~ 2026년 10월 13일 13:10 KST ① 한눈에 보는 결론 오늘 리포트에서 가장 중요한 변화는 반도체가 다시 “메모리 가격”에서 “장비·패키징·테스트의 물리적 공급능력” 문제로 확장됐다는 점이다.
1:39 PM · Oct 13, 2026

[피터리 - 2026년 10월 13일 증권사 종목리포트 브리핑] 기준: 2026년 10월 12일 13:00 초과 ~ 2026년 10월 13일 13:00 KST ① 한눈에 보는 결론 오늘 리포트에서 가장 중요한 변화는 다섯 가지다. 첫째, 반도체 업사이클은 유지되지만 오늘 시장이 느끼는 위험과 증권사 실적 전망 사이의 괴리가
1:48 PM · Oct 13, 2026

피터리 - 2026년 10월 13일 증권사 산업분석 리포트 브리핑 - 축약본
2:21 PM · Oct 13, 2026

피터리 - 2026년 10월 13일 증권사 종목리포트 브리핑 - 축약본
2:42 PM · Oct 13, 2026

저는 개인적으로 940 매수분 들고 오버나잇합니다. 4+3+3+4+5+4+4+5= 32p 손실
3:13 PM · Oct 13, 2026
```

**`data/peter_feed/2026-10-13_tr.draft.txt`** — 170B · 10-13 15:40:05
```
08:59 L 975 / 09:05 X 971 손절
09:13 L 965 / 09:46 X 957 손절
09:48 L 960 / 09:53 X 956 손절
10:10 L 951 / 10:21 X 947 손절
10:36 L 947 / 10:41 X 942 손절
```

**`data/peter_feed/2026-10-13_tr.txt`** — 264B · 10-13 16:15:40
```
08:59 L 975 / 09:05 X 971 손절
09:13 L 965 / 09:16 X 962 손절
09:19 L 962 / 09:23 X 959 손절
09:23 L 962 / 09:32 X 958 손절
09:36 L 962 / 09:46 X 957 손절
09:48 L 960 / 09:53 X 956 손절
10:10 L 951 / 10:21 X 947 손절
10:36 L 947 / 10:41 X 942 손절
```

**`data/shutdown_normal_20261013.txt`** — 43B · 10-13 15:47:14
```
auto_shutdown
2026-10-13T15:47:14.776331
```

_다이제스트 대상 8/22개 (중요도순). 제외: `20261013_DATA.log`, `20261013_PROBE.log`, `launcher_20261013_084001_8417.log`, `launcher_20261013_153442_24135.log`, `20261013_DEBUG.log`, `shindong2_20261013.log`, `peter2_receiver_20261013.log`, `20261013_REGULAR_COLLECT.log`_

### `logs/20261013_TRADE.log` — 30.2KB · 188행 · 최종 15:40:05

- 형식 평문 · 시각 인식 188행 · WARNING=6, INFO=182

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-13 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-13 09:01:10 [INFO] TRADE: [Peter2] 진입 LONG 1계약 @973.04 손절 968.80 목표 - — limit LONG 지시 975(미니 972.8) 현재 973.04
2026-10-13 09:01:10 [INFO] TRADE: [Position] 진입 LONG 1계약 @ 973.04 | 손절=968.80 1차=10973.04(×1.00) 2차=10973.04
2026-10-13 09:01:10 [INFO] TRADE: [주문요청] LONG->LONG 1계약 @ 973.04 등급=P 역방향진입=OFF 체결대기
  …
2026-10-13 14:45:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=33,613,809) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-13 14:45:01 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk❌ chas✅ coun✅ | conf=46.1%
2026-10-13 15:35:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-13 15:37:00 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-13 15:40:05 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 6 | 09:01:10 | 09:48:34 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=973.36 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×188

**컴포넌트 상위 15** — `Sizer`×56, `진입체크`×28, `Chejan`×24, `Position`×19, `주문요청`×12, `모드필터 차단`×12, `Peter2`×7, `PositionFallback`×6, `체결진입`×6, `TickStop-S0C`×6, `청산 완료`×6, `ProfitGuard`×4, `JointGateBlock 차단`×2

### `logs/20261013_WARN.log` — 779.8KB · 3557행 · 최종 15:46:06

- 형식 평문 · 시각 인식 3550행 · WARNING=3550, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-13 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-13 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-10-13 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-13 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-13 15:46:03 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-10-13 10:06:00 cols=['open'] existing_source=rt
2026-10-13 15:46:03 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-10-13 10:08:00 cols=['open'] existing_source=rt
2026-10-13 15:46:03 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-10-13 10:09:00 cols=['open'] existing_source=rt
2026-10-13 15:46:03 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=408 inserted=3 open_fixed=1 mismatch=48
2026-10-13 15:46:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3188ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3188 band=INFO since_pipe_s=NA
```

</details>

**WARNING — 태그 35종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2746 | 09:01:08 | 15:37:07 | paintEvent slow 58.9ms | size=1793x950 candles=17 grid=6.0 spans=2.7 candles=47.0 dir=0.1 regime=0.0 markers=0.0 axes=0.9 cross=0.0 | slow_cnt=1 total_cnt=97 overlay_cnt=933 |
| `LiveDBG` | 379 | 08:41:08 | 15:46:06 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 78 | 08:41:18 | 15:37:13 | 그리기 73.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 869x1001 |
| `EntryAttempt` | 34 | 09:01:10 | 14:45:01 | atr=1.8886 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='LONG' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='P' | pending='NONE' | … |
| `SHAP` | 29 | 11:00:01 | 15:06:01 | 슬로우 감지 1171ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `PendingOrder` | 24 | 09:01:10 | 09:53:12 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 973.04, 'reason': '진입', 'hint_source': '', 'atr': 1.8886, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qty'… |
| `ChejanFlow` | 24 | 09:01:10 | 09:53:11 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='203' | pending='ENTRY:LONG qty=1 filled=0 order_no=? reason=진입 req_at=09:01:10.668' | position… |
| `ChejanMatch` | 24 | 09:01:10 | 09:53:11 | order_no='203' | pending='ENTRY:LONG qty=1 filled=0 order_no=203 reason=진입 req_at=09:01:10.668' | pending_matched=True |
| `Peter2` | 20 | 09:12:20 | 13:43:50 | 수집기 하트비트 없음/지연(정상수집 92초 전 · X 페이지 오류: Top) — 신규 추종 진입 정지. Chrome 확장·수신기(tools/peter2_live) 확인 |
| `Health` | 18 | 09:00:01 | 14:57:00 | level=WARNING degraded=OFF | latency=1550ms | quality=1.00 | cache_age=53s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |
| `CB③-P4` | 18 | 10:54:00 | 14:50:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=10.0%) |
| `PipePerf` | 16 | 09:00:01 | 14:40:01 | total=1550ms | S0=2ms S1=14ms S2=0ms S3=0ms S4=102ms S5=944ms S6=470ms S7=12ms S8=5ms |

**채널** — `SYSTEM`×3532, `HEALTH`×18

**컴포넌트 상위 15** — `ChartDBG`×2746, `LiveDBG`×379, `OptionFlowChart`×78, `EntryAttempt`×34, `SHAP`×29, `PendingOrder`×24, `ChejanFlow`×24, `ChejanMatch`×24, `Peter2`×20, `Health`×18, `CB③-P4`×18, `PipePerf`×16, `CB⑤`×16, `ScalerRefresh`×13, `SessionBackfill`×12

### `logs/20261013_SYSTEM.log` — 1.1MB · 7522행 · 최종 15:47:14

- 형식 평문 · 시각 인식 7497행 · INFO=7497, PLAIN=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=14192 | 행감지=30s all_threads=True
2026-10-13 08:40:46 [INFO] SYSTEM: [DBInit] 합계 0.50s | predictions=0.05s trades=0.22s daily_stats=0.01s shap=0.02s raw_data=0.14s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-13 08:40:46 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-13 08:40:46 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-13 08:40:46 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-13 15:46:03 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-13) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-13 15:47:03 [INFO] SYSTEM: [System] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:47:03
2026-10-13 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-13 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-13 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×7497

**컴포넌트 상위 15** — `CybosRT-TICK`×1736, `CybosInvestorRaw`×1572, `PumpGuard`×765, `CybosRT-ROLLOVER`×408, `BAR-CLOSE`×408, `CVD-ANCHOR`×408, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `System`×111, `MicroRegime`×90, `OptionChain`×83, `OptionBook`×79, `BalanceUI`×75, `RegimeFingerprint`×67

### `logs/20261013_SIGNAL.log` — 616.2KB · 5334행 · 최종 15:40:06

- 형식 평문 · 시각 인식 5334행 · WARNING=1880, INFO=3454

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.433
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.412
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.408
2026-10-13 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.416
  …
2026-10-13 15:36:57 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-13 15:37:03 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
2026-10-13 15:40:05 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-13 15:40:06 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-13 age=44m extreme=594 refresh=31 grade_x=0 cb3=0
2026-10-13 15:40:06 [INFO] SIGNAL: [ModelHealth] date=2026-10-13 앙상블유효가동률=미측정 | 파이프라인 0분 | ConstOut 0회/0분 | WeightCollapse 0분 | 장중재학습 0회 | CB③ ready 0분/0분 (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1398 | 09:00:01 | 14:56:01 | 1m 'macro_vix' scale=0.0013 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 135 | 09:20:00 | 15:09:00 | 신뢰도 미달 34.2% < 39.0% → 강제 X등급 |
| `Model` | 132 | 09:01:00 | 14:12:00 | 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 114 | 09:01:00 | 14:12:00 | ts=09:00 horizon=1m age=1m max_z=+10.68(prev_day_same_hour_ret) extreme=5 adj=4 |
| `WeightCollapse` | 84 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 8 | 09:35:00 | 14:11:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ScalerRefresh` | 6 | 08:45:09 | 08:45:09 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `MetaGate` | 3 | 09:08:00 | 09:12:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×5334

**컴포넌트 상위 15** — `ScalerFloor`×1410, `SIGNAL`×740, `MetaGate`×459, `Ensemble`×381, `FQAdj`×369, `ZeroDiag`×298, `Checklist`×268, `ATR-Horizon`×203, `Model`×150, `차단`×116, `ScalerMonitor`×115, `MicroRegime`×90, `WeightCollapse`×84, `InstabilityGate`×81, `ToxicityGate`×77

### `logs/20261013_LEARNING.log` — 379.7KB · 3333행 · 최종 15:40:06

- 형식 평문 · 시각 인식 3333행 · WARNING=416, INFO=2917

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.2757 < conf_floor=0.3300 (span=0.00114 auc=0.539 out_max=0.2757, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00037 auc=0.516 out_max=0.2708 (기준 auc<0.53 and span<0.020, 기저율=0.2706 n=85) → 보정 미적용, raw 통과
2026-10-13 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00010 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-13 08:40:51 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00100 auc=0.548 out_max=0.3698 (n=130) → 보정 재적용
  …
2026-10-13 15:40:05 [INFO] LEARNING: [DriftAdjuster] 표본 부족(n=0 < 15) — acc=50.0% 반영 스킵, alpha=0.01000 유지
2026-10-13 15:40:05 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-13 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-13 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-13 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 142 | 08:40:51 | 15:36:55 | 축퇴 감지 — span=0.00010 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 129 | 08:40:51 | 15:36:55 | 하한 도달불가 — out_max=0.2757 < conf_floor=0.3300 (span=0.00114 auc=0.539 out_max=0.2757, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 50 | 08:40:51 | 15:36:55 | 축퇴 감지 — span=0.00021 auc=0.530 out_max=0.3501 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 39 | 08:40:51 | 15:36:54 | 축퇴 감지 — span=0.00154 auc=0.403 out_max=0.2257 (기준 auc<0.53 and span<0.020, 기저율=0.2250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 34 | 08:40:51 | 15:36:55 | 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00150 auc=0.562 out_max=0.3258, 기저율=0.3250 n=120) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 17 | 08:40:51 | 15:36:53 | 축퇴 감지 — span=0.00007 auc=0.500 out_max=0.2625 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 4 | 08:40:59 | 15:36:55 | 복원한 보정기가 축퇴 상태 — span=0.00342 auc=0.529 out_max=0.2615 (n=3295) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 09:32:00 | 09:32:00 | total=412ms raw_fetch=11ms pred_select=368ms pred_update=27ms pred_insert=0ms verified=3 |

**채널** — `LEARNING`×3333

**컴포넌트 상위 15** — `LEARNING`×1219, `SGD`×369, `sigma`×357, `Calibration:30m`×283, `Calibration:1m`×256, `Bias⚠`×198, `Bias`×159, `Calibration:3m`×99, `MetaConf`×79, `Calibration:5m`×74, `Calibration:10m`×65, `OnlineLearner`×46, `ScalerWarmup`×36, `Calibration:15m`×33, `BiasReset`×16

### `logs/20261013_HEALTH.log` — 5.9KB · 36행 · 최종 14:58:00

- 형식 평문 · 시각 인식 36행 · WARNING=18, INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1550ms | quality=1.00 | cache_age=53s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1
2026-10-13 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=673ms | quality=1.00 | cache_age=112s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1
2026-10-13 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 392ms (표본 20분)
2026-10-13 09:31:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=525ms | quality=1.00 | cache_age=78s | exceptions_10m=6 | exc_tags=[ExitCooldown]×2 [Peter2Offset]×2 [Peter2]×2
2026-10-13 09:32:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2175ms | quality=1.00 | cache_age=139s | exceptions_10m=6 | exc_tags=[ExitCooldown]×2 [Peter2Offset]×2 [Peter2]×2
  …
2026-10-13 14:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=363ms | quality=1.00 | cache_age=92s | exceptions_10m=4 | exc_tags=[CB③-P4]×2 [SHAP]×2
2026-10-13 14:40:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1030ms | quality=1.00 | cache_age=81s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-10-13 14:41:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=545ms | quality=1.00 | cache_age=141s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-13 14:57:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=399ms | quality=1.00 | cache_age=182s | exceptions_10m=3 | exc_tags=[CB③-P4]×2 [SHAP]×1
2026-10-13 14:58:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=345ms | quality=1.00 | cache_age=58s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 18 | 09:00:01 | 14:57:00 | level=WARNING degraded=OFF | latency=1550ms | quality=1.00 | cache_age=53s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |

**채널** — `HEALTH`×36

**컴포넌트 상위 15** — `Health`×35, `HealthTrend`×1

### `logs/retrain_eod_20261013.log` — 21.8KB · 149행 · 최종 15:53:42

- 형식 평문 · 시각 인식 149행 · WARNING=11, INFO=138

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 15:50:03,022 [INFO] EOD_RETRAIN: =======================================================
2026-10-13 15:50:03,022 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-13 15:50:03,022 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-13 15:50:03,022 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-13 15:50:03,023 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-13 15:53:42,380 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0364 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-13 15:53:42,383 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1177 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-13 15:53:42,386 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.09s
2026-10-13 15:53:42,391 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.09s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-13 15:53:42,392 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:38 | 15:52:39 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1501봉(81%)이 현행 학습구간 (현행 cutoff=2026-10-12 14:38:00 ≥ 홀드아웃 시작=2026-10-02 12:46:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-12 14:38 >= holdout_start=2026-10-02 12:46 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-12 … |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-13 | 최신 2026-10-12 · 기준 5거래일. 복구: python scripts/collect_regular_futures.py --from 20261013 --to 20261013 |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 19717/44080 제외 (418차 결정 1) — 남은 24363행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/24363행 제외 (559차 P1'-2) — 남은 22917행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `Retrain` | 1 | 15:50:50 | 15:50:50 | 3m 교체 보류(EOD 모델가드) — acc 하락 0.0469 > 허용 0.0250 (new=0.3581 old=0.4050) — 참고용 저장, 구모델 유지 |
| `RegimeFingerprint` | 1 | 15:53:41 | 15:53:41 | 백필 0행 제외 — 필터가 무효일 수 있다. 20440행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×63, `SIGNAL`×49, `EOD_RETRAIN`×27, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×22, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2, `P8`×2

### `logs/20261013_MICRO.log` — 1.2MB · 3191행 · 최종 15:33:15

- 형식 평문 · 시각 인식 3191행 · DEBUG=3191

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=975.90/2 ask1=976.62/3 mp={'microprice_tick': 976.188, 'midprice_tick': 976.26, 'depth_bias_tick': -0.5403} mlofi_tick=None queue=None
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=975.90/2 ask1=976.62/3 mp={'microprice_tick': 976.188, 'midprice_tick': 976.26, 'depth_bias_tick': -0.5386} mlofi_tick=-2.45 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=975.90/3 ask1=976.60/2 mp={'microprice_tick': 976.32, 'midprice_tick': 976.25, 'depth_bias_tick': -0.3316} mlofi_tick=-7.5333 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.6…
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=975.90/1 ask1=976.60/2 mp={'microprice_tick': 976.1333, 'midprice_tick': 976.25, 'depth_bias_tick': -0.5778} mlofi_tick=-2.0 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1.09…
2026-10-13 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=975.68/1 ask1=976.40/1 mp={'microprice_tick': 976.04, 'midprice_tick': 976.04, 'depth_bias_tick': -0.0914} mlofi_tick=-5.5667 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
  …
2026-10-13 15:32:13 [DEBUG] MICRO: [MICRO-TICK] #278300 bid1=946.60/1 ask1=946.84/1 mp={'microprice_tick': 946.72, 'midprice_tick': 946.72, 'depth_bias_tick': 0.298} mlofi_tick=-5.6667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-10-13 15:32:26 [DEBUG] MICRO: [MICRO-TICK] #278400 bid1=946.20/1 ask1=946.46/1 mp={'microprice_tick': 946.33, 'midprice_tick': 946.33, 'depth_bias_tick': -0.0242} mlofi_tick=-3.5333 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-10-13 15:32:43 [DEBUG] MICRO: [MICRO-TICK] #278500 bid1=945.88/1 ask1=946.26/2 mp={'microprice_tick': 946.0067, 'midprice_tick': 946.07, 'depth_bias_tick': 0.1548} mlofi_tick=-1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': …
2026-10-13 15:33:00 [DEBUG] MICRO: [MICRO-TICK] #278600 bid1=945.50/1 ask1=945.64/4 mp={'microprice_tick': 945.528, 'midprice_tick': 945.57, 'depth_bias_tick': -0.2416} mlofi_tick=1.75 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-10-13 15:33:15 [DEBUG] MICRO: [MICRO-TICK] #278700 bid1=945.62/1 ask1=945.78/1 mp={'microprice_tick': 945.7, 'midprice_tick': 945.7, 'depth_bias_tick': 0.3249} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
```

</details>

**채널** — `MICRO`×3191

**컴포넌트 상위 15** — `MICRO-TICK`×2807, `MICRO-MINUTE`×384

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 28 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 6 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 6 |
| 차단(`[차단]`) | 116 |
| 사이저 호출(`[Sizer]`) | 56 |

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

### CB③ 판정 가능 시간 — **0분 / 0분 (—)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

등급 분포 — `A급(원시C)`×26, `A급(원시X)`×2

**진입한 건들의 체크리스트 미통과 항목** — `fore`×28, `risk`×28, `chas`×10, `prev`×8, `cvd`×8, `ofi`×8

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×11, **2계약**×6, **3계약**×39

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×56

### 차단 사유 116건 · 42종

| 건수 | 사유 |
|---|---|
| 53 | 등급X — 미통과 항목: 2_confidence |
| 10 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 5 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 4 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 9_risk |
| 4 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 9_risk |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 9_risk |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 9_risk |
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
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.7pt > ATR×5.0=12.6pt (시가=974.66 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×53, `3_vwap`×14, `6_foreign`×14, `9_risk`×14, `7_prev_bar`×7, `4_cvd`×6, `5_ofi`×5, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 8건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×5
- `일간 리셋 완료` ×2
- `연속 손절 2회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 39건 · 최대 13844ms · 5초 초과 1건

상위 — 13844ms, 4688ms, 4437ms, 4187ms, 4141ms, 4094ms, 3781ms, 3750ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:32:13 | 13844ms | 2175ms | **11669ms (84%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261013_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:06 2026-10-13 15:40:06 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 52분/일 < 하한 60분 — 금일 83분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- PSI ×1(표본)
15:40:03 2026-10-13 15:40:03 [WARNING] SYSTEM: [RegimeFingerprint] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerprint] 기준선 키 불일치` WARNING 이 기동 로그에 있는지 먼저 확인할 것
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
--- ConstOut ×8(표본)
09:35:00 2026-10-13 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3917) | 앙상블 제외는 유지
09:44:00 2026-10-13 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3578) | 앙상블 제외는 유지
10:56:00 2026-10-13 10:56:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3945) | 앙상블 제외는 유지
11:05:00 2026-10-13 11:05:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4252) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:06 2026-10-13 15:40:06 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 0분 / 파이프라인 0분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-13 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:05:00 2026-10-13 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:11:00 2026-10-13 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
09:16:00 2026-10-13 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.002 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:05 2026-10-13 15:40:05 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:05 2026-10-13 15:40:05 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:09 2026-10-13 15:11:09 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×4(표본)
15:33:22 2026-10-13 15:33:22 [INFO] SYSTEM: [Shutdown] intent=user_restart keep_alive=True files=0
15:36:17 2026-10-13 15:36:17 [INFO] SYSTEM: [Shutdown] intent=user_restart keep_alive=True files=0
15:40:07 2026-10-13 15:40:07 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-10-13 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:07 2026-10-13 15:40:07 [INFO] SYSTEM: [Notify] ℹ️ [15:40:07] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:07 2026-10-13 15:40:07 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 412초
15:40:07 2026-10-13 15:40:07 [INFO] SYSTEM: 자동 종료 예약 — 427초 후 Qt 이벤트 루프 종료
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
--- 기동 복원 ×8(표본)
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
| 14:00 | 장중 후반 · 장중 재학습 | 2 | 13:54:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=33,613,809) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShad… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:35:46 [INFO] 설정 업데이트 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261013_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 24 | 08:52:39 [WARNING] A056B 실측=-1.9 n=7 spread=0.09 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.9 | 직전일=-2.2(prev_day:2026-10-12, … |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 69 | 09:00:01 [WARNING] total=1550ms | S0=2ms S1=14ms S2=0ms S3=0ms S4=102ms S5=944ms S6=470ms S7=12ms S8=5ms |
| 10:00 | 장중 초반 | 159 | 09:54:47 [WARNING] paintEvent slow 126.3ms | size=1793x950 candles=70 grid=33.9 spans=21.7 candles=19.5 dir=0.3 regime=0.2 marke… |
| 12:00 | 장중 중간점 | 107 | 11:54:00 [WARNING] 과신 경고 | 이동평균=0.359 > 0.35 |
| 14:00 | 장중 후반 · 장중 재학습 | 96 | 13:54:00 [WARNING] paintEvent slow 111.1ms | size=1041x876 candles=131 grid=27.9 spans=21.0 candles=11.5 dir=0.6 regime=0.5 mark… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 97 | 15:04:02 [WARNING] paintEvent slow 109.4ms | size=1041x876 candles=131 grid=35.5 spans=14.5 candles=12.0 dir=0.6 regime=0.5 mark… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 100 | 15:12:00 [WARNING] paintEvent slow 114.9ms | size=1041x876 candles=131 grid=15.1 spans=18.4 candles=13.9 dir=0.6 regime=0.5 mark… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 42 | 15:35:50 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 15:47 | EOD 재학습(py310_64) 완료 | 7 | 15:46:03 [WARNING] OHLCV 불일치 ts=2026-10-13 10:04:00 cols=['open'] existing_source=rt |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261013_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 97 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=14192 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 171 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 270 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 234 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 227 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 224 | 13:54:00 [INFO] code=A056B from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 203 | 15:04:01 [INFO] code=A056B from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 178 | 15:12:00 [INFO] code=A056B from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 175 | 15:35:22 [INFO] 활성화 | file=logs\crash_fault.log PID=17288 | 행감지=30s all_threads=True |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:42:03 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:42:03 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261013_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 38 | 08:45:09 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 89 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0013 → floor=0.10 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 240 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0013 → floor=0.10 적용 (z-score 폭발 방지) |
| 10:00 | 장중 초반 | 140 | 09:54:00 [WARNING] ts=09:53 horizon=1m age=3m max_z=-4.21(mlofi_slope) extreme=1 adj=1 |
| 12:00 | 장중 중간점 | 167 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=7m max_z=+4.13(volume_acceleration) extreme=1 adj=1 |
| 14:00 | 장중 후반 · 장중 재학습 | 165 | 13:56:00 [WARNING] 신뢰도 미달 32.8% < 37.8% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 61 | 15:04:02 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 37 | 15:35:18 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.433 |

- 이 로그 생존구간: 08:40 ~ 15:40

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
| **오늘 20261013** | **15:47** | 로그 본문 |

- 델타 **-166분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-13 (MW0601 688차 — 687차 후속 장중 점검)
### 증거수집
### 오늘 거래 결과 — 보조 로직(피터2) 6전 6패 -1,040,578원
### [신규 P1] 이상점 1-2 — 피터2 진입 6건 전부 "(추정귀속)" 오분류, 근본 메커니즘 확정
### 결정
### Why
### How to apply
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
sition] 진입`
로그가 찍혀 있다** — "로그 자체가 없다"는 종전 가설(Chejan 선행 체결 레이스, 10/7 사례는
이미 장후 DB대조로 기각됨)과는 다른 경우다.

`strategy/position/position_tracker.py:549-550`:
```python
_hz_tag = f" horizon={entry_horizon}" if entry_horizon else ""
_hb_tag = f" hurst={hurst_bucket}" if _regime_mult else ""
```
피터2 경로는 `entry_horizon=None`을 넘겨(`[PositionFallback] entry_horizon 미설정` 경고와
동일 원인, 기존 F-5 등록 사안) `_hz_tag`가 빈 문자열이 되고, 로그 줄에서
`horizon=…hurst=…` 접미사가 통째로 빠진다.

수집기 entry 정규식(`.claude/skills/mireuk-daily-check/scripts/collect_evidence.py:169`):
```python
"entry": r"\[Position\] 진입 (?P<dir>\w+) (?P<qty>\d+)계약 @ (?P<px>[\d.]+).*?horizon=(?P<hz>\w+)\s+hurst=(?P<hurst>\S+)",
```
이 접미사를 필수로 요구해 매치 실패 → `assemble_positions()`가 "진입 로그 없음"으로 보고
체결(`[체결진입]`)만으로 재구성(`inferred=True`, "(추정귀속)"). `data/position_state.json`
(09:48:34 스냅샷)의 `entry_source: "PETER2"` 필드로 코드 레벨 출처는 명확함을 교차 확인.

부수 확인: 수집기의 자동 적신호("엔진 진입 0건인데 계좌 체결 N건", `collect_evidence.py:1550`)
는 `ext_entry`(외부동기화) 비어있지 않은 경우만 보도록 짜여 있어, 오늘처럼 외부동기화 0건인
케이스에서는 발동하지 않았다 — 이 적신호도 사각지대가 있음을 확인(G-6로 등록).

### 결정
이상점 1-2(P1)로 등록, Fix는 기존 F-5(PositionFallback)에 합류(함정① — 근본원인
`entry_horizon=None`이 F-5와 동일). 신규 제안 F-5 확장: 수집기 entry 정규식의
`horizon=`/`hurst=` 접미사를 선택 항목으로 변경(`collect_evidence.py:169`). G-6: 자동
적신호 조건을 "체결>0 and 엔진==0"으로 넓혀 외부동기화 여부와 무관하게 발동하도록.
둘 다 로그 파싱/수집기 전용 — 라이브 매매 로직 미변경, 저위험. 이 세션은 장중 규약상
코드를 변경하지 않았다(계획만 제시, 승인 시 장후 또는 별도 세션 적용).
확정 판정은 장후에 `trades.db`의 `entry_source='PETER2'` 6건과 대조 후.

### Why
계측 4원칙① — 실측 로그가 존재하는데도 집계 프로그램의 요건 불일치로 "측정 불가"로
떨어졌다. 손익·수량은 체결 실측이라 정확(정합성 확인 완료) — 영향받는 것은 "오늘 거래를
엔진 vs 보조 로직 중 누구 책임으로 보는가"라는 보고서 분류뿐, 실손익 집계는 오염되지 않았다.

### How to apply
`collect_evidence.py:169`의 entry 정규식에서 `.*?horizon=(?P<hz>\w+)\s+hurst=(?P<hurst>\S+)`
부분을 선택적(optional) 그룹으로 변경 — 접미사가 없으면 `hz`·`hurst`를 `None`으로 두고도
"엔진 진입"으로 인정. 변경 전 `tests/test_482_position_assembler.py` 등 기존 조립기
테스트가 깨지지 않는지 먼저 확인(함정① — 이미 있는 테스트 보호). `collect_evidence.py:1550`
적신호 조건은 `if _fi_kept and not en:`로 변경 검토.

### 검증
`logs/20261013_TRADE.log:4,19,32,47,61,75`(진입 6건) · `logs/20261013_TRADE.log:15,29,43,57,72,86`
(청산 6건, 전부 하드스톱(틱)) · `data/position_state.json.gen_20261013_095311`
(entry_source=PETER2 교차확인) · `strategy/position/position_tracker.py:549-558` ·
`.claude/skills/mireuk-daily-check/scripts/collect_evidence.py:169,1550`.
장후 재검증: `trades.db` entry_source='PETER2' COUNT 6건 vs 오늘 요약 "(추정귀속) 6건" 대조.

**라이브 미검증 항목 기한(갱신)**: F-18 라이브 검증·10/12 재기동 의도 확인은 오늘도
재기동 0건으로 표본 없음 — 무기한 대기 지속. F-15·1-2 확정 판정은 장후로 이월(미루지 않음,
오늘 장후에 반드시 처분).

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2)
## 2026-10-12 (MW0601 680차 — 장전 점검)
## 2026-10-12 (MW0601 681차 — 장중 점검)
## 2026-10-12 (MW0601 682차 — 장후 점검)
## 2026-10-12 (MW0601 684차 — 682차 후속 장후 자동조치)
## 2026-10-12 (MW0601 686차 — option_hts MW0602 미러)
## 2026-10-13 (MW0601 687차 — 장전 점검)
## 2026-10-13 (MW0601 688차 — 687차 후속 장중 점검)
```

미완료 체크박스 **3134건** (끝에서 30건)
```
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
- [ ] F-5 확장(P1, 신규 제안) — 수집기 entry 정규식(`collect_evidence.py:169`)의
- [ ] G-6(P2, 신규 제안) — 수집기 자동 적신호("엔진 0건인데 계좌 체결 N건",
- [ ] 1-2 확정 판정(장후 소관, 이월 금지) — `trades.db` entry_source='PETER2' COUNT 6건
- [ ] 보조 로직(피터2) 6전 6패 -1,040,578원 케이스 딥다이브 — 장후 제4부 진입 승패
- [ ] F-18 라이브 검증(지속) — 오늘도 기동 1회·재시작 0건, 표본 없음.
- [ ] 10/12 09:33·11:22 재기동 의도 사용자 확인(지속) — 오늘 재기동 0건, 새 관찰 없음.
- [ ] F-15 반영 확인(장후 소관, 이월 금지) — 오늘 체결 6건, `commission_rate_used` 확정 판정.
- [ ] F-16(소급 정정)·F-1(538-4)·F-2·663-1(F-5)·663-2(F-7) — 전부 지속, 변화 없음.
- [ ] 미커밋 변경 106건(실질 3건) 정리 확인 — `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 변화 없음(10/9 673차부터 등록).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 완료, Everyone Read 확인)** 읽기전용 공유 생성:
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

## 2026-10-13 (MW0601 688차 — 687차 후속 장중 점검)
- [ ] F-5 확장(P1, 신규 제안) — 수집기 entry 정규식(`collect_evidence.py:169`)의
      `horizon=`/`hurst=` 접미사를 선택 항목으로 변경, 접미사 없어도 `[Position] 진입`
      줄이면 엔진 진입으로 인정. 변경 전 `tests/test_482_position_assembler.py` 영향 확인.
      장후 승인 대기.
- [ ] G-6(P2, 신규 제안) — 수집기 자동 적신호("엔진 0건인데 계좌 체결 N건",
      `collect_evidence.py:1550`) 조건을 `if _ext and not en` → `if _fi_kept and not en`로
      넓혀 외부동기화 없는 케이스도 잡히게. 장후 검토.
- [ ] 1-2 확정 판정(장후 소관, 이월 금지) — `trades.db` entry_source='PETER2' COUNT 6건
      vs 오늘 "(추정귀속) 6건" 대조.
- [ ] 보조 로직(피터2) 6전 6패 -1,040,578원 케이스 딥다이브 — 장후 제4부 진입 승패
      사후검증에서 "추세 하락 중 반복 LONG 재진입이 왜 허용됐는가"(재진입 조건에 추세
      필터 존재 여부) 요인 귀인.
- [ ] F-18 라이브 검증(지속) — 오늘도 기동 1회·재시작 0건, 표본 없음.
- [ ] 10/12 09:33·11:22 재기동 의도 사용자 확인(지속) — 오늘 재기동 0건, 새 관찰 없음.
- [ ] F-15 반영 확인(장후 소관, 이월 금지) — 오늘 체결 6건, `commission_rate_used` 확정 판정.
- [ ] F-16(소급 정정)·F-1(538-4)·F-2·663-1(F-5)·663-2(F-7) — 전부 지속, 변화 없음.
- [ ] 미커밋 변경 106건(실질 3건) 정리 확인 — `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 변화 없음(10/9 673차부터 등록).

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

### `data/dailycheck_markers/MW0601-20261013-intra-pid7.json` — 157B · 10-13 12:35:07
```json
{
 "pc": "MW0601",
 "date": "20261013",
 "phase": "intra",
 "session": "pid7",
 "pid": 7,
 "started_epoch": 1791862507.0654602,
 "started_at": "2026-10-13 03:35:07"
}
```

### `data/dailycheck_markers/claude-20261013-post-cowork-post-20261013.json` — 171B · 10-13 16:17:16
```json
{
 "pc": "claude",
 "date": "20261013",
 "phase": "post",
 "session": "cowork-post-20261013",
 "pid": 7,
 "started_epoch": 1791875836.608809,
 "started_at": "2026-10-13 07:17:16"
}
```

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

### `data/heartbeat_MW0601_20261013.json` — 245B · 10-13 15:47:04
```json
{
 "pid": 19652,
 "written_at": "2026-10-13T15:47:04",
 "beat_epoch": 1791874023.6274507,
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

### `data/peter_feed/_raw/2026-10-13.jsonl` — 9.9KB · 10-13 15:13:53
```json
JSONL 49행 ⏎ 첫: {"id": "2109792714858664353", "dt": "2026-10-12T23:45:55.000Z", "text": "제가 방송에서 제시한 종목중 손절가에 도달해서 손절된 종목들이 있다면.\n\n손절 가격에서 5-10프로 더 떨어진 가격에서 재매수 가능합니다.\n단, 그 가격에서 7프로 이하를 다시 손절가 잡으면 됩니다.\n\n만약 코스피 추가하락이 예상되어 기다리고 싶으면\n\n차라리 다시 제가 제시한 매수가 올때까지", "seen_at": "2026-10-13T08:46:07+09:00", "src": "live"} | {"id": "2109794316357079252", "dt": "2026-10-12T23:52:17.000Z", "text": "오늘도 매수 단타만 할 예정.\n\n975 아래로 떨어지면 기회 보고 장초부터 들어갈 예정", "seen_at": "2026-10-13T08:52:52+09:00", "src": "live"} | {"id": "2109796086886093222", "dt": "2026-10-12T23:59:19.000Z", "text": "975 매수체결.", "seen_at": "2026-10-13T09:01:08+09:00", "src": "live"} ⏎ 끝: {"id": "2109882673531621457", "dt": "2026-10-13T05:43:23.000Z", "text": "", "seen_at": "2026-10-13T14:43:52+09:00", "src": "live"} | {"id": "2109882598411674054", "dt": "2026-10-13T05:43:05.000Z", "text": "", "seen_at": "2026-10-13T14:43:52+09:00", "src": "live"} | {"id": "2109890309379547629", "dt": "2026-10-13T06:13:44.000Z", "text": "저는 개인적으로 940 매수분 들고 오버나잇합니다.\n\n4+3+3+4+5+4+4+5= 32p 손실", "seen_at": "2026-10-13T15:13:53+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-13 15:53:42**

| 키 | 값 | 수집 대상일(2026-10-13)과 일치 |
|---|---|---|
| `date` | 2026-10-13 | 예 |
| `p8_last_success_date` | 2026-10-13 | 예 |
| `eod_retrain_ok_date` | 2026-10-13 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-13 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-12) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-13 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-12) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261013_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 3회 · 재시작 1회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 3개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **9건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 14192: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
- PID 17288: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 15:35:22 · 정규장(09:00) 이후 **3건**
- PID 19652: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 15:36:39 · 정규장(09:00) 이후 **3건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 14192 | 08:40:45 | 15:33:22 | 없음 | 판정불가 — WER **미측정** |
| 17288 | 15:35:22 | 15:36:17 | 없음 | 판정불가 — WER **미측정** |
| 19652 | 15:36:39 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


#### 재기동 귀속 대사 (684차 G-5)

| 재시작 | 런처 분류 | 종료 의도 로그(−3~+1분) | ±5분 이내 커밋(설명 후보) | 창 밖 당일 커밋 |
|---|---|---|---|---|
| 15:36 | 일시적 크래시 | 15:33 `user_restart`, 15:36 `user_restart` | 없음 | 2건(시각 불일치 — 후보 아님) |

- 🔴 커밋은 **인과가 아니라 후보**다. 창 밖 커밋을 원인으로 적지 말 것.
- 「종료 의도 로그 **없음**」 + `[CLEAN EXIT]` 있음 = 의도 경로를 거치지 않은 정상 종료다. ⚠ **684차 이전**의 X 버튼 종료(`user_close`/`user_restart`)는 로그 파일에 남지 않았다(모듈 로거가 파일 핸들러에 안 붙어 있었다) — 그 시기의 「없음」은 X 버튼 재시작을 배제하지 못한다.

> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 222개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261013-점검리포트.md` | 31.5KB | 10-13 12:45 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261013.md` | 17.5KB | 10-13 12:42 |
| `docs/정기점검/매일점검/evidence_MW0601-20261013_intra.md` | 84.4KB | 10-13 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261013_pre.md` | 61.3KB | 10-13 08:59 |
| `docs/정기점검/매일점검/MW0601-20261012-점검리포트.md` | 79.2KB | 10-12 17:32 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_post.md` | 99.1KB | 10-12 16:18 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261012.md` | 18.0KB | 10-12 12:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_intra.md` | 84.1KB | 10-12 12:27 |

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

1. **엔진 진입 0건 / 계좌 진입 6건**(그중 외부표식 0건) — 차단 116건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
2. 포지션 6건 중 최종청산이 하드스톱·손절 계열 **6건(100%)** — 손절 준수율 확인 필요 (레그 6행)
3. **SYSTEM 로그가 직전 5거래일 중앙값(18:33)보다 166분 이르게 끝났다** (오늘 15:47) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
4. 메인 스레드 정지 5초 초과 **1건** (최대 13844ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
5. `logs/20261013_WARN.log`: **[Brier] 과신** 8건(표본)
6. `logs/20261013_SYSTEM.log`: **ConstOut** 8건(표본)
7. `logs/20261013_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20261013_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20261013_LEARNING.log`: **축퇴** 8건(표본)
10. `logs/crash_fault.log`: `Windows fatal exception` **9건** (정규장 09:00 이후 6건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
11. 미커밋 변경 117건 (실질 6건 · 코드 0건 · EOL 파생 0건)
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261013*.log` (Windows) / `grep 강제청산 logs/*20261013*.log`*