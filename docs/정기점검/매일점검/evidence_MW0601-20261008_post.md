# 미륵이 증거 다이제스트 — 2026-10-08 / POST

- 생성 2026-10-08 16:18:03 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01tj8psdtunkmnf9zsbtvnx5/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261008` · `2026-10-08` · `261008` · `1008`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **45개** 파일 · 45개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `261007_{DATE}_D.xls` | 1 | `data/db/option_hts/261007_1008_D.xls` | 480.4KB | 10-07 10:06 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261008.log` | 269B | 10-08 08:28 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261008.txt` | 28B | 10-08 15:43 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261008.txt` | 28B | 10-08 15:43 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261008.txt` | 233B | 10-08 15:53 |
| `force_flat_alert_{DATE}.txt` | 1 | `data/force_flat_alert_20261008.txt` | 490B | 10-08 15:42 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261008.log` | 1.8KB | 10-08 15:42 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261008.log` | 433B | 10-08 15:49 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261008.json` | 243B | 10-08 15:43 |
| `launcher_{DATE}_084001_6711.log` | 1 | `logs/Mireuk_batch/launcher_20261008_084001_6711.log` | 2.4MB | 10-08 15:39 |
| `launcher_{DATE}_154157_23850.log` | 1 | `logs/Mireuk_batch/launcher_20261008_154157_23850.log` | 25.0KB | 10-08 15:43 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261008.log` | 5.7KB | 10-08 14:38 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261008.log` | 109.9KB | 10-08 15:42 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261008.log` | 491B | 10-08 16:15 |
| `position_state.json.gen_{DATE}_140903` | 1 | `data/position_state.json.gen_20261008_140903` | 1.4KB | 10-08 14:03 |
| `position_state.json.gen_{DATE}_140904` | 1 | `data/position_state.json.gen_20261008_140904` | 1.5KB | 10-08 14:09 |
| `position_state.json.gen_{DATE}_141309` | 1 | `data/position_state.json.gen_20261008_141309` | 1.6KB | 10-08 14:13 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261008.log` | 40.3KB | 10-08 16:17 |
| `retrain_intraday_{DATE}_092102.log` | 1 | `logs/retrain_intraday_20261008_092102.log` | 5.7KB | 10-08 09:21 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261008.log` | 58.8KB | 10-08 15:58 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261008.txt` | 43B | 10-08 15:43 |
| `strategy_report_{DATE}_154340.txt` | 1 | `data/daily_reports/strategy_report_20261008_154340.txt` | 2.4KB | 10-08 15:43 |
| `{DATE}.eod_ids.json` | 1 | `data/peter_feed/_raw/2026-10-08.eod_ids.json` | 667B | 10-08 16:17 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-08.jsonl` | 5.9KB | 10-08 15:25 |
| `{DATE}_0908_D.xls` | 1 | `data/db/option_hts/261008_0908_D.xls` | 480.2KB | 10-08 09:08 |
| `{DATE}_0946_D.xls` | 1 | `data/db/option_hts/261008_0946_D.xls` | 480.3KB | 10-08 09:46 |
| `{DATE}_1230_D.xls` | 1 | `data/db/option_hts/261008_1230_D.xls` | 480.4KB | 10-08 12:30 |
| `{DATE}_1315_D.xls` | 1 | `data/db/option_hts/261008_1315_D.xls` | 480.4KB | 10-08 13:15 |
| `{DATE}_1348_D.xls` | 1 | `data/db/option_hts/261008_1348_D.xls` | 480.5KB | 10-08 13:48 |
| `{DATE}_1415_D.xls` | 1 | `data/db/option_hts/261008_1415_D.xls` | 480.5KB | 10-08 14:15 |
| `{DATE}_1452_D.xls` | 1 | `data/db/option_hts/261008_1452_D.xls` | 480.4KB | 10-08 14:52 |
| `{DATE}_DATA.log` | 1 | `logs/20261008_DATA.log` | 428.2KB | 10-08 15:19 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261008_DEBUG.log` | 234.7KB | 10-08 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261008_HEALTH.log` | 4.9KB | 10-08 14:45 |
| `{DATE}_HOGA.log` | 1 | `logs/20261008_HOGA.log` | 38.8MB | 10-08 15:21 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261008_LEARNING.log` | 454.2KB | 10-08 15:43 |
| `{DATE}_MICRO.log` | 1 | `logs/20261008_MICRO.log` | 764.8KB | 10-08 15:20 |
| `{DATE}_PROBE.log` | 1 | `logs/20261008_PROBE.log` | 91.8KB | 10-08 15:42 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261008_REGULAR_COLLECT.log` | 6.7KB | 10-08 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261008_SIGNAL.log` | 695.3KB | 10-08 15:43 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261008_SYSTEM.log` | 908.3KB | 10-08 15:43 |
| `{DATE}_TRADE.log` | 1 | `logs/20261008_TRADE.log` | 20.1KB | 10-08 15:43 |
| `{DATE}_WARN.log` | 1 | `logs/20261008_WARN.log` | 709.4KB | 10-08 15:43 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-08_tr.draft.txt` | 144B | 10-08 15:43 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-10-08_tr.txt` | 144B | 10-08 15:43 |

## 2. 코드·커밋 상태

- HEAD `780b2de` · 브랜치 `v9-dev` · 미커밋 101건 · 실질 변경 16건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 16 · 미추적 85 · 삭제 12 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261007.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json` … 외 4개
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 5.9초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261007.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260911.md
 M docs/정기점검/수익률향상_누적대장.md
?? "MAEKJEOM_LADDER.bat - 바로 가기.lnk"
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_20261002.md
?? dev_memory/_tmp_append_decisionlog_20261006_post.md
?? dev_memory/_tmp_append_decisionlog_20261007_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_pre.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_pre.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261008.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261012.md
?? docs/미륵이고도화3/옵션_전일보유_맥점되돌림_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자흐름_맥점관계_MW0601-20261002.md
?? docs/미륵이고도화3/외인선물순매수_수집현황_조사_MW0601-20261002.md
… 외 61건
```

**당일(2026-10-08) 커밋**
```
780b2de [MW0601] 668차 후속6: 피터2 진입 전량 증발 — kill_switch.is_active property 호출 수정
4b94f9f [MW0601] 668차 후속5: 피터2 수집 — X 검색 한도 소진·고아 스크립트·NEW 로그 오기 수정
```

**최근 커밋 12건**
```
780b2de [MW0601] 668차 후속6: 피터2 진입 전량 증발 — kill_switch.is_active property 호출 수정
4b94f9f [MW0601] 668차 후속5: 피터2 수집 — X 검색 한도 소진·고아 스크립트·NEW 로그 오기 수정
a0f179f [MW0601] 668차 후속4: 피터2 차트 갱신 메서드를 DashboardAdapter 에도 — 첫 기동 AttributeError
d5b183f [MW0601] 668차 후속3: 피터2 MW0602(dev) 독자 개발 가이드
2ecda7f [MW0601] 668차 후속2: 피터2 논의 정리 문서 — 장중 수집 개선 · 추종 거래
200432c [MW0601] 668차 후속: 피터2 「손절 2회 당일 정지」 해제 — PETER2_DAILY_STOP_LIMIT=0
c0933c8 [MW0601] 668차: 피터2 — 피터리 트윗 실시간 추종 모의매매(1계약) 신설
a995ac0 [MW0601] 667차 후속: 장후 자동조치 기록 — G-2 결과 · 663-3 조사
f9e54dd [MW0601] 667차 후속: 장후 자동조치 — G-2 (수집기 장중 분모 컷)
5cf61ee [MW0601] 662차 후속6: 사다리 「신동2 해설」 패널에 익일 계획 표시
eb4bad3 [MW0601] 662차 후속5: 신동2 예약작업(3단계) — 월–금 5개 작업 등록 · 헤드리스 Claude 래퍼 · 첫 실제 장후 실행
b9aa63b [MW0601] 662차 후속4: 신동2 라이브 — 스킬 · 이벤트 감지 · 사다리 「신동2 해설」 패널 · 재량(AI) 기록·채점
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

