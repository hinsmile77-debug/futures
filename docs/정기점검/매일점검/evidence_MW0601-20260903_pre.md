# 미륵이 증거 다이제스트 — 2026-09-03 / PRE

- 생성 2026-09-03 08:59:42 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/optimistic-blissful-turing/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260903` · `2026-09-03` · `260903` · `0903`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260903.log` | 125B | 09-03 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260903.log` | 140B | 09-03 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260903.json` | 245B | 09-03 08:59 |
| `launcher_{DATE}_084001_27535.log` | 1 | `logs/Mireuk_batch/launcher_20260903_084001_27535.log` | 41.7KB | 09-03 08:58 |
| `strategy_report_20260508_18{DATE}.txt` | 1 | `data/daily_reports/strategy_report_20260508_180903.txt` | 708B | 05-08 18:09 |
| `{DATE}_DATA.log` | 1 | `logs/20260903_DATA.log` | 914B | 09-03 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260903_DEBUG.log` | 0B | 09-03 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260903_HEALTH.log` | 0B | 09-03 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260903_HOGA.log` | 1.2MB | 09-03 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260903_LEARNING.log` | 51.9KB | 09-03 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260903_MICRO.log` | 33.3KB | 09-03 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260903_PROBE.log` | 1.7KB | 09-03 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260903_SIGNAL.log` | 11.3KB | 09-03 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260903_SYSTEM.log` | 24.9KB | 09-03 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260903_TRADE.log` | 167B | 09-03 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20260903_WARN.log` | 1.2KB | 09-03 08:41 |

## 2. 코드·커밋 상태

- HEAD `8997136` · 브랜치 `v9-dev` · 미커밋 515건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 515건 (추적변경 515 · 미추적 0 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .claude/skills/mireuk-daily-check/scripts/collect_evidence.py
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
… 외 475건
```

**당일(2026-09-03) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
8997136 [MW0601] 519차 기록: DECISION_LOG · NEXT_TODO · 리포트 제5부
d03b629 [MW0601] 519차: CB② 복원 · 메인스레드 정지 경보 · F-1 마감 잔여 자동청산 (사용자 지시)
7338611 [MW0601] 518차 후속: 장후 자동조치 — F-3(진입출처 라벨) · G-1(재기동 잔량 경보 문구) · G-4(이월손익 가시화)
a3f70ab [MW0601] 514차 후속: 장후 자동조치 — F-A(P1-3) · F-B(고도화①) · F-C(고도화②/P5-신규)
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
db48586 [MW0601] 507차 후속: 리포트 제8부에 커밋 해시 기입
2d6a1bb [MW0601] 507차 후속: 장후 자동조치 — F-7·F-8·F-11·F-12·F-14 + G-4·G-5
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
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

_본문 미열람(설정): `20260903_HOGA.log` 1.2MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_reports/strategy_report_20260508_180903.txt`** — 708B · 05-08 18:09:03
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-05-08 18:09
========================================================
  버전    : v1.2  (1일차)
  판정    : INSUFFICIENT
  롤링20일: 누적 +0원  Sh=0.00  MDD=0.0%
--------------------------------------------------------
  CUSUM   : CRITICAL (1618766.50)
  PSI     : 0.000 (CLEAR)
  PSI/feat: cvd=0.000  vwap_position=0.000  ofi=0.000
--------------------------------------------------------
  권고    : ⛔ 롤백 검토
  사유    : CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요.
========================================================
```

_다이제스트 대상 8/11개 (중요도순). 제외: `launcher_20260903_084001_27535.log`, `freeze_sentinel_20260903.log`, `force_flat_guard_20260903.log`_

### `logs/20260903_TRADE.log` — 167B · 2행 · 최종 08:41:03

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-03 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-09-03 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-03 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260903_WARN.log` — 1.2KB · 17행 · 최종 08:41:12

- 형식 평문 · 시각 인식 17행 · WARNING=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-03 08:41:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
2026-09-03 08:41:12 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3343ms — live 중단 원인 분석용
  …
2026-09-03 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0
2026-09-03 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1486ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-03 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1486ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-03 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8734ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8734 band=WARN since_pipe_s=0.2
2026-09-03 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260903.log
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 11 | 08:41:06 | 09:00:08 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 1486ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0 |
| `MainStallTrace` | 1 | 09:00:08 | 09:00:08 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260903.log |

**채널** — `SYSTEM`×16, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×11, `PipePerf`×2, `CB⑤`×2, `Health`×1, `MainStallTrace`×1

### `logs/20260903_SYSTEM.log` — 24.9KB · 212행 · 최종 08:59:19

- 형식 평문 · 시각 인식 205행 · INFO=205, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:32 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21356 | 행감지=30s all_threads=True
2026-09-03 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-03 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-03 08:40:48 [INFO] SYSTEM: 미륵이 초기화
2026-09-03 08:40:48 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-02) 종가 버퍼 로드: 384봉
  …
