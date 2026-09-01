# 미륵이 증거 다이제스트 — 2026-09-01 / INTRA

- 생성 2026-09-01 12:27:26 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/adoring-cool-planck/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260901` · `2026-09-01` · `260901` · `0901`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **21개** 파일 · 21개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260901.log` | 125B | 09-01 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260901.log` | 139B | 09-01 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260901.json` | 244B | 09-01 12:27 |
| `launcher_{DATE}_084002_20299.log` | 1 | `logs/Mireuk_batch/launcher_20260901_084002_20299.log` | 1.0MB | 09-01 12:27 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260901.log` | 2.9KB | 09-01 09:00 |
| `retrain_intraday_20260716_10{DATE}.log` | 1 | `logs/retrain_intraday_20260716_100901.log` | 4.5KB | 07-16 10:09 |
| `retrain_intraday_20260807_{DATE}03.log` | 1 | `logs/retrain_intraday_20260807_090103.log` | 4.5KB | 08-07 09:01 |
| `retrain_intraday_{DATE}_092700.log` | 1 | `logs/retrain_intraday_20260901_092700.log` | 2.7KB | 09-01 09:27 |
| `retrain_intraday_{DATE}_102000.log` | 1 | `logs/retrain_intraday_20260901_102000.log` | 2.7KB | 09-01 10:20 |
| `retrain_intraday_{DATE}_111200.log` | 1 | `logs/retrain_intraday_20260901_111200.log` | 2.7KB | 09-01 11:12 |
| `{DATE}_DATA.log` | 1 | `logs/20260901_DATA.log` | 183.4KB | 09-01 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260901_DEBUG.log` | 131.1KB | 09-01 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260901_HEALTH.log` | 5.1KB | 09-01 12:02 |
| `{DATE}_HOGA.log` | 1 | `logs/20260901_HOGA.log` | 27.7MB | 09-01 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260901_LEARNING.log` | 182.6KB | 09-01 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260901_MICRO.log` | 562.0KB | 09-01 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260901_PROBE.log` | 57.6KB | 09-01 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260901_SIGNAL.log` | 343.9KB | 09-01 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260901_SYSTEM.log` | 524.4KB | 09-01 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260901_TRADE.log` | 17.1KB | 09-01 11:39 |
| `{DATE}_WARN.log` | 1 | `logs/20260901_WARN.log` | 75.1KB | 09-01 12:21 |

## 2. 코드·커밋 상태

- HEAD `c5eddda` · 브랜치 `v9-dev` · 미커밋 515건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 511건 (추적변경 513 · 미추적 2 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
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
… 외 475건
```

**당일(2026-09-01) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
db48586 [MW0601] 507차 후속: 리포트 제8부에 커밋 해시 기입
2d6a1bb [MW0601] 507차 후속: 장후 자동조치 — F-7·F-8·F-11·F-12·F-14 + G-4·G-5
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
6dfe6d7 [MW0601] 504차: 8월 손실일 딥다이브 + 손익추이2(CREON 반사실)·거래 출처 필터
fc05088 [MW0601] test_479 오탐 정정: broker_net_chain_audit.py를 _COMPRESSED_AWARE에 등록
1c51249 [MW0601] dev 502차 후속 체리픽: U-1 te ready 플래그 + U-2 [57] 게이트 섀도 배선
614eda2 [MW0601] dev 501차 D1 정정 실행 완료 — daily_broker_pnl 브로커net 재산출
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `9999` | `9999` | 일치 | 모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. 재검토 기한 2026-08-29 |
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

### 차단 게이트 전수 인벤토리 — 33개 중 **9개 꺼짐**

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

_본문 미열람(설정): `20260901_HOGA.log` 27.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20260901_092700.log`, `retrain_intraday_20260901_111200.log`, `retrain_intraday_20260901_102000.log`, `20260901_MICRO.log`, `20260901_DATA.log`, `20260901_PROBE.log`, `launcher_20260901_084002_20299.log`, `20260901_DEBUG.log`_

### `logs/20260901_TRADE.log` — 17.1KB · 130행 · 최종 11:39:59

- 형식 평문 · 시각 인식 130행 · WARNING=12, INFO=118

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-01 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-01 09:09:02 [INFO] TRADE: [Chejan] 상태=접수 주문번호=462 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-01 09:09:04 [INFO] TRADE: [Chejan] 상태=체결 주문번호=462 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-01 09:09:04 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1063.54 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
  …
2026-09-01 11:39:59 [INFO] TRADE: [주문요청] 하드스톱(틱) 청산 SHORT 1계약 @ 1063.79 체결대기
2026-09-01 11:39:59 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2828 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-01 11:39:59 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2828 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-01 11:39:59 [INFO] TRADE: [Position] 체결청산 SHORT @ 1063.74 | PnL=+0.42pt (+10,560원) | 하드스톱(틱)
2026-09-01 11:39:59 [INFO] TRADE: [청산 완료] PnL=+0.42pt (+10,560원) | 포지션 합계 +10,560원 (레그 1)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 12 | 09:09:04 | 09:33:44 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1063.54 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×130

**컴포넌트 상위 15** — `Chejan`×45, `Position`×29, `PositionFallback`×12, `체결동기화`×12, `주문요청`×8, `청산 완료`×8, `TickStop-S0C`×5, `체결청산-부분`×3, `TickTP1`×3, `ProfitGuard`×1, `TP1 부분청산`×1, `Sizer`×1, `진입체크`×1, `체결진입`×1

### `logs/20260901_WARN.log` — 75.1KB · 379행 · 최종 12:21:00

- 형식 평문 · 시각 인식 379행 · CRITICAL=18, WARNING=361

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-01 08:41:07 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 47ms
2026-09-01 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-09-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
2026-09-01 08:41:14 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3500ms — live 중단 원인 분석용
  …
2026-09-01 12:16:02 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: RESTRICTED → WATCH (acc=30.0%)
2026-09-01 12:16:02 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: RESTRICTED → WATCH (acc=30.0%)
2026-09-01 12:18:00 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: WATCH → NORMAL (acc=36.7%)
2026-09-01 12:18:00 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: WATCH → NORMAL (acc=36.7%)
2026-09-01 12:21:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.109% (임계 ±0.098%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 18 | 09:23:01 | 09:40:00 | level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
```

