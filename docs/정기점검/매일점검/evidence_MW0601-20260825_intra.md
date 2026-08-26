# 미륵이 증거 다이제스트 — 2026-08-25 / INTRA

- 생성 2026-08-25 12:25:59 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/dreamy-charming-babbage/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260825` · `2026-08-25` · `260825` · `0825`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260825.log` | 125B | 08-25 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260825.log` | 140B | 08-25 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260825.json` | 242B | 08-25 12:25 |
| `launcher_{DATE}_084000_11357.log` | 1 | `logs/Mireuk_batch/launcher_20260825_084000_11357.log` | 922.0KB | 08-25 12:24 |
| `retrain_intraday_{DATE}_094500.log` | 1 | `logs/retrain_intraday_20260825_094500.log` | 2.4KB | 08-25 09:45 |
| `retrain_intraday_{DATE}_121600.log` | 1 | `logs/retrain_intraday_20260825_121600.log` | 2.4KB | 08-25 12:16 |
| `{DATE}_DATA.log` | 1 | `logs/20260825_DATA.log` | 182.0KB | 08-25 12:25 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260825_DEBUG.log` | 130.1KB | 08-25 12:25 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260825_HEALTH.log` | 2.4KB | 08-25 12:18 |
| `{DATE}_HOGA.log` | 1 | `logs/20260825_HOGA.log` | 29.5MB | 08-25 12:25 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260825_LEARNING.log` | 182.2KB | 08-25 12:25 |
| `{DATE}_MICRO.log` | 1 | `logs/20260825_MICRO.log` | 591.8KB | 08-25 12:25 |
| `{DATE}_PROBE.log` | 1 | `logs/20260825_PROBE.log` | 57.3KB | 08-25 12:25 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260825_SIGNAL.log` | 374.8KB | 08-25 12:25 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260825_SYSTEM.log` | 447.2KB | 08-25 12:25 |
| `{DATE}_TRADE.log` | 1 | `logs/20260825_TRADE.log` | 2.9KB | 08-25 12:20 |
| `{DATE}_WARN.log` | 1 | `logs/20260825_WARN.log` | 23.7KB | 08-25 12:21 |

## 2. 코드·커밋 상태

- HEAD `f18cdad` · 브랜치 `v9-dev` · 미커밋 502건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 497건 (추적변경 499 · 미추적 3 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 3.2시간 · git 프로세스 0개 → **커밋 불가 상태**
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
… 외 462건
```

**당일(2026-08-25) 커밋**
```
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
```

**최근 커밋 12건**
```
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
91c6120 [MW0601] 491차: 0824 장후 fix 9건 구현 — F-L·F-M·F-N·F-G·F-K·F-I·F-B·F-F·F-D (+ lock_guard 콘솔)
d66ec0d [MW0601] 점검 산출물 적재: 0812~0824 일일점검 증거 27건 · 리포트 2건 · 0821 주간 3종 · 26주 WFA 피처셋 재검증
4dbdf80 [MW0601] 489차: 주간회의 승인 6건 — ⑨ WFA 이관 · [46]③ 재등록+배선 · 좀비결정 7건 분류 · [8]② 계측 이식
10178cb [MW0601] 489차 A-1: CB② 카운트를 절대원칙 문구에 맞춘다 — 시간창 + 포지션 단위 (한도 무변경)
9acc983 [MW0601] 488차 후속: 라이브 데이터에 고정된 캠페인 테스트 4개 재설계 — FAIL 12건 해소
7e82dcd [MW0601] 488차: [35] 유령 하드스톱 — 439차 "모집단 소멸" 서술 MW0601 비적용 + drop-max 계측
7451a64 [MW0601] dev_memory: MW0601_이관_점검사항 7건 조사 결과 기록
f628b83 [MW0601] 멀티PC 정책 폐기 후속: 운영 문서 3건에 남은 상호조율 관행 정리
302c8b5 [MW0601] 487차 후속 cherry-pick 조정: ConstOut 채널 번호 [51] 유지 (F-9 재배정 미적용)
1c4c6d1 [MW0602] 487차 후속: F-8(B)+F-9 구현 — 채널 [50]/[54] 브랜치 미가용 표기(감지형) + ConstOut [51]→[54] 재배정
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

### 차단 게이트 전수 인벤토리 — 32개 중 **9개 꺼짐**

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
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260825_HOGA.log` 29.5MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `20260825_MICRO.log`, `20260825_DATA.log`, `20260825_PROBE.log`, `launcher_20260825_084000_11357.log`, `20260825_DEBUG.log`, `freeze_sentinel_20260825.log`, `force_flat_guard_20260825.log`_

### `logs/20260825_TRADE.log` — 2.9KB · 23행 · 최종 12:20:00

