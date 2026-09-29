# 미륵이 증거 다이제스트 — 2026-09-28 / POST

- 생성 2026-09-28 16:18:05 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01kzgbmgxfhmwmka7b1octsu/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260928` · `2026-09-28` · `260928` · `0928`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **29개** 파일 · 29개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260928.txt` | 28B | 09-28 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20260928.txt` | 28B | 09-28 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260928.txt` | 233B | 09-28 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20260928.log` | 1.3KB | 09-28 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20260928.log` | 217B | 09-28 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20260928.json` | 245B | 09-28 15:46 |
| `launcher_{DATE}_084001_3298.log` | 1 | `logs/Mireuk_batch/launcher_20260928_084001_3298.log` | 1.9MB | 09-28 15:47 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20260928.log` | 3.6KB | 09-28 13:22 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20260928.log` | 1.0KB | 09-28 16:10 |
| `position_state.json.gen_{DATE}_094002` | 1 | `data/position_state.json.gen_20260928_094002` | 1.5KB | 09-28 09:40 |
| `position_state.json.gen_{DATE}_094020` | 1 | `data/position_state.json.gen_20260928_094020` | 1.5KB | 09-28 09:40 |
| `position_state.json.gen_{DATE}_094301` | 1 | `data/position_state.json.gen_20260928_094301` | 1.6KB | 09-28 09:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260928.log` | 21.8KB | 09-28 15:53 |
| `retrain_intraday_{DATE}_104801.log` | 1 | `logs/retrain_intraday_20260928_104801.log` | 3.2KB | 09-28 10:48 |
| `retrain_intraday_{DATE}_132101.log` | 1 | `logs/retrain_intraday_20260928_132101.log` | 3.2KB | 09-28 13:21 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20260928.txt` | 43B | 09-28 15:47 |
| `strategy_report_{DATE}_154017.txt` | 1 | `data/daily_reports/strategy_report_20260928_154017.txt` | 2.4KB | 09-28 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260928_DATA.log` | 439.7KB | 09-28 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260928_DEBUG.log` | 233.8KB | 09-28 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260928_HEALTH.log` | 4.1KB | 09-28 15:05 |
| `{DATE}_HOGA.log` | 1 | `logs/20260928_HOGA.log` | 49.1MB | 09-28 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260928_LEARNING.log` | 299.4KB | 09-28 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260928_MICRO.log` | 927.6KB | 09-28 15:40 |
| `{DATE}_PROBE.log` | 1 | `logs/20260928_PROBE.log` | 94.6KB | 09-28 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20260928_REGULAR_COLLECT.log` | 6.6KB | 09-28 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260928_SIGNAL.log` | 492.9KB | 09-28 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260928_SYSTEM.log` | 950.6KB | 09-28 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20260928_TRADE.log` | 9.1KB | 09-28 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260928_WARN.log` | 320.2KB | 09-28 15:46 |

## 2. 코드·커밋 상태

- HEAD `c2d5eee` · 브랜치 `v9-dev` · 미커밋 6건 · 실질 변경 **미측정**(git diff 실패) · 인덱스락 없음
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md
?? docs/정기점검/매일점검/MW0601-20260928-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md
```

**당일(2026-09-28) 커밋**
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
c2d5eee [MW0601] 631차: Claude 앱 — 19:20 업데이트 창이 VS Code Claude Code 까지 죽이던 것 수정 + 절전 해제 시 앱 자동 복구
91f5afe [MW0601] 631차: PC 종료→절전 해제→Cybos Plus→미륵이 실전 흐름 확인 기록 (1차 로그인 37초·DB 초기화 0.4초)
ddcddef [MW0601] 631차 딥다이브2 후속: Cybos 연결 확인을 매번 새 프로세스로 — 자동로그인이 성공을 실패로 오판해 세션을 끊던 원인
b7b274b [MW0601] 631차 딥다이브2: 15:58 기동 실패 — 금요일 종료 작업이 최대 절전이라 Cybos 세션만 끊긴 채 CpStart 생존
da5a604 [MW0601] 631차 후속: GP 분석 캐시를 GP_test/ 로 분리 — 파일은 남기고 미추적 목록에서만 숨김
3d68065 [MW0601] 631차 후속: git 밖 작업 코드 6개 — 섀도 게이트·피터 수집기·롤 정책 대조 (라이브 미배선)
4575a77 [MW0601] 631차 후속: 미커밋 기록 일괄 — 매일점검 리포트·증거, 주간 리포트 0923, GP 연구 문서
ddf376c [MW0601] 631차 후속: data/peter_feed/ 무시 + 송신 도구 git add -f
b4f7127 [MW0601] 631차 기록: 0926 휴장일 점검 리포트 · 딥다이브 · 구현 결과 + dev_memory
44c0a71 [MW0601] 631차 F-4: 증거 수집기 휴장일 인식 — 거래일 전제 적신호 9종 생략
bc81108 [MW0601] 631차 F-3·F-3b: 런처는 자동로그인이 끝나고 연결이 10초 유지된 뒤 출발
4aecc7f [MW0601] 631차 F-6·F-7·F-8: 자동로그인 재시도가 살아 있는 세션을 죽이지 않게
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

### 차단 게이트 전수 인벤토리 — 38개 중 **9개 꺼짐**

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
| `OPTION_BOOK_ENABLED` | True | — |
| `SHINDONG_ENABLED` | True | — |
| `SHINDONG_RUNNER_SHADOW_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260928_HOGA.log` 49.1MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260928.txt`** — 28B · 09-28 15:40:17
```
2026-09-28T15:40:17.688179
```

**`data/daily_close_started_20260928.txt`** — 28B · 09-28 15:40:11
```
2026-09-28T15:40:11.144646
```

**`data/daily_reports/strategy_report_20260928_154017.txt`** — 2.4KB · 09-28 15:40:17
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-09-28 15:40
========================================================
  버전    : v1.0  (87일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-2.08  MDD(자본대비)=29.9%
  당일      : WR=100.0%  PF=999.00
  롤링20일: 누적 -6733604원  Sh=-2.08  MDD(자본대비)=29.9%  MDD(peak대비)=2140.4%
  당일손익 : broker(gross) +256,000원  수수료 43,435원  net +212,565원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.001 (CLEAR)
  PSI/feat: cvd_delta=0.001  ofi_pressure=0.000  vwap_position=0.013
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 +368,324원  승률 75.0%  합계 +7,366,484원
  등급별 순EV(30일): A=+156,374원(43건,승63%)  BROKER=-2,574,591원(4건,승50%)  MANUAL=-27,752원(139건,승46%)
  호라이즌별 순EV(30일): 1m=-62원(9건)  3m=+1,985원(29건)  5m=-84,845원(3건)  ?=-49,892원(145건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 23분  5일평균 24분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 32.9pt(5일평균 21.6pt)  1분평균변동 0.64pt(5일평균 0.54pt)
--------------------------------------------------------
  진입 퍼널(2026-09-28, 총 370분):
    FLAT 226 → conf미달 111 → CoherenceGate 10 → 게이트차단 20 → 후보 3 → 진입 2
    게이트별: 시가갭(OPEN_VOLATILE)=12  포지션보유중(평가생략)=2  체크리스트항목미달=2  콜드스타트/기타(조건부구간)=1  쿨다운=1  모드필터=1  ATR변동성=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 1건
      └ 상세: JointGateBlock=1
      └ JointGateBlock 1건 (무정보폴백 0건 = 0.0%) [표본 19건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260928.txt`** — 233B · 09-28 15:53:27
