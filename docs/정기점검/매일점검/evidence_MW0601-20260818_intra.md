# 미륵이 증거 다이제스트 — 2026-08-18 / INTRA

- 생성 2026-08-18 13:49:07 KST · PC **MW0601** (`DeskTop-MW0601`)
- 리포 `/sessions/awesome-pensive-volta/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260818` · `2026-08-18` · `260818` · `0818`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `launcher_{DATE}_084001_2415.log` | 1 | `logs/Mireuk_batch/launcher_20260818_084001_2415.log` | 1.4MB | 08-18 13:48 |
| `retrain_intraday_{DATE}_093759.log` | 1 | `logs/retrain_intraday_20260818_093759.log` | 2.4KB | 08-18 09:38 |
| `retrain_intraday_{DATE}_113159.log` | 1 | `logs/retrain_intraday_20260818_113159.log` | 2.4KB | 08-18 11:32 |
| `retrain_intraday_{DATE}_122559.log` | 1 | `logs/retrain_intraday_20260818_122559.log` | 2.4KB | 08-18 12:26 |
| `retrain_intraday_{DATE}_125859.log` | 1 | `logs/retrain_intraday_20260818_125859.log` | 2.4KB | 08-18 12:59 |
| `retrain_intraday_{DATE}_133159.log` | 1 | `logs/retrain_intraday_20260818_133159.log` | 2.4KB | 08-18 13:32 |
| `{DATE}_DATA.log` | 1 | `logs/20260818_DATA.log` | 255.0KB | 08-18 13:48 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260818_DEBUG.log` | 183.8KB | 08-18 13:48 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260818_HEALTH.log` | 4.4KB | 08-18 13:43 |
| `{DATE}_HOGA.log` | 1 | `logs/20260818_HOGA.log` | 42.2MB | 08-18 13:49 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260818_LEARNING.log` | 229.4KB | 08-18 13:48 |
| `{DATE}_MICRO.log` | 1 | `logs/20260818_MICRO.log` | 839.5KB | 08-18 13:49 |
| `{DATE}_PROBE.log` | 1 | `logs/20260818_PROBE.log` | 74.7KB | 08-18 13:48 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260818_SIGNAL.log` | 535.3KB | 08-18 13:48 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260818_SYSTEM.log` | 690.5KB | 08-18 13:48 |
| `{DATE}_TRADE.log` | 1 | `logs/20260818_TRADE.log` | 27.0KB | 08-18 13:48 |
| `{DATE}_WARN.log` | 1 | `logs/20260818_WARN.log` | 103.7KB | 08-18 13:41 |

## 2. 코드·커밋 상태

- HEAD `7dc14bc` · 브랜치 `v9-dev` · 미커밋 455건
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
… 외 415건
```

**당일(2026-08-18) 커밋**
```
(당일 커밋 없음)
```

**최근 커밋 12건**
```
7dc14bc [MW0601] 474차: D9 딥다이브 — §3 정합화 + 라우팅 밴드 채널 + 30m 역필터 기각
68ff91c [MW0601] 473차: 구조적 교착 해소 — 테스트 오염 · F-8 배선/판정 · D9 도달성 · D8 인프라
e995764 [MW0601] 472차: UI 좌상단 "Phase 3 예정" 배지 → Phase 5 전환 게이트 자동 판정
f911e8d [MW0601] 471차 후속8: G-3 강제청산 리허설 26주 WFA 편입 + 로드맵 반영 + dev_memory
211246d [MW0601] 471차 후속7: G-2 ConstOut 호라이즌 건강도 채널 [51] 신설
ca954b8 [MW0601] 471차 후속6: G-1 사이징 계보 구조체 저장 + [28] 사이저 압력 실측화
cdb7462 [MW0601] 471차 후속5: dev_memory 반영 — F-9 구현 기록
7284b95 [MW0601] 471차 후속4: entry_mode 예외 폴백 가시화 (F-9)
fc889ff [MW0601] 471차 후속3: dev_memory 반영 — 471차 구현 기록 + 잔여/후속 항목
82e7554 [MW0601] 471차 후속2: 차단사유 정합 — 동시 성립 축 전량 + 선제차단 플래그 (스키마)
8be4048 [MW0601] 471차 후속: [SizerMatch] binding 게이트 명시 + 품질군 전량 출력
76211c3 [MW0601] 471차: 15:10 강제청산 1차 경로 도달성 복구 + 안전망 하트비트
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

_본문 미열람(설정): `20260818_HOGA.log` 42.2MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `retrain_intraday_20260818_125859.log`, `retrain_intraday_20260818_133159.log`, `retrain_intraday_20260818_122559.log`, `20260818_MICRO.log`, `20260818_DATA.log`, `20260818_PROBE.log`, `launcher_20260818_084001_2415.log`, `20260818_DEBUG.log`_

### `logs/20260818_TRADE.log` — 27.0KB · 193행 · 최종 13:48:59

- 형식 평문 · 시각 인식 193행 · WARNING=1, INFO=192

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:41:14 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-18 08:41:18 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-18 09:32:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,053,027) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 09:34:58 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,053,027) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 09:35:58 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,053,027) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-18 13:41:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.0→3계약]
2026-08-18 13:43:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 13:44:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 13:45:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 13:48:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.0→3계약]
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ProfitGuard-L1` | 1 | 13:19:59 | 13:19:59 | 트레일링 발동 — 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원) |

