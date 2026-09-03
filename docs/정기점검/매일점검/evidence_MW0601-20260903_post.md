# 미륵이 증거 다이제스트 — 2026-09-03 / POST

- 생성 2026-09-03 16:18:10 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/focused-inspiring-goodall/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260903` · `2026-09-03` · `260903` · `0903`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **27개** 파일 · 27개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260903.txt` | 28B | 09-03 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260903.txt` | 28B | 09-03 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260903.txt` | 209B | 09-03 15:49 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260903.log` | 1.4KB | 09-03 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260903.log` | 217B | 09-03 15:45 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260903.json` | 244B | 09-03 15:40 |
| `launcher_{DATE}_084001_27535.log` | 1 | `logs/Mireuk_batch/launcher_20260903_084001_27535.log` | 1.6MB | 09-03 15:40 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260903.log` | 13.1KB | 09-03 12:33 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260903.log` | 19.6KB | 09-03 15:49 |
| `retrain_intraday_{DATE}_123901.log` | 1 | `logs/retrain_intraday_20260903_123901.log` | 2.7KB | 09-03 12:39 |
| `retrain_intraday_{DATE}_131800.log` | 1 | `logs/retrain_intraday_20260903_131800.log` | 2.7KB | 09-03 13:18 |
| `retrain_intraday_{DATE}_140101.log` | 1 | `logs/retrain_intraday_20260903_140101.log` | 2.7KB | 09-03 14:01 |
| `retrain_intraday_{DATE}_143600.log` | 1 | `logs/retrain_intraday_20260903_143600.log` | 2.7KB | 09-03 14:36 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260903.txt` | 43B | 09-03 15:40 |
| `strategy_report_20260508_18{DATE}.txt` | 1 | `data/daily_reports/strategy_report_20260508_180903.txt` | 708B | 05-08 18:09 |
| `strategy_report_{DATE}_154007.txt` | 1 | `data/daily_reports/strategy_report_20260903_154007.txt` | 2.5KB | 09-03 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260903_DATA.log` | 343.1KB | 09-03 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260903_DEBUG.log` | 235.2KB | 09-03 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260903_HEALTH.log` | 3.8KB | 09-03 14:38 |
| `{DATE}_HOGA.log` | 1 | `logs/20260903_HOGA.log` | 51.9MB | 09-03 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260903_LEARNING.log` | 290.1KB | 09-03 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260903_MICRO.log` | 1.0MB | 09-03 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260903_PROBE.log` | 96.5KB | 09-03 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260903_SIGNAL.log` | 526.8KB | 09-03 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260903_SYSTEM.log` | 871.4KB | 09-03 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260903_TRADE.log` | 21.9KB | 09-03 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260903_WARN.log` | 97.5KB | 09-03 15:40 |

## 2. 코드·커밋 상태

