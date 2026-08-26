# 미륵이 증거 다이제스트 — 2026-08-26 / POST

- 생성 2026-08-26 16:16:18 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/eager-bold-cori/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260826` · `2026-08-26` · `260826` · `0826`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260826.txt` | 28B | 08-26 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260826.txt` | 28B | 08-26 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260826.txt` | 209B | 08-26 15:48 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260826.log` | 437B | 08-26 15:12 |
| `freeze_sentinel_alert_{DATE}.txt` | 1 | `data/freeze_sentinel_alert_20260826.txt` | 528B | 08-26 15:45 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260826.log` | 17.3KB | 08-26 16:15 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260826.json` | 242B | 08-26 15:40 |
| `launcher_{DATE}_084001_31359.log` | 1 | `logs/Mireuk_batch/launcher_20260826_084001_31359.log` | 1.6MB | 08-26 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260826.log` | 26.2KB | 08-26 12:17 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260826.log` | 20.8KB | 08-26 15:48 |
| `retrain_intraday_{DATE}_093600.log` | 1 | `logs/retrain_intraday_20260826_093600.log` | 2.4KB | 08-26 09:36 |
| `retrain_intraday_{DATE}_103001.log` | 1 | `logs/retrain_intraday_20260826_103001.log` | 2.4KB | 08-26 10:30 |
| `retrain_intraday_{DATE}_111200.log` | 1 | `logs/retrain_intraday_20260826_111200.log` | 2.4KB | 08-26 11:12 |
| `retrain_intraday_{DATE}_120501.log` | 1 | `logs/retrain_intraday_20260826_120501.log` | 2.4KB | 08-26 12:05 |
| `retrain_intraday_{DATE}_131302.log` | 1 | `logs/retrain_intraday_20260826_131302.log` | 2.4KB | 08-26 13:13 |
| `strategy_report_{DATE}_154023.txt` | 1 | `data/daily_reports/strategy_report_20260826_154023.txt` | 2.3KB | 08-26 15:40 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260826_BACKFILL.log` | 0B | 08-26 07:18 |
| `{DATE}_DATA.log` | 1 | `logs/20260826_DATA.log` | 343.7KB | 08-26 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260826_DEBUG.log` | 232.0KB | 08-26 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260826_HEALTH.log` | 3.5KB | 08-26 14:37 |
| `{DATE}_HOGA.log` | 1 | `logs/20260826_HOGA.log` | 48.5MB | 08-26 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260826_LEARNING.log` | 295.2KB | 08-26 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260826_MICRO.log` | 976.5KB | 08-26 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260826_PROBE.log` | 96.6KB | 08-26 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260826_SIGNAL.log` | 586.4KB | 08-26 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260826_SYSTEM.log` | 785.0KB | 08-26 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260826_TRADE.log` | 7.7KB | 08-26 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260826_WARN.log` | 83.7KB | 08-26 15:40 |

## 2. 코드·커밋 상태

- HEAD `9d664fa` · 브랜치 `v9-dev` · 미커밋 520건 · 실질 변경 3건 · 코드(.py) 0건 · EOL 파생 510건 (추적변경 513 · 미추적 7 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `.claude/skills/mireuk-daily-check/SKILL.md`, `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`
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
… 외 480건
```

**당일(2026-08-26) 커밋**
```
9d664fa [MW0601] 494차 후속: F-AE·F-AF — 청산 마감 줄 포지션 합계 병기 + 승패 단위 섀도
74aaee6 [MW0601] 497차 체리픽: 손익 축 정합 P1·P2·P3 — commission_rate_used 기록 결함 fix 포함
5c54496 [MW0601] 495차 후속 체리픽: 수수료율을 로그인 채널 감지로 파생 — v9-dev는 CYBOS
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
```

**최근 커밋 12건**
```
9d664fa [MW0601] 494차 후속: F-AE·F-AF — 청산 마감 줄 포지션 합계 병기 + 승패 단위 섀도
74aaee6 [MW0601] 497차 체리픽: 손익 축 정합 P1·P2·P3 — commission_rate_used 기록 결함 fix 포함
5c54496 [MW0601] 495차 후속 체리픽: 수수료율을 로그인 채널 감지로 파생 — v9-dev는 CYBOS
c0f2735 [MW0601] 493차 후속8: 미니선물 사양 반영 + 브로커 사양 설정절 신설 — 공식 요율로 CR-7 종료
35ed037 [MW0601] 493차 후속7: F-U 단일 인스턴스 가드 — 프로브 분리·리허설 완료, 런처 배선은 되돌림
a0fcee2 [MW0601] 493차 후속6: 사용자 조치 구현 8건 — F-Y·F-X·F-V·F-Z·F-AA·F-AB·F-P·F-Q
a7120ad [MW0601] 493차 후속5: 수수료율 6.54배 오차 fix — F-1~F-5 (F-AD ①~⑥ 구현)
f18cdad [MW0601] 492차 후속: 배포 피처셋 vs 노이즈 하한선 대조 (§17) — 배포 67개 중 하한 초과 9개(13%)
fc9f843 [MW0601] 492차: 피처 수명(persistence) 분석 — 호라이즌 배정 근거 없음 확정 · 재검증 규약 신설 · L0/L1 참고계측 확장
91c6120 [MW0601] 491차: 0824 장후 fix 9건 구현 — F-L·F-M·F-N·F-G·F-K·F-I·F-B·F-F·F-D (+ lock_guard 콘솔)
d66ec0d [MW0601] 점검 산출물 적재: 0812~0824 일일점검 증거 27건 · 리포트 2건 · 0821 주간 3종 · 26주 WFA 피처셋 재검증
4dbdf80 [MW0601] 489차: 주간회의 승인 6건 — ⑨ WFA 이관 · [46]③ 재등록+배선 · 좀비결정 7건 분류 · [8]② 계측 이식
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

_본문 미열람(설정): `20260826_HOGA.log` 48.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260826.txt`** — 28B · 08-26 15:40:23
```
2026-08-26T15:40:23.335383
```

