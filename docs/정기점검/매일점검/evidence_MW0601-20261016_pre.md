# 미륵이 증거 다이제스트 — 2026-10-16 / PRE

- 생성 2026-10-16 08:59:29 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01cpg1qxisweox7zxpobfxhk/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261016` · `2026-10-16` · `261016` · `1016`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **21개** 파일 · 21개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261016.log` | 136B | 10-16 07:21 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261016.log` | 124B | 10-16 08:45 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261016.log` | 140B | 10-16 08:45 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261016.json` | 244B | 10-16 08:59 |
| `launcher_{DATE}_084001_2887.log` | 1 | `logs/Mireuk_batch/launcher_20261016_084001_2887.log` | 959B | 10-16 08:40 |
| `launcher_{DATE}_084533_3971.log` | 1 | `logs/Mireuk_batch/launcher_20261016_084533_3971.log` | 54.1KB | 10-16 08:58 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261016.log` | 173B | 10-16 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261016.log` | 148B | 10-16 08:46 |
| `retrain_intraday_20260709_{DATE}00.log` | 1 | `logs/retrain_intraday_20260709_101600.log` | 4.6KB | 07-09 10:16 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261016.log` | 2.2KB | 10-16 08:57 |
| `{DATE}_DATA.log` | 1 | `logs/20261016_DATA.log` | 892B | 10-16 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261016_DEBUG.log` | 0B | 10-16 08:46 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261016_HEALTH.log` | 0B | 10-16 08:46 |
| `{DATE}_HOGA.log` | 1 | `logs/20261016_HOGA.log` | 959.8KB | 10-16 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261016_LEARNING.log` | 53.8KB | 10-16 08:57 |
| `{DATE}_MICRO.log` | 1 | `logs/20261016_MICRO.log` | 26.3KB | 10-16 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20261016_PROBE.log` | 12.1KB | 10-16 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261016_SIGNAL.log` | 8.6KB | 10-16 08:57 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261016_SYSTEM.log` | 25.2KB | 10-16 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261016_TRADE.log` | 167B | 10-16 08:46 |
| `{DATE}_WARN.log` | 1 | `logs/20261016_WARN.log` | 5.1KB | 10-16 08:58 |

## 2. 코드·커밋 상태

- HEAD `51d5de4` · 브랜치 `v9-dev` · 미커밋 132건 · 실질 변경 4건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 4 · 미추적 128 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.6초(`git diff --numstat`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261013.md
 M docs/미륵이고도화3/신동2/학습/lessons.json
 M docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md
 M docs/미륵이고도화3/신동2/학습/추이_MW0601.md
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
?? dev_memory/_tmp_append_decisionlog_20261013_intra.md
?? dev_memory/_tmp_append_decisionlog_20261015_post.md
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
?? dev_memory/_tmp_append_nexttodo_20261013_intra.md
?? dev_memory/_tmp_append_nexttodo_20261015_post.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261014.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261015.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261016.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261012.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261013.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261014.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261015.md
… 외 92건
```

**당일(2026-10-16) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
51d5de4 [MW0601] 696차 후속: 장후 자동조치 — E-2 · F-X1
bd501c2 [MW0601] 692차 후속3: 피터2 — 도착 시점에 이미 만료된 지시는 대기로 열지 않는다
46d2e13 [MW0601] 692차 후속2: CREON 런처 기동흐름 — LAUNCH_API 파싱 즉사 · 계좌비밀번호 창 자동처리 · 사이드카 중복/자진종료
6118658 [MW0601] 692차 후속: 08:50 맥점 08:45 시가 당일 차트 보정 — 실시간 첫 틱 → 개장 체결가
57155d1 [MW0601] 692차: 장후 봉 정합 — 만기일 창(15:22–15:39)·종료 전 확정 판정 · raw_candles 창 안 보충(618차 번복, bar_recovered=2/3) · 따라잡기 · 부분 봉 교정
0ca2476 [MW0601] 691차: 08:50 맥점 전일 이력 경고 — 「전일 이력 없음」 깜박임 · 「전일 부분 결손」 주황 고정
fe22516 [MW0601] 690차: 10-14 장후 점검 리포트 · 피터2 트레일 결정 기록
0140c60 [MW0601] 690차 후속: 피터2 이익보호 트레일 실거래 적용 + 기존 규칙 섀도
acc5a13 [MW0602] 체리픽: ProfitGuard broker 추정 수수료 이중 차감 수정 · 8a5f782 설명 정정 (원 4d050d7, dev)
8a5f782 [MW0602] 체리픽: 실계좌 일일손익 TR 기준일자 재시도 · 브로커 손익 net 축 판별 · 잔고 기본값 미측정 표기 (원 a6ab8f2·c1ff742, dev)
74f1d4b [MW0601] 피터2: 진입 로그를 시도·접수·실패로 분리 — 브로커 거부도 TRADE 로그상 진입으로 읽히던 문제
271ddbd Merge remote-tracking branch 'origin/v9-dev' into v9-dev
```

⚠ **PC명 태그 누락 커밋 1건** (CLAUDE.md 멀티PC 컨벤션 위반):
```
271ddbd Merge remote-tracking branch 'origin/v9-dev' into v9-dev
```

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

### 차단 게이트 전수 인벤토리 — 41개 중 **9개 꺼짐**

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

_본문 미열람(설정): `20261016_HOGA.log` 959.8KB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/17개 (중요도순). 제외: `20261016_PROBE.log`, `launcher_20261016_084533_3971.log`, `launcher_20261016_084001_2887.log`, `shindong2_20261016.log`, `maekjeom_ladder_20261016.log`, `peter2_receiver_20261016.log`, `freeze_sentinel_20261016.log`, `claude_resume_20261016.log`_

### `logs/20261016_TRADE.log` — 167B · 2행 · 최종 08:46:31

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:26 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-16 08:46:31 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-16 08:46:26 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-16 08:46:31 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261016_WARN.log` — 5.1KB · 31행 · 최종 08:58:00

