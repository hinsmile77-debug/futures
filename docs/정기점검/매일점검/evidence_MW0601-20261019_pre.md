# 미륵이 증거 다이제스트 — 2026-10-19 / PRE

- 생성 2026-10-19 08:59:34 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01fmpqk68jycwsacdjcv6vrd/mnt/futures`
- 점검 범위: pre (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261019` · `2026-10-19` · `261019` · `1019`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **19개** 파일 · 19개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261019.log` | 125B | 10-19 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261019.log` | 197B | 10-19 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261019.json` | 243B | 10-19 08:59 |
| `launcher_{DATE}_084001_30125.log` | 1 | `logs/Mireuk_batch/launcher_20261019_084001_30125.log` | 62.2KB | 10-19 08:59 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261019.log` | 109B | 10-19 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261019.log` | 1.1KB | 10-19 08:58 |
| `retrain_intraday_20260811_{DATE}59.log` | 1 | `logs/retrain_intraday_20260811_101959.log` | 4.5KB | 08-11 10:20 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261019.log` | 2.3KB | 10-19 08:57 |
| `{DATE}_DATA.log` | 1 | `logs/20261019_DATA.log` | 894B | 10-19 08:58 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261019_DEBUG.log` | 0B | 10-19 08:40 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261019_HEALTH.log` | 0B | 10-19 08:40 |
| `{DATE}_HOGA.log` | 1 | `logs/20261019_HOGA.log` | 1.4MB | 10-19 08:59 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261019_LEARNING.log` | 52.6KB | 10-19 08:59 |
| `{DATE}_MICRO.log` | 1 | `logs/20261019_MICRO.log` | 35.2KB | 10-19 08:59 |
| `{DATE}_PROBE.log` | 1 | `logs/20261019_PROBE.log` | 12.1KB | 10-19 08:58 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261019_SIGNAL.log` | 10.5KB | 10-19 08:59 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261019_SYSTEM.log` | 30.1KB | 10-19 08:59 |
| `{DATE}_TRADE.log` | 1 | `logs/20261019_TRADE.log` | 167B | 10-19 08:41 |
| `{DATE}_WARN.log` | 1 | `logs/20261019_WARN.log` | 3.6KB | 10-19 08:58 |

## 2. 코드·커밋 상태

- HEAD `5aaad2d` · 브랜치 `v9-dev` · 미커밋 1건 · 실질 변경 1건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 1 · 미추적 0 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.7초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md
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

_본문 미열람(설정): `20261019_HOGA.log` 1.4MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/15개 (중요도순). 제외: `20261019_PROBE.log`, `launcher_20261019_084001_30125.log`, `shindong2_20261019.log`, `peter2_receiver_20261019.log`, `freeze_sentinel_20261019.log`, `force_flat_guard_20261019.log`, `maekjeom_ladder_20261019.log`_

### `logs/20261019_TRADE.log` — 167B · 2행 · 최종 08:41:05

- 형식 평문 · 시각 인식 2행 · INFO=2

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-19 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
  …
2026-10-19 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-19 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
```

</details>

**채널** — `TRADE`×2

**컴포넌트 상위 15** — `Position`×1, `ProfitGuard`×1

### `logs/20261019_WARN.log` — 3.6KB · 21행 · 최종 08:58:09

- 형식 평문 · 시각 인식 21행 · WARNING=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 78ms
2026-10-19 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr11)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-19 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr11)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=783343908
  …
