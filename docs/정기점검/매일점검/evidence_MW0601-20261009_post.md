# 미륵이 증거 다이제스트 — 2026-10-09 / POST

- 생성 2026-10-09 16:17:40 KST · PC **MW0601** (`claude (override)`)
- 리포 `/sessions/rcw-01wyqsnqqhzprzprkjad1r4s/mnt/futures`
- 점검 범위: pre, intra, post (장전=pre / 장중=intra / 장후=post)
- 날짜 토큰: `20261009` · `2026-10-09` · `261009` · `1009`
- 🟦 **휴장일** — KRX 휴장일(`config/krx_holidays.py` 등록). 매매·매분 파이프라인이 없는 것이 정상이므로 장중 로그 침묵(FZ-6)·장후 조기종료(480차) 적신호를 **끈다**. 목록이 틀렸을 수 있다(2026-09-28 오등록 전례) — 이 판정이 의심되면 파일을 확인하라.
- 보관정책: **무기한 · git 추적**(2026-08-18 실측 — `docs/정기점검` 전체 3.4MB, 소급 인용 꼬리 182일=26주 WFA, 재생성은 원본 로그 생존에 종속). 정리 수단은 `--prune-days`이며 **기본 꺼져 있다**

## 1. 당일 파일 인벤토리 (날짜 토큰 자동탐색)

총 **11개** 파일 · 11개 그룹

| 그룹(파일명 패턴) | 개수 | 경로 | 크기 | 최종기록 |
|---|---|---|---|---|
| `claude_resume_{DATE}.log` | 1 | `logs/claude_resume_20261009.log` | 402B | 10-09 14:59 |
| `eod_retrain_done_{DATE}.txt` | 1 | `data/eod_retrain_done_20261009.txt` | 238B | 10-09 16:13 |
| `peter_feed_push_{DATE}.log` | 1 | `logs/peter_feed_push_20261009.log` | 513B | 10-09 16:15 |
| `retrain_eod_{DATE}.log` | 1 | `logs/retrain_eod_20261009.log` | 27.4KB | 10-09 16:13 |
| `retrain_intraday_20260624_{DATE}56.log` | 1 | `logs/retrain_intraday_20260624_100956.log` | 4.6KB | 06-24 10:10 |
| `retrain_intraday_20260626_{DATE}55.log` | 1 | `logs/retrain_intraday_20260626_100955.log` | 4.6KB | 06-26 10:10 |
| `retrain_intraday_20260708_{DATE}56.log` | 1 | `logs/retrain_intraday_20260708_100956.log` | 4.6KB | 07-08 10:10 |
| `retrain_intraday_20260716_{DATE}01.log` | 1 | `logs/retrain_intraday_20260716_100901.log` | 4.5KB | 07-16 10:09 |
| `retrain_intraday_20260724_{DATE}58.log` | 1 | `logs/retrain_intraday_20260724_100958.log` | 4.5KB | 07-24 10:10 |
| `retrain_intraday_20260728_{DATE}42.log` | 1 | `logs/retrain_intraday_20260728_100942.log` | 4.5KB | 07-28 10:10 |
| `shindong2_{DATE}.log` | 1 | `logs/shindong2_20261009.log` | 461B | 10-09 15:55 |

## 2. 코드·커밋 상태

