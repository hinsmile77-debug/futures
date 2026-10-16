# 미륵이 증거 다이제스트 — 2026-10-12 / INTRA

- 생성 2026-10-12 12:26:49 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01unjhzg1di56gxu8rdn4bqp/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261012` · `2026-10-12` · `261012` · `1012`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **34개** 파일 · 34개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-intra-cowork-intra-{DATE}-1226.json` | 1 | `data/dailycheck_markers/claude-20261012-intra-cowork-intra-20261012-1226.json` | 179B | 10-12 12:26 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261012.log` | 124B | 10-12 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261012.log` | 140B | 10-12 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261012.json` | 241B | 10-12 12:26 |
| `launcher_{DATE}_084000_21183.log` | 1 | `logs/Mireuk_batch/launcher_20261012_084000_21183.log` | 1.4MB | 10-12 12:26 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261012.log` | 109B | 10-12 08:44 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261012.log` | 7.9KB | 10-12 12:11 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261012.log` | 45.8KB | 10-12 12:25 |
| `position_state.json.gen_{DATE}_101702` | 1 | `data/position_state.json.gen_20261012_101702` | 1.4KB | 10-12 10:09 |
| `position_state.json.gen_{DATE}_101703` | 1 | `data/position_state.json.gen_20261012_101703` | 1.5KB | 10-12 10:17 |
| `position_state.json.gen_{DATE}_101940` | 1 | `data/position_state.json.gen_20261012_101940` | 1.5KB | 10-12 10:17 |
| `retrain_intraday_20260706_{DATE}58.log` | 1 | `logs/retrain_intraday_20260706_101258.log` | 4.6KB | 07-06 10:13 |
| `retrain_intraday_{DATE}_093420.log` | 1 | `logs/retrain_intraday_20261012_093420.log` | 5.7KB | 10-12 09:35 |
| `retrain_intraday_{DATE}_112306.log` | 1 | `logs/retrain_intraday_20261012_112306.log` | 5.7KB | 10-12 11:23 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261012.log` | 34.5KB | 10-12 12:20 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-12.jsonl` | 2.7KB | 10-12 10:34 |
| `{DATE}_0902_D.xls` | 1 | `data/db/option_hts/261012_0902_D.xls` | 477.2KB | 10-12 09:03 |
| `{DATE}_0931_D.xls` | 1 | `data/db/option_hts/261012_0931_D.xls` | 477.4KB | 10-12 09:31 |
| `{DATE}_1007_D.xls` | 1 | `data/db/option_hts/261012_1007_D.xls` | 477.5KB | 10-12 10:07 |
| `{DATE}_1030_D.xls` | 1 | `data/db/option_hts/261012_1030_D.xls` | 477.5KB | 10-12 10:33 |
| `{DATE}_1105_D.xls` | 1 | `data/db/option_hts/261012_1105_D.xls` | 477.6KB | 10-12 11:05 |
| `{DATE}_1133_D.xls` | 1 | `data/db/option_hts/261012_1133_D.xls` | 477.6KB | 10-12 11:33 |
| `{DATE}_1202_D.xls` | 1 | `data/db/option_hts/261012_1202_D.xls` | 477.6KB | 10-12 12:02 |
| `{DATE}_DATA.log` | 1 | `logs/20261012_DATA.log` | 230.8KB | 10-12 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261012_DEBUG.log` | 125.3KB | 10-12 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261012_HEALTH.log` | 3.2KB | 10-12 12:25 |
| `{DATE}_HOGA.log` | 1 | `logs/20261012_HOGA.log` | 31.5MB | 10-12 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261012_LEARNING.log` | 277.2KB | 10-12 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20261012_MICRO.log` | 600.0KB | 10-12 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20261012_PROBE.log` | 83.1KB | 10-12 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261012_SIGNAL.log` | 350.6KB | 10-12 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261012_SYSTEM.log` | 541.6KB | 10-12 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20261012_TRADE.log` | 4.3KB | 10-12 11:23 |
| `{DATE}_WARN.log` | 1 | `logs/20261012_WARN.log` | 384.0KB | 10-12 12:26 |

## 2. 코드·커밋 상태

- HEAD `b0b92de` · 브랜치 `v9-dev` · 미커밋 109건 · 실질 변경 15건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 15 · 미추적 94 · 삭제 12 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261012.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json` … 외 3개
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.8초(`git diff --numstat`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261012.md
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
?? "MAEKJEOM_LADDER.bat - 바로 가기.lnk"
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_20261002.md
?? dev_memory/_tmp_append_decisionlog_20261006_post.md
?? dev_memory/_tmp_append_decisionlog_20261007_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_pre.md
?? dev_memory/_tmp_append_decisionlog_20261009_intra.md
?? dev_memory/_tmp_append_decisionlog_20261009_post.md
?? dev_memory/_tmp_append_decisionlog_20261012_pre.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_pre.md
?? dev_memory/_tmp_append_nexttodo_20261009_intra.md
?? dev_memory/_tmp_append_nexttodo_20261012_pre.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_전일보유_맥점되돌림_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md
… 외 69건
```

