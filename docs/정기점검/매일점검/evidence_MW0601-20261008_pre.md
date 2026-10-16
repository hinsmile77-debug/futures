# 미륵이 증거 다이제스트 — 2026-10-08 / PRE

- 생성 2026-10-08 08:59:31 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01yasenaqr7di1ayvafd5r78/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261008` · `2026-10-08` · `261008` · `1008`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **20개** 파일 · 20개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `261007_{DATE}_D.xls` | 1 | `data/db/option_hts/261007_1008_D.xls` | 480.4KB | 10-07 10:06 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261008.log` | 269B | 10-08 08:28 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261008.log` | 125B | 10-08 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261008.log` | 140B | 10-08 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261008.json` | 244B | 10-08 08:59 |
| `launcher_{DATE}_084001_6711.log` | 1 | `logs/Mireuk_batch/launcher_20261008_084001_6711.log` | 93.0KB | 10-08 08:59 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261008.log` | 2.9KB | 10-08 08:41 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261008.log` | 6.8KB | 10-08 08:54 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261008.log` | 1.9KB | 10-08 08:55 |
| `{DATE}_DATA.log` | 1 | `logs/20261008_DATA.log` | 894B | 10-08 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261008_DEBUG.log` | 0B | 10-08 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261008_HEALTH.log` | 0B | 10-08 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261008_HOGA.log` | 620.4KB | 10-08 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261008_LEARNING.log` | 159.6KB | 10-08 08:58 |
| `{DATE}_MICRO.log` | 1 | `logs/20261008_MICRO.log` | 26.1KB | 10-08 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20261008_PROBE.log` | 12.4KB | 10-08 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261008_SIGNAL.log` | 20.9KB | 10-08 08:58 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261008_SYSTEM.log` | 41.5KB | 10-08 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261008_TRADE.log` | 501B | 10-08 08:55 |
| `{DATE}_WARN.log` | 1 | `logs/20261008_WARN.log` | 8.3KB | 10-08 08:55 |

## 2. 코드·커밋 상태

- HEAD `a0f179f` · 브랜치 `v9-dev` · 미커밋 74건 · 실질 변경 8건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 8 · 미추적 66 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261007.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md`, `docs/정기점검/수익률향상_누적대장.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.0초(`git status --porcelain`)
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
?? "MAEKJEOM_LADDER.bat - 바로 가기.lnk"
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
?? docs/정기점검/_tmp_ledger_append_20261002.md
… 외 34건
```

**당일(2026-10-08) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
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
f9d4b64 [MW0601] 662차 후속3: 신동2 — 피터 진입(1116)·청산가(1095) 딥다이브 + 섀도 P2·P3 + S1·E2 기록
9f993ea [MW0601] 662차 후속2: 신동2 문서 폴더 통합 — 미래예측 → docs/미륵이고도화3/신동2
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

_본문 미열람(설정): `20261008_HOGA.log` 620.4KB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `launcher_20261008_084001_6711.log`, `peter2_receiver_20261008.log`, `mainstall_traceback_20261008.log`, `shindong2_20261008.log`, `claude_resume_20261008.log`, `freeze_sentinel_20261008.log`, `force_flat_guard_20261008.log`_

### `logs/20261008_TRADE.log` — 501B · 6행 · 최종 08:55:03

- 형식 평문 · 시각 인식 6행 · INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:41:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:41:15 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:49:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:49:11 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:54:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-10-08 08:41:15 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:49:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:49:11 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:54:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:55:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×6

**컴포넌트 상위 15** — `Position`×3, `ProfitGuard`×3

### `logs/20261008_WARN.log` — 8.3KB · 54행 · 최종 08:55:38

- 형식 평문 · 시각 인식 54행 · WARNING=54

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 359ms account=333044256
2026-10-08 08:41:22 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-08 08:41:22 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-08 08:55:37 [WARNING] SYSTEM: [LEVELS] 08:45 결손 — 차트 TR 보충 code=A056A 11봉 (08:45~08:55) 63ms
2026-10-08 08:55:37 [WARNING] SYSTEM: [LEVELS 08:50] 봉원천=db_fallback(버퍼 0봉) 1봉 · 기준봉=08:45 · 구독지연=Nones
2026-10-08 08:55:38 [WARNING] SYSTEM: [Canary] scaler 노후=0h  z경고피처=16개  ⚠ z경고 폭증
2026-10-08 08:55:38 [WARNING] SYSTEM: [Canary] z경고 폭증(16개 ≥ 5개) → 장전 scaler 재적합 시도 (08:58 전)
2026-10-08 08:55:38 [WARNING] SYSTEM: [Canary] 장전 재적합 완료 n=30봉 z경고 →8개 ⚠ z경고 지속 — bar14 재적합 대기
```

