# 미륵이 증거 다이제스트 — 2026-10-23 / POST

- 생성 2026-10-23 16:21:19 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-011psp7mn7qfkhh7ad78dven/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261023` · `2026-10-23` · `261023` · `1023`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **44개** 파일 · 44개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-intra-mireuk-intra-{DATE}032723.json` | 1 | `data/dailycheck_markers/claude-20261023-intra-mireuk-intra-20261023032723.json` | 180B | 10-23 12:27 |
| `claude-{DATE}-post-coworksession_{DATE}_post.json` | 1 | `data/dailycheck_markers/claude-20261023-post-coworksession_20261023_post.json` | 179B | 10-23 16:20 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261023.txt` | 28B | 10-23 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261023.txt` | 28B | 10-23 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261023.txt` | 233B | 10-23 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261023.log` | 1.5KB | 10-23 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261023.log` | 708B | 10-23 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261023.json` | 244B | 10-23 15:46 |
| `launcher_{DATE}_043744_29897.log` | 1 | `logs/Mireuk_batch/launcher_20261023_043744_29897.log` | 41.9KB | 10-23 06:23 |
| `launcher_{DATE}_062335_17869.log` | 1 | `logs/Mireuk_batch/launcher_20261023_062335_17869.log` | 18.6KB | 10-23 06:25 |
| `launcher_{DATE}_062623_18417.log` | 1 | `logs/Mireuk_batch/launcher_20261023_062623_18417.log` | 18.6KB | 10-23 06:27 |
| `launcher_{DATE}_084001_11833.log` | 1 | `logs/Mireuk_batch/launcher_20261023_084001_11833.log` | 2.7MB | 10-23 15:47 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261023.log` | 109B | 10-23 08:44 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261023.log` | 2.3KB | 10-23 15:46 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261023.log` | 45.9KB | 10-23 16:09 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261023.log` | 491B | 10-23 16:15 |
| `position_state.json.gen_{DATE}_141010` | 1 | `data/position_state.json.gen_20261023_141010` | 1.5KB | 10-23 14:10 |
| `position_state.json.gen_{DATE}_142640` | 1 | `data/position_state.json.gen_20261023_142640` | 1.6KB | 10-23 14:26 |
| `position_state.json.gen_{DATE}_143126` | 1 | `data/position_state.json.gen_20261023_143126` | 1.7KB | 10-23 14:29 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261023.log` | 35.6KB | 10-23 16:20 |
| `retrain_intraday_20260625_{DATE}59.log` | 1 | `logs/retrain_intraday_20260625_102359.log` ⚠ 다른 날짜(20260625) 파일 — 날짜 토큰 오매칭 | 4.6KB | 06-25 10:24 |
| `retrain_intraday_{DATE}_114600.log` | 1 | `logs/retrain_intraday_20261023_114600.log` | 3.2KB | 10-23 11:46 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261023.log` | 116.7KB | 10-23 16:04 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261023.txt` | 43B | 10-23 15:47 |
| `strategy_report_{DATE}_154028.txt` | 1 | `data/daily_reports/strategy_report_20261023_154028.txt` | 2.4KB | 10-23 15:40 |
| `{DATE}.eod_ids.json` | 1 | `data/peter_feed/_raw/2026-10-23.eod_ids.json` | 437B | 10-23 16:10 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-23.jsonl` | 4.7KB | 10-23 15:16 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20261023_BACKFILL.log` | 0B | 10-23 05:22 |
| `{DATE}_DATA.log` | 1 | `logs/20261023_DATA.log` | 439.5KB | 10-23 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261023_DEBUG.log` | 264.5KB | 10-23 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261023_HEALTH.log` | 42.8KB | 10-23 15:01 |
| `{DATE}_HOGA.log` | 1 | `logs/20261023_HOGA.log` | 61.3MB | 10-23 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261023_LEARNING.log` | 483.3KB | 10-23 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261023_MICRO.log` | 1.1MB | 10-23 15:37 |
| `{DATE}_OPTION_BACKFILL.log` | 1 | `logs/20261023_OPTION_BACKFILL.log` | 652B | 10-23 16:21 |
| `{DATE}_OPTION_HTS_SYNC.log` | 1 | `logs/20261023_OPTION_HTS_SYNC.log` | 2.3KB | 10-23 09:42 |
| `{DATE}_PROBE.log` | 1 | `logs/20261023_PROBE.log` | 95.0KB | 10-23 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261023_REGULAR_COLLECT.log` | 9.0KB | 10-23 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261023_SIGNAL.log` | 536.5KB | 10-23 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261023_SYSTEM.log` | 1.2MB | 10-23 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261023_TRADE.log` | 45.0KB | 10-23 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261023_WARN.log` | 909.1KB | 10-23 15:46 |
| `{DATE}_main.json` | 1 | `data/alert_mail/2026-10-23_main.json` | 263B | 10-23 12:28 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-23_tr.draft.txt` | 0B | 10-23 15:40 |

_다른 날짜 파일 1개는 짧은 날짜 토큰(`1023`)이 시각 숫자와 우연히 겹친 것이라 이후 절에서 제외했다: `retrain_intraday_20260625_102359.log`_

## 2. 코드·커밋 상태

- HEAD `bf99769e` · 브랜치 `v9-dev` · 미커밋 27건 · 실질 변경 12건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 12 · 미추적 15 · 삭제 6 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261023.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260923.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260923.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260923.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260923.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260923.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260923.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 7.0초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261023.md
 M docs/미륵이고도화3/신동2/학습/lessons.json
 M docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md
 M docs/미륵이고도화3/신동2/학습/추이_MW0601.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260923.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260923.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260923.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260923.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260923.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260923.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261026.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261023.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261023.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261023.md
?? docs/신동거래/일일/신동_일일_MW0601_20261023.md
?? docs/신동거래/일일/신동_일일_MW0601_20261023.svg
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261023.json
?? docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261023.md
?? docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261023.json
?? docs/정기점검/금요일점검/MW0601/featureset_health_report_20261023.md
?? docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261023.json
?? docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261023.md
?? docs/정기점검/매일점검/MW0601-20261023-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20261023_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261023_pre.md
```

**당일(2026-10-23) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
bf99769e [MW0601] 710차 기록: DECISION_LOG — [9842] 수집 흐름 점검 · 사다리 API 폴백 · 장후 스냅샷 대사 오탐
bd61aa66 [MW0601] 710차: [9842] 사다리 API 수집본 폴백 · 장후 스냅샷 대사 오탐(rc=1) 해소
0a880ff9 [MW0601] 707차 후속2: dev 실전 자본 3층 켜짐 기록 — 이식 메모 갱신 (dev a815d2dd, 사용자 지시)
54144e55 [MW0601] 707차 후속: 실전 자본 3층 dev 배포 기록 — 이식 메모 (dev 22fdb663, 동작 변경 3종 기본 꺼짐 · 모니터만 켜짐)
be41c470 [MW0601] 708차: 신동 실거래 출처 분리 · 철회 섀도 계측
6d483785 [MW0601] 707차: 실전 자본 3층(관측·정책·통제) — 신동 수량 증거금 연동 · 위험자본 min(정책, 예탁금) · PG 수량 비례 · 주문/체결 탭 모니터
5360d398 [MW0601] 706차: CREON 실거래 런처 실패 경로 — 08:35 트리거 봉쇄 해소 · 불일치 세션 정리 · starter 레지스트리 계측
```

**최근 커밋 12건**
```
bf99769e [MW0601] 710차 기록: DECISION_LOG — [9842] 수집 흐름 점검 · 사다리 API 폴백 · 장후 스냅샷 대사 오탐
bd61aa66 [MW0601] 710차: [9842] 사다리 API 수집본 폴백 · 장후 스냅샷 대사 오탐(rc=1) 해소
0a880ff9 [MW0601] 707차 후속2: dev 실전 자본 3층 켜짐 기록 — 이식 메모 갱신 (dev a815d2dd, 사용자 지시)
54144e55 [MW0601] 707차 후속: 실전 자본 3층 dev 배포 기록 — 이식 메모 (dev 22fdb663, 동작 변경 3종 기본 꺼짐 · 모니터만 켜짐)
be41c470 [MW0601] 708차: 신동 실거래 출처 분리 · 철회 섀도 계측
6d483785 [MW0601] 707차: 실전 자본 3층(관측·정책·통제) — 신동 수량 증거금 연동 · 위험자본 min(정책, 예탁금) · PG 수량 비례 · 주문/체결 탭 모니터
5360d398 [MW0601] 706차: CREON 실거래 런처 실패 경로 — 08:35 트리거 봉쇄 해소 · 불일치 세션 정리 · starter 레지스트리 계측
6dae99c8 [MW0601] 705차 후속5: 점검 문서 일괄 커밋 — 10-19~10-22 점검리포트·증거 · 신동2·피터2·신동 일일 · F-1 설정 · 수익률향상 누적대장
8b4d72ca [MW0601] 705차 후속5: 청산 라벨 외부 주체 분기 — 신동1차 EXT_TARGET1 · 신동최종 EXT_TARGET2 · 피터2미러 EXT_INSTRUCTED
c293b355 [MW0601] 705차 후속4: 신동 실거래 대사 dev 배포 기록 — 이식 메모 (dev b8c7b864, A·C 이식 · B 해당 없음)
ac1958d6 [MW0601] 705차 후속4: 장후 자동조치 — F-27(전제 반박 → 라벨 자기대사 신동 1차익절 버킷) · G-1 · G-2
e7076f5b [MW0601] 705차 후속3: 신동 실거래 대사 — dev(MW0602) 집행 기록 형식(shindong_exec.json 신호별 상태) 읽기 지원
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `3` | `3` | 일치 | [2026-09-02 519차] 모의 한정 예외 해제 — 9999→3 복원(절대원칙 ② 문구와 일치). ⚠ 값 복원만으로 실전 전환 기준 ⑤가 충족되지 않는다 … |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `3` | `3` | 일치 | 431차 10→3 인하 → [2026-10-13 사용자 결정 56cc917] CREON 실거래 전환으로 3→1 → [2026-10-23 사용자 결정 707차] … |
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

