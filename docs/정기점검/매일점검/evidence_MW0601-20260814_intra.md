# 미륵이 증거 다이제스트 — 2026-08-14 / INTRA

- 생성 2026-08-14 12:27:31 KST · PC **MW0601** (`DeskTop-MW0601`)
- 리포 `/sessions/gracious-focused-mendel/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260814` · `2026-08-14` · `260814` · `0814`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_20710.log` | 1 | `logs/Mireuk_batch/launcher_20260814_084001_20710.log` | 957.8KB | 08-14 12:26 |
| `retrain_intraday_{DATE}_093659.log` | 1 | `logs/retrain_intraday_20260814_093659.log` | 2.4KB | 08-14 09:37 |
| `retrain_intraday_{DATE}_103759.log` | 1 | `logs/retrain_intraday_20260814_103759.log` | 2.4KB | 08-14 10:38 |
| `retrain_intraday_{DATE}_112159.log` | 1 | `logs/retrain_intraday_20260814_112159.log` | 2.4KB | 08-14 11:22 |
| `{DATE}_DATA.log` | 1 | `logs/20260814_DATA.log` | 182.6KB | 08-14 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260814_DEBUG.log` | 124.6KB | 08-14 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260814_HEALTH.log` | 2.3KB | 08-14 12:06 |
| `{DATE}_HOGA.log` | 1 | `logs/20260814_HOGA.log` | 29.3MB | 08-14 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260814_LEARNING.log` | 176.1KB | 08-14 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260814_MICRO.log` | 589.1KB | 08-14 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260814_PROBE.log` | 57.8KB | 08-14 12:27 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260814_SIGNAL.log` | 417.2KB | 08-14 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260814_SYSTEM.log` | 438.2KB | 08-14 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260814_TRADE.log` | 3.1KB | 08-14 11:48 |
| `{DATE}_WARN.log` | 1 | `logs/20260814_WARN.log` | 23.2KB | 08-14 12:20 |

## 2. 코드·커밋 상태

- HEAD `e8a56ea` · 브랜치 `v9-dev` · 미커밋 435건
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/RUN_ON_MW0602.md
 M .claude/skills/mireuk-daily-check/SKILL.md
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
 M ROADMAP.md
 M SETUP_GUIDE.md
 M backtest/param_optimizer.py
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
 M config/secrets_example.py
… 외 395건
```

**당일(2026-08-14) 커밋**
```
e8a56ea [MW0602] 459차: F1 승패 집계 단위(레그→포지션) + F2 SHS CORE 미측정 분리
fe88f93 [MW0602] 460차: 공용 헬퍼 _spearman 동률 처리 버그 — 사본 2벌 정정 + 회귀테스트
f75ae87 [MW0602] 458차 후속: [40-B]·[49] 채널 구현 + 기대값 지도 — 손익원천이전 3종
ab5a103 [MW0602] 458차: 손익 원천 이전 제안서 — P7 딥다이브 (미승인, 라이브 무변경)
68d31a6 [MW0602] 457차: 모델 메타 사이드카 + GuardFair 유효성 판정 + ConstOut 재학습 스코프
8ef8878 [MW0602] 456차: ZeroDiag 오진 수정 + min_conf 완화하한 + JointGate 폴백 섀도
a581231 [MW0602] 469차: 일일 점검 스킬 — 승패 사후검증 편입 + 313차 방법론 확정 + 불변식 감시 누락 수정
```

**최근 커밋 12건**
```
e8a56ea [MW0602] 459차: F1 승패 집계 단위(레그→포지션) + F2 SHS CORE 미측정 분리
fe88f93 [MW0602] 460차: 공용 헬퍼 _spearman 동률 처리 버그 — 사본 2벌 정정 + 회귀테스트
f75ae87 [MW0602] 458차 후속: [40-B]·[49] 채널 구현 + 기대값 지도 — 손익원천이전 3종
ab5a103 [MW0602] 458차: 손익 원천 이전 제안서 — P7 딥다이브 (미승인, 라이브 무변경)
68d31a6 [MW0602] 457차: 모델 메타 사이드카 + GuardFair 유효성 판정 + ConstOut 재학습 스코프
8ef8878 [MW0602] 456차: ZeroDiag 오진 수정 + min_conf 완화하한 + JointGate 폴백 섀도
a581231 [MW0602] 469차: 일일 점검 스킬 — 승패 사후검증 편입 + 313차 방법론 확정 + 불변식 감시 누락 수정
6aeccac [MW0601] 461차 고도화: 퍼널 자기검증 + DB폴백 자동검출 + JointGateBlock 폴백비율 집계
0424f64 [MW0601] 461차 문서: 한시예외 4번째 항목 등록 + CB③ 임계 문구 정정
c68e7b4 [MW0601] 461차 후속: Live MDD 분모 정합(자본대비) + 거래0건 폴백 미측정 표기
36d1687 [MW0601] 461차: 진입 퍼널 등급상향 경로 누락 수정 + 증거 다이제스트 덮어쓰기 방지
4fae03d [MW0601] 459차: 일일 점검 스킬 MW0601 실측 정밀조정 — 태그 파싱 수정 + 거래일 요약 신설
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
| `MODEL_LABEL_STATE_UNLOCK_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지 |
| `PRE_RETRAIN_DONE_BY_EOD_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치 |
| `ZONE_ENTRY_BAN_ENFORCE` | `—` | `False` | **미발견 ⚠** | 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지 |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | `—` | `True` | **미발견 ⚠** | 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다 |
| `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` | `—` | `True` | **미발견 ⚠** | 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치) |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

### 차단 게이트 전수 인벤토리 — 27개 중 **7개 꺼짐**

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
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260814_HOGA.log` 29.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `retrain_intraday_20260814_112159.log`, `20260814_MICRO.log`, `20260814_DATA.log`, `20260814_PROBE.log`, `launcher_20260814_084001_20710.log`, `20260814_DEBUG.log`_