</details>

**WARNING — 태그 12종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 28 | 08:41:20 | 08:55:11 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `출처축` | 6 | 08:41:22 | 08:55:07 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionBackfill` | 6 | 08:41:53 | 08:41:53 | OHLCV 불일치 ts=2026-10-07 09:32:00 cols=['open'] existing_source=rt |
| `Canary` | 3 | 08:55:38 | 08:55:38 | scaler 노후=0h  z경고피처=16개  ⚠ z경고 폭증 |
| `SessionStateDrop` | 2 | 08:41:23 | 08:41:23 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-10-07 → 2026-10-08)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `LEVELS` | 2 | 08:50:15 | 08:55:37 | 08:45 결손 — 차트 TR 보충 code=A056A 6봉 (08:45~08:50) 41ms |
| `LEVELS 08:50` | 2 | 08:50:15 | 08:55:37 | 봉원천=db_fallback(버퍼 0봉) 1봉 · 기준봉=08:45 · 구독지연=Nones |
| `MainStallTrace` | 1 | 08:41:26 | 08:41:26 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20261008.log |
| `Peter2` | 1 | 08:41:28 | 08:41:28 | 실시간 사료 기록 실패: 'DashboardAdapter' object has no attribute 'minute_chart_refresh_peter' |
| `OptionFlowChart` | 1 | 08:41:32 | 08:41:32 | 그리기 60.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 869x1001 |
| `ChartDBG` | 1 | 08:52:21 | 08:52:21 | paintEvent slow 75.4ms | size=1955x1124 candles=3 grid=34.4 spans=0.0 candles=0.2 dir=0.0 regime=0.0 markers=0.0 axes=39.3 cross=0.0 | slow_cnt=1 total_cnt=11 overlay_cnt=46 |
| `BarGap` | 1 | 08:54:42 | 08:54:42 | 기동 시점 결손 6봉 / 검사창 08:45~08:53 (분그리드 기준) — 08:48, 08:49, 08:50, 08:51, 08:52, 08:53 | session_bars 보존 여부는 15:46 확정 판정에서 |

**채널** — `SYSTEM`×54

**컴포넌트 상위 15** — `LiveDBG`×28, `출처축`×6, `SessionBackfill`×6, `Canary`×3, `SessionStateDrop`×2, `LEVELS`×2, `LEVELS 08:50`×2, `MainStallTrace`×1, `Peter2`×1, `OptionFlowChart`×1, `ChartDBG`×1, `BarGap`×1

### `logs/20261008_SYSTEM.log` — 41.5KB · 312행 · 최종 08:59:14

- 형식 평문 · 시각 인식 299행 · INFO=299, PLAIN=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:47 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=6040 | 행감지=30s all_threads=True
2026-10-08 08:40:48 [INFO] SYSTEM: [DBInit] 합계 0.55s | predictions=0.05s trades=0.25s daily_stats=0.01s shap=0.02s raw_data=0.16s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-08 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-08 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-08 08:40:48 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-08 08:59:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=08:58 O=1074.10 H=1074.10 L=1073.50 C=1073.84 V=65
2026-10-08 08:59:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:58 vol=65 | live_buy=36 shadow_buy=18 anchor_buy=18 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-10-08 08:59:08 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=14개 (08:55 최종 4개 대비 +10) — 재측정만, 재적합 없음
2026-10-08 08:59:14 [INFO] SYSTEM: [CybosRT-TICK] #300 code=A056A raw_time=85913 parsed=08:59:13 price=1074.10 vol=1 bid1=1073.78 ask1=1074.12 flag=49 side=BUY anchor=1/0
2026-10-08 08:59:46 [INFO] SYSTEM: [TickUI] alive ticks=358 code=A056A close=1073.00
```

