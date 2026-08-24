# 미륵이 증거 다이제스트 — 2026-08-20 / POST

- 생성 2026-08-20 16:22:17 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/festive-sharp-archimedes/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260820` · `2026-08-20` · `260820` · `0820`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **24개** 파일 · 24개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260820.txt` | 28B | 08-20 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260820.txt` | 181B | 08-20 15:49 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260820.log` | 320B | 08-20 15:12 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260820.json` | 243B | 08-20 15:40 |
| `launcher_{DATE}_084001_9654.log` | 1 | `logs/Mireuk_batch/launcher_20260820_084001_9654.log` | 1.6MB | 08-20 15:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260820.log` | 20.1KB | 08-20 15:49 |
| `retrain_intraday_{DATE}_093700.log` | 1 | `logs/retrain_intraday_20260820_093700.log` | 2.4KB | 08-20 09:37 |
| `retrain_intraday_{DATE}_101100.log` | 1 | `logs/retrain_intraday_20260820_101100.log` | 2.4KB | 08-20 10:11 |
| `retrain_intraday_{DATE}_110200.log` | 1 | `logs/retrain_intraday_20260820_110200.log` | 2.4KB | 08-20 11:02 |
| `retrain_intraday_{DATE}_114103.log` | 1 | `logs/retrain_intraday_20260820_114103.log` | 2.4KB | 08-20 11:41 |
| `retrain_intraday_{DATE}_131400.log` | 1 | `logs/retrain_intraday_20260820_131400.log` | 2.4KB | 08-20 13:14 |
| `retrain_intraday_{DATE}_135200.log` | 1 | `logs/retrain_intraday_20260820_135200.log` | 2.4KB | 08-20 13:52 |
| `strategy_report_{DATE}_154007.txt` | 1 | `data/daily_reports/strategy_report_20260820_154007.txt` | 2.3KB | 08-20 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260820_DATA.log` | 342.9KB | 08-20 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260820_DEBUG.log` | 222.1KB | 08-20 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260820_HEALTH.log` | 4.7KB | 08-20 14:37 |
| `{DATE}_HOGA.log` | 1 | `logs/20260820_HOGA.log` | 54.0MB | 08-20 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260820_LEARNING.log` | 277.8KB | 08-20 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260820_MICRO.log` | 1.0MB | 08-20 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260820_PROBE.log` | 96.7KB | 08-20 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260820_SIGNAL.log` | 567.1KB | 08-20 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260820_SYSTEM.log` | 841.7KB | 08-20 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260820_TRADE.log` | 12.9KB | 08-20 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260820_WARN.log` | 67.7KB | 08-20 15:40 |

## 2. 코드·커밋 상태

- HEAD `7a59796` · 브랜치 `v9-dev` · 미커밋 461건
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
 M ROADMAP.md
 M SETUP_GUIDE.md
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
 M config/secrets_example.py
 M config/strategy_params.py
… 외 421건
```

**당일(2026-08-20) 커밋**
```
7a59796 [MW0601] 480차 후속4: F-2 가드가 감시 개시를 파일에 남긴다 — 사이드카 자신의 생존 증거
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
```

**최근 커밋 12건**
```
7a59796 [MW0601] 480차 후속4: F-2 가드가 감시 개시를 파일에 남긴다 — 사이드카 자신의 생존 증거
f94536f [MW0601] 473차 F1~F3 검증 완료: F-8 Phase B 라이브 확인 — 배선 무결 + 경고 전제 정정
091783c [MW0601] 480차 후속3: DECISION_LOG 테스트 집계 정정 — 576 passed / 신규 38건
ac73a18 [MW0601] 480차 후속2: F-5 폴백 경고 테스트를 전체 스위트에서도 통과하게 — caplog 제거
af2dbcc [MW0601] 480차 후속: F-2 수동 실행(--once)은 경보 마커를 남기지 않는다
c30e414 [MW0601] 480차 (3/3): 로드맵·dev_memory — 전환기준 ② 선행 ⓑ 추가 + 워치독 임계 26주 WFA 편입
9bb58eb [MW0601] 480차 (2/3): 0819 리포트 F-3·F-4·G-2 — ofi_norm 분포 프로브 + WaitDC 폴백 마커 + 로그 종료시각 기준선
ea60409 [MW0601] 480차 (1/3): 0819 리포트 F-2·G-1·F-5 — 프로세스 밖 FLAT 가드 + 하트비트 파일 + 진입 파라미터 승계
2330a66 [MW0601] 479차 후속: 배포 검증에서 발견 — pipeperf(SYSTEM 소급 glob, dev 전용) 예외 등록 + 문서 dev 특이점 2건
fdd80f5 [MW0601] 479차 (3/3): v9-dev 전용분 — 476차 스킬/설정 + test_476 + dev_memory 기록
49980d9 [MW0601] 479차 (2/3): 로그 채널별 차등 보관 — 측정 근거 + 압축 단계 + EOD 체인 발화 배선
59c516a [MW0601] 479차 (1/3): 476차 보관정책 재설계분 커밋 — monthly_cleanup 안전화 + 보관정책 문서
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
| `MODEL_LABEL_STATE_UNLOCK_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지 |
| `PRE_RETRAIN_DONE_BY_EOD_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치 |
| `ZONE_ENTRY_BAN_ENFORCE` | `—` | `False` | **미발견 ⚠** | 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지 |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | `—` | `True` | **미발견 ⚠** | 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다 |
| `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` | `—` | `True` | **미발견 ⚠** | 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치) |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

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

