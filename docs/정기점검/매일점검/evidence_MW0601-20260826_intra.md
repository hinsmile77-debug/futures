# 미륵이 증거 다이제스트 — 2026-08-26 / INTRA

- 생성 2026-08-26 12:26:33 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/kind-zealous-pasteur/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260826` · `2026-08-26` · `260826` · `0826`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **21개** 파일 · 21개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260826.log` | 124B | 08-26 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260826.log` | 140B | 08-26 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260826.json` | 243B | 08-26 12:26 |
| `launcher_{DATE}_084001_31359.log` | 1 | `logs/Mireuk_batch/launcher_20260826_084001_31359.log` | 970.0KB | 08-26 12:26 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260826.log` | 26.2KB | 08-26 12:17 |
| `retrain_intraday_{DATE}_093600.log` | 1 | `logs/retrain_intraday_20260826_093600.log` | 2.4KB | 08-26 09:36 |
| `retrain_intraday_{DATE}_103001.log` | 1 | `logs/retrain_intraday_20260826_103001.log` | 2.4KB | 08-26 10:30 |
| `retrain_intraday_{DATE}_111200.log` | 1 | `logs/retrain_intraday_20260826_111200.log` | 2.4KB | 08-26 11:12 |
| `retrain_intraday_{DATE}_120501.log` | 1 | `logs/retrain_intraday_20260826_120501.log` | 2.4KB | 08-26 12:05 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260826_BACKFILL.log` | 0B | 08-26 07:18 |
| `{DATE}_DATA.log` | 1 | `logs/20260826_DATA.log` | 182.4KB | 08-26 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260826_DEBUG.log` | 133.3KB | 08-26 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260826_HEALTH.log` | 2.4KB | 08-26 12:07 |
| `{DATE}_HOGA.log` | 1 | `logs/20260826_HOGA.log` | 28.7MB | 08-26 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260826_LEARNING.log` | 183.7KB | 08-26 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260826_MICRO.log` | 577.4KB | 08-26 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260826_PROBE.log` | 57.5KB | 08-26 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260826_SIGNAL.log` | 378.9KB | 08-26 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260826_SYSTEM.log` | 463.6KB | 08-26 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260826_TRADE.log` | 7.3KB | 08-26 12:19 |
| `{DATE}_WARN.log` | 1 | `logs/20260826_WARN.log` | 42.5KB | 08-26 12:26 |

## 2. 코드·커밋 상태

- HEAD `5c54496` · 브랜치 `v9-dev` · 미커밋 517건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 509건 (추적변경 511 · 미추적 6 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 0.0시간 · git 프로세스 0개 (판정 보류 — 3중 조건 미충족)
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
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
… 외 477건
```

**당일(2026-08-26) 커밋**
```
5c54496 [MW0601] 495차 후속 체리픽: 수수료율을 로그인 채널 감지로 파생 — v9-dev는 CYBOS
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
```

**최근 커밋 12건**
```
5c54496 [MW0601] 495차 후속 체리픽: 수수료율을 로그인 채널 감지로 파생 — v9-dev는 CYBOS
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
a0fcee2 [MW0601] 493차 후속6: 사용자 조치 구현 8건 — F-Y·F-X·F-V·F-Z·F-AA·F-AB·F-P·F-Q
a7120ad [MW0601] 493차 후속5: 수수료율 6.54배 오차 fix — F-1~F-5 (F-AD ①~⑥ 구현)
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
91c6120 [MW0601] 491차: 0824 장후 fix 9건 구현 — F-L·F-M·F-N·F-G·F-K·F-I·F-B·F-F·F-D (+ lock_guard 콘솔)
d66ec0d [MW0601] 점검 산출물 적재: 0812~0824 일일점검 증거 27건 · 리포트 2건 · 0821 주간 3종 · 26주 WFA 피처셋 재검증
4dbdf80 [MW0601] 489차: 주간회의 승인 6건 — ⑨ WFA 이관 · [46]③ 재등록+배선 · 좀비결정 7건 분류 · [8]② 계측 이식
10178cb [MW0601] 489차 A-1: CB② 카운트를 절대원칙 문구에 맞춘다 — 시간창 + 포지션 단위 (한도 무변경)
9acc983 [MW0601] 488차 후속: 라이브 데이터에 고정된 캠페인 테스트 4개 재설계 — FAIL 12건 해소
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
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

_이 브랜치(`v9-dev`) 범위 밖 **5건** — 표에서 제외했다(계측 4원칙 ③): `MODEL_LABEL_STATE_UNLOCK_ENABLED`(→dev), `PRE_RETRAIN_DONE_BY_EOD_ENABLED`(→dev), `ZONE_ENTRY_BAN_ENFORCE`(→dev), `ZONE_ENTRY_BAN_SHADOW_ENABLED`(→dev), `PIPE_LATENCY_EXCLUDE_MODEL_SWAP`(→dev)._
> 제외는 "없어도 된다"가 아니라 "이 브랜치에는 기능 자체가 없다"는 뜻이다. 이식 여부는 별개 안건이며 주간회의에서 정한다.

### 차단 게이트 전수 인벤토리 — 33개 중 **9개 꺼짐**

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

_본문 미열람(설정): `20260826_HOGA.log` 28.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/18개 (중요도순). 제외: `retrain_intraday_20260826_103001.log`, `retrain_intraday_20260826_120501.log`, `20260826_MICRO.log`, `20260826_DATA.log`, `20260826_PROBE.log`, `launcher_20260826_084001_31359.log`, `20260826_DEBUG.log`, `mainstall_traceback_20260826.log`_

### `logs/20260826_TRADE.log` — 7.3KB · 57행 · 최종 12:19:01

- 형식 평문 · 시각 인식 57행 · INFO=57

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-26 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-26 09:39:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,349,062) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-26 09:39:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev❌ time✅ risk✅ chas✅ coun✅ | conf=45.0%
2026-08-26 09:39:01 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 1062.82 | 손절=1066.36 1차=1061.64(×0.42) 2차=1059.28 horizon=3m hurst=mean-revert
  …