- HEAD `7235337` · 브랜치 `v9-dev` · 미커밋 102건 · 실질 변경 14건 · 코드(.py) 0건 · EOL 파생 0건 (추적변경 14 · 미추적 88 · 삭제 12 · core.autocrlf=미설정) · 인덱스락 없음
  - 실질 변경 파일: `dev_memory/DECISION_LOG.md`, `dev_memory/NEXT_TODO.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_metrics_20260913.json`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/cvd_anchor_report_20260913.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_metrics_20260911.json`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260904.md`, `docs/정기점검/금요일점검/MW0601/featureset_health_report_20260911.md`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260904.json`, `docs/정기점검/금요일점검/MW0601/validation_campaign_metrics_20260911.json` … 외 2개
  - 락 자가점검: 이 수집 실행은 락을 만들지 않았다
  - git 호출 기록: 7회 · 타임아웃 0 · 실패 1 · 락 생성 구간 0 · 최장 3.5초(`git status --porcelain`)
    - `git config --get core.autocrlf` → fail · 0.0초 · 락 없음→없음
```
M dev_memory/DECISION_LOG.md
 M dev_memory/NEXT_TODO.md
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
?? dev_memory/_tmp_append_decisionlog_followup_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261001.md
?? dev_memory/_tmp_append_nexttodo_20261002.md
?? dev_memory/_tmp_append_nexttodo_20261006_post.md
?? dev_memory/_tmp_append_nexttodo_20261007_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_intra.md
?? dev_memory/_tmp_append_nexttodo_20261008_pre.md
?? dev_memory/_tmp_append_nexttodo_20261009_intra.md
?? docs/미륵이고도화3/4상태_모니터링목록_검증딥다이브_MW0601-20261004.md
?? docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md
?? docs/미륵이고도화3/나스닥선물_1분봉_수집방안_및_Cybos거울상_검토_MW0601-20261002.md
?? docs/미륵이고도화3/먼스리_월위클리_옵션흐름_선물추종선행_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_전일보유_맥점되돌림_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자포지션_수집가능성_MW0601-20261002.md
?? docs/미륵이고도화3/옵션_행사가별_투자자흐름_맥점관계_MW0601-20261002.md
?? docs/미륵이고도화3/외인선물순매수_수집현황_조사_MW0601-20261002.md
?? docs/미륵이고도화3/위클리먼스리_선물추종_주체비중_일별_MW0601-20260921-20261002.md
?? docs/미륵이고도화3/피터2/live/
… 외 62건
```

**당일(2026-10-09) 커밋**
(경계 기준: KST +0900 고정 · 수집 환경 로컬 시간대 +0000 — ⚠ KST 아님, 경계는 보정됨)
```
(당일 커밋 없음 — 커밋 가능 상태였음)
```

**최근 커밋 12건**
```
7235337 [MW0601] CREON HTS 자동기동: Cybos Plus → 미륵이 → CREON 순서 보장
7240653 [MW0601] 672차 후속2: dev 배포 기록(a18b016)
5bfeadd [MW0601] 672차 후속: 신동2 프롬프트.txt 10/8 추가분(학습 사이클 지시 원문)
8ea6f6e [MW0601] 672차: 신동2 학습 사이클 — 예측→실행→평가·반성→레슨런→개선 예측 (evaluate·feedback·lesson·trend·brief)
73cffd1 [MW0601] 671차 후속: 장후 자동조치 기록 — F-10 · G-1 결과 · 1-4 원인 단서
dd37273 [MW0601] 671차 후속: 장후 자동조치 — F-10 · 장전 고도화2 · 장후 G-1
780b2de [MW0601] 668차 후속6: 피터2 진입 전량 증발 — kill_switch.is_active property 호출 수정
4b94f9f [MW0601] 668차 후속5: 피터2 수집 — X 검색 한도 소진·고아 스크립트·NEW 로그 오기 수정
a0f179f [MW0601] 668차 후속4: 피터2 차트 갱신 메서드를 DashboardAdapter 에도 — 첫 기동 AttributeError
d5b183f [MW0601] 668차 후속3: 피터2 MW0602(dev) 독자 개발 가이드
2ecda7f [MW0601] 668차 후속2: 피터2 논의 정리 문서 — 장중 수집 개선 · 추종 거래
200432c [MW0601] 668차 후속: 피터2 「손절 2회 당일 정지」 해제 — PETER2_DAILY_STOP_LIMIT=0
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

### 당일 마커·리포트 파일 (전문)

완료 마커(`*_done_*.txt`)는 **있으면 그 단계가 끝났다는 뜻**이고, 없으면 안 끝났거나 안 돌았다는 뜻이다. 어느 쪽인지는 로그로 구분한다.

**`data/eod_retrain_done_20261009.txt`** — 238B · 10-09 16:13:26
```
completed: 2026-10-09 16:13:26
rows: 19744
cols: 97
phase2_fallback: false
horizons_replaced: 6/6
t_load_s: 25.7
t_retrain_s: 176.7
t_total_s: 202.8
daily_close_seen: false
wait_dc_timeout: true
daily_close_stalled: unmeasured
```

_다이제스트 대상 8/10개 (중요도순). 제외: `shindong2_20261009.log`, `claude_resume_20261009.log`_

### `logs/retrain_eod_20261009.log` — 27.4KB · 192행 · 최종 16:13:27

- 형식 평문 · 시각 인식 192행 · WARNING=11, INFO=181

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-10-09 15:50:02,759 [INFO] EOD_RETRAIN: =======================================================
2026-10-09 15:50:02,759 [INFO] EOD_RETRAIN: 미륵이 EOD 재학습 시작
2026-10-09 15:50:02,759 [INFO] EOD_RETRAIN: Python : 3.10.20 64-bit
2026-10-09 15:50:02,759 [INFO] EOD_RETRAIN: sklearn: 1.0.2
2026-10-09 15:50:02,759 [INFO] EOD_RETRAIN: numpy  : 1.26.4
  …
