# 미륵이 증거 다이제스트 — 2026-10-20 / PRE

- 생성 2026-10-20 08:59:26 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01x9t9snachqmqrjjyyhzisf/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261020` · `2026-10-20` · `261020` · `1020`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **25개** 파일 · 25개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `MW0601-{DATE}-pre-cowork-0858.json` | 1 | `data/dailycheck_markers/MW0601-20261020-pre-cowork-0858.json` | 162B | 10-20 08:59 |
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261020.log` | 136B | 10-20 06:33 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261020.log` | 125B | 10-20 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261020.log` | 198B | 10-20 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261020.json` | 243B | 10-20 08:59 |
| `launcher_{DATE}_084001_17359.log` | 1 | `logs/Mireuk_batch/launcher_20261020_084001_17359.log` | 62.2KB | 10-20 08:58 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261020.log` | 108B | 10-20 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261020.log` | 2.7KB | 10-20 08:58 |
| `retrain_intraday_20260708_{DATE}56.log` | 1 | `logs/retrain_intraday_20260708_102056.log` | 4.6KB | 07-08 10:21 |
| `retrain_intraday_20260807_{DATE}59.log` | 1 | `logs/retrain_intraday_20260807_102059.log` | 4.5KB | 08-07 10:21 |
| `retrain_intraday_20260820_1{DATE}0.log` | 1 | `logs/retrain_intraday_20260820_110200.log` | 2.4KB | 08-20 11:02 |
| `retrain_intraday_20260901_{DATE}00.log` | 1 | `logs/retrain_intraday_20260901_102000.log` | 2.7KB | 09-01 10:20 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261020.log` | 2.5KB | 10-20 08:58 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-20.jsonl` | 1.2KB | 10-20 08:58 |
| `{DATE}_DATA.log` | 1 | `logs/20261020_DATA.log` | 896B | 10-20 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261020_DEBUG.log` | 0B | 10-20 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261020_HEALTH.log` | 0B | 10-20 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261020_HOGA.log` | 1.4MB | 10-20 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261020_LEARNING.log` | 46.5KB | 10-20 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20261020_MICRO.log` | 34.1KB | 10-20 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20261020_PROBE.log` | 12.1KB | 10-20 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261020_SIGNAL.log` | 10.7KB | 10-20 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261020_SYSTEM.log` | 29.2KB | 10-20 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261020_TRADE.log` | 167B | 10-20 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261020_WARN.log` | 4.4KB | 10-20 08:58 |

## 2. 코드·커밋 상태

- HEAD `87864966` · 브랜치 `v9-dev` · 미커밋 15건 · 실질 변경 4건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 4 · 미추적 11 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md`, `docs/미륵이고도화3/신동2/학습/lessons.json`, `docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md`, `docs/미륵이고도화3/신동2/학습/추이_MW0601.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.7초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md
 M docs/미륵이고도화3/신동2/학습/lessons.json
 M docs/미륵이고도화3/신동2/학습/레슨런_레지스트리.md
 M docs/미륵이고도화3/신동2/학습/추이_MW0601.md
?? docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261020.md
?? docs/미륵이고도화3/신동2/학습/피드백_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_MW0601_20261019.md
?? docs/미륵이고도화3/피터2/일일/피터2_일일_claude_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.md
?? docs/신동거래/일일/신동_일일_MW0601_20261019.svg
?? docs/정기점검/매일점검/MW0601-20261019-점검리포트.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_post.md
?? docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md
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

_본문 미열람(설정): `20261020_HOGA.log` 1.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20260820_110200.log`, `20261020_MICRO.log`, `20261020_DATA.log`, `20261020_PROBE.log`, `launcher_20261020_084001_17359.log`, `peter2_receiver_20261020.log`, `shindong2_20261020.log`, `freeze_sentinel_20261020.log`_

