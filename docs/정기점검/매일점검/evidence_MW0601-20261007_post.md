# 미륵이 증거 다이제스트 — 2026-10-07 / POST

- 생성 2026-10-07 16:16:57 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01va6wqw7yyxwk5epwcwg6gy/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261007` · `2026-10-07` · `261007` · `1007`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **43개** 파일 · 43개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261007.txt` | 28B | 10-07 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261007.txt` | 28B | 10-07 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261007.txt` | 233B | 10-07 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261007.log` | 1.4KB | 10-07 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261007.log` | 216B | 10-07 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261007.json` | 245B | 10-07 15:46 |
| `launcher_{DATE}_084001_19477.log` | 1 | `logs/Mireuk_batch/launcher_20261007_084001_19477.log` | 2.4MB | 10-07 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261007.log` | 24.0KB | 10-07 15:46 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261007.log` | 513B | 10-07 16:15 |
| `position_state.json.gen_{DATE}_111112` | 1 | `data/position_state.json.gen_20261007_111112` | 1.6KB | 10-07 11:08 |
| `position_state.json.gen_{DATE}_111901` | 1 | `data/position_state.json.gen_20261007_111901` | 1.5KB | 10-07 11:19 |
| `position_state.json.gen_{DATE}_111917` | 1 | `data/position_state.json.gen_20261007_111917` | 1.5KB | 10-07 11:19 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261007.log` | 22.8KB | 10-07 15:53 |
| `retrain_intraday_20260701_{DATE}00.log` | 1 | `logs/retrain_intraday_20260701_100700.log` | 4.6KB | 07-01 10:07 |
| `retrain_intraday_20260805_{DATE}01.log` | 1 | `logs/retrain_intraday_20260805_100701.log` | 4.5KB | 08-05 10:07 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261007.log` | 53.6KB | 10-07 15:59 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261007.txt` | 43B | 10-07 15:47 |
| `strategy_report_{DATE}_154022.txt` | 1 | `data/daily_reports/strategy_report_20261007_154022.txt` | 2.5KB | 10-07 15:40 |
| `{DATE}_0916_D.xls` | 1 | `data/db/option_hts/261007_0916_D.xls` | 480.3KB | 10-07 09:16 |
| `{DATE}_1008_D.xls` | 1 | `data/db/option_hts/261007_1008_D.xls` | 480.4KB | 10-07 10:06 |
| `{DATE}_1031_D.xls` | 1 | `data/db/option_hts/261007_1031_D.xls` | 480.5KB | 10-07 10:31 |
| `{DATE}_1103_D.xls` | 1 | `data/db/option_hts/261007_1103_D.xls` | 480.5KB | 10-07 11:04 |
| `{DATE}_1144_D.xls` | 1 | `data/db/option_hts/261007_1144_D.xls` | 480.5KB | 10-07 11:44 |
| `{DATE}_1215_D.xls` | 1 | `data/db/option_hts/261007_1215_D.xls` | 480.6KB | 10-07 12:15 |
| `{DATE}_1244_D.xls` | 1 | `data/db/option_hts/261007_1244_D.xls` | 480.6KB | 10-07 12:44 |
| `{DATE}_1316_D.xls` | 1 | `data/db/option_hts/261007_1316_D.xls` | 480.6KB | 10-07 13:16 |
| `{DATE}_1345_D.xls` | 1 | `data/db/option_hts/261007_1345_D.xls` | 480.6KB | 10-07 13:45 |
| `{DATE}_1415_D.xls` | 1 | `data/db/option_hts/261007_1415_D.xls` | 480.6KB | 10-07 14:15 |
| `{DATE}_1519_D.xls` | 1 | `data/db/option_hts/261007_1519_D.xls` | 480.6KB | 10-07 14:46 |
| `{DATE}_D.xls` | 1 | `data/db/option_hts/261007_D.xls` | 480.6KB | 10-07 15:45 |
| `{DATE}_DATA.log` | 1 | `logs/20261007_DATA.log` | 439.8KB | 10-07 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261007_DEBUG.log` | 241.4KB | 10-07 15:10 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261007_HEALTH.log` | 5.3KB | 10-07 14:36 |
| `{DATE}_HOGA.log` | 1 | `logs/20261007_HOGA.log` | 51.8MB | 10-07 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261007_LEARNING.log` | 287.6KB | 10-07 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261007_MICRO.log` | 969.0KB | 10-07 15:36 |
| `{DATE}_P.xls` | 1 | `data/db/option_hts/261007_P.xls` | 481.5KB | 10-07 15:46 |
| `{DATE}_PROBE.log` | 1 | `logs/20261007_PROBE.log` | 94.6KB | 10-07 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261007_REGULAR_COLLECT.log` | 6.6KB | 10-07 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261007_SIGNAL.log` | 646.6KB | 10-07 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261007_SYSTEM.log` | 1013.1KB | 10-07 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261007_TRADE.log` | 25.5KB | 10-07 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261007_WARN.log` | 685.6KB | 10-07 15:47 |

## 2. 코드·커밋 상태

- HEAD `5cf61ee` · 브랜치 `v9-dev` · 미커밋 75건 · 실질 변경 10건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 10 · 미추적 65 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261007.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md`, `docs/정기점검/수익률향상_누적대장.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.8초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261007.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md
 M docs/정기점검/수익률향상_누적대장.md
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_20261002.md
?? dev_memory/_tmp_append_decisionlog_20261006_post.md
?? dev_memory/_tmp_append_decisionlog_20261007_intra.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261008.md
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
?? docs/신동거래/일일/신동_일일_MW0601_20261006.md
?? docs/신동거래/일일/신동_일일_MW0601_20261006.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261007.md
?? docs/신동거래/일일/신동_일일_MW0601_20261007.svg
… 외 35건
```

**당일(2026-10-07) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
5cf61ee [MW0601] 662차 후속6: 사다리 「신동2 해설」 패널에 익일 계획 표시
eb4bad3 [MW0601] 662차 후속5: 신동2 예약작업(3단계) — 월–금 5개 작업 등록 · 헤드리스 Claude 래퍼 · 첫 실제 장후 실행
b9aa63b [MW0601] 662차 후속4: 신동2 라이브 — 스킬 · 이벤트 감지 · 사다리 「신동2 해설」 패널 · 재량(AI) 기록·채점
f9d4b64 [MW0601] 662차 후속3: 신동2 — 피터 진입(1116)·청산가(1095) 딥다이브 + 섀도 P2·P3 + S1·E2 기록
9f993ea [MW0601] 662차 후속2: 신동2 문서 폴더 통합 — 미래예측 → docs/미륵이고도화3/신동2
e682703 [MW0601] 662차 후속: 신동2 — 외인 수급 시점별(PIT) 제안·채점 + 신동2-P(피터식 보유) 사전등록 + 사다리 표시
d600c5b [MW0601] 663차: 661차 후속 장후 자동조치 기록 — DECISION_LOG·NEXT_TODO (659–661차 점검 기록 포함)
d30a9cd [MW0601] 661차 후속: 장후 자동조치 — F-1·F-3·F-4·F-6·A-3·G-3
2967e9a [MW0601] 662차: dll_bootstrap 이 pywin32 두 벌 중 옛 판을 앞세워 옵션 흐름 마감 재수집 실패 — pywin32_system32 뒤로
8e3ccec [MW0601] 656차 후속4: 사다리에 선물 주체별 누적 순매수 띠 — 옵션 흐름과 같은 시간축
84bb350 [MW0601] 656차 후속3: 사다리 당일 외인·개인 층에 전일 보유 그림자 + 현재 보유 눈금
9412bd3 [MW0601] 656차 후속2: 사다리 9842 시점 파일(YYMMDD_HHMM_D) — 30분 단위 외인·개인 증감
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