</details>

**채널** — `SYSTEM`×299

**컴포넌트 상위 15** — `CybosSub`×49, `System`×28, `CybosRT-TICK`×18, `SYSTEM`×17, `BrokerSync`×12, `BalanceUI`×12, `CybosRT-START`×11, `Notify`×9, `TickUI`×9, `-`×8, `CybosRT-ROLLOVER`×7, `BAR-CLOSE`×7, `CVD-ANCHOR`×7, `Account`×6, `CybosDailyPnl`×6

### `logs/20261008_SIGNAL.log` — 20.9KB · 176행 · 최종 08:58:02

- 형식 평문 · 시각 인식 176행 · WARNING=60, INFO=116

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-10-08 08:58:02 [WARNING] SIGNAL: [ScalerRefresh] 15m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-10-08 08:58:02 [WARNING] SIGNAL: [ScalerRefresh] 15m CORE 'ofi_norm' raw_std≈0(0.0491) → identity(0,1) 강제 (FLAT 100% 방지)
2026-10-08 08:58:02 [WARNING] SIGNAL: [ScalerRefresh] 30m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-10-08 08:58:02 [WARNING] SIGNAL: [ScalerRefresh] 30m CORE 'ofi_norm' raw_std≈0(0.0491) → identity(0,1) 강제 (FLAT 100% 방지)
2026-10-08 08:58:02 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase1_3bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 60 | 08:45:22 | 08:58:02 | 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×176

**컴포넌트 상위 15** — `ScalerRefresh`×64, `ScalerFloor`×54, `DynMC`×21, `Model`×18, `TimeRouter`×7, `GapOffset`×4, `EnsembleGater`×3, `FeatureBuilder`×3, `MA-cont`×2

### `logs/20261008_LEARNING.log` — 159.6KB · 878행 · 최종 08:58:02

- 형식 평문 · 시각 인식 878행 · WARNING=435, INFO=443

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-08 08:40:54 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00024 auc=0.533 out_max=0.3766 (n=85) → 보정 재적용
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00063 auc=0.507 out_max=0.3669 (기준 auc<0.53 and span<0.020, 기저율=0.3667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-08 08:54:58 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=SATURATED_MAX
2026-10-08 08:55:05 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=0개 | 교체후보=3개 | CORE안전=⚠️
2026-10-08 08:55:37 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 혼합], total=1853, ver=5)
2026-10-08 08:55:38 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-08 08:58:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 144 | 08:40:54 | 08:54:58 | 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:1m` | 129 | 08:40:54 | 08:54:58 | 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 54 | 08:40:54 | 08:54:57 | 축퇴 감지 — span=0.00025 auc=0.526 out_max=0.3911 (기준 auc<0.53 and span<0.020, 기저율=0.3909 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 51 | 08:40:54 | 08:54:58 | 축퇴 감지 — span=0.00017 auc=0.462 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 36 | 08:40:56 | 08:54:57 | 축퇴 감지 — span=0.00130 auc=0.529 out_max=0.4068 (기준 auc<0.53 and span<0.020, 기저율=0.4061 n=165) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:15m` | 18 | 08:40:55 | 08:54:57 | 축퇴 감지 — span=0.00087 auc=0.448 out_max=0.2754 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 3 | 08:41:05 | 08:54:58 | 복원한 보정기가 축퇴 상태 — span=0.01232 auc=0.468 out_max=0.4068 (n=3107) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×878