2026-08-26 12:19:01 [INFO] TRADE: [주문요청] TP2 청산 LONG 1계약 @ 1085.24 체결대기
2026-08-26 12:19:01 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2579 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-26 12:19:01 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2579 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-26 12:19:01 [INFO] TRADE: [Position] 체결청산 LONG @ 1085.52 | PnL=+2.85pt (+131,879원) | TP2(전량)
2026-08-26 12:19:01 [INFO] TRADE: [청산 완료] PnL=+2.85pt (+131,879원)
```

</details>

**채널** — `TRADE`×57

**컴포넌트 상위 15** — `Chejan`×14, `Position`×9, `Sizer`×8, `주문요청`×6, `JointGateBlock 차단`×6, `진입체크`×2, `체결진입`×2, `체결진입보정`×2, `TickTP1`×2, `TP1 부분청산`×2, `청산 완료`×2, `ProfitGuard`×1, `TickStop-S0C`×1

### `logs/20260826_WARN.log` — 42.5KB · 208행 · 최종 12:26:00

- 형식 평문 · 시각 인식 208행 · WARNING=208

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-08-26 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3328 band=INFO since_pipe_s=NA
2026-08-26 08:41:28 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3750ms — live 중단 원인 분석용
  …
2026-08-26 12:25:00 [WARNING] SYSTEM: [HealthPolicy] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\PycharmProjects\futures\config\constants.py)
2026-08-26 12:26:00 [WARNING] SYSTEM: [HealthPolicy] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\PycharmProjects\futures\config\constants.py)
2026-08-26 12:27:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.286% (임계 ±0.177%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-26 12:27:00 [WARNING] SYSTEM: [HealthPolicy] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\PycharmProjects\futures\config\constants.py)
2026-08-26 12:27:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1180ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
```

</details>

**WARNING — 태그 29종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 54 | 08:41:21 | 12:19:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `HealthPolicy` | 18 | 09:01:00 | 12:27:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1904ms quality=0.86 cache=0s exc10m=0) | cause=S5(1481ms) |
| `ChejanFlow` | 14 | 09:39:01 | 12:19:01 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='793' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:39:00.987' | positio… |
| `ChejanMatch` | 14 | 09:39:01 | 12:19:01 | order_no='793' | pending='ENTRY:SHORT qty=2 filled=0 order_no=793 reason=진입 req_at=09:39:00.987' | pending_matched=True |
| `PendingOrder` | 12 | 09:39:00 | 12:19:01 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1062.82, 'reason': '진입', 'hint_source': '', 'atr': 2.7786, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `PipePerf` | 10 | 09:00:02 | 12:06:02 | total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| `CB⑤` | 10 | 09:00:02 | 12:06:02 | 파이프라인 1904ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `Health` | 9 | 09:00:02 | 12:06:02 | level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0 |
| `ScalerRefresh` | 9 | 09:19:00 | 12:27:00 | 5분 누적 수익률 +0.739% (임계 ±0.529%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `MainStallTrace` | 8 | 09:00:08 | 12:17:05 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260826.log |
| `CB③-P4` | 8 | 10:24:00 | 11:46:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `ConstOut` | 4 | 09:35:00 | 12:04:00 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

**채널** — `SYSTEM`×199, `HEALTH`×9

**컴포넌트 상위 15** — `LiveDBG`×54, `HealthPolicy`×18, `ChejanFlow`×14, `ChejanMatch`×14, `PendingOrder`×12, `PipePerf`×10, `CB⑤`×10, `Health`×9, `ScalerRefresh`×9, `MainStallTrace`×8, `CB③-P4`×8, `ConstOut`×4, `EntryFillFlow`×4, `ExitCooldown`×4, `PartialExitAttempt`×3

### `logs/20260826_SYSTEM.log` — 463.6KB · 3359행 · 최종 12:26:21

- 형식 평문 · 시각 인식 3352행 · INFO=3352, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18960 | 행감지=30s all_threads=True
2026-08-26 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-26 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-26 08:41:00 [INFO] SYSTEM: 미륵이 초기화
2026-08-26 08:41:00 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-25) 종가 버퍼 로드: 384봉
  …
