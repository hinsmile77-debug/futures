# 미륵이 증거 다이제스트 — 2026-10-12 / PRE

- 생성 2026-10-12 09:01:03 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01xxasnnhvijme5j4jb7ie7t/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261012` · `2026-10-12` · `261012` · `1012`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261012.log` | 124B | 10-12 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261012.log` | 140B | 10-12 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261012.json` | 242B | 10-12 09:00 |
| `launcher_{DATE}_084000_21183.log` | 1 | `logs/Mireuk_batch/launcher_20261012_084000_21183.log` | 73.8KB | 10-12 09:01 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261012.log` | 109B | 10-12 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261012.log` | 36B | 10-12 08:40 |
| `retrain_intraday_20260706_{DATE}58.log` | 1 | `logs/retrain_intraday_20260706_101258.log` | 4.6KB | 07-06 10:13 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261012.log` | 2.2KB | 10-12 08:54 |
| `{DATE}_DATA.log` | 1 | `logs/20261012_DATA.log` | 1.3KB | 10-12 09:01 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261012_DEBUG.log` | 1.2KB | 10-12 09:01 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261012_HEALTH.log` | 278B | 10-12 09:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20261012_HOGA.log` | 1.7MB | 10-12 09:01 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261012_LEARNING.log` | 52.0KB | 10-12 09:01 |
| `{DATE}_MICRO.log` | 1 | `logs/20261012_MICRO.log` | 39.3KB | 10-12 09:01 |
| `{DATE}_PROBE.log` | 1 | `logs/20261012_PROBE.log` | 12.1KB | 10-12 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261012_SIGNAL.log` | 24.1KB | 10-12 09:01 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261012_SYSTEM.log` | 31.6KB | 10-12 09:01 |
| `{DATE}_TRADE.log` | 1 | `logs/20261012_TRADE.log` | 167B | 10-12 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261012_WARN.log` | 3.5KB | 10-12 09:00 |

## 2. 코드·커밋 상태

- HEAD `0b73a74` · 브랜치 `v9-dev` · 미커밋 103건 · 실질 변경 13건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 13 · 미추적 90 · 삭제 12 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261012.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md` … 외 1개
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 6.4초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
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
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_pre.md
?? dev_memory/_tmp_append_nexttodo_20261009_intra.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_전일보유_맥점되돌림_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자흐름_맥점관계_MW0601-20261002.md
?? docs/미륵이고도화3/외인선물순매수_수집현황_조사_MW0601-20261002.md
?? docs/미륵이고도화3/위클리먼스리_선물추종_주체비중_일별_MW0601-20260921-20261002.md
?? docs/미륵이고도화3/피터2/live/
… 외 63건
```

**당일(2026-10-12) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
0b73a74 [MW0601] 679차: 맥점 사다리 자동기동 예약작업 — 월–금 08:44, 휴장일 건너뜀 · 매일 새로 기동
b5c7df0 [MW0601] 678차 후속: dev 배포 기록(3db460b)
9114943 [MW0601] 678차: 신동2 사전등록 개정 v2(위클리 원천·금액 단위) + 사다리 시인성(시간 창·방향 영역·개요)
b7a59cc [MW0601] 677차 후속: dev 이식 기록(37b3877)
bb66c99 [MW0601] 677차: 피터2 백필 — 실거래 개시(10/12) 이전 손익을 손익추이·손익추이2 에 올린다
6cb4c04 [MW0601] 676차(675차 후속): 장후 자동조치 — F-1 재진단 · G-1 리포트 append 마커
7235337 [MW0601] CREON HTS 자동기동: Cybos Plus → 미륵이 → CREON 순서 보장
7240653 [MW0601] 672차 후속2: dev 배포 기록(a18b016)
5bfeadd [MW0601] 672차 후속: 신동2 프롬프트.txt 10/8 추가분(학습 사이클 지시 원문)
8ea6f6e [MW0601] 672차: 신동2 학습 사이클 — 예측→실행→평가·반성→레슨런→개선 예측 (evaluate·feedback·lesson·trend·brief)
73cffd1 [MW0601] 671차 후속: 장후 자동조치 기록 — F-10 · G-1 결과 · 1-4 원인 단서
dd37273 [MW0601] 671차 후속: 장후 자동조치 — F-10 · 장전 고도화2 · 장후 G-1
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

