# 미륵이 증거 다이제스트 — 2026-08-25 / POST

- 생성 2026-08-25 16:21:41 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/magical-clever-ptolemy/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260825` · `2026-08-25` · `260825` · `0825`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **23개** 파일 · 23개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260825.txt` | 28B | 08-25 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260825.txt` | 208B | 08-25 15:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260825.log` | 443B | 08-25 15:12 |
| `freeze_sentinel_alert_{DATE}.txt` | 1 | `data/freeze_sentinel_alert_20260825.txt` | 434B | 08-25 15:45 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260825.log` | 16.7KB | 08-25 16:20 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260825.json` | 243B | 08-25 15:40 |
| `launcher_{DATE}_084000_11357.log` | 1 | `logs/Mireuk_batch/launcher_20260825_084000_11357.log` | 1.5MB | 08-25 15:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260825.log` | 19.3KB | 08-25 15:48 |
| `retrain_intraday_{DATE}_094500.log` | 1 | `logs/retrain_intraday_20260825_094500.log` | 2.4KB | 08-25 09:45 |
| `retrain_intraday_{DATE}_121600.log` | 1 | `logs/retrain_intraday_20260825_121600.log` | 2.4KB | 08-25 12:16 |
| `retrain_intraday_{DATE}_131100.log` | 1 | `logs/retrain_intraday_20260825_131100.log` | 2.4KB | 08-25 13:11 |
| `retrain_intraday_{DATE}_141000.log` | 1 | `logs/retrain_intraday_20260825_141000.log` | 2.4KB | 08-25 14:10 |
| `{DATE}_DATA.log` | 1 | `logs/20260825_DATA.log` | 343.8KB | 08-25 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260825_DEBUG.log` | 232.4KB | 08-25 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260825_HEALTH.log` | 4.0KB | 08-25 14:35 |
| `{DATE}_HOGA.log` | 1 | `logs/20260825_HOGA.log` | 50.9MB | 08-25 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260825_LEARNING.log` | 291.4KB | 08-25 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260825_MICRO.log` | 1018.5KB | 08-25 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260825_PROBE.log` | 96.6KB | 08-25 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260825_SIGNAL.log` | 562.8KB | 08-25 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260825_SYSTEM.log` | 793.7KB | 08-25 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260825_TRADE.log` | 5.6KB | 08-25 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260825_WARN.log` | 43.6KB | 08-25 15:40 |

## 2. 코드·커밋 상태

- HEAD `f18cdad` · 브랜치 `v9-dev` · 미커밋 504건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 497건 (추적변경 499 · 미추적 5 · 삭제 0 · core.autocrlf=미설정) · 🔴 **인덱스락 잔존** 0바이트 · 7.1시간 · git 프로세스 0개 → **커밋 불가 상태**
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
… 외 464건
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

_본문 미열람(설정): `20260825_HOGA.log` 50.9MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_started_20260825.txt`** — 28B · 08-25 15:40:16
```
2026-08-25T15:40:16.256597
```

**`data/eod_retrain_done_20260825.txt`** — 208B · 08-25 15:48:39
```
completed: 2026-08-25 15:48:39
rows: 40386
cols: 97
horizons_replaced: 6/6
t_load_s: 42.7
t_retrain_s: 171.8
t_total_s: 215.0
daily_close_seen: false
wait_dc_timeout: true
daily_close_stalled: true
```

**`data/freeze_sentinel_alert_20260825.txt`** — 434B · 08-25 15:45:41
```
[FreezeSentinel] 2026-08-25 15:45:41 CRITICAL
  라이브 프로세스 동결 — 측정 가능한 신호 3종이 전부 300s 이상 정체다. 프로세스는 살아 있을 수 있으나 아무 일도 하지 않는다 (런처 재기동도 걸리지 않는다)
  · heartbeat        312s 전 (임계 300s) — 정체
  · crash_fault[TS]  312s 전 (임계 300s) — 정체
  · SYSTEM.log       309s 전 (임계 300s) — 정체