**`data/daily_close_started_20260826.txt`** — 28B · 08-26 15:40:20
```
2026-08-26T15:40:20.774513
```

**`data/daily_reports/strategy_report_20260826_154023.txt`** — 2.3KB · 08-26 15:40:23
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-08-26 15:40
========================================================
  버전    : v1.0  (66일차)
  판정    : OUTPERFORM
  Live(20일): Sh=3.01  MDD(자본대비)=2.2%
  당일      : WR=100.0%  PF=16.92
  롤링20일: 누적 +1473041원  Sh=3.01  MDD(자본대비)=2.2%  MDD(peak대비)=60.0%
  당일손익 : broker(gross) +232,000원  수수료 42,098원  net +189,902원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.090 (CLEAR)
  PSI/feat: cvd=0.128  vwap_position=0.090  ofi=0.006
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 -12,001원  승률 70.0%  합계 -240,026원
  등급별 순EV(30일): A=+7,839원(139건,승65%)  C=-1,367원(34건,승74%)
  호라이즌별 순EV(30일): 1m=+22,598원(23건)  3m=-6,900원(124건)  5m=+50,393원(23건)  ?=+73,309원(3건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 31분  5일평균 46분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 29.9pt(5일평균 45.2pt)  1분평균변동 0.93pt(5일평균 1.06pt)
--------------------------------------------------------
  진입 퍼널(2026-08-26, 총 370분):
    FLAT 228 → conf미달 94 → CoherenceGate 15 → 게이트차단 24 → 후보 9 → 진입 2
    └ 등급상향경로(앙상블X→체크리스트통과): 3건 [285차-P5]
    게이트별: 체크리스트항목미달=19  마감시간(신규진입금지)=2  포지션보유중(평가생략)=1  콜드스타트/기타(RegimeOverride)=1  Degraded신뢰도=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 7건
      └ 상세: JointGateBlock=7
      └ JointGateBlock 7건 (무정보폴백 5건 = 71.4%) [표본 13건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260826.txt`** — 209B · 08-26 15:48:52
```
completed: 2026-08-26 15:48:52
rows: 40383
cols: 97
horizons_replaced: 6/6
t_load_s: 46.5
t_retrain_s: 180.8
t_total_s: 228.1
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/freeze_sentinel_alert_20260826.txt`** — 528B · 08-26 15:45:40
```
[FreezeSentinel] 2026-08-26 15:45:40 CRITICAL
  라이브 프로세스 동결 — 측정 가능한 신호 3종이 전부 300s 이상 정체다. 프로세스는 살아 있을 수 있으나 아무 일도 하지 않는다 (런처 재기동도 걸리지 않는다)
  · heartbeat        307s 전 (임계 300s) — 정체
  · crash_fault[TS]  307s 전 (임계 300s) — 정체
  · SYSTEM.log       302s 전 (임계 300s) — 정체
  · _exit_normally   **미측정**(플래그 없음/읽기 실패) — 동결 판정 유지
```

_다이제스트 대상 8/20개 (중요도순). 제외: `retrain_intraday_20260826_093600.log`, `retrain_intraday_20260826_111200.log`, `retrain_intraday_20260826_103001.log`, `retrain_intraday_20260826_120501.log`, `20260826_MICRO.log`, `20260826_DATA.log`, `20260826_PROBE.log`, `launcher_20260826_084001_31359.log`_

### `logs/20260826_TRADE.log` — 7.7KB · 60행 · 최종 15:40:21

- 형식 평문 · 시각 인식 60행 · INFO=60

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:13 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-26 08:41:17 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-26 09:39:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,349,062) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-26 09:39:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev❌ time✅ risk✅ chas✅ coun✅ | conf=45.0%
2026-08-26 09:39:01 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 1062.82 | 손절=1066.36 1차=1061.64(×0.42) 2차=1059.28 horizon=3m hurst=mean-revert
  …
2026-08-26 12:19:01 [INFO] TRADE: [Position] 체결청산 LONG @ 1085.52 | PnL=+2.85pt (+131,879원) | TP2(전량)
2026-08-26 12:19:01 [INFO] TRADE: [청산 완료] PnL=+2.85pt (+131,879원)
2026-08-26 14:38:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=49,538,950) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-26 14:38:01 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-08-26 15:40:21 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×60

**컴포넌트 상위 15** — `Chejan`×14, `Position`×9, `Sizer`×9, `JointGateBlock 차단`×7, `주문요청`×6, `ProfitGuard`×2, `진입체크`×2, `체결진입`×2, `체결진입보정`×2, `TickTP1`×2, `TP1 부분청산`×2, `청산 완료`×2, `TickStop-S0C`×1

### `logs/20260826_WARN.log` — 83.7KB · 415행 · 최종 15:40:22

- 형식 평문 · 시각 인식 415행 · WARNING=415

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-26 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-08-26 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3328 band=INFO since_pipe_s=NA
2026-08-26 08:41:28 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3750ms — live 중단 원인 분석용
  …
2026-08-26 15:07:03 [WARNING] SYSTEM: [HealthPolicy] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\PycharmProjects\futures\config\constants.py)
2026-08-26 15:08:00 [WARNING] SYSTEM: [HealthPolicy] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\PycharmProjects\futures\config\constants.py)
2026-08-26 15:09:00 [WARNING] SYSTEM: [HealthPolicy] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\PycharmProjects\futures\config\constants.py)
2026-08-26 15:40:22 [WARNING] SYSTEM: [NetRecon] 브로커 net 미수신 — 대사 불가(0이 아니라 미측정). CpTd6197 예탁현금/익일가예탁현금 수신 여부를 확인할 것
2026-08-26 15:40:22 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 46분/일 < 하한 60분 — 금일 31분. | ConfFloorGuard 도달가능 0분 · 도달불가 39분 · 재지않음 331분
```

</details>

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `HealthPolicy` | 181 | 09:01:00 | 15:09:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1904ms quality=0.86 cache=0s exc10m=0) | cause=S5(1481ms) |
| `LiveDBG` | 67 | 08:41:21 | 15:05:03 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ScalerRefresh` | 16 | 09:19:00 | 15:05:02 | 5분 누적 수익률 +0.739% (임계 ±0.529%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `CB③-P4` | 16 | 10:24:00 | 14:22:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `ChejanFlow` | 14 | 09:39:01 | 12:19:01 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='793' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:39:00.987' | positio… |
| `ChejanMatch` | 14 | 09:39:01 | 12:19:01 | order_no='793' | pending='ENTRY:SHORT qty=2 filled=0 order_no=793 reason=진입 req_at=09:39:00.987' | pending_matched=True |
| `Health` | 13 | 09:00:02 | 14:36:00 | level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0 |
| `PipePerf` | 12 | 09:00:02 | 14:24:02 | total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| `CB⑤` | 12 | 09:00:02 | 14:24:02 | 파이프라인 1904ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `PendingOrder` | 12 | 09:39:00 | 12:19:01 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1062.82, 'reason': '진입', 'hint_source': '', 'atr': 2.7786, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `MainStallTrace` | 8 | 09:00:08 | 12:17:05 | 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260826.log |
| `SHAP` | 8 | 11:40:01 | 15:05:03 | 슬로우 감지 937ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |

**채널** — `SYSTEM`×402, `HEALTH`×13

**컴포넌트 상위 15** — `HealthPolicy`×181, `LiveDBG`×67, `ScalerRefresh`×16, `CB③-P4`×16, `ChejanFlow`×14, `ChejanMatch`×14, `Health`×13, `PipePerf`×12, `CB⑤`×12, `PendingOrder`×12, `MainStallTrace`×8, `SHAP`×8, `ConstOut`×5, `EntryFillFlow`×4, `ExitCooldown`×4

### `logs/20260826_SYSTEM.log` — 785.0KB · 5784행 · 최종 15:40:38

- 형식 평문 · 시각 인식 5763행 · INFO=5763, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:40:46 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=18960 | 행감지=30s all_threads=True
2026-08-26 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-26 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-26 08:41:00 [INFO] SYSTEM: 미륵이 초기화
2026-08-26 08:41:00 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-25) 종가 버퍼 로드: 384봉
  …
2026-08-26 15:40:23 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-08-26 15:40:23 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-26 15:40:38 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-26 15:40:38 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-26 15:40:38 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5763

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1163, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `MicroRegime`×110, `System`×98, `RegimeFingerprint`×67, `OptionChain`×42, `IntradayRegime`×31, `CybosEvent`×28, `BalanceUI`×26

### `logs/20260826_SIGNAL.log` — 586.4KB · 5163행 · 최종 15:40:22

- 형식 평문 · 시각 인식 5163행 · WARNING=2050, INFO=3113

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.455
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.442
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.433
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.429
2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.438
  …
2026-08-26 15:09:00 [INFO] SIGNAL: [차단] 14:50 이후 — 신규 진입 금지 구간 (345차)
2026-08-26 15:10:14 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-26 15:40:21 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-26 15:40:22 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-26 age=26m extreme=444 refresh=38 grade_x=118 cb3=0
2026-08-26 15:40:22 [INFO] SIGNAL: [ModelHealth] date=2026-08-26 앙상블유효가동률=75.9% | 파이프라인 370분 | ConstOut 5회/9분 {"3m": {"events": 3, "minutes": 5}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 80분 | 장중재학습 5회 | CB③ ready 152분/370분 (41%) (리셋 3회, 표본손실 90건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1506 | 09:00:02 | 15:05:02 | 1m 'macro_vix' scale=0.0139 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 156 | 09:00:00 | 14:32:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 128 | 09:06:01 | 15:09:00 | 신뢰도 미달 34.4% < 41.2% → 강제 X등급 |
| `ScalerMonitor` | 126 | 09:00:00 | 14:32:00 | ts=08:59 horizon=1m age=1m max_z=-4.33(mlofi_norm) extreme=2 |
| `WeightCollapse` | 80 | 09:07:00 | 15:07:03 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 48 | 08:45:21 | 08:59:01 | 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 5 | 09:35:00 | 13:12:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:00:01 | 09:00:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4550 (conf_floor=0.330, min_conf=0.455, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5163

**컴포넌트 상위 15** — `ScalerFloor`×1530, `SIGNAL`×740, `Ensemble`×381, `FQAdj`×367, `MetaGate`×356, `ZeroDiag`×340, `Model`×192, `Checklist`×147, `ATR-Horizon`×131, `ScalerMonitor`×127, `InstabilityGate`×122, `ConfStuckBoost`×111, `MicroRegime`×110, `ScalerRefresh`×91, `차단`×83

### `logs/20260826_LEARNING.log` — 295.2KB · 2904행 · 최종 15:40:21

- 형식 평문 · 시각 인식 2904행 · WARNING=145, INFO=2759

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00082 auc=0.530 out_max=0.4460 (기준 auc<0.53 and span<0.020, 기저율=0.4455 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00036 auc=0.509 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
2026-08-26 08:41:04 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00084 auc=0.533 out_max=0.4505 (n=120) → 보정 재적용
  …
2026-08-26 15:40:21 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-26 15:40:21 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-26 15:40:21 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-26 15:40:21 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-26 15:40:21 [INFO] LEARNING: [Sigma] EOD sigma_20=0.09098% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 143 | 08:41:04 | 13:07:01 | 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Buffer-Timing` | 1 | 14:24:01 | 14:24:01 | total=966ms raw_fetch=4ms pred_select=3ms pred_update=1ms pred_insert=0ms verified=4 |
| `Consolidator` | 1 | 15:40:21 | 15:40:21 | 구간 'OPEN_VOLATILE' 최근 4일 풀링(n=281) 기대손익 -0.637pt (CI상단 -0.200pt) < 0 → 패널티 +0.04 (참고 정확도 27.4%) |

**채널** — `LEARNING`×2904

**컴포넌트 상위 15** — `LEARNING`×1213, `SGD`×371, `sigma`×357, `Calibration`×279, `Bias⚠`×183, `Bias`×131, `CONF⚠`×115, `MetaConf`×77, `OnlineLearner`×66, `ScalerWarmup`×43, `BiasReset`×16, `SHAP`×12, `GBM-64`×10, `GBM`×10, `RF`×6

### `logs/20260826_HEALTH.log` — 3.5KB · 26행 · 최종 14:37:00

- 형식 평문 · 시각 인식 26행 · WARNING=13, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0
2026-08-26 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=519ms | quality=0.86 | cache_age=96s | exceptions_10m=0
2026-08-26 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 276ms (표본 20분)
2026-08-26 09:33:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=264ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-26 09:34:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=242ms | quality=1.00 | cache_age=58s | exceptions_10m=0
  …
2026-08-26 13:45:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=336ms | quality=1.00 | cache_age=59s | exceptions_10m=1
2026-08-26 14:24:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1852ms | quality=1.00 | cache_age=15s | exceptions_10m=3
2026-08-26 14:25:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=297ms | quality=1.00 | cache_age=73s | exceptions_10m=3
2026-08-26 14:36:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=301ms | quality=1.00 | cache_age=183s | exceptions_10m=1
2026-08-26 14:37:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=270ms | quality=1.00 | cache_age=59s | exceptions_10m=1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 13 | 09:00:02 | 14:36:00 | level=WARNING degraded=OFF | latency=1904ms | quality=0.86 | cache_age=37s | exceptions_10m=0 |

**채널** — `HEALTH`×26

**컴포넌트 상위 15** — `Health`×25, `HealthTrend`×1

### `logs/retrain_eod_20260826.log` — 20.8KB · 142행 · 최종 15:48:53

- 형식 평문 · 시각 인식 142행 · WARNING=10, INFO=132

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 15:45:04,849 [INFO] EOD_RETRAIN: =======================================================
2026-08-26 15:45:04,850 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-26 15:45:04,850 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-26 15:45:04,850 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-26 15:45:04,851 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-26 15:48:53,480 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0478 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-26 15:48:53,481 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1184 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-26 15:48:53,483 [INFO] SIGNAL: [ScalerRefresh] ts=15:48 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-08-26 15:48:53,488 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-26 15:48:53,489 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:59 | 15:47:45 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1502봉(81%)이 현행 학습구간 (현행 cutoff=2026-08-25 14:38:00 ≥ 홀드아웃 시작=2026-08-19 11:19:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-25 14:38 >= holdout_start=2026-08-19 11:19 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-25 … |
| `GuardGhost` | 4 | 15:46:07 | 15:46:19 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-26 12:42:00까지)인데 acc.txt=0.4144는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×65, `SIGNAL`×49, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×20, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `GuardGhost`×4, `RegimeFingerprint`×3, `WaitDC`×2, `P8`×2

### `logs/retrain_intraday_20260826_131302.log` — 2.4KB · 20행 · 최종 13:13:23

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-26 13:13:02,321 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-26 13:13:02,322 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-26 13:13:02,322 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-26 13:13:02,322 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_9a6f5af4.json
2026-08-26 13:13:05,313 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-26 13:13:23,645 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=1.03s | old_acc=0.4144)
2026-08-26 13:13:23,732 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-26 13:13:23,732 [INFO] LEARNING: [Retrain] 완료 | 18.4초 | 성공=1/1 호라이즌
2026-08-26 13:13:23,733 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 21.4s 데이터=4800행
2026-08-26 13:13:23,734 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_9a6f5af4.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) | 2 |
| 체결(`[체결진입]`) | 2 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 83 |
| 사이저 호출(`[Sizer]`) | 9 |

