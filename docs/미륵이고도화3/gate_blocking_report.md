# Gate Blocking Report — 30일 게이트 차단 전수 집계 (v9 Phase 0)

- Generated at: 2026-08-23 17:56:18
- 조회 구간: 최근 30일 (2026-07-24 17:56:18 ~)
- 전체 분봉 판정 수: 6937건 (게이트 스냅샷 보유: 6937건)
- 등급 분포: {'X': 5705, 'C': 1232}
- auto_entry=1232건, entry_final_ok=358건, entry_executed=157건

## 겹별(마지널) 게이트 통과율 — 낮은 순

- `p4_cvd_ofi_demoted`: 0.0296
- `hurst_soft_block_noop`: 0.0442
- `hurst_soft_block_applied`: 0.051
- `qty_ok`: 0.0901
- `mode_filter_ok`: 0.1044
- `cb3_restricted_at_entry`: 0.2486
- `hurst_ok`: 0.568
- `conf_raw_ge_min_conf`: 0.5743
- `cal_degenerate`: 0.65
- `conf_raw_ge_floor`: 0.9146
- `atr_ok`: 0.9403
- `new_entry_time`: 0.9467
- `exit_cooldown_ok`: 0.949
- `open_gap_ok`: 0.9775
- `conf_raw`: 0.9866
- `reverse_clamp_ok`: 0.9937
- `ecb_observe_ok`: 0.9968
- `cb_normal`: 0.997
- `armistice_ok`: 0.9997
- `hc_ok`: 1.0
- `broker_sync_ok`: 1.0
- `cooldown_ok`: 1.0
- `integrity_ok`: 1.0
- `bar_volume_ok`: 1.0
- `intraday_ok`: 1.0
- `kill_switch_ok`: 1.0
- `cal_out_max`: 1.0

## 결합 통과율 vs 이론적 곱셈값 (AND 직렬 붕괴 검증)

- 게이트 27겹, 이론적 곱셈 통과율(독립 가정): 0.0
- 실측 결합 통과율(전 게이트 True): 0.001
- collapse_ratio(실측/이론): 41089.1021 (1에 가까울수록 게이트 간 독립에 가까움 — 1보다 많이 낮으면 서로 다른 시점에 번갈아 차단해 결합 통과율이 이론보다도 더 붕괴한다는 뜻)

## 최종 차단 원인 분류 (entry_block_reason 실측 문구 기준)

- 차단없음: 4225건
- 등급X_기타: 1504건
- 청산후쿨다운: 202건
- 포지션보유중(평가생략): 191건
- JointGateBlock: 190건
- 사이저수량0: 181건
- 시가이격과다: 151건
- 마감전신규진입금지: 131건
- 게이트강등_기타: 43건
- ATR고변동성과대: 40건
- ATR변동성부족: 28건
- 게이트강등_Meta: 17건
- ReverseClamp: 11건
- conf_floor미달: 9건
- 게이트강등_Toxicity: 6건
- 거래소CB_관망: 3건
- 점심휴식구간(8_time): 3건
- Degraded최소신뢰도: 2건

## 체크리스트 등급 X 세부 원인 (checklist_reason)

- FLAT: 3549건
- pass 1/9: 1688건
- RegimeOverride: 389건
- VWAP강제X: 307건
- σ미수집: 87건
- conf↓: 68건
- Coherence↓: 31건
- 조건부구간: 25건
- pass 6/9: 6건
- ATR저변동: 4건
- pass 5/9: 1건

---

## 해석 가이드

- `gate_marginal_pass_rate` 하위 항목이 실제 병목 게이트 후보.
- `collapse_ratio` < 1이면 "각 게이트는 그럭저럭 통과하는데 서로 다른 시점에 번갈아 차단해 결합 통과율이 곱셈보다도 낮다" — L3 소프트 게이트(점수 합산) 전환의 정량적 근거.
- `block_reason_dist`의 최빈 항목이 §5(구현계획) 우선 개선 대상.