2026-09-03 09:00:01 [INFO] SYSTEM: [PipePerf][DBG] total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms
2026-09-03 09:00:08 [INFO] SYSTEM: [CybosRT-TICK] #2300 code=A0569 raw_time=90001 parsed=09:00:01 price=1045.60 vol=1 bid1=1045.60 ask1=1045.80 flag=49 side=BUY anchor=1/0
2026-09-03 09:00:11 [INFO] SYSTEM: [CybosRT-TICK] #2400 code=A0569 raw_time=90011 parsed=09:00:11 price=1046.08 vol=1 bid1=1045.58 ask1=1046.28 flag=49 side=BUY anchor=1/0
2026-09-03 09:00:19 [INFO] SYSTEM: [TickUI] alive ticks=2469 code=A0569 close=1044.84
2026-09-03 09:00:23 [INFO] SYSTEM: [CybosRT-TICK] #2500 code=A0569 raw_time=90023 parsed=09:00:23 price=1045.80 vol=1 bid1=1045.78 ask1=1046.12 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×205

**컴포넌트 상위 15** — `CybosRT-TICK`×30, `CybosSub`×21, `System`×17, `TickUI`×16, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `Notify`×5, `BrokerSync`×4, `BalanceUI`×4, `-`×4, `EarlyWarmup`×3

### `logs/20260903_SIGNAL.log` — 11.3KB · 163행 · 최종 08:59:00

- 형식 평문 · 시각 인식 163행 · WARNING=109, INFO=54

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.418
  …
2026-09-03 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.0573 → floor=0.25 적용 (z-score 폭발 방지)
2026-09-03 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.0447 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-03 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0459 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-03 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0908 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-03 09:00:02 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
```

</details>

**WARNING — 태그 5종 (상위 5)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 48 | 09:00:02 | 09:00:02 | 1m 'macro_vix' scale=0.0251 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 42 | 08:45:06 | 08:59:00 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 12 | 09:00:00 | 09:00:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 6 | 09:00:00 | 09:00:00 | ts=08:59 horizon=1m age=1m max_z=-15.19(institution_futures_net) extreme=1 |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×163

**컴포넌트 상위 15** — `ScalerFloor`×72, `ScalerRefresh`×48, `Model`×18, `DynMC`×7, `ScalerMonitor`×6, `TimeRouter`×3, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1, `ZeroDiag`×1

### `logs/20260903_LEARNING.log` — 51.9KB · 293행 · 최종 08:59:00

- 형식 평문 · 시각 인식 293행 · WARNING=143, INFO=150

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3009 < conf_floor=0.3300 (span=0.00172 auc=0.604 out_max=0.3009, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-03 08:40:49 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3464 < conf_floor=0.3300 (n=90) → 보정 재적용
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00081 auc=0.459 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
  …
2026-09-03 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-03 08:55:06 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=18582, ver=5)
2026-09-03 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-03 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1046.16
2026-09-03 09:00:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 143 | 08:40:49 | 08:40:58 | 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×293

**컴포넌트 상위 15** — `Calibration`×278, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260903_MICRO.log` — 33.3KB · 97행 · 최종 08:59:26

