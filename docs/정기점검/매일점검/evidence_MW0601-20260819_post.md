# 미륵이 증거 다이제스트 — 2026-08-19 / POST

- 생성 2026-08-19 16:22:00 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/focused-practical-bardeen/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260819` · `2026-08-19` · `260819` · `0819`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **20개** 파일 · 20개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260819.txt` | 133B | 08-19 16:08 |
| `launcher_{DATE}_084001_22417.log` | 1 | `logs/Mireuk_batch/launcher_20260819_084001_22417.log` | 1.3MB | 08-19 13:41 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260819.log` | 24.4KB | 08-19 16:08 |
| `retrain_intraday_{DATE}_093601.log` | 1 | `logs/retrain_intraday_20260819_093601.log` | 2.4KB | 08-19 09:36 |
| `retrain_intraday_{DATE}_101001.log` | 1 | `logs/retrain_intraday_20260819_101001.log` | 2.4KB | 08-19 10:10 |
| `retrain_intraday_{DATE}_104301.log` | 1 | `logs/retrain_intraday_20260819_104301.log` | 2.4KB | 08-19 10:43 |
| `retrain_intraday_{DATE}_114901.log` | 1 | `logs/retrain_intraday_20260819_114901.log` | 2.4KB | 08-19 11:49 |
| `retrain_intraday_{DATE}_123601.log` | 1 | `logs/retrain_intraday_20260819_123601.log` | 2.4KB | 08-19 12:36 |
| `retrain_intraday_{DATE}_132601.log` | 1 | `logs/retrain_intraday_20260819_132601.log` | 2.4KB | 08-19 13:26 |
| `{DATE}_DATA.log` | 1 | `logs/20260819_DATA.log` | 251.4KB | 08-19 13:41 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260819_DEBUG.log` | 171.4KB | 08-19 13:41 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260819_HEALTH.log` | 3.3KB | 08-19 13:11 |
| `{DATE}_HOGA.log` | 1 | `logs/20260819_HOGA.log` | 38.4MB | 08-19 13:41 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260819_LEARNING.log` | 216.3KB | 08-19 13:41 |
| `{DATE}_MICRO.log` | 1 | `logs/20260819_MICRO.log` | 771.2KB | 08-19 13:41 |
| `{DATE}_PROBE.log` | 1 | `logs/20260819_PROBE.log` | 73.1KB | 08-19 13:41 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260819_SIGNAL.log` | 502.4KB | 08-19 13:41 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260819_SYSTEM.log` | 625.9KB | 08-19 13:51 |
| `{DATE}_TRADE.log` | 1 | `logs/20260819_TRADE.log` | 12.0KB | 08-19 13:38 |
| `{DATE}_WARN.log` | 1 | `logs/20260819_WARN.log` | 62.4KB | 08-19 13:25 |

## 2. 코드·커밋 상태

- HEAD `624a275` · 브랜치 `v9-dev` · 미커밋 463건
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
… 외 423건
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

_본문 미열람(설정): `20260819_HOGA.log` 38.4MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/eod_retrain_done_20260819.txt`** — 133B · 08-19 16:08:44
```
completed: 2026-08-19 16:08:44
rows: 40400
cols: 97
horizons_replaced: 6/6
t_load_s: 38.0
t_retrain_s: 182.4
t_total_s: 220.9
```

_다이제스트 대상 8/18개 (중요도순). 제외: `retrain_intraday_20260819_101001.log`, `retrain_intraday_20260819_104301.log`, `retrain_intraday_20260819_114901.log`, `retrain_intraday_20260819_132601.log`, `retrain_intraday_20260819_123601.log`, `20260819_MICRO.log`, `20260819_DATA.log`, `20260819_PROBE.log`_

### `logs/20260819_TRADE.log` — 12.0KB · 95행 · 최종 13:38:01

- 형식 평문 · 시각 인식 95행 · INFO=95

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-19 08:41:18 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-19 09:49:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,507) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-19 09:49:01 [INFO] TRADE: [진입체크] LONG→LONG 3계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas✅ coun✅ | conf=40.7%
2026-08-19 09:49:01 [INFO] TRADE: [Chejan] 상태=접수 주문번호=814 code=A0569 방향=LONG 체결=3 미체결=0
  …
2026-08-19 13:23:31 [INFO] TRADE: [Chejan] 상태=체결 주문번호=3197 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-19 13:23:31 [INFO] TRADE: [Position] 체결청산 SHORT @ 1017.88 | PnL=+0.26pt (+11,473원) | 하드스톱(틱)
2026-08-19 13:23:31 [INFO] TRADE: [청산 완료] PnL=+0.26pt (+11,473원)
2026-08-19 13:38:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,610,582) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdvisedSkip]
2026-08-19 13:38:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 1계약 C급 (meta=0.67 tox=0.70 joint=0.465)
```