2026-10-19 08:47:09 [WARNING] SYSTEM: [Peter2Offset] A056B 실측=-1.48 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-1.48 | 직전일=-2.08(prev_day:2026-10-16, safe=True) 차=0.6 | 61ms
2026-10-19 08:52:39 [WARNING] SYSTEM: [Peter2Offset] A056B 실측=-1.54 n=7 spread=0.37 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.54 | 직전일=-2.08(prev_day:2026-10-16, safe=True) 차=0.54 | 32ms
2026-10-19 08:55:09 [WARNING] SYSTEM: [Canary] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증
2026-10-19 08:55:09 [WARNING] SYSTEM: [Canary] z경고 폭증(12개 ≥ 12개) → 장전 scaler 재적합 시도 (08:58 전)
2026-10-19 08:58:09 [WARNING] SYSTEM: [Peter2Offset] A056B 실측=-1.55 n=13 spread=0.31 safe=False(불안정 spread=0.31>0.30) 창=08:46~08:58 전일정=-1.55 | 직전일=-2.08(prev_day:2026-10-16, safe=True) 차=0.53 | 46ms
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 10 | 08:41:08 | 08:41:16 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `Peter2Offset` | 3 | 08:47:09 | 08:58:09 | A056B 실측=-1.48 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-1.48 | 직전일=-2.08(prev_day:2026-10-16, safe=True) 차=0.6 | 61ms |
| `CybosDailyPnl` | 2 | 08:41:08 | 08:41:08 | 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr11)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용 |
| `출처축` | 2 | 08:41:09 | 08:41:09 | 미분류 entry_source ['PHANTOM_STATE_ARTIFACT'] — 「자동」이 아니라 「미측정」으로 집계한다. 시스템 거래라면 PROFIT_GUARD_SYSTEM_SOURCES 에, 사람·외부라면 _MANUAL_SOURCES 에 등록할 것 |
| `Canary` | 2 | 08:55:09 | 08:55:09 | scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| `OptionFlowChart` | 1 | 08:41:18 | 08:41:18 | 그리기 69.0ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 785x1001 |
| `SessionBackfill` | 1 | 08:41:39 | 08:41:39 | 2026-10-16 차트 보충 — chart=411 existing=411 inserted=0 mismatch=1 |

**채널** — `SYSTEM`×21

**컴포넌트 상위 15** — `LiveDBG`×10, `Peter2Offset`×3, `CybosDailyPnl`×2, `출처축`×2, `Canary`×2, `OptionFlowChart`×1, `SessionBackfill`×1

### `logs/20261019_SYSTEM.log` — 30.1KB · 226행 · 최종 08:59:21

- 형식 평문 · 시각 인식 220행 · INFO=220, PLAIN=6

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=4572 | 행감지=30s all_threads=True
2026-10-19 08:40:46 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.22s daily_stats=0.01s shap=0.01s raw_data=0.10s broker_pnl=0.02s broker_recon=0.01s premarket_levels=0.02s
2026-10-19 08:40:46 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-19 08:40:46 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-19 08:40:46 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-19 08:59:00 [INFO] SYSTEM: [CVD-ANCHOR] ts=08:58 vol=188 | live_buy=161 shadow_buy=153 anchor_buy=153 | resid(anchor)=0 resid(shadow)=0 unknown_ticks=0 resets=0
2026-10-19 08:59:01 [INFO] SYSTEM: [PreMarket] Phase4 refit 기동 (14봉 z경고=8개)
2026-10-19 08:59:01 [INFO] SYSTEM: [PreMarket] Phase4 refit 완료 n=30봉 z경고 8→8개 | 잔존=atr,avg_volume,microprice_bias,microprice_depth_bias,ofi_reversal_speed,queue_depletion_speed,queue_refill_rate,toxicity_queue_stress
2026-10-19 08:59:09 [INFO] SYSTEM: [CanaryShadow] ts=08:59 z경고=10개 (08:55 최종 8개 대비 +2) — 재측정만, 재적합 없음
2026-10-19 08:59:21 [INFO] SYSTEM: [TickUI] alive ticks=3136 code=A056B close=851.58
```

</details>

**채널** — `SYSTEM`×220

**컴포넌트 상위 15** — `CybosRT-TICK`×36, `CybosSub`×21, `System`×17, `TickUI`×15, `CybosRT-ROLLOVER`×14, `BAR-CLOSE`×14, `CVD-ANCHOR`×14, `SYSTEM`×9, `PreMarket`×9, `CybosRT-START`×6, `BrokerSync`×4, `BalanceUI`×4, `Notify`×4, `Capital`×4, `LEVELS 08:50`×4

### `logs/20261019_SIGNAL.log` — 10.5KB · 85행 · 최종 08:59:01

- 형식 평문 · 시각 인식 85행 · WARNING=6, INFO=79

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.461
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.443
  …
2026-10-19 08:55:09 [INFO] SIGNAL: [ScalerFloor] 30m 'macro_risk_on' scale=0.4714 → floor=0.50 적용 (z-score 폭발 방지)
2026-10-19 08:55:09 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0388 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-19 08:55:09 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0470 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-19 08:55:09 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP  n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-10-19 08:59:01 [INFO] SIGNAL: [ScalerRefresh] ts=— trigger=A_WARMUP pre_market_phase4_14bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.02s
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerRefresh` | 6 | 08:45:09 | 08:45:09 | 1m CORE 'cvd_divergence' raw_std≈0(0.0239) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×85