</details>

**WARNING — 태그 32종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 124 | 08:41:07 | 11:40:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 45 | 09:09:02 | 11:39:59 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1063.54 | fill_qty=1 | gubun='0' | order_no='462' | pending='NONE' | position='FLAT' | position_qty=0 | sell_balance=0 | side='LONG' | … |
| `ChejanMatch` | 45 | 09:09:03 | 11:39:59 | order_no='462' | pending='NONE' | pending_matched=False |
| `OrderSync` | 28 | 09:09:04 | 09:33:44 | 미추적 체결 감지 (pending_miss) order_no=462 side=LONG qty=1 price=1063.54 before=FLAT |
| `PendingOrder` | 16 | 09:10:49 | 11:39:59 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 1059.68, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `ExitCooldown` | 16 | 09:10:49 | 11:39:59 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:13:49) |
| `Health` | 11 | 09:00:01 | 12:01:00 | level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |
| `ExitFillFlow` | 9 | 09:10:49 | 11:39:59 | after='FLAT' | before='LONG 1계약 @ 1063.54' | fill_price=1059.64 | fill_qty=1 | mode='final' | pending='EXIT_FULL:LONG qty=1 filled=1 order_no=504 reason=하드스톱(틱) req_at=09:10:49.779' | reason='하드스톱(틱)' |
| `ScalerRefresh` | 9 | 09:14:00 | 12:21:00 | 5분 누적 수익률 -0.557% (임계 ±0.445%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `CB③-P4` | 8 | 10:52:01 | 12:18:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=3.3%) |
| `TickStop` | 5 | 09:10:49 | 11:39:59 | 스톱 히트 감지 (틱) LONG tick=1059.64 stop=1059.68 → 즉시 처리 예약 |
| `ExitSendOrderResult` | 5 | 09:10:49 | 11:39:59 | ret=0 kind=하드스톱(틱) direction=LONG qty=1 |

**채널** — `SYSTEM`×350, `HEALTH`×29

**컴포넌트 상위 15** — `LiveDBG`×124, `ChejanFlow`×45, `ChejanMatch`×45, `Health`×29, `OrderSync`×28, `PendingOrder`×16, `ExitCooldown`×16, `ExitFillFlow`×9, `ScalerRefresh`×9, `CB③-P4`×8, `TickStop`×5, `ExitSendOrderResult`×5, `CB`×5, `PartialExitAttempt`×4, `HealthPolicy`×3

### `logs/20260901_SYSTEM.log` — 524.4KB · 3540행 · 최종 12:27:07

- 형식 평문 · 시각 인식 3533행 · INFO=3533, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=17924 | 행감지=30s all_threads=True
2026-09-01 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-01 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-01 08:40:49 [INFO] SYSTEM: 미륵이 초기화
2026-09-01 08:40:49 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-31) 종가 버퍼 로드: 384봉
  …
2026-09-01 12:28:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=12:27 vol=278 | live_buy=176 shadow_buy=147 anchor_buy=147 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-09-01 12:28:00 [INFO] SYSTEM: [MicroRegime] 추세장 → 횡보장 (ADX=10.9, ATR=0.891, ratio=0.95)
2026-09-01 12:28:00 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=17ms meta_gate=10ms gates=0ms imp=0ms shap=5ms corr=10ms dash_ui=0ms tail=16ms
2026-09-01 12:28:00 [INFO] SYSTEM: [PipePerf][DBG] total=376ms | S0=2ms S1=18ms S2=10ms S3=0ms S4=91ms S5=184ms S6=61ms S7=5ms S8=4ms
2026-09-01 12:28:01 [INFO] SYSTEM: [CybosRT-TICK] #71200 code=A0569 raw_time=122800 parsed=12:28:00 price=1068.38 vol=1 bid1=1068.36 ask1=1068.44 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3533

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×717, `CybosRT-ROLLOVER`×223, `BAR-CLOSE`×223, `CVD-ANCHOR`×223, `TickUI`×222, `S6Detail`×209, `PipePerf`×209, `CybosEvent`×90, `BalanceUI`×80, `CybosDailyPnl`×74, `System`×59, `MicroRegime`×55, `BalanceRefresh`×54, `RegimeFingerprint`×39

### `logs/20260901_SIGNAL.log` — 343.9KB · 3027행 · 최종 12:27:01

- 형식 평문 · 시각 인식 3027행 · WARNING=1293, INFO=1734

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.416
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
  …
