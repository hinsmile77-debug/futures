# 미륵이 증거 다이제스트 — 2026-08-14 / PRE

- 생성 2026-08-14 08:50:50 KST · PC **MW0602** (`MW0602 (override . host=claude)`)
- 리포 `/sessions/charming-gracious-mccarthy/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260814` · `2026-08-14` · `260814` · `0814`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **12개** 파일 · 12개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_20714.log` | 1 | `logs/Mireuk_batch/launcher_20260814_084001_20714.log` | 29.8KB | 08-14 08:49 |
| `{DATE}_DATA.log` | 1 | `logs/20260814_DATA.log` | 0B | 08-14 08:40 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260814_DEBUG.log` | 0B | 08-14 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260814_HEALTH.log` | 0B | 08-14 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260814_HOGA.log` | 647.0KB | 08-14 08:50 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260814_LEARNING.log` | 106.3KB | 08-14 08:49 |
| `{DATE}_MICRO.log` | 1 | `logs/20260814_MICRO.log` | 19.6KB | 08-14 08:50 |
| `{DATE}_PROBE.log` | 1 | `logs/20260814_PROBE.log` | 95B | 08-14 08:41 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260814_SIGNAL.log` | 9.4KB | 08-14 08:49 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260814_SYSTEM.log` | 14.7KB | 08-14 08:50 |
| `{DATE}_TRADE.log` | 1 | `logs/20260814_TRADE.log` | 167B | 08-14 08:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260814_WARN.log` | 590B | 08-14 08:41 |

## 2. 코드·커밋 상태

- HEAD `a86b238` · 브랜치 `dev` · 미커밋 520건
```
M .claude/skills/mireuk-daily-check/SKILL.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/scripts/collect_evidence.py
 M .gitignore
 M AGENTS.md
 M CLAUDE.md
 M CORE.md
 M ENSEMBLE_SIGNAL_UPGRADE_PLAN.md
 M EOD_RETRAIN.bat
 M INSTALL.bat
 M LAUNCH_API.bat
 M README.md
 M ROADMAP.md
 M SETUP_GUIDE.md
 M STRATEGY_PARAMS_GUIDE.md
 M _archive/docs/260601_DYNAMIC_MIN_CONF_PLAN.md
 M _archive/docs/260625_MODEL_OPERATION_AUDIT.md
 M _archive/docs/260629_MAITREYA_DIST_DEPLOYMENT_PLAN.md
 M _archive/docs/Audit_prompt.txt
 M "_archive/docs/\353\252\250\353\223\234\355\225\204\355\204\260_X\353\223\261\352\270\211_\354\230\244\353\266\204\353\245\230_\354\210\230\354\240\225_2026-07-15.md"
 M _archive/plans/CODEX_SESSION_START.md
 M _archive/plans/CYBOS_PLUS_REFACTOR_PLAN.md
 M _archive/plans/PROJECT_DESIGN.md
 M _archive/plans/REVIEW_REPORT_v6.5.md
 M _archive/plans/REVIEW_REPORT_v7.0.md
 M "_archive/root_scripts/MW0602 pull guide.txt"
 M _archive/root_scripts/_check_7212.py
 M _archive/root_scripts/_check_pkl_compat.py
 M _archive/root_scripts/_fix_registry_p0.py
 M _archive/root_scripts/_measure_retrain.py
 M _archive/root_scripts/_purge_extreme_conf.py
 M _archive/sub_docs/260425.txt
 M _archive/sub_docs/gemi_UPGRADE_PROPOSAL.md
 M _archive/sub_docs/gpt_futures_trading_system_improvement.md
 M "_archive/sub_docs/\355\216\230\353\204\220\355\231\225\354\236\245.txt"
 M backtest/__init__.py
 M backtest/param_optimizer.py
… 외 480건
```

**당일(2026-08-14) 커밋**
```
a86b238 [MW0601] 456차 Wave 2: F5 opt_pcr 진단 — 가설 반증, 조치 보류 (코드 변경 0)
4abf7c4 [MW0602] 469차: 일일 점검 스킬 — 승패 사후검증 편입 + 313차 방법론 확정 + 불변식 감시 누락 수정
9d6f85f [MW0602] 468차: 로드맵 반영 — 26주 WFA에 고착 지표 점검 편입 + ⑧에 G-1 선행조건 기록
f2332be [MW0602] 468차 G-1: 사이즈 제한 해제를 이벤트→상태로 (사이드카 레이블 규칙 판정)
1b2342f [MW0602] 468차 G-3: 청산 라벨 트리거/결과 2축 — exit_reason 은 무변경
a21b66a [MW0602] 468차 G-4: 파이프라인 지연 원인 확정 — S6 → SHAP 심사 (기존 S1 가설 반증)
e5764ed [MW0602] 468차 G-2: 수집기 §12 고착 지표 — "죽은 지표"를 기계가 잡는다
92dd09a [MW0602] 468차: test_465 tp1_reached 단정 정정 + test_425 판정 전환 등록
7558523 [MW0602] 468차: 보호트레일 분리를 표시 계층에서 (F-2 / A안) — exit_reason 라벨은 무변경
ce3d9d9 [MW0602] 468차: _pre_retrain_done 을 전일 EOD 적재로도 해제 (F-1, 킬스위치 동반)
5a40b47 [MW0602] 468차: SHAP CORE 지표를 운영 CORE 정의에 연결 (F-3) — F-2는 465차 결정 충돌로 보류
0ca3091 [MW0602] 468차: 일일 점검 오탐 2건 정정 — 수집기 화이트리스트 + DailyClose 마커 경고 레벨
```

