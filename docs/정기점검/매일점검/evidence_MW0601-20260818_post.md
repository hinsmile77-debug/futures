# 미륵이 증거 다이제스트 — 2026-08-18 / POST

- 생성 2026-08-18 16:22:12 KST · PC **MW0601** (`DeskTop-MW0601`)
- 리포 `/sessions/charming-vigilant-hawking/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20260818` · `2026-08-18` · `260818` · `0818`

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **22개** 파일 · 22개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `daily_close_done_{DATE}.txt` | 1 | `data/daily_close_done_20260818.txt` | 28B | 08-18 15:40 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20260818.txt` | 133B | 08-18 15:50 |
| `launcher_{DATE}_084001_2415.log` | 1 | `logs/Mireuk_batch/launcher_20260818_084001_2415.log` | 1.8MB | 08-18 15:40 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20260818.log` | 19.9KB | 08-18 15:50 |
| `retrain_intraday_{DATE}_093759.log` | 1 | `logs/retrain_intraday_20260818_093759.log` | 2.4KB | 08-18 09:38 |
| `retrain_intraday_{DATE}_113159.log` | 1 | `logs/retrain_intraday_20260818_113159.log` | 2.4KB | 08-18 11:32 |
| `retrain_intraday_{DATE}_122559.log` | 1 | `logs/retrain_intraday_20260818_122559.log` | 2.4KB | 08-18 12:26 |
| `retrain_intraday_{DATE}_125859.log` | 1 | `logs/retrain_intraday_20260818_125859.log` | 2.4KB | 08-18 12:59 |
| `retrain_intraday_{DATE}_133159.log` | 1 | `logs/retrain_intraday_20260818_133159.log` | 2.4KB | 08-18 13:32 |
| `retrain_intraday_{DATE}_145459.log` | 1 | `logs/retrain_intraday_20260818_145459.log` | 2.4KB | 08-18 14:55 |
| `strategy_report_{DATE}_154023.txt` | 1 | `data/daily_reports/strategy_report_20260818_154023.txt` | 2.3KB | 08-18 15:40 |
| `{DATE}_DATA.log` | 1 | `logs/20260818_DATA.log` | 343.0KB | 08-18 15:34 |
| `{DATE}_DEBUG.log` | 1 | `logs/20260818_DEBUG.log` | 236.6KB | 08-18 15:09 |
| `{DATE}_HEALTH.log` | 1 | `logs/20260818_HEALTH.log` | 4.7KB | 08-18 14:31 |
| `{DATE}_HOGA.log` | 1 | `logs/20260818_HOGA.log` | 55.0MB | 08-18 15:40 |
| `{DATE}_LEARNING.log` | 1 | `logs/20260818_LEARNING.log` | 281.7KB | 08-18 15:40 |
| `{DATE}_MICRO.log` | 1 | `logs/20260818_MICRO.log` | 1.1MB | 08-18 15:38 |
| `{DATE}_PROBE.log` | 1 | `logs/20260818_PROBE.log` | 96.7KB | 08-18 15:34 |
| `{DATE}_SIGNAL.log` | 1 | `logs/20260818_SIGNAL.log` | 655.6KB | 08-18 15:40 |
| `{DATE}_SYSTEM.log` | 1 | `logs/20260818_SYSTEM.log` | 878.3KB | 08-18 15:40 |
| `{DATE}_TRADE.log` | 1 | `logs/20260818_TRADE.log` | 30.6KB | 08-18 15:40 |
| `{DATE}_WARN.log` | 1 | `logs/20260818_WARN.log` | 106.2KB | 08-18 15:40 |

## 2. 코드·커밋 상태

- HEAD `7dc14bc` · 브랜치 `v9-dev` · 미커밋 458건
```
M .claude/commands/dailycheck.md
 M .claude/skills/mireuk-daily-check/RUN_ON_MW0602.md
 M .claude/skills/mireuk-daily-check/SKILL.md
 M .claude/skills/mireuk-daily-check/config_dailycheck_targets.json
 M .claude/skills/mireuk-daily-check/references/evidence_map.md
 M .claude/skills/mireuk-daily-check/references/invariants.md
 M .claude/skills/mireuk-daily-check/references/phases.md
 M .claude/skills/mireuk-daily-check/references/postmortem.md
 M .claude/skills/mireuk-daily-check/references/report_template.md
 M .claude/skills/mireuk-daily-check/scripts/collect_evidence.py
 M .gitignore
 M CLAUDE.md
 M INSTALL.bat
 M LAUNCH_API.bat
 M ROADMAP.md
 M SETUP_GUIDE.md
 M backtest/param_optimizer.py
 M backtest/walk_forward.py
 M challenger/challenger_db.py
 M challenger/challenger_engine.py
 M challenger/promotion_manager.py
 M challenger/variants/base_challenger.py
 M challenger/variants/champion_tp1_skip_trail.py
 M collection/broker/base.py
 M collection/broker/cybos_broker.py
 M collection/broker/factory.py
 M collection/cybos/api_connector.py
 M collection/cybos/investor_data.py
 M collection/cybos/realtime_data.py
 M collection/kiwoom/api_connector.py
 M collection/kiwoom/investor_data.py
 M collection/macro/macro_fetcher.py
 M collection/macro/micro_regime.py
 M collection/options/pcr_store.py
 M collection/provenance.py
 M config/capital.py
 M config/constants.py
 M config/dailycheck_targets.json
 M config/krx_holidays.py
 M config/secrets_example.py
… 외 418건
```

**당일(2026-08-18) 커밋**
```
(당일 커밋 없음)
```

**최근 커밋 12건**
```
7dc14bc [MW0601] 474차: D9 딥다이브 — §3 정합화 + 라우팅 밴드 채널 + 30m 역필터 기각
68ff91c [MW0601] 473차: 구조적 교착 해소 — 테스트 오염 · F-8 배선/판정 · D9 도달성 · D8 인프라
e995764 [MW0601] 472차: UI 좌상단 "Phase 3 예정" 배지 → Phase 5 전환 게이트 자동 판정
f911e8d [MW0601] 471차 후속8: G-3 강제청산 리허설 26주 WFA 편입 + 로드맵 반영 + dev_memory
211246d [MW0601] 471차 후속7: G-2 ConstOut 호라이즌 건강도 채널 [51] 신설
ca954b8 [MW0601] 471차 후속6: G-1 사이징 계보 구조체 저장 + [28] 사이저 압력 실측화
cdb7462 [MW0601] 471차 후속5: dev_memory 반영 — F-9 구현 기록
7284b95 [MW0601] 471차 후속4: entry_mode 예외 폴백 가시화 (F-9)
fc889ff [MW0601] 471차 후속3: dev_memory 반영 — 471차 구현 기록 + 잔여/후속 항목
82e7554 [MW0601] 471차 후속2: 차단사유 정합 — 동시 성립 축 전량 + 선제차단 플래그 (스키마)
8be4048 [MW0601] 471차 후속: [SizerMatch] binding 게이트 명시 + 품질군 전량 출력
76211c3 [MW0601] 471차: 15:10 강제청산 1차 경로 도달성 복구 + 안전망 하트비트
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
| `MODEL_LABEL_STATE_UNLOCK_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지 |
| `PRE_RETRAIN_DONE_BY_EOD_ENABLED` | `—` | `True` | **미발견 ⚠** | 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치 |
| `ZONE_ENTRY_BAN_ENFORCE` | `—` | `False` | **미발견 ⚠** | 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지 |
| `ZONE_ENTRY_BAN_SHADOW_ENABLED` | `—` | `True` | **미발견 ⚠** | 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다 |
| `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` | `—` | `True` | **미발견 ⚠** | 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치) |
| `VALIDATION_CAMPAIGN["mode"]` | `standing` | `standing` | 일치 | 2026-08-01 상시 운영 전환 |

> 이 표는 **의도한 예외가 여전히 의도대로인지** 보는 것이다. `불일치`는 누군가 바꿨다는 뜻이고, 바꿨다면 `dev_memory/DECISION_LOG.md` 에 근거가 있어야 한다.

### 차단 게이트 전수 인벤토리 — 27개 중 **7개 꺼짐**

| 플래그 | 값 | 기록됨 |
|---|---|---|
| `CB3_P4_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `FP_CRITICAL_GRADE_BLOCK_ENABLED` | False | 기록됨 |
| `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` | False | 기록됨 |
| `LIMIT_ENTRY_FIRST_ENABLED` | False | 기능토글 |
| `LOSS_TIER1_QTY1_ENABLED` | False | 기능토글 |
| `TICKUI_TRACE_ENABLED` | False | 기능토글 |
| `TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED` | False | 기록됨 |
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
| `SIGNAL_DECAY_EXIT_ENABLED` | True | — |
| `SIZING_TARGET_CAPITAL_ENABLED` | True | — |
| `TP1_TICK_ENABLED` | True | — |
| `VOLATILITY_BURST_GUARD_ENABLED` | True | — |

## 4. 마커·리포트 · 로그 다이제스트

_본문 미열람(설정): `20260818_HOGA.log` 55.0MB — 존재와 크기만 증거로 본다_

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/daily_close_done_20260818.txt`** — 28B · 08-18 15:40:23
```
2026-08-18T15:40:23.271522
```