### `logs/20260814_TRADE.log` — 3.1KB · 25행 · 최종 11:48:59

- 형식 평문 · 시각 인식 25행 · INFO=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-14 08:41:12 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-14 11:48:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,042,406) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-14 11:48:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi❌ fore✅ prev✅ time✅ risk✅ chas❌ coun✅ | conf=43.8%
2026-08-14 11:48:00 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2202 code=A0569 방향=SHORT 체결=2 미체결=0
  …
2026-08-14 11:48:55 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2212 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-14 11:48:55 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2212 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-14 11:48:55 [INFO] TRADE: [Position] 체결청산 SHORT @ 1089.88 | PnL=-0.03pt (-3,135원) | 하드스톱(틱)
2026-08-14 11:48:55 [INFO] TRADE: [청산 완료] PnL=-0.03pt (-3,135원)
2026-08-14 11:48:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,053,027) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
```

</details>

**채널** — `TRADE`×25

**컴포넌트 상위 15** — `Chejan`×7, `Position`×5, `주문요청`×3, `Sizer`×2, `ProfitGuard`×1, `진입체크`×1, `체결진입`×1, `체결진입보정`×1, `TickTP1`×1, `TP1 부분청산`×1, `TickStop-S0C`×1, `청산 완료`×1

### `logs/20260814_WARN.log` — 23.2KB · 123행 · 최종 12:20:59

- 형식 평문 · 시각 인식 123행 · WARNING=123

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:41:15 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-14 08:41:15 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-14 08:41:16 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 156ms account=333044256
2026-08-14 08:41:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-14 08:41:21 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3375ms — live 중단 원인 분석용
  …
2026-08-14 12:05:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=277ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-14 12:13:59 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 +0.207% (임계 ±0.153%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-14 12:14:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 939ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-08-14 12:20:59 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: NORMAL → RESTRICTED (acc=0.0%)
2026-08-14 12:20:59 [WARNING] SYSTEM: [CB③-P4] acc30m 단계 전환: NORMAL → RESTRICTED (acc=0.0%)
```

</details>

