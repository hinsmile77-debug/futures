# 미륵이 증거 다이제스트 — 2026-08-31 / INTRA

- 생성 2026-08-31 12:26:52 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/keen-awesome-bohr/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260831` · `2026-08-31` · `260831` · `0831`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **20개** 파일 · 20개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260831.log` | 498B | 08-31 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260831.log` | 558B | 08-31 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260831.json` | 244B | 08-31 12:26 |
| `launcher_{DATE}_004147_4902.log` | 1 | `logs/Mireuk_batch/launcher_20260831_004147_4902.log` | 16.9KB | 08-31 01:02 |
| `launcher_{DATE}_012504_13379.log` | 1 | `logs/Mireuk_batch/launcher_20260831_012504_13379.log` | 16.5KB | 08-31 01:30 |
| `launcher_{DATE}_013454_15309.log` | 1 | `logs/Mireuk_batch/launcher_20260831_013454_15309.log` | 16.8KB | 08-31 01:41 |
| `launcher_{DATE}_084001_297.log` | 1 | `logs/Mireuk_batch/launcher_20260831_084001_297.log` | 1.2MB | 08-31 12:26 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260831.log` | 2.9KB | 08-31 09:00 |
| `retrain_intraday_{DATE}_093701.log` | 1 | `logs/retrain_intraday_20260831_093701.log` | 2.7KB | 08-31 09:37 |
| `{DATE}_DATA.log` | 1 | `logs/20260831_DATA.log` | 182.2KB | 08-31 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260831_DEBUG.log` | 136.8KB | 08-31 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260831_HEALTH.log` | 9.1KB | 08-31 11:55 |
| `{DATE}_HOGA.log` | 1 | `logs/20260831_HOGA.log` | 30.3MB | 08-31 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260831_LEARNING.log` | 326.1KB | 08-31 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20260831_MICRO.log` | 605.1KB | 08-31 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20260831_PROBE.log` | 57.8KB | 08-31 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260831_SIGNAL.log` | 351.0KB | 08-31 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260831_SYSTEM.log` | 650.3KB | 08-31 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20260831_TRADE.log` | 33.7KB | 08-31 12:20 |
| `{DATE}_WARN.log` | 1 | `logs/20260831_WARN.log` | 148.0KB | 08-31 12:26 |

## 2. 코드·커밋 상태

- HEAD `f01080b` · 브랜치 `v9-dev` · 미커밋 515건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 511건 (추적변경 513 · 미추적 2 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
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
… 외 475건
```

**당일(2026-08-31) 커밋**
```
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
6dfe6d7 [MW0601] 504차: 8월 손실일 딥다이브 + 손익추이2(CREON 반사실)·거래 출처 필터
```

**최근 커밋 12건**
```
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
5cf1eab [MW0601] 금요일점검 주간 산출물: 2026-08-28 3종 + 4주 FIFO 보관 정리
4b494df [MW0601] 매일점검 산출물: 2026-08-27 점검리포트 + 증거 다이제스트 2건
81096d5 [MW0601] 504차 후속: 기동 패널 복원 4단계 체인 — 워커 스레드 QTimer 미발화 수정
6dfe6d7 [MW0601] 504차: 8월 손실일 딥다이브 + 손익추이2(CREON 반사실)·거래 출처 필터
fc05088 [MW0601] test_479 오탐 정정: broker_net_chain_audit.py를 _COMPRESSED_AWARE에 등록
1c51249 [MW0601] dev 502차 후속 체리픽: U-1 te ready 플래그 + U-2 [57] 게이트 섀도 배선
614eda2 [MW0601] dev 501차 D1 정정 실행 완료 — daily_broker_pnl 브로커net 재산출
9bf94dd [MW0601] dev 501차 체리픽: 브로커 net 예탁금 체인 결함 3종(D1/D2/D3) 수정
b2f94eb [MW0601] 500차 4단계: 구성적 중복 검출 + CORE 우선 시계 스크린 (SOP §3 B-5 / §2 A-6)
3f6f7bf [MW0601] 500차 3단계: 주간회의 결정 1·2·3 집행 (사용자 승인)
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

_본문 미열람(설정): `20260831_HOGA.log` 30.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/18개 (중요도순). 제외: `20260831_DATA.log`, `20260831_PROBE.log`, `launcher_20260831_084001_297.log`, `launcher_20260831_004147_4902.log`, `launcher_20260831_013454_15309.log`, `launcher_20260831_012504_13379.log`, `20260831_DEBUG.log`, `mainstall_traceback_20260831.log`_

### `logs/20260831_TRADE.log` — 33.7KB · 254행 · 최종 12:20:01

- 형식 평문 · 시각 인식 254행 · WARNING=37, INFO=217

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:18 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-31 00:42:22 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-31 00:42:24 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=4 entry=1068.47 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-08-31 00:42:24 [WARNING] TRADE: [Position] 브로커 기준 동기화: LONG 4계약 @ 1068.47 | 손절=1067.72
2026-08-31 01:25:35 [WARNING] TRADE: [Position] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72)
  …
2026-08-31 12:20:00 [INFO] TRADE: [주문요청] TP2 청산 SHORT 1계약 @ 1051.92 체결대기
2026-08-31 12:20:01 [INFO] TRADE: [Chejan] 상태=접수 주문번호=3264 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-31 12:20:01 [INFO] TRADE: [Chejan] 상태=체결 주문번호=3264 code=A0569 방향=LONG 체결=1 미체결=0
2026-08-31 12:20:01 [INFO] TRADE: [Position] 체결청산 SHORT @ 1052.12 | PnL=+2.08pt (+93,658원) | TP2(전량)
2026-08-31 12:20:01 [INFO] TRADE: [청산 완료] PnL=+2.08pt (+93,658원) | 포지션 합계 +93,658원 (레그 1)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 27 | 00:42:24 | 12:16:32 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=4 entry=1068.47 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `Position` | 7 | 00:42:24 | 08:41:05 | 브로커 기준 동기화: LONG 4계약 @ 1068.47 | 손절=1067.72 |
| `PositionDiag` | 3 | 01:25:35 | 08:40:57 | restore source=sync_from_broker:LONG saved_at=2026-08-31T00:42:24.750030 last_update_ts=2026-08-31T00:42:24.750030 |

**채널** — `TRADE`×254

**컴포넌트 상위 15** — `Chejan`×82, `Position`×59, `PositionFallback`×27, `체결동기화`×23, `주문요청`×15, `청산 완료`×14, `TickStop-S0C`×10, `체결청산-부분`×8, `TickTP1`×6, `ProfitGuard`×4, `PositionDiag`×3, `TP1 부분청산`×3

### `logs/20260831_WARN.log` — 148.0KB · 745행 · 최종 12:26:00

- 형식 평문 · 시각 인식 745행 · CRITICAL=9, WARNING=736

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-08-31 00:42:24 [WARNING] SYSTEM: [BrokerSync] balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '49756819', '총평가손익': '45412818', '실현손익': '0', '총평가': '-8.73', '총평가수익률': '45412818', '추정자산': '296000'}
2026-08-31 00:42:24 [WARNING] SYSTEM: [BrokerSync] startup sync raw rows=1 nonempty_rows=1 all_blank_rows=False record_name='CpTd0723' prev_next='' rows=[{'종목코드': 'A0569', '종목명': '¹Ì´ÏÄÚ½ºÇÇ F 202609', '구분': '매수', '매매구분': '매수', '잔고수량': '4', '청산가능': '4', '평균가': '1068.47', '매입단가': '1068.47', '현재가': '…
  …
2026-08-31 12:20:01 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 110ms account=333044256
2026-08-31 12:20:02 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-31 12:20:02 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-31 12:20:02 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 110ms account=333044256
2026-08-31 12:26:00 [WARNING] SYSTEM: [RegimeFingerprint] update_live 예외 (5분 스로틀): 'cvd_divergence'
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 8 | 09:45:00 | 10:00:00 | level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13 |
| CRITICAL | `BrokerSync` | 1 | 00:42:24 | 00:42:24 | startup sync 완료: FLAT -> LONG 4계약 @ 1068.47 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-08-31 09:45:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13
2026-08-31 09:51:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=271ms | quality=1.00 | cache_age=163s | exceptions_10m=15
```

