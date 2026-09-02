# 미륵이 증거 다이제스트 — 2026-09-02 / INTRA

- 생성 2026-09-02 12:26:37 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/wizardly-laughing-wozniak/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260902` · `2026-09-02` · `260902` · `0902`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **18개** 파일 · 18개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260902.log` | 125B | 09-02 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260902.log` | 140B | 09-02 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260902.json` | 243B | 09-02 12:26 |
| `launcher_{DATE}_084001_7533.log` | 1 | `logs/Mireuk_batch/launcher_20260902_084001_7533.log` | 933.7KB | 09-02 12:26 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260902.log` | 11.4KB | 09-02 11:33 |
| `retrain_intraday_{DATE}_093600.log` | 1 | `logs/retrain_intraday_20260902_093600.log` | 2.7KB | 09-02 09:36 |
| `retrain_intraday_{DATE}_120001.log` | 1 | `logs/retrain_intraday_20260902_120001.log` | 2.7KB | 09-02 12:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260902_DATA.log` | 183.1KB | 09-02 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260902_DEBUG.log` | 131.0KB | 09-02 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260902_HEALTH.log` | 2.5KB | 09-02 12:02 |
| `{DATE}_HOGA.log` | 1 | `logs/20260902_HOGA.log` | 27.7MB | 09-02 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260902_LEARNING.log` | 180.7KB | 09-02 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260902_MICRO.log` | 561.8KB | 09-02 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260902_PROBE.log` | 57.5KB | 09-02 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260902_SIGNAL.log` | 344.0KB | 09-02 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260902_SYSTEM.log` | 458.0KB | 09-02 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260902_TRADE.log` | 8.1KB | 09-02 10:51 |
| `{DATE}_WARN.log` | 1 | `logs/20260902_WARN.log` | 44.8KB | 09-02 12:16 |

## 2. 코드·커밋 상태