**WARNING — 태그 28종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 38 | 08:41:15 | 12:00:05 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 8 | 09:01:00 | 11:23:02 | total=1118ms | S0=3ms S1=12ms S2=0ms S3=0ms S4=135ms S5=611ms S6=310ms S7=19ms S8=28ms |
| `Health` | 8 | 09:01:00 | 12:05:59 | level=WARNING degraded=OFF | latency=1118ms | quality=0.86 | cache_age=99s | exceptions_10m=0 |
| `CB⑤` | 8 | 09:01:00 | 11:23:02 | 파이프라인 1118ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 8 | 09:16:59 | 12:13:59 | 5분 누적 수익률 -0.783% (임계 ±0.474%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ChejanFlow` | 7 | 11:48:00 | 11:48:55 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='2202' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=11:48:00.800' | positi… |
| `ChejanMatch` | 7 | 11:48:00 | 11:48:55 | order_no='2202' | pending='ENTRY:SHORT qty=2 filled=0 order_no=2202 reason=진입 req_at=11:48:00.800' | pending_matched=True |
| `PendingOrder` | 6 | 11:48:00 | 11:48:55 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1089.82, 'reason': '진입', 'hint_source': '', 'atr': 1.3729, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `SHAP` | 4 | 10:51:01 | 12:14:00 | 슬로우 감지 1225ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `CB③-P4` | 4 | 10:56:59 | 12:20:59 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=13.3%) |
| `ConstOut` | 3 | 09:35:59 | 11:20:59 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| `HealthPolicy` | 3 | 09:39:00 | 11:24:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2262ms quality=1.00 cache=0s exc10m=0) | cause=S0(1915ms) |

**채널** — `SYSTEM`×115, `HEALTH`×8

**컴포넌트 상위 15** — `LiveDBG`×38, `PipePerf`×8, `Health`×8, `CB⑤`×8, `ScalerRefresh`×8, `ChejanFlow`×7, `ChejanMatch`×7, `PendingOrder`×6, `SHAP`×4, `CB③-P4`×4, `ConstOut`×3, `HealthPolicy`×3, `Canary`×2, `EntryFillFlow`×2, `ExitCooldown`×2

### `logs/20260814_SYSTEM.log` — 438.2KB · 3201행 · 최종 12:27:16

- 형식 평문 · 시각 인식 3194행 · INFO=3194, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:45 [INFO] SYSTEM: [FaultHandler] 로테이션 — 9.5MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-08-14 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=4232 | 행감지=30s all_threads=True
2026-08-14 08:40:58 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-14 08:40:58 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-14 08:40:58 [INFO] SYSTEM: 미륵이 초기화
  …
2026-08-14 12:27:13 [INFO] SYSTEM: [CybosRT-TICK] #73600 code=A0569 raw_time=122714 parsed=12:27:14 price=1090.70 vol=1 bid1=1090.62 ask1=1090.74 flag=49 side=BUY anchor=1/0
2026-08-14 12:27:16 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+270,foreign:-133,institution:-173}
2026-08-14 12:27:16 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+270,foreign:-133,institution:-173}
2026-08-14 12:27:16 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-57530 nonarb=+171342
2026-08-14 12:27:16 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-57530 nonarb=+171342
```

</details>

**채널** — `SYSTEM`×3194

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×741, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×207, `PipePerf`×207, `System`×59, `MicroRegime`×37, `OptionChain`×28, `CybosSub`×21, `IntradayRegime`×19, `ConstOut`×15, `CybosEvent`×14

### `logs/20260814_SIGNAL.log` — 417.2KB · 3575행 · 최종 12:26:59

- 형식 평문 · 시각 인식 3575행 · WARNING=1858, INFO=1717

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.416
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.441
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.428
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.420
2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.424
  …
2026-08-14 12:26:59 [INFO] SIGNAL: [MetaGate][LIVE] skip: blended=0.460 reduce_thr=0.465 take_thr=0.570 (grade=X min_conf=0.620 ens=0.365 meta_raw=0.601 ens_w=0.60)
2026-08-14 12:26:59 [INFO] SIGNAL: 앙상블: dir=-1 conf=36.5% grade=X micro=추세장
2026-08-14 12:26:59 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=3m tf=4.13 → TP1×0.5
2026-08-14 12:26:59 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.365<mc0.620)
2026-08-14 12:26:59 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=46.0% size_mult=1.00 reason=meta_skip
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1386 | 09:01:01 | 12:14:00 | 1m 'macro_vix' scale=0.0049 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 164 | 09:00:59 | 12:25:59 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 125 | 09:00:59 | 12:25:59 | ts=09:00 horizon=1m age=2m max_z=+4.58(volume_acceleration) extreme=1 |
| `Checklist` | 102 | 09:05:59 | 12:26:59 | 신뢰도 미달 34.4% < 39.8% → 강제 X등급 |
| `WeightCollapse` | 44 | 09:07:59 | 12:22:59 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 18 | 08:45:16 | 08:48:01 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `PCR-Dampen` | 12 | 09:11:59 | 11:39:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConstOut` | 4 | 09:35:59 | 11:20:59 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 3 | 09:05:59 | 11:20:59 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3488 < 필요 0.3980 (conf_floor=0.330, min_conf=0.398, span=0.0081). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3575

**컴포넌트 상위 15** — `ScalerFloor`×1452, `SIGNAL`×414, `Ensemble`×208, `ZeroDiag`×205, `FQAdj`×205, `MetaGate`×200, `Model`×188, `ScalerMonitor`×125, `Checklist`×107, `ATR-Horizon`×92, `차단`×55, `ScalerRefresh`×54, `WeightCollapse`×44, `ToxicityGate`×40, `MicroRegime`×37

### `logs/20260814_LEARNING.log` — 176.1KB · 1638행 · 최종 12:26:59

- 형식 평문 · 시각 인식 1638행 · WARNING=140, INFO=1498

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 08:40:59 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00034 auc=0.510 out_max=0.3915 (기준 auc<0.53 and span<0.020, 기저율=0.3913 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00037 auc=0.520 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3281 < conf_floor=0.3300 (span=0.00315 auc=0.573 out_max=0.3281, 기저율=0.3263 n=95) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-14 08:40:59 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3619 < conf_floor=0.3300 (n=100) → 보정 재적용
  …
2026-08-14 12:26:59 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=41.3% 예측=DN 실제=UP)
2026-08-14 12:26:59 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=44.2% UP)
2026-08-14 12:26:59 [INFO] LEARNING: [Bias⚠] 5m 적중=28%(7/25) UP=3 DN=15 FL=7 [DN편향⚠ 60%]
2026-08-14 12:26:59 [INFO] LEARNING: [MetaConf] LR[추세장] 비동기 결과 반영 (cnt=3776)
2026-08-14 12:26:59 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=25.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 140 | 08:40:59 | 12:15:59 | 축퇴 감지 — span=0.00034 auc=0.510 out_max=0.3915 (기준 auc<0.53 and span<0.020, 기저율=0.3913 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제] |

**채널** — `LEARNING`×1638

**컴포넌트 상위 15** — `LEARNING`×660, `Calibration`×272, `SGD`×207, `sigma`×194, `Bias⚠`×94, `Bias`×66, `MetaConf`×41, `ScalerWarmup`×36, `OnlineLearner`×30, `BiasReset`×9, `SHAP`×7, `GBM-64`×6, `GBM`×6, `RF`×4, `ExtremityCorrector`×2

### `logs/20260814_HEALTH.log` — 2.3KB · 17행 · 최종 12:06:59

- 형식 평문 · 시각 인식 17행 · WARNING=8, INFO=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 09:01:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1118ms | quality=0.86 | cache_age=99s | exceptions_10m=0
2026-08-14 09:01:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=440ms | quality=0.74 | cache_age=158s | exceptions_10m=0
2026-08-14 09:26:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=267ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-14 09:27:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=277ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-14 09:29:59 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 281ms (표본 20분)
  …
2026-08-14 11:12:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=311ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-14 11:23:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2829ms | quality=1.00 | cache_age=171s | exceptions_10m=0
2026-08-14 11:24:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=392ms | quality=1.00 | cache_age=46s | exceptions_10m=0
2026-08-14 12:05:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=277ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-14 12:06:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=290ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 8 | 09:01:00 | 12:05:59 | level=WARNING degraded=OFF | latency=1118ms | quality=0.86 | cache_age=99s | exceptions_10m=0 |

**채널** — `HEALTH`×17

**컴포넌트 상위 15** — `Health`×16, `HealthTrend`×1

### `logs/retrain_intraday_20260814_093659.log` — 2.4KB · 20행 · 최종 09:37:21

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 09:36:59,501 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-14 09:36:59,502 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-14 09:36:59,502 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-14 09:36:59,502 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d37417f4.json
2026-08-14 09:37:02,925 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-14 09:37:21,884 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.93s | old_acc=0.4331)
2026-08-14 09:37:21,993 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-14 09:37:21,993 [INFO] LEARNING: [Retrain] 완료 | 19.1초 | 성공=1/1 호라이즌
2026-08-14 09:37:21,994 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.5s 데이터=4800행
2026-08-14 09:37:21,995 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d37417f4.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260814_103759.log` — 2.4KB · 20행 · 최종 10:38:21

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-14 10:37:59,227 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-14 10:37:59,227 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-14 10:37:59,227 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-14 10:37:59,228 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_60c26eb0.json
2026-08-14 10:38:02,077 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-14 10:38:21,098 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=1.01s | old_acc=0.4331)
2026-08-14 10:38:21,187 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-14 10:38:21,187 [INFO] LEARNING: [Retrain] 완료 | 19.1초 | 성공=1/1 호라이즌
2026-08-14 10:38:21,189 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.0s 데이터=4800행
2026-08-14 10:38:21,190 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_60c26eb0.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) | 1 |
| 체결(`[체결진입]`) | 1 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 55 |
| 사이저 호출(`[Sizer]`) | 2 |