_본문 미열람(설정): `20261007_HOGA.log` 51.8MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261007.txt`** — 28B · 10-07 15:40:22
```
2026-10-07T15:40:22.715023
```

**`data/daily_close_started_20261007.txt`** — 28B · 10-07 15:40:08
```
2026-10-07T15:40:08.064420
```

**`data/daily_reports/strategy_report_20261007_154022.txt`** — 2.5KB · 10-07 15:40:22
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-07 15:40
========================================================
  버전    : v1.0  (93일차)
  판정    : OUTPERFORM
  Live(20일): Sh=2.51  MDD(자본대비)=3.0%
  당일      : WR=80.0%  PF=0.26
  롤링20일: 누적 +5404225원  Sh=2.51  MDD(자본대비)=3.0%  MDD(peak대비)=24.7%
  당일손익 : broker(gross) -19,000원  수수료 95,998원  net -114,998원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.000  vwap_position=0.034
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 -25,613원  승률 40.0%  합계 -512,252원
  등급별 순EV(30일): A=+105,528원(59건,승53%)  BROKER=+231,616원(2건,승100%)  MANUAL=-51,406원(25건,승44%)
  호라이즌별 순EV(30일): 1m=-1,283원(8건)  3m=+15,033원(32건)  5m=-68,603원(17건)  ?=+210,334원(29건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 83분  5일평균 41분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 27.8pt(5일평균 24.7pt)  1분평균변동 0.58pt(5일평균 0.61pt)
--------------------------------------------------------
  진입 퍼널(2026-10-07, 총 371분):
    FLAT 211 → conf미달 70 → CoherenceGate 7 → 게이트차단 65 → 후보 18 → 진입 5
    └ 등급상향경로(앙상블X→체크리스트통과): 2건 [285차-P5]
    게이트별: ATR변동성=20  포지션보유중(평가생략)=10  콜드스타트/기타(DataAnomalyGate)=8  체크리스트항목미달=7  시가갭(OPEN_VOLATILE)=7  콜드스타트/기타(σ미수집)=4  쿨다운=4  모드필터=3  콜드스타트/기타(조건부구간)=2
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 13건
      └ 상세: JointGateBlock=13
      └ JointGateBlock 13건 (무정보폴백 10건 = 76.9%) [표본 7건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261007.txt`** — 233B · 10-07 15:53:47
```
completed: 2026-10-07 15:53:47
rows: 19403
cols: 97
phase2_fallback: false
horizons_replaced: 5/6
t_load_s: 26.4
t_retrain_s: 196.1
t_total_s: 223.0
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20261007.txt`** — 43B · 10-07 15:47:14
```
auto_shutdown
2026-10-07T15:47:14.733124
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260805_100701.log`, `20261007_MICRO.log`, `20261007_DATA.log`, `20261007_PROBE.log`, `launcher_20261007_084001_19477.log`, `20261007_DEBUG.log`, `shindong2_20261007.log`, `mainstall_traceback_20261007.log`_

### `logs/20261007_TRADE.log` — 25.5KB · 168행 · 최종 15:40:09

- 형식 평문 · 시각 인식 168행 · INFO=168

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-07 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-07 09:32:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-07 09:33:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-07 09:38:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-10-07 14:17:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.0→3계약]
2026-10-07 14:18:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.2→3계약]
2026-10-07 14:19:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdvisedSkip]
2026-10-07 14:21:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.0→3계약]
2026-10-07 15:40:09 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×168

**컴포넌트 상위 15** — `Sizer`×52, `Chejan`×32, `Position`×21, `JointGateBlock 차단`×13, `주문요청`×13, `체결진입`×6, `진입체크`×5, `TickStop-S0C`×5, `청산 완료`×5, `TickTP1`×4, `모드필터 차단`×3, `체결진입보정`×3, `TP1 부분청산`×3, `ProfitGuard`×2, `손절1차 조기축소`×1

### `logs/20261007_WARN.log` — 685.6KB · 3074행 · 최종 15:47:11

- 형식 평문 · 시각 인식 3074행 · ERROR=3, WARNING=3071

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-10-07 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-07 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-07 15:46:16 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (8/20) → logs/mainstall_traceback_20261007.log
2026-10-07 15:46:16 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 99.7ms | size=1955x1124 candles=411 grid=23.0 spans=14.1 candles=15.4 dir=1.5 regime=6.4 markers=36.7 axes=0.6 cross=0.0 | slow_cnt=2500 total_cnt=2641 overlay_cnt=28318
2026-10-07 15:46:29 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 118.9ms | size=1955x1124 candles=411 grid=27.9 spans=19.0 candles=15.8 dir=1.4 regime=6.2 markers=45.7 axes=0.7 cross=0.0 | slow_cnt=2501 total_cnt=2642 overlay_cnt=28318
2026-10-07 15:46:32 [WARNING] SYSTEM: [LiveDBG] DynMCPanel.refresh slow 281ms
2026-10-07 15:47:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 98.7ms | size=1955x1124 candles=411 grid=22.2 spans=11.0 candles=15.4 dir=1.3 regime=6.4 markers=40.0 axes=0.7 cross=0.0 | slow_cnt=2502 total_cnt=2643 overlay_cnt=28319
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `LiveDBG` | 2 | 11:21:18 | 11:25:24 | _tick_header 간격 18204ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=18204 band=ALERT since_pipe_s=10.0 |
| ERROR | `BarGap` | 1 | 15:46:08 | 15:46:08 | 당일 확정(2026-10-07) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉 | ⚠ 절단선 초과 1봉 (15:09) — 15:10 파이프라인 중단선 미작동 |

<details><summary>ERROR/LiveDBG 원문 2건</summary>

```
2026-10-07 11:21:18 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 18204ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=18204 band=ALERT since_pipe_s=10.0
2026-10-07 11:25:24 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 23750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23750 band=ALERT since_pipe_s=0.4
```

</details>

<details><summary>ERROR/BarGap 원문 1건</summary>

```
2026-10-07 15:46:08 [ERROR] SYSTEM: [BarGap] 당일 확정(2026-10-07) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉 | ⚠ 절단선 초과 1봉 (15:09) — 15:10 파이프라인 중단선 미작동
```

</details>