</details>

**채널** — `TRADE`×95

**컴포넌트 상위 15** — `Chejan`×26, `Position`×20, `주문요청`×10, `Sizer`×8, `체결진입`×6, `진입체크`×4, `청산 완료`×4, `JointGateBlock 차단`×4, `TickTP1`×3, `TickStop-S0C`×3, `체결진입보정`×2, `ProfitGuard`×1, `TP1 부분청산`×1, `체결청산-부분`×1, `손절1차 분할체결`×1

### `logs/20260819_WARN.log` — 62.4KB · 287행 · 최종 13:25:01

- 형식 평문 · 시각 인식 287행 · ERROR=1, WARNING=286

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-19 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-19 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-19 08:41:27 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3594ms — live 중단 원인 분석용
  …
2026-08-19 13:23:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 94ms account=333044256
2026-08-19 13:23:33 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-19 13:23:33 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-19 13:23:33 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 78ms account=333044256
2026-08-19 13:25:01 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
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

**WARNING — 태그 29종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 87 | 08:41:21 | 13:23:33 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 26 | 09:49:01 | 13:23:31 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='814' | pending='ENTRY:LONG qty=3 filled=0 order_no=? reason=진입 req_at=09:49:01.502' | position… |
| `ChejanMatch` | 26 | 09:49:01 | 13:23:31 | order_no='814' | pending='ENTRY:LONG qty=3 filled=0 order_no=814 reason=진입 req_at=09:49:01.502' | pending_matched=True |
| `PendingOrder` | 20 | 09:49:01 | 13:23:31 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1018.74, 'reason': '진입', 'hint_source': '', 'atr': 2.2271, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `PipePerf` | 14 | 09:00:02 | 12:37:03 | total=1806ms | S0=4ms S1=10ms S2=1ms S3=0ms S4=229ms S5=718ms S6=810ms S7=29ms S8=5ms |
| `CB⑤` | 14 | 09:00:02 | 12:37:03 | 파이프라인 1806ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 12 | 09:00:02 | 13:10:01 | level=WARNING degraded=OFF | latency=1806ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |
| `ScalerRefresh` | 12 | 09:05:00 | 13:23:01 | 5분 누적 수익률 -1.379% (임계 ±0.815%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `EntryFillFlow` | 8 | 09:49:01 | 13:23:02 | actual_side='LONG' | after='LONG 1계약 @ 1018.32' | applied_side='LONG' | before='FLAT' | fill_no='' | fill_price=1018.32 | fill_qty=1 | order_no='814' | pending='ENTRY:LONG qty=3 filled=1 order_no=814 reason=진입 req_at=09:49:01.502' |
| `ExitCooldown` | 8 | 09:57:22 | 13:23:31 | 하드스톱(틱) 후 2분 재진입 금지 (until 09:59:22) |
| `HealthPolicy` | 6 | 09:01:01 | 12:38:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1806ms quality=0.86 cache=0s exc10m=0) | cause=S6(810ms) |
| `ConstOut` | 6 | 09:35:01 | 13:25:01 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

**채널** — `SYSTEM`×275, `HEALTH`×12

**컴포넌트 상위 15** — `LiveDBG`×87, `ChejanFlow`×26, `ChejanMatch`×26, `PendingOrder`×20, `PipePerf`×14, `CB⑤`×14, `Health`×12, `ScalerRefresh`×12, `EntryFillFlow`×8, `ExitCooldown`×8, `HealthPolicy`×6, `ConstOut`×6, `ExitFillFlow`×5, `EntryAttempt`×4, `EntrySendOrderResult`×4

### `logs/20260819_SYSTEM.log` — 625.9KB · 4492행 · 최종 13:51:22

- 형식 평문 · 시각 인식 4485행 · INFO=4485, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21612 | 행감지=30s all_threads=True
2026-08-19 08:40:59 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-19 08:40:59 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-19 08:40:59 [INFO] SYSTEM: 미륵이 초기화
2026-08-19 08:40:59 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-18) 종가 버퍼 로드: 385봉
  …
