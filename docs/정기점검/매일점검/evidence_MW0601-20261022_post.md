# 미륵이 증거 다이제스트 — 2026-10-22 / POST

- 생성 2026-10-22 16:18:30 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01fblks1fa9gmj3kbixftew1/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261022` · `2026-10-22` · `261022` · `1022`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **43개** 파일 · 43개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-intra-cowork-intra-0330.json` | 1 | `data/dailycheck_markers/claude-20261022-intra-cowork-intra-0330.json` | 170B | 10-22 12:30 |
| `claude-{DATE}-post-cowork-postmarket-1792653493.json` | 1 | `data/dailycheck_markers/claude-20261022-post-cowork-postmarket-1792653493.json` | 180B | 10-22 16:18 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261022.txt` | 28B | 10-22 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261022.txt` | 28B | 10-22 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261022.txt` | 233B | 10-22 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261022.log` | 1.4KB | 10-22 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261022.log` | 275B | 10-22 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261022.json` | 245B | 10-22 15:46 |
| `launcher_{DATE}_084001_24599.log` | 1 | `logs/Mireuk_batch/launcher_20261022_084001_24599.log` | 2.6MB | 10-22 15:47 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261022.log` | 109B | 10-22 08:44 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261022.log` | 2.3KB | 10-22 15:46 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261022.log` | 46.3KB | 10-22 16:16 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261022.log` | 491B | 10-22 16:15 |
| `position_state.json.gen_{DATE}_132205` | 1 | `data/position_state.json.gen_20261022_132205` | 1.6KB | 10-22 13:22 |
| `position_state.json.gen_{DATE}_150501` | 1 | `data/position_state.json.gen_20261022_150501` | 1.5KB | 10-22 13:22 |
| `position_state.json.gen_{DATE}_150502` | 1 | `data/position_state.json.gen_20261022_150502` | 1.6KB | 10-22 15:05 |
| `probe_9842_{DATE}_142216.json` | 1 | `logs/probe_9842_20261022_142216.json` | 572.3KB | 10-22 14:22 |
| `probe_9842_{DATE}_142216.md` | 1 | `logs/probe_9842_20261022_142216.md` | 4.2KB | 10-22 14:22 |
| `probe_9842_{DATE}_142817.json` | 1 | `logs/probe_9842_20261022_142817.json` | 619.5KB | 10-22 14:28 |
| `probe_9842_{DATE}_142817.md` | 1 | `logs/probe_9842_20261022_142817.md` | 4.0KB | 10-22 14:28 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261022.log` | 21.9KB | 10-22 15:53 |
| `retrain_intraday_20260624_{DATE}56.log` | 1 | `logs/retrain_intraday_20260624_102256.log` | 4.6KB | 06-24 10:23 |
| `retrain_intraday_20261015_{DATE}00.log` | 1 | `logs/retrain_intraday_20261015_102200.log` | 3.2KB | 10-15 10:22 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261022.log` | 114.8KB | 10-22 16:04 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261022.txt` | 43B | 10-22 15:47 |
| `strategy_report_{DATE}_154017.txt` | 1 | `data/daily_reports/strategy_report_20261022_154017.txt` | 2.4KB | 10-22 15:40 |
| `{DATE}.eod_ids.json` | 1 | `data/peter_feed/_raw/2026-10-22.eod_ids.json` | 391B | 10-22 16:16 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-22.jsonl` | 5.5KB | 10-22 16:16 |
| `{DATE}_D.xls` | 1 | `data/db/option_hts/261022_D.xls` | 483.2KB | 10-22 15:44 |
| `{DATE}_DATA.log` | 1 | `logs/20261022_DATA.log` | 437.7KB | 10-22 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261022_DEBUG.log` | 283.2KB | 10-22 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261022_HEALTH.log` | 2.9KB | 10-22 15:04 |
| `{DATE}_HOGA.log` | 1 | `logs/20261022_HOGA.log` | 57.5MB | 10-22 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261022_LEARNING.log` | 283.3KB | 10-22 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261022_MICRO.log` | 1.1MB | 10-22 15:38 |
| `{DATE}_P.xls` | 1 | `data/db/option_hts/261022_P.xls` | 484.1KB | 10-22 15:44 |
| `{DATE}_PROBE.log` | 1 | `logs/20261022_PROBE.log` | 105.4KB | 10-22 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261022_REGULAR_COLLECT.log` | 9.0KB | 10-22 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261022_SIGNAL.log` | 556.7KB | 10-22 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261022_SYSTEM.log` | 1.1MB | 10-22 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261022_TRADE.log` | 35.7KB | 10-22 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261022_WARN.log` | 813.5KB | 10-22 15:46 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-22_tr.draft.txt` | 0B | 10-22 15:40 |

## 2. 코드·커밋 상태

- HEAD `51bdd5da` · 브랜치 `v9-dev` · 미커밋 46건 · 실질 변경 6건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 6 · 미추적 40 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 5.2초(`git status --porcelain`)
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
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261022.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261023.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261019.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261020.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261021.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261022.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261020.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261021.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261022.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261019.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261020.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261021.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261022.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_claude_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261020.md
?? docs/신동거래/일일/신동_일일_MW0601_20261020.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261021.md
?? docs/신동거래/일일/신동_일일_MW0601_20261021.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261022.md
?? docs/신동거래/일일/신동_일일_MW0601_20261022.svg
?? docs/정기점검/매일점검/MW0601-20261019-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261020-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261021-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261022-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_post.md
… 외 6건
```

**당일(2026-10-22) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
51bdd5da [MW0601] 704차 후속2: 수집기 첫 실행 결함 3건 — 콜풋 '콜'/'풋' 표기 · COM 재사용 시 풋 0행 · 빈 응답을 성공으로 처리
5bed3446 [MW0601] 704차 후속: [9842] 행사가 × 투자자 12주체 수집기 (CpSvr9842) — ENABLED=False 배포
53601c55 [MW0601] 704차: [9842] CpSvr9842 실계좌 로그인에서 사용 가능 확정 · 점검 프로브 신설
87ee17cc [MW0601] 703차: F-701-A ProfitGuard 계좌 축(주체 3종 실현 net 합) · 신동·피터2 관문 배선 · L4 축 통일 · L3 카운터 부활
d76d1307 [MW0601] 702차 후속: F-10 dev 이식 메모 — tp1_reached 오염 경로·측정 쿼리·이식 범위 (MW0602 판단용)
7a4f6387 [MW0601] 702차: F-10 — exit_stage 라벨 축 분리(tp1_protect_armed), 하드스톱 분할체결 TRAIL_AFTER_TP1 오분류 해소
```

**최근 커밋 12건**
```
51bdd5da [MW0601] 704차 후속2: 수집기 첫 실행 결함 3건 — 콜풋 '콜'/'풋' 표기 · COM 재사용 시 풋 0행 · 빈 응답을 성공으로 처리
5bed3446 [MW0601] 704차 후속: [9842] 행사가 × 투자자 12주체 수집기 (CpSvr9842) — ENABLED=False 배포
53601c55 [MW0601] 704차: [9842] CpSvr9842 실계좌 로그인에서 사용 가능 확정 · 점검 프로브 신설
87ee17cc [MW0601] 703차: F-701-A ProfitGuard 계좌 축(주체 3종 실현 net 합) · 신동·피터2 관문 배선 · L4 축 통일 · L3 카운터 부활
d76d1307 [MW0601] 702차 후속: F-10 dev 이식 메모 — tp1_reached 오염 경로·측정 쿼리·이식 범위 (MW0602 판단용)
7a4f6387 [MW0601] 702차: F-10 — exit_stage 라벨 축 분리(tp1_protect_armed), 하드스톱 분할체결 TRAIL_AFTER_TP1 오분류 해소
ec6e9e83 [MW0602] research_snapshot --status cp949 콘솔 크래시 수정 (en-dash → ~)
96823eba [MW0601] 701차: DECISION_LOG — 연구용 장후 사본 신설 · regime_history 보존 무변경 · 가격패턴 연구 양방향 공유
555ab45b [MW0601] 701차: CLAUDE.md 멀티PC 절 — docs/가격움직임패턴연구/ 양방향 공유 예외 (사용자 지시)
1808af74 [MW0601] 701차 [가격패턴]: 선물시장 국면 분류 연구 — 조사 보고서·근거 노트·표본 실측·양방향 공유 규약
48f1f658 [MW0601] 701차: 연구용 장후 사본 research_snapshot — ensemble_decisions 삭제 없는 증분 아카이브
50dcb0f1 [MW0601] 신동 실거래 수량 SHINDONG_LIVE_QTY 1 → 2 (사용자 결정 2026-10-21)
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `1` | `1` | 일치 | 431차 10→3 인하 → [2026-10-13 사용자 결정 56cc917] CREON 실거래 전환으로 3→1 (1계약 명목가치만 실운영금 1,500만원의 약 … |
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

### 차단 게이트 전수 인벤토리 — 47개 중 **11개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FREEZE_SENTINEL_KILL_ENABLED` | False | 기능토글 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL` | False | **미기록 ⚠** |
| `STRIKE_INVESTOR_FLOW_ENABLED` | False | 기능토글 |
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

> ⚠ **꺼져 있는데 근거가 기록되지 않은 차단 게이트 1개**: `PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL`
> 의도한 것이면 `dev_memory/DECISION_LOG.md` 에 사유·복원조건을 적고 `config/dailycheck_targets.json` 의 `documented_disabled_flags` 에 추가하라. 의도한 것이 아니면 그 자체가 P0다.

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20261022_HOGA.log` 57.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261022.txt`** — 28B · 10-22 15:40:17
```
2026-10-22T15:40:17.466391
```

**`data/daily_close_started_20261022.txt`** — 28B · 10-22 15:40:04
```
2026-10-22T15:40:04.548916
```

**`data/daily_reports/strategy_report_20261022_154017.txt`** — 2.4KB · 10-22 15:40:17
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-22 15:40
========================================================
  버전    : v1.0  (103일차)
  판정    : OUTPERFORM
  Live(20일): Sh=1.68  MDD(자본대비)=4.5%
  당일      : WR=66.7%  PF=2.29
  롤링20일: 누적 +1411486원  Sh=1.68  MDD(자본대비)=4.5%  MDD(peak대비)=159.8%
  당일손익 : broker(gross) +1,127,174원  수수료 29,860원  net +1,127,140원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.004 (CLEAR)
  PSI/feat: cvd_delta=0.004  ofi_pressure=0.000  vwap_position=0.075
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 +85,648원  승률 65.0%  합계 +1,712,965원
  등급별 순EV(30일): A=-6,062원(58건,승57%)  P=-79,556원(20건,승20%)  S=+145,834원(23건,승70%)
  호라이즌별 순EV(30일): 1m=+2,297원(7건)  3m=+15,483원(33건)  5m=-48,810원(18건)  ?=+41,001원(43건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 28분  5일평균 33분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 42.5pt(5일평균 40.4pt)  1분평균변동 0.80pt(5일평균 0.94pt)
--------------------------------------------------------
  진입 퍼널(2026-10-22, 총 370분):
    FLAT 181 → conf미달 140 → CoherenceGate 22 → 게이트차단 19 → 후보 8 → 진입 7
    게이트별: 콜드스타트/기타(σ미수집)=5  체크리스트항목미달=5  쿨다운=3  콜드스타트/기타(DataAnomalyGate)=2  포지션보유중(평가생략)=1  콜드스타트/기타(RegimeOverride)=1  모드필터=1  마감시간(신규진입금지)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 1건
      └ 상세: JointGateBlock=1
      └ JointGateBlock 1건 (무정보폴백 0건 = 0.0%) [표본 19건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261022.txt`** — 233B · 10-22 15:53:38