```
completed: 2026-09-28 15:53:27
rows: 17305
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 22.9
t_retrain_s: 180.0
t_total_s: 203.5
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20260928.txt`** — 43B · 09-28 15:47:14
```
auto_shutdown
2026-09-28T15:47:14.679296
```

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20260928_132101.log`, `20260928_MICRO.log`, `20260928_DATA.log`, `20260928_PROBE.log`, `launcher_20260928_084001_3298.log`, `20260928_DEBUG.log`, `20260928_REGULAR_COLLECT.log`, `mainstall_traceback_20260928.log`_

### `logs/20260928_TRADE.log` — 9.1KB · 63행 · 최종 15:40:14

- 형식 평문 · 시각 인식 63행 · INFO=63

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:41:02 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-09-28 08:41:08 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-09-28 09:34:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,731,078) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-28 09:34:00 [INFO] TRADE: [진입체크] SHORT→SHORT 2계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore✅ prev✅ time✅ risk✅ chas❌ coun✅ | conf=50.2%
2026-09-28 09:34:00 [INFO] TRADE: [Position] 진입 SHORT 2계약 @ 1107.84 | 손절=1110.18 1차=1107.06(×0.42) 2차=1105.50 horizon=3m hurst=mean-revert
  …
2026-09-28 10:20:01 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,943,669) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-28 11:35:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,943,669) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-28 11:35:00 [INFO] TRADE: [JointGateBlock 차단] SHORT 2계약 A급 (meta=0.59 tox=0.70 joint=0.412)
2026-09-28 13:08:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=35,943,669) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1)
2026-09-28 15:40:14 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×63

**컴포넌트 상위 15** — `Sizer`×18, `Chejan`×14, `Position`×9, `주문요청`×6, `ProfitGuard`×2, `진입체크`×2, `체결진입`×2, `체결진입보정`×2, `TickTP1`×2, `TP1 부분청산`×2, `청산 완료`×2, `모드필터 차단`×1, `JointGateBlock 차단`×1

### `logs/20260928_WARN.log` — 320.2KB · 1498행 · 최종 15:46:35

- 형식 평문 · 시각 인식 1491행 · WARNING=1491, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-09-28 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-09-28 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 187ms account=333044256
2026-09-28 08:41:11 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-09-28 08:41:11 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-09-28 15:46:11 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-28 09:40:00 cols=['open'] existing_source=rt
2026-09-28 15:46:11 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-28 09:47:00 cols=['open'] existing_source=rt
2026-09-28 15:46:11 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=410 inserted=1 open_fixed=1 mismatch=13
2026-09-28 15:46:13 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3328ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2231 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=3328 band=INFO since_pipe_s=2232.8
2026-09-28 15:46:35 [WARNING] SYSTEM: [LiveDBG] DynMCPanel.refresh slow 250ms
```

</details>