</details>

<details><summary>CRITICAL/BrokerSync 원문 1건</summary>

```
2026-08-31 00:42:24 [CRITICAL] SYSTEM: [BrokerSync] startup sync 완료: FLAT -> LONG 4계약 @ 1068.47
```

</details>

**WARNING — 태그 29종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 249 | 00:42:24 | 12:20:02 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 82 | 08:45:06 | 12:20:01 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=4 | gubun='0' | order_no='53' | pending='EXIT_FULL:LONG qty=4 filled=0 order_no=? reason=하드스톱(틱) req_at=08:45:06.058' | … |
| `ChejanMatch` | 82 | 08:45:06 | 12:20:01 | order_no='53' | pending='EXIT_FULL:LONG qty=4 filled=0 order_no=53 reason=하드스톱(틱) req_at=08:45:06.058' | pending_matched=True |
| `OrderSync` | 50 | 09:28:47 | 12:16:32 | 미추적 체결 감지 (pending_miss) order_no=700 side=SHORT qty=1 price=1047.14 before=FLAT |
| `Health` | 48 | 09:00:01 | 11:54:00 | level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0 |
| `RegimeFingerprint` | 38 | 09:00:00 | 12:26:00 | update_live 예외 (5분 스로틀): 'cvd_divergence' |
| `PendingOrder` | 30 | 08:45:06 | 12:20:01 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 4, 'price_hint': 1067.72, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `ExitCooldown` | 28 | 08:45:06 | 12:20:01 | 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06) |
| `ExitFillFlow` | 20 | 08:45:06 | 12:20:01 | after='LONG 3계약 @ 1068.47' | before='LONG 4계약 @ 1068.47' | fill_price=1041.5 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:LONG qty=4 filled=1 order_no=53 reason=하드스톱(틱) req_at=08:45:06.058' | reason='하드스톱(틱)' |
| `BrokerSync` | 16 | 00:42:24 | 08:41:05 | balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '49756819', '총평가손익': '45412818', '실현손익': '0', '총평가': '-8.73', '총평가수익률': '45412818', '추정자산': '296000'} |
| `ExitSendOrderResult` | 11 | 08:45:06 | 11:45:15 | ret=0 kind=하드스톱(틱) direction=LONG qty=4 |
| `TickStop` | 10 | 08:45:06 | 11:45:15 | 스톱 히트 감지 (틱) LONG tick=1041.18 stop=1067.72 → 즉시 처리 예약 |

**채널** — `SYSTEM`×689, `HEALTH`×56