_본문 미열람(설정): `20260820_HOGA.log` 54.0MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260820.txt`** — 28B · 08-20 15:40:07
```
2026-08-20T15:40:07.147164
```

**`data/daily_reports/strategy_report_20260820_154007.txt`** — 2.3KB · 08-20 15:40:07
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-08-20 15:40
========================================================
  버전    : v1.0  (64일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=0.32  MDD(자본대비)=3.0%
  당일      : WR=50.0%  PF=0.17
  롤링20일: 누적 +198565원  Sh=0.32  MDD(자본대비)=3.0%  MDD(peak대비)=274.2%
  당일손익 : broker(gross) -335,000원  수수료 13,017원  net -348,017원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.26)
  PSI     : 0.040 (CLEAR)
  PSI/feat: cvd=0.125  vwap_position=0.040  ofi=0.007
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -4,188원  승률 55.0%  합계 -83,757원
  등급별 순EV(30일): A=+13,104원(147건,승63%)  C=-22,381원(39건,승62%)
  호라이즌별 순EV(30일): 1m=+32,730원(20건)  3m=-6,753원(104건)  5m=+11,276원(58건)  ?=+111,813원(4건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 62분  5일평균 53분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 56.0pt(5일평균 39.8pt)  1분평균변동 1.06pt(5일평균 0.93pt)
--------------------------------------------------------
  진입 퍼널(2026-08-20, 총 369분):
    FLAT 209 → conf미달 90 → CoherenceGate 9 → 게이트차단 55 → 후보 6 → 진입 4
    게이트별: 체크리스트항목미달=42  시가갭(OPEN_VOLATILE)=5  마감시간(신규진입금지)=3  포지션보유중(평가생략)=2  쿨다운=1  Degraded신뢰도=1  콜드스타트/기타(RegimeOverride)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 2건
      └ 상세: JointGateBlock=2
      └ JointGateBlock 2건 (무정보폴백 1건 = 50.0%) [표본 18건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260820.txt`** — 181B · 08-20 15:49:02
```
completed: 2026-08-20 15:49:02
rows: 40395
cols: 97
horizons_replaced: 6/6
t_load_s: 45.7
t_retrain_s: 190.7
t_total_s: 237.0
daily_close_seen: true
wait_dc_timeout: false
```

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20260820_101100.log`, `retrain_intraday_20260820_110200.log`, `retrain_intraday_20260820_114103.log`, `retrain_intraday_20260820_131400.log`, `retrain_intraday_20260820_135200.log`, `20260820_MICRO.log`, `20260820_DATA.log`, `20260820_PROBE.log`_

### `logs/20260820_TRADE.log` — 12.9KB · 99행 · 최종 15:40:04

- 형식 평문 · 시각 인식 99행 · INFO=99

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:24 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-20 08:41:29 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-20 10:04:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-20 10:05:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-20 10:06:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-20 14:01:35 [INFO] TRADE: [Chejan] 상태=체결 주문번호=5408 code=A0569 방향=SHORT 체결=1 미체결=0
2026-08-20 14:01:35 [INFO] TRADE: [Position] 체결청산 LONG @ 1078.92 | PnL=+0.48pt (+22,382원) | 하드스톱(틱)
2026-08-20 14:01:35 [INFO] TRADE: [청산 완료] PnL=+0.48pt (+22,382원)
2026-08-20 14:58:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,190,486) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.2→2계약]
2026-08-20 15:40:04 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×99

**컴포넌트 상위 15** — `Chejan`×27, `Position`×18, `Sizer`×13, `주문요청`×11, `진입체크`×4, `체결진입`×4, `체결진입보정`×4, `TickStop-S0C`×4, `청산 완료`×4, `ProfitGuard`×2, `손절1차 조기축소`×2, `JointGateBlock 차단`×2, `TickTP1`×2, `손절1차 분할체결`×1, `TP1 부분청산`×1

### `logs/20260820_WARN.log` — 67.7KB · 321행 · 최종 15:40:06

- 형식 평문 · 시각 인식 314행 · WARNING=314, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-20 08:41:32 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-20 08:41:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-20 08:41:40 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 4125ms — live 중단 원인 분석용
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -348017원
════════════════════════════════════════════════════
```

</details>

**WARNING — 태그 33종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 84 | 08:41:32 | 14:47:44 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 27 | 10:55:01 | 14:01:35 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='2883' | pending='ENTRY:LONG qty=3 filled=0 order_no=? reason=진입 req_at=10:55:00.852' | positio… |
| `ChejanMatch` | 27 | 10:55:01 | 14:01:35 | order_no='2883' | pending='ENTRY:LONG qty=3 filled=0 order_no=2883 reason=진입 req_at=10:55:00.852' | pending_matched=True |
| `PendingOrder` | 22 | 10:55:00 | 14:01:35 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 1085.54, 'reason': '진입', 'hint_source': '', 'atr': 1.8071, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_qty… |
| `Health` | 17 | 09:01:02 | 14:36:02 | level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0 |
| `PipePerf` | 16 | 09:01:02 | 13:53:03 | total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| `CB⑤` | 16 | 09:01:02 | 13:53:03 | 파이프라인 2353ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `ScalerRefresh` | 15 | 09:13:00 | 15:03:01 | 5분 누적 수익률 +0.643% (임계 ±0.585%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `HealthPolicy` | 8 | 09:02:00 | 13:54:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2353ms quality=0.74 cache=1s exc10m=0) | cause=S5(1200ms) |
| `EntryFillFlow` | 8 | 10:55:01 | 13:57:01 | actual_side='LONG' | after='LONG 3계약 @ 1085.42' | applied_side='LONG' | before='LONG 3계약 @ 1085.54' | fill_no='' | fill_price=1085.42 | fill_qty=1 | order_no='2883' | pending='ENTRY:LONG qty=3 filled=1 order_no=2883 reason=진입 req_at=10:55:… |
| `ExitCooldown` | 8 | 10:56:05 | 14:01:35 | 하드스톱(틱) 후 3분 재진입 금지 (until 10:59:05) |
| `ConstOut` | 6 | 09:36:00 | 13:51:01 | ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 |

