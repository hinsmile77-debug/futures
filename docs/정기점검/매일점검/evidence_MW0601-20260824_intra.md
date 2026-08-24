# 미륵이 증거 다이제스트 — 2026-08-24 / INTRA

- 생성 2026-08-24 12:26:44 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/youthful-compassionate-davinci/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260824` · `2026-08-24` · `260824` · `0824`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **17개** 파일 · 17개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260824.log` | 125B | 08-24 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260824.json` | 244B | 08-24 12:26 |
| `launcher_{DATE}_084001_24123.log` | 1 | `logs/Mireuk_batch/launcher_20260824_084001_24123.log` | 1.0MB | 08-24 12:25 |
| `retrain_intraday_{DATE}_093601.log` | 1 | `logs/retrain_intraday_20260824_093601.log` | 2.4KB | 08-24 09:36 |
| `retrain_intraday_{DATE}_103000.log` | 1 | `logs/retrain_intraday_20260824_103000.log` | 2.4KB | 08-24 10:30 |
| `retrain_intraday_{DATE}_112502.log` | 1 | `logs/retrain_intraday_20260824_112502.log` | 2.4KB | 08-24 11:25 |
| `{DATE}_DATA.log` | 1 | `logs/20260824_DATA.log` | 183.6KB | 08-24 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260824_DEBUG.log` | 140.2KB | 08-24 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260824_HEALTH.log` | 2.5KB | 08-24 12:07 |
| `{DATE}_HOGA.log` | 1 | `logs/20260824_HOGA.log` | 30.4MB | 08-24 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260824_LEARNING.log` | 166.0KB | 08-24 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260824_MICRO.log` | 608.3KB | 08-24 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260824_PROBE.log` | 57.5KB | 08-24 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260824_SIGNAL.log` | 376.4KB | 08-24 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260824_SYSTEM.log` | 510.4KB | 08-24 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260824_TRADE.log` | 21.2KB | 08-24 12:15 |
| `{DATE}_WARN.log` | 1 | `logs/20260824_WARN.log` | 84.6KB | 08-24 12:24 |

## 2. 코드·커밋 상태

- HEAD `4dbdf80` · 브랜치 `v9-dev` · 미커밋 488건 · 🔴 **인덱스락 잔존** 0바이트 · 3.2시간 · git 프로세스 0개 → **커밋 불가 상태**
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
… 외 448건
```

**당일(2026-08-24) 커밋**
```
(당일 커밋 없음 — ⚠ 인덱스락 잔존으로 **커밋 불가 상태였음**. 미조치가 아니다)
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

_본문 미열람(설정): `20260824_HOGA.log` 30.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `retrain_intraday_20260824_112502.log`, `20260824_MICRO.log`, `20260824_DATA.log`, `20260824_PROBE.log`, `launcher_20260824_084001_24123.log`, `20260824_DEBUG.log`, `force_flat_guard_20260824.log`_

### `logs/20260824_TRADE.log` — 21.2KB · 159행 · 최종 12:15:00

- 형식 평문 · 시각 인식 159행 · INFO=159

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:12 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-24 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-24 09:30:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,955,870) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-24 09:32:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,955,870) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-24 09:33:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,955,870) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-24 11:44:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 1계약 C급 (meta=0.50 tox=0.70 joint=0.350)
2026-08-24 11:45:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,438,210) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1)
2026-08-24 11:45:01 [INFO] TRADE: [JointGateBlock 차단] SHORT 1계약 A급 (meta=0.65 tox=0.70 joint=0.456)
2026-08-24 12:15:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,438,210) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.5→2계약]
2026-08-24 12:15:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 1계약 A급 (meta=0.58 tox=0.70 joint=0.403)
```

</details>

**채널** — `TRADE`×159

**컴포넌트 상위 15** — `Chejan`×39, `Position`×29, `Sizer`×22, `주문요청`×15, `JointGateBlock 차단`×12, `진입체크`×6, `체결진입`×6, `체결진입보정`×6, `TickStop-S0C`×6, `청산 완료`×6, `TickTP1`×5, `손절1차 분할체결`×2, `손절1차 조기축소`×2, `ProfitGuard`×1, `TP1 부분청산`×1

### `logs/20260824_WARN.log` — 84.6KB · 350행 · 최종 12:24:01

- 형식 평문 · 시각 인식 350행 · ERROR=1, WARNING=349

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 32ms
2026-08-24 08:41:20 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-24 08:41:23 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2859ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2859 band=INFO since_pipe_s=NA
2026-08-24 08:41:26 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3375ms — live 중단 원인 분석용
  …