**컴포넌트 상위 15** — `LiveDBG`×249, `ChejanFlow`×82, `ChejanMatch`×82, `Health`×56, `OrderSync`×50, `RegimeFingerprint`×38, `PendingOrder`×30, `ExitCooldown`×28, `ExitFillFlow`×20, `BrokerSync`×17, `ExitSendOrderResult`×11, `TickStop`×10, `ScalerRefresh`×9, `CB`×7, `HealthPolicy`×7

### `logs/20260831_SYSTEM.log` — 650.3KB · 4061행 · 최종 12:26:36

- 형식 평문 · 시각 인식 4048행 · INFO=4048, PLAIN=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:08 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=9328 | 행감지=30s all_threads=True
2026-08-31 00:42:08 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-31 00:42:08 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-31 00:42:08 [INFO] SYSTEM: 미륵이 초기화
2026-08-31 00:42:08 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-28) 종가 버퍼 로드: 384봉
  …
2026-08-31 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-1143,foreign:+1831,institution:-228}
2026-08-31 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:-1143,foreign:+1831,institution:-228}
2026-08-31 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+145827 nonarb=-584219
2026-08-31 12:27:05 [INFO] SYSTEM: [CybosInvestorRaw] program via CpSvr8111(market=1) arb=+145827 nonarb=-584219
2026-08-31 12:27:24 [INFO] SYSTEM: [CybosRT-TICK] #79100 code=A0569 raw_time=122724 parsed=12:27:24 price=1053.54 vol=1 bid1=1053.52 ask1=1053.62 flag=50 side=SELL anchor=0/1
```

</details>

**채널** — `SYSTEM`×4048

**컴포넌트 상위 15** — `CybosInvestorRaw`×826, `CybosRT-TICK`×796, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×208, `PipePerf`×208, `BalanceUI`×186, `CybosEvent`×164, `CybosDailyPnl`×148, `BalanceRefresh`×111, `System`×82, `CybosDailyPnlHeaders`×74, `MicroRegime`×60

### `logs/20260831_SIGNAL.log` — 351.0KB · 3095행 · 최종 12:26:00

- 형식 평문 · 시각 인식 3095행 · WARNING=1310, INFO=1785

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.429
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.425
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.437
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.416
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.412
  …
2026-08-31 12:27:01 [INFO] SIGNAL: [MetaGate][LIVE] skip: blended=0.358 reduce_thr=0.465 take_thr=0.570 (grade=X min_conf=0.620 ens=0.364 meta_raw=0.446 ens_w=0.60)
2026-08-31 12:27:01 [INFO] SIGNAL: 앙상블: dir=-1 conf=36.4% grade=X micro=추세장
2026-08-31 12:27:01 [INFO] SIGNAL: [ATR-Horizon] 진입 호라이즌=1m tf=3.18 → TP1×0.3
2026-08-31 12:27:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: conf미달(0.364<mc0.620)
2026-08-31 12:27:01 [INFO] SIGNAL: [MetaGate] action=skip meta_conf=35.8% size_mult=1.00 reason=meta_skip
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 906 | 09:00:02 | 12:19:01 | 1m 'macro_vix' scale=0.0037 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 186 | 08:45:05 | 12:19:01 | 1m CORE 'cvd_divergence' raw_std≈0(0.0148) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Checklist` | 72 | 09:06:00 | 12:27:01 | 신뢰도 미달 34.9% < 39.9% → 강제 X등급 |
| `Model` | 60 | 09:01:00 | 12:15:00 | 1m 극단 z-score 5개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 42 | 09:01:00 | 12:15:00 | ts=09:00 horizon=1m age=1m max_z=+8.71(va_bandwidth) extreme=5 |
| `WeightCollapse` | 42 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4370 (conf_floor=0.330, min_conf=0.437, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |
| `ConstOut` | 1 | 09:36:00 | 09:36:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외 |

**채널** — `SIGNAL`×3095

**컴포넌트 상위 15** — `ScalerFloor`×966, `SIGNAL`×416, `ScalerRefresh`×213, `Ensemble`×209, `ZeroDiag`×207, `FQAdj`×205, `MetaGate`×192, `Model`×90, `ATR-Horizon`×88, `Checklist`×77, `InstabilityGate`×63, `MicroRegime`×60, `ScalerMonitor`×42, `WeightCollapse`×42, `ToxicityGate`×35

### `logs/20260831_LEARNING.log` — 326.1KB · 2472행 · 최종 12:26:00

- 형식 평문 · 시각 인식 2472행 · WARNING=572, INFO=1900

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:10 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00067 auc=0.357 out_max=0.1503 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00060 auc=0.490 out_max=0.3002 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00056 auc=0.537 out_max=0.2447 (n=135) → 보정 재적용
  …
2026-08-31 12:27:01 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=40.1% 예측=DN 실제=FL)
2026-08-31 12:27:01 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=47.5% 예측=DN 실제=UP)
2026-08-31 12:27:01 [INFO] LEARNING: [Bias⚠] 3m 적중=10%(3/30) UP=2 DN=20 FL=8 [DN편향⚠ 67%]
2026-08-31 12:27:01 [INFO] LEARNING: [MetaConf] LR[혼합] 비동기 학습 완료 (n=263, classes=[0, 1, 2, 3])
2026-08-31 12:27:01 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=25.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 572 | 00:42:10 | 12:15:00 | 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×2472

**컴포넌트 상위 15** — `Calibration`×1118, `LEARNING`×667, `SGD`×208, `sigma`×195, `Bias`×88, `Bias⚠`×68, `MetaConf`×40, `ScalerWarmup`×27, `OnlineLearner`×19, `SHAP`×10, `ExtremityCorrector`×8, `BiasReset`×6, `RF`×5, `Consolidator`×4, `DriftAdjuster`×4

