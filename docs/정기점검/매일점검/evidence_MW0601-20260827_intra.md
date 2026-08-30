# 미륵이 증거 다이제스트 — 2026-08-27 / INTRA

- 생성 2026-08-27 12:26:45 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/compassionate-charming-gates/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260827` · `2026-08-27` · `260827` · `0827`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **18개** 파일 · 18개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260827.log` | 124B | 08-27 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260827.log` | 139B | 08-27 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260827.json` | 244B | 08-27 12:26 |
| `launcher_{DATE}_084001_18593.log` | 1 | `logs/Mireuk_batch/launcher_20260827_084001_18593.log` | 917.7KB | 08-27 12:26 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260827.log` | 21.7KB | 08-27 12:11 |
| `retrain_intraday_{DATE}_093700.log` | 1 | `logs/retrain_intraday_20260827_093700.log` | 2.4KB | 08-27 09:37 |
| `retrain_intraday_{DATE}_105101.log` | 1 | `logs/retrain_intraday_20260827_105101.log` | 2.4KB | 08-27 10:51 |
| `{DATE}_DATA.log` | 1 | `logs/20260827_DATA.log` | 182.2KB | 08-27 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260827_DEBUG.log` | 130.9KB | 08-27 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260827_HEALTH.log` | 2.7KB | 08-27 12:11 |
| `{DATE}_HOGA.log` | 1 | `logs/20260827_HOGA.log` | 29.4MB | 08-27 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260827_LEARNING.log` | 174.6KB | 08-27 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260827_MICRO.log` | 590.4KB | 08-27 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260827_PROBE.log` | 57.5KB | 08-27 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260827_SIGNAL.log` | 366.5KB | 08-27 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260827_SYSTEM.log` | 448.8KB | 08-27 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260827_TRADE.log` | 1.4KB | 08-27 09:37 |
| `{DATE}_WARN.log` | 1 | `logs/20260827_WARN.log` | 21.5KB | 08-27 12:26 |

## 2. 코드·커밋 상태

- HEAD `0814498` · 브랜치 `v9-dev` · 미커밋 517건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 511건 (추적변경 513 · 미추적 4 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
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
… 외 477건
```

**당일(2026-08-27) 커밋**
```
0814498 [MW0601] 497차 후속: 잔고 표시 축 정합이 2초마다 원상복구되던 버그 fix
```

**최근 커밋 12건**
```
0814498 [MW0601] 497차 후속: 잔고 표시 축 정합이 2초마다 원상복구되던 버그 fix
f5ae831 [MW0601] 498차 후속: 리포트 제8-7절 — 자동조치 커밋 해시·푸시 결과 기록
7afa4f7 [MW0601] 498차: 장후 자동조치 — F-10·F-8·F-9·F-2·F-12·F-11·F-3·G-6·방안5
9d664fa [MW0601] 494차 후속: F-AE·F-AF — 청산 마감 줄 포지션 합계 병기 + 승패 단위 섀도
74aaee6 [MW0601] 497차 체리픽: 손익 축 정합 P1·P2·P3 — commission_rate_used 기록 결함 fix 포함
5c54496 [MW0601] 495차 후속 체리픽: 수수료율을 로그인 채널 감지로 파생 — v9-dev는 CYBOS
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
a0fcee2 [MW0601] 493차 후속6: 사용자 조치 구현 8건 — F-Y·F-X·F-V·F-Z·F-AA·F-AB·F-P·F-Q
a7120ad [MW0601] 493차 후속5: 수수료율 6.54배 오차 fix — F-1~F-5 (F-AD ①~⑥ 구현)
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
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

_본문 미열람(설정): `20260827_HOGA.log` 29.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `20260827_MICRO.log`, `20260827_DATA.log`, `20260827_PROBE.log`, `launcher_20260827_084001_18593.log`, `20260827_DEBUG.log`, `mainstall_traceback_20260827.log`, `freeze_sentinel_20260827.log`, `force_flat_guard_20260827.log`_

### `logs/20260827_TRADE.log` — 1.4KB · 11행 · 최종 09:37:46

- 형식 평문 · 시각 인식 11행 · WARNING=1, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:57 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-27 08:41:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-27 09:35:39 [INFO] TRADE: [Chejan] 상태=접수 주문번호=1051 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-27 09:35:39 [INFO] TRADE: [Chejan] 상태=체결 주문번호=1051 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-27 09:35:39 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1093.18 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
  …
2026-08-27 09:35:39 [INFO] TRADE: [체결동기화] 외부진입 SHORT 1계약 @ 1093.18 | 평균=1093.18 보유=1계약
2026-08-27 09:37:46 [INFO] TRADE: [Chejan] 상태=접수 주문번호=1083 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-27 09:37:46 [INFO] TRADE: [Chejan] 상태=체결 주문번호=1083 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-27 09:37:46 [INFO] TRADE: [Position] 체결청산 SHORT @ 1091.32 | PnL=+1.86pt (+82,275원) | 미추적체결(pending_miss)
2026-08-27 09:37:46 [INFO] TRADE: [청산 완료] PnL=+1.86pt (+82,275원) | 포지션 합계 +82,275원 (레그 1)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 1 | 09:35:39 | 09:35:39 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1093.18 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×11

**컴포넌트 상위 15** — `Chejan`×4, `Position`×3, `ProfitGuard`×1, `PositionFallback`×1, `체결동기화`×1, `청산 완료`×1

### `logs/20260827_WARN.log` — 21.5KB · 140행 · 최종 12:26:01

- 형식 평문 · 시각 인식 140행 · CRITICAL=1, WARNING=139

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-27 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-27 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-08-27 08:41:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2922 band=INFO since_pipe_s=NA
2026-08-27 08:41:11 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3593ms — live 중단 원인 분석용
  …
2026-08-27 12:11:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5000ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5000 band=WARN since_pipe_s=0.0
2026-08-27 12:11:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (7/20) → logs/mainstall_traceback_20260827.log
2026-08-27 12:21:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2296ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2296 band=INFO since_pipe_s=0.0
2026-08-27 12:26:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
2026-08-27 12:26:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1047ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 10:27:08 | 10:27:08 | level=CRITICAL degraded=OFF | latency=6690ms | quality=1.00 | cache_age=105s | exceptions_10m=0 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-08-27 10:27:08 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6690ms | quality=1.00 | cache_age=105s | exceptions_10m=0
```

