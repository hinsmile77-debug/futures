# 미륵이 증거 다이제스트 — 2026-08-21 / POST

- 생성 2026-08-21 16:22:48 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/nifty-funny-davinci/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260821` · `2026-08-21` · `260821` · `0821`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **22개** 파일 · 22개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260821.txt` | 28B | 08-21 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260821.txt` | 181B | 08-21 15:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260821.log` | 445B | 08-21 15:12 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260821.json` | 244B | 08-21 15:40 |
| `launcher_{DATE}_084001_29653.log` | 1 | `logs/Mireuk_batch/launcher_20260821_084001_29653.log` | 1.5MB | 08-21 15:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260821.log` | 34.8KB | 08-21 16:05 |
| `retrain_intraday_{DATE}_093759.log` | 1 | `logs/retrain_intraday_20260821_093759.log` | 2.4KB | 08-21 09:38 |
| `retrain_intraday_{DATE}_113102.log` | 1 | `logs/retrain_intraday_20260821_113102.log` | 2.4KB | 08-21 11:31 |
| `retrain_intraday_{DATE}_130500.log` | 1 | `logs/retrain_intraday_20260821_130500.log` | 2.4KB | 08-21 13:05 |
| `retrain_intraday_{DATE}_145800.log` | 1 | `logs/retrain_intraday_20260821_145800.log` | 2.4KB | 08-21 14:58 |
| `strategy_report_{DATE}_154026.txt` | 1 | `data/daily_reports/strategy_report_20260821_154026.txt` | 2.1KB | 08-21 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260821_DATA.log` | 343.2KB | 08-21 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260821_DEBUG.log` | 238.5KB | 08-21 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260821_HEALTH.log` | 3.8KB | 08-21 15:00 |
| `{DATE}_HOGA.log` | 1 | `logs/20260821_HOGA.log` | 52.4MB | 08-21 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260821_LEARNING.log` | 293.0KB | 08-21 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260821_MICRO.log` | 1.0MB | 08-21 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260821_PROBE.log` | 96.6KB | 08-21 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260821_SIGNAL.log` | 485.2KB | 08-21 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260821_SYSTEM.log` | 834.6KB | 08-21 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260821_TRADE.log` | 10.0KB | 08-21 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260821_WARN.log` | 64.9KB | 08-21 15:40 |

## 2. 코드·커밋 상태

- HEAD `0be0eaa` · 브랜치 `v9-dev` · 미커밋 474건
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
… 외 434건
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

_본문 미열람(설정): `20260821_HOGA.log` 52.4MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260821.txt`** — 28B · 08-21 15:40:26
```
2026-08-21T15:40:26.843643
```

**`data/daily_reports/strategy_report_20260821_154026.txt`** — 2.1KB · 08-21 15:40:26
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-08-21 15:40
========================================================
  버전    : v1.0  (65일차)
  판정    : OUTPERFORM
  Live(20일): Sh=2.63  MDD(자본대비)=2.2%
  당일      : WR=50.0%  PF=0.19
  롤링20일: 누적 +1285511원  Sh=2.63  MDD(자본대비)=2.2%  MDD(peak대비)=60.0%
  당일손익 : broker(gross) -170,000원  수수료 9,884원  net -179,884원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.044 (CLEAR)
  PSI/feat: cvd=0.120  vwap_position=0.044  ofi=0.005
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 -30,163원  승률 45.0%  합계 -603,255원
  등급별 순EV(30일): A=+3,570원(143건,승62%)  C=-16,818원(39건,승64%)
  호라이즌별 순EV(30일): 1m=+22,741원(22건)  3m=-6,740원(108건)  5m=-7,604원(48건)  ?=+111,813원(4건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 47분  5일평균 55분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 41.9pt(5일평균 41.6pt)  1분평균변동 1.11pt(5일평균 0.99pt)
--------------------------------------------------------
  진입 퍼널(2026-08-21, 총 369분):
    FLAT 190 → conf미달 115 → CoherenceGate 17 → 게이트차단 43 → 후보 4 → 진입 4
    게이트별: 체크리스트항목미달=28  포지션보유중(평가생략)=5  콜드스타트/기타(σ미수집)=3  콜드스타트/기타(조건부구간)=3  콜드스타트/기타(RegimeOverride)=1  시가갭(OPEN_VOLATILE)=1  쿨다운=1  마감시간(신규진입금지)=1
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260821.txt`** — 181B · 08-21 15:48:31
```
completed: 2026-08-21 15:48:31
rows: 40386
cols: 97
horizons_replaced: 6/6
t_load_s: 40.4
t_retrain_s: 166.5
t_total_s: 207.4
daily_close_seen: true
wait_dc_timeout: false
```

_다이제스트 대상 8/17개 (중요도순). 제외: `retrain_intraday_20260821_130500.log`, `retrain_intraday_20260821_145800.log`, `retrain_intraday_20260821_113102.log`, `20260821_MICRO.log`, `20260821_DATA.log`, `20260821_PROBE.log`, `launcher_20260821_084001_29653.log`, `20260821_DEBUG.log`_

### `logs/20260821_TRADE.log` — 10.0KB · 80행 · 최종 15:40:24

- 형식 평문 · 시각 인식 80행 · INFO=80

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:10 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-21 08:41:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-21 09:53:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,190,493) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
2026-08-21 13:10:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,190,493) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-21 13:10:00 [INFO] TRADE: [진입체크] LONG→LONG 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd❌ ofi✅ fore✅ prev❌ time✅ risk✅ chas✅ coun✅ | conf=38.7%
  …