2026-08-26 12:27:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=12:26 O=1082.50 H=1082.54 L=1081.16 C=1081.96 V=286
2026-08-26 12:27:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=12:26 vol=286 | live_buy=172 shadow_buy=119 anchor_buy=119 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-08-26 12:27:00 [INFO] SYSTEM: [S6Detail] ensemble=3ms checklist_pre=3ms meta_gate=9ms gates=0ms imp=0ms shap=3ms corr=10ms dash_ui=0ms tail=89ms
2026-08-26 12:27:00 [INFO] SYSTEM: [PipePerf][DBG] total=452ms | S0=22ms S1=22ms S2=6ms S3=0ms S4=60ms S5=198ms S6=120ms S7=11ms S8=12ms
2026-08-26 12:27:01 [INFO] SYSTEM: [CybosRT-TICK] #75900 code=A0569 raw_time=122700 parsed=12:27:00 price=1081.84 vol=1 bid1=1081.82 ask1=1081.94 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3352

**컴포넌트 상위 15** — `CybosInvestorRaw`×822, `CybosRT-TICK`×764, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×220, `S6Detail`×208, `PipePerf`×208, `System`×59, `MicroRegime`×59, `RegimeFingerprint`×38, `CybosEvent`×28, `BalanceUI`×26, `IntradayRegime`×24, `OptionChain`×23

### `logs/20260826_SIGNAL.log` — 378.9KB · 3331행 · 최종 12:26:00

- 형식 평문 · 시각 인식 3331행 · WARNING=1460, INFO=1871

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.455
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.442
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.433
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.429
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.438
  …
