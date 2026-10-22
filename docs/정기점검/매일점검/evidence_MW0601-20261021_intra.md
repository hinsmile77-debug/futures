# 미륵이 증거 다이제스트 — 2026-10-21 / INTRA

- 생성 2026-10-21 12:26:31 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01u2myacyrbhgupxzg5r555q/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261021` · `2026-10-21` · `261021` · `1021`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261021.log` | 124B | 10-21 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261021.log` | 198B | 10-21 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261021.json` | 244B | 10-21 12:26 |
| `launcher_{DATE}_084001_4597.log` | 1 | `logs/Mireuk_batch/launcher_20261021_084001_4597.log` | 1.6MB | 10-21 12:26 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261021.log` | 108B | 10-21 08:44 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261021.log` | 7.1KB | 10-21 11:52 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261021.log` | 20.9KB | 10-21 12:25 |
| `position_state.json.gen_{DATE}_121544` | 1 | `data/position_state.json.gen_20261021_121544` | 1.5KB | 10-21 12:12 |
| `position_state.json.gen_{DATE}_122513` | 1 | `data/position_state.json.gen_20261021_122513` | 1.5KB | 10-21 12:25 |
| `position_state.json.gen_{DATE}_122611` | 1 | `data/position_state.json.gen_20261021_122611` | 1.6KB | 10-21 12:26 |
| `retrain_intraday_20260703_{DATE}00.log` | 1 | `logs/retrain_intraday_20260703_102100.log` | 4.6KB | 07-03 10:21 |
| `retrain_intraday_20260706_{DATE}58.log` | 1 | `logs/retrain_intraday_20260706_102158.log` | 4.6KB | 07-06 10:22 |
| `retrain_intraday_{DATE}_115100.log` | 1 | `logs/retrain_intraday_20261021_115100.log` | 3.2KB | 10-21 11:51 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261021.log` | 60.6KB | 10-21 12:22 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-21.jsonl` | 797B | 10-21 11:44 |
| `{DATE}_0902_D.xls` | 1 | `data/db/option_hts/261021_0902_D.xls` | 482.8KB | 10-21 09:02 |
| `{DATE}_1214_D.xls` | 1 | `data/db/option_hts/261021_1214_D.xls` | 483.1KB | 10-21 12:14 |
| `{DATE}_DATA.log` | 1 | `logs/20261021_DATA.log` | 231.3KB | 10-21 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261021_DEBUG.log` | 150.7KB | 10-21 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261021_HEALTH.log` | 3.5KB | 10-21 12:22 |
| `{DATE}_HOGA.log` | 1 | `logs/20261021_HOGA.log` | 33.1MB | 10-21 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261021_LEARNING.log` | 179.9KB | 10-21 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20261021_MICRO.log` | 627.9KB | 10-21 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20261021_PROBE.log` | 55.4KB | 10-21 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261021_SIGNAL.log` | 391.1KB | 10-21 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261021_SYSTEM.log` | 663.7KB | 10-21 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20261021_TRADE.log` | 31.2KB | 10-21 12:26 |
| `{DATE}_WARN.log` | 1 | `logs/20261021_WARN.log` | 472.6KB | 10-21 12:26 |

## 2. 코드·커밋 상태

- HEAD `50dcb0f1` · 브랜치 `v9-dev` · 미커밋 29건 · 실질 변경 3건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 3 · 미추적 26 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.5초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md
?? docs/가격움직임패턴연구/
?? docs/미륵이고도화3/시장국면/
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261020.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261021.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261019.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261020.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261020.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261021.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261019.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261020.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_claude_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261020.md
?? docs/신동거래/일일/신동_일일_MW0601_20261020.svg
?? docs/정기점검/매일점검/MW0601-20261019-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261020-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261021-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261021_pre.md
```