### 포지션 2건 · 승 2 (100%) · 합계 +4.64pt (+189,902원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:39:01 | SHORT | 2 | 3m | 2 | +0.84 | +21,144 | 하드스톱(틱) |
| 12:17:00 | LONG | 2 | 3m | 2 | +3.80 | +168,758 | TP2(전량) |

**청산 레그 4행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:39:44 | 부분 | 1 | +0.87 | +33,072 | TP1 부분청산 33% |
| 09:41:09 | 전량 | 1 | -0.03 | -11,928 | 하드스톱(틱) |
| 12:18:14 | 부분 | 1 | +0.95 | +36,879 | TP1 부분청산 33% |
| 12:19:01 | 전량 | 1 | +2.85 | +131,879 | TP2(전량) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱(틱)`×1, `TP2(전량)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +189,902 = 포지션합 +189,902 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### CB③ 판정 가능 시간 — **152분 / 370분 (41%)**

acc30m 버퍼 리셋 3회 · 그때 버린 표본 90건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:39:01 | SHORT | 2 | 1062.82 | 3m | mean-revert |
| 12:17:00 | LONG | 2 | 1082.66 | 3m | trend |

계약수 분포 — 2계약×2

등급 분포 — `A급(원시C)`×1, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×1, `prev`×1, `time`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **3계약**×9

