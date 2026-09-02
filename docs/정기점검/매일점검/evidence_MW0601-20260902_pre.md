# 미륵이 증거 다이제스트 — 2026-09-02 / PRE

- 생성 2026-09-02 08:59:43 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/gifted-affectionate-ptolemy/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260902` · `2026-09-02` · `260902` · `0902`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **15개** 파일 · 15개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260902.log` | 125B | 09-02 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260902.log` | 140B | 09-02 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260902.json` | 244B | 09-02 08:59 |
| `launcher_{DATE}_084001_7533.log` | 1 | `logs/Mireuk_batch/launcher_20260902_084001_7533.log` | 57.7KB | 09-02 08:58 |
| `{DATE}_DATA.log` | 1 | `logs/20260902_DATA.log` | 914B | 09-02 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260902_DEBUG.log` | 0B | 09-02 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260902_HEALTH.log` | 0B | 09-02 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20260902_HOGA.log` | 1.2MB | 09-02 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260902_LEARNING.log` | 52.2KB | 09-02 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20260902_MICRO.log` | 32.5KB | 09-02 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20260902_PROBE.log` | 1.7KB | 09-02 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260902_SIGNAL.log` | 16.9KB | 09-02 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260902_SYSTEM.log` | 27.7KB | 09-02 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20260902_TRADE.log` | 2.2KB | 09-02 08:52 |
| `{DATE}_WARN.log` | 1 | `logs/20260902_WARN.log` | 8.0KB | 09-02 08:55 |

## 2. 코드·커밋 상태

- HEAD `a3f70ab` · 브랜치 `v9-dev` · 미커밋 514건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 514건 (추적변경 514 · 미추적 0 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
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
… 외 474건
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

_본문 미열람(설정): `20260902_HOGA.log` 1.2MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/11개 (중요도순). 제외: `launcher_20260902_084001_7533.log`, `freeze_sentinel_20260902.log`, `force_flat_guard_20260902.log`_

### `logs/20260902_TRADE.log` — 2.2KB · 18행 · 최종 08:52:26

- 형식 평문 · 시각 인식 18행 · WARNING=2, INFO=16

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:41:00 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-02 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-02 08:41:09 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-09-02 08:41:09 [WARNING] TRADE: [Position] 브로커 기준 동기화: LONG 3계약 @ 1076.0 | 손절=1075.25
2026-09-02 08:45:09 [INFO] TRADE: [TickStop-S0C] 하드스톱(틱) LONG 3ct tick=1041.44 stop=1075.25 → 주문 전송
  …
2026-09-02 08:45:10 [INFO] TRADE: [Chejan] 상태=체결 주문번호=101 code=A0569 방향=SHORT 체결=1 미체결=0
2026-09-02 08:45:10 [INFO] TRADE: [Position] 체결청산 LONG @ 1040.92 | PnL=-35.08pt (-1,764,556원) | 하드스톱(틱)
2026-09-02 08:45:10 [INFO] TRADE: [청산 완료] PnL=-35.12pt (-5,299,668원) | 포지션 합계 -5,299,668원 (레그 3)
2026-09-02 08:52:19 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-02 08:52:26 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 1 | 08:41:09 | 08:41:09 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=3 entry=1076.00 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `Position` | 1 | 08:41:09 | 08:41:09 | 브로커 기준 동기화: LONG 3계약 @ 1076.0 | 손절=1075.25 |

**채널** — `TRADE`×18

**컴포넌트 상위 15** — `Position`×5, `Chejan`×4, `ProfitGuard`×3, `체결청산-부분`×2, `PositionFallback`×1, `TickStop-S0C`×1, `주문요청`×1, `청산 완료`×1

### `logs/20260902_WARN.log` — 8.0KB · 43행 · 최종 08:55:10

- 형식 평문 · 시각 인식 43행 · CRITICAL=1, WARNING=42

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-09-02 08:41:09 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 188ms account=333044256
2026-09-02 08:41:09 [WARNING] SYSTEM: [BrokerSync] balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '42172727', '총평가손익': '42172727', '실현손익': '0', '총평가': '0.00', '총평가수익률': '42172727', '추정자산': '-1144000'}
2026-09-02 08:41:09 [WARNING] SYSTEM: [BrokerSync] startup sync raw rows=1 nonempty_rows=1 all_blank_rows=False record_name='CpTd0723' prev_next='' rows=[{'종목코드': 'A0569', '종목명': '¹Ì´ÏÄÚ½ºÇÇ F 202609', '구분': '매수', '매매구분': '매수', '잔고수량': '3', '청산가능': '3', '평균가': '1076.0', '매입단가': '1076.0', '현재가': '',…
  …
2026-09-02 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2491ms | quality=0.86 | cache_age=46s | exceptions_10m=1
2026-09-02 09:00:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 2491ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-02 09:00:03 [WARNING] SYSTEM: [CB⑤] 파이프라인 2491ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-09-02 09:00:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 10953ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=10953 band=WARN since_pipe_s=0.2
2026-09-02 09:00:10 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260902.log
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `BrokerSync` | 1 | 08:41:09 | 08:41:09 | startup sync 완료: FLAT -> LONG 3계약 @ 1076.00 |

<details><summary>CRITICAL/BrokerSync 원문 1건</summary>

```
2026-09-02 08:41:09 [CRITICAL] SYSTEM: [BrokerSync] startup sync 완료: FLAT -> LONG 3계약 @ 1076.00
```

</details>

**WARNING — 태그 16종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 11 | 08:41:09 | 09:00:10 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `BrokerSync` | 4 | 08:41:09 | 08:41:09 | balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '42172727', '총평가손익': '42172727', '실현손익': '0', '총평가': '0.00', '총평가수익률': '42172727', '추정자산': '-1144000'} |
| `ChejanFlow` | 4 | 08:45:10 | 08:45:10 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='101' | pending='EXIT_FULL:LONG qty=3 filled=0 order_no=? reason=하드스톱(틱) req_at=08:45:09.952' |… |
| `ChejanMatch` | 4 | 08:45:10 | 08:45:10 | order_no='101' | pending='EXIT_FULL:LONG qty=3 filled=0 order_no=101 reason=하드스톱(틱) req_at=08:45:09.952' | pending_matched=True |
| `ExitFillFlow` | 3 | 08:45:10 | 08:45:11 | after='LONG 2계약 @ 1076.00' | before='LONG 3계약 @ 1076.00' | fill_price=1040.74 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:LONG qty=3 filled=1 order_no=101 reason=하드스톱(틱) req_at=08:45:09.952' | reason='하드스톱(틱)' |
| `PendingOrder` | 2 | 08:45:09 | 08:45:11 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1075.25, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `ExitCooldown` | 2 | 08:45:10 | 08:45:10 | 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10) |
| `Canary` | 2 | 08:55:10 | 08:55:10 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:02 | 09:00:02 | total=2491ms | S0=3ms S1=10ms S2=0ms S3=0ms S4=92ms S5=863ms S6=1347ms S7=153ms S8=24ms |
| `CB⑤` | 2 | 09:00:03 | 09:00:03 | 파이프라인 2491ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `TickStop` | 1 | 08:45:09 | 08:45:09 | 스톱 히트 감지 (틱) LONG tick=1041.44 stop=1075.25 → 즉시 처리 예약 |
| `ExitSendOrderResult` | 1 | 08:45:09 | 08:45:09 | ret=0 kind=하드스톱(틱) direction=LONG qty=3 |

**채널** — `SYSTEM`×42, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×11, `BrokerSync`×5, `ChejanFlow`×4, `ChejanMatch`×4, `ExitFillFlow`×3, `PendingOrder`×2, `ExitCooldown`×2, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `TickStop`×1, `ExitSendOrderResult`×1, `CB`×1, `Armistice`×1, `Health`×1

### `logs/20260902_SYSTEM.log` — 27.7KB · 229행 · 최종 08:59:35

- 형식 평문 · 시각 인식 222행 · INFO=222, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:33 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.9MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-09-02 08:40:33 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=2768 | 행감지=30s all_threads=True
2026-09-02 08:40:49 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-02 08:40:49 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-02 08:40:49 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-02 09:00:10 [INFO] SYSTEM: [CybosRT-TICK] #2300 code=A0569 raw_time=90002 parsed=09:00:02 price=1040.56 vol=1 bid1=1040.56 ask1=1040.80 flag=50 side=SELL anchor=0/1
2026-09-02 09:00:11 [INFO] SYSTEM: [CybosRT-TICK] #2400 code=A0569 raw_time=90011 parsed=09:00:11 price=1041.14 vol=1 bid1=1040.98 ask1=1041.32 flag=50 side=SELL anchor=0/1
2026-09-02 09:00:20 [INFO] SYSTEM: [CybosRT-TICK] #2500 code=A0569 raw_time=90020 parsed=09:00:20 price=1040.62 vol=1 bid1=1040.36 ask1=1040.64 flag=49 side=BUY anchor=1/0
2026-09-02 09:00:30 [INFO] SYSTEM: [CybosRT-TICK] #2600 code=A0569 raw_time=90030 parsed=09:00:30 price=1040.98 vol=1 bid1=1040.86 ask1=1040.98 flag=49 side=BUY anchor=1/0
2026-09-02 09:00:31 [INFO] SYSTEM: [TickUI] alive ticks=2641 code=A0569 close=1041.14
```