**컴포넌트 상위 15** — `ScalerFloor`×54, `ScalerRefresh`×12, `DynMC`×7, `Model`×6, `TimeRouter`×2, `EnsembleGater`×1, `FeatureBuilder`×1, `GapOffset`×1, `MA-cont`×1

### `logs/20261019_LEARNING.log` — 52.6KB · 294행 · 최종 08:59:01

- 형식 평문 · 시각 인식 294행 · WARNING=142, INFO=152

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00158 auc=0.502 out_max=0.2959 (기준 auc<0.53 and span<0.020, 기저율=0.2952 n=105) → 보정 미적용, raw 통과
  …
2026-10-19 08:50:00 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-19 08:55:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-19 08:55:09 [INFO] LEARNING: [MetaConf] 상태 복원 완료: meta_conf_state.pkl (fitted=[추세장, 횡보장, 급변장, 혼합], total=1344, ver=5)
2026-10-19 08:55:09 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
2026-10-19 08:59:01 [INFO] LEARNING: [ScalerWarmup] 피처 로드 완료 n=30 feat=97
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 42 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 40 | 08:40:51 | 08:40:59 | 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 26 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 19 | 08:40:51 | 08:40:58 | 하한 도달불가 — out_max=0.2515 < conf_floor=0.3300 (span=0.00276 auc=0.608 out_max=0.2515, 기저율=0.2500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 8 | 08:40:52 | 08:40:56 | 축퇴 감지 — span=0.00013 auc=0.527 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 6 | 08:40:51 | 08:40:58 | 축퇴 감지 — span=0.00172 auc=0.445 out_max=0.3383 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:59 | 08:40:59 | 복원한 보정기가 축퇴 상태 — span=0.00457 auc=0.500 out_max=0.3478 (n=3928) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×294

**컴포넌트 상위 15** — `Calibration:30m`×83, `Calibration:1m`×80, `Calibration:3m`×50, `Calibration:5m`×38, `Calibration:15m`×16, `Calibration:10m`×12, `ScalerWarmup`×6, `ExtremityCorrector`×2, `Calibration:ensemble`×2, `RF`×1, `Consolidator`×1, `DriftAdjuster`×1, `SHAP`×1, `MetaConf`×1

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

### `logs/20261019_MICRO.log` — 35.2KB · 97행 · 최종 08:59:32

- 형식 평문 · 시각 인식 97행 · DEBUG=97

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #1 bid1=840.00/1 ask1=840.96/6 mp={'microprice_tick': 840.1371, 'midprice_tick': 840.48, 'depth_bias_tick': -0.3968} mlofi_tick=None queue=None
2026-10-19 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #2 bid1=839.92/2 ask1=840.96/6 mp={'microprice_tick': 840.18, 'midprice_tick': 840.44, 'depth_bias_tick': -0.3265} mlofi_tick=-1.4167 queue={'depletion_bid': 0.0, 'depletion_ask': -0.0, 'refill_bid': 1.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-19 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #3 bid1=840.00/2 ask1=840.96/6 mp={'microprice_tick': 840.24, 'midprice_tick': 840.48, 'depth_bias_tick': -0.3096} mlofi_tick=4.5167 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-19 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #4 bid1=840.60/1 ask1=840.96/6 mp={'microprice_tick': 840.6514, 'midprice_tick': 840.78, 'depth_bias_tick': -0.4358} mlofi_tick=3.3667 queue={'depletion_bid': 1.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': 0.…
2026-10-19 08:45:09 [DEBUG] MICRO: [MICRO-TICK] #5 bid1=840.60/1 ask1=840.96/5 mp={'microprice_tick': 840.66, 'midprice_tick': 840.78, 'depth_bias_tick': -0.3231} mlofi_tick=2.7333 queue={'depletion_bid': -0.0, 'depletion_ask': 1.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.0…
  …
2026-10-19 08:58:52 [DEBUG] MICRO: [MICRO-TICK] #6000 bid1=850.94/1 ask1=851.08/34 mp={'microprice_tick': 850.944, 'midprice_tick': 851.01, 'depth_bias_tick': -0.8401} mlofi_tick=-1.0 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
2026-10-19 08:59:00 [DEBUG] MICRO: [MICRO-MINUTE] #14 ts=2026-10-19 08:58:00 close=851.08 bias=-0.013940 slope=-0.020092 depth_bias=-0.3071 mlofi_norm=0.007881 mlofi_pressure=1 mlofi_slope=16.741667 queue_signal=0.0888 queue_ma=0.0311 queue_momentum=0.0276 depletion=0.4989 refill=0.5011 imbalance_s…
2026-10-19 08:59:16 [DEBUG] MICRO: [MICRO-TICK] #6100 bid1=850.96/1 ask1=851.28/1 mp={'microprice_tick': 851.12, 'midprice_tick': 851.12, 'depth_bias_tick': -0.1194} mlofi_tick=0.5 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -0.…
2026-10-19 08:59:32 [DEBUG] MICRO: [MICRO-TICK] #6200 bid1=851.92/2 ask1=852.20/2 mp={'microprice_tick': 852.06, 'midprice_tick': 852.06, 'depth_bias_tick': -0.0838} mlofi_tick=-1.45 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': -…
2026-10-19 08:59:48 [DEBUG] MICRO: [MICRO-TICK] #6300 bid1=851.12/1 ask1=851.46/1 mp={'microprice_tick': 851.29, 'midprice_tick': 851.29, 'depth_bias_tick': -0.1051} mlofi_tick=1.9833 queue={'depletion_bid': -0.0, 'depletion_ask': -0.0, 'refill_bid': 0.0, 'refill_ask': 0.0, 'bid_cancel_add_ratio': …
```

</details>

**채널** — `MICRO`×97

**컴포넌트 상위 15** — `MICRO-TICK`×83, `MICRO-MINUTE`×14

### `logs/20261019_DATA.log` — 894B · 4행 · 최종 08:58:42

- 형식 평문 · 시각 인식 4행 · INFO=4

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:58:12 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+537 individual=+348 institution=-883 oi=0 call_foreign=+22 put_foreign=-248 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-19 08:58:12 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-19 08:58:42 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+552 individual=+334 institution=-883 oi=0 call_foreign=+33 put_foreign=-310 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-19 08:58:42 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
  …
2026-10-19 08:58:12 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+537 individual=+348 institution=-883 oi=0 call_foreign=+22 put_foreign=-248 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-19 08:58:12 [INFO] DATA: [CybosInvestor] fetch#1 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
2026-10-19 08:58:42 [INFO] DATA: [CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=+552 individual=+334 institution=-883 oi=0 call_foreign=+33 put_foreign=-310 option_supported=True reason=probe ok via CpSysDib.CpSvrNew7221
2026-10-19 08:58:42 [INFO] DATA: [CybosInvestor] fetch#2 futures_supported=True program_supported=False option_supported=True futures_source=CpSysDib.CpSvrNew7221 program_source=runtime_disabled
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

### 메인 스레드 블로킹 2건 · 최대 4562ms · 5초 초과 0건

상위 — 4562ms, 3500ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261019_WARN.log`
```
--- 메인 스레드 블로킹 ×2(표본)
08:41:12 2026-10-19 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4562ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4562 band=INFO since_pipe_s=NA
08:41:16 2026-10-19 08:41:16 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3500 band=INFO since_pipe_s=NA
```

### `logs/20261019_SIGNAL.log`
```
--- 기동 복원 ×7(표본)
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
08:40:42 2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.461
```

### `logs/20261019_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:40:51 2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00158 auc=0.502 out_max=0.2959 (기준 auc<0.53 and span<0.020, 기저율=0.2952 n=105) → 보정 미적용, raw 통과
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20261019_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:40:59 [INFO] 저장 상태가 어제 데이터 — 무시 |

- 이 로그 생존구간: 08:40 ~ 08:41

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261019_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:08 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 4 | 08:52:39 [WARNING] A056B 실측=-1.54 n=7 spread=0.37 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.54 | 직전일=-2.08(prev_day:2026-10-1… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 3 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |

- 이 로그 생존구간: 08:41 ~ 08:58

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261019_SYSTEM.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 102 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=4572 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 101 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 62 | 08:54:00 [INFO] code=A056B from=08:53 to=08:54 |

- 이 로그 생존구간: 08:40 ~ 08:59

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261019_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0239) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 40 | 08:50:00 [INFO] ts=— trigger=A_WARMUP pre_market_phase2_5bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elap… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 39 | 08:55:01 [INFO] ts=— trigger=A_WARMUP pre_market_phase3_10bars n=30 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] ela… |

