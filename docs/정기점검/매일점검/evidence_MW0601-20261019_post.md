# 미륵이 증거 다이제스트 — 2026-10-19 / POST

- 생성 2026-10-19 16:21:22 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01eymbau83rl88n73zvrbh4h/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261019` · `2026-10-19` · `261019` · `1019`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **43개** 파일 · 43개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-intra-cowork-intra-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261019-intra-cowork-intra-20261019.json` | 174B | 10-19 12:26 |
| `claude-{DATE}-pre-cowork-pre-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261019-pre-cowork-pre-20261019.json` | 170B | 10-19 09:03 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261019.txt` | 28B | 10-19 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261019.txt` | 28B | 10-19 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261019.txt` | 233B | 10-19 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261019.log` | 1.4KB | 10-19 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261019.log` | 274B | 10-19 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261019.json` | 244B | 10-19 15:46 |
| `launcher_{DATE}_084001_30125.log` | 1 | `logs/Mireuk_batch/launcher_20261019_084001_30125.log` | 2.3MB | 10-19 15:47 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261019.log` | 109B | 10-19 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261019.log` | 65.3KB | 10-19 16:20 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261019.log` | 491B | 10-19 16:15 |
| `position_state.json.gen_{DATE}_113743` | 1 | `data/position_state.json.gen_20261019_113743` | 1.5KB | 10-19 10:58 |
| `position_state.json.gen_{DATE}_131214` | 1 | `data/position_state.json.gen_20261019_131214` | 1.5KB | 10-19 13:12 |
| `position_state.json.gen_{DATE}_150426` | 1 | `data/position_state.json.gen_20261019_150426` | 1.5KB | 10-19 13:12 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261019.log` | 21.5KB | 10-19 15:53 |
| `retrain_intraday_20260811_{DATE}59.log` | 1 | `logs/retrain_intraday_20260811_101959.log` | 4.5KB | 08-11 10:20 |
| `retrain_intraday_{DATE}_094000.log` | 1 | `logs/retrain_intraday_20261019_094000.log` | 3.2KB | 10-19 09:40 |
| `retrain_intraday_{DATE}_114000.log` | 1 | `logs/retrain_intraday_20261019_114000.log` | 3.2KB | 10-19 11:40 |
| `retrain_intraday_{DATE}_130001.log` | 1 | `logs/retrain_intraday_20261019_130001.log` | 3.2KB | 10-19 13:00 |
| `retrain_intraday_{DATE}_135100.log` | 1 | `logs/retrain_intraday_20261019_135100.log` | 3.2KB | 10-19 13:51 |
| `retrain_intraday_{DATE}_142100.log` | 1 | `logs/retrain_intraday_20261019_142100.log` | 3.2KB | 10-19 14:21 |
| `retrain_intraday_{DATE}_145100.log` | 1 | `logs/retrain_intraday_20261019_145100.log` | 3.2KB | 10-19 14:51 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261019.log` | 86.3KB | 10-19 16:05 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261019.txt` | 43B | 10-19 15:47 |
| `strategy_report_{DATE}_154018.txt` | 1 | `data/daily_reports/strategy_report_20261019_154018.txt` | 2.1KB | 10-19 15:40 |
| `trail_state_{DATE}.json` | 1 | `data/peter2_live/trail_state_2026-10-19.json` | 51B | 10-19 15:04 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-19.jsonl` | 5.7KB | 10-19 15:08 |
| `{DATE}_DATA.log` | 1 | `logs/20261019_DATA.log` | 437.3KB | 10-19 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261019_DEBUG.log` | 271.3KB | 10-19 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261019_HEALTH.log` | 4.5KB | 10-19 15:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20261019_HOGA.log` | 58.2MB | 10-19 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261019_LEARNING.log` | 284.7KB | 10-19 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261019_MICRO.log` | 1.1MB | 10-19 15:40 |
| `{DATE}_OPTION_BACKFILL.log` | 1 | `logs/20261019_OPTION_BACKFILL.log` | 652B | 10-19 16:21 |
| `{DATE}_PROBE.log` | 1 | `logs/20261019_PROBE.log` | 94.6KB | 10-19 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261019_REGULAR_COLLECT.log` | 8.8KB | 10-19 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261019_SIGNAL.log` | 484.7KB | 10-19 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261019_SYSTEM.log` | 1.0MB | 10-19 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261019_TRADE.log` | 18.8KB | 10-19 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261019_WARN.log` | 678.8KB | 10-19 15:46 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-19_tr.draft.txt` | 136B | 10-19 15:40 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-10-19_tr.txt` | 136B | 10-19 15:40 |

## 2. 코드·커밋 상태

- HEAD `5aaad2d` · 브랜치 `v9-dev` · 미커밋 15건 · 실질 변경 6건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 6 · 미추적 9 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.4초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md
 M docs/미륵이고도화3/신동2/학습/lessons.json
 M docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md
 M docs/미륵이고도화3/신동2/학습/추이_MW0601.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261020.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.svg
?? docs/정기점검/매일점검/MW0601-20261019-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md
```

**당일(2026-10-19) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
5aaad2d [MW0602] v9-dev 배포(체리픽): A-04 당일 손실 기준 자본 1,500만원 고정 — 두 PC 동일 (원 c68b442, dev)
a00a688 [MW0602] v9-dev 배포(체리픽): 긴급 이상 알림 메일 S/A/B 14종 (원 ec00de0, dev)
0116377 [MW0601] 대시보드 3번 행 명칭 단순화 + [메일] On/Off 체크박스
ef8d795 [MW0602] v9-dev 배포(체리픽): 청산 거부 113분 재발 방지 ①~⑥ · 거래소 CB 차단을 모든 주체에 (원 d4776ed, dev)
5aa7c6c [MW0601] 문서 정리: 09-30–10-16 미커밋 산출물 일괄 커밋
af1e961 [MW0602] v9-dev 배포(체리픽): F-1009 동결 경보 메일([긴급이상]/[이상해소]) · G-1i closeEvent 진입/결과 로그 (원 f5ff9cb, dev)
f119a31 [MW0601] 697차 후속: 장후 자동조치 — F-26 (+ 10-16 장전·장중·장후 dev_memory · 누적대장 P5-18)
7a5275b [MW0601] 697차: 피터2 X 수집 한도 소진 — 한도 헤더 계측 · 80초 · reset 백오프
d81c079 [MW0601] 692차 후속4: 아침 coStarter 크래시 근절 — 장후 API 세션·맥점 사다리 정리(16:30) · 자동로그인 크래시 팝업 처리
51d5de4 [MW0601] 696차 후속: 장후 자동조치 — E-2 · F-X1
bd501c2 [MW0601] 692차 후속3: 피터2 — 도착 시점에 이미 만료된 지시는 대기로 열지 않는다
46d2e13 [MW0601] 692차 후속2: CREON 런처 기동흐름 — LAUNCH_API 파싱 즉사 · 계좌비밀번호 창 자동처리 · 사이드카 중복/자진종료
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `1` | `3` | **불일치 ⚠** | 431차 10→3 인하. 실전 자본 확정 시 재산출 대상 |
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

