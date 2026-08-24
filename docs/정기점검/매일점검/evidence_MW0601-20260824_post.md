# 미륵이 증거 다이제스트 — 2026-08-24 / POST

- 생성 2026-08-24 16:21:39 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/vigilant-busy-clarke/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260824` · `2026-08-24` · `260824` · `0824`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **23개** 파일 · 23개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260824.txt` | 181B | 08-24 16:08 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260824.log` | 445B | 08-24 15:12 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260824.json` | 244B | 08-24 15:40 |
| `launcher_{DATE}_084001_24123.log` | 1 | `logs/Mireuk_batch/launcher_20260824_084001_24123.log` | 1.7MB | 08-24 15:33 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260824.log` | 25.2KB | 08-24 16:08 |
| `retrain_intraday_{DATE}_093601.log` | 1 | `logs/retrain_intraday_20260824_093601.log` | 2.4KB | 08-24 09:36 |
| `retrain_intraday_{DATE}_103000.log` | 1 | `logs/retrain_intraday_20260824_103000.log` | 2.4KB | 08-24 10:30 |
| `retrain_intraday_{DATE}_112502.log` | 1 | `logs/retrain_intraday_20260824_112502.log` | 2.4KB | 08-24 11:25 |
| `retrain_intraday_{DATE}_124200.log` | 1 | `logs/retrain_intraday_20260824_124200.log` | 2.4KB | 08-24 12:42 |
| `retrain_intraday_{DATE}_134200.log` | 1 | `logs/retrain_intraday_20260824_134200.log` | 2.4KB | 08-24 13:42 |
| `retrain_intraday_{DATE}_143000.log` | 1 | `logs/retrain_intraday_20260824_143000.log` | 2.4KB | 08-24 14:30 |
| `retrain_intraday_{DATE}_150900.log` | 1 | `logs/retrain_intraday_20260824_150900.log` | 2.4KB | 08-24 15:09 |
| `{DATE}_DATA.log` | 1 | `logs/20260824_DATA.log` | 345.7KB | 08-24 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260824_DEBUG.log` | 242.2KB | 08-24 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260824_HEALTH.log` | 4.5KB | 08-24 14:49 |
| `{DATE}_HOGA.log` | 1 | `logs/20260824_HOGA.log` | 51.6MB | 08-24 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260824_LEARNING.log` | 274.9KB | 08-24 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260824_MICRO.log` | 1.0MB | 08-24 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260824_PROBE.log` | 96.6KB | 08-24 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260824_SIGNAL.log` | 594.0KB | 08-24 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260824_SYSTEM.log` | 868.3KB | 08-24 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260824_TRADE.log` | 30.2KB | 08-24 14:30 |
| `{DATE}_WARN.log` | 1 | `logs/20260824_WARN.log` | 133.4KB | 08-24 15:08 |

## 2. 코드·커밋 상태

- HEAD `4dbdf80` · 브랜치 `v9-dev` · 미커밋 491건 · 인덱스락 없음
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
… 외 451건
```

**당일(2026-08-24) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
4dbdf80 [MW0601] 489차: 주간회의 승인 6건 — ⑨ WFA 이관 · [46]③ 재등록+배선 · 좀비결정 7건 분류 · [8]② 계측 이식
10178cb [MW0601] 489차 A-1: CB② 카운트를 절대원칙 문구에 맞춘다 — 시간창 + 포지션 단위 (한도 무변경)
9acc983 [MW0601] 488차 후속: 라이브 데이터에 고정된 캠페인 테스트 4개 재설계 — FAIL 12건 해소
7e82dcd [MW0601] 488차: [35] 유령 하드스톱 — 439차 "모집단 소멸" 서술 MW0601 비적용 + drop-max 계측
7451a64 [MW0601] dev_memory: MW0601_이관_점검사항 7건 조사 결과 기록
f628b83 [MW0601] 멀티PC 정책 폐기 후속: 운영 문서 3건에 남은 상호조율 관행 정리
302c8b5 [MW0601] 487차 후속 cherry-pick 조정: ConstOut 채널 번호 [51] 유지 (F-9 재배정 미적용)
1c4c6d1 [MW0602] 487차 후속: F-8(B)+F-9 구현 — 채널 [50]/[54] 브랜치 미가용 표기(감지형) + ConstOut [51]→[54] 재배정
ed8b919 [MW0602] 487차: 멀티PC 정책 폐기(사용자 결정) — F-8 MW0602 한정 권고(B 확정·A 폐기) + MW0601 이관 점검사항 분리
dfe97e8 [MW0601] docs/Ref: entry_band_watch.py 설명서 신설 — 라우팅 밴드 감시 채널
b2f02db [MW0601] 483차 후속5: 진입 호라이즌 경계 동결 — 5주 경보에 대한 명시적 결정 3건
9fab78f [MW0601] 483차 후속4: 캠페인 스텝이 인쇄 때문에 죽지 않게 한다 — P2-H
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

_본문 미열람(설정): `20260824_HOGA.log` 51.6MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/eod_retrain_done_20260824.txt`** — 181B · 08-24 16:08:14
```
completed: 2026-08-24 16:08:14
rows: 40386
cols: 97
horizons_replaced: 6/6
t_load_s: 30.9
t_retrain_s: 160.4
t_total_s: 191.6
daily_close_seen: false
wait_dc_timeout: true
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260824_124200.log`, `retrain_intraday_20260824_134200.log`, `retrain_intraday_20260824_143000.log`, `retrain_intraday_20260824_150900.log`, `retrain_intraday_20260824_103000.log`, `retrain_intraday_20260824_112502.log`, `20260824_MICRO.log`, `20260824_DATA.log`_

### `logs/20260824_TRADE.log` — 30.2KB · 227행 · 최종 14:30:16

- 형식 평문 · 시각 인식 227행 · INFO=227

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:12 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-24 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-24 09:30:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,955,870) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-24 09:32:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,955,870) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-24 09:33:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,955,870) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-24 14:30:15 [INFO] TRADE: [주문요청] 하드스톱(틱) 청산 SHORT 1계약 @ 1056.25 체결대기
2026-08-24 14:30:15 [INFO] TRADE: [Chejan] 상태=접수 주문번호=3333 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-24 14:30:16 [INFO] TRADE: [Chejan] 상태=체결 주문번호=3333 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-24 14:30:16 [INFO] TRADE: [Position] 체결청산 SHORT @ 1056.32 | PnL=+0.22pt (+9,415원) | 하드스톱(틱)
2026-08-24 14:30:16 [INFO] TRADE: [청산 완료] PnL=+0.22pt (+9,415원)
```

