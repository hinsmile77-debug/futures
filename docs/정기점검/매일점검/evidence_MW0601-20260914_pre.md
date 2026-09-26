# 미륵이 증거 다이제스트 — 2026-09-14 / PRE

- 생성 2026-09-14 09:00:26 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/festive-blissful-bohr/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260914` · `2026-09-14` · `260914` · `0914`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260914.log` | 124B | 09-14 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260914.log` | 140B | 09-14 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260914.json` | 243B | 09-14 09:00 |
| `launcher_{DATE}_084001_18182.log` | 1 | `logs/Mireuk_batch/launcher_20260914_084001_18182.log` | 53.7KB | 09-14 09:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260914_DATA.log` | 1.1KB | 09-14 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260914_DEBUG.log` | 625B | 09-14 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260914_HEALTH.log` | 142B | 09-14 09:00 |
| `{DATE}_HOGA.log` | 1 | `logs/20260914_HOGA.log` | 1.7MB | 09-14 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260914_LEARNING.log` | 56.9KB | 09-14 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260914_MICRO.log` | 39.0KB | 09-14 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260914_PROBE.log` | 1.7KB | 09-14 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260914_SIGNAL.log` | 15.6KB | 09-14 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260914_SYSTEM.log` | 29.3KB | 09-14 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260914_TRADE.log` | 167B | 09-14 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260914_WARN.log` | 3.3KB | 09-14 09:00 |

## 2. 코드·커밋 상태

- HEAD `f179140` · 브랜치 `v9-dev` · 미커밋 606건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
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
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/settings.py
 M config/strategy_params.py
… 외 566건
```

**당일(2026-09-14) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
f179140 [MW0601] 559차 후속2: NEXT_TODO 등록 검사를 브랜치 무관하게
2310df1 [MW0601] 559차 후속: 다음 거래일 「결함 3건 정상 수집」 점검기 + NEXT_TODO 보강
857c71d [MW0601] 559차: 데이터 결함 3건 — 상태 판정 + P0·P1·P1' 구현 (매매 정책 무변경)
9d79eef [MW0601] 558차 후속: 리포트 제8부 커밋 해시 기입
c80f09c [MW0601] 558차 후속: 09-11 점검 산출물 일괄 커밋 + 리포트 제8부(장후 자동조치)
84d4ba7 [MW0601] 558차 후속: 장후 자동조치 — G-3(556-6) 재기동 대사 원장
ac042a0 [MW0601] 556차 후속: 장후 자동조치 기록 — 리포트 제4부 + dev_memory + 09-09·09-10 점검 산출물
5f8e40e [MW0601] 556차 후속: 장후 자동조치 — F-5(Armistice 고착 오탐)·G-4(래치 스냅샷)·G-1(상태파일 회전)
da66651 [MW0601] 555차 후속2: 출처축(P0)·차트 Y축(P1)·라벨 레지스트리(P2) + GP 마커 재지정
106f6e2 [MW0601] 555차 병합: GP 청산 패널 갱신 트리거 + 출처축 화이트리스트
c08128f [MW0601] 555차 후속: 손익 추이 「출처」축을 화이트리스트로 뒤집음 — 모르는 라벨은 auto 가 아니다
c91d591 [MW0601] 555차: GP 가상 청산이 손익 추이 패널을 갱신하지 않던 결함 — run_shadow 반환값 신설
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

_본문 미열람(설정): `20260914_HOGA.log` 1.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/13개 (중요도순). 제외: `20260914_PROBE.log`, `launcher_20260914_084001_18182.log`, `20260914_DEBUG.log`, `freeze_sentinel_20260914.log`, `force_flat_guard_20260914.log`_

### `logs/20260914_TRADE.log` — 167B · 2행 · 최종 08:41:06

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-14 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-14 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-14 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260914_WARN.log` — 3.3KB · 20행 · 최종 09:00:03

- 형식 평문 · 시각 인식 20행 · WARNING=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-14 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-14 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-09-14 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-14 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-14 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0
2026-09-14 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1164ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-14 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1164ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-14 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4735ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4735 band=INFO since_pipe_s=0.1
2026-09-14 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=0.0
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 11 | 08:41:09 | 09:01:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:10 | 08:41:10 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-09-11 → 2026-09-14)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1164ms | S0=3ms S1=15ms S2=0ms S3=0ms S4=95ms S5=650ms S6=381ms S7=15ms S8=5ms |
| `CB⑤` | 2 | 09:00:01 | 09:00:01 | 파이프라인 1164ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0 |

**채널** — `SYSTEM`×19, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×11, `출처축`×2, `SessionStateDrop`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1