```
completed: 2026-10-22 15:53:38
rows: 22802
cols: 97
phase2_fallback: false
horizons_replaced: 5/6
t_load_s: 27.6
t_retrain_s: 186.1
t_total_s: 214.2
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20261022.txt`** — 43B · 10-22 15:47:14
```
auto_shutdown
2026-10-22T15:47:14.532625
```

_다이제스트 대상 8/22개 (중요도순). 제외: `retrain_intraday_20261015_102200.log`, `20261022_MICRO.log`, `20261022_DATA.log`, `20261022_PROBE.log`, `launcher_20261022_084001_24599.log`, `20261022_DEBUG.log`, `shindong2_20261022.log`, `peter2_receiver_20261022.log`_

### `logs/20261022_TRADE.log` — 35.7KB · 265행 · 최종 15:40:06

- 형식 평문 · 시각 인식 265행 · WARNING=17, INFO=248

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:57 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-22 08:41:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-22 09:32:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=27,232,318) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=1.0 안전배수=1.00(정상) → 1계약 (최소=1)
2026-10-22 09:32:00 [INFO] TRADE: [진입체크] SHORT→SHORT 1계약 A급(원시C) | sign✅ conf✅ vwap✅ cvd✅ ofi✅ fore❌ prev✅ time✅ risk✅ chas✅ coun✅ | conf=40.0%
2026-10-22 09:32:00 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 882.66 | 손절=886.54 1차=881.37(×0.60) 2차=878.78 horizon=3m hurst=trend
  …
2026-10-22 15:05:01 [INFO] TRADE: [체결청산-부분] SHORT 1계약 @ 856.42 | PnL=+4.05pt (+200,865원) | 잔여=1계약 | 사유=신동시간청산
2026-10-22 15:05:02 [INFO] TRADE: [Chejan] 상태=체결 주문번호=2420 code=A056B 방향=LONG 체결=1 미체결=0
2026-10-22 15:05:02 [INFO] TRADE: [Position] 체결청산 SHORT @ 856.44 | PnL=+4.03pt (+199,865원) | 신동시간청산
2026-10-22 15:05:02 [INFO] TRADE: [청산 완료] PnL=+4.04pt (+400,730원) | 포지션 합계 +400,730원 (레그 2)
2026-10-22 15:40:06 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 17 | 09:33:05 | 13:22:05 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=2 entry=881.94 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×265

**컴포넌트 상위 15** — `Chejan`×72, `Position`×50, `ShindongExec`×27, `주문요청`×20, `PositionFallback`×17, `Sizer`×13, `Virtual`×12, `체결진입`×9, `청산 완료`×9, `체결진입보정`×8, `진입체크`×7, `TickStop-S0C`×7, `체결청산-부분`×6, `ExitStage`×4, `ProfitGuard`×2

### `logs/20261022_WARN.log` — 813.5KB · 3557행 · 최종 15:46:12

- 형식 평문 · 시각 인식 3557행 · WARNING=3557

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-22 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-22 08:41:05 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr27)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-22 08:41:05 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr27)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-22 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 266ms account=783343908
  …
