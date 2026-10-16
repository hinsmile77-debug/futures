# 미륵이 증거 다이제스트 — 2026-10-08 / INTRA

- 생성 2026-10-08 12:27:39 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-016yhnvvjdm5ldwjuwraymsz/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261008` · `2026-10-08` · `261008` · `1008`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **27개** 파일 · 27개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `261007_{DATE}_D.xls` | 1 | `data/db/option_hts/261007_1008_D.xls` | 480.4KB | 10-07 10:06 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261008.log` | 269B | 10-08 08:28 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261008.log` | 125B | 10-08 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261008.log` | 140B | 10-08 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261008.json` | 243B | 10-08 12:27 |
| `launcher_{DATE}_084001_6711.log` | 1 | `logs/Mireuk_batch/launcher_20261008_084001_6711.log` | 1.4MB | 10-08 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261008.log` | 2.9KB | 10-08 08:41 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261008.log` | 48.5KB | 10-08 12:25 |
| `position_state.json.gen_{DATE}_105406` | 1 | `data/position_state.json.gen_20261008_105406` | 1.6KB | 10-08 10:54 |
| `position_state.json.gen_{DATE}_105419` | 1 | `data/position_state.json.gen_20261008_105419` | 1.6KB | 10-08 10:54 |
| `position_state.json.gen_{DATE}_105803` | 1 | `data/position_state.json.gen_20261008_105803` | 1.7KB | 10-08 10:55 |
| `retrain_intraday_{DATE}_092102.log` | 1 | `logs/retrain_intraday_20261008_092102.log` | 5.7KB | 10-08 09:21 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261008.log` | 34.0KB | 10-08 12:20 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-08.jsonl` | 2.3KB | 10-08 12:18 |
| `{DATE}_0908_D.xls` | 1 | `data/db/option_hts/261008_0908_D.xls` | 480.2KB | 10-08 09:08 |
| `{DATE}_0946_D.xls` | 1 | `data/db/option_hts/261008_0946_D.xls` | 480.3KB | 10-08 09:46 |
| `{DATE}_DATA.log` | 1 | `logs/20261008_DATA.log` | 234.2KB | 10-08 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261008_DEBUG.log` | 130.2KB | 10-08 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261008_HEALTH.log` | 2.0KB | 10-08 12:24 |
| `{DATE}_HOGA.log` | 1 | `logs/20261008_HOGA.log` | 23.1MB | 10-08 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261008_LEARNING.log` | 291.4KB | 10-08 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20261008_MICRO.log` | 457.4KB | 10-08 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20261008_PROBE.log` | 56.0KB | 10-08 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261008_SIGNAL.log` | 472.6KB | 10-08 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261008_SYSTEM.log` | 491.6KB | 10-08 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20261008_TRADE.log` | 5.6KB | 10-08 10:59 |
| `{DATE}_WARN.log` | 1 | `logs/20261008_WARN.log` | 342.2KB | 10-08 12:27 |

## 2. 코드·커밋 상태

- HEAD `a0f179f` · 브랜치 `v9-dev` · 미커밋 81건 · 실질 변경 10건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 10 · 미추적 71 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
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
?? "MAEKJEOM_LADDER.bat - 바로 가기.lnk"
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_20261002.md
?? dev_memory/_tmp_append_decisionlog_20261006_post.md
?? dev_memory/_tmp_append_decisionlog_20261007_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_pre.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_pre.md
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
?? docs/미륵이고도화3/피터2/live/
?? docs/미륵이고도화3/피터리_위로막힘_근거조사_MW0601-20261002.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.md
?? docs/신동거래/일일/신동_일일_MW0601_20260930.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261001.md
?? docs/신동거래/일일/신동_일일_MW0601_20261001.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261002.md
?? docs/신동거래/일일/신동_일일_MW0601_20261002.svg
… 외 41건
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

_본문 미열람(설정): `20261008_HOGA.log` 23.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/18개 (중요도순). 제외: `20261008_DATA.log`, `20261008_PROBE.log`, `launcher_20261008_084001_6711.log`, `20261008_DEBUG.log`, `peter2_receiver_20261008.log`, `shindong2_20261008.log`, `mainstall_traceback_20261008.log`, `claude_resume_20261008.log`_

### `logs/20261008_TRADE.log` — 5.6KB · 39행 · 최종 10:59:08

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:41:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:41:15 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:49:05 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-08 08:49:11 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-08 08:54:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-10-08 10:58:03 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2521 code=A056A 방향=SHORT 체결=1 미체결=0
2026-10-08 10:58:03 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2521 code=A056A 방향=SHORT 체결=1 미체결=0
2026-10-08 10:58:03 [INFO] TRADE: [Position] 체결청산 LONG @ 1071.6 | PnL=+0.16pt (+5,964원) | 하드스톱(틱)
2026-10-08 10:58:03 [INFO] TRADE: [청산 완료] PnL=+0.16pt (+5,964원) | 포지션 합계 -35,071원 (레그 2)
2026-10-08 10:59:08 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,272,393) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
```