**채널** — `SYSTEM`×297, `HEALTH`×17

**컴포넌트 상위 15** — `LiveDBG`×84, `ChejanFlow`×27, `ChejanMatch`×27, `PendingOrder`×22, `Health`×17, `PipePerf`×16, `CB⑤`×16, `ScalerRefresh`×15, `HealthPolicy`×8, `EntryFillFlow`×8, `ExitCooldown`×8, `-`×7, `ConstOut`×6, `ExitSendOrderResult`×6, `CB`×5

### `logs/20260820_SYSTEM.log` — 841.7KB · 6057행 · 최종 15:40:22

- 형식 평문 · 시각 인식 6036행 · INFO=6036, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:40:50 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=13140 | 행감지=30s all_threads=True
2026-08-20 08:41:10 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-20 08:41:10 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-20 08:41:10 [INFO] SYSTEM: 미륵이 초기화
2026-08-20 08:41:10 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-19) 종가 버퍼 로드: 296봉
  …
2026-08-20 15:40:07 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-08-20 15:40:07 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-20 15:40:22 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-20 15:40:22 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-20 15:40:22 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×6036

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1384, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×408, `S6Detail`×369, `PipePerf`×369, `System`×98, `MicroRegime`×69, `RegimeFingerprint`×67, `CybosEvent`×54, `BalanceUI`×50, `OptionChain`×49, `CybosDailyPnl`×36

### `logs/20260820_SIGNAL.log` — 567.1KB · 5015행 · 최종 15:40:04

- 형식 평문 · 시각 인식 5015행 · WARNING=2095, INFO=2920

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.409
  …