</details>

**WARNING — 태그 16종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 62 | 08:41:05 | 12:21:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 10 | 09:00:03 | 12:08:02 | total=3188ms | S0=4ms S1=10ms S2=0ms S3=0ms S4=101ms S5=2553ms S6=423ms S7=41ms S8=57ms |
| `Health` | 9 | 09:00:03 | 12:10:01 | level=WARNING degraded=OFF | latency=3188ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |
| `MainStallTrace` | 9 | 09:00:08 | 12:11:04 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260827.log |
| `CB⑤` | 8 | 09:00:03 | 12:08:11 | 파이프라인 3188ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 8 | 09:14:00 | 11:53:00 | 5분 누적 수익률 -0.423% (임계 ±0.382%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `HealthPolicy` | 5 | 09:01:01 | 12:09:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=3188ms quality=0.86 cache=0s exc10m=0) | cause=S5(2553ms) |
| `Brier` | 5 | 11:20:00 | 11:24:00 | 과신 경고 | 이동평균=0.351 > 0.35 |
| `ChejanFlow` | 4 | 09:35:39 | 09:37:46 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=1093.18 | fill_qty=1 | gubun='0' | order_no='1051' | pending='NONE' | position='FLAT' | position_qty=0 | sell_balance=0 | side='SHORT' … |
| `ChejanMatch` | 4 | 09:35:39 | 09:37:46 | order_no='1051' | pending='NONE' | pending_matched=False |
| `OrderSync` | 4 | 09:35:39 | 09:37:47 | 미추적 체결 감지 (pending_miss) order_no=1051 side=SHORT qty=1 price=1093.18 before=FLAT |
| `ConstOut` | 3 | 09:36:00 | 12:26:00 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

**채널** — `SYSTEM`×130, `HEALTH`×10

**컴포넌트 상위 15** — `LiveDBG`×62, `PipePerf`×10, `Health`×10, `MainStallTrace`×9, `CB⑤`×8, `ScalerRefresh`×8, `HealthPolicy`×5, `Brier`×5, `ChejanFlow`×4, `ChejanMatch`×4, `OrderSync`×4, `ConstOut`×3, `Canary`×2, `ExitCooldown`×2, `CB`×2

### `logs/20260827_SYSTEM.log` — 448.8KB · 3289행 · 최종 12:26:25

- 형식 평문 · 시각 인식 3278행 · INFO=3278, PLAIN=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:33 [INFO] SYSTEM: [FaultHandler] 로테이션 — 9.3MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-08-27 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18600 | 행감지=30s all_threads=True
2026-08-27 08:40:47 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-27 08:40:47 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-27 08:40:47 [INFO] SYSTEM: 미륵이 초기화
  …
