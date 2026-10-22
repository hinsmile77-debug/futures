# 미륵이 증거 다이제스트 — 2026-10-20 / POST

- 생성 2026-10-20 16:20:16 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-0194rtjzwq3lmqqx1xsyupa7/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261020` · `2026-10-20` · `261020` · `1020`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **42개** 파일 · 42개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `MW0601-{DATE}-intra-cowork_intra_{DATE}.json` | 1 | `data/dailycheck_markers/MW0601-20261020-intra-cowork_intra_20261020.json` | 173B | 10-20 12:26 |
| `MW0601-{DATE}-pre-cowork-0858.json` | 1 | `data/dailycheck_markers/MW0601-20261020-pre-cowork-0858.json` | 162B | 10-20 08:59 |
| `claude-{DATE}-post-cowork-postcheck-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261020-post-cowork-postcheck-20261020.json` | 176B | 10-20 16:20 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261020.log` | 136B | 10-20 06:33 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261020.txt` | 28B | 10-20 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261020.txt` | 28B | 10-20 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261020.txt` | 233B | 10-20 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261020.log` | 1.9KB | 10-20 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261020.log` | 275B | 10-20 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261020.json` | 243B | 10-20 15:46 |
| `launcher_{DATE}_084001_17359.log` | 1 | `logs/Mireuk_batch/launcher_20261020_084001_17359.log` | 2.4MB | 10-20 15:47 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261020.log` | 108B | 10-20 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261020.log` | 46.1KB | 10-20 16:10 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261020.log` | 491B | 10-20 16:15 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261020.log` | 19.9KB | 10-20 15:53 |
| `retrain_intraday_20260708_{DATE}56.log` | 1 | `logs/retrain_intraday_20260708_102056.log` | 4.6KB | 07-08 10:21 |
| `retrain_intraday_20260807_{DATE}59.log` | 1 | `logs/retrain_intraday_20260807_102059.log` | 4.5KB | 08-07 10:21 |
| `retrain_intraday_20260820_1{DATE}0.log` | 1 | `logs/retrain_intraday_20260820_110200.log` | 2.4KB | 08-20 11:02 |
| `retrain_intraday_20260901_{DATE}00.log` | 1 | `logs/retrain_intraday_20260901_102000.log` | 2.7KB | 09-01 10:20 |
| `retrain_intraday_{DATE}_105600.log` | 1 | `logs/retrain_intraday_20261020_105600.log` | 3.2KB | 10-20 10:56 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261020.log` | 88.4KB | 10-20 16:03 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261020.txt` | 43B | 10-20 15:47 |
| `strategy_report_{DATE}_154021.txt` | 1 | `data/daily_reports/strategy_report_20261020_154021.txt` | 2.4KB | 10-20 15:40 |
| `{DATE}.eod_ids.json` | 1 | `data/peter_feed/_raw/2026-10-20.eod_ids.json` | 437B | 10-20 16:10 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-20.jsonl` | 6.7KB | 10-20 15:23 |
| `{DATE}_0916_D.xls` | 1 | `data/db/option_hts/261020_0916_D.xls` | 482.8KB | 10-20 09:16 |
| `{DATE}_0945_D.xls` | 1 | `data/db/option_hts/261020_0945_D.xls` | 482.9KB | 10-20 09:45 |
| `{DATE}_1217_D.xls` | 1 | `data/db/option_hts/261020_1217_D.xls` | 483.1KB | 10-20 12:17 |
| `{DATE}_DATA.log` | 1 | `logs/20261020_DATA.log` | 439.0KB | 10-20 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261020_DEBUG.log` | 237.1KB | 10-20 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261020_HEALTH.log` | 3.8KB | 10-20 15:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20261020_HOGA.log` | 62.1MB | 10-20 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261020_LEARNING.log` | 282.5KB | 10-20 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261020_MICRO.log` | 1.1MB | 10-20 15:38 |
| `{DATE}_OPTION_BACKFILL.log` | 1 | `logs/20261020_OPTION_BACKFILL.log` | 330B | 10-20 16:20 |
| `{DATE}_PROBE.log` | 1 | `logs/20261020_PROBE.log` | 94.6KB | 10-20 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261020_REGULAR_COLLECT.log` | 8.8KB | 10-20 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261020_SIGNAL.log` | 513.4KB | 10-20 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261020_SYSTEM.log` | 1.0MB | 10-20 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261020_TRADE.log` | 19.2KB | 10-20 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261020_WARN.log` | 685.6KB | 10-20 15:46 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-20_tr.draft.txt` | 0B | 10-20 15:40 |

## 2. 코드·커밋 상태

- HEAD `87864966` · 브랜치 `v9-dev` · 미커밋 26건 · 실질 변경 6건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 6 · 미추적 20 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
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
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261021.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261019.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261020.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261020.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261019.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261020.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_claude_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261020.md
?? docs/신동거래/일일/신동_일일_MW0601_20261020.svg
?? docs/정기점검/매일점검/MW0601-20261019-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261020-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_pre.md
```

**당일(2026-10-20) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
87864966 [MW0601] 698차: 피터2 X 수집 공유 해소 — MW0602 수집기 중지(사용자 결정) · 단독 수집 효과 추적기
```

**최근 커밋 12건**
```
87864966 [MW0601] 698차: 피터2 X 수집 공유 해소 — MW0602 수집기 중지(사용자 결정) · 단독 수집 효과 추적기
97c7317e [MW0601] 697차 후속2: 장후 자동조치 — G-1 기록 (+ 10-19 장전·장중 dev_memory)
49083264 [MW0601] 697차 후속2: 장후 자동조치 — G-1 (점검 지침서 3원 대사에 거래주체 확인 명문화)
5aaad2d5 [MW0602] v9-dev 배포(체리픽): A-04 당일 손실 기준 자본 1,500만원 고정 — 두 PC 동일 (원 c68b442, dev)
a00a6880 [MW0602] v9-dev 배포(체리픽): 긴급 이상 알림 메일 S/A/B 14종 (원 ec00de0, dev)
01163773 [MW0601] 대시보드 3번 행 명칭 단순화 + [메일] On/Off 체크박스
ef8d795c [MW0602] v9-dev 배포(체리픽): 청산 거부 113분 재발 방지 ①~⑥ · 거래소 CB 차단을 모든 주체에 (원 d4776ed, dev)
5aa7c6c2 [MW0601] 문서 정리: 09-30–10-16 미커밋 산출물 일괄 커밋
af1e961c [MW0602] v9-dev 배포(체리픽): F-1009 동결 경보 메일([긴급이상]/[이상해소]) · G-1i closeEvent 진입/결과 로그 (원 f5ff9cb, dev)
f119a315 [MW0601] 697차 후속: 장후 자동조치 — F-26 (+ 10-16 장전·장중·장후 dev_memory · 누적대장 P5-18)
7a5275b5 [MW0601] 697차: 피터2 X 수집 한도 소진 — 한도 헤더 계측 · 80초 · reset 백오프
d81c079f [MW0601] 692차 후속4: 아침 coStarter 크래시 근절 — 장후 API 세션·맥점 사다리 정리(16:30) · 자동로그인 크래시 팝업 처리
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

_본문 미열람(설정): `20261020_HOGA.log` 62.1MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261020.txt`** — 28B · 10-20 15:40:22
```
2026-10-20T15:40:22.003081
```