2026-08-26 12:27:00 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.0903 → floor=0.25 적용 (z-score 폭발 방지)
2026-08-26 12:27:00 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4929 → floor=0.50 적용 (z-score 폭발 방지)
2026-08-26 12:27:00 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0514 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-26 12:27:00 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1118 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-26 12:27:00 [INFO] SIGNAL: [ScalerRefresh] ts=12:26 trigger=D_FORCE price_momentum_5m=-0.286% n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.08s
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1044 | 09:00:02 | 12:27:00 | 1m 'macro_vix' scale=0.0139 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 120 | 09:00:00 | 12:17:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 108 | 09:00:00 | 12:21:00 | ts=08:59 horizon=1m age=1m max_z=-4.33(mlofi_norm) extreme=2 |
| `Checklist` | 90 | 09:06:01 | 12:25:00 | 신뢰도 미달 34.4% < 41.2% → 강제 X등급 |
| `ScalerRefresh` | 48 | 08:45:21 | 08:59:01 | 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 45 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 4 | 09:35:00 | 12:04:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4550 (conf_floor=0.330, min_conf=0.455, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3331

**컴포넌트 상위 15** — `ScalerFloor`×1068, `SIGNAL`×416, `MetaGate`×216, `Ensemble`×210, `FQAdj`×205, `ZeroDiag`×186, `Model`×150, `ScalerMonitor`×108, `Checklist`×105, `ATR-Horizon`×93, `ScalerRefresh`×80, `InstabilityGate`×68, `ConfStuckBoost`×61, `MicroRegime`×59, `ToxicityGate`×59

### `logs/20260826_LEARNING.log` — 183.7KB · 1718행 · 최종 12:26:00

- 형식 평문 · 시각 인식 1718행 · WARNING=141, INFO=1577

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00082 auc=0.530 out_max=0.4460 (기준 auc<0.53 and span<0.020, 기저율=0.4455 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00036 auc=0.509 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-08-26 08:41:04 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00084 auc=0.533 out_max=0.4505 (n=120) → 보정 재적용
  …
2026-08-26 12:27:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=48.1% 예측=DN 실제=FL)
2026-08-26 12:27:00 [INFO] LEARNING: [Bias⚠] 1m 적중=36%(8/22) UP=0 DN=4 FL=18 [FL편향⚠ 82%]
2026-08-26 12:27:00 [INFO] LEARNING: [CONF⚠] 5m conf=0.4237 3분 고착 | gbm_raw=0.4237 sgd=None bar_age=3
2026-08-26 12:27:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
2026-08-26 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=10.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 141 | 08:41:04 | 11:45:00 | 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×1718

**컴포넌트 상위 15** — `LEARNING`×661, `Calibration`×275, `SGD`×208, `sigma`×195, `Bias⚠`×105, `CONF⚠`×63, `Bias`×59, `MetaConf`×39, `OnlineLearner`×36, `ScalerWarmup`×32, `BiasReset`×10, `GBM-64`×8, `GBM`×8, `SHAP`×7, `RF`×5

### `logs/20260826_HEALTH.log` — 2.4KB · 18행 · 최종 12:07:00

- 형식 평문 · 시각 인식 18행 · WARNING=9, INFO=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0
2026-08-26 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=519ms | quality=0.86 | cache_age=96s | exceptions_10m=0
2026-08-26 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 276ms (표본 20분)
2026-08-26 09:33:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=264ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-26 09:34:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=242ms | quality=1.00 | cache_age=58s | exceptions_10m=0
  …
2026-08-26 11:15:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=333ms | quality=1.00 | cache_age=57s | exceptions_10m=0
2026-08-26 12:03:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=306ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-26 12:04:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=298ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-26 12:06:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2448ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-08-26 12:07:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=345ms | quality=1.00 | cache_age=54s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:02 | 12:06:02 | level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0 |

**채널** — `HEALTH`×18

**컴포넌트 상위 15** — `Health`×17, `HealthTrend`×1

### `logs/retrain_intraday_20260826_093600.log` — 2.4KB · 20행 · 최종 09:36:22

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 09:36:00,666 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-26 09:36:00,666 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-26 09:36:00,666 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-26 09:36:00,666 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_8fa36c18.json
2026-08-26 09:36:03,608 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-26 09:36:22,099 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.90s | old_acc=0.4144)
2026-08-26 09:36:22,210 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-26 09:36:22,210 [INFO] LEARNING: [Retrain] 완료 | 18.6초 | 성공=1/1 호라이즌
2026-08-26 09:36:22,210 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.5s 데이터=4800행
2026-08-26 09:36:22,211 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_8fa36c18.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260826_111200.log` — 2.4KB · 20행 · 최종 11:12:22

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 11:12:00,825 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-26 11:12:00,825 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-26 11:12:00,825 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-26 11:12:00,825 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_8eb53d14.json
2026-08-26 11:12:03,715 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-26 11:12:22,401 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.98s | old_acc=0.4144)
2026-08-26 11:12:22,488 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-26 11:12:22,488 [INFO] LEARNING: [Retrain] 완료 | 18.8초 | 성공=1/1 호라이즌
2026-08-26 11:12:22,489 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.7s 데이터=4800행
2026-08-26 11:12:22,491 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_8eb53d14.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) | 2 |
| 체결(`[체결진입]`) | 2 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 57 |
| 사이저 호출(`[Sizer]`) | 8 |

### 포지션 2건 · 승 2 (100%) · 합계 +4.64pt (+189,902원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:39:01 | SHORT | 2 | 3m | 2 | +0.84 | +21,144 | 하드스톱(틱) |
| 12:17:00 | LONG | 2 | 3m | 2 | +3.80 | +168,758 | TP2(전량) |

**청산 레그 4행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:39:44 | 부분 | 1 | +0.87 | +33,072 | TP1 부분청산 33% |
| 09:41:09 | 전량 | 1 | -0.03 | -11,928 | 하드스톱(틱) |
| 12:18:14 | 부분 | 1 | +0.95 | +36,879 | TP1 부분청산 33% |
| 12:19:01 | 전량 | 1 | +2.85 | +131,879 | TP2(전량) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱(틱)`×1, `TP2(전량)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +189,902 = 포지션합 +189,902 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:39:01 | SHORT | 2 | 1062.82 | 3m | mean-revert |
| 12:17:00 | LONG | 2 | 1082.66 | 3m | trend |

계약수 분포 — 2계약×2

등급 분포 — `A급(원시C)`×1, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×1, `prev`×1, `time`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×8

실제 진입 계약수 — **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×8

### 차단 사유 57건 · 17종

| 건수 | 사유 |
|---|---|
| 33 | 등급X — 미통과 항목: 2_confidence |
| 4 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 1 | 청산 후 쿨다운 — 128초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar |
| 1 | JointGateBlock — meta=0.63 tox=0.70 joint=0.439 < 0.50 |
| 1 | JointGateBlock — meta=0.61 tox=0.70 joint=0.426 < 0.50 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 10_chase |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 11_countertrend |
| 1 | 청산 후 쿨다운 — 60초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 0초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×33, `3_vwap`×14, `6_foreign`×14, `5_ofi`×8, `7_prev_bar`×7, `4_cvd`×7, `11_countertrend`×2, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 18건 · 최대 8141ms · 5초 초과 8건

상위 — 8141ms, 7718ms, 7297ms, 5765ms, 5343ms, 5312ms, 5218ms, 5016ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8141ms | 1904ms | **6237ms (77%)** |
| 11:39:04 | 5312ms | 463ms | **4849ms (91%)** |
| 11:44:04 | 5218ms | 352ms | **4866ms (93%)** |
| 11:49:04 | 5343ms | 337ms | **5006ms (94%)** |
| 11:54:07 | 7718ms | 469ms | **7249ms (94%)** |
| 12:07:05 | 5765ms | 2448ms | **3317ms (58%)** |
| 12:12:06 | 7297ms | 434ms | **6863ms (94%)** |
| 12:17:05 | 5016ms | 548ms | **4468ms (89%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260826_WARN.log`
```
--- ConstOut ×4(표본)
09:35:00 2026-08-26 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:29:00 2026-08-26 10:29:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:11:00 2026-08-26 11:11:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:04:00 2026-08-26 12:04:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×8(표본)
09:00:08 2026-08-26 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260826.log
11:39:04 2026-08-26 11:39:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260826.log
11:44:04 2026-08-26 11:44:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260826.log
11:49:04 2026-08-26 11:49:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260826.log
--- [Brier] 과신 ×1(표본)
11:47:00 2026-08-26 11:47:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.354 > 0.35
--- [CB] ×1(표본)
09:41:09 2026-08-26 09:41:09 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×4(표본)
09:41:09 2026-08-26 09:41:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:44:09)
09:41:09 2026-08-26 09:41:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:44:09)
12:19:01 2026-08-26 12:19:01 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 12:21:01)
12:19:01 2026-08-26 12:19:01 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 12:21:01)
--- [SHAP] 슬로우 ×3(표본)
11:40:01 2026-08-26 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 937ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:10:02 2026-08-26 12:10:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1262ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:27:01 2026-08-26 12:27:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1180ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:24 2026-08-26 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3328 band=INFO since_pipe_s=NA
09:00:08 2026-08-26 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8141 band=WARN since_pipe_s=0.2
09:05:04 2026-08-26 09:05:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4563ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4563 band=INFO since_pipe_s=0.1
09:37:02 2026-08-26 09:37:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2797 band=INFO since_pipe_s=0.0
```