</details>

**채널** — `TRADE`×227

**컴포넌트 상위 15** — `Chejan`×55, `Position`×44, `Sizer`×30, `주문요청`×23, `JointGateBlock 차단`×14, `진입체크`×10, `체결진입`×10, `TickStop-S0C`×10, `청산 완료`×10, `TickTP1`×8, `체결진입보정`×6, `손절1차 분할체결`×2, `손절1차 조기축소`×2, `ProfitGuard`×1, `TP1 부분청산`×1

### `logs/20260824_WARN.log` — 133.4KB · 567행 · 최종 15:08:00

- 형식 평문 · 시각 인식 567행 · ERROR=1, WARNING=566

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 32ms
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-24 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2859ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2859 band=INFO since_pipe_s=NA
2026-08-24 08:41:26 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3375ms — live 중단 원인 분석용
  …
2026-08-24 15:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.0
2026-08-24 15:02:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.227% (임계 ±0.205%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-24 15:03:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 955ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-08-24 15:03:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4453ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4453 band=INFO since_pipe_s=0.0
2026-08-24 15:08:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| ERROR | `LiveDBG` | 1 | 11:16:22 | 11:16:22 | _tick_header 간격 20985ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=20985 band=ALERT since_pipe_s=0.1 |

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-08-24 11:16:22 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 20985ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=20985 band=ALERT since_pipe_s=0.1
```

</details>

**WARNING — 태그 33종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 150 | 08:41:20 | 15:03:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 55 | 09:44:01 | 14:30:16 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='907' | pending='ENTRY:SHORT qty=3 filled=0 order_no=? reason=진입 req_at=09:44:01.013' | positio… |
| `ChejanMatch` | 55 | 09:44:01 | 14:30:16 | order_no='907' | pending='ENTRY:SHORT qty=3 filled=0 order_no=907 reason=진입 req_at=09:44:01.013' | pending_matched=True |
| `PendingOrder` | 46 | 09:44:01 | 14:30:16 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1077.32, 'reason': '진입', 'hint_source': '', 'atr': 2.9657, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `ExitCooldown` | 20 | 09:48:11 | 14:30:16 | 하드스톱(틱) 후 2분 재진입 금지 (until 09:50:11) |
| `PipePerf` | 16 | 09:00:02 | 14:31:02 | total=2549ms | S0=3ms S1=14ms S2=0ms S3=0ms S4=160ms S5=2017ms S6=303ms S7=45ms S8=6ms |
| `Health` | 16 | 09:00:02 | 14:48:00 | level=WARNING degraded=OFF | latency=2549ms | quality=0.86 | cache_age=35s | exceptions_10m=0 |
| `CB⑤` | 16 | 09:00:02 | 14:31:02 | 파이프라인 2549ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 16 | 09:05:00 | 15:02:00 | 5분 누적 수익률 -1.393% (임계 ±0.500%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `EntryFillFlow` | 16 | 09:44:01 | 14:30:01 | actual_side='SHORT' | after='SHORT 3계약 @ 1077.36' | applied_side='SHORT' | before='SHORT 3계약 @ 1077.32' | fill_no='' | fill_price=1077.36 | fill_qty=1 | order_no='907' | pending='ENTRY:SHORT qty=3 filled=1 order_no=907 reason=진입 req_at=09:… |
| `ChartDBG` | 15 | 14:12:56 | 14:13:56 | paintEvent slow 47.0ms | size=1756x917 candles=20 grid=16.0 spans=0.0 candles=16.0 dir=0.0 regime=0.0 markers=15.0 axes=0.0 cross=0.0 | slow_cnt=1 total_cnt=1 |
| `ExitSendOrderResult` | 12 | 09:48:11 | 14:30:15 | ret=0 kind=하드스톱(틱) direction=SHORT qty=2 |

**채널** — `SYSTEM`×551, `HEALTH`×16

**컴포넌트 상위 15** — `LiveDBG`×151, `ChejanFlow`×55, `ChejanMatch`×55, `PendingOrder`×46, `ExitCooldown`×20, `PipePerf`×16, `Health`×16, `CB⑤`×16, `ScalerRefresh`×16, `EntryFillFlow`×16, `ChartDBG`×15, `ExitSendOrderResult`×12, `ExitFillFlow`×11, `EntryAttempt`×10, `EntrySendOrderResult`×10

### `logs/20260824_SYSTEM.log` — 868.3KB · 6121행 · 최종 15:40:22

- 형식 평문 · 시각 인식 6114행 · INFO=6114, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:40:48 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=25592 | 행감지=30s all_threads=True
2026-08-24 08:41:02 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-24 08:41:02 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-24 08:41:02 [INFO] SYSTEM: 미륵이 초기화
2026-08-24 08:41:02 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-21) 종가 버퍼 로드: 384봉
  …
2026-08-24 15:40:20 [INFO] SYSTEM: [FeatureBuilder] 전일 종가 버퍼 갱신: 384봉
2026-08-24 15:40:20 [INFO] SYSTEM: [Model] 재학습 완료 — 다음 파이프라인 시작 전 모델 교체 예약
2026-08-24 15:40:22 [INFO] SYSTEM: [DynMC] mc 재보정 완료 trigger=RETRAIN  base=0.422  (n=2099봉)
2026-08-24 15:40:22 [INFO] SYSTEM: [GBM] 재학습 이력 저장: 2026-08-24 15:09 (7회)
2026-08-24 15:40:22 [INFO] SYSTEM: [Notify] ℹ️ [15:40:22] [미륵이] GBM 배치 재학습 완료
```

</details>

**채널** — `SYSTEM`×6114

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1203, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `BalanceUI`×112, `CybosEvent`×110, `System`×97, `MicroRegime`×97, `CybosDailyPnl`×76, `BalanceRefresh`×75, `RegimeFingerprint`×67

### `logs/20260824_SIGNAL.log` — 594.0KB · 5220행 · 최종 15:40:22

- 형식 평문 · 시각 인식 5220행 · WARNING=2105, INFO=3115

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.419
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-08-24 15:09:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
2026-08-24 15:09:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=85.0% grade=X micro=횡보장
2026-08-24 15:09:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.850<mc0.970)
2026-08-24 15:10:14 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-24 15:40:22 [INFO] SIGNAL: [DynMC] mc 갱신 trigger=RETRAIN base=0.422  LUNCH_RECOVERY 0.413→0.418 | CLOSE_VOLATILE 0.421→0.426
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1380 | 09:00:03 | 15:08:00 | 1m 'macro_vix' scale=0.0190 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 240 | 08:45:20 | 15:08:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0118) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 154 | 09:00:00 | 14:26:01 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 119 | 09:00:00 | 14:27:01 | ts=08:59 horizon=1m age=1m max_z=+4.87(queue_refill_rate) extreme=2 |
| `Checklist` | 114 | 09:06:00 | 15:08:00 | 신뢰도 미달 34.9% < 38.9% → 강제 X등급 |
| `WeightCollapse` | 83 | 09:07:00 | 15:09:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 9 | 09:35:00 | 15:08:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 4 | 09:07:00 | 09:22:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 1 | 09:00:02 | 09:00:02 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `MetaGate` | 1 | 09:30:00 | 09:30:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×5220