_본문 미열람(설정): `20261008_HOGA.log` 38.8MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261008.txt`** — 28B · 10-08 15:43:40
```
2026-10-08T15:43:40.739188
```

**`data/daily_close_started_20261008.txt`** — 28B · 10-08 15:43:27
```
2026-10-08T15:43:27.212039
```

**`data/daily_reports/strategy_report_20261008_154340.txt`** — 2.4KB · 10-08 15:43:40
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-08 15:43
========================================================
  버전    : v1.0  (94일차)
  판정    : OUTPERFORM
  Live(20일): Sh=3.18  MDD(자본대비)=1.6%
  당일      : WR=57.1%  PF=0.35
  롤링20일: 누적 +6666672원  Sh=3.18  MDD(자본대비)=1.6%  MDD(peak대비)=10.6%
  당일손익 : broker(gross) -152,000원  수수료 18,128원  net -170,128원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 미측정 (오늘 update_live 성공 0회 — 0.000이 아니다)
  PSI/feat: 미측정
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 -14,427원  승률 50.0%  합계 -288,545원
  등급별 순EV(30일): A=+97,388원(63건,승54%)  BROKER=+231,616원(2건,승100%)  MANUAL=+9,710원(7건,승57%)
  호라이즌별 순EV(30일): 1m=+2,297원(7건)  3m=+8,763원(36건)  5m=-62,093원(18건)  ?=+677,527원(11건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 52분  5일평균 44분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 26.4pt(5일평균 26.4pt)  1분평균변동 0.68pt(5일평균 0.59pt)
--------------------------------------------------------
  진입 퍼널(2026-10-08, 총 370분):
    FLAT 234 → conf미달 75 → CoherenceGate 10 → 게이트차단 43 → 후보 8 → 진입 7
    게이트별: 체크리스트항목미달=10  시가갭(OPEN_VOLATILE)=8  포지션보유중(평가생략)=8  콜드스타트/기타(σ미수집)=6  쿨다운=6  콜드스타트/기타(DataAnomalyGate)=3  콜드스타트/기타(조건부구간)=2
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 1건
      └ 상세: JointGateBlock=1
      └ JointGateBlock 1건 (무정보폴백 0건 = 0.0%) [표본 19건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261008.txt`** — 233B · 10-08 15:53:39
```
completed: 2026-10-08 15:53:39
rows: 19744
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 26.5
t_retrain_s: 188.9
t_total_s: 215.9
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/force_flat_alert_20261008.txt`** — 490B · 10-08 15:42:24
```
[ForceFlatGuard] 2026-10-08 15:42:24 WARNING
  라이브 프로세스 정지(포지션은 FLAT) — 오늘 실손해는 없으나 15:40 일일마감·EOD 체인이 실행되지 않는다
  · 하트비트: 파일 242s 전 기록 · 이벤트루프 나이 5s · pid=29516 · strikes=0
  · → 임계 180s 초과 — 라이브 프로세스가 멈춘 것으로 본다
  · 포지션: status=FLAT qty=0 · 최종갱신=2026-10-08T14:13:09.764826 (apply_exit_fill_final:하드스톱(틱))
```

**`data/peter_feed/2026-10-08_tr.draft.txt`** — 144B · 10-08 15:43:28
```
09:26 L 1072 / 09:56 X 1068 손절
09:58 L 1070 / 12:13 X 1064 손절
12:17 L 1063 / 12:38 X 1060 손절
13:02 L 1056 / 15:22 X 1052 손절
```

**`data/peter_feed/2026-10-08_tr.txt`** — 144B · 10-08 15:43:28
```
09:26 L 1072 / 09:56 X 1068 손절
09:58 L 1070 / 12:13 X 1064 손절
12:17 L 1063 / 12:38 X 1060 손절
13:02 L 1056 / 15:22 X 1052 손절
```

**`data/shutdown_normal_20261008.txt`** — 43B · 10-08 15:43:55
```
auto_shutdown
2026-10-08T15:43:55.762003
```

_다이제스트 대상 8/22개 (중요도순). 제외: `20261008_MICRO.log`, `20261008_DATA.log`, `20261008_PROBE.log`, `launcher_20261008_084001_6711.log`, `launcher_20261008_154157_23850.log`, `20261008_DEBUG.log`, `peter2_receiver_20261008.log`, `shindong2_20261008.log`_

### `logs/20261008_TRADE.log` — 20.1KB · 147행 · 최종 15:43:28

- 형식 평문 · 시각 인식 147행 · INFO=147

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:41:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:41:15 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:49:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:49:11 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:54:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-10-08 14:14:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,078,811) 기본리스크=1,500,000 신뢰도배수=0.8 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→2계약]
2026-10-08 14:15:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,078,811) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-10-08 15:03:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,078,811) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→2계약]
2026-10-08 15:42:53 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 15:43:28 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×147

**컴포넌트 상위 15** — `Chejan`×34, `Position`×30, `Sizer`×24, `주문요청`×16, `진입체크`×7, `체결진입`×7, `TickStop-S0C`×7, `청산 완료`×7, `ProfitGuard`×5, `TickTP1`×5, `체결진입보정`×2, `손절1차 조기축소`×1, `TP1 부분청산`×1, `JointGateBlock 차단`×1

### `logs/20261008_WARN.log` — 709.4KB · 3235행 · 최종 15:43:36

- 형식 평문 · 시각 인식 3176행 · CRITICAL=1, ERROR=15, WARNING=3160, PLAIN=59

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 359ms account=333044256
2026-10-08 08:41:22 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-08 08:41:22 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
├ gross 축  : 엔진 -152,000 vs 브로커 -152,000 → 기여 +0 (0%)
└ 수수료 축 : 엔진 18,128 vs 브로커 93,601 → 기여 +75,473 (100%, 배수 5.16)
⇒ 지배 축 = 수수료. scripts/commission_rate_recon.py --verify 로 실효 요율을 재산출할 것
2026-10-08 15:43:28 [WARNING] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 5레그 / 5포지션 중 TP 이벤트 대응 1 · 단일계약 보호전환(설계) 3 · 미대응 1 ⚠ 미대응 합계 -35,072원 (진입 10:54:06). 이 레그들은 라벨상 「TP1 뒤 트레일(이익 청산)」이지만 그 포지션에 TP가 난 적이 없다 — 손절률 분모·분자가 오염된다
2026-10-08 15:43:36 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 44분/일 < 하한 60분 — 금일 52분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `Peter2` | 14 | 09:25:54 | 13:03:00 | 폴링 예외 — 이번 주기 건너뜀: 'bool' object is not callable |
| CRITICAL | `SHS-EKS` | 1 | 09:05:01 | 09:05:01 | Early Kill Switch 발동 — 일시 관망 conf_max=39.4% bars=5 (delayed=0 policy=4 conf측정=1) → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |
| ERROR | `NetRecon` | 1 | 15:43:28 | 15:43:28 | 🔴 net 불일치 — 엔진 -170,128원 vs 브로커 -245,601원 (잔차 +75,473원, 허용 ±18,720) |

<details><summary>ERROR/Peter2 원문 2건</summary>

```
2026-10-08 09:25:54 [ERROR] SYSTEM: [Peter2] 폴링 예외 — 이번 주기 건너뜀: 'bool' object is not callable
2026-10-08 09:25:54 [ERROR] SYSTEM: [Peter2] 폴링 예외: 'bool' object is not callable
```

</details>

<details><summary>CRITICAL/SHS-EKS 원문 1건</summary>

```
2026-10-08 09:05:01 [CRITICAL] SYSTEM: [SHS-EKS] Early Kill Switch 발동 — 일시 관망 conf_max=39.4% bars=5 (delayed=0 policy=4 conf측정=1) → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)
```

</details>

<details><summary>ERROR/NetRecon 원문 1건</summary>

```
2026-10-08 15:43:28 [ERROR] SYSTEM: [NetRecon] 🔴 net 불일치 — 엔진 -170,128원 vs 브로커 -245,601원 (잔차 +75,473원, 허용 ±18,720)
```

</details>

