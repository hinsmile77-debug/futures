# 미륵이 증거 다이제스트 — 2026-08-31 / PRE

- 생성 2026-08-31 09:00:10 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/zealous-festive-lovelace/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260831` · `2026-08-31` · `260831` · `0831`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260831.log` | 498B | 08-31 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260831.log` | 558B | 08-31 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260831.json` | 244B | 08-31 09:00 |
| `launcher_{DATE}_004147_4902.log` | 1 | `logs/Mireuk_batch/launcher_20260831_004147_4902.log` | 16.9KB | 08-31 01:02 |
| `launcher_{DATE}_012504_13379.log` | 1 | `logs/Mireuk_batch/launcher_20260831_012504_13379.log` | 16.5KB | 08-31 01:30 |
| `launcher_{DATE}_013454_15309.log` | 1 | `logs/Mireuk_batch/launcher_20260831_013454_15309.log` | 16.8KB | 08-31 01:41 |
| `launcher_{DATE}_084001_297.log` | 1 | `logs/Mireuk_batch/launcher_20260831_084001_297.log` | 69.7KB | 08-31 09:00 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260831.log` | 2.9KB | 08-31 09:00 |
| `{DATE}_DATA.log` | 1 | `logs/20260831_DATA.log` | 1.1KB | 08-31 09:00 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260831_DEBUG.log` | 626B | 08-31 09:00 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260831_HEALTH.log` | 142B | 08-31 09:00 |
| `{DATE}_HOGA.log` | 1 | `logs/20260831_HOGA.log` | 1.4MB | 08-31 09:00 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260831_LEARNING.log` | 201.5KB | 08-31 09:00 |
| `{DATE}_MICRO.log` | 1 | `logs/20260831_MICRO.log` | 37.1KB | 08-31 09:00 |
| `{DATE}_PROBE.log` | 1 | `logs/20260831_PROBE.log` | 2.0KB | 08-31 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260831_SIGNAL.log` | 29.8KB | 08-31 09:00 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260831_SYSTEM.log` | 52.4KB | 08-31 09:00 |
| `{DATE}_TRADE.log` | 1 | `logs/20260831_TRADE.log` | 4.2KB | 08-31 08:45 |
| `{DATE}_WARN.log` | 1 | `logs/20260831_WARN.log` | 15.9KB | 08-31 09:00 |

## 2. 코드·커밋 상태

- HEAD `f01080b` · 브랜치 `v9-dev` · 미커밋 513건 · 실질 변경 0건 · 코드(.py) 0건 · EOL 파생 513건 (추적변경 513 · 미추적 0 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
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
… 외 473건
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

_본문 미열람(설정): `20260831_HOGA.log` 1.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `20260831_PROBE.log`, `launcher_20260831_084001_297.log`, `launcher_20260831_004147_4902.log`, `launcher_20260831_013454_15309.log`, `launcher_20260831_012504_13379.log`, `20260831_DEBUG.log`, `mainstall_traceback_20260831.log`, `freeze_sentinel_20260831.log`_

### `logs/20260831_TRADE.log` — 4.2KB · 31행 · 최종 08:45:06

- 형식 평문 · 시각 인식 31행 · WARNING=14, INFO=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:18 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-31 00:42:22 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-31 00:42:24 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=4 entry=1068.47 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-08-31 00:42:24 [WARNING] TRADE: [Position] 브로커 기준 동기화: LONG 4계약 @ 1068.47 | 손절=1067.72
2026-08-31 01:25:35 [WARNING] TRADE: [Position] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72)
  …