_본문 미열람(설정): `20261012_HOGA.log` 1.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `20261012_DATA.log`, `20261012_PROBE.log`, `launcher_20261012_084000_21183.log`, `20261012_DEBUG.log`, `shindong2_20261012.log`, `freeze_sentinel_20261012.log`, `force_flat_guard_20261012.log`, `maekjeom_ladder_20261012.log`_

### `logs/20261012_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-12 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-12 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-12 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261012_WARN.log` — 3.5KB · 24행 · 최종 09:00:02

- 형식 평문 · 시각 인식 24행 · WARNING=24

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-10-12 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-12 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-12 09:00:01 [WARNING] SYSTEM: [PipePerf] total=1059ms | S0=2ms S1=16ms S2=0ms S3=0ms S4=92ms S5=772ms S6=157ms S7=14ms S8=4ms
2026-10-12 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0
2026-10-12 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1059ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-10-12 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1059ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-10-12 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.1
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 11 | 08:41:08 | 09:00:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `Peter2` | 2 | 08:41:14 | 08:41:14 | 기동 date=2026-10-12 offset=-4.88 src=prev_day:2026-10-08 safe=False 복원트윗=0 집행이력=0 손절=0 |
| `OptionFlowChart` | 2 | 08:41:19 | 08:47:58 | 그리기 71.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 889x1001 |
| `Canary` | 2 | 08:55:09 | 08:55:09 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1059ms | S0=2ms S1=16ms S2=0ms S3=0ms S4=92ms S5=772ms S6=157ms S7=14ms S8=4ms |
| `CB⑤` | 2 | 09:00:01 | 09:00:01 | 파이프라인 1059ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0 |

**채널** — `SYSTEM`×23, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×11, `출처축`×2, `Peter2`×2, `OptionFlowChart`×2, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1

### `logs/20261012_SYSTEM.log` — 31.6KB · 246행 · 최종 09:01:02

- 형식 평문 · 시각 인식 239행 · INFO=239, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15168 | 행감지=30s all_threads=True
2026-10-12 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.42s | predictions=0.05s trades=0.20s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-12 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-12 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-12 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-12 09:01:06 [INFO] SYSTEM: [CybosRT-TICK] #3600 code=A056B raw_time=90106 parsed=09:01:06 price=1039.38 vol=1 bid1=1039.38 ask1=1039.54 flag=50 side=SELL anchor=0/1
2026-10-12 09:01:08 [INFO] SYSTEM: [CybosRT-TICK] #3700 code=A056B raw_time=90108 parsed=09:01:08 price=1039.70 vol=1 bid1=1039.68 ask1=1039.82 flag=50 side=SELL anchor=0/1
2026-10-12 09:01:09 [INFO] SYSTEM: [System] 대기 중 | 장중 — Cybos 실시간 분봉 대기 중 (FutureCurOnly/FutureJpBid 수신 시 자동 진행) | 레짐=RISK_ON | 포지션=FLAT | 09:01:09
2026-10-12 09:01:13 [INFO] SYSTEM: [CybosRT-TICK] #3800 code=A056B raw_time=90113 parsed=09:01:13 price=1039.20 vol=2 bid1=1039.20 ask1=1039.22 flag=50 side=SELL anchor=0/2
2026-10-12 09:01:18 [INFO] SYSTEM: [CybosRT-TICK] #3900 code=A056B raw_time=90118 parsed=09:01:18 price=1037.90 vol=1 bid1=1037.98 ask1=1038.12 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×239