2026-08-19 13:41:21 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-2286,foreign:-5760,institution:+8666}
2026-08-19 13:41:21 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-2286,foreign:-5760,institution:+8666}
2026-08-19 13:41:21 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-267787 nonarb=-2295812
2026-08-19 13:41:21 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-267787 nonarb=-2295812
2026-08-19 13:51:22 [INFO] SYSTEM: [OptionChain][Worker] 완료 601493ms | target=24 valid=24 PCR=0.103 ATM_PCR=1.000 GEX=169.19B
```

</details>

**채널** — `SYSTEM`×4485

**컴포넌트 상위 15** — `CybosInvestorRaw`×1122, `CybosRT-TICK`×935, `CybosRT-ROLLOVER`×296, `BAR-CLOSE`×296, `CVD-ANCHOR`×296, `TickUI`×294, `S6Detail`×282, `PipePerf`×282, `MicroRegime`×82, `System`×74, `BalanceUI`×53, `RegimeFingerprint`×52, `CybosEvent`×52, `IntradayRegime`×51, `OptionChain`×38

### `logs/20260819_SIGNAL.log` — 502.4KB · 4361행 · 최종 13:41:01

- 형식 평문 · 시각 인식 4361행 · WARNING=2107, INFO=2254

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.403
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.395
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.391
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.399
2026-08-19 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
  …
2026-08-19 13:41:01 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.40→0.37 (완화)
2026-08-19 13:41:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=43.6% grade=X regime=NEUTRAL
2026-08-19 13:41:01 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 4회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-08-19 13:41:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=43.6% grade=X micro=추세장
2026-08-19 13:41:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1308 | 09:00:02 | 13:30:02 | 1m 'macro_vix' scale=0.0036 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 258 | 08:45:21 | 13:30:02 | 1m CORE 'ofi_norm' raw_std≈0(0.0280) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 196 | 09:00:00 | 13:24:01 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 191 | 09:00:00 | 13:24:01 | ts=08:59 horizon=1m age=1m max_z=+4.99(cancel_add_ratio) extreme=1 |
| `Checklist` | 85 | 09:06:00 | 13:34:01 | 신뢰도 미달 34.9% < 37.3% → 강제 X등급 |
| `WeightCollapse` | 61 | 09:07:00 | 13:37:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 7 | 09:35:01 | 13:25:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4190 (conf_floor=0.330, min_conf=0.419, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4361

**컴포넌트 상위 15** — `ScalerFloor`×1326, `SIGNAL`×564, `ScalerRefresh`×297, `Ensemble`×284, `FQAdj`×279, `ZeroDiag`×245, `Model`×238, `ScalerMonitor`×191, `MetaGate`×185, `Checklist`×131, `ATR-Horizon`×108, `MicroRegime`×82, `InstabilityGate`×79, `WeightCollapse`×61, `차단`×60

### `logs/20260819_LEARNING.log` — 216.3KB · 2105행 · 최종 13:41:01

- 형식 평문 · 시각 인식 2105행 · WARNING=136, INFO=1969

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-19 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00024 auc=0.524 out_max=0.3178 (기준 auc<0.53 and span<0.020, 기저율=0.3176 n=85) → 보정 미적용, raw 통과
2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00035 auc=0.536 out_max=0.3336 (n=90) → 보정 재적용
2026-08-19 08:41:05 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3336 < conf_floor=0.3300 (n=90) → 보정 재적용
  …
2026-08-19 13:41:01 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=36.2% FL)
2026-08-19 13:41:01 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=42.4% DN)
2026-08-19 13:41:01 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=48.9% 예측=FL 실제=UP)
2026-08-19 13:41:01 [INFO] LEARNING: [OnlineLearner] 15m SGD UP붕괴 자동 복구 (≥80% 12분 지속) → 모델·스케일러 리셋
2026-08-19 13:41:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=13.3%
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 135 | 08:41:05 | 13:21:01 | 하한 도달불가 — out_max=0.3252 < conf_floor=0.3300 (span=0.00027 auc=0.531 out_max=0.3252, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Buffer-Timing` | 1 | 12:36:01 | 12:36:01 | total=310ms raw_fetch=5ms pred_select=3ms pred_update=1ms pred_insert=286ms verified=3 |

**채널** — `LEARNING`×2105

**컴포넌트 상위 15** — `LEARNING`×912, `SGD`×282, `sigma`×269, `Calibration`×265, `Bias⚠`×101, `Bias`×89, `MetaConf`×57, `ScalerWarmup`×39, `OnlineLearner`×32, `GBM-64`×12, `GBM`×12, `BiasReset`×11, `SHAP`×10, `RF`×7, `ExtremityCorrector`×2

### `logs/20260819_HEALTH.log` — 3.3KB · 24행 · 최종 13:11:01

- 형식 평문 · 시각 인식 24행 · WARNING=12, INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1806ms | quality=0.86 | cache_age=39s | exceptions_10m=0
2026-08-19 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=639ms | quality=0.86 | cache_age=98s | exceptions_10m=0
2026-08-19 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 318ms (표본 20분)
2026-08-19 09:36:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=461ms | quality=1.00 | cache_age=181s | exceptions_10m=0 [GBM재학습중→lat임계 5000/10000ms]
2026-08-19 09:37:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2148ms | quality=1.00 | cache_age=60s | exceptions_10m=0
  …