### 차단 게이트 전수 인벤토리 — 47개 중 **10개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FORCE_FLAT_GUARD_ORDER_ENABLED` | False | 기능토글 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FREEZE_SENTINEL_KILL_ENABLED` | False | 기능토글 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `PROFIT_GUARD_BLOCK_VIRTUAL_PRINCIPAL` | False | 기록됨 |
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
| `STRIKE_INVESTOR_FLOW_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `WEEKLY_OPTION_FLOW_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20261023_HOGA.log` 61.3MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261023.txt`** — 28B · 10-23 15:40:28
```
2026-10-23T15:40:28.416127
```

**`data/daily_close_started_20261023.txt`** — 28B · 10-23 15:40:09
```
2026-10-23T15:40:09.689487
```

**`data/daily_reports/strategy_report_20261023_154028.txt`** — 2.4KB · 10-23 15:40:28
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-23 15:40
========================================================
  버전    : v1.0  (104일차)
  판정    : UNDERPERFORM
  Live(20일): Sh=-0.89  MDD(자본대비)=4.8%
  당일      : WR=44.4%  PF=0.42
  롤링20일: 누적 -965853원  Sh=-0.89  MDD(자본대비)=4.8%  MDD(peak대비)=168.4%
  당일손익 : broker(gross) -2,377,405원  수수료 43,339원  net -2,377,339원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : WATCHLIST (3.16)
  PSI     : 0.005 (CLEAR)
  PSI/feat: cvd_delta=0.005  ofi_pressure=0.000  vwap_position=0.055
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -75,966원  승률 65.0%  합계 -1,519,317원
  등급별 순EV(30일): A=-8,248원(54건,승54%)  P=-79,556원(20건,승20%)  S=+27,909원(35건,승66%)
  호라이즌별 순EV(30일): 1m=+2,297원(7건)  3m=+14,383원(29건)  5m=-48,810원(18건)  ?=-11,169원(55건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 41분  5일평균 41분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 37.7pt(5일평균 38.7pt)  1분평균변동 1.10pt(5일평균 0.88pt)
--------------------------------------------------------
  진입 퍼널(2026-10-23, 총 370분):
    FLAT 219 → conf미달 102 → CoherenceGate 8 → 게이트차단 30 → 후보 11 → 진입 4
    게이트별: 포지션보유중(평가생략)=8  콜드스타트/기타(DataAnomalyGate)=6  모드필터=5  체크리스트항목미달=4  쿨다운=3  Degraded신뢰도=3  콜드스타트/기타(조건부구간)=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 7건
      └ 상세: Degraded신뢰도=4  JointGateBlock=3
      └ JointGateBlock 3건 (무정보폴백 3건 = 100.0%) [표본 17건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261023.txt`** — 233B · 10-23 15:53:35
```
completed: 2026-10-23 15:53:35
rows: 23155
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 27.2
t_retrain_s: 183.6
t_total_s: 211.3
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/shutdown_normal_20261023.txt`** — 43B · 10-23 15:47:15
```
auto_shutdown
2026-10-23T15:47:15.441635
```

_다이제스트 대상 8/26개 (중요도순). 제외: `20261023_MICRO.log`, `20261023_DATA.log`, `20261023_PROBE.log`, `launcher_20261023_084001_11833.log`, `launcher_20261023_043744_29897.log`, `launcher_20261023_062335_17869.log`, `launcher_20261023_062623_18417.log`, `20261023_DEBUG.log`_

### `logs/20261023_TRADE.log` — 45.0KB · 323행 · 최종 15:40:23

- 형식 평문 · 시각 인식 323행 · WARNING=31, INFO=292

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:35 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-23 04:38:41 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-23 06:17:07 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-23 06:17:11 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-23 06:24:20 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-10-23 14:45:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=31,622,595) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 1계약 (최소=1) [ConfShadow: 1.0→3계약]
2026-10-23 14:45:00 [INFO] TRADE: [모드필터 차단] LONG->LONG 1계약 C급 (모드=hybrid, 허용=['A', 'B'])
2026-10-23 14:49:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=31,622,595) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-10-23 14:49:00 [INFO] TRADE: [JointGateBlock 차단] LONG 2계약 A급 (meta=0.50<fallback> tox=0.70 joint=0.350)
2026-10-23 15:40:23 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 22 | 09:03:11 | 14:10:10 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=3 entry=834.08 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |
| `ShindongExec` | 9 | 09:03:10 | 14:10:10 | 주문가능수량 미측정 — 계획 수량 3계약 그대로 주문(최종 판정은 브로커) |

**채널** — `TRADE`×323

**컴포넌트 상위 15** — `Chejan`×86, `Position`×57, `ShindongExec`×24, `PositionFallback`×22, `주문요청`×20, `Sizer`×20, `체결청산-부분`×13, `체결진입`×11, `체결진입보정`×11, `Virtual`×11, `청산 완료`×9, `ProfitGuard`×7, `TickStop-S0C`×7, `ExitStage`×6, `자동진입 차단`×6

### `logs/20261023_WARN.log` — 909.1KB · 4173행 · 최종 15:46:18

- 형식 평문 · 시각 인식 4166행 · CRITICAL=39, WARNING=4127, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-23 04:38:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-23 04:38:44 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr25)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-23 04:38:44 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr25)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-23 04:38:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=783343908
  …
오늘 PnL: -2377339원
════════════════════════════════════════════════════
2026-10-23 15:46:17 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2231 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=7063 band=WARN since_pipe_s=2236.8
2026-10-23 15:46:17 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20261023.log
2026-10-23 15:46:18 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 130.5ms | size=1967x1935 candles=411 grid=48.3 spans=0.2 candles=17.1 dir=1.4 regime=16.3 markers=35.1 axes=0.9 cross=0.0 | slow_cnt=2629 total_cnt=2963 overlay_cnt=42379
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 39 | 09:14:00 | 14:07:00 | level=CRITICAL degraded=ON | latency=315ms | quality=1.00 | cache_age=153s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-10-23 09:14:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=315ms | quality=1.00 | cache_age=153s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
2026-10-23 09:15:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=405ms | quality=1.00 | cache_age=30s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
```

</details>

**WARNING — 태그 43종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2629 | 08:56:35 | 15:46:18 | paintEvent slow 32.2ms | size=1484x950 candles=12 grid=10.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.4 cross=0.0 | slow_cnt=1 total_cnt=106 overlay_cnt=708 |
| `LiveDBG` | 506 | 04:38:44 | 15:46:17 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ShindongExec` | 196 | 09:04:10 | 14:31:10 | 정규 재생 대조 60초 미갱신(옵션흐름 수집 미성공) — 직전 재생 결과(DB 1건)로 보유 포지션 대조 |
| `Health` | 182 | 09:00:01 | 15:00:00 | level=WARNING degraded=OFF | latency=1638ms | quality=1.00 | cache_age=50s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1 |
| `ChejanFlow` | 86 | 09:03:11 | 14:31:26 | account='783343908' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=3 | gubun='0' | order_no='90' | pending='ENTRY:SHORT qty=3 filled=0 order_no=? reason=진입 req_at=09:03:10.877' | position… |
| `ChejanMatch` | 86 | 09:03:11 | 14:31:26 | order_no='90' | pending='ENTRY:SHORT qty=3 filled=0 order_no=90 reason=진입 req_at=09:03:10.877' | pending_matched=True |
| `OptionFlowChart` | 82 | 04:38:54 | 15:33:10 | 그리기 78.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 774x1001 |
| `CybosMarginQty` | 72 | 08:45:40 | 15:31:39 | 조회 실패 ret=0 status=-1 msg=11298 시장가/신고대량/최우선/최유리지정가 주문은 단가를 입력하지 않습니다. (ordsvr58)(ord.fo.dpmyinqr.selanwordpsblqty) account=783343908 code=A056B |
| `PendingOrder` | 42 | 09:03:10 | 14:31:26 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 3, 'price_hint': 834.22, 'reason': '진입', 'hint_source': '', 'atr': 2.9543, 'grade': 'S', 'stage': None, 'order_no': '', 'filled_qt… |
| `EntryFillFlow` | 22 | 09:03:11 | 14:10:10 | actual_side='SHORT' | after='SHORT 3계약 @ 834.08' | applied_side='SHORT' | before='SHORT 3계약 @ 834.22' | fill_no='' | fill_price=834.08 | fill_qty=2 | order_no='90' | pending='ENTRY:SHORT qty=3 filled=2 order_no=90 reason=진입 req_at=09:03:10… |
| `ExitFillFlow` | 22 | 09:53:19 | 14:31:26 | after='SHORT 2계약 @ 834.07' | before='SHORT 3계약 @ 834.07' | fill_price=844.7 | fill_qty=1 | mode='partial_or_remaining' | pending='EXIT_FULL:SHORT qty=3 filled=1 order_no=377 reason=하드스톱(틱) req_at=09:53:19.035' | reason='하드스톱(틱)' |
| `HealthPolicy` | 18 | 09:01:00 | 14:21:00 | Degraded 선제차단: streak=1.00+1.00 ≥ 2 (latency=1638ms quality=1.00 cache=0s exc10m=2) | cause=S6(761ms) |

**채널** — `SYSTEM`×3945, `HEALTH`×221

**컴포넌트 상위 15** — `ChartDBG`×2629, `LiveDBG`×506, `Health`×221, `ShindongExec`×196, `ChejanFlow`×86, `ChejanMatch`×86, `OptionFlowChart`×82, `CybosMarginQty`×72, `PendingOrder`×42, `EntryFillFlow`×22, `ExitFillFlow`×22, `HealthPolicy`×18, `ExitCooldown`×18, `ScalerRefresh`×16, `EntryAttempt`×13

### `logs/20261023_SYSTEM.log` — 1.2MB · 8152행 · 최종 15:47:15

- 형식 평문 · 시각 인식 8111행 · INFO=8107, PLAIN=45

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:21 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=8984 | 행감지=30s all_threads=True
2026-10-23 04:38:21 [INFO] SYSTEM: [DBInit] 합계 0.46s | predictions=0.05s trades=0.23s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-23 04:38:21 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-23 04:38:21 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-23 04:38:21 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-23 15:46:10 [INFO] SYSTEM: [RawFill] 2026-10-23 raw_candles 창 안 보충 0봉(bar_recovered=2) · 차트 보정 1봉(bar_recovered=3) — 보충 — / 보정 08:45
2026-10-23 15:46:10 [INFO] SYSTEM: [BarGap] 당일 확정(2026-10-23) — raw_candles 384봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 0봉
2026-10-23 15:47:15 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-23 15:47:15 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-23 15:47:15 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×8107

**컴포넌트 상위 15** — `CybosRT-TICK`×1607, `CybosInvestorRaw`×1576, `PumpGuard`×769, `BAR-CLOSE`×410, `CVD-ANCHOR`×410, `CybosRT-ROLLOVER`×409, `TickUI`×408, `S6Detail`×370, `PipePerf`×370, `ShindongExec`×196, `CybosEvent`×172, `System`×144, `BalanceUI`×137, `MicroRegime`×104, `CybosDailyPnl`×94

### `logs/20261023_SIGNAL.log` — 536.5KB · 4780행 · 최종 15:40:23

- 형식 평문 · 시각 인식 4780행 · WARNING=1633, INFO=3147

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-10-23 15:10:02 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-23 15:40:23 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-23 15:40:23 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 370분 중 섀도만 활성 UP 80분(21.6%) / DN 11분(3.0%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-23 15:40:23 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-23 age=32m extreme=786 refresh=32 grade_x=103 cb3=0
2026-10-23 15:40:23 [INFO] SIGNAL: [ModelHealth] date=2026-10-23 앙상블유효가동률=71.6% | 파이프라인 370분 | ConstOut 13회/22분 {"3m": {"events": 12, "minutes": 20}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 83분 | 장중재학습 1회 | CB③ ready 169분/370분 (46%) (리셋 1회, 표본손실 30건)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1104 | 09:00:02 | 15:07:01 | 1m 'macro_vix' scale=0.0211 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 156 | 09:00:00 | 15:06:00 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 126 | 09:00:00 | 15:09:00 | ts=08:59 horizon=1m age=1m max_z=-8.68(institution_futures_net) extreme=2 adj=2 |
| `Checklist` | 108 | 09:14:00 | 15:08:00 | CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=+0.189 need <0 (SHORT) bull_exh=0.00 |
| `WeightCollapse` | 84 | 09:07:00 | 15:09:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 42 | 08:45:10 | 08:55:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0235) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 13 | 09:35:00 | 15:09:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |

**채널** — `SIGNAL`×4780

**컴포넌트 상위 15** — `ScalerFloor`×1122, `SIGNAL`×740, `Ensemble`×375, `FQAdj`×369, `ZeroDiag`×336, `MetaGate`×305, `Model`×192, `Checklist`×163, `ATR-Horizon`×139, `ScalerMonitor`×127, `InstabilityGate`×108, `MicroRegime`×104, `WeightCollapse`×84, `차단`×82, `ScalerRefresh`×79

### `logs/20261023_LEARNING.log` — 483.3KB · 3906행 · 최종 15:40:23

- 형식 평문 · 시각 인식 3896행 · WARNING=699, INFO=3197, PLAIN=10

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:23 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.2001 < conf_floor=0.3300 (span=0.00021 auc=0.548 out_max=0.2001, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.498 out_max=0.2477 (기준 auc<0.53 and span<0.020, 기저율=0.2476 n=105) → 보정 미적용, raw 통과
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00007 auc=0.476 out_max=0.4000 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=80) → 보정 미적용, raw 통과
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00058 auc=0.453 out_max=0.2877 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
  …
2026-10-23 15:40:23 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-23 15:40:23 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-23 15:40:23 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-23 15:40:23 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-23 15:40:23 [INFO] LEARNING: [Sigma] EOD sigma_20=0.08987% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 219 | 04:38:26 | 14:55:00 | 축퇴 감지 — span=0.00007 auc=0.476 out_max=0.4000 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 210 | 04:38:26 | 14:57:00 | 하한 도달불가 — out_max=0.2001 < conf_floor=0.3300 (span=0.00021 auc=0.548 out_max=0.2001, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 110 | 04:38:26 | 08:40:59 | 축퇴 감지 — span=0.00058 auc=0.453 out_max=0.2877 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 100 | 04:38:26 | 08:40:59 | 축퇴 감지 — span=0.00027 auc=0.521 out_max=0.3766 (기준 auc<0.53 and span<0.020, 기저율=0.3765 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:10m` | 30 | 04:38:27 | 08:41:00 | 하한 도달불가 — out_max=0.2508 < conf_floor=0.3300 (span=0.00127 auc=0.715 out_max=0.2508, 기저율=0.2500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 20 | 04:38:27 | 08:40:59 | 하한 도달불가 — out_max=0.3233 < conf_floor=0.3300 (span=0.00294 auc=0.582 out_max=0.3233, 기저율=0.3217 n=115) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 9 | 04:38:35 | 11:22:00 | 복원한 보정기가 축퇴 상태 — span=0.00797 auc=0.530 out_max=0.2787 (n=5112) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `DriftAdjuster` | 1 | 15:40:11 | 15:40:11 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 24일) |

**채널** — `LEARNING`×3896

**컴포넌트 상위 15** — `LEARNING`×1219, `Calibration:30m`×430, `Calibration:1m`×412, `SGD`×370, `sigma`×357, `Calibration:3m`×210, `Bias⚠`×200, `Calibration:5m`×190, `Bias`×146, `MetaConf`×77, `OnlineLearner`×57, `Calibration:10m`×55, `ScalerWarmup`×37, `Calibration:15m`×30, `BiasReset`×27

### `logs/20261023_HEALTH.log` — 42.8KB · 239행 · 최종 15:01:00

- 형식 평문 · 시각 인식 239행 · CRITICAL=39, WARNING=182, INFO=18

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1638ms | quality=1.00 | cache_age=50s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1
2026-10-23 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=584ms | quality=1.00 | cache_age=109s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1
2026-10-23 09:09:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=300ms | quality=1.00 | cache_age=36s | exceptions_10m=7 | exc_tags=[ShindongExec]×5 [Peter2Offset]×1 [Peter2]×1
2026-10-23 09:10:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=430ms | quality=1.00 | cache_age=97s | exceptions_10m=8 | exc_tags=[ShindongExec]×6 [Peter2Offset]×1 [Peter2]×1
2026-10-23 09:11:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=311ms | quality=1.00 | cache_age=157s | exceptions_10m=9 | exc_tags=[ShindongExec]×7 [Peter2Offset]×1 [Peter2]×1
  …
2026-10-23 14:36:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=375ms | quality=1.00 | cache_age=27s | exceptions_10m=7 | exc_tags=[ShindongExec]×6 [ExitCooldown]×1
2026-10-23 14:37:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=314ms | quality=1.00 | cache_age=87s | exceptions_10m=6 | exc_tags=[ShindongExec]×5 [ExitCooldown]×1
2026-10-23 14:38:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=312ms | quality=1.00 | cache_age=147s | exceptions_10m=5 | exc_tags=[ShindongExec]×4 [ExitCooldown]×1
2026-10-23 15:00:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=355ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-10-23 15:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=279ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 39 | 09:14:00 | 14:07:00 | level=CRITICAL degraded=ON | latency=315ms | quality=1.00 | cache_age=153s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1 |

<details><summary>CRITICAL/Health 원문 2건</summary>

```
2026-10-23 09:14:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=315ms | quality=1.00 | cache_age=153s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
2026-10-23 09:15:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=405ms | quality=1.00 | cache_age=30s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 182 | 09:00:01 | 15:00:00 | level=WARNING degraded=OFF | latency=1638ms | quality=1.00 | cache_age=50s | exceptions_10m=2 | exc_tags=[Peter2Offset]×1 [Peter2]×1 |

**채널** — `HEALTH`×239

**컴포넌트 상위 15** — `Health`×238, `HealthTrend`×1

### `logs/retrain_eod_20261023.log` — 35.6KB · 303행 · 최종 16:20:10

- 형식 평문 · 시각 인식 172행 · WARNING=17, INFO=155, PLAIN=131

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 15:50:03,450 [INFO] EOD_RETRAIN: =======================================================
2026-10-23 15:50:03,451 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-23 15:50:03,451 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-23 15:50:03,451 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-23 15:50:03,451 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
10m    성공         3902   1.2501        0.112        0.101
15m    성공         2514   1.5166        0.100        0.086
30m    성공        24439   1.4609        0.100        0.086
참고: 커버리지<q10은 이상적으로 ~0.10, 커버리지>q90은 ~0.10 근처여야 함
(실측이 크게 벗어나면 분위 추정이 편향됐다는 뜻 — GBR_PARAMS 조정 검토)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:50:38 | 15:52:27 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1497봉(81%)이 현행 학습구간 (현행 cutoff=2026-10-22 14:38:00 ≥ 홀드아웃 시작=2026-10-16 13:05:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-22 14:38 >= holdout_start=2026-10-16 13:05 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-22 … |
| `UnitMismatch` | 4 | 15:50:15 | 16:12:48 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/27313행 제외 (559차 P1'-2) — 남은 25867행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `BackfillFilter` | 2 | 15:50:15 | 16:12:51 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 16669/43982 제외 (418차 결정 1) — 남은 27313행 |
| `GuardGhost` | 2 | 15:50:51 | 15:50:51 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-10-23 11:15:00까지)인데 acc.txt=0.3778는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `RegularFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-23 | 최신 2026-10-22 · 기준 9거래일. 복구: python scripts/collect_regular_futures.py --from 20261023 --to 20261023 |
| `OptionFlowFresh` | 1 | 15:50:04 | 15:50:04 | 결손 1일 — 2026-10-13(최신봉 15:33) | 기준 8거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\<YYYYMMDD>_OPTION_BACKFILL.log |
| `RegimeFingerprint` | 1 | 15:53:35 | 15:53:35 | 백필 0행 제외 — 필터가 무효일 수 있다. 23155행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×64, `SIGNAL`×43, `EOD_RETRAIN`×39, `FEAT_REG`×6

**컴포넌트 상위 15** — `-`×130, `ScalerFloor`×36, `Retrain`×21, `EOD_RETRAIN`×15, `검증 캠페인`×11, `RF`×9, `ShadowTB`×8, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4

### `logs/retrain_intraday_20261023_114600.log` — 3.2KB · 24행 · 최종 11:46:23

- 형식 평문 · 시각 인식 24행 · WARNING=2, INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 11:46:00,394 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-23 11:46:00,394 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-23 11:46:00,394 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-23 11:46:00,394 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-23 11:46:00,394 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_da581142.json
  …
2026-10-23 11:46:23,548 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-23 11:46:23,548 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-23 11:46:23,549 [INFO] LEARNING: [Retrain] 완료 | 20.1초 | 성공=1/1 호라이즌
2026-10-23 11:46:23,549 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 23.1s 데이터=4800행
2026-10-23 11:46:23,551 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_da581142.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 11:46:13 | 11:46:13 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 16883/43993 제외 (418차 결정 1) — 남은 27110행 |
| `UnitMismatch` | 1 | 11:46:13 | 11:46:13 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/27110행 제외 (559차 P1'-2) — 남은 25664행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: WATCHLIST (Lv.1)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: -2377339원
════════════════════════════════════════════════════
2026-10-23 15:46:17 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 7063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2231 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=7063 band=WARN since_pipe_s=2236.8
2026-10-23 15:46:17 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (1/20) → logs/mainstall_traceback_20261023.log
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 4 |
| 진입 등록(`[Position] 진입`) | 12 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 0 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 4 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 8 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 11  ※ 두 형식 중복 3건 접음 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 9 |
| 차단(`[차단]`) | 82 |
| 사이저 호출(`[Sizer]`) | 20 |

> 🔴 **엔진 진입 0건인데 계좌 체결 11건**(외부표식 0 · 피터2 0 · 판별불가 8) — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.
>
> 별도로 **가상 장부 진입 4건**이 `[Position] 진입` 에 섞여 있다 — 실주문이 없으므로 계좌 체결·손익과 무관하다(아래 「가상 장부」 표).

### 포지션 9건 · 승 4 (44%) · 합계 -46.71pt (-2,377,336원)  ※ 레그 22행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:03:11 | 추정 | SHORT | 3 | — | 3 | -32.03 | -1,605,754 | 하드스톱(틱) |
| 09:59:11 | 추정 | LONG | 3 | — | 3 | -5.25 | -266,811 | 하드스톱(틱) |
| 10:05:10 | 추정 | LONG | 3 | — | 2 | -13.16 | -662,824 | 하드스톱(틱) |
| 10:16:10 (추정귀속) | 추정 | SHORT | 3 | — | 2 | -16.06 | -807,790 | 하드스톱(틱) |
| 10:36:10 | 추정 | LONG | 3 | — | 3 | +17.83 | +886,202 | 수동 전량청산 |
| 11:49:10 | 추정 | SHORT | 3 | — | 2 | -15.16 | -762,791 | 하드스톱(틱) |
| 12:34:10 | 추정 | LONG | 3 | — | 2 | +7.48 | +369,162 | 수동 전량청산 |
| 13:20:10 | 추정 | LONG | 3 | — | 3 | +5.35 | +263,144 | 하드스톱(틱) |
| 14:10:10 | 추정 | SHORT | 3 | — | 2 | +4.29 | +210,126 | 하드스톱(틱) |

**출처별 소계** — 추정 9건 -2,377,336원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「피터2」는 `[Peter2] 진입`이 동반된 보조 로직 자리로 역시 엔진 성적이 아니다. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**가상 장부 4건(청산 4 · 합계 -449,353원) — 실주문 없음, 엔진·계좌 손익 아님**

| 진입 | 주체 | 방향 | 수량 | hz | 가상 pt | 가상 net(원) | 가상 청산사유 |
|---|---|---|---|---|---|---|---|
| 10:08:00 | 미륵 | LONG | 1 | 3m | -5.05 | -254,254 | 가상:하드스톱 |
| 11:08:00 | 미륵 | SHORT | 2 | 3m | -3.81 | -191,876 | 가상:하드스톱 |
| 11:40:00 | 미륵 | LONG | 2 | 3m | +0.00 | -1,601 | 가상:하드스톱 |
| 14:19:00 | 미륵 | LONG | 2 | 3m | +0.00 | -1,622 | 가상:하드스톱 |

> ⚠ 이 표는 `[Virtual] … 가상진입`/`가상청산` 로그로 조립한 **가상 장부**다. 같은 초에 `[Position] 진입` 이 찍혀 진입 건수에는 잡히지만 체결이 없다 — 3원 대사(로그·DB·브로커)에서 로그 쪽이 더 많아 보이면 먼저 이 표를 뺄 것.

> ⚠ **(추정귀속) 1건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 22행** (부분청산 13 · 전량청산 9)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:53:19 | 부분 | 1 | -10.63 | -532,918 | 하드스톱(틱) |
| 09:53:19 | 부분 | 1 | -10.69 | -535,918 | 하드스톱(틱) |
| 09:53:19 | 전량 | 1 | -10.71 | -536,918 | 하드스톱(틱) |
| 10:00:35 | 부분 | 1 | -1.73 | -87,937 | 하드스톱(틱) |
| 10:00:35 | 부분 | 1 | -1.75 | -88,937 | 하드스톱(틱) |
| 10:00:35 | 전량 | 1 | -1.77 | -89,937 | 하드스톱(틱) |
| 10:12:15 | 부분 | 2 | -4.38 | -441,216 | 하드스톱(틱) |
| 10:12:15 | 전량 | 1 | -4.40 | -221,608 | 하드스톱(틱) |
| 10:26:37 | 부분 | 2 | -5.36 | -539,193 | 하드스톱(틱) |
| 10:26:37 | 전량 | 1 | -5.34 | -268,597 | 하드스톱(틱) |
| 10:40:32 | 부분 | 1 | +1.47 | +71,734 | 신동1차 |
| 10:42:26 | 부분 | 1 | +8.19 | +407,734 | 수동 전량청산 |
| 10:42:26 | 전량 | 1 | +8.17 | +406,734 | 수동 전량청산 |
| 12:28:39 | 부분 | 2 | -5.02 | -505,194 | 하드스톱(틱) |
| 12:28:39 | 전량 | 1 | -5.12 | -257,597 | 하드스톱(틱) |
| 12:44:44 | 부분 | 1 | +3.44 | +170,387 | 신동1차 |
| 12:54:39 | 전량 | 2 | +2.02 | +198,775 | 수동 전량청산 |
| 14:04:57 | 부분 | 1 | +1.81 | +89,048 | 하드스톱(틱) |
| 14:04:57 | 부분 | 1 | +1.79 | +88,048 | 하드스톱(틱) |
| 14:04:57 | 전량 | 1 | +1.75 | +86,048 | 하드스톱(틱) |
| 14:26:40 | 부분 | 1 | +3.95 | +196,042 | 신동1차 |
| 14:31:26 | 전량 | 2 | +0.17 | +14,084 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×16, `신동1차`×3, `수동 전량청산`×3

> 최종 청산이 하드스톱·손절 계열인 포지션 7/9건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -2,377,336 = 포지션합 -2,377,336 → OK · `[청산 완료]` 9건 = 조립 포지션 9건 → OK

### CB③ 판정 가능 시간 — **169분 / 370분 (46%)**

acc30m 버퍼 리셋 1회 · 그때 버린 표본 30건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 12건

| 시각 | 출처 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|---|
| 09:03:11 | 추정 | SHORT | 3 | 834.22 | — | — |
| 09:59:11 | 추정 | LONG | 3 | 844.08 | — | — |
| 10:05:10 | 추정 | LONG | 3 | 846.04 | — | — |
| 10:08:00 | 가상 | LONG | 1 | 847.06 | 3m | neutral |
| 10:36:10 | 추정 | LONG | 3 | 841.68 | — | — |
| 11:08:00 | 가상 | SHORT | 2 | 836.26 | 3m | trend |
| 11:40:00 | 가상 | LONG | 2 | 842.68 | 3m | neutral |
| 11:49:10 | 추정 | SHORT | 3 | 840.78 | — | — |
| 12:34:10 | 추정 | LONG | 3 | 848.8 | — | — |
| 13:20:10 | 추정 | LONG | 3 | 852.0 | — | — |
| 14:10:10 | 추정 | SHORT | 3 | 855.2 | — | — |
| 14:19:00 | 가상 | LONG | 2 | 853.62 | 3m | mean-revert |

계약수 분포 — 1계약×1, 2계약×3, 3계약×8

등급 분포 — `A급(원시C)`×4

**진입한 건들의 체크리스트 미통과 항목** — `risk`×4, `fore`×3, `ofi`×1, `chas`×1, `prev`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×5, **2계약**×7, **3계약**×8

실제 진입 계약수 — **1계약**×1, **2계약**×3, **3계약**×8

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×20

### 차단 사유 82건 · 20종

| 건수 | 사유 |
|---|---|
| 34 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 20 | 등급X — 미통과 항목: 2_confidence |
| 5 | 모드필터 — C급 신호 vs hybrid 모드(['A', 'B'] 만 허용) |
| 4 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 3 | JointGateBlock — meta=0.50<fallback> tox=0.70 joint=0.350 < 0.50 |
| 2 | 등급X — 미통과 항목: 3_vwap, 9_risk |
| 1 | 청산 후 쿨다운 — 138초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 18초 후 재진입 가능 |
| 1 | 자동진입 Degraded 정책 차단 — conf=42.2% < 62.0% |
| 1 | 청산 후 쿨다운 — 95초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 35초 후 재진입 가능 |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar, 9_risk |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar, 9_risk |
| 1 | 자동진입 Degraded 정책 차단 — conf=39.5% < 62.0% |
| 1 | 자동진입 Degraded 정책 차단 — conf=39.4% < 62.0% |
| 1 | 청산 후 쿨다운 — 99초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 98초 후 재진입 가능 |
| 1 | 자동진입 Degraded 정책 차단 — conf=39.8% < 62.0% |
| 1 | 자동진입 Degraded 정책 차단 — conf=39.3% < 62.0% |
| 1 | 자동진입 Degraded 정책 차단 — conf=40.9% < 62.0% |

**체크리스트 미통과 항목 누적** — `2_confidence`×20, `3_vwap`×4, `9_risk`×4, `4_cvd`×2, `7_prev_bar`×2, `5_ofi`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 7건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×5
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 11건 · 최대 7063ms · 5초 초과 1건

상위 — 7063ms, 4750ms, 4437ms, 3875ms, 3782ms, 3657ms, 3157ms, 2922ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 15:46:17 | 7063ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261023_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:27 2026-10-23 15:40:27 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 41분/일 < 하한 60분 — 금일 41분. | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 370분
--- ConstOut ×1(표본)
11:45:00 2026-10-23 11:45:00 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(3m=0.3579)
--- [Brier] 과신 ×6(표본)
11:50:00 2026-10-23 11:50:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.366 > 0.35
11:51:00 2026-10-23 11:51:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.364 > 0.35
11:52:00 2026-10-23 11:52:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.362 > 0.35
11:53:00 2026-10-23 11:53:00 [WARNING] SYSTEM: [Brier] 과신 경고 | 이동평균=0.358 > 0.35
--- [CB] ×5(표본)
09:53:19 2026-10-23 09:53:19 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:00:35 2026-10-23 10:00:35 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:12:15 2026-10-23 10:12:15 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:26:37 2026-10-23 10:26:37 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
09:53:19 2026-10-23 09:53:19 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:56:19)
09:53:19 2026-10-23 09:53:19 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:56:19)
09:54:00 2026-10-23 09:54:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=495ms | quality=1.00 | cache_age=171s | exceptions_10m=11 | exc_tags=[ShindongExec]×10 [ExitCooldown]×1
09:55:00 2026-10-23 09:55:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=307ms | quality=1.00 | cache_age=48s | exceptions_10m=10 | exc_tags=[ShindongExec]×9 [ExitCooldown]×1
--- [SHAP] 슬로우 ×7(표본)
11:34:04 2026-10-23 11:34:04 [WARNING] SYSTEM: [SHAP] 슬로우 감지 2970ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
12:28:01 2026-10-23 12:28:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 937ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:06:01 2026-10-23 13:06:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1142ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
13:30:01 2026-10-23 13:30:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 965ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
--- degraded=ON ×8(표본)
09:14:00 2026-10-23 09:14:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=315ms | quality=1.00 | cache_age=153s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
09:15:00 2026-10-23 09:15:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=405ms | quality=1.00 | cache_age=30s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
09:16:00 2026-10-23 09:16:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=272ms | quality=1.00 | cache_age=90s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
09:17:01 2026-10-23 09:17:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=366ms | quality=1.00 | cache_age=150s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
--- 메인 스레드 블로킹 ×8(표본)
04:38:49 2026-10-23 04:38:49 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4437 band=INFO since_pipe_s=NA
08:41:14 2026-10-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4750 band=INFO since_pipe_s=NA
08:41:18 2026-10-23 08:41:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3875 band=INFO since_pipe_s=NA
09:00:03 2026-10-23 09:00:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3782ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3782 band=INFO since_pipe_s=0.1
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20261023_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-23 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3366) | 앙상블 제외는 유지
09:44:00 2026-10-23 09:44:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3971) | 앙상블 제외는 유지
09:54:00 2026-10-23 09:54:00 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4456) | 앙상블 제외는 유지
10:29:00 2026-10-23 10:29:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.3409) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:23 2026-10-23 15:40:23 [INFO] SYSTEM: [CB③계측] 조건성립 138분 / 판정가능 169분 / 파이프라인 370분 · 그 창 진입 5포지션 · 손익 -183,503원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-23 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:05:00 2026-10-23 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:10:00 2026-10-23 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
09:15:00 2026-10-23 09:15:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.004 level=0 (heartbeat)
--- [CB] ×2(표본)
15:40:23 2026-10-23 15:40:23 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:23 2026-10-23 15:40:23 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:23 2026-10-23 15:40:23 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 1레그 / 1포지션 중 TP 이벤트 대응 0 · 신동 1차익절 대응 1 · 단일계약 보호전환(설계) 0 · 미대응 0
--- [SchedForceExit] ×1(표본)
15:11:09 2026-10-23 15:11:09 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×6(표본)
06:15:56 2026-10-23 06:15:56 [INFO] SYSTEM: [Shutdown] intent=user_restart keep_alive=True files=0 recent_stall=none
06:23:26 2026-10-23 06:23:26 [INFO] SYSTEM: [Shutdown] intent=user_close keep_alive=False files=2 recent_stall=none
06:25:04 2026-10-23 06:25:04 [INFO] SYSTEM: [Shutdown] intent=user_close keep_alive=False files=2 recent_stall=none
06:27:32 2026-10-23 06:27:32 [INFO] SYSTEM: [Shutdown] intent=user_close keep_alive=False files=2 recent_stall=none
--- 자동 종료 ×6(표본)
15:40:28 2026-10-23 15:40:28 [INFO] SYSTEM: [Notify] ℹ️ [15:40:28] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:28 2026-10-23 15:40:28 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 392초
15:40:28 2026-10-23 15:40:28 [INFO] SYSTEM: 자동 종료 예약 — 407초 후 Qt 이벤트 루프 종료
```

### `logs/20261023_SIGNAL.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-23 09:35:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1730 dir=+0)
09:35:00 2026-10-23 09:35:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:35:00 2026-10-23 09:35:00 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
09:36:00 2026-10-23 09:36:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1730 dir=+0)
--- WeightCollapse ×8(표본)
09:07:00 2026-10-23 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:10:00 2026-10-23 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:00 2026-10-23 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
09:16:00 2026-10-23 09:16:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×8(표본)
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
--- 안전망 ×8(표본)
09:07:00 2026-10-23 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-23 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-23 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:00 2026-10-23 09:16:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261023_LEARNING.log`
```
--- 축퇴 ×8(표본)
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.2001 < conf_floor=0.3300 (span=0.00021 auc=0.548 out_max=0.2001, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.498 out_max=0.2477 (기준 auc<0.53 and span<0.020, 기저율=0.2476 n=105) → 보정 미적용, raw 통과
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00007 auc=0.476 out_max=0.4000 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=80) → 보정 미적용, raw 통과
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00058 auc=0.453 out_max=0.2877 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
```

### `logs/20261023_HEALTH.log`
```
--- [ExitCooldown] ×8(표본)
09:54:00 2026-10-23 09:54:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=495ms | quality=1.00 | cache_age=171s | exceptions_10m=11 | exc_tags=[ShindongExec]×10 [ExitCooldown]×1
09:55:00 2026-10-23 09:55:00 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=307ms | quality=1.00 | cache_age=48s | exceptions_10m=10 | exc_tags=[ShindongExec]×9 [ExitCooldown]×1
09:56:01 2026-10-23 09:56:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=454ms | quality=1.00 | cache_age=108s | exceptions_10m=9 | exc_tags=[ShindongExec]×8 [ExitCooldown]×1
09:57:01 2026-10-23 09:57:01 [WARNING] HEALTH: [Health] level=WARNING degraded=ON | latency=442ms | quality=1.00 | cache_age=168s | exceptions_10m=8 | exc_tags=[ShindongExec]×7 [ExitCooldown]×1
--- degraded=ON ×8(표본)
09:14:00 2026-10-23 09:14:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=315ms | quality=1.00 | cache_age=153s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
09:15:00 2026-10-23 09:15:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=405ms | quality=1.00 | cache_age=30s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
09:16:00 2026-10-23 09:16:00 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=272ms | quality=1.00 | cache_age=90s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
09:17:01 2026-10-23 09:17:01 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=ON | latency=366ms | quality=1.00 | cache_age=150s | exceptions_10m=13 | exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1
```

### `logs/retrain_eod_20261023.log`
```
--- ConstOut ×1(표본)
??:??:?? | `[51]` | `아직 미확인` | ConstOut 호라이즌 건강도 |
--- 축퇴 ×1(표본)
??:??:?? | `[45]` | `cal_guard_flap_watch` | 축퇴 가드 플래핑 (게이지) |
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261023_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 4 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 13 | 09:03:10 [WARNING] 주문가능수량 미측정 — 계획 수량 3계약 그대로 주문(최종 판정은 브로커) |
| 10:00 | 장중 초반 | 49 | 09:59:10 [WARNING] 주문가능수량 미측정 — 계획 수량 3계약 그대로 주문(최종 판정은 브로커) |
| 14:00 | 장중 후반 · 장중 재학습 | 18 | 13:59:10 [INFO] 손절 849.5 → 852.90 (replay) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:23 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 04:38 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261023_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:41:10 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 24 | 08:50:22 [WARNING] 그리기 99.6ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 1048x1024 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 50 | 08:56:35 [WARNING] paintEvent slow 32.2ms | size=1484x950 candles=12 grid=10.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=… |
| 10:00 | 장중 초반 | 198 | 09:54:00 [WARNING] paintEvent slow 84.3ms | size=1967x1935 candles=69 grid=27.3 spans=10.3 candles=3.1 dir=0.3 regime=1.2 marker… |
| 12:00 | 장중 중간점 | 124 | 11:54:00 [WARNING] 과신 경고 | 이동평균=0.355 > 0.35 |
| 14:00 | 장중 후반 · 장중 재학습 | 175 | 13:54:01 [WARNING] level=WARNING degraded=ON | latency=315ms | quality=1.00 | cache_age=75s | exceptions_10m=10 | exc_tags=[Shin… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 136 | 15:04:01 [WARNING] paintEvent slow 120.2ms | size=1967x1935 candles=380 grid=41.3 spans=0.2 candles=21.8 dir=1.9 regime=8.1 mark… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 163 | 15:12:01 [WARNING] paintEvent slow 101.8ms | size=1967x1935 candles=388 grid=27.2 spans=0.2 candles=16.6 dir=1.5 regime=14.6 mar… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 16 | 15:34:00 [WARNING] paintEvent slow 86.6ms | size=1967x1935 candles=410 grid=23.5 spans=0.2 candles=18.4 dir=1.5 regime=5.7 marke… |
| 15:47 | EOD 재학습(py310_64) 완료 | 3 | 15:46:17 [WARNING] _tick_header 간격 7063ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2231 watchdog_alerted=[90, 150, 240] | [MainStall] stal… |

- 이 로그 생존구간: 04:38 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261023_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 99 | 08:40:47 [INFO] 활성화 | file=logs\crash_fault.log PID=3624 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 159 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 263 | 08:54:00 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 341 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 214 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 257 | 13:54:00 [INFO] code=A056B from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 192 | 15:04:00 [INFO] code=A056B from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 165 | 15:12:01 [INFO] code=A056B from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 67 | 15:34:00 [INFO] #160100 code=A056B raw_time=153400 parsed=15:34:00 price=864.74 vol=1 bid1=864.74 ask1=864.78 flag=49 side=BU… |
| 15:47 | EOD 재학습(py310_64) 완료 | 10 | 15:41:09 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:41:09 |

- 이 로그 생존구간: 04:38 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261023_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:10 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0235) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 98 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0468) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 188 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0465) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 154 | 09:54:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 12:00 | 장중 중간점 | 107 | 11:54:00 [WARNING] 신뢰도 미달 38.0% < 62.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 96 | 13:58:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 124 | 15:04:01 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:23 [INFO] daily reset complete |

