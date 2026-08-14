# 미륵이 증거 다이제스트 — 2026-08-12 / POST

- 생성 2026-08-12 19:28:01 KST · PC **MW0602** (`DESKTOP-MW0602`)
- 리포 `C:\Users\pc1\PycharmProjects\futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260812` · `2026-08-12` · `260812` · `0812`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **18개** 파일 · 18개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260812.txt` | 28B | 08-12 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260812.txt` | 134B | 08-12 15:47 |
| `launcher_{DATE}_084001_13478.log` | 1 | `logs/Mireuk_batch/launcher_20260812_084001_13478.log` | 1.6MB | 08-12 15:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260812.log` | 18.0KB | 08-12 15:47 |
| `retrain_intraday_{DATE}_140157.log` | 1 | `logs/retrain_intraday_20260812_140157.log` | 4.2KB | 08-12 14:02 |
| `strategy_report_{DATE}_154012.txt` | 1 | `data/daily_reports/strategy_report_20260812_154012.txt` | 1.9KB | 08-12 15:40 |
| `{DATE}_BACKFILL.log` | 1 | `logs/20260812_BACKFILL.log` | 0B | 08-12 16:53 |
| `{DATE}_DATA.log` | 1 | `logs/20260812_DATA.log` | 344.5KB | 08-12 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260812_DEBUG.log` | 223.3KB | 08-12 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260812_HEALTH.log` | 3.3KB | 08-12 14:58 |
| `{DATE}_HOGA.log` | 1 | `logs/20260812_HOGA.log` | 51.1MB | 08-12 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260812_LEARNING.log` | 353.4KB | 08-12 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260812_MICRO.log` | 1022.3KB | 08-12 15:39 |
| `{DATE}_PROBE.log` | 1 | `logs/20260812_PROBE.log` | 96.6KB | 08-12 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260812_SIGNAL.log` | 551.4KB | 08-12 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260812_SYSTEM.log` | 815.1KB | 08-12 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260812_TRADE.log` | 15.2KB | 08-12 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260812_WARN.log` | 73.8KB | 08-12 15:40 |

## 2. 코드·커밋 상태

- HEAD `84be75a` · 브랜치 `dev` · 미커밋 2건
```
?? MIREUK_DAILYCHECK_HANDOFF.md
?? docs/정기점검/매일점검/evidence_MW0602-20260812_post.md
```

**당일(2026-08-12) 커밋**
```
84be75a [MW0601] 459차: 일일 점검 스킬 MW0601 실측 정밀조정 — 태그 파싱 수정 + 거래일 요약 신설
5a57f4d [MW0602] 466차: 일일 점검 스킬 — 증거 수집기·국면별 체크리스트·차단 게이트 인벤토리
b552c8e [MW0602] 465차: DriftRetrain 교체 스코프 한정 + TP1 도달 계측 (P1~P6-b)
```

**최근 커밋 12건**
```
84be75a [MW0601] 459차: 일일 점검 스킬 MW0601 실측 정밀조정 — 태그 파싱 수정 + 거래일 요약 신설
5a57f4d [MW0602] 466차: 일일 점검 스킬 — 증거 수집기·국면별 체크리스트·차단 게이트 인벤토리
b552c8e [MW0602] 465차: DriftRetrain 교체 스코프 한정 + TP1 도달 계측 (P1~P6-b)
8c9589b [MW0602] 464차 P5-c: 3m·5m 유령 acc.txt 1회성 삭제 — 콜드스타트 유도 (판정 로직 무변경)
215184c [MW0602] 464차: P5 딥다이브 — BiasReset↔ConstOut 오인 차단 + 유령 기준 HOLD 계측
1223cfe [MW0602] 463차 후속: 미할당 속성 전수 감사 — 진짜 1건 발견, 오탐 6건 (배선 없음)
cd14f28 [MW0602] 463차: 미할당 속성 2건 배선(C3·C4) + daily_stats 리셋 순서(C5) — 진입 판단 무변경
c63b4ee [MW0602] 462차: 0811 점검 — 자기유발 차단 2건 + min_conf 계측 결함 (섀도·계측만, 라이브 무변경)
907f9c4 [MW0602] 461차: 보정기 학습표본 오염 발견 + P-A~P-D (섀도·계측만, 라이브 무변경)
7ce3a4b [MW0602] 459차: F1 승패 집계 단위(레그→포지션) + F2 SHS CORE 미측정 분리
470577e [MW0602] 460차: 공용 헬퍼 _spearman 동률 처리 버그 — 사본 2벌 정정 + 회귀테스트
e49a2af [MW0602] 458차 후속: [40-B]·[49] 채널 구현 + 기대값 지도 — 손익원천이전 3종
```

PC명 태그 규약: 최근 12건 모두 `[MW####]` 접두 확인

## 3. 설정 불변식 — 절대원칙·한시예외 (config/settings.py)

| 상수 | 현재값 | 기대값 | 판정 | 왜 보는가 |
|---|---|---|---|---|
| `CB_CONSEC_STOP_LIMIT` | `9999` | `9999` | 일치 | 모의투자 한정 예외(CB② 사실상 비활성). 실투 전환 전 2~3 복원 필수. 재검토 기한 2026-08-29 |
| `CB3_P4_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | 30m 퇴역으로 CB③-P4 상시 RESTRICTED 고착 → 차단만 비활성 (296·297차) |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | `False` | `False` | 일치 | PSI 계측 결함으로 차단만 비활성. 371차 분위수 재설계 후 라이브 관찰 중 |
| `MAX_CONTRACTS` | `3` | `3` | 일치 | 431차 10→3 인하. 실전 자본 확정 시 재산출 대상 |
| `SIZING_TARGET_CAPITAL_ENABLED` | `True` | `True` | 일치 | 모의투자 한정. False 전환은 단독 지시로 읽지 말 것 (손실 구간 복원 위험) |
| `SIZING_TARGET_CAPITAL_KRW` | `50_000_000` | — | 값 확인 | 현행 5천만원. 실전 전환 기준 ⑧의 남은 해제 조건 |
| `HURST_WINDOW_N` | `90` | `90` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `HURST_MAX_LAG` | `9` | `9` | 일치 | 317차 재보정. 26주 WFA마다 재검증 |
| `VALIDATION_REPORT_KEEP_WEEKS` | `4` | `4` | 일치 | 주간 리포트 FIFO 보관 |
| `CB_ACCURACY_MIN_30M` | `0.28` | `0.28` | 일치 | CB③ 임계. ⚠ CLAUDE.md 절대원칙 §2는 35%로 적혀 있다 — 코드가 0.35→0.28 완화됨. 문서 갱신 필요 |
| `CB_ACC_RESTRICTED_MIN` | `0.30` | `0.30` | 일치 | WATCH→RESTRICTED 경계. 30m 구조적 성능(0.3052)과 거의 같아 CB③-P4 비활성의 직접 원인 |
| `CB_ACCURACY_MIN_30M_STRICT` | `0.42` | `0.42` | 일치 | 과신 연속 시 강화 임계 (0.50→0.42 완화) |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | `False` | `False` | 일치 | ⚠ CLAUDE.md 한시예외 목록에 없는 네 번째 비활성 차단 게이트. 근거·복원조건 미기록 상태 |
| `LIMIT_PIN_ENTRY_BLOCK_ENABLED` | `True` | `True` | 일치 | 호가 상하한 핀 진입 차단 — 켜져 있어야 정상 |
| `HURST_SOFT_BLOCK_ENABLED` | `True` | `True` | 일치 | Hurst 소프트 차단(사이즈 0.5배). 316~318차 재보정 계열 |
| `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY` | `True` | `True` | 일치 | Degraded 상태 자동진입 차단 — 켜져 있어야 정상 |
| `CB_PIPE_PAUSE_MS` | `5_000` | `5_000` | 일치 | CB⑤ 실질 구현. `CB_API_LATENCY_LIMIT` 은 Kiwoom 레거시로 Cybos에서 미사용 |
| `ENTRY_HORIZON_B1` | `3.2` | `3.2` | 일치 | 1m/3m 경계 [374차 1.5→3.5, 387차 3.5→3.2] — 드리프트 항목 |
| `ENTRY_HORIZON_B2` | `4.4` | `4.4` | 일치 | 3m/5m 경계 [374차 2.5→4.0, 387차 4.0→4.4] — 드리프트 항목 |
| `CB_DAILY_HALT_FULL_BLOCK` | `3` | `3` | 일치 | HALT 3회 → 완전 관망 |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

### 차단 게이트 전수 인벤토리 — 29개 중 **7개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `TICKUI_TRACE_ENABLED` | False | 기능토글 |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | **미기록 ⚠** |
| `ATR_EXPIRY_CEILING_ENABLED` | True | — |
| `CHASE_FILTER_ENABLED` | True | — |
| `CONF_STUCK_BOOST_ENABLED` | True | — |
| `COUNTERTREND_CAP_ENABLED` | True | — |
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
| `MC_CONF_GAP_ALERT_ENABLED` | True | — |
| `MC_UNREACHABLE_ALERT_ENABLED` | True | — |
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | True | — |

> ⚠ **꺼져 있는데 근거가 기록되지 않은 차단 게이트 1개**: `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED`
> 의도한 것이면 `dev_memory/DECISION_LOG.md` 에 사유·복원조건을 적고 `config/dailycheck_targets.json` 의 `documented_disabled_flags` 에 추가하라. 의도한 것이 아니면 그 자체가 P0다.

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260812_HOGA.log` 51.1MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260812.txt`** — 28B · 08-12 15:40:12
```
2026-08-12T15:40:12.611832
```

**`data/daily_reports/strategy_report_20260812_154012.txt`** — 1.9KB · 08-12 15:40:12
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-08-12 15:40
========================================================
  버전    : v1.0  (57일차)
  판정    : UNDERPERFORM
  Live    : Sh=-0.19  MDD=129.2%  WR=83.3%  PF=2.50
  롤링20일: 누적 -108479원  Sh=-0.19  MDD=129.2%
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.110 (WATCHLIST)
  PSI/feat: cvd=0.244  vwap_position=0.110  ofi=0.003
--------------------------------------------------------
  권고    : 🔄 교체 후보 탐색
  사유    : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
--------------------------------------------------------
  최근20건 순EV: 평균 -18,001원  승률 50.0%  합계 -360,028원
  등급별 순EV(30일): A=+3,204원(119건,승60%)  C=+2,254원(58건,승69%)
  호라이즌별 순EV(30일): 1m=-8,801원(21건)  3m=-6,322원(96건)  5m=+21,729원(60건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 58분  5일평균 56분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 47.4pt(5일평균 36.2pt)  1분평균변동 0.77pt(5일평균 1.11pt)
--------------------------------------------------------
  진입 퍼널(2026-08-12, 총 370분):
    FLAT 216 → conf미달 91 → CoherenceGate 5 → 게이트차단 52 → 후보 6 → 진입 6
    게이트별: 체크리스트항목미달=25  콜드스타트/기타(σ미수집)=8  시가갭(OPEN_VOLATILE)=5  콜드스타트/기타(RegimeOverride)=4  쿨다운=4  콜드스타트/기타(조건부구간)=3  포지션보유중(평가생략)=3
========================================================
```

**`data/eod_retrain_done_20260812.txt`** — 134B · 08-12 15:47:31
```
completed: 2026-08-12 15:47:31
rows: 39122
cols: 105
horizons_replaced: 5/6
t_load_s: 21.2
t_retrain_s: 127.8
t_total_s: 149.2
```

_다이제스트 대상 8/13개 (중요도순). 제외: `20260812_MICRO.log`, `20260812_DATA.log`, `20260812_PROBE.log`, `launcher_20260812_084001_13478.log`, `20260812_DEBUG.log`_

### `logs/20260812_TRADE.log` — 15.2KB · 119행 · 최종 15:40:12

- 형식 평문 · 시각 인식 119행 · INFO=119

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 08:41:06 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-12 08:41:09 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-12 10:17:56 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=29,271,370) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShadow: 1.0→3계약]
2026-08-12 10:18:56 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=29,271,370) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-12 10:21:56 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=29,271,370) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-12 14:56:27 [INFO] TRADE: [Chejan] 상태=접수 주문번호=4571 code=A0568 방향=SHORT 체결=1 미체결=0
2026-08-12 14:56:27 [INFO] TRADE: [Chejan] 상태=체결 주문번호=4571 code=A0568 방향=SHORT 체결=1 미체결=0
2026-08-12 14:56:27 [INFO] TRADE: [Position] 체결청산 LONG @ 1031.02 | PnL=+0.14pt (+5,454원) | 하드스톱(틱)
2026-08-12 14:56:27 [INFO] TRADE: [청산 완료] PnL=+0.14pt (+5,454원)
2026-08-12 15:40:12 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**채널** — `TRADE`×119