### 차단 게이트 전수 인벤토리 — 45개 중 **9개 꺼짐**

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
| `ALERT_MAIL_ENABLED` | True | — |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
| `DAILY_CLOSE_FORCE_EXIT_ENABLED` | True | — |
| `EXIT_LIMIT_FALLBACK_ENABLED` | True | — |
| `EXIT_REJECT_BLOCK_ENTRIES` | True | — |
| `FORCE_FLAT_GUARD_ENABLED` | True | — |
| `FREEZE_SENTINEL_ENABLED` | True | — |
| `FREEZE_SENTINEL_MAIL_ENABLED` | True | — |
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
| `PRINCIPAL_SHINDONG_ENABLED` | True | — |
| `SHINDONG_DAILY_REPORT_ENABLED` | True | — |
| `SHINDONG_ENABLED` | True | — |
| `SHINDONG_REPORT_MAIL_ENABLED` | True | — |
| `SHINDONG_RUNNER_SHADOW_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20261019_HOGA.log` 58.2MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261019.txt`** — 28B · 10-19 15:40:18
```
2026-10-19T15:40:18.696596
```

**`data/daily_close_started_20261019.txt`** — 28B · 10-19 15:40:08
```
2026-10-19T15:40:08.329255
```

**`data/daily_reports/strategy_report_20261019_154018.txt`** — 2.1KB · 10-19 15:40:18
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-19 15:40
========================================================
  버전    : v1.0  (100일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-4.55  MDD(자본대비)=4.5%
  당일      : WR=25.0%  PF=0.26
  롤링20일: 누적 -1942692원  Sh=-4.55  MDD(자본대비)=4.5%  MDD(peak대비)=721.8%
  당일손익 : broker(gross) -508,651원  수수료 6,642원  net -508,642원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.84)
  PSI     : 0.003 (CLEAR)
  PSI/feat: cvd_delta=0.003  ofi_pressure=0.000  vwap_position=0.059
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -57,153원  승률 30.0%  합계 -1,143,063원
  등급별 순EV(30일): A=-6,062원(58건,승57%)  P=-79,556원(20건,승20%)
  호라이즌별 순EV(30일): 1m=+2,297원(7건)  3m=+15,483원(33건)  5m=-48,810원(18건)  ?=-79,556원(20건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 32분  5일평균 24분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 49.9pt(5일평균 42.1pt)  1분평균변동 1.01pt(5일평균 0.99pt)
--------------------------------------------------------
  진입 퍼널(2026-10-19, 총 370분):
    FLAT 233 → conf미달 103 → CoherenceGate 2 → 게이트차단 30 → 후보 2 → 진입 2
    게이트별: 체크리스트항목미달=20  콜드스타트/기타(DataAnomalyGate)=4  콜드스타트/기타(σ미수집)=4  포지션보유중(평가생략)=2
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261019.txt`** — 233B · 10-19 15:53:32
```
completed: 2026-10-19 15:53:32
rows: 21750
cols: 97
phase2_fallback: false
horizons_replaced: 5/6
t_load_s: 26.5
t_retrain_s: 181.4
t_total_s: 208.4
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/peter_feed/2026-10-19_tr.draft.txt`** — 136B · 10-19 15:40:10
```
09:04 S 865 / 09:06 X 869 손절
09:08 S 870 / 10:19 X 885 손절
10:19 S 883 / 13:02 X 890 손절
13:12 S 885 / 15:07 X 890 손절
```

**`data/peter_feed/2026-10-19_tr.txt`** — 136B · 10-19 15:40:10
```
09:04 S 865 / 09:06 X 869 손절
09:08 S 870 / 10:19 X 885 손절
10:19 S 883 / 13:02 X 890 손절
13:12 S 885 / 15:07 X 890 손절
```

**`data/shutdown_normal_20261019.txt`** — 43B · 10-19 15:47:14
```
auto_shutdown
2026-10-19T15:47:14.710335
```

_다이제스트 대상 8/27개 (중요도순). 제외: `retrain_intraday_20261019_114000.log`, `retrain_intraday_20261019_130001.log`, `retrain_intraday_20261019_135100.log`, `retrain_intraday_20261019_142100.log`, `retrain_intraday_20261019_145100.log`, `retrain_intraday_20261019_094000.log`, `20261019_MICRO.log`, `20261019_DATA.log`_

### `logs/20261019_TRADE.log` — 18.8KB · 135행 · 최종 15:40:16

- 형식 평문 · 시각 인식 135행 · WARNING=11, INFO=124

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-19 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-19 09:04:45 [INFO] TRADE: [Peter2] 진입시도 SHORT 1계약 @863.02 손절 866.92 목표 - — brk_dn SHORT 지시 865(미니 862.92) 현재 863.02
2026-10-19 09:04:45 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 863.02 | 손절=866.92 1차=-9136.98(×1.00) 2차=-9136.98
2026-10-19 09:04:45 [INFO] TRADE: [주문요청] SHORT->SHORT 1계약 @ 863.02 등급=P 역방향진입=OFF 체결대기
  …
2026-10-19 15:04:26 [INFO] TRADE: [Position] 체결청산 SHORT @ 888.02 | PnL=-4.70pt (-236,678원) | 하드스톱(틱)
2026-10-19 15:04:27 [INFO] TRADE: [청산 완료] PnL=-4.70pt (-236,678원) | 포지션 합계 -236,678원 (레그 1)
2026-10-19 15:05:00 [INFO] TRADE: [Position] 청산 LONG @ 887.58 | PnL=+13.76pt (+686,340원) 수수료=1,660원 | 가상:신동시간청산
2026-10-19 15:05:00 [INFO] TRADE: [Virtual] 신동 가상청산 LONG 1계약 @887.58 가상:신동시간청산 | +13.76pt +686,340원 (포지션 종료)
2026-10-19 15:40:16 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 11 | 09:04:45 | 13:12:14 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=862.96 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×135

**컴포넌트 상위 15** — `Position`×33, `Chejan`×24, `Virtual`×18, `Peter2Trail`×14, `PositionFallback`×11, `Peter2`×8, `주문요청`×8, `체결진입`×4, `TickStop-S0C`×4, `청산 완료`×4, `ProfitGuard`×2, `Sizer`×2, `진입체크`×2, `Peter2TrailShadow`×1

### `logs/20261019_WARN.log` — 678.8KB · 3041행 · 최종 15:46:08

- 형식 평문 · 시각 인식 3034행 · WARNING=3034, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 78ms
2026-10-19 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr11)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-19 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr11)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=783343908
  …