실제 진입 계약수 — **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×9

### 차단 사유 83건 · 20종

| 건수 | 사유 |
|---|---|
| 50 | 등급X — 미통과 항목: 2_confidence |
| 5 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 3 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 3 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 3 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 1 | 청산 후 쿨다운 — 128초 후 재진입 가능 |
| 1 | JointGateBlock — meta=0.63 tox=0.70 joint=0.439 < 0.50 |
| 1 | JointGateBlock — meta=0.61 tox=0.70 joint=0.426 < 0.50 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 10_chase |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 11_countertrend |
| 1 | 청산 후 쿨다운 — 60초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 0초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 10_chase |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 7_prev_bar |

**체크리스트 미통과 항목 누적** — `2_confidence`×50, `3_vwap`×19, `6_foreign`×19, `5_ofi`×11, `7_prev_bar`×10, `4_cvd`×8, `10_chase`×2, `11_countertrend`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 3건

- `일간 리셋 완료` ×2
- `연속 손절 1회 (300초 창, 포지션 단위)` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 29건 · 최대 8141ms · 5초 초과 8건

상위 — 8141ms, 7718ms, 7297ms, 5765ms, 5343ms, 5312ms, 5218ms, 5016ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8141ms | 1904ms | **6237ms (77%)** |
| 11:39:04 | 5312ms | 463ms | **4849ms (91%)** |
| 11:44:04 | 5218ms | 352ms | **4866ms (93%)** |
| 11:49:04 | 5343ms | 337ms | **5006ms (94%)** |
| 11:54:07 | 7718ms | 469ms | **7249ms (94%)** |
| 12:07:05 | 5765ms | 2448ms | **3317ms (58%)** |
| 12:12:06 | 7297ms | 434ms | **6863ms (94%)** |
| 12:17:05 | 5016ms | 548ms | **4468ms (89%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260826_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:22 2026-08-26 15:40:22 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 46분/일 < 하한 60분 — 금일 31분. | ConfFloorGuard 도달가능 0분 · 도달불가 39분 · 재지않음 331분
--- ConstOut ×5(표본)
09:35:00 2026-08-26 09:35:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:29:00 2026-08-26 10:29:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
11:11:00 2026-08-26 11:11:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:04:00 2026-08-26 12:04:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×8(표본)
09:00:08 2026-08-26 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260826.log
11:39:04 2026-08-26 11:39:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260826.log
11:44:04 2026-08-26 11:44:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260826.log
11:49:04 2026-08-26 11:49:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260826.log
--- [Brier] 과신 ×1(표본)
11:47:00 2026-08-26 11:47:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.354 > 0.35
--- [CB] ×1(표본)
09:41:09 2026-08-26 09:41:09 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×4(표본)
09:41:09 2026-08-26 09:41:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:44:09)
09:41:09 2026-08-26 09:41:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:44:09)
12:19:01 2026-08-26 12:19:01 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 12:21:01)
12:19:01 2026-08-26 12:19:01 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 12:21:01)
--- [SHAP] 슬로우 ×8(표본)
11:40:01 2026-08-26 11:40:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 937ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:10:02 2026-08-26 12:10:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1262ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:27:01 2026-08-26 12:27:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1180ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:38:01 2026-08-26 12:38:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1005ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:24 2026-08-26 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3328 band=INFO since_pipe_s=NA
09:00:08 2026-08-26 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8141 band=WARN since_pipe_s=0.2
09:05:04 2026-08-26 09:05:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4563ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4563 band=INFO since_pipe_s=0.1
09:37:02 2026-08-26 09:37:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2797ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2797 band=INFO since_pipe_s=0.0
```

### `logs/20260826_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-08-26 09:35:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:37:00 (const_output)
09:35:00 2026-08-26 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:35:00 2026-08-26 09:35:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=90ms fit=58ms total=150ms
09:36:00 2026-08-26 09:36:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- HALT ×1(표본)
15:40:22 2026-08-26 15:40:22 [INFO] SYSTEM: [CB③계측] 조건성립 64분 / 판정가능 152분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-08-26 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.058 level=0 (heartbeat)
09:05:00 2026-08-26 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.057 level=0 (heartbeat)
09:10:00 2026-08-26 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.056 level=0 (heartbeat)
09:15:00 2026-08-26 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.056 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:21 2026-08-26 15:40:21 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:21 2026-08-26 15:40:21 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:20 2026-08-26 15:11:20 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:23 2026-08-26 15:40:23 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:38 2026-08-26 15:40:38 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:23 2026-08-26 15:40:23 [INFO] SYSTEM: [Notify] ℹ️ [15:40:23] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:23 2026-08-26 15:40:23 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:38 2026-08-26 15:40:38 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260826_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:00:01 2026-08-26 09:00:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4550 (conf_floor=0.330, min_conf=0.455, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-08-26 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:36:00 2026-08-26 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:02 2026-08-26 09:37:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:29:00 2026-08-26 10:29:00 [WARNING] SIGNAL: [ConstOut] 5m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:00 2026-08-26 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=34.9% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-08-26 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-08-26 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.9% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-08-26 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.455
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.442
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.433
08:40:43 2026-08-26 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.429
--- 안전망 ×8(표본)
09:07:00 2026-08-26 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-08-26 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-08-26 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-08-26 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260826_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3131 < conf_floor=0.3300 (span=0.00111 auc=0.613 out_max=0.3131, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00082 auc=0.530 out_max=0.4460 (기준 auc<0.53 and span<0.020, 기저율=0.4455 n=110) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:41:04 2026-08-26 08:41:04 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00036 auc=0.509 out_max=0.3001 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:41:04 2026-08-26 08:41:04 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00084 auc=0.533 out_max=0.4505 (n=120) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260826_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:13 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 4 | 09:54:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=49,370,212) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:21 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260826_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 09:00:02 [WARNING] total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 09:00:02 [WARNING] total=1904ms | S0=4ms S1=14ms S2=0ms S3=0ms S4=101ms S5=1481ms S6=276ms S7=17ms S8=11ms |
| 10:00 | 장중 초반 | 2 | 09:59:00 [WARNING] 5분 누적 수익률 +0.280% (임계 ±0.262%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 15 | 11:54:07 [WARNING] _tick_header 간격 7718ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=7718 band=… |
| 14:00 | 장중 후반 · 장중 재학습 | 14 | 13:54:00 [WARNING] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\Pychar… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 9 | 15:04:01 [WARNING] settings.py 핫리로드 실패: cannot import name 'BROKER_CHANNEL_SPECS' from 'config.constants' (C:\Users\82108\Pychar… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:40:22 [WARNING] 브로커 net 미수신 — 대사 불가(0이 아니라 미측정). CpTd6197 예탁현금/익일가예탁현금 수신 여부를 확인할 것 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260826_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 86 | 08:40:46 [INFO] 활성화 | file=logs\crash_fault.log PID=18960 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 137 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 205 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 202 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 186 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 178 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 147 | 15:04:00 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 125 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 40 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260826_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 67 | 08:45:21 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 88 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0250) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 158 | 08:55:03 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0251) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 175 | 09:56:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=-1.986 need >0 (LONG) bear_exh=0.00 |
| 12:00 | 장중 중간점 | 168 | 11:54:00 [WARNING] 신뢰도 미달 34.3% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 148 | 13:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 98 | 15:04:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:21 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260825 | 15:40 | 로그 본문 |
| 20260824 | 15:40 | 로그 본문 |
| 20260821 | 15:40 | 로그 본문 |
| 20260820 | 21:17 | 로그 본문 |
| 20260819 | 17:02 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260826** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.4MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 이 정정이 남긴 교훈
## 2026-08-26 (MW0601 494차 후속 — 15:10, F-1′ 적용 완료)
### 확정된 괴리 — 실측
### 조치 1 — 앱 저장 스킬 교체 (`save_skill overwrite=true`)
### 조치 2 — 예약작업 3종 프롬프트에 `## 0. 시작 전` 블록 주입
### Why — 왜 프롬프트까지 이중으로 박았나
### 검증
### 남은 위험 (닫지 않았다)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
).