2026-08-19 12:19:02 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=262ms | quality=1.00 | cache_age=61s | exceptions_10m=0
2026-08-19 12:37:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2316ms | quality=1.00 | cache_age=41s | exceptions_10m=1
2026-08-19 12:38:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=404ms | quality=1.00 | cache_age=99s | exceptions_10m=1
2026-08-19 13:10:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=387ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-19 13:11:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=298ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 12 | 09:00:02 | 13:10:01 | level=WARNING degraded=OFF | latency=1806ms | quality=0.86 | cache_age=39s | exceptions_10m=0 |

**채널** — `HEALTH`×24

**컴포넌트 상위 15** — `Health`×23, `HealthTrend`×1

### `logs/retrain_eod_20260819.log` — 24.4KB · 176행 · 최종 16:08:45

- 형식 평문 · 시각 인식 176행 · WARNING=17, INFO=159

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-19 15:45:03,720 [INFO] EOD_RETRAIN: =======================================================
2026-08-19 15:45:03,721 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-19 15:45:03,721 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-19 15:45:03,721 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-19 15:45:03,721 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-19 16:08:45,462 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0334 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-19 16:08:45,462 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1284 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-19 16:08:45,465 [INFO] SIGNAL: [ScalerRefresh] ts=16:08 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-08-19 16:08:45,470 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-19 16:08:45,471 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 16:05:49 | 16:07:36 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1590봉(86%)이 현행 학습구간 (현행 cutoff=2026-08-18 14:39:00 ≥ 홀드아웃 시작=2026-08-11 10:57:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-18 14:39 >= holdout_start=2026-08-11 10:57 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-18 … |
| `ScalerRefresh` | 6 | 16:08:45 | 16:08:45 | 1m CORE 'ofi_norm' raw_std≈0(0.0346) → identity(0,1) 강제 (FLAT 100% 방지) |
| `GuardGhost` | 4 | 16:05:59 | 16:06:12 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-19 11:18:00까지)인데 acc.txt=0.4094는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `WaitDC` | 1 | 16:05:04 | 16:05:04 | daily_close() 20분 대기 타임아웃 — pkl 경합 위험 있으나 강제 진행 |

**채널** — `LEARNING`×65, `EOD_RETRAIN`×60, `SIGNAL`×43, `FEAT_REG`×6

**컴포넌트 상위 15** — `WaitDC`×42, `ScalerFloor`×30, `Retrain`×20, `EOD_RETRAIN`×14, `RF`×9, `ScalerRefresh`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `GuardGhost`×4, `RegimeFingerprint`×3

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

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 4 |
| 진입 등록(`[Position] 진입`) | 3 |
| 체결(`[체결진입]`) | 6 |
| 청산(`체결청산`) | 4 |
| 차단(`[차단]`) | 60 |
| 사이저 호출(`[Sizer]`) | 8 |

### 청산 4건 · 승 3 (75%) · 합계 +1.64pt (+75,890원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 09:57:22 | LONG | +1.03 | +50,139 | 하드스톱(틱) |
| 11:21:33 | SHORT | -2.89 | -146,192 | 하드스톱(틱) |
| 11:42:02 | SHORT | +3.24 | +160,470 | TP2(전량) |
| 13:23:31 | SHORT | +0.26 | +11,473 | 하드스톱(틱) |

**청산 사유 분포** — `하드스톱(틱)`×3, `TP2(전량)`×1

> 하드스톱·손절 계열 3/4건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 3건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 11:11:01 | SHORT | 3 | 1016.68 | 3m | neutral |
| 11:26:01 | SHORT | 1 | 1019.88 | 3m | neutral |
| 13:23:01 | SHORT | 1 | 1018.16 | 1m | mean-revert |

계약수 분포 — 1계약×2, 3계약×1

등급 분포 — `A급(원시C)`×2, `C급`×2

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×2, `ofi`×2, `prev`×2, `fore`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×3, **3계약**×5

실제 진입 계약수 — **1계약**×2, **3계약**×1

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×8

### 차단 사유 60건 · 24종

| 건수 | 사유 |
|---|---|
| 31 | 등급X — 미통과 항목: 2_confidence |
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