### `logs/20260831_HEALTH.log` — 9.1KB · 66행 · 최종 11:55:00

- 형식 평문 · 시각 인식 66행 · CRITICAL=8, WARNING=48, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0
2026-08-31 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=485ms | quality=0.86 | cache_age=106s | exceptions_10m=0
2026-08-31 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 284ms (표본 20분)
2026-08-31 09:36:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=323ms | quality=0.94 | cache_age=182s | exceptions_10m=9
2026-08-31 09:37:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=432ms | quality=1.00 | cache_age=59s | exceptions_10m=9 [GBM재학습중→lat임계 5000/10000ms]
  …
2026-08-31 11:37:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=258ms | quality=1.00 | cache_age=82s | exceptions_10m=7
2026-08-31 11:38:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=142s | exceptions_10m=7
2026-08-31 11:39:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=275ms | quality=1.00 | cache_age=18s | exceptions_10m=4
2026-08-31 11:54:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=354ms | quality=1.00 | cache_age=182s | exceptions_10m=3
2026-08-31 11:55:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=327ms | quality=1.00 | cache_age=59s | exceptions_10m=3
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 8 | 09:45:00 | 10:00:00 | level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-08-31 09:45:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=434ms | quality=1.00 | cache_age=171s | exceptions_10m=13
2026-08-31 09:51:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=271ms | quality=1.00 | cache_age=163s | exceptions_10m=15
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 48 | 09:00:01 | 11:54:00 | level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0 |

**채널** — `HEALTH`×66

**컴포넌트 상위 15** — `Health`×65, `HealthTrend`×1

### `logs/retrain_intraday_20260831_093701.log` — 2.7KB · 21행 · 최종 09:37:23

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-31 09:37:01,211 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dcb44c89.json
2026-08-31 09:37:04,317 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-31 09:37:23,485 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-08-31 09:37:23,485 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-31 09:37:23,486 [INFO] LEARNING: [Retrain] 완료 | 19.2초 | 성공=1/1 호라이즌
2026-08-31 09:37:23,486 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.3s 데이터=4800행
2026-08-31 09:37:23,488 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dcb44c89.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/20260831_MICRO.log` — 605.1KB · 1618행 · 최종 12:26:38

- 형식 평문 · 시각 인식 1618행 · DEBUG=1618

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1040.62/3 ask1=1040.98/1 mp={'microprice_tick': 1040.89, 'midprice_tick': 1040.8, 'depth_bias_tick': 0.3538} mlofi_tick=None queue=None
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1040.64/1 ask1=1041.34/3 mp={'microprice_tick': 1040.815, 'midprice_tick': 1040.99, 'depth_bias_tick': -0.1948} mlofi_tick=5.9 queue={'depletion_bid': 2.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': 1.0…
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1040.68/1 ask1=1041.34/1 mp={'microprice_tick': 1041.01, 'midprice_tick': 1041.01, 'depth_bias_tick': 0.0431} mlofi_tick=4.2 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1040.72/2 ask1=1041.38/1 mp={'microprice_tick': 1041.16, 'midprice_tick': 1041.05, 'depth_bias_tick': 0.2352} mlofi_tick=8.7333 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1040.74/1 ask1=1041.50/1 mp={'microprice_tick': 1041.12, 'midprice_tick': 1041.12, 'depth_bias_tick': 0.2392} mlofi_tick=5.1167 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
  …
2026-08-31 12:26:38 [DEBUG] MICRO: [MICRO-TICK] #137300 bid1=1053.32/1 ask1=1053.38/1 mp={'microprice_tick': 1053.35, 'midprice_tick': 1053.35, 'depth_bias_tick': -0.1414} mlofi_tick=-8.2 queue={'depletion_bid': 1.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-08-31 12:26:55 [DEBUG] MICRO: [MICRO-TICK] #137400 bid1=1053.38/1 ask1=1053.50/2 mp={'microprice_tick': 1053.42, 'midprice_tick': 1053.44, 'depth_bias_tick': -0.3568} mlofi_tick=3.7 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio'…
2026-08-31 12:27:01 [DEBUG] MICRO: [MICRO-MINUTE] #222 ts=2026-08-31 12:26:00 close=1053.54 bias=-0.001407 slope=0.115476 depth_bias=-0.0376 mlofi_norm=0.027241 mlofi_pressure=1 mlofi_slope=-4.818333 queue_signal=0.0244 queue_ma=-0.0282 queue_momentum=0.0473 depletion=0.5000 refill=0.5000 imbalance…
2026-08-31 12:27:09 [DEBUG] MICRO: [MICRO-TICK] #137500 bid1=1053.60/2 ask1=1053.70/1 mp={'microprice_tick': 1053.6666, 'midprice_tick': 1053.65, 'depth_bias_tick': 0.22} mlofi_tick=-6.0667 queue={'depletion_bid': 0.0, 'depletion_ask': 1.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-08-31 12:27:27 [DEBUG] MICRO: [MICRO-TICK] #137600 bid1=1053.50/1 ask1=1053.60/1 mp={'microprice_tick': 1053.55, 'midprice_tick': 1053.55, 'depth_bias_tick': -0.0585} mlofi_tick=2.95 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
```

</details>

**채널** — `MICRO`×1618

**컴포넌트 상위 15** — `MICRO-TICK`×1396, `MICRO-MINUTE`×222

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 14 |
| 차단(`[차단]`) | 32 |
| 사이저 호출(`[Sizer]`) | 0 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|

