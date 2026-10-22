# 미륵이 증거 다이제스트 — 2026-10-19 / INTRA

- 생성 2026-10-19 12:26:37 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01mtr4csrngi9x5uqtbcvxnv/mnt/futures`
- 점검 범위: pre, intra (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261019` · `2026-10-19` · `261019` · `1019`
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **28개** 파일 · 28개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude-{DATE}-intra-cowork-intra-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261019-intra-cowork-intra-20261019.json` | 174B | 10-19 12:26 |
| `claude-{DATE}-pre-cowork-pre-{DATE}.json` | 1 | `data/dailycheck_markers/claude-20261019-pre-cowork-pre-20261019.json` | 170B | 10-19 09:03 |
| `force_flat_guard_{DATE}.log` | 1 | `logs/force_flat_guard_20261019.log` | 125B | 10-19 08:40 |
| `freeze_sentinel_{DATE}.log` | 1 | `logs/freeze_sentinel_20261019.log` | 197B | 10-19 08:40 |
| `heartbeat_MW0601_{DATE}.json` | 1 | `data/heartbeat_MW0601_20261019.json` | 242B | 10-19 12:26 |
| `launcher_{DATE}_084001_30125.log` | 1 | `logs/Mireuk_batch/launcher_20261019_084001_30125.log` | 1.3MB | 10-19 12:26 |
| `maekjeom_ladder_{DATE}.log` | 1 | `logs/maekjeom_ladder_20261019.log` | 109B | 10-19 08:44 |
| `peter2_receiver_{DATE}.log` | 1 | `logs/peter2_receiver_20261019.log` | 37.2KB | 10-19 12:25 |
| `position_state.json.gen_{DATE}_101102` | 1 | `data/position_state.json.gen_20261019_101102` | 1.5KB | 10-19 09:09 |
| `position_state.json.gen_{DATE}_102021` | 1 | `data/position_state.json.gen_20261019_102021` | 1.5KB | 10-19 10:20 |
| `position_state.json.gen_{DATE}_113743` | 1 | `data/position_state.json.gen_20261019_113743` | 1.5KB | 10-19 10:58 |
| `retrain_intraday_20260811_{DATE}59.log` | 1 | `logs/retrain_intraday_20260811_101959.log` | 4.5KB | 08-11 10:20 |
| `retrain_intraday_{DATE}_094000.log` | 1 | `logs/retrain_intraday_20261019_094000.log` | 3.2KB | 10-19 09:40 |
| `retrain_intraday_{DATE}_114000.log` | 1 | `logs/retrain_intraday_20261019_114000.log` | 3.2KB | 10-19 11:40 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261019.log` | 41.0KB | 10-19 12:20 |
| `trail_state_{DATE}.json` | 1 | `data/peter2_live/trail_state_2026-10-19.json` | 336B | 10-19 11:37 |
| `{DATE}.jsonl` | 1 | `data/peter_feed/_raw/2026-10-19.jsonl` | 2.5KB | 10-19 10:53 |
| `{DATE}_DATA.log` | 1 | `logs/20261019_DATA.log` | 231.2KB | 10-19 12:26 |
| `{DATE}_DEBUG.log` | 1 | `logs/20261019_DEBUG.log` | 154.0KB | 10-19 12:26 |
| `{DATE}_HEALTH.log` | 1 | `logs/20261019_HEALTH.log` | 2.3KB | 10-19 12:25 |
| `{DATE}_HOGA.log` | 1 | `logs/20261019_HOGA.log` | 34.9MB | 10-19 12:26 |
| `{DATE}_LEARNING.log` | 1 | `logs/20261019_LEARNING.log` | 178.9KB | 10-19 12:26 |
| `{DATE}_MICRO.log` | 1 | `logs/20261019_MICRO.log` | 658.1KB | 10-19 12:26 |
| `{DATE}_PROBE.log` | 1 | `logs/20261019_PROBE.log` | 55.5KB | 10-19 12:26 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20261019_SIGNAL.log` | 299.0KB | 10-19 12:26 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20261019_SYSTEM.log` | 613.1KB | 10-19 12:26 |
| `{DATE}_TRADE.log` | 1 | `logs/20261019_TRADE.log` | 15.9KB | 10-19 11:42 |
| `{DATE}_WARN.log` | 1 | `logs/20261019_WARN.log` | 358.6KB | 10-19 12:26 |

## 2. 코드·커밋 상태