**컴포넌트 상위 15** — `ScalerFloor`×1440, `SIGNAL`×740, `Ensemble`×379, `FQAdj`×367, `MetaGate`×347, `ZeroDiag`×319, `ScalerRefresh`×286, `Checklist`×202, `Model`×196, `ATR-Horizon`×157, `ScalerMonitor`×119, `InstabilityGate`×103, `MicroRegime`×97, `차단`×93, `WeightCollapse`×83

### `logs/20260824_LEARNING.log` — 274.9KB · 2740행 · 최종 15:40:22

- 형식 평문 · 시각 인식 2740행 · WARNING=129, INFO=2611

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:04 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00129 auc=0.498 out_max=0.5673 (기준 auc<0.53 and span<0.020, 기저율=0.5667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00055 auc=0.550 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00038 auc=0.529 out_max=0.3296 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
  …
2026-08-24 15:09:00 [INFO] LEARNING: [MetaConf] LR[횡보장] 비동기 결과 반영 (cnt=3816)
2026-08-24 15:09:00 [INFO] LEARNING: [SGD] 5건 학습 | SGD비중=30% 50분정확도=0.0%
2026-08-24 15:40:20 [INFO] LEARNING: [GBM-64] subprocess 완료 (returncode=0) → _on_gbm_retrain_done 호출
2026-08-24 15:40:22 [INFO] LEARNING: [DynMC] mc 변경 기록 trigger=RETRAIN base=0.422 zones=2개
2026-08-24 15:40:22 [INFO] LEARNING: [GBM] 배치 재학습 완료 | 20.8초 데이터=4800행
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 129 | 08:41:04 | 13:55:00 | 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×2740

**컴포넌트 상위 15** — `LEARNING`×1211, `SGD`×370, `sigma`×357, `Calibration`×249, `Bias⚠`×189, `Bias`×127, `MetaConf`×77, `ScalerWarmup`×46, `OnlineLearner`×46, `GBM-64`×14, `BiasReset`×13, `GBM`×13, `SHAP`×12, `RF`×7, `DynMC`×4

### `logs/20260824_HEALTH.log` — 4.5KB · 33행 · 최종 14:49:01

- 형식 평문 · 시각 인식 33행 · WARNING=16, INFO=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2549ms | quality=0.86 | cache_age=35s | exceptions_10m=0
2026-08-24 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=648ms | quality=0.86 | cache_age=94s | exceptions_10m=0
2026-08-24 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=305ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-24 09:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=277ms | quality=1.00 | cache_age=56s | exceptions_10m=0
2026-08-24 09:29:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 329ms (표본 20분)
  …
2026-08-24 14:30:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=798ms | quality=1.00 | cache_age=19s | exceptions_10m=3 [GBM재학습중→lat임계 5000/10000ms]
2026-08-24 14:31:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2582ms | quality=1.00 | cache_age=81s | exceptions_10m=5
2026-08-24 14:32:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=470ms | quality=1.00 | cache_age=139s | exceptions_10m=5
2026-08-24 14:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=298ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-24 14:49:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=436ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 16 | 09:00:02 | 14:48:00 | level=WARNING degraded=OFF | latency=2549ms | quality=0.86 | cache_age=35s | exceptions_10m=0 |

**채널** — `HEALTH`×33

**컴포넌트 상위 15** — `Health`×32, `HealthTrend`×1

### `logs/retrain_eod_20260824.log` — 25.2KB · 182행 · 최종 16:08:14

- 형식 평문 · 시각 인식 182행 · WARNING=17, INFO=165

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 15:45:02,483 [INFO] EOD_RETRAIN: =======================================================
2026-08-24 15:45:02,483 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-24 15:45:02,483 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-24 15:45:02,483 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-24 15:45:02,483 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-24 16:08:14,895 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0331 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-24 16:08:14,895 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1003 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-24 16:08:14,895 [INFO] SIGNAL: [ScalerRefresh] ts=16:08 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-08-24 16:08:14,895 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-24 16:08:14,895 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 4종 (상위 4)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 16:05:40 | 16:07:07 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-08-21 14:38:00 ≥ 홀드아웃 시작=2026-08-14 11:09:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-21 14:38 >= holdout_start=2026-08-14 11:09 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-21 … |
| `ScalerRefresh` | 6 | 16:08:14 | 16:08:14 | 1m CORE 'ofi_norm' raw_std≈0(0.0357) → identity(0,1) 강제 (FLAT 100% 방지) |
| `GuardGhost` | 4 | 16:05:49 | 16:05:59 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-24 14:38:00까지)인데 acc.txt=0.3997는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `WaitDC` | 1 | 16:05:02 | 16:05:02 | daily_close() 20분 대기 타임아웃 — pkl 경합 위험 있으나 강제 진행 |