**체크리스트 미통과 항목 누적** — `2_confidence`×31, `3_vwap`×13, `4_cvd`×7, `7_prev_bar`×7, `5_ofi`×6, `6_foreign`×6, `11_countertrend`×5, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `연속 손절 1회` ×1
- `연속 손절 2회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 26건 · 최대 6766ms · 5초 초과 4건

상위 — 6766ms, 6422ms, 5782ms, 5078ms, 4891ms, 4859ms, 4703ms, 4687ms

> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **4건**이다. CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260819_WARN.log`
```
--- ConstOut ×6(표본)
09:35:01 2026-08-19 09:35:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:09:01 2026-08-19 10:09:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:42:01 2026-08-19 10:42:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:48:01 2026-08-19 11:48:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×2(표본)
11:12:08 2026-08-19 11:12:08 [WARNING] SYSTEM: [CB] 연속 손절 1회
11:21:33 2026-08-19 11:21:33 [WARNING] SYSTEM: [CB] 연속 손절 2회
--- [ExitCooldown] ×8(표본)
09:57:22 2026-08-19 09:57:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:59:22)
09:57:22 2026-08-19 09:57:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:59:22)
11:21:33 2026-08-19 11:21:33 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:24:33)
11:21:33 2026-08-19 11:21:33 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 11:24:33)
--- [SHAP] 슬로우 ×2(표본)
12:35:02 2026-08-19 12:35:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 912ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:23:02 2026-08-19 13:23:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 930ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
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

- 이 로그 생존구간: 08:41 ~ 13:38

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260819_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 11 | 09:00:02 [WARNING] total=1806ms | S0=4ms S1=10ms S2=1ms S3=0ms S4=229ms S5=718ms S6=810ms S7=29ms S8=5ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 13 | 09:00:02 [WARNING] total=1806ms | S0=4ms S1=10ms S2=1ms S3=0ms S4=229ms S5=718ms S6=810ms S7=29ms S8=5ms |
| 10:00 | 장중 초반 | 25 | 09:57:20 [WARNING] 스톱 히트 감지 (틱) LONG tick=1019.42 stop=1019.46 → 즉시 처리 예약 |

- 이 로그 생존구간: 08:41 ~ 13:25

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
| 15:10 | _**오버나이트 금지 — 강제 청산** (절대원칙 1) (이 로그 생존구간 밖)_ | 0 | — |
| 15:18 | _안전망 청산 (STEP 8 5단계 마지막) (이 로그 생존구간 밖)_ | 0 | — |
| 15:40 | _자가학습 일일 마감 + SHAP 피처 심사 (이 로그 생존구간 밖)_ | 0 | — |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 13:51

**매분 루프 커버리지 09:00~15:10: 283/371분 (76.3%)**

연속 3분 이상 기록 없는 구간 2개:

| 시작 | 끝 | 분 |
|---|---|---|
| 13:42 | 13:50 | 9 |
| 13:52 | 15:10 | 79 |

**08:55~15:12 구간 10분 이상 공백: 1건**

| 시작 | 재개 | 공백(분) |
|---|---|---|
| 13:41 | 13:51 | 10 |

### `logs/20260819_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:21 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0280) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 105 | 08:50:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0344) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 251 | 08:55:01 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0434) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 204 | 09:55:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 12:00 | 장중 중간점 | 112 | 11:54:02 [WARNING] 신뢰도 미달 33.3% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 13:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.9MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-08-19 (MW0601 478차 후속 — 장중 점검)
### [신규 P1] Chejan 선행 레이스로 위험 파라미터 5종이 조용히 기본값으로 진입 — TP1이 설계의 2배
### [신규 P1] STEP 1 채점 커버리지 구조적 결손 — 10m 20% / 15m 13%
### [신규 P2] `references/phases.md` B-1 "T-30 퇴역" 문구가 CLAUDE.md 474차와 충돌
### 기존 항목 갱신 (신규 아님)
### 이미 반영된 사안 — 신규 아님(함정 ①)
### 08-29 CB② 복원 상정에 함께 올릴 것
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
을 이상점으로 보고하게 된다. CLAUDE.md 절대원칙 §3
474차는 정반대다 — *"30m 학습을 중단하면 안 된다 — CB③의 유일한 입력원"*
(`main.py:5546-5553`이 30m·conf>0.38·FLAT제외로만 `record_accuracy()`에 적재).
라이브 실측: `11:49:01 [CB③] acc30m 버퍼 리셋 스킵 — 기존 표본 14건 < 최소 30건`.
**CLAUDE.md가 정본, `phases.md`가 낡았다.** → F-7(F-2·F-4와 같은 커밋).

### 기존 항목 갱신 (신규 아님)

- **G-1/G-2 `ofi_norm` identity 강제 3거래일째** — 오늘 12:35까지 1m CORE 36회 중
  **32회(89%)**, 6개 호라이즌 동시 216행. 08-18 34/36(94%), 08-17 이전 0~6회.
- **O-G IntradayRegime 전이 4일차** — 반일 **42회**(08-14 19 / 08-18 22 종일 대비 2배).
  `day`가 −1.00% 경계에서 진동(11:13→11:14→11:15→11:16 4분 연속 4회).
  ⚠ **실해 미확인** — `[Sizer]` 6회 전부 `레짐배수=0.8` 고정, `min_conf` 무전파.
