# 미륵이 증거 다이제스트 — 2026-08-20 / INTRA

- 생성 2026-08-20 12:27:12 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/stoic-wonderful-thompson/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260820` · `2026-08-20` · `260820` · `0820`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260820.json` | 243B | 08-20 12:27 |
| `launcher_{DATE}_084001_9654.log` | 1 | `logs/Mireuk_batch/launcher_20260820_084001_9654.log` | 946.0KB | 08-20 12:26 |
| `retrain_intraday_{DATE}_093700.log` | 1 | `logs/retrain_intraday_20260820_093700.log` | 2.4KB | 08-20 09:37 |
| `retrain_intraday_{DATE}_101100.log` | 1 | `logs/retrain_intraday_20260820_101100.log` | 2.4KB | 08-20 10:11 |
| `retrain_intraday_{DATE}_110200.log` | 1 | `logs/retrain_intraday_20260820_110200.log` | 2.4KB | 08-20 11:02 |
| `retrain_intraday_{DATE}_114103.log` | 1 | `logs/retrain_intraday_20260820_114103.log` | 2.4KB | 08-20 11:41 |
| `{DATE}_DATA.log` | 1 | `logs/20260820_DATA.log` | 182.2KB | 08-20 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260820_DEBUG.log` | 125.6KB | 08-20 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260820_HEALTH.log` | 2.8KB | 08-20 12:07 |
| `{DATE}_HOGA.log` | 1 | `logs/20260820_HOGA.log` | 32.1MB | 08-20 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260820_LEARNING.log` | 175.5KB | 08-20 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260820_MICRO.log` | 636.7KB | 08-20 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260820_PROBE.log` | 57.5KB | 08-20 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260820_SIGNAL.log` | 364.1KB | 08-20 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260820_SYSTEM.log` | 474.3KB | 08-20 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260820_TRADE.log` | 5.4KB | 08-20 11:42 |
| `{DATE}_WARN.log` | 1 | `logs/20260820_WARN.log` | 25.1KB | 08-20 12:23 |

## 2. 코드·커밋 상태

- HEAD `7a59796` · 브랜치 `v9-dev` · 미커밋 459건
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
 M config/strategy_params.py
… 외 419건
```

**당일(2026-08-20) 커밋**
```
7a59796 [MW0601] 480차 후속4: F-2 가드가 감시 개시를 파일에 남긴다 — 사이드카 자신의 생존 증거
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
```

**최근 커밋 12건**
```
7a59796 [MW0601] 480차 후속4: F-2 가드가 감시 개시를 파일에 남긴다 — 사이드카 자신의 생존 증거
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
091783c [MW0601] 480차 후속3: DECISION_LOG 테스트 집계 정정 — 576 passed / 신규 38건
ac73a18 [MW0601] 480차 후속2: F-5 폴백 경고 테스트를 전체 스위트에서도 통과하게 — caplog 제거
af2dbcc [MW0601] 480차 후속: F-2 수동 실행(--once)은 경보 마커를 남기지 않는다
c30e414 [MW0601] 480차 (3/3): 로드맵·dev_memory — 전환기준 ② 선행 ⓑ 추가 + 워치독 임계 26주 WFA 편입
9bb58eb [MW0601] 480차 (2/3): 0819 리포트 F-3·F-4·G-2 — ofi_norm 분포 프로브 + WaitDC 폴백 마커 + 로그 종료시각 기준선
ea60409 [MW0601] 480차 (1/3): 0819 리포트 F-2·G-1·F-5 — 프로세스 밖 FLAT 가드 + 하트비트 파일 + 진입 파라미터 승계
2330a66 [MW0601] 479차 후속: 배포 검증에서 발견 — pipeperf(SYSTEM 소급 glob, dev 전용) 예외 등록 + 문서 dev 특이점 2건
fdd80f5 [MW0601] 479차 (3/3): v9-dev 전용분 — 476차 스킬/설정 + test_476 + dev_memory 기록
49980d9 [MW0601] 479차 (2/3): 로그 채널별 차등 보관 — 측정 근거 + 압축 단계 + EOD 체인 발화 배선
59c516a [MW0601] 479차 (1/3): 476차 보관정책 재설계분 커밋 — monthly_cleanup 안전화 + 보관정책 문서
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

### 차단 게이트 전수 인벤토리 — 30개 중 **8개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
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
| `FORCE_FLAT_GUARD_ENABLED` | True | — |
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
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260820_HOGA.log` 32.1MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `retrain_intraday_20260820_110200.log`, `retrain_intraday_20260820_114103.log`, `20260820_MICRO.log`, `20260820_DATA.log`, `20260820_PROBE.log`, `launcher_20260820_084001_9654.log`, `20260820_DEBUG.log`_

### `logs/20260820_TRADE.log` — 5.4KB · 38행 · 최종 11:42:03

- 형식 평문 · 시각 인식 38행 · INFO=38

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:24 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-20 08:41:29 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-20 10:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-20 10:05:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-20 10:06:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-20 10:57:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,313,671) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.0→3계약]
2026-08-20 11:37:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,313,671) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.0→2계약]
2026-08-20 11:37:00 [INFO] TRADE: [JointGateBlock 차단] LONG 1계약 C급 (meta=0.50 tox=0.70 joint=0.350)
2026-08-20 11:42:03 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,313,671) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-20 11:42:03 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.59 tox=0.70 joint=0.415)
```