### 조치 1 — 앱 저장 스킬 교체 (`save_skill overwrite=true`)

`skill_01SuNm6mFhT7EVkSDBGDKLLq` · `updated_at 2026-08-26T06:09:46Z`.
정본 433줄을 기반으로 하되 **다음을 보강**했다:

- **머리말에 「이 문서는 사본이다 — 정본을 먼저 Read 하라」 경고 블록** (자기참조 방어)
- 함정 ①에 **2026-08-26 3회째 위반** 실측 추가 + *"Fix를 쓰기 전에 `grep`으로 실물 확인"*
- git 호출 규약에 **`git branch` 명시** + **샌드박스 `unlink` EPERM 실측**(회수 불가) 추가
- 자가점검 한계 명기 — *"수집기 **실행 전에** 세션이 친 명령이 만든 락은 «내가 안 만들었다»로
  정상 보고된다"* (오늘 실제로 그렇게 찍혔다)
- **`### 🔴 병행 세션 확인`** 신설 — 자기 절 쓰기 **전에** `git log --since=<오늘>` +
  `ls -lt docs/정기점검/매일점검/`. 0825 1-20 · 0826 4세션 병행 근거
- §5-0을 5규칙 완전형으로(§0 평문 강제 · `영향`/`영향(기술)` 둘 다 · 사용자 조치 3요소)
- §5-2에 「같은 국면 두 번 → `제2부-B`」 · 「한 PC가 다른 PC 절을 잇지 않는다」 추가
- §5-4에 **브로커 실측 net 판정 원천**(`fetch_daily_net_for_verdict()`) 명기
- §6에 **`git add .` 금지**(EOL 착시) · 예약은 커밋 안 함
- 실행지시 **9번 신설** — *"스킬을 고쳤으면 정본과 앱 스킬 **둘 다** 갱신한다"* (재발방지 본체)
- §7 체크리스트에 §0-①②③ 4줄 선두 배치