- **G-A/G-B PSI 라이브** — 하트비트 **40건 · PSI 0.009~0.012 · level=0 전량**. 477차 F-5 정상.
- **GR-3V** — ProfitGuard 차단 여전히 0건 → `src=` 토큰 미확인 유지.
- **ConstOut/장중재학습 4회**(09:35·10:09·10:42·11:48) — 평시 2~6 범위. ⚠ 최근 5거래일
  ConstOut 14건 중 **13건이 `['3m']`** — 3m 편중. `G-3b RouterHealth` 오늘 4회(08-18 3회).

### 이미 반영된 사안 — 신규 아님(함정 ①)

- `[JointGateBlock 차단] meta=0.50 tox=0.70 joint=0.350` ×3 (10:05·10:44·11:02) —
  431차가 **사이징 경로만** 중립화하고 차단 기준 `size_multiplier`는 **무변경**으로 둔
  의도된 설계. 오늘 MetaGate 61회 중 `reduce size_mult=0.50` **31회(51%)**.
- `[CB] 연속 손절 1회/2회`(11:12:08·11:21:33) — **한 포지션이 2 카운트**. 360차가
  *"포지션 하나가 손실 이벤트를 최대 2회(1차+최종) 만들 수 있음 — CB② 복원 시 감안"*
  으로 이미 기록·등록. `9999` 유지라 정지 없음(정상).
- `min_conf 0.65→0.62` 11:50:05부터 46분 연속 — **점심구간 zone_mc 상한**
  (`config/settings.py:505 MC_ZONE_MAX = 0.65`). 08-14·08-18 모두 **11:50~12:59:59**
  정확히 같은 창에서 70회씩. **정상 동작이며 래치가 아니다.**
- 불변식 `미발견` 5행 / 미커밋 461건(CRLF) — 478차 장전에 이미 등록(F-2 / 실질 4건).

### 08-29 CB② 복원 상정에 함께 올릴 것

CLAUDE.md 절대원칙 §2는 CB②를 *"5분 내 손절 3연속"*이라 쓰지만
`safety/circuit_breaker.py:206-213`에는 **시간창이 없다** — `_consec_stops`는 승리
레그(`record_win()`)로만 리셋된다. 게다가 `record_stop_loss()` 호출부가 **청산 레그
단위 4곳**(`main.py:10072 _post_partial_exit` / `10153 _post_loss_tier1_exit` /
`10482 _post_exit` / `14115 _ts_record_nonfinal_exit`)이라 **한 포지션이 2 카운트**를
만든다(오늘 11:11 SHORT 3계약이 실례). 한도를 2~3으로 되돌리면 **단일 포지션의 계단식
손절만으로 당일 정지**가 성립한다. 계측 4원칙 ①(단위 명시)의 CB② 판이다.
※ 참고 실측(일자별 카운터 최고치): 07-23 6회 / 08-03 3회 / 08-05 3회 / 08-11 3회.

### 검증

- 코드 변경 0건 · 커밋 0건 · 라이브 DB 접근 0건(로그·설정·소스·git 메타만, `sqlite3` 0회).
- 재인용 금지 수치 미사용: 2026-06-25 SHAP=0 / 0801 §9-3 이벤트 단위 사이징 4종 /
  CB③ "35%" / 417차 "379건 중 86건" / 476차 §3 "133건·29.6%".
- conf 절대값을 구 판단기준표에 대보지 않음 — DynMC `base=0.401` 및 점심 zone 0.65
  대비 상대 위치로만 서술. 붕괴행 45/207 = 21.7%(문서 기재 21~22% 일치) 집계 제외.
- 표본 부족 확정 결론 없음(313차): 1-1 원인(n=1) · 1-2 원인 후보 · IntradayRegime 실해.

```

</details>

### dev_memory/NEXT_TODO.md — 980.6KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 477차 — post 확인필요 3건 딥다이브 후속 (MW0601, 2026-08-18 분석만·코드 0건)
### 477차 후속2 — 476차 Fix 계획 검토 결과 (MW0601, 2026-08-18 · 검토만, 코드 0건)
### 477차 후속1~3 — 476차 Fix 구현 완료 (MW0601, 2026-08-18 · 커밋 3건)
### 477차 후속5 — 476차 §3 고도화 방안 조사 결과 (MW0601, 2026-08-18 · 조사만)
### 477차 후속6 — GR-1 구현 완료 (MW0601, 2026-08-18)
### 477차 후속7 — GR-3 구현 완료 (MW0601, 2026-08-18)
### 478차 — 장전 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 478차 후속 — 장중 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
```