**`data/daily_reports/strategy_report_20260818_154023.txt`** — 2.3KB · 08-18 15:40:23
```
========================================================
  미륵이 일일 전략 상태 리포트  2026-08-18 15:40
========================================================
  버전    : v1.0  (62일차)
  판정    : OUTPERFORM
  Live(20일): Sh=1.95  MDD(자본대비)=3.3%
  당일      : WR=85.7%  PF=3.70
  롤링20일: 누적 +1308736원  Sh=1.95  MDD(자본대비)=3.3%  MDD(peak대비)=127.0%
--------------------------------------------------------
  CUSUM   : CLEAR (0.00)
  PSI     : 0.008 (CLEAR)
  PSI/feat: cvd=0.142  vwap_position=0.008  ofi=0.005
--------------------------------------------------------
  권고    : ● 정상 유지
  사유    : 기대값 상회 & 드리프트 정상 — 현재 전략 유지.
--------------------------------------------------------
  최근20건 순EV: 평균 +31,683원  승률 75.0%  합계 +633,653원
  등급별 순EV(30일): A=+14,380원(142건,승63%)  C=-27,056원(34건,승62%)
  호라이즌별 순EV(30일): 1m=+46,493원(17건)  3m=-3,912원(96건)  5m=+12,148원(60건)  ?=-7,238원(3건)
--------------------------------------------------------
  CL신뢰도차단: 0회 (앙상블 통과→conf 미달 강제 X)
--------------------------------------------------------
  진입후보(conf≥mc): 금일 94분  5일평균 56분 ⚠ 하한 미달
    └ 변동성(참고): 당일 레인지 73.1pt(5일평균 32.3pt)  1분평균변동 1.14pt(5일평균 0.89pt)
--------------------------------------------------------
  진입 퍼널(2026-08-18, 총 370분):
    FLAT 164 → conf미달 99 → CoherenceGate 13 → 게이트차단 77 → 후보 17 → 진입 7
    └ 등급상향경로(앙상블X→체크리스트통과): 2건 [285차-P5]
    게이트별: 게이트강등(기타)=25  체크리스트항목미달=24  포지션보유중(평가생략)=10  콜드스타트/기타(σ미수집)=4  쿨다운=4  시가갭(OPEN_VOLATILE)=3  콜드스타트/기타(조건부구간)=2  Degraded신뢰도=2  마감시간(신규진입금지)=2  ATR변동성=1
    ⚠ 2차게이트차단(체크리스트 통과 후 미진입): 10건
      └ 상세: JointGateBlock=10
      └ JointGateBlock 10건 (무정보폴백 10건 = 100.0%) [표본 10건 부족 — 판정보류]
    └ 정합성: OK (칸합계·진입·JointGateBlock 3종 일치)
========================================================
```

**`data/eod_retrain_done_20260818.txt`** — 133B · 08-18 15:50:48
```
completed: 2026-08-18 15:50:48
rows: 40140
cols: 97
horizons_replaced: 6/6
t_load_s: 82.5
t_retrain_s: 256.4
t_total_s: 340.2
```

_다이제스트 대상 8/18개 (중요도순). 제외: `retrain_intraday_20260818_113159.log`, `retrain_intraday_20260818_125859.log`, `retrain_intraday_20260818_133159.log`, `retrain_intraday_20260818_145459.log`, `retrain_intraday_20260818_122559.log`, `20260818_MICRO.log`, `20260818_DATA.log`, `20260818_PROBE.log`_

### `logs/20260818_TRADE.log` — 30.6KB · 210행 · 최종 15:40:22

- 형식 평문 · 시각 인식 210행 · WARNING=1, INFO=209

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:41:14 [INFO] TRADE: [Position] 저장 상태가 어제 데이터 — 무시
2026-08-18 08:41:18 [INFO] TRADE: [ProfitGuard] 설정 업데이트 완료
2026-08-18 09:32:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,053,027) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 09:34:58 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,053,027) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 09:35:58 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,053,027) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
  …
2026-08-18 14:41:00 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 14:45:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 14:54:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 14:59:59 [INFO] TRADE: [Sizer] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 3계약 (최소=1)
2026-08-18 15:40:22 [INFO] TRADE: [ProfitGuard] 일간 리셋 완료
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ProfitGuard-L1` | 1 | 13:19:59 | 13:19:59 | 트레일링 발동 — 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원) |

**채널** — `TRADE`×210

**컴포넌트 상위 15** — `Sizer`×59, `Chejan`×47, `Position`×29, `주문요청`×21, `JointGateBlock 차단`×10, `진입체크`×7, `체결진입`×7, `청산 완료`×7, `TickTP1`×6, `TP1 부분청산`×6, `체결진입보정`×5, `ProfitGuard`×2, `TickStop-S0C`×2, `손절1차 조기축소`×1, `ProfitGuard-L1`×1

### `logs/20260818_WARN.log` — 106.2KB · 457행 · 최종 15:40:22

- 형식 평문 · 시각 인식 457행 · WARNING=457

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance(account_no)…
2026-08-18 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance TradeInit 완료 31ms
2026-08-18 08:41:21 [WARNING] SYSTEM: [LiveDBG] request_futures_balance 완료 총 141ms account=333044256
2026-08-18 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
2026-08-18 08:41:27 [WARNING] SYSTEM: [LiveDBG] _restore_panels_worker 지연 3453ms — live 중단 원인 분석용
  …
2026-08-18 14:34:59 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 -0.321% (임계 ±0.193%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-18 14:50:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 948ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
2026-08-18 14:53:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
2026-08-18 14:56:59 [WARNING] SYSTEM: [ScalerRefresh] 5분 누적 수익률 +0.347% (임계 ±0.298%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분)
2026-08-18 15:40:22 [WARNING] SYSTEM: [경보] mc-conf 괴리: 최근 5거래일 평균 진입후보 56분/일 < 하한 60분 — 금일 94분.
```

</details>

