# 미륵이 증거 다이제스트 — 2026-08-14 / INTRA

- 생성 2026-08-14 12:41:18 KST · PC **MW0602** (`MW0602 (override . host=claude)`)
- 리포 `/sessions/peaceful-jolly-wright/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260814` · `2026-08-14` · `260814` · `0814`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **12개** 파일 · 12개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_20714.log` | 1 | `logs/Mireuk_batch/launcher_20260814_084001_20714.log` | 977.8KB | 08-14 12:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260814_DATA.log` | 195.0KB | 08-14 12:41 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260814_DEBUG.log` | 134.5KB | 08-14 12:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260814_HEALTH.log` | 1.5KB | 08-14 12:15 |
| `{DATE}_HOGA.log` | 1 | `logs/20260814_HOGA.log` | 30.7MB | 08-14 12:41 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260814_LEARNING.log` | 256.6KB | 08-14 12:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260814_MICRO.log` | 618.7KB | 08-14 12:41 |
| `{DATE}_PROBE.log` | 1 | `logs/20260814_PROBE.log` | 60.7KB | 08-14 12:41 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260814_SIGNAL.log` | 419.9KB | 08-14 12:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260814_SYSTEM.log` | 457.1KB | 08-14 12:41 |
| `{DATE}_TRADE.log` | 1 | `logs/20260814_TRADE.log` | 5.0KB | 08-14 12:08 |
| `{DATE}_WARN.log` | 1 | `logs/20260814_WARN.log` | 15.9KB | 08-14 12:34 |

## 2. 코드·커밋 상태

- HEAD `a86b238` · 브랜치 `dev` · 미커밋 522건
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
… 외 482건
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

_본문 미열람(설정): `20260814_HOGA.log` 30.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/11개 (중요도순). 제외: `20260814_PROBE.log`, `launcher_20260814_084001_20714.log`, `20260814_DEBUG.log`_

### `logs/20260814_TRADE.log` — 5.0KB · 35행 · 최종 12:08:56

- 형식 평문 · 시각 인식 35행 · INFO=35

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:56 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-14 08:40:59 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-14 09:53:54 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=29,721,639) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-14 09:53:54 [INFO] TRADE: [MarginCap] SHORT 산출=3계약 → 증거금상한=2계약으로 축소
2026-08-14 09:54:54 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=29,721,639) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.0→3계약]
  …
2026-08-14 11:26:55 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2058 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-14 11:26:55 [INFO] TRADE: [Position] 체결청산 SHORT @ 1090.62 | PnL=+1.03pt (+49,863원) | 하드스톱 [TP1보호]
2026-08-14 11:26:55 [INFO] TRADE: [청산 완료] PnL=+1.03pt (+49,863원)
2026-08-14 12:08:56 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=29,795,493) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-14 12:08:56 [INFO] TRADE: [MarginCap] SHORT 산출=3계약 → 증거금상한=2계약으로 축소
```

</details>

**채널** — `TRADE`×35

**컴포넌트 상위 15** — `Sizer`×10, `Chejan`×7, `Position`×5, `MarginCap`×3, `주문요청`×3, `ProfitGuard`×1, `진입체크`×1, `체결진입`×1, `체결진입보정`×1, `TickTP1`×1, `TP1 부분청산`×1, `청산 완료`×1

### `logs/20260814_WARN.log` — 15.9KB · 68행 · 최종 12:34:55

- 형식 평문 · 시각 인식 68행 · WARNING=68

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:01 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-14 08:41:01 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-14 08:41:02 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 110ms account=777019873
2026-08-14 08:41:03 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
2026-08-14 08:55:02 [WARNING] SYSTEM: [Canary] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증
  …
2026-08-14 11:26:57 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 94ms account=777019873
2026-08-14 11:50:55 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.238% (임계 ±0.204%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-14 12:13:55 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 +0.207% (임계 ±0.153%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-14 12:14:56 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=213ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-14 12:34:55 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.136% (임계 ±0.133%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
```

</details>

