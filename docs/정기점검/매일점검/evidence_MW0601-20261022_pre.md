# 미륵이 증거 다이제스트 — 2026-10-22 / PRE

- 생성 2026-10-22 08:59:12 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01hft7omnunrorktz9gpyjns/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261022` · `2026-10-22` · `261022` · `1022`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **21개** 파일 · 21개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261022.log` | 125B | 10-22 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261022.log` | 198B | 10-22 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261022.json` | 244B | 10-22 08:59 |
| `launcher_{DATE}_084001_24599.log` | 1 | `logs/Mireuk_batch/launcher_20261022_084001_24599.log` | 54.2KB | 10-22 08:58 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261022.log` | 109B | 10-22 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261022.log` | 2.1KB | 10-22 08:59 |
| `retrain_intraday_20260624_{DATE}56.log` | 1 | `logs/retrain_intraday_20260624_102256.log` | 4.6KB | 06-24 10:23 |
| `retrain_intraday_20261015_{DATE}00.log` | 1 | `logs/retrain_intraday_20261015_102200.log` | 3.2KB | 10-15 10:22 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261022.log` | 2.4KB | 10-22 08:56 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-22.jsonl` | 819B | 10-22 08:47 |
| `{DATE}_DATA.log` | 1 | `logs/20261022_DATA.log` | 892B | 10-22 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261022_DEBUG.log` | 0B | 10-22 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261022_HEALTH.log` | 0B | 10-22 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261022_HOGA.log` | 1.3MB | 10-22 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261022_LEARNING.log` | 47.4KB | 10-22 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20261022_MICRO.log` | 32.3KB | 10-22 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20261022_PROBE.log` | 12.1KB | 10-22 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261022_SIGNAL.log` | 5.0KB | 10-22 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261022_SYSTEM.log` | 28.4KB | 10-22 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261022_TRADE.log` | 167B | 10-22 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261022_WARN.log` | 4.7KB | 10-22 08:58 |

## 2. 코드·커밋 상태

- HEAD `87ee17cc` · 브랜치 `v9-dev` · 미커밋 38건 · 실질 변경 6건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 6 · 미추적 32 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 5.0초(`git status --porcelain`)
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
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261019.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261020.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261021.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261020.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261021.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261022.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261019.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261020.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261021.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_claude_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261020.md
?? docs/신동거래/일일/신동_일일_MW0601_20261020.svg
?? docs/신동거래/일일/신동_일일_MW0601_20261021.md
?? docs/신동거래/일일/신동_일일_MW0601_20261021.svg
?? docs/정기점검/매일점검/MW0601-20261019-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261020-점검리포트.md
?? docs/정기점검/매일점검/MW0601-20261021-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261020_pre.md
?? docs/정기점검/매일점검/evidence_MW0601-20261021_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261021_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261021_pre.md
```

**당일(2026-10-22) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
87ee17cc [MW0601] 703차: F-701-A ProfitGuard 계좌 축(주체 3종 실현 net 합) · 신동·피터2 관문 배선 · L4 축 통일 · L3 카운터 부활
d76d1307 [MW0601] 702차 후속: F-10 dev 이식 메모 — tp1_reached 오염 경로·측정 쿼리·이식 범위 (MW0602 판단용)
7a4f6387 [MW0601] 702차: F-10 — exit_stage 라벨 축 분리(tp1_protect_armed), 하드스톱 분할체결 TRAIL_AFTER_TP1 오분류 해소
```