- HEAD `8997136` · 브랜치 `v9-dev` · 미커밋 520건 · 실질 변경 2건 · 코드(.py) 0건 · EOL 파생 515건 (추적변경 517 · 미추적 3 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
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
 M .claude/skills/mireuk-daily-check/scripts/collect_evidence.py
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

**당일(2026-09-03) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
8997136 [MW0601] 519차 기록: DECISION_LOG · NEXT_TODO · 리포트 제5부
d03b629 [MW0601] 519차: CB② 복원 · 메인스레드 정지 경보 · F-1 마감 잔여 자동청산 (사용자 지시)
7338611 [MW0601] 518차 후속: 장후 자동조치 — F-3(진입출처 라벨) · G-1(재기동 잔량 경보 문구) · G-4(이월손익 가시화)
a3f70ab [MW0601] 514차 후속: 장후 자동조치 — F-A(P1-3) · F-B(고도화①) · F-C(고도화②/P5-신규)
3f5781c [MW0601] dev_memory: 512차 체리픽(ProfitGuard 패널 입력 격자) 검증 기록
e5b7bcf [MW0602] 512차: 수익 보존 가드 파라미터 입력 격자 재설정 (10만원 / 5% / 1 단위)
a06cd05 [MW0601] 511차: 청산 주문 브로커 거부 대응 — 실패 가시화 + 재시도 백오프 (P0)
c5eddda [MW0601] 508차: F-6 배포 — Restart Armistice 고착 해소 (2026-08-31 자동진입 0건)
db48586 [MW0601] 507차 후속: 리포트 제8부에 커밋 해시 기입
2d6a1bb [MW0601] 507차 후속: 장후 자동조치 — F-7·F-8·F-11·F-12·F-14 + G-4·G-5
f01080b [MW0601] 문서: MW0602 장후 자동조치 예약작업 설치 지침 (mireuk-postmarket-autofix)
da120b1 [MW0601] 점검 프롬프트: 8월 10만원 이상 손실일 딥다이브 지시 추가
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
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

### 차단 게이트 전수 인벤토리 — 34개 중 **9개 꺼짐**

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
| `DAILY_CLOSE_FORCE_EXIT_ENABLED` | True | — |
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

_본문 미열람(설정): `20260903_HOGA.log` 51.9MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260903.txt`** — 28B · 09-03 15:40:07
```
2026-09-03T15:40:07.374271
```

**`data/daily_close_started_20260903.txt`** — 28B · 09-03 15:40:05
```
2026-09-03T15:40:05.710724
```

**`data/daily_reports/strategy_report_20260508_180903.txt`** — 708B · 05-08 18:09:03
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-05-08 18:09
========================================================
  버전    : v1.2  (1일차)
  판정    : INSUFFICIENT
  롤링20일: 누적 +0원  Sh=0.00  MDD=0.0%
--------------------------------------------------------
  CUSUM   : CRITICAL (1618766.50)
  PSI     : 0.000 (CLEAR)
  PSI/feat: cvd=0.000  vwap_position=0.000  ofi=0.000
--------------------------------------------------------
  권고    : ⛔ 롤백 검토
  사유    : CUSUM CRITICAL — 성과 6σ 이탈. 롤백 검토 및 사이즈 50%% 축소 필요.
========================================================
```

**`data/daily_reports/strategy_report_20260903_154007.txt`** — 2.5KB · 09-03 15:40:07
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-03 15:40
========================================================
  버전    : v1.0  (72일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-4.52  MDD(자본대비)=26.9%
  당일      : WR=57.1%  PF=0.51
  롤링20일: 누적 -10741212원  Sh=-4.52  MDD(자본대비)=26.9%  MDD(peak대비)=498.4%
  당일손익 : broker(gross) -63,000원  수수료 102,617원  net -165,617원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.005 (CLEAR)
  PSI/feat: cvd_delta=0.005  ofi_pressure=0.001  vwap_position=0.072
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -511,821원  승률 55.0%  합계 -10,236,414원
  등급별 순EV(30일): A=+8,045원(135건,승67%)  BROKER=-5,380,798원(2건,승0%)  C=+9,768원(23건,승78%)  MANUAL=-18,904원(91건,승45%)
  호라이즌별 순EV(30일): 1m=+12,001원(24건)  3m=-2,323원(108건)  5m=+44,423원(24건)  ?=-129,205원(95건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 72분  5일평균 26분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 41.2pt(5일평균 27.4pt)  1분평균변동 0.76pt(5일평균 0.81pt)
--------------------------------------------------------
  진입 퍼널(2026-09-03, 총 370분):
    FLAT 228 → conf미달 66 → CoherenceGate 7 → 게이트차단 59 → 후보 10 → 진입 7
    └ 등급상향경로(앙상블X→체크리스트통과): 2건 [285차-P5]
    게이트별: 체크리스트항목미달=23  쿨다운=9  콜드스타트/기타(RegimeOverride)=9  포지션보유중(평가생략)=8  ATR변동성=4  모드필터=3  마감시간(신규진입금지)=3
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 3건
      └ 상세: JointGateBlock=3
      └ JointGateBlock 3건 (무정보폴백 3건 = 100.0%) [표본 17건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260903.txt`** — 209B · 09-03 15:49:08
```
completed: 2026-09-03 15:49:08
rows: 40788
cols: 97
horizons_replaced: 6/6
t_load_s: 42.8
t_retrain_s: 200.8
t_total_s: 244.1
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260903.txt`** — 43B · 09-03 15:40:22
```
auto_shutdown
2026-09-03T15:40:22.376071
```

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20260903_123901.log`, `retrain_intraday_20260903_131800.log`, `retrain_intraday_20260903_140101.log`, `20260903_MICRO.log`, `20260903_DATA.log`, `20260903_PROBE.log`, `launcher_20260903_084001_27535.log`, `20260903_DEBUG.log`_

### `logs/20260903_TRADE.log` — 21.9KB · 157행 · 최종 15:40:06

- 형식 평문 · 시각 인식 157행 · INFO=157

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-03 08:41:03 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-03 10:02:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,600,786) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-03 10:02:01 [INFO] TRADE: [모드필터 차단] LONG->LONG 2계약 C급 (모드=hybrid, 허용=['A', 'B'])
2026-09-03 10:03:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,600,786) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-09-03 13:36:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.2→3계약]
2026-09-03 14:53:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdvisedSkip]
2026-09-03 14:54:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdvisedSkip]
2026-09-03 14:59:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdvisedSkip]
2026-09-03 15:40:06 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×157

**컴포넌트 상위 15** — `Chejan`×37, `Position`×29, `Sizer`×28, `주문요청`×17, `진입체크`×7, `체결진입`×7, `청산 완료`×7, `TickStop-S0C`×6, `TickTP1`×5, `모드필터 차단`×3, `체결진입보정`×3, `JointGateBlock 차단`×3, `ProfitGuard`×2, `손절1차 조기축소`×2, `TP1 부분청산`×1

### `logs/20260903_WARN.log` — 97.5KB · 439행 · 최종 15:40:06