### `logs/20260914_SYSTEM.log` — 29.3KB · 250행 · 최종 09:00:17

- 형식 평문 · 시각 인식 243행 · INFO=243, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:40:34 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.7MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-09-14 08:40:34 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=1000 | 행감지=30s all_threads=True
2026-09-14 08:40:50 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-14 08:40:50 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-14 08:40:50 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-14 09:01:28 [INFO] SYSTEM: [OptionChain][Worker] 완료 1746ms | target=24 valid=24 PCR=0.916 ATM_PCR=1.636 GEX=12.87B
2026-09-14 09:01:30 [INFO] SYSTEM: [TickUI] alive ticks=4475 code=A056A close=1045.50
2026-09-14 09:01:31 [INFO] SYSTEM: [CybosRT-TICK] #4500 code=A056A raw_time=90131 parsed=09:01:31 price=1045.00 vol=1 bid1=1045.00 ask1=1045.06 flag=50 side=SELL anchor=0/1
2026-09-14 09:01:34 [INFO] SYSTEM: [CybosRT-TICK] #4600 code=A056A raw_time=90134 parsed=09:01:34 price=1045.06 vol=1 bid1=1045.02 ask1=1045.18 flag=50 side=SELL anchor=0/1
2026-09-14 09:01:41 [INFO] SYSTEM: [CybosRT-TICK] #4700 code=A056A raw_time=90141 parsed=09:01:41 price=1045.52 vol=2 bid1=1045.40 ask1=1045.52 flag=49 side=BUY anchor=2/0
```

</details>

**채널** — `SYSTEM`×243

**컴포넌트 상위 15** — `CybosRT-TICK`×52, `CybosSub`×21, `System`×18, `TickUI`×17, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `LEVELS 08:50`×4

### `logs/20260914_SIGNAL.log` — 15.6KB · 168행 · 최종 09:00:04

- 형식 평문 · 시각 인식 168행 · WARNING=121, INFO=47

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.405
  …
2026-09-14 09:01:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_nasdaq_chg' scale=0.0612 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-14 09:01:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.0631 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-14 09:01:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0654 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-14 09:01:01 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1129 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-14 09:01:01 [INFO] SIGNAL: [ScalerRefresh] ts=09:00 trigger=D_FORCE feat=va_bandwidth repeat=2회 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 72 | 09:00:01 | 09:01:01 | 1m 'macro_vix' scale=0.0329 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 24 | 08:45:09 | 08:48:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0217) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:00:00 | 09:01:00 | ts=08:59 horizon=1m age=1m max_z=-12.76(institution_futures_net) extreme=2 adj=2 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×168

**컴포넌트 상위 15** — `ScalerFloor`×84, `ScalerRefresh`×31, `Model`×18, `ScalerMonitor`×12, `DynMC`×7, `SIGNAL`×4, `TimeRouter`×3, `ZeroDiag`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1

### `logs/20260914_LEARNING.log` — 56.9KB · 325행 · 최종 09:00:01

- 형식 평문 · 시각 인식 325행 · WARNING=157, INFO=168

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:40:51 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.454 out_max=0.2000 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00155 auc=0.431 out_max=0.4132 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3206 < conf_floor=0.3300 (span=0.00102 auc=0.686 out_max=0.3206, 기저율=0.3200 n=100) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-14 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00022 auc=0.517 out_max=0.2563 (기준 auc<0.53 and span<0.020, 기저율=0.2562 n=160) → 보정 미적용, raw 통과
  …
2026-09-14 09:00:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-14 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1046.88 cur_p=1046.00
2026-09-14 09:01:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=42.8% 예측=UP 실제=DN)
2026-09-14 09:01:00 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
2026-09-14 09:01:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 157 | 08:40:52 | 08:41:00 | 축퇴 감지 — span=0.00013 auc=0.454 out_max=0.2000 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×325

**컴포넌트 상위 15** — `Calibration`×306, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Consolidator`×2, `sigma`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `LEARNING`×1, `SGD`×1

### `logs/20260914_HEALTH.log` — 142B · 2행 · 최종 09:00:01

- 형식 평문 · 시각 인식 2행 · WARNING=1, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0
2026-09-14 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=481ms | quality=0.86 | cache_age=102s | exceptions_10m=0
  …
2026-09-14 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0
2026-09-14 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=481ms | quality=0.86 | cache_age=102s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1164ms | quality=0.86 | cache_age=43s | exceptions_10m=0 |

**채널** — `HEALTH`×2

**컴포넌트 상위 15** — `Health`×2