2026-08-24 12:09:07 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7359ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7359 band=WARN since_pipe_s=0.0
2026-08-24 12:12:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.307% (임계 ±0.307%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-24 12:14:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3875 band=INFO since_pipe_s=0.0
2026-08-24 12:19:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3984ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3984 band=INFO since_pipe_s=0.0
2026-08-24 12:24:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1177ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
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

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 98 | 08:41:20 | 12:19:05 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 39 | 09:44:01 | 11:38:38 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='907' | pending='ENTRY:SHORT qty=3 filled=0 order_no=? reason=진입 req_at=09:44:01.013' | positio… |
| `ChejanMatch` | 39 | 09:44:01 | 11:38:38 | order_no='907' | pending='ENTRY:SHORT qty=3 filled=0 order_no=907 reason=진입 req_at=09:44:01.013' | pending_matched=True |
| `PendingOrder` | 30 | 09:44:01 | 11:38:39 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1077.32, 'reason': '진입', 'hint_source': '', 'atr': 2.9657, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `EntryFillFlow` | 12 | 09:44:01 | 11:34:01 | actual_side='SHORT' | after='SHORT 3계약 @ 1077.36' | applied_side='SHORT' | before='SHORT 3계약 @ 1077.32' | fill_no='' | fill_price=1077.36 | fill_qty=1 | order_no='907' | pending='ENTRY:SHORT qty=3 filled=1 order_no=907 reason=진입 req_at=09:… |
| `ExitCooldown` | 12 | 09:48:11 | 11:38:38 | 하드스톱(틱) 후 2분 재진입 금지 (until 09:50:11) |
| `Health` | 9 | 09:00:02 | 12:06:00 | level=WARNING degraded=OFF | latency=2549ms | quality=0.86 | cache_age=35s | exceptions_10m=0 |
| `ScalerRefresh` | 9 | 09:05:00 | 12:12:00 | 5분 누적 수익률 -1.393% (임계 ±0.500%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PipePerf` | 8 | 09:00:02 | 11:26:03 | total=2549ms | S0=3ms S1=14ms S2=0ms S3=0ms S4=160ms S5=2017ms S6=303ms S7=45ms S8=6ms |
| `CB⑤` | 8 | 09:00:02 | 11:26:03 | 파이프라인 2549ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ExitSendOrderResult` | 8 | 09:48:11 | 11:38:38 | ret=0 kind=하드스톱(틱) direction=SHORT qty=2 |
| `ExitFillFlow` | 7 | 09:48:11 | 11:38:39 | after='SHORT 1계약 @ 1077.42' | before='SHORT 2계약 @ 1077.42' | fill_price=1077.42 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:SHORT qty=2 filled=1 order_no=976 reason=하드스톱(틱) req_at=09:48:11.007' | reason='하드스톱(틱)' |

**채널** — `SYSTEM`×341, `HEALTH`×9

**컴포넌트 상위 15** — `LiveDBG`×99, `ChejanFlow`×39, `ChejanMatch`×39, `PendingOrder`×30, `EntryFillFlow`×12, `ExitCooldown`×12, `Health`×9, `ScalerRefresh`×9, `PipePerf`×8, `CB⑤`×8, `ExitSendOrderResult`×8, `ExitFillFlow`×7, `EntryAttempt`×6, `EntrySendOrderResult`×6, `FixB`×6

### `logs/20260824_SYSTEM.log` — 510.4KB · 3536행 · 최종 12:26:29

- 형식 평문 · 시각 인식 3529행 · INFO=3529, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:40:48 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=25592 | 행감지=30s all_threads=True
2026-08-24 08:41:02 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-24 08:41:02 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-24 08:41:02 [INFO] SYSTEM: 미륵이 초기화
2026-08-24 08:41:02 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-21) 종가 버퍼 로드: 384봉
  …
2026-08-24 12:26:20 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+10,foreign:-1489,institution:+1543}
2026-08-24 12:26:20 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+10,foreign:-1489,institution:+1543}
2026-08-24 12:26:20 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+127459 nonarb=-2090912
2026-08-24 12:26:20 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+127459 nonarb=-2090912
2026-08-24 12:26:29 [INFO] SYSTEM: [CybosRT-TICK] #78300 code=A0569 raw_time=122629 parsed=12:26:29 price=1053.58 vol=1 bid1=1053.58 ask1=1053.60 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×3529

**컴포넌트 상위 15** — `CybosInvestorRaw`×822, `CybosRT-TICK`×788, `CybosRT-ROLLOVER`×221, `BAR-CLOSE`×221, `CVD-ANCHOR`×221, `TickUI`×220, `S6Detail`×207, `PipePerf`×207, `CybosEvent`×78, `BalanceUI`×74, `System`×59, `CybosDailyPnl`×52, `MicroRegime`×49, `BalanceRefresh`×49, `RegimeFingerprint`×38

### `logs/20260824_SIGNAL.log` — 376.4KB · 3258행 · 최종 12:26:02

