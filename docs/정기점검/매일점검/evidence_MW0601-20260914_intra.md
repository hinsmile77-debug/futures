# 미륵이 증거 다이제스트 — 2026-09-14 / INTRA

- 생성 2026-09-14 12:27:15 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/modest-serene-faraday/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260914` · `2026-09-14` · `260914` · `0914`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **20개** 파일 · 20개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260914.log` | 124B | 09-14 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260914.log` | 140B | 09-14 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260914.json` | 243B | 09-14 12:26 |
| `launcher_{DATE}_084001_18182.log` | 1 | `logs/Mireuk_batch/launcher_20260914_084001_18182.log` | 853.7KB | 09-14 12:26 |
| `position_state.json.gen_{DATE}_105101` | 1 | `data/position_state.json.gen_20260914_105101` | 1.4KB | 09-14 10:51 |
| `position_state.json.gen_{DATE}_105245` | 1 | `data/position_state.json.gen_20260914_105245` | 1.5KB | 09-14 10:52 |
| `retrain_intraday_{DATE}_093600.log` | 1 | `logs/retrain_intraday_20260914_093600.log` | 1.7KB | 09-14 09:36 |
| `retrain_intraday_{DATE}_111601.log` | 1 | `logs/retrain_intraday_20260914_111601.log` | 3.2KB | 09-14 11:16 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260914_BACKFILL.log` | 0B | 09-14 11:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260914_DATA.log` | 184.5KB | 09-14 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260914_DEBUG.log` | 131.2KB | 09-14 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260914_HEALTH.log` | 1.8KB | 09-14 11:58 |
| `{DATE}_HOGA.log` | 1 | `logs/20260914_HOGA.log` | 30.6MB | 09-14 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260914_LEARNING.log` | 190.9KB | 09-14 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260914_MICRO.log` | 573.5KB | 09-14 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260914_PROBE.log` | 57.8KB | 09-14 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260914_SIGNAL.log` | 312.6KB | 09-14 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260914_SYSTEM.log` | 442.0KB | 09-14 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260914_TRADE.log` | 3.1KB | 09-14 11:12 |
| `{DATE}_WARN.log` | 1 | `logs/20260914_WARN.log` | 19.0KB | 09-14 12:25 |

## 2. 코드·커밋 상태

- HEAD `fdbbf2a` · 브랜치 `v9-dev` · 미커밋 622건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .gitignore
 M CLAUDE.md
 M INSTALL.bat
 M LAUNCH_API.bat
 M MIREUK_DAILYCHECK_HANDOFF.md
 M ROADMAP.md
 M SETUP_GUIDE.md
 M TASK_CLAUDE_WAKE_INSTALL.bat
 M TASK_CLAUDE_WAKE_VERIFY.bat
 M backtest/param_optimizer.py
 M backtest/slippage_simulator.py
 M backtest/transaction_cost.py
 M backtest/walk_forward.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/champion_tp1_skip_trail.py
 M collection/broker/base.py
 M collection/broker/cybos_broker.py
 M collection/broker/factory.py
 M collection/cybos/api_connector.py
 M collection/cybos/investor_data.py
 M collection/cybos/realtime_data.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/constants.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/settings.py
… 외 582건
```

**당일(2026-09-14) 커밋**
```
fdbbf2a [MW0601] 561차: 호가잔량 유효성 딥다이브 — 판정기가 점표본을 읽고 있었다 (매매 정책 무변경)
19c4076 Merge remote-tracking branch 'origin/v9-dev' into v9-dev
d9bdea6 [MW0601] 559차 후속3: 559차 필터가 장중 재학습을 죽였다 — 로더 최소표본에 intraday 전달
```

**최근 커밋 12건**
```
fdbbf2a [MW0601] 561차: 호가잔량 유효성 딥다이브 — 판정기가 점표본을 읽고 있었다 (매매 정책 무변경)
19c4076 Merge remote-tracking branch 'origin/v9-dev' into v9-dev
d9bdea6 [MW0601] 559차 후속3: 559차 필터가 장중 재학습을 죽였다 — 로더 최소표본에 intraday 전달
f786aef [MW0602] O-77-C 배포 완료: 스크립트형 4파일 pytest 전환 — collect_ignore 가 비었다
af9f52a [MW0602] O-77 배포: 테스트 스위트 복구 — 고아 래퍼가 캡처 파일을 닫던 문제
67a8c02 [MW0602] R2·R3·R4 배포: 채널 번호 즉시차단 + 레지스트리 + 키 인용 (dev 0ba6acf 계열)
1bcf718 [MW0602] R1 배포: 캠페인 채널 번호 PC 대역 분할 (dev 3bc965d 동일 적용)
f179140 [MW0601] 559차 후속2: NEXT_TODO 등록 검사를 브랜치 무관하게
2310df1 [MW0601] 559차 후속: 다음 거래일 「결함 3건 정상 수집」 점검기 + NEXT_TODO 보강
857c71d [MW0601] 559차: 데이터 결함 3건 — 상태 판정 + P0·P1·P1' 구현 (매매 정책 무변경)
9d79eef [MW0601] 558차 후속: 리포트 제8부 커밋 해시 기입
c80f09c [MW0601] 558차 후속: 09-11 점검 산출물 일괄 커밋 + 리포트 제8부(장후 자동조치)
```

⚠ **PC명 태그 누락 커밋 1건** (CLAUDE.md 멀티PC 컨벤션 위반):
```
19c4076 Merge remote-tracking branch 'origin/v9-dev' into v9-dev
```

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

### 차단 게이트 전수 인벤토리 — 34개 중 **9개 꺼짐**

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
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260914_HOGA.log` 30.6MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `20260914_MICRO.log`, `20260914_DATA.log`, `20260914_PROBE.log`, `launcher_20260914_084001_18182.log`, `20260914_DEBUG.log`, `freeze_sentinel_20260914.log`, `force_flat_guard_20260914.log`_

