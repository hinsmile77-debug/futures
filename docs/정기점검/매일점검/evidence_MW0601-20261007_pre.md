# 미륵이 증거 다이제스트 — 2026-10-07 / PRE

- 생성 2026-10-07 08:59:19 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01qurkkfzwyjtlo2bmbwz5qd/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261007` · `2026-10-07` · `261007` · `1007`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **18개** 파일 · 18개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261007.log` | 125B | 10-07 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261007.log` | 139B | 10-07 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261007.json` | 245B | 10-07 08:59 |
| `launcher_{DATE}_084001_19477.log` | 1 | `logs/Mireuk_batch/launcher_20261007_084001_19477.log` | 53.7KB | 10-07 08:58 |
| `retrain_intraday_20260701_{DATE}00.log` | 1 | `logs/retrain_intraday_20260701_100700.log` | 4.6KB | 07-01 10:07 |
| `retrain_intraday_20260805_{DATE}01.log` | 1 | `logs/retrain_intraday_20260805_100701.log` | 4.5KB | 08-05 10:07 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261007.log` | 1.9KB | 10-07 08:54 |
| `{DATE}_DATA.log` | 1 | `logs/20261007_DATA.log` | 892B | 10-07 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261007_DEBUG.log` | 0B | 10-07 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261007_HEALTH.log` | 0B | 10-07 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261007_HOGA.log` | 1.1MB | 10-07 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261007_LEARNING.log` | 50.9KB | 10-07 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20261007_MICRO.log` | 30.3KB | 10-07 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20261007_PROBE.log` | 12.1KB | 10-07 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261007_SIGNAL.log` | 5.0KB | 10-07 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261007_SYSTEM.log` | 26.7KB | 10-07 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261007_TRADE.log` | 167B | 10-07 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261007_WARN.log` | 5.3KB | 10-07 08:59 |

## 2. 코드·커밋 상태

- HEAD `5cf61ee` · 브랜치 `v9-dev` · 미커밋 64건 · 실질 변경 8건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 8 · 미추적 56 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261007.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md`, `docs/정기점검/수익률향상_누적대장.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.2초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
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
?? docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261002.json
?? docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261002.md
… 외 24건
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

_본문 미열람(설정): `20261007_HOGA.log` 1.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20261007_DATA.log`, `20261007_PROBE.log`, `launcher_20261007_084001_19477.log`, `shindong2_20261007.log`, `freeze_sentinel_20261007.log`, `force_flat_guard_20261007.log`_

### `logs/20261007_TRADE.log` — 167B · 2행 · 최종 08:41:04

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-07 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-07 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-07 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261007_WARN.log` — 5.3KB · 31행 · 최종 08:59:11

- 형식 평문 · 시각 인식 31행 · WARNING=31

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-10-07 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-10-07 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-07 08:41:08 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-07 08:57:59 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 35.2ms | size=1955x1124 candles=13 grid=10.8 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=22.5 cross=0.0 | slow_cnt=6 total_cnt=14 overlay_cnt=228
2026-10-07 08:59:00 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 60.5ms | size=1955x1124 candles=15 grid=29.9 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=28.6 cross=0.0 | slow_cnt=7 total_cnt=20 overlay_cnt=261
2026-10-07 08:59:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 41.6ms | size=1955x1124 candles=15 grid=11.8 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=27.8 cross=0.0 | slow_cnt=8 total_cnt=21 overlay_cnt=271
2026-10-07 08:59:21 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 30.0ms | size=1955x1124 candles=15 grid=11.3 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=16.7 cross=0.0 | slow_cnt=9 total_cnt=22 overlay_cnt=282
2026-10-07 08:59:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 42.4ms | size=1955x1124 candles=15 grid=15.1 spans=0.0 candles=0.7 dir=0.0 regime=0.0 markers=0.0 axes=25.2 cross=0.0 | slow_cnt=10 total_cnt=23 overlay_cnt=295
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 10 | 08:41:07 | 08:52:24 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChartDBG` | 10 | 08:52:24 | 08:59:32 | paintEvent slow 41.9ms | size=1955x1124 candles=8 grid=21.2 spans=0.0 candles=0.3 dir=0.0 regime=0.0 markers=0.0 axes=19.2 cross=0.0 | slow_cnt=1 total_cnt=3 overlay_cnt=2 |
| `SessionBackfill` | 6 | 08:41:38 | 08:41:38 | OHLCV 불일치 ts=2026-10-06 09:57:00 cols=['open'] existing_source=rt |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:08 | 08:41:08 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-10-06 → 2026-10-07)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `OptionFlowChart` | 1 | 08:41:17 | 08:41:17 | 그리기 59.1ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 856x1001 |

