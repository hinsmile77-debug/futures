# 미륵이 증거 다이제스트 — 2026-09-04 / INTRA

- 생성 2026-09-04 12:27:28 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/compassionate-modest-ptolemy/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260904` · `2026-09-04` · `260904` · `0904`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260904.log` | 125B | 09-04 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260904.log` | 140B | 09-04 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260904.json` | 243B | 09-04 12:27 |
| `launcher_{DATE}_084000_14769.log` | 1 | `logs/Mireuk_batch/launcher_20260904_084000_14769.log` | 1.5MB | 09-04 12:26 |
| `retrain_intraday_{DATE}_093900.log` | 1 | `logs/retrain_intraday_20260904_093900.log` | 2.7KB | 09-04 09:39 |
| `retrain_intraday_{DATE}_113500.log` | 1 | `logs/retrain_intraday_20260904_113500.log` | 2.7KB | 09-04 11:35 |
| `retrain_intraday_{DATE}_121300.log` | 1 | `logs/retrain_intraday_20260904_121300.log` | 2.7KB | 09-04 12:13 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260904_BACKFILL.log` | 0B | 09-04 07:57 |
| `{DATE}_DATA.log` | 1 | `logs/20260904_DATA.log` | 182.3KB | 09-04 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260904_DEBUG.log` | 134.0KB | 09-04 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260904_HEALTH.log` | 14.0KB | 09-04 12:27 |
| `{DATE}_HOGA.log` | 1 | `logs/20260904_HOGA.log` | 25.0MB | 09-04 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260904_LEARNING.log` | 187.1KB | 09-04 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260904_MICRO.log` | 514.4KB | 09-04 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260904_PROBE.log` | 58.2KB | 09-04 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260904_SIGNAL.log` | 311.5KB | 09-04 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260904_SYSTEM.log` | 781.0KB | 09-04 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260904_TRADE.log` | 60.8KB | 09-04 12:26 |
| `{DATE}_WARN.log` | 1 | `logs/20260904_WARN.log` | 289.9KB | 09-04 12:27 |

## 2. 코드·커밋 상태

- HEAD `9738080` · 브랜치 `v9-dev` · 미커밋 520건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 516건 (추적변경 518 · 미추적 2 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
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
 M challenger/challenger_db.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/base_challenger.py
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
… 외 480건
```

**당일(2026-09-04) 커밋**
```
9738080 [MW0601] 527~529차: 탈진 레짐은 라벨 0건이었다 — 레그 위치를 새 축으로 계측(스윙 피처 + 채널 3종)
c9f76f8 [MW0601] 524~526차: 급변장 라벨의 82%가 z경고였다 — 라벨·게이트 분리(동작 불변) · P5-13 채널 · z경고 잡음 보정(모니터 전용)
```

**최근 커밋 12건**
```
9738080 [MW0601] 527~529차: 탈진 레짐은 라벨 0건이었다 — 레그 위치를 새 축으로 계측(스윙 피처 + 채널 3종)
c9f76f8 [MW0601] 524~526차: 급변장 라벨의 82%가 z경고였다 — 라벨·게이트 분리(동작 불변) · P5-13 채널 · z경고 잡음 보정(모니터 전용)
c26c513 [MW0601] 523차 후속: 리포트 제4부에 커밋 해시 기재
e1f063a [MW0601] 523차 후속: 장후 자동조치 — G-1(기동마커 게재) · G-2(ConfFloorGuard auc) · G-3(ExitStageRecon 인용)
8997136 [MW0601] 519차 기록: DECISION_LOG · NEXT_TODO · 리포트 제5부
d03b629 [MW0601] 519차: CB② 복원 · 메인스레드 정지 경보 · F-1 마감 잔여 자동청산 (사용자 지시)
7338611 [MW0601] 518차 후속: 장후 자동조치 — F-3(진입출처 라벨) · G-1(재기동 잔량 경보 문구) · G-4(이월손익 가시화)
a3f70ab [MW0601] 514차 후속: 장후 자동조치 — F-A(P1-3) · F-B(고도화①) · F-C(고도화②/P5-신규)
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
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

_본문 미열람(설정): `20260904_HOGA.log` 25.0MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `retrain_intraday_20260904_113500.log`, `20260904_MICRO.log`, `20260904_DATA.log`, `20260904_PROBE.log`, `launcher_20260904_084000_14769.log`, `20260904_DEBUG.log`, `freeze_sentinel_20260904.log`, `force_flat_guard_20260904.log`_

### `logs/20260904_TRADE.log` — 60.8KB · 468행 · 최종 12:26:37

- 형식 평문 · 시각 인식 468행 · WARNING=40, INFO=428

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-04 09:42:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,166) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-04 09:42:00 [INFO] TRADE: [진입체크] LONG→LONG 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore✅ prev✅ time✅ risk✅ chas✅ coun✅ | conf=40.0%
2026-09-04 09:42:00 [INFO] TRADE: [Position] 진입 LONG 2계약 @ 1049.44 | 손절=1047.71 1차=1049.79(×0.26) 2차=1051.17 horizon=1m hurst=mean-revert
2026-09-04 09:42:00 [INFO] TRADE: [주문요청] LONG->LONG 2계약 @ 1049.44 등급=A 역방향진입=OFF 체결대기
  …
2026-09-04 12:26:36 [INFO] TRADE: [Position] 체결부분청산 1계약 @ 1048.72 | 잔여=1계약 | PnL=-0.13pt (-16,954원) | 미추적체결(pending_miss)
2026-09-04 12:26:36 [INFO] TRADE: [체결청산-부분] SHORT 1계약 @ 1048.72 | PnL=-0.13pt (-16,954원) | 잔여=1계약 | 사유=미추적체결(pending_miss)
2026-09-04 12:26:37 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2912 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-04 12:26:37 [INFO] TRADE: [Position] 체결청산 SHORT @ 1048.72 | PnL=-0.13pt (-16,954원) | 미추적체결(pending_miss)
2026-09-04 12:26:37 [INFO] TRADE: [청산 완료] PnL=-0.13pt (-16,954원) | 포지션 합계 -52,861원 (레그 3)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 40 | 10:43:53 | 12:25:11 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1046.66 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×468

**컴포넌트 상위 15** — `Chejan`×160, `Position`×102, `체결동기화`×47, `PositionFallback`×40, `주문요청`×35, `청산 완료`×21, `TickStop-S0C`×15, `체결청산-부분`×15, `TickTP1`×13, `TP1 부분청산`×11, `TP2 부분청산`×4, `ProfitGuard`×1, `Sizer`×1, `진입체크`×1, `체결진입`×1

### `logs/20260904_WARN.log` — 289.9KB · 1334행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1334행 · CRITICAL=58, ERROR=47, WARNING=1229

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-09-04 08:40:50 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
2026-09-04 08:40:50 [WARNING] SYSTEM: [LiveDBG] _apply update_learning 15ms
  …
2026-09-04 12:26:38 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-04 12:26:38 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-09-04 12:26:38 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 78ms account=333044256
2026-09-04 12:27:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=286ms | quality=1.00 | cache_age=0s | exceptions_10m=44
2026-09-04 12:28:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=300ms | quality=1.00 | cache_age=60s | exceptions_10m=35
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 58 | 10:46:00 | 12:28:00 | level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16 |
| ERROR | `ExternalEntry` | 47 | 10:43:53 | 12:25:11 | 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.66 (보유 1계약, 평균 1046.66). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
```

