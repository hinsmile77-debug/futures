# 미륵이 증거 다이제스트 — 2026-10-23 / PRE

- 생성 2026-10-23 08:59:28 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-012wvtzggxhyv8ttmhsqjen6/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261023` · `2026-10-23` · `261023` · `1023`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **26개** 파일 · 26개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261023.log` | 249B | 10-23 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261023.log` | 631B | 10-23 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261023.json` | 244B | 10-23 08:59 |
| `launcher_{DATE}_043744_29897.log` | 1 | `logs/Mireuk_batch/launcher_20261023_043744_29897.log` | 41.9KB | 10-23 06:23 |
| `launcher_{DATE}_062335_17869.log` | 1 | `logs/Mireuk_batch/launcher_20261023_062335_17869.log` | 18.6KB | 10-23 06:25 |
| `launcher_{DATE}_062623_18417.log` | 1 | `logs/Mireuk_batch/launcher_20261023_062623_18417.log` | 18.6KB | 10-23 06:27 |
| `launcher_{DATE}_084001_11833.log` | 1 | `logs/Mireuk_batch/launcher_20261023_084001_11833.log` | 66.2KB | 10-23 08:59 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261023.log` | 109B | 10-23 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261023.log` | 2.0KB | 10-23 08:58 |
| `retrain_intraday_20260625_{DATE}59.log` | 1 | `logs/retrain_intraday_20260625_102359.log` ⚠ 다른 날짜(20260625) 파일 — 날짜 토큰 오매칭 | 4.6KB | 06-25 10:24 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261023.log` | 2.6KB | 10-23 08:55 |
| `shutdown_normal_{DATE}.txt` | 1 | `data/shutdown_normal_20261023.txt` | 40B | 10-23 06:27 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-23.jsonl` | 327B | 10-23 08:50 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20261023_BACKFILL.log` | 0B | 10-23 05:22 |
| `{DATE}_DATA.log` | 1 | `logs/20261023_DATA.log` | 892B | 10-23 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261023_DEBUG.log` | 0B | 10-23 04:38 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261023_HEALTH.log` | 0B | 10-23 04:38 |
| `{DATE}_HOGA.log` | 1 | `logs/20261023_HOGA.log` | 1.5MB | 10-23 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261023_LEARNING.log` | 246.9KB | 10-23 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20261023_MICRO.log` | 36.7KB | 10-23 08:59 |
| `{DATE}_OPTION_HTS_SYNC.log` | 1 | `logs/20261023_OPTION_HTS_SYNC.log` | 464B | 10-23 05:25 |
| `{DATE}_PROBE.log` | 1 | `logs/20261023_PROBE.log` | 12.5KB | 10-23 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261023_SIGNAL.log` | 16.0KB | 10-23 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261023_SYSTEM.log` | 69.1KB | 10-23 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261023_TRADE.log` | 1.4KB | 10-23 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261023_WARN.log` | 16.6KB | 10-23 08:58 |

_다른 날짜 파일 1개는 짧은 날짜 토큰(`1023`)이 시각 숫자와 우연히 겹친 것이라 이후 절에서 제외했다: `retrain_intraday_20260625_102359.log`_

## 2. 코드·커밋 상태

- HEAD `0a880ff9` · 브랜치 `v9-dev` · 미커밋 2건 · 실질 변경 1건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 1 · 미추적 1 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261023.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.9초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261023.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261023.md
```

**당일(2026-10-23) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
0a880ff9 [MW0601] 707차 후속2: dev 실전 자본 3층 켜짐 기록 — 이식 메모 갱신 (dev a815d2dd, 사용자 지시)
54144e55 [MW0601] 707차 후속: 실전 자본 3층 dev 배포 기록 — 이식 메모 (dev 22fdb663, 동작 변경 3종 기본 꺼짐 · 모니터만 켜짐)
be41c470 [MW0601] 708차: 신동 실거래 출처 분리 · 철회 섀도 계측
6d483785 [MW0601] 707차: 실전 자본 3층(관측·정책·통제) — 신동 수량 증거금 연동 · 위험자본 min(정책, 예탁금) · PG 수량 비례 · 주문/체결 탭 모니터
5360d398 [MW0601] 706차: CREON 실거래 런처 실패 경로 — 08:35 트리거 봉쇄 해소 · 불일치 세션 정리 · starter 레지스트리 계측
```

**최근 커밋 12건**
```
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
ab7bf96a [MW0601] 705차 후속2: COM RunLevel 판정기 dev 배포 기록 — 이식 메모 (dev 08807a68)
689d1956 [MW0601] 705차 후속: COM 예약작업 RunLevel 공용 판정기 · 등록 작업 전수 점검 (704-6 해소)
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