**채널** — `LEARNING`×65, `EOD_RETRAIN`×60, `SIGNAL`×49, `FEAT_REG`×6

**컴포넌트 상위 15** — `WaitDC`×42, `ScalerFloor`×36, `Retrain`×20, `EOD_RETRAIN`×14, `RF`×9, `ScalerRefresh`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `GuardGhost`×4, `RegimeFingerprint`×3

### `logs/retrain_intraday_20260824_093601.log` — 2.4KB · 20행 · 최종 09:36:23

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 09:36:01,432 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-24 09:36:01,432 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-24 09:36:01,432 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-24 09:36:01,433 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_14801a25.json
2026-08-24 09:36:04,362 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-24 09:36:22,947 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.90s | old_acc=0.3997)
2026-08-24 09:36:23,033 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-24 09:36:23,033 [INFO] LEARNING: [Retrain] 완료 | 18.7초 | 성공=1/1 호라이즌
2026-08-24 09:36:23,034 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.6s 데이터=4800행
2026-08-24 09:36:23,035 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_14801a25.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 10 |
| 진입 등록(`[Position] 진입`) | 10 |
| 체결(`[체결진입]`) | 10 |
| 청산(`체결청산`) | 10 |
| 차단(`[차단]`) | 93 |
| 사이저 호출(`[Sizer]`) | 30 |

### 포지션 10건 · 승 6 (60%) · 합계 -8.75pt (-462,687원)  ※ 레그 16행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:44:01 | SHORT | 3 | 3m | 3 | +2.08 | +99,152 | 하드스톱(틱) |
| 09:56:00 | SHORT | 3 | 3m | 3 | -3.76 | -192,857 | 하드스톱(틱) |
| 10:15:00 | SHORT | 3 | 3m | 3 | -4.17 | -212,856 | 하드스톱(틱) |
| 10:55:00 | SHORT | 1 | 3m | 1 | +0.64 | +30,396 | 하드스톱(틱) |
| 11:11:01 | SHORT | 1 | 5m | 1 | -3.14 | -158,591 | 하드스톱(틱) |
| 11:34:00 | SHORT | 1 | 5m | 1 | +0.52 | +24,396 | 하드스톱(틱) |
| 12:29:03 | SHORT | 1 | 3m | 1 | +0.42 | +19,421 | 하드스톱(틱) |
| 13:02:00 | SHORT | 1 | 3m | 1 | -1.84 | -93,575 | 하드스톱(틱) |
| 14:25:01 | SHORT | 1 | 1m | 1 | +0.28 | +12,412 | 하드스톱(틱) |
| 14:30:00 | SHORT | 1 | 1m | 1 | +0.22 | +9,415 | 하드스톱(틱) |

**청산 레그 16행** (부분청산 6 · 전량청산 10)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:44:58 | 부분 | 1 | +1.90 | +93,384 | TP1 부분청산 33% |
| 09:48:11 | 부분 | 1 | -0.00 | -1,616 | 하드스톱(틱) |
| 09:48:11 | 전량 | 1 | +0.18 | +7,384 | 하드스톱(틱) |
| 09:57:09 | 부분 | 1 | -2.18 | -110,619 | 손절1차 조기축소 |
| 09:57:09 | 부분 | 1 | -2.18 | -110,619 | 손절1차 조기축소 |
| 10:03:04 | 전량 | 1 | +0.60 | +28,381 | 하드스톱(틱) |
| 10:15:52 | 부분 | 1 | -2.39 | -120,952 | 손절1차 조기축소 |
| 10:15:52 | 부분 | 1 | -2.37 | -119,952 | 손절1차 조기축소 |
| 10:22:48 | 전량 | 1 | +0.59 | +28,048 | 하드스톱(틱) |
| 10:55:32 | 전량 | 1 | +0.64 | +30,396 | 하드스톱(틱) |
| 11:14:36 | 전량 | 1 | -3.14 | -158,591 | 하드스톱(틱) |
| 11:38:38 | 전량 | 1 | +0.52 | +24,396 | 하드스톱(틱) |
| 12:32:09 | 전량 | 1 | +0.42 | +19,421 | 하드스톱(틱) |
| 13:04:43 | 전량 | 1 | -1.84 | -93,575 | 하드스톱(틱) |
| 14:25:06 | 전량 | 1 | +0.28 | +12,412 | 하드스톱(틱) |
| 14:30:16 | 전량 | 1 | +0.22 | +9,415 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×11, `손절1차 조기축소`×4, `TP1 부분청산 33%`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 10/10건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -462,687 = 포지션합 -462,687 → OK · `[청산 완료]` 10건 = 조립 포지션 10건 → OK

### 진입 10건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:44:01 | SHORT | 3 | 1077.32 | 3m | trend |
| 09:56:00 | SHORT | 3 | 1078.94 | 3m | trend |
| 10:15:00 | SHORT | 3 | 1079.36 | 3m | neutral |
| 10:55:00 | SHORT | 1 | 1069.64 | 3m | mean-revert |
| 11:11:01 | SHORT | 1 | 1060.7 | 5m | mean-revert |
| 11:34:00 | SHORT | 1 | 1069.62 | 5m | neutral |
| 12:29:03 | SHORT | 1 | 1052.54 | 3m | trend |
| 13:02:00 | SHORT | 1 | 1049.88 | 3m | mean-revert |
| 14:25:01 | SHORT | 1 | 1058.28 | 1m | mean-revert |
| 14:30:00 | SHORT | 1 | 1056.34 | 1m | mean-revert |

계약수 분포 — 1계약×7, 3계약×3

등급 분포 — `A급(원시C)`×8, `A급(원시X)`×1, `C급`×1

**진입한 건들의 체크리스트 미통과 항목** — `ofi`×5, `fore`×4, `chas`×4, `cvd`×3, `prev`×1, `time`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×23, **3계약**×7