- 형식 평문 · 시각 인식 432행 · WARNING=432, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-09-03 08:41:06 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 172ms account=333044256
2026-09-03 08:41:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
2026-09-03 08:41:12 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3343ms — live 중단 원인 분석용
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -165617원
════════════════════════════════════════════════════
```

</details>

**WARNING — 태그 35종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 116 | 08:41:06 | 14:46:01 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 37 | 10:03:01 | 11:31:19 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1384' | pending='ENTRY:LONG qty=2 filled=0 order_no=? reason=진입 req_at=10:03:01.118' | positio… |
| `ChejanMatch` | 37 | 10:03:01 | 11:31:19 | order_no='1384' | pending='ENTRY:LONG qty=2 filled=0 order_no=1384 reason=진입 req_at=10:03:01.118' | pending_matched=True |
| `PendingOrder` | 34 | 10:03:01 | 11:31:19 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1044.72, 'reason': '진입', 'hint_source': '', 'atr': 1.3571, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `ScalerRefresh` | 16 | 09:10:00 | 14:51:00 | 5분 누적 수익률 -0.362% (임계 ±0.251%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 14 | 09:00:01 | 14:37:03 | level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0 |
| `ExitCooldown` | 14 | 10:05:27 | 11:31:19 | 하드스톱(틱) 후 2분 재진입 금지 (until 10:07:27) |
| `CB` | 13 | 10:03:20 | 14:44:00 | 연속 손절 1회 (300초 창, 포지션 단위) |
| `PipePerf` | 12 | 09:00:01 | 14:37:03 | total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |
| `CB⑤` | 12 | 09:00:02 | 14:37:03 | 파이프라인 1486ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `EntryFillFlow` | 10 | 10:03:01 | 11:30:02 | actual_side='LONG' | after='LONG 2계약 @ 1044.64' | applied_side='LONG' | before='LONG 2계약 @ 1044.72' | fill_no='' | fill_price=1044.64 | fill_qty=1 | order_no='1384' | pending='ENTRY:LONG qty=2 filled=1 order_no=1384 reason=진입 req_at=10:03:… |
| `ExitSendOrderResult` | 8 | 10:03:20 | 11:31:18 | ret=0 kind=손절1차 direction=LONG qty=1 |

**채널** — `SYSTEM`×418, `HEALTH`×14

**컴포넌트 상위 15** — `LiveDBG`×116, `ChejanFlow`×37, `ChejanMatch`×37, `PendingOrder`×34, `ScalerRefresh`×16, `Health`×14, `ExitCooldown`×14, `CB`×13, `PipePerf`×12, `CB⑤`×12, `EntryFillFlow`×10, `ExitSendOrderResult`×8, `CB③-P4`×8, `EntryAttempt`×7, `EntrySendOrderResult`×7

### `logs/20260903_SYSTEM.log` — 871.4KB · 6183행 · 최종 15:40:22

- 형식 평문 · 시각 인식 6152행 · INFO=6152, PLAIN=31

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:32 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21356 | 행감지=30s all_threads=True
2026-09-03 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료
2026-09-03 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-03 08:40:48 [INFO] SYSTEM: 미륵이 초기화
2026-09-03 08:40:48 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-09-02) 종가 버퍼 로드: 384봉
  …
2026-09-03 15:40:07 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-09-03 15:40:07 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-09-03 15:40:22 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-03 15:40:22 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-03 15:40:22 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×6152

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1394, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `System`×98, `BalanceUI`×76, `CybosEvent`×74, `RegimeFingerprint`×68, `MicroRegime`×68, `BalanceRefresh`×56, `CybosDailyPnl`×52

### `logs/20260903_SIGNAL.log` — 526.8KB · 4656행 · 최종 15:40:06

- 형식 평문 · 시각 인식 4656행 · WARNING=1791, INFO=2865

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.418
  …
2026-09-03 15:10:29 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-03 15:40:06 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-03 15:40:06 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 136분(36.8%) / DN 20분(5.4%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-03 15:40:06 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-03 age=28m extreme=1331 refresh=39 grade_x=80 cb3=0
2026-09-03 15:40:06 [INFO] SIGNAL: [ModelHealth] date=2026-09-03 앙상블유효가동률=77.0% | 파이프라인 370분 | ConstOut 5회/7분 {"3m": {"events": 4, "minutes": 6}, "15m": {"events": 1, "minutes": 1}} | WeightCollapse 78분 | 장중재학습 4회 | CB③ ready 103분/370분 (28%) (리셋 2회, 표본손실 60건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1302 | 09:00:02 | 14:51:01 | 1m 'macro_vix' scale=0.0251 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 126 | 08:45:06 | 14:51:01 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Checklist` | 97 | 09:06:00 | 15:06:01 | 신뢰도 미달 34.9% < 38.0% → 강제 X등급 |
| `ScalerMonitor` | 96 | 09:00:00 | 14:51:00 | ts=08:59 horizon=1m age=1m max_z=-15.19(institution_futures_net) extreme=1 |
| `Model` | 84 | 09:00:00 | 14:51:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `WeightCollapse` | 78 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 6 | 12:30:00 | 14:35:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 2 | 09:00:00 | 11:38:01 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4656

**컴포넌트 상위 15** — `ScalerFloor`×1326, `SIGNAL`×740, `Ensemble`×387, `FQAdj`×357, `ZeroDiag`×311, `MetaGate`×288, `Checklist`×171, `ScalerRefresh`×170, `ATR-Horizon`×118, `Model`×114, `ScalerMonitor`×97, `차단`×82, `WeightCollapse`×78, `MicroRegime`×68, `InstabilityGate`×54

### `logs/20260903_LEARNING.log` — 290.1KB · 2857행 · 최종 15:40:06

- 형식 평문 · 시각 인식 2857행 · WARNING=149, INFO=2708

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 08:40:49 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3009 < conf_floor=0.3300 (span=0.00172 auc=0.604 out_max=0.3009, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-03 08:40:49 [INFO] LEARNING: [Calibration] 도달불가 해소 — out_max=0.3464 < conf_floor=0.3300 (n=90) → 보정 재적용
2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00081 auc=0.459 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
  …
2026-09-03 15:40:06 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-03 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-03 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-03 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-03 15:40:06 [INFO] LEARNING: [Sigma] EOD sigma_20=0.10116% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 148 | 08:40:49 | 13:38:00 | 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `DriftAdjuster` | 1 | 15:40:06 | 15:40:06 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 6일) |

**채널** — `LEARNING`×2857

**컴포넌트 상위 15** — `LEARNING`×1200, `SGD`×370, `sigma`×357, `Calibration`×289, `Bias⚠`×264, `Bias`×118, `MetaConf`×76, `OnlineLearner`×74, `ScalerWarmup`×44, `BiasReset`×20, `SHAP`×11, `GBM-64`×8, `GBM`×8, `RF`×5, `ExtremityCorrector`×5

### `logs/20260903_HEALTH.log` — 3.8KB · 28행 · 최종 14:38:00

- 형식 평문 · 시각 인식 28행 · WARNING=14, INFO=14

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0
2026-09-03 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=408ms | quality=0.86 | cache_age=107s | exceptions_10m=0
2026-09-03 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 281ms (표본 20분)
2026-09-03 09:39:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=322ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-03 09:40:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=294ms | quality=1.00 | cache_age=58s | exceptions_10m=0
  …