- HEAD `a3f70ab` · 브랜치 `v9-dev` · 미커밋 518건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 514건 (추적변경 516 · 미추적 2 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M .claude/commands/dailycheck.md
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
 M config/dailycheck_targets.json
… 외 478건
```

**당일(2026-09-02) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
a3f70ab [MW0601] 514차 후속: 장후 자동조치 — F-A(P1-3) · F-B(고도화①) · F-C(고도화②/P5-신규)
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
db48586 [MW0601] 507차 후속: 리포트 제8부에 커밋 해시 기입
2d6a1bb [MW0601] 507차 후속: 장후 자동조치 — F-7·F-8·F-11·F-12·F-14 + G-4·G-5
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
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
| `FUTURES_COMMISSION_RATE` | `_BROKER_SPEC["one_way_commission_rate"]` | `_BROKER_SPEC["one_way_commission_rate"]` | 일치 | 495차 후속 — 로그인 채널 감지로 **파생**. 숫자 리터럴로 되돌아가면 회귀(2026-05-11~08-25 6개월간 1/6.54 사고). 실제 요율은 채널… |
| `FUTURES_COMMISSION_RATE_EFFECTIVE_FROM` | `_BROKER_SPEC["effective_from"]` | `_BROKER_SPEC["effective_from"]` | 일치 | 시계열 불연속 경계 — 이 날짜 앞뒤 손익 직접 비교 금지의 근거(461차 mdd_pct 유형) |
| `COST_MODEL_COMMISSION_RATE` | `0.000015` | `0.000015` | 일치 | 캠페인·섀도 계측 전용 요율. 라이브와 **의도적으로 갈라져 있다**(493차 F-3 핀). 주간회의 승인 시 라이브와 같은 값으로 교체 — 그때 이 기대값도 … |
| `COST_MODEL_COMMISSION_RATE_PINNED` | `True` | `True` | 일치 | 라이브와 계측이 갈린 상태임을 매일 명시. 승인 교체 후에도 True면 그것이 이상 |
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

_본문 미열람(설정): `20260902_HOGA.log` 27.7MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `20260902_MICRO.log`, `20260902_DATA.log`, `20260902_PROBE.log`, `launcher_20260902_084001_7533.log`, `20260902_DEBUG.log`, `mainstall_traceback_20260902.log`, `freeze_sentinel_20260902.log`, `force_flat_guard_20260902.log`_

### `logs/20260902_TRADE.log` — 8.1KB · 64행 · 최종 10:51:02

- 형식 평문 · 시각 인식 64행 · WARNING=2, INFO=62

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-02 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-02 08:41:09 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-09-02 08:41:09 [WARNING] TRADE: [Position] 브로커 기준 동기화: LONG 3계약 @ 1076.0 | 손절=1075.25
2026-09-02 08:45:09 [INFO] TRADE: [TickStop-S0C] 하드스톱(틱) LONG 3ct tick=1041.44 stop=1075.25 → 주문 전송
  …
2026-09-02 10:51:01 [INFO] TRADE: [주문요청] 하드스톱 청산 SHORT 1계약 @ 1040.19
2026-09-02 10:51:01 [INFO] TRADE: [Chejan] 상태=접수 주문번호=1987 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-02 10:51:02 [INFO] TRADE: [Chejan] 상태=체결 주문번호=1987 code=A0569 방향=LONG 체결=1 미체결=0
2026-09-02 10:51:02 [INFO] TRADE: [Position] 체결청산 SHORT @ 1039.74 | PnL=+0.45pt (+12,295원) | 하드스톱
2026-09-02 10:51:02 [INFO] TRADE: [청산 완료] PnL=+0.45pt (+12,295원) | 포지션 합계 +41,591원 (레그 2)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 1 | 08:41:09 | 08:41:09 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `Position` | 1 | 08:41:09 | 08:41:09 | 브로커 기준 동기화: LONG 3계약 @ 1076.0 | 손절=1075.25 |

**채널** — `TRADE`×64

**컴포넌트 상위 15** — `Chejan`×18, `Position`×13, `주문요청`×7, `Sizer`×4, `ProfitGuard`×3, `청산 완료`×3, `TickStop-S0C`×2, `체결청산-부분`×2, `진입체크`×2, `체결진입`×2, `체결진입보정`×2, `TickTP1`×2, `TP1 부분청산`×2, `PositionFallback`×1, `JointGateBlock 차단`×1

### `logs/20260902_WARN.log` — 44.8KB · 203행 · 최종 12:16:00

- 형식 평문 · 시각 인식 203행 · CRITICAL=1, ERROR=1, WARNING=201

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-09-02 08:41:09 [WARNING] SYSTEM: [BrokerSync] balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '42172727', '총평가손익': '42172727', '실현손익': '0', '총평가': '0.00', '총평가수익률': '42172727', '추정자산': '-1144000'}
2026-09-02 08:41:09 [WARNING] SYSTEM: [BrokerSync] startup sync raw rows=1 nonempty_rows=1 all_blank_rows=False record_name='CpTd0723' prev_next='' rows=[{'종목코드': 'A0569', '종목명': '¹Ì´ÏÄÚ½ºÇÇ F 202609', '구분': '매수', '매매구분': '매수', '잔고수량': '3', '청산가능': '3', '평균가': '1076.0', '매입단가': '1076.0', '현재가': '',…
  …
2026-09-02 12:01:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 3069ms 경고 (기준 1000ms)
2026-09-02 12:01:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3516 band=INFO since_pipe_s=0.0
2026-09-02 12:02:01 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.35+1.00 ≥ 2 (latency=3069ms quality=1.00 cache=0s exc10m=0) | cause=S0(2762ms)
2026-09-02 12:06:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4297 band=INFO since_pipe_s=0.0
2026-09-02 12:16:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.236% (임계 ±0.150%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `BrokerSync` | 1 | 08:41:09 | 08:41:09 | startup sync 완료: FLAT -> LONG 3계약 @ 1076.00 |
| ERROR | `LiveDBG` | 1 | 11:28:57 | 11:28:57 | _tick_header 간격 56875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=56875 band=ALERT since_pipe_s=0.1 |

<details><summary>CRITICAL/BrokerSync 원문 1건</summary>

```
2026-09-02 08:41:09 [CRITICAL] SYSTEM: [BrokerSync] startup sync 완료: FLAT -> LONG 3계약 @ 1076.00
```

</details>

<details><summary>ERROR/LiveDBG 원문 1건</summary>

```
2026-09-02 11:28:57 [ERROR] SYSTEM: [LiveDBG] _tick_header 간격 56875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=56875 band=ALERT since_pipe_s=0.1
```

</details>

**WARNING — 태그 29종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 55 | 08:41:09 | 12:06:04 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 18 | 08:45:10 | 10:51:02 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='101' | pending='EXIT_FULL:LONG qty=3 filled=0 order_no=? reason=하드스톱(틱) req_at=08:45:09.952' |… |
| `ChejanMatch` | 18 | 08:45:10 | 10:51:02 | order_no='101' | pending='EXIT_FULL:LONG qty=3 filled=0 order_no=101 reason=하드스톱(틱) req_at=08:45:09.952' | pending_matched=True |
| `PendingOrder` | 14 | 08:45:09 | 10:51:02 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1075.25, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `PipePerf` | 10 | 09:00:02 | 12:01:03 | total=2491ms | S0=3ms S1=10ms S2=0ms S3=0ms S4=92ms S5=863ms S6=1347ms S7=153ms S8=24ms |
| `Health` | 10 | 09:00:02 | 12:01:03 | level=WARNING degraded=OFF | latency=2491ms | quality=0.86 | cache_age=46s | exceptions_10m=1 |
| `CB⑤` | 10 | 09:00:03 | 12:01:03 | 파이프라인 2491ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 7 | 09:11:00 | 12:16:00 | 5분 누적 수익률 +0.367% (임계 ±0.367%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ExitCooldown` | 6 | 08:45:10 | 10:51:02 | 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10) |
| `MainStallTrace` | 6 | 09:00:10 | 11:33:05 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260902.log |
| `ExitFillFlow` | 5 | 08:45:10 | 10:51:02 | after='LONG 2계약 @ 1076.00' | before='LONG 3계약 @ 1076.00' | fill_price=1040.74 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:LONG qty=3 filled=1 order_no=101 reason=하드스톱(틱) req_at=08:45:09.952' | reason='하드스톱(틱)' |
| `HealthPolicy` | 5 | 09:01:02 | 12:02:01 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2491ms quality=0.86 cache=0s exc10m=1) | cause=S6(1347ms) |