**WARNING — 태그 20종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 17 | 08:41:01 | 11:26:57 | request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 9 | 09:16:54 | 12:34:55 | 5분 누적 수익률 -0.783% (임계 ±0.474%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ChejanFlow` | 7 | 11:25:55 | 11:26:55 | account='777019873' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='2048' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=11:25:55.039' | positi… |
| `ChejanMatch` | 7 | 11:25:55 | 11:26:55 | order_no='2048' | pending='ENTRY:SHORT qty=2 filled=0 order_no=2048 reason=진입 req_at=11:25:55.039' | pending_matched=True |
| `PendingOrder` | 6 | 11:25:55 | 11:26:55 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1091.54, 'reason': '진입', 'hint_source': '', 'atr': 1.2614, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `Health` | 5 | 09:38:55 | 12:14:56 | level=WARNING degraded=OFF | latency=199ms | quality=1.00 | cache_age=182s | exceptions_10m=0 |
| `Canary` | 2 | 08:55:02 | 08:55:02 | scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `EntryFillFlow` | 2 | 11:25:56 | 11:25:56 | actual_side='SHORT' | after='SHORT 2계약 @ 1091.64' | applied_side='SHORT' | before='SHORT 2계약 @ 1091.54' | fill_no='' | fill_price=1091.64 | fill_qty=1 | order_no='2048' | pending='ENTRY:SHORT qty=2 filled=1 order_no=2048 reason=진입 req_at=1… |
| `ExitCooldown` | 2 | 11:26:55 | 11:26:55 | 하드스톱 후 2분 재진입 금지 (until 11:28:55) |
| `EntryAttempt` | 1 | 11:25:55 | 11:25:55 | atr=1.2614 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='SHORT' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='A' | pending='NONE' |… |
| `EntrySendOrderResult` | 1 | 11:25:55 | 11:25:55 | code='A0569' | direction='SHORT' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=11:25:55.039' | position='FLAT' | quantity=2 | raw_direction='SHORT' | ret=0 | reverse_entry_enabled=False |
| `FixB` | 1 | 11:25:55 | 11:25:55 | 낙관적 오픈 완료 direction=SHORT status=SHORT qty=2 optimistic=True |

**채널** — `SYSTEM`×63, `HEALTH`×5

**컴포넌트 상위 15** — `LiveDBG`×17, `ScalerRefresh`×9, `ChejanFlow`×7, `ChejanMatch`×7, `PendingOrder`×6, `Health`×5, `Canary`×2, `EntryFillFlow`×2, `ExitCooldown`×2, `EntryAttempt`×1, `EntrySendOrderResult`×1, `FixB`×1, `EntryPendingCreated`×1, `TickTP1`×1, `PartialExitAttempt`×1

### `logs/20260814_SYSTEM.log` — 457.1KB · 3338행 · 최종 12:41:03

- 형식 평문 · 시각 인식 3329행 · INFO=3329, PLAIN=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:41 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15140 | 행감지=30s all_threads=True
2026-08-14 08:40:41 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-14 08:40:41 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-14 08:40:41 [INFO] SYSTEM: 미륵이 초기화
2026-08-14 08:40:41 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-13) 종가 버퍼 로드: 385봉
  …
2026-08-14 12:41:02 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-57343 nonarb=+171928
2026-08-14 12:41:02 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-57343 nonarb=+171928
2026-08-14 12:41:02 [INFO] SYSTEM: [System] 대기 중 | 장중 — Cybos 실시간 분봉 대기 중 (FutureCurOnly/FutureJpBid 수신 시 자동 진행) | 레짐=RISK_ON | 포지션=FLAT | 12:41:02
2026-08-14 12:41:02 [INFO] SYSTEM: [CybosRT-TICK] #76300 code=A0569 raw_time=124107 parsed=12:41:07 price=1090.02 vol=2 bid1=1089.68 ask1=1090.04 flag=49 side=BUY anchor=2/0
2026-08-14 12:41:03 [INFO] SYSTEM: [OptionChain][Worker] 완료 1544ms | target=24 valid=24 PCR=0.733 ATM_PCR=1.071 GEX=53.04B
```

</details>

**채널** — `SYSTEM`×3329

**컴포넌트 상위 15** — `CybosInvestorRaw`×882, `CybosRT-TICK`×768, `CybosRT-ROLLOVER`×236, `BAR-CLOSE`×236, `CVD-ANCHOR`×236, `TickUI`×235, `S6Detail`×221, `PipePerf`×221, `System`×62, `MicroRegime`×42, `OptionChain`×27, `CybosSub`×21, `IntradayRegime`×19, `CybosEvent`×14, `BalanceUI`×13

### `logs/20260814_SIGNAL.log` — 419.9KB · 3603행 · 최종 12:40:56

- 형식 평문 · 시각 인식 3603행 · WARNING=1811, INFO=1792

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.414
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.406
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.402
2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.410
  …
2026-08-14 12:40:56 [INFO] SIGNAL: [MetaGate][LIVE] skip: blended=0.396 reduce_thr=0.465 take_thr=0.570 (grade=X min_conf=0.620 ens=0.322 meta_raw=0.506 ens_w=0.60)
2026-08-14 12:40:56 [INFO] SIGNAL: 앙상블: dir=+1 conf=32.2% grade=X micro=혼합
2026-08-14 12:40:56 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=5m tf=5.25 → TP1×0.7
2026-08-14 12:40:56 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: CoherenceGate / conf미달(0.322<mc0.620)
2026-08-14 12:40:56 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=39.6% size_mult=1.00 reason=meta_skip
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1326 | 09:00:55 | 12:34:55 | 1m 'macro_vix' scale=0.0049 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 168 | 09:00:54 | 12:25:55 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 126 | 09:00:54 | 12:25:55 | ts=09:00 horizon=1m age=2m max_z=+4.56(volume_acceleration) extreme=1 |
| `Checklist` | 100 | 09:11:54 | 12:40:56 | 신뢰도 미달 37.8% < 38.4% → 강제 X등급 |
| `WeightCollapse` | 44 | 09:07:54 | 12:37:55 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 30 | 08:45:02 | 08:49:55 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `PCR-Dampen` | 12 | 09:11:54 | 11:37:55 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 3 | 09:22:54 | 10:36:55 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3829 < 필요 0.3840 (conf_floor=0.330, min_conf=0.384, span=0.0169). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `MetaGate` | 2 | 09:13:54 | 09:29:54 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×3603

**컴포넌트 상위 15** — `ScalerFloor`×1392, `SIGNAL`×442, `Ensemble`×231, `FQAdj`×219, `MetaGate`×210, `ZeroDiag`×208, `Model`×174, `ScalerMonitor`×126, `Checklist`×123, `ATR-Horizon`×101, `ScalerRefresh`×65, `차단`×57, `WeightCollapse`×44, `MicroRegime`×42, `ToxicityGate`×41

### `logs/20260814_LEARNING.log` — 256.6KB · 2111행 · 최종 12:40:56

- 형식 평문 · 시각 인식 2111행 · WARNING=178, INFO=1933

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:43 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00090 auc=0.579 out_max=0.3506) vs clean(n=80 span=0.00090 auc=0.579 out_max=0.3506 base=0.3500) 오염행=0건 축퇴판정 live=False clean=False
2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00241 auc=0.547 out_max=0.4138) vs clean(n=80 span=0.00241 auc=0.547 out_max=0.4138 base=0.4125) 오염행=0건 축퇴판정 live=False clean=False
2026-08-14 08:40:43 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.527 out_max=0.3335 (기준 auc<0.53 and span<0.020, 기저율=0.3333 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00042 auc=0.457 out_max=0.5002) vs clean(n=80 span=0.00042 auc=0.457 out_max=0.5002 base=0.5000) 오염행=0건 축퇴판정 live=True clean=True
  …