### 조치 2 — 예약작업 3종 프롬프트에 `## 0. 시작 전` 블록 주입

`mireuk-premarket-check` · `mireuk-intraday-check` · `mireuk-postmarket-check` **전부 갱신**.
**스킬이 또 낡아도 프롬프트가 정본을 강제**하는 이중화다(스킬 캐시는 우리가 통제 못 한다).

공통 3항목: ① 정본 Read 선행(경로 명시, *"다르면 정본이 이긴다"*) ② `--no-optional-locks`
전면 적용(예시 3줄) ③ 병행 세션 확인.
국면별 추가:
- **장전** — `--pc MW0601` 누락 경고 · `OPT50029`는 키움 전용이라 Cybos에선 해당 없음 ·
  **STEP3 "30분마다" 오독 금지**(483차 문서정정 — 0회가 정상인 날이 있다)
- **장중** — 위 + 이월 처리 **전에** 병행 확인 · 재학습 트리거 6종 명시
- **장후** — 위 + **제4·5부 누락 경고를 §0-①에 직접 박음** · 브로커 net 판정 원천 ·
  딥다이브 발견 시 **열어 읽고 역링크**(F-AE) · 산출 목차를 제4~7부로 재번호 ·
  코드정책에 *"스킬 고치면 두 곳 다"* 추가

### Why — 왜 프롬프트까지 이중으로 박았나

**함정 ①(이미 있는가 확인)을 막는 장치가 함정 ③(사본 괴리)에 의해 무력화됐다.**
두 함정이 곱해지면 개별 대책으로는 안 잡힌다. 스킬 캐시 갱신은 **우리가 시점을 통제할 수 없고**
(앱이 언제 다시 스냅샷을 뜨는지 모른다), 예약 프롬프트는 통제할 수 있다. ⇒ **통제 가능한 층에
정본 참조를 강제**한다.

### 검증

- [x] `save_skill` 응답 `updated_at 2026-08-26T06:09:46Z` 확인
- [x] 예약 3종 `updated: prompt` 응답 확인
- [ ] **O-8** (내일 08:57) 장전 세션의 첫 bash git 호출이 `git --no-optional-locks …` 인가 ·
      세션 종료 시 `.git/index.lock` **부재**
- [ ] **O-9** (다음 장중·장후) 자기 절 시작 전 당일 커밋·산출물 목록 확인을 **명시**하는가
- [ ] **O-10** 🔴 (다음 장후) `references/postmortem.md`를 열고 **제4부(승패 사후검증)·
      제5부(수익률 향상방안)** 를 실제로 붙이는가 — 6일간 누락됐을 수 있다

### 남은 위험 (닫지 않았다)