2026-08-31 08:45:06 [INFO] TRADE: [Position] 체결부분청산 2계약 @ 1041.18 | 잔여=1계약 | PnL=-27.29pt (-2,749,964원) | 하드스톱(틱)
2026-08-31 08:45:06 [INFO] TRADE: [체결청산-부분] LONG 2계약 @ 1041.18 | PnL=-27.29pt (-2,749,964원) | 잔여=1계약 | 사유=하드스톱(틱)
2026-08-31 08:45:06 [INFO] TRADE: [Chejan] 상태=체결 주문번호=53 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-31 08:45:06 [INFO] TRADE: [Position] 체결청산 LONG @ 1041.62 | PnL=-26.85pt (-1,352,982원) | 하드스톱(틱)
2026-08-31 08:45:06 [INFO] TRADE: [청산 완료] PnL=-27.10pt (-5,461,928원) | 포지션 합계 -5,461,928원 (레그 3)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Position` | 7 | 00:42:24 | 08:41:05 | 브로커 기준 동기화: LONG 4계약 @ 1068.47 | 손절=1067.72 |
| `PositionFallback` | 4 | 00:42:24 | 08:41:05 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=4 entry=1068.47 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `PositionDiag` | 3 | 01:25:35 | 08:40:57 | restore source=sync_from_broker:LONG saved_at=2026-08-31T00:42:24.750030 last_update_ts=2026-08-31T00:42:24.750030 |

**채널** — `TRADE`×31

**컴포넌트 상위 15** — `Position`×11, `ProfitGuard`×4, `PositionFallback`×4, `Chejan`×4, `PositionDiag`×3, `체결청산-부분`×2, `TickStop-S0C`×1, `주문요청`×1, `청산 완료`×1

### `logs/20260831_WARN.log` — 15.9KB · 80행 · 최종 09:00:07

- 형식 평문 · 시각 인식 80행 · CRITICAL=1, WARNING=79

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 0ms
2026-08-31 00:42:24 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 140ms account=333044256
2026-08-31 00:42:24 [WARNING] SYSTEM: [BrokerSync] balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '49756819', '총평가손익': '45412818', '실현손익': '0', '총평가': '-8.73', '총평가수익률': '45412818', '추정자산': '296000'}
2026-08-31 00:42:24 [WARNING] SYSTEM: [BrokerSync] startup sync raw rows=1 nonempty_rows=1 all_blank_rows=False record_name='CpTd0723' prev_next='' rows=[{'종목코드': 'A0569', '종목명': '¹Ì´ÏÄÚ½ºÇÇ F 202609', '구분': '매수', '매매구분': '매수', '잔고수량': '4', '청산가능': '4', '평균가': '1068.47', '매입단가': '1068.47', '현재가': '…
  …
2026-08-31 09:00:02 [WARNING] SYSTEM: [CB⑤] 파이프라인 1376ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s]
2026-08-31 09:00:07 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7718ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7718 band=WARN since_pipe_s=0.1
2026-08-31 09:00:07 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260831.log
2026-08-31 09:00:29 [WARNING] SYSTEM: [LiveDBG] ConfTrend SLOW total 234ms rows=1 | import=0ms completed_map=62ms db_query(rows=1)=31ms arithmetic=16ms table_update=109ms row_calc=0ms tooltip_calc=0ms qt_apply=0ms scroll=16ms
2026-08-31 09:00:29 [WARNING] SYSTEM: [LiveDBG] ConfTrendWidget.refresh slow 234ms
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `BrokerSync` | 1 | 00:42:24 | 00:42:24 | startup sync 완료: FLAT -> LONG 4계약 @ 1068.47 |

<details><summary>CRITICAL/BrokerSync 원문 1건</summary>

```
2026-08-31 00:42:24 [CRITICAL] SYSTEM: [BrokerSync] startup sync 완료: FLAT -> LONG 4계약 @ 1068.47
```

</details>

**WARNING — 태그 17종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 30 | 00:42:24 | 09:00:29 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `BrokerSync` | 16 | 00:42:24 | 08:41:05 | balance result rows=1 nonempty=1 summary_nonblank=True probe_nonblank=True summary={'총매매': '49756819', '총평가손익': '45412818', '실현손익': '0', '총평가': '-8.73', '총평가수익률': '45412818', '추정자산': '296000'} |
| `Position` | 6 | 01:25:35 | 08:40:57 | 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72) |
| `ChejanFlow` | 4 | 08:45:06 | 08:45:06 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=4 | gubun='0' | order_no='53' | pending='EXIT_FULL:LONG qty=4 filled=0 order_no=? reason=하드스톱(틱) req_at=08:45:06.058' | … |
| `ChejanMatch` | 4 | 08:45:06 | 08:45:06 | order_no='53' | pending='EXIT_FULL:LONG qty=4 filled=0 order_no=53 reason=하드스톱(틱) req_at=08:45:06.058' | pending_matched=True |
| `ExitFillFlow` | 3 | 08:45:06 | 08:45:06 | after='LONG 3계약 @ 1068.47' | before='LONG 4계약 @ 1068.47' | fill_price=1041.5 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:LONG qty=4 filled=1 order_no=53 reason=하드스톱(틱) req_at=08:45:06.058' | reason='하드스톱(틱)' |
| `PendingOrder` | 2 | 08:45:06 | 08:45:06 | set {'kind': 'EXIT_FULL', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 4, 'price_hint': 1067.72, 'reason': '하드스톱(틱)', 'hint_source': 'stop_tick', 'atr': 0.0, 'grade': '', 'stage': None, 'order_no': '… |
| `ExitCooldown` | 2 | 08:45:06 | 08:45:06 | 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06) |
| `Canary` | 2 | 08:55:06 | 08:55:06 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `PipePerf` | 2 | 09:00:01 | 09:00:01 | total=1376ms | S0=4ms S1=8ms S2=0ms S3=0ms S4=68ms S5=584ms S6=681ms S7=29ms S8=3ms |
| `CB⑤` | 2 | 09:00:02 | 09:00:02 | 파이프라인 1376ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `TickStop` | 1 | 08:45:06 | 08:45:06 | 스톱 히트 감지 (틱) LONG tick=1041.18 stop=1067.72 → 즉시 처리 예약 |

**채널** — `SYSTEM`×79, `HEALTH`×1

**컴포넌트 상위 15** — `LiveDBG`×30, `BrokerSync`×17, `Position`×6, `ChejanFlow`×4, `ChejanMatch`×4, `ExitFillFlow`×3, `PendingOrder`×2, `ExitCooldown`×2, `Canary`×2, `PipePerf`×2, `CB⑤`×2, `TickStop`×1, `ExitSendOrderResult`×1, `CB`×1, `RegimeFingerprint`×1

### `logs/20260831_SYSTEM.log` — 52.4KB · 391행 · 최종 09:00:08

- 형식 평문 · 시각 인식 378행 · INFO=378, PLAIN=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:08 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=9328 | 행감지=30s all_threads=True
2026-08-31 00:42:08 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-31 00:42:08 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-31 00:42:08 [INFO] SYSTEM: 미륵이 초기화
2026-08-31 00:42:08 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-28) 종가 버퍼 로드: 384봉
  …
2026-08-31 09:00:36 [INFO] SYSTEM: [CybosRT-TICK] #3500 code=A0569 raw_time=90035 parsed=09:00:35 price=1040.86 vol=1 bid1=1040.58 ask1=1040.92 flag=50 side=SELL anchor=0/1
2026-08-31 09:00:39 [INFO] SYSTEM: [CybosRT-TICK] #3600 code=A0569 raw_time=90039 parsed=09:00:39 price=1038.92 vol=1 bid1=1038.68 ask1=1039.16 flag=50 side=SELL anchor=0/1
2026-08-31 09:00:43 [INFO] SYSTEM: [CybosRT-TICK] #3700 code=A0569 raw_time=90043 parsed=09:00:43 price=1036.78 vol=1 bid1=1036.76 ask1=1037.08 flag=49 side=BUY anchor=1/0
2026-08-31 09:00:47 [INFO] SYSTEM: [CybosRT-TICK] #3800 code=A0569 raw_time=90047 parsed=09:00:47 price=1037.58 vol=1 bid1=1037.50 ask1=1037.64 flag=49 side=BUY anchor=1/0
2026-08-31 09:00:53 [INFO] SYSTEM: [CybosRT-TICK] #3900 code=A0569 raw_time=90053 parsed=09:00:53 price=1037.54 vol=1 bid1=1037.42 ask1=1037.58 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×378

**컴포넌트 상위 15** — `CybosRT-TICK`×44, `CybosSub`×42, `System`×40, `SYSTEM`×21, `BalanceUI`×21, `TickUI`×16, `CybosRT-ROLLOVER`×15, `BAR-CLOSE`×15, `CVD-ANCHOR`×15, `BrokerSync`×11, `Notify`×11, `PreMarket`×9, `Account`×8, `CybosDailyPnl`×8, `WarmupRetrain`×8

### `logs/20260831_SIGNAL.log` — 29.8KB · 248행 · 최종 09:00:02

- 형식 평문 · 시각 인식 248행 · WARNING=109, INFO=139

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.429
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.425
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.437
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.416
2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.412
  …
2026-08-31 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4375 → floor=0.50 적용 (z-score 폭발 방지)
2026-08-31 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0463 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-31 09:00:02 [WARNING] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1039 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-31 09:00:02 [INFO] SIGNAL: [ScalerRefresh] ts=08:59 trigger=C_PERIODIC elapsed=infmin n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-08-31 09:00:29 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → GAP_OPEN: 시초가 급변 — 고신뢰·소규모 진입만 허용
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 66 | 08:45:05 | 09:00:02 | 1m CORE 'cvd_divergence' raw_std≈0(0.0148) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerFloor` | 42 | 09:00:02 | 09:00:02 | 1m 'macro_vix' scale=0.0037 → floor=0.10 적용 (z-score 폭발 방지) |
| `ConfFloorGuard` | 1 | 09:00:00 | 09:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4370 (conf_floor=0.330, min_conf=0.437, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×248

**컴포넌트 상위 15** — `ScalerFloor`×102, `ScalerRefresh`×73, `DynMC`×28, `Model`×24, `TimeRouter`×6, `EnsembleGater`×4, `FeatureBuilder`×4, `SIGNAL`×2, `GapOffset`×1, `DayRegimeShadow`×1, `ConfFloorGuard`×1, `Ensemble`×1, `ZeroDiag`×1

### `logs/20260831_LEARNING.log` — 201.5KB · 1125행 · 최종 09:00:02

- 형식 평문 · 시각 인식 1125행 · WARNING=560, INFO=565

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 00:42:10 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00067 auc=0.357 out_max=0.1503 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00060 auc=0.490 out_max=0.3002 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-08-31 00:42:10 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00056 auc=0.537 out_max=0.2447 (n=135) → 보정 재적용
  …
2026-08-31 08:55:05 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=14885, ver=5)
2026-08-31 08:55:06 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-31 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-08-31 09:00:00 [INFO] LEARNING: [sigma] sigma_at_t=0.0000% buf_n=0 nonzero=0 prev_p=0.00 cur_p=1039.18
2026-08-31 09:00:02 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=500 feat=97
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 560 | 00:42:10 | 08:40:57 | 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×1125