**청산 레그 0행** (부분청산 11 · 전량청산 14)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 -6,477,882 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 14건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패 레그 25행 ⚠**(진입 로그 없는 이월 포지션 가능)

### 차단 사유 32건 · 1종

| 건수 | 사유 |
|---|---|
| 32 | Restart Armistice — 재시작 유예 중 (time_ok=True sync=0/2) |

### Circuit Breaker 이벤트 7건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×6
- `연속 손절 2회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 12건 · 최대 7718ms · 5초 초과 1건

상위 — 7718ms, 4859ms, 4813ms, 4796ms, 4407ms, 3046ms, 3000ms, 2750ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:07 | 7718ms | 1376ms | **6342ms (82%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260831_WARN.log`
```
--- ConstOut ×1(표본)
09:36:00 2026-08-31 09:36:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×1(표본)
09:00:07 2026-08-31 09:00:07 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260831.log
--- [CB] ×7(표본)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:30:37 2026-08-31 09:30:37 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:42:52 2026-08-31 09:42:52 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
09:52:39 2026-08-31 09:52:39 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06)
09:30:37 2026-08-31 09:30:37 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:33:37)
09:30:37 2026-08-31 09:30:37 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:33:37)
--- degraded=ON ×8(표본)
09:39:00 2026-08-31 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=494ms | quality=1.00 | cache_age=178s | exceptions_10m=7
09:40:00 2026-08-31 09:40:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=368ms | quality=1.00 | cache_age=55s | exceptions_10m=7
09:41:00 2026-08-31 09:41:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=404ms | quality=1.00 | cache_age=115s | exceptions_10m=6
09:42:00 2026-08-31 09:42:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=340ms | quality=1.00 | cache_age=175s | exceptions_10m=6
--- 메인 스레드 블로킹 ×8(표본)
01:30:03 2026-08-31 01:30:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2328 band=INFO since_pipe_s=NA
08:41:08 2026-08-31 08:41:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3046ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3046 band=INFO since_pipe_s=NA
09:00:07 2026-08-31 09:00:07 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7718ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7718 band=WARN since_pipe_s=0.1
09:01:01 2026-08-31 09:01:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2109ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2109 band=INFO since_pipe_s=0.1
```

### `logs/20260831_SYSTEM.log`
```
--- ConstOut ×5(표본)
09:36:00 2026-08-31 09:36:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:38:00 (const_output)
09:36:00 2026-08-31 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:00 2026-08-31 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=376ms fit=61ms total=440ms
09:37:00 2026-08-31 09:37:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
```

### `logs/20260831_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-08-31 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4370 (conf_floor=0.330, min_conf=0.437, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×2(표본)
09:36:00 2026-08-31 09:36:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+0) → 앙상블 제외
09:37:01 2026-08-31 09:37:01 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-08-31 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-08-31 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=74.4% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-08-31 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=70.4% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-08-31 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=53.6% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.429
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.425
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.437
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.416
--- 안전망 ×8(표본)
09:07:00 2026-08-31 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-31 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-08-31 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-08-31 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260831_LEARNING.log`
```
--- 축퇴 ×8(표본)
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00067 auc=0.357 out_max=0.1503 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00060 auc=0.490 out_max=0.3002 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00056 auc=0.537 out_max=0.2447 (n=135) → 보정 재적용
```

### `logs/20260831_HEALTH.log`
```
--- degraded=ON ×8(표본)
09:39:00 2026-08-31 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=494ms | quality=1.00 | cache_age=178s | exceptions_10m=7
09:40:00 2026-08-31 09:40:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=368ms | quality=1.00 | cache_age=55s | exceptions_10m=7
09:41:00 2026-08-31 09:41:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=404ms | quality=1.00 | cache_age=115s | exceptions_10m=6
09:42:00 2026-08-31 09:42:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=340ms | quality=1.00 | cache_age=175s | exceptions_10m=6
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260831_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:40:57 [WARNING] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72) |
| 10:00 | 장중 초반 | 11 | 09:56:09 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=1045.82 — 진입 경로가 파라미터를 넘기지… |

- 이 로그 생존구간: 00:42 ~ 12:20

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260831_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 34 | 08:40:57 [WARNING] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 14 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 18 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 42 | 09:54:00 [WARNING] update_live 예외 (5분 스로틀): 'cvd_divergence' |
| 12:00 | 장중 중간점 | 6 | 11:54:00 [WARNING] acc30m 단계 전환: WATCH → RESTRICTED (acc=26.7%) |

- 이 로그 생존구간: 00:42 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260831_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=24976 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 193 | 08:54:02 [INFO] #2100 code=A0569 raw_time=85402 parsed=08:54:02 price=1043.10 vol=1 bid1=1042.88 ask1=1043.34 flag=49 side=BU… |
| 10:00 | 장중 초반 | 254 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 176 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 00:42 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260831_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:05 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0148) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 142 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0449) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 275 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0392) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 138 | 09:54:01 [WARNING] 신뢰도 미달 34.0% < 38.6% → 강제 X등급 |
| 12:00 | 장중 중간점 | 171 | 11:54:00 [WARNING] 신뢰도 미달 34.5% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 00:42 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| 20260827 | 15:40 | 로그 본문 |
| 20260826 | 15:40 | 로그 본문 |
| 20260825 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260831** | **12:27** | 로그 본문 |