### 청산 1건 · 승 0 (0%) · 합계 -0.03pt (-3,135원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 11:48:55 | SHORT | -0.03 | -3,135 | 하드스톱(틱) |

**청산 사유 분포** — `하드스톱(틱)`×1

> 하드스톱·손절 계열 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:48:00 | SHORT | 2 | 1089.82 | 3m | mean-revert |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `ofi`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×2

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×2

### 차단 사유 55건 · 24종

| 건수 | 사유 |
|---|---|
| 29 | 등급X — 미통과 항목: 2_confidence |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.9pt > ATR×5.0=10.0pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.7pt > ATR×5.0=10.4pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.7pt > ATR×5.0=10.8pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.8pt > ATR×5.0=11.1pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.9pt > ATR×5.0=11.4pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.3pt > ATR×5.0=12.1pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.9pt > ATR×5.0=12.2pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.2pt > ATR×5.0=12.5pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=12.0pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=12.4pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=12.2pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.8pt > ATR×5.0=12.6pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.0pt > ATR×5.0=12.5pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.1pt > ATR×5.0=12.0pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.2pt > ATR×5.0=11.9pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.4pt > ATR×5.0=13.3pt (시가=1102.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.0pt > ATR×5.0=13.2pt (시가=1102.78 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×29

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 18건 · 최대 9125ms · 5초 초과 5건

상위 — 9125ms, 6328ms, 6312ms, 5625ms, 5046ms, 4843ms, 4781ms, 4437ms

> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **5건**이다. CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260814_WARN.log`
```
--- ConstOut ×3(표본)
09:35:59 2026-08-14 09:35:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:36:59 2026-08-14 10:36:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:20:59 2026-08-14 11:20:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×1(표본)
11:48:55 2026-08-14 11:48:55 [WARNING] SYSTEM: [CB] 연속 손절 1회
--- [ExitCooldown] ×2(표본)
11:48:55 2026-08-14 11:48:55 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:51:55)
11:48:55 2026-08-14 11:48:55 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:51:55)
--- [SHAP] 슬로우 ×4(표본)
10:51:01 2026-08-14 10:51:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1225ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
11:40:00 2026-08-14 11:40:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 926ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:51:00 2026-08-14 11:51:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 945ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:14:00 2026-08-14 12:14:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 939ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:18 2026-08-14 08:41:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:01:07 2026-08-14 09:01:07 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 9125ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:06:02 2026-08-14 09:06:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:38:01 2026-08-14 09:38:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2766ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