**컴포넌트 상위 15** — `Calibration`×1092, `ExtremityCorrector`×8, `ScalerWarmup`×7, `RF`×4, `Consolidator`×4, `DriftAdjuster`×4, `SHAP`×4, `MetaConf`×1, `sigma`×1

### `logs/20260831_HEALTH.log` — 142B · 1행 · 최종 09:00:01

- 형식 평문 · 시각 인식 1행 · WARNING=1

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0
  …
2026-08-31 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 1 | 09:00:01 | 09:00:01 | level=WARNING degraded=OFF | latency=1376ms | quality=0.86 | cache_age=46s | exceptions_10m=0 |

**채널** — `HEALTH`×1

**컴포넌트 상위 15** — `Health`×1

### `logs/20260831_MICRO.log` — 37.1KB · 110행 · 최종 09:00:07

- 형식 평문 · 시각 인식 110행 · DEBUG=110

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=1040.62/3 ask1=1040.98/1 mp={'microprice_tick': 1040.89, 'midprice_tick': 1040.8, 'depth_bias_tick': 0.3538} mlofi_tick=None queue=None
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=1040.64/1 ask1=1041.34/3 mp={'microprice_tick': 1040.815, 'midprice_tick': 1040.99, 'depth_bias_tick': -0.1948} mlofi_tick=5.9 queue={'depletion_bid': 2.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 2.0, 'bid_cancel_add_ratio': 1.0…
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=1040.68/1 ask1=1041.34/1 mp={'microprice_tick': 1041.01, 'midprice_tick': 1041.01, 'depth_bias_tick': 0.0431} mlofi_tick=4.2 queue={'depletion_bid': -0.0, 'depletion_ask': 2.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=1040.72/2 ask1=1041.38/1 mp={'microprice_tick': 1041.16, 'midprice_tick': 1041.05, 'depth_bias_tick': 0.2352} mlofi_tick=8.7333 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-08-31 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=1040.74/1 ask1=1041.50/1 mp={'microprice_tick': 1041.12, 'midprice_tick': 1041.12, 'depth_bias_tick': 0.2392} mlofi_tick=5.1167 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
  …
2026-08-31 09:00:38 [DEBUG] MICRO: [MICRO-TICK] #7100 bid1=1038.86/2 ask1=1039.28/2 mp={'microprice_tick': 1039.07, 'midprice_tick': 1039.07, 'depth_bias_tick': -0.208} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-08-31 09:00:42 [DEBUG] MICRO: [MICRO-TICK] #7200 bid1=1037.00/1 ask1=1037.40/1 mp={'microprice_tick': 1037.2, 'midprice_tick': 1037.2, 'depth_bias_tick': -0.0418} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0…
2026-08-31 09:00:46 [DEBUG] MICRO: [MICRO-TICK] #7300 bid1=1037.26/1 ask1=1037.32/1 mp={'microprice_tick': 1037.29, 'midprice_tick': 1037.29, 'depth_bias_tick': -0.0897} mlofi_tick=3.1167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rati…
2026-08-31 09:00:50 [DEBUG] MICRO: [MICRO-TICK] #7400 bid1=1037.72/1 ask1=1038.00/1 mp={'microprice_tick': 1037.86, 'midprice_tick': 1037.86, 'depth_bias_tick': -0.9001} mlofi_tick=29.2167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_rat…
2026-08-31 09:00:57 [DEBUG] MICRO: [MICRO-TICK] #7500 bid1=1038.22/1 ask1=1038.36/1 mp={'microprice_tick': 1038.29, 'midprice_tick': 1038.29, 'depth_bias_tick': 0.0} mlofi_tick=4.5667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
```

</details>

**채널** — `MICRO`×110

**컴포넌트 상위 15** — `MICRO-TICK`×95, `MICRO-MINUTE`×15

### `logs/20260831_DATA.log` — 1.1KB · 5행 · 최종 09:00:00

- 형식 평문 · 시각 인식 5행 · INFO=5

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-31 08:58:09 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=155238 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-31 08:58:09 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-31 08:58:39 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=155250 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-31 08:58:39 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-31 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
  …
2026-08-31 08:58:09 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=155238 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-31 08:58:09 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-31 08:58:39 [INFO] DATA: [CybosInvestor] futures supported=False source=FutureMst_oi foreign=+0 individual=+0 institution=+0 oi=155250 call_foreign=+0 put_foreign=+0 option_supported=False reason=Cybos 선물 투자자 TR 미발견; 미결제약정만 제공
2026-08-31 08:58:39 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=False program_supported=False option_supported=False futures_source=FutureMst_oi program_source=runtime_disabled
2026-08-31 09:00:00 [INFO] DATA: [DivergencePanel] source=cybos status=unavailable div=+0 futures(fi=+0 rt=+0 inst=+0) call(fi=+0 rt=+0) put(fi=+0 rt=+0) bias(fi=0.00 rt=0.00) program(arb=+0 nonarb=+0 total=+0)
```

</details>

**채널** — `DATA`×5

**컴포넌트 상위 15** — `CybosInvestor`×4, `DivergencePanel`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 1 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 포지션 0건 · 승 0 (—) · 합계 +0.00pt (+0원)  ※ 레그 0행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|

**청산 레그 0행** (부분청산 2 · 전량청산 1)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|

**청산 사유 분포(레그 단위)** — 

**정합성**: 레그합 -5,461,928 = 포지션합 +0 → **불일치 ⚠** · `[청산 완료]` 1건 = 조립 포지션 0건 → **불일치 ⚠** · **귀속 실패 레그 3행 ⚠**(진입 로그 없는 이월 포지션 가능)

### Circuit Breaker 이벤트 1건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 3건 · 최대 7718ms · 5초 초과 1건

상위 — 7718ms, 3046ms, 2328ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:07 | 7718ms | 1376ms | **6342ms (82%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260831_WARN.log`
```
--- Traceback ×1(표본)
09:00:07 2026-08-31 09:00:07 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260831.log
--- [CB] ×1(표본)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×2(표본)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06)
08:45:06 2026-08-31 08:45:06 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 08:48:06)
--- 메인 스레드 블로킹 ×3(표본)
01:30:03 2026-08-31 01:30:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2328 band=INFO since_pipe_s=NA
08:41:08 2026-08-31 08:41:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3046ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3046 band=INFO since_pipe_s=NA
09:00:07 2026-08-31 09:00:07 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7718ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7718 band=WARN since_pipe_s=0.1
```

### `logs/20260831_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:00 2026-08-31 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4370 (conf_floor=0.330, min_conf=0.437, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- 기동 복원 ×8(표본)
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.429
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.425
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.437
00:42:06 2026-08-31 00:42:06 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.416
```

### `logs/20260831_LEARNING.log`
```
--- 축퇴 ×8(표본)
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00064 auc=0.471 out_max=0.3503 (기준 auc<0.53 and span<0.020, 기저율=0.3500 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00067 auc=0.357 out_max=0.1503 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00060 auc=0.490 out_max=0.3002 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
00:42:10 2026-08-31 00:42:10 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00056 auc=0.537 out_max=0.2447 (n=135) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260831_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:40:57 [WARNING] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72) |

- 이 로그 생존구간: 00:42 ~ 08:45

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260831_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 34 | 08:40:57 [WARNING] 이전 포지션 복원: LONG 4계약 @ 1068.47 (손절=1067.72) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 12 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 00:42 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260831_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 106 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=24976 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 113 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 78 | 08:54:02 [INFO] #2100 code=A0569 raw_time=85402 parsed=08:54:02 price=1043.10 vol=1 bid1=1042.88 ask1=1043.34 flag=49 side=BU… |

- 이 로그 생존구간: 00:42 ~ 09:00

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260831_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:05 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0148) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 120 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0449) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 113 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0392) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 00:42 ~ 09:00

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
| **오늘 20260831** | **09:00** | 로그 본문 |