**당일(2026-10-21) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
50dcb0f1 [MW0601] 신동 실거래 수량 SHINDONG_LIVE_QTY 1 → 2 (사용자 결정 2026-10-21)
26b8e9c3 [MW0601] 700차: 신동 섀도 SHADOW_ATRS(R3 손절 0.25×ATR14) · TR44 반사실 · 방향 적중 비교 자료
```

**최근 커밋 12건**
```
50dcb0f1 [MW0601] 신동 실거래 수량 SHINDONG_LIVE_QTY 1 → 2 (사용자 결정 2026-10-21)
26b8e9c3 [MW0601] 700차: 신동 섀도 SHADOW_ATRS(R3 손절 0.25×ATR14) · TR44 반사실 · 방향 적중 비교 자료
d63de063 [MW0601] 699차 후속: 신동 보완 분석 세션 자료 모음 — docs/미륵이고도화3/신동2/신동보완분석_MW0601-20261020/
8a1ddebc [MW0601] 699차 후속: DECISION_LOG 제목 정정 — 「실주문 로직 변경」 → 「가상 집행 변경 — 신동 선택 시 실주문」
e612cbab [MW0601] 699차: 신동 규격 v3 — TR44 → MAIN 승격 · SHADOW_V2(되돌림 기준) · MW0602 보완 판정 사전등록
c045a60e [MW0601] 641차 이식 후속: 고착 전일 「갭」 판정 레슨 메모 · 지표 I1–I3 재검증(근월물 수정 후)
26006d0e [MW0602] 641차: 「정규봉 적재 중단」 딥다이브 — 미니 근월물 A056A 하드코딩 수정 + research 금요일 17:00
cb086cf9 [MW0601] 640차 이식 §4-3·§4-5: 레슨 축 소급 부여 L1–L20 · 첫 trend(AI 대 MAIN) · 지표 I1–I3 검증
29f11de3 [MW0601] 640차 이식 §4: 사전등록 SD2AI-MW0601-2026-10-20-v1 · SKILL 규격 표현 · research 금요일 17:00
10cd8a51 [MW0602] 640차 후속: MW0601(v9-dev) 이식 보강 + 이식 가이드
e5c35a41 [MW0602] 640차: 맥점×옵션사다리 개선 5단계 — 신동2 AI 를 신동 MAIN·섀도의 경쟁자로
256218db [MW0601] 698차 후속: 장후 자동조치 — F-1 보강(test_514 기대값) · F-2 원인 확정(헛경보) 기록 (+ 10-20 장전·장중·장후 dev_memory)
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `1` | `1` | 일치 | 431차 10→3 인하 → [2026-10-13 사용자 결정 56cc917] CREON 실거래 전환으로 3→1 (1계약 명목가치만 실운영금 1,500만원의 약 … |
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

### 차단 게이트 전수 인벤토리 — 45개 중 **9개 꺼짐**

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
| `ALERT_MAIL_ENABLED` | True | — |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
| `DAILY_CLOSE_FORCE_EXIT_ENABLED` | True | — |
| `EXIT_LIMIT_FALLBACK_ENABLED` | True | — |
| `EXIT_REJECT_BLOCK_ENTRIES` | True | — |
| `FORCE_FLAT_GUARD_ENABLED` | True | — |
| `FREEZE_SENTINEL_ENABLED` | True | — |
| `FREEZE_SENTINEL_MAIL_ENABLED` | True | — |
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

_본문 미열람(설정): `20261021_HOGA.log` 33.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20261021_115100.log`, `20261021_MICRO.log`, `20261021_DATA.log`, `20261021_PROBE.log`, `launcher_20261021_084001_4597.log`, `20261021_DEBUG.log`, `shindong2_20261021.log`, `peter2_receiver_20261021.log`_

### `logs/20261021_TRADE.log` — 31.2KB · 235행 · 최종 12:26:11

- 형식 평문 · 시각 인식 235행 · WARNING=13, INFO=222

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-21 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-21 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-21 09:02:13 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 878.16 | 손절=882.72 1차=-9121.84(×1.00) 2차=-9121.84
2026-10-21 09:02:13 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=2 entry=878.16 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-10-21 09:02:13 [INFO] TRADE: [Virtual] 신동 가상진입 SHORT 2계약 @878.16 손절 882.72 목표 864.50 (principal)
  …
2026-10-21 12:26:11 [INFO] TRADE: [체결청산-부분] LONG 1계약 @ 891.48 | PnL=-2.32pt (-117,698원) | 잔여=1계약 | 사유=하드스톱(틱)
2026-10-21 12:26:11 [INFO] TRADE: [Chejan] 상태=정정확인 주문번호=1117 code=A056B 방향=SHORT 체결=2 미체결=0
2026-10-21 12:26:11 [INFO] TRADE: [Chejan] 상태=체결 주문번호=1117 code=A056B 방향=SHORT 체결=1 미체결=0
2026-10-21 12:26:11 [INFO] TRADE: [Position] 체결청산 LONG @ 891.46 | PnL=-2.34pt (-118,698원) | 하드스톱(틱)
2026-10-21 12:26:11 [INFO] TRADE: [청산 완료] PnL=-2.33pt (-236,396원) | 포지션 합계 -236,396원 (레그 2)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 12 | 09:02:13 | 12:25:13 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=2 entry=878.16 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `ProfitGuard-L4` | 1 | 11:38:57 | 11:38:57 | 수익 보존 CB 발동 — 당일 수익 +1,559,970원 상태에서 2연속 손실 → 당일 진입 중단 |

**채널** — `TRADE`×235

**컴포넌트 상위 15** — `Chejan`×56, `Position`×47, `ShindongExec`×32, `주문요청`×16, `Sizer`×15, `Virtual`×14, `PositionFallback`×12, `진입체크`×9, `체결진입`×8, `청산 완료`×7, `TickStop-S0C`×6, `체결청산-부분`×6, `체결진입보정`×3, `ProfitGuard`×1, `자동진입 차단`×1

### `logs/20261021_WARN.log` — 472.6KB · 2064행 · 최종 12:26:23

- 형식 평문 · 시각 인식 2064행 · ERROR=1, WARNING=2063

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-21 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-21 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3188ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3188 band=INFO since_pipe_s=NA
2026-10-21 08:41:12 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr67)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-21 08:41:12 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr67)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
  …
2026-10-21 12:26:13 [WARNING] SYSTEM: [LiveDBG] _fetch_investor_data 지연 638ms — 메인 스레드 638ms 점유 (live 중단 원인 후보)
2026-10-21 12:26:13 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 103.9ms | size=1484x911 candles=222 grid=28.0 spans=14.2 candles=8.5 dir=0.8 regime=6.0 markers=33.2 axes=11.8 cross=0.0 | slow_cnt=1540 total_cnt=1862 overlay_cnt=22903
2026-10-21 12:26:23 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 114.9ms | size=1484x911 candles=222 grid=31.1 spans=12.7 candles=8.3 dir=0.8 regime=6.5 markers=38.7 axes=15.7 cross=0.0 | slow_cnt=1541 total_cnt=1863 overlay_cnt=22924
2026-10-21 12:26:34 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 112.3ms | size=1484x911 candles=222 grid=33.6 spans=14.0 candles=8.4 dir=1.0 regime=7.5 markers=33.3 axes=13.2 cross=0.0 | slow_cnt=1542 total_cnt=1864 overlay_cnt=22945
2026-10-21 12:26:44 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 112.4ms | size=1484x911 candles=222 grid=33.3 spans=14.4 candles=8.2 dir=0.8 regime=7.2 markers=33.9 axes=13.4 cross=0.0 | slow_cnt=1543 total_cnt=1865 overlay_cnt=22965
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `FixB` | 1 | 11:44:13 | 11:44:13 | open_position 실패 direction=SHORT status_before=SHORT err=이미 포지션 보유 중 | 파라미터=entry_horizon=None hurst=None extra_stop_mult=1.0 pass_count=10 (pending 경유로 apply_entry_fill이 승계) |

<details><summary>ERROR/FixB 원문 1건</summary>

```
2026-10-21 11:44:13 [ERROR] SYSTEM: [FixB] open_position 실패 direction=SHORT status_before=SHORT err=이미 포지션 보유 중 | 파라미터=entry_horizon=None hurst=None extra_stop_mult=1.0 pass_count=10 (pending 경유로 apply_entry_fill이 승계)
```

</details>

**WARNING — 태그 38종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1543 | 08:50:41 | 12:26:44 | paintEvent slow 41.1ms | size=1994x950 candles=6 grid=19.4 spans=0.0 candles=0.2 dir=0.0 regime=0.0 markers=0.0 axes=20.5 cross=0.0 | slow_cnt=1 total_cnt=54 overlay_cnt=444 |
| `LiveDBG` | 144 | 08:41:09 | 12:26:13 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 56 | 09:34:13 | 12:26:11 | account='783343908' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='339' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:34:13.336' | positio… |
| `ChejanMatch` | 56 | 09:34:13 | 12:26:11 | order_no='339' | pending='ENTRY:SHORT qty=2 filled=0 order_no=339 reason=진입 req_at=09:34:13.336' | pending_matched=True |
| `OptionFlowChart` | 40 | 08:41:22 | 12:25:12 | 그리기 73.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 774x1001 |
| `PendingOrder` | 32 | 09:34:13 | 12:26:11 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 896.16, 'reason': '진입', 'hint_source': '', 'atr': 2.0057, 'grade': 'S', 'stage': None, 'order_no': '', 'filled_qt… |
| `EntryAttempt` | 16 | 09:34:13 | 12:25:13 | atr=2.0057 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='SHORT' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='S' | pending='NONE' |… |
| `CybosMarginQty` | 15 | 09:30:00 | 11:10:01 | 조회 실패 ret=0 status=-1 msg=11298 시장가/신고대량/최우선/최유리지정가 주문은 단가를 입력하지 않습니다. (ordsvr46)(ord.fo.dpmyinqr.selanwordpsblqty) account=783343908 code=A056B |
| `ExitCooldown` | 14 | 10:12:39 | 12:26:11 | 하드스톱(틱) 후 2분 재진입 금지 (until 10:14:39) |
| `ExitFillFlow` | 13 | 10:12:39 | 12:26:11 | after='SHORT 1계약 @ 896.07' | before='SHORT 2계약 @ 896.07' | fill_price=885.64 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:SHORT qty=2 filled=1 order_no=523 reason=하드스톱(틱) req_at=10:12:39.431' | reason='하드스톱(틱)' |
| `Peter2Offset` | 11 | 08:47:13 | 11:13:12 | A056B 실측=-1.99 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-1.99 | 직전일=-1.82(prev_day:2026-10-19, safe=True) 차=-0.17 | 48ms |
| `Health` | 11 | 09:00:01 | 12:21:00 | level=WARNING degraded=OFF | latency=1089ms | quality=1.00 | cache_age=50s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |

**채널** — `SYSTEM`×2053, `HEALTH`×11

**컴포넌트 상위 15** — `ChartDBG`×1543, `LiveDBG`×144, `ChejanFlow`×56, `ChejanMatch`×56, `OptionFlowChart`×40, `PendingOrder`×32, `EntryAttempt`×16, `CybosMarginQty`×15, `ExitCooldown`×14, `ExitFillFlow`×13, `Peter2Offset`×11, `Health`×11, `EntryFillFlow`×11, `PipePerf`×10, `CB⑤`×10

### `logs/20261021_SYSTEM.log` — 663.7KB · 4291행 · 최종 12:26:30

- 형식 평문 · 시각 인식 4284행 · INFO=4284, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 로테이션 — 9.7MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-10-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=24328 | 행감지=30s all_threads=True
2026-10-21 08:40:47 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.04s trades=0.22s daily_stats=0.01s shap=0.00s raw_data=0.11s broker_pnl=0.02s broker_recon=0.00s premarket_levels=0.03s
2026-10-21 08:40:47 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-21 08:40:47 [INFO] SYSTEM: [System] 미륵이 초기화
  …
2026-10-21 12:26:25 [INFO] SYSTEM: [TickUI] alive ticks=90070 code=A056B close=891.10
2026-10-21 12:26:30 [INFO] SYSTEM: [CybosRT-TICK] #90100 code=A056B raw_time=122630 parsed=12:26:30 price=891.00 vol=1 bid1=891.00 ask1=891.08 flag=50 side=SELL anchor=0/1
2026-10-21 12:26:32 [INFO] SYSTEM: [OptionChain][Worker] 완료 3025ms | target=48 valid=48 PCR=1.228 ATM_PCR=0.686 GEX=-0.57B
2026-10-21 12:26:41 [INFO] SYSTEM: [CybosRT-TICK] #90200 code=A056B raw_time=122641 parsed=12:26:41 price=891.72 vol=1 bid1=891.66 ask1=891.70 flag=49 side=BUY anchor=1/0
2026-10-21 12:26:42 [INFO] SYSTEM: [PumpGuard] rollover 연기 — 메인 펌프(BlockRequest 대기) 중 재진입 회피 (누적 392회, 재시도=호출부)
```

</details>

**채널** — `SYSTEM`×4284

**컴포넌트 상위 15** — `CybosRT-TICK`×907, `CybosInvestorRaw`×824, `PumpGuard`×392, `TickUI`×221, `CybosRT-ROLLOVER`×221, `BAR-CLOSE`×221, `CVD-ANCHOR`×221, `S6Detail`×207, `PipePerf`×207, `CybosEvent`×112, `BalanceUI`×89, `BalanceRefresh`×65, `CybosDailyPnl`×60, `System`×59, `MicroRegime`×47

### `logs/20261021_SIGNAL.log` — 391.1KB · 3336행 · 최종 12:26:00

- 형식 평문 · 시각 인식 3336행 · WARNING=1556, INFO=1780

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-10-21 12:26:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=37.6% grade=X regime=NEUTRAL
2026-10-21 12:26:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-10-21 12:26:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=37.6% grade=X micro=추세장
2026-10-21 12:26:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.376<mc0.620)
2026-10-21 12:26:00 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L4-ProfitCB] 수익 보존 CB 발동 (0연속 손실) | src=engine(net·시스템진입만)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1032 | 09:00:01 | 12:23:02 | 1m 'macro_vix' scale=0.0472 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 203 | 09:00:00 | 12:24:00 | ts=08:59 horizon=1m age=1m max_z=-10.79(institution_futures_net) extreme=1 adj=1 |
| `Model` | 180 | 09:00:00 | 12:22:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 76 | 09:06:00 | 12:15:00 | 신뢰도 미달 36.3% < 39.0% → 강제 X등급 |
| `WeightCollapse` | 45 | 09:07:01 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 12 | 08:45:13 | 08:45:13 | 1m CORE 'cvd_divergence' raw_std≈0(0.0263) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 7 | 09:35:00 | 11:50:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 1 | 11:47:01 | 11:47:01 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×3336