</details>

**채널** — `TRADE`×38

**컴포넌트 상위 15** — `Sizer`×9, `Chejan`×9, `Position`×6, `주문요청`×3, `체결진입보정`×2, `JointGateBlock 차단`×2, `ProfitGuard`×1, `진입체크`×1, `체결진입`×1, `손절1차 분할체결`×1, `손절1차 조기축소`×1, `TickStop-S0C`×1, `청산 완료`×1

### `logs/20260820_WARN.log` — 25.1KB · 130행 · 최종 12:23:05

- 형식 평문 · 시각 인식 130행 · WARNING=130

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-20 08:41:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-20 08:41:40 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 4125ms — live 중단 원인 분석용
  …
2026-08-20 12:11:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=22 watchdog_alerted=[]
2026-08-20 12:11:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.0ms | size=1756x917 candles=206 grid=0.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=0.0 cross=15.0 | slow_cnt=2 total_cnt=46
2026-08-20 12:11:38 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 32.0ms | size=1756x917 candles=207 grid=0.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=0.0 axes=16.0 cross=0.0 | slow_cnt=3 total_cnt=141
2026-08-20 12:12:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.489% (임계 ±0.228%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-20 12:23:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

</details>

**WARNING — 태그 24종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 37 | 08:41:32 | 12:23:05 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 10 | 09:01:02 | 11:42:03 | total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| `Health` | 10 | 09:01:02 | 12:06:02 | level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0 |
| `CB⑤` | 10 | 09:01:02 | 11:42:03 | 파이프라인 2353ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ChejanFlow` | 9 | 10:55:01 | 10:56:05 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='2883' | pending='ENTRY:LONG qty=3 filled=0 order_no=? reason=진입 req_at=10:55:00.852' | positio… |
| `ChejanMatch` | 9 | 10:55:01 | 10:56:05 | order_no='2883' | pending='ENTRY:LONG qty=3 filled=0 order_no=2883 reason=진입 req_at=10:55:00.852' | pending_matched=True |
| `ScalerRefresh` | 8 | 09:13:00 | 12:12:00 | 5분 누적 수익률 +0.643% (임계 ±0.585%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PendingOrder` | 6 | 10:55:00 | 10:56:05 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1085.54, 'reason': '진입', 'hint_source': '', 'atr': 1.8071, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `HealthPolicy` | 5 | 09:02:00 | 11:43:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2353ms quality=0.74 cache=1s exc10m=0) | cause=S5(1200ms) |
| `ConstOut` | 4 | 09:36:00 | 11:40:02 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| `EntryFillFlow` | 3 | 10:55:01 | 10:55:01 | actual_side='LONG' | after='LONG 3계약 @ 1085.42' | applied_side='LONG' | before='LONG 3계약 @ 1085.54' | fill_no='' | fill_price=1085.42 | fill_qty=1 | order_no='2883' | pending='ENTRY:LONG qty=3 filled=1 order_no=2883 reason=진입 req_at=10:55:… |
| `ChartDBG` | 3 | 12:09:37 | 12:11:38 | paintEvent slow 63.0ms | size=1756x917 candles=20 grid=47.0 spans=0.0 candles=0.0 dir=0.0 regime=0.0 markers=16.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1 |

**채널** — `SYSTEM`×120, `HEALTH`×10

**컴포넌트 상위 15** — `LiveDBG`×37, `PipePerf`×10, `Health`×10, `CB⑤`×10, `ChejanFlow`×9, `ChejanMatch`×9, `ScalerRefresh`×8, `PendingOrder`×6, `HealthPolicy`×5, `ConstOut`×4, `EntryFillFlow`×3, `ChartDBG`×3, `CB③-P4`×2, `ExitSendOrderResult`×2, `CB`×2

### `logs/20260820_SYSTEM.log` — 474.3KB · 3415행 · 최종 12:27:01

- 형식 평문 · 시각 인식 3408행 · INFO=3408, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:40:50 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=13140 | 행감지=30s all_threads=True
2026-08-20 08:41:10 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-20 08:41:10 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-20 08:41:10 [INFO] SYSTEM: 미륵이 초기화
2026-08-20 08:41:10 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-19) 종가 버퍼 로드: 296봉
  …