**채널** — `TRADE`×193

**컴포넌트 상위 15** — `Chejan`×47, `Sizer`×43, `Position`×29, `주문요청`×21, `JointGateBlock 차단`×10, `진입체크`×7, `체결진입`×7, `청산 완료`×7, `TickTP1`×6, `TP1 부분청산`×6, `체결진입보정`×5, `TickStop-S0C`×2, `ProfitGuard`×1, `손절1차 조기축소`×1, `ProfitGuard-L1`×1

### `logs/20260818_WARN.log` — 103.7KB · 437행 · 최종 13:41:59

- 형식 평문 · 시각 인식 437행 · WARNING=437

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-18 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-18 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-18 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-18 08:41:27 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3453ms — live 중단 원인 분석용
  …
2026-08-18 13:33:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 2545ms 경고 (기준 1000ms)
2026-08-18 13:33:01 [WARNING] SYSTEM: [CB⑤] 파이프라인 2545ms 경고 (기준 1000ms)
2026-08-18 13:33:59 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2545ms quality=1.00 cache=0s exc10m=1) | cause=S0(2113ms)
2026-08-18 13:36:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
2026-08-18 13:41:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=436ms | quality=1.00 | cache_age=181s | exceptions_10m=0
```

</details>

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 123 | 08:41:21 | 13:36:03 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 47 | 10:20:59 | 13:19:39 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1545' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=10:20:58.824' | positi… |
| `ChejanMatch` | 47 | 10:20:59 | 13:19:39 | order_no='1545' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1545 reason=진입 req_at=10:20:58.824' | pending_matched=True |
| `PendingOrder` | 42 | 10:20:58 | 13:19:39 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1132.68, 'reason': '진입', 'hint_source': '', 'atr': 1.8586, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `Health` | 17 | 09:08:58 | 13:41:59 | level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |
| `ExitCooldown` | 14 | 10:21:59 | 13:19:39 | 하드스톱 후 2분 재진입 금지 (until 10:23:59) |
| `ScalerRefresh` | 12 | 09:14:58 | 13:24:59 | 5분 누적 수익률 +0.457% (임계 ±0.344%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `EntryFillFlow` | 12 | 10:20:59 | 13:07:01 | actual_side='SHORT' | after='SHORT 2계약 @ 1132.44' | applied_side='SHORT' | before='SHORT 2계약 @ 1132.68' | fill_no='' | fill_price=1132.44 | fill_qty=1 | order_no='1545' | pending='ENTRY:SHORT qty=2 filled=1 order_no=1545 reason=진입 req_at=1… |
| `PipePerf` | 10 | 09:39:01 | 13:33:01 | total=2826ms | S0=2407ms S1=20ms S2=21ms S3=0ms S4=101ms S5=157ms S6=110ms S7=8ms S8=3ms |
| `CB⑤` | 10 | 09:39:01 | 13:33:01 | 파이프라인 2826ms 경고 (기준 1000ms) |
| `ExitSendOrderResult` | 8 | 10:21:59 | 13:19:39 | ret=0 kind=하드스톱 direction=SHORT qty=1 |
| `CB③-P4` | 8 | 10:56:58 | 12:39:59 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |

**채널** — `SYSTEM`×420, `HEALTH`×17

**컴포넌트 상위 15** — `LiveDBG`×123, `ChejanFlow`×47, `ChejanMatch`×47, `PendingOrder`×42, `Health`×17, `ExitCooldown`×14, `ScalerRefresh`×12, `EntryFillFlow`×12, `PipePerf`×10, `CB⑤`×10, `ExitSendOrderResult`×8, `CB③-P4`×8, `EntryAttempt`×7, `EntrySendOrderResult`×7, `FixB`×7

### `logs/20260818_SYSTEM.log` — 690.5KB · 4793행 · 최종 13:48:59

- 형식 평문 · 시각 인식 4786행 · INFO=4786, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:40:47 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21660 | 행감지=30s all_threads=True
2026-08-18 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-18 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-18 08:41:00 [INFO] SYSTEM: 미륵이 초기화
2026-08-18 08:41:00 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-14) 종가 버퍼 로드: 384봉
  …
2026-08-18 13:48:59 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=13:48 O=1090.94 H=1090.98 L=1090.16 C=1090.80 V=84
2026-08-18 13:48:59 [INFO] SYSTEM: [CVD-ANCHOR] ts=13:48 vol=84 | live_buy=48 shadow_buy=47 anchor_buy=47 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-08-18 13:48:59 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=12ms meta_gate=5ms gates=0ms imp=0ms shap=5ms corr=7ms dash_ui=0ms tail=15ms
2026-08-18 13:48:59 [INFO] SYSTEM: [PipePerf][DBG] total=380ms | S0=33ms S1=39ms S2=7ms S3=0ms S4=62ms S5=152ms S6=48ms S7=36ms S8=4ms
2026-08-18 13:49:10 [INFO] SYSTEM: [CybosRT-TICK] #110700 code=A0569 raw_time=134911 parsed=13:49:11 price=1091.22 vol=1 bid1=1091.30 ask1=1091.38 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×4786

**컴포넌트 상위 15** — `CybosInvestorRaw`×1150, `CybosRT-TICK`×1112, `CybosRT-ROLLOVER`×304, `BAR-CLOSE`×304, `CVD-ANCHOR`×304, `TickUI`×302, `S6Detail`×289, `PipePerf`×289, `CybosEvent`×94, `BalanceUI`×76, `System`×75, `MicroRegime`×69, `CybosDailyPnl`×64, `BalanceRefresh`×56, `OptionChain`×39

### `logs/20260818_SIGNAL.log` — 535.3KB · 4615행 · 최종 13:48:59

- 형식 평문 · 시각 인식 4615행 · WARNING=1909, INFO=2706

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.434
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.413
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.409
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.417
  …
2026-08-18 13:48:59 [INFO] SIGNAL: [HurstGate] 하드차단 대신 사이즈축소: hurst=0.320 < 0.45 size_mult=0.50 (§3-6 FAIL 완화, 333차 후속) quality_min=0.50
2026-08-18 13:48:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L1-Trail] 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원)
2026-08-18 13:48:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단: [L1-Trail] 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원)
2026-08-18 13:48:59 [INFO] SIGNAL: [ProfitGuard][DebugPnL] source=broker used=+685,000원 engine=+661,668원 broker=+685,000원
2026-08-18 13:48:59 [INFO] SIGNAL: [차단] 게이트 강등 X — ProfitGuard 진입 차단 ([L1-Trail] 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원)) (체크리스트 등급=C, 통과 9개)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1344 | 09:00:59 | 13:31:00 | 1m 'macro_sp500_chg' scale=0.0701 → floor=0.15 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 180 | 08:45:21 | 13:31:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0294) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 132 | 09:00:58 | 12:20:59 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 98 | 09:05:58 | 13:47:59 | 신뢰도 미달 34.9% < 39.2% → 강제 X등급 |
| `ScalerMonitor` | 88 | 09:00:58 | 12:30:58 | ts=09:00 horizon=1m age=2m max_z=+6.42(ret_15m) extreme=2 |
| `WeightCollapse` | 61 | 09:07:59 | 13:47:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 5 | 09:36:58 | 13:31:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:05:58 | 09:05:58 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3920 (conf_floor=0.330, min_conf=0.392, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4615

**컴포넌트 상위 15** — `ScalerFloor`×1362, `SIGNAL`×578, `MetaGate`×382, `Ensemble`×298, `FQAdj`×287, `ZeroDiag`×234, `ScalerRefresh`×222, `Checklist`×193, `Model`×168, `ATR-Horizon`×145, `ScalerMonitor`×88, `ToxicityGate`×86, `ProfitGuard`×86, `차단`×84, `MicroRegime`×69

### `logs/20260818_LEARNING.log` — 229.4KB · 2191행 · 최종 13:48:59

- 형식 평문 · 시각 인식 2191행 · WARNING=154, INFO=2037

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2002 < conf_floor=0.3300 (span=0.00040 auc=0.536 out_max=0.2002, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00033 auc=0.529 out_max=0.2002 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=85) → 보정 미적용, raw 통과
2026-08-18 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00064 auc=0.556 out_max=0.2004 (n=90) → 보정 재적용
  …
2026-08-18 13:48:59 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=34.5% 예측=FL 실제=UP)
2026-08-18 13:48:59 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=43.8% 예측=UP 실제=DN)
2026-08-18 13:48:59 [INFO] LEARNING: [Bias⚠] 1m 적중=35%(6/17) UP=2 DN=3 FL=12 [FL편향⚠ 71%]
2026-08-18 13:48:59 [INFO] LEARNING: [MetaConf] LR[추세장] 비동기 학습 완료 (n=300, classes=[0, 1, 2, 3])
2026-08-18 13:48:59 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=7.1%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 154 | 08:41:05 | 13:04:58 | 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×2191

**컴포넌트 상위 15** — `LEARNING`×940, `Calibration`×302, `SGD`×288, `sigma`×276, `Bias`×101, `Bias⚠`×93, `MetaConf`×62, `ScalerWarmup`×42, `OnlineLearner`×37, `SHAP`×10, `GBM-64`×10, `GBM`×10, `BiasReset`×9, `RF`×6, `ExtremityCorrector`×2

### `logs/20260818_HEALTH.log` — 4.4KB · 33행 · 최종 13:43:01

- 형식 평문 · 시각 인식 33행 · WARNING=17, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 09:08:58 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-18 09:09:58 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=260ms | quality=1.00 | cache_age=49s | exceptions_10m=0
2026-08-18 09:29:58 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 256ms (표본 20분)
2026-08-18 09:39:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2826ms | quality=1.00 | cache_age=132s | exceptions_10m=0
2026-08-18 09:39:58 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=335ms | quality=1.00 | cache_age=7s | exceptions_10m=0
  …
2026-08-18 13:02:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=307ms | quality=1.00 | cache_age=50s | exceptions_10m=0
2026-08-18 13:33:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2545ms | quality=1.00 | cache_age=10s | exceptions_10m=1
2026-08-18 13:33:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=335ms | quality=1.00 | cache_age=68s | exceptions_10m=1
2026-08-18 13:41:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=436ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-18 13:43:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=414ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 17 | 09:08:58 | 13:41:59 | level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |

**채널** — `HEALTH`×33

**컴포넌트 상위 15** — `Health`×32, `HealthTrend`×1

### `logs/retrain_intraday_20260818_093759.log` — 2.4KB · 20행 · 최종 09:38:27

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 09:37:59,005 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-18 09:37:59,006 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-18 09:37:59,006 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-18 09:37:59,006 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_71f9dec0.json
2026-08-18 09:38:02,508 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-18 09:38:26,928 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.92s | old_acc=0.4227)
2026-08-18 09:38:27,028 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-18 09:38:27,028 [INFO] LEARNING: [Retrain] 완료 | 24.5초 | 성공=1/1 호라이즌
2026-08-18 09:38:27,028 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 28.0s 데이터=4800행
2026-08-18 09:38:27,030 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_71f9dec0.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260818_113159.log` — 2.4KB · 20행 · 최종 11:32:20

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 11:31:59,013 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-18 11:31:59,014 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-18 11:31:59,014 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-18 11:31:59,014 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_07366610.json
2026-08-18 11:32:01,709 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-18 11:32:19,971 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.92s | old_acc=0.4227)
2026-08-18 11:32:20,051 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-18 11:32:20,052 [INFO] LEARNING: [Retrain] 완료 | 18.3초 | 성공=1/1 호라이즌
2026-08-18 11:32:20,053 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.0s 데이터=4800행
2026-08-18 11:32:20,054 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_07366610.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 7 |
| 진입 등록(`[Position] 진입`) | 7 |
| 체결(`[체결진입]`) | 7 |
| 청산(`체결청산`) | 7 |
| 차단(`[차단]`) | 84 |
| 사이저 호출(`[Sizer]`) | 43 |