</details>

**채널** — `TRADE`×39

**컴포넌트 상위 15** — `Sizer`×11, `Position`×8, `Chejan`×7, `ProfitGuard`×3, `주문요청`×3, `진입체크`×1, `체결진입`×1, `체결진입보정`×1, `손절1차 조기축소`×1, `TickTP1`×1, `TickStop-S0C`×1, `청산 완료`×1

### `logs/20261008_WARN.log` — 342.2KB · 1590행 · 최종 12:27:28

- 형식 평문 · 시각 인식 1550행 · CRITICAL=1, ERROR=10, WARNING=1539, PLAIN=40

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-10-08 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 359ms account=333044256
2026-10-08 08:41:22 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-08 08:41:22 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-08 12:27:07 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 81.9ms | size=1955x1124 candles=216 grid=21.6 spans=7.2 candles=14.6 dir=0.8 regime=6.9 markers=28.6 axes=0.6 cross=0.0 | slow_cnt=1309 total_cnt=1459 overlay_cnt=11265
2026-10-08 12:27:18 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 133.6ms | size=1955x1124 candles=216 grid=35.3 spans=7.9 candles=15.6 dir=0.9 regime=12.8 markers=58.8 axes=0.7 cross=0.0 | slow_cnt=1310 total_cnt=1460 overlay_cnt=11271
2026-10-08 12:27:28 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 105.8ms | size=1955x1124 candles=216 grid=29.1 spans=8.7 candles=15.7 dir=0.9 regime=8.1 markers=41.1 axes=0.7 cross=0.0 | slow_cnt=1311 total_cnt=1461 overlay_cnt=11282
2026-10-08 12:27:39 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 114.5ms | size=1955x1124 candles=216 grid=34.1 spans=10.4 candles=17.4 dir=0.9 regime=9.9 markers=39.4 axes=0.7 cross=0.0 | slow_cnt=1312 total_cnt=1462 overlay_cnt=11292
2026-10-08 12:27:50 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 143.9ms | size=1955x1124 candles=216 grid=32.6 spans=13.1 candles=21.1 dir=1.0 regime=10.0 markers=63.2 axes=0.8 cross=0.0 | slow_cnt=1313 total_cnt=1463 overlay_cnt=11304
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `Peter2` | 10 | 09:25:54 | 12:18:24 | 폴링 예외 — 이번 주기 건너뜀: 'bool' object is not callable |
| CRITICAL | `SHS-EKS` | 1 | 09:05:01 | 09:05:01 | Early Kill Switch 발동 — 일시 관망 conf_max=39.4% bars=5 (delayed=0 policy=4 conf측정=1) → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가) |

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