2026-08-20 12:27:00 [INFO] SYSTEM: [MicroRegime] 횡보장 → 추세장 (ADX=26.5, ATR=1.374, ratio=0.79)
2026-08-20 12:27:00 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=9ms meta_gate=4ms gates=0ms imp=0ms shap=3ms corr=9ms dash_ui=0ms tail=14ms
2026-08-20 12:27:00 [INFO] SYSTEM: [PipePerf][DBG] total=388ms | S0=22ms S1=19ms S2=13ms S3=0ms S4=101ms S5=185ms S6=40ms S7=5ms S8=2ms
2026-08-20 12:27:01 [INFO] SYSTEM: [CybosRT-TICK] #89600 code=A0569 raw_time=122701 parsed=12:27:01 price=1079.40 vol=1 bid1=1079.36 ask1=1079.48 flag=49 side=BUY anchor=1/0
2026-08-20 12:27:12 [INFO] SYSTEM: [TickUI] alive ticks=89645 code=A0569 close=1079.38
```

</details>

**채널** — `SYSTEM`×3408

**컴포넌트 상위 15** — `CybosRT-TICK`×901, `CybosInvestorRaw`×822, `TickUI`×222, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `S6Detail`×207, `PipePerf`×207, `System`×59, `RegimeFingerprint`×38, `MicroRegime`×38, `OptionChain`×27, `CybosSub`×21, `ConstOut`×20, `CybosEvent`×18

### `logs/20260820_SIGNAL.log` — 364.1KB · 3170행 · 최종 12:27:00

- 형식 평문 · 시각 인식 3170행 · WARNING=1401, INFO=1769

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
  …
2026-08-20 12:27:00 [WARNING] SIGNAL: [ScalerMonitor] ts=12:26 horizon=30m age=1m max_z=+12.89(ofi_reversal_speed) extreme=1
2026-08-20 12:27:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-08-20 12:27:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=40.2% grade=X regime=RISK_ON
2026-08-20 12:27:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=40.2% grade=X micro=추세장
2026-08-20 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.402<mc0.620) | 참고: 이상값피처(ofi_reversal_speed(candidate))
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 864 | 09:01:02 | 12:26:01 | 1m 'macro_vix' scale=0.0136 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 180 | 08:45:03 | 12:26:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0379) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 107 | 09:01:00 | 12:27:00 | ts=09:00 horizon=1m age=2m max_z=-15.07(institution_futures_net) extreme=3 |
| `Model` | 106 | 09:01:00 | 12:25:01 | 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 96 | 09:06:00 | 12:24:02 | 신뢰도 미달 34.9% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 43 | 09:08:00 | 12:23:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 4 | 09:36:00 | 11:39:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:06:00 | 09:06:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3170

**컴포넌트 상위 15** — `ScalerFloor`×888, `SIGNAL`×414, `MetaGate`×274, `ScalerRefresh`×209, `Ensemble`×206, `FQAdj`×205, `ZeroDiag`×161, `Model`×136, `Checklist`×124, `ScalerMonitor`×107, `ATR-Horizon`×93, `차단`×75, `ToxicityGate`×56, `WeightCollapse`×43, `MicroRegime`×38

### `logs/20260820_LEARNING.log` — 175.5KB · 1638행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1638행 · WARNING=135, INFO=1503

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:12 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.499 out_max=0.3750 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-20 08:41:14 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00062 auc=0.538 out_max=0.3559 (n=135) → 보정 재적용
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00047 auc=0.523 out_max=0.3646 (기준 auc<0.53 and span<0.020, 기저율=0.3643 n=140) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-08-20 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.1057% buf_n=20 nonzero=20 prev_p=1079.90 cur_p=1079.48
2026-08-20 12:27:00 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=39.1% FL)
2026-08-20 12:27:00 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=39.2% DN)
2026-08-20 12:27:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=46.1% UP)
2026-08-20 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=21.9%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 135 | 08:41:14 | 11:56:02 | 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1638

**컴포넌트 상위 15** — `LEARNING`×664, `Calibration`×263, `SGD`×207, `sigma`×194, `Bias⚠`×101, `Bias`×60, `MetaConf`×41, `OnlineLearner`×34, `ScalerWarmup`×29, `BiasReset`×11, `SHAP`×8, `GBM-64`×8, `GBM`×8, `RF`×5, `ExtremityCorrector`×2

### `logs/20260820_HEALTH.log` — 2.8KB · 21행 · 최종 12:07:01

- 형식 평문 · 시각 인식 21행 · WARNING=10, INFO=11

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 09:01:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0
2026-08-20 09:02:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=588ms | quality=0.74 | cache_age=148s | exceptions_10m=0
2026-08-20 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=315ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-20 09:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=264ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-20 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 315ms (표본 20분)
  …
2026-08-20 11:12:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=325ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-20 11:42:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3114ms | quality=1.00 | cache_age=29s | exceptions_10m=0
2026-08-20 11:43:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=348ms | quality=1.00 | cache_age=87s | exceptions_10m=0
2026-08-20 12:06:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=306ms | quality=1.00 | cache_age=184s | exceptions_10m=0
2026-08-20 12:07:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=305ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 10 | 09:01:02 | 12:06:02 | level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0 |

**채널** — `HEALTH`×21

**컴포넌트 상위 15** — `Health`×20, `HealthTrend`×1

### `logs/retrain_intraday_20260820_093700.log` — 2.4KB · 20행 · 최종 09:37:24

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 09:37:00,660 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-20 09:37:00,661 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-20 09:37:00,661 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-20 09:37:00,661 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d6528b03.json
2026-08-20 09:37:03,822 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-20 09:37:23,973 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=1.01s | old_acc=0.4217)
2026-08-20 09:37:24,062 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-20 09:37:24,062 [INFO] LEARNING: [Retrain] 완료 | 20.2초 | 성공=1/1 호라이즌
2026-08-20 09:37:24,063 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 23.4s 데이터=4800행
2026-08-20 09:37:24,064 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d6528b03.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260820_101100.log` — 2.4KB · 20행 · 최종 10:11:21

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 10:11:00,465 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-20 10:11:00,466 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-20 10:11:00,466 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-20 10:11:00,466 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7f2494c0.json
2026-08-20 10:11:03,150 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-20 10:11:21,646 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.90s | old_acc=0.4217)
2026-08-20 10:11:21,733 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-20 10:11:21,734 [INFO] LEARNING: [Retrain] 완료 | 18.6초 | 성공=1/1 호라이즌
2026-08-20 10:11:21,734 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.3s 데이터=4800행
2026-08-20 10:11:21,735 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7f2494c0.json
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
| 차단(`[차단]`) | 75 |
| 사이저 호출(`[Sizer]`) | 9 |