**컴포넌트 상위 15** — `Chejan`×33, `Position`×25, `주문요청`×15, `Sizer`×12, `진입체크`×6, `체결진입`×6, `청산 완료`×6, `TickTP1`×5, `TickStop-S0C`×3, `체결진입보정`×3, `ProfitGuard`×2, `TP1 부분청산`×2, `손절1차 조기축소`×1

### `logs/20260812_WARN.log` — 73.8KB · 309행 · 최종 15:40:12

- 형식 평문 · 시각 인식 302행 · WARNING=302, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-12 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-12 08:41:11 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 156ms account=777019873
2026-08-12 08:41:13 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-12 08:41:13 [WARNING] SYSTEM: [LiveDBG] _apply 시작 (4단계 체인)
  …
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +218135원
════════════════════════════════════════════════════
```

</details>

**WARNING — 태그 31종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 74 | 08:41:11 | 14:56:29 | request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 33 | 10:38:56 | 14:56:27 | account='777019873' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0568' | fill_price=0.0 | fill_qty=1 | gubun='0' | order_no='1720' | pending='ENTRY:LONG qty=1 filled=0 order_no=? reason=진입 req_at=10:38:56.450' | positio… |
| `ChejanMatch` | 33 | 10:38:56 | 14:56:27 | order_no='1720' | pending='ENTRY:LONG qty=1 filled=0 order_no=1720 reason=진입 req_at=10:38:56.450' | pending_matched=True |
| `PendingOrder` | 30 | 10:38:56 | 14:56:28 | set {'kind': 'ENTRY', 'direction': 'LONG', 'raw_direction': 'LONG', 'reverse_entry_enabled': False, 'qty': 1, 'price_hint': 1020.24, 'reason': '진입', 'hint_source': '', 'atr': 1.6143, 'grade': 'C', 'stage': None, 'order_no': '', 'filled_qty… |
| `ScalerRefresh` | 17 | 09:08:56 | 15:04:57 | 5분 누적 수익률 -0.296% (임계 ±0.248%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `Health` | 12 | 09:23:56 | 14:57:58 | level=WARNING degraded=OFF | latency=187ms | quality=1.00 | cache_age=182s | exceptions_10m=0 |
| `ExitCooldown` | 12 | 10:42:56 | 14:56:27 | TP2(전량) 후 2분 재진입 금지 (until 10:44:56) |
| `EntryFillFlow` | 9 | 10:38:56 | 14:36:57 | actual_side='LONG' | after='LONG 1계약 @ 1020.44' | applied_side='LONG' | before='LONG 1계약 @ 1020.24' | fill_no='' | fill_price=1020.44 | fill_qty=1 | order_no='1720' | pending='ENTRY:LONG qty=1 filled=1 order_no=1720 reason=진입 req_at=10:38:… |
| `CB③-P4` | 8 | 13:22:56 | 13:45:56 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `EntryAttempt` | 6 | 10:38:56 | 14:36:57 | atr=1.6143 | block_new_entries=False | broker_sync_reason='blank/no holdings response interpreted as flat' | broker_sync_verified=True | direction='LONG' | exit_cooldown_active=False | exit_cooldown_remain=0 | grade='C' | pending='NONE' | … |
| `EntrySendOrderResult` | 6 | 10:38:56 | 14:36:57 | code='A0568' | direction='LONG' | pending='ENTRY:LONG qty=1 filled=0 order_no=? reason=진입 req_at=10:38:56.450' | position='FLAT' | quantity=1 | raw_direction='LONG' | ret=0 | reverse_entry_enabled=False |
| `FixB` | 6 | 10:38:56 | 14:36:57 | 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True |

**채널** — `SYSTEM`×290, `HEALTH`×12

**컴포넌트 상위 15** — `LiveDBG`×74, `ChejanFlow`×33, `ChejanMatch`×33, `PendingOrder`×30, `ScalerRefresh`×17, `Health`×12, `ExitCooldown`×12, `EntryFillFlow`×9, `CB③-P4`×8, `-`×7, `EntryAttempt`×6, `EntrySendOrderResult`×6, `FixB`×6, `EntryPendingCreated`×6, `PartialExitAttempt`×6

### `logs/20260812_SYSTEM.log` — 815.1KB · 5833행 · 최종 15:40:27

- 형식 평문 · 시각 인식 5810행 · INFO=5810, PLAIN=23

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 08:40:40 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=5816 | 행감지=30s all_threads=True
2026-08-12 08:40:52 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-12 08:40:52 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-12 08:40:52 [INFO] SYSTEM: 미륵이 초기화
2026-08-12 08:40:52 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-11) 종가 버퍼 로드: 385봉
  …
2026-08-12 15:40:12 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\pc1\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-08-12 15:40:12 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-12 15:40:27 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-12 15:40:27 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-12 15:40:27 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\pc1\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×5810

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1210, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×406, `S6Detail`×370, `PipePerf`×370, `System`×98, `MicroRegime`×87, `BalanceUI`×66, `CybosEvent`×66, `OptionChain`×52, `CybosDailyPnl`×48, `BalanceRefresh`×48

### `logs/20260812_SIGNAL.log` — 551.4KB · 4893행 · 최종 15:40:12

- 형식 평문 · 시각 인식 4893행 · WARNING=1960, INFO=2933

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.414
2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.406
2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.402
2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.410
  …
2026-08-12 15:09:57 [INFO] SIGNAL: 앙상블: dir=+0 conf=39.3% grade=X micro=횡보장
2026-08-12 15:09:57 [INFO] SIGNAL: [ZeroDiag] 진입X 원인: FLAT수렴 / conf미달(0.393<mc0.970)
2026-08-12 15:10:07 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-12 15:40:12 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-12 15:40:12 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-12 age=32m extreme=504 refresh=38 grade_x=113 cb3=0
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1386 | 09:00:56 | 15:04:57 | 1m 'macro_vix' scale=0.0086 → floor=0.10 적용 (z-score 폭발 방지) |
| `Model` | 180 | 09:00:56 | 15:07:56 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `ScalerMonitor` | 168 | 09:00:56 | 15:03:57 | ts=09:00 horizon=1m age=2m max_z=-13.32(prev_day_same_hour_ret) extreme=2 |
| `Checklist` | 126 | 09:05:56 | 15:03:57 | CORE VWAP ✗ → 강제 X등급 (pass_count=9, group=short) | VWAP pos=+0.069 need <0 (SHORT) bull_exh=0.00 |
| `WeightCollapse` | 76 | 09:07:56 | 15:07:57 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ScalerRefresh` | 24 | 08:45:11 | 08:45:11 | 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |

**채널** — `SIGNAL`×4893

**컴포넌트 상위 15** — `ScalerFloor`×1452, `SIGNAL`×740, `MetaGate`×392, `Ensemble`×370, `FQAdj`×368, `ZeroDiag`×327, `Model`×192, `ScalerMonitor`×169, `Checklist`×168, `ATR-Horizon`×138, `차단`×88, `MicroRegime`×87, `InstabilityGate`×82, `WeightCollapse`×76, `ScalerRefresh`×68

### `logs/20260812_LEARNING.log` — 353.4KB · 3145행 · 최종 15:40:12

- 형식 평문 · 시각 인식 3145행 · WARNING=179, INFO=2966

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 08:40:53 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-12 08:40:53 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00021 auc=0.405 out_max=0.2876) vs clean(n=80 span=0.00021 auc=0.405 out_max=0.2876 base=0.2875) 오염행=0건 축퇴판정 live=True clean=True
2026-08-12 08:40:53 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.405 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
2026-08-12 08:40:53 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00068 auc=0.593 out_max=0.3254) vs clean(n=80 span=0.00068 auc=0.593 out_max=0.3254 base=0.3250) 오염행=0건 축퇴판정 live=False clean=False
2026-08-12 08:40:53 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3254 < conf_floor=0.3300 (span=0.00068 auc=0.593 out_max=0.3254, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
  …
2026-08-12 15:40:12 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-12 15:40:12 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-12 15:40:12 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-12 15:40:12 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-12 15:40:12 [INFO] LEARNING: [Sigma] EOD sigma_20=0.07518% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 179 | 08:40:53 | 14:12:57 | 축퇴 감지 — span=0.00021 auc=0.405 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과 |

**채널** — `LEARNING`×3145

**컴포넌트 상위 15** — `LEARNING`×1195, `Calibration`×582, `SGD`×370, `sigma`×357, `Bias⚠`×264, `Bias`×140, `MetaConf`×77, `OnlineLearner`×66, `ScalerWarmup`×44, `BiasReset`×22, `SHAP`×11, `ExtremityCorrector`×5, `Consolidator`×3, `RF`×2, `DriftAdjuster`×2

### `logs/20260812_HEALTH.log` — 3.3KB · 25행 · 최종 14:58:57

- 형식 평문 · 시각 인식 25행 · WARNING=12, INFO=13

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 09:23:56 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=187ms | quality=1.00 | cache_age=182s | exceptions_10m=0
2026-08-12 09:24:56 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=182ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-12 09:29:56 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 184ms (표본 20분)
2026-08-12 10:06:56 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=185ms | quality=1.00 | cache_age=183s | exceptions_10m=0
2026-08-12 10:07:56 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=177ms | quality=1.00 | cache_age=59s | exceptions_10m=0
  …
2026-08-12 14:09:57 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=512ms | quality=1.00 | cache_age=57s | exceptions_10m=0
2026-08-12 14:54:57 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=415ms | quality=1.00 | cache_age=183s | exceptions_10m=1
2026-08-12 14:55:57 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=422ms | quality=1.00 | cache_age=60s | exceptions_10m=1
2026-08-12 14:57:58 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=536ms | quality=1.00 | cache_age=181s | exceptions_10m=1
2026-08-12 14:58:57 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=444ms | quality=1.00 | cache_age=56s | exceptions_10m=1
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 12 | 09:23:56 | 14:57:58 | level=WARNING degraded=OFF | latency=187ms | quality=1.00 | cache_age=182s | exceptions_10m=0 |

**채널** — `HEALTH`×25

**컴포넌트 상위 15** — `Health`×24, `HealthTrend`×1

### `logs/retrain_eod_20260812.log` — 18.0KB · 125행 · 최종 15:47:31

- 형식 평문 · 시각 인식 125행 · WARNING=8, INFO=117

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 15:45:01,797 [INFO] EOD_RETRAIN: =======================================================
2026-08-12 15:45:01,797 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-12 15:45:01,798 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-12 15:45:01,798 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-12 15:45:01,798 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-12 15:47:31,458 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0371 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-12 15:47:31,459 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0896 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-12 15:47:31,461 [INFO] SIGNAL: [ScalerRefresh] ts=15:47 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.03s
2026-08-12 15:47:31,477 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.03s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-12 15:47:31,485 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:45:29 | 15:46:32 | 1m ⚠ 이 격차는 성능차가 아니다 — 현행이 홀드아웃을 이미 학습했다. 판정·인용 금지 (무효 (구모델 pkl mtime=2026-08-12 14:02) | 현행이 홀드아웃 학습함 — train_end=2026-08-12 13:31 >= holdout_start=2026-08-05 12:11 (source=intraday)) |
| `Retrain` | 2 | 15:46:00 | 15:46:00 | 10m 교체 보류(EOD 모델가드) — acc 하락 0.0524 > 허용 0.0300 (new=0.4290 old=0.4814) — 참고용 저장, 구모델 유지 |

**채널** — `LEARNING`×56, `SIGNAL`×43, `EOD_RETRAIN`×20, `FEAT_REG`×4

**컴포넌트 상위 15** — `ScalerFloor`×36, `Retrain`×21, `EOD_RETRAIN`×14, `GuardFair`×12, `RF`×9, `Retrain-Timing`×6, `GuardShadow`×6, `Model`×6, `FeatureReg`×4, `RegimeFingerprint`×3, `WaitDC`×2, `P8`×2, `CUSUM`×1, `EOD`×1, `ScalerWarmup`×1

### `logs/retrain_intraday_20260812_140157.log` — 4.2KB · 37행 · 최종 14:02:21

- 형식 평문 · 시각 인식 37행 · INFO=37

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-12 14:01:57,113 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-12 14:01:57,113 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-12 14:01:57,113 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-12 14:01:57,113 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True horizons=ALL result_path=C:\Users\pc1\PycharmProjects\futures\data\_gbm_result_138ab7c4.json
2026-08-12 14:01:59,321 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-12 14:02:21,201 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=0.56s | old_acc=0.4920)
2026-08-12 14:02:21,251 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-12 14:02:21,251 [INFO] LEARNING: [Retrain] 완료 | 21.9초 | 성공=6/6 호라이즌
2026-08-12 14:02:21,251 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 24.1s 데이터=4800행
2026-08-12 14:02:21,253 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\pc1\PycharmProjects\futures\data\_gbm_result_138ab7c4.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×4

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `Retrain-Timing`×6, `FeatureReg`×4, `CUSUM`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