- 델타 **-400분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### G. 🔴 사고 1건 — 테스트가 사용자 `ui_prefs.json`을 덮어썼다
### H. 부수 발견 — 별도 확인 필요
## 2026-08-31 (MW0601 504차 후속 — 기동 패널 복원 4단계 체인이 한 번도 실행된 적이 없었다)
### 🔴 근본 원인 — 워커 스레드에서 예약한 QTimer는 발화하지 않는다
### 지문은 로그에 그대로 있었다 — 아무도 안 봤을 뿐이다
### 조치 — 새 기전을 만들지 않는다
### 라이브 검증 — 같은 로그 파일 안에서 before/after 대조
### 회귀 고정
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
9** · pytest 41 passed ·
회귀 5종(`dashboard_smoke`·`477_f4`·`477_gr3`·`497_pnl_axis`·`457_fallback`) OK ·
`ui_prefs.json` 무결. **라이브 매매 상수 무변경** — 표시 계층만 바뀌었다.

---

## 2026-08-31 (MW0601 504차 후속 — 기동 패널 복원 4단계 체인이 한 번도 실행된 적이 없었다)

**계기**: 504차로 붙인 손익추이2 탭에 데이터가 안 올라온다는 사용자 지적.
조사해 보니 **신규 결함이 아니라 기동 경로의 잠복 결함**이었고, 막혀 있던 것은
손익추이2 하나가 아니라 **패널 4종 전부**였다.