2026-08-27 12:27:01 [INFO] SYSTEM: [PipePerf][DBG] [GBM재학습중] total=732ms | S0=88ms S1=37ms S2=116ms S3=0ms S4=175ms S5=254ms S6=44ms S7=16ms S8=3ms
2026-08-27 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+289,foreign:+3524,institution:-3886}
2026-08-27 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+289,foreign:+3524,institution:-3886}
2026-08-27 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+89380 nonarb=+160486
2026-08-27 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+89380 nonarb=+160486
```

</details>

**채널** — `SYSTEM`×3278

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×780, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `System`×59, `MicroRegime`×44, `RegimeFingerprint`×37, `IntradayRegime`×28, `OptionChain`×22, `CybosSub`×21, `BalanceUI`×16

### `logs/20260827_SIGNAL.log` — 366.5KB · 3201행 · 최종 12:26:02

- 형식 평문 · 시각 인식 3201행 · WARNING=1427, INFO=1774

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.450
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.437
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.424
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.433
2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.428
  …
2026-08-27 12:27:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['10m', '15m', '5m'] 중 미배포=['10m', '15m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=None)
2026-08-27 12:27:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
2026-08-27 12:27:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=85.0% grade=X micro=횡보장
2026-08-27 12:27:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
2026-08-27 12:27:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1032 | 09:00:03 | 12:26:02 | 1m 'macro_vix' scale=0.0087 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 108 | 09:00:00 | 12:12:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 91 | 09:08:00 | 12:23:01 | 신뢰도 미달 34.9% < 40.7% → 강제 X등급 |
| `ScalerMonitor` | 78 | 09:00:00 | 12:12:00 | ts=08:59 horizon=1m age=1m max_z=-4.29(prev_day_same_hour_ret) extreme=1 |
| `ScalerRefresh` | 60 | 08:45:05 | 08:59:03 | 1m CORE 'cvd_divergence' raw_std≈0(0.0176) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 45 | 09:07:00 | 12:27:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `MetaGate` | 6 | 09:08:00 | 10:29:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |
| `PCR-Dampen` | 3 | 09:27:00 | 09:40:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConstOut` | 3 | 09:35:00 | 12:26:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:02 | 09:00:02 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4500 (conf_floor=0.330, min_conf=0.450, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3201

**컴포넌트 상위 15** — `ScalerFloor`×1092, `SIGNAL`×416, `MetaGate`×284, `Ensemble`×213, `ZeroDiag`×208, `FQAdj`×205, `Model`×126, `Checklist`×91, `ScalerRefresh`×90, `ATR-Horizon`×83, `ScalerMonitor`×78, `차단`×51, `ToxicityGate`×50, `WeightCollapse`×45, `MicroRegime`×44

### `logs/20260827_LEARNING.log` — 174.6KB · 1643행 · 최종 12:26:02

- 형식 평문 · 시각 인식 1643행 · WARNING=139, INFO=1504

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00112 auc=0.370 out_max=0.3754 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00143 auc=0.428 out_max=0.4882 (기준 auc<0.53 and span<0.020, 기저율=0.4875 n=80) → 보정 미적용, raw 통과
2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.530 out_max=0.3826 (기준 auc<0.53 and span<0.020, 기저율=0.3826 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-27 08:40:49 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00144 auc=0.542 out_max=0.3169 (n=155) → 보정 재적용
  …
2026-08-27 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0695% buf_n=20 nonzero=20 prev_p=1096.16 cur_p=1095.80
2026-08-27 12:27:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=33.3% 예측=UP 실제=DN)
2026-08-27 12:27:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=33.3% 예측=UP 실제=DN)
2026-08-27 12:27:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=41.4% DN)
2026-08-27 12:27:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=12.5%
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 138 | 08:40:49 | 12:04:01 | 축퇴 감지 — span=0.00112 auc=0.370 out_max=0.3754 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 1 | 10:27:02 | 10:27:02 | total=542ms raw_fetch=120ms pred_select=19ms pred_update=7ms pred_insert=336ms verified=3 |

**채널** — `LEARNING`×1643

**컴포넌트 상위 15** — `LEARNING`×667, `Calibration`×270, `SGD`×208, `sigma`×195, `Bias⚠`×94, `Bias`×82, `MetaConf`×41, `ScalerWarmup`×30, `OnlineLearner`×25, `SHAP`×7, `BiasReset`×6, `GBM-64`×5, `GBM`×4, `RF`×3, `ExtremityCorrector`×2

### `logs/20260827_HEALTH.log` — 2.7KB · 20행 · 최종 12:11:00

- 형식 평문 · 시각 인식 20행 · CRITICAL=1, WARNING=9, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 09:00:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3188ms | quality=0.86 | cache_age=44s | exceptions_10m=0
2026-08-27 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=808ms | quality=0.86 | cache_age=102s | exceptions_10m=0
2026-08-27 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 292ms (표본 20분)
2026-08-27 09:30:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=413ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-27 09:31:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=243ms | quality=1.00 | cache_age=56s | exceptions_10m=0
  …
2026-08-27 11:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=327ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-27 12:08:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2140ms | quality=1.00 | cache_age=62s | exceptions_10m=0
2026-08-27 12:09:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=548ms | quality=1.00 | cache_age=122s | exceptions_10m=1
2026-08-27 12:10:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=370ms | quality=1.00 | cache_age=181s | exceptions_10m=1
2026-08-27 12:11:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=286ms | quality=1.00 | cache_age=56s | exceptions_10m=1
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 10:27:08 | 10:27:08 | level=CRITICAL degraded=OFF | latency=6690ms | quality=1.00 | cache_age=105s | exceptions_10m=0 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-08-27 10:27:08 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6690ms | quality=1.00 | cache_age=105s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:03 | 12:10:01 | level=WARNING degraded=OFF | latency=3188ms | quality=0.86 | cache_age=44s | exceptions_10m=0 |

**채널** — `HEALTH`×20

**컴포넌트 상위 15** — `Health`×19, `HealthTrend`×1