**WARNING — 태그 41종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1314 | 08:52:21 | 12:27:50 | paintEvent slow 75.4ms | size=1955x1124 candles=3 grid=34.4 spans=0.0 candles=0.2 dir=0.0 regime=0.0 markers=0.0 axes=39.3 cross=0.0 | slow_cnt=1 total_cnt=11 overlay_cnt=46 |
| `LiveDBG` | 81 | 08:41:20 | 12:27:07 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 41 | 08:41:32 | 12:24:07 | 그리기 60.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 869x1001 |
| `ScalerRefresh` | 9 | 09:14:01 | 12:11:01 | 5분 누적 수익률 -0.413% (임계 ±0.358%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ChejanFlow` | 7 | 10:54:02 | 10:58:03 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='2481' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=10:54:01.977' | positio… |
| `ChejanMatch` | 7 | 10:54:02 | 10:58:03 | order_no='2481' | pending='ENTRY:LONG qty=2 filled=0 order_no=2481 reason=진입 req_at=10:54:01.977' | pending_matched=True |
| `출처축` | 6 | 08:41:22 | 08:55:07 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionBackfill` | 6 | 08:41:53 | 08:41:53 | OHLCV 불일치 ts=2026-10-07 09:32:00 cols=['open'] existing_source=rt |
| `Health` | 6 | 09:04:01 | 12:23:01 | level=WARNING degraded=OFF | latency=421ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS 08:50]×1 [LEVELS]×1 |
| `CB③-P4` | 6 | 10:20:02 | 10:33:07 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=20.0%) |
| `PendingOrder` | 6 | 10:54:01 | 10:58:03 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1071.56, 'reason': '진입', 'hint_source': '', 'atr': 1.3014, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `SHS-EKS` | 4 | 09:05:01 | 09:21:02 | Early Kill Switch 발동 conf_max=39.4% < 발동선=39.7%(mc=41.7%-margin2.0%p) core_pass=0/5봉(측정 0봉) | bars=5 (delayed=0 policy=4 conf측정=1) core측정=0봉 | 보정기 상한=41.1% auc=0.463 state=unmeasured:calibrator_unfitted ⇒ 도달가능 → 일시 관망 (09:20부터 30분 간격 자동 회복… |

**채널** — `SYSTEM`×1544, `HEALTH`×6

**컴포넌트 상위 15** — `ChartDBG`×1314, `LiveDBG`×81, `OptionFlowChart`×41, `-`×40, `Peter2`×11, `ScalerRefresh`×9, `ChejanFlow`×7, `ChejanMatch`×7, `출처축`×6, `SessionBackfill`×6, `Health`×6, `CB③-P4`×6, `PendingOrder`×6, `SHS-EKS`×5, `PipePerf`×4

### `logs/20261008_SYSTEM.log` — 491.6KB · 3389행 · 최종 12:27:37

- 형식 평문 · 시각 인식 3371행 · INFO=3371, PLAIN=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:47 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=6040 | 행감지=30s all_threads=True
2026-10-08 08:40:48 [INFO] SYSTEM: [DBInit] 합계 0.55s | predictions=0.05s trades=0.25s daily_stats=0.01s shap=0.02s raw_data=0.16s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-08 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-08 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-08 08:40:48 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-08 12:27:07 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-228922 nonarb=-643716
2026-10-08 12:27:09 [INFO] SYSTEM: [CybosRT-TICK] #29000 code=A056A raw_time=122709 parsed=12:27:09 price=1060.04 vol=1 bid1=1060.02 ask1=1060.24 flag=50 side=SELL anchor=0/1
2026-10-08 12:27:28 [INFO] SYSTEM: [TickUI] alive ticks=29045 code=A056A close=1061.04
2026-10-08 12:27:37 [INFO] SYSTEM: [PumpGuard] rollover 연기 — 메인 펌프(BlockRequest 대기) 중 재진입 회피 (누적 366회, 재시도=호출부)
2026-10-08 12:27:48 [INFO] SYSTEM: [CybosRT-TICK] #29100 code=A056A raw_time=122748 parsed=12:27:48 price=1061.20 vol=1 bid1=1061.20 ask1=1061.44 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3371

**컴포넌트 상위 15** — `CybosInvestorRaw`×828, `PumpGuard`×366, `CybosRT-TICK`×306, `CybosRT-ROLLOVER`×215, `BAR-CLOSE`×215, `CVD-ANCHOR`×215, `TickUI`×212, `S6Detail`×208, `PipePerf`×208, `System`×70, `CybosSub`×49, `OptionChain`×46, `MicroRegime`×44, `IntradayRegime`×43, `OptionBook`×42

### `logs/20261008_SIGNAL.log` — 472.6KB · 3960행 · 최종 12:27:00

- 형식 평문 · 시각 인식 3960행 · WARNING=2130, INFO=1830

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.417
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.405
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.397
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.393
2026-10-08 08:40:44 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.401
  …
2026-10-08 12:26:02 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.342<mc0.650)
2026-10-08 12:27:00 [INFO] SIGNAL: --- 2026-10-08 12:26:00 분봉 파이프라인 시작 ---
2026-10-08 12:27:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.3% grade=X regime=NEUTRAL
2026-10-08 12:27:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=34.2% grade=X micro=횡보장
2026-10-08 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.343<mc0.650)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1488 | 09:00:01 | 12:12:09 | 1m 'macro_vix' scale=0.0100 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 288 | 09:00:00 | 12:20:00 | ts=08:59 horizon=1m age=2m max_z=-9.53(opt_pcr_norm) extreme=3 adj=3 |
| `Model` | 180 | 09:00:00 | 12:11:00 | 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 62 | 09:18:00 | 12:25:01 | CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+0.427 need <0 (SHORT) bull_exh=0.00 |
| `ScalerRefresh` | 60 | 08:45:22 | 08:58:02 | 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 43 | 09:07:01 | 12:22:02 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `PCR-Dampen` | 4 | 10:29:01 | 10:44:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConstOut` | 4 | 11:14:00 | 12:14:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 11:09:00 | 11:09:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3610 < 필요 0.4530 (conf_floor=0.330, min_conf=0.453, span=0.0203, auc=0.398). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3960

**컴포넌트 상위 15** — `ScalerFloor`×1542, `SIGNAL`×416, `ScalerMonitor`×288, `Ensemble`×214, `MetaGate`×214, `Model`×204, `ZeroDiag`×188, `FQAdj`×169, `ScalerRefresh`×95, `Checklist`×93, `ATR-Horizon`×66, `ToxicityGate`×58, `차단`×50, `MicroRegime`×44, `IntradayRegime`×43

### `logs/20261008_LEARNING.log` — 291.4KB · 2295행 · 최종 12:27:00

- 형식 평문 · 시각 인식 2295행 · WARNING=441, INFO=1854

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-08 08:40:54 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00024 auc=0.533 out_max=0.3766 (n=85) → 보정 재적용
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00063 auc=0.507 out_max=0.3669 (기준 auc<0.53 and span<0.020, 기저율=0.3667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-10-08 08:40:54 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-10-08 12:27:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=44.1% UP)
2026-10-08 12:27:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=36.5% 예측=FL 실제=UP)
2026-10-08 12:27:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=39.4% 예측=FL 실제=DN)
2026-10-08 12:27:00 [INFO] LEARNING: [MetaConf] LR[횡보장] 비동기 결과 반영 (cnt=961)
2026-10-08 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=36.1%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 145 | 08:40:54 | 09:48:01 | 하한 도달불가 — out_max=0.2382 < conf_floor=0.3300 (span=0.00126 auc=0.661 out_max=0.2382, 기저율=0.2375 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:1m` | 130 | 08:40:54 | 09:29:00 | 축퇴 감지 — span=0.00041 auc=0.514 out_max=0.3877 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 54 | 08:40:54 | 08:54:57 | 축퇴 감지 — span=0.00025 auc=0.526 out_max=0.3911 (기준 auc<0.53 and span<0.020, 기저율=0.3909 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 51 | 08:40:54 | 08:54:58 | 축퇴 감지 — span=0.00017 auc=0.462 out_max=0.3376 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 36 | 08:40:56 | 08:54:57 | 축퇴 감지 — span=0.00130 auc=0.529 out_max=0.4068 (기준 auc<0.53 and span<0.020, 기저율=0.4061 n=165) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:15m` | 20 | 08:40:55 | 11:14:00 | 축퇴 감지 — span=0.00087 auc=0.448 out_max=0.2754 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 5 | 08:41:05 | 11:52:00 | 복원한 보정기가 축퇴 상태 — span=0.01232 auc=0.468 out_max=0.4068 (n=3107) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×2295

**컴포넌트 상위 15** — `LEARNING`×656, `Calibration:30m`×290, `Calibration:1m`×258, `SGD`×208, `sigma`×195, `Bias⚠`×118, `Calibration:3m`×102, `Calibration:5m`×99, `Bias`×77, `Calibration:10m`×69, `OnlineLearner`×54, `MetaConf`×43, `Calibration:15m`×36, `ScalerWarmup`×35, `BiasReset`×12

### `logs/20261008_HEALTH.log` — 2.0KB · 13행 · 최종 12:24:05

- 형식 평문 · 시각 인식 13행 · WARNING=6, INFO=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 09:04:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=421ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS 08:50]×1 [LEVELS]×1
2026-10-08 09:05:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=499ms | quality=1.00 | cache_age=56s | exceptions_10m=4 | exc_tags=[SHS-EKS]×2 [LEVELS 08:50]×1 [LEVELS]×1
2026-10-08 09:22:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3236ms | quality=1.00 | cache_age=155s | exceptions_10m=1 | exc_tags=[SHS-EKS]×1
2026-10-08 09:23:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=391ms | quality=1.00 | cache_age=27s | exceptions_10m=1 | exc_tags=[SHS-EKS]×1
2026-10-08 09:30:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 352ms (표본 20분)
  …
2026-10-08 10:06:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=499ms | quality=1.00 | cache_age=38s | exceptions_10m=2 | exc_tags=[Peter2]×2
2026-10-08 11:31:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=481ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-08 11:32:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=420ms | quality=1.00 | cache_age=57s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-08 12:23:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=300ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[Peter2]×2
2026-10-08 12:24:05 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=276ms | quality=1.00 | cache_age=61s | exceptions_10m=2 | exc_tags=[Peter2]×2
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 6 | 09:04:01 | 12:23:01 | level=WARNING degraded=OFF | latency=421ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[BarGap]×1 [LEVELS 08:50]×1 [LEVELS]×1 |

**채널** — `HEALTH`×13

**컴포넌트 상위 15** — `Health`×12, `HealthTrend`×1

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

### `logs/20261008_MICRO.log` — 457.4KB · 1226행 · 최종 12:27:31

- 형식 평문 · 시각 인식 1226행 · DEBUG=1226

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1076.52/2 ask1=1077.00/1 mp={'microprice_tick': 1076.84, 'midprice_tick': 1076.76, 'depth_bias_tick': -0.2335} mlofi_tick=None queue=None
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1076.70/1 ask1=1077.00/1 mp={'microprice_tick': 1076.85, 'midprice_tick': 1076.85, 'depth_bias_tick': 0.0987} mlofi_tick=7.0667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1076.70/1 ask1=1077.00/1 mp={'microprice_tick': 1076.85, 'midprice_tick': 1076.85, 'depth_bias_tick': 0.0987} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1076.70/1 ask1=1076.98/5 mp={'microprice_tick': 1076.7466, 'midprice_tick': 1076.84, 'depth_bias_tick': -0.386} mlofi_tick=-6.2833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 4.0, 'bid_cancel_add_ratio'…
2026-10-08 08:45:23 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1076.52/2 ask1=1076.98/5 mp={'microprice_tick': 1076.6514, 'midprice_tick': 1076.75, 'depth_bias_tick': -0.3136} mlofi_tick=-2.7833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
  …
2026-10-08 12:27:00 [DEBUG] MICRO: [MICRO-MINUTE] #212 ts=2026-10-08 12:26:00 close=1059.90 bias=-0.009219 slope=0.127346 depth_bias=-0.1089 mlofi_norm=0.069655 mlofi_pressure=1 mlofi_slope=79.845000 queue_signal=0.0394 queue_ma=0.0023 queue_momentum=0.0061 depletion=0.4919 refill=0.5081 imbalance_…
2026-10-08 12:27:03 [DEBUG] MICRO: [MICRO-TICK] #95500 bid1=1059.88/1 ask1=1060.02/4 mp={'microprice_tick': 1059.908, 'midprice_tick': 1059.95, 'depth_bias_tick': -0.0654} mlofi_tick=2.8167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-10-08 12:27:20 [DEBUG] MICRO: [MICRO-TICK] #95600 bid1=1060.08/1 ask1=1060.24/1 mp={'microprice_tick': 1060.16, 'midprice_tick': 1060.16, 'depth_bias_tick': 0.3521} mlofi_tick=12.3 queue={'depletion_bid': 4.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-10-08 12:27:31 [DEBUG] MICRO: [MICRO-TICK] #95700 bid1=1060.88/1 ask1=1061.14/1 mp={'microprice_tick': 1061.01, 'midprice_tick': 1061.01, 'depth_bias_tick': 0.3372} mlofi_tick=-2.8667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-10-08 12:27:43 [DEBUG] MICRO: [MICRO-TICK] #95800 bid1=1061.28/1 ask1=1061.48/1 mp={'microprice_tick': 1061.38, 'midprice_tick': 1061.38, 'depth_bias_tick': -0.1759} mlofi_tick=3.0 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
```

</details>

**채널** — `MICRO`×1226

**컴포넌트 상위 15** — `MICRO-TICK`×1011, `MICRO-MINUTE`×215

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 1 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 1 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 50 |
| 사이저 호출(`[Sizer]`) | 11 |

### 포지션 1건 · 승 0 (0%) · 합계 -0.62pt (-35,072원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:54:02 | 엔진 | LONG | 2 | 5m | 2 | -0.62 | -35,072 | 하드스톱(틱) |

**청산 레그 2행** (부분청산 1 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:54:19 | 부분 | 1 | -0.78 | -41,036 | 손절1차 조기축소 |
| 10:58:03 | 전량 | 1 | +0.16 | +5,964 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `손절1차 조기축소`×1, `하드스톱(틱)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -35,072 = 포지션합 -35,072 → OK · `[청산 완료]` 1건 = 조립 포지션 1건 → OK

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:54:02 | LONG | 2 | 1071.56 | 5m | mean-revert |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `ofi`×1, `fore`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×2, **2계약**×3, **3계약**×6

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×11

### 차단 사유 50건 · 31종

| 건수 | 사유 |
|---|---|
| 18 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 2 | ATR 0.94pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
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
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.3pt > ATR×5.0=8.2pt (시가=1075.20 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap |

**체크리스트 미통과 항목 누적** — `2_confidence`×18, `3_vwap`×10, `7_prev_bar`×7, `5_ofi`×6, `4_cvd`×5, `6_foreign`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 9건 · 최대 6437ms · 5초 초과 1건

상위 — 6437ms, 4875ms, 3813ms, 3750ms, 3359ms, 2797ms, 2328ms, 2235ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 08:41:26 | 6437ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261008_WARN.log`
```
--- Traceback ×5(표본)
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
??:??:?? Traceback (most recent call last):
--- [CB] ×1(표본)
10:54:19 2026-10-08 10:54:19 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×2(표본)
10:58:03 2026-10-08 10:58:03 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:00:03)
10:58:03 2026-10-08 10:58:03 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:00:03)
--- [SHAP] 슬로우 ×4(표본)
11:25:01 2026-10-08 11:25:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 943ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:40:02 2026-10-08 11:40:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1028ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:51:01 2026-10-08 11:51:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 927ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:11:02 2026-10-08 12:11:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 924ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:26 2026-10-08 08:41:26 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=6437 band=WARN since_pipe_s=NA
08:49:19 2026-10-08 08:49:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4875 band=INFO since_pipe_s=NA
08:49:30 2026-10-08 08:49:30 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2797 band=INFO since_pipe_s=NA
08:55:11 2026-10-08 08:55:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3813ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3813 band=INFO since_pipe_s=NA
```

### `logs/20261008_SYSTEM.log`
```
--- ConstOut ×5(표본)
09:22:04 2026-10-08 09:22:04 [INFO] SYSTEM: [DynMC] ConstOut 고착 conf 제외: [0.85] → 407건 제거 (잔여 2165건)
11:14:00 2026-10-08 11:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.7367) | 앙상블 제외는 유지
11:23:00 2026-10-08 11:23:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4075) | 앙상블 제외는 유지
12:05:02 2026-10-08 12:05:02 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3861) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-10-08 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-08 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:10:00 2026-10-08 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:16:00 2026-10-08 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
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

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261008_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:05 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 4 | 08:49:05 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:54:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 3 | 10:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,324,412) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShad… |

- 이 로그 생존구간: 08:41 ~ 10:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261008_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 22 | 08:41:20 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 34 | 08:49:14 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 36 | 08:54:42 [WARNING] 기동 시점 결손 6봉 / 검사창 08:45~08:53 (분그리드 기준) — 08:48, 08:49, 08:50, 08:51, 08:52, 08:53 | session_bars 보존 여부는 15:4… |
| 10:00 | 장중 초반 | 124 | 09:54:01 [WARNING] paintEvent slow 129.0ms | size=1955x1124 candles=63 grid=40.2 spans=0.5 candles=17.0 dir=0.3 regime=16.1 mark… |
| 12:00 | 장중 중간점 | 87 | 11:54:00 [WARNING] paintEvent slow 92.3ms | size=1955x1124 candles=183 grid=23.2 spans=6.3 candles=14.5 dir=0.7 regime=6.9 marke… |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261008_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:47 [INFO] 활성화 | file=logs\crash_fault.log PID=6040 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 214 | 08:49:05 [INFO] 기동 사전 학습 완료: 18000건 (극단성보정 live={'30m': True}) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 234 | 08:54:15 [INFO] 대기 중 | 장 개시 대기 — 09:00 분봉 파이프라인 시작 예정 | 레짐=NEUTRAL | 포지션=FLAT | 08:54:15 |
| 10:00 | 장중 초반 | 203 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 186 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~12:27: 208/208분 (100.0%)**

_장중 수집 — 분모를 수집 시각 12:27 까지로 줄였다. 이후 163분(~15:10)은 **미도래**라 제외(결손 아님)._

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261008_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:45:22 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 232 | 08:55:38 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 330 | 08:55:38 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 182 | 09:56:01 [WARNING] 신뢰도 미달 33.4% < 38.1% → 강제 X등급 |
| 12:00 | 장중 중간점 | 218 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=3m max_z=+7.25(ofi_reversal_speed) extreme=2 adj=2 |

- 이 로그 생존구간: 08:40 ~ 12:27

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
| **오늘 20261008** | **12:27** | 로그 본문 |

- 델타 **-365분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-08 (MW0601 669차 — 장전 점검)
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
`--until`)이 `+0900` 시간대 미지정 — 리눅스 샌드박스(UTC)에서 KST 00:00~09:00 커밋을 놓친다(653차/652 G-1 규약이 이 줄에는 미반영). 오늘 커밋 `a0f179f`(08:51:15 KST)가 실제 재현 사례 — 수집기 다이제스트는 "당일 커밋 없음"으로 오보고, 이 세션이 `git log --since="2026-10-08 00:00:00 +0900"`로 직접 재확인해 걸러냄. 그레핑으로 파일 내 동일 패턴(`"--since=%s 00:00"` 꼴 시간대 미지정) 전수 확인 — 이 한 줄이 유일.
③ D-664-1 · D-664-2(10/7 664차가 10/8 장전 몫으로 이월 등록한 관측) 판정완료 — 둘 다 재현, 기존 판정(무해 · F-1 미적용 지속) 유지. D-664-1은 오늘 PID 교체(①과 연결)가 동반된 점이 과거 9일(항상 같은 PID 생존)과 다름 — 같은 원인으로 섣불리 합치지 않고 ①로 분리 등록.
④ 668차 후속4(어제 장후, 별도 세션) 피터2 `DashboardAdapter` `AttributeError` 수정 커밋(`a0f179f`) 반영 확인 — `grep minute_chart_refresh_peter dashboard/main_dashboard.py main.py`로 메서드 추가(`dashboard/main_dashboard.py` `DashboardAdapter` 클래스) 확인, 08:54:42 이후 인스턴스(PID 29516)에서 `[Peter2] 실시간 사료 기록 실패` 재발 없음(WARN 로그 `Peter2` 태그 1건만, 08:41:28 — 수정 반영 전 인스턴스에서만 발생).
⑤ 설정 불변식 24행 전부 일치, 차단게이트 9/40 비활성 전부 기록된 의도. 한시예외 재검토 기한 경과 0건(CB②는 2026-09-02 519차로 복원 완료, 남은 것은 발동 1회 관측).

### 결정
- 1-1·1-2 둘 다 Fix 계획만 수립, 적용은 장후(오늘은 라이브 프로세스 운영 중 + 장전 예약이라 코드 변경·커밋·배포·재기동 금지 규약 준수).
- D-664-1·D-664-2는 NEXT_TODO에서 판정완료로 닫고, 1-1을 신규 관측(O-p1, 내일 장전 재현 여부)으로 이어 등록.

### Why
함정①(판정≠결정) — 1-2는 "이미 653차가 고친 줄 알았던 지점"이 실은 한 곳에는 안 고쳐져 있었던 사례라 신규 Fix로 등록했다(그레핑으로 중복 등록 아님을 먼저 확인). 1-1은 기존에 추적 중인 "부팅구간 access violation"(9관측일, 늘 같은 PID 생존)과 외형이 비슷해 혼동하기 쉬웠으나, watchdog strikes=0·실제 PID 교체라는 점에서 다른 메커니즘일 가능성이 있어 313차 원칙(다른 증거를 같은 원인으로 섣불리 합치지 않는다)에 따라 별개 항목으로 분리했다.

### How to apply
1-2: `collect_evidence.py:2637`의 `"--since=%s 00:00" % D` → `"--since=%s 00:00:00 +0900" % D`, `until` 인자도 `"--until=%s 00:00:00 +0900" % nxt`로 동일 패턴 적용.
1-1: 선행 조사(런처 스크립트 소스 위치 확인, `main.py` 종료 경로 그레핑으로 `sys.exit`/`QApplication.quit()`/예외 전파 추적) 후 종료 사유 3분류 로깅 보강 — 위치 미확정, 장후 세션에서 먼저 조사.

### 검증
1-2는 수정 후 리눅스 샌드박스 재실행으로 오늘 커밋 1건이 정상 표시되는지 확인. 1-1은 내일(10/9) 장전에도 2단 재시작이 재현되는지, 가동시간 추이(8분→6분처럼 변화하는지)를 관측(O-p1).

### 병행 세션
2026-10-08 00:00 KST~점검 시작(08:58) 사이 당일 커밋 1건(`a0f179f`, 08:51:15, 668차 후속4 — 전날 장후 세션의 연장) — 역링크: 변경 내역은 위 10/7 668차 기록(「668차 후속4 — 2026-10-08 장전 첫 기동 점검」) 참조, 결론 1줄 "피터2 대시보드 어댑터에 메서드 1개 추가해 AttributeError 해소", 이 장전 판정에 영향 — 반영 확인 후 추가 조치 없음으로 판정에 반영 완료(위 발견 ④). 그 외 딥다이브·특별조사 파일 없음. `.git/index.lock` 없음(`git_lock_guard.py --check` rc=0). 읽기전용 git 전량 `--no-optional-locks`. 코드 변경 없음, 라이브 DB 스캔 없음(08:45 이후 라이브 DB 분석 금지 구간 준수).

산출물: `docs/정기점검/매일점검/MW0601-20261008-점검리포트.md`(신규) · `evidence_MW0601-20261008_pre.md`(신규) · `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md`. 이 세션은 커밋하지 않음 — 커밋 대기: 위 산출물 + 경로 명시 add 필요(`git add .` 금지).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-06 (MW0601 660차 — 장중 점검)
## 2026-10-06 (MW0601 661차 — 장후 점검, 종합 완성본)
## 2026-10-06 (MW0601 663차 — 661차 후속 장후 자동조치)
## 2026-10-07 (MW0601 664차 — 장전 점검)
## 2026-10-07 (MW0601 666차 — 장후 점검, 종합 완성본)
## 2026-10-07 (MW0601 667차 — 666차 후속 장후 자동조치)
## 2026-10-07 (MW0601 668차 — 피터2 실시간 추종 신설)
## 2026-10-08 (MW0601 669차 — 장전 점검)
```

미완료 체크박스 **3050건** (끝에서 30건)
```
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
- [ ] **1-1 (P1, 신규)** 개장전(08:48·08:54) 원인불명 2회 자동 재시작 — watchdog 트리거 아님 확인(strikes=0, 동결센티나 FZ-2도 감시창 밖). 런처 종료사유 3분류 로깅 선행 조사 필요(위치 미확정) — 장후 세션에서 조사 착수.
- [ ] **O-p1 (신규, 다음 장전 판정)** 내일(10/9) 장전에도 개장전 2단 재시작이 재현되는지, 가동시간 추이(8분→6분) 지속되는지.
- [ ] **1-2 (P1, 신규)** `collect_evidence.py:2637` "당일 커밋" 시간대 미지정 결함(리눅스 샌드박스 전용, Windows 무관) — Fix: `"--since=%s 00:00:00 +0900" % D` / `until` 동일 패턴. 사용자 승인 후 장후 적용.
- [ ] 663-3(부팅 access violation 코드 직접 검토, `dashboard/main_dashboard.py:7240~7250`) 지속 — 오늘도 미착수, 다음 장후로 이월.
- [ ] 663-4(git diff 타임아웃 2차 호출 생략 검증) 지속 — 오늘도 조건 미발생(타임아웃 0건).
- [ ] 663-1(F-5)·663-2(F-7)·F-1(538-4)·F-2·G-3 — 전부 지속, 변화 없음(사용자 승인/선택 대기).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
드) 재발 시 `[주문요청]`도 함께 빠지는지 재확인(§1-5 패턴 일반성 확인) — 다음 재발 1건으로 패턴 재확인.
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

### `data/heartbeat_MW0601_20261008.json` — 243B · 10-08 12:27:15
```json
{
 "pid": 29516,
 "written_at": "2026-10-08T12:27:45",
 "beat_epoch": 1791430062.2062032,
 "beat_age_sec": 3.2,
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

### `data/peter_feed/_raw/2026-10-08.jsonl` — 2.3KB · 10-08 12:18:23
```json
JSONL 12행 ⏎ 첫: {"id": "2107986754829697490", "dt": "2026-10-08T00:09:41.000Z", "text": "1070 부근에서 반등 가능성 큼.\n\n만약 1070 밑으로 떨어지면 매수 기회니까 대기.", "seen_at": "2026-10-08T09:09:53+09:00", "src": "live"} | {"id": "2107990718077972868", "dt": "2026-10-08T00:25:26.000Z", "text": "1072 상방돌파시 매수. 손절가 1068", "seen_at": "2026-10-08T09:25:54+09:00", "src": "live"} | {"id": "2107990891164209552", "dt": "2026-10-08T00:26:07.000Z", "text": "1072 매수체결.", "seen_at": "2026-10-08T09:26:24+09:00", "src": "live"} ⏎ 끝: {"id": "2108032910918082689", "dt": "2026-10-08T03:13:05.000Z", "text": "1064 손절", "seen_at": "2026-10-08T12:13:23+09:00", "src": "live"} | {"id": "2108033892410335482", "dt": "2026-10-08T03:16:59.000Z", "text": "1063 상방 돌파시 재매수. 손절 1060", "seen_at": "2026-10-08T12:17:24+09:00", "src": "live"} | {"id": "2108034141199757606", "dt": "2026-10-08T03:17:59.000Z", "text": "1063 매수체결.", "seen_at": "2026-10-08T12:18:23+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-08 09:22:04**

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
| `raw_candles` 당일 max ts | **12:26** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 12:27 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 215 |
| `session_bars` 당일 행수 | 215 (기대 411) |

- 미도래 **162봉** (12:27~15:08) — 수집 시각 12:27 이후라 결손·영구결손에서 제외
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

### `docs/정기점검/매일점검` — 205개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261008-점검리포트.md` | 19.6KB | 10-08 09:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20261008_pre.md` | 64.9KB | 10-08 08:59 |
| `docs/정기점검/매일점검/MW0601-20261007-점검리포트.md` | 85.5KB | 10-07 17:31 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_post.md` | 92.8KB | 10-07 16:17 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261007.md` | 17.4KB | 10-07 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_intra.md` | 80.5KB | 10-07 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261007_pre.md` | 60.1KB | 10-07 08:59 |
| `docs/정기점검/매일점검/MW0601-20261006-점검리포트.md` | 87.4KB | 10-06 17:34 |

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

1. `logs/20261008_WARN.log`: ERROR 이상 11건
2. `logs/20261008_WARN.log`: **Traceback** 출현 5건 — 크래시/메모리 계열
3. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
4. 메인 스레드 정지 5초 초과 **1건** (최대 6437ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
5. `logs/20261008_SYSTEM.log`: **ConstOut** 5건(표본)
6. `logs/20261008_SIGNAL.log`: **WeightCollapse** 8건(표본)
7. `logs/20261008_SIGNAL.log`: **ConstOut** 8건(표본)
8. `logs/20261008_LEARNING.log`: **축퇴** 8건(표본)
9. `logs/crash_fault.log`: `Windows fatal exception` **9건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
10. 런처 재시작 같은 날 **2회** (08:48 일시적 크래시, 08:54 일시적 크래시) — 재시작 간격·가동시간이 줄어드는지 §9 「프로세스 종료 3축 대사」에서 볼 것 (661차 G-3)
11. 미커밋 변경 81건 (실질 10건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261008*.log` (Windows) / `grep 강제청산 logs/*20261008*.log`*