- 델타 **-193분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 계열
### 부수 확정 사실
### 결정 (오늘은 계획만 — 코드 변경 0, 커밋 0)
### Why
### How to apply
### 검증 (전부 미실시 — 장후 예정)
### 고도화 (섀도만 — 차단 아님)
### 오늘 상태 (장전 시점)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
xit()` 신설
  (`TickTP1`·`TickStop-S0C`·`SchedForceExit` 3곳). 1주 섀도 후 승격.
- **F-2 (P0)** `main.py:16271~16283` — `ret != 0` 3회 재시도(0.5/1/2s) + 다음 분
  재시도 플래그 + 15:44 하드 캡. ⚠ **재시도 전 잔고 재조회 필수**(F-1 ⓒ 재사용) —
  이중 청산 위험은 CLAUDE.md 전환기준 ② 주석이 이미 주간회의 안건으로 못박았다.
  잔고 재확인 없이 재시도만 넣는 것은 **금지**.
- **F-3 (P1)** 15:10 시점 미체결 **진입** 주문 일괄 취소(`kind`가 `ENTRY_*`인 것만).
  `[SchedForceExit] pending_cancel=N건` 계측(4원칙 ③ — 실패 건수 명시).
- **F-4 (P1)** `daily_close()` 마감 요약에 **브로커 종가 포지션 확인** 병기.
- **F-5 (P2)** 08-28 손익 기록 정정 + `strategy_events` `METRIC_REDEFINITION`.
  ⚠ 전환기준 ① 표본을 건드리므로 **사용자 승인 후**. 자동조치 등급 밖.

### Why

절대원칙 §1의 집행이 **단일 시도에 걸려 있었다**(F-2), 그리고 §1이 성립했는지를
**아무도 종가에 확인하지 않았다**(F-4·G-2). 두 구멍이 같은 날 동시에 열려야
사고가 되는데, 08-28에 정확히 그랬다. 손실 546만원의 대부분은 **금요일 15:50에
잔고를 1회 조회하는 것만으로** 회피 가능했다.

### How to apply

장후(15:45 이후) 순서: F-1 테스트 선행 → F-1 → F-2(F-1 ⓒ 의존) → F-3 → F-4.
F-5는 사용자 승인 대기. 회귀 5종 + `test_471_force_exit_reachability` 재실행 필수.

### 검증 (전부 미실시 — 장후 예정)

- `tests/test_505_broker_sync_blank_rows.py` — 08-28 15:30:02 원문 응답을 픽스처로
  고정(`rows=[]`, `summary={'총매매': '49838525', ...}`)해 **이 사고의 지문을 회귀로 박는다.**
- `tests/test_505_direct_exit_retry.py` — 재시도 전 잔고 재조회 호출 확인(이중 청산).
- `tests/test_505_pending_entry_cancel_at_1510.py` — 진입만 취소·청산 보존.
- `tests/test_505_daily_close_position_recon.py` — 엔진 FLAT·브로커 non-FLAT 시 경고.

### 고도화 (섀도만 — 차단 아님)

- **G-1** `position_recon_shadow` — 매분 엔진 포지션 vs `broker_cached` 대사를
  `predictions.db`에 적재. **TR 추가 호출 0회**(08-28 로그가 `broker_cached=0ct`를
  이미 들고 있었다). 갈라짐 노출 지연이 현행 **2일 18시간** → 1분.
- **G-2** 15:50 종가 후 포지션 확인 잡(**알림 전용, 주문 없음**) — 이중 청산 위험 0,
  자동조치 등급 안. F-2와 한 묶음으로 올리지 말 것.
- 둘 다 사고 표본 **n=1** — 313차 원칙, 확정 결론 금지. 승격은 최소 4주 뒤.

### 오늘 상태 (장전 시점)

브랜치 `v9-dev` · HEAD `f01080b` · 설정 불변식 24개 전부 일치 · `.git/index.lock` 없음 ·
전일 EOD 재학습 성공(`data/eod_retrain_done_20260828.txt`) · 08:55 `[PreRetrain]` 스킵
정상 · 08:45:06 이후 포지션 **FLAT** · 09:00:00 `[ConfFloorGuard] 자동진입 하한 도달
불가 (0.3479 < 0.4370)` → 오늘 자동진입 0건 가능성 높음(O-p1).

⚠ **CB② 복원 재검토 기한 2026-08-29 경과** — `CB_CONSEC_STOP_LIMIT=9999` 유지.
오늘이 기한 후 첫 거래일이다. 주간회의 안건.

⚠ 08-31 00:18 `MW0601-20260831-8월손실일-딥다이브.md`(504차)의 8월 net 집계
(−537,103원)에 **오늘 −5,461,928원은 포함돼 있지 않다.** 8월 통산 인용 시 병기할 것.
또한 오늘 손실은 그 문서의 3층(기하·비용·사이징) 어느 것으로도 설명되지 않는
**네 번째 층**(이월 포지션 개장 갭)이며, §5의 「일일 손실 하드 브레이크」로는 막히지
않는다 — 하루가 시작되기 전에 손실이 확정됐다.

**커밋하지 않았다.** 대기: `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` ·
`docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` · `dev_memory/DECISION_LOG.md` ·
`dev_memory/NEXT_TODO.md`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### MW0601 494차 정정 (2026-08-26 14:55)
### MW0601 494차 후속 (2026-08-26 15:10) — F-1′ 적용 완료
### MW0601 494차 후속2 (2026-08-26 15:30) — 커밋으로는 동기화가 안 된다 (실측 확정)
### MW0601 494차 후속3 (2026-08-26 16:40 — 장후 점검)
### 498차 — 장후 자동조치 (MW0601, 2026-08-26 17:30~19:0x · `mireuk-postmarket-autofix` 첫 실행)
### MW0601 499차 (2026-08-27 08:57~09:1x — 장전 점검)
### MW0601 500차 (2026-08-30 — CVD·OFI 유효성 조사 · 5단계 집행)
### MW0601 505차 (2026-08-31 08:57~09:2x — 장전 점검)
```