```

_다이제스트 대상 8/18개 (중요도순). 제외: `retrain_intraday_20260825_094500.log`, `retrain_intraday_20260825_131100.log`, `retrain_intraday_20260825_141000.log`, `20260825_MICRO.log`, `20260825_DATA.log`, `20260825_PROBE.log`, `launcher_20260825_084000_11357.log`, `20260825_DEBUG.log`_

### `logs/20260825_TRADE.log` — 5.6KB · 46행 · 최종 15:40:17

- 형식 평문 · 시각 인식 46행 · INFO=46

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:38 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-25 08:41:43 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-25 10:12:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,350,842) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-25 10:12:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.53 tox=0.70 joint=0.374)
2026-08-25 11:25:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,350,842) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-25 12:33:25 [INFO] TRADE: [Chejan] 상태=접수 주문번호=2716 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-25 12:33:26 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2716 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-25 12:33:26 [INFO] TRADE: [Position] 체결청산 LONG @ 1042.64 | PnL=+0.27pt (+11,936원) | 하드스톱(틱)
2026-08-25 12:33:26 [INFO] TRADE: [청산 완료] PnL=+0.27pt (+11,936원)
2026-08-25 15:40:17 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×46

**컴포넌트 상위 15** — `Chejan`×13, `Position`×9, `Sizer`×4, `주문요청`×4, `체결진입`×3, `ProfitGuard`×2, `JointGateBlock 차단`×2, `진입체크`×2, `청산 완료`×2, `체결청산-부분`×1, `체결진입보정`×1, `TickTP1`×1, `TP1 부분청산`×1, `TickStop-S0C`×1

### `logs/20260825_WARN.log` — 43.6KB · 231행 · 최종 15:40:17

- 형식 평문 · 시각 인식 225행 · ERROR=3, WARNING=222, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 63ms
2026-08-25 08:41:46 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-08-25 08:41:49 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3016 band=INFO since_pipe_s=NA
2026-08-25 08:41:53 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3578ms — live 중단 원인 분석용
  …
self.daily_close()
File "C:\Users\82108\PycharmProjects\futures\main.py", line 11849, in daily_close
float(_cb3_avail_eod.get("threshold") or 0.0)),
ValueError: unsupported format character ',' (0x2c) at index 62
2026-08-25 15:40:17 [ERROR] SYSTEM: [DailyClose] 예외 → 강제 종료 예약: unsupported format character ',' (0x2c) at index 62
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `DailyClose` | 2 | 15:40:17 | 15:40:17 | 예외 발생 — 강제 종료 예약: unsupported format character ',' (0x2c) at index 62 |
| ERROR | `LiveDBG` | 1 | 13:14:21 | 13:14:21 | _tick_header 간격 21781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=21781 band=ALERT since_pipe_s=0.1 |

<details><summary>ERROR/DailyClose 원문 2건</summary>

```
2026-08-25 15:40:17 [ERROR] SYSTEM: [DailyClose] 예외 발생 — 강제 종료 예약: unsupported format character ',' (0x2c) at index 62
2026-08-25 15:40:17 [ERROR] SYSTEM: [DailyClose] 예외 → 강제 종료 예약: unsupported format character ',' (0x2c) at index 62
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-08-25 13:14:21 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 21781ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=21781 band=ALERT since_pipe_s=0.1
```

</details>

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 61 | 08:41:46 | 14:47:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `PipePerf` | 16 | 09:00:01 | 14:11:03 | total=1683ms | S0=2ms S1=12ms S2=0ms S3=0ms S4=125ms S5=799ms S6=706ms S7=11ms S8=28ms |
| `CB⑤` | 16 | 09:00:02 | 14:11:03 | 파이프라인 1683ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 16 | 09:07:00 | 14:44:01 | 5분 누적 수익률 -1.112% (임계 ±0.425%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 15 | 09:00:01 | 14:34:00 | level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0 |
| `CB③-P4` | 14 | 10:54:00 | 13:47:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=6.7%) |
| `ChejanFlow` | 13 | 11:25:01 | 12:33:26 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1940' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=11:25:00.827' | positio… |
| `ChejanMatch` | 13 | 11:25:01 | 12:33:26 | order_no='1940' | pending='ENTRY:LONG qty=2 filled=0 order_no=1940 reason=진입 req_at=11:25:00.827' | pending_matched=True |
| `PendingOrder` | 10 | 11:25:00 | 12:33:26 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1035.64, 'reason': '진입', 'hint_source': '', 'atr': 1.7657, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `HealthPolicy` | 8 | 09:01:00 | 14:12:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1683ms quality=0.86 cache=0s exc10m=0) | cause=S5(799ms) |
| `ConstOut` | 4 | 09:44:00 | 14:09:01 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| `EntryFillFlow` | 4 | 11:25:01 | 12:32:00 | actual_side='LONG' | after='LONG 1계약 @ 1036.00' | applied_side='LONG' | before='FLAT' | fill_no='' | fill_price=1036.0 | fill_qty=1 | order_no='1940' | pending='ENTRY:LONG qty=2 filled=1 order_no=1940 reason=진입 req_at=11:25:00.827' |

**채널** — `SYSTEM`×210, `HEALTH`×15

**컴포넌트 상위 15** — `LiveDBG`×62, `PipePerf`×16, `CB⑤`×16, `ScalerRefresh`×16, `Health`×15, `CB③-P4`×14, `ChejanFlow`×13, `ChejanMatch`×13, `PendingOrder`×10, `HealthPolicy`×8, `-`×6, `ConstOut`×4, `EntryFillFlow`×4, `ExitCooldown`×4, `ExitFillFlow`×3

### `logs/20260825_SYSTEM.log` — 793.7KB · 5839행 · 최종 15:40:32

- 형식 평문 · 시각 인식 5826행 · INFO=5826, PLAIN=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:40:54 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=5080 | 행감지=30s all_threads=True
2026-08-25 08:41:25 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-25 08:41:25 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-25 08:41:25 [INFO] SYSTEM: 미륵이 초기화
2026-08-25 08:41:25 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-24) 종가 버퍼 로드: 384봉
  …
2026-08-25 15:40:17 [INFO] SYSTEM: [BrokerPnl] EOD 확정 — gross +39,000 − 수수료 6,235 = net +32,765원 (broker 대사 일치)
2026-08-25 15:40:17 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-25 15:40:32 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-25 15:40:32 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-25 15:40:32 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5826

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1259, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `MicroRegime`×109, `System`×98, `RegimeFingerprint`×68, `OptionChain`×41, `IntradayRegime`×38, `CybosEvent`×26, `BalanceUI`×22

### `logs/20260825_SIGNAL.log` — 562.8KB · 5043행 · 최종 15:40:17

- 형식 평문 · 시각 인식 5043행 · WARNING=1885, INFO=3158

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.426
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.442
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.421
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.418
2026-08-25 08:40:48 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.426
  …
2026-08-25 15:09:00 [INFO] SIGNAL: [MetaGate] action=reduce meta_conf=47.3% size_mult=0.70 reason=meta_reduce
2026-08-25 15:10:09 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-25 15:40:17 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-25 15:40:17 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-25 age=26m extreme=584 refresh=37 grade_x=134 cb3=0
2026-08-25 15:40:17 [INFO] SIGNAL: [ModelHealth] date=2026-08-25 앙상블유효가동률=77.8% | 파이프라인 370분 | ConstOut 4회/7분 {"3m": {"events": 2, "minutes": 4}, "5m": {"events": 2, "minutes": 3}} | WeightCollapse 75분 | 장중재학습 4회 | CB③ ready 110분/370분 (30%) (리셋 2회, 표본손실 60건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1140 | 09:00:02 | 14:44:01 | 1m 'macro_vix' scale=0.0144 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 186 | 08:45:17 | 11:40:01 | 1m CORE 'ofi_norm' raw_std≈0(0.0231) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 168 | 09:00:00 | 14:49:00 | 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 167 | 09:00:00 | 14:49:00 | ts=08:59 horizon=1m age=1m max_z=+17.78(cancel_add_ratio) extreme=4 |
| `Checklist` | 143 | 09:06:00 | 15:09:00 | 신뢰도 미달 34.9% < 39.6% → 강제 X등급 |
| `WeightCollapse` | 76 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 4 | 09:44:00 | 14:09:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4420 (conf_floor=0.330, min_conf=0.442, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5043

**컴포넌트 상위 15** — `ScalerFloor`×1206, `SIGNAL`×740, `MetaGate`×407, `Ensemble`×375, `FQAdj`×367, `ZeroDiag`×351, `ScalerRefresh`×229, `Model`×198, `Checklist`×174, `ScalerMonitor`×168, `ATR-Horizon`×139, `InstabilityGate`×131, `MicroRegime`×109, `차단`×82, `ToxicityGate`×81

### `logs/20260825_LEARNING.log` — 291.4KB · 2863행 · 최종 15:40:17

- 형식 평문 · 시각 인식 2863행 · WARNING=153, INFO=2710

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 08:41:27 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00052 auc=0.500 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-25 08:41:29 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00022 auc=0.538 out_max=0.2942 (n=85) → 보정 재적용
2026-08-25 08:41:29 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2942 < conf_floor=0.3300 (span=0.00022 auc=0.538 out_max=0.2942, 기저율=0.2941 n=85) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-08-25 15:40:17 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-25 15:40:17 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-25 15:40:17 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-25 15:40:17 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-25 15:40:17 [INFO] LEARNING: [Sigma] EOD sigma_20=0.09624% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 149 | 08:41:29 | 14:17:00 | 축퇴 감지 — span=0.00031 auc=0.443 out_max=0.3626 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 2 | 11:43:00 | 12:53:00 | total=712ms raw_fetch=5ms pred_select=2ms pred_update=1ms pred_insert=0ms verified=2 |
| `Consolidator` | 1 | 15:40:17 | 15:40:17 | 구간 'OPEN_VOLATILE' 최근 4일 풀링(n=272) 기대손익 -0.591pt (CI상단 -0.156pt) < 0 → 패널티 +0.04 (참고 정확도 30.9%) |
| `DriftAdjuster` | 1 | 15:40:17 | 15:40:17 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 3일) |

**채널** — `LEARNING`×2863

**컴포넌트 상위 15** — `LEARNING`×1209, `SGD`×369, `sigma`×357, `Calibration`×292, `Bias⚠`×245, `Bias`×128, `MetaConf`×78, `OnlineLearner`×77, `ScalerWarmup`×43, `BiasReset`×16, `SHAP`×12, `GBM-64`×8, `GBM`×8, `RF`×5, `ExtremityCorrector`×5

### `logs/20260825_HEALTH.log` — 4.0KB · 30행 · 최종 14:35:00

- 형식 평문 · 시각 인식 30행 · WARNING=15, INFO=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0
2026-08-25 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=521ms | quality=0.86 | cache_age=68s | exceptions_10m=0
2026-08-25 09:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=333ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-08-25 09:10:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=440ms | quality=1.00 | cache_age=56s | exceptions_10m=0
2026-08-25 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 384ms (표본 20분)
  …
2026-08-25 13:46:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=283ms | quality=1.00 | cache_age=59s | exceptions_10m=1
2026-08-25 14:11:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2897ms | quality=1.00 | cache_age=91s | exceptions_10m=1
2026-08-25 14:12:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=513ms | quality=1.00 | cache_age=148s | exceptions_10m=1
2026-08-25 14:34:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=342ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-25 14:35:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=322ms | quality=1.00 | cache_age=57s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 15 | 09:00:01 | 14:34:00 | level=WARNING degraded=OFF | latency=1683ms | quality=0.86 | cache_age=9s | exceptions_10m=0 |

**채널** — `HEALTH`×30

**컴포넌트 상위 15** — `Health`×29, `HealthTrend`×1

### `logs/retrain_eod_20260825.log` — 19.3KB · 130행 · 최종 15:48:39

- 형식 평문 · 시각 인식 130행 · WARNING=11, INFO=119

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-25 15:45:04,177 [INFO] EOD_RETRAIN: =======================================================
2026-08-25 15:45:04,177 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-25 15:45:04,177 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-25 15:45:04,177 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-25 15:45:04,177 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-25 15:48:39,639 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0493 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-25 15:48:39,639 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0673 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-25 15:48:39,639 [INFO] SIGNAL: [ScalerRefresh] ts=15:48 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.06s
2026-08-25 15:48:39,639 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.06s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-25 15:48:39,639 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:56 | 15:47:31 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-08-24 14:38:00 ≥ 홀드아웃 시작=2026-08-18 11:20:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-24 14:38 >= holdout_start=2026-08-18 11:20 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-24 … |
| `GuardGhost` | 4 | 15:46:07 | 15:46:19 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-25 11:45:00까지)인데 acc.txt=0.4054는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `WaitDC` | 1 | 15:45:04 | 15:45:04 | 마감 프로세스 정체 감지 — started 마커 있음 · SYSTEM.log 최종 기록 272s 전(임계 180s) · done 마커 없음. 20분을 기다리지 않고 즉시 진행한다 (490차 F-N) |

**채널** — `LEARNING`×65, `SIGNAL`×37, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×30, `Retrain`×20, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `GuardGhost`×4, `RegimeFingerprint`×3, `WaitDC`×2, `P8`×2

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

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) | 1 |
| 체결(`[체결진입]`) | 3 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 82 |
| 사이저 호출(`[Sizer]`) | 4 |

### 포지션 1건 · 승 1 (100%) · 합계 +1.20pt (+56,872원)  ※ 레그 2행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|
| 12:32:00 | LONG | 2 | 3m | 2 | +1.20 | +56,872 | 하드스톱(틱) |

**청산 레그 2행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 12:33:12 | 부분 | 1 | +0.93 | +44,936 | TP1 부분청산 33% |
| 12:33:26 | 전량 | 1 | +0.27 | +11,936 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×1, `하드스톱(틱)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/1건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +32,764 = 포지션합 +56,872 → **불일치 ⚠** · `[청산 완료]` 2건 = 조립 포지션 1건 → **불일치 ⚠** · **귀속 실패 레그 2행 ⚠**(진입 로그 없는 이월 포지션 가능)