2026-09-03 14:02:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3067ms | quality=1.00 | cache_age=165s | exceptions_10m=1
2026-09-03 14:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=359ms | quality=1.00 | cache_age=38s | exceptions_10m=1
2026-09-03 14:36:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=450ms | quality=1.00 | cache_age=182s | exceptions_10m=2 [GBM재학습중→lat임계 5000/10000ms]
2026-09-03 14:37:03 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3257ms | quality=1.00 | cache_age=61s | exceptions_10m=3
2026-09-03 14:38:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=392ms | quality=1.00 | cache_age=118s | exceptions_10m=3
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 14 | 09:00:01 | 14:37:03 | level=WARNING degraded=OFF | latency=1486ms | quality=0.86 | cache_age=48s | exceptions_10m=0 |

**채널** — `HEALTH`×28

**컴포넌트 상위 15** — `Health`×27, `HealthTrend`×1

### `logs/retrain_eod_20260903.log` — 19.6KB · 131행 · 최종 15:49:09

- 형식 평문 · 시각 인식 131행 · WARNING=16, INFO=115

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 15:45:04,478 [INFO] EOD_RETRAIN: =======================================================
2026-09-03 15:45:04,479 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-03 15:45:04,479 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-03 15:45:04,480 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-03 15:45:04,480 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-03 15:49:09,160 [INFO] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4386 → floor=0.50 적용 (z-score 폭발 방지)
2026-09-03 15:49:09,161 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0370 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-03 15:49:09,163 [INFO] SIGNAL: [ScalerRefresh] ts=15:49 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-09-03 15:49:09,169 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-03 15:49:09,170 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:55 | 15:47:54 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1500봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-02 14:38:00 ≥ 홀드아웃 시작=2026-08-27 13:00:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-02 14:38 >= holdout_start=2026-08-27 13:00 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-02 … |
| `ScalerRefresh` | 6 | 15:49:09 | 15:49:09 | 1m CORE 'ofi_norm' raw_std≈0(0.0436) → identity(0,1) 강제 (FLAT 100% 방지) |
| `GuardGhost` | 4 | 15:46:06 | 15:47:29 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-03 13:30:00까지)인데 acc.txt=0.3674는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×66, `SIGNAL`×37, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×24, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `ScalerRefresh`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `GuardGhost`×4, `RegimeFingerprint`×3, `WaitDC`×2