2026-08-21 14:26:51 [INFO] TRADE: [Chejan] 상태=접수 주문번호=4644 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-21 14:26:51 [INFO] TRADE: [Chejan] 상태=체결 주문번호=4644 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-21 14:26:51 [INFO] TRADE: [Position] 체결청산 LONG @ 1103.16 | PnL=+0.34pt (+15,346원) | 하드스톱(틱)
2026-08-21 14:26:51 [INFO] TRADE: [청산 완료] PnL=+0.34pt (+15,346원)
2026-08-21 15:40:24 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×80

**컴포넌트 상위 15** — `Chejan`×22, `Position`×18, `주문요청`×10, `Sizer`×5, `진입체크`×4, `체결진입`×4, `TickStop-S0C`×4, `청산 완료`×4, `TickTP1`×3, `ProfitGuard`×2, `체결진입보정`×2, `손절1차 조기축소`×2

### `logs/20260821_WARN.log` — 64.9KB · 299행 · 최종 15:40:26

- 형식 평문 · 시각 인식 299행 · WARNING=299

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-21 08:41:18 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-21 08:41:20 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=NA
2026-08-21 08:41:21 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
2026-08-21 15:26:14 [WARNING] SYSTEM: [LiveDBG] DynMCPanel.refresh slow 328ms
2026-08-21 15:40:22 [WARNING] SYSTEM: [ThresholdRecal] 경보 발생: {'1m': 'UPDATE', '3m': 'UPDATE', '5m': 'UPDATE', '10m': 'UPDATE', '15m': 'UPDATE', '30m': 'UPDATE'}  docs/정기점검/LABEL_THRESHOLD_RECALIBRATION_GUIDE.md 참조
2026-08-21 15:40:22 [WARNING] SYSTEM: [ATRCeilingRecal] UPDATE — floor 3.5→2.5pt (-29%), ceiling 6.0→4.0pt (-33%) — Slack 알림 발송, 수동 검토 필요
2026-08-21 15:40:23 [WARNING] SYSTEM: [EntryHorizonRecal] UPDATE — 경계 3.2/4.4 → 재계산 5.721/8.574 (δ+79%/+95%), 버킷비중(1m/3m/5m)=2%/12%/86% — 수동 검토 필요
2026-08-21 15:40:26 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 55분/일 < 하한 60분 — 금일 47분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
```

</details>

**WARNING — 태그 33종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 90 | 08:41:18 | 15:26:14 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 22 | 13:10:04 | 14:26:51 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='3826' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=13:10:00.433' | positio… |
| `ChejanMatch` | 22 | 13:10:04 | 14:26:51 | order_no='3826' | pending='ENTRY:LONG qty=2 filled=0 order_no=3826 reason=진입 req_at=13:10:00.433' | pending_matched=True |
| `PendingOrder` | 20 | 13:10:00 | 14:26:51 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1096.9, 'reason': '진입', 'hint_source': '', 'atr': 1.7, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty': 0… |
| `ScalerRefresh` | 15 | 09:05:59 | 15:09:00 | 5분 누적 수익률 +0.974% (임계 ±0.921%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 14 | 09:29:59 | 14:59:02 | level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |
| `PipePerf` | 12 | 09:39:01 | 14:59:02 | total=2399ms | S0=1971ms S1=28ms S2=9ms S3=0ms S4=146ms S5=148ms S6=88ms S7=6ms S8=2ms |
| `CB⑤` | 12 | 09:39:01 | 14:59:02 | 파이프라인 2399ms 경고 (기준 1000ms) |
| `ExitCooldown` | 8 | 13:15:47 | 14:26:51 | 하드스톱(틱) 후 2분 재진입 금지 (until 13:17:47) |
| `HealthPolicy` | 6 | 09:40:00 | 15:00:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2399ms quality=1.00 cache=0s exc10m=0) | cause=S0(1971ms) |
| `SHAP` | 6 | 12:49:01 | 14:42:01 | 슬로우 감지 910ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `EntryFillFlow` | 6 | 13:10:04 | 14:13:01 | actual_side='LONG' | after='LONG 2계약 @ 1096.82' | applied_side='LONG' | before='LONG 2계약 @ 1096.90' | fill_no='' | fill_price=1096.82 | fill_qty=1 | order_no='3826' | pending='ENTRY:LONG qty=2 filled=1 order_no=3826 reason=진입 req_at=13:10:… |

**채널** — `SYSTEM`×285, `HEALTH`×14

**컴포넌트 상위 15** — `LiveDBG`×90, `ChejanFlow`×22, `ChejanMatch`×22, `PendingOrder`×20, `ScalerRefresh`×15, `Health`×14, `PipePerf`×12, `CB⑤`×12, `ExitCooldown`×8, `HealthPolicy`×6, `SHAP`×6, `EntryFillFlow`×6, `ExitSendOrderResult`×6, `ChartDBG`×6, `ConstOut`×4

### `logs/20260821_SYSTEM.log` — 834.6KB · 6044행 · 최종 15:40:41

- 형식 평문 · 시각 인식 6019행 · INFO=6019, PLAIN=25

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 로테이션 — 8.4MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대)
2026-08-21 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18348 | 행감지=30s all_threads=True
2026-08-21 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-21 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-21 08:41:00 [INFO] SYSTEM: 미륵이 초기화
  …
2026-08-21 15:40:26 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-08-21 15:40:26 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-21 15:40:41 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-21 15:40:41 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-21 15:40:41 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×6019

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1365, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×407, `S6Detail`×369, `PipePerf`×369, `MicroRegime`×104, `System`×98, `RegimeFingerprint`×67, `OptionChain`×56, `BalanceUI`×50, `CybosEvent`×44, `BalanceRefresh`×35

### `logs/20260821_SIGNAL.log` — 485.2KB · 4427행 · 최종 15:40:24

- 형식 평문 · 시각 인식 4427행 · WARNING=1341, INFO=3086

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
2026-08-21 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.424
  …
2026-08-21 15:09:00 [INFO] SIGNAL: [ScalerRefresh] ts=15:08 trigger=D_FORCE price_momentum_5m=-0.237% n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.07s
2026-08-21 15:10:12 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-21 15:40:24 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-21 15:40:24 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-21 age=27m extreme=252 refresh=33 grade_x=148 cb3=0
2026-08-21 15:40:24 [INFO] SIGNAL: [ModelHealth] date=2026-08-21 앙상블유효가동률=76.7% | 파이프라인 369분 | ConstOut 4회/7분 {"3m": {"events": 3, "minutes": 5}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 79분 | 장중재학습 4회 | CB③ ready 111분/369분 (30%) (리셋 3회, 표본손실 90건)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 954 | 09:01:00 | 15:09:00 | 1m 'macro_vix' scale=0.0148 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 160 | 09:05:59 | 15:06:00 | 신뢰도 미달 35.0% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 81 | 09:07:59 | 15:08:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerMonitor` | 72 | 09:00:59 | 14:21:00 | ts=09:00 horizon=1m age=2m max_z=+6.33(volume_acceleration) extreme=2 |
| `Model` | 60 | 09:00:59 | 14:14:01 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerRefresh` | 6 | 08:45:18 | 08:45:18 | 1m CORE 'cvd_divergence' raw_std≈0(0.0225) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 4 | 09:35:59 | 14:57:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `PCR-Dampen` | 3 | 09:09:59 | 14:15:02 | opt_pcr_* 피처 D_FORCE 발동 → 30분간 0.3× 감쇠 적용 |
| `ConfFloorGuard` | 1 | 09:05:59 | 09:05:59 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4427

**컴포넌트 상위 15** — `ScalerFloor`×972, `SIGNAL`×738, `MetaGate`×483, `Ensemble`×383, `FQAdj`×367, `ZeroDiag`×329, `Checklist`×180, `ATR-Horizon`×164, `MicroRegime`×104, `차단`×98, `InstabilityGate`×93, `Model`×90, `WeightCollapse`×81, `ToxicityGate`×79, `ScalerMonitor`×73

### `logs/20260821_LEARNING.log` — 293.0KB · 2887행 · 최종 15:40:24

- 형식 평문 · 시각 인식 2877행 · WARNING=146, INFO=2731, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 08:41:01 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00035 auc=0.529 out_max=0.4002 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=120) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2754 < conf_floor=0.3300 (span=0.00060 auc=0.568 out_max=0.2754, 기저율=0.2750 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-21 08:41:02 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00040 auc=0.501 out_max=0.1502 (기준 auc<0.53 and span<0.020, 기저율=0.1500 n=100) → 보정 미적용, raw 통과
  …
2026-08-21 15:40:24 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-21 15:40:24 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-21 15:40:24 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-21 15:40:24 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-21 15:40:24 [INFO] LEARNING: [Sigma] EOD sigma_20=0.07438% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 144 | 08:41:02 | 13:53:00 | 하한 도달불가 — out_max=0.1503 < conf_floor=0.3300 (span=0.00051 auc=0.546 out_max=0.1503, 기저율=0.1500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Consolidator` | 1 | 15:40:19 | 15:40:19 | 구간 'CLOSE_VOLATILE' 최근 4일 풀링(n=172) 기대손익 -0.314pt (CI상단 -0.007pt) < 0 → 패널티 +0.04 (참고 정확도 26.7%) |
| `DriftAdjuster` | 1 | 15:40:19 | 15:40:19 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 2일) |

