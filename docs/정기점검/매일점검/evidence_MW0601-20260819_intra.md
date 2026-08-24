# 미륵이 증거 다이제스트 — 2026-08-19 / INTRA

- 생성 2026-08-19 12:26:50 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/pensive-dazzling-pasteur/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260819` · `2026-08-19` · `260819` · `0819`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_22417.log` | 1 | `logs/Mireuk_batch/launcher_20260819_084001_22417.log` | 1009.8KB | 08-19 12:26 |
| `retrain_intraday_{DATE}_093601.log` | 1 | `logs/retrain_intraday_20260819_093601.log` | 2.4KB | 08-19 09:36 |
| `retrain_intraday_{DATE}_101001.log` | 1 | `logs/retrain_intraday_20260819_101001.log` | 2.4KB | 08-19 10:10 |
| `retrain_intraday_{DATE}_104301.log` | 1 | `logs/retrain_intraday_20260819_104301.log` | 2.4KB | 08-19 10:43 |
| `retrain_intraday_{DATE}_114901.log` | 1 | `logs/retrain_intraday_20260819_114901.log` | 2.4KB | 08-19 11:49 |
| `{DATE}_DATA.log` | 1 | `logs/20260819_DATA.log` | 184.1KB | 08-19 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260819_DEBUG.log` | 127.2KB | 08-19 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260819_HEALTH.log` | 2.7KB | 08-19 12:19 |
| `{DATE}_HOGA.log` | 1 | `logs/20260819_HOGA.log` | 30.2MB | 08-19 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260819_LEARNING.log` | 170.0KB | 08-19 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260819_MICRO.log` | 603.1KB | 08-19 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260819_PROBE.log` | 57.5KB | 08-19 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260819_SIGNAL.log` | 386.3KB | 08-19 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260819_SYSTEM.log` | 484.0KB | 08-19 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260819_TRADE.log` | 9.6KB | 08-19 11:42 |
| `{DATE}_WARN.log` | 1 | `logs/20260819_WARN.log` | 50.8KB | 08-19 12:18 |

## 2. 코드·커밋 상태

- HEAD `624a275` · 브랜치 `v9-dev` · 미커밋 461건
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
… 외 421건
```

**당일(2026-08-19) 커밋**
```
(당일 커밋 없음)
```

**최근 커밋 12건**
```
624a275 [MW0601] 477차 후속7: GR-3 — ProfitGuard 차단 로그에 일일손익 원천 토큰(gross/net)
389a3e5 [MW0601] 477차 후속6: GR-1 — ProfitGuard L1 래치 기회비용 소급 계측 스크립트 신설
108f940 [MW0601] 477차 후속5: 476차 §3 고도화 방안 구현이득 조사 — G-2 라이브 배선 기각, 한계 기회비용 0 실측
1863a43 [MW0601] 477차 후속4: 문서 정리 — 475~477차 점검 산출물 + dev_memory + 08-29 안건 2건
ae5c29b [MW0601] 477차 후속3: 476차 F-3 재설계 + G-1 — TP1 훅 qty>=2 확장(경로 분리) + 포지션 MFE 소급 계측
a5f4b4c [MW0601] 477차 후속2: 476차 F-4 — daily_broker_pnl 단위 명시(gross/수수료/net) + 휴장일 유령 행 가드
710c1c5 [MW0601] 477차 후속: 476차 F-1+F-5 — DriftAdjuster 포화 가시화 + RegimeFingerprint PSI 매분 영속
cf0f803 [MW0601] 477차: ModelLive DB 승격(n_eff·교차표·σ·clean 4열) + 방향정렬 edge + ghost_bypass clean 어긋남 관측
7dc14bc [MW0601] 474차: D9 딥다이브 — §3 정합화 + 라우팅 밴드 채널 + 30m 역필터 기각
68ff91c [MW0601] 473차: 구조적 교착 해소 — 테스트 오염 · F-8 배선/판정 · D9 도달성 · D8 인프라
e995764 [MW0601] 472차: UI 좌상단 "Phase 3 예정" 배지 → Phase 5 전환 게이트 자동 판정
f911e8d [MW0601] 471차 후속8: G-3 강제청산 리허설 26주 WFA 편입 + 로드맵 반영 + dev_memory
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

_본문 미열람(설정): `20260819_HOGA.log` 30.2MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `retrain_intraday_20260819_104301.log`, `retrain_intraday_20260819_114901.log`, `20260819_MICRO.log`, `20260819_DATA.log`, `20260819_PROBE.log`, `launcher_20260819_084001_22417.log`, `20260819_DEBUG.log`_

### `logs/20260819_TRADE.log` — 9.6KB · 77행 · 최종 11:42:02

- 형식 평문 · 시각 인식 77행 · INFO=77

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-19 08:41:18 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-19 09:49:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,507) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-19 09:49:01 [INFO] TRADE: [진입체크] LONG→LONG 3계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas✅ coun✅ | conf=40.7%
2026-08-19 09:49:01 [INFO] TRADE: [Chejan] 상태=접수 주문번호=814 code=A0569 방향=LONG 체결=3 미체결=0
  …
