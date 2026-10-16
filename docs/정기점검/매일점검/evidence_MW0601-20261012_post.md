# 미륵이 증거 다이제스트 — 2026-10-12 / POST

- 생성 2026-10-12 16:18:24 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01dfw9a3fzxqctn1gyucmrti/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261012` · `2026-10-12` · `261012` · `1012`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **50개** 파일 · 50개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-intra-cowork-intra-{DATE}-1226.json` | 1 | `data/dailycheck_markers/claude-20261012-intra-cowork-intra-20261012-1226.json` | 179B | 10-12 12:26 |
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20261012.txt` | 28B | 10-12 15:40 |
| `daily_close_started_{DATE}.txt` | 1 | `data/daily_close_started_20261012.txt` | 28B | 10-12 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261012.txt` | 233B | 10-12 15:53 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261012.log` | 1.4KB | 10-12 15:39 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261012.log` | 217B | 10-12 15:52 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261012.json` | 244B | 10-12 15:46 |
| `launcher_{DATE}_084000_21183.log` | 1 | `logs/Mireuk_batch/launcher_20261012_084000_21183.log` | 2.5MB | 10-12 15:47 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261012.log` | 109B | 10-12 08:44 |
| `mainstall_traceback_{DATE}.log` | 1 | `logs/mainstall_traceback_20261012.log` | 12.0KB | 10-12 15:46 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261012.log` | 68.7KB | 10-12 15:34 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261012.log` | 491B | 10-12 16:15 |
| `position_state.json.gen_{DATE}_144202` | 1 | `data/position_state.json.gen_20261012_144202` | 1.5KB | 10-12 14:42 |
| `position_state.json.gen_{DATE}_144237` | 1 | `data/position_state.json.gen_20261012_144237` | 1.5KB | 10-12 14:42 |
| `position_state.json.gen_{DATE}_144602` | 1 | `data/position_state.json.gen_20261012_144602` | 1.6KB | 10-12 14:42 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261012.log` | 26.1KB | 10-12 15:53 |
| `retrain_intraday_20260706_{DATE}58.log` | 1 | `logs/retrain_intraday_20260706_101258.log` | 4.6KB | 07-06 10:13 |
| `retrain_intraday_{DATE}_093420.log` | 1 | `logs/retrain_intraday_20261012_093420.log` | 5.7KB | 10-12 09:35 |
| `retrain_intraday_{DATE}_112306.log` | 1 | `logs/retrain_intraday_20261012_112306.log` | 5.7KB | 10-12 11:23 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261012.log` | 64.2KB | 10-12 16:04 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261012.txt` | 43B | 10-12 15:47 |
| `strategy_report_{DATE}_154020.txt` | 1 | `data/daily_reports/strategy_report_20261012_154020.txt` | 2.3KB | 10-12 15:40 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-12.jsonl` | 7.3KB | 10-12 15:14 |
| `{DATE}_0902_D.xls` | 1 | `data/db/option_hts/261012_0902_D.xls` | 477.2KB | 10-12 09:03 |
| `{DATE}_0931_D.xls` | 1 | `data/db/option_hts/261012_0931_D.xls` | 477.4KB | 10-12 09:31 |
| `{DATE}_1007_D.xls` | 1 | `data/db/option_hts/261012_1007_D.xls` | 477.5KB | 10-12 10:07 |
| `{DATE}_1030_D.xls` | 1 | `data/db/option_hts/261012_1030_D.xls` | 477.5KB | 10-12 10:33 |
| `{DATE}_1105_D.xls` | 1 | `data/db/option_hts/261012_1105_D.xls` | 477.6KB | 10-12 11:05 |
| `{DATE}_1133_D.xls` | 1 | `data/db/option_hts/261012_1133_D.xls` | 477.6KB | 10-12 11:33 |
| `{DATE}_1202_D.xls` | 1 | `data/db/option_hts/261012_1202_D.xls` | 477.6KB | 10-12 12:02 |
| `{DATE}_1230_D.xls` | 1 | `data/db/option_hts/261012_1230_D.xls` | 477.6KB | 10-12 12:30 |
| `{DATE}_1330_D.xls` | 1 | `data/db/option_hts/261012_1330_D.xls` | 477.6KB | 10-12 13:30 |
| `{DATE}_1400_D.xls` | 1 | `data/db/option_hts/261012_1400_D.xls` | 477.6KB | 10-12 14:01 |
| `{DATE}_1500_D.xls` | 1 | `data/db/option_hts/261012_1500_D.xls` | 477.7KB | 10-12 15:00 |
| `{DATE}_D.xls` | 1 | `data/db/option_hts/261012_D.xls` | 477.7KB | 10-12 15:52 |
| `{DATE}_DATA.log` | 1 | `logs/20261012_DATA.log` | 436.5KB | 10-12 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261012_DEBUG.log` | 228.2KB | 10-12 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261012_HEALTH.log` | 4.2KB | 10-12 14:52 |
| `{DATE}_HOGA.log` | 1 | `logs/20261012_HOGA.log` | 56.5MB | 10-12 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261012_LEARNING.log` | 386.8KB | 10-12 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20261012_MICRO.log` | 1.0MB | 10-12 15:38 |
| `{DATE}_P.xls` | 1 | `data/db/option_hts/261012_P.xls` | 478.0KB | 10-12 15:52 |
| `{DATE}_PROBE.log` | 1 | `logs/20261012_PROBE.log` | 122.3KB | 10-12 15:34 |
| `{DATE}_REGULAR_COLLECT.log` | 1 | `logs/20261012_REGULAR_COLLECT.log` | 8.2KB | 10-12 15:52 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261012_SIGNAL.log` | 561.3KB | 10-12 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261012_SYSTEM.log` | 1.0MB | 10-12 15:47 |
| `{DATE}_TRADE.log` | 1 | `logs/20261012_TRADE.log` | 12.1KB | 10-12 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20261012_WARN.log` | 763.8KB | 10-12 15:46 |
| `{DATE}_tr.draft.txt` | 1 | `data/peter_feed/2026-10-12_tr.draft.txt` | 216B | 10-12 15:40 |
| `{DATE}_tr.txt` | 1 | `data/peter_feed/2026-10-12_tr.txt` | 216B | 10-12 15:40 |

## 2. 코드·커밋 상태

- HEAD `efbadf8` · 브랜치 `v9-dev` · 미커밋 120건 · 실질 변경 18건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 18 · 미추적 102 · 삭제 12 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261012.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json` … 외 6개
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 3.9초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261012.md
 M docs/미륵이고도화3/신동2/학습/lessons.json
 M docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md
 M docs/미륵이고도화3/신동2/학습/추이_MW0601.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md
 D docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md
 D docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260904.md
 D docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260911.md
?? "MAEKJEOM_LADDER.bat - 바로 가기.lnk"
?? dev_memory/_tmp_append_decisionlog_20261001.md
?? dev_memory/_tmp_append_decisionlog_20261002.md
?? dev_memory/_tmp_append_decisionlog_20261006_post.md
?? dev_memory/_tmp_append_decisionlog_20261007_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_intra.md
?? dev_memory/_tmp_append_decisionlog_20261008_pre.md
?? dev_memory/_tmp_append_decisionlog_20261009_intra.md
?? dev_memory/_tmp_append_decisionlog_20261009_post.md
?? dev_memory/_tmp_append_decisionlog_20261012_intra.md
?? dev_memory/_tmp_append_decisionlog_20261012_pre.md
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_pre.md
?? dev_memory/_tmp_append_nexttodo_20261009_intra.md
?? dev_memory/_tmp_append_nexttodo_20261012_intra.md
?? dev_memory/_tmp_append_nexttodo_20261012_pre.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
… 외 80건
```

**당일(2026-10-12) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
efbadf8 [MW0601] 668차 후속11·12 후속: dev 배포 기록(74b7d3c·94aaa20)
9e88005 [MW0601] 668차 후속12: 과금 채널을 PC 에 고정 — MW0601=CYBOS 0.0098% · MW0602=CREON 0.0019%
2ad034b [MW0601] 668차 후속11: 피터2 해석 결함 3건 + 파일 교체 재시도 (10-12 장중 실측)
b0b92de [MW0601] 679차 후속2 후속: dev 배포 기록(64e1f0e)
924f20e [MW0601] 679차 후속2: 신동2 실행기 — 장중 회차 잠금 대기 · 원자적 잠금 · 로그 뮤텍스
7068f81 [MW0601] 679차 후속: 사다리 증분 커서 잠재결함 딥다이브 기록 — 현행 유지
d80df65 [MW0601] 679차 후속 후속: dev 배포 기록(5351c8b)
b5d1100 [MW0601] 679차 후속: 맥점 사다리 — 7222 흐름 미래분 채움 제거 · 신동2 최신 해설 legacy 배제
89b4b0b [MW0601] 668차 후속10: dev 피터2 수정 이식 — 시간순 처리 · 탭 증식 · 고아 스크립트 (원 4f603c7·8876cb0·60bfd55, dev/MW0602)
d5f05e9 [MW0601] 668차 후속9 후속: dev 배포 기록(ba1bf6a)
e7f50c6 [MW0601] 668차 후속9: 피터2 체결 트윗 대기에 앞선 지시의 손절·목표 승계 + CLOSED 사유 키 수정
131db0a [MW0601] 668차 후속8 후속: dev 배포 기록(f1d9000·fcdeca8·b44dbd6)
4631654 [MW0601] 668차 후속8: 피터2 하트비트를 「마지막 정상 게시」 기준으로 — X 페이지 오류 반영
c81fa27 [MW0601] 668차 후속7: 피터2 당일 수동 오프셋 — 만기 다음 날 진입 공백 해소
```