**컴포넌트 상위 15** — `Calibration:30m`×288, `Calibration:1m`×255, `Calibration:3m`×102, `Calibration:5m`×99, `Calibration:10m`×69, `Calibration:15m`×33, `ExtremityCorrector`×6, `Calibration:ensemble`×6, `Consolidator`×6, `ScalerWarmup`×4, `RF`×3, `DriftAdjuster`×3, `SHAP`×3, `MetaConf`×1

### `logs/20261008_MICRO.log` — 26.1KB · 72행 · 최종 08:59:17

- 형식 평문 · 시각 인식 72행 · DEBUG=72

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1076.52/2 ask1=1077.00/1 mp={'microprice_tick': 1076.84, 'midprice_tick': 1076.76, 'depth_bias_tick': -0.2335} mlofi_tick=None queue=None
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1076.70/1 ask1=1077.00/1 mp={'microprice_tick': 1076.85, 'midprice_tick': 1076.85, 'depth_bias_tick': 0.0987} mlofi_tick=7.0667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1076.70/1 ask1=1077.00/1 mp={'microprice_tick': 1076.85, 'midprice_tick': 1076.85, 'depth_bias_tick': 0.0987} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1076.70/1 ask1=1076.98/5 mp={'microprice_tick': 1076.7466, 'midprice_tick': 1076.84, 'depth_bias_tick': -0.386} mlofi_tick=-6.2833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 4.0, 'bid_cancel_add_ratio'…
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1076.52/2 ask1=1076.98/5 mp={'microprice_tick': 1076.6514, 'midprice_tick': 1076.75, 'depth_bias_tick': -0.3136} mlofi_tick=-2.7833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
  …
2026-10-08 08:58:34 [DEBUG] MICRO: [MICRO-TICK] #900 bid1=1073.56/1 ask1=1073.64/1 mp={'microprice_tick': 1073.6, 'midprice_tick': 1073.6, 'depth_bias_tick': -0.2176} mlofi_tick=-4.3833 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-10-08 08:58:59 [DEBUG] MICRO: [MICRO-TICK] #1000 bid1=1073.66/1 ask1=1073.94/2 mp={'microprice_tick': 1073.7533, 'midprice_tick': 1073.8, 'depth_bias_tick': -0.0188} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-10-08 08:59:00 [DEBUG] MICRO: [MICRO-MINUTE] #4 ts=2026-10-08 08:58:00 close=1073.84 bias=-0.011049 slope=-0.534556 depth_bias=-0.1174 mlofi_norm=-0.034444 mlofi_pressure=-1 mlofi_slope=1.711667 queue_signal=0.0271 queue_ma=0.0320 queue_momentum=0.0122 depletion=0.5000 refill=0.5000 imbalance_…
2026-10-08 08:59:17 [DEBUG] MICRO: [MICRO-TICK] #1100 bid1=1073.66/1 ask1=1073.86/1 mp={'microprice_tick': 1073.76, 'midprice_tick': 1073.76, 'depth_bias_tick': -0.4374} mlofi_tick=-7.75 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-10-08 08:59:33 [DEBUG] MICRO: [MICRO-TICK] #1200 bid1=1073.06/1 ask1=1073.56/1 mp={'microprice_tick': 1073.3101, 'midprice_tick': 1073.3101, 'depth_bias_tick': -0.1122} mlofi_tick=-5.2333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add…
```

</details>

**채널** — `MICRO`×72

**컴포넌트 상위 15** — `MICRO-TICK`×65, `MICRO-MINUTE`×7

### `logs/20261008_DATA.log` — 894B · 4행 · 최종 08:58:41

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:58:11 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-235 individual=-166 institution=+409 oi=0 call_foreign=-263 put_foreign=+28 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-08 08:58:11 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-08 08:58:41 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-254 individual=-151 institution=+413 oi=0 call_foreign=-280 put_foreign=+57 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-08 08:58:41 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
  …
2026-10-08 08:58:11 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-235 individual=-166 institution=+409 oi=0 call_foreign=-263 put_foreign=+28 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-08 08:58:11 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-08 08:58:41 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-254 individual=-151 institution=+413 oi=0 call_foreign=-280 put_foreign=+57 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-08 08:58:41 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
```