- 형식 평문 · 시각 인식 31행 · WARNING=31

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:11 [WARNING] SYSTEM: [BarGap] 기동 시점 결손 1봉 / 검사창 08:45~08:45 (분그리드 기준) — 08:45 | session_bars 보존 여부는 15:46 확정 판정에서
2026-10-16 08:46:34 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-16 08:46:34 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 62ms
2026-10-16 08:46:34 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-16 08:46:34 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
  …
2026-10-16 08:58:00 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.5ms | size=1994x950 candles=12 grid=9.9 spans=0.0 candles=0.4 dir=0.0 regime=0.0 markers=0.0 axes=19.9 cross=0.0 | slow_cnt=4 total_cnt=86 overlay_cnt=440
2026-10-16 08:59:42 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 32.4ms | size=1994x950 candles=13 grid=10.3 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=20.2 cross=0.0 | slow_cnt=5 total_cnt=103 overlay_cnt=544
2026-10-16 08:59:43 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 44.0ms | size=1994x950 candles=13 grid=14.1 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=28.0 cross=0.0 | slow_cnt=6 total_cnt=105 overlay_cnt=545
2026-10-16 08:59:47 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 36.7ms | size=1994x950 candles=13 grid=14.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.2 cross=0.0 | slow_cnt=7 total_cnt=106 overlay_cnt=549
2026-10-16 08:59:47 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 34.6ms | size=1994x950 candles=13 grid=11.6 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=21.1 cross=0.0 | slow_cnt=8 total_cnt=107 overlay_cnt=549
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 11 | 08:46:34 | 08:48:29 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChartDBG` | 8 | 08:55:36 | 08:59:47 | paintEvent slow 45.0ms | size=1994x950 candles=9 grid=24.8 spans=0.0 candles=0.3 dir=0.0 regime=0.0 markers=0.0 axes=18.7 cross=0.0 | slow_cnt=1 total_cnt=71 overlay_cnt=339 |
| `CybosDailyPnl` | 2 | 08:46:34 | 08:46:34 | 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용 |
| `출처축` | 2 | 08:46:35 | 08:46:35 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:46:35 | 08:46:35 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-10-15 → 2026-10-16)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Peter2Offset` | 2 | 08:47:05 | 08:52:05 | A056B 실측=-2.29 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-2.29 | 직전일=-2.12(prev_day:2026-10-15, safe=True) 차=-0.17 | 57ms |
| `Canary` | 2 | 08:55:06 | 08:55:06 | scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `BarGap` | 1 | 08:46:11 | 08:46:11 | 기동 시점 결손 1봉 / 검사창 08:45~08:45 (분그리드 기준) — 08:45 | session_bars 보존 여부는 15:46 확정 판정에서 |
| `LEVELS 08:50` | 1 | 08:50:05 | 08:50:05 | 봉원천=db_fallback(버퍼 0봉)+chart(1봉) 1봉 · 기준봉=08:45 · 구독지연=125.7s |

**채널** — `SYSTEM`×31

**컴포넌트 상위 15** — `LiveDBG`×11, `ChartDBG`×8, `CybosDailyPnl`×2, `출처축`×2, `SessionStateDrop`×2, `Peter2Offset`×2, `Canary`×2, `BarGap`×1, `LEVELS 08:50`×1

### `logs/20261016_SYSTEM.log` — 25.2KB · 195행 · 최종 08:59:22

- 형식 평문 · 시각 인식 189행 · INFO=189, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:11 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=3744 | 행감지=30s all_threads=True
2026-10-16 08:46:11 [INFO] SYSTEM: [DBInit] 합계 0.51s | predictions=0.06s trades=0.25s daily_stats=0.01s shap=0.02s raw_data=0.13s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.04s
2026-10-16 08:46:11 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-16 08:46:11 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-16 08:46:11 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-16 08:59:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:58 vol=158 | live_buy=96 shadow_buy=71 anchor_buy=71 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-10-16 08:59:06 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=10개 (08:55 최종 6개 대비 +4) — 재측정만, 재적합 없음
2026-10-16 08:59:19 [INFO] SYSTEM: [TickUI] alive ticks=1293 code=A056B close=880.10
2026-10-16 08:59:22 [INFO] SYSTEM: [CybosRT-TICK] #1300 code=A056B raw_time=85922 parsed=08:59:22 price=880.08 vol=1 bid1=879.96 ask1=880.18 flag=49 side=BUY anchor=1/0
2026-10-16 08:59:40 [INFO] SYSTEM: [CybosRT-TICK] #1400 code=A056B raw_time=85939 parsed=08:59:39 price=879.24 vol=1 bid1=879.08 ask1=879.24 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×189