### `logs/20261020_TRADE.log` — 167B · 2행 · 최종 08:41:04

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-20 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-20 08:40:58 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-20 08:41:04 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261020_WARN.log` — 4.4KB · 24행 · 최종 08:58:11

- 형식 평문 · 시각 인식 24행 · WARNING=24

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-20 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 15ms
2026-10-20 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-20 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-20 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 109ms account=783343908
  …
2026-10-20 08:55:09 [WARNING] SYSTEM: [Canary] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증
2026-10-20 08:55:09 [WARNING] SYSTEM: [Canary] z경고 폭증(12개 ≥ 12개) → 장전 scaler 재적합 시도 (08:58 전)
2026-10-20 08:57:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 48.3ms | size=1994x950 candles=13 grid=26.6 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.0 cross=0.0 | slow_cnt=1 total_cnt=82 overlay_cnt=555
2026-10-20 08:58:11 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 30.6ms | size=1994x950 candles=14 grid=10.4 spans=0.0 candles=1.3 dir=0.0 regime=0.0 markers=0.0 axes=17.7 cross=0.0 | slow_cnt=2 total_cnt=86 overlay_cnt=613
2026-10-20 08:59:32 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 33.8ms | size=1994x950 candles=15 grid=5.9 spans=0.0 candles=0.6 dir=0.0 regime=0.0 markers=0.0 axes=26.0 cross=0.0 | slow_cnt=3 total_cnt=95 overlay_cnt=674
```

</details>

**WARNING — 태그 9종 (상위 9)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 9 | 08:41:08 | 08:41:13 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChartDBG` | 3 | 08:57:32 | 08:59:32 | paintEvent slow 48.3ms | size=1994x950 candles=13 grid=26.6 spans=0.0 candles=0.5 dir=0.0 regime=0.0 markers=0.0 axes=20.0 cross=0.0 | slow_cnt=1 total_cnt=82 overlay_cnt=555 |
| `CybosDailyPnl` | 2 | 08:41:08 | 08:41:08 | 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr65)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용 |
| `출처축` | 2 | 08:41:08 | 08:41:08 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `SessionStateDrop` | 2 | 08:41:09 | 08:41:09 | 완료 마커 소실 ['p8_last_success_date', 'eod_retrain_ok_date'] — 날짜 전환(2026-10-19 → 2026-10-20)이 새 딕셔너리를 만들면서 이어받지 않았다 (호출부=session_recovery_service.py:increment_session). F-1 미적용 상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 이상점 1-4(판정 근거 정합성)의 확인 수단… |
| `Peter2Offset` | 2 | 08:47:08 | 08:52:38 | A056B 실측=-1.52 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-1.52 | 직전일=-1.82(prev_day:2026-10-19, safe=True) 차=0.3 | 48ms |
| `Canary` | 2 | 08:55:09 | 08:55:09 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `OptionFlowChart` | 1 | 08:41:18 | 08:41:18 | 그리기 75.8ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 774x1001 |
| `SessionBackfill` | 1 | 08:41:38 | 08:41:38 | 2026-10-19 차트 보충 — chart=411 existing=411 inserted=0 mismatch=2 |

**채널** — `SYSTEM`×24

**컴포넌트 상위 15** — `LiveDBG`×9, `ChartDBG`×3, `CybosDailyPnl`×2, `출처축`×2, `SessionStateDrop`×2, `Peter2Offset`×2, `Canary`×2, `OptionFlowChart`×1, `SessionBackfill`×1

### `logs/20261020_SYSTEM.log` — 29.2KB · 222행 · 최종 08:59:21

- 형식 평문 · 시각 인식 216행 · INFO=216, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:44 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=2344 | 행감지=30s all_threads=True
2026-10-20 08:40:45 [INFO] SYSTEM: [DBInit] 합계 0.47s | predictions=0.05s trades=0.23s daily_stats=0.01s shap=0.02s raw_data=0.11s broker_pnl=0.01s broker_recon=0.01s premarket_levels=0.03s
2026-10-20 08:40:45 [INFO] SYSTEM: [System] DB 초기화 완료 (0.5s)
2026-10-20 08:40:45 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-20 08:40:45 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-20 08:59:00 [INFO] SYSTEM: [PreMarket] Phase4 refit 기동 (14봉 z경고=4개)
2026-10-20 08:59:00 [INFO] SYSTEM: [PreMarket] Phase4 refit 완료 n=30봉 z경고 4→5개 | 잔존=atr,avg_volume,toxicity_score_ma
2026-10-20 08:59:09 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=12개 (08:55 최종 5개 대비 +7) — 재측정만, 재적합 없음
2026-10-20 08:59:14 [INFO] SYSTEM: [CybosRT-TICK] #2600 code=A056B raw_time=85914 parsed=08:59:14 price=884.18 vol=1 bid1=884.18 ask1=884.30 flag=50 side=SELL anchor=0/1
2026-10-20 08:59:21 [INFO] SYSTEM: [TickUI] alive ticks=2616 code=A056B close=884.32
```