**당일(2026-10-12) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
b0b92de [MW0601] 679차 후속2 후속: dev 배포 기록(64e1f0e)
924f20e [MW0601] 679차 후속2: 신동2 실행기 — 장중 회차 잠금 대기 · 원자적 잠금 · 로그 뮤텍스
7068f81 [MW0601] 679차 후속: 사다리 증분 커서 잠재결함 딥다이브 기록 — 현행 유지
d80df65 [MW0601] 679차 후속 후속: dev 배포 기록(5351c8b)
b5d1100 [MW0601] 679차 후속: 맥점 사다리 — 7222 흐름 미래분 채움 제거 · 신동2 최신 해설 legacy 배제
89b4b0b [MW0601] 668차 후속10: dev 피터2 수정 이식 — 시간순 처리 · 탭 증식 · 고아 스크립트 (원 4f603c7·8876cb0·60bfd55, dev/MW0602)
d5f05e9 [MW0601] 668차 후속9 후속: dev 배포 기록(ba1bf6a)
e7f50c6 [MW0601] 668차 후속9: 피터2 체결 트윗 대기에 앞선 지시의 손절·목표 승계 + CLOSED 사유 키 수정
131db0a [MW0601] 668차 후속8 후속: dev 배포 기록(f1d9000·fcdeca8·b44dbd6)
4631654 [MW0601] 668차 후속8: 피터2 하트비트를 「마지막 정상 게시」 기준으로 — X 페이지 오류 반영
c81fa27 [MW0601] 668차 후속7: 피터2 당일 수동 오프셋 — 만기 다음 날 진입 공백 해소
```

**최근 커밋 12건**
```
b0b92de [MW0601] 679차 후속2 후속: dev 배포 기록(64e1f0e)
924f20e [MW0601] 679차 후속2: 신동2 실행기 — 장중 회차 잠금 대기 · 원자적 잠금 · 로그 뮤텍스
7068f81 [MW0601] 679차 후속: 사다리 증분 커서 잠재결함 딥다이브 기록 — 현행 유지
d80df65 [MW0601] 679차 후속 후속: dev 배포 기록(5351c8b)
b5d1100 [MW0601] 679차 후속: 맥점 사다리 — 7222 흐름 미래분 채움 제거 · 신동2 최신 해설 legacy 배제
89b4b0b [MW0601] 668차 후속10: dev 피터2 수정 이식 — 시간순 처리 · 탭 증식 · 고아 스크립트 (원 4f603c7·8876cb0·60bfd55, dev/MW0602)
d5f05e9 [MW0601] 668차 후속9 후속: dev 배포 기록(ba1bf6a)
e7f50c6 [MW0601] 668차 후속9: 피터2 체결 트윗 대기에 앞선 지시의 손절·목표 승계 + CLOSED 사유 키 수정
131db0a [MW0601] 668차 후속8 후속: dev 배포 기록(f1d9000·fcdeca8·b44dbd6)
4631654 [MW0601] 668차 후속8: 피터2 하트비트를 「마지막 정상 게시」 기준으로 — X 페이지 오류 반영
c81fa27 [MW0601] 668차 후속7: 피터2 당일 수동 오프셋 — 만기 다음 날 진입 공백 해소
0b73a74 [MW0601] 679차: 맥점 사다리 자동기동 예약작업 — 월–금 08:44, 휴장일 건너뜀 · 매일 새로 기동
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

_본문 미열람(설정): `20261012_HOGA.log` 31.5MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260706_101258.log`, `20261012_MICRO.log`, `20261012_DATA.log`, `20261012_PROBE.log`, `launcher_20261012_084000_21183.log`, `20261012_DEBUG.log`, `peter2_receiver_20261012.log`, `shindong2_20261012.log`_

### `logs/20261012_TRADE.log` — 4.3KB · 35행 · 최종 11:23:02

- 형식 평문 · 시각 인식 35행 · WARNING=2, INFO=33

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-12 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-12 09:34:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-12 09:34:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-12 10:02:40 [INFO] TRADE: [Peter2] 진입 LONG 1계약 @1023.66 손절 1019.72 목표 - — limit LONG 지시 1026(미니 1023.72) 현재 1023.66
  …
2026-10-12 10:19:40 [INFO] TRADE: [Chejan] 상태=체결 주문번호=1738 code=A056B 방향=SHORT 체결=1 미체결=0
2026-10-12 10:19:40 [INFO] TRADE: [Position] 체결청산 LONG @ 1016.66 | PnL=-3.76pt (-189,939원) | 하드스톱(틱)
2026-10-12 10:19:40 [INFO] TRADE: [청산 완료] PnL=-3.76pt (-189,939원) | 포지션 합계 -189,939원 (레그 1)
2026-10-12 10:28:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=34,671,804) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-10-12 11:23:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 2 | 10:02:40 | 10:17:03 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1023.70 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×35

**컴포넌트 상위 15** — `Position`×8, `Chejan`×8, `주문요청`×4, `ProfitGuard`×3, `Peter2`×3, `PositionFallback`×2, `체결진입`×2, `TickStop-S0C`×2, `청산 완료`×2, `Sizer`×1

### `logs/20261012_WARN.log` — 384.0KB · 1782행 · 최종 12:26:39

- 형식 평문 · 시각 인식 1782행 · CRITICAL=1, WARNING=1781

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-10-12 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-12 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-12 12:26:39 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 81.5ms | size=1793x930 candles=220 grid=25.5 spans=1.9 candles=17.4 dir=0.7 regime=4.9 markers=29.1 axes=0.8 cross=0.0 | slow_cnt=498 total_cnt=498 overlay_cnt=4949
2026-10-12 12:26:50 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 96.4ms | size=1793x930 candles=220 grid=30.4 spans=1.9 candles=17.5 dir=0.7 regime=4.9 markers=38.1 axes=1.5 cross=0.0 | slow_cnt=499 total_cnt=499 overlay_cnt=4963
2026-10-12 12:27:01 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 114.3ms | size=1793x930 candles=221 grid=32.4 spans=1.9 candles=21.8 dir=0.9 regime=6.6 markers=48.0 axes=1.4 cross=0.0 | slow_cnt=500 total_cnt=500 overlay_cnt=4980
2026-10-12 12:27:07 [WARNING] SYSTEM: [LiveDBG] _fetch_investor_data 지연 544ms — 메인 스레드 544ms 점유 (live 중단 원인 후보)
2026-10-12 12:27:07 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 83.3ms | size=1793x930 candles=221 grid=23.8 spans=1.8 candles=16.6 dir=0.7 regime=4.9 markers=32.6 axes=1.6 cross=0.0 | slow_cnt=501 total_cnt=501 overlay_cnt=4991
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 09:36:06 | 09:36:06 | level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 30종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1453 | 09:36:09 | 12:27:07 | restore_saved_geometry: y=-493 < 0 → y=0으로 보정 (음수 y → Windows DPI 1.5× 확대 방지) |
| `LiveDBG` | 157 | 08:41:08 | 12:27:07 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 42 | 08:41:19 | 12:26:07 | 그리기 71.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 889x1001 |
| `Peter2` | 17 | 08:41:14 | 12:22:56 | 기동 date=2026-10-12 offset=-4.88 src=prev_day:2026-10-08 safe=False 복원트윗=0 집행이력=0 손절=0 |
| `PipePerf` | 12 | 09:00:01 | 12:11:04 | total=1059ms | S0=2ms S1=16ms S2=0ms S3=0ms S4=92ms S5=772ms S6=157ms S7=14ms S8=4ms |
| `CB⑤` | 10 | 09:00:01 | 12:11:04 | 파이프라인 1059ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 9 | 09:00:01 | 12:24:00 | level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0 |
| `ScalerRefresh` | 9 | 09:22:00 | 12:11:03 | 5분 누적 수익률 +0.527% (임계 ±0.442%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PendingOrder` | 8 | 10:02:40 | 10:19:40 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 1023.66, 'reason': '진입', 'hint_source': '', 'atr': 2.1514, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qty… |
| `ChejanFlow` | 8 | 10:02:40 | 10:19:40 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='1484' | pending='ENTRY:LONG qty=1 filled=0 order_no=? reason=진입 req_at=10:02:40.440' | positio… |
| `ChejanMatch` | 8 | 10:02:40 | 10:19:40 | order_no='1484' | pending='ENTRY:LONG qty=1 filled=0 order_no=1484 reason=진입 req_at=10:02:40.440' | pending_matched=True |
| `출처축` | 6 | 08:41:09 | 11:23:06 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |

**채널** — `SYSTEM`×1772, `HEALTH`×10

**컴포넌트 상위 15** — `ChartDBG`×1453, `LiveDBG`×157, `OptionFlowChart`×42, `Peter2`×17, `PipePerf`×12, `Health`×10, `CB⑤`×10, `ScalerRefresh`×9, `PendingOrder`×8, `ChejanFlow`×8, `ChejanMatch`×8, `출처축`×6, `CB`×4, `ExitCooldown`×4, `CB③-P4`×4

### `logs/20261012_SYSTEM.log` — 541.6KB · 3700행 · 최종 12:26:41

- 형식 평문 · 시각 인식 3685행 · INFO=3685, PLAIN=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15168 | 행감지=30s all_threads=True
2026-10-12 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.42s | predictions=0.05s trades=0.20s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-12 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-12 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-12 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-12 12:27:06 [INFO] SYSTEM: [PumpGuard] rollover 연기 — 메인 펌프(BlockRequest 대기) 중 재진입 회피 (누적 69회, 재시도=호출부)
2026-10-12 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-639,foreign:-920,institution:+1597} amt_mn={individual:-164063,foreign:-237816,institution:+411458}
2026-10-12 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-639,foreign:-920,institution:+1597} amt_mn={individual:-164063,foreign:-237816,institution:+411458}
2026-10-12 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-32633 nonarb=-425832
2026-10-12 12:27:06 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-32633 nonarb=-425832
```

</details>

**채널** — `SYSTEM`×3685

**컴포넌트 상위 15** — `CybosInvestorRaw`×828, `CybosRT-TICK`×758, `TickUI`×220, `CybosRT-ROLLOVER`×220, `BAR-CLOSE`×220, `CVD-ANCHOR`×220, `S6Detail`×206, `PipePerf`×206, `PumpGuard`×117, `System`×71, `CybosSub`×63, `OptionChain`×46, `MicroRegime`×46, `OptionBook`×42, `RegimeFingerprint`×39

### `logs/20261012_SIGNAL.log` — 350.6KB · 3028행 · 최종 12:26:00

- 형식 평문 · 시각 인식 3028행 · WARNING=1421, INFO=1607

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.411
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.403
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.399
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.407
  …
2026-10-12 12:27:00 [INFO] SIGNAL: [MicroRegime] 레짐 변경 → 횡보장 (ADX=19.0 ATR비=0.92 지속=1분 근거=none z=0)
2026-10-12 12:27:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=44.9% grade=X regime=NEUTRAL
2026-10-12 12:27:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-10-12 12:27:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=44.9% grade=X micro=횡보장
2026-10-12 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.449<mc0.650) / FL고착(1m)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1104 | 09:00:01 | 12:24:00 | 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 96 | 09:01:00 | 11:24:00 | 1m 극단 z-score 7개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 90 | 09:01:00 | 11:24:00 | ts=09:00 horizon=1m age=1m max_z=+5.18(volume_acceleration) extreme=7 adj=5 |
| `Checklist` | 55 | 09:06:00 | 12:21:00 | 신뢰도 미달 36.9% < 38.1% → 강제 X등급 |
| `WeightCollapse` | 50 | 09:07:00 | 12:25:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 18 | 08:45:09 | 08:45:09 | 1m CORE 'vwap_position' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 7 | 10:14:00 | 12:14:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 1 | 09:47:00 | 09:47:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×3028

**컴포넌트 상위 15** — `ScalerFloor`×1164, `SIGNAL`×412, `Ensemble`×203, `ZeroDiag`×203, `FQAdj`×167, `MetaGate`×132, `Model`×126, `ScalerMonitor`×90, `Checklist`×61, `WeightCollapse`×50, `ScalerRefresh`×47, `MicroRegime`×46, `ATR-Horizon`×41, `InstabilityGate`×33, `TrendGate`×29

### `logs/20261012_LEARNING.log` — 277.2KB · 2160행 · 최종 12:26:00

- 형식 평문 · 시각 인식 2160행 · WARNING=433, INFO=1727

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00133 auc=0.543 out_max=0.3734 (n=110) → 보정 재적용
  …
2026-10-12 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0728% buf_n=20 nonzero=20 prev_p=1019.96 cur_p=1019.56
2026-10-12 12:27:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=56.6% 예측=FL 실제=DN)
2026-10-12 12:27:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=39.1% FL)
2026-10-12 12:27:00 [INFO] LEARNING: [Bias⚠] 1m 적중=32%(6/19) UP=0 DN=0 FL=19 [FL편향⚠ 100%]
2026-10-12 12:27:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=10.0%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 143 | 08:40:50 | 11:22:57 | 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 126 | 08:40:50 | 11:40:00 | 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 53 | 08:40:50 | 11:39:00 | 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 49 | 08:40:51 | 11:22:57 | 하한 도달불가 — out_max=0.3005 < conf_floor=0.3300 (span=0.00088 auc=0.534 out_max=0.3005, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 45 | 08:40:51 | 11:22:57 | 축퇴 감지 — span=0.00044 auc=0.490 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 13 | 08:40:51 | 11:22:57 | 축퇴 감지 — span=0.00081 auc=0.517 out_max=0.2629 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 3 | 08:40:59 | 11:22:58 | 복원한 보정기가 축퇴 상태 — span=0.01232 auc=0.468 out_max=0.4068 (n=3107) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 12:11:01 | 12:11:01 | total=856ms raw_fetch=9ms pred_select=829ms pred_update=7ms pred_insert=6ms verified=3 |

**채널** — `LEARNING`×2160

**컴포넌트 상위 15** — `LEARNING`×615, `Calibration:30m`×285, `Calibration:1m`×248, `SGD`×207, `sigma`×167, `Calibration:3m`×101, `Bias⚠`×97, `Calibration:10m`×95, `Calibration:5m`×84, `Bias`×61, `OnlineLearner`×58, `MetaConf`×36, `ScalerWarmup`×29, `Calibration:15m`×23, `BiasReset`×16

### `logs/20261012_HEALTH.log` — 3.2KB · 22행 · 최종 12:25:01

- 형식 평문 · 시각 인식 22행 · CRITICAL=1, WARNING=9, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0
2026-10-12 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=591ms | quality=1.00 | cache_age=111s | exceptions_10m=0
2026-10-12 09:14:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1776ms | quality=1.00 | cache_age=155s | exceptions_10m=0
2026-10-12 09:15:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=356ms | quality=1.00 | cache_age=30s | exceptions_10m=0
2026-10-12 09:29:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 374ms (표본 20분)
  …
2026-10-12 11:43:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 296ms (표본 20분)
2026-10-12 12:11:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3416ms | quality=1.00 | cache_age=140s | exceptions_10m=3 | exc_tags=[Peter2]×3
2026-10-12 12:12:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=331ms | quality=1.00 | cache_age=13s | exceptions_10m=3 | exc_tags=[Peter2]×3
2026-10-12 12:24:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=390ms | quality=1.00 | cache_age=182s | exceptions_10m=3 | exc_tags=[Peter2]×3
2026-10-12 12:25:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=279ms | quality=1.00 | cache_age=59s | exceptions_10m=3 | exc_tags=[Peter2]×3
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 09:36:06 | 09:36:06 | level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:01 | 12:24:00 | level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0 |

**채널** — `HEALTH`×22

**컴포넌트 상위 15** — `Health`×19, `HealthTrend`×3

### `logs/retrain_intraday_20261012_093420.log` — 5.7KB · 43행 · 최종 09:35:03

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 09:34:20,955 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-12 09:34:20,955 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-12 09:34:20,956 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-12 09:34:20,956 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-12 09:34:20,956 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7924fd37.json
  …
2026-10-12 09:35:03,964 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-12 09:35:03,965 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-12 09:35:03,965 [INFO] LEARNING: [Retrain] 완료 | 39.9초 | 성공=6/6 호라이즌
2026-10-12 09:35:03,966 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 43.0s 데이터=4800행
2026-10-12 09:35:03,968 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7924fd37.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 09:34:34 | 09:34:34 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 20444/44090 제외 (418차 결정 1) — 남은 23646행 |
| `UnitMismatch` | 1 | 09:34:34 | 09:34:34 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23646행 제외 (559차 P1'-2) — 남은 22200행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

### `logs/retrain_intraday_20261012_112306.log` — 5.7KB · 43행 · 최종 11:23:47

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 11:23:06,670 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-12 11:23:06,671 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-12 11:23:06,671 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-12 11:23:06,671 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-12 11:23:06,672 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7ca13668.json
  …
2026-10-12 11:23:47,434 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-12 11:23:47,435 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-12 11:23:47,436 [INFO] LEARNING: [Retrain] 완료 | 37.9초 | 성공=6/6 호라이즌
2026-10-12 11:23:47,437 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 40.8s 데이터=4800행
2026-10-12 11:23:47,438 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7ca13668.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 11:23:19 | 11:23:19 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 20335/44089 제외 (418차 결정 1) — 남은 23754행 |
| `UnitMismatch` | 1 | 11:23:19 | 11:23:19 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23754행 제외 (559차 P1'-2) — 남은 22308행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 23 |
| 사이저 호출(`[Sizer]`) | 1 |

### 포지션 2건 · 승 0 (0%) · 합계 -7.74pt (-390,884원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:02:40 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.98 | -200,945 | 하드스톱(틱) |
| 10:17:03 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.76 | -189,939 | 하드스톱(틱) |

**출처별 소계** — 추정 2건 -390,884원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 2건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 2행** (부분청산 0 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:09:22 | 전량 | 1 | -3.98 | -200,945 | 하드스톱(틱) |
| 10:19:40 | 전량 | 1 | -3.76 | -189,939 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×2

> 최종 청산이 하드스톱·손절 계열인 포지션 2/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -390,884 = 포지션합 -390,884 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×1

### 차단 사유 23건 · 7종

| 건수 | 사유 |
|---|---|
| 16 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 청산 후 쿨다운 — 82초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 160초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.2pt > ATR×5.0=9.8pt (시가=1033.20 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |

**체크리스트 미통과 항목 누적** — `2_confidence`×16, `3_vwap`×3, `4_cvd`×3, `6_foreign`×3, `7_prev_bar`×3, `11_countertrend`×3, `5_ofi`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 9건

- `×1 [LEVELS]×1 [RESTART]×1` ×3
- `5분 진입 정지 | 파이프라인 5990ms — 처리 지연 (임계=5000ms)` ×2
- `일시 정지 해제 — 정상 복귀` ×2
- `연속 손절 1회 (300초 창, 포지션 단위)` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 18건 · 최대 7484ms · 5초 초과 2건

상위 — 7484ms, 5375ms, 4203ms, 3562ms, 3390ms, 3234ms, 3062ms, 2859ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:36:07 | 7484ms | 5990ms | **1494ms (20%)** |
| 12:11:05 | 5375ms | 3416ms | **1959ms (36%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261012_WARN.log`
```
--- [CB] ×5(표본)
09:36:06 2026-10-12 09:36:06 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5990ms — 처리 지연 (임계=5000ms)
09:36:06 2026-10-12 09:36:06 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5990ms — 처리 지연 (임계=5000ms)
09:37:00 2026-10-12 09:37:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=409ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[CB]×1 [LEVELS]×1 [RESTART]×1
10:09:22 2026-10-12 10:09:22 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×5(표본)
10:09:22 2026-10-12 10:09:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:12:22)
10:09:22 2026-10-12 10:09:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:12:22)
10:19:40 2026-10-12 10:19:40 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:22:40)
10:19:40 2026-10-12 10:19:40 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:22:40)
--- level=CRITICAL ×1(표본)
09:36:06 2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-12 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4203 band=INFO since_pipe_s=NA
09:00:02 2026-10-12 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.1
09:05:02 2026-10-12 09:05:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.0
09:14:03 2026-10-12 09:14:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3234 band=INFO since_pipe_s=0.1
```