**컴포넌트 상위 15** — `CybosSub`×21, `CybosRT-TICK`×19, `System`×16, `TickUI`×13, `CybosRT-ROLLOVER`×12, `BAR-CLOSE`×12, `CVD-ANCHOR`×12, `SYSTEM`×9, `PreMarket`×7, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `Capital`×4, `CybosInvestorRaw`×4

### `logs/20261016_SIGNAL.log` — 8.6KB · 71행 · 최종 08:57:00

- 형식 평문 · 시각 인식 71행 · INFO=71

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.466
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.448
  …
2026-10-16 08:55:06 [INFO] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.0566 → floor=0.25 적용 (z-score 폭발 방지)
2026-10-16 08:55:06 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0549 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-16 08:55:06 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1132 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-16 08:55:06 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP  n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-10-16 08:57:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**채널** — `SIGNAL`×71

**컴포넌트 상위 15** — `ScalerFloor`×48, `DynMC`×7, `Model`×6, `ScalerRefresh`×5, `EnsembleGater`×1, `TimeRouter`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1

### `logs/20261016_LEARNING.log` — 53.8KB · 298행 · 최종 08:57:00

- 형식 평문 · 시각 인식 298행 · WARNING=145, INFO=153

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:46:13 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과
2026-10-16 08:46:17 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00121 auc=0.532 out_max=0.4229 (n=135) → 보정 재적용
  …
2026-10-16 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-16 08:52:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-16 08:55:05 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장], total=140, ver=5)
2026-10-16 08:55:06 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-16 08:57:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:1m` | 48 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:30m` | 41 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 24 | 08:46:16 | 08:46:25 | 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 17 | 08:46:17 | 08:46:25 | 축퇴 감지 — span=0.00084 auc=0.529 out_max=0.2880 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 9 | 08:46:17 | 08:46:25 | 축퇴 감지 — span=0.00108 auc=0.453 out_max=0.3129 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 6 | 08:46:17 | 08:46:25 | 축퇴 감지 — span=0.00051 auc=0.520 out_max=0.3781 (기준 auc<0.53 and span<0.020, 기저율=0.3778 n=90) → 보정 미적용, raw 통과 [기존 fitted 해제] |

**채널** — `LEARNING`×298

**컴포넌트 상위 15** — `Calibration:1m`×94, `Calibration:30m`×81, `Calibration:3m`×46, `Calibration:5m`×33, `Calibration:10m`×18, `Calibration:15m`×12, `ScalerWarmup`×5, `ExtremityCorrector`×2, `Consolidator`×2, `RF`×1, `Calibration:ensemble`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

### `logs/retrain_intraday_20260709_101600.log` — 4.6KB · 39행 · 최종 10:16:34

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-09 10:16:00,674 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a8266270.json
2026-07-09 10:16:02,578 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-09 10:16:34,710 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.35s | old_acc=nan)
2026-07-09 10:16:34,714 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-09 10:16:34,714 [INFO] LEARNING: [Retrain] 완료 | 32.1초 | 성공=6/6 호라이즌
2026-07-09 10:16:34,716 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.0s 데이터=20000행
2026-07-09 10:16:34,719 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_a8266270.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/20261016_MICRO.log` — 26.3KB · 74행 · 최종 08:59:20

- 형식 평문 · 시각 인식 74행 · DEBUG=74

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:47:05 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=883.14/1 ask1=883.36/1 mp={'microprice_tick': 883.25, 'midprice_tick': 883.25, 'depth_bias_tick': -0.049} mlofi_tick=None queue=None
2026-10-16 08:47:06 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=883.14/1 ask1=883.16/1 mp={'microprice_tick': 883.15, 'midprice_tick': 883.15, 'depth_bias_tick': 0.0265} mlofi_tick=-3.0667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-16 08:47:06 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=883.14/1 ask1=883.36/1 mp={'microprice_tick': 883.25, 'midprice_tick': 883.25, 'depth_bias_tick': -0.049} mlofi_tick=3.0667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-10-16 08:47:06 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=883.14/1 ask1=883.36/1 mp={'microprice_tick': 883.25, 'midprice_tick': 883.25, 'depth_bias_tick': -0.1088} mlofi_tick=-1.7333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
2026-10-16 08:47:06 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=883.14/1 ask1=883.36/2 mp={'microprice_tick': 883.2133, 'midprice_tick': 883.25, 'depth_bias_tick': -0.1731} mlofi_tick=-3.0667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio': -…
  …
2026-10-16 08:59:00 [DEBUG] MICRO: [MICRO-MINUTE] #12 ts=2026-10-16 08:58:00 close=880.18 bias=0.001687 slope=-0.334101 depth_bias=0.0206 mlofi_norm=-0.026672 mlofi_pressure=-1 mlofi_slope=-22.738333 queue_signal=-0.0398 queue_ma=-0.0110 queue_momentum=-0.0095 depletion=0.4928 refill=0.5072 imbalan…
2026-10-16 08:59:05 [DEBUG] MICRO: [MICRO-TICK] #3900 bid1=879.90/2 ask1=880.14/2 mp={'microprice_tick': 880.02, 'midprice_tick': 880.02, 'depth_bias_tick': -0.1237} mlofi_tick=2.4833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-10-16 08:59:20 [DEBUG] MICRO: [MICRO-TICK] #4000 bid1=879.96/1 ask1=880.06/1 mp={'microprice_tick': 880.01, 'midprice_tick': 880.01, 'depth_bias_tick': -0.0115} mlofi_tick=-4.0167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-10-16 08:59:30 [DEBUG] MICRO: [MICRO-TICK] #4100 bid1=879.46/1 ask1=879.74/2 mp={'microprice_tick': 879.5533, 'midprice_tick': 879.6, 'depth_bias_tick': -0.2425} mlofi_tick=-6.7667 queue={'depletion_bid': -0.0, 'depletion_ask': 0.0, 'refill_bid': 0.0, 'refill_ask': 1.0, 'bid_cancel_add_ratio':…
2026-10-16 08:59:42 [DEBUG] MICRO: [MICRO-TICK] #4200 bid1=878.96/1 ask1=879.08/69 mp={'microprice_tick': 878.9617, 'midprice_tick': 879.02, 'depth_bias_tick': -0.883} mlofi_tick=1.0 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0…
```