</details>

**채널** — `SYSTEM`×216

**컴포넌트 상위 15** — `CybosRT-TICK`×31, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `Capital`×4, `LEVELS 08:50`×4

### `logs/20261020_SIGNAL.log` — 10.7KB · 85행 · 최종 08:59:00

- 형식 평문 · 시각 인식 85행 · WARNING=18, INFO=67

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.415
  …
2026-10-20 08:55:09 [INFO] SIGNAL: [ScalerFloor] 30m 'macro_us10y_chg' scale=0.0308 → floor=0.25 적용 (z-score 폭발 방지)
2026-10-20 08:55:09 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0821 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-20 08:55:09 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0175 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-20 08:55:09 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP  n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-10-20 08:59:00 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.08s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 18 | 08:45:08 | 08:45:08 | 1m CORE 'cvd_divergence' raw_std≈0(0.0223) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×85

**컴포넌트 상위 15** — `ScalerFloor`×42, `ScalerRefresh`×24, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1

### `logs/20261020_LEARNING.log` — 46.5KB · 259행 · 최종 08:59:00

- 형식 평문 · 시각 인식 259행 · WARNING=124, INFO=135

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-20 08:40:46 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-20 08:40:49 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00074 auc=0.407 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과
2026-10-20 08:40:49 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00117 auc=0.397 out_max=0.2005 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과
2026-10-20 08:40:50 [WARNING] LEARNING: [Calibration:5m] 축퇴 감지 — span=0.00014 auc=0.500 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과
2026-10-20 08:40:50 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00029 auc=0.518 out_max=0.3706 (기준 auc<0.53 and span<0.020, 기저율=0.3704 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제]
  …