_본문 미열람(설정): `20261023_HOGA.log` 1.5MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/shutdown_normal_20261023.txt`** — 40B · 10-23 06:27:32
```
user_close
2026-10-23T06:27:32.380572
```

_다이제스트 대상 8/18개 (중요도순). 제외: `launcher_20261023_084001_11833.log`, `launcher_20261023_043744_29897.log`, `launcher_20261023_062335_17869.log`, `launcher_20261023_062623_18417.log`, `shindong2_20261023.log`, `peter2_receiver_20261023.log`, `freeze_sentinel_20261023.log`, `20261023_OPTION_HTS_SYNC.log`_

### `logs/20261023_TRADE.log` — 1.4KB · 12행 · 최종 08:41:40

- 형식 평문 · 시각 인식 12행 · INFO=12

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:35 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-23 04:38:41 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-23 06:17:07 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-23 06:17:11 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-23 06:24:20 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
  …
2026-10-23 06:27:13 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-23 08:41:01 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-23 08:41:06 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-23 08:41:40 [INFO] TRADE: [ProfitGuard] 원화 임계 배율 ×1.00 → ×1.50 (신동 3계약) — L1 발동 3,000,000원 · L2 중단 6,000,000원 · L3 1,500,000원 · L4 2,250,000원
2026-10-23 08:41:40 [INFO] TRADE: [Capital] 예탁금 3,400만 · 위험자본 3,400만(정책) · 계약당 증거금≈미측정 | 가능수량 지금 미측정 · 장시작 미측정 · 위험최대 5 | 신동 실주문 3(최대허용 3 · 폴백 3) ✅ | 일일한도 68만 · PG ×1.50(신동) | 장시작 가능수량 미측정 — SHINDONG_LIVE_QTY=3 폴백 · 지금 주문가능수량 미측정
```

</details>

**채널** — `TRADE`×12

**컴포넌트 상위 15** — `ProfitGuard`×6, `Position`×5, `Capital`×1

### `logs/20261023_WARN.log` — 16.6KB · 92행 · 최종 08:58:40

- 형식 평문 · 시각 인식 92행 · WARNING=92

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-23 04:38:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-23 04:38:44 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr25)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-23 04:38:44 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr25)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-23 04:38:44 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 125ms account=783343908
  …
2026-10-23 08:57:45 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 403.5ms | size=1484x950 candles=13 grid=31.7 spans=0.0 candles=1.6 dir=0.0 regime=0.0 markers=0.0 axes=368.2 cross=0.0 | slow_cnt=6 total_cnt=113 overlay_cnt=795
2026-10-23 08:58:10 [WARNING] SYSTEM: [Peter2] 오프셋 자동 적용 -1.82(prev_day:2026-10-19, safe=True) → -1.29(live:08:58:10, safe=True)
2026-10-23 08:58:10 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 40.9ms | size=1484x950 candles=14 grid=7.8 spans=0.0 candles=1.0 dir=0.0 regime=0.0 markers=0.0 axes=30.4 cross=0.0 | slow_cnt=7 total_cnt=116 overlay_cnt=821
2026-10-23 08:58:21 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 31.2ms | size=1484x950 candles=14 grid=6.8 spans=0.0 candles=0.9 dir=0.0 regime=0.0 markers=0.0 axes=22.2 cross=0.0 | slow_cnt=8 total_cnt=117 overlay_cnt=834
2026-10-23 08:58:40 [WARNING] SYSTEM: [OptionFlowChart] 그리기 109.4ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 1015x1001
```

</details>

**WARNING — 태그 11종 (상위 11)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 45 | 04:38:44 | 08:57:33 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `CybosDailyPnl` | 10 | 04:38:44 | 08:41:10 | 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr25)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용 |
| `출처축` | 10 | 04:38:45 | 08:41:10 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT', 'SHINDONG'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `OptionFlowChart` | 8 | 04:38:54 | 08:58:40 | 그리기 78.5ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 774x1001 |
| `ChartDBG` | 8 | 08:56:35 | 08:58:21 | paintEvent slow 32.2ms | size=1484x950 candles=12 grid=10.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.4 cross=0.0 | slow_cnt=1 total_cnt=106 overlay_cnt=708 |
| `CybosMarginQty` | 3 | 08:45:40 | 08:56:40 | 조회 실패 ret=0 status=-1 msg=11298 시장가/신고대량/최우선/최유리지정가 주문은 단가를 입력하지 않습니다. (ordsvr58)(ord.fo.dpmyinqr.selanwordpsblqty) account=783343908 code=A056B |
| `Capital` | 2 | 04:38:45 | 04:38:45 | 기준자본(15,000,000원)과 실제잔고(28,359,492원) 괴리 +89.1% — 계좌가 바뀌었거나 자본 설정이 낡았을 수 있습니다(config/settings.py:SIZING_TARGET_CAPITAL_KRW). |
| `SessionStateDrop` | 2 | 04:38:45 | 04:38:45 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-10-22 → 2026-10-23)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Peter2Offset` | 2 | 08:47:10 | 08:52:40 | A056B 실측=-1.09 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-1.09 | 직전일=-1.82(prev_day:2026-10-19, safe=True) 차=0.73 | 44ms |
| `SessionBackfill` | 1 | 08:41:40 | 08:41:40 | 2026-10-22 차트 보충 — chart=411 existing=411 inserted=0 mismatch=8 |
| `Peter2` | 1 | 08:58:10 | 08:58:10 | 오프셋 자동 적용 -1.82(prev_day:2026-10-19, safe=True) → -1.29(live:08:58:10, safe=True) |