2026-10-09 16:13:27,015 [INFO] SIGNAL: [ScalerFloor] 30m 'quality_investor_age_sec' scale=0.0381 → floor=0.15 적용 (z-score 폭발 방지)
2026-10-09 16:13:27,016 [INFO] SIGNAL: [ScalerFloor] 30m 'toxicity_atr_stress' scale=0.1008 → floor=0.20 적용 (z-score 폭발 방지)
2026-10-09 16:13:27,019 [INFO] SIGNAL: [ScalerRefresh] ts=16:13 trigger=E_EOD retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화 n=500 bars horizons=['1m', '3m', '5m', '10m', '15m', '30m'] elapsed=0.05s
2026-10-09 16:13:27,022 [INFO] EOD_RETRAIN: [P8] 스케일러 재적합 완료 n=500봉 elapsed=0.05s horizons=['1m', '3m', '5m', '10m', '15m', '30m']
2026-10-09 16:13:27,023 [INFO] EOD_RETRAIN: [P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료
```

</details>

**WARNING — 태그 6종 (상위 6)**

| tag | 건수 | 최초 | 최종 | 대표 |
|---|---|---|---|---|
| `GuardFair` | 6 | 16:10:40 | 16:12:34 | 1m 판정 불가 — 오염 홀드아웃 1850봉 중 1850봉(100%)이 현행 학습구간 (현행 cutoff=2026-10-08 14:38:00 ≥ 홀드아웃 시작=2026-09-30 12:51:00) | 사이드카=현행이 홀드아웃 학습함 — train_end=2026-10-08 14:38 >= holdout_start=2026-09-30 12:51 (source=eod) — 판정 보류 (구모델 pkl mtime=2026-10-08… |
| `WaitDC` | 1 | 16:10:03 | 16:10:03 | daily_close() 20분 대기 타임아웃 — pkl 경합 위험 있으나 강제 진행 |
| `OptionFlowFresh` | 1 | 16:10:03 | 16:10:03 | 결손 4일 — 2026-09-29(최신봉 15:34), 2026-09-30(최신봉 15:34), 2026-10-01(최신봉 15:34), 2026-10-02(최신봉 15:34) | 기준 7거래일. ⚠ 지난 날짜는 복구 불가(7222 는 당일만 준다). 원인 점검: 예약작업 \Mireuk\Mireuk_OptionFlowBackfill_1605 의 LastTaskResult · logs\<YYYYMMDD>_OPTION_BACKF… |
| `BackfillFilter` | 1 | 16:10:13 | 16:10:13 | ] learning.feature_epoch_mask: [BackfillFilter] Phase1 백필 오염행 20479/44078 제외 (418차 결정 1) — 남은 23599행 |
| `UnitMismatch` | 1 | 16:10:13 | 16:10:13 | ] learning.feature_epoch_mask: [UnitMismatch] Phase1 압축 이전 단위 거래일 1446/23599행 제외 (559차 P1'-2) — 남은 22153행. 이 행들을 넣으면 수급 8키 스케일러 std 가 5.7만 배로 뛴다. |
| `RegimeFingerprint` | 1 | 16:13:26 | 16:13:26 | 백필 0행 제외 — 필터가 무효일 수 있다. 19744행 전수가 마커(0.3±1e-06)와 불일치. X.dtype과 허용오차를 확인할 것(424차: float32 회귀). |

**채널** — `EOD_RETRAIN`×65, `LEARNING`×62, `SIGNAL`×55, `FEAT_REG`×6

**컴포넌트 상위 15** — `ScalerFloor`×48, `WaitDC`×42, `Retrain`×21, `EOD_RETRAIN`×14, `RF`×9, `FeatureReg`×6, `Retrain-Timing`×6, `GuardShadow`×6, `GuardFair`×6, `GuardClean`×6, `ModelLive`×6, `Model`×6, `RegimeFingerprint`×4, `LEVELS`×2, `P8`×2

### `logs/retrain_intraday_20260626_100955.log` — 4.6KB · 39행 · 최종 10:10:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-06-26 10:09:55,449 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-26 10:09:55,449 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-06-26 10:09:55,449 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-26 10:09:55,449 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_168e49de.json
2026-06-26 10:09:58,598 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-06-26 10:10:36,422 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.41s | old_acc=0.2796)
2026-06-26 10:10:36,426 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-06-26 10:10:36,426 [INFO] LEARNING: [Retrain] 완료 | 37.8초 | 성공=6/6 호라이즌
2026-06-26 10:10:36,428 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 41.0s 데이터=20000행
2026-06-26 10:10:36,430 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_168e49de.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260624_100956.log` — 4.6KB · 39행 · 최종 10:10:27

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-06-24 10:09:56,797 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-24 10:09:56,797 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-06-24 10:09:56,797 [INFO] RETRAIN_INTRADAY: ==================================================
2026-06-24 10:09:56,797 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_4c977b7b.json
2026-06-24 10:09:58,199 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-06-24 10:10:27,699 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.37s | old_acc=nan)
2026-06-24 10:10:27,703 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-06-24 10:10:27,703 [INFO] LEARNING: [Retrain] 완료 | 29.5초 | 성공=6/6 호라이즌
2026-06-24 10:10:27,705 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 30.9s 데이터=20000행
2026-06-24 10:10:27,706 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_4c977b7b.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260708_100956.log` — 4.6KB · 39행 · 최종 10:10:25

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-08 10:09:56,495 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-08 10:09:56,496 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-08 10:09:56,496 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-08 10:09:56,496 [INFO] RETRAIN_INTRADAY: 파라미터: force=False intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_49e7844f.json
2026-07-08 10:09:58,416 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-08 10:10:25,848 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.50s | old_acc=nan)
2026-07-08 10:10:25,852 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-08 10:10:25,852 [INFO] LEARNING: [Retrain] 완료 | 27.4초 | 성공=6/6 호라이즌
2026-07-08 10:10:25,854 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 29.4s 데이터=20000행
2026-07-08 10:10:25,855 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_49e7844f.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260716_100901.log` — 4.5KB · 39행 · 최종 10:09:36

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-16 10:09:01,735 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-16 10:09:01,736 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
2026-07-16 10:09:04,490 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-16 10:09:36,601 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.43s | old_acc=0.2874)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-16 10:09:36,604 [INFO] LEARNING: [Retrain] 완료 | 32.1초 | 성공=6/6 호라이즌
2026-07-16 10:09:36,606 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 34.9s 데이터=20000행
2026-07-16 10:09:36,607 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_de5f6a4a.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260724_100958.log` — 4.5KB · 39행 · 최종 10:10:28

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-24 10:09:58,762 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-24 10:09:58,762 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-24 10:09:58,763 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-24 10:09:58,763 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_5d07d3f3.json
2026-07-24 10:10:00,150 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-24 10:10:28,402 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.44s | old_acc=0.3053)
2026-07-24 10:10:28,405 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-24 10:10:28,405 [INFO] LEARNING: [Retrain] 완료 | 28.3초 | 성공=6/6 호라이즌
2026-07-24 10:10:28,407 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 29.6s 데이터=20000행
2026-07-24 10:10:28,409 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_5d07d3f3.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/retrain_intraday_20260728_100942.log` — 4.5KB · 39행 · 최종 10:10:17

