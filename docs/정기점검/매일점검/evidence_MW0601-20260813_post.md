# 미륵이 증거 다이제스트 — 2026-08-13 / POST

- 생성 2026-08-13 16:22:47 KST · PC **MW0601** (`DeskTop-MW0601`)
- 리포 `/sessions/optimistic-brave-rubin/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260813` · `2026-08-13` · `260813` · `0813`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **18개** 파일 · 18개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260813.txt` | 28B | 08-13 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260813.txt` | 133B | 08-13 15:49 |
| `launcher_{DATE}_084000_708.log` | 1 | `logs/Mireuk_batch/launcher_20260813_084000_708.log` | 1.5MB | 08-13 15:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260813.log` | 22.4KB | 08-13 15:49 |
| `retrain_intraday_{DATE}_093758.log` | 1 | `logs/retrain_intraday_20260813_093758.log` | 4.9KB | 08-13 09:38 |
| `retrain_intraday_{DATE}_113559.log` | 1 | `logs/retrain_intraday_20260813_113559.log` | 4.9KB | 08-13 11:36 |
| `strategy_report_{DATE}_154020.txt` | 1 | `data/daily_reports/strategy_report_20260813_154020.txt` | 2.0KB | 08-13 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260813_DATA.log` | 334.9KB | 08-13 15:19 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260813_DEBUG.log` | 221.6KB | 08-13 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260813_HEALTH.log` | 3.6KB | 08-13 14:47 |
| `{DATE}_HOGA.log` | 1 | `logs/20260813_HOGA.log` | 39.7MB | 08-13 15:19 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260813_LEARNING.log` | 285.4KB | 08-13 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260813_MICRO.log` | 826.2KB | 08-13 15:19 |
| `{DATE}_PROBE.log` | 1 | `logs/20260813_PROBE.log` | 93.7KB | 08-13 15:19 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260813_SIGNAL.log` | 701.4KB | 08-13 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260813_SYSTEM.log` | 646.0KB | 08-13 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260813_TRADE.log` | 3.4KB | 08-13 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260813_WARN.log` | 13.9KB | 08-13 15:40 |

## 2. 코드·커밋 상태

- HEAD `4fae03d` · 브랜치 `v9-dev` · 미커밋 409건
```
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
 M config/krx_holidays.py
 M config/secrets_example.py
 M config/settings.py
 M config/strategy_params.py
 M config/strategy_registry.py
 M dashboard/main_dashboard.py
 M dashboard/panels/atr_ceiling_monitor_panel.py
 M dashboard/panels/atr_multiple_monitor_panel.py
 M dashboard/panels/challenger_panel.py
 M dashboard/panels/conf_trend_widget.py
 M dashboard/panels/direction_indicator_dialog.py
 M dashboard/panels/entry_horizon_monitor_panel.py
 M dashboard/panels/recalibrator_monitor_panel.py
… 외 369건
```

**당일(2026-08-13) 커밋**
```
(당일 커밋 없음)
```