**채널** — `SYSTEM`×92

**컴포넌트 상위 15** — `LiveDBG`×45, `CybosDailyPnl`×10, `출처축`×10, `OptionFlowChart`×8, `ChartDBG`×8, `CybosMarginQty`×3, `Capital`×2, `SessionStateDrop`×2, `Peter2Offset`×2, `SessionBackfill`×1, `Peter2`×1

### `logs/20261023_SYSTEM.log` — 69.1KB · 496행 · 최종 08:59:18

- 형식 평문 · 시각 인식 482행 · INFO=482, PLAIN=14

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:21 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=8984 | 행감지=30s all_threads=True
2026-10-23 04:38:21 [INFO] SYSTEM: [DBInit] 합계 0.46s | predictions=0.05s trades=0.23s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-23 04:38:21 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-23 04:38:21 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-23 04:38:21 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-23 08:59:02 [INFO] SYSTEM: [CybosRT-TICK] #3000 code=A056B raw_time=85902 parsed=08:59:02 price=841.24 vol=1 bid1=841.00 ask1=841.20 flag=49 side=BUY anchor=1/0
2026-10-23 08:59:11 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=9개 (08:55 최종 4개 대비 +5) — 재측정만, 재적합 없음
2026-10-23 08:59:15 [INFO] SYSTEM: [TickUI] alive ticks=3084 code=A056B close=840.66
2026-10-23 08:59:18 [INFO] SYSTEM: [CybosRT-TICK] #3100 code=A056B raw_time=85918 parsed=08:59:18 price=840.38 vol=3 bid1=840.36 ask1=840.38 flag=49 side=BUY anchor=3/0
2026-10-23 08:59:40 [INFO] SYSTEM: [CybosRT-TICK] #3200 code=A056B raw_time=85940 parsed=08:59:40 price=838.14 vol=1 bid1=837.90 ask1=838.16 flag=49 side=BUY anchor=1/0
```

</details>

**채널** — `SYSTEM`×482

**컴포넌트 상위 15** — `System`×61, `CybosSub`×49, `CybosRT-TICK`×37, `SYSTEM`×25, `BrokerSync`×20, `BalanceUI`×20, `Capital`×20, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `Notify`×12, `Account`×10, `CybosDailyPnl`×10, `WarmupRetrain`×10

### `logs/20261023_SIGNAL.log` — 16.0KB · 148행 · 최종 08:59:00

- 형식 평문 · 시각 인식 148행 · WARNING=42, INFO=106

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-10-23 08:55:00 [WARNING] SIGNAL: [ScalerRefresh] 10m CORE 'ofi_norm' raw_std≈0(0.0465) → identity(0,1) 강제 (FLAT 100% 방지)
2026-10-23 08:55:00 [WARNING] SIGNAL: [ScalerRefresh] 15m CORE 'ofi_norm' raw_std≈0(0.0465) → identity(0,1) 강제 (FLAT 100% 방지)
2026-10-23 08:55:00 [WARNING] SIGNAL: [ScalerRefresh] 30m CORE 'ofi_norm' raw_std≈0(0.0465) → identity(0,1) 강제 (FLAT 100% 방지)
2026-10-23 08:55:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-10-23 08:59:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 42 | 08:45:10 | 08:55:00 | 1m CORE 'cvd_divergence' raw_std≈0(0.0235) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×148

**컴포넌트 상위 15** — `ScalerRefresh`×47, `DynMC`×35, `Model`×30, `ScalerFloor`×18, `TimeRouter`×6, `EnsembleGater`×5, `FeatureBuilder`×5, `GapOffset`×1, `MA-cont`×1

### `logs/20261023_LEARNING.log` — 246.9KB · 1356행 · 최종 08:59:00

- 형식 평문 · 시각 인식 1356행 · WARNING=685, INFO=671

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:23 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.2001 < conf_floor=0.3300 (span=0.00021 auc=0.548 out_max=0.2001, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.498 out_max=0.2477 (기준 auc<0.53 and span<0.020, 기저율=0.2476 n=105) → 보정 미적용, raw 통과
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00007 auc=0.476 out_max=0.4000 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=80) → 보정 미적용, raw 통과
2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00058 auc=0.453 out_max=0.2877 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
  …
2026-10-23 08:48:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-23 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-23 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-23 08:55:10 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=6325, ver=5)
2026-10-23 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 215 | 04:38:26 | 08:41:01 | 축퇴 감지 — span=0.00007 auc=0.476 out_max=0.4000 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 205 | 04:38:26 | 08:41:00 | 하한 도달불가 — out_max=0.2001 < conf_floor=0.3300 (span=0.00021 auc=0.548 out_max=0.2001, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 110 | 04:38:26 | 08:40:59 | 축퇴 감지 — span=0.00058 auc=0.453 out_max=0.2877 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:5m` | 100 | 04:38:26 | 08:40:59 | 축퇴 감지 — span=0.00027 auc=0.521 out_max=0.3766 (기준 auc<0.53 and span<0.020, 기저율=0.3765 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:10m` | 30 | 04:38:27 | 08:41:00 | 하한 도달불가 — out_max=0.2508 < conf_floor=0.3300 (span=0.00127 auc=0.715 out_max=0.2508, 기저율=0.2500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 20 | 04:38:27 | 08:40:59 | 하한 도달불가 — out_max=0.3233 < conf_floor=0.3300 (span=0.00294 auc=0.582 out_max=0.3233, 기저율=0.3217 n=115) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 5 | 04:38:35 | 08:41:01 | 복원한 보정기가 축퇴 상태 — span=0.00797 auc=0.530 out_max=0.2787 (n=5112) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×1356

**컴포넌트 상위 15** — `Calibration:30m`×420, `Calibration:1m`×400, `Calibration:3m`×210, `Calibration:5m`×190, `Calibration:10m`×55, `Calibration:15m`×30, `ExtremityCorrector`×10, `Calibration:ensemble`×10, `Consolidator`×10, `RF`×5, `DriftAdjuster`×5, `SHAP`×5, `ScalerWarmup`×5, `MetaConf`×1

### `logs/20261023_MICRO.log` — 36.7KB · 102행 · 최종 08:59:20

- 형식 평문 · 시각 인식 102행 · DEBUG=102

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 08:45:10 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=831.52/1 ask1=832.26/1 mp={'microprice_tick': 831.89, 'midprice_tick': 831.89, 'depth_bias_tick': -0.0792} mlofi_tick=None queue=None
2026-10-23 08:45:11 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=831.52/1 ask1=832.26/1 mp={'microprice_tick': 831.89, 'midprice_tick': 831.89, 'depth_bias_tick': -0.0792} mlofi_tick=0.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0, …
2026-10-23 08:45:11 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=831.72/1 ask1=832.30/1 mp={'microprice_tick': 832.01, 'midprice_tick': 832.01, 'depth_bias_tick': -0.0484} mlofi_tick=4.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-23 08:45:11 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=832.22/1 ask1=832.28/1 mp={'microprice_tick': 832.25, 'midprice_tick': 832.25, 'depth_bias_tick': -0.0092} mlofi_tick=-0.05 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-10-23 08:45:11 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=831.72/1 ask1=832.28/1 mp={'microprice_tick': 832.0, 'midprice_tick': 832.0, 'depth_bias_tick': 0.0091} mlofi_tick=-2.6833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0,…
  …
2026-10-23 08:59:01 [DEBUG] MICRO: [MICRO-TICK] #6400 bid1=841.08/1 ask1=841.28/1 mp={'microprice_tick': 841.18, 'midprice_tick': 841.18, 'depth_bias_tick': -0.0222} mlofi_tick=-0.1333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
2026-10-23 08:59:10 [DEBUG] MICRO: [MICRO-TICK] #6500 bid1=841.34/2 ask1=841.76/1 mp={'microprice_tick': 841.62, 'midprice_tick': 841.55, 'depth_bias_tick': 0.2534} mlofi_tick=-7.8 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.6…
2026-10-23 08:59:20 [DEBUG] MICRO: [MICRO-TICK] #6600 bid1=840.02/1 ask1=840.12/1 mp={'microprice_tick': 840.07, 'midprice_tick': 840.07, 'depth_bias_tick': 0.0737} mlofi_tick=-1.0 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.69…
2026-10-23 08:59:31 [DEBUG] MICRO: [MICRO-TICK] #6700 bid1=838.50/2 ask1=838.90/1 mp={'microprice_tick': 838.7667, 'midprice_tick': 838.7, 'depth_bias_tick': 0.1387} mlofi_tick=-2.7833 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-10-23 08:59:42 [DEBUG] MICRO: [MICRO-TICK] #6800 bid1=837.96/1 ask1=838.32/1 mp={'microprice_tick': 838.14, 'midprice_tick': 838.14, 'depth_bias_tick': 0.0717} mlofi_tick=5.2333 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
```

</details>

**채널** — `MICRO`×102

**컴포넌트 상위 15** — `MICRO-TICK`×88, `MICRO-MINUTE`×14

### `logs/20261023_DATA.log` — 892B · 4행 · 최종 08:58:43

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+50 individual=-112 institution=+120 oi=0 call_foreign=+40 put_foreign=+496 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-23 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-23 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+71 individual=-128 institution=+117 oi=0 call_foreign=+95 put_foreign=+442 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-23 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
  …
2026-10-23 08:58:13 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+50 individual=-112 institution=+120 oi=0 call_foreign=+40 put_foreign=+496 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-23 08:58:13 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-23 08:58:43 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+71 individual=-128 institution=+117 oi=0 call_foreign=+95 put_foreign=+442 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-23 08:58:43 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
```

</details>

**채널** — `DATA`×4

**컴포넌트 상위 15** — `CybosInvestor`×4

### `logs/20261023_PROBE.log` — 12.5KB · 8행 · 최종 08:58:43

- 형식 평문 · 시각 인식 8행 · INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-23 04:38:45 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056B']
2026-10-23 06:17:29 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056B']
2026-10-23 06:24:27 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056B']
2026-10-23 06:27:16 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056B']
2026-10-23 08:41:10 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056B']
  …
2026-10-23 06:27:16 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056B']
2026-10-23 08:41:10 [INFO] PROBE: [CybosInvestorProbe] not implemented; extra_codes=['A056B']
2026-10-23 08:58:13 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
2026-10-23 08:58:13 [INFO] PROBE: [CybosProbe][RAW] CpSysDib.CpSvrNew7221 field_limit=64 headers={0: '28', 1: '28', 2: '75'} rows_sample=[{0: '0', 1: '0', 2: '0', 3: '0', 4: '0', 5: '0', 6: '0', 7: '0', 8: '0', 9: '0', 10: '0', 11: '0', 12: '0', 13: '0', 14: '0', 15: '0', 16: '0', 17: '0', 18: '0',…
2026-10-23 08:58:43 [INFO] PROBE: [CybosProbe] CpSysDib.CpSvrNew7221 ok status=0 nonempty_headers=3 rows=30
```

</details>

**채널** — `PROBE`×8

**컴포넌트 상위 15** — `CybosInvestorProbe`×5, `CybosProbe`×3

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

### 메인 스레드 블로킹 3건 · 최대 4750ms · 5초 초과 0건

상위 — 4750ms, 4437ms, 3875ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261023_WARN.log`
```
--- 메인 스레드 블로킹 ×3(표본)
04:38:49 2026-10-23 04:38:49 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4437ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4437 band=INFO since_pipe_s=NA
08:41:14 2026-10-23 08:41:14 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4750 band=INFO since_pipe_s=NA
08:41:18 2026-10-23 08:41:18 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3875ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3875 band=INFO since_pipe_s=NA
```

### `logs/20261023_SYSTEM.log`
```
--- [Shutdown] ×4(표본)
06:15:56 2026-10-23 06:15:56 [INFO] SYSTEM: [Shutdown] intent=user_restart keep_alive=True files=0 recent_stall=none
06:23:26 2026-10-23 06:23:26 [INFO] SYSTEM: [Shutdown] intent=user_close keep_alive=False files=2 recent_stall=none
06:25:04 2026-10-23 06:25:04 [INFO] SYSTEM: [Shutdown] intent=user_close keep_alive=False files=2 recent_stall=none
06:27:32 2026-10-23 06:27:32 [INFO] SYSTEM: [Shutdown] intent=user_close keep_alive=False files=2 recent_stall=none
```

### `logs/20261023_SIGNAL.log`
```
--- 기동 복원 ×8(표본)
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
04:38:18 2026-10-23 04:38:18 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
```

### `logs/20261023_LEARNING.log`
```
--- 축퇴 ×8(표본)
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.2001 < conf_floor=0.3300 (span=0.00021 auc=0.548 out_max=0.2001, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00006 auc=0.498 out_max=0.2477 (기준 auc<0.53 and span<0.020, 기저율=0.2476 n=105) → 보정 미적용, raw 통과
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00007 auc=0.476 out_max=0.4000 (기준 auc<0.53 and span<0.020, 기저율=0.4000 n=80) → 보정 미적용, raw 통과
04:38:26 2026-10-23 04:38:26 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00058 auc=0.453 out_max=0.2877 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261023_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 4 | 08:41:01 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 04:38 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261023_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:41:10 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 15 | 08:50:22 [WARNING] 그리기 99.6ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 1048x1024 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 12 | 08:56:35 [WARNING] paintEvent slow 32.2ms | size=1484x950 candles=12 grid=10.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=… |

- 이 로그 생존구간: 04:38 ~ 08:58

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261023_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 99 | 08:40:47 [INFO] 활성화 | file=logs\crash_fault.log PID=3624 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 107 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 70 | 08:54:00 [INFO] code=A056B from=08:53 to=08:54 |

- 이 로그 생존구간: 04:38 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261023_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 62 | 08:45:10 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0235) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 15 | 08:50:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0468) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 8 | 08:55:00 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0465) → identity(0,1) 강제 (FLAT 100% 방지) |