- 이 로그 생존구간: 08:40 ~ 08:59

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
| **오늘 20261019** | **08:59** | 로그 본문 |

- 델타 **-408분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · 마지막 갱신 2026-10-16 17:27

최근 헤딩 8개:
```
## 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도 소진: 한도 헤더 계측 · 80초 · reset 백오프) — 🟡 **구현 · 수신기 재기동 완료 · 확장 재로드(사용자) 대기 · 라이브 미검증**
## 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
### 증상 → 원인 → 결정 (이월 — 1-1 CREON 좀비 세션 충돌)
### 신규 1-5 — 수익률향상_누적대장 10-15 등록 누락 (소급 발견·해소)
### 신규 1-6 — 697차 구현 코드 당일 미커밋
### 신규 1-7 — 섀도우 TB(검증 캠페인) 재학습 강제 종료 (표본 1건, 확인 필요)
### 이월(변경 없음) — 1-1(CREON)·1-2(F-1 SessionStateDrop)·1-3(머지커밋 PC태그 확인필요)·1-4(피터2 수신오류, 697차 수정 배포·라이브 검증 대기)
## 2026-10-16 (MW0601 697차 후속 — 장후 자동조치: F-26)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
t.js`·`manifest.json`·`tools/peter2_live/latency_report.py`·`receiver.py`) + 신규 테스트 파일 `tests/test_697_peter2_ratelimit.py`가 당일 커밋 없이 작업트리에만 존재(`git --no-optional-locks log --since="2026-10-16 00:00:00 +0900"` 커밋 0건).
- **원인**: 커밋 단계가 누락됨(코드·테스트는 정상, 구현 자체의 문제는 아님).
- **결정**: `references/postmortem.md` §1-2 규칙에 따라 P1 이상점으로 등록, Fix F-26(커밋 안내)으로 사용자 조치에 반영. 이 세션은 커밋을 직접 수행하지 않는다(장후 점검 세션의 코드 변경 정책 — 관측·계획만).
- **Why**: 멀티PC 컨벤션(함정③)상 PC간 공유는 반드시 git 커밋 문서로 이뤄져야 한다. 미커밋 상태로 남으면 다음 세션의 "오늘 할일 대조"가 이 변경을 "완료-커밋확인"으로 승격시키지 못한다.
- **How to apply**: 사용자가 경로를 명시해 `git add`·`git commit` 수행(사용자 조치 2번).
- **검증**: 다음 장전 점검이 `git log`에 해당 커밋 해시 존재 확인.