**`data/daily_close_started_20261020.txt`** — 28B · 10-20 15:40:08
```
2026-10-20T15:40:08.674540
```

**`data/daily_reports/strategy_report_20261020_154021.txt`** — 2.4KB · 10-20 15:40:21
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-20 15:40
========================================================
  버전    : v1.0  (101일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-4.55  MDD(자본대비)=4.5%
  당일      : WR=미측정(거래0건)  PF=미측정
  롤링20일: 누적 -1942692원  Sh=-4.55  MDD(자본대비)=4.5%  MDD(peak대비)=721.8%
  당일손익 : broker(gross) +0원  수수료 0원  net +0원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.005 (CLEAR)
  PSI/feat: cvd_delta=0.005  ofi_pressure=0.000  vwap_position=0.071
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
  진입후보(conf≥mc): 금일 38분  5일평균 15분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 35.9pt(5일평균 44.9pt)  1분평균변동 0.91pt(5일평균 1.01pt)
--------------------------------------------------------
  진입 퍼널(2026-10-20, 총 370분):
    FLAT 191 → conf미달 120 → CoherenceGate 20 → 게이트차단 24 → 후보 15 → 진입 9
    └ 등급상향경로(앙상블X→체크리스트통과): 1건 [285차-P5]
    게이트별: 체크리스트항목미달=10  모드필터=4  포지션보유중(평가생략)=4  콜드스타트/기타(σ미수집)=3  시가갭(OPEN_VOLATILE)=3
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 6건
      └ 상세: JointGateBlock=6
      └ JointGateBlock 6건 (무정보폴백 3건 = 50.0%) [표본 14건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261020.txt`** — 233B · 10-20 15:53:37
```
completed: 2026-10-20 15:53:37
rows: 22101
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 26.9
t_retrain_s: 185.5
t_total_s: 212.9
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20261020.txt`** — 43B · 10-20 15:47:15
```
auto_shutdown
2026-10-20T15:47:15.025879
```

_다이제스트 대상 8/26개 (중요도순). 제외: `retrain_intraday_20260807_102059.log`, `retrain_intraday_20261020_105600.log`, `retrain_intraday_20260901_102000.log`, `retrain_intraday_20260820_110200.log`, `20261020_MICRO.log`, `20261020_DATA.log`, `20261020_PROBE.log`, `launcher_20261020_084001_17359.log`_

### `logs/20261020_TRADE.log` — 19.2KB · 121행 · 최종 15:40:10

- 형식 평문 · 시각 인식 121행 · WARNING=10, INFO=111

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-20 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-20 09:02:09 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 882.52 | 손절=887.72 1차=-9117.48(×1.00) 2차=-9117.48
2026-10-20 09:02:09 [WARNING] TRADE: [PositionFallback] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=882.52 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상)
2026-10-20 09:02:09 [INFO] TRADE: [Virtual] 신동 가상진입 SHORT 1계약 @882.52 손절 887.72 목표 868.50 (principal)
  …
2026-10-20 13:52:00 [INFO] TRADE: [Position] 청산 SHORT @ 855.6630175 | PnL=-1.70pt (-86,773원) 수수료=1,623원 | 가상:하드스톱
2026-10-20 13:52:00 [INFO] TRADE: [Virtual] 미륵 가상청산 SHORT 1계약 @855.66 가상:하드스톱 | -1.70pt -86,773원 (포지션 종료)
2026-10-20 13:53:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=18,935,259) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1)
2026-10-20 13:53:00 [INFO] TRADE: [진입체크] SHORT→SHORT 1계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas✅ coun✅ | conf=40.1%
2026-10-20 15:40:10 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 10 | 09:02:09 | 12:21:09 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=882.52 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×121

**컴포넌트 상위 15** — `Position`×35, `Virtual`×32, `Sizer`×23, `PositionFallback`×10, `진입체크`×9, `JointGateBlock 차단`×6, `모드필터 차단`×4, `ProfitGuard`×2

### `logs/20261020_WARN.log` — 685.6KB · 3084행 · 최종 15:46:13

- 형식 평문 · 시각 인식 3078행 · WARNING=3078, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-20 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-10-20 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-20 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-20 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=783343908
  …
════════════════════════════════════════════════════
2026-10-20 15:40:20 [WARNING] SYSTEM: [LiveDBG] _refresh_pnl_history fetch+update_pnl 240ms
2026-10-20 15:40:20 [WARNING] SYSTEM: [LiveDBG] _refresh_pnl_history 총 248ms
2026-10-20 15:46:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2229 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=4437 band=INFO since_pipe_s=2232.2
2026-10-20 15:46:13 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 123.2ms | size=1994x950 candles=411 grid=46.5 spans=0.2 candles=17.0 dir=1.5 regime=16.3 markers=33.4 axes=0.8 cross=0.0 | slow_cnt=2796 total_cnt=3075 overlay_cnt=43163
```

</details>

**WARNING — 태그 25종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2796 | 08:57:32 | 15:46:13 | paintEvent slow 48.3ms | size=1994x950 candles=13 grid=26.6 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.0 cross=0.0 | slow_cnt=1 total_cnt=82 overlay_cnt=555 |
| `OptionFlowChart` | 75 | 08:41:18 | 15:32:09 | 그리기 75.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 774x1001 |
| `LiveDBG` | 72 | 08:41:08 | 15:46:12 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `CybosMarginQty` | 23 | 09:47:00 | 13:53:00 | 조회 실패 ret=0 status=-1 msg=11298 시장가/신고대량/최우선/최유리지정가 주문은 단가를 입력하지 않습니다. (ordsvr15)(ord.fo.dpmyinqr.selanwordpsblqty) account=783343908 code=A056B |
| `SHAP` | 21 | 12:11:01 | 15:07:02 | 슬로우 감지 923ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림) |
| `ScalerRefresh` | 14 | 09:05:00 | 14:42:00 | 5분 누적 수익률 -0.653% (임계 ±0.630%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 13 | 09:00:01 | 15:00:00 | level=WARNING degraded=OFF | latency=1419ms | quality=1.00 | cache_age=52s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |
| `CB③-P4` | 12 | 12:46:00 | 14:53:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `PipePerf` | 10 | 09:00:01 | 14:08:02 | total=1419ms | S0=3ms S1=12ms S2=0ms S3=0ms S4=111ms S5=487ms S6=736ms S7=44ms S8=26ms |
| `CB⑤` | 10 | 09:00:01 | 14:08:02 | 파이프라인 1419ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |
| `EntryAttempt` | 9 | 11:11:00 | 13:53:00 | atr=1.9986 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='SHORT' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='A' | pending='NONE' |… |
| `HealthPolicy` | 3 | 09:01:00 | 14:09:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1419ms quality=1.00 cache=0s exc10m=1) | cause=S6(736ms) |

**채널** — `SYSTEM`×3065, `HEALTH`×13

**컴포넌트 상위 15** — `ChartDBG`×2796, `OptionFlowChart`×75, `LiveDBG`×72, `CybosMarginQty`×23, `SHAP`×21, `ScalerRefresh`×14, `Health`×13, `CB③-P4`×12, `PipePerf`×10, `CB⑤`×10, `EntryAttempt`×9, `-`×6, `HealthPolicy`×3, `CybosDailyPnl`×2, `출처축`×2

### `logs/20261020_SYSTEM.log` — 1.0MB · 7165행 · 최종 15:47:15

- 형식 평문 · 시각 인식 7144행 · INFO=7144, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=2344 | 행감지=30s all_threads=True
2026-10-20 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.47s | predictions=0.05s trades=0.23s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-20 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-20 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-20 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-20 15:46:09 [INFO] SYSTEM: [RawFill] 2026-10-20 raw_candles 창 안 보충 0봉(bar_recovered=2) · 차트 보정 1봉(bar_recovered=3) — 보충 — / 보정 08:45
2026-10-20 15:46:09 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-20) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-20 15:47:15 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-20 15:47:15 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-20 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×7144