- 이 로그 생존구간: 04:38 ~ 08:59

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
| **오늘 20261023** | **08:59** | 로그 본문 |

- 델타 **-408분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-22 (MW0601 704차 후속 — [9842] 행사가 × 투자자 수집기 구현 · `STRIKE_INVESTOR_FLOW_ENABLED=False` 배포) — 🟡 **구현 완료 · 라이브 미검증**
## 2026-10-22 (MW0601 704차 후속3 — [9842] 수집기 활성화 · 장후 기간 스냅샷 예약작업 등록) — 🟢 **사용자 지시**
## 2026-10-22 (MW0601 705차 — 장후 점검, 종합 완성본)
## 2026-10-22 (MW0601 705차 — 신동 일일 리포트 vs 실거래 패널 불일치: 실거래 대사 절 · 보유 중 신호 기록 · 실집행 누적 참고 행) — 🟢 **사용자 지시 A·B·C**
## 2026-10-22 (MW0601 705차 후속 — COM 예약작업 RunLevel 공용 판정기 · 704-6 해소) — 🟢 **사용자 지시 · 매매 코드 무변경**
## 2026-10-22 (MW0601 705차 후속4 — 장후 자동조치: F-27 전제 반박 → 라벨 자기대사 축 보강 · G-1 · G-2) — 🟢 **자동조치(A등급) · 매매 경로 무변경**
## 2026-10-22 (MW0601 705차 후속5 — 청산 라벨 외부 주체 분기 신설 (705b-2) · 쌓인 점검 문서 일괄 커밋) — 🟢 **사용자 지시 「1, 2 진행해」 · 매매 경로 무변경**
## 2026-10-23 (MW0601 706차 — CREON 실거래 런처 실패 경로: 08:35 트리거 봉쇄 · 잘못된 세션 방치 · 저장 ID 계측) — 🟢 **사용자 지시 「2–3번 진행하고 개선안 구현해」 · 매매 경로 무변경**
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
T_TARGET1"` 도 신동 1차익절 대응으로 센다.
- How to apply: 기존 7행은 `OTHER` 로 남는다(소급 안 함 — 490차 관례). 이 라벨 세대 경계 = 다음 재기동. `exit_stage` 집계 시 2026-10-22 이전 `OTHER` 는 신동·피터2 청산이 섞여 있다.
- 검증: `test_490` 통과, `test_705b` 12건 통과. 관련 40파일 575 passed / 2 failed — `test_virtual_book::test_main_dispatch_is_isolated`(py37 에 `ast.get_source_segment` 없음) · `test_554::test_missing_reference_skips_check_but_is_not_silent`(test_virtual_book 과 함께 돌 때만 실패, HEAD 코드에서도 동일 재현) — 둘 다 기존 실패.
- 문서 일괄 커밋: 10-19~10-22 점검리포트·증거 · 신동2 해설/학습 · 피터2 실시간/일일 · 신동 일일 · `config/dailycheck_targets.json`(F-1) · 수익률향상 누적대장.