**최근 커밋 12건**
```
a86b238 [MW0601] 456차 Wave 2: F5 opt_pcr 진단 — 가설 반증, 조치 보류 (코드 변경 0)
4abf7c4 [MW0602] 469차: 일일 점검 스킬 — 승패 사후검증 편입 + 313차 방법론 확정 + 불변식 감시 누락 수정
9d6f85f [MW0602] 468차: 로드맵 반영 — 26주 WFA에 고착 지표 점검 편입 + ⑧에 G-1 선행조건 기록
f2332be [MW0602] 468차 G-1: 사이즈 제한 해제를 이벤트→상태로 (사이드카 레이블 규칙 판정)
1b2342f [MW0602] 468차 G-3: 청산 라벨 트리거/결과 2축 — exit_reason 은 무변경
a21b66a [MW0602] 468차 G-4: 파이프라인 지연 원인 확정 — S6 → SHAP 심사 (기존 S1 가설 반증)
e5764ed [MW0602] 468차 G-2: 수집기 §12 고착 지표 — "죽은 지표"를 기계가 잡는다
92dd09a [MW0602] 468차: test_465 tp1_reached 단정 정정 + test_425 판정 전환 등록
7558523 [MW0602] 468차: 보호트레일 분리를 표시 계층에서 (F-2 / A안) — exit_reason 라벨은 무변경
ce3d9d9 [MW0602] 468차: _pre_retrain_done 을 전일 EOD 적재로도 해제 (F-1, 킬스위치 동반)
5a40b47 [MW0602] 468차: SHAP CORE 지표를 운영 CORE 정의에 연결 (F-3) — F-2는 465차 결정 충돌로 보류
0ca3091 [MW0602] 468차: 일일 점검 오탐 2건 정정 — 수집기 화이트리스트 + DailyClose 마커 경고 레벨
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
| `CB_ACCURACY_MIN_30M` | `0.28` | `0.28` | 일치 | CB③ 임계(0.35→0.28 완화). CLAUDE.md 절대원칙 §2 본문 '35%' 옆에 실값 병기 완료(468차) — 문서-코드 괴리 해소됨 |
| `CB_ACC_RESTRICTED_MIN` | `0.30` | `0.30` | 일치 | WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인 |
| `CB_ACCURACY_MIN_30M_STRICT` | `0.42` | `0.42` | 일치 | 과신 연속 시 강화 임계 (0.50→0.42 완화) |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | `False` | `False` | 일치 | 극단 스프레드(20틱) block — 311차 섀도우 검증 대기. 근거·활성화 조건은 config/settings.py:4770-4781 |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | `True` | `True` | 일치 | 호가 상하한 핀 진입 차단 — 켜져 있어야 정상 |
| `HURST_SOFT_BLOCK_ENABLED` | `True` | `True` | 일치 | Hurst 소프트 차단(사이즈 0.5배). 316~318차 재보정 계열 |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | `True` | `True` | 일치 | Degraded 상태 자동진입 차단 — 켜져 있어야 정상 |
| `CB_PIPE_PAUSE_MS` | `5_000` | `5_000` | 일치 | CB⑤ 실질 구현. `CB_API_LATENCY_LIMIT` 은 Kiwoom 레거시로 Cybos에서 미사용 |
| `ENTRY_HORIZON_B1` | `3.2` | `3.2` | 일치 | 1m/3m 경계 [374차 1.5→3.5, 387차 3.5→3.2] — 드리프트 항목 |
| `ENTRY_HORIZON_B2` | `4.4` | `4.4` | 일치 | 3m/5m 경계 [374차 2.5→4.0, 387차 4.0→4.4] — 드리프트 항목 |
| `CB_DAILY_HALT_FULL_BLOCK` | `3` | `3` | 일치 | HALT 3회 → 완전 관망 |
| `MODEL_LABEL_STATE_UNLOCK_ENABLED` | `True` | `True` | 일치 | 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지 |
| `PRE_RETRAIN_DONE_BY_EOD_ENABLED` | `True` | `True` | 일치 | 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치 |
| `ZONE_ENTRY_BAN_ENFORCE` | `False` | `False` | 일치 | 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지 |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | `True` | `True` | 일치 | 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다 |
| `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` | `True` | `True` | 일치 | 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치) |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

### 차단 게이트 전수 인벤토리 — 29개 중 **7개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `TICKUI_TRACE_ENABLED` | False | 기능토글 |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | 기록됨 |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
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
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `MC_UNREACHABLE_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260814_HOGA.log` 647.0KB — 존재와 크기만 증거로 본다_

### `logs/20260814_TRADE.log` — 167B · 2행 · 최종 08:40:59

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:56 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-14 08:40:59 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-08-14 08:40:56 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-14 08:40:59 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20260814_WARN.log` — 590B · 4행 · 최종 08:41:03

- 형식 평문 · 시각 인식 4행 · WARNING=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:01 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-14 08:41:01 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-14 08:41:02 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 110ms account=777019873
2026-08-14 08:41:03 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
2026-08-14 08:41:01 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-14 08:41:01 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-14 08:41:02 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 110ms account=777019873
2026-08-14 08:41:03 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 4 | 08:41:01 | 08:41:03 | request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |

**채널** — `SYSTEM`×4

**컴포넌트 상위 15** — `LiveDBG`×4