</details>

**채널** — `SYSTEM`×222

**컴포넌트 상위 15** — `CybosRT-TICK`×31, `CybosSub`×21, `System`×17, `TickUI`×16, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `SYSTEM`×9, `BalanceUI`×9, `PreMarket`×9, `CybosEvent`×8, `CybosRT-START`×6, `Notify`×5, `-`×4, `EarlyWarmup`×3

### `logs/20260902_SIGNAL.log` — 16.9KB · 170행 · 최종 08:59:00

- 형식 평문 · 시각 인식 170행 · WARNING=79, INFO=91

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
  …
2026-09-02 09:00:04 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4030 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-02 09:00:04 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0469 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-02 09:00:04 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1217 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-02 09:00:04 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-09-02 09:00:10 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 48 | 08:45:09 | 08:59:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0327) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 30 | 09:00:04 | 09:00:04 | 1m 'macro_krw_chg' scale=0.0502 → floor=0.10 적용 (z-score 폭발 방지) |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×170

**컴포넌트 상위 15** — `ScalerFloor`×90, `ScalerRefresh`×55, `DynMC`×7, `Model`×6, `TimeRouter`×3, `SIGNAL`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1, `ZeroDiag`×1

### `logs/20260902_LEARNING.log` — 52.2KB · 295행 · 최종 08:59:00