## 2026-10-23 (MW0601 706차 — CREON 실거래 런처 실패 경로: 08:35 트리거 봉쇄 · 잘못된 세션 방치 · 저장 ID 계측) — 🟢 **사용자 지시 「2–3번 진행하고 개선안 구현해」 · 매매 경로 무변경**

- 증상: 04:12 `CREON Plus` 작업 **수동 실행**(이벤트 110)에서 `/prj:cp /id:smart7na` 가 **Smart1na 계좌 783293269** 로 사인온 → 가드가 실패 처리(주문 위험 없음). 그런데 ① `:end_error` 가 `PAUSE` + `CMD /K` 로 창을 붙잡아 작업이 Running 으로 남음 — 작업은 `MultipleInstances=IgnoreNew`·시간제한 없음이라 **08:35 트리거가 무시될 상태**였다 ② 실패 뒤 Smart1na 세션(CpStart 5596·DibServer 27860)이 그대로 생존 — 10-16 08:35 좀비 크래시 경로 ③ 런처 콘솔에 `'��그램' is not recognized` — 한글 REM 줄(구 218행 「보안 프로그램」)이 잘려 명령으로 실행됨.
- 조치(운영): 사용자가 창을 닫음 → Smart1na 세션을 `_kill_cybos_procs(_REAL_KILL_NAMES)`(PlusDisconnect)로 정리 → 04:25 재실행 — **재현**(783293269, 7초).
- 결정(코드):
  1. `LAUNCH_API.bat :end_error` — `PAUSE`/`CMD /K` 제거 → `TIMEOUT /T 600` + `EXIT /B 1`. 04:25 재실행에서 작업이 rc=1 로 종료(04:26:17)되는 것 확인.
  2. `scripts/cybos_autologin.py` 계좌 불일치 경로 — 레지스트리 판독 후 **잘못된 세션을 내리고** False. 재시도는 하지 않는다(같은 명령은 같은 계좌로 붙는다 — 10-15 12:20·13:22, 10-23 04:12·04:25). 04:26:04 `IsConnect=0` 확인.
  3. 같은 파일 `_starter_registry_snapshot()` 신설(읽기 전용) — `CREON\starter`·`CREON\dstarter`·`DAISHIN\starter` 의 LoginID·저장 계좌(PNA-MA-REM)·키 수정시각을 로그인 전/성공/실패 시점에 `[DIAG]` 로 남긴다.
  4. `LAUNCH_API.bat` 한글 REM 25줄 → ASCII.