### `logs/20260814_SYSTEM.log` — 14.7KB · 117행 · 최종 08:50:36

- 형식 평문 · 시각 인식 115행 · INFO=115, PLAIN=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:41 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15140 | 행감지=30s all_threads=True
2026-08-14 08:40:41 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-14 08:40:41 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-14 08:40:41 [INFO] SYSTEM: 미륵이 초기화
2026-08-14 08:40:41 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-13) 종가 버퍼 로드: 385봉
  …
2026-08-14 08:50:05 [INFO] SYSTEM: [TickUI] alive ticks=1211 code=A0569 close=1101.68
2026-08-14 08:50:36 [INFO] SYSTEM: [CybosRT-TICK] #1300 code=A0569 raw_time=85042 parsed=08:50:42 price=1101.28 vol=1 bid1=1101.16 ask1=1101.30 flag=49 side=BUY anchor=1/0
2026-08-14 08:50:54 [INFO] SYSTEM: [CybosRT-ROLLOVER] code=A0569 from=08:50 to=08:51
2026-08-14 08:50:54 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=08:50 O=1101.64 H=1102.20 L=1100.64 C=1101.48 V=211
2026-08-14 08:50:54 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:50 vol=211 | live_buy=133 shadow_buy=117 anchor_buy=117 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
```

</details>

**채널** — `SYSTEM`×115

**컴포넌트 상위 15** — `CybosSub`×21, `CybosRT-TICK`×18, `System`×7, `CybosRT-START`×6, `TickUI`×6, `CybosRT-ROLLOVER`×6, `BAR-CLOSE`×6, `CVD-ANCHOR`×6, `PreMarket`×5, `SYSTEM`×4, `BrokerSync`×4, `BalanceUI`×4, `EarlyWarmup`×3, `Account`×2, `CybosDailyPnl`×2

### `logs/20260814_SIGNAL.log` — 9.4KB · 75행 · 최종 08:49:55

- 형식 평문 · 시각 인식 75행 · WARNING=30, INFO=45

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.414
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.406
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.402
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.410
  …
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 5m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 10m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 15m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 30m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.01s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 30 | 08:45:02 | 08:49:55 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×75

**컴포넌트 상위 15** — `ScalerRefresh`×33, `ScalerFloor`×24, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1

### `logs/20260814_LEARNING.log` — 106.3KB · 542행 · 최종 08:49:55

- 형식 평문 · 시각 인식 542행 · WARNING=167, INFO=375

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:43 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00090 auc=0.579 out_max=0.3506) vs clean(n=80 span=0.00090 auc=0.579 out_max=0.3506 base=0.3500) 오염행=0건 축퇴판정 live=False clean=False
2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00241 auc=0.547 out_max=0.4138) vs clean(n=80 span=0.00241 auc=0.547 out_max=0.4138 base=0.4125) 오염행=0건 축퇴판정 live=False clean=False
2026-08-14 08:40:43 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.527 out_max=0.3335 (기준 auc<0.53 and span<0.020, 기저율=0.3333 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00042 auc=0.457 out_max=0.5002) vs clean(n=80 span=0.00042 auc=0.457 out_max=0.5002 base=0.5000) 오염행=0건 축퇴판정 live=True clean=True
  …
2026-08-14 08:40:56 [INFO] LEARNING: [DriftAdjuster] 로드: alpha=0.01000, 이력 10일, 마지막 액션=DRIFT_UP
2026-08-14 08:41:00 [INFO] LEARNING: [SHAP] 주간 심사 완료 | 하락피처=0개 | 교체후보=3개 | CORE안전=✅ (슬라이스 2/2 · 그룹 3개 · 모델미탑재 ofi_pressure · 중요도0 cvd_delta_norm,vwap_position | hz=1m)
2026-08-14 08:45:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=105
2026-08-14 08:47:56 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=105
2026-08-14 08:49:55 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=105
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 167 | 08:40:43 | 08:40:56 | 축퇴 감지 — span=0.00021 auc=0.527 out_max=0.3335 (기준 auc<0.53 and span<0.020, 기저율=0.3333 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제] |

**채널** — `LEARNING`×542

**컴포넌트 상위 15** — `Calibration`×532, `ScalerWarmup`×3, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1

### `logs/20260814_MICRO.log` — 19.6KB · 54행 · 최종 08:50:38

- 형식 평문 · 시각 인식 54행 · DEBUG=54

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1103.28/3 ask1=1103.40/1 mp={'microprice_tick': 1103.37, 'midprice_tick': 1103.34, 'depth_bias_tick': 0.6565} mlofi_tick=None queue=None
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1103.28/1 ask1=1103.40/1 mp={'microprice_tick': 1103.34, 'midprice_tick': 1103.34, 'depth_bias_tick': 0.5713} mlofi_tick=-4.0 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1.0…
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1103.42/8 ask1=1103.62/3 mp={'microprice_tick': 1103.5655, 'midprice_tick': 1103.52, 'depth_bias_tick': 0.3388} mlofi_tick=0.25 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 7.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': -2…
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1103.44/1 ask1=1103.62/3 mp={'microprice_tick': 1103.485, 'midprice_tick': 1103.53, 'depth_bias_tick': 0.1051} mlofi_tick=5.7833 queue={'depletion_bid': 7.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1102.90/1 ask1=1103.62/4 mp={'microprice_tick': 1103.044, 'midprice_tick': 1103.26, 'depth_bias_tick': -0.4268} mlofi_tick=-5.2167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio'…
  …
2026-08-14 08:50:01 [DEBUG] MICRO: [MICRO-TICK] #2500 bid1=1101.56/1 ask1=1101.72/2 mp={'microprice_tick': 1101.6134, 'midprice_tick': 1101.64, 'depth_bias_tick': -0.1006} mlofi_tick=1.6833 queue={'depletion_bid': 1.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_rati…
2026-08-14 08:50:11 [DEBUG] MICRO: [MICRO-TICK] #2600 bid1=1101.68/1 ask1=1101.98/1 mp={'microprice_tick': 1101.83, 'midprice_tick': 1101.83, 'depth_bias_tick': -0.1105} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-14 08:50:25 [DEBUG] MICRO: [MICRO-TICK] #2700 bid1=1101.14/1 ask1=1101.38/1 mp={'microprice_tick': 1101.26, 'midprice_tick': 1101.26, 'depth_bias_tick': -0.2346} mlofi_tick=-2.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-08-14 08:50:38 [DEBUG] MICRO: [MICRO-TICK] #2800 bid1=1101.30/1 ask1=1101.40/1 mp={'microprice_tick': 1101.35, 'midprice_tick': 1101.35, 'depth_bias_tick': -0.1543} mlofi_tick=-2.1167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-08-14 08:50:54 [DEBUG] MICRO: [MICRO-MINUTE] #6 ts=2026-08-14 08:50:00 close=1101.48 bias=0.000235 slope=-0.028897 depth_bias=-0.0197 mlofi_norm=0.014287 mlofi_pressure=1 mlofi_slope=36.760000 queue_signal=0.0178 queue_ma=-0.0237 queue_momentum=0.0249 depletion=0.5000 refill=0.5000 imbalance_s…
```