- 형식 평문 · 시각 인식 295행 · WARNING=143, INFO=152

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00008 auc=0.274 out_max=0.0875 (기준 auc<0.53 and span<0.020, 기저율=0.0875 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00217 auc=0.298 out_max=0.2759 (기준 auc<0.53 and span<0.020, 기저율=0.2750 n=80) → 보정 미적용, raw 통과
2026-09-02 08:40:52 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00111 auc=0.595 out_max=0.1796 (n=95) → 보정 재적용
  …
2026-09-02 08:55:09 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=17358, ver=5)
2026-09-02 08:55:10 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-02 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-09-02 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1041.70
2026-09-02 09:00:04 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 143 | 08:40:52 | 08:41:00 | 축퇴 감지 — span=0.00048 auc=0.431 out_max=0.3752 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×295

**컴포넌트 상위 15** — `Calibration`×279, `ScalerWarmup`×7, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1, `sigma`×1

### `logs/20260902_MICRO.log` — 32.5KB · 95행 · 최종 08:59:31

- 형식 평문 · 시각 인식 95행 · DEBUG=95

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1040.98/1 ask1=1041.46/3 mp={'microprice_tick': 1041.1, 'midprice_tick': 1041.22, 'depth_bias_tick': -0.4771} mlofi_tick=None queue=None
2026-09-02 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1040.98/2 ask1=1041.46/3 mp={'microprice_tick': 1041.172, 'midprice_tick': 1041.22, 'depth_bias_tick': -0.3253} mlofi_tick=1.0 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-09-02 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1040.98/1 ask1=1041.40/1 mp={'microprice_tick': 1041.19, 'midprice_tick': 1041.19, 'depth_bias_tick': -0.0987} mlofi_tick=-3.7833 queue={'depletion_bid': 1.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-09-02 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1040.90/1 ask1=1041.34/2 mp={'microprice_tick': 1041.0467, 'midprice_tick': 1041.12, 'depth_bias_tick': -0.1387} mlofi_tick=-5.5667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio…
2026-09-02 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1040.72/1 ask1=1041.34/2 mp={'microprice_tick': 1040.9266, 'midprice_tick': 1041.03, 'depth_bias_tick': 0.1166} mlofi_tick=-2.4833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio…
  …
2026-09-02 09:00:10 [DEBUG] MICRO: [MICRO-TICK] #5600 bid1=1040.72/1 ask1=1040.82/2 mp={'microprice_tick': 1040.7533, 'midprice_tick': 1040.77, 'depth_bias_tick': -0.113} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-02 09:00:11 [DEBUG] MICRO: [MICRO-TICK] #5700 bid1=1040.70/1 ask1=1041.18/2 mp={'microprice_tick': 1040.86, 'midprice_tick': 1040.94, 'depth_bias_tick': -0.3522} mlofi_tick=3.6333 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio…
2026-09-02 09:00:17 [DEBUG] MICRO: [MICRO-TICK] #5800 bid1=1040.74/2 ask1=1040.98/1 mp={'microprice_tick': 1040.9, 'midprice_tick': 1040.86, 'depth_bias_tick': 0.1496} mlofi_tick=3.8667 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-09-02 09:00:24 [DEBUG] MICRO: [MICRO-TICK] #5900 bid1=1041.52/1 ask1=1041.82/1 mp={'microprice_tick': 1041.67, 'midprice_tick': 1041.67, 'depth_bias_tick': -0.0987} mlofi_tick=-5.8167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-09-02 09:00:30 [DEBUG] MICRO: [MICRO-TICK] #6000 bid1=1041.16/1 ask1=1041.50/1 mp={'microprice_tick': 1041.33, 'midprice_tick': 1041.33, 'depth_bias_tick': 0.033} mlofi_tick=5.15 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
```

</details>

**채널** — `MICRO`×95

**컴포넌트 상위 15** — `MICRO-TICK`×80, `MICRO-MINUTE`×15

### `logs/20260902_DATA.log` — 914B · 5행 · 최종 08:58:43

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=154621 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-02 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-02 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=154614 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-02 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-02 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-09-02 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=154621 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-02 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-02 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=154614 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-09-02 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-09-02 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

### `logs/20260902_PROBE.log` — 1.7KB · 11행 · 최종 08:58:43

- 형식 평문 · 시각 인식 11행 · WARNING=10, INFO=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-02 08:41:09 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A0569']
2026-09-02 08:58:13 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-02 08:58:13 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-02 08:58:13 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-02 08:58:13 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
  …
2026-09-02 08:58:43 [WARNING] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None)
2026-09-02 08:58:43 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-02 08:58:43 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrader dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-02 08:58:43 [WARNING] PROBE: [CybosProbe] Dscbo1.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
2026-09-02 08:58:43 [WARNING] PROBE: [CybosProbe] CpSysDib.FutureTrade dispatch/request failed: (-2147221005, '잘못된 클래스 문자열입니다.', None, None)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `CybosProbe` | 10 | 08:58:13 | 08:58:43 | CpSysDib.CpSvrNew7221 dispatch/request failed: (-2147221008, 'CoInitialize가 호출되지 않았습니다.', None, None) |

**채널** — `PROBE`×11

**컴포넌트 상위 15** — `CybosProbe`×10, `CybosInvestorProbe`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) — **엔진** | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|

**출처별 소계** — 

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**청산 레그 0행** (부분청산 2 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 -5,299,668 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 1건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패 레그 3행 ⚠**(진입 로그 없는 이월 포지션 가능)

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 2건 · 최대 10953ms · 5초 초과 1건

상위 — 10953ms, 3250ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:10 | 10953ms | 2491ms | **8462ms (77%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260902_WARN.log`
```
--- Traceback ×1(표본)
09:00:10 2026-09-02 09:00:10 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260902.log
--- [CB] ×1(표본)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×2(표본)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10)
08:45:10 2026-09-02 08:45:10 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:10)
--- 메인 스레드 블로킹 ×2(표본)
08:41:12 2026-09-02 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3250 band=INFO since_pipe_s=NA
09:00:10 2026-09-02 09:00:10 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 10953ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=10953 band=WARN since_pipe_s=0.2
```

### `logs/20260902_SYSTEM.log`
```
--- PSI ×1(표본)
09:00:00 2026-09-02 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20260902_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-09-02 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4240 (conf_floor=0.330, min_conf=0.424, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×7(표본)
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:30 2026-09-02 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
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

- 이 로그 생존구간: 08:41 ~ 08:52

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260902_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 33 | 08:41:09 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 10 | 08:55:10 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260902_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:33 [INFO] 로테이션 — 8.9MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 104 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 73 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260902_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:09 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0327) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 102 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0456) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 95 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0446) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 08:40 ~ 09:00

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
| **오늘 20260902** | **09:00** | 로그 본문 |

- 델타 **-400분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · 마지막 갱신 2026-09-01 18:17

최근 헤딩 8개:
```
### 원인 — 세 겹이 **동시에** 조용했다. 하나도 고장 나지 않았다는 것이 핵심이다
### 결정 — 알림 축 3개를 더한다. **매매 경로는 하나도 건드리지 않는다**
### Why — 설계에서 일부러 하지 **않은** 것
### 계측 4원칙 적용
### 보류 (자동조치 C등급 — 구현하지 않음)
### 검증
### ⚠ 인계 — 전체 스위트 실행 시 `--ignore` 가 **한 개 늘었다**
### 라이브 미검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 값·타입을 바꾸면 그 항목의 대조 대상이 어긋난다
(461차 `mdd_pct` 교훈). 새 상수 `FORCE_FLAT_GUARD_EXTRA_AT` 로 **축을 더하기만** 했다.
`FORCE_FLAT_GUARD_ORDER_ENABLED` 는 `False` 유지 — 1단계 「알림 전용」 성격 무변경.

🔴 **Slack 은 쓰지 않는다.** 사용자 결정(개발단계 직접 모니터링)이며
`scripts/force_flat_guard.py:emit()` 이 같은 이유로 이미 Slack 을 배제하고 있다.
경보 채널은 대시보드 「경보」 탭으로 올라가는 `log_manager.system(..., "ERROR")` 다.

⚠ **반복 판정의 종합은 `max(rc)` 가 아니다.** RC 숫자는 심각도 순이 **아니다** —
미청산(`RC_UNCLOSED=3`)이 가장 심각한데 비거래일(`RC_NOT_APPLICABLE=6`)보다 **작다**.
`max` 를 쓰면 미청산이 조용히 묻힌다. `_RC_SEVERITY` 표로 명시했다(계측 4원칙 ① —
축을 이름으로 못박는다).

### 계측 4원칙 적용

- ② **미측정 ≠ 0** — F-A 는 포지션 상태를 못 읽으면 「FLAT」이 아니라 **미측정**으로
  적는다("FLAT 확인이 아니다"를 문구에 박았다). F-C 는 외부 진입 0건도
  「실측 — 미측정이 아니다」로 명시 기록한다.
- ④ **폴백 가시화** — `_external_entry_legs_today`·`_external_entry_qty_today` 는
  `__init__` 에서 명시 초기화한다(`getattr` 폴백 금지). 일별 집계는 **리셋 전에**
  스냅샷을 잡는다(`_ccf_today` 관례).
- ⑤ **모든 축** — F-A 는 엔진 포지션 축과 브로커 잔량(`_integrity_broker_qty`) 축을
  **둘 다** 건다. 한 축만 보면 엔진 FLAT + 브로커 잔량 형태를 통째로 놓친다.

### 보류 (자동조치 C등급 — 구현하지 않음)

- **P0-2** — 리포트 자신이 C등급으로 표기. 주간회의 안건.
- **P2-2 (`TRAIL_AFTER_TP1` 라벨에 TP1 실도달 플래그)** — 🔴 **함정① 확인 결과
  전제가 달랐다.** 섀도 대사는 **이미 배선돼 있다**(507차 G-5 `[ExitStageRecon]`,
  `main.py`) — 이상점 1-7 을 찾아낸 것이 바로 그 계측이다. 남은 것은 **라벨 자체를
  고치는 것**인데 그것은 코드 주석이 명시하듯 **F-10 = 청산 트리거 경로 변경**이고
  **섀도 10거래일 관찰(P5-06)이 선행조건**이다. 오늘은 1거래일차다.
  ⇒ 승인·표본 둘 다 미충족. 보류.

### 검증

- `tests/test_514_postmarket_autofix.py` **24 passed** — F-A 경보 존재·통계 앞 실행·
  미측정 구분·두 축·**주문 미호출** / F-B 추가시각·주 상수 무변경·주문 비활성·
  `_worse_rc` 심각도 순서·파서 방어·판정 로직 무변경·2026-09-01 재현(15:12 OK →
  15:39 CRITICAL) / F-C 경보 존재·명시 초기화·0 실측 기록·리셋 전 스냅샷·
  **매매 경로 미호출**·Slack 미사용 / 절대원칙 토글 6종 무변경.
- 전체 스위트 **1,071 passed · 1 skipped · 4 xfailed · 3 failed**.
  실패 3건은 전량 **선행 실패**다(08-31 상태파일에 동일 기록):
  `test_483_git_lock_guard[fuoption]`(형제 저장소 사본 대조) ·
  `test_504_pnl_history_creon_tab` 2건. 이번 변경과 무관.
- 관련 스위트 회귀 없음: 457(폴백 가시성)·480(F-2 가드)·483(마감 스냅샷 순서)·
  490·513 = **48 passed**.

### ⚠ 인계 — 전체 스위트 실행 시 `--ignore` 가 **한 개 늘었다**

`tests/test_511_exit_order_reject.py` 는 pytest 테스트가 아니라 **단독 스크립트**다
(모듈 스코프에서 `import main` 후 즉시 실행, 끝에 `sys.exit`). 전체 수집에 섞이면
`win32com` 로드가 **0xC0000139 로 프로세스를 통째로 죽여** 수집이 중단된다
(테스트 0건 수집 → 전체 실행 불가). 단독 실행은 정상이다 —
`python tests/test_511_exit_order_reject.py` → **ALL PASS**.

⇒ 전체 실행 명령: `--ignore=tests/test_511_exit_order_reject.py` +
`test_500_*.py` 5개. **이 실패는 511차가 남긴 것이며 514차 변경과 무관하다.**

### 라이브 미검증

F-A·F-C 는 다음 재기동(2026-09-02) 후부터, F-B 는 다음 거래일 15:20 부터 발화한다.
오늘 돌고 있는 프로세스·가드는 구코드다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · 마지막 갱신 2026-09-01 18:18

최근 헤딩 8개:
```
### 장후로 이월된 확인 (관측)
### 🔴 사용자 최우선 확인 (오늘 리포트에서 이관)
## 2026-09-01 (MW0601 514차 — 장후 자동조치 구현 결과)
### 완료
### 라이브 확인 (2026-09-02 이후)
### 보류 (자동조치 C등급 — 승인 전 구현 금지)
### 사용자 몫 (자동조치 범위 밖 — 손 작업)
### 인계
```

미완료 체크박스 **2280건** (끝에서 30건)
```
- [ ] **커밋 대기**: `main.py` · `config/settings.py` · `tests/test_511_exit_order_reject.py`
- [ ] **F-23R 라이브 확인 (2026-09-02 장후)** — 재기동 후 정상 마감한 날에
- [ ] **배포(재기동)** — 장 마감 후. 재기동 전까지 구코드가 돈다.
- [ ] **F-25 (참고) 498차 F-10 축 처분** — `daily_close_done` 축은 그대로 뒀다
- [ ] **P0-2 (🔴 주간회의 안건 — 자동조치 C등급) `daily_close()` 진입 전 잔여 포지션
- [ ] **P1-3 (승인 불요 — 즉시 구현 가능) `daily_close()` 진입 시 잔여 포지션 있으면
- [ ] **`force_flat_guard.py` 15:12 단발 → 15:10~15:39 반복 스케줄로 확장** —
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
i5(이월) — `[BalanceUI]` 키 매핑, `dashboard/main_dashboard.py` 확인 필요.
- [ ] O-t4(지속) — 15m EOD 교체 보류 반복, 실거래 영향 없음 계속 확인.

### 🔴 사용자 최우선 확인 (오늘 리포트에서 이관)

- [ ] **지금 즉시 — 대신증권 계좌에 LONG 3계약(평균 1076.00)이 남아있는지 확인,
      있으면 시장가 매도.** 미륵이는 내일 08:45까지 재기동하지 않는다.
- [ ] **오늘 정체불명 매매 38건(-163만원)이 사용자 본인 것인지 확인** — O-i4/O-p5.

## 2026-09-01 (MW0601 514차 — 장후 자동조치 구현 결과)

> 상세: `DECISION_LOG.md` 2026-09-01(514차). 리포트 제8부.

### 완료

- [x] **F-A = P1-3 `daily_close()` 진입 시 잔여 포지션 경보** — ✅ `main.py:daily_close()`.
      엔진 축 + `_integrity_broker_qty` 축 동시 확인, 미측정 구분. **청산 안 함**.
- [x] **F-B = 고도화① FLAT 가드 반복 판정** — ✅ `FORCE_FLAT_GUARD_EXTRA_AT =
      ["15:20","15:30","15:39"]` 신설 + `scripts/force_flat_guard.py` 에
      `judge_and_emit()`·`_extra_times()`·`_worse_rc()`.
      ⚠ `FORCE_FLAT_GUARD_AT`(26주 WFA 등록 상수)는 **무변경** — 축을 더하기만 했다.
- [x] **F-C = 고도화②·P5-신규 외부 진입 실시간 경보** — ✅ `main.py` 외부진입
      동기화 지점 `log_manager.system(ERROR)` + 일별 집계(마감 1회 보고).
      Slack 미사용(사용자 결정).
- [x] **⚠완료주장-커밋없음 F-23·F-24 확인** — 실재 확인 완료(워킹트리에 미커밋으로
      존재했다). 514차 커밋에 함께 포함해 해소.

### 라이브 확인 (2026-09-02 이후)

- [ ] **O-514a F-A 발화 확인** — 정상 마감일에 `[DailyCloseResidual] 마감 진입 시
      FLAT 확인` INFO 1줄. 잔여 포지션이 있던 날에는 ERROR 1줄.
      ⚠ 한 줄도 없으면 삽입 지점이 skip 분기에 걸린 것이다.
- [ ] **O-514b F-B 발화 확인** — `logs/force_flat_guard_<date>.log` 에 판정이
      **4회**(15:12·15:20·15:30·15:39) 남는가. 1회뿐이면 `--once` 경로를 탔거나
      프로세스가 15:12 에 종료된 것이다.
- [ ] **O-514c F-C 발화 확인** — 외부 진입이 다시 들어오면 경보 탭에
      `[ExternalEntry]` 가 **검출과 같은 분에** 뜨는가. 없으면 마감 집계
      `오늘 외부 진입 0건` 만 확인하고 종결.

### 보류 (자동조치 C등급 — 승인 전 구현 금지)

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

### `data/heartbeat_MW0601_20260902.json` — 244B · 09-02 08:59:40
```json
{
 "pid": 2768,
 "written_at": "2026-09-02T09:00:10",
 "beat_epoch": 1788307202.7110844,
 "beat_age_sec": 8.0,
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

### `docs/정기점검/매일점검` — 90개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-01 18:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_post.md` | 89.7KB | 09-01 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_intra.md` | 68.8KB | 09-01 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260901_pre.md` | 49.8KB | 09-01 09:01 |
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 203.4KB | 08-31 18:13 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_post.md` | 79.5KB | 08-31 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_intra.md` | 65.5KB | 08-31 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` | 57.8KB | 08-31 09:00 |

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

1. `logs/20260902_WARN.log`: ERROR 이상 1건
2. `logs/20260902_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
3. 메인 스레드 정지 5초 초과 **1건** (최대 10953ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20260902_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260902*.log` (Windows) / `grep 강제청산 logs/*20260902*.log`*