- 형식 평문 · 시각 인식 39행 · INFO=39

<details><summary>첫 5행 / 끝 5행</summary>

```
2026-07-28 10:09:42,031 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-28 10:09:42,031 [INFO] RETRAIN_INTRADAY: 미륵이 장중 재학습 시작 | Python 3.10.20 64-bit
2026-07-28 10:09:42,031 [INFO] RETRAIN_INTRADAY: ==================================================
2026-07-28 10:09:42,031 [INFO] RETRAIN_INTRADAY: 파라미터: force=True intraday=True result_path=C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ebf52d74.json
2026-07-28 10:09:44,564 [INFO] LEARNING: [Retrain] 배치 재학습 시작 (weeks_back=26, phase2=False, intraday=True)
  …
2026-07-28 10:10:17,035 [INFO] LEARNING: [Retrain] 30m 교체 (intraday — CV 없음 | fit=1.47s | old_acc=0.3416)
2026-07-28 10:10:17,038 [INFO] LEARNING: [Retrain] 장중 경량 모드: RF 학습 스킵 (기존 RF 모델 유지)
2026-07-28 10:10:17,039 [INFO] LEARNING: [Retrain] 완료 | 32.5초 | 성공=6/6 호라이즌
2026-07-28 10:10:17,041 [INFO] RETRAIN_INTRADAY: 재학습 완료 | 35.0s 데이터=20000행
2026-07-28 10:10:17,043 [INFO] RETRAIN_INTRADAY: 결과 JSON 저장: C:\Users\82108\PycharmProjects\futures\data\_gbm_result_ebf52d74.json
```

</details>

**채널** — `LEARNING`×27, `RETRAIN_INTRADAY`×6, `FEAT_REG`×6

**컴포넌트 상위 15** — `Retrain`×20, `RETRAIN_INTRADAY`×6, `FeatureReg`×6, `Retrain-Timing`×6, `CUSUM`×1

### `logs/peter_feed_push_20261009.log` — 513B · 9행 · 최종 16:15:26

- 형식 평문 · 시각 인식 2행 · INFO=2, PLAIN=7

<details><summary>첫 5행 / 끝 5행</summary>

```
============================================================
[2026-10-09 16:15:00.97] peter_feed_push 시작 (cwd=C:\Users\82108\PycharmProjects\futures)
[INFO] python: "C:\Users\82108\AppData\Local\Programs\Python\Launcher\py.exe" -3
[INFO] 3.12.3
futures                  OK    index.lock 없음
  …
futures                  OK    index.lock 없음
변경 없음 — 새 커밋을 만들지 않았다.
푸시 완료 -> origin/peter-feed @ f2cbe70ea
futures                  OK    index.lock 없음
[2026-10-09 16:15:26.26] peter_feed_push 종료 rc=0
```

</details>

**컴포넌트 상위 15** — `-`×9

## 5. 거래일 요약 — 오늘 무엇을 했는가

_거래일 패턴이 하나도 안 잡혔다. 로그 문구가 바뀌었을 수 있다 — `config/dailycheck_targets.json` 의 `day_summary_patterns` 를 확인하라._

## 6. 항상 인용하는 패턴 (안전장치·크래시·성능·학습)

(해당 패턴 없음 — 안전장치가 조용했거나, 계측이 없거나. 어느 쪽인지 원본으로 구분할 것)

## 7. 타임라인 앵커 · 매분 루프 커버리지

### `logs/retrain_eod_20261009.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|
| 15:47 | EOD 재학습(py310_64) 완료 | 15 | 15:50:02 [INFO] ======================================================= |

- 이 로그 생존구간: 15:50 ~ 16:13

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/retrain_intraday_20260626_100955.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|

- 이 로그 생존구간: 10:09 ~ 10:10

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/retrain_intraday_20260624_100956.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|

- 이 로그 생존구간: 10:09 ~ 10:10

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### `logs/retrain_intraday_20260708_100956.log` _(보조 로그 — 매분 루프 대상 아님)_

| 시각 | 앵커 | 창 내 | 대표 |
|---|---|---|---|

- 이 로그 생존구간: 10:09 ~ 10:10

_이 로그는 매분 루프 로그가 아니므로 커버리지·공백 판정을 하지 않는다._

### 로그 종료시각 — 직전 5거래일 대조 (SYSTEM)

| 일자 | 종료시각 | 출처 |
|---|---|---|
| 20261008 | 15:43 | 로그 본문 |
| 20261007 | 20:26 | 로그 본문 |
| 20261006 | 15:47 | 로그 본문 |
| 20261005 | 09:41 | 로그 본문 |
| 20261003 | 18:32 | 로그 본문 |
| **중앙값** | **15:47** | 기준선 |
| **오늘 20261009** | **—(미측정)** | 오늘 SYSTEM 로그 없음 |

- ⚠ 오늘 종료시각 미측정 — **0으로 읽지 말 것**(계측 4원칙 ②).


## 8. dev_memory