2026-08-14 12:40:55 [INFO] LEARNING: [Bias⚠] 15m 적중=33%(5/15) UP=4 DN=1 FL=10 [FL편향⚠ 67%]
2026-08-14 12:40:55 [INFO] LEARNING: [Bias] 30m 적중=0%(0/10) UP=0 DN=0 FL=10
2026-08-14 12:40:55 [INFO] LEARNING: [Bias] 3m 적중=23%(7/30) UP=3 DN=15 FL=12
2026-08-14 12:40:55 [INFO] LEARNING: [Bias] 5m 적중=47%(14/30) UP=6 DN=17 FL=7
2026-08-14 12:40:56 [INFO] LEARNING: [SGD] 4건 학습 | SGD비중=30% 50분정확도=16.7%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 178 | 08:40:43 | 12:37:55 | 축퇴 감지 — span=0.00021 auc=0.527 out_max=0.3335 (기준 auc<0.53 and span<0.020, 기저율=0.3333 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제] |

**채널** — `LEARNING`×2111

**컴포넌트 상위 15** — `LEARNING`×713, `Calibration`×576, `SGD`×220, `sigma`×208, `Bias⚠`×177, `Bias`×88, `MetaConf`×41, `ScalerWarmup`×35, `OnlineLearner`×28, `BiasReset`×13, `SHAP`×6, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1