### `logs/retrain_intraday_20260827_093700.log` — 2.4KB · 20행 · 최종 09:37:22

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 09:37:00,751 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-27 09:37:00,751 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-27 09:37:00,752 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-27 09:37:00,752 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_6d5d7abc.json
2026-08-27 09:37:03,766 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-27 09:37:22,829 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=1.00s | old_acc=0.4174)
2026-08-27 09:37:22,946 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-27 09:37:22,946 [INFO] LEARNING: [Retrain] 완료 | 19.2초 | 성공=1/1 호라이즌
2026-08-27 09:37:22,947 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.2s 데이터=4800행
2026-08-27 09:37:22,948 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_6d5d7abc.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260827_105101.log` — 2.4KB · 20행 · 최종 10:51:23

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-27 10:51:01,132 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-27 10:51:01,132 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-27 10:51:01,132 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-27 10:51:01,132 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b7902aec.json
2026-08-27 10:51:04,403 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-27 10:51:23,846 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.93s | old_acc=0.4174)
2026-08-27 10:51:23,929 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-27 10:51:23,929 [INFO] LEARNING: [Retrain] 완료 | 19.5초 | 성공=1/1 호라이즌
2026-08-27 10:51:23,930 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.8s 데이터=4800행
2026-08-27 10:51:23,931 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_b7902aec.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 51 |
| 사이저 호출(`[Sizer]`) | 0 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|

**청산 레그 0행** (부분청산 0 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 +82,275 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 1건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패 레그 1행 ⚠**(진입 로그 없는 이월 포지션 가능)

### 차단 사유 51건 · 27종

| 건수 | 사유 |
|---|---|
| 25 | 등급X — 미통과 항목: 2_confidence |
| 1 | 청산 후 쿨다운 — 103초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 46초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.5pt > ATR×5.0=11.8pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.9pt > ATR×5.0=12.0pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.6pt > ATR×5.0=12.4pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.8pt > ATR×5.0=12.0pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.3pt > ATR×5.0=11.8pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.0pt > ATR×5.0=12.1pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.9pt > ATR×5.0=11.9pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.9pt > ATR×5.0=12.4pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 24.3pt > ATR×5.0=12.3pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 26.5pt > ATR×5.0=12.6pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 25.5pt > ATR×5.0=12.5pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.5pt > ATR×5.0=13.0pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.2pt > ATR×5.0=13.2pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.0pt > ATR×5.0=12.7pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.2pt > ATR×5.0=12.2pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 26.0pt > ATR×5.0=13.7pt (시가=1106.32 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 26.4pt > ATR×5.0=13.1pt (시가=1106.32 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×25

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 4건

- `5분 진입 정지 | 파이프라인 6690ms — 처리 지연 (임계=5000ms)` ×2
- `일시 정지 해제 — 정상 복귀` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 34건 · 최대 12500ms · 5초 초과 9건

상위 — 12500ms, 9797ms, 9500ms, 5562ms, 5390ms, 5047ms, 5015ms, 5000ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 9500ms | 3188ms | **6312ms (66%)** |
| 09:05:04 | 5047ms | 306ms | **4741ms (94%)** |
| 10:27:10 | 9797ms | 6690ms | **3107ms (32%)** |
| 10:27:36 | 5000ms | 6690ms | **-1690ms (-34%)** |
| 10:28:05 | 5562ms | 6690ms | **-1128ms (-20%)** |
| 11:21:05 | 5390ms | 380ms | **5010ms (93%)** |
| 11:31:05 | 5015ms | 365ms | **4650ms (93%)** |
| 12:08:12 | 12500ms | 2140ms | **10360ms (83%)** |
| 12:11:04 | 5000ms | 370ms | **4630ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260827_WARN.log`
```
--- ConstOut ×3(표본)
09:36:00 2026-08-27 09:36:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:50:00 2026-08-27 10:50:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:26:00 2026-08-27 12:26:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×7(표본)
09:00:08 2026-08-27 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260827.log
09:05:04 2026-08-27 09:05:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260827.log
10:27:10 2026-08-27 10:27:10 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260827.log
11:21:05 2026-08-27 11:21:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260827.log
--- [Brier] 과신 ×5(표본)
11:20:00 2026-08-27 11:20:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.351 > 0.35
11:21:00 2026-08-27 11:21:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.356 > 0.35
11:22:00 2026-08-27 11:22:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.362 > 0.35
11:23:02 2026-08-27 11:23:02 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.369 > 0.35
--- [CB] ×2(표본)
10:27:09 2026-08-27 10:27:09 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 6690ms — 처리 지연 (임계=5000ms)
10:27:09 2026-08-27 10:27:09 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 6690ms — 처리 지연 (임계=5000ms)
--- [ExitCooldown] ×2(표본)
09:37:46 2026-08-27 09:37:46 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:39:46)
09:37:46 2026-08-27 09:37:46 [WARNING] SYSTEM: [ExitCooldown] 미추적체결(pending_miss) 후 2분 재진입 금지 (until 09:39:46)
--- [SHAP] 슬로우 ×2(표본)
12:08:02 2026-08-27 12:08:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 936ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:26:01 2026-08-27 12:26:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1047ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- level=CRITICAL ×1(표본)
10:27:08 2026-08-27 10:27:08 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6690ms | quality=1.00 | cache_age=105s | exceptions_10m=0
--- 메인 스레드 블로킹 ×8(표본)
08:41:08 2026-08-27 08:41:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2922 band=INFO since_pipe_s=NA
09:00:08 2026-08-27 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 9500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9500 band=WARN since_pipe_s=0.1
09:01:02 2026-08-27 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3250 band=INFO since_pipe_s=0.1
09:05:04 2026-08-27 09:05:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5047 band=WARN since_pipe_s=0.0
```

