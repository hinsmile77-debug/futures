# 미륵이 증거 다이제스트 — 2026-10-07 / INTRA

- 생성 2026-10-07 12:27:14 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01c34pgmdhrjhsqdmtac5yyn/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261007` · `2026-10-07` · `261007` · `1007`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261007.log` | 125B | 10-07 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261007.log` | 139B | 10-07 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261007.json` | 243B | 10-07 12:26 |
| `launcher_{DATE}_084001_19477.log` | 1 | `logs/Mireuk_batch/launcher_20261007_084001_19477.log` | 1.5MB | 10-07 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261007.log` | 14.3KB | 10-07 11:28 |
| `position_state.json.gen_{DATE}_111112` | 1 | `data/position_state.json.gen_20261007_111112` | 1.6KB | 10-07 11:08 |
| `position_state.json.gen_{DATE}_111901` | 1 | `data/position_state.json.gen_20261007_111901` | 1.5KB | 10-07 11:19 |
| `position_state.json.gen_{DATE}_111917` | 1 | `data/position_state.json.gen_20261007_111917` | 1.5KB | 10-07 11:19 |
| `retrain_intraday_20260701_{DATE}00.log` | 1 | `logs/retrain_intraday_20260701_100700.log` | 4.6KB | 07-01 10:07 |
| `retrain_intraday_20260805_{DATE}01.log` | 1 | `logs/retrain_intraday_20260805_100701.log` | 4.5KB | 08-05 10:07 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261007.log` | 28.4KB | 10-07 12:20 |
| `{DATE}_0916_D.xls` | 1 | `data/db/option_hts/261007_0916_D.xls` | 480.3KB | 10-07 09:16 |
| `{DATE}_1008_D.xls` | 1 | `data/db/option_hts/261007_1008_D.xls` | 480.4KB | 10-07 10:06 |
| `{DATE}_1031_D.xls` | 1 | `data/db/option_hts/261007_1031_D.xls` | 480.5KB | 10-07 10:31 |
| `{DATE}_1103_D.xls` | 1 | `data/db/option_hts/261007_1103_D.xls` | 480.5KB | 10-07 11:04 |
| `{DATE}_1144_D.xls` | 1 | `data/db/option_hts/261007_1144_D.xls` | 480.5KB | 10-07 11:44 |
| `{DATE}_1215_D.xls` | 1 | `data/db/option_hts/261007_1215_D.xls` | 480.6KB | 10-07 12:15 |
| `{DATE}_DATA.log` | 1 | `logs/20261007_DATA.log` | 232.9KB | 10-07 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261007_DEBUG.log` | 139.5KB | 10-07 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261007_HEALTH.log` | 3.7KB | 10-07 11:41 |
| `{DATE}_HOGA.log` | 1 | `logs/20261007_HOGA.log` | 31.3MB | 10-07 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261007_LEARNING.log` | 176.3KB | 10-07 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20261007_MICRO.log` | 584.5KB | 10-07 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20261007_PROBE.log` | 55.7KB | 10-07 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261007_SIGNAL.log` | 428.1KB | 10-07 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261007_SYSTEM.log` | 602.4KB | 10-07 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20261007_TRADE.log` | 21.6KB | 10-07 12:15 |
| `{DATE}_WARN.log` | 1 | `logs/20261007_WARN.log` | 411.6KB | 10-07 12:27 |

## 2. 코드·커밋 상태

- HEAD `5cf61ee` · 브랜치 `v9-dev` · 미커밋 68건 · 실질 변경 10건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 10 · 미추적 58 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261007.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md`, `docs/정기점검/수익률향상_누적대장.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.3초(`git status --porcelain`)
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
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
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
?? docs/신동거래/일일/신동_일일_MW0601_20261006.md
?? docs/신동거래/일일/신동_일일_MW0601_20261006.svg
?? docs/정기점검/_tmp_ledger_append_20261002.md
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261002.md
?? docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/featureset_health_report_20261002.md
… 외 28건
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

_본문 미열람(설정): `20261007_HOGA.log` 31.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `20261007_MICRO.log`, `20261007_DATA.log`, `20261007_PROBE.log`, `launcher_20261007_084001_19477.log`, `20261007_DEBUG.log`, `shindong2_20261007.log`, `mainstall_traceback_20261007.log`, `freeze_sentinel_20261007.log`_