### `logs/20260826_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-08-26 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-08-26 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-08-26 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=90ms fit=58ms total=150ms
09:36:00 2026-08-26 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-08-26 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.058 level=0 (heartbeat)
09:05:00 2026-08-26 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.057 level=0 (heartbeat)
09:10:00 2026-08-26 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.056 level=0 (heartbeat)
09:15:00 2026-08-26 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.056 level=0 (heartbeat)
```

### `logs/20260826_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-08-26 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4550 (conf_floor=0.330, min_conf=0.455, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-08-26 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:36:00 2026-08-26 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:02 2026-08-26 09:37:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:29:00 2026-08-26 10:29:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:00 2026-08-26 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-08-26 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-08-26 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-08-26 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.455
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.442
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.433
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.429
--- 안전망 ×8(표본)
09:07:00 2026-08-26 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-26 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-08-26 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-08-26 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260826_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00082 auc=0.530 out_max=0.4460 (기준 auc<0.53 and span<0.020, 기저율=0.4455 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00036 auc=0.509 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:41:04 2026-08-26 08:41:04 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00084 auc=0.533 out_max=0.4505 (n=120) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260826_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:13 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 4 | 09:54:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=49,370,212) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |

- 이 로그 생존구간: 08:41 ~ 12:19

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260826_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 09:00:02 [WARNING] total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 09:00:02 [WARNING] total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| 10:00 | 장중 초반 | 2 | 09:59:00 [WARNING] 5분 누적 수익률 +0.280% (임계 ±0.262%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 15 | 11:54:07 [WARNING] _tick_header 간격 7718ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7718 band=… |

- 이 로그 생존구간: 08:41 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260826_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=18960 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 137 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 205 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 202 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 186 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260826_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:21 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 88 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0250) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 158 | 08:55:03 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0251) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 175 | 09:56:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=-1.986 need >0 (LONG) bear_exh=0.00 |
| 12:00 | 장중 중간점 | 168 | 11:54:00 [WARNING] 신뢰도 미달 34.3% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260825 | 15:40 | 로그 본문 |
| 20260824 | 15:40 | 로그 본문 |
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260826** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [C-1] (확인 필요 · 확정 결론 금지) 개장 첫 분 `min_conf` 괴리가 11거래일 최대
### [C-2] (확인 필요) 개장 직후 `IntradayRegime NORMAL → CRASH` · `DayRegimeShadow RANGE → CHAOS(90%)`
### 이미 반영된 사안 (신규 아님 — 함정 ① 차단)
### 고도화 (당일 관측 근거)
### 기한 도래
### 관측 항목 (장중·장후·내일이 닫는다)
### 점검 규약 메모
### 커밋 대기 (오늘 커밋하지 않았다 — 예약 실행은 커밋하지 않는다)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
**G-2 — 개장 첫 분 괴리 시계열 적재.** C-1을 재려고 로그 11개를 grep했고, 08-17은 **결측인지
정상인지 구분 불가**였다(4원칙 ②). 매 거래일 09:00 첫 파이프라인에서 `cal_out_max` ·
`min_conf_raw` · `min_conf_effective`(FQAdj 후) · `gap` · `guard_fired`(0/1)를
**경보 유무와 무관하게** 1행 적재. 적재처 `model/scaler_monitor_db.py` 계열(493차 F-AB와 같은 축).
⚠ **판정 무관 — 사전등록 합격선 무변경**(458차 D6).

**로드맵 반영 제안** — ① 실전 전환 기준 ②ⓑ(동결→하드종료→런처 재기동→세션 복원 왕복)의
**마지막 단계가 이중 기동을 만들 수 있다.** 가드가 가짜인 상태로 ②ⓑ를 통과시키면 왕복 시험
자체가 위험하므로 F-2를 ②ⓑ 하위 확인사항으로 편입 검토. ② 26주 WFA 「선물 수수료율」에
F-3의 불변식 3행을 **일일 점검 축**으로 명시 — 상시 감시(F-2 net 대사)는 **상수가 조용히
바뀌는 것**을 못 잡는다.

---

### 기한 도래