### `logs/20260914_MICRO.log` — 39.0KB · 120행 · 최종 09:00:18

- 형식 평문 · 시각 인식 120행 · DEBUG=120

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1057.02/1 ask1=1057.42/2 mp={'microprice_tick': 1057.1534, 'midprice_tick': 1057.22, 'depth_bias_tick': 0.1278} mlofi_tick=None queue=None
2026-09-14 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1057.00/6 ask1=1057.40/2 mp={'microprice_tick': 1057.3, 'midprice_tick': 1057.2, 'depth_bias_tick': 0.3641} mlofi_tick=-9.15 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 5.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -1.7…
2026-09-14 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1056.90/2 ask1=1057.40/2 mp={'microprice_tick': 1057.15, 'midprice_tick': 1057.15, 'depth_bias_tick': 0.0} mlofi_tick=-8.1167 queue={'depletion_bid': 4.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1.6…
2026-09-14 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1056.88/2 ask1=1057.22/3 mp={'microprice_tick': 1057.016, 'midprice_tick': 1057.05, 'depth_bias_tick': -0.103} mlofi_tick=-8.0667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio':…
2026-09-14 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1056.84/1 ask1=1057.22/3 mp={'microprice_tick': 1056.935, 'midprice_tick': 1057.03, 'depth_bias_tick': -0.2567} mlofi_tick=-3.4833 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
  …
2026-09-14 09:01:15 [DEBUG] MICRO: [MICRO-TICK] #8000 bid1=1045.74/2 ask1=1045.96/2 mp={'microprice_tick': 1045.85, 'midprice_tick': 1045.85, 'depth_bias_tick': -0.1053} mlofi_tick=-4.15 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-14 09:01:24 [DEBUG] MICRO: [MICRO-TICK] #8100 bid1=1046.14/1 ask1=1046.24/1 mp={'microprice_tick': 1046.19, 'midprice_tick': 1046.19, 'depth_bias_tick': -0.052} mlofi_tick=-0.1 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-14 09:01:31 [DEBUG] MICRO: [MICRO-TICK] #8200 bid1=1045.00/4 ask1=1045.06/2 mp={'microprice_tick': 1045.04, 'midprice_tick': 1045.03, 'depth_bias_tick': 0.1248} mlofi_tick=-4.0 queue={'depletion_bid': 4.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-14 09:01:35 [DEBUG] MICRO: [MICRO-TICK] #8300 bid1=1045.02/1 ask1=1045.16/1 mp={'microprice_tick': 1045.09, 'midprice_tick': 1045.09, 'depth_bias_tick': 0.0994} mlofi_tick=-3.85 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-14 09:01:41 [DEBUG] MICRO: [MICRO-TICK] #8400 bid1=1045.30/1 ask1=1045.46/2 mp={'microprice_tick': 1045.3534, 'midprice_tick': 1045.38, 'depth_bias_tick': -0.2539} mlofi_tick=7.9 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
```

</details>

**채널** — `MICRO`×120

**컴포넌트 상위 15** — `MICRO-TICK`×104, `MICRO-MINUTE`×16

### `logs/20260914_DATA.log` — 1.1KB · 6행 · 최종 09:00:00

- 형식 평문 · 시각 인식 6행 · INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-14 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=129047 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-14 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-14 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=129086 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-14 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-14 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-14 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-14 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=129086 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-14 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-14 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-14 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×6

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×2

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

### 메인 스레드 블로킹 3건 · 최대 4735ms · 5초 초과 0건

상위 — 4735ms, 3157ms, 2297ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260914_WARN.log`
```
--- 메인 스레드 블로킹 ×3(표본)
08:41:12 2026-09-14 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
09:00:03 2026-09-14 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4735ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4735 band=INFO since_pipe_s=0.1
09:01:01 2026-09-14 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2297 band=INFO since_pipe_s=0.0
```

### `logs/20260914_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-14 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20260914_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-14 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.401
08:40:31 2026-09-14 08:40:31 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.397
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

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260914_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 13 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 7 | 09:00:01 [WARNING] total=1164ms | S0=3ms S1=15ms S2=0ms S3=0ms S4=95ms S5=650ms S6=381ms S7=15ms S8=5ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 7 | 09:00:01 [WARNING] total=1164ms | S0=3ms S1=15ms S2=0ms S3=0ms S4=95ms S5=650ms S6=381ms S7=15ms S8=5ms |

- 이 로그 생존구간: 08:41 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260914_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 94 | 08:40:34 [INFO] 로테이션 — 8.7MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:02 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 97 | 08:54:00 [INFO] code=A056A from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260914_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 50 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0217) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 111 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 110 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 09:01

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
| **오늘 20260914** | **09:01** | 로그 본문 |