**컴포넌트 상위 15** — `ScalerFloor`×1050, `SIGNAL`×414, `Ensemble`×210, `FQAdj`×206, `ScalerMonitor`×203, `MetaGate`×199, `Model`×192, `ZeroDiag`×170, `Checklist`×110, `ATR-Horizon`×95, `ScalerRefresh`×49, `차단`×49, `ProfitGuard`×48, `MicroRegime`×47, `WeightCollapse`×45

### `logs/20261021_LEARNING.log` — 179.9KB · 1671행 · 최종 12:26:00

- 형식 평문 · 시각 인식 1671행 · WARNING=146, INFO=1525

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-21 08:40:48 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-21 08:40:51 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3298 < conf_floor=0.3300 (span=0.00065 auc=0.567 out_max=0.3298, 기저율=0.3294 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-21 08:40:51 [INFO] LEARNING: [Calibration:1m] 도달불가 해소 — out_max=0.3337 < conf_floor=0.3300 (n=90) → 보정 재적용
2026-10-21 08:40:51 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3010 < conf_floor=0.3300 (span=0.00174 auc=0.693 out_max=0.3010, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-21 08:40:51 [INFO] LEARNING: [Calibration:30m] 도달불가 해소 — out_max=0.3304 < conf_floor=0.3300 (n=85) → 보정 재적용
  …
2026-10-21 12:26:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=40.6% 예측=FL 실제=DN)
2026-10-21 12:26:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=42.1% 예측=FL 실제=DN)
2026-10-21 12:26:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=42.4% 예측=FL 실제=DN)
2026-10-21 12:26:00 [INFO] LEARNING: [Bias⚠] 5m 적중=38%(9/24) UP=3 DN=5 FL=16 [FL편향⚠ 67%]
2026-10-21 12:26:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 43 | 08:40:51 | 09:47:00 | 하한 도달불가 — out_max=0.3010 < conf_floor=0.3300 (span=0.00174 auc=0.693 out_max=0.3010, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:1m` | 40 | 08:40:51 | 11:25:00 | 하한 도달불가 — out_max=0.3298 < conf_floor=0.3300 (span=0.00065 auc=0.567 out_max=0.3298, 기저율=0.3294 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 23 | 08:40:52 | 12:00:00 | 하한 도달불가 — out_max=0.2882 < conf_floor=0.3300 (span=0.00120 auc=0.625 out_max=0.2882, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 22 | 08:40:52 | 11:00:00 | 축퇴 감지 — span=0.00021 auc=0.521 out_max=0.3751 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:10m` | 10 | 08:40:52 | 08:41:00 | 하한 도달불가 — out_max=0.2753 < conf_floor=0.3300 (span=0.00050 auc=0.543 out_max=0.2753, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 4 | 08:40:52 | 08:40:58 | 축퇴 감지 — span=0.00073 auc=0.467 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 2 | 08:41:00 | 09:12:00 | 복원한 보정기가 하한 도달불가 — out_max=0.3102 < conf_floor=0.3300 (span=0.01100 auc=0.542 out_max=0.3102, n=4520) → 보정 미적용으로 시작, raw 통과. 축퇴(auc/span)와 별개 사유이며, 표본이 쌓여 출력상한이 하한 위로 올라오면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 2 | 09:47:00 | 11:05:00 | total=490ms raw_fetch=13ms pred_select=466ms pred_update=8ms pred_insert=0ms verified=3 |

**채널** — `LEARNING`×1671

**컴포넌트 상위 15** — `LEARNING`×664, `SGD`×207, `sigma`×194, `Bias⚠`×123, `Calibration:30m`×86, `Calibration:1m`×79, `Bias`×74, `Calibration:5m`×45, `Calibration:3m`×42, `MetaConf`×41, `ScalerWarmup`×37, `Calibration:10m`×20, `OnlineLearner`×17, `BiasReset`×12, `Calibration:15m`×8

### `logs/20261021_HEALTH.log` — 3.5KB · 22행 · 최종 12:22:00

- 형식 평문 · 시각 인식 22행 · WARNING=11, INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-21 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1089ms | quality=1.00 | cache_age=50s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1
2026-10-21 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=530ms | quality=1.00 | cache_age=109s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1
2026-10-21 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 324ms (표본 20분)
2026-10-21 09:45:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=370ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1
2026-10-21 09:46:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=333ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[Peter2]×1
  …
2026-10-21 11:30:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=412ms | quality=1.00 | cache_age=56s | exceptions_10m=0
2026-10-21 11:52:05 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=4921ms | quality=1.00 | cache_age=97s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [FixB]×1
2026-10-21 11:53:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=511ms | quality=1.00 | cache_age=152s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [FixB]×1
2026-10-21 12:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=276ms | quality=0.94 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
2026-10-21 12:22:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=502ms | quality=0.94 | cache_age=59s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 11 | 09:00:01 | 12:21:00 | level=WARNING degraded=OFF | latency=1089ms | quality=1.00 | cache_age=50s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |

**채널** — `HEALTH`×22

**컴포넌트 상위 15** — `Health`×21, `HealthTrend`×1

### `logs/retrain_intraday_20260703_102100.log` — 4.6KB · 39행 · 최종 10:21:31

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-03 10:21:00,648 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-03 10:21:00,649 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-03 10:21:00,649 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-03 10:21:00,649 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a42a8dfe.json
2026-07-03 10:21:02,227 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-03 10:21:31,917 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.40s | old_acc=nan)
2026-07-03 10:21:31,920 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-03 10:21:31,921 [INFO] LEARNING: [Retrain] 완료 | 29.7초 | 성공=6/6 호라이즌
2026-07-03 10:21:31,922 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 31.3s 데이터=20000행
2026-07-03 10:21:31,924 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a42a8dfe.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260706_102158.log` — 4.6KB · 39행 · 최종 10:22:33

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-06 10:21:58,335 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-06 10:21:58,336 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-06 10:21:58,336 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-06 10:21:58,336 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ac6ead15.json
2026-07-06 10:22:00,348 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-06 10:22:33,128 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.40s | old_acc=nan)
2026-07-06 10:22:33,131 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-06 10:22:33,131 [INFO] LEARNING: [Retrain] 완료 | 32.8초 | 성공=6/6 호라이즌
2026-07-06 10:22:33,133 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.8s 데이터=20000행
2026-07-06 10:22:33,135 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ac6ead15.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 9 |
| 진입 등록(`[Position] 진입`) | 13 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 0 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 7 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 6 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 8  ※ 두 형식 중복 2건 접음 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 7 |
| 차단(`[차단]`) | 49 |
| 사이저 호출(`[Sizer]`) | 15 |

> 🔴 **엔진 진입 0건인데 계좌 체결 8건**(외부표식 0 · 피터2 0 · 판별불가 6) — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.
>
> 별도로 **가상 장부 진입 7건**이 `[Position] 진입` 에 섞여 있다 — 실주문이 없으므로 계좌 체결·손익과 무관하다(아래 「가상 장부」 표).

### 포지션 7건 · 승 4 (57%) · 합계 +27.98pt (+1,375,164원)  ※ 레그 13행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:34:13 | 추정 | SHORT | 2 | — | 2 | +20.84 | +1,038,594 | 하드스톱(틱) |
| 10:17:13 | 추정 | LONG | 2 | — | 2 | +12.12 | +602,620 | 신동최종 |
| 10:48:13 | 추정 | LONG | 2 | — | 2 | +4.00 | +196,576 | 하드스톱(틱) |
| 11:30:13 | 추정 | SHORT | 2 | — | 2 | -3.86 | -196,412 | 하드스톱(틱) |
| 11:37:13 | 추정 | LONG | 2 | — | 2 | -1.56 | -81,408 | 하드스톱(틱) |
| 11:44:13 (추정귀속) | 추정 | SHORT | 2 | — | 1 | +1.10 | +51,590 | 하드스톱(틱) |
| 12:25:13 | 추정 | LONG | 2 | — | 2 | -4.66 | -236,396 | 하드스톱(틱) |

**출처별 소계** — 추정 7건 +1,375,164원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「피터2」는 `[Peter2] 진입`이 동반된 보조 로직 자리로 역시 엔진 성적이 아니다. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**가상 장부 7건(청산 7 · 합계 -192,275원) — 실주문 없음, 엔진·계좌 손익 아님**

| 진입 | 주체 | 방향 | 수량 | hz | 가상 pt | 가상 net(원) | 가상 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:02:13 | 신동 | SHORT | 2 | — | -9.12 | -459,337 | 가상:하드스톱 |
| 10:11:00 | 미륵 | SHORT | 1 | 5m | -3.55 | -178,981 | 가상:하드스톱 |
| 10:33:01 | 미륵 | LONG | 1 | 5m | +0.34 | +15,317 | 가상:하드스톱 |
| 10:40:00 | 미륵 | LONG | 1 | 3m | +3.80 | +188,298 | 가상:TP2(전량) |
| 10:45:00 | 미륵 | LONG | 1 | 3m | +4.14 | +205,290 | 가상:TP2(전량) |
| 10:54:00 | 미륵 | LONG | 1 | 1m | +0.39 | +17,768 | 가상:하드스톱 |
| 11:02:00 | 미륵 | LONG | 1 | 1m | +0.42 | +19,370 | 가상:하드스톱 |

> ⚠ 이 표는 `[Virtual] … 가상진입`/`가상청산` 로그로 조립한 **가상 장부**다. 같은 초에 `[Position] 진입` 이 찍혀 진입 건수에는 잡히지만 체결이 없다 — 3원 대사(로그·DB·브로커)에서 로그 쪽이 더 많아 보이면 먼저 이 표를 뺄 것.

> ⚠ **(추정귀속) 1건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 13행** (부분청산 6 · 전량청산 7)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:12:39 | 부분 | 1 | +10.43 | +519,797 | 하드스톱(틱) |
| 10:12:39 | 전량 | 1 | +10.41 | +518,797 | 하드스톱(틱) |
| 10:26:09 | 부분 | 1 | +3.25 | +160,810 | 신동1차 |
| 10:42:33 | 전량 | 1 | +8.87 | +441,810 | 신동최종 |
| 10:51:19 | 부분 | 1 | +2.88 | +142,288 | 신동1차 |
| 11:06:32 | 전량 | 1 | +1.12 | +54,288 | 하드스톱(틱) |
| 11:33:05 | 부분 | 1 | -1.92 | -97,706 | 하드스톱(틱) |
| 11:33:05 | 전량 | 1 | -1.94 | -98,706 | 하드스톱(틱) |
| 11:38:57 | 부분 | 1 | -0.77 | -40,204 | 하드스톱(틱) |
| 11:38:57 | 전량 | 1 | -0.79 | -41,204 | 하드스톱(틱) |
| 12:15:44 | 전량 | 2 | +0.55 | +51,590 | 하드스톱(틱) |
| 12:26:11 | 부분 | 1 | -2.32 | -117,698 | 하드스톱(틱) |
| 12:26:11 | 전량 | 1 | -2.34 | -118,698 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×10, `신동1차`×2, `신동최종`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 6/7건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +1,375,164 = 포지션합 +1,375,164 → OK · `[청산 완료]` 7건 = 조립 포지션 7건 → OK

### 진입 13건

| 시각 | 출처 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|---|
| 09:02:13 | 가상 | SHORT | 2 | 878.16 | — | — |
| 09:34:13 | 추정 | SHORT | 2 | 896.16 | — | — |
| 10:11:00 | 가상 | SHORT | 1 | 884.62 | 5m | trend |
| 10:17:13 | 추정 | LONG | 2 | 889.42 | — | — |
| 10:33:01 | 가상 | LONG | 1 | 894.84 | 5m | trend |
| 10:40:00 | 가상 | LONG | 1 | 895.86 | 3m | trend |
| 10:45:00 | 가상 | LONG | 1 | 900.16 | 3m | trend |
| 10:48:13 | 추정 | LONG | 2 | 901.26 | — | — |
| 10:54:00 | 가상 | LONG | 1 | 902.38 | 1m | trend |
| 11:02:00 | 가상 | LONG | 1 | 904.64 | 1m | neutral |
| 11:30:13 | 추정 | SHORT | 2 | 898.0 | — | — |
| 11:37:13 | 추정 | LONG | 2 | 896.78 | — | — |
| 12:25:13 | 추정 | LONG | 2 | 893.78 | — | — |

계약수 분포 — 1계약×6, 2계약×7

등급 분포 — `A급(원시C)`×9

**진입한 건들의 체크리스트 미통과 항목** — `prev`×3, `chas`×2, `fore`×1, `cvd`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×15

실제 진입 계약수 — **1계약**×6, **2계약**×7

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×15

### 차단 사유 49건 · 23종

| 건수 | 사유 |
|---|---|
| 23 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | 청산 후 쿨다운 — 32초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.1pt > ATR×5.0=9.9pt (시가=882.74 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.3pt > ATR×5.0=10.0pt (시가=882.74 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.2pt > ATR×5.0=9.8pt (시가=882.74 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.6pt > ATR×5.0=9.7pt (시가=882.74 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.6pt > ATR×5.0=10.0pt (시가=882.74 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.1pt > ATR×5.0=9.7pt (시가=882.74 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 10_chase |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.9pt > ATR×5.0=7.6pt (시가=882.74 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 11_countertrend |
| 1 | 자동진입 Degraded 정책 차단 — conf=38.3% < 62.0% |
| 1 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 1 | 청산 후 쿨다운 — 125초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×23, `3_vwap`×9, `6_foreign`×7, `7_prev_bar`×5, `4_cvd`×4, `5_ofi`×3, `11_countertrend`×3, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 3건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 10건 · 최대 9672ms · 5초 초과 2건

상위 — 9672ms, 5406ms, 4985ms, 3907ms, 3422ms, 3390ms, 3188ms, 2890ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 10:31:09 | 9672ms | 2283ms | **7389ms (76%)** |
| 11:52:05 | 5406ms | 4921ms | **485ms (9%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261021_WARN.log`
```
--- ConstOut ×1(표본)
11:50:00 2026-10-21 11:50:00 [WARNING] SYSTEM: [ConstOut] ['10m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(10m=0.3697)
--- [Brier] 과신 ×2(표본)
10:56:00 2026-10-21 10:56:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.353 > 0.35
10:57:00 2026-10-21 10:57:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.355 > 0.35
--- [CB] ×3(표본)
11:33:05 2026-10-21 11:33:05 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:38:57 2026-10-21 11:38:57 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
12:26:11 2026-10-21 12:26:11 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
10:12:39 2026-10-21 10:12:39 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:14:39)
10:12:39 2026-10-21 10:12:39 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:14:39)
10:42:33 2026-10-21 10:42:33 [WARNING] SYSTEM: [ExitCooldown] 신동최종 후 2분 재진입 금지 (until 10:44:33)
10:42:33 2026-10-21 10:42:33 [WARNING] SYSTEM: [ExitCooldown] 신동최종 후 2분 재진입 금지 (until 10:44:33)
--- [SHAP] 슬로우 ×1(표본)
12:13:02 2026-10-21 12:13:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1692ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-21 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3188ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3188 band=INFO since_pipe_s=NA
08:41:17 2026-10-21 08:41:17 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3422ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3422 band=INFO since_pipe_s=NA
08:51:20 2026-10-21 08:51:20 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3390ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3390 band=INFO since_pipe_s=NA
09:00:02 2026-10-21 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2890ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2890 band=INFO since_pipe_s=0.1
```

### `logs/20261021_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-21 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5567) | 앙상블 제외는 유지
09:44:00 2026-10-21 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3942) | 앙상블 제외는 유지
09:54:00 2026-10-21 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4036) | 앙상블 제외는 유지
10:50:00 2026-10-21 10:50:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5419) | 앙상블 제외는 유지
--- PSI ×8(표본)
09:00:00 2026-10-21 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:05:00 2026-10-21 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:10:00 2026-10-21 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:16:00 2026-10-21 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
```

### `logs/20261021_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-21 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1340 dir=-1)
09:35:00 2026-10-21 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-10-21 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-10-21 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1340 dir=-1)
--- WeightCollapse ×8(표본)
09:07:01 2026-10-21 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=69.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-10-21 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=53.2% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-10-21 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.5% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-21 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
08:40:43 2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
08:40:43 2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
08:40:43 2026-10-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
--- 안전망 ×8(표본)
09:07:01 2026-10-21 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-21 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-21 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-21 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261021_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-10-21 08:40:51 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3298 < conf_floor=0.3300 (span=0.00065 auc=0.567 out_max=0.3298, 기저율=0.3294 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-10-21 08:40:51 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3010 < conf_floor=0.3300 (span=0.00174 auc=0.693 out_max=0.3010, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-10-21 08:40:51 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3233 < conf_floor=0.3300 (span=0.00180 auc=0.664 out_max=0.3233, 기저율=0.3222 n=90) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-10-21 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00035 auc=0.530 out_max=0.3588 (기준 auc<0.53 and span<0.020, 기저율=0.3586 n=145) → 보정 미적용, raw 통과 [기존 fitted 해제]
```

### `logs/20261021_HEALTH.log`
```
--- [ExitCooldown] ×2(표본)
12:21:00 2026-10-21 12:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=276ms | quality=0.94 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
12:22:00 2026-10-21 12:22:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=502ms | quality=0.94 | cache_age=59s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261021_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 3 | 09:02:13 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=2 entry=878.16 — 진입 경로가 파라미터를 넘기지 … |
| 10:00 | 장중 초반 | 7 | 09:58:13 [INFO] 손절 891.84 → 890.94 (replay) |

- 이 로그 생존구간: 08:41 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261021_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 21 | 08:41:09 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 12 | 08:50:41 [WARNING] paintEvent slow 41.1ms | size=1994x950 candles=6 grid=19.4 spans=0.0 candles=0.2 dir=0.0 regime=0.0 markers=0… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 20 | 08:55:59 [WARNING] paintEvent slow 32.3ms | size=1484x950 candles=11 grid=13.3 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=… |
| 10:00 | 장중 초반 | 101 | 09:54:00 [WARNING] paintEvent slow 73.3ms | size=1484x912 candles=70 grid=27.4 spans=0.1 candles=2.6 dir=0.2 regime=3.6 markers=… |
| 12:00 | 장중 중간점 | 95 | 11:54:00 [WARNING] paintEvent slow 99.2ms | size=1484x911 candles=190 grid=25.0 spans=11.0 candles=8.2 dir=0.7 regime=5.3 marker… |

- 이 로그 생존구간: 08:41 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261021_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 103 | 08:40:46 [INFO] 로테이션 — 9.7MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 147 | 08:49:02 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 219 | 08:54:00 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 234 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 200 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:26

**매분 루프 커버리지 09:00~12:26: 207/207분 (100.0%)**

_장중 수집 — 분모를 수집 시각 12:26 까지로 줄였다. 이후 164분(~15:10)은 **미도래**라 제외(결손 아님)._

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261021_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:13 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0263) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 66 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 148 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 161 | 09:54:00 [WARNING] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| 12:00 | 장중 중간점 | 217 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=4m max_z=+4.27(opt_pcr_bearish) extreme=1 adj=1 |

- 이 로그 생존구간: 08:40 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261020 | 15:47 | 로그 본문 |
| 20261019 | 15:47 | 로그 본문 |
| 20261017 | 12:11 | 로그 본문 |
| 20261016 | 15:47 | 로그 본문 |
| 20261015 | 15:47 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261021** | **12:26** | 로그 본문 |

- 델타 **-201분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-20 (MW0601 — 장중 점검)
## 2026-10-20 (MW0601 — 장후 점검, 종합 완성본)
## 2026-10-20 (MW0601 698차 후속 — 장후 자동조치: F-1 구현 · F-2 원인 확정) — 🟢 **구현 · 조사 완료**
### F-1 — 증거 수집기·점검 체크리스트 기대값 동기화
### F-2 — `[RegimeFingerprint] 백필 0행 제외` 24거래일 연속 경보: **헛경보 확정 (가설 a·b 둘 다 아님)**
## 2026-10-20 (MW0601 699차 — 신동 규격 v3: TR44 → MAIN 승격 · MW0602 보완 판정 사전등록) — 🟢 **구현 완료 · 가상 집행 변경 — 신동 선택 시 실주문(R3 손절 갱신)**
## 2026-10-21 (MW0601 700차 — 신동 섀도 SHADOW_ATRS: R3 손절 0.25×ATR14) — 🟢 **구현 완료 · 섀도(기록만, 주문 없음)**
## 2026-10-21 (MW0601 — 장전 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 **결정(사용자)**: 방향 적중 비교(10-21 장전)에서 신동2(MW0601) R3 손절 중앙 3.48pt 가 1분 노이즈 안이라 「15:05 방향은 맞았는데 손실」 31% → 「손절 폭을 ATR 에 비례시키는 섀도」 권고안(k=0.25)으로 **지금 구현 · 금일 장 시작부터 채점**.
- **무엇을**: `SHADOW_ATRS` = v3 MAIN(TR44 트레일 포함) 그대로 + R3 초기 손절만 진입가 ∓ `R3_ATR_STOP_K`(0.25) × ATR14(08:50 `premarket_levels.atr14`, 일봉). 현행 손절보다 좁히지 않는다. ATR 없으면 현행 + `notes` 폴백 기록. R2 무변경. `VARIANTS` 끝에 추가 · `LATE_SHADOW_START["SHADOW_ATRS"] = 2026-10-21`. MAIN 무변경 → `SPEC_VERSION` 유지(632·598차 섀도 추가 관례).
- **Why(k)**: 「손절 ≤ R3 1차 목표 거리(중앙 8.67pt)」 — ATR14 30–42pt 에서 7.5–10.4pt. 성과 격자로 고르지 않았다.
- **참고(판정 아님, 등록 뒤 확인)**: v2 창 13일 소급 재생 ATRS +354.7만 · 최악 −177.0만 · 승 45/62 · SL 14 vs MAIN +519.9만 · −95.9만 · 50/85 · SL 34. 손절 횟수·승률은 좋아지고 한 번의 손절이 커진다(10-06 −177만). 결과를 보고 k 를 바꾸지 말 것.
- **How to apply**: 판정은 10-21부터 10거래일(2026-11-03경), 기존 섀도 규정. 채택 후보가 돼도 자동 승격 없음 — 새 SPEC_VERSION 개정으로만.
- **검증**: `tests/test_700_shindong_atrs_shadow.py` 6건(넓힘·좁히지 않음·폴백 기록·트레일 동일·라벨). 변형 목록을 고정하던 `test_598/626/632/699` 갱신. 신동 묶음 330 passed · 6 skipped(py37_32). 리포트 「섀도 흐름」에 `손절 폭 차이` 귀인 줄 추가.
- 근거: `docs/미륵이고도화3/신동2/신동보완분석_MW0601-20261020/방향적중_신동2MAIN(MW0601)vs신동MAIN(MW0602)_MW0601-20261021.md` · 사전등록 §6-1.

## 2026-10-21 (MW0601 — 장전 점검)

- **증상/관측**: ① `606-4` 기동 access violation(`main_dashboard.py:7434 _build`)이 오늘도 3건 재현 — 어제(10-20) 5거래일 연속에서 **6거래일 연속**으로 연장. ② 메인 스레드 블로킹 3건(최대 3422ms, 5000ms 임계 미달) — 기존 패턴 지속. ③ `SessionStateDrop`(`p8_last_success_date`·`eod_retrain_ok_date` 마커 유실) 10-21 재발 확인 — `[PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-20) → PreRetrain 스킵` 로그로 **실질 피해 없음**을 재확인(F-1 적용 전 현재 동작). ④ 옵션 체인 재수집 완료 시각이 09:01:26(10-19)→09:01:28(10-20)→09:01:32(10-21) **3거래일 연속 거의 동일** — "해소 유력" 관측을 **해소(설계된 정상 범위)**로 확정. ⑤ 계좌 실제잔고(25,005,259원) vs 기준자본(15,000,000원) 괴리 +66.7% — 기존 O-4 추이 기록(단일일 판정 금지) 갱신. ⑥ 이 계정 앱 저장 스킬 사본(rev 2026-08-26e)이 저장소 정본(rev 2026-09-07, 538차)보다 낡은 상태 재확인 — 이번 점검은 정본을 직접 Read해서 수행.
- **원인**: ①은 기존 미해결 결함(원인 미규명, 사용자 결정 대기). ③은 날짜 전환 시 `session_recovery_service.py:increment_session`이 새 세션 딕셔너리를 만들며 전일 마커를 이어받지 않는 기존 구조(F-1 대상). ⑤는 10-13 실거래 전환으로 기준값이 실운영금(1,500만원)으로 바뀐 뒤 누적 수익이 반영된 결과.
- **결정**: 새 Fix·고도화 항목 없음 — ①·②·③·⑤·⑥ 전부 이미 추적 중인 기존 항목이라 신규로 올리지 않는다(함정① 방지). ④만 "해소"로 상태 전환.
- **Why**: `dev_memory/NEXT_TODO.md`의 `606-4`·`F-1`·`O-4`·스킬 사본 드리프트 항목과 중복 등재를 피하기 위함.
- **How to apply**: 해당 없음(관측 점검, 코드 변경 없음). 장전·장중 코드 변경 금지 원칙 준수.
- **검증**: `docs/정기점검/매일점검/evidence_MW0601-20261021_pre.md` · `docs/정기점검/매일점검/MW0601-20261021-점검리포트.md` §1 참조. 장중 점검이 O-p1(캐너리 z경고 재상승)·O-p2(피터2 오프셋 표본 확대)를 재확인한다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2026-10-19 (MW0601 697차 후속2 — 장후 자동조치)
### 2026-10-20 (MW0601 698차 — 피터2 단독 수집 전환)
### 2026-10-20 (MW0601 — 장전 점검)
### 2026-10-20 (MW0601 — 장중 점검)
### 2026-10-20 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-20 (MW0601 698차 후속 — 단독 수집 첫날 판독, 16:40)
### 2026-10-20 (MW0601 698차 후속 — 장후 자동조치)
### 2026-10-21 (MW0601 — 장전 점검)
```

미완료 체크박스 **3277건** (끝에서 30건)
```
- [ ] (참고) 이 계정 앱 저장 스킬 사본(rev 2026-08-26e)이 저장소 정본(rev 2026-09-07, 538차)보다 낡음 — 사용자가 해당 PC에서 재저장하면 해소. 이 세션은 스킬 저장 도구에 접근 불가.
- [ ] **1-3 (P2, 장후 판정 대기)** 피터2 오프셋 보정값(`PETER2_OFFSET_TOL_PT`) spread가 08:58~11:23 구간 n=30까지 쌓여도 0.31~0.40 사이로 전혀 0.30 이하로 내려오지 않음 — 장후 점검이 하루 전체 추이로 "안정화됐는지/계속 불안정했는지" 최종 판정. 안정화 안 되면 `main.py:_pe…
- [ ] **O-p2 (판정보류 → 장후)** 캐너리 z경고 재상승 — 09:00~12:26 구간 재측정 로그 0건. 장후 점검이 `grep -c "Canary" logs/20261019_*.log`로 하루 전체 측정 횟수 재확인하고, 장중 미측정이 설계상 정상(1회성 장전 체크)인지 `main.py`에서 확인.
- [ ] **F-1 (C, 사용자 결정)** 피터2 X 전용 계정 분리(697-3 분기 충족 — 1-4 p90 237.2초 FAIL · 창별 rem 소진 > 우리 관측). 결정 후 별도 세션 구현.
- [ ] **R-1 (C, 승인 대기)** `latency_report.py` 일별 p90·429·PAGE_ERROR 를 누적하는 관찰 스크립트 — 10거래일 후 p90 vs 피터2 순손익 일자단위 상관(313차 5갈래). 표본 1일이라 자동 구현 제외, 도구 자체는 무위험.
- [ ] **G-2(10-16) 보류 유지** 재시도·캐시 보강은 공유 소비 판정 하에서 한도 소진을 키운다 — F-1 결정 이후 재평가.
- [ ] **1-3 (C)** `PETER2_OFFSET_TOL_PT`/`_peter2_measure_offset()` 창 재검토 — 복수 거래일 spread>0.30 지속 시 안건.
- [ ] **698-1 (10-20 장중·장후)** RATE 우리 요청 사이 rem 감소가 1로 떨어졌는가(① 외부 소진 중앙 ≤ 3). 아니면 MW0602 중지 미반영 → 사용자 확인.
- [ ] **698-2 (매 장후, 5거래일)** `collect_evidence --phase post` §9-e 확인 · 최종 판정은 평가 창 5거래일 도달 시(빠르면 10-26 장후). IMPROVED → F-4·G-2 종결 / NOT_LIMIT → 03 §2 혼자 소진 가지 / STILL_SHARED → 사용자 확인.
- [ ] **R-1 연계** 지연 누적은 698 추적기가 대신한다 — 5거래일 후 R-1(지연 vs 피터2 손익) 필요성 재평가.
- [ ] **F-1 (P2, 저부담 문서동기화)** `collect_evidence.py`의 `MAX_CONTRACTS` 기대값 3→1 정정 · `.claude/skills/mireuk-daily-check/references/phases.md` 32행 `joblib 1.1.1`→`1.1.0` 정정. 매매 로직 무관, 사용자 승인 불필요, 적용은 장후.
- [ ] **(이월, 변경 없음)** 606-4 기동 access violation(1-1, `main_dashboard.py:7434 _build`) — 10-20으로 관측일 추가(최소 2거래일 연속), 여전히 사용자 결정 대기.
- [ ] **(이월, 변경 없음)** CREON-M1(P0) 장후 API 세션 정리 적용 시간대 — 여전히 사용자 결정 대기.
- [ ] **(참고)** 698-1/698-2(피터2 단독수집 전환, 698차) 오늘 아침 1차 관측: 15분 창 2개 중 외부소진 1회·0회(10-19 중앙값 27회 대비 큰 개선) — 최종 판정은 5거래일 후(10-26 장후 예정)까지 유지, 이 점검은 재해석하지 않음.
- [ ] (참고) **1-3 / F-5 재확인** `[PositionFallback]` 10건(전부 '신동' 채널) — 기존 F-5 대상, 신규 Fix 없음. 메인 엔진('미륵') 채널은 horizon 정상 전달로 미발생(구조적 원인 재확인).
- [ ] **698-1 장중 중간 관측(보강)** 08:30~12:45 15분 창 17개 중 16개 외부소진 0회(1개 창만 1회) — 전일 중앙값 27회 대비 뚜렷한 개선 지속. 최종 판정은 10-26 장후까지 유지.
- [ ] **F-2 (신규, P2, 조사 전용·코드변경 없음)** `[RegimeFingerprint] 백필 0행 제외` 경보 — 최소 09-16부터 10-20까지 24거래일 연속 매일 발생, 어떤 리포트도 원인 확인한 적 없음. `scripts/backfill_features.py` 실행 이력 또는 `raw_features` 생성일 분포 vs 오늘 기…
- [ ] **O-t1 (신규)** `[진입체크]` 통과 9건 중 3건(13:05·13:11·13:53)이 실제 포지션 진입으로 이어지지 않음 — `main.py`의 진입체크→포지션등록 경로를 코드로 추적해 차단 사유 확인 필요. 표본 1거래일(3건)이라 313차 원칙상 확정 결론 금지.
- [ ] **O-t2 (계승)** 698-1/2(피터2 X 단독수집 전환) 1일차 종합 — 사전등록 기준 2개 전부 PASS(외부소진 중앙값 0.0 vs 27.0, p90 76.5초 vs 237.2초, PAGE_ERROR 0 vs 248). 최종 판정은 5거래일째(빠르면 10-26 장후).
- [ ] **(참고, 등록 보류)** 미륵 엔진 가상 6포지션(2승4패, -438,211원 가상) 중 2분 이내 손절 3건 — B(타이밍)/E(짧은호라이즌노이즈) 가설, 표본 n=6·1거래일이라 누적대장(수익률향상_누적대장.md) 등록 보류(6칸 중 기대효과·검증 미달). 미륵이 실주문 채널로 복귀하거나 가상채널도 집계 대상으로 삼기로 결정되면 재검토.
- [ ] **698-2** 계속 — 평가 창 1/5. 최종 판정 빠르면 10-26 장후. (첫날 통합 p90 76.5초는 참고만)
- [ ] (참고) 12:18 수집 탭이 `compose/post`·피터 글 상세로 이탈 4회(각 1초 내 자동 복귀) — 사람이 수집 탭을 클릭한 흔적, 그 창(12:14)만 관측 31줄로 늘었다. 수집 탭은 건드리지 않도록.
- [ ] (참고) 14:06 이후 새로고침당 요청 2→1회(창당 24→12줄) — 원인 미확인(두 번째 요청은 추가 로드로 추정), 지연·누락 영향 없음. 13:09:38 한도 헤더 없는 응답 1건(무해).
- [ ] (참고) 수신기는 10-19 08:40 기동(pid 5780) 그대로 — 코드 최종 변경 10-16(7a5275b)이라 구버전 아님. 오늘 08:40 `SKIP already running` 은 자동기동 중복 시도(무해).
- [ ] **F-2b (A등급 후보, 장후 전용)** `retrain_eod.py` 424차 가드 문구·조건 정정 — 상류 `[BackfillFilter]`가 이미 제거했으면 INFO("상류에서 N행 제외됨")로 낮추고, 진짜 경보는 "창 안에 마커행이 있는데 상류 제외 0"으로 옮긴다. 상류 제외 수를 retrainer에서 노출해야 하므로 `learn…
- [ ] **O-t1 (이월, 그대로)** 진입체크 통과 후 미진입 3건 — 다음 장후 코드 추적.
- [ ] **698-T (P2)** 전체 테스트 스위트 미청결 — ~66%에서 대시보드 테스트 access violation으로 중단(`main_dashboard.py:7434`, 606-4 동일 자리) + 실패 13파일(457·477·483·490·493·497·498·504·554·555·598·621·virtual_book). 기준선(이전 커밋) …
- [ ] **O-p1 (장중 재확인)** 캐너리 z경고 08:59 재측정 11개(08:55 재적합 직후 3개 대비 +8) — 09:10~09:15 재측정값으로 안정권(8개 이하) 복귀 여부 판정.
- [ ] **O-p2 (장중 재확인, 기존 1-3 계승)** 피터2 A056B 오프셋 스프레드 08:52 기준 0.12(n=7, 표본 8 미만이라 판정 보류) — 표본 8개 이상 확보 후 안정 여부 재확인.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation — 오늘로 6거래일 연속 재현, 여전히 사용자 결정 대기.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
2초, PAGE_ERROR 0 vs 248). 최종 판정은 5거래일째(빠르면 10-26 장후).
- [ ] **(참고, 등록 보류)** 미륵 엔진 가상 6포지션(2승4패, -438,211원 가상) 중 2분 이내 손절 3건 — B(타이밍)/E(짧은호라이즌노이즈) 가설, 표본 n=6·1거래일이라 누적대장(수익률향상_누적대장.md) 등록 보류(6칸 중 기대효과·검증 미달). 미륵이 실주문 채널로 복귀하거나 가상채널도 집계 대상으로 삼기로 결정되면 재검토.