### CB③ 판정 가능 시간 — **110분 / 370분 (30%)**

acc30m 버퍼 리셋 2회 · 그때 버린 표본 60건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 1건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 12:32:00 | LONG | 2 | 1042.34 | 3m | mean-revert |

계약수 분포 — 2계약×1

등급 분포 — `A급(원시C)`×1, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×2, `chas`×2, `ofi`×1, `time`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×4

실제 진입 계약수 — **2계약**×1

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×4

### 차단 사유 82건 · 18종

| 건수 | 사유 |
|---|---|
| 54 | 등급X — 미통과 항목: 2_confidence |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 등급X — 미통과 항목: 3_vwap |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 10_chase |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | JointGateBlock — meta=0.53 tox=0.70 joint=0.374 < 0.50 |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi |
| 1 | 등급X — 미통과 항목: 3_vwap, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar, 10_chase |
| 1 | 청산 후 쿨다운 — 121초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 61초 후 재진입 가능 |
| 1 | JointGateBlock — meta=0.69 tox=0.70 joint=0.486 < 0.50 |
| 1 | 청산 후 쿨다운 — 85초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 24초 후 재진입 가능 |
| 1 | Reverse Clamp (P3-b) — 청산 후 역방향(LONG→SHORT) 25s 이내 진입 금지 |