실제 진입 계약수 — **1계약**×7, **3계약**×3

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×30

### 차단 사유 93건 · 36종

| 건수 | 사유 |
|---|---|
| 38 | 등급X — 미통과 항목: 2_confidence |
| 8 | JointGateBlock — meta=0.50 tox=0.70 joint=0.350 < 0.50 |
| 6 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 17.1pt > ATR×5.0=13.0pt (시가=1087.98 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.2pt > ATR×5.0=14.0pt (시가=1087.98 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.7pt > ATR×5.0=14.3pt (시가=1087.98 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.4pt > ATR×5.0=14.2pt (시가=1087.98 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.5pt > ATR×5.0=14.5pt (시가=1087.98 반등위험) |
| 1 | JointGateBlock — meta=0.64 tox=0.70 joint=0.449 < 0.50 |
| 1 | 청산 후 쿨다운 — 70초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 10초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 3초 후 재진입 가능 |
| 1 | Reverse Clamp (P3-b) — 청산 후 역방향(SHORT→LONG) 4s 이내 진입 금지 |
| 1 | 청산 후 쿨다운 — 106초 후 재진입 가능 |
| 1 | Reverse Clamp (P3-b) — 청산 후 역방향(SHORT→LONG) 47s 이내 진입 금지 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.0pt > ATR×5.0=9.9pt (시가=1087.98 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×38, `3_vwap`×14, `6_foreign`×14, `4_cvd`×10, `7_prev_bar`×10, `5_ofi`×5

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 4건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×4

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 33건 · 최대 20985ms · 5초 초과 7건

상위 — 20985ms, 7500ms, 7359ms, 6187ms, 5625ms, 5297ms, 5032ms, 4718ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 7500ms | 2549ms | **4951ms (66%)** |
| 09:05:05 | 6187ms | 472ms | **5715ms (92%)** |
| 11:06:06 | 5625ms | 610ms | **5015ms (89%)** |
| 11:16:22 | 20985ms | 671ms | **20314ms (97%)** |
| 12:09:07 | 7359ms | 433ms | **6926ms (94%)** |
| 14:20:05 | 5297ms | 427ms | **4870ms (92%)** |
| 14:43:05 | 5032ms | 367ms | **4665ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260824_WARN.log`
```
--- ConstOut ×7(표본)
09:35:00 2026-08-24 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:29:00 2026-08-24 10:29:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:24:00 2026-08-24 11:24:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
12:41:00 2026-08-24 12:41:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×4(표본)
09:57:09 2026-08-24 09:57:09 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:15:52 2026-08-24 10:15:52 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:14:36 2026-08-24 11:14:36 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:04:43 2026-08-24 13:04:43 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:48:11 2026-08-24 09:48:11 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:50:11)
09:48:11 2026-08-24 09:48:11 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:50:11)
10:03:04 2026-08-24 10:03:04 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:05:04)
10:03:04 2026-08-24 10:03:04 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:05:04)
--- [SHAP] 슬로우 ×5(표본)
12:24:01 2026-08-24 12:24:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1177ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:45:01 2026-08-24 13:45:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 908ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
14:25:02 2026-08-24 14:25:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1029ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
14:55:02 2026-08-24 14:55:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1078ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:23 2026-08-24 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2859ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2859 band=INFO since_pipe_s=NA
09:00:06 2026-08-24 09:00:06 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7500 band=WARN since_pipe_s=0.1
09:05:05 2026-08-24 09:05:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6187ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=6187 band=WARN since_pipe_s=0.1
09:37:02 2026-08-24 09:37:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2500 band=INFO since_pipe_s=0.0
```

### `logs/20260824_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-08-24 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-08-24 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:01 2026-08-24 09:35:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=332ms fit=29ms total=364ms
09:36:01 2026-08-24 09:36:01 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-08-24 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.027 level=0 (heartbeat)
09:05:00 2026-08-24 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.027 level=0 (heartbeat)
09:10:00 2026-08-24 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.027 level=0 (heartbeat)
09:15:00 2026-08-24 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.028 level=0 (heartbeat)
--- [SchedForceExit] ×1(표본)
15:11:19 2026-08-24 15:11:19 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
```

### `logs/20260824_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:02 2026-08-24 09:00:02 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-08-24 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:37:02 2026-08-24 09:37:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:29:00 2026-08-24 10:29:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:31:02 2026-08-24 10:31:02 [INFO] SIGNAL: [ConstOut] 5m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-08-24 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-08-24 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-08-24 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-08-24 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.419
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
08:40:45 2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
--- 안전망 ×8(표본)
09:07:00 2026-08-24 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-24 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-08-24 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-08-24 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260824_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00129 auc=0.498 out_max=0.5673 (기준 auc<0.53 and span<0.020, 기저율=0.5667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00055 auc=0.550 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:04 2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00038 auc=0.529 out_max=0.3296 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260824_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:12 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 29 | 09:56:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=50,028,172) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |

- 이 로그 생존구간: 08:41 ~ 14:30

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260824_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:20 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 59 | 09:56:00 [WARNING] atr=2.5657 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | … |
| 12:00 | 장중 중간점 | 4 | 11:59:04 [WARNING] _tick_header 간격 4078ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4078 band=… |
| 14:00 | 장중 후반 · 장중 재학습 | 2 | 13:56:02 [WARNING] level=WARNING degraded=OFF | latency=296ms | quality=1.00 | cache_age=180s | exceptions_10m=0 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1 | 15:08:00 [WARNING] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

- 이 로그 생존구간: 08:41 ~ 15:08

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260824_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:48 [INFO] 활성화 | file=logs\crash_fault.log PID=25592 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 128 | 08:49:02 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 262 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 170 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 171 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 157 | 15:04:01 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 130 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 18 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260824_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:20 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0118) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 130 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0311) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 231 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0285) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 137 | 09:54:00 [WARNING] 신뢰도 미달 34.1% < 38.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 124 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=11m max_z=+4.07(ofi_reversal_speed) extreme=1 |
| 14:00 | 장중 후반 · 장중 재학습 | 144 | 13:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 97 | 15:04:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:22 [INFO] mc 갱신 trigger=RETRAIN base=0.422  LUNCH_RECOVERY 0.413→0.418 | CLOSE_VOLATILE 0.421→0.426 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| 20260817 | 17:58 | 로그 본문 |
| **중앙값** | **17:02** | 기준선 |
| **오늘 20260824** | **15:40** | 로그 본문 |