**컴포넌트 상위 15** — `CybosRT-TICK`×44, `CybosSub`×21, `System`×18, `TickUI`×16, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20261012_SIGNAL.log` — 24.1KB · 185행 · 최종 09:01:00

- 형식 평문 · 시각 인식 185행 · WARNING=84, INFO=101

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.411
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.403
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.399
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.407
  …
2026-10-12 09:01:00 [INFO] SIGNAL: [AutoMasked] 이상값 5개 즉시 격리 예측 (CORE 제외): ['mlofi_norm', 'program_non_arb_net', 'quality_investor_program_supported', 'quality_investor_reason_code', 'ret_1m']
2026-10-12 09:01:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.42→0.39 (완화)
2026-10-12 09:01:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-10-12 09:01:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.393) | 참고: 이상값피처(mlofi_norm(candidate),program_non_arb_net(candidate),quality_investor_program_supported(candidate))
2026-10-12 09:01:00 [INFO] SIGNAL: [SHS-EKS-Bar] GAP_OPEN #2 경과=580ms delayed=False policy_blocked=True conf=0.0% core측정=False core통과=False → conf_max 산입=False
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 48 | 09:00:01 | 09:00:01 | 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 18 | 08:45:09 | 08:45:09 | 1m CORE 'vwap_position' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:01:00 | 09:01:00 | 1m 극단 z-score 7개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:01:00 | 09:01:00 | ts=09:00 horizon=1m age=1m max_z=+5.18(volume_acceleration) extreme=7 adj=5 |

**채널** — `SIGNAL`×185

**컴포넌트 상위 15** — `ScalerFloor`×108, `ScalerRefresh`×25, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `SIGNAL`×4, `TimeRouter`×3, `FQAdj`×2, `ZeroDiag`×2, `SHS-EKS-Bar`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1

### `logs/20261012_LEARNING.log` — 52.0KB · 289행 · 최종 09:01:00

- 형식 평문 · 시각 인식 289행 · WARNING=139, INFO=150

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00133 auc=0.543 out_max=0.3734 (n=110) → 보정 재적용
  …
2026-10-12 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1034.26
2026-10-12 09:00:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-10-12 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1034.26 cur_p=1037.66
2026-10-12 09:01:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=44.9% 예측=DN 실제=UP)
2026-10-12 09:01:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 45 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 39 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 19 | 08:40:50 | 08:40:59 | 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 18 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.3005 < conf_floor=0.3300 (span=0.00088 auc=0.534 out_max=0.3005, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 15 | 08:40:51 | 08:40:58 | 축퇴 감지 — span=0.00044 auc=0.490 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 2 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00081 auc=0.517 out_max=0.2629 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:59 | 08:40:59 | 복원한 보정기가 축퇴 상태 — span=0.01232 auc=0.468 out_max=0.4068 (n=3107) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×289

**컴포넌트 상위 15** — `Calibration:30m`×90, `Calibration:1m`×77, `Calibration:3m`×36, `Calibration:10m`×35, `Calibration:5m`×28, `ScalerWarmup`×7, `Calibration:15m`×3, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `sigma`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/20261012_HEALTH.log` — 278B · 2행 · 최종 09:01:00

- 형식 평문 · 시각 인식 2행 · WARNING=1, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0
2026-10-12 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=591ms | quality=1.00 | cache_age=111s | exceptions_10m=0
  …
2026-10-12 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0
2026-10-12 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=591ms | quality=1.00 | cache_age=111s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0 |

**채널** — `HEALTH`×2

**컴포넌트 상위 15** — `Health`×2