**채널** — `SYSTEM`×31

**컴포넌트 상위 15** — `LiveDBG`×10, `ChartDBG`×10, `SessionBackfill`×6, `출처축`×2, `SessionStateDrop`×2, `OptionFlowChart`×1

### `logs/20261007_SYSTEM.log` — 26.7KB · 206행 · 최종 08:59:16

- 형식 평문 · 시각 인식 200행 · INFO=200, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=12412 | 행감지=30s all_threads=True
2026-10-07 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.21s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-07 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-07 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-07 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-07 08:59:00 [INFO] SYSTEM: [PreMarket] Phase4 refit 기동 (14봉 z경고=4개)
2026-10-07 08:59:00 [INFO] SYSTEM: [PreMarket] Phase4 refit 완료 n=30봉 z경고 4→4개 | 잔존=atr,avg_volume,institution_futures_net,toxicity_queue_stress
2026-10-07 08:59:08 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=7개 (08:55 최종 4개 대비 +3) — 재측정만, 재적합 없음
2026-10-07 08:59:16 [INFO] SYSTEM: [CybosRT-TICK] #1700 code=A056A raw_time=85916 parsed=08:59:16 price=1084.84 vol=1 bid1=1084.74 ask1=1084.86 flag=49 side=BUY anchor=1/0
2026-10-07 08:59:26 [INFO] SYSTEM: [TickUI] alive ticks=1734 code=A056A close=1084.72
```

</details>

**채널** — `SYSTEM`×200

**컴포넌트 상위 15** — `CybosRT-TICK`×22, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `LEVELS 08:50`×4, `CybosInvestorRaw`×4

### `logs/20261007_SIGNAL.log` — 5.0KB · 43행 · 최종 08:59:00

- 형식 평문 · 시각 인식 43행 · INFO=43

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-10-07 08:46:00 [INFO] SIGNAL: [MA-cont] 2026-10-07 연속 MA 버퍼 프라이밍 61봉 (버퍼 61)
2026-10-07 08:48:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase1_3bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.01s
2026-10-07 08:50:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.16s
2026-10-07 08:55:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.01s
2026-10-07 08:59:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**채널** — `SIGNAL`×43

**컴포넌트 상위 15** — `ScalerFloor`×18, `DynMC`×7, `Model`×6, `ScalerRefresh`×5, `TimeRouter`×3, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1

### `logs/20261007_LEARNING.log` — 50.9KB · 281행 · 최종 08:59:00

- 형식 평문 · 시각 인식 281행 · WARNING=138, INFO=143

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-10-07 08:40:49 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00081 auc=0.557 out_max=0.3115 (n=90) → 보정 재적용
2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3115 < conf_floor=0.3300 (span=0.00081 auc=0.557 out_max=0.3115, 기저율=0.3111 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-07 08:48:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-07 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-07 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-07 08:55:08 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 혼합], total=619, ver=5)
2026-10-07 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 46 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 40 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 19 | 08:40:49 | 08:40:57 | 축퇴 감지 — span=0.00008 auc=0.523 out_max=0.3500 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 17 | 08:40:50 | 08:40:57 | 축퇴 감지 — span=0.00071 auc=0.518 out_max=0.3623 (기준 auc<0.53 and span<0.020, 기저율=0.3619 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:10m` | 12 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00033 auc=0.505 out_max=0.4377 (기준 auc<0.53 and span<0.020, 기저율=0.4375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 3 | 08:40:50 | 08:40:56 | 축퇴 감지 — span=0.00004 auc=0.485 out_max=0.3125 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:58 | 08:40:58 | 복원한 보정기가 축퇴 상태 — span=0.00502 auc=0.442 out_max=0.3779 (n=2811) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×281

**컴포넌트 상위 15** — `Calibration:30m`×92, `Calibration:1m`×79, `Calibration:3m`×36, `Calibration:5m`×33, `Calibration:10m`×22, `Calibration:15m`×5, `ScalerWarmup`×5, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

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

### `logs/20261007_MICRO.log` — 30.3KB · 83행 · 최종 08:59:18

- 형식 평문 · 시각 인식 83행 · DEBUG=83

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-07 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1083.84/1 ask1=1084.30/1 mp={'microprice_tick': 1084.07, 'midprice_tick': 1084.07, 'depth_bias_tick': -0.0069} mlofi_tick=None queue=None
2026-10-07 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1083.82/5 ask1=1084.24/2 mp={'microprice_tick': 1084.12, 'midprice_tick': 1084.03, 'depth_bias_tick': 0.298} mlofi_tick=-8.35 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 4.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -1.6…
2026-10-07 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1083.82/5 ask1=1084.24/4 mp={'microprice_tick': 1084.0533, 'midprice_tick': 1084.03, 'depth_bias_tick': 0.0} mlofi_tick=-4.1167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': -…
2026-10-07 08:45:08 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1083.84/1 ask1=1084.24/1 mp={'microprice_tick': 1084.04, 'midprice_tick': 1084.04, 'depth_bias_tick': 0.2564} mlofi_tick=10.15 queue={'depletion_bid': 4.0, 'depletion_ask': 3.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1.6…
2026-10-07 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1083.64/1 ask1=1084.22/3 mp={'microprice_tick': 1083.785, 'midprice_tick': 1083.93, 'depth_bias_tick': -0.3829} mlofi_tick=-9.65 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': …
  …
2026-10-07 08:58:48 [DEBUG] MICRO: [MICRO-TICK] #4600 bid1=1085.50/2 ask1=1085.70/1 mp={'microprice_tick': 1085.6333, 'midprice_tick': 1085.6, 'depth_bias_tick': 0.1253} mlofi_tick=8.3333 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-10-07 08:59:00 [DEBUG] MICRO: [MICRO-MINUTE] #14 ts=2026-10-07 08:58:00 close=1085.54 bias=0.003002 slope=-0.065302 depth_bias=0.0006 mlofi_norm=-0.015175 mlofi_pressure=-1 mlofi_slope=-13.821667 queue_signal=-0.0144 queue_ma=0.0003 queue_momentum=-0.0359 depletion=0.5028 refill=0.4972 imbalan…
2026-10-07 08:59:05 [DEBUG] MICRO: [MICRO-TICK] #4700 bid1=1085.06/2 ask1=1085.22/1 mp={'microprice_tick': 1085.1667, 'midprice_tick': 1085.14, 'depth_bias_tick': 0.2523} mlofi_tick=-9.0 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-10-07 08:59:18 [DEBUG] MICRO: [MICRO-TICK] #4800 bid1=1084.82/1 ask1=1085.00/1 mp={'microprice_tick': 1084.91, 'midprice_tick': 1084.91, 'depth_bias_tick': -0.2452} mlofi_tick=-3.7667 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-10-07 08:59:31 [DEBUG] MICRO: [MICRO-TICK] #4900 bid1=1084.34/1 ask1=1084.50/1 mp={'microprice_tick': 1084.42, 'midprice_tick': 1084.42, 'depth_bias_tick': -0.0092} mlofi_tick=-0.05 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
```

</details>

**채널** — `MICRO`×83

**컴포넌트 상위 15** — `MICRO-TICK`×69, `MICRO-MINUTE`×14

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

### 메인 스레드 블로킹 2건 · 최대 4016ms · 5초 초과 0건

상위 — 4016ms, 3391ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261007_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:41:11 2026-10-07 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4016 band=INFO since_pipe_s=NA
08:52:24 2026-10-07 08:52:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3391 band=INFO since_pipe_s=NA
```

### `logs/20261007_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
08:40:41 2026-10-07 08:40:41 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
```

### `logs/20261007_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00144 auc=0.494 out_max=0.4133 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
08:40:49 2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00062 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
08:40:49 2026-10-07 08:40:49 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00081 auc=0.557 out_max=0.3115 (n=90) → 보정 재적용
08:40:49 2026-10-07 08:40:49 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3115 < conf_floor=0.3300 (span=0.00081 auc=0.557 out_max=0.3115, 기저율=0.3111 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261007_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261007_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 20 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 11 | 08:52:24 [WARNING] _tick_header 간격 3391ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3391 band… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 08:56:32 [WARNING] paintEvent slow 51.0ms | size=1955x1124 candles=12 grid=10.9 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers… |

- 이 로그 생존구간: 08:41 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261007_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=12412 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 94 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 61 | 08:54:02 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261007_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 39 | 08:40:41 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.417 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 3 | 08:50:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:55:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] ela… |

- 이 로그 생존구간: 08:40 ~ 08:59

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
| **오늘 20261007** | **08:59** | 로그 본문 |

- 델타 **-408분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · 마지막 갱신 2026-10-06 17:34

최근 헤딩 8개:
```
## 2026-10-05 (MW0601 657차 — 장전 점검)
## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)
## 2026-10-06 (MW0601 659차 — 장전 점검)
### 2026-10-06 (MW0601 659차 후속 — 장전 세션 내 인덱스락 해소)
## 2026-10-06 (MW0601 660차 — 장중 점검)
## 2026-10-06 (MW0601 661차 — 장후 점검, 종합 완성본)
## 2026-10-06 (MW0601 662차 — 옵션 흐름 마감 재수집 실패 원인: dll_bootstrap 이 pywin32 두 벌 중 옛 판을 앞세움)
## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치: F-1·F-2·F-3·F-4·F-6·A-3·G-3)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
_537·test_655 포함 31 passed, `audit_dll_bootstrap --fail-on-gap` 결손 없음, 맨손 py37_32 BLAS(np.corrcoef) 정상.
   - 10/6 마감 구간은 `conda run` 수동 백필로 복구(16:07 까지, 순증 228행).
4. **같은 날 발견 — 10/6 월물 콜 마감 직전 외인 매수는 실제 매매(수집 오류 아님)**
   - 15:20 −393 → 15:45 **+8,433**(16:07 +9,405), 기관 −1,165 → −10,021, 개인 거의 불변. 장중 행 덮어쓰기 없음(09:30 −2,036 일치).
   - 9/21–10/2 같은 구간 외인 변화 ±200 이내 → 10/6 단독 이벤트. 15:21 부터 계약당 금액 0.3 → 2–3백만원 = 등가격 근처 콜. 행사가 분해는 9842 당일 마감본 필요(미확보).

## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치: F-1·F-2·F-3·F-4·F-6·A-3·G-3)

1. **증상**: 659–661차 점검이 F-1–F-7·A-1–A-3·G-3 을 계획만 등록. 1-1 인덱스락 3회, 1-10 루트 기형파일 2건, 1-7 `[Retrain] DB 로드 오류: ` 빈 메시지.
2. **원인·결정**
   - F-1: `git_change_profile` 이 `_files([])` 실패 뒤에도 `_files(["-w","--ignore-cr-at-eol"])` 를 호출. → 첫 실패면 즉시 반환, `second_diff_skipped=True`, `fail_reason` 에 생략 명시. 성공 경로 무변경.
   - F-2: 워킹트리만 손상(HEAD `49a2244` 원본 정상) → `git restore`. 커밋 없음.
   - F-3: `CLAUDE.md` joblib 1.1.1 → 1.1.0 (`requirements.txt:10`, py37_32 `joblib.__version__` 실측 1.1.0).
   - F-4/A-3: **근본 원인 확정 — 이 저장소 안이었다.** 파일명 2·3번째 문자가 U+F03A·U+F05C(= `:`·`\` 의 WSL/샌드박스 사설영역 매핑). 즉 리눅스 샌드박스에서 `tools/peter_month_report.py --out "C:\Users\...\Peter\트윗원문\....md"` 를 실행 → `\` 가 구분자가 아니라 `dirname==""` → cwd(저장소 루트)에 단일 파일. 날짜 토큰 `20261001_1006` 은 SKILL 템플릿 `<YYYYMMDD>_<MMDD>` 그대로라 "날짜 계산 어긋남"(1-10 근거)은 오독이었다. 조치: `mangled_out_path()` — `splitdrive` 후 dirname 이 비고 `^[A-Za-z]:?\\?Users` 면 rc=2 로 쓰지 않음(윈도우 `C:\Users\…` 는 오탐 없음, 드라이브 상대 `C:Users…` 는 잡음). peter-daily SKILL 예시 슬래시화. 기존 2파일은 삭제 대신 `Peter\트윗원문\피터리_10월매매_{20261001_1006,20261002_1002}.md` 로 이동(동명 파일 없음 확인). `.gitignore` `/C*Users82108*`.
   - F-6: `batch_retrainer.py` `[Retrain] DB 로드 오류: {e!r}` + `exc_info=True`. 반환 무변경.
   - G-3: `wer_crash_section` 이 `fau["launcher_restarts"]`(런처 미측정이면 None) 를 싣고 §11 이 `len>=2` 면 적신호.
   - A-1 불요: faulthandler 스택 8159(`__init__`)→8443(`PnlHistoryPanel()`)→7103→7249(`_cb_origin` 체크박스 루프)로 위젯이 이미 특정됨. 다음 조사는 로그 추가가 아니라 7240–7250 체크박스 생성 구간 직접 검토.
   - A-2 기반영: `retrain_eod.py:195` `[P8] session_state … 기록 완료` 존재.
   - 보류(C): F-5(`collection/cybos/api_connector.py` = 브로커 어댑터), F-7(ⓐⓑⓒ 사용자 선택).
3. **Why**: 계획만 쌓이고 3일째 미적용 항목(F-2·F-3)이 매 점검 반복 지적. A-3 은 "저장소 밖"이라는 오진으로 방치될 뻔했다.
4. **How to apply**: 새 기형 파일이 또 생기면 생성 도구가 `peter_month_report` 외의 경로라는 뜻 — 파일명 문자 코드부터 볼 것(U+F03A/F05C = 샌드박스 경로).
5. **검증**: `tests/test_661_postmarket_autofix_20261006.py` 15 passed, 관련 32파일 366 passed(py37_32). 커밋 `d30a9cd` 푸시 완료. 라이브 검증: 다음 장전 수집에서 diff 타임아웃 시 두 번째 호출 생략 확인(기한 10/7 장전).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-10-06 17:34

최근 헤딩 8개:
```
## 2026-10-04 (MW0601 655차 — 옵션 흐름 장 마감 재수집 보강)
## 2026-10-04 (MW0601 656차 — 맥점 × 옵션 사다리 로컬 서버)
## 2026-10-05 (MW0601 657차 — 장전 점검, 휴장일)
## 2026-10-05 (MW0601 658차 — 장후 점검, 휴장일)
## 2026-10-06 (MW0601 659차 — 장전 점검)
## 2026-10-06 (MW0601 660차 — 장중 점검)
## 2026-10-06 (MW0601 661차 — 장후 점검, 종합 완성본)
## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치)
```

미완료 체크박스 **3022건** (끝에서 30건)
```
- [ ] **O-p1 (신규, 오늘 밤 장후 판정)** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date` 키 공백 — 10/2 EOD 성공에도 불구 오늘 아침 비어 있었음(PreRetrain 폴백으로 실거래 영향 없음 확인). 오늘 밤 EOD 이후 이 키들이 2026-10-06으로 채…
- [ ] **O-u1 (지속, 다음 거래일)** 부팅구간 access violation — 10/6로 8관측일째(9/17·9/28·9/29·9/30·10/1·10/2·10/5·10/6). 다음 실거래일(10/7 수)에 9관측일째 재현 여부 확인.
- [ ] **O-u5 (지속)** 기형 파일 — 10/6에도 변동 없이 그대로.
- [ ] **648-2 (P2, 지속)** `.git/objects/**/tmp_obj_*` + 이름변경된 index.lock 부스러기 — T2 `.git/index.lock.stale_20261005001120_6`(24.1시간, 스테일 확정) 포함. Windows에서 `--reclaim` 필요.
- [ ] **660-1 (P1, 장후 적용)** `collection/cybos/api_connector.py:_pump_messages`(1729행)·launcher 재시작 로그에 진단 로그 추가(F-5) — 장중 2회 크래시·재시작(10:53·11:59) 원인 좁히기용.
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
ing(f"[Retrain] DB 로드 오류: {e}")` → `repr(e)` + `exc_info=True`로 변경(위치 확정, grep으로 실물 확인 완료).
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

### `data/heartbeat_MW0601_20261007.json` — 245B · 10-07 08:59:08
```json
{
 "pid": 12412,
 "written_at": "2026-10-07T08:59:08",
 "beat_epoch": 1791331148.6906595,
 "beat_age_sec": 0.2,
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
| `raw_candles` 당일 max ts | **08:58** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 14 |
| `session_bars` 당일 행수 | 14 (기대 411) |

- 결손 **0봉**
- ⚠ **영구 결손 370봉** (`session_bars` 에도 없음): 08:59, 09:00, 09:01, 09:02, 09:03, 09:04, 09:05, 09:06, 09:07, 09:08, 09:09, 09:10, 09:11, 09:12, 09:13, 09:14, 09:15, 09:16, 09:17, 09:18

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

### `docs/정기점검/매일점검` — 198개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261006-점검리포트.md` | 87.4KB | 10-06 17:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_post.md` | 86.9KB | 10-06 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_intra.md` | 76.7KB | 10-06 12:32 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_pre.md` | 63.0KB | 10-06 09:00 |
| `docs/정기점검/매일점검/MW0601-20261005-점검리포트.md` | 36.6KB | 10-06 08:01 |
| `docs/정기점검/매일점검/evidence_MW0601-20261005_pre.md` | 57.6KB | 10-05 09:00 |
| `docs/정기점검/매일점검/MW0601-20261002-점검리포트.md` | 91.4KB | 10-02 17:29 |
| `docs/정기점검/매일점검/_tmp_append_post_20261002.md` | 0B | 10-02 16:31 |

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

1. `logs/20261007_LEARNING.log`: **축퇴** 8건(표본)
2. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
3. 미커밋 변경 64건 (실질 8건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261007*.log` (Windows) / `grep 강제청산 logs/*20261007*.log`*