### 신규 1-7 — 섀도우 TB(검증 캠페인) 재학습 강제 종료 (표본 1건, 확인 필요)
- **증상**: `logs/retrain_eod_20261016.log` 16:00:03 `[검증 캠페인] 섀도우 TB 재학습 → 실패 (rc=3221225786)`. `rc=3221225786` = Windows `STATUS_CONTROL_C_EXIT`(0xC000013A, 외부 강제종료). 핵심 EOD 재학습(6/6 호라이즌, py310_64)은 15:53:33에 정상 성공 — 이 실패는 그 뒤 이어진 검증 캠페인 전용 섀도 채널에서만 발생.
- **원인**: 미확정. 1m·3m 호라이즌은 cv_acc까지 로그에 남아 학습 자체는 끝났고 그 뒤 프로세스가 끊긴 것으로 보임 — 상위 배치 스크립트 타임아웃 추정, 확인 필요.
- **결정**: P2로 등록, 표본 1건이라 확정 결론 내리지 않음. 다음 재현 시 조사.
- **Why**: 실거래 경로(체크리스트·앙상블·진입 게이트) 밖의 섀도 채널이라 오늘 거래·내일 모델 교체에는 영향이 없다. 계측 4원칙(실패를 미측정으로 덮지 않는다)에 따라 기록만 남긴다.
- **How to apply**: 해당 없음(조사 필요 단계).
- **검증**: 다음 EOD 재학습 로그에서 섀도우 TB 재학습 재발 여부 관찰.

### 이월(변경 없음) — 1-1(CREON)·1-2(F-1 SessionStateDrop)·1-3(머지커밋 PC태그 확인필요)·1-4(피터2 수신오류, 697차 수정 배포·라이브 검증 대기)

## 2026-10-16 (MW0601 697차 후속 — 장후 자동조치: F-26)