- 형식 평문 · 시각 인식 3258행 · WARNING=1355, INFO=1903

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.419
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.410
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.406
2026-08-24 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-08-24 12:26:02 [INFO] SIGNAL: [MetaGate][LIVE] skip: blended=0.442 reduce_thr=0.465 take_thr=0.570 (grade=X min_conf=0.620 ens=0.379 meta_raw=0.535 ens_w=0.60)
2026-08-24 12:26:02 [INFO] SIGNAL: 앙상블: dir=+1 conf=37.9% grade=X micro=추세장
2026-08-24 12:26:02 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=3m tf=4.29 → TP1×0.5
2026-08-24 12:26:02 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.379<mc0.620)
2026-08-24 12:26:02 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=44.2% size_mult=1.00 reason=meta_skip
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 876 | 09:00:03 | 12:12:01 | 1m 'macro_vix' scale=0.0190 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 156 | 08:45:20 | 12:12:01 | 1m CORE 'cvd_divergence' raw_std≈0(0.0118) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 108 | 09:00:00 | 12:22:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 84 | 09:00:00 | 12:22:00 | ts=08:59 horizon=1m age=1m max_z=+4.87(queue_refill_rate) extreme=2 |
| `Checklist` | 79 | 09:06:00 | 12:26:02 | 신뢰도 미달 34.9% < 38.9% → 강제 X등급 |
| `WeightCollapse` | 43 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `PCR-Dampen` | 4 | 09:07:00 | 09:22:00 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConstOut` | 3 | 09:35:00 | 11:24:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:02 | 09:00:02 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `MetaGate` | 1 | 09:30:00 | 09:30:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×3258

**컴포넌트 상위 15** — `ScalerFloor`×936, `SIGNAL`×414, `MetaGate`×241, `Ensemble`×210, `FQAdj`×204, `ScalerRefresh`×188, `ZeroDiag`×164, `Checklist`×150, `Model`×132, `ATR-Horizon`×111, `ScalerMonitor`×84, `차단`×63, `ToxicityGate`×53, `MicroRegime`×49, `InstabilityGate`×45

### `logs/20260824_LEARNING.log` — 166.0KB · 1568행 · 최종 12:26:02

- 형식 평문 · 시각 인식 1568행 · WARNING=124, INFO=1444

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 08:41:04 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00129 auc=0.498 out_max=0.5673 (기준 auc<0.53 and span<0.020, 기저율=0.5667 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00055 auc=0.550 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-24 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00038 auc=0.529 out_max=0.3296 (기준 auc<0.53 and span<0.020, 기저율=0.3294 n=85) → 보정 미적용, raw 통과
  …
2026-08-24 12:26:02 [INFO] LEARNING: ✓ 1m 예측 적중 (conf=37.5% DN)
2026-08-24 12:26:02 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=49.4% 예측=UP 실제=FL)
2026-08-24 12:26:02 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=39.6% DN)
2026-08-24 12:26:02 [INFO] LEARNING: [Bias⚠] 3m 적중=13%(4/30) UP=18 DN=4 FL=8 [UP편향⚠ 60%]
2026-08-24 12:26:02 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=0.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 124 | 08:41:04 | 12:04:00 | 축퇴 감지 — span=0.00014 auc=0.492 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1568

**컴포넌트 상위 15** — `LEARNING`×656, `Calibration`×239, `SGD`×207, `sigma`×194, `Bias⚠`×76, `Bias`×67, `MetaConf`×41, `ScalerWarmup`×32, `OnlineLearner`×21, `SHAP`×7, `BiasReset`×6, `GBM-64`×6, `GBM`×6, `RF`×4, `ExtremityCorrector`×2

### `logs/20260824_HEALTH.log` — 2.5KB · 19행 · 최종 12:07:00

- 형식 평문 · 시각 인식 19행 · WARNING=9, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2549ms | quality=0.86 | cache_age=35s | exceptions_10m=0
2026-08-24 09:01:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=648ms | quality=0.86 | cache_age=94s | exceptions_10m=0
2026-08-24 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=305ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-24 09:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=277ms | quality=1.00 | cache_age=56s | exceptions_10m=0
2026-08-24 09:29:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 329ms (표본 20분)
  …
2026-08-24 11:27:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=481ms | quality=1.00 | cache_age=43s | exceptions_10m=0
2026-08-24 12:03:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=314ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-24 12:04:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=321ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-08-24 12:06:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=284ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-08-24 12:07:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=303ms | quality=1.00 | cache_age=57s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:02 | 12:06:00 | level=WARNING degraded=OFF | latency=2549ms | quality=0.86 | cache_age=35s | exceptions_10m=0 |

**채널** — `HEALTH`×19

**컴포넌트 상위 15** — `Health`×18, `HealthTrend`×1

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

### `logs/retrain_intraday_20260824_103000.log` — 2.4KB · 20행 · 최종 10:30:21

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-24 10:30:00,475 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-24 10:30:00,475 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-24 10:30:00,476 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-24 10:30:00,476 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['5m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_21930c98.json
2026-08-24 10:30:02,814 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-24 10:30:21,290 [INFO] LEARNING: [Retrain] 5m 교체 (intraday — CV 없음 | fit=0.94s | old_acc=0.4206)
2026-08-24 10:30:21,382 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-24 10:30:21,382 [INFO] LEARNING: [Retrain] 완료 | 18.6초 | 성공=1/1 호라이즌
2026-08-24 10:30:21,383 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 20.9s 데이터=4800행
2026-08-24 10:30:21,384 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_21930c98.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 6 |
| 진입 등록(`[Position] 진입`) | 6 |
| 체결(`[체결진입]`) | 6 |
| 청산(`체결청산`) | 6 |
| 차단(`[차단]`) | 63 |
| 사이저 호출(`[Sizer]`) | 22 |

### 포지션 6건 · 승 3 (50%) · 합계 -7.83pt (-410,360원)  ※ 레그 12행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:44:01 | SHORT | 3 | 3m | 3 | +2.08 | +99,152 | 하드스톱(틱) |
| 09:56:00 | SHORT | 3 | 3m | 3 | -3.76 | -192,857 | 하드스톱(틱) |
| 10:15:00 | SHORT | 3 | 3m | 3 | -4.17 | -212,856 | 하드스톱(틱) |
| 10:55:00 | SHORT | 1 | 3m | 1 | +0.64 | +30,396 | 하드스톱(틱) |
| 11:11:01 | SHORT | 1 | 5m | 1 | -3.14 | -158,591 | 하드스톱(틱) |
| 11:34:00 | SHORT | 1 | 5m | 1 | +0.52 | +24,396 | 하드스톱(틱) |

**청산 레그 12행** (부분청산 6 · 전량청산 6)

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

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×7, `손절1차 조기축소`×4, `TP1 부분청산 33%`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 6/6건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -410,360 = 포지션합 -410,360 → OK · `[청산 완료]` 6건 = 조립 포지션 6건 → OK

### 진입 6건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:44:01 | SHORT | 3 | 1077.32 | 3m | trend |
| 09:56:00 | SHORT | 3 | 1078.94 | 3m | trend |
| 10:15:00 | SHORT | 3 | 1079.36 | 3m | neutral |
| 10:55:00 | SHORT | 1 | 1069.64 | 3m | mean-revert |
| 11:11:01 | SHORT | 1 | 1060.7 | 5m | mean-revert |
| 11:34:00 | SHORT | 1 | 1069.62 | 5m | neutral |

계약수 분포 — 1계약×3, 3계약×3

등급 분포 — `A급(원시C)`×5, `C급`×1

**진입한 건들의 체크리스트 미통과 항목** — `ofi`×4, `fore`×4, `cvd`×3, `chas`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×15, **3계약**×7

실제 진입 계약수 — **1계약**×3, **3계약**×3

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×22

### 차단 사유 63건 · 30종

| 건수 | 사유 |
|---|---|
| 20 | 등급X — 미통과 항목: 2_confidence |
| 6 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 6 | JointGateBlock — meta=0.50 tox=0.70 joint=0.350 < 0.50 |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
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
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 7_prev_bar |

**체크리스트 미통과 항목 누적** — `2_confidence`×20, `3_vwap`×14, `6_foreign`×14, `4_cvd`×10, `7_prev_bar`×10, `5_ofi`×5

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 3건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 19건 · 최대 20985ms · 5초 초과 5건

상위 — 20985ms, 7500ms, 7359ms, 6187ms, 5625ms, 4718ms, 4407ms, 4219ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:06 | 7500ms | 2549ms | **4951ms (66%)** |
| 09:05:05 | 6187ms | 472ms | **5715ms (92%)** |
| 11:06:06 | 5625ms | 610ms | **5015ms (89%)** |
| 11:16:22 | 20985ms | 671ms | **20314ms (97%)** |
| 12:09:07 | 7359ms | 433ms | **6926ms (94%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260824_WARN.log`
```
--- ConstOut ×3(표본)
09:35:00 2026-08-24 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:29:00 2026-08-24 10:29:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:24:00 2026-08-24 11:24:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×3(표본)
09:57:09 2026-08-24 09:57:09 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:15:52 2026-08-24 10:15:52 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:14:36 2026-08-24 11:14:36 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:48:11 2026-08-24 09:48:11 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:50:11)
09:48:11 2026-08-24 09:48:11 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 09:50:11)
10:03:04 2026-08-24 10:03:04 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:05:04)
10:03:04 2026-08-24 10:03:04 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:05:04)
--- [SHAP] 슬로우 ×1(표본)
12:24:01 2026-08-24 12:24:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1177ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
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
```