</details>

**채널** — `MICRO`×74

**컴포넌트 상위 15** — `MICRO-TICK`×62, `MICRO-MINUTE`×12

### `logs/20261016_DATA.log` — 892B · 4행 · 최종 08:58:38

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-16 08:58:09 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-103 individual=+144 institution=-60 oi=0 call_foreign=+460 put_foreign=-46 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-16 08:58:09 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-16 08:58:38 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-114 individual=+163 institution=-71 oi=0 call_foreign=+522 put_foreign=-38 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-16 08:58:38 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
  …
2026-10-16 08:58:09 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-103 individual=+144 institution=-60 oi=0 call_foreign=+460 put_foreign=-46 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-16 08:58:09 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-16 08:58:38 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=-114 individual=+163 institution=-71 oi=0 call_foreign=+522 put_foreign=-38 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-16 08:58:38 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
```

</details>

**채널** — `DATA`×4

**컴포넌트 상위 15** — `CybosInvestor`×4

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 0 |
| 진입 등록(`[Position] 진입`) | 0 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 0 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 0 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 0 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 0 |
| 차단(`[차단]`) | 0 |
| 사이저 호출(`[Sizer]`) | 0 |

### 메인 스레드 블로킹 2건 · 최대 4407ms · 5초 초과 0건

상위 — 4407ms, 3765ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261016_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:46:39 2026-10-16 08:46:39 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4407ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4407 band=INFO since_pipe_s=NA
08:46:42 2026-10-16 08:46:42 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3765ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3765 band=INFO since_pipe_s=NA
```

### `logs/20261016_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.466
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
08:46:07 2026-10-16 08:46:07 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
```

### `logs/20261016_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:46:16 2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00316 auc=0.367 out_max=0.3888 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
08:46:16 2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00040 auc=0.471 out_max=0.4252 (기준 auc<0.53 and span<0.020, 기저율=0.4250 n=80) → 보정 미적용, raw 통과
08:46:16 2026-10-16 08:46:16 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00048 auc=0.479 out_max=0.5502 (기준 auc<0.53 and span<0.020, 기저율=0.5500 n=80) → 보정 미적용, raw 통과
08:46:17 2026-10-16 08:46:17 [INFO] LEARNING: [Calibration:3m] 축퇴 해소 — span=0.00121 auc=0.532 out_max=0.4229 (n=135) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261016_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:46:26 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:46 ~ 08:46

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261016_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:46:11 [WARNING] 기동 시점 결손 1봉 / 검사창 08:45~08:45 (분그리드 기준) — 08:45 | session_bars 보존 여부는 15:46 확정 판정에서 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 12 | 08:50:05 [WARNING] 봉원천=db_fallback(버퍼 0봉)+chart(1봉) 1봉 · 기준봉=08:45 · 구독지연=125.7s |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 10 | 08:55:06 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:46 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261016_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 57 | 08:46:11 [INFO] 활성화 | file=logs\crash_fault.log PID=3744 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 96 | 08:49:03 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 59 | 08:54:09 [INFO] #800 code=A056B raw_time=85409 parsed=08:54:09 price=881.66 vol=1 bid1=881.70 ask1=881.74 flag=49 side=BUY an… |

- 이 로그 생존구간: 08:46 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261016_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:46:07 [INFO] 기동 복원: GAP_OPEN  0.670 → 0.466 |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 34 | 08:50:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase1_3bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 32 | 08:55:06 [INFO] 1m 'macro_vix' scale=0.0331 → floor=0.10 적용 (z-score 폭발 방지) |