**WARNING — 태그 39종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2502 | 08:52:24 | 15:47:11 | paintEvent slow 41.9ms | size=1955x1124 candles=8 grid=21.2 spans=0.0 candles=0.3 dir=0.0 regime=0.0 markers=0.0 axes=19.2 cross=0.0 | slow_cnt=1 total_cnt=3 overlay_cnt=2 |
| `LiveDBG` | 193 | 08:41:07 | 15:46:32 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 68 | 08:41:17 | 15:34:36 | 그리기 59.1ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 856x1001 |
| `ChejanFlow` | 32 | 10:20:01 | 11:19:17 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1438' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=10:20:00.956' | positi… |
| `ChejanMatch` | 32 | 10:20:01 | 11:19:17 | order_no='1438' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1438 reason=진입 req_at=10:20:00.956' | pending_matched=True |
| `PendingOrder` | 28 | 10:20:00 | 11:19:17 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1091.52, 'reason': '진입', 'hint_source': '', 'atr': 1.2886, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `SHAP` | 23 | 10:45:01 | 15:04:01 | 슬로우 감지 1018ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `PipePerf` | 20 | 09:32:01 | 13:50:01 | total=1064ms | S0=1ms S1=48ms S2=22ms S3=0ms S4=149ms S5=155ms S6=142ms S7=546ms S8=2ms |
| `CB⑤` | 20 | 09:32:01 | 13:50:01 | 파이프라인 1064ms 경고 (기준 1000ms) |
| `Health` | 16 | 09:32:01 | 14:36:00 | level=WARNING degraded=OFF | latency=1064ms | quality=1.00 | cache_age=137s | exceptions_10m=0 |
| `CB③-P4` | 16 | 11:30:00 | 14:19:59 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `ScalerRefresh` | 15 | 09:06:00 | 14:56:59 | 5분 누적 수익률 +0.723% (임계 ±0.572%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |

**채널** — `SYSTEM`×3058, `HEALTH`×16

**컴포넌트 상위 15** — `ChartDBG`×2502, `LiveDBG`×195, `OptionFlowChart`×68, `ChejanFlow`×32, `ChejanMatch`×32, `PendingOrder`×28, `SHAP`×23, `PipePerf`×20, `CB⑤`×20, `Health`×16, `CB③-P4`×16, `ScalerRefresh`×15, `SessionBackfill`×12, `ExitCooldown`×10, `MainStallTrace`×10

### `logs/20261007_SYSTEM.log` — 1013.1KB · 6756행 · 최종 15:47:14

- 형식 평문 · 시각 인식 6735행 · INFO=6735, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=12412 | 행감지=30s all_threads=True
2026-10-07 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-07 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-07 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-07 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-07 15:46:08 [INFO] SYSTEM: [SessionBackfill] 08:45 개장 체결 보정 ts=2026-10-07 08:45:00 rt O=1083.82/V=289 → chart O=1084.44/V=490
2026-10-07 15:46:08 [INFO] SYSTEM: [SessionBackfill] 2026-10-07~2026-10-07 chart=411 existing=410 inserted=1 open_fixed=1 mismatch=39
2026-10-07 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-07 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-07 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6735

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1140, `PumpGuard`×768, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×406, `S6Detail`×371, `PipePerf`×371, `System`×100, `MicroRegime`×93, `OptionChain`×81, `OptionBook`×79, `RegimeFingerprint`×68, `CybosEvent`×64

### `logs/20261007_SIGNAL.log` — 646.6KB · 5549행 · 최종 15:40:09

- 형식 평문 · 시각 인식 5549행 · WARNING=2340, INFO=3209

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-10-07 15:10:00 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-07 15:40:09 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-07 15:40:09 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 371분 중 섀도만 활성 UP 1분(0.3%) / DN 102분(27.5%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-07 15:40:09 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-07 age=32m extreme=852 refresh=36 grade_x=83 cb3=0
2026-10-07 15:40:09 [INFO] SIGNAL: [ModelHealth] date=2026-10-07 앙상블유효가동률=70.4% | 파이프라인 371분 | ConstOut 12회/23분 {"3m": {"events": 10, "minutes": 19}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 87분 | 장중재학습 0회 | CB③ ready 235분/371분 (63%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1704 | 09:00:02 | 14:57:00 | 1m 'macro_vix' scale=0.0163 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 234 | 09:00:00 | 14:41:59 | ts=08:59 horizon=1m age=1m max_z=-7.21(institution_futures_net) extreme=2 adj=2 |
| `Model` | 204 | 09:00:00 | 14:41:59 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 96 | 09:06:00 | 15:09:01 | CORE VWAP ✗ → 강제 X등급 (pass_count=9, group=short) | VWAP pos=+0.897 need <0 (SHORT) bull_exh=0.00 |
| `WeightCollapse` | 87 | 09:07:00 | 15:10:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 12 | 09:35:00 | 13:47:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 2 | 10:07:00 | 10:12:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `MetaGate` | 1 | 11:15:00 | 11:15:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×5549

**컴포넌트 상위 15** — `ScalerFloor`×1722, `SIGNAL`×742, `Ensemble`×375, `FQAdj`×370, `ZeroDiag`×304, `MetaGate`×294, `ScalerMonitor`×235, `Model`×210, `Checklist`×199, `ATR-Horizon`×145, `차단`×118, `ToxicityGate`×106, `MicroRegime`×93, `InstabilityGate`×92, `WeightCollapse`×87

### `logs/20261007_LEARNING.log` — 287.6KB · 2826행 · 최종 15:40:09

- 형식 평문 · 시각 인식 2826행 · WARNING=147, INFO=2679

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-10-07 08:40:49 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00081 auc=0.557 out_max=0.3115 (n=90) → 보정 재적용
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3115 < conf_floor=0.3300 (span=0.00081 auc=0.557 out_max=0.3115, 기저율=0.3111 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-07 15:40:09 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-07 15:40:09 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-07 15:40:09 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-07 15:40:09 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-07 15:40:09 [INFO] LEARNING: [Sigma] EOD sigma_20=0.05200% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 51 | 08:40:49 | 15:04:00 | 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 40 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 19 | 08:40:49 | 08:40:57 | 축퇴 감지 — span=0.00008 auc=0.523 out_max=0.3500 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 18 | 08:40:50 | 14:34:59 | 축퇴 감지 — span=0.00071 auc=0.518 out_max=0.3623 (기준 auc<0.53 and span<0.020, 기저율=0.3619 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:10m` | 12 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00033 auc=0.505 out_max=0.4377 (기준 auc<0.53 and span<0.020, 기저율=0.4375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 3 | 08:40:50 | 08:40:56 | 축퇴 감지 — span=0.00004 auc=0.485 out_max=0.3125 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:58 | 08:40:58 | 복원한 보정기가 축퇴 상태 — span=0.00502 auc=0.442 out_max=0.3779 (n=2811) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 11:21:00 | 11:21:00 | total=522ms raw_fetch=37ms pred_select=31ms pred_update=295ms pred_insert=0ms verified=3 |
| `Consolidator` | 1 | 15:40:09 | 15:40:09 | 구간 'STABLE_TREND' 최근 4일 풀링(n=284) 기대손익 -0.281pt (CI상단 -0.103pt) < 0 → 패널티 +0.04 (참고 정확도 25.4%) |
| `DriftAdjuster` | 1 | 15:40:09 | 15:40:09 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 20일) |

**채널** — `LEARNING`×2826

**컴포넌트 상위 15** — `LEARNING`×1219, `SGD`×370, `sigma`×358, `Bias⚠`×232, `Bias`×138, `Calibration:30m`×101, `Calibration:1m`×80, `MetaConf`×76, `OnlineLearner`×53, `ScalerWarmup`×41, `Calibration:3m`×36, `Calibration:5m`×36, `BiasReset`×33, `Calibration:10m`×22, `SHAP`×10

### `logs/20261007_HEALTH.log` — 5.3KB · 33행 · 최종 14:36:59

- 형식 평문 · 시각 인식 33행 · WARNING=16, INFO=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 388ms (표본 20분)
2026-10-07 09:32:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1064ms | quality=1.00 | cache_age=137s | exceptions_10m=0
2026-10-07 09:33:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=318ms | quality=1.00 | cache_age=12s | exceptions_10m=0
2026-10-07 09:44:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=290ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-10-07 09:45:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=308ms | quality=1.00 | cache_age=58s | exceptions_10m=0
  …
2026-10-07 13:48:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=347ms | quality=1.00 | cache_age=56s | exceptions_10m=3 | exc_tags=[SHAP]×2 [CB③-P4]×1
2026-10-07 13:50:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1184ms | quality=1.00 | cache_age=177s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
2026-10-07 13:51:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=334ms | quality=1.00 | cache_age=52s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
2026-10-07 14:36:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=337ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-07 14:36:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=291ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 16 | 09:32:01 | 14:36:00 | level=WARNING degraded=OFF | latency=1064ms | quality=1.00 | cache_age=137s | exceptions_10m=0 |

**채널** — `HEALTH`×33

**컴포넌트 상위 15** — `Health`×32, `HealthTrend`×1

### `logs/retrain_eod_20261007.log` — 22.8KB · 155행 · 최종 15:53:47

- 형식 평문 · 시각 인식 155행 · WARNING=12, INFO=143

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 15:50:03,510 [INFO] EOD_RETRAIN: =======================================================
2026-10-07 15:50:03,510 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-07 15:50:03,510 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-07 15:50:03,511 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-07 15:50:03,511 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-07 15:53:47,882 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0622 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-07 15:53:47,884 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1024 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-07 15:53:47,888 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-10-07 15:53:47,893 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-07 15:53:47,895 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:42 | 15:52:54 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1498봉(81%)이 현행 학습구간 (현행 cutoff=2026-10-06 14:38:00 ≥ 홀드아웃 시작=2026-09-29 13:01:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-06 14:38 >= holdout_start=2026-09-29 13:01 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-06 … |
| `RegularFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-07 | 최신 2026-10-06 · 기준 7거래일. 복구: python scripts/collect_regular_futures.py --from 20261007 --to 20261007 |
| `OptionFlowFresh` | 1 | 15:50:04 | 15:50:04 | 결손 5일 — 2026-09-28(최신봉 15:34), 2026-09-29(최신봉 15:34), 2026-09-30(최신봉 15:34), 2026-10-01(최신봉 15:34), 2026-10-02(최신봉 15:34) | 기준 6거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\… |
| `BackfillFilter` | 1 | 15:50:15 | 15:50:15 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 21241/44464 제외 (418차 결정 1) — 남은 23223행 |
| `UnitMismatch` | 1 | 15:50:15 | 15:50:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23223행 제외 (559차 P1'-2) — 남은 21777행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `Retrain` | 1 | 15:51:16 | 15:51:16 | 5m 교체 보류(EOD 모델가드) — acc 하락 0.0347 > 허용 0.0250 (new=0.3865 old=0.4211) — 참고용 저장, 구모델 유지 |
| `RegimeFingerprint` | 1 | 15:53:47 | 15:53:47 | 백필 0행 제외 — 필터가 무효일 수 있다. 19403행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×63, `SIGNAL`×55, `EOD_RETRAIN`×27, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×48, `Retrain`×22, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2, `P8`×2

### `logs/retrain_intraday_20260701_100700.log` — 4.6KB · 39행 · 최종 10:07:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-01 10:07:00,671 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 10:07:00,671 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-01 10:07:00,671 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-01 10:07:00,671 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ecddc60d.json
2026-07-01 10:07:02,992 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-01 10:07:36,589 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.37s | old_acc=nan)
2026-07-01 10:07:36,592 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-01 10:07:36,592 [INFO] LEARNING: [Retrain] 완료 | 33.6초 | 성공=6/6 호라이즌
2026-07-01 10:07:36,593 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 35.9s 데이터=20000행
2026-07-01 10:07:36,595 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ecddc60d.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 5 |
| 진입 등록(`[Position] 진입`) — **엔진** | 4 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 6  ※ 두 형식 중복 2건 접음 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 5 |
| 차단(`[차단]`) | 118 |
| 사이저 호출(`[Sizer]`) | 52 |

### 포지션 5건 · 승 3 (60%) · 합계 -0.38pt (-114,995원)  ※ 레그 9행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:20:01 | 엔진 | SHORT | 2 | 3m | 2 | +0.78 | +17,586 | 하드스톱(틱) |
| 10:26:01 | 엔진 | SHORT | 2 | 1m | 2 | +0.26 | -8,422 | 하드스톱(틱) |
| 10:48:00 (추정귀속) | 추정 | SHORT | 2 | — | 2 | +0.58 | +7,662 | 하드스톱(틱) |
| 11:08:01 | 엔진 | SHORT | 2 | 5m | 2 | -2.22 | -132,204 | 하드스톱(틱) |
| 11:19:01 | 엔진 | SHORT | 1 | 3m | 1 | +0.22 | +383 | 하드스톱(틱) |

**출처별 소계** — 엔진 4건 -122,657원 · 추정 1건 +7,662원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 1건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 9행** (부분청산 4 · 전량청산 5)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:20:09 | 부분 | 1 | +0.73 | +25,793 | TP1 부분청산 33% |
| 10:20:23 | 전량 | 1 | +0.05 | -8,207 | 하드스톱(틱) |
| 10:26:17 | 부분 | 1 | +0.33 | +5,789 | TP1 부분청산 33% |
| 10:29:03 | 전량 | 1 | -0.07 | -14,211 | 하드스톱(틱) |
| 10:48:40 | 부분 | 1 | +0.39 | +8,831 | TP1 부분청산 33% |
| 10:57:45 | 전량 | 1 | +0.19 | -1,169 | 하드스톱(틱) |
| 11:08:31 | 부분 | 1 | -0.77 | -49,102 | 손절1차 조기축소 |
| 11:11:12 | 전량 | 1 | -1.45 | -83,102 | 하드스톱(틱) |
| 11:19:17 | 전량 | 1 | +0.22 | +383 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×5, `TP1 부분청산 33%`×3, `손절1차 조기축소`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 5/5건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -114,995 = 포지션합 -114,995 → OK · `[청산 완료]` 5건 = 조립 포지션 5건 → OK

### CB③ 판정 가능 시간 — **235분 / 371분 (63%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 4건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:20:01 | SHORT | 2 | 1091.52 | 3m | neutral |
| 10:26:01 | SHORT | 2 | 1092.02 | 1m | neutral |
| 11:08:01 | SHORT | 2 | 1080.64 | 5m | mean-revert |
| 11:19:01 | SHORT | 1 | 1082.36 | 3m | mean-revert |

계약수 분포 — 1계약×1, 2계약×3

등급 분포 — `A급(원시C)`×4, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×2, `chas`×2, `cvd`×2, `prev`×2

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×14, **2계약**×15, **3계약**×23

실제 진입 계약수 — **1계약**×1, **2계약**×3

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×52

### 차단 사유 118건 · 64종

| 건수 | 사유 |
|---|---|
| 17 | 등급X — 미통과 항목: 2_confidence |
| 8 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 4 | ATR 0.85pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 3 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.88pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.82pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.79pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 2 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 2 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 1.00pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.74pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.65pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.68pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.73pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.81pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×17, `3_vwap`×7, `6_foreign`×7, `5_ofi`×2, `4_cvd`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×2
- `일간 리셋 완료` ×2
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-10-07 11:08:01, 현재 1…` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 47건 · 최대 23750ms · 5초 초과 10건

상위 — 23750ms, 18204ms, 13890ms, 8391ms, 7031ms, 6797ms, 6047ms, 6016ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 11:21:18 | 18204ms | 3186ms | **15018ms (82%)** |
| 11:22:00 | 6047ms | 3186ms | **2861ms (47%)** |
| 11:22:14 | 13890ms | 3186ms | **10704ms (77%)** |
| 11:24:05 | 5750ms | 1175ms | **4575ms (80%)** |
| 11:25:24 | 23750ms | 1175ms | **22575ms (95%)** |
| 11:27:06 | 6016ms | 875ms | **5141ms (85%)** |
| 11:28:07 | 6797ms | 875ms | **5922ms (87%)** |
| 12:55:05 | 5156ms | 727ms | **4429ms (86%)** |
| 15:35:10 | 7031ms | **미측정** | — |
| 15:46:16 | 8391ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261007_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:18 2026-10-07 15:40:18 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 41분/일 < 하한 60분 — 금일 83분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 371분
--- [CB] ×2(표본)
10:29:03 2026-10-07 10:29:03 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:08:31 2026-10-07 11:08:31 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
10:20:23 2026-10-07 10:20:23 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:22:23)
10:20:23 2026-10-07 10:20:23 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:22:23)
10:28:00 2026-10-07 10:28:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=302ms | quality=1.00 | cache_age=184s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
10:29:03 2026-10-07 10:29:03 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:32:03)
--- [SHAP] 슬로우 ×8(표본)
10:45:01 2026-10-07 10:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1018ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:02:01 2026-10-07 11:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 934ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:22:16 2026-10-07 11:22:16 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1376ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:30:02 2026-10-07 11:30:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1539ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:11 2026-10-07 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4016 band=INFO since_pipe_s=NA
08:52:24 2026-10-07 08:52:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3391 band=INFO since_pipe_s=NA
09:00:04 2026-10-07 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4969ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4969 band=INFO since_pipe_s=0.1
09:01:01 2026-10-07 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2016 band=INFO since_pipe_s=0.0
```

### `logs/20261007_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-07 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4046) | 앙상블 제외는 유지
09:44:00 2026-10-07 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4483) | 앙상블 제외는 유지
09:53:59 2026-10-07 09:53:59 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3546) | 앙상블 제외는 유지
10:45:00 2026-10-07 10:45:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3982) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:09 2026-10-07 15:40:09 [INFO] SYSTEM: [CB③계측] 조건성립 118분 / 판정가능 235분 / 파이프라인 371분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-07 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-07 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:10:00 2026-10-07 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:15:00 2026-10-07 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×3(표본)
11:11:12 2026-10-07 11:11:12 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-10-07 11:08:01, 현재 1회)
15:40:09 2026-10-07 15:40:09 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:09 2026-10-07 15:40:09 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:09 2026-10-07 15:40:09 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 4레그 / 4포지션 중 TP 이벤트 대응 3 · 단일계약 보호전환(설계) 1 · 미대응 0
--- [SchedForceExit] ×1(표본)
15:11:07 2026-10-07 15:11:07 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=1회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:22 2026-10-07 15:40:22 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-10-07 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:22 2026-10-07 15:40:22 [INFO] SYSTEM: [Notify] ℹ️ [15:40:22] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:22 2026-10-07 15:40:22 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 397초
15:40:22 2026-10-07 15:40:22 [INFO] SYSTEM: 자동 종료 예약 — 412초 후 Qt 이벤트 루프 종료
```

### `logs/20261007_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-07 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0420 dir=-1)
09:35:00 2026-10-07 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-10-07 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-10-07 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0420 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-10-07 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-10-07 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-10-07 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-10-07 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
--- 안전망 ×8(표본)
09:07:00 2026-10-07 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-07 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-07 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-07 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261007_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
08:40:49 2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
08:40:49 2026-10-07 08:40:49 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00081 auc=0.557 out_max=0.3115 (n=90) → 보정 재적용
08:40:49 2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3115 < conf_floor=0.3300 (span=0.00081 auc=0.557 out_max=0.3115, 기저율=0.3111 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

### `logs/20261007_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
10:28:00 2026-10-07 10:28:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=302ms | quality=1.00 | cache_age=184s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
10:29:00 2026-10-07 10:29:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=466ms | quality=1.00 | cache_age=53s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
11:02:01 2026-10-07 11:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1145ms | quality=1.00 | cache_age=16s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
11:03:00 2026-10-07 11:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=816ms | quality=1.00 | cache_age=75s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261007_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 2 | 10:06:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |
| 14:00 | 장중 후반 · 장중 재학습 | 6 | 13:56:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShad… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:09 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261007_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 23 | 08:52:24 [WARNING] _tick_header 간격 3391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3391 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 38 | 08:56:32 [WARNING] paintEvent slow 51.0ms | size=1955x1124 candles=12 grid=10.9 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers… |
| 10:00 | 장중 초반 | 5 | 09:54:07 [WARNING] paintEvent slow 63.5ms | size=1955x1124 candles=70 grid=26.8 spans=0.1 candles=2.7 dir=0.2 regime=3.4 markers… |
| 12:00 | 장중 중간점 | 127 | 11:54:01 [WARNING] paintEvent slow 98.6ms | size=1955x1124 candles=190 grid=33.8 spans=10.2 candles=8.4 dir=0.9 regime=4.4 marke… |
| 14:00 | 장중 후반 · 장중 재학습 | 92 | 13:54:01 [WARNING] paintEvent slow 139.2ms | size=1955x1124 candles=310 grid=39.2 spans=13.0 candles=16.7 dir=1.5 regime=8.5 mar… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 115 | 15:04:01 [WARNING] paintEvent slow 234.9ms | size=1955x1124 candles=380 grid=79.8 spans=24.3 candles=21.3 dir=1.7 regime=10.0 ma… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 112 | 15:12:08 [WARNING] paintEvent slow 107.1ms | size=1955x1124 candles=388 grid=27.3 spans=17.2 candles=14.8 dir=1.4 regime=6.2 mar… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 41 | 15:34:36 [WARNING] paintEvent slow 127.8ms | size=2952x1778 candles=410 grid=37.5 spans=17.3 candles=15.9 dir=1.4 regime=5.9 mar… |
| 15:47 | EOD 재학습(py310_64) 완료 | 17 | 15:43:41 [WARNING] paintEvent slow 98.6ms | size=1955x1124 candles=410 grid=24.7 spans=12.1 candles=17.1 dir=1.4 regime=5.0 mark… |

- 이 로그 생존구간: 08:41 ~ 15:47

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261007_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=12412 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 140 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 198 | 08:54:02 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 224 | 09:54:07 [INFO] rollover 연기 — 메인 펌프(BlockRequest 대기) 중 재진입 회피 (누적 87회, 재시도=호출부) |
| 12:00 | 장중 중간점 | 196 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 206 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 186 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 157 | 15:12:02 [INFO] alive ticks=110470 code=A056A close=1076.20 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 60 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 7 | 15:41:08 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=RISK_ON | 포지션=FLAT | 15:41:08 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261007_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 39 | 08:40:41 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.417 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 78 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 219 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 169 | 09:54:59 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m'] 중 미배포=['10m', '15m', '3m'] → flat_score=1.0 안전망 발동 (active_horizon… |
| 12:00 | 장중 중간점 | 106 | 11:54:00 [WARNING] 신뢰도 미달 34.6% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 136 | 13:54:01 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=6, group=short) | VWAP pos=-2.000 need >0 (LONG) bear_exh=0.00 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 61 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:09 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261006 | 15:47 | 로그 본문 |
| 20261005 | 09:41 | 로그 본문 |
| 20261003 | 18:32 | 로그 본문 |
| 20261002 | 19:02 | 로그 본문 |
| 20261001 | 15:47 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261007** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-07 (MW0601 665차 — 장중 점검)
### 증상/관측
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
차 장후)에는 같은 가설이 DB 직접 대조로 **기각**되고 실제 원인이 "`[Position] 진입]` 로그 줄 자체 미출력"으로 좁혀진 전례가 있다 — 원인이 매번 같다고 단정하지 않는다(G-3). 장중 라이브 DB 스캔 금지 규칙에 따라 오늘 이 건은 DB 대조를 하지 않았다. **O-i1으로 신규 등록**, 장후 제4부에서 `ensemble_decisions`·`trades` 대조로 원인 확정.
(5) O-p1(canary 노후판정 오판 여부, 장전 등록): `[CanaryShadow] ts=08:59 z경고=7개(08:55 대비 +3) — 재측정만, 재적합 없음` 1건 관측. 재측정만 하고 정책 변경(재적합) 없음이 로그 자체에 명시돼 있어 오판 증거 아님 — 보류 유지, 장후까지 계속 관찰.
(6) GBM 배치 재학습(STEP3) 오늘 0회 — `[ConstOut]` 트리거가 09:35·09:44·09:53·10:45 네 번 올라왔으나 전부 "BiasReset uniform fallback 구간" 사유로 억제됨(로그 명시). 정기 트리거(월요일 08:50/매월 1일 07:00) 대상일 아님. 0회=정상(483차 P2-J 정정 적용, "30분마다" 오독 없음).