### `logs/20260914_TRADE.log` — 3.1KB · 24행 · 최종 11:12:00

- 형식 평문 · 시각 인식 24행 · INFO=24

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-14 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-14 10:51:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,814,784) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-14 10:51:01 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas✅ coun✅ | conf=37.3%
2026-09-14 10:51:01 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2520 code=A056A 방향=SHORT 체결=2 미체결=0
  …
2026-09-14 10:52:45 [INFO] TRADE: [청산 완료] PnL=-1.63pt (-183,558원) | 포지션 합계 -183,558원 (레그 2)
2026-09-14 11:11:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,210) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-14 11:11:00 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-09-14 11:12:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,631,210) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-14 11:12:00 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
```

</details>

**채널** — `TRADE`×24

**컴포넌트 상위 15** — `Chejan`×6, `Position`×5, `Sizer`×3, `체결진입`×2, `JointGateBlock 차단`×2, `ProfitGuard`×1, `진입체크`×1, `TickStop-S0C`×1, `주문요청`×1, `체결청산-부분`×1, `청산 완료`×1

### `logs/20260914_WARN.log` — 19.0KB · 95행 · 최종 12:25:00

- 형식 평문 · 시각 인식 95행 · WARNING=95

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-14 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-14 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-09-14 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-14 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-14 12:11:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 990ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-09-14 12:22:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1161ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-09-14 12:24:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.125% (임계 ±0.115%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-09-14 12:25:00 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: NORMAL → RESTRICTED (acc=0.0%)
2026-09-14 12:25:00 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: NORMAL → RESTRICTED (acc=0.0%)
```

</details>

**WARNING — 태그 22종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 31 | 08:41:09 | 11:31:10 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 9 | 09:07:00 | 12:24:00 | 5분 누적 수익률 +0.375% (임계 ±0.351%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 6 | 09:00:01 | 11:57:01 | level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0 |
| `ChejanFlow` | 6 | 10:51:01 | 10:52:45 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='2520' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=10:51:01.349' | positi… |
| `ChejanMatch` | 6 | 10:51:01 | 10:52:45 | order_no='2520' | pending='ENTRY:SHORT qty=2 filled=0 order_no=2520 reason=진입 req_at=10:51:01.349' | pending_matched=True |
| `SHAP` | 5 | 11:32:01 | 12:22:02 | 슬로우 감지 954ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `PipePerf` | 4 | 09:00:01 | 10:51:01 | total=1164ms | S0=3ms S1=15ms S2=0ms S3=0ms S4=95ms S5=650ms S6=381ms S7=15ms S8=5ms |
| `CB⑤` | 4 | 09:00:01 | 10:51:01 | 파이프라인 1164ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `PendingOrder` | 4 | 10:51:01 | 10:52:46 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1048.0, 'reason': '진입', 'hint_source': '', 'atr': 1.22, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty'… |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:10 | 08:41:10 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-11 → 2026-09-14)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `ConstOut` | 2 | 09:35:00 | 11:15:00 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

**채널** — `SYSTEM`×89, `HEALTH`×6

**컴포넌트 상위 15** — `LiveDBG`×31, `ScalerRefresh`×9, `Health`×6, `ChejanFlow`×6, `ChejanMatch`×6, `SHAP`×5, `PipePerf`×4, `CB⑤`×4, `PendingOrder`×4, `출처축`×2, `SessionStateDrop`×2, `ConstOut`×2, `EntryFillFlow`×2, `ExitFillFlow`×2, `ExitCooldown`×2

### `logs/20260914_SYSTEM.log` — 442.0KB · 3227행 · 최종 12:27:12

- 형식 평문 · 시각 인식 3220행 · INFO=3220, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:40:34 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.7MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-09-14 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=1000 | 행감지=30s all_threads=True
2026-09-14 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-14 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-14 08:40:50 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-14 12:28:09 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-178,foreign:-3745,institution:+3989}
2026-09-14 12:28:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+41243 nonarb=-1909318
2026-09-14 12:28:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+41243 nonarb=-1909318
2026-09-14 12:28:12 [INFO] SYSTEM: [TickUI] alive ticks=71257 code=A056A close=1059.90
2026-09-14 12:28:18 [INFO] SYSTEM: [CybosRT-TICK] #71300 code=A056A raw_time=122818 parsed=12:28:18 price=1059.64 vol=1 bid1=1059.64 ask1=1059.68 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3220