- 이 로그 생존구간: 08:46 ~ 08:57

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261015 | 15:47 | 로그 본문 |
| 20261014 | 17:41 | 로그 본문 |
| 20261013 | 19:02 | 로그 본문 |
| 20261012 | 18:35 | 로그 본문 |
| 20261009 | 18:33 | 로그 본문 |
| **중앙값** | **18:33** | 기준선 |
| **오늘 20261016** | **08:59** | 로그 본문 |

- 델타 **-574분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · 마지막 갱신 2026-10-15 17:43

최근 헤딩 8개:
```
## 2026-10-15 (MW0601 693차 — 장중 점검)
## 2026-10-15 (MW0601 694차 — 장전 점검, 지연 발화)
## 2026-10-15 (MW0601 695차 — 694차 후속: 「장후」 예약작업도 같은 지연/오발화 폭풍에 포함)
## 2026-10-15 (MW0601 696차 — 장후 점검: 종합 완성본)
## 2026-10-15 (MW0601 696차 후속 — 장후 자동조치: E-2 가상 장부 분리 · F-X1 종료 로그 직전 정지 꼬리) — 🟢 **구현 · 계측/도구 한정 · 매매 경로 무변경**
### E-2 — 점검 수집기가 가상 장부 진입을 「가상」으로 분리
### F-X1 — X 버튼 종료 로그에 직전 메인 스레드 정지 동반 기록
### 이월(C·사용자 몫)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
손 작업.

### E-2 — 점검 수집기가 가상 장부 진입을 「가상」으로 분리
- **증상**: 10-15 수집기 §5 진입 4건이 엔진 1 · 피터2 1 · 추정 2로 나왔다. 실제는 피터2 1(실거래) + 가상 3(신동 09:41:59·09:48:59, 미륵 11:32:00). 미륵 가상은 `horizon=3m hurst=mean-revert`까지 붙어 **「엔진」으로 오분류**됐고, 가상 3건은 `체결청산`이 없어 「미청산(보유 중)」으로 찍혔다. 3원 대사 「1=1≠4」를 사람이 15:40 로그로 직접 풀어야 했다.
- **원인**: 가상 레그도 같은 초에 `[Position] 진입`을 남긴다(F-19 뿌리문제). 수집기 `entry_source_of()`에 `[Virtual]` 분기가 없었다. 부수 결함: `assemble_positions()`에서 가상 진입이 `cur`를 열어 ① 뒤이은 실체결(FLAT→보유)이 cur 존재로 안 열리고 그 청산 레그가 가상 포지션에 붙을 수 있었고 ② 보유 중 실포지션이 「안 닫힌 채」 밀려날 수 있었다(10-15에는 순서상 발생 안 함).
- **결정**: 패턴 `virtual_entry`/`virtual_exit` 신설 · 출처 우선순위 **가상 > 피터2 > 엔진(horizon=) > 추정** · 가상 포지션은 cur와 독립(가상청산으로만 닫음, 주체·방향 FIFO, 짝 없는 가상청산은 inferred 행으로 보존) · 헤드라인·레그표·손절준수율·다레그 적신호에서 제외하고 「가상 장부」 표로 **병기**(합산 금지).
- **Why**: 가상은 실주문이 없다 — 엔진 성적·계좌 손익에 섞이면 507차 F-8·689차 F-5 확장과 같은 오귀속이다.
- **How to apply**: `count_entry_sources()` 반환 키가 4개(`엔진/피터2/가상/추정`)가 됐다 — 이 dict를 정확 비교하는 테스트는 `가상` 키를 포함해야 한다(test_689 2a 갱신). F-19(매매 코드 쪽 가상 레그 분리, C)는 **별개**로 남는다 — 이건 점검 도구 쪽 표시만 고친 것이다.
- **검증**: 10-15 실로그 재수집(스크래치) — 엔진 0 · 피터2 1 · 가상 3, 가상 장부 신동 −113,664 + 713,344 = **+599,680** · 미륵 **+22,290** = 15:40 `[Virtual] 장후 … 가상 실적`과 일치. 실계좌 헤드라인 1건 +662,304 · 정합성 OK. 회귀: `tests/test_696_autofix_virtual_ledger_and_stall_tail.py` §1.

### F-X1 — X 버튼 종료 로그에 직전 메인 스레드 정지 동반 기록
- **증상**: 12:12:04 `[MainStall]` 7,750ms → 12:14:13 사용자 종료. 로그로 인과를 가를 수 없어 O-i2/693-2 판정 보류.
- **결정**: `utils/exit_flags.py`에 `format_recent_stall()` + `write_exit_flags(extra=)` · 대시보드 `_tick_header`가 WARN(≥5s) 이상 정지의 ms·monotonic을 `self._last_stall_ms/_mono`에 기록(`__init__` 명시 초기화, 4원칙 ④) · `closeEvent` 두 분기(user_close/user_restart)가 `[Shutdown] intent=… files=N recent_stall_ms=7750 stall_age_s=129.0 within_window=True(300s)` 형태로 남김. 미관측이면 `recent_stall=none`(0ms 아님, 4원칙 ②).
- **리포트 제안과 다른 점(의도적)**: ① 변경 파일은 `main.py`가 아니라 `dashboard/main_dashboard.py` closeEvent(X 버튼 경로의 실제 위치, 618/684차) ② 「60초 내」 창 대신 **경과초 상시 기록 + 300초 창 플래그** — 10-15 사례가 129초라 60초 창이면 흔적이 안 남았다.
- **회귀 위험**: 로그 문자열 꼬리만 추가. 앞머리 `[Shutdown] intent=(\w+)`는 그대로라 수집기 의도 파서·test_684 무영향. daily_close/auto_shutdown(extra 없음)은 바이트 동일. 꼬리 계산 실패는 try로 흡수(종료 경로를 막지 않음). `_last_stall_*`는 종료 로그 외 읽는 곳 0(테스트 고정).
- **검증**: 단위 테스트만. **라이브 미검증** — 다음 사용자 X 종료 시 SYSTEM 로그에 꼬리가 붙는지 확인(기한: 다음 수동 종료 발생일).

### 이월(C·사용자 몫)
- L-2·L-3·L-5·L-6·L-7: 이미 NEXT_TODO 등록(696차 장후 점검). 사용자 결정 대기 — 자동조치 미구현.
- P5-18: 6칸 미완 → 구현 금지, 표본 축적(O-t3).
- 사용자 조치 1(12:14 종료 의도 확인)·2(트리거 3종 확인)·4(신동2 문서 등 커밋) — 손대지 않음.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · 마지막 갱신 2026-10-15 17:43

최근 헤딩 8개:
```
## 2026-10-14 (MW0601 690차 — 장후 점검)
### MW0601 691차 — 맥점 전일 이력 경고 (2026-10-15)
### MW0601 692차 — 장후 봉 정합 (2026-10-15)
### MW0601 693차 — 장중 점검 (2026-10-15)
### MW0601 694차 — 장전 점검, 지연 발화 (2026-10-15)
### MW0601 695차 — 장후 트리거, 조기(12:50 KST) 오발화 (2026-10-15)
### MW0601 696차 — 장후 점검, 종합 완성본 (2026-10-15)
### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
```

미완료 체크박스 **3202건** (끝에서 30건)
```
- [ ] 692-4 `rt_chart_fix` 교정 빈도 관찰 — 재기동 부분 봉 외(정상 분)에서 뜨면 규칙 재검토.
- [ ] **693-1 (사용자 확인 필요)** 12:14:13 `user_close` 종료 — 의도적 종료인지, 무엇 때문에 껐는지 사용자 확인. 재기동 여부도 사람 판단(⚠ 즉시판단, 점검리포트 1-1).
- [ ] **693-2 (O-i2)** 12:12:04 MainStall(7750ms)과 12:14 종료의 인과관계 미확정 — 장후 점검에서 재확인.
- [ ] **F-X1(제안, 미승인)** 종료 핸들러가 직전 60초 내 MainStall 이력을 `[Shutdown]` 줄에 동반 기록(원인 구분용). 적용 전 F-18과 중복 여부 확인 필요.
- [ ] (F-19 연장) 오늘 09:48:59 신동 가상 SHORT 미종결 표본 — F-19 회귀 테스트 케이스로 추가.
- [ ] (O-i1) 오늘 장전 점검 미실행 — 예약작업 동작 여부 내일 장전에서 확인.
- [ ] **694-1 (사용자 확인 필요)** "Mireuk premarket check" 예약작업이 08:57 KST 목표 대비
- [ ] **695-1 (사용자 확인 필요)** "Mireuk postmarket check"(예정 16:15 KST)가 694차가 보고한
- [ ] **695-2** 이 발화는 장이 열려 있는 시점(12:50 KST)이라 정식 「장후」 종합 완성본을 쓰지
- [ ] 693-1(엔진 12:14 종료 후 미재기동) — 이 세션 작성 시각(약 12:52 KST)까지도 **미해소**.
- [ ] **693-1 (사용자 확인 필요, 이월)** 12:14:13 `user_close` 종료 — 의도적인지 사용자
- [ ] **693-2 (판정보류, 이월)** 12:12:04 MainStall(7750ms)과 12:14 종료 인과관계 —
- [ ] **694-1 (사용자 확인 필요, 이월)** "Mireuk premarket check" 3시간53분 지연 발화
- [ ] **695-1 (사용자 확인 필요, 이월)** 트리거 3종 동시 오발화 원인 — 16:15 장후 재발
- [ ] **F-X1 (제안, 미승인)** 종료 핸들러(`main.py`)가 직전 60초 내 MainStall 이력을
- [ ] **F-19 연장 (690차 P1 유지)** 신동/미륵 가상 레그 분리 — 오늘 표본(3원 대사
- [ ] **L-2 (CREON 딥다이브 승계, P1)** `LAUNCH_API.bat:288` "이미 연결됨" 분기 —
- [ ] **L-3 (CREON 딥다이브 승계, P1)** 08:35→08:40 기동 간격 — STEP4 대기를 로그인
- [ ] **L-5 (CREON 딥다이브 승계, P2)** `cybos_autologin.py` 전일 잔존 세션 kill 실패 시
- [ ] **L-6 (CREON 딥다이브 승계, P2)** autologin 단일 인스턴스 락(`data/_autologin.lock`).
- [ ] **L-7 (CREON 딥다이브 승계, P2)** 계좌 불일치 실패 후 잘못된 ID 세션 정리 +
- [ ] **O-t1** 10-16 08:35 무인 기동이 L-1 수정 후 "두 번째 날"에도 끝까지 완주하는지.
- [ ] **O-t2** CREON 로그인 창 "아이디 저장" 값이 프로젝트(cp/dcybos)별 독립인지 —
- [ ] **O-t3** `ConfFloorGuard`(오후 보정기 출력상한<자동진입하한) 재발 여부 — P5-18
- [ ] **O-t4** "장전 점검" 예약작업이 10-16 08:57 KST 근처(±수 분)에 정상 발화하는지.
- [ ] **P5-18 (신규, 판정보류)** 오후 `ConfFloorGuard` 발동(14:55, 보정기 출력상한
- [ ] **F-X1 라이브 확인** 다음 사용자 X 종료 시 SYSTEM 로그 `[Shutdown] intent=user_* … recent_stall…` 꼬리 출현 확인.
- [ ] **E-2 후속(선택)** 실청산 0·가상만 있는 날은 수집기 §5 포지션 블록(`if ex or pe:`)이 안 그려져 가상 장부 표도 안 나온다 — 그런 날이 생기면 블록 조건 확장 검토(A등급).
- [ ] **(C 이월) L-2·L-3·L-5·L-6·L-7** — 위 696차 항목 그대로. 기동·로그인 흐름 변경이라 사용자 결정 후 별도 세션.
- [ ] **(C 이월) P5-18** — 6칸 미완(변경대상·기대효과·회귀위험 미정). O-t3 표본 축적 후 재평가.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
  필요"로 유지 — 693-1·693-2 그대로 둠(아래 재등록).
- [ ] **693-1 (사용자 확인 필요, 이월)** 12:14:13 `user_close` 종료 — 의도적인지 사용자
      확인. 여전히 미해결.
- [ ] **693-2 (판정보류, 이월)** 12:12:04 MainStall(7750ms)과 12:14 종료 인과관계 —
      사전등록된 확인 수단 없음, 313차 원칙상 확정 불가. 사람 확인 전까지 보류 유지.
- [ ] **694-1 (사용자 확인 필요, 이월)** "Mireuk premarket check" 3시간53분 지연 발화
      원인(트리거 `trig_0194gQz4dwrhmrw8D3tpsMDY`) — 사용자가 스케줄 설정 확인 필요.
- [ ] **695-1 (사용자 확인 필요, 이월)** 트리거 3종 동시 오발화 원인 — 16:15 장후 재발
      없음 확인(1차 긍정), 근본 원인(스케줄러)은 미확인.
- [ ] **F-X1 (제안, 미승인)** 종료 핸들러(`main.py`)가 직전 60초 내 MainStall 이력을
      `[Shutdown]` 줄에 동반 기록. grep 확인: `recent_stall` 키워드 0건 — 미구현.
- [ ] **F-19 연장 (690차 P1 유지)** 신동/미륵 가상 레그 분리 — 오늘 표본(3원 대사
      1=1≠4, 가상 3건 귀속 확인: 신동 2건 +599,680원·미륵 1건 +22,290원) 회귀 테스트
      케이스로 추가 권고. `scripts/collect_evidence.py` 엔트리 페어링에 `[Virtual]`
      분기 없음(grep 확인).
- [ ] **L-2 (CREON 딥다이브 승계, P1)** `LAUNCH_API.bat:288` "이미 연결됨" 분기 —
      IsConnect만 보지 말고 `cybos_autologin --broker creon` 항상 호출.
- [ ] **L-3 (CREON 딥다이브 승계, P1)** 08:35→08:40 기동 간격 — STEP4 대기를 로그인
      최악 소요(≈15분) 이상으로 늘리거나 완료 마커 대기로 변경.
- [ ] **L-5 (CREON 딥다이브 승계, P2)** `cybos_autologin.py` 전일 잔존 세션 kill 실패 시
      "이미 실행중" 자동 '예' 대신 즉시 실패+경보.
- [ ] **L-6 (CREON 딥다이브 승계, P2)** autologin 단일 인스턴스 락(`data/_autologin.lock`).
- [ ] **L-7 (CREON 딥다이브 승계, P2)** 계좌 불일치 실패 후 잘못된 ID 세션 정리 +
      원인(D, CYBOS 경로 저장ID) 추가 실측.
- [ ] **O-t1** 10-16 08:35 무인 기동이 L-1 수정 후 "두 번째 날"에도 끝까지 완주하는지.
- [ ] **O-t2** CREON 로그인 창 "아이디 저장" 값이 프로젝트(cp/dcybos)별 독립인지 —
      10-16 08:35 계좌가 바로 783343908로 붙는지(표본 2일차).
- [ ] **O-t3** `ConfFloorGuard`(오후 보정기 출력상한<자동진입하한) 재발 여부 — P5-18
      표본 축적.
- [ ] **O-t4** "장전 점검" 예약작업이 10-16 08:57 KST 근처(±수 분)에 정상 발화하는지.
- [ ] **P5-18 (신규, 판정보류)** 오후 `ConfFloorGuard` 발동(14:55, 보정기 출력상한
      0.3313 < 필요 0.4180) — n=1, 관측일 1일. 반복되면 `docs/정기점검/수익률향상_누적대장.md`에
      정식 등록.

### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
- [x] **E-2** 수집기 가상 장부 분리 — 구현(696차 후속 커밋). `[Virtual] … 가상진입` 동반 진입을 「가상」으로 분류·병기.
- [x] **F-X1** `[Shutdown] intent=` 줄에 `recent_stall_ms/stall_age_s/within_window` 꼬리 — 구현(`dashboard/main_dashboard.py` closeEvent · `utils/exit_flags.py`).
- [ ] **F-X1 라이브 확인** 다음 사용자 X 종료 시 SYSTEM 로그 `[Shutdown] intent=user_* … recent_stall…` 꼬리 출현 확인.
- [ ] **E-2 후속(선택)** 실청산 0·가상만 있는 날은 수집기 §5 포지션 블록(`if ex or pe:`)이 안 그려져 가상 장부 표도 안 나온다 — 그런 날이 생기면 블록 조건 확장 검토(A등급).
- [ ] **(C 이월) L-2·L-3·L-5·L-6·L-7** — 위 696차 항목 그대로. 기동·로그인 흐름 변경이라 사용자 결정 후 별도 세션.
- [ ] **(C 이월) P5-18** — 6칸 미완(변경대상·기대효과·회귀위험 미정). O-t3 표본 축적 후 재평가.

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

### `data/heartbeat_MW0601_20261016.json` — 244B · 10-16 08:59:06
```json
{
 "pid": 3744,
 "written_at": "2026-10-16T08:59:36",
 "beat_epoch": 1792108775.696483,
 "beat_age_sec": 0.7,
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

- 파일 최종 기록: **10-16 08:47:59**

| 키 | 값 | 수집 대상일(2026-10-16)과 일치 |
|---|---|---|
| `date` | 2026-10-16 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-16 08:55:06 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-15) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-16 08:55:06 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-15) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **08:58** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 08:59 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 12 |
| `session_bars` 당일 행수 | 12 (기대 411) |

- 미도래 **370봉** (08:59~15:08) — 수집 시각 08:59 이후라 결손·영구결손에서 제외
- 결손 **0봉**
- ⚠ **영구 결손 2봉** (`session_bars` 에도 없음): 08:45, 08:46

- 라이브 로그 대조: `logs/20261016_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | 측정됨 — 기동 1회 · 재시작 0회 |
| `crash_fault.log`(정상종료 기록) | 측정됨 — PID 1개 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | 측정됨 — **3건** |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- PID 3744: `Windows fatal exception` **3건** (access violation 3) — 직전 표식 시각 08:46:11 · 정규장(09:00) 이후 **0건**
  - 시각은 **발생 하한**이다(머리줄에 시각이 없다). 프로세스가 죽지 않은 오류이므로 위 종료 판정과 별개로 읽을 것. 스택은 `logs/crash_fault.log` 원문

| 미륵이 PID | 기동 | 정상종료 기록 | WER 네이티브 예외 | 판정 |
|---|---|---|---|---|
| 3744 | 08:46:11 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 231개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` | 6.5KB | 10-16 08:51 |
| `docs/정기점검/매일점검/MW0601-20261015-점검리포트.md` | 69.1KB | 10-15 17:48 |
| `docs/정기점검/매일점검/_tmp_append_post_20261015.md` | 33.9KB | 10-15 16:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261015_post.md` | 105.6KB | 10-15 16:18 |
| `docs/정기점검/매일점검/MW0601-20261015-CREON런처기동흐름-딥다이브.md` | 23.4KB | 10-15 14:22 |
| `docs/정기점검/매일점검/evidence_MW0601-20261015_intra.md` | 83.1KB | 10-15 12:27 |
| `docs/정기점검/매일점검/MW0601-20261014-점검리포트.md` | 43.4KB | 10-14 17:55 |
| `docs/정기점검/매일점검/evidence_MW0601-20261014_post.md` | 101.3KB | 10-14 17:46 |

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

1. 설정 불변식 `MAX_CONTRACTS` = `1` (기대 `3`) — 431차 10→3 인하. 실전 자본 확정 시 재산출 대상
2. `logs/20261016_LEARNING.log`: **축퇴** 8건(표본)
3. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
4. PC명 태그 누락 커밋 1건 — 멀티PC 컨벤션 위반
5. 미커밋 변경 132건 (실질 4건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261016*.log` (Windows) / `grep 강제청산 logs/*20261016*.log`*