**최근 커밋 12건**
```
4fae03d [MW0601] 459차: 일일 점검 스킬 MW0601 실측 정밀조정 — 태그 파싱 수정 + 거래일 요약 신설
7c0b399 [MW0602] 466차: 일일 점검 스킬 — 증거 수집기·국면별 체크리스트·차단 게이트 인벤토리
0ea204f [MW0601] 458차 후속: P0 선로드 조용한 창 + P3 경과시간 축 — 정책 변경 0건
4be1498 [MW0601] 458차: 0812 일일점검 + 이상점 3건 딥다이브·조치 — 전부 계측, 정책 변경 0건
080c982 [MW0601] 457차 후속: 고도화 G4~G9 — 전부 계측·규약, 정책 변경 0건
f6f9670 [MW0601] 457차: 0811 일일점검 + Fix 파동 W-A~W-E 구현
a675e20 [MW0601] 456차 Wave 4: 사전등록 하위 축 3종 + _spearman 동률 버그 수정
12d6d5e [MW0601] 456차 Wave 3: 학습 컷오프 메타데이터(F6) + 판정 소스 게이트(F7)
f15a23d [MW0601] 456차 Wave 2: F5 opt_pcr 진단 — 가설 반증, 조치 보류 (코드 변경 0)
267f3e6 [MW0601] 456차 Wave 1: 승패 집계 단위(F1) + SHS CORE 통과율(F2)
54ae0c3 [MW0601] 456차: 8/10 일일점검 + Fix·고도화 통합계획 + Wave 0(F8·F3) 구현
a6acc5c [MW0601] docs: QDQ 스펙 폴더명 정정 (Validation for feature → Feature integrity) + 경로 참조 갱신
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
| `CB_ACCURACY_MIN_30M` | `0.28` | `0.28` | 일치 | CB③ 임계. ⚠ CLAUDE.md 절대원칙 §2는 35%로 적혀 있다 — 코드가 0.35→0.28 완화됨. 문서 갱신 필요 |
| `CB_ACC_RESTRICTED_MIN` | `0.30` | `0.30` | 일치 | WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인 |
| `CB_ACCURACY_MIN_30M_STRICT` | `0.42` | `0.42` | 일치 | 과신 연속 시 강화 임계 (0.50→0.42 완화) |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | `False` | `False` | 일치 | ⚠ CLAUDE.md 한시예외 목록에 없는 네 번째 비활성 차단 게이트. 근거·복원조건 미기록 상태 |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | `True` | `True` | 일치 | 호가 상하한 핀 진입 차단 — 켜져 있어야 정상 |
| `HURST_SOFT_BLOCK_ENABLED` | `True` | `True` | 일치 | Hurst 소프트 차단(사이즈 0.5배). 316~318차 재보정 계열 |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | `True` | `True` | 일치 | Degraded 상태 자동진입 차단 — 켜져 있어야 정상 |
| `CB_PIPE_PAUSE_MS` | `5_000` | `5_000` | 일치 | CB⑤ 실질 구현. `CB_API_LATENCY_LIMIT` 은 Kiwoom 레거시로 Cybos에서 미사용 |
| `ENTRY_HORIZON_B1` | `3.2` | `3.2` | 일치 | 1m/3m 경계 [374차 1.5→3.5, 387차 3.5→3.2] — 드리프트 항목 |
| `ENTRY_HORIZON_B2` | `4.4` | `4.4` | 일치 | 3m/5m 경계 [374차 2.5→4.0, 387차 4.0→4.4] — 드리프트 항목 |
| `CB_DAILY_HALT_FULL_BLOCK` | `3` | `3` | 일치 | HALT 3회 → 완전 관망 |
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
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | **미기록 ⚠** |
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

> ⚠ **꺼져 있는데 근거가 기록되지 않은 차단 게이트 1개**: `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED`
> 의도한 것이면 `dev_memory/DECISION_LOG.md` 에 사유·복원조건을 적고 `config/dailycheck_targets.json` 의 `documented_disabled_flags` 에 추가하라. 의도한 것이 아니면 그 자체가 P0다.

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260813_HOGA.log` 39.7MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260813.txt`** — 28B · 08-13 15:40:20
```
2026-08-13T15:40:20.661227
```

**`data/daily_reports/strategy_report_20260813_154020.txt`** — 2.0KB · 08-13 15:40:20
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-08-13 15:40
========================================================
  버전    : v1.0  (60일차)
  판정    : UNDERPERFORM
  Live    : Sh=0.57  MDD=215.4%  WR=0.0%  PF=1.00
  롤링20일: 누적 +371426원  Sh=0.57  MDD=215.4%
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.014 (CLEAR)
  PSI/feat: cvd=0.157  vwap_position=0.014  ofi=0.002
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +1,715원  승률 55.0%  합계 +34,293원
  등급별 순EV(30일): A=+12,109원(132건,승61%)  C=-12,920원(37건,승62%)
  호라이즌별 순EV(30일): 1m=+44,452원(15건)  3m=-3,084원(90건)  5m=+12,342원(61건)  ?=-7,238원(3건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 34분  5일평균 55분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 24.1pt(5일평균 41.2pt)  1분평균변동 0.86pt(5일평균 1.05pt)
--------------------------------------------------------
  진입 퍼널(2026-08-13, 총 370분):
    FLAT 194 → conf미달 119 → CoherenceGate 25 → 게이트차단 25 → 후보 7 → 진입 0
    게이트별: 체크리스트항목미달=13  콜드스타트/기타(σ미수집)=4  콜드스타트/기타(RegimeOverride)=4  콜드스타트/기타(조건부구간)=2  시가갭(OPEN_VOLATILE)=2
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 7건
      └ 상세: JointGateBlock=6  Degraded신뢰도=1
========================================================
```

**`data/eod_retrain_done_20260813.txt`** — 133B · 08-13 15:49:06
```
completed: 2026-08-13 15:49:06
rows: 39809
cols: 97
horizons_replaced: 6/6
t_load_s: 45.7
t_retrain_s: 195.4
t_total_s: 241.6
```

_다이제스트 대상 8/14개 (중요도순). 제외: `retrain_intraday_20260813_113559.log`, `20260813_MICRO.log`, `20260813_DATA.log`, `20260813_PROBE.log`, `launcher_20260813_084000_708.log`, `20260813_DEBUG.log`_

### `logs/20260813_TRADE.log` — 3.4KB · 21행 · 최종 15:40:18

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 08:41:10 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-13 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-13 09:39:58 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,042,406) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
2026-08-13 09:39:58 [INFO] TRADE: [자동진입 차단] SHORT->SHORT 1계약 C급 (degraded_conf=40.8%, min=62.0%)
2026-08-13 09:48:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,042,406) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
  …
2026-08-13 11:29:58 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,042,406) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-13 11:29:58 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.50 tox=0.70 joint=0.350)
2026-08-13 11:37:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,042,406) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.5→3계약]
2026-08-13 11:37:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 1계약 C급 (meta=0.50 tox=0.70 joint=0.350)
2026-08-13 15:40:18 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×21

**컴포넌트 상위 15** — `Sizer`×10, `JointGateBlock 차단`×7, `ProfitGuard`×2, `Position`×1, `자동진입 차단`×1

### `logs/20260813_WARN.log` — 13.9KB · 103행 · 최종 15:40:19