**컴포넌트 상위 15** — `CybosInvestorRaw`×830, `CybosRT-TICK`×718, `CybosRT-ROLLOVER`×223, `BAR-CLOSE`×223, `CVD-ANCHOR`×223, `TickUI`×222, `S6Detail`×209, `PipePerf`×209, `System`×59, `MicroRegime`×48, `RegimeFingerprint`×38, `OptionChain`×24, `CybosSub`×21, `BalanceUI`×14, `CybosDailyPnl`×12

### `logs/20260914_SIGNAL.log` — 312.6KB · 2761행 · 최종 12:27:00

- 형식 평문 · 시각 인식 2761행 · WARNING=1150, INFO=1611

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-14 12:28:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=None)
2026-09-14 12:28:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
2026-09-14 12:28:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 5회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-09-14 12:28:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=85.0% grade=X micro=횡보장
2026-09-14 12:28:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 828 | 09:00:01 | 12:24:00 | 1m 'macro_vix' scale=0.0329 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 96 | 09:00:00 | 11:33:01 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 85 | 09:06:00 | 12:18:01 | 신뢰도 미달 34.4% < 37.9% → 강제 X등급 |
| `ScalerMonitor` | 66 | 09:00:00 | 11:33:01 | ts=08:59 horizon=1m age=1m max_z=-12.76(institution_futures_net) extreme=2 adj=2 |
| `WeightCollapse` | 43 | 09:07:00 | 12:28:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 24 | 08:45:09 | 08:48:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0217) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConfFloorGuard` | 3 | 09:00:00 | 11:20:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `ConstOut` | 3 | 09:35:00 | 11:15:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 2 | 10:32:01 | 10:37:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |

**채널** — `SIGNAL`×2761

**컴포넌트 상위 15** — `ScalerFloor`×840, `SIGNAL`×418, `FQAdj`×206, `Ensemble`×205, `ZeroDiag`×200, `MetaGate`×199, `Model`×108, `Checklist`×93, `ATR-Horizon`×80, `ScalerMonitor`×66, `ScalerRefresh`×56, `MicroRegime`×48, `WeightCollapse`×43, `차단`×43, `InstabilityGate`×37

### `logs/20260914_LEARNING.log` — 190.9KB · 1763행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1763행 · WARNING=166, INFO=1597

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:40:51 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.454 out_max=0.2000 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00155 auc=0.431 out_max=0.4132 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3206 < conf_floor=0.3300 (span=0.00102 auc=0.686 out_max=0.3206, 기저율=0.3200 n=100) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.517 out_max=0.2563 (기준 auc<0.53 and span<0.020, 기저율=0.2562 n=160) → 보정 미적용, raw 통과
  …
2026-09-14 12:28:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=33.3% 예측=UP 실제=FL)
2026-09-14 12:28:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=45.2% 예측=UP 실제=DN)
2026-09-14 12:28:00 [INFO] LEARNING: [Bias⚠] 3m 적중=40%(12/30) UP=2 DN=4 FL=24 [FL편향⚠ 80%]
2026-09-14 12:28:00 [INFO] LEARNING: [Bias⚠] 5m 적중=50%(13/26) UP=1 DN=6 FL=19 [FL편향⚠ 73%]
2026-09-14 12:28:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=10.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 166 | 08:40:52 | 12:20:00 | 축퇴 감지 — span=0.00013 auc=0.454 out_max=0.2000 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1763

**컴포넌트 상위 15** — `LEARNING`×663, `Calibration`×324, `SGD`×209, `sigma`×196, `Bias⚠`×155, `Bias`×68, `MetaConf`×41, `OnlineLearner`×39, `ScalerWarmup`×32, `BiasReset`×14, `SHAP`×7, `GBM-64`×4, `GBM`×3, `RF`×2, `ExtremityCorrector`×2

### `logs/20260914_HEALTH.log` — 1.8KB · 13행 · 최종 11:58:00

- 형식 평문 · 시각 인식 13행 · WARNING=6, INFO=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0
2026-09-14 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=481ms | quality=0.86 | cache_age=102s | exceptions_10m=0
2026-09-14 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 345ms (표본 20분)
2026-09-14 09:33:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=415ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-09-14 09:34:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=454ms | quality=1.00 | cache_age=59s | exceptions_10m=0
  …
2026-09-14 10:52:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=491ms | quality=1.00 | cache_age=142s | exceptions_10m=0
2026-09-14 11:08:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=448ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-09-14 11:09:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=437ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-09-14 11:57:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=343ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-14 11:58:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=374ms | quality=1.00 | cache_age=57s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 6 | 09:00:01 | 11:57:01 | level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0 |

**채널** — `HEALTH`×13

**컴포넌트 상위 15** — `Health`×12, `HealthTrend`×1

### `logs/retrain_intraday_20260914_111601.log` — 3.2KB · 24행 · 최종 11:16:16

- 형식 평문 · 시각 인식 24행 · WARNING=2, INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 11:16:01,794 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-14 11:16:01,794 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-14 11:16:01,794 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-14 11:16:01,795 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-14 11:16:01,795 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a9b5000a.json
  …
2026-09-14 11:16:16,880 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-14 11:16:16,880 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-14 11:16:16,881 [INFO] LEARNING: [Retrain] 완료 | 12.0초 | 성공=1/1 호라이즌
2026-09-14 11:16:16,881 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 15.1s 데이터=4800행
2026-09-14 11:16:16,883 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a9b5000a.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 11:16:08 | 11:16:08 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 27962/45612 제외 (418차 결정 1) — 남은 17650행 |
| `UnitMismatch` | 1 | 11:16:08 | 11:16:08 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/17650행 제외 (559차 P1'-2) — 남은 16204행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260914_093600.log` — 1.7KB · 14행 · 최종 09:36:15