**채널** — `SYSTEM`×193, `HEALTH`×10

**컴포넌트 상위 15** — `LiveDBG`×56, `ChejanFlow`×18, `ChejanMatch`×18, `PendingOrder`×14, `PipePerf`×10, `Health`×10, `CB⑤`×10, `ScalerRefresh`×7, `ExitCooldown`×6, `MainStallTrace`×6, `BrokerSync`×5, `ExitFillFlow`×5, `HealthPolicy`×5, `EntryFillFlow`×4, `ExitSendOrderResult`×3

### `logs/20260902_SYSTEM.log` — 458.0KB · 3308행 · 최종 12:26:27

- 형식 평문 · 시각 인식 3301행 · INFO=3301, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:33 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.9MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-09-02 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=2768 | 행감지=30s all_threads=True
2026-09-02 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-02 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-02 08:40:49 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-02 12:27:01 [INFO] SYSTEM: [PipePerf][DBG] total=365ms | S0=21ms S1=22ms S2=15ms S3=0ms S4=58ms S5=195ms S6=41ms S7=11ms S8=2ms
2026-09-02 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-824,foreign:-6630,institution:+7160}
2026-09-02 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-824,foreign:-6630,institution:+7160}
2026-09-02 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-95530 nonarb=-1011793
2026-09-02 12:27:09 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=-95530 nonarb=-1011793
```

</details>

**채널** — `SYSTEM`×3301

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×714, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×220, `S6Detail`×208, `PipePerf`×208, `MicroRegime`×62, `System`×59, `RegimeFingerprint`×38, `CybosEvent`×36, `BalanceUI`×34, `OptionChain`×23, `CybosSub`×21

### `logs/20260902_SIGNAL.log` — 344.0KB · 3002행 · 최종 12:26:00

- 형식 평문 · 시각 인식 3002행 · WARNING=1321, INFO=1681

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
  …
2026-09-02 12:27:01 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-09-02 12:27:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=40.9% grade=X regime=NEUTRAL
2026-09-02 12:27:01 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 5회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-09-02 12:27:01 [INFO] SIGNAL: 앙상블: dir=+0 conf=40.9% grade=X micro=횡보장
2026-09-02 12:27:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.409<mc0.620)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 936 | 09:00:04 | 12:16:01 | 1m 'macro_krw_chg' scale=0.0502 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 108 | 09:01:01 | 12:06:00 | 1m 극단 z-score 4개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 102 | 09:01:01 | 12:06:00 | ts=09:00 horizon=1m age=1m max_z=+7.79(va_bandwidth) extreme=4 |
| `Checklist` | 80 | 09:06:00 | 12:18:03 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `ScalerRefresh` | 48 | 08:45:09 | 08:59:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0327) → identity(0,1) 강제 (FLAT 100% 방지) |
| `WeightCollapse` | 42 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 3 | 09:35:00 | 11:59:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 2 | 09:00:01 | 10:55:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×3002

**컴포넌트 상위 15** — `ScalerFloor`×996, `SIGNAL`×416, `Ensemble`×209, `FQAdj`×205, `ZeroDiag`×196, `MetaGate`×162, `Model`×126, `ScalerMonitor`×102, `Checklist`×87, `ScalerRefresh`×79, `ATR-Horizon`×77, `MicroRegime`×62, `InstabilityGate`×51, `차단`×44, `WeightCollapse`×42

### `logs/20260902_LEARNING.log` — 180.7KB · 1680행 · 최종 12:26:00

- 형식 평문 · 시각 인식 1680행 · WARNING=154, INFO=1526

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00008 auc=0.274 out_max=0.0875 (기준 auc<0.53 and span<0.020, 기저율=0.0875 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00217 auc=0.298 out_max=0.2759 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00111 auc=0.595 out_max=0.1796 (n=95) → 보정 재적용
  …
2026-09-02 12:27:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0573% buf_n=20 nonzero=20 prev_p=1039.98 cur_p=1039.44
2026-09-02 12:27:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=33.3% 예측=UP 실제=DN)
2026-09-02 12:27:00 [INFO] LEARNING: ✓ 3m 예측 적중 (conf=36.9% FL)
2026-09-02 12:27:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=36.1% 예측=DN 실제=FL)
2026-09-02 12:27:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=16.7%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 154 | 08:40:52 | 12:10:00 | 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1680

**컴포넌트 상위 15** — `LEARNING`×667, `Calibration`×300, `SGD`×208, `sigma`×195, `Bias⚠`×99, `Bias`×73, `MetaConf`×41, `ScalerWarmup`×31, `OnlineLearner`×31, `BiasReset`×11, `SHAP`×7, `GBM-64`×4, `GBM`×4, `RF`×3, `ExtremityCorrector`×2

### `logs/20260902_HEALTH.log` — 2.5KB · 18행 · 최종 12:02:01

- 형식 평문 · 시각 인식 18행 · WARNING=10, INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2491ms | quality=0.86 | cache_age=46s | exceptions_10m=1
2026-09-02 09:01:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2157ms | quality=0.86 | cache_age=106s | exceptions_10m=1
2026-09-02 09:02:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=447ms | quality=0.74 | cache_age=164s | exceptions_10m=1
2026-09-02 09:22:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1163ms | quality=1.00 | cache_age=78s | exceptions_10m=0
2026-09-02 09:23:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=348ms | quality=1.00 | cache_age=137s | exceptions_10m=0
  …
2026-09-02 11:57:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=279ms | quality=1.00 | cache_age=184s | exceptions_10m=0
2026-09-02 11:58:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=268ms | quality=1.00 | cache_age=60s | exceptions_10m=0
2026-09-02 12:00:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=392ms | quality=1.00 | cache_age=180s | exceptions_10m=0 [GBM재학습중→lat임계 5000/10000ms]
2026-09-02 12:01:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3069ms | quality=1.00 | cache_age=44s | exceptions_10m=0
2026-09-02 12:02:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=346ms | quality=1.00 | cache_age=102s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 10 | 09:00:02 | 12:01:03 | level=WARNING degraded=OFF | latency=2491ms | quality=0.86 | cache_age=46s | exceptions_10m=1 |

**채널** — `HEALTH`×18

**컴포넌트 상위 15** — `Health`×17, `HealthTrend`×1

### `logs/retrain_intraday_20260902_093600.log` — 2.7KB · 21행 · 최종 09:36:22

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-02 09:36:00,784 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_1ca1a6d7.json
2026-09-02 09:36:03,859 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-02 09:36:22,309 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-02 09:36:22,310 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-02 09:36:22,310 [INFO] LEARNING: [Retrain] 완료 | 18.5초 | 성공=1/1 호라이즌
2026-09-02 09:36:22,311 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.5s 데이터=4800행
2026-09-02 09:36:22,312 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_1ca1a6d7.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260902_120001.log` — 2.7KB · 21행 · 최종 12:00:23

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 12:00:01,156 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-02 12:00:01,157 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-02 12:00:01,157 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-02 12:00:01,157 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_85fa56b4.json
2026-09-02 12:00:03,998 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-02 12:00:23,263 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-02 12:00:23,264 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-02 12:00:23,264 [INFO] LEARNING: [Retrain] 완료 | 19.3초 | 성공=1/1 호라이즌
2026-09-02 12:00:23,265 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.1s 데이터=4800행
2026-09-02 12:00:23,266 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_85fa56b4.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) — **엔진** | 2 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 3 |
| 차단(`[차단]`) | 44 |
| 사이저 호출(`[Sizer]`) | 4 |