- HEAD `5aaad2d` · 브랜치 `v9-dev` · 미커밋 6건 · 실질 변경 3건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 3 · 미추적 3 · 삭제 0 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md`
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 4.6초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
 M docs/미륵이고도화3/신동2/live/신동2_해설_MW0601-20261019.md
?? docs/미륵이고도화3/피터2/live/피터2_실시간_MW0601-20261019.md
?? docs/정기점검/매일점검/MW0601-20261019-점검리포트.md
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

_본문 미열람(설정): `20261019_HOGA.log` 34.9MB — 존재와 크기만 증거로 본다_

_다이제스트 대상 8/19개 (중요도순). 제외: `retrain_intraday_20261019_094000.log`, `20261019_MICRO.log`, `20261019_DATA.log`, `20261019_PROBE.log`, `launcher_20261019_084001_30125.log`, `20261019_DEBUG.log`, `shindong2_20261019.log`, `peter2_receiver_20261019.log`_

### `logs/20261019_TRADE.log` — 15.9KB · 113행 · 최종 11:42:00

- 형식 평문 · 시각 인식 113행 · WARNING=10, INFO=103

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:59 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-10-19 08:41:05 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-10-19 09:04:45 [INFO] TRADE: [Peter2] 진입시도 SHORT 1계약 @863.02 손절 866.92 목표 - — brk_dn SHORT 지시 865(미니 862.92) 현재 863.02
2026-10-19 09:04:45 [INFO] TRADE: [Position] 진입 SHORT 1계약 @ 863.02 | 손절=866.92 1차=-9136.98(×1.00) 2차=-9136.98
2026-10-19 09:04:45 [INFO] TRADE: [주문요청] SHORT->SHORT 1계약 @ 863.02 등급=P 역방향진입=OFF 체결대기
  …
2026-10-19 11:41:04 [INFO] TRADE: [Position] 진입 LONG 1계약 @ 878.5 | 손절=876.22 1차=878.96(×0.30) 2차=880.78 horizon=1m hurst=neutral
2026-10-19 11:41:04 [INFO] TRADE: [Virtual] 미륵 가상진입 LONG 1계약 @878.50 손절 876.22 (principal)
2026-10-19 11:41:04 [INFO] TRADE: [Position] 1계약 TP1 보호전환 @ 878.96 | mode=atr_profit | stop 876.22 -> 878.88 | 회계상 확정 33% @ +0.46pt
2026-10-19 11:42:00 [INFO] TRADE: [Position] 청산 LONG @ 878.879275 | PnL=+0.38pt (+17,295원) 수수료=1,669원 | 가상:하드스톱
2026-10-19 11:42:00 [INFO] TRADE: [Virtual] 미륵 가상청산 LONG 1계약 @878.88 가상:하드스톱 | +0.38pt +17,295원 (포지션 종료)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `PositionFallback` | 10 | 09:04:45 | 11:02:09 | entry_horizon 미설정 → TP1 배수 폴백 1.00 적용 (호라이즌별 설계값의 최대 2배). status=SHORT qty=1 entry=862.96 — 진입 경로가 파라미터를 넘기지 않았다(F-5 대상) |

**채널** — `TRADE`×113

**컴포넌트 상위 15** — `Position`×29, `Chejan`×18, `Virtual`×17, `Peter2Trail`×13, `PositionFallback`×10, `Peter2`×6, `주문요청`×6, `체결진입`×3, `TickStop-S0C`×3, `청산 완료`×3, `Sizer`×2, `진입체크`×2, `ProfitGuard`×1

### `logs/20261019_WARN.log` — 358.6KB · 1601행 · 최종 12:26:29

- 형식 평문 · 시각 인식 1601행 · WARNING=1601

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 78ms
2026-10-19 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr11)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-19 08:41:08 [WARNING] SYSTEM: [CybosDailyPnl] 기준일자 형식 전환 %y%m%d→%Y%m%d account=783343908 — 앞 형식은 '12242 조회된 내용이 없습니다. (ciisvr11)(cii.cif.cstpftrt.selfoaccptthdys)' 였고 뒤 형식은 성공했다. 이후 이 계좌는 %Y%m%d 사용
2026-10-19 08:41:08 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 203ms account=783343908
  …
2026-10-19 12:26:09 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 94.2ms | size=1994x950 candles=222 grid=25.2 spans=10.6 candles=21.5 dir=0.8 regime=5.2 markers=28.9 axes=0.6 cross=0.0 | slow_cnt=1347 total_cnt=1462 overlay_cnt=21212
2026-10-19 12:26:19 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 92.1ms | size=1994x950 candles=222 grid=22.9 spans=10.5 candles=20.5 dir=0.8 regime=5.7 markers=29.6 axes=0.6 cross=0.0 | slow_cnt=1348 total_cnt=1463 overlay_cnt=21229
2026-10-19 12:26:29 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 92.7ms | size=1994x950 candles=222 grid=21.7 spans=9.4 candles=22.3 dir=0.8 regime=5.6 markers=31.0 axes=0.6 cross=0.0 | slow_cnt=1349 total_cnt=1464 overlay_cnt=21247
2026-10-19 12:26:39 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 128.2ms | size=1994x950 candles=222 grid=30.0 spans=13.1 candles=29.6 dir=1.0 regime=7.0 markers=45.3 axes=0.7 cross=0.0 | slow_cnt=1350 total_cnt=1465 overlay_cnt=21260
2026-10-19 12:26:51 [WARNING] SYSTEM: [ChartDBG] paintEvent slow 107.9ms | size=1994x950 candles=222 grid=28.1 spans=13.5 candles=25.1 dir=0.8 regime=6.2 markers=32.1 axes=0.6 cross=0.0 | slow_cnt=1351 total_cnt=1466 overlay_cnt=21275
```

</details>

**WARNING — 태그 30종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ChartDBG` | 1351 | 09:15:50 | 12:26:51 | paintEvent slow 149.4ms | size=1994x950 candles=31 grid=19.5 spans=50.4 candles=55.7 dir=0.1 regime=0.1 markers=4.6 axes=6.0 cross=0.0 | slow_cnt=1 total_cnt=116 overlay_cnt=602 |
| `LiveDBG` | 65 | 08:41:08 | 12:23:09 | request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `OptionFlowChart` | 37 | 08:41:18 | 12:22:09 | 그리기 69.0ms > 50ms (5분 스로틀) — 메인 스레드를 매매 파이프라인과 공유한다. 크기 785x1001 |
| `ChejanFlow` | 18 | 09:04:45 | 11:37:43 | account='783343908' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A056B' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='158' | pending='ENTRY:SHORT qty=1 filled=0 order_no=? reason=진입 req_at=09:04:45.024' | positio… |
| `ChejanMatch` | 18 | 09:04:45 | 11:37:43 | order_no='158' | pending='ENTRY:SHORT qty=1 filled=0 order_no=158 reason=진입 req_at=09:04:45.024' | pending_matched=True |
| `Peter2` | 13 | 09:24:11 | 11:55:08 | 오프셋 자동 적용 -2.08(prev_day:2026-10-16, safe=True) → -1.72(live:09:24:09, safe=True) |
| `PendingOrder` | 12 | 09:04:45 | 11:37:43 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 863.02, 'reason': '진입', 'hint_source': '', 'atr': 2.5714, 'grade': 'P', 'stage': None, 'order_no': '', 'filled_qt… |
| `Peter2Offset` | 9 | 08:47:09 | 11:23:38 | A056B 실측=-1.48 n=2 spread=0.0 safe=False(표본 부족 n=2<8) 창=08:46~08:47 전일정=-1.48 | 직전일=-2.08(prev_day:2026-10-16, safe=True) 차=0.6 | 61ms |
| `ScalerRefresh` | 9 | 09:05:00 | 12:11:00 | 5분 누적 수익률 +1.366% (임계 ±0.845%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 7 | 09:00:01 | 12:24:01 | level=WARNING degraded=OFF | latency=1232ms | quality=1.00 | cache_age=51s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2 |
| `PipePerf` | 6 | 09:00:01 | 11:41:04 | total=1232ms | S0=2ms S1=14ms S2=0ms S3=0ms S4=61ms S5=909ms S6=229ms S7=11ms S8=6ms |
| `CB⑤` | 6 | 09:00:01 | 11:41:04 | 파이프라인 1232ms 경고 (기준 1000ms) [장시작 버스트] [장시작버스트→임계9s] |

**채널** — `SYSTEM`×1594, `HEALTH`×7

**컴포넌트 상위 15** — `ChartDBG`×1351, `LiveDBG`×65, `OptionFlowChart`×37, `ChejanFlow`×18, `ChejanMatch`×18, `Peter2`×13, `PendingOrder`×12, `Peter2Offset`×9, `ScalerRefresh`×9, `Health`×7, `PipePerf`×6, `CB⑤`×6, `ExitCooldown`×6, `EntryAttempt`×5, `EntrySendOrderResult`×3

### `logs/20261019_SYSTEM.log` — 613.1KB · 4089행 · 최종 12:26:30

- 형식 평문 · 시각 인식 4082행 · INFO=4082, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:45 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=4572 | 행감지=30s all_threads=True
2026-10-19 08:40:46 [INFO] SYSTEM: [DBInit] 합계 0.43s | predictions=0.05s trades=0.22s daily_stats=0.01s shap=0.01s raw_data=0.10s broker_pnl=0.02s broker_recon=0.01s premarket_levels=0.02s
2026-10-19 08:40:46 [INFO] SYSTEM: [System] DB 초기화 완료 (0.4s)
2026-10-19 08:40:46 [INFO] SYSTEM: [System] 미륵이 초기화
2026-10-19 08:40:46 [INFO] SYSTEM: 미륵이 초기화
  …
2026-10-19 12:26:17 [INFO] SYSTEM: [CybosRT-TICK] #97900 code=A056B raw_time=122616 parsed=12:26:16 price=884.10 vol=1 bid1=883.98 ask1=884.10 flag=49 side=BUY anchor=1/0
2026-10-19 12:26:28 [INFO] SYSTEM: [OptionChain][Worker] 완료 2921ms | target=48 valid=48 PCR=1.699 ATM_PCR=3.079 GEX=-1.16B
2026-10-19 12:26:30 [INFO] SYSTEM: [TickUI] alive ticks=97960 code=A056B close=884.22
2026-10-19 12:26:38 [INFO] SYSTEM: [CybosRT-TICK] #98000 code=A056B raw_time=122638 parsed=12:26:38 price=884.40 vol=2 bid1=884.38 ask1=884.40 flag=49 side=BUY anchor=2/0
2026-10-19 12:26:38 [INFO] SYSTEM: [PumpGuard] rollover 연기 — 메인 펌프(BlockRequest 대기) 중 재진입 회피 (누적 392회, 재시도=호출부)
```