### 청산 1건 · 승 0 (0%) · 합계 -2.92pt (-147,628원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 10:56:05 | LONG | -2.92 | -147,628 | 하드스톱(틱) |

**청산 사유 분포** — `하드스톱(틱)`×1

> 하드스톱·손절 계열 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:55:00 | LONG | 3 | 1085.54 | 3m | neutral |

계약수 분포 — 3계약×1

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×2, **2계약**×1, **3계약**×6

실제 진입 계약수 — **3계약**×1

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×9

### 차단 사유 75건 · 22종

| 건수 | 사유 |
|---|---|
| 29 | 등급X — 미통과 항목: 2_confidence |
| 7 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 7 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 7 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 6 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 11_countertrend |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.1pt > ATR×5.0=13.4pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.6pt > ATR×5.0=12.8pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.3pt > ATR×5.0=12.8pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.1pt > ATR×5.0=12.3pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.2pt > ATR×5.0=13.1pt (시가=1050.50 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.7pt > ATR×5.0=13.1pt (시가=1050.50 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign |
| 1 | 청산 후 쿨다운 — 124초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `3_vwap`×34, `6_foreign`×34, `2_confidence`×29, `5_ofi`×22, `7_prev_bar`×18, `4_cvd`×17, `11_countertrend`×11

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `연속 손절 1회` ×1
- `연속 손절 2회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 13건 · 최대 4750ms · 5초 초과 0건

상위 — 4750ms, 4547ms, 4453ms, 4406ms, 4344ms, 4063ms, 3500ms, 3422ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260820_WARN.log`
```
--- ConstOut ×4(표본)
09:36:00 2026-08-20 09:36:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:10:00 2026-08-20 10:10:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:01:00 2026-08-20 11:01:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:40:02 2026-08-20 11:40:02 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×2(표본)
10:55:17 2026-08-20 10:55:17 [WARNING] SYSTEM: [CB] 연속 손절 1회
10:56:05 2026-08-20 10:56:05 [WARNING] SYSTEM: [CB] 연속 손절 2회
--- [ExitCooldown] ×2(표본)
10:56:05 2026-08-20 10:56:05 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:59:05)
10:56:05 2026-08-20 10:56:05 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:59:05)
--- 메인 스레드 블로킹 ×8(표본)
08:41:35 2026-08-20 08:41:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:01:03 2026-08-20 09:01:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4344ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:11:02 2026-08-20 09:11:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:38:03 2026-08-20 09:38:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

### `logs/20260820_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:00 2026-08-20 09:36:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:38:00 (const_output)
09:36:00 2026-08-20 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:00 2026-08-20 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=424ms fit=39ms total=467ms
09:37:00 2026-08-20 09:37:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:01:00 2026-08-20 09:01:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.008 level=0 (heartbeat)
09:07:00 2026-08-20 09:07:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
09:12:00 2026-08-20 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
09:18:00 2026-08-20 09:18:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
```

### `logs/20260820_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:06:00 2026-08-20 09:06:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:36:00 2026-08-20 09:36:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:36:00 2026-08-20 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:00 2026-08-20 09:37:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:38:02 2026-08-20 09:38:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:08:00 2026-08-20 09:08:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:11:00 2026-08-20 09:11:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.7% grade=X regime=RISK_ON [WeightCollapse]
09:14:00 2026-08-20 09:14:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=RISK_ON [WeightCollapse]
09:17:00 2026-08-20 09:17:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.3% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
--- 안전망 ×8(표본)
09:08:00 2026-08-20 09:08:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:11:00 2026-08-20 09:11:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:14:00 2026-08-20 09:14:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:17:00 2026-08-20 09:17:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260820_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.499 out_max=0.3750 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:41:14 2026-08-20 08:41:14 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00062 auc=0.538 out_max=0.3559 (n=135) → 보정 재적용
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00047 auc=0.523 out_max=0.3646 (기준 auc<0.53 and span<0.020, 기저율=0.3643 n=140) → 보정 미적용, raw 통과 [기존 fitted 해제]
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260820_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:24 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 3 | 10:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |

- 이 로그 생존구간: 08:41 ~ 11:42

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260820_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:32 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 7 | 09:01:02 [WARNING] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 09:01:02 [WARNING] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| 10:00 | 장중 초반 | 1 | 10:01:00 [WARNING] 5분 누적 수익률 +0.354% (임계 ±0.326%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1 | 12:06:02 [WARNING] level=WARNING degraded=OFF | latency=306ms | quality=1.00 | cache_age=184s | exceptions_10m=0 |

- 이 로그 생존구간: 08:41 ~ 12:23

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260820_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:50 [INFO] 활성화 | file=logs\crash_fault.log PID=13140 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 193 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 212 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 171 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260820_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:03 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0379) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 93 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0366) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 179 | 08:55:04 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0428) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 167 | 09:54:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=6, group=short) | VWAP pos=+2.000 need <0 (SHORT) bull_exh=0.00 |
| 12:00 | 장중 중간점 | 90 | 11:56:02 [WARNING] 신뢰도 미달 35.3% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| 20260817 | 17:58 | 로그 본문 |
| 20260814 | 15:40 | 로그 본문 |
| 20260813 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260820** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [1] 476차 §6-1 미결(차등 보관) 측정으로 종결 — 3계층 확정
## 2026-08-20 (MW0601 481차 — 장전 점검 · 분석만, 코드 0건)
### [1] 개장 첫 봉 `institution_futures_net` z=-15.07 — 프리장 0-충전이 만든 z 폭발 (P1, 신규)
### [2] 단기 CORE `ofi_norm` identity 강제율 2거래일 연속 100% (P1, 임계 접근)
### [3] `CybosProbe` 프리장 실패의 정체 확정 — "TR 없음"이 아니라 "프리장 미제공" (P2, 0819 2-1 이월)
### [4] 수집기 오탐 3종 — 재발 카운트 갱신 (P2)
### [5] EOD 체인이 08-19 동결을 견디고 완주했다 — 문서화 안 된 복원력 (관측)
### [6] 정상 확인 (이상점 아님 — 재상정 방지용 기록)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
그에 `-2147221008` **0건**. 1거래일 `logs/crash_fault.log`
0xC0000409 감시 필수(COM 스레드 경계).