### `logs/20260824_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:02 2026-08-24 09:00:02 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4310 (conf_floor=0.330, min_conf=0.431, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×6(표본)
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

- 이 로그 생존구간: 08:41 ~ 12:15

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260824_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:20 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 9 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:55:21 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 59 | 09:56:00 [WARNING] atr=2.5657 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | … |
| 12:00 | 장중 중간점 | 4 | 11:59:04 [WARNING] _tick_header 간격 4078ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4078 band=… |

- 이 로그 생존구간: 08:41 ~ 12:24

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260824_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:48 [INFO] 활성화 | file=logs\crash_fault.log PID=25592 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 128 | 08:49:02 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 262 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 170 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:26

**매분 루프 커버리지 09:00~15:10: 207/371분 (55.8%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:27 | 15:10 | 164 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260824_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:20 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0118) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 130 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0311) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 231 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0285) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 137 | 09:54:00 [WARNING] 신뢰도 미달 34.1% < 38.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 124 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=11m max_z=+4.07(ofi_reversal_speed) extreme=1 |

- 이 로그 생존구간: 08:40 ~ 12:26

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
| **오늘 20260824** | **12:26** | 로그 본문 |

- 델타 **-276분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 이상점 6건 (P0 0 / P1 1 / P2 5) — 신규 결함 0건
### Fix 계획 (전부 장후 적용 대상 — 오늘 미적용)
### 고도화 (당일 관측 근거)
### 함정 점검 (SKILL.md §0)
### 규약 메모
### 검증
### [세션 내 자체발생 1건 — 이상점 1-7] 이 점검 세션이 `.git/index.lock`을 남겼다
### [자체 정정 1건 — 이상점 1-1 근거 명령]
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
델 mtime뿐.