2026-09-01 12:28:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=None)
2026-09-01 12:28:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
2026-09-01 12:28:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-09-01 12:28:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=85.0% grade=X micro=횡보장
2026-09-01 12:28:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 762 | 09:00:02 | 12:21:00 | 1m 'macro_sp500_chg' scale=0.0574 → floor=0.15 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 192 | 08:45:08 | 12:21:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0205) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 113 | 09:00:00 | 12:12:01 | ts=08:59 horizon=1m age=1m max_z=-7.42(prev_day_same_hour_ret) extreme=1 |
| `Model` | 94 | 09:00:00 | 12:11:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 74 | 09:06:00 | 12:27:01 | 신뢰도 미달 34.3% < 38.6% → 강제 X등급 |
| `WeightCollapse` | 45 | 09:07:00 | 12:28:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `MetaGate` | 7 | 09:30:00 | 09:43:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `ConfFloorGuard` | 3 | 09:00:01 | 11:20:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `ConstOut` | 3 | 09:26:01 | 11:11:00 | 3m 상수 출력 5분 감지 (range=0.0040 dir=-1) → 앙상블 제외 |

**채널** — `SIGNAL`×3027

**컴포넌트 상위 15** — `ScalerFloor`×816, `SIGNAL`×418, `MetaGate`×246, `ScalerRefresh`×221, `Ensemble`×212, `ZeroDiag`×208, `FQAdj`×206, `Model`×118, `ScalerMonitor`×113, `Checklist`×76, `ATR-Horizon`×74, `MicroRegime`×55, `InstabilityGate`×47, `WeightCollapse`×45, `차단`×35

### `logs/20260901_LEARNING.log` — 182.6KB · 1680행 · 최종 12:27:01

- 형식 평문 · 시각 인식 1680행 · WARNING=163, INFO=1517

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.508 out_max=0.3054 (기준 auc<0.53 and span<0.020, 기저율=0.3053 n=95) → 보정 미적용, raw 통과
2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.436 out_max=0.1126 (기준 auc<0.53 and span<0.020, 기저율=0.1125 n=80) → 보정 미적용, raw 통과
2026-09-01 08:40:51 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00058 auc=0.537 out_max=0.2913 (n=110) → 보정 재적용
  …
2026-09-01 12:28:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=33.3% UP)
2026-09-01 12:28:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=40.7% 예측=UP 실제=FL)
2026-09-01 12:28:00 [INFO] LEARNING: [Bias⚠] 3m 적중=27%(8/30) UP=3 DN=7 FL=20 [FL편향⚠ 67%]
2026-09-01 12:28:00 [INFO] LEARNING: [MetaConf] LR[추세장] 비동기 결과 반영 (cnt=9703)
2026-09-01 12:28:00 [INFO] LEARNING: [SGD] 2건 학습 | SGD비중=30% 50분정확도=6.2%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 163 | 08:40:51 | 12:15:01 | 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×1680

**컴포넌트 상위 15** — `LEARNING`×663, `Calibration`×319, `SGD`×209, `sigma`×196, `Bias⚠`×88, `Bias`×77, `MetaConf`×41, `ScalerWarmup`×29, `OnlineLearner`×23, `SHAP`×8, `GBM-64`×6, `GBM`×6, `BiasReset`×5, `RF`×4, `ExtremityCorrector`×2

### `logs/20260901_HEALTH.log` — 5.1KB · 37행 · 최종 12:02:01

- 형식 평문 · 시각 인식 37행 · CRITICAL=18, WARNING=11, INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0
2026-09-01 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=744ms | quality=0.86 | cache_age=98s | exceptions_10m=0
2026-09-01 09:21:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=266ms | quality=1.00 | cache_age=184s | exceptions_10m=4
2026-09-01 09:22:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=316ms | quality=1.00 | cache_age=57s | exceptions_10m=7
2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
  …
2026-09-01 11:22:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=471ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-09-01 11:24:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=312ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-09-01 11:25:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=347ms | quality=1.00 | cache_age=56s | exceptions_10m=0
2026-09-01 12:01:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=268ms | quality=1.00 | cache_age=187s | exceptions_10m=2
2026-09-01 12:02:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=331ms | quality=1.00 | cache_age=60s | exceptions_10m=2
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 18 | 09:23:01 | 09:40:00 | level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 11 | 09:00:01 | 12:01:00 | level=WARNING degraded=OFF | latency=1651ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |

**채널** — `HEALTH`×37

**컴포넌트 상위 15** — `Health`×36, `HealthTrend`×1