### `logs/20260814_HEALTH.log` — 1.5KB · 11행 · 최종 12:15:55

- 형식 평문 · 시각 인식 11행 · WARNING=5, INFO=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 09:29:54 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 191ms (표본 20분)
2026-08-14 09:38:55 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=199ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-14 09:39:55 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=201ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-14 10:27:55 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=185ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-14 10:28:54 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=168ms | quality=1.00 | cache_age=57s | exceptions_10m=0
  …
2026-08-14 11:20:55 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=216ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-08-14 11:22:55 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=196ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-08-14 11:23:56 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=196ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-14 12:14:56 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=213ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-14 12:15:55 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=365ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 5 | 09:38:55 | 12:14:56 | level=WARNING degraded=OFF | latency=199ms | quality=1.00 | cache_age=182s | exceptions_10m=0 |

**채널** — `HEALTH`×11

**컴포넌트 상위 15** — `Health`×10, `HealthTrend`×1

### `logs/20260814_MICRO.log` — 618.7KB · 1651행 · 최종 12:41:10

- 형식 평문 · 시각 인식 1651행 · DEBUG=1651

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1103.28/3 ask1=1103.40/1 mp={'microprice_tick': 1103.37, 'midprice_tick': 1103.34, 'depth_bias_tick': 0.6565} mlofi_tick=None queue=None
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1103.28/1 ask1=1103.40/1 mp={'microprice_tick': 1103.34, 'midprice_tick': 1103.34, 'depth_bias_tick': 0.5713} mlofi_tick=-4.0 queue={'depletion_bid': 2.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 1.0…
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1103.42/8 ask1=1103.62/3 mp={'microprice_tick': 1103.5655, 'midprice_tick': 1103.52, 'depth_bias_tick': 0.3388} mlofi_tick=0.25 queue={'depletion_bid': 0.0, 'depletion_ask': 0.0, 'refill_bid': 7.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': -2…
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1103.44/1 ask1=1103.62/3 mp={'microprice_tick': 1103.485, 'midprice_tick': 1103.53, 'depth_bias_tick': 0.1051} mlofi_tick=5.7833 queue={'depletion_bid': 7.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-08-14 08:45:02 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1102.90/1 ask1=1103.62/4 mp={'microprice_tick': 1103.044, 'midprice_tick': 1103.26, 'depth_bias_tick': -0.4268} mlofi_tick=-5.2167 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio'…
  …
2026-08-14 12:40:39 [DEBUG] MICRO: [MICRO-TICK] #139200 bid1=1090.74/2 ask1=1090.86/1 mp={'microprice_tick': 1090.82, 'midprice_tick': 1090.8, 'depth_bias_tick': 0.1758} mlofi_tick=-1.7667 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-08-14 12:40:52 [DEBUG] MICRO: [MICRO-TICK] #139300 bid1=1090.78/1 ask1=1090.88/1 mp={'microprice_tick': 1090.83, 'midprice_tick': 1090.83, 'depth_bias_tick': 0.0717} mlofi_tick=5.85 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
2026-08-14 12:40:55 [DEBUG] MICRO: [MICRO-MINUTE] #236 ts=2026-08-14 12:40:00 close=1090.92 bias=0.002329 slope=0.028872 depth_bias=0.0362 mlofi_norm=-0.027986 mlofi_pressure=-1 mlofi_slope=-55.151667 queue_signal=-0.0525 queue_ma=0.0203 queue_momentum=-0.0030 depletion=0.5000 refill=0.5000 imbalan…
2026-08-14 12:41:02 [DEBUG] MICRO: [MICRO-TICK] #139400 bid1=1089.68/1 ask1=1089.94/1 mp={'microprice_tick': 1089.81, 'midprice_tick': 1089.81, 'depth_bias_tick': -0.2475} mlofi_tick=-6.6833 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ra…
2026-08-14 12:41:10 [DEBUG] MICRO: [MICRO-TICK] #139500 bid1=1090.42/1 ask1=1090.52/3 mp={'microprice_tick': 1090.445, 'midprice_tick': 1090.47, 'depth_bias_tick': -0.2821} mlofi_tick=-0.3333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_…
```

</details>

**채널** — `MICRO`×1651

**컴포넌트 상위 15** — `MICRO-TICK`×1415, `MICRO-MINUTE`×236

### `logs/20260814_DATA.log` — 195.0KB · 885행 · 최종 12:41:02

- 형식 평문 · 시각 인식 885행 · INFO=885

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:58:05 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=157343 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-14 08:58:05 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-14 08:58:35 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=157319 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-14 08:58:35 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-14 09:00:54 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-08-14 12:40:02 [INFO] DATA: [CybosInvestor] fetch#221 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
2026-08-14 12:40:55 [INFO] DATA: [DivergencePanel] source=cybos status=partial div=-85 futures(fi=+165 rt=+250 inst=-446) call(fi=-376 rt=+133) put(fi=+2138 rt=-1658) bias(fi=-1.00 rt=1.00) program(arb=-57326 nonarb=+169248 total=+111922)
2026-08-14 12:41:02 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+187 individual=+246 institution=-464 oi=39820 call_foreign=-384 put_foreign=+2132 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-08-14 12:41:02 [INFO] DATA: [CybosInvestor] program supported=True state=unknown source=Dscbo1.CpSvr8111 arb=-57343 nonarb=+171928 total=+114585 reason=verified field mapping (cybosplus docs, 2026-07-05)
2026-08-14 12:41:02 [INFO] DATA: [CybosInvestor] fetch#222 futures_supported=True program_supported=True option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=Dscbo1.CpSvr8111
```

</details>

**채널** — `DATA`×885

**컴포넌트 상위 15** — `CybosInvestor`×664, `DivergencePanel`×221

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) | 1 |
| 체결(`[체결진입]`) | 1 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 57 |
| 사이저 호출(`[Sizer]`) | 10 |

### 청산 1건 · 승 1 (100%) · 합계 +1.03pt (+49,863원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 11:26:55 | SHORT | +1.03 | +49,863 | 하드스톱 [TP1보호] |

**청산 사유 분포** — `하드스톱 [TP1보호]`×1

> **손절 계열 분해** — 진짜 손절 0건 · TP1 보호트레일 1건 · 태그없음 0건 (청산 1건 중)
> `하드스톱` 라벨이지만 **TP1 도달 후 보호 스톱 = 이익 청산**인 건이 1건이다. 손절로 세지 말 것 — 라벨 하나에 정반대 두 사건이 들어 있다(465차 `tp1_reached`, 468차 로그 태그).

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:25:55 | SHORT | 2 | 1091.54 | 3m | mean-revert |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1, **2계약**×1, **3계약**×8

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×10

### 차단 사유 57건 · 25종

| 건수 | 사유 |
|---|---|
| 33 | 등급X — 미통과 항목: 2_confidence |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.9pt > ATR×5.0=10.0pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.7pt > ATR×5.0=10.4pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.7pt > ATR×5.0=10.8pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.8pt > ATR×5.0=11.1pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.9pt > ATR×5.0=11.4pt (시가=1102.78 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.3pt > ATR×5.0=12.1pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.9pt > ATR×5.0=12.2pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.2pt > ATR×5.0=12.5pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=12.0pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=12.4pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=12.2pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.3pt > ATR×5.0=12.4pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.1pt > ATR×5.0=12.0pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.2pt > ATR×5.0=11.9pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.7pt > ATR×5.0=12.1pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=13.1pt (시가=1102.78 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×33, `3_vwap`×4, `4_cvd`×3, `7_prev_bar`×3, `5_ofi`×2, `6_foreign`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 1건 · 최대 3641ms · 5초 초과 0건

상위 — 3641ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260814_WARN.log`
```
--- [ExitCooldown] ×2(표본)
11:26:55 2026-08-14 11:26:55 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:28:55)
11:26:55 2026-08-14 11:26:55 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 11:28:55)
--- 메인 스레드 블로킹 ×1(표본)
09:57:40 2026-08-14 09:57:40 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3641ms — 메인 스레드 블로킹 발생 | pipe_elapsed=42 watchdog_alerted=[]
```

### `logs/20260814_SIGNAL.log`
```
--- ConfFloorGuard ×6(표본)
09:05:54 2026-08-14 09:05:54 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3896 ≥ 필요 0.3840
09:22:54 2026-08-14 09:22:54 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3829 < 필요 0.3840 (conf_floor=0.330, min_conf=0.384, span=0.0169). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
09:27:54 2026-08-14 09:27:54 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3984 ≥ 필요 0.3840
10:18:55 2026-08-14 10:18:55 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3818 < 필요 0.3840 (conf_floor=0.330, min_conf=0.384, span=0.0143). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- WeightCollapse ×8(표본)
09:07:54 2026-08-14 09:07:54 [INFO] SIGNAL: [Ensemble] dir=+0 conf=39.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:54 2026-08-14 09:10:54 [INFO] SIGNAL: [Ensemble] dir=+0 conf=39.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:54 2026-08-14 09:13:54 [INFO] SIGNAL: [Ensemble] dir=+0 conf=39.0% grade=X regime=RISK_ON [WeightCollapse]
09:16:54 2026-08-14 09:16:54 [INFO] SIGNAL: [Ensemble] dir=+0 conf=38.4% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.414
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.406
08:40:39 2026-08-14 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.402
--- 안전망 ×8(표본)
09:07:54 2026-08-14 09:07:54 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:54 2026-08-14 09:10:54 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:13:54 2026-08-14 09:13:54 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:54 2026-08-14 09:16:54 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260814_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:43 2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00090 auc=0.579 out_max=0.3506) vs clean(n=80 span=0.00090 auc=0.579 out_max=0.3506 base=0.3500) 오염행=0건 축퇴판정 live=False clean=False
08:40:43 2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00241 auc=0.547 out_max=0.4138) vs clean(n=80 span=0.00241 auc=0.547 out_max=0.4138 base=0.4125) 오염행=0건 축퇴판정 live=False clean=False
08:40:43 2026-08-14 08:40:43 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.527 out_max=0.3335 (기준 auc<0.53 and span<0.020, 기저율=0.3333 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:43 2026-08-14 08:40:43 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00042 auc=0.457 out_max=0.5002) vs clean(n=80 span=0.00042 auc=0.457 out_max=0.5002 base=0.5000) 오염행=0건 축퇴판정 live=True clean=True
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260814_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:56 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 8 | 09:54:54 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=29,721,639) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShad… |