### 🔴 근본 원인 — 워커 스레드에서 예약한 QTimer는 발화하지 않는다

`_restore_panels_bg()`가 `threading.Thread`로 띄운 **워커 스레드** 안에서
`_QTimer.singleShot(0, _stage1)`로 4단계 체인을 시작하고 있었다. 타이머는
**호출한 스레드에 붙는데** 그 스레드에는 Qt 이벤트 루프가 없다 — 그래서
`_stage1`이 한 번도 발화하지 않았다.

환경에서 직접 재현했다(PyQt5 / py37_32):

```
메인 스레드에서 singleShot 예약 → 발화 True
워커 스레드에서 singleShot 예약 → 발화 False
```

### 지문은 로그에 그대로 있었다 — 아무도 안 봤을 뿐이다

```
[LiveDBG] _apply 시작 (4단계 체인)      ← 매 기동마다 찍힌다
[LiveDBG] _apply update_learning …ms    ← 전 기간 로그에 단 한 줄도 없다
[LiveDBG] _apply update_efficacy …ms    ← 없다
[LiveDBG] _apply update_trend …ms       ← 없다
[LiveDBG] _apply pnl_history …ms        ← 없다
```

⇒ **기동 시 자가학습·효과검증·추이·손익추이 4개 패널이 복원된 적이 없다.**
거래일에는 이후 이벤트 구동 갱신(`_record_trade_result`·`daily_close`·청산 콜백 등)이
채워줘서 드러나지 않았고, **거래가 없는 날에만** 빈 화면으로 보였다.
게다가 각 단계의 예외는 `logger.debug`로 삼켜져 흔적조차 남지 않는다 —
"시작 로그는 있는데 완료 로그가 없다"가 유일한 단서였다.