### 포지션 2건 · 승 1 (50%) · 합계 +1.54pt (+36,014원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:19:00 | 엔진 | LONG | 2 | 1m | 2 | +0.30 | -5,576 | 하드스톱(틱) |
| 10:49:00 | 엔진 | SHORT | 2 | 3m | 2 | +1.24 | +41,590 | 하드스톱 |

**청산 레그 4행** (부분청산 4 · 전량청산 3)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:21:08 | 부분 | 1 | +0.33 | +6,212 | TP1 부분청산 33% |
| 10:21:18 | 전량 | 1 | -0.03 | -11,788 | 하드스톱(틱) |
| 10:50:16 | 부분 | 1 | +0.79 | +29,295 | TP1 부분청산 33% |
| 10:51:02 | 전량 | 1 | +0.45 | +12,295 | 하드스톱 |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱(틱)`×1, `하드스톱`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 2/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -5,263,654 = 포지션합 +36,014 → **불일치 ⚠** · `[청산 완료]` 3건 = 조립 포지션 2건 → **불일치 ⚠** · **귀속 실패 레그 3행 ⚠**(진입 로그 없는 이월 포지션 가능)

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:19:00 | LONG | 2 | 1048.54 | 1m | mean-revert |
| 10:49:00 | SHORT | 2 | 1040.2 | 3m | mean-revert |

계약수 분포 — 2계약×2

등급 분포 — `A급(원시C)`×1, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `risk`×2, `cvd`×1, `fore`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1, **3계약**×3

실제 진입 계약수 — **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×4

### 차단 사유 44건 · 15종

| 건수 | 사유 |
|---|---|
| 28 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 9_risk |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 9_risk |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.3pt > ATR×5.0=10.1pt (시가=1040.10 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.0pt > ATR×5.0=11.0pt (시가=1040.10 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.1pt > ATR×5.0=10.2pt (시가=1040.10 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar, 9_risk |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.0pt > ATR×5.0=9.8pt (시가=1040.10 반등위험) |
| 1 | 청산 후 쿨다운 — 77초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 17초 후 재진입 가능 |
| 1 | JointGateBlock — meta=0.50 tox=0.70 joint=0.352 < 0.50 |
| 1 | 청산 후 쿨다운 — 1초 후 재진입 가능 |
| 1 | ATR 0.99pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | ATR 0.93pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |

**체크리스트 미통과 항목 누적** — `2_confidence`×28, `3_vwap`×5, `9_risk`×5, `5_ofi`×3, `4_cvd`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 17건 · 최대 56875ms · 5초 초과 6건

상위 — 56875ms, 10953ms, 7375ms, 5562ms, 5047ms, 5031ms, 4468ms, 4297ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:10 | 10953ms | 2491ms | **8462ms (77%)** |
| 09:01:05 | 5562ms | 2491ms | **3071ms (55%)** |
| 11:26:07 | 7375ms | 713ms | **6662ms (90%)** |
| 11:27:04 | 5047ms | 713ms | **4334ms (86%)** |
| 11:28:57 | 56875ms | 573ms | **56302ms (99%)** |
| 11:33:05 | 5031ms | 339ms | **4692ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260902_WARN.log`
```
--- ConstOut ×2(표본)
09:35:00 2026-09-02 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:59:00 2026-09-02 11:59:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×4(표본)
09:00:10 2026-09-02 09:00:10 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260902.log
11:26:07 2026-09-02 11:26:07 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260902.log
11:28:57 2026-09-02 11:28:57 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260902.log
11:33:05 2026-09-02 11:33:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260902.log
--- [CB] ×2(표본)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:21:18 2026-09-02 10:21:18 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×6(표본)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10)
10:21:18 2026-09-02 10:21:18 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:24:18)
10:21:18 2026-09-02 10:21:18 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:24:18)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-09-02 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3250 band=INFO since_pipe_s=NA
09:00:10 2026-09-02 09:00:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 10953ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=10953 band=WARN since_pipe_s=0.2
09:01:05 2026-09-02 09:01:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 5562ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=5562 band=WARN since_pipe_s=0.1
09:01:36 2026-09-02 09:01:36 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2640ms — 메인 스레드 블로킹 발생 | pipe_elapsed=30 watchdog_alerted=[] | [MainStall] stall_ms=2640 band=INFO since_pipe_s=31.4
```