- 이 로그 생존구간: 04:38 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261022 | 15:47 | 로그 본문 |
| 20261021 | 15:47 | 로그 본문 |
| 20261020 | 15:47 | 로그 본문 |
| 20261019 | 15:47 | 로그 본문 |
| 20261017 | 12:11 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261023** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-23 (MW0601 706차 — CREON 실거래 런처 실패 경로: 08:35 트리거 봉쇄 · 잘못된 세션 방치 · 저장 ID 계측) — 🟢 **사용자 지시 「2–3번 진행하고 개선안 구현해」 · 매매 경로 무변경**
## 2026-10-23 (MW0601 709차 — 장전 점검: CpTd6722 증거금조회 근본원인 특정 · O-4 해소관측) — 🟡 **조사 완료 · Fix 계획만(장후 적용 대기)**
## 2026-10-23 (MW0601 710차 — [9842] 수집 흐름 점검 → 사다리 API 폴백 · 장후 스냅샷 대사 오탐 해소) — ✅ **적용 · dev 배포**
## 2026-10-23 (MW0601 711차 — 709차 후속 장중 점검)
### 병행 세션 확인
### [신규 P1] 이상점 1-2 — 오늘 실손익(-2,456,977원) 전액이 수집기에 "추정"(출처불명)으로 오분류 — 실제 출처는 신동
### [신규 P1] 이상점 1-3 — `[ShindongExec]` 보유중 재생대조 지연 상시화 → HealthPolicy degraded 71%(실거래 영향 없음 확인)
### 검증
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
NG_ENTRY_SOURCE)`, 6346행 부근)는 설계상 `entry_horizon`을 넘기지 않는다(신동은 모델 호라이즌이 아니라 자체 규칙의 손절·목표가를 `set_external_levels()`로 덮어쓴다) — 이것 자체는 버그 아님. 수집기가 이 설계를 반영하지 못한 것이 버그.

**영향**: 돈·매매 영향 없음(순수 보고서 표시 문제). 다만 2026-10-13(688차)에 등록된 피터2 F-5/G-6과 같은 메커니즘이 신동에는 아직 이식되지 않은 채로 있었고, 707차로 신동이 주력 실거래 채널이 되면서(위험자본 3,400만원·`MAX_CONTRACTS=3`) 영향 범위가 "보조 채널 일부"에서 "하루 손익 전액"으로 커졌다.

**신규 여부(함정① 확인)**: 신동의 `entry_horizon=None` 설계 자체는 기존(685차부터 v9 전용 실행기). **신규인 것은** 이 조합이 하루 손익 전액에 영향을 미친 첫 사례라는 점. F-5/G-6(피터2용)과 합류하지 않고 별도 F-2로 분리 등록(신동은 피터2와 달리 `[Shindong]` 전용 태그·`position_state.json.entry_source`라는 더 신뢰도 높은 판별 신호가 있어, 수정 방법이 다르다).

**결정**: F-2(P1) — `collect_evidence.py:entry_source_of()`에 "신동" 분기 추가(`[Shindong] … OPEN` 같은 초 짝 또는 `entry_source` 필드 참조). `count_entry_sources()` 반환에 "신동" 키 추가. §5 출력 문구를 "엔진/피터2/신동/가상/추정" 5갈래로. 적용은 장후(스크립트 변경이라도 장중 규약을 그대로 지킨다).

### [신규 P1] 이상점 1-3 — `[ShindongExec]` 보유중 재생대조 지연 상시화 → HealthPolicy degraded 71%(실거래 영향 없음 확인)

**증상**: 신동 보유 구간에서 "60초 넘게 정규 대조가 없어 DB 직전 결과로 대신한다"는 폴백 경고(`[ShindongExec] 정규 재생 대조 N초 미갱신(옵션흐름 수집 미성공)`)가 오늘 **116회**(`grep -cE "정규 재생 대조 [0-9]+초 미갱신" logs/20261023_WARN.log`) — 보유 포지션 6건 대비 포지션당 약 19회. 직전 3거래일(10/22·21·20)은 보유건수가 더 많았는데도(9·11·12건) 같은 경고가 5·7·0회(포지션당 0.6·0.6·0회)뿐이었다. `logs/20261023_HEALTH.log` 138줄 중 98줄(71%)이 `degraded=ON`, 25줄이 `level=CRITICAL`이었고 거의 전부의 `exc_tags`가 `[ShindongExec]`로 지배됨(예: 09:14:00 CRITICAL `exceptions_10m=13 exc_tags=[ShindongExec]×10 [Peter2Offset]×2 [Peter2]×1`).

**원인 가설(미확정, 313차 원칙 — 확정 아님)**: `_shindong_hold_reconcile()`(main.py:6530 부근)의 "60초" 임계 체크가 매번 **자기 자신이 세운 `_sd_exec_last_sync`를 기준으로 재시작**되는 구조라, 정규(옵션흐름 기반) 경로가 한 번이라도 60초 안에 못 끝나면 그 뒤로는 폴백만 계속 돌 수 있는 설계로 보인다(코드 레벨 확인, 라이브 타이밍 계측은 아직 안 함). 오늘 신설된 F-1 대상 증거금 조회(`CpTd6722`, `BlockRequest` 동기호출)가 같은 2초 작업창을 잠식해 정규 경로를 매번 지연시키는지는 **시간적 동시 발생만 확인**, 인과는 미확정.

**영향**: 신동 자신의 진입·청산 판단은 `_shindong_entry_block_reason()`에 건강상태 조건이 없어(코드 확인) 이 영향을 받지 않음 — 오늘 실거래 손익에는 영향 없음. 다만 `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY=True`가 미륵 엔진(SYSTEM_AUTO, 오늘은 가상장부행) 자동진입의 최소신뢰도를 62%로 올리는 경로에는 걸려, 오늘 차단 49건 중 25건(51%)이 이 장치 때문이었다 — 엔진 신호 관측 품질이 평소보다 왜곡됐을 가능성.

**결정**: F-3(P1, 계측만 추가) — `_shindong_hold_reconcile()`·옵션흐름 수집 호출 지점에 소요시간 로그 추가(동작 변경 없음). G-2(고도화) — HealthPolicy 예외집계에서 "설계상 폴백 경로 사용"과 "진짜 코드 예외"를 분리. O-i1(관측) — F-1 적용 전후로 이 지연 빈도가 줄어드는지 비교해 인과 판정, 다음 거래일 이월.

### 검증

- 코드 변경 0건 · 커밋 0건 · 라이브 DB 접근 0건(로그·설정·git·`position_state.json` 스냅샷만).
- 재인용 금지 수치 미사용.
- 표본 부족 항목에 확정 결론 없음(313차): 이상점 1-3의 근본원인(F-1 부하 여부)은 "미확인"으로 명시, O-i1으로 다음 거래일 이월.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 709-1 [MW0601] CpTd6722 증거금조회 — 시장가 조회 시 단가필드 제거 (P1, 이상점 1-1)
### 709-2 [MW0601] O-4(계좌잔고 vs 기준자본 괴리) 해소 관측 — 1일 더 재확인 후 종결
### 709-3 [MW0601] O-p1 — 707·708차 라이브 첫날 종합 확인 (다음 국면이 판정)
## 2026-10-23 (MW0601 711차 — 장중 점검 등록)
### 711-1 [MW0601] F-2 — 증거 수집기에 "신동" 출처 분류 추가 (P1, 이상점 1-2)
### 711-2 [MW0601] F-3 — 신동 보유관리 지연 원인 가시화용 계측 로그 추가 (P1, 이상점 1-3)
### 711-3 [MW0601] G-2 — HealthPolicy 예외집계에서 "설계상 폴백"과 "진짜 예외" 분리 (고도화, 이번 주~26주 WFA 주기)
### 711-4 [MW0601] O-i1 — 신동 보유관리 지연(1-3)과 증거금조회(F-1) 신규부하의 인과관계 (다음 거래일 판정)
```