- 형식 평문 · 시각 인식 14행 · WARNING=5, INFO=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 09:36:00,684 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-14 09:36:00,684 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-14 09:36:00,685 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-14 09:36:00,685 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-14 09:36:00,686 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_695ebe96.json
  …
2026-09-14 09:36:15,586 [INFO] LEARNING: [Retrain] 미래 가격 불완전 행 1882개 제거 (max_horizon=30m 후 종가 없음)
2026-09-14 09:36:15,586 [WARNING] LEARNING: [Retrain] 학습 데이터 부족 (미래가격 제거 후 14222 < 15000)
2026-09-14 09:36:15,669 [WARNING] LEARNING: [Retrain] 학습 데이터 부족 (0 < 4800)
2026-09-14 09:36:15,669 [WARNING] RETRAIN_INTRADAY: 재학습 실패: 학습 데이터 부족 (0 < 4800)
2026-09-14 09:36:15,670 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_695ebe96.json
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Retrain` | 2 | 09:36:15 | 09:36:15 | 학습 데이터 부족 (미래가격 제거 후 14222 < 15000) |
| `BackfillFilter` | 1 | 09:36:13 | 09:36:13 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 28062/45612 제외 (418차 결정 1) — 남은 17550행 |
| `UnitMismatch` | 1 | 09:36:13 | 09:36:13 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/17550행 제외 (559차 P1'-2) — 남은 16104행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RETRAIN_INTRADAY` | 1 | 09:36:15 | 09:36:15 | 재학습 실패: 학습 데이터 부족 (0 < 4800) |

**채널** — `RETRAIN_INTRADAY`×7, `LEARNING`×5

**컴포넌트 상위 15** — `RETRAIN_INTRADAY`×6, `Retrain`×5, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2  ※ 두 형식 중복 2건 접음 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 43 |
| 사이저 호출(`[Sizer]`) | 3 |

### 포지션 1건 · 승 0 (0%) · 합계 -3.26pt (-183,558원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:51:01 (추정귀속) | 추정 | SHORT | 2 | — | 2 | -3.26 | -183,558 | 하드스톱(틱) |