- 형식 평문 · 시각 인식 23행 · INFO=23

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:38 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-25 08:41:43 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-25 10:12:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,350,842) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-25 10:12:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.53 tox=0.70 joint=0.374)
2026-08-25 11:25:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,350,842) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-25 11:25:01 [INFO] TRADE: [Chejan] 상태=체결 주문번호=1941 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-25 11:25:01 [INFO] TRADE: [Position] 체결청산 LONG @ 1035.74 | PnL=-0.26pt (-14,554원) | 하드스톱
2026-08-25 11:25:01 [INFO] TRADE: [청산 완료] PnL=-0.21pt (-24,108원)
2026-08-25 12:20:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,309,518) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-25 12:20:00 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.69 tox=0.70 joint=0.486)
```

</details>

**채널** — `TRADE`×23

**컴포넌트 상위 15** — `Chejan`×6, `Position`×5, `Sizer`×3, `JointGateBlock 차단`×2, `체결진입`×2, `ProfitGuard`×1, `진입체크`×1, `주문요청`×1, `체결청산-부분`×1, `청산 완료`×1

### `logs/20260825_WARN.log` — 23.7KB · 131행 · 최종 12:21:04

- 형식 평문 · 시각 인식 131행 · WARNING=131

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 63ms
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-08-25 08:41:49 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3016 band=INFO since_pipe_s=NA
2026-08-25 08:41:53 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3578ms — live 중단 원인 분석용
  …
2026-08-25 12:17:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 2974ms 경고 (기준 1000ms)
2026-08-25 12:17:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 2974ms 경고 (기준 1000ms)
2026-08-25 12:17:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3234 band=INFO since_pipe_s=0.0
2026-08-25 12:18:00 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2974ms quality=1.00 cache=0s exc10m=0) | cause=S0(2706ms)
2026-08-25 12:21:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4390ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4390 band=INFO since_pipe_s=0.1
```

</details>