🔴 **CB② 복원 재검토 기한 2026-08-29** — `CB_CONSEC_STOP_LIMIT = 9999`(수집기 §3 `일치`).
2026-08-29는 **토요일**이므로 마지막 거래일은 **2026-08-28(금)**. 오늘 포함 **거래일 3일**
(08-26·27·28). **이번 주 금요일 주간점검에서 처리해야 기한을 지킨다.**
근거: CLAUDE.md 절대원칙 §2 CB② — *"무기한 유예가 아니다 — Phase 5 조건 ②·⑤가 여기 걸려
있고 … 2026-08-29에 반드시 재론할 것"*.
⚠ **이 세션은 결정하지 않는다**(함정 ① 판정 ≠ 결정). 기한 도래 사실만 올린다.

---

### 관측 항목 (장중·장후·내일이 닫는다)

- **O-1** C-1 괴리 0.1071 — 장중: ConfFloorGuard 재발 / FQAdj 후 실효 min_conf / 자동진입 발생
- **O-2** C-2 CRASH·CHAOS — 장중: 복귀 시각 / ZeroDiag 사유 분포 / AutoMasked 3피처 격리 해제
- **O-3** 1-2 — (F-2 적용 후) **내일 08:40** 런처 로그 프로브 출력 줄 실재 여부
- **O-4** 1-3 — ProfitGuard 한도 도달 속도 / 장후 `[NetRecon]`·`[BrokerPnl]` **첫 라이브 대사** /
  `trades.commission_rate_used` 오늘 행 새 요율 기록
- **O-5** (0825 O-11 승계) `logs/retrain_intraday_20260826_15*.log` 존재 — 0825는 마지막이 14:10이라 이월
- **O-6** (0825 O-13 승계) F-Y 적용 후 첫 15:40 — `[CB③계측]` 1줄 + `daily_close_done_<date>.txt`
- **O-7** (0825 O-14 승계) F-Z 적용 후 15:45 — `freeze_sentinel_20260826.log` CRITICAL 0건 +
  「정상 종료」/「동결」 구분 기록

---

### 점검 규약 메모

`references/report_template.md`는 절 번호 접미사(`0i`/`0p`)를 말하고 SKILL.md 대원칙 B는
**파일** 접미사(`-pre`/`-intra`/`-post`)만 금지한다 — 충돌하지 않는다. 이 리포트는
**하루 한 파일 + 절 번호 `1p-*`** 로 절충했다(대원칙 B 우선 규정에 따름).
다음 세션이 같은 판단을 반복하지 않도록 명시해 둔다.

---

### 커밋 대기 (오늘 커밋하지 않았다 — 예약 실행은 커밋하지 않는다)

```
docs/정기점검/매일점검/MW0601-20260826-점검리포트.md      (신규)
docs/정기점검/매일점검/evidence_MW0601-20260826_pre.md    (신규 · 미추적)
docs/정기점검/매일점검/evidence_MW0601-20260825_pre.md    (어제분 · 미추적 잔존)
docs/정기점검/매일점검/evidence_MW0601-20260825_intra.md  (어제분 · 미추적 잔존)
docs/정기점검/매일점검/evidence_MW0601-20260825_post.md   (어제분 · 미추적 잔존)
dev_memory/DECISION_LOG.md                                (이 절)
dev_memory/NEXT_TODO.md                                   (494차 절)
```

🔴 **이상점 1-1의 `.git/index.lock`을 먼저 지워야 커밋이 된다** —
`del C:\Users\82108\PycharmProjects\futures\.git\index.lock`
⚠ **`git add .` 금지** — 나머지 509건은 EOL 착시다. 위 7개 경로만 명시 add 할 것.

```

</details>

### dev_memory/NEXT_TODO.md — 1.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## MW0601 494차 (2026-08-26 08:59 — 장전 점검)
### 🔴 최우선 — 기한 임박
### 장후 적용 (오늘, 사용자 지시 시) — 코드 변경은 15:10 이후
### 고도화 (당일 관측 근거)
### 로드맵·실전전환 기준 반영 제안 (주간회의)
### 494차 관측 항목
### 점검 규약 메모
### 커밋 대기 (오늘 커밋하지 않았다)
```