### `logs/20260814_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:59 2026-08-14 09:35:59 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:38:00 (const_output)
09:35:59 2026-08-14 09:35:59 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:59 2026-08-14 09:35:59 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=346ms fit=48ms total=396ms
09:36:58 2026-08-14 09:36:58 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
```

### `logs/20260814_SIGNAL.log`
```
--- ConfFloorGuard ×5(표본)
09:05:59 2026-08-14 09:05:59 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3488 < 필요 0.3980 (conf_floor=0.330, min_conf=0.398, span=0.0081). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:42:59 2026-08-14 10:42:59 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3892 ≥ 필요 0.3830
11:02:59 2026-08-14 11:02:59 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3799 < 필요 0.3830 (conf_floor=0.330, min_conf=0.383, span=0.0212). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
11:08:00 2026-08-14 11:08:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3893 ≥ 필요 0.3830
--- ConstOut ×8(표본)
09:35:59 2026-08-14 09:35:59 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:59 2026-08-14 09:35:59 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:38:01 2026-08-14 09:38:01 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:36:59 2026-08-14 10:36:59 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0040 dir=+0) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:59 2026-08-14 09:07:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=RISK_ON [WeightCollapse]
09:10:59 2026-08-14 09:10:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:13:59 2026-08-14 09:13:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:16:59 2026-08-14 09:16:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.4% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.416
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.441
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.428
08:40:42 2026-08-14 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.420
--- 안전망 ×8(표본)
09:07:59 2026-08-14 09:07:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:59 2026-08-14 09:10:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:13:59 2026-08-14 09:13:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:59 2026-08-14 09:16:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260814_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00034 auc=0.510 out_max=0.3915 (기준 auc<0.53 and span<0.020, 기저율=0.3913 n=115) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00037 auc=0.520 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3281 < conf_floor=0.3300 (span=0.00315 auc=0.573 out_max=0.3281, 기저율=0.3263 n=95) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:59 2026-08-14 08:40:59 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3198 < conf_floor=0.3300 (span=0.00464 auc=0.631 out_max=0.3198, 기저율=0.3172 n=145) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260814_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:08 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 11:48

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:15 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 08:55:16 [WARNING] scaler 노후=0h  z경고피처=19개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 08:55:16 [WARNING] scaler 노후=0h  z경고피처=19개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1 | 10:00:59 [WARNING] 5분 누적 수익률 -0.280% (임계 ±0.273%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 3 | 11:55:04 [WARNING] _tick_header 간격 5625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] |

- 이 로그 생존구간: 08:41 ~ 12:20

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260814_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:45 [INFO] 로테이션 — 9.5MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 133 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 202 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 201 | 09:54:05 [INFO] #29500 code=A0569 raw_time=95406 parsed=09:54:06 price=1088.34 vol=2 bid1=1088.32 ask1=1088.38 flag=49 side=B… |
| 12:00 | 장중 중간점 | 157 | 11:54:06 [INFO] #67500 code=A0569 raw_time=115407 parsed=11:54:07 price=1086.94 vol=1 bid1=1086.80 ask1=1086.96 flag=49 side=… |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260814_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:16 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 165 | 09:00:59 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 258 | 09:00:59 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 257 | 09:54:59 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 12:00 | 장중 중간점 | 112 | 11:55:59 [WARNING] 신뢰도 미달 39.8% < 44.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [판정] P0 없음 — 오늘 거래 자격 충족
### [신규 P1] 불변식 감시표 5행이 `미발견` — 감시표는 `dev` 세대, 코드는 `v9-dev` 세대
### [신규 P1] 참조문서가 CLAUDE.md의 「재인용 금지」 수치를 싣고 있다 — CB③ 35%
### [신규 P2] `미커밋 433건`은 전부 개행문자(CRLF) 차이 — 코웍 샌드박스 실행 시 계측 오탐
### [신규 P2] `v9-dev` 수집기에 `--pc` 가 없다 — `evidence_UNKNOWN` 이 될 뻔했다
### [관측] 프리장 CORE `above_vwap` raw_std=0.0000 — 6호라이즌 전부, 개장 11분 전 해소
### [확인 필요] 수급 3종 `+0` 의 하류 소비 — 장후로 미룸
### [참고] 본 세션은 커밋하지 않았다
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
. 완화가 아니라 98차(`f96d341`, 2026-06-02)가 **집계 대상(분모)** 을 바꿔
(FLAT 예측 제외 → 2클래스) 무정보 기준선이 33%에서 50%로 옮겨간 데 따른 동반 조정이었다.
행을 지우면 다음 세션이 같은 오해석을 다시 만든다 — 2026-07-15 Hurst 완화가 3주째
재상정된 것과 같은 사고 형태다(함정 ①·②).

**검증**: `grep -n "35%" references/invariants.md` → CB③ 관련 0건. 다음 점검이 CB③ 문구
정정을 신규 안건으로 올리지 않는지.

### [신규 P2] `미커밋 433건`은 전부 개행문자(CRLF) 차이 — 코웍 샌드박스 실행 시 계측 오탐

`git diff --ignore-all-space --numstat | wc -l` = **0**. `config/settings.py` 단독
`6241 insertions / 6241 deletions`(삽입=삭제). 워킹트리는 CRLF, 인덱스 블롭은 LF인데
윈도우 전역 `core.autocrlf=true`가 **리눅스 샌드박스에서 보이지 않아** 전 파일이 수정으로 보인다.

→ `phases.md` A-4(미커밋 변경 확인)가 무력화된다. 진짜 미커밋 수정이 433행에 숨어도 못 잡는다.
**라이브 무영향** — 윈도우 본체 git 상태는 정상일 가능성이 높다.
조치: 수집기 §2를 `미커밋 N건 (실변경 M건 · 개행차이 K건)`으로 분해하고 §11은 실변경만 판정.