</details>

**채널** — `MICRO`×54

**컴포넌트 상위 15** — `MICRO-TICK`×48, `MICRO-MINUTE`×6

### `logs/20260814_PROBE.log` — 95B · 1행 · 최종 08:41:02

- 형식 평문 · 시각 인식 1행 · INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:02 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
  …
2026-08-14 08:41:02 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
```

</details>

**채널** — `PROBE`×1

**컴포넌트 상위 15** — `CybosInvestorProbe`×1

### `logs/Mireuk_batch/launcher_20260814_084001_20714.log` — 29.8KB · 273행 · 최종 08:49:55

- 형식 평문 · 시각 인식 190행 · WARNING=34, WARN=2, INFO=167, PLAIN=70

<details><summary>첫 5행 / 끝 5행</summary>

```
============================================================
Mireuk (KOSPI 200 Futures Auto Trader)
Broker : creon
Launch : 20260814_084001
Log    : C:\Users\pc1\PycharmProjects\futures\logs\Mireuk_batch\launcher_20260814_084001_20714.log
  …
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 5m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 10m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 15m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [WARNING] SIGNAL: [ScalerRefresh] 30m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지)
2026-08-14 08:49:55 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 30 | 08:45:02 | 08:49:55 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `LiveDBG` | 4 | 08:41:01 | 08:41:03 | request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `-` | 2 | ??:??:?? | ??:??:?? | ] 이미 실행 중인 main.py 프로세스가 감지됐습니다. |

**채널** — `SYSTEM`×112, `SIGNAL`×75, `TRADE`×2, `PROBE`×1

**컴포넌트 상위 15** — `-`×69, `ScalerRefresh`×33, `ScalerFloor`×24, `CybosSub`×21, `CybosRT-TICK`×16, `DynMC`×7, `System`×7, `Model`×6, `CybosRT-START`×6, `TickUI`×5, `CybosRT-ROLLOVER`×5, `BAR-CLOSE`×5, `CVD-ANCHOR`×5, `GUARD`×4, `SYSTEM`×4

## 5. 거래일 요약 — 오늘 무엇을 했는가

_거래일 패턴이 하나도 안 잡혔다. 로그 문구가 바뀌었을 수 있다 — `config/dailycheck_targets.json` 의 `day_summary_patterns` 를 확인하라._

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260814_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.414
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.406
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.402
```

### `logs/20260814_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:43 2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00090 auc=0.579 out_max=0.3506) vs clean(n=80 span=0.00090 auc=0.579 out_max=0.3506 base=0.3500) 오염행=0건 축퇴판정 live=False clean=False
08:40:43 2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00241 auc=0.547 out_max=0.4138) vs clean(n=80 span=0.00241 auc=0.547 out_max=0.4138 base=0.4125) 오염행=0건 축퇴판정 live=False clean=False
08:40:43 2026-08-14 08:40:43 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.527 out_max=0.3335 (기준 auc<0.53 and span<0.020, 기저율=0.3333 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:43 2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00042 auc=0.457 out_max=0.5002) vs clean(n=80 span=0.00042 auc=0.457 out_max=0.5002 base=0.5000) 오염행=0건 축퇴판정 live=True clean=True
```

### `logs/Mireuk_batch/launcher_20260814_084001_20714.log`
```
--- 기동 복원 ×7(표본)
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.414
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.406
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.402
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260814_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:56 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 4 | 08:41:01 [WARNING] request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmPro… |

- 이 로그 생존구간: 08:41 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 88 | 08:40:41 [INFO] 활성화 | file=logs\crash_fault.log PID=15140 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 13 | 08:49:05 [INFO] alive ticks=1052 code=A0569 close=1101.02 |