### [4] 수집기 오탐 3종 — 재발 카운트 갱신 (P2)

- **CRLF 미커밋 457건**(0819 2-2, **2일차**): `git diff --ignore-cr-at-eol --stat` **출력 없음**
  = 실질 소스 변경 **0건**. 남는 것은 미추적 18건(본 점검 산출물)뿐. 어제는 실질 4건이
  묻혀 있었으므로 오늘 무해했던 건 우연이다.
- **불변식 `미발견` 5행**(0819 1-3, **7일차**): 5개 상수가 `collect_evidence.py` 기대표
  안에만 존재하고 repo 소스 어디에도 없음을 실측 확인(관련 키워드 검색도 0건).
  단 `_pre_retrain_done` **런타임 플래그는 살아 있고 정상 동작**(`main.py:791/4730/7299/11523`,
  오늘 08:55:03 `[PreRetrain] … 스킵` 로그로 실증). §11 자동 적신호 7건 중 5칸 상시 점유.
- **§7 로그 종료시각 델타 -399분**(**신규**): 480차 G-2가 장후 조기종료용으로 넣은 대조가
  국면 분기 없이 `pre`에서도 출력된다. 09:01은 종료시각이 아니라 현재시각이다.

**결정**: F-4(브랜치 스코프 분리) · F-5(CRLF 내성 + §7 국면 스코프)로 등록. 장후 적용.
**Why**: 적신호 7칸 중 6칸이 오탐이면 진짜 신호가 밀려난다(계측 4원칙 ③ 취지).

### [5] EOD 체인이 08-19 동결을 견디고 완주했다 — 문서화 안 된 복원력 (관측)