### [신규 P2] `v9-dev` 수집기에 `--pc` 가 없다 — `evidence_UNKNOWN` 이 될 뻔했다

467차(`0f44477`, `--pc override`)가 `origin/dev` 전용이라 `--pc MW0601`이
`unrecognized arguments`로 죽는다. 샌드박스 호스트명은 `claude`이므로 그대로 돌면
`evidence_UNKNOWN-20260814_pre.md`가 생긴다. 이번 회차는 `platform.node()`를 대체하는
런처 래퍼로 우회해 정상 파일명을 얻었다. **1-1과 같은 뿌리**(둘 다 `dev` 전용 커밋)이므로
F-1과 같은 커밋에 묶는다. 예약작업이 매일 자동으로 도는 한 재발한다.

### [관측] 프리장 CORE `above_vwap` raw_std=0.0000 — 6호라이즌 전부, 개장 11분 전 해소

```
08:45:16 [WARNING] SIGNAL: [ScalerRefresh] 1m CORE 'above_vwap' raw_std≈0(0.0000)
                            → identity(0,1) 강제 (FLAT 100% 방지)
```
08:45:16(12건) · 08:48:01(6건) 총 18건. 08:49:59 Phase2 refit부터 소멸.
**가드가 설계대로 작동해 FLAT 고착을 막았으므로 절대원칙 §3 위반이 아니다.**
다만 프리장 30봉이 VWAP 한쪽에만 있으면 구조적으로 발생하며, Phase4(08:58:58) 이후까지
남는 날에는 09:00 첫 봉의 1m CORE가 사실상 상수로 들어간다 — 그 경우 "미통과 → 강제 X"가
무의미해진다. **1일차이므로 313차 원칙에 따라 확정 결론 보류**(O-1, 5거래일 누적, 판정 08-20).

### [확인 필요] 수급 3종 `+0` 의 하류 소비 — 장후로 미룸

`[CybosInvestor] futures supported=False … foreign=+0 individual=+0 institution=+0` 은
같은 줄에 `supported=False`·`reason=`이 있어 **로그 계층은 계측 4원칙 ② 를 지킨다.**
문제는 그 `+0`이 피처로 흐르는지다 — `institution_futures_net`이 Phase1·2·3 refit
**잔존 z경고**에 반복 등장한다(08:48:01 / 08:49:59 / 08:54:58). 상수 0이면 std≈0이어야 정상이다.
451차 `program_*` 3종(상수 0이 정상 수집으로 위장 → 폐기)과 **같은 패턴일 가능성**이 있으나
오늘 증거만으로 단정 불가. **장중 라이브 DB 금지 구간이라 `raw_features` 조회를 장후로 미뤘다**
(O-2). 2026-08-10 CB⑤ 자기유발 전례를 반복하지 않기 위함이다.

### [참고] 본 세션은 커밋하지 않았다

예약작업 지시(개장 3분 전 실행)에 따라 코드 변경·커밋·배포·재기동을 일절 하지 않았고
라이브 DB도 조회하지 않았다. 변경 파일은 아래 3개(전부 문서·산출물)뿐이다.

| 파일 | 성격 |
|---|---|
| `docs/정기점검/매일점검/MW0601-20260814-점검리포트-pre.md` | 신규(날짜본, 덮어쓰기 없음) |
| `docs/정기점검/매일점검/evidence_MW0601-20260814_pre.md` | 신규(수집기 생성) |
| `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md` | append |

```

</details>

### dev_memory/NEXT_TODO.md — 874.5KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 고도화
### 문서·운영
### 다음 거래일(2026-08-14) 관측 예정
## 2026-08-14 (MW0601 470차 — 장전 점검) 신규 항목
### Fix — 전부 **장후 적용**
### 고도화
### 문서·운영
### 다음 관측 (판정 근거)
```