### dev_memory/DECISION_LOG.md — 3.5MB · **오늘 갱신됨**

최근 헤딩 8개:
```
### 증상
### 원인
### 결정
### Why
### How to apply
### 검증
### 병행 세션
## 2026-10-09 (MW0601 674차 — 장중 점검, 673차 장전 절 이어받음)
```

<details><summary>dev_memory/DECISION_LOG.md 꼬리 2.5KB</summary>

```
 사람이 사후에 바로 알 수 있게 함.

### 검증
- F-1: 다음 거래일(10/12) `logs/shindong2_20261012.log`에서 동일 `UnicodeEncodeError` 재현 여부로 확인. 라이브 미검증 — 적용 후 최소 1영업일 관찰 필요.
- G-1: 미구현.

### 병행 세션
- 장중 세션(`rcw-01lue2z5ptfjqd5dkzhbjxw3`)이 생성한 `evidence_MW0601-20261009_intra.md`를 열어 읽음 — 결론 동일(휴장일), 판정 충돌 없음. 그 세션이 별도 리포트 본문을 쓴다면 이 장전 절(§1 1-1~1-3·이월 항목)을 반영해야 함.

## 2026-10-09 (MW0601 674차 — 장중 점검, 673차 장전 절 이어받음)

**증상**: 오늘(한글날 공휴일) 미륵이 메인 엔진이 하루 종일 미기동. 장전·장중 두 예약작업(`Mireuk premarket check`·`Mireuk intraday check`)이 각각 원래 예정 시각(08:57 KST·12:25 KST)보다 6시간36분·3시간8분 늦게, 서로 19초 차이로 거의 동시에 발동함(`list_triggers` 조회 — `fired_at` 2026-10-09T06:33:17Z·06:32:58Z).

**원인**: 확정 아님(313차 원칙 — 판정 보류). `logs/claude_resume_20261009.log`에 07:21·14:17·14:58 세 차례 "데스크톱 재기동 감시" 깨어남 기록이 있고, 매번 "Claude desktop already running — nothing to do"로 끝나 앱 프로세스 자체의 생사 문제는 아닌 것으로 보임. 가설: 이 PC-클라우드 세션 간 원격 기기 브리지 연결이 어느 시점에 끊겼다가 14:58~15:3X KST 사이 복구되어, 그 사이 쌓인 두 예약이 복구 직후 한꺼번에 처리됨. 사람의 PC·네트워크 상태 직접 확인 필요.

**결정**: 이 세션(장중)은 장전 절이 이미 생성한 `MW0601-20261009-점검리포트.md`에 append만 하고, 장전 절 본문은 고치지 않음. 장전 절의 이상점 1-1(병행 발화)·1-2(신동2 gate 재발)·1-3(미커밋 96건), 그리고 이월 항목 O-p1·O-t1·O-t2는 전부 "🔄 지속(변화 없음 또는 이월 유지)"로 처분하고, 1-1에만 위 `claude_resume` 로그와 정확한 `fired_at` 간격(19초)을 보강 근거로 추가함. 새 이상점 번호는 발급하지 않음(신규 0건).

**Why**: 두 점검 세션이 거의 동시에 돌면서도 서로 다른 파일(`evidence_..._pre.md`/`evidence_..._intra.md`)에만 쓰고 본 리포트 파일(`MW0601-20261009-점검리포트.md`) 쓰기는 장전 세션이 먼저 선점해, append 경쟁(2026-08-26 사고 유형)이 실제로는 일어나지 않았음. 장중 세션은 작성 직전 파일 크기(21001바이트)를 기록해 두고, append 직후 다시 크기를 확인해(21001→28679바이트, 기대한 7678바이트 증가와 일치) 제3자 동시 쓰기가 없었음을 확인함.

**추가 — 전송 사고(이 세션 자체 결함, 사용자 조치 불필요)**: append 과정에서 큰 텍스트를 base64로 인코딩해 Read 도구로 읽은 뒤 그 내용을 device_bash 명령에 다시 옮기는 과정에서, 모델(이 세션)이 그 base64 문자열을 옮겨적다 1바이트를 오기해 "결론으로"가 "결론으각에"로 깨지는 사고가 있었다. `device_stage_files`로 파일을 그대로 가져와 로컬 원본과 바이트 단위로 diff해 정확한 위치(딱 1곳)를 찾아내 바로잡았고, 재확인(`device_stage_files` 재실행 + diff)으로 완전 일치를 확인했다. **Fix(적용 완료)**: 앞으로 이런 대용량 한글 텍스트를 device에 쓸 때는 base64를 모델이 직접 옮겨적지 말고, `device_commit_files`(바이너리 전송, 모델이 재입력하지 않음)로 작은 임시 파일을 올린 뒤 device_bash에서 `cat tmpfile >> target`으로 합치는 방식을 쓴다 — 이 방식은 Korean 텍스트를 모델이 다시 입력하지 않으므로 같은 사고가 구조적으로 발생하지 않는다.

**How to apply**: 적용 완료(리포트 파일 수정 완료, 위 설명대로). 앞으로 이 세션류(미륵이·마흐디·메시아 일일점검 등)에서 대용량 한글 콘텐츠를 device에 쓸 때는 `device_commit_files` + `cat >> ` 패턴을 기본으로 쓰는 것을 권고(스킬 문서에는 아직 반영하지 않음 — 다음 스킬 개정 시 반영 검토).

**검증**: `device_stage_files`로 최종 리포트 파일을 다시 가져와 로컬 원본(장중 절 소스)과 바이트 단위 완전 일치(`tail == mine`) 확인함(2026-10-09 06:48 UTC경). 라이브 미검증 항목 없음(장전·장중 둘 다 정적 리포트 작성 작업이라 재현성 검증 불필요).

```