### `logs/retrain_intraday_20260706_101258.log` — 4.6KB · 39행 · 최종 10:13:29

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-06 10:12:58,210 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-06 10:12:58,210 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-06 10:12:58,211 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-06 10:12:58,211 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_27a17224.json
2026-07-06 10:13:00,040 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-06 10:13:29,421 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.47s | old_acc=nan)
2026-07-06 10:13:29,424 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-06 10:13:29,424 [INFO] LEARNING: [Retrain] 완료 | 29.4초 | 성공=6/6 호라이즌
2026-07-06 10:13:29,426 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 31.2s 데이터=20000행
2026-07-06 10:13:29,427 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_27a17224.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/20261012_MICRO.log` — 39.3KB · 111행 · 최종 09:01:02

- 형식 평문 · 시각 인식 111행 · DEBUG=111

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1036.30/1 ask1=1036.62/2 mp={'microprice_tick': 1036.4067, 'midprice_tick': 1036.46, 'depth_bias_tick': 0.3072} mlofi_tick=None queue=None
2026-10-12 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1036.28/1 ask1=1036.56/2 mp={'microprice_tick': 1036.3734, 'midprice_tick': 1036.42, 'depth_bias_tick': 0.501} mlofi_tick=-12.6 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-10-12 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1036.28/1 ask1=1036.54/7 mp={'microprice_tick': 1036.3125, 'midprice_tick': 1036.41, 'depth_bias_tick': 0.1386} mlofi_tick=-9.0667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 5.0, 'bid_cancel_add_ratio'…
2026-10-12 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1036.28/1 ask1=1036.54/7 mp={'microprice_tick': 1036.3125, 'midprice_tick': 1036.41, 'depth_bias_tick': 0.1252} mlofi_tick=-0.25 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-10-12 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1036.28/1 ask1=1036.44/1 mp={'microprice_tick': 1036.36, 'midprice_tick': 1036.36, 'depth_bias_tick': 0.575} mlofi_tick=-3.2333 queue={'depletion_bid': -0.0, 'depletion_ask': 6.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
  …
2026-10-12 09:01:06 [DEBUG] MICRO: [MICRO-TICK] #7100 bid1=1039.14/1 ask1=1039.36/1 mp={'microprice_tick': 1039.25, 'midprice_tick': 1039.25, 'depth_bias_tick': -0.4846} mlofi_tick=-10.3 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-10-12 09:01:09 [DEBUG] MICRO: [MICRO-TICK] #7200 bid1=1040.12/2 ask1=1040.32/1 mp={'microprice_tick': 1040.2533, 'midprice_tick': 1040.22, 'depth_bias_tick': 0.226} mlofi_tick=-3.0333 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-10-12 09:01:14 [DEBUG] MICRO: [MICRO-TICK] #7300 bid1=1038.86/1 ask1=1038.92/17 mp={'microprice_tick': 1038.8633, 'midprice_tick': 1038.89, 'depth_bias_tick': -0.7637} mlofi_tick=0.4667 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-10-12 09:01:18 [DEBUG] MICRO: [MICRO-TICK] #7400 bid1=1037.58/1 ask1=1037.68/1 mp={'microprice_tick': 1037.63, 'midprice_tick': 1037.63, 'depth_bias_tick': -0.1464} mlofi_tick=5.0167 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-10-12 09:01:25 [DEBUG] MICRO: [MICRO-TICK] #7500 bid1=1036.12/1 ask1=1036.42/1 mp={'microprice_tick': 1036.27, 'midprice_tick': 1036.27, 'depth_bias_tick': -0.0529} mlofi_tick=-3.5333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
```

</details>

**채널** — `MICRO`×111

**컴포넌트 상위 15** — `MICRO-TICK`×95, `MICRO-MINUTE`×16

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

### 메인 스레드 블로킹 2건 · 최대 4203ms · 5초 초과 0건

상위 — 4203ms, 2594ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261012_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:41:12 2026-10-12 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4203 band=INFO since_pipe_s=NA
09:00:02 2026-10-12 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.1
```

### `logs/20261012_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-10-12 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
```

### `logs/20261012_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.411
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.403
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.399
```

### `logs/20261012_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00133 auc=0.543 out_max=0.3734 (n=110) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261012_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261012_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 14 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:51:32 [WARNING] ChallengerPanel.refresh slow 297ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261012_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 97 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=15168 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 128 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 95 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261012_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:09 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 128 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 127 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |

- 이 로그 생존구간: 08:40 ~ 09:01

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
| **오늘 20261012** | **09:01** | 로그 본문 |

- 델타 **-406분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.5MB · 마지막 갱신 2026-10-10 09:43