- 관측(가설 D 재료, **미확정**): 실패 2회 모두 로그인 전 `CREON\starter LoginID=SMART7NA`(10-15 13:35 이후 무변경)인데 `CREON\dstarter`(HTS 키: SMART1NA·783293269)와 `DAISHIN\starter`(SMART5NA·783293269)가 **API 로그인 도중에 갱신**됐다 → `/prj:cp` 가 자기 키가 아니라 이 두 키를 쓰고 있다. 다만 HTS 는 매일 08:42 Smart1na 로 로그인하는데 10-16–10-22 아침 API 는 성공했으므로 "dstarter=SMART1NA 이면 실패"로는 설명이 안 된다. 성공일 표본이 쌓이면 대조한다.
- P2(보류): 로그인 전 dstarter/DAISHIN 저장 ID·계좌를 smart7na/783343908 로 맞추는 안 — HTS 설정과 얽혀 D 확정 전에는 넣지 않는다.
- How to apply: 오늘 08:35 전에 10-15 방식(CREON Plus 로그인 창에서 smart7na 직접 로그인 + 「아이디 저장」) 으로 복구가 필요하다. 이후 매일 `creon_autologin_diag.log` 의 `[DIAG]` 줄을 성공/실패별로 비교.
- 검증: `tests/test_706_launcher_fail_path.py` 5건 + 관련(631·692·564) 합계 35 passed.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · 마지막 갱신 2026-10-22 17:55