### `logs/20260827_SYSTEM.log`
```
--- CIRCUIT ×2(표본)
10:27:09 2026-08-27 10:27:09 [INFO] SYSTEM: [Notify] 🚨 [10:27:09] [미륵이] Circuit Breaker 발동!
10:27:09 2026-08-27 10:27:09 [INFO] SYSTEM: [Notify] 🚨 [10:27:09] [미륵이] Circuit Breaker 발동!
--- ConstOut ×8(표본)
09:36:00 2026-08-27 09:36:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:38:00 (const_output)
09:36:00 2026-08-27 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:00 2026-08-27 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=90ms fit=68ms total=161ms
09:37:00 2026-08-27 09:37:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-08-27 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.077 level=0 (heartbeat)
09:05:00 2026-08-27 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.077 level=0 (heartbeat)
09:10:00 2026-08-27 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.077 level=0 (heartbeat)
09:16:00 2026-08-27 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.077 level=0 (heartbeat)
--- [CB] ×2(표본)
10:33:00 2026-08-27 10:33:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
10:33:00 2026-08-27 10:33:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
```

### `logs/20260827_SIGNAL.log`
```
--- CIRCUIT ×1(표본)
10:32:00 2026-08-27 10:32:00 [INFO] SIGNAL: [차단] Circuit Breaker PAUSED — 진입 불가 (CB 해제까지 대기)
--- ConfFloorGuard ×1(표본)
09:00:02 2026-08-27 09:00:02 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4500 (conf_floor=0.330, min_conf=0.450, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-08-27 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-08-27 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-08-27 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:00 2026-08-27 09:37:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-08-27 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-08-27 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:13:01 2026-08-27 09:13:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-08-27 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.450
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.437
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.424
08:40:31 2026-08-27 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.433
--- 안전망 ×8(표본)
09:07:00 2026-08-27 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-27 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:01 2026-08-27 09:13:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-08-27 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260827_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00112 auc=0.370 out_max=0.3754 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:40:49 2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00143 auc=0.428 out_max=0.4882 (기준 auc<0.53 and span<0.020, 기저율=0.4875 n=80) → 보정 미적용, raw 통과
08:40:49 2026-08-27 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.530 out_max=0.3826 (기준 auc<0.53 and span<0.020, 기저율=0.3826 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:49 2026-08-27 08:40:49 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00144 auc=0.542 out_max=0.3169 (n=155) → 보정 재적용
```