- **증상**: 장후 점검 1-6 — 697차(피터2 X 수집 한도) 구현분 7경로가 DECISION_LOG 「구현 완료」 선언에도 당일 커밋 0건.
- **원인**: 697차 세션이 테스트·수신기 재기동까지 마치고 커밋 단계를 빠뜨림(완료주장-커밋없음).
- **결정**: F-26을 A등급(동작 무변경 — 코드는 16:13 재기동으로 이미 라이브)으로 보고 자동조치가 사후 커밋 → `7a5275b`. 리포트 목록에 없던 신규 파일 `tools/peter2_live/extension/ratelimit_hook.js`도 포함했다 — manifest 1.1.0이 MAIN world 스크립트로 참조하므로 빠지면 다른 PC·재체크아웃에서 확장 로드가 깨진다.
- **이미 반영돼 안 한 것**: 사용자 조치 1번(CREON-M1 장후 API 세션 정리)·CREON-M3(팝업 자동처리)는 `d81c079`(16:50, 692차 후속4)가 이미 구현·커밋 — 장후 리포트(16:35)보다 늦게 들어와 리포트엔 「계획 단계」로 남아 있다. CREON-M2는 계획과 다르게 갔다(「이미 실행중→예」 유지 · PlusDisconnect 무조건 요청) — 그 커밋의 판독 근거(10-16 08:39:55 '예' 뒤 좀비 소멸)를 따른다.
- **G·제5부**: 신규 구현 대상 없음(G-2는 697차 라이브 검증 10-19 대기, P5-18은 표본 갱신만 · 6칸 미완 C 유지).
- **Why**: 미커밋 상태는 멀티PC·동시 세션 stash 사고에 취약하고, 다음 장전 점검이 「완료-커밋확인」으로 승격할 수 없다.
- **How to apply**: 다음 장전이 1-6/F-26을 해소로, 1-1 CREON-M1~M3를 「구현·라이브 미검증」으로 처리. 판정은 10-19 08:35대 `logs/crash_fault.log` DibServer 크래시 부재(O-t1).
- **검증**: py37_32 `test_697`(13) + 611·612·615·668·690 trail·692 = **106 passed**. 푸시 `origin v9-dev`.

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · 마지막 갱신 2026-10-16 17:27

최근 헤딩 8개:
```
### MW0601 695차 — 장후 트리거, 조기(12:50 KST) 오발화 (2026-10-15)
### MW0601 696차 — 장후 점검, 종합 완성본 (2026-10-15)
### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
### 2026-10-16 (MW0601 — 장전 점검)
### 2026-10-16 (MW0601 — 장중 점검)
### 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도) — 장중 1-4 / G-2 후속
### 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-16 (MW0601 697차 후속 — 장후 자동조치)
```

미완료 체크박스 **3226건** (끝에서 30건)
```
- [ ] **O-t4** "장전 점검" 예약작업이 10-16 08:57 KST 근처(±수 분)에 정상 발화하는지.
- [ ] **P5-18 (신규, 판정보류)** 오후 `ConfFloorGuard` 발동(14:55, 보정기 출력상한
- [ ] **F-X1 라이브 확인** 다음 사용자 X 종료 시 SYSTEM 로그 `[Shutdown] intent=user_* … recent_stall…` 꼬리 출현 확인.
- [ ] **E-2 후속(선택)** 실청산 0·가상만 있는 날은 수집기 §5 포지션 블록(`if ex or pe:`)이 안 그려져 가상 장부 표도 안 나온다 — 그런 날이 생기면 블록 조건 확장 검토(A등급).
- [ ] **(C 이월) L-2·L-3·L-5·L-6·L-7** — 위 696차 항목 그대로. 기동·로그인 흐름 변경이라 사용자 결정 후 별도 세션.
- [ ] **(C 이월) P5-18** — 6칸 미완(변경대상·기대효과·회귀위험 미정). O-t3 표본 축적 후 재평가.
- [ ] **CREON-M1 (신규, P0)** 장후 API 세션 정리 — main.py 미실행 시에만 `PlusDisconnect()` 선행호출. 좀비 CpStart/DibServer 생성을 장후에 차단한다(10-16 딥다이브 근본원인). 저녁 수동 세션과 겹치지 않을 시간 조건 — 사용자 결정 필요.
- [ ] **CREON-M2 (신규, P1)** 자동로그인: 좀비(`CpStart` 생존 && `IsConnect=0`) 감지 시 "이미 실행중→예" 자동클릭 금지, 대신 좀비 정리 시도(`PlusDisconnect()` IsConnect 무관 1회 + CpStart 창 WM_CLOSE) → 실패 시 즉시 실패+사유 로그. 정리 수단 실효성 미검증 — …
- [ ] **CREON-M3 (신규, P1)** 자동로그인: coStarter "Unhandled exception" 팝업 자동감지 → 확인클릭 → 크래시 사실 로그 → 240초 대기 생략.
- [ ] **CREON-M4 (관찰 전용)** CREON-M1 적용 후 LAUNCH_API 증상 재평가. 별도 조치 불필요 시 종료.
- [ ] **O-p2 (장중 지속, 격상 없음)** 메인 스레드 블로킹 — 장중에도 4건 추가(09:00:03 3922ms·09:02:01 2063ms 등, 최대 4468ms), 당일 합계 6건. 전부 CB⑤ 실질 임계(5,000ms) 미달이라 경보 대상 아니지만 반복 중 — 장후까지 계속 관찰.
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```