⚠ FP-CRITICAL 죽은 게이트(2개월 PSI=0.0)·TOX 죽은 섀도(한 달)와 **같은 계열**이다.
코드는 있는데 실행되지 않고, 실행되지 않는다는 사실이 어디에도 안 뜬다.

### 조치 — 새 기전을 만들지 않는다

`system._dashboard_call(_stage1)`로 바꿨다. 304차 후속(0708 access violation
크래시 루프)이 만들고 490차 F-L(0824 GIL 데드락)이 helper로 감싼 **그 통로를
그대로 재사용**한다. `_stage1`이 메인 스레드에서 돌기 시작하면 그 안의
`singleShot(10, _stage2)`는 정상 동작하므로 **체인 시작 한 줄만** 바뀐다
(단계 사이 10ms 양보 구조도 그대로 — 14.8초 블로킹 회피 취지 보존).

### 라이브 검증 — 같은 로그 파일 안에서 before/after 대조

```
00:42:25  _apply 시작            (그 뒤 없음)   ← 수정 전
01:25:43  _apply 시작            (그 뒤 없음)   ← 수정 전
01:35:39  _apply 시작
01:35:39  _apply update_learning   0ms          ← 수정 후, 처음 찍힘
01:35:39  _apply update_efficacy   0ms
01:35:40  _apply update_trend     32ms
01:35:40  _apply pnl_history      47ms 총422ms
```

오류 0건(`pnl_history_refresh`·Traceback·CRITICAL 없음), 총 422ms로 메인 스레드
블로킹 없음, 하트비트 정상(`beat_age_sec=0.4`, `strikes=0`).

### 회귀 고정

`tests/test_504_startup_panel_restore_thread.py` 5건 — 워커 스레드에서 시작해도
4단계 전부 실행 / 순서 유지 / **GUI 갱신이 메인 스레드에서 일어남**(304차·490차
사고 유형) / 체인 시작이 다시 워커 타이머로 돌아가지 않음(AST 성격의 소스 검사) /
**"워커 타이머는 발화하지 않는다"는 전제 자체**도 고정 — PyQt 동작이 바뀌면 그
테스트가 깨져 이 항목이 낡았음을 알린다.

⚠ **`logger.debug`로 예외를 삼키는 구조는 이번에 건드리지 않았다.** 그 자체가
같은 사고를 또 숨길 수 있으므로 별도 안건으로 남긴다(`_stage1~4`·
`restore_panels_from_history` 4곳).

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · 마지막 갱신 2026-08-30 23:10