### `logs/20260902_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-09-02 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-09-02 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-09-02 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=90ms fit=39ms total=150ms
09:36:00 2026-09-02 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:00 2026-09-02 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-09-02 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:11:00 2026-09-02 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:17:00 2026-09-02 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20260902_SIGNAL.log`
```
--- ConfFloorGuard ×3(표본)
09:00:01 2026-09-02 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:49:00 2026-09-02 10:49:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3807 ≥ 필요 0.3720
10:55:00 2026-09-02 10:55:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3715 < 필요 0.3720 (conf_floor=0.330, min_conf=0.372, span=0.0135). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-09-02 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-09-02 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-09-02 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:02 2026-09-02 09:37:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-02 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-09-02 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-09-02 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-09-02 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.2% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
--- 안전망 ×8(표본)
09:07:00 2026-09-02 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-02 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-02 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-02 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260902_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:52 2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00008 auc=0.274 out_max=0.0875 (기준 auc<0.53 and span<0.020, 기저율=0.0875 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00217 auc=0.298 out_max=0.2759 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
08:40:52 2026-09-02 08:40:52 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00111 auc=0.595 out_max=0.1796 (n=95) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260902_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:09 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 … |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:52:19 [INFO] 설정 업데이트 완료 |

- 이 로그 생존구간: 08:41 ~ 10:51

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260902_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 33 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 22 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 24 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 12:00 | 장중 중간점 | 12 | 11:54:00 [WARNING] 5분 누적 수익률 -0.240% (임계 ±0.166%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |

- 이 로그 생존구간: 08:41 ~ 12:16

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260902_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:33 [INFO] 로테이션 — 8.9MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 130 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 187 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 199 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 184 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260902_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:09 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0327) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 124 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0456) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0446) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 116 | 09:55:01 [WARNING] 신뢰도 미달 31.7% < 38.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 229 | 11:54:00 [WARNING] ts=11:53 horizon=1m age=24m max_z=+4.88(cancel_add_ratio) extreme=1 |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260901 | 15:40 | 로그 본문 |
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| 20260827 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260902** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 원인 — 09-01 1-6과 동일 뿌리, 오늘은 결과만 실현됐다
### 결정 — 코드를 바꾸지 않는다(장전 세션 규약)
### Why
### How to apply
### 계측 4원칙 적용
### 부가 관측 — 511차 Fix(청산 주문 거부 대응) 첫 라이브 확인
### 라이브 미검증 / 이월
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
터, F-B 는 다음 거래일 15:20 부터 발화한다.
오늘 돌고 있는 프로세스·가드는 구코드다.

---

## 2026-09-02 (MW0601 515차 — 장전 점검: 09-01 이상점 1-6이 오늘 아침 -530만원 실현손실로 귀결)

**계기**: 예약 장전 점검(08:57 KST). 09-01 장후 리포트가 P0(이상점 1-6)로 등록한
"15:34:46 원인불명 매수 3계약, 청산 시도 없이 밤새 보유"가 오늘 08:40 재기동 시점까지
정리되지 않은 상태로 확인됐다.

### 증상

- `08:41:09 [CRITICAL] [BrokerSync] startup sync 완료: FLAT -> LONG 3계약 @ 1076.00`
- `08:45:09 [TickStop-S0C] 하드스톱(틱) LONG 3ct tick=1041.44 stop=1075.25 → 주문 전송`
- `08:45:10~11 [ExitFillFlow] ×3` 전량 정상 체결(fill 1040.74/1040.98/1040.92)
- `[청산 완료] PnL=-105.36pt | 포지션 합계 -5,299,668원 (레그 3)` — 자본(5천만원) 대비
  **-10.60%**