- 형식 평문 · 시각 인식 97행 · WARNING=97, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 08:41:17 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-13 08:41:17 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-08-13 08:41:17 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 157ms account=333044256
2026-08-13 08:41:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-13 08:41:23 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3281ms — live 중단 원인 분석용
  …
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
════════════════════════════════════════════════════
```

</details>

**WARNING — 태그 13종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 36 | 08:41:17 | 15:09:00 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 17 | 09:05:58 | 15:02:59 | 5분 누적 수익률 +0.781% (임계 ±0.195%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 13 | 09:00:59 | 14:45:59 | level=WARNING degraded=OFF | latency=1811ms | quality=0.86 | cache_age=97s | exceptions_10m=0 |
| `PipePerf` | 6 | 09:00:59 | 11:37:01 | total=1811ms | S0=15ms S1=22ms S2=0ms S3=0ms S4=432ms S5=827ms S6=381ms S7=64ms S8=70ms |
| `CB⑤` | 6 | 09:01:00 | 11:37:01 | 파이프라인 1811ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `CB③-P4` | 6 | 10:59:58 | 15:04:59 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `HealthPolicy` | 3 | 09:01:58 | 11:37:59 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1811ms quality=0.74 cache=1s exc10m=0) | cause=S5(827ms) |
| `Canary` | 2 | 08:55:17 | 08:55:18 | scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `ConstOut` | 2 | 09:36:58 | 11:34:59 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| `SHAP` | 2 | 13:13:02 | 13:23:59 | 슬로우 감지 1284ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `ChartDBG` | 2 | 13:18:40 | 13:18:42 | paintEvent slow 62.0ms | size=1756x917 candles=20 grid=46.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `경보` | 1 | 15:40:19 | 15:40:19 | mc-conf 괴리: 최근 5거래일 평균 진입후보 55분/일 < 하한 60분 — 금일 34분. |

**채널** — `SYSTEM`×84, `HEALTH`×13

**컴포넌트 상위 15** — `LiveDBG`×36, `ScalerRefresh`×17, `Health`×13, `PipePerf`×6, `CB⑤`×6, `CB③-P4`×6, `-`×6, `HealthPolicy`×3, `Canary`×2, `ConstOut`×2, `SHAP`×2, `ChartDBG`×2, `경보`×1, `SYSTEM`×1

### `logs/20260813_SYSTEM.log` — 646.0KB · 4935행 · 최종 15:40:35

- 형식 평문 · 시각 인식 4914행 · INFO=4914, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=1408 | 행감지=30s all_threads=True
2026-08-13 08:40:59 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-13 08:40:59 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-13 08:40:59 [INFO] SYSTEM: 미륵이 초기화
2026-08-13 08:40:59 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-12) 종가 버퍼 로드: 385봉
  …
2026-08-13 15:40:20 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-08-13 15:40:20 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-13 15:40:35 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-13 15:40:35 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-13 15:40:35 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×4914

**컴포넌트 상위 15** — `CybosInvestorRaw`×1514, `CybosRT-TICK`×655, `CybosRT-ROLLOVER`×394, `BAR-CLOSE`×394, `CVD-ANCHOR`×394, `TickUI`×388, `S6Detail`×370, `PipePerf`×370, `MicroRegime`×106, `System`×98, `OptionChain`×53, `IntradayRegime`×29, `CybosSub`×21, `-`×18, `SYSTEM`×12

### `logs/20260813_SIGNAL.log` — 701.4KB · 6078행 · 최종 15:40:18

- 형식 평문 · 시각 인식 6078행 · WARNING=2841, INFO=3237

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.416
2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.441
2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.428
2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.420
2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.424
  …
2026-08-13 15:09:59 [INFO] SIGNAL: [ToxicityGate] action=reduce score=0.32 ma=0.36 size_mult=0.70 reason=toxicity_reduce
2026-08-13 15:10:11 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-13 15:40:18 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-13 15:40:18 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-13 age=31m extreme=1020 refresh=47 grade_x=144 cb3=0
2026-08-13 15:40:18 [INFO] SIGNAL: [ModelHealth] date=2026-08-13 앙상블유효가동률=78.4% | 파이프라인 370분 | ConstOut 2회/3분 {"3m": {"events": 1, "minutes": 1}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 77분 | 장중재학습 2회
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 2070 | 09:01:00 | 15:03:00 | 1m 'macro_vix' scale=0.0044 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerMonitor` | 288 | 09:00:58 | 14:48:59 | ts=09:00 horizon=1m age=2m max_z=+6.52(ret_15m) extreme=1 |
| `Model` | 228 | 09:00:58 | 14:48:01 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 163 | 09:09:58 | 15:09:59 | 신뢰도 미달 38.5% < 39.8% → 강제 X등급 |
| `WeightCollapse` | 77 | 09:07:58 | 15:07:59 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 12 | 08:45:17 | 08:45:17 | 1m CORE 'cvd_divergence' raw_std≈0(0.0359) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 2 | 09:36:58 | 11:34:59 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:05:58 | 09:05:58 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3435 < 필요 0.3980 (conf_floor=0.330, min_conf=0.398, span=0.0076). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×6078

**컴포넌트 상위 15** — `ScalerFloor`×2130, `SIGNAL`×740, `MetaGate`×393, `Ensemble`×391, `FQAdj`×368, `ZeroDiag`×345, `ScalerMonitor`×289, `Model`×246, `Checklist`×194, `ATR-Horizon`×154, `ToxicityGate`×147, `MicroRegime`×106, `차단`×104, `InstabilityGate`×99, `WeightCollapse`×77

### `logs/20260813_LEARNING.log` — 285.4KB · 2832행 · 최종 15:40:18