오늘 PnL: -508642원
════════════════════════════════════════════════════
2026-10-19 15:40:17 [WARNING] SYSTEM: [LiveDBG] _refresh_pnl_history 총 215ms
2026-10-19 15:45:00 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 239.7ms | size=1994x937 candles=410 grid=38.8 spans=30.7 candles=52.1 dir=1.5 regime=8.5 markers=102.9 axes=1.1 cross=0.0 | slow_cnt=2588 total_cnt=2703 overlay_cnt=37074
2026-10-19 15:46:08 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 103.8ms | size=1994x937 candles=411 grid=21.2 spans=12.7 candles=30.0 dir=1.3 regime=5.8 markers=30.8 axes=0.6 cross=0.0 | slow_cnt=2589 total_cnt=2704 overlay_cnt=37075
```

</details>

**WARNING — 태그 34종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2589 | 09:15:50 | 15:46:08 | paintEvent slow 149.4ms | size=1994x950 candles=31 grid=19.5 spans=50.4 candles=55.7 dir=0.1 regime=0.1 markers=4.6 axes=6.0 cross=0.0 | slow_cnt=1 total_cnt=116 overlay_cnt=602 |
| `LiveDBG` | 127 | 08:41:08 | 15:40:17 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 73 | 08:41:18 | 15:34:08 | 그리기 69.0ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 785x1001 |
| `ChejanFlow` | 24 | 09:04:45 | 15:04:26 | account='783343908' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='158' | pending='ENTRY:SHORT qty=1 filled=0 order_no=? reason=진입 req_at=09:04:45.024' | positio… |
| `ChejanMatch` | 24 | 09:04:45 | 15:04:26 | order_no='158' | pending='ENTRY:SHORT qty=1 filled=0 order_no=158 reason=진입 req_at=09:04:45.024' | pending_matched=True |
| `SHAP` | 22 | 11:35:01 | 15:06:01 | 슬로우 감지 1037ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `Peter2` | 18 | 09:24:11 | 14:37:10 | 오프셋 자동 적용 -2.08(prev_day:2026-10-16, safe=True) → -1.72(live:09:24:09, safe=True) |
| `PendingOrder` | 16 | 09:04:45 | 15:04:27 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 863.02, 'reason': '진입', 'hint_source': '', 'atr': 2.5714, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qt… |
| `ScalerRefresh` | 16 | 09:05:00 | 14:55:00 | 5분 누적 수익률 +1.366% (임계 ±0.845%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `PipePerf` | 14 | 09:00:01 | 14:52:04 | total=1232ms | S0=2ms S1=14ms S2=0ms S3=0ms S4=61ms S5=909ms S6=229ms S7=11ms S8=6ms |
| `Health` | 14 | 09:00:01 | 15:00:01 | level=WARNING degraded=OFF | latency=1232ms | quality=1.00 | cache_age=51s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2 |
| `CB⑤` | 14 | 09:00:01 | 14:52:04 | 파이프라인 1232ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |

**채널** — `SYSTEM`×3020, `HEALTH`×14

**컴포넌트 상위 15** — `ChartDBG`×2589, `LiveDBG`×127, `OptionFlowChart`×73, `ChejanFlow`×24, `ChejanMatch`×24, `SHAP`×22, `Peter2`×18, `PendingOrder`×16, `ScalerRefresh`×16, `PipePerf`×14, `Health`×14, `CB⑤`×14, `Peter2Offset`×11, `ExitCooldown`×8, `-`×7

### `logs/20261019_SYSTEM.log` — 1.0MB · 7210행 · 최종 15:47:14

- 형식 평문 · 시각 인식 7189행 · INFO=7189, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=4572 | 행감지=30s all_threads=True
2026-10-19 08:40:46 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.22s daily_stats=0.01s shap=0.01s raw_data=0.10s broker_pnl=0.02s broker_recon=0.01s premarket_levels=0.02s
2026-10-19 08:40:46 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-19 08:40:46 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-19 08:40:46 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-19 15:46:08 [INFO] SYSTEM: [RawFill] 2026-10-19 raw_candles 창 안 보충 0봉(bar_recovered=2) · 차트 보정 1봉(bar_recovered=3) — 보충 — / 보정 08:45
2026-10-19 15:46:08 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-19) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-19 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-19 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-19 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×7189

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1516, `PumpGuard`×768, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `MicroRegime`×105, `System`×100, `OptionChain`×81, `OptionBook`×79, `RegimeFingerprint`×69, `CybosEvent`×48

### `logs/20261019_SIGNAL.log` — 484.7KB · 4367행 · 최종 15:40:17

- 형식 평문 · 시각 인식 4367행 · WARNING=1441, INFO=2926

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.461
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.443
  …
2026-10-19 15:10:00 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-19 15:40:16 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-19 15:40:16 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 169분(45.7%) / DN 0분(0.0%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-19 15:40:17 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-19 age=27m extreme=332 refresh=36 grade_x=121 cb3=0
2026-10-19 15:40:17 [INFO] SIGNAL: [ModelHealth] date=2026-10-19 앙상블유효가동률=69.5% | 파이프라인 370분 | ConstOut 18회/28분 {"3m": {"events": 10, "minutes": 17}, "5m": {"events": 3, "minutes": 5}, "10m": {"events": 5, "minutes": 6}} | WeightCollapse 85분 | 장중재학습 6회 | CB③ ready 81분/370분 (22%) (리셋 2회, 표본손실 60건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1026 | 09:00:01 | 15:04:01 | 1m 'macro_vix' scale=0.0172 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 133 | 09:06:00 | 15:09:02 | CORE VWAP ✗ → 강제 X등급 (pass_count=9, group=short) | VWAP pos=+1.237 need <0 (SHORT) bull_exh=0.00 |
| `Model` | 86 | 09:00:00 | 15:03:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 86 | 09:00:00 | 15:04:00 | ts=08:59 horizon=1m age=1m max_z=-4.88(macro_nasdaq_chg) extreme=2 adj=2 |
| `WeightCollapse` | 85 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 18 | 09:35:00 | 14:49:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ScalerRefresh` | 6 | 08:45:09 | 08:45:09 | 1m CORE 'cvd_divergence' raw_std≈0(0.0239) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConfFloorGuard` | 1 | 13:00:00 | 13:00:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3586 < 필요 0.3820 (conf_floor=0.330, min_conf=0.382, span=0.0079, auc=0.551). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4367

**컴포넌트 상위 15** — `ScalerFloor`×1080, `SIGNAL`×740, `FQAdj`×369, `Ensemble`×367, `ZeroDiag`×346, `MetaGate`×341, `Checklist`×145, `Model`×128, `ATR-Horizon`×125, `MicroRegime`×105, `InstabilityGate`×88, `ScalerMonitor`×87, `WeightCollapse`×85, `차단`×82, `ScalerRefresh`×48

### `logs/20261019_LEARNING.log` — 284.7KB · 2805행 · 최종 15:40:16

- 형식 평문 · 시각 인식 2805행 · WARNING=152, INFO=2653

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00158 auc=0.502 out_max=0.2959 (기준 auc<0.53 and span<0.020, 기저율=0.2952 n=105) → 보정 미적용, raw 통과
  …
2026-10-19 15:40:16 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-19 15:40:16 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-19 15:40:16 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-19 15:40:16 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-19 15:40:16 [INFO] LEARNING: [Sigma] EOD sigma_20=0.10206% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 45 | 08:40:51 | 14:58:01 | 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 44 | 08:40:51 | 11:50:00 | 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 26 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 20 | 08:40:51 | 12:55:00 | 하한 도달불가 — out_max=0.2515 < conf_floor=0.3300 (span=0.00276 auc=0.608 out_max=0.2515, 기저율=0.2500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 8 | 08:40:52 | 08:40:56 | 축퇴 감지 — span=0.00013 auc=0.527 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 6 | 08:40:51 | 08:40:58 | 축퇴 감지 — span=0.00172 auc=0.445 out_max=0.3383 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 2 | 08:40:59 | 14:39:00 | 복원한 보정기가 축퇴 상태 — span=0.00457 auc=0.500 out_max=0.3478 (n=3928) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Retrain` | 1 | 15:40:16 | 15:40:16 | DB pruning 실패 — 삭제 롤백(반영 0행, 시도 30480행): database table is locked |

**채널** — `LEARNING`×2805

**컴포넌트 상위 15** — `LEARNING`×1219, `SGD`×370, `sigma`×357, `Bias⚠`×183, `Bias`×141, `Calibration:1m`×88, `Calibration:30m`×87, `MetaConf`×80, `Calibration:3m`×50, `ScalerWarmup`×42, `Calibration:5m`×39, `OnlineLearner`×37, `BiasReset`×23, `Calibration:15m`×16, `Calibration:10m`×12

### `logs/20261019_HEALTH.log` — 4.5KB · 29행 · 최종 15:01:00

- 형식 평문 · 시각 인식 29행 · WARNING=14, INFO=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1232ms | quality=1.00 | cache_age=51s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2
2026-10-19 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=613ms | quality=1.00 | cache_age=111s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2
2026-10-19 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 400ms (표본 20분)
2026-10-19 09:41:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3493ms | quality=1.00 | cache_age=128s | exceptions_10m=0
2026-10-19 09:42:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=562ms | quality=1.00 | cache_age=1s | exceptions_10m=0
  …
2026-10-19 14:23:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=375ms | quality=1.00 | cache_age=165s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-19 14:52:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3471ms | quality=1.00 | cache_age=73s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-19 14:53:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=305ms | quality=1.00 | cache_age=129s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-19 15:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=735ms | quality=1.00 | cache_age=183s | exceptions_10m=3 | exc_tags=[SHAP]×2 [CB③-P4]×1
2026-10-19 15:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=337ms | quality=1.00 | cache_age=59s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 14 | 09:00:01 | 15:00:01 | level=WARNING degraded=OFF | latency=1232ms | quality=1.00 | cache_age=51s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2 |

**채널** — `HEALTH`×29

**컴포넌트 상위 15** — `Health`×28, `HealthTrend`×1

### `logs/retrain_eod_20261019.log` — 21.5KB · 141행 · 최종 15:53:32

