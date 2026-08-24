# 미륵이 증거 다이제스트 — 2026-08-21 / INTRA

- 생성 2026-08-21 12:27:02 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/friendly-magical-keller/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260821` · `2026-08-21` · `260821` · `0821`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **16개** 파일 · 16개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260821.log` | 125B | 08-21 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260821.json` | 243B | 08-21 12:26 |
| `launcher_{DATE}_084001_29653.log` | 1 | `logs/Mireuk_batch/launcher_20260821_084001_29653.log` | 833.9KB | 08-21 12:26 |
| `retrain_intraday_{DATE}_093759.log` | 1 | `logs/retrain_intraday_20260821_093759.log` | 2.4KB | 08-21 09:38 |
| `retrain_intraday_{DATE}_113102.log` | 1 | `logs/retrain_intraday_20260821_113102.log` | 2.4KB | 08-21 11:31 |
| `{DATE}_DATA.log` | 1 | `logs/20260821_DATA.log` | 182.0KB | 08-21 12:27 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260821_DEBUG.log` | 133.2KB | 08-21 12:27 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260821_HEALTH.log` | 2.3KB | 08-21 12:13 |
| `{DATE}_HOGA.log` | 1 | `logs/20260821_HOGA.log` | 31.5MB | 08-21 12:27 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260821_LEARNING.log` | 179.5KB | 08-21 12:27 |
| `{DATE}_MICRO.log` | 1 | `logs/20260821_MICRO.log` | 626.5KB | 08-21 12:27 |
| `{DATE}_PROBE.log` | 1 | `logs/20260821_PROBE.log` | 57.5KB | 08-21 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260821_SIGNAL.log` | 285.7KB | 08-21 12:27 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260821_SYSTEM.log` | 461.3KB | 08-21 12:27 |
| `{DATE}_TRADE.log` | 1 | `logs/20260821_TRADE.log` | 412B | 08-21 09:53 |
| `{DATE}_WARN.log` | 1 | `logs/20260821_WARN.log` | 9.8KB | 08-21 12:22 |

## 2. 코드·커밋 상태

- HEAD `0be0eaa` · 브랜치 `v9-dev` · 미커밋 467건
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
… 외 427건
```

**당일(2026-08-21) 커밋**
```
(당일 커밋 없음)
```

**최근 커밋 12건**
```
0be0eaa [MW0601] docs/프롬프트 신설: 점검 체계 이관 지침 + 스킬/템플릿 참고본
d1dd4fb [MW0601] 482차 후속6: 481차 점검 산출물 복원 + 리포트 md 추적 편입
ccfad20 [MW0601] 482차 후속5: DECISION_LOG 테스트 집계 정정 — 613 passed
ab44ecb [MW0601] 482차 후속4: dev_memory 기록 + 457차 테스트 문자열 매칭 정정
74191d6 [MW0601] 482차 후속3: ConfFloorGuard 3상태 — G-3의 전제를 먼저 복구한다
0d48be8 [MW0601] 482차 후속2: 메인 스레드 정지 섀도 계측 — CB5와 FZ-1 사이 무관측 구간
7c1412e [MW0601] 482차 후속: CB③ 가용성 계측 — 판정 가능 시간을 처음 시계열화
44e2652 [MW0602] 477차: 일일점검 스킬 개정 — 리포트 가독성 대원칙 + 하루 한 파일 append 규약
0215f6c [MW0602] 476차: 장전·장후 점검 (G-1 label_scheme 유실 + 등급 A/B 도달불가) + 이월분 정리
38a8312 [MW0601] 482차: 점검 수집기 — 포지션 단위 집계 + 브랜치 스코프 분리
7a59796 [MW0601] 480차 후속4: F-2 가드가 감시 개시를 파일에 남긴다 — 사이드카 자신의 생존 증거
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
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

_본문 미열람(설정): `20260821_HOGA.log` 31.5MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/14개 (중요도순). 제외: `20260821_MICRO.log`, `20260821_DATA.log`, `20260821_PROBE.log`, `launcher_20260821_084001_29653.log`, `20260821_DEBUG.log`, `force_flat_guard_20260821.log`_

### `logs/20260821_TRADE.log` — 412B · 3행 · 최종 09:53:59

- 형식 평문 · 시각 인식 3행 · INFO=3

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:10 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-21 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-21 09:53:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,190,493) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
  …