**채널** — `LEARNING`×2877

**컴포넌트 상위 15** — `LEARNING`×1214, `SGD`×369, `sigma`×356, `Calibration`×281, `Bias⚠`×274, `Bias`×129, `MetaConf`×78, `OnlineLearner`×71, `ScalerWarmup`×38, `BiasReset`×16, `SHAP`×12, `GBM-64`×8, `GBM`×8, `UPDATE`×6, `RF`×5

### `logs/20260821_HEALTH.log` — 3.8KB · 28행 · 최종 15:00:00

- 형식 평문 · 시각 인식 28행 · WARNING=14, INFO=14

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 09:29:59 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 266ms (표본 20분)
2026-08-21 09:29:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-21 09:30:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=297ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-21 09:39:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2399ms | quality=1.00 | cache_age=173s | exceptions_10m=0
2026-08-21 09:40:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=524ms | quality=1.00 | cache_age=48s | exceptions_10m=0
  …
2026-08-21 13:57:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=375ms | quality=1.00 | cache_age=58s | exceptions_10m=1
2026-08-21 14:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=387ms | quality=1.00 | cache_age=183s | exceptions_10m=1
2026-08-21 14:49:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=338ms | quality=1.00 | cache_age=60s | exceptions_10m=1
2026-08-21 14:59:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2118ms | quality=1.00 | cache_age=109s | exceptions_10m=0
2026-08-21 15:00:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=379ms | quality=1.00 | cache_age=167s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 14 | 09:29:59 | 14:59:02 | level=WARNING degraded=OFF | latency=269ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |

**채널** — `HEALTH`×28

**컴포넌트 상위 15** — `Health`×27, `HealthTrend`×1

### `logs/retrain_eod_20260821.log` — 34.8KB · 316행 · 최종 16:05:54

- 형식 평문 · 시각 인식 167행 · WARNING=10, INFO=157, PLAIN=149

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-21 15:45:03,935 [INFO] EOD_RETRAIN: =======================================================
2026-08-21 15:45:03,935 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-21 15:45:03,935 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-21 15:45:03,935 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-21 15:45:03,935 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
UnicodeEncodeError: 'cp949' codec can't encode character '\u2014' in position 8: illegal multibyte sequence
2026-08-21 16:05:54,364 [INFO] EOD_RETRAIN: [검증 캠페인] 요약: 게이트 ablation 리포트=OK | 호라이즌 conf-층화 검정=OK | 검증 캠페인 판정 리포트=OK | 피처셋 건강 리포트=OK | CVD 앵커 대조 리포트=OK | 조기청산 반사실 [49]=OK | 방향 처분 실험 [40-B]=OK | 섀도우 TB 재학습=OK | 분위 회귀 재학습=OK | 메타라벨 분류기 재학습=OK | MAE/MFE 분석=OK | 월간 로그 정리=FAIL(rc=1)
2026-08-21 16:05:54,395 [INFO] EOD_RETRAIN: 판정 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\validation_campaign_report_20260821.md
2026-08-21 16:05:54,395 [INFO] EOD_RETRAIN: 피처셋 건강 리포트: C:\Users\82108\PycharmProjects\futures\docs\정기점검\금요일점검\MW0601\featureset_health_report_20260821.md
2026-08-21 16:05:54,395 [INFO] EOD_RETRAIN: =======================================================
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:51 | 15:47:25 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1508봉(82%)이 현행 학습구간 (현행 cutoff=2026-08-20 14:38:00 ≥ 홀드아웃 시작=2026-08-13 11:00:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-20 14:38 >= holdout_start=2026-08-13 11:00 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-20 … |
| `GuardGhost` | 4 | 15:46:01 | 15:46:13 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-21 14:27:00까지)인데 acc.txt=0.4048는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×65, `EOD_RETRAIN`×38, `SIGNAL`×37, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×147, `ScalerFloor`×30, `Retrain`×20, `EOD_RETRAIN`×18, `검증 캠페인`×14, `RF`×9, `ShadowTB`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `QuantileReg`×6

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

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 4 |
| 진입 등록(`[Position] 진입`) | 4 |
| 체결(`[체결진입]`) | 4 |
| 청산(`체결청산`) | 4 |
| 차단(`[차단]`) | 98 |
| 사이저 호출(`[Sizer]`) | 5 |

### 포지션 4건 · 승 2 (50%) · 합계 -3.40pt (-179,883원)  ※ 레그 6행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|
| 13:10:00 | LONG | 2 | 3m | 2 | -0.86 | -46,290 | 하드스톱(틱) |
| 13:50:00 | LONG | 2 | 1m | 2 | -3.02 | -154,294 | 하드스톱(틱) |
| 14:00:00 | LONG | 1 | 3m | 1 | +0.14 | +5,355 | 하드스톱(틱) |
| 14:13:00 | LONG | 1 | 3m | 1 | +0.34 | +15,346 | 하드스톱(틱) |

**청산 레그 6행** (부분청산 2 · 전량청산 4)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 13:12:42 | 부분 | 1 | -1.32 | -67,645 | 손절1차 조기축소 |
| 13:15:47 | 전량 | 1 | +0.46 | +21,355 | 하드스톱(틱) |
| 13:51:12 | 부분 | 1 | -1.03 | -53,147 | 손절1차 조기축소 |
| 13:53:08 | 전량 | 1 | -1.99 | -101,147 | 하드스톱(틱) |
| 14:00:44 | 전량 | 1 | +0.14 | +5,355 | 하드스톱(틱) |
| 14:26:51 | 전량 | 1 | +0.34 | +15,346 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×4, `손절1차 조기축소`×2

> 최종 청산이 하드스톱·손절 계열인 포지션 4/4건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -179,883 = 포지션합 -179,883 → OK · `[청산 완료]` 4건 = 조립 포지션 4건 → OK

### CB③ 판정 가능 시간 — **111분 / 369분 (30%)**

acc30m 버퍼 리셋 3회 · 그때 버린 표본 90건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 4건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 13:10:00 | LONG | 2 | 1096.9 | 3m | neutral |
| 13:50:00 | LONG | 2 | 1098.1 | 1m | mean-revert |
| 14:00:00 | LONG | 1 | 1096.6 | 3m | mean-revert |
| 14:13:00 | LONG | 1 | 1102.7 | 3m | mean-revert |

계약수 분포 — 1계약×2, 2계약×2

등급 분포 — `A급(원시C)`×3, `C급`×1

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×2, `prev`×2, `chas`×2, `ofi`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×2, **2계약**×1, **3계약**×2

실제 진입 계약수 — **1계약**×2, **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×5

### 차단 사유 98건 · 30종