### 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도) — 장중 1-4 / G-2 후속
- [ ] **697-1 (사용자, 10-19 장전까지)** `chrome://extensions` → Mireuk Peter2 Collector 새로고침, 버전 **1.1.0** 확인. 안 하면 F-1–F-3 미적용.
- [ ] **697-2 (10-19 장후)** `python tools/peter2_live/latency_report.py 2026-10-19` — ① `RATE` 줄 존재(없으면 `docs/피터2수집/02` §5) ② 사전등록 p90 ≤ 90초 판정 ③ 창별 rem 감소폭 vs 우리 관측 수 → 다른 소비자 유무. 판정 나무: `docs/피터2수집/03_다음단계_판정절차.md`.
- [ ] **697-3 (조건부, 사용자 결정)** 697-2 가 공유 소비를 보이면 F-5 계정 분리(MW0601 전용 X 계정 — 조율 불필요). 혼자 소진이면 RELOAD_SEC 역산, 그래도 FAIL 이면 F-4 프로필 폴백(답글형 지시 비율 선측정).
- [ ] **697-4 (장전 점검 항목)** `python tools/peter2_live/receiver.py --check` 의 `started` 가 당일 아침인지 — 10-15 13:43 수신기가 10-16 장 마감까지 살아 옛 코드로 돌았다.


### 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
- [x] **F-26 (신규, P1)** 697차 구현분(`tools/peter2_live/extension/background.js`·`content.js`·`manifest.json`·`tools/peter2_live/latency_report.py`·`receiver.py`·`tests/test_697_peter2_ratelimit.py`·`docs/피터2수집/`) 당일 커밋 — 코드는 완성·테스트(105 passed)됐으나 커밋이 없다. 사용자 조치 2번.
- [x] **1-5 해소** 수익률향상_누적대장 10-15 등록 누락 — 이 세션이 `P5-18` 행 소급 등록(10-15 n=1 + 10-16 09:00:00 n=2 증분)으로 해소.
- [ ] **1-7 (확인 필요, P2)** 섀도우 TB 재학습 강제종료(`rc=STATUS_CONTROL_C_EXIT`) 원인 조사 — 표본 1건, 반복되면 승격.
- [ ] (이월, 변경 없음) **CREON-M1 (P0)** 장후 API 세션 정리 — 적용 시간대 사용자 결정 대기. **CREON-M2·M3 (P1)** 좀비 감지·팝업 자동처리. **CREON-M4** CREON-M1 적용 후 재평가.
- [ ] (이월, 변경 없음) **L-2·L-3·L-5·L-6·L-7** CREON 런처 잔여 Fix — 기동·로그인 흐름 변경, 사용자 결정 후 별도 세션.
- [ ] (이월, 변경 없음) **F-1** session_state 마커 유실(오늘도 재발, 보완 경로로 무해) · **F-24** MAX_CONTRACTS 기대값 수집기 쪽 정정(참고 사안, 조치 불필요) · **1-3** 머지 커밋 PC태그 과거 전례 확인 필요.
- [ ] (이월, 변경 없음) **697-1** Chrome 확장 재로드(사용자, 10-19 장전까지) · **697-2** 10-19 장후 `latency_report.py` 라이브 검증 · **697-3·697-4** 조건부 후속.
- [ ] (이월, 변경 없음) **G-7** 피터2 연속손절 조기정지 · **G-8** 피터2 추세필터 — 오늘 CASE-1·3·4가 같은 패턴 재확인(10-13 선례와 동일 계열), 여전히 사용자 결정 대기(C등급).
- [ ] (참고) **P5-18** 표본 2건/2거래일(`docs/정기점검/수익률향상_누적대장.md`) — 10-15 오후·10-16 오전 `ConfFloorGuard` 재발. 다음 장후가 표본 갱신.
- [ ] (참고) 오늘 Peter2Trail(690차 후속) CASE-2에서 Δ+5.52pt 효과 실측 확인(섀도 대조 로그 자체 산출) — 기존 기능의 실거래 검증 데이터 포인트 1건, 신규 제안 아님.