최근 헤딩 8개:
```
### 2026-10-22 (MW0601 703차 — F-701-A ProfitGuard 계좌 축)
### 2026-10-22 (MW0601 — 장전 점검)
### 2026-10-22 (MW0601 — 장중 점검)
### 2026-10-22 (MW0601 704차 — [9842] CpSvr9842 실계좌 사용 가능)
### 2026-10-22 (MW0601 705차 — 장후 점검)
### 2026-10-22 (MW0601 705차 — 신동 리포트 실거래 대사)
### 2026-10-22 (MW0601 705차 후속4 — 장후 자동조치)
### 2026-10-22 (MW0601 705차 후속5 — 사용자 지시)
```

미완료 체크박스 **3316건** (끝에서 30건)
```
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
- [ ] **704-5 (다음 거래일)** 재기동 후 장중 수집 첫날 확인 — `[StrikeInvestor] stored=… (오늘 첫 수집 — 전체 저장)` · `strike_investor_flow_status` ok=1 비율 · `BLOCKED`/`EMPTY` 0건. 16:25 예약작업 `LastTaskResult=0` · `logs/<date>…
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
iff 직접 확인). 라이브 전환은 사용자 결정(704-1 잔여 ⓐⓑⓒ) 대기.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation — 오늘로 8거래일 연속 재현, 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **O-4 계열** 계좌 잔고 vs 사이저 기준자본 괴리 — 종가 즈음 약 28,359,139원 추정, 하루치 단독 판정 금지 설계 그대로.

### 2026-10-22 (MW0601 705차 — 신동 리포트 실거래 대사)
- [ ] **705-1 (재기동 후 첫 거래일)** `[ShindongExec] … 보유 중(…), 새 신호 미집행` 로그와 `SKIP_HOLDING` 이벤트 → 리포트 §2-1 「재생만」 사유가 「집행 기록 없음(미측정)」 대신 「보유 중」으로 찍히는지.
- [ ] **705-2 (조사)** 10/21 리포트 MAIN +104.8만 vs 실거래 +222.7만 — 오늘과 반대 방향 차이. `python scripts/shindong_daily_report.py 2026-10-21` 재생성 후 §2-1로 분해.
- [ ] **705-3 (결정 대기)** 신동 판정 기준 — 사전등록 MAIN 재생 vs 실집행. 철회 후 집행 거래를 채점에 넣을지는 사전등록 §6(새 버전·재채점) 안건.

- [ ] **705-4 (조건부)** 이 PC 에서 **UAC 를 다시 켜면**(재부팅 필요) 직후 `powershell -File scripts/audit_com_task_runlevel.ps1` → 백필·정규수집·9842 스냅샷 3종을 각 `*_task.ps1` 로 재등록(Highest). 안 하면 매일 IsConnect=0 으로 조용히 실패.

### 2026-10-22 (MW0601 705차 후속4 — 장후 자동조치)
- [x] **F-27 처분: 전제 반박** — 신동1차 뒤 하드스톱은 본전 이동 뒤 트레일이라 `TRAIL_AFTER_TP1` 이 맞다. 라벨 무변경, `recon_exit_stage_labels` 에 `external_target`(신동 1차익절 대응) 버킷 신설로 오경보 해소. 위 F-27 항목·O-t4 는 이것으로 대체.
- [ ] **705b-1 (다음 신동 「1차 익절 → 하드스톱」 날)** `[ExitStageRecon]` 이 INFO · `신동 1차익절 대응 1 · 미대응 0` 으로 찍히는지.
- [ ] **705b-2 (사용자 결정)** 라벨 체계에 외부 주체 사유 분기(`신동1차`→예: `EXT_TARGET1`) 신설 여부 — `test_490_exit_stage::test_실DB의_모든_exit_reason이_분류된다` 실패가 이것을 요구한다(702-1 별건과 동일). 라벨 체계 변경이라 자동조치 범위 밖.
- [x] **G-1·G-2 구현** — 수집기 근거 추적(`rationale_trace`) · 다른 날짜 파일 오매칭 제외(`foreign_date_in_name`). 다음 장전 다이제스트 §1에 `⚠ 다른 날짜(…) 파일` 주석, §11에서 `retrain_intraday_2026…` 이 다이제스트되지 않는지 1차 확인.
- [ ] **705b-3 (기존 테스트 실패 6건 — 이번 변경 밖)** `test_498` 2건(704차 `strike_investor_flow.py` IDX_INS/StrikeInvestor · 705차 `shindong/daily_report.py` 대사 문구 태그 미등록) · `test_457` dashboard `peter_paste` 폴백 플래그 · `test_493` `generate_validation_campaign_report.py:7931` 라이브 요율 · `test_483` fuoption 사본 불일치 · `test_490` 실DB 사유 미분류(705b-2). 각 원 커밋 세션이 처리할 것.

