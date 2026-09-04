# 미륵이 증거 다이제스트 — 2026-09-04 / PRE

- 생성 2026-09-04 09:00:48 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/jolly-epic-bohr/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260904` · `2026-09-04` · `260904` · `0904`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260904.log` | 125B | 09-04 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260904.log` | 140B | 09-04 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260904.json` | 244B | 09-04 09:00 |
| `launcher_{DATE}_084000_14769.log` | 1 | `logs/Mireuk_batch/launcher_20260904_084000_14769.log` | 57.7KB | 09-04 09:00 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260904_BACKFILL.log` | 0B | 09-04 07:57 |
| `{DATE}_DATA.log` | 1 | `logs/20260904_DATA.log` | 1.1KB | 09-04 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260904_DEBUG.log` | 623B | 09-04 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260904_HEALTH.log` | 142B | 09-04 09:00 |
| `{DATE}_HOGA.log` | 1 | `logs/20260904_HOGA.log` | 1.4MB | 09-04 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260904_LEARNING.log` | 53.7KB | 09-04 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260904_MICRO.log` | 35.8KB | 09-04 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260904_PROBE.log` | 1.7KB | 09-04 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260904_SIGNAL.log` | 22.7KB | 09-04 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260904_SYSTEM.log` | 27.1KB | 09-04 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260904_TRADE.log` | 76B | 09-04 08:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260904_WARN.log` | 2.0KB | 09-04 09:00 |

## 2. 코드·커밋 상태