### `logs/20260827_HEALTH.log`
```
--- level=CRITICAL ×1(표본)
10:27:08 2026-08-27 10:27:08 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=6690ms | quality=1.00 | cache_age=105s | exceptions_10m=0
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260827_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:57 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 09:37

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260827_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:05 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 11 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 13 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=14개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1 | 09:55:00 [WARNING] 5분 누적 수익률 -0.718% (임계 ±0.285%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 4 | 11:56:03 [WARNING] _tick_header 간격 3625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3625 band=… |

- 이 로그 생존구간: 08:41 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260827_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:33 [INFO] 로테이션 — 9.3MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 196 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 212 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 168 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260827_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:05 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0176) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 154 | 08:50:00 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 228 | 08:55:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0315) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 150 | 09:55:00 [WARNING] 1m 'macro_vix' scale=0.0079 → floor=0.10 적용 (z-score 폭발 방지) |
| 12:00 | 장중 중간점 | 130 | 11:54:00 [WARNING] 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260826 | 15:40 | 로그 본문 |
| 20260825 | 15:40 | 로그 본문 |
| 20260824 | 15:40 | 로그 본문 |
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260827** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 499-1-2. 관측 번호 국면 접두 규약이 도입 당일 충돌했다 (P2)
### 499-C-1. Canary / CanaryShadow z경고 기준선 불일치 (확인 필요 — 확정 결함 아님)
### 499-C-2. 설정 핫리로드 — 오늘 시도 0건 (조건 미도래)
### 499. 이월 처리 — 미처분 0건
### 499. 재보고하지 않은 것 — `ConfFloorGuard` (함정 ① 회피)
### 499. 정상 확인 (근거 있는 것만)
### 499. 관측 등록 (오늘 장중·장후가 판정)
### 499. 규약 준수 메모
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
다 —
오늘 기동분이 `BROKER_CHANNEL_SPECS` 를 정상 임포트했음이 다이제스트 §3
`FUTURES_COMMISSION_RATE = _BROKER_SPEC[...]` **`일치`** 로 간접 확인.
⚠ **시도 0건을 「성공」으로 적지 않는다**(계측 4원칙 ② — 미측정 ≠ 0). 장중 `O-p3`.

### 499. 이월 처리 — 미처분 0건

✅해소 3: 0826 제6부 `O-t1`(= 제8부 `O-p1`) 런처 단일 인스턴스 가드 —
`launcher_20260827_084001_18593.log` 24~25행 `[GUARD] 기존 main.py 프로세스 체크...`
→ `[GUARD] 기존 main.py 없음 -- 단일 인스턴스 확인.` **프로브 실재 + 허위 「종료 완료」 소멸** /
제8부 `O-p2` 비용 모델 4행 전부 `일치`.
⏭이월: `O-t5`(장중) · `O-t2`·`O-t3`·`O-t4`(장후) · `O-t6`(포지션 잔존일) ·
`O-t7`(표본 도달 시) · `O-t8`(08-28 주간점검) · `O-t9`·`O-t10`(09-02).
🔄지속: 이상점 1-4(점심 블랙아웃 무력) — 코드 변경 없음(F-4 보류).

### 499. 재보고하지 않은 것 — `ConfFloorGuard` (함정 ① 회피)

`09:00:02 [ConfFloorGuard] 자동진입 하한 도달 불가 — 출력상한 0.3479 < 필요 0.4500`.
**7거래일 연속 개장 첫 분 1건**(08-19 0.4190 / 08-20·21 0.3790 / 08-24 0.4310 /
08-25 0.4420 / 08-26 0.4550 / 08-27 0.4500) 이며 **어제 이미 반증됐다**
(0826 리포트 683행 — 자동진입 2건 실제 발생, 09:39:01·12:17:00 둘 다 등급 A).
래치 구조(`model/ensemble_decision.py:384` 상태 무변화 시 로그 억제 +
이후 분 대부분 `unmeasured:calibrator_unfitted`)상 **하루 1건 ≠ 하루 종일 차단**.
→ 신규 이상점으로 올리지 않고 관측 `O-p1` 로만 등록.

### 499. 정상 확인 (근거 있는 것만)

전일 EOD 재학습 **성공**(`data/eod_retrain_done_20260826.txt` — 15:48:52,
rows 40383 · cols 97 · **horizons_replaced 6/6** · daily_close_stalled false) →
CB③ HALT 유발 경로 없음 / `08:55:06 [PreRetrain] 스킵 — 1영업일 전 EOD 성공`
= **정상**(STEP 3 는 이벤트 구동. "30분마다"는 코드에 존재한 적 없다 — 483차) /
`[WarmupRetrain]` 예약 08:41 등록 → 08:55 소진 /
py37_32 32-bit 확인(mainstall traceback 프레임 경로) /
`[CybosSub] Dscbo1.CpFConclusion` 체결 구독 08:41:05 + `[EarlyWarmup]` 08:45:06 선행 구독 /
분봉은 `OPT50029`(키움 전용, Cybos 해당 없음) 대신 `[BAR-CLOSE][CYBOS]` **15봉** 자체 집계 /
`08:58:10 [Regime] NEUTRAL (점수=1) VIX=15.4 SP500=-0.02% USD/KRW +0.10%` /
설정 불변식 **25행 전부 일치** · 차단 게이트 33개 중 꺼진 9개 **전부 기록된 사안** ·
브랜치 밖 5건은 계측 4원칙 ③에 따라 제외 표기 /
장전 스케일러 3단계 완주(Phase1 20→7 · Phase2 7→4 · Phase3 8→4).

### 499. 관측 등록 (오늘 장중·장후가 판정)

`O-p1` 개장 첫 분 하한 경보 실효성(재발 여부 + 자동진입 발생 여부) ·
`O-p2` 점심 블랙아웃 진입 재현(발생 시 `O-t7` 표본 적립) ·
`O-p3` 설정 핫리로드 첫 성공(0건이면 **미도래**로 이월) ·
`O-p4` Canary/CanaryShadow 분모 일치 여부 ·
`O-p5` 개장 버스트 메인 정지 추이(오늘 09:00:08 **9,500ms**, 어제 최대 8,141ms·29건.
⚠ CB⑤와 **단위 상이** — 미발동이 정상) ·
`O-p6` `[NetRecon]` 대사 결과(`MISMATCH` 면 요율 축 1순위 의심).

### 499. 규약 준수 메모

- 코드 변경·커밋·배포·재기동 **없음**(개장 3분 전 예약).
- **라이브 DB 미조회** — `raw_data.db`·`predictions.db`·`trades.db` 쿼리 0건.
  수집기는 로그·설정·git 전용이라 안전(2026-08-10 CB⑤ 자가유발 전례 회피).
- 재인용 금지 수치 미사용(2026-06-25 SHAP=0 · 0801 §9-3 이벤트 단위 사이징 4종).
- 하루 한 파일 규약 준수 — `-pre` 접미사 파일 **미생성**.
- 세션 종료 시 `.git/index.lock` 없음.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 점검 규약 메모
### 커밋 대기 (오늘 커밋하지 않았다)
### MW0601 494차 정정 (2026-08-26 14:55)
### MW0601 494차 후속 (2026-08-26 15:10) — F-1′ 적용 완료
### MW0601 494차 후속2 (2026-08-26 15:30) — 커밋으로는 동기화가 안 된다 (실측 확정)
### MW0601 494차 후속3 (2026-08-26 16:40 — 장후 점검)
### 498차 — 장후 자동조치 (MW0601, 2026-08-26 17:30~19:0x · `mireuk-postmarket-autofix` 첫 실행)
### MW0601 499차 (2026-08-27 08:57~09:1x — 장전 점검)
```