</details>

### dev_memory/NEXT_TODO.md — 1.6MB · **오늘 갱신됨**

최근 헤딩 8개:
```
## 2026-10-07 (MW0601 668차 — 피터2 실시간 추종 신설)
## 2026-10-08 (MW0601 669차 — 장전 점검)
## 2026-10-08 (MW0601 670차 — 장중 점검)
## 2026-10-08 (MW0601 671차 — 장후 점검)
## 2026-10-08 (MW0601 672차 — 671차 후속 장후 자동조치)
## 2026-10-08 (MW0601 672차 — 신동2 학습 사이클)
## 2026-10-09 (MW0601 673차 — 장전 점검)
## 2026-10-09 (MW0601 674차 — 장중 점검)
```

미완료 체크박스 **3080건** (끝에서 30건)
```
- [ ] F-12: `main.py:3991` `_peter2_execute()` — `self.kill_switch.is_active()` → `self.kill_switch.is_active`(소괄호 제거, `KillSwitch.is_active`가 `@property`라 호출 불가). 피터2 폴링이 오늘 6회 중 5회 `TypeError`로 중단(…
- [ ] 1-1 원인 조사(장후 이월, 669차에서 이미 등록): 개장 전 08:48·08:54 2단 자동 재시작 원인 — 런처 스크립트 + `main.py` 종료 경로 그레핑 선행 조사. 장중 재확인 결과 09:00 이후 재발 0건.
- [ ] O-p1 판정: 10/9 장전 점검에서 "개장 전 2단계 재시작 재현 여부" 반드시 확인·판정(보류 중 이월분).
- [ ] **F-15(사람, 승인 필요)**: `MIREUK_BROKER_CHANNEL=CYBOS` 환경변수 명시 고정 — 단, 적용 전에 오늘 왜 CREON이 선택됐는지(env var 오설정 vs 로그 mtime 역전) PC에서 먼저 확인할 것. `echo %MIREUK_BROKER_CHANNEL%` + `C:\CREON\STARTER\ncstarte…
- [ ] **F-16(사람, 승인 필요)**: `scripts/commission_rate_recon.py --backfill`로 10-08 거래(id 622~630) `commission_rate_used`·`commission_krw`·`net_pnl_krw` CYBOS 요율 소급 정정. 적용 전 `data/db/trades.db` 백업.
- [ ] **F-17(사람, 검토)**: 런처의 "15:10 이후 종료 시 AUTO-RESTART 금지" 로직에 "daily_close/P8 미완료 상태에서의 조용한 종료"를 구분하는 예외 경로 설계 검토 — 1-1·1-5 원인이 먼저 확정돼야 설계 방향을 정할 수 있음(선행 조건: 1-1 원인조사).
- [ ] **1-1 원인조사(장전부터 3세션째 이월)**: 개장전 08:48·08:54 2단 자동 재시작 + 오늘 오후 15:38:49 3번째 유사 사례(1-5) — 런처 스크립트 종료사유 3분류 로깅 + Windows 이벤트 뷰어/작업 관리자 종료 기록, 이 세션(리눅스 샌드박스)이 접근 불가해 **사람이 PC에서 직접 확인 필요**.
- [ ] **O-t1(신규)**: 10/9 장전 `trades.db`에서 `commission_rate_used`가 CYBOS(`9.8104e-05`)로 정상 복귀했는지 1차 확인 — 최우선 확인 항목.
- [ ] **O-t2(신규)**: 1-1·1-5와 같은 "원인불명 조용한 종료"가 10/9 이후에도 재현되는지 누적 관찰 — 재현되면 단일 결함으로 승격 검토.
- [ ] O-p1·1-2·663-1~4·F-1(538-4)·F-2·G-3 — 전부 지속, 변화 없음(기존 승인/판정 대기, 중복 기재 생략).
- [ ] **F-15 원인 단서 확보 → 승인만 남음**: 10-08 실측 `C:\CREON\STARTER\ncstarter.log` mtime **13:05:40** > `C:\Daishin\...` **08:35:49**, `MIREUK_BROKER_CHANNEL` 사용자·시스템 모두 미설정. ⇒ mtime 역전(CREON 기동)이 원인. 런처에 `…
- [ ] 기존 실패 테스트 2건(이번 변경 무관): `test_498::test_every_recon_log_is_registered`(`CybosInvestor` 대사 로그 RECON_INVENTORY 미등록 — `collection/cybos/investor_data.py`·`main.py`) · `test_457::test_db_fallback_c…
- [ ] 이월(하루 3건 상한): 장중 고도화1(수집기 §5 EKS 관망→해제→재학습 한 줄 요약) · 장중 고도화2(`[Peter2]` 태그 적신호 「메인 엔진 영향 없음」 자동 분류).
- [ ] F-11(종료 사유 3분류 로깅) — 위치 미특정, 조사 선행(C 보류). 장후 고도화2(마감 경고 휴대폰 알림)는 Slack 보류 결정으로 미착수.
- [ ] **672-1** 10/12(월) 장전: `brief` 로 레슨·피드백·추이 읽고 장전계획 **live + legacy 두 건** 남기기(새 월물·3일 연휴 갭 → 수급·맥점·벽 재확인).
- [ ] **672-2** 10/12 장후: `evaluate` → `feedback`(잘한 점/잘못한 점/개선점/레슨) → `trend`. 첫 「개선 − 기존」 짝 1건 적립.
- [ ] **672-3** 후보 레슨 승격 심사(적용 3회·적중 우세): L9·L12·L13 이 10/12–10/14 에 3회 적용되면 10/14 장후 `lesson set --status 적용중`.
- [ ] **672-4** 헤드리스 예약작업 첫 실행(10/12 08:52·15:55)에서 새 명령이 허용 패턴 안에서 실제로 돌았는지 `logs/shindong2_20261012.log` 확인.
- [ ] **672-5** 추이가 5일 쌓이면 사다리 학습 블록의 창 표기(최근 5일)가 의미를 갖는다 — 그때 10/20일 창도 패널에 올릴지 판단.
- [ ] **F-1(1-2 재발 대응)**: `scripts/shindong2_run.ps1`의 `conda run python scripts/shindong2_live.py …` 호출(특히 `gate`)에 `$env:PYTHONIOENCODING="utf-8"; $env:PYTHONUTF8="1"` 추가. 적용 전 다른 서브커맨드 호출부에 이미 적용돼…
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
```

<details><summary>dev_memory/NEXT_TODO.md 꼬리 2.5KB</summary>

```
용 3회·적중 우세): L9·L12·L13 이 10/12–10/14 에 3회 적용되면 10/14 장후 `lesson set --status 적용중`.
      실패 우세면 딥다이브(L11 과 L3 의 균형이 1순위 주제 — 추세장 되돌림 대기 vs 이탈추종).