### `logs/retrain_intraday_20260716_100901.log` — 4.5KB · 39행 · 최종 10:09:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,736 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
2026-07-16 10:09:04,490 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-16 10:09:36,601 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.43s | old_acc=0.2874)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 완료 | 32.1초 | 성공=6/6 호라이즌
2026-07-16 10:09:36,606 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.9s 데이터=20000행
2026-07-16 10:09:36,607 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260807_090103.log` — 4.5KB · 39행 · 최종 09:01:47

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-07 09:01:03,400 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_40c7d357.json
2026-08-07 09:01:07,156 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-07 09:01:47,800 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=0.95s | old_acc=0.4289)
2026-08-07 09:01:47,839 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-07 09:01:47,839 [INFO] LEARNING: [Retrain] 완료 | 40.7초 | 성공=6/6 호라이즌
2026-08-07 09:01:47,840 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 44.4s 데이터=4800행
2026-08-07 09:01:47,841 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_40c7d357.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) — **엔진** | 1 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 13 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 12 |
| 청산(`체결청산`) | 8 |
| 차단(`[차단]`) | 35 |
| 사이저 호출(`[Sizer]`) | 1 |

### 포지션 8건 · 승 3 (38%) · 합계 -21.40pt (-1,205,674원)  ※ 레그 12행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:09:04 (추정귀속) | 외부 | LONG | 1 | — | 1 | -3.90 | -205,434 | 하드스톱(틱) |
| 09:20:27 (추정귀속) | 외부 | LONG | 2 | — | 1 | -4.56 | -248,854 | 미추적체결(pending_miss) |
| 09:22:03 (추정귀속) | 외부 | SHORT | 3 | — | 3 | -11.28 | -595,230 | 하드스톱(틱) |
| 09:25:03 (추정귀속) | 외부 | LONG | 2 | — | 2 | +5.82 | +270,110 | TP2(전량) |
| 09:28:00 (추정귀속) | 외부 | LONG | 1 | — | 1 | +3.20 | +149,541 | 미추적체결(pending_miss) |
| 09:32:24 (추정귀속) | 외부 | LONG | 1 | — | 1 | -3.54 | -187,477 | 하드스톱(틱) |
| 09:33:32 (추정귀속) | 외부 | SHORT | 2 | — | 2 | -7.56 | -398,890 | 하드스톱(틱) |
| 11:38:01 | 엔진 | SHORT | 1 | 3m | 1 | +0.42 | +10,560 | 하드스톱(틱) |

**출처별 소계** — 엔진 1건 +10,560원 · 외부 7건 -1,216,234원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 7건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 12행** (부분청산 4 · 전량청산 8)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:10:49 | 전량 | 1 | -3.90 | -205,434 | 하드스톱(틱) |
| 09:21:43 | 전량 | 2 | -2.28 | -248,854 | 미추적체결(pending_miss) |
| 09:25:02 | 부분 | 1 | -3.76 | -198,410 | 하드스톱(틱) |
| 09:25:02 | 부분 | 1 | -3.76 | -198,410 | 하드스톱(틱) |
| 09:25:02 | 전량 | 1 | -3.76 | -198,410 | 하드스톱(틱) |
| 09:26:23 | 부분 | 1 | +2.33 | +106,055 | TP1 부분청산 33% |
| 09:27:00 | 전량 | 1 | +3.49 | +164,055 | TP2(전량) |
| 09:31:34 | 전량 | 1 | +3.20 | +149,541 | 미추적체결(pending_miss) |
| 09:33:09 | 전량 | 1 | -3.54 | -187,477 | 하드스톱(틱) |
| 09:37:02 | 부분 | 1 | -3.78 | -199,445 | 하드스톱(틱) |
| 09:37:02 | 전량 | 1 | -3.78 | -199,445 | 하드스톱(틱) |
| 11:39:59 | 전량 | 1 | +0.42 | +10,560 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×8, `미추적체결(pending_miss)`×2, `TP1 부분청산 33%`×1, `TP2(전량)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 5/8건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -1,205,674 = 포지션합 -1,205,674 → OK · `[청산 완료]` 8건 = 조립 포지션 8건 → OK

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:38:01 | SHORT | 1 | 1063.96 | 3m | neutral |

계약수 분포 — 1계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×1, `fore`×1, `prev`×1, `risk`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1

실제 진입 계약수 — **1계약**×1

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×1

### 차단 사유 35건 · 10종