미완료 체크박스 **2101건** (끝에서 30건)
```
- [ ] **498-1. 2026-08-26 당일치 `broker_net_krw` 소급 보정 여부 결정.**
- [ ] **498-2. 스킬 세 곳 중 두 곳은 사용자만 갱신할 수 있다** (F-11·F-12 반영분).
- [ ] **498-3. 형제 저장소 `fuoption` 의 `git_lock_guard.py` 사본이 정본과 갈라졌다.**
- [ ] **F-5 (P1, 장중 등록)** 장중 설정 편집 감지 경고. 우선순위 목록에 없어 제외.
- [ ] **F-6 (P2, 장중 등록)** 진단 문자열이 최종 문턱을 인용하게 한다.
- [ ] **F-7 (P2, 장중 등록)** 보고서 서브프로세스를 장중 밖으로 밀거나 비블로킹으로.
- [ ] **CB② 복원** — 재검토 기한 **2026-08-29**, 이번 금요일이 마지막 회차.
- [ ] **전환기준 ② ⓑ 선행조건에 F-10 을 못박기.** 동결 감시 오탐이 살아 있는 채로
- [ ] **비용 모델 이원화 종료** — 라이브 `9.8104e-05`(채널 파생) vs 검증 계측
- [ ] **G-7** 진입후보 시간의 변동성 정규화 — 하한 60분이 사전등록 값이라 판정식 변경은
- [ ] **F-4** 점심 블랙아웃 하드 게이트 승격 — `P5-04` 채널이 판정을 낼 때까지 보류.
- [ ] **P5-01~P5-04 는 전부 「313차 가드 미통과」** — 표본이 찰 때까지 구현 금지.
- [ ] **P5-05 검증** 2026-09-02(5거래일 뒤)까지 장후 세션이 대장을 갱신하는가.
- [ ] **F-1 (P1) 브로커 채널·요율 기동 로그 1줄.** `main.py` 기동 배너 직후
- [ ] **F-2 (C등급 — 주간회의) 런처 `MIREUK_BROKER_CHANNEL=CYBOS` 고정** (구 495-1).
- [ ] **F-3 (P2) `scripts/obs_number_lint.py` 신설.** 같은 `O-` 번호가 서로 다른
- [ ] **G-1 재발 경보 자동 표기.** 수집기 §6 인용 블록에
- [ ] **G-2 `data/env_probe_<date>.json`** — 기동 시 CREON·Daishin 스타터 로그
- [ ] **O-p1 (장중)** 개장 첫 분 하한 경보 실효성 — 재발 여부 + 자동진입 발생 여부 +
- [ ] **O-p2 (장중)** 11:50~13:00 `[차단] OTHER 구간` 중 진입 발생 여부 →
- [ ] **O-p3 (장중→장후)** `[HealthPolicy]` 핫리로드 **성공** 1건.
- [ ] **O-p4 (장후)** `Canary` vs `CanaryShadow` z경고 분모 일치 여부(3 vs 5).
- [ ] **O-p5 (장후)** 개장 버스트 메인 정지 추이 — 오늘 09:00:08 **9,500ms**
- [ ] **O-p6 (장후)** `[NetRecon]` 대사 결과. **`MISMATCH` 면 요율 축을 1순위로 의심**
- [ ] 🔴 **어제분 커밋이 아직 안 됐다** — 0826 리포트/증거/dev_memory 2종 +
- [ ] 🔴 **MW0602 에 `mireuk_skill_sync_20260826/` 두 파일 전달** (어제 이월, 미이행).
- [ ] 🔴 **자동조치 예약 프롬프트에 관측 번호 일련 규약 1줄 추가**
- [ ] 🔴 **CB② 복원 재검토 기한 2026-08-29** — 내일이 **기한 전 마지막 회차**.
- [ ] **비용 모델 이원화 종료** — 라이브 `9.8104e-05`(채널 파생) vs
- [ ] **F-2 (신규 상정)** 런처 채널 고정 — 위 Fix F-2 참조.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
CYBOS` 고정** (구 495-1).
      **F-1 배선 후 `source=` 를 며칠 실측한 뒤** 상정한다. 감지 결과를 사람이
      덮어쓰는 조치라, 판단이 틀린 날 오류가 영구화된다. 섀도 선행 원칙과 동일.
- [ ] **F-3 (P2) `scripts/obs_number_lint.py` 신설.** 같은 `O-` 번호가 서로 다른
      「무엇을 보면 닫히는가」로 2회 이상 정의되면 `rc=2`. 장후 세션이 자기 절을
      쓰기 **전에** 실행. `tests/` 에 `MW0601-20260826-점검리포트.md` 픽스처로
      **rc=2 양성** 회귀 고정(첫 양성 표본).

#### 고도화 (당일 관측 근거 있음)

- [ ] **G-1 재발 경보 자동 표기.** 수집기 §6 인용 블록에
      `[재발 N/M거래일 · 값 동일 · 최근 판정: <날짜> <처분>]` 병기.
      최근 판정은 `docs/정기점검/매일점검/*-점검리포트.md` 최근 10일치 역인용.
      근거: `ConfFloorGuard` **7/7거래일** 동값 재발을 이 세션이 grep 6회로 손판정했다.
      → 함정 ①(판정된 사안 재보고)을 기계가 1차 차단. DB 미접근이라 장중 안전.