미완료 체크박스 **2139건** (끝에서 30건)
```
- [ ] **결정 2** CORE 정의 3곳 통합 → `CORE_FEATURES_BY_GROUP` 단일 출처.
- [ ] **결정 3** 97 슈퍼셋 — 컬럼 **삭제 금지**(shape mismatch). 폐기 예정 등록 +
- [ ] SOP §3에 **구성적 중복**(`f = g(h)` 소스 검사) 신설 — 상관 재기 전에 잡는다
- [ ] SOP §2 D형 스크린을 **CORE 우선** 적용 규약
- [ ] 26주 WFA L1→L2→L3 재실행 — 🔴 **위 4단계 전에는 금지**.
- [ ] `vpin` 14일 max **0.3822** — 설계 임계 0.5/0.7/0.9 대비 `signal_level` 영구 LOW.
- [ ] **2026-05-11·05-12 net 이상치 원인 확인** — `commission_rate_recon.py
- [ ] **D2 체인 불연속 19건 잔여 재확인** — `broker_net_chain_audit.py` D2
- [ ] **판정창 2026-09-01~ 진입 후 주간 확인** — `trend_efficiency_gate_shadow`에
- [ ] **[18] regime_exhaustion_watch와 이중계상 확인** — MW0602 실측에서 두 채널이
- [ ] **F-1 blank-rows 폴백 재설계** `main.py:17107~17132`
- [ ] **F-1 테스트 선행** `tests/test_505_broker_sync_blank_rows.py` —
- [ ] **F-2 `BrokerDirectExit` 재시도** `main.py:16271~16283` —
- [ ] **F-2 테스트** `tests/test_505_direct_exit_retry.py` — 재시도 전 잔고 재조회
- [ ] `config/settings.py` 신설 — `BROKER_DIRECT_EXIT_RETRY = 3` ·
- [ ] **F-3 15:10 미체결 진입 주문 일괄 취소** — `SchedForceExit` 경로에
- [ ] **F-4 `daily_close()` 마감 요약에 브로커 종가 포지션 병기** —
- [ ] **F-5 08-28 손익 기록 정정** 🔴 **사용자 승인 필요 · 자동조치 등급 밖**
- [ ] **G-1 `position_recon_shadow`** — 매분 엔진 포지션 vs `broker_cached` 대사를
- [ ] **G-2 15:50 종가 후 포지션 확인 잡** — **알림 전용, 주문 없음**(이중 청산
- [ ] **O-p1 (장중→장후)** `[ConfFloorGuard]`(09:00:00, 출력상한 0.3479 < 필요 0.4370)
- [ ] **O-p2 (장후)** `[CybosOrder] ret=4` 의미 — 일시적/구조적. 과거 로그 전수
- [ ] **O-p3 (장후)** 08-28 주문번호 3639 주체(사람/엔진) — `ensemble_decisions`
- [ ] **O-p4 (장후)** `[Canary] z경고피처=12개`가 임계 12와 **정확히 같다**(경계 접촉).
- [ ] **O-p5 (장후)** 개장 버스트 메인 정지 — 오늘 **7,718ms**(0827 9,500ms 대비).
- [ ] **O-p6 (장후)** `session_state.json`에 `p8_last_success_date`·
- [ ] 🔴 **오늘 15:45~16:00 증권사 화면에서 선물 잔고 0 직접 확인** — 프로그램
- [ ] 🔴 **CB② 복원 재검토 기한 2026-08-29 경과** — `CB_CONSEC_STOP_LIMIT=9999` 유지.
- [ ] **2026-08-28(금) 매일점검 미실행 원인 확인** — 리포트·증거 다이제스트 둘 다
- [ ] **커밋 대기 (이 세션은 커밋하지 않았다)** — ⚠ `git add .` 금지
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
정반대 사고). `[SchedForceExit] pending_cancel=N건` +
      취소 실패 건수 명시(계측 4원칙 ③)
- [ ] **F-4 `daily_close()` 마감 요약에 브로커 종가 포지션 병기** —
      `순손익: … | 브로커 종가 포지션 확인: FLAT ✅` / 불일치 시 경고 + 알림 등급 상향
      (계측 4원칙 ⑤ — 이번에 빠진 축은 **포지션 축**)
- [ ] **F-5 08-28 손익 기록 정정** 🔴 **사용자 승인 필요 · 자동조치 등급 밖**
      ⓐ `trades` 08-28 15:30:05~07 4행을 "청산 아님/신규 진입" 표기(삭제 금지)
      ⓑ 08-31 08:45:06 3레그를 그 진입에 귀속(수집기 §5 `귀속 실패 레그 3행`)
      ⓒ `strategy_events` `METRIC_REDEFINITION` — 08-28~08-31 손익 시계열 불연속
      ⚠ 전환기준 ①(4주 통산) 판정 표본을 건드린다

**고도화 — 섀도만, 차단 아님 (n=1, 313차 원칙: 확정 결론 금지)**

- [ ] **G-1 `position_recon_shadow`** — 매분 엔진 포지션 vs `broker_cached` 대사를
      `predictions.db` 적재. **TR 추가 호출 0회**(08-28 로그가 `broker_cached=0ct`를
      이미 들고 있었다). 검증: 08-28 15:20:38~15:30:07 리플레이로 불일치 포착 확인