**최근 커밋 12건**
```
efbadf8 [MW0601] 668차 후속11·12 후속: dev 배포 기록(74b7d3c·94aaa20)
9e88005 [MW0601] 668차 후속12: 과금 채널을 PC 에 고정 — MW0601=CYBOS 0.0098% · MW0602=CREON 0.0019%
2ad034b [MW0601] 668차 후속11: 피터2 해석 결함 3건 + 파일 교체 재시도 (10-12 장중 실측)
b0b92de [MW0601] 679차 후속2 후속: dev 배포 기록(64e1f0e)
924f20e [MW0601] 679차 후속2: 신동2 실행기 — 장중 회차 잠금 대기 · 원자적 잠금 · 로그 뮤텍스
7068f81 [MW0601] 679차 후속: 사다리 증분 커서 잠재결함 딥다이브 기록 — 현행 유지
d80df65 [MW0601] 679차 후속 후속: dev 배포 기록(5351c8b)
b5d1100 [MW0601] 679차 후속: 맥점 사다리 — 7222 흐름 미래분 채움 제거 · 신동2 최신 해설 legacy 배제
89b4b0b [MW0601] 668차 후속10: dev 피터2 수정 이식 — 시간순 처리 · 탭 증식 · 고아 스크립트 (원 4f603c7·8876cb0·60bfd55, dev/MW0602)
d5f05e9 [MW0601] 668차 후속9 후속: dev 배포 기록(ba1bf6a)
e7f50c6 [MW0601] 668차 후속9: 피터2 체결 트윗 대기에 앞선 지시의 손절·목표 승계 + CLOSED 사유 키 수정
131db0a [MW0601] 668차 후속8 후속: dev 배포 기록(f1d9000·fcdeca8·b44dbd6)
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

### 차단 게이트 전수 인벤토리 — 40개 중 **9개 꺼짐**

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

_본문 미열람(설정): `20261012_HOGA.log` 56.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20261012.txt`** — 28B · 10-12 15:40:20
```
2026-10-12T15:40:20.519541
```

**`data/daily_close_started_20261012.txt`** — 28B · 10-12 15:40:06
```
2026-10-12T15:40:06.485428
```