- 형식 평문 · 시각 인식 141행 · WARNING=16, INFO=125

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 15:50:03,264 [INFO] EOD_RETRAIN: =======================================================
2026-10-19 15:50:03,264 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-19 15:50:03,265 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-19 15:50:03,265 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-19 15:50:03,265 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-19 15:53:32,918 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0514 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-19 15:53:32,920 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0807 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-19 15:53:32,923 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.04s
2026-10-19 15:53:32,928 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.04s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-19 15:53:32,929 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:38 | 15:52:33 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-10-16 14:38:00 ≥ 홀드아웃 시작=2026-10-12 11:00:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-16 14:38 >= holdout_start=2026-10-12 11:00 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-16 … |
| `GuardGhost` | 4 | 15:51:02 | 15:51:31 | 5m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-10-19 09:09:00까지)인데 acc.txt=0.3647는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-19 | 최신 2026-10-16 · 기준 6거래일. 복구: python scripts/collect_regular_futures.py --from 20261019 --to 20261019 |
| `OptionFlowFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-13(최신봉 15:33) | 기준 5거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\<YYYYMMDD>_OPTION_BACKFILL.log |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 18193/43974 제외 (418차 결정 1) — 남은 25781행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/25781행 제외 (559차 P1'-2) — 남은 24335행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `Retrain` | 1 | 15:50:50 | 15:50:50 | 3m 교체 보류(EOD 모델가드) — acc 하락 0.0282 > 허용 0.0250 (new=0.3479 old=0.3761) — 참고용 저장, 구모델 유지 |
| `RegimeFingerprint` | 1 | 15:53:32 | 15:53:32 | 백필 0행 제외 — 필터가 무효일 수 있다. 21750행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×67, `SIGNAL`×37, `EOD_RETRAIN`×27, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×30, `Retrain`×22, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `GuardGhost`×4, `RegimeFingerprint`×4, `WaitDC`×2

### `logs/retrain_intraday_20260811_101959.log` — 4.5KB · 39행 · 최종 10:20:41

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-11 10:19:59,552 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-11 10:19:59,552 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-11 10:19:59,552 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-11 10:19:59,552 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_3cddcfd9.json
2026-08-11 10:20:02,266 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-11 10:20:41,930 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.18s | old_acc=0.4414)
2026-08-11 10:20:41,992 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-11 10:20:41,992 [INFO] LEARNING: [Retrain] 완료 | 39.7초 | 성공=6/6 호라이즌
2026-08-11 10:20:41,993 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 42.4s 데이터=4800행
2026-08-11 10:20:41,995 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_3cddcfd9.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -508642원
════════════════════════════════════════════════════
2026-10-19 15:40:17 [WARNING] SYSTEM: [LiveDBG] _refresh_pnl_history 총 215ms
2026-10-19 15:45:00 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 239.7ms | size=1994x937 candles=410 grid=38.8 spans=30.7 candles=52.1 dir=1.5 regime=8.5 markers=102.9 axes=1.1 cross=0.0 | slow_cnt=2…
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) | 13 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 4 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 9 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 4 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 4 |
| 차단(`[차단]`) | 82 |
| 사이저 호출(`[Sizer]`) | 2 |

> 🔴 **엔진 진입 0건인데 계좌 체결 4건**(외부표식 0 · 피터2 4 · 판별불가 0) — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.
>
> 별도로 **가상 장부 진입 9건**이 `[Position] 진입` 에 섞여 있다 — 실주문이 없으므로 계좌 체결·손익과 무관하다(아래 「가상 장부」 표).

### 포지션 4건 · 승 1 (25%) · 합계 -10.04pt (-508,642원)  ※ 레그 4행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:04:45 | 피터2 | SHORT | 1 | — | 1 | -3.94 | -198,640 | 하드스톱(틱) |
| 09:09:07 | 피터2 | SHORT | 1 | — | 1 | -5.02 | -252,649 | 하드스톱(틱) |
| 10:20:21 | 피터2 | SHORT | 1 | — | 1 | +3.62 | +179,325 | 하드스톱(틱) |
| 13:12:14 | 피터2 | SHORT | 1 | — | 1 | -4.70 | -236,678 | 하드스톱(틱) |

**출처별 소계** — 피터2 4건 -508,642원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「피터2」는 `[Peter2] 진입`이 동반된 보조 로직 자리로 역시 엔진 성적이 아니다. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**가상 장부 9건(청산 9 · 합계 +633,074원) — 실주문 없음, 엔진·계좌 손익 아님**

| 진입 | 주체 | 방향 | 수량 | hz | 가상 pt | 가상 net(원) | 가상 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:33:09 | 신동 | LONG | 1 | — | -4.88 | -245,644 | 가상:하드스톱 |
| 09:39:09 | 신동 | SHORT | 1 | — | -2.54 | -128,636 | 가상:하드스톱 |
| 09:45:09 | 신동 | LONG | 1 | — | +3.42 | +169,351 | 가상:외부목표 |
| 09:50:09 | 신동 | SHORT | 1 | — | +6.16 | +306,350 | 가상:신동1차 |
| 10:13:09 | 신동 | LONG | 1 | — | -4.86 | -244,663 | 가상:하드스톱 |
| 10:59:09 | 신동 | SHORT | 1 | — | -1.58 | -80,657 | 가상:신동미러:SL |
| 11:02:09 | 신동 | LONG | 1 | — | +13.76 | +686,340 | 가상:신동시간청산 |
| 11:35:01 | 미륵 | LONG | 1 | 3m | +3.10 | +153,338 | 가상:TP2(전량) |
| 11:41:04 | 미륵 | LONG | 1 | 1m | +0.38 | +17,295 | 가상:하드스톱 |

> ⚠ 이 표는 `[Virtual] … 가상진입`/`가상청산` 로그로 조립한 **가상 장부**다. 같은 초에 `[Position] 진입` 이 찍혀 진입 건수에는 잡히지만 체결이 없다 — 3원 대사(로그·DB·브로커)에서 로그 쪽이 더 많아 보이면 먼저 이 표를 뺄 것.

**청산 레그 4행** (부분청산 0 · 전량청산 4)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:06:30 | 전량 | 1 | -3.94 | -198,640 | 하드스톱(틱) |
| 10:11:02 | 전량 | 1 | -5.02 | -252,649 | 하드스톱(틱) |
| 11:37:43 | 전량 | 1 | +3.62 | +179,325 | 하드스톱(틱) |
| 15:04:26 | 전량 | 1 | -4.70 | -236,678 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×4

> 최종 청산이 하드스톱·손절 계열인 포지션 4/4건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -508,642 = 포지션합 -508,642 → OK · `[청산 완료]` 4건 = 조립 포지션 4건 → OK

### CB③ 판정 가능 시간 — **81분 / 370분 (22%)**

acc30m 버퍼 리셋 2회 · 그때 버린 표본 60건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 13건

| 시각 | 출처 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|---|
| 09:04:45 | 피터2 | SHORT | 1 | 863.02 | — | — |
| 09:09:07 | 피터2 | SHORT | 1 | 868.12 | — | — |
| 09:33:09 | 가상 | LONG | 1 | 865.38 | — | — |
| 09:39:09 | 가상 | SHORT | 1 | 860.96 | — | — |
| 09:45:09 | 가상 | LONG | 1 | 868.08 | — | — |
| 09:50:09 | 가상 | SHORT | 1 | 868.66 | — | — |
| 10:13:09 | 가상 | LONG | 1 | 875.36 | — | — |
| 10:20:21 | 피터2 | SHORT | 1 | 881.74 | — | — |
| 10:59:09 | 가상 | SHORT | 1 | 871.92 | — | — |
| 11:02:09 | 가상 | LONG | 1 | 873.82 | — | — |
| 11:35:01 | 가상 | LONG | 1 | 874.58 | 3m | neutral |
| 11:41:04 | 가상 | LONG | 1 | 878.5 | 1m | neutral |
| 13:12:14 | 피터2 | SHORT | 1 | 883.32 | — | — |

계약수 분포 — 1계약×13

등급 분포 — `A급(원시C)`×2

**진입한 건들의 체크리스트 미통과 항목** — `fore`×2, `prev`×1, `risk`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×2

실제 진입 계약수 — **1계약**×13

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×2

### 차단 사유 82건 · 31종

| 건수 | 사유 |
|---|---|
| 43 | 등급X — 미통과 항목: 2_confidence |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 9_risk, 11_countertrend |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 9_risk, 11_countertrend |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 9_risk, 11_countertrend |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 9_risk |
| 2 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.8pt > ATR×5.0=17.0pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 24.1pt > ATR×5.0=16.4pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 24.2pt > ATR×5.0=17.1pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.9pt > ATR×5.0=14.6pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.9pt > ATR×5.0=13.9pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 24.2pt > ATR×5.0=14.8pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 29.0pt > ATR×5.0=14.3pt (시가=841.08 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.6pt > ATR×5.0=13.2pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.5pt > ATR×5.0=12.7pt (시가=841.08 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.4pt > ATR×5.0=12.8pt (시가=841.08 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×43, `3_vwap`×19, `6_foreign`×19, `9_risk`×14, `4_cvd`×12, `5_ofi`×12, `7_prev_bar`×10, `11_countertrend`×8, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 12건 · 최대 4891ms · 5초 초과 0건

상위 — 4891ms, 4562ms, 4422ms, 4203ms, 4109ms, 3859ms, 3750ms, 3500ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261019_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:17 2026-10-19 15:40:17 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 24분/일 < 하한 60분 — 금일 32분. | ConfFloorGuard 도달가능 0분 · 도달불가 99분 · 재지않음 271분
--- ConstOut ×6(표본)
09:39:00 2026-10-19 09:39:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(5m=0.3688)
11:39:00 2026-10-19 11:39:00 [WARNING] SYSTEM: [ConstOut] ['10m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(10m=0.4350)
12:59:00 2026-10-19 12:59:00 [WARNING] SYSTEM: [ConstOut] ['10m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(10m=0.4168)
13:50:00 2026-10-19 13:50:00 [WARNING] SYSTEM: [ConstOut] ['10m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(10m=0.4123)
--- [CB] ×3(표본)
09:06:30 2026-10-19 09:06:30 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:11:02 2026-10-19 10:11:02 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
15:04:27 2026-10-19 15:04:27 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:06:30 2026-10-19 09:06:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:09:30)
09:06:30 2026-10-19 09:06:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:09:30)
10:11:02 2026-10-19 10:11:02 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:14:02)
10:11:02 2026-10-19 10:11:02 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:14:02)
--- [SHAP] 슬로우 ×8(표본)
11:35:01 2026-10-19 11:35:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1037ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:43:01 2026-10-19 11:43:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 943ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:10:01 2026-10-19 12:10:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 930ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:29:01 2026-10-19 12:29:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1056ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-19 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4562ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4562 band=INFO since_pipe_s=NA
08:41:16 2026-10-19 08:41:16 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3500 band=INFO since_pipe_s=NA
09:00:02 2026-10-19 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=0.1
09:05:02 2026-10-19 09:05:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20261019_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-19 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4363) | 앙상블 제외는 유지
09:39:00 2026-10-19 09:39:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:41:00 (const_output)
09:39:00 2026-10-19 09:39:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['5m']
09:39:00 2026-10-19 09:39:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['5m'] load=447ms fit=52ms total=503ms
--- HALT ×1(표본)
15:40:17 2026-10-19 15:40:17 [INFO] SYSTEM: [CB③계측] 조건성립 11분 / 판정가능 81분 / 파이프라인 370분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-19 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-10-19 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:10:00 2026-10-19 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:16:00 2026-10-19 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:16 2026-10-19 15:40:16 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:16 2026-10-19 15:40:16 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:08 2026-10-19 15:11:08 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:18 2026-10-19 15:40:18 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-10-19 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:18 2026-10-19 15:40:18 [INFO] SYSTEM: [Notify] ℹ️ [15:40:18] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:18 2026-10-19 15:40:18 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 401초
15:40:18 2026-10-19 15:40:18 [INFO] SYSTEM: 자동 종료 예약 — 416초 후 Qt 이벤트 루프 종료
```