</details>

<details><summary>ERROR/ExternalEntry 원문 2건</summary>

```
2026-09-04 10:43:53 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.66 (보유 1계약, 평균 1046.66). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
2026-09-04 10:44:03 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.18 (보유 2계약, 평균 1046.42). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫히지 않는다
```

</details>

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 461 | 08:40:48 | 12:26:38 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 160 | 09:42:00 | 12:26:37 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='974' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=09:42:00.619' | position… |
| `ChejanMatch` | 160 | 09:42:00 | 12:26:37 | order_no='974' | pending='ENTRY:LONG qty=2 filled=0 order_no=974 reason=진입 req_at=09:42:00.619' | pending_matched=True |
| `OrderSync` | 102 | 10:43:53 | 12:26:37 | 미추적 체결 감지 (pending_miss) order_no=1965 side=SHORT qty=1 price=1046.66 before=FLAT |
| `PendingOrder` | 70 | 09:42:00 | 12:25:01 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1049.44, 'reason': '진입', 'hint_source': '', 'atr': 1.3543, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `ExitCooldown` | 42 | 09:43:56 | 12:26:37 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:46:56) |
| `Health` | 35 | 09:00:01 | 12:19:01 | level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0 |
| `ExitFillFlow` | 32 | 09:43:56 | 12:25:01 | after='FLAT' | before='LONG 1계약 @ 1049.18' | fill_price=1049.18 | fill_qty=1 | mode='final' | pending='EXIT_FULL:LONG qty=1 filled=1 order_no=1008 reason=하드스톱(틱) req_at=09:43:55.864' | reason='하드스톱(틱)' |
| `PartialExitAttempt` | 21 | 09:42:03 | 12:25:01 | pending='NONE' | position='LONG 2계약 @ 1049.18' | price=1049.56 | stage=1 |
| `PartialExitSendOrderResult` | 19 | 09:42:04 | 12:25:01 | position='LONG 2계약 @ 1049.18' | reason='TP1 부분청산 33%' | ret=0 | send_qty=1 | stage=1 | stage_plan=(1, 1, 0) | target_qty=1 |
| `IntrabarTPSchedule` | 15 | 09:42:04 | 12:25:01 | EXIT_PARTIAL 해소 → 300ms 후 TP 재점검 스케줄 price=1049.56 pos=LONG p1=True p2=False p3=False |
| `TickStop` | 15 | 09:43:55 | 12:21:54 | 스톱 히트 감지 (틱) LONG tick=1049.16 stop=1049.18 → 즉시 처리 예약 |

**채널** — `SYSTEM`×1241, `HEALTH`×93

**컴포넌트 상위 15** — `LiveDBG`×461, `ChejanFlow`×160, `ChejanMatch`×160, `OrderSync`×102, `Health`×93, `PendingOrder`×70, `ExternalEntry`×47, `ExitCooldown`×42, `ExitFillFlow`×32, `PartialExitAttempt`×21, `PartialExitSendOrderResult`×19, `IntrabarTPSchedule`×15, `TickStop`×15, `ExitSendOrderResult`×15, `CB`×14

### `logs/20260904_SYSTEM.log` — 781.0KB · 4375행 · 최종 12:27:25

- 형식 평문 · 시각 인식 4368행 · INFO=4368, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:30 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=11496 | 행감지=30s all_threads=True
2026-09-04 08:40:31 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-04 08:40:31 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-04 08:40:31 [INFO] SYSTEM: 미륵이 초기화
2026-09-04 08:40:31 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-03) 종가 버퍼 로드: 384봉
  …
2026-09-04 12:28:00 [INFO] SYSTEM: [CybosRT-ROLLOVER] code=A0569 from=12:27 to=12:28
2026-09-04 12:28:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=12:27 O=1049.04 H=1049.26 L=1048.40 C=1048.54 V=204
2026-09-04 12:28:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=12:27 vol=204 | live_buy=118 shadow_buy=82 anchor_buy=82 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-04 12:28:00 [INFO] SYSTEM: [S6Detail] ensemble=2ms checklist_pre=9ms meta_gate=6ms gates=0ms imp=0ms shap=1ms corr=5ms dash_ui=0ms tail=12ms
2026-09-04 12:28:00 [INFO] SYSTEM: [PipePerf][DBG] total=300ms | S0=3ms S1=25ms S2=8ms S3=0ms S4=65ms S5=156ms S6=36ms S7=5ms S8=2ms
```

</details>

**채널** — `SYSTEM`×4368

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×596, `CybosEvent`×320, `CybosDailyPnl`×302, `BalanceUI`×271, `CybosRT-ROLLOVER`×223, `BAR-CLOSE`×223, `CVD-ANCHOR`×223, `TickUI`×221, `S6Detail`×209, `PipePerf`×209, `BalanceRefresh`×163, `CybosDailyPnlHeaders`×151, `System`×59, `MicroRegime`×50

### `logs/20260904_SIGNAL.log` — 311.5KB · 2744행 · 최종 12:27:00

- 형식 평문 · 시각 인식 2744행 · WARNING=1183, INFO=1561

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
  …
2026-09-04 12:28:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-09-04 12:28:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=None)
2026-09-04 12:28:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
2026-09-04 12:28:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=85.0% grade=X micro=혼합
2026-09-04 12:28:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 660 | 09:00:00 | 12:25:00 | 1m 'macro_vix' scale=0.0206 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 193 | 09:00:00 | 12:20:00 | ts=08:59 horizon=1m age=1m max_z=+4.90(toxicity_flow_stress) extreme=2 adj=2 |
| `Model` | 146 | 09:00:00 | 12:20:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerRefresh` | 84 | 08:45:18 | 09:15:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0293) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Checklist` | 49 | 09:06:00 | 12:03:01 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `WeightCollapse` | 45 | 09:07:01 | 12:28:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConfFloorGuard` | 3 | 09:00:00 | 11:20:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4230 (conf_floor=0.330, min_conf=0.423, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `ConstOut` | 3 | 09:38:00 | 12:12:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |

**채널** — `SIGNAL`×2744

**컴포넌트 상위 15** — `ScalerFloor`×708, `SIGNAL`×418, `Ensemble`×212, `FQAdj`×206, `ZeroDiag`×205, `ScalerMonitor`×193, `Model`×170, `MetaGate`×117, `ScalerRefresh`×113, `Checklist`×55, `MicroRegime`×50, `ATR-Horizon`×47, `WeightCollapse`×45, `InstabilityGate`×28, `DayRegimeShadow`×26

### `logs/20260904_LEARNING.log` — 187.1KB · 1729행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1729행 · WARNING=163, INFO=1566

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:33 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2630 < conf_floor=0.3300 (span=0.00096 auc=0.546 out_max=0.2630, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00019 auc=0.521 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-04 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00109 auc=0.539 out_max=0.4351 (n=145) → 보정 재적용
  …
2026-09-04 12:28:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=42.7% 예측=FL 실제=DN)
2026-09-04 12:28:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=48.7% 예측=DN 실제=FL)
2026-09-04 12:28:00 [INFO] LEARNING: [Bias⚠] 1m 적중=33%(5/15) UP=1 DN=0 FL=14 [FL편향⚠ 93%]
2026-09-04 12:28:00 [INFO] LEARNING: [OnlineLearner] 1m SGD UP붕괴 자동 복구 (≥80% 12분 지속) → 모델·스케일러 리셋
2026-09-04 12:28:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=8.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 163 | 08:40:33 | 11:37:01 | 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1729