### [세션 내 자체발생 1건 — 이상점 1-7] 이 점검 세션이 `.git/index.lock`을 남겼다

**증상**: `.git/index.lock` 0바이트, 생성 **2026-08-24 09:13:46**. 샌드박스에서
`rm -f` → `Operation not permitted`. `git_lock_guard.py --check` = `HOLD`(나이 77초 < 600초).

**락 이전 상태 확정**: 오늘 증거 다이제스트 §2(08:59:37 생성)가 `인덱스락 없음`을 기록.
⇒ 08:59:37 **이후, 점검 세션 안에서** 생겼다.

**원인 — 483차 후속2가 시험하지 않은 두 번째 경로**:

| 항목 | 483차 후속2 실험 | 오늘 실측 |
|---|---|---|
| 실행 위치 | Windows 로컬 | **Cowork 리눅스 샌드박스**(마운트 경유) |
| 실패 방식 | `taskkill /F` 강제 종료 | **중단 없음** — 명령 정상 종료 |
| 락 잔존 이유 | 인덱스 쓰기 중 사망 | **`unlink` 권한 거부**(mount) |
| 대상 명령 | `git status` / `git add -A` | **`git diff`**(stat 캐시 갱신 시도) |

🔴 **483차 결론(`git status` 잔존 0/5, 수집기 무죄)을 반증하지 않는다.** 그 실험은
Windows·강제종료·`status` 조합이었고 유효하다. 오늘 것은 **다른 발생 경로**다.
483차가 *"🔴 주체는 확정하지 못했다"* 로 남긴 칸에 대한 직접 증거다.

**정황 — 08-21 사고와 시각 일치 (가설, 미확정)**:
futures 락 08-21 **08:59:53.65** vs 미륵이 장전 점검 다이제스트 생성 **08:59:50**(mtime 08:59:55).
fuoption 락 **09:08:53.87** — 483차가 *"9분 간격 두 저장소 = 프로젝트를 돌아가며 같은 작업"* 로
읽은 패턴이 **두 예약 점검(미륵이 선물 / 마흐디 옵션)이 9분 간격으로 도는 것**과 부합한다.
⚠ **확정 금지** — 오늘 것은 직접 증거, 08-21 것은 시각 일치뿐이다.
확정된 것은 *"483차가 `diff`·`log`·`rev-list`·`ls-files` × 샌드박스 마운트 조합을
시험하지 않았다"* 는 사실뿐이다.

**결정 — P1 F-F (장후 적용)**:
① `--no-optional-locks`를 수집기 한정이 아니라 **세션 규약으로 승격**. `SKILL.md` 절차부에
   `git diff`·`git log`·`git rev-list`·`git ls-files` 를 **명시**한다(오늘 범인은 `status`가 아니다).