### `logs/20261012_SYSTEM.log`
```
--- CIRCUIT ×2(표본)
09:36:06 2026-10-12 09:36:06 [INFO] SYSTEM: [Notify] 🚨 [09:36:06] [미륵이] Circuit Breaker 발동!
09:36:06 2026-10-12 09:36:06 [INFO] SYSTEM: [Notify] 🚨 [09:36:06] [미륵이] Circuit Breaker 발동!
--- ConstOut ×8(표본)
09:36:05 2026-10-12 09:36:05 [INFO] SYSTEM: [DynMC] ConstOut 고착 conf 제외: [0.85] → 233건 제거 (잔여 1257건)
10:14:00 2026-10-12 10:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4533) | 앙상블 제외는 유지
10:22:00 2026-10-12 10:22:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5399) | 앙상블 제외는 유지
10:34:01 2026-10-12 10:34:01 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4567) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-10-12 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-12 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-10-12 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:16:00 2026-10-12 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×2(표본)
09:42:00 2026-10-12 09:42:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
09:42:00 2026-10-12 09:42:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
```

### `logs/20261012_SIGNAL.log`
```
--- ConstOut ×8(표본)
10:14:00 2026-10-12 10:14:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.2500 dir=-1)
10:14:00 2026-10-12 10:14:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:15:00 2026-10-12 10:15:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:22:00 2026-10-12 10:22:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1110 dir=+0)
--- WeightCollapse ×8(표본)
09:07:00 2026-10-12 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-10-12 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-10-12 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:16:01 2026-10-12 09:16:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.411
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.403
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.399
--- 안전망 ×8(표본)
09:07:00 2026-10-12 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-12 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-12 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:01 2026-10-12 09:16:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261012_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00133 auc=0.543 out_max=0.3734 (n=110) → 보정 재적용
```