| 건수 | 사유 |
|---|---|
| 25 | 등급X — 미통과 항목: 2_confidence |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 청산 후 쿨다운 — 94초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 121초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 61초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 1초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 118초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 58초 후 재진입 가능 |
| 1 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.83pt < 1.0pt — 변동성 부족 (휩쏘 위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×25

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `연속 손절 2회 (300초 창, 포지션 단위)` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 5건 · 최대 6250ms · 5초 초과 1건

상위 — 6250ms, 4813ms, 3125ms, 2891ms, 2141ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 6250ms | 1651ms | **4599ms (74%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260901_WARN.log`
```
--- ConstOut ×3(표본)
09:26:01 2026-09-01 09:26:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:19:00 2026-09-01 10:19:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:11:00 2026-09-01 11:11:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×1(표본)
09:00:06 2026-09-01 09:00:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260901.log
--- [CB] ×5(표본)
09:10:49 2026-09-01 09:10:49 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:21:43 2026-09-01 09:21:43 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:25:02 2026-09-01 09:25:02 [WARNING] SYSTEM: [CB] 연속 손절 2회 (300초 창, 포지션 단위)
09:33:09 2026-09-01 09:33:09 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:10:49 2026-09-01 09:10:49 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:13:49)
09:10:49 2026-09-01 09:10:49 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:13:49)
09:21:43 2026-09-01 09:21:43 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 3분 재진입 금지 (until 09:24:43)
09:21:43 2026-09-01 09:21:43 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 3분 재진입 금지 (until 09:24:43)
--- [SHAP] 슬로우 ×2(표본)
11:40:01 2026-09-01 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 912ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:57:02 2026-09-01 11:57:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 920ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- degraded=ON ×8(표본)
09:24:00 2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
09:25:00 2026-09-01 09:25:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=281ms | quality=1.00 | cache_age=51s | exceptions_10m=13
09:26:01 2026-09-01 09:26:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=419ms | quality=1.00 | cache_age=112s | exceptions_10m=18
09:27:00 2026-09-01 09:27:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=519ms | quality=1.00 | cache_age=171s | exceptions_10m=18 [GBM재학습중→lat임계 5000/10000ms]
--- level=CRITICAL ×1(표본)
09:23:01 2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
--- 메인 스레드 블로킹 ×5(표본)
08:41:11 2026-09-01 08:41:11 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3125 band=INFO since_pipe_s=NA
08:46:05 2026-09-01 08:46:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2891ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2891 band=INFO since_pipe_s=NA
09:00:06 2026-09-01 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6250 band=WARN since_pipe_s=0.1
09:01:01 2026-09-01 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.1
```

### `logs/20260901_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:26:01 2026-09-01 09:26:01 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:28:00 (const_output)
09:26:01 2026-09-01 09:26:01 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:26:01 2026-09-01 09:26:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=92ms fit=103ms total=197ms
09:27:00 2026-09-01 09:27:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-09-01 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-09-01 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:11:00 2026-09-01 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:16:00 2026-09-01 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20260901_SIGNAL.log`
```
--- ConfFloorGuard ×6(표본)
09:00:01 2026-09-01 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:42:00 2026-09-01 10:42:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3809 ≥ 필요 0.3780
10:55:00 2026-09-01 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3752 < 필요 0.3780 (conf_floor=0.330, min_conf=0.378, span=0.0109). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:13:00 2026-09-01 11:13:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3757 ≥ 필요 0.3720
--- ConstOut ×8(표본)
09:26:01 2026-09-01 09:26:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0040 dir=-1) → 앙상블 제외
09:27:00 2026-09-01 09:27:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:19:00 2026-09-01 10:19:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:21:00 2026-09-01 10:21:00 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-01 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-01 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.5% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-01 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.4% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-01 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.416
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.408
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.404
08:40:31 2026-09-01 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.412
--- 안전망 ×8(표본)
09:07:00 2026-09-01 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-01 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-01 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-01 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260901_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.544 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00018 auc=0.508 out_max=0.3054 (기준 auc<0.53 and span<0.020, 기저율=0.3053 n=95) → 보정 미적용, raw 통과
08:40:51 2026-09-01 08:40:51 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.436 out_max=0.1126 (기준 auc<0.53 and span<0.020, 기저율=0.1125 n=80) → 보정 미적용, raw 통과
08:40:51 2026-09-01 08:40:51 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00058 auc=0.537 out_max=0.2913 (n=110) → 보정 재적용
```

### `logs/20260901_HEALTH.log`
```
--- degraded=ON ×8(표본)
09:24:00 2026-09-01 09:24:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=302ms | quality=1.00 | cache_age=177s | exceptions_10m=13
09:25:00 2026-09-01 09:25:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=281ms | quality=1.00 | cache_age=51s | exceptions_10m=13
09:26:01 2026-09-01 09:26:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=419ms | quality=1.00 | cache_age=112s | exceptions_10m=18
09:27:00 2026-09-01 09:27:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=519ms | quality=1.00 | cache_age=171s | exceptions_10m=18 [GBM재학습중→lat임계 5000/10000ms]
--- level=CRITICAL ×1(표본)
09:23:01 2026-09-01 09:23:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=337ms | quality=1.00 | cache_age=117s | exceptions_10m=13
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260901_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:00 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 11:39

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260901_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 13 | 08:41:07 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 11 | 08:55:08 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 08:55:08 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 2 | 10:01:00 [WARNING] level=WARNING degraded=OFF | latency=304ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |
| 12:00 | 장중 중간점 | 5 | 11:54:00 [WARNING] acc30m 단계 전환: NORMAL → RESTRICTED (acc=16.7%) |

- 이 로그 생존구간: 08:41 ~ 12:21

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260901_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 88 | 08:40:34 [INFO] 활성화 | file=logs\crash_fault.log PID=17924 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 124 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 183 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 212 | 09:54:01 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 169 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:28

**매분 루프 커버리지 09:00~15:10: 209/371분 (56.3%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:29 | 15:10 | 162 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260901_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:08 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0205) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 142 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0170) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 234 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0274) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 197 | 09:54:01 [WARNING] 신뢰도 미달 33.8% < 38.6% → 강제 X등급 |
| 12:00 | 장중 중간점 | 186 | 11:55:00 [WARNING] 신뢰도 미달 35.0% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:28

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| 20260827 | 15:40 | 로그 본문 |
| 20260826 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260901** | **12:28** | 로그 본문 |