- **앱 스킬 캐시는 언제든 다시 낡을 수 있다.** 정본을 커밋해도 앱이 자동으로 따라오지 않는다.
  ⇒ **스킬 파일을 고칠 때마다 `save_skill overwrite=true` 를 같이 돌리는 것**이 유일한 동기화
  수단이며, 그 의무를 정본 §「실행을 요청받았을 때」 9번과 장후 프롬프트 코드정책에 박았다.
  **자동 검출 수단은 없다** — 정본 md5와 앱 사본 md5를 비교하는 계측을 만들 수는 있으나
  앱 사본 경로가 세션마다 바뀌어 안정적이지 않다. 우선 **관측(O-8)** 으로 대체한다.
- MW0602 쪽 앱 스킬은 **이 세션에서 손댈 수 없다**(PC별 저장). 그 PC에서 같은 조치가 필요하다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.2MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 494차 후속 관측 항목
### 고도화 (당일 관측 근거)
### 로드맵·실전전환 기준 반영 제안 (주간회의)
### 점검 규약 메모
### 커밋 대기 (오늘 커밋하지 않았다)
### MW0601 494차 정정 (2026-08-26 14:55)
### MW0601 494차 후속 (2026-08-26 15:10) — F-1′ 적용 완료
### MW0601 494차 후속2 (2026-08-26 15:30) — 커밋으로는 동기화가 안 된다 (실측 확정)
```

미완료 체크박스 **2039건** (끝에서 30건)
```
- [ ] **F-6 (P2)** `[ZeroDiag] 진입X 원인` 문자열이 `actual_min_conf`(전 게이트 적용 후)를
- [ ] **F-7 (P2)** `_run_effect_report_script` 장중 회피 또는 비블로킹화.
- [ ] `tests/test_496_zone_entry_hard_gate.py` 신설 (F-4 도달성 불변식,
- [ ] **O-8** 🆕 점심 블랙아웃(11:50~13:00) 진입 **9건 / 6일**(08-03 3 · 08-04 1 · 08-05 2 ·
- [ ] **O-9** 🆕 1-5 — 종가까지 `[HealthPolicy] … 핫리로드 실패` 총 건수 · 재기동 후 첫
- [ ] **O-10** 🆕 1-7 — 15:10까지 재학습 총 횟수 대비 `Degraded 선제차단` 동반 비율
- [ ] **O-11** 🆕 절대원칙 §1 — 종가 포지션 보유 시 `[ForceExitPass]`→`[TimeExit]`→
- [ ] (승계) **O-3** 내일 장전 · **O-4·O-5·O-6·O-7** 장후
- [ ] **G-3** 「선언-실효 대조」 정기 점검 신설 — 정책 딕셔너리 불리언 키의 소비처를 세어
- [ ] **G-4** `TIME_ZONES` 미정의 공백(11:50~13:00) 제거 — ① `LUNCH_BLACKOUT` 명시 존
- [ ] **G-5** `dev`의 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` 이식 여부 → 주간회의.
- [ ] 실전 전환 기준 ②에 **「차단 게이트가 선언대로 실제로 차단하는가」** 축 추가 검토
- [ ] 26주 WFA 주기 항목에 **G-3** 편입 검토
- [ ] `dev`→`v9-dev` 이식 안건 2건: `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` · `ZONE_ENTRY_BAN_*`.
- [ ] (승계, 최우선) **CB② 복원 재검토 기한 2026-08-29(토) → 마지막 거래일 08-28(금)**
- [ ] 🔴 **F-1′** (P2 · **선행순서는 F-2·F-3보다 앞**) 예약 실행 로드 SKILL.md 사본 ↔ repo 원본
- [ ] ⚠ **F-3 설계 변경** — `5c54496`(12:24:59)이 `FUTURES_COMMISSION_RATE`를
- [ ] **F-AE′** (P2, 기존 F-AE에 흡수) 뒤 국면이 자기 절 시작 **전에**
- [ ] **O-8** (내일 장전) 예약 실행 첫 bash git 호출이 `git --no-optional-locks …` 인가
- [ ] **O-9** (장후) 장후 세션이 자기 절 시작 전 당일 커밋·당일 산출물 목록 확인을 명시하는가
- [ ] **장후 숙제** `MW0601-20260826-청산로그갭-딥다이브.md`(11.7KB, 11:58) **내용 열람 후**
- [ ] **O-8** (내일 08:57) 장전 첫 bash git 호출이 `git --no-optional-locks …` 인가 ·
- [ ] **O-9** (다음 장중·장후) 자기 절 시작 전 **당일 커밋·산출물 목록 확인**을 명시하는가
- [ ] 🔴 **O-10** (다음 장후) `references/postmortem.md`를 열고 **제4부 승패 사후검증 ·
- [ ] **MW0602 동일 조치 필요** — 앱 저장 스킬은 PC별이라 이 세션에서 손댈 수 없다.
- [ ] **(설계) 정본↔앱 사본 드리프트 자동 검출** — 정본 md5와 앱 사본 md5 비교.
- [ ] 🔴 **사용자 조치** `outputs/mireuk_skill_sync_20260826/SKILL.md` →
- [ ] 🔴 **사용자 조치** `README_MW0602에게.md` + `SKILL.md` 를 MW0602 로 전달 →
- [ ] **MW0602 회신 확인 항목** — ① `dev` 브랜치에 `scripts/git_lock_guard.py` 가 있는가
- [ ] **(설계) `rev:` 대조를 세션 절차로 승격** — 정본 첫 줄 `<!-- rev: YYYY-MM-DD -->` 와
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
명시하는가
- [ ] 🔴 **O-10** (다음 장후) `references/postmortem.md`를 열고 **제4부 승패 사후검증 ·
      제5부 수익률 향상방안**을 실제로 붙이는가 — **6일간 누락됐을 수 있다.**
      누락 확인되면 그 기간(2026-08-20~26) 장후 리포트를 소급 보완 대상으로 등록
- [ ] **MW0602 동일 조치 필요** — 앱 저장 스킬은 PC별이라 이 세션에서 손댈 수 없다.
      그 PC 세션에서 `save_skill overwrite=true` + 예약 3종 프롬프트 갱신
- [ ] **(설계) 정본↔앱 사본 드리프트 자동 검출** — 정본 md5와 앱 사본 md5 비교.
      ⚠ 앱 사본 경로가 세션마다 바뀌어 안정적이지 않다 → 우선 O-8 관측으로 대체.
      대안: 정본 첫 줄에 `<!-- rev: YYYY-MM-DD -->` 를 박고 세션이 사본의 rev와 대조

### MW0601 494차 후속2 (2026-08-26 15:30) — 커밋으로는 동기화가 안 된다 (실측 확정)

**사용자 질문**: *"커밋대기를 커밋해야 그 PC에서 동기화할 수 있는 것 아닌가"* → **아니다.**

**실측 근거 (2026-08-26)**

```
git rev-list --count origin/dev ^HEAD   = 397   (dev 가 v9-dev 대비 앞선 커밋)
git rev-list --count HEAD ^origin/dev   = 383   (v9-dev 가 dev 대비 앞선 커밋)

.claude/skills/mireuk-daily-check/SKILL.md
  v9-dev : 433줄 · 2026-08-24 · 91c6120
  dev    : 378줄 · 2026-08-20 · 062fd84   ← MW0602 가 pull 해도 이걸 받는다
```

두 이유로 커밋이 해결책이 아니다:
① **브랜치 분기** — MW0601 커밋은 `v9-dev` 로 가고 MW0602 는 `dev` 를 pull한다.
② **앱 저장 스킬·예약작업은 git 대상이 아니다** — 계정/PC별 저장.

⇒ **파일 직접 전달만이 방법이다.**

**산출물 (outputs 폴더)** `mireuk_skill_sync_20260826/`
- `SKILL.md` — 새 지침서 정본 후보. `<!-- rev: 2026-08-26 -->` 표기.
  **PC 중립화**: `--pc MW0602` 예시 · `MW0602 46X차` 헤더 예시 · `v9-dev` 전용 산물
  (`postmortem.md` · `fetch_daily_net_for_verdict()` · `commission_rate_used` ·
  `git_lock_guard.py`)에는 **"자기 브랜치에 있는지 확인하고 없으면 없다고 리포트에 적어라"**
  단서 부착
- `README_MW0602에게.md` — 배경·근거·3단계 절차·예약 프롬프트 §0 블록 전문

**MW0601 저장소 정본은 아직 미갱신** — `.claude/` 경로가 도구 정책상 보호돼 세션이 직접
쓰지 못한다(`Write ... is blocked — protected location`). **사용자 수동 복사 필요.**

- [ ] 🔴 **사용자 조치** `outputs/mireuk_skill_sync_20260826/SKILL.md` →
      `C:\Users\82108\PycharmProjects\futures\.claude\skills\mireuk-daily-check\SKILL.md` 복사
      (덮어쓰기). 그래야 `v9-dev` 정본이 앱 스킬과 같은 세대가 된다.
      ⚠ **복사 전 백업**: `SKILL.md.bak_494`
      ⚠ 복사 후 `head -5` 로 `<!-- rev: 2026-08-26 -->` 확인
- [ ] 🔴 **사용자 조치** `README_MW0602에게.md` + `SKILL.md` 를 MW0602 로 전달 →
      그 PC 세션에 "이대로 진행해"
- [ ] **MW0602 회신 확인 항목** — ① `dev` 브랜치에 `scripts/git_lock_guard.py` 가 있는가
      ② `collect_evidence.py` 에 `--no-optional-locks` 배선이 있는가
      ③ `references/postmortem.md` 가 있는가.
      **셋 다 `v9-dev` 기준 산물이라 `dev` 에는 없을 수 있다** — 없으면 그 브랜치의
      점검은 해당 절차를 쓸 수 없으므로, **이식 여부를 주간회의 안건**으로 올린다
- [ ] **(설계) `rev:` 대조를 세션 절차로 승격** — 정본 첫 줄 `<!-- rev: YYYY-MM-DD -->` 와
      로드된 사본의 `rev` 를 비교. 자동 검출 수단이 없으므로 이것이 유일한 저비용 탐지다.
      예약 프롬프트 §0-① 에 이미 문구는 넣었고, **수집기 §2 에 「스킬 rev」 1줄 추가**를 검토

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

### `data/heartbeat_MW0601_20260826.json` — 242B · 08-26 15:40:34
```json
{
 "pid": 18960,
 "written_at": "2026-08-26T15:40:34",
 "beat_epoch": 1787726430.78691,
 "beat_age_sec": 4.1,
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

### `docs/정기점검/매일점검` — 77개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260826-점검리포트.md` | 112.7KB | 08-26 15:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_intra.md` | 64.8KB | 08-26 12:27 |
| `docs/정기점검/매일점검/MW0601-20260826-청산로그갭-딥다이브.md` | 11.4KB | 08-26 11:58 |
| `docs/정기점검/매일점검/evidence_MW0601-20260826_pre.md` | 52.3KB | 08-26 09:00 |
| `docs/정기점검/매일점검/MW0601-20260825-점검리포트.md` | 301.3KB | 08-25 22:33 |
| `docs/정기점검/매일점검/MW0601-20260825-브로커손익불일치-딥다이브.md` | 25.8KB | 08-25 21:52 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_post.md` | 70.9KB | 08-25 16:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20260825_intra.md` | 61.7KB | 08-25 12:26 |

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

1. `logs/20260826_WARN.log`: **Traceback** 출현 8건 — 크래시/메모리 계열
2. 포지션 2건 중 최종청산이 하드스톱·손절 계열 **1건(50%)** — 손절 준수율 확인 필요 (레그 4행)
3. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. 메인 스레드 정지 5초 초과 **8건** (최대 8141ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20260826_WARN.log`: **[Brier] 과신** 1건(표본)
7. `logs/20260826_WARN.log`: **ConstOut** 5건(표본)
8. `logs/20260826_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20260826_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260826_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260826_LEARNING.log`: **축퇴** 8건(표본)
12. 미커밋 변경 520건 (실질 3건 · 코드 0건 · EOL 파생 510건)
13. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260826*.log` (Windows) / `grep 강제청산 logs/*20260826*.log`*