- 형식 평문 · 시각 인식 97행 · DEBUG=97

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1044.78/1 ask1=1045.72/3 mp={'microprice_tick': 1045.015, 'midprice_tick': 1045.25, 'depth_bias_tick': -0.2849} mlofi_tick=None queue=None
2026-09-03 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1044.78/1 ask1=1045.70/1 mp={'microprice_tick': 1045.24, 'midprice_tick': 1045.24, 'depth_bias_tick': -0.136} mlofi_tick=-4.3167 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-03 08:45:07 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1044.78/1 ask1=1045.64/3 mp={'microprice_tick': 1044.995, 'midprice_tick': 1045.21, 'depth_bias_tick': -0.258} mlofi_tick=-5.5667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio':…
2026-09-03 08:45:07 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1044.78/1 ask1=1045.64/2 mp={'microprice_tick': 1045.0667, 'midprice_tick': 1045.21, 'depth_bias_tick': -0.1635} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-09-03 08:45:07 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1044.80/1 ask1=1045.64/2 mp={'microprice_tick': 1045.08, 'midprice_tick': 1045.22, 'depth_bias_tick': -0.2715} mlofi_tick=2.6167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
  …
2026-09-03 09:00:00 [DEBUG] MICRO: [MICRO-MINUTE] #15 ts=2026-09-03 08:59:00 close=1046.16 bias=-0.000417 slope=-0.095432 depth_bias=0.0139 mlofi_norm=-0.116512 mlofi_pressure=-1 mlofi_slope=-27.996667 queue_signal=-0.0110 queue_ma=0.0026 queue_momentum=0.0046 depletion=0.4981 refill=0.5019 imbalan…
2026-09-03 09:00:08 [DEBUG] MICRO: [MICRO-TICK] #5900 bid1=1046.00/1 ask1=1046.28/2 mp={'microprice_tick': 1046.0933, 'midprice_tick': 1046.14, 'depth_bias_tick': -0.2808} mlofi_tick=-6.6833 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ra…
2026-09-03 09:00:12 [DEBUG] MICRO: [MICRO-TICK] #6000 bid1=1045.88/2 ask1=1046.26/1 mp={'microprice_tick': 1046.1333, 'midprice_tick': 1046.07, 'depth_bias_tick': 0.1387} mlofi_tick=3.2833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-09-03 09:00:20 [DEBUG] MICRO: [MICRO-TICK] #6100 bid1=1044.84/2 ask1=1045.30/1 mp={'microprice_tick': 1045.1467, 'midprice_tick': 1045.07, 'depth_bias_tick': 0.3028} mlofi_tick=-5.9667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-09-03 09:00:28 [DEBUG] MICRO: [MICRO-TICK] #6200 bid1=1045.52/3 ask1=1045.98/1 mp={'microprice_tick': 1045.865, 'midprice_tick': 1045.75, 'depth_bias_tick': 0.3965} mlofi_tick=-2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
```

</details>

**채널** — `MICRO`×97

**컴포넌트 상위 15** — `MICRO-TICK`×82, `MICRO-MINUTE`×15

### `logs/20260903_DATA.log` — 914B · 5행 · 최종 08:58:41

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:58:10 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=151308 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-03 08:58:10 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-03 08:58:41 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=151309 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-03 08:58:41 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-03 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-03 08:58:10 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=151308 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-03 08:58:10 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-03 08:58:41 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=151309 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-03 08:58:41 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-03 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

### `logs/20260903_PROBE.log` — 1.7KB · 11행 · 최종 08:58:41

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:41:06 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-09-03 08:58:10 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-03 08:58:10 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-03 08:58:10 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-03 08:58:10 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-09-03 08:58:41 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-03 08:58:41 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-03 08:58:41 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-03 08:58:41 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-03 08:58:41 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:10 | 08:58:41 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

**채널** — `PROBE`×11

**컴포넌트 상위 15** — `CybosProbe`×10, `CybosInvestorProbe`×1

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

### 메인 스레드 블로킹 2건 · 최대 8734ms · 5초 초과 1건

상위 — 8734ms, 3157ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8734ms | 1486ms | **7248ms (83%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260903_WARN.log`
```
--- Traceback ×1(표본)
09:00:08 2026-09-03 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260903.log
--- 메인 스레드 블로킹 ×2(표본)
08:41:09 2026-09-03 08:41:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
09:00:08 2026-09-03 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8734ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8734 band=WARN since_pipe_s=0.2
```