**증상(좋은 쪽)**: 2026-08-19 메인 프로세스는 13:41부터 동결이었는데
`logs/retrain_eod_20260819.log`는 **15:45:03 시작 → 16:08:45 정상 완료**
(`Python : 3.10.20 64-bit`, `[P8] session_state p8_last_success_date + eod_retrain_ok_date
기록 완료`)이고 모델 12종 mtime이 16:05~16:08이다. 그 덕에 오늘 08:55:03
`[PreRetrain] … 1영업일 전(2026-08-19) EOD 재학습 성공 → 스킵`이 성립했고,
CLAUDE.md가 경고한 **"재학습 실패 → 모델 미교체 → CB③ HALT" 연쇄가 발생하지 않았다.**

**결정**: G-1로 등록 — ① `CLAUDE.md` 운영 환경 절에 "EOD 체인은 장중 본체와 별도 프로세스이며
본체 이상 시에도 독립 완주한다"를 명기(지금은 py310_64 분리 이유가 OOM 회피로만 적혀 있어
이 복원력이 읽는 사람에게 안 보인다) ② **역방향 계측** — `campaign_steps.py` EOD 체인 끝에
`data/eod_retrain_ok_YYYYMMDD.txt` 마커, 런처가 08:41 기동 시 날짜 검사 →
`[EODGuard] 전일 EOD 미완료 — 모델 노후 N일` WARN.

**Why**: 지금 역방향(EOD 실패 + 본체 정상)을 잡는 곳은 08:55 `[PreRetrain]` 한 곳뿐이고
그때는 이미 개장 5분 전이다. 마커 검사를 08:41로 당기면 +14분을 번다.

**검증**: 다음 26주간 `[EODGuard]` 발화 건수와 09:00 전 조치로 이어진 비율.

### [6] 정상 확인 (이상점 아님 — 재상정 방지용 기록)

- 브랜치 `v9-dev` ✅ (ahead 7 · behind 0). ⚠ 로컬 7커밋 미push — MW0602가 480차 후속을 못 본다.
- py37_32 32-bit ✅ / PID 13140 단일 ✅ / Cybos `connect=Y/Y balance=Y/Y` ✅
- 08:45:03 실시간 **사전** 구독(09:00보다 15분 앞섬) ✅ / 08:58:06 레짐 `RISK_ON` ✅
- OptionChain 5242종목, 09:01:51 `target=24 valid=24 PCR=0.921 GEX=12.20B` ✅
- `[RegimeFingerprint] PSI=0.008 level=0` ✅ / 09:01:02 CB⑤ 경고는 **장시작 버스트 예외(임계 9s)** 정상
- FZ-1 워치독 라이브 배선 확인 — `heartbeat_MW0601_20260820.json`:
  `beat_age_sec 0.3 / strikes 0 / fired false / window ["09:00","15:45"]`.
  **FZ-11(오늘자 오탐 0건 확인) 관측 1일차 진행 중** — 장후에 종일 `beat_age` 확인.
- 한시예외 재검토 기한 경과 **0건** (CB② `2026-08-29` 미도래, 9일 남음).
- `MAX_CONTRACTS=3`은 431차 배포분 — 실전전환 ⑧ **조건 2 이미 충족**. 재상정 금지.
- `OPT50029` 미출현은 정상(Cybos 경로, OPT50029는 Kiwoom 전용 — 0819 2-3 등록).

```

</details>

### dev_memory/NEXT_TODO.md — 1007.7KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 477차 후속5 — 476차 §3 고도화 방안 조사 결과 (MW0601, 2026-08-18 · 조사만)
### 477차 후속6 — GR-1 구현 완료 (MW0601, 2026-08-18)
### 477차 후속7 — GR-3 구현 완료 (MW0601, 2026-08-18)
### 478차 — 장전 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 478차 후속 — 장중 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 478차 후속 — 08-19 메인 스레드 라이브락(미종료 사고) Fix (MW0601, 상세: MW0601-20260819-미종료-딥다이브.md §5)
### 478차 후속2 — 장후 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 481차 — 장전 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
```