**WARNING — 태그 32종 (상위 12)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `LiveDBG` | 129 | 08:41:21 | 14:21:03 | request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmProjects\futures\collection\broker\cybos_broker.py", line 79, in request_futures_balance |   return self._api.request_futures_balance… |
| `ChejanFlow` | 47 | 10:20:59 | 13:19:39 | account='333044256' | balance_side_code='' | buy_balance=0 | closable_qty=0 | code='A0569' | fill_price=0.0 | fill_qty=2 | gubun='0' | order_no='1545' | pending='ENTRY:SHORT qty=2 filled=0 order_no=? reason=진입 req_at=10:20:58.824' | positi… |
| `ChejanMatch` | 47 | 10:20:59 | 13:19:39 | order_no='1545' | pending='ENTRY:SHORT qty=2 filled=0 order_no=1545 reason=진입 req_at=10:20:58.824' | pending_matched=True |
| `PendingOrder` | 42 | 10:20:58 | 13:19:39 | set {'kind': 'ENTRY', 'direction': 'SHORT', 'raw_direction': 'SHORT', 'reverse_entry_enabled': False, 'qty': 2, 'price_hint': 1132.68, 'reason': '진입', 'hint_source': '', 'atr': 1.8586, 'grade': 'A', 'stage': None, 'order_no': '', 'filled_q… |
| `Health` | 18 | 09:08:58 | 14:30:59 | level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |
| `ScalerRefresh` | 16 | 09:14:58 | 14:56:59 | 5분 누적 수익률 +0.457% (임계 ±0.344%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| `ExitCooldown` | 14 | 10:21:59 | 13:19:39 | 하드스톱 후 2분 재진입 금지 (until 10:23:59) |
| `EntryFillFlow` | 12 | 10:20:59 | 13:07:01 | actual_side='SHORT' | after='SHORT 2계약 @ 1132.44' | applied_side='SHORT' | before='SHORT 2계약 @ 1132.68' | fill_no='' | fill_price=1132.44 | fill_qty=1 | order_no='1545' | pending='ENTRY:SHORT qty=2 filled=1 order_no=1545 reason=진입 req_at=1… |
| `CB③-P4` | 12 | 10:56:58 | 14:30:59 | acc30m 단계 전환: NORMAL → WATCH (acc=33.3%) |
| `PipePerf` | 10 | 09:39:01 | 13:33:01 | total=2826ms | S0=2407ms S1=20ms S2=21ms S3=0ms S4=101ms S5=157ms S6=110ms S7=8ms S8=3ms |
| `CB⑤` | 10 | 09:39:01 | 13:33:01 | 파이프라인 2826ms 경고 (기준 1000ms) |
| `ExitSendOrderResult` | 8 | 10:21:59 | 13:19:39 | ret=0 kind=하드스톱 direction=SHORT qty=1 |

**채널** — `SYSTEM`×439, `HEALTH`×18

**컴포넌트 상위 15** — `LiveDBG`×129, `ChejanFlow`×47, `ChejanMatch`×47, `PendingOrder`×42, `Health`×18, `ScalerRefresh`×16, `ExitCooldown`×14, `EntryFillFlow`×12, `CB③-P4`×12, `PipePerf`×10, `CB⑤`×10, `ExitSendOrderResult`×8, `EntryAttempt`×7, `EntrySendOrderResult`×7, `FixB`×7

### `logs/20260818_SYSTEM.log` — 878.3KB · 6193행 · 최종 15:40:38

- 형식 평문 · 시각 인식 6172행 · INFO=6172, PLAIN=21

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:40:47 [INFO] SYSTEM: [FaultHandler] 활성화 | file=logs\crash_fault.log PID=21660 | 행감지=30s all_threads=True
2026-08-18 08:41:00 [INFO] SYSTEM: [System] DB 초기화 완료
2026-08-18 08:41:00 [INFO] SYSTEM: [System] 미륵이 초기화
2026-08-18 08:41:00 [INFO] SYSTEM: 미륵이 초기화
2026-08-18 08:41:00 [INFO] SYSTEM: [FeatureBuilder] 기동 시 전일(2026-08-14) 종가 버퍼 로드: 384봉
  …
2026-08-18 15:40:23 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
2026-08-18 15:40:23 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
2026-08-18 15:40:38 [INFO] SYSTEM: [System] 자동 종료 실행
2026-08-18 15:40:38 [INFO] SYSTEM: 미륵이 자동 종료
2026-08-18 15:40:38 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
```

</details>

**채널** — `SYSTEM`×6172

**컴포넌트 상위 15** — `CybosInvestorRaw`×1574, `CybosRT-TICK`×1402, `CybosRT-ROLLOVER`×409, `BAR-CLOSE`×409, `CVD-ANCHOR`×409, `TickUI`×407, `S6Detail`×370, `PipePerf`×370, `System`×98, `CybosEvent`×94, `MicroRegime`×77, `BalanceUI`×76, `CybosDailyPnl`×64, `BalanceRefresh`×56, `OptionChain`×52

### `logs/20260818_SIGNAL.log` — 655.6KB · 5651행 · 최종 15:40:22

- 형식 평문 · 시각 인식 5651행 · WARNING=2176, INFO=3475

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.434
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.413
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.409
2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: CLOSE_VOLATILE  0.620 → 0.417
  …
2026-08-18 15:09:59 [INFO] SIGNAL: [ProfitGuard] 진입 차단 [L1-Trail] 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,600원)
2026-08-18 15:10:15 [INFO] SIGNAL: [TimeRouter] 시간대 전환 → OTHER: 기타 구간 — 진입 금지
2026-08-18 15:40:22 [INFO] SIGNAL: [FeatureBuilder] daily reset complete
2026-08-18 15:40:22 [INFO] SIGNAL: [ScalerMonitor] EOD 일별 집계 저장 | date=2026-08-18 age=23m extreme=425 refresh=43 grade_x=121 cb3=0
2026-08-18 15:40:22 [INFO] SIGNAL: [ModelHealth] date=2026-08-18 앙상블유효가동률=76.5% | 파이프라인 370분 | ConstOut 6회/8분 {"3m": {"events": 5, "minutes": 6}, "5m": {"events": 1, "minutes": 2}} | WeightCollapse 79분 | 장중재학습 6회
```

</details>

**WARNING — 태그 8종 (상위 8)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `ScalerFloor` | 1524 | 09:00:59 | 14:56:59 | 1m 'macro_sp500_chg' scale=0.0701 → floor=0.15 적용 (z-score 폭발 방지) |
| `ScalerRefresh` | 216 | 08:45:21 | 14:56:59 | 1m CORE 'ofi_norm' raw_std≈0(0.0294) → identity(0,1) 강제 (FLAT 100% 방지) |
| `Model` | 132 | 09:00:58 | 12:20:59 | 1m 극단 z-score 2개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| `Checklist` | 130 | 09:05:58 | 15:09:59 | 신뢰도 미달 34.9% < 39.2% → 강제 X등급 |
| `ScalerMonitor` | 88 | 09:00:58 | 12:30:58 | ts=09:00 horizon=1m age=2m max_z=+6.42(ret_15m) extreme=2 |
| `WeightCollapse` | 79 | 09:07:59 | 15:07:59 | 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m']) |
| `ConstOut` | 6 | 09:36:58 | 14:53:59 | 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외 |
| `ConfFloorGuard` | 1 | 09:05:58 | 09:05:58 | 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3920 (conf_floor=0.330, min_conf=0.392, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다. |

**채널** — `SIGNAL`×5651

**컴포넌트 상위 15** — `ScalerFloor`×1542, `SIGNAL`×740, `MetaGate`×465, `Ensemble`×379, `FQAdj`×368, `ZeroDiag`×284, `ScalerRefresh`×264, `Checklist`×262, `ProfitGuard`×197, `ATR-Horizon`×193, `Model`×174, `차단`×121, `ToxicityGate`×112, `ScalerMonitor`×89, `WeightCollapse`×79

### `logs/20260818_LEARNING.log` — 281.7KB · 2753행 · 최종 15:40:22

- 형식 평문 · 시각 인식 2753행 · WARNING=157, INFO=2596

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 08:41:02 [INFO] LEARNING: [RF] 로드 완료: 6호라이즌 ready=True
2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2002 < conf_floor=0.3300 (span=0.00040 auc=0.536 out_max=0.2002, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00033 auc=0.529 out_max=0.2002 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=85) → 보정 미적용, raw 통과
2026-08-18 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00064 auc=0.556 out_max=0.2004 (n=90) → 보정 재적용
  …
2026-08-18 15:40:22 [INFO] LEARNING: [OnlineLearner] 일간 리셋 (모델 가중치 유지)
2026-08-18 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-18 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 재적합 완료 (n=5000)
2026-08-18 15:40:22 [INFO] LEARNING: [ExtremityCorrector] 일일 재적합: {'live': {'30m': True}, 'shadow': {'30m': True}}
2026-08-18 15:40:22 [INFO] LEARNING: [Sigma] EOD sigma_20=0.15226% 저장 (내일 장 초반 20봉 미수집 구간 폴백용)
```

</details>

**WARNING — 태그 2종 (상위 2)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Calibration` | 156 | 08:41:05 | 14:30:59 | 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과 |
| `DriftAdjuster` | 1 | 15:40:22 | 15:40:22 | 3일 연속 정확도 50% 미만 → alpha 0.01000→0.01000 |

**채널** — `LEARNING`×2753

**컴포넌트 상위 15** — `LEARNING`×1216, `SGD`×369, `sigma`×357, `Calibration`×308, `Bias`×136, `Bias⚠`×122, `MetaConf`×78, `OnlineLearner`×51, `ScalerWarmup`×48, `SHAP`×12, `BiasReset`×12, `GBM-64`×12, `GBM`×12, `RF`×7, `ExtremityCorrector`×5

### `logs/20260818_HEALTH.log` — 4.7KB · 35행 · 최종 14:31:59

- 형식 평문 · 시각 인식 35행 · WARNING=18, INFO=17

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 09:08:58 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-18 09:09:58 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=260ms | quality=1.00 | cache_age=49s | exceptions_10m=0
2026-08-18 09:29:58 [INFO] HEALTH: [HealthTrend] 세션 지연 기준선 확정: 256ms (표본 20분)
2026-08-18 09:39:01 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=2826ms | quality=1.00 | cache_age=132s | exceptions_10m=0
2026-08-18 09:39:58 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=335ms | quality=1.00 | cache_age=7s | exceptions_10m=0
  …
2026-08-18 13:33:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=335ms | quality=1.00 | cache_age=68s | exceptions_10m=1
2026-08-18 13:41:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=436ms | quality=1.00 | cache_age=181s | exceptions_10m=0
2026-08-18 13:43:01 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=414ms | quality=1.00 | cache_age=59s | exceptions_10m=0
2026-08-18 14:30:59 [WARNING] HEALTH: [Health] level=WARNING degraded=OFF | latency=374ms | quality=1.00 | cache_age=182s | exceptions_10m=1
2026-08-18 14:31:59 [INFO] HEALTH: [Health] level=INFO degraded=OFF | latency=382ms | quality=1.00 | cache_age=51s | exceptions_10m=2
```

</details>

**WARNING — 태그 1종 (상위 1)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `Health` | 18 | 09:08:58 | 14:30:59 | level=WARNING degraded=OFF | latency=289ms | quality=1.00 | cache_age=181s | exceptions_10m=0 |

**채널** — `HEALTH`×35

**컴포넌트 상위 15** — `Health`×34, `HealthTrend`×1

### `logs/retrain_eod_20260818.log` — 19.9KB · 136행 · 최종 15:50:50

- 형식 평문 · 시각 인식 136행 · WARNING=16, INFO=120

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 15:45:08,464 [INFO] EOD_RETRAIN: =======================================================
2026-08-18 15:45:08,465 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-08-18 15:45:08,465 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-08-18 15:45:08,465 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-08-18 15:45:08,466 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-08-18 15:50:50,045 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0345 → floor=0.15 적용 (z-score 폭발 방지)
2026-08-18 15:50:50,046 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.0931 → floor=0.20 적용 (z-score 폭발 방지)
2026-08-18 15:50:50,050 [INFO] SIGNAL: [ScalerRefresh] ts=15:50 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-08-18 15:50:50,056 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-08-18 15:50:50,057 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 3종 (상위 3)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 15:46:42 | 15:49:25 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1509봉(82%)이 현행 학습구간 (현행 cutoff=2026-08-14 14:38:00 ≥ 홀드아웃 시작=2026-08-10 12:17:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-08-14 14:38 >= holdout_start=2026-08-10 12:17 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-08-14 … |
| `ScalerRefresh` | 6 | 15:50:49 | 15:50:50 | 1m CORE 'ofi_norm' raw_std≈0(0.0312) → identity(0,1) 강제 (FLAT 100% 방지) |
| `GuardGhost` | 4 | 15:47:00 | 15:47:20 | 3m 비교 기준이 유령이다 — 배포된 pkl은 CV 미검증 intraday 모델(학습 2026-08-18 14:24:00까지)인데 acc.txt=0.4227는 다른 모델의 성적이다. 이 판정은 존재하지 않는 모델과의 비교다. |

**채널** — `LEARNING`×65, `SIGNAL`×43, `EOD_RETRAIN`×20, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×30, `Retrain`×20, `EOD_RETRAIN`×14, `RF`×9, `ScalerRefresh`×7, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `GuardGhost`×4, `RegimeFingerprint`×3, `WaitDC`×2

### `logs/retrain_intraday_20260818_093759.log` — 2.4KB · 20행 · 최종 09:38:27

- 형식 평문 · 시각 인식 20행 · INFO=20

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-08-18 09:37:59,005 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-18 09:37:59,006 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-08-18 09:37:59,006 [INFO] RETRAIN_INTRADAY: ==================================================
2026-08-18 09:37:59,006 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True horizons=['3m'] result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_71f9dec0.json
2026-08-18 09:38:02,508 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-08-18 09:38:26,928 [INFO] LEARNING: [Retrain] 3m 교체 (intraday — CV 없음 | fit=0.92s | old_acc=0.4227)
2026-08-18 09:38:27,028 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-08-18 09:38:27,028 [INFO] LEARNING: [Retrain] 완료 | 24.5초 | 성공=1/1 호라이즌
2026-08-18 09:38:27,028 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 28.0s 데이터=4800행
2026-08-18 09:38:27,030 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_71f9dec0.json
```

</details>

**채널** — `LEARNING`×13, `RETRAIN_INTRADAY`×6, `FEAT_REG`×1

**컴포넌트 상위 15** — `Retrain`×11, `RETRAIN_INTRADAY`×6, `CUSUM`×1, `FeatureReg`×1, `Retrain-Timing`×1

## 5. 거래일 요약 — 오늘 무엇을 했는가

| 항목 | 건수 |
|---|---|
| 진입체크 통과(`[진입체크]`) | 7 |
| 진입 등록(`[Position] 진입`) | 7 |
| 체결(`[체결진입]`) | 7 |
| 청산(`체결청산`) | 7 |
| 차단(`[차단]`) | 121 |
| 사이저 호출(`[Sizer]`) | 59 |

### 청산 7건 · 승 6 (86%) · 합계 +5.62pt (+269,334원)

| 시각 | 방향 | PnL(pt) | PnL(원) | 사유 |
|---|---|---|---|---|
| 10:21:59 | SHORT | +1.55 | +75,801 | 하드스톱 |
| 10:40:59 | SHORT | +2.13 | +104,805 | 하드스톱 |
| 10:50:59 | SHORT | +1.30 | +63,325 | 하드스톱 |
| 10:57:59 | SHORT | +1.42 | +69,330 | 하드스톱 |
| 11:35:47 | SHORT | +0.17 | +6,859 | 하드스톱(틱) |
| 11:42:00 | SHORT | +2.38 | +117,353 | 하드스톱 |
| 13:19:39 | SHORT | -3.33 | -168,139 | 하드스톱(틱) |

**청산 사유 분포** — `하드스톱`×5, `하드스톱(틱)`×2

> 하드스톱·손절 계열 7/7건. **손절 준수율**(실현손실 ÷ 의도손절폭 ATR×1.5)은 417차 재분해에서 유일하게 유의했던 축이다 — 진입 로그의 `손절=` 값과 대조하라.

### 진입 7건

| 시각 | 방향 | 계약 | 진입가 | 호라이즌 | Hurst |
|---|---|---|---|---|---|
| 10:20:58 | SHORT | 2 | 1132.68 | 3m | mean-revert |
| 10:39:59 | SHORT | 2 | 1129.94 | 1m | neutral |
| 10:49:58 | SHORT | 2 | 1117.04 | 5m | trend |
| 10:55:59 | SHORT | 2 | 1113.4 | 5m | trend |
| 11:34:59 | SHORT | 2 | 1094.34 | 5m | trend |
| 11:39:59 | SHORT | 2 | 1098.14 | 5m | trend |
| 13:06:59 | SHORT | 2 | 1092.54 | 3m | mean-revert |

계약수 분포 — 2계약×7

등급 분포 — `A급(원시C)`×6, `A급(원시X)`×1

**진입한 건들의 체크리스트 미통과 항목** — `fore`×4, `chas`×4, `ofi`×3, `prev`×3, `cvd`×2

### 사이저 출력 vs 실제 진입 — 게이트 배수에 눌리고 있는가

사이저 출력 계약수 — **1계약**×4, **2계약**×16, **3계약**×39

실제 진입 계약수 — **2계약**×7

> ⚠ 사이저는 최대 **3계약**을 냈는데 실제 진입 최대는 **2계약**이다. 게이트 배수(meta·tox 등)에 눌린 것인지 확인하라 — 실전 전환 기준 ⑧의 `sizing_inversion_watch` 채널이 이것을 본다.

배수 조합 상위 — `conf=0.6 regime=0.8 safe=1.00`×59

### 차단 사유 121건 · 39종

| 건수 | 사유 |
|---|---|
| 37 | 등급X — 미통과 항목: 2_confidence |
| 18 | 게이트 강등 X — ProfitGuard 진입 차단 ([L1-Trail] 피크 +927,000원 대비 20% 하락 (현재 +685,000원 < 보호선 +741,… |
| 6 | JointGateBlock — meta=0.50 tox=0.70 joint=0.350 < 0.50 |
| 6 | 14:50 이후 — 신규 진입 금지 구간 (345차) |
| 5 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar |
| 5 | 자동진입 Degraded 최소신뢰도 62.0% 미달 |
| 5 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar |
| 3 | 등급X — 미통과 항목: 3_vwap, 6_foreign |
| 3 | 게이트 강등 X — ProfitGuard 진입 차단 ([L2-Tier2] Tier 2: size_mult 0.6 < 최소 1.0 요구) (체크리스트 등급=C, … |
| 3 | 점심 휴식 구간 (11:50~13:00 OTHER) — 체크리스트 8_time 실패 |
| 2 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 5_ofi, 6_foreign, 7_prev_bar, 11_countertrend |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 18.2pt > ATR×5.0=13.7pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.8pt > ATR×5.0=13.4pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.8pt > ATR×5.0=11.4pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 20.3pt > ATR×5.0=10.1pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 21.8pt > ATR×5.0=9.8pt (시가=1118.78 반등위험) |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 23.0pt > ATR×5.0=9.2pt (시가=1118.78 반등위험) |
| 1 | 등급X — 미통과 항목: 3_vwap, 6_foreign, 7_prev_bar, 10_chase |
| 1 | 등급X — 미통과 항목: 3_vwap, 4_cvd, 6_foreign, 7_prev_bar, 10_chase |
| 1 | OPEN_VOLATILE 시가이격 과다 — 방향이탈 15.9pt > ATR×5.0=9.9pt (시가=1118.78 반등위험) |

**체크리스트 미통과 항목 누적** — `2_confidence`×37, `3_vwap`×23, `6_foreign`×22, `7_prev_bar`×17, `4_cvd`×14, `5_ofi`×12, `10_chase`×3, `11_countertrend`×3

> 진입 0건이거나 적을 때 여기가 출발점이다. 특정 항목 하나가 압도적이면 그 게이트의 임계를 의심하라 — 316차 HurstGate 63% 차단이 그렇게 발견됐다.

### Circuit Breaker 이벤트 4건

- `일간 리셋 완료` ×2
- `연속 손절 1회` ×1
- `연속 손절 2회` ×1

> CB② 는 `CB_CONSEC_STOP_LIMIT=9999` 라 **연속 손절 카운터는 올라가되 정지는 안 한다.** 카운터 로그가 보이는 것은 정상이다.

### 메인 스레드 블로킹 22건 · 최대 37875ms · 5초 초과 5건

상위 — 37875ms, 14422ms, 5532ms, 5203ms, 5172ms, 4734ms, 4500ms, 4172ms

> ⚠ `CB_PIPE_PAUSE_MS = 5_000`(CB⑤ 실질 구현) 이상이 **5건**이다. CB⑤가 실제로 발동했는지, 아니면 계측만 되고 지나갔는지 확인하라.

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

### `logs/20260818_WARN.log`
```
--- ConstOut ×6(표본)
09:36:58 2026-08-18 09:36:58 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
11:30:58 2026-08-18 11:30:58 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
12:24:59 2026-08-18 12:24:59 [WARNING] SYSTEM: [ConstOut] ['5m'] 상수 출력 확정 → 스케일러 재적합 시작
12:57:59 2026-08-18 12:57:59 [WARNING] SYSTEM: [ConstOut] ['3m'] 상수 출력 확정 → 스케일러 재적합 시작
--- [CB] ×2(표본)
13:08:37 2026-08-18 13:08:37 [WARNING] SYSTEM: [CB] 연속 손절 1회
13:19:39 2026-08-18 13:19:39 [WARNING] SYSTEM: [CB] 연속 손절 2회
--- [ExitCooldown] ×8(표본)
10:21:59 2026-08-18 10:21:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:23:59)
10:21:59 2026-08-18 10:21:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:23:59)
10:40:59 2026-08-18 10:40:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:42:59)
10:40:59 2026-08-18 10:40:59 [WARNING] SYSTEM: [ExitCooldown] 하드스톱 후 2분 재진입 금지 (until 10:42:59)
--- [SHAP] 슬로우 ×5(표본)
12:18:03 2026-08-18 12:18:03 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1978ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 1m는 유실 없이 밀림)
13:29:00 2026-08-18 13:29:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1080ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 3m는 유실 없이 밀림)
14:20:00 2026-08-18 14:20:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 1087ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
14:31:00 2026-08-18 14:31:00 [WARNING] SYSTEM: [SHAP] 슬로우 감지 904ms (임계 900ms) — 다음 5분 건너뜀 (호라이즌 5m는 유실 없이 밀림)
--- 메인 스레드 블로킹 ×8(표본)
08:41:24 2026-08-18 08:41:24 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2750ms — 메인 스레드 블로킹 발생 | pipe_elapsed=-1 watchdog_alerted=[]
09:01:00 2026-08-18 09:01:00 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:06:02 2026-08-18 09:06:02 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 3719ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
09:31:59 2026-08-18 09:31:59 [WARNING] SYSTEM: [LiveDBG] _tick_header 간격 2016ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[]
```

### `logs/20260818_SYSTEM.log`
```
--- ConstOut ×8(표본)
09:36:58 2026-08-18 09:36:58 [INFO] SYSTEM: [ConstOut] heavy cooldown armed until 09:39:00 (const_output)
09:36:58 2026-08-18 09:36:58 [INFO] SYSTEM: [ConstOut][Worker] 시작 hz=['3m']
09:36:58 2026-08-18 09:36:58 [INFO] SYSTEM: [ConstOut][Worker] 완료 hz=['3m'] load=87ms fit=48ms total=137ms
09:37:58 2026-08-18 09:37:58 [INFO] SYSTEM: [ConstOut] ['3m'] 재적합 완료 → acc30m 버퍼 리셋 스킵(표본 누적 중)
--- [CB] ×2(표본)
15:40:22 2026-08-18 15:40:22 [INFO] SYSTEM: [CB] 일간 리셋 완료
15:40:22 2026-08-18 15:40:22 [INFO] SYSTEM: [CB] 일간 리셋 완료
--- [SchedForceExit] ×1(표본)
15:11:21 2026-08-18 15:11:21 [INFO] SYSTEM: [SchedForceExit] 15:11 점검 — status=FLAT engine=0ct broker_cached=0ct bar_pass=1회 → 청산 대상 없음(정상)
--- [Shutdown] ×2(표본)
15:40:23 2026-08-18 15:40:23 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (daily_close)
15:40:38 2026-08-18 15:40:38 [INFO] SYSTEM: [Shutdown] 정상 종료 플래그 기록: C:\Users\82108\PycharmProjects\futures\data\_exit_normally (auto_shutdown)
--- 자동 종료 ×5(표본)
15:40:23 2026-08-18 15:40:23 [INFO] SYSTEM: [Notify] ℹ️ [15:40:23] [미륵이] 🏁 미륵이 일일 마감 완료 — 자동 종료 예정
??:??:?? 15초 후 프로그램 자동 종료
15:40:23 2026-08-18 15:40:23 [INFO] SYSTEM: 자동 종료 예약 — 15초 후 Qt 이벤트 루프 종료
15:40:38 2026-08-18 15:40:38 [INFO] SYSTEM: [System] 자동 종료 실행
```

### `logs/20260818_SIGNAL.log`
```
--- ConfFloorGuard ×2(표본)
09:05:58 2026-08-18 09:05:58 [WARNING] SIGNAL: [ConfFloorGuard] 자동진입 하한 도달 불가 — 보정기 출력상한 0.3528 < 필요 0.3920 (conf_floor=0.330, min_conf=0.392, span=0.0059). 이 상태에서는 어떤 신호도 자동진입 하한을 넘을 수 없다.
10:29:58 2026-08-18 10:29:58 [INFO] SIGNAL: [ConfFloorGuard] 하한 도달 가능 복구 — 출력상한 0.3936 ≥ 필요 0.3730
--- ConstOut ×8(표본)
09:36:58 2026-08-18 09:36:58 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
09:37:58 2026-08-18 09:37:58 [INFO] SIGNAL: [ConstOut] 3m 상수 출력 해소 → 앙상블 복귀
11:30:58 2026-08-18 11:30:58 [WARNING] SIGNAL: [ConstOut] 3m 상수 출력 5분 감지 (range=0.0000 dir=+1) → 앙상블 제외
11:30:59 2026-08-18 11:30:59 [INFO] SIGNAL: [RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m const_out=['3m'] (섀도 기록만, 정책 무변경)
--- WeightCollapse ×8(표본)
09:07:59 2026-08-18 09:07:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=35.3% grade=X regime=NEUTRAL [WeightCollapse]
09:10:59 2026-08-18 09:10:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:13:58 2026-08-18 09:13:58 [INFO] SIGNAL: [Ensemble] dir=+0 conf=85.0% grade=X regime=NEUTRAL [WeightCollapse]
09:16:59 2026-08-18 09:16:59 [INFO] SIGNAL: [Ensemble] dir=+0 conf=84.4% grade=X regime=NEUTRAL [WeightCollapse]
--- 기동 복원 ×7(표본)
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: GAP_OPEN  0.670 → 0.434
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: OPEN_VOLATILE  0.600 → 0.422
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: STABLE_TREND  0.540 → 0.413
08:40:43 2026-08-18 08:40:43 [INFO] SIGNAL: [DynMC] 기동 복원: LUNCH_RECOVERY  0.570 → 0.409
--- 안전망 ×8(표본)
09:07:59 2026-08-18 09:07:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['3m'])
09:10:59 2026-08-18 09:10:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:13:58 2026-08-18 09:13:58 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m'])
09:16:59 2026-08-18 09:16:59 [WARNING] SIGNAL: [WeightCollapse] 실질 가중합 0 (1연속) — 활성기대=['3m', '5m'] 중 미배포=['3m', '5m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m', '5m'])
```

### `logs/20260818_LEARNING.log`
```
--- 축퇴 ×8(표본)
08:41:05 2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00073 auc=0.477 out_max=0.3753 (기준 auc<0.53 and span<0.020, 기저율=0.3750 n=80) → 보정 미적용, raw 통과
08:41:05 2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 하한 도달불가 — out_max=0.2002 < conf_floor=0.3300 (span=0.00040 auc=0.536 out_max=0.2002, 기저율=0.2000 n=80) → 보정 미적용, raw 통과. 축퇴 가드와 별개 사유다(auc/span은 정상 범위).
08:41:05 2026-08-18 08:41:05 [WARNING] LEARNING: [Calibration] 축퇴 감지 — span=0.00033 auc=0.529 out_max=0.2002 (기준 auc<0.53 and span<0.020, 기저율=0.2000 n=85) → 보정 미적용, raw 통과
08:41:05 2026-08-18 08:41:05 [INFO] LEARNING: [Calibration] 축퇴 해소 — span=0.00064 auc=0.556 out_max=0.2004 (n=90) → 보정 재적용
```

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/20260818_TRADE.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 2 | 08:41:14 [INFO] 저장 상태가 어제 데이터 — 무시 |
| 14:00 | 장중 후반 · 장중 재학습 | 1 | 13:59:59 [INFO] 미니선물 실효잔고=50,000,000(실제잔고=50,585,496) 기본리스크=1,500,000 신뢰도배수=0.6 레짐배수=0.8 안전배수=1.00(정상) → 2계약 (최소=1) [ConfShad… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:22 [INFO] 일간 리셋 완료 |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260818_WARN.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 6 | 08:41:21 [WARNING] request_futures_balance 호출 account=333044256 | caller=_balance(account_no) |  File "C:\Users\82108\PycharmPro… |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 1 | 09:01:00 [WARNING] _tick_header 간격 3516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 2 | 09:01:00 [WARNING] _tick_header 간격 3516ms — 메인 스레드 블로킹 발생 | pipe_elapsed=0 watchdog_alerted=[] |
| 10:00 | 장중 초반 | 3 | 09:55:58 [WARNING] 5분 누적 수익률 -0.467% (임계 ±0.294%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 12:00 | 장중 중간점 | 4 | 11:55:58 [WARNING] 5분 누적 수익률 -0.483% (임계 ±0.481%) → D_PRICE_MOMENTUM 트리거 (쿨다운 20분) |
| 14:00 | 장중 후반 · 장중 재학습 | 2 | 13:58:59 [WARNING] acc30m 단계 전환: NORMAL → WATCH (acc=30.0%) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 1 | 15:40:22 [WARNING] mc-conf 괴리: 최근 5거래일 평균 진입후보 56분/일 < 하한 60분 — 금일 94분. |

- 이 로그 생존구간: 08:41 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/20260818_SYSTEM.log`

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 90 | 08:40:47 [INFO] 활성화 | file=logs\crash_fault.log PID=21660 | 행감지=30s all_threads=True |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 134 | 08:49:22 [INFO] alive ticks=1242 code=A0569 close=1117.84 |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 197 | 08:54:07 [INFO] #2000 code=A0569 raw_time=85409 parsed=08:54:09 price=1122.44 vol=1 bid1=1122.10 ask1=1122.40 flag=49 side=BU… |
| 10:00 | 장중 초반 | 194 | 09:54:04 [INFO] #29600 code=A0569 raw_time=95406 parsed=09:54:06 price=1138.44 vol=1 bid1=1138.44 ask1=1138.50 flag=50 side=S… |
| 12:00 | 장중 중간점 | 183 | 11:54:15 [INFO] #77500 code=A0569 raw_time=115416 parsed=11:54:16 price=1091.02 vol=1 bid1=1091.08 ask1=1091.38 flag=50 side=… |
| 14:00 | 장중 후반 · 장중 재학습 | 178 | 13:54:10 [INFO] #111900 code=A0569 raw_time=135411 parsed=13:54:11 price=1095.96 vol=1 bid1=1095.96 ask1=1096.04 flag=50 side… |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 168 | 15:04:11 [INFO] #132800 code=A0569 raw_time=150411 parsed=15:04:11 price=1073.70 vol=1 bid1=1073.60 ask1=1073.68 flag=49 side… |
| 15:18 | 안전망 청산 (STEP 8 5단계 마지막) | 136 | 15:12:01 [INFO] #135800 code=A0569 raw_time=151202 parsed=15:12:02 price=1079.90 vol=1 bid1=1079.80 ask1=1079.92 flag=49 side… |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 35 | 15:34:21 [INFO] futures via CpSysDib.CpSvrNew7221 supported=True nets={individual:+408,foreign:+498,institution:-976} |
| 15:47 | _EOD 재학습(py310_64) 완료 (이 로그 생존구간 밖)_ | 0 | — |

- 이 로그 생존구간: 08:40 ~ 15:40

**매분 루프 커버리지 09:00~15:10: 371/371분 (100.0%)**

**08:55~15:12 구간 10분 이상 공백: 0건**

### `logs/20260818_SIGNAL.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 08:40 | 런처 기동 (Mireuk_batch) | 55 | 08:45:21 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0294) → identity(0,1) 강제 (FLAT 100% 방지) |
| 08:55 | 매크로 수집 → 레짐 판정 + 실시간 구독 사전 시작 | 97 | 08:49:58 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0352) → identity(0,1) 강제 (FLAT 100% 방지) |
| 09:00 | 정규장 개장 · 매분 루프 시작 | 173 | 08:54:58 [WARNING] 1m CORE 'ofi_norm' raw_std≈0(0.0401) → identity(0,1) 강제 (FLAT 100% 방지) |
| 10:00 | 장중 초반 | 226 | 09:55:58 [WARNING] 1m 'macro_vix' scale=0.0016 → floor=0.10 적용 (z-score 폭발 방지) |
| 12:00 | 장중 중간점 | 251 | 11:54:58 [WARNING] 1m 극단 z-score 1개 피처 감지 (|z|>4) — 스케일러 노후화 또는 이상 데이터 의심 |
| 14:00 | 장중 후반 · 장중 재학습 | 108 | 13:57:00 [WARNING] CORE VWAP ✗ → 강제 X등급 (pass_count=7, group=short) | VWAP pos=-2.000 need >0 (LONG) bear_exh=0.00 |
| 15:10 | **오버나이트 금지 — 강제 청산** (절대원칙 1) | 65 | 15:04:59 [WARNING] 실질 가중합 0 (1연속) — 활성기대=['3m'] 중 미배포=['3m'] → flat_score=1.0 안전망 발동 (active_horizons=['1m', '3m']) |
| 15:40 | 자가학습 일일 마감 + SHAP 피처 심사 | 3 | 15:40:22 [INFO] daily reset complete |

- 이 로그 생존구간: 08:40 ~ 15:40

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 1.8MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### [3] Degraded 선제차단이 S5(1,630ms) 주도 — 08-14 S0 사슬의 새 변종 (P1 — 신규)
### [4] 수집기 §5 손익 집계가 레그 단위라 오늘 실현손익을 59% 과소 표기 (P2 — 재발·확대)
### [5] ProfitGuard L1-Trail 당일 래치 — 세션의 30%가 구조적 무거래로 확정 (관측)
### [6] 장전 점검이 13:44:15에 돌았고 리포트 산출물이 없다 (P2 — O-7 답 확정)
### [7] 오탐 정정 — 재인용 금지 대상에 준해 다룰 것
### [8] 손절 준수율 — 오늘 표본은 깨끗하다 (관측)
### [9] 사이저 압력 — binding 게이트는 `tox(0.70)`가 지배적 (관측)
### [검증]
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
에 따라 확정 결론 금지.**
**우선순위 이번 주** — 발동일이 드물어 오늘 데이터를 놓치면 다음 표본이 7주 뒤다.

### [6] 장전 점검이 13:44:15에 돌았고 리포트 산출물이 없다 (P2 — O-7 답 확정)

`evidence_MW0601-20260818_pre.md` 생성 시각 **13:44:15 KST**, 리포 경로
`/sessions/sharp-gallant-volta/...`(본 세션과 다른 세션). 대응하는
`MW0601-20260818-점검리포트-pre.md`는 **부재** — 다이제스트만 있다.

**O-7 답**: 장전 점검은 08:57±5분에 돌지 **않았다. 4시간 47분 늦었다.**
장 시작 후에 도는 장전 점검은 "오늘 거래할 자격이 되는가"라는 질문 자체가 성립하지 않는다
(이미 7건 진입·청산 완료 후).

**G-3(점검 세션 동시 실행 직렬화) 재발** — 08-17 pre/intra/post 3세션 겹침에 이어
오늘 pre(13:44)·intra(13:49) 5분 간격. `dev_memory` 동시 append 유실 위험
(MW0602 `483d41a` 전례). 기등록 항목이므로 신규 안건으로 올리지 않는다.

### [7] 오탐 정정 — 재인용 금지 대상에 준해 다룰 것

- **수집기 §11 "미커밋 변경 455건"은 사실이 아니다.** 리눅스 샌드박스 CRLF 아티팩트.
  473차 후속2 §5가 이미 확정(`git diff --ignore-cr-at-eol` 기준 10파일).
  **샌드박스 실행 시 §2·§11의 미커밋 건수 신뢰 금지.** `NEXT_TODO` F-5 등록됨.
- **수집기 §11 6·7번(커버리지 78.2% / 13:50~15:10 81분 공백)은 계산 산물**이다 —
  13:49에 돌려 미래 구간을 분모에 넣었다. 경과분 대비 공백 **0**.
- **수집기 §11 9번(5초 초과 4건 — CB⑤ 발동 여부)** — CB⑤ 미발동이 정상. G-3 기등록.
- **CLAUDE.md STEP 3 "GBM 배치 재학습(30분마다)"이 코드에 없다** — 오늘도 장중 재학습 5회가
  전부 ConstOut 트리거(간격 114/54/33/33분). **08-14 F-8로 이미 등록됨. 신규 아님.**
- **`[Calibration]` WARNING 154건** — 기동 워밍업 스윕. 일별 평탄(08-10 157 / 08-11 148 /
  08-12 145 / 08-13 141 / 08-14 144 / 08-17 143 / 08-18 154). `NEXT_TODO` G-4 등록됨.
- **CB② 연속 손절 카운터 2회** — `CB_CONSEC_STOP_LIMIT=9999`라 **카운터만 오르고 정지 안 하는
  것이 정상**이다(한시예외).
- **`WeightCollapse` 61건(약 21%)** — CLAUDE.md 기술 범위(21~22%) 안. conf 평균 집계 제외 대상.
- **설정 불변식 `미발견` 5종** — 브랜치 격차(320/315)가 원인, 473차 후속2 확정. 주간회의 안건.

### [8] 손절 준수율 — 오늘 표본은 깨끗하다 (관측)

유일한 패: 13:06:59 SHORT 2ct @1092.67 → 13:08:37 손절1차 조기축소 −77,139원
→ 13:19:39 하드스톱(틱) −168,139원.
의도 손절폭 `stop_dist=3.21pt`(`[DBG-F8] stop=1095.75`) 대비 실현 −3.33pt = **초과율 1.04배**.
틱스톱 슬리피지 1095.88→1096.00 = **0.12pt**.
417차가 지목한 "진입수량 vs 손절폭 초과비율" 축은 오늘 표본(1건)에서는 문제없다.
⚠ **n=1 — 확정 결론 금지.**

### [9] 사이저 압력 — binding 게이트는 `tox(0.70)`가 지배적 (관측)

471차 후속6 G-1의 `[SizerMatch]`가 정상 동작한다. 오늘 전량 `sizer=3계약 → actual=2계약`이며
binding은 `tox(0.70)` 다수 · `meta(0.66)` 1 · `hurst(0.50)` 1.
`meta=1.00(raw0.50·무정보폴백→중립)` 표기도 정상 출력된다(431차 무정보 폴백 중립화).
`MAX_CONTRACTS=3` 상한에 걸린 건은 **0건**(사이저 출력 자체가 최대 3).
[28] `sizing_inversion_watch` 표본 적립 중 — **1거래일이므로 판정 금지**.

### [검증]

코드 변경 0건 · 커밋 0건 · 라이브 DB 쿼리 0건. 근거는 전량 `logs/` 텍스트다.
손익 집계는 **포지션 단위**로 수행했고(계측 4원칙 ①) 엔진 값(`engine=+661,668원`)과
원 단위까지 교차검증했다. 레그 단위 수치(+269,334원)는 **인용하지 말 것**.
conf 절대값을 CLAUDE.md 구 "확률 판단 기준" 표에 대보지 않았다(2026-07-31 스케일 전환).
표본 1거래일 채널([28]·G-1·G-5)에는 **확정 결론을 내지 않았다**(313차 원칙).

```

</details>

### dev_memory/NEXT_TODO.md — 948.9KB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 완료 처리 (475차)
## 2026-08-18 (MW0601 475차 — 장중 점검 / intra) 신규 항목
### Fix — 08-18 장 마감 후 적용 (장중 금지: 라이브 프로세스 PID 21660 가동 중)
### 고도화
### 오늘 장후에 답이 나오는 것
### 완료 처리
### 기한
### 커밋 대기 (475차 — 본 세션은 커밋하지 않았다)
```

미완료 체크박스 **1379건** (끝에서 30건)
```
- [ ] **O-1 EOD 재학습 완주 확인 (오늘 15:45~16:10)** — `logs/retrain_eod_20260818.log`가
- [ ] **O-2 `session_state.json` P8 키 재생성 (오늘 EOD 직후)** — 오늘 13:33 스냅샷 기준
- [ ] **O-3 P8 키 잔존 (08-19 08:41 기동 후)** — 재생성됐다면 기동 후에도 남는가.
- [ ] **F-1H 하트비트 1일차 (오늘 15:10)** — `[SchedForceExit] … bar_pass=N회` 출현.
- [ ] **F-4M 스키마 마이그레이션 1일차 (오늘 EOD 후)** — 471차 후속2 신규 행.
- [ ] **F-1R 15:10 강제청산 리허설 — ⚠ 사용자 실행 필요.** 15:05~15:09 모의 1계약 진입 후
- [ ] **커밋 대기 — 475차 산출물 4종(코드 변경 0건).**
- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **11일** 남음. 오늘 `9999` 유지 확인.
- [ ] **브랜치 격차 처분을 주간회의 안건으로** — `v9-dev`↔`origin/dev` = **320/315**(기존).
- [ ] **실전전환 ⑨ TOX-SEVERE-SPREAD 처분** — 473차 F-8 Phase A `INSUFFICIENT`(ETA 7.1개월).
- [ ] **F-1 수집기 §5 포지션 단위 집계 (P1) — 08-18 장후 점검 *종료 후* 적용** —
- [ ] **F-2 CB③ HALT 비활성 사실을 문서 3곳에 등재 (P1) — 08-14 잔여 F-2·F-8과 같은 커밋** —
- [ ] **F-3 `_tick_header` 크기 기준 적신호 + 포지션 보유 여부 인라인 (P1) — F-1과 한 커밋** —
- [ ] **F-4 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` 체리픽 심사에 S5 변종 첨부 (P2)** —
- [ ] **G-1 ProfitGuard L1-Trail 기회비용 섀도 채널 (이번 주 — 우선)** —
- [ ] **G-2 `_tick_header` 블로킹 경고에 포지션 상태 인라인 (이번 주 — F-3보다 먼저)** —
- [ ] **G-3b `RouterHealth` 섀도 → 판정 채널 승격 검토 (26주 WFA 주기)** —
- [ ] **O-A F-1H 하트비트 1일차 (08-17에서 이월)** — 15:10:00~05에 `[ForceExitPass]` →
- [ ] **O-B `[Bias⚠] 1m FL편향` 15:10까지 추이** — 13:47 67% → 13:51 **75%**(적중 30%, 6/20).
- [ ] **O-C FP-CRITICAL PSI 값이 file 로그에 남는가** — 당일 출력 **0건**(08-14도 동일).
- [ ] **O-D broker(+685,000) − engine(+661,668) = 23,332원의 정체** — 수수료·미결제 시차로
- [ ] **O-E ProfitGuard L1 차단 82건 중 A/B등급 반사실 손익** —
- [ ] **O-F `_tick_header` ≥20,000ms 재발 + 포지션 보유 중 발생 여부** —
- [ ] **O-G IntradayRegime 전이 건수** — 08-14 19회 / **08-18 18회**. G-5 5거래일 누적 **2일차**,
- [ ] **O-H 장전 점검 실행 시각** — 오늘 **13:44:15**(08:57 대비 4시간 47분 지연, 리포트 부재).
- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **11일** 남음. 오늘 `9999` 유지 확인.
- [ ] `docs/정기점검/매일점검/MW0601-20260818-점검리포트-intra.md` (신규)
- [ ] `docs/정기점검/매일점검/evidence_MW0601-20260818_intra.md` (신규)
- [ ] `docs/정기점검/매일점검/evidence_MW0601-20260818_pre.md` (신규 — pre 세션 산출물)
- [ ] `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md` (append)
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
 섀도 → 판정 채널 승격 검토 (26주 WFA 주기)** —
  `VALIDATION_CAMPAIGN`에 `router_constout_overlap`(`min_samples=20`, `min_days=10`) 등록만.
  집행(라우터가 ConstOut 호라이즌 회피)은 판정 후에.
  근거: 08-18 `[RouterHealth] 라우터가 ConstOut 활성 호라이즌 선택 — chosen=3m` **3회**
  (11:30:59·12:24:59·12:25:59). 오늘 실해 없음(그 3분 진입 0).
  **오늘 3회는 표본이 아니다.** 목적은 "섀도로만 기록 중" 상태의 **종료 조건 정의** —
  종료 조건이 없으면 TOX-SEVERE-SPREAD가 한 달간 죽은 섀도였던 경로에 그대로 올라탄다.
  ⚠ 기존 G-3(점검 세션 직렬화)과 다른 항목이다 — ID 충돌 주의.

### 오늘 장후에 답이 나오는 것

- [ ] **O-A F-1H 하트비트 1일차 (08-17에서 이월)** — 15:10:00~05에 `[ForceExitPass]` →
  `[TimeExit]` → `[ExitAttempt]` 출현하고 `[SchedForceExit] … 안전망 발동`(ERROR) **미출현**.
  15:11에 ERROR가 뜨면 1차 경로가 다시 죽은 것. **F-1R(리허설)·F-4M(스키마 1일차)도 이월 중.**
- [ ] **O-B `[Bias⚠] 1m FL편향` 15:10까지 추이** — 13:47 67% → 13:51 **75%**(적중 30%, 6/20).
  `record_horizon_fl_bias()`의 CRITICAL 기준은 `streak ≥ 30분`인데 오늘 `[CB-FLBias]` **0건**.
  streak≥30분에도 미출현이면 **P5 경보 경로 점검**.
- [ ] **O-C FP-CRITICAL PSI 값이 file 로그에 남는가** — 당일 출력 **0건**(08-14도 동일).
  차단은 비활성이나 계산·file 로그는 유지돼야 한다(CLAUDE.md 한시예외 3).
  **0건이면 P1 승격** — 셰도 모니터링 사망은 TOX-SEVERE-SPREAD와 같은 패턴이다.
- [ ] **O-D broker(+685,000) − engine(+661,668) = 23,332원의 정체** — 수수료·미결제 시차로
  추정하나 **미검증**. 장후 3원 대사에서 확정(계측 4원칙 ② — 미측정 ≠ 0).
- [ ] **O-E ProfitGuard L1 차단 82건 중 A/B등급 반사실 손익** —
  **1거래일 표본, 판정 금지. 적립만**(313차).
- [ ] **O-F `_tick_header` ≥20,000ms 재발 + 포지션 보유 중 발생 여부** —
  포지션 보유 중 1건이라도 나오면 **P0**. 매 거래일 관측.
- [ ] **O-G IntradayRegime 전이 건수** — 08-14 19회 / **08-18 18회**. G-5 5거래일 누적 **2일차**,
  3일치 더 필요. ⚠ 오늘도 진입 7건 전부 `레짐배수=0.8` 고정이라 실해 미확인.
- [ ] **O-H 장전 점검 실행 시각** — 오늘 **13:44:15**(08:57 대비 4시간 47분 지연, 리포트 부재).
  08-19에 08:57±5분 복귀 여부. **세션 직렬화 G-3도 재발** — pre 13:44 / intra 13:49.

### 완료 처리

- [x] **O-8 08-18 08:40 자동 기동 여부** → **정상.** `launcher_20260818_084001_2415.log`,
  `08:41:00 [System] 미륵이 초기화`, `08:41:21 [Session] 재기동 #1 | cause=STARTUP`.
- [x] **O-7 장전 점검이 08:57±5분에 도는지** → **아니다.** 13:44:15 실행, 리포트 미산출.
  후속은 O-H로 승계.

### 기한

- [ ] **CB② 복원 08-29 주간회의 상정** — 기한 **11일** 남음. 오늘 `9999` 유지 확인.
  **표본 진전 있음** — 연속 손절 카운터 2회 기록(13:08:37 · 13:19:39).

### 커밋 대기 (475차 — 본 세션은 커밋하지 않았다)

- [ ] `docs/정기점검/매일점검/MW0601-20260818-점검리포트-intra.md` (신규)
- [ ] `docs/정기점검/매일점검/evidence_MW0601-20260818_intra.md` (신규)
- [ ] `docs/정기점검/매일점검/evidence_MW0601-20260818_pre.md` (신규 — pre 세션 산출물)
- [ ] `dev_memory/DECISION_LOG.md` · `dev_memory/NEXT_TODO.md` (append)
- ⚠ 08-17 세션의 미커밋 10파일(`learning/prediction_buffer.py` · `utils/db_utils.py` ·
  `config/settings.py` 등)도 **여전히 대기 중**이다 — 함께 정리할 것.

```

</details>

### dev_memory/CURRENT_STATE.md — 529.4KB · 마지막 갱신 2026-08-17 17:53

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

(없음)

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 39개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-intra.md` | 39.4KB | 08-18 14:00 |
| `docs/정기점검/매일점검/MW0601-20260818-점검리포트-pre.md` | 45.5KB | 08-18 13:59 |
| `docs/정기점검/매일점검/evidence_MW0601-20260818_intra.md` | 61.8KB | 08-18 13:49 |
| `docs/정기점검/매일점검/evidence_MW0601-20260818_pre.md` | 60.5KB | 08-18 13:44 |
| `docs/정기점검/매일점검/dailycheck_prompt.txt` | 12.5KB | 08-17 17:47 |
| `docs/정기점검/매일점검/MW0601-20260817-점검리포트-post.md` | 42.5KB | 08-17 17:08 |
| `docs/정기점검/매일점검/MW0601-20260817-점검리포트-intra.md` | 27.5KB | 08-17 17:06 |
| `docs/정기점검/매일점검/MW0601-20260817-점검리포트-pre.md` | 35.4KB | 08-17 16:57 |

### `docs/정기점검/금요일점검` — 51개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/금요일점검/weekly_prompt.txt` | 1.8KB | 08-16 15:46 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260814.md` | 4.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260814.json` | 2.9KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260814.md` | 26.2KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260814.json` | 34.4KB | 08-14 15:50 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_report_20260814.md` | 163.4KB | 08-14 15:49 |
| `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260814.json` | 83.5KB | 08-14 15:49 |
| `docs/정기점검/금요일점검/MW0602/exit_expectancy_map_20260810.md` | 1.8KB | 08-14 07:47 |

## 11. 자동 적신호 (출발점이지 결론이 아니다)

1. 설정 불변식 `MODEL_LABEL_STATE_UNLOCK_ENABLED` = `None` (기대 `True`) — 468차 G-1. 사이즈 제한 해제를 이벤트→상태 판정으로. **라이브 미검증** — `사이즈 축소 ×0.6` 0건 확인 전까지 CLAUDE.md ⑧ 해제 금지
2. 설정 불변식 `PRE_RETRAIN_DONE_BY_EOD_ENABLED` = `None` (기대 `True`) — 468차 F-1. EOD 완료로 `_pre_retrain_done` 해제 — G-1의 동반 스위치
3. 설정 불변식 `ZONE_ENTRY_BAN_ENFORCE` = `None` (기대 `False`) — 462차 P1-a. 🔴 True면 라이브 진입이 즉시 준다. 위반 7건이 오히려 흑자(+596,858원)라 [53] 채널 판정 전까지 False 유지
4. 설정 불변식 `ZONE_ENTRY_BAN_SHADOW_ENABLED` = `None` (기대 `True`) — 462차 P1-a 섀도. 집행과 무관하게 위반 계측은 항상 켜져 있어야 한다
5. 설정 불변식 `PIPE_LATENCY_EXCLUDE_MODEL_SWAP` = `None` (기대 `True`) — 462차 P2. 모델 교체 구간을 CB⑤ 판정용 지연에서만 차감(원값은 `raw=…ms`로 존치)
6. 청산 7건 중 하드스톱·손절 계열 **7건(100%)** — 손절 준수율 확인 필요
7. 사이저 최대 3계약 → 실제 진입 최대 2계약 — 게이트 배수에 눌림 (sizing_inversion_watch 대상)
8. 메인 스레드 블로킹 5초 초과 **5건** (최대 37875ms) — `CB_PIPE_PAUSE_MS=5_000` 기준 초과. CB⑤ 발동 여부 확인
9. `logs/20260818_WARN.log`: **ConstOut** 6건(표본)
10. `logs/20260818_SYSTEM.log`: **ConstOut** 8건(표본)
11. `logs/20260818_SIGNAL.log`: **WeightCollapse** 8건(표본)
12. `logs/20260818_SIGNAL.log`: **ConstOut** 8건(표본)
13. `logs/20260818_LEARNING.log`: **축퇴** 8건(표본)
14. 미커밋 변경 458건
15. 상태 파일 `data/_exit_normally` 없음 — 정상 종료 플래그. **기동 시 소비되므로 재기동했다면 없는 것이 정상**이다. 로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20260818*.log` (Windows) / `grep 강제청산 logs/*20260818*.log`*