2026-08-19 11:42:01 [INFO] TRADE: [주문요청] TP2 청산 SHORT 1계약 @ 1016.88 체결대기
2026-08-19 11:42:02 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2212 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-19 11:42:02 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2212 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-19 11:42:02 [INFO] TRADE: [Position] 체결청산 SHORT @ 1016.9 | PnL=+3.24pt (+160,470원) | TP2(전량)
2026-08-19 11:42:02 [INFO] TRADE: [청산 완료] PnL=+3.24pt (+160,470원)
```

</details>

**채널** — `TRADE`×77

**컴포넌트 상위 15** — `Chejan`×22, `Position`×16, `주문요청`×8, `Sizer`×6, `체결진입`×5, `진입체크`×3, `청산 완료`×3, `JointGateBlock 차단`×3, `TickTP1`×2, `TickStop-S0C`×2, `체결진입보정`×2, `ProfitGuard`×1, `TP1 부분청산`×1, `체결청산-부분`×1, `손절1차 분할체결`×1

### `logs/20260819_WARN.log` — 50.8KB · 233행 · 최종 12:18:01

- 형식 평문 · 시각 인식 233행 · ERROR=1, WARNING=232

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-19 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-19 08:41:27 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3594ms — live 중단 원인 분석용
  …
2026-08-19 11:50:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2735ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
2026-08-19 11:51:01 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2100ms quality=1.00 cache=0s exc10m=1) | cause=S0(1798ms)
2026-08-19 11:52:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4891ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
2026-08-19 12:08:01 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.346% (임계 ±0.231%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-19 12:18:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=183s | exceptions_10m=0
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `FixB` | 1 | 09:49:01 | 09:49:01 | open_position 실패 direction=LONG status_before=LONG err=이미 포지션 보유 중 |

<details><summary>ERROR/FixB 원문 1건</summary>

```
2026-08-19 09:49:01 [ERROR] SYSTEM: [FixB] open_position 실패 direction=LONG status_before=LONG err=이미 포지션 보유 중
```

</details>

**WARNING — 태그 28종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 73 | 08:41:21 | 11:52:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 22 | 09:49:01 | 11:42:02 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='814' | pending='ENTRY:LONG qty=3 filled=0 order_no=? reason=진입 req_at=09:49:01.502' | position… |
| `ChejanMatch` | 22 | 09:49:01 | 11:42:02 | order_no='814' | pending='ENTRY:LONG qty=3 filled=0 order_no=814 reason=진입 req_at=09:49:01.502' | pending_matched=True |
| `PendingOrder` | 16 | 09:49:01 | 11:42:02 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1018.74, 'reason': '진입', 'hint_source': '', 'atr': 2.2271, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `PipePerf` | 12 | 09:00:02 | 11:50:05 | total=1806ms | S0=4ms S1=10ms S2=1ms S3=0ms S4=229ms S5=718ms S6=810ms S7=29ms S8=5ms |
| `CB⑤` | 12 | 09:00:02 | 11:50:05 | 파이프라인 1806ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 10 | 09:00:02 | 12:18:01 | level=WARNING degraded=OFF | latency=1806ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |
| `ScalerRefresh` | 9 | 09:05:00 | 12:08:01 | 5분 누적 수익률 -1.379% (임계 ±0.815%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `EntryFillFlow` | 7 | 09:49:01 | 11:26:01 | actual_side='LONG' | after='LONG 1계약 @ 1018.32' | applied_side='LONG' | before='FLAT' | fill_no='' | fill_price=1018.32 | fill_qty=1 | order_no='814' | pending='ENTRY:LONG qty=3 filled=1 order_no=814 reason=진입 req_at=09:49:01.502' |
| `ExitCooldown` | 6 | 09:57:22 | 11:42:02 | 하드스톱(틱) 후 2분 재진입 금지 (until 09:59:22) |
| `HealthPolicy` | 5 | 09:01:01 | 11:51:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1806ms quality=0.86 cache=0s exc10m=0) | cause=S6(810ms) |
| `ConstOut` | 4 | 09:35:01 | 11:48:01 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

**채널** — `SYSTEM`×223, `HEALTH`×10

**컴포넌트 상위 15** — `LiveDBG`×73, `ChejanFlow`×22, `ChejanMatch`×22, `PendingOrder`×16, `PipePerf`×12, `CB⑤`×12, `Health`×10, `ScalerRefresh`×9, `EntryFillFlow`×7, `ExitCooldown`×6, `HealthPolicy`×5, `ConstOut`×4, `ExitFillFlow`×4, `EntryAttempt`×3, `EntrySendOrderResult`×3

### `logs/20260819_SYSTEM.log` — 484.0KB · 3447행 · 최종 12:26:46

- 형식 평문 · 시각 인식 3440행 · INFO=3440, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21612 | 행감지=30s all_threads=True
2026-08-19 08:40:59 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-19 08:40:59 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-19 08:40:59 [INFO] SYSTEM: 미륵이 초기화
2026-08-19 08:40:59 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-18) 종가 버퍼 로드: 385봉
  …
2026-08-19 12:26:21 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-2296,foreign:-5122,institution:+7999}
2026-08-19 12:26:21 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-277012 nonarb=-1855139
2026-08-19 12:26:21 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-277012 nonarb=-1855139
2026-08-19 12:26:22 [INFO] SYSTEM: [OptionChain][Worker] 완료 1495ms | target=24 valid=24 PCR=1.102 ATM_PCR=1.219 GEX=-20.56B
2026-08-19 12:26:46 [INFO] SYSTEM: [CybosRT-TICK] #76900 code=A0569 raw_time=122645 parsed=12:26:45 price=1015.68 vol=1 bid1=1015.56 ask1=1015.68 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×3440

**컴포넌트 상위 15** — `CybosInvestorRaw`×822, `CybosRT-TICK`×774, `CybosRT-ROLLOVER`×221, `BAR-CLOSE`×221, `CVD-ANCHOR`×221, `TickUI`×220, `S6Detail`×207, `PipePerf`×207, `System`×59, `MicroRegime`×59, `BalanceUI`×45, `CybosEvent`×44, `IntradayRegime`×39, `RegimeFingerprint`×38, `BalanceRefresh`×31

### `logs/20260819_SIGNAL.log` — 386.3KB · 3329행 · 최종 12:26:01

- 형식 평문 · 시각 인식 3329행 · WARNING=1665, INFO=1664

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.403
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.395
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.391
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.399
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
  …
2026-08-19 12:26:01 [INFO] SIGNAL: [IntradayRegime] NORMAL → DAY_RISK_OFF | day=-1.13% ATR=1.11 z=0
2026-08-19 12:26:01 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-08-19 12:26:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.4% grade=X regime=NEUTRAL
2026-08-19 12:26:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=35.4% grade=X micro=횡보장
2026-08-19 12:26:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.354<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1044 | 09:00:02 | 12:08:01 | 1m 'macro_vix' scale=0.0036 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 210 | 08:45:21 | 12:08:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0280) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 155 | 09:00:00 | 12:13:01 | ts=08:59 horizon=1m age=1m max_z=+4.99(cancel_add_ratio) extreme=1 |
| `Model` | 148 | 09:00:00 | 12:13:01 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 58 | 09:06:00 | 12:23:01 | 신뢰도 미달 34.9% < 37.3% → 강제 X등급 |
| `WeightCollapse` | 45 | 09:07:00 | 12:22:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 4 | 09:35:01 | 11:47:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3329

**컴포넌트 상위 15** — `ScalerFloor`×1062, `SIGNAL`×414, `ScalerRefresh`×241, `Ensemble`×207, `FQAdj`×204, `Model`×178, `ZeroDiag`×173, `ScalerMonitor`×155, `MetaGate`×132, `Checklist`×99, `ATR-Horizon`×82, `MicroRegime`×59, `InstabilityGate`×59, `차단`×47, `WeightCollapse`×45

### `logs/20260819_LEARNING.log` — 170.0KB · 1604행 · 최종 12:26:01

- 형식 평문 · 시각 인식 1604행 · WARNING=133, INFO=1471

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00024 auc=0.524 out_max=0.3178 (기준 auc<0.53 and span<0.020, 기저율=0.3176 n=85) → 보정 미적용, raw 통과
2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00035 auc=0.536 out_max=0.3336 (n=90) → 보정 재적용
2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3336 < conf_floor=0.3300 (n=90) → 보정 재적용
  …
2026-08-19 12:26:01 [INFO] LEARNING: [sigma] sigma_at_t=0.1093% buf_n=20 nonzero=20 prev_p=1016.42 cur_p=1014.90
2026-08-19 12:26:01 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=33.3% 예측=UP 실제=DN)
2026-08-19 12:26:01 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=42.9% 예측=DN 실제=FL)
2026-08-19 12:26:01 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=35.7% 예측=DN 실제=FL)
2026-08-19 12:26:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=16.7%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 133 | 08:41:05 | 12:23:01 | 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×1604

**컴포넌트 상위 15** — `LEARNING`×664, `Calibration`×261, `SGD`×207, `sigma`×194, `Bias⚠`×81, `Bias`×65, `MetaConf`×39, `ScalerWarmup`×31, `OnlineLearner`×20, `SHAP`×8, `GBM-64`×8, `GBM`×8, `BiasReset`×7, `RF`×5, `ExtremityCorrector`×2

### `logs/20260819_HEALTH.log` — 2.7KB · 20행 · 최종 12:19:02

- 형식 평문 · 시각 인식 20행 · WARNING=10, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1806ms | quality=0.86 | cache_age=39s | exceptions_10m=0
2026-08-19 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=639ms | quality=0.86 | cache_age=98s | exceptions_10m=0
2026-08-19 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 318ms (표본 20분)
2026-08-19 09:36:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=461ms | quality=1.00 | cache_age=181s | exceptions_10m=0 [GBM재학습중→lat임계 5000/10000ms]
2026-08-19 09:37:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2148ms | quality=1.00 | cache_age=60s | exceptions_10m=0
  …
2026-08-19 11:27:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=349ms | quality=1.00 | cache_age=58s | exceptions_10m=2
2026-08-19 11:50:05 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2100ms | quality=1.00 | cache_age=157s | exceptions_10m=1
2026-08-19 11:51:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=345ms | quality=1.00 | cache_age=30s | exceptions_10m=1
2026-08-19 12:18:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-19 12:19:02 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=262ms | quality=1.00 | cache_age=61s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 10 | 09:00:02 | 12:18:01 | level=WARNING degraded=OFF | latency=1806ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |

**채널** — `HEALTH`×20

**컴포넌트 상위 15** — `Health`×19, `HealthTrend`×1

### `logs/retrain_intraday_20260819_093601.log` — 2.4KB · 20행 · 최종 09:36:23

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 09:36:01,269 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-19 09:36:01,269 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-19 09:36:01,269 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-19 09:36:01,269 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_6deb2a50.json
2026-08-19 09:36:04,221 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-19 09:36:23,830 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.97s | old_acc=0.4094)
2026-08-19 09:36:23,916 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-19 09:36:23,916 [INFO] LEARNING: [Retrain] 완료 | 19.7초 | 성공=1/1 호라이즌
2026-08-19 09:36:23,917 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.6s 데이터=4800행
2026-08-19 09:36:23,918 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_6deb2a50.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260819_101001.log` — 2.4KB · 20행 · 최종 10:10:23

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 10:10:01,156 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-19 10:10:01,156 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-19 10:10:01,157 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-19 10:10:01,157 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_f3ecc7a2.json
2026-08-19 10:10:04,042 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-19 10:10:22,984 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.96s | old_acc=0.4094)
2026-08-19 10:10:23,069 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-19 10:10:23,069 [INFO] LEARNING: [Retrain] 완료 | 19.0초 | 성공=1/1 호라이즌
2026-08-19 10:10:23,069 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.9s 데이터=4800행
2026-08-19 10:10:23,071 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_f3ecc7a2.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 3 |
| 진입 등록(`[Position] 진입`) | 2 |
| 체결(`[체결진입]`) | 5 |
| 청산(`체결청산`) | 3 |
| 차단(`[차단]`) | 47 |
| 사이저 호출(`[Sizer]`) | 6 |