**컴포넌트 상위 15** — `LEARNING`×669, `Calibration`×320, `SGD`×209, `sigma`×196, `Bias⚠`×131, `Bias`×68, `MetaConf`×41, `ScalerWarmup`×29, `OnlineLearner`×28, `BiasReset`×8, `SHAP`×7, `GBM-64`×6, `GBM`×6, `RF`×4, `ExtremityCorrector`×2

### `logs/20260904_HEALTH.log` — 14.0KB · 102행 · 최종 12:27:00

- 형식 평문 · 시각 인식 102행 · CRITICAL=58, WARNING=35, INFO=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0
2026-09-04 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=653ms | quality=0.86 | cache_age=124s | exceptions_10m=0
2026-09-04 09:02:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=428ms | quality=0.74 | cache_age=184s | exceptions_10m=0
2026-09-04 09:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=287ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-09-04 09:05:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=407ms | quality=1.00 | cache_age=180s | exceptions_10m=0
  …
2026-09-04 12:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=310ms | quality=1.00 | cache_age=4s | exceptions_10m=30
2026-09-04 12:25:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=385ms | quality=1.00 | cache_age=64s | exceptions_10m=31
2026-09-04 12:26:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=297ms | quality=1.00 | cache_age=123s | exceptions_10m=37
2026-09-04 12:27:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=286ms | quality=1.00 | cache_age=0s | exceptions_10m=44
2026-09-04 12:28:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=300ms | quality=1.00 | cache_age=60s | exceptions_10m=35
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 58 | 10:46:00 | 12:28:00 | level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 35 | 09:00:01 | 12:19:01 | level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0 |

**채널** — `HEALTH`×102

**컴포넌트 상위 15** — `Health`×101, `HealthTrend`×1