② 수집기가 실행 전후 `.git/index.lock` 존재를 **비교**해, 없다가 생겼으면 §2에 경고.
   현행 §2는 **수집 시작 시점**만 보므로 같은 세션 후반 락을 구조적으로 못 본다.
③ `SKILL.md` 자체 검증에 `[ ] 세션 종료 시 index.lock 미잔존` 체크박스.

**Why**: 483차가 본질로 지목한 것은 락이 아니라 **「53시간 무증상」**이다
(`git status` rc=0 조용히 통과 / `commit` rc=128). 생성 경로를 못 막으면 그 무증상이 반복되고,
지난번처럼 「당일 커밋 0건」이 *안 했다*로 오귀속된다 — 계측 4원칙 ②.
✅ 오귀속 재발은 483차 P0-2가 이미 막는다(`⚠ 인덱스락 잔존으로 커밋 불가 상태였음. 미조치가 아니다`).

**How to apply**: 사용자가 Windows에서 `python scripts\git_lock_guard.py --check` →
`STALE`이면 `--reclaim`. `HOLD`면 09:24 이후 재판정.
🔴 `del .git\index.lock` 직접 실행 금지 — 3중 조건(0바이트 · 나이>600s · git 프로세스 0)
미확인 상태로 지우면 실행 중인 git의 인덱스를 깨뜨린다.

**검증**: 다음 장전 점검 종료 후 `.git/index.lock` 미존재. 존재 시 §2가 자동 경고(F-F ②).

### [자체 정정 1건 — 이상점 1-1 근거 명령]

초판 리포트가 `git diff -w --name-only | grep -cE "\.py$"` = 0 을 인용했으나 **틀렸다.**
`--name-only` 는 **`-w` 를 적용하지 않는다** — 같은 시점 실측 `--name-only` **457개
(그중 `.py` 244개)** vs `--numstat`/`--stat` **4개**. 결론(실질 4건 · `.py` 0건)은 불변이며
`git diff -w --numstat | awk '{print $3}' | grep -cE "\.py$"` = **0** 으로 재확인했다.
리포트 인용을 수정하고 F-D 구현 시 명령을 `--numstat`/`--stat` 으로 **고정**하도록 명기.
⚠ 앞으로 실질 변경 수를 셀 때 `--name-only` 를 쓰지 말 것.

```

</details>

### dev_memory/NEXT_TODO.md — 1.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 폐기 처리
## 2026-08-24 (MW0601 490차 — 장전 점검) — 분석만, 코드 0건
### Fix (장후 적용 대상 — 오늘 미적용)
### 고도화 (당일 관측 근거)
### 오늘 관측 항목 (장중·장후가 닫을 것)
### 이월 처분 (전 거래일 장전 몫)
### 규약 메모
### 세션 내 자체발생 (2026-08-24 490차)
```