미완료 체크박스 **1515건** (끝에서 30건)
```
- [ ] **R-후보(5거래일 누적 후 판정)** — 등급 인플레(원시 C → A급) 축. 오늘 2건 승1 패1이고
- [ ] **[실전전환기준 ②에 선행 확인사항 추가 제안]** — *"장중 프로세스 정지 감지·조치 경로 1회 실측"*.
- [ ] **[로드맵] 26주 WFA 재검증 항목에 라이브니스 워치독 임계(180초) 편입 제안** —
- [ ] **[08-29 CB② 보강]** — 오늘 **CASE-02(11:11 SHORT 3계약)가 한 포지션으로 `연속 손절 1회`·`2회`를
- [ ] **F-2 유지 — 후속2 고유 항목.** 딥다이브 P0-1은 스스로 *"15:10 이후 동결이면 런처가
- [ ] **G-1 조정** — 딥다이브 P0-1의 `_main_beat`를 파일로도 내보내는 형태로, **P0-1과 같은 커밋**.
- [ ] **G-2 병합** — 딥다이브 **P2-2**(장중 로그 침묵)와 같은 커밋. 잡는 구간이 다르다 —
- [ ] **딥다이브 고유 항목은 그대로 채택** — P1-1(COM 타이머 위상 분리 +17s) ·
- [ ] **FZ-1L (P1) 라이브 리허설** — 하드 종료 → 런처 RESTART_LOOP 재기동 → 세션 복원의
- [ ] **FZ-10 (주간회의 안건) 26주 WFA 재검증 항목 편입** — FZ-1L을 471차 G-3(15:10 경로
- [ ] **FZ-8 (선택) 풀 덤프 WinDbg 분석** — `c:	mp\mireuk_freeze_20260819_pid21612.dmp`
- [ ] **FZ-11 (관찰, 08-20) 워치독 오탐 0건 확인** — `logs/crash_fault.log`의 `[TS]` 줄에서
- [ ] **[MW0601 479차] HOGA 압축본 190일 컷 면제 해제 여부 — 주간회의 안건.**
- [ ] **[MW0601 479차] 월간 로그 정리 배선 라이브 검증** — 2026-08-21(금) EOD 로그에서
- [ ] **[MW0601 479차] MW0602 배포 확인** — dev 체리픽 push 완료 후, MW0602에서
- [ ] **`raw_data.db`(508MB)·`shap_tracker.db`(132MB) 보관정책 부재** — 별도 조사
- [ ] **F-2 (P1, 최우선 · 코드 변경 없음) `ofi_norm` 분포 프로브 실행** —
- [ ] **F-1 (P1) 프리장 수급 미측정 플래그 + 스케일러 제외 섀도** —
- [ ] **F-3 (P2, 0819 2-1 이월 · 2일차) CybosProbe CoInitialize + 실패사유 3분류** —
- [ ] **F-4 (P2, 0819 F-1 이월 · 7일차) 수집기 브랜치 스코프 분리** —
- [ ] **F-5 (P2) 수집기 CRLF 내성 + §7 국면 스코프** —
- [ ] **G-1 (이번 주) EOD 체인 프로세스 독립성 명문화 + 역방향 계측** —
- [ ] **G-2 (이번 주, F-5와 병합) 개장 첫봉 z 프로파일 상설 계측** —
- [ ] **G-3 (다음 주, F-2 결과 확인 후) CORE 스케일러 폴백률 일일 집계** —
- [ ] **O-1 (장중) `[IntradayRegime]` 종일 전이 횟수** — 09:01:59 `NORMAL → CRASH
- [ ] **O-2 (장중·장후) `institution_futures_net` max_z 재출현 여부** — 09:00 봉 한정인지,
- [ ] **O-3 (장후) `institution_futures_net` σ_floor 0.15 실적용 여부** —
- [ ] **O-4 (장후) `ofi_norm` identity 종일 발동률** — 90% 이상이면 **P-4 2일차 확정**,
- [ ] **O-5 (장후) FZ-11 워치독 오탐 0건** — `heartbeat_MW0601_20260820.json` /
- [ ] **O-6 (장후) 로컬 7커밋 push** — `origin/v9-dev` 대비 ahead 7. MW0602가 480차 후속을
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
*"]` 추가.
      해당 없는 행은 `미발견`이 아니라 `해당없음(브랜치 dev 전용)` + **§11 적신호 제외**.
      기본값은 `["*"]`여야 한다(진짜 상수 소멸을 놓치지 않도록).
      검증: §11 적신호 7건 → **2건**(축퇴 + 미커밋).
- [ ] **F-5 (P2) 수집기 CRLF 내성 + §7 국면 스코프** —
      미커밋 집계를 `git diff --ignore-cr-at-eol --numstat` 기준으로(⚠ `--name-only`는 blob 차이만으로도 200여 파일을 나열해 정반대 결론이 난다), 원 카운트와 **둘 다 표기**(계측 4원칙 ④).
      §7 "로그 종료시각 5거래일 대조"는 **`phase == "post"` 에서만** 출력(480차 G-2가 장전에도 나와
      매일 "-399분" 거짓 적색을 만든다).

#### 고도화

- [ ] **G-1 (이번 주) EOD 체인 프로세스 독립성 명문화 + 역방향 계측** —
      ① `CLAUDE.md` 운영 환경 절에 "EOD 재학습 체인은 장중 본체와 별도 프로세스, 본체 이상 시에도
      독립 완주" 명기(2026-08-19 동결에도 15:45→16:08 완주해 CB③ HALT를 막았다 — 우연이 아니라 구조).
      ② `scripts/campaign_steps.py` EOD 끝에 `data/eod_retrain_ok_YYYYMMDD.txt` 마커 →
      런처 08:41 기동 시 날짜 검사 → `[EODGuard] 전일 EOD 미완료 — 모델 노후 N일` WARN(**경보만, 차단 없음**).
      효과: 현행 08:55 `[PreRetrain]` 대비 **+14분** 조기 인지.