- 델타 **-399분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.9MB · 마지막 갱신 2026-09-13 14:46

최근 헤딩 8개:
```
### 증상
### 원인
### 결정
### Why
### 구현 중 잡은 결함 (내 코드)
### How to apply
### 검증
### 병행 세션
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
에 실패하지
   않았다(제3부 1-3 이 `--shortstat` 결과를 정상 인용). 재현 없는 상태에서 건드리지 않는다.

### Why

- **계측 4원칙 ⑤(대사는 모든 축을 걸어라)** — G-3 원문이 요구한 것은
  *"몇 번 재기동했고 **그중** 몇 번 불일치가 있었는지"* 다. MISMATCH 행만 쌓으면
  **분자만 남고 분모가 없어** 그 비율을 영영 못 낸다. 그래서 정상 종결도 적는다.
  `broker_sync_recon_counts()` 의 분모는 **대조가 성립한 건수**(match+mismatch)이며,
  UNVERIFIED 를 분모에 넣으면 「대조를 못 한 날」이 비율을 좋아 보이게 만든다.
- **계측 4원칙 ②(미측정 ≠ 0)** — 대조 불성립을 MATCH 로 적으면 "오늘 이상 없음"으로
  **위장**된다. FP-CRITICAL 이 PSI=0.0 으로 2개월, TOX 섀도가 한 달 넘게 죽어 있던
  것과 같은 계열이다. 표본 0일 때 비율은 `0.0` 이 아니라 **`None`** 을 돌려준다.
- **계측 4원칙 ①(단위 명시)** — 브로커 잔고 수량은 청산 레그가 아니라 포지션 단위다
  → 컬럼명 `broker_qty_per_position`.
- **관측이 판단을 오염시키지 않는다** — 기록 실패는 두 겹(`record_*` 내부 +
  `_ts_record_broker_sync_recon` 래퍼)으로 삼킨다. 여기는 **재기동 경로 한복판**이라
  DB 잠금 하나로 브로커 동기화가 깨지면 안 된다.

### 구현 중 잡은 결함 (내 코드)

`utils/db_utils.py` 에는 모듈 레벨 `logger` 가 **없다**(관례는
`logging.getLogger("SYSTEM")`). 초판이 `except` 안에서 `logger.warning` 을 불러
**예외를 삼키는 코드가 스스로 `NameError` 를 냈다** — 재기동 경로에서 터질 뻔했다.
새 테스트가 잡았고 3곳 전부 교정.

> 🔵 **부수 발견(미조치·등록만)**: 같은 파일에 **선행 결함 3건**이 동일 형태로 존재한다
> (`db_utils.py` GP 패널 2곳·MA-cont 1곳의 `except` 안 `logger.debug`). 전부 예외
> 처리 경로라 평소엔 드러나지 않는다. 오늘 범위 밖 → `NEXT_TODO` 558-2.

### How to apply

- 다음 기동부터 `data/db/trades.db: broker_sync_recon` 에 행이 쌓인다.
  집계: `python -c "from utils.db_utils import broker_sync_recon_counts as c; print(c(30))"`
- 불일치 **경보**는 종전처럼 518차 ERROR 가 낸다. 이 원장은 그 사건을 **세는** 역할만 한다.
- F-3(장중 주기 재대사)이 들어오면 이 원장이 그 전후 빈도 비교의 기준선이 된다.

### 검증

- 신규 `tests/test_558_broker_sync_recon.py` **11건 통과** — 스키마 · 3분류 구분 ·
  분모 노출 · 표본 0 → `None` · 모르는 outcome 격리 · 기록 실패 무시 ·
  **「라이브 반영 0」 불변식 4종**(반환값 미소비 / 래퍼 전량 예외 삼킴 /
  종결 분기 전수 계측 / `strategy`·`model` 이 원장을 참조하지 않음).
- `tests/test_498_recon_log_inventory.py` 가 **미등록 대사 로그로 실패했다** — 이
  프로젝트가 계측 4원칙 ⑤를 강제하는 정적 장치다. `BrokerSyncRecon` 을 3칸
  (compares / independent / missing_literal) 채워 등록 → 14건 통과.
- 기존 스위트: `main.py`·`db_utils` 참조 **86파일 3배치 → 948통과 · 7실패.**
  7건 전부 기존 실패 — 5건은 556-8 대장 등록분, 2건(`test_504_pnl_history_creon_tab`)은
  **변경 전량을 HEAD 로 되돌려 동일 실패 재현**을 확인해 기존으로 판정(556-8 에 추가).
  `test_500_cvd_ofi_live_defects` 는 수집 단계 `SystemExit`(기존, 556-7).

### 병행 세션

없음. 당일 커밋 0건(인덱스락으로 물리적 불가) 상태에서 시작했고, 작업 시작 시각
(17:26) 기준 미륵이 python 프로세스 0개. 종료 시 `.git/index.lock` 부재 재확인.
읽기 전용 git 은 전량 `--no-optional-locks`. `git add .` 미사용(경로 명시).

산출물: `main.py`·`utils/db_utils.py`·`tests/test_498_recon_log_inventory.py`(수정),
`tests/test_558_broker_sync_recon.py`(신규),
`docs/정기점검/매일점검/MW0601-20260911-점검리포트.md` 제8부 append.

```