2026-08-21 08:41:10 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-21 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-21 09:53:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,190,493) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
```

</details>

**채널** — `TRADE`×3

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1, `Sizer`×1

### `logs/20260821_WARN.log` — 9.8KB · 64행 · 최종 12:22:08

- 형식 평문 · 시각 인식 64행 · WARNING=64

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-21 08:41:20 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=NA
2026-08-21 08:41:21 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
2026-08-21 11:33:00 [WARNING] SYSTEM: [HealthPolicy] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2238ms quality=1.00 cache=0s exc10m=0) | cause=S0(1951ms)
2026-08-21 11:43:00 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.259% (임계 ±0.217%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-21 12:05:59 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.311% (임계 ±0.201%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-21 12:12:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=281ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-21 12:22:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7813ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7813 band=WARN since_pipe_s=0.1
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 24 | 08:41:18 | 12:22:08 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 8 | 09:05:59 | 12:05:59 | 5분 누적 수익률 +0.974% (임계 ±0.921%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 8 | 09:29:59 | 12:12:00 | level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |
| `PipePerf` | 8 | 09:39:01 | 11:32:02 | total=2399ms | S0=1971ms S1=28ms S2=9ms S3=0ms S4=146ms S5=148ms S6=88ms S7=6ms S8=2ms |
| `CB⑤` | 8 | 09:39:01 | 11:32:02 | 파이프라인 2399ms 경고 (기준 1000ms) |
| `HealthPolicy` | 4 | 09:40:00 | 11:33:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2399ms quality=1.00 cache=0s exc10m=0) | cause=S0(1971ms) |
| `ConstOut` | 2 | 09:36:59 | 11:29:59 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| `CB③-P4` | 2 | 10:39:59 | 10:39:59 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=13.3%) |

**채널** — `SYSTEM`×56, `HEALTH`×8

**컴포넌트 상위 15** — `LiveDBG`×24, `ScalerRefresh`×8, `Health`×8, `PipePerf`×8, `CB⑤`×8, `HealthPolicy`×4, `ConstOut`×2, `CB③-P4`×2

### `logs/20260821_SYSTEM.log` — 461.3KB · 3372행 · 최종 12:27:00

- 형식 평문 · 시각 인식 3365행 · INFO=3365, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.4MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-08-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18348 | 행감지=30s all_threads=True
2026-08-21 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-21 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-21 08:41:00 [INFO] SYSTEM: 미륵이 초기화
  …
2026-08-21 12:27:00 [INFO] SYSTEM: [BAR-CLOSE][CYBOS] ts=12:26 O=1096.24 H=1097.54 L=1096.12 C=1097.22 V=194
2026-08-21 12:27:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=12:26 vol=194 | live_buy=135 shadow_buy=100 anchor_buy=100 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-08-21 12:27:00 [INFO] SYSTEM: [S6Detail] ensemble=1ms checklist_pre=10ms meta_gate=8ms gates=0ms imp=0ms shap=7ms corr=9ms dash_ui=0ms tail=17ms
2026-08-21 12:27:00 [INFO] SYSTEM: [PipePerf][DBG] total=427ms | S0=2ms S1=77ms S2=7ms S3=0ms S4=72ms S5=206ms S6=53ms S7=7ms S8=3ms
2026-08-21 12:27:09 [INFO] SYSTEM: [TickUI] alive ticks=91454 code=A0569 close=1097.24
```

</details>

**채널** — `SYSTEM`×3365

**컴포넌트 상위 15** — `CybosRT-TICK`×919, `CybosInvestorRaw`×822, `CybosRT-ROLLOVER`×222, `BAR-CLOSE`×222, `CVD-ANCHOR`×222, `TickUI`×221, `S6Detail`×207, `PipePerf`×207, `System`×59, `MicroRegime`×55, `RegimeFingerprint`×38, `OptionChain`×31, `CybosSub`×21, `IntradayRegime`×17, `ConstOut`×10

### `logs/20260821_SIGNAL.log` — 285.7KB · 2599행 · 최종 12:27:00

- 형식 평문 · 시각 인식 2599행 · WARNING=812, INFO=1787

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
  …