- HEAD `9738080` · 브랜치 `v9-dev` · 미커밋 516건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 516건 (추적변경 516 · 미추적 0 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
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
… 외 476건
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

_본문 미열람(설정): `20260904_HOGA.log` 1.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/13개 (중요도순). 제외: `20260904_PROBE.log`, `launcher_20260904_084000_14769.log`, `20260904_DEBUG.log`, `freeze_sentinel_20260904.log`, `force_flat_guard_20260904.log`_

### `logs/20260904_TRADE.log` — 76B · 1행 · 최종 08:40:46

- 형식 평문 · 시각 인식 1행 · INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-04 08:40:46 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×1

**컴포넌트 상위 15** — `ProfitGuard`×1

### `logs/20260904_WARN.log` — 2.0KB · 16행 · 최종 09:00:01

- 형식 평문 · 시각 인식 16행 · WARNING=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-04 08:40:48 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-09-04 08:40:50 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
2026-09-04 08:40:50 [WARNING] SYSTEM: [LiveDBG] _apply update_learning 15ms
  …
2026-09-04 09:00:01 [WARNING] SYSTEM: [PipePerf] total=1082ms | S0=4ms S1=9ms S2=0ms S3=0ms S4=56ms S5=309ms S6=688ms S7=13ms S8=4ms
2026-09-04 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0
2026-09-04 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1082ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-04 09:00:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 1082ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-04 09:00:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2281 band=INFO since_pipe_s=0.1
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 9 | 08:40:48 | 09:00:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Canary` | 2 | 08:55:19 | 08:55:19 | scaler 노후=0h  z경고피처=18개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1082ms | S0=4ms S1=9ms S2=0ms S3=0ms S4=56ms S5=309ms S6=688ms S7=13ms S8=4ms |
| `CB⑤` | 2 | 09:00:01 | 09:00:01 | 파이프라인 1082ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0 |

**채널** — `SYSTEM`×15, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×9, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `Health`×1

### `logs/20260904_SYSTEM.log` — 27.1KB · 231행 · 최종 09:00:48

- 형식 평문 · 시각 인식 224행 · INFO=224, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:30 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=11496 | 행감지=30s all_threads=True
2026-09-04 08:40:31 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-04 08:40:31 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-04 08:40:31 [INFO] SYSTEM: 미륵이 초기화
2026-09-04 08:40:31 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-03) 종가 버퍼 로드: 384봉
  …
2026-09-04 09:01:17 [INFO] SYSTEM: [CybosRT-TICK] #3100 code=A0569 raw_time=90117 parsed=09:01:17 price=1047.08 vol=1 bid1=1047.08 ask1=1047.22 flag=50 side=SELL anchor=0/1
2026-09-04 09:01:23 [INFO] SYSTEM: [CybosRT-TICK] #3200 code=A0569 raw_time=90123 parsed=09:01:23 price=1048.06 vol=1 bid1=1048.10 ask1=1048.16 flag=50 side=SELL anchor=0/1
2026-09-04 09:01:30 [INFO] SYSTEM: [CybosRT-TICK] #3300 code=A0569 raw_time=90130 parsed=09:01:30 price=1049.00 vol=1 bid1=1048.82 ask1=1049.00 flag=49 side=BUY anchor=1/0
2026-09-04 09:01:34 [INFO] SYSTEM: [CybosRT-TICK] #3400 code=A0569 raw_time=90134 parsed=09:01:34 price=1049.20 vol=1 bid1=1049.10 ask1=1049.26 flag=49 side=BUY anchor=1/0
2026-09-04 09:01:39 [INFO] SYSTEM: [CybosRT-TICK] #3500 code=A0569 raw_time=90139 parsed=09:01:39 price=1050.00 vol=1 bid1=1049.90 ask1=1050.02 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×224

**컴포넌트 상위 15** — `CybosRT-TICK`×40, `CybosSub`×21, `System`×18, `TickUI`×16, `CybosRT-ROLLOVER`×16, `BAR-CLOSE`×16, `CVD-ANCHOR`×16, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `EarlyWarmup`×3

### `logs/20260904_SIGNAL.log` — 22.7KB · 185행 · 최종 09:00:13

- 형식 평문 · 시각 인식 185행 · WARNING=103, INFO=82

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
  …
2026-09-04 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=10m age=1m max_z=+4.27(quality_investor_reason_code) extreme=1 adj=0
2026-09-04 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=15m age=1m max_z=+4.27(quality_investor_reason_code) extreme=1 adj=0
2026-09-04 09:01:00 [WARNING] SIGNAL: [ScalerMonitor] ts=09:00 horizon=30m age=1m max_z=+4.27(quality_investor_reason_code) extreme=1 adj=0
2026-09-04 09:01:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=0.0% grade=X micro=혼합
2026-09-04 09:01:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.000<mc0.423) | 참고: 이상값피처(quality_investor_reason_code(candidate))
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 54 | 08:45:18 | 09:00:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0293) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 24 | 09:00:00 | 09:00:01 | 1m 'macro_vix' scale=0.0206 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 12 | 09:00:00 | 09:01:00 | ts=08:59 horizon=1m age=1m max_z=+4.90(toxicity_flow_stress) extreme=2 adj=2 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4230 (conf_floor=0.330, min_conf=0.423, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×185

**컴포넌트 상위 15** — `ScalerFloor`×72, `ScalerRefresh`×61, `Model`×18, `ScalerMonitor`×12, `DynMC`×7, `SIGNAL`×4, `TimeRouter`×3, `ZeroDiag`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1

### `logs/20260904_LEARNING.log` — 53.7KB · 309행 · 최종 09:00:00

- 형식 평문 · 시각 인식 309행 · WARNING=147, INFO=162

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:40:33 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2630 < conf_floor=0.3300 (span=0.00096 auc=0.546 out_max=0.2630, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00019 auc=0.521 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-04 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00109 auc=0.539 out_max=0.4351 (n=145) → 보정 재적용
  …
2026-09-04 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1046.10
2026-09-04 09:00:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-09-04 09:01:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=1 nonzero=1 prev_p=1046.10 cur_p=1048.12
2026-09-04 09:01:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=36.0% 예측=DN 실제=UP)
2026-09-04 09:01:01 [INFO] LEARNING: [SGD] 1건 학습 | SGD비중=30% 50분정확도=50.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 147 | 08:40:33 | 08:40:42 | 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×309

**컴포넌트 상위 15** — `Calibration`×290, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Consolidator`×2, `sigma`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `LEARNING`×1, `SGD`×1

### `logs/20260904_HEALTH.log` — 142B · 2행 · 최종 09:00:01

- 형식 평문 · 시각 인식 2행 · WARNING=1, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0
2026-09-04 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=653ms | quality=0.86 | cache_age=124s | exceptions_10m=0
  …
2026-09-04 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0
2026-09-04 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=653ms | quality=0.86 | cache_age=124s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1082ms | quality=0.86 | cache_age=64s | exceptions_10m=0 |

**채널** — `HEALTH`×2

**컴포넌트 상위 15** — `Health`×2

### `logs/20260904_MICRO.log` — 35.8KB · 107행 · 최종 09:00:45

- 형식 평문 · 시각 인식 107행 · DEBUG=107

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:45:19 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1044.64/6 ask1=1045.34/1 mp={'microprice_tick': 1045.24, 'midprice_tick': 1044.99, 'depth_bias_tick': 0.3159} mlofi_tick=None queue=None
2026-09-04 08:45:19 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1044.64/7 ask1=1045.64/1 mp={'microprice_tick': 1045.515, 'midprice_tick': 1045.14, 'depth_bias_tick': 0.3635} mlofi_tick=4.9167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-04 08:45:19 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1045.10/2 ask1=1045.64/1 mp={'microprice_tick': 1045.46, 'midprice_tick': 1045.37, 'depth_bias_tick': -0.0599} mlofi_tick=3.5333 queue={'depletion_bid': 5.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-04 08:45:19 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1045.10/2 ask1=1045.64/1 mp={'microprice_tick': 1045.46, 'midprice_tick': 1045.37, 'depth_bias_tick': 0.0591} mlofi_tick=1.65 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-04 08:45:19 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1045.10/2 ask1=1045.66/2 mp={'microprice_tick': 1045.38, 'midprice_tick': 1045.38, 'depth_bias_tick': -0.041} mlofi_tick=3.9833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -…
  …
2026-09-04 09:01:18 [DEBUG] MICRO: [MICRO-TICK] #6700 bid1=1047.26/1 ask1=1047.38/1 mp={'microprice_tick': 1047.32, 'midprice_tick': 1047.32, 'depth_bias_tick': 0.2808} mlofi_tick=4.0667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-09-04 09:01:23 [DEBUG] MICRO: [MICRO-TICK] #6800 bid1=1048.14/1 ask1=1048.28/1 mp={'microprice_tick': 1048.21, 'midprice_tick': 1048.21, 'depth_bias_tick': 0.0} mlofi_tick=-0.7833 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-04 09:01:29 [DEBUG] MICRO: [MICRO-TICK] #6900 bid1=1048.72/1 ask1=1048.84/1 mp={'microprice_tick': 1048.78, 'midprice_tick': 1048.78, 'depth_bias_tick': 0.0} mlofi_tick=-2.4833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-04 09:01:34 [DEBUG] MICRO: [MICRO-TICK] #7000 bid1=1049.00/3 ask1=1049.10/1 mp={'microprice_tick': 1049.075, 'midprice_tick': 1049.05, 'depth_bias_tick': 0.3075} mlofi_tick=-6.6 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 2.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-04 09:01:39 [DEBUG] MICRO: [MICRO-TICK] #7100 bid1=1049.94/1 ask1=1050.06/1 mp={'microprice_tick': 1050.0, 'midprice_tick': 1050.0, 'depth_bias_tick': -0.1135} mlofi_tick=2.7333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
```

</details>

**채널** — `MICRO`×107

**컴포넌트 상위 15** — `MICRO-TICK`×91, `MICRO-MINUTE`×16

### `logs/20260904_DATA.log` — 1.1KB · 6행 · 최종 09:00:00

- 형식 평문 · 시각 인식 6행 · INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-04 08:58:21 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149230 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-04 08:58:21 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-04 08:58:52 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149233 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-04 08:58:52 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-04 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-04 08:58:21 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-04 08:58:52 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=149233 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-04 08:58:52 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-04 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
2026-09-04 09:01:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
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

### 메인 스레드 블로킹 1건 · 최대 2281ms · 5초 초과 0건

상위 — 2281ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260904_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
09:00:01 2026-09-04 09:00:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2281 band=INFO since_pipe_s=0.1
```

### `logs/20260904_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-04 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
```

### `logs/20260904_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-04 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4230 (conf_floor=0.330, min_conf=0.423, span=0.0063, auc=0.550). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:28 2026-09-04 08:40:28 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
```

### `logs/20260904_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00652 auc=0.102 out_max=0.2407 (기준 auc<0.53 and span<0.020, 기저율=0.2375 n=80) → 보정 미적용, raw 통과
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2630 < conf_floor=0.3300 (span=0.00096 auc=0.546 out_max=0.2630, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:33 2026-09-04 08:40:33 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00019 auc=0.521 out_max=0.4223 (기준 auc<0.53 and span<0.020, 기저율=0.4222 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:33 2026-09-04 08:40:33 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00109 auc=0.539 out_max=0.4351 (n=145) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260904_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 1 | 08:40:46 [INFO] 설정 업데이트 완료 |

- 이 로그 생존구간: 08:40 ~ 08:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260904_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 8 | 08:40:48 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 08:55:19 [WARNING] scaler 노후=0h  z경고피처=18개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 08:55:19 [WARNING] scaler 노후=0h  z경고피처=18개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260904_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 90 | 08:40:30 [INFO] 활성화 | file=logs\crash_fault.log PID=11496 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 122 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 93 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:01

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260904_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:18 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0293) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 123 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0254) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 116 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0272) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:01

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
| **오늘 20260904** | **09:01** | 로그 본문 |

- 델타 **-399분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 1. 피처 — 무엇을, 왜
### 2. 최적안 — 두 장치는 고치지 않는다 (실측이 반대)
## 2026-09-04 (MW0601 529차 후속 — 레그 위치 채널 3종 + 판정기 구현: 사전등록만, 매매 동작 0)
### 1. 채널 A `leg_exhaustion_entry_watch` (P5-14)
### 2. 채널 C `streak_leg_end_watch` (P5-15) · 완화 유지 확정
### 3. 채널 E `leg_entry_early_watch` (P5-16) — 관측 전용
### 4. 확정 결정 `core_vwap_directional_requirement` — 3_vwap 무변경 (D)
### 5. 판정기·검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
ist=`dist_to_high_60m_atr`).
- 합격선(사전등록·고정): `min_samples=40` 且 `min_days=25` · 일자 부호검정 p<0.05 · drop-worst-3 부호 유지 ·
  **`require_early_group_better`**(레그 초입군 평균 > 처리군 평균).