미완료 체크박스 **1457건** (끝에서 30건)
```
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
- [ ] **F-5① 진입 레이스 폴백 가시화 (P1, 장후 즉시)** — `main.py:16361-16365` ERROR
- [ ] **F-5② `apply_entry_fill()` 파라미터 확장 (P1, 다음 세션)** —
- [ ] **F-5③ 콜백 큐잉으로 레이스 제거 — 보류** ⚠ **절대원칙 ④에 인접.**
- [ ] **F-6 1단계 `scripts/step1_scoring_coverage.py` 신설 (P1, 장후)** — 읽기 전용,
- [ ] **F-6 2단계 `[HorizonEmit] hz={sorted(horizon_proba)}` 매분 1줄 (P1, 장후)** —
- [ ] **F-7 `references/phases.md` B-1 T-30 문구 정정 (P2, 장후)** — *"퇴역 대상"* →
- [ ] **G-5 `tests/test_478_entry_param_completeness.py` 신설 (이번 주)** — 포지션을 여는
- [ ] **G-6 수집기 §5에 "STEP 1 채점 커버리지" 표 상설 편입 (이번 주)** —
- [ ] **G-7 `scripts/intraday_regime_flap_watch.py` 신설 (이번 주, 계측만)** —
- [ ] **[로드맵] 26주 WFA 재검증 항목에 "STEP 1 채점 커버리지" 편입 제안** —
- [ ] **O-1** — 09:49 포지션의 `trades.entry_horizon` · `ensemble_decisions` 09:49 행.
- [ ] **O-2** — 오늘 종일 `[FixB] open_position 실패` 추가 발생. 2건 이상이면 F-5 우선순위 상향
- [ ] **O-3** — `ofi_norm` identity 강제 **종일** 비율(3거래일째). 08-18의 94%를 넘는가
- [ ] **O-4** — IntradayRegime 종일 전이 횟수. 08-18의 22회 대비 2배 이상이면 G-7 착수
- [ ] **O-5** — 15:10 경로 `[ForceExitPass]`→`[TimeExit]`→`[ExitAttempt]`.
- [ ] **O-8** — F-6 1단계 스크립트가 §1-2 표를 재현하는가 (08-20)
- [ ] **[08-29 상정 보강] CB② 복원 안건에 "시간창 없음 + 레그 단위 카운트" 함께 올릴 것** —
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
.py` 신설 (P1, 장후)** — 읽기 전용,
      `logs/*_LEARNING.log`의 `✓|✗ {h} 예측`을 호라이즌별·분 mod h 별로 집계.
      검증: 08-12/14/18/19 표(1m 369/366/368 · 10m 72/70/72 · 15m 47/46/47) 재현
- [ ] **F-6 2단계 `[HorizonEmit] hz={sorted(horizon_proba)}` 매분 1줄 (P1, 장후)** —
      **사전등록 판정문**: *"10m·15m를 매분 싣는데도 채점이 2/h면 원인은 채점기(후보②),
      발행이 2/h면 STEP 5(후보①). 5거래일 관측으로 확정하며 그 전에는 발행 주기를 바꾸지
      않는다."* ⚠ 임계는 지금 등록하고 이후 움직이지 않는다(313차 ④, 458차 D6).
      ⚠ **30m은 건드리지 않는다 — CB③의 유일한 입력원**(CLAUDE.md §3 474차)
- [ ] **F-7 `references/phases.md` B-1 T-30 문구 정정 (P2, 장후)** — *"퇴역 대상"* →
      *"채점 유지가 정상, 끊기면 그것이 이상점"*. **F-2·F-4와 같은 커밋**(스킬 참조문서 묶음)
- [ ] **G-5 `tests/test_478_entry_param_completeness.py` 신설 (이번 주)** — 포지션을 여는
      3경로(`open_position()` / `apply_entry_fill()` FLAT / `_ts_manual_position_restore()`)를
      AST로 열거해 `entry_horizon`·`entry_hurst_bucket` 설정 수단 보유를 정적 검사.
      474차 `test_473_core_group_reachability.py`와 같은 방식. 선행: F-5①
- [ ] **G-6 수집기 §5에 "STEP 1 채점 커버리지" 표 상설 편입 (이번 주)** —
      `collect_evidence.py`. 호라이즌별 채점 건수 / 경과분 대비 비율 / 전일 델타.
      DB 접근 없음(장중 안전). ⚠ **임계는 걸지 않는다** — 섀도 관찰
- [ ] **G-7 `scripts/intraday_regime_flap_watch.py` 신설 (이번 주, 계측만)** —
      전이 횟수 · 체류시간 중앙값 · 전이 시점 `day`의 임계 대비 거리 분포.
      **사전등록 판정문**: *"전이 시점 |거리| 중앙값 < 0.10%p 가 5거래일 연속이면
      히스테리시스/최소체류시간 도입을 주간회의 안건으로. 아니면 현행 유지."*
      ⚠ **집행(차단·등급·배수)에 연결 금지** — 섀도 관찰 후 승격