### `logs/20261007_TRADE.log` — 21.6KB · 150행 · 최종 12:15:00

- 형식 평문 · 시각 인식 150행 · INFO=150

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-07 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-07 09:32:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-07 09:33:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-07 09:38:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,439,402) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-10-07 11:40:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 1계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-07 12:11:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-10-07 12:12:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-10-07 12:14:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-10-07 12:15:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,324,404) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
```

</details>

**채널** — `TRADE`×150

**컴포넌트 상위 15** — `Sizer`×37, `Chejan`×32, `Position`×21, `JointGateBlock 차단`×13, `주문요청`×13, `체결진입`×6, `진입체크`×5, `TickStop-S0C`×5, `청산 완료`×5, `TickTP1`×4, `체결진입보정`×3, `TP1 부분청산`×3, `ProfitGuard`×1, `모드필터 차단`×1, `손절1차 조기축소`×1

### `logs/20261007_WARN.log` — 411.6KB · 1838행 · 최종 12:27:08

- 형식 평문 · 시각 인식 1838행 · ERROR=2, WARNING=1836

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-10-07 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-07 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-07 12:27:00 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 122.9ms | size=1955x1124 candles=223 grid=36.8 spans=12.7 candles=14.2 dir=1.1 regime=9.6 markers=45.8 axes=1.0 cross=0.0 | slow_cnt=1402 total_cnt=1543 overlay_cnt=17590
2026-10-07 12:27:08 [WARNING] SYSTEM: [OptionFlowChart] 그리기 74.9ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 916x1001
2026-10-07 12:27:08 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 98.5ms | size=1955x1124 candles=223 grid=32.0 spans=12.9 candles=8.3 dir=0.8 regime=4.8 markers=37.3 axes=0.6 cross=0.0 | slow_cnt=1403 total_cnt=1544 overlay_cnt=17604
2026-10-07 12:27:20 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 121.7ms | size=1955x1124 candles=223 grid=38.7 spans=16.1 candles=9.2 dir=1.0 regime=6.6 markers=47.8 axes=0.6 cross=0.0 | slow_cnt=1404 total_cnt=1545 overlay_cnt=17620
2026-10-07 12:27:31 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 106.8ms | size=1955x1124 candles=223 grid=37.9 spans=11.7 candles=9.2 dir=0.8 regime=5.4 markers=39.4 axes=0.8 cross=0.0 | slow_cnt=1405 total_cnt=1546 overlay_cnt=17634
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `LiveDBG` | 2 | 11:21:18 | 11:25:24 | _tick_header 간격 18204ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=18204 band=ALERT since_pipe_s=10.0 |

<details><summary>ERROR/LiveDBG 원문 2건</summary>

```
2026-10-07 11:21:18 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 18204ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=18204 band=ALERT since_pipe_s=10.0
2026-10-07 11:25:24 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 23750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=23750 band=ALERT since_pipe_s=0.4
```

</details>

**WARNING — 태그 37종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1405 | 08:52:24 | 12:27:31 | paintEvent slow 41.9ms | size=1955x1124 candles=8 grid=21.2 spans=0.0 candles=0.3 dir=0.0 regime=0.0 markers=0.0 axes=19.2 cross=0.0 | slow_cnt=1 total_cnt=3 overlay_cnt=2 |
| `LiveDBG` | 144 | 08:41:07 | 12:22:08 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 36 | 08:41:17 | 12:27:08 | 그리기 59.1ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 856x1001 |
| `ChejanFlow` | 32 | 10:20:01 | 11:19:17 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1438' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=10:20:00.956' | positi… |
| `ChejanMatch` | 32 | 10:20:01 | 11:19:17 | order_no='1438' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1438 reason=진입 req_at=10:20:00.956' | pending_matched=True |
| `PendingOrder` | 28 | 10:20:00 | 11:19:17 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1091.52, 'reason': '진입', 'hint_source': '', 'atr': 1.2886, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `PipePerf` | 16 | 09:32:01 | 11:40:01 | total=1064ms | S0=1ms S1=48ms S2=22ms S3=0ms S4=149ms S5=155ms S6=142ms S7=546ms S8=2ms |
| `CB⑤` | 16 | 09:32:01 | 11:40:01 | 파이프라인 1064ms 경고 (기준 1000ms) |
| `Health` | 11 | 09:32:01 | 11:40:01 | level=WARNING degraded=OFF | latency=1064ms | quality=1.00 | cache_age=137s | exceptions_10m=0 |
| `ExitCooldown` | 10 | 10:20:23 | 11:19:17 | 하드스톱(틱) 후 2분 재진입 금지 (until 10:22:23) |
| `EntryFillFlow` | 9 | 10:20:01 | 11:19:01 | actual_side='SHORT' | after='SHORT 2계약 @ 1091.36' | applied_side='SHORT' | before='SHORT 2계약 @ 1091.52' | fill_no='' | fill_price=1091.36 | fill_qty=1 | order_no='1438' | pending='ENTRY:SHORT qty=2 filled=1 order_no=1438 reason=진입 req_at=1… |
| `SHAP` | 9 | 10:45:01 | 12:20:01 | 슬로우 감지 1018ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |

**채널** — `SYSTEM`×1827, `HEALTH`×11

**컴포넌트 상위 15** — `ChartDBG`×1405, `LiveDBG`×146, `OptionFlowChart`×36, `ChejanFlow`×32, `ChejanMatch`×32, `PendingOrder`×28, `PipePerf`×16, `CB⑤`×16, `Health`×11, `ExitCooldown`×10, `EntryFillFlow`×9, `SHAP`×9, `ScalerRefresh`×8, `MainStallTrace`×7, `SessionBackfill`×6

### `logs/20261007_SYSTEM.log` — 602.4KB · 3941행 · 최종 12:27:08

- 형식 평문 · 시각 인식 3934행 · INFO=3934, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=12412 | 행감지=30s all_threads=True
2026-10-07 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-07 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-07 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-07 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-07 12:27:08 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-199,foreign:-2263,institution:+2199} amt_mn={individual:-54995,foreign:-618252,institution:+601305}
2026-10-07 12:27:08 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-199,foreign:-2263,institution:+2199} amt_mn={individual:-54995,foreign:-618252,institution:+601305}
2026-10-07 12:27:08 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-76413 nonarb=-1132808
2026-10-07 12:27:08 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-76413 nonarb=-1132808
2026-10-07 12:27:08 [INFO] SYSTEM: [CybosRT-TICK] #77200 code=A056A raw_time=122708 parsed=12:27:08 price=1086.34 vol=1 bid1=1086.30 ask1=1086.34 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×3934

**컴포넌트 상위 15** — `CybosInvestorRaw`×828, `CybosRT-TICK`×777, `PumpGuard`×393, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `CybosEvent`×64, `System`×59, `BalanceUI`×58, `MicroRegime`×55, `OptionChain`×44, `CybosDailyPnl`×42

### `logs/20261007_SIGNAL.log` — 428.1KB · 3618행 · 최종 12:27:00

- 형식 평문 · 시각 인식 3618행 · WARNING=1617, INFO=2001

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-10-07 12:27:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-10-07 12:27:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=33.5% grade=X regime=RISK_ON
2026-10-07 12:27:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-10-07 12:27:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=33.5% grade=X micro=추세장
2026-10-07 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.335<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1176 | 09:00:02 | 12:18:00 | 1m 'macro_vix' scale=0.0163 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 174 | 09:00:00 | 12:22:01 | ts=08:59 horizon=1m age=1m max_z=-7.21(institution_futures_net) extreme=2 adj=2 |
| `Model` | 144 | 09:00:00 | 12:15:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 62 | 09:06:00 | 12:23:02 | CORE VWAP ✗ → 강제 X등급 (pass_count=9, group=short) | VWAP pos=+0.897 need <0 (SHORT) bull_exh=0.00 |
| `WeightCollapse` | 49 | 09:07:00 | 12:22:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 9 | 09:35:00 | 12:20:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 2 | 10:07:00 | 10:12:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `MetaGate` | 1 | 11:15:00 | 11:15:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×3618

**컴포넌트 상위 15** — `ScalerFloor`×1194, `SIGNAL`×416, `MetaGate`×230, `Ensemble`×211, `FQAdj`×207, `ScalerMonitor`×174, `ZeroDiag`×160, `Model`×150, `Checklist`×133, `ATR-Horizon`×97, `차단`×75, `ToxicityGate`×67, `InstabilityGate`×63, `MicroRegime`×55, `WeightCollapse`×49

### `logs/20261007_LEARNING.log` — 176.3KB · 1633행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1633행 · WARNING=141, INFO=1492

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-10-07 08:40:49 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00081 auc=0.557 out_max=0.3115 (n=90) → 보정 재적용
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3115 < conf_floor=0.3300 (span=0.00081 auc=0.557 out_max=0.3115, 기저율=0.3111 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-07 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0413% buf_n=20 nonzero=20 prev_p=1085.88 cur_p=1086.28
2026-10-07 12:27:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=36.2% 예측=DN 실제=UP)
2026-10-07 12:27:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=33.3% 예측=UP 실제=FL)
2026-10-07 12:27:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=60.1% 예측=UP 실제=FL)
2026-10-07 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=12.5%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 48 | 08:40:49 | 11:29:00 | 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 40 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 19 | 08:40:49 | 08:40:57 | 축퇴 감지 — span=0.00008 auc=0.523 out_max=0.3500 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 17 | 08:40:50 | 08:40:57 | 축퇴 감지 — span=0.00071 auc=0.518 out_max=0.3623 (기준 auc<0.53 and span<0.020, 기저율=0.3619 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:10m` | 12 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00033 auc=0.505 out_max=0.4377 (기준 auc<0.53 and span<0.020, 기저율=0.4375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 3 | 08:40:50 | 08:40:56 | 축퇴 감지 — span=0.00004 auc=0.485 out_max=0.3125 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:58 | 08:40:58 | 복원한 보정기가 축퇴 상태 — span=0.00502 auc=0.442 out_max=0.3779 (n=2811) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 11:21:00 | 11:21:00 | total=522ms raw_fetch=37ms pred_select=31ms pred_update=295ms pred_insert=0ms verified=3 |

**채널** — `LEARNING`×1633

**컴포넌트 상위 15** — `LEARNING`×663, `SGD`×207, `sigma`×195, `Bias⚠`×98, `Calibration:30m`×94, `Calibration:1m`×79, `Bias`×66, `MetaConf`×39, `Calibration:3m`×36, `Calibration:5m`×34, `ScalerWarmup`×30, `OnlineLearner`×29, `BiasReset`×23, `Calibration:10m`×22, `Calibration:15m`×5

### `logs/20261007_HEALTH.log` — 3.7KB · 23행 · 최종 11:41:00

- 형식 평문 · 시각 인식 23행 · WARNING=11, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 388ms (표본 20분)
2026-10-07 09:32:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1064ms | quality=1.00 | cache_age=137s | exceptions_10m=0
2026-10-07 09:33:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=318ms | quality=1.00 | cache_age=12s | exceptions_10m=0
2026-10-07 09:44:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=290ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-10-07 09:45:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=308ms | quality=1.00 | cache_age=58s | exceptions_10m=0
  …
2026-10-07 11:25:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=954ms | quality=1.00 | cache_age=111s | exceptions_10m=3 | exc_tags=[ExitCooldown]×1 [SHAP]×1 [SingleContractTP1]×1
2026-10-07 11:30:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2066ms | quality=1.00 | cache_age=45s | exceptions_10m=3 | exc_tags=[SHAP]×2 [CB③-P4]×1
2026-10-07 11:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=367ms | quality=1.00 | cache_age=103s | exceptions_10m=3 | exc_tags=[SHAP]×2 [CB③-P4]×1
2026-10-07 11:40:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1013ms | quality=1.00 | cache_age=94s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-07 11:41:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=337ms | quality=1.00 | cache_age=153s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 11 | 09:32:01 | 11:40:01 | level=WARNING degraded=OFF | latency=1064ms | quality=1.00 | cache_age=137s | exceptions_10m=0 |

**채널** — `HEALTH`×23

**컴포넌트 상위 15** — `Health`×22, `HealthTrend`×1

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

### `logs/retrain_intraday_20260805_100701.log` — 4.5KB · 39행 · 최종 10:07:45

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-05 10:07:01,154 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-05 10:07:01,154 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-05 10:07:01,155 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-05 10:07:01,155 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a510f41e.json
2026-08-05 10:07:04,171 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-05 10:07:45,703 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.06s | old_acc=0.4039)
2026-08-05 10:07:45,752 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-05 10:07:45,753 [INFO] LEARNING: [Retrain] 완료 | 41.6초 | 성공=6/6 호라이즌
2026-08-05 10:07:45,754 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 44.6s 데이터=4800행
2026-08-05 10:07:45,756 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a510f41e.json
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
| 차단(`[차단]`) | 75 |
| 사이저 호출(`[Sizer]`) | 37 |

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