2026-08-21 12:27:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-08-21 12:27:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=56.2% grade=X regime=NEUTRAL
2026-08-21 12:27:00 [INFO] SIGNAL: [InstabilityGate] (섀도) 레짐전환 5회/10분 — 활성 시 min_conf +5%p 예상(미적용)
2026-08-21 12:27:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=56.2% grade=X micro=추세장
2026-08-21 12:27:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.562<mc0.620)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 570 | 09:01:00 | 12:06:00 | 1m 'macro_vix' scale=0.0148 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 109 | 09:05:59 | 12:26:01 | 신뢰도 미달 35.0% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 44 | 09:07:59 | 12:23:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerMonitor` | 42 | 09:00:59 | 10:34:00 | ts=09:00 horizon=1m age=2m max_z=+6.33(volume_acceleration) extreme=2 |
| `Model` | 36 | 09:00:59 | 10:24:59 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerRefresh` | 6 | 08:45:18 | 08:45:18 | 1m CORE 'cvd_divergence' raw_std≈0(0.0225) → identity(0,1) 강제 (FLAT 100% 방지) |
| `PCR-Dampen` | 2 | 09:09:59 | 09:14:59 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConstOut` | 2 | 09:35:59 | 11:29:59 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:05:59 | 09:05:59 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×2599

**컴포넌트 상위 15** — `ScalerFloor`×588, `SIGNAL`×414, `MetaGate`×275, `Ensemble`×215, `FQAdj`×205, `ZeroDiag`×187, `Checklist`×120, `ATR-Horizon`×98, `ToxicityGate`×63, `차단`×63, `MicroRegime`×55, `Model`×54, `WeightCollapse`×44, `InstabilityGate`×44, `ScalerMonitor`×42

### `logs/20260821_LEARNING.log` — 179.5KB · 1670행 · 최종 12:27:00

- 형식 평문 · 시각 인식 1670행 · WARNING=143, INFO=1527

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:01 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.529 out_max=0.4002 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2754 < conf_floor=0.3300 (span=0.00060 auc=0.568 out_max=0.2754, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.501 out_max=0.1502 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=100) → 보정 미적용, raw 통과
  …
2026-08-21 12:27:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=35.9% 예측=FL 실제=UP)
2026-08-21 12:27:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=35.3% 예측=DN 실제=FL)
2026-08-21 12:27:00 [INFO] LEARNING: ✓ 30m 예측 적중 (conf=51.3% DN)
2026-08-21 12:27:00 [INFO] LEARNING: [Bias⚠] 5m 적중=41%(9/22) UP=2 DN=5 FL=15 [FL편향⚠ 68%]
2026-08-21 12:27:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=20.0%
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 143 | 08:41:02 | 11:33:59 | 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |

**채널** — `LEARNING`×1670

**컴포넌트 상위 15** — `LEARNING`×664, `Calibration`×277, `SGD`×207, `sigma`×194, `Bias⚠`×124, `Bias`×66, `MetaConf`×41, `OnlineLearner`×39, `ScalerWarmup`×23, `BiasReset`×11, `SHAP`×7, `GBM-64`×4, `GBM`×4, `RF`×3, `ExtremityCorrector`×2

### `logs/20260821_HEALTH.log` — 2.3KB · 17행 · 최종 12:13:00

- 형식 평문 · 시각 인식 17행 · WARNING=8, INFO=9

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 09:29:59 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 266ms (표본 20분)
2026-08-21 09:29:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-21 09:30:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=297ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-21 09:39:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2399ms | quality=1.00 | cache_age=173s | exceptions_10m=0
2026-08-21 09:40:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=524ms | quality=1.00 | cache_age=48s | exceptions_10m=0
  …
2026-08-21 11:17:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=296ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-21 11:32:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2238ms | quality=1.00 | cache_age=167s | exceptions_10m=0
2026-08-21 11:33:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=511ms | quality=1.00 | cache_age=42s | exceptions_10m=0
2026-08-21 12:12:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=281ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-21 12:13:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=333ms | quality=1.00 | cache_age=58s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 8 | 09:29:59 | 12:12:00 | level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |

**채널** — `HEALTH`×17

**컴포넌트 상위 15** — `Health`×16, `HealthTrend`×1

### `logs/retrain_intraday_20260821_093759.log` — 2.4KB · 20행 · 최종 09:38:21

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 09:37:59,763 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-21 09:37:59,763 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-21 09:37:59,764 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-21 09:37:59,764 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_46e1a75e.json
2026-08-21 09:38:02,702 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-21 09:38:21,279 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.88s | old_acc=0.4048)
2026-08-21 09:38:21,360 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-21 09:38:21,360 [INFO] LEARNING: [Retrain] 완료 | 18.7초 | 성공=1/1 호라이즌
2026-08-21 09:38:21,361 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.6s 데이터=4800행
2026-08-21 09:38:21,363 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_46e1a75e.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/retrain_intraday_20260821_113102.log` — 2.4KB · 20행 · 최종 11:31:25

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 11:31:02,344 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-21 11:31:02,345 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-21 11:31:02,345 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-21 11:31:02,345 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['5m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_0e39263a.json
2026-08-21 11:31:05,894 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-21 11:31:25,569 [INFO] LEARNING: [Retrain] 5m 교체 (intraday — CV 없음 | fit=0.89s | old_acc=0.4284)
2026-08-21 11:31:25,650 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-21 11:31:25,650 [INFO] LEARNING: [Retrain] 완료 | 19.8초 | 성공=1/1 호라이즌
2026-08-21 11:31:25,651 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 23.3s 데이터=4800행
2026-08-21 11:31:25,653 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_0e39263a.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| 체결(`[체결진입]`) | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 63 |
| 사이저 호출(`[Sizer]`) | 1 |

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×1

### 차단 사유 63건 · 22종

| 건수 | 사유 |
|---|---|
| 34 | 등급X — 미통과 항목: 2_confidence |
| 5 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 3 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.1pt > ATR×5.0=13.9pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.3pt > ATR×5.0=12.3pt (시가=1068.40 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.8pt > ATR×5.0=13.3pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.0pt > ATR×5.0=14.2pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.3pt > ATR×5.0=14.8pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.4pt > ATR×5.0=14.7pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.2pt > ATR×5.0=14.4pt (시가=1068.40 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 11_countertrend |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.2pt > ATR×5.0=14.2pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.2pt > ATR×5.0=14.0pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.5pt > ATR×5.0=14.0pt (시가=1068.40 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×34, `3_vwap`×18, `6_foreign`×18, `5_ofi`×11, `4_cvd`×10, `7_prev_bar`×9, `11_countertrend`×3, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### 메인 스레드 블로킹 20건 · 최대 9922ms · 5초 초과 8건

상위 — 9922ms, 7813ms, 7515ms, 7500ms, 7296ms, 6890ms, 5797ms, 5281ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:01:08 | 9922ms | 953ms | **8969ms (90%)** |
| 10:19:06 | 7296ms | 1339ms | **5957ms (82%)** |
| 10:24:05 | 6890ms | 335ms | **6555ms (95%)** |
| 10:34:06 | 7500ms | 481ms | **7019ms (94%)** |
| 10:39:06 | 7515ms | 410ms | **7105ms (95%)** |
| 10:44:04 | 5281ms | 329ms | **4952ms (94%)** |
| 10:49:04 | 5797ms | 251ms | **5546ms (96%)** |
| 12:22:08 | 7813ms | 390ms | **7423ms (95%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260821_WARN.log`
```
--- ConstOut ×2(표본)
09:36:59 2026-08-21 09:36:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:29:59 2026-08-21 11:29:59 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
--- 메인 스레드 블로킹 ×8(표본)
08:41:20 2026-08-21 08:41:20 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=NA
09:01:08 2026-08-21 09:01:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 9922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9922 band=WARN since_pipe_s=0.2
09:06:03 2026-08-21 09:06:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4484ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4484 band=INFO since_pipe_s=0.1
09:36:03 2026-08-21 09:36:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4547ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4547 band=INFO since_pipe_s=0.0
```

### `logs/20260821_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:59 2026-08-21 09:36:59 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:39:00 (const_output)
09:36:59 2026-08-21 09:36:59 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:59 2026-08-21 09:36:59 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=98ms fit=43ms total=145ms
09:37:59 2026-08-21 09:37:59 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:00:59 2026-08-21 09:00:59 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.020 level=0 (heartbeat)
09:05:59 2026-08-21 09:05:59 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.020 level=0 (heartbeat)
09:10:59 2026-08-21 09:10:59 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.020 level=0 (heartbeat)
09:15:59 2026-08-21 09:15:59 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.020 level=0 (heartbeat)
```

### `logs/20260821_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:05:59 2026-08-21 09:05:59 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×6(표본)
09:35:59 2026-08-21 09:35:59 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:59 2026-08-21 09:35:59 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:59 2026-08-21 09:36:59 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:59 2026-08-21 09:37:59 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:59 2026-08-21 09:07:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:59 2026-08-21 09:10:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:59 2026-08-21 09:10:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:59 2026-08-21 09:13:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
08:40:43 2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
--- 안전망 ×8(표본)
09:07:59 2026-08-21 09:07:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:59 2026-08-21 09:10:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:10:59 2026-08-21 09:10:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:13:59 2026-08-21 09:13:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20260821_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.529 out_max=0.4002 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2754 < conf_floor=0.3300 (span=0.00060 auc=0.568 out_max=0.2754, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:02 2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.501 out_max=0.1502 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=100) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260821_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:10 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:41 ~ 09:53

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260821_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 5 | 08:41:18 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:01:08 [WARNING] _tick_header 간격 9922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9922 band=… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 3 | 09:01:08 [WARNING] _tick_header 간격 9922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9922 band=… |
| 10:00 | 장중 초반 | 1 | 09:55:59 [WARNING] 5분 누적 수익률 -0.682% (임계 ±0.454%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1 | 12:05:59 [WARNING] 5분 누적 수익률 -0.311% (임계 ±0.201%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |

- 이 로그 생존구간: 08:41 ~ 12:22

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260821_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:46 [INFO] 로테이션 — 8.4MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 200 | 08:54:01 [INFO] #2000 code=A0569 raw_time=85402 parsed=08:54:02 price=1064.06 vol=2 bid1=1063.80 ask1=1064.04 flag=49 side=BU… |
| 10:00 | 장중 초반 | 216 | 09:54:00 [INFO] #35100 code=A0569 raw_time=95401 parsed=09:54:01 price=1090.02 vol=1 bid1=1089.90 ask1=1090.12 flag=50 side=S… |
| 12:00 | 장중 중간점 | 168 | 11:54:00 [INFO] ensemble=1ms checklist_pre=9ms meta_gate=6ms gates=0ms imp=0ms shap=4ms corr=8ms dash_ui=0ms tail=13ms |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:27

**매분 루프 커버리지 09:00~15:10: 208/371분 (56.1%)**

연속 3분 이상 기록 없는 구간 1개:

| 시작 | 끝 | 분 |
|---|---|---|
| 12:28 | 15:10 | 163 |

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260821_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 43 | 08:45:18 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0225) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 110 | 09:00:59 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 09:00:59 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 145 | 09:54:59 [WARNING] 신뢰도 미달 35.4% < 38.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 148 | 11:54:00 [WARNING] 신뢰도 미달 40.1% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:27

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| 20260817 | 17:58 | 로그 본문 |
| 20260814 | 15:40 | 로그 본문 |
| **중앙값** | **17:02** | 기준선 |
| **오늘 20260821** | **12:27** | 로그 본문 |

- 델타 **-275분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-08-21 (MW0601 483차 — 장전 점검 · 분석만, 코드 0건)
### [1] 런처 단일 인스턴스 가드가 죽인 프로세스의 정체가 로그에 남지 않는다 (P2, 신규)
### [2] 단기 CORE `cvd_divergence` 스케일러 항등 폴백 6건 — 3일 연속 단조 감소 (P2, 지속·완화)
### [3] NEXT_TODO 주간회의 기한 「2026-08-22 금」이 달력과 불일치 — 08-22는 토요일 (P2, 신규)
### [4] 미커밋 463건 = CRLF 착시 100% (P2, 🔄 지속 3일차 · 리포트 이상점 1-4)
### [5] 이월 처리 결과 (08-20 장후 → 08-21 장전)
### [6] 정상 확인 (이상점 아님 — 재상정 방지)
### [7] 코드 변경 0건 · 라이브 DB 미접근
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
MED pid=19972
   판정예정=15:12 정지임계=180s (알림 전용 — 주문 없음)`.
8. **메인 스레드 블로킹 1건 2,844ms** — `pipe_elapsed=-1 band=INFO`, `CB_PIPE_PAUSE_MS=5_000`의
   **56.9%**. 기동 직후 1회, 파이프라인 미가동 구간이라 CB⑤ 대상 아님.
   ⚠ NEXT_TODO O-10 문언("5,000ms 초과 1건이면 CB⑤ 실발동")은 **전제 오류(단위 불일치)** —
   근거로 쓰지 않았다. 폐기 승인은 주간회의 안건.
9. **`[Calibration]` 268건은 구조적 상수** — 기동창(08:40~08:45) 6거래일 대조
   0814=260(축퇴89/하한불가44) · 0817=282(90/53) · 0818=282(90/53) · 0819=247(90/35) ·
   0820=255(93/37) · **0821=268(93/44)**. 전 항목 밴드 내 → **적신호 아님.**
   보정기 본체 정상: `복원 완료 n=888 fitted=True degenerate=False unreachable=False
   span=0.00630 auc=0.550 out_max=0.3479`.
10. **`[CybosProbe]` 실패 10건 — 종결 사안, 재상정 금지.** DECISION_LOG:27413
    "O-8에서 '매일 같은 패턴이면 정상'으로 종결 확정(0819)" · :27499 "프리장 미제공".
    파일당 `CoInitialize` 실패 건수 0818~0821 전부 **2건**으로 동일.
11. **`[PreRetrain] … session_state 미기록 보완` 은 설계된 폴백** — `main.py:5117~5131`
    `# [Fallback] session_state 미기록 시 마커 파일 직접 확인`. `session_state.json`이
    `_DAILY_RESET_KEYS`로 아침 리셋되므로 EOD가 15:49에 쓴 `p8_last_success_date` ·
    `eod_retrain_ok_date`가 08:45에 없는 것이 **정상**. `main.py:11285` 435차 주석
    ("아침 PreRetrain은 매번 마커 직접 확인으로 정상 동작") + 0814·0818·0819·0820·0821
    **5거래일 동일 문구** 실측. 폴백이 로그를 남기므로 계측 4원칙 ④ 준수.
12. **실시간 구독 사전 시작** — 08:45:18 `[EarlyWarmup] Cybos RT 08:45 선행 구독 시작
    (프리장 봉 15봉 확보)`. 08:59:59 `[BAR-CLOSE][CYBOS] ts=08:59 … C=1065.10 V=146`.
    09:00 첫 봉 미유실.
13. **레짐** — 08:58:21·08:58:51 `[Regime] NEUTRAL (점수=1) | VIX=14.9 (극저공포) |
    SP500=-0.87% (하락) | USD/KRW +0.07% (중립)`. 옵션 체인 5,242 종목 로드.
14. **TR 상수** — `config/constants.py:13 TR_FUTURES_1MIN = "OPT50029"` · `OPT10080` 0건.
    ⚠ 단 이 상수는 **Kiwoom 경로 전용**이고 오늘 브로커는 **Cybos**(실시간 틱 +
    `[BAR-CLOSE][CYBOS]` 자체 집계) — 값은 옳으나 오늘 실행 경로가 아니다.
15. **설정 불변식 21행 전부 `일치`/의도된 `값 확인` · `불일치` 0 · 미기록 차단게이트 0.**
    한시예외 재검토 기한 **경과 0건**(CB② 2026-08-29, 8일 남음).
16. **주간 리포트 결번 없음** — 최신 `validation_campaign_report_20260814.md`(금),
    그 이후 금요일은 오늘이 처음.
17. **미관측 1건** — scipy 1.5.4 / sklearn 1.0.2 / joblib 1.1.1 버전이 **어떤 로그에도
    없다.** 32-bit DLL 충돌 시 즉시 크래시하므로 기동 성공이 간접 증거이나 직접 확인이
    아니다 → O-5로 등록(장후 확인 + 기동 시 1회 로그 남길지 검토).
18. **재인용 금지 수치 미사용** — ① 2026-06-25 SHAP=0 ② 2026-08-01 §9-3 이벤트 단위
    사이징 통계 4종 ③ `mdd_pct_of_peak` ④ 417차 이전 `[Sizer]` 379/86(22.7%) —
    **넷 다 인용하지 않았다.**

### [7] 코드 변경 0건 · 라이브 DB 미접근

개장 3분 전 실행이라 `raw_data.db`·`predictions.db`·`trades.db`에 **어떤 쿼리도 돌리지
않았다**(CLAUDE.md 「장중 라이브 DB 분석 금지」, 2026-08-10 CB⑤ 자가유발 전례).
증거는 로그 파일·설정 파일·git 메타데이터에서만 취득. `git commit`/`git push` 미실행.

```

</details>

### dev_memory/NEXT_TODO.md — 1.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 📄 문서 정정 (근거 오류 — 다음 세션이 오독한다)
### 🔵 기한 — 주간회의(2026-08-22 금) 상정
### 다음 거래일(08-21)~ 관측
### ✅ 완료·종결 처리 (477차 장전·장중 등록분)
### 481차 — 장전 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 481차 후속 — 장중 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 481차 후속2 — 장후 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 483차 — 장전 점검 (MW0601, 2026-08-21 금 · 분석만, 코드 0건)
```

미완료 체크박스 **1740건** (끝에서 30건)
```
- [ ] **O-1 (장후) 수집기 §5 포지션 단위 재현** — F-4 미적용이면 3자 차이 재기록.
- [ ] **O-2 (장중) `_tick_header` 5초 초과 건수와 `pipe_elapsed`** —
- [ ] **O-3 (장후) 3m 라이브 적중률·ConstOut 집중도** — 오늘 3m 0.2828(전 호라이즌 최저),
- [ ] **O-4 `ZONE_ENTRY_BAN_SHADOW_ENABLED` 실효 확인** — 채널 `[53]` 표본 적립 주체를
- [ ] **O-5 (장후) `[GuardGhost] 3m` 재발 여부** — 오늘 1회(457차 F7 ⑤안으로 정상 처리).
- [ ] **O-6 등급 인플레 4일차** — R-후보 아님(위 반증). 일자단위 누적만.
- [ ] **O-7 (장후) 15:10 강제청산 실집행** — 누적 **0회**. 진입이 15:05 이후까지 열린 날이
- [ ] **O-8 로컬 커밋 push** — `origin/v9-dev` 대비 **ahead 8**(어제 7 → 오늘 8).
- [ ] **O-9 (장전) 미커밋 건수 표기** — 수집기 CRLF 착시(`461건`). F-5 적용 전까지
- [ ] **P2-A (신규) 런처 단일 인스턴스 가드 진단 출력을 로그 파일로 영속화** —
- [ ] **P2-B (기등록 F-5 승계) 수집기 CRLF 내성** — `미커밋 463건` 중 **463건 전부 착시**
- [ ] **P2-C (신규) NEXT_TODO 주간회의 기한 요일 정정** — 14642·14778·14895·15013행
- [ ] **G-1(483) 아침 CORE 스케일러 폴백을 "어느 피처가 며칠째"로 시계열화** —
- [ ] **G-2(483) 런처 가드 이벤트를 하트비트 JSON에 편입** —
- [ ] **G-3(483) 장전 점검이 "오늘 금요일"을 스스로 인지** —
- [ ] **`ZONE_ENTRY_BAN_SHADOW_ENABLED` 양 PC 배선** — `v9-dev`에 상수 자체가 없다.
- [ ] **전환기준 ⑥에 "CB③ ready 시간 ≥ 장중 50%"를 판정 전제로 추가** 검토 —
- [ ] **NEXT_TODO O-10 문언 폐기 승인** — "5,000ms 초과 1건이라도 나오면 CB⑤ 실발동"은
- [ ] **계측 4원칙 ① 적용범위(기등록 유지)**.
- [ ] **(신규) CB② 재검토 기한 표기** — `2026-08-29`는 **토요일**이다. 실무 판정 가능일은
- [ ] **O-1 (장후) 수집기 §5 포지션 단위 집계 실효 검증** — F-4(`38a8312`) 배포 후 첫 거래일.
- [ ] **O-2 (장중) `_tick_header` 5초 초과 건수와 `pipe_elapsed`** — `pipe_elapsed≠0`인
- [ ] **O-3 (장후) CORE 스케일러 폴백 4일차** — 08:45 창 6건(cvd_divergence 단독)이
- [ ] **O-4 (장후) 3m 라이브 적중률·`ConstOut` 집중도** — 전일 3m 0.2828(전 호라이즌 최저),
- [ ] **O-5 (장후) scipy 1.5.4 / sklearn 1.0.2 / joblib 1.1.1 버전 직접 확인** —
- [ ] **O-6 (다음 거래일) 런처 가드 대상 프로세스 정체** — P2-A 적용 후 2거래일 관측 →
- [ ] **O-7 (장후) 15:10 강제청산 실집행** — 누적 **0회**. 진입이 15:05 이후까지 열린 날이
- [ ] **O-8 (장후) 오늘(금) 검증 캠페인 주간 리포트 생성** —
- [ ] **O-9 (내일 장전) 미커밋 CRLF 착시 4일차** — F-5/P2-B 적용 전까지
- [ ] **O-10 (장후) 등급 인플레 5일차 — 일자단위 누적만.** 481차 후속 [5]에서
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
맡긴 것이 P2-C의 구조적 원인이다.

#### 🔵 기한 — 주간회의(**2026-08-21 금 = 오늘**) 상정

> ⚠ 아래 4건은 481차가 `2026-08-22 금`으로 적었으나 **08-22는 토요일**이다(P2-C).
> **실제 회의일은 오늘 08-21이다.** 오늘 넘기면 08-28로 밀린다.

- [ ] **`ZONE_ENTRY_BAN_SHADOW_ENABLED` 양 PC 배선** — `v9-dev`에 상수 자체가 없다.
      캠페인 채널 `[53]`이 MW0602 단독 적립일 가능성.
      **오늘 생성될 `금요일점검/MW0601/…_20260821.md` × `MW0602/…` 대조로 확인.**
- [ ] **전환기준 ⑥에 "CB③ ready 시간 ≥ 장중 50%"를 판정 전제로 추가** 검토 —
      482차 후속 `7c1412e`(CB③ 가용성 시계열화) 결과 확인 후.
- [ ] **NEXT_TODO O-10 문언 폐기 승인** — "5,000ms 초과 1건이라도 나오면 CB⑤ 실발동"은
      **전제가 틀렸다**(단위 불일치). 483차도 이 문언을 근거로 쓰지 않았다.
- [ ] **계측 4원칙 ① 적용범위(기등록 유지)**.
- [ ] **(신규) CB② 재검토 기한 표기** — `2026-08-29`는 **토요일**이다. 실무 판정 가능일은
      **08-28(금)**. CLAUDE.md 절대원칙 §2 한시예외 문구에 `(판정은 08-28 금 금요일점검에서)`를
      덧붙일지 결정. **단독 판단 금지 — 절대원칙 문구 수정이다.**

#### 다음 국면(오늘 장중·장후) 관측 항목

- [ ] **O-1 (장후) 수집기 §5 포지션 단위 집계 실효 검증** — F-4(`38a8312`) 배포 후 첫 거래일.
      3원 대사: 로그 `[Position] 진입` = `ensemble_decisions.entry_executed=1` =
      `COUNT(DISTINCT trades.entry_ts)`. **청산 레그가 더 많은 것은 불일치가 아니다.**
- [ ] **O-2 (장중) `_tick_header` 5초 초과 건수와 `pipe_elapsed`** — `pipe_elapsed≠0`인
      5초 초과가 **1건이라도** 나오면 CB⑤ 실발동 가능 → 즉시 추적.
      장전 구간은 1건 2,844ms(`pipe_elapsed=-1`, 임계의 56.9%).
- [ ] **O-3 (장후) CORE 스케일러 폴백 4일차** — 08:45 창 6건(cvd_divergence 단독)이
      유지/감소면 "봉 부족 일시현상". **2피처 이상으로 다시 늘면 483차 [2]를 P1로 격상.**
- [ ] **O-4 (장후) 3m 라이브 적중률·`ConstOut` 집중도** — 전일 3m 0.2828(전 호라이즌 최저),
      `ConstOut` 6/6 전량 3m. **2일 연속 3m 단독 집중이면 R-1 우선순위를 "이번 주"로.**
- [ ] **O-5 (장후) scipy 1.5.4 / sklearn 1.0.2 / joblib 1.1.1 버전 직접 확인** —
      **어떤 로그에도 없다.** 기동 성공은 간접 증거일 뿐. 장후 `py37_32`에서 1회 확인하고,
      **기동 시 1회 로그로 남길지**를 고도화 후보로 등록할 것.
- [ ] **O-6 (다음 거래일) 런처 가드 대상 프로세스 정체** — P2-A 적용 후 2거래일 관측 →
      ①저녁 재기동분 / ②종료 실패 판정.
- [ ] **O-7 (장후) 15:10 강제청산 실집행** — 누적 **0회**. 진입이 15:05 이후까지 열린 날이
      오면 `[ForceExitPass]` → `[TimeExit]` → `[ExitAttempt]` 순서 확인.
      **`[SchedForceExit] … 안전망 발동`(ERROR)이 뜨면 P0.** 전환기준 ② ⓐ.
- [ ] **O-8 (장후) 오늘(금) 검증 캠페인 주간 리포트 생성** —
      `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` +
      `_metrics_20260821.json`. **고정 파일명 덮어쓰기 없음** ·
      FIFO(`VALIDATION_REPORT_KEEP_WEEKS=4`)가 수동 스냅샷 `_20260801_pre405` 를 지우지
      않았는지 · `UNKNOWN/` 폴더 미생성 · stderr 호스트명 경고 없음.
- [ ] **O-9 (내일 장전) 미커밋 CRLF 착시 4일차** — F-5/P2-B 적용 전까지
      `--ignore-cr-at-eol` 실측치로 매 리포트 정정. 오늘 착시율 **100%(463/463)**.
- [ ] **O-10 (장후) 등급 인플레 5일차 — 일자단위 누적만.** 481차 후속 [5]에서
      **R-후보 강등(반증)**. 손익 결론을 다시 내지 않는다. **확정 결론 금지(313차).**

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

### `data/heartbeat_MW0601_20260821.json` — 243B · 08-21 12:26:57
```json
{
 "pid": 18348,
 "written_at": "2026-08-21T12:26:57",
 "beat_epoch": 1787282813.330927,
 "beat_age_sec": 3.8,
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

### `docs/정기점검/매일점검` — 62개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260821-점검리포트.md` | 49.9KB | 08-21 09:14 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_pre.md` | 46.8KB | 08-21 08:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_pre.md` | 49.0KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_post.md` | 70.5KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_intra.md` | 61.3KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_pre.md` | 46.2KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_post.md` | 63.9KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_intra.md` | 59.8KB | 08-20 22:24 |

### `docs/정기점검/금요일점검` — 54개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.json` | 7.6KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.md` | 3.8KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20260821_SYSTEM.log`: 매분 루프 커버리지 208/371분 (56.1%) — 루프가 빠진 구간이 있다
2. `logs/20260821_SYSTEM.log`: 12:28~15:10 **연속 163분 매분 루프 기록 없음**
3. 메인 스레드 정지 5초 초과 **8건** (최대 9922ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
4. `logs/20260821_WARN.log`: **ConstOut** 2건(표본)
5. `logs/20260821_SYSTEM.log`: **ConstOut** 8건(표본)
6. `logs/20260821_SIGNAL.log`: **WeightCollapse** 8건(표본)
7. `logs/20260821_SIGNAL.log`: **ConstOut** 6건(표본)
8. `logs/20260821_LEARNING.log`: **축퇴** 8건(표본)
9. 미커밋 변경 467건

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260821*.log` (Windows) / `grep 강제청산 logs/*20260821*.log`*