**`data/daily_reports/strategy_report_20261012_154020.txt`** — 2.3KB · 10-12 15:40:20
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-10-12 15:40
========================================================
  버전    : v1.0  (95일차)
  판정    : OUTPERFORM
  Live(20일): Sh=2.96  MDD(자본대비)=2.3%
  당일      : WR=40.0%  PF=0.26
  롤링20일: 누적 +6238290원  Sh=2.96  MDD(자본대비)=2.3%  MDD(peak대비)=15.6%
  당일손익 : broker(gross) -345,000원  수수료 15,415원  net -360,415원  ※ 전환기준①=net
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.002 (CLEAR)
  PSI/feat: cvd_delta=0.002  ofi_pressure=0.001  vwap_position=0.092
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 -33,177원  승률 50.0%  합계 -663,539원
  등급별 순EV(30일): A=-9,070원(59건,승56%)  P=-161,935원(3건,승0%)
  호라이즌별 순EV(30일): 1m=+2,297원(7건)  3m=+9,628원(34건)  5m=-48,810원(18건)  ?=-161,935원(3건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 14분  5일평균 38분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 36.1pt(5일평균 26.6pt)  1분평균변동 0.90pt(5일평균 0.60pt)
--------------------------------------------------------
  진입 퍼널(2026-10-12, 총 368분):
    FLAT 256 → conf미달 94 → CoherenceGate 3 → 게이트차단 12 → 후보 3 → 진입 2
    └ 등급상향경로(앙상블X→체크리스트통과): 1건 [285차-P5]
    게이트별: 콜드스타트/기타(조건부구간)=5  콜드스타트/기타(σ미수집)=4  체크리스트항목미달=3
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 1건
      └ 상세: JointGateBlock=1
      └ JointGateBlock 1건 (무정보폴백 0건 = 0.0%) [표본 19건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20261012.txt`** — 233B · 10-12 15:53:38
```
completed: 2026-10-12 15:53:38
rows: 20091
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 25.5
t_retrain_s: 189.3
t_total_s: 215.3
daily_close_seen: true
wait_dc_timeout: false
daily_close_stalled: false
```

**`data/peter_feed/2026-10-12_tr.draft.txt`** — 216B · 10-12 15:40:07
```
09:08 L 1035 / 09:50 X 1030 손절
10:02 L 1026 / 10:09 X 1022 손절
10:11 L 1022 / 10:19 X 1019 손절
10:27 L 1017 / 14:21 X 1014 손절
14:24 L 1015 / 14:34 X 1012 손절
14:46 L 1007 / 15:11 X 1012 수익
```

**`data/peter_feed/2026-10-12_tr.txt`** — 216B · 10-12 15:40:07
```
09:08 L 1035 / 09:50 X 1030 손절
10:02 L 1026 / 10:09 X 1022 손절
10:11 L 1022 / 10:19 X 1019 손절
10:27 L 1017 / 14:21 X 1014 손절
14:24 L 1015 / 14:34 X 1012 손절
14:46 L 1007 / 15:11 X 1012 수익
```

**`data/shutdown_normal_20261012.txt`** — 43B · 10-12 15:47:14
```
auto_shutdown
2026-10-12T15:47:14.535884
```

_다이제스트 대상 8/23개 (중요도순). 제외: `retrain_intraday_20261012_112306.log`, `retrain_intraday_20260706_101258.log`, `20261012_MICRO.log`, `20261012_DATA.log`, `20261012_PROBE.log`, `launcher_20261012_084000_21183.log`, `20261012_DEBUG.log`, `peter2_receiver_20261012.log`_

### `logs/20261012_TRADE.log` — 12.1KB · 98행 · 최종 15:40:15

- 형식 평문 · 시각 인식 98행 · WARNING=3, INFO=95

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-12 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-12 09:34:08 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-12 09:34:14 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-12 10:02:40 [INFO] TRADE: [Peter2] 진입 LONG 1계약 @1023.66 손절 1019.72 목표 - — limit LONG 지시 1026(미니 1023.72) 현재 1023.66
  …
2026-10-12 14:46:02 [INFO] TRADE: [Chejan] 상태=접수 주문번호=5032 code=A056B 방향=LONG 체결=1 미체결=0
2026-10-12 14:46:02 [INFO] TRADE: [Chejan] 상태=체결 주문번호=5032 code=A056B 방향=LONG 체결=1 미체결=0
2026-10-12 14:46:02 [INFO] TRADE: [Position] 체결청산 SHORT @ 1006.56 | PnL=+0.59pt (+27,586원) | 하드스톱(틱)
2026-10-12 14:46:02 [INFO] TRADE: [청산 완료] PnL=+0.59pt (+27,586원) | 포지션 합계 +57,173원 (레그 2)
2026-10-12 15:40:15 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 3 | 10:02:40 | 14:21:30 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1023.70 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×98

**컴포넌트 상위 15** — `Chejan`×27, `Position`×19, `주문요청`×12, `Peter2`×5, `체결진입`×5, `청산 완료`×5, `ProfitGuard`×4, `TickStop-S0C`×4, `Sizer`×4, `PositionFallback`×3, `체결진입보정`×3, `진입체크`×2, `TickTP1`×2, `TP1 부분청산`×2, `JointGateBlock 차단`×1

### `logs/20261012_WARN.log` — 763.8KB · 3497행 · 최종 15:46:12

- 형식 평문 · 시각 인식 3493행 · CRITICAL=1, ERROR=1, WARNING=3491, PLAIN=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-12 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=333044256
2026-10-12 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
2026-10-12 08:41:09 [WARNING] SYSTEM: [출처축] 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것
  …
2026-10-12 15:46:06 [WARNING] SYSTEM: [SessionBackfill] OHLCV 불일치 ts=2026-10-12 12:50:00 cols=['open'] existing_source=rt
2026-10-12 15:46:06 [WARNING] SYSTEM: [SessionBackfill] 당일 마감구간 보충 — chart=411 existing=408 inserted=3 open_fixed=1 mismatch=6
2026-10-12 15:46:06 [WARNING] SYSTEM: [BarGap] 당일 확정(2026-10-12) — raw_candles 382봉 / session_bars 384봉 (절단선 15:08 이하) | 결손 2봉 (09:33, 11:22) — 전부 session_bars 에 보존됨, 백필 안 함(533차)
2026-10-12 15:46:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 6297ms — 메인 스레드 블로킹 발생 | pipe_elapsed=2226 watchdog_alerted=[90, 150, 240] | [MainStall] stall_ms=6297 band=WARN since_pipe_s=2231.6
2026-10-12 15:46:12 [WARNING] SYSTEM: [MainStallTrace] 스택 스냅샷 기록 (2/20) → logs/mainstall_traceback_20261012.log
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 09:36:06 | 09:36:06 | level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1 |
| ERROR | `NetRecon` | 1 | 15:40:15 | 15:40:15 | 🔴 net 불일치 — 엔진 -360,415원 vs 브로커 -424,534원 (잔차 +64,119원, 허용 ±15,907) |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

</details>

<details><summary>ERROR/NetRecon 원문 1건</summary>

```
2026-10-12 15:40:15 [ERROR] SYSTEM: [NetRecon] 🔴 net 불일치 — 엔진 -360,415원 vs 브로커 -424,534원 (잔차 +64,119원, 허용 ±15,907)
```

</details>

**WARNING — 태그 40종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 2799 | 09:36:09 | 15:36:06 | restore_saved_geometry: y=-493 < 0 → y=0으로 보정 (음수 y → Windows DPI 1.5× 확대 방지) |
| `LiveDBG` | 333 | 08:41:08 | 15:46:12 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 77 | 08:41:19 | 15:30:07 | 그리기 71.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 889x1001 |
| `Peter2` | 31 | 08:41:14 | 13:43:56 | 기동 date=2026-10-12 offset=-4.88 src=prev_day:2026-10-08 safe=False 복원트윗=0 집행이력=0 손절=0 |
| `ChejanFlow` | 27 | 10:02:40 | 14:46:02 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='1484' | pending='ENTRY:LONG qty=1 filled=0 order_no=? reason=진입 req_at=10:02:40.440' | positio… |
| `ChejanMatch` | 27 | 10:02:40 | 14:46:02 | order_no='1484' | pending='ENTRY:LONG qty=1 filled=0 order_no=1484 reason=진입 req_at=10:02:40.440' | pending_matched=True |
| `PendingOrder` | 24 | 10:02:40 | 14:46:02 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 1023.66, 'reason': '진입', 'hint_source': '', 'atr': 2.1514, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qty… |
| `ScalerRefresh` | 16 | 09:22:00 | 14:55:00 | 5분 누적 수익률 +0.527% (임계 ±0.442%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `SHAP` | 14 | 13:04:02 | 15:07:01 | 슬로우 감지 1181ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림) |
| `PipePerf` | 12 | 09:00:01 | 12:11:04 | total=1059ms | S0=2ms S1=16ms S2=0ms S3=0ms S4=92ms S5=772ms S6=157ms S7=14ms S8=4ms |
| `Health` | 12 | 09:00:01 | 14:51:00 | level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0 |
| `CB③-P4` | 12 | 11:00:00 | 14:19:00 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |

**채널** — `SYSTEM`×3480, `HEALTH`×13

**컴포넌트 상위 15** — `ChartDBG`×2799, `LiveDBG`×333, `OptionFlowChart`×77, `Peter2`×31, `ChejanFlow`×27, `ChejanMatch`×27, `PendingOrder`×24, `ScalerRefresh`×16, `SHAP`×14, `Health`×13, `PipePerf`×12, `CB③-P4`×12, `CB⑤`×10, `ExitCooldown`×10, `EntryFillFlow`×8

### `logs/20261012_SYSTEM.log` — 1.0MB · 6878행 · 최종 15:47:14

- 형식 평문 · 시각 인식 6849행 · INFO=6849, PLAIN=29

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=15168 | 행감지=30s all_threads=True
2026-10-12 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.42s | predictions=0.05s trades=0.20s daily_stats=0.01s shap=0.02s raw_data=0.10s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-12 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-12 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-12 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-12 15:46:06 [INFO] SYSTEM: [SessionBackfill] 08:45 개장 체결 보정 ts=2026-10-12 08:45:00 rt O=1036.46/V=407 → chart O=1037.12/V=655
2026-10-12 15:46:06 [INFO] SYSTEM: [SessionBackfill] 2026-10-12~2026-10-12 chart=411 existing=408 inserted=3 open_fixed=1 mismatch=6
2026-10-12 15:47:14 [INFO] SYSTEM: [System] 자동 종료 실행
2026-10-12 15:47:14 [INFO] SYSTEM: 미륵이 자동 종료
2026-10-12 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
```

</details>

**채널** — `SYSTEM`×6849

**컴포넌트 상위 15** — `CybosInvestorRaw`×1576, `CybosRT-TICK`×1310, `PumpGuard`×492, `BAR-CLOSE`×408, `CVD-ANCHOR`×408, `CybosRT-ROLLOVER`×407, `TickUI`×406, `S6Detail`×368, `PipePerf`×368, `System`×112, `OptionChain`×84, `OptionBook`×80, `MicroRegime`×74, `BalanceUI`×71, `RegimeFingerprint`×70

### `logs/20261012_SIGNAL.log` — 561.3KB · 4902행 · 최종 15:40:15

- 형식 평문 · 시각 인식 4902행 · WARNING=2156, INFO=2746

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.411
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.403
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.399
2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.407
  …
2026-10-12 15:10:28 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-10-12 15:40:15 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-10-12 15:40:15 [INFO] SIGNAL: [TrendGate][섀도] 조건A(CVD 동조) enabled=False — 관측 226분 중 섀도만 활성 UP 0분(0.0%) / DN 33분(14.6%). 켜면 이만큼 min_conf 완화가 늘어난다.
2026-10-12 15:40:15 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-10-12 age=29m extreme=576 refresh=33 grade_x=47 cb3=0
2026-10-12 15:40:15 [INFO] SIGNAL: [ModelHealth] date=2026-10-12 앙상블유효가동률=72.1% | 파이프라인 226분 | ConstOut 6회/12분 {"3m": {"events": 4, "minutes": 8}, "5m": {"events": 2, "minutes": 4}} | WeightCollapse 51분 | 장중재학습 1회 | CB③ ready 119분/226분 (53%) (리셋 0회, 표본손실 0건)
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1584 | 09:00:01 | 14:58:01 | 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 192 | 09:01:00 | 14:58:00 | 1m 극단 z-score 7개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 168 | 09:01:00 | 15:02:00 | ts=09:00 horizon=1m age=1m max_z=+5.18(volume_acceleration) extreme=7 adj=5 |
| `Checklist` | 95 | 09:06:00 | 15:09:00 | 신뢰도 미달 36.9% < 38.1% → 강제 X등급 |
| `WeightCollapse` | 85 | 09:07:00 | 15:07:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 18 | 08:45:09 | 08:45:09 | 1m CORE 'vwap_position' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| `ConstOut` | 11 | 10:14:00 | 13:48:00 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `MetaGate` | 3 | 09:47:00 | 14:59:00 | meta_conf 5회 연속 과소 → 다음 배치 재학습 대기 (streak=5) |

**채널** — `SIGNAL`×4902

**컴포넌트 상위 15** — `ScalerFloor`×1644, `SIGNAL`×736, `Ensemble`×367, `ZeroDiag`×363, `FQAdj`×287, `Model`×222, `MetaGate`×210, `ScalerMonitor`×169, `Checklist`×108, `ATR-Horizon`×93, `WeightCollapse`×85, `MicroRegime`×74, `TrendGate`×60, `InstabilityGate`×59, `ScalerRefresh`×57

### `logs/20261012_LEARNING.log` — 386.8KB · 3324행 · 최종 15:40:15

- 형식 평문 · 시각 인식 3324행 · WARNING=438, INFO=2886

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-12 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00133 auc=0.543 out_max=0.3734 (n=110) → 보정 재적용
  …
2026-10-12 15:40:15 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-10-12 15:40:15 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-12 15:40:15 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-10-12 15:40:15 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-10-12 15:40:15 [INFO] LEARNING: [Sigma] EOD sigma_20=0.11062% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 144 | 08:40:50 | 14:46:00 | 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 127 | 08:40:50 | 12:55:00 | 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 54 | 08:40:50 | 14:12:00 | 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 49 | 08:40:51 | 11:22:57 | 하한 도달불가 — out_max=0.3005 < conf_floor=0.3300 (span=0.00088 auc=0.534 out_max=0.3005, 기저율=0.3000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 45 | 08:40:51 | 11:22:57 | 축퇴 감지 — span=0.00044 auc=0.490 out_max=0.3003 (기준 auc<0.53 and span<0.020, 기저율=0.3000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 13 | 08:40:51 | 11:22:57 | 축퇴 감지 — span=0.00081 auc=0.517 out_max=0.2629 (기준 auc<0.53 and span<0.020, 기저율=0.2625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 3 | 08:40:59 | 11:22:58 | 복원한 보정기가 축퇴 상태 — span=0.01232 auc=0.468 out_max=0.4068 (n=3107) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |
| `Buffer-Timing` | 1 | 12:11:01 | 12:11:01 | total=856ms raw_fetch=9ms pred_select=829ms pred_update=7ms pred_insert=6ms verified=3 |
| `Retrain` | 1 | 15:40:15 | 15:40:15 | DB pruning 실패 — 삭제 롤백(반영 0행, 시도 26670행): database table is locked |
| `DriftAdjuster` | 1 | 15:40:15 | 15:40:15 | 3일 연속 정확도 50% 미만 — alpha 0.01000 유지, ALPHA_MAX 포화 (연속 21일) |

**채널** — `LEARNING`×3324

**컴포넌트 상위 15** — `LEARNING`×1143, `SGD`×369, `sigma`×329, `Calibration:30m`×286, `Calibration:1m`×250, `Bias⚠`×232, `Bias`×115, `Calibration:3m`×104, `OnlineLearner`×104, `Calibration:10m`×95, `Calibration:5m`×84, `MetaConf`×65, `ScalerWarmup`×39, `BiasReset`×35, `Calibration:15m`×23

### `logs/20261012_HEALTH.log` — 4.2KB · 28행 · 최종 14:52:00

- 형식 평문 · 시각 인식 28행 · CRITICAL=1, WARNING=12, INFO=15

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0
2026-10-12 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=591ms | quality=1.00 | cache_age=111s | exceptions_10m=0
2026-10-12 09:14:02 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1776ms | quality=1.00 | cache_age=155s | exceptions_10m=0
2026-10-12 09:15:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=356ms | quality=1.00 | cache_age=30s | exceptions_10m=0
2026-10-12 09:29:01 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 374ms (표본 20분)
  …
2026-10-12 13:17:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=359ms | quality=1.00 | cache_age=59s | exceptions_10m=4 | exc_tags=[Peter2]×3 [SHAP]×1
2026-10-12 14:02:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=303ms | quality=1.00 | cache_age=183s | exceptions_10m=2 | exc_tags=[SHAP]×2
2026-10-12 14:03:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=330ms | quality=1.00 | cache_age=58s | exceptions_10m=1 | exc_tags=[SHAP]×1
2026-10-12 14:51:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=301ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
2026-10-12 14:52:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=309ms | quality=1.00 | cache_age=59s | exceptions_10m=3 | exc_tags=[SHAP]×2 [ExitCooldown]×1
```

</details>

**ERROR 이상**

| level | tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|---|
| CRITICAL | `Health` | 1 | 09:36:06 | 09:36:06 | level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1 |

<details><summary>CRITICAL/Health 원문 1건</summary>

```
2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 12 | 09:00:01 | 14:51:00 | level=WARNING degraded=OFF | latency=1059ms | quality=1.00 | cache_age=51s | exceptions_10m=0 |

**채널** — `HEALTH`×28

**컴포넌트 상위 15** — `Health`×25, `HealthTrend`×3

### `logs/retrain_eod_20261012.log` — 26.1KB · 166행 · 최종 15:53:39

- 형식 평문 · 시각 인식 166행 · WARNING=23, INFO=143

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 15:50:02,708 [INFO] EOD_RETRAIN: =======================================================
2026-10-12 15:50:02,709 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-12 15:50:02,709 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-12 15:50:02,709 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-12 15:50:02,709 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-12 15:53:39,381 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0446 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-12 15:53:39,382 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0866 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-12 15:53:39,385 [INFO] SIGNAL: [ScalerRefresh] ts=15:53 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-10-12 15:53:39,389 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-12 15:53:39,391 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardGhost` | 12 | 15:50:36 | 15:52:41 | 1m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-10-12 10:51:00까지)인데 acc.txt=0.4695는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |
| `GuardFair` | 6 | 15:50:36 | 15:52:41 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1625봉(88%)이 현행 학습구간 (현행 cutoff=2026-10-12 10:51:00 ≥ 홀드아웃 시작=2026-10-01 12:48:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-12 10:51 >= holdout_start=2026-10-01 12:48 (source=intraday) — 판정 보류 (구모델 pkl mtime=2026-1… |
| `RegularFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-12 | 최신 2026-10-08 · 기준 5거래일. 복구: python scripts/collect_regular_futures.py --from 20261012 --to 20261012 |
| `OptionFlowFresh` | 1 | 15:50:03 | 15:50:03 | 결손 1일 — 2026-10-02(최신봉 15:34) | 기준 4거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\<YYYYMMDD>_OPTION_BACKFILL.log |
| `BackfillFilter` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 20098/44078 제외 (418차 결정 1) — 남은 23980행 |
| `UnitMismatch` | 1 | 15:50:14 | 15:50:14 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23980행 제외 (559차 P1'-2) — 남은 22534행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 15:53:38 | 15:53:38 | 백필 0행 제외 — 필터가 무효일 수 있다. 20091행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `LEARNING`×74, `SIGNAL`×55, `EOD_RETRAIN`×27, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×48, `Retrain`×21, `EOD_RETRAIN`×14, `GuardGhost`×12, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `LEVELS`×4, `RegimeFingerprint`×4, `WaitDC`×2

### `logs/retrain_intraday_20261012_093420.log` — 5.7KB · 43행 · 최종 09:35:03

- 형식 평문 · 시각 인식 43행 · WARNING=2, INFO=41

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-12 09:34:20,955 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-12 09:34:20,955 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-12 09:34:20,956 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-12 09:34:20,956 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-12 09:34:20,956 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7924fd37.json
  …
2026-10-12 09:35:03,964 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-12 09:35:03,965 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-12 09:35:03,965 [INFO] LEARNING: [Retrain] 완료 | 39.9초 | 성공=6/6 호라이즌
2026-10-12 09:35:03,966 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 43.0s 데이터=4800행
2026-10-12 09:35:03,968 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_7924fd37.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 09:34:34 | 09:34:34 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 20444/44090 제외 (418차 결정 1) — 남은 23646행 |
| `UnitMismatch` | 1 | 09:34:34 | 09:34:34 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23646행 제외 (559차 P1'-2) — 남은 22200행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×28, `RETRAIN_INTRADAY`×7, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×21, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) — **엔진** | 2 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 5 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 5 |
| 차단(`[차단]`) | 47 |
| 사이저 호출(`[Sizer]`) | 4 |

### 포지션 5건 · 승 2 (40%) · 합계 -6.91pt (-360,416원)  ※ 레그 7행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 10:02:40 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.98 | -200,945 | 하드스톱(틱) |
| 10:17:03 (추정귀속) | 추정 | LONG | 1 | — | 1 | -3.76 | -189,939 | 하드스톱(틱) |
| 12:47:00 | 엔진 | SHORT | 3 | 5m | 2 | +1.47 | +68,218 | 하드스톱 |
| 14:21:30 (추정귀속) | 추정 | LONG | 1 | — | 1 | -1.86 | -94,922 | 하드스톱(틱) |
| 14:42:00 | 엔진 | SHORT | 2 | 3m | 2 | +1.22 | +57,172 | 하드스톱(틱) |

**출처별 소계** — 엔진 2건 +125,390원 · 추정 3건 -485,806원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

> ⚠ **(추정귀속) 3건** — `[Position] 진입` 로그가 없어 `[체결진입]`(FLAT→보유) 으로 조립한 포지션이다. **손익·수량은 체결 실측이라 정확하지만** `hz`(진입 호라이즌)·등급은 그 줄에 없어 `—` 다. 이 경로가 나타났다는 것 자체가 **Chejan 선행 체결 레이스의 지문**이므로 이상점 후보로 볼 것(2026-08-25 유령 하드스톱 1-9와 같은 날 같은 포지션).

**청산 레그 7행** (부분청산 2 · 전량청산 5)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 10:09:22 | 전량 | 1 | -3.98 | -200,945 | 하드스톱(틱) |
| 10:19:40 | 전량 | 1 | -3.76 | -189,939 | 하드스톱(틱) |
| 12:49:44 | 부분 | 1 | +0.85 | +40,739 | TP1 부분청산 33% |
| 12:50:01 | 전량 | 2 | +0.31 | +27,479 | 하드스톱 |
| 14:34:08 | 전량 | 1 | -1.86 | -94,922 | 하드스톱(틱) |
| 14:42:37 | 부분 | 1 | +0.63 | +29,586 | TP1 부분청산 33% |
| 14:46:02 | 전량 | 1 | +0.59 | +27,586 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×4, `TP1 부분청산 33%`×2, `하드스톱`×1

> 최종 청산이 하드스톱·손절 계열인 포지션 5/5건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -360,416 = 포지션합 -360,416 → OK · `[청산 완료]` 5건 = 조립 포지션 5건 → OK

### CB③ 판정 가능 시간 — **119분 / 226분 (53%)**

acc30m 버퍼 리셋 0회 · 그때 버린 표본 0건 (스케일러 재적합이 CB③ 표본을 되감는다)

> `acc30m` 값이 낮은데 HALT 가 없다면 먼저 이 값을 보라 — ready 가 아닌 분에는 CB③이 **판정 자체를 하지 않는다**. 전환기준 ⑥(CB③ 기준 호라이즌 교체)을 논의하려면 임계보다 이 가용시간이 먼저다.

### 진입 2건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 12:47:00 | SHORT | 3 | 1014.54 | 5m | neutral |
| 14:42:00 | SHORT | 2 | 1007.22 | 3m | trend |

계약수 분포 — 2계약×1, 3계약×1

등급 분포 — `A급(원시C)`×1, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×2, `cvd`×1, `prev`×1, `time`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1, **3계약**×3

실제 진입 계약수 — **2계약**×1, **3계약**×1

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×4

### 차단 사유 47건 · 14종

| 건수 | 사유 |
|---|---|
| 31 | 등급X — 미통과 항목: 2_confidence |
| 3 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 청산 후 쿨다운 — 82초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 160초 후 재진입 가능 |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.2pt > ATR×5.0=9.8pt (시가=1033.20 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 1 | 청산 후 쿨다운 — 60초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 127초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 67초 후 재진입 가능 |
| 1 | JointGateBlock — meta=0.57 tox=0.70 joint=0.396 < 0.50 |
| 1 | 청산 후 쿨다운 — 61초 후 재진입 가능 |
| 1 | 청산 후 쿨다운 — 1초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×31, `3_vwap`×3, `4_cvd`×3, `6_foreign`×3, `7_prev_bar`×3, `11_countertrend`×3, `5_ofi`×2

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 12건

- `×1 [LEVELS]×1 [RESTART]×1` ×3
- `연속 손절 1회 (300초 창, 포지션 단위)` ×3
- `5분 진입 정지 | 파이프라인 5990ms — 처리 지연 (임계=5000ms)` ×2
- `일시 정지 해제 — 정상 복귀` ×2
- `일간 리셋 완료` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 24건 · 최대 7484ms · 5초 초과 3건

상위 — 7484ms, 6297ms, 5375ms, 4593ms, 4203ms, 3562ms, 3390ms, 3234ms

**5초 초과 건 — CB⑤ 미계상 잔차** (`CB_PIPE_PAUSE_MS=5_000`)

_대조값은 같은 분과 **직전 분** `PipePerf total` 중 **큰 쪽**이다 — 잔차를 과대평가하지 않기 위한 보수적 선택이다(정지가 분 경계를 넘을 수 있다)._

| 시각 | 메인 정지 | 같은 분 `PipePerf total` | 잔차(CB⑤ 사각) |
|---|---|---|---|
| 09:36:07 | 7484ms | 5990ms | **1494ms (20%)** |
| 12:11:05 | 5375ms | 3416ms | **1959ms (36%)** |
| 15:46:12 | 6297ms | **미측정** | — |

> ⚠ **CB⑤ 미발동이 결함이 아니다.** CB⑤는 파이프라인 경과시간에 걸리고, 위 정지는 메인 스레드 전체 정지시간이라 **단위가 다르다**. 잔차가 큰 건은 정지의 대부분이 S0~S8 밖(COM 콜백·Qt 페인트·다른 타이머)에서 났다는 뜻이며, 그 구간은 CB⑤도 FZ-1(180초)도 보지 않는다. 482차 F-3 섀도 계측(`MAIN_THREAD_STALL_*`)이 이 구간을 2주 관찰한다.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261012_WARN.log`
```
--- ConfFloorGuard ×1(표본)
15:40:19 2026-10-12 15:40:19 [WARNING] SYSTEM: [경보] mc-conf 괴리: 금일 진입후보(conf≥mc) 14분 < 하한 25분 — 최근 5거래일 평균 38분/일. mc는 자동 조정하지 않음(사용자 판단 필요). | ConfFloorGuard 도달가능 0분 · 도달불가 0분 · 재지않음 226분
--- [CB] ×6(표본)
09:36:06 2026-10-12 09:36:06 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5990ms — 처리 지연 (임계=5000ms)
09:36:06 2026-10-12 09:36:06 [WARNING] SYSTEM: [CB] 5분 진입 정지 | 파이프라인 5990ms — 처리 지연 (임계=5000ms)
09:37:00 2026-10-12 09:37:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=409ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[CB]×1 [LEVELS]×1 [RESTART]×1
10:09:22 2026-10-12 10:09:22 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×8(표본)
10:09:22 2026-10-12 10:09:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:12:22)
10:09:22 2026-10-12 10:09:22 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:12:22)
10:19:40 2026-10-12 10:19:40 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:22:40)
10:19:40 2026-10-12 10:19:40 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:22:40)
--- [SHAP] 슬로우 ×8(표본)
13:04:02 2026-10-12 13:04:02 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1181ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:15:01 2026-10-12 13:15:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1391ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:26:01 2026-10-12 13:26:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1176ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:52:01 2026-10-12 13:52:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 946ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
--- level=CRITICAL ×1(표본)
09:36:06 2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
--- 메인 스레드 블로킹 ×8(표본)
08:41:12 2026-10-12 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4203 band=INFO since_pipe_s=NA
09:00:02 2026-10-12 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.1
09:05:02 2026-10-12 09:05:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2141ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2141 band=INFO since_pipe_s=0.0
09:14:03 2026-10-12 09:14:03 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3234ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=3234 band=INFO since_pipe_s=0.1
```

### `logs/20261012_SYSTEM.log`
```
--- CIRCUIT ×2(표본)
09:36:06 2026-10-12 09:36:06 [INFO] SYSTEM: [Notify] 🚨 [09:36:06] [미륵이] Circuit Breaker 발동!
09:36:06 2026-10-12 09:36:06 [INFO] SYSTEM: [Notify] 🚨 [09:36:06] [미륵이] Circuit Breaker 발동!
--- ConstOut ×8(표본)
09:36:05 2026-10-12 09:36:05 [INFO] SYSTEM: [DynMC] ConstOut 고착 conf 제외: [0.85] → 233건 제거 (잔여 1257건)
10:14:00 2026-10-12 10:14:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4533) | 앙상블 제외는 유지
10:22:00 2026-10-12 10:22:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.5399) | 앙상블 제외는 유지
10:34:01 2026-10-12 10:34:01 [INFO] SYSTEM: [ConstOut] 5m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4567) | 앙상블 제외는 유지
--- HALT ×1(표본)
15:40:15 2026-10-12 15:40:15 [INFO] SYSTEM: [CB③계측] 조건성립 41분 / 판정가능 119분 / 파이프라인 226분 · 그 창 진입 0포지션 · 손익 +0원 (임계 acc30m<0.28 · HALT 차단은 한시예외로 비활성)
--- PSI ×8(표본)
09:00:00 2026-10-12 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:05:00 2026-10-12 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:11:00 2026-10-12 09:11:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
09:16:00 2026-10-12 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.001 level=0 (heartbeat)
--- [CB] ×4(표본)
09:42:00 2026-10-12 09:42:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
09:42:00 2026-10-12 09:42:00 [INFO] SYSTEM: [CB] 일시 정지 해제 — 정상 복귀
15:40:15 2026-10-12 15:40:15 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:15 2026-10-12 15:40:15 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [ExitStageRecon] ×1(표본)
15:40:15 2026-10-12 15:40:15 [INFO] SYSTEM: [ExitStageRecon] 오늘 TRAIL_AFTER_TP1 2레그 / 2포지션 중 TP 이벤트 대응 2 · 단일계약 보호전환(설계) 0 · 미대응 0
--- [SchedForceExit] ×1(표본)
15:11:06 2026-10-12 15:11:06 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=2회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:20 2026-10-12 15:40:20 [INFO] SYSTEM: [Shutdown] intent=daily_close keep_alive=False files=2
15:47:14 2026-10-12 15:47:14 [INFO] SYSTEM: [Shutdown] intent=auto_shutdown keep_alive=False files=2
--- 자동 종료 ×6(표본)
15:40:20 2026-10-12 15:40:20 [INFO] SYSTEM: [Notify] ℹ️ [15:40:20] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:20 2026-10-12 15:40:20 [INFO] SYSTEM: 자동 종료 지연 — 당일 마감구간 보충(15:46) 대기 399초
15:40:20 2026-10-12 15:40:20 [INFO] SYSTEM: 자동 종료 예약 — 414초 후 Qt 이벤트 루프 종료
```

### `logs/20261012_SIGNAL.log`
```
--- ConstOut ×8(표본)
10:14:00 2026-10-12 10:14:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.2500 dir=-1)
10:14:00 2026-10-12 10:14:00 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
10:15:00 2026-10-12 10:15:00 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
10:22:00 2026-10-12 10:22:00 [INFO] SIGNAL: [ConstOutShadow] 3m 불일치 live=STUCK raw=- | live(range=0.0000 dir=+1) raw(range=0.1110 dir=+0)
--- WeightCollapse ×8(표본)
09:07:00 2026-10-12 09:07:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:10:00 2026-10-12 09:10:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:13:00 2026-10-12 09:13:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
09:16:01 2026-10-12 09:16:01 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=RISK_ON [WeightCollapse]
--- 기동 복원 ×8(표본)
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.423
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.411
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.403
08:40:42 2026-10-12 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.399
--- 안전망 ×8(표본)
09:07:00 2026-10-12 09:07:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:00 2026-10-12 09:10:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:13:00 2026-10-12 09:13:00 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:01 2026-10-12 09:16:01 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20261012_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00071 auc=0.521 out_max=0.3629 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00050 auc=0.467 out_max=0.4128 (기준 auc<0.53 and span<0.020, 기저율=0.4125 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00174 auc=0.445 out_max=0.3883 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:40:50 2026-10-12 08:40:50 [INFO] LEARNING: [Calibration:30m] 축퇴 해소 — span=0.00133 auc=0.543 out_max=0.3734 (n=110) → 보정 재적용
```

### `logs/20261012_HEALTH.log`
```
--- [CB] ×2(표본)
09:37:00 2026-10-12 09:37:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=409ms | quality=1.00 | cache_age=180s | exceptions_10m=3 | exc_tags=[CB]×1 [LEVELS]×1 [RESTART]×1
09:38:00 2026-10-12 09:38:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=305ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[CB]×1 [LEVELS]×1 [RESTART]×1
--- [ExitCooldown] ×3(표본)
10:29:00 2026-10-12 10:29:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=288ms | quality=1.00 | cache_age=180s | exceptions_10m=1 | exc_tags=[ExitCooldown]×1
14:51:00 2026-10-12 14:51:00 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=301ms | quality=1.00 | cache_age=182s | exceptions_10m=2 | exc_tags=[ExitCooldown]×1 [SHAP]×1
14:52:00 2026-10-12 14:52:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=309ms | quality=1.00 | cache_age=59s | exceptions_10m=3 | exc_tags=[SHAP]×2 [ExitCooldown]×1
--- level=CRITICAL ×1(표본)
09:36:06 2026-10-12 09:36:06 [CRITICAL] HEALTH: [Health] level=CRITICAL degraded=OFF | latency=5990ms | quality=1.00 | cache_age=126s | exceptions_10m=2 | exc_tags=[LEVELS]×1 [RESTART]×1
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261012_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 10:00 | 장중 초반 | 8 | 10:02:40 [WARNING] entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=LONG qty=1 entry=1023.70 — 진입 경로가 파라미터를 넘기지 … |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:15 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261012_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 14 | 08:41:08 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:51:32 [WARNING] ChallengerPanel.refresh slow 297ms |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 147 | 09:54:00 [WARNING] paintEvent slow 57.5ms | size=1793x930 candles=69 grid=21.4 spans=0.6 candles=7.4 dir=0.2 regime=0.8 markers=… |
| 12:00 | 장중 중간점 | 109 | 11:54:01 [WARNING] _tick_header 간격 2281ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2281 band=… |
| 14:00 | 장중 후반 · 장중 재학습 | 106 | 13:54:02 [WARNING] paintEvent slow 91.3ms | size=1793x930 candles=308 grid=24.3 spans=1.9 candles=20.7 dir=1.0 regime=5.3 marker… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 104 | 15:04:00 [WARNING] paintEvent slow 109.1ms | size=1793x902 candles=200 grid=25.3 spans=2.6 candles=20.4 dir=0.8 regime=5.0 marke… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 102 | 15:12:00 [WARNING] paintEvent slow 120.7ms | size=1793x902 candles=200 grid=12.3 spans=4.6 candles=22.5 dir=0.8 regime=6.4 marke… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 22 | 15:34:00 [WARNING] paintEvent slow 97.9ms | size=1793x930 candles=408 grid=12.2 spans=3.0 candles=29.4 dir=1.3 regime=5.6 marker… |
| 15:47 | EOD 재학습(py310_64) 완료 | 9 | 15:46:06 [WARNING] OHLCV 불일치 ts=2026-10-12 09:34:00 cols=['open', 'high', 'volume'] existing_source=rt |

- 이 로그 생존구간: 08:41 ~ 15:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261012_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 97 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=15168 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 135 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 193 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 223 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 202 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | 장중 후반 · 장중 재학습 | 219 | 13:54:01 [INFO] code=A056B from=13:53 to=13:54 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 191 | 15:04:00 [INFO] code=A056B from=15:03 to=15:04 |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 169 | 15:12:00 [INFO] code=A056B from=15:11 to=15:12 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 59 | 15:34:00 [INFO] code=A056B from=15:33 to=15:34 |
| 15:47 | EOD 재학습(py310_64) 완료 | 6 | 15:43:06 [INFO] 대기 중 | 장 마감 후 — 내일 08:45 매크로 수집 재개 | 레짐=NEUTRAL | 포지션=FLAT | 15:43:06 |

- 이 로그 생존구간: 08:40 ~ 15:47

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261012_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:09 [WARNING] 1m CORE 'vwap_position' raw_std≈0(0.0473) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 128 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 225 | 09:00:01 [WARNING] 1m 'macro_vix' scale=0.0014 → floor=0.10 적용 (z-score 폭발 방지) |
| 10:00 | 장중 초반 | 212 | 09:54:00 [WARNING] 신뢰도 미달 39.9% < 47.0% → 강제 X등급 |
| 12:00 | 장중 중간점 | 96 | 11:55:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 14:00 | 장중 후반 · 장중 재학습 | 163 | 13:55:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['10m', '15m', '3m', '5m'] 중 미배포=['10m', '15m', '3m', '5m'] → flat_score=1.0 안전망 발동 (ac… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 52 | 15:04:00 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 4 | 15:40:15 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261009 | 18:33 | 로그 본문 |
| 20261008 | 15:43 | 로그 본문 |
| 20261007 | 20:26 | 로그 본문 |
| 20261006 | 15:47 | 로그 본문 |
| 20261005 | 09:41 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261012** | **15:47** | 로그 본문 |

- 델타 **+0분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 병행 세션
## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치: F-1 재진단 · G-1 리포트 append 마커)
## 2026-10-09 (MW0601 677차 — 피터2 백필: 실거래 개시 이전 손익을 손익추이·손익추이2 에 올린다)
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2: 위클리 원천 · 먼스리 만기주 기권 · 옵션 금액 단위) — 🟡 **구현 · 라이브 미배포(사다리 서버 재기동 대기)**
## 2026-10-10 (MW0601 679차 — 맥점 사다리 자동기동 예약작업)
## 2026-10-12 (MW0601 680차 — 장전 점검)
## 2026-10-12 (MW0601 668차 후속6–8 — 피터2 집행·오프셋·하트비트 + dev 배포)
## 2026-10-12 (MW0601 681차 — 장중 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
추가. 사용자 승인 후 장후 적용.
   - 검증: 장후 점검에서 사용자에게 09:33·11:22 재기동 의도 여부 직접 확인. `raw_candles` 09:33·11:22 영구결손 2봉은 재기동의 정상적 부산물(618차 기존 메커니즘)로 별도 조치 불필요.

2. **피터2 경로 진입 2건 — 기존 사안 재확인(함정① 확인, 신규 아님)**
   - 증상: 10:02:40 LONG 1계약(1023.66) → 10:09:22 하드스톱 청산(-200,945원), 10:17:03(추정) LONG 1계약 → 10:19:40 하드스톱 청산(-189,939원). 둘 다 `[Position] 진입` 로그 없이 체결 기록만으로 "(추정귀속)" 조립. 둘 다 "피터2"(외부 트레이더 트윗 추종 매매) 경로.
   - 원인: 이미 같은 날 다른 세션(668차 후속9)이 1차 진입의 손절가 미승계 원인(09:54 지시 대기가 `stop_before_entry`로 먼저 해제됨)과 CLOSED 사유 키 버그를 확인·수정(`e7f50c6`, 11:27 커밋)해 뒀다. `(추정귀속)` 표기 자체는 `_peter2_execute()`가 공용 `_execute_entry()`를 호출하는 구조라 기존 G-3(Chejan 선행 체결 레이스 로그누락, NEXT_TODO 기존 등록)과 같은 메커니즘으로 추정(확정 아님 — 2026-09-14 563차 장후가 "매번 같은 원인은 아니다"로 유보한 전례 있음).
   - 결정: 신규 Fix 등록 안 함(함정① — 이미 반영된 사안). 금액·수량 정합성만 확인(레그합 -390,884원 = 포지션합 -390,884원, OK). G-3 누적 사례로만 추가.
   - Why: 함정① 방지 — grep 결과 손절가 미승계·CLOSED 키 버그 둘 다 오늘 오전 이미 커밋됨을 확인.
   - How to apply: 해당 없음(이미 적용 완료, 다른 세션 소관).
   - 검증: 장후 DB 대사(`ensemble_decisions`·`trades`)에서 금액 재확인 권고(O-t1과 같은 장후 작업에 묶어서).

**추가**: CB⑤ 1회 발동(09:36:06, 5990ms 지연 → 5분 진입정지 → 09:42:00 정상복귀) — 재기동 직후 차트 데이터 보충(`[LEVELS]`)과 브로커 포지션 재동기화가 겹친 것으로, 설계대로 작동한 정상 안전장치(신규 결함 아님). 매분 루프 커버리지 09:00~12:26 207/207분(100%), 공백 없음. 6개 호라이즌(1·3·5·10·15·30분) 예측·채점 전부 정상 발행. CB②·CB③·설정 불변식 전부 일치. 엔진 자체 ML 진입은 오늘 0건(신뢰도 미달 게이트가 16/23건 차단 — 설계대로 작동).

**[668차 후속11 `2ad034b`] 피터2 해석 결함 3건 + 파일 교체 재시도** (10-12 장중 실측)
14:20 「단타는 1014깨지면 다시 매수하더라도 무조건 손절해야」를 매수 지시로 오독 → 실주문(롱 1011.62, −1.86pt —
14:23 그의 「1015 돌파 매수·손절 1012」와 우연히 같은 방향이 돼 손절선 일치). 14:46 「1007 체결 안된사람은 1009부근 매수」의
1009 지시 누락 · 14:47 「1007-1009 매수 체결」 구간을 1007 로만 읽음 → 마지막 거래 미추종.
수정: _NOT_ORDER 에 더라도|해야(「깨지면·이탈시」는 「965돌파시 매수 958이탈시 손절」 정상 지시 회귀라 제외 — _raw 702건
재해석 대조로 실측) · 체결 문장을 「안된/못한 사람·분」 앞에서 분할 · _RANGE 4자리 전체 표기 + fill lo/hi + 대기 구간 확장 ·
_arm 손절 승계 일반화 · collector/state/feed.json os.replace WinError 5(10-12 3회) 재시도.
**배포**: dev 체리픽 `74b7d3c`(충돌 0, 피터 계열 95 passed).

**[668차 후속12 `9e88005`] 과금 채널 PC 고정.** 사용자 지시: «손익 추이» = CYBOS 0.0098% · «손익 추이2» = 0.0019%(CREON 반사실).
원인 실측: C:\CREON\STARTER\ncstarter.log 10-12 08:42 > C:\Daishin\STARTER 08:35 → 감지 CREON → trades.commission_rate_used
1.9e-05 (**10-08 9행 · 10-12 7행**), 반사실 배수 1.000. `_PC_CHANNEL_PIN {MW0601: CYBOS, MW0602: CREON}`(env 다음·스타터 앞).
**배포**: dev 체리픽 `94aaa20`(test_495 충돌 — v9 고유 테스트 제외). MW0602 는 동작 변화 없음.
⚠ **미정정**: 10-08·10-12 행 수수료(실제의 1/5.16). 정정하려면 trades.db 백업 + strategy_events METRIC_REDEFINITION 마커 필요 — 사용자 결정 대기.
⚠ 반영은 재기동 후 — 지금 프로세스는 CREON 요율로 떠 있다.

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-08 (MW0601 672차 — 671차 후속 장후 자동조치)
## 2026-10-08 (MW0601 672차 — 신동2 학습 사이클)
## 2026-10-09 (MW0601 673차 — 장전 점검)
## 2026-10-09 (MW0601 674차 — 장중 점검)
## 2026-10-09 (MW0601 676차 — 675차 후속 장후 자동조치)
## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2)
## 2026-10-12 (MW0601 680차 — 장전 점검)
## 2026-10-12 (MW0601 681차 — 장중 점검)
```

미완료 체크박스 **3100건** (끝에서 30건)
```
- [ ] **G-1(1-1 병행 발화 대응)**: 점검 리포트 append 직전 세션별 생존 마커(`<PC>-<날짜>.lock`, 타임스탬프 포함, 2시간 초과 시 무시) 도입 검토 — 오늘 장전·장중 예약이 12초 차이로 병행 발화했으나 결과 우연히 무해(둘 다 휴장일 판정). 거래일 재발 시 리포트 append 순서 꼬임 위험.
- [ ] **O-p1(2026-10-07 669차 등록, 재이월)**: 개장전(08:48·08:54) 2단 자동 재시작 재현 여부 — 10/9는 휴장일이라 관측 기회 없음. **10/12(월) 장전으로 이월.**
- [ ] **1-1(2026-10-07 669차 등록, 재이월)**: 위와 같은 원인조사(런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 직접 Windows 이벤트 뷰어/작업 관리자 확인 필요) — 10/9 관측 기회 없음. **10/12 장전으로 이월.**
- [ ] **O-t1(2026-10-08 672차 등록, 재이월)**: `trades.db`의 `commission_rate_used`가 CYBOS(`9.8104e-05`)로 정상 복귀했는지 확인 — 10/9는 거래 자체가 없어 확인 대상 없음, 08:45 이후 라이브 DB 전수 스캔 금지 구간이기도 해 이번 세션 미실행. **10/12 거래 발생 이후…
- [ ] **O-t2(2026-10-08 672차 등록, 재이월)**: "원인불명 조용한 종료" 재현 누적 관찰 — 10/9는 시스템 미기동으로 관측 대상 없음. **10/12로 이월.**
- [ ] 미커밋 변경 96건(실질 12건) 정리 — `docs/정기점검/금요일점검/MW0601/` 삭제 12건이 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 — 저장소 정본 `rev: 2026-09-07`(538차) 대비 앱 사본이 `rev: 2026-08-26e`(499차)로 낡음. `save_skill overwrite: true` 필요(이 PC, MW0601 한정 — 함정③).
- [ ] O-i1 (신규, 다음 거래일 판정): 2026-10-12(월) 장전·장중 예약작업이 각자 정해진 시각 근처(±30분)에 발동하는지 확인. 지연 없으면 1-1 ✅해소, 재발하면 `logs/claude_resume_*.log` 감시 스크립트·원격 기기 브리지 연결 상태 원인조사 착수.
- [ ] G-2 (고도화, 이번 주): `collect_evidence.py` §2(병행 세션 확인)에 "예약작업 예정 시각 대비 실제 fired_at 지연"을 자동으로 찍는 계측 추가(현재는 수집기가 `list_triggers` API에 접근하지 않아 수동 대조만 가능). 지연이 30분 이상이면 §11 자동 적신호로 승격.
- [ ] (절차 개선, 비승인 필요 — 기술부채) 대용량 한글 텍스트를 리눅스 샌드박스 세션에서 device에 쓸 때 base64를 모델이 직접 옮겨적는 방식은 1바이트 오기 위험이 있음(2026-10-09 674차에서 실제 발생·즉시 발견·수정함). 앞으로 `device_commit_files` + `cat >> ` 패턴으로 바꿀 것 — DECISIO…
- [ ] **G-2(674차) 이월** — 예약 fired_at 원천 미정(수집기가 예약 목록에 접근 불가). 원천(예: 예약 세션 첫 줄에 발화시각 기록 → `data/dailycheck_markers` 의 `started_at` 활용 가능)부터 정할 것. G-1 마커의 `started_at`이 사실상의 fired_at 근사치가 될 수 있다 — 예정시…
- [ ] 1-2 처분: 10/12 장전 점검에서 오진으로 ✅해소 처리(로그 `(designed rc=…)` 줄 확인).
- [ ] 앱 저장 스킬 사본 갱신 시 §5-2 마커 규약이 들어간 판으로 저장(사용자 몫).
- [ ] 10/12 08:45 전 사다리 서버 재기동(`MAEKJEOM_LADDER.bat`) — 모듈 캐시(`_SD2`) 때문에 재기동해야 v2 가 화면에 뜬다. 신동2 예약작업은 실행마다 새 프로세스라 자동 반영.
- [ ] 10/12 장전 신동2 실행 로그에서 `위클리[…]` 표기 확인 — 10/12(월)은 월위클리(당일 만기) 여야 한다.
- [ ] v2 20거래일 채점(10/12–) 중 O1L·O2L·PX 동시 투표율 기록 — 금액이 PX 와 같은 표만 던지는지(개정 문서 §5 관찰, 판정 무관).
- [ ] MW0602(`dev`) 신동2 코드 보유 여부 — 같은 문제. 반영은 그 PC 결정.
- [ ] 1-1(원인조사, 669차 등록, 재이월 지속) — 런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 Windows 이벤트 뷰어/작업 관리자 직접 확인 필요. 오늘도 미착수.
- [ ] O-t1(2026-10-08 672차 등록, 3차 재이월) — `commission_rate_used` CYBOS 복귀 확인. 오늘 09:01 기준 체결 0건으로 확인 대상 없음. **2026-10-12 장후 점검에서 반드시 확정 판정(더 이상 이월 금지).**
- [ ] O-t2(2026-10-08 672차 등록, 3차 재이월) — "원인불명 조용한 종료" 재현 관찰. 오늘 하루 미종료로 판정 대상 없음, 장후로 이월.
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·F-15·F-16·G-3 — 전부 지속, 변화 없음(사용자 승인/선택 대기 — 중복 기재 생략, 680차 DECISION_LOG 참조).
- [ ] G-4(신규, 고도화 제안) — 오늘 장전 예약 발화 지연값(+39초, 목표 08:57 대비)을 G-2(674차, 발화지연 자동계측) 구현 시 정상 기준표본 1건으로 기록.
- [ ] 미커밋 변경 103건(실질 13건) 정리 확인 — `docs/정기점검/금요일점검/MW0601/` 12건 삭제가 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 정본 `rev: 2026-09-07`(538차) 대비 앱 사본 `rev: 2026-08-26e`(499차)로 낡음(10/9 673차부터 등록, 변화 없음). `save_skill overwrite: true` 필요(이 PC 한정).
- [ ] **1-2(신규)** 09:33·11:22 장중 재기동 2건이 사용자 의도적 조치였는지 확인 — 장후 점검에서 사용자에게 직접 질문. 확인되면 O-t2 "해소(설명됨)"로 닫고, 안 되면 "지속(진짜 원인불명)"으로 유지.
- [ ] **O-t1(4차 재이월 — 더 이상 이월 금지)**: 오늘 체결 2건 발생. 장후 점검에서 `trades.db`의 `commission_rate_used`가 CYBOS(`9.8104e-05`)인지 반드시 확정.
- [ ] **F-18(신규 제안, 비승인)**: 런처/엔진 종료 경로에 `[Shutdown] intent=user_close|watchdog|crash` 구분 로그 추가 — 1-2·O-t2류 재발 시 원인 구분을 로그만으로 가능하게. 적용 전 기존(618차 등)에 같은 제안이 이미 있는지 grep 확인 필요(미확인 상태).
- [ ] **G-5(신규, 고도화 제안)**: 수집기 §2(병행 세션 확인)에 "재기동 시각 ±5분 이내 당일 커밋 존재 여부" 자동 대사 열 추가 — O-t2류 오탐(의도적 재시작을 원인불명으로 오판) 감소.
- [ ] **1-1 범위 확장 확인**: 오늘 재기동 2회의 부팅 구간 모두에서 access violation 3건씩 재현(종전엔 "그날 첫 부팅만"으로 알려짐) — 표본 1일, 다음 재기동 발생일에 "매 재기동마다 재현"인지 재확인 필요.
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·F-15·F-16·G-3 — 전부 지속, 변화 없음(680차 DECISION_LOG 참조, 중복 기재 생략).
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 점검에서 오진으로 ✅해소 처리(로그 `(designed rc=…)` 줄 확인).
- [ ] 앱 저장 스킬 사본 갱신 시 §5-2 마커 규약이 들어간 판으로 저장(사용자 몫).

## 2026-10-10 (MW0601 678차 — 신동2 사전등록 개정 v2)
- [ ] 10/12 08:45 전 사다리 서버 재기동(`MAEKJEOM_LADDER.bat`) — 모듈 캐시(`_SD2`) 때문에 재기동해야 v2 가 화면에 뜬다. 신동2 예약작업은 실행마다 새 프로세스라 자동 반영.
- [ ] 10/12 장전 신동2 실행 로그에서 `위클리[…]` 표기 확인 — 10/12(월)은 월위클리(당일 만기) 여야 한다.
- [ ] v2 20거래일 채점(10/12–) 중 O1L·O2L·PX 동시 투표율 기록 — 금액이 PX 와 같은 표만 던지는지(개정 문서 §5 관찰, 판정 무관).
- [ ] MW0602(`dev`) 신동2 코드 보유 여부 — 같은 문제. 반영은 그 PC 결정.

## 2026-10-12 (MW0601 680차 — 장전 점검)

- [x] O-p1(2026-10-07 669차 등록, 10/9 재이월) 판정완료 — 개장전 2단 재시작 미재현(08:41:09 재기동 #1 1건뿐).
- [x] O-i1(2026-10-09 674차 등록) 장전 몫 판정완료 — 장전 예약 발화 08:57:39(목표 대비 +39초), 지연 없음. 장중 몫은 장중 점검이 판정.
- [ ] 1-1(원인조사, 669차 등록, 재이월 지속) — 런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 Windows 이벤트 뷰어/작업 관리자 직접 확인 필요. 오늘도 미착수.
- [ ] O-t1(2026-10-08 672차 등록, 3차 재이월) — `commission_rate_used` CYBOS 복귀 확인. 오늘 09:01 기준 체결 0건으로 확인 대상 없음. **2026-10-12 장후 점검에서 반드시 확정 판정(더 이상 이월 금지).**
- [ ] O-t2(2026-10-08 672차 등록, 3차 재이월) — "원인불명 조용한 종료" 재현 관찰. 오늘 하루 미종료로 판정 대상 없음, 장후로 이월.
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·F-15·F-16·G-3 — 전부 지속, 변화 없음(사용자 승인/선택 대기 — 중복 기재 생략, 680차 DECISION_LOG 참조).
- [ ] G-4(신규, 고도화 제안) — 오늘 장전 예약 발화 지연값(+39초, 목표 08:57 대비)을 G-2(674차, 발화지연 자동계측) 구현 시 정상 기준표본 1건으로 기록.
- [ ] 미커밋 변경 103건(실질 13건) 정리 확인 — `docs/정기점검/금요일점검/MW0601/` 12건 삭제가 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 지속 — 정본 `rev: 2026-09-07`(538차) 대비 앱 사본 `rev: 2026-08-26e`(499차)로 낡음(10/9 673차부터 등록, 변화 없음). `save_skill overwrite: true` 필요(이 PC 한정).

## 2026-10-12 (MW0601 681차 — 장중 점검)

- [ ] **1-2(신규)** 09:33·11:22 장중 재기동 2건이 사용자 의도적 조치였는지 확인 — 장후 점검에서 사용자에게 직접 질문. 확인되면 O-t2 "해소(설명됨)"로 닫고, 안 되면 "지속(진짜 원인불명)"으로 유지.
- [ ] **O-t1(4차 재이월 — 더 이상 이월 금지)**: 오늘 체결 2건 발생. 장후 점검에서 `trades.db`의 `commission_rate_used`가 CYBOS(`9.8104e-05`)인지 반드시 확정.
- [ ] **F-18(신규 제안, 비승인)**: 런처/엔진 종료 경로에 `[Shutdown] intent=user_close|watchdog|crash` 구분 로그 추가 — 1-2·O-t2류 재발 시 원인 구분을 로그만으로 가능하게. 적용 전 기존(618차 등)에 같은 제안이 이미 있는지 grep 확인 필요(미확인 상태).
- [ ] **G-5(신규, 고도화 제안)**: 수집기 §2(병행 세션 확인)에 "재기동 시각 ±5분 이내 당일 커밋 존재 여부" 자동 대사 열 추가 — O-t2류 오탐(의도적 재시작을 원인불명으로 오판) 감소.
- [ ] **1-1 범위 확장 확인**: 오늘 재기동 2회의 부팅 구간 모두에서 access violation 3건씩 재현(종전엔 "그날 첫 부팅만"으로 알려짐) — 표본 1일, 다음 재기동 발생일에 "매 재기동마다 재현"인지 재확인 필요.
- [x] O-p1·O-i1(장중 몫) — 둘 다 판정완료(✅해소). O-i1 전체 해소.
- [ ] F-1(538-4)·F-2·663-1(F-5)·663-2(F-7)·F-15·F-16·G-3 — 전부 지속, 변화 없음(680차 DECISION_LOG 참조, 중복 기재 생략).

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

### `data/dailycheck_markers/claude-20261012-intra-cowork-intra-20261012-1226.json` — 179B · 10-12 12:26:45
```json
{
 "pc": "claude",
 "date": "20261012",
 "phase": "intra",
 "session": "cowork-intra-20261012-1226",
 "pid": 6,
 "started_epoch": 1791775606.1705668,
 "started_at": "2026-10-12 03:26:46"
}
```

### `data/heartbeat_MW0601_20261012.json` — 244B · 10-12 15:46:45
```json
{
 "pid": 6396,
 "written_at": "2026-10-12T15:46:45",
 "beat_epoch": 1791787601.4668157,
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

### `data/peter_feed/_raw/2026-10-12.jsonl` — 7.3KB · 10-12 15:14:43
```json
JSONL 39행 ⏎ 첫: {"id": "2109435496904683987", "dt": "2026-10-12T00:06:28.000Z", "text": "1035 상방돌파시 매수. 손절가 1031", "seen_at": "2026-10-12T09:07:08+09:00", "src": "live"} | {"id": "2109436040171929972", "dt": "2026-10-12T00:08:38.000Z", "text": "1035 매수체결.", "seen_at": "2026-10-12T09:09:23+09:00", "src": "live"} | {"id": "2109439327327719926", "dt": "2026-10-12T00:21:41.000Z", "text": "오늘 튀면 죽 튀는 자리니까 청산가 크게 보고 대기", "seen_at": "2026-10-12T09:22:08+09:00", "src": "live"} ⏎ 끝: {"id": "2109521334263042287", "dt": "2026-10-12T05:47:33.000Z", "text": "1007-1009 매수 체결. 손절 1004- 오늘 마지막 도전.", "seen_at": "2026-10-12T14:47:42+09:00", "src": "live"} | {"id": "2109527458211082539", "dt": "2026-10-12T06:11:53.000Z", "text": "1012 청산", "seen_at": "2026-10-12T15:12:28+09:00", "src": "live"} | {"id": "2109528102770708533", "dt": "2026-10-12T06:14:27.000Z", "text": "1012 청산체결. \n\n5+4+3+3+3= 18p 손실\n\n5p ~3p 수익\n\n총 13p~15p 손실.\n\n오늘 아래꼬리 달고 올라올 자리라고 생각이 되는데.\n\n끝까지 밀어버리네요.\n\n고생하셨습니다.", "seen_at": "2026-10-12T15:14:43+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-12 15:53:39**

| 키 | 값 | 수집 대상일(2026-10-12)과 일치 |
|---|---|---|
| `date` | 2026-10-12 | 예 |
| `p8_last_success_date` | 2026-10-12 | 예 |
| `eod_retrain_ok_date` | 2026-10-12 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-12 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (3일 전: 2026-10-09) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-12 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-09) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:08** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 정상 (절단선과 일치) |
| `raw_candles` 당일 행수 | 382 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **2봉**: 09:33, 11:22
  - 전부 `session_bars` 에 보존됨 → **데이터 손실 아님**. 백필하지 않는다(533차 — 최근 N행 창이 밀린다).

- 라이브 로그 대조: `logs/20261012_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 3회 · 재시작 2회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 3개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **9건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 6396: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 11:22:46 · 정규장(09:00) 이후 **3건**
- PID 15168: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:40:45 · 정규장(09:00) 이후 **0건**
- PID 24772: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 09:33:56 · 정규장(09:00) 이후 **3건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 15168 | 08:40:45 | 09:33:34 | 없음 | 판정불가 — WER **미측정** |
| 24772 | 09:33:56 | 11:22:25 | 없음 | 판정불가 — WER **미측정** |
| 6396 | 11:22:46 | 15:47:14 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 217개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261012-점검리포트.md` | 33.9KB | 10-12 12:39 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261012.md` | 18.0KB | 10-12 12:39 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_intra.md` | 84.1KB | 10-12 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261012_pre.md` | 62.0KB | 10-12 09:01 |
| `docs/정기점검/매일점검/MW0601-20261009-점검리포트.md` | 51.1KB | 10-09 17:29 |
| `docs/정기점검/매일점검/_tmp_append_post_20261009.md` | 19.2KB | 10-09 16:25 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_post.md` | 53.0KB | 10-09 16:17 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_pre.md` | 48.6KB | 10-09 15:34 |

### `docs/정기점검/금요일점검` — 60개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261008.json` | 3.0KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261008.md` | 5.0KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20261008.json` | 38.9KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20261008.md` | 32.5KB | 10-08 15:57 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20261008.json` | 125.0KB | 10-08 15:56 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20261008.md` | 194.1KB | 10-08 15:56 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20261002.json` | 3.0KB | 10-02 15:57 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20261002.md` | 5.0KB | 10-02 15:57 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. `logs/20261012_WARN.log`: ERROR 이상 2건
2. `logs/20261012_HEALTH.log`: ERROR 이상 1건
3. 포지션 5건 중 최종청산이 하드스톱·손절 계열 **5건(100%)** — 손절 준수율 확인 필요 (레그 7행)
4. 다레그 포지션 **2건** — 레그 단위 집계는 손익·승률을 왜곡한다(계측 4원칙 ①). §5 표는 포지션 단위이니 그 값을 인용하라
5. 메인 스레드 정지 5초 초과 **3건** (최대 7484ms) — CB⑤(파이프라인 경과시간)와 **단위가 다르다**. CB⑤ 미발동이 정상이며, 5초~180초 구간은 FZ-1 워치독도 보지 않는다. §5 잔차 표로 CB⑤ 사각 크기를 확인하라 (482차 F-3)
6. `logs/20261012_WARN.log`: **level=CRITICAL** 1건(표본)
7. `logs/20261012_SYSTEM.log`: **ConstOut** 8건(표본)
8. `logs/20261012_SIGNAL.log`: **WeightCollapse** 8건(표본)
9. `logs/20261012_SIGNAL.log`: **ConstOut** 8건(표본)
10. `logs/20261012_LEARNING.log`: **축퇴** 8건(표본)
11. `logs/20261012_HEALTH.log`: **level=CRITICAL** 1건(표본)
12. `logs/crash_fault.log`: `Windows fatal exception` **9건** (정규장 09:00 이후 6건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
13. 런처 재시작 같은 날 **2회** (09:33 일시적 크래시, 11:22 일시적 크래시) — 재시작 간격·가동시간이 줄어드는지 §9 「프로세스 종료 3축 대사」에서 볼 것 (661차 G-3)
14. 미커밋 변경 120건 (실질 18건 · 코드 0건 · EOL 파생 0건)
15. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. [618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을 쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261012*.log` (Windows) / `grep 강제청산 logs/*20261012*.log`*