- 델타 **-82분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 결과 요약
### 🔴 F-1 이번 창의 74.6%가 백필 행이다 — 26주 판정이 성립하지 않는다
### 🔴 F-2 CORE VWAP 게이트 방향이 실측과 반대 + 역추세 예외 경로 사망
### F-3 `vwap_momentum` — 백필/라이브 계산 동치성 의심
### F-4 L1이 **폐기 피처**를 Bonferroni 통과 후보로 올린다
### F-5 L3 무력화 + 잠긴 피처 11종
### F-6 L3 해석에 무정보 기준선이 없었다 (신규 계측 3종)
### 후속 (전부 미조치 — 주간회의 승인 필요, `NEXT_TODO.md` 490차 후속2 항목)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
ion`/`bull_exhaustion`이
**130거래일 전 구간 상수 0.0**(2026-08 5,629행 전수 `{0.0: 5629}`)이라 **발동 불가**다.
273차가 "MR 발동 0회"를 임계 완화(0.70→0.60)로 풀려 했으나 **원인은 임계가 아니라 입력이
상수**였다 — 471차 F-1·474차와 같은 계열(도달 불가 경로).

⚠ **"뒤집으면 이긴다"는 성립하지 않는다** — L2 역방향도 h=30 net +0.52pt(**t=0.08**),
전·후반 부호 반전. 게다가 L1·L2는 h분 뒤 **종가**를 재는데 라이브는 ATR TP/SL의 **경로 의존
청산**이고, 게이트는 방향을 만드는 게 아니라 **거르는** 필터라 모집단이 바뀐다.
→ 안건 B-1(exhaustion 상수 0 규명) · B-3(섀도 계측). **게이트는 건드리지 않는다.**

### F-3 `vwap_momentum` — 백필/라이브 계산 동치성 의심

`momentum==0` 비율이 1.0%(2~6월) → 21.3%(7월) → **33.0%(8월)**, IC도 h=5 전반 −0.145 →
후반 −0.072로 반감. clip 포화 가설은 **반증**됐다(`|pos|==2.0` 비율은 2월 56.9% > 8월 38.6%,
clip 5분 지속률은 전 구간 81.8~89.6%로 불변). 2월은 clip 56.9%×지속률 89.6% ≈ 51%가 0이어야
하는데 실측 1.0% ⇒ **2~5월 값은 현행 공식(`_vh[-1]-_vh[-5]`, 119차 `bd87f06`)이 만든 값이
아니다.** `vwap_momentum`은 `_BACKFILL_COMPUTED_KEYS`에 있으므로 **같은 이름이 두 구현에서
다른 값**을 쓰고 있을 가능성. → 안건 B-2.

### F-4 L1이 **폐기 피처**를 Bonferroni 통과 후보로 올린다

`program_foreign_net_krw`가 h=5 후보 3위(\|t\|=8.07, ★)로 등장 — **451차가 오라벨+100%
중복으로 삭제한 피처**다. 130일 창이 폐기 이전까지 닿는 한 매 사이클 되살아난다.
유일한 단서인 **유효일수 17일**이 L1 표에 출력되지 않는다(계산은 돼 있다). → 안건 A-2·A-3.

### F-5 L3 무력화 + 잠긴 피처 11종

OLD(배포 pkl)와 NEW(JSON∩마스터97)의 차집합이 **양방향 공집합**이라 Δ가 구조적으로 0.
원인은 458차 동결 슈퍼셋 — JSON이 요구하나 `feature_names.pkl` 97개에 없어 탈락하는 피처
11종(1m 2 / 3m 1 / 5m 1 / 10m 4 / 15m 1 / 30m 7, `opt_chain_pcr` 포함).

### F-6 L3 해석에 무정보 기준선이 없었다 (신규 계측 3종)

L3는 `acc=0.3834`만 출력해 **좋은지 나쁜지 판단할 수 없었다.** 실측 라벨 분포는 FLAT
46.0~66.1%이고, "항상 FLAT" 기준선 대비 acc3는 **8.6~27.4%p 낮다**. 단 프로덕션은
`_make_sample_weight()`로 FLAT 가중을 낮춰 **일부러 방향을 내게** 설계됐으므로 이 비교는
불공정하다. 공정한 지표(**균형정확도**, 기저율 무관, 0.5=무정보)로 재측정:

**1m 0.5003 / 3m 0.5178 / 5m 0.5373 / 15m 0.5207.**

- **1m 스킬이 정확히 0**인데 `ENSEMBLE_WEIGHTS`가 이미 1m을 퇴역(331차 후속2)시켰다 —
  설계와 실측의 **독립적 일치**.
- 가중 최대(0.30)인 **5m이 최고** — 가중 배분이 성능과 정합적이다.
- ⚠ 5m +3.7%p는 명목 5σ이나 5분 **중첩 라벨** 보정 시 **2σ 남짓** — "약하지만 아마 실재".
- ⚠ **10m은 측정되지 않았다**(L3 `HORIZONS_MIN` 미포함). 가중 0.29로 2위인데 사각지대.
  → 안건 A-4·A-5.

기존 `feature_ablation_purged_cv.eval_feature_set`이 `sample_weight`를 `"3m"`으로 **고정**해
다른 호라이즌에 부정확한 것도 이때 확인했다(그래서 L3'는 동등 구현을 별도로 씀).

### 후속 (전부 미조치 — 주간회의 승인 필요, `NEXT_TODO.md` 490차 후속2 항목)

- **A-1** L1·L2 `--live-only` + 헤더에 백필 비율 / **A-2** L1 표에 유효일수 열 /
  **A-3** 폐기 피처 태그 / **A-4** L3에 10m 추가 / **A-5** 균형정확도 L3 기본 출력 편입
- **B-1** exhaustion 상수 0 규명 / **B-2** `vwap_momentum` 백필·라이브 동치성 /
  **B-3** `3_vwap` 섀도 손익 / **B-4** 5m 4개 피처 다음 사이클 필수 재확인 /
  **B-5** `time_cos` 청산·사이징 축 검토
- ⚠ A-1~A-5는 **합격선·판정문 무변경**이므로 사전등록(§9-4) 대상이 아니다.

---

```