- [ ] **G-2 15:50 종가 후 포지션 확인 잡** — **알림 전용, 주문 없음**(이중 청산
      위험 0 → 자동조치 등급 안). 검증: 08-28 15:50 리플레이 탐지 + 최근 20거래일
      오탐 0. ⚠ **F-2와 한 묶음으로 올리지 말 것** — 성격이 다르다

**관측 (장중·장후가 판정/보류/이월 중 하나로 닫는다 — 미처분 금지)**

- [ ] **O-p1 (장중→장후)** `[ConfFloorGuard]`(09:00:00, 출력상한 0.3479 < 필요 0.4370)
      실효성 — 오늘 자동 진입 실제 0건인가 · 0건이면 이 경고가 원인인가 · 매일 뜨는가
- [ ] **O-p2 (장후)** `[CybosOrder] ret=4` 의미 — 일시적/구조적. 과거 로그 전수
      `ret=` 분포 + Cybos 반환코드 표. **F-2 설계의 선행 조건**
- [ ] **O-p3 (장후)** 08-28 주문번호 3639 주체(사람/엔진) — `ensemble_decisions`
      08-28 14:30~14:32 행 유무. `pending_matched=False`라 엔진 자신도 모른다
- [ ] **O-p4 (장후)** `[Canary] z경고피처=12개`가 임계 12와 **정확히 같다**(경계 접촉).
      최근 5거래일 추이 + `CanaryShadow` 분모 대조
- [ ] **O-p5 (장후)** 개장 버스트 메인 정지 — 오늘 **7,718ms**(0827 9,500ms 대비).
      CB⑤ 잔차 6,342ms(82%)는 파이프라인 밖 — 482차 F-3 섀도 누적
- [ ] **O-p6 (장후)** `session_state.json`에 `p8_last_success_date`·
      `eod_retrain_ok_date` 부재(08:55 로그가 "session_state 미기록 보완"이라 자백).
      오늘 EOD 후 두 키가 기록되는지 — 계측 4원칙 ④ 계열

**사용자 조치 (리포트 §사용자 조치와 동일)**

- [ ] 🔴 **오늘 15:45~16:00 증권사 화면에서 선물 잔고 0 직접 확인** — 프로그램
      마감 요약을 믿지 말 것(08-28에 그 요약이 틀렸다). 546만원 중 대부분은
      금요일 저녁 1회 조회로 회피 가능했다
- [ ] 🔴 **CB② 복원 재검토 기한 2026-08-29 경과** — `CB_CONSEC_STOP_LIMIT=9999` 유지.
      오늘이 기한 후 첫 거래일. ⓐ 2~3 복원 / ⓑ 재연기(사유+다음 기한 기록) /
      ⓒ 전환기준 ⑤ 재정의. **주간회의 안건**
- [ ] **2026-08-28(금) 매일점검 미실행 원인 확인** — 리포트·증거 다이제스트 둘 다
      없음(금요일 주간 산출물 3종만 15:50 생성). 하필 사고 원인 전부가 그날.
      예약 실패인지 주간점검이 대체 처리했는지
- [ ] **커밋 대기 (이 세션은 커밋하지 않았다)** — ⚠ `git add .` 금지
      (실질 변경 0건 · EOL 파생 513건). 경로 명시:
      `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` ·
      `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` ·
      `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md`

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

### `data/heartbeat_MW0601_20260831.json` — 244B · 08-31 12:26:42
```json
{
 "pid": 24976,
 "written_at": "2026-08-31T12:27:12",
 "beat_epoch": 1788146830.5814579,
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

### `docs/정기점검/매일점검` — 84개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260831-점검리포트.md` | 52.7KB | 08-31 09:15 |
| `docs/정기점검/매일점검/evidence_MW0601-20260831_pre.md` | 57.8KB | 08-31 09:00 |
| `docs/정기점검/매일점검/MW0601-20260831-8월손실일-딥다이브.md` | 22.2KB | 08-31 00:18 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.2KB | 08-31 00:05 |
| `docs/정기점검/매일점검/MW0601-20260827-점검리포트.md` | 90.4KB | 08-27 12:43 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_intra.md` | 66.2KB | 08-27 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_pre.md` | 52.6KB | 08-27 09:00 |
| `docs/정기점검/매일점검/MW0601-20260826-점검리포트.md` | 225.1KB | 08-26 19:04 |

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

1. `logs/20260831_WARN.log`: ERROR 이상 9건
2. `logs/20260831_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
3. `logs/20260831_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
4. `logs/20260831_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
5. `logs/20260831_HEALTH.log`: ERROR 이상 8건
6. 메인 스레드 정지 5초 초과 **1건** (최대 7718ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260831_WARN.log`: **degraded=ON** 8건(표본)
8. `logs/20260831_WARN.log`: **ConstOut** 1건(표본)
9. `logs/20260831_SYSTEM.log`: **ConstOut** 5건(표본)
10. `logs/20260831_SIGNAL.log`: **WeightCollapse** 8건(표본)
11. `logs/20260831_SIGNAL.log`: **ConstOut** 2건(표본)
12. `logs/20260831_LEARNING.log`: **축퇴** 8건(표본)
13. `logs/20260831_HEALTH.log`: **degraded=ON** 8건(표본)
14. 미커밋 변경 515건 (실질 2건 · 코드 0건 · EOL 파생 511건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260831*.log` (Windows) / `grep 강제청산 logs/*20260831*.log`*