**컴포넌트 상위 15** — `CybosRT-TICK`×1696, `CybosInvestorRaw`×1576, `PumpGuard`×768, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×408, `S6Detail`×370, `PipePerf`×370, `System`×100, `MicroRegime`×99, `OptionChain`×81, `OptionBook`×79, `RegimeFingerprint`×69, `Peter2Offset`×37

### `logs/20261020_SIGNAL.log` — 513.4KB · 4593행 · 최종 15:40:11

- 형식 평문 · 시각 인식 4593행 · WARNING=1428, INFO=3165

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-10-20 15:10:00 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-20 15:40:10 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-20 15:40:10 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 11분(3.0%) / DN 124분(33.5%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-20 15:40:11 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-20 age=27m extreme=390 refresh=33 grade_x=139 cb3=0
2026-10-20 15:40:11 [INFO] SIGNAL: [ModelHealth] date=2026-10-20 앙상블유효가동률=75.1% | 파이프라인 370분 | ConstOut 7회/12분 {"3m": {"events": 5, "minutes": 9}, "5m": {"events": 2, "minutes": 3}} | WeightCollapse 80분 | 장중재학습 1회 | CB③ ready 221분/370분 (60%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 882 | 09:00:02 | 15:04:01 | 1m 'macro_vix' scale=0.0680 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 156 | 09:01:00 | 15:03:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 144 | 09:12:00 | 15:09:00 | 신뢰도 미달 38.9% < 39.0% → 강제 X등급 |
| `ScalerMonitor` | 138 | 09:01:00 | 15:04:01 | ts=09:00 horizon=1m age=1m max_z=+4.33(quality_investor_reason_code) extreme=1 adj=0 |
| `WeightCollapse` | 80 | 09:07:00 | 15:07:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 18 | 08:45:08 | 08:45:08 | 1m CORE 'cvd_divergence' raw_std≈0(0.0223) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 9 | 10:51:00 | 15:03:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:06:00 | 09:06:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3441 < 필요 0.3900 (conf_floor=0.330, min_conf=0.390, span=0.0089, auc=0.577). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4593

**컴포넌트 상위 15** — `ScalerFloor`×924, `SIGNAL`×740, `MetaGate`×390, `Ensemble`×385, `FQAdj`×369, `ZeroDiag`×335, `Checklist`×204, `ATR-Horizon`×171, `Model`×168, `ScalerMonitor`×139, `MicroRegime`×99, `차단`×97, `InstabilityGate`×93, `WeightCollapse`×80, `ToxicityGate`×80

### `logs/20261020_LEARNING.log` — 282.5KB · 2807행 · 최종 15:40:10

- 형식 평문 · 시각 인식 2807행 · WARNING=137, INFO=2670

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-20 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00074 auc=0.407 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-20 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00117 auc=0.397 out_max=0.2005 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
2026-10-20 08:40:50 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00014 auc=0.500 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-10-20 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00029 auc=0.518 out_max=0.3706 (기준 auc<0.53 and span<0.020, 기저율=0.3704 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-10-20 15:40:10 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-20 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-20 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-20 15:40:10 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-20 15:40:10 [INFO] LEARNING: [Sigma] EOD sigma_20=0.12781% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 44 | 08:40:49 | 15:08:00 | 축퇴 감지 — span=0.00117 auc=0.397 out_max=0.2005 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 36 | 08:40:49 | 14:38:00 | 축퇴 감지 — span=0.00074 auc=0.407 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 24 | 08:40:50 | 13:59:00 | 축퇴 감지 — span=0.00029 auc=0.518 out_max=0.3706 (기준 auc<0.53 and span<0.020, 기저율=0.3704 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 16 | 08:40:50 | 13:15:00 | 축퇴 감지 — span=0.00014 auc=0.500 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 9 | 08:40:50 | 08:40:58 | 하한 도달불가 — out_max=0.3254 < conf_floor=0.3300 (span=0.00069 auc=0.635 out_max=0.3254, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 4 | 08:40:58 | 15:04:00 | 복원한 보정기가 하한 도달불가 — out_max=0.3284 < conf_floor=0.3300 (span=0.00736 auc=0.570 out_max=0.3284, n=4224) → 보정 미적용으로 시작, raw 통과. 축퇴(auc/span)와 별개 사유이며, 표본이 쌓여 출력상한이 하한 위로 올라오면 fit()에서 자동 재적용된다. |
| `Calibration:15m` | 3 | 08:40:50 | 08:40:55 | 축퇴 감지 — span=0.00158 auc=0.426 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Buffer-Timing` | 1 | 12:21:00 | 12:21:00 | total=355ms raw_fetch=4ms pred_select=4ms pred_update=31ms pred_insert=2ms verified=3 |

**채널** — `LEARNING`×2807

**컴포넌트 상위 15** — `LEARNING`×1219, `SGD`×370, `sigma`×357, `Bias⚠`×239, `Bias`×154, `Calibration:30m`×87, `MetaConf`×76, `Calibration:1m`×70, `Calibration:3m`×48, `ScalerWarmup`×39, `OnlineLearner`×38, `Calibration:5m`×31, `BiasReset`×19, `Calibration:10m`×18, `SHAP`×10

### `logs/20261020_HEALTH.log` — 3.8KB · 26행 · 최종 15:01:00

- 형식 평문 · 시각 인식 26행 · WARNING=13, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1419ms | quality=1.00 | cache_age=52s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1
2026-10-20 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=485ms | quality=1.00 | cache_age=111s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1
2026-10-20 09:29:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 319ms (표본 20분)
2026-10-20 09:42:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=325ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-10-20 09:43:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=247ms | quality=1.00 | cache_age=59s | exceptions_10m=0
  …
2026-10-20 14:06:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=300ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-20 14:08:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1963ms | quality=1.00 | cache_age=181s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-20 14:09:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=360ms | quality=1.00 | cache_age=55s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-20 15:00:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=347ms | quality=1.00 | cache_age=180s | exceptions_10m=2 | exc_tags=[CB③-P4]×1 [SHAP]×1
2026-10-20 15:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=313ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[SHAP]×2 [CB③-P4]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 13 | 09:00:01 | 15:00:00 | level=WARNING degraded=OFF | latency=1419ms | quality=1.00 | cache_age=52s | exceptions_10m=1 | exc_tags=[Peter2Offset]×1 |

**채널** — `HEALTH`×26

**컴포넌트 상위 15** — `Health`×25, `HealthTrend`×1

### `logs/retrain_eod_20261020.log` — 19.9KB · 132행 · 최종 15:53:37

- 형식 평문 · 시각 인식 132행 · WARNING=13, INFO=119

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 15:50:03,359 [INFO] EOD_RETRAIN: =======================================================
2026-10-20 15:50:03,359 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-20 15:50:03,359 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-20 15:50:03,359 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-20 15:50:03,360 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-20 15:53:37,593 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0362 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-20 15:53:37,593 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0939 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-20 15:53:37,596 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-10-20 15:53:37,601 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.03s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-20 15:53:37,603 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:40 | 15:52:37 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-10-19 14:38:00 ≥ 홀드아웃 시작=2026-10-13 11:03:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-19 14:38 >= holdout_start=2026-10-13 11:03 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-19 … |
| `GuardGhost` | 2 | 15:51:05 | 15:51:05 | 5m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-10-20 10:25:00까지)인데 acc.txt=0.3593는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-20 | 최신 2026-10-19 · 기준 7거래일. 복구: python scripts/collect_regular_futures.py --from 20261020 --to 20261020 |
| `OptionFlowFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-13(최신봉 15:33) | 기준 6거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\<YYYYMMDD>_OPTION_BACKFILL.log |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 17812/43976 제외 (418차 결정 1) — 남은 26164행 |
| `UnitMismatch` | 1 | 15:50:15 | 15:50:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/26164행 제외 (559차 P1'-2) — 남은 24718행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:37 | 15:53:37 | 백필 0행 제외 — 필터가 무효일 수 있다. 22101행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×64, `SIGNAL`×31, `EOD_RETRAIN`×27, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×24, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2, `GuardGhost`×2

### `logs/retrain_intraday_20260708_102056.log` — 4.6KB · 39행 · 최종 10:21:34

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-08 10:20:56,636 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-08 10:20:56,637 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-08 10:20:56,637 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-08 10:20:56,637 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ed01cbfc.json
2026-07-08 10:20:58,891 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-08 10:21:34,087 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=2.04s | old_acc=nan)
2026-07-08 10:21:34,091 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-08 10:21:34,092 [INFO] LEARNING: [Retrain] 완료 | 35.2초 | 성공=6/6 호라이즌
2026-07-08 10:21:34,093 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 37.5s 데이터=20000행
2026-07-08 10:21:34,095 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ed01cbfc.json
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
════════════════════════════════════════════════════
2026-10-20 15:40:20 [WARNING] SYSTEM: [LiveDBG] _refresh_pnl_history fetch+update_pnl 240ms
2026-10-20 15:40:20 [WARNING] SYSTEM: [LiveDBG] _refresh_pnl_history 총 248ms
2026-10-20 15:46:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2229 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=4437 band=INFO since_pipe_s=2232.2
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 9 |
| 진입 등록(`[Position] 진입`) | 16 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 0 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 16 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 97 |
| 사이저 호출(`[Sizer]`) | 23 |

### CB③ 판정 가능 시간 — **221분 / 370분 (60%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 16건

| 시각 | 출처 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|---|
| 09:02:09 | 가상 | SHORT | 1 | 882.52 | — | — |
| 09:35:09 | 가상 | SHORT | 1 | 870.1 | — | — |
| 09:44:09 | 가상 | SHORT | 1 | 865.54 | — | — |
| 10:43:09 | 가상 | SHORT | 1 | 867.3 | — | — |
| 10:50:09 | 가상 | LONG | 1 | 868.92 | — | — |
| 11:07:09 | 가상 | SHORT | 1 | 865.6 | — | — |
| 11:11:00 | 가상 | SHORT | 1 | 865.3 | 5m | trend |
| 11:20:09 | 가상 | SHORT | 1 | 872.1 | — | — |
| 11:39:09 | 가상 | LONG | 1 | 867.34 | — | — |
| 11:48:09 | 가상 | LONG | 1 | 871.28 | — | — |
| 12:21:09 | 가상 | SHORT | 1 | 865.16 | — | — |
| 12:32:01 | 가상 | SHORT | 1 | 863.34 | 3m | trend |
| 13:02:01 | 가상 | SHORT | 1 | 858.68 | 3m | mean-revert |
| 13:08:00 | 가상 | SHORT | 1 | 856.68 | 3m | mean-revert |
| 13:12:01 | 가상 | SHORT | 1 | 855.76 | 3m | mean-revert |
| 13:51:00 | 가상 | SHORT | 1 | 853.96 | 3m | mean-revert |

계약수 분포 — 1계약×16

등급 분포 — `A급(원시C)`×8, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×9, `chas`×5, `prev`×4, `cvd`×4, `ofi`×2, `time`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×23

실제 진입 계약수 — **1계약**×16

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×23

### 차단 사유 97건 · 31종

| 건수 | 사유 |
|---|---|
| 58 | 등급X — 미통과 항목: 2_confidence |
| 4 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 2 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.6pt > ATR×5.0=10.7pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.1pt > ATR×5.0=9.9pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 24.1pt > ATR×5.0=9.3pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.6pt > ATR×5.0=9.8pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.6pt > ATR×5.0=9.9pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.9pt > ATR×5.0=10.1pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.1pt > ATR×5.0=9.4pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.1pt > ATR×5.0=9.7pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.1pt > ATR×5.0=9.7pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 26.0pt > ATR×5.0=10.5pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.6pt > ATR×5.0=11.2pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 25.3pt > ATR×5.0=11.1pt (시가=883.84 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 26.7pt > ATR×5.0=11.0pt (시가=883.84 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×58, `3_vwap`×8, `6_foreign`×8, `4_cvd`×5, `7_prev_bar`×5, `5_ofi`×3, `11_countertrend`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 16건 · 최대 4437ms · 5초 초과 0건

상위 — 4437ms, 4344ms, 4313ms, 3891ms, 3844ms, 3625ms, 3141ms, 2860ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261020_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:20 2026-10-20 15:40:20 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 15분/일 < 하한 60분 — 금일 38분. | ConfFloorGuard 도달가능 0분 · 도달불가 50분 · 재지않음 320분
--- ConstOut ×1(표본)
10:55:00 2026-10-20 10:55:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(5m=0.4735)
--- [SHAP] 슬로우 ×8(표본)
12:11:01 2026-10-20 12:11:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 923ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:30:01 2026-10-20 12:30:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1193ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:50:01 2026-10-20 12:50:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1350ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:02:01 2026-10-20 13:02:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 922ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-20 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4313ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4313 band=INFO since_pipe_s=NA
09:00:03 2026-10-20 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3625ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3625 band=INFO since_pipe_s=0.1
09:05:01 2026-10-20 09:05:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2532ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2532 band=INFO since_pipe_s=0.1
10:57:03 2026-10-20 10:57:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4344ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=4344 band=INFO since_pipe_s=0.0
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20261020_SYSTEM.log`
```
--- ConstOut ×8(표본)
10:51:00 2026-10-20 10:51:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4494) | 앙상블 제외는 유지
10:55:00 2026-10-20 10:55:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 10:57:00 (const_output)
10:55:00 2026-10-20 10:55:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['5m']
10:55:01 2026-10-20 10:55:01 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['5m'] load=384ms fit=33ms total=438ms
--- HALT ×1(표본)
15:40:11 2026-10-20 15:40:11 [INFO] SYSTEM: [CB③계측] 조건성립 52분 / 판정가능 221분 / 파이프라인 370분 · 그 창 진입 6포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-20 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-10-20 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:10:00 2026-10-20 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:15:00 2026-10-20 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:10 2026-10-20 15:40:10 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:10 2026-10-20 15:40:10 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:08 2026-10-20 15:11:08 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:22 2026-10-20 15:40:22 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:15 2026-10-20 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:22 2026-10-20 15:40:22 [INFO] SYSTEM: [Notify] ℹ️ [15:40:22] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:22 2026-10-20 15:40:22 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 398초
15:40:22 2026-10-20 15:40:22 [INFO] SYSTEM: 자동 종료 예약 — 413초 후 Qt 이벤트 루프 종료
```

### `logs/20261020_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:06:00 2026-10-20 09:06:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3441 < 필요 0.3900 (conf_floor=0.330, min_conf=0.390, span=0.0089, auc=0.577). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
10:44:00 2026-10-20 10:44:00 [INFO] SIGNAL: [ConstOutShadow] 15m 불일치 live=- raw=STUCK | live(range=0.0520 dir=+0) raw(range=0.0000 dir=+0)
10:45:00 2026-10-20 10:45:00 [INFO] SIGNAL: [ConstOutShadow] 15m 불일치 live=- raw=STUCK | live(range=0.0520 dir=+0) raw(range=0.0000 dir=+0)
10:51:00 2026-10-20 10:51:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0430 dir=-1)
10:51:00 2026-10-20 10:51:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
--- WeightCollapse ×8(표본)
09:07:00 2026-10-20 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-10-20 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=74.4% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-10-20 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=67.1% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-20 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=67.6% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
--- 안전망 ×8(표본)
09:07:00 2026-10-20 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-20 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-20 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-20 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261020_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:49 2026-10-20 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00074 auc=0.407 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:49 2026-10-20 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00117 auc=0.397 out_max=0.2005 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-20 08:40:50 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00014 auc=0.500 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-20 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00029 auc=0.518 out_max=0.3706 (기준 auc<0.53 and span<0.020, 기저율=0.3704 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261020_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:58 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5 | 09:02:09 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=882.52 — 진입 경로가 파라미터를 넘기지 … |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:10 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261020_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:41:08 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 15 | 08:52:38 [WARNING] A056B 실측=-1.67 n=7 spread=0.05 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.67 | 직전일=-1.82(prev_day:2026-10-1… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 44 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 97 | 09:54:00 [WARNING] paintEvent slow 80.9ms | size=1994x922 candles=36 grid=28.9 spans=0.0 candles=2.0 dir=0.2 regime=5.3 markers=… |
| 12:00 | 장중 중간점 | 84 | 11:54:00 [WARNING] paintEvent slow 81.8ms | size=1994x922 candles=36 grid=22.3 spans=0.0 candles=2.3 dir=0.2 regime=6.3 markers=… |
| 14:00 | 장중 후반 · 장중 재학습 | 88 | 13:54:01 [WARNING] paintEvent slow 97.0ms | size=1994x950 candles=310 grid=33.0 spans=0.2 candles=12.3 dir=1.2 regime=14.1 marke… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 90 | 15:04:01 [WARNING] paintEvent slow 97.7ms | size=1994x950 candles=380 grid=35.0 spans=0.2 candles=14.3 dir=1.5 regime=13.4 marke… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 87 | 15:12:00 [WARNING] paintEvent slow 95.4ms | size=1994x950 candles=387 grid=20.4 spans=0.2 candles=18.0 dir=2.3 regime=10.9 marke… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 15 | 15:34:00 [WARNING] paintEvent slow 85.6ms | size=1994x950 candles=410 grid=21.5 spans=0.2 candles=15.8 dir=1.5 regime=6.9 marker… |
| 15:47 | EOD 재학습(py310_64) 완료 | 2 | 15:46:12 [WARNING] _tick_header 간격 4437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2229 watchdog_alerted=[90, 150, 240] | [MainStall] stal… |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261020_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 102 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=2344 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 146 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 223 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 243 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 204 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 209 | 13:54:00 [INFO] code=A056B from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 219 | 15:04:00 [INFO] code=A056B from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 191 | 15:12:00 [INFO] code=A056B from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 68 | 15:34:00 [INFO] #169000 code=A056B raw_time=153400 parsed=15:34:00 price=861.18 vol=1 bid1=861.08 ask1=861.18 flag=49 side=BU… |
| 15:47 | EOD 재학습(py310_64) 완료 | 12 | 15:41:08 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:08 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261020_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0223) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 90 | 09:00:02 [WARNING] 1m 'macro_vix' scale=0.0680 → floor=0.10 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 203 | 09:00:02 [WARNING] 1m 'macro_vix' scale=0.0680 → floor=0.10 적용 (z-score 폭발 방지) |
| 10:00 | 장중 초반 | 134 | 09:54:00 [WARNING] 신뢰도 미달 38.9% < 39.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 109 | 11:54:00 [WARNING] 신뢰도 미달 32.6% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 114 | 13:55:01 [WARNING] 1m 'macro_vix' scale=0.0409 → floor=0.10 적용 (z-score 폭발 방지) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 95 | 15:04:01 [WARNING] ts=15:03 horizon=1m age=22m max_z=+22.26(toxicity_queue_stress) extreme=4 adj=4 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:10 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261019 | 15:47 | 로그 본문 |
| 20261017 | 12:11 | 로그 본문 |
| 20261016 | 15:47 | 로그 본문 |
| 20261015 | 15:47 | 로그 본문 |
| 20261014 | 17:41 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261020** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-19 (MW0601 — 장전 점검)
## 2026-10-19 (MW0601 — 장중 점검)
## 2026-10-19 (MW0601 697차 후속2 — 장후 자동조치: G-1) — 🟢 **구현 · 문서/테스트 한정 · 매매 경로 무변경**
## 2026-10-19 (MW0601 — 장후 점검, 종합 완성본)
## 2026-10-19 (MW0601 — 장후 점검 세션, 교차확인 메모)
## 2026-10-20 (MW0601 698차 — 피터2 X 수집 공유 해소: MW0602 수집기 중지 · 단독 수집 추적기) — 🟡 **결정 · 추적 도구 구현 · 라이브 미검증**
## 2026-10-20 (MW0601 — 장전 점검)
## 2026-10-20 (MW0601 — 장중 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
). ⑤·⑥은 "확인 필요"(O-p1·O-p2)로 등록해 장중 점검이 판정하도록 넘김.

**Why**: 313차 원칙(표본 부족 시 확정 금지) — Peter2Offset 표본 13개, Canary 재상승 관측 1회로는 "해소" 또는 "악화" 어느 쪽도 확정할 수 없음. 함정①(판정≠결정) — MAX_CONTRACTS·joblib 불일치는 이미 F-24/491차가 결론낸 사안이라 재상정하지 않음.

**How to apply**: 장중 점검이 O-p1(09:30 전후 Peter2Offset 재측정)·O-p2(09:10~09:15 Canary 재측정)를 판정/판정보류/다음거래일이월 중 하나로 닫을 것. F-1(문서 동기화)은 장후에 `collect_evidence.py`의 MAX_CONTRACTS 기대값과 `phases.md` 32행 joblib 표기를 수정.

**검증**: 다음 장전 점검에서 수집기 §3 표가 MAX_CONTRACTS 행도 `일치`로 나오는지 확인. Peter2Offset·Canary는 장중·장후 점검이 직접 판정.

⚠ 코드 변경 없음(장전 점검 — 관측·로그 읽기 전용). git add/commit/push 전혀 하지 않음(장전 세션 규칙).


## 2026-10-20 (MW0601 — 장중 점검)

**증상**: ① O-p1(피터2 오프셋) 09:00~12:02 구간 n=30 반복 측정 15회, spread 전부 0.12~0.24로 안정 기준(0.30 이하) 충족, safe=True 지속 — 전일(10-19) 하루 종일 불안정(0.31~0.40)과 대조. ② O-p2(캐너리 z경고 재상승) 09:00~12:26 구간 Canary 재측정 로그 0건이지만 `main.py:17659`(`[493차 후속5 / F-Q②] 08:59 Canary 확인 사격 — 섀도 관측`) 확인 결과 08:59 CanaryShadow가 설계상 **1회성 확인사격**임을 코드로 확인. ③ O-p3(옵션체인 재수집 09:01:28) 전일(09:01:26)·633차 선례와 일치. ④ `[PositionFallback]`(entry_horizon 미설정 → TP1 배수 폴백 1.00) 10건 — 전부 '신동' 보조전략 채널 진입(10건 전수), 메인 엔진('미륵') 채널의 유일한 진입(11:11:00, horizon=5m hurst=trend)에는 미발생. ⑤ 매분 루프 09:00~12:26 207/207분(100%) 생존, 10분 이상 공백 0건. ⑥ CB 미발동 — CB⑤ 경고 2건(09:00:01 1419ms·10:57:03 3498ms) 모두 정지 기준(5000ms) 미달, CB③ 리셋 스킵(표본 20건<30건, 정상). ⑦ 체결(실제 계좌 주문) 0건 — 모의투자 단계 지속. 가상 채널: '신동' 9건 청산 순손익 +408,242원(수수료 차감후, 1건 미청산), '미륵' 1건 청산 -183,162원(수수료 포함).

**원인**: O-p1은 698차(피터2 X 단독 수집 전환, MW0602 수집기 중지) 결정 이후 안정화 추세가 장중까지 이어진 것으로 보이나 확정 인과관계는 아니며 최종 판정은 698-2(5거래일 후, 10-26 장후 예정) 몫. O-p2는 추가 조사 없이 코드 확인만으로 해소(측정 자체가 1회성 설계). ④ PositionFallback은 '신동' 채널이 메인 앙상블의 entry_horizon 산출 경로(STEP5 멀티호라이즌)를 거치지 않는 별도 전략 구조라는 기존 원인 그대로 — 신규 원인 없음.

**결정**: O-p1·O-p2·O-p3 전부 ✅ 해소로 종결(NEXT_TODO 체크 완료). PositionFallback은 오늘 리포트에 이상점 1-3(P1)으로 등록했으나 기존 F-5에 합류시키고 신규 Fix ID는 발급하지 않음(함정① 방지 — 2026-08-25 48236행 선례와 동일 처리). 장중 신규 Fix·고도화 제안 없음(장전 F-1 계획만 유지, 적용은 장후).

**Why**: 함정①(판정≠결정, 이미 반영된 권고 재상정 금지) — F-5는 dev_memory에 2026-08부터 반복 기록된 결정이라 재상정하지 않음. 313차 원칙(표본 부족 시 확정 금지) — O-p1은 3시간 동안 n=30 포화 표본으로 15회 반복 측정해 장중 시점 판정 근거로 충분하다고 보되, "하루 전체 추이"의 최종 확정은 장후로 넘김(오후 변동 가능성 배제 안 함).

**How to apply**: 장후 점검이 (1) Peter2Offset 오후~15:10 종가까지 추이 재확인, (2) '신동'·'미륵' 채널 당일 최종 가상손익 재계산(포지션 단위), (3) 15:10 강제청산·EOD·P8 확인, (4) F-1(MAX_CONTRACTS·joblib 문서동기화) 실제 적용.

**검증**: 다음 장전 점검에서 O-p1(Peter2Offset) 안정 지속 여부를 재확인(1거래일만으로 "완전 해소"를 영구 확정하지는 않음 — 추세 지속 관찰).

⚠ 코드 변경 없음(장중 점검 — 관측·로그 읽기 전용). git add/commit/push 전혀 하지 않음(장중 세션 규칙).

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-16 (MW0601 697차 후속 — 장후 자동조치)
### 2026-10-19 (MW0601 — 장전 점검)
## 2026-10-19 (MW0601 — 장중 점검)
### 2026-10-19 (MW0601 697차 후속2 — 장후 자동조치)
### 2026-10-20 (MW0601 698차 — 피터2 단독 수집 전환)
### 2026-10-20 (MW0601 — 장전 점검)
### 2026-10-20 (MW0601 — 장중 점검)
```

미완료 체크박스 **3250건** (끝에서 30건)
```
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
- [ ] **F-1 (C, 사용자 결정)** 피터2 X 전용 계정 분리(697-3 분기 충족 — 1-4 p90 237.2초 FAIL · 창별 rem 소진 > 우리 관측). 결정 후 별도 세션 구현.
- [ ] **R-1 (C, 승인 대기)** `latency_report.py` 일별 p90·429·PAGE_ERROR 를 누적하는 관찰 스크립트 — 10거래일 후 p90 vs 피터2 순손익 일자단위 상관(313차 5갈래). 표본 1일이라 자동 구현 제외, 도구 자체는 무위험.
- [ ] **G-2(10-16) 보류 유지** 재시도·캐시 보강은 공유 소비 판정 하에서 한도 소진을 키운다 — F-1 결정 이후 재평가.
- [ ] **1-3 (C)** `PETER2_OFFSET_TOL_PT`/`_peter2_measure_offset()` 창 재검토 — 복수 거래일 spread>0.30 지속 시 안건.
- [ ] **698-1 (10-20 장중·장후)** RATE 우리 요청 사이 rem 감소가 1로 떨어졌는가(① 외부 소진 중앙 ≤ 3). 아니면 MW0602 중지 미반영 → 사용자 확인.
- [ ] **698-2 (매 장후, 5거래일)** `collect_evidence --phase post` §9-e 확인 · 최종 판정은 평가 창 5거래일 도달 시(빠르면 10-26 장후). IMPROVED → F-4·G-2 종결 / NOT_LIMIT → 03 §2 혼자 소진 가지 / STILL_SHARED → 사용자 확인.
- [ ] **R-1 연계** 지연 누적은 698 추적기가 대신한다 — 5거래일 후 R-1(지연 vs 피터2 손익) 필요성 재평가.
- [ ] **F-1 (P2, 저부담 문서동기화)** `collect_evidence.py`의 `MAX_CONTRACTS` 기대값 3→1 정정 · `.claude/skills/mireuk-daily-check/references/phases.md` 32행 `joblib 1.1.1`→`1.1.0` 정정. 매매 로직 무관, 사용자 승인 불필요, 적용은 장후.
- [ ] **(이월, 변경 없음)** 606-4 기동 access violation(1-1, `main_dashboard.py:7434 _build`) — 10-20으로 관측일 추가(최소 2거래일 연속), 여전히 사용자 결정 대기.
- [ ] **(이월, 변경 없음)** CREON-M1(P0) 장후 API 세션 정리 적용 시간대 — 여전히 사용자 결정 대기.
- [ ] **(참고)** 698-1/698-2(피터2 단독수집 전환, 698차) 오늘 아침 1차 관측: 15분 창 2개 중 외부소진 1회·0회(10-19 중앙값 27회 대비 큰 개선) — 최종 판정은 5거래일 후(10-26 장후 예정)까지 유지, 이 점검은 재해석하지 않음.
- [ ] (참고) **1-3 / F-5 재확인** `[PositionFallback]` 10건(전부 '신동' 채널) — 기존 F-5 대상, 신규 Fix 없음. 메인 엔진('미륵') 채널은 horizon 정상 전달로 미발생(구조적 원인 재확인).
- [ ] **698-1 장중 중간 관측(보강)** 08:30~12:45 15분 창 17개 중 16개 외부소진 0회(1개 창만 1회) — 전일 중앙값 27회 대비 뚜렷한 개선 지속. 최종 판정은 10-26 장후까지 유지.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
동조치)
- [x] **G-1** 점검 지침서 3원 대사에 거래주체 확인 명문화 → `4908326`.
- [ ] **F-1 (C, 사용자 결정)** 피터2 X 전용 계정 분리(697-3 분기 충족 — 1-4 p90 237.2초 FAIL · 창별 rem 소진 > 우리 관측). 결정 후 별도 세션 구현.
- [ ] **R-1 (C, 승인 대기)** `latency_report.py` 일별 p90·429·PAGE_ERROR 를 누적하는 관찰 스크립트 — 10거래일 후 p90 vs 피터2 순손익 일자단위 상관(313차 5갈래). 표본 1일이라 자동 구현 제외, 도구 자체는 무위험.
- [ ] **G-2(10-16) 보류 유지** 재시도·캐시 보강은 공유 소비 판정 하에서 한도 소진을 키운다 — F-1 결정 이후 재평가.
- [ ] **1-3 (C)** `PETER2_OFFSET_TOL_PT`/`_peter2_measure_offset()` 창 재검토 — 복수 거래일 spread>0.30 지속 시 안건.


### 2026-10-20 (MW0601 698차 — 피터2 단독 수집 전환)
- [x] **F-1 / 697-3 결정** 사용자: 새 계정 없이 MW0602 피터2 수집기 10-20부터 중지(②안). 추적기 `tools/peter2_live/sole_collect_tracker.py` · 문서 `docs/피터2수집/04_…`.
- [ ] **698-1 (10-20 장중·장후)** RATE 우리 요청 사이 rem 감소가 1로 떨어졌는가(① 외부 소진 중앙 ≤ 3). 아니면 MW0602 중지 미반영 → 사용자 확인.
- [ ] **698-2 (매 장후, 5거래일)** `collect_evidence --phase post` §9-e 확인 · 최종 판정은 평가 창 5거래일 도달 시(빠르면 10-26 장후). IMPROVED → F-4·G-2 종결 / NOT_LIMIT → 03 §2 혼자 소진 가지 / STILL_SHARED → 사용자 확인.
- [ ] **R-1 연계** 지연 누적은 698 추적기가 대신한다 — 5거래일 후 R-1(지연 vs 피터2 손익) 필요성 재평가.

### 2026-10-20 (MW0601 — 장전 점검)
- [ ] **F-1 (P2, 저부담 문서동기화)** `collect_evidence.py`의 `MAX_CONTRACTS` 기대값 3→1 정정 · `.claude/skills/mireuk-daily-check/references/phases.md` 32행 `joblib 1.1.1`→`1.1.0` 정정. 매매 로직 무관, 사용자 승인 불필요, 적용은 장후.
- [x] **O-p1 (장중 판정 완료)** Peter2Offset(피터2 오프셋) 08:58:08 spread=0.13 n=13 safe=True — 10-19 하루 종일 불안정(0.31~0.40)과 대조적 개선 신호. → **장중 09:00~12:02 구간 n=30 반복 측정 15회 전부 spread 0.12~0.24 safe=True로 확인, ✅ 해소 판정(10-20 장중 점검)**.
- [x] **O-p2 (장중 판정 완료)** Canary(캐너리) z경고 08:55 재적합 후 4~5개 → 08:59:09 재적합 없이 12개 재상승 — 10-19와 동일 패턴 반복. → **`main.py:17659` 확인 결과 08:59 CanaryShadow는 설계상 1회성 확인사격이며 09:00 이후 재측정 없음이 정상, ✅ 해소(설계 확인, 10-20 장중 점검)**.
- [x] **O-p3 (장중 판정 완료)** 옵션체인 재수집 완료 09:01:28 — 10-19(09:01:26)와 거의 동일 타이밍, 633차 선례와도 일치 → **✅ 해소 확정(10-20 장중 점검)**.
- [ ] **(이월, 변경 없음)** 606-4 기동 access violation(1-1, `main_dashboard.py:7434 _build`) — 10-20으로 관측일 추가(최소 2거래일 연속), 여전히 사용자 결정 대기.
- [ ] **(이월, 변경 없음)** CREON-M1(P0) 장후 API 세션 정리 적용 시간대 — 여전히 사용자 결정 대기.
- [ ] **(참고)** 698-1/698-2(피터2 단독수집 전환, 698차) 오늘 아침 1차 관측: 15분 창 2개 중 외부소진 1회·0회(10-19 중앙값 27회 대비 큰 개선) — 최종 판정은 5거래일 후(10-26 장후 예정)까지 유지, 이 점검은 재해석하지 않음.


### 2026-10-20 (MW0601 — 장중 점검)
- [ ] (참고) **1-3 / F-5 재확인** `[PositionFallback]` 10건(전부 '신동' 채널) — 기존 F-5 대상, 신규 Fix 없음. 메인 엔진('미륵') 채널은 horizon 정상 전달로 미발생(구조적 원인 재확인).
- [ ] **698-1 장중 중간 관측(보강)** 08:30~12:45 15분 창 17개 중 16개 외부소진 0회(1개 창만 1회) — 전일 중앙값 27회 대비 뚜렷한 개선 지속. 최종 판정은 10-26 장후까지 유지.

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

### `data/dailycheck_markers/MW0601-20261020-intra-cowork_intra_20261020.json` — 173B · 10-20 12:26:54
```json
{
 "pc": "MW0601",
 "date": "20261020",
 "phase": "intra",
 "session": "cowork_intra_20261020",
 "pid": 6,
 "started_epoch": 1792466814.579796,
 "started_at": "2026-10-20 03:26:54"
}
```

### `data/dailycheck_markers/MW0601-20261020-pre-cowork-0858.json` — 162B · 10-20 08:59:23
```json
{
 "pc": "MW0601",
 "date": "20261020",
 "phase": "pre",
 "session": "cowork-0858",
 "pid": 7,
 "started_epoch": 1792454363.8060517,
 "started_at": "2026-10-19 23:59:23"
}
```

### `data/dailycheck_markers/claude-20261020-post-cowork-postcheck-20261020.json` — 176B · 10-20 16:20:11
```json
{
 "pc": "claude",
 "date": "20261020",
 "phase": "post",
 "session": "cowork-postcheck-20261020",
 "pid": 9,
 "started_epoch": 1792480811.505467,
 "started_at": "2026-10-20 07:20:11"
}
```

### `data/heartbeat_MW0601_20261020.json` — 243B · 10-20 15:46:52
```json
{
 "pid": 2344,
 "written_at": "2026-10-20T15:46:52",
 "beat_epoch": 1792478808.666219,
 "beat_age_sec": 4.2,
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

### `data/peter_feed/_raw/2026-10-20.eod_ids.json` — 437B · 10-20 16:10:11
```json
[
 "2112332062451695986",
 "2112332393906606550",
 "2112397081029882068",
 "2112398037817708623",
 "2112402284902813721",
 "2112409322999398468",
 "2112409372890677615",
 "2112409417455165445",
 "2112409481565085860",
 "2112409534262374735",
 "2112413263556489270",
 "2112414801154691246",
 "2112417243657293859",
 "2112417376822256061",
 "2112417552114868431",
 "2112417631605256410",
 "2112417750161514660",
 "2112420668495335782",
 "2112429177618198792"
]
```

### `data/peter_feed/_raw/2026-10-20.jsonl` — 6.7KB · 10-20 15:23:00
```json
JSONL 26행 ⏎ 첫: {"id": "2112331823854571858", "dt": "2026-10-19T23:55:26.000Z", "text": "책 추천해 달라는 요청이 너무 많은데\n\n퀀트책 외에는 추천한 적이 없어.\n\n좋은 책은 많은데 뭔가 집대성한 느낌의 책이 없어서 딱 생각하는게 없었기 때문이야.\n\n그래서 내가 그동안 공부한것도 정리할겸해서 책을 썼거든.\n\n우선 '차트' 의 모든것을 집대성했어.( 보조지표등 각종 지표 심화편은", "seen_at": "2026-10-20T08:56:20+09:00", "src": "live"} | {"id": "2112332062451695986", "dt": "2026-10-19T23:56:23.000Z", "text": "책 추천해 달라는 요청이 너무 많은데\n\n퀀트책 외에는 추천한 적이 없어.\n\n좋은 책은 많은데 뭔가 집대성한 느낌의 책이 없어서 딱 생각나는게 없었기 때문이야.\n\n그래서 내가 그동안 공부한것도 정리할겸해서 책을 썼거든.\n\n우선 '차트' 의 모든것을 집대성했어.( 보조지표등 각종 지표 심화편은", "seen_at": "2026-10-20T08:57:39+09:00", "src": "live"} | {"id": "2112332393906606550", "dt": "2026-10-19T23:57:42.000Z", "text": "코스피는 오늘 상방 어려우니 매수하지는 말고.\n\n우선 지켜보자.", "seen_at": "2026-10-20T08:58:11+09:00", "src": "live"} ⏎ 끝: {"id": "2112417631605256410", "dt": "2026-10-20T05:36:24.000Z", "text": "", "seen_at": "2026-10-20T14:37:40+09:00", "kind": "empty", "src": "live"} | {"id": "2112420668495335782", "dt": "2026-10-20T05:48:28.000Z", "text": "보통 6시 전후로 올라가요", "seen_at": "2026-10-20T14:49:40+09:00", "src": "live"} | {"id": "2112429177618198792", "dt": "2026-10-20T06:22:17.000Z", "text": "봐요", "seen_at": "2026-10-20T15:23:00+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-20 15:53:37**

| 키 | 값 | 수집 대상일(2026-10-20)과 일치 |
|---|---|---|
| `date` | 2026-10-20 | 예 |
| `p8_last_success_date` | 2026-10-20 | 예 |
| `eod_retrain_ok_date` | 2026-10-20 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-20 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-19) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-20 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-19) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261020_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 2344: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:44 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 2344 | 08:40:44 | 15:47:15 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

### 9-e. 피터2 단독 수집 추적 (698차 — MW0602 수집기 중지 효과)

- 최종: **IN_PROGRESS** — 진행 중 — 평가 창 5거래일 미도달(중간값은 참고만) (평가 1/5거래일)
- 오늘: 트윗 n=26 · p90=76.5초 · 외부소진 중앙 0.0(기준선 27.0) · 429(정규장) 0건 · ① PASS · ② PASS
- 전체 표: `python tools/peter2_live/sole_collect_tracker.py --upto 2026-10-20`

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 235개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261020-점검리포트.md` | 29.1KB | 10-20 12:36 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_intra.md` | 75.7KB | 10-20 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_pre.md` | 61.7KB | 10-20 08:59 |
| `docs/정기점검/매일점검/MW0601-20261019-점검리포트.md` | 68.1KB | 10-19 17:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_post.md` | 94.7KB | 10-19 16:21 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md` | 81.1KB | 10-19 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md` | 59.6KB | 10-19 08:59 |
| `docs/정기점검/매일점검/MW0602-20261017-긴급알림메일-종합검토.md` | 14.1KB | 10-17 11:49 |

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
3. **엔진 진입 0건 / 계좌 진입 0건**(그중 외부표식 0건 · 피터2 0건 · 판별불가 0건 · 별도 가상 장부 16건) — 차단 97건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
4. `logs/20261020_WARN.log`: **ConstOut** 1건(표본)
5. `logs/20261020_SYSTEM.log`: **ConstOut** 8건(표본)
6. `logs/20261020_SIGNAL.log`: **WeightCollapse** 8건(표본)
7. `logs/20261020_SIGNAL.log`: **ConstOut** 8건(표본)
8. `logs/20261020_LEARNING.log`: **축퇴** 8건(표본)
9. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
10. 미커밋 변경 26건 (실질 6건 · 코드 0건 · EOL 파생 0건)
11. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261020*.log` (Windows) / `grep 강제청산 logs/*20261020*.log`*