### 청산 3건 · 승 2 (67%) · 합계 +1.38pt (+64,417원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 09:57:22 | LONG | +1.03 | +50,139 | 하드스톱(틱) |
| 11:21:33 | SHORT | -2.89 | -146,192 | 하드스톱(틱) |
| 11:42:02 | SHORT | +3.24 | +160,470 | TP2(전량) |

**청산 사유 분포** — `하드스톱(틱)`×2, `TP2(전량)`×1

> 하드스톱·손절 계열 2/3건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:11:01 | SHORT | 3 | 1016.68 | 3m | neutral |
| 11:26:01 | SHORT | 1 | 1019.88 | 3m | neutral |

계약수 분포 — 1계약×1, 3계약×1

등급 분포 — `A급(원시C)`×2, `C급`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×1, `chas`×1, `cvd`×1, `ofi`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1, **3계약**×5

실제 진입 계약수 — **1계약**×1, **3계약**×1

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×6

### 차단 사유 47건 · 21종

| 건수 | 사유 |
|---|---|
| 21 | 등급X — 미통과 항목: 2_confidence |
| 3 | JointGateBlock — meta=0.50 tox=0.70 joint=0.350 < 0.50 |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.1pt > ATR×5.0=13.7pt (시가=1026.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.1pt > ATR×5.0=14.3pt (시가=1026.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.1pt > ATR×5.0=14.1pt (시가=1026.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.1pt > ATR×5.0=11.9pt (시가=1026.48 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.9pt > ATR×5.0=11.4pt (시가=1026.48 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 11_countertrend |
| 1 | 청산 후 쿨다운 — 20초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi |
| 1 | 청산 후 쿨다운 — 92초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×21, `3_vwap`×12, `4_cvd`×7, `7_prev_bar`×7, `5_ofi`×5, `6_foreign`×5, `11_countertrend`×5

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `연속 손절 1회` ×1
- `연속 손절 2회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 21건 · 최대 6766ms · 5초 초과 4건

상위 — 6766ms, 6422ms, 5782ms, 5078ms, 4891ms, 4859ms, 4703ms, 4656ms

> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **4건**이다. CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260819_WARN.log`
```
--- ConstOut ×4(표본)
09:35:01 2026-08-19 09:35:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:09:01 2026-08-19 10:09:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:42:01 2026-08-19 10:42:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:48:01 2026-08-19 11:48:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×2(표본)
11:12:08 2026-08-19 11:12:08 [WARNING] SYSTEM: [CB] 연속 손절 1회
11:21:33 2026-08-19 11:21:33 [WARNING] SYSTEM: [CB] 연속 손절 2회
--- [ExitCooldown] ×6(표본)
09:57:22 2026-08-19 09:57:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:59:22)
09:57:22 2026-08-19 09:57:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:59:22)
11:21:33 2026-08-19 11:21:33 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:24:33)
11:21:33 2026-08-19 11:21:33 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:24:33)
--- 메인 스레드 블로킹 ×8(표본)
08:41:23 2026-08-19 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:00:06 2026-08-19 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6766ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:01:02 2026-08-19 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:05:04 2026-08-19 09:05:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

### `logs/20260819_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:01 2026-08-19 09:35:01 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:01 2026-08-19 09:35:01 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:01 2026-08-19 09:35:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=378ms fit=36ms total=417ms
09:36:00 2026-08-19 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-08-19 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
09:06:00 2026-08-19 09:06:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
09:12:00 2026-08-19 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
09:17:01 2026-08-19 09:17:01 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
```

### `logs/20260819_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-08-19 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:01 2026-08-19 09:35:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:01 2026-08-19 09:35:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:01 2026-08-19 09:36:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:03 2026-08-19 09:37:03 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-08-19 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-08-19 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-08-19 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:16:01 2026-08-19 09:16:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.403
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.395
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.391
08:40:43 2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.399
--- 안전망 ×8(표본)
09:07:00 2026-08-19 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-19 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-08-19 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:01 2026-08-19 09:16:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260819_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:05 2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:05 2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00024 auc=0.524 out_max=0.3178 (기준 auc<0.53 and span<0.020, 기저율=0.3176 n=85) → 보정 미적용, raw 통과
08:41:05 2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00035 auc=0.536 out_max=0.3336 (n=90) → 보정 재적용
08:41:05 2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00013 auc=0.513 out_max=0.3369 (기준 auc<0.53 and span<0.020, 기저율=0.3368 n=95) → 보정 미적용, raw 통과 [기존 fitted 해제]
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260819_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:13 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 11 | 09:57:20 [INFO] 하드스톱(틱) LONG 2ct tick=1019.42 stop=1019.46 → 주문 전송 |

- 이 로그 생존구간: 08:41 ~ 11:42

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260819_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 11 | 09:00:02 [WARNING] total=1806ms | S0=4ms S1=10ms S2=1ms S3=0ms S4=229ms S5=718ms S6=810ms S7=29ms S8=5ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 13 | 09:00:02 [WARNING] total=1806ms | S0=4ms S1=10ms S2=1ms S3=0ms S4=229ms S5=718ms S6=810ms S7=29ms S8=5ms |
| 10:00 | 장중 초반 | 25 | 09:57:20 [WARNING] 스톱 히트 감지 (틱) LONG tick=1019.42 stop=1019.46 → 즉시 처리 예약 |

- 이 로그 생존구간: 08:41 ~ 12:18

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260819_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=21612 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 125 | 08:49:03 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 198 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 234 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 170 | 11:54:02 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:26

**매분 루프 커버리지 09:00~15:10: 207/371분 (55.8%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:27 | 15:10 | 164 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260819_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:21 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0280) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 105 | 08:50:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0344) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 251 | 08:55:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0434) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 204 | 09:55:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 12:00 | 장중 중간점 | 112 | 11:54:02 [WARNING] 신뢰도 미달 33.3% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.9MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [신규 P1] 단기 CORE `ofi_norm` 스케일러 identity 강제가 장전 국한 → 종일·전 호라이즌으로 확산 (2거래일째)
### [기존 P1 재발 · 6일째] 불변식 감시표 5행 `미발견` — F-1(브랜치 스코프 분리) 미적용 확인
### [신규 P2] `CybosProbe` 후보 1종이 COM 초기화 누락으로 한 번도 실제 시험된 적이 없다
### [신규 P2] 수집기 §2 "미커밋 459건"은 CRLF 아티팩트 — 실질 4건
### [문서] 장전 체크리스트 `OPT50029` 항목은 Cybos에서 해당 없음
### 오늘 §11 자동 적신호 7건 — 진짜 0건
### 정상 확인 (장전 필수)
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
2026-08-19 08:58:25 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed:
                                     (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-08-19 08:58:25 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader … (-2147221005, '잘못된 클래스 문자열입니다.')
   (나머지 3종도 -2147221005)
```
5개 후보 중 4개는 `-2147221005`(클래스 없음) = 정당한 "없다" 결론. 그러나 `CpSvrNew7221` 하나는
`-2147221008` = **워커 스레드가 `CoInitialize`를 호출하지 않아 디스패치조차 못 했다.**
이 실패가 `[CybosInvestor] reason=Cybos 선물 투자자 TR 미발견` 결론에 합산되고 있다 —
**"없다"와 "못 봤다"가 같은 결론으로 흘렀다**(계측 4원칙 ②).
**결정**: F-3 — `pythoncom.CoInitialize()` 배선 + `미시험(COM 초기화 실패)` / `미발견(클래스 없음)`
**분리 표기**. ⚠ **적용 전 호출 스택이 COM 콜백 내부가 아님을 반드시 확인**(절대원칙 ④ 인접).
수집 성공 시 새 피처는 **학습 투입 전 섀도 필수**(97개 동결 슈퍼셋 — 458차 P2-B 온보딩 절차).
오늘 실손해 0(해당 피처는 451차 `program_*` 폐기 계열로 학습에서 이미 빠져 있다).

### [신규 P2] 수집기 §2 "미커밋 459건"은 CRLF 아티팩트 — 실질 4건

`file CLAUDE.md` → `with CRLF line terminators`. `git diff --stat CLAUDE.md` = `749 insertions(+),
749 deletions(-)`(전파일 재작성). `git diff --ignore-all-space --stat` → **4 files changed**
(`SKILL.md` · `collect_evidence.py` · `config/dailycheck_targets.json` · `scripts/monthly_cleanup.py`).
코웍 bash가 리눅스 샌드박스라 `core.autocrlf`가 비어 있는 탓 — **repo 이상이 아니다.**
→ F-2 같은 커밋에서 수집기 §2에 실질 건수 괄호 병기.

### [문서] 장전 체크리스트 `OPT50029` 항목은 Cybos에서 해당 없음

`grep -rn "OPT50029" --include=*.py .` → 전부 `collection/kiwoom/api_connector.py`.
오늘 `[Capability] broker=cybos … server=Cybos 모의투자`. 오늘 로그의 `OPT#####` 토큰 0건은 정상.
→ F-4로 `references/phases.md` A절에 브로커 분기 명시.

### 오늘 §11 자동 적신호 7건 — 진짜 0건

1~5 브랜치 차이(오탐) · 6 `Calibration 축퇴`(평상 수준: 08-12 102 / 08-13 97 / 08-14 99 /
08-18 98 / 08-19 90) · 7 CRLF(오탐). **본 세션 P1 3건은 전부 §11이 못 잡은 것이다** —
스킬 §2의 *"자동 적신호는 출발점이지 결론이 아니다"* 가 오늘도 성립.

### 정상 확인 (장전 필수)

브랜치 `v9-dev` · 전일 EOD 재학습 `호라이즌 교체=6/6 가드보류=0 합계=340.2s`(py310_64 정상) ·
본체 py37_32 · `[Capability] broker=cybos connect=Y/Y balance=Y/Y … Cybos 모의투자` ·
08:45 선행구독 · 08:55 매크로 seed → 08:58:25 `[Regime] NEUTRAL (점수=0) VIX=15.2` ·
모델 6종 + RF 6호라이즌 로드 · 메인스레드 블로킹 최대 **2,797ms** (CB⑤ 임계 5,000ms 미달) ·
크래시 0건 · **O-H 장전 점검 08:57±5분 복귀 확인**(08:59:54, 어제 13:44 지연에서 정상화) ·
`[RegimeFingerprint] PSI=0.009 level=0 (heartbeat)` 09:00:00 **라이브 첫 확인**(477차 F-5).

### 검증

- 코드 변경 0건 · 커밋 0건 · 라이브 DB 접근 0건(로그·설정·JSON·git 메타만).
- 재인용 금지 수치 미사용: 2026-06-25 SHAP=0 / 0801 §9-3 이벤트 단위 사이징 4종 / CB③ "35%" /
  417차 "379건 중 86건" / 476차 §3 "133건·29.6%"·"binding 20분·≈+0.00pt".
- 표본 부족 항목에 확정 결론 없음(313차): `ofi_norm` 손익 영향 · 원인 3후보 · `session_state` 원인.

```

</details>

### dev_memory/NEXT_TODO.md — 975.6KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 커밋 대기 (476차 — 본 세션은 커밋하지 않았다)
### 477차 — post 확인필요 3건 딥다이브 후속 (MW0601, 2026-08-18 분석만·코드 0건)
### 477차 후속2 — 476차 Fix 계획 검토 결과 (MW0601, 2026-08-18 · 검토만, 코드 0건)
### 477차 후속1~3 — 476차 Fix 구현 완료 (MW0601, 2026-08-18 · 커밋 3건)
### 477차 후속5 — 476차 §3 고도화 방안 조사 결과 (MW0601, 2026-08-18 · 조사만)
### 477차 후속6 — GR-1 구현 완료 (MW0601, 2026-08-18)
### 477차 후속7 — GR-3 구현 완료 (MW0601, 2026-08-18)
### 478차 — 장전 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
```

미완료 체크박스 **1440건** (끝에서 30건)
```
- [ ] **[안건] 진입모드(`entry_mode`) 실전 목표값** — 476차 §1-5. 최소 08-03 이래
- [ ] **[안건] DD-3 ghost_bypass 범위** (477차 등록, 재확인) — D6 clean 판정 전환이
- [ ] **GR-1 `scripts/profit_guard_latch_watch.py` 신설 (이번 주)** — 읽기 전용 소급.
- [ ] **GR-2 [08-29 주간회의] ProfitGuard 래치 판정문 재등록 승인** —
- [ ] **GR-3 ProfitGuard 손익 원천 토큰 (소, 저위험)** — `strategy/profit_guard.py:_block()`
- [ ] **GR-4 재인용 금지 등재** — 476차 §3의 "L1 차단 133건 · 세션의 29.6%"를
- [ ] **GR-1R 다음 L1 발동일에 재실행** — L1은 2.5개월 4회라 다음 발동이 언제일지
- [ ] **GR-4 재인용 금지 갱신** — 476차 §3 "133건·29.6%"(로그 콜 수)에 더해,
- [ ] **GR-3V 다음 거래일 라이브 확인** — SIGNAL 로그의 `[ProfitGuard] 진입 차단` 줄에
- [ ] **GR-3F (후속 판단, 서두르지 말 것)** — 토큰이 며칠 쌓여 **broker/engine 혼재가
- [ ] **F-1 `session_state` EOD 인계키 소멸 — 원인 규명 + 폴백 가시화 (P1, 장후)**
- [ ] **F-1V 08-20 장전 판정** — `data/session_state.json`에 4키 잔존 + `[SessionState]` 신규 로그
- [ ] **F-2 수집기 불변식 감시표 브랜치 스코프 분리 (P1, 장후)** — 08-14·08-17에 이어 **3번째 등록**.
- [ ] **F-3 `CybosProbe` CoInitialize 배선 + 미시험/미발견 분리 표기 (P2, 장후)**
- [ ] **F-4 `references/phases.md` A절에 선물 분봉 TR 브로커 분기 명시** —
- [ ] **G-1 `scripts/core_scaler_degeneracy_watch.py` 신설 (이번 주)** — 읽기 전용 소급.
- [ ] **G-2 `ofi_norm` 축퇴 원인 3분기 진단 (1회성, 장후)** —
- [ ] **G-3 `SESSION_STATE_REQUIRED_KEYS` 스키마 + 기동 시 부재 키 WARNING** —
- [ ] **[안건] `v9-dev` ← `dev` 315커밋 정렬 여부 (주간회의)** — 특히
- [ ] **[로드맵] 26주 WFA 재검증 항목에 G-1 채널 편입 제안** —
- [ ] **`ofi_norm` identity 강제율 종일 집계** — 08-18의 71%를 넘는가.
- [ ] **15:51 `data/session_state.json` 스냅샷** (F-1 조사 1단계)
- [ ] **GR-3V** — `[ProfitGuard] 진입 차단` 줄에 `| src=` 토큰. 장전 차단 0건이라 **미확인**.
- [ ] **G-A/G-B PSI** — 09:00:00 `PSI=0.009 level=0` **하트비트 1건 확인됨**.
- [ ] **G-C DriftAdjuster** — 오늘 기동 `alpha=0.01000, 이력 10일, 마지막 액션=DRIFT_UP`.
- [ ] **G-D** — 15:40 `[BrokerPnl] EOD 확정 — gross … − 수수료 … = net …`
- [ ] **O-G IntradayRegime 전이 4일차** — 09:02:00 이미 `NORMAL → CRASH (day=-1.11% atr=1.00 z=3)`.
- [ ] **`[ModelLive]` 10m·15m 5일차** (어제 20.8%/21.3%)
- [ ] **F-1R 15:10 강제청산 리허설 — ⚠ 사용자 실행 필요.** 전환기준 ②의 유일한 해소 경로
- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **10일**. 오늘 `9999` 유지 확인
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 `타브랜치 미적용 N종` 필수. `invariants.md` §2-B에 `적용 브랜치` 열.
      같은 커밋에서 §2에 `git diff --ignore-all-space` 실질 건수 괄호 병기(CRLF 오탐 제거).
      검증: `v9-dev` 재실행 시 §11 적신호 **7 → 0~1건**
- [ ] **F-3 `CybosProbe` CoInitialize 배선 + 미시험/미발견 분리 표기 (P2, 장후)**
      ⚠ **적용 전 호출 스택이 COM 콜백 내부가 아님을 반드시 확인**(절대원칙 ④ 인접).
      확인 미완이면 **다음 세션으로 넘긴다.** 런타임 py37_32.
      ⚠ 수집 성공해도 새 피처 **학습 투입 금지** — 458차 P2-B 온보딩 절차 선행
- [ ] **F-4 `references/phases.md` A절에 선물 분봉 TR 브로커 분기 명시** —
      `Cybos: 해당없음 / Kiwoom: OPT50029`. F-2와 같은 커밋
- [ ] **G-1 `scripts/core_scaler_degeneracy_watch.py` 신설 (이번 주)** — 읽기 전용 소급.
      `[ScalerRefresh] … raw_std≈0`을 CORE 피처별·호라이즌별·일자별 identity 강제율로 집계.
      **사전등록 판정문**: *"단기 그룹 CORE 1종의 일별 강제율이 5거래일 연속 50% 초과면 해당
      피처의 CORE 지위를 주간회의 안건으로. 미만이면 현행 유지."*
      ⚠ 임계는 지금 등록하고 **이후 움직이지 않는다**(313차 ④, 458차 D6).
      ⚠ 집행(차단·등급)에 연결 금지 — 섀도 관찰 후 승격
- [ ] **G-2 `ofi_norm` 축퇴 원인 3분기 진단 (1회성, 장후)** —
      (a) 원값 0 점질량 비율 일자별 추이 (b) `ofi_imbalance`·`mlofi_norm` 동반 축퇴 여부
      (c) `tick_size` 변경 시점 정렬. ⚠ `guard_intraday()` + `connect_ro()` 필수.
      **판정이 아니라 후보를 3→1로 좁히는 것이 목표**
- [ ] **G-3 `SESSION_STATE_REQUIRED_KEYS` 스키마 + 기동 시 부재 키 WARNING** —
      ⚠ **F-1 원인 규명이 선행**. 원인을 모른 채 스키마만 넣으면 경고만 늘어난다
- [ ] **[안건] `v9-dev` ← `dev` 315커밋 정렬 여부 (주간회의)** — 특히
      `MODEL_LABEL_STATE_UNLOCK_ENABLED`(실전전환 ⑧ 선행조건)가 `v9-dev`에 부재.
      **MW0601 단독 관측으로 ⑧을 판정하지 말 것.** 대규모 머지는 점검 세션 단독 실행 금지
      (2026-08-12 289커밋 사고)
- [ ] **[로드맵] 26주 WFA 재검증 항목에 G-1 채널 편입 제안** —
      455차 "호라이즌 방향예측 피처셋 재검증"과 같은 성격, IC 드리프트의 **선행 지표**

#### 오늘(08-19) 장중·장후 관측 예정

- [ ] **`ofi_norm` identity 강제율 종일 집계** — 08-18의 71%를 넘는가.
      09:02 `raw_std=0.0321`. 15:50 E_EOD에서도 걸리면 **3거래일 연속**
- [ ] **15:51 `data/session_state.json` 스냅샷** (F-1 조사 1단계)
- [ ] **GR-3V** — `[ProfitGuard] 진입 차단` 줄에 `| src=` 토큰. 장전 차단 0건이라 **미확인**.
      L2-Tier/L3-Afternoon 차단 줄에서 먼저 보일 것
- [ ] **G-A/G-B PSI** — 09:00:00 `PSI=0.009 level=0` **하트비트 1건 확인됨**.
      장후 `ensemble_decisions.fp_psi` 비-NULL 행수 = 당일 행수인지
- [ ] **G-C DriftAdjuster** — 오늘 기동 `alpha=0.01000, 이력 10일, 마지막 액션=DRIFT_UP`.
      15:40 로그가 포화를 가시화하는가(미적용이면 `0.01000→0.01000` **7번째**)
- [ ] **G-D** — 15:40 `[BrokerPnl] EOD 확정 — gross … − 수수료 … = net …`
- [ ] **O-G IntradayRegime 전이 4일차** — 09:02:00 이미 `NORMAL → CRASH (day=-1.11% atr=1.00 z=3)`.
      08-14 19회 / 08-18 18회 대비
- [ ] **`[ModelLive]` 10m·15m 5일차** (어제 20.8%/21.3%)
- [ ] **F-1R 15:10 강제청산 리허설 — ⚠ 사용자 실행 필요.** 전환기준 ②의 유일한 해소 경로
- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **10일**. 오늘 `9999` 유지 확인

```

</details>

### dev_memory/CURRENT_STATE.md — 529.4KB · 마지막 갱신 2026-08-17 17:53

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

### `docs/정기점검/매일점검` — 46개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-pre.md` | 33.8KB | 08-19 09:11 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_pre.md` | 46.2KB | 08-19 09:00 |
| `docs/정기점검/매일점검/MW0601-20260818-고도화방안검토.md` | 16.3KB | 08-18 23:04 |
| `docs/정기점검/매일점검/MW0601-20260818-Fix계획검토.md` | 13.8KB | 08-18 19:28 |
| `docs/정기점검/매일점검/MW0601-20260818-확인필요3건-딥다이브.md` | 15.5KB | 08-18 18:33 |
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-post.md` | 45.0KB | 08-18 16:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260818_post.md` | 69.3KB | 08-18 16:22 |
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-intra.md` | 39.4KB | 08-18 14:00 |

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
6. `logs/20260819_WARN.log`: ERROR 이상 1건
7. `logs/20260819_SYSTEM.log`: 매분 루프 커버리지 207/371분 (55.8%) — 루프가 빠진 구간이 있다
8. `logs/20260819_SYSTEM.log`: 12:27~15:10 **연속 164분 매분 루프 기록 없음**
9. 메인 스레드 블로킹 5초 초과 **4건** (최대 6766ms) — `CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인
10. `logs/20260819_WARN.log`: **ConstOut** 4건(표본)
11. `logs/20260819_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20260819_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20260819_SIGNAL.log`: **ConstOut** 8건(표본)
14. `logs/20260819_LEARNING.log`: **축퇴** 8건(표본)
15. 미커밋 변경 461건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260819*.log` (Windows) / `grep 강제청산 logs/*20260819*.log`*