</details>

### dev_memory/NEXT_TODO.md — 1.5MB · 마지막 갱신 2026-09-13 18:22

최근 헤딩 8개:
```
## 2026-09-10 (MW0601 556차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖)
### 다음 세션 관측
## 2026-09-11 (MW0601 557차 — 장전 점검)
## 2026-09-11 (MW0601 557차 후속 — 장중 점검)
## 2026-09-11 (MW0601 558차 후속 — 장후 자동조치)
### 이월·승인 대기 (자동조치 범위 밖 — 변경 없음)
### 다음 세션 관측
```

미완료 체크박스 **2613건** (끝에서 30건)
```
- [ ] 🔴 **556-4 (신규 · C등급)** `data/ui_prefs.json:state_persist_enabled = False`
- [ ] **556-5 (기록 결손)** `DECISION_LOG.md` 에 **555차·556차 본문 항목이 없다.**
- [ ] **556-6 (G-3 이월 · A등급)** 재기동 시 엔진↔브로커 상태 불일치 발견 이벤트를
- [ ] **556-7 (테스트 인프라)** `pytest tests/` 전체 실행이 **수집 단계에서**
- [ ] **556-8 (기존 실패 8건 대장)** 아래는 HEAD 에서도 동일하게 실패하는 **기존**
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
6·531-3은 기존 승인 대기 상태 유지
      (재상정 안 함, 함정 ① 준수).


## 2026-09-11 (MW0601 558차 후속 — 장후 자동조치)

- [x] **556-6 (G-3 이월) [DONE 2026-09-11]** 재기동 시 엔진↔브로커 대사 결과를
      누적 기록 — `broker_sync_recon` 테이블(TRADES_DB) + `record_broker_sync_recon()`
      + `broker_sync_recon_counts()`. `_ts_sync_position_from_broker()` 종결 분기
      **7곳 전부** 계측. `MATCH`/`MISMATCH`/`UNVERIFIED` 3분류 —
      **MISMATCH 만 적으면 분모가 없다**(계측 4원칙 ⑤). 대조 불성립은
      `reconciled_measured=0` + 그 자리 WARNING(계측 4원칙 ②).
      라이브 반영 0 불변식 4종. `tests/test_558_broker_sync_recon.py` 11건.
- [x] **558-1 [DONE 2026-09-11]** `.git/index.lock`(09:02, STALE 8.4시간) 회수 완료.
      낮 세션들이 못 지운 것은 **리눅스 샌드박스 마운트의 `unlink` EPERM** 때문이며
      futures 결함이 아니다 — 윈도우 네이티브 세션에서는 `--reclaim` 이 그대로 통한다.
      ⇒ 같은 상황이 또 나오면 **장후 자동조치 세션이 회수한다**(사용자 조치 불필요).
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

### `data/heartbeat_MW0601_20260914.json` — 243B · 09-14 09:00:10
```json
{
 "pid": 1000,
 "written_at": "2026-09-14T09:01:40",
 "beat_epoch": 1789344099.7926462,
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

- 파일 최종 기록: **09-14 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-14)과 일치 |
|---|---|---|
| `date` | 2026-09-14 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 131개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260911-점검리포트.md` | 70.1KB | 09-11 17:37 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_post.md` | 73.1KB | 09-11 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_intra.md` | 61.2KB | 09-11 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260911_pre.md` | 53.7KB | 09-11 09:02 |
| `docs/정기점검/매일점검/MW0601-20260910-점검리포트.md` | 103.5KB | 09-10 18:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_post.md` | 84.6KB | 09-10 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_intra.md` | 69.2KB | 09-10 12:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20260910_pre.md` | 56.9KB | 09-10 09:01 |

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

1. `logs/20260914_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 606건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260914*.log` (Windows) / `grep 강제청산 logs/*20260914*.log`*