**최근 커밋 12건**
```
87ee17cc [MW0601] 703차: F-701-A ProfitGuard 계좌 축(주체 3종 실현 net 합) · 신동·피터2 관문 배선 · L4 축 통일 · L3 카운터 부활
d76d1307 [MW0601] 702차 후속: F-10 dev 이식 메모 — tp1_reached 오염 경로·측정 쿼리·이식 범위 (MW0602 판단용)
7a4f6387 [MW0601] 702차: F-10 — exit_stage 라벨 축 분리(tp1_protect_armed), 하드스톱 분할체결 TRAIL_AFTER_TP1 오분류 해소
ec6e9e83 [MW0602] research_snapshot --status cp949 콘솔 크래시 수정 (en-dash → ~)
96823eba [MW0601] 701차: DECISION_LOG — 연구용 장후 사본 신설 · regime_history 보존 무변경 · 가격패턴 연구 양방향 공유
555ab45b [MW0601] 701차: CLAUDE.md 멀티PC 절 — docs/가격움직임패턴연구/ 양방향 공유 예외 (사용자 지시)
1808af74 [MW0601] 701차 [가격패턴]: 선물시장 국면 분류 연구 — 조사 보고서·근거 노트·표본 실측·양방향 공유 규약
48f1f658 [MW0601] 701차: 연구용 장후 사본 research_snapshot — ensemble_decisions 삭제 없는 증분 아카이브
50dcb0f1 [MW0601] 신동 실거래 수량 SHINDONG_LIVE_QTY 1 → 2 (사용자 결정 2026-10-21)
26b8e9c3 [MW0601] 700차: 신동 섀도 SHADOW_ATRS(R3 손절 0.25×ATR14) · TR44 반사실 · 방향 적중 비교 자료
d63de063 [MW0601] 699차 후속: 신동 보완 분석 세션 자료 모음 — docs/미륵이고도화3/신동2/신동보완분석_MW0601-20261020/
8a1ddebc [MW0601] 699차 후속: DECISION_LOG 제목 정정 — 「실주문 로직 변경」 → 「가상 집행 변경 — 신동 선택 시 실주문」
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

### 차단 게이트 전수 인벤토리 — 46개 중 **10개 꺼짐**

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

_본문 미열람(설정): `20261022_HOGA.log` 1.3MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/16개 (중요도순). 제외: `20261022_DATA.log`, `20261022_PROBE.log`, `launcher_20261022_084001_24599.log`, `shindong2_20261022.log`, `peter2_receiver_20261022.log`, `freeze_sentinel_20261022.log`, `force_flat_guard_20261022.log`, `maekjeom_ladder_20261022.log`_

### `logs/20261022_TRADE.log` — 167B · 2행 · 최종 08:41:02

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:57 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-22 08:41:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-22 08:40:57 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-22 08:41:02 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261022_WARN.log` — 4.7KB · 24행 · 최종 08:58:48

- 형식 평문 · 시각 인식 24행 · WARNING=24

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-22 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 16ms
2026-10-22 08:41:05 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr27)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-22 08:41:05 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr27)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-22 08:41:05 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 266ms account=783343908
  …
2026-10-22 08:47:16 [WARNING] SYSTEM: [OptionFlowChart] 그리기 106.2ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 837x1001
2026-10-22 08:52:35 [WARNING] SYSTEM: [Peter2Offset] A056B 실측=-1.39 n=7 spread=0.13 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.39 | 직전일=-1.82(prev_day:2026-10-19, safe=True) 차=0.43 | 50ms
2026-10-22 08:56:12 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 45.7ms | size=1484x930 candles=12 grid=23.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.7 cross=0.0 | slow_cnt=1 total_cnt=50 overlay_cnt=182
2026-10-22 08:58:06 [WARNING] SYSTEM: [Peter2] 오프셋 자동 적용 -1.82(prev_day:2026-10-19, safe=True) → -1.45(live:08:58:05, safe=True)
2026-10-22 08:58:48 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 34.1ms | size=1484x930 candles=14 grid=7.4 spans=0.0 candles=1.0 dir=0.0 regime=0.0 markers=0.0 axes=24.7 cross=0.0 | slow_cnt=2 total_cnt=80 overlay_cnt=383
```

</details>

**WARNING — 태그 10종 (상위 10)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 8 | 08:41:05 | 08:41:06 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `CybosDailyPnl` | 2 | 08:41:05 | 08:41:05 | 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr27)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용 |
| `출처축` | 2 | 08:41:05 | 08:41:05 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT', 'SHINDONG'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `Capital` | 2 | 08:41:05 | 08:41:05 | 기준자본(15,000,000원)과 실제잔고(27,232,318원) 괴리 +81.5% — 계좌가 바뀌었거나 자본 설정이 낡았을 수 있습니다(config/settings.py:SIZING_TARGET_CAPITAL_KRW). |
| `SessionStateDrop` | 2 | 08:41:05 | 08:41:05 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-10-21 → 2026-10-22)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `OptionFlowChart` | 2 | 08:41:15 | 08:47:16 | 그리기 70.6ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 785x1001 |
| `Peter2Offset` | 2 | 08:47:05 | 08:52:35 | A056B 실측=-1.11 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-1.11 | 직전일=-1.82(prev_day:2026-10-19, safe=True) 차=0.71 | 64ms |
| `ChartDBG` | 2 | 08:56:12 | 08:58:48 | paintEvent slow 45.7ms | size=1484x930 candles=12 grid=23.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.7 cross=0.0 | slow_cnt=1 total_cnt=50 overlay_cnt=182 |
| `SessionBackfill` | 1 | 08:41:35 | 08:41:35 | 2026-10-21 차트 보충 — chart=411 existing=411 inserted=0 mismatch=26 |
| `Peter2` | 1 | 08:58:06 | 08:58:06 | 오프셋 자동 적용 -1.82(prev_day:2026-10-19, safe=True) → -1.45(live:08:58:05, safe=True) |

**채널** — `SYSTEM`×24

**컴포넌트 상위 15** — `LiveDBG`×8, `CybosDailyPnl`×2, `출처축`×2, `Capital`×2, `SessionStateDrop`×2, `OptionFlowChart`×2, `Peter2Offset`×2, `ChartDBG`×2, `SessionBackfill`×1, `Peter2`×1

### `logs/20261022_SYSTEM.log` — 28.4KB · 218행 · 최종 08:59:05

- 형식 평문 · 시각 인식 212행 · INFO=212, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=19924 | 행감지=30s all_threads=True
2026-10-22 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.48s | predictions=0.05s trades=0.24s daily_stats=0.01s shap=0.01s raw_data=0.12s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-22 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-22 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-22 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-22 08:59:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:58 vol=142 | live_buy=71 shadow_buy=53 anchor_buy=53 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-10-22 08:59:00 [INFO] SYSTEM: [PreMarket] Phase4 refit 기동 (14봉 z경고=4개)
2026-10-22 08:59:01 [INFO] SYSTEM: [PreMarket] Phase4 refit 완료 n=30봉 z경고 4→4개 | 잔존=atr,avg_volume,institution_futures_net,microprice_bias
2026-10-22 08:59:05 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=9개 (08:55 최종 4개 대비 +5) — 재측정만, 재적합 없음
2026-10-22 08:59:20 [INFO] SYSTEM: [TickUI] alive ticks=2234 code=A056B close=878.46
```