2026-10-20 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-20 08:55:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-20 08:55:08 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=2594, ver=5)
2026-10-20 08:55:09 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-20 08:59:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 41 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00117 auc=0.397 out_max=0.2005 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 34 | 08:40:49 | 08:40:58 | 축퇴 감지 — span=0.00074 auc=0.407 out_max=0.3878 (기준 auc<0.53 and span<0.020, 기저율=0.3875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 21 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00029 auc=0.518 out_max=0.3706 (기준 auc<0.53 and span<0.020, 기저율=0.3704 n=135) → 보정 미적용, raw 통과 [기존 fitted 해제] |
| `Calibration:5m` | 15 | 08:40:50 | 08:40:58 | 축퇴 감지 — span=0.00014 auc=0.500 out_max=0.3126 (기준 auc<0.53 and span<0.020, 기저율=0.3125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 9 | 08:40:50 | 08:40:58 | 하한 도달불가 — out_max=0.3254 < conf_floor=0.3300 (span=0.00069 auc=0.635 out_max=0.3254, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 3 | 08:40:50 | 08:40:55 | 축퇴 감지 — span=0.00158 auc=0.426 out_max=0.3632 (기준 auc<0.53 and span<0.020, 기저율=0.3625 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:58 | 08:40:58 | 복원한 보정기가 하한 도달불가 — out_max=0.3284 < conf_floor=0.3300 (span=0.00736 auc=0.570 out_max=0.3284, n=4224) → 보정 미적용으로 시작, raw 통과. 축퇴(auc/span)와 별개 사유이며, 표본이 쌓여 출력상한이 하한 위로 올라오면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×259

**컴포넌트 상위 15** — `Calibration:30m`×81, `Calibration:1m`×67, `Calibration:3m`×41, `Calibration:5m`×30, `Calibration:10m`×18, `Calibration:15m`×6, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `Consolidator`×2, `RF`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

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

### `logs/retrain_intraday_20260807_102059.log` — 4.5KB · 39행 · 최종 10:21:31

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-07 10:20:59,329 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-07 10:20:59,329 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-07 10:20:59,329 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-07 10:20:59,329 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ca552d64.json
2026-08-07 10:21:00,860 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-07 10:21:31,327 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=0.95s | old_acc=0.4289)
2026-08-07 10:21:31,366 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-07 10:21:31,366 [INFO] LEARNING: [Retrain] 완료 | 30.5초 | 성공=6/6 호라이즌
2026-08-07 10:21:31,367 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 32.0s 데이터=4800행
2026-08-07 10:21:31,368 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ca552d64.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260901_102000.log` — 2.7KB · 21행 · 최종 10:20:14

- 형식 평문 · 시각 인식 21행 · INFO=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-09-01 10:20:00,494 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-01 10:20:00,494 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-09-01 10:20:00,494 [INFO] RETRAIN_INTRADAY: ==================================================
2026-09-01 10:20:00,494 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['5m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_c430dda1.json
2026-09-01 10:20:02,330 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-09-01 10:20:14,146 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-09-01 10:20:14,146 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-09-01 10:20:14,146 [INFO] LEARNING: [Retrain] 완료 | 11.8초 | 성공=1/1 호라이즌
2026-09-01 10:20:14,147 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 13.7s 데이터=4800행
2026-09-01 10:20:14,148 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_c430dda1.json
```

</details>

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

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

### 메인 스레드 블로킹 1건 · 최대 4313ms · 5초 초과 0건

상위 — 4313ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261020_WARN.log`
```
--- 메인 스레드 블로킹 ×1(표본)
08:41:12 2026-10-20 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4313ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4313 band=INFO since_pipe_s=NA
```

### `logs/20261020_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.432
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.420
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.411
08:40:42 2026-10-20 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.407
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

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261020_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 17 | 08:41:08 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 6 | 08:52:38 [WARNING] A056B 실측=-1.67 n=7 spread=0.05 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.67 | 직전일=-1.82(prev_day:2026-10-1… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 5 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261020_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 102 | 08:40:44 [INFO] 활성화 | file=logs\crash_fault.log PID=2344 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 99 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 65 | 08:54:01 [INFO] code=A056B from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261020_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 56 | 08:45:08 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0223) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 28 | 08:50:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 27 | 08:55:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] ela… |

- 이 로그 생존구간: 08:40 ~ 08:59

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
| **오늘 20261020** | **08:59** | 로그 본문 |

- 델타 **-408분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 이월(변경 없음) — 1-1(CREON)·1-2(F-1 SessionStateDrop)·1-3(머지커밋 PC태그 확인필요)·1-4(피터2 수신오류, 697차 수정 배포·라이브 검증 대기)
## 2026-10-16 (MW0601 697차 후속 — 장후 자동조치: F-26)
## 2026-10-19 (MW0601 — 장전 점검)
## 2026-10-19 (MW0601 — 장중 점검)
## 2026-10-19 (MW0601 697차 후속2 — 장후 자동조치: G-1) — 🟢 **구현 · 문서/테스트 한정 · 매매 경로 무변경**
## 2026-10-19 (MW0601 — 장후 점검, 종합 완성본)
## 2026-10-19 (MW0601 — 장후 점검 세션, 교차확인 메모)
## 2026-10-20 (MW0601 698차 — 피터2 X 수집 공유 해소: MW0602 수집기 중지 · 단독 수집 추적기) — 🟡 **결정 · 추적 도구 구현 · 라이브 미검증**
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
추적.

⚠ 코드 변경 없음(장후 점검 세션 — 관측·DB 읽기 전용 조회만). git add/commit/push 전혀 하지 않음(장후 세션 규칙).

## 2026-10-19 (MW0601 — 장후 점검 세션, 교차확인 메모)

**증상/확인 대상**: 위 「장후 점검, 종합 완성본」 작성 중 발견한 G-1(거래주체분리가 3원 대사에 미치는 영향 문서화)·F-1(피터2 계정분리)·R-1(신호지연 관찰채널)을 `dev_memory/DECISION_LOG.md`·`dev_memory/NEXT_TODO.md`에 등록하려는 시점에, 같은 날 이미 별도의 "697차 후속2: 장후 자동조치" 세션(Claude Opus 5.5)이 동일한 세 항목을 독립적으로 발견해 다음과 같이 선행 처리했음을 git log·NEXT_TODO.md grep으로 확인했다: (1) G-1은 `postmortem.md`§2-1·`evidence_map.md`§8-5에 실제 문서화되고 회귀테스트(`tests/test_697b_skill_principal_reconcile_doc.py`)까지 추가돼 커밋 `49083264`·`97c7317e`로 완료, (2) `NEXT_TODO.md` "2026-10-19 (MW0601 697차 후속2 — 장후 자동조치)" 절에 F-1·R-1·G-2(10-16 보류 유지)·1-3(C) 체크박스가 이미 등록되어 있음, (3) 리포트 파일 자체에도 해당 세션이 「제10부. 장후 자동조치 구현 결과」를 이미 append해 동일 내용을 기록함.

**결정**: 함정①(판정≠결정) 재확인 차원에서 NEXT_TODO.md에 F-1·R-1을 중복 등록하지 않는다. 위 「장후 점검, 종합 완성본」 항목의 결정 5(G-1 제안)·6(R-1 제안)은 작성 시점 기준 독자적 발견이었음을 남기되, 실제 반영은 이미 완료된 것으로 간주한다(중복 작업 금지).

**Why**: 하루 안에 "장후 점검"과 "장후 자동조치" 두 세션이 겹쳐 돌 수 있다는 것을 이번에 실측으로 확인했다 — 향후 세션은 DECISION_LOG·NEXT_TODO를 쓰기 직전에 한 번 더 `git log --since="오늘 00:00 KST"`로 재확인할 것(단순 세션 시작 시점 체크만으로는 부족).

**How to apply**: 해당 없음(기록·교차확인만, 코드·문서 변경 없음).

**검증**: 다음 세션이 이 메모를 참고해 같은 사안을 세 번째로 "신규 발견"하지 않도록 한다.

⚠ 코드 변경 없음. git add/commit/push 없음(장후 세션 규칙).


## 2026-10-20 (MW0601 698차 — 피터2 X 수집 공유 해소: MW0602 수집기 중지 · 단독 수집 추적기) — 🟡 **결정 · 추적 도구 구현 · 라이브 미검증**

- **증상**: 10-19 장후 697-2 FAIL — 트윗 지연 p90 237.2초(>90), 정규장 429 23건, PAGE_ERROR 248.
- **원인**: 같은 X 로그인을 MW0602 수집기가 함께 써 15분 한도(50회)를 나눠 소진. 실측: 우리 요청은 80초마다 2회(RATE `n=1`·`n=2`)인데 그 사이 rem이 5–6 감소 → 창당 외부 소진 중앙 **27회**(24창, 최대 35). 우리 몫(창당 약 22회)만으로는 한도 미도달.
- **결정(사용자 2026-10-20)**: 새 계정 없이 **MW0602 피터2 수집기를 10-20부터 중지**(03 §4 ②안). MW0601 단독 수집.
  ⚠ 2026-08-23 멀티PC 상호조율 폐기와의 관계: 이것은 PC간 협상이 아니라 **사용자 자신의 운영 결정**이다(두 PC 모두 사용자 운영).
- **구현**: `tools/peter2_live/sole_collect_tracker.py`(읽기 전용, 로그만) — 기준선 10-19 대비 평가 창 5거래일 사전등록 판정
  ① 외부 소진 중앙 ≤ 3(일별) ② 정규장 429 ≤ 1(일별) ③ 통합 p90 ≤ 90초·n≥30 → IMPROVED / NOT_LIMIT / STILL_SHARED / INSUFFICIENT.
  장후 증거 수집기 `collect_evidence.py` §9-e 자동 요약. 문서 `docs/피터2수집/04_…`. 테스트 `tests/test_698_peter2_sole_collect_tracker.py`(9) + collect_evidence 계열 276 passed.
- **Why**: 판정 기준을 결과 보기 전에 고정해야 "좋아진 것 같다"류 사후 해석을 막는다(458차 D6). 외부 소진은 로그만으로 직접 재는 지표라 MW0602가 실제로 꺼졌는지 첫날 확인 가능.
- **How to apply**: 매 장후 §9-e 확인. STILL_SHARED면 MW0602 수집기 실제 중지 여부·같은 계정 수동 X 검색 여부를 사용자에게 확인. NOT_LIMIT면 03 §2 혼자 소진 가지.
- **검증 예정**: 10-20 장중 RATE에서 우리 요청 사이 rem 감소 1 → ① 즉시 판독. 최종 판정은 5거래일 후(빠르면 10-26 장후).

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 2026-10-16 (MW0601 — 장중 점검)
### 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도) — 장중 1-4 / G-2 후속
### 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-16 (MW0601 697차 후속 — 장후 자동조치)
### 2026-10-19 (MW0601 — 장전 점검)
## 2026-10-19 (MW0601 — 장중 점검)
### 2026-10-19 (MW0601 697차 후속2 — 장후 자동조치)
### 2026-10-20 (MW0601 698차 — 피터2 단독 수집 전환)
```

미완료 체크박스 **3244건** (끝에서 30건)
```
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
- [ ] **F-1 (C, 사용자 결정)** 피터2 X 전용 계정 분리(697-3 분기 충족 — 1-4 p90 237.2초 FAIL · 창별 rem 소진 > 우리 관측). 결정 후 별도 세션 구현.
- [ ] **R-1 (C, 승인 대기)** `latency_report.py` 일별 p90·429·PAGE_ERROR 를 누적하는 관찰 스크립트 — 10거래일 후 p90 vs 피터2 순손익 일자단위 상관(313차 5갈래). 표본 1일이라 자동 구현 제외, 도구 자체는 무위험.
- [ ] **G-2(10-16) 보류 유지** 재시도·캐시 보강은 공유 소비 판정 하에서 한도 소진을 키운다 — F-1 결정 이후 재평가.
- [ ] **1-3 (C)** `PETER2_OFFSET_TOL_PT`/`_peter2_measure_offset()` 창 재검토 — 복수 거래일 spread>0.30 지속 시 안건.
- [ ] **698-1 (10-20 장중·장후)** RATE 우리 요청 사이 rem 감소가 1로 떨어졌는가(① 외부 소진 중앙 ≤ 3). 아니면 MW0602 중지 미반영 → 사용자 확인.
- [ ] **698-2 (매 장후, 5거래일)** `collect_evidence --phase post` §9-e 확인 · 최종 판정은 평가 창 5거래일 도달 시(빠르면 10-26 장후). IMPROVED → F-4·G-2 종결 / NOT_LIMIT → 03 §2 혼자 소진 가지 / STILL_SHARED → 사용자 확인.
- [ ] **R-1 연계** 지연 누적은 698 추적기가 대신한다 — 5거래일 후 R-1(지연 vs 피터2 손익) 필요성 재평가.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
ard.py:7434 _build) 원인 조사 착수 여부 — 10-19로 관측일 추가, 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **CREON-M1 (P0)** 장후 API 세션 정리 적용 시간대 — 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **F-24** `MAX_CONTRACTS` 수집기 기대값(3) 정정 — 실제 운용값 1은 의도값, 수집기 쪽 기대값만 낡음.
- [ ] (이월, 변경 없음) **F-1** `session_state.json` 마커 유실(SessionStateDrop) — 10-19 재발, EOD 마커 파일 보완 경로로 실질 피해 없음 재확인.
- [x] **697-1 (유력 해소)** `logs/peter2_receiver_20261019.log`에 "RATE ... rem=48/50" 형태 한도 헤더 값이 정상 수신·기록됨을 확인 — 확장 v1.1.0 반영 정황. 다만 사용자가 `chrome://extensions`에서 버전 직접 확인하면 완전히 닫힘(사용자 조치 아님, 참고).
- [ ] **697-4 관련 메모** `python tools/peter2_live/receiver.py --check`는 코웍 리눅스 샌드박스에서 실행하면 Windows 본체가 아닌 다른 네트워크 네임스페이스로 접속을 시도해 항상 Connection refused가 난다 — 이 환경에서는 로그 파일 증거(START 시각·최근 RATE 줄)로 대체 판정할 것. 다음 세션을 위한 운영 메모(조치 항목 아님).
- [ ] (참고) 이 계정 앱 저장 스킬 사본(rev 2026-08-26e)이 저장소 정본(rev 2026-09-07, 538차)보다 낡음 — 사용자가 해당 PC에서 재저장하면 해소. 이 세션은 스킬 저장 도구에 접근 불가.

## 2026-10-19 (MW0601 — 장중 점검)
- [ ] **1-3 (P2, 장후 판정 대기)** 피터2 오프셋 보정값(`PETER2_OFFSET_TOL_PT`) spread가 08:58~11:23 구간 n=30까지 쌓여도 0.31~0.40 사이로 전혀 0.30 이하로 내려오지 않음 — 장후 점검이 하루 전체 추이로 "안정화됐는지/계속 불안정했는지" 최종 판정. 안정화 안 되면 `main.py:_peter2_measure_offset()` 또는 `PETER2_OFFSET_TOL_PT` 임계 재검토를 사용자 승인 대기 항목으로 등록할 것(장중에는 Fix 제안만, 적용 안 함).
- [ ] **O-p2 (판정보류 → 장후)** 캐너리 z경고 재상승 — 09:00~12:26 구간 재측정 로그 0건. 장후 점검이 `grep -c "Canary" logs/20261019_*.log`로 하루 전체 측정 횟수 재확인하고, 장중 미측정이 설계상 정상(1회성 장전 체크)인지 `main.py`에서 확인.


### 2026-10-19 (MW0601 697차 후속2 — 장후 자동조치)
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

### `data/heartbeat_MW0601_20261020.json` — 243B · 10-20 08:59:09
```json
{
 "pid": 2344,
 "written_at": "2026-10-20T08:59:39",
 "beat_epoch": 1792454378.7208924,
 "beat_age_sec": 1.2,
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

### `data/peter_feed/_raw/2026-10-20.jsonl` — 1.2KB · 10-20 08:58:11
```json
JSONL 3행 ⏎ 첫: {"id": "2112331823854571858", "dt": "2026-10-19T23:55:26.000Z", "text": "책 추천해 달라는 요청이 너무 많은데\n\n퀀트책 외에는 추천한 적이 없어.\n\n좋은 책은 많은데 뭔가 집대성한 느낌의 책이 없어서 딱 생각하는게 없었기 때문이야.\n\n그래서 내가 그동안 공부한것도 정리할겸해서 책을 썼거든.\n\n우선 '차트' 의 모든것을 집대성했어.( 보조지표등 각종 지표 심화편은", "seen_at": "2026-10-20T08:56:20+09:00", "src": "live"} | {"id": "2112332062451695986", "dt": "2026-10-19T23:56:23.000Z", "text": "책 추천해 달라는 요청이 너무 많은데\n\n퀀트책 외에는 추천한 적이 없어.\n\n좋은 책은 많은데 뭔가 집대성한 느낌의 책이 없어서 딱 생각나는게 없었기 때문이야.\n\n그래서 내가 그동안 공부한것도 정리할겸해서 책을 썼거든.\n\n우선 '차트' 의 모든것을 집대성했어.( 보조지표등 각종 지표 심화편은", "seen_at": "2026-10-20T08:57:39+09:00", "src": "live"} | {"id": "2112332393906606550", "dt": "2026-10-19T23:57:42.000Z", "text": "코스피는 오늘 상방 어려우니 매수하지는 말고.\n\n우선 지켜보자.", "seen_at": "2026-10-20T08:58:11+09:00", "src": "live"} ⏎ 끝:
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-20 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-20)과 일치 |
|---|---|---|
| `date` | 2026-10-20 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-20 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-10-19) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-20 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-19) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

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
| 2344 | 08:40:44 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 232개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261019-점검리포트.md` | 68.1KB | 10-19 17:29 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_post.md` | 94.7KB | 10-19 16:21 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_intra.md` | 81.1KB | 10-19 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md` | 59.6KB | 10-19 08:59 |
| `docs/정기점검/매일점검/MW0602-20261017-긴급알림메일-종합검토.md` | 14.1KB | 10-17 11:49 |
| `docs/정기점검/매일점검/MW0602-20261015-청산거부113분-딥다이브.md` | 21.3KB | 10-17 10:31 |
| `docs/정기점검/매일점검/MW0601-20261016-점검리포트.md` | 75.9KB | 10-16 17:28 |
| `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` | 8.9KB | 10-16 16:40 |

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
2. `logs/20261020_LEARNING.log`: **축퇴** 8건(표본)
3. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
4. 미커밋 변경 15건 (실질 4건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261020*.log` (Windows) / `grep 강제청산 logs/*20261020*.log`*