**WARNING — 태그 46종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2519 | 08:52:21 | 15:43:06 | paintEvent slow 75.4ms | size=1955x1124 candles=3 grid=34.4 spans=0.0 candles=0.2 dir=0.0 regime=0.0 markers=0.0 axes=39.3 cross=0.0 | slow_cnt=1 total_cnt=11 overlay_cnt=46 |
| `LiveDBG` | 233 | 08:41:20 | 15:43:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 77 | 08:41:32 | 15:43:06 | 그리기 60.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 869x1001 |
| `ChejanFlow` | 34 | 10:54:02 | 14:13:09 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='2481' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=10:54:01.977' | positio… |
| `ChejanMatch` | 34 | 10:54:02 | 14:13:09 | order_no='2481' | pending='ENTRY:LONG qty=2 filled=0 order_no=2481 reason=진입 req_at=10:54:01.977' | pending_matched=True |
| `PendingOrder` | 32 | 10:54:01 | 14:13:09 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1071.56, 'reason': '진입', 'hint_source': '', 'atr': 1.3014, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `SHAP` | 21 | 11:25:01 | 15:03:02 | 슬로우 감지 943ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `CB③-P4` | 18 | 10:20:02 | 14:50:03 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=20.0%) |
| `Health` | 16 | 09:04:01 | 14:44:00 | level=WARNING degraded=OFF | latency=421ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS 08:50]×1 [LEVELS]×1 |
| `ScalerRefresh` | 15 | 09:14:01 | 14:55:00 | 5분 누적 수익률 -0.413% (임계 ±0.358%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ExitCooldown` | 14 | 10:58:03 | 14:13:09 | 하드스톱(틱) 후 2분 재진입 금지 (until 11:00:03) |
| `PipePerf` | 10 | 09:22:04 | 14:38:04 | total=3236ms | S0=2946ms S1=10ms S2=5ms S3=0ms S4=63ms S5=140ms S6=61ms S7=9ms S8=2ms |

**채널** — `SYSTEM`×3160, `HEALTH`×16

**컴포넌트 상위 15** — `ChartDBG`×2519, `LiveDBG`×233, `OptionFlowChart`×77, `-`×59, `ChejanFlow`×34, `ChejanMatch`×34, `PendingOrder`×32, `SHAP`×21, `CB③-P4`×18, `Health`×16, `Peter2`×15, `ScalerRefresh`×15, `ExitCooldown`×14, `PipePerf`×10, `CB⑤`×10

### `logs/20261008_SYSTEM.log` — 908.3KB · 6119행 · 최종 15:43:55

- 형식 평문 · 시각 인식 6085행 · INFO=6085, PLAIN=34

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:47 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=6040 | 행감지=30s all_threads=True
2026-10-08 08:40:48 [INFO] SYSTEM: [DBInit] 합계 0.55s | predictions=0.05s trades=0.25s daily_stats=0.01s shap=0.02s raw_data=0.16s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-08 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-08 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-08 08:40:48 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-08 15:43:40 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-10-08 15:43:41 [INFO] SYSTEM: [ShindongMail] 발송 완료 → smart1na@naver.com
2026-10-08 15:43:55 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-08 15:43:55 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-08 15:43:55 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6085

**컴포넌트 상위 15** — `CybosInvestorRaw`×1516, `PumpGuard`×710, `CybosRT-TICK`×458, `BAR-CLOSE`×388, `CVD-ANCHOR`×388, `CybosRT-ROLLOVER`×387, `TickUI`×379, `S6Detail`×370, `PipePerf`×370, `System`×115, `BalanceUI`×87, `OptionChain`×81, `OptionBook`×76, `MicroRegime`×69, `CybosEvent`×68

### `logs/20261008_SIGNAL.log` — 695.3KB · 5941행 · 최종 15:43:28

- 형식 평문 · 시각 인식 5941행 · WARNING=2794, INFO=3147

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-10-08 15:42:49 [INFO] SIGNAL: [TimeRouter] 월물 만기 당일 — 신뢰도↑ 사이즈×0.6
2026-10-08 15:42:56 [INFO] SIGNAL: [FeatureBuilder] tick_size 갱신: 0.0200 (spread_ticks 계산 기준)
2026-10-08 15:43:28 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-08 15:43:28 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-08 age=35m extreme=1188 refresh=41 grade_x=0 cb3=0
2026-10-08 15:43:28 [INFO] SIGNAL: [ModelHealth] date=2026-10-08 앙상블유효가동률=미측정 | 파이프라인 0분 | ConstOut 0회/0분 | WeightCollapse 0분 | 장중재학습 0회 | CB③ ready 0분/0분 (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1968 | 09:00:01 | 14:58:00 | 1m 'macro_vix' scale=0.0100 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 336 | 09:00:00 | 15:09:05 | ts=08:59 horizon=1m age=2m max_z=-9.53(opt_pcr_norm) extreme=3 adj=3 |
| `Model` | 240 | 09:00:00 | 15:09:05 | 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 94 | 09:18:00 | 15:09:05 | CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+0.427 need <0 (SHORT) bull_exh=0.00 |
| `WeightCollapse` | 82 | 09:07:01 | 15:07:06 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 60 | 08:45:22 | 08:58:02 | 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 9 | 11:14:00 | 15:06:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 4 | 10:29:01 | 10:44:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 1 | 11:09:00 | 11:09:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3610 < 필요 0.4530 (conf_floor=0.330, min_conf=0.453, span=0.0203, auc=0.398). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5941

**컴포넌트 상위 15** — `ScalerFloor`×2022, `SIGNAL`×740, `MetaGate`×473, `Ensemble`×379, `ScalerMonitor`×337, `ZeroDiag`×330, `FQAdj`×289, `Model`×270, `Checklist`×149, `ATR-Horizon`×121, `ScalerRefresh`×105, `ToxicityGate`×103, `WeightCollapse`×82, `차단`×80, `MicroRegime`×69

### `logs/20261008_LEARNING.log` — 454.2KB · 3752행 · 최종 15:43:28

- 형식 평문 · 시각 인식 3752행 · WARNING=593, INFO=3159

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-08 08:40:54 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00024 auc=0.533 out_max=0.3766 (n=85) → 보정 재적용
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00063 auc=0.507 out_max=0.3669 (기준 auc<0.53 and span<0.020, 기저율=0.3667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-08 15:43:28 [INFO] LEARNING: [DriftAdjuster] 표본 부족(n=0 < 15) — acc=50.0% 반영 스킵, alpha=0.01000 유지
2026-10-08 15:43:28 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-08 15:43:28 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-08 15:43:28 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-08 15:43:28 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 194 | 08:40:54 | 15:42:47 | 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:1m` | 172 | 08:40:54 | 15:42:47 | 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 73 | 08:40:54 | 15:42:47 | 축퇴 감지 — span=0.00025 auc=0.526 out_max=0.3911 (기준 auc<0.53 and span<0.020, 기저율=0.3909 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 66 | 08:40:54 | 15:42:46 | 축퇴 감지 — span=0.00017 auc=0.462 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 54 | 08:40:56 | 15:42:47 | 축퇴 감지 — span=0.00130 auc=0.529 out_max=0.4068 (기준 auc<0.53 and span<0.020, 기저율=0.4061 n=165) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:15m` | 22 | 08:40:55 | 15:42:47 | 축퇴 감지 — span=0.00087 auc=0.448 out_max=0.2754 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 9 | 08:41:05 | 15:42:47 | 복원한 보정기가 축퇴 상태 — span=0.01232 auc=0.468 out_max=0.4068 (n=3107) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 2 | 14:37:08 | 14:38:02 | total=570ms raw_fetch=2ms pred_select=3ms pred_update=34ms pred_insert=1ms verified=2 |
| `Consolidator` | 1 | 15:43:28 | 15:43:28 | 구간 'STABLE_TREND' 최근 3일 풀링(n=203) 기대손익 -0.237pt (CI상단 -0.028pt) < 0 → 패널티 +0.04 (참고 정확도 24.6%) |

**채널** — `LEARNING`×3752

**컴포넌트 상위 15** — `LEARNING`×1176, `Calibration:30m`×387, `SGD`×370, `sigma`×357, `Calibration:1m`×339, `Bias⚠`×240, `Bias`×145, `Calibration:3m`×138, `Calibration:5m`×127, `OnlineLearner`×115, `Calibration:10m`×104, `MetaConf`×77, `ScalerWarmup`×45, `Calibration:15m`×39, `BiasReset`×24

### `logs/20261008_HEALTH.log` — 4.9KB · 29행 · 최종 14:45:04

- 형식 평문 · 시각 인식 29행 · WARNING=16, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 09:04:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=421ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS 08:50]×1 [LEVELS]×1
2026-10-08 09:05:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=499ms | quality=1.00 | cache_age=56s | exceptions_10m=4 | exc_tags=[SHS-EKS]×2 [LEVELS 08:50]×1 [LEVELS]×1
2026-10-08 09:22:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3236ms | quality=1.00 | cache_age=155s | exceptions_10m=1 | exc_tags=[SHS-EKS]×1
2026-10-08 09:23:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=391ms | quality=1.00 | cache_age=27s | exceptions_10m=1 | exc_tags=[SHS-EKS]×1
2026-10-08 09:30:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 352ms (표본 20분)
  …
2026-10-08 14:37:09 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1637ms | quality=1.00 | cache_age=139s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-08 14:38:04 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=2022ms | quality=1.00 | cache_age=9s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-08 14:39:03 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=345ms | quality=1.00 | cache_age=68s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-08 14:44:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=345ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-10-08 14:45:04 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=302ms | quality=1.00 | cache_age=62s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 16 | 09:04:01 | 14:44:00 | level=WARNING degraded=OFF | latency=421ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS 08:50]×1 [LEVELS]×1 |

**채널** — `HEALTH`×29

**컴포넌트 상위 15** — `Health`×28, `HealthTrend`×1

### `logs/retrain_eod_20261008.log` — 40.3KB · 325행 · 최종 16:17:45

- 형식 평문 · 시각 인식 194행 · WARNING=27, INFO=167, PLAIN=131

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 15:50:03,118 [INFO] EOD_RETRAIN: =======================================================
2026-10-08 15:50:03,119 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-08 15:50:03,119 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-08 15:50:03,119 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-08 15:50:03,119 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
10m    성공         3966   1.3070        0.108        0.116
15m    성공         2559   1.6004        0.101        0.110
30m    성공        21027   1.5346        0.092        0.092
참고: 커버리지<q10은 이상적으로 ~0.10, 커버리지>q90은 ~0.10 근처여야 함
(실측이 크게 벗어나면 분위 추정이 편향됐다는 뜻 — GBR_PARAMS 조정 검토)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:42 | 15:52:46 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-10-08 08:46:00까지)인데 acc.txt=0.4711는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:42 | 15:52:46 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1510봉(82%)이 현행 학습구간 (현행 cutoff=2026-10-08 08:46:00 ≥ 홀드아웃 시작=2026-09-30 12:51:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-08 08:46 >= holdout_start=2026-09-30 12:51 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-1… |
| `UnitMismatch` | 4 | 15:50:14 | 16:11:19 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23599행 제외 (559차 P1'-2) — 남은 22153행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `BackfillFilter` | 2 | 15:50:14 | 16:11:22 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 20860/44459 제외 (418차 결정 1) — 남은 23599행 |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-08 | 최신 2026-10-07 · 기준 8거래일. 복구: python scripts/collect_regular_futures.py --from 20261008 --to 20261008 |
| `OptionFlowFresh` | 1 | 15:50:03 | 15:50:03 | 결손 5일 — 2026-09-28(최신봉 15:34), 2026-09-29(최신봉 15:34), 2026-09-30(최신봉 15:34), 2026-10-01(최신봉 15:34), 2026-10-02(최신봉 15:34) | 기준 7거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\… |
| `RegimeFingerprint` | 1 | 15:53:39 | 15:53:39 | 백필 0행 제외 — 필터가 무효일 수 있다. 19744행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×74, `SIGNAL`×55, `EOD_RETRAIN`×39, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×130, `ScalerFloor`×48, `Retrain`×21, `EOD_RETRAIN`×15, `GuardGhost`×12, `검증 캠페인`×11, `RF`×9, `ShadowTB`×8, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6

### `logs/retrain_intraday_20261008_092102.log` — 5.7KB · 43행 · 최종 09:21:46

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 09:21:02,886 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-08 09:21:02,887 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-08 09:21:02,887 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-08 09:21:02,887 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-08 09:21:02,888 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_4627d1d6.json
  …
2026-10-08 09:21:46,157 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-08 09:21:46,158 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-08 09:21:46,158 [INFO] LEARNING: [Retrain] 완료 | 39.9초 | 성공=6/6 호라이즌
2026-10-08 09:21:46,159 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 43.3s 데이터=4800행
2026-10-08 09:21:46,161 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_4627d1d6.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 09:21:16 | 09:21:16 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 21219/44470 제외 (418차 결정 1) — 남은 23251행 |
| `UnitMismatch` | 1 | 09:21:16 | 09:21:16 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23251행 제외 (559차 P1'-2) — 남은 21805행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 7 |
| 진입 등록(`[Position] 진입`) — **엔진** | 7 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 7 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 7 |
| 차단(`[차단]`) | 80 |
| 사이저 호출(`[Sizer]`) | 24 |

### 포지션 7건 · 승 4 (57%) · 합계 -3.04pt (-170,128원)  ※ 레그 9행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:54:02 | 엔진 | LONG | 2 | 5m | 2 | -0.62 | -35,072 | 하드스톱(틱) |
| 13:02:00 | 엔진 | SHORT | 2 | 3m | 2 | +0.56 | +24,006 | 하드스톱(틱) |
| 13:32:03 | 엔진 | SHORT | 1 | 3m | 1 | -2.20 | -112,005 | 하드스톱(틱) |
| 13:41:03 | 엔진 | SHORT | 1 | 3m | 1 | -1.94 | -99,008 | 하드스톱(틱) |
| 13:59:03 | 엔진 | SHORT | 1 | 3m | 1 | +0.34 | +14,984 | 하드스톱(틱) |
| 14:03:01 | 엔진 | SHORT | 1 | 1m | 1 | +0.56 | +25,985 | 하드스톱(틱) |
| 14:09:03 | 엔진 | SHORT | 1 | 3m | 1 | +0.26 | +10,982 | 하드스톱(틱) |

**청산 레그 9행** (부분청산 2 · 전량청산 7)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:54:19 | 부분 | 1 | -0.78 | -41,036 | 손절1차 조기축소 |
| 10:58:03 | 전량 | 1 | +0.16 | +5,964 | 하드스톱(틱) |
| 13:02:15 | 부분 | 1 | +0.72 | +34,003 | TP1 부분청산 33% |
| 13:02:50 | 전량 | 1 | -0.16 | -9,997 | 하드스톱(틱) |
| 13:36:09 | 전량 | 1 | -2.20 | -112,005 | 하드스톱(틱) |
| 13:52:14 | 전량 | 1 | -1.94 | -99,008 | 하드스톱(틱) |
| 14:00:08 | 전량 | 1 | +0.34 | +14,984 | 하드스톱(틱) |
| 14:03:21 | 전량 | 1 | +0.56 | +25,985 | 하드스톱(틱) |
| 14:13:09 | 전량 | 1 | +0.26 | +10,982 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×7, `손절1차 조기축소`×1, `TP1 부분청산 33%`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 7/7건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -170,128 = 포지션합 -170,128 → OK · `[청산 완료]` 7건 = 조립 포지션 7건 → OK

### CB③ 판정 가능 시간 — **0분 / 0분 (—)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 7건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:54:02 | LONG | 2 | 1071.56 | 5m | mean-revert |
| 13:02:00 | SHORT | 2 | 1051.0 | 3m | neutral |
| 13:32:03 | SHORT | 1 | 1055.02 | 3m | trend |
| 13:41:03 | SHORT | 1 | 1057.26 | 3m | trend |
| 13:59:03 | SHORT | 1 | 1060.92 | 3m | trend |
| 14:03:01 | SHORT | 1 | 1060.18 | 1m | trend |
| 14:09:03 | SHORT | 1 | 1062.56 | 3m | neutral |

계약수 분포 — 1계약×5, 2계약×2

등급 분포 — `A급(원시C)`×7

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×2, `coun`×2, `ofi`×1, `fore`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×14, **2계약**×3, **3계약**×7

실제 진입 계약수 — **1계약**×5, **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×21, `conf=0.8 regime=0.8 safe=1.00`×3

### 차단 사유 80건 · 37종

| 건수 | 사유 |
|---|---|
| 36 | 등급X — 미통과 항목: 2_confidence |
| 5 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 2 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 청산 후 쿨다운 — 68초 후 재진입 가능 |
| 2 | 청산 후 쿨다운 — 8초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.8pt > ATR×5.0=8.9pt (시가=1075.20 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.7pt > ATR×5.0=8.2pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.5pt > ATR×5.0=8.0pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.4pt > ATR×5.0=7.8pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.2pt > ATR×5.0=7.7pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.0pt > ATR×5.0=7.9pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.2pt > ATR×5.0=7.8pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.7pt > ATR×5.0=8.7pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.8pt > ATR×5.0=9.1pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.5pt > ATR×5.0=9.1pt (시가=1075.20 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.2pt > ATR×5.0=8.5pt (시가=1075.20 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×36, `3_vwap`×10, `7_prev_bar`×7, `5_ofi`×6, `4_cvd`×5, `6_foreign`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 6건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×4
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 23건 · 최대 6437ms · 5초 초과 2건

상위 — 6437ms, 5500ms, 4875ms, 4641ms, 4344ms, 4079ms, 3813ms, 3750ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:41:26 | 6437ms | **미측정** | — |
| 14:38:05 | 5500ms | 2022ms | **3478ms (63%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261008_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:43:36 2026-10-08 15:43:36 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 44분/일 < 하한 60분 — 금일 52분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- PSI ×1(표본)
15:43:27 2026-10-08 15:43:27 [WARNING] SYSTEM: [RegimeFingerprint] 🔴 오늘 PSI 측정 성공 0회 — 하루 종일 미측정이다(0.000/CLEAR 가 아니다). 기준선 키 불일치·라이브 표본 미달·update_live 예외 중 하나다. `[RegimeFingerprint] 기준선 키 불일치` WARNING 이 기동 로그에 있는지 먼저 확인할 것
--- Traceback ×7(표본)
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
--- [CB] ×4(표본)
10:54:19 2026-10-08 10:54:19 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:02:50 2026-10-08 13:02:50 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:36:09 2026-10-08 13:36:09 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:52:14 2026-10-08 13:52:14 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
10:58:03 2026-10-08 10:58:03 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:00:03)
10:58:03 2026-10-08 10:58:03 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:00:03)
13:02:50 2026-10-08 13:02:50 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:05:50)
13:02:50 2026-10-08 13:02:50 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:05:50)
--- [ExitStageRecon] ×1(표본)
15:43:28 2026-10-08 15:43:28 [WARNING] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 5레그 / 5포지션 중 TP 이벤트 대응 1 · 단일계약 보호전환(설계) 3 · 미대응 1 ⚠ 미대응 합계 -35,072원 (진입 10:54:06). 이 레그들은 라벨상 「TP1 뒤 트레일(이익 청산)」이지만 그 포지션에 TP가 난 적이 없다 — 손절률 분모·…
--- [SHAP] 슬로우 ×8(표본)
11:25:01 2026-10-08 11:25:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 943ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:40:02 2026-10-08 11:40:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1028ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:51:01 2026-10-08 11:51:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 927ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:11:02 2026-10-08 12:11:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 924ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- degraded=ON ×1(표본)
14:38:04 2026-10-08 14:38:04 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=2022ms | quality=1.00 | cache_age=9s | exceptions_10m=1 | exc_tags=[SHAP]×1
--- 메인 스레드 블로킹 ×8(표본)
08:41:26 2026-10-08 08:41:26 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6437 band=WARN since_pipe_s=NA
08:49:19 2026-10-08 08:49:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4875 band=INFO since_pipe_s=NA
08:49:30 2026-10-08 08:49:30 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2797 band=INFO since_pipe_s=NA
08:55:11 2026-10-08 08:55:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3813ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3813 band=INFO since_pipe_s=NA
```

### `logs/20261008_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:22:04 2026-10-08 09:22:04 [INFO] SYSTEM: [DynMC] ConstOut 고착 conf 제외: [0.85] → 407건 제거 (잔여 2165건)
11:14:00 2026-10-08 11:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.7367) | 앙상블 제외는 유지
11:23:00 2026-10-08 11:23:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4075) | 앙상블 제외는 유지
12:05:02 2026-10-08 12:05:02 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3861) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:43:28 2026-10-08 15:43:28 [INFO] SYSTEM: [CB③계측] 조건성립 0분 / 판정가능 0분 / 파이프라인 0분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-08 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-08 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:10:00 2026-10-08 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:16:00 2026-10-08 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
15:43:28 2026-10-08 15:43:28 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:43:28 2026-10-08 15:43:28 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:07 2026-10-08 15:11:07 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:43:40 2026-10-08 15:43:40 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:43:55 2026-10-08 15:43:55 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×5(표본)
15:43:40 2026-10-08 15:43:40 [INFO] SYSTEM: [Notify] ℹ️ [15:43:40] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:43:40 2026-10-08 15:43:40 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:43:55 2026-10-08 15:43:55 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20261008_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
11:09:00 2026-10-08 11:09:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3610 < 필요 0.4530 (conf_floor=0.330, min_conf=0.453, span=0.0203, auc=0.398). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
11:14:00 2026-10-08 11:14:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1860 dir=+0)
11:14:00 2026-10-08 11:14:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
11:14:00 2026-10-08 11:14:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
11:15:00 2026-10-08 11:15:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1840 dir=+0)
--- WeightCollapse ×8(표본)
09:07:01 2026-10-08 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:01 2026-10-08 09:10:01 [INFO] SIGNAL: [Ensemble] dir=-1 conf=38.2% grade=C regime=NEUTRAL [WeightCollapse]
09:13:01 2026-10-08 09:13:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-08 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
--- 안전망 ×8(표본)
09:07:01 2026-10-08 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:01 2026-10-08 09:10:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:01 2026-10-08 09:13:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-08 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261008_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:54 2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:54 2026-10-08 08:40:54 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00024 auc=0.533 out_max=0.3766 (n=85) → 보정 재적용
08:40:54 2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00063 auc=0.507 out_max=0.3669 (기준 auc<0.53 and span<0.020, 기저율=0.3667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:54 2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

### `logs/20261008_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
13:06:03 2026-10-08 13:06:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1196ms | quality=1.00 | cache_age=7s | exceptions_10m=5 | exc_tags=[Peter2]×2 [CB③-P4]×1 [ExitCooldown]×1 외 1종
13:07:00 2026-10-08 13:07:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=260ms | quality=1.00 | cache_age=64s | exceptions_10m=5 | exc_tags=[Peter2]×2 [CB③-P4]×1 [ExitCooldown]×1 외 1종
13:12:00 2026-10-08 13:12:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=298ms | quality=1.00 | cache_age=181s | exceptions_10m=4 | exc_tags=[CB③-P4]×1 [ExitCooldown]×1 [Peter2]×1 외 1종
13:58:01 2026-10-08 13:58:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=278ms | quality=1.00 | cache_age=183s | exceptions_10m=4 | exc_tags=[SHAP]×2 [CB③-P4]×1 [ExitCooldown]×1
--- degraded=ON ×1(표본)
14:38:04 2026-10-08 14:38:04 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=2022ms | quality=1.00 | cache_age=9s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

### `logs/retrain_eod_20261008.log`
```
--- ConstOut ×1(표본)
??:??:?? | `[51]` | `아직 미확인` | ConstOut 호라이즌 건강도 |
--- 축퇴 ×1(표본)
??:??:?? | `[45]` | `cal_guard_flap_watch` | 축퇴 가드 플래핑 (게이지) |
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261008_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:05 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 4 | 08:49:05 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:54:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 3 | 10:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,324,412) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShad… |
| 14:00 | 장중 후반 · 장중 재학습 | 33 | 13:59:03 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,052,034) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:42:53 [INFO] 설정 업데이트 완료 |
| 15:47 | EOD 재학습(py310_64) 완료 | 2 | 15:42:53 [INFO] 설정 업데이트 완료 |

- 이 로그 생존구간: 08:41 ~ 15:43

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261008_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 22 | 08:41:20 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 34 | 08:49:14 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 36 | 08:54:42 [WARNING] 기동 시점 결손 6봉 / 검사창 08:45~08:53 (분그리드 기준) — 08:48, 08:49, 08:50, 08:51, 08:52, 08:53 | session_bars 보존 여부는 15:4… |
| 10:00 | 장중 초반 | 124 | 09:54:01 [WARNING] paintEvent slow 129.0ms | size=1955x1124 candles=63 grid=40.2 spans=0.5 candles=17.0 dir=0.3 regime=16.1 mark… |
| 12:00 | 장중 중간점 | 87 | 11:54:00 [WARNING] paintEvent slow 92.3ms | size=1955x1124 candles=183 grid=23.2 spans=6.3 candles=14.5 dir=0.7 regime=6.9 marke… |
| 14:00 | 장중 후반 · 장중 재학습 | 167 | 13:54:02 [WARNING] paintEvent slow 79.1ms | size=1955x1104 candles=303 grid=21.0 spans=1.3 candles=14.9 dir=1.3 regime=10.3 mark… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 85 | 15:04:00 [WARNING] paintEvent slow 85.1ms | size=1955x1104 candles=373 grid=24.1 spans=1.4 candles=17.5 dir=1.8 regime=8.0 marke… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 98 | 15:12:04 [WARNING] paintEvent slow 78.3ms | size=1955x1104 candles=381 grid=14.8 spans=1.5 candles=17.1 dir=1.4 regime=4.1 marke… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 21 | 15:35:01 [WARNING] ScalerMonitorPanel.refresh slow 532ms |
| 15:47 | EOD 재학습(py310_64) 완료 | 19 | 15:42:33 [WARNING] 기동 시점 결손 7봉 / 검사창 08:45~15:08 (분그리드 기준) — 08:48, 08:49, 08:50, 08:51, 08:52, 08:53, 08:54 | session_bars 보존 여… |

- 이 로그 생존구간: 08:41 ~ 15:43

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261008_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:47 [INFO] 활성화 | file=logs\crash_fault.log PID=6040 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 214 | 08:49:05 [INFO] 기동 사전 학습 완료: 18000건 (극단성보정 live={'30m': True}) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 234 | 08:54:15 [INFO] 대기 중 | 장 개시 대기 — 09:00 분봉 파이프라인 시작 예정 | 레짐=NEUTRAL | 포지션=FLAT | 08:54:15 |
| 10:00 | 장중 초반 | 203 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 186 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 254 | 13:54:02 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 165 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 95 | 15:12:04 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 101 | 15:35:07 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:35:07 |
| 15:47 | EOD 재학습(py310_64) 완료 | 100 | 15:42:33 [INFO] 활성화 | file=logs\crash_fault.log PID=17076 | 행감지=30s all_threads=True |

- 이 로그 생존구간: 08:40 ~ 15:43

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261008_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:45:22 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 232 | 08:55:38 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 330 | 08:55:38 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 182 | 09:56:01 [WARNING] 신뢰도 미달 33.4% < 38.1% → 강제 X등급 |
| 12:00 | 장중 중간점 | 218 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=3m max_z=+7.25(ofi_reversal_speed) extreme=2 adj=2 |
| 14:00 | 장중 후반 · 장중 재학습 | 111 | 13:56:02 [WARNING] 신뢰도 미달 36.2% < 44.9% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 75 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 21 | 15:42:30 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.423 |
| 15:47 | EOD 재학습(py310_64) 완료 | 21 | 15:42:30 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.423 |

- 이 로그 생존구간: 08:40 ~ 15:43

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261007 | 20:26 | 로그 본문 |
| 20261006 | 15:47 | 로그 본문 |
| 20261005 | 09:41 | 로그 본문 |
| 20261003 | 18:32 | 로그 본문 |
| 20261002 | 19:02 | 로그 본문 |
| **중앙값** | **18:32** | 기준선 |
| **오늘 20261008** | **15:43** | 로그 본문 |

- 델타 **-169분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-08 (MW0601 670차 — 장중 점검)
### 증상/확인 대상
### 발견
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 결함)·관측 O-p1을 이월 처리.
- 피터2(668차 신설, 트위터 실시간 추종 모의매매) 폴링에서 `TypeError: 'bool' object is not callable`이 `logs/20261008_WARN.log`에 09:25:54·09:57:58·09:58:24·12:17:24·12:18:24 5회 발생 — 확인 대상으로 등록.

### 발견
- 매분 루프 09:00~12:27 208/208분(100.0%), 10분 이상 공백 0건 — 정상.
- EKS 09:05:01 발동(GAP_OPEN 5봉 최대 conf 39.4%) → 09:21:02 해제 + 장중 경량 재학습(43.3초, 6/6 호라이즌 성공). 설계대로.
- 진입 1건(10:54:02 LONG 2계약 @1071.56, 5m, Hurst mean-revert, 체크리스트 9/11 통과 C→A 상향, vwap 통과) → 부분청산(10:54:19, 손절1차 조기축소, -41,036원) → 전량청산(10:58:03, 하드스톱(틱), +5,964원). 포지션 합계 -0.62pt(-35,072원), 승0/1.
- `[GradeEVGuard](섀도) A→B 강등 조건 충족(미적용): A등급 최근30일 n=52 평균순EV=-11,846원` — 2026-07-22(366차) 신설, 2026-08-01 검증캠페인[13] "부결 — 활성화하지 않음" 그대로 작동. 재발견 아님(함정① 확인).
- **신규**: `main.py:3991` `_peter2_execute()`의 `if self.kill_switch.is_active():` — `safety/kill_switch.py`의 `KillSwitch.is_active`는 `@property`(소괄호 없이 값 반환)인데 피터2 코드만 함수처럼 호출(`is_active()`)해 `TypeError`. `grep -rn "kill_switch\.is_active" --include="*.py" .` 결과 이 한 줄뿐. DECISION_LOG·NEXT_TODO 전수 그레핑 결과 기존 기록 없음 — 신규 결함.
- 사이저 출력 최대 3계약 vs 실제 진입 최대 2계약 — 기존 `sizing_inversion_watch`(실전 전환 기준⑧) 관측치 추가, 신규 아님.
- 메인 스레드 블로킹 9건·최대 6437ms(08:41:26)·5초 초과 1건 — 482차 F-3 섀도 계측 기존 채널, 신규 아님.
- SHAP 슬로우 5건(924~1215ms, 임계 900ms) — 정상 완충(다음 5분 건너뜀), degraded=ON 0건, Brier과신 0건.
- 1-2(수집기 커밋판정 UTC 결함) 장중 수집에서도 재확인 — "당일 커밋 없음" 오보, 실제 08:51:15 `a0f179f` 1건. 판정에는 영향 없음(이 세션이 `--since +0900`으로 직접 재확인).

### 결정
- 1-3(피터2 kill_switch 오류)을 P1 신규로 등록. Fix(F-12)는 `main.py:3991` 한 글자 수정(`is_active()` → `is_active`), **장후 사용자 승인 후 적용** — 장중 라이브 프로세스 운영 중이라 지금 적용하지 않는다.
- O-p1(개장전 2단계 재시작 재현 관측)은 오늘 장중 데이터로 판정 불가 — 다음 거래일(10/9) 장전으로 이월.
- 1-1·1-2는 변화 없이 지속(원인조사·Fix 승인 모두 장후로 이월, 기존 계획 유지).

### Why
- 피터2는 모의매매(1계약)이고 kill_switch 체크가 fail-safe 방향(예외 시 해당 주기 스킵 = 신규 주문 안 나감)이라 실거래 리스크는 없다고 판단 — 라이브 중 즉시 수정보다 장후 일괄 적용이 안전.
- GradeEVGuard·sizing_inversion_watch·메인스레드블로킹·SHAP슬로우는 모두 기존에 결정·배선된 섀도/관측 채널이 그대로 작동한 것이라 재보고하지 않음(함정① — 그레핑으로 확인 후 판단).

### How to apply
- `main.py:3991`: `if self.kill_switch.is_active():` → `if self.kill_switch.is_active:`. 리포 전체에서 이 속성을 `()` 호출식으로 쓰는 곳이 이 한 줄뿐(그레핑 확인)이라 다른 호출부 회귀 없음.
- 적용 후 다음 거래일 장전부터 `logs/<날짜>_WARN.log`에서 동일 `TypeError` 재현 여부로 검증.

### 검증
- 라이브 미검증(장후 적용 예정) — 검증 기한: 다음 거래일(10/9) 장전 점검.

### 병행 세션
- `git --no-optional-locks log --since="2026-10-08 00:00:00 +0900"` 재확인 — 장전 이후 추가 커밋 0건(08:51:15 `a0f179f` 1건뿐, 669차가 이미 확인한 것). 별도 딥다이브·특별조사 파일 없음(`ls -lt docs/정기점검/매일점검/` 확인). `.git/index.lock`·`.git/HEAD.lock` 둘 다 없음, `git_lock_guard.py --check` OK.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-06 (MW0601 661차 — 장후 점검, 종합 완성본)
## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치)
## 2026-10-07 (MW0601 664차 — 장전 점검)
## 2026-10-07 (MW0601 666차 — 장후 점검, 종합 완성본)
## 2026-10-07 (MW0601 667차 — 666차 후속 장후 자동조치)
## 2026-10-07 (MW0601 668차 — 피터2 실시간 추종 신설)
## 2026-10-08 (MW0601 669차 — 장전 점검)
## 2026-10-08 (MW0601 670차 — 장중 점검)
```

미완료 체크박스 **3053건** (끝에서 30건)
```
- [ ] **D-664-1 (10/8 수 장전, 관측)** 부팅구간 access violation 10관측일째 재현 여부
- [ ] **D-664-2 (관측)** `[SessionStateDrop]` 10/8 장전에도 재현되는지 — F-1(538-4) 미적용 지속 확인
- [ ] 663-4 F-1(663차) 라이브 검증 — 오늘 diff 타임아웃 0건으로 조건 미발생, 판정 보류 유지. 다음 타임아웃 발생일에 재확인.
- [ ] **사용자 조치 대기 — F-1(538-4) 승인 여부** session_state 마커 승계(`strategy/runtime/session_recovery_service.py:increment_session()`) 적용 승인 필요 (검토 ~5분).
- [ ] (고도화 제안, 승인 대기) `scripts/collect_evidence.py`의 매분 루프 커버리지·`raw_candles` 결손 계산을 장중 실행 시 분모 "09:00~수집 시각"으로 국면 분기 — 2026-09-14·09-29·10-07(665차) 3회 반복된 "미발생 구간을 결손으로 오독" 패턴 근거. 코드 변경 승인 필요(C등급 아님…
- [ ] **F-2 (신규, 사용자 승인 대기)** 15:10 예측 파이프라인 중단 가드 보강 — `main.py:_on_candle_closed()`(약 5881행)의 `is_force_exit_time(now)` 판정에 분봉 자체의 `ts`(벽시계가 아닌 분봉 소속 시각) 병행 확인 조건 추가, `utils/time_utils.py`에 `is_for…
- [ ] **G-3 재우선순위화 검토** `[Position] 진입` 로그 공통화(기존 항목) — 666차에서 범위 확장 확인: 종전엔 "[Position] 진입" 한 줄만 빠지는 것으로 알려졌으나, 실제로는 `[주문요청]`(등급·방향·역방향진입 여부)도 함께 빠진다(§1-5). G-3 착수 여부 판단 시 이 범위 확장을 반영할 것 — 코드 변경은 아직…
- [ ] **O-t1 (신규, 상시 관측)** `raw_candles` 당일 max ts가 15:08을 다시 넘는지(`[BarGap]` ERROR 재현 여부) — 재현되면 "드문 사고 아니라 상시 위험"으로 격상, F-2 적용 시급성 상향.
- [ ] **O-t2 (신규)** Chejan 선행체결 레이스(`[C1]` 가드) 재발 시 `[주문요청]`도 함께 빠지는지 재확인(§1-5 패턴 일반성 확인) — 다음 재발 1건으로 패턴 재확인.
- [ ] 1-1·1-2·1-3(부팅 access violation·SessionStateDrop·git lock 잔재) 지속 — 변화 없음, D-664-1·D-664-2(10/8 장전 재현 여부)로 이월 유지.
- [ ] 663-4(git diff 타임아웃 2차 호출 생략 검증) 지속 — 오늘도 조건 미발생(타임아웃 0건), 다음 타임아웃 발생일에 재확인.
- [ ] 663-3(부팅 access violation 코드 직접 검토, `dashboard/main_dashboard.py:7240~7250`) 지속 — 조사 자체는 승인 불요, 다음 장후로 착수 이월.
- [ ] 663-1(F-5 브로커 어댑터 진단 로그)·663-2(F-7 microstructure 백테스트 실패) — 사용자 선택 대기 지속, 변화 없음.
- [ ] F-1(538-4, session_state 마커 승계) — 사용자 승인 대기 지속, 변화 없음.
- [ ] 663-3 하향: 부팅 access violation = 처리된 first-chance 예외 **추정**(덤프 뒤 `[FreezeWatchdog] START` 연속, 21회 전부 생존). D-664-1 관측 시 "덤프 뒤 기동 계속 여부" 병기 → 3거래일 연속 생존이면 무해로 종결.
- [ ] F-2·F-1(538-4)·G-3 — 승인/결정 대기 지속(666차 항목 그대로, 자동조치 범위 밖).
- [ ] **10-08 장전(사람)**: Chrome 확장 설치 — `chrome://extensions` → 개발자 모드 → 압축해제 로드 `tools\peter2_live\extension`. X 로그인 확인. 08:30 이후 고정 탭 생성·`receiver.py --check` posts 증가 확인. SYSTEM `[Peter2] 기동 … offs…
- [ ] **10-08 장후**: `일일/피터2_일일_MW0601_20261008.md` 검토 — 수신 지연 중앙값(재생 가정 20초 대비), 기각·해제 사유, 오진입 0건 여부(사전등록 ④ 즉시정지 조건).
- [ ] X 호출 제한 실측 — 15초 새로고침에서 오류 화면(`collector.json` error) 발생 여부. 나면 주기 재조정.
- [ ] `peter_month_report.py` 에 피터2 추종 집계 절 추가.
- [ ] 10-12(만기 다음 첫날) `safe=False` 로 진입 없이 기록만 되는지 확인 → 그날 장후 offset 실측 뒤 10-13 재개.
- [ ] **1-1 (P1, 신규)** 개장전(08:48·08:54) 원인불명 2회 자동 재시작 — watchdog 트리거 아님 확인(strikes=0, 동결센티나 FZ-2도 감시창 밖). 런처 종료사유 3분류 로깅 선행 조사 필요(위치 미확정) — 장후 세션에서 조사 착수.
- [ ] **O-p1 (신규, 다음 장전 판정)** 내일(10/9) 장전에도 개장전 2단 재시작이 재현되는지, 가동시간 추이(8분→6분) 지속되는지.
- [ ] **1-2 (P1, 신규)** `collect_evidence.py:2637` "당일 커밋" 시간대 미지정 결함(리눅스 샌드박스 전용, Windows 무관) — Fix: `"--since=%s 00:00:00 +0900" % D` / `until` 동일 패턴. 사용자 승인 후 장후 적용.
- [ ] 663-3(부팅 access violation 코드 직접 검토, `dashboard/main_dashboard.py:7240~7250`) 지속 — 오늘도 미착수, 다음 장후로 이월.
- [ ] 663-4(git diff 타임아웃 2차 호출 생략 검증) 지속 — 오늘도 조건 미발생(타임아웃 0건).
- [ ] 663-1(F-5)·663-2(F-7)·F-1(538-4)·F-2·G-3 — 전부 지속, 변화 없음(사용자 승인/선택 대기).
- [ ] F-12: `main.py:3991` `_peter2_execute()` — `self.kill_switch.is_active()` → `self.kill_switch.is_active`(소괄호 제거, `KillSwitch.is_active`가 `@property`라 호출 불가). 피터2 폴링이 오늘 6회 중 5회 `TypeError`로 중단(…
- [ ] 1-1 원인 조사(장후 이월, 669차에서 이미 등록): 개장 전 08:48·08:54 2단 자동 재시작 원인 — 런처 스크립트 + `main.py` 종료 경로 그레핑 선행 조사. 장중 재확인 결과 09:00 이후 재발 0건.
- [ ] O-p1 판정: 10/9 장전 점검에서 "개장 전 2단계 재시작 재현 여부" 반드시 확인·판정(보류 중 이월분).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 없음.

## 2026-10-07 (MW0601 667차 — 666차 후속 장후 자동조치)

- [x] (고도화 G-2) 수집기 장중 분모 컷 — `f9e54dd` (위 665차 「고도화 제안, 승인 대기」 항목 완료)
- [ ] 663-3 하향: 부팅 access violation = 처리된 first-chance 예외 **추정**(덤프 뒤 `[FreezeWatchdog] START` 연속, 21회 전부 생존). D-664-1 관측 시 "덤프 뒤 기동 계속 여부" 병기 → 3거래일 연속 생존이면 무해로 종결.
- [ ] F-2·F-1(538-4)·G-3 — 승인/결정 대기 지속(666차 항목 그대로, 자동조치 범위 밖).
## 2026-10-07 (MW0601 668차 — 피터2 실시간 추종 신설)

- [ ] **10-08 장전(사람)**: Chrome 확장 설치 — `chrome://extensions` → 개발자 모드 → 압축해제 로드 `tools\peter2_live\extension`. X 로그인 확인. 08:30 이후 고정 탭 생성·`receiver.py --check` posts 증가 확인. SYSTEM `[Peter2] 기동 … offset=-5.4 safe=True` 확인.
- [ ] **10-08 장후**: `일일/피터2_일일_MW0601_20261008.md` 검토 — 수신 지연 중앙값(재생 가정 20초 대비), 기각·해제 사유, 오진입 0건 여부(사전등록 ④ 즉시정지 조건).
- [ ] X 호출 제한 실측 — 15초 새로고침에서 오류 화면(`collector.json` error) 발생 여부. 나면 주기 재조정.
- [x] `PETER2_DAILY_STOP_LIMIT` → 0(해제) — 2026-10-07 사용자 결정.
- [ ] `peter_month_report.py` 에 피터2 추종 집계 절 추가.
- [ ] 10-12(만기 다음 첫날) `safe=False` 로 진입 없이 기록만 되는지 확인 → 그날 장후 offset 실측 뒤 10-13 재개.

## 2026-10-08 (MW0601 669차 — 장전 점검)

- [x] D-664-1 판정완료 — 부팅구간 access violation 10관측일째 재현, 오늘은 PID 교체 동반(1-1 참조, 과거 9일과 다름).
- [x] D-664-2 판정완료 — [SessionStateDrop] 재현, F-1(538-4) 미적용 지속 확인(변화 없음).
- [ ] **1-1 (P1, 신규)** 개장전(08:48·08:54) 원인불명 2회 자동 재시작 — watchdog 트리거 아님 확인(strikes=0, 동결센티나 FZ-2도 감시창 밖). 런처 종료사유 3분류 로깅 선행 조사 필요(위치 미확정) — 장후 세션에서 조사 착수.
- [ ] **O-p1 (신규, 다음 장전 판정)** 내일(10/9) 장전에도 개장전 2단 재시작이 재현되는지, 가동시간 추이(8분→6분) 지속되는지.
- [ ] **1-2 (P1, 신규)** `collect_evidence.py:2637` "당일 커밋" 시간대 미지정 결함(리눅스 샌드박스 전용, Windows 무관) — Fix: `"--since=%s 00:00:00 +0900" % D` / `until` 동일 패턴. 사용자 승인 후 장후 적용.
- [ ] 663-3(부팅 access violation 코드 직접 검토, `dashboard/main_dashboard.py:7240~7250`) 지속 — 오늘도 미착수, 다음 장후로 이월.
- [ ] 663-4(git diff 타임아웃 2차 호출 생략 검증) 지속 — 오늘도 조건 미발생(타임아웃 0건).
- [ ] 663-1(F-5)·663-2(F-7)·F-1(538-4)·F-2·G-3 — 전부 지속, 변화 없음(사용자 승인/선택 대기).
- [x] 668차 후속4(Peter2 DashboardAdapter AttributeError) 반영 확인 완료 — grep·로그 재확인, 08:54:42 이후 인스턴스 재발 없음.

## 2026-10-08 (MW0601 670차 — 장중 점검)

- [ ] F-12: `main.py:3991` `_peter2_execute()` — `self.kill_switch.is_active()` → `self.kill_switch.is_active`(소괄호 제거, `KillSwitch.is_active`가 `@property`라 호출 불가). 피터2 폴링이 오늘 6회 중 5회 `TypeError`로 중단(09:25:54·09:57:58·09:58:24·12:17:24·12:18:24, `logs/20261008_WARN.log`). 사용자 승인 후 장후 적용.
- [ ] 1-1 원인 조사(장후 이월, 669차에서 이미 등록): 개장 전 08:48·08:54 2단 자동 재시작 원인 — 런처 스크립트 + `main.py` 종료 경로 그레핑 선행 조사. 장중 재확인 결과 09:00 이후 재발 0건.
- [ ] O-p1 판정: 10/9 장전 점검에서 "개장 전 2단계 재시작 재현 여부" 반드시 확인·판정(보류 중 이월분).

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

### `data/heartbeat_MW0601_20261008.json` — 243B · 10-08 15:43:27
```json
{
 "pid": 17076,
 "written_at": "2026-10-08T15:43:27",
 "beat_epoch": 1791441807.228559,
 "beat_age_sec": 0.3,
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

### `data/peter_feed/_raw/2026-10-08.eod_ids.json` — 667B · 10-08 16:17:48
```json
[
 "2107986754829697490",
 "2107990718077972868",
 "2107990891164209552",
 "2107998608826220608",
 "2107998789894393978",
 "2107998963999912446",
 "2108028213050106067",
 "2108028918771192271",
 "2108031411995464020",
 "2108032910918082689",
 "2108033892410335482",
 "2108034141199757606",
 "2108039359689814483",
 "2108044882246021630",
 "2108045446476370273",
 "2108052144805077206",
 "2108054958688161847",
 "2108058246091255875",
 "2108058346565873973",
 "2108058411711795306",
 "2108058506150686902",
 "2108058587721572717",
 "2108068399544926581",
 "2108068483737194650",
 "2108068595809091736",
 "2108068687613927594",
 "2108068785861304459",
 "2108080532622045666",
 "2108081128360013903"
]
```

### `data/peter_feed/_raw/2026-10-08.jsonl` — 5.9KB · 10-08 15:25:39
```json
JSONL 31행 ⏎ 첫: {"id": "2107986754829697490", "dt": "2026-10-08T00:09:41.000Z", "text": "1070 부근에서 반등 가능성 큼.\n\n만약 1070 밑으로 떨어지면 매수 기회니까 대기.", "seen_at": "2026-10-08T09:09:53+09:00", "src": "live"} | {"id": "2107990718077972868", "dt": "2026-10-08T00:25:26.000Z", "text": "1072 상방돌파시 매수. 손절가 1068", "seen_at": "2026-10-08T09:25:54+09:00", "src": "live"} | {"id": "2107990891164209552", "dt": "2026-10-08T00:26:07.000Z", "text": "1072 매수체결.", "seen_at": "2026-10-08T09:26:24+09:00", "src": "live"} ⏎ 끝: {"id": "2108080475772432531", "dt": "2026-10-08T06:22:06.000Z", "text": "1053 청산가로 변경", "seen_at": "2026-10-08T15:22:24+09:00", "src": "live"} | {"id": "2108081128360013903", "dt": "2026-10-08T06:24:41.000Z", "text": "4+6+3+4 = 17p  손실.\n\n오늘 예상외로 빼네요.\n\n중간에 1068까지 갔는데 욕심낸것도 패착.", "seen_at": "2026-10-08T15:25:39+09:00", "src": "live"} | {"id": "2108080532622045666", "dt": "2026-10-08T06:22:19.000Z", "text": "1052 손절", "seen_at": "2026-10-08T15:25:39+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-08 15:53:40**

| 키 | 값 | 수집 대상일(2026-10-08)과 일치 |
|---|---|---|
| `date` | 2026-10-08 | 예 |
| `p8_last_success_date` | 2026-10-08 | 예 |
| `eod_retrain_ok_date` | 2026-10-08 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-08 08:55:38 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-07) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-08 08:55:38 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-07) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 377 |
| `session_bars` 당일 행수 | 388 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 7봉** (`session_bars` 에도 없음): 08:48, 08:49, 08:50, 08:51, 08:52, 08:53, 08:54