사이저 출력 계약수 — **1계약**×8, **2계약**×6, **3계약**×23

실제 진입 계약수 — **1계약**×1, **2계약**×3

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×37

### 차단 사유 75건 · 46종

| 건수 | 사유 |
|---|---|
| 14 | 등급X — 미통과 항목: 2_confidence |
| 8 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 3 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 3 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 2 | ATR 0.98pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 1.00pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.65pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.3pt > ATR×5.0=9.1pt (시가=1085.04 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.7pt > ATR×5.0=8.6pt (시가=1085.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.6pt > ATR×5.0=8.4pt (시가=1085.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.7pt > ATR×5.0=8.2pt (시가=1085.04 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.7pt > ATR×5.0=7.3pt (시가=1085.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.0pt > ATR×5.0=7.3pt (시가=1085.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.1pt > ATR×5.0=7.7pt (시가=1085.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.0pt > ATR×5.0=8.3pt (시가=1085.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.5pt > ATR×5.0=6.8pt (시가=1085.04 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×14, `3_vwap`×7, `6_foreign`×7, `5_ofi`×2, `4_cvd`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 3건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×2
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-10-07 11:08:01, 현재 1…` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 31건 · 최대 23750ms · 5초 초과 7건

상위 — 23750ms, 18204ms, 13890ms, 6797ms, 6047ms, 6016ms, 5750ms, 4969ms

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

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261007_WARN.log`
```
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
--- PSI ×8(표본)
09:00:00 2026-10-07 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-07 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:10:00 2026-10-07 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:15:00 2026-10-07 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×1(표본)
11:11:12 2026-10-07 11:11:12 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-10-07 11:08:01, 현재 1회)
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

- 이 로그 생존구간: 08:40 ~ 12:15

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261007_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 23 | 08:52:24 [WARNING] _tick_header 간격 3391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3391 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 38 | 08:56:32 [WARNING] paintEvent slow 51.0ms | size=1955x1124 candles=12 grid=10.9 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers… |
| 10:00 | 장중 초반 | 5 | 09:54:07 [WARNING] paintEvent slow 63.5ms | size=1955x1124 candles=70 grid=26.8 spans=0.1 candles=2.7 dir=0.2 regime=3.4 markers… |
| 12:00 | 장중 중간점 | 127 | 11:54:01 [WARNING] paintEvent slow 98.6ms | size=1955x1124 candles=190 grid=33.8 spans=10.2 candles=8.4 dir=0.9 regime=4.4 marke… |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261007_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=12412 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 140 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 198 | 08:54:02 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 224 | 09:54:07 [INFO] rollover 연기 — 메인 펌프(BlockRequest 대기) 중 재진입 회피 (누적 87회, 재시도=호출부) |
| 12:00 | 장중 중간점 | 196 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261007_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 39 | 08:40:41 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.417 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 78 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 219 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 169 | 09:54:59 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m'] 중 미배포=['10m', '15m', '3m'] → flat_score=1.0 안전망 발동 (active_horizon… |
| 12:00 | 장중 중간점 | 106 | 11:54:00 [WARNING] 신뢰도 미달 34.6% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:27

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
| **오늘 20261007** | **12:27** | 로그 본문 |

- 델타 **-200분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치: F-1·F-2·F-3·F-4·F-6·A-3·G-3)
## 2026-10-07 (MW0601 664차 — 장전 점검)
### 증상/확인 대상
### 발견
### 결정
### Why
### How to apply
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
collection/cybos/api_connector.py` = 브로커 어댑터), F-7(ⓐⓑⓒ 사용자 선택).
3. **Why**: 계획만 쌓이고 3일째 미적용 항목(F-2·F-3)이 매 점검 반복 지적. A-3 은 "저장소 밖"이라는 오진으로 방치될 뻔했다.
4. **How to apply**: 새 기형 파일이 또 생기면 생성 도구가 `peter_month_report` 외의 경로라는 뜻 — 파일명 문자 코드부터 볼 것(U+F03A/F05C = 샌드박스 경로).
5. **검증**: `tests/test_661_postmarket_autofix_20261006.py` 15 passed, 관련 32파일 366 passed(py37_32). 커밋 `d30a9cd` 푸시 완료. 라이브 검증: 다음 장전 수집에서 diff 타임아웃 시 두 번째 호출 생략 확인(기한 10/7 장전).

## 2026-10-07 (MW0601 664차 — 장전 점검)

### 증상/확인 대상
오늘 장전 점검. 정본 SKILL.md(rev 2026-09-07, 538차)를 `.claude/skills/mireuk-daily-check/SKILL.md`에서 먼저 Read로 읽음 — 이 세션의 앱 저장 스킬 사본(rev 2026-08-26e)보다 한 세대 신선함을 확인, 정본 기준으로 진행. 모든 git 명령에 `--no-optional-locks` 적용. 병행 세션 확인 — 당일(10/7) 커밋 0건, 오늘자 다이제스트/리포트 신규 산출물이 이 세션 이전에 없음(병행 세션 없음). 브랜치 `v9-dev`(MW0601 정상) · HEAD `5cf61ee`. 인덱스락 없음(`index.lock.stale.5` 부스러기 1건만 잔존, 648-2 계승).

### 발견
① 부팅구간(08:40:44) access violation 3건, PID 12412, 스택 `main_dashboard.py:7249(_build)`→`:7103(__init__)`→`:8443(_build)`→`:8159(__init__)`(`_cb_origin` 체크박스 구간, 663-3과 동일 지점) — 09/17·09/28·09/29·09/30·10/01·10/02·10/05·10/06에 이어 **10/7로 9관측일째**. 정규장(09:00) 이후 0건. NEXT_TODO `D-661-1` 종결(재현 확인).
② `[SessionStateDrop]` 재현(08:41:08) — `data/session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date` 공백. `[PreRetrain]`이 EOD 마커 파일 폴백으로 정상 우회(08:55:08, 1영업일 전 10/6 EOD 성공 인식) — 실질 피해 없음. 근본원인 F-1(538차/538-4, `session_recovery_service.py:139-161`의 `increment_session()`이 다섯 키만 승계)은 여전히 "승인 재요청" 상태, 코드 미변경(직접 재확인). 오늘 리포트 1-2에 등록.
③ 663-4 라이브 검증(diff 타임아웃 시 second_diff_skipped 여부) — 오늘 git 호출 7회 중 타임아웃 0건으로 **검증 조건 미발생**. 성공/실패 판정 보류(G-3 확정판정 게이트 적용 — 조건 미충족 상태를 "통과"로 쓰지 않음).
④ 설정 불변식 전부 일치(24행 중 불일치 0건), 절대원칙 6종 중 오늘 판정 가능한 5종 정상, ①(오버나이트 금지)은 장후 판정 대상. 한시 예외 재검토 기한 도래 항목 없음(CB②는 2026-09-02 519차로 이미 복원 완료, "발동 1회 확인"만 상시 관측 중).
⑤ 미커밋 64건 중 실질 변경 8건(코드 0건) — 사용자에게 경로 명시 add 안내.

### 결정
- 오늘 신규 Fix 없음 — 기존 F-1(538-4)·663-3 계획이 그대로 유효, 사용자 승인/코드검토 대기.
- `.git/index.lock.stale.5`(생성 2026-09-27 23:59 UTC, 약 9일째) 커밋 비차단 확인 — 648-2 계승, 삭제는 Windows에서.

### Why
함정① 준수 — F-1(538차)과 F-1(663차, 서로 다른 항목)을 명확히 구분해 신규 Fix로 재상정하지 않음. G-3(확정판정 사전등록 수단 전부 충족) 준수 — 663-4는 조건 미발생을 "통과"로 쓰지 않고 판정 보류로 남김.

### How to apply
F-1(538-4) 승인 시 다음 장후 세션에서 `strategy/runtime/session_recovery_service.py:increment_session()`에 `_MARKER_KEYS` 승계 로직 추가. 663-3은 승인 불요 — 다음 장후 세션에서 `dashboard/main_dashboard.py:7240~7250` 직접 코드 검토.

### 검증
다음 날짜 전환(10/8 장전)에서 `[SessionStateDrop]` 재현 여부로 F-1(538-4) 미적용 지속 확인. `D-661-1` 10번째 관측일 여부는 10/8 장전에서 판정.

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

미완료 체크박스 **3027건** (끝에서 30건)
```
- [ ] **660-2 (P1, 장후 적용)** GBM 재학습 DB 로드 실패 시 `repr(e)` 로깅 추가(F-6) — 11:59 재학습 완전 실패(0<4800행, 메시지 공백) 재발 시 원인 확인용.
- [ ] **660-3 (P2, 장후 결정)** `run_microstructure_ab_backtest.py` guard_intraday 배선 여부 먼저 grep 확인(함정①) 후 F-7(2026-08-27 제안 ⓐⓑⓒ 중 택1) 적용 — 오늘 9회 비정상 종료(rc=3221225477/rc=1).
- [ ] **D-660-1 (10/7 수 장전, 관측)** 3차 장중 재시작 발생 여부·가동시간 추이(132분→67분 추세 지속 여부).
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
(수집기 git diff 타임아웃 개선) 여전히 미적용 — 다음 수집에서도 재발 가능.
- [ ] **O-u1 (지속, 다음 거래일)** 부팅구간 access violation — 10/6로 8관측일째, 정규장 중 재발 없음(1-2 변경 없음). 10/7(수) 9관측일째 재현 여부 확인.
- [ ] **O-u5 (지속→1-10으로 대체)** 기형 파일 — 1건→2건 증가. 이 항목은 1-10으로 추적을 넘긴다.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` 부스러기 — 장후 수집 중 8개 생성됐다가 16:2X 재확인 시 1개로 자연 감소. Windows에서 남은 1개 `--reclaim` 필요.
- [ ] **D-661-1 (10/7 수 장전, 관측)** 부팅구간 access violation 9관측일째 재현 여부.
- [ ] **D-661-2 (10/7 수 장후, 관측)** 진입후보 가능시간(O-t1, 오늘 26분·5일평균 37분·하한 60분) 다음날도 하한 미달 지속되는지.
- [ ] **D-661-3 (관측)** 기형 파일(1-10) 세 번째 발생 여부.
- [ ] **D-661-4 (관측)** `.git/index.lock` — F-1 미반영 상태에서 다음 수집도 재발하는지.
- [ ] **사용자 조치 대기 — Fix 적용 승인** F-1~F-7 전부 계획만 세워져 있고 미적용(장전·장중·장후 공통 규약 — 이 점검 세션은 코드를 변경하지 않음). 검토 후 별도 세션에서 적용 지시 필요.

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

### `data/heartbeat_MW0601_20261007.json` — 243B · 10-07 12:26:45
```json
{
 "pid": 12412,
 "written_at": "2026-10-07T12:27:15",
 "beat_epoch": 1791343633.2424188,
 "beat_age_sec": 2.3,
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

- 파일 최종 기록: **10-07 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-07)과 일치 |
|---|---|---|
| `date` | 2026-10-07 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-07 08:55:08 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-06) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-07 08:55:08 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-06) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:26** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 222 |
| `session_bars` 당일 행수 | 222 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 162봉** (`session_bars` 에도 없음): 12:27, 12:28, 12:29, 12:30, 12:31, 12:32, 12:33, 12:34, 12:35, 12:36, 12:37, 12:38, 12:39, 12:40, 12:41, 12:42, 12:43, 12:44, 12:45, 12:46

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
| 12412 | 08:40:44 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 200개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261007-점검리포트.md` | 20.8KB | 10-07 09:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_pre.md` | 60.1KB | 10-07 08:59 |
| `docs/정기점검/매일점검/MW0601-20261006-점검리포트.md` | 87.4KB | 10-06 17:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_post.md` | 86.9KB | 10-06 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_intra.md` | 76.7KB | 10-06 12:32 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_pre.md` | 63.0KB | 10-06 09:00 |
| `docs/정기점검/매일점검/MW0601-20261005-점검리포트.md` | 36.6KB | 10-06 08:01 |
| `docs/정기점검/매일점검/evidence_MW0601-20261005_pre.md` | 57.6KB | 10-05 09:00 |

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

1. `logs/20261007_WARN.log`: ERROR 이상 2건
2. `logs/20261007_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
3. `logs/20261007_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. 메인 스레드 정지 5초 초과 **7건** (최대 23750ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20261007_SYSTEM.log`: **ConstOut** 8건(표본)
7. `logs/20261007_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20261007_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20261007_LEARNING.log`: **축퇴** 8건(표본)
10. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
11. 미커밋 변경 68건 (실질 10건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261007*.log` (Windows) / `grep 강제청산 logs/*20261007*.log`*