최근 헤딩 8개:
```
### Why
### How to apply
### 검증
### 병행 세션
## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치: F-1 재진단 · G-1 리포트 append 마커)
## 2026-10-09 (MW0601 677차 — 피터2 백필: 실거래 개시 이전 손익을 손익추이·손익추이2 에 올린다)
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2: 위클리 원천 · 먼스리 만기주 기권 · 옵션 금액 단위) — 🟡 **구현 · 라이브 미배포(사다리 서버 재기동 대기)**
## 2026-10-10 (MW0601 679차 — 맥점 사다리 자동기동 예약작업)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
아래는 납작 → **세로축을 창 안 캔들에 맞추는 것**이 핵심.
- 시간 창 60·120분·전체(+사용자 지정): Ctrl+휠 = 커서 기준 확대 · 드래그/Shift+휠 = 이동 · 더블클릭 = 전체 · ◀▶ = 반 창 · 최신(장중 추종). **그냥 휠은 가로채지 않는다**(긴 페이지 스크롤 보존).
  창 크기 버튼은 보던 창의 가운데를 유지. 날짜를 바꾸면 위치 초기화. 플롯 클립(라벨 열·분포는 제외), 분포 막대 높이 상한 16.
- 창 밖 맥점: 위·아래 가장자리에 가까운 3개 + `외 N개`, 전체 목록은 hover(계측 4원칙 ③).
- 방향 영역: 신동2 토글의 주체(전부 = AI → P → 기본). 전면 옅게(5.5%) + 바닥 리본 진하게 + 글자. 같은 방향 연속 구간 병합.
  **판단 기록 전 구간은 칠하지 않는다**(미측정 ≠ 관망) · legacy 섀도 기록 제외 · P 는 09:05 부터(세팅 전 = 관망).
  색 토큰 `--dir-buy/sell/flat` 라이트·다크 각각. 밴드(가로 띠)와 방향(세로 구간)은 모양으로 구분된다.
- 미니 개요: 하루 종가선 + 방향 리본 + 창 사각형(끌기 · 바깥 클릭 = 이동 · 전체에서 클릭 = 그 자리 60분).
- 검증: 헤드리스 Edge 스크린샷(전체·60·120·다크) · CDP 실입력 시험(Ctrl+휠 확대, 그냥 휠 = scrollY 147→247 창 불변, 드래그·Shift휠·◀·120분·더블클릭·개요·최신 전부 기대대로, page errors 0) · node --check · 테스트 91 pass.
**[678차 후속3 — Ctrl+휠 감도]** 사용자 「확대·축소가 너무 빠르다」. 원인: 이벤트마다 고정 ×1.25/×0.8 — 고해상도 휠·터치패드는 한 칸에 이벤트가 여러 번 와서 몇 배씩 튐 +
같은 프레임 이벤트가 갱신 전 `LV` 를 기준으로 서로 덮음. 수정: 배율 = exp(deltaY × ln(1.07)/100)(마우스 한 칸 7%, deltaMode 줄·쪽 환산), 이벤트당 ±12% 상한, 기준 창 = `winRange()`.
CDP 실측(421분에서): 한 칸 337 → **393분** · 다섯 칸 138 → **300분** · 터치패드형(−10×20) 364분 · 다섯 칸 확대 후 축소 = 421(대칭).
**배포 기록**: v9-dev `9114943` → dev **체리픽** `3db460b`(코드 충돌 0 — 672차 체리픽 이후 dev 의 MW0602 614차 「파일명 PC 파생」과 자동 병합. 충돌은 dev_memory 2개 파일 끝 덧붙이기뿐 — dev 내용 유지 + 678차 항목 추가로 해결).
임시 워크트리에서 작업(본 폴더 미추적 파일 무접촉). 검증 dev 위 테스트 86 pass · 6 skip(워크트리에 실데이터 DB 없음) · 사다리 스크립트 node --check 통과. 2026-10-10 푸시 완료.
⚠ MW0602 는 신동2 v2 규칙이 그 PC 데이터에도 적용된다(채점 재시작 10/12 동일) — 그 PC 의 사다리 서버도 재기동해야 반영.

## 2026-10-10 (MW0601 679차 — 맥점 사다리 자동기동 예약작업)

사용자 지시 「MAEKJEOM_LADDER.bat 를 작업스케줄러에 자동기동, 미륵이 작동을 반영해 시각 선택」.
- 등록: `\Mireuk\Mireuk_MaekjeomLadder` **월–금 08:44** · `scripts/maekjeom_ladder_task.ps1 -Action Register|Status|Unregister|Run [-NoGate]`(ASCII 전용).
- 시각 근거: 기존 08:35 Cybos Plus → 08:40 미륵이 → 08:42 CREON 기동 뒤, 08:45 첫 봉 · 08:50 맥점 · 08:52 신동2 장전 앞. 사다리는 읽기 전용·COM 없음이라 엔진과 경합 없음.
- 동작: ① 휴장일(KRX, `shindong2_live.py gate`) 건너뜀 ② 떠 있는 사다리 서버(명령줄 `maekjeom_ladder\server.py` 일치분과 그 bat 콘솔만)를 내리고 **매일 새로 기동** — 어제 띄운 서버의 모듈 캐시가 코드 변경을 가리는 문제(678차 v2 배포가 재기동을 요구) 해소
  ③ bat 을 최소화 콘솔로 기동(브라우저 열림). 늦게 부팅하면 그때라도 실행(StartWhenAvailable — 신동2 와 달리 늦은 사다리도 유용). 로그 `logs/maekjeom_ladder_YYYYMMDD.log`.
- 검증(10/10 토): 실작업 → `gate rc=3 휴장일 → skip` · 임시 시험작업(-NoGate, 검증 후 삭제) → 작업 종료(rc=0) 뒤 서버 생존·HTTP 200 · 재실행 시 기존 서버/콘솔 종료 후 재기동 확인.
- ⚠ 「다음 실행 08:44:44」 표시는 스케줄러 표시 특이점 — StartBoundary 는 `08:44:00`(신동2 08:52:52 와 같은 현상).
- ⚠ 다른 PC(MW0602)는 각자 등록해야 한다(예약작업은 PC 로컬).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-10-10 07:13

최근 헤딩 8개:
```
## 2026-10-08 (MW0601 670차 — 장중 점검)
## 2026-10-08 (MW0601 671차 — 장후 점검)
## 2026-10-08 (MW0601 672차 — 671차 후속 장후 자동조치)
## 2026-10-08 (MW0601 672차 — 신동2 학습 사이클)
## 2026-10-09 (MW0601 673차 — 장전 점검)
## 2026-10-09 (MW0601 674차 — 장중 점검)
## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치)
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2)
```

미완료 체크박스 **3087건** (끝에서 30건)
```
- [ ] **O-t1(신규)**: 10/9 장전 `trades.db`에서 `commission_rate_used`가 CYBOS(`9.8104e-05`)로 정상 복귀했는지 1차 확인 — 최우선 확인 항목.
- [ ] **O-t2(신규)**: 1-1·1-5와 같은 "원인불명 조용한 종료"가 10/9 이후에도 재현되는지 누적 관찰 — 재현되면 단일 결함으로 승격 검토.
- [ ] O-p1·1-2·663-1~4·F-1(538-4)·F-2·G-3 — 전부 지속, 변화 없음(기존 승인/판정 대기, 중복 기재 생략).
- [ ] **F-15 원인 단서 확보 → 승인만 남음**: 10-08 실측 `C:\CREON\STARTER\ncstarter.log` mtime **13:05:40** > `C:\Daishin\...` **08:35:49**, `MIREUK_BROKER_CHANNEL` 사용자·시스템 모두 미설정. ⇒ mtime 역전(CREON 기동)이 원인. 런처에 `…
- [ ] 기존 실패 테스트 2건(이번 변경 무관): `test_498::test_every_recon_log_is_registered`(`CybosInvestor` 대사 로그 RECON_INVENTORY 미등록 — `collection/cybos/investor_data.py`·`main.py`) · `test_457::test_db_fallback_c…
- [ ] 이월(하루 3건 상한): 장중 고도화1(수집기 §5 EKS 관망→해제→재학습 한 줄 요약) · 장중 고도화2(`[Peter2]` 태그 적신호 「메인 엔진 영향 없음」 자동 분류).
- [ ] F-11(종료 사유 3분류 로깅) — 위치 미특정, 조사 선행(C 보류). 장후 고도화2(마감 경고 휴대폰 알림)는 Slack 보류 결정으로 미착수.
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
-10-07 669차 등록, 재이월)**: 위와 같은 원인조사(런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 직접 Windows 이벤트 뷰어/작업 관리자 확인 필요) — 10/9 관측 기회 없음. **10/12 장전으로 이월.**
- [ ] **O-t1(2026-10-08 672차 등록, 재이월)**: `trades.db`의 `commission_rate_used`가 CYBOS(`9.8104e-05`)로 정상 복귀했는지 확인 — 10/9는 거래 자체가 없어 확인 대상 없음, 08:45 이후 라이브 DB 전수 스캔 금지 구간이기도 해 이번 세션 미실행. **10/12 거래 발생 이후 장후 점검으로 이월.**
- [ ] **O-t2(2026-10-08 672차 등록, 재이월)**: "원인불명 조용한 종료" 재현 누적 관찰 — 10/9는 시스템 미기동으로 관측 대상 없음. **10/12로 이월.**
- [ ] 미커밋 변경 96건(실질 12건) 정리 — `docs/정기점검/금요일점검/MW0601/` 삭제 12건이 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 — 저장소 정본 `rev: 2026-09-07`(538차) 대비 앱 사본이 `rev: 2026-08-26e`(499차)로 낡음. `save_skill overwrite: true` 필요(이 PC, MW0601 한정 — 함정③).