- 라이브 로그 대조: `logs/20261008_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 4회 · 재시작 2회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 4개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **12건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 6040: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:47 · 정규장(09:00) 이후 **0건**
- PID 17076: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 15:42:33 · 정규장(09:00) 이후 **3건**
- PID 29516: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:54:42 · 정규장(09:00) 이후 **0건**
- PID 29960: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:48:50 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 6040 | 08:40:47 | 08:48:28 | 없음 | 판정불가 — WER **미측정** |
| 29960 | 08:48:50 | 08:54:20 | 없음 | 판정불가 — WER **미측정** |
| 29516 | 08:54:42 | 15:38:49 | 없음 | 판정불가 — WER **미측정** |
| 17076 | 15:42:33 | 15:43:55 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 207개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261008-점검리포트.md` | 35.5KB | 10-08 12:38 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261008.md` | 15.9KB | 10-08 12:38 |
| `docs/정기점검/매일점검/evidence_MW0601-20261008_intra.md` | 81.9KB | 10-08 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261008_pre.md` | 64.9KB | 10-08 08:59 |
| `docs/정기점검/매일점검/MW0601-20261007-점검리포트.md` | 85.5KB | 10-07 17:31 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_post.md` | 92.8KB | 10-07 16:17 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261007.md` | 17.4KB | 10-07 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_intra.md` | 80.5KB | 10-07 12:27 |

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

1. `logs/20261008_WARN.log`: ERROR 이상 16건
2. `logs/20261008_WARN.log`: **Traceback** 출현 7건 — 크래시/메모리 계열
3. 포지션 7건 중 최종청산이 하드스톱·손절 계열 **7건(100%)** — 손절 준수율 확인 필요 (레그 9행)
4. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. **SYSTEM 로그가 직전 5거래일 중앙값(18:32)보다 169분 이르게 끝났다** (오늘 15:43) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
7. 메인 스레드 정지 5초 초과 **2건** (최대 6437ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
8. `logs/20261008_WARN.log`: **degraded=ON** 1건(표본)
9. `logs/20261008_SYSTEM.log`: **ConstOut** 8건(표본)
10. `logs/20261008_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20261008_SIGNAL.log`: **ConstOut** 8건(표본)
12. `logs/20261008_LEARNING.log`: **축퇴** 8건(표본)
13. `logs/20261008_HEALTH.log`: **degraded=ON** 1건(표본)
14. `logs/retrain_eod_20261008.log`: **축퇴** 1건(표본)
15. `logs/retrain_eod_20261008.log`: **ConstOut** 1건(표본)
16. `logs/crash_fault.log`: `Windows fatal exception` **12건** (정규장 09:00 이후 3건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
17. 런처 재시작 같은 날 **2회** (08:48 일시적 크래시, 08:54 일시적 크래시) — 재시작 간격·가동시간이 줄어드는지 §9 「프로세스 종료 3축 대사」에서 볼 것 (661차 G-3)
18. 미커밋 변경 101건 (실질 16건 · 코드 0건 · EOL 파생 0건)
19. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261008*.log` (Windows) / `grep 강제청산 logs/*20261008*.log`*