### `logs/20261012_HEALTH.log`
```
--- [CB] ×2(표본)
09:37:00 2026-10-12 09:37:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=409ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[CB]×1 [LEVELS]×1 [RESTART]×1
09:38:00 2026-10-12 09:38:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=305ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[CB]×1 [LEVELS]×1 [RESTART]×1
--- [ExitCooldown] ×1(표본)
10:29:00 2026-10-12 10:29:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=288ms | quality=1.00 | cache_age=180s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
--- level=CRITICAL ×1(표본)
09:36:06 2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261012_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 8 | 10:02:40 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1023.70 — 진입 경로가 파라미터를 넘기지 … |

- 이 로그 생존구간: 08:40 ~ 11:23

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261012_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 14 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:51:32 [WARNING] ChallengerPanel.refresh slow 297ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 147 | 09:54:00 [WARNING] paintEvent slow 57.5ms | size=1793x930 candles=69 grid=21.4 spans=0.6 candles=7.4 dir=0.2 regime=0.8 markers=… |
| 12:00 | 장중 중간점 | 109 | 11:54:01 [WARNING] _tick_header 간격 2281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2281 band=… |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261012_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 97 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=15168 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 193 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 223 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 202 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~12:26: 207/207분 (100.0%)**

_장중 수집 — 분모를 수집 시각 12:26 까지로 줄였다. 이후 164분(~15:10)은 **미도래**라 제외(결손 아님)._

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261012_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:09 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 128 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 225 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| 10:00 | 장중 초반 | 212 | 09:54:00 [WARNING] 신뢰도 미달 39.9% < 47.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 96 | 11:55:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261009 | 18:33 | 로그 본문 |
| 20261008 | 15:43 | 로그 본문 |
| 20261007 | 20:26 | 로그 본문 |
| 20261006 | 15:47 | 로그 본문 |
| 20261005 | 09:41 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261012** | **12:27** | 로그 본문 |

- 델타 **-200분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 검증
### 병행 세션
## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치: F-1 재진단 · G-1 리포트 append 마커)
## 2026-10-09 (MW0601 677차 — 피터2 백필: 실거래 개시 이전 손익을 손익추이·손익추이2 에 올린다)
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2: 위클리 원천 · 먼스리 만기주 기권 · 옵션 금액 단위) — 🟡 **구현 · 라이브 미배포(사다리 서버 재기동 대기)**
## 2026-10-10 (MW0601 679차 — 맥점 사다리 자동기동 예약작업)
## 2026-10-12 (MW0601 680차 — 장전 점검)
## 2026-10-12 (MW0601 668차 후속6–8 — 피터2 집행·오프셋·하트비트 + dev 배포)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 — 오늘 미발생, 저우선.
**배포 기록**: v9-dev `b5d1100` → dev 체리픽 `5351c8b`. ladder_data.py 충돌 — dev 에 **같은 legacy 배제(MW0602 614차 후속2)가 이미 있어** dev 쪽 유지,
flow1m 만 반영. dev 위 test_656·614·678·603 68 passed · 3 skipped. 2026-10-12 푸시 완료.
⚠ MW0602 는 사다리 서버 재기동(또는 다음 날 08:44 자동기동) 후 반영.

**[679차 후속 딥다이브] 사다리 증분 커서의 「늦게 기록된 과거 행」 미반영 — 현행 유지(A) 결정.** 코드 수정 없음.
`_candles_live()`·`futflow()` 는 `ts >= last_ts` 증분이라 last_ts 보다 앞선 ts 가 나중에 기록되면 서버 메모리 캐시가 비워질 때까지 못 본다.
쓰기 경로 전수 확인(2026-10-12):
- 메인 봉 저장 = 비동기 큐 FIFO 단일 워커(`main.py:7911`) → 순서 보존. 프리장 봉은 동기. 7221 은 `ts=now` 분내림 동기 → 단조.
- 복구 재처리는 453차부터 raw_candles 를 다시 쓰지 않는다(`bar_recovered=1` 신규 중단과 일치).
- 재기동 봉결손은 `session_bars` 에만 보충(618차) — raw_candles 결손은 영구(10-12 09:33·11:22).
트리거는 둘뿐: ① 큐(maxsize=60) 포화 시 동기 폴백이 큐에 남은 앞 봉을 추월 — 로그 64개 파일(09-02–10-12)에서 `[DBQueue] 큐 포화` **0회**.
② `scripts/backfill_investor_futures.py`(날짜 상한 없음 → 오늘 포함) 를 장마감 뒤 서버 생존 중 수동 실행 — 호출부 없음, 장중은 guard_intraday 차단.
피해 상한 = 하루: 679차 예약작업이 월–금 08:44 서버를 새로 띄워 캐시가 비워지고, 지난 날짜는 처음부터 다시 읽는다.
보류한 대안: B 되돌아보기 창(last_ts−15분, ①만 막음) · C 매 빌드 당일 PK 범위 전체 재조회(약 420행, 결함 원천 제거 — 656차 「증분 하나뿐」 선언을 뒤집으므로 보류).
⚠ 재론 조건: `[DBQueue] 큐 포화` 가 한 번이라도 찍히거나, 7221 백필을 정기 체인에 편입할 때 → C 로 전환.

**[679차 후속2 `924f20e`] 신동2 실행기 — 장중 회차 잠금 대기 · 원자적 잠금 · 로그 뮤텍스.** 10-12 사다리 점검에서 「11:05 회차 누락」으로 보고했으나
**정정: 10:05 이후 장중은 10:30·11:00·11:30 …(30분)이며 빠진 것은 11:00·11:30 두 회차**였다.
원인: Intraday(10:30+30분)와 Poll(10:10+10분)이 :00·:30 마다 같은 초 출발 → `run.lock` 경합에서 진 쪽이 대기 없이 skip.
poll 은 새 이벤트 없으면 6초 만에 끝나는데 intraday 가 버려졌다. 10:30 이후 장중 9/21(43%) 소실 — 10-07 11:00·13:30·14:00 / 10-08 11:00·13:00·13:30·14:00 / 10-12 11:00·11:30.
10:51 이후 12:00 까지 Claude 판단 0회(패널 정지, 가격 1028→1021).
부수 결함 2건도 실측: ① Test-Path→Set-Content 비원자 잠금 — 12:00 intraday·poll 동시 실행, poll finally 가 intraday 잠금 삭제(피해 없음)
② 동시 Add-Content 공유 위반으로 로그 줄 소실 — 10-07 13:30 intraday 결과·poll start 줄이 흔적 없이 사라짐(계측 4원칙 ③).
조치: poll 외 단계는 3초 간격 최대 5분 대기(`lock acquired after waiting Ns`) · FileMode.CreateNew 잠금 · 이름 있는 뮤텍스(`Local\Mireuk_Shindong2_Log`) 로그 직렬화.
⚠ 첫 판(Add-Content 재시도 40회)은 3프로세스 격리 시험에서 기아로 대량 소실 → 11:59:28 원본 복구 후 뮤텍스로 재작성, 12:01 반영.
격리 시험: 대기 획득 9s · 6개 동시 출발 3초 간격 직렬화 · 로그 900/900 · 13분 묵은 잠금 인수 · 실 실행기 DryRun rc=0(로그 12:03:21 dry=True 4줄이 그 흔적).
**배포 기록**: v9-dev `924f20e` → dev 체리픽 `64e1f0e`. 충돌 — dev 에 676차(`6cb4c04`) 「designed rc」 블록이 없어 그 6줄을 빼고 반영. 2026-10-12 푸시 완료.
⚠ 라이브 첫 확인은 12:30(intraday·poll 겹침) — `[intraday] lock acquired after waiting` 또는 `claude:` 줄이 찍히면 정상.
⚠ MW0602 는 예약작업 재등록 불필요(같은 실행기 경로), 다음 회차부터 반영.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-08 (MW0601 671차 — 장후 점검)
## 2026-10-08 (MW0601 672차 — 671차 후속 장후 자동조치)
## 2026-10-08 (MW0601 672차 — 신동2 학습 사이클)
## 2026-10-09 (MW0601 673차 — 장전 점검)
## 2026-10-09 (MW0601 674차 — 장중 점검)
## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치)
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2)
## 2026-10-12 (MW0601 680차 — 장전 점검)
```