- 형식 평문 · 시각 인식 2832행 · WARNING=142, INFO=2690

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 08:41:01 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00491 auc=0.249 out_max=0.3272 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.526 out_max=0.3818 (기준 auc<0.53 and span<0.020, 기저율=0.3818 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00051 auc=0.490 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3264 < conf_floor=0.3300 (span=0.00086 auc=0.540 out_max=0.3264, 기저율=0.3259 n=135) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-08-13 15:40:18 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-13 15:40:18 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-13 15:40:18 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-13 15:40:18 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-13 15:40:18 [INFO] LEARNING: [Sigma] EOD sigma_20=0.12509% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 141 | 08:41:01 | 13:57:59 | 축퇴 감지 — span=0.00491 auc=0.249 out_max=0.3272 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과 |
| `DriftAdjuster` | 1 | 15:40:18 | 15:40:18 | 3일 연속 정확도 50% 미만 → alpha 0.01000→0.01000 |

**채널** — `LEARNING`×2832

**컴포넌트 상위 15** — `LEARNING`×1215, `SGD`×369, `sigma`×357, `Calibration`×277, `Bias⚠`×230, `Bias`×158, `MetaConf`×76, `OnlineLearner`×55, `ScalerWarmup`×53, `SHAP`×12, `BiasReset`×7, `ExtremityCorrector`×5, `GBM-64`×4, `GBM`×4, `RF`×3

### `logs/20260813_HEALTH.log` — 3.6KB · 27행 · 최종 14:47:00

- 형식 평문 · 시각 인식 27행 · WARNING=13, INFO=14

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 09:00:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1811ms | quality=0.86 | cache_age=97s | exceptions_10m=0
2026-08-13 09:01:58 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=384ms | quality=0.74 | cache_age=156s | exceptions_10m=0
2026-08-13 09:26:58 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=333ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-13 09:27:58 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=384ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-08-13 09:29:58 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 311ms (표본 20분)
  …
2026-08-13 13:57:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=257ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-13 14:42:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=335ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-13 14:44:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=289ms | quality=1.00 | cache_age=61s | exceptions_10m=0
2026-08-13 14:45:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=264ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-08-13 14:47:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=276ms | quality=1.00 | cache_age=57s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 13 | 09:00:59 | 14:45:59 | level=WARNING degraded=OFF | latency=1811ms | quality=0.86 | cache_age=97s | exceptions_10m=0 |

**채널** — `HEALTH`×27

**컴포넌트 상위 15** — `Health`×26, `HealthTrend`×1

### `logs/retrain_eod_20260813.log` — 22.4KB · 150행 · 최종 15:49:06

- 형식 평문 · 시각 인식 150행 · WARNING=18, INFO=132

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 15:45:04,551 [INFO] EOD_RETRAIN: =======================================================
2026-08-13 15:45:04,552 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-13 15:45:04,552 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-13 15:45:04,552 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-13 15:45:04,553 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-13 15:49:06,727 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0343 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-13 15:49:06,728 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1324 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-13 15:49:06,730 [INFO] SIGNAL: [ScalerRefresh] ts=15:49 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-08-13 15:49:06,735 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-13 15:49:06,736 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:46:01 | 15:48:02 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-13 11:05:00까지)인데 acc.txt=0.4268는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:46:01 | 15:48:02 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1636봉(88%)이 현행 학습구간 (현행 cutoff=2026-08-13 11:05:00 ≥ 홀드아웃 시작=2026-08-06 12:19:00) — 판정 보류 (구모델 pkl mtime=2026-08-13 11:36) |

**채널** — `LEARNING`×73, `SIGNAL`×49, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×20, `EOD_RETRAIN`×14, `GuardGhost`×12, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `RegimeFingerprint`×3, `WaitDC`×2, `P8`×2

### `logs/retrain_intraday_20260813_093758.log` — 4.9KB · 39행 · 최종 09:38:40

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-13 09:37:58,860 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-13 09:37:58,860 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-13 09:37:58,861 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-13 09:37:58,861 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_073727b3.json
2026-08-13 09:38:01,968 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-13 09:38:40,879 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.03s | old_acc=0.4502)
2026-08-13 09:38:40,923 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-13 09:38:40,923 [INFO] LEARNING: [Retrain] 완료 | 39.0초 | 성공=6/6 호라이즌
2026-08-13 09:38:40,924 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 42.1s 데이터=4800행
2026-08-13 09:38:40,925 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_073727b3.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 104 |
| 사이저 호출(`[Sizer]`) | 10 |

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×2, **2계약**×4, **3계약**×4

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×10

### 차단 사유 104건 · 41종