### `logs/20261019_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
13:00:00 2026-10-19 13:00:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3586 < 필요 0.3820 (conf_floor=0.330, min_conf=0.382, span=0.0079, auc=0.551). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
09:35:00 2026-10-19 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0620 dir=+0)
09:35:00 2026-10-19 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-10-19 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-10-19 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0620 dir=+0)
--- WeightCollapse ×8(표본)
09:07:00 2026-10-19 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-10-19 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-10-19 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-19 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.461
--- 안전망 ×8(표본)
09:07:00 2026-10-19 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-19 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-19 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-19 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261019_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00158 auc=0.502 out_max=0.2959 (기준 auc<0.53 and span<0.020, 기저율=0.2952 n=105) → 보정 미적용, raw 통과
```

### `logs/20261019_HEALTH.log`
```
--- [ExitCooldown] ×2(표본)
11:41:04 2026-10-19 11:41:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=4113ms | quality=1.00 | cache_age=174s | exceptions_10m=3 | exc_tags=[ExitCooldown]×1 [Peter2]×1 [SHAP]×1
11:42:00 2026-10-19 11:42:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=385ms | quality=1.00 | cache_age=47s | exceptions_10m=3 | exc_tags=[ExitCooldown]×1 [Peter2]×1 [SHAP]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261019_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 18 | 09:04:45 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=862.96 — 진입 경로가 파라미터를 넘기지 … |
| 10:00 | 장중 초반 | 2 | 09:56:16 [INFO] 청산 SHORT @ 862.5 | PnL=+6.16pt (+306,350원) 수수료=1,650원 | 가상:신동1차 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 9 | 15:04:26 [INFO] 하드스톱(틱) SHORT 1ct tick=888.12 stop=888.12 → 주문 전송 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:16 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261019_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:08 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:52:39 [WARNING] A056B 실측=-1.54 n=7 spread=0.37 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.54 | 직전일=-2.08(prev_day:2026-10-1… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 48 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 86 | 09:54:00 [WARNING] paintEvent slow 83.0ms | size=1994x950 candles=70 grid=28.9 spans=7.3 candles=8.8 dir=0.3 regime=4.4 markers=… |
| 12:00 | 장중 중간점 | 85 | 11:54:01 [WARNING] paintEvent slow 122.2ms | size=1994x950 candles=190 grid=30.0 spans=14.4 candles=26.2 dir=1.0 regime=7.7 mark… |
| 14:00 | 장중 후반 · 장중 재학습 | 86 | 13:54:00 [WARNING] 5분 누적 수익률 +0.269% (임계 ±0.223%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 143 | 15:04:01 [WARNING] paintEvent slow 122.4ms | size=1994x950 candles=380 grid=27.3 spans=15.1 candles=36.2 dir=1.4 regime=7.6 mark… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 105 | 15:12:00 [WARNING] paintEvent slow 204.3ms | size=1994x937 candles=388 grid=20.0 spans=14.4 candles=40.4 dir=1.8 regime=13.3 mar… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 17 | 15:34:00 [WARNING] paintEvent slow 119.5ms | size=1994x937 candles=410 grid=20.4 spans=13.4 candles=34.6 dir=1.4 regime=6.0 mark… |
| 15:47 | EOD 재학습(py310_64) 완료 | 2 | 15:45:00 [WARNING] paintEvent slow 239.7ms | size=1994x937 candles=410 grid=38.8 spans=30.7 candles=52.1 dir=1.5 regime=8.5 mark… |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261019_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 102 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=4572 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 140 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 265 | 08:54:00 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 243 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 198 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 202 | 13:54:00 [INFO] code=A056B from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 233 | 15:04:00 [INFO] code=A056B from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 166 | 15:12:00 [INFO] code=A056B from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 68 | 15:34:00 [INFO] code=A056B from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 12 | 15:41:08 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:08 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261019_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0239) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 110 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 242 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 131 | 09:54:00 [WARNING] 신뢰도 미달 35.8% < 39.5% → 강제 X등급 |
| 12:00 | 장중 중간점 | 113 | 11:54:00 [WARNING] 신뢰도 미달 35.7% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 124 | 13:54:01 [WARNING] 1m 'macro_vix' scale=0.0718 → floor=0.10 적용 (z-score 폭발 방지) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 92 | 15:04:00 [WARNING] ts=15:03 horizon=1m age=9m max_z=+7.84(is_close_volatile) extreme=5 adj=4 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:16 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261017 | 12:11 | 로그 본문 |
| 20261016 | 15:47 | 로그 본문 |
| 20261015 | 15:47 | 로그 본문 |
| 20261014 | 17:41 | 로그 본문 |
| 20261013 | 19:02 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261019** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 증상 → 원인 → 결정 (이월 — 1-1 CREON 좀비 세션 충돌)
### 신규 1-5 — 수익률향상_누적대장 10-15 등록 누락 (소급 발견·해소)
### 신규 1-6 — 697차 구현 코드 당일 미커밋
### 신규 1-7 — 섀도우 TB(검증 캠페인) 재학습 강제 종료 (표본 1건, 확인 필요)
### 이월(변경 없음) — 1-1(CREON)·1-2(F-1 SessionStateDrop)·1-3(머지커밋 PC태그 확인필요)·1-4(피터2 수신오류, 697차 수정 배포·라이브 검증 대기)
## 2026-10-16 (MW0601 697차 후속 — 장후 자동조치: F-26)
## 2026-10-19 (MW0601 — 장전 점검)
## 2026-10-19 (MW0601 — 장중 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
없음. 1-1(access violation)·1-2(메인스레드 블로킹) 모두 기존 TODO(606-4, O-p2) 계승, 관측일만 추가(함정① 방지).
2. 신규 관측 등록(O-p1·O-p2·O-p3) — 전부 "확인 필요" 등급, 장중 점검이 판정/판정보류/다음거래일이월 중 하나로 닫을 것.
3. 주간(월요일) GBM 재학습 0회는 정상 판정 — `main.py` 코드로 직접 확인(`_eod_retrain_ok` 조건), 483차 "재학습 0회가 정상인 날이 있다" 원칙의 실제 사례로 추가.
4. 697-1(Chrome 확장 재로드)은 로그 증거(rate limit 헤더 값 정상 수신)로 **유력 해소**로 처리하되, 코웍 환경에서 `receiver.py --check`를 직접 실행하는 것은 이 환경(리눅스 샌드박스)에서는 의미가 없다는 점을 다음 세션을 위해 기록한다 — 로컬호스트 접속 시도는 반드시 Windows 본체에서 해야 유효하다.
5. 이 계정의 앱 저장 스킬 사본이 저장소 정본보다 두 세대(538차분) 낡았음을 사용자 조치 3번으로 전달 — 이 세션은 스킬 저장 도구에 접근할 수 없어 직접 갱신하지 못함.

**Why**: 함정①(판정≠결정) 방지 — 606-4·O-p2·F-24를 전부 grep으로 먼저 확인한 뒤 신규가 아님을 검증했다. 계측 4원칙②(미제출≠일치) 준수 — 주간 재학습 트리거 로그가 없는 것을 곧바로 "정상"으로 쓰지 않고 `main.py` 코드의 조건문을 직접 읽어 근거를 확보한 뒤에만 정상으로 판정했다.

**How to apply**: 해당 없음(장전 점검 세션 — 관측·판정만, 코드 변경 없음).

**검증**: O-p1(피터2 오프셋 spread)·O-p2(캐너리 z경고 재상승)·O-p3(옵션체인 재수집 타이밍)은 다음 장중 점검이 재측정값으로 판정. 697-1은 사용자가 `chrome://extensions`에서 Mireuk Peter2 Collector 버전이 1.1.0인지 직접 확인하면 완전히 닫힌다.

⚠ **코드 변경 없음(장전 점검 세션 — 라이브 프로세스 실행 중, 08:57 KST경 예약 실행).** 라이브 DB 스캔 없음(수집기는 로그·설정·git 전용).

## 2026-10-19 (MW0601 — 장중 점검)

**증상/확인 대상**: (1) 09:00~12:26 매분 루프 207/207분(100%) 생존, 10분 이상 공백 0건 — 정상. (2) 장전이 등록한 관측 3건 처분: O-p1(피터2 오프셋 spread 불안정)은 08:58~11:23 구간 n=30까지 표본이 쌓였는데도 spread가 0.31~0.40 사이에서 전혀 0.30 이하로 내려오지 않아 "불안정 지속"으로 확정, 이상점 1-3으로 격상 등록(Fix 없음 — 표본 1일·보조로직 전용 지표). O-p2(캐너리 z경고 재상승)는 08:55:09·08:59:09 두 번만 측정되고 이후(09:00~12:26) 재측정 로그가 전혀 없어 판정 자체가 불가능 — 판정보류로 장후 이월. O-p3(옵션체인 09:01:26 재수집)은 과거 633-4 선례(08:41부터 5분 간격 정상 재수집 패턴)와 일치 확인되어 해소 처리. (3) 핵심 모델(엔진) 실주문 0건, 계좌 체결 3건 전부 피터2(보조로직) 경로 — 10-13 "엔진 0·피터2 6" 사례와 같은 계열, 신규 아님. 손익 -271,964원(2패1승, 포지션 기준). (4) `[PositionFallback]` 10건 재현 — 기존 F-5 계승, 신규 Fix 없음. (5) `[ChartDBG] paintEvent slow` 1,351건(12:26 기준) — 기존 F-1p 계승. 과거(09-15·09-16) 같은 시각 기준치(16,858~20,902건)보다 현저히 낮으나 원인 조사는 이번 세션 범위 밖, 단정하지 않음.

**결정**:
1. 신규 이상점 1-3(P2) 등록 — 피터2 오프셋 보정값 불안정 지속(spread>0.30, n=30까지 미해소). Fix 미등록(보조로직 전용·표본 부족·장중 코드변경 금지).
2. O-p2는 판정보류 — 장후 점검에서 하루 전체 Canary 측정 횟수를 재확인하고 "장중 미측정이 설계상 정상인지"를 코드로 확인할 것.
3. 그 외 신규 이상점·Fix 등록 없음(함정① 방지 — 기존 F-5·F-1p·F-24 계승 확인).
4. DB 조회·코드 변경·커밋 전부 하지 않음(장중 세션 규칙 준수). 인덱스락 없음(`git_lock_guard.py --check` rc=0).

**Why**: 313차 원칙 — O-p1은 표본이 충분(n=30)해져 "불안정하다"는 관측 자체는 확정할 수 있지만, 오늘 보조로직 손익과의 인과관계는 하루치 표본으로 주장하지 않는다(상관조사 미시행, 인과주장 아님).

**How to apply**: 1-3은 장후 점검이 하루 치 전체(피터2 오프셋 안정화 여부)로 최종 판정한다. O-p2는 장후가 `grep -c "Canary" logs/20261019_*.log`로 재확인.

**검증**: 라이브 미검증 — 장후 점검(오늘)에서 하루 전체 추이로 재확인.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
### 2026-10-16 (MW0601 — 장전 점검)
### 2026-10-16 (MW0601 — 장중 점검)
### 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도) — 장중 1-4 / G-2 후속
### 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-16 (MW0601 697차 후속 — 장후 자동조치)
### 2026-10-19 (MW0601 — 장전 점검)
## 2026-10-19 (MW0601 — 장중 점검)
```

미완료 체크박스 **3237건** (끝에서 30건)
```
- [ ] **O-p3 (확인 필요, P2)** 커밋 `271ddbd`(머지 커밋) PC명 태그 누락 — 과거 머지 커밋이 태그 예외로 다뤄진 전례가 있는지 미조사. 반복 관측되면 컨벤션 명문화 검토.
- [ ] (O-p2 지속) 메인 스레드 블로킹 당일 합계 6건(최대 4468ms) — 장후 누계로 재평가.
- [ ] **1-4 / G-2 (신규, P2)** 피터2(`tools/peter2_live/receiver.py`) X 페이지 'Top' 탭 조회 실패 재발(오늘 28회+, 10-12 39회와 동일 계열) — 마지막 성공 응답 짧은 캐시 + 재시도, 장시간(예: 5분) 지속 시만 별도 경보로 전환 제안. 적용은 장후 이후 사용자 승인 필요.
- [ ] **O-i1 참고 (366차 연계)** 11:27:00 A급(원시C) 신호에서 GradeEVGuard(A등급 n=58 평균순EV=-6062원)·ChaseForeignComboGuard 섀도 동시 트리거 — 366차 "다음 A등급 라이브 확인" 데이터 포인트 1건 추가. 섀도 가드 활성화 여부는 별개 안건(주간회의).
- [ ] (참고) `report_append_marker.py release`가 코웍 마운트에서 마커 파일을 못 지움(`os.remove` 거부) — 다음 국면(장후) 세션이 이 마커를 "병행 세션"으로 오인하지 않도록 유의. 삭제 권한 요청은 하지 않음(경미, max-age 경과로 자연 정리됨).
- [ ] **697-1 (사용자, 10-19 장전까지)** `chrome://extensions` → Mireuk Peter2 Collector 새로고침, 버전 **1.1.0** 확인. 안 하면 F-1–F-3 미적용.
- [ ] **697-2 (10-19 장후)** `python tools/peter2_live/latency_report.py 2026-10-19` — ① `RATE` 줄 존재(없으면 `docs/피터2수집/02` §5) ② 사전등록 p90 ≤ 90초 판정 ③ 창별 rem 감소폭 vs 우리 관측 수 → 다른 소비자 유무. 판정 나무: `docs/피터2수집/…
- [ ] **697-3 (조건부, 사용자 결정)** 697-2 가 공유 소비를 보이면 F-5 계정 분리(MW0601 전용 X 계정 — 조율 불필요). 혼자 소진이면 RELOAD_SEC 역산, 그래도 FAIL 이면 F-4 프로필 폴백(답글형 지시 비율 선측정).
- [ ] **697-4 (장전 점검 항목)** `python tools/peter2_live/receiver.py --check` 의 `started` 가 당일 아침인지 — 10-15 13:43 수신기가 10-16 장 마감까지 살아 옛 코드로 돌았다.
- [ ] **1-7 (확인 필요, P2)** 섀도우 TB 재학습 강제종료(`rc=STATUS_CONTROL_C_EXIT`) 원인 조사 — 표본 1건, 반복되면 승격.
- [ ] (이월, 변경 없음) **CREON-M1 (P0)** 장후 API 세션 정리 — 적용 시간대 사용자 결정 대기. **CREON-M2·M3 (P1)** 좀비 감지·팝업 자동처리. **CREON-M4** CREON-M1 적용 후 재평가.
- [ ] (이월, 변경 없음) **L-2·L-3·L-5·L-6·L-7** CREON 런처 잔여 Fix — 기동·로그인 흐름 변경, 사용자 결정 후 별도 세션.
- [ ] (이월, 변경 없음) **F-1** session_state 마커 유실(오늘도 재발, 보완 경로로 무해) · **F-24** MAX_CONTRACTS 기대값 수집기 쪽 정정(참고 사안, 조치 불필요) · **1-3** 머지 커밋 PC태그 과거 전례 확인 필요.
- [ ] (이월, 변경 없음) **697-1** Chrome 확장 재로드(사용자, 10-19 장전까지) · **697-2** 10-19 장후 `latency_report.py` 라이브 검증 · **697-3·697-4** 조건부 후속.
- [ ] (이월, 변경 없음) **G-7** 피터2 연속손절 조기정지 · **G-8** 피터2 추세필터 — 오늘 CASE-1·3·4가 같은 패턴 재확인(10-13 선례와 동일 계열), 여전히 사용자 결정 대기(C등급).
- [ ] (참고) **P5-18** 표본 2건/2거래일(`docs/정기점검/수익률향상_누적대장.md`) — 10-15 오후·10-16 오전 `ConfFloorGuard` 재발. 다음 장후가 표본 갱신.
- [ ] (참고) 오늘 Peter2Trail(690차 후속) CASE-2에서 Δ+5.52pt 효과 실측 확인(섀도 대조 로그 자체 산출) — 기존 기능의 실거래 검증 데이터 포인트 1건, 신규 제안 아님.
- [ ] **CREON-M2** 계획(「예」 금지)과 달리 `d81c079`는 「예」 유지 + PlusDisconnect 무조건 요청 — 효과 미검증(`was_connected` 출력). 다음 좀비 재현일에 판독.
- [ ] **(사용자)** 697-1 Chrome 확장 새로고침 v1.1.0 — 여전히 사용자 몫.
- [ ] **O-p1 (신규, 확인 필요)** 피터2 오프셋 보정값(A056B) 08:58:09 spread=0.31>0.30 "불안정"(표본 13개) — 09:30 전후 재측정에서 0.30 이하로 복귀하는지 장중 점검이 판정.
- [ ] **O-p2 (신규, 확인 필요)** 캐너리 z-경고 피처 수 08:59:09 10개로 재상승(08:55 임계접촉→재적합→08:59 8개 이후) — 09:10~09:15 재측정값이 8개 이하로 복귀하는지 장중 점검이 판정.
- [ ] **O-p3 (신규, 확인 필요)** 옵션체인 재수집이 09:01:26(개장 1분 후)에 완료 — 과거 타이밍 기준 판정 기록 부재. 다른 평일과 비교해 정상 범위인지 장중/다음 점검이 확인.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation(1-1, main_dashboard.py:7434 _build) 원인 조사 착수 여부 — 10-19로 관측일 추가, 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **CREON-M1 (P0)** 장후 API 세션 정리 적용 시간대 — 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **F-24** `MAX_CONTRACTS` 수집기 기대값(3) 정정 — 실제 운용값 1은 의도값, 수집기 쪽 기대값만 낡음.
- [ ] (이월, 변경 없음) **F-1** `session_state.json` 마커 유실(SessionStateDrop) — 10-19 재발, EOD 마커 파일 보완 경로로 실질 피해 없음 재확인.
- [ ] **697-4 관련 메모** `python tools/peter2_live/receiver.py --check`는 코웍 리눅스 샌드박스에서 실행하면 Windows 본체가 아닌 다른 네트워크 네임스페이스로 접속을 시도해 항상 Connection refused가 난다 — 이 환경에서는 로그 파일 증거(START 시각·최근 RATE 줄)로 대체 판정…
- [ ] (참고) 이 계정 앱 저장 스킬 사본(rev 2026-08-26e)이 저장소 정본(rev 2026-09-07, 538차)보다 낡음 — 사용자가 해당 PC에서 재저장하면 해소. 이 세션은 스킬 저장 도구에 접근 불가.
- [ ] **1-3 (P2, 장후 판정 대기)** 피터2 오프셋 보정값(`PETER2_OFFSET_TOL_PT`) spread가 08:58~11:23 구간 n=30까지 쌓여도 0.31~0.40 사이로 전혀 0.30 이하로 내려오지 않음 — 장후 점검이 하루 전체 추이로 "안정화됐는지/계속 불안정했는지" 최종 판정. 안정화 안 되면 `main.py:_pe…
- [ ] **O-p2 (판정보류 → 장후)** 캐너리 z경고 재상승 — 09:00~12:26 구간 재측정 로그 0건. 장후 점검이 `grep -c "Canary" logs/20261019_*.log`로 하루 전체 측정 횟수 재확인하고, 장중 미측정이 설계상 정상(1회성 장전 체크)인지 `main.py`에서 확인.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
점검/수익률향상_누적대장.md`) — 10-15 오후·10-16 오전 `ConfFloorGuard` 재발. 다음 장후가 표본 갱신.
- [ ] (참고) 오늘 Peter2Trail(690차 후속) CASE-2에서 Δ+5.52pt 효과 실측 확인(섀도 대조 로그 자체 산출) — 기존 기능의 실거래 검증 데이터 포인트 1건, 신규 제안 아님.

### 2026-10-16 (MW0601 697차 후속 — 장후 자동조치)
- [x] **F-26** 697차 피터2 수집 개선분 커밋 → `7a5275b`(ratelimit_hook.js 포함). 106 passed.
- [x] **CREON-M1·M3** 이미 `d81c079`(692차 후속4)로 구현·커밋됨 — 예약작업 `\Mireuk\Mireuk_EodSessionCleanup` 16:30. 라이브 판정은 O-t1(10-19 08:35대 크래시 부재).
- [ ] **CREON-M2** 계획(「예」 금지)과 달리 `d81c079`는 「예」 유지 + PlusDisconnect 무조건 요청 — 효과 미검증(`was_connected` 출력). 다음 좀비 재현일에 판독.
- [ ] **(사용자)** 697-1 Chrome 확장 새로고침 v1.1.0 — 여전히 사용자 몫.

### 2026-10-19 (MW0601 — 장전 점검)
- [ ] **O-p1 (신규, 확인 필요)** 피터2 오프셋 보정값(A056B) 08:58:09 spread=0.31>0.30 "불안정"(표본 13개) — 09:30 전후 재측정에서 0.30 이하로 복귀하는지 장중 점검이 판정.
- [ ] **O-p2 (신규, 확인 필요)** 캐너리 z-경고 피처 수 08:59:09 10개로 재상승(08:55 임계접촉→재적합→08:59 8개 이후) — 09:10~09:15 재측정값이 8개 이하로 복귀하는지 장중 점검이 판정.
- [ ] **O-p3 (신규, 확인 필요)** 옵션체인 재수집이 09:01:26(개장 1분 후)에 완료 — 과거 타이밍 기준 판정 기록 부재. 다른 평일과 비교해 정상 범위인지 장중/다음 점검이 확인.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation(1-1, main_dashboard.py:7434 _build) 원인 조사 착수 여부 — 10-19로 관측일 추가, 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **CREON-M1 (P0)** 장후 API 세션 정리 적용 시간대 — 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **F-24** `MAX_CONTRACTS` 수집기 기대값(3) 정정 — 실제 운용값 1은 의도값, 수집기 쪽 기대값만 낡음.
- [ ] (이월, 변경 없음) **F-1** `session_state.json` 마커 유실(SessionStateDrop) — 10-19 재발, EOD 마커 파일 보완 경로로 실질 피해 없음 재확인.
- [x] **697-1 (유력 해소)** `logs/peter2_receiver_20261019.log`에 "RATE ... rem=48/50" 형태 한도 헤더 값이 정상 수신·기록됨을 확인 — 확장 v1.1.0 반영 정황. 다만 사용자가 `chrome://extensions`에서 버전 직접 확인하면 완전히 닫힘(사용자 조치 아님, 참고).
- [ ] **697-4 관련 메모** `python tools/peter2_live/receiver.py --check`는 코웍 리눅스 샌드박스에서 실행하면 Windows 본체가 아닌 다른 네트워크 네임스페이스로 접속을 시도해 항상 Connection refused가 난다 — 이 환경에서는 로그 파일 증거(START 시각·최근 RATE 줄)로 대체 판정할 것. 다음 세션을 위한 운영 메모(조치 항목 아님).
- [ ] (참고) 이 계정 앱 저장 스킬 사본(rev 2026-08-26e)이 저장소 정본(rev 2026-09-07, 538차)보다 낡음 — 사용자가 해당 PC에서 재저장하면 해소. 이 세션은 스킬 저장 도구에 접근 불가.

## 2026-10-19 (MW0601 — 장중 점검)
- [ ] **1-3 (P2, 장후 판정 대기)** 피터2 오프셋 보정값(`PETER2_OFFSET_TOL_PT`) spread가 08:58~11:23 구간 n=30까지 쌓여도 0.31~0.40 사이로 전혀 0.30 이하로 내려오지 않음 — 장후 점검이 하루 전체 추이로 "안정화됐는지/계속 불안정했는지" 최종 판정. 안정화 안 되면 `main.py:_peter2_measure_offset()` 또는 `PETER2_OFFSET_TOL_PT` 임계 재검토를 사용자 승인 대기 항목으로 등록할 것(장중에는 Fix 제안만, 적용 안 함).
- [ ] **O-p2 (판정보류 → 장후)** 캐너리 z경고 재상승 — 09:00~12:26 구간 재측정 로그 0건. 장후 점검이 `grep -c "Canary" logs/20261019_*.log`로 하루 전체 측정 횟수 재확인하고, 장중 미측정이 설계상 정상(1회성 장전 체크)인지 `main.py`에서 확인.

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

### `data/dailycheck_markers/claude-20261019-intra-cowork-intra-20261019.json` — 174B · 10-19 12:26:27
```json
{
 "pc": "claude",
 "date": "20261019",
 "phase": "intra",
 "session": "cowork-intra-20261019",
 "pid": 7,
 "started_epoch": 1792380387.6740777,
 "started_at": "2026-10-19 03:26:27"
}
```

### `data/dailycheck_markers/claude-20261019-pre-cowork-pre-20261019.json` — 170B · 10-19 09:03:57
```json
{
 "pc": "claude",
 "date": "20261019",
 "phase": "pre",
 "session": "cowork-pre-20261019",
 "pid": 6,
 "started_epoch": 1792368237.8175673,
 "started_at": "2026-10-19 00:03:57"
}
```

### `data/heartbeat_MW0601_20261019.json` — 244B · 10-19 15:46:51
```json
{
 "pid": 4572,
 "written_at": "2026-10-19T15:46:51",
 "beat_epoch": 1792392408.3739173,
 "beat_age_sec": 3.2,
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

### `data/peter2_live/trail_state_2026-10-19.json` — 51B · 10-19 15:04:27
```json
{
 "date": "2026-10-19",
 "trail": null,
 "ghosts": []
}
```

### `data/peter_feed/_raw/2026-10-19.jsonl` — 5.7KB · 10-19 15:08:22
```json
JSONL 29행 ⏎ 첫: {"id": "2111971403377561735", "dt": "2026-10-19T00:03:15.000Z", "text": "865 하방돌파시 매도. 손절가 869", "seen_at": "2026-10-19T09:04:20+09:00", "src": "live"} | {"id": "2111971777853468772", "dt": "2026-10-19T00:04:45.000Z", "text": "865 매도 체결.", "seen_at": "2026-10-19T09:05:40+09:00", "src": "live"} | {"id": "2111972308869071027", "dt": "2026-10-19T00:06:51.000Z", "text": "869 손절", "seen_at": "2026-10-19T09:07:00+09:00", "src": "live"} ⏎ 끝: {"id": "2112059589953044807", "dt": "2026-10-19T05:53:41.000Z", "text": "", "seen_at": "2026-10-19T14:54:59+09:00", "kind": "empty", "src": "live"} | {"id": "2112059967557763248", "dt": "2026-10-19T05:55:11.000Z", "text": "", "seen_at": "2026-10-19T14:56:19+09:00", "kind": "empty", "src": "live"} | {"id": "2112062986508767565", "dt": "2026-10-19T06:07:10.000Z", "text": "890 손절. \n\n13+3+7+5 = 28p 손실.", "seen_at": "2026-10-19T15:08:22+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-19 15:53:32**

| 키 | 값 | 수집 대상일(2026-10-19)과 일치 |
|---|---|---|
| `date` | 2026-10-19 | 예 |
| `p8_last_success_date` | 2026-10-19 | 예 |
| `eod_retrain_ok_date` | 2026-10-19 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-19 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (3일 전: 2026-10-16) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-19 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-16) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261019_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 4572: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 4572 | 08:40:45 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 231개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261019-점검리포트.md` | 26.9KB | 10-19 12:35 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md` | 81.1KB | 10-19 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md` | 59.6KB | 10-19 08:59 |
| `docs/정기점검/매일점검/MW0602-20261017-긴급알림메일-종합검토.md` | 14.1KB | 10-17 11:49 |
| `docs/정기점검/매일점검/MW0602-20261015-청산거부113분-딥다이브.md` | 21.3KB | 10-17 10:31 |
| `docs/정기점검/매일점검/MW0601-20261016-점검리포트.md` | 75.9KB | 10-16 17:28 |
| `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` | 8.9KB | 10-16 16:40 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_post.md` | 97.3KB | 10-16 16:19 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261016.json` | 3.1KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261016.md` | 5.4KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261016.json` | 38.9KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20261016.md` | 32.1KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261016.json` | 127.6KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261016.md` | 193.6KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261008.json` | 3.0KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261008.md` | 5.0KB | 10-08 15:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MAX_CONTRACTS` = `1` (기대 `3`) — 431차 10→3 인하. 실전 자본 확정 시 재산출 대상
2. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
3. **엔진 진입 0건 / 계좌 진입 4건**(그중 외부표식 0건 · 피터2 4건 · 판별불가 0건 · 별도 가상 장부 9건) — 차단 82건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
4. 포지션 4건 중 최종청산이 하드스톱·손절 계열 **4건(100%)** — 손절 준수율 확인 필요 (레그 4행)
5. `logs/20261019_WARN.log`: **ConstOut** 6건(표본)
6. `logs/20261019_SYSTEM.log`: **ConstOut** 8건(표본)
7. `logs/20261019_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20261019_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20261019_LEARNING.log`: **축퇴** 8건(표본)
10. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
11. 미커밋 변경 15건 (실질 6건 · 코드 0건 · EOL 파생 0건)
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261019*.log` (Windows) / `grep 강제청산 logs/*20261019*.log`*