### 원인

(1)은 수집기(`scripts/collect_evidence.py`)의 커버리지·결손 계산이 국면(phase)과 무관하게 분모를 "거래일 전체"로 고정하기 때문 — 장중(미래 미도래) 실행 시 필연적으로 발생하는 집계 특성, 코드 결함 아님. (3)은 Cybos COM 메시지 펌프 블로킹 계열로 원인 미특정(482차 F-3 섀도 계측 대상, 기존). (4)는 Chejan 레이스 vs 로그 누락 두 가설이 경합 중이며 오늘 사례만으로는 판별 불가 — DB 대조 필요.

### 결정

- (1) 신규 이상점/Fix 없음. §11 해석을 "미발생 구간 집계 특성"으로 명시 정정(이상점으로 올리지 않음) — 향후 장중 점검 세션도 같은 해석 적용. 수집기 분모 계산을 "09:00~수집 시각"으로 바꾸는 개선은 오늘 리포트 고도화 방안 1번으로 제안(코드 변경 승인 대기, 장중이라 미적용).
- (2)·(5)·(6) 기존 채널(sizing_inversion_watch[28], canary shadow O-p1, STEP3 정상 트리거 억제) 표본만 추가, 신규 Fix 없음.
- (3) 신규 Fix 없음 — 482차 F-3 섀도 채널에 표본만 누적(함정① — 이미 관찰 체계 있음).
- (4) O-i1 신규 등록, 장후 DB 대조로 원인 확정. 장중에는 라이브 DB 스캔 금지로 추가 조사 안 함.
- 장전 이상점 1-1·1-2·1-3 전부 지속(변화 없음), 확인 필요 663-4 판정 보류 유지(오늘도 git diff 타임아웃 0건으로 조건 미발생). 미처분 0건.