</details>

### dev_memory/NEXT_TODO.md — 1.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### P1
### P2
### 고도화 (당일 관측 근거)
### 다음 국면(오늘 장후)이 닫을 관측 항목
## MW0601 490차 후속2 — 26주 WFA 피처셋 재검증 후속 (전부 미조치 · 주간회의 승인 필요)
### A. 계측 신뢰 회복 — 피처 변경보다 **먼저**
### B. 조사 안건 (결론 없음 — 조사 지시)
### 다음 사이클(2027-02경) 착수 시 확인
```

미완료 체크박스 **1856건** (끝에서 30건)
```
- [ ] **`references/report_template.md` 갱신 (P2, 기등록 재확인)** — 아직 `-pre`/`-intra`/`-post`
- [ ] **🔴 사용자 조치 (오늘 중) — `.git/index.lock` 회수 (이상점 1-7)** —
- [ ] **P1 F-F 점검 세션 git 호출이 락을 남기지 못하게 한다 (이상점 1-7)** —
- [ ] **F-G — CB③ 「조건 성립 분수 + 그 창 안 진입·손익」 계량 (이상점 1-8)**
- [ ] **F-J — 5~180초 정지 구간 스택 스냅샷, 섀도 한정 (이상점 1-10)**
- [ ] **F-I — 기등록 P2-I(`trades.exit_stage`) 근거 보강 (이상점 1-9)**
- [ ] **F-K — `[JointGateBlock 차단]` 무정보 폴백 가시화 (이상점 1-11)**
- [ ] **고도화 ⑤ — 08-28 CB② 결정용 카운터팩추얼 표에 CB③ 열을 합본**
- [ ] **고도화 ⑥ — 「TP1 보호전환 → 청산」 경과초 라이브 계측 (사전등록 문턱 명시)**
- [ ] **고도화 ⑦ — `[IntradayRegime]` 로그에 z 산출 표본 봉 수 `n=` 병기**
- [ ] **O-2′** 이상점 1-3 ② 축 — `cvd_divergence`·`ofi_norm` 피처 구성 기여.
- [ ] **O-5** `[Capital]` 2행 중복 — `main.py:12727` 호출 경로 (P2 미만).
- [ ] **N-10** (누적) 15:10 강제청산 실집행 — 누적 0회. `[ForceExitPass]`→`[TimeExit]`→
- [ ] **O-6 🆕** `12:31:20 … 포지션=SHORT` — 12:26 다이제스트에 없는 **7번째 진입**. 전량 재집계.
- [ ] **O-7 🆕** STEP9 예측 DB 행수 = 파이프라인 분수 대조(12:26 기준 211분). 장중 DB 금지로 미판정.
- [ ] **O-8 🆕** 11:25:02 CB③ 버퍼 리셋(`n=1/30`) 후 15:10까지 `ready=Y` 재도달 및 임계 미달 지속 여부.
- [ ] **O-9 🆕** `band=ALERT` 재발화 여부. 재발화 시 표본 3(08-21 11,016ms / 08-24 20,985ms / +1).
- [ ] **1-7** `.git/index.lock` — 사용자 조치 대기. 장후에도 남아 있으면 **그날 산출물이 커밋되지 않은 채 끝난다**.
- [ ] **A-1** L1·L2에 `--live-only`(백필 행 제외) 신설 + 출력 헤더에 백필 비율 1줄.
- [ ] **A-2** `core_feature_discovery.py` 후보 표에 **유효일수(`n_days`) 열** 추가.
- [ ] **A-3** `excluded_from_all_horizons` 등재 피처에 `[폐기]` 태그 표시(제외가 아니라 표시).
- [ ] **A-4** `validate_feature_set_purged_cv.py:HORIZONS_MIN`에 **10m 추가**(dict 1줄).
- [ ] **A-5** 균형정확도·조건부 적중률을 L3 기본 출력에 편입.
- [ ] **B-1** `bear_exhaustion`/`bull_exhaustion`이 **130거래일 전 구간 상수 0.0**인 이유 규명.
- [ ] **B-2** `vwap_momentum` **백필 구현 vs 라이브 구현 동치성** 검증.
- [ ] **B-3** `3_vwap` 게이트 **섀도 손익 계측**(게이트는 **건드리지 않는다**).
- [ ] **B-4** 5m `bb_position`·`poc_above`·`is_close_volatile`·`ret_5m` —
- [ ] **B-5** `time_cos`(일중 시간대 구조)를 **청산·사이징 축** 입력으로 볼 가치 검토.
- [ ] 2026-08 이후가 전부 라이브 구간이므로 **A-1 없이도 백필 오염이 줄어든다** — 다만
- [ ] 기준선 대조: `docs/정기점검/26주WFA_MW0601-20260824/` 의 L1 IC·L2 net·균형정확도와 비교.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
보 표에 **유효일수(`n_days`) 열** 추가.
      이미 계산돼 있고 **표에서만 빠졌다**. 이게 없어 A-3의 좀비 피처를 못 걸렀다.
- [ ] **A-3** `excluded_from_all_horizons` 등재 피처에 `[폐기]` 태그 표시(제외가 아니라 표시).
- [ ] **A-4** `validate_feature_set_purged_cv.py:HORIZONS_MIN`에 **10m 추가**(dict 1줄).
      앙상블 가중 **0.29로 2위**인데 purged CV에서 한 번도 측정된 적이 없다.