### `logs/retrain_intraday_20260903_143600.log` — 2.7KB · 21행 · 최종 14:36:23

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-03 14:36:00,646 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-03 14:36:00,646 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-03 14:36:00,646 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-03 14:36:00,646 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['15m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_75d658c0.json
2026-09-03 14:36:03,542 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-03 14:36:23,133 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-03 14:36:23,134 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-03 14:36:23,134 [INFO] LEARNING: [Retrain] 완료 | 19.6초 | 성공=1/1 호라이즌
2026-09-03 14:36:23,135 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.5s 데이터=4800행
2026-09-03 14:36:23,136 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_75d658c0.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -165617원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 7 |
| 진입 등록(`[Position] 진입`) — **엔진** | 7 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 7 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 7 |
| 차단(`[차단]`) | 82 |
| 사이저 호출(`[Sizer]`) | 28 |

### 포지션 7건 · 승 3 (43%) · 합계 -1.26pt (-165,617원)  ※ 레그 10행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:03:01 | 엔진 | LONG | 2 | 3m | 2 | -0.54 | -47,496 | 하드스톱(틱) |
| 10:24:00 | 엔진 | LONG | 2 | 3m | 2 | -2.96 | -168,566 | 하드스톱(틱) |
| 10:33:00 | 엔진 | LONG | 2 | 3m | 2 | +3.62 | +160,424 | TP2(전량) |
| 11:02:00 | 엔진 | SHORT | 1 | 3m | 1 | -2.08 | -114,209 | 하드스톱(틱) |
| 11:18:00 | 엔진 | LONG | 1 | 3m | 1 | +0.18 | -1,260 | 하드스톱(틱) |
| 11:25:01 | 엔진 | LONG | 1 | 1m | 1 | +0.28 | +3,751 | 하드스톱(틱) |
| 11:30:01 | 엔진 | LONG | 1 | 1m | 1 | +0.24 | +1,739 | 하드스톱(틱) |

**청산 레그 10행** (부분청산 3 · 전량청산 7)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:03:20 | 부분 | 1 | -0.81 | -50,748 | 손절1차 조기축소 |
| 10:05:27 | 전량 | 1 | +0.27 | +3,252 | 하드스톱(틱) |
| 10:24:10 | 부분 | 1 | -0.93 | -56,783 | 손절1차 조기축소 |
| 10:25:09 | 전량 | 1 | -2.03 | -111,783 | 하드스톱(틱) |
| 10:33:16 | 부분 | 1 | +0.93 | +36,212 | TP1 부분청산 33% |
| 10:35:04 | 전량 | 1 | +2.69 | +124,212 | TP2(전량) |
| 11:07:51 | 전량 | 1 | -2.08 | -114,209 | 하드스톱(틱) |
| 11:19:06 | 전량 | 1 | +0.18 | -1,260 | 하드스톱(틱) |
| 11:27:15 | 전량 | 1 | +0.28 | +3,751 | 하드스톱(틱) |
| 11:31:19 | 전량 | 1 | +0.24 | +1,739 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×6, `손절1차 조기축소`×2, `TP1 부분청산 33%`×1, `TP2(전량)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 6/7건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -165,617 = 포지션합 -165,617 → OK · `[청산 완료]` 7건 = 조립 포지션 7건 → OK

### CB③ 판정 가능 시간 — **103분 / 370분 (28%)**

acc30m 버퍼 리셋 2회 · 그때 버린 표본 60건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 7건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:03:01 | LONG | 2 | 1044.72 | 3m | neutral |
| 10:24:00 | LONG | 2 | 1048.3 | 3m | neutral |
| 10:33:00 | LONG | 2 | 1048.66 | 3m | neutral |
| 11:02:00 | SHORT | 1 | 1040.74 | 3m | neutral |
| 11:18:00 | LONG | 1 | 1045.64 | 3m | neutral |
| 11:25:01 | LONG | 1 | 1044.88 | 1m | neutral |
| 11:30:01 | LONG | 1 | 1046.08 | 1m | neutral |

계약수 분포 — 1계약×4, 2계약×3

등급 분포 — `A급(원시C)`×6, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×6, `chas`×2, `prev`×1, `ofi`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×17, **2계약**×3, **3계약**×8

실제 진입 계약수 — **1계약**×4, **2계약**×3

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×28

### 차단 사유 82건 · 48종

| 건수 | 사유 |
|---|---|
| 9 | 등급X — 미통과 항목: 2_confidence |
| 6 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 4 | 등급X — 미통과 항목: 3_vwap |
| 4 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 3 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 3 | ATR 0.84pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 3 | ATR 0.75pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi |
| 2 | 등급X — 미통과 항목: 3_vwap, 10_chase |
| 2 | ATR 0.87pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.7pt > ATR×5.0=7.9pt (시가=1045.56 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.8pt > ATR×5.0=7.5pt (시가=1045.56 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=7.8pt (시가=1045.56 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.6pt > ATR×5.0=8.2pt (시가=1045.56 반등위험) |
| 1 | 청산 후 쿨다운 — 86초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 128초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 63초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `3_vwap`×22, `4_cvd`×13, `7_prev_bar`×13, `5_ofi`×12, `2_confidence`×9, `10_chase`×2, `6_foreign`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 26건

- `일시 정지 해제 — 정상 복귀` ×10
- `3분 진입 정지 | ATR 2.2배 지속 급등 (중앙값, 버퍼=30)` ×8
- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `3분 진입 정지 | ATR 2.1배 지속 급등 (중앙값, 버퍼=30)` ×2
- `일간 리셋 완료` ×2
- `같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-03 10:24:01, 현재 1…` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 27건 · 최대 8734ms · 5초 초과 5건

상위 — 8734ms, 5578ms, 5141ms, 5140ms, 5015ms, 4672ms, 4641ms, 4563ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:00:08 | 8734ms | 1486ms | **7248ms (83%)** |
| 11:34:06 | 5015ms | 1835ms | **3180ms (63%)** |
| 11:35:04 | 5140ms | 1835ms | **3305ms (64%)** |
| 12:30:04 | 5141ms | 398ms | **4743ms (92%)** |
| 12:33:05 | 5578ms | 711ms | **4867ms (87%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260903_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:06 2026-09-03 15:40:06 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 26분/일 < 하한 60분 — 금일 72분. | ConfFloorGuard 도달가능 111분 · 도달불가 59분 · 재지않음 200분
--- ConstOut ×4(표본)
12:38:00 2026-09-03 12:38:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
13:17:01 2026-09-03 13:17:01 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
14:00:00 2026-09-03 14:00:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
14:35:00 2026-09-03 14:35:00 [WARNING] SYSTEM: [ConstOut] ['15m'] 상수 출력 확정 → 스케일러 재적합 시작
--- Traceback ×4(표본)
09:00:08 2026-09-03 09:00:08 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20260903.log
11:34:06 2026-09-03 11:34:06 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20260903.log
12:30:04 2026-09-03 12:30:04 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (3/20) → logs/mainstall_traceback_20260903.log
12:33:05 2026-09-03 12:33:05 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (4/20) → logs/mainstall_traceback_20260903.log
--- [CB] ×8(표본)
10:03:20 2026-09-03 10:03:20 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:24:10 2026-09-03 10:24:10 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
11:07:51 2026-09-03 11:07:51 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
14:29:00 2026-09-03 14:29:00 [WARNING] SYSTEM: [CB] 3분 진입 정지 | ATR 2.1배 지속 급등 (중앙값, 버퍼=30)
--- [ExitCooldown] ×8(표본)
10:05:27 2026-09-03 10:05:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:07:27)
10:05:27 2026-09-03 10:05:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:07:27)
10:25:09 2026-09-03 10:25:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:28:09)
10:25:09 2026-09-03 10:25:09 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:28:09)
--- [SHAP] 슬로우 ×6(표본)
11:34:05 2026-09-03 11:34:05 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1658ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:52:01 2026-09-03 12:52:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1017ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:06:01 2026-09-03 13:06:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 959ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:30:01 2026-09-03 13:30:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 931ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:09 2026-09-03 08:41:09 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3157ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3157 band=INFO since_pipe_s=NA
09:00:08 2026-09-03 09:00:08 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 8734ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=8734 band=WARN since_pipe_s=0.2
09:05:04 2026-09-03 09:05:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4203 band=INFO since_pipe_s=0.1
09:50:04 2026-09-03 09:50:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4234 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260903_SYSTEM.log`
```
--- CIRCUIT ×5(표본)
14:29:00 2026-09-03 14:29:00 [INFO] SYSTEM: [Notify] 🚨 [14:29:00] [미륵이] Circuit Breaker 발동!
14:33:00 2026-09-03 14:33:00 [INFO] SYSTEM: [Notify] 🚨 [14:33:00] [미륵이] Circuit Breaker 발동!
14:37:03 2026-09-03 14:37:03 [INFO] SYSTEM: [Notify] 🚨 [14:37:03] [미륵이] Circuit Breaker 발동!
14:41:00 2026-09-03 14:41:00 [INFO] SYSTEM: [Notify] 🚨 [14:41:00] [미륵이] Circuit Breaker 발동!
--- ConstOut ×8(표본)
12:38:00 2026-09-03 12:38:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 12:40:00 (const_output)
12:38:00 2026-09-03 12:38:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
12:38:01 2026-09-03 12:38:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=689ms fit=33ms total=743ms
12:39:01 2026-09-03 12:39:01 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋
--- HALT ×1(표본)
15:40:06 2026-09-03 15:40:06 [INFO] SYSTEM: [CB③계측] 조건성립 61분 / 판정가능 103분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-03 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-09-03 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:11:00 2026-09-03 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:16:00 2026-09-03 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
--- [CB] ×8(표본)
10:25:09 2026-09-03 10:25:09 [INFO] SYSTEM: [CB] 같은 포지션의 추가 손절 레그 — 카운트하지 않는다 (key=2026-09-03 10:24:01, 현재 1회)
14:32:00 2026-09-03 14:32:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
14:32:00 2026-09-03 14:32:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
14:36:05 2026-09-03 14:36:05 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
--- [SchedForceExit] ×1(표본)
15:11:05 2026-09-03 15:11:05 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:07 2026-09-03 15:40:07 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:22 2026-09-03 15:40:22 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:07 2026-09-03 15:40:07 [INFO] SYSTEM: [Notify] ℹ️ [15:40:07] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:07 2026-09-03 15:40:07 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:22 2026-09-03 15:40:22 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260903_SIGNAL.log`
```
--- ConfFloorGuard ×3(표본)
09:00:00 2026-09-03 09:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3479 < 필요 0.4180 (conf_floor=0.330, min_conf=0.418, span=0.0063). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
09:47:00 2026-09-03 09:47:00 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3857 ≥ 필요 0.3800
11:38:01 2026-09-03 11:38:01 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3714 < 필요 0.3720 (conf_floor=0.330, min_conf=0.372, span=0.0132). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
12:30:00 2026-09-03 12:30:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
12:30:00 2026-09-03 12:30:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
12:31:00 2026-09-03 12:31:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
12:38:00 2026-09-03 12:38:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:00 2026-09-03 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-03 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-03 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.2% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-03 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.7% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.410
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.402
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.398
08:40:30 2026-09-03 08:40:30 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.406
--- 안전망 ×8(표본)
09:07:00 2026-09-03 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-03 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-03 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-03 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260903_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3015 < conf_floor=0.3300 (span=0.00238 auc=0.634 out_max=0.3015, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3009 < conf_floor=0.3300 (span=0.00172 auc=0.604 out_max=0.3009, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00081 auc=0.459 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과
08:40:49 2026-09-03 08:40:49 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3179 < conf_floor=0.3300 (span=0.00233 auc=0.559 out_max=0.3179, 기저율=0.3167 n=120) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260903_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 26 | 10:02:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=36,600,786) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |
| 12:00 | 장중 중간점 | 1 | 12:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=36,435,156) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShad… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:06 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260903_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 10 | 08:41:06 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 8 | 09:00:01 [WARNING] total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 9 | 09:00:01 [WARNING] total=1486ms | S0=3ms S1=7ms S2=0ms S3=0ms S4=140ms S5=620ms S6=597ms S7=96ms S8=23ms |
| 10:00 | 장중 초반 | 53 | 09:58:00 [WARNING] 5분 누적 수익률 -0.228% (임계 ±0.221%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1 | 12:06:01 [WARNING] level=WARNING degraded=OFF | latency=318ms | quality=1.00 | cache_age=182s | exceptions_10m=0 |
| 14:00 | 장중 후반 · 장중 재학습 | 12 | 14:00:00 [WARNING] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:06 [WARNING] 오늘 TRAIL_AFTER_TP1 4레그 / 4포지션 중 TP 이벤트 대응 0 · 단일계약 보호전환(설계) 3 · 미대응 1 ⚠ 미대응 합계 -47,496원 (진입 10:03:01). 이 레그들은… |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260903_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:32 [INFO] 활성화 | file=logs\crash_fault.log PID=21356 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 126 | 08:49:01 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 179 | 08:54:01 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 245 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 165 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 194 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 162 | 15:04:00 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 131 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 45 | 15:34:00 [INFO] code=A0569 from=15:33 to=15:34 |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260903_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 61 | 08:45:06 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 104 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0384) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 189 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0390) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 133 | 09:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 12:00 | 장중 중간점 | 107 | 11:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 138 | 13:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 37 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:06 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260902 | 15:40 | 로그 본문 |
| 20260901 | 15:40 | 로그 본문 |
| 20260831 | 15:40 | 로그 본문 |
| 20260830 | 00:07 | 로그 본문 |
| 20260828 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260903** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 검증 총계
## 2026-09-03 (MW0601 520차 — 장전 점검)
### 1. CB② 복원(519차) 라이브 반영 확인 — 재기동 완료
### 2. `session_state.json`의 P8 완료 마커가 다음날 아침 사라짐 — 설계된 폴백으로 실피해 없음
### 3. 오늘 장전 관측 요약 (신규 이상점 없음 확인)
## 2026-09-03 (MW0601 521차 — 장중 점검)
### 1. `[ConfFloorGuard]` 자동진입 하한 도달 불가 — 09:47 복구 후 11:38 재발동, 12:28 시점까지 미복구 (이상점 1-2, 어제 1-6의 2번째 연속 사례)
### 2. 그 외 장중 관측 — 신규 이상점 아님 확인
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 정지 8,734ms(09:00:08, 개장 버스트) — 최근치(0821 11,016 / 0824 20,985 /
  0825 21,781ms)보다 낮음, 15초 미만이라 519차 신규 ALERT 미발화, 정상 범위.
- `[ConfFloorGuard]` 09:00:00 1건 — 기존 반복 패턴(O-p1로 등록, 장중 판정 예정).
- 설정 불변식 28행 전부 `일치`. 브랜치 `v9-dev` 정상. `.git/index.lock` 없음.
  당일 동시 세션 없음(오늘 첫 세션).

**세션 헤더**: MW0601 520차. 리포트: `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md`.

## 2026-09-03 (MW0601 521차 — 장중 점검)

### 1. `[ConfFloorGuard]` 자동진입 하한 도달 불가 — 09:47 복구 후 11:38 재발동, 12:28 시점까지 미복구 (이상점 1-2, 어제 1-6의 2번째 연속 사례)

- **증상**: 09:00:00 발동(`출력상한 0.3479 < 0.4180`) → 09:47:00 복구(`출력상한 0.3857 ≥ 0.3800`,
  장전이 기대한 "오전 중 자연 복귀" 패턴과 일치) → 11:38:01 재발동(`출력상한 0.3714 < 0.3720`),
  이후 12:28(장중 점검 종료 시점)까지 복구 로그 없음. 마지막 진입도 11:30:01이 끝이라
  시간상 정황이 일치한다.
- **원인**: 미확정. (a) 오늘 시장 레짐이 저신호 국면(방향성 약함)인 정상 반응 vs
  (b) 보정기(Calibration) 계산 결함으로 출력 상한이 구조적으로 눌리는 것 — 두 가설
  구분 불가. 장중은 라이브 DB(`predictions`) 조회 금지 구간이라(CLAUDE.md) 확인 불가.
- **결정**: P1로 등록(이상점 1-2). 어제(2026-09-02) 이상점 1-6이 "과거엔 개장 첫 분
  한정이었는데 09-02는 3시간 넘게 지속돼 패턴 이탈"이라 처음 기록했고, 오늘이 그
  패턴의 **2번째 연속 사례**다. 다만 표본 2거래일로는 "구조적 결함"과 "이틀 연속
  저신호 레짐 우연"을 구분할 수 없어(313차 원칙) 아직 확정 결론을 내리지 않는다.
- **Why**: ConfFloorGuard 자체는 설계대로 동작 중(확신도 낮을 때 진입을 막는 것이
  목적)이라 절대원칙 위반은 아니다. 다만 진입 기회가 장시간 사라지는 것이 시장 탓인지
  판단 능력 저하인지 구분해야 다음 조치(방치 vs 보정기 재점검)를 정할 수 있다.
- **How to apply**: F-2(리포트 §2i)로 등록 — 장후 `predictions` 테이블에서 오늘
  09:00~12:28 보정기 출력 분포를 최근 5거래일(08-28~09-02)과 비교. 오늘만 유독
  낮으면 (b) 쪽에 무게, 최근 며칠도 비슷하면 (a) 쪽에 무게. 3거래일째도 같은 패턴이면
  주간회의 안건 상정 검토(아직 이르다).
- **검증**: 표본 2거래일(09-02·09-03) — 313차 원칙에 따라 확정 결론 보류. 장후
  DB 조회로 오늘분 1차 조사, 패턴 지속 여부는 09-04 이후 추가 관측.

### 2. 그 외 장중 관측 — 신규 이상점 아님 확인

- 메인 스레드 정지 17건, 최대 8,734ms, 5초 초과 3건 — CB⑤·FZ-1과 단위가 다른 기존
  482차 F-3 섀도 계측 대상. 오늘 최대치가 최근 실측치(0821·0824·0825)보다 낮음.
- 사이저 최대 3계약 → 실제 진입 최대 2계약 — 기존 `sizing_inversion_watch`
  (실전 전환 기준 ⑧, 417차·431차) 표본 누적, 신규 안건 아님.
- GBM 배치 재학습 0회 — `[WarmupRetrain]` 예약이 08:55 `[PreRetrain]` 스킵으로
  소진됨(전날 EOD 성공). 483차 정정대로 재학습 0회는 정상.
- CB② 카운터 3건(10:03:20·10:24:10·11:07:51), 각각 300초 창 밖이라 리셋 —
  당일정지 미발동. 실전 전환 기준 ⑤ "발동 1회 관측"은 오늘도 미충족.
- 수집기 §11 자동 적신호 중 "매분 루프 커버리지 56.1%"·"12:28~15:10 공백 163분"·
  "Traceback 2건"은 전부 오진 확인 — 증거 수집 시각(12:26)이 장중이라 아직 지나지
  않은 시간이 공백으로 잡혔을 뿐(12:28 `[PipePerf]` 로그로 파이프라인 생존 재확인),
  Traceback은 `[MainStallTrace]` 정상 계측(482차 F-3)이지 크래시가 아니다.
- 오늘 진입 7건 전부 체크리스트 미통과 항목에 `vwap` 없음 — 절대원칙 ③(강제 X) 위반 0건.
- 오늘 매매: 포지션 7건 · 승 3(43%) · 합계 -1.26pt(-165,617원, 포지션 단위). 12:28
  현재 포지션 FLAT.

**세션 헤더**: MW0601 521차. 리포트: `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md`(장중 절).

```

</details>

### dev_memory/NEXT_TODO.md — 1.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 관측 예정
### 이월 (09-02 519차 장후에서 승계, 미해결)
### 사용자 몫 (자동조치가 할 수 없음, 09-02에서 이월)
## 2026-09-03 (MW0601 521차 — 장중 점검)
### 승격 처리
### 신규 등록
### 이월 (09-02 519차 장후에서 승계, 오늘도 미해결)
### 사용자 몫 (자동조치가 할 수 없음, 09-02에서 이월 — 오늘도 미해결)
```

미완료 체크박스 **2360건** (끝에서 30건)
```
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔(F-3은 미래만 고침)
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **G-2 잔여** 정지 경보의 **임계 근거** — 이번엔 화면 노출만 했고 임계는 무변경
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
- [ ] **F-1** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`가
- [ ] **G-1** `collect_evidence.py` §9에 `session_state.json`의 `p8_last_success_date`·
- [ ] **O-p1** `[ConfFloorGuard]` 09:00:00 발동 — 오전 중 자연 복귀 여부를 장중에 확인
- [ ] **CB② 발동 1회 관측** — 실전 전환 기준 ⑤의 남은 조건. 인위적으로 만들지 말 것
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
- [ ] **F-2** `[ConfFloorGuard]` 장시간 미복구 원인 규명 — 장후 `predictions` 테이블에서
- [ ] **G-2** `[ConfFloorGuard]` 발동 로그에 그 시점 `[Calibration]` auc·span 스냅샷
- [ ] **CB② 발동 1회 관측** — 실전 전환 기준 ⑤의 남은 조건. 오늘 카운터 3건 발생했으나
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **1-1** `session_state.json` P8 마커 소실 재발 여부 — 내일(09-04) 장전 재확인
- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 고침)
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **G-2 잔여** 정지 경보의 **임계 근거** — 이번엔 화면 노출만 했고 임계는 무변경

### 사용자 몫

- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인

## 2026-09-03 (MW0601 520차 — 장전 점검)

### 완료 처리

- [x] **미륵이 재기동**(519차 CB②·정지경보·F-1 반영) — 오늘 08:40:01 기동(PID 21356,
      커밋 `8997136` 이후 첫 기동) 확인. 설정 불변식 `CB_CONSEC_STOP_LIMIT=3` `일치` 확인됨

### 신규 등록

- [ ] **F-1** `session_state.json`의 `p8_last_success_date`·`eod_retrain_ok_date`가
      다음날 아침 사라지는 경로 규명 — 어제 15:48:54 정상 기록 확인(`retrain_eod_20260902.log:142`)
      됐으나 오늘 08:46 파일에 없음. 폴백(마커 파일 직접확인)이 정상 작동해 실피해는 없었음.
      표본 1일, 내일(09-04) 장전에 재확인 필요
- [ ] **G-1** `collect_evidence.py` §9에 `session_state.json`의 `p8_last_success_date`·
      `eod_retrain_ok_date`·`date` 3키 자동 게재 — 수동 발견 대신 매일 자동 추적

### 관측 예정

- [ ] **O-p1** `[ConfFloorGuard]` 09:00:00 발동 — 오전 중 자연 복귀 여부를 장중에 확인
      (기존 반복 패턴과 일치하는지)

### 이월 (09-02 519차 장후에서 승계, 미해결)

- [ ] **CB② 발동 1회 관측** — 실전 전환 기준 ⑤의 남은 조건. 인위적으로 만들지 말 것
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건

### 사용자 몫 (자동조치가 할 수 없음, 09-02에서 이월)

- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인

## 2026-09-03 (MW0601 521차 — 장중 점검)

### 승격 처리

- [x] **O-p1 → 이상점 1-2로 승격** — `[ConfFloorGuard]` 09:47 복구 후 11:38 재발동,
      12:28까지 미복구. 어제 1-6의 2번째 연속 사례로 표본이 늘어 이상점 번호 부여.

### 신규 등록

- [ ] **F-2** `[ConfFloorGuard]` 장시간 미복구 원인 규명 — 장후 `predictions` 테이블에서
      오늘 보정기 출력 분포를 최근 5거래일(08-28~09-02)과 비교. 3거래일째도 같은
      패턴이면 주간회의 안건 상정 검토
- [ ] **G-2** `[ConfFloorGuard]` 발동 로그에 그 시점 `[Calibration]` auc·span 스냅샷
      동봉 — 장중에도 DB 조회 없이 레짐 탓/보정기 결함 1차 판단 가능하게

### 이월 (09-02 519차 장후에서 승계, 오늘도 미해결)

- [ ] **CB② 발동 1회 관측** — 실전 전환 기준 ⑤의 남은 조건. 오늘 카운터 3건 발생했으나
      매번 300초 창 밖이라 리셋(당일정지 미발동). 인위적으로 만들지 말 것
- [ ] **O-t1** net 대사 gross 축 차이(-315,000원) 원인 규명
- [ ] **O-t2** F-10(exit_stage 다중체결 오분류) 3번째 사례
- [ ] **O-t3** `entry_source` 오표기 과거 영향 범위 회고 스캔
- [ ] **1-10** 누적 대장 P5-01~05·07·08 재검증 6건
- [ ] **1-1** `session_state.json` P8 마커 소실 재발 여부 — 내일(09-04) 장전 재확인

### 사용자 몫 (자동조치가 할 수 없음, 09-02에서 이월 — 오늘도 미해결)

- [ ] 09-01 "매수 3계약 매도" 지시 미반영 경위 확인
- [ ] 정체불명 매매 38건 · 09-02 손실 포지션 본인 여부 확인
- [ ] 대신증권 계좌·정산(-556만원) 직접 확인

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

### `data/heartbeat_MW0601_20260903.json` — 244B · 09-03 15:40:18
```json
{
 "pid": 21356,
 "written_at": "2026-09-03T15:40:18",
 "beat_epoch": 1788417615.7343554,
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

### `docs/정기점검/매일점검` — 97개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260903-점검리포트.md` | 30.6KB | 09-03 12:32 |
| `docs/정기점검/매일점검/evidence_MW0601-20260903_intra.md` | 69.0KB | 09-03 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260903_pre.md` | 54.0KB | 09-03 09:00 |
| `docs/정기점검/매일점검/MW0601-20260902-점검리포트.md` | 114.3KB | 09-02 19:10 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_post.md` | 78.0KB | 09-02 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_intra.md` | 66.8KB | 09-02 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20260902_pre.md` | 58.1KB | 09-02 09:00 |
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-01 18:19 |

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

1. `logs/20260903_WARN.log`: **Traceback** 출현 4건 — 크래시/메모리 계열
2. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
3. 포지션 7건 중 최종청산이 하드스톱·손절 계열 **6건(86%)** — 손절 준수율 확인 필요 (레그 10행)
4. 다레그 포지션 **3건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. 메인 스레드 정지 5초 초과 **5건** (최대 8734ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260903_WARN.log`: **ConstOut** 4건(표본)
8. `logs/20260903_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20260903_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260903_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260903_LEARNING.log`: **축퇴** 8건(표본)
12. 미커밋 변경 520건 (실질 2건 · 코드 0건 · EOL 파생 515건)
13. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260903*.log` (Windows) / `grep 강제청산 logs/*20260903*.log`*