**WARNING — 태그 23종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 42 | 08:41:46 | 12:21:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 10 | 09:00:01 | 12:17:03 | total=1683ms | S0=2ms S1=12ms S2=0ms S3=0ms S4=125ms S5=799ms S6=706ms S7=11ms S8=28ms |
| `CB⑤` | 10 | 09:00:02 | 12:17:03 | 파이프라인 1683ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `CB③-P4` | 10 | 10:54:00 | 11:49:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=6.7%) |
| `Health` | 9 | 09:00:01 | 12:17:03 | level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0 |
| `ScalerRefresh` | 9 | 09:07:00 | 12:14:01 | 5분 누적 수익률 -1.112% (임계 ±0.425%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ChejanFlow` | 6 | 11:25:01 | 11:25:01 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1940' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=11:25:00.827' | positio… |
| `ChejanMatch` | 6 | 11:25:01 | 11:25:01 | order_no='1940' | pending='ENTRY:LONG qty=2 filled=0 order_no=1940 reason=진입 req_at=11:25:00.827' | pending_matched=True |
| `HealthPolicy` | 5 | 09:01:00 | 12:18:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1683ms quality=0.86 cache=0s exc10m=0) | cause=S5(799ms) |
| `PendingOrder` | 4 | 11:25:00 | 11:25:02 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1035.64, 'reason': '진입', 'hint_source': '', 'atr': 1.7657, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `Canary` | 2 | 08:55:17 | 08:55:17 | scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `ConstOut` | 2 | 09:44:00 | 12:15:01 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

**채널** — `SYSTEM`×122, `HEALTH`×9

**컴포넌트 상위 15** — `LiveDBG`×42, `PipePerf`×10, `CB⑤`×10, `CB③-P4`×10, `Health`×9, `ScalerRefresh`×9, `ChejanFlow`×6, `ChejanMatch`×6, `HealthPolicy`×5, `PendingOrder`×4, `Canary`×2, `ConstOut`×2, `Contrarian`×2, `EntryFillFlow`×2, `ExitFillFlow`×2

### `logs/20260825_SYSTEM.log` — 447.2KB · 3283행 · 최종 12:25:46

- 형식 평문 · 시각 인식 3276행 · INFO=3276, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:40:54 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=5080 | 행감지=30s all_threads=True
2026-08-25 08:41:25 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-25 08:41:25 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-25 08:41:25 [INFO] SYSTEM: 미륵이 초기화
2026-08-25 08:41:25 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-24) 종가 버퍼 로드: 384봉
  …
2026-08-25 12:26:00 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=10ms meta_gate=5ms gates=0ms imp=0ms shap=6ms corr=8ms dash_ui=0ms tail=14ms
2026-08-25 12:26:00 [INFO] SYSTEM: [PipePerf][DBG] total=337ms | S0=1ms S1=23ms S2=7ms S3=0ms S4=80ms S5=172ms S6=46ms S7=5ms S8=3ms
2026-08-25 12:26:01 [INFO] SYSTEM: [CybosRT-TICK] #78000 code=A0569 raw_time=122600 parsed=12:26:00 price=1036.62 vol=1 bid1=1036.52 ask1=1036.62 flag=49 side=BUY anchor=1/0
2026-08-25 12:26:14 [INFO] SYSTEM: [CybosRT-TICK] #78100 code=A0569 raw_time=122614 parsed=12:26:14 price=1037.34 vol=1 bid1=1037.40 ask1=1037.54 flag=50 side=SELL anchor=0/1
2026-08-25 12:26:38 [INFO] SYSTEM: [CybosRT-TICK] #78200 code=A0569 raw_time=122638 parsed=12:26:38 price=1037.06 vol=1 bid1=1036.94 ask1=1037.06 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×3276

**컴포넌트 상위 15** — `CybosInvestorRaw`×818, `CybosRT-TICK`×787, `CybosRT-ROLLOVER`×221, `BAR-CLOSE`×221, `CVD-ANCHOR`×221, `TickUI`×220, `S6Detail`×207, `PipePerf`×207, `MicroRegime`×68, `System`×58, `RegimeFingerprint`×38, `OptionChain`×22, `CybosSub`×21, `IntradayRegime`×18, `BalanceUI`×13

### `logs/20260825_SIGNAL.log` — 374.8KB · 3293행 · 최종 12:25:02

- 형식 평문 · 시각 인식 3293행 · WARNING=1373, INFO=1920

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.426
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.442
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.421
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.418
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.426
  …
2026-08-25 12:26:00 [WARNING] SIGNAL: [Checklist] 신뢰도 미달 38.4% < 44.0% → 강제 X등급
2026-08-25 12:26:00 [INFO] SIGNAL: 앙상블: dir=+1 conf=38.4% grade=X micro=추세장
2026-08-25 12:26:00 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=3m tf=3.38 → TP1×0.5
2026-08-25 12:26:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.384<mc0.620)
2026-08-25 12:26:00 [INFO] SIGNAL: [MetaGate] action=reduce meta_conf=46.0% size_mult=0.68 reason=meta_reduce
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 780 | 09:00:02 | 12:15:01 | 1m 'macro_vix' scale=0.0144 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 186 | 08:45:17 | 11:40:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0231) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 144 | 09:00:00 | 12:03:00 | ts=08:59 horizon=1m age=1m max_z=+17.78(cancel_add_ratio) extreme=4 |
| `Model` | 132 | 09:00:00 | 12:02:00 | 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 86 | 09:06:00 | 12:26:00 | 신뢰도 미달 34.9% < 39.6% → 강제 X등급 |
| `WeightCollapse` | 42 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 2 | 09:44:00 | 12:14:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4420 (conf_floor=0.330, min_conf=0.442, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3293

**컴포넌트 상위 15** — `ScalerFloor`×846, `SIGNAL`×414, `MetaGate`×275, `ScalerRefresh`×217, `Ensemble`×209, `FQAdj`×204, `ZeroDiag`×189, `Model`×150, `ScalerMonitor`×144, `Checklist`×115, `InstabilityGate`×88, `ATR-Horizon`×83, `MicroRegime`×68, `ToxicityGate`×63, `차단`×48

### `logs/20260825_LEARNING.log` — 182.2KB · 1702행 · 최종 12:25:02

- 형식 평문 · 시각 인식 1702행 · WARNING=148, INFO=1554

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:27 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00052 auc=0.500 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-25 08:41:29 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00022 auc=0.538 out_max=0.2942 (n=85) → 보정 재적용
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2942 < conf_floor=0.3300 (span=0.00022 auc=0.538 out_max=0.2942, 기저율=0.2941 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-08-25 12:26:00 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=40.3% FL)
2026-08-25 12:26:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=56.1% UP)
2026-08-25 12:26:00 [INFO] LEARNING: [MetaConf] LR[추세장] 비동기 학습 완료 (n=300, classes=[0, 1, 2, 3])
2026-08-25 12:26:00 [INFO] LEARNING: [OnlineLearner] 15m SGD UP붕괴 자동 복구 (≥80% 12분 지속) → 모델·스케일러 리셋
2026-08-25 12:26:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=25.0%
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 147 | 08:41:29 | 12:23:01 | 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 1 | 11:43:00 | 11:43:00 | total=712ms raw_fetch=5ms pred_select=2ms pred_update=1ms pred_insert=0ms verified=2 |

**채널** — `LEARNING`×1702

**컴포넌트 상위 15** — `LEARNING`×660, `Calibration`×286, `SGD`×206, `sigma`×194, `Bias⚠`×137, `Bias`×70, `OnlineLearner`×43, `MetaConf`×40, `ScalerWarmup`×31, `BiasReset`×10, `SHAP`×7, `GBM-64`×4, `GBM`×4, `RF`×3, `ExtremityCorrector`×2

### `logs/20260825_HEALTH.log` — 2.4KB · 18행 · 최종 12:18:00

- 형식 평문 · 시각 인식 18행 · WARNING=9, INFO=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0
2026-08-25 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=521ms | quality=0.86 | cache_age=68s | exceptions_10m=0
2026-08-25 09:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=333ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-08-25 09:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=440ms | quality=1.00 | cache_age=56s | exceptions_10m=0
2026-08-25 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 384ms (표본 20분)
  …
2026-08-25 11:44:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=360ms | quality=1.00 | cache_age=95s | exceptions_10m=0
2026-08-25 12:10:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=332ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-25 12:11:02 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=295ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-25 12:17:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2974ms | quality=1.00 | cache_age=52s | exceptions_10m=0
2026-08-25 12:18:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=378ms | quality=1.00 | cache_age=110s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:01 | 12:17:03 | level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0 |

**채널** — `HEALTH`×18

**컴포넌트 상위 15** — `Health`×17, `HealthTrend`×1

### `logs/retrain_intraday_20260825_121600.log` — 2.4KB · 20행 · 최종 12:16:23

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 12:16:00,717 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-25 12:16:00,717 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-25 12:16:00,718 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-25 12:16:00,718 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_07b506a1.json
2026-08-25 12:16:03,448 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-25 12:16:23,114 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.96s | old_acc=0.4054)
2026-08-25 12:16:23,202 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-25 12:16:23,202 [INFO] LEARNING: [Retrain] 완료 | 19.8초 | 성공=1/1 호라이즌
2026-08-25 12:16:23,203 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.5s 데이터=4800행
2026-08-25 12:16:23,204 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_07b506a1.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260825_094500.log` — 2.4KB · 20행 · 최종 09:45:22

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 09:45:00,803 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-25 09:45:00,803 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-25 09:45:00,804 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-25 09:45:00,804 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7a8c09cb.json
2026-08-25 09:45:03,851 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-25 09:45:22,612 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.94s | old_acc=0.4054)
2026-08-25 09:45:22,701 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-25 09:45:22,702 [INFO] LEARNING: [Retrain] 완료 | 18.8초 | 성공=1/1 호라이즌
2026-08-25 09:45:22,702 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.9s 데이터=4800행
2026-08-25 09:45:22,704 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7a8c09cb.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 1 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 2 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 48 |
| 사이저 호출(`[Sizer]`) | 3 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|