- 이 로그 생존구간: 08:40 ~ 12:08

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 4 | 08:41:01 [WARNING] request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:55:02 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:55:02 [WARNING] scaler 노후=0h  z경고피처=20개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 2 | 09:57:40 [WARNING] _tick_header 간격 3641ms — 메인 스레드 블로킹 발생 | pipe_elapsed=42 watchdog_alerted=[] |

- 이 로그 생존구간: 08:41 ~ 12:34

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 88 | 08:40:41 [INFO] 활성화 | file=logs\crash_fault.log PID=15140 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:05 [INFO] alive ticks=1052 code=A0569 close=1101.02 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 202 | 08:54:10 [INFO] alive ticks=1717 code=A0569 close=1102.34 |
| 10:00 | 장중 초반 | 200 | 09:54:01 [INFO] #29600 code=A0569 raw_time=95406 parsed=09:54:06 price=1088.52 vol=1 bid1=1088.36 ask1=1088.54 flag=49 side=B… |
| 12:00 | 장중 중간점 | 158 | 11:54:02 [INFO] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+319,foreign:-241,institution:-125} |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:41

**매분 루프 커버리지 09:00~15:10: 222/371분 (59.8%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:42 | 15:10 | 149 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260814_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:02 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 170 | 08:49:55 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 253 | 09:00:54 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 270 | 09:54:54 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 12:00 | 장중 중간점 | 115 | 11:54:55 [WARNING] 신뢰도 미달 31.3% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:40

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

### dev_memory/NEXT_TODO.md — 868.7KB · **오늘 갱신됨**

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

미완료 체크박스 **1207건** (끝에서 30건)
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

### `docs/정기점검/매일점검` — 22개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0602-20260814-점검리포트.md` | 40.2KB | 08-14 09:15 |
| `docs/정기점검/매일점검/evidence_MW0602-20260814_pre.md` | 48.3KB | 08-14 08:50 |
| `docs/정기점검/매일점검/evidence_MW0602-20260812_post.md` | 63.9KB | 08-14 08:01 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 11.8KB | 08-14 08:01 |
| `docs/정기점검/매일점검/MW0601-20260810-점검리포트.md` | 43.1KB | 08-14 07:58 |
| `docs/정기점검/매일점검/0810_Fix_고도화_통합구현계획_MW0601.md` | 22.4KB | 08-14 07:58 |
| `docs/정기점검/매일점검/MW0602-20260813-점검리포트.md` | 39.5KB | 08-13 23:43 |
| `docs/정기점검/매일점검/evidence_MW0602-20260813_post.md` | 65.5KB | 08-13 23:26 |

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

1. `logs/20260814_SYSTEM.log`: 매분 루프 커버리지 222/371분 (59.8%) — 루프가 빠진 구간이 있다
2. `logs/20260814_SYSTEM.log`: 12:42~15:10 **연속 149분 매분 루프 기록 없음**
3. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
4. `logs/20260814_SIGNAL.log`: **WeightCollapse** 8건(표본)
5. `logs/20260814_LEARNING.log`: **축퇴** 8건(표본)
6. 미커밋 변경 522건
7. 고착 지표 **`전략판정`** — `UNDERPERFORM` 100% (8건 / 8일). 안전장치가 '켜져 있다'와 '작동한다'는 다르다 (§12)

## 12. 고착 지표 (최근 10거래일 상태값 분포)

> **왜 보는가.** 292차(CB③-P4 상시 RESTRICTED)·303차(FP-CRITICAL 상시 CRITICAL)·
> 371차(PSI 메가빈)·468차(`CORE안전` 6거래일 100% ⚠️)는 전부 **같은 실패**였다 — 
> 지표가 한쪽 값에 붙박여 죽어 있는데 매번 사람이 뒤늦게 발견했다.
> `무기록`은 그 반대 형태다: 문구가 바뀌어 계측이 조용히 끊긴 상태.

| 지표 | 판정 | 관측일 | 표본 | 값 분포 | 왜 보는가 |
|---|---|---|---|---|---|
| `CORE안전` | ✅ 변동 | 10 | 94 | `⚠️`×89, `✅`×5 | SHAP CORE 감시. 468차 F-3 이전 6거래일 100% ⚠️ 고착 실적 |
| `degraded` | ✅ 변동 | 9 | 184 | `OFF`×183, `ON`×1 | 시스템 헬스 강등. OFF 고착은 정상(사고 없음) |
| `CB_state` | ⚪ 정상고착 | 9 | 3178 | `NORMAL`×3178 | CB 전체 상태(매분 샘플). NORMAL 고착은 정상 — 단 Phase 5 조건 ②(CB 실발동 확인)가 여전히 미충족이라는 뜻이기도 하다 |
| `GuardFair_유효` | ✅ 변동 | 8 | 48 | `ok`×30, `무효`×18 | 457차 fair_valid. 무효 100%면 GuardFair 비교가 죽어 있다 |
| `전략판정` | 🔴 고착 | 8 | 8 | `UNDERPERFORM`×8 | 전략 상태 경보 판정. 한 값 고착이면 판정식이 무의미해진 것 |

*판정 기준: 한 값이 100%면 `고착`, 표본 0이면 `무기록`, 관측일·표본이 기준 미달이면 `표본부족`(판정 보류). **출발점이지 결론이 아니다** — 고착이 정상인 지표도 있다(예: 사고 없는 날의 CB 상태).*

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260814*.log` (Windows) / `grep 강제청산 logs/*20260814*.log`*