</details>

**채널** — `SYSTEM`×4082

**컴포넌트 상위 15** — `CybosRT-TICK`×985, `CybosInvestorRaw`×824, `PumpGuard`×392, `TickUI`×221, `CybosRT-ROLLOVER`×221, `BAR-CLOSE`×221, `CVD-ANCHOR`×221, `S6Detail`×207, `PipePerf`×207, `System`×59, `MicroRegime`×55, `OptionChain`×44, `OptionBook`×41, `RegimeFingerprint`×38, `CybosEvent`×36

### `logs/20261019_SIGNAL.log` — 299.0KB · 2667행 · 최종 12:26:00

- 형식 평문 · 시각 인식 2667행 · WARNING=890, INFO=1777

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.452
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.443
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.439
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.461
2026-10-19 08:40:42 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.443
  …
2026-10-19 12:26:00 [INFO] SIGNAL: --- 2026-10-19 12:25:00 분봉 파이프라인 시작 ---
2026-10-19 12:26:00 [INFO] SIGNAL: [FQAdj] fq=1.00 → min_conf 0.65→0.62 (완화)
2026-10-19 12:26:00 [INFO] SIGNAL: [Ensemble] dir=+0 conf=33.8% grade=X regime=NEUTRAL
2026-10-19 12:26:00 [INFO] SIGNAL: 앙상블: dir=+0 conf=33.8% grade=X micro=횡보장
2026-10-19 12:26:00 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.338<mc0.620)
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 624 | 09:00:01 | 12:11:01 | 1m 'macro_vix' scale=0.0172 → floor=0.10 적용 (z-score 폭발 방지) |
| `Checklist` | 93 | 09:06:00 | 12:24:01 | CORE VWAP ✗ → 강제 X등급 (pass_count=9, group=short) | VWAP pos=+1.237 need <0 (SHORT) bull_exh=0.00 |
| `ScalerMonitor` | 61 | 09:00:00 | 11:42:00 | ts=08:59 horizon=1m age=1m max_z=-4.88(macro_nasdaq_chg) extreme=2 adj=2 |
| `Model` | 48 | 09:00:00 | 11:41:03 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `WeightCollapse` | 48 | 09:07:00 | 12:22:00 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 10 | 09:35:00 | 12:24:01 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ScalerRefresh` | 6 | 08:45:09 | 08:45:09 | 1m CORE 'cvd_divergence' raw_std≈0(0.0239) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×2667

**컴포넌트 상위 15** — `ScalerFloor`×678, `SIGNAL`×414, `MetaGate`×263, `FQAdj`×206, `Ensemble`×204, `ZeroDiag`×183, `Checklist`×105, `ATR-Horizon`×86, `Model`×66, `ScalerMonitor`×61, `차단`×58, `MicroRegime`×55, `WeightCollapse`×48, `InstabilityGate`×46, `ToxicityGate`×34

### `logs/20261019_LEARNING.log` — 178.9KB · 1665행 · 최종 12:26:00

- 형식 평문 · 시각 인식 1665행 · WARNING=146, INFO=1519

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 08:40:47 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:1m] 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:30m] 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-10-19 08:40:51 [WARNING] LEARNING: [Calibration:3m] 축퇴 감지 — span=0.00158 auc=0.502 out_max=0.2959 (기준 auc<0.53 and span<0.020, 기저율=0.2952 n=105) → 보정 미적용, raw 통과
  …
2026-10-19 12:26:00 [INFO] LEARNING: [sigma] sigma_at_t=0.1374% buf_n=20 nonzero=20 prev_p=883.94 cur_p=883.98
2026-10-19 12:26:00 [INFO] LEARNING: ✗ 1m 예측 실패 (conf=37.4% 예측=DN 실제=FL)
2026-10-19 12:26:00 [INFO] LEARNING: ✗ 3m 예측 실패 (conf=33.3% 예측=UP 실제=DN)
2026-10-19 12:26:00 [INFO] LEARNING: ✗ 30m 예측 실패 (conf=56.3% 예측=FL 실제=UP)
2026-10-19 12:26:00 [INFO] LEARNING: [SGD] 3건 학습 | SGD비중=30% 50분정확도=0.0%
```

</details>