### 2026-10-22 (MW0601 705차 후속5 — 사용자 지시)
- [x] **705b-2 완료** — 청산 라벨 외부 주체 분기(`EXT_TARGET1`·`EXT_TARGET2`·`EXT_INSTRUCTED`) 신설, `test_490` 실DB 커버리지 통과.
- [ ] **705c-1 (다음 재기동 후 첫 신동 청산일)** `trades.exit_stage` 에 `EXT_TARGET1`/`EXT_TARGET2` 가 찍히고, 1차 익절 뒤 하드스톱은 `TRAIL_AFTER_TP1` · `[ExitStageRecon]` 미대응 0 인지.
- [x] **장후 사용자 조치 1 완료** — 10-19~10-22 누적 점검 문서 일괄 커밋.
- [ ] (705b-3 보강) `test_554::test_missing_reference_skips_check_but_is_not_silent` 는 `test_virtual_book` 과 같이 돌 때만 실패(실행 순서 간섭, HEAD 에서도 재현) · `test_virtual_book::test_main_dispatch_is_isolated` 는 py37 미지원 `ast.get_source_segment` 사용.

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

### `data/heartbeat_MW0601_20261023.json` — 244B · 10-23 08:59:11
```json
{
 "pid": 3624,
 "written_at": "2026-10-23T08:59:41",
 "beat_epoch": 1792713580.5214481,
 "beat_age_sec": 0.8,
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

### `data/peter_feed/_raw/2026-10-23.jsonl` — 327B · 10-23 08:50:58
```json
{
 "id": "2113417767793926641",
 "dt": "2026-10-22T23:50:35.000Z",
 "text": "오늘은 19일 월요일처럼\n\n갭하락후 어느정도는 올릴 수 있지만\n\n쭉 말아 올리는 패턴이 오늘은 어렵습니다.\n\n우선 지켜보고 코멘트 하겠습니다.",
 "seen_at": "2026-10-23T08:50:58+09:00",
 "src": "live"
}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-23 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-23)과 일치 |
|---|---|---|
| `date` | 2026-10-23 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-23 08:55:11 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-22) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-23 08:55:11 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-22) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **08:58** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 08:59 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 14 |
| `session_bars` 당일 행수 | 14 (기대 411) |

- 미도래 **370봉** (08:59~15:08) — 수집 시각 08:59 이후라 결손·영구결손에서 제외
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
| 3624 | 08:40:47 | 없음 | 없음 | 판정불가 — WER **미측정** |


#### 재기동 귀속 대사 (684차 G-5)

| 재시작 | 런처 분류 | 종료 의도 로그(−3~+1분) | ±5분 이내 커밋(설명 후보) | 창 밖 당일 커밋 |
|---|---|---|---|---|
| 06:15 | 일시적 크래시 | 06:15 `user_restart` | 06:17 `0a880ff9` [MW0601] 707차 후속2: dev 실전 자본 3층 켜짐 기록 — 이식 메모 갱신 …, 06:12 `54144e55` [MW0601] 707차 후속: 실전 자본 3층 dev 배포 기록 — 이식 메모 (dev…, 06:11 `be41c470` [MW0601] 708차: 신동 실거래 출처 분리 · 철회 섀도 계측 | 2건(시각 불일치 — 후보 아님) |

- 🔴 커밋은 **인과가 아니라 후보**다. 창 밖 커밋을 원인으로 적지 말 것.
- 「종료 의도 로그 **없음**」 + `[CLEAN EXIT]` 있음 = 의도 경로를 거치지 않은 정상 종료다. ⚠ **684차 이전**의 X 버튼 종료(`user_close`/`user_restart`)는 로그 파일에 남지 않았다(모듈 로거가 파일 핸들러에 안 붙어 있었다) — 그 시기의 「없음」은 X 버튼 재시작을 배제하지 못한다.

> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 244개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261022-점검리포트.md` | 72.3KB | 10-22 17:55 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_post.md` | 102.7KB | 10-22 16:18 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_intra.md` | 83.8KB | 10-22 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261022_pre.md` | 65.5KB | 10-22 08:59 |
| `docs/정기점검/매일점검/MW0601-20261021-점검리포트.md` | 70.3KB | 10-21 17:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_post.md` | 103.3KB | 10-21 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_intra.md` | 85.3KB | 10-21 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_pre.md` | 63.6KB | 10-21 08:59 |

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

1. `logs/20261023_LEARNING.log`: **축퇴** 8건(표본)
2. `logs/crash_fault.log`: `Windows fatal exception` **6건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
3. 미커밋 변경 2건 (실질 1건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261023*.log` (Windows) / `grep 강제청산 logs/*20261023*.log`*