### 원인 — 09-01 1-6과 동일 뿌리, 오늘은 결과만 실현됐다

09-01 리포트가 이미 원인 가설(force_flat_guard 15:12 단발·daily_close 잔여포지션
미확인·SchedForceExit이 daily_close보다 늦게 재실행됨)을 세워뒀고, 오늘 세션은 그
가설을 재검증하지 않았다(장전 시점이라 DB 접근 불가, 코드 확인도 하지 않음 — 09-01
리포트의 "다음 세션에서 반드시 코드 확인 후 확정" 지시가 아직 이행되지 않았다).

**08-31 505차 사고(LONG 4계약 -5,461,928원, -10.92%)와 손실 규모는 비슷하지만 경로가
다르다.** 08-31은 청산 주문이 브로커에서 거부돼 신규 진입으로 오인된 결함(주문 실패에
재시도가 없던 구조)이었고, 오늘은 09-01 15:34:46에 실제로 열린 정체불명 매수 포지션이
`daily_close()`의 잔여 포지션 미확인 때문에 밤새 방치된 것이다. 둘 다 궁극 원인은
"정체불명 외부/MANUAL 진입"(09-01 1-1, O-i4 — 아직 발생원 미확정)으로 수렴한다.

### 결정 — 코드를 바꾸지 않는다(장전 세션 규약)

09-01이 이미 낸 계획(P0-2: `daily_close()` 진입 전 잔여 포지션 강제청산 통합, 자동조치
C등급 — 승인 대기)을 재확인만 하고 오늘 사고를 근거로 승인 우선순위를 높일 것을
권고했다. 신규 Fix로 다시 올리지 않았다(함정① 확인 — `grep`으로 미구현 상태 재확인).

### Why

- 장전 예약은 개장 3분 전에 돌고 라이브 프로세스가 이미 기동한 뒤라 코드 변경·재기동이
  금지된다(CLAUDE.md 스케줄 지시문).
- P0-2는 주문·청산 실행 경로 변경이라 자동조치 C등급 — 사용자 승인 없이 구현 불가.

### How to apply

승인 후 `main.py: daily_close()` 진입부에 잔여 포지션 확인 + 동기 강제청산 호출 추가
(09-01 리포트 1147~1161행 계획 그대로, 상한 시도 횟수·타임아웃 필수).

### 계측 4원칙 적용

- ① **단위 명시** — 손실은 포지션 단위 -5,299,668원(레그 3개 합산 -105.36pt)으로
  일관 표기.
- ③ **탈락 가시화** — 증거 수집기 §5가 이 포지션을 "귀속 실패 레그 3행"으로 명시
  했다(진입 로그 없는 이월 포지션). 요약 표만 보면 손익이 0으로 보이므로 리포트
  본문에서 원본 로그 인용으로 보완했다(이상점 1-4로 별도 등록).

### 부가 관측 — 511차 Fix(청산 주문 거부 대응) 첫 라이브 확인