미완료 체크박스 **2007건** (끝에서 30건)
```
- [ ] **문서 정정** `dev_memory/NEXT_TODO.md:16752~16753`의 「**F-L 미적용**은 그대로 유효하다」
- [ ] **소급 통계 규약** `phantom_stop_shadow`로 과거 통계를 낼 때
- [ ] **F-V ④**(`phantom_stop_shadow`에 `entry_after_bar`·`stop_updated_at_null` 컬럼 추가)를
- [ ] **O-10** SHAP 주간 심사 `CORE안전=⚠️` 상시 표기 이유 — 오늘 12회 전부
- [ ] **O-11** (O-3 승계) **F-L 라이브 왕복** — `logs/retrain_intraday_*_15*.log`가 생기는 날에
- [ ] **O-12** SGD 정확도 3일 연속 50% 미만 — 오늘 `daily_stats.sgd_accuracy=0.1746`(17.5%),
- [ ] **O-13** **F-Y 적용 후 첫 15:40** — ① `[CB③계측]` 1줄 ② `daily_close_done_<date>.txt`
- [ ] **O-14** **F-Z 적용 후 15:45** — `freeze_sentinel_<date>.log` CRITICAL **0건** +
- [ ] **491차 fix 잔여 검증** F-B · F-D · F-F — 오늘 첫 실행 판정이 붙지 않은 3건.
- [ ] 🔴 **F-AD** (P0) 수수료율 확정 → 재보정 + net/현금 대사 신설 (이상점 1-19)
- [ ] **F-AE** (P2) 특별조사 산출물 역링크 의무화 (이상점 1-20)
- [ ] **F-3′** (주간회의) 비용 모델 소비처 일괄 재실행 — `_calc_commission` ·
- [ ] **F-4′** (주간회의) **실전 전환 기준 ①의 판정 원천을 브로커 net으로 재정의** 검토 —
- [ ] **실전 계좌 요율 확인**을 실전 전환 기준 ⑧(자본 재설정)에 묶을 것 —
- [ ] **사용자 확인 대기** 🔴 브로커 공식 선물 미니 수수료율 (F-AD ①의 입력)
- [ ] 🔴 **CB② 복원 재검토 — 기한 2026-08-29(토) ⇒ 마지막 거래일 2026-08-28(금)**
- [ ] **F-1** (P1) 점검 세션이 repo에 잠금 시체를 남기지 않게 (이상점 1-1)
- [ ] **F-2** (P1) 런처 단일 인스턴스 가드 **재배선** (이상점 1-2)
- [ ] **F-3** (P2) 설정 불변식에 비용 모델 3행 추가 (이상점 1-3)
- [ ] **G-1** 비용 모델 **세대 배지** — 손익 표출 지점마다 `rate_gen` 병기.
- [ ] **G-2** 개장 첫 분 「하한 vs 보정기 상한」 괴리 **시계열 적재** —
- [ ] **실전 전환 기준 ②ⓑ에 F-2를 하위 확인사항으로 편입 검토** —
- [ ] **26주 WFA 「선물 수수료율」에 F-3 불변식 3행을 일일 점검 축으로 명시** —
- [ ] **O-1** (장중) C-1 — 개장 첫 분 괴리 **0.1071**(11거래일 최대, out_max 0.3479 / min_conf 0.4550).
- [ ] **O-2** (장중) C-2 — `09:03 IntradayRegime NORMAL → CRASH (day=-0.37% ATR=1.00 z=4)` ·
- [ ] **O-3** (내일 장전) F-2 적용 후 **08-27 08:40** 런처 로그에 프로브 출력 줄이 실재하는가
- [ ] **O-4** (장중·장후) 비용 모델 첫 거래일 — ① `[ProfitGuard]` 일간 한도 도달 속도
- [ ] **O-5** (0825 O-11 승계) `logs/retrain_intraday_20260826_15*.log` 존재 여부 — F-L 라이브 왕복.
- [ ] **O-6** (0825 O-13 승계) F-Y 적용 후 **첫 15:40** — ① `[CB③계측]` 1줄
- [ ] **O-7** (0825 O-14 승계) F-Z 적용 후 15:45 — `freeze_sentinel_20260826.log` CRITICAL **0건** +
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
_fired`(0/1)를 **경보 유무와 무관하게** 1행.
      적재처 `model/scaler_monitor_db.py` 계열(493차 F-AB와 같은 축).
      근거: C-1을 재려고 로그 11개 grep했고 08-17은 **결측/정상 구분 불가**(4원칙 ②)
      ⚠ **판정 무관 — 사전등록 합격선 무변경**(458차 D6)

### 로드맵·실전전환 기준 반영 제안 (주간회의)

- [ ] **실전 전환 기준 ②ⓑ에 F-2를 하위 확인사항으로 편입 검토** —
      ②ⓑ는 "동결 감시 → 하드 종료 → 런처 재기동 → 세션 복원 왕복 1회 실측"인데
      **마지막 단계인 런처 재기동이 이중 기동을 만들 수 있다.** 가드가 가짜인 상태로
      ②ⓑ를 통과시키면 왕복 시험 자체가 위험하다
- [ ] **26주 WFA 「선물 수수료율」에 F-3 불변식 3행을 일일 점검 축으로 명시** —
      상시 감시(F-2 net 대사)는 **상수가 조용히 바뀌는 것**을 못 잡는다

### 494차 관측 항목

- [ ] **O-1** (장중) C-1 — 개장 첫 분 괴리 **0.1071**(11거래일 최대, out_max 0.3479 / min_conf 0.4550).
      ① `[ConfFloorGuard]` 재발 여부 ② `[FQAdj]` 완화 후 실효 min_conf ③ 자동진입(A/B/C) 발생 여부.
      ⚠ **확정 결론 금지**(313차) — 표본 10일·결측 1일, FQAdj가 매일 개입
- [ ] **O-2** (장중) C-2 — `09:03 IntradayRegime NORMAL → CRASH (day=-0.37% ATR=1.00 z=4)` ·
      `DayRegimeShadow RANGE → CHAOS(90%)`. ① 복귀 시각 ② `[ZeroDiag]` 사유 분포
      ③ `AutoMasked` 3피처(`atr_ratio`·`volume_acceleration`·`vwap_momentum`) 격리 해제