미완료 체크박스 **1829건** (끝에서 30건)
```
- [ ] **N-6 (2026-08-28 금) `[EntryHorizonRecal]` 6주차** — 하락 추세 지속이면
- [ ] **N-7 (2026-08-28 금) 월간 로그 정리** — P2-H 미적용이면 **또 `FAIL(rc=1)`이 나와야
- [ ] **N-8 (2026-08-28 금) 캠페인 [9]** — 오늘 차단 10건 resolve 후 n=37→47 근처에서
- [ ] **N-9 (2026-08-28 금) 캠페인 [46]** — 2주 연속 FAIL인지, OOS 표본 증가 시
- [ ] **N-10 (매 장후 누적) 15:10 강제청산 실집행** — 누적 **0회** 유지.
- [ ] **N-11 (다음 장후) 등급 인플레 일자단위** — 오늘 원시C→최종A **3건**
- [ ] **N-12 (다음 장전) `py37_32` 런타임 버전 (O-5 재이월)** — scipy 1.5.4 / joblib 1.1.1.
- [ ] **N-13 (다음 장전) 미커밋 실질 변경** — `git diff -w --stat` 실측치 병기.
- [ ] **O-21 (08-28 금 EOD) — 정식 판정은 자동 생성본으로.** 오늘 생성본은 스크래치
- [ ] **[50]/[51] 생산부 `dev` 자체 재구현 여부** — 소비자가 생기면(O-19 판정 필요
- [ ] **`monthly_cleanup` 장중 가드 자체 구현 여부** — `utils/analysis_db.py` 체리픽
- [ ] **P1 F-A `core_feature_health` 일별 1행 (이상점 1-3)** — `utils/db_utils.py`에 테이블
- [ ] **P2 F-B `main.py` 기동 시 `[Runtime]` 1행 (이상점 1-5 · N-12 영구 해소)** —
- [ ] **P2 F-C Cybos 투자자 탐침 COM 초기화 후 섀도 재실행 (이상점 1-6)** —
- [ ] **P2 F-D 수집기 §2·§11에 실질 변경 수·EOL 상태 병기 (이상점 1-1)** —
- [ ] **P2 F-E `CLAUDE.md:654` "모의 잔고(4.9억)" 정정** — 실측 `[Capital] 실제잔고=49,955,870원
- [ ] **고도화 ① Canary 임계 여유 로깅 (근거 1-4)** — `z경고피처=12개 (임계 12개, 여유 0개 ·
- [ ] **고도화 ② `[PreflightSummary]` 장전 자격 1행 (근거 1-B)** — branch/origin/eod_retrain/
- [ ] **고도화 ③ 다이제스트 §0 「관측 지점 프로파일」 (근거 1-1)** — 셸 종류 · `core.autocrlf` ·
- [ ] **고도화 ④ CB② 카운터팩추얼 표 — 08-27(목) 장후 선제 작성 (근거 1-2)** —
- [ ] **O-1 (장중)** 09:02:00 `[IntradayRegime] NORMAL → CRASH | day=-0.09% atr=1.00 z=5` —
- [ ] **O-2 (장후) N-4 ② 축** — `cvd_divergence`·`ofi_norm`이 실제 `[진입체크]` 체크리스트에서
- [ ] **O-3 (장중) 1-4 잔존 2종(`atr`·`avg_volume`)** 장중 `[Canary]` 재발화 여부.
- [ ] **O-4 (장중) 30m 채점 생존** — CB③의 **유일한 입력원**(절대원칙 §2·§3). 끊기면 P1 이상.
- [ ] **O-5 (장후) `[Capital]` 2행 중복 출력** — 08-18 2 / 08-19 **4** / 08-20 2 / 08-21 2 /
- [ ] **N-12 3회 연속 이월 ⬆️** — 사유 갱신: 샌드박스 문제가 아니라 **로그에 버전이 없다**.
- [ ] **CB② 기한 카운트다운** — 남은 거래일 **5**(08-24·25·26·27·28). 판정일 08-28(금).
- [ ] **`references/report_template.md` 갱신 (P2, 기등록 재확인)** — 아직 `-pre`/`-intra`/`-post`
- [ ] **🔴 사용자 조치 (오늘 중) — `.git/index.lock` 회수 (이상점 1-7)** —
- [ ] **P1 F-F 점검 세션 git 호출이 락을 남기지 못하게 한다 (이상점 1-7)** —
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
5/9999별 ① 당일 정지 발동 일수 ② 차단됐을 진입 건수 ③ **포지션 단위** 실현손익 합.
      🔴 반드시 장후 · `utils/analysis_db.py:guard_intraday()` 경유(장중 실행은 CB⑤ 자가유발).
      🔴 **청산 레그 단위 집계 금지**(417차 재인용 금지 수치 계열 재생산 방지).
      ⚠ 소수 이상치 좌우 시 372차처럼 **"근거 부족 → 유지/연기"도 정당** — 연기 시 사유·다음 기한 기록.

### 오늘 관측 항목 (장중·장후가 닫을 것)

- [ ] **O-1 (장중)** 09:02:00 `[IntradayRegime] NORMAL → CRASH | day=-0.09% atr=1.00 z=5` —
      일중 -0.09%에 z=5가 붙은 조합의 정당성. 개장 직후 ATR 표본 얕음에 의한 착시 여부.
      ⚠ 08:59 증거 수집 **이후** 관측이라 장전 다이제스트에는 없다.
- [ ] **O-2 (장후) N-4 ② 축** — `cvd_divergence`·`ofi_norm`이 실제 `[진입체크]` 체크리스트에서
      통과/미통과 어느 쪽으로 기여했는가.
- [ ] **O-3 (장중) 1-4 잔존 2종(`atr`·`avg_volume`)** 장중 `[Canary]` 재발화 여부.
- [ ] **O-4 (장중) 30m 채점 생존** — CB③의 **유일한 입력원**(절대원칙 §2·§3). 끊기면 P1 이상.
- [ ] **O-5 (장후) `[Capital]` 2행 중복 출력** — 08-18 2 / 08-19 **4** / 08-20 2 / 08-21 2 /
      08-24 2. 무해하나 `main.py:12727` 호출 경로가 2회 도는 뜻. **P2 미만 — 이상점 아님.**

### 이월 처분 (전 거래일 장전 몫)

- [x] **N-13 종결** — 미커밋 실질 변경 **4건 · 코드(.py) 0건**. 상세 이상점 1-1.
- [ ] **N-12 3회 연속 이월 ⬆️** — 사유 갱신: 샌드박스 문제가 아니라 **로그에 버전이 없다**.
      F-B로 영구 해소 예정.
- [ ] **CB② 기한 카운트다운** — 남은 거래일 **5**(08-24·25·26·27·28). 판정일 08-28(금).

### 규약 메모

- [ ] **`references/report_template.md` 갱신 (P2, 기등록 재확인)** — 아직 `-pre`/`-intra`/`-post`
      3파일 형식을 말한다. 오늘도 **대원칙 B(하루 한 파일 append)를 우선 적용**해
      `MW0601-20260824-점검리포트.md` 단일 파일로 작성했다.

### 세션 내 자체발생 (2026-08-24 490차)

- [ ] **🔴 사용자 조치 (오늘 중) — `.git/index.lock` 회수 (이상점 1-7)** —
      0바이트 · 생성 2026-08-24 09:13:46 · 이 점검 세션의 `git diff`가 남겼고 샌드박스에서
      `unlink` 권한 없음. `python scripts\git_lock_guard.py --check` → `STALE`이면 `--reclaim`.
      `HOLD`(나이<600s)면 09:24 이후 재판정. 🔴 `del` 직접 실행 금지(3중 조건 미확인 삭제는
      실행 중 git의 인덱스를 깨뜨린다). **매매 영향 0 · 커밋 봉쇄 1.**
- [ ] **P1 F-F 점검 세션 git 호출이 락을 남기지 못하게 한다 (이상점 1-7)** —
      ① `--no-optional-locks`를 수집기 한정 → **세션 규약으로 승격**. `SKILL.md` 절차부에
         `git diff`·`git log`·`git rev-list`·`git ls-files` **명시**(오늘 범인은 `status` 아님).
      ② `collect_evidence.py`가 실행 **전후** `.git/index.lock` 존재를 비교해 신규 생성 시 §2 경고.
         현행 §2는 수집 **시작 시점**만 봐서 같은 세션 후반 락을 구조적으로 못 본다.
      ③ `SKILL.md` 자체 검증에 `[ ] 세션 종료 시 index.lock 미잔존` 체크박스.
      ⚠ 483차 후속2의 재현 실험(Windows·강제종료·`git status` → 잔존 0/5)을 **반증하지 않는다**.
         막는 것은 **샌드박스 마운트 · 중단 없음 · unlink 거부**라는 다른 경로.
      검증: 다음 장전 종료 후 `.git/index.lock` 미존재.
- [x] **자체 정정 — 이상점 1-1 근거 명령** — `git diff -w --name-only` 는 `-w` 미적용
      (실측 457개 / `.py` 244개). 실질 변경은 반드시 **`--numstat`/`--stat`**(4개, `.py` 0개).
      리포트 수정 완료. **F-D 구현 시 명령 고정할 것.**

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

### `data/heartbeat_MW0601_20260824.json` — 244B · 08-24 12:26:27
```json
{
 "pid": 25592,
 "written_at": "2026-08-24T12:26:27",
 "beat_epoch": 1787541985.2454185,
 "beat_age_sec": 2.0,
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

### `docs/정기점검/매일점검` — 66개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260824-점검리포트.md` | 58.6KB | 08-24 09:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260824_pre.md` | 47.4KB | 08-24 08:59 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.0KB | 08-23 16:51 |
| `docs/정기점검/매일점검/MW0601-20260821-점검리포트.md` | 208.7KB | 08-21 16:54 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_post.md` | 74.4KB | 08-21 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_intra.md` | 57.0KB | 08-21 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_pre.md` | 46.8KB | 08-21 08:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_pre.md` | 49.0KB | 08-20 22:24 |

### `docs/정기점검/금요일점검` — 58개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.2KB | 08-23 22:09 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260821.md` | 4.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260821.json` | 2.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md` | 26.2KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json` | 34.4KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json` | 91.9KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `.git/index.lock` **스테일 잔존** (0바이트 · 3.2시간 · git 프로세스 0개) — 이 저장소는 **커밋 불가** 상태다. `git status` 는 rc=0 으로 조용히 통과하므로 다른 어떤 계측에도 안 걸린다. 3중 조건 확인 후 제거할 것
2. `logs/20260824_WARN.log`: ERROR 이상 1건
3. `logs/20260824_SYSTEM.log`: 매분 루프 커버리지 207/371분 (55.8%) — 루프가 빠진 구간이 있다
4. `logs/20260824_SYSTEM.log`: 12:27~15:10 **연속 164분 매분 루프 기록 없음**
5. 메인 스레드 정지 5초 초과 **5건** (최대 20985ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260824_WARN.log`: **ConstOut** 3건(표본)
7. `logs/20260824_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20260824_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20260824_SIGNAL.log`: **ConstOut** 6건(표본)
10. `logs/20260824_LEARNING.log`: **축퇴** 8건(표본)
11. 미커밋 변경 488건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260824*.log` (Windows) / `grep 강제청산 logs/*20260824*.log`*