- [ ] **672-4** 헤드리스 예약작업 첫 실행(10/12 08:52·15:55)에서 새 명령이 허용 패턴 안에서 실제로 돌았는지 `logs/shindong2_20261012.log` 확인.
      실패하면 `shindong2_run.ps1` 의 `$allowed` 가 아니라 **conda 출력 인코딩**(`−` 문자) 쪽을 먼저 의심(10/6 전례).
- [ ] **672-5** 추이가 5일 쌓이면 사다리 학습 블록의 창 표기(최근 5일)가 의미를 갖는다 — 그때 10/20일 창도 패널에 올릴지 판단.

## 2026-10-09 (MW0601 673차 — 장전 점검)

- [ ] **F-1(1-2 재발 대응)**: `scripts/shindong2_run.ps1`의 `conda run python scripts/shindong2_live.py …` 호출(특히 `gate`)에 `$env:PYTHONIOENCODING="utf-8"; $env:PYTHONUTF8="1"` 추가. 적용 전 다른 서브커맨드 호출부에 이미 적용돼 있는지 grep으로 먼저 확인(함정①). 장후 적용 권고.
- [ ] **G-1(1-1 병행 발화 대응)**: 점검 리포트 append 직전 세션별 생존 마커(`<PC>-<날짜>.lock`, 타임스탬프 포함, 2시간 초과 시 무시) 도입 검토 — 오늘 장전·장중 예약이 12초 차이로 병행 발화했으나 결과 우연히 무해(둘 다 휴장일 판정). 거래일 재발 시 리포트 append 순서 꼬임 위험.
- [ ] **O-p1(2026-10-07 669차 등록, 재이월)**: 개장전(08:48·08:54) 2단 자동 재시작 재현 여부 — 10/9는 휴장일이라 관측 기회 없음. **10/12(월) 장전으로 이월.**
- [ ] **1-1(2026-10-07 669차 등록, 재이월)**: 위와 같은 원인조사(런처 종료사유 3분류 로깅 선행 조사, 사람이 PC에서 직접 Windows 이벤트 뷰어/작업 관리자 확인 필요) — 10/9 관측 기회 없음. **10/12 장전으로 이월.**
- [ ] **O-t1(2026-10-08 672차 등록, 재이월)**: `trades.db`의 `commission_rate_used`가 CYBOS(`9.8104e-05`)로 정상 복귀했는지 확인 — 10/9는 거래 자체가 없어 확인 대상 없음, 08:45 이후 라이브 DB 전수 스캔 금지 구간이기도 해 이번 세션 미실행. **10/12 거래 발생 이후 장후 점검으로 이월.**
- [ ] **O-t2(2026-10-08 672차 등록, 재이월)**: "원인불명 조용한 종료" 재현 누적 관찰 — 10/9는 시스템 미기동으로 관측 대상 없음. **10/12로 이월.**
- [ ] 미커밋 변경 96건(실질 12건) 정리 — `docs/정기점검/금요일점검/MW0601/` 삭제 12건이 FIFO 보관정책(`VALIDATION_REPORT_KEEP_WEEKS=4`) 소행인지 사람 확인 필요. `git add .` 금지, 경로 명시 add.
- [ ] 앱 저장 스킬(mireuk-daily-check) 사본 갱신 — 저장소 정본 `rev: 2026-09-07`(538차) 대비 앱 사본이 `rev: 2026-08-26e`(499차)로 낡음. `save_skill overwrite: true` 필요(이 PC, MW0601 한정 — 함정③).

## 2026-10-09 (MW0601 674차 — 장중 점검)