### 전략 상태 경보 — 그날의 판정

```
[전략 상태 경보] v1.0
판정  : UNDERPERFORM
드리프트: CLEAR (Lv.0)
액션  : 🔄 교체 후보 탐색
사유  : 기대값 하회 — param_optimizer + WFA 즉시 예약. Shadow 전략 2주 가동 후 Hot-Swap 검토.
오늘 PnL: +218135원
════════════════════════════════════════════════════
```

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 6 |
| 진입 등록(`[Position] 진입`) | 6 |
| 체결(`[체결진입]`) | 6 |
| 청산(`체결청산`) | 6 |
| 차단(`[차단]`) | 88 |
| 사이저 호출(`[Sizer]`) | 12 |

### 청산 6건 · 승 5 (83%) · 합계 +4.55pt (+218,258원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 10:42:56 | LONG | +3.12 | +154,469 | TP2(전량) |
| 11:22:29 | LONG | +0.30 | +13,458 | 하드스톱(틱) |
| 11:25:57 | LONG | +1.66 | +81,459 | 하드스톱 |
| 11:30:57 | LONG | +1.31 | +63,954 | 하드스톱 |
| 14:27:54 | SHORT | -1.98 | -100,536 | 하드스톱(틱) |
| 14:56:27 | LONG | +0.14 | +5,454 | 하드스톱(틱) |

**청산 사유 분포** — `하드스톱(틱)`×3, `하드스톱`×2, `TP2(전량)`×1

> 하드스톱·손절 계열 5/6건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 6건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:38:56 | LONG | 1 | 1020.24 | 3m | neutral |
| 11:20:56 | LONG | 1 | 1027.7 | 3m | mean-revert |
| 11:24:56 | LONG | 2 | 1027.32 | 3m | mean-revert |
| 11:29:56 | LONG | 2 | 1030.94 | 3m | mean-revert |
| 14:24:57 | SHORT | 2 | 1023.94 | 3m | mean-revert |
| 14:36:57 | LONG | 1 | 1030.8 | 3m | trend |

계약수 분포 — 1계약×3, 2계약×3

등급 분포 — `A급(원시C)`×2, `C급`×4

**진입한 건들의 체크리스트 미통과 항목** — `cvd`×5, `prev`×5, `ofi`×4, `chas`×4

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×1, **2계약**×4, **3계약**×7

실제 진입 계약수 — **1계약**×3, **2계약**×3

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×12