### 2026-10-20 (MW0601 698차 후속 — 단독 수집 첫날 판독, 16:40)
- [x] **698-1 PASS** 외부 소진 중앙 **0.0**/최대 1(24창, 10-19 27.0/35) · 정규장 429 **0**(23) · PAGE_ERROR **0**(248) · 오류 분 0/380(63) · 트윗 n=26 p50/p90/max **44/76.5/88초**(65/237.2/364) — 일 판정 PASS. MW0602 수집기 중지 실반영 확인.
- [ ] **698-2** 계속 — 평가 창 1/5. 최종 판정 빠르면 10-26 장후. (첫날 통합 p90 76.5초는 참고만)
- [ ] (참고) 12:18 수집 탭이 `compose/post`·피터 글 상세로 이탈 4회(각 1초 내 자동 복귀) — 사람이 수집 탭을 클릭한 흔적, 그 창(12:14)만 관측 31줄로 늘었다. 수집 탭은 건드리지 않도록.
- [ ] (참고) 14:06 이후 새로고침당 요청 2→1회(창당 24→12줄) — 원인 미확인(두 번째 요청은 추가 로드로 추정), 지연·누락 영향 없음. 13:09:38 한도 헤더 없는 응답 1건(무해).
- [ ] (참고) 수신기는 10-19 08:40 기동(pid 5780) 그대로 — 코드 최종 변경 10-16(7a5275b)이라 구버전 아님. 오늘 08:40 `SKIP already running` 은 자동기동 중복 시도(무해).