**출처별 소계** — 추정 1건 -183,558원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 1건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 2행** (부분청산 1 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:52:45 | 부분 | 1 | -1.63 | -91,779 | 하드스톱(틱) |
| 10:52:45 | 전량 | 1 | -1.63 | -91,779 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×2

> 최종 청산이 하드스톱·손절 계열인 포지션 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -183,558 = 포지션합 -183,558 → OK · `[청산 완료]` 1건 = 조립 포지션 1건 → OK

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×3

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×3

### 차단 사유 43건 · 15종

| 건수 | 사유 |
|---|---|
| 27 | 등급X — 미통과 항목: 2_confidence |
| 3 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=8.6pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.4pt > ATR×5.0=8.3pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.6pt > ATR×5.0=8.1pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.6pt > ATR×5.0=8.3pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.4pt > ATR×5.0=7.6pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.3pt > ATR×5.0=7.4pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.9pt > ATR×5.0=6.8pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.8pt > ATR×5.0=6.6pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.0pt > ATR×5.0=6.5pt (시가=1054.04 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.7pt > ATR×5.0=6.4pt (시가=1054.04 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |

**체크리스트 미통과 항목 누적** — `2_confidence`×27, `3_vwap`×5, `6_foreign`×5, `5_ofi`×4, `4_cvd`×2, `7_prev_bar`×2, `11_countertrend`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 6건 · 최대 4735ms · 5초 초과 0건

상위 — 4735ms, 4625ms, 3563ms, 3157ms, 2579ms, 2297ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260914_WARN.log`
```
--- ConstOut ×2(표본)
09:35:00 2026-09-14 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:15:00 2026-09-14 11:15:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×1(표본)
10:52:45 2026-09-14 10:52:45 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×2(표본)
10:52:45 2026-09-14 10:52:45 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:55:45)
10:52:45 2026-09-14 10:52:45 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:55:45)
--- [SHAP] 슬로우 ×5(표본)
11:32:01 2026-09-14 11:32:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 954ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:40:01 2026-09-14 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 900ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:48:02 2026-09-14 11:48:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1028ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:11:01 2026-09-14 12:11:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 990ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×6(표본)
08:41:12 2026-09-14 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
09:00:03 2026-09-14 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4735ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4735 band=INFO since_pipe_s=0.1
09:01:01 2026-09-14 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=0.0
09:05:02 2026-09-14 09:05:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3563ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3563 band=INFO since_pipe_s=0.0
```

### `logs/20260914_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-14 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-09-14 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-09-14 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=118ms fit=48ms total=199ms
09:36:00 2026-09-14 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-09-14 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-09-14 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:11:00 2026-09-14 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:17:00 2026-09-14 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20260914_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:00:00 2026-09-14 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:49:00 2026-09-14 10:49:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3808 ≥ 필요 0.3710 (span=0.0120, auc=0.570)
10:55:00 2026-09-14 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3703 < 필요 0.3710 (conf_floor=0.330, min_conf=0.371, span=0.0111, auc=0.571). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:07:00 2026-09-14 11:07:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3811 ≥ 필요 0.3710 (span=0.0128, auc=0.583)
--- ConstOut ×8(표본)
09:35:00 2026-09-14 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-14 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-14 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:01 2026-09-14 09:37:01 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-14 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-14 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-14 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-14 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
--- 안전망 ×8(표본)
09:07:00 2026-09-14 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-14 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-14 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-14 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260914_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.454 out_max=0.2000 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00155 auc=0.431 out_max=0.4132 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3206 < conf_floor=0.3300 (span=0.00102 auc=0.686 out_max=0.3206, 기저율=0.3200 n=100) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:52 2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.517 out_max=0.2563 (기준 auc<0.53 and span<0.020, 기저율=0.2562 n=160) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260914_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 11:12

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260914_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 13 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 7 | 09:00:01 [WARNING] total=1164ms | S0=3ms S1=15ms S2=0ms S3=0ms S4=95ms S5=650ms S6=381ms S7=15ms S8=5ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 09:00:01 [WARNING] total=1164ms | S0=3ms S1=15ms S2=0ms S3=0ms S4=95ms S5=650ms S6=381ms S7=15ms S8=5ms |
| 10:00 | 장중 초반 | 1 | 09:57:00 [WARNING] 5분 누적 수익률 -0.251% (임계 ±0.249%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1 | 11:57:01 [WARNING] level=WARNING degraded=OFF | latency=343ms | quality=1.00 | cache_age=182s | exceptions_10m=1 | exc_tags=[SHA… |

- 이 로그 생존구간: 08:41 ~ 12:25

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260914_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:34 [INFO] 로테이션 — 8.7MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:02 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 185 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 190 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 167 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:28

**매분 루프 커버리지 09:00~15:10: 209/371분 (56.3%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:29 | 15:10 | 162 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260914_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0217) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 111 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 190 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 119 | 09:54:00 [WARNING] 신뢰도 미달 34.0% < 37.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 86 | 11:54:01 [WARNING] 신뢰도 미달 35.9% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:28

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260911 | 15:40 | 로그 본문 |
| 20260910 | 15:40 | 로그 본문 |
| 20260909 | 15:40 | 로그 본문 |
| 20260908 | 15:40 | 로그 본문 |
| 20260907 | 21:59 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260914** | **12:28** | 로그 본문 |

- 델타 **-192분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.9MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-14 (MW0601 560차 — 장전 점검)
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
`·`tests/test_498_recon_log_inventory.py`(수정),
`tests/test_558_broker_sync_recon.py`(신규),
`docs/정기점검/매일점검/MW0601-20260911-점검리포트.md` 제8부 append.

## 2026-09-14 (MW0601 560차 — 장전 점검)

### 증상

`data/session_state.json`의 완료 마커 2종(`p8_last_success_date`·`eod_retrain_ok_date`)이
날짜 전환(2026-09-11 → 2026-09-14, 주말 낀 다음 거래일) 시 또 소실됨.
`logs/20260914_WARN.log` 08:41:10 `[SessionStateDrop]` 2건.

### 원인

기존과 동일 — `strategy/runtime/session_recovery_service.py:increment_session()`이
날짜 전환 시 새 딕셔너리를 생성하며 이전 완료 마커를 이어받지 않음. 538차에 이미
"F-1 가설 확정"으로 판정됐고 근본 수정(538-4)은 사용자 승인 대기 상태.

### 결정

- 신규 조사·신규 Fix 제안 없음(함정① 준수 — 538-4로 이미 등록된 사안).
- 09-09·09-10·09-11 장전이 이미 각각 재발을 기록했고, 09-11 장전이 "다음 거래일에도
  재현되면 4거래일 연속 확정, F-1 승인 필요성을 사용자에게 다시 물을 것"을 조건부로
  등록해 뒀다(NEXT_TODO 2026-09-11 557차 항목). 09-12·09-13은 휴장이라 오늘(09-14,
  이번 주 첫 거래일)이 그 "다음 거래일"에 해당 — 조건 충족을 확인하고 리포트
  「사용자 조치」 1번으로 승인 여부를 재상정했다.
- 실손해 없음을 재확인: `data/eod_retrain_done_20260911.txt` 직접 대조 —
  `completed: 2026-09-11 15:54:05`, `rows: 40818`, `horizons_replaced: 6/6`,
  `daily_close_seen: true`. 마커만 소실될 뿐 EOD 재학습 자체는 매일 정상 완료.

### Why

- 계측 4원칙 ②(미측정 ≠ 0) — "표시가 없다"가 "실패했다"로 오독될 위험이 있어
  매번 원본 파일(`eod_retrain_done_{d}.txt`)로 재확인하는 절차를 반복 중.
- 313차 원칙과 무관(표본 문제 아님) — 이건 재발 카운트에 기반한 사전등록된
  에스컬레이션 조건(4거래일 연속)일 뿐이라 판정을 미루지 않는다.

### How to apply

- 사용자가 승인하면 다음 장후 세션이 `session_recovery_service.py:increment_session()`을
  수정해 마커 2종을 이월시킨다. 승인 전까지는 손대지 않는다.

### 검증

- `data/eod_retrain_done_20260911.txt` 직접 열람으로 09-11 EOD 재학습 성공 재확인.
- `git --no-optional-locks status --short`의 566건 M 중 CLAUDE.md 1건을 `git diff`로
  대조 — 1,224줄 삭제/1,224줄 추가로 정확히 일치, EOL(줄바꿈 문자) 차이로 추정.
  수집기의 "실질 변경 미측정(git diff 실패)"과 같은 계열 재발(544-5·544-6·549-3·549-4).
  이번 세션은 신규 조사 없이 재발 사실만 기록(함정① 준수, 549-4로 이관된 사안).
- 설정 불변식 25개 항목 전부 `일치`. 브랜치 `v9-dev` 일치. `.git/index.lock` 없음.
  Python 3.7.13 32bit / scipy 1.5.4 / sklearn 1.0.2 / joblib 1.1.0(문서 표기 1.1.1과의
  차이는 491차 기존 등록 사안, 재보고 안 함) 확인. 레짐 RISK_ON(VIX 15.8) 08:58:13 확정.
  실시간 구독 08:45:09 사전 시작 확인(09:00 이전).
- 2026-09-13(559차) 배포분 `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED=True`(기본 활성)는
  오늘 낮 로그에 소비 지점이 없는 것이 정상(EOD 전용 경로) — O-p1으로 오늘 장후 검증
  이관.

### 병행 세션

당일(2026-09-14) 커밋 0건 상태에서 시작, 세션 시작 시점 `.git/index.lock` 없음(수집기
자가점검도 "이 수집 실행은 락을 만들지 않았다" 확인). 읽기 전용 git은 전량
`--no-optional-locks`. 코드 변경 없음, 라이브 DB 스캔 없음(로그·설정·git만 사용).

산출물: `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md`(신규),
`docs/정기점검/매일점검/evidence_MW0601-20260914_pre.md`(수집기 자동 생성).
커밋 대기: 위 2개 파일(경로 명시 add 필요 — `git add .` 금지, 566건 EOL 파생 혼입 주의).

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 이월·승인 대기 (자동조치 범위 밖)
### 다음 세션 관측
## 2026-09-11 (MW0601 557차 — 장전 점검)
## 2026-09-11 (MW0601 557차 후속 — 장중 점검)
## 2026-09-11 (MW0601 558차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖 — 변경 없음)
### 다음 세션 관측
## 2026-09-14 (MW0601 560차 — 장전 점검)
```

미완료 체크박스 **2625건** (끝에서 30건)
```
- [ ] **F-1 (승인 대기, 리포트 제3부 §2)** ProfitGuard Tier4 래치를 「정정 가능한
- [ ] **F-3 (P0, 승인 대기)** 장중 브로커 잔고 주기 재대사 — 09-10 이월 그대로.
- [ ] **G-2 (주간회의)** 외부 진입 감지를 「엔진 기동 전 포지션」까지 확장 — 536-2와 통합.
- [ ] **O-t2′** 내일 장중 재기동이 있으면 `[Armistice] … 고착[sync]` / `[time]` 중
- [ ] **O-t6** ProfitGuard 래치가 실제로 걸리는 날 `[ProfitGuard][LatchSnapshot]` 이
- [ ] **O-t7** 포지션이 열리고 닫히는 날 `data/position_state.json.gen_*` 이 최대
- [ ] **O-p1 (다음 거래일 장전 판정, 구 O-t1 계승)** `[SessionStateDrop]` 완료 마커
- [ ] **O-p2 (오늘 장중·장후 판정, 구 O-t3 계승)** `[ConfFloorGuard]` 자동진입 하한
- [ ] 신규 Fix/고도화 없음 — F-1·F-3·544-6(git diff 실패 재시도, G-1)은 기존 승인
- [ ] **O-p3 (오늘 중 재확인)** `.git/index.lock`(09:02 생성) 스테일 확정·회수 여부 —
- [ ] **O-i1 (장후 판정)** confidence 게이트 압도적 차단(오늘 36건 중 25건 69%)의
- [ ] **O-i2 (26주 WFA 참고용, 즉시 조치 아님)** 메인 스레드 최대 블로킹 드리프트
- [ ] O-p1(`[SessionStateDrop]` 재발, F-1/538-4 승인 필요성) — 변경 없음, 다음
- [ ] 신규 Fix/고도화 없음 — F-1·F-3·544-6·531-3은 기존 승인 대기 상태 유지
- [ ] 🔵 **558-2 (신규 · 선행 결함, 미조치)** `utils/db_utils.py` 에 모듈 레벨
- [ ] **558-3 (556-8 대장 추가)** `test_504_pnl_history_creon_tab` 2건
- [ ] **544-6 (이월 유지)** 수집기 `git diff` 재시도 — 오늘은 **재현되지 않았다**
- [ ] 🔴 **F-1** ProfitGuard Tier4 래치 「정정 가능한 재평가」 전환 — 승인 대기.
- [ ] 🔴 **F-3 (P0)** 장중 브로커 잔고 주기 재대사 — 승인 대기(우선순위 사용자 위임).
- [ ] 🔴 **556-4** `state_persist_enabled=False` 유지 여부 — 주간회의(실전 전환 기준 ②).
- [ ] **G-2** 외부 진입 감지 확장 — 536-2와 통합해 주간회의.
- [ ] **556-5** `DECISION_LOG` 555차·556차 본문 결손 소급 보완 여부.
- [ ] **556-7** `pytest tests/` 전체 수집 단계 사망 — 원인 모듈 특정 필요.
- [ ] **O-t8 (다음 재기동 시)** `broker_sync_recon` 에 행이 실제로 쌓이는지 —
- [ ] **O-t2′·O-t6·O-t7** (556차 후속 F-5·G-4·G-1 라이브 검증) — 변경 없이 유지.
- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 4거래일 연속 재현)** `[SessionStateDrop]` 완료
- [ ] 신규 Fix/고도화 없음 — 549-4(수집기 git diff 재시도)는 기존 승인·처리 대기 상태
- [ ] **O-p1 (오늘 장후 판정)** 2026-09-13(559차) 배포 `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED=True`가
- [ ] **O-p2 (장중~장후 판정)** `[ConfFloorGuard]` 09:00:00 1회 발동이 오늘 오실레이션으로
- [ ] **O-p3 (다음 거래일 09-15 장전 판정)** `[SessionStateDrop]` 5거래일 연속 재현 여부.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
회수한다**(사용자 조치 불필요).
- [ ] 🔵 **558-2 (신규 · 선행 결함, 미조치)** `utils/db_utils.py` 에 모듈 레벨
      `logger` 가 없는데(관례는 `logging.getLogger("SYSTEM")`) **`except` 안에서
      `logger.*` 를 부르는 곳이 3군데** 있다 — GP 패널 2곳(`[GP패널]` 사전등록 조회 /
      challenger.db 조회)·MA-cont 1곳(`[MA-cont]` 이전 정규장 종가 조회).
      전부 예외 처리 경로라 평소엔 드러나지 않지만, **터지면 예외를 삼키려던 코드가
      `NameError` 로 다시 터진다.** 558차 후속이 자기 코드에서 같은 결함을 실제로
      밟았다(테스트가 잡음). 범위 밖이라 손대지 않음 — 3줄 교정이면 끝난다.
- [ ] **558-3 (556-8 대장 추가)** `test_504_pnl_history_creon_tab` 2건
      (`test_two_tabs_diverge_on_real_data` · `test_filter_link_carries_origin`)을
      기존 실패 대장에 추가. 2026-09-11 에 **변경 전량을 HEAD 로 되돌려 동일 실패
      재현**을 확인했다(이번 변경과 무관). 552-9 가 규명한 「사용자 UI 설정」 계열과
      같은 원인인지는 미확인.
- [ ] **544-6 (이월 유지)** 수집기 `git diff` 재시도 — 오늘은 **재현되지 않았다**
      (제3부 1-3 이 `--shortstat` 결과를 정상 인용). 재현 없는 상태에서 건드리지
      않는다. 다음 실패 관측 시 착수.

### 이월·승인 대기 (자동조치 범위 밖 — 변경 없음)

- [ ] 🔴 **F-1** ProfitGuard Tier4 래치 「정정 가능한 재평가」 전환 — 승인 대기.
      리포트가 **"안전장치를 여는 방향 · 사용자 승인 필수"** 로 명시.
- [ ] 🔴 **F-3 (P0)** 장중 브로커 잔고 주기 재대사 — 승인 대기(우선순위 사용자 위임).
      ⚠ 556-6 장부는 **세기만** 한다 — 장중 노출 자체를 줄이지는 못한다.
- [ ] 🔴 **556-4** `state_persist_enabled=False` 유지 여부 — 주간회의(실전 전환 기준 ②).
- [ ] **G-2** 외부 진입 감지 확장 — 536-2와 통합해 주간회의.
- [ ] **556-5** `DECISION_LOG` 555차·556차 본문 결손 소급 보완 여부.
- [ ] **556-7** `pytest tests/` 전체 수집 단계 사망 — 원인 모듈 특정 필요.
      2026-09-11 재확인: `test_500_cvd_ofi_live_defects` 가 수집 중 `SystemExit: 0`.

### 다음 세션 관측

- [ ] **O-t8 (다음 재기동 시)** `broker_sync_recon` 에 행이 실제로 쌓이는지 —
      정상이면 대부분 `MATCH`/`synced`. 모의서버 blank rows 면 `UNVERIFIED` +
      `[BrokerSyncRecon] … 미측정이다` WARNING 1줄. **하루 종일 0행이면 배선 실패다.**
- [ ] **O-t2′·O-t6·O-t7** (556차 후속 F-5·G-4·G-1 라이브 검증) — 변경 없이 유지.

## 2026-09-14 (MW0601 560차 — 장전 점검)

- [ ] 🔴 **F-1 (538-4) 승인 재요청 (P1, 4거래일 연속 재현)** `[SessionStateDrop]` 완료
      마커 소실이 09-09·09-10·09-11·09-14 4거래일 연속 재현됨(09-12·09-13 휴장 제외).
      실손해 없음(09-11 EOD 재학습 정상 완료 `eod_retrain_done_20260911.txt`로 재확인).
      09-11 장전이 등록한 에스컬레이션 조건("다음 거래일에도 재현 시 4거래일 연속 확정,
      승인 필요성 재확인") 충족 — 리포트 「사용자 조치」 1번으로 재상정.
- [ ] 신규 Fix/고도화 없음 — 549-4(수집기 git diff 재시도)는 기존 승인·처리 대기 상태
      유지(재상정 안 함, 함정① 준수).
- [ ] **O-p1 (오늘 장후 판정)** 2026-09-13(559차) 배포 `INVESTOR_UNIT_MISMATCH_EXCLUDE_ENABLED=True`가
      오늘 밤 EOD 재학습에서 3분·15분 수급 피처 표준편차를 정상치(약 0.884)로 되돌리는지 확인.
- [ ] **O-p2 (장중~장후 판정)** `[ConfFloorGuard]` 09:00:00 1회 발동이 오늘 오실레이션으로
      번지는지, 아니면 09-11처럼 1회성으로 끝나는지.
- [ ] **O-p3 (다음 거래일 09-15 장전 판정)** `[SessionStateDrop]` 5거래일 연속 재현 여부.

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

### `data/heartbeat_MW0601_20260914.json` — 243B · 09-14 12:26:46
```json
{
 "pid": 1000,
 "written_at": "2026-09-14T12:28:16",
 "beat_epoch": 1789356494.4554875,
 "beat_age_sec": 2.4,
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

- 파일 최종 기록: **09-14 11:17:00**

| 키 | 값 | 수집 대상일(2026-09-14)과 일치 |
|---|---|---|
| `date` | 2026-09-14 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 133개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260914-점검리포트.md` | 13.8KB | 09-14 09:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20260914_pre.md` | 51.2KB | 09-14 09:01 |
| `docs/정기점검/매일점검/MW0601-20260911-점검리포트.md` | 70.1KB | 09-11 17:37 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_post.md` | 73.1KB | 09-11 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_intra.md` | 61.2KB | 09-11 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_pre.md` | 53.7KB | 09-11 09:02 |
| `docs/정기점검/매일점검/MW0601-20260910-점검리포트.md` | 103.5KB | 09-10 18:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_post.md` | 84.6KB | 09-10 16:20 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json` | 3.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md` | 5.0KB | 09-13 14:43 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json` | 2.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md` | 4.9KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json` | 38.8KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md` | 32.1KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json` | 115.4KB | 09-11 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260911.md` | 189.4KB | 09-11 15:56 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260914_SYSTEM.log`: 매분 루프 커버리지 209/371분 (56.3%) — 루프가 빠진 구간이 있다
2. `logs/20260914_SYSTEM.log`: 12:29~15:10 **연속 162분 매분 루프 기록 없음**
3. `logs/20260914_WARN.log`: **ConstOut** 2건(표본)
4. `logs/20260914_SYSTEM.log`: **ConstOut** 8건(표본)
5. `logs/20260914_SIGNAL.log`: **WeightCollapse** 8건(표본)
6. `logs/20260914_SIGNAL.log`: **ConstOut** 8건(표본)
7. `logs/20260914_LEARNING.log`: **축퇴** 8건(표본)
8. PC명 태그 누락 커밋 1건 — 멀티PC 컨벤션 위반
9. 미커밋 변경 622건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260914*.log` (Windows) / `grep 강제청산 logs/*20260914*.log`*