미완료 체크박스 **1237건** (끝에서 30건)
```
- [ ] **G-3 수집기 적신호에서 `_tick_header` 블로킹과 `PipePerf total`을 분리** —
- [ ] **O-1 오늘 15:35 이후 장후 재점검** — `강제청산`·`daily_close_done`·`eod_retrain_done`
- [ ] **O-2 `[JointGateBlock 차단]` 건수와 `meta=` 분포** — 폴백(0.50) 비중이 오늘처럼 6/7이면
- [ ] **O-3 진입 건수 회복 여부** — 0건 2거래일 연속이면 진입0 딥다이브 절차 착수
- [ ] **O-4 `[ConfFloorGuard]` 경보 건수 vs out_max 초과 분봉 수** — 오늘 괴리(1 vs 140)가
- [ ] **O-5 `[Bias⚠] 5m` 종가 최종값 · SGD 50분 정확도** — 오늘 13:13 적중 23%(DN편향 63%) /
- [ ] **O-6 `WeightCollapse / Ensemble` 종가 비율** — 13:16 기준 106/268 = 39.6%로 CLAUDE.md
- [ ] **O-7 `_tick_header` 5초 초과 건수** — 오늘 9건(최대 11,625ms). 증가면 G-3 상향
- [ ] **404차 후속4 검증항목 "11:50~13:00 ConfFloorGuard WARNING 없음"** — 2026-08-13 실측
- [ ] **N-1 `[JointGateBlock 차단]` 중 `meta=0.50` 비율** — 3거래일 연속 80% 초과면 게이트 원인 확정.
- [ ] **N-2 진입 건수** — 0건이면 **2거래일 연속** → 진입0 딥다이브 절차 착수(460차 O-3 승계)
- [ ] **N-3 퍼널 `JointGateBlock=N` vs `TRADE.log` grep** — F-5 적용 후 정확히 일치해야 함
- [ ] **N-4 `_tick_header ≥5000ms` 건수** — 오늘 10건(460차 9건). 15건 초과면 G-3 상향
- [ ] **N-5 `[FeatureReg] 5m … 제외: ['opt_chain_pcr']` 만성도** — `최초관측` → `만성` 승격 여부.
- [ ] **N-6 `eod_retrain_done_*.txt` 의 `horizons_replaced`** — `6/6` 유지. 미달이면 익일 CB③ HALT 위험
- [ ] **N-7 `[ConfFloorGuard]` 경보 vs `conf > out_max` 분봉 수** — 오늘 1 vs 210(붕괴행 제외).
- [ ] **N-8 예약작업 `mireuk-postmarket-check` 트리거 시각** — **15:50 KST** 변경 여부(460차 F-0).
- [ ] **F-1 불변식 감시표를 브랜치 인식형으로 (P1)** — `collect_evidence.py` 불변식 스펙 dict에
- [ ] **F-1B 462·468차 스위치 5종의 `v9-dev` 체리픽 여부 심사 (P1, 별건)** —
- [ ] **F-2 `invariants.md` CB③ 35% 문구 정정 (P1)** — 33행 → `③ 30분 **방향성** 정확도
- [ ] **F-3 수집기 `--pc` / `MIREUK_PC_ID` 지원 (P2)** — 우선순위 `--pc > MIREUK_PC_ID >
- [ ] **F-4 수집기 미커밋 집계에서 개행차이 분리 (P2)** — §2를
- [ ] **G-1 브랜치 격차를 수집기 §2에 계측 (이번 주)** — 상대 브랜치 대비 ahead/behind ·
- [ ] **G-2 프리장 CORE 상수화 조기경보 (이번 주 관측 → 다음 주 판단)** —
- [ ] **G-3 `raw_features` 열별 `nunique==1` 자동 판정을 EOD에 추가** — 해당 열이 학습 X의
- [ ] **브랜치 격차 관리를 금요일점검 상설 안건으로 등록** — 개별 버그로 처리하면 계속 재발한다.
- [ ] **O-1 `above_vwap raw_std≈0` 이 Phase2(08:49) 이후까지 남는 날** — 오늘 1일차(08:49 해소).
- [ ] **O-2 `institution_futures_net` 당일 분산 — 상수 0인가** — 장후 `raw_features` 조회.
- [ ] **O-3 `[Calibration] 축퇴 감지` 일일 건수 추이** — 오늘 기동 시 **133건**(08:40:59~08:41:08).
- [ ] **O-4 오늘 15:35 이후 장후 재점검** — `강제청산`·`daily_close_done`·`eod_retrain_done`.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
이후 310/300 커밋 분기.

- [ ] **F-2 `invariants.md` CB③ 35% 문구 정정 (P1)** — 33행 → `③ 30분 **방향성** 정확도
  < **28%**` + 461차 요지 각주(98차가 FLAT 예측 제외로 **분모**를 바꿔 기준선이 2클래스 50%가
  됐고 임계도 0.35→0.28로 동반 조정). 153행은 **삭제하지 말고** "해소됨(`0424f64`)"으로
  판정만 변경 — 지우면 다음 세션이 같은 오해석을 다시 만든다. §3에 3-3항 신설.
  **근거**: CLAUDE.md 절대원칙 §2가 "재인용 금지"로 못박은 수치가 점검 참조문서에 살아 있다.
  **검증**: `grep -n "35%" references/invariants.md` → CB③ 관련 0건.

- [ ] **F-3 수집기 `--pc` / `MIREUK_PC_ID` 지원 (P2)** — 우선순위 `--pc > MIREUK_PC_ID >
  platform.node()`. override 시 헤더에 `MW0601 (override · host=claude)` 표기(폴백 가시화,
  계측 4원칙 ④). `UNKNOWN` 폴백 시 **stderr 경고**.
  **근거**: 467차(`0f44477`)가 `dev` 전용이라 `--pc`가 `unrecognized arguments`로 죽는다.
  예약작업이 코웍 샌드박스(호스트명 `claude`)에서 매일 도는 한 `evidence_UNKNOWN` 이 재발한다.
  **F-1과 같은 커밋에 묶는다.**

- [ ] **F-4 수집기 미커밋 집계에서 개행차이 분리 (P2)** — §2를
  `미커밋 N건 (실변경 M건 · 개행차이 K건)` 으로 렌더링하고 §11은 **실변경 건수로만** 판정.
  **근거**: 오늘 433건 전부 CRLF 차이(`git diff --ignore-all-space --numstat` = 0행).
  `phases.md` A-4가 무력화돼 진짜 미커밋 수정이 숨는다.

### 고도화

- [ ] **G-1 브랜치 격차를 수집기 §2에 계측 (이번 주)** — 상대 브랜치 대비 ahead/behind ·
  merge-base 날짜와 차수 · **상대 브랜치에만 있는 `config/settings.py` 상수 개수**(기능 격차
  대리지표) 3줄 추가. ⚠ fetch 실패 시 `(오래된 기준)` 표기 필요.
  **근거**: 오늘 P1 1건 + P2 1건이 **둘 다 310/300 커밋 분기의 증상**이었는데 각각을 개별
  버그로 발견하는 데 시간을 썼다. **선행: F-1.**

- [ ] **G-2 프리장 CORE 상수화 조기경보 (이번 주 관측 → 다음 주 판단)** —
  `[PreMarket] Phase4 refit 완료` 직후 CORE 피처 `raw_std`를 재확인해 0이면 개장 전 1회 경고
  (`[CoreConst] 09:00 시점 1m CORE 'above_vwap' std=0 — 이 봉의 CORE 판정은 무의미`).
  ⚠ **알림만. 차단 로직으로 승격하지 않는다** — 게이트 신설은 섀도 계측이 선행(스킬 §7-7).
  **선행: O-1 5거래일 누적.**

- [ ] **G-3 `raw_features` 열별 `nunique==1` 자동 판정을 EOD에 추가** — 해당 열이 학습 X의
  97개 동결 슈퍼셋에 포함돼 있으면 `[ConstFeature] N종` 으로 리포트. 461차 G-5(INSERT 계층)의
  DB 계층 대응물.
  ⚠ **반드시 EOD(15:45 이후)에만 돈다** — 2026-08-10 CB⑤ 자기유발 전례(전수 스캔 중
  파이프라인 7,619ms).
  ⚠ **중복 주의 — 468차 G-2("고착 지표") 구현을 `dev`에서 먼저 확인할 것.**
  **선행: O-2 조사 결과.**

### 문서·운영

- [ ] **브랜치 격차 관리를 금요일점검 상설 안건으로 등록** — 개별 버그로 처리하면 계속 재발한다.

### 다음 관측 (판정 근거)

- [ ] **O-1 `above_vwap raw_std≈0` 이 Phase2(08:49) 이후까지 남는 날** — 오늘 1일차(08:49 해소).
  5거래일 누적, **판정 예정 08-20**. 남는 날이 있으면 G-2 착수
- [ ] **O-2 `institution_futures_net` 당일 분산 — 상수 0인가** — 장후 `raw_features` 조회.
  `feature_names.pkl` 97개 슈퍼셋 포함 여부도 함께. 451차 `program_*` 전례 대조
- [ ] **O-3 `[Calibration] 축퇴 감지` 일일 건수 추이** — 오늘 기동 시 **133건**(08:40:59~08:41:08).
  전일 대비 증감 확인(403차 축퇴 가드 이후의 기지 상태인지)
- [ ] **O-4 오늘 15:35 이후 장후 재점검** — `강제청산`·`daily_close_done`·`eod_retrain_done`.
  N-1~N-3·N-5·N-7·N-8 이월분 함께 판정

```