### 차단 사유 88건 · 37종

| 건수 | 사유 |
|---|---|
| 42 | 등급X — 미통과 항목: 2_confidence |
| 6 | 등급X — 미통과 항목: 3_vwap, 10_chase |
| 3 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 7_prev_bar |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 7_prev_bar, 10_chase |
| 2 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.4pt > ATR×5.0=9.8pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 11.0pt > ATR×5.0=9.9pt (시가=1000.60 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 10_chase |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 8.4pt > ATR×5.0=7.8pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.7pt > ATR×5.0=8.4pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 12.0pt > ATR×5.0=8.9pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.2pt > ATR×5.0=8.6pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.6pt > ATR×5.0=8.6pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.4pt > ATR×5.0=8.1pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.7pt > ATR×5.0=8.1pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.4pt > ATR×5.0=8.2pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 14.5pt > ATR×5.0=7.9pt (시가=1000.60 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 13.0pt > ATR×5.0=7.5pt (시가=1000.60 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×42, `3_vwap`×22, `10_chase`×11, `4_cvd`×11, `5_ofi`×10, `7_prev_bar`×9, `6_foreign`×5

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 4건

- `일간 리셋 완료` ×2
- `연속 손절 1회` ×1
- `연속 손절 2회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 1건 · 최대 2203ms · 5초 초과 0건

상위 — 2203ms

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260812_WARN.log`
```
--- [CB] ×2(표본)
14:25:08 2026-08-12 14:25:08 [WARNING] SYSTEM: [CB] 연속 손절 1회
14:27:54 2026-08-12 14:27:54 [WARNING] SYSTEM: [CB] 연속 손절 2회
--- [ExitCooldown] ×8(표본)
10:42:56 2026-08-12 10:42:56 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 10:44:56)
10:42:56 2026-08-12 10:42:56 [WARNING] SYSTEM: [ExitCooldown] TP2(전량) 후 2분 재진입 금지 (until 10:44:56)
11:22:29 2026-08-12 11:22:29 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:24:29)
11:22:29 2026-08-12 11:22:29 [WARNING] SYSTEM: [ExitCooldown] 하드스톱(틱) 후 2분 재진입 금지 (until 11:24:29)
--- 메인 스레드 블로킹 ×1(표본)
08:41:13 2026-08-12 08:41:13 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2203ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
--- 전략 상태 경보 ×1(표본)
??:??:?? [전략 상태 경보] v1.0
--- 판정  : ×1(표본)
??:??:?? 판정  : UNDERPERFORM
```

### `logs/20260812_SYSTEM.log`
```
--- [CB] ×2(표본)
15:40:12 2026-08-12 15:40:12 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:12 2026-08-12 15:40:12 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [Shutdown] ×2(표본)
15:40:12 2026-08-12 15:40:12 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\pc1\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:27 2026-08-12 15:40:27 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\pc1\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:12 2026-08-12 15:40:12 [INFO] SYSTEM: [Notify] ℹ️ [15:40:12] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:12 2026-08-12 15:40:12 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:27 2026-08-12 15:40:27 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260812_SIGNAL.log`
```
--- ConfFloorGuard ×1(표본)
09:05:56 2026-08-12 09:05:56 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3975 ≥ 필요 0.3840
--- WeightCollapse ×8(표본)
09:07:56 2026-08-12 09:07:56 [INFO] SIGNAL: [Ensemble] dir=+0 conf=39.7% grade=X regime=NEUTRAL [WeightCollapse]
09:10:56 2026-08-12 09:10:56 [INFO] SIGNAL: [Ensemble] dir=+0 conf=40.3% grade=X regime=NEUTRAL [WeightCollapse]
09:13:56 2026-08-12 09:13:56 [INFO] SIGNAL: [Ensemble] dir=+0 conf=40.3% grade=X regime=NEUTRAL [WeightCollapse]
09:16:56 2026-08-12 09:16:56 [INFO] SIGNAL: [Ensemble] dir=+0 conf=39.8% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:39 2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.431
08:40:39 2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.414
08:40:39 2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.406
08:40:39 2026-08-12 08:40:39 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.402
--- 안전망 ×8(표본)
09:07:56 2026-08-12 09:07:56 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:56 2026-08-12 09:10:56 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:13:56 2026-08-12 09:13:56 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:56 2026-08-12 09:16:56 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260812_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:40:53 2026-08-12 08:40:53 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00021 auc=0.405 out_max=0.2876) vs clean(n=80 span=0.00021 auc=0.405 out_max=0.2876 base=0.2875) 오염행=0건 축퇴판정 live=True clean=True
08:40:53 2026-08-12 08:40:53 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00021 auc=0.405 out_max=0.2876 (기준 auc<0.53 and span<0.020, 기저율=0.2875 n=80) → 보정 미적용, raw 통과
08:40:53 2026-08-12 08:40:53 [INFO] LEARNING: [Calibration][CleanShadow] live(span=0.00068 auc=0.593 out_max=0.3254) vs clean(n=80 span=0.00068 auc=0.593 out_max=0.3254 base=0.3250) 오염행=0건 축퇴판정 live=False clean=False
08:40:53 2026-08-12 08:40:53 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.3254 < conf_floor=0.3300 (span=0.00068 auc=0.593 out_max=0.3254, 기저율=0.3250 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260812_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:06 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:12 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260812_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 5 | 08:41:11 [WARNING] request_futures_balance 호출 account=777019873 | caller=es_balance(account_no) |  File "C:\Users\pc1\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 2 | 08:55:12 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 08:55:12 [WARNING] scaler 노후=0h  z경고피처=13개 (EarlyWarmup 완료 — 임계 12개)  ⚠ z경고 폭증 |
| 10:00 | 장중 초반 | 1 | 10:06:56 [WARNING] level=WARNING degraded=OFF | latency=185ms | quality=1.00 | cache_age=183s | exceptions_10m=0 |
| 14:00 | 장중 후반 · 장중 재학습 | 2 | 14:01:56 [WARNING] acc5m=6.7%(n=15) < 15% → 조기 트리거 (1335분 경과) → 장중 경량 재학습 트리거 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 1 | 15:04:57 [WARNING] 5분 누적 수익률 +0.212% (임계 ±0.194%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:12 [WARNING] EOD 재학습 마커 없음 — retrain_eod.py 미실행 또는 실패 (내일 PreRetrain에서 보완 재학습 예약됨) |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260812_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 85 | 08:40:40 [INFO] 활성화 | file=logs\crash_fault.log PID=5816 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 123 | 08:49:15 [INFO] alive ticks=647 code=A0568 close=998.46 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 182 | 08:54:31 [INFO] alive ticks=1273 code=A0568 close=1000.50 |
| 10:00 | 장중 초반 | 182 | 09:54:02 [INFO] alive ticks=27037 code=A0568 close=1007.44 |
| 12:00 | 장중 중간점 | 176 | 11:54:05 [INFO] alive ticks=61213 code=A0568 close=1036.56 |
| 14:00 | 장중 후반 · 장중 재학습 | 177 | 13:54:11 [INFO] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+1170,foreign:+3005,institution:-4682} |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 168 | 15:04:11 [INFO] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+1502,foreign:+2512,institution:-4616} |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 137 | 15:12:11 [INFO] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+1490,foreign:+2330,institution:-4472} |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 34 | 15:34:11 [INFO] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+1331,foreign:+1217,institution:-3171} |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260812_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 68 | 08:45:11 [WARNING] 1m CORE 'above_vwap' raw_std≈0(0.0000) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 152 | 09:00:56 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 233 | 09:00:56 [WARNING] 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 10:00 | 장중 초반 | 92 | 09:54:56 [WARNING] 신뢰도 미달 34.2% < 38.4% → 강제 X등급 |
| 12:00 | 장중 중간점 | 148 | 11:57:56 [WARNING] 신뢰도 미달 39.9% < 44.0% → 강제 X등급 |
| 14:00 | 장중 후반 · 장중 재학습 | 150 | 13:56:58 [WARNING] 신뢰도 미달 31.6% < 45.2% → 강제 X등급 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 91 | 15:04:57 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 2 | 15:40:12 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-07-20 (362차) — 청산 P1~P6 문서-코드 불일치 정리 중 숨은 AttributeError 버그 발견·수정 + exit_manager.py 제거
## 2026-07-20 (362차 후속) — Hurst 재검증(317차 Phase 5)을 CLAUDE.md "주기적 재검증" 등록부에 편입
## 2026-07-21 (363차 — 0721 정기점검 딥다이브: 손절계단화(Loss Tier1) 사각지대 2건 해소)
### [설계결정] 오늘 실손실 2건 다 Loss Tier1(360차)이 못 뜬 원인 규명 + tick-level 확장(라이브) + qty=1 대체안 섀도 계측
## 2026-07-21 (363차 후속 — 0721 딥다이브 제안3·4를 360/361차 계열 캠페인에 편입)
### [설계결정] quantile 기대엣지 필터·qty=1 TP1 이후 트레일 폭을 별도 신설 대신 기존 캠페인에 컬럼/자매채널로 편입
## 2026-07-21 (364차 — 0721 정기점검 딥다이브: tp2_hold_shadow 표본 0건 구조적 원인 규명 + 363차 커밋 라이브 미반영 확인)
### [발견] tp2_hold_shadow(361차)가 구현 이후 단 한 건도 기록되지 않음 — EntryGate×MetaGate 사이즈 감쇠 중첩으로 진입수량이 항상 1에 수렴
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
밋 라이브 미반영 확인)

### [발견] tp2_hold_shadow(361차)가 구현 이후 단 한 건도 기록되지 않음 — EntryGate×MetaGate 사이즈 감쇠 중첩으로 진입수량이 항상 1에 수렴

**File**: `main.py:6724-6744`(진입수량 결정부), `main.py:10579`(tp2_hold_shadow 기록
조건)
**증상**: 0721 정기점검 딥다이브 중 오늘 실거래 10건(6승4패, +1,019,004원)을
조사하다, Sizer가 매 사이클 2~5계약을 제안(`[Sizer] ... → N계약` 로그)했음에도
실제 체결은 10건 전부 예외 없이 1계약이었음을 발견. `data/db/trades.db`를 직접
조회한 결과 `tp2_hold_shadow`(361차, 0720 구현, "TP3 도달 0건" 원인규명용
counterfactual 채널) 누적 총 건수가 **0건**(구현일 이후 하루도 빠짐없이 0) —
최소표본(15건) 판정이 구조적으로 영원히 불가능한 상태로 방치돼 있었음.
**원인**: `main.py:10579`의 `if stage == 2 and is_full_close and total_qty == 2:`가
`tp2_hold_shadow` 기록 조건인데, 실제 진입 수량이 항상 1로 귀결돼 이 조건이 한
번도 참이 된 적이 없음. 수량이 항상 1로 귀결되는 이유를 추적한 결과, 대시보드
"최대허용수량"(기본값 10, `dashboard/main_dashboard.py:4431`)이 원인이 아니라,
`main.py:6724` 이하에서 Sizer 산출값(`_qty_display`)에 `[EntryGate] 사이즈 축소
×0.6`(GBM 재학습 임박 시)과 `[MetaGate] action=reduce size_mult=0.5~0.75`(메타
확신도 낮을 때)가 **곱으로 중첩** 적용되기 때문임을 확인(예: Sizer 2계약 × 0.6 ×
0.75 = 0.9 → `max(1, round(...))`로 바닥값 1에 수렴). 오늘 10건 전부 이 두 감쇠 중
최소 하나가 동시에 걸려 있었음(TRADE/SIGNAL 로그 대조 확인).
**Why**: 361차가 tp2_hold_shadow를 설계할 때 "qty=2 포지션이 TP2에서 잔량을 100%
종료하는 순간"을 관측 대상으로 삼았는데, 그 전제(qty=2 진입이 종종 발생함)가
EntryGate·MetaGate의 독립적인 위험 감쇠가 곱으로 겹치는 현재 운영 조건에서는
성립하지 않음 — 각 게이트는 개별적으로는 합리적인 안전장치이지만, 상호작용으로
"항상 qty=1"이라는 의도치 않은 부작용을 냄. 363차가 그 사이 신설한
tp1_trail_shadow/loss_tier1_qty1_shadow는 (의도했든 우연이든) qty=1을 정확히
겨냥하고 있어 현재 실제 운영 상태와 합치함.
**결정**: 코드 변경 없음(이번 세션은 진단·보고 전용, §9 사전등록 원칙에 따라
즉시 자동 수정하지 않음). 조치 방향은 NEXT_TODO 364차 항목으로 등록 — 주간회의에서
(a) EntryGate×MetaGate 중첩 감쇠를 완화해 qty=2 진입을 실제로 발생시킬지, 또는
(b) qty=1 고정을 현재의 정상 운영 상태로 받아들이고 tp2_hold_shadow를 qty=1 전용
로직으로 재설계할지 결정.
**부수 발견**: 같은 날 앞서 커밋된 363차/363차 후속(`2239db4`/`0cde21f` —
loss_tier1_qty1_shadow·tp1_trail_shadow 신규 테이블+quantile 컬럼)이 오늘 실제
라이브 프로세스에는 반영되지 않은 채로 하루가 지나갔음을 `data/db/trades.db`에
해당 테이블이 없는 것으로 확인 — 오늘 qty=1 손실 4건(아래 참고) 전부가 이 신규
섀도 계측의 관측 대상이었는데 하나도 기록되지 못한 기회비용 발생. 다음 재기동 시
최신 커밋 반영 여부 확인 필요(NEXT_TODO 364차 항목).
**참고(비공식 손계산, 확정 아님)**: 오늘 손실 4건 중 TP1 미도달 3건(#2 -4.2pt, #5
-4.0pt, #9 -3.2pt)에 대해 entry~stop 50%(tier1) 조기청산을 가정하면 각각 약
-2.4pt/-1.6pt/-1.65pt로 손실 규모가 대략 절반 수준으로 줄었을 개연성 — n=3의
손계산이라 확정적 결론은 아니며, 공식 판정은 loss_tier1_qty1_shadow 표본 축적 후
금요일 캠페인 리포트로.
**검증**: `data/db/trades.db` 직접 쿼리로 tp2_hold_shadow 누적 0건 확인,
predictions.db 사후검증(5m 방향성 정확도 44.4%, 체크리스트+게이트 통과 후 실현
승률 60%)으로 필터링 레이어의 실효성 별도 확인. 코드 변경 없어
py_compile/라이브 검증 해당 없음.
**관련**: 361차(tp2_hold_shadow 원 구현), 363차/363차 후속(qty=1 전용 섀도 채널),
`docs/정기점검/매일점검/0721.txt`(이 딥다이브 리포트 원문).

```

</details>

### dev_memory/NEXT_TODO.md — 836.7KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### DONE
### NEXT
## 2026-05-22 (82차) — 미시 레짐 워밍업 UI
### 처리 완료
### 다음 작업
## 2026-06-25 (243차 이후)
### DONE
### NEXT (Stage 2 ~ Phase 3)
```

미완료 체크박스 **1149건** (끝에서 30건)
```
- [ ] **pred_select 5-12초 병목 (S1)** — verified=6 전환 시점(30m 첫 채점 후) predictions DB 쿼리 풀스캔 의심. `ts`/`horizon` 컬럼 인덱스 추가 검토
- [ ] **30m FL편향 87%** — 09:50~10:07 구간 FL편향 심각. BiasReset 발동 여부 확인
- [ ] **`[Model] 정합성 오류` 로그 재발 없음** — 재시작·재학습 후 허위 불일치 미발생 확인
- [ ] **`resync_mismatch` 사유 비계획 GBM 재학습 없음** — `[GBM] 수동 재학습 시작 | resync_mismatch` 로그 미발생 확인
- [ ] **오늘(06-16) 09:01~13:03 구간 진입판단 재검토** — 버그로 인해 GBM이 일시적으로 FLAT 디폴트(33.3%)였을 가능성 있는 구간. SGD 블렌딩 비중이 낮았던 분봉이 있었는지 LEARNING.log 확인
- [ ] **EOD 재학습 실패해도 P8/WAL 계속 진행 확인** — 다음 EOD에서 (정상이든 또 실패하든) `[P8] EOD 스케일러 재적합 완료`·`[WAL] 체크포인트 완료` 로그가 항상 출력되는지 확인
- [ ] **time_zone 크래시 미재발** — `[ERR-FATAL] minute_pipeline: local variable 'time_zone' referenced before assignment` 재발 없음 확인 (WARN.log)
- [ ] **진입단계 추적 카드 신규 컬럼 표시** — "차단사유" 컬럼, "8.STEP7 차단/9.진입후보(최종)/10.진입완료" 단계, 게이트 상세 툴팁이 신뢰도게이트 탭에서 정상 렌더링되는지 확인
- [ ] **Hurst 차단 표시 확인** — Hurst<0.45로 막힌 분봉이 "8. STEP7 차단" + "Hurst X.XXX < 0.45" 텍스트로 정확히 표시되는지 확인
- [ ] **차단사유 파일 로깅 확인** — `SIGNAL.log`/`SYSTEM.log` 등에서 `[차단] ...` 메시지가 grep으로 확인되는지 점검 (기존엔 대시보드 버퍼 전용)
- [ ] **`ensemble_decisions` 마이그레이션 확인** — 재시작 후 `entry_gate_json` 등 6컬럼이 `ALTER TABLE`로 정상 추가됐는지 (`PRAGMA table_info`) 확인
- [ ] **PipePerf 라벨 정상화** — `S1=Xms`가 STEP1(검증) 본문을 가리키는지 확인 (종전 S2로 오표기되던 것)
- [ ] **`[Buffer-Timing]` 로그 확인** — 정체 재발 시 raw_fetch/pred_select/pred_update/pred_insert 중 실제 병목 구간 확정 (179차 "S2 지연 원인" TODO를 이 계측으로 대체)
- [ ] **15:10 이후 워치독 경보 미반복** — "파이프라인 N분 미실행" 90초 간격 반복 없음 확인
- [ ] **15:10 이후 강제 파이프라인 재실행 부작용 소멸** — `_try_pipeline_recovery`가 `run_minute_pipeline`을 추가 호출하는 로그 없음 확인
- [ ] **`verify_and_update` timeout 부작용 점검** — `[Buffer] verify_and_update 배치 오류` (3s timeout 실패) 빈도, 너무 잦으면 timeout 상향 검토
- [ ] **ScalerRefresh B_INTRADAY** `horizons=['1m','3m','5m','10m','15m','30m']` — `_is_fitted` 제거 효과 유지 확인
- [ ] **SGD 가중치 로그 형식** — `[OnlineLearner] 1m 가중치 조정 SGD=XX% GBM=XX%` (버킷→호라이즌별 변경 확인)
- [ ] **ERR-FATAL 없음** — `X has N features` 에러 재발 없음
- [ ] **STABLE_TREND 진입 개선** — 12시대 conf=48~52% 신호 발생 시 `[P1] Checklist min_conf 분리: 0.XX→0.48` 로그 확인
- [ ] **편향패널티 비활성화** — TrendGate ON 구간에서 `[MetaGate] 편향패널티` 로그 없음 확인
- [ ] **opt 4주 수집 후 Phase D 재검증**: opt_chain_pcr/gex_bn/atm_* 누적 확인
- [ ] **feat=118 vs managed=97 불일치** 해소: shap_feature_registry.json active_features 갱신 (opt_chain 포함)
- [ ] **SHAP 탭 호라이즌별 확장** — Phase C 호라이즌별 SHAP 계산 (현재 1m 기준만)
- [ ] `raw_features` DB 조회: `opt_chain_pcr`, `opt_gex_bn` 키 존재 여부 (미확인)
- [ ] **Phase D 재검증**: opt_chain_pcr/gex_bn/atm_* 4주 축적 확인 후 Walk-Forward 재실행
- [ ] **GBM retrain**: opt 피처 포함 첫 retrain → per-horizon pkl 생성 → 호라이즌별 모델 전환
- [ ] **Phase E**: SHAP Tracker 6개 호라이즌 확장 (shap_tracker.py horizon 컬럼 추가)
- [ ] **feat=118 vs managed=97 불일치** 해소: shap_feature_registry.json active_features 갱신 (opt_chain 포함)
- [ ] **Cybos Chejan `status` 필드 실측**
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
un_minute_pipeline()` 공통 차단 로그 경로보다 앞에서 `entry_mode`/`allowed_grades`/`mode_filter_passed`를 안전 초기화하도록 조정

[DONE 2026-05-20] **68차: watchdog 허위 지연 경보 원인 규명**
- 11:06~11:13 반복 경보는 실시간 분봉 미수신이 아니라 `minute_pipeline` 예외로 `notify_pipeline_ran()` 미도달한 결과임을 확인

[NEXT 실세션] **68차 수정사항 장중 검증 (2026-05-21)**
- SYSTEM 로그에 `ERR-FATAL minute_pipeline: local variable 'entry_mode' referenced before assignment` 재발 없는지 확인
- 자동진입 OFF, ENTRY cooldown, X등급 분봉에서 공통 차단 로그만 남고 파이프라인이 정상 종료되는지 확인
- 11시대와 유사한 흐름에서 watchdog 90초/150초 경보가 사라지는지 확인

[NEXT 미정] **watchdog 경보 문구 정밀화**
- 현재 `파이프라인 1분 30초 미실행` 문구가 예외 중단과 분봉 수신 지연을 구분하지 못함
- 최근 fatal 예외가 있었으면 `수신 지연 의심` 대신 `직전 파이프라인 예외 후 미복구` 식으로 원인 힌트 분리 검토
## 2026-05-22 (82차) — 미시 레짐 워밍업 UI

### 처리 완료

- [DONE 2026-05-22] **MicroRegime 워밍업 메타 추가**
  - `collection/macro/micro_regime.py` 에 `warmup` 상태 계산 추가
  - 단계: `L1 TR/ATR seed` → `L2 ADX warmup` → `L3 ATR avg warmup` → `READY`

- [DONE 2026-05-22] **헤더 미시 레짐 아래 워밍업 상태줄 추가**
  - `dashboard/main_dashboard.py` 에 라벨 + progress bar 추가
  - `main.py` 에서 `_mr["warmup"]` 를 대시보드로 전달

- [DONE 2026-05-22] **ATR avg 워밍업용 캔들 버퍼 상한 수정**
  - close/high/low buffer 길이를 늘려 `ATR avg 20샘플` 완료 전에 버퍼가 먼저 잘리는 문제 수정

### 다음 작업

- [NEXT 2026-05-23] **실 UI 워밍업 표시 검증**
  - `start_mireuk.bat` 기동 후 헤더에서 워밍업 라벨/바 위치, 색상, 폭 확인
  - 장중 재시작 시 `L1 → L2 → L3 → READY` 전환이 실제 분봉 흐름과 맞는지 확인

- [NEXT 2026-05-23] **워밍업 중 레짐 텍스트 처리 정책 검토**
  - 현재는 `횡보장/추세장` 텍스트는 유지하고, 아래에 워밍업 보조 설명을 표시
  - 필요 시 워밍업 중 본문 텍스트를 `레짐 워밍업` 또는 `혼합` 으로 강등할지 검토

- [NEXT 향후] **미시 레짐 워밍업 로그 명시화**
  - `MicroRegime` 로그에 `warmup level/progress` 를 함께 남길지 검토

---

---

## 2026-06-25 (243차 이후)

### DONE

- [DONE 2026-06-25] **Phase 2 재학습 경로 피처 슬라이싱 적용 (Audit Q1·Q2 해소)**
  - `learning/batch_retrainer.py` `_retrain_phase2()`에 `get_available_feature_set()` 호출 추가
  - 스케일러 97개 전체 fit, GBM h_idx 슬라이싱, feature_names_{hz}.pkl 저장
  - 커밋: 2f2cb8e (243차)

### NEXT (Stage 2 ~ Phase 3)

- [NEXT Stage 2] **buy_vol/sell_vol 30일 누적 후 1m/3m 재학습**
  - Phase 2 배포 후 ~30일 경과 시 OFI/CVD 기반 단기 모델 추가 개선 가능
  - EOD_RETRAIN.bat --phase2 로그에서 cvd_direction 비제로 비율 모니터링

- [NEXT Stage 3] **TRAINING_WINDOW 3m:5000 / 5m:3000 효과 확인**
  - 50일+ 누적 시 3m/5m 학습 윈도우 상한 실제 적용 여부 확인
  - `[Retrain-P2] * TRAINING_WINDOW=N 적용` 로그 출력 확인

- [NEXT Phase 3] **Platt Scaling 호라이즌별 독립 적용**
  - 현재 앙상블 캘리브레이션 공유 → 호라이즌별 독립 Platt 보정기 분리
  - 앙상블 왜곡 제거 효과 기대

- [NEXT 모니터링] **다음 EOD 재학습 후 슬라이싱 로그 확인**
  - `[Retrain-P2] *m 피처 슬라이싱: 97 → N개 (horizon_feature_sets.json)` 출력 여부
  - 출력 없으면: JSON에 해당 호라이즌 미등록 또는 전체 피처셋과 동일한 경우

```

</details>

### dev_memory/CURRENT_STATE.md — 515.8KB · 마지막 갱신 2026-08-11 18:30

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

### dev_memory/SESSION_LOG.md — 583.6KB · 마지막 갱신 2026-08-10 00:14

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

(없음)

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 16개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/evidence_MW0602-20260812_post.md` | 63.8KB | 08-12 19:19 |
| `docs/정기점검/매일점검/MW0602-20260812-점검리포트.md` | 25.2KB | 08-12 16:58 |
| `docs/정기점검/매일점검/MW0602-20260811-점검리포트.md` | 23.7KB | 08-11 17:50 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 11.8KB | 08-11 16:28 |
| `docs/정기점검/매일점검/MW0602-20260808-점검리포트.md` | 20.3KB | 08-08 16:51 |
| `docs/정기점검/매일점검/MW0602-20260806-점검리포트.md` | 20.9KB | 08-06 17:35 |
| `docs/정기점검/매일점검/MW0602-20260805-점검리포트.md` | 35.0KB | 08-05 19:30 |
| `docs/정기점검/매일점검/MW0601-20260731-점검리포트.md` | 40.2KB | 08-02 18:45 |

### `docs/정기점검/금요일점검` — 42개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/MW0602/exit_expectancy_map_20260810.md` | 1.8KB | 08-10 18:39 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_metrics_20260810.json` | 2.0KB | 08-10 15:18 |
| `docs/정기점검/금요일점검/MW0602/cvd_anchor_report_20260810.md` | 4.6KB | 08-10 15:18 |
| `docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601_잔여채널.md` | 39.1KB | 08-08 19:21 |
| `docs/정기점검/금요일점검/MW0601/0808_주간회의_검토보고_MW0601.md` | 24.3KB | 08-08 17:55 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260807.md` | 131.5KB | 08-07 19:23 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260807.json` | 70.5KB | 08-07 19:23 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260807.md` | 26.2KB | 08-07 19:23 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 차단 게이트 `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` = False 인데 **근거 미기록** — 의도한 예외인지 확인하고 DECISION_LOG에 남길 것
2. 장후인데 **강제청산(15:10) 흔적을 못 찾았다** — 절대원칙 1 확인 필요 (포지션이 없었을 수도 있다. 원본으로 구분할 것)
3. 전략 상태 경보 **판정 = UNDERPERFORM** — 배너 전문을 §5에서 확인하라
4. 청산 6건 중 하드스톱·손절 계열 **5건(83%)** — 손절 준수율 확인 필요
5. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
6. `logs/20260812_SIGNAL.log`: **WeightCollapse** 8건(표본)
7. `logs/20260812_LEARNING.log`: **축퇴** 8건(표본)
8. 미커밋 변경 2건
9. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260812*.log` (Windows) / `grep 강제청산 logs/*20260812*.log`*