### 2026-10-16 (MW0601 697차 후속 — 장후 자동조치)
- [x] **F-26** 697차 피터2 수집 개선분 커밋 → `7a5275b`(ratelimit_hook.js 포함). 106 passed.
- [x] **CREON-M1·M3** 이미 `d81c079`(692차 후속4)로 구현·커밋됨 — 예약작업 `\Mireuk\Mireuk_EodSessionCleanup` 16:30. 라이브 판정은 O-t1(10-19 08:35대 크래시 부재).
- [ ] **CREON-M2** 계획(「예」 금지)과 달리 `d81c079`는 「예」 유지 + PlusDisconnect 무조건 요청 — 효과 미검증(`was_connected` 출력). 다음 좀비 재현일에 판독.
- [ ] **(사용자)** 697-1 Chrome 확장 새로고침 v1.1.0 — 여전히 사용자 몫.

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

### `data/heartbeat_MW0601_20261019.json` — 243B · 10-19 08:59:09
```json
{
 "pid": 4572,
 "written_at": "2026-10-19T08:59:39",
 "beat_epoch": 1792367979.1312015,
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

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-19 08:46:00**

| 키 | 값 | 수집 대상일(2026-10-19)과 일치 |
|---|---|---|
| `date` | 2026-10-19 | 예 |
| `p8_last_success_date` | **(키 없음 — 미측정)** | — |
| `eod_retrain_ok_date` | **(키 없음 — 미측정)** | — |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: ✅ 우회 확인 **성공** → 스킵. session_state 마커는 비어 있었고 EOD 마커 파일로 메웠다(SessionStateDrop 재현, 실질 피해 없음)
  - `2026-10-19 08:55:09 [INFO] SYSTEM: [PreRetrain] EOD 마커 파일 직접 확인 (3일 전: 2026-10-16) → PreRetrain 스킵 (session_state 미기록 보완)`
  - `2026-10-19 08:55:09 [INFO] SYSTEM: [PreRetrain] 08:55 사전 재학습 스킵 — 1영업일 전(2026-10-16) EOD 재학습 성공 (동일 데이터 중복 불필요) | WarmupRetrain 예약 소진`

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
| 4572 | 08:40:45 | 없음 | 없음 | 판정불가 — WER **미측정** |


> 🔴 **「WER 기록 없음」을 「크래시가 아니다」로 읽지 말 것.** 참인 것은 **「미처리 네이티브 예외는 아니었다」까지**다 — `sys.exit`·창 닫기·`TerminateProcess`(하드킬)는 전부 이벤트를 안 남긴다. 종료 *의도*는 618차가 넣은 `[Shutdown] intent=` 줄과 함께 봐야 갈린다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 228개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0602-20261017-긴급알림메일-종합검토.md` | 14.1KB | 10-17 11:49 |
| `docs/정기점검/매일점검/MW0602-20261015-청산거부113분-딥다이브.md` | 21.3KB | 10-17 10:31 |
| `docs/정기점검/매일점검/MW0601-20261016-점검리포트.md` | 75.9KB | 10-16 17:28 |
| `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` | 8.9KB | 10-16 16:40 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_post.md` | 97.3KB | 10-16 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_intra.md` | 80.4KB | 10-16 12:26 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_pre.md` | 59.8KB | 10-16 08:59 |
| `docs/정기점검/매일점검/MW0601-20261015-점검리포트.md` | 69.1KB | 10-15 17:48 |

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
2. `logs/20261019_LEARNING.log`: **축퇴** 8건(표본)
3. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
4. 미커밋 변경 1건 (실질 1건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261019*.log` (Windows) / `grep 강제청산 logs/*20261019*.log`*