### 2026-10-20 (MW0601 698차 후속 — 장후 자동조치)
- [x] **F-1** 수집기·점검 체크리스트 기대값 동기화(`MAX_CONTRACTS` 3→1 · joblib 1.1.1→1.1.0 · invariants.md·phases.md) — `tests/test_698_collector_invariant_expect_sync.py`. 다음 장전 수집기 §3 두 행 `일치` 확인.
- [x] **F-2** `[RegimeFingerprint] 백필 0행 제외` 원인 확정 — **헛경보**. 559차 상류 `[BackfillFilter]`가 먼저 제거(10-20: 17812/43976 → 26164, DB 실측 26164 일치). 창 안 백필 18,193행 잔존이라 가설 (a) 기각, 상류 정상이라 (b) 기각. DECISION_LOG 동일 날짜 항목.
- [ ] **F-2b (A등급 후보, 장후 전용)** `retrain_eod.py` 424차 가드 문구·조건 정정 — 상류 `[BackfillFilter]`가 이미 제거했으면 INFO("상류에서 N행 제외됨")로 낮추고, 진짜 경보는 "창 안에 마커행이 있는데 상류 제외 0"으로 옮긴다. 상류 제외 수를 retrainer에서 노출해야 하므로 `learning/feature_epoch_mask.py` 반환값 확인 선행. 2027-01-11경 창이 07-13을 벗어나면 상류 제외도 0이 정상이 된다 — 그 분기도 함께 설계.
- [ ] **O-t1 (이월, 그대로)** 진입체크 통과 후 미진입 3건 — 다음 장후 코드 추적.
- [ ] **698-T (P2)** 전체 테스트 스위트 미청결 — ~66%에서 대시보드 테스트 access violation으로 중단(`main_dashboard.py:7434`, 606-4 동일 자리) + 실패 13파일(457·477·483·490·493·497·498·504·554·555·598·621·virtual_book). 기준선(이전 커밋) 재실행으로 사전 존재 확인 후 개별 정리. 특히 490(`피터2미러(청산)` 청산사유 미분류)·498(대사 로그 인벤토리 누락)은 신규 기능이 가드를 안 따라간 유형.