| 건수 | 사유 |
|---|---|
| 49 | 등급X — 미통과 항목: 2_confidence |
| 8 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 4 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.1pt > ATR×5.0=13.9pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.3pt > ATR×5.0=12.3pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.8pt > ATR×5.0=13.3pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.0pt > ATR×5.0=14.2pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 16.3pt > ATR×5.0=14.8pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.4pt > ATR×5.0=14.7pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.2pt > ATR×5.0=14.4pt (시가=1068.40 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 11_countertrend |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.2pt > ATR×5.0=14.2pt (시가=1068.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.2pt > ATR×5.0=14.0pt (시가=1068.40 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×49, `3_vwap`×27, `6_foreign`×27, `4_cvd`×16, `5_ofi`×16, `7_prev_bar`×15, `11_countertrend`×3, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회` ×2
- `일간 리셋 완료` ×2
- `연속 손절 2회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 39건 · 최대 11016ms · 5초 초과 15건

상위 — 11016ms, 9922ms, 9703ms, 7813ms, 7515ms, 7500ms, 7296ms, 6890ms

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
| 12:27:09 | 9703ms | 427ms | **9276ms (96%)** |
| 12:37:13 | 11016ms | 461ms | **10555ms (96%)** |
| 12:52:04 | 5109ms | 325ms | **4784ms (94%)** |
| 13:45:04 | 5063ms | 336ms | **4727ms (93%)** |
| 14:05:04 | 5375ms | 370ms | **5005ms (93%)** |
| 14:10:05 | 5219ms | 411ms | **4808ms (92%)** |
| 14:45:04 | 5172ms | 356ms | **4816ms (93%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260821_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:26 2026-08-21 15:40:26 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 55분/일 < 하한 60분 — 금일 47분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 0분
--- ConstOut ×4(표본)
09:36:59 2026-08-21 09:36:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:29:59 2026-08-21 11:29:59 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
13:04:00 2026-08-21 13:04:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
14:57:00 2026-08-21 14:57:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×3(표본)
13:12:42 2026-08-21 13:12:42 [WARNING] SYSTEM: [CB] 연속 손절 1회
13:51:12 2026-08-21 13:51:12 [WARNING] SYSTEM: [CB] 연속 손절 1회
13:53:08 2026-08-21 13:53:08 [WARNING] SYSTEM: [CB] 연속 손절 2회
--- [ExitCooldown] ×8(표본)
13:15:47 2026-08-21 13:15:47 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 13:17:47)
13:15:47 2026-08-21 13:15:47 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 13:17:47)
13:53:08 2026-08-21 13:53:08 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:56:08)
13:53:08 2026-08-21 13:53:08 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:56:08)
--- [SHAP] 슬로우 ×6(표본)
12:49:01 2026-08-21 12:49:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 910ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:57:02 2026-08-21 12:57:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 919ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:46:01 2026-08-21 13:46:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 962ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
14:12:01 2026-08-21 14:12:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1129ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
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
--- [CB] ×2(표본)
15:40:24 2026-08-21 15:40:24 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:24 2026-08-21 15:40:24 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:18 2026-08-21 15:11:18 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:26 2026-08-21 15:40:26 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:41 2026-08-21 15:40:41 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:26 2026-08-21 15:40:26 [INFO] SYSTEM: [Notify] ℹ️ [15:40:26] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:26 2026-08-21 15:40:26 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:41 2026-08-21 15:40:41 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260821_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:05:59 2026-08-21 09:05:59 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
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