**체크리스트 미통과 항목 누적** — `2_confidence`×54, `3_vwap`×15, `4_cvd`×8, `7_prev_bar`×7, `5_ofi`×5, `10_chase`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 3건

- `일간 리셋 완료` ×2
- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 28건 · 최대 21781ms · 5초 초과 7건

상위 — 21781ms, 8625ms, 7297ms, 5890ms, 5437ms, 5234ms, 5093ms, 4687ms

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
| 13:14:21 | 21781ms | 361ms | **21420ms (98%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260825_WARN.log`
```
--- ConstOut ×4(표본)
09:44:00 2026-08-25 09:44:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:15:01 2026-08-25 12:15:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
13:10:00 2026-08-25 13:10:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
14:09:01 2026-08-25 14:09:01 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×1(표본)
??:??:?? Traceback (most recent call last):
--- [CB] ×1(표본)
11:25:01 2026-08-25 11:25:01 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×4(표본)
11:25:01 2026-08-25 11:25:01 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 3분 재진입 금지 (until 11:28:01)
11:25:01 2026-08-25 11:25:01 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 3분 재진입 금지 (until 11:28:01)
12:33:26 2026-08-25 12:33:26 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 12:35:26)
12:33:26 2026-08-25 12:33:26 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 12:35:26)
--- [SHAP] 슬로우 ×3(표본)
12:30:01 2026-08-25 12:30:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 906ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:15:01 2026-08-25 13:15:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 969ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
14:02:01 2026-08-25 14:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 975ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
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
--- [CB] ×2(표본)
15:40:17 2026-08-25 15:40:17 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:17 2026-08-25 15:40:17 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:16 2026-08-25 15:11:16 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×1(표본)
15:40:32 2026-08-25 15:40:32 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×3(표본)
15:40:17 2026-08-25 15:40:17 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:32 2026-08-25 15:40:32 [INFO] SYSTEM: [System] 자동 종료 실행
15:40:32 2026-08-25 15:40:32 [INFO] SYSTEM: 미륵이 자동 종료
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
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:17 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260825_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:46 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 14 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 16 | 08:55:17 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 2 | 09:54:00 [WARNING] 5분 누적 수익률 +0.507% (임계 ±0.393%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 2 | 11:58:05 [WARNING] _tick_header 간격 5234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5234 band=… |
| 14:00 | 장중 후반 · 장중 재학습 | 2 | 14:02:00 [WARNING] 5분 누적 수익률 +0.372% (임계 ±0.297%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:40:17 [ERROR] 예외 발생 — 강제 종료 예약: unsupported format character ',' (0x2c) at index 62 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260825_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 87 | 08:40:54 [INFO] 활성화 | file=logs\crash_fault.log PID=5080 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 127 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 190 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 184 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 170 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 179 | 13:54:00 [INFO] #102500 code=A0569 raw_time=135400 parsed=13:54:00 price=1046.32 vol=1 bid1=1046.24 ask1=1046.34 flag=50 side… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 145 | 15:04:01 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 130 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 27 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260825_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:17 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0231) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 183 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0235) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 268 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0258) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 209 | 09:54:00 [WARNING] ts=09:53 horizon=1m age=10m max_z=+4.35(cancel_add_ratio) extreme=1 |
| 12:00 | 장중 중간점 | 159 | 11:58:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 150 | 13:56:00 [WARNING] 신뢰도 미달 35.0% < 39.9% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 46 | 15:04:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:17 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

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
| **오늘 20260825** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [1-9 후속] 480차 G-3 보류 근거가 실측으로 반증됐다 — 재판정 필요
### [1-10] (P1) 앙상블 미산출 5분이 `conf=0.0%`로 표기됐다 — 계측 4원칙 ② 위반 (장전 O-5 판정)
### [1-11] (P1) 수집기 §5가 오늘 유일한 포지션을 `0건 · +0원`으로 집계했다 — 1-9와 같은 뿌리
### 장전 이월 항목 처분 (요약)
### 장중 신규 관측 (장후가 닫는다)
### 장중 정상 확인 (이상 없음 — 근거 보존)
### 이 점검이 남긴 교훈
### [493차 후속2 · 절차 기록] 같은 시각에 두 절이 병행 작성됐다 — 「하루 한 파일 append」의 경합
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 다 섀도라 미적용이 정상**(이상점 아님). ⚠ 표본 1건으로 승격 판단 금지(313차).
- **O-9** `phantom_stop_shadow` 11:25:01 행에서 `stop_updated_at` NULL · `would_suppress`
  참 여부 확인(장중 DB 금지로 미뤘다). 참이면 1-9 진단이 DB로 확증된다.

### 장중 정상 확인 (이상 없음 — 근거 보존)

- 프로세스 생존: 12:31:24 하트비트 `beat_age_sec=2.4 watching=true strikes=0 fired=false`
  (08-19 동결과 다르다 — 그때는 프로세스만 살아 있었다)
- 매분 루프 공백: 08:55~12:26 **10분 이상 공백 0건**, 경과분 207/207 = 100%.
  ⚠ 다이제스트 §7의 `커버리지 55.8%` · `종료시각 델타 -194분`은 **장중이라 당연**하며
  이 값으로 이상 판정을 내리면 안 된다(장후가 판정)
- STEP 3: 이벤트 구동 2회. ⚠ "30분마다 12회"로 읽지 말 것(483차 문서정정)
- `[WeightCollapse]` 42/207분 = **20.3%** — CLAUDE.md 기재 21~22%와 일치, 어제 43건과 동수준
- 차단 48건/14종, 최다 `2_confidence` 28건(58%) — **단일 게이트 압도적 편중 없음**
  (316차 HurstGate 63% 패턴 아님)
- `[SizerMatch] sizer=3계약 → actual=2계약 (gap=1) | binding=hurst(0.50) |
  kelly=0.60 meta=0.65 tox=1.00 exec=1.00` — 471차 후속6 `sizing_trace`가 **묶는 게이트를
  하나로 특정**했다. 검증 캠페인 [28] `sizing_inversion_watch`에 표본 1건 적립
- CB⑤ 경고 10건 전부 경고(정지 0건). 개장 첫 분 `[장시작버스트→임계9s]`는 설계된 완화
- PSI 0.033~0.038(평온) · `OPT10080` 0건 · ERROR 0건(⚠ 이 P0은 INFO 채널에서만 보인다)
- ⚠ **conf 절대값을 CLAUDE.md 「확률 판단 기준」 표에 대지 않았다**(2026-07-31
  `CONF_SCALE_BREAKS`). 오늘 `min_conf` 0.396~0.620 범위 대비 **상대 위치로 판정**했다

### 이 점검이 남긴 교훈

**423차·424차·480차·493차가 같은 결함의 네 번째 얼굴이다.**
*"진입/조이기 사실을 기록하는 지점이 여러 곳인데, 새 경로가 생길 때마다 한 곳이
빠지고, 빠졌다는 사실이 로그에 안 남는다."*
480차가 F-5②에서 **바로 이 함수의 FLAT 분기를 "레이스 경로의 유일한 세팅 지점"으로
지목하고 3개 필드를 심으면서도** `stop_updated_at`을 빠뜨린 것이 결정적이다 —
**필드를 하나씩 세는 방식으로는 다음 누락을 막을 수 없다.**
⇒ F-V ②의 `entry_time` 가드(고도화 ①의 `entry_bar_start` 명시 필드)가 근본 해법인
이유가 이것이다. **"스톱이 조여졌는가"(간접)가 아니라 "포지션이 이 봉보다 나중에
열렸는가"(직접)를 묻는 편이, 앞으로 생길 진입 경로에도 자동으로 적용된다.**
그리고 AST 불변식 테스트가 **새 경로 추가 시 깨지도록** 고정한다.

### [493차 후속2 · 절차 기록] 같은 시각에 두 절이 병행 작성됐다 — 「하루 한 파일 append」의 경합

**사실** — 이 장중 점검(제2부)을 쓰는 동안 같은 파일에 **제1부-E**(12:35, GUARD 결함의
근본 원인 확정 — H2 철회·H1 확정)가 병행 append 됐다. 제2부는 파일 끝에 붙었으므로
**순서는 시간순으로 맞다**. 다만 제2부의 이월 처리 표가 제1부-D 시점 상태(H2 확정 ·
8′ 미이행)로 먼저 쓰였고, 확인 후 **제2부 안에서 정정**했다(제1부-E 본문은 손대지 않았다).

**정정한 것**
- 이월 표 `1-8` 행 → *"제1부-E의 판정이 이 표보다 우선한다 — H1 확정"*
- 이월 표 `8′` 행 → ⏭미이행 → **✅완료**, `fuoption` = 메시아
- 「이미 등록된 항목」 표의 `F-U(+5′·8·9)` → **`F-U 개정(0·1~7·10)`**
- 사용자 조치 번호 **10~13 → 11~14**(제1부-E가 10번을 이미 썼다) · 절 제목에 범위 병기
- §0-B에 두 조사가 병행됐다는 안내 한 문단

**교훈 (점검 규약 후보)** — 대원칙 B는 *"뒤 국면이 앞 절 항목을 전부 처분한 뒤 시작한다"*
고 규정하는데, **같은 국면·같은 시각에 두 절이 붙는 경우**를 상정하지 않았다.
⇒ **append 직전에 파일 끝을 다시 읽고, 읽은 시점과 쓰는 시점 사이에 새 절이 생겼으면
자기 절 안에서 정정한다.** 사용자 조치 번호도 같은 이유로 **append 직전에 최댓값을
다시 확인**해야 한다. `references/postmortem.md`에 반영 후보.

```

</details>

### dev_memory/NEXT_TODO.md — 1.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 493차에 종결된 항목
## MW0601 493차 후속 (2026-08-25 12:01) — 사용자 정정에 따른 GUARD 재조사
## MW0601 493차 후속2 (2026-08-25 12:35) — GUARD 근본원인 확정
## MW0601 493차 후속2 (2026-08-25 12:35) — 장중 점검 fix/관측
### 장후 적용 (오늘, 사용자 지시 시)
### 주간회의 안건 (오늘 착수하지 않는다)
### 493차 후속2 관측 항목 (오늘 장후가 닫는다)
### 커밋 대기 (오늘 커밋하지 않았다)
```

미완료 체크박스 **1935건** (끝에서 30건)
```
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
- [ ] **F-U-0 (즉효, 장후)** — 4곳의 `!=` 를 **`not (p.pid == os.getpid())`** 로 치환.
- [ ] **F-U-1 (근본, 장후)** — 프로브를 `scripts/guard_single_instance.py`로 분리해
- [ ] **F-U-10 (신설, 장후) 회귀 테스트 `tests/test_493_bat_python_oneliner_bang.py`** —
- [ ] **F-U-8 우선순위 하향** — 32/64비트 사각지대는 12:25 실측 `판독불가` **0개**로
- [ ] **(사용자) `scripts\diag_guard_delayedexp.bat` 1회 실행** — [A] SyntaxError /
- [ ] **🔴 단일 인스턴스 불변식이 배포 이래 미보장이었다는 사실을 CLAUDE.md 실전 전환
- [ ] **(점검 규약 · 신규) 판별 시험은 「고장 난 그 환경」에서 재현할 것** —
- [ ] **F-V 유령 하드스톱 가드를 진입 경로 전부에서 켠다 (P0, 오늘 최우선)** —
- [ ] **F-V 검증 3종 (F-V와 같은 커밋)** —
- [ ] **F-X 수집기 포지션 조립 확장 (P1, 라이브 무관 — 언제든 가능)** —
- [ ] **F-W 앙상블 미산출을 「값 없음」으로 표기 (P1, F-V 다음)** —
- [ ] **⚠ G-3 손익 판정 재계산 — 480차 보류 근거가 493차 실측으로 반증됐다** —
- [ ] **(설계) 「진입 직후 유예(entry grace)」를 명시 규칙으로 승격** —
- [ ] **O-7 CB③ acc30m** — 오늘 최저 6.7%(10:54) → 11:49 NORMAL(36.7%) → **12:16 버퍼 리셋
- [ ] **O-8 섀도 게이트 2종 동시 발화** — 11:25 진입에 `[ChaseForeignComboGuard] … A → C
- [ ] **O-9 `phantom_stop_shadow` 11:25:01 행** — `stop_updated_at` NULL · `would_suppress`
- [ ] **O-3 승계** — `logs/retrain_intraday_20260825_15*.log` 존재 여부.
- [ ] **장후 손익 집계 수동 보정 필수** — F-X 미적용 상태에서 다이제스트 §5는
- [ ] **(점검 규약 · 신규) 하루 한 파일 append의 동시성 규약** — 같은 국면·같은 시각에
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
[Ensemble]` 미산출(`[S6Detail] ensemble=0ms`)이
      `conf=0.0%` → `[ZeroDiag] conf미달(0.000<mc0.442)`로 흘렀다. 계측 4원칙 ②

### 주간회의 안건 (오늘 착수하지 않는다)

- [ ] **⚠ G-3 손익 판정 재계산 — 480차 보류 근거가 493차 실측으로 반증됐다** —
      480차(`DECISION_LOG.md:991`)의 *"편익의 대부분(파라미터 유실)은 F-5①②가 이미 걷는다"*
      가 무너졌다. 오늘 F-5② 5종은 **정상 승계**됐고(`[PositionFallback]` 0건, 480차 O-4
      기대값 충족) **그런데도 유령 하드스톱이 났다** — `stop_updated_at`이 그 5종에 없다.
      ⇒ **F-5①②가 걷지 못하는 여섯 번째 결과.**
      ⚠ **판정 ≠ 결정** — 근거만 갱신한다. 480차의 다른 근거(*"진입 경로 리팩터링 =
      라이브 위험"*)는 유효하고, F-V ①은 리팩터링이 아니라 한 줄 복원이라 별개다

- [ ] **(설계) 「진입 직후 유예(entry grace)」를 명시 규칙으로 승격** —
      `Position.entry_bar_start` 명시 필드 신설 → 봉중 판정 함수가 **그 필드 하나만** 본다
      (`bar_start <= entry_bar_start` → 부적격). `stop_updated_at`은 트레일링·TP1 조이기
      전용으로 남긴다. **두 관심사를 한 필드에 얹은 것이 1-9의 구조적 원인이다.**
      ⚠ 섀도 병기 10거래일 후 교체

### 493차 후속2 관측 항목 (오늘 장후가 닫는다)

- [ ] **O-7 CB③ acc30m** — 오늘 최저 6.7%(10:54) → 11:49 NORMAL(36.7%) → **12:16 버퍼 리셋
      (버린 표본 30건)**. 장후 EOD `cb3_availability` 스냅샷에서 **`would_halt` 참이었던
      분수**와 **그 창의 포지션 손익**. 490차 F-G 첫 실전 표본.
      ⚠ **HALT 미발동은 결함이 아니다**(296차 영구 비활성, `safety/circuit_breaker.py:445`)
- [ ] **O-8 섀도 게이트 2종 동시 발화** — 11:25 진입에 `[ChaseForeignComboGuard] … A → C
      강등 후보 (미적용)` · `[RegimeExhaustionGate] … hurst=0.376 ext60m=+8.82ATR (미적용)`.
      **둘 다 섀도라 미적용이 정상.** 당일 발화 횟수 + 실적용이었다면 오늘 유일 진입이
      막혔겠는가. ⚠ **표본 1건으로 승격 판단 금지**(313차)
- [ ] **O-9 `phantom_stop_shadow` 11:25:01 행** — `stop_updated_at` NULL · `would_suppress`
      참 여부. 참이면 1-9 진단이 DB로 확증된다(장중 DB 금지로 미룬 항목)
- [ ] **O-3 승계** — `logs/retrain_intraday_20260825_15*.log` 존재 여부.
      현재까지 09:45(21.9s) · 12:16(22.5s) 2건, 둘 다 `[ConstOut] ['3m']` 후속, 15:10 걸침 없음
- [ ] **장후 손익 집계 수동 보정 필수** — F-X 미적용 상태에서 다이제스트 §5는
      `0건 · +0원`을 낸다. **실제는 1포지션(2계약) -24,108원**(레그 2행: -9,554 / -14,554).
      ⚠ 포지션 단위/청산 레그 단위 병기할 것(계측 4원칙 ①)

### 커밋 대기 (오늘 커밋하지 않았다)

- `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` (제2부 append)
- `docs/정기점검/매일점검/evidence_MW0601-20260825_intra.md` (신규)
- `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md` (append)
- `scripts/diag_guard_processes.py` (제1부-D에서 신설, 미실행)

- [ ] **(점검 규약 · 신규) 하루 한 파일 append의 동시성 규약** — 같은 국면·같은 시각에
      두 절이 병행 append 되는 경우가 실제로 발생했다(2026-08-25 12:35, 제1부-E ↔ 제2부).
      ⇒ ① **append 직전에 파일 끝을 다시 읽는다** ② 읽은 시점 이후 새 절이 생겼으면
      **자기 절 안에서 정정**한다(앞 절은 손대지 않는다) ③ **사용자 조치 번호는 append
      직전에 최댓값을 재확인**한다. 대원칙 B는 국면 간 순서만 규정하고 이 경우를
      상정하지 않았다. `references/phases.md`·`references/postmortem.md`에 반영

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

### `data/heartbeat_MW0601_20260825.json` — 243B · 08-25 15:40:29
```json
{
 "pid": 5080,
 "written_at": "2026-08-25T15:40:29",
 "beat_epoch": 1787640026.2589343,
 "beat_age_sec": 2.9,
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

### `docs/정기점검/매일점검` — 71개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` | 161.7KB | 08-25 12:46 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_intra.md` | 61.7KB | 08-25 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_pre.md` | 51.5KB | 08-25 09:00 |
| `docs/정기점검/매일점검/MW0601-20260824-점검리포트.md` | 191.2KB | 08-24 16:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_post.md` | 70.6KB | 08-24 16:21 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_intra.md` | 65.2KB | 08-24 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_pre.md` | 47.4KB | 08-24 08:59 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.0KB | 08-23 16:51 |

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

1. `.git/index.lock` **스테일 잔존** (0바이트 · 7.1시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. `logs/20260825_WARN.log`: ERROR 이상 3건
3. `logs/20260825_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
4. 완료 마커 **`daily_close_done`** 없음 — 15:40 일일 마감 완료 마커
5. 완료 마커 **`strategy_report`** 없음 — 일일 전략 리포트
6. 포지션 1건 중 최종청산이 하드스톱·손절 계열 **1건(100%)** — 손절 준수율 확인 필요 (레그 2행)
7. 다레그 포지션 **1건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
8. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
9. 메인 스레드 정지 5초 초과 **7건** (최대 21781ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
10. `logs/20260825_WARN.log`: **ConstOut** 4건(표본)
11. `logs/20260825_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20260825_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20260825_SIGNAL.log`: **ConstOut** 8건(표본)
14. `logs/20260825_LEARNING.log`: **축퇴** 8건(표본)
15. 미커밋 변경 504건 (실질 2건 · 코드 0건 · EOL 파생 497건)
16. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260825*.log` (Windows) / `grep 강제청산 logs/*20260825*.log`*