- 델타 **-192분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-01 (MW0601 509차 — 장전 점검)
### 증상 → 확인
### 원인 — 결함 없음, 정상 작동 확인
### 결정
### Why
### How to apply
### 검증
### 그 외 장전 확인
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
n.py` CRLF 18,463/18,463 보존(변경 전과 동일). AST 파싱 통과.

### 부수 사실 — 갭 손실과 자동매매 정지는 같은 뿌리다

이월 LONG 4계약이 1068.47 → 1041.18 갭에 맞아 08:45:06 하드스톱 **-5,461,928원**.
당일 총 -6,389,518원의 **85.5%**다. 절대원칙 §1(15:10 강제청산)은 엔진이 연
포지션을 전제하는데 **외부에서 들어와 이월된 포지션에는 장전 강제청산 경로가 없다.**
그리고 바로 그 포지션이 Armistice 고착의 방아쇠였다.
⇒ 「장전 이월 포지션 처리」는 F-6과 **별개 안건**으로 NEXT_TODO에 남긴다.

## 2026-09-01 (MW0601 509차 — 장전 점검)

### 증상 → 확인
08-31 508차(F-6)가 배포한 Restart Armistice 승격 로직이 실제 재시작 상황에서
정상 작동하는지가 오늘 장전 점검의 핵심 확인사항이었다. 08-31 하루 종일
`armistice cleared`가 0건이고 차단이 47건 쌓였던 것과 달리, 오늘은 기동 직후
08:41:07 startup sync 시작 → 08:41:08 `[BrokerSync] startup sync 무포지션
확인(blank rows): FLAT -> FLAT (armistice cleared)` 로 **1분 내 정상 해제**됐다.
F-6이 요구한 3조건(`sync_count<2` AND `time_ok` AND 브로커 동기화 검증완료)이
오늘은 blank-as-flat 해석(`status verified=True block_new_entries=False
reason=blank/no holdings response interpreted as flat`)으로 즉시 충족됐다.

### 원인 — 결함 없음, 정상 작동 확인
어제 사고는 재시작 시점에 실제 이월 포지션이 있었는데 blank 응답을 FLAT으로
잘못 해석해 반대 방향 정리 주문이 신규 진입으로 처리된 것이었다(508차 F-6이
근본 원인은 아직 미해결로 남김 — 「장전 이월 포지션 처리」 별도 안건).
오늘은 실제로 계좌가 비어 있어(전날 08:45:06 하드스톱으로 완전 정리) blank
해석이 우연이 아니라 정답과 일치했다. 즉 **오늘 관측은 F-6의 정상 경로 검증이지,
어제 근본원인(blank=FLAT 오판 자체)의 해소 검증은 아니다** — 그 검증은 실제
이월 포지션이 있는 재시작 상황에서만 가능하다.

### 결정
O-t2(08-31 507차 등록, "다음 거래일 장전 판정") **판정 완료 — 재현 안 됨**으로
닫는다. O-t1·O-t3·O-t4·P-1·P-2는 정의된 대로 장중·장후로 이월.

### Why
F-6 배포 후 첫 재시작 관측이라는 점에서 최소한의 "안 깨졌다" 확인은 의미가
있으나, 위에서 밝힌 대로 오늘은 실제 이월 포지션이 없는 케이스라 F-6의 핵심
분기(blank-as-flat 오판 방지)는 아직 실전 검증되지 않았다. 다음에 실제
이월 포지션이 있는 상태로 재시작하는 날이 이 로직의 진짜 시험대다.

### How to apply
해당 없음(코드 변경 없음, 장전 점검은 관찰만).

### 검증
장전 로그 인용 — `logs/20260901_SYSTEM.log:23~33`.
다음 재시작 시 이월 포지션이 실제로 있는 경우를 만나면 그 케이스로 F-6을
재검증할 것(별도 관측 등록 필요 — 이번 세션은 등록하지 않음, 발생 시 장중/장후가
등록).

### 그 외 장전 확인
- 08:55 사전 재학습 정상 스킵(전일 EOD 성공 08-31) — `[PreRetrain]` 정상 로그.
- py37_32 32bit 런타임 확인(`Python 3.7.13 32bit | scipy=1.5.4`).
- Cybos 접속·구독 정상(`[CybosRT-START]`, `[CybosSub]`).
- 레짐 NEUTRAL 확정(08:58:12, VIX=14.4).
- 계좌 blank-as-flat → FLAT 확인, 이월 포지션 없음(어제 사고 유형 오늘은 재현 안 됨).
- 개장 버스트 메인스레드 정지 6250ms(09:00:06) — CB⑤ 사각 74%(482차 F-3 패턴,
  기지 유형, 신규 아님).
- `[HealthPolicy] Degraded 선제차단`(09:01:00, cause=S5 1207ms) — O-p1로 등록,
  실제 진입 차단 여부는 장중이 `ensemble_decisions`로 확인.
- `[ConfFloorGuard]` 자동진입 하한 도달 불가(09:00:01) — O-p2로 등록, 정상 복귀
  시각은 장중 확인.
- CB②(`CB_CONSEC_STOP_LIMIT=9999`) 재검토 기한(2026-08-29) 초과 지속 — 신규
  아님, 08-31 리포트 사용자 조치 5번과 동일 사안 계속 열려 있음.

근거: `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` 제1부(장전),
`docs/정기점검/매일점검/evidence_MW0601-20260901_pre.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## MW0601 507차 후속 — 장후 자동조치 이월분 (2026-08-31 자동)
### C등급 — 주문·청산 경로 (사용자 지시 없이는 착수 금지)
### C등급 — 판정 기준·표본 (사용자 승인 필요)
### F-4 — 등급상 자동 가능이나 **일부러 멈춤** (근거 있음)
### 고도화 이월 (오늘 상한 3건 소진: G-4·G-5 완료)
### 제5부 수익률 방안 이월
### 정비
### 2026-09-01 (MW0601 509차 — 장전 점검) 등록/이월
```

미완료 체크박스 **2225건** (끝에서 30건)
```
- [ ] **4. net 대사 9만원 차이 — 사용자 조치 없음. 내일 재발 시 조사 지시**(O-t1)
- [ ] **5. CB② 복원 결정** (기한 2026-08-29 경과) — 오늘 「2회」 2번 도달.
- [ ] **6. 08-27·08-28 매일점검 장후 미실행 원인 확인** (2거래일 연속 · 대장 3일 미갱신 유발)
- [ ] **7. 주간회의 안건 3건** — ⓐ 전환기준 ③ 승률의 gross/net 정의 ⓑ F-15 외부진입 손익 처리
- [ ] **8. 커밋 대기 (세 세션 모두 커밋하지 않았다)** — ⚠ `git add .` 금지
- [ ] **F-1 (P0)** blank-rows 폴백을 "유지"에서 "잠금"으로 — `main.py:17107~17132`
- [ ] **F-2 (P0)** `BrokerDirectExit` 주문 실패 재시도 — 🔴 **주간회의 안건**
- [ ] **F-3 (P1)** 15:10 미체결 **진입** 주문 일괄 취소 — 주문 경로.
- [ ] **F-6 (P0)** Restart Armistice 고착 해소 — `main.py:8537~8556`
- [ ] **F-10 (P1)** `partial_1_done` 에 사유 축 — `position_tracker.py:1509~1513`
- [ ] **F-5 (P2)** 08-28 손익 기록 정정 + `METRIC_REDEFINITION` 마커
- [ ] **F-15 (P2)** 외부 진입을 브로커 net 판정 경로에서 분리 — 🔴 **주간회의 안건**
- [ ] **F-13 (P2)** `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` `dev` → `v9-dev` 이식 여부
- [ ] **승률의 정의** — 실전 전환 기준 ③ 「승률 ≥ 53%」가 gross 인지 net 인지
- [ ] **CB② 복원 여부** — 재검토 기한 2026-08-29 경과. 절대원칙 §2 / 전환기준 ⑤.
- [ ] **F-4 (P1)** 일일 마감 손익을 **브로커 포지션 축**과 대사 — `main.py:daily_close()`
- [ ] **G-2** 「장 마감 후 잔고 최종 확인」 잡 — 15:50에 브로커 잔고 1회 조회,
- [ ] **G-1** `position_recon_shadow` — 매분 「엔진 포지션 vs 브로커 잔고 캐시」 대조.
- [ ] **G-3** `entry_gate_stuck_shadow` — 차단 사유별 연속 지속시간 매분 누적,
- [ ] **G-6** `selfinduced_cb_shadow` — CB 발동 직전 60초에 `ConstOut` 재적합 /
- [ ] **P5-06** 분할체결 손절을 손절률 분모에서 되찾는다 — **관찰은 오늘 시작됐다**
- [ ] **P5-07** `net_breakeven_pt`(= 왕복수수료 ÷ (계약수 × 50,000)) 를 청산 시점에
- [ ] **P5-08** 자가유발 CB 발동을 진입공백 비용으로 환산 — G-6 선행.
- [ ] `tests/test_500_*.py` 5개 파일이 pytest 수집 시 `SystemExit: 0` 을 낸다
- [ ] 선행 실패 3건 정리 — `test_483_git_lock_guard[fuoption]`(형제 프로젝트 사본
- [ ] **O-p1(신규)** `[HealthPolicy] Degraded 선제차단`(09:01:00, cause=S5 1207ms)이
- [ ] **O-p2(신규)** `[ConfFloorGuard]` 자동진입 하한 도달 불가(09:00:01) 상태의
- [ ] **O-t1·O-t3·O-t4·P-1·P-2(08-31 이월, 계속)** — 정의된 조건대로 장중·장후 판정 대기.
- [ ] CB② 복원 여부 — 재검토 기한 2026-08-29 경과, 계속 미결(3일째). 절대원칙 §2/전환기준 ⑤.
- [ ] 주간회의 안건 3건(승률 정의·F-15 외부진입 손익·F-13 이식) — 계속 미결.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
T 이면 알림 + `logs/` 기록. **주문 없음 = 이중 청산 위험 0.**
      · 🔴 **다음 회차 1순위.** 이번 사고 546만원 중 대부분이 「금요일 15:50 알림
        1건」으로 회피 가능했다. `scripts/force_flat_guard.py` 를 확장하지 말고
        **그 앞단에 신설**할 것(리포트 G-2 변경대상 칸).
      · 검증: 08-28 15:50 리플레이로 `LONG 4계약` 탐지 + 최근 20거래일 오탐 0.
- [ ] **G-1** `position_recon_shadow` — 매분 「엔진 포지션 vs 브로커 잔고 캐시」 대조.
      · **캐시를 쓴다 — TR 추가 호출 0회.** 차단 없음. 섀도 4주 후 승격 판단.
      · ⚠ F-4와 같은 한계를 공유한다(캐시가 틀리면 못 잡는다) — 그래도 **갈라짐이
        발생한 분**을 잡는 것이 목적이라 가치가 다르다. 승격 시 그 한계를 명기할 것.
- [ ] **G-3** `entry_gate_stuck_shadow` — 차단 사유별 연속 지속시간 매분 누적,
      개장 후 30분 이상이면 경보 등급 상향. `_entry_block_reason` 이 이미 사유
      문자열을 만든다 = **새 계산 0회.** F-6 ⓒ항과 묶어서 구현할 것.
- [ ] **G-6** `selfinduced_cb_shadow` — CB 발동 직전 60초에 `ConstOut` 재적합 /
      `retrain_intraday` 완료 / 모델 pkl mtime 갱신 / `HealthPolicy cause=S0` 중
      하나가 있으면 `selfinduced=1` 태그. `predictions.db` 컬럼 1개. **CB 동작 무변경.**
      · CLAUDE.md 456차가 세운 「자가유발은 전환기준 ②의 근거로 쓰지 말 것」 규율을
        사람이 매번 손으로 하는 것을 없앤다. 4주 뒤 자동 제외 승격 판단.

### 제5부 수익률 방안 이월

- [ ] **P5-06** 분할체결 손절을 손절률 분모에서 되찾는다 — **관찰은 오늘 시작됐다**
      (G-5). 판정식: G-5 「미대응」이 10거래일 중 3일 이상에서 1건 이상 → F-10 승인.
- [ ] **P5-07** `net_breakeven_pt`(= 왕복수수료 ÷ (계약수 × 50,000)) 를 청산 시점에
      `predictions.db` 에 적재. **계측만 — 임계 변경 제안 없음.** 섀도 15거래일,
      `min_samples=20 且 min_days=10` 도달 시 사전등록 판정식 적용.
      · F-11이 승패 축을 이미 갈라 두었으므로 그 위에 얹으면 된다.
- [ ] **P5-08** 자가유발 CB 발동을 진입공백 비용으로 환산 — G-6 선행.

### 정비

- [ ] `tests/test_500_*.py` 5개 파일이 pytest 수집 시 `SystemExit: 0` 을 낸다
      (단독 실행 스크립트라 모듈 끝에서 `sys.exit(0)`). 전체 스위트를 돌릴 때마다
      `--ignore` 5개를 붙여야 한다. `if __name__ == "__main__":` 로 감싸거나
      `tests/scripts/` 로 옮길 것. **검사 내용 자체는 정상 통과한다.**
- [ ] 선행 실패 3건 정리 — `test_483_git_lock_guard[fuoption]`(형제 프로젝트 사본
      불일치, 08-26부터) · `test_504_pnl_history_creon_tab` 2건(504차 커밋).

### 2026-09-01 (MW0601 509차 — 장전 점검) 등록/이월

- [x] **O-t2(08-31 이월)** Restart Armistice 재현 여부 — **판정: 재현 안 됨**(2026-09-01
      08:41:08 `armistice cleared`). ⚠ 단 오늘은 실제 이월 포지션이 없는 케이스라
      F-6의 핵심 분기(blank-as-flat 오판)는 미검증 — 실제 이월 포지션 재시작 케이스를
      만나면 재검증 필요.
- [ ] **O-p1(신규)** `[HealthPolicy] Degraded 선제차단`(09:01:00, cause=S5 1207ms)이
      실제 진입을 막았는지 `ensemble_decisions`로 대조 — 장중 판정.
- [ ] **O-p2(신규)** `[ConfFloorGuard]` 자동진입 하한 도달 불가(09:00:01) 상태의
      `state=OK` 복귀 시각 확인 — 장중 판정.
- [ ] **O-t1·O-t3·O-t4·P-1·P-2(08-31 이월, 계속)** — 정의된 조건대로 장중·장후 판정 대기.
- [ ] CB② 복원 여부 — 재검토 기한 2026-08-29 경과, 계속 미결(3일째). 절대원칙 §2/전환기준 ⑤.
- [ ] 주간회의 안건 3건(승률 정의·F-15 외부진입 손익·F-13 이식) — 계속 미결.

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

### `data/heartbeat_MW0601_20260901.json` — 244B · 09-01 12:27:14
```json
{
 "pid": 17924,
 "written_at": "2026-09-01T12:27:44",
 "beat_epoch": 1788233262.8601487,
 "beat_age_sec": 1.8,
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

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 88개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 10.7KB | 09-01 09:05 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_pre.md` | 49.8KB | 09-01 09:01 |
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 203.4KB | 08-31 18:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_post.md` | 79.5KB | 08-31 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_intra.md` | 65.5KB | 08-31 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` | 57.8KB | 08-31 09:00 |
| `docs/정기점검/매일점검/MW0601-20260831-8월손실일-딥다이브.md` | 22.2KB | 08-31 00:18 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.2KB | 08-31 00:05 |

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

1. `logs/20260901_WARN.log`: ERROR 이상 18건
2. `logs/20260901_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
3. `logs/20260901_SYSTEM.log`: 매분 루프 커버리지 209/371분 (56.3%) — 루프가 빠진 구간이 있다
4. `logs/20260901_SYSTEM.log`: 12:29~15:10 **연속 162분 매분 루프 기록 없음**
5. `logs/20260901_HEALTH.log`: ERROR 이상 18건
6. 메인 스레드 정지 5초 초과 **1건** (최대 6250ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260901_WARN.log`: **degraded=ON** 8건(표본)
8. `logs/20260901_WARN.log`: **level=CRITICAL** 1건(표본)
9. `logs/20260901_WARN.log`: **ConstOut** 3건(표본)
10. `logs/20260901_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260901_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260901_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260901_LEARNING.log`: **축퇴** 8건(표본)
14. `logs/20260901_HEALTH.log`: **degraded=ON** 8건(표본)
15. `logs/20260901_HEALTH.log`: **level=CRITICAL** 1건(표본)
16. 미커밋 변경 515건 (실질 2건 · 코드 0건 · EOL 파생 511건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260901*.log` (Windows) / `grep 강제청산 logs/*20260901*.log`*