**WARNING — 태그 32종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1103 | 08:59:36 | 13:35:48 | paintEvent slow 55.9ms | size=1955x1124 candles=15 grid=28.6 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=25.4 cross=0.0 | slow_cnt=1 total_cnt=4 overlay_cnt=1 |
| `LiveDBG` | 152 | 08:41:11 | 15:46:35 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 77 | 08:41:21 | 15:30:11 | 그리기 73.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 874x1001 |
| `Health` | 14 | 09:00:02 | 15:04:00 | level=WARNING degraded=OFF | latency=2296ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |
| `ChejanFlow` | 14 | 09:34:01 | 09:43:01 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056A' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1139' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:34:00.782' | positi… |
| `ChejanMatch` | 14 | 09:34:01 | 09:43:01 | order_no='1139' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1139 reason=진입 req_at=09:34:00.782' | pending_matched=True |
| `ScalerRefresh` | 13 | 09:12:00 | 14:43:00 | 5분 누적 수익률 -0.502% (임계 ±0.393%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SessionBackfill` | 12 | 08:41:42 | 15:46:11 | OHLCV 불일치 ts=2026-09-23 09:44:00 cols=['open'] existing_source=rt |
| `PendingOrder` | 12 | 09:34:00 | 09:43:01 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1107.84, 'reason': '진입', 'hint_source': '', 'atr': 1.8386, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `PipePerf` | 10 | 09:00:02 | 13:22:04 | total=2296ms | S0=3ms S1=38ms S2=0ms S3=0ms S4=149ms S5=1671ms S6=375ms S7=47ms S8=13ms |
| `CB⑤` | 10 | 09:00:02 | 13:22:04 | 파이프라인 2296ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `CB③-P4` | 10 | 11:15:00 | 14:14:00 | acc30m 단계 전환: NORMAL → RESTRICTED (acc=20.0%) |

**채널** — `SYSTEM`×1477, `HEALTH`×14

**컴포넌트 상위 15** — `ChartDBG`×1103, `LiveDBG`×152, `OptionFlowChart`×77, `Health`×14, `ChejanFlow`×14, `ChejanMatch`×14, `ScalerRefresh`×13, `SessionBackfill`×12, `PendingOrder`×12, `PipePerf`×10, `CB⑤`×10, `CB③-P4`×10, `SHAP`×10, `-`×7, `EntryFillFlow`×4

### `logs/20260928_SYSTEM.log` — 950.6KB · 6445행 · 최종 15:47:14

- 형식 평문 · 시각 인식 6424행 · INFO=6424, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:40:48 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=19608 | 행감지=30s all_threads=True
2026-09-28 08:40:48 [INFO] SYSTEM: [DBInit] 합계 0.42s | predictions=0.04s trades=0.20s daily_stats=0.01s shap=0.01s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-09-28 08:40:48 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-09-28 08:40:48 [INFO] SYSTEM: [System] 미륵이 초기화
2026-09-28 08:40:48 [INFO] SYSTEM: 미륵이 초기화
  …
2026-09-28 15:46:11 [INFO] SYSTEM: [SessionBackfill] 2026-09-28~2026-09-28 chart=411 existing=410 inserted=1 open_fixed=1 mismatch=13
2026-09-28 15:46:11 [INFO] SYSTEM: [BarGap] 당일 확정(2026-09-28) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-09-28 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-09-28 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-09-28 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6424

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×925, `PumpGuard`×768, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `System`×100, `MicroRegime`×91, `OptionChain`×81, `OptionBook`×79, `RegimeFingerprint`×69, `BalanceUI`×29

### `logs/20260928_SIGNAL.log` — 492.9KB · 4406행 · 최종 15:40:14

- 형식 평문 · 시각 인식 4406행 · WARNING=1425, INFO=2981

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.434
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.434
  …
2026-09-28 15:10:03 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-09-28 15:40:14 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-09-28 15:40:14 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 0분(0.0%) / DN 146분(39.5%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-09-28 15:40:14 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-09-28 age=34m extreme=396 refresh=34 grade_x=111 cb3=0
2026-09-28 15:40:14 [INFO] SIGNAL: [ModelHealth] date=2026-09-28 앙상블유효가동률=74.1% | 파이프라인 370분 | ConstOut 9회/12분 {"3m": {"events": 6, "minutes": 9}, "5m": {"events": 3, "minutes": 3}} | WeightCollapse 84분 | 장중재학습 2회 | CB③ ready 185분/370분 (50%) (리셋 1회, 표본손실 30건)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 870 | 09:00:02 | 14:43:01 | 1m 'macro_us10y_chg' scale=0.1404 → floor=0.25 적용 (z-score 폭발 방지) |
| `Model` | 168 | 09:00:00 | 14:29:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 162 | 09:00:00 | 14:29:00 | ts=08:59 horizon=1m age=1m max_z=+7.74(institution_futures_net) extreme=2 adj=2 |
| `Checklist` | 120 | 09:06:00 | 15:04:00 | 신뢰도 미달 34.2% < 40.4% → 강제 X등급 |
| `WeightCollapse` | 84 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 12 | 08:45:12 | 08:48:00 | 1m CORE 'ofi_norm' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 9 | 10:20:01 | 14:50:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |

**채널** — `SIGNAL`×4406

**컴포넌트 상위 15** — `ScalerFloor`×888, `SIGNAL`×740, `Ensemble`×376, `FQAdj`×359, `ZeroDiag`×348, `MetaGate`×291, `Model`×186, `Checklist`×164, `ScalerMonitor`×163, `ATR-Horizon`×133, `ToxicityGate`×104, `MicroRegime`×91, `차단`×90, `WeightCollapse`×84, `InstabilityGate`×77

### `logs/20260928_LEARNING.log` — 299.4KB · 2916행 · 최종 15:40:14

- 형식 평문 · 시각 인식 2916행 · WARNING=167, INFO=2749

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 08:40:50 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00131 auc=0.530 out_max=0.3722 (기준 auc<0.53 and span<0.020, 기저율=0.3714 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3017 < conf_floor=0.3300 (span=0.00316 auc=0.566 out_max=0.3017, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-09-28 08:40:53 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00146 auc=0.532 out_max=0.3554 (n=110) → 보정 재적용
2026-09-28 08:40:53 [INFO] LEARNING: [Calibration:30m] 도달불가 해소 — out_max=0.3434 < conf_floor=0.3300 (n=85) → 보정 재적용
  …
2026-09-28 15:40:14 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-09-28 15:40:14 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-28 15:40:14 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-09-28 15:40:14 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-09-28 15:40:14 [INFO] LEARNING: [Sigma] EOD sigma_20=0.06124% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 54 | 08:40:53 | 14:25:00 | 축퇴 감지 — span=0.00131 auc=0.530 out_max=0.3722 (기준 auc<0.53 and span<0.020, 기저율=0.3714 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:30m` | 52 | 08:40:53 | 14:15:00 | 하한 도달불가 — out_max=0.3017 < conf_floor=0.3300 (span=0.00316 auc=0.566 out_max=0.3017, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 22 | 08:40:53 | 13:57:00 | 하한 도달불가 — out_max=0.3129 < conf_floor=0.3300 (span=0.00067 auc=0.553 out_max=0.3129, 기저율=0.3125 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 16 | 08:40:54 | 13:49:00 | 축퇴 감지 — span=0.00083 auc=0.525 out_max=0.4100 (기준 auc<0.53 and span<0.020, 기저율=0.4095 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 11 | 08:40:53 | 14:00:00 | 축퇴 감지 — span=0.00119 auc=0.490 out_max=0.3631 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 6 | 08:40:57 | 08:41:01 | 축퇴 감지 — span=0.00128 auc=0.529 out_max=0.3356 (기준 auc<0.53 and span<0.020, 기저율=0.3350 n=200) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:ensemble` | 4 | 08:41:02 | 13:55:00 | 복원한 보정기가 축퇴 상태 — span=0.00163 auc=0.497 out_max=0.3407 (n=1184) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Retrain` | 1 | 15:40:14 | 15:40:14 | DB pruning 실패: database table is locked |
| `DriftAdjuster` | 1 | 15:40:14 | 15:40:14 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 14일) |

**채널** — `LEARNING`×2916

**컴포넌트 상위 15** — `LEARNING`×1219, `SGD`×370, `sigma`×357, `Bias⚠`×275, `Bias`×141, `Calibration:1m`×107, `Calibration:30m`×102, `MetaConf`×78, `OnlineLearner`×54, `Calibration:3m`×43, `ScalerWarmup`×39, `Calibration:10m`×31, `Calibration:5m`×22, `BiasReset`×22, `Calibration:15m`×12

### `logs/20260928_HEALTH.log` — 4.1KB · 29행 · 최종 15:05:02

- 형식 평문 · 시각 인식 29행 · WARNING=14, INFO=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 09:00:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2296ms | quality=1.00 | cache_age=43s | exceptions_10m=0
2026-09-28 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=613ms | quality=1.00 | cache_age=101s | exceptions_10m=0
2026-09-28 09:02:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1021ms | quality=0.88 | cache_age=162s | exceptions_10m=0
2026-09-28 09:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=376ms | quality=1.00 | cache_age=35s | exceptions_10m=0
2026-09-28 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 343ms (표본 20분)
  …
2026-09-28 13:39:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=376ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-28 14:30:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=626ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-09-28 14:31:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=343ms | quality=1.00 | cache_age=58s | exceptions_10m=0
2026-09-28 15:04:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=355ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-09-28 15:05:02 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=395ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 14 | 09:00:02 | 15:04:00 | level=WARNING degraded=OFF | latency=2296ms | quality=1.00 | cache_age=43s | exceptions_10m=0 |

**채널** — `HEALTH`×29

**컴포넌트 상위 15** — `Health`×28, `HealthTrend`×1

### `logs/retrain_eod_20260928.log` — 21.8KB · 145행 · 최종 15:53:27

- 형식 평문 · 시각 인식 145행 · WARNING=14, INFO=131

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 15:50:03,001 [INFO] EOD_RETRAIN: =======================================================
2026-09-28 15:50:03,001 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-09-28 15:50:03,002 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-09-28 15:50:03,002 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-09-28 15:50:03,002 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-09-28 15:53:27,653 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0630 → floor=0.15 적용 (z-score 폭발 방지)
2026-09-28 15:53:27,654 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0979 → floor=0.20 적용 (z-score 폭발 방지)
2026-09-28 15:53:27,657 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-09-28 15:53:27,661 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-09-28 15:53:27,662 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:37 | 15:52:39 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1500봉(81%)이 현행 학습구간 (현행 cutoff=2026-09-23 14:38:00 ≥ 홀드아웃 시작=2026-09-17 12:13:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-09-23 14:38 >= holdout_start=2026-09-17 12:13 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-09-23 … |
| `GuardGhost` | 4 | 15:50:53 | 15:51:09 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-09-28 10:17:00까지)인데 acc.txt=0.4158는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-09-28 | 최신 2026-09-23 · 기준 5거래일. 복구: python scripts/collect_regular_futures.py --from 20260928 --to 20260928 |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 23908/44832 제외 (418차 결정 1) — 남은 20924행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/20924행 제외 (559차 P1'-2) — 남은 19478행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:27 | 15:53:27 | 백필 0행 제외 — 필터가 무효일 수 있다. 17305행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×66, `SIGNAL`×43, `EOD_RETRAIN`×26, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×36, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `GuardGhost`×4, `RegimeFingerprint`×4, `WaitDC`×2

### `logs/retrain_intraday_20260928_104801.log` — 3.2KB · 24행 · 최종 10:48:24

- 형식 평문 · 시각 인식 24행 · WARNING=2, INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-28 10:48:01,570 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-28 10:48:01,570 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-28 10:48:01,571 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-28 10:48:01,571 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-09-28 10:48:01,571 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_45cd1c22.json
  …
2026-09-28 10:48:24,466 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-28 10:48:24,467 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-28 10:48:24,468 [INFO] LEARNING: [Retrain] 완료 | 19.6초 | 성공=1/1 호라이즌
2026-09-28 10:48:24,468 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 22.9s 데이터=4800행
2026-09-28 10:48:24,470 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_45cd1c22.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:48:15 | 10:48:15 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 24180/44843 제외 (418차 결정 1) — 남은 20663행 |
| `UnitMismatch` | 1 | 10:48:15 | 10:48:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/20663행 제외 (559차 P1'-2) — 남은 19217행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +212565원
════════════════════════════════════════════════════
2026-09-28 15:46:11 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-28 09:34:00 cols=['open'] existing_source=rt
2026-09-28 15:46:11 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-09-28 09:38:00 cols=['open'] existing_source=rt
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) — **엔진** | 2 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 2 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 2 |
| 차단(`[차단]`) | 90 |
| 사이저 호출(`[Sizer]`) | 18 |

### 포지션 2건 · 승 2 (100%) · 합계 +5.12pt (+212,566원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:34:00 | 엔진 | SHORT | 2 | 3m | 2 | +1.32 | +44,266 | 하드스톱 |
| 09:40:01 | 엔진 | SHORT | 2 | 3m | 2 | +3.80 | +168,300 | TP2(전량) |

**청산 레그 4행** (부분청산 2 · 전량청산 2)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:36:34 | 부분 | 1 | +0.81 | +29,633 | TP1 부분청산 33% |
| 09:37:01 | 전량 | 1 | +0.51 | +14,633 | 하드스톱 |
| 09:40:20 | 부분 | 1 | +0.98 | +38,150 | TP1 부분청산 33% |
| 09:43:01 | 전량 | 1 | +2.82 | +130,150 | TP2(전량) |

**청산 사유 분포(레그 단위)** — `TP1 부분청산 33%`×2, `하드스톱`×1, `TP2(전량)`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 1/2건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +212,566 = 포지션합 +212,566 → OK · `[청산 완료]` 2건 = 조립 포지션 2건 → OK

### CB③ 판정 가능 시간 — **185분 / 370분 (50%)**

acc30m 버퍼 리셋 1회 · 그때 버린 표본 30건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 09:34:00 | SHORT | 2 | 1107.84 | 3m | mean-revert |
| 09:40:01 | SHORT | 2 | 1106.34 | 3m | mean-revert |

계약수 분포 — 2계약×2

등급 분포 — `A급(원시C)`×2

**진입한 건들의 체크리스트 미통과 항목** — `chas`×2, `ofi`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **2계약**×3, **3계약**×15

실제 진입 계약수 — **2계약**×2

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×18

### 차단 사유 90건 · 58종

| 건수 | 사유 |
|---|---|
| 28 | 등급X — 미통과 항목: 2_confidence |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | ATR 0.77pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.86pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 2 | ATR 0.76pt < 1.0pt — 변동성 부족 (휩쏘 위험) |
| 1 | 청산 후 쿨다운 — 59초 후 재진입 가능 |
| 1 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 1 | 청산 후 쿨다운 — 60초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 0초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 7.8pt > ATR×5.0=7.0pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=6.9pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=7.0pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.8pt > ATR×5.0=7.2pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.1pt > ATR×5.0=7.1pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.5pt > ATR×5.0=7.5pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 9.3pt > ATR×5.0=7.8pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 10.5pt > ATR×5.0=7.8pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.2pt > ATR×5.0=8.2pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.1pt > ATR×5.0=8.2pt (시가=1112.40 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.6pt > ATR×5.0=7.9pt (시가=1112.40 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×28, `3_vwap`×2, `6_foreign`×2, `4_cvd`×1, `7_prev_bar`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 21건 · 최대 5187ms · 5초 초과 1건

상위 — 5187ms, 4500ms, 4219ms, 3656ms, 3328ms, 3156ms, 3047ms, 2890ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 13:22:04 | 5187ms | 4486ms | **701ms (14%)** |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260928_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:16 2026-09-28 15:40:16 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 23분 < 하한 25분 — 최근 5거래일 평균 24분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 370분
--- ConstOut ×2(표본)
10:47:00 2026-09-28 10:47:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(3m=0.4675)
13:20:01 2026-09-28 13:20:01 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(5m=0.3801)
--- [ExitCooldown] ×5(표본)
09:37:01 2026-09-28 09:37:01 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 09:39:01)
09:37:01 2026-09-28 09:37:01 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 09:39:01)
09:43:01 2026-09-28 09:43:01 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 09:45:01)
09:43:01 2026-09-28 09:43:01 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 09:45:01)
--- [SHAP] 슬로우 ×8(표본)
11:35:01 2026-09-28 11:35:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1013ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:43:01 2026-09-28 11:43:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 953ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:51:01 2026-09-28 11:51:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 947ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:05:01 2026-09-28 12:05:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 972ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:14 2026-09-28 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3656ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3656 band=INFO since_pipe_s=NA
08:59:35 2026-09-28 08:59:35 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3156ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3156 band=INFO since_pipe_s=NA
09:00:04 2026-09-28 09:00:04 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4219ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4219 band=INFO since_pipe_s=0.1
09:01:02 2026-09-28 09:01:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2344ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2344 band=INFO since_pipe_s=0.2
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260928_SYSTEM.log`
```
--- ConstOut ×8(표본)
10:20:01 2026-09-28 10:20:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4964) | 앙상블 제외는 유지
10:47:00 2026-09-28 10:47:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 10:49:00 (const_output)
10:47:00 2026-09-28 10:47:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
10:47:01 2026-09-28 10:47:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=331ms fit=50ms total=385ms
--- HALT ×1(표본)
15:40:14 2026-09-28 15:40:14 [INFO] SYSTEM: [CB③계측] 조건성립 179분 / 판정가능 185분 / 파이프라인 370분 · 그 창 진입 1포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-09-28 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.000 level=0 (heartbeat)
09:05:00 2026-09-28 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.000 level=0 (heartbeat)
09:11:00 2026-09-28 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.000 level=0 (heartbeat)
09:17:00 2026-09-28 09:17:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.000 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:14 2026-09-28 15:40:14 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:14 2026-09-28 15:40:14 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:14 2026-09-28 15:40:14 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 1레그 / 1포지션 중 TP 이벤트 대응 1 · 단일계약 보호전환(설계) 0 · 미대응 0
--- [SchedForceExit] ×1(표본)
15:11:11 2026-09-28 15:11:11 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:17 2026-09-28 15:40:17 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-09-28 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:17 2026-09-28 15:40:17 [INFO] SYSTEM: [Notify] ℹ️ [15:40:17] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:17 2026-09-28 15:40:17 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 402초
15:40:17 2026-09-28 15:40:17 [INFO] SYSTEM: 자동 종료 예약 — 417초 후 Qt 이벤트 루프 종료
```

### `logs/20260928_SIGNAL.log`
```
--- ConstOut ×8(표본)
10:20:01 2026-09-28 10:20:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0370 dir=-1)
10:20:01 2026-09-28 10:20:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:20:01 2026-09-28 10:20:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
10:21:00 2026-09-28 10:21:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
--- WeightCollapse ×8(표본)
09:07:00 2026-09-28 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-09-28 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=74.6% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-09-28 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=58.7% grade=X regime=RISK_ON [WeightCollapse]
09:16:00 2026-09-28 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=41.3% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.434
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.451
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.429
08:40:45 2026-09-28 08:40:45 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.425
--- 안전망 ×8(표본)
09:07:00 2026-09-28 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-09-28 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-09-28 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-09-28 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260928_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:53 2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00131 auc=0.530 out_max=0.3722 (기준 auc<0.53 and span<0.020, 기저율=0.3714 n=105) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:53 2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3017 < conf_floor=0.3300 (span=0.00316 auc=0.566 out_max=0.3017, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:53 2026-09-28 08:40:53 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00146 auc=0.532 out_max=0.3554 (n=110) → 보정 재적용
08:40:53 2026-09-28 08:40:53 [WARNING] LEARNING: [Calibration:30m] 하한 도달불가 — out_max=0.3285 < conf_floor=0.3300 (span=0.00403 auc=0.595 out_max=0.3285, 기저율=0.3263 n=95) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

### `logs/20260928_HEALTH.log`
```
--- [ExitCooldown] ×2(표본)
09:43:01 2026-09-28 09:43:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1175ms | quality=1.00 | cache_age=44s | exceptions_10m=3 | exc_tags=[ExitCooldown]×2 [ExitAttempt]×1
09:44:00 2026-09-28 09:44:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=334ms | quality=1.00 | cache_age=104s | exceptions_10m=3 | exc_tags=[ExitCooldown]×2 [ExitAttempt]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260928_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:02 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 4 | 09:56:00 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=35,943,669) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 3계약 (최소=1) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:14 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260928_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 18 | 08:41:11 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 23 | 08:58:35 [WARNING] 그리기 77.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 50 | 08:58:35 [WARNING] 그리기 77.7ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 752x1287 |
| 10:00 | 장중 초반 | 157 | 09:54:00 [WARNING] paintEvent slow 120.9ms | size=1955x1124 candles=70 grid=46.7 spans=16.1 candles=3.3 dir=0.3 regime=3.9 marke… |
| 12:00 | 장중 중간점 | 164 | 11:54:11 [WARNING] paintEvent slow 141.6ms | size=1955x1124 candles=190 grid=54.0 spans=14.7 candles=7.3 dir=0.7 regime=8.5 mark… |
| 14:00 | 장중 후반 · 장중 재학습 | 5 | 13:57:12 [WARNING] 그리기 94.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 856x1001 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 11 | 15:04:00 [WARNING] level=WARNING degraded=OFF | latency=355ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[SHA… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 11 | 15:12:11 [WARNING] _fetch_investor_data 지연 720ms — 메인 스레드 720ms 점유 (live 중단 원인 후보) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 11 | 15:34:11 [WARNING] _fetch_investor_data 지연 521ms — 메인 스레드 521ms 점유 (live 중단 원인 후보) |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:46:11 [WARNING] OHLCV 불일치 ts=2026-09-28 09:34:00 cols=['open'] existing_source=rt |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260928_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 95 | 08:40:48 [INFO] 활성화 | file=logs\crash_fault.log PID=19608 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 137 | 08:49:00 [INFO] code=A056A from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 192 | 08:54:01 [INFO] code=A056A from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 225 | 09:54:00 [INFO] code=A056A from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 202 | 11:54:00 [INFO] code=A056A from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 195 | 13:54:00 [INFO] code=A056A from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 182 | 15:04:00 [INFO] code=A056A from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 160 | 15:12:00 [INFO] code=A056A from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 59 | 15:34:00 [INFO] code=A056A from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 8 | 15:41:11 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=RISK_ON | 포지션=FLAT | 15:41:11 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260928_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:12 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 91 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 130 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 184 | 09:54:00 [WARNING] 신뢰도 미달 32.5% < 40.4% → 강제 X등급 |
| 12:00 | 장중 중간점 | 151 | 11:56:00 [WARNING] 신뢰도 미달 34.0% < 44.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 140 | 13:54:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 37 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:14 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20260926 | 16:50 | 로그 본문 |
| 20260924 | 10:58 | 로그 본문 |
| 20260923 | 18:44 | 로그 본문 |
| 20260922 | 15:47 | 로그 본문 |
| 20260921 | 17:30 | 로그 본문 |
| **중앙값** | **16:50** | 기준선 |
| **오늘 20260928** | **15:47** | 로그 본문 |

- 델타 **-63분** (음수 = 기준선보다 이르게 끝났다)
- 🔴 30분 이상 조기 종료 — §11 적신호 참조


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.3MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-09-23 (MW0601 624차 — 장후 자동조치: 「무흔적 크래시」 하나는 동결 감시자의 자기 종료였다)
## 2026-09-23 (MW0601 625차 — Ctrl+Shift+X 1분봉 차트: 창이 화면보다 넓어 못 줄이고, 4K 로 옮기면 봉이 사라졌다)
## 2026-09-24 (MW0601 630차 — 줄끝 규칙을 저장소 안으로 + 가드가 못 보던 잠금: 「오염 759개」는 오판이었다)
## 2026-09-26 (MW0601 631차 — 휴장일 점검: 부팅 직후 DB 초기화가 3분 넘게 안 끝났다)
## 2026-09-26 (MW0601 632차 — 장중 재점검, 10:44 절로부터 27분 뒤: 무변화 확인 + 수집기 자가점검 사례)
## 2026-09-26 (MW0601 631차 후속 — 장후: 휴장일 상황 동결 확인 + F-4 범위 확장)
## 2026-09-28 (MW0601 633차 — 장전 점검)
## 2026-09-28 (MW0601 634차 — 장중 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
라이브 미검증 항목**: `opt_chain_pcr` 옵션체인 로드 로그가 이번 점검 범위(08:40~09:00)에 나타나지 않음 — 장중 절에서 재확인 필요(검증 기한: 오늘 장중).

**추가 발견 (633차, 점검 마무리 단계)**: 위 항목들을 기록한 직후 `.git/index.lock`(0바이트)이 새로 생성된 것을 발견했다. `git_lock_guard.py --check`로 추적한 결과 나이 600초를 넘기며 `HOLD(판정보류)` → `STALE(스테일 확정, git 프로세스 0개)`로 전이했으나, `--reclaim` 시도가 `[Errno 1] Operation not permitted`로 실패했다 — SKILL.md가 경고한 "코웍 마운트 경유 세션은 unlink가 EPERM으로 막힌다" 시나리오의 정확한 재현. 세션 안에서는 회수 불가로 판단하고 리포트 이상점 1-2(P1)·사용자 조치 1번으로 올렸다. 이 락이 남아 있는 한 이번 점검이 만든 dev_memory 갱신분과 신규 리포트·증거 파일도 커밋되지 못한다.

## 2026-09-28 (MW0601 634차 — 장중 점검)

**증상**: 장전(633차) 리포트가 이상점 1-2로 올린 `.git/index.lock`(0바이트) 회수 실패가 장중에도 그대로 재현됐다. `python scripts/git_lock_guard.py --check`는 `STALE 스테일 확정 - 0바이트 · 3.5시간 · git 프로세스 0개`로 판정했지만, `--reclaim`을 실행하면 `[Errno 1] Operation not permitted: '.../futures/.git/index.lock'`로 실패했다(재현 2회째 — 장전·장중 동일 결과).

**원인**: 코웍(리눅스 샌드박스) 마운트 경유 세션은 `unlink`(파일 삭제) 시스템콜을 거부하지만 `rename`(이름 변경)은 허용한다. `git_lock_guard.py --reclaim`은 삭제(`os.remove`)만 시도하고 이름 변경 경로가 없어 여기서 막힌다. `.claude/skills/mireuk-daily-check/references/invariants.md` §0-B가 이미 이 정확한 우회(같은 파일을 `<이름>.stale.<pid>`로 `mv`)를 문서화해 두고 있었다.

**결정**: 문서화된 우회를 직접 실행했다 — `mv .git/index.lock .git/index.lock.stale.5`. 실행 직후 `git_lock_guard.py --check`가 `OK index.lock 없음`으로 전환됐다. `git commit`은 이번 세션에서 실행하지 않았다(장중 규정 준수 — 저장소 변경 금지는 코드·설정에 적용되는 것이고, 스테일 잠금 파일을 옆으로 비켜두는 것은 "장전·장중에는 코드를 바꾸거나 실행하지 않는다"는 원칙이 막는 대상이 아니라고 판단했다 — 실제 커밋·배포·재기동은 하지 않았다).

**Why**: 사용자에게 "탐색기에서 직접 지워달라"고 요청하는 것보다, 정본이 이미 검증한 세션 내 자가 우회를 먼저 시도하는 것이 원칙(§7 체크리스트 — "지워달라"를 쓰기 전에 우회 절차를 실제로 시도했는가)에 부합한다.

**How to apply**: 이미 적용 완료(이 세션 안에서). 향후 재발 시 같은 `mv` 절차를 다시 쓰면 된다. 근본적으로는 `scripts/git_lock_guard.py --reclaim`이 삭제 실패 시 자동으로 `rename` 우회를 시도하도록 만드는 안을 634-1로 등록(P2, 이번 리포트 고도화 방안 3 참조).

**검증**: `python scripts/git_lock_guard.py --check` → `OK index.lock 없음` 확인. `git --no-optional-locks status --short`가 오류 없이 정상 동작함을 확인(단, 실제 커밋은 이 세션에서 수행하지 않았으므로 "커밋 성공"까지는 라이브 미검증 — 다음 사람의 실제 커밋으로 최종 확인 필요).

---

기타 장중 확인 사항(문제 아님, 기록만):
- 옵션체인(`OptionChain`/`OptionBook`) 로드가 08:41부터 5분 간격으로 정상 재수집 중임을 로그로 확인 — 633-4 종결.
- 사이저 3계약→실제 2계약 눌림은 `HurstGate` 사이즈 축소(×0.5, hurst=0.136<0.45) 때문으로 확인 — 기존 `sizing_inversion_watch`([28]) 표본에 1건 추가, 신규 사안 아님.
- 매분 루프 커버리지 "209/371분(56.3%)" 자동 적신호는 증거 수집 시각(12:27, 장중)이 장마감(15:10) 전이라 발생한 것으로, 실제 공백이 아님을 확인(경과 시간 대비로는 사실상 100%).
- 서킷브레이커 상태 오늘 전 구간(211 표본) `NORMAL` 유지, CB⑤ 경고 8건은 전부 장시작버스트 완화기준(9초) 이내로 실제 정지 0건.
- 오전 매매: 진입 2건·청산 2건(레그 4건), 전승, 합계 +5.12pt/+212,566원. 정합성(레그합=포지션합) 확인.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 신규 등록
### 확인 완료 (604차 후속2가 재확인·재분류, 신규 아님)
## 2026-09-23 (MW0601 624차 — 장후 자동조치)
## 2026-09-26 (MW0601 631차 — 휴장일 점검)
## 2026-09-26 (MW0601 632차 — 장중 재점검)
## 2026-09-26 (MW0601 631차 후속 — 장후)
## 2026-09-28 (MW0601 633차 — 장전 점검)
## 2026-09-28 (MW0601 634차 — 장중 점검)
```

미완료 체크박스 **2862건** (끝에서 30건)
```
- [ ] **631-1** 9/28(월) 첫 기동 `FaultHandler 활성화 → DB 초기화 완료` 간격 확인(재부팅 직후면 특히). 20초 초과 시 1-1 재현.
- [ ] **631-2 (F-1)** `utils/db_utils.py:_migrate_predictions_db()` 역채움 UPDATE를 1회 마커(`PRAGMA user_version` 등)로 건너뛰기 — 매 기동 454MB 풀스캔 제거.
- [ ] **631-3 (F-2)** `init_all_dbs()` 단계별 소요시간 `[DBInit]` 로그(계측 4원칙 ④).
- [ ] **631-4 (F-3)** 미륵이 런처 STEP 4: 자동로그인 스크립트 실행 중이면 준비 판정 보류.
- [ ] **631-5 (F-4)** `collect_evidence.py` §11 영업일 판정 — 휴장일 가짜 동결 경보 제거.
- [ ] **632-1** `scripts/collect_evidence.py` 실행 중 `.git/index.lock`이 0.1분(약 6초) 생성됐다 자연 해소된 경로 특정 — 어느 내부 호출이 `--no-optional-locks` 없이 인덱스에 쓰는지 grep으로 확인 (P2, 장후 또는 여유 있을 때).
- [ ] **632-2** 미륵이 점검 예약작업(장중)이 같은 날 약 20분 간격으로 두 번 발화된 것으로 관측됨 — 트리거 설정 확인 필요(코드 사안 아님, 운영 사안. 사용자 확인 권장).
- [ ] **631-6 (F-4 범위확장)** `collect_evidence.py` §11 적신호 생성부를 `--phase` 무관 영업일 게이트로 — 휴장일이면 8개 규칙 전부 생략, "휴장일" 배너만 출력. 631-1~631-5(장중 등록분)는 변경 없음.
- [ ] **631-6** 미커밋 3건 커밋 권고(사용자 결정) — 되돌리면 캐시(`roll_adj` 262건) TypeError + 0917 자동로그인 결함 부활. 두 커밋 분리. 근거: 0926 리포트 추기.
- [ ] **631-7** `premarket_levels.compute_manual()` 에 `roll_adj` 전달 누락 — `ROLL_POLICY=adjust` 켜기 전 수정.
- [ ] **631-8** `cybos_autologin._is_already_running_text()` any → "이미실행" 필수로 축소(오탐 여지 제거).
- [ ] **631-9** dev 이식 결정(사용자): `723c208` 은 무충돌 적용 가능(권고) · `46f3ee7` 은 충돌 3곳 + dev 에 roll_days 라벨 배치 없음 → 보류 권고. `v9-dev` push 여부도 함께.
- [ ] **631-10 (F-1a, 1순위)** `_migrate_predictions_db()` 역채움 UPDATE 앞에 부분 인덱스 `idx_pred_prob_null`(WHERE 세 확률 IS NULL) — 복사본 실측 UPDATE 0.6s→0.0000s, 생성 1회 6.3s. 631-2(user_version 마커안)를 대체.
- [ ] **631-11 (F-5)** 초기화 중 런처 콘솔에 `[BOOT] DB 초기화 중…` 진행 표시 — 0926 사용자가 "안 올라온다"고 판단해 수동 종료.
- [ ] **631-12 (F-6/F-7/F-8)** 자동로그인: 재시도 직전 `_is_connected()` 재확인 · kill 실패 가시화 · diag 줄별 시각. F-6은 모의 리허설 1회 후.
- [ ] **631-13 (F-3/F-3b)** 런처 STEP 4: autologin 락 대기 + IsConnect 연속 10초 유지 판정.
- [ ] **631-14 (F-4/G-1)** 스킬 폴더 `collect_evidence.py`에 `config/krx_holidays.py`(파일경로 로드) 휴장일 판정 — FZ-6·480차 규칙 스킵 + 배너.
- [ ] **631-15** `tests/test_458_p0_quiet_window.py:163` 이 운영 DB 경로로 `init_all_dbs()` 를 호출한다 — 임시 DB_DIR 로 격리할 것(2026-09-26 이 테스트가 운영 predictions.db 에 색인을 만들었다; 이번엔 무해).
- [ ] **631-16 (S-1, 권고)** `auto_trader_kiwoom/scripts/shutdown_friday.bat`(한량이 저장소): `shutdown /h` 직전 CpStart·ncStarter·DibServer·미륵이 main.py 종료 — 절전 해제 후 끊긴 세션을 든 CpStart 가 남아 LAUNCH_API 가 "Already…
- [ ] **631-17 (S-2/S-3)** `LAUNCH_API.bat`: CpStart 시작 < 마지막 절전 해제면 연결 불신 → 자동로그인 / `[CHECK] IsConnect` 값을 로그 파일에도 기록.
- [ ] **631-18 (S-4)** `start_mireuk.bat` STEP 4 실패 시 "CpStart 생존·미연결 = 절전 해제 후 끊김" 힌트.
- [ ] **631-19** 옛 Cybos 생존 상태 자동로그인 1차 성공 여부 — 다음 절전 해제 아침 diag 로그로 확인(새 프로세스 IsConnect 확인 라이브 검증)
- [ ] **631-17 (S-2/S-3)** 여전히 미구현 확인 — `logs/Mireuk_batch/launcher_20260928_084001_3298.log`에 `[CHECK] IsConnect` 값이 파일로 기록되지 않음(grep 0건). 변경 없음, 계속 열어둠.
- [ ] **633-1 (P2, 신규)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 1행 마크다운 제목(`# 재시작...`) 손상 상태로 미커밋 — 사용자에게 의도한 편집인지 확인 후, 아니라면 `git checkout --`로 복원. 근거: 0928 장전 리포트 이상점 1-1.
- [ ] **633-2 (고도화, P2)** `[PreRetrain]` 판정에서 `data/eod_retrain_done_{d}.txt` 마커 파일 직접 확인 경로를 "미기록 보완"이 아니라 1차 확인 경로로 격상 검토 — 근거: `SessionStateDrop`(606-2 근본원인 미해결) 발생 시마다(09-14·09-17·09-21·09-22·09-…
- [ ] **633-3 (고도화, P2)** 커밋 전 프리플라이트(`scripts/git_lock_guard.py` 또는 별도 스크립트)에 "마크다운 파일 첫 줄이 `# `로 시작하다가 사라졌는가" 같은 가벼운 문서 손상 탐지 경고 추가 검토 — 근거: 0928 이상점 1-1(재현 1건, 원인 미상).
- [ ] **633-4** `opt_chain_pcr`(옵션체인 → 30m CORE 피처 입력) 로드 로그가 0928 장전(08:40~09:00) 구간에 미확인 — 장중 점검에서 재확인.
- [ ] **633-5 (P1, 신규)** `.git/index.lock`(0바이트) 스테일 확정 후에도 `--reclaim`이 `EPERM`으로 실패 — 코웍 마운트 경유 세션의 구조적 한계(SKILL.md 예고대로 재현). 사용자가 로컬에서 직접 삭제하거나 `--reclaim` 재시도 필요. 근거: 0928 장전 리포트 이상점 1-2.
- [ ] **634-1 (P2, 고도화)** `scripts/git_lock_guard.py --reclaim`이 `unlink` 실패(`EPERM`) 시 `os.rename()`으로 `<파일>.stale.<pid>` 우회를 자동 시도하도록 — 단 "스테일 확정" 판정 후에만 동작하고 "판정보류"에서는 지금처럼 손대지 않아야 함. 근거: 0928 장전·…
- [ ] **634-2** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상(633-1 계승). 잠금 해소로 이제 언제든 `git checkout --`로 되돌릴 수 있음, 의도한 편집인지 확인 먼저.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
631-16** 절전 전 Cybos 세션 정리 — auto_trader_kiwoom `333e3ee`(PlusDisconnect; 강제 종료는 보안 모듈이 거부)
- [ ] **631-19** 옛 Cybos 생존 상태 자동로그인 1차 성공 여부 — 다음 절전 해제 아침 diag 로그로 확인(새 프로세스 IsConnect 확인 라이브 검증)

## 2026-09-28 (MW0601 633차 — 장전 점검)
- [x] **631-1** 종결 — 9/28 첫 기동 `[FaultHandler] 활성화`(08:40:48)와 `[DBInit] 합계 0.42s`(08:40:48)가 같은 초 — 20초 초과 재현 없음. 정상.
- [x] **631-10/11** 종결 — 9/28 첫 기동 `[DBInit] 합계 0.42s`(predictions=0.04s trades=0.20s 등 세부 포함) 실측 확인. "1초대 확인 대기" 해소.
- [x] **631-12** 종결 — `logs/cybos_autologin_diag.log` 09/28 08:35:11~08:35:50 진단 로그로 재시도 없는 1회 성공 확인. "라이브 리허설 미실시" 해소.
- [x] **631-19** 종결 — 위와 동일 로그로 "다음 절전 해제 아침 diag 로그" 확인 완료. 첫 시도 성공, 세션 끊김 재현 없음.
- [ ] **631-17 (S-2/S-3)** 여전히 미구현 확인 — `logs/Mireuk_batch/launcher_20260928_084001_3298.log`에 `[CHECK] IsConnect` 값이 파일로 기록되지 않음(grep 0건). 변경 없음, 계속 열어둠.
- [ ] **633-1 (P2, 신규)** `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 1행 마크다운 제목(`# 재시작...`) 손상 상태로 미커밋 — 사용자에게 의도한 편집인지 확인 후, 아니라면 `git checkout --`로 복원. 근거: 0928 장전 리포트 이상점 1-1.
- [ ] **633-2 (고도화, P2)** `[PreRetrain]` 판정에서 `data/eod_retrain_done_{d}.txt` 마커 파일 직접 확인 경로를 "미기록 보완"이 아니라 1차 확인 경로로 격상 검토 — 근거: `SessionStateDrop`(606-2 근본원인 미해결) 발생 시마다(09-14·09-17·09-21·09-22·09-28 등) 이 fallback이 매번 정확히 대신 판정. 606-2 근본수정 전까지의 임시 완화책.
- [ ] **633-3 (고도화, P2)** 커밋 전 프리플라이트(`scripts/git_lock_guard.py` 또는 별도 스크립트)에 "마크다운 파일 첫 줄이 `# `로 시작하다가 사라졌는가" 같은 가벼운 문서 손상 탐지 경고 추가 검토 — 근거: 0928 이상점 1-1(재현 1건, 원인 미상).
- [ ] **633-4** `opt_chain_pcr`(옵션체인 → 30m CORE 피처 입력) 로드 로그가 0928 장전(08:40~09:00) 구간에 미확인 — 장중 점검에서 재확인.
- [ ] **633-5 (P1, 신규)** `.git/index.lock`(0바이트) 스테일 확정 후에도 `--reclaim`이 `EPERM`으로 실패 — 코웍 마운트 경유 세션의 구조적 한계(SKILL.md 예고대로 재현). 사용자가 로컬에서 직접 삭제하거나 `--reclaim` 재시도 필요. 근거: 0928 장전 리포트 이상점 1-2.

## 2026-09-28 (MW0601 634차 — 장중 점검)
- [x] **633-4** 종결 — 옵션체인 로드(`[OptionChain] 초기화 완료`, 08:41:12) + 5분 간격 재수집 44회, `[OptionBook]` 먼스리/위클리 GEX 정상 출력 확인. 미확인 해소.
- [x] **633-5** 종결 — `invariants.md` §0-B의 `mv` 우회(`.git/index.lock` → `.git/index.lock.stale.5`)로 이번 세션 안에서 회수 성공. `git_lock_guard.py --check` → `OK index.lock 없음`. 커밋은 미실행(장중 규정 준수) — 다음 실제 커밋으로 최종 검증 필요.
- [ ] **634-1 (P2, 고도화)** `scripts/git_lock_guard.py --reclaim`이 `unlink` 실패(`EPERM`) 시 `os.rename()`으로 `<파일>.stale.<pid>` 우회를 자동 시도하도록 — 단 "스테일 확정" 판정 후에만 동작하고 "판정보류"에서는 지금처럼 손대지 않아야 함. 근거: 0928 장전·장중 2회 동일 수동 우회 반복. 표본 2건 — 확정 결론 금지, 우선순위 P2 유지.
- [ ] **634-2** 사용자 확인 대기 유지 — `docs/미륵이고도화3/재시작_종료사유분류_봉결손_구현계획_20260922.md` 제목 손상(633-1 계승). 잠금 해소로 이제 언제든 `git checkout --`로 되돌릴 수 있음, 의도한 편집인지 확인 먼저.

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

### `data/heartbeat_MW0601_20260928.json` — 245B · 09-28 15:46:54
```json
{
 "pid": 19608,
 "written_at": "2026-09-28T15:46:54",
 "beat_epoch": 1790578011.1632261,
 "beat_age_sec": 3.6,
 "watching": false,
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

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **09-28 15:53:27**

| 키 | 값 | 수집 대상일(2026-09-28)과 일치 |
|---|---|---|
| `date` | 2026-09-28 | 예 |
| `p8_last_success_date` | 2026-09-28 | 예 |
| `eod_retrain_ok_date` | 2026-09-28 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20260928_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 19608 | 08:40:48 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 172개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260928-점검리포트.md` | 39.5KB | 09-28 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_intra.md` | 74.0KB | 09-28 12:28 |
| `docs/정기점검/매일점검/evidence_MW0601-20260928_pre.md` | 56.8KB | 09-28 09:00 |
| `docs/정기점검/매일점검/MW0601-20260926-점검리포트.md` | 67.5KB | 09-26 16:43 |
| `docs/정기점검/매일점검/evidence_MW0601-20260926_intra_1107.md` | 41.3KB | 09-26 11:07 |
| `docs/정기점검/매일점검/evidence_MW0601-20260926_post.md` | 41.7KB | 09-26 11:06 |
| `docs/정기점검/매일점검/evidence_MW0601-20260926_intra.md` | 41.7KB | 09-26 10:44 |
| `docs/정기점검/매일점검/MW0601-20260901-점검리포트.md` | 121.4KB | 09-24 18:10 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260923.json` | 3.0KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260923.md` | 4.9KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260923.json` | 38.8KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260923.md` | 32.3KB | 09-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260923.json` | 121.3KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260923.md` | 195.2KB | 09-23 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260918.json` | 3.0KB | 09-18 15:55 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260918.md` | 5.0KB | 09-18 15:55 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
2. 포지션 2건 중 최종청산이 하드스톱·손절 계열 **1건(50%)** — 손절 준수율 확인 필요 (레그 4행)
3. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
4. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
5. **SYSTEM 로그가 직전 5거래일 중앙값(16:50)보다 63분 이르게 끝났다** (오늘 15:47) — 15:40 daily_close까지 살아 있었는지 확인하라. 프로세스 동결이면 15:10 강제청산·15:40 마감이 통째로 미실행이다 (2026-08-19 13:41 사고)
6. 메인 스레드 정지 5초 초과 **1건** (최대 5187ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
7. `logs/20260928_WARN.log`: **ConstOut** 2건(표본)
8. `logs/20260928_SYSTEM.log`: **ConstOut** 8건(표본)
9. `logs/20260928_SIGNAL.log`: **WeightCollapse** 8건(표본)
10. `logs/20260928_SIGNAL.log`: **ConstOut** 8건(표본)
11. `logs/20260928_LEARNING.log`: **축퇴** 8건(표본)
12. 미커밋 변경 6건 — **실질 변경 미측정**(git diff 실패). 원시 건수만으로는 착시인지 알 수 없다
13. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260928*.log` (Windows) / `grep 강제청산 logs/*20260928*.log`*