### 2026-10-21 (MW0601 — 장전 점검)
- [ ] **O-p1 (장중 재확인)** 캐너리 z경고 08:59 재측정 11개(08:55 재적합 직후 3개 대비 +8) — 09:10~09:15 재측정값으로 안정권(8개 이하) 복귀 여부 판정.
- [ ] **O-p2 (장중 재확인, 기존 1-3 계승)** 피터2 A056B 오프셋 스프레드 08:52 기준 0.12(n=7, 표본 8 미만이라 판정 보류) — 표본 8개 이상 확보 후 안정 여부 재확인.
- [x] **(해소)** 옵션 체인 재수집 완료 시각 3거래일 연속(09:01:26→09:01:28→09:01:32) 동일 패턴 확인 — 설계된 정상 범위로 확정, 더 추적 불필요.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation — 오늘로 6거래일 연속 재현, 여전히 사용자 결정 대기.

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

### `data/heartbeat_MW0601_20261021.json` — 244B · 10-21 12:26:20
```json
{
 "pid": 24328,
 "written_at": "2026-10-21T12:26:20",
 "beat_epoch": 1792553177.6044407,
 "beat_age_sec": 2.8,
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

### `data/peter_feed/_raw/2026-10-21.jsonl` — 797B · 10-21 11:44:20
```json
JSONL 2행 ⏎ 첫: {"id": "2112722372331778066", "dt": "2026-10-21T01:47:20.000Z", "text": "우리 애기들. \n\n아 미장 오르긴 올랐는데...\n\n좀 찜찜한데...\n\n사야 돼 말아야 돼....\n\n어..피터가 사란다.\n\n그냥 사!!!!!\n\nㅋㅋ\n\n그래서 종교가 있는거야", "seen_at": "2026-10-21T10:48:21+09:00", "src": "live"} | {"id": "2112736670701518898", "dt": "2026-10-21T02:44:09.000Z", "text": "책 다 쓰고 편집하고 있는데.\n\n스마트폰으로 읽는 용과\n테블릿 또는 pc로 읽는 용\n\n둘중에 하나의 버전으로 만들어야 돼.\n\n뭐로 편집할까? 아니면 두가지 버전으로 다 만들까?\n\n도표랑 그래프 추가했더니 테블릿용 기준 800페이지 넘어버렸음ㅋ", "seen_at": "2026-10-21T11:44:20+09:00", "src": "live"} ⏎ 끝:
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-21 11:52:04**