### Why

함정①(판정≠결정) 방지 — sizing_inversion_watch·482차 F-3·canary shadow·STEP3 트리거 전부 grep으로 기존 등록 확인 후 신규 아님으로 처리했다. (1)의 집계 특성 오탐도 2026-09-14/09-29 기록을 grep으로 먼저 확인한 뒤 같은 해석을 적용했다. O-i1만 grep으로 걸리는 "오늘 이 특정 건"에 대한 확정 등록이 없어 신규로 등록했다(패턴 자체는 기존 추적 대상이나 개별 사례 판정은 미완료).

### How to apply

해당 없음 — 장중 세션, 코드 변경 없음. 제안(고도화 방안 1번: `scripts/collect_evidence.py` 분모 계산 국면 분기)은 장후 이후 별도 세션에서 사용자 승인 하에 적용 검토.

### 검증

장후 점검에서 (4) O-i1을 `data/db/predictions.db`·`data/db/trades.db` 3원 대사로 확정할 것. (3)은 482차 F-3 2주 섀도 누적치에 오늘 23,750ms 표본 반영.

### 병행 세션

당일(2026-10-07) 커밋 0건 확인(장전 09:03 이후 변화 없음) — 이 세션이 만든 것도 0건. 딥다이브·특별조사 파일 없음. `.git/index.lock` 없음(수집기 자가점검 확인, 이 실행이 만들지 않음). `.git/index.lock.stale.5` 잔해 1건 지속(장전과 동일, 변화 없음). 읽기 전용 git은 전량 `--no-optional-locks`. 코드 변경 없음, 라이브 DB 스캔 없음(로그·git·설정만 사용).