- [ ] **G-2 (이번 주, F-5와 병합) 개장 첫봉 z 프로파일 상설 계측** —
      수집기 §5에 ① 오늘 `ts=09:00` `max_z` 값·피처·`extreme` ② 직전 5거래일 중앙값과 델타
      ③ **포화 상수 필터**(3거래일 이상 소수점까지 동일하면 `(포화)` 표기 후 2순위).
      근거: 1-1의 -15.07은 손 대조로만 발견됐고, `quality_investor_stale z=+22.34`(4일 연속 동일)가
      매일 최댓값을 차지해 진짜 변화를 가린다.
- [ ] **G-3 (다음 주, F-2 결과 확인 후) CORE 스케일러 폴백률 일일 집계** —
      수집기 §5에 CORE 피처별 `identity 강제 / 전체 호라이즌 검사` %를 직전 2거래일과 나란히.
      90% 3연속이면 §11 적신호. **P-4는 문턱만 있고 계기가 없다** — FP-CRITICAL이 "저장 함수가
      호출된 적 없어 2개월 PSI=0.0"이었던 것과 같은 형태.
      ⚠ 선행 조건은 F-2다 — 원인 모르는 채 비율만 자동화하면 "숫자는 있는데 뭘 할지 모르는" 채널이 는다.
      ⚠ 계측일 뿐 **CORE 처분이 아니다**(절대원칙 §3, 주간회의 안건).

#### 다음 국면(장중·장후) 관측 항목

- [ ] **O-1 (장중) `[IntradayRegime]` 종일 전이 횟수** — 09:01:59 `NORMAL → CRASH
      (day=-0.61% atr=1.00 z=3)` 로 개장 2분 만에 전이. P-5(40회 이상 2일 연속 → G-7 착수)
      대상이며 08-19가 반일 51회였다. **장전 표본으로 결론 금지.**
- [ ] **O-2 (장중·장후) `institution_futures_net` max_z 재출현 여부** — 09:00 봉 한정인지,
      일중에도 나오는지. 일중에도 나오면 1-1의 "프리장 warmup" 가설이 틀린 것이다.
- [ ] **O-3 (장후) `institution_futures_net` σ_floor 0.15 실적용 여부** —
      오늘 `[ScalerFloor]` 발동 6종에 이 피처가 **없다**. σ ≥ 0.15였다면 -15.07을 만들려면
      원값 편차 2.26 이상이어야 한다. 스케일러 상태 조회 필요 → 장후.
- [ ] **O-4 (장후) `ofi_norm` identity 종일 발동률** — 90% 이상이면 **P-4 2일차 확정**,
      다음 거래일이 3일차. (장전 42/42 = 100%)
- [ ] **O-5 (장후) FZ-11 워치독 오탐 0건** — `heartbeat_MW0601_20260820.json` /
      `logs/crash_fault.log` `[TS]` 의 `beat_age` 가 장중 내내 0~5초인지. 30초 이상 튀면
      임계 재검토 전에 **그 블로킹의 정체부터 밝힐 것**.
- [ ] **O-6 (장후) 로컬 7커밋 push** — `origin/v9-dev` 대비 ahead 7. MW0602가 480차 후속을
      아직 못 본다. NEXT_TODO `[MW0601 479차] MW0602 배포 확인` 과 묶어서 처리.

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

### `data/heartbeat_MW0601_20260820.json` — 243B · 08-20 12:27:11
```json
{
 "pid": 13140,
 "written_at": "2026-08-20T12:27:11",
 "beat_epoch": 1787196428.092033,
 "beat_age_sec": 3.0,
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

### `docs/정기점검/매일점검` — 53개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260820-점검리포트-pre.md` | 36.8KB | 08-20 09:15 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_pre.md` | 49.0KB | 08-20 09:01 |
| `docs/정기점검/매일점검/MW0601-20260819-미종료-딥다이브.md` | 26.0KB | 08-19 17:07 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-post.md` | 42.9KB | 08-19 16:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_post.md` | 63.9KB | 08-19 16:22 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-intra.md` | 33.7KB | 08-19 12:42 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_intra.md` | 59.8KB | 08-19 12:26 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-pre.md` | 33.8KB | 08-19 09:11 |

### `docs/정기점검/금요일점검` — 53개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.json` | 7.6KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.md` | 3.8KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260814.md` | 163.4KB | 08-14 15:49 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. `logs/20260820_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
7. `logs/20260820_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
8. `logs/20260820_WARN.log`: **ConstOut** 4건(표본)
9. `logs/20260820_SYSTEM.log`: **ConstOut** 8건(표본)
10. `logs/20260820_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20260820_SIGNAL.log`: **ConstOut** 8건(표본)
12. `logs/20260820_LEARNING.log`: **축퇴** 8건(표본)
13. 미커밋 변경 459건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260820*.log` (Windows) / `grep 강제청산 logs/*20260820*.log`*