- 이 로그 생존구간: 08:40 ~ 08:50

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:02 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 7 | 08:49:55 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 08:49

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-07-20 (362차) — 청산 P1~P6 문서-코드 불일치 정리 중 숨은 AttributeError 버그 발견·수정 + exit_manager.py 제거
## 2026-07-20 (362차 후속) — Hurst 재검증(317차 Phase 5)을 CLAUDE.md "주기적 재검증" 등록부에 편입
## 2026-07-21 (363차 — 0721 정기점검 딥다이브: 손절계단화(Loss Tier1) 사각지대 2건 해소)
### [설계결정] 오늘 실손실 2건 다 Loss Tier1(360차)이 못 뜬 원인 규명 + tick-level 확장(라이브) + qty=1 대체안 섀도 계측
## 2026-07-21 (363차 후속 — 0721 딥다이브 제안3·4를 360/361차 계열 캠페인에 편입)
### [설계결정] quantile 기대엣지 필터·qty=1 TP1 이후 트레일 폭을 별도 신설 대신 기존 캠페인에 컬럼/자매채널로 편입
## 2026-07-21 (364차 — 0721 정기점검 딥다이브: tp2_hold_shadow 표본 0건 구조적 원인 규명 + 363차 커밋 라이브 미반영 확인)
### [발견] tp2_hold_shadow(361차)가 구현 이후 단 한 건도 기록되지 않음 — EntryGate×MetaGate 사이즈 감쇠 중첩으로 진입수량이 항상 1에 수렴
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
밋 라이브 미반영 확인)

### [발견] tp2_hold_shadow(361차)가 구현 이후 단 한 건도 기록되지 않음 — EntryGate×MetaGate 사이즈 감쇠 중첩으로 진입수량이 항상 1에 수렴