- [ ] **O-3** (내일 장전) F-2 적용 후 **08-27 08:40** 런처 로그에 프로브 출력 줄이 실재하는가
- [ ] **O-4** (장중·장후) 비용 모델 첫 거래일 — ① `[ProfitGuard]` 일간 한도 도달 속도
      ② `[NetRecon]`/`[BrokerPnl]` **첫 라이브 EOD 대사**(F-AD ⑤) ③ `trades.commission_rate_used`
      오늘 행이 새 요율로 기록되는가
- [ ] **O-5** (0825 O-11 승계) `logs/retrain_intraday_20260826_15*.log` 존재 여부 — F-L 라이브 왕복.
      0825는 마지막 장중 재학습이 **14:10**이라 미충족 이월
- [ ] **O-6** (0825 O-13 승계) F-Y 적용 후 **첫 15:40** — ① `[CB③계측]` 1줄
      ② `daily_close_done_<date>.txt` 마커 생성
- [ ] **O-7** (0825 O-14 승계) F-Z 적용 후 15:45 — `freeze_sentinel_20260826.log` CRITICAL **0건** +
      「정상 종료」와 「동결」이 구분돼 기록되는가

### 점검 규약 메모

- [x] `report_template.md`의 절 번호 접미사(`0i`/`0p`)와 SKILL.md 대원칙 B의 **파일** 접미사
      금지(`-pre`/`-intra`/`-post`)는 **충돌하지 않는다.** 494차는 **하루 한 파일 + 절 번호
      `1p-*`** 로 절충했다(대원칙 B 우선 규정). 다음 세션이 같은 판단을 반복하지 않도록 명시.

### 커밋 대기 (오늘 커밋하지 않았다)

```
docs/정기점검/매일점검/MW0601-20260826-점검리포트.md      (신규)
docs/정기점검/매일점검/evidence_MW0601-20260826_pre.md    (신규 · 미추적)
docs/정기점검/매일점검/evidence_MW0601-20260825_pre.md    (어제분 · 미추적 잔존)
docs/정기점검/매일점검/evidence_MW0601-20260825_intra.md  (어제분 · 미추적 잔존)
docs/정기점검/매일점검/evidence_MW0601-20260825_post.md   (어제분 · 미추적 잔존)
dev_memory/DECISION_LOG.md                                (494차 append)
dev_memory/NEXT_TODO.md                                   (이 절)
```

🔴 **선행: `del C:\Users\82108\PycharmProjects\futures\.git\index.lock`** (이상점 1-1).
⚠ **`git add .` 금지** — 나머지 509건은 EOL 착시(`core.autocrlf=미설정`). 위 7개 경로만 명시 add.

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

### `data/heartbeat_MW0601_20260826.json` — 243B · 08-26 12:26:28
```json
{
 "pid": 18960,
 "written_at": "2026-08-26T12:26:58",
 "beat_epoch": 1787714816.206149,
 "beat_age_sec": 2.7,
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

### `docs/정기점검/매일점검` — 76개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260826-청산로그갭-딥다이브.md` | 11.4KB | 08-26 11:58 |
| `docs/정기점검/매일점검/MW0601-20260826-점검리포트.md` | 42.6KB | 08-26 09:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_pre.md` | 52.3KB | 08-26 09:00 |
| `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` | 301.3KB | 08-25 22:33 |
| `docs/정기점검/매일점검/MW0601-20260825-브로커손익불일치-딥다이브.md` | 25.8KB | 08-25 21:52 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_post.md` | 70.9KB | 08-25 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_intra.md` | 61.7KB | 08-25 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_pre.md` | 51.5KB | 08-25 09:00 |

### `docs/정기점검/금요일점검` — 58개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.4KB | 08-24 15:09 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260821.md` | 4.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260821.json` | 2.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md` | 26.2KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json` | 34.4KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json` | 91.9KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `.git/index.lock` 존재 (0바이트 · 0.4분 · git 프로세스 0) — 실행 중인 git 일 수 있으니 **지우지 말 것**. 몇 분 뒤에도 남아 있으면 재판정
2. `logs/20260826_WARN.log`: **Traceback** 출현 8건 — 크래시/메모리 계열
3. `logs/20260826_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
4. `logs/20260826_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. 메인 스레드 정지 5초 초과 **8건** (최대 8141ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260826_WARN.log`: **[Brier] 과신** 1건(표본)
8. `logs/20260826_WARN.log`: **ConstOut** 4건(표본)
9. `logs/20260826_SYSTEM.log`: **ConstOut** 8건(표본)
10. `logs/20260826_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20260826_SIGNAL.log`: **ConstOut** 8건(표본)
12. `logs/20260826_LEARNING.log`: **축퇴** 8건(표본)
13. 미커밋 변경 517건 (실질 2건 · 코드 0건 · EOL 파생 509건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260826*.log` (Windows) / `grep 강제청산 logs/*20260826*.log`*