### `logs/retrain_eod_20260821.log`
```
--- Traceback ×1(표본)
??:??:?? DB ���� : Traceback (most recent call last):
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260821_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:10 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 14:00 | 장중 후반 · 장중 재학습 | 16 | 14:00:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=49,953,444) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShad… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:24 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260821_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 5 | 08:41:18 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:01:08 [WARNING] _tick_header 간격 9922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9922 band=… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 3 | 09:01:08 [WARNING] _tick_header 간격 9922ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=9922 band=… |
| 10:00 | 장중 초반 | 1 | 09:55:59 [WARNING] 5분 누적 수익률 -0.682% (임계 ±0.454%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1 | 12:05:59 [WARNING] 5분 누적 수익률 -0.311% (임계 ±0.201%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 14:00 | 장중 후반 · 장중 재학습 | 46 | 13:56:01 [WARNING] level=WARNING degraded=OFF | latency=413ms | quality=1.00 | cache_age=182s | exceptions_10m=2 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1 | 15:09:00 [WARNING] 5분 누적 수익률 -0.237% (임계 ±0.170%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 1 | 15:24:43 [WARNING] DynMCPanel.refresh slow 359ms |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:22 [WARNING] 경보 발생: {'1m': 'UPDATE', '3m': 'UPDATE', '5m': 'UPDATE', '10m': 'UPDATE', '15m': 'UPDATE', '30m': 'UPDATE'}  d… |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260821_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 92 | 08:40:46 [INFO] 로테이션 — 8.4MB >= 8MB 임계 → crash_fault.log.1 (보관 4세대) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 200 | 08:54:01 [INFO] #2000 code=A0569 raw_time=85402 parsed=08:54:02 price=1064.06 vol=2 bid1=1063.80 ask1=1064.04 flag=49 side=BU… |
| 10:00 | 장중 초반 | 216 | 09:54:00 [INFO] #35100 code=A0569 raw_time=95401 parsed=09:54:01 price=1090.02 vol=1 bid1=1089.90 ask1=1090.12 flag=50 side=S… |
| 12:00 | 장중 중간점 | 168 | 11:54:00 [INFO] ensemble=1ms checklist_pre=9ms meta_gate=6ms gates=0ms imp=0ms shap=4ms corr=8ms dash_ui=0ms tail=13ms |
| 14:00 | 장중 후반 · 장중 재학습 | 209 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 152 | 15:04:00 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 129 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 41 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260821_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 43 | 08:45:18 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0225) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 110 | 09:00:59 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 09:00:59 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 145 | 09:54:59 [WARNING] 신뢰도 미달 35.4% < 38.9% → 강제 X등급 |
| 12:00 | 장중 중간점 | 148 | 11:54:00 [WARNING] 신뢰도 미달 40.1% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 199 | 13:54:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+2.000 need <0 (SHORT) bull_exh=0.00 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 84 | 15:05:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:24 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

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
| **오늘 20260821** | **15:40** | 로그 본문 |

- 델타 **-82분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [1] 메인 스레드 정지 5초 초과 9건 — 6거래일 동시간대 최다 (P1, 신규 · 리포트 이상점 1-5)
### [2] CB③ 판정 가능 시간 24.4% · 재적합이 만석 30건을 폐기 (P2, 신규 · G-2 첫 라이브 실측)
### [3] `_acc30m_stage` 의 RESTRICTED→NORMAL 복귀가 무기록 (P2, 신규 · 계측 4원칙 ④ 위반 · 리포트 이상점 1-7)
### [4] 시가이격 필터 10건 전량 차단 — 원시 A 1건 포함 (P2, 신규 · 결함 아님 · 리포트 이상점 1-8)
### [5] 이월 처리 결과 (08-21 장전 → 장중)
### [6] 정상 확인 (이상점 아님 — 재상정 방지)
### [7] 코드 변경 0건 · 재기동 0건 · 라이브 DB 미접근
### [8] 스킬 템플릿 정합성
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 모두
   `py310_64`(191차 결정, 재거론 금지) `returncode=0` · **OOM 0건** · 3m/5m 교체 성공
   (`old_acc=0.4048` / `0.4284`) · `ConstOut` 2회 모두 **2분 내 자동 해소** ·
   `[RouterHealth]` 섀도 기록 정상(계측 4원칙 ④ 준수).
5. **CB 발동 0건** — CB① 0 / CB② 0(`9999`, **발동 안 하는 것이 정상**, 재검토 2026-08-29 8일 남음) /
   CB③ HALT 0 / CB④ 0 / **CB⑤ 실발동 0**(경고 4건 전부 발동 임계 5,000ms의 27~48%).
   CB⑤ 경고 원인은 전부 파이프라인 내부 — 09:39:01 `S0=1971ms`가 total 2,399ms의 **82.2%**
   (09:38·11:31 재학습 직후 모델 교체). 2026-08-10 DB 스캔 사고(`S0=3ms` / `S1=3,098ms` /
   `S4=1,951ms`)와 **프로파일이 다르다** — 오늘 점검이 DB를 안 건드렸다는 방증.
6. **`degraded=ON` 0건** · `[HealthPolicy] Degraded 선제차단` 4건 중 실제 진입 차단 1건(09:40:00) ·
   `[Health]` WARNING 8건 전부 다음 분 INFO 복귀 · 지연 기준선 266ms.
7. **`[Brier]` 0건 · `[SHAP] 슬로우` 0건** · SHAP 심사 6회 정상 완료.
   단 `CORE안전=⚠️` 6/6 · 교체후보 1→3개 · 12:13 하락피처 1개 최초 → **주간 심사이므로
   일일 변동으로 판단하지 않는다** → O-14.
8. **`WeightCollapse` 44/205행 = 21.5%** — CLAUDE.md 「확률 판단 기준」 주석의 *"매일 약 21~22%"*
   밴드 내. **평균 conf 집계에서 제외**했다(conf 0.85 고정 「판단 불가」 행).
9. **conf 절대값을 구 기준표에 대지 않았다** — 그날 `min_conf`(09:05 0.379 → 10:30 0.380 →
   11:50 0.620) 대비 상대 위치로만 읽었다. `CONF_SCALE_BREAKS` 2026-07-31 경계 준수.
10. **등급 최종 A/B 0건 · C 27 · X 178(발행 205행)** — 476차 MW0602 「등급 A/B 도달불가」와
    방향은 같으나 MW0601에서는 **원시 A 1건이 생성→P4 강등**됐다. *"도달 불가"* 와
    *"도달 후 강등"* 은 다른 이야기. **브랜치 상이(함정 ③) — 두 관측 합산 금지 · 표본 1건
    확정 결론 금지(313차).**
11. **`MAX_CONTRACTS=3` 상한 접촉 0건** · [28] `sizing_inversion_watch` qty≥3 표본 오늘 **0건 추가**.
12. **중기(10m·15m)·장기(30m) CORE 그룹 미발동** — 474차 확정 구조(`select_entry_horizon()`이
    `1m`/`3m`/`5m`/`None`만 반환). `tests/test_473_core_group_reachability.py`가 고정. **재상정 금지.**
13. **절대원칙 §3 VWAP 강제 X 준수** — `3_vwap` 미통과 상태 진입 **0건**(진입 자체가 0건).
14. **절대원칙 §6 준수** — 알파 리서치 봇 자동 통합 흔적 0건.
15. **재인용 금지 수치 미사용** — ① 2026-06-25 SHAP=0 ② 2026-08-01 §9-3 이벤트 단위 사이징
    통계 4종 ③ `mdd_pct_of_peak` ④ 417차 이전 `[Sizer]` 379/86(22.7%) — **넷 다 인용하지 않았다.**

### [7] 코드 변경 0건 · 재기동 0건 · 라이브 DB 미접근

`raw_data.db`·`predictions.db`·`trades.db`에 **어떤 쿼리도 돌리지 않았다**
(CLAUDE.md 「장중 라이브 DB 분석 금지」 — 2026-08-10 13:47 CB⑤ 자가유발 전례).
증거는 로그 파일·설정 파일·git 메타데이터에서만 취득. 소스 파일은 **읽기만** 했다
(`safety/circuit_breaker.py` · `strategy/entry/time_strategy_router.py` ·
`strategy/entry/checklist.py` · `config/settings.py`).
`git commit` / `git push` **미실행**.

### [8] 스킬 템플릿 정합성

`references/report_template.md`는 아직 `-pre`/`-intra`/`-post` 3파일 형식을 서술하고 있으나,
477차(`44e2652`) 대원칙 B가 **하루 한 파일 append**로 철회했다. 이번 장중 절도 대원칙 B를
따랐고 템플릿을 따르지 않았다. **템플릿 갱신은 별도 항목**(SKILL.md 「단 하나 예외」 절 지시대로
여기 한 줄 남긴다).

```