2026-10-22 15:46:01 [WARNING] SYSTEM: [LiveDBG] DynMCPanel.refresh slow 1485ms
2026-10-22 15:46:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2532ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2219 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=2532 band=INFO since_pipe_s=2220.6
2026-10-22 15:46:12 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 87.6ms | size=1484x913 candles=411 grid=24.5 spans=0.1 candles=15.8 dir=1.4 regime=11.0 markers=32.4 axes=1.0 cross=0.0 | slow_cnt=2912 total_cnt=3191 overlay_cnt=38540
2026-10-22 15:46:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6766ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2225 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=6766 band=WARN since_pipe_s=2231.7
2026-10-22 15:46:12 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20261022.log
```

</details>

**WARNING — 태그 38종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2912 | 08:56:12 | 15:46:12 | paintEvent slow 45.7ms | size=1484x930 candles=12 grid=23.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.7 cross=0.0 | slow_cnt=1 total_cnt=50 overlay_cnt=182 |
| `LiveDBG` | 196 | 08:41:05 | 15:46:12 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 76 | 08:41:15 | 15:30:04 | 그리기 70.6ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 785x1001 |
| `ChejanFlow` | 72 | 09:33:05 | 15:05:02 | account='783343908' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='385' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=09:33:05.732' | positio… |
| `ChejanMatch` | 72 | 09:33:05 | 15:05:02 | order_no='385' | pending='ENTRY:SHORT qty=2 filled=0 order_no=385 reason=진입 req_at=09:33:05.732' | pending_matched=True |
| `PendingOrder` | 40 | 09:33:05 | 15:05:02 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 882.04, 'reason': '진입', 'hint_source': '', 'atr': 2.1229, 'grade': 'S', 'stage': None, 'order_no': '', 'filled_qt… |
| `ExitCooldown` | 18 | 09:41:20 | 15:05:02 | 하드스톱(틱) 후 3분 재진입 금지 (until 09:44:20) |
| `EntryFillFlow` | 17 | 09:33:05 | 13:22:05 | actual_side='SHORT' | after='SHORT 2계약 @ 881.94' | applied_side='SHORT' | before='SHORT 2계약 @ 882.04' | fill_no='' | fill_price=881.94 | fill_qty=1 | order_no='385' | pending='ENTRY:SHORT qty=2 filled=1 order_no=385 reason=진입 req_at=09:33:… |
| `ScalerRefresh` | 16 | 09:05:00 | 15:08:00 | 5분 누적 수익률 +0.875% (임계 ±0.326%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `EntryAttempt` | 16 | 09:32:00 | 14:47:00 | atr=2.1571 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='SHORT' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='A' | pending='NONE' |… |
| `ExitFillFlow` | 15 | 09:41:20 | 15:05:02 | after='FLAT' | before='SHORT 2계약 @ 881.93' | fill_price=885.74 | fill_qty=2 | mode='final' | pending='EXIT_FULL:SHORT qty=2 filled=2 order_no=428 reason=하드스톱(틱) req_at=09:41:20.620' | reason='하드스톱(틱)' |
| `CybosMarginQty` | 13 | 09:32:00 | 14:54:00 | 조회 실패 ret=0 status=-1 msg=11298 시장가/신고대량/최우선/최유리지정가 주문은 단가를 입력하지 않습니다. (ordsvr35)(ord.fo.dpmyinqr.selanwordpsblqty) account=783343908 code=A056B |

**채널** — `SYSTEM`×3548, `HEALTH`×9

**컴포넌트 상위 15** — `ChartDBG`×2912, `LiveDBG`×196, `OptionFlowChart`×76, `ChejanFlow`×72, `ChejanMatch`×72, `PendingOrder`×40, `ExitCooldown`×18, `EntryFillFlow`×17, `ScalerRefresh`×16, `EntryAttempt`×16, `ExitFillFlow`×15, `CybosMarginQty`×13, `Health`×9, `EntrySendOrderResult`×9, `FixB`×9

### `logs/20261022_SYSTEM.log` — 1.1MB · 7416행 · 최종 15:47:14

- 형식 평문 · 시각 인식 7395행 · INFO=7395, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=19924 | 행감지=30s all_threads=True
2026-10-22 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.48s | predictions=0.05s trades=0.24s daily_stats=0.01s shap=0.01s raw_data=0.12s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-22 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-22 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-22 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-22 15:46:05 [INFO] SYSTEM: [RawFill] 2026-10-22 raw_candles 창 안 보충 0봉(bar_recovered=2) · 차트 보정 1봉(bar_recovered=3) — 보충 — / 보정 08:45
2026-10-22 15:46:05 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-22) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-22 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-22 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-22 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×7395

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1430, `PumpGuard`×768, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×408, `S6Detail`×370, `PipePerf`×370, `CybosEvent`×144, `MicroRegime`×118, `BalanceUI`×111, `System`×100, `OptionChain`×81, `BalanceRefresh`×81

### `logs/20261022_SIGNAL.log` — 556.7KB · 4956행 · 최종 15:40:06

- 형식 평문 · 시각 인식 4956행 · WARNING=1787, INFO=3169

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-10-22 15:10:28 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-22 15:40:06 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-22 15:40:06 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 0분(0.0%) / DN 181분(48.9%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-22 15:40:06 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-22 age=29m extreme=384 refresh=30 grade_x=152 cb3=0
2026-10-22 15:40:06 [INFO] SIGNAL: [ModelHealth] date=2026-10-22 앙상블유효가동률=75.1% | 파이프라인 370분 | ConstOut 6회/11분 {"3m": {"events": 6, "minutes": 11}} | WeightCollapse 81분 | 장중재학습 0회 | CB③ ready 271분/370분 (73%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1290 | 09:00:01 | 15:08:01 | 1m 'macro_vix' scale=0.0328 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 156 | 09:06:00 | 15:09:00 | 신뢰도 미달 34.7% < 39.0% → 강제 X등급 |
| `Model` | 132 | 09:00:00 | 14:20:00 | 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 114 | 09:00:00 | 14:30:00 | ts=08:59 horizon=1m age=1m max_z=+8.69(institution_futures_net) extreme=1 adj=1 |
| `WeightCollapse` | 82 | 09:07:00 | 15:07:01 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 6 | 08:45:05 | 08:45:05 | 1m CORE 'cvd_divergence' raw_std≈0(0.0204) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 6 | 11:29:01 | 14:26:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 10:44:00 | 10:44:00 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3322 < 필요 0.3810 (conf_floor=0.330, min_conf=0.381, span=0.0146, auc=0.593). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×4956

**컴포넌트 상위 15** — `ScalerFloor`×1302, `SIGNAL`×740, `MetaGate`×448, `Ensemble`×388, `FQAdj`×369, `ZeroDiag`×351, `Checklist`×197, `ATR-Horizon`×176, `Model`×138, `InstabilityGate`×126, `MicroRegime`×118, `ScalerMonitor`×115, `WeightCollapse`×82, `차단`×73, `ToxicityGate`×52

### `logs/20261022_LEARNING.log` — 283.3KB · 2806행 · 최종 15:40:06

- 형식 평문 · 시각 인식 2806행 · WARNING=143, INFO=2663

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00126 auc=0.574 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-22 08:40:47 [INFO] LEARNING: [Calibration:1m] 도달불가 해소 — out_max=0.3301 < conf_floor=0.3300 (n=85) → 보정 재적용
2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00083 auc=0.529 out_max=0.3405 (기준 auc<0.53 and span<0.020, 기저율=0.3400 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00069 auc=0.521 out_max=0.4121 (기준 auc<0.53 and span<0.020, 기저율=0.4118 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-10-22 15:40:06 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-22 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-22 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-22 15:40:06 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-22 15:40:06 [INFO] LEARNING: [Sigma] EOD sigma_20=0.12624% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 45 | 08:40:47 | 14:33:01 | 축퇴 감지 — span=0.00069 auc=0.521 out_max=0.4121 (기준 auc<0.53 and span<0.020, 기저율=0.4118 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:1m` | 41 | 08:40:47 | 14:04:01 | 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00126 auc=0.574 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 19 | 08:40:47 | 08:40:54 | 하한 도달불가 — out_max=0.2881 < conf_floor=0.3300 (span=0.00093 auc=0.606 out_max=0.2881, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 18 | 08:40:47 | 08:40:56 | 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00047 auc=0.615 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 11 | 08:40:47 | 11:20:00 | 축퇴 감지 — span=0.00021 auc=0.525 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 4 | 08:40:48 | 08:40:54 | 하한 도달불가 — out_max=0.3255 < conf_floor=0.3300 (span=0.00087 auc=0.554 out_max=0.3255, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 4 | 08:40:56 | 15:02:00 | 복원한 보정기가 축퇴 상태 — span=0.00376 auc=0.483 out_max=0.2870 (n=4816) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 11:01:02 | 11:01:02 | total=388ms raw_fetch=14ms pred_select=363ms pred_update=7ms pred_insert=1ms verified=2 |

**채널** — `LEARNING`×2806

**컴포넌트 상위 15** — `LEARNING`×1211, `SGD`×369, `sigma`×357, `Bias⚠`×253, `Bias`×156, `Calibration:30m`×90, `Calibration:1m`×81, `MetaConf`×78, `Calibration:5m`×36, `ScalerWarmup`×35, `Calibration:3m`×34, `OnlineLearner`×33, `Calibration:10m`×21, `BiasReset`×14, `SHAP`×11

### `logs/20261022_HEALTH.log` — 2.9KB · 19행 · 최종 15:04:00

- 형식 평문 · 시각 인식 19행 · WARNING=9, INFO=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1137ms | quality=1.00 | cache_age=52s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1
2026-10-22 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=666ms | quality=1.00 | cache_age=112s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1
2026-10-22 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 303ms (표본 20분)
2026-10-22 09:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=301ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [ShindongExec]×1
2026-10-22 09:49:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=358ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
  …
2026-10-22 13:20:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=355ms | quality=1.00 | cache_age=60s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
2026-10-22 14:14:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=421ms | quality=1.00 | cache_age=183s | exceptions_10m=1 | exc_tags=[ShindongExec]×1
2026-10-22 14:15:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=362ms | quality=1.00 | cache_age=59s | exceptions_10m=1 | exc_tags=[ShindongExec]×1
2026-10-22 15:03:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=188s | exceptions_10m=0
2026-10-22 15:04:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=293ms | quality=1.00 | cache_age=57s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 9 | 09:00:01 | 15:03:00 | level=WARNING degraded=OFF | latency=1137ms | quality=1.00 | cache_age=52s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1 |

**채널** — `HEALTH`×19

**컴포넌트 상위 15** — `Health`×18, `HealthTrend`×1

### `logs/retrain_eod_20261022.log` — 21.9KB · 149행 · 최종 15:53:39

- 형식 평문 · 시각 인식 149행 · WARNING=12, INFO=137

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 15:50:03,726 [INFO] EOD_RETRAIN: =======================================================
2026-10-22 15:50:03,727 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-22 15:50:03,727 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-22 15:50:03,727 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-22 15:50:03,727 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-22 15:53:39,311 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0384 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-22 15:53:39,312 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0922 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-22 15:53:39,314 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-10-22 15:53:39,318 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-22 15:53:39,320 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:41 | 15:52:37 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1499봉(81%)이 현행 학습구간 (현행 cutoff=2026-10-21 14:38:00 ≥ 홀드아웃 시작=2026-10-15 11:11:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-21 14:38 >= holdout_start=2026-10-15 11:11 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-21 … |
| `RegularFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-22 | 최신 2026-10-21 · 기준 9거래일. 복구: python scripts/collect_regular_futures.py --from 20261022 --to 20261022 |
| `OptionFlowFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-13(최신봉 15:33) | 기준 8거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\<YYYYMMDD>_OPTION_BACKFILL.log |
| `BackfillFilter` | 1 | 15:50:15 | 15:50:15 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 17050/43980 제외 (418차 결정 1) — 남은 26930행 |
| `UnitMismatch` | 1 | 15:50:15 | 15:50:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/26930행 제외 (559차 P1'-2) — 남은 25484행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `Retrain` | 1 | 15:50:53 | 15:50:53 | 3m 교체 보류(EOD 모델가드) — acc 하락 0.0365 > 허용 0.0250 (new=0.3412 old=0.3778) — 참고용 저장, 구모델 유지 |
| `RegimeFingerprint` | 1 | 15:53:38 | 15:53:38 | 백필 0행 제외 — 필터가 무효일 수 있다. 22802행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×63, `SIGNAL`×49, `EOD_RETRAIN`×27, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×42, `Retrain`×22, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2, `P8`×2

### `logs/retrain_intraday_20260624_102256.log` — 4.6KB · 39행 · 최종 10:23:28

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-06-24 10:22:56,958 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-24 10:22:56,958 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-06-24 10:22:56,958 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-24 10:22:56,958 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d5318140.json
2026-06-24 10:22:58,358 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-06-24 10:23:28,020 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.37s | old_acc=nan)
2026-06-24 10:23:28,024 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-06-24 10:23:28,024 [INFO] LEARNING: [Retrain] 완료 | 29.7초 | 성공=6/6 호라이즌
2026-06-24 10:23:28,025 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 31.1s 데이터=20000행
2026-06-24 10:23:28,027 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_d5318140.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 7 |
| 진입 등록(`[Position] 진입`) | 15 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 0 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 6 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 9 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 9 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 9 |
| 차단(`[차단]`) | 73 |
| 사이저 호출(`[Sizer]`) | 13 |

> 🔴 **엔진 진입 0건인데 계좌 체결 9건**(외부표식 0 · 피터2 0 · 판별불가 9) — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.
>
> 별도로 **가상 장부 진입 6건**이 `[Position] 진입` 에 섞여 있다 — 실주문이 없으므로 계좌 체결·손익과 무관하다(아래 「가상 장부」 표).

### 포지션 9건 · 승 6 (67%) · 합계 +23.14pt (+1,127,140원)  ※ 레그 15행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:33:05 | 추정 | SHORT | 2 | — | 1 | -7.62 | -384,351 | 하드스톱(틱) |
| 09:52:05 | 추정 | SHORT | 2 | — | 1 | +5.54 | +273,624 | 하드스톱(틱) |
| 10:13:05 | 추정 | SHORT | 2 | — | 2 | +14.94 | +743,648 | 하드스톱(틱) |
| 10:51:05 | 추정 | LONG | 2 | — | 1 | -6.28 | -317,327 | 하드스톱(틱) |
| 10:54:05 | 추정 | SHORT | 2 | — | 2 | +3.12 | +152,682 | 하드스톱(틱) |
| 11:44:05 | 추정 | LONG | 2 | — | 2 | +0.68 | +30,702 | 하드스톱(틱) |
| 12:34:05 | 추정 | SHORT | 2 | — | 2 | +8.08 | +400,708 | 신동최종 |
| 13:08:05 | 추정 | SHORT | 2 | — | 2 | -3.40 | -173,276 | 하드스톱(틱) |
| 13:22:05 | 추정 | SHORT | 2 | — | 2 | +8.08 | +400,730 | 신동시간청산 |

**출처별 소계** — 추정 9건 +1,127,140원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「피터2」는 `[Peter2] 진입`이 동반된 보조 로직 자리로 역시 엔진 성적이 아니다. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**가상 장부 6건(청산 6 · 합계 -194,530원) — 실주문 없음, 엔진·계좌 손익 아님**

| 진입 | 주체 | 방향 | 수량 | hz | 가상 pt | 가상 net(원) | 가상 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:32:00 | 미륵 | SHORT | 1 | 3m | +0.54 | +25,287 | 가상:하드스톱 |
| 09:38:00 | 미륵 | SHORT | 1 | 3m | -3.76 | -189,515 | 가상:하드스톱 |
| 10:06:00 | 미륵 | SHORT | 1 | 3m | -3.29 | -166,251 | 가상:하드스톱 |
| 10:38:00 | 미륵 | SHORT | 1 | 3m | +0.40 | +18,157 | 가상:하드스톱 |
| 10:42:00 | 미륵 | SHORT | 1 | 3m | +0.46 | +21,413 | 가상:하드스톱 |
| 14:47:00 | 미륵 | SHORT | 1 | 3m | +1.96 | +96,379 | 가상:TP2(전량) |

> ⚠ 이 표는 `[Virtual] … 가상진입`/`가상청산` 로그로 조립한 **가상 장부**다. 같은 초에 `[Position] 진입` 이 찍혀 진입 건수에는 잡히지만 체결이 없다 — 3원 대사(로그·DB·브로커)에서 로그 쪽이 더 많아 보이면 먼저 이 표를 뺄 것.

**청산 레그 15행** (부분청산 6 · 전량청산 9)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:41:20 | 전량 | 2 | -3.81 | -384,351 | 하드스톱(틱) |
| 10:07:27 | 전량 | 2 | +2.77 | +273,624 | 하드스톱(틱) |
| 10:38:42 | 부분 | 1 | +7.63 | +379,824 | 신동1차 |
| 10:45:14 | 전량 | 1 | +7.31 | +363,824 | 하드스톱(틱) |
| 10:53:05 | 전량 | 2 | -3.14 | -317,327 | 하드스톱(틱) |
| 11:30:32 | 부분 | 1 | +1.57 | +76,841 | 하드스톱(틱) |
| 11:30:32 | 전량 | 1 | +1.55 | +75,841 | 하드스톱(틱) |
| 12:28:08 | 부분 | 1 | +0.35 | +15,851 | 하드스톱(틱) |
| 12:28:08 | 전량 | 1 | +0.33 | +14,851 | 하드스톱(틱) |
| 13:04:26 | 부분 | 1 | +3.77 | +186,854 | 신동1차 |
| 13:04:48 | 전량 | 1 | +4.31 | +213,854 | 신동최종 |
| 13:16:08 | 부분 | 1 | -1.67 | -85,138 | 하드스톱(틱) |
| 13:16:08 | 전량 | 1 | -1.73 | -88,138 | 하드스톱(틱) |
| 15:05:01 | 부분 | 1 | +4.05 | +200,865 | 신동시간청산 |
| 15:05:02 | 전량 | 1 | +4.03 | +199,865 | 신동시간청산 |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×10, `신동1차`×2, `신동시간청산`×2, `신동최종`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 7/9건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 +1,127,140 = 포지션합 +1,127,140 → OK · `[청산 완료]` 9건 = 조립 포지션 9건 → OK

### CB③ 판정 가능 시간 — **271분 / 370분 (73%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 15건

| 시각 | 출처 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|---|
| 09:32:00 | 가상 | SHORT | 1 | 882.66 | 3m | trend |
| 09:33:05 | 추정 | SHORT | 2 | 882.04 | — | — |
| 09:38:00 | 가상 | SHORT | 1 | 882.3 | 3m | trend |
| 09:52:05 | 추정 | SHORT | 2 | 888.4 | — | — |
| 10:06:00 | 가상 | SHORT | 1 | 882.64 | 3m | trend |
| 10:13:05 | 추정 | SHORT | 2 | 882.2 | — | — |
| 10:38:00 | 가상 | SHORT | 1 | 875.94 | 3m | neutral |
| 10:42:00 | 가상 | SHORT | 1 | 872.72 | 3m | trend |
| 10:51:05 | 추정 | LONG | 2 | 875.46 | — | — |
| 10:54:05 | 추정 | SHORT | 2 | 873.4 | — | — |
| 11:44:05 | 추정 | LONG | 2 | 867.96 | — | — |
| 12:34:05 | 추정 | SHORT | 2 | 866.26 | — | — |
| 13:08:05 | 추정 | SHORT | 2 | 862.22 | — | — |
| 13:22:05 | 추정 | SHORT | 2 | 860.46 | — | — |
| 14:47:00 | 가상 | SHORT | 1 | 853.2 | 3m | mean-revert |

계약수 분포 — 1계약×6, 2계약×9

등급 분포 — `A급(원시C)`×7

**진입한 건들의 체크리스트 미통과 항목** — `fore`×7, `chas`×4, `cvd`×1, `risk`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×13

실제 진입 계약수 — **1계약**×6, **2계약**×9

배수 조합 상위 — `conf=0.6 regime=1.0 safe=1.00`×13

### 차단 사유 73건 · 19종

| 건수 | 사유 |
|---|---|
| 51 | 등급X — 미통과 항목: 2_confidence |
| 5 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 1 | JointGateBlock — meta=0.71 tox=0.70 joint=0.497 < 0.50 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 9_risk, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 9_risk, 11_countertrend |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 9_risk |
| 1 | Reverse Clamp (P3-b) — 청산 후 역방향(SHORT→LONG) 27s 이내 진입 금지 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign |
| 1 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 11_countertrend |
| 1 | 청산 후 쿨다운 — 13초 후 재진입 가능 |
| 1 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 1 | 청산 후 쿨다운 — 124초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 65초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 4초 후 재진입 가능 |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 청산 후 쿨다운 — 31초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 107초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 61초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×51, `3_vwap`×6, `6_foreign`×6, `5_ofi`×4, `9_risk`×3, `11_countertrend`×3, `4_cvd`×2, `7_prev_bar`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 5건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 11건 · 최대 6766ms · 5초 초과 1건

상위 — 6766ms, 4266ms, 3594ms, 3171ms, 3157ms, 3047ms, 2532ms, 2469ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 15:46:12 | 6766ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261022_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:15 2026-10-22 15:40:15 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 33분/일 < 하한 60분 — 금일 28분. | ConfFloorGuard 도달가능 0분 · 도달불가 119분 · 재지않음 251분
--- [CB] ×3(표본)
09:41:20 2026-10-22 09:41:20 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:53:05 2026-10-22 10:53:05 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
13:16:08 2026-10-22 13:16:08 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:41:20 2026-10-22 09:41:20 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:44:20)
09:41:20 2026-10-22 09:41:20 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:44:20)
09:48:00 2026-10-22 09:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=301ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [ShindongExec]×1
10:07:27 2026-10-22 10:07:27 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 10:09:27)
--- [ExitStageRecon] ×1(표본)
15:40:06 2026-10-22 15:40:06 [WARNING] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 1레그 / 1포지션 중 TP 이벤트 대응 0 · 단일계약 보호전환(설계) 0 · 미대응 1 ⚠ 미대응 합계 +743,648원 (진입 10:13:05). 이 레그들은 라벨상 「TP1 뒤 트레일(이익 청산)」이지만 그 포지션에 TP가 난 적이 없다 — 손절률 분모…
--- [SHAP] 슬로우 ×1(표본)
14:38:01 2026-10-22 14:38:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 923ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
09:00:01 2026-10-22 09:00:01 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2422ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2422 band=INFO since_pipe_s=0.0
11:01:05 2026-10-22 11:01:05 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3171ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3171 band=INFO since_pipe_s=0.0
11:01:07 2026-10-22 11:01:07 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2469ms — 메인 스레드 블로킹 발생 | pipe_elapsed=1 watchdog_alerted=[] | [MainStall] stall_ms=2469 band=INFO since_pipe_s=2.5
14:15:02 2026-10-22 14:15:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3047ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3047 band=INFO since_pipe_s=0.0
```

### `logs/20261022_SYSTEM.log`
```
--- ConstOut ×6(표본)
11:29:01 2026-10-22 11:29:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3595) | 앙상블 제외는 유지
11:38:01 2026-10-22 11:38:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3602) | 앙상블 제외는 유지
13:30:00 2026-10-22 13:30:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3717) | 앙상블 제외는 유지
13:38:01 2026-10-22 13:38:01 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4953) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:06 2026-10-22 15:40:06 [INFO] SYSTEM: [CB③계측] 조건성립 271분 / 판정가능 271분 / 파이프라인 370분 · 그 창 진입 3포지션 · 손익 +858,042원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-22 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-10-22 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:10:00 2026-10-22 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:16:00 2026-10-22 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:06 2026-10-22 15:40:06 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:06 2026-10-22 15:40:06 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:04 2026-10-22 15:11:04 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:17 2026-10-22 15:40:17 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-10-22 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:17 2026-10-22 15:40:17 [INFO] SYSTEM: [Notify] ℹ️ [15:40:17] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:17 2026-10-22 15:40:17 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 402초
15:40:17 2026-10-22 15:40:17 [INFO] SYSTEM: 자동 종료 예약 — 417초 후 Qt 이벤트 루프 종료
```

### `logs/20261022_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
10:44:00 2026-10-22 10:44:00 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3322 < 필요 0.3810 (conf_floor=0.330, min_conf=0.381, span=0.0146, auc=0.593). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
--- ConstOut ×8(표본)
11:29:01 2026-10-22 11:29:01 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0580 dir=-1)
11:29:01 2026-10-22 11:29:01 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
11:29:01 2026-10-22 11:29:01 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
11:30:00 2026-10-22 11:30:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.0580 dir=-1)
--- WeightCollapse ×8(표본)
09:07:00 2026-10-22 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:07:00 2026-10-22 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-10-22 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-10-22 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
--- 안전망 ×8(표본)
09:07:00 2026-10-22 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:07:00 2026-10-22 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (2연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-22 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-22 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
```

### `logs/20261022_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:47 2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00126 auc=0.574 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:47 2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00083 auc=0.529 out_max=0.3405 (기준 auc<0.53 and span<0.020, 기저율=0.3400 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:47 2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00069 auc=0.521 out_max=0.4121 (기준 auc<0.53 and span<0.020, 기저율=0.4118 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:47 2026-10-22 08:40:47 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00095 auc=0.540 out_max=0.3339 (n=120) → 보정 재적용
```

### `logs/20261022_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
09:48:00 2026-10-22 09:48:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=301ms | quality=1.00 | cache_age=181s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [ShindongExec]×1
09:49:00 2026-10-22 09:49:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=358ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
11:01:04 2026-10-22 11:01:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1773ms | quality=1.00 | cache_age=158s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
11:02:01 2026-10-22 11:02:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=362ms | quality=1.00 | cache_age=31s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [ShindongExec]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261022_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:57 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 10 | 09:54:05 [INFO] 손절 892.5 → 888.50 (replay) |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 10 | 15:05:01 [INFO] 신동시간청산 SHORT 2계약 @ 856.46 체결대기 (poll) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:06 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261022_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 18 | 08:41:05 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:52:35 [WARNING] A056B 실측=-1.39 n=7 spread=0.13 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.39 | 직전일=-1.82(prev_day:2026-10-1… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 11 | 08:56:12 [WARNING] paintEvent slow 45.7ms | size=1484x930 candles=12 grid=23.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=… |
| 10:00 | 장중 초반 | 99 | 09:54:00 [WARNING] paintEvent slow 60.4ms | size=1484x911 candles=70 grid=26.8 spans=0.0 candles=2.8 dir=0.2 regime=4.1 markers=… |
| 12:00 | 장중 중간점 | 92 | 11:54:00 [WARNING] paintEvent slow 99.2ms | size=1484x911 candles=190 grid=33.9 spans=0.1 candles=10.0 dir=1.0 regime=9.1 marker… |
| 14:00 | 장중 후반 · 장중 재학습 | 94 | 13:54:00 [WARNING] paintEvent slow 109.1ms | size=1484x911 candles=310 grid=37.7 spans=0.2 candles=18.1 dir=1.6 regime=13.6 mark… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 122 | 15:04:00 [WARNING] paintEvent slow 98.9ms | size=1484x913 candles=380 grid=29.2 spans=0.2 candles=19.2 dir=2.4 regime=8.0 marker… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 100 | 15:12:00 [WARNING] paintEvent slow 89.5ms | size=1484x913 candles=388 grid=16.7 spans=0.5 candles=16.6 dir=1.8 regime=9.1 marker… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 21 | 15:34:00 [WARNING] paintEvent slow 106.4ms | size=1484x913 candles=410 grid=26.5 spans=0.2 candles=17.0 dir=2.1 regime=8.7 marke… |
| 15:47 | EOD 재학습(py310_64) 완료 | 9 | 15:44:20 [WARNING] paintEvent slow 112.6ms | size=1484x913 candles=410 grid=20.3 spans=0.2 candles=18.2 dir=2.2 regime=14.1 mark… |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261022_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 102 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=19924 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 141 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 215 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 224 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 199 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 211 | 13:54:00 [INFO] code=A056B from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 237 | 15:04:00 [INFO] code=A056B from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 173 | 15:12:00 [INFO] code=A056B from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 66 | 15:34:00 [INFO] code=A056B from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 12 | 15:41:04 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=RISK_ON | 포지션=FLAT | 15:41:04 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261022_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 38 | 08:45:05 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0204) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 85 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 219 | 09:00:00 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 128 | 09:56:00 [WARNING] 신뢰도 미달 32.0% < 39.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 85 | 11:54:00 [WARNING] 신뢰도 미달 32.8% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 241 | 13:54:00 [WARNING] 신뢰도 미달 33.3% < 37.7% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 100 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:06 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261021 | 15:47 | 로그 본문 |
| 20261020 | 15:47 | 로그 본문 |
| 20261019 | 15:47 | 로그 본문 |
| 20261017 | 12:11 | 로그 본문 |
| 20261016 | 15:47 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261022** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-21 (MW0601 — 장전 점검)
## 2026-10-21 (MW0601 — 장중 점검)
## 2026-10-21 (MW0601 — 장후 점검, 종합 완성본)
## 2026-10-21 (MW0601 701차 후속 — 장후 자동조치: F-701-B 조사로 1-6 전제 반박 · 코드 무변경) — 🟡 **조사 완료 · 구현 0건**
## 2026-10-22 (MW0601 — 장전 점검)
## 2026-10-22 (MW0601 — 장중 점검)
## 2026-10-22 (MW0601 704차 — [9842] `CpSvr9842` 실계좌 로그인에서 사용 가능 확정 · 점검 프로브 신설) — 🟢 **조사 완료 · 매매 코드 무변경**
## 2026-10-22 (MW0601 704차 후속 — [9842] 행사가 × 투자자 수집기 구현 · `STRIKE_INVESTOR_FLOW_ENABLED=False` 배포) — 🟡 **구현 완료 · 라이브 미검증**
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
**콜·풋 각 1,372/1,372칸 일치** — API = HTS 화면 같은 원천.
  - 7222 대사: Σ행사가 외인 당일 vs `mon_call`/`mon_put` 외인 차 +27–40 / +15–17(≈1%, 9842가 두 번 다 0 쪽).
  - **인덱스 2 기관계 = Σ인덱스 3–10 소계**, 기관계 제외 합 = 0 — 전 행 성립.
  - **위클리 미지원 확정** — 월물값 `'3'` → `near_far_gb` 입력 오류. 최근월/차근월만.
  - 🔴 **명세 「연속조회 없음」은 틀렸다** — 차근월 `71102 조회가 계속됩니다` → 2쪽 567행.
  - `amt` 단위 십만원 · 매도 보유 음수 · 행사가는 `CpOptionCode` 필드 4(문자열 파싱 금지).
- **결정(사용자)**: 모의계정에서는 사용하지 않는다(1588-4488 문의 불필요). **수집기(구현계획 P2)는 장 마감 후 구현.**
- **Why**: 「등급 차단」이 최종 결론으로 남아 있으면 다음 세션이 그대로 인용한다. 또 명세만 믿고 수집기를 짰다면 차근월 행사가가 조용히 잘리고(연속조회), 기관이 이중계상됐다(소계) — 둘 다 「조용히 그럴듯한 값」 유형.
- **How to apply**: 수집기 설계 조건 ① 실계좌 로그인일 때만 — 차단 응답이면 행을 쓰지 않고 상태 테이블에 `ok=0`(미측정 ≠ 0) ② 차근월 `Continue` 루프 ③ 기관계는 소계로 저장·합산 제외 ④ 먼스리만. MW0602(CREON)에서 쓰려면 같은 프로브 1회 선행.
- **검증**: `scripts/probe_cpsvr9842.py`(읽기전용, 요청 상한 8건+연속 4건) · `logs/probe_9842_20261022_142817.md`(+`.json`) · `logs/20261022_PROBE.log`. 문서 `옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md` §7 · `9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md` 머리 정정.

## 2026-10-22 (MW0601 704차 후속 — [9842] 행사가 × 투자자 수집기 구현 · `STRIKE_INVESTOR_FLOW_ENABLED=False` 배포) — 🟡 **구현 완료 · 라이브 미검증**

- **무엇**: `collection/cybos/strike_investor_flow.py`(CpSvr9842 당일 모드, 수급 타이머 경로) · `main.py:_fetch_strike_investor_flow`(7222 뒤 호출) · `scripts/strike_investor_snapshot.py`(기간 모드 = HTS `_P`, 백필·HTS 대사) · 설정 `STRIKE_INVESTOR_FLOW_*` · 별도 DB `data/db/strike_investor.db`.
- **설계(704차 실측 조건)**: ① 등급 차단 문구(「계좌등급」)면 행 없이 상태 1행 + WARNING 1회, **그날 재호출 없음** ② 연속조회 루프(상한 6쪽, 넘으면 `ok=0 truncated`) ③ 행사가는 `CpOptionCode` 필드 4 — 미매핑은 `strike=NULL` + 상태 `unmapped`(문자열 추측 금지) ④ 주체 대사(기관계=Σ3–10 · 기관계 제외 합=0) 위반 행 수를 상태에 ⑤ 조회 한도 잔여 < 25+요청수면 그 분 `SKIP_QUOTA`.
- **저장 규칙**: 프로세스가 그날 처음 찍는 스냅샷은 전 행(`full=1`), 이후 **바뀐 행만**. 시각 t 값 = `snap_hm<=t` 최신 행, 없으면 0. 그 이전 `ok=1·full=1` 상태가 없으면 **미측정**(`snapshot_at()` → None). DB 쓰기 실패 시 다음 회차를 전체 저장으로 되돌린다.
- **Why**: 전 행 매분 저장이면 하루 약 26만 행이고 대부분 불변. 재기동이 「바뀐 행만」 기준을 지우는 552-10 계열 결함은 「첫 스냅샷 전체」로 막는다.
- **How to apply**: 켜기 전 `scripts/strike_investor_snapshot.py --end <오늘>`을 장후 1회 돌려 HTS 대사 일치 확인 → `STRIKE_INVESTOR_FLOW_ENABLED=True` + 재기동. 만기주는 `STRIKE_INVESTOR_FLOW_MONTHS=("1","2")`. ⚠ 과거 날짜 백필은 만기 지난 월물 코드가 `CpOptionCode`에 없어 `strike=NULL`이 된다(원값은 보존) — 기간 모드의 「최근월」이 종료일 기준인지도 미확인.
- **검증**: `tests/test_704_strike_investor_flow.py` 11건 통과(py37_32) · `test_611`·`test_617` 래칫·`test_537` DLL 감사 통과. `test_457::test_db_fallback_columns_have_measured_flag` 1건 실패는 703차 `main_dashboard.py peter_paste` 기존 결함(이번 변경 무관, 파일 무변경).

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2026-10-20 (MW0601 698차 후속 — 장후 자동조치)
### 2026-10-21 (MW0601 — 장전 점검)
### 2026-10-21 (MW0601 — 장중 점검)
### 2026-10-21 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-22 (MW0601 703차 — F-701-A ProfitGuard 계좌 축)
### 2026-10-22 (MW0601 — 장전 점검)
### 2026-10-22 (MW0601 — 장중 점검)
### 2026-10-22 (MW0601 704차 — [9842] CpSvr9842 실계좌 사용 가능)
```

미완료 체크박스 **3302건** (끝에서 30건)
```
- [ ] **698-2** 계속 — 평가 창 1/5. 최종 판정 빠르면 10-26 장후. (첫날 통합 p90 76.5초는 참고만)
- [ ] (참고) 12:18 수집 탭이 `compose/post`·피터 글 상세로 이탈 4회(각 1초 내 자동 복귀) — 사람이 수집 탭을 클릭한 흔적, 그 창(12:14)만 관측 31줄로 늘었다. 수집 탭은 건드리지 않도록.
- [ ] (참고) 14:06 이후 새로고침당 요청 2→1회(창당 24→12줄) — 원인 미확인(두 번째 요청은 추가 로드로 추정), 지연·누락 영향 없음. 13:09:38 한도 헤더 없는 응답 1건(무해).
- [ ] (참고) 수신기는 10-19 08:40 기동(pid 5780) 그대로 — 코드 최종 변경 10-16(7a5275b)이라 구버전 아님. 오늘 08:40 `SKIP already running` 은 자동기동 중복 시도(무해).
- [ ] **F-2b (A등급 후보, 장후 전용)** `retrain_eod.py` 424차 가드 문구·조건 정정 — 상류 `[BackfillFilter]`가 이미 제거했으면 INFO("상류에서 N행 제외됨")로 낮추고, 진짜 경보는 "창 안에 마커행이 있는데 상류 제외 0"으로 옮긴다. 상류 제외 수를 retrainer에서 노출해야 하므로 `learn…
- [ ] **O-t1 (이월, 그대로)** 진입체크 통과 후 미진입 3건 — 다음 장후 코드 추적.
- [ ] **698-T (P2)** 전체 테스트 스위트 미청결 — ~66%에서 대시보드 테스트 access violation으로 중단(`main_dashboard.py:7434`, 606-4 동일 자리) + 실패 13파일(457·477·483·490·493·497·498·504·554·555·598·621·virtual_book). 기준선(이전 커밋) …
- [ ] **O-p1 (장중 재확인)** 캐너리 z경고 08:59 재측정 11개(08:55 재적합 직후 3개 대비 +8) — 09:10~09:15 재측정값으로 안정권(8개 이하) 복귀 여부 판정.
- [ ] **O-p2 (장중 재확인, 기존 1-3 계승)** 피터2 A056B 오프셋 스프레드 08:52 기준 0.12(n=7, 표본 8 미만이라 판정 보류) — 표본 8개 이상 확보 후 안정 여부 재확인.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation — 오늘로 6거래일 연속 재현, 여전히 사용자 결정 대기.
- [ ] **1-3 (P0, 사용자 결정 필요, 신규)** 신동이 오늘 09:05 실거래 주체로 첫 전환(`data/trade_principal.json` PETER→SHINDONG) — `main.py:5977 _shindong_entry_block_reason()`가 공식 CB·킬스위치는 검사하나 `profit_guard.is_entry_allowe…
- [ ] **O-p2 (장후 최종판정, 기존 1-3 계승)** 피터2 오프셋 스프레드 — 09:03~09:35 불안정 확대(0.32~0.56) 후 10:56 이후 n=30, 12:05:42 spread=0.06 safe=True로 안정권 복귀. 오늘치는 "개선"이나 하루 전체 추이로 장후 최종판정.
- [ ] (이월, 격상) **1-2** 메인 스레드 블로킹 — 장중 10건·최대 9672ms·5초초과 2건(11:52:05 건은 파이프라인 경과시간이 CB⑤ 작동기준의 98%까지 근접). 482차 F-3 섀도 계측 대상 그대로, 새 Fix 없음.
- [ ] (참고, 신규 아님) **1-5 / O-2·F-5** `[FixB] open_position 실패` 1건(11:44:13, Chejan 분할체결 레이스) — 설계된 복구로 즉시 정상화. O-2 기준(2건 이상) 미충족, 우선순위 변경 없음.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation — 정규장 이후 오늘도 0건, 여전히 사용자 결정 대기.
- [ ] 🔴 **F-10 (C, 사용자 결정 대기 — 2026-08-31 등록분 재상정)** 하드스톱 분할 체결 시 `exit_stage` 오분류 수정 승인 여부. 10-21 신동 채널 6레그 추가 재현(이번 건은 장후 점검이 이 오분류 위에 R-1 개선안까지 세움). 08-31 계획서가 이름 붙인 회귀 테스트 `tests/test_507_exit_st…
- [ ] **O-t1 (10-22부터 신규 관측)** 신동 `TRAIL_AFTER_TP1` 레그의 전량손실 비율 — `[ExitStageRecon]` 일일 자기대사 로그로 5거래일 누적 후 1-6 재판정.
- [ ] **O-t2 (상시 관측)** 1-3 미해결 상태에서 신동의 연속손실(CB② 임계 3 근접 여부) — 사용자 결정 전까지 매 장후 점검.
- [ ] **O-t3** `trade_principal.json`의 `principal`이 `MIREUK`로 복귀하는 날 — 복귀 시 `docs/정기점검/수익률향상_누적대장.md` P5-01~18 재가동.
- [ ] **703-0 (장후)** 재기동 후 라이브 첫날 확인 — `[ProfitGuard] 포지션 청산 반영 …` 매 청산 1줄 · 신동/피터 기각 사유 `ProfitGuard [L…]` · 13시 이후 L3 카운트 증가 · 미륵 가상 시 `[ProfitGuard][Virtual]`. 커밋은 사용자 지시 후.
- [ ] **703-1 (10거래일 뒤, 2026-11-05경)** 임계 재판정 — 래치 날별 「래치 후 놓친 손익 vs 피한 손실」(신동 재생 기록 대비). L1 150만/35% · L2 400만 · L3 200만/2회 · L4 100만/3연패는 19일 표본 출발값이다.
- [ ] **703-2** 실행 중 프로세스에서 ProfitGuard 패널 [적용] 금지(옛 값 재저장) — 재기동으로 prefs 703 값이 로드된 것을 배지 툴팁으로 확인.
- [ ] **703-3 (참고)** 신동 실거래 기각(ProfitGuard)이 재생 채점과 실거래를 가른다 — 신동 일일 리포트 대사에 `REJECT why=ProfitGuard` 사유 표기 여부 확인.
- [ ] **F-1 (P2, 장후 적용)** `config/dailycheck_targets.json`의 `documented_disabled_flags`에 `PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL` 추가 — 703차가 신설한 플래그를 점검 도구 화이트리스트가 아직 모름(근거 자체는 DECISION_LOG·커밋 메시지에 이미 …
- [ ] **O-i1 (장후가 닫을 것)** 703-0의 "매 청산 1줄" 요건은 오늘 장중 중 충족 확인(`[ProfitGuard] 포지션 청산 반영 출처=SHINDONG …` 6줄 = 오늘 청산 6건과 1:1). 다만 "실제 차단 작동"(`ProfitGuard [L…]` 기각 · L3 카운트 증가 · `[ProfitGuard][Virtual]`) 사…
- [ ] **G-2 (P2, 점검 도구 자체 개선 — 매매 코드 무관)** `scripts/collect_evidence.py` 날짜 토큰 매칭이 `retrain_intraday_{과거날짜}_{DATE}56.log` 식으로 오늘 날짜와 무관한 과거 파일(2026-06-24·2026-10-15 등)을 "오늘 파일"로 다이제스트 §4에 집계 — 어제(10-…
- [ ] **704-1 (장 마감 후)** `collection/cybos/strike_investor_flow.py` 수집기 구현 — 구현계획 P2. 조건: 실계좌 로그인 한정(차단 시 행 미기록·상태 `ok=0`) · 차근월 `Continue` 루프 · 기관계 소계 저장(합산 제외) · 먼스리만 · `STRIKE_INVESTOR_FLOW_ENABLE…
- [ ] **704-2** P3 대사 — 장후 API 스냅샷 vs HTS `_P` 전 칸 · Σ외인 vs 7222(오늘 ≈1%, 9842가 0 쪽 — 갱신 지연 여부 확인) · 기관계 제외 합 = 0.
- [ ] **704-3 (선택)** MW0602(CREON)에서 `scripts/probe_cpsvr9842.py` 1회 — 그쪽에서 쓸 때만.
- [ ] **704-4 (신규)** `test_457::test_db_fallback_columns_have_measured_flag` 실패 — `dashboard/main_dashboard.py` `peter_paste` INSERT 의 `or ''`·`or 0.0` 폴백(703차 이후). 704차 무관, 별도 처리.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
virtual_cooldown(until HH:MM)`). 10-20·10-21 2거래일 연속 동일 패턴 재현, 버그 아님 — 추가 코드 추적 불필요.

### 2026-10-22 (MW0601 703차 — F-701-A ProfitGuard 계좌 축)
- [ ] **703-0 (장후)** 재기동 후 라이브 첫날 확인 — `[ProfitGuard] 포지션 청산 반영 …` 매 청산 1줄 · 신동/피터 기각 사유 `ProfitGuard [L…]` · 13시 이후 L3 카운트 증가 · 미륵 가상 시 `[ProfitGuard][Virtual]`. 커밋은 사용자 지시 후.
- [ ] **703-1 (10거래일 뒤, 2026-11-05경)** 임계 재판정 — 래치 날별 「래치 후 놓친 손익 vs 피한 손실」(신동 재생 기록 대비). L1 150만/35% · L2 400만 · L3 200만/2회 · L4 100만/3연패는 19일 표본 출발값이다.
- [ ] **703-2** 실행 중 프로세스에서 ProfitGuard 패널 [적용] 금지(옛 값 재저장) — 재기동으로 prefs 703 값이 로드된 것을 배지 툴팁으로 확인.
- [ ] **703-3 (참고)** 신동 실거래 기각(ProfitGuard)이 재생 채점과 실거래를 가른다 — 신동 일일 리포트 대사에 `REJECT why=ProfitGuard` 사유 표기 여부 확인.

### 2026-10-22 (MW0601 — 장전 점검)
- [ ] **F-1 (P2, 장후 적용)** `config/dailycheck_targets.json`의 `documented_disabled_flags`에 `PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL` 추가 — 703차가 신설한 플래그를 점검 도구 화이트리스트가 아직 모름(근거 자체는 DECISION_LOG·커밋 메시지에 이미 있음). 회귀위험 없음(점검 도구 설정 파일).

### 2026-10-22 (MW0601 — 장중 점검)
- [ ] **O-i1 (장후가 닫을 것)** 703-0의 "매 청산 1줄" 요건은 오늘 장중 중 충족 확인(`[ProfitGuard] 포지션 청산 반영 출처=SHINDONG …` 6줄 = 오늘 청산 6건과 1:1). 다만 "실제 차단 작동"(`ProfitGuard [L…]` 기각 · L3 카운트 증가 · `[ProfitGuard][Virtual]`) 사례는 장중 내내 0건 — 오늘 손익이 전부 임계(L1~L4) 미달 구간이었기 때문. 703-0을 완전 종결로 바꾸지 말고, 장후 15:10 종가까지 재확인 후 판정/판정보류/이월 중 하나로 닫을 것.
- [ ] **G-2 (P2, 점검 도구 자체 개선 — 매매 코드 무관)** `scripts/collect_evidence.py` 날짜 토큰 매칭이 `retrain_intraday_{과거날짜}_{DATE}56.log` 식으로 오늘 날짜와 무관한 과거 파일(2026-06-24·2026-10-15 등)을 "오늘 파일"로 다이제스트 §4에 집계 — 어제(10-21)도 동일 현상(2026-07-03·07-06 파일). 파일명 앞머리 8자리 날짜가 수집 대상일과 다르면 §1 인벤토리에만 남기고 다이제스트 본문에서는 빼도록(또는 "다른 날짜 파일" 주석) 수정 제안. 우선순위 낮음.

### 2026-10-22 (MW0601 704차 — [9842] CpSvr9842 실계좌 사용 가능)
- [ ] **704-1 (장 마감 후)** `collection/cybos/strike_investor_flow.py` 수집기 구현 — 구현계획 P2. 조건: 실계좌 로그인 한정(차단 시 행 미기록·상태 `ok=0`) · 차근월 `Continue` 루프 · 기관계 소계 저장(합산 제외) · 먼스리만 · `STRIKE_INVESTOR_FLOW_ENABLED=False`로 배포 · 피처/게이트 미배선.
- [ ] **704-2** P3 대사 — 장후 API 스냅샷 vs HTS `_P` 전 칸 · Σ외인 vs 7222(오늘 ≈1%, 9842가 0 쪽 — 갱신 지연 여부 확인) · 기관계 제외 합 = 0.
- [ ] **704-3 (선택)** MW0602(CREON)에서 `scripts/probe_cpsvr9842.py` 1회 — 그쪽에서 쓸 때만.
- [x] **704-1 구현 완료(2026-10-22 장후)** — `ENABLED=False` 배포. 남은 것: ⓐ 장후 `strike_investor_snapshot.py --end <날짜>` 실행·HTS 대사 ⓑ `ENABLED=True` + 재기동 ⓒ 첫 라이브 날 `[StrikeInvestor] stored=… (오늘 첫 수집 — 전체 저장)` · 상태 테이블 `ok=1` 비율 확인.
- [ ] **704-4 (신규)** `test_457::test_db_fallback_columns_have_measured_flag` 실패 — `dashboard/main_dashboard.py` `peter_paste` INSERT 의 `or ''`·`or 0.0` 폴백(703차 이후). 704차 무관, 별도 처리.

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

### `data/dailycheck_markers/claude-20261022-intra-cowork-intra-0330.json` — 170B · 10-22 12:30:42
```json
{
 "pc": "claude",
 "date": "20261022",
 "phase": "intra",
 "session": "cowork-intra-0330",
 "pid": 8,
 "started_epoch": 1792639842.8040602,
 "started_at": "2026-10-22 03:30:42"
}
```

### `data/dailycheck_markers/claude-20261022-post-cowork-postmarket-1792653493.json` — 180B · 10-22 16:18:13
```json
{
 "pc": "claude",
 "date": "20261022",
 "phase": "post",
 "session": "cowork-postmarket-1792653493",
 "pid": 7,
 "started_epoch": 1792653493.3112302,
 "started_at": "2026-10-22 07:18:13"
}
```

### `data/heartbeat_MW0601_20261022.json` — 245B · 10-22 15:46:48
```json
{
 "pid": 19924,
 "written_at": "2026-10-22T15:46:48",
 "beat_epoch": 1792651604.7260568,
 "beat_age_sec": 3.4,
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

### `data/peter_feed/_raw/2026-10-22.eod_ids.json` — 391B · 10-22 16:16:53
```json
[
 "2113052640632582604",
 "2113054283587575961",
 "2113072895777984899",
 "2113099590547427533",
 "2113129703087526028",
 "2113133674443288882",
 "2113137528081625404",
 "2113141239843570016",
 "2113141303987019948",
 "2113141396056244517",
 "2113141466705080518",
 "2113141522766115262",
 "2113146871334195651",
 "2113146954243035373",
 "2113147032760422520",
 "2113147113878192299",
 "2113147226830868898"
]
```

### `data/peter_feed/_raw/2026-10-22.jsonl` — 5.5KB · 10-22 16:16:09
```json
JSONL 19행 ⏎ 첫: {"id": "2113052640632582604", "dt": "2026-10-21T23:39:42.000Z", "text": "오늘 코스피는 외인들의 수급이 중요.\n\n매수를 해 주면 좋고\n매수를 안 하더라도 매도량이 적어야 함.\n\n오늘 만약 매도량이 많으면 조심해야 함.\n\n어제 일부 매수 들어간 분은 오늘 추가매수하지 말고 관망하고(더 떨어지거나 갭 메우러 올라갈 때 추가매수 전략)\n\n신규 매수 준비중인 분은 외인", "seen_at": "2026-10-22T08:44:31+09:00", "src": "live"} | {"id": "2113054283587575961", "dt": "2026-10-21T23:46:14.000Z", "text": "제가 말씀 드리는건 코스피 지수 기준입니다.\n\n반도체를 제외한 종목들은 좋은가격 오면 사도 되는 장이라 판단됩니다.", "seen_at": "2026-10-22T08:47:02+09:00", "src": "live"} | {"id": "2113072895777984899", "dt": "2026-10-22T01:00:12.000Z", "text": "875 895 싸움", "seen_at": "2026-10-22T10:00:20+09:00", "src": "live"} ⏎ 끝: {"id": "2113147113878192299", "dt": "2026-10-22T05:55:06.000Z", "text": "", "seen_at": "2026-10-22T14:56:21+09:00", "kind": "empty", "src": "live"} | {"id": "2113166370733170744", "dt": "2026-10-22T07:11:38.000Z", "text": "[피터리 - 2026년 10월 22일 국내 주식시장 마감 브리핑]\n\n기준: 2026년 10월 22일 목요일 / 한국 정규장 마감\n\n① 한눈에 보는 결론\n\n오늘 코스피는 **5,533.77, -201.89포인트, -3.52%**로 마감했다. 코스닥은 **764.10, -28.66포인트, -3.62%**로 마감했다.\n\n어제 코스피가 3.29%, 코스닥이 1.38%", "seen_at": "2026-10-22T16:16:09+09:00", "src": "live"} | {"id": "2113162083177304296", "dt": "2026-10-22T06:54:35.000Z", "text": "[피터리 - 2026년 10월 22일 코스피·코스닥 ±10% 급등락 브리핑]\n\n기준: 2026년 10월 22일 목요일 정규장 종가 / ETF·ETN 제외\n\n① 오늘 급등락 시장의 핵심\n\n오늘 국내 증시는 전날의 반등을 다시 반납하는 급락장이었다.\n\n코스피는 약 3.6%, 코스닥은 약 3%대 하락하면서 시장 전반에 매도 압력이", "seen_at": "2026-10-22T16:16:09+09:00", "src": "live"}
```

### `logs/probe_9842_20261022_142216.json` — 572.3KB · 10-22 14:22:20
```json
{ ⏎  "call_day": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>" ⏎  }, ⏎  "put_day": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>" ⏎  }, ⏎  "call_period": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>" ⏎  }, ⏎  "put_period": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>" ⏎  }, ⏎  "call_day_next": { ⏎   "ok": true, ⏎   "msg": "71102 조회가 계속됩니다.(stock.svrnew.9841)", ⏎   "rows": "<list 400건>" ⏎  }, ⏎  "fut_day": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 2건>" ⏎  }, ⏎  "call_day_m3": { ⏎   "ok": false, ⏎   "msg": "status=-1 입력값을 확인해주세요. near_far_gb[3] (stock.svrnew.9841)", ⏎   "rows": null ⏎  }, ⏎  "call_day_m4": { ⏎   "ok": false, ⏎   "msg": "status=-1 입력값을 확인해주세요. near_far_gb[4] (stock.svrnew.9841)", ⏎   "rows": null ⏎  } ⏎ }
```

### `logs/probe_9842_20261022_142817.json` — 619.5KB · 10-22 14:28:21
```json
{ ⏎  "call_day": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>", ⏎   "pages": 1 ⏎  }, ⏎  "put_day": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>", ⏎   "pages": 1 ⏎  }, ⏎  "call_period": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>", ⏎   "pages": 1 ⏎  }, ⏎  "put_period": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 343건>", ⏎   "pages": 1 ⏎  }, ⏎  "call_day_next": { ⏎   "ok": true, ⏎   "msg": "71102 조회가 계속됩니다.(stock.svrnew.9841)", ⏎   "rows": "<list 567건>", ⏎   "pages": 2 ⏎  }, ⏎  "fut_day": { ⏎   "ok": true, ⏎   "msg": "71101 조회가 완료되었습니다.(stock.svrnew.9841)", ⏎   "rows": "<list 2건>", ⏎   "pages": 1 ⏎  }, ⏎  "call_day_m3": { ⏎   "ok": false, ⏎   "msg": "status=-1 입력값을 확인해주세요. near_far_gb[3] (stock.svrnew.9841)", ⏎   "rows": null ⏎  }, ⏎  "call_day_m4": { ⏎   "ok": false, ⏎   "msg": "SKIP 요청 상한 8 도달", ⏎   "rows": null ⏎  } ⏎ }
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-22 15:53:39**

| 키 | 값 | 수집 대상일(2026-10-22)과 일치 |
|---|---|---|
| `date` | 2026-10-22 | 예 |
| `p8_last_success_date` | 2026-10-22 | 예 |
| `eod_retrain_ok_date` | 2026-10-22 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-22 08:55:05 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-21) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-22 08:55:05 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-21) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261022_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 19924: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 19924 | 08:40:45 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

### 9-e. 피터2 단독 수집 추적 (698차 — MW0602 수집기 중지 효과)

- 최종: **IN_PROGRESS** — 진행 중 — 평가 창 5거래일 미도달(중간값은 참고만) (평가 3/5거래일)
- 오늘: 트윗 n=19 · p90=274.6초 · 외부소진 중앙 0.0(기준선 27.0) · 429(정규장) 0건 · ① PASS · ② PASS
- 전체 표: `python tools/peter2_live/sole_collect_tracker.py --upto 2026-10-22`

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 243개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261022-점검리포트.md` | 27.6KB | 10-22 12:37 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_intra.md` | 83.8KB | 10-22 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_pre.md` | 65.5KB | 10-22 08:59 |
| `docs/정기점검/매일점검/MW0601-20261021-점검리포트.md` | 70.3KB | 10-21 17:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_post.md` | 103.3KB | 10-21 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_intra.md` | 85.3KB | 10-21 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_pre.md` | 63.6KB | 10-21 08:59 |
| `docs/정기점검/매일점검/MW0601-20261020-점검리포트.md` | 70.2KB | 10-20 17:57 |

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

1. 차단 게이트 `PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL` = False 인데 **근거 미기록** — 의도한 예외인지 확인하고 DECISION_LOG에 남길 것
2. **엔진 진입 0건 / 계좌 진입 9건**(그중 외부표식 0건 · 피터2 0건 · 판별불가 9건 · 별도 가상 장부 6건) — 차단 73건. 최다 차단 사유: `등급X — 미통과 항목: 2_confidence` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
3. 포지션 9건 중 최종청산이 하드스톱·손절 계열 **7건(78%)** — 손절 준수율 확인 필요 (레그 15행)
4. 다레그 포지션 **6건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
5. 메인 스레드 정지 5초 초과 **1건** (최대 6766ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20261022_SYSTEM.log`: **ConstOut** 6건(표본)
7. `logs/20261022_SIGNAL.log`: **WeightCollapse** 8건(표본)
8. `logs/20261022_SIGNAL.log`: **ConstOut** 8건(표본)
9. `logs/20261022_LEARNING.log`: **축퇴** 8건(표본)
10. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
11. 미커밋 변경 46건 (실질 6건 · 코드 0건 · EOL 파생 0건)
12. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261022*.log` (Windows) / `grep 강제청산 logs/*20261022*.log`*