미완료 체크박스 **3094건** (끝에서 30건)
```
- [ ] **672-1** 10/12(월) 장전: `brief` 로 레슨·피드백·추이 읽고 장전계획 **live + legacy 두 건** 남기기(새 월물·3일 연휴 갭 → 수급·맥점·벽 재확인).
- [ ] **672-2** 10/12 장후: `evaluate` → `feedback`(잘한 점/잘못한 점/개선점/레슨) → `trend`. 첫 「개선 − 기존」 짝 1건 적립.
- [ ] **672-3** 후보 레슨 승격 심사(적용 3회·적중 우세): L9·L12·L13 이 10/12–10/14 에 3회 적용되면 10/14 장후 `lesson set --status 적용중`.
- [ ] **672-4** 헤드리스 예약작업 첫 실행(10/12 08:52·15:55)에서 새 명령이 허용 패턴 안에서 실제로 돌았는지 `logs/shindong2_20261012.log` 확인.
- [ ] **672-5** 추이가 5일 쌓이면 사다리 학습 블록의 창 표기(최근 5일)가 의미를 갖는다 — 그때 10/20일 창도 패널에 올릴지 판단.
- [ ] **F-1(1-2 재발 대응)**: `scripts/shindong2_run.ps1`의 `conda run python scripts/shindong2_live.py …` 호출(특히 `gate`)에 `$env:PYTHONIOENCODING="utf-8"; $env:PYTHONUTF8="1"` 추가. 적용 전 다른 서브커맨드 호출부에 이미 적용돼…
- [ ] **G-1(1-1 병행 발화 대응)**: 점검 리포트 append 직전 세션별 생존 마커(`<PC>-<날짜>.lock`, 타임스탬프 포함, 2시간 초과 시 무시) 도입 검토 — 오늘 장전·장중 예약이 12초 차이로 병행 발화했으나 결과 우연히 무해(둘 다 휴장일 판정). 거래일 재발 시 리포트 append 순서 꼬임 위험.
- [ ] **O-p1(2026-10-07 669차 등록, 재이월)**: 개장전(08:48·08:54) 2단 자동 재시작 재현 여부 — 10/9는 휴장일이라 관측 기회 없음. **10/12(월) 장전으로 이월.**
- [ ] **1-1(2026-10-07 669차 등록, 재이월)**: 위와 같은 원인조사(런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 직접 Windows 이벤트 뷰어/작업 관리자 확인 필요) — 10/9 관측 기회 없음. **10/12 장전으로 이월.**
- [ ] **O-t1(2026-10-08 672차 등록, 재이월)**: `trades.db`의 `commission_rate_used`가 CYBOS(`9.8104e-05`)로 정상 복귀했는지 확인 — 10/9는 거래 자체가 없어 확인 대상 없음, 08:45 이후 라이브 DB 전수 스캔 금지 구간이기도 해 이번 세션 미실행. **10/12 거래 발생 이후…
- [ ] **O-t2(2026-10-08 672차 등록, 재이월)**: "원인불명 조용한 종료" 재현 누적 관찰 — 10/9는 시스템 미기동으로 관측 대상 없음. **10/12로 이월.**
- [ ] 미커밋 변경 96건(실질 12건) 정리 — `docs/정기점검/금요일점검/MW0601/` 삭제 12건이 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 — 저장소 정본 `rev: 2026-09-07`(538차) 대비 앱 사본이 `rev: 2026-08-26e`(499차)로 낡음. `save_skill overwrite: true` 필요(이 PC, MW0601 한정 — 함정③).
- [ ] O-i1 (신규, 다음 거래일 판정): 2026-10-12(월) 장전·장중 예약작업이 각자 정해진 시각 근처(±30분)에 발동하는지 확인. 지연 없으면 1-1 ✅해소, 재발하면 `logs/claude_resume_*.log` 감시 스크립트·원격 기기 브리지 연결 상태 원인조사 착수.
- [ ] G-2 (고도화, 이번 주): `collect_evidence.py` §2(병행 세션 확인)에 "예약작업 예정 시각 대비 실제 fired_at 지연"을 자동으로 찍는 계측 추가(현재는 수집기가 `list_triggers` API에 접근하지 않아 수동 대조만 가능). 지연이 30분 이상이면 §11 자동 적신호로 승격.
- [ ] (절차 개선, 비승인 필요 — 기술부채) 대용량 한글 텍스트를 리눅스 샌드박스 세션에서 device에 쓸 때 base64를 모델이 직접 옮겨적는 방식은 1바이트 오기 위험이 있음(2026-10-09 674차에서 실제 발생·즉시 발견·수정함). 앞으로 `device_commit_files` + `cat >> ` 패턴으로 바꿀 것 — DECISIO…
- [ ] **G-2(674차) 이월** — 예약 fired_at 원천 미정(수집기가 예약 목록에 접근 불가). 원천(예: 예약 세션 첫 줄에 발화시각 기록 → `data/dailycheck_markers` 의 `started_at` 활용 가능)부터 정할 것. G-1 마커의 `started_at`이 사실상의 fired_at 근사치가 될 수 있다 — 예정시…
- [ ] 1-2 처분: 10/12 장전 점검에서 오진으로 ✅해소 처리(로그 `(designed rc=…)` 줄 확인).
- [ ] 앱 저장 스킬 사본 갱신 시 §5-2 마커 규약이 들어간 판으로 저장(사용자 몫).
- [ ] 10/12 08:45 전 사다리 서버 재기동(`MAEKJEOM_LADDER.bat`) — 모듈 캐시(`_SD2`) 때문에 재기동해야 v2 가 화면에 뜬다. 신동2 예약작업은 실행마다 새 프로세스라 자동 반영.
- [ ] 10/12 장전 신동2 실행 로그에서 `위클리[…]` 표기 확인 — 10/12(월)은 월위클리(당일 만기) 여야 한다.
- [ ] v2 20거래일 채점(10/12–) 중 O1L·O2L·PX 동시 투표율 기록 — 금액이 PX 와 같은 표만 던지는지(개정 문서 §5 관찰, 판정 무관).
- [ ] MW0602(`dev`) 신동2 코드 보유 여부 — 같은 문제. 반영은 그 PC 결정.
- [ ] 1-1(원인조사, 669차 등록, 재이월 지속) — 런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 Windows 이벤트 뷰어/작업 관리자 직접 확인 필요. 오늘도 미착수.
- [ ] O-t1(2026-10-08 672차 등록, 3차 재이월) — `commission_rate_used` CYBOS 복귀 확인. 오늘 09:01 기준 체결 0건으로 확인 대상 없음. **2026-10-12 장후 점검에서 반드시 확정 판정(더 이상 이월 금지).**
- [ ] O-t2(2026-10-08 672차 등록, 3차 재이월) — "원인불명 조용한 종료" 재현 관찰. 오늘 하루 미종료로 판정 대상 없음, 장후로 이월.
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·F-15·F-16·G-3 — 전부 지속, 변화 없음(사용자 승인/선택 대기 — 중복 기재 생략, 680차 DECISION_LOG 참조).
- [ ] G-4(신규, 고도화 제안) — 오늘 장전 예약 발화 지연값(+39초, 목표 08:57 대비)을 G-2(674차, 발화지연 자동계측) 구현 시 정상 기준표본 1건으로 기록.
- [ ] 미커밋 변경 103건(실질 13건) 정리 확인 — `docs/정기점검/금요일점검/MW0601/` 12건 삭제가 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 정본 `rev: 2026-09-07`(538차) 대비 앱 사본 `rev: 2026-08-26e`(499차)로 낡음(10/9 673차부터 등록, 변화 없음). `save_skill overwrite: true` 필요(이 PC 한정).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
만 가능). 지연이 30분 이상이면 §11 자동 적신호로 승격.
- [ ] (절차 개선, 비승인 필요 — 기술부채) 대용량 한글 텍스트를 리눅스 샌드박스 세션에서 device에 쓸 때 base64를 모델이 직접 옮겨적는 방식은 1바이트 오기 위험이 있음(2026-10-09 674차에서 실제 발생·즉시 발견·수정함). 앞으로 `device_commit_files` + `cat >> ` 패턴으로 바꿀 것 — DECISION_LOG 674차 항목 참조.
- [x] O-p1·O-t1·O-t2(10/8 이전 등록) — 장중 절에서도 지속 확인, 10/12로 이월 유지(장전 673차 판정과 동일, 추가 처분 없음).


## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치)

- [x] **F-1(673차)** — 원안은 이미 반영(`eb4bad3`)·1-2는 오진(conda가 설계 종료코드 3/10에 찍는 ERROR 문구). 대신 래퍼 로그에 `(designed rc=…)` 주석 줄 추가. DECISION_LOG 676차.
- [x] **G-1(673차)** — `scripts/report_append_marker.py` + SKILL.md §5-2 규약. 테스트 `test_675_postmarket_autofix.py`.
- [ ] **G-2(674차) 이월** — 예약 fired_at 원천 미정(수집기가 예약 목록에 접근 불가). 원천(예: 예약 세션 첫 줄에 발화시각 기록 → `data/dailycheck_markers` 의 `started_at` 활용 가능)부터 정할 것. G-1 마커의 `started_at`이 사실상의 fired_at 근사치가 될 수 있다 — 예정시각 표만 있으면 지연 계산 가능.
- [ ] 1-2 처분: 10/12 장전 점검에서 오진으로 ✅해소 처리(로그 `(designed rc=…)` 줄 확인).
- [ ] 앱 저장 스킬 사본 갱신 시 §5-2 마커 규약이 들어간 판으로 저장(사용자 몫).

## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2)
- [ ] 10/12 08:45 전 사다리 서버 재기동(`MAEKJEOM_LADDER.bat`) — 모듈 캐시(`_SD2`) 때문에 재기동해야 v2 가 화면에 뜬다. 신동2 예약작업은 실행마다 새 프로세스라 자동 반영.
- [ ] 10/12 장전 신동2 실행 로그에서 `위클리[…]` 표기 확인 — 10/12(월)은 월위클리(당일 만기) 여야 한다.
- [ ] v2 20거래일 채점(10/12–) 중 O1L·O2L·PX 동시 투표율 기록 — 금액이 PX 와 같은 표만 던지는지(개정 문서 §5 관찰, 판정 무관).
- [ ] MW0602(`dev`) 신동2 코드 보유 여부 — 같은 문제. 반영은 그 PC 결정.

## 2026-10-12 (MW0601 680차 — 장전 점검)

- [x] O-p1(2026-10-07 669차 등록, 10/9 재이월) 판정완료 — 개장전 2단 재시작 미재현(08:41:09 재기동 #1 1건뿐).
- [x] O-i1(2026-10-09 674차 등록) 장전 몫 판정완료 — 장전 예약 발화 08:57:39(목표 대비 +39초), 지연 없음. 장중 몫은 장중 점검이 판정.
- [ ] 1-1(원인조사, 669차 등록, 재이월 지속) — 런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 Windows 이벤트 뷰어/작업 관리자 직접 확인 필요. 오늘도 미착수.
- [ ] O-t1(2026-10-08 672차 등록, 3차 재이월) — `commission_rate_used` CYBOS 복귀 확인. 오늘 09:01 기준 체결 0건으로 확인 대상 없음. **2026-10-12 장후 점검에서 반드시 확정 판정(더 이상 이월 금지).**
- [ ] O-t2(2026-10-08 672차 등록, 3차 재이월) — "원인불명 조용한 종료" 재현 관찰. 오늘 하루 미종료로 판정 대상 없음, 장후로 이월.
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·F-15·F-16·G-3 — 전부 지속, 변화 없음(사용자 승인/선택 대기 — 중복 기재 생략, 680차 DECISION_LOG 참조).
- [ ] G-4(신규, 고도화 제안) — 오늘 장전 예약 발화 지연값(+39초, 목표 08:57 대비)을 G-2(674차, 발화지연 자동계측) 구현 시 정상 기준표본 1건으로 기록.
- [ ] 미커밋 변경 103건(실질 13건) 정리 확인 — `docs/정기점검/금요일점검/MW0601/` 12건 삭제가 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 정본 `rev: 2026-09-07`(538차) 대비 앱 사본 `rev: 2026-08-26e`(499차)로 낡음(10/9 673차부터 등록, 변화 없음). `save_skill overwrite: true` 필요(이 PC 한정).

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

### `data/dailycheck_markers/claude-20261012-intra-cowork-intra-20261012-1226.json` — 179B · 10-12 12:26:45
```json
{
 "pc": "claude",
 "date": "20261012",
 "phase": "intra",
 "session": "cowork-intra-20261012-1226",
 "pid": 6,
 "started_epoch": 1791775606.1705668,
 "started_at": "2026-10-12 03:26:46"
}
```

### `data/heartbeat_MW0601_20261012.json` — 241B · 10-12 12:26:39
```json
{
 "pid": 6396,
 "written_at": "2026-10-12T12:26:39",
 "beat_epoch": 1791775596.95652,
 "beat_age_sec": 2.5,
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

### `data/peter_feed/_raw/2026-10-12.jsonl` — 2.7KB · 10-12 10:34:53
```json
JSONL 16행 ⏎ 첫: {"id": "2109435496904683987", "dt": "2026-10-12T00:06:28.000Z", "text": "1035 상방돌파시 매수. 손절가 1031", "seen_at": "2026-10-12T09:07:08+09:00", "src": "live"} | {"id": "2109436040171929972", "dt": "2026-10-12T00:08:38.000Z", "text": "1035 매수체결.", "seen_at": "2026-10-12T09:09:23+09:00", "src": "live"} | {"id": "2109439327327719926", "dt": "2026-10-12T00:21:41.000Z", "text": "오늘 튀면 죽 튀는 자리니까 청산가 크게 보고 대기", "seen_at": "2026-10-12T09:22:08+09:00", "src": "live"} ⏎ 끝: {"id": "2109453964840505502", "dt": "2026-10-12T01:19:51.000Z", "text": "1019 손절.", "seen_at": "2026-10-12T10:20:38+09:00", "src": "live"} | {"id": "2109455838150844787", "dt": "2026-10-12T01:27:18.000Z", "text": "1017 매수체결. 안된사람 1018에 매수", "seen_at": "2026-10-12T10:34:53+09:00", "src": "live"} | {"id": "2109455711424164155", "dt": "2026-10-12T01:26:48.000Z", "text": "1017 상방돌파시 매수. 손절가 1014", "seen_at": "2026-10-12T10:34:53+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-12 11:24:00**

| 키 | 값 | 수집 대상일(2026-10-12)과 일치 |
|---|---|---|
| `date` | 2026-10-12 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-12 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (3일 전: 2026-10-09) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-12 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-09) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:26** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 12:26 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 220 |
| `session_bars` 당일 행수 | 220 (기대 411) |

- 미도래 **162봉** (12:27~15:08) — 수집 시각 12:26 이후라 결손·영구결손에서 제외
- 결손 **0봉**
- ⚠ **영구 결손 2봉** (`session_bars` 에도 없음): 09:33, 11:22

- 라이브 로그 대조: `logs/20261012_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 3회 · 재시작 2회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 3개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **9건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 6396: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 11:22:46 · 정규장(09:00) 이후 **3건**
- PID 15168: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
- PID 24772: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 09:33:56 · 정규장(09:00) 이후 **3건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 15168 | 08:40:45 | 09:33:34 | 없음 | 판정불가 — WER **미측정** |
| 24772 | 09:33:56 | 11:22:25 | 없음 | 판정불가 — WER **미측정** |
| 6396 | 11:22:46 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 215개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261012-점검리포트.md` | 15.9KB | 10-12 09:11 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_pre.md` | 62.0KB | 10-12 09:01 |
| `docs/정기점검/매일점검/MW0601-20261009-점검리포트.md` | 51.1KB | 10-09 17:29 |
| `docs/정기점검/매일점검/_tmp_append_post_20261009.md` | 19.2KB | 10-09 16:25 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_post.md` | 53.0KB | 10-09 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_pre.md` | 48.6KB | 10-09 15:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_intra.md` | 48.6KB | 10-09 15:34 |
| `docs/정기점검/매일점검/MW0601-20261008-점검리포트.md` | 87.1KB | 10-08 17:30 |

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

1. `logs/20261012_WARN.log`: ERROR 이상 1건
2. `logs/20261012_HEALTH.log`: ERROR 이상 1건
3. 메인 스레드 정지 5초 초과 **2건** (최대 7484ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20261012_WARN.log`: **level=CRITICAL** 1건(표본)
5. `logs/20261012_SYSTEM.log`: **ConstOut** 8건(표본)
6. `logs/20261012_SIGNAL.log`: **WeightCollapse** 8건(표본)
7. `logs/20261012_SIGNAL.log`: **ConstOut** 8건(표본)
8. `logs/20261012_LEARNING.log`: **축퇴** 8건(표본)
9. `logs/20261012_HEALTH.log`: **level=CRITICAL** 1건(표본)
10. `logs/crash_fault.log`: `Windows fatal exception` **9건** (정규장 09:00 이후 6건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
11. 런처 재시작 같은 날 **2회** (09:33 일시적 크래시, 11:22 일시적 크래시) — 재시작 간격·가동시간이 줄어드는지 §9 「프로세스 종료 3축 대사」에서 볼 것 (661차 G-3)
12. 미커밋 변경 109건 (실질 15건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261012*.log` (Windows) / `grep 강제청산 logs/*20261012*.log`*