09-01까지 163건 거부되던 청산 주문이 오늘은 08:45:09~11 약 1초 안에 3계약 전량 정상
체결됐다(거부·재시도 로그 0건). `NEXT_TODO.md`의 O-p3("511차 Fix 재기동 후 라이브
동작 확인")를 **판정 완료 — 정상**으로 닫는다. 단 09-01 문제가 됐던 "외부 미체결
주문과의 청산가능수량 경합" 조건은 오늘 재현되지 않아 그 조건까지 완전히 검증된 것은
아니다.

### 라이브 미검증 / 이월

- 1-1 발생원(O-i4 연장): 08:45 이후 라이브 DB 분석 금지 구간이라 장전에서 확정 불가.
  장후에 `trades`/`ensemble_decisions`에서 09-01 15:34:46 진입의 `grade` 조회 필요.
- 1-2(entry_horizon 미전달)가 엔진 진입 경로뿐 아니라 브로커 동기화 경로에서도
  재현됨을 확인 — F-5 범위 확장 필요 여부는 코드 확인 후 장후에 판단.

### 검증

이 세션은 로그·설정·git만 읽었다(DB 조회 없음 — 규약 준수). 테스트 실행 없음(코드
변경 없음).

전문: `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` 장전(pre) 절.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 보류 (자동조치 C등급 — 승인 전 구현 금지)
### 사용자 몫 (자동조치 범위 밖 — 손 작업)
### 인계
## 2026-09-02 (MW0601 515차 — 장전 점검 결과)
### 위 09-01 항목 처리 — 완료(자동, 손실 확정)
### 신규 — P0 후속
### 판정 완료 (09-01 이월 항목)
### 사용자 몫 (자동조치 범위 밖 — 손 작업, 오늘 리포트 "사용자 조치" 절과 동일)
```

미완료 체크박스 **2287건** (끝에서 30건)
```
- [ ] **외부/MANUAL 진입 실시간 경보 훅** — `main.py` `[체결동기화] 외부진입` 로그
- [ ] **⚠완료주장-커밋없음 — F-23(종료 마커)·F-24(센티넬 4번째 축)** — 513차
- [ ] **`docs/정기점검/수익률향상_누적대장.md` 갱신 미이행** — 장후 세션이 신규
- [ ] **P2-2 `exit_stage='TRAIL_AFTER_TP1'` 오판정 3건 원인 확인** — 1-7.
- [ ] **레그합-포지션합 불일치(-54,538원) 원인 특정** — 귀속 실패 레그 3행
- [ ] **O-p3** — 511차 Fix(F-19·F-21·F-22·G-6) 재기동 후 라이브 동작 확인.
- [ ] **O-p4** — 오늘 밤새 보유된 LONG 3계약(또는 사용자 수동 정리 결과)의 내일
- [ ] **O-p5** — O-i4(외부 진입 발생원) 사용자 답변 반영.
- [ ] O-i5(이월) — `[BalanceUI]` 키 매핑, `dashboard/main_dashboard.py` 확인 필요.
- [ ] O-t4(지속) — 15m EOD 교체 보류 반복, 실거래 영향 없음 계속 확인.
- [ ] **지금 즉시 — 대신증권 계좌에 LONG 3계약(평균 1076.00)이 남아있는지 확인,
- [ ] **오늘 정체불명 매매 38건(-163만원)이 사용자 본인 것인지 확인** — O-i4/O-p5.
- [ ] **O-514a F-A 발화 확인** — 정상 마감일에 `[DailyCloseResidual] 마감 진입 시
- [ ] **O-514b F-B 발화 확인** — `logs/force_flat_guard_<date>.log` 에 판정이
- [ ] **O-514c F-C 발화 확인** — 외부 진입이 다시 들어오면 경보 탭에
- [ ] **P0-2 `daily_close()` 자동 청산 통합** — 🔴 주간회의 안건. 주문·청산 실행
- [ ] **P2-2 `TRAIL_AFTER_TP1` 라벨 수정** — 🔴 **전제 정정**: 섀도 대사는 이미
- [ ] **CB② 복원 재검토** — 기한 2026-08-29 경과, 계속 미결. 이번 주 중.
- [ ] **주간회의 안건 6건** — 승률 정의 축 · F-15/F-16 외부진입 손익 통합 ·
- [ ] **🔴 대신증권 계좌 LONG 3계약(평균 1076.00) 확인·정리** — 리포트 사용자 조치 1.
- [ ] **정체불명 매매 38건(-163만원) 본인 여부 확인** — O-i4/O-p5.
- [ ] **재기동** — 511차·513차·514차 코드는 재기동 전까지 적용되지 않는다.
- [ ] **전체 테스트 실행 시 `--ignore` 목록 갱신** — `tests/test_511_exit_order_reject.py`
- [ ] **F-1 = P0-2 승인 촉구** — `daily_close()` 진입 전 잔여 포지션 강제청산 통합.
- [ ] **F-2 코드 확인** — `entry_horizon` 미전달이 엔진 진입 경로뿐 아니라 브로커
- [ ] **O-p2** — 오늘 손실 포지션(09-01 15:34:46 진입)의 `grade`·발생원을
- [ ] **이상점 1-4** — 증거 다이제스트 정합성 불일치(귀속 실패 레그) 규모가 -54,538원
- [ ] **어제 저녁 "즉시 매도" 요청을 실행하려 했는지, 왜 반영되지 않았는지 확인**
- [ ] **정체불명 매매 38건(-163만원) + 오늘 손실 포지션 본인 여부 확인** (O-i4)
- [ ] **대신증권 계좌 상태 재확인** — 시스템상 현재 FLAT(포지션 없음)이나 08-31 전례상
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
인 전 구현 금지)

- [ ] **P0-2 `daily_close()` 자동 청산 통합** — 🔴 주간회의 안건. 주문·청산 실행
      경로 변경. F-A(경보)가 임시 안전판으로 먼저 들어갔다.
- [ ] **P2-2 `TRAIL_AFTER_TP1` 라벨 수정** — 🔴 **전제 정정**: 섀도 대사는 이미
      배선돼 있다(507차 G-5 `[ExitStageRecon]` — 1-7 을 찾아낸 것이 그 계측이다).
      남은 것은 **라벨 자체 수정 = F-10 = 청산 트리거 경로 변경**이고
      **섀도 10거래일 관찰(P5-06)이 선행조건**이다. 오늘 1거래일차 — 표본 미달.
- [ ] **CB② 복원 재검토** — 기한 2026-08-29 경과, 계속 미결. 이번 주 중.
- [ ] **주간회의 안건 6건** — 승률 정의 축 · F-15/F-16 외부진입 손익 통합 ·
      F-13 이식 · F-18 미체결 자동취소 승인 · P0-2 자동 청산 통합 ·
      FZ-2 하드 종료 승격.

### 사용자 몫 (자동조치 범위 밖 — 손 작업)

- [ ] **🔴 대신증권 계좌 LONG 3계약(평균 1076.00) 확인·정리** — 리포트 사용자 조치 1.
- [ ] **정체불명 매매 38건(-163만원) 본인 여부 확인** — O-i4/O-p5.
- [ ] **재기동** — 511차·513차·514차 코드는 재기동 전까지 적용되지 않는다.

### 인계

- [ ] **전체 테스트 실행 시 `--ignore` 목록 갱신** — `tests/test_511_exit_order_reject.py`
      추가(단독 스크립트, 수집 시 `win32com` 0xC0000139 로 프로세스 사망).
      `test_500_*.py` 5개와 같은 성격. 단독 실행은 ALL PASS.

## 2026-09-02 (MW0601 515차 — 장전 점검 결과)

> 상세: `DECISION_LOG.md` 2026-09-02(515차). 리포트
> `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` 장전(pre) 절.

### 위 09-01 항목 처리 — 완료(자동, 손실 확정)

- [x] **대신증권 계좌 LONG 3계약(평균 1076.00) 확인·정리** — ✅ **자동 처리됨(사용자
      조치 아님)**: 09-02 08:45 하드스톱으로 시스템이 자동 청산했다. 결과는 손실
      -5,299,668원(자본대비 -10.60%). "정리됨"이지 "문제없이 정리됨"이 아니다 —
      사용자가 그 사이 직접 정리를 시도했는지는 미확인(아래 신규 항목).

### 신규 — P0 후속

- [ ] **F-1 = P0-2 승인 촉구** — `daily_close()` 진입 전 잔여 포지션 강제청산 통합.
      09-01부터 계획은 있으나 자동조치 C등급이라 미승인. 오늘 사고(-530만원 실현손실)를
      근거로 주간회의 우선순위 상향 권고.
- [ ] **F-2 코드 확인** — `entry_horizon` 미전달이 엔진 진입 경로뿐 아니라 브로커
      동기화(이월 포지션 인식) 경로에서도 재현됨(오늘 08:41:09 PositionFallback).
      `grep -n "PositionFallback" main.py`로 호출 지점 확인 후 F-5 범위 확장 필요
      여부 판단 — 장후 이월.
- [ ] **O-p2** — 오늘 손실 포지션(09-01 15:34:46 진입)의 `grade`·발생원을
      `trades`/`ensemble_decisions`에서 조회(O-i4 연장). 08:45 이후 라이브 DB 분석
      금지 구간이라 장전엔 불가 — **장후 필수 확인**.
- [ ] **이상점 1-4** — 증거 다이제스트 정합성 불일치(귀속 실패 레그) 규모가 -54,538원
      (09-01)에서 -5,299,668원(09-02, 전액)으로 확대 재현. DB 3원 대사로 보완 가능한지
      장후에 확인.

### 판정 완료 (09-01 이월 항목)

- [x] **O-p3** — 511차 Fix(F-19·F-21·F-22·G-6) 재기동 후 라이브 동작 확인 → **정상**.
      오늘 08:45:09~11 청산 주문 3계약 전량 거부 없이 체결(09-01 163건 거부와 대조).
      단 "외부 미체결 주문과의 청산가능수량 경합" 조건은 오늘 재현되지 않아 그 조건은
      미검증으로 남는다.

### 사용자 몫 (자동조치 범위 밖 — 손 작업, 오늘 리포트 "사용자 조치" 절과 동일)

- [ ] **어제 저녁 "즉시 매도" 요청을 실행하려 했는지, 왜 반영되지 않았는지 확인**
- [ ] **정체불명 매매 38건(-163만원) + 오늘 손실 포지션 본인 여부 확인** (O-i4)
- [ ] **대신증권 계좌 상태 재확인** — 시스템상 현재 FLAT(포지션 없음)이나 08-31 전례상
      시스템·실계좌 불일치 가능성을 배제하지 않음

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

### `data/heartbeat_MW0601_20260902.json` — 243B · 09-02 12:26:16
```json
{
 "pid": 2768,
 "written_at": "2026-09-02T12:27:16",
 "beat_epoch": 1788319634.625001,
 "beat_age_sec": 2.3,
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

### `docs/정기점검/매일점검` — 92개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` | 23.0KB | 09-02 09:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_pre.md` | 58.1KB | 09-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-01 18:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_post.md` | 89.7KB | 09-01 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_intra.md` | 68.8KB | 09-01 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_pre.md` | 49.8KB | 09-01 09:01 |
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 203.4KB | 08-31 18:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_post.md` | 79.5KB | 08-31 16:17 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 2.6KB | 08-31 00:05 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260828.json` | 2.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260828.md` | 4.9KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260828.md` | 28.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260828.json` | 35.2KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260828.md` | 178.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260828.json` | 97.7KB | 08-28 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-23 21:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260902_WARN.log`: ERROR 이상 2건
2. `logs/20260902_WARN.log`: **Traceback** 출현 4건 — 크래시/메모리 계열
3. `logs/20260902_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
4. `logs/20260902_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. 메인 스레드 정지 5초 초과 **6건** (최대 56875ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260902_WARN.log`: **ConstOut** 2건(표본)
8. `logs/20260902_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20260902_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260902_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260902_LEARNING.log`: **축퇴** 8건(표본)
12. 미커밋 변경 518건 (실질 2건 · 코드 0건 · EOL 파생 514건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260902*.log` (Windows) / `grep 강제청산 logs/*20260902*.log`*