</details>

### dev_memory/CURRENT_STATE.md — 519.4KB · 마지막 갱신 2026-08-12 18:40

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

(없음)

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 24개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260814-점검리포트-pre.md` | 31.4KB | 08-14 09:08 |
| `docs/정기점검/매일점검/evidence_MW0601-20260814_pre.md` | 47.8KB | 08-14 09:00 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 12.2KB | 08-14 07:39 |
| `docs/정기점검/매일점검/MW0601-20260813-점검리포트-post.md` | 40.6KB | 08-13 16:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20260813_post.md` | 62.3KB | 08-13 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260812_post.md` | 67.0KB | 08-12 19:35 |
| `docs/정기점검/매일점검/MW0602-20260808-점검리포트.md` | 20.8KB | 08-12 18:40 |
| `docs/정기점검/매일점검/MW0602-20260806-점검리포트.md` | 21.2KB | 08-12 18:40 |

### `docs/정기점검/금요일점검` — 45개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0602/exit_expectancy_map_20260810.md` | 1.8KB | 08-14 07:47 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_report_20260810.md` | 4.6KB | 08-14 07:39 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_metrics_20260810.json` | 2.0KB | 08-14 07:39 |
| `docs/정기점검/금요일점검/주간회의.txt` | 2.2KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.7KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/validation capain.txt` | 4.7KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/Validation/validation.txt` | 158B | 08-12 18:40 |
| `docs/정기점검/금요일점검/MW0602/validation_campaign_report_20260807.md` | 128.0KB | 08-12 18:40 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. `logs/20260814_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
7. `logs/20260814_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
8. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
9. 메인 스레드 블로킹 5초 초과 **5건** (최대 9125ms) — `CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인
10. `logs/20260814_WARN.log`: **ConstOut** 3건(표본)
11. `logs/20260814_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20260814_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20260814_SIGNAL.log`: **ConstOut** 8건(표본)
14. `logs/20260814_LEARNING.log`: **축퇴** 8건(표본)
15. 미커밋 변경 435건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260814*.log` (Windows) / `grep 강제청산 logs/*20260814*.log`*