</details>

### dev_memory/NEXT_TODO.md — 1.1MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 🔵 기한 — 주간회의(2026-08-22 금) 상정
### 다음 거래일(08-21)~ 관측
### ✅ 완료·종결 처리 (477차 장전·장중 등록분)
### 481차 — 장전 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 481차 후속 — 장중 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 481차 후속2 — 장후 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 483차 — 장전 점검 (MW0601, 2026-08-21 금 · 분석만, 코드 0건)
### 483차 후속 — 장중 점검 (MW0601, 2026-08-21 금 · 분석만, 코드 0건)
```

미완료 체크박스 **1754건** (끝에서 30건)
```
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
- [ ] **P2-E 메인 스레드 정지 일별 집계 승격 (P2 · 이상점 1-5)** —
- [ ] **P2-F `_acc30m_stage` 변경에 사유 로그 필수화 (P2 · 이상점 1-7 · 계측 4원칙 ④)** —
- [ ] **P2-G `references/phases.md` B-1 「T-30은 퇴역 대상」 문구 정정 (P2)** —
- [ ] **테스트 축 확장 검토 (P2, 설계 미착수)** — `tests/test_457_fallback_visibility.py`는
- [ ] **고도화 ④ CB③ 판정 가능 시간 × 스케일러 재적합 스케줄 (G-2 후속)** —
- [ ] **고도화 ⑤ 「진입 0건」 원인 계층화 (`[ZeroDiag]` layer 코드)** —
- [ ] **고도화 ⑥ 시가이격 채널 [9]에 판정 축 2개 추가 (354차 후속 · 완화 제안 아님)** —
- [ ] **O-11 (장후) 메인 스레드 정지 종일 집계** — 15:45까지 5초 초과 총건수·최대·`band=WARN` 비율.
- [ ] **O-12 (장후) 시가이격 채널 [9] `open_gap_shadow` 누적** — 오늘 EOD 생성
- [ ] **O-13 (장후) GBM 배치 재학습 「30분마다」 조건 확인** — 오늘 2회 모두 `ConstOut`
- [ ] **O-14 (장후 + 주간회의) `[SHAP] CORE안전=⚠️` 6/6 · 교체후보 1→3개** —
- [ ] **O-15 (장후) CB③ 판정 가능 시간 종일 비율** — 12:28 현재 24.4%(51/209분).
- [ ] **O-16 (장후) 오늘 최종 진입 0건 여부** — 13:00 `OTHER`→`LUNCH_RECOVERY` 전환 후 진입 발생 여부.
- [ ] **`references/report_template.md` 갱신 (P2)** — 아직 `-pre`/`-intra`/`-post` 3파일 형식을
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
()`에 ①`scope`에 `30m` 미포함 시 리셋 스킵
      ②표본 가중 감쇠로 `n_effective` 유지 — 두 안의 `ready=Y` 시간을 **실제와 나란히 기록만**.
      2주 뒤 「가용 시간 증가분」과 「그 구간 CB③ 오판 여부」를 함께 판정.
      ⚠ **P2-F 선행.** 1일 관측으로 정책 변경 금지.
- [ ] **고도화 ⑤ 「진입 0건」 원인 계층화 (`[ZeroDiag]` layer 코드)** —
      오늘 진입 0건의 원인이 3층으로 갈렸는데 `[차단]` 63건이 한 통에 섞여 층이 안 보인다:
      ①시간대 정책(`OTHER` 11:50~13:00, 37분/12:27 기준·13:00까지면 70분)
      ②품질 게이트 52건 ③상황 필터 11건.
      `2_confidence` 34건이 "압도적"으로 보였으나 상당수가 ①층 `min_conf=0.620` 탓이라
      **게이트 임계 의심의 근거가 못 된다** — 316차 HurstGate 발견 규칙이 층이 섞이면 오작동한다.
      제안: `[ZeroDiag]`(오늘 187건)에 `| layer=TIME_POLICY(zone=OTHER)` 필드 추가,
      수집기 §5 차단 사유 표에 **층별 소계**. 로그 문자열 한 필드 · **정책 무변경.**
- [ ] **고도화 ⑥ 시가이격 채널 [9]에 판정 축 2개 추가 (354차 후속 · 완화 제안 아님)** —
      현재 `open_gap_shadow`는 `hyp_pnl_pts`·승률만 본다. 여기에
      ①차단 시점 **방향이탈 ÷ (ATR×5)** 배율 ②그날 **시초가 대비 종가 변동률** 을 함께 적재하면,
      FAIL 판정 시 *"임계를 올릴 것인가 / 기준점을 VWAP 등으로 바꿀 것인가"* 를 같은 데이터로 답한다.
      354차 항목이 이미 *"그때의 실측 gap·ATR 값을 근거로 기준점(예: VWAP)·임계값 재설계 착수"*
      라고 적어 뒀으므로 **그 "그때"를 위한 적재를 지금 시작**하는 것.
      실측: 오늘 방향이탈 16.3~23.5pt vs 임계 12.3~14.8pt, 시초가 1068.40 → 12:31 1098.38
      (+29.98pt/+2.81%). ⚠ **오늘 10건은 표본이지 판정이 아니다. 문턱 인하 금지(458차 D6).**

**관측 (장후가 닫는다)**

- [ ] **O-11 (장후) 메인 스레드 정지 종일 집계** — 15:45까지 5초 초과 총건수·최대·`band=WARN` 비율.
      **9건이 오전에만 나온 것**이라 종일로는 더 늘 수 있다. 직전 5거래일 종일과 대조.
- [ ] **O-12 (장후) 시가이격 채널 [9] `open_gap_shadow` 누적** — 오늘 EOD 생성
      `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` [9]번 채널.
      누적 표본이 `min_samples=20`에 도달했는가 · 판정 `PASS`/`FAIL`/`보류`.
      **문턱을 낮춰 판정하지 말 것(458차 D6 위반).**
- [ ] **O-13 (장후) GBM 배치 재학습 「30분마다」 조건 확인** — 오늘 2회 모두 `ConstOut`
      트리거(`force=True intraday=True`, `scope` 단일 호라이즌). CLAUDE.md STEP 3의 *"30분마다"*가
      정기 스케줄인지 조건부인지 코드 확인 → 다르면 **문서 정정 대상 등록**.
- [ ] **O-14 (장후 + 주간회의) `[SHAP] CORE안전=⚠️` 6/6 · 교체후보 1→3개** —
      08:41 `하락피처=0 교체후보=1` → 10:41~ `교체후보=3` → 12:13 `하락피처=1` 최초.
      **주간 심사**이므로 일일 변동으로 판단 금지. 절대원칙 §3 CORE는 **교체 불가**이므로
      `CORE안전=⚠️`의 정확한 의미를 코드에서 확인할 것.
- [ ] **O-15 (장후) CB③ 판정 가능 시간 종일 비율** — 12:28 현재 24.4%(51/209분).
      15:45까지 재적합 추가 횟수와 폐기 표본 수(`[DBG-CB] resets=N dropped=M` 최종값). G-2 근거.
- [ ] **O-16 (장후) 오늘 최종 진입 0건 여부** — 13:00 `OTHER`→`LUNCH_RECOVERY` 전환 후 진입 발생 여부.
      **끝내 0건이면 O-1·O-6·O-7·O-10을 전부 다음 거래일로 재이월**해야 한다 —
      4개 항목이 연달아 표본 부족으로 밀리는 것 자체를 기록할 것.
- [ ] **`references/report_template.md` 갱신 (P2)** — 아직 `-pre`/`-intra`/`-post` 3파일 형식을
      서술한다. 477차(`44e2652`) 대원칙 B(하루 한 파일 append)로 철회됐으므로 템플릿을 맞출 것.

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

### `data/heartbeat_MW0601_20260821.json` — 244B · 08-21 15:40:34
```json
{
 "pid": 18348,
 "written_at": "2026-08-21T15:40:34",
 "beat_epoch": 1787294433.3273687,
 "beat_age_sec": 0.7,
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

### `docs/정기점검/매일점검` — 63개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260821-점검리포트.md` | 108.1KB | 08-21 12:42 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_intra.md` | 57.0KB | 08-21 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260821_pre.md` | 46.8KB | 08-21 08:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_pre.md` | 49.0KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_post.md` | 70.5KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_intra.md` | 61.3KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_pre.md` | 46.2KB | 08-20 22:24 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_post.md` | 63.9KB | 08-20 22:24 |

### `docs/정기점검/금요일점검` — 58개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260821.md` | 4.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260821.json` | 2.9KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260821.md` | 26.2KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260821.json` | 34.4KB | 08-21 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260821.md` | 167.8KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260821.json` | 91.9KB | 08-21 15:49 |
| `docs/정기점검/금요일점검/MW0602/0816_주간회의_검토보고_MW0602.md` | 39.2KB | 08-20 21:31 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.json` | 7.6KB | 08-18 22:58 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/retrain_eod_20260821.log`: **Traceback** 출현 1건 — 크래시/메모리 계열
2. 포지션 4건 중 최종청산이 하드스톱·손절 계열 **4건(100%)** — 손절 준수율 확인 필요 (레그 6행)
3. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. **SYSTEM 로그가 직전 5거래일 중앙값(17:02)보다 82분 이르게 끝났다** (오늘 15:40) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
6. 메인 스레드 정지 5초 초과 **15건** (최대 11016ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260821_WARN.log`: **ConstOut** 4건(표본)
8. `logs/20260821_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20260821_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260821_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260821_LEARNING.log`: **축퇴** 8건(표본)
12. 미커밋 변경 474건
13. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260821*.log` (Windows) / `grep 강제청산 logs/*20260821*.log`*