미완료 체크박스 **3333건** (끝에서 30건)
```
- [ ] 🔴 **F-27 (P1, 사용자 결정 대기)** `strategy/position/position_tracker.py: classify_exit_stage()`(560행대)·`_sync_partial_progress()`(1766~1801행) — 신동·피터2 자체 부분청산 사유("신동1차"·"신동최종"·"피터2미러")가 `"OTHER"`로 분류…
- [ ] **O-t4 (신규)** F-27 미승인 상태에서 신동이 "부분청산 후 하드스톱" 패턴을 다시 만드는 날 — `[ExitStageRecon]` 미대응 재현 여부를 매 장후 확인.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation — 오늘로 8거래일 연속 재현, 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **O-4 계열** 계좌 잔고 vs 사이저 기준자본 괴리 — 종가 즈음 약 28,359,139원 추정, 하루치 단독 판정 금지 설계 그대로.
- [ ] **705-1 (재기동 후 첫 거래일)** `[ShindongExec] … 보유 중(…), 새 신호 미집행` 로그와 `SKIP_HOLDING` 이벤트 → 리포트 §2-1 「재생만」 사유가 「집행 기록 없음(미측정)」 대신 「보유 중」으로 찍히는지.
- [ ] **705-2 (조사)** 10/21 리포트 MAIN +104.8만 vs 실거래 +222.7만 — 오늘과 반대 방향 차이. `python scripts/shindong_daily_report.py 2026-10-21` 재생성 후 §2-1로 분해.
- [ ] **705-3 (결정 대기)** 신동 판정 기준 — 사전등록 MAIN 재생 vs 실집행. 철회 후 집행 거래를 채점에 넣을지는 사전등록 §6(새 버전·재채점) 안건.
- [ ] **705-4 (조건부)** 이 PC 에서 **UAC 를 다시 켜면**(재부팅 필요) 직후 `powershell -File scripts/audit_com_task_runlevel.ps1` → 백필·정규수집·9842 스냅샷 3종을 각 `*_task.ps1` 로 재등록(Highest). 안 하면 매일 IsConnect=0 으로 조용히 실패.
- [ ] **705b-1 (다음 신동 「1차 익절 → 하드스톱」 날)** `[ExitStageRecon]` 이 INFO · `신동 1차익절 대응 1 · 미대응 0` 으로 찍히는지.
- [ ] **705b-2 (사용자 결정)** 라벨 체계에 외부 주체 사유 분기(`신동1차`→예: `EXT_TARGET1`) 신설 여부 — `test_490_exit_stage::test_실DB의_모든_exit_reason이_분류된다` 실패가 이것을 요구한다(702-1 별건과 동일). 라벨 체계 변경이라 자동조치 범위 밖.
- [ ] **705b-3 (기존 테스트 실패 6건 — 이번 변경 밖)** `test_498` 2건(704차 `strike_investor_flow.py` IDX_INS/StrikeInvestor · 705차 `shindong/daily_report.py` 대사 문구 태그 미등록) · `test_457` dashboard `peter_paste` 폴백 플…
- [ ] **705c-1 (다음 재기동 후 첫 신동 청산일)** `trades.exit_stage` 에 `EXT_TARGET1`/`EXT_TARGET2` 가 찍히고, 1차 익절 뒤 하드스톱은 `TRAIL_AFTER_TP1` · `[ExitStageRecon]` 미대응 0 인지.
- [ ] (705b-3 보강) `test_554::test_missing_reference_skips_check_but_is_not_silent` 는 `test_virtual_book` 과 같이 돌 때만 실패(실행 순서 간섭, HEAD 에서도 재현) · `test_virtual_book::test_main_dispatch_is_isolated` 는 py…
- [ ] `collection/cybos/api_connector.py:request_order_available_qty()`(1176행 부근) `input_pairs`에서 `(2, float(price or 0.0))` 제거 — 시장가(`ORDER_HOGA_MARKET`) 조회에는 단가 필드를 넘기지 않는다.
- [ ] 적용 후 1~2거래일은 `main.py:6115 _cap_margin_qty()`의 캡 적용은 보류하고 조회 성공 여부·값만 로그로 확인.
- [ ] `tests/test_707_capital_three_layers.py`에 CpTd6722 조회 성공 케이스(현재는 실패만 가정) 테스트 추가.
- [ ] G-1(저부담, 함께 적용 권장): `scripts/collect_evidence.py` §11에 `[CybosMarginQty] 조회 실패`/`margin_qty_fail_count`(B-02 계열) 당일 누적을 자동 노출.
- [ ] 10/24 장전 점검이 `logs/*_WARN.log`의 `Capital` 태그(기준자본 vs 실제잔고 괴리) 재현 여부 확인. 2일 연속(10/23·10/24) 미재현이면 O-4 완전 종결로 전환, 이후 지속관측 목록에서 제거.
- [ ] ProfitGuard 수량비례(원화임계 4종 × max(1, 선택주체 수량÷2)) — 실제 체결 로그에서 올바른 배율 확인.
- [ ] 손익추이 패널 `sdx`(신동 실거래, 708차 신설) 라벨 — 오늘 체결건 정상 분류 확인(기존 `sd`=신동(재생)과 혼동 없는지).
- [ ] 철회 섀도(`[ShindongRetractShadow]`, 708차 후속) — 실제 철회 상황 발생 시 로그 기록 확인.
- [ ] 우측패널 「3 주문/체결」 탭(707차 신설 UI 모니터) — 화면 정상표시는 로그로 확인 불가, 사용자 확인 필요.
- [ ] `.claude/skills/mireuk-daily-check/scripts/collect_evidence.py:entry_source_of()`에 "신동" 분기 추가 — `[Shindong] … OPEN` 같은 초(±2초) 짝 또는 `data/position_state.json`의 `entry_source` 필드 참조.
- [ ] `count_entry_sources()` 반환 딕셔너리에 "신동" 키 추가, §5 출력을 "엔진/피터2/신동/가상/추정" 5갈래로.
- [ ] 리포 루트에 스크립트 사본이 따로 있다면 양쪽 동기화(함정③ — 2026-08-26 사고 재발방지).
- [ ] `main.py:_shindong_hold_reconcile()`과 옵션흐름 수집 호출 지점에 소요시간 로그 추가(동작 변경 없음, 계측만).
- [ ] F-1(증거금 조회 수정) 적용 전후로 "정규 재생 대조 미갱신" 빈도 비교 — O-i1 판정 자료로 쓴다.
- [ ] `exc_tags` 집계 로직에 폴백 경로 사용(설계상 정상)과 `except Exception` 포착 예외를 별도 카운터로 분리.
- [ ] F-3 계측으로 1~2주 추이 관측 후 적용.
- [ ] F-1 적용 전후로 "정규 재생 대조 미갱신" 빈도가 줄어드는지 비교. 장중 라이브 DB 스캔 금지 규칙상 오늘은 로그 시간적 선후만 확인, 인과 미확정 상태로 이월.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
con]` 미대응 0 인지.
- [x] **장후 사용자 조치 1 완료** — 10-19~10-22 누적 점검 문서 일괄 커밋.
- [ ] (705b-3 보강) `test_554::test_missing_reference_skips_check_but_is_not_silent` 는 `test_virtual_book` 과 같이 돌 때만 실패(실행 순서 간섭, HEAD 에서도 재현) · `test_virtual_book::test_main_dispatch_is_isolated` 는 py37 미지원 `ast.get_source_segment` 사용.


## 2026-10-23 (MW0601 709차 — 장전 점검 등록)

### 709-1 [MW0601] CpTd6722 증거금조회 — 시장가 조회 시 단가필드 제거 (P1, 이상점 1-1)

- [ ] `collection/cybos/api_connector.py:request_order_available_qty()`(1176행 부근) `input_pairs`에서 `(2, float(price or 0.0))` 제거 — 시장가(`ORDER_HOGA_MARKET`) 조회에는 단가 필드를 넘기지 않는다.
- [ ] 적용 후 1~2거래일은 `main.py:6115 _cap_margin_qty()`의 캡 적용은 보류하고 조회 성공 여부·값만 로그로 확인.
- [ ] `tests/test_707_capital_three_layers.py`에 CpTd6722 조회 성공 케이스(현재는 실패만 가정) 테스트 추가.
- [ ] G-1(저부담, 함께 적용 권장): `scripts/collect_evidence.py` §11에 `[CybosMarginQty] 조회 실패`/`margin_qty_fail_count`(B-02 계열) 당일 누적을 자동 노출.

### 709-2 [MW0601] O-4(계좌잔고 vs 기준자본 괴리) 해소 관측 — 1일 더 재확인 후 종결

- [ ] 10/24 장전 점검이 `logs/*_WARN.log`의 `Capital` 태그(기준자본 vs 실제잔고 괴리) 재현 여부 확인. 2일 연속(10/23·10/24) 미재현이면 O-4 완전 종결로 전환, 이후 지속관측 목록에서 제거.

### 709-3 [MW0601] O-p1 — 707·708차 라이브 첫날 종합 확인 (다음 국면이 판정)

- [ ] ProfitGuard 수량비례(원화임계 4종 × max(1, 선택주체 수량÷2)) — 실제 체결 로그에서 올바른 배율 확인.
- [ ] 손익추이 패널 `sdx`(신동 실거래, 708차 신설) 라벨 — 오늘 체결건 정상 분류 확인(기존 `sd`=신동(재생)과 혼동 없는지).
- [ ] 철회 섀도(`[ShindongRetractShadow]`, 708차 후속) — 실제 철회 상황 발생 시 로그 기록 확인.
- [ ] 우측패널 「3 주문/체결」 탭(707차 신설 UI 모니터) — 화면 정상표시는 로그로 확인 불가, 사용자 확인 필요.

## 2026-10-23 (MW0601 711차 — 장중 점검 등록)

### 711-1 [MW0601] F-2 — 증거 수집기에 "신동" 출처 분류 추가 (P1, 이상점 1-2)

- [ ] `.claude/skills/mireuk-daily-check/scripts/collect_evidence.py:entry_source_of()`에 "신동" 분기 추가 — `[Shindong] … OPEN` 같은 초(±2초) 짝 또는 `data/position_state.json`의 `entry_source` 필드 참조.
- [ ] `count_entry_sources()` 반환 딕셔너리에 "신동" 키 추가, §5 출력을 "엔진/피터2/신동/가상/추정" 5갈래로.
- [ ] 리포 루트에 스크립트 사본이 따로 있다면 양쪽 동기화(함정③ — 2026-08-26 사고 재발방지).

### 711-2 [MW0601] F-3 — 신동 보유관리 지연 원인 가시화용 계측 로그 추가 (P1, 이상점 1-3)

- [ ] `main.py:_shindong_hold_reconcile()`과 옵션흐름 수집 호출 지점에 소요시간 로그 추가(동작 변경 없음, 계측만).
- [ ] F-1(증거금 조회 수정) 적용 전후로 "정규 재생 대조 미갱신" 빈도 비교 — O-i1 판정 자료로 쓴다.

### 711-3 [MW0601] G-2 — HealthPolicy 예외집계에서 "설계상 폴백"과 "진짜 예외" 분리 (고도화, 이번 주~26주 WFA 주기)

- [ ] `exc_tags` 집계 로직에 폴백 경로 사용(설계상 정상)과 `except Exception` 포착 예외를 별도 카운터로 분리.
- [ ] F-3 계측으로 1~2주 추이 관측 후 적용.

### 711-4 [MW0601] O-i1 — 신동 보유관리 지연(1-3)과 증거금조회(F-1) 신규부하의 인과관계 (다음 거래일 판정)

- [ ] F-1 적용 전후로 "정규 재생 대조 미갱신" 빈도가 줄어드는지 비교. 장중 라이브 DB 스캔 금지 규칙상 오늘은 로그 시간적 선후만 확인, 인과 미확정 상태로 이월.

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

### `data/alert_mail/2026-10-23_main.json` — 263B · 10-23 12:28:39
```json
{
 "open": {},
 "oneshot": [
  "A-04|trade:2026-10-23 09:53:19",
  "A-04|day",
  "A-04|trade:2026-10-23 10:26:37",
  "A-04|trade:2026-10-23 12:28:39"
 ],
 "sent": 4,
 "cap_notified": false,
 "history": [
  "A-04",
  "A-04",
  "A-04",
  "A-04"
 ]
}
```

### `data/dailycheck_markers/claude-20261023-intra-mireuk-intra-20261023032723.json` — 180B · 10-23 12:27:23
```json
{
 "pc": "claude",
 "date": "20261023",
 "phase": "intra",
 "session": "mireuk-intra-20261023032723",
 "pid": 7,
 "started_epoch": 1792726043.2199051,
 "started_at": "2026-10-23 03:27:23"
}
```

### `data/dailycheck_markers/claude-20261023-post-coworksession_20261023_post.json` — 179B · 10-23 16:20:53
```json
{
 "pc": "claude",
 "date": "20261023",
 "phase": "post",
 "session": "coworksession_20261023_post",
 "pid": 6,
 "started_epoch": 1792740054.2478726,
 "started_at": "2026-10-23 07:20:54"
}
```

### `data/heartbeat_MW0601_20261023.json` — 244B · 10-23 15:46:53
```json
{
 "pid": 3624,
 "written_at": "2026-10-23T15:46:53",
 "beat_epoch": 1792738009.7372758,
 "beat_age_sec": 3.9,
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

### `data/peter_feed/_raw/2026-10-23.eod_ids.json` — 437B · 10-23 16:10:04
```json
[
 "2113417767793926641",
 "2113420447845155173",
 "2113420578355122646",
 "2113420733707845849",
 "2113420871306235965",
 "2113421008040579324",
 "2113491528761135458",
 "2113492755523735981",
 "2113504501265297488",
 "2113505476570947665",
 "2113505602840531070",
 "2113505714996232701",
 "2113505796210446705",
 "2113505857124384826",
 "2113514293769707776",
 "2113514354029343051",
 "2113514443951030612",
 "2113514585416438187",
 "2113514644354830496"
]
```

### `data/peter_feed/_raw/2026-10-23.jsonl` — 4.7KB · 10-23 15:16:18
```json
JSONL 20행 ⏎ 첫: {"id": "2113417767793926641", "dt": "2026-10-22T23:50:35.000Z", "text": "오늘은 19일 월요일처럼\n\n갭하락후 어느정도는 올릴 수 있지만\n\n쭉 말아 올리는 패턴이 오늘은 어렵습니다.\n\n우선 지켜보고 코멘트 하겠습니다.", "seen_at": "2026-10-23T08:50:58+09:00", "src": "live"} | {"id": "2113420447845155173", "dt": "2026-10-23T00:01:14.000Z", "text": "피터리 - 10월 23일 국내 장전 주식뉴스 - 축약본", "seen_at": "2026-10-23T09:01:36+09:00", "src": "live"} | {"id": "2113420733707845849", "dt": "2026-10-23T00:02:23.000Z", "text": "", "seen_at": "2026-10-23T09:02:58+09:00", "kind": "empty", "src": "live"} ⏎ 끝: {"id": "2113514644354830496", "dt": "2026-10-23T06:15:33.000Z", "text": "", "seen_at": "2026-10-23T15:16:18+09:00", "kind": "empty", "src": "live"} | {"id": "2113514585416438187", "dt": "2026-10-23T06:15:19.000Z", "text": "", "seen_at": "2026-10-23T15:16:18+09:00", "kind": "empty", "src": "live"} | {"id": "2113514443951030612", "dt": "2026-10-23T06:14:45.000Z", "text": "", "seen_at": "2026-10-23T15:16:18+09:00", "kind": "empty", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-23 15:53:36**

| 키 | 값 | 수집 대상일(2026-10-23)과 일치 |
|---|---|---|
| `date` | 2026-10-23 | 예 |
| `p8_last_success_date` | 2026-10-23 | 예 |
| `eod_retrain_ok_date` | 2026-10-23 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-23 08:55:11 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-22) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-23 08:55:11 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-22) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 384 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **0봉**

- 라이브 로그 대조: `logs/20261023_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 5회 · 재시작 1회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 5개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **6건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 3624: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:47 · 정규장(09:00) 이후 **0건**
- PID 20240: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 06:16:54 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 8984 | 04:38:21 | 06:15:56 | 없음 | 판정불가 — WER **미측정** |
| 20240 | 06:16:54 | 06:23:26 | 없음 | 판정불가 — WER **미측정** |
| 23308 | 06:24:09 | 06:25:04 | 없음 | 판정불가 — WER **미측정** |
| 26720 | 06:26:58 | 06:27:32 | 없음 | 판정불가 — WER **미측정** |
| 3624 | 08:40:47 | 15:47:15 | 없음 | 판정불가 — WER **미측정** |


#### 재기동 귀속 대사 (684차 G-5)

| 재시작 | 런처 분류 | 종료 의도 로그(−3~+1분) | ±5분 이내 커밋(설명 후보) | 창 밖 당일 커밋 |
|---|---|---|---|---|
| 06:15 | 일시적 크래시 | 06:15 `user_restart` | 06:17 `0a880ff9` [MW0601] 707차 후속2: dev 실전 자본 3층 켜짐 기록 — 이식 메모 갱신 …, 06:12 `54144e55` [MW0601] 707차 후속: 실전 자본 3층 dev 배포 기록 — 이식 메모 (dev…, 06:11 `be41c470` [MW0601] 708차: 신동 실거래 출처 분리 · 철회 섀도 계측 | 4건(시각 불일치 — 후보 아님) |

- 🔴 커밋은 **인과가 아니라 후보**다. 창 밖 커밋을 원인으로 적지 말 것.
- 「종료 의도 로그 **없음**」 + `[CLEAN EXIT]` 있음 = 의도 경로를 거치지 않은 정상 종료다. ⚠ **684차 이전**의 X 버튼 종료(`user_close`/`user_restart`)는 로그 파일에 남지 않았다(모듈 로거가 파일 핸들러에 안 붙어 있었다) — 그 시기의 「없음」은 X 버튼 재시작을 배제하지 못한다.

> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

### 9-e. 피터2 단독 수집 추적 (698차 — MW0602 수집기 중지 효과)

- 최종: **IN_PROGRESS** — 진행 중 — 평가 창 5거래일 미도달(중간값은 참고만) (평가 4/5거래일)
- 오늘: 트윗 n=20 · p90=74.9초 · 외부소진 중앙 0.0(기준선 27.0) · 429(정규장) 0건 · ① PASS · ② PASS
- 전체 표: `python tools/peter2_live/sole_collect_tracker.py --upto 2026-10-23`

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 247개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261023-점검리포트.md` | 46.6KB | 10-23 12:41 |
| `docs/정기점검/매일점검/evidence_MW0601-20261023_intra.md` | 91.6KB | 10-23 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261023_pre.md` | 67.5KB | 10-23 08:59 |
| `docs/정기점검/매일점검/MW0601-20261022-점검리포트.md` | 72.3KB | 10-22 17:55 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_post.md` | 102.7KB | 10-22 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_intra.md` | 83.8KB | 10-22 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_pre.md` | 65.5KB | 10-22 08:59 |
| `docs/정기점검/매일점검/MW0601-20261021-점검리포트.md` | 70.3KB | 10-21 17:29 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261023.json` | 3.1KB | 10-23 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261023.md` | 5.4KB | 10-23 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261023.json` | 38.9KB | 10-23 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20261023.md` | 32.0KB | 10-23 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261023.json` | 130.5KB | 10-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261023.md` | 194.4KB | 10-23 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261016.json` | 3.1KB | 10-16 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261016.md` | 5.4KB | 10-16 15:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20261023_WARN.log`: ERROR 이상 39건
2. `logs/20261023_HEALTH.log`: ERROR 이상 39건
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. **엔진 진입 0건 / 계좌 진입 11건**(그중 외부표식 0건 · 피터2 0건 · 판별불가 8건 · 별도 가상 장부 4건) — 차단 82건. 최다 차단 사유: `자동진입 Degraded 최소신뢰도 62.0% 미달` (진입0 딥다이브 절차를 따르라. 계좌 진입이 있으면 그 손익을 **엔진 성적으로 집계하지 말 것**)
5. 포지션 9건 중 최종청산이 하드스톱·손절 계열 **7건(78%)** — 손절 준수율 확인 필요 (레그 22행)
6. 다레그 포지션 **9건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
7. 메인 스레드 정지 5초 초과 **1건** (최대 7063ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
8. `logs/20261023_WARN.log`: **[Brier] 과신** 6건(표본)
9. `logs/20261023_WARN.log`: **degraded=ON** 8건(표본)
10. `logs/20261023_WARN.log`: **ConstOut** 1건(표본)
11. `logs/20261023_SYSTEM.log`: **ConstOut** 8건(표본)
12. `logs/20261023_SIGNAL.log`: **WeightCollapse** 8건(표본)
13. `logs/20261023_SIGNAL.log`: **ConstOut** 8건(표본)
14. `logs/20261023_LEARNING.log`: **축퇴** 8건(표본)
15. `logs/20261023_HEALTH.log`: **degraded=ON** 8건(표본)
16. `logs/retrain_eod_20261023.log`: **축퇴** 1건(표본)
17. `logs/retrain_eod_20261023.log`: **ConstOut** 1건(표본)
18. `logs/crash_fault.log`: `Windows fatal exception` **6건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
19. 미커밋 변경 27건 (실질 12건 · 코드 0건 · EOL 파생 0건)
20. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261023*.log` (Windows) / `grep 강제청산 logs/*20261023*.log`*