- [ ] **A-5** 균형정확도·조건부 적중률을 L3 기본 출력에 편입.
      현행 `dir_acc`는 **FLAT 예측을 오답으로 세어** 구조적으로 눌린다(0.31~0.37) →
      그 값만 보면 "모델 무스킬"로 오독된다. 실제 균형정확도는 5m **0.5373**.
      참고 구현: `docs/정기점검/26주WFA_MW0601-20260824/committed.py`.
      ⚠ 같이 발견: `feature_ablation_purged_cv.eval_feature_set`이 `sample_weight`를
      **`"3m"` 고정**으로 넘긴다 — 다른 호라이즌에 부정확.

### B. 조사 안건 (결론 없음 — 조사 지시)

- [ ] **B-1** `bear_exhaustion`/`bull_exhaustion`이 **130거래일 전 구간 상수 0.0**인 이유 규명.
      (2026-08 5,629행 전수 `{0.0: 5629}`) 이 때문에 `checklist.py`의 MEAN_REVERSION 분기
      (`>= MR_EXHAUSTION_MIN_WEAK=0.60`)가 **구조적으로 발동 불가**다.
      273차가 "MR 발동 0회"를 임계 완화(0.70→0.60)로 풀려 했으나 **원인은 임계가 아니라 입력**.
      471차 F-1·474차와 같은 계열(도달 불가 경로).
- [ ] **B-2** `vwap_momentum` **백필 구현 vs 라이브 구현 동치성** 검증.
      `momentum==0` 비율 1.0%(2~6월) → 21.3%(7월) → **33.0%(8월)**. clip 포화 가설은 반증
      (`|pos|==2.0` 비율 2월 56.9% > 8월 38.6%, 5분 지속률 전 구간 81.8~89.6% 불변).
      2월은 51%가 0이어야 하는데 실측 1.0% ⇒ **2~5월 값은 현행 공식이 만든 값이 아니다.**
      119차(`bd87f06`)가 이 피처의 "항상 0" 버그를 고친 이력 확인 포함.
- [ ] **B-3** `3_vwap` 게이트 **섀도 손익 계측**(게이트는 **건드리지 않는다**).
      `vwap_position` IC가 전 호라이즌 음수인데(hit 43.9%/39.0%/**33.3%**)
      `checklist.py:163,171`은 추세추종 방향만 통과시키고 미통과 시 **강제 X등급**이다.
      ⚠ **부호 반전은 L2가 기각**(역방향 h=30 net +0.52pt, **t=0.08**, 전·후반 부호 반전).
      게이트는 방향을 만드는 게 아니라 거르는 필터라 바꾸면 모집단이 변한다 → 섀도 표본 선행.
- [ ] **B-4** 5m `bb_position`·`poc_above`·`is_close_volatile`·`ret_5m` —
      **다음 26주 사이클 필수 재확인 항목으로 등록**. L3' leave-one-out에서 넷 다 역기여
      (+0.48~0.71%p)로 나왔고, 331차 후속이 예고했던 확인이 **같은 방향으로 재현**됐다.
      ⚠ 지금 제거하지 않는다 — 효과 크기(0.7%p)가 폴드 편차(1m 0.281~0.409, **12.8%p**)보다
      작고 `Δdir`·`Δacc3` 부호가 엇갈린다(사후선택 위험).
- [ ] **B-5** `time_cos`(일중 시간대 구조)를 **청산·사이징 축** 입력으로 볼 가치 검토.
      L2 net/일 상위 3개를 전부 차지(+7.9~9.1pt/일)하고 전·후반 모두 양수인데 **t=1.38 미달**.
      ⚠ 진입 축 채택은 사전등록 위반(458차 D6). 455차 N2가 "부호반전형은 청산 축 후보"로
      분리한 것과 같은 취급까지만.

### 다음 사이클(2027-02경) 착수 시 확인

- [ ] 2026-08 이후가 전부 라이브 구간이므로 **A-1 없이도 백필 오염이 줄어든다** — 다만
      130일 창은 여전히 2026-08 이전에 닿으므로 A-1이 반영됐는지 **먼저 확인**할 것.
- [ ] 기준선 대조: `docs/정기점검/26주WFA_MW0601-20260824/` 의 L1 IC·L2 net·균형정확도와 비교.
      균형정확도 기준선 = 1m **0.5003** / 3m **0.5178** / 5m **0.5373** / 15m **0.5207**.

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

### `data/heartbeat_MW0601_20260824.json` — 244B · 08-24 15:40:03
```json
{
 "pid": 25592,
 "written_at": "2026-08-24T15:40:03",
 "beat_epoch": 1787553599.8062935,
 "beat_age_sec": 3.2,
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

### `docs/정기점검/매일점검` — 67개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260824-점검리포트.md` | 113.3KB | 08-24 12:41 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_intra.md` | 65.2KB | 08-24 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_pre.md` | 47.4KB | 08-24 08:59 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.0KB | 08-23 16:51 |
| `docs/정기점검/매일점검/MW0601-20260821-점검리포트.md` | 208.7KB | 08-21 16:54 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_post.md` | 74.4KB | 08-21 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_intra.md` | 57.0KB | 08-21 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_pre.md` | 46.8KB | 08-21 08:59 |

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

1. `logs/20260824_WARN.log`: ERROR 이상 1건
2. 완료 마커 **`daily_close_done`** 없음 — 15:40 일일 마감 완료 마커
3. 완료 마커 **`strategy_report`** 없음 — 일일 전략 리포트
4. 포지션 10건 중 최종청산이 하드스톱·손절 계열 **10건(100%)** — 손절 준수율 확인 필요 (레그 16행)
5. 다레그 포지션 **3건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
6. **SYSTEM 로그가 직전 5거래일 중앙값(17:02)보다 82분 이르게 끝났다** (오늘 15:40) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
7. 메인 스레드 정지 5초 초과 **7건** (최대 20985ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
8. `logs/20260824_WARN.log`: **ConstOut** 7건(표본)
9. `logs/20260824_SYSTEM.log`: **ConstOut** 8건(표본)
10. `logs/20260824_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20260824_SIGNAL.log`: **ConstOut** 8건(표본)
12. `logs/20260824_LEARNING.log`: **축퇴** 8건(표본)
13. 미커밋 변경 491건
14. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260824*.log` (Windows) / `grep 강제청산 logs/*20260824*.log`*