산출물: `docs/정기점검/매일점검/MW0601-20261007-점검리포트.md`(장중 절 append), `docs/정기점검/매일점검/evidence_MW0601-20261007_intra.md`(수집기 자동 생성), `docs/정기점검/매일점검/_tmp_append_intra_20261007.md`(병합용 임시 파일, 기존 `_tmp_append_*` 관례와 동일 — 정리는 사용자 선택). 커밋 대기: 위 산출물 + `dev_memory/DECISION_LOG.md`·`NEXT_TODO.md`(경로 명시 add 필요 — `git add .` 금지).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버)
## 2026-10-05 (MW0601 657차 — 장전 점검, 휴장일)
## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)
## 2026-10-06 (MW0601 659차 — 장전 점검)
## 2026-10-06 (MW0601 660차 — 장중 점검)
## 2026-10-06 (MW0601 661차 — 장후 점검, 종합 완성본)
## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치)
## 2026-10-07 (MW0601 664차 — 장전 점검)
```

미완료 체크박스 **3030건** (끝에서 30건)
```
- [ ] **D-660-2 (오늘 장후, 관측)** 11:59 재학습 실패 이후 다음 재학습 트리거(이벤트 구동 또는 15:40 EOD)가 정상 성공하는지.
- [ ] **O-p1 (지속, 장후 판정 — 변경 없음)** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date` 공백 — 장중에 새로 볼 것 없음, 오늘 밤 장후에 그대로 판정.
- [ ] **O-u1 (지속, 변경 없음)** 부팅구간 access violation 3건·8관측일째 — 장중 데이터 추가 없음.
- [ ] **O-u5 (지속, 변경 없음)** 기형 파일.
- [ ] **648-2 (P2, 지속)** `.git/index.lock` 부스러기 — 10/6 장중분 1건(`index.lock.stale_20261006034328_6`) 추가.
- [ ] **F-6 (P1, 사용자 승인 후 적용)** `learning/batch_retrainer.py:2613` `logger.warning(f"[Retrain] DB 로드 오류: {e}")` → `repr(e)` + `exc_info=True`로 변경(위치 확정, grep으로 실물 확인 완료).
- [ ] **F-7 (P2, 사용자 승인 필요)** `run_microstructure_ab_backtest.py` — `grep -rn "guard_intraday"` 결과 미반영 확인(함정① 통과). 2026-08-27 제안 ⓐⓑⓒ 중 택1 필요 — 오늘까지 하루 집계 11회 비정상종료.
- [ ] **1-10 (P1, 신규)** 기형 파일 2건으로 증가(`…20261001_1006.md` 오늘 07:20 신규) — F-4 범위를 "이 저장소 정리"로 조정, 근본 원인(`peter-daily` 스킬 추정)은 이 저장소 밖 — 사용자가 해당 스킬 쪽 직접 확인 필요.
- [ ] **A-3 (P2, 신규)** 기형 파일 발생 경로 역추적 — `peter-daily` 계열 스킬의 `--out` 인자 절대/상대경로 처리부 확인. 표본 2건(10/2, 10/6), 확정 결론 금지.
- [ ] **O-u2-3차 (지속)** `.git/index.lock` 세 번째 재발 — 이번엔 `--reclaim` 없이 세션 내 자연 해소(16:23 `OK index.lock 없음`). F-1(수집기 git diff 타임아웃 개선) 여전히 미적용 — 다음 수집에서도 재발 가능.
- [ ] **O-u1 (지속, 다음 거래일)** 부팅구간 access violation — 10/6로 8관측일째, 정규장 중 재발 없음(1-2 변경 없음). 10/7(수) 9관측일째 재현 여부 확인.
- [ ] **O-u5 (지속→1-10으로 대체)** 기형 파일 — 1건→2건 증가. 이 항목은 1-10으로 추적을 넘긴다.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` 부스러기 — 장후 수집 중 8개 생성됐다가 16:2X 재확인 시 1개로 자연 감소. Windows에서 남은 1개 `--reclaim` 필요.
- [ ] **D-661-1 (10/7 수 장전, 관측)** 부팅구간 access violation 9관측일째 재현 여부.
- [ ] **D-661-2 (10/7 수 장후, 관측)** 진입후보 가능시간(O-t1, 오늘 26분·5일평균 37분·하한 60분) 다음날도 하한 미달 지속되는지.
- [ ] **D-661-3 (관측)** 기형 파일(1-10) 세 번째 발생 여부.
- [ ] **D-661-4 (관측)** `.git/index.lock` — F-1 미반영 상태에서 다음 수집도 재발하는지.
- [ ] **사용자 조치 대기 — Fix 적용 승인** F-1~F-7 전부 계획만 세워져 있고 미적용(장전·장중·장후 공통 규약 — 이 점검 세션은 코드를 변경하지 않음). 검토 후 별도 세션에서 적용 지시 필요.
- [ ] **663-1 (C, 사용자 승인 대기) F-5** `collection/cybos/api_connector.py:_pump_messages` 진입·반복 DEBUG 로그 + 재시작 로그에 직전 크래시 PID. 브로커 어댑터라 자동조치 범위 밖. 계획: 펌프 루프 반복 카운터·마지막 메시지 타입을 인스턴스 변수에 적재하고 faulthandler …
- [ ] **663-2 (C, 사용자 선택 대기) F-7** `scripts/run_microstructure_ab_backtest.py` 장중 실패(10/6 11회) — 08-27 제시 ⓐ장외 이동 ⓑ무거운 스크립트만 EOD ⓒ주기완화+점심 한정 중 택1. `guard_intraday` 미배선 확인(10/6).
- [ ] 663-3 A-1 대체: 부팅 access violation 위치 `PnlHistoryPanel._build` 7240–7250(`_cb_origin` 체크박스 루프) 직접 검토 — 로그 추가 불요(스택이 이미 특정).
- [ ] 663-4 F-1 라이브 확인: 10/7 장전 수집에서 diff 타임아웃 시 `second_diff_skipped`·인덱스락 미재발 여부.
- [ ] **O-p1 (신규, 오늘 장중·장후 판정)** `main.py:9049` 부근 canary 노후판정이 `p8_last_success_date` 공백 상태에서 오판하는지 — `[CanaryShadow]` 경고 패턴 확인
- [ ] **D-664-1 (10/8 수 장전, 관측)** 부팅구간 access violation 10관측일째 재현 여부
- [ ] **D-664-2 (관측)** `[SessionStateDrop]` 10/8 장전에도 재현되는지 — F-1(538-4) 미적용 지속 확인
- [ ] 663-4 F-1(663차) 라이브 검증 — 오늘 diff 타임아웃 0건으로 조건 미발생, 판정 보류 유지. 다음 타임아웃 발생일에 재확인.
- [ ] **사용자 조치 대기 — F-1(538-4) 승인 여부** session_state 마커 승계(`strategy/runtime/session_recovery_service.py:increment_session()`) 적용 승인 필요 (검토 ~5분).
- [ ] **O-i1 (2026-10-07 665차 신규)** 10:48:00 SHORT 2계약 포지션이 `[Position] 진입` 로그 없이 체결 기록으로만 조립됨(`(추정귀속)`, +7,662원) — Chejan 선행 체결 레이스 지문 후보 vs 로그 누락(2026-09-14/563차 전례는 로그 누락으로 확정, 매번 같다고 단정 금지). 장후 제…
- [ ] O-p1(MW0601 664차 이월, canary 노후판정 오판 여부) — 665차(장중) 확인: `[CanaryShadow] ts=08:59 z경고=7개(+3), 재측정만·재적합 없음` 1건 관측, 오판 증거 없음. 장후까지 보류 유지.
- [ ] (고도화 제안, 승인 대기) `scripts/collect_evidence.py`의 매분 루프 커버리지·`raw_candles` 결손 계산을 장중 실행 시 분모 "09:00~수집 시각"으로 국면 분기 — 2026-09-14·09-29·10-07(665차) 3회 반복된 "미발생 구간을 결손으로 오독" 패턴 근거. 코드 변경 승인 필요(C등급 아님…
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 — Fix 적용 승인** F-1~F-7 전부 계획만 세워져 있고 미적용(장전·장중·장후 공통 규약 — 이 점검 세션은 코드를 변경하지 않음). 검토 후 별도 세션에서 적용 지시 필요.

## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치)

- [x] 659-1(F-1) 수집기 첫 diff 실패 시 두 번째 변형 생략 — `d30a9cd`
- [x] 659-2(F-2) 문서 제목 — 워킹트리 손상분 `git restore` (커밋 없음)
- [x] 659-3(F-3) CLAUDE.md joblib 1.1.0 — `d30a9cd`
- [x] 659-4(F-4) 루트 기형파일 2건 → Peter\트윗원문 이동 + `.gitignore` — `d30a9cd`
- [x] 660-2(F-6) `[Retrain] DB 로드 오류` repr+exc_info — `d30a9cd`
- [x] A-3 기형파일 근본원인(peter_month_report 리눅스 샌드박스 경로) 차단 — `d30a9cd`
- [x] G-3 같은 날 런처 재시작 ≥2 §11 적신호 — `d30a9cd`
- [ ] **663-1 (C, 사용자 승인 대기) F-5** `collection/cybos/api_connector.py:_pump_messages` 진입·반복 DEBUG 로그 + 재시작 로그에 직전 크래시 PID. 브로커 어댑터라 자동조치 범위 밖. 계획: 펌프 루프 반복 카운터·마지막 메시지 타입을 인스턴스 변수에 적재하고 faulthandler 덤프 직전 읽을 수 있게(콜백 내부 dynamicCall·emit 없음 유지).
- [ ] **663-2 (C, 사용자 선택 대기) F-7** `scripts/run_microstructure_ab_backtest.py` 장중 실패(10/6 11회) — 08-27 제시 ⓐ장외 이동 ⓑ무거운 스크립트만 EOD ⓒ주기완화+점심 한정 중 택1. `guard_intraday` 미배선 확인(10/6).
- [ ] 663-3 A-1 대체: 부팅 access violation 위치 `PnlHistoryPanel._build` 7240–7250(`_cb_origin` 체크박스 루프) 직접 검토 — 로그 추가 불요(스택이 이미 특정).
- [ ] 663-4 F-1 라이브 확인: 10/7 장전 수집에서 diff 타임아웃 시 `second_diff_skipped`·인덱스락 미재발 여부.

## 2026-10-07 (MW0601 664차 — 장전 점검)

- [x] D-661-1 부팅구간 access violation 9관측일째 재현 여부 — **재현 확인으로 종결** (08:40:44, PID 12412, 동일 스택)
- [ ] **O-p1 (신규, 오늘 장중·장후 판정)** `main.py:9049` 부근 canary 노후판정이 `p8_last_success_date` 공백 상태에서 오판하는지 — `[CanaryShadow]` 경고 패턴 확인
- [ ] **D-664-1 (10/8 수 장전, 관측)** 부팅구간 access violation 10관측일째 재현 여부
- [ ] **D-664-2 (관측)** `[SessionStateDrop]` 10/8 장전에도 재현되는지 — F-1(538-4) 미적용 지속 확인
- [ ] 663-4 F-1(663차) 라이브 검증 — 오늘 diff 타임아웃 0건으로 조건 미발생, 판정 보류 유지. 다음 타임아웃 발생일에 재확인.
- [ ] **사용자 조치 대기 — F-1(538-4) 승인 여부** session_state 마커 승계(`strategy/runtime/session_recovery_service.py:increment_session()`) 적용 승인 필요 (검토 ~5분).

- [ ] **O-i1 (2026-10-07 665차 신규)** 10:48:00 SHORT 2계약 포지션이 `[Position] 진입` 로그 없이 체결 기록으로만 조립됨(`(추정귀속)`, +7,662원) — Chejan 선행 체결 레이스 지문 후보 vs 로그 누락(2026-09-14/563차 전례는 로그 누락으로 확정, 매번 같다고 단정 금지). 장후 제4부에서 `data/db/predictions.db`(`ensemble_decisions`)·`data/db/trades.db` 3원 대사로 원인 확정할 것.
- [ ] O-p1(MW0601 664차 이월, canary 노후판정 오판 여부) — 665차(장중) 확인: `[CanaryShadow] ts=08:59 z경고=7개(+3), 재측정만·재적합 없음` 1건 관측, 오판 증거 없음. 장후까지 보류 유지.
- [ ] (고도화 제안, 승인 대기) `scripts/collect_evidence.py`의 매분 루프 커버리지·`raw_candles` 결손 계산을 장중 실행 시 분모 "09:00~수집 시각"으로 국면 분기 — 2026-09-14·09-29·10-07(665차) 3회 반복된 "미발생 구간을 결손으로 오독" 패턴 근거. 코드 변경 승인 필요(C등급 아님, 점검 스크립트 자체 — 장후 세션에서 검토 가능).

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

### `data/heartbeat_MW0601_20261007.json` — 245B · 10-07 15:46:52
```json
{
 "pid": 12412,
 "written_at": "2026-10-07T15:46:52",
 "beat_epoch": 1791355608.1505735,
 "beat_age_sec": 4.0,
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

- 파일 최종 기록: **10-07 15:53:47**

| 키 | 값 | 수집 대상일(2026-10-07)과 일치 |
|---|---|---|
| `date` | 2026-10-07 | 예 |
| `p8_last_success_date` | 2026-10-07 | 예 |
| `eod_retrain_ok_date` | 2026-10-07 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-07 08:55:08 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-06) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-07 08:55:08 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-06) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:09** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 🔴 **이상** — 15:10 파이프라인 중단선 미작동 |
| `raw_candles` 당일 행수 | 385 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**
- 🔴 절단선 초과 1봉: 15:09

- 라이브 로그 대조: `logs/20261007_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 12412: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:44 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 12412 | 08:40:44 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 202개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261007-점검리포트.md` | 38.2KB | 10-07 12:36 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261007.md` | 17.4KB | 10-07 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_intra.md` | 80.5KB | 10-07 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_pre.md` | 60.1KB | 10-07 08:59 |
| `docs/정기점검/매일점검/MW0601-20261006-점검리포트.md` | 87.4KB | 10-06 17:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_post.md` | 86.9KB | 10-06 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_intra.md` | 76.7KB | 10-06 12:32 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_pre.md` | 63.0KB | 10-06 09:00 |

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

1. `logs/20261007_WARN.log`: ERROR 이상 3건
2. 포지션 5건 중 최종청산이 하드스톱·손절 계열 **5건(100%)** — 손절 준수율 확인 필요 (레그 9행)
3. 다레그 포지션 **4건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. 메인 스레드 정지 5초 초과 **10건** (최대 23750ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20261007_SYSTEM.log`: **ConstOut** 8건(표본)
7. `logs/20261007_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20261007_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20261007_LEARNING.log`: **축퇴** 8건(표본)
10. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
11. 미커밋 변경 75건 (실질 10건 · 코드 0건 · EOL 파생 0건)
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261007*.log` (Windows) / `grep 강제청산 logs/*20261007*.log`*