| 건수 | 사유 |
|---|---|
| 47 | 등급X — 미통과 항목: 2_confidence |
| 6 | JointGateBlock — meta=0.50 tox=0.70 joint=0.350 < 0.50 |
| 6 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 2 | ATR 0.90pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.95pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.91pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.96pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.6pt > ATR×5.0=10.6pt (시가=1059.72 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.3pt > ATR×5.0=10.6pt (시가=1059.72 반등위험) |
| 1 | 자동진입 Degraded 정책 차단 — conf=40.8% < 62.0% |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.2pt > ATR×5.0=11.0pt (시가=1059.72 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.8pt > ATR×5.0=10.6pt (시가=1059.72 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.8pt > ATR×5.0=9.0pt (시가=1059.72 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.8pt > ATR×5.0=9.1pt (시가=1059.72 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.2pt > ATR×5.0=8.1pt (시가=1059.72 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.0pt > ATR×5.0=8.0pt (시가=1059.72 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.6pt > ATR×5.0=7.9pt (시가=1059.72 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×47, `3_vwap`×13, `7_prev_bar`×9, `6_foreign`×8, `4_cvd`×7, `5_ofi`×7, `11_countertrend`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 27건 · 최대 11625ms · 5초 초과 10건

상위 — 11625ms, 8563ms, 6656ms, 6156ms, 5953ms, 5891ms, 5297ms, 5109ms

> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **10건**이다. CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260813_WARN.log`
```
--- ConstOut ×2(표본)
09:36:58 2026-08-13 09:36:58 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:34:59 2026-08-13 11:34:59 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [SHAP] 슬로우 ×2(표본)
13:13:02 2026-08-13 13:13:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1284ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:23:59 2026-08-13 13:23:59 [WARNING] SYSTEM: [SHAP] 슬로우 감지 929ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:19 2026-08-13 08:41:19 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:01:08 2026-08-13 09:01:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 11625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:06:02 2026-08-13 09:06:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:16:03 2026-08-13 09:16:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5109ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260813_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:58 2026-08-13 09:36:58 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:39:00 (const_output)
09:36:58 2026-08-13 09:36:58 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:58 2026-08-13 09:36:58 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=83ms fit=84ms total=202ms
09:37:58 2026-08-13 09:37:58 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- [CB] ×2(표본)
15:40:18 2026-08-13 15:40:18 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:18 2026-08-13 15:40:18 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [Shutdown] ×2(표본)
15:40:20 2026-08-13 15:40:20 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:35 2026-08-13 15:40:35 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:20 2026-08-13 15:40:20 [INFO] SYSTEM: [Notify] ℹ️ [15:40:20] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:20 2026-08-13 15:40:20 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:35 2026-08-13 15:40:35 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260813_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:05:58 2026-08-13 09:05:58 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3435 < 필요 0.3980 (conf_floor=0.330, min_conf=0.398, span=0.0076). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×6(표본)
09:36:58 2026-08-13 09:36:58 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:37:58 2026-08-13 09:37:58 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
11:34:59 2026-08-13 11:34:59 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
11:34:59 2026-08-13 11:34:59 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=5m const_out=['5m'] (섀도 기록만, 정책 무변경)
--- WeightCollapse ×8(표본)
09:07:58 2026-08-13 09:07:58 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:58 2026-08-13 09:10:58 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:13:59 2026-08-13 09:13:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:16:59 2026-08-13 09:16:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.416
08:40:43 2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.441
08:40:43 2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.428
08:40:43 2026-08-13 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.420
--- 안전망 ×8(표본)
09:07:58 2026-08-13 09:07:58 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:58 2026-08-13 09:10:58 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:13:59 2026-08-13 09:13:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:59 2026-08-13 09:16:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260813_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:01 2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00491 auc=0.249 out_max=0.3272 (기준 auc<0.53 and span<0.020, 기저율=0.3250 n=80) → 보정 미적용, raw 통과
08:41:01 2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.526 out_max=0.3818 (기준 auc<0.53 and span<0.020, 기저율=0.3818 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:01 2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00051 auc=0.490 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:01 2026-08-13 08:41:01 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3264 < conf_floor=0.3300 (span=0.00086 auc=0.540 out_max=0.3264, 기저율=0.3259 n=135) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260813_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:10 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:18 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260813_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:17 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=15개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1 | 10:05:58 [WARNING] 5분 누적 수익률 +0.426% (임계 ±0.271%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 14:00 | 장중 후반 · 장중 재학습 | 2 | 13:56:59 [WARNING] level=WARNING degraded=OFF | latency=279ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 3 | 15:04:59 [WARNING] acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:40:19 [WARNING] mc-conf 괴리: 최근 5거래일 평균 진입후보 55분/일 < 하한 60분 — 금일 34분. |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260813_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=1408 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 116 | 08:49:20 [INFO] alive ticks=580 code=A0568 close=1060.28 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 168 | 08:54:13 [INFO] #1300 code=A0568 raw_time=85415 parsed=08:54:15 price=1065.68 vol=1 bid1=1065.60 ask1=1065.70 flag=49 side=BU… |
| 10:00 | 장중 초반 | 161 | 09:54:17 [INFO] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+581,foreign:+1249,institution:-1916} |
| 12:00 | 장중 중간점 | 150 | 11:54:02 [INFO] #38800 code=A0568 raw_time=115404 parsed=11:54:04 price=1075.82 vol=1 bid1=1075.60 ask1=1075.84 flag=49 side=… |
| 14:00 | 장중 후반 · 장중 재학습 | 163 | 13:54:04 [INFO] #52600 code=A0568 raw_time=135405 parsed=13:54:05 price=1076.10 vol=9 bid1=1076.10 ask1=1076.18 flag=50 side=… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 148 | 15:04:04 [INFO] alive ticks=62163 code=A0568 close=1062.02 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 76 | 15:12:15 [INFO] alive ticks=63851 code=A0568 close=1066.02 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 30 | 15:36:17 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:36:17 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260813_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:17 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0359) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 116 | 09:00:58 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 262 | 09:00:58 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 183 | 09:54:58 [WARNING] 신뢰도 미달 31.6% < 39.8% → 강제 X등급 |
| 12:00 | 장중 중간점 | 120 | 11:54:58 [WARNING] 신뢰도 미달 31.4% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 278 | 13:55:04 [WARNING] 신뢰도 미달 35.5% < 41.6% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 59 | 15:04:59 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:18 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-08-13 (MW0601 460차 — 일일 점검 / 예약 "장후"였으나 실제 13:13 장중 실행)
### [발견] 진입 0건의 결정적 차단점은 JointGateBlock이며 7건 중 6건이 MetaGate 무정보 폴백에 의한 산술적 차단
### [발견] ConfFloorGuard가 축퇴 가드로 우회된 보정기의 출력상한을 근거로 판정하고 하루 종일 래치된다
### [확인] 404차 후속4(ConfFloorGuard 존 축 오탐 억제)가 라이브에서 정상 작동한다
### [문서] 절대원칙 §2 CB③ 임계가 코드와 다르다 (35% vs 0.28)
### [미결 이월] `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED = False` 근거 미기록 (2일째)
### [운영] 예약작업 `mireuk-postmarket-check`가 13:13에 실행됐다 — 장후 항목 검증 불가
### [참고] 오늘 정상 확인 항목
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
하고 True면
`zone_allows_entry=False`와 동일하게 **판정 스킵 + 상태 무갱신**. `learning/calibration.py`가
우회 사실을 `is_bypassed` 프로퍼티로 노출(현재는 WARNING 문자열로만 존재).
**Why**: 경보 자체는 진입을 막지 않아 거래 영향은 0이지만, 이 경보는 "진입 봉쇄"로 읽히고
오늘은 사실이 아니었다. 반대로 진짜 스케일 불일치(07-30 사고 유형)를 가릴 수 있다.
`NEXT_TODO.md`에 *"ConfFloorGuard 경보와 중복되지 않는지 — 둘은 다른 레이어(보정기 vs
앙상블)의 같은 사실을 본다"* 로 이미 등록돼 있던 항목에 오늘 처음 **정량 근거
(경보 1건 vs 반증 140건)** 가 붙었다.
**How to apply**: 장후 적용. ⚠ **`main.py` 앙상블 호출부는 2곳(주경로·masked fallback)이며
둘 다 kwarg를 넘겨야 한다** — 404차가 명시한 함정으로, 한 곳만 넘기면 폴백 분에 재오탐한다.
**검증**: 오늘 09:05:58 시퀀스 재현 시 WARNING → DEBUG. **대조군 필수** — 축퇴가 아닌
정상 fitted 보정기 저장본으로 WARNING이 여전히 나는지 확인(404차 검증 방식 재사용).
경보를 없애는 대신 DEBUG + 별도 카운터로 남겨 EOD 1줄 요약 권고.

### [확인] 404차 후속4(ConfFloorGuard 존 축 오탐 억제)가 라이브에서 정상 작동한다

11:50~12:55 구간 24개 분봉이 `min_conf=62.0%`로 차단됐는데 이는 결함이 아니라 `TIME_ZONES`
미정의 공백(`OTHER` 존, `allow_new_entry=False`, min_conf 0.65→MC_ABS_CEIL 0.62 클램프)의
**설계된 점심 블랙아웃**이다. 그리고 그 구간에 **ConfFloorGuard 경보가 0건** —
`NEXT_TODO.md`의 *"11:50~13:00 ConfFloorGuard WARNING이 없는지 확인"* 항목이 충족됐다
(완료 표기는 사용자 확인 후). 431차의 사이징 중립화도 `size_mult_sizing=1.00(무정보폴백→중립)`
로그로 라이브 반영을 확인했다.

### [문서] 절대원칙 §2 CB③ 임계가 코드와 다르다 (35% vs 0.28)

`config/settings.py:CB_ACCURACY_MIN_30M = 0.28`인데 CLAUDE.md 절대원칙 §2 ③은
"30분 정확도 < 35%"로 적혀 있다. **코드는 바꾸지 않는다**(임계 변경은 전 채널 판정에 영향).
`git log -S "CB_ACCURACY_MIN_30M"`으로 완화 커밋·차수를 특정해 CLAUDE.md 문구를 정정할 것.

### [미결 이월] `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED = False` 근거 미기록 (2일째)

`config/settings.py:4813`. 차단 게이트 27개 중 **유일하게 비활성 근거가 CLAUDE.md에도
DECISION_LOG에도 없다**. CB②·CB③-P4·FP-CRITICAL과 달리 **복원 조건이 없어 실전 전환
체크리스트에서 누락된다.** `config/dailycheck_targets.json`이 일부러 미결로 남겨둔 항목이며
08-12 수집기도 같은 지적을 했다. 조치: 도입·비활성 커밋 특정 → 사유·복원조건 기록 →
CLAUDE.md 한시예외 **네 번째 항목**으로 추가 → 실전 전환 기준 **⑨**로 승격(권고).

### [운영] 예약작업 `mireuk-postmarket-check`가 13:13에 실행됐다 — 장후 항목 검증 불가

국면 인자는 `post` 고정인데 트리거 시각이 13:13이라 15:10 강제청산·15:18 안전망·
15:40 자가학습 마감·15:45 EOD 재학습이 **아직 발생하지 않았다**. 또한 이 시각은
"장중 라이브 DB 분석 금지"(08:45~15:35) 구간이라 `predictions.db`·`trades.db` 사후검증도
수행하지 않았다(456차 자가유발 CB⑤ 전례 회피). 수집기는 로그만 읽고 DB를 열지 않으며,
실행(13:13:48) 이후 WARN 신규 0건으로 자가유발이 없었음을 확인했다.
**결정**: 예약 트리거를 **평일 15:50 KST**로 변경 권고(EOD 재학습 완료 마커 이후).
코드 변경 아님 — 사용자 확인 필요.

### [참고] 오늘 정상 확인 항목

- 브랜치 `v9-dev`(MW0601 규약 일치), 설정 불변식 21행 전부 일치
- 장중 재학습 2회 성공(09:37:58·11:35:59, 각 `성공=6/6 호라이즌`, `Python 3.10.20 64-bit` — 191차 결정대로 정상)
- 매분 루프 08:55~13:13 구간 10분 이상 공백 0건 / CB⑤ 경고 6건 전부 `CB_PIPE_PAUSE_MS=5,000` 미만 → 미발동이 정상
- 크래시·COM 오류 0건(절대원칙 ④·⑤)
- **본 세션 코드 변경 0줄, git 커밋 없음**

```

</details>

### dev_memory/NEXT_TODO.md — 842.7KB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-06-25 (243차 이후)
### DONE
### NEXT (Stage 2 ~ Phase 3)
## 2026-08-13 (MW0601 460차 — 일일 점검)
### NEXT (Fix)
### NEXT (고도화)
### 다음 거래일 관측 (판정 근거)
### 충족 근거 확보(완료 표기는 사용자 확인 후)
```

미완료 체크박스 **1183건** (끝에서 30건)
```
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
- [ ] **F-0 예약작업 `mireuk-postmarket-check` 트리거를 15:50 KST로 변경** — 현재 13:13에
- [ ] **F-1 JointGateBlock 무정보 폴백 플래그 분리 계측 (P1)** — MetaGate가
- [ ] **F-2 ConfFloorGuard 축퇴-우회 축 오탐 억제 (P1)** —
- [ ] **F-3 CLAUDE.md 절대원칙 §2 ③ CB③ 임계 문구 정정 (P2)** — "30분 정확도 < 35%" →
- [ ] **F-4 `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED = False` 근거 확정 (P2, 2일째 이월)** —
- [ ] **G-1 `ReachabilityGuard` — "산술적 도달 불가" 조합을 게이트 체인 전체로 일반화** —
- [ ] **G-2 `HEALTH_DEGRADED_MIN_CONF = 0.62`의 현행 conf 스케일 정합성 재확인** —
- [ ] **G-3 수집기 적신호에서 `_tick_header` 블로킹과 `PipePerf total`을 분리** —
- [ ] **O-1 오늘 15:35 이후 장후 재점검** — `강제청산`·`daily_close_done`·`eod_retrain_done`
- [ ] **O-2 `[JointGateBlock 차단]` 건수와 `meta=` 분포** — 폴백(0.50) 비중이 오늘처럼 6/7이면
- [ ] **O-3 진입 건수 회복 여부** — 0건 2거래일 연속이면 진입0 딥다이브 절차 착수
- [ ] **O-4 `[ConfFloorGuard]` 경보 건수 vs out_max 초과 분봉 수** — 오늘 괴리(1 vs 140)가
- [ ] **O-5 `[Bias⚠] 5m` 종가 최종값 · SGD 50분 정확도** — 오늘 13:13 적중 23%(DN편향 63%) /
- [ ] **O-6 `WeightCollapse / Ensemble` 종가 비율** — 13:16 기준 106/268 = 39.6%로 CLAUDE.md
- [ ] **O-7 `_tick_header` 5초 초과 건수** — 오늘 9건(최대 11,625ms). 증가면 G-3 상향
- [ ] **404차 후속4 검증항목 "11:50~13:00 ConfFloorGuard WARNING 없음"** — 2026-08-13 실측
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
CCURACY_MIN_30M = 0.28`. `git log -S "CB_ACCURACY_MIN_30M"`으로 완화 커밋·차수
  특정 후 근거와 함께 기재. **코드는 바꾸지 않는다.**
- [ ] **F-4 `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED = False` 근거 확정 (P2, 2일째 이월)** —
  `git log -S "TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED" -- config/settings.py`로 비활성 커밋 특정
  → DECISION_LOG에 사유·복원조건 → CLAUDE.md 한시예외 **네 번째 항목** 추가 →
  `config/dailycheck_targets.json:documented_disabled_flags`에 추가 →
  실전 전환 기준 **⑨**로 승격 여부 결정(권고: 승격).

### NEXT (고도화)

- [ ] **G-1 `ReachabilityGuard` — "산술적 도달 불가" 조합을 게이트 체인 전체로 일반화** —
  오늘 같은 형태가 두 축에서 동시 발생(ConfFloorGuard `out_max 0.3435 < min_conf 0.3980` /
  JointGate `0.50×0.70=0.35 < 0.50`)했는데 전자만 전용 가드가 있어 후자 7건이 조용히 지나갔다.
  경보 전용(새 차단 아님)이므로 섀도 승격 불필요. 대상: JointGate, Degraded min_conf,
  CoherenceGate(min=0.60). 오전 소표본 오탐 회피를 위해 **09:30 이후부터 평가**.
  **선행: F-1**(폴백/계산 구분 없이는 상한 정의가 무의미).
- [ ] **G-2 `HEALTH_DEGRADED_MIN_CONF = 0.62`의 현행 conf 스케일 정합성 재확인** —
  비붕괴 앙상블 conf 최대치: 08-07 58.8 / 08-10 70.4 / 08-11 65.7 / 08-12 56.3 / 08-13 53.6.
  **5일 중 3일은 62%에 한 번도 도달하지 못했다** → 그런 날의 Degraded는 "고신뢰 신호만 허용"이
  아니라 사실상 전면 차단이다(오늘 09:39:58 `conf=40.8% < 62.0%` 차단 실측).
  1차는 계측만(Degraded 진입 시 `reachable=Y/N` 로그). 임계 재정의(min_conf 배수 또는 당일
  분위수)는 **주간회의 안건 — 자동 변경 금지**(§9 사전등록).
  ⚠ 2026-07-31 `CONF_SCALE_BREAKS` 이후 표본만 사용할 것.
- [ ] **G-3 수집기 적신호에서 `_tick_header` 블로킹과 `PipePerf total`을 분리** —
  오늘 UI 블로킹 9건이 5초를 넘었으나 파이프라인 최대는 2,664ms였는데, 수집기 적신호 9번이
  둘을 같은 축으로 읽어 "CB⑤ 기준 초과"로 오탐했다.
  `.claude/skills/mireuk-daily-check/scripts/collect_evidence.py` 규칙 수정, UI 축 임계 8초 권고.

### 다음 거래일 관측 (판정 근거)

- [ ] **O-1 오늘 15:35 이후 장후 재점검** — `강제청산`·`daily_close_done`·`eod_retrain_done`
  3종 존재 확인. EOD 재학습 `성공=N/6`. **판정 예정 2026-08-13 15:50**
- [ ] **O-2 `[JointGateBlock 차단]` 건수와 `meta=` 분포** — 폴백(0.50) 비중이 오늘처럼 6/7이면
  F-1 우선순위 상향. `joint_gate_shadow` min_samples=20까지 13건 부족
- [ ] **O-3 진입 건수 회복 여부** — 0건 2거래일 연속이면 진입0 딥다이브 절차 착수
- [ ] **O-4 `[ConfFloorGuard]` 경보 건수 vs out_max 초과 분봉 수** — 오늘 괴리(1 vs 140)가
  재현되면 F-2 확정 근거
- [ ] **O-5 `[Bias⚠] 5m` 종가 최종값 · SGD 50분 정확도** — 오늘 13:13 적중 23%(DN편향 63%) /
  SGD 25.3% → 13:16 적중 30% / SGD 32.0%로 회복 중. 종가 < 30% 지속이면 STEP 2/5 딥다이브
- [ ] **O-6 `WeightCollapse / Ensemble` 종가 비율** — 13:16 기준 106/268 = 39.6%로 CLAUDE.md
  평시 21~22%의 약 2배. 단 반일치 + ConstOut 구간 포함이라 **종가 재집계 전 확정 결론 보류**
- [ ] **O-7 `_tick_header` 5초 초과 건수** — 오늘 9건(최대 11,625ms). 증가면 G-3 상향

### 충족 근거 확보(완료 표기는 사용자 확인 후)

- [ ] **404차 후속4 검증항목 "11:50~13:00 ConfFloorGuard WARNING 없음"** — 2026-08-13 실측
  0건으로 충족. 기존 체크박스에 DONE 표기 여부는 사용자 판단

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

### `docs/정기점검/매일점검` — 23개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/evidence_UNKNOWN-20260813_post.md` | 62.4KB | 08-13 16:21 |
| `docs/정기점검/매일점검/MW0601-20260813-점검리포트.md` | 30.7KB | 08-13 13:21 |
| `docs/정기점검/매일점검/evidence_MW0601-20260813_post.md` | 57.4KB | 08-13 13:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20260812_post.md` | 67.0KB | 08-12 19:35 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 11.6KB | 08-12 18:40 |
| `docs/정기점검/매일점검/MW0602-20260808-점검리포트.md` | 20.8KB | 08-12 18:40 |
| `docs/정기점검/매일점검/MW0602-20260806-점검리포트.md` | 21.2KB | 08-12 18:40 |
| `docs/정기점검/매일점검/MW0602-20260805-점검리포트.md` | 35.0KB | 08-12 18:40 |

### `docs/정기점검/금요일점검` — 42개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/주간회의.txt` | 2.2KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.7KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/validation capain.txt` | 4.7KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/Validation/validation.txt` | 158B | 08-12 18:40 |
| `docs/정기점검/금요일점검/MW0602/validation_campaign_report_20260807.md` | 128.0KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/MW0602/validation_campaign_report_20260801.md` | 38.2KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/MW0602/validation_campaign_metrics_20260807.json` | 71.3KB | 08-12 18:40 |
| `docs/정기점검/금요일점검/MW0602/validation_campaign_metrics_20260801.json` | 26.1KB | 08-12 18:40 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 차단 게이트 `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` = False 인데 **근거 미기록** — 의도한 예외인지 확인하고 DECISION_LOG에 남길 것
2. 장후인데 **강제청산(15:10) 흔적을 못 찾았다** — 절대원칙 1 확인 필요 (포지션이 없었을 수도 있다. 원본으로 구분할 것)
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. **진입 0건** — 차단 104건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라)
5. 메인 스레드 블로킹 5초 초과 **10건** (최대 11625ms) — `CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인
6. `logs/20260813_WARN.log`: **ConstOut** 2건(표본)
7. `logs/20260813_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20260813_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260813_SIGNAL.log`: **ConstOut** 6건(표본)
10. `logs/20260813_LEARNING.log`: **축퇴** 8건(표본)
11. 미커밋 변경 409건
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260813*.log` (Windows) / `grep 강제청산 logs/*20260813*.log`*