**File**: `main.py:6724-6744`(진입수량 결정부), `main.py:10579`(tp2_hold_shadow 기록
조건)
**증상**: 0721 정기점검 딥다이브 중 오늘 실거래 10건(6승4패, +1,019,004원)을
조사하다, Sizer가 매 사이클 2~5계약을 제안(`[Sizer] ... → N계약` 로그)했음에도
실제 체결은 10건 전부 예외 없이 1계약이었음을 발견. `data/db/trades.db`를 직접
조회한 결과 `tp2_hold_shadow`(361차, 0720 구현, "TP3 도달 0건" 원인규명용
counterfactual 채널) 누적 총 건수가 **0건**(구현일 이후 하루도 빠짐없이 0) —
최소표본(15건) 판정이 구조적으로 영원히 불가능한 상태로 방치돼 있었음.
**원인**: `main.py:10579`의 `if stage == 2 and is_full_close and total_qty == 2:`가
`tp2_hold_shadow` 기록 조건인데, 실제 진입 수량이 항상 1로 귀결돼 이 조건이 한
번도 참이 된 적이 없음. 수량이 항상 1로 귀결되는 이유를 추적한 결과, 대시보드
"최대허용수량"(기본값 10, `dashboard/main_dashboard.py:4431`)이 원인이 아니라,
`main.py:6724` 이하에서 Sizer 산출값(`_qty_display`)에 `[EntryGate] 사이즈 축소
×0.6`(GBM 재학습 임박 시)과 `[MetaGate] action=reduce size_mult=0.5~0.75`(메타
확신도 낮을 때)가 **곱으로 중첩** 적용되기 때문임을 확인(예: Sizer 2계약 × 0.6 ×
0.75 = 0.9 → `max(1, round(...))`로 바닥값 1에 수렴). 오늘 10건 전부 이 두 감쇠 중
최소 하나가 동시에 걸려 있었음(TRADE/SIGNAL 로그 대조 확인).
**Why**: 361차가 tp2_hold_shadow를 설계할 때 "qty=2 포지션이 TP2에서 잔량을 100%
종료하는 순간"을 관측 대상으로 삼았는데, 그 전제(qty=2 진입이 종종 발생함)가
EntryGate·MetaGate의 독립적인 위험 감쇠가 곱으로 겹치는 현재 운영 조건에서는
성립하지 않음 — 각 게이트는 개별적으로는 합리적인 안전장치이지만, 상호작용으로
"항상 qty=1"이라는 의도치 않은 부작용을 냄. 363차가 그 사이 신설한
tp1_trail_shadow/loss_tier1_qty1_shadow는 (의도했든 우연이든) qty=1을 정확히
겨냥하고 있어 현재 실제 운영 상태와 합치함.
**결정**: 코드 변경 없음(이번 세션은 진단·보고 전용, §9 사전등록 원칙에 따라
즉시 자동 수정하지 않음). 조치 방향은 NEXT_TODO 364차 항목으로 등록 — 주간회의에서
(a) EntryGate×MetaGate 중첩 감쇠를 완화해 qty=2 진입을 실제로 발생시킬지, 또는
(b) qty=1 고정을 현재의 정상 운영 상태로 받아들이고 tp2_hold_shadow를 qty=1 전용
로직으로 재설계할지 결정.
**부수 발견**: 같은 날 앞서 커밋된 363차/363차 후속(`2239db4`/`0cde21f` —
loss_tier1_qty1_shadow·tp1_trail_shadow 신규 테이블+quantile 컬럼)이 오늘 실제
라이브 프로세스에는 반영되지 않은 채로 하루가 지나갔음을 `data/db/trades.db`에
해당 테이블이 없는 것으로 확인 — 오늘 qty=1 손실 4건(아래 참고) 전부가 이 신규
섀도 계측의 관측 대상이었는데 하나도 기록되지 못한 기회비용 발생. 다음 재기동 시
최신 커밋 반영 여부 확인 필요(NEXT_TODO 364차 항목).
**참고(비공식 손계산, 확정 아님)**: 오늘 손실 4건 중 TP1 미도달 3건(#2 -4.2pt, #5
-4.0pt, #9 -3.2pt)에 대해 entry~stop 50%(tier1) 조기청산을 가정하면 각각 약
-2.4pt/-1.6pt/-1.65pt로 손실 규모가 대략 절반 수준으로 줄었을 개연성 — n=3의
손계산이라 확정적 결론은 아니며, 공식 판정은 loss_tier1_qty1_shadow 표본 축적 후
금요일 캠페인 리포트로.
**검증**: `data/db/trades.db` 직접 쿼리로 tp2_hold_shadow 누적 0건 확인,
predictions.db 사후검증(5m 방향성 정확도 44.4%, 체크리스트+게이트 통과 후 실현
승률 60%)으로 필터링 레이어의 실효성 별도 확인. 코드 변경 없어
py_compile/라이브 검증 해당 없음.
**관련**: 361차(tp2_hold_shadow 원 구현), 363차/363차 후속(qty=1 전용 섀도 채널),
`docs/정기점검/매일점검/0721.txt`(이 딥다이브 리포트 원문).

```

</details>

### dev_memory/NEXT_TODO.md — 859.9KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### DONE
### NEXT
## 2026-05-22 (82차) — 미시 레짐 워밍업 UI
### 처리 완료
### 다음 작업
## 2026-06-25 (243차 이후)
### DONE
### NEXT (Stage 2 ~ Phase 3)
```

미완료 체크박스 **1189건** (끝에서 30건)
```
- [ ] **pred_select 5-12초 병목 (S1)** — verified=6 전환 시점(30m 첫 채점 후) predictions DB 쿼리 풀스캔 의심. `ts`/`horizon` 컬럼 인덱스 추가 검토
- [ ] **30m FL편향 87%** — 09:50~10:07 구간 FL편향 심각. BiasReset 발동 여부 확인
- [ ] **`[Model] 정합성 오류` 로그 재발 없음** — 재시작·재학습 후 허위 불일치 미발생 확인
- [ ] **`resync_mismatch` 사유 비계획 GBM 재학습 없음** — `[GBM] 수동 재학습 시작 | resync_mismatch` 로그 미발생 확인
- [ ] **오늘(06-16) 09:01~13:03 구간 진입판단 재검토** — 버그로 인해 GBM이 일시적으로 FLAT 디폴트(33.3%)였을 가능성 있는 구간. SGD 블렌딩 비중이 낮았던 분봉이 있었는지 LEARNING.log 확인
- [ ] **EOD 재학습 실패해도 P8/WAL 계속 진행 확인** — 다음 EOD에서 (정상이든 또 실패하든) `[P8] EOD 스케일러 재적합 완료`·`[WAL] 체크포인트 완료` 로그가 항상 출력되는지 확인
- [ ] **time_zone 크래시 미재발** — `[ERR-FATAL] minute_pipeline: local variable 'time_zone' referenced before assignment` 재발 없음 확인 (WARN.log)
- [ ] **진입단계 추적 카드 신규 컬럼 표시** — "차단사유" 컬럼, "8.STEP7 차단/9.진입후보(최종)/10.진입완료" 단계, 게이트 상세 툴팁이 신뢰도게이트 탭에서 정상 렌더링되는지 확인
- [ ] **Hurst 차단 표시 확인** — Hurst<0.45로 막힌 분봉이 "8. STEP7 차단" + "Hurst X.XXX < 0.45" 텍스트로 정확히 표시되는지 확인
- [ ] **차단사유 파일 로깅 확인** — `SIGNAL.log`/`SYSTEM.log` 등에서 `[차단] ...` 메시지가 grep으로 확인되는지 점검 (기존엔 대시보드 버퍼 전용)
- [ ] **`ensemble_decisions` 마이그레이션 확인** — 재시작 후 `entry_gate_json` 등 6컬럼이 `ALTER TABLE`로 정상 추가됐는지 (`PRAGMA table_info`) 확인
- [ ] **PipePerf 라벨 정상화** — `S1=Xms`가 STEP1(검증) 본문을 가리키는지 확인 (종전 S2로 오표기되던 것)
- [ ] **`[Buffer-Timing]` 로그 확인** — 정체 재발 시 raw_fetch/pred_select/pred_update/pred_insert 중 실제 병목 구간 확정 (179차 "S2 지연 원인" TODO를 이 계측으로 대체)
- [ ] **15:10 이후 워치독 경보 미반복** — "파이프라인 N분 미실행" 90초 간격 반복 없음 확인
- [ ] **15:10 이후 강제 파이프라인 재실행 부작용 소멸** — `_try_pipeline_recovery`가 `run_minute_pipeline`을 추가 호출하는 로그 없음 확인
- [ ] **`verify_and_update` timeout 부작용 점검** — `[Buffer] verify_and_update 배치 오류` (3s timeout 실패) 빈도, 너무 잦으면 timeout 상향 검토
- [ ] **ScalerRefresh B_INTRADAY** `horizons=['1m','3m','5m','10m','15m','30m']` — `_is_fitted` 제거 효과 유지 확인
- [ ] **SGD 가중치 로그 형식** — `[OnlineLearner] 1m 가중치 조정 SGD=XX% GBM=XX%` (버킷→호라이즌별 변경 확인)
- [ ] **ERR-FATAL 없음** — `X has N features` 에러 재발 없음
- [ ] **STABLE_TREND 진입 개선** — 12시대 conf=48~52% 신호 발생 시 `[P1] Checklist min_conf 분리: 0.XX→0.48` 로그 확인
- [ ] **편향패널티 비활성화** — TrendGate ON 구간에서 `[MetaGate] 편향패널티` 로그 없음 확인
- [ ] **opt 4주 수집 후 Phase D 재검증**: opt_chain_pcr/gex_bn/atm_* 누적 확인
- [ ] **feat=118 vs managed=97 불일치** 해소: shap_feature_registry.json active_features 갱신 (opt_chain 포함)
- [ ] **SHAP 탭 호라이즌별 확장** — Phase C 호라이즌별 SHAP 계산 (현재 1m 기준만)
- [ ] `raw_features` DB 조회: `opt_chain_pcr`, `opt_gex_bn` 키 존재 여부 (미확인)
- [ ] **Phase D 재검증**: opt_chain_pcr/gex_bn/atm_* 4주 축적 확인 후 Walk-Forward 재실행
- [ ] **GBM retrain**: opt 피처 포함 첫 retrain → per-horizon pkl 생성 → 호라이즌별 모델 전환
- [ ] **Phase E**: SHAP Tracker 6개 호라이즌 확장 (shap_tracker.py horizon 컬럼 추가)
- [ ] **feat=118 vs managed=97 불일치** 해소: shap_feature_registry.json active_features 갱신 (opt_chain 포함)
- [ ] **Cybos Chejan `status` 필드 실측**
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
un_minute_pipeline()` 공통 차단 로그 경로보다 앞에서 `entry_mode`/`allowed_grades`/`mode_filter_passed`를 안전 초기화하도록 조정

[DONE 2026-05-20] **68차: watchdog 허위 지연 경보 원인 규명**
- 11:06~11:13 반복 경보는 실시간 분봉 미수신이 아니라 `minute_pipeline` 예외로 `notify_pipeline_ran()` 미도달한 결과임을 확인

[NEXT 실세션] **68차 수정사항 장중 검증 (2026-05-21)**
- SYSTEM 로그에 `ERR-FATAL minute_pipeline: local variable 'entry_mode' referenced before assignment` 재발 없는지 확인
- 자동진입 OFF, ENTRY cooldown, X등급 분봉에서 공통 차단 로그만 남고 파이프라인이 정상 종료되는지 확인
- 11시대와 유사한 흐름에서 watchdog 90초/150초 경보가 사라지는지 확인

[NEXT 미정] **watchdog 경보 문구 정밀화**
- 현재 `파이프라인 1분 30초 미실행` 문구가 예외 중단과 분봉 수신 지연을 구분하지 못함
- 최근 fatal 예외가 있었으면 `수신 지연 의심` 대신 `직전 파이프라인 예외 후 미복구` 식으로 원인 힌트 분리 검토
## 2026-05-22 (82차) — 미시 레짐 워밍업 UI

### 처리 완료

- [DONE 2026-05-22] **MicroRegime 워밍업 메타 추가**
  - `collection/macro/micro_regime.py` 에 `warmup` 상태 계산 추가
  - 단계: `L1 TR/ATR seed` → `L2 ADX warmup` → `L3 ATR avg warmup` → `READY`

- [DONE 2026-05-22] **헤더 미시 레짐 아래 워밍업 상태줄 추가**
  - `dashboard/main_dashboard.py` 에 라벨 + progress bar 추가
  - `main.py` 에서 `_mr["warmup"]` 를 대시보드로 전달

- [DONE 2026-05-22] **ATR avg 워밍업용 캔들 버퍼 상한 수정**
  - close/high/low buffer 길이를 늘려 `ATR avg 20샘플` 완료 전에 버퍼가 먼저 잘리는 문제 수정

### 다음 작업

- [NEXT 2026-05-23] **실 UI 워밍업 표시 검증**
  - `start_mireuk.bat` 기동 후 헤더에서 워밍업 라벨/바 위치, 색상, 폭 확인
  - 장중 재시작 시 `L1 → L2 → L3 → READY` 전환이 실제 분봉 흐름과 맞는지 확인

- [NEXT 2026-05-23] **워밍업 중 레짐 텍스트 처리 정책 검토**
  - 현재는 `횡보장/추세장` 텍스트는 유지하고, 아래에 워밍업 보조 설명을 표시
  - 필요 시 워밍업 중 본문 텍스트를 `레짐 워밍업` 또는 `혼합` 으로 강등할지 검토

- [NEXT 향후] **미시 레짐 워밍업 로그 명시화**
  - `MicroRegime` 로그에 `warmup level/progress` 를 함께 남길지 검토

---

---

## 2026-06-25 (243차 이후)

### DONE

- [DONE 2026-06-25] **Phase 2 재학습 경로 피처 슬라이싱 적용 (Audit Q1·Q2 해소)**
  - `learning/batch_retrainer.py` `_retrain_phase2()`에 `get_available_feature_set()` 호출 추가
  - 스케일러 97개 전체 fit, GBM h_idx 슬라이싱, feature_names_{hz}.pkl 저장
  - 커밋: 2f2cb8e (243차)

### NEXT (Stage 2 ~ Phase 3)

- [NEXT Stage 2] **buy_vol/sell_vol 30일 누적 후 1m/3m 재학습**
  - Phase 2 배포 후 ~30일 경과 시 OFI/CVD 기반 단기 모델 추가 개선 가능
  - EOD_RETRAIN.bat --phase2 로그에서 cvd_direction 비제로 비율 모니터링

- [NEXT Stage 3] **TRAINING_WINDOW 3m:5000 / 5m:3000 효과 확인**
  - 50일+ 누적 시 3m/5m 학습 윈도우 상한 실제 적용 여부 확인
  - `[Retrain-P2] * TRAINING_WINDOW=N 적용` 로그 출력 확인

- [NEXT Phase 3] **Platt Scaling 호라이즌별 독립 적용**
  - 현재 앙상블 캘리브레이션 공유 → 호라이즌별 독립 Platt 보정기 분리
  - 앙상블 왜곡 제거 효과 기대

- [NEXT 모니터링] **다음 EOD 재학습 후 슬라이싱 로그 확인**
  - `[Retrain-P2] *m 피처 슬라이싱: 97 → N개 (horizon_feature_sets.json)` 출력 여부
  - 출력 없으면: JSON에 해당 호라이즌 미등록 또는 전체 피처셋과 동일한 경우

```

</details>

### dev_memory/CURRENT_STATE.md — 515.8KB · 마지막 갱신 2026-08-11 18:30

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

### dev_memory/SESSION_LOG.md — 583.6KB · 마지막 갱신 2026-08-10 00:14

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

(없음)

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 20개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/evidence_MW0602-20260812_post.md` | 63.9KB | 08-14 08:01 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 11.8KB | 08-14 08:01 |
| `docs/정기점검/매일점검/MW0601-20260810-점검리포트.md` | 43.1KB | 08-14 07:58 |
| `docs/정기점검/매일점검/0810_Fix_고도화_통합구현계획_MW0601.md` | 22.4KB | 08-14 07:58 |
| `docs/정기점검/매일점검/MW0602-20260813-점검리포트.md` | 39.5KB | 08-13 23:43 |
| `docs/정기점검/매일점검/evidence_MW0602-20260813_post.md` | 65.5KB | 08-13 23:26 |
| `docs/정기점검/매일점검/MW0602-20260812-점검리포트.md` | 25.2KB | 08-12 16:58 |
| `docs/정기점검/매일점검/MW0602-20260811-점검리포트.md` | 23.7KB | 08-11 17:50 |

### `docs/정기점검/금요일점검` — 42개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0602/exit_expectancy_map_20260810.md` | 1.8KB | 08-10 18:39 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_metrics_20260810.json` | 2.0KB | 08-10 15:18 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_report_20260810.md` | 4.6KB | 08-10 15:18 |
| `docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md` | 39.1KB | 08-08 19:21 |
| `docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601.md` | 24.3KB | 08-08 17:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260807.md` | 131.5KB | 08-07 19:23 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260807.json` | 70.5KB | 08-07 19:23 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260807.md` | 26.2KB | 08-07 19:23 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260814_LEARNING.log`: **축퇴** 8건(표본)
2. 미커밋 변경 520건
3. 고착 지표 **`전략판정`** — `UNDERPERFORM` 100% (8건 / 8일). 안전장치가 '켜져 있다'와 '작동한다'는 다르다 (§12)

## 12. 고착 지표 (최근 10거래일 상태값 분포)

> **왜 보는가.** 292차(CB③-P4 상시 RESTRICTED)·303차(FP-CRITICAL 상시 CRITICAL)·
> 371차(PSI 메가빈)·468차(`CORE안전` 6거래일 100% ⚠️)는 전부 **같은 실패**였다 — 
> 지표가 한쪽 값에 붙박여 죽어 있는데 매번 사람이 뒤늦게 발견했다.
> `무기록`은 그 반대 형태다: 문구가 바뀌어 계측이 조용히 끊긴 상태.

| 지표 | 판정 | 관측일 | 표본 | 값 분포 | 왜 보는가 |
|---|---|---|---|---|---|
| `CORE안전` | ✅ 변동 | 10 | 90 | `⚠️`×89, `✅`×1 | SHAP CORE 감시. 468차 F-3 이전 6거래일 100% ⚠️ 고착 실적 |
| `degraded` | ✅ 변동 | 8 | 174 | `OFF`×173, `ON`×1 | 시스템 헬스 강등. OFF 고착은 정상(사고 없음) |
| `CB_state` | ⚪ 정상고착 | 8 | 2957 | `NORMAL`×2957 | CB 전체 상태(매분 샘플). NORMAL 고착은 정상 — 단 Phase 5 조건 ②(CB 실발동 확인)가 여전히 미충족이라는 뜻이기도 하다 |
| `GuardFair_유효` | ✅ 변동 | 8 | 48 | `ok`×30, `무효`×18 | 457차 fair_valid. 무효 100%면 GuardFair 비교가 죽어 있다 |
| `전략판정` | 🔴 고착 | 8 | 8 | `UNDERPERFORM`×8 | 전략 상태 경보 판정. 한 값 고착이면 판정식이 무의미해진 것 |

*판정 기준: 한 값이 100%면 `고착`, 표본 0이면 `무기록`, 관측일·표본이 기준 미달이면 `표본부족`(판정 보류). **출발점이지 결론이 아니다** — 고착이 정상인 지표도 있다(예: 사고 없는 날의 CB 상태).*

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260814*.log` (Windows) / `grep 강제청산 logs/*20260814*.log`*