</details>

**채널** — `SYSTEM`×212

**컴포넌트 상위 15** — `CybosRT-TICK`×27, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `Capital`×4, `LEVELS 08:50`×4

### `logs/20261022_SIGNAL.log` — 5.0KB · 42행 · 최종 08:59:01

- 형식 평문 · 시각 인식 42행 · WARNING=6, INFO=36

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-10-22 08:46:00 [INFO] SIGNAL: [MA-cont] 2026-10-22 연속 MA 버퍼 프라이밍 61봉 (버퍼 61)
2026-10-22 08:48:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase1_3bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-10-22 08:50:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-10-22 08:55:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
2026-10-22 08:59:01 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 6 | 08:45:05 | 08:45:05 | 1m CORE 'cvd_divergence' raw_std≈0(0.0204) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×42

**컴포넌트 상위 15** — `ScalerFloor`×12, `ScalerRefresh`×11, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1

### `logs/20261022_LEARNING.log` — 47.4KB · 263행 · 최종 08:59:01

- 형식 평문 · 시각 인식 263행 · WARNING=130, INFO=133

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00126 auc=0.574 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-22 08:40:47 [INFO] LEARNING: [Calibration:1m] 도달불가 해소 — out_max=0.3301 < conf_floor=0.3300 (n=85) → 보정 재적용
2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00083 auc=0.529 out_max=0.3405 (기준 auc<0.53 and span<0.020, 기저율=0.3400 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00069 auc=0.521 out_max=0.4121 (기준 auc<0.53 and span<0.020, 기저율=0.4118 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-10-22 08:48:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-22 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-22 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-22 08:55:05 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=5090, ver=5)
2026-10-22 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 40 | 08:40:47 | 08:40:56 | 축퇴 감지 — span=0.00069 auc=0.521 out_max=0.4121 (기준 auc<0.53 and span<0.020, 기저율=0.4118 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:1m` | 39 | 08:40:47 | 08:40:56 | 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00126 auc=0.574 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 19 | 08:40:47 | 08:40:54 | 하한 도달불가 — out_max=0.2881 < conf_floor=0.3300 (span=0.00093 auc=0.606 out_max=0.2881, 기저율=0.2875 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:3m` | 18 | 08:40:47 | 08:40:56 | 하한 도달불가 — out_max=0.3253 < conf_floor=0.3300 (span=0.00047 auc=0.615 out_max=0.3253, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:10m` | 9 | 08:40:47 | 08:40:55 | 축퇴 감지 — span=0.00021 auc=0.525 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:15m` | 4 | 08:40:48 | 08:40:54 | 하한 도달불가 — out_max=0.3255 < conf_floor=0.3300 (span=0.00087 auc=0.554 out_max=0.3255, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:ensemble` | 1 | 08:40:56 | 08:40:56 | 복원한 보정기가 축퇴 상태 — span=0.00376 auc=0.483 out_max=0.2870 (n=4816) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×263

**컴포넌트 상위 15** — `Calibration:30m`×79, `Calibration:1m`×76, `Calibration:5m`×36, `Calibration:3m`×34, `Calibration:10m`×17, `Calibration:15m`×6, `ScalerWarmup`×5, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

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

### `logs/retrain_intraday_20261015_102200.log` — 3.2KB · 24행 · 최종 10:22:24

- 형식 평문 · 시각 인식 24행 · WARNING=2, INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-15 10:22:00,385 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-15 10:22:00,385 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-15 10:22:00,386 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-15 10:22:00,386 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-15 10:22:00,386 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_66e97cc6.json
  …
2026-10-15 10:22:24,132 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-15 10:22:24,133 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-15 10:22:24,133 [INFO] LEARNING: [Retrain] 완료 | 21.0초 | 성공=1/1 호라이즌
2026-10-15 10:22:24,134 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 23.7s 데이터=4800행
2026-10-15 10:22:24,135 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_66e97cc6.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 10:22:13 | 10:22:13 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 19253/44084 제외 (418차 결정 1) — 남은 24831행 |
| `UnitMismatch` | 1 | 10:22:13 | 10:22:13 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/24831행 제외 (559차 P1'-2) — 남은 23385행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

### `logs/20261022_MICRO.log` — 32.3KB · 89행 · 최종 08:59:00

- 형식 평문 · 시각 인식 89행 · DEBUG=89

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-22 08:45:05 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=877.78/2 ask1=878.32/1 mp={'microprice_tick': 878.14, 'midprice_tick': 878.05, 'depth_bias_tick': -0.0125} mlofi_tick=None queue=None
2026-10-22 08:45:05 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=877.58/1 ask1=878.32/1 mp={'microprice_tick': 877.95, 'midprice_tick': 877.95, 'depth_bias_tick': -0.1917} mlofi_tick=-3.2833 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.6…
2026-10-22 08:45:05 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=877.78/1 ask1=878.32/1 mp={'microprice_tick': 878.05, 'midprice_tick': 878.05, 'depth_bias_tick': 0.1198} mlofi_tick=4.2833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-10-22 08:45:05 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=877.82/1 ask1=878.32/1 mp={'microprice_tick': 878.07, 'midprice_tick': 878.07, 'depth_bias_tick': 0.2505} mlofi_tick=5.6167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
2026-10-22 08:45:06 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=877.82/1 ask1=878.32/1 mp={'microprice_tick': 878.07, 'midprice_tick': 878.07, 'depth_bias_tick': 0.2863} mlofi_tick=0.25 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0, …
  …
2026-10-22 08:58:28 [DEBUG] MICRO: [MICRO-TICK] #5200 bid1=878.82/1 ask1=878.96/1 mp={'microprice_tick': 878.89, 'midprice_tick': 878.89, 'depth_bias_tick': 0.2346} mlofi_tick=0.0167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-10-22 08:58:45 [DEBUG] MICRO: [MICRO-TICK] #5300 bid1=878.02/1 ask1=878.24/1 mp={'microprice_tick': 878.13, 'midprice_tick': 878.13, 'depth_bias_tick': 0.0219} mlofi_tick=5.2833 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
2026-10-22 08:59:00 [DEBUG] MICRO: [MICRO-TICK] #5400 bid1=877.80/2 ask1=878.02/1 mp={'microprice_tick': 877.9467, 'midprice_tick': 877.91, 'depth_bias_tick': -0.0203} mlofi_tick=2.4333 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio'…
2026-10-22 08:59:00 [DEBUG] MICRO: [MICRO-MINUTE] #14 ts=2026-10-22 08:58:00 close=877.84 bias=0.003011 slope=0.433128 depth_bias=0.0527 mlofi_norm=-0.063464 mlofi_pressure=-1 mlofi_slope=-24.248333 queue_signal=-0.0528 queue_ma=-0.0293 queue_momentum=-0.0140 depletion=0.5000 refill=0.5000 imbalanc…
2026-10-22 08:59:19 [DEBUG] MICRO: [MICRO-TICK] #5500 bid1=878.20/1 ask1=878.38/1 mp={'microprice_tick': 878.29, 'midprice_tick': 878.29, 'depth_bias_tick': -0.0425} mlofi_tick=-3.0667 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio':…
```

</details>

**채널** — `MICRO`×89

**컴포넌트 상위 15** — `MICRO-TICK`×75, `MICRO-MINUTE`×14

## 5. 거래일 요약 — 오늘 무엇을 했는가

_거래일 패턴이 하나도 안 잡혔다. 로그 문구가 바뀌었을 수 있다 — `config/dailycheck_targets.json` 의 `day_summary_patterns` 를 확인하라._

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261022_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
08:40:42 2026-10-22 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
```

### `logs/20261022_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:47 2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 하한 도달불가 — out_max=0.3258 < conf_floor=0.3300 (span=0.00126 auc=0.574 out_max=0.3258, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:47 2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00083 auc=0.529 out_max=0.3405 (기준 auc<0.53 and span<0.020, 기저율=0.3400 n=100) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:47 2026-10-22 08:40:47 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00069 auc=0.521 out_max=0.4121 (기준 auc<0.53 and span<0.020, 기저율=0.4118 n=85) → 보정 미적용, raw 통과 [기존 fitted 해제]
08:40:47 2026-10-22 08:40:47 [INFO] LEARNING: [Calibration:1m] 축퇴 해소 — span=0.00095 auc=0.540 out_max=0.3339 (n=120) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261022_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:57 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261022_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 18 | 08:41:05 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 4 | 08:52:35 [WARNING] A056B 실측=-1.39 n=7 spread=0.13 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.39 | 직전일=-1.82(prev_day:2026-10-1… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 3 | 08:56:12 [WARNING] paintEvent slow 45.7ms | size=1484x930 candles=12 grid=23.4 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=… |

- 이 로그 생존구간: 08:41 ~ 08:58

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261022_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 102 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=19924 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 97 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 63 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261022_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 38 | 08:45:05 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0204) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 3 | 08:50:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:55:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] ela… |

- 이 로그 생존구간: 08:40 ~ 08:59

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
| **오늘 20261022** | **08:59** | 로그 본문 |

- 델타 **-408분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### F-1 — 증거 수집기·점검 체크리스트 기대값 동기화
### F-2 — `[RegimeFingerprint] 백필 0행 제외` 24거래일 연속 경보: **헛경보 확정 (가설 a·b 둘 다 아님)**
## 2026-10-20 (MW0601 699차 — 신동 규격 v3: TR44 → MAIN 승격 · MW0602 보완 판정 사전등록) — 🟢 **구현 완료 · 가상 집행 변경 — 신동 선택 시 실주문(R3 손절 갱신)**
## 2026-10-21 (MW0601 700차 — 신동 섀도 SHADOW_ATRS: R3 손절 0.25×ATR14) — 🟢 **구현 완료 · 섀도(기록만, 주문 없음)**
## 2026-10-21 (MW0601 — 장전 점검)
## 2026-10-21 (MW0601 — 장중 점검)
## 2026-10-21 (MW0601 — 장후 점검, 종합 완성본)
## 2026-10-21 (MW0601 701차 후속 — 장후 자동조치: F-701-B 조사로 1-6 전제 반박 · 코드 무변경) — 🟡 **조사 완료 · 구현 0건**
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
live_legs.py:poll()`과 `strategy/position/position_tracker.py:613`의 상대거리 조사, 표본 10거래일 이상 섀도 후 재판정). 1-3(ProfitGuard-신동) Fix(F-701-A, `main.py:5977`에 `self.profit_guard.is_entry_allowed()` 호출 추가)는 여전히 사용자 결정 전까지 보류. 1-7은 코드변경 대상 아님 — NEXT_TODO O-t1을 ✅해소로 전환.
- **Why**: 1-6은 `dev_memory` 전체를 "TRAIL_AFTER_TP1"+"신동" 키워드로 검색해 기존 미등록 확인(함정① 통과, P5-06은 엔진 전용이라 별개). 1-7은 2거래일 연속 동일 메시지·동일 패턴(entry_executed − virtual 체결 = 정확히 쿨다운 로그 건수)으로 원인 확정.
- **How to apply**: F-701-A는 사용자 결정 수신 후 다음 장후 세션에서 `main.py:5977` 수정 + 재기동. F-701-B는 조사용 계측(TP1 트레일 전환 시점 가격 틱 로그) 신설이 선행조건 — 사용자 승인 필요(신동 거래규격 변경 소지, C등급).
- **검증**: `docs/정기점검/매일점검/evidence_MW0601-20261021_post.md` · `docs/정기점검/매일점검/MW0601-20261021-점검리포트.md` 제4·5부 참조. `data/db/trades.db`(`entry_source='SHINDONG'`, `exit_stage` 컬럼) 직접 조회(읽기 전용) · `fetch_daily_net_for_verdict()` 브로커 실측 net 확인 · `strategy/shindong/live_legs.py`·`strategy/position/position_tracker.py:613` 코드 Read로 확인. DB는 읽기전용으로만 접근, 쓰기 없음.



## 2026-10-21 (MW0601 701차 후속 — 장후 자동조치: F-701-B 조사로 1-6 전제 반박 · 코드 무변경) — 🟡 **조사 완료 · 구현 0건**

- **증상**: 장후 점검 1-6이 신동 `exit_stage=TRAIL_AFTER_TP1` 7레그(4패)를 "엔진 TP1
  보호전환(`position_tracker.py:613` `tp1_armed`)이 신동 `t1`보다 먼저 발동하는 설계 간극"으로
  해석하고 F-701-B(거리 조사)·R-1(분할청산 공백 개선)을 냈다.
- **원인(실측)**: 7레그 중 **6레그가 F-10(2026-08-31 1-19) 재현** — 2계약 하드스톱(틱)이
  거래소에서 1+1로 분할 체결 → 첫 체결이 `apply_exit_fill()` 비최종 분기(`:1019`)에서
  `_sync_partial_progress()`(`:1745`, closed_qty 1 ≥ target_1 1)로 `partial_1_done=True` →
  최종 레그가 `classify_exit_stage()`(`:613`)에서 `TRAIL_AFTER_TP1`. 손실 4건(11:30·11:37·12:25·
  13:28)의 청산가는 전부 `[ShindongExec]` 진입 시 손절선(899.86·896.08·891.50·882.50)과 일치 →
  **최초 손절**. 대조군 11:44는 2계약 단일 체결이라 `INITIAL_STOP`. 10:48만 진짜(신동1차 후).
  - 전제 자체도 성립하지 않는다: 외부 손절 포지션은 엔진 TP1~3을 `entry±10000`으로 무력화
    (`:1723-1724`, 진입 로그 `1차=-9102.00`). `:613`은 발동기가 아니라 사후 라벨러다.
- **결정**: 코드 변경 없음. F-10 수정은 기존대로 C등급(사용자 결정 대기) — 자동조치 범위 밖이며
  exit 경로(`position_tracker.py`) 수정이다. F-701-B는 조사 완료(전제 반박), R-1은 근거 소멸로
  진행 안 함. F-701-A(신동 ProfitGuard)는 C — 변동 없음.
- **Why**: 라벨 오염 위에 개선안을 쌓으면 신동 규격(spec.LEGS) 변경 같은 매매 정책 안건이
  틀린 근거로 상정된다. 08-31 이후 `[ExitStageRecon]` "미대응"이 같은 오분류를 매일 잡고 있었다.
- **How to apply**: 신동 채널 `TRAIL_AFTER_TP1`을 집계할 때는 **같은 `entry_ts`의 하드스톱
  분할 체결 여부**(`[Position] 체결부분청산 … 하드스톱(틱)`)를 먼저 걸러라. O-t1(10-22–)은 이
  필터 없이 재면 F-10 오분류를 센다. F-10 표본 갱신: 신동 채널 6레그/1거래일 추가.
- **검증**: 로그 `20261021_TRADE.log` `[ShindongExec] 진입`·`체결부분청산` 대조, `trades.db`
  읽기전용 조회(12레그). 테스트 실행 없음(코드 무변경). 커밋 안 함 — 장후 점검 미커밋분과 섞여
  사용자 커밋 대기 목록에 합류.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2026-10-20 (MW0601 — 장중 점검)
### 2026-10-20 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-20 (MW0601 698차 후속 — 단독 수집 첫날 판독, 16:40)
### 2026-10-20 (MW0601 698차 후속 — 장후 자동조치)
### 2026-10-21 (MW0601 — 장전 점검)
### 2026-10-21 (MW0601 — 장중 점검)
### 2026-10-21 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-22 (MW0601 703차 — F-701-A ProfitGuard 계좌 축)
```

미완료 체크박스 **3295건** (끝에서 30건)
```
- [ ] **(참고)** 698-1/698-2(피터2 단독수집 전환, 698차) 오늘 아침 1차 관측: 15분 창 2개 중 외부소진 1회·0회(10-19 중앙값 27회 대비 큰 개선) — 최종 판정은 5거래일 후(10-26 장후 예정)까지 유지, 이 점검은 재해석하지 않음.
- [ ] (참고) **1-3 / F-5 재확인** `[PositionFallback]` 10건(전부 '신동' 채널) — 기존 F-5 대상, 신규 Fix 없음. 메인 엔진('미륵') 채널은 horizon 정상 전달로 미발생(구조적 원인 재확인).
- [ ] **698-1 장중 중간 관측(보강)** 08:30~12:45 15분 창 17개 중 16개 외부소진 0회(1개 창만 1회) — 전일 중앙값 27회 대비 뚜렷한 개선 지속. 최종 판정은 10-26 장후까지 유지.
- [ ] **F-2 (신규, P2, 조사 전용·코드변경 없음)** `[RegimeFingerprint] 백필 0행 제외` 경보 — 최소 09-16부터 10-20까지 24거래일 연속 매일 발생, 어떤 리포트도 원인 확인한 적 없음. `scripts/backfill_features.py` 실행 이력 또는 `raw_features` 생성일 분포 vs 오늘 기…
- [ ] **O-t1 (신규)** `[진입체크]` 통과 9건 중 3건(13:05·13:11·13:53)이 실제 포지션 진입으로 이어지지 않음 — `main.py`의 진입체크→포지션등록 경로를 코드로 추적해 차단 사유 확인 필요. 표본 1거래일(3건)이라 313차 원칙상 확정 결론 금지.
- [ ] **O-t2 (계승)** 698-1/2(피터2 X 단독수집 전환) 1일차 종합 — 사전등록 기준 2개 전부 PASS(외부소진 중앙값 0.0 vs 27.0, p90 76.5초 vs 237.2초, PAGE_ERROR 0 vs 248). 최종 판정은 5거래일째(빠르면 10-26 장후).
- [ ] **(참고, 등록 보류)** 미륵 엔진 가상 6포지션(2승4패, -438,211원 가상) 중 2분 이내 손절 3건 — B(타이밍)/E(짧은호라이즌노이즈) 가설, 표본 n=6·1거래일이라 누적대장(수익률향상_누적대장.md) 등록 보류(6칸 중 기대효과·검증 미달). 미륵이 실주문 채널로 복귀하거나 가상채널도 집계 대상으로 삼기로 결정되면 재검토.
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 — 계좌 축(주체 3종 합) · 신동·피터2 관문 · L4 축 통일 · L3 카운터 부활 · 임계 재설정. DECISION_LOG 703차.
      ~~원문:~~ **F-701-A (P0, 사용자 결정 필요)** 신동 실거래 경로(`main.py:5977 _shindong_entry_block_reason()`)에 ProfitGuard(`self.profit_guard.is_entry_allowed()`) 체크를 추가할지 결정. 오늘(10-21) 11:38:57 ProfitGuard-L4 래치(엔진기준) 이후에도 신동이 4건 추가 거래(2승2패, +615,480원) — 결과는 양호했으나 노출 구조는 그대로. 결정 전까지 코드 변경 없음.
- [x] **F-701-B (P2, 조사전용·코드변경 없음)** 신동 1차 분할청산(`strategy/shindong/live_legs.py:poll()`의 `t1`)과 외부 TP1 트레일 전환(`strategy/position/position_tracker.py:613` `tp1_armed`)의 상대 거리 조사 — 오늘 TRAIL_AFTER_TP1 7레그 전부(7/7) 외부 트레일이 먼저 발동, 그중 4건이 전량손실로 마감(1-6). 조사용 가격틱 계측 신설이 선행조건(사용자 승인 필요, C등급).
      → **[2026-10-21 17:40 장후 자동조치] 조사 완료 — 전제 반박.** 7레그 중 6레그는 F-10(하드스톱 1+1 분할 체결 → `_sync_partial_progress()` 오판) 재현이고 손실 4건은 전부 최초 손절. 외부 포지션은 엔진 TP1~3이 무력화돼 있어(`position_tracker.py:1723-1724`) "어느 쪽이 먼저"라는 질문이 성립 안 함. R-1 근거 소멸. 상세: `MW0601-20261021-점검리포트.md` 제10부 · DECISION_LOG 701차 후속.
- [ ] 🔴 **F-10 (C, 사용자 결정 대기 — 2026-08-31 등록분 재상정)** 하드스톱 분할 체결 시 `exit_stage` 오분류 수정 승인 여부. 10-21 신동 채널 6레그 추가 재현(이번 건은 장후 점검이 이 오분류 위에 R-1 개선안까지 세움). 08-31 계획서가 이름 붙인 회귀 테스트 `tests/test_507_exit_stage_multifill.py`는 **아직 없다**(2026-10-21 확인 — 있는 것은 섀도 `test_507_exit_stage_recon_shadow.py`뿐).
- [ ] **O-t1 (10-22부터 신규 관측)** 신동 `TRAIL_AFTER_TP1` 레그의 전량손실 비율 — `[ExitStageRecon]` 일일 자기대사 로그로 5거래일 누적 후 1-6 재판정.
      ⚠ **[2026-10-21 자동조치] 이 라벨 그대로 세면 F-10 오분류를 센다** — 같은 `entry_ts`의 `[Position] 체결부분청산 … 하드스톱(틱)` 존재 레그는 제외하고 집계할 것.
- [ ] **O-t2 (상시 관측)** 1-3 미해결 상태에서 신동의 연속손실(CB② 임계 3 근접 여부) — 사용자 결정 전까지 매 장후 점검.
- [ ] **O-t3** `trade_principal.json`의 `principal`이 `MIREUK`로 복귀하는 날 — 복귀 시 `docs/정기점검/수익률향상_누적대장.md` P5-01~18 재가동.
- [x] **O-t1 (2026-10-20 등록분) 해소** — 엔진 모의결정(entry_executed=1) 9건 중 가상장부 미체결 3건의 원인을 `virtual_cooldown` 설계로 확인(로그: `[Virtual] 미륵 가상진입 생략 — virtual_cooldown(until HH:MM)`). 10-20·10-21 2거래일 연속 동일 패턴 재현, 버그 아님 — 추가 코드 추적 불필요.

### 2026-10-22 (MW0601 703차 — F-701-A ProfitGuard 계좌 축)
- [ ] **703-0 (장후)** 재기동 후 라이브 첫날 확인 — `[ProfitGuard] 포지션 청산 반영 …` 매 청산 1줄 · 신동/피터 기각 사유 `ProfitGuard [L…]` · 13시 이후 L3 카운트 증가 · 미륵 가상 시 `[ProfitGuard][Virtual]`. 커밋은 사용자 지시 후.
- [ ] **703-1 (10거래일 뒤, 2026-11-05경)** 임계 재판정 — 래치 날별 「래치 후 놓친 손익 vs 피한 손실」(신동 재생 기록 대비). L1 150만/35% · L2 400만 · L3 200만/2회 · L4 100만/3연패는 19일 표본 출발값이다.
- [ ] **703-2** 실행 중 프로세스에서 ProfitGuard 패널 [적용] 금지(옛 값 재저장) — 재기동으로 prefs 703 값이 로드된 것을 배지 툴팁으로 확인.
- [ ] **703-3 (참고)** 신동 실거래 기각(ProfitGuard)이 재생 채점과 실거래를 가른다 — 신동 일일 리포트 대사에 `REJECT why=ProfitGuard` 사유 표기 여부 확인.

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

### `data/heartbeat_MW0601_20261022.json` — 244B · 10-22 08:59:06
```json
{
 "pid": 19924,
 "written_at": "2026-10-22T08:59:06",
 "beat_epoch": 1792627145.861345,
 "beat_age_sec": 0.2,
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

### `data/peter_feed/_raw/2026-10-22.jsonl` — 819B · 10-22 08:47:02
```json
JSONL 2행 ⏎ 첫: {"id": "2113052640632582604", "dt": "2026-10-21T23:39:42.000Z", "text": "오늘 코스피는 외인들의 수급이 중요.\n\n매수를 해 주면 좋고\n매수를 안 하더라도 매도량이 적어야 함.\n\n오늘 만약 매도량이 많으면 조심해야 함.\n\n어제 일부 매수 들어간 분은 오늘 추가매수하지 말고 관망하고(더 떨어지거나 갭 메우러 올라갈 때 추가매수 전략)\n\n신규 매수 준비중인 분은 외인", "seen_at": "2026-10-22T08:44:31+09:00", "src": "live"} | {"id": "2113054283587575961", "dt": "2026-10-21T23:46:14.000Z", "text": "제가 말씀 드리는건 코스피 지수 기준입니다.\n\n반도체를 제외한 종목들은 좋은가격 오면 사도 되는 장이라 판단됩니다.", "seen_at": "2026-10-22T08:47:02+09:00", "src": "live"} ⏎ 끝:
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-22 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-22)과 일치 |
|---|---|---|
| `date` | 2026-10-22 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-22 08:55:05 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-21) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-22 08:55:05 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-21) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

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
| 19924 | 08:40:45 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 240개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261021-점검리포트.md` | 70.3KB | 10-21 17:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_post.md` | 103.3KB | 10-21 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_intra.md` | 85.3KB | 10-21 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261021_pre.md` | 63.6KB | 10-21 08:59 |
| `docs/정기점검/매일점검/MW0601-20261020-점검리포트.md` | 70.2KB | 10-20 17:57 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_post.md` | 90.1KB | 10-20 16:20 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_intra.md` | 75.7KB | 10-20 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261020_pre.md` | 61.7KB | 10-20 08:59 |

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
2. `logs/20261022_LEARNING.log`: **축퇴** 8건(표본)
3. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
4. 미커밋 변경 38건 (실질 6건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261022*.log` (Windows) / `grep 강제청산 logs/*20261022*.log`*