### 청산 7건 · 승 6 (86%) · 합계 +5.62pt (+269,334원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 10:21:59 | SHORT | +1.55 | +75,801 | 하드스톱 |
| 10:40:59 | SHORT | +2.13 | +104,805 | 하드스톱 |
| 10:50:59 | SHORT | +1.30 | +63,325 | 하드스톱 |
| 10:57:59 | SHORT | +1.42 | +69,330 | 하드스톱 |
| 11:35:47 | SHORT | +0.17 | +6,859 | 하드스톱(틱) |
| 11:42:00 | SHORT | +2.38 | +117,353 | 하드스톱 |
| 13:19:39 | SHORT | -3.33 | -168,139 | 하드스톱(틱) |

**청산 사유 분포** — `하드스톱`×5, `하드스톱(틱)`×2

> 하드스톱·손절 계열 7/7건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 7건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:20:58 | SHORT | 2 | 1132.68 | 3m | mean-revert |
| 10:39:59 | SHORT | 2 | 1129.94 | 1m | neutral |
| 10:49:58 | SHORT | 2 | 1117.04 | 5m | trend |
| 10:55:59 | SHORT | 2 | 1113.4 | 5m | trend |
| 11:34:59 | SHORT | 2 | 1094.34 | 5m | trend |
| 11:39:59 | SHORT | 2 | 1098.14 | 5m | trend |
| 13:06:59 | SHORT | 2 | 1092.54 | 3m | mean-revert |