- [ ] **G-2 `data/env_probe_<date>.json`** — 기동 시 CREON·Daishin 스타터 로그
      mtime 2종 기록, 수집기 §9에 적재. F-1 로그와 **원천이 달라 상호 대사**
      (계측 4원칙 ⑤). 파일 부재 시 `measured=false` 명시(②).
      근거: 이 세션이 `C:\CREON\`·`C:\Daishin\` 를 볼 수 없어 요율 1차 원천을
      **구조적으로 확인 불가**했다.

#### 관측 (오늘 장중·장후가 판정 — 미처분으로 남기지 말 것)

- [ ] **O-p1 (장중)** 개장 첫 분 하한 경보 실효성 — 재발 여부 + 자동진입 발생 여부 +
      해당 분 `conf_floor_state`. 반증되면 ✅ / 진입 0건이면 격상 검토.
- [ ] **O-p2 (장중)** 11:50~13:00 `[차단] OTHER 구간` 중 진입 발생 여부 →
      발생 시 포지션 단위 손익을 `O-t7` 표본에 적립.
- [ ] **O-p3 (장중→장후)** `[HealthPolicy]` 핫리로드 **성공** 1건.
      하루 종일 0건이면 **「미도래」로 이월**(성공으로 적지 말 것 — 계측 4원칙 ②).
- [ ] **O-p4 (장후)** `Canary` vs `CanaryShadow` z경고 분모 일치 여부(3 vs 5).
      다르면 "08:55 최종" 문구를 어느 기준으로 고칠지 확정.
- [ ] **O-p5 (장후)** 개장 버스트 메인 정지 추이 — 오늘 09:00:08 **9,500ms**
      (어제 최대 8,141ms · 총 29건). ⚠ CB⑤(파이프라인 경과시간)와 **단위 상이**,
      미발동이 정상. 482차 F-3 섀도 2주 관찰 구간.
- [ ] **O-p6 (장후)** `[NetRecon]` 대사 결과. **`MISMATCH` 면 요율 축을 1순위로 의심**
      (이상점 1-1). `일치` 면 오늘 채널이 CYBOS였다는 간접 증거.

#### 사용자 조치 (세션이 할 수 없는 것)

- [ ] 🔴 **어제분 커밋이 아직 안 됐다** — 0826 리포트/증거/dev_memory 2종 +
      오늘 0827 리포트/증거. **경로 명시 add**(`git add .` 금지 — 515건 중
      **실질 변경 0건 · EOL 파생 513건**).
- [ ] 🔴 **MW0602 에 `mireuk_skill_sync_20260826/` 두 파일 전달** (어제 이월, 미이행).
      브랜치가 갈라져 `git pull` 로 안 간다(함정 ③).
- [ ] 🔴 **자동조치 예약 프롬프트에 관측 번호 일련 규약 1줄 추가**
      (`C:\Users\82108\.claude\scheduled-tasks\mireuk-postmarket-autofix\SKILL.md`).
      저장소 밖 파일이라 세션 권한 밖. 미이행 시 499-1-2 재발.

#### 주간회의(2026-08-28) 상정 — 기한 임박

- [ ] 🔴 **CB② 복원 재검토 기한 2026-08-29** — 내일이 **기한 전 마지막 회차**.
      `CB_CONSEC_STOP_LIMIT` 9999 → 2~3. 미처리 시 전환기준 ②·⑤가 함께 잠긴다.
- [ ] **비용 모델 이원화 종료** — 라이브 `9.8104e-05`(채널 파생) vs
      `COST_MODEL_COMMISSION_RATE=0.000015`. 승인 시 `..._PINNED=False` +
      **수집기 불변식 기대값 동시 갱신**(498차 F-3 감시 대상).
- [ ] **F-2 (신규 상정)** 런처 채널 고정 — 위 Fix F-2 참조.

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

### `data/heartbeat_MW0601_20260827.json` — 244B · 08-27 12:26:42
```json
{
 "pid": 18600,
 "written_at": "2026-08-27T12:27:12",
 "beat_epoch": 1787801230.3313034,
 "beat_age_sec": 2.7,
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

### `docs/정기점검/매일점검` — 80개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260827-점검리포트.md` | 35.7KB | 08-27 09:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_pre.md` | 52.6KB | 08-27 09:00 |
| `docs/정기점검/매일점검/MW0601-20260826-점검리포트.md` | 225.1KB | 08-26 19:04 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_post.md` | 75.3KB | 08-26 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_intra.md` | 64.8KB | 08-26 12:27 |
| `docs/정기점검/매일점검/MW0601-20260826-청산로그갭-딥다이브.md` | 11.4KB | 08-26 11:58 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_pre.md` | 52.3KB | 08-26 09:00 |
| `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` | 301.3KB | 08-25 22:33 |

### `docs/정기점검/금요일점검` — 58개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.4KB | 08-24 15:09 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260821.md` | 4.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260821.json` | 2.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md` | 26.2KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json` | 34.4KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json` | 91.9KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260827_WARN.log`: ERROR 이상 1건
2. `logs/20260827_WARN.log`: **Traceback** 출현 7건 — 크래시/메모리 계열
3. `logs/20260827_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
4. `logs/20260827_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
5. `logs/20260827_HEALTH.log`: ERROR 이상 1건
6. 메인 스레드 정지 5초 초과 **9건** (최대 12500ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260827_WARN.log`: **[Brier] 과신** 5건(표본)
8. `logs/20260827_WARN.log`: **level=CRITICAL** 1건(표본)
9. `logs/20260827_WARN.log`: **ConstOut** 3건(표본)
10. `logs/20260827_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260827_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260827_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260827_LEARNING.log`: **축퇴** 8건(표본)
14. `logs/20260827_HEALTH.log`: **level=CRITICAL** 1건(표본)
15. 미커밋 변경 517건 (실질 2건 · 코드 0건 · EOL 파생 511건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260827*.log` (Windows) / `grep 강제청산 logs/*20260827*.log`*