### `logs/20260903_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-03 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20260903_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-09-03 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
```

### `logs/20260903_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3009 < conf_floor=0.3300 (span=0.00172 auc=0.604 out_max=0.3009, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00081 auc=0.459 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3179 < conf_floor=0.3300 (span=0.00233 auc=0.559 out_max=0.3179, 기저율=0.3167 n=120) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260903_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260903_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 10 | 08:41:06 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 7 | 09:00:01 [WARNING] total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 7 | 09:00:01 [WARNING] total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260903_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=21356 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 104 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 73 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260903_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:06 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 95 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0384) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 88 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0390) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260902 | 15:40 | 로그 본문 |
| 20260901 | 15:40 | 로그 본문 |
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260903** | **09:00** | 로그 본문 |

- 델타 **-400분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · 마지막 갱신 2026-09-02 19:09

최근 헤딩 8개:
```
### 부수: 세션 번호 자리표시자 확정
### 구현하지 않음 (C등급 · 보류)
## 2026-09-02 (MW0601 519차 — 사용자 지시: CB② 복원 · 정지 경보 · F-1 마감 잔여 청산)
### 1. CB② 복원 — `CB_CONSEC_STOP_LIMIT` 9999 → 3
### 2. `[MainStall]` ALERT(≥15초) → 대시보드 「2 경보」 탭
### 3. F-1 — `daily_close()` 진입 시 잔여 포지션 자동청산
### 부수: `test_514` 토글 가드의 **범위**를 옮겼다(삭제가 아니다)
### 검증 총계
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
정됐다.
- **원인**: 514차가 마감 진입부에 **탐지**(`[DailyCloseResidual]`)를 넣었으나 경보뿐이라,
  15:40에 사람이 화면 앞에 없으면 아무 일도 일어나지 않았다.
- **결정**: 그 탐지 블록을 **집행**으로 승격. 잔량이 보이면 시장가 청산을 시도한다.
- **Why(상한이 필수인 이유)**: 마감은 Qt 메인 스레드에서 돌고 뒤에 EOD 재학습·P8·
  세션 저장이 줄줄이 기다린다. 청산이 마감을 인질로 잡으면 피해가 더 크다.
  ⇒ **시도 3회 + 벽시계 12초**를 둘 다 걸고, 넘기면 포기하고 **경보 후 마감을 계속
  진행한다**. 시한 12초는 `MAIN_THREAD_STALL_ALERT_MS`(15초)보다 **짧게** 잡았다 —
  안전장치가 자기 자신 때문에 정지 경보를 울리는 모양을 피한다(테스트가 이 부등식을 고정).
- **How to apply**:
  · 청산은 검증된 `_ts_broker_direct_force_exit()` **재사용**(새 주문 경로 신설 금지).
  · 종료 판정용 **읽기전용 프로브** `_ts_broker_residual_qty()` 신설 — 기존 함수의
    반환값은 `ret == 0`("주문을 보냈는가")이라 **「이미 FLAT」과 「TR 실패」를 같은
    `False`로 뭉갠다.** 그 둘을 구분하지 못하면 루프 종료 조건을 만들 수 없다
    (계측 4원칙 ②). 프로브는 `(qty, side, measured)`를 돌려준다.
  · **미측정이어도 시도한다** — 프로브가 브로커 잔고를 직접 읽으므로 계좌가 FLAT이면
    주문 없이 끝난다. "엔진 상태를 못 읽었다"는 "포지션이 없다"가 아니다.
  · 킬스위치 `DAILY_CLOSE_FORCE_EXIT_ENABLED`(False면 514차 경보 전용으로 복귀).
- **검증(시뮬)**: 가짜 브로커 5종 —
  ① 잔량3·체결 → **1시도 1주문, 최종 0계약, closed=True**
  ② 이미 FLAT → **0시도 0주문**(불필요한 주문을 내지 않는다)
  ③ 미체결 → 3시도 3주문 후 `잔량 3계약`으로 **정직한 실패 보고**
  ④ 잔고 TR 실패 → **주문 0건**, `잔량 **미측정**`으로 보고(눈감고 쏘지 않는다)
  ⑤ 주문 거부 → 3시도 0성공, 실패 보고
  전부 0.05초 내 종료, 예외 전파 0.
- **검증(테스트)**: §3(12건) — 설정 상한·부등식(시한 < ALERT) · 배선 2경로 ·
  미측정 경로도 시도 · 이중 상한 루프 · 예외 미전파 · 실패를 실패로 보고 ·
  프로브 읽기전용(AST) · FLAT/미측정 구분 · **두 함수 파싱 키 일치**(드리프트 방지) ·
  기존 청산 경로 재사용 · 외부 가드 주문권한 False.
- ⚠ **이중 청산 위험 없음** — 같은 시간대 주문 가능 경로는 `scripts/force_flat_guard.py`
  뿐인데 `FORCE_FLAT_GUARD_ORDER_ENABLED = False`(**미구현**)다. 그 플래그를 켤 때는
  이 항목과 **함께** 재검토할 것(15:39 가드와 15:40 마감이 같은 잔량에 두 번 주문한다).
  테스트가 그 플래그를 고정한다.
- **미검증(라이브)**: 실제 마감에서 잔량이 있는 날의 왕복. 잔량 없는 날은 프로브가
  `[ResidualProbe]` 없이 조용히 지나가는 것이 정상 — **미발화를 결함으로 읽지 말 것.**

### 부수: `test_514` 토글 가드의 **범위**를 옮겼다(삭제가 아니다)

`test_514`는 *"자동조치가 절대원칙·한시예외 토글을 하나도 건드리지 않았다"* 를 고정한다.
CB② 값이 바뀌었으므로 기대값을 3으로 옮기고 **근거를 주석으로 남겼다** — 이 표는
「값이 영원히 고정」이 아니라 「자동조치가 넘지 않을 선」을 재는 것이므로, 승인된 변경이
나면 기대값을 함께 옮기지 않으면 **가드가 승인된 결정을 계속 위반으로 신고한다.**
`test_fa_is_alert_only_no_exit_order` 도 같은 이유로
`test_fa_exit_goes_only_through_the_bounded_helper` 로 재정의했다 — 지금 지킬 선은
「청산하지 않는다」가 아니라 **「임시 주문 경로를 daily_close 안에 만들지 않는다」** 다.

### 검증 총계

신규 29 passed. 전체 **1,118 passed · 3 failed · 1 skipped · 4 xfailed**.
실패 3건 **전량 선행**(`test_483` 형제 프로젝트 사본 대조 · `test_504` ×2).
직전 1,089 + 29 = **1,118** 정확 일치 — 신규 실패 0.
⚠ 환경(선행·무관): `test_500_*.py` 5개(모듈 최상단 `sys.exit(0)`) ·
`test_511_exit_order_reject.py`(전체 실행 시 `win32com` 적재 `0xc0000139` 하드 크래시).
전체는 **청크 분할**로 측정.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · 마지막 갱신 2026-09-02 19:09

최근 헤딩 8개:
```
### 사용자 몫 (자동조치가 할 수 없음)
## 2026-09-02 (MW0601 519차 — 사용자 지시 구현 결과)
### 구현 완료 (커밋됨 · 재기동 대기)
### 🔴 재기동 필요
### 라이브 검증 대기
### 함께 재검토해야 하는 것 (묶여 있음)
### 이월 (미해결, 517·518차에서 승계)
### 사용자 몫
```

미완료 체크박스 **2338건** (끝에서 30건)
```
- [ ] 🔴 **미륵이 재기동** — F-3·G-1은 `main.py` 변경이라 재기동 전까지 실효 없음
- [ ] **F-3 실측**: 재기동 후 첫 자동진입의 `trades.entry_source = 'SYSTEM_AUTO'` 확인.
- [ ] **G-1 실측**: 재기동 시 잔량이 있으면 「2 경보」 탭에 새 ERROR 줄 실물 확인.
- [ ] **G-4 회귀**: 다음 장후 다이제스트에서 이월분이 있으면 블록이 뜨는지,
- [ ] **F-1** `daily_close()` 진입 전 잔여 포지션 강제청산 — **주간회의 승인 대기
- [ ] **CB② 복원**(`CB_CONSEC_STOP_LIMIT` 9999 → 2~3) — 재검토 기한 2026-08-29
- [ ] **G-2** 메인 스레드 정지 실시간 경보 — 표본 1건이라 임계 근거 부족(313차).
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례 — 발생 시 승인 검토 착수
- [ ] **O-t3** `entry_source` 오표기 **과거 영향 범위** 회고 스캔 — `trades.db` 전수:
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건 — 다음 장후 필수
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 오늘 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
- [ ] **미륵이 재기동** — 셋 다 `config/settings.py`·`main.py`·`dashboard/` 변경이라
- [ ] **CB② 발동 1회 관측** — 🔴 **실전 전환 기준 ⑤의 남은 조건.** 값 복원만으로는
- [ ] **CB② 부작용 관측** — 발동 시 그날 신규 진입이 전부 사라진다. 장후 점검에서
- [ ] **정지 경보 실물 확인** — 다음 ALERT(≥15초) 발생 시 「2 경보」 탭에 뜨는지.
- [ ] **F-1 왕복 확인** — 마감 시각에 잔량이 있는 날 `[DailyCloseForceExit]` 로그로
- [ ] **F-1 마감 지연 관측** — 청산이 붙은 날 마감 소요시간이 12초 이상 늘지 않는지,
- [ ] **`FORCE_FLAT_GUARD_ORDER_ENABLED`(현재 False·미구현) 승격 논의는 F-1과 한 묶음.**
- [ ] **`MAIN_THREAD_STALL_ALERT_MS`(15초) 재보정** — 26주 WFA 항목(482차 F-3 섀도
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔(F-3은 미래만 고침)
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **G-2 잔여** 정지 경보의 **임계 근거** — 이번엔 화면 노출만 했고 임계는 무변경
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
거 부족(313차).
      **26주 WFA 주기**에 482차 F-3 섀도 관찰 종료와 함께 판정

### 이월 (517차 장후가 등록, 미해결)

- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례 — 발생 시 승인 검토 착수
- [ ] **O-t3** `entry_source` 오표기 **과거 영향 범위** 회고 스캔 — `trades.db` 전수:
      "복구 이벤트 이후 같은 세션 내 진입 중 entry_source != SYSTEM_AUTO" 건수.
      🔵 F-3이 **미래**를 고치므로 이 회고는 여전히 필요하다(소급 정정 없음).
      코드 변경 없이 지금도 실행 가능
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건 — 다음 장후 필수

### 사용자 몫 (자동조치가 할 수 없음)

- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 오늘 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인

## 2026-09-02 (MW0601 519차 — 사용자 지시 구현 결과)

> 상세: `DECISION_LOG.md` 2026-09-02(519차). 커밋 `d03b629`.
> 세 항목 모두 종전 C등급이었고 **사용자가 직접 지시**해 구현했다.

### 구현 완료 (커밋됨 · 재기동 대기)

- [x] **CB② 복원** `CB_CONSEC_STOP_LIMIT` 9999 → **3** (기대값 7곳 동반 이동)
- [x] **정지 경보** `[MainStall]` ALERT(≥15초) → 대시보드 「2 경보」 탭
- [x] **F-1** `daily_close()` 잔여 포지션 자동청산 (시도 3회 · 12초 상한)

### 🔴 재기동 필요

- [ ] **미륵이 재기동** — 셋 다 `config/settings.py`·`main.py`·`dashboard/` 변경이라
      재기동 전까지 실효 없음

### 라이브 검증 대기

- [ ] **CB② 발동 1회 관측** — 🔴 **실전 전환 기준 ⑤의 남은 조건.** 값 복원만으로는
      충족되지 않는다(게이트가 `UNMEASURED` 반환). 5분 내 서로 다른 3포지션 손절이
      나면 당일 정지가 걸린다. ⚠ **인위적으로 만들지 말 것** — 관측될 때까지 열어둔다
- [ ] **CB② 부작용 관측** — 발동 시 그날 신규 진입이 전부 사라진다. 장후 점검에서
      ⓐ 발동 로그 ⓑ min_samples 미달 채널 적립 속도 를 함께 볼 것.
      적립이 눈에 띄게 느려지면 2~3 사이 재조정 또는 재유예를 주간회의에 상정
- [ ] **정지 경보 실물 확인** — 다음 ALERT(≥15초) 발생 시 「2 경보」 탭에 뜨는지.
      ⚠ ALERT는 5거래일에 1건꼴이라 **며칠 안 뜨는 것이 정상**이다
- [ ] **F-1 왕복 확인** — 마감 시각에 잔량이 있는 날 `[DailyCloseForceExit]` 로그로
      청산 완료까지 확인. ⚠ 잔량 없는 날은 **조용한 것이 정상**
- [ ] **F-1 마감 지연 관측** — 청산이 붙은 날 마감 소요시간이 12초 이상 늘지 않는지,
      `[MainStall]` ALERT가 마감 때문에 발화하지 않는지

### 함께 재검토해야 하는 것 (묶여 있음)

- [ ] **`FORCE_FLAT_GUARD_ORDER_ENABLED`(현재 False·미구현) 승격 논의는 F-1과 한 묶음.**
      둘 다 켜면 15:39 외부 가드와 15:40 마감이 **같은 잔량에 두 번 주문**한다.
      `tests/test_519_*.py:test_f1_no_double_exit_with_external_guard` 가 고정 중
- [ ] **`MAIN_THREAD_STALL_ALERT_MS`(15초) 재보정** — 26주 WFA 항목(482차 F-3 섀도
      관찰 종료와 함께). WARN(5~15초) 승격 여부도 그때 판단(현재 일부러 제외)

### 이월 (미해결, 517·518차에서 승계)

- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔(F-3은 미래만 고침)
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **G-2 잔여** 정지 경보의 **임계 근거** — 이번엔 화면 노출만 했고 임계는 무변경

### 사용자 몫

- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인

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

### `data/heartbeat_MW0601_20260903.json` — 245B · 09-03 08:59:37
```json
{
 "pid": 21356,
 "written_at": "2026-09-03T09:00:07",
 "beat_epoch": 1788393601.6654131,
 "beat_age_sec": 5.9,
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

### `docs/정기점검/매일점검` — 94개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` | 114.3KB | 09-02 19:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_post.md` | 78.0KB | 09-02 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_intra.md` | 66.8KB | 09-02 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_pre.md` | 58.1KB | 09-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-01 18:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_post.md` | 89.7KB | 09-01 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_intra.md` | 68.8KB | 09-01 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_pre.md` | 49.8KB | 09-01 09:01 |

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

1. `logs/20260903_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
2. 메인 스레드 정지 5초 초과 **1건** (최대 8734ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
3. `logs/20260903_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260903*.log` (Windows) / `grep 강제청산 logs/*20260903*.log`*