**WARNING — 태그 7종 (상위 7)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration:30m` | 44 | 08:40:51 | 11:50:00 | 축퇴 감지 — span=0.00273 auc=0.167 out_max=0.2139 (기준 auc<0.53 and span<0.020, 기저율=0.2125 n=80) → 보정 미적용, raw 통과 |
| `Calibration:1m` | 42 | 08:40:51 | 11:28:01 | 축퇴 감지 — span=0.00223 auc=0.415 out_max=0.3384 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:3m` | 26 | 08:40:51 | 08:40:59 | 하한 도달불가 — out_max=0.2632 < conf_floor=0.3300 (span=0.00113 auc=0.675 out_max=0.2632, 기저율=0.2625 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:5m` | 19 | 08:40:51 | 08:40:58 | 하한 도달불가 — out_max=0.2515 < conf_floor=0.3300 (span=0.00276 auc=0.608 out_max=0.2515, 기저율=0.2500 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위). |
| `Calibration:15m` | 8 | 08:40:52 | 08:40:56 | 축퇴 감지 — span=0.00013 auc=0.527 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |
| `Calibration:10m` | 6 | 08:40:51 | 08:40:58 | 축퇴 감지 — span=0.00172 auc=0.445 out_max=0.3383 (기준 auc<0.53 and span<0.020, 기저율=0.3375 n=80) → 보정 미적용, raw 통과 |
| `Calibration:ensemble` | 1 | 08:40:59 | 08:40:59 | 복원한 보정기가 축퇴 상태 — span=0.00457 auc=0.500 out_max=0.3478 (n=3928) → 보정 미적용으로 시작, raw 통과. 표본이 새로 쌓여 순위변별력이 회복되면 fit()에서 자동 재적용된다. |

**채널** — `LEARNING`×1665

**컴포넌트 상위 15** — `LEARNING`×664, `SGD`×207, `sigma`×194, `Bias⚠`×113, `Calibration:30m`×87, `Calibration:1m`×83, `Bias`×72, `Calibration:3m`×50, `MetaConf`×41, `Calibration:5m`×38, `ScalerWarmup`×27, `OnlineLearner`×21, `Calibration:15m`×16, `BiasReset`×15, `Calibration:10m`×12

### `logs/20261019_HEALTH.log` — 2.3KB · 15행 · 최종 12:25:00

- 형식 평문 · 시각 인식 15행 · WARNING=7, INFO=8

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 09:00:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=1232ms | quality=1.00 | cache_age=51s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2
2026-10-19 09:01:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=613ms | quality=1.00 | cache_age=111s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2
2026-10-19 09:29:00 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 400ms (표본 20분)
2026-10-19 09:41:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=3493ms | quality=1.00 | cache_age=128s | exceptions_10m=0
2026-10-19 09:42:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=562ms | quality=1.00 | cache_age=1s | exceptions_10m=0
  …
2026-10-19 11:33:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=310ms | quality=1.00 | cache_age=57s | exceptions_10m=3 | exc_tags=[Peter2]×2 [Peter2Offset]×1
2026-10-19 11:41:04 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=4113ms | quality=1.00 | cache_age=174s | exceptions_10m=3 | exc_tags=[ExitCooldown]×1 [Peter2]×1 [SHAP]×1
2026-10-19 11:42:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=385ms | quality=1.00 | cache_age=47s | exceptions_10m=3 | exc_tags=[ExitCooldown]×1 [Peter2]×1 [SHAP]×1
2026-10-19 12:24:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=419ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-10-19 12:25:00 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=271ms | quality=1.00 | cache_age=59s | exceptions_10m=0
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 7 | 09:00:01 | 12:24:01 | level=WARNING degraded=OFF | latency=1232ms | quality=1.00 | cache_age=51s | exceptions_10m=2 | exc_tags=[Peter2Offset]×2 |

**채널** — `HEALTH`×15

**컴포넌트 상위 15** — `Health`×14, `HealthTrend`×1

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

### `logs/retrain_intraday_20261019_114000.log` — 3.2KB · 24행 · 최종 11:40:25

- 형식 평문 · 시각 인식 24행 · WARNING=2, INFO=22

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-19 11:40:00,685 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-19 11:40:00,685 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-10-19 11:40:00,686 [INFO] RETRAIN_INTRADAY: ==================================================
2026-10-19 11:40:00,686 [INFO] RETRAIN_INTRADAY: [DLL] BLAS 경로 이미 충족
2026-10-19 11:40:00,686 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['10m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dfff380d.json
  …
2026-10-19 11:40:25,178 [INFO] LEARNING: [Retrain] 슈퍼셋에 폐기 예정 컬럼 10개 유지 중 (설계상 정상 — 제거는 P2-B 경로): cvd, cvd_direction, cvd_divergence, cvd_exhaustion, cvd_exhaustion_signal, cvd_slope, macro_risk_off, ofi_imbalance, program_individual_net_krw, program_institution_net_krw
2026-10-19 11:40:25,179 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-10-19 11:40:25,179 [INFO] LEARNING: [Retrain] 완료 | 20.7초 | 성공=1/1 호라이즌
2026-10-19 11:40:25,180 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 24.5s 데이터=4800행
2026-10-19 11:40:25,182 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_dfff380d.json
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `BackfillFilter` | 1 | 11:40:15 | 11:40:15 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 18413/43985 제외 (418차 결정 1) — 남은 25572행 |
| `UnitMismatch` | 1 | 11:40:15 | 11:40:15 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/25572행 제외 (559차 P1'-2) — 남은 24126행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |

**채널** — `LEARNING`×14, `RETRAIN_INTRADAY`×7, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×12, `RETRAIN_INTRADAY`×6, `DLL`×1, `BackfillFilter`×1, `UnitMismatch`×1, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 2 |
| 진입 등록(`[Position] 진입`) | 12 |
| └ 그중 **엔진**(`horizon=` 동반) | 0 |
| └ 그중 피터2(`[Peter2] 진입` 동반) — 보조 로직 | 3 |
| └ 그중 가상(`[Virtual] … 가상진입` 동반) — **실주문 없음** | 9 |
| └ 그중 판별불가(둘 다 없음 — 미측정) | 0 |
| 체결(`[체결진입]`·`[Position] 체결진입`) | 3 |
| └ 그중 외부(`[체결동기화] 외부진입`) — **계좌** | 0 |
| 청산(`체결청산`) | 3 |
| 차단(`[차단]`) | 58 |
| 사이저 호출(`[Sizer]`) | 2 |

> 🔴 **엔진 진입 0건인데 계좌 체결 3건**(외부표식 0 · 피터2 3 · 판별불가 0) — 이 날의 손익은 엔진 성적이 아니다. 아래 포지션 표의 「출처」 칸을 반드시 볼 것.
>
> 별도로 **가상 장부 진입 9건**이 `[Position] 진입` 에 섞여 있다 — 실주문이 없으므로 계좌 체결·손익과 무관하다(아래 「가상 장부」 표).

### 포지션 3건 · 승 1 (33%) · 합계 -5.34pt (-271,964원)  ※ 레그 3행

> ⚠ **단위 주의** — 이 표는 **포지션 단위**다. `체결청산` 행만 세면(종전 방식) 부분청산으로 빠져나간 레그가 통째로 사라진다. 2026-08-20 실측: 레그 기준 4건 승 1(25%) −230,004원 vs **포지션 기준 4건 승 2(50%) −348,018원** — 손익 34% 과소, 승률 25%p 과소였다(계측 4원칙 ①).

| 진입 | 출처 | 방향 | 진입수량 | hz | 레그 | 포지션 pt | 포지션 net(원) | 최종 청산사유 |
|---|---|---|---|---|---|---|---|---|
| 09:04:45 | 피터2 | SHORT | 1 | — | 1 | -3.94 | -198,640 | 하드스톱(틱) |
| 09:09:07 | 피터2 | SHORT | 1 | — | 1 | -5.02 | -252,649 | 하드스톱(틱) |
| 10:20:21 | 피터2 | SHORT | 1 | — | 1 | +3.62 | +179,325 | 하드스톱(틱) |

**출처별 소계** — 피터2 3건 -271,964원

> ⚠ 「외부」는 `[체결동기화] 외부진입`이 동반된 자리다 — 엔진 판단이 만든 것이 아니므로 **엔진 성적·승률에 넣지 말 것**. 「피터2」는 `[Peter2] 진입`이 동반된 보조 로직 자리로 역시 엔진 성적이 아니다. 「추정」은 판별 불가(미측정)이지 「외부 아님」이 아니다(계측 4원칙 ②).

**가상 장부 9건(청산 8 · 합계 -53,266원) — 실주문 없음, 엔진·계좌 손익 아님**

| 진입 | 주체 | 방향 | 수량 | hz | 가상 pt | 가상 net(원) | 가상 청산사유 |
|---|---|---|---|---|---|---|---|
| 09:33:09 | 신동 | LONG | 1 | — | -4.88 | -245,644 | 가상:하드스톱 |
| 09:39:09 | 신동 | SHORT | 1 | — | -2.54 | -128,636 | 가상:하드스톱 |
| 09:45:09 | 신동 | LONG | 1 | — | +3.42 | +169,351 | 가상:외부목표 |
| 09:50:09 | 신동 | SHORT | 1 | — | +6.16 | +306,350 | 가상:신동1차 |
| 10:13:09 | 신동 | LONG | 1 | — | -4.86 | -244,663 | 가상:하드스톱 |
| 10:59:09 | 신동 | SHORT | 1 | — | -1.58 | -80,657 | 가상:신동미러:SL |
| 11:02:09 | 신동 | LONG | 1 | — | +0.00 | +0 | 가상청산 로그 없음(장후 일괄평가 대기일 수 있음) |
| 11:35:01 | 미륵 | LONG | 1 | 3m | +3.10 | +153,338 | 가상:TP2(전량) |
| 11:41:04 | 미륵 | LONG | 1 | 1m | +0.38 | +17,295 | 가상:하드스톱 |

> ⚠ 이 표는 `[Virtual] … 가상진입`/`가상청산` 로그로 조립한 **가상 장부**다. 같은 초에 `[Position] 진입` 이 찍혀 진입 건수에는 잡히지만 체결이 없다 — 3원 대사(로그·DB·브로커)에서 로그 쪽이 더 많아 보이면 먼저 이 표를 뺄 것.

**청산 레그 3행** (부분청산 0 · 전량청산 3)

> 단위 주 — 여기 레그는 **체결 단위**다. `trades` 테이블은 같은 부분청산을 주문 단위 한 행으로 합쳐 적으므로 DB 행수가 더 적을 수 있다(2026-08-20: 체결 8 vs DB 7). **포지션 합계는 양쪽이 일치해야 한다** — 아래 정합성 줄이 그것을 본다.

| 시각 | 종류 | 계약 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|---|
| 09:06:30 | 전량 | 1 | -3.94 | -198,640 | 하드스톱(틱) |
| 10:11:02 | 전량 | 1 | -5.02 | -252,649 | 하드스톱(틱) |
| 11:37:43 | 전량 | 1 | +3.62 | +179,325 | 하드스톱(틱) |

**청산 사유 분포(레그 단위)** — `하드스톱(틱)`×3

> 최종 청산이 하드스톱·손절 계열인 포지션 3/3건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

**정합성**: 레그합 -271,964 = 포지션합 -271,964 → OK · `[청산 완료]` 3건 = 조립 포지션 3건 → OK

### 진입 12건

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

계약수 분포 — 1계약×12

등급 분포 — `A급(원시C)`×2

**진입한 건들의 체크리스트 미통과 항목** — `fore`×2, `prev`×1, `risk`×1, `chas`×1

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×2

실제 진입 계약수 — **1계약**×12

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×2

### 차단 사유 58건 · 28종

| 건수 | 사유 |
|---|---|
| 25 | 등급X — 미통과 항목: 2_confidence |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 9_risk, 11_countertrend |
| 2 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 9_risk, 11_countertrend |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 9_risk, 11_countertrend |
| 2 | 등급X — 미통과 항목: 3_vwap, 5_ofi, 6_foreign, 9_risk |
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
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 22.0pt > ATR×5.0=12.4pt (시가=841.08 반등위험) |
| 1 | 청산 후 쿨다운 — 121초 후 재진입 가능 |

**체크리스트 미통과 항목 누적** — `2_confidence`×25, `3_vwap`×19, `6_foreign`×19, `9_risk`×14, `4_cvd`×12, `5_ofi`×12, `7_prev_bar`×10, `11_countertrend`×8, `10_chase`×1

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 2건

- `연속 손절 1회 (300초 창, 포지션 단위)` ×2

> CB② 는 `CB_CONSEC_STOP_LIMIT=3`(2026-09-02 복원) — **3회 도달 시 실제로 당일 정지한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 6건 · 최대 4562ms · 5초 초과 0건

상위 — 4562ms, 4203ms, 3750ms, 3500ms, 2844ms, 2594ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20261019_WARN.log`
```
--- ConstOut ×2(표본)
09:39:00 2026-10-19 09:39:00 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(5m=0.3688)
11:39:00 2026-10-19 11:39:00 [WARNING] SYSTEM: [ConstOut] ['10m'] 상수 출력 확정 → 스케일러 재적합 시작 | bias_override=N gbm_raw(10m=0.4350)
--- [CB] ×2(표본)
09:06:30 2026-10-19 09:06:30 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
10:11:02 2026-10-19 10:11:02 [WARNING] SYSTEM: [CB] 연속 손절 1회 (300초 창, 포지션 단위)
--- [ExitCooldown] ×7(표본)
09:06:30 2026-10-19 09:06:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:09:30)
09:06:30 2026-10-19 09:06:30 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 09:09:30)
10:11:02 2026-10-19 10:11:02 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:14:02)
10:11:02 2026-10-19 10:11:02 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 3분 재진입 금지 (until 10:14:02)
--- [SHAP] 슬로우 ×3(표본)
11:35:01 2026-10-19 11:35:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1037ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
11:43:01 2026-10-19 11:43:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 943ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
12:10:01 2026-10-19 12:10:01 [WARNING] SYSTEM: [SHAP] 슬로우 감지 930ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×6(표본)
08:41:12 2026-10-19 08:41:12 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 4562ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=4562 band=INFO since_pipe_s=NA
08:41:16 2026-10-19 08:41:16 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3500ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[] | [MainStall] stall_ms=3500 band=INFO since_pipe_s=NA
09:00:02 2026-10-19 09:00:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2844ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2844 band=INFO since_pipe_s=0.1
09:05:02 2026-10-19 09:05:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2594ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] | [MainStall] stall_ms=2594 band=INFO since_pipe_s=0.1
```

### `logs/20261019_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:35:00 2026-10-19 09:35:00 [INFO] SYSTEM: [ConstOut] 3m 재학습 트리거 억제 — BiasReset uniform fallback 구간이라 GBM 출력이 아니다 (gbm_raw=0.4363) | 앙상블 제외는 유지
09:39:00 2026-10-19 09:39:00 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:41:00 (const_output)
09:39:00 2026-10-19 09:39:00 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['5m']
09:39:00 2026-10-19 09:39:00 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['5m'] load=447ms fit=52ms total=503ms
--- PSI ×8(표본)
09:00:00 2026-10-19 09:00:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:05:00 2026-10-19 09:05:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:10:00 2026-10-19 09:10:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
09:16:00 2026-10-19 09:16:00 [INFO] SYSTEM: [RegimeFingerprint] PSI=0.003 level=0 (heartbeat)
```

### `logs/20261019_SIGNAL.log`
```
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

- 이 로그 생존구간: 08:40 ~ 11:42

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261019_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 16 | 08:41:08 [WARNING] request_futures_balance 호출 account=783343908 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 10 | 08:52:39 [WARNING] A056B 실측=-1.54 n=7 spread=0.37 safe=False(표본 부족 n=7<8) 창=08:46~08:52 전일정=-1.54 | 직전일=-2.08(prev_day:2026-10-1… |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 48 | 08:55:09 [WARNING] scaler 노후=0h  z경고피처=12개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 86 | 09:54:00 [WARNING] paintEvent slow 83.0ms | size=1994x950 candles=70 grid=28.9 spans=7.3 candles=8.8 dir=0.3 regime=4.4 markers=… |
| 12:00 | 장중 중간점 | 85 | 11:54:01 [WARNING] paintEvent slow 122.2ms | size=1994x950 candles=190 grid=30.0 spans=14.4 candles=26.2 dir=1.0 regime=7.7 mark… |

- 이 로그 생존구간: 08:41 ~ 12:26

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20261019_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 102 | 08:40:45 [INFO] 활성화 | file=logs\crash_fault.log PID=4572 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 140 | 08:49:00 [INFO] code=A056B from=08:48 to=08:49 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 265 | 08:54:00 [INFO] code=A056B from=08:53 to=08:54 |
| 10:00 | 장중 초반 | 243 | 09:54:00 [INFO] code=A056B from=09:53 to=09:54 |
| 12:00 | 장중 중간점 | 198 | 11:54:00 [INFO] code=A056B from=11:53 to=11:54 |
| 14:00 | _장중 후반 · 장중 재학습 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 12:26

**매분 루프 커버리지 09:00~12:26: 207/207분 (100.0%)**

_장중 수집 — 분모를 수집 시각 12:26 까지로 줄였다. 이후 164분(~15:10)은 **미도래**라 제외(결손 아님)._

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20261019_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 44 | 08:45:09 [WARNING] 1m CORE 'cvd_divergence' raw_std≈0(0.0239) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 110 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 242 | 09:00:00 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 131 | 09:54:00 [WARNING] 신뢰도 미달 35.8% < 39.5% → 강제 X등급 |
| 12:00 | 장중 중간점 | 113 | 11:54:00 [WARNING] 신뢰도 미달 35.7% < 62.0% → 강제 X등급 |

- 이 로그 생존구간: 08:40 ~ 12:26

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
| **오늘 20261019** | **12:26** | 로그 본문 |

- 델타 **-201분** (음수 = 기준선보다 이르게 끝났다)


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
### 증상 → 원인 → 결정 (이월 — 1-1 CREON 좀비 세션 충돌)
### 신규 1-5 — 수익률향상_누적대장 10-15 등록 누락 (소급 발견·해소)
### 신규 1-6 — 697차 구현 코드 당일 미커밋
### 신규 1-7 — 섀도우 TB(검증 캠페인) 재학습 강제 종료 (표본 1건, 확인 필요)
### 이월(변경 없음) — 1-1(CREON)·1-2(F-1 SessionStateDrop)·1-3(머지커밋 PC태그 확인필요)·1-4(피터2 수신오류, 697차 수정 배포·라이브 검증 대기)
## 2026-10-16 (MW0601 697차 후속 — 장후 자동조치: F-26)
## 2026-10-19 (MW0601 — 장전 점검)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
:34 완료, `session_state.json`에 당시 `p8_last_success_date`·`eod_retrain_ok_date` 둘 다 기록됨(과거 완료, 오늘자가 아님). (4) 오늘 `data/session_state.json`에는 두 키가 없음(F-1 `SessionStateDrop` 재발, 기존 지속 항목) — `[PreRetrain]` 08:55:09 로그가 "EOD 마커 파일 직접 확인(3일 전: 2026-10-16) → PreRetrain 스킵"으로 보완 경로를 탔음을 확인, 실질 피해 없음. (5) 주간(월요일 08:50~09:00) GBM 배치 재학습 — 오늘 로그에 `periodic` 트리거 발동 기록 없음. `main.py:8930`대 코드 확인 결과 "`_weekly_needed = should_retrain_weekly() and not self._eod_retrain_ok`" — 전일 EOD가 성공했으면 주간 재학습을 의도적으로 스킵하는 설계(주석: "daily_close()가 월요일 포함 매일 정규 파라미터로 재학습하므로 중복 불필요"). 전일 EOD 성공이 확인됐으므로 **오늘 0회가 정상**(483차 정정 사항과 같은 계열, 신규 이상점 아님). (6) `MAX_CONTRACTS` 1 vs 수집기 기대값 3 불일치 — 기존 F-24(수집기 기대값이 낡음), 신규 아님. (7) 피터2(X 기반 보조지표) 오프셋 보정값 08:58:09 기준 spread=0.31>0.30 "불안정" — 표본 13개로 313차 원칙상 확정 결론 보류, 신규 관측 O-p1로만 등록. (8) 캐너리(스케일러 노후 감시) z-경고 피처 08:55 12개→재적합→08:59 8개→09:59:09 10개(+2) 재상승 — O-p2로 등록, 장중 재확인 대상. (9) 옵션체인 재수집이 09:01:26(개장 1분 후)에 완료 — 과거 명시적 판정 기록을 찾지 못해 O-p3로만 등록, 확정 판정 보류. (10) 피터2(X 수집) 697-1 Chrome 확장 재로드 여부 — `logs/peter2_receiver_20261019.log`에 "RATE SearchTimeline ... rem=48/50 reset=08:59:17" 형태의 한도 헤더 값이 실제로 수신·기록되고 있음을 확인(697차 F-1~F-3 계측 기능이 동작 중인 정황). `receiver.py --check`는 이 코웍 샌드박스(리눅스 VM)에서 로컬호스트로 접속을 시도해 Connection refused를 반환했으나, 이는 **receiver가 실제로 도는 Windows 본체가 아니라 다른 네트워크 네임스페이스에서 접속을 시도했기 때문**이며 receiver 장애를 의미하지 않음 — 로그 증거(08:40:36 START, 09:01:38까지 연속 기록)로 대체 판정.

**결정**:
1. 신규 이상점 등록: 없음. 1-1(access violation)·1-2(메인스레드 블로킹) 모두 기존 TODO(606-4, O-p2) 계승, 관측일만 추가(함정① 방지).
2. 신규 관측 등록(O-p1·O-p2·O-p3) — 전부 "확인 필요" 등급, 장중 점검이 판정/판정보류/다음거래일이월 중 하나로 닫을 것.
3. 주간(월요일) GBM 재학습 0회는 정상 판정 — `main.py` 코드로 직접 확인(`_eod_retrain_ok` 조건), 483차 "재학습 0회가 정상인 날이 있다" 원칙의 실제 사례로 추가.
4. 697-1(Chrome 확장 재로드)은 로그 증거(rate limit 헤더 값 정상 수신)로 **유력 해소**로 처리하되, 코웍 환경에서 `receiver.py --check`를 직접 실행하는 것은 이 환경(리눅스 샌드박스)에서는 의미가 없다는 점을 다음 세션을 위해 기록한다 — 로컬호스트 접속 시도는 반드시 Windows 본체에서 해야 유효하다.
5. 이 계정의 앱 저장 스킬 사본이 저장소 정본보다 두 세대(538차분) 낡았음을 사용자 조치 3번으로 전달 — 이 세션은 스킬 저장 도구에 접근할 수 없어 직접 갱신하지 못함.

**Why**: 함정①(판정≠결정) 방지 — 606-4·O-p2·F-24를 전부 grep으로 먼저 확인한 뒤 신규가 아님을 검증했다. 계측 4원칙②(미제출≠일치) 준수 — 주간 재학습 트리거 로그가 없는 것을 곧바로 "정상"으로 쓰지 않고 `main.py` 코드의 조건문을 직접 읽어 근거를 확보한 뒤에만 정상으로 판정했다.

**How to apply**: 해당 없음(장전 점검 세션 — 관측·판정만, 코드 변경 없음).

**검증**: O-p1(피터2 오프셋 spread)·O-p2(캐너리 z경고 재상승)·O-p3(옵션체인 재수집 타이밍)은 다음 장중 점검이 재측정값으로 판정. 697-1은 사용자가 `chrome://extensions`에서 Mireuk Peter2 Collector 버전이 1.1.0인지 직접 확인하면 완전히 닫힌다.

⚠ **코드 변경 없음(장전 점검 세션 — 라이브 프로세스 실행 중, 08:57 KST경 예약 실행).** 라이브 DB 스캔 없음(수집기는 로그·설정·git 전용).

```

</details>

### dev_memory/NEXT_TODO.md — 1.7MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### MW0601 696차 — 장후 점검, 종합 완성본 (2026-10-15)
### 2026-10-15 (MW0601 696차 후속 — 장후 자동조치 결과)
### 2026-10-16 (MW0601 — 장전 점검)
### 2026-10-16 (MW0601 — 장중 점검)
### 2026-10-16 (MW0601 697차 — 피터2 X 수집 한도) — 장중 1-4 / G-2 후속
### 2026-10-16 (MW0601 — 장후 점검, 종합 완성본)
### 2026-10-16 (MW0601 697차 후속 — 장후 자동조치)
### 2026-10-19 (MW0601 — 장전 점검)
```

미완료 체크박스 **3235건** (끝에서 30건)
```
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
- [ ] **O-p1 (신규, 확인 필요)** 피터2 오프셋 보정값(A056B) 08:58:09 spread=0.31>0.30 "불안정"(표본 13개) — 09:30 전후 재측정에서 0.30 이하로 복귀하는지 장중 점검이 판정.
- [ ] **O-p2 (신규, 확인 필요)** 캐너리 z-경고 피처 수 08:59:09 10개로 재상승(08:55 임계접촉→재적합→08:59 8개 이후) — 09:10~09:15 재측정값이 8개 이하로 복귀하는지 장중 점검이 판정.
- [ ] **O-p3 (신규, 확인 필요)** 옵션체인 재수집이 09:01:26(개장 1분 후)에 완료 — 과거 타이밍 기준 판정 기록 부재. 다른 평일과 비교해 정상 범위인지 장중/다음 점검이 확인.
- [ ] (이월, 변경 없음) **606-4** 기동 access violation(1-1, main_dashboard.py:7434 _build) 원인 조사 착수 여부 — 10-19로 관측일 추가, 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **CREON-M1 (P0)** 장후 API 세션 정리 적용 시간대 — 여전히 사용자 결정 대기.
- [ ] (이월, 변경 없음) **F-24** `MAX_CONTRACTS` 수집기 기대값(3) 정정 — 실제 운용값 1은 의도값, 수집기 쪽 기대값만 낡음.
- [ ] (이월, 변경 없음) **F-1** `session_state.json` 마커 유실(SessionStateDrop) — 10-19 재발, EOD 마커 파일 보완 경로로 실질 피해 없음 재확인.
- [ ] **697-4 관련 메모** `python tools/peter2_live/receiver.py --check`는 코웍 리눅스 샌드박스에서 실행하면 Windows 본체가 아닌 다른 네트워크 네임스페이스로 접속을 시도해 항상 Connection refused가 난다 — 이 환경에서는 로그 파일 증거(START 시각·최근 RATE 줄)로 대체 판정…
- [ ] (참고) 이 계정 앱 저장 스킬 사본(rev 2026-08-26e)이 저장소 정본(rev 2026-09-07, 538차)보다 낡음 — 사용자가 해당 PC에서 재저장하면 해소. 이 세션은 스킬 저장 도구에 접근 불가.
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
5·L-6·L-7** CREON 런처 잔여 Fix — 기동·로그인 흐름 변경, 사용자 결정 후 별도 세션.
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

### `data/heartbeat_MW0601_20261019.json` — 242B · 10-19 12:26:15
```json
{
 "pid": 4572,
 "written_at": "2026-10-19T12:26:45",
 "beat_epoch": 1792380403.8195894,
 "beat_age_sec": 1.9,
 "watching": true,
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

### `data/peter2_live/trail_state_2026-10-19.json` — 336B · 10-19 11:37:43
```json
{
 "date": "2026-10-19",
 "trail": null,
 "ghosts": [
  {
   "pos_key": "2026-10-19 10:20:21|SHORT",
   "side": "S",
   "entry": 881.8,
   "stop": 888.28,
   "target": null,
   "start_hm": "11:37",
   "real_exit_px": 878.18,
   "real_pnl_pts": 3.62,
   "atr": 2.3429,
   "peak_px": 869.9,
   "done": false,
   "exit_px": null,
   "exit_hm": null,
   "exit_why": null,
   "last_px": null
  }
 ]
}
```

### `data/peter_feed/_raw/2026-10-19.jsonl` — 2.5KB · 10-19 10:53:39
```json
JSONL 13행 ⏎ 첫: {"id": "2111971403377561735", "dt": "2026-10-19T00:03:15.000Z", "text": "865 하방돌파시 매도. 손절가 869", "seen_at": "2026-10-19T09:04:20+09:00", "src": "live"} | {"id": "2111971777853468772", "dt": "2026-10-19T00:04:45.000Z", "text": "865 매도 체결.", "seen_at": "2026-10-19T09:05:40+09:00", "src": "live"} | {"id": "2111972308869071027", "dt": "2026-10-19T00:06:51.000Z", "text": "869 손절", "seen_at": "2026-10-19T09:07:00+09:00", "src": "live"} ⏎ 끝: {"id": "2111990564120055907", "dt": "2026-10-19T01:19:24.000Z", "text": "885손절.  883에 다시매도. 손절가 890", "seen_at": "2026-10-19T10:20:20+09:00", "src": "live"} | {"id": "2111989808084234362", "dt": "2026-10-19T01:16:23.000Z", "text": "손절가 885로 변경", "seen_at": "2026-10-19T10:20:20+09:00", "src": "live"} | {"id": "2111999040460366178", "dt": "2026-10-19T01:53:04.000Z", "text": "죽 치고 나갈려면 외인들이 상방으로 힘을 모아야 합니다.\n\n지금은 미야간선물 급등으로 인해 자동 세팅정도이지 상방으로 세팅하지는 않고 있습니다.\n\n만약 장중이나 오늘밤 현재 야간선물 나스닥 약 1프로에서 하락하게 되면\n\n오늘 하락이 그냥 내일로 미루어 지는겁니다.\n\n토요일 방송에서 말씀", "seen_at": "2026-10-19T10:53:39+09:00", "src": "live"}
```

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-19 11:41:03**

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
| `raw_candles` 당일 max ts | **12:25** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | 진행 중 — 수집 시각 12:26 라 절단선 `15:08` 미도래. 결손은 아래 「확정 대상」만 본다 |
| `raw_candles` 당일 행수 | 221 |
| `session_bars` 당일 행수 | 221 (기대 411) |

- 미도래 **163봉** (12:26~15:08) — 수집 시각 12:26 이후라 결손·영구결손에서 제외
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

### `docs/정기점검/매일점검` — 230개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261019-점검리포트.md` | 13.9KB | 10-19 09:07 |
| `docs/정기점검/매일점검/evidence_MW0601-20261019_pre.md` | 59.6KB | 10-19 08:59 |
| `docs/정기점검/매일점검/MW0602-20261017-긴급알림메일-종합검토.md` | 14.1KB | 10-17 11:49 |
| `docs/정기점검/매일점검/MW0602-20261015-청산거부113분-딥다이브.md` | 21.3KB | 10-17 10:31 |
| `docs/정기점검/매일점검/MW0601-20261016-점검리포트.md` | 75.9KB | 10-16 17:28 |
| `docs/정기점검/매일점검/MW0601-20261016-CREON기동-coStarter크래시-딥다이브.md` | 8.9KB | 10-16 16:40 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_post.md` | 97.3KB | 10-16 16:19 |
| `docs/정기점검/매일점검/evidence_MW0601-20261016_intra.md` | 80.4KB | 10-16 12:26 |

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
2. `logs/20261019_WARN.log`: **ConstOut** 2건(표본)
3. `logs/20261019_SYSTEM.log`: **ConstOut** 8건(표본)
4. `logs/20261019_SIGNAL.log`: **WeightCollapse** 8건(표본)
5. `logs/20261019_SIGNAL.log`: **ConstOut** 8건(표본)
6. `logs/20261019_LEARNING.log`: **축퇴** 8건(표본)
7. `logs/crash_fault.log`: `Windows fatal exception` **3건** (정규장 09:00 이후 0건) — 프로세스는 살아남았다. §9 「프로세스 종료 3축 대사」 아래 PID별 표를 볼 것 (641차 637-2)
8. 미커밋 변경 6건 (실질 3건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261019*.log` (Windows) / `grep 강제청산 logs/*20261019*.log`*