최근 헤딩 8개:
```
### 커밋 대기 (오늘 커밋하지 않았다)
### MW0601 494차 정정 (2026-08-26 14:55)
### MW0601 494차 후속 (2026-08-26 15:10) — F-1′ 적용 완료
### MW0601 494차 후속2 (2026-08-26 15:30) — 커밋으로는 동기화가 안 된다 (실측 확정)
### MW0601 494차 후속3 (2026-08-26 16:40 — 장후 점검)
### 498차 — 장후 자동조치 (MW0601, 2026-08-26 17:30~19:0x · `mireuk-postmarket-autofix` 첫 실행)
### MW0601 499차 (2026-08-27 08:57~09:1x — 장전 점검)
### MW0601 500차 (2026-08-30 — CVD·OFI 유효성 조사 · 5단계 집행)
```

미완료 체크박스 **2119건** (끝에서 30건)
```
- [ ] **O-p1 (장중)** 개장 첫 분 하한 경보 실효성 — 재발 여부 + 자동진입 발생 여부 +
- [ ] **O-p2 (장중)** 11:50~13:00 `[차단] OTHER 구간` 중 진입 발생 여부 →
- [ ] **O-p3 (장중→장후)** `[HealthPolicy]` 핫리로드 **성공** 1건.
- [ ] **O-p4 (장후)** `Canary` vs `CanaryShadow` z경고 분모 일치 여부(3 vs 5).
- [ ] **O-p5 (장후)** 개장 버스트 메인 정지 추이 — 오늘 09:00:08 **9,500ms**
- [ ] **O-p6 (장후)** `[NetRecon]` 대사 결과. **`MISMATCH` 면 요율 축을 1순위로 의심**
- [ ] 🔴 **어제분 커밋이 아직 안 됐다** — 0826 리포트/증거/dev_memory 2종 +
- [ ] 🔴 **MW0602 에 `mireuk_skill_sync_20260826/` 두 파일 전달** (어제 이월, 미이행).
- [ ] 🔴 **자동조치 예약 프롬프트에 관측 번호 일련 규약 1줄 추가**
- [ ] 🔴 **CB② 복원 재검토 기한 2026-08-29** — 내일이 **기한 전 마지막 회차**.
- [ ] **비용 모델 이원화 종료** — 라이브 `9.8104e-05`(채널 파생) vs
- [ ] **F-2 (신규 상정)** 런처 채널 고정 — 위 Fix F-2 참조.
- [ ] **D-1 TrendGate 하드브레이크** `_CVD_SLOPE_HARD_BREAK_DN/-UP` (-300/+200) vs
- [ ] **D-2 `int(cvd_direction)` 절단** `trend_persistence.py:132` · `main.py:9432`
- [ ] **D-3 앙상블 숏서킷 LONG 편향** `ensemble_decision.py:896`
- [ ] **D-4 Guard-F1 키** `main.py:6365` → `CORE_FEATURES_BY_GROUP`에서 읽기
- [ ] 회귀 테스트 — **③ 임계-범위 묶음을 fix보다 먼저** 넣을 것
- [ ] CVD `n<3` → 0.0 대신 미측정 표기 (`cvd.py:85-94`)
- [ ] VPIN 버킷<10 → 0.0 대신 미측정 표기 (실측 zero 6.3%)
- [ ] **결정 1** `CVD_DEBIAS_MODE` 섀도 신설(기본 off) — delta 당일 러닝 중심화 +
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
식으로만 바꾸면 안 된다 — `cvd_slope`가 음수 0건이라
      `up_hbreak`는 여전히 도달 불가다.
- [ ] **D-2 `int(cvd_direction)` 절단** `trend_persistence.py:132` · `main.py:9432`
- [ ] **D-3 앙상블 숏서킷 LONG 편향** `ensemble_decision.py:896`
- [ ] **D-4 Guard-F1 키** `main.py:6365` → `CORE_FEATURES_BY_GROUP`에서 읽기
- [ ] 회귀 테스트 — **③ 임계-범위 묶음을 fix보다 먼저** 넣을 것

**2단계 — 워밍업 폴백 가시화 (P1, 계측 4원칙 ②·④)**
- [ ] CVD `n<3` → 0.0 대신 미측정 표기 (`cvd.py:85-94`)
- [ ] VPIN 버킷<10 → 0.0 대신 미측정 표기 (실측 zero 6.3%)

**3단계 — 주간회의 결정 집행**
- [ ] **결정 1** `CVD_DEBIAS_MODE` 섀도 신설(기본 off) — delta 당일 러닝 중심화 +
      slope 분모를 롤링 스케일로. ⚠ 정규화만으로는 편향이 안 없어진다(98.6% 양수 유지)
- [ ] **결정 2** CORE 정의 3곳 통합 → `CORE_FEATURES_BY_GROUP` 단일 출처.
      PSI CORE `cvd_divergence` → `cvd_delta_norm` (기준선 재생성 동반)
- [ ] **결정 3** 97 슈퍼셋 — 컬럼 **삭제 금지**(shape mismatch). 폐기 예정 등록 +
      신규 유입 차단까지만. 실제 제거는 P2-B 온보딩 경로

**4단계 — 재검증 SOP 보강**
- [ ] SOP §3에 **구성적 중복**(`f = g(h)` 소스 검사) 신설 — 상관 재기 전에 잡는다
- [ ] SOP §2 D형 스크린을 **CORE 우선** 적용 규약

**그 다음**
- [ ] 26주 WFA L1→L2→L3 재실행 — 🔴 **위 4단계 전에는 금지**.
      L1 사전필터(커버리지·고유값>=20·첫관측)가 병든 6개 중 4개를 통과시킨다.

**섀도 관찰 등록 (조치 아님)**
- [ ] `vpin` 14일 max **0.3822** — 설계 임계 0.5/0.7/0.9 대비 `signal_level` 영구 LOW.
      게다가 `_complete_bucket`의 `signal_level`/`alert`를 아무도 소비하지 않는다(죽은 코드).
      `vpin`은 97셋 밖이라 우선순위 하 — 26주 주기로 이월.

**[2026-08-30 dev 501차 체리픽 후속] 미해결 — 사용자 확인 필요**
- [ ] **2026-05-11·05-12 net 이상치 원인 확인** — `commission_rate_recon.py
      --backfill --force` 정정 후 두 날 모두 gross(pnl_krw)=0인데
      broker_net_krw가 각각 −19,292,312 / −2,711,546원. 수수료로는 불가능한
      규모라 실제 입출금(원인 후보 (b), 가이드 문서 참조)이 섞였을 가능성이
      높다. 계좌 입출금 내역과 대조해 확정할 것 — 확정 전까지 이 두 날짜의
      net을 전환기준 ①·기타 성과 지표 집계에 그대로 쓰지 말 것.
      근거: `dev_memory/DECISION_LOG.md` 2026-08-30.
- [ ] **D2 체인 불연속 19건 잔여 재확인** — `broker_net_chain_audit.py` D2
      절이 지목한 19건 중 08-05→08-06(차 −439,302,126)은 규모상 명백한
      실제 입출금으로 보이나, 나머지는 D1 오염일과 겹쳐 정정 후 자동 해소
      됐는지 재확인 필요(다음 실행 시 잔여 건수만 보면 됨).

**[2026-08-30 dev 502차 후속 체리픽] [57] trend_efficiency 게이트 — 표본 적립 대기**
- [ ] **판정창 2026-09-01~ 진입 후 주간 확인** — `trend_efficiency_gate_shadow`에
      실제 진입 분봉이 쌓이기 시작하면 `min_samples=20`(스킵 코호트) 도달 시점을
      추적. 임계 0.32는 MW0602 자기 데이터 기준이므로 **v9-dev 판정에 그대로 쓰지
      말 것** — v9-dev 자체 표본이 충분히 쌓이면(권장: 최소 100+ 진입) 501차
      후속2와 같은 절차(LODO·시간분할·부트스트랩)로 독립 재검증할 것.
- [ ] **[18] regime_exhaustion_watch와 이중계상 확인** — MW0602 실측에서 두 채널이
      같은 손실 구간(te<0.32)의 상당 부분을 중복 포착했다. v9-dev에서도 두 채널이
      쌓이면 같은 대조를 해볼 것(승격 논의 시 병기 필수).
      근거: `dev_memory/DECISION_LOG.md` 2026-08-30.

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

### `data/heartbeat_MW0601_20260831.json` — 244B · 08-31 09:00:06
```json
{
 "pid": 24976,
 "written_at": "2026-08-31T09:00:36",
 "beat_epoch": 1788134435.806318,
 "beat_age_sec": 1.0,
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

### `docs/정기점검/매일점검` — 82개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260831-8월손실일-딥다이브.md` | 22.2KB | 08-31 00:18 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 13.2KB | 08-31 00:05 |
| `docs/정기점검/매일점검/MW0601-20260827-점검리포트.md` | 90.4KB | 08-27 12:43 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_intra.md` | 66.2KB | 08-27 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260827_pre.md` | 52.6KB | 08-27 09:00 |
| `docs/정기점검/매일점검/MW0601-20260826-점검리포트.md` | 225.1KB | 08-26 19:04 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_post.md` | 75.3KB | 08-26 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_intra.md` | 64.8KB | 08-26 12:27 |

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

1. `logs/20260831_WARN.log`: ERROR 이상 1건
2. `logs/20260831_WARN.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
3. 메인 스레드 정지 5초 초과 **1건** (최대 7718ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20260831_LEARNING.log`: **축퇴** 8건(표본)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260831*.log` (Windows) / `grep 강제청산 logs/*20260831*.log`*