</details>

**채널** — `DATA`×4

**컴포넌트 상위 15** — `CybosInvestor`×4

### `logs/20261008_PROBE.log` — 12.4KB · 6행 · 최종 08:58:41

- 형식 평문 · 시각 인식 6행 · INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:41:22 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-10-08 08:49:15 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-10-08 08:55:07 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-10-08 08:58:11 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
2026-10-08 08:58:11 [INFO] PROBE: [CybosProbe][RAW] CpSysDib.CpSvrNew7221 field_limit=64 headers={0: '28', 1: '28', 2: '75'} rows_sample=[{0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0', 10: '0', 11: '0', 12: '0', 13: '0', 14: '0', 15: '0', 16: '0', 17: '0', 18: '0',…
  …
2026-10-08 08:49:15 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-10-08 08:55:07 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056A']
2026-10-08 08:58:11 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
2026-10-08 08:58:11 [INFO] PROBE: [CybosProbe][RAW] CpSysDib.CpSvrNew7221 field_limit=64 headers={0: '28', 1: '28', 2: '75'} rows_sample=[{0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0', 10: '0', 11: '0', 12: '0', 13: '0', 14: '0', 15: '0', 16: '0', 17: '0', 18: '0',…
2026-10-08 08:58:41 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
```

</details>

**채널** — `PROBE`×6

**컴포넌트 상위 15** — `CybosInvestorProbe`×3, `CybosProbe`×3

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

### 메인 스레드 블로킹 4건 · 최대 6437ms · 5초 초과 1건

상위 — 6437ms, 4875ms, 3813ms, 2797ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:41:26 | 6437ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261008_WARN.log`
```
--- 메인 스레드 블로킹 ×4(표본)
08:41:26 2026-10-08 08:41:26 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6437 band=WARN since_pipe_s=NA
08:49:19 2026-10-08 08:49:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4875 band=INFO since_pipe_s=NA
08:49:30 2026-10-08 08:49:30 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2797 band=INFO since_pipe_s=NA
08:55:11 2026-10-08 08:55:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3813ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3813 band=INFO since_pipe_s=NA
```

### `logs/20261008_SIGNAL.log`
```
--- 기동 복원 ×8(표본)
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
08:40:44 2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
```

### `logs/20261008_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:54 2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:54 2026-10-08 08:40:54 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00024 auc=0.533 out_max=0.3766 (n=85) → 보정 재적용
08:40:54 2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00063 auc=0.507 out_max=0.3669 (기준 auc<0.53 and span<0.020, 기저율=0.3667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:54 2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261008_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:05 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 4 | 08:49:05 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:54:58 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 08:55

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261008_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 22 | 08:41:20 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 32 | 08:49:14 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 17 | 08:54:42 [WARNING] 기동 시점 결손 6봉 / 검사창 08:45~08:53 (분그리드 기준) — 08:48, 08:49, 08:50, 08:51, 08:52, 08:53 | session_bars 보존 여부는 15:4… |

- 이 로그 생존구간: 08:41 ~ 08:55

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261008_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:47 [INFO] 활성화 | file=logs\crash_fault.log PID=6040 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 186 | 08:49:05 [INFO] 기동 사전 학습 완료: 18000건 (극단성보정 live={'30m': True}) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 133 | 08:54:15 [INFO] 대기 중 | 장 개시 대기 — 09:00 분봉 파이프라인 시작 예정 | 레짐=NEUTRAL | 포지션=FLAT | 08:54:15 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261008_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:45:22 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 92 | 08:55:38 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 88 | 08:55:38 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 08:58

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
| **오늘 20261008** | **08:59** | 로그 본문 |

- 델타 **-573분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 결정
### Why
### How to apply
### 검증
### 병행 세션
## 2026-10-07 (MW0601 666차 — 장후 점검, 종합 완성본)
## 2026-10-07 (MW0601 667차 — 666차 후속 장후 자동조치: G-2 · 663-3 조사)
## 2026-10-07 (MW0601 668차 — 피터2: 피터리 트윗 실시간 추종 모의매매 신설)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
D-664-1 관측에 "오류 뒤 FreezeWatchdog START 연속 여부"를 병기.

**미처리(C/승인 대기)**: F-2(15:10 중단 가드 분봉 ts 병행 — 청산 경로 인접 + 15:09 학습 포함 여부 사용자 결정 선행), F-1/538-4(승인 대기), G-3(리포트가 코드 변경 비제안). 제5부 신규 0.
## 2026-10-07 (MW0601 668차 — 피터2: 피터리 트윗 실시간 추종 모의매매 신설)

**결정(사용자, 2026-10-07 장후)**: 장중 피터리(@PeterLeejoa) 트윗을 실시간 수집해 그의 진입·손절·청산 지시대로 **모의 1계약**을 추종한다. 10-08부터 집행(P1 섀도 관찰 생략 — 사용자 지시). 우선순위·CB는 권고안(미륵이 보유 중이면 건너뜀 / 피터2 손절도 CB②에 계수, 자체 한도 손절 2회). 수집은 로그인된 X 세션의 Chrome 확장. P&L 패널 「피터2」 별도 집계. 당일 1분봉 실시간 표시 → 장후 확정. 모든 문서는 `docs/미륵이고도화3/피터2/`.

**구현**: `strategy/peter2/{parse,follower,store}.py`(순수 해석·상태기계) · `tools/peter2_live/{receiver.py,extension/}`(127.0.0.1:8766 배타 바인딩, start_mireuk 6-D) · main.py `_peter2_*`(QTimer 2초, `_execute_entry(entry_source=PETER2)`, 외부 손절/목표, 미러 청산) · `PositionTracker.ext_stop/ext_target`(PETER2일 때만 ATR·TP1–3·손절계단·트레일링 덮음, 비-PETER2면 폐기) · `_post_exit` 켈리·앙상블 학습 제외(CB는 유지) · 청산 후 쿨다운 면제 · 대시보드(손익추이 출처 `pt2`, P&L 탭 「피터2」 버튼, `peter2_live_row` 실시간 사료) · `tools/peter2_eod.py`(daily_close 연결: `_tr` 초안·삭제 탐지·실추종·섀도·지연) · `tools/peter2_replay.py` · `peter_capture --src eod`. 출처 분류 `external` 신설(`PETER2` — system 아님, 전환기준 ① 판정에서 제외).

**근거(재생, 실측 아님)**: 41거래일(08-03–10-07) 지연 20초 재생에서 피터 +153.5pt vs 추종 +152.9pt(효율 1.00, 44건). 10-07 그의 거래줄이 손으로 쓴 `_tr.txt` 와 글자까지 일치. ⚠ 일일 손절 2회 정지가 41일간 약 47pt를 깎는다(한도 없음 +199.7pt, 3회 +189.6pt) — 한도 변경은 사용자 결정 안건으로 남김. 지연 40초면 효율 0.85.

**오프셋**: 장중엔 직전 실측일 값(10-08 → −5.40). 직전 실측일이 둘째 목요일(만기) 이전이면 `safe=False` → 진입 안 함(10-12가 해당).

**검증**: `tests/test_668_peter2.py` 16 pass(py37_32). 수신기 단독 기동·중복 기동 차단(Windows SO_REUSEADDR 중복 바인딩 실측 → SO_EXCLUSIVEADDRUSE)·UTF-8 적재 실측.

**[668차 후속 — 사용자 결정 2026-10-07]** `PETER2_DAILY_STOP_LIMIT` 2 → **0(해제)**. 「피터 손절 2회면 당일 정지」 제외. 근거: 재생에서 2회 정지가 41일간 약 47pt 손실(해제 시 +199.7pt, 최악일 −7.6). 0 = 해제로 follower 가 해석. 집행 시작(10-08) 전이라 사전등록 표본 분할 불필요. 남은 안전장치: CB②·일 최대 진입 6회·15:10.

**[668차 후속4 — 2026-10-08 장전 첫 기동 점검]** 피터2 08:41:28 정상 기동(live · offset −5.4 · safe=True), 수신기 08:40:37, Chrome 확장 설치 확인(Default 프로필), 하트비트 5초 간격. **결함 1건**: 엔진의 `self.dashboard` 는 `DashboardAdapter` 인데 `minute_chart_refresh_peter` 를 창(`MireukDashboard`)에만 넣어 `AttributeError`(WARN) — 당일 1분봉 실시간 사료 갱신만 누락, 수집·주문·버튼 무영향. 어댑터에 전달 메서드 추가 + AST 회귀 테스트(`test_engine_dashboard_calls_exist_on_adapter`). 문자열 존재 검사(`test_dashboard_wiring`)로는 못 잡았다 — 클래스 귀속을 확인해야 한다. **반영은 미륵이 재시작 시**. ⚠ 장중(08:5x) 커밋 — v9-dev 「장중 실시간코드 커밋 금지」의 **사용자 지시 예외**(「커밋하고 dev 배포해」). 기동 스크립트에 git pull 이 없어 실행 중 세션 무영향. dev 에는 코드가 없으므로 가이드 문서(어댑터 함정 추가)만 배포.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · 마지막 갱신 2026-10-07 20:01

최근 헤딩 8개:
```
## 2026-10-06 (MW0601 659차 — 장전 점검)
## 2026-10-06 (MW0601 660차 — 장중 점검)
## 2026-10-06 (MW0601 661차 — 장후 점검, 종합 완성본)
## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치)
## 2026-10-07 (MW0601 664차 — 장전 점검)
## 2026-10-07 (MW0601 666차 — 장후 점검, 종합 완성본)
## 2026-10-07 (MW0601 667차 — 666차 후속 장후 자동조치)
## 2026-10-07 (MW0601 668차 — 피터2 실시간 추종 신설)
```

미완료 체크박스 **3044건** (끝에서 30건)
```
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
nce.py`의 매분 루프 커버리지·`raw_candles` 결손 계산을 장중 실행 시 분모 "09:00~수집 시각"으로 국면 분기 — 2026-09-14·09-29·10-07(665차) 3회 반복된 "미발생 구간을 결손으로 오독" 패턴 근거. 코드 변경 승인 필요(C등급 아님, 점검 스크립트 자체 — 장후 세션에서 검토 가능).
## 2026-10-07 (MW0601 666차 — 장후 점검, 종합 완성본)

- [ ] **F-2 (신규, 사용자 승인 대기)** 15:10 예측 파이프라인 중단 가드 보강 — `main.py:_on_candle_closed()`(약 5881행)의 `is_force_exit_time(now)` 판정에 분봉 자체의 `ts`(벽시계가 아닌 분봉 소속 시각) 병행 확인 조건 추가, `utils/time_utils.py`에 `is_force_exit_bar(candle_ts)` 헬퍼 신설 계획(이상점 1-4 대응). **선행 결정 필요**: 15:09분 1분봉이 당일 온라인학습(SGD·스케일러 갱신)에 포함되는 것이 설계 의도인지, 제외돼야 하는지 — 사용자 확인 후 수정 범위 확정.
- [ ] **G-3 재우선순위화 검토** `[Position] 진입` 로그 공통화(기존 항목) — 666차에서 범위 확장 확인: 종전엔 "[Position] 진입" 한 줄만 빠지는 것으로 알려졌으나, 실제로는 `[주문요청]`(등급·방향·역방향진입 여부)도 함께 빠진다(§1-5). G-3 착수 여부 판단 시 이 범위 확장을 반영할 것 — 코드 변경은 아직 제안하지 않음.
- [ ] **O-t1 (신규, 상시 관측)** `raw_candles` 당일 max ts가 15:08을 다시 넘는지(`[BarGap]` ERROR 재현 여부) — 재현되면 "드문 사고 아니라 상시 위험"으로 격상, F-2 적용 시급성 상향.
- [ ] **O-t2 (신규)** Chejan 선행체결 레이스(`[C1]` 가드) 재발 시 `[주문요청]`도 함께 빠지는지 재확인(§1-5 패턴 일반성 확인) — 다음 재발 1건으로 패턴 재확인.
- [ ] 1-1·1-2·1-3(부팅 access violation·SessionStateDrop·git lock 잔재) 지속 — 변화 없음, D-664-1·D-664-2(10/8 장전 재현 여부)로 이월 유지.
- [ ] 663-4(git diff 타임아웃 2차 호출 생략 검증) 지속 — 오늘도 조건 미발생(타임아웃 0건), 다음 타임아웃 발생일에 재확인.
- [ ] 663-3(부팅 access violation 코드 직접 검토, `dashboard/main_dashboard.py:7240~7250`) 지속 — 조사 자체는 승인 불요, 다음 장후로 착수 이월.
- [ ] 663-1(F-5 브로커 어댑터 진단 로그)·663-2(F-7 microstructure 백테스트 실패) — 사용자 선택 대기 지속, 변화 없음.
- [ ] F-1(538-4, session_state 마커 승계) — 사용자 승인 대기 지속, 변화 없음.

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

### `data/heartbeat_MW0601_20261008.json` — 244B · 10-08 08:59:08
```json
{
 "pid": 29516,
 "written_at": "2026-10-08T08:59:38",
 "beat_epoch": 1791417577.7599826,
 "beat_age_sec": 0.6,
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

- 파일 최종 기록: **10-08 08:56:01**

| 키 | 값 | 수집 대상일(2026-10-08)과 일치 |
|---|---|---|
| `date` | 2026-10-08 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-08 08:55:38 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-07) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-08 08:55:38 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-07) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **08:58** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 08:59 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 7 |
| `session_bars` 당일 행수 | 7 (기대 411) |

- 미도래 **370봉** (08:59~15:08) — 수집 시각 08:59 이후라 결손·영구결손에서 제외
- 결손 **0봉**
- ⚠ **영구 결손 7봉** (`session_bars` 에도 없음): 08:48, 08:49, 08:50, 08:51, 08:52, 08:53, 08:54

- 라이브 로그 대조: `logs/20261008_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 3회 · 재시작 2회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 3개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **9건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 6040: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:47 · 정규장(09:00) 이후 **0건**
- PID 29516: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:54:42 · 정규장(09:00) 이후 **0건**
- PID 29960: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:48:50 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 6040 | 08:40:47 | 08:48:28 | 없음 | 판정불가 — WER **미측정** |
| 29960 | 08:48:50 | 08:54:20 | 없음 | 판정불가 — WER **미측정** |
| 29516 | 08:54:42 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 203개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261007-점검리포트.md` | 85.5KB | 10-07 17:31 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_post.md` | 92.8KB | 10-07 16:17 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261007.md` | 17.4KB | 10-07 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_intra.md` | 80.5KB | 10-07 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_pre.md` | 60.1KB | 10-07 08:59 |
| `docs/정기점검/매일점검/MW0601-20261006-점검리포트.md` | 87.4KB | 10-06 17:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_post.md` | 86.9KB | 10-06 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261006_intra.md` | 76.7KB | 10-06 12:32 |

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

1. 메인 스레드 정지 5초 초과 **1건** (최대 6437ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
2. `logs/20261008_LEARNING.log`: **축퇴** 8건(표본)
3. `logs/crash_fault.log`: `Windows fatal exception` **9건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
4. 런처 재시작 같은 날 **2회** (08:48 일시적 크래시, 08:54 일시적 크래시) — 재시작 간격·가동시간이 줄어드는지 §9 「프로세스 종료 3축 대사」에서 볼 것 (661차 G-3)
5. 미커밋 변경 74건 (실질 8건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261008*.log` (Windows) / `grep 강제청산 logs/*20261008*.log`*