- **거울상 보존 조건이 이 채널의 고유 안전장치다** — 처리군을 누르는 조치가 초입 승리군(소급 70건 +888,515,
  승률 69%)까지 누르면 순이익이 사라진다. 소급에서 초입군이 이미 우세하므로 조건은 살아 있다.
- 승격 형태를 **판정 전에 확정**(B): `promotion_order=["checklist_demote","size_half"]`,
  `hard_block_forbidden=True`. 1순위는 체크리스트 `12_leg_position` 감점(10_chase 동형), 2순위 사이저 ×0.5.
  🔴 하드차단 금지 — 317차 FalseBlock + 처리군 승률 51%(09-03 C3가 그 절반, 같은 위치 +160,424).
- **첫 판정 INSUFFICIENT** — 처리군 47건/**17거래일** < min_days 25. 소급 −1,254,231원(대조군 +2,410,899),
  사이즈½ 가정 +616,394, 일자 9/8 p=1.00.
- ⚠ 컷(5.0/1.0)은 관측 전 고정. 소급에서 `run≥8·dist≤1.5`가 더 좋아 보였으나(11/5 p=0.21) 채택하면 313차 ④ 위반.

### 2. 채널 C `streak_leg_end_watch` (P5-15) · 완화 유지 확정
- 묻는 것은 완화가 아니라 **결합**이다. `min_samples=20` 且 `min_days=10`, 승격은
  `skip_relax_when_leg_end`(결합일 때만 완화 미적용 — 원래 문턱 복귀, 하드차단 아님).
- **첫 판정 NO_CHANGE** — 처리군 34건/16일 −264,823(59%) vs 대조군 54건 +1,064,943(69%), 일자 6/7 **p=1.00**.
- ⚠ **모집단 원천이 로그뿐이다** — TrendGate 활성 상태가 DB에 없다(`ensemble_decisions` trend/streak 컬럼 0,
  `gate_signals`에도 없음). `[TrendGate] … ON/OFF` 전이 파싱으로 재구성하므로 `LOG_KEEP_DAYS`가 표본 상한이다.
- 확정 결정 `trend_gate_relax_keep`: 완화 **유지**. 실제 인하 547회 중 `0.62→0.44` 333회 — 주 효과가 점심
  진입금지 창 개방이고, 완화 없이는 불가했던 5건이 **5승 +279,000원**. streak ON 통산 +800,120원.

### 3. 채널 E `leg_entry_early_watch` (P5-16) — 관측 전용
- 초입(`run ≤ 2.0 ATR`) 13건/10일 **+319,726원**(승률 77%) vs 나머지 166건 +836,942(61%).
- **판정문·승격 경로 없음**(`observe_only=True`) — 가점은 진입을 늘리는 방향이라 faststop_discovery와 충돌.
  A의 거울상 판정 입력으로만 쓴다. 테스트가 `promotion_order` 부재를 강제한다.

### 4. 확정 결정 `core_vwap_directional_requirement` — 3_vwap 무변경 (D)
- "멀리 벗어날수록 잘 통과" 구조는 사실이나 손익은 반대다: 순방향 이탈 ≥1.5σ 44건 통산 −9,395(중립)인데
  **초입 15건 +675,319(12승3패)** / 레그 끝 16건 −96,093, 이탈이 작아도(0~1.5σ) 레그 끝이면 8건 −536,430.
  ⇒ 축은 이탈 크기가 아니라 **레그 위치**. 상한 감점은 최상위 승리군을 먼저 깎는다.
- CORE 방향 요구 자체는 절대원칙 §3이라 변경 대상 아님 — 논점은 "상한을 둘 것인가"였고 답은 위 실측.

### 5. 판정기·검증
- `scripts/leg_position_watch.py` — 값 원천 2단(배선 후 DB 스윙 키 / 이전 `raw_candles` 재계산 `replay_proxy`),
  겹치는 구간은 매 실행 `source_crosscheck`(473차 규약). 장중 가드·읽기전용. py37 안전(`math.comb` 미사용,
  `"{:,.0f}".format`).
- `tests/test_529_leg_position_watch.py` 8 tests + 스윙 피처 7 tests + 기존 채널 테스트 = **40 passed**.
  못박은 것: 합격선 settings 단일 원천 · 하드차단 금지 · 거울상 조건 존재 · 표본 게이트 · E 관측 전용 ·
  py37 부호검정 · 09-03 C1~C4 프록시 재현.
- 기동 안전성 확인: `config.settings`·`features.feature_builder`·`config.strategy_params`·캠페인 생성기 import OK.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-04 (MW0601 526차 후속 — F-A·P5-13·F-C 구현 완료, 사용자 승인)
### 남은 것
### 관측 예정
## 2026-09-04 (MW0601 527·528차 — 탈진 레짐 조사 · C1~C4 사전감지 조사) — 승인 대기
### 관측 예정
## 2026-09-04 (MW0601 529차 — 스윙 피처 착수 · 3_vwap×TrendGate 최적안)
## 2026-09-04 (MW0601 529차 후속 — 채널 3종 구현 완료)
### 남은 것
```

미완료 체크박스 **2419건** (끝에서 30건)
```
- [ ] **525-3 / P5-10 판정식 확정** `regime_override_volatile_watch`를 (a)진짜 변동성 / (b)z_warn 두 갈래로 —
- [ ] **525-4 (P2)** 349차 `VolatilityBurstGuard` 07-16 이후 0회 발동 — 임계(틱 600·atr_ratio 1.8) 산출 근거를
- [ ] **O-t8** 525-1 배선 후 첫 5거래일 급변장 근거 분포(`z_warn` 비중) — 81%가 재현되면 ③ 조건 처분을 주간회의 안건으로.
- [ ] **526-1 / F-A (A등급 후보 · 매매 동작 불변)** 급변장 라벨과 데이터이상 게이트 분리 —
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 반영할지. 거울상 유의(역행 진입 p=0.04 · CVD 역방향 p=0.00)가 계기. faststop_discovery(2026-08-03) 결정과 충돌 여부 먼저.

### 관측 예정
- [ ] **O-t10** CFCG "강등 후보" 뒤 진입 손익 누적(현 23건 −248,263) — 528-B 판정 표본.
- [ ] **O-t11** streak≥10 ON 분 순방향 진입(524차 O-t5 승계, 현 13건 avg −25,376) — 5건 이상 추가 시 집계.
## 2026-09-04 (MW0601 529차 — 스윙 피처 착수 · 3_vwap×TrendGate 최적안)

- [DONE 2026-09-04] **529-1** 스윙 위치 피처 7키(창 60) `feature_builder.py` 착수 — 기록 전용, 소비자 0, 7 tests passed. **재기동 후 적재.**
- [ ] **529-2 (P1 라이브 검증)** 첫 거래일: `raw_features`에 `swing_ready_60m` True 비율(개장 60분 후 ~100%) · `dist_to_*` 분포가 오프라인
      재현(179건 run p50 5.7 ATR)과 같은 자릿수인지 · `[FeatureBuilder] 스윙 피처 오류` 로그 0건.
- [ ] **529-A** 채널 `leg_exhaustion_entry_watch` 사전등록(승인 대기) — 모집단 순방향 진입 且 run≥5 ATR 且 극단≤1.0 ATR 且 ready.
      판정 `min_samples=40` 且 `min_days=25` 且 일자 p<0.05 且 drop-worst-3 且 초입군 비악화 → 소프트 승격 안건. 컷 고정(사후 변경 금지).
- [ ] **529-B** 승격 형태 사전 확정(감점 `12_leg_position` vs 사이저 ×0.5) — 판정 전에 채널 판정문에 박는다.
- [ ] **529-C** 채널 `streak_leg_end_watch` — TrendGate 완화 적용 분 且 레그 끝 진입(현 35건 −243k / 완화-필수 5건 5승) `min_samples=20`.
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

### `data/heartbeat_MW0601_20260904.json` — 244B · 09-04 09:00:20
```json
{
 "pid": 11496,
 "written_at": "2026-09-04T09:01:20",
 "beat_epoch": 1788480078.7718256,
 "beat_age_sec": 1.3,
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

- 파일 최종 기록: **09-04 08:46:00**

| 키 | 값 | 수집 대상일(2026-09-04)과 일치 |
|---|---|---|
| `date` | 2026-09-04 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 105개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md` | 85.0KB | 09-04 07:51 |
| `docs/정기점검/매일점검/MW0601-20260904-스윙피처도입과-3vwap-TrendGate-손익최적안.md` | 10.9KB | 09-04 07:38 |
| `docs/정기점검/매일점검/MW0601-20260904-탈진위치진입-C1C4-사전감지게이트-조사.md` | 17.4KB | 09-04 06:41 |
| `docs/정기점검/매일점검/MW0601-20260904-탈진레짐-보유현황과작동이력-조사.md` | 15.6KB | 09-04 06:23 |
| `docs/정기점검/매일점검/MW0601-20260903-급변장라벨fix-손익과제안-딥다이브.md` | 20.3KB | 09-04 05:50 |
| `docs/정기점검/매일점검/MW0601-20260903-급변장기준과차단손익-딥다이브.md` | 17.3KB | 09-03 22:54 |
| `docs/정기점검/매일점검/MW0601-20260903-지수흐름x진입청산-딥다이브.md` | 26.9KB | 09-03 22:14 |
| `docs/정기점검/매일점검/MW0601-20260903-지수흐름x진입청산.svg` | 67.1KB | 09-03 22:07 |

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

1. `logs/20260904_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260904*.log` (Windows) / `grep 강제청산 logs/*20260904*.log`*