**청산 레그 0행** (부분청산 1 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 -24,108 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 1건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패 레그 2행 ⚠**(진입 로그 없는 이월 포지션 가능)

등급 분포 — `A급(원시C)`×1

**진입한 건들의 체크리스트 미통과 항목** — `ofi`×1, `fore`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×3

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×3

### 차단 사유 48건 · 14종

| 건수 | 사유 |
|---|---|
| 28 | 등급X — 미통과 항목: 2_confidence |
| 3 | 등급X — 미통과 항목: 3_vwap |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 10_chase |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd |
| 1 | JointGateBlock — meta=0.53 tox=0.70 joint=0.374 < 0.50 |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi |
| 1 | 등급X — 미통과 항목: 3_vwap, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar, 10_chase |
| 1 | 청산 후 쿨다운 — 121초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 61초 후 재진입 가능 |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | JointGateBlock — meta=0.69 tox=0.70 joint=0.486 < 0.50 |

**체크리스트 미통과 항목 누적** — `2_confidence`×28, `3_vwap`×15, `4_cvd`×8, `7_prev_bar`×7, `5_ofi`×5, `10_chase`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 21건 · 최대 8625ms · 5초 초과 6건

상위 — 8625ms, 7297ms, 5890ms, 5437ms, 5234ms, 5093ms, 4687ms, 4625ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8625ms | 1683ms | **6942ms (80%)** |
| 09:05:04 | 5093ms | 294ms | **4799ms (94%)** |
| 11:43:07 | 7297ms | 2506ms | **4791ms (66%)** |
| 11:48:05 | 5437ms | 381ms | **5056ms (93%)** |
| 11:58:05 | 5234ms | 392ms | **4842ms (93%)** |
| 12:03:06 | 5890ms | 381ms | **5509ms (94%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260825_WARN.log`
```
--- ConstOut ×2(표본)
09:44:00 2026-08-25 09:44:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:15:01 2026-08-25 12:15:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×1(표본)
11:25:01 2026-08-25 11:25:01 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×2(표본)
11:25:01 2026-08-25 11:25:01 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 3분 재진입 금지 (until 11:28:01)
11:25:01 2026-08-25 11:25:01 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 3분 재진입 금지 (until 11:28:01)
--- 메인 스레드 블로킹 ×8(표본)
08:41:49 2026-08-25 08:41:49 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3016 band=INFO since_pipe_s=NA
09:00:08 2026-08-25 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8625 band=WARN since_pipe_s=0.2
09:01:01 2026-08-25 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2234 band=INFO since_pipe_s=0.0
09:02:01 2026-08-25 09:02:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2218ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2218 band=INFO since_pipe_s=0.0
```

### `logs/20260825_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:44:00 2026-08-25 09:44:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:46:00 (const_output)
09:44:00 2026-08-25 09:44:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:44:00 2026-08-25 09:44:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=97ms fit=79ms total=179ms
09:45:00 2026-08-25 09:45:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-08-25 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.033 level=0 (heartbeat)
09:05:00 2026-08-25 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.033 level=0 (heartbeat)
09:11:00 2026-08-25 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.033 level=0 (heartbeat)
09:16:00 2026-08-25 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.033 level=0 (heartbeat)
```

### `logs/20260825_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-08-25 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4420 (conf_floor=0.330, min_conf=0.442, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:44:00 2026-08-25 09:44:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:44:00 2026-08-25 09:44:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:45:00 2026-08-25 09:45:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:46:03 2026-08-25 09:46:03 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-08-25 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:07:00 2026-08-25 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-08-25 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-08-25 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.426
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.442
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.421
08:40:48 2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.418
--- 안전망 ×8(표본)
09:07:00 2026-08-25 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-08-25 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-25 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-08-25 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260825_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:29 2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:41:29 2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00052 auc=0.500 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:29 2026-08-25 08:41:29 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00022 auc=0.538 out_max=0.2942 (n=85) → 보정 재적용
08:41:29 2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2942 < conf_floor=0.3300 (span=0.00022 auc=0.538 out_max=0.2942, 기저율=0.2941 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260825_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:38 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 12:20

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260825_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:46 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 14 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 16 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 2 | 09:54:00 [WARNING] 5분 누적 수익률 +0.507% (임계 ±0.393%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 2 | 11:58:05 [WARNING] _tick_header 간격 5234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5234 band=… |

- 이 로그 생존구간: 08:41 ~ 12:21

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260825_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 87 | 08:40:54 [INFO] 활성화 | file=logs\crash_fault.log PID=5080 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 127 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 190 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 184 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 170 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:26

**매분 루프 커버리지 09:00~15:10: 207/371분 (55.8%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:27 | 15:10 | 164 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260825_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:17 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0231) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 183 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0235) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 268 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0258) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 209 | 09:54:00 [WARNING] ts=09:53 horizon=1m age=10m max_z=+4.35(cancel_add_ratio) extreme=1 |
| 12:00 | 장중 중간점 | 159 | 11:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |

- 이 로그 생존구간: 08:40 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260824 | 15:40 | 로그 본문 |
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260825** | **12:26** | 로그 본문 |

- 델타 **-194분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [1-5] 미커밋 499건 — 전부 EOL 파생, 실질 변경 0 (P2)
### [1-6] 예약 실행이 로드한 스킬 사본이 낡은 판 — `--pc MW0602`를 지시하고 있었다 (P2)
### 이상점으로 올리지 않은 것 — 기존 특성화·기존 등록 (중복 보고 방지)
### 재인용 금지 준수
### [1-7] 🔴 이 점검이 `.git/index.lock`을 남겼고 세션에서 지울 수 없다 (P2, 자가유발)
### [1-8 / ↩️1-1 정정] `[GUARD]` 단일 인스턴스 감지가 11회 중 10회 위양성 — 판정 근거 3갈래가 전부 폐기된다 (P1)
### [1-8 후속 12:20] 판별 완료 — **H1 기각 · H2 확정.** 가드가 남의 프로세스를 죽여 왔을 개연성
### [1-8 후속2 12:23] 재실행 2회 — 새 정보 없음. 진단을 **스크립트로 전환**
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
.py` 글자 없음) · 마흐디 관측루프
(`uv run python -m mahdi.main` — **모듈 호출**이라 글자 불일치, 실측으로도
`options/logs/watchdog.log` 08:40:02·08:50:02 전부 `OK — 박동 정상`) · 마흐디 대시보드
(`streamlit run mahdi/dashboard/app.py`) · 미륵이 `scripts/*.py`의 `main.py` 언급
(전부 주석·독스트링, 명령줄 아님).
**남은 후보**: ① **타 프로젝트의 `main.py`** — 사용자 셸 cwd가
`C:\Users\82108\PycharmProjects\fuoption` 이었다. futures·options 외 최소 1개 프로젝트가
더 있다 ② 08:40 전후 단명 프로세스.

**🔴 부수 발견 — 프로브가 32비트라 64비트 프로세스를 못 본다.**
`py37_32`에서 64비트 프로세스의 `cmdline`을 읽으면 AccessDenied → `psutil`이 `None` 반환
→ 코드가 `(… or [])`로 받아 **빈 목록 → 무조건 불일치**. ⇒ 가드는 **양방향으로 틀린다**:
글자만 겹치면 남의 것도 잡고(과잉 종료), 64비트로 도는 진짜 중복은 **미탐**.
본체가 `py37_32`(32비트)라 보이는 것은 **우연이지 설계가 아니다.**
계측 4원칙 ②의 전형 — *"못 읽었다"* 가 *"일치하지 않는다"* 로 조용히 바뀐다.

**결정: F-U에 3개 추가(장후).**
- **5′** 절대경로 일치 + **`p.cwd()`가 WORKDIR 하위인지** 확인, 불일치는
  `[GUARD] 대상 아님(타 프로젝트): PID=… path=…` 로 **로그 후 건너뛴다**
- **8** 프로브를 **64비트(py310_64)** 로 실행하거나, 명령줄 판독 실패를
  `[GUARD] 판독불가 PID=… (권한)` 으로 **집계·로그**. 1건이라도 있으면
  **`단일 인스턴스 미확정`** 표기(계측 4원칙 ②)
  ⚠ 프로브 전용 단발 호출이며 재학습 런타임 규약(191차)과 무관
- **9** `terminate()` 대상이 **WORKDIR 밖**이면 **죽이지 않고 경고만**(기본값).
  넘어서려면 명시 플래그. **남의 프로그램을 죽이는 것은 이 런처의 권한 밖이다**

**다음 입력 대기**: 사용자에게 ① 파이썬 프로세스 전수 목록(**기동시각 포함**) —
08:40:4x 기동이 있으면 그것이 "죽고 다시 켜진" 범인이다 ② 같은 명령을 **64비트로 한 번 더**
(32비트 사각지대 실측 확인) ③ `fuoption` 프로젝트의 정체를 요청했다.

### [1-8 후속2 12:23] 재실행 2회 — 새 정보 없음. 진단을 **스크립트로 전환**

사용자가 실행한 것은 제1부-B의 **같은 판별 명령 2회**였다(요청한 전수 목록 명령이 아니다).
원인은 **내가 준 명령이 한 줄 300자를 넘어 붙여넣기에서 잘린 것**으로 보인다 —
전달 방식의 문제이지 사용자 문제가 아니다.

**두 번의 결과가 준 정보 하나**: 12:20·12:23 3분 간격으로 `실행 중 main.py: 1`(PID 5080
본체)로 동일. ⇒ 스냅샷 요동이 아니라 **안정 상태**이며, 08:40:24에 잡힌 프로세스는
**지금 재기동돼 돌고 있지 않다.** 후보 ①(죽였는데 재기동 장치가 없다) 또는
②(08:40 전후 단명)로 기운다. H2 확정은 그대로.

**결정**: `scripts/diag_guard_processes.py` **신설(진단 전용)**.
- **기존 코드 무수정.** `main.py`·`config/settings.py`·매매 로직에서 import 되지 않는다.
  표준 라이브러리 + `psutil` 만. **`terminate`/`kill` 호출이 파일에 없고**, 파일 쓰기·DB·
  주문 전무. 장중 실행 안전. `py_compile` 통과 + 샌드박스 실행 확인.
- 출력 4절: [1] 파이썬 전수(기동시각순, `<< 08:35~08:50 기동` 표시) ·
  [2] 지금 `[GUARD]`가 돌면 죽일 대상(`🔴 미륵이가 아니다` 표시) ·
  [3] `판독불가` 개수(32/64비트 대조용) · [4] 아침 창 기동 목록.
- 판정식(`'python' in name` ∧ `'main.py' in cmdline`)을 **런처와 글자 하나까지 같게**
  유지한다 — 다르면 진단이 무의미하다. 주석에 그 요구를 박아 뒀다.
**Why**: (c) 프로브 stdout 미기록을 사람 손으로 대신 본다. F-U 적용 전까지 유일한 관측 수단.
**F-U와의 관계**: 이 파일이 **F-U 프로브의 원형**이다. 구현 시
`scripts/guard_single_instance.py`로 정리하며 종료코드 3분류(0/1/3) + 런처 로그 기록을 붙인다.
**검증 대기**: 사용자 실행 결과 — [2]에 `🔴 미륵이가 아니다`가 뜨면 **과잉 종료 실증**,
[3]의 32/64 `판독불가` 개수 차이가 나면 **미탐 실증**.

```

</details>

### dev_memory/NEXT_TODO.md — 1.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 492차 (2026-08-25) — 피처 수명 분석 후속 · 주간회의 안건
### 주간회의 안건 (신규)
### 다음 26주 창 사전등록 대상
### 상시 주의 (규약)
## MW0601 493차 (2026-08-25) — 일일 점검 장전 fix/관측
### 493차 관측 항목 (오늘 장중·장후가 닫는다)
### 493차에 종결된 항목
## MW0601 493차 후속 (2026-08-25 12:01) — 사용자 정정에 따른 GUARD 재조사
```

미완료 체크박스 **1916건** (끝에서 30건)
```
- [ ] **B-10** 계열별 호라이즌 특화를 **사전등록 항목**으로 등록. §14-5 순열 p=0.1426은
- [ ] **B-11** 순열·집계 코드에 **NaN 가드 공통화**. 이번에 NaN 전파가 p를 0에 붙였다
- [ ] **B-12** tau ≤ 1분 16개는 **1분봉 격자로 판정 불가** — 초 단위 데이터가 있어야 한다.
- [ ] **B-13** 피처 등록 시 **유형 태그(D/B/C/S/I/N)를 메타데이터로 부착**.
- [ ] 26주 재검증 착수 시 **`피처_재검증_및_호라이즌배정_원칙.md`를 먼저 열 것.**
- [ ] **임계 상수가 두 곳에 복사돼 있다** — `feature_health_report.py`의 `SHAPE_*` ↔
- [ ] 자기상관·수명 지표의 널은 **`shuffle`이다.** `phase_randomize`는 ACF를 보존해
- [ ] **F-P (P1) 5초~180초 무감시 구간 스택 스냅샷** — `main.py:_tick_header()` `[MainStall]`
- [ ] **F-Q (P1) 장전 스케일러 궤적 1줄 + 08:59 Canary 섀도** — `main.py`의
- [ ] **F-R (P2) `.gitattributes` 신설 + `git add --renormalize .`** — 미커밋 499건이
- [ ] **F-S (P2) 예약 실행 경로에 `--pc MW0601` 명시 고정** —
- [ ] **(스킬 문서) `phases.md` A-2 "선물 분봉 TR이 `OPT50029`인가" 를 브로커 분기로 나눌 것** —
- [ ] **O-4** `[ConfFloorGuard]` 09:00:01 1건이 이후 `state=OK`로 복귀하는가(복귀 시각 기록).
- [ ] **O-5** 개장 첫 4분 `[ZeroDiag] conf미달` 중 **`conf=0.000`이 2분**(09:01·09:02).
- [ ] **O-6** 장전 z경고 잔존 목록에 `institution_futures_net`이 08:48·08:50·08:55
- [ ] **N-11** 잔고 요약 필드 매핑 — 오늘 `총평가수익률=49,350,842`(=총매매와 동일 금액) ·
- [ ] **O-1(승계 O-2′)** 단기 CORE 2종의 SHAP 피처 구성 기여 — `15:40 [SHAP] 주간 심사 완료`.
- [ ] **O-2(승계 O-10)** 30m 모델 정확도(어제 0.4158→0.3786). 오늘 `gbm_30m_acc.txt`.
- [ ] **O-3(승계 O-11)** `logs/retrain_intraday_20260825_15*.log` 존재 여부 —
- [ ] **CB② 복원 카운터팩추얼 표를 08-27까지 준비** — 재검토 기한 2026-08-29, 실무 판정일
- [ ] **F-T (P2, 자가유발) 점검 세션의 git 호출을 인덱스 무접촉으로 고정** —
- [ ] **F-U (P1, 장후) 단일 인스턴스 가드를 「증거를 남기는」 형태로 재작성** —
- [ ] **(사용자) H1/H2 판별 1회 실행** — 원 명령에서 **`2>NUL` 제거 + terminate 제외** 후
- [ ] **(점검 규약) 근거로 쓰는 로그 줄의 「출력 조건」을 확인할 것** —
- [ ] **1-1 재분류** — "사용자 미이행"이 아니라 **가드 위양성**이었다. 다만 0824 이상점
- [ ] **F-U 보강 3건(위 F-U에 병합)** — **5′** cwd가 WORKDIR 하위인지 확인 후 불일치는
- [ ] **(사용자 입력 대기) 파이썬 프로세스 전수 목록 + 기동시각** — 08:40:4x 기동이 있으면
- [ ] **(사용자 입력 대기) `C:\Users\82108\PycharmProjects\fuoption` 프로젝트 정체** —
- [ ] **(사용자 입력 대기 · 8′) `scripts/diag_guard_processes.py` 를 32비트·64비트로 각 1회** —
- [ ] **`scripts/diag_guard_processes.py` 를 F-U 구현 시 `guard_single_instance.py` 로 승격** —
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 08-24 월 감지**가 결정적). 원인은 (a) 종료코드 충돌 `sys.exit(1 if procs else 0)` ↔
      파이썬 예외도 1 (b) `2>NUL`로 stderr 폐기 (c) 프로브 stdout이 로그에 **11개 전수 0건**.
      ⚠ `main.py`·`config/settings.py`·매매 로직 **무접촉**. 절대원칙 저촉 없음.
      검증: 유닛(0/1/예외→0/1/3) · **리허설에서 `[GUARD] 기존 main.py 없음`이 찍히는가
      (11회 중 0회였던 줄 — 이 한 줄이 합격 판정)** · 더미 프로세스 종료 후 `잔여=0` ·
      다음 거래일 08:40에 `[GUARD] 실행 중 main.py: N` 최초 기록. 비용 중.

- [ ] **(사용자) H1/H2 판별 1회 실행** — 원 명령에서 **`2>NUL` 제거 + terminate 제외** 후
      py37_32로 실행. `실행 중 main.py: 1`(+오늘 본체 PID) → **H2**(판정식이 느슨) /
      `Traceback` → **H1**(프로브 자체가 무동작). 둘의 수리 지점이 다르다.
      ⚠ **`p.terminate()`가 든 원 명령은 실행 금지** — 라이브 미륵이를 즉시 죽인다.
      ⚠ 장중 실행 안전(프로세스 열거만, DB·주문 무관).

- [ ] **(점검 규약) 근거로 쓰는 로그 줄의 「출력 조건」을 확인할 것** —
      ① 조건부 출력인가 **무조건 출력**인가 ② 판정에 쓰인 **원자료가 로그에 함께 남는가**.
      0825에 `[GUARD] 기존 프로세스 종료 완료`(무조건 출력)와 `[WARN] … 감지`(원자료 폐기)를
      **관측 사실로 오독**해 이상점 1-1의 전제를 틀리게 세웠다. 사용자 정정이 없었으면
      그대로 지나갔다. `references/postmortem.md` 또는 `phases.md` 서문에 반영할 것.

- [ ] **1-1 재분류** — "사용자 미이행"이 아니라 **가드 위양성**이었다. 다만 0824 이상점
      1-12(15:40:20 동결)와 **F-L 미적용**은 그대로 유효하다 — 어제 동결은 실재했고
      사용자가 당일 종료했다. **F-L의 우선순위는 내려가지 않는다.**
- [x] **H1/H2 판별 완료(12:20)** — **H1 기각 · H2 확정.** 프로브는 정상 동작한다
      (`실행 중 main.py: 1` + PID 5080 본체, traceback 없음). ⇒ 08:40:24의 감지는 진짜
      일치였고, 그것은 본체도 전날 잔류도 아니다 ⇒ **판정식이 남의 프로세스를 잡아
      죽여 왔을 개연성.** 상세는 DECISION_LOG 493차 후속.
- [ ] **F-U 보강 3건(위 F-U에 병합)** — **5′** cwd가 WORKDIR 하위인지 확인 후 불일치는
      로그 남기고 **건너뛴다** · **8** 프로브를 **64비트로 실행**하거나 명령줄 판독실패를
      `판독불가` 로 집계하고 1건이라도 있으면 **`단일 인스턴스 미확정`** 표기(계측 4원칙 ②
      — 32비트 프로브는 64비트 프로세스 cmdline을 못 읽어 **미탐**한다) · **9** WORKDIR 밖
      대상은 **죽이지 않고 경고만**(기본값).
- [ ] **(사용자 입력 대기) 파이썬 프로세스 전수 목록 + 기동시각** — 08:40:4x 기동이 있으면
      "08:40:37에 죽고 곧바로 재기동된" 범인이다. **64비트 파이썬으로도 한 번 더** 받아
      32비트 사각지대를 실측 확인할 것.
- [ ] **(사용자 입력 대기) `C:\Users\82108\PycharmProjects\fuoption` 프로젝트 정체** —
      `main.py`가 있고 아침에 돌면 최우선 용의자.
- [ ] **(사용자 입력 대기 · 8′) `scripts/diag_guard_processes.py` 를 32비트·64비트로 각 1회** —
      긴 한 줄 명령이 붙여넣기에서 잘려 12:20·12:23 재실행이 **같은 판별 명령 2회**가 됐다.
      스크립트로 전환했다. 확인 지점: [2]에 `🔴 미륵이가 아니다` → **과잉 종료 실증** /
      [3] 32·64비트 `판독불가` 개수 차 → **미탐 실증** / [4] 08:35~08:50 기동 목록 → **범인**.
- [ ] **`scripts/diag_guard_processes.py` 를 F-U 구현 시 `guard_single_instance.py` 로 승격** —
      판정식을 런처와 **글자 하나까지 같게** 유지할 것(다르면 진단이 무의미하다).
      승격 시 종료코드 3분류(0없음/1발견/3실패) + `CALL :L` 로그 기록 + cwd 게이트(5′) +
      64비트 실행 또는 `판독불가` 집계(8) + WORKDIR 밖 경고전용(9) 을 함께 붙인다.

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

### `data/heartbeat_MW0601_20260825.json` — 242B · 08-25 12:25:53
```json
{
 "pid": 5080,
 "written_at": "2026-08-25T12:26:23",
 "beat_epoch": 1787628381.7116933,
 "beat_age_sec": 2.2,
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

### `docs/정기점검/매일점검` — 70개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` | 87.5KB | 08-25 12:23 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_pre.md` | 51.5KB | 08-25 09:00 |
| `docs/정기점검/매일점검/MW0601-20260824-점검리포트.md` | 191.2KB | 08-24 16:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_post.md` | 70.6KB | 08-24 16:21 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_intra.md` | 65.2KB | 08-24 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_pre.md` | 47.4KB | 08-24 08:59 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.0KB | 08-23 16:51 |
| `docs/정기점검/매일점검/MW0601-20260821-점검리포트.md` | 208.7KB | 08-21 16:54 |

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

1. `.git/index.lock` **스테일 잔존** (0바이트 · 3.2시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. `logs/20260825_SYSTEM.log`: 매분 루프 커버리지 207/371분 (55.8%) — 루프가 빠진 구간이 있다
3. `logs/20260825_SYSTEM.log`: 12:27~15:10 **연속 164분 매분 루프 기록 없음**
4. 메인 스레드 정지 5초 초과 **6건** (최대 8625ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
5. `logs/20260825_WARN.log`: **ConstOut** 2건(표본)
6. `logs/20260825_SYSTEM.log`: **ConstOut** 8건(표본)
7. `logs/20260825_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20260825_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20260825_LEARNING.log`: **축퇴** 8건(표본)
10. 미커밋 변경 502건 (실질 2건 · 코드 0건 · EOL 파생 497건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260825*.log` (Windows) / `grep 강제청산 logs/*20260825*.log`*