- [ ] **[로드맵] 26주 WFA 재검증 항목에 "STEP 1 채점 커버리지" 편입 제안** —
      455차 "호라이즌 방향예측 피처셋 재검증"과 같은 절. 가중 57%를 지는 축이 5~8배
      희소하게 배우는 상태는 피처셋 재검증의 전제를 흔든다

#### 오늘(08-19) 장후 확인 예정 — 장중 점검에서 추가

- [ ] **O-1** — 09:49 포지션의 `trades.entry_horizon` · `ensemble_decisions` 09:49 행.
      NULL/미기록이면 F-5 영향 ③ 확정. ⚠ `guard_intraday()` 해제 후
- [ ] **O-2** — 오늘 종일 `[FixB] open_position 실패` 추가 발생. 2건 이상이면 F-5 우선순위 상향
- [ ] **O-3** — `ofi_norm` identity 강제 **종일** 비율(3거래일째). 08-18의 94%를 넘는가
- [ ] **O-4** — IntradayRegime 종일 전이 횟수. 08-18의 22회 대비 2배 이상이면 G-7 착수
- [ ] **O-5** — 15:10 경로 `[ForceExitPass]`→`[TimeExit]`→`[ExitAttempt]`.
      `[SchedForceExit] 안전망 발동`(ERROR) 출현 시 **P0**
- [ ] **O-8** — F-6 1단계 스크립트가 §1-2 표를 재현하는가 (08-20)
- [ ] **[08-29 상정 보강] CB② 복원 안건에 "시간창 없음 + 레그 단위 카운트" 함께 올릴 것** —
      CLAUDE.md §2는 *"5분 내 손절 3연속"*이라 쓰지만 `safety/circuit_breaker.py:206-213`에
      **시간창이 없고**(승리 레그로만 리셋), `record_stop_loss()` 호출부가 청산 레그 단위
      4곳(`main.py:10072`/`10153`/`10482`/`14115`)이라 **한 포지션이 2 카운트**를 만든다
      (08-19 11:11 SHORT 3계약이 실례). 한도 2~3 복원 시 **단일 포지션의 계단식 손절만으로
      당일 정지**가 성립한다. 계측 4원칙 ①의 CB② 판. 기한 **10일**(영업일 8일)

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

### `docs/정기점검/매일점검` — 48개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-intra.md` | 33.7KB | 08-19 12:42 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_intra.md` | 59.8KB | 08-19 12:26 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-pre.md` | 33.8KB | 08-19 09:11 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_pre.md` | 46.2KB | 08-19 09:00 |
| `docs/정기점검/매일점검/MW0601-20260818-고도화방안검토.md` | 16.3KB | 08-18 23:04 |
| `docs/정기점검/매일점검/MW0601-20260818-Fix계획검토.md` | 13.8KB | 08-18 19:28 |
| `docs/정기점검/매일점검/MW0601-20260818-확인필요3건-딥다이브.md` | 15.5KB | 08-18 18:33 |
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-post.md` | 45.0KB | 08-18 16:35 |

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
7. `logs/20260819_SYSTEM.log`: 매분 루프 커버리지 283/371분 (76.3%) — 루프가 빠진 구간이 있다
8. `logs/20260819_SYSTEM.log`: 13:42~13:50 **연속 9분 매분 루프 기록 없음**
9. `logs/20260819_SYSTEM.log`: 13:52~15:10 **연속 79분 매분 루프 기록 없음**
10. 장후인데 **15:10 청산 경로가 아무 흔적도 남기지 않았다** — 실집행(`강제청산`)도 하트비트(`[SchedForceExit]`)도 없다. 절대원칙 1 확인 필요 (471차 F-2 배포 이후라면 하트비트 부재 자체가 이상)
11. 완료 마커 **`daily_close_done`** 없음 — 15:40 일일 마감 완료 마커
12. 완료 마커 **`strategy_report`** 없음 — 일일 전략 리포트
13. 청산 4건 중 하드스톱·손절 계열 **3건(75%)** — 손절 준수율 확인 필요
14. 메인 스레드 블로킹 5초 초과 **4건** (최대 6766ms) — `CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인
15. `logs/20260819_WARN.log`: **ConstOut** 6건(표본)
16. `logs/20260819_SYSTEM.log`: **ConstOut** 8건(표본)
17. `logs/20260819_SIGNAL.log`: **WeightCollapse** 8건(표본)
18. `logs/20260819_SIGNAL.log`: **ConstOut** 8건(표본)
19. `logs/20260819_LEARNING.log`: **축퇴** 8건(표본)
20. 미커밋 변경 463건
21. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260819*.log` (Windows) / `grep 강제청산 logs/*20260819*.log`*