2026-08-20 15:09:01 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: RegimeOverride / FLAT수렴 / conf미달(0.400<mc0.970)
2026-08-20 15:10:26 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-20 15:40:04 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-20 15:40:04 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-20 age=22m extreme=415 refresh=37 grade_x=129 cb3=0
2026-08-20 15:40:04 [INFO] SIGNAL: [ModelHealth] date=2026-08-20 앙상블유효가동률=76.2% | 파이프라인 369분 | ConstOut 6회/9분 {"3m": {"events": 6, "minutes": 9}} | WeightCollapse 79분 | 장중재학습 6회
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1344 | 09:01:02 | 15:03:02 | 1m 'macro_vix' scale=0.0136 → floor=0.10 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 192 | 08:45:03 | 12:43:02 | 1m CORE 'ofi_norm' raw_std≈0(0.0379) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ScalerMonitor` | 165 | 09:01:00 | 14:50:01 | ts=09:00 horizon=1m age=2m max_z=-15.07(institution_futures_net) extreme=3 |
| `Model` | 164 | 09:01:00 | 14:50:01 | 1m 극단 z-score 3개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 144 | 09:06:00 | 15:07:01 | 신뢰도 미달 34.9% < 37.9% → 강제 X등급 |
| `WeightCollapse` | 79 | 09:08:00 | 15:08:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 6 | 09:36:00 | 13:51:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:06:00 | 09:06:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5015

**컴포넌트 상위 15** — `ScalerFloor`×1368, `SIGNAL`×738, `MetaGate`×390, `Ensemble`×373, `FQAdj`×367, `ZeroDiag`×309, `ScalerRefresh`×234, `Model`×206, `Checklist`×185, `ScalerMonitor`×166, `ATR-Horizon`×145, `차단`×101, `WeightCollapse`×79, `ToxicityGate`×76, `MicroRegime`×69

### `logs/20260820_LEARNING.log` — 277.8KB · 2742행 · 최종 15:40:04

- 형식 평문 · 시각 인식 2742행 · WARNING=139, INFO=2603

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 08:41:12 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.499 out_max=0.3750 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-20 08:41:14 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00062 auc=0.538 out_max=0.3559 (n=135) → 보정 재적용
2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00047 auc=0.523 out_max=0.3646 (기준 auc<0.53 and span<0.020, 기저율=0.3643 n=140) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-08-20 15:40:04 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-20 15:40:04 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-20 15:40:04 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-20 15:40:04 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-20 15:40:04 [INFO] LEARNING: [Sigma] EOD sigma_20=0.12236% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 137 | 08:41:14 | 14:56:02 | 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 1 | 12:40:01 | 12:40:01 | total=556ms raw_fetch=6ms pred_select=124ms pred_update=49ms pred_insert=161ms verified=5 |
| `DriftAdjuster` | 1 | 15:40:04 | 15:40:04 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 1일) |

**채널** — `LEARNING`×2742

**컴포넌트 상위 15** — `LEARNING`×1214, `SGD`×369, `sigma`×356, `Calibration`×266, `Bias⚠`×155, `Bias`×133, `MetaConf`×80, `OnlineLearner`×54, `ScalerWarmup`×42, `BiasReset`×15, `SHAP`×13, `GBM-64`×12, `GBM`×12, `RF`×7, `ExtremityCorrector`×5

### `logs/20260820_HEALTH.log` — 4.7KB · 35행 · 최종 14:37:03

- 형식 평문 · 시각 인식 35행 · WARNING=17, INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 09:01:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0
2026-08-20 09:02:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=588ms | quality=0.74 | cache_age=148s | exceptions_10m=0
2026-08-20 09:27:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=315ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-20 09:28:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=264ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-20 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 315ms (표본 20분)
  …
2026-08-20 13:54:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=390ms | quality=1.00 | cache_age=47s | exceptions_10m=0
2026-08-20 14:33:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=380ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-20 14:34:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=312ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-08-20 14:36:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=383ms | quality=1.00 | cache_age=180s | exceptions_10m=0
2026-08-20 14:37:03 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=295ms | quality=1.00 | cache_age=57s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 17 | 09:01:02 | 14:36:02 | level=WARNING degraded=OFF | latency=2353ms | quality=0.86 | cache_age=89s | exceptions_10m=0 |

**채널** — `HEALTH`×35

**컴포넌트 상위 15** — `Health`×34, `HealthTrend`×1

### `logs/retrain_eod_20260820.log` — 20.1KB · 140행 · 최종 15:49:02

- 형식 평문 · 시각 인식 140행 · WARNING=8, INFO=132

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 15:45:05,305 [INFO] EOD_RETRAIN: =======================================================
2026-08-20 15:45:05,305 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-20 15:45:05,305 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-20 15:45:05,305 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-20 15:45:05,305 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-20 15:49:02,982 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0375 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-20 15:49:02,983 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0952 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-20 15:49:02,986 [INFO] SIGNAL: [ScalerRefresh] ts=15:49 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-08-20 15:49:02,990 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-20 15:49:02,992 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:59 | 15:47:54 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1504봉(81%)이 현행 학습구간 (현행 cutoff=2026-08-19 13:10:00 ≥ 홀드아웃 시작=2026-08-12 10:59:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-19 13:10 >= holdout_start=2026-08-12 10:59 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-19 … |
| `GuardGhost` | 2 | 15:46:10 | 15:46:10 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-20 13:21:00까지)인데 acc.txt=0.4217는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×63, `SIGNAL`×49, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×20, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `RegimeFingerprint`×3, `WaitDC`×2, `GuardGhost`×2, `P8`×2

### `logs/retrain_intraday_20260820_093700.log` — 2.4KB · 20행 · 최종 09:37:24

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-20 09:37:00,660 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-20 09:37:00,661 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-20 09:37:00,661 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-20 09:37:00,661 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d6528b03.json
2026-08-20 09:37:03,822 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-20 09:37:23,973 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=1.01s | old_acc=0.4217)
2026-08-20 09:37:24,062 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-20 09:37:24,062 [INFO] LEARNING: [Retrain] 완료 | 20.2초 | 성공=1/1 호라이즌
2026-08-20 09:37:24,063 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 23.4s 데이터=4800행
2026-08-20 09:37:24,064 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d6528b03.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -348017원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 4 |
| 진입 등록(`[Position] 진입`) | 4 |
| 체결(`[체결진입]`) | 4 |
| 청산(`체결청산`) | 4 |
| 차단(`[차단]`) | 101 |
| 사이저 호출(`[Sizer]`) | 13 |

### 청산 4건 · 승 1 (25%) · 합계 -4.47pt (-230,004원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 10:56:05 | LONG | -2.92 | -147,628 | 하드스톱(틱) |
| 13:22:51 | LONG | -2.01 | -102,134 | 하드스톱(틱) |
| 13:43:58 | LONG | -0.02 | -2,624 | 하드스톱(틱) |
| 14:01:35 | LONG | +0.48 | +22,382 | 하드스톱(틱) |

**청산 사유 분포** — `하드스톱(틱)`×4

> 하드스톱·손절 계열 4/4건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 4건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:55:00 | LONG | 3 | 1085.54 | 3m | neutral |
| 13:20:00 | LONG | 2 | 1088.98 | 1m | neutral |
| 13:41:01 | LONG | 2 | 1082.64 | 3m | trend |
| 13:57:01 | LONG | 1 | 1078.52 | 3m | trend |

계약수 분포 — 1계약×1, 2계약×2, 3계약×1

등급 분포 — `A급(원시C)`×2, `C급`×2

**진입한 건들의 체크리스트 미통과 항목** — `fore`×4, `cvd`×2, `ofi`×2, `prev`×2, `chas`×1, `coun`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×4, **2계약**×1, **3계약**×8

실제 진입 계약수 — **1계약**×1, **2계약**×2, **3계약**×1

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×13

### 차단 사유 101건 · 28종

| 건수 | 사유 |
|---|---|
| 43 | 등급X — 미통과 항목: 2_confidence |
| 8 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 7 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 7 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 6 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 4 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 11_countertrend |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.1pt > ATR×5.0=13.4pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.6pt > ATR×5.0=12.8pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.3pt > ATR×5.0=12.8pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.1pt > ATR×5.0=12.3pt (시가=1050.50 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.2pt > ATR×5.0=13.1pt (시가=1050.50 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 19.7pt > ATR×5.0=13.1pt (시가=1050.50 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign |

**체크리스트 미통과 항목 누적** — `2_confidence`×43, `3_vwap`×40, `6_foreign`×40, `5_ofi`×26, `7_prev_bar`×21, `4_cvd`×19, `11_countertrend`×11, `10_chase`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 7건

- `연속 손절 1회` ×2
- `일간 리셋 완료` ×2
- `연속 손절 2회` ×1
- `연속 손절 3회` ×1
- `연속 손절 4회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 25건 · 최대 8375ms · 5초 초과 4건

상위 — 8375ms, 5297ms, 5141ms, 5047ms, 4797ms, 4750ms, 4735ms, 4547ms

> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **4건**이다. CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260820_WARN.log`
```
--- ConstOut ×6(표본)
09:36:00 2026-08-20 09:36:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
10:10:00 2026-08-20 10:10:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:01:00 2026-08-20 11:01:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:40:02 2026-08-20 11:40:02 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×5(표본)
10:55:17 2026-08-20 10:55:17 [WARNING] SYSTEM: [CB] 연속 손절 1회
10:56:05 2026-08-20 10:56:05 [WARNING] SYSTEM: [CB] 연속 손절 2회
13:20:30 2026-08-20 13:20:30 [WARNING] SYSTEM: [CB] 연속 손절 3회
13:22:51 2026-08-20 13:22:51 [WARNING] SYSTEM: [CB] 연속 손절 4회
--- [ExitCooldown] ×8(표본)
10:56:05 2026-08-20 10:56:05 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:59:05)
10:56:05 2026-08-20 10:56:05 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:59:05)
13:22:51 2026-08-20 13:22:51 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:25:51)
13:22:51 2026-08-20 13:22:51 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 13:25:51)
--- [SHAP] 슬로우 ×3(표본)
13:41:01 2026-08-20 13:41:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 902ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
14:17:02 2026-08-20 14:17:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1135ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
15:06:02 2026-08-20 15:06:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1091ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:35 2026-08-20 08:41:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3250ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:01:03 2026-08-20 09:01:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4344ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:11:02 2026-08-20 09:11:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:38:03 2026-08-20 09:38:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260820_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:00 2026-08-20 09:36:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:38:00 (const_output)
09:36:00 2026-08-20 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:00 2026-08-20 09:36:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=424ms fit=39ms total=467ms
09:37:00 2026-08-20 09:37:00 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- PSI ×8(표본)
09:01:00 2026-08-20 09:01:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.008 level=0 (heartbeat)
09:07:00 2026-08-20 09:07:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
09:12:00 2026-08-20 09:12:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
09:18:00 2026-08-20 09:18:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.009 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:04 2026-08-20 15:40:04 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:04 2026-08-20 15:40:04 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:03 2026-08-20 15:11:03 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:07 2026-08-20 15:40:07 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:22 2026-08-20 15:40:22 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:07 2026-08-20 15:40:07 [INFO] SYSTEM: [Notify] ℹ️ [15:40:07] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:07 2026-08-20 15:40:07 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:22 2026-08-20 15:40:22 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260820_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:06:00 2026-08-20 09:06:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3790 (conf_floor=0.330, min_conf=0.379, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:36:00 2026-08-20 09:36:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:36:00 2026-08-20 09:36:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:37:00 2026-08-20 09:37:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:38:02 2026-08-20 09:38:02 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:08:00 2026-08-20 09:08:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=RISK_ON [WeightCollapse]
09:11:00 2026-08-20 09:11:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.7% grade=X regime=RISK_ON [WeightCollapse]
09:14:00 2026-08-20 09:14:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.8% grade=X regime=RISK_ON [WeightCollapse]
09:17:00 2026-08-20 09:17:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=36.3% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.419
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.400
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.396
08:40:46 2026-08-20 08:40:46 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.404
--- 안전망 ×8(표본)
09:08:00 2026-08-20 09:08:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:11:00 2026-08-20 09:11:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:14:00 2026-08-20 09:14:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:17:00 2026-08-20 09:17:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260820_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00049 auc=0.464 out_max=0.3127 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00002 auc=0.499 out_max=0.3750 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:41:14 2026-08-20 08:41:14 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00062 auc=0.538 out_max=0.3559 (n=135) → 보정 재적용
08:41:14 2026-08-20 08:41:14 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00047 auc=0.523 out_max=0.3646 (기준 auc<0.53 and span<0.020, 기저율=0.3643 n=140) → 보정 미적용, raw 통과 [기존 fitted 해제]
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260820_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:24 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 3 | 10:04:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=50,610,589) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |
| 14:00 | 장중 후반 · 장중 재학습 | 16 | 13:57:01 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=50,177,068) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1) [KellyAdv… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:04 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260820_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:32 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 7 | 09:01:02 [WARNING] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 09:01:02 [WARNING] total=2353ms | S0=13ms S1=34ms S2=0ms S3=0ms S4=541ms S5=1200ms S6=498ms S7=22ms S8=44ms |
| 10:00 | 장중 초반 | 1 | 10:01:00 [WARNING] 5분 누적 수익률 +0.354% (임계 ±0.326%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 1 | 12:06:02 [WARNING] level=WARNING degraded=OFF | latency=306ms | quality=1.00 | cache_age=184s | exceptions_10m=0 |
| 14:00 | 장중 후반 · 장중 재학습 | 38 | 13:54:00 [WARNING] Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=2615ms quality=1.00 cache=0s exc10m=0) | cause=S0(2318ms) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1 | 15:06:02 [WARNING] 슬로우 감지 1091ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:40:06 [WARNING] mc-conf 괴리: 최근 5거래일 평균 진입후보 53분/일 < 하한 60분 — 금일 62분. |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260820_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 89 | 08:40:50 [INFO] 활성화 | file=logs\crash_fault.log PID=13140 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:00 [INFO] code=A0569 from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 193 | 08:54:00 [INFO] code=A0569 from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 212 | 09:54:00 [INFO] code=A0569 from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 171 | 11:54:00 [INFO] code=A0569 from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 224 | 13:54:00 [INFO] code=A0569 from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 173 | 15:04:00 [INFO] code=A0569 from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 141 | 15:12:00 [INFO] code=A0569 from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 40 | 15:34:00 [INFO] #137800 code=A0569 raw_time=153400 parsed=15:34:00 price=1078.10 vol=1 bid1=1078.08 ask1=1078.10 flag=49 side… |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260820_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:03 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0379) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 93 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0366) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 179 | 08:55:04 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0428) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 167 | 09:54:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=6, group=short) | VWAP pos=+2.000 need <0 (SHORT) bull_exh=0.00 |
| 12:00 | 장중 중간점 | 90 | 11:56:02 [WARNING] 신뢰도 미달 35.3% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 155 | 13:54:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+2.000 need <0 (SHORT) bull_exh=0.00 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 50 | 15:05:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:04 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260819 | 17:02 | 로그 본문 |
| 20260818 | 15:40 | 로그 본문 |
| 20260817 | 17:58 | 로그 본문 |
| 20260814 | 15:40 | 로그 본문 |
| 20260813 | 15:40 | 로그 본문 |
| **중앙값** | **15:40** | 기준선 |
| **오늘 20260820** | **15:40** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 2.0MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [6] 정상 확인 (이상점 아님 — 재상정 방지용 기록)
## 2026-08-20 (MW0601 481차 후속 — 장중 점검 · 분석만, 코드 0건)
### [1] 수집기 §5가 부분청산 레그를 세지 않는다 — 당일 손실의 45% 은닉 (P1, 신규)
### [2] 등급 인플레(원시C→A)가 CB③-P4의 유일한 사정권을 구조적으로 비운다 (P1, 기전은 신규)
### [3] 스킬 참조문서가 CLAUDE.md 461·474차와 정면 충돌 (P2, 신규)
### [4] 재발 카운트 갱신 (신규 아님 — 재상정 방지용)
### [5] [16] chase_foreign_combo — 표본 1건 추가 (판단 금지)
### [6] 정상 확인 (이상점 아님 — 재상정 방지용 기록)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
%**"* ↔ 461차가 **재인용 금지**로
  못박은 값. 정본은 `CB_ACCURACY_MIN_30M = 0.28`(FLAT 제외 방향성 채점, 98차).
  §3-B에 드리프트로 적혀 있으나 **§1이 여전히 35%를 "절대원칙 원문"으로 제시**한다.

**결정**: F-2로 등록, **장후 적용**(F-1과 같은 커밋 가능).
**Why**: 매 국면 3회 × 매 거래일 반복 노출되는 경로다. SKILL.md 자체 규약이
*"CLAUDE.md가 옳다 — 갱신하고 넘어가라"* 이다.

### [4] 재발 카운트 갱신 (신규 아님 — 재상정 방지용)

| 관측 | 오늘 실측 | 기존 등록 |
|---|---|---|
| `ConstOut ['3m']` → 스케일러 재적합 | **4회** (09:36·10:10·11:01·11:39) — 08-19와 동수 | 08-14 F-8. `DECISION_LOG:25327` *"이미 등록됨. 신규 아님"* / `:26215` 5거래일 14건 중 13건이 3m |
| 장중 재학습 → S0 리로드 → CB⑤ 경고 | S0 **2,342~2,632ms**, 파이프 2,659~3,114ms, CB⑤ 4건, `HealthPolicy Degraded 선제차단` 4회 → `[차단] Degraded 최소신뢰도 62.0% 미달` **3건** | 462차 P2 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP`가 이 경로를 겨냥했으나 **v9-dev 미배선**(481차 [4] 실측) — F-4에 물림 |
| CB② 카운터가 **한 포지션**에서 `1회`·`2회` | 10:55:17 조기축소 → 1회, 10:56:05 하드스톱 → 2회 | `NEXT_TODO:14085` [08-29 CB② 보강] 라이브 실례 **2일차** |
| 미커밋 459건 (CRLF) | `git diff --stat` 2,200 ins / 2,200 del 대칭 | F-5, **3일차** |
| 불변식 `미발견` 5행 | 동일 | F-4, **7일차** — repo 소스에 상수 자체가 없음(481차 [4]) |
| `WeightCollapse` 43건 / `ConfFloorGuard` 1건(09:06) | 안전망 정상 발동 | 기존 관측 축 |

### [5] [16] chase_foreign_combo — 표본 1건 추가 (판단 금지)

오늘 **유일 진입이 정확히 그 조합**(`fore❌`+`chas❌`), 등급 A, 패 **-269,884원**.
🔴 **확정 결정 존재 — 재상정 금지.** `VALIDATION_CAMPAIGN_DECISIONS["chase_foreign_combo_watch"]`
(449차, 2026-08-08 주간회의 승인) = *"활성화 금지 유지 — PC간 부호 역전"*
(MW0601 −451,249 vs MW0602 **+2,099,082**). **재검토 조건은 양 PC A등급 누적 부호 수렴**이며
오늘 표본은 그것을 만들지 못한다. 표본만 축적, 판단은 주간회의.

### [6] 정상 확인 (이상점 아님 — 재상정 방지용 기록)

- 매분 9단계 파이프라인 **09:01~12:31 209분 전량 커버**, 공백 0. `[PipePerf][DBG]` 209건.
  (수집기 §11의 "커버리지 56.1% / 12:28~15:10 163분 공백"은 **장중 실행이라 당연** — F-5의
  §7 국면 스코프 이슈와 같은 계열)
- 절대원칙 ③ ✅ — 10:55 진입 `vwap✅ cvd✅ ofi✅`(단기 3m 그룹 CORE 3종 전량 통과).
  **`vwap` 미통과 진입 0건**
- 절대원칙 ④⑤ ✅ — `0xC0000409`·`STACK_BUFFER`·`-2147221008` 각 0건, PID 13140 단일
- 절대원칙 ⑥ ✅ — 알파봇 자동통합·백테스트 큐 흔적 0건 / ⑦ 장중 코드 배포·재기동 0건
- CB① 신호반전 0 / CB③ HALT 0 / CB④ 0 / **CB⑤ 5초 초과 0건**(경고 5건은 전부 3.2s 이하,
  09:01은 `[장시작버스트→임계9s]` 정상 예외)
- `degraded=ON` 0건 / `[Brier] 과신` 0건 / `SHAP 슬로우` 0건 / `MemoryError`·OOM 0건
- FP-CRITICAL 섀도 `PSI=0.008~0.009 level=0` ✅ / FZ-1 하트비트
  `beat_age_sec 3.0 · strikes 0 · fired false` ✅ (FZ-11 관측 1일차 진행)
- 손절 설계 준수 ✅ — 진입 1085.54 · 손절 1082.83 = **2.71pt = ATR 1.8071 × 1.5**
- `[Sizer]` 3계약 = `MAX_CONTRACTS=3` 상한 도달. **431차 배포분 — 재상정 금지**
  ([28] `sizing_inversion_watch` qty=3 표본 1건 축적)
- 블로킹 최대 **4,750ms**(12:23:05) — `CB_PIPE_PAUSE_MS=5_000`의 95%, **초과 0건**.
  4초대 6건 → 장후 종일 분포 확인(O-10)

```

</details>

### dev_memory/NEXT_TODO.md — 1013.7KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 477차 후속6 — GR-1 구현 완료 (MW0601, 2026-08-18)
### 477차 후속7 — GR-3 구현 완료 (MW0601, 2026-08-18)
### 478차 — 장전 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 478차 후속 — 장중 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 478차 후속 — 08-19 메인 스레드 라이브락(미종료 사고) Fix (MW0601, 상세: MW0601-20260819-미종료-딥다이브.md §5)
### 478차 후속2 — 장후 점검 (MW0601, 2026-08-19 · 분석만, 코드 0건)
### 481차 — 장전 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
### 481차 후속 — 장중 점검 (MW0601, 2026-08-20 · 분석만, 코드 0건)
```

미완료 체크박스 **1530건** (끝에서 30건)
```
- [ ] **`raw_data.db`(508MB)·`shap_tracker.db`(132MB) 보관정책 부재** — 별도 조사
- [ ] **F-2 (P1, 최우선 · 코드 변경 없음) `ofi_norm` 분포 프로브 실행** —
- [ ] **F-1 (P1) 프리장 수급 미측정 플래그 + 스케일러 제외 섀도** —
- [ ] **F-3 (P2, 0819 2-1 이월 · 2일차) CybosProbe CoInitialize + 실패사유 3분류** —
- [ ] **F-4 (P2, 0819 F-1 이월 · 7일차) 수집기 브랜치 스코프 분리** —
- [ ] **F-5 (P2) 수집기 CRLF 내성 + §7 국면 스코프** —
- [ ] **G-1 (이번 주) EOD 체인 프로세스 독립성 명문화 + 역방향 계측** —
- [ ] **G-2 (이번 주, F-5와 병합) 개장 첫봉 z 프로파일 상설 계측** —
- [ ] **G-3 (다음 주, F-2 결과 확인 후) CORE 스케일러 폴백률 일일 집계** —
- [ ] **O-1 (장중) `[IntradayRegime]` 종일 전이 횟수** — 09:01:59 `NORMAL → CRASH
- [ ] **O-2 (장중·장후) `institution_futures_net` max_z 재출현 여부** — 09:00 봉 한정인지,
- [ ] **O-3 (장후) `institution_futures_net` σ_floor 0.15 실적용 여부** —
- [ ] **O-4 (장후) `ofi_norm` identity 종일 발동률** — 90% 이상이면 **P-4 2일차 확정**,
- [ ] **O-5 (장후) FZ-11 워치독 오탐 0건** — `heartbeat_MW0601_20260820.json` /
- [ ] **O-6 (장후) 로컬 7커밋 push** — `origin/v9-dev` 대비 ahead 7. MW0602가 480차 후속을
- [ ] **F-1 (P1, 장후) 수집기 §5 부분청산 레그 합산** —
- [ ] **F-2 (P2, 장후 · F-1과 같은 커밋 가능) 스킬 참조문서를 CLAUDE.md 461·474차에 정합** —
- [ ] **F-3 (P1, 장후 · 조사만 — 코드 변경 없음) CB③-P4 판정 입력 결정** —
- [ ] **G-1 (이번 주, 선행 F-1) 포지션 조립기를 수집기 1급 구조로 승격** —
- [ ] **G-2 (이번 주, F-1과 같은 커밋 가능) `[Sizer]` 배수 상수화 감시** —
- [ ] **G-3 (다음 주, 선행 O-9) CB③ 유효시간 계측** —
- [ ] **[실전전환기준 ⑥ 문언 확장]** — *"30m 재도입 또는 CB③ 기준 호라이즌 교체"* 에
- [ ] **[계측 4원칙 ① 적용범위]** — "점검 수집기 자신에게도 적용"을 명시.
- [ ] **[16] `chase_foreign_combo_watch` 표본 갱신 보고** — 오늘 A급 패 1건 추가
- [ ] **O-7 (장후) 15:10 강제청산 경로** — 12:31 현재 FLAT이라 **미발생이 정상**.
- [ ] **O-8 (장후) 잔고 델타 잔차 27,034원** — 레그 합 -269,884 vs 잔고 델타 -296,918.
- [ ] **O-9 (장후) `[CB③]` acc30m 종일 리셋/스킵 횟수와 ready 구간** —
- [ ] **O-10 (장후) `_tick_header` 블로킹 종일 분포** — 오전 최대 4,750ms(임계의 95%),
- [ ] **O-11 (장후) `ConstOut ['3m']` 종일 횟수** — 오전 4회(08-19와 동수).
- [ ] **O-12 (08-21) 등급 인플레 R-후보 3일차** — 오늘 2일차 누적 3건 승1 패2,
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
C"` 만 본다 → **등급 인플레가 P4의 유일 사정권을 비운다.**
      장후 DB로 `trades.raw_grade='C' AND grade IN ('A','B')` 건수·손익 집계
      (`_entry_raw_grade`는 `main.py:9162`에 이미 존재).
      ⚠ 표본 미달이면 **판정하지 않는다**(313차). 문턱 인하 금지(458차 D6).
      ⚠ P4 입력 변경은 **매매 정책 변경** → 주간회의 + 섀도 계측 선행.

#### 고도화

- [ ] **G-1 (이번 주, 선행 F-1) 포지션 조립기를 수집기 1급 구조로 승격** —
      `assemble_positions(lines) -> List[Position]` 신설(진입 → 부분청산 n → `[청산 완료]`).
      §5의 손익·승률·수량·보유시간 집계가 **그 함수만** 쓰게 하고 레그 표는 하단 참고로.
      미종결 포지션은 `open=True`(장중 점검 안전).
      **왜**: 같은 오류가 두 번 났다 — 417차 이벤트 단위 사이징 통계 무효화, 그리고 오늘.
      **기대효과**: §5 포지션 합계 vs `[청산 완료]` PnL 합 **오차 0**.
- [ ] **G-2 (이번 주, F-1과 같은 커밋 가능) `[Sizer]` 배수 상수화 감시** —
      오늘 사이저 9건의 배수 조합이 **전부 동일**(`conf=0.6 regime=1.0 safe=1.00`),
      `[ConfShadow: 1.0→2계약]` 3건이 "0.6이 아니었다면 달랐다"를 명시.
      §5에 `conf: {0.6×9} (unique=1)` 한 줄 추가, **3거래일 연속 unique=1 → §11 적신호**.
      ⚠ **계측만이다** — 배수 변경은 실전 전환 기준 ⑧ 소관, `MAX_CONTRACTS=3`은
      431차 배포분(**재상정 금지**).
- [ ] **G-3 (다음 주, 선행 O-9) CB③ 유효시간 계측** —
      오늘 `[CB③] acc30m 버퍼 리셋` 판단 4회(09:37 0건·10:11 14건·11:41 28건 = 기아방지
      스킵 / **11:02 실제 리셋** `쿨다운=15샘플`). **CB③이 오늘 몇 분간 판정 가능
      상태였는지 아무 데도 기록되지 않는다.**
      `[CB③]` 로그에 `n=28 ready=False` 항상 병기(계측 4원칙 ②·④) +
      §5에 `CB③ ready 분 / 장중 분`.
      **왜**: FP-CRITICAL이 "저장 함수 미호출로 2개월 PSI=0.0"이었던 것과 같은 형태의 침묵.
      ⚠ 선행 O-9 없이 비율만 자동화하면 481차 G-3이 경고한 "숫자는 있는데 뭘 할지 모르는 채널".

#### 주간회의 상정

- [ ] **[실전전환기준 ⑥ 문언 확장]** — *"30m 재도입 또는 CB③ 기준 호라이즌 교체"* 에
      **"+ CB③-P4의 판정 입력(원시 등급 vs 최종 등급)을 함께 정할 것"** 추가.
      **근거**: 지금 상태로 플래그만 True로 되돌려도 오늘 같은 A급(원시C) 경로는 그대로 통과한다.
- [ ] **[계측 4원칙 ① 적용범위]** — "점검 수집기 자신에게도 적용"을 명시.
      원칙을 담은 문서를 만든 도구가 그 원칙을 어기고 있었다(F-1).
- [ ] **[16] `chase_foreign_combo_watch` 표본 갱신 보고** — 오늘 A급 패 1건 추가
      (-269,884원). **PC 부호 역전 미해소 → 449차 확정 결정 "활성화 금지 유지" 그대로.**

#### 다음 국면(장후) 관측 항목

- [ ] **O-7 (장후) 15:10 강제청산 경로** — 12:31 현재 FLAT이라 **미발생이 정상**.
      `[SchedForceExit] … 안전망 발동`(ERROR)이 뜨면 P0.
- [ ] **O-8 (장후) 잔고 델타 잔차 27,034원** — 레그 합 -269,884 vs 잔고 델타 -296,918.
      `trades` 포지션 합과 대사.
- [ ] **O-9 (장후) `[CB③]` acc30m 종일 리셋/스킵 횟수와 ready 구간** —
      ready가 장중의 50% 미만이면 G-3 착수.
- [ ] **O-10 (장후) `_tick_header` 블로킹 종일 분포** — 오전 최대 4,750ms(임계의 95%),
      4초대 6건. **5,000ms 초과 1건이라도 나오면 CB⑤ 실발동 — 사유 추적 필수.**
- [ ] **O-11 (장후) `ConstOut ['3m']` 종일 횟수** — 오전 4회(08-19와 동수).
      **6회 이상이면 08-14 F-8 재발 강도 상향.**
- [ ] **O-12 (08-21) 등급 인플레 R-후보 3일차** — 오늘 2일차 누적 3건 승1 패2,
      이틀 연속 패 쪽이 당일 손실의 전부. **5거래일 전까지 확정 결론 금지(313차).**

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

### `data/heartbeat_MW0601_20260820.json` — 243B · 08-20 15:40:16
```json
{
 "pid": 13140,
 "written_at": "2026-08-20T15:40:16",
 "beat_epoch": 1787208013.130496,
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

### `docs/정기점검/매일점검` — 55개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260820-점검리포트-intra.md` | 29.7KB | 08-20 12:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_intra.md` | 61.3KB | 08-20 12:27 |
| `docs/정기점검/매일점검/MW0601-20260820-점검리포트-pre.md` | 36.8KB | 08-20 09:15 |
| `docs/정기점검/매일점검/evidence_MW0601-20260820_pre.md` | 49.0KB | 08-20 09:01 |
| `docs/정기점검/매일점검/MW0601-20260819-미종료-딥다이브.md` | 26.0KB | 08-19 17:07 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-post.md` | 42.9KB | 08-19 16:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20260819_post.md` | 63.9KB | 08-19 16:22 |
| `docs/정기점검/매일점검/MW0601-20260819-점검리포트-intra.md` | 33.7KB | 08-19 12:42 |

### `docs/정기점검/금요일점검` — 53개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.json` | 7.6KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/MW0601/profit_guard_latch_20260818.md` | 3.8KB | 08-18 22:58 |
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260814.md` | 163.4KB | 08-14 15:49 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
7. 청산 4건 중 하드스톱·손절 계열 **4건(100%)** — 손절 준수율 확인 필요
8. 메인 스레드 블로킹 5초 초과 **4건** (최대 8375ms) — `CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인
9. `logs/20260820_WARN.log`: **ConstOut** 6건(표본)
10. `logs/20260820_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260820_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260820_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260820_LEARNING.log`: **축퇴** 8건(표본)
14. 미커밋 변경 461건
15. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260820*.log` (Windows) / `grep 강제청산 logs/*20260820*.log`*