## 2026-10-09 (MW0601 674차 — 장중 점검)

- [ ] O-i1 (신규, 다음 거래일 판정): 2026-10-12(월) 장전·장중 예약작업이 각자 정해진 시각 근처(±30분)에 발동하는지 확인. 지연 없으면 1-1 ✅해소, 재발하면 `logs/claude_resume_*.log` 감시 스크립트·원격 기기 브리지 연결 상태 원인조사 착수.
- [ ] G-2 (고도화, 이번 주): `collect_evidence.py` §2(병행 세션 확인)에 "예약작업 예정 시각 대비 실제 fired_at 지연"을 자동으로 찍는 계측 추가(현재는 수집기가 `list_triggers` API에 접근하지 않아 수동 대조만 가능). 지연이 30분 이상이면 §11 자동 적신호로 승격.
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

### `data/heartbeat_MW0601_20261012.json` — 242B · 10-12 09:00:40
```json
{
 "pid": 15168,
 "written_at": "2026-10-12T09:01:10",
 "beat_epoch": 1791763269.3155317,
 "beat_age_sec": 0.8,
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

- 파일 최종 기록: **10-12 08:46:00**

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
| `raw_candles` 당일 max ts | **09:00** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 09:01 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 16 |
| `session_bars` 당일 행수 | 16 (기대 411) |

- 미도래 **368봉** (09:01~15:08) — 수집 시각 09:01 이후라 결손·영구결손에서 제외
- 결손 **0봉**

- 라이브 로그 대조: `logs/20261012_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 15168: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 15168 | 08:40:45 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 213개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261009-점검리포트.md` | 51.1KB | 10-09 17:29 |
| `docs/정기점검/매일점검/_tmp_append_post_20261009.md` | 19.2KB | 10-09 16:25 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_post.md` | 53.0KB | 10-09 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_pre.md` | 48.6KB | 10-09 15:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_intra.md` | 48.6KB | 10-09 15:34 |
| `docs/정기점검/매일점검/MW0601-20261008-점검리포트.md` | 87.1KB | 10-08 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20261008_post.md` | 99.0KB | 10-08 16:18 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261008.md` | 15.9KB | 10-08 12:38 |

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

1. `logs/20261012_LEARNING.log`: **축퇴** 8건(표본)
2. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
3. 미커밋 변경 103건 (실질 13건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261012*.log` (Windows) / `grep 강제청산 logs/*20261012*.log`*