| 키 | 값 | 수집 대상일(2026-10-21)과 일치 |
|---|---|---|
| `date` | 2026-10-21 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-21 08:55:13 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-20) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-21 08:55:13 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-20) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **12:25** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 12:26 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 221 |
| `session_bars` 당일 행수 | 221 (기대 411) |

- 미도래 **163봉** (12:26~15:08) — 수집 시각 12:26 이후라 결손·영구결손에서 제외
- 결손 **0봉**

- 라이브 로그 대조: `logs/20261021_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 24328: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:46 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 24328 | 08:40:46 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 238개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261021-점검리포트.md` | 13.3KB | 10-21 09:04 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_pre.md` | 63.6KB | 10-21 08:59 |
| `docs/정기점검/매일점검/MW0601-20261020-점검리포트.md` | 70.2KB | 10-20 17:57 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_post.md` | 90.1KB | 10-20 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_intra.md` | 75.7KB | 10-20 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_pre.md` | 61.7KB | 10-20 08:59 |
| `docs/정기점검/매일점검/MW0601-20261019-점검리포트.md` | 68.1KB | 10-19 17:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_post.md` | 94.7KB | 10-19 16:21 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261016.json` | 3.1KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261016.md` | 5.4KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261016.json` | 38.9KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20261016.md` | 32.1KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261016.json` | 127.6KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261016.md` | 193.6KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261008.json` | 3.0KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261008.md` | 5.0KB | 10-08 15:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20261021_WARN.log`: ERROR 이상 1건
2. 메인 스레드 정지 5초 초과 **2건** (최대 9672ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20261021_WARN.log`: **[Brier] 과신** 2건(표본)
4. `logs/20261021_WARN.log`: **ConstOut** 1건(표본)
5. `logs/20261021_SYSTEM.log`: **ConstOut** 8건(표본)
6. `logs/20261021_SIGNAL.log`: **WeightCollapse** 8건(표본)
7. `logs/20261021_SIGNAL.log`: **ConstOut** 8건(표본)
8. `logs/20261021_LEARNING.log`: **축퇴** 8건(표본)
9. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
10. 미커밋 변경 29건 (실질 3건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261021*.log` (Windows) / `grep 강제청산 logs/*20261021*.log`*