### `logs/retrain_intraday_20260904_093900.log` — 2.7KB · 21행 · 최종 09:39:20

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 09:39:00,561 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-04 09:39:00,562 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-04 09:39:00,562 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-04 09:39:00,562 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_9cce9847.json
2026-09-04 09:39:03,521 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-04 09:39:20,699 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-04 09:39:20,700 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-04 09:39:20,701 [INFO] LEARNING: [Retrain] 완료 | 17.2초 | 성공=1/1 호라이즌
2026-09-04 09:39:20,701 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 20.1s 데이터=4800행
2026-09-04 09:39:20,703 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_9cce9847.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260904_121300.log` — 2.7KB · 21행 · 최종 12:13:23

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 12:13:00,636 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-04 12:13:00,636 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-04 12:13:00,636 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-04 12:13:00,636 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a02d16d3.json
2026-09-04 12:13:04,486 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-04 12:13:23,439 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-04 12:13:23,440 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-04 12:13:23,440 [INFO] LEARNING: [Retrain] 완료 | 19.0초 | 성공=1/1 호라이즌
2026-09-04 12:13:23,440 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.8s 데이터=4800행
2026-09-04 12:13:23,442 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a02d16d3.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 1 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 48 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 47 |
| 청산(`체결청산`) | 21 |
| 차단(`[차단]`) | 26 |
| 사이저 호출(`[Sizer]`) | 1 |

### 포지션 21건 · 승 8 (38%) · 합계 +3.68pt (-352,572원)  ※ 레그 51행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:42:00 | 엔진 | LONG | 2 | 1m | 2 | +0.34 | -3,586 | 하드스톱(틱) |
| 10:43:53 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -2.18 | -129,532 | 하드스톱(틱) |
| 10:45:17 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.57 | -2,787 | 하드스톱(틱) |
| 10:46:31 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.61 | +209 | 하드스톱(틱) |
| 10:49:42 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +1.97 | +68,245 | 하드스톱(틱) |
| 10:55:29 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -3.51 | -206,712 | 하드스톱(틱) |
| 11:08:03 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.38 | -11,807 | 하드스톱(틱) |
| 11:18:09 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +1.45 | +42,107 | 하드스톱(틱) |
| 11:31:56 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +0.44 | -8,870 | 하드스톱(틱) |
| 11:34:01 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +4.11 | +174,138 | TP3(전량) |
| 11:39:07 (추정귀속) | 외부 | LONG | 3 | — | 2 | +1.01 | +19,233 | 하드스톱(틱) |
| 11:43:24 (추정귀속) | 외부 | LONG | 2 | — | 2 | +1.50 | +54,476 | TP2(전량) |
| 11:49:14 (추정귀속) | 외부 | LONG | 1 | — | 1 | +1.28 | +53,721 | TP2(전량) |
| 11:52:12 (추정귀속) | 외부 | SHORT | 1 | — | 1 | -0.94 | -57,297 | 미추적체결(pending_miss) |
| 11:55:27 (추정귀속) | 외부 | LONG | 2 | — | 2 | -2.06 | -123,596 | 하드스톱(틱) |
| 11:57:46 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -2.28 | -134,574 | 하드스톱(틱) |
| 12:04:11 (추정귀속) | 외부 | SHORT | 1 | — | 1 | -0.46 | -33,301 | 하드스톱(틱) |
| 12:17:36 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -1.83 | -122,919 | 하드스톱(틱) |
| 12:19:38 (추정귀속) | 외부 | LONG | 3 | — | 3 | +0.37 | -12,940 | 하드스톱(틱) |
| 12:23:23 (추정귀속) | 외부 | SHORT | 3 | — | 3 | +3.34 | +136,082 | TP3(전량) |
| 12:25:10 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -0.43 | -52,862 | 미추적체결(pending_miss) |

**출처별 소계** — 엔진 1건 -3,586원 · 외부 20건 -348,986원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 20건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 51행** (부분청산 30 · 전량청산 21)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:42:04 | 부분 | 1 | +0.34 | +6,707 | TP1 부분청산 33% |
| 09:43:56 | 전량 | 1 | +0.00 | -10,293 | 하드스톱(틱) |
| 10:44:53 | 부분 | 1 | -1.16 | -68,266 | 하드스톱(틱) |
| 10:44:54 | 전량 | 1 | -1.02 | -61,266 | 하드스톱(틱) |
| 10:45:37 | 부분 | 1 | +0.57 | +18,071 | TP1 부분청산 33% |
| 10:46:12 | 부분 | 1 | +0.01 | -9,929 | 하드스톱(틱) |
| 10:46:12 | 전량 | 1 | -0.01 | -10,929 | 하드스톱(틱) |
| 10:46:51 | 부분 | 1 | +0.59 | +19,403 | TP1 부분청산 33% |
| 10:47:42 | 부분 | 1 | +0.01 | -9,597 | 하드스톱(틱) |
| 10:47:43 | 전량 | 1 | +0.01 | -9,597 | 하드스톱(틱) |
| 10:50:10 | 부분 | 1 | +0.55 | +17,415 | TP1 부분청산 33% |
| 10:52:00 | 부분 | 1 | +1.49 | +64,415 | TP2 부분청산 33% |
| 10:52:50 | 전량 | 1 | -0.07 | -13,585 | 하드스톱(틱) |
| 10:56:10 | 부분 | 1 | -1.19 | -69,904 | 하드스톱(틱) |
| 10:56:10 | 부분 | 1 | -1.19 | -69,904 | 하드스톱(틱) |
| 10:56:10 | 전량 | 1 | -1.13 | -66,904 | 하드스톱(틱) |
| 11:09:10 | 부분 | 1 | +0.66 | +22,731 | TP1 부분청산 33% |
| 11:09:41 | 부분 | 1 | -0.12 | -16,269 | 하드스톱(틱) |
| 11:09:41 | 전량 | 1 | -0.16 | -18,269 | 하드스톱(틱) |
| 11:18:32 | 부분 | 1 | +0.61 | +20,369 | TP1 부분청산 33% |
| 11:20:01 | 부분 | 1 | +0.89 | +34,369 | TP2 부분청산 33% |
| 11:30:03 | 전량 | 1 | -0.05 | -12,631 | 하드스톱(틱) |
| 11:32:11 | 부분 | 1 | +0.56 | +17,710 | TP1 부분청산 33% |
| 11:32:55 | 부분 | 1 | -0.06 | -13,290 | 하드스톱(틱) |
| 11:32:55 | 전량 | 1 | -0.06 | -13,290 | 하드스톱(틱) |
| 11:34:28 | 부분 | 1 | +0.55 | +17,046 | TP1 부분청산 33% |
| 11:35:00 | 부분 | 1 | +1.39 | +59,046 | TP2 부분청산 33% |
| 11:37:01 | 전량 | 1 | +2.17 | +98,046 | TP3(전량) |
| 11:39:41 | 부분 | 1 | +0.63 | +21,078 | TP1 부분청산 33% |
| 11:42:35 | 전량 | 2 | +0.19 | -1,845 | 하드스톱(틱) |
| 11:48:01 | 부분 | 1 | +0.74 | +26,738 | TP2(전량) |
| 11:48:01 | 전량 | 1 | +0.76 | +27,738 | TP2(전량) |
| 11:51:01 | 전량 | 1 | +1.28 | +53,721 | TP2(전량) |
| 11:54:36 | 전량 | 1 | -0.94 | -57,297 | 미추적체결(pending_miss) |
| 11:57:23 | 부분 | 1 | -1.03 | -61,798 | 하드스톱(틱) |
| 11:57:24 | 전량 | 1 | -1.03 | -61,798 | 하드스톱(틱) |
| 11:59:44 | 부분 | 1 | -1.14 | -67,287 | 하드스톱(틱) |
| 11:59:44 | 전량 | 1 | -1.14 | -67,287 | 하드스톱(틱) |
| 12:15:57 | 전량 | 1 | -0.46 | -33,301 | 하드스톱(틱) |
| 12:19:07 | 부분 | 1 | -0.61 | -40,973 | 하드스톱(틱) |
| 12:19:07 | 부분 | 1 | -0.61 | -40,973 | 하드스톱(틱) |
| 12:19:07 | 전량 | 1 | -0.61 | -40,973 | 하드스톱(틱) |
| 12:21:02 | 부분 | 1 | +0.33 | +6,020 | TP1 부분청산 33% |
| 12:21:54 | 부분 | 1 | +0.01 | -9,980 | 하드스톱(틱) |
| 12:21:55 | 전량 | 1 | +0.03 | -8,980 | 하드스톱(틱) |
| 12:24:01 | 부분 | 1 | +0.52 | +15,694 | TP1 부분청산 33% |
| 12:25:01 | 부분 | 1 | +1.38 | +58,694 | TP2 부분청산 33% |
| 12:25:01 | 전량 | 1 | +1.44 | +61,694 | TP3(전량) |
| 12:26:35 | 부분 | 1 | -0.17 | -18,954 | 미추적체결(pending_miss) |
| 12:26:36 | 부분 | 1 | -0.13 | -16,954 | 미추적체결(pending_miss) |
| 12:26:37 | 전량 | 1 | -0.13 | -16,954 | 미추적체결(pending_miss) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×27, `TP1 부분청산 33%`×11, `TP2 부분청산 33%`×4, `미추적체결(pending_miss)`×4, `TP2(전량)`×3, `TP3(전량)`×2

> 최종 청산이 하드스톱·손절 계열인 포지션 15/21건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -352,572 = 포지션합 -352,572 → OK · `[청산 완료]` 21건 = 조립 포지션 21건 → OK

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:42:00 | LONG | 2 | 1049.44 | 1m | mean-revert |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×1

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×1

### 차단 사유 26건 · 14종

| 건수 | 사유 |
|---|---|
| 12 | 등급X — 미통과 항목: 2_confidence |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 6.1pt > ATR×5.0=5.8pt (시가=1043.24 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 6.5pt > ATR×5.0=6.1pt (시가=1043.24 반등위험) |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.97pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 101초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 169초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 110초 후 재진입 가능 |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 청산 후 쿨다운 — 60초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 155초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 43초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×12, `3_vwap`×1, `4_cvd`×1, `5_ofi`×1, `6_foreign`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 16건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×10
- `연속 손절 2회 (300초 창, 포지션 단위)` ×4
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-04 12:25:10, 현재 1…` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 3건 · 최대 3343ms · 5초 초과 0건