- [ ] O-i1 (신규, 다음 거래일 판정): 2026-10-12(월) 장전·장중 예약작업이 각자 정해진 시각 근처(±30분)에 발동하는지 확인. 지연 없으면 1-1 ✅해소, 재발하면 `logs/claude_resume_*.log` 감시 스크립트·원격 기기 브리지 연결 상태 원인조사 착수.
- [ ] G-2 (고도화, 이번 주): `collect_evidence.py` §2(병행 세션 확인)에 "예약작업 예정 시각 대비 실제 fired_at 지연"을 자동으로 찍는 계측 추가(현재는 수집기가 `list_triggers` API에 접근하지 않아 수동 대조만 가능). 지연이 30분 이상이면 §11 자동 적신호로 승격.
- [ ] (절차 개선, 비승인 필요 — 기술부채) 대용량 한글 텍스트를 리눅스 샌드박스 세션에서 device에 쓸 때 base64를 모델이 직접 옮겨적는 방식은 1바이트 오기 위험이 있음(2026-10-09 674차에서 실제 발생·즉시 발견·수정함). 앞으로 `device_commit_files` + `cat >> ` 패턴으로 바꿀 것 — DECISION_LOG 674차 항목 참조.
- [x] O-p1·O-t1·O-t2(10/8 이전 등록) — 장중 절에서도 지속 확인, 10/12로 이월 유지(장전 673차 판정과 동일, 추가 처분 없음).

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

(없음)

### `data/session_state.json` — 기동 마커 스냅샷 (날짜 토큰 없어 인벤토리 미포함)

- 파일 최종 기록: **10-09 16:13:27**

| 키 | 값 | 수집 대상일(2026-10-09)과 일치 |
|---|---|---|
| `date` | 2026-10-08 | **아니오** |
| `p8_last_success_date` | 2026-10-09 | 예 |
| `eod_retrain_ok_date` | 2026-10-09 | 예 |

> 「아니오」거나 「키 없음」이면 그 마커를 남기는 경로(EOD 재학습·P8 재적합)가 어제 것을 못 남겼거나 오늘 아침 누군가 덮었다는 뜻이다 — 2026-09-03 이상점 1-1 계열.

- **PreRetrain 우회 확인**: — PreRetrain 로그 없음 — **미측정** (08:55 이전 수집이거나 그날 미기동)

### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **(없음)** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **행 없음** — 그날 파이프라인이 한 번도 안 돌았다 |
| `raw_candles` 당일 행수 | 0 |
| `session_bars` 당일 행수 | 0 (기대 411) |

- 라이브 로그 대조: `logs/20261009_SYSTEM.log` 의 `[BarGap]` 줄
  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). **한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.

> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: 결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` 줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.


### 프로세스 종료 3축 대사 (620차)

| 축 | 상태 |
|---|---|
| 런처 로그(기동 PID·재시작 분류) | **미측정** — 그날 런처 로그 없음 — 런처를 안 썼거나 파일명 규칙이 바뀌었다 |
| `crash_fault.log`(정상종료 기록) | **그날 행 없음** — 롤링으로 잘렸을 수 있다. 「정상종료 없었음」으로 읽지 말 것 |
| `crash_fault.log`(`Windows fatal exception` — 살아남은 것 포함) | **그날 행 없음** — 「0건」으로 읽지 말 것 |
| Windows WER(네이티브 예외) | **미측정** — 비Windows 플랫폼 — WER 이벤트 로그가 없다 |

- 런처 축이 없어 PID 대사를 할 수 없다. **「크래시 0건」이 아니라 「재지 못했다」**이다.

## 10. 정기점검 리포트 현황

### `docs/정기점검/매일점검` — 211개 (최근 8개)

| 파일 | 크기 | 최종 |
|---|---|---|
| `docs/정기점검/매일점검/MW0601-20261009-점검리포트.md` | 28.0KB | 10-09 15:55 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_pre.md` | 48.6KB | 10-09 15:34 |
| `docs/정기점검/매일점검/evidence_MW0601-20261009_intra.md` | 48.6KB | 10-09 15:34 |
| `docs/정기점검/매일점검/MW0601-20261008-점검리포트.md` | 87.1KB | 10-08 17:30 |
| `docs/정기점검/매일점검/evidence_MW0601-20261008_post.md` | 99.0KB | 10-08 16:18 |
| `docs/정기점검/매일점검/_tmp_append_intra_20261008.md` | 15.9KB | 10-08 12:38 |
| `docs/정기점검/매일점검/evidence_MW0601-20261008_intra.md` | 81.9KB | 10-08 12:27 |
| `docs/정기점검/매일점검/evidence_MW0601-20261008_pre.md` | 64.9KB | 10-08 08:59 |

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

1. (관측) 휴장일 — 거래일 전제 적신호(당일 파일 0개·매분 루프 커버리지·15:10 청산 흔적·완료 마커·진입 0건·장후 조기종료·장중 로그 침묵·dev_memory 갱신·상태 파일)를 생략했다. 인프라 적신호는 그대로 본다
2. 미커밋 변경 102건 (실질 14건 · 코드 0건 · EOL 파생 0건)

---

*요약이지 원본이 아니다. 특정 패턴 전량이 필요하면 원본을 직접 열 것 — 예: `findstr /C:"강제청산" logs\*20261009*.log` (Windows) / `grep 강제청산 logs/*20261009*.log`*