계약수 분포 — 2계약×7

등급 분포 — `A급(원시C)`×6, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×4, `chas`×4, `ofi`×3, `prev`×3, `cvd`×2

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×4, **2계약**×11, **3계약**×28

실제 진입 계약수 — **2계약**×7

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×43

### 차단 사유 84건 · 32종

| 건수 | 사유 |
|---|---|
| 31 | 등급X — 미통과 항목: 2_confidence |
| 7 | 게이트 강등 X — ProfitGuard 진입 차단 ([L1-Trail] 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,… |
| 6 | JointGateBlock — meta=0.50 tox=0.70 joint=0.350 < 0.50 |
| 5 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 3 | 게이트 강등 X — ProfitGuard 진입 차단 ([L2-Tier2] Tier 2: size_mult 0.6 < 최소 1.0 요구) (체크리스트 등급=C, … |
| 3 | 점심 휴식 구간 (11:50~13:00 OTHER) — 체크리스트 8_time 실패 |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.2pt > ATR×5.0=13.7pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.8pt > ATR×5.0=13.4pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.8pt > ATR×5.0=11.4pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.3pt > ATR×5.0=10.1pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.8pt > ATR×5.0=9.8pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.0pt > ATR×5.0=9.2pt (시가=1118.78 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar, 10_chase |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 10_chase |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.9pt > ATR×5.0=9.9pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.1pt > ATR×5.0=9.4pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.5pt > ATR×5.0=9.6pt (시가=1118.78 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×31, `3_vwap`×9, `6_foreign`×8, `7_prev_bar`×7, `4_cvd`×6, `5_ofi`×3, `10_chase`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `연속 손절 1회` ×1
- `연속 손절 2회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 18건 · 최대 37875ms · 5초 초과 4건

상위 — 37875ms, 14422ms, 5532ms, 5203ms, 4500ms, 4172ms, 3719ms, 3672ms

> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **4건**이다. CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260818_WARN.log`
```
--- ConstOut ×5(표본)
09:36:58 2026-08-18 09:36:58 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:30:58 2026-08-18 11:30:58 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:24:59 2026-08-18 12:24:59 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
12:57:59 2026-08-18 12:57:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×2(표본)
13:08:37 2026-08-18 13:08:37 [WARNING] SYSTEM: [CB] 연속 손절 1회
13:19:39 2026-08-18 13:19:39 [WARNING] SYSTEM: [CB] 연속 손절 2회
--- [ExitCooldown] ×8(표본)
10:21:59 2026-08-18 10:21:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:23:59)
10:21:59 2026-08-18 10:21:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:23:59)
10:40:59 2026-08-18 10:40:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:42:59)
10:40:59 2026-08-18 10:40:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:42:59)
--- [SHAP] 슬로우 ×2(표본)
12:18:03 2026-08-18 12:18:03 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1978ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:29:00 2026-08-18 13:29:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1080ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:24 2026-08-18 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:01:00 2026-08-18 09:01:00 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:06:02 2026-08-18 09:06:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:31:59 2026-08-18 09:31:59 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

### `logs/20260818_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:58 2026-08-18 09:36:58 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:39:00 (const_output)
09:36:58 2026-08-18 09:36:58 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:58 2026-08-18 09:36:58 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=87ms fit=48ms total=137ms
09:37:58 2026-08-18 09:37:58 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
```

### `logs/20260818_SIGNAL.log`
```
--- ConfFloorGuard ×2(표본)
09:05:58 2026-08-18 09:05:58 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3920 (conf_floor=0.330, min_conf=0.392, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:29:58 2026-08-18 10:29:58 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3936 ≥ 필요 0.3730
--- ConstOut ×8(표본)
09:36:58 2026-08-18 09:36:58 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:37:58 2026-08-18 09:37:58 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
11:30:58 2026-08-18 11:30:58 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
11:30:59 2026-08-18 11:30:59 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
--- WeightCollapse ×8(표본)
09:07:59 2026-08-18 09:07:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:59 2026-08-18 09:10:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:58 2026-08-18 09:13:58 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:16:59 2026-08-18 09:16:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.434
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.413
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.409
--- 안전망 ×8(표본)
09:07:59 2026-08-18 09:07:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:59 2026-08-18 09:10:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:13:58 2026-08-18 09:13:58 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:59 2026-08-18 09:16:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260818_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:05 2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:41:05 2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2002 < conf_floor=0.3300 (span=0.00040 auc=0.536 out_max=0.2002, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:05 2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00033 auc=0.529 out_max=0.2002 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=85) → 보정 미적용, raw 통과
08:41:05 2026-08-18 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00064 auc=0.556 out_max=0.2004 (n=90) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260818_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:14 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 13:48

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260818_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:01:00 [WARNING] _tick_header 간격 3516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 09:01:00 [WARNING] _tick_header 간격 3516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] |
| 10:00 | 장중 초반 | 3 | 09:55:58 [WARNING] 5분 누적 수익률 -0.467% (임계 ±0.294%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 4 | 11:55:58 [WARNING] 5분 누적 수익률 -0.483% (임계 ±0.481%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |

- 이 로그 생존구간: 08:41 ~ 13:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260818_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 90 | 08:40:47 [INFO] 활성화 | file=logs\crash_fault.log PID=21660 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:22 [INFO] alive ticks=1242 code=A0569 close=1117.84 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 197 | 08:54:07 [INFO] #2000 code=A0569 raw_time=85409 parsed=08:54:09 price=1122.44 vol=1 bid1=1122.10 ask1=1122.40 flag=49 side=BU… |
| 10:00 | 장중 초반 | 194 | 09:54:04 [INFO] #29600 code=A0569 raw_time=95406 parsed=09:54:06 price=1138.44 vol=1 bid1=1138.44 ask1=1138.50 flag=50 side=S… |
| 12:00 | 장중 중간점 | 183 | 11:54:15 [INFO] #77500 code=A0569 raw_time=115416 parsed=11:54:16 price=1091.02 vol=1 bid1=1091.08 ask1=1091.38 flag=50 side=… |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 13:49

**매분 루프 커버리지 09:00~15:10: 290/371분 (78.2%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 13:50 | 15:10 | 81 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260818_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:21 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0294) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 97 | 08:49:58 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0352) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 173 | 08:54:58 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0401) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 226 | 09:55:58 [WARNING] 1m 'macro_vix' scale=0.0016 → floor=0.10 적용 (z-score 폭발 방지) |
| 12:00 | 장중 중간점 | 251 | 11:54:58 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |

- 이 로그 생존구간: 08:40 ~ 13:48

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.8MB · 마지막 갱신 2026-08-17 17:42

최근 헤딩 8개:
```
## 2026-08-17 (MW0601 473차 후속2 — 장후 점검 / KRX 휴장일)
### [0] 전제 — 휴장일이고 P0는 0건이다
### [1] EOD 재학습 미완주 확정 (P1 — 장전 1-2의 후속 확정)
### [2] `session_state.json` P8 스탬프 2키 소실 (P1 — 🆕 신규)
### [3] 장후 뼈대 4단계가 "무증거"로 지나갔다 (P2 — 🆕 신규)
### [4] 점검 세션 3개 동시 실행 (P2 — 🆕 신규)
### [5] 오탐 정정 — 재인용 금지 대상에 준해 다룰 것
### [검증]
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
train_eod.py`는 **`py310_64`** —
한 커밋에 담되 각 런타임에서 컴파일 확인.

### [3] 장후 뼈대 4단계가 "무증거"로 지나갔다 (P2 — 🆕 신규)

수집기 §11 적신호 **6·7·8·10**(15:10 흔적 없음 / `daily_close_done` 없음 /
`eod_retrain_done` 없음 / 진입 0)은 **휴장일이면 전부 정상**인데 적신호로 뜬다.
**계측 4원칙 ②의 확장** — *"휴장이라 안 돈 것"* 과 *"돌았어야 하는데 죽은 것"* 이
같은 표현(로그 부재)을 갖는다.

**결정**: PF-3 — 수집기가 `config/krx_holidays.py`를 읽어 비거래일 배지를 찍고
6·7·8·10을 **삭제가 아니라 `(비거래일 — 정상)`으로 강등**한다.
⚠ **삭제 금물** — 계측 4원칙 ③(탈락 가시화). 없어진 신호는 확인할 수 없고,
거래일 판정이 틀리면 진짜 15:10 미이행이 숨는다.

**Why**: 오탐에 익숙해지면 진짜 미이행이 같은 자리에 섞여도 걸러진다.
471차 F-1이 복구한 15:10 1차 경로가 **6개월간 라이브 0회**였는데 아무도 몰랐던
이유가 정확히 이것이다("조용히 성립하는 것처럼 보였다").

**부수 확정**: 오늘 **F-1H(하트비트 1일차)는 판정 불가**다 — 본체가 15:11에 부재해
`[SchedForceExit]`가 나올 수 없었다. F-1R·F-4M과 함께 **08-18로 이월**한다.
`trades.exit_reason LIKE '%15:10%'`는 여전히 **전기간 0건**(실측 재확인).

### [4] 점검 세션 3개 동시 실행 (P2 — 🆕 신규)

pre 16:48:00 / intra 16:49:16 / post 16:55:24 — 세 다이제스트의 리포 경로가 전부
다르다(별개 세션). pre 세션은 **본 세션 진행 중인 16:57에** 리포트와
`DECISION_LOG.md`(1.8MB)에 append했다. MW0602가 `483d41a`(470차 후속7)에서
*"동시 세션 reset으로 유실 → 재커밋"* 을 이미 겪었다.
추가로 **pre 다이제스트는 헤더 PC가 `UNKNOWN`(host=claude)인데 파일명만 `MW0601`**로
맞춰져 있다 — SKILL.md 1-B *"어느 PC의 관찰인지 영영 모르게 된다"* 에 걸린다.

**결정**: G-3 — `dev_memory/.dailycheck.lock` 도입, 획득 실패 시
`dev_memory/pending/<PC>-<날짜>-<국면>.md` 조각으로 떨어뜨리고 다음 세션이 흡수.
스테일 잠금은 **mtime 10분 초과 시 무시**(471차 `.git/index.lock` 전례).

### [5] 오탐 정정 — 재인용 금지 대상에 준해 다룰 것

- **수집기 §11 "미커밋 변경 454건"은 사실이 아니다.** Linux 샌드박스 CRLF 아티팩트다.
  `git diff --stat` 430파일/241,400+ ↔ `git diff --ignore-cr-at-eol --stat`
  **10파일 / 404+ / 20−**. 수집기 §2·§11의 미커밋 건수는 **샌드박스 실행 시 신뢰 금지**.
- **`[SHAP] … CORE안전=⚠️`(08:41:14)는 만성이다** — 08-13 7회·08-14 10회 전부 동일.
- **`[Calibration]` WARNING 143건도 신규가 아니다** — 기동 워밍업 시퀀스이며 일별 실측이
  평탄하다(08-10 157 / 08-11 148 / 08-12 145 / 08-13 141 / 08-14 144 / **08-17 143**).
  최종 상태 `보정기 복원 완료 (… degenerate=False unreachable=False)`. 오늘 로그가
  288행뿐이라 **비율만 높아 보이는 착시**다(08-14는 2,814행 중 144건).
- **설정 불변식 `미발견` 5종**은 장전 1-1이 원인(브랜치 분기)까지 확정했다.
  실측 재확인만: 5종 모두 `config/settings.py` 출현 **0회**, repo 전체에서 수집기
  자신(`collect_evidence.py:179~187`) 외 0회. 해당 커밋 10건은 전부
  `[MW0602]`이고 `v9-dev`에 0건. `git rev-list --left-right --count v9-dev...origin/dev`
  = **320 / 315**. 처분은 **주간회의 안건**(점검 세션 단독 결정 사안 아님).

### [검증]

코드 변경 0건이므로 회귀 테스트 대상 없음. 라이브 DB는 **읽기전용 조회만**
(현재 15:35 이후로 장중 분석 차단 구간 아님). 손익·승패 집계는 **포지션 단위**로
수행했다(계측 4원칙 ① — `entry_ts||direction||entry_price` 고유조합, 청산 레그
`COUNT(*)`와 분리 표기). 당일 표본 0이라 §5 수익률 향상방안은 **도출 불가**로 남겼다 —
억지로 채우면 일반론이 된다(SKILL.md §5).

```

</details>

### dev_memory/NEXT_TODO.md — 929.3KB · 마지막 갱신 2026-08-17 17:42

최근 헤딩 8개:
```
### 고도화
### 다음 거래일(08-18) 관측 — 본 세션 추가분
## 2026-08-17 (MW0601 473차 후속2 — 장후 점검 / KRX 휴장일) 신규 항목
### 🔴 최우선 — 다음 거래일(2026-08-18)에 답이 나오는 것
### Fix — 08-18 장 마감 후 적용 (오늘 밤 금지: 08-18 EOD가 미검증 코드로 돈다)
### 조사 (fix가 아니다)
### 고도화
### 문서·운영
```

미완료 체크박스 **1337건** (끝에서 30건)
```
- [ ] **실전전환 ⑨ TOX-SEVERE-SPREAD 처분** — 473차 F-8 Phase A `INSUFFICIENT`(ETA 7.1개월).
- [ ] **F-5 수집기 git 호출부 CRLF 정규화 + `--pc` 인자 (P1)** —
- [ ] **F-6 백필 스크립트 기동·종료 흔적 로깅 (P2)** —
- [ ] **F-7 런처 정상 종료 문구 정정 (P2)** — `start_mireuk.bat` 재시작 판정 블록에서
- [ ] **G-4 `Calibration` 기동 복원 스윕 로그 레벨 하향 (이번 주)** —
- [ ] **G-5 `references/phases.md` D절 "휴장일" 신설 (이번 주, 장전 G-1과 같은 커밋)** —
- [ ] **O-9 `20260818_BACKFILL.log` 크기** — 0바이트면 F-6을 **P2 → P1 승격**(휴장일 한정이
- [ ] **O-10 `LEARNING` WARNING 중 `Calibration` 비율** — 오늘 143/143(100%).
- [ ] **O-11 예약 3국면 실행 시각 3개 전부** — 오늘 16:48/16:49/16:55.
- [ ] **O-12 `[SHAP] … CORE안전=⚠️` 상세** — 오늘 1행만 있고 대상 피처 불명.
- [ ] **O-1 EOD 재학습 완주 확인** — `logs/retrain_eod_20260818.log`가 10KB 이상 +
- [ ] **O-2 `session_state.json` P8 키 재생성** — 08-18 EOD 완주 후
- [ ] **O-3 P8 키 잔존(C-2 2단계)** — 08-19 08:41 기동 **후에도** 두 키가 남아 있는지.
- [ ] **F-1R 15:10 강제청산 리허설 — 08-18로 이월(사용자 실행 필요).**
- [ ] **F-1H 하트비트 1일차 — 08-18로 이월.** 오늘 본체가 15:11에 부재해
- [ ] **F-4M 스키마 마이그레이션 1일차 — 08-18로 이월.** 오늘 신규 행 0건.
- [ ] **O-8 08-18 08:40 자동 기동 여부** — 오늘 12:55 `user_close` 수동 종료 후
- [ ] **O-7 예약 점검 시각(C-3)** — 장전 점검이 08:57±5분에 도는지.
- [ ] **PF-1 `retrain_eod.py` 거래일 게이트 + 완주/중단 흔적 (P1)** —
- [ ] **PF-2 `session_state` 완료 스탬프 가시화 (P1)** —
- [ ] **PF-3 수집기 §11 비거래일 인지 (P2) — 장전 G-1과 통합, 중복 구현 금지** —
- [ ] **C-2 `p8_last_success_date`·`eod_retrain_ok_date` 소실 근본원인** —
- [ ] **C-1 EOD 재학습이 왜 15:46:34에 멈췄는가** — Windows 이벤트 뷰어 15:46~15:48
- [ ] **G-1 재학습 파이프라인 완주 마커 (이번 주)** — 시작 시
- [ ] **G-3 점검 세션 동시 실행 직렬화 (이번 주)** — `dev_memory/.dailycheck.lock`.
- [ ] **G-2 휴장일 정상 프로파일 기준선 (26주 WFA 주기)** —
- [ ] **커밋 대기 — 473차 실질 변경 10파일 + untracked 2종.**
- [ ] **정기점검 산출물 untracked 16종 추적 편입** — 장전 1-5와 동일 항목(중복 착수 금지).
- [ ] **브랜치 격차 처분을 주간회의 안건으로** — `v9-dev` ↔ `origin/dev` = **320 / 315**.
- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **12일** 남음. 오늘 `9999` 유지 확인.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
장전 G-1과 통합, 중복 구현 금지** —
  `collect_evidence.py` 적신호 생성부가 `config/krx_holidays.py`를 읽어
  다이제스트 첫 줄에 `· 비거래일(휴장)` 배지를 찍고, 적신호 6·7·8·10을
  **삭제가 아니라 `(비거래일 — 정상)`으로 강등**.
  ⚠ 삭제 금물 — 계측 4원칙 ③(탈락 가시화). 거래일 판정이 틀리면 진짜 15:10 미이행이 숨는다.
  ⚠ 수집기는 표준 라이브러리 전용 — 외부 의존이 붙으면 날짜 리스트만 정규식 파싱.
  검증: 2026-08-17 날짜로 `--phase post` 재실행 → 6·7·8·10만 강등되고
  1~5(브랜치 격차)는 그대로 남는지.

### 조사 (fix가 아니다)

- [ ] **C-2 `p8_last_success_date`·`eod_retrain_ok_date` 소실 근본원인** —
  08-14 15:48:45 기록 로그는 있는데 08-17 08:41 파일에 없다. 08-14~08-17 사이 쓰기 경로는
  전부 merge 기반이고, `[SessionState] load failed:` 경고는 최근 6일 **0건**이다.
  조사 대상: 그 사이 `data/session_state.json` 백업/복원·수동 편집 여부.
  **판정은 O-2 → O-3 관측으로 낸다.**

- [ ] **C-1 EOD 재학습이 왜 15:46:34에 멈췄는가** — Windows 이벤트 뷰어 15:46~15:48
  프로세스 종료 기록 · 작업 스케줄러 `Maitreya_EODretrain` 마지막 실행 결과 코드 ·
  `EOD_RETRAIN.bat` 콘솔 잔존 여부. **원인과 무관하게 PF-1은 유효**하다
  ("흔적을 안 남긴다"는 결함이 독립적으로 성립).

### 고도화

- [ ] **G-1 재학습 파이프라인 완주 마커 (이번 주)** — 시작 시
  `data/eod_retrain_running_{d}.txt`(PID·시작시각) 생성, `finally`에서 삭제 + 결과 마커.
  `running`만 남으면 **"시작했고 끝내지 못했다"** 를 즉시 안다. 수집기 §11에
  `EOD 중단 흔적` 적신호로 배선. ⚠ 기동 시 전일 이전 `running` 마커 정리 필요.
  **선행: PF-1**(`try/finally`를 두 번 만들지 않는다).

- [ ] **G-3 점검 세션 동시 실행 직렬화 (이번 주)** — `dev_memory/.dailycheck.lock`.
  획득 실패 시 `dev_memory/pending/<PC>-<날짜>-<국면>.md` 조각으로 떨어뜨리고
  다음 세션이 흡수. 스테일 잠금은 **mtime 10분 초과 시 무시**(471차 `.git/index.lock` 전례).
  근거: 오늘 pre 16:48 / intra 16:49 / post 16:55 3세션이 겹쳤고 pre가 본 세션 진행 중
  `DECISION_LOG.md`(1.8MB)에 append했다. MW0602 `483d41a` 유실 전례.
  함께 처리: **pre 다이제스트 헤더 PC가 `UNKNOWN`인데 파일명만 `MW0601`** (헤더-파일명 불일치).

- [ ] **G-2 휴장일 정상 프로파일 기준선 (26주 WFA 주기)** —
  `docs/정기점검/매일점검/baseline_nontrading_<PC>.json`에 로그별 행수·채널 분포·마커
  유무를 휴장일마다 1행 누적. 거래일 점검에서 당일 프로파일이 그 기준선에 가까우면
  "장이 열렸는데 휴장일처럼 조용하다"를 자동 탐지.
  근거: 오늘 LEARNING 288행 vs 08-14 2,814행(약 1/10).
  ⚠ 표본이 연 10여 일뿐 — **판정에 쓰지 말고 경보에만**(313차 원칙).
  **선행: PF-3.**

### 문서·운영

- [ ] **커밋 대기 — 473차 실질 변경 10파일 + untracked 2종.**
  `git diff --ignore-cr-at-eol --stat` = 10파일 / 404+ / 20−.
  라이브 경로: `learning/prediction_buffer.py` · `utils/db_utils.py` · `config/settings.py`.
  untracked: `scripts/spread_extreme_watch.py` · `scripts/feature_superset_expand.py`.
  ⚠ **수집기가 표시한 "454건"은 샌드박스 CRLF 아티팩트다 — 재인용 금지.**
- [ ] **정기점검 산출물 untracked 16종 추적 편입** — 장전 1-5와 동일 항목(중복 착수 금지).
- [ ] **브랜치 격차 처분을 주간회의 안건으로** — `v9-dev` ↔ `origin/dev` = **320 / 315**.
  점검 세션 단독 결정 사안 아님. 설정 불변식 `미발견` 5종의 근본 원인이다.
- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **12일** 남음. 오늘 `9999` 유지 확인.
  ⚠ 오늘은 휴장이라 표본 진전 0.

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

### `docs/정기점검/매일점검` — 36개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/evidence_MW0601-20260818_pre.md` | 60.5KB | 08-18 13:44 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 12.5KB | 08-17 17:47 |
| `docs/정기점검/매일점검/MW0601-20260817-점검리포트-post.md` | 42.5KB | 08-17 17:08 |
| `docs/정기점검/매일점검/MW0601-20260817-점검리포트-intra.md` | 27.5KB | 08-17 17:06 |
| `docs/정기점검/매일점검/MW0601-20260817-점검리포트-pre.md` | 35.4KB | 08-17 16:57 |
| `docs/정기점검/매일점검/evidence_MW0601-20260817_post.md` | 44.8KB | 08-17 16:55 |
| `docs/정기점검/매일점검/evidence_MW0601-20260817_intra.md` | 43.9KB | 08-17 16:49 |
| `docs/정기점검/매일점검/evidence_MW0601-20260817_pre.md` | 43.7KB | 08-17 16:48 |

### `docs/정기점검/금요일점검` — 51개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260814.md` | 163.4KB | 08-14 15:49 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260814.json` | 83.5KB | 08-14 15:49 |
| `docs/정기점검/금요일점검/MW0602/exit_expectancy_map_20260810.md` | 1.8KB | 08-14 07:47 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. `logs/20260818_SYSTEM.log`: 매분 루프 커버리지 290/371분 (78.2%) — 루프가 빠진 구간이 있다
7. `logs/20260818_SYSTEM.log`: 13:50~15:10 **연속 81분 매분 루프 기록 없음**
8. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
9. 메인 스레드 블로킹 5초 초과 **4건** (최대 37875ms) — `CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인
10. `logs/20260818_WARN.log`: **ConstOut** 5건(표본)
11. `logs/20260818_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20260818_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20260818_SIGNAL.log`: **ConstOut** 8건(표본)
14. `logs/20260818_LEARNING.log`: **축퇴** 8건(표본)
15. 미커밋 변경 455건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260818*.log` (Windows) / `grep 강제청산 logs/*20260818*.log`*