상위 — 3343ms, 3000ms, 2281ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260904_WARN.log`
```
--- ConstOut ×3(표본)
09:38:00 2026-09-04 09:38:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:34:01 2026-09-04 11:34:01 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
12:12:01 2026-09-04 12:12:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×8(표본)
09:43:56 2026-09-04 09:43:56 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:44:54 2026-09-04 10:44:54 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:46:12 2026-09-04 10:46:12 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:52:50 2026-09-04 10:52:50 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:43:56 2026-09-04 09:43:56 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:46:56)
09:43:56 2026-09-04 09:43:56 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:46:56)
10:44:54 2026-09-04 10:44:54 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:47:53)
10:44:54 2026-09-04 10:44:54 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:47:53)
--- [SHAP] 슬로우 ×1(표본)
11:51:01 2026-09-04 11:51:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 970ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- degraded=ON ×8(표본)
10:47:01 2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
10:48:02 2026-09-04 10:48:02 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=269ms | quality=1.00 | cache_age=120s | exceptions_10m=24
10:49:00 2026-09-04 10:49:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=341ms | quality=1.00 | cache_age=178s | exceptions_10m=24
10:50:00 2026-09-04 10:50:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=321ms | quality=1.00 | cache_age=55s | exceptions_10m=33
--- level=CRITICAL ×2(표본)
10:46:00 2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
12:20:00 2026-09-04 12:20:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=369ms | quality=1.00 | cache_age=130s | exceptions_10m=20
--- 강제청산 ×8(표본)
10:43:53 2026-09-04 10:43:53 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.66 (보유 1계약, 평균 1046.66). 오늘 누적 1건 / 1계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
10:44:03 2026-09-04 10:44:03 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.18 (보유 2계약, 평균 1046.42). 오늘 누적 2건 / 2계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
10:45:17 2026-09-04 10:45:17 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.08 (보유 1계약, 평균 1046.08). 오늘 누적 3건 / 3계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
10:45:18 2026-09-04 10:45:18 [ERROR] SYSTEM: [ExternalEntry] 🔴 미륵이가 내지 않은 진입이 계좌에 들어왔다 — SHORT 1계약 @ 1046.08 (보유 2계약, 평균 1046.08). 오늘 누적 4건 / 4계약. HTS·MTS 등 다른 경로에서 같은 계좌를 만지고 있는지 지금 확인할 것 — 15:10 이후에 들어오면 강제청산 단계가 이미 지나가 자동으로 닫…
--- 메인 스레드 블로킹 ×3(표본)
09:00:01 2026-09-04 09:00:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2281 band=INFO since_pipe_s=0.1
12:06:03 2026-09-04 12:06:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3343ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3343 band=INFO since_pipe_s=0.1
12:14:03 2026-09-04 12:14:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3000ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3000 band=INFO since_pipe_s=0.0
```

### `logs/20260904_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:38:00 2026-09-04 09:38:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:40:00 (const_output)
09:38:00 2026-09-04 09:38:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:38:00 2026-09-04 09:38:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=86ms fit=75ms total=162ms
09:39:00 2026-09-04 09:39:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-09-04 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:05:00 2026-09-04 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:10:00 2026-09-04 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:15:00 2026-09-04 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
--- [CB] ×2(표본)
12:26:36 2026-09-04 12:26:36 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-04 12:25:10, 현재 1회)
12:26:37 2026-09-04 12:26:37 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-04 12:25:10, 현재 1회)
```

### `logs/20260904_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:00:00 2026-09-04 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4230 (conf_floor=0.330, min_conf=0.423, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:42:00 2026-09-04 10:42:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3789 ≥ 필요 0.3720 (span=0.0185, auc=0.567)
10:55:00 2026-09-04 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3671 < 필요 0.3720 (conf_floor=0.330, min_conf=0.372, span=0.0149, auc=0.560). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:07:00 2026-09-04 11:07:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3764 ≥ 필요 0.3720 (span=0.0134, auc=0.547)
--- ConstOut ×8(표본)
09:38:00 2026-09-04 09:38:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:38:00 2026-09-04 09:38:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:39:00 2026-09-04 09:39:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:40:00 2026-09-04 09:40:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:01 2026-09-04 09:07:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-04 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-04 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.7% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-04 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.3% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
--- 안전망 ×8(표본)
09:07:01 2026-09-04 09:07:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-04 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-04 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-04 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260904_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2630 < conf_floor=0.3300 (span=0.00096 auc=0.546 out_max=0.2630, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00019 auc=0.521 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:33 2026-09-04 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00109 auc=0.539 out_max=0.4351 (n=145) → 보정 재적용
```

### `logs/20260904_HEALTH.log`
```
--- degraded=ON ×8(표본)
10:47:01 2026-09-04 10:47:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=303ms | quality=1.00 | cache_age=59s | exceptions_10m=23
10:48:02 2026-09-04 10:48:02 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=269ms | quality=1.00 | cache_age=120s | exceptions_10m=24
10:49:00 2026-09-04 10:49:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=341ms | quality=1.00 | cache_age=178s | exceptions_10m=24
10:50:00 2026-09-04 10:50:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=321ms | quality=1.00 | cache_age=55s | exceptions_10m=33
--- level=CRITICAL ×2(표본)
10:46:00 2026-09-04 10:46:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=442ms | quality=1.00 | cache_age=183s | exceptions_10m=16
12:20:00 2026-09-04 12:20:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=369ms | quality=1.00 | cache_age=130s | exceptions_10m=20
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260904_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 1 | 08:40:46 [INFO] 설정 업데이트 완료 |
| 12:00 | 장중 중간점 | 45 | 11:55:27 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1049.90 — 진입 경로가 파라미터를 넘기지 … |

- 이 로그 생존구간: 08:40 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260904_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 8 | 08:40:48 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 08:55:19 [WARNING] scaler 노후=0h  z경고피처=18개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:19 [WARNING] scaler 노후=0h  z경고피처=18개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1 | 09:57:00 [WARNING] level=WARNING degraded=OFF | latency=267ms | quality=1.00 | cache_age=180s | exceptions_10m=0 |
| 12:00 | 장중 중간점 | 139 | 11:54:00 [CRITICAL] level=CRITICAL degraded=ON | latency=260ms | quality=1.00 | cache_age=39s | exceptions_10m=14 |

- 이 로그 생존구간: 08:40 ~ 12:28

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260904_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 90 | 08:40:30 [INFO] 활성화 | file=logs\crash_fault.log PID=11496 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 127 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 184 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 182 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 315 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:28

**매분 루프 커버리지 09:00~15:10: 209/371분 (56.3%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:29 | 15:10 | 162 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260904_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:18 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0293) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 123 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0254) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 227 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0272) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 105 | 09:54:00 [WARNING] 신뢰도 미달 36.1% < 38.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 159 | 11:55:00 [WARNING] 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 12:28

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260903 | 15:40 | 로그 본문 |
| 20260902 | 15:40 | 로그 본문 |
| 20260901 | 15:40 | 로그 본문 |
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260904** | **12:28** | 로그 본문 |

- 델타 **-192분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 3. 채널 E `leg_entry_early_watch` (P5-16) — 관측 전용
### 4. 확정 결정 `core_vwap_directional_requirement` — 3_vwap 무변경 (D)
### 5. 판정기·검증
## 2026-09-04 (MW0601 530차 — 장전 점검)
### 1. 이상점 1-1 재발 — `session_state.json` P8/EOD 완료 마커 2일 연속 소실 → P2에서 P1로 격상
### 2. 병행 세션 확인 — 오늘 새벽 딥다이브 3건(527·528·529차) 역링크
### 3. 설정 불변식·게이트 인벤토리 — 전부 일치, 신규 이상 없음
### 4. 개장 준비 확인 — A절 체크리스트 전 항목 정상
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
logs/retrain_eod_20260903.log:129-131` "session_state
  p8_last_success_date + eod_retrain_ok_date 기록 완료"). 그런데 오늘(09-04) 08:46 시점 실측
  `data/session_state.json`에는 `p8_last_success_date`·`eod_retrain_ok_date` 두 키가 다시 없다.
  09-03 이상점 1-1과 완전히 동일한 현상 — 2일 연속.
- **원인**: 미규명. 09-03 리포트가 세운 가설(main.py 여러 초기화 쓰기 경합 / 날짜 전환 로직 / retrain_eod.py
  기록 실패)이 그대로 유효. (c) retrain_eod 기록 실패 가설은 로그상 "기록 완료" 메시지가 09-03에도
  확인돼 기각 유지. 2일 연속 재현은 (a) 경합 가설의 신빙성을 높인다.
- **결정**: 09-03 리포트가 사전에 "내일도 사라지면 구조적 문제로 격상"이라 정한 기준을 오늘 충족 →
  P2 → **P1**로 격상. F-1(원인 조사)을 계속 연다.
- **Why**: 대비 경로(`[PreRetrain] EOD 마커 파일 직접 확인`)가 오늘도 정상 작동해 실거래 지장은
  없었다(`logs/20260904_SYSTEM.log:150-151`). 다만 정상 경로가 매일 조용히 사라지는 원인 미규명 상태가
  길어지면, 이 상태 파일을 참조하는 다른 로직이 향후 조용히 잘못 판단할 위험이 있다.
- **How to apply**: (장후 이후) `main.py`의 `_write_session_state()`/`_read_session_state()` 호출부에
  실제 기록 키 목록 + 파일 mtime을 DEBUG로 남기는 진단 로그 추가(G-1). 09-03 리포트 기준 호출부 행 번호
  (3382/3395/4757/4968/12031/13030)는 이번 세션에서 재확인하지 않았다 — 461차 사례처럼 밀렸을 수 있어
  실제 작업 착수 시 `grep -n "_write_session_state\|_read_session_state" main.py`로 재확인할 것.
- **검증**: 내일(09-05) 아침 08:45~08:50 `session_state.json` 재확인. 3일 연속이면 확정 구조적 결함.

### 2. 병행 세션 확인 — 오늘 새벽 딥다이브 3건(527·528·529차) 역링크

장전 점검 세션 이전에 이미 같은 날 별도 세션이 조사 문서 3건을 작성하고 커밋 2건(`c9f76f8`, `9738080`)으로
관측 전용 채널(P5-14/15/16, 사전등록만·매매 동작 0)을 반영해뒀다. 오늘 리포트 §1 "이미 반영된 사안"에
경로+결론+영향 역링크를 남겼다(§0 병행 세션 확인 규약). 코드 변경 없음(조사 세션도 이번 세션도).
- `docs/정기점검/매일점검/MW0601-20260904-탈진레짐-보유현황과작동이력-조사.md`
- `docs/정기점검/매일점검/MW0601-20260904-탈진위치진입-C1C4-사전감지게이트-조사.md`
- `docs/정기점검/매일점검/MW0601-20260904-스윙피처도입과-3vwap-TrendGate-손익최적안.md`

### 3. 설정 불변식·게이트 인벤토리 — 전부 일치, 신규 이상 없음

수집기 §3 표 24개 항목 전부 `일치`(CB②=3 복원 확인 포함), 차단 게이트 34개 중 9개 꺼짐 — 전부 기존
등록된 한시예외·기능토글. 브랜치 `v9-dev` 확인, HEAD `9738080`, 미커밋 516건 전량 EOL/CRLF 파생(실질
코드 변경 0, 리눅스 샌드박스 마운트 특성 — 조치 불필요).

### 4. 개장 준비 확인 — A절 체크리스트 전 항목 정상

- 단일 인스턴스 확인(`[GUARD] 기존 main.py 없음`), Cybos preflight 통과, PID 11496.
- 런타임 `Python 3.7.13 32bit | scipy=1.5.4 | sklearn=1.0.2 | joblib=1.1.0 | numpy=1.21.6`
  (joblib 1.1.0 vs CLAUDE.md 표기 1.1.1 — 491차 기지 사안, 재상정 안 함).
- 모델 로드: `[RF] 로드 완료: 6호라이즌 ready=True`(08:40:33).
- 매크로 2단계 수집: seed 08:55:18 → 레짐 확정 08:58:21 `RISK_ON`(VIX 15.2·SP500 +1.06%·USD/KRW -0.44%).
- 실시간 구독 사전 시작 08:45:18(개장 09:00보다 앞섬) — 정상.
- 옵션체인: 초기화 5242종목 캐시(08:40:48) → PCR Worker 완료 09:01:07 `PCR=0.851 ATM_PCR=0.875 GEX=78.84B`.
- 오늘 브로커=Cybos이므로 OPT50029/OPT10080 TR 판정은 해당 없음(CLAUDE.md 각주) — 대신 실시간 틱 +
  `[BAR-CLOSE]` 자체 집계 로그(SYSTEM.log 컴포넌트 상위: `BAR-CLOSE`×16) 확인.


```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 남은 것
### 관측 예정
## 2026-09-04 (MW0601 527·528차 — 탈진 레짐 조사 · C1~C4 사전감지 조사) — 승인 대기
### 관측 예정
## 2026-09-04 (MW0601 529차 — 스윙 피처 착수 · 3_vwap×TrendGate 최적안)
## 2026-09-04 (MW0601 529차 후속 — 채널 3종 구현 완료)
### 남은 것
## 2026-09-04 (MW0601 530차 — 장전 점검)
```

미완료 체크박스 **2423건** (끝에서 30건)
```
- [ ] **526-2 / P5-13** 채널 `data_anomaly_gate_watch` — 판정식 `min_days=10` 且 비중첩 `min_samples=30` · 일자 p<0.05 · 수수료 포함 net>0 ·
- [ ] **526-3 / F-C (P2)** `_Z_WARN_EXEMPT`에 `quality_*` 12종 추가 + OFI 항등 3종·`cvd_direction` dedupe — **스케일러 모니터 집계·대시보드에만**
- [ ] **O-t9** F-A 배선 첫 거래일: `DataAnomalyGate` 분 수 ≈ 종전 z-only 급변장 분 수(일평균 ~12분)인지 · 리플레이 잡음 전환 0건인지.
- [ ] **526-4 (P1, 라이브 검증)** 다음 거래일 확인 — ① `[MicroRegime] … 근거=` 로그 출현 ② `DataAnomalyGate` 분 수
- [ ] **526-5 (P2)** P5-13이 `min_days=10`·`min_samples=30`을 **gate 표본만으로** 채우는 시점 재판정
- [ ] **526-6 (P2)** `raw_features_horizon.regime`·`regime_history`가 **③ 제외 라벨**을 저장하는지 확인
- [ ] **525-4 (P2, 유지)** 349차 `VolatilityBurstGuard` 0회 발동 — 임계 재측정.
- [ ] **O-t9** 위 526-4 5항목. 미달이면 배선 결함으로 즉시 격상.
- [ ] **527-A (P1 계측)** 교정판 소진 신호 bear 0건 원인 규명 — `cvd_exhaustion.py` detrend 오실레이터가 단조증가 계열에서
- [ ] **527-B (P2 문서)** 탈진 레짐을 "예약(도달 불가)"로 CLAUDE.md/CORE.md에 명기 + 83차 후속("0회면 하한 1.1") **철회**(병목은 c2) +
- [ ] **528-A [18b]** `RegimeExhaustionGate` hurst<0.45 전제 해제 변형 섀도 — 별도 테이블/컬럼으로 카운터팩추얼. C2형 포착 여부 + 79건 부호 유지 확인.
- [ ] **528-B [16]** `chase_foreign_combo_watch` 판정식 사전등록 — `min_samples=20`(현 23) 且 `min_days=10` 且 일자 p<0.05 且 drop-worst 유지
- [ ] **528-C** 채널 `leg_exhaustion_entry_watch` 사전등록 — `run≥5 ATR 且 60분 극단≤1 ATR 순방향`, `min_days=25` 且 일자 p<0.05 且
- [ ] **528-D (주간회의 안건)** CORE 3_vwap 순방향 요구 + TrendGate streak≥10 완화가 진입을 연장 쪽으로 미는 구조 — "레그 길이"를
- [ ] **O-t10** CFCG "강등 후보" 뒤 진입 손익 누적(현 23건 −248,263) — 528-B 판정 표본.
- [ ] **O-t11** streak≥10 ON 분 순방향 진입(524차 O-t5 승계, 현 13건 avg −25,376) — 5건 이상 추가 시 집계.
- [ ] **529-2 (P1 라이브 검증)** 첫 거래일: `raw_features`에 `swing_ready_60m` True 비율(개장 60분 후 ~100%) · `dist_to_*` 분포가 오프라인
- [ ] **529-A** 채널 `leg_exhaustion_entry_watch` 사전등록(승인 대기) — 모집단 순방향 진입 且 run≥5 ATR 且 극단≤1.0 ATR 且 ready.
- [ ] **529-B** 승격 형태 사전 확정(감점 `12_leg_position` vs 사이저 ×0.5) — 판정 전에 채널 판정문에 박는다.
- [ ] **529-C** 채널 `streak_leg_end_watch` — TrendGate 완화 적용 분 且 레그 끝 진입(현 35건 −243k / 완화-필수 5건 5승) `min_samples=20`.
- [ ] **529-E** 관측 `leg_entry_early_watch` — 초입(run≤2) 12건 10/2 +532k · 이탈≥1.5σ 且 초입 15건 12/3 +675k.
- [ ] **529-D** 3_vwap **무변경** 확정 기록(실측: 상한 감점 시 +675k 군 손상).
- [ ] **529-2 (P1 라이브 검증, 재확인)** 첫 거래일 스윙 피처 적재 — `swing_ready_60m` True 비율 · `dist_to_*` 분포 ·
- [ ] **529-F (P2)** 캠페인 주간 리포트에 P5-14/15/16 렌더링 연결 — 현재는 `leg_position_watch.py` 단독 실행이다
- [ ] **529-G (P2)** C 채널 원천 취약성 — TrendGate 활성 상태를 `ensemble_decisions`에 컬럼으로 남길지 검토
- [ ] **529-H** 처리군 거래일 25일 도달 시 A 재판정 → `SOFT_DEMOTE_CANDIDATE`면 주간회의 상정(승격 형태는 확정됨).
- [ ] **530-1 / F-1 (P1, 격상)** `data/session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`
- [ ] **530-2 / G-1 (P2)** `_write_session_state()`가 실제로 기록하는 키 목록 + 파일 mtime을 매 호출마다
- [ ] **O-p1** `[ConfFloorGuard] 자동진입 하한 도달 불가`(09:00:00, 보정기 출력상한 0.3479 < 필요 0.4230)
- [ ] **529-2 재확인(오늘 장후)** 스윙 위치 피처 7키 첫 라이브 적재 — `swing_ready_60m` True 비율(개장
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 `streak_leg_end_watch` — TrendGate 완화 적용 분 且 레그 끝 진입(현 35건 −243k / 완화-필수 5건 5승) `min_samples=20`.
- [ ] **529-E** 관측 `leg_entry_early_watch` — 초입(run≤2) 12건 10/2 +532k · 이탈≥1.5σ 且 초입 15건 12/3 +675k.
- [ ] **529-D** 3_vwap **무변경** 확정 기록(실측: 상한 감점 시 +675k 군 손상).
## 2026-09-04 (MW0601 529차 후속 — 채널 3종 구현 완료)

- [DONE 2026-09-04] **529-A/B** 채널 `leg_exhaustion_entry_watch`(P5-14) 사전등록 + 승격 형태 확정
      (`checklist_demote` 1순위 · `size_half` 2순위 · 하드차단 금지). 첫 판정 **INSUFFICIENT**(17/25일).
- [DONE 2026-09-04] **529-C** 채널 `streak_leg_end_watch`(P5-15). 첫 판정 **NO_CHANGE**(p=1.00).
- [DONE 2026-09-04] **529-D** 확정 결정 2건 등록 — `core_vwap_directional_requirement`(3_vwap 무변경) ·
      `trend_gate_relax_keep`(완화 유지).
- [DONE 2026-09-04] **529-E** 관측 채널 `leg_entry_early_watch`(P5-16) — OBSERVE, 승격 경로 없음.
- [DONE 2026-09-04] 판정기 `scripts/leg_position_watch.py` + `tests/test_529_leg_position_watch.py`(40 passed 합산).

### 남은 것
- [ ] **529-2 (P1 라이브 검증, 재확인)** 첫 거래일 스윙 피처 적재 — `swing_ready_60m` True 비율 · `dist_to_*` 분포 ·
      `[FeatureBuilder] 스윙 피처 오류` 0건. 추가로 `leg_position_watch.py`의 `source_crosscheck`가
      **db vs replay_proxy 불일치 0**인지(배선 검증의 유일 수단).
- [ ] **529-F (P2)** 캠페인 주간 리포트에 P5-14/15/16 렌더링 연결 — 현재는 `leg_position_watch.py` 단독 실행이다
      (`spread_extreme_watch`와 같은 상태). EOD 체인 편입 여부는 주간회의.
- [ ] **529-G (P2)** C 채널 원천 취약성 — TrendGate 활성 상태를 `ensemble_decisions`에 컬럼으로 남길지 검토
      (지금은 로그 파싱이라 `LOG_KEEP_DAYS`가 표본 상한). 계측 4원칙 ②(미측정≠0) 적용 대상.
- [ ] **529-H** 처리군 거래일 25일 도달 시 A 재판정 → `SOFT_DEMOTE_CANDIDATE`면 주간회의 상정(승격 형태는 확정됨).

## 2026-09-04 (MW0601 530차 — 장전 점검)

- [ ] **530-1 / F-1 (P1, 격상)** `data/session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`
      마커가 2일 연속(09-03→09-04) 아침에 소실 — 원인 미규명. 내일(09-05) 아침 재확인해 3일 연속이면
      확정 구조적 결함으로 보고 `main.py:_write_session_state()`/`_read_session_state()` 호출부
      (09-03 기준 3382/3395/4757/4968/12031/13030행 — 재확인 필요)에 진단 로그 추가 착수.
- [ ] **530-2 / G-1 (P2)** `_write_session_state()`가 실제로 기록하는 키 목록 + 파일 mtime을 매 호출마다
      DEBUG 로그로 남긴다 — 530-1 재발 시 어느 호출이 두 키를 지웠는지 로그만으로 특정하기 위한 선행 계측.
      장후 이후 적용.
- [ ] **O-p1** `[ConfFloorGuard] 자동진입 하한 도달 불가`(09:00:00, 보정기 출력상한 0.3479 < 필요 0.4230)
      — 기존 반복 패턴, 오전 중 자연 복귀 여부를 오늘 장중·장후에 판정.
- [ ] **529-2 재확인(오늘 장후)** 스윙 위치 피처 7키 첫 라이브 적재 — `swing_ready_60m` True 비율(개장
      60분 후 ~100% 기대) · `dist_to_*` 분포가 오프라인 재현(179건 run p50 5.7 ATR)과 같은 자릿수인지 ·
      `[FeatureBuilder] 스윙 피처 오류` 로그 0건 · `leg_position_watch.py`의 `source_crosscheck`
      db vs replay_proxy 불일치 0.


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

### `data/heartbeat_MW0601_20260904.json` — 243B · 09-04 12:27:25
```json
{
 "pid": 11496,
 "written_at": "2026-09-04T12:27:55",
 "beat_epoch": 1788492473.3492506,
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

- 파일 최종 기록: **09-04 12:14:02**

| 키 | 값 | 수집 대상일(2026-09-04)과 일치 |
|---|---|---|
| `date` | 2026-09-04 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 107개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260904-점검리포트.md` | 18.2KB | 09-04 09:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20260904_pre.md` | 51.1KB | 09-04 09:01 |
| `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md` | 85.0KB | 09-04 07:51 |
| `docs/정기점검/매일점검/MW0601-20260904-스윙피처도입과-3vwap-TrendGate-손익최적안.md` | 10.9KB | 09-04 07:38 |
| `docs/정기점검/매일점검/MW0601-20260904-탈진위치진입-C1C4-사전감지게이트-조사.md` | 17.4KB | 09-04 06:41 |
| `docs/정기점검/매일점검/MW0601-20260904-탈진레짐-보유현황과작동이력-조사.md` | 15.6KB | 09-04 06:23 |
| `docs/정기점검/매일점검/MW0601-20260903-급변장라벨fix-손익과제안-딥다이브.md` | 20.3KB | 09-04 05:50 |
| `docs/정기점검/매일점검/MW0601-20260903-급변장기준과차단손익-딥다이브.md` | 17.3KB | 09-03 22:54 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260828.md` | 4.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260828.md` | 28.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260828.json` | 35.2KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260828.md` | 178.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260828.json` | 97.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260904_WARN.log`: ERROR 이상 105건
2. `logs/20260904_SYSTEM.log`: 매분 루프 커버리지 209/371분 (56.3%) — 루프가 빠진 구간이 있다
3. `logs/20260904_SYSTEM.log`: 12:29~15:10 **연속 162분 매분 루프 기록 없음**
4. `logs/20260904_HEALTH.log`: ERROR 이상 58건
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. `logs/20260904_WARN.log`: **degraded=ON** 8건(표본)
7. `logs/20260904_WARN.log`: **level=CRITICAL** 2건(표본)
8. `logs/20260904_WARN.log`: **ConstOut** 3건(표본)
9. `logs/20260904_SYSTEM.log`: **ConstOut** 8건(표본)
10. `logs/20260904_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20260904_SIGNAL.log`: **ConstOut** 8건(표본)
12. `logs/20260904_LEARNING.log`: **축퇴** 8건(표본)
13. `logs/20260904_HEALTH.log`: **degraded=ON** 8건(표본)
14. `logs/20260904_HEALTH.log`: **level=CRITICAL** 2건(표본)
15. 미커밋 변경 520건 (실질 2건 · 코드 0건 · EOL 파생 516건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260904*.log` (Windows) / `grep 강제청산 logs/*20260904*.log`*