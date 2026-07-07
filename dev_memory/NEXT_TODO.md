# 다음 할 일 목록 — futures (미륵이)

> 검증 필요 항목, 예정된 작업, 알려진 잠재 이슈.

### 완료 처리 규칙
- 완료 시 `[DONE YYYY-MM-DD]` 태그 추가
- DONE 태그 후 1주일 경과 시 삭제

---

## 2026-07-07 (301차) [Hurst 산출 흐름 점검 및 배선 수정]

- [DONE 2026-07-07] **`hurst_override` 배선 + backfill Hurst 공식 통일 +
  shadow_evaluator 경계값 정합 + 죽은 코드 제거** — 상세:
  `dev_memory/SESSION_LOG.md`/`DECISION_LOG.md` 301차 항목.
- [ ] **탈진 레짐 Hurst 우회 라이브 검증** — `main.py:6055-6059`에
  `current_micro_regime == REGIME_EXHAUSTION` 조건 추가. 다음 기동 후
  `[MicroRegime] * → 탈진` 로그가 뜬 분봉에서 Hurst<0.45라도 진입이 차단되지
  않는지 확인. (탈진 레짐 자체가 드물게 발생하므로 며칠간 관찰 필요할 수 있음)
- [ ] **backfill_features.py 재실행 여부 결정** — Hurst 공식을 `calculate_hurst()`로
  통일했으나, 이미 DB에 적재된 과거(2026-04-28 이전 소급 또는 이전
  `--update-features` 실행분) `hurst` 값은 소급 정정되지 않음. 학습 데이터
  일관성이 실제로 문제가 될 만큼 중요하면 `--update-features`로 재실행 검토.

## 2026-07-07 (300차) [루트/docs 문서·스크립트 정리]

- [DONE 2026-07-07] **루트/docs 정리 실행** — `_archive/` 신설 후 완료된 계획·리뷰
  문서·1회성 스크립트 이동, 죽은 중복 파일(`adaptive_kelly.py`/`hurst_exponent.py`/
  `Mouse.py`) 삭제, `backup_pull/` 삭제, `CLAUDE.md`/`README.md`/`AGENTS.md`/`CORE.md`/
  `ENSEMBLE_SIGNAL_UPGRADE_PLAN.md`/`STRATEGY_PARAMS_GUIDE.md` 갱신,
  `MIREUKI_OVERVIEW.md` 재작성. 상세: `dev_memory/SESSION_LOG.md` 300차 항목.
- [ ] **`maitreya_dist` 브랜치 존치 여부 결정** — 배포 계획서(`_archive/docs/
  260629_MAITREYA_DIST_DEPLOYMENT_PLAN.md`)는 아카이브했으나 브랜치 자체는 로컬/
  원격에 그대로 존재. 실제로 안 쓰는 게 맞으면 삭제, 여전히 배포용으로 쓴다면
  `docs/MW0602_SETUP.md`와의 관계를 문서로 명확히 할 것.
- [ ] **`docs/정기점검/PERIODIC_INSPECTION_PLAN.md` 처리 방향 결정** — SQL 기반
  점검 루틴이 실제로 기계적으로 실행된 흔적이 없고, 292/297/298/299차식 수시
  딥다이브 + 검증캠페인(`docs/260705_...`)으로 대체 운영 중인 것으로 보임.
  다음 정기점검 때 자동화할지, 현재 방식을 공식 대체 문서로 재정리할지 결정 필요.

## 2026-07-07 (299차) [docs/MW0601 대조 → EOD 리포터 코드버그 4건 MW0601 수준 구현]

- [DONE 2026-07-07] **③-b(298차 이월) CUSUM ref_mean/ref_std 미보정 수정** —
  298차 ③에서 "`estimate_ref_from_trades()`로 실측 표준편차를 세팅하는 배선이
  있는지 확인 필요"로 남겨뒀던 부분. 확인 결과 배선 자체가 없었음(다른 PC
  MW0601의 독립 딥다이브 문서, `docs/MW0601/`에서 동일 원인 재확인).
  `strategy/param_drift_detector.py`에 `MultiMetricDriftDetector
  .calibrate_from_live_history()` 신설 — `get_drift_detector()` 싱글턴 최초
  생성 시 registry의 실제 라이브 히스토리(daily_pnl/win_rate/profit_factor,
  최대 20일)로 `ref_mean`/`ref_std` 자동 추정. 격리 스크립트 검증: 보정 전
  `ref_mean=0.0/ref_std=1.0`(상시 CRITICAL 유발) → 보정 후 실측 스케일
  반영(`ref_mean=-184,000/ref_std=3,406,422` 예시), 동일 -100만원 손실 입력이
  CRITICAL→CLEAR로 정상화됨을 확인.
- [ ] **③-a(298차 이월, 미해결) CUSUM 인메모리 싱글턴 재기동 리셋** — 298차가
  지적한 디스크 영속화 이슈는 이번 세션 범위 밖, 그대로 남음. 매일 재기동 시
  20거래일 누적이 리셋될 수 있음.
- [DONE 2026-07-07] **PSI 상시 0.000 고정 수정** — `save_training_fingerprint()`
  호출부가 프로덕션 어디에도 없어 `_training`(WFA 학습분포 기준선)이 항상
  비어있고, 그 결과 `update_live()`가 매번 조기 반환해 PSI가 영원히 0.0으로
  고정되던 문제(`docs/MW0601/` 딥다이브로 발견, 이 PC엔 처음 확인). `strategy/
  regime_fingerprint.py`에 `RegimeFingerprint._try_bootstrap_baseline()` 신설
  — `update_live()` 호출 시 `_training`이 비어있고 Live 버퍼가 CORE 3피처
  모두 50개(`_N_BINS×5`) 이상 쌓이면 그 시점 분포를 자동으로 기준선 승격
  (`reset_to_live_baseline()` 재사용). 격리 스크립트 검증: 부트스트랩 전
  `has_training_data=False` → 50개 누적 후 `True`, 동일분포 유지 시 PSI≈0,
  분포를 이동시켜 주입하면 WATCHLIST→ALARM→CRITICAL로 정상 전환 확인.
- [DONE 2026-07-07] **활성 버전 이원화 — 코드 레벨 통일 (298차 DB정리의 후속)**
  — 298차는 `data/db/strategy_registry.db`의 `is_current`만 정정하고, `main.py`
  (라이브 스냅샷 기록)와 `strategy/ops/hotswap_gate.py`(다음 버전 넘버링)가
  여전히 `config.strategy_params.PARAM_HISTORY[-1]`을 별도로 읽는 구조적
  원인은 손대지 않아, 다음 실제 Hot-Swap 때 두 소스가 다시 갈라질 위험이
  남아있었음(`docs/MW0601/`의 독립 딥다이브가 이 코드 레벨 원인까지 지적).
  두 파일 모두 `get_registry().get_current_version()`을 유일한 활성 버전
  소스로 읽도록 통일, `PARAM_HISTORY`는 `hotswap_gate.py`에서 문서화용
  이력으로만 append(`param_optimizer.apply_best()`와 동일 패턴).
- [DONE 2026-07-07] **stuck_exit_flat grade/entry_horizon 소싱 수정** —
  285/286차부터 "미조치"로 남아있던 항목(등급 "?" 버킷의 근본원인). `main.py
  :_ts_resolve_stuck_exit_pending`이 `grade`를 EXIT 주문 dict(`pending`, 항상
  빈값)가 아니라 정상 청산 경로와 동일하게 `self.position`에서 읽도록 수정,
  누락돼 있던 `entry_horizon`도 `self.position`에서 추가.
- [ ] **다음 실거래일 라이브 검증(최우선)** — 다음 기동일 15:40 EOD 리포트에서
  CUSUM/PSI 값이 더 이상 상시 CRITICAL/0.000 고정이 아닌지 실제 확인. §1
  (활성 버전 통일)은 다음 실제 Hot-Swap이 발동해야 회귀 여부를 확인 가능 —
  그 전까지는 코드 리뷰 + 격리 스크립트 검증 수준.
- [ ] **wr/pf DriftDetector ref_std 하한(1.0) 스케일 재검토 (범위 밖, 미해결)**
  — `estimate_ref_from_trades()`의 `max(std, 1.0)` 0-division 가드는 원화
  PnL 스케일을 가정한 것이라, 승률(0~1)/PF(~1) 값엔 과도하게 큰 floor로
  작용해 wr/pf CUSUM이 사실상 항상 과소민감(CLEAR 편향)할 수 있음.
  `docs/MW0601/`에도 언급 없던 부분이라 이번엔 그대로 두었음 — 별도 검토 필요.
- [ ] **docs/MW0601/ 커밋 여부 결정** — 다른 PC(MW0601) 문서를 참고용으로
  복사해온 상태로 현재 untracked. 커밋해서 공유할지, 로컬 참고용으로만
  둘지 결정 필요.

---

## 2026-07-06 (298차 검증) [v1.2 유령버전 버그 수정 후 확인 + UNDERPERFORM 신호 검토]

- [ ] **① UNDERPERFORM 신호 실질 검토(최우선)** — DB 정리 후 처음 드러난 v1.0
  32일 실적: 판정 UNDERPERFORM, 롤링20일 MDD=58.6%(WFA 기준 14.2%). 버그로
  가려져 있던 기간 동안 이 신호가 계속 존재했을 가능성 — 실제 롤백/교체후보
  검토가 필요한지 사람이 직접 판단할 것.
- [ ] **② 다음 EOD(07-07 15:40)에서 정상 동작 확인** — `daily_exporter` 리포트가
  "버전 v1.0 (33일차)"로 정상 증가하는지, `strategy_events`에 v1.0 기준
  액션이 새로 쌓이는지 확인.
- [ ] **③ CUSUM 드리프트 감시 영속화/스케일 결정 (정정: 배선은 이미 있음)** —
  최초 조사에서 "배선 자체가 없다"고 잘못 결론냈다가 정정함(`main.py:8310-
  8325`에 `get_drift_detector().update(daily_pnl=...)` 실호출 존재, 멀티라인
  호출이라 grep이 놓쳤었음). 진짜 남은 문제 둘: (a) `MultiMetricDriftDetector`
  가 인메모리 싱글턴이라 매일 재기동 시 CUSUM 누적이 리셋될 수 있음 — 디스크
  영속화(재기동해도 상태 유지) 추가 여부 결정. (b) `ref_std`가 기본 하한(1.0)에
  걸려있어 하루 PnL(수십만~수백만원)이 그대로 거대한 z-score로 환산되는 것으로
  보임(07-01 CRITICAL 1181230.50이 그 증거) — `estimate_ref_from_trades()`로
  WFA 실측 표준편차를 실제로 세팅하는 배선이 있는지 확인 필요.
- [ ] **④ backup_pull/db/strategy_registry.db 처리** — MW0602 pull 절차용
  백업이 수정 전(phantom v1.2) 상태를 그대로 갖고 있음. 해당 절차를 다시 쓸
  계획이면 이 백업도 함께 정리하거나 절차 자체를 건너뛸 것.
- [ ] **⑤ dev-v9(origin/v9-dev) → MW0601 cherry-pick 검토 재개** — 조사 중
  사용자 요청으로 중단. 아래 "dev-v9 cherry-pick 조사 현황" 참고해 이어서
  진행할 것.

### dev-v9 cherry-pick 조사 현황 (미완 — 298차 중단분)

- `origin/v9-dev`는 로컬에 없던 원격 브랜치(이번에 `git fetch`로 확인).
  merge-base는 `5e1426c`(291차).
- v9-dev 상위 6개 커밋(292~297차 — `6cc41eb` `570929a` `00774a2` `de9dba6`
  `bb852f7` `2a2d6c7`)은 dev와 **커밋 메시지가 동일하지만 patch-id는 다름**
  (`git patch-id`로 확인) — 같은 작업을 두 브랜치에 독립적으로 커밋한 것으로
  추정. 이 6개는 **cherry-pick 대상에서 제외**해야 함(이미 dev에 동등한 내용
  존재, 재적용 시 불필요한 충돌만 유발).
- 나머지 v9-dev 전용 커밋 11개(병합커밋 `333ff60` 제외, 실질 10개: `8fc41d7`
  `cd1e0a4` `cddd415` `2412a15` `c16e56f` `5a21dc5` `b727298` `feb69fb`
  `07c0c59` `0857333`, 오래된 순)를 `git worktree add --detach`로 만든 격리
  worktree에서 dev 기준으로 순서대로 dry-run cherry-pick 테스트한 결과:
  - `8fc41d7`에서 최초 충돌 — `.gitignore`, `dev_memory/CURRENT_STATE.md`,
    `dev_memory/NEXT_TODO.md` (양쪽이 독립적으로 이어써온 로그 파일이라
    발생하는 예상된 충돌, 내용만 합치면 되는 사소한 수준)
  - `cd1e0a4` `cddd415` `2412a15` `c16e56f`는 충돌 없이 그대로 적용됨
  - `5a21dc5`에서 `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` 충돌(양쪽이
    같은 문서에 각자 절을 추가 — 수동 병합 필요)
  - `b727298`에서 **`config/settings.py` 충돌** — CB②(사실상비활성) 관련
    설정으로 추정, 실제 설정값 충돌이라 신중한 수동 병합이 필요. **여기서
    사용자 요청("dev_memory update")으로 조사 중단.**
  - `feb69fb`(docs만), `07c0c59`(main.py 62줄 변경 — v9 Track L1/L3 day
    regime engine·soft-gate scoring shadow), `0857333`(LAUNCH_API.bat)은
    아직 테스트 안 함.
- **잠정 결론**: 단순 `git cherry-pick <range>` 일괄 적용은 위험 — 최소
  3개 커밋(`8fc41d7`, `5a21dc5`, `b727298`)에서 수동 충돌 해결이 필요하고,
  미검증 3개(`feb69fb`/`07c0c59`/`0857333`) 중 특히 `07c0c59`가 `main.py`를
  건드려 dev의 292~297차 `main.py` 변경(118줄)과 겹칠 가능성이 있음. 재개
  시 격리 worktree에서 10개 커밋 전부 완주 테스트 후 실제 브랜치(및
  MW0601)에 적용 권장. 테스트에 쓴 worktree(`scratchpad/cherrypick_test`)는
  이미 정리(`git worktree remove`)했으니 재개 시 새로 만들 것.

---

## 2026-07-06 (297차 검증) [진입0 딥다이브 P0 수정 2건 + 재발방지 계측 6종 라이브 검증]

> 앱 미기동 상태에서 소스만 수정 — 전부 라이브 미검증. 다음 기동(0707 장중) 후
> 아래 항목을 순서대로 확인할 것. 상세 배경은
> `docs/진입0/260706_진입0_딥다이브_및_개선구현.md` 참조.

- [ ] **① conf 분포 회복 여부 확인 (최우선 — "모델 문제 vs 데이터 문제" 판별)** —
  295차(K200/VKOSPI MarketEye 수정)·296차(30m 퇴역)가 오늘 장중에는 재기동이
  없어 전혀 반영 안 됐었음. 다음 기동 후 conf 중앙값·p90이 7/3 수준(31.5%→,
  35.5%→39.5%대)으로 회복되는지 확인. 회복 안 되면 모델/캘리브레이션 층 딥다이브.
- [ ] **② FQAdj 완화 실효 확인** — `[FQAdj] fq=... → min_conf ...(완화)` 로그 이후
  실제로 그 완화된 값 기준으로 grade가 산정되는지(`[Checklist] 신뢰도 미달 X% <
  완화된 값`으로 찍히는지, 완화 전 값으로 잘못 찍히면 재발) 확인.
- [ ] **③ CB③-P4 미차단 확인** — `[CB③-P4] RESTRICTED... C등급 차단` 로그가 더 이상
  찍히지 않는지(플래그 False로 비활성했으므로), 대신 `acc30m_stage`/`accuracy_buf`
  누적 자체는 계속되는지(모니터링 단절 여부) 대시보드에서 확인.
- [ ] **④ mc-conf 괴리 경보 정상 동작 확인** — EOD(15:40) 로그에 `[경보] mc-conf
  괴리` 또는 `[mc-conf gap] 정상`이 찍히는지, daily_exporter 리포트에 "진입후보
  (conf≥mc): 금일 N분 5일평균 N분" 줄이 실제 값으로 나오는지 확인.
- [ ] **⑤ 진입 퍼널 daily_exporter 출력 확인** — 리포트에 "진입 퍼널(날짜, 총 N분):
  FLAT→conf미달→CoherenceGate→게이트차단→후보→진입" 줄과 게이트별 breakdown이
  정상 출력되는지, `coherence_blocked` 컬럼이 내일부터 실제 값(0 아닌 값 가능)을
  담는지 확인(오늘 이전 데이터는 컬럼 신설 전이라 0 고정이 정상).
- [ ] **⑥ Hurst counterfactual 첫 표본 축적 확인** — Hurst만 차단한 A/B/C 신호가
  발생하면 `hurst_gate_shadow` 테이블에 행이 쌓이는지(`[HurstShadow] counterfactual
  기록 실패` 경고가 없는지) 확인. 최소 20건 쌓일 때까지는 §3-6 판정 INSUFFICIENT가
  정상.
- [ ] **⑦ 표본 기아 사다리 1단계 관찰 지속** — 297차(2026-07-06)가 FQAdj 수정
  배포일 — 5거래일(약 2026-07-13 전후) 경과 후에도 주간 진입<10건이 지속되면
  `eval_sample_starvation()` 리포트가 2단계(MetaGate take_ceil 완화) 권고로
  전환되는지 확인. 그 전까지는 사다리 임의로 올리지 말 것(§2 사전등록 원칙).
- [ ] **⑧ CB③-P4·CB② 두 예외 모두 실전 전환 전 복원 대상임을 재확인** —
  `CLAUDE.md` Phase 5 체크리스트에 ⑤(CB②)·⑥(CB③-P4) 두 항목이 모두 등재됐는지,
  실전 전환 논의 시 둘 다 빠짐없이 검토 대상에 포함되는지 확인.

---

## 2026-07-06 (296차 검증) [30m 호라이즌 퇴역 반영 실기동 검증]

> 290차가 사전 등록한 "EOD full_cv 재학습 후 30m acc 목표(0.38~0.41) 미달 시 퇴역"
> 기준이 296차 EOD(15:46, acc=0.3052)에서 충족되어 퇴역 확정. `model/ensemble_decision.py`
> (CascadeCoherence·CoherenceGate 30m 제외), `config/settings.py`(ENSEMBLE_WEIGHTS류
> 30m→0.0), `safety/circuit_breaker.py`(주석), `docs/260707_FEATURE_ADD_TIMING_REPORT.md`
> ·`ROADMAP.md`(재활성화 조건 철회) 반영. py_compile 통과, 앱 미기동 상태에서 텍스트 편집만
> — 라이브 미검증.

- [ ] **① 다음 기동 후 CascadeCoherence/CoherenceGate 30m 제외 정상 동작 확인** — 30m
  방향이 1m과 반대여도 더 이상 `[Ensemble] CascadeCoherence 차단`/`CoherenceGate 차단`
  로그에 영향 주지 않는지, 과거처럼 "30m ConstOut(dir=+1) + 1m SHORT(-1) → score=0.50
  차단" 같은 패턴이 재발하지 않는지 확인
- [ ] **② ENSEMBLE_WEIGHTS 30m=0 반영 후 앙상블 conf 분포 변화 확인** — 나머지 5개
  호라이즌 가중치 재분배(+0.03씩)로 conf 분포가 급변하지 않는지, MC_PERCENTILE 기반
  동적 min_conf가 기존 대비 크게 흔들리지 않는지 며칠 관찰
- [ ] **③ 30m predict_proba·GBM/RF 학습·CB③ P4 모니터링이 계속 정상 동작하는지 확인**
  — 퇴역은 의사결정 반영 차단이지 예측/학습 중단이 아님. 대시보드에서 30m 카드가
  계속 값을 표시하는지, EOD 재학습 로그에 30m GBM/RF 학습이 계속 도는지 확인
- [ ] **④ 296차 이전 13:09~13:11 사고(292차 registry 97→105 hot-swap 중 스케일러
  차원불일치 → 자동진입 정지 3회 → 허위 거래소CB 감지) 재발 방지 별도 검토** — 이번
  296차 변경은 registry 피처 개수를 다시 바꾸지 않으므로 무관하나, 향후 active_features
  개수가 바뀌는 변경 시 재기동 없이 hot-swap하지 않는 안전장치 설계 필요(미착수)

---

## 2026-07-06 (292차 검증) [옵션체인 등 8개 피처 registry 활성화]

### 피처 활성화 반영 후 30m 모델 회복 확인

- [ ] **① 재학습 로그에서 8개 피처 반영 확인** — 다음 자동 재학습(intraday/EOD) 로그의 `[FeatureReg] 5m/10m/15m/30m` 제외 목록에서 `opt_chain_pcr`/`opt_gex_bn`/`opt_gex_sign`/`opt_atm_call_oi`/`opt_atm_pcr`/`micro_regime_code`/`queue_directional_depletion`/`threshold_feasibility`가 사라졌는지, `피처 슬라이싱: 105 → N`에서 N이 예상대로 늘었는지 확인
- [ ] **② acc30m 회복 확인** — `[DriftRetrain] acc30m=...` 로그가 랜덤(33%) 이상으로 올라오는지 며칠 관찰
- [x] **③ [DONE 2026-07-06] EOD full_cv 재학습으로 CV acc 재검증 완료 → 미달 확정, 퇴역 결정** — 296차 15:46 EOD(26주·105피처) 결과 30m CV acc=0.3052 (<0.33 재활성화 기준, <0.38~0.41 목표 구간, 랜덤 0.333보다도 낮음). 조건 미충족이므로 재활성화 대신 영구 퇴역으로 최종 결정(NEXT_TODO 296차 섹션·ROADMAP.md·DECISION_LOG 296차 참조)
- [x] **④ [DONE 2026-07-06] KOSPI200/VKOSPI 폴링 수정 완료 — 재기동 후 실동작 확인만 남음** `get_index_price()`(`collection/cybos/api_connector.py:1032`)를 `dscbo1.StockMst`(개별종목 전용 TR로 확정, 지수 완전 미지원) → `CpSysDib.MarketEye`(주식·지수·선물옵션 통합 조회)로 교체 완료(295차, `py_compile` 통과). 실측(`probe_cp_market_eye.py`, 관리자 권한)으로 K2G01P/O2901P가 MarketEye에서 정상 조회됨을 확인 후 반영.
  - [ ] **재기동 후 확인**: 다음 main.py 재시작 이후 `[CybosIndex] 종목명 검증 실패` 로그가 더 이상 안 뜨는지, `_last_kospi200_spot`/`_last_vkospi`가 실제 값으로 채워지는지, `features/technical/basis.py`의 `basis_ready`/`vkospi_ready`가 True로 전환되는지 SIGNAL/SYSTEM 로그로 확인.
- [ ] **⑤ [신규발견, 남겨둠] 나머지 3개 need_add 피처 도달 시 처리** — `opt_atm_put_oi`(3,900행, 07-07 예상), `cvd_monotone_ratio`(3,608행), `opt_pcr_extreme_bearish`(3,249행) 4,000행 도달 시 이번과 동일하게 `shap_feature_registry.json` 반영 (이번 세션 전례처럼 "계획만 하고 registry 반영 누락"이 반복되지 않도록 주의 — DECISION_LOG 292차 참조)

---

## 2026-07-05 (291차 검증) [검증 캠페인 계측·판정 자동화]

> 260705 계획 문서 §1 공백 3종(합격선 사전등록·롤백 기준·스케줄 미연결) 구현 완료.
> 합격선: `config/settings.py:VALIDATION_CAMPAIGN` (사전 등록 — 사후 변경 금지, §9-4).
> 판정 로직은 합성 데이터 격리 테스트로 5개 채널 전부 검증 완료(스크래치패드, 운영 DB 미접촉).

- [ ] **① 금요일 EOD 캠페인 체인 첫 실행 확인** — `EOD_RETRAIN.bat`(py310_64)이
  금요일에 재학습 후 `[검증 캠페인] 주간 스텝 5개 실행` 로그와 함께
  ablation→판정리포트→TB재학습→분위재학습(→격주 MAE/MFE) 순으로 도는지,
  `data/validation_campaign_report.md` 생성되는지 확인. 강제 실행: `--campaign` 플래그.
  주의: 판정 리포트가 TB 재학습보다 **먼저** 도는 순서가 OOS 보장의 핵심 — 순서 바꾸지 말 것
- [ ] **② 신규 로깅 3컬럼 축적 확인** — 다음 장중 `ensemble_decisions`에
  quantile_q10_pt/quantile_q90_pt/meta_gate_horizon이 매분 기록되는지
  (마이그레이션은 앱 기동 시 init_all_dbs()가 자동 수행, 개발PC에서 확인 완료)
- [ ] **③ 신호소멸청산 counterfactual 행 기록 확인** — 다음 신호소멸청산 발동 시
  trades.db `signal_decay_exits`에 스톱/TP1 가격 포함 행이 남는지, 다음 금요일
  리포트 [4]에서 resolve(STOP/TP1/NEITHER 판정)되는지 확인
- [ ] **④ 첫 판정 리포트는 전 채널 INSUFFICIENT가 정상** — TB는 모델 mtime 이후
  OOS 표본이 1주 쌓여야 하고, meta/quantile은 신규 컬럼 축적 후부터. W2 리포트부터
  수치가 나오기 시작하는 게 정상 진행. 조급하게 합격선을 건드리지 말 것

## 2026-07-05 (290차 검증) [260704 종합감사 P0~P3]

### 실기동/실브로커 검증 필요 항목

- [ ] **① 지정가 우선 집행 실브로커 검증** — `LIMIT_ENTRY_FIRST_ENABLED=True`로 전환 후
  모의투자에서 Cybos CpTd6831(지정가)/CpTd6833(취소) TR이 실제로 정상 동작하는지,
  타임아웃(12초) 시 시장가 전환 없이 취소만 되는지, `[LimitEntry]` 계측 로그로 실측
  체결 타이밍 확인 (개발환경은 COM 미지원이라 미검증 상태)
- [ ] **② 신호 소멸 청산(P4.5) 실거래 영향 확인** — `SIGNAL_DECAY_EXIT_ENABLED=True` 기본
  ON 상태로 며칠 운영 후, 반대방향 고신뢰 전환 시 실제로 손절가 도달 전 조기청산되는지,
  기존 청산 우선순위(하드스톱→TP1/TP2)와 충돌 없는지 로그 확인
- [ ] **③ 30m 다음 EOD 재학습 후 정확도 재측정** — `batch_retrainer.py:_retrain_phase2()`
  피처명 합집합 수정이 반영된 다음 재학습에서 `feature_names_30m.pkl`에 opt_gex_bn/
  opt_chain_pcr/opt_atm_pcr/opt_atm_call_oi가 실제로 포함되는지, `gbm_30m_acc.txt`가
  목표(0.38~0.41)에 근접하는지 확인 → 미달 시 30m 퇴역 최종 결정
- [ ] **④ 챌린저 부트스트랩/heartbeat 콜드스타트 해소 여부 판단** — 최초 승격이 한 번
  발생한 뒤 CHAMPION_BASELINE 자체 shadow 이력이 쌓이기 시작하는지, 그 전까지 계속
  "표본부족"만 반환하는 게 맞는지 재확인. 실거래 브릿지(별도 설계) 필요 여부 결정
- [ ] **⑤ TP1 스킵·트레일단독 챌린저(`E_CHAMPION_TP1_SKIP_TRAIL`) 20일 병행평가** —
  기존 challenger_daily_metrics 집계로 자동 축적되는지 확인 후 20일 뒤 A/B 결과 검토
- [ ] **⑥ 신규 피처 4종(베이시스·VKOSPI·프로그램매매·외인선물) + 만기더미 4종 SHAP 심사** —
  `include_pending_validation`으로 등록만 해둔 상태 — 충분한 표본 축적 후 SHAP 심사
  통과 시 `include`로 승격할지 판단
- [ ] **⑦ 탭 15개→4그룹 재편** — headless 개발환경에서 레이아웃 회귀를 시각 확인할 수
  없어 보류함. 사용자가 직접 실행하며 `UiAutoTabController` 자동포커스 로직까지 포함해
  진행할 것 (`ROADMAP.md` §5-3 참조)
- [ ] **⑧ position_state.json 재발 방지 확인** — 이번 세션 중 검증 스크립트가 실제
  운영 파일을 오염시킨 사고가 있었음(290차, `force_flat()`으로 복구 완료). 프로그램
  재시작 후 실제로 FLAT 상태가 정상 로드되는지, 이후 검증 스크립트 작성 시 격리 경로를
  쓰는 습관이 지켜지는지 확인

## 2026-07-03 (289차 검증)

### 틱 단위 하드스톱 AttributeError 수정 실기동 검증

- [ ] **① 틱 하드스톱 정상 발동 확인** — 다음 장중 스톱 히트 케이스에서 AttributeError 없이 `[TickStop]`(틱 콜백)·`[TickStop-S0C]`(파이프라인 소비부) 로그가 정상 출력되는지, 기존 인트라바 스톱(STEP 8)보다 먼저 청산 주문이 나가는지 확인

## 2026-07-03 (288차 검증) [P0~P5]

### SGD 온라인학습 구조 재설계 실기동 검증

- [ ] **① 콜드스타트 루프 해소 확인(P0)** — 다음 장중 GBM 재학습이 여러 번 발생해도 SGD `_acc_buf`가 그 사이에 초기화되지 않고 계속 누적되는지, `_adjust_weights()`가 실제로 작동해(`[OnlineLearner] 가중치 조정` 로그) SGD/GBM 블렌딩 비중이 하루 종일 30% 고정이 아니라 변화하는지 확인
- [ ] **② 봉단위 dedup 정상 작동 확인(P1)** — 대시보드 SGD 카드 "누적 N건"이 예전보다 느리게 증가하는지(30m은 매분이 아니라 대략 30분에 1건), `_horizon_counts`가 이제 "독립 표본 수"를 의미하게 됐다는 점 육안 확인
- [ ] **③ 클래스체계 전환 자동리셋 로그 확인(P3)** — 배포 후 첫 실행에서 각 호라이즌당 `[OnlineLearner] {hz} 클래스 체계 변경(3클래스→이진) → 리셋` 로그가 정확히 1번씩(호라이즌당) 뜨는지, 이후 크래시 없이 정상 학습되는지 확인
- [ ] **④ SGD_FULL_RESET_PENDING 소비 확인(P4)** — 다음 GBM 재학습 완료 시 `[SGD] threshold 교체 후 완전 리셋 완료` 로그가 뜨고 `config/settings.py`의 `SGD_FULL_RESET_PENDING`이 코드상 `False`로 되돌아가는지 확인 (재시작 시 파일이 실제로 갱신되는지까지 — 메모리상 플래그가 아니라 파일을 직접 고쳤으므로 재시작 후에도 True로 남아있을 수 있음, 재확인 필요)
- [ ] **⑤ 재보정된 HORIZON_THRESHOLDS로 실측 FLAT 비율 확인** — 재보정 후 며칠간 실측 UP/DN/FLAT 비율이 33/34/33 근처로 유지되는지, 새 GBM 재학습분부터 반영되는지 확인
- [ ] **⑥ SGD_BLEND_DISABLED_HORIZONS 배지 확인(P5)** — 대시보드에서 1m/15m/30m 카드가 `OFF·학습됨`/`OFF·리셋됨`/`OFF·미학습`으로 표시되고, 3m/5m/10m는 기존처럼 정상 배지로 표시되는지 육안 확인
- [ ] **⑦ (다음 금요일) ThresholdRecalibrator 재보정 방향 정상 확인** — `LOOKBACK_TRADING_DAYS=21` 적용 후 첫 금요일(15:40) 자동 실행 시 `threshold_monitor.db`의 신규 레코드가 `WATCHLIST` 이하로 안정적인지(6/12~6/26처럼 반대방향 UPDATE 경보가 재발하지 않는지) 확인

## 2026-07-03 (287차 검증) [P0]

### 하드스톱·시간청산 pending 선등록 수정 실기동 검증

- [ ] **① 하드스톱 발동 시 미추적체결(pending_miss) 미재발 확인** — 다음 장중 하드스톱이 실제로 발동하는 케이스에서 체결 콜백이 `사유=미추적체결(pending_miss)`가 아니라 정상 `[체결청산-부분]`/`[체결청산]` 경로로 매칭되는지 로그 확인
- [ ] **② 15:10 시간청산도 동일 확인** — 시간청산 발동 시 동일하게 pending_miss 없이 정상 매칭되는지 확인
- [ ] **③ 청산 완료 후 브로커 잔고 = 0 확인** — 하드스톱/시간청산으로 "청산 완료" 로그가 찍힌 직후 UI 실시간 잔고(브로커 실제 잔고)가 정확히 0으로 일치하는지, 이번 사고처럼 잔고가 남지 않는지 확인
- [ ] **④ 주문 실패 시 롤백 확인** — 하드스톱/시간청산 주문이 `ret != 0`으로 실패하는 케이스가 있다면 `_clear_pending_order()`가 정상 호출되어 이후 재시도가 `_has_pending_order()`에 막히지 않는지 확인
- [ ] **⑤ (선택) 이번 사고로 실제 발생한 잔고 잔존분 수동 정리 여부** — 사고 당시(13:32경) 브로커에 남았던 1계약 잔고가 이후 다음 하드스톱/시간청산 등으로 자동 정리됐는지, 아니면 아직 남아있어 수동 확인이 필요한지 HTS에서 재확인

## 2026-07-03 (286차 검증) [P1]

### stuck exit 손익 부풀림 버그 수정 후속 조치

- [ ] **① 과거 오기록 3건 보정 여부 결정** — `trades.db`의 06-22 13:23(+240,528원 표기, 실제는 정상 범위 확인 필요)·07-01 11:42(-1,227,356원→정상 -615,686원)·07-01 13:00(-5,987,676원→정상 -1,205,676원) 보정 진행할지, 진행한다면 `daily_stats`/PnL 히스토리 등 파생 집계에도 영향 없는지 확인 후 결정
- [ ] **② 다음 stuck exit 발생 시 정상 금액 기록 확인** — 다계약 포지션에서 Chejan 콜백 누락 + `_ts_resolve_stuck_exit_pending()` 재발동 시, `pnl_krw`가 더 이상 quantity배로 부풀지 않고 TRADE 로그 개별 체결 합산과 일치하는지 확인
- [ ] **③ (범위 외, 근본 원인) Chejan 콜백 누락 자체는 미해결** — 이번 수정은 콜백 누락 시의 "합성 기록 손익 계산"만 고쳤을 뿐, 콜백이 애초에 누락되는 근본 원인(COM 이벤트 유실)은 다루지 않음. 재발 빈도가 잦다면 별도 조사 필요.

## 2026-07-03 (285차 검증) [P1]

### 앙상블 CoherenceGate + 체크리스트 C등급 이중차단 규칙(`[285차-P5]`) 실기동 검증

- [ ] **① `[P5]` 로그 발생 확인** — 다음 장중 앙상블 `coherence_blocked=True` + 체크리스트 C등급이 동시 발생하는 사이클에서 `[P5] CoherenceGate+체크리스트C 동시발생 — C등급 차단` 로그가 실제로 찍히고 `_final_grade`가 X로 전환돼 진입이 안 되는지 확인
- [ ] **② A/B등급 영향 없음 확인** — 앙상블 `coherence_blocked=True` + 체크리스트 A/B등급 사이클은 이 규칙과 무관하게 기존처럼 정상 자동진입되는지 확인 (백테스트 근거인 승률92.9% 구간을 실수로 막지 않는지가 핵심)
- [ ] **③ coherence_blocked 없는 일반 C등급 영향 없음 확인** — 앙상블이 정상(coherence 문제 없음)인데 체크리스트만 C등급인 평범한 사이클은 기존처럼 자동진입되는지 확인
- [ ] **④ (범위 외, 별도 검토) stuck_exit_flat/remainder 버그** — 백테스트 중 발견한 `exit_reason='stuck_exit_flat'/'stuck_exit_remainder'`(대량계약·grade 공백, 07-01 -1,227,356원 등) — 오늘 수정과 무관, 원인 딥다이브 필요 여부 사용자 확인 대기

## 2026-07-03 (283차 검증) [P0]

### 증거금 미반영 진입거부 재발방지 검증

- [ ] **① CpTd6722 실거래 반환값 검증** — 다음 장중 grade A/B/C(auto_entry=True) 사이클에서 `[MarginCap]`/`[MarginBlock]`/`[증거금부족 차단]` 로그가 실제로 찍히는지, `buy_new_qty`/`sell_new_qty`(idx 29/19) 값이 계좌 실제 증거금 여력과 합리적으로 일치하는지 확인 (공식 문서 기준으로만 구현, 실기동 검증 없음)
- [ ] **② 주문 거부 시 status/msg 노출 확인** — 다음 SendOrder 실패(ret≠0) 발생 시 `[EntrySendResult]`/`[Entry]` 로그에 `status=`/`msg=`가 실제로 채워지는지 (예전엔 이 정보가 통째로 유실됐음)
- [ ] **③ 대시보드 "진입 수량" 카드 확인** — A급 자동진입 사이클에서 "진입 수량" 카드 값이 실제 `_execute_entry`에 전달된 수량과 일치하는지, 증거금 부족 시 "0(증거금부족)" 빨간색으로 표시되는지 육안 확인
- [ ] **④ 증거금 조회 호출 빈도 확인** — grade=X 및 auto_entry=False 사이클은 건너뛰도록 게이팅했음. PipePerf 로그로 실제 CpTd6722 호출 빈도가 예상(A/B/C auto_entry 사이클만)과 일치하는지, 매분 무조건 호출되고 있지 않은지 확인
- [ ] **⑤ Kiwoom 브로커 폴백 확인 (해당 시)** — BROKER_TYPE=kiwoom 환경이 있다면 `get_order_available_qty`가 `None`을 반환해 기존 동작(증거금 캡핑 없이 max_entry_qty만 적용)으로 안전하게 폴백하는지 확인

## 2026-07-02 (281차 검증) [P1]

### start_mireuk.bat 15:10 이후 CHOICE Y 재시작 검증

- [ ] **① 정상 EOD 종료 회귀 없음 확인** — `data\_exit_normally` 마커가 있는 정상 15:10 강제청산 종료 시, 새 CHOICE 프롬프트 없이 기존처럼 조용히 종료되는지 확인 (프롬프트가 뜨면 안 됨)
- [ ] **② 15:10 이후 크래시 → CHOICE Y 재시작 실측** — 장중부터 실행 중이던 세션이 15:10 이후 `_exit_normally` 없이 종료됐을 때 "의도적 재시작입니까?" 프롬프트가 뜨고, Y 응답 시 main.py가 재기동되는지 실기동 확인
- [ ] **③ N/타임아웃 시 정상 종료 확인** — 위 프롬프트에서 N 또는 10초 타임아웃 시 기존과 동일하게 "재시작 안 함 (오버나이트 금지)"로 종료되는지 확인
- [ ] **④ 같은 세션 반복 재확인 없음 확인** — ②에서 Y 응답 후 다시 크래시가 나면 재프롬프트 없이 바로 재시작되는지 확인 (`_debug_afterhours` 마커 유지 확인)
- [ ] **⑤ (범위 외, 저우선) 5회 초과 분기 GOTO-in-block 검증** — `IF !_RESTART_CNT! GTR 5 (...GOTO :restart_done...)`가 실제 5회 초과 상황에서 jump table 오염 없이 정상 종료되는지 별도 확인 필요 (이번 수정에서 손대지 않음)

## 2026-07-02 (273차 검증) [P0]

### PYTHON_64_EXEC 경로 하드코딩 수정 검증

- [ ] **① GBM-64 ERROR 재발 여부** — 다음 장중 `DriftRetrain` 트리거 시 `[GBM-64] py310_64 Python 없음` ERROR가 더 이상 발생하지 않는지 SYSTEM/WARN 로그 확인
- [ ] **② 장중 경량 재학습 실제 성공 확인** — `[GBM-64] 재학습 완료` 등 정상 완료 로그 및 `_on_gbm_retrain_done()` 호출 확인
- [ ] **③ 82108 PC(다른 머신) 기동 검증** — 다음 그 PC에서 `git pull` 후 재기동 시 `PYTHON_64_EXEC`가 `C:\Users\82108\anaconda3\envs\py310_64\python.exe`로 자동 해석되고 재학습이 정상 동작하는지 확인 (코드 수정 불필요해야 함)
- [ ] **④ Degraded Mode 오발동 감소 확인** — 향후 acc30m 붕괴 상황에서 재학습이 정상 작동해 Degraded Mode 진입 빈도가 줄어드는지 관찰
## 2026-07-02 (280차 검증) [P1]

### 자가학습 탭 표시 버그 4종 수정 실사용 확인

- [ ] **① SGD 호라이즌 카드 배지 확인** — 실제 대시보드에서 BiasReset/SGD 붕괴복구가
      발생한 호라이즌이 "리셋됨"(주황) 배지로, 완전 미학습 호라이즌은 "미학습"(회색)으로
      정상 구분되는지 육안 확인. 건수 라벨이 "누적 N건"으로 바뀐 것도 확인.
- [ ] **② 정확도 판정불가 표시 확인** — `reset_daily()` 직후(GBM 재학습 완료 시점)
      정확도 버퍼가 5건 미만인 호라이즌이 "0.0%" 대신 "—.—%(n건)"으로 표시되는지, 5건
      이상 쌓인 후 정상 %로 전환되는지 확인.
- [ ] **③ GBM 재학습 횟수 누적 확인** — 다음 STEP3 장중 재학습(30분 주기) 완료 후
      대시보드 "재학습 횟수"가 0회에서 1씩 증가하는지, `data/session_state.json`의
      `gbm_total_retrain_count`와 일치하는지 확인. 다음 15:45 EOD 재학습(`retrain_eod.py`)
      완료 후에도 카운트가 추가로 +1 되는지 로그(`logs/retrain_eod_*.log`)에서
      "[EOD] 재학습 이력 저장" 라인으로 확인.
- [ ] **④ CB③ 강조색 임계값 확인** — 30건 미만 표본에서 CB③ 정확도 라벨이 회색으로,
      30건 이상부터 실제 %에 따라 녹/황/적으로 색이 바뀌는지 확인.

---

## 2026-07-02 (279차 검증) [P2]

### drift_adjuster 대시보드 표시 실사용 확인

- [ ] **① LearningPanel 라벨 표시 확인** — 실제 대시보드 기동 후 "🧠 자가학습 모니터"
      탭에서 CB③ 라인 바로 아래 `SGD alpha: 0.00xxx  ...  |  이력: ...` 라벨이 정상
      노출되는지, 폰트 크기·정렬이 다른 라벨과 어긋나지 않는지 육안 확인(오프스크린
      PyQt5 렌더 테스트만 완료, 실제 창에서는 미확인)
- [ ] **② EOD 마감 후 실제 반영 확인** — 다음 15:40 마감 직후 대시보드 값이
      `data/drift_adjuster_state.json`의 `alpha`/`last_action`과 일치하는지, 스파크라인
      이력이 갱신되는지 확인
- [ ] **③ 툴팁 텍스트 검수** — DRIFT_UP/RECOVERY_DOWN/SKIP_LOW_SAMPLE 설명 툴팁이
      실사용자 관점에서 이해 가능한지 검토

---

## 2026-07-02 (278차 검증) [P1]

### drift_adjuster 최소 표본 가드 검증

- [ ] **① SKIP_LOW_SAMPLE 로그 확인** — 다음 EOD 마감(15:40) 시 당일 `sample_count`가
      15 미만이면 `[DriftAdjuster] 표본 부족(n=... < 15) — ... 반영 스킵, alpha=...
      유지` INFO 로그 출현 확인
- [ ] **② 정상 기록 경로 확인** — `sample_count>=15`인 날은 기존과 동일하게
      `acc_history`에 반영되고 `[DriftAdjuster] SGD alpha 갱신` 로그가 찍히는지 확인
- [ ] **③ 임계값(15) 적정성 관찰** — 며칠간 EOD 로그의 실제 `n_samples` 값 분포를
      보고 15가 너무 낮은지/높은지(항상 스킵되거나 항상 통과) 판단, 필요 시 재조정

---

## 2026-07-02 (277차 검증) [P0]

### acc30m 버퍼 기아 방지 수정 검증

- [ ] **① 리셋 스킵 로그 확인** — 다음 거래일 ConstOut 재적합 시점(~30분 간격)에
      버퍼 표본이 30 미만이면 `[CB③] acc30m 버퍼 리셋 스킵 — 기존 표본 N건 < 최소 30건`
      INFO 로그 출현 확인 (기존엔 항상 무조건 `[CB③] acc30m 버퍼 리셋` 로그만 찍혔음)
- [ ] **② P4 단계 전환 최초 발생 확인** — 표본이 실제로 30건 이상 누적된 후
      `[CB③-P4] acc30m 단계 전환: ...` 로그가 (오늘까지 0건이었으나) 처음으로 찍히는지 확인
- [ ] **③ 표본 혼입 부작용 관찰** — 리셋 스킵으로 서로 다른 스케일러 버전 하 예측이 섞인
      구간에서 acc30m 수치가 부자연스럽게 튀는지(예: 순간적으로 100%↔0% 널뛰기) 1~2일
      관찰. 심하면 리셋 스킵 대신 다른 완화책(쿨다운 시간 단축 등) 재검토

---

## 2026-07-02 (277차 결정) [P0 — 모니터링]

### CB③ 재활성화 대기 — 30m 정확도 회복 트리거 확인 (매 세션 체크)

- [ ] **CB③ 재활성화 조건 확인** — `calibration_report.md` "최근(Platt 보정 이후)" 30m
      accuracy가 `CB_ACC_WATCH_MIN`(0.35) 이상 **5거래일 연속** + `conf_inversion` 미발동
      상태 유지되면 [[DECISION_LOG 277차]] 기준 재활성화 검토 시작. 그 전까지는 매 세션
      simply 확인만 하고 재활성화 착수하지 말 것
- [x] **(재활성화 착수 시 선행)** acc30m 버퍼 리셋 주기(~30분, 스케일러 재적합 연동)와
      `CB_ACC30M_MIN_SAMPLES=30` 관계 재검토 — [DONE 2026-07-02] 같은 날 즉시 수정.
      `circuit_breaker.py::reset_acc30m_buffer()`가 표본<30이면 clear() 스킵하도록 변경
      (기아 방지). **다음 거래일 검증 필요**: `[CB③] acc30m 버퍼 리셋 스킵` 로그 출현 +
      이후 `[CB③-P4]` 단계 전환 로그가 처음으로 찍히는지 확인 (오늘까진 하루 종일 0건)

---

## 2026-07-02 (275차 검증) [P0]

### conf/mc 통과율 0 딥다이브 후속 — 근본 원인 미조사 항목

- [x] **① conf 하락(06-29~) 근본 원인 특정** — [DONE 2026-07-02] 276차에서 확정. EOD 재학습/
      canary/scaler는 결백(06-26 EOD·06-29 프리마켓 로그 정상). `predictions.db` 일별 accuracy
      쿼리 결과 정확도는 06-29 전후로 꺾이지 않고 6월 내내 랜덤 근방(25~40%)이었음. 진짜 원인은
      261차(06-29) Platt 보정 강화(WINDOW 100→200, C 0.05→0.02)가 그동안 가려져 있던 랜덤급
      정확도를 정직하게 반영한 것. 07-01~07-02 추가 하락은 06-25 Q3 배포정책으로 줄어든 표본
      속도 탓에 WINDOW 완전 수렴까지 ~2.8~3거래일 걸린 지연 효과 — 버그 아님
- [x] **② CB③(30분 정확도<35%→당일 정지) 오늘 발동 여부 확인** — [DONE 2026-07-02] 277차
      확정. `circuit_breaker.py:315` HALT 트리거가 **06-25부터 코드 하드 비활성화**
      (임계 미달 시 debug 로그만, `_trigger_halt()` 미호출). 오늘 12:05~12:11 acc30m이
      5.9~26.1%(현재 실제 임계=0.28, CLAUDE.md의 35%는 구값)까지 떨어져도 state=NORMAL
      유지로 실측 확인. 비활성화 사유(need_add 피처 미탑재)는 178차(06-15)로 이미 해소됐지만
      acc 회복 미충족으로 재활성화 안 됨. 부가로 acc30m 버퍼가 스케일러 재적합마다(~30분
      간격) 리셋돼 MIN_SAMPLES=30 표본이 잘 안 쌓이는 구조적 문제도 확인 — CB③ 재활성화
      여부는 사용자 정책 판단 필요(코드 미변경)
- [ ] **③ conf_inversion 임계값(3%p) 근소 미달 관찰** — 현재 gap=2.85%p로 발동 임계 바로
      아래. 273차 EKS 마진 이슈와 동일 패턴이므로 1~2주 관찰 후 임계를 2%p대로 낮출지
      히스테리시스를 넣을지 판단
- [x] **④ drift_adjuster 최소 표본수 가드 검토** — [DONE 2026-07-02] 278차에서 구현.
      `MIN_SAMPLES_REQUIRED=15` 미만이면 이력 기록·alpha 조정 스킵(`SKIP_LOW_SAMPLE`).
      다음 거래일 EOD 로그 검증은 아래 278차 항목 참고
- [ ] **⑤ meta_gate_tuning 리포트 수정 반영 확인** — 다음 정기 리포트 생성 시
      `avg_meta_confidence`가 0.2 전후(실제 blended_conf, flat_signal 0.0 다수 포함)로
      나오는 게 정상임을 대시보드/모니터링에서 오인하지 않는지 확인

---

## 2026-07-02 (273차 검증) [P0]

### EKS 히스테리시스 + 진단 로그 3종 검증

- [ ] **① EKS 히스테리시스 로그 확인** — 09:05 GAP_OPEN 판정 시 근소 미달(margin 2%p 이내)이면
      `[SHS-EKS] EKS 미발동 — 마진 내 근소 미달` WARNING 로그 확인 (기존처럼 CRITICAL 발동 아님).
      반대로 conf_max가 확실히 낮으면(발동선 밑) 여전히 `Early Kill Switch 발동` 정상 확인
- [ ] **② Phase4 잔존 피처 확인** — `[PreMarket] Phase4 refit 완료 ... | 잔존=...` 로그에서
      08:59 refit이 못 누른 피처명 확인. Phase1~3와 겹치는 피처인지, Phase마다 다른지 비교해
      "최신봉 비중 클수록 억제 안 됨" 가설 검증
- [ ] **③ S6Detail 병목 특정** — `[S6Detail] ensemble=Xms checklist_pre=Yms meta_gate=Zms gates=Wms dashboard=Vms tail=Ums`
      로그에서 어느 구간이 PipePerf S6(79~83%)의 실제 원인인지 확인. `ensemble`(ensemble.compute)이
      유력 후보 — 크면 ensemble.compute 내부 프로파일링 추가 검토
- [ ] **④ ConfTrend breakdown 확인** — `[LiveDBG] ConfTrend SLOW total ... | import=Xms completed_map=Yms db_query(rows=30)=Zms arithmetic=Wms table_update=Vms scroll=Ums`
      형태로 출력되는지, 어느 구간이 300~400ms의 실제 원인인지 확인 (db_query 유력 후보 —
      predictions.db 580MB로 커진 것과 연관 가능성)
- [ ] **⑤ EKS 마진으로 인한 부작용 없는지 관찰** — 히스테리시스 도입으로 실제 저신뢰 구간에서
      EKS가 필요한데 마진 때문에 안 켜지는 사례가 있는지 1~2주 관찰

---

## 2026-07-01 (264차 검증) [P0]

### EKS·z경고·Canary 3종 수정 검증

- [ ] **① EKS cold-start 정상 판정 확인** — 내일 장 시작 09:05 분봉에서 `[SHS-EKS] EKS 미발동 — cold-start (conf_max=0%% delayed=1 policy_blocked=4 / 5봉)` INFO 로그 출현 확인 (EKS CRITICAL 로그 미출현)
- [ ] **② Canary z 감소 확인** — 08:55 `[Canary] z경고피처=N개` 값이 이전 14개 대비 감소 (~10개 이하) 확인. `is_open_volatile`, `hurst_ready` 피처가 제외됐음을 `[Canary] 장전 재적합 완료 n=30봉 z경고 →N개 ✓ 임계 이하` 로그로 확인
- [ ] **③ Canary refit 완료 후 z 갱신 확인** — `[Canary] 장전 재적합 완료` 로그 이후 EKS 원인 메시지의 z경고 수가 pre-refit 값이 아닌 post-refit 값으로 출력되는지 확인
- [ ] **④ Phase1(bar3) refit 효과 가시화** — `[PreMarket] Phase1 refit 완료 n=30봉 z경고 X→Y개` 로그에서 z경고 감소(Y < X) 확인
- [ ] **⑤ EKS 자동 회복 경로 불필요화 확인** — 오늘 수정 후 EKS가 발동되지 않으므로 09:20 회복 평가 자체가 실행 안 됨 확인 (`[SHS-EKS] EKS 자동 해제` 로그 미출현이 정상)

---

## 2026-06-30 (263차 검증) [P0]

### 진입 안전장치 3종 검증

- [ ] **① ATR 상한 차단 로그 확인** — 고변동성 분봉에서 `[차단] ATR X.XXpt > 3.5pt — 손절거리 X.Xpt 과대 (고변동성 진입 차단)` 로그 출현 확인
- [x] **② 시가 이격 차단 로그 확인** — [발견 2026-07-02, 281차] 이 로그가 한 번도 안 찍힌 이유는 `self._session_open_price`가 대입되는 곳이 없어 필터가 상시 no-op(N/A)였기 때문. 281차에서 GapOffset 캡처 경로(`today_open`)와 연결 완료. 내일 장중 OPEN_VOLATILE 구간에서 `gap_chk` 값이 실제 pt로 표시되는지, 이격 과다 시 위 차단 로그가 뜨는지 재검증 필요
- [ ] **③ 인트라바 스톱 발동 확인** — 분봉 종가보다 먼저 bar_high(SHORT)/bar_low(LONG)가 스톱을 터치하는 케이스에서 `[DBG-STOP] 하드스톱 발동: close=X bar_low=X bar_high=X stop=X → exit=X` 로그에 bar_high가 stop 근처임을 확인
- [x] **④ ATR_MAX_ENTRY 임계 재조정 여부** — [DONE 2026-07-02] 07-02 딥다이브로 06-24~07-02 7거래일 ATR 중앙값이 3.5~6.2pt로 만성적으로 상한 근처/초과임을 확인, 274차에서 적응형 상한으로 교체 (아래 274차 항목 참고)

---

## 2026-07-02 (274차 검증) [P0]

### 진입0 개선 2종 — ATR 적응형 상한 + Hurst/MR 조건부 완화 검증

- [ ] **① 적응형 ATR 상한 작동 확인** — `[차단] ATR X.XXpt > Y.YYpt(적응형, 정적=3.5)` 로그에서 Y.YY가 3.5보다 커지는지, 그리고 07-02 10:21~10:28처럼 ATR 4.2~4.6pt대 A등급 신호가 실제로 진입되는지 확인 (`_atr_recent_window` 표본 20개 쌓이는 장 시작 20분 이후부터 유효)
- [ ] **② MEAN_REVERSION 모드 발동 확인** — `[Checklist] ... 모드=MEAN_REVERSION` 로그가 실제로 찍히는지 (최근 2거래일 0회였음). 찍히면 같은 분봉에서 `[차단] Hurst ...` 로그가 함께 안 뜨는지(exempt 확인)
- [ ] **③ 약한 MR 사이즈 축소 확인** — `[Checklist] MR 약한탈진(0.60~0.70) → 사이즈×0.5 축소` 로그 출현 시 실제 Sizer 계약 수가 절반으로 줄어드는지 TRADE 로그 대조
- [ ] **④ 부작용 관찰** — 적응형 상한 상향으로 손절거리(ATR×1.5)가 커진 트레이드의 승률/손익이 기존 3.5pt 캡 트레이드 대비 악화되지 않는지 1~2주 관찰. MR 약한탈진 진입의 성과도 별도 트래킹

---

## 2026-06-30 (262차 검증) [P0]

### SHORT 진입·손실청산 개선 4종 검증

- [ ] **① TP1 손절 이동 로그 확인** — TP1 부분청산 체결 후 `[TP1-Breakeven] SHORT/LONG 잔여 N계약 손절 XXX.XX → 진입가 XXX.XX` INFO 로그 출현 확인 (2계약 이상 포지션 TP1 시)
- [ ] **② 1계약 arm 경로 간섭 없음 확인** — 1계약 TP1 시 기존 `[SingleContractTP1] 1계약 TP1 도달 -> 보호전환` 로그만 출현하고 TP1-Breakeven 로그 미출현 확인 (별도 경로라 도달 안 함)
- [ ] **③ 0.5ATR 트레일링 발동 확인** — 포지션 수익이 0.5~1.0 ATR 구간에서 반전 시 손절가가 -1.5ATR 아닌 -0.75ATR에서 히트되는지 로그/PnL 확인
- [ ] **④ MR SHORT #7 완화 확인** — entry_mode=MEAN_REVERSION SHORT 진입 시 직전봉이 양봉(+1)이어도 `7_prev_bar: True` 로 체크리스트 통과 확인
- [ ] **⑤ MR 임계 0.70 효과** — bull_exhaustion=0.60~0.69 구간(volume ~1.8~2.1×) 분봉에서 MR SHORT 미발동 확인 (VWAP 강제X 유지)

---

## 2026-06-29 (261차 검증) [P0]

### HCGuard + Platt 개선 검증

- [ ] **① HCGuard 발동 확인** — 내일 장 중 conf≥0.65 예측 20건 이상 누적 후 `[HCGuard] Grade A → B 강등` WARN 로그 출현 확인
- [ ] **② HCGuard acc 로그** — 차단 시 `고신뢰 최근 N건 acc=XX.X% < 42%` 수치 출력 확인
- [ ] **③ Platt WINDOW=200 효과** — 1주일 후 calibration_report.md에서 `0.8~0.9: gap` 값이 0.53 → 0.45 이하로 감소 추이 확인
- [ ] **④ 역전 경보 출력 확인** — `python scripts/generate_calibration_report.py` 실행 시 `CONF_INVERSION_ALERT` stdout 출력 + 리포트 상단 경고 섹션 확인
- [ ] **⑤ conf_inversion JSON 키** — `calibration_metrics.json`에 `conf_inversion: {inverted: true, ...}` 포함 확인
- [ ] **⑥ HCGuard 해제 시나리오** — 모의투자 누적 acc가 회복될 때 `[HCGuard] Grade A 차단 해제` INFO 로그 출현 확인

---

## 2026-06-29 (260차 검증) [P0]

### Extreme 피처 5종 수정 검증

- [ ] **① atr_expansion_rate 클리핑 효과** — scaler_monitor에서 `atr_expansion_rate` max|z|가 8.0 이하로 유지되는지 확인 (이전 18.32)
- [ ] **② bull_reversal_signal 쿨다운 효과** — 하루 발동 횟수 15회 이하로 감소 확인 (이전 30회)
- [ ] **③ toxicity_spread_stress SCALE_FLOOR 효과** — `[ScalerFloor] toxicity_spread_stress scale=... → floor=0.25 적용` 로그 출현 확인 (다음 B/D refresh 시)
- [ ] **④ hurst_ready / is_close_volatile WARNING 제거** — scaler_monitor extreme Top5에서 두 피처 미출현 확인
- [ ] **⑤ toxicity_spread_stress μ 정상화** — 다음 EOD 재학습 후 scaler_mean이 0.05~0.15 범위로 내려왔는지 확인 (현재 0.978 이상)

---

## 2026-06-29 (259차 검증) [P0]

### bull_reversal_signal + HealthPolicy 수정 검증

- [DONE 2026-06-29] **② Z_WARN_EXEMPT 즉시 효과** — 260차에서 `hurst_ready`·`is_close_volatile`·`is_open_volatile` 함께 등록 완료
- [ ] **① ScalerFloor 재학습 효과** — 다음 B_INTRADAY/GBM 재학습 후 `bull_reversal_signal` z-score가 2.2 이하로 유지되는지 scaler_monitor 확인
- [ ] **③ HealthPolicy 동적 차단 효과** — Degraded Mode 발동 중 `conf >= zone_mc` 조건 충족 시 `[HealthPolicy] Degraded Mode 차단` 미출현 + `Degraded Mode 축소 size_mult=0.60` 출현 확인
- [ ] **④ ConstOut 필터 효과** — 다음 DynMC RETRAIN 로그에서 `[DynMC] ConstOut 고착 conf 제외: {0.36} → N건 제거` 출현 (ConstOut 구간 존재 시)

---

## 2026-06-29 (258차 검증) [P0]

### horizon_features DB 쓰기 복구 확인

- [ ] **save_horizon_features 정상 동작** — WARN 로그에 `[DBQueue] 쓰기 실패 (op=horizon_features)` 미출현 확인 (258차 재시작 이후)

---

## 2026-06-29 (257차 검증) [P0]

### DynMC 5종 수정 검증

- [x] **MC_PERCENTILE 수정 효과** — 11:31:58 DynMC RETRAIN에서 `conf_p65=0.170` → `base=0.357` 즉시 수렴 확인 **[DONE 2026-06-29]**
- [ ] **mc_history 복원 성공** — 기동 로그에 `[DynMC] 기동 복원: STABLE_TREND 0.540 → 0.42` (오늘 저장 값) 출현
- [ ] **빈 DB fallback 확인** — DB 소실 시뮬레이션 필요 시: `[DynMC] mc_history 레코드 없음 — 안전 fallback=0.35` 로그 출현
- [ ] **cold-start EKS 미발동** — 내일 장 시작 시 GAP_OPEN 5봉 conf=0%여도 EKS 미발동 (대신 `[SHS-EKS] EKS 미발동 — cold-start` 로그 출현)
- [ ] **EKS 회복 로그 강화 확인** — EKS 발동 시 `[SHS-EKS] 회복 평가 시작 (#N)` + `[SHS-EKS] EKS 미해제 — 미충족: conf_hits=N/10` WARNING 출현

---

## 2026-06-29 (256차 검증) [P0]

### EKS 회복 메시지 확인

- [ ] **EKS 발동 로그 문구** — 다음 EKS 발동 시 `→ 일시 관망 (09:20부터 30분 간격 평가)` 포함 확인 ("당일 관망 선언" 미출현)
- [ ] **EKS 회복 로그 출현** — `[SHS-EKS] EKS 미해제 (시도 #N)` WARNING 로그 출현 확인 (257차로 INFO→WARNING 전환)
- [ ] **EKS 해제 Slack 수신** — EKS 해제 시 `✅ Early Kill Switch 해제 — 장중 진입 재개` Slack 알림 수신 확인

---

## 2026-06-27 (254차 검증) [P0]

### 거래소 CB 대응 검증

- [ ] **240초 조기 감지 작동** — 다음 CB 발동 시 `[ExchangeCB] 분봉 4분 00초 미수신 + Cybos 연결 정상 → 거래소 CB 조기 확정` 로그 출현
- [ ] **Slack 예상 재개 시각 포함** — CB 감지 Slack 알림에 `재개 ≈ HH:MM` 포함 확인
- [ ] **관망 10분 작동** — CB 해제 후 `[ExchangeCB] 관망 기간 설정 — 10분` 로그 출현, STEP 7에서 `[차단] 거래소 CB 해제 후 관망 중` 10분간 차단 확인
- [ ] **대시보드 배지 표시** — CB 발동 시 빨간 "KRX CB ⏸" 배지 출현, 관망 중 주황 "관망 N분" 배지 출현, 정상 시 숨김 복귀
- [ ] **포지션 즉시 청산** — CB 해제 직후 포지션 보유 시 `[ExchangeCB] CB 해제 직후 포지션 보유 — 즉시 청산 실행` 로그 출현

---

## 2026-06-27 (253차 검증) [P0]

### 크래시·블로킹 수정 확인

- [ ] **OptionChainWorker 크래시 재발 없음** — `[OptionChain] 이전 워커 실행 중 — 스킵` 로그 정상 출현, RuntimeError 없음
- [ ] **09:00~09:02 investor skip 확인** — `[LiveDBG] _fetch_investor_data 09:00~09:02 서버피크 스킵` 로그 출현
- [ ] **재시작 후 4단계 체인 확인** — `[LiveDBG] _apply 시작 (4단계 체인)` 후 `update_learning/efficacy/trend/pnl_history` 4줄 순서대로 출현, 각 ≤5s
- [ ] **14828ms 블로킹 재발 없음** — `_tick_header 간격 >5000ms` WARNING 없음 (재시작 후 60초 내)

### z경고 억제 확인

- [ ] **EarlyWarmup ScalerFloor INFO 전환** — 08:45 이후 `[ScalerFloor]` 로그가 WARNING 아닌 INFO로 출현
- [ ] **quality_investor_age_sec z경고 없음** — 09:00 첫 분봉에서 `quality_investor_age_sec` extreme 로그 없음
- [ ] **toxicity_atr_stress z경고 감소** — 고변동성 구간에서 `toxicity_atr_stress` extreme 로그 없음
- [ ] **EKS 미발동** — `[SHS-EKS] Early Kill Switch 발동` CRITICAL 없음 (단, 진짜 불량 장이면 정상 발동 허용)

### session_state 레이스 수정 확인 (EOD 후)

- [ ] **P8 완료 후 양키 기록** — retrain_eod 로그에 `p8_last_success_date + eod_retrain_ok_date 기록 완료` 출현
- [ ] **다음날 PreRetrain fallback 없음** — 08:55 로그에 `session_state 미기록 보완` 문구 없음, `PreRetrain 스킵 검토` 직접 출현

---

## 2026-06-26 (250차 검증) [P0]

### 30m·CB③ 비활성화 확인

- [ ] **30m 역방향 필터 미발동** — `[Ensemble] 30m 역방향 감지(필터 비활성)` DEBUG 로그 출현 시 grade=X 강제 없음 확인
- [ ] **CB③ HALT 미발동** — `[CB③ 비활성] acc30m=...%` DEBUG 로그 확인, CRITICAL/Slack 미발송 확인
- [ ] **P4 stage 추적 유지** — `status_dict()["acc30m_stage"]` 변화 모니터링 (NORMAL/WATCH/RESTRICTED)

### CORE 피처 교체 확인

- [ ] **체크리스트 4번 실질 평가** — 하락봉 구간에서 `[Checklist] CORE 4·5 ✗` 로그 출현 확인 (기존에는 cvd_direction=+0.5 고착으로 항상 통과)
- [ ] **cvd_delta_norm z-score 정상** — ScalerRefresh에서 `cvd_delta_norm` identity 강제 미발동 확인 (std ≥ 0.05 기대)
- [ ] **cvd_direction AutoMask 발동 허용** — D_FORCE 시 cvd_direction 마스킹 허용 (CORE 면제 해제됨)

### feature_names_hz.pkl 정합성

- [ ] **EOD 재학습 후 pkl 정합** — `feature_names_1m.pkl`=12, `3m`=12, `5m`=15, `10m`=11, `15m`=15, `30m`=11 확인
- [ ] **[FeatureReg] 로그 현행화 확인** — 1m에 `queue_directional_depletion` need_add 로그 출현 (기존 미출현)

### ERR-FATAL 재발 없음

- [ ] **방어 fallback 작동** — 불일치 발생 시 `[Model] %s 피처 차원 불일치` ERROR 로그 후 default_result 반환 (프로세스 종료 없음)

---

## 2026-07-02 (30m·CB③ 재활성화 검토) [예정]

- [ ] `opt_gex_bn` / `opt_chain_pcr` 각 4,000행 달성 SQL 확인
- [ ] `shap_feature_registry.json` + `horizon_feature_sets.json` need_add → in_pkl 업데이트
- [ ] EOD 재학습 (full_cv=True) 실행 → 30m CV acc 확인
- [ ] acc ≥ 0.33: `ensemble_decision.py` Q3 블록·`circuit_breaker.py` CB③ 주석 해제

---

## 2026-06-25 (249차 — poll_option_chain QThread 분리 검증) [P1]

- [ ] **워커 기동 로그 확인** — 실운영 시 `[LiveDBG] OptionChainWorker 기동 spot=XXX.X` 로그 출현 확인
- [ ] **완료 로그 확인** — `[OptionChain][Worker] 완료 XXXXms | target=N valid=M PCR=...` 로그 출현 및 elapsed ~3000ms 내외 확인
- [ ] **메인 스레드 블로킹 없음 확인** — 워커 기동 후 5분간 틱 수신·파이프라인 로그가 연속 출현 (3초 공백 없음)
- [ ] **실패 격리 확인** — stale chain 발생 시 `[OptionChain][Worker] ATM 대상 없음 ... stale, 재로드` 로그 후 정상 재수집되는지 확인

---

## 2026-06-25 (248차 — EXIT stuck 수정 후 검증) [P0]

- [ ] **3-confirm 자동 해소 로그 확인** — 향후 stuck 발생 시 `[PendingOrder] EXIT stuck 3회 브로커 확인 → 원주문(...) 거래소 취소 간주, pending 소멸 후 TP 재점검` CRITICAL 로그 출현 확인
- [ ] **ManualExit override 로그 확인** — stuck 상황에서 수동 청산 시 `[ManualExit] stuck EXIT pending(...) 브로커 확인 완료 → 강제 소멸 후 수동 청산 진행` 로그 출현 확인
- [ ] **IntrabarTPSchedule 정상 발동** — `_clear_pending_order` 호출 후 300ms 내 `[IntrabarTPSchedule] EXIT_PARTIAL 해소 → 300ms 후 TP 재점검` 로그 출현 확인
- [ ] **position_before_qty 개선** — `_set_pending_order`에 `position_before_qty: int` 필드 추가 → `expected_remaining` 계산에 사용 → 부분 Chejan 유실을 1회 만에 탐지 가능 (현재는 3-confirm fallback으로 커버 중, 긴급 아님)

---

## 2026-06-25 (247차 — PRE_MARKET_SCALER_BARS=30 검증) [P0]

- [ ] **z경고 임계 이하 확인** — 다음 장 SYSTEM.log에서 `[PreMarket] Phase refit 완료 n=30봉 z경고 X→Y개`에서 bar5 이후 Y < 12 확인
- [ ] **Canary refit 미발동 확인** — `[Canary] 장전 재적합 시도` 로그 미출현 (z<12 → 자동 패스)
- [ ] **Canary z 재측정 로그 확인** — `[Canary] 장전 재적합 완료 n=30봉 z경고 →N개 ✓ 임계 이하` 패턴 확인
- [ ] **09:00 첫봉 z경고 없음 확인** — WARN.log에 `z경고` 관련 항목 미출현
- [ ] **D_FORCE refit 정상 전환** — 09:30~10:00 내 `D_FORCE` 혹은 `D_PRICE_MOMENTUM` 트리거 후 500봉 scaler 복원 확인

---

## 2026-06-25 (246차 — Phase C 불일치 수정 후 검증) [P0]

- [ ] **불일치 자동 복구 확인** — 다음 시작 시 `[Model] {h} feature_names_{h}.pkl({N}개) vs GBM({M}개) 불일치 — pkl 무효화` 로그 출현 후 정상 운영되는지 확인 (현재 디스크에 불일치 파일 잔류 가능)
- [ ] **ERR-FATAL 재발 없음** — `X has N features, but HistGradientBoostingClassifier is expecting 97` 에러 재발 여부 확인 (FIX-A의 97개 fallback이 정상 작동해야 함)
- [ ] **Phase C 슬라이싱 경고 로그 모니터링** — `[Retrain] {hz} feature_names_{hz}.pkl {N}개→{M}개 변경 — Phase C 슬라이싱 비활성화` 로그 출현 여부 (FIX-B 경고, `_registry_ok=False` 탐지용)
- [ ] **Canary refit 완료 확인** — 08:55 `[Canary] 장전 재적합 완료` 로그 후 `pre_market_scaler=True` 재시작 로그 확인 (FIX-C)

## 2026-06-25 (245차 — SGD 불일치 수정 후 검증) [DONE 2026-06-25]

- [x] **경고 로그 1회 출현 확인** — [OnlineLearner] 피처 수 불일치 → 리셋 경고 확인됨
- [x] **ERR-FATAL 재발 없음** — 245차 이후 StandardScaler ERR-FATAL 소멸 확인
- [x] **SGD 학습 재개 확인** — 246차 분석에서 09:50+ SGD 경로로 전환된 것 확인

---

## P2 Regime-Conditional GBM — 사전 준비 추적 [장기, ≈2027-01]

> 2026-06-24 `raw_features_horizon` 테이블에 `regime` 컬럼 추가 완료. 이후 데이터 자동 누적.

- [ ] **regime_history 26주 도달 확인** — 예상 시점 ≈ 2027-01-20. `SELECT MIN(ts), MAX(ts) FROM regime_history`로 확인.
- [ ] **레짐별 샘플 수 확인** — 착수 조건: `SELECT horizon, regime, COUNT(*) FROM raw_features_horizon GROUP BY horizon, regime` → 최소 레짐이 5000봉 이상
- [ ] **본구현 착수** — 조건 충족 시 `docs/260611_DIRECTION_BIAS_IMPROVEMENT_PLAN.md` §4.2 참고

---

## 2026-06-25 (244차 — Q3 배포 절충안 검증) [최우선]

### 배포 정책 작동 확인 [P0]

- [ ] **[Deploy] 스킵 로그 출현** — SIGNAL.log에서 `[Deploy] 3m | age= 1 | policy=bar_only | ⏸ 스킵` 패턴 확인 (3m/5m: age>0 시, 10m/15m: age>1 시)
- [ ] **[Deploy] 배포 로그 확인** — 완성봉 직후 분에 `✅ 배포` 전환 로그 출현 (5m 완성 직후 age=0)
- [ ] **30m 역방향 필터 작동** — `[Ensemble] 30m 역방향 필터 작동: 30m=-1 ens=+1 → grade=X` 로그 출현 여부 (일 1~3회 예상)

### 부작용 모니터링 [P1]

- [ ] **신호 밀도 변화** — 일 진입 기회가 기존 대비 크게 감소하지 않는지 확인 (3m/5m 스킵이 많아도 1m+10m+15m 커버)
- [ ] **confidence 분포 변화** — `blended_conf` 분포가 피처 decay 제거 후 이상 급등 없는지 확인 (3~5일 관찰)
- [ ] **ensemble_decision 오류 없음** — `30m_filter_blocked` 키 접근 시 KeyError 없는지 대시보드·로그 확인

---

## 2026-06-25 (242차 — Phase 2 재학습 효과 확인) [최우선]

### Phase 2 모델 교체 확인 [P0]

- [ ] **30m FLAT 고착 감소** — SIGNAL.log에서 `horizon_proba["30m"]["direction"]` 이 UP/DN으로 전환되는 빈도 증가 확인 (기존 거의 항상 FLAT)
- [ ] **confidence 상승** — `blended_conf` 평균이 0.38 → 0.43+ 로 상승하는지 확인 (MetaConf 재보정 중이므로 3~5일 누적 필요)
- [ ] **[BiasReset] 1m DN편향 로그** — `[DN편향⚠ XX%]` 출현 여부 (241차-b 수정 효과, 63% → 0.60 경보)
- [ ] **진입 기회 증가** — 일평균 진입 0~3회 → 3~6회 방향으로 개선 추세 확인 (1주일 단위 관찰)

### Stage 2 재학습 일정 확인 [P1]

- [ ] **~7/8 이후**: `buy_vol/sell_vol` 30일 누적 확인 후 `eod_retrain.py --phase2 --weeks 4` 실행
  - 1m/3m OFI·CVD 피처가 0 fill → 실측 값으로 교체 예정
- [ ] **~7/28 이후**: Stage 3 — `eod_retrain.py --phase2 --weeks 8` 전면 재학습

### multi_timeframe.py 삭제 [P2 — Stage 2 때 처리]

- [ ] `features/technical/multi_timeframe.py` 삭제 (dead code, Stage 2~7/8 때 같이 처리)

---

## 2026-06-25 (236차 — 저신뢰 자동진입 차단 검증) [최우선]

### ENS_CONF_FLOOR_FOR_AUTO 작동 확인 [P0]

- [ ] **차단 로그 출현** — conf<33% 신호 발생 시 SIGNAL.log에 `[Checklist] conf=XX.X% < floor=33.0% → 등급=A 유지, auto_entry=OFF` 출현
- [ ] **수동 모드에서는 여전히 알림** — grade=A 신호가 수동확인 팝업으로 뜨는지 확인 (진입 차단 ≠ 신호 무시)
- [ ] **conf≥33% 신호 자동진입 정상** — 기존 A등급 자동진입 작동 이상 없음

### JointGateBlock 작동 확인 [P1]

- [ ] **차단 로그** — MetaGate+ToxGate 동시 reduce 발생 시 SIGNAL.log에 `[JointGateBlock] MetaGate(X.XX)×ToxGate(X.XX)=X.XXX < 0.50 → 진입 차단` 출현
- [ ] **정상 진입 미영향** — meta=reduce + tox=pass (합산≥0.50) 케이스는 정상 진입됨

### Degraded Mode 선제차단 확인 [P1]

- [ ] **선제차단 로그** — 다음 Degraded Mode 진입 사이클에서 `[HealthPolicy] Degraded 선제차단: streak=X.XX+X.XX ≥ 2` 출현
- [ ] **_last_pipe_ms 업데이트** — SYSTEM.log에서 파이프라인 latency가 매 사이클 갱신되는지 확인

---

## 2026-06-25 (235차 — 미니선물 전용 설정 검증) [최우선]

### CodeGuard 작동 확인 [P0]

- [ ] **정상 기동 로그** — `[DBG CK-3] 금월물코드=A0567 ... is_mini=True` 출현
- [ ] **CodeGuard 통과** — `[CodeGuard]` CRITICAL 로그 없음 (A05 계열 정상 통과)
- [ ] **계약스펙 로그** — `[ContractSpec] 계약스펙 확정: 미니선물 tick_size=0.02 pt_value=50,000` (235차-d에서 로그 태그 변경)

### spread_ticks 정상화 확인 [P1]

- [ ] **SIGNAL.log** — `[FeatureBuilder] tick_size 갱신: 0.0200` 출현 (기동 직후)
- [ ] EarlyWarmup 시 `_tick_size=0.02` 적용 (장 개시 전 spread_ticks 과소계산 없음)

### 미니선물 전용 설정 파일 최종 상태

- [x] `ui_prefs.json`: market="KOSPI200 미니선물" / symbol_code="A0567000" ✅
- [x] `config/settings.py`: TICK_SIZE=0.02 ✅
- [x] `config/secrets.py` (로컬): FUTURES_CODE_PREFIX="A05" ✅
- [x] `main.py`: 초기 _pt_value=50,000 ✅

---

## 2026-06-25 (234차 — 재시동 수정 검증) [최우선]

### X버튼 재시작 프로세스 종료 확인 [P0]

- [ ] **재시작 선택 후 프로세스 종료** — "재시작 (10초 후)" 선택 → `[AUTO-RESTART]` 10초 후 main.py 재기동 로그 출현
- [ ] **완전 종료 후 프로세스 사망** — "완전 종료" 선택 → Task Manager 에서 python main.py 프로세스 소멸 확인
- [ ] **GUARD 다음날 자동 통과** — 스케줄러 자동 기동 시 _exit_normally 정리 후 GUARD 없이 바로 시작

### 종목변경 배지 확인 [P1]

- [ ] **배지 표시** — UI 종목 변경 후 ⚠ 배지 출현 (기동 코드 ≠ UI 코드일 때만)
- [ ] **클릭 재시작** — 포지션 FLAT + 15:10 이전 조건 만족 시 quit() → AUTO-RESTART 재기동

---

## 2026-06-25 (232차 — ScaleFloor 효과 검증) [최우선]

### macro_risk_off ScaleFloor 작동 확인 [P0]

- [ ] **ScaleFloor 출현** — 급락 당일 `[ScalerFloor] macro_risk_off scale=X.XXX → floor=0.50 적용` 출현
- [ ] **z-score 억제** — `macro_risk_off` z ≤ 2.0 (이전 +15.78σ, D_FORCE 연속 트리거 없음)
- [ ] **D_FORCE consec=5 미발생** — SIGNAL.log에 `D_FORCE feat=macro_risk_off consec=5` 미출현

### WarmupRetrain 미실행 — 설계대로 동작 확인 [DONE 2026-06-24]

- [x] **원인 확인**: 장전(08:48) 기동 → L2368 장중 재시작 블록 미해당 → L3101 PreRetrain이 `_warmup_retrain_pending` 소비 → `_eod_retrain_ok=True`로 스킵. 버그 아님.
- [x] **개선**: EKS 해제 시 GBM 재학습 트리거 추가 (232차-b, ca55a8c)

### EKS 해제 후 GBM 재학습 확인 [P0]

- [ ] **재학습 시작** — EKS 해제 시 `[SHS-EKS] EKS 해제 → GBM 경량 재학습 시작` 출현
- [ ] **subprocess 완료** — `[GBM-64] subprocess 완료 (returncode=0)` 출현

### P1 후속 개선 (별도 검토) [P2]

- [ ] **identity 강제 임계 바이너리 분리** — `_BINARY_PASSTHROUGH` 목록 추가하여 raw_std 무관하게 이진 피처 항상 identity 유지 (P0 ScaleFloor 보다 구조적 수정)
- [ ] **macro_risk_off 연속형 리디자인** — 이진→연속형 점수화 검토 (GBM 재학습 필요, 중기)
- [x] **macro_vix CORE 강등** — 일봉 상수·SHAP ≈ 0·임계 비현실 확인 → 보조 피처 유지, 251차 f157046

---

## 2026-06-24 (231차 — EOD 수정 효과 검증) [최우선]

### ScalerWarmup 피처 수 확인 [P0]
- [ ] EOD 로그 `[ScalerWarmup] 피처 로드 완료 n=500 feat=97` — 120 → 97 변경 확인
- [ ] `[ScalerWarmup] 입력 데이터에 없는 피처 N개 (0 패딩)` 경고 미출현

### 피처 활성화 확인 [P0]
- [ ] EOD 로그 `1m 피처 슬라이싱: 97 → 13개` (+1), `15m → 16개` (+1), `30m → 12개` (+1)
- [ ] `1m: queue_directional_depletion 제외` 로그 미출현 (활성화 완료)
- [ ] `15m·30m: threshold_feasibility 제외` 로그 미출현

### macro chg 캐시 확인 [P1]
- [ ] MACRO 로그에서 sp500_chg가 장중 0으로 떨어지는 구간 없음 (또는 감소)

### need_add 잔여 피처 활성화 일정 모니터링 [P2]
- micro_regime_code (3,253행): 06-26 이후
- cvd_monotone_ratio (2,902행): 06-28~07-05
- opt_chain_pcr·opt_gex 3종 (1,897행): 06-29 이후 일괄
- opt_atm_call_oi·opt_atm_pcr (1,724/1,738행): 07-02 이후
- opt_atm_put_oi (1,616행): 07-09 이후
- opt_pcr_extreme_bearish (1,832행): 07-01 예상

---

## 2026-06-24 (229차 — 종료/재시작 흐름 검증) [234차에서 수정 완료, 재검증 대상]

### X 버튼 다이얼로그 확인 [P0]

- [ ] **다이얼로그 출현** — X 클릭 시 "완전 종료 / 재시작 (10초 후) / 취소" 3-way 선택창 표시
- [ ] **완전 종료 동작** — "완전 종료" 선택 → `data/_exit_normally` 생성 → 런처 `[AUTO-RESTART] 정상 종료 감지 — 재시작 안 함` 로그 → 배치창 자동 닫힘
- [ ] **재시작 동작** — "재시작 (10초 후)" 선택 → 플래그 없음 → 10초 후 `[AUTO-RESTART] main.py 재시작...` → 새 인스턴스 기동 [234차 QApplication.quit() 추가로 프로세스 확실 종료]
- [ ] **취소 동작** — "취소" 선택 → 창 닫히지 않음, 거래 계속

### 단일 인스턴스 가드 확인 [P1]

- [ ] **기존 인스턴스 감지** — 런처 재실행 시 `[GUARD] 이미 실행 중인 main.py 프로세스가 감지됐습니다` 출현
- [x] **장전 자동 Y** — 09:00 이전 기동 시 10초 후 자동 Y → 기존 프로세스 종료 후 재시작 [DONE 2026-06-24, 233차]

---

## 2026-06-24 (228차 — ExchangeCB 수정 효과 검증) [최우선]

### ExchangeCB 정상 감지 확인 [P0]

- [ ] **ExchangeCB 로그 출현** — 분봉 5분 이상 미수신 시 `[ExchangeCB] 분봉 N미수신(실경과=Xs) — 거래소 CB/단일가 구간 추정` 출현
- [ ] **Slack 도배 없음** — ExchangeCB 진입 후 90초마다 경보 STOP, 30분마다 생존 알림 1회만
- [ ] **CB 재개 후 _post_exchange_cb_resume** — `[ExchangeCB] 거래소 CB 해제` + `[GBM-64] 재학습 시작` + CB③ 쿨다운=30샘플 출현
- [ ] **_last_real_pipeline_dt 갱신** — 실 분봉 처리 후 워치독 실경과 정상 누적 (복구 스킵 시 타이머 리셋 없음)

### OptionChain 블로킹 해소 필요 (별도 개선 검토) [P1]

- [ ] `[LiveDBG] _poll_option_chain 지연 2897ms` — 메인 스레드 3초 블로킹 반복
  → CB 재개 직후 크래시 원인 후보. `_poll_option_chain` timeout 단축 또는 비동기 처리 검토

---

## 2026-06-24 (226차 — 64비트 subprocess 재학습 효과 검증) [최우선]

### GBM 64비트 subprocess 작동 확인 [P0]

- [ ] **subprocess 시작** — LEARNING.log에 `[GBM-64] 64비트 서브프로세스 재학습 시작 | ... pid=N` 출현
- [ ] **subprocess 완료** — `[GBM-64] subprocess 완료 (returncode=0)` 출현 (returncode≠0 이면 retrain_intraday_{}.log 확인)
- [ ] **GBM 배치 완료** — `[GBM] 웜업 배치 재학습 완료 | Xs 데이터=N행` 출현 (OOM 없이)
- [ ] **로그 파일 생성** — `logs/retrain_intraday_{YYYYMMDD_HHMMSS}.log` 존재 확인
- [ ] **결과 JSON 정리** — `data/_gbm_result_*.json` 임시 파일이 완료 후 삭제됨 (잔류 시 S0 읽기 오류)

### OOM 재발 없음 확인 [P1]

- [ ] **OOM 미출현** — `Unable to allocate 14.8 MiB` 미출현 (출현 시 py310_64 경로 확인)
- [ ] **모델 교체** — S0에서 `[Model] 재학습 완료 모델 교체 적용 (S0)` 출현

### 30m ConstOut 감소 [P2]

- [ ] **ConstOut 빈도 감소** — 이전 12~14시 4회 → 재학습 후 감소 기대
- [ ] **30m 정확도 회복** — GBM 교체 후 30m acc30m ≥ 35% 수준으로 회복 여부

---

## 2026-06-24 (225차 — sigma·QTimer·CB③ 수정 효과 검증) [최우선]

### sigma 수정 확인 [P0]

- [ ] **nonzero > 0** — `[sigma] sigma_at_t=X.XXXX% buf_n=20 nonzero=Y` 에서 Y ≥ 1 출력 확인 (0이면 _sigma_prev_price 커밋 누락)
- [ ] **sigma 정상 범위** — 오전 장 평균 σ ≥ 0.03% (KOSPI 200 선물 통상 분봉 변동률)
- [ ] **ConstOut 발생 빈도 감소** — 기존 하루 3~4회 → 없거나 1회 이하 기대

### QTimer → deferred 큐 확인 [P1]

- [ ] **GBM 재학습 완료 로그** — LEARNING.log에 `[GBM] 배치 재학습 완료 | Xs 데이터=N행` 출현 (08:55 PreRetrain 포함)
- [ ] **ConstOut 재적합 콜백** — SYSTEM.log에 `[ConstOut] [] 재적합 완료 → acc30m 버퍼 리셋` 출현 (ConstOut 발생 시)
- [ ] **모델 교체** — S0에서 `[Model] 재학습 완료 모델 교체 적용 (S0)` 출현
- [ ] **DeferredCB 오류 없음** — `[DeferredCB] 콜백 처리 오류` 미출현

### CB③ 쿨다운 확인 [P2]

- [ ] **재트리거 방어** — ConstOut 재적합 후 CB③ 즉시 재HALT 없음 확인
- [ ] **쿨다운 로그** — `reset_acc30m_buffer` 직후 15샘플 내 warn_count 미증가

### CB③ HALT 정상 복구 확인 [P3]

- [ ] **lift_cb3_halt 성공** — `[CB③→RESUME]` 로그 출현 (ConstOut 발생 시 GBM 재학습 후 자동 해제)
- [ ] **주기적 재시도 불필요** — `[CB③→RESUME] 주기적 재시도` 미출현이 정상 (콜백이 제대로 작동한 경우)

### GBM 타임아웃 10분 확인 [P4]

- [ ] **정상 완료 시 타임아웃 미발동** — `[GBM] 재학습 플래그 10분 타임아웃 강제 해제` 미출현 (재학습이 10분 내 완료되면 타임아웃 불필요)
- [ ] **PreRetrain 10분 초과 시 경보** — 타임아웃 로그 출현 시 batch_retrainer 성능 점검 필요

---

## 2026-06-24 (224차 — SGD 임계 완화 효과 검증)

### SGD 붕괴 복구 조기 발동 확인 [P0]

- [ ] **DN/UP 편향 시 80% 임계 복구 발동** — `[OnlineLearner] Xm SGD DN붕괴 자동 복구 (≥80% 12분 지속)` 로그 출현 시 기존 95% 대비 평균 3분 단축 여부 확인
- [ ] **BiasReset 연계 SGD 리셋** — BiasReset 발동 직후 `[OnlineLearner] Xm BiasReset 연계 SGD 리셋` 로그 출현 → conf=34.0% UP 고착 재발 여부 확인 (미출현이 정상: 편향 없음)
- [ ] **오발동 없음 확인** — 정상 원웨이 추세(적중률≥60%)에서 BiasReset 미발동 → SGD 리셋 미발동 (기존 `적중률≥0.55 → BiasReset 스킵` 조건이 보호)

---

## 2026-06-24 (222차 — EOD 마커·PreRetrain 수정 검증)

### PreRetrain 스킵 확인 [P0]

- [ ] **[PreRetrain] EOD 마커 파일 직접 확인** — `[PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-06-23) → PreRetrain 스킵 (session_state 미기록 보완)` 로그 출현 확인
- [ ] **PreRetrain 스킵** — `[PreRetrain] 08:55 사전 재학습 스킵 — 전날 EOD 재학습 성공 (동일 데이터 중복 불필요)` 로그 출현 (GBM 사전 재학습 시작 로그 없음)
- [ ] **session_state 저장** — 오늘 15:40 daily_close() 시 `eod_retrain_ok_date` 저장 여부 → `[DailyClose] EOD 재학습 마커 확인 — 스케줄러 완료, 내일 PreRetrain 스킵 예약` 로그 출현 (retrain_eod.py가 15:40 이전 완료 시)

### DailyClose retrain_str 알림 확인 [P1]

- [ ] **retrain_str 정상 출력** — 오늘 15:40 Slack 알림에 `"재학습: 완료 (스케줄러)"` 또는 `"재학습: 미완료 (내일 PreRetrain 보완)"` 포함 확인 (NameError 소멸)

---

## 2026-06-23 (220차 — 15:10 강제청산 + FINAL_CLOSE 검증)

### BrokerDirect 경로 동작 확인 [P0]

- [ ] **[BrokerDirectExit] 로그 출현** — 내부 FLAT이지만 broker 잔량이 있을 때
  `[BrokerDirectExit] 15:10 FLAT불일치 강제청산 — broker SHORT N계약 → BUY 직접주문` 확인
- [ ] **send_market_order ret=0** — `[BrokerDirectExit] send_market_order ret=0 SHORT N계약` 확인
  (ret≠0이면 broker API 오류 — 수동 청산 필요)

### FINAL_CLOSE 15:18 동작 확인 [P0]

- [ ] **정상 케이스** — 15:10에 이미 청산 완료 시 15:18에
  `[BrokerDirectExit] broker 잔고 없음 → 진짜 FLAT (15:18 FINAL_CLOSE 안전망)` 출력 확인
- [ ] **_final_close_done = True** — 이후 중복 발동 없음 확인

### 오늘 사고 미재발 확인 [P1]

- [ ] **15:20 Cybos 잔고 0** — 장 종료 후 Cybos HTS에서 보유 잔고 없음 확인
- [ ] **ExitAttempt 로그** — `[ExitAttempt] 시간청산 status=FLAT engine=0ct broker_cached=3ct` 출현 후
  BrokerDirect 경로 진입했는지 확인 (broker_cached=3이 key signal)

### P1 개선 — 분할체결 qty 누락 (레이스컨디션 방어) [P1]

- [ ] **`_ts_handle_entry_fill_cybos_safe` VWAP 보정 분기** — `position.quantity += fill_qty` 추가
  대상: `main.py` L10277~10288 의 보정 분기 (2번째 이후 분할체결)
  조건: 테스트 환경에서 4계약 전량 체결 시뮬레이션 후 적용 권장

---

## 2026-06-23 (219차 — 브로커 잔여계약 수정 검증)

### Bug1 잔여계약 PnL 처리 검증 [P0]

- [ ] **[잔여청산] 로그 출현** — 다음 번 다계약 청산 시 TRADE 탭에
  `[잔여청산] SHORT N계약 @ P.PP PnL=±X.XXpt (±Y원) │ 금일누적 Z원 [브로커FLAT 추정가]` 확인
- [ ] **DB 기록 확인** — trades DB에 `exit_reason="stuck_exit_remainder"` 행이 남는지 확인
- [ ] **엔진·브로커 괴리 축소** — 이전 256,130원 괴리가 ±50,000원 이내(수수료 오차 수준)로 줄었는지 확인

### Bug2 Sizer 잔고 갱신 검증 [P1]

- [ ] **Sizer 잔고 변동** — 거래 후 `[Sizer] 미니선물 잔고=481,XXX,XXX` 값이
  익일예탁금(CpTd6197 header2)으로 업데이트되는지 확인 (481,366,885 고정 탈피)
- [ ] **잔고 방향성** — 손실 거래 후 Sizer 잔고가 감소하는지 확인

### Bug3 TRADE 로그 확인 [P2]

- [ ] **blank-as-flat 경로** — 모의투자 blank rows 상황에서
  `[BrokerSync] blank-as-flat 강제: SHORT N계약 @ P.PP → FLAT` 로그 확인

### 잠재 이슈 — stuck_exit_remainder 추정가 정확도

추정가 = Chejan 확인된 마지막 체결가(`_sq_avg_price`) 사용.
실제 잔여계약 체결가와 ±0.5pt 이내이면 허용 오차 수준.
만약 시장이 급변해 추정가 오차가 크면 → 향후 개선안:
CpTd6197 header 8(총손익)에서 역산하는 방법 검토.

---

## 2026-06-23 (218차 — DriftRetrain OOM 수정 검증)

### 재학습 정상화 확인 [P0]

- [ ] **OOM 소멸** — `[Retrain] DB 로드 오류: Unable to allocate 14.8 MiB` 로그 없음 확인
- [ ] **사전 제한 로그 출현** — `[Retrain] 장중 경량 모드(DB): 39880 → 20000행 사전 제한 (OOM 방지)` 확인
- [ ] **재학습 완료** — `[GBM] 배치 재학습 완료 | ...초 데이터=20000행` 확인
- [ ] **DriftRetrain 단발성 종료** — 재학습 성공 후 `_last_retrain` 갱신되어 경과=1분 → 30분 이상 재트리거 없음 확인

### 쿨다운 동작 확인 [P1]

- [ ] **5분 쿨다운** — 만약 재학습 실패 시 5분 이상 간격 유지 확인 (분당 1회 트리거 없음)

### 30m 모델 편향 모니터링 [P2]

- [ ] **UP편향 개선** — `[Bias⚠] 30m UP편향` 비율이 80% 이하로 감소하는지 확인
- [ ] **acc30m 회복** — 재학습 완료 후 acc30m이 35% 이상으로 회복되는지 확인

---

## 2026-06-23 (217차 — 재시작 후 검증)

### 재시작 즉시 확인 [P0]

- [ ] **GDI 크래시 소멸** — `createDIB: CreateDIBSection failed` 로그 없음 확인
- [ ] **차트 정상 복원** — `restore_saved_geometry: 32-bit GDI 상한 초과 3030x1460 → 1920x1060` 로그 후 차트 정상 표시
- [ ] **1m/3m ACTIVE 전환** — 세션 시작 3분 후 `[Qualify] 1m 자격 획득 (verified=3 trained=0)` 로그 확인
- [ ] **자동 재시작 동작** — 장중 crash 발생 시 10초 후 `[AUTO-RESTART] #1 시도` 로그 출현

### 런처 로그 인코딩 확인 [P1]

- [ ] **한글 정상화** — launcher_*.log 파일에서 한글이 `2 0 2 6 - 0 6 - 2 2...` 대신 정상 출력되는지 확인 (PYTHONUTF8=1 효과)

### 잠재 리스크 [P2]

- [ ] **세션 중 창 리사이즈 시 안전성** — 사용자가 차트를 1920px 초과로 늘렸을 때 `paintEvent 거대 캔버스 차단` 로그 없이 정상 그려지는지 (3000 이하 허용)
- [ ] **closeEvent cap 동작** — 세션 종료 시 ui_prefs.json에 `w ≤ 1920, h ≤ 1060`으로 저장되는지 확인

---

## 2026-06-23 (216차 — CB③ HALT 해제 검증)

### ConstOut + HALT 재발 시 확인 [P0]

- [ ] **CB③ HALT 발동** — `[CRITICAL] [CB] 당일 시스템 정지 | 30분 정확도` 로그 이후 `_halt_cause="cb3"` 설정 확인 (직접 확인 불가 → 아래 로그로 간접 확인)
- [ ] **HALT 해제 로그 출현** — `[CB③] ConstOut 회복 — HALT 해제 (당일 HALT N회, 진입 사이즈 풀사이즈)` 로그 확인
- [ ] **거래 재개** — HALT 해제 후 STEP7 진입 평가 정상 진행 확인 (`is_entry_allowed() == True`)
- [ ] **Slack 알림** — "ConstOut 회복 후 CB③ HALT 해제" 알림 수신 확인

### CB② (연속 손절) 보호 확인 [P1]

- [ ] **CB② HALT는 해제 안 됨** — 연속 손절 HALT 후 GBM 재학습 완료 시 `[CB③] HALT 해제 불가 — 원인이 CB③ 아님 (cause='cb2')` 로그 출현 (재현 어려우나 로그 패턴 확인)

### 잠재 리스크 [P2]

- [ ] **daily_halt_count=3 이상 시 해제 거부** — `[CB③] HALT 해제 불가 — 당일 HALT 3회` 로그 출현 확인 (3회 HALT는 드문 상황)

---

## 2026-06-23 (214차 — ERR-FATAL 수정 + 프리장 Phase 재설계 검증)

### 내일 장초반 즉시 확인 [P0]

- [ ] **ERR-FATAL 소멸** — `[ERR-FATAL] minute_chart_set_direction` 로그 없음 (오늘 09:00~09:07 매분 발생 → 내일 없어야 함)
- [ ] **자동진입 정상화** — 앙상블 grade=A·B·C 판정 후 STEP7 진입 평가까지 정상 진행 확인
- [ ] **Cybos RT 08:45 선행 구독** — `[EarlyWarmup] Cybos RT 08:45 선행 구독 시작` 로그 출현 확인
- [ ] **Phase1~4 전 단계 발동** — `[PreMarket] Phase1 refit 기동` ~ `Phase4 refit 완료` 4회 모두 출력
- [ ] **z경고 단조감소** — Phase 진행하며 z경고 수가 줄어드는 추이 확인 (3봉 역효과 없음)

### Phase별 z경고 목표 [P1]

| Phase | 봉 수 | 시각(추정) | z경고 목표 |
|---|---|---|---|
| Phase1 | 3봉 | ~08:47 | ≤10개 |
| Phase2 | 5봉 | ~08:49 | ≤7개 |
| Phase3 | 10봉 | ~08:54 | ≤5개 |
| Phase4 | 14봉 | ~08:58 | ≤3개 |

### 잠재 리스크 [P2]

- [ ] **Cybos RT 중복 구독** — 08:45 선행 구독 후 08:55 `pre_market_setup()`에서 또 구독 시도. `_running` 체크로 보호되나, 이미 실행 중이면 `_rd.start()` 내부에서 no-op인지 확인
- [ ] **z경고 악화 태그 출현 시** — `⚠ 악화 (봉 수 부족)` 로그 출현 시 Phase 최소 봉수 추가 상향 검토 (3→5)
- [ ] **방향예측 레인 표시 정상화** — ERR-FATAL 해소 후 봉차트 X축 위 방향 색상 바가 나타나는지 확인 (210차 NEXT_TODO 검증)

---

## 2026-06-19 (212차 — 차트 DPI 1.5× 근본 수정)

### 다음 재시동 시 확인 [P0]

- [ ] **y<0 보정 로그** — `[ChartDBG] restore_saved_geometry: y=N < 0 → y=0으로 보정` 로그 출현 확인 (보조 모니터 avail.top()<0 환경에서만)
- [ ] **"Unable to set geometry" 미발생** — launcher 로그에서 `QWindowsWindow::setGeometry: Unable to set geometry` 메시지 사라짐 확인
- [ ] **차트 창 크기 정상** — 자동팝업 후 3030×1460 (저장값) 또는 적정 크기로 열림, 4547×2124 미발생 확인
- [ ] **봉차트 정상 렌더링** — 차트 크기에 무관하게 봉 데이터 표시 (paintEvent guard 6000으로 상향 효과)

### pickle protocol=4 (213차) [P1]

- [ ] **KeyError: 63 크래시 미발생** — GBM 재학습 후 스케일러 저장/로드 시 크래시 없음 확인
- [ ] **기존 pkl 파일 호환** — 기존 joblib 저장 파일 로드 시 정상 동작 확인 (로드는 joblib 유지)

### 잠재 리스크 [P2]

- [ ] **y=0 보정 부작용** — 사용자가 의도적으로 창을 보조 모니터 최상단(y=avail.top())에 두려 할 때 y=0으로 밀려남 (몇 픽셀 차이, 허용 가능)
- [ ] **_center_on_second_screen y=max(y,0)** — 보조 모니터 height가 작을 경우 y가 음수가 될 수 있는 엣지케이스 처리 확인

---

## 2026-06-19 (210차 — X축 방향예측·레짐 레인)

### 다음 장 시작 시 확인 [P0]

- [ ] **방향예측 레인** — 장 시작 후 첫 분봉 완성 시 레짐 바 위 4px 방향 색상 바가 나타나는지 확인
- [ ] **레짐 레인** — 기존 레짐 바가 그대로 표시되는지 확인 (회귀 없음)
- [ ] **현재봉 빈칸** — 가장 우측 봉(현재봉)은 두 레인 모두 빈칸인지 확인
- [ ] **재시작 복원** — 장중 재기동 후 세션 시작부터 재기동 직전까지 방향 이력이 복원되는지 확인

---

## 2026-06-19 (208차-추가 — 차트 창 크기 복원 버그 수정)

### 다음 장 시작 시 즉시 확인 [P0]

- [ ] **자동팝업 크기** — 자동팝업 설정 후 프로그램 재시동 시 차트가 `_center_on_second_screen` 크기(1680 이하 폭)로 열리는지 확인 (이번 기동은 `chart_dialog_geometry` 초기화 상태)
- [ ] **Ctrl+Shift+X 닫기 후 크기 저장 확인** — 차트 창 크기 조정 후 Ctrl+Shift+X 닫기 → `data/ui_prefs.json`의 `chart_dialog_geometry`에 조정된 크기(w < 2880)가 저장됐는지 확인
- [ ] **재열기 시 크기 복원** — 저장된 크기로 재열기 시 같은 크기로 열리는지 확인
- [ ] **최대화 상태 비저장** — 창 최대화 후 Ctrl+Shift+X 닫기 → `chart_dialog_geometry`가 이전 정상 크기 그대로 유지되는지 확인 (최대화 크기로 덮어쓰이면 안 됨)

### 잠재 리스크 [P2]

- [ ] **88% 상한이 너무 작은 경우** — 사용자가 의도적으로 화면의 90~100% 크기로 사용하고 싶은 경우 88% 상한에 막힘. 필요 시 95%로 완화 고려
- [ ] **`isMaximized()` on Windows** — 비최대화 상태에서도 Windows WM 이벤트로 인해 `isMaximized()`가 True를 반환하는 경우 있을 수 있음. 이 경우 정상 크기 저장 스킵 → 이전 저장값 유지 (해결책: 로그 확인)

---

## 2026-06-19 (208차 — 예측 카드 제거)

- [ ] **UI 확인** — 앱 재시동 후 좌측 패널에 호라이즌 이름 레이블 + On/Off 체크박스만 표시되는지 확인
- [ ] **On/Off 동작** — 체크박스 토글 시 앙상블 집계 필터가 정상 적용되는지 확인 (_hz_enabled 참조 경로)

---

## 2026-06-19 (207차 — 1분봉 차트 복원 4종 수정)

### 다음 장중 재시동 시 즉시 확인 [P0]

- [ ] **데이터 복원** — Ctrl+Shift+X 열기 후 당일 분봉 차트(09:00~현재)와 거래 이력 표시 확인
- [ ] **[ChartDBG] 로그** — `_reload_today_bg 완료 | total=Xms raw_candles=Y봉 trades=Z건` 로그 출현 확인 (X ms 이내에 완료, Y봉 > 0)
- [ ] **레짐 색상** — 봉 색상이 RISK_ON(녹)/NEUTRAL(회)/RISK_OFF(적)로 정상 표시되는지 확인
- [ ] **활성 포지션 마커** — 재시동 시 포지션 보유 중이면 차트에 진입 마커 표시 확인

### 다음 장중 Ctrl+Shift+X 토글 시 확인 [P0]

- [ ] **닫기 후 재열기** — Ctrl+Shift+X로 닫고 다시 열 때 데이터·거래 이력 유지 확인
- [ ] **윈도우 위치 복원** — 재열기 시 이전 위치/크기 그대로 복원 확인
- [ ] **자동팝업 위치** — 자동팝업 모드에서도 마지막 저장 위치로 복원 확인 (과거에는 제2모니터 중앙 고정이었음)

### 메인 프로그램 정상 종료 시 확인 [P1]

- [ ] **geometry 저장** — 차트 열린 상태로 메인 종료 후 `data/ui_prefs.json`에 `chart_dialog_geometry` 키 존재 확인
- [ ] **다음 기동 시 위치 복원** — 저장된 geometry로 차트가 열리는지 확인

### 잠재 리스크 [P2]

- [ ] **pyqtSignal emit from thread** — Python 3.7 32-bit에서 `pyqtSignal.emit(list, list, list)` cross-thread 동작 검증. 만약 크래시 발생 시 대안: `QMetaObject.invokeMethod` 또는 Queue + QTimer polling
- [ ] **_reload_running 초기화** — `_reload_running`이 `__init__`에서 초기화되지 않고 `getattr(self, '_reload_running', False)`로 처리됨. 이 패턴은 Python에서 안전하지만, 명시적 초기화가 더 명확함 (차후 리팩토링 시 정리)
- [ ] **이중 reload** — 기동 시 `singleShot(0, _start_reload_thread)` + `toggle_minute_chart_dialog`의 `_start_reload_thread()` 두 번 호출됨. `_reload_running` 플래그로 중복 방지되나, 첫 번째 완료 후 두 번째가 시작될 수 있음 (정확성 무해, 이중 DB 쿼리만 발생)

---

## 2026-06-19 (206차 — poc_distance VP 버퍼 DB 복원)

### 다음 재시작 시 즉시 확인 [P0]

- [ ] **VP 복원 로그** — 기동 시 `[VPRestore] VP 버퍼 복원 완료: 60봉` 로그 출현 확인
- [ ] **[AnalysisRestore] vp_bars=60** — 로그에서 `vp_bars=60` 확인 (0이면 raw_candles 비어있음)
- [ ] **poc_distance z폭발 미발생** — 재시작 직후 첫 5분간 `[ScalerMonitor]` 로그에서 poc_distance 극단값 없음 확인

### 잠재 리스크 [P2]

- [ ] **당일 첫 기동(DB 비어있음)**: raw_candles가 0행이면 vp_bars=0 → cold start 유지 (정상 fallback). 당일 기동 직후는 여전히 cold start — 09:00 이전 pre-market 봉으로 VP가 채워질 때까지 poc_distance z 주의
- [ ] **스케일러 오염 잔재**: 과거 DB의 cold-start 0.0값은 기존 scaler에 이미 반영됨. 다음 scaler refit 때까지 std가 낮게 유지될 수 있음 (D_FORCE 또는 C_PERIODIC refit으로 자연 교정)

---

## 2026-06-19 (205차 — 5m FL편향·30m acc·SGD 악순환 수정)

### 내일 DriftRetrain 발동 시 즉시 확인 [P0]

- [ ] **BiasReset 즉시 해제** — DriftRetrain 완료 후 `[GBM] 재학습 완료 → BiasReset·SGD 상태 초기화` 로그 출현 확인
- [ ] **5m uniform fallback 해제** — 재학습 직후 `[BiasReset] 5m FL편향 → uniform fallback 해제` 로그 (또는 해제 없이 재평가 시작 — `_bias_override_horizons` 클리어됨)
- [ ] **SGD 비중 30%로 복구** — `[OnlineLearner] 가중치 조정 SGD=30% GBM=70%` 수준으로 복귀 확인 (기존 15%)

### 내일 DriftRetrain 조기 트리거 확인 [P1]

- [ ] **조기 트리거 로그** — acc<15% 시 `[DriftRetrain] acc30m=X% < 15% → 조기 트리거 (30분 경과)` 로그 출현 확인
  - 기존: acc=10%이어도 60분 대기 → 내일은 30분 후 발동 기대
- [ ] **조기 트리거 오발동 방지** — n<15건 상태에서 조기 트리거가 잘못 발동되지 않는지 확인

### 다음 GBM 재학습 시 [P1]

- [ ] **30m FL 레이블 비율 증가** — `[Retrain] y_dict` 로그에서 30m FL 비율이 이전 대비 증가했는지 확인 (PATH_LABEL_RATIO 0.55→0.45 효과)
- [ ] **30m acc 회복** — 재학습 후 30m acc가 25% 이상으로 회복되는지 CB③ 버퍼 추적

### 잠재 리스크 [P2]

- [ ] **reset_daily 타이밍 충돌** — `_on_gbm_retrain_done`이 호출되는 시점에 파이프라인이 실행 중이면 `_acc_buf` 초기화와 race condition 가능성 (QTimer.singleShot이 메인 스레드이므로 낮지만 확인)
- [ ] **BiasReset 재발동 주기 단축** — 재학습 후 클리어된 상태에서 GBM이 여전히 편향이면 10분 후 재발동. 재학습-BiasReset-재학습 반복 루프 여부 모니터링
- [ ] **30m PATH_LABEL_RATIO 0.45 과도 완화** — FL 레이블이 지나치게 많아져 30m 모델이 FL 과다 예측으로 전환될 가능성. 재학습 후 30m UP/DN/FL 분포 확인

---

## 2026-06-19 (204차 — ConfTrend refresh 장 후반 지연 수정)

### 내일 장중 확인 [P0]

- [ ] **step3_db_query ≤30ms 유지** — 11:00 이후에도 `[LiveDBG] ConfTrend step3_db_query` 30ms 이하인지 확인 (기존 11:53 906ms)
- [ ] **step2_completed_map ≤10ms** — `[LiveDBG] ConfTrend step2_completed_map` 10ms 이하인지 확인 (기존 343ms)
- [ ] **전체 refresh ≤100ms** — `[LiveDBG] ConfTrend total` 100ms 이하로 하루종일 유지

### 잠재 리스크 [P1]

- [ ] **영구 연결 오류 시 재연결 확인** — `step3_db_EXCEPTION` 로그 후 다음 refresh에서 자동 재연결되는지 확인 (`_pred_conn = None` 후 `_get_pred_conn()` 재생성)
- [ ] **wal_autocheckpoint=100 부작용** — 더 잦은 체크포인트로 PREDICTIONS_DB 쓰기 경합 증가 여부. `[DBWriter]` 큐 포화 로그 모니터링

---

## 2026-06-19 (203차 — EKS z_ok 버그 수정)

### 배경
EKS 회복 평가에서 `_last_canary_z_warn`(stale 고착값)을 사용하던 버그 수정.
- `_last_canary_z_warn`은 `pre_market_setup()` 안 Canary 블록에서 **1회만** 설정(08:55, z=18)
- PreMarket refit 완료 후 실제 z=4로 줄었지만 회복 시 여전히 18 참조 → z_ok=False → 영구 차단
- 수정: `_p3_z_warn = getattr(self.model, "last_z_warn_count", 0)` (매분 predict_proba 갱신값)
- 커밋: 202차

### 내일 장초반 즉시 확인 [P0]

- [ ] **EKS 회복 z_ok=True** — 회복 시도 시 `z_ok=True(z=N)` (N<15) 로그 확인
  - 기존: `z_ok=False(z=18)` 매 회복 시도마다 반복 → 내일은 `z_ok=True` 기대
- [ ] **EKS 미발동 또는 정상 해제** — EKS 발동 시에도 30분 후 conf/z 조건 충족 시 자동 해제되는지 확인
  - z경고가 15개 미만으로 안정화되면 `[SHS-EKS] EKS 자동 해제 (회복 #N)` 로그 출현

### 잠재 리스크 [P1]

- [ ] **last_z_warn_count가 EKS 발동 직전 파이프라인 값** — EKS 판정(09:05) 직전 파이프라인이 실행됐는지 확인. 만약 09:00~09:05 conf=0%여서 `last_z_warn_count`가 발동 당시 z와 같다면 변화 없음
- [ ] **오늘 conf_hits 조건 검토** — 오늘 conf_hits=10/10이었지만 mc=25% 기준. 내일도 GAP_OPEN mc 수준에 따라 달라질 수 있음

---

## 2026-06-20 (201차 — 프리장 점진 재적합 효과 검증)

### 내일 장초반 즉시 확인 [P0]

- [ ] **Phase1~4 refit 완료 로그** — `[PreMarket] Phase1 refit 기동 (1봉 z경고=X개)` → `Phase1 refit 완료 n=501봉 z경고 X→Y개` 패턴 4회 출력 확인
- [ ] **z경고 수렴 추이** — Phase1→4 진행하며 z경고 단조감소 확인 (목표: Phase4 완료 후 ≤5개)
- [ ] **EKS 미발동** — `[SHS-EKS] Early Kill Switch 발동` 로그 없음 (오늘 09:05 발동 → 내일 없어야 함)
- [ ] **GAP_OPEN conf 정상화** — `conf_max`가 GAP_OPEN mc(≈45%) 이상으로 기록되는지 확인
- [ ] **피처 DB 저장 에러 없음** — `[PreMarket] 피처 DB 저장 실패` 로그 없음 확인

### Phase별 z경고 목표 [P1]

| Phase | 봉 수 | 시각 | z경고 목표 |
|---|---|---|---|
| 기동 전 | 0봉 | 08:45 전 | 18개 (오늘 실측) |
| Phase1 완료 | 1봉 | ~08:46 | ≤15개 |
| Phase2 완료 | 5봉 | ~08:50 | ≤10개 |
| Phase3 완료 | 10봉 | ~08:55 | ≤7개 |
| Phase4 완료 | 14봉 | ~08:59 | ≤5개 |

### 잠재 리스크 [P2]

- [ ] **Phase 건너뜀** — `_scaler_refresh_running=True` 상태에서 다음 STEP 봉 도착 시 해당 Phase 스킵. Phase 번호가 연속되지 않으면 EarlyWarmup 오버랩 의심
- [ ] **동기 DB write 블로킹** — 프리장 봉 `save_candle_and_features()` 메인스레드 동기 호출. `[PreMarket]` 로그 간격이 60초 이상이면 비동기 전환 검토
- [ ] **갭 매우 큰 날 Phase1 역효과** — 1봉으로 scaler 왜곡 가능. Phase1 완료 후 z경고 증가 시 `PRE_MARKET_REFIT_STEPS` 최솟값 3으로 상향 검토

---

## 2026-06-19 (199차 후속 — UI 블로킹 수정 검증)

### 내일 장중 즉시 확인 [P0]

- [ ] **파이프라인 재시작 반복 없음** — 장중 `재기동 #N cause=STARTUP` 로그가 없어야 함 (199차 이전 14:18까지 8회 재시작)
- [ ] **`[LiveDBG] ConfTrendWidget.refresh slow`** — 200ms 이하로 줄었는지 확인. 초과 시 MAX_ROWS 추가 감소 검토
- [ ] **`_tick_header 간격` 경고 없음** — 장중 2초 이상 갭이 없어야 파이프라인 안전
- [ ] **1분봉 차트 응답없음 없음** — 마우스 hover 및 닫기 버튼 정상 동작 확인

### 장중 후 정리 예정 [P1]

- [ ] **LiveDBG 진단 코드 제거** — 이슈 확인 완료 후 아래 파일에서 WARNING 로그 제거:
  - `dashboard/main_dashboard.py` (_tick_header, paintEvent, ChartDBG, _scheduler_tick)
  - `main.py` (BalanceRefresh, _fetch_investor_data, _poll_option_chain)
  - `collection/cybos/api_connector.py` (request_futures_balance 호출 스택)
  - `strategy/runtime/session_recovery_service.py` (_apply 단계 타이밍)
  - `dashboard/panels/conf_trend_widget.py` (step1~6 타이밍)
- [ ] **`conf_trend_widget.py` step 타이밍 제거** — 검증 완료 후 _do_refresh() 내 LiveDBG WARNING 삭제

### 잠재 리스크 [P2]

- [ ] **In-place 업데이트 첫 렌더링** — 최초 setItem() 300회 (~1200ms) 장중 첫 파이프라인 타이밍과 겹치면 지연. `ConfTrendWidget.__init__`의 `self.refresh()` 초기 호출은 이벤트 루프 이전이므로 빠름
- [ ] **`restore_saved_geometry` geometry 재저장** — `closeEvent` 가드가 2480×1473 (2모니터)을 합법으로 판단해 저장 → Qt가 3688×2060으로 확장하는 문제 재발 가능. `[ChartDBG] 범위 초과 — 복원 스킵` 로그로 모니터링

---

## 2026-06-18 (197차 — P8 스케일러 재적합 retrain_eod.py 재배치)

### 내일 즉시 확인 [P0]

- [ ] **retrain_eod.py에서 P8 로그 출현** — `logs/retrain_eod_20260619.log`에서 `[P8] 스케일러 재적합 완료 n=500봉` 확인
- [ ] **daily_close() 로그에 `[P8]` 없음** — `20260619_SYSTEM.log`에서 `[P8] EOD 스케일러 재적합` 로그 없어야 함 (재배치 효과)
- [ ] **p8_last_success_date 갱신** — 내일 retrain_eod.py 완료 후 `data/session_state.json`에 `p8_last_success_date: 2026-06-19` 기록 확인

### 잠재 리스크 [P1]

- [ ] **retrain_eod.py 실패 시 P8 미실행** — retrain_eod.py 예외 발생(catch 블록)이면 p8_scaler_refit() 미호출. 내일 `data/eod_retrain_fail_20260619.txt` 없음 확인. 있으면 `catch_up_eod.py --skip-retrain` 수동 실행
- [ ] **스케줄러 오늘 미실행 원인** — `LastTaskResult: 267011` (한 번도 실행 안 됨). 내일 15:45 실행 전 `Get-ScheduledTask -TaskName "MireukiEODRetrain"` 상태 확인 → 필요 시 `register_eod_scheduler.ps1` 재실행

---

## 2026-06-18 (193차 — GBM 재학습 완료 모델 교체 race condition 수정)

### 배경
`_on_gbm_retrain_done`에서 `_load_all()` 즉시 호출 → `run_minute_pipeline` `predict_proba()`와
동시 실행 → `ValueError: X has N features, expected M` → `apply_error_policy(FATAL)` → 자동재시작.
오늘(2026-06-18) RF 로드 완료 후 8초 → RESTART 패턴 7회 반복 관찰. 커밋: `6ae2b91`

### 재시작 후 확인 [P0]

- [ ] **`[Model] 재학습 완료 모델 교체 적용 (S0)` 로그 출현** — SIGNAL.log에서 확인. 재학습 완료 후 이 로그가 나오면 플래그 방식으로 정상 작동
- [ ] **RESTART 반복 패턴 소멸** — WARN.log에서 `[RF] 로드 완료` 후 8초 이내 `[RESTART]` 없음 확인
- [ ] **`[Model] 재학습 완료 — 다음 파이프라인 시작 전 모델 교체 예약` 로그** — LEARNING.log에서 재학습 완료 직후 출현

### 잠재 리스크 [P1]

- [ ] **S0 모델 교체 지연으로 인한 오래된 모델 1분봉 사용** — 재학습 완료 후 다음 분봉까지 (최대 1분) 이전 모델 사용. 이건 race condition보다 훨씬 낮은 위험
- [ ] **`_pending_model_reload` 초기화 여부** — 프로그램 시작 시 `getattr(..., False)` 기본값 False로 정상 처리됨

---

## 2026-06-18 (192차 — macro_risk_off AutoMask CORE 면제)

### 배경
VIX>28 이진 신호 `macro_risk_off`가 학습기간 σ≈0 → 실거래 z=+22.34 폭발 → AutoMask 소거 →
15m/30m GBM FLAT=0.80 과신뢰 → 앙상블 conf=20% 고착 (09:00~09:55+ 전 구간). 어제 커밋과 무관.
커밋: `c3875dd`

### 재시작 후 확인 [P0]

- [ ] **AutoMask 목록에서 macro_risk_off 소멸** — `[AutoMasked]` 로그에 `macro_risk_off` 없어야 함 (VIX 급등 상황에서도)
- [ ] **conf=20% 고착 해소** — VIX 급등 구간에서 앙상블 conf가 20% 바닥에 고착되지 않음 확인
- [ ] **15m/30m GBM FL=0.8000 고착 소멸** — `[CONF⚠]` 15m/30m conf=0.8000 로그 없어야 함
- [ ] **ZeroDiag 원인 변화** — `극단z값포함(macro_risk_off)` 차단 사유 소멸 확인

### 잠재 리스크 [P1]

- [ ] **GBM 과방향 예측 여부** — macro_risk_off=1.0이 GBM에 직접 입력 시 특정 방향(DN)을 과신뢰할 수 있음. VIX 급등 상황에서 conf가 너무 높아지는지 (60%+) 모니터링
- [ ] **단기(1m~5m) AutoMask 잔존** — short 그룹은 의도적으로 미면제. 1m~5m에서 macro_risk_off AutoMask 유지는 정상

---

## 2026-06-17 (191차 — EOD 재학습 OOM 해결 + py310_64 장외 스케줄러)

### 내일 즉시 확인 [P0]

- [DONE 2026-06-18] **스케줄러 첫 실행 성공** — 오늘 스케줄러 미실행(LastTaskResult: 267011). 수동 `retrain_eod.py`로 대체 처리. 스케줄러 원인은 197차 P1 참조
- [DONE 2026-06-18] **완료 마커 생성** — `data/eod_retrain_done_20260618.txt` 확인 (6/6 호라이즌, 194.3s)
- [DONE 2026-06-18] **재학습 로그 정상** — `logs/retrain_eod_20260618.log` 6/6 교체, 합계 194.3s
- [DONE 2026-06-18] **EarlyWarmup 경고 소멸** — 08:45 `완료 n=500봉` 정상, 노후 경고 없음

### 잠재 리스크 [P1]

- [DONE 2026-06-18] **스케줄러 실패 시 대응** — 수동 retrain_eod.py + catch_up_eod.py --skip-retrain 실행 완료
- [DONE 2026-06-18] **daily_close OOM 로그 계속 출력** — 197차에서 P8을 retrain_eod.py로 재배치 완료. in-process 재학습 OOM은 여전히 발생 가능하나 잔여 단계(WAL 등) 계속 진행됨

---

## 2026-06-17 (190차 — SGD B군 피처 N분봉 교정)

### 다음 장 즉시 확인 [P0]

- [ ] **B군 교정 효과** — 10m/15m/30m SGD acc가 이전(189차 42% 평균) 대비 개선되는지 관찰
- [ ] **캐시 스킵 정상** — 장 초반(09:01~09:29) 30m 교정이 조용히 스킵되는지 (WARN 로그 없음)
- [ ] **슬라이싱 일관성** — B군 교정 후 슬라이싱이 정상 작동하는지 (`[SGD] N건 학습` 로그 이상 없음)

### A안 전체 구현 트리거 조건 (모니터링)

- [ ] Phase C need_add 14개 피처 pkl 추가 완료 여부
- [ ] SGD acc 48% 이상 4주 평균 유지 여부
- [ ] 모의투자 4주 완료 여부

---

## 2026-06-17 (189차 — SGD 붕괴 감지 + BAR_CACHE_DECAY + FULL_RESET_PENDING)

### 다음 장 즉시 확인 [P0]

- [ ] **UP/DN 붕괴 자동 복구 로그** — `[OnlineLearner] Xm SGD UP붕괴 자동 복구 (≥95% 15분 지속)` 또는 `DN붕괴` 로그가 실제 붕괴 시 출력되는지 확인
- [ ] **conf 고착 분수 감소** — `[CONF⚠] Xm bar_age=N` 에서 N이 이전(19분) 대비 낮아지는지 확인 (BAR_CACHE_DECAY 효과)
- [ ] **SGD 리셋 미발동** — 재시작 후 GBM 재학습 완료 시 `[SGD] threshold 교체 후 완전 리셋 완료` 로그 없음 확인 (FULL_RESET_PENDING=False 효과)
- [ ] **SGD비중 안정성** — GBM 재학습 완료 후 SGD비중이 30%로 초기화되지 않고 이전 값 유지되는지 확인

### 잠재 리스크 모니터링 [P1]

- [ ] **BAR_CACHE_DECAY 과감쇠 여부** — 15m bar_age=14 → 0.92^14=0.33배. 신호가 너무 약해져 FL로 수렴하는지 모니터링. 심하면 decay 값 완화 검토
- [ ] **P2-D 필터 과도 차단** — 오늘 89.4% 차단. conf<0.52 임계값 완화(0.44~0.46) 검토 필요

---

## 2026-06-17 (185·186차 — pred_select CB⑤ 근본 수정 + FL편향 3종 수정)

### 다음 장 즉시 확인 [P0]

- [ ] **[185차] pred_select < 300ms** — 09:31~09:45 CB⑤ 패턴 소멸. `[Buffer-Timing]` 경보 없음 확인
- [ ] **[185차] CB⑤ 미발동** — 09:30~09:50 `[CB] 5분 진입 정지` 로그 없음
- [ ] **[186차] UP예측 출현** — 오전 상승장에서 `앙상블: dir=+1` 로그 확인 (기존 UP=0건)
- [ ] **[186차] EarlyDirDamp 조기 발동** — `[EarlyDirDamp] 3m FL=47% 10min → weight×0.2` 형태 로그 확인
- [ ] **[186차] BiasReset 조기 발동** — FL=70% 이상 10분 → `[BiasReset] Xm FL편향 70% Y분 지속` 로그

### 재학습 후 확인 [P1]

- [ ] **FLAT_CAP 효과** — 재학습 후 `[Retrain] X동적가중치 FL=0.55 UP=0.65` 비율 확인 (DEBUG 로그)
- [ ] **3m/5m 예측 분포 정상화** — `[Bias] 3m UP=X DN=X FL=X` 에서 UP≥5건 이상 출현

---

## 2026-06-17 (184차 — 봉차트 손익 이력 분실 3종 버그 수정)

### 다음 장 즉시 확인 [P0]

- [ ] **[Fix1] stuck exit 시 차트 이력 보존** — stuck exit(브로커 무포지션) 발생 시 `[ChartFix] stuck exit 차트·DB 합성 기록:` 로그가 SYSTEM.log에 출력되고, 봉차트에 해당 거래 스팬이 남는지 확인
- [ ] **[Fix2] 마커 위치 정확도** — 체결 봉차트에서 청산 마커가 실제 체결 분봉에 위치하는지 확인 (기존 1~2초 오프셋 개선)
- [ ] **[Fix3] ChartWarn 무음 로그** — 정상 동작 시 `[ChartWarn] record_exit(finalize=True) called with no active_trade` 로그가 나오지 않아야 함. 나온다면 새로운 stuck 경로 존재 가능성

### 이월 관찰 이슈

- [ ] **trades DB 재확인** — stuck exit 발생 후 재열기 시 차트에 해당 거래가 표시되는지 (`SELECT * FROM trades WHERE exit_reason = 'stuck_exit_flat'`)

---

## 2026-06-17 (183차 — retrain worker MemoryError 미처리 버그 수정)

### 수정 배경
- 06-16 EOD 재학습이 자동종료(15:41:40)로 인터럽트 → eod_retrain_ok_date 미저장
- 06-17 08:55 PreRetrain 시작 → 40093행 풀 GBM 학습 중 MemoryError 발생
- `except Exception`이 BaseException(MemoryError) 못 잡음 → `_gbm_retrain_running=True` 고착
- 장중 모든 재학습 skip → `_pre_retrain_done=False` → 사이즈 ×0.6 하루 종일 지속

### 다음 장 즉시 확인 [P0]

- [ ] **MemoryError 재발 없음** — LEARNING.log에 `[Retrain] 완료 | ...초 | 성공=6/6` 로그 확인 (08:55~08:59 사이)
- [ ] **`_pre_retrain_done=True` 해제** — `[EntryGate] GBM 첫 재학습 완료(방법3 레이블) — 사이즈 제한 해제` (SYSTEM.log)
- [ ] **사이즈 축소 ×0.6 없음** — `[EntryGate] 사이즈 축소 ×0.6 (GBM 재학습 전)` 로그 없음 확인
- [ ] **MemoryError 발생 시 플래그 해제 확인** — 혹시 재학습 실패하더라도 `[GBM] ...재학습 건너뜀: MemoryError` 로그가 LEARNING.log에 남는지 확인 (이전엔 아무 로그도 없었음)

### 이월 관찰 이슈

- [ ] **pred_select 5-12초 병목 (S1)** — verified=6 전환 시점(30m 첫 채점 후) predictions DB 쿼리 풀스캔 의심. `ts`/`horizon` 컬럼 인덱스 추가 검토
- [ ] **30m FL편향 87%** — 09:50~10:07 구간 FL편향 심각. BiasReset 발동 여부 확인

---

## 2026-06-17 (182차 — EOD MemoryError 복구 + validate_and_resync() 허위 정합성오류 수정)

### 다음 장 즉시 확인 [P0]

- [ ] **`[Model] 정합성 오류` 로그 재발 없음** — 재시작·재학습 후 허위 불일치 미발생 확인
- [ ] **`resync_mismatch` 사유 비계획 GBM 재학습 없음** — `[GBM] 수동 재학습 시작 | resync_mismatch` 로그 미발생 확인
- [ ] **오늘(06-16) 09:01~13:03 구간 진입판단 재검토** — 버그로 인해 GBM이 일시적으로 FLAT 디폴트(33.3%)였을 가능성 있는 구간. SGD 블렌딩 비중이 낮았던 분봉이 있었는지 LEARNING.log 확인
- [ ] **EOD 재학습 실패해도 P8/WAL 계속 진행 확인** — 다음 EOD에서 (정상이든 또 실패하든) `[P8] EOD 스케일러 재적합 완료`·`[WAL] 체크포인트 완료` 로그가 항상 출력되는지 확인

---

## 2026-06-17 (181차 — time_zone 크래시 수정 + 진입단계 추적 카드 전면 개선)

### 다음 장 즉시 확인 [P0]

- [ ] **time_zone 크래시 미재발** — `[ERR-FATAL] minute_pipeline: local variable 'time_zone' referenced before assignment` 재발 없음 확인 (WARN.log)
- [ ] **진입단계 추적 카드 신규 컬럼 표시** — "차단사유" 컬럼, "8.STEP7 차단/9.진입후보(최종)/10.진입완료" 단계, 게이트 상세 툴팁이 신뢰도게이트 탭에서 정상 렌더링되는지 확인
- [ ] **Hurst 차단 표시 확인** — Hurst<0.45로 막힌 분봉이 "8. STEP7 차단" + "Hurst X.XXX < 0.45" 텍스트로 정확히 표시되는지 확인
- [ ] **차단사유 파일 로깅 확인** — `SIGNAL.log`/`SYSTEM.log` 등에서 `[차단] ...` 메시지가 grep으로 확인되는지 점검 (기존엔 대시보드 버퍼 전용)
- [ ] **`ensemble_decisions` 마이그레이션 확인** — 재시작 후 `entry_gate_json` 등 6컬럼이 `ALTER TABLE`로 정상 추가됐는지 (`PRAGMA table_info`) 확인

---

## 2026-06-17 (180차 — CB 파이프라인 정체 진단 + 워치독 무한루프 수정)

### 다음 장 즉시 확인 [P0]

- [ ] **PipePerf 라벨 정상화** — `S1=Xms`가 STEP1(검증) 본문을 가리키는지 확인 (종전 S2로 오표기되던 것)
- [ ] **`[Buffer-Timing]` 로그 확인** — 정체 재발 시 raw_fetch/pred_select/pred_update/pred_insert 중 실제 병목 구간 확정 (179차 "S2 지연 원인" TODO를 이 계측으로 대체)
- [ ] **15:10 이후 워치독 경보 미반복** — "파이프라인 N분 미실행" 90초 간격 반복 없음 확인
- [ ] **15:10 이후 강제 파이프라인 재실행 부작용 소멸** — `_try_pipeline_recovery`가 `run_minute_pipeline`을 추가 호출하는 로그 없음 확인
- [ ] **`verify_and_update` timeout 부작용 점검** — `[Buffer] verify_and_update 배치 오류` (3s timeout 실패) 빈도, 너무 잦으면 timeout 상향 검토

---

## 2026-06-17 (179차 — Phase C 슬라이싱 + SGD 최적화 + CORE 그룹 분리)

### 다음 장 즉시 확인 [P0]

- [ ] **ScalerRefresh B_INTRADAY** `horizons=['1m','3m','5m','10m','15m','30m']` — `_is_fitted` 제거 효과 유지 확인
- [ ] **SGD 가중치 로그 형식** — `[OnlineLearner] 1m 가중치 조정 SGD=XX% GBM=XX%` (버킷→호라이즌별 변경 확인)
- [ ] **ERR-FATAL 없음** — `X has N features` 에러 재발 없음
- [ ] **STABLE_TREND 진입 개선** — 12시대 conf=48~52% 신호 발생 시 `[P1] Checklist min_conf 분리: 0.XX→0.48` 로그 확인
- [ ] **편향패널티 비활성화** — TrendGate ON 구간에서 `[MetaGate] 편향패널티` 로그 없음 확인

### 이월 미해결 이슈

- [DONE 2026-06-16] **S2 지연 원인** — 180차에서 라벨 오프셋 버그 확인(실제로는 STEP1 `verify_and_update`) + sub-timing 계측·`_lock`+timeout 3s 적용 완료. 위 180차 [P0] 항목으로 후속 확인 진행 중
- [TODO P1] **feat=121 vs managed=97 불일치** — ScalerWarmup 로드 feat=121, 재학습 97개. registry 재정합 필요
- [TODO P2] **quality_investor_fetch_count D_FORCE 반복** — 매 5분마다 consec=5 발동. 이진 피처 D_FORCE 차단 검토
- [TODO P2] **ConstOut 해소 속도** — 재시작 후 1m~30m 순환 ConstOut 14분 지속. CONST_OUTPUT_MIN_BARS 5→3 검토

### 예정 작업

- [ ] **opt 4주 수집 후 Phase D 재검증**: opt_chain_pcr/gex_bn/atm_* 누적 확인
  - 조건: `SELECT COUNT(*) FROM raw_features WHERE features LIKE '%opt_chain_pcr%' AND CAST(json_extract(features,'$.opt_chain_pcr') AS REAL) != 0` > 3000행
- [ ] **feat=118 vs managed=97 불일치** 해소: shap_feature_registry.json active_features 갱신 (opt_chain 포함)
- [ ] **SHAP 탭 호라이즌별 확장** — Phase C 호라이즌별 SHAP 계산 (현재 1m 기준만)

---

## 2026-06-15 (178차 — 호라이즌별 피처셋 인프라 + opt_chain 버그 수정)

### 다음 장 즉시 확인 [P0]

- [DONE 2026-06-16] `[OptionChain] 갱신` 로그 확인 — PCR/GEX 비영, avail=True ✅
- [ ] `raw_features` DB 조회: `opt_chain_pcr`, `opt_gex_bn` 키 존재 여부 (미확인)
- [DONE 2026-06-16] `[Macro] 갱신 | VIX=17.7` ✅
- [DONE 2026-06-16] `[InvestorData]` 60초마다 갱신 ✅

### 예정 작업 (opt 4주 수집 후)

- [ ] **Phase D 재검증**: opt_chain_pcr/gex_bn/atm_* 4주 축적 확인 후 Walk-Forward 재실행
  - 조건: `SELECT COUNT(*) FROM raw_features WHERE features LIKE '%opt_chain_pcr%' AND CAST(json_extract(features,'$.opt_chain_pcr') AS REAL) != 0` > 3000행
- [ ] **GBM retrain**: opt 피처 포함 첫 retrain → per-horizon pkl 생성 → 호라이즌별 모델 전환
- [ ] **Phase E**: SHAP Tracker 6개 호라이즌 확장 (shap_tracker.py horizon 컬럼 추가)
- [ ] **feat=118 vs managed=97 불일치** 해소: shap_feature_registry.json active_features 갱신 (opt_chain 포함)

### 미해결 이슈 (이월)

- [TODO P1] **S2 지연 원인 추적** — 장 시작 직후 S2=56s 지연. `[S2] gil_wait` DEBUG 로그 임계 50ms로 낮춰 세분화 필요
- [TODO P1] **TimeRouter 스팸** — 30초 간격 동일 메시지 반복 (state-change 방식 수정 필요)

---

## 2026-06-15 (177차 — C_PERIODIC 독립 타이머 + P1-A 강화 + EKS z조건 완화)

### 다음 장 확인 사항

#### [P0] C_PERIODIC 독립 타이머 발동
- `[ScalerRefresh] trigger=C_PERIODIC elapsed=60min` 로그 확인 — D_FORCE 발동 없는 구간에서 60분마다 발동
- D_FORCE 연속 발동 중에도 `_last_periodic_refit_at` 기준으로 독립 카운트 → 60분 후 C_PERIODIC 발동 확인
- D_FORCE와 C_PERIODIC 동시 조건이면 D_FORCE 우선 반환 (C_PERIODIC 타이머만 리셋)

#### [P0] _gbm_retrain_running 30분 타임아웃 경고 소멸
- `[GBM] 재학습 플래그 30분 타임아웃 강제 해제` 로그 **없음** 확인 (오늘 10:25 발동 → 내일 없어야 함)
- `_gbm_retrain_done_event.set()`이 worker에서 즉시 실행되므로 daily_close 대기도 정상화 확인

#### [P0] EKS z조건 완화 효과
- EKS 회복 시도에서 `z_ok=True` 출현 확인 (기존 z=22 > 5 → 22 < 15로 통과)
- `[SHS-EKS] EKS 자동 해제 ... z_warn=22` 로그 — z=22여도 해제되는지 확인
- EKS 해제 후 정상 진입 재개 여부 (conf_hits 조건도 동시 충족 필요)

### 미해결 이슈 (이월)

- [TODO P1] **S2 지연 원인 추적** — 장 시작 직후 S2=56s 지연. `[S2] gil_wait` DEBUG 로그 임계 50ms로 낮춰 세분화 필요
- [TODO P1] **TimeRouter 스팸** — 30초 간격 동일 메시지 반복 (state-change 방식 수정 필요)
- [TODO P2] **feat=114 vs managed=97 불일치** — ScalerWarmup 114개 vs 재학습 97개. registry 재정합 필요

---

## 2026-06-11 (156차 — GBM 플래그 고착 + ScalerRefresh 3종 수정)

### 다음 장 검증 항목 (최우선)

#### [P0] GBM 재학습 성공 확인
- `[Retrain] 배치 재학습 시작 (weeks_back=26)` 로그 확인
- `[Retrain] DB 로드 완료: XXXXX행 × 97피처` — 미래가격 제거 후 15000+ 행 확인 (P2 효과)
- `[Retrain] 완료` 로그 + 하루 종일 재학습 없던 현상 해소 확인

#### [P0] ScalerRefresh 60분 이내 발동
- `[ScalerRefresh]` C_PERIODIC 트리거 로그 — 재학습 상태 무관 60분 내 발동 (P3 효과)
- 스케일러 노후화 경고 `[Model] 1m 스케일러 Xm 미갱신` — 60분 초과 없음

#### [P1] P1-A 플래그 즉시 리셋
- 재학습 실패(`ok=False`) 시 LEARNING.log 직후 Phase B ScalerRefresh 발동으로 간접 확인
- `[GBM] 재학습 플래그 30분 타임아웃 강제 해제` 로그 없음 (정상 흐름)

---

## 2026-06-11 (155차 — EKS·conf100%·SHAP 3종 수정)

### 다음 장 검증 항목

#### [P1] EKS 기준 통합 확인
- `[SHS-EKS] 기준=XX.X%` 로그에서 DynMC mc 값 표시 (45% 고정 아님)
- `[SHS-EKS] 회복 기준=XX.X%` — 0.42 floor 없이 mc 직접 사용 확인

#### [P1] conf=100% FLAT 재발 없음
- SIGNAL.log에서 `conf=100%` 패턴 전수 확인
- flat_score가 1.0으로 팽창하는 로그 없음 확인

#### [P2] SHAP weekly_review 개선 확인
- `방향별분석=ON` 로그 확인
- `direction_top` dict 키 포함 확인 (UP/DN/FL top-3)
- per-class Tier 2 발동 로그: `[SHAP] GBM 다중 클래스: ... per-class 트리 중요도로 폴백 (1회 알림)`

---

## 2026-06-10 (142~147차 — 금일 장중 이상점 6세션 수정)

### 금일 수정 완료 요약

| 차수 | 핵심 수정 |
|---|---|
| 142 | EOD 자동종료 ShutdownSignal + WAL 6개 + DBWriter 플러시 |
| 143 | conf=100% 근본 수정 4종 + EKS·DailyClose 관측성 7종 |
| 144 | scaler↔GBM 상호 잠금 + ConstOut→GBM 자동 연계 + CB③/PipePerf 개선 |
| 145 | horizon_proba={} 봉쇄 + SHAP 수정 2종 + Armistice 버그 |
| 146 | MetaConf class_weight 버그 + RF OOB 추론 불일치 2종 |
| 147 | Retrain force=True 하향 래칫 제거 + FLAT 레이블 오염 제거 |

- [DONE 2026-06-10] **conf=100% 경로 원천 봉쇄** — horizon_proba={} → grade=X/conf=0 + score 재정규화 + CONF_CLIP 0.80 + T=1.2 (`model/ensemble_decision.py`, `model/multi_horizon_model.py`)
- [DONE 2026-06-10] **SGD 붕괴 근본 수정** — MetaConf `class_weight='balanced'` + `partial_fit` 비호환 → `compute_class_weight` + `sample_weight` 배열 교체 (`learning/meta_confidence.py`)
- [DONE 2026-06-10] **scaler↔GBM 상호 잠금** — raw_data.db 동시 접근 경합 방지 + ConstOut 재적합 후 GBM 자동 연계 (`main.py` 3곳)
- [DONE 2026-06-10] **Retrain force=True 하향 래칫 제거** — 장중 acc 하락 모델 강제 저장 방지. 08:55 pre-market만 force=True 유지 (`main.py:2156`, `3075`)
- [DONE 2026-06-10] **미래 가격 없는 행 FLAT 오염 제거** — close_map 기반 필터로 T+30m 종가 없는 행 학습 제외 (`batch_retrainer.py:_load_from_db`)
- [DONE 2026-06-10] **RF OOB 추론 스케일 불일치 수정** — `apply_robust_preprocess` 추론 경로 추가 + OOB<0.45 앙상블 블렌딩 비활성화 (`model/rf_horizon_model.py`, `main.py`)
- [DONE 2026-06-10] **SHAP 수정 2종** — TreeExplainer WARNING 반복→1회 + 주간 심사 중복 2회→1회 (`shap_tracker.py`, `main.py`)
- [DONE 2026-06-10] **FLAT 재시작 Armistice 영구 미해제 버그** — sync_count=2 직접 설정으로 즉시 해제 (`main.py`)
- [DONE 2026-06-10] **EOD 자동종료 안전화** — ShutdownSignal QueuedConnection + WAL 6개 DB + DBWriter 플러시 (`main.py`, `config/settings.py`)

### 다음 장 검증 항목

#### [P0] 147차 — Retrain 안정화 (최우선)
- `[Retrain] {hz} 유지 (cv_acc=0.XXXX < old_acc-0.01)` 로그 확인 — 장중 acc 하락 시 이전 모델 보존
- `[Retrain] 미래 가격 불완전 행 X개 제거 (max_horizon=30m)` 로그 확인
- EOD Retrain acc ≤ 0.70 수준 안정화 (기존 0.80~0.90 폭등 억제 목표)
- DriftAdjuster 실측 acc와 CV acc 간격 축소 모니터링

#### [P0] 146차 — MetaConf·RF 복구
- `[MetaConf] 학습 오류` 로그 완전 소멸 (기존 09:24~세션끝 매분 반복 → 0건)
- `[MetaGate] SGD 붕괴 보완` 로그 없음 + meta_raw 0.30+ 정상화 확인
- RF OOB 재학습 후 >50% 확인 (재학습 전까지 ~37% 유지)

#### [P1] 145차 — 앙상블 안전망
- conf=100% 재발 없음 (SIGNAL.log 전수)
- FLAT 재시작 후 Armistice 즉시 해제 확인

#### [P1] 144차 — ConstOut 재발 방지
- ConstOut 발동 후 GBM 재학습 자동 연계 로그 + 30분 후 재발 없음

#### [P2] 143·142차 — EOD·관측성 (이월)
- Canary z경고 폭증 시 08:58 전 재적합 발동 확인
- `[System] 자동 종료 실행` 15:40 이후 + WAL 체크포인트 6개 DB 전체

### 미해결 이상점 — 로그 관찰, 수정 미완료

- [TODO P1] **TimeRouter "월물 만기 전날" 30초 간격 스팸** — 7,624줄 중 ~3,000줄 동일 메시지 반복. state-change 방식으로 수정 필요 (`time_strategy_router.py`)
- [TODO P1] **GapOffset today_open 재시작마다 다른 값** — 09:00: 1251.10 → 12:45 재시작: 1233.14 (-17.96p). 09:00 최초 확정 후 당일 고정 필요
- [TODO P2] **macro_quality_available z=-11.14 장 개시 직후 5분 반복** — 09:04~09:08 30회 동일 경고. 장 개시 전 매크로 유효성 검증 또는 Canary refit 포함 검토
- [TODO P2] **스케일러 90~130분 노후화** — 12:45: 95분, 15:01: 123분 미갱신. 144차 효과 확인 후 재시작 A_WARMUP 강제 실행 여부 판단
- [TODO P2] **registry=97 vs scaler=101 차원 불일치** — 시작 시 WARNING, 11:04에 ERROR 전환. 재학습 후 97→101 복구 확인. 미복구 시 원인 조사

### 재학습 필요

- **내일 장 전 GBM 재학습** — 147차(force=True 제거 + FLAT 오염 제거) + 146차(RF preprocess) 반영
  - 앱 재시작 → SHAP 탭 "현재 세트 재학습" 클릭
  - 재학습 후 feature_names 피처 수 97→101 복구 확인
  - `[Retrain] 미래 가격 불완전 행 X개 제거` 로그 확인

---

## 2026-06-10 (142차 — EOD 자동종료 흐름 6종 안전화)

### 한일 요약

- [DONE 2026-06-10] **_ShutdownSignal(QObject) 추가** — DailyClose 스레드의 `QTimer.singleShot` 비-Qt 호출 → `_shutdown_sig.request.emit()` + `QueuedConnection`으로 교체 (`main.py`)
- [DONE 2026-06-10] **_schedule_shutdown() 신규** — append_sys_log·QTimer 메인 스레드에서 실행 보장 (`main.py`)
- [DONE 2026-06-10] **_run_daily_close 예외 처리 강화** — try/except + `_emit_done` 플래그로 예외 시에도 종료 보장 (`main.py`)
- [DONE 2026-06-10] **DBWriter 큐 플러시** — WAL 체크포인트 전 `put(None)` + `join()` 추가 (`main.py`)
- [DONE 2026-06-10] **WAL 체크포인트 6개 DB 전체 확장** — `EOD_WAL_CHECKPOINT_DBS` 상수화 (`config/settings.py`, `main.py`)
- [DONE 2026-06-10] **EOD retrain force=False 명시** — standalone vs in-process 의도 차이 주석 기록 (`main.py`)

### 다음 할 일

- *(142~147차 통합 섹션으로 이동)*

---

## 2026-06-09 (135차 — Meta skip·conf=100% 4종 근본 원인 수정)

### 한일 요약

- [DONE 2026-06-09] **MetaGate reduce_thr 공식 수정** — `max(0.43, min_conf+0.04)` → `max(0.38, min_conf)`. 오프셋 제거로 actual_min_conf가 실질 하한이 됨 (`strategy/entry/meta_gate.py`)
- [DONE 2026-06-09] **actual_min_conf MetaGate 전달** — STEP 6에서 `max(decision["min_conf"], zone_mc)` 계산값을 MetaGate.evaluate()에 직접 전달. UI 표시 mc 불일치 해소 (`main.py`)
- [DONE 2026-06-09] **SGD 붕괴 보완 (rule-based floor)** — meta_conf<0.15이면 `_rule_based_confidence()` 값으로 하한 보정 (`strategy/entry/meta_gate.py`)
- [DONE 2026-06-09] **MetaConfidenceLearner 붕괴 자동 복구** — `_is_collapsed()` (최근 30회 max<0.05) + `_reset_model()` 구현 (`learning/meta_confidence.py`)
- [DONE 2026-06-09] **AutoMask CORE 피처 면제** — `_CORE_MASK_EXEMPT` frozenset(cvd/vwap/ofi 계열) 추가. 극단 z-score를 "신호"로 인식, xs=0.0 대체 차단 (`model/multi_horizon_model.py`)
- [DONE 2026-06-09] **cvd_direction·cvd DFORCE_EXCLUDE 추가** — 이산(-1/0/+1) 피처는 D_FORCE로 z-score 해소 불가. 일방향 장에서 std→0 → transform(-1)=0 → FLAT 100% 고착 방지 (`config/settings.py`)
- [DONE 2026-06-09] **refit_scalers_only() CORE scale 보호** — 새 스케일러 CORE 피처 `scale_<0.05`이면 이전 mean/scale 복원 (`model/multi_horizon_model.py`)

### 다음 할 일

- [NEXT 내일 장] **135차 패치 효과 확인** (최우선)
  - D_FORCE: `feat=cvd_direction` 발동 없음 확인 (`DFORCE_EXCLUDE` 적용)
  - AutoMask: `cvd_direction` 격리 목록에서 빠짐 확인 (`_CORE_MASK_EXEMPT` 적용)
  - conf=100% FLAT 고착 재발 없음 (SIGNAL.log)
  - MetaGate: reduce_thr ≈ actual_min_conf (오프셋 없음), skip 비율 정상화
  - C_PERIODIC/A_WARMUP 후 `[ScalerRefresh] CORE 'cvd_direction' std≈0 → 이전 scale 복원` 로그 (scale 보호)

- [NEXT 즉시] **GBM 재학습** — 131차+133차+135차 패치 반영 (계속 이월)
  - 앱 재시작 → SHAP 탭 "현재 세트 재학습" 클릭

---

## 2026-06-09 (134차 — 파이프라인 지연 CB⑤ 2종 제거)

### 한일 요약

- [DONE 2026-06-09] **Fix 3: STEP 4 DB 비동기화** — candle_features·horizon_features `save_*()` 동기 호출 → `_db_write_queue.put_nowait()` 교체. 큐 포화 시 동기 fallback 포함 (`main.py`)
- [DONE 2026-06-09] **Fix 4: WAL 체크포인트** — `daily_close()` 마감 시 PREDICTIONS_DB·RAW_DATA_DB WAL TRUNCATE (`main.py`)
- [DONE 2026-06-09] **Fix 6: PipePerf 스텝별 breakdown** — CB임박(≥5s) 시 전체 스텝, 경고(>1s) 시 100ms 초과 스텝만 출력 (`main.py`)
- [DONE 2026-06-09] **Fix 7: scaler_monitor 비동기화** — `predict_proba()` 내 동기 `insert_events_batch()` 제거 → `last_monitor_rows` 속성으로 caller에 전달 → `_db_write_worker` 큐 처리 (`main.py`, `model/multi_horizon_model.py`)
- [DONE 2026-06-09] **Fix 8: scaler_monitor.db WAL 모드** — `insert_events_batch()`, `update_event_refresh()` 모두 `PRAGMA journal_mode=WAL` 적용 → 배경 스레드 write와 EXCLUSIVE lock 경합 해소 (`model/scaler_monitor_db.py`)
- [DONE 2026-06-09] **Fix 9: monitor rows 조건부 수집** — extreme_count>0 또는 age>90m일 때만 row 추가 → 정상 분봉 노이즈 제거 (`model/multi_horizon_model.py`)

### 다음 할 일

- [NEXT 내일 장] **134차 패치 효과 확인** (최우선)
  - `[PipePerf][CB임박]` 로그에서 스텝별 지연 분포 확인
  - CB⑤ 5000ms 미발동 확인 (10:23 유형 재발 없음)
  - `[DBQueue] 큐 포화` fallback 로그 없음 확인
  - Degraded Mode 진입 없음 확인

- [NEXT 즉시] **GBM 재학습** — 131차 패치(CORE 완화·MC_FLOOR 0.25) + 133차 피처 제외 반영 (이월)
  - 앱 재시작 → SHAP 탭 "현재 세트 재학습" 클릭

- [NEXT 중기] **133차 패치 효과 확인** (이월)
  - `is_open_volatile`, `opt_pcr_bullish` D_FORCE 발동 없음 확인
  - CoherenceGate 차단 횟수 감소 확인
  - `[SHS-EKS] 재시작 후 GAP_OPEN 봉 없음 (09:15 이후) — EKS 미발동 확정` 로그 확인

---

## 2026-06-09 (133차 — 이진 피처 D_FORCE 차단 + EKS 재시작 안정화)

### 한일 요약

- [DONE 2026-06-09] **DFORCE_EXCLUDE_FEATURES 추가** — `is_open_volatile`, `opt_pcr_bullish/bearish` D_FORCE 트리거 제외. 이진(0/1) 피처는 스케일러 재적합으로 z폭발 해소 불가 (`config/settings.py`, `model/multi_horizon_model.py`)
- [DONE 2026-06-09] **opt_pcr_bullish/bearish CLIP 추가** — z=+22.34 실측. 원시값 (0.0, 1.0) cap (`config/settings.py`)
- [DONE 2026-06-09] **EKS 재시작 안정화** — 09:15 이후 재시작 시 GAP_OPEN 봉 없으면 EKS 미발동 확정 (판단 근거 없음). 유예 메시지 반복 방지 (`safety/system_health.py`)

### 다음 할 일

- [NEXT 내일 장] **133차 패치 효과 확인** (최우선)
  - `is_open_volatile`, `opt_pcr_bullish` D_FORCE 발동 없음 확인
  - CoherenceGate 차단 횟수 감소 (132차까지 09:08, 09:27 × 2회 → 0회 목표)
  - `[SHS-EKS] 재시작 후 GAP_OPEN 봉 없음 (09:15 이후) — EKS 미발동 확정` 확인

- [NEXT 즉시] **GBM 재학습** — 131차 패치(CORE 완화·MC_FLOOR 0.25) + 133차 피처 제외 반영 (이월)
  - 앱 재시작 → SHAP 탭 "현재 세트 재학습" 클릭

- [NEXT 중기] **CB S2 지연 원인 분석** — 오늘 S2=5~9초 (정상 <1초)
  - OnlineLearner가 verified 예측 × MetaGate × DB 조회 중 어느 단계가 느린지 프로파일링 필요

- [NEXT 중기] **110차 Platt/ShortHorizonOverride 동작 확인**
  - `[Calibration] 앙상블 보정기 복원/저장` 로그 확인 (ScalerWarmup 스레드에서 실행)
  - `[ShortHorizonOverride]` 발동 조건 재점검 (FLAT streak ≥ 5봉 조건 도달 여부)

---

## 2026-06-09 (132차 — 장전/장시작 연쇄 오류 7종 패치)

### 한일 요약

- [DONE 2026-06-09] **`'min_conf'` KeyError 수정** — `ensemble_decision.compute()` 조기 반환 dict에 `min_conf` 등 누락 키 추가 (`model/ensemble_decision.py:290`)
- [DONE 2026-06-09] **decision.get() 안전 접근** — `decision["min_conf"]` → `decision.get("min_conf", _zone_mc)` (`main.py:3606`)
- [DONE 2026-06-09] **Canary z경고 임계 완화** — EarlyWarmup 후 5→12개. 허위 알림 억제 (`main.py:2325`)
- [DONE 2026-06-09] **CB⑤ 완화 구간 확장** — 09:00~09:10, 5000→9000ms (`safety/circuit_breaker.py:408`)
- [DONE 2026-06-09] **EKS 최솟 bars=3 조건** — bars<3 시 당일 관망 선언 유예 (`safety/system_health.py:84`)
- [DONE 2026-06-09] **Degraded Mode 09:10 이전 진입 유예** — 장 시작 초기 파이프라인 버스트 대응 (`main.py:1231`)

### 다음 할 일

- [NEXT 내일 장] **132차 패치 효과 확인** (최우선)
  - `[Canary]` z경고 12개 미만 → `⚠ z경고 폭증` 알림 미발생
  - `[CB⑤]` 09:00~09:10 `[장시작 버스트]` 경고만, PAUSE 미발동
  - `[SHS-EKS] EKS 판정 유예 — GAP_OPEN 봉 부족` 로그 (bars<3 시)
  - `[HealthPolicy] Degraded Mode 진입 유예 — 장 시작 초기` 로그 (09:10 전)
  - ERR-FATAL `'min_conf'` 재발 없음

- [NEXT 즉시] **GBM 재학습** — 131차 패치(CORE 완화·MC_FLOOR 0.25) 반영 (이월)
  - 앱 재시작 → SHAP 탭 "현재 세트 재학습" 클릭
  - `[DynMC] step clamp 적용: p65=0.279 → base=0.390` 로그 확인

---

## 2026-06-08 (131차 — 진입0 탈출 5종 패치)

### 한일 요약

- [DONE 2026-06-08] **CascadeCoherence FL 제외 패치** — FL 호라이즌 제외 후 방향성 있는 것만 집계. 오늘 케이스(30m/15m/10m=DN, 5m/3m=FL, 1m=DN) 0.17→1.00 (`model/ensemble_decision.py`)
- [DONE 2026-06-08] **CascadeCoherence 임계값 0.34→0.25** — 혼합 방향 케이스 허용 확대 (`model/ensemble_decision.py`)
- [DONE 2026-06-08] **MC_ABS_FLOOR 0.42→0.25** — 실 conf(27.9%) 분포에 수렴 허용. REGIME_MIN_CONF RISK_ON/NEUTRAL 0.42→0.25 동기화 (`config/settings.py`)
- [DONE 2026-06-08] **BiasReset coldstart FL 기준 완화** — startup_warmup 구간에서 10분→5분 (`main.py`)
- [DONE 2026-06-08] **CORE CVD/OFI 강제X → pass_count-1** — VWAP만 강제X 유지, CVD/OFI 불일치는 등급 하락으로 처리 (`strategy/entry/checklist.py`)
- [DONE 2026-06-08] **_restore_mc_from_history SELECT 버그 수정** — `SELECT zone, new_mc` → `zone, new_mc, base_mc`. KeyError로 REGIME_MIN_CONF 동기화 항상 실패하던 문제 (`strategy/entry/time_strategy_router.py`)

### 다음 할 일

- [NEXT 즉시] **앱 재시작 후 GBM 재학습** (최우선, 132차로 이월)
  - 앱 재시작 → SHAP 탭 "현재 세트 재학습" 클릭
  - 재학습 완료 후 `[DynMC] step clamp 적용: p65=0.279 → base=0.390` 로그 확인 (MC_FLOOR 하강 첫 단계)
  - cvd_divergence SHAP rank 상승 확인

- [NEXT 내일 장] **131차 패치 효과 확인**
  - `[CascadeCoherence]` 차단 비율 대폭 감소 확인 (오늘 96% → 개선 기대)
  - `[BiasReset]` coldstart 5분 기준 발동 확인 (재기동 직후 FL 고착 시)
  - `[Checklist] CORE CVD/OFI ✗` INFO 로그 확인 (강제X → 등급하락 처리 확인)
  - DynMC step clamp 로그로 mc 하강 추이 모니터링
  - ⚠ 오늘 132차 패치도 함께 확인 (위 132차 NEXT 항목 참조)

- [NEXT 중기] **MC 하강 후 진입 재개 확인**
  - 재학습 5~6회 후 mc ≈ 0.28~0.30 수렴 시 conf 33%대 신호 통과 가능
  - 과진입(과도한 완화) 여부 모니터링 — 필요 시 MC_ABS_FLOOR 상향 조정

---

## 2026-06-08 (130차 — CVD SHAP 복구 + SHAP 추천 3단 개선 + 코드 정리)

### 한일 요약

- [DONE 2026-06-08] **CVD signal_strength 단위 불일치 버그 수정** — cvd_slope/price_slope(계약수÷포인트) → cvd_slope_norm(일중 max 대비) 사용. cvd_divergence 이진값({0,-1}) → 연속값(-1~+1). (`features/technical/cvd.py`)
- [DONE 2026-06-08] **buy_vol fallback 가격기반으로 교체** — vol/2(delta=0→CVD고착) → `vol×(close-low)/range`. (`features/feature_builder.py`)
- [DONE 2026-06-08] **cvd_divergence 부호 수정** — 다이버전스=음수, 동방향=양수. (`features/feature_builder.py`)
- [DONE 2026-06-08] **raw_data.db 72,591봉 소급 재계산** — 백업 후 날짜별 reset_daily() 적용. 이진 2종→연속 1,789 unique값. (`data/db/raw_data.db`)
- [DONE 2026-06-08] **"현재 세트 재학습" 버튼 영구 비활성화 버그 수정** — `_on_gbm_retrain_done` 완료 후 `_update_shap_dashboard()` 추가. (`main.py`)
- [DONE 2026-06-08] **SHAP 추천 3단 개선** — ①주별 dedup ②3/4 완화 ③절대값 기준(mean×0.3) 즉시 후보. (`learning/shap/shap_tracker.py`)
- [DONE 2026-06-08] **update_shap 3중 정의 → 1개 통합** — 죽은코드(NameError 위험)·중간버전(action_state 누락) 제거. (`dashboard/main_dashboard.py`)

### 다음 할 일

- [NEXT 즉시] **앱 재시작 후 GBM 재학습** (최우선)
  - 앱 재시작 → SHAP 탭 "현재 세트 재학습" 버튼 클릭
  - 재학습 완료 후 버튼 enabled 복원 확인 (`_update_shap_dashboard` 호출 효과)
  - cvd_divergence SHAP rank 상승 확인 (기존 rank 63/101 0.0% → 개선 예상)

- [DONE 2026-06-08] **`_up_r` UnboundLocalError 조사** — 129차에서 이미 수정 확인. 원인: 미커밋 편집 중 `_dir_bias_r = max(_up_r, _dn_r, _fl_r)` 추가 후 초기화 누락(당시 `_fl_r = 0.0`만 있었음). 수정: `_up_r = _dn_r = _fl_r = 0.0` (main.py:2777)

---

## 2026-06-08 (129차 — 3m/5m FL 편향 버그 수정)

### 한일 요약

- [DONE 2026-06-08] **F1AdaptiveWeight FL 스킵 버그 수정** — `update(predicted==0)` 스킵 제거. FL 예측도 obs 누적 → min_obs 도달 후 동적 억제 활성. (`model/ensemble_decision.py:139`)
- [DONE 2026-06-08] **_fl_streak 임계값 70%→50%** — 3m conf 50~55% FL 편향이 70% 임계 미달로 감쇠 불발 → 50%로 낮춰 10분 연속 시 weight×0.2 발동. (`model/ensemble_decision.py:322`)
- [DONE 2026-06-08] **BiasReset 발동 조건 완화** — FL 20→10분, UP/DN 10→5분, tot≥20→15, 80% 임계. 오늘 18분 FL 100% 미발동 재발 방지. (`main.py:2797-2799`)

### 다음 할 일

- [NEXT 다음 장] **129차 발동 확인**
  - `[EarlyDirDamp] 3m FL=XX% 10min → weight×0.2` 로그 확인
  - `[BiasReset] 3m FL편향 XX% 10분 지속 → uniform fallback 적용` 로그 확인
  - Bias⚠ 소멸 후 15m/30m 앙상블 점유율 증가 확인 (flat_score 감소)

- [NEXT 다음 장] **1m UP편향 모니터링**
  - 오늘 1m UP=65%, 적중=23% — BiasReset 발동 조건 충족 시 uniform fallback 적용 여부 확인
  - 오발동(정상 UP 추세에서 BiasReset 발동) 여부 점검

- [NEXT 중기] **3m/5m GBM class_weight 검토**
  - FL 편향이 구조적으로 반복되면 class_weight {FL:0.70} 등 재학습 검토

---

## 2026-06-08 (128차 — 30m DN 편향 고착 대응)

### 한일 요약

- [DONE 2026-06-08] **EarlyDirDamp 일반화** — FL 전용(`_fl_streak`) → UP/DN/FL 공통. 단일 방향 70%+ 10분 지속 → weight×0.2 + 재정규화. 로그: `[EarlyDirDamp] 30m DN=XX% 10min → weight×0.2` (`model/ensemble_decision.py`)
- [DONE 2026-06-08] **BiasReset 일반화** — FL 전용 → UP/DN/FL 공통. FL=20분, UP/DN=10분 임계. 30m DN 100% 고착 시 즉시 uniform fallback 적용. 로그: `[BiasReset] 30m DN편향 100% N분 지속 → uniform fallback 적용` (`main.py`)
- [DONE 2026-06-08] **30m class_weight DN 균형** — UP=1.15→1.40, DN=1.15→0.90, FL=0.70 유지. DN 과잉 학습 억제, UP 강화로 DN 100% 편향 구조적 해소 (다음 재학습 적용) (`learning/batch_retrainer.py`)

### 다음 할 일

- [NEXT 다음 장] **128차 발동 확인**
  - `[EarlyDirDamp] 30m DN=XX% 10min → weight×0.2` 로그 확인
  - `[BiasReset] 30m DN편향 100% 10분 지속 → uniform fallback 적용` 로그 확인
  - uniform fallback 적용 후 30m 예측이 UP=1/3, DN=1/3, FL=1/3으로 전환 확인
  - 과도한 오발동 모니터링: UP/DN 방향 예측이 잠깐 70% 넘는 정상 추세 구간에서도 발동되는지

- [NEXT 다음 재학습 후] **30m class_weight 효과 확인**
  - `[Bias] 30m DN%` 로그에서 DN 비율 감소 여부 (기존 100% → 40~50% 목표)
  - UP 예측 출현 여부 (현재 UP=0 → 재학습 후 UP 예측 발생해야 함)

- [NEXT 1주 모니터링] **EarlyDirDamp 오발동 점검**
  - TrendGate DN 구간에서 30m DN 70%+ 정상 추세 → EarlyDirDamp 발동 여부
  - 오발동 빈번 시: DN 임계 70%→80% 상향 또는 TrendGate active 중 EarlyDirDamp 스킵 검토

---

## 2026-06-08 (127차 — 완성봉 입력 개선안 구현)

### 한일 요약

- [DONE 2026-06-08] **`build_for_horizon` cvd_direction 재계산** — N분봉 buy_vol/sell_vol 합계로 `cvd_direction` override. 125차 scaling 동일 (`(buy-sell)/(buy+sell) × 0.5`, clip ±0.45). buy/sell=0이면 1m 값 그대로 사용 (`features/feature_builder.py`)
- [DONE 2026-06-08] **`generate_calibration_report.py` Platt 도입일 필터** — Platt 보정기 도입일(2026-06-04) 이후 데이터만 현재 성능으로 보고. ECE 0.2477(전체 누적 raw) → **0.1526(최근 5050건 calibrated)** 로 실제 성능 확인. 기존 `overall`/`by_horizon` 키 유지(하위 호환) (`scripts/generate_calibration_report.py`)
- [DONE 2026-06-08] **`_retrain_phase2` cvd_direction 비제로 검증 로그** — 재학습 시 `[Retrain-P2] %s cvd_direction 비제로 N/M (XX%)` 로그 추가. build_for_horizon N분봉 재계산 반영률 확인용 (`learning/batch_retrainer.py`)

### 127차 calibration 스냅샷

| 구간 | ECE | 적중율 | 비고 |
|---|---|---|---|
| 전체 누적 | 0.2477 | 36.5% | Platt 이전 raw conf 오염 |
| 최근(since 2026-06-04) | **0.1526** | 30.3% | Platt 보정 후 실제 성능 |
| 1m (최근) | **0.0532** | 38.4% | 목표 0.05에 근접 |
| 3m (최근) | 0.1236 | 30.5% | |
| 30m (최근) | 0.2165 | 25.0% | 개선 여지 가장 큼 |

### 다음 할 일

- [NEXT 다음 재학습 후] **cvd_direction 재계산 효과 확인**
  - `[Retrain-P2] 3m cvd_direction 비제로 N/M (XX%)` — 50% 이상이면 재계산 데이터 충분
  - 비제로율이 낮으면 → buy_vol/sell_vol이 기존 DB에 미저장 (Phase 1 백필 데이터)
  - 신규 세션 데이터 누적 후 재학습 시 비율 증가 예상

- [NEXT 다음 장] **127차 수정 발동 확인**
  - 완성봉 발생 시 `cvd_direction` 값이 1m 기준과 달라지는지 SIGNAL.log 확인
  - N분봉 buy_vol=sell_vol=0인 봉은 1m 값 그대로 유지됨 (정상)

- [NEXT 중기] **30m ECE 0.2165 개선**
  - 최근 25.0% accuracy, gap 0.43 (0.6~0.7 bin) → 30m 과신뢰 구간 집중
  - class_weight {FL:0.70} 재조정 또는 min_conf 0.6 이상 30m 신호 차단 강화 검토

- [NEXT 중기] **calibration_metrics.json 대시보드 파싱 업데이트**
  - 현재 대시보드에서 `calibration_metrics["overall"]["ece"]`로 접근 중
  - 이제 `"recent"` 섹션이 현재 성능. 대시보드 EfficacyPanel에서 `"recent"` 우선 읽도록 수정 검토

---

## 2026-06-08 (126차 — 거래소 CB 대응 + Registry 정합성 + cvd_direction clip)

### 한일 요약

- [DONE 2026-06-08] **거래소 CB 상태머신** — 5분 미수신 → ExchangeCB 모드 진입, 분봉 재개 시 자동 복구 (`main.py`)
- [DONE 2026-06-08] **ShadowSession ExchangeCB 연동** — `mark_exchange_cb()` + `force_live()` 추가, BLOCKED 복구 시도 중단 (`safety/shadow_session.py`)
- [DONE 2026-06-08] **앙상블 CB 해제 초기화** — `reset_exchange_cb()` 추가 (hz_conf_hist/stuck/fl_streak 리셋) (`model/ensemble_decision.py`)
- [DONE 2026-06-08] **Registry 정합성 동기화** — 115차에서 삭제된 4개 피처(vwap/microprice/macro_vix_abs/feature_recoverable_errors) registry에서 제거 (105→101) (`data/db/shap_feature_registry.json`)
- [DONE 2026-06-08] **cvd_direction clip 추가** — `(-0.45, 0.45)` SCALER_CLIP_FEATURES 추가, z=-6.38 D_FORCE 반복 방지 (`config/settings.py`)

### 다음 할 일

- [NEXT 다음 장] **126차 수정 발동 확인**
  - `[ExchangeCB] 분봉 5분 미수신 — 거래소 CB/단일가 구간 추정` SYSTEM WARNING 로그
  - `[ExchangeCB] 거래소 CB 해제 — N분 공백 후 분봉 재개. 상태 초기화 시작` 복구 로그
  - `[ShadowSession] 거래소 CB 해제 → 강제 LIVE 복구` 로그
  - cvd_direction D_FORCE 재발 없음 확인 (SIGNAL.log)
  - `managed feature set 적용: 101개` 재학습 로그 (registry 101 일치 확인)

---

## 2026-06-08 (125차 — Extreme 피처 z-score 억제)

### 한일 요약

- [DONE 2026-06-08] **vwap_momentum clip** — `np.clip(..., -2.0, 2.0)` (max|z| 46→9)
- [DONE 2026-06-08] **opt_pcr_extreme × 0.5** — 스케일 반감 (max|z| 16→8), 완전 삭제는 재학습 후
- [DONE 2026-06-08] **ret_1m/5m/15m 클리핑** — ±1%/2%/5% 상한 (fat-tail 억제)
- [DONE 2026-06-08] **cvd_direction × 0.5** — {-1,0,1} → {-0.5,0,0.5} (max|z| 6.7→3.3)
- [DONE 2026-06-08] **수급 8개 피처 로그 압축** — `sign × log1p(|v|/1000)` (드리프트 근본 억제)

### 다음 할 일

- [NEXT 즉시] **실세션 extreme 패널 재확인** — 5종 수정 후 max|z| 변화 확인
- [NEXT 재학습 후] **opt_pcr_extreme 완전 삭제** — GBM 재학습 + 1주 안정 후 `option_features.py` 키 제거

---

## 2026-06-08 (124차 — v8.0 Phase 0)

### 한일 요약

- [DONE 2026-06-08] **TICK_SIZE 설정화** — `config/settings.py`에 `TICK_SIZE = 0.05`
- [DONE 2026-06-08] **HORIZON_TIME_POLICY + HORIZON_COLDSTART_MIN_PASS** — cold-start 2단계 + 마감 구간 정책
- [DONE 2026-06-08] **compute_cascade_coherence()** — 30m→1m 방향 정렬 점수 반환 (유틸 함수)
- [DONE 2026-06-08] **select_entry_horizon()** — ATR feasibility 기반 최적 호라이즌 선택 (유틸 함수)
- [DONE 2026-06-08] **FL 조기 감쇠 `_fl_streak`** — FL 70%+ 10분 → weight×0.2 앙상블 차단
- [DONE 2026-06-08] **`active_horizons` 앙상블 적용** — 시간대 정책 비활성 호라이즌 weight=0
- [DONE 2026-06-08] **CascadeCoherence gate** — score < 0.34 시 방향성 신호 차단 (CoherenceGate 보완)
- [DONE 2026-06-08] **`entry_ok` 파라미터** — checklist.check()에 추가, 0.0이면 즉시 X등급
- [DONE 2026-06-08] **만기일 마감 수정** — `is_market_open` / `minutes_to_close` 만기일 15:20, 일반 15:35
- [DONE 2026-06-08] **scaler_events DB 컬럼 확장** — raw_value/pre_value/scaler_mean/scaler_std + 자동 마이그레이션
- [DONE 2026-06-08] **ScalerMonitorPanel Top5 6컬럼 확장** — raw→pre, μ/σ, 최근 ts/horizon
- [DONE 2026-06-08] **CYBOS_PLUS.bat STEP 0** — 다른 창 최소화 + 마우스 (0,0) 리셋 (close_other_windows.ps1 신규)
- [DONE 2026-06-08] **docs 정리** — 구버전 3개 삭제, V8 통합 계획서 신규, SGD_FEATURE_VECTOR 갱신

### 다음 할 일

- [NEXT 즉시] **main.py 연결** (Phase 0 함수들을 실제 파이프라인에 연결)
  - `HORIZON_TIME_POLICY` → 매분 `active_horizons` 계산 → `EnsembleDecision.compute(active_horizons=...)` 전달
  - `select_entry_horizon(atr, threshold_1m)` → `active_entry_hz` → 로그 기록
  - `entry_ok` → `EntryChecklist.check(entry_ok=...)` 전달 (독성·품질·스프레드 미달 시 0.0)
  - `cascade_blocked` 반환값 → 대시보드 진입 단계 표시 연결

- [NEXT 즉시] **feature_builder.py Phase 0 버그 수정** (V8 S0/6번)
  - `prev_day_same_hour_ret`: `timedelta(minutes=0)` 잔존 코드 제거 (`prev_d.strftime` 직접 사용)
  - `ema_cross`: 이진값 → `(ema5 - ema20) / (ema20 + 1e-9)` 연속값
  - `avg_volume`: `bar_volume = vol` 분리 + `avg_volume = rolling_mean`
  - `atr_expansion_rate` 신규: `(atr[-1] - atr[-2]) / atr[-2]`
  - `investor_age_norm` 정규화: `min(age, 300.0) / 300.0`

- [NEXT 다음 장] **Phase 0 실세션 확인**
  - STEP 0 pre-launch: 다른 창 최소화 → Cybos 로그인 정상
  - `[EarlyFLDamp]` 로그: FL 70%+ 10분 연속 시 출력
  - `[Ensemble] CascadeCoherence 차단` 로그: 하위만 방향 시 차단
  - 만기일 `is_market_open` 15:20 마감 동작

## 2026-06-08 (121~123차)

### 한일 요약

- [DONE 2026-06-08] **백필 실행** — `aggregate_and_backfill.py --weeks 10` (raw_features JOIN 방식 v2로 수정 후 실행)
- [DONE 2026-06-08] **Phase 2 재학습** — 버그 3종 수정 후 `eod_retrain.py --phase2 --weeks 10` 완료 (전 호라이즌 105차원 일치)
- [DONE 2026-06-08] **Phase 2 백필 12피처 버그 수정** — raw_features JOIN으로 105+피처 저장 (`aggregate_and_backfill.py` v2 전면 재작성)
- [DONE 2026-06-08] **feature_names.pkl 오염 버그 수정** — `_load_feature_names()` 신규 + 105개 재학습 완료 후 복원 (`batch_retrainer.py`)
- [DONE 2026-06-08] **X 행렬 차원 불일치 버그 수정** — `use_feat_names = _existing_feat_names` 105개 고정 (`batch_retrainer.py`)
- [DONE 2026-06-08] **cp949 UnicodeEncodeError 수정** — ✓/−/— → OK/-- ASCII 대체 (`eod_retrain.py`)
- [DONE 2026-06-08] **UI v7.0→v8.0** + Phase 3 깜박임 배지 추가 (`dashboard/main_dashboard.py`)
- [DONE 2026-06-08] **PredictionPanel bar_age 시각화** — `{age}m전` 표시 + stale시 주황 dashed 테두리 (`dashboard/main_dashboard.py`, `main.py`)
- [DONE 2026-06-08] **lbl_futures_code 동적화** — "F202606" 하드코딩 → `_MARKET_SYMBOLS` 동적 계산

### 다음 할 일

- [NEXT 다음 장] **Phase 2 실세션 확인** (최우선)
  - `[Phase2-STEP4]` 오류 로그 없음 확인
  - 3m봉 완성 시 PredictionPanel `"58.3% 2m전"` 표시 확인
  - 30m봉 16분 경과 시 카드 테두리 주황 dashed 전환 확인
  - BAR_CACHE_DECAY: 30m봉 미완성 구간 confidence 점진 감소 확인
  - `validate_horizon_scaler_consistency()` 불일치 경보 없음

- [NEXT ~30일 후] **Stage 2: buy_vol/sell_vol 축적 후 1m/3m 재학습**
  - raw_candles.buy_vol/sell_vol 30일 축적
  - `eod_retrain.py --phase2` 재실행 → OFI/CVD 정상 학습

- [NEXT ~50일 후] **Stage 3: 전 호라이즌 go-forward 데이터 전면 재학습**
  - raw_features_horizon 50일+ 데이터 기준

## 2026-06-07 (120차 — Phase 2 호라이즌별 완성봉 입력 구조 구현)

### 한일 요약

- [DONE 2026-06-07] **`features/bar_aggregator.py` 신규** — 1m봉→3/5/10/15/30m 완성봉 집계. `push(bar_1m)` → `{h_min: agg_bar}`, `reset_daily()` 포함
- [DONE 2026-06-07] **`feats_to_vec` + `build_for_horizon` 추가** — `feature_builder.py`. N분봉 OHLCV에서 atr/bar_volume/ret_Nm 재산출 후 feature_decay 적용
- [DONE 2026-06-07] **DB 스키마 확장** — `raw_features_horizon`, `raw_candles_aggregated` 테이블 신규; `raw_candles`에 `buy_vol`/`sell_vol` 컬럼 추가 (마이그레이션 포함)
- [DONE 2026-06-07] **`validate_horizon_scaler_consistency` + `predict_proba_multi` 추가** — `model/multi_horizon_model.py`
- [DONE 2026-06-07] **`MIN_TRAIN_BARS_PER_HORIZON` + `_retrain_phase2` 추가** — `learning/batch_retrainer.py`; `--phase2` 플래그 추가 `scripts/eod_retrain.py`
- [DONE 2026-06-07] **`main.py` STEP 4/5 Phase 2 로직** — `bar_aggregator.push()` → `save_horizon_features()` → `_hz_feat_cache` 캐시 → `BAR_CACHE_DECAY` 신뢰도 감쇠
- [DONE 2026-06-07] **`scripts/aggregate_and_backfill.py` 신규** — 기존 72k봉 소급 백필 스크립트 (v1, v2로 교체됨)
- [DONE 2026-06-07] **6종 기능 테스트 통과**

---

## 2026-06-06 (119차 — FeatureBuilder 양방향성 버그 수정 4건)

### 한일 요약

- [DONE 2026-06-06] **vwap_momentum 항상 0 버그 수정** — features.get("vwap") 참조 잔존 → features.get("vwap_position") + 5분 변화량 방식으로 전환 (feature_builder.py)
- [DONE 2026-06-06] **ofi_imbalance 방향 복원** — abs(ofi_norm) → 부호 유지 np.clip(ofi_norm/3.0, -1.0, 1.0) (ofi.py)
- [DONE 2026-06-06] **volume_acceleration 클리핑 추가** — np.clip(..., -3.0, 3.0) (feature_builder.py)
- [DONE 2026-06-06] **queue_directional_depletion 신규 피처** — 매도/매수호가 고갈 방향 강도 [-1, 1] (queue_dynamics.py, feature_builder.py)

### 다음 할 일

- [NEXT 다음 재학습 전] **shap_feature_registry에 queue_directional_depletion 수동 추가**
  - shap_feature_registry.json active_features 배열에 "queue_directional_depletion" 추가
  - GBM 재학습 후 피처 수 카운트 +1 확인

- [NEXT 다음 재학습 후] **119차 수정 효과 확인**
  - SHAP 리포트: vwap_momentum 비제로값 출현 (기존 0 → 의미있는 값)
  - ofi_imbalance DB 분포가 [-1, 1] 대칭으로 변경됨 (기존 [0, 1])
  - queue_directional_depletion DB에 정상 저장 확인
  - volume_acceleration 극단값 3.0 클리핑 동작 확인

- [NEXT 이번 주] **ema_cross 연속값 전환**
  - features["ema_cross"] = 이진값 → (ema5 - ema20) / (ema20 + 1e-9) 연속값
  - 초기 워밍업 20봉 이전은 0.0 처리 방어 코드 필요

- [NEXT 이번 주] **avg_volume 이름 분리**
  - features["avg_volume"] = vol → features["bar_volume"] = vol + features["avg_volume"] = 이동평균
  - _vol_history 버퍼 활용 (이미 존재)
  - OfiReversalCalculator에 전달하는 avg_volume=vol 인자도 함께 수정

- [NEXT 추후] **tick_size = 0.05 설정화**
  - config/settings.py TICK_SIZE = 0.05 추가
  - feature_builder.py FeatureBuilder.__init__ 파라미터화

---
## 2026-06-05 (118차 — daily_close Qt 메인 스레드 블로킹 버그 수정)

### 한일 요약

- [DONE 2026-06-05] **UI 먹통 버그 수정** — `daily_close()` 백그라운드 데몬 스레드 분리. Qt 타이머 stop을 스레드 분기 전 메인 스레드에서 처리. (`main.py` `_scheduler_tick`)

### 다음 할 일

- [NEXT 다음 장] **118차 수정 효과 확인**
  - 기동 후 38초 뒤에도 UI 정상 응답 (먹통 재발 없음)
  - `[Retrain] 배치 재학습 시작` 로그가 백그라운드에서 출력 (장외 재시동 시)
  - `[Daily] 마감 통계` → `[FeatureBuilder]` 로그 이후 타이머·탭 자동전환 정상 동작 확인

- [NEXT 추후] **daily_close 내 Qt-unsafe 호출 점검**
  - `notify()` Slack HTTP 직접 호출이면 안전. Qt 시그널 emit 있으면 `QTimer.singleShot(0, ...)` 마샬링 검토

---

## 2026-06-05 (117차 — 종료 흐름 구조 수정 + microprice 버그 방어)

### 한일 요약

- [DONE 2026-06-05] **microprice debug log 방어** — `.get(, 0.0)` fallback + try/except (`features/feature_builder.py`)
- [DONE 2026-06-05] **`_gbm_retrain_done_event` 직렬화 구현** — 재학습 시작 4곳 clear + 완료 콜백 set + daily_close 대기 블록 (`main.py`)

### 다음 할 일

- [NEXT 다음 장] **EOD 직렬화 효과 확인**
  - `[DailyClose] STEP 3 재학습 진행 중 — EOD 재학습 전 완료 대기` 로그 여부
  - 전 호라이즌 pkl 수정 시각이 15:40 이후 동일 세션으로 완성되는지 (오늘 15m/30m/RF 미완)
  - `[P8] EOD 스케일러 재적합 완료` + `session_state["p8_last_success_date"]` 기록 확인

- [NEXT 다음 장] **116차 + 117차 수정 효과 통합 확인**
  - `[PipePerf] total=Xms` 2500ms 이하 (DB 배치화 효과)
  - `[EffectReports] run failed` 재발 없음 (IndexError 수정 효과)
  - microprice ERR-FATAL 재발 없음

---

## 2026-06-05 (116차 — subprocess/DB 병목 수정 + 로그 레벨 정비)

### 한일 요약

- [DONE 2026-06-05] **EffectReports subprocess IndexError 수정** — `text=True` 제거, 바이너리 PIPE + 수동 decode
- [DONE 2026-06-05] **ConstOut 스팸 억제** — `scripts/run_microstructure_ab_backtest.py` SIGNAL 로거 ERROR 설정
- [DONE 2026-06-05] **verify_and_update 배치화** — 24연결→2연결, 예상 6250ms→520ms
- [DONE 2026-06-05] **save_candle_and_features 신규** — 2연결→1연결
- [DONE 2026-06-05] **save_step9_batch 신규** — 7연결→1연결, 예상 1753ms→260ms
- [DONE 2026-06-05] **BrokerSync 로그 레벨 조정** — `before=FLAT+rows=0` → DEBUG/INFO

### 다음 할 일

- [NEXT 다음 장] **파이프라인 병목 개선 효과 실측**
  - `[PipePerf] total=Xms` 로그에서 13242ms→2500ms 이하 개선 여부 확인
  - CB 5분 정지 재발 여부 확인
  - `[EffectReports] run failed` 로그 재발 없음 확인

- [NEXT 다음 장] **STEP 4 잔여 병목 파악**
  - 위 배치화 이후에도 S5 레이블 여전히 >500ms이면 STEP 4 내 추가 DB 호출 존재 가능
  - `_record_shap_feature_window`, `_refresh_shap_state` 등 점검

---

## 2026-06-05 (115차 — Extreme 피처 절대값→상대값 정규화 전면 구현)

### 한일 요약

- [DONE 2026-06-05] **Phase 1: SCALER_CLIP_FEATURES 확장** — 8개 추가/변경 (`config/settings.py`)
- [DONE 2026-06-05] **Phase 2-A: macro_vix_abs 제거** (`macro_feature_transformer.py`, `registry.json`)
- [DONE 2026-06-05] **Phase 2-B: feature_recoverable_errors 제거** (`feature_builder.py`, `registry.json`)
- [DONE 2026-06-05] **Phase 4: Gap Offset 구현** (`multi_horizon_model.py`, `main.py`)
- [DONE 2026-06-05] **Phase 2-C/D: microprice/vwap 절대값 제거** (`feature_builder.py`, `registry.json`)
- [DONE 2026-06-05] **Phase 3-A: cvd/cvd_slope 일중 정규화** (`cvd.py`, `feature_builder.py`)
- [DONE 2026-06-05] **Phase 3-B: queue 비율화** (`queue_dynamics.py`, `feature_builder.py`)
- [DONE 2026-06-05] **GBM 재훈련** — weeks_back=10, 16,406행×105피처, 6/6 성공
- [DONE 2026-06-05] **EOD 재훈련 스크립트** — `scripts/eod_retrain.py`, `EOD_RETRAIN.bat`
- [DONE 2026-06-05] **구현 계획서** — `docs/260605_FEATURE_NORMALIZATION_PLAN.md`

### 다음 할 일

- [NEXT 2~3일 후] **feat=118 불일치 해소 확인** — ScalerWarmup 로그 `feat=105` 안착 확인. 오늘 DB 잔존 이전 피처 사라지면 자연 해소

- [NEXT 다음 장] **115차 수정 발동 확인**
  - 스케일러 패널 extreme Top5에서 microprice/vwap 발생수 감소 여부
  - `[GapOffset] today_open=XXXX | offset: {...}` 로그 (09:00 첫 분봉)
  - D_FORCE extreme 발생 시 vwap 더 이상 Top5 진입 여부

- [NEXT 1주일 후] **Phase 2-E: *_age_sec 2개 제거** — Phase 1 clip 안정 확인 후 `quality_investor_age_sec`, `quality_macro_age_sec` feature_builder.py 제거 + registry 제거 + GBM 재훈련

- [NEXT 1주일 후] **cvd/queue DB 혼재 해소 확인** — cvd 값 범위 [-1,+1] 수렴, GBM acc 변화 모니터링

- [NEXT 추후] **Phase 3-C: B축 수급 11개 OI 비율화 설계** — Cybos FutureMst open_interest 활용. `docs/260605_FEATURE_NORMALIZATION_PLAN.md` Task 3-3 참조

---

## 2026-06-05 (114차 — 재학습 피처셋 불일치 사고 분석 + P0~P4 개선)

### 한일 요약

- [DONE 2026-06-05] **P0: registry 수동 복구** — `shap_feature_registry.json` active/baseline_features 87→105개 교체. feat=105 복귀 확인. 백업: `.bak_20260605_125941`
- [DONE 2026-06-05] **P1: ScalerWarmup managed_feats 필터 제거** — `load_features_for_warmup`에서 registry 기준 필터 블록 제거. registry 변화에 면역. (`learning/batch_retrainer.py:436`)
- [DONE 2026-06-05] **P2: 재학습 실패 시 registry 롤백** — `_reset_rollback_active` 저장/복원. (`main.py`)
- [DONE 2026-06-05] **P3: 시작 시 registry ↔ pkl 정합성 경고** — `_check_registry_feature_consistency()` 신규. (`model/multi_horizon_model.py`)
- [DONE 2026-06-05] **P4: weeks_back 8→10** — 실측 12,605봉 → ~15,750봉. (`learning/batch_retrainer.py`, `main.py` 3곳)

### 다음 할 일

- [NEXT 다음 기동 시] **114차 개선 발동 검증**
  - `[Retrain] 배치 재학습 시작 (weeks_back=10)` + 피처 15,000+ 확인 (P4)
  - `[ScalerWarmup] 피처 로드 완료 n=500 feat=105` 유지 확인 (P1)
  - 재학습 성공 후 `[Model] 시작 시 정합성 오류` 로그 없음 확인 (P3)
  - `[FeatureOps] 재학습 실패 — active_features 롤백 N개 복원` WARN 로그 — reset 후 재학습 실패 시 (P2)

- [NEXT 재학습 성공 후] **long 정확도 회복 확인**
  - 현재 long 50분 14~20% → 재학습 후 40%대 회복 여부 확인

- [NEXT 추후] **shap_feature_registry 자동화**
  - 재학습 완료 후 `feature_names.pkl` 기준으로 registry.active_features 자동 동기화 검토
  - `_save_feature_names()` 완료 후 registry 동기화 로직 추가

---

## 2026-06-05 (113차 — FL 편향 고착 4종 구조 개선)

### 한일 요약

- [DONE 2026-06-05] **P1: 10m/15m class_weight 명시 설정** — `_CW_10M={FL:0.80}`, `_CW_15M={FL:0.75}` 추가. `balanced` 제거. (`learning/batch_retrainer.py`)
- [DONE 2026-06-05] **P2: FL 편향 고착 → uniform fallback** — FL 90%+ 20분 지속 시 해당 호라이즌 예측을 `{1/3,1/3,1/3}`으로 치환. `[BiasReset]` 로그. (`main.py`)
- [DONE 2026-06-05] **P3: CB③ 해제 마진 0.05→0.03** — `CB_CB3_WARN_RESET_MARGIN=0.03`. 28%+3%=31% 기준으로 경고 리셋. (`config/settings.py`)
- [DONE 2026-06-05] **P5: 15m FL 편향 독립 CB 이벤트** — `record_horizon_fl_bias()` 신규. 30분 지속 시 CRITICAL + Slack. (`safety/circuit_breaker.py`, `main.py`)

### 다음 할 일

- [NEXT 다음 장 중] **113차 4종 수정 발동 검증**
  - `[BiasReset] 10m FL편향 XX% 20분 지속 → uniform fallback 적용` 로그 확인
  - `[BiasReset] 15m FL편향 XX% 20분 지속 → uniform fallback 적용` 로그 확인
  - `[CB-FLBias] 15m FL편향 XX% 30분 고착` Slack 경보 수신 여부
  - GBM 재학습 후 `[Bias]` 로그에서 10m/15m FL 비율 감소 여부

- [NEXT 다음 장 중] **P2 오발동 모니터링**
  - uniform fallback 적용 중 실제 FL 구간(횡보장)에서 잘못 치환되는 케이스 확인
  - 오발동 빈번 시 임계 90%→95% 상향 또는 연속 20분→30분으로 강화 검토

- [NEXT 다음 장 중] **오늘 09:11~09:12 지연 원인 재확인**
  - P4(EarlyWarmup 가드)는 오진으로 취소. 실제 원인은 EKS 발동 후 스케일러 재적합 경합
  - 다음 장 EKS 발동 시 `[PipePerf]` S5 구간 소요시간 확인

- [NEXT GBM 재학습 후] **10m/15m FL 비율 정량 검증**
  - 현재 FL~34% → class_weight 변경 후 FL~30% 수준으로 감소 확인
  - `[Bias]` 로그 FL 비율 추이 1주 관찰

- [NEXT 중기] **5m 정확도 20% 급락 원인 파악**
  - 오늘 10:40 이후 5m 20%로 급락. FL 편향 전이로 추정.
  - P2(uniform fallback)가 5m에도 적용되는지 확인 (FL 90%+ 조건 충족 시)

## 2026-06-05 (112차 — 신규 버그 3종 수정)

### 한일 요약

- [DONE 2026-06-05] **P1: EarlyWarmup 임계값 24h→4h** — EARLY_WARMUP_MIN_AGE_HOURS=4.0 신규 상수, main.py EarlyWarmup 조건 완화 (config/settings.py, main.py)
- [DONE 2026-06-05] **P2: CB③ 최솟 샘플 수 25→30** — CB_ACC30M_MIN_SAMPLES=30 신규 상수, 경고·HALT 메시지에 
=샘플수 표시 (config/settings.py, safety/circuit_breaker.py)
- [DONE 2026-06-05] **P6: Contrarian CLEARED streak 리셋 버그** — CLEARED→WATCHING 시 streak/last_dir/active_dir 리셋 추가 (safety/contrarian_mode.py)

### 다음 할 일

- [NEXT 다음 장 중] **112차 3종 수정 발동 검증**
  - [EarlyWarmup] 08:45 발동 여부 (SYSTEM.log)
  - [CB③] 경고·HALT 메시지에 
= 표시 확인
  - Contrarian ACTIVE→CLEARED 후 재진입 억제 확인

- [NEXT 다음 장 중] **파이프라인 지연 근본 원인 파악**
  - 오늘 09:11~09:44 CB⑤ 4회 반복 — scaler 재적합 daemon 경합인지 STEP별 DEBUG.log 확인
  - [PipePerf] 로그에서 S2·S3·S5 구간별 소요시간 확인


## 2026-06-04 (110차 세션 마무리) — 진입0 개선 6종 후속 검증

### 한일 요약

- [DONE 2026-06-04] **① opt_pcr_slope_norm SCALER_CLIP_FEATURES 추가** — `(-3.0, 3.0)` clip (`config/settings.py`)
- [DONE 2026-06-04] **② EKS P3 해제 임계값 완화** — 0.50 → `max(mc, 0.42)` (`safety/system_health.py`, `main.py`)
- [DONE 2026-06-04] **③ CoherenceGate 차등 임계값** — GAP_OPEN·TrendGate ON 구간 0.60→0.50 (`model/ensemble_decision.py`)
- [DONE 2026-06-04] **④ ShortHorizonOverride** — FLAT 5봉+ 시 1m/3m+OFI/CVD 합의로 방향 결정 (`model/ensemble_decision.py`)
- [DONE 2026-06-04] **⑤ Platt 보정기 영속화** — save/load, ENSEMBLE_CALIBRATOR_PATH (`learning/calibration.py`, `main.py`, `config/settings.py`)
- [DONE 2026-06-04] **⑥ opt_pcr_* D_FORCE 연동 감쇠** — 30분간 0.3× 타이머 (`model/multi_horizon_model.py`)

### 다음 할 일

- [NEXT 다음 장 중] **110차 개선 6종 발동 로그 확인**
  - `[PCR-Dampen]` — opt_pcr D_FORCE 후 감쇠 발동 확인
  - `[ShortHorizonOverride]` — FLAT 고착 시 1m/3m 방향 채택 확인
  - `[SHS-EKS] EKS 자동 해제 ... (임계=43.0%)` — P3 완화 조건 동작 확인
  - `[CoherenceGate 차단 ... zone=GAP_OPEN min=0.50]` — 차등 임계값 로그 확인
  - `[Calibration] 앙상블 보정기 복원/저장 완료` — pkl 영속화 확인

- [NEXT 다음 장 중] **ShortHorizonOverride 오발동 모니터링**
  - 실제 횡보장에서 1m/3m 우연 합의로 진입 후 손절 발생 여부
  - 오발동 빈번 시 streak 임계 5→7 상향 또는 OFI+CVD 동시 조건으로 강화

- [NEXT 다음 장 중] **PCR 감쇠 효과 검증**
  - D_FORCE opt_pcr 발동 후 30분 conf 개선 여부 (before/after)
  - 감쇠 중에도 D_FORCE 반복 발동 시 → 감쇠 계수 0.3 → 0.1 추가 강화 검토

- [NEXT 중기] **ECE 0.250 → 0.05 목표 캘리브레이션 개선**
  - 영속화 보정기 사용 후 calibration_metrics.json 재생성 → ECE 추이 확인
  - bin=4(40~50%) 실제 acc 36.3% → 보정 후 40%+ 달성 여부
  - 보정 후 mc 기준 재검토 가능

- [NEXT 1주 후] **CoherenceGate 차등 임계값 정량 검증**
  - GAP_OPEN 구간 CoherenceGate 차단 건수 감소 비율 확인
  - 승률 저하 없이 진입 증가 확인 → 0.50 유지. 승률 저하 시 0.55 조정

## 2026-06-04 (109차 세션 마무리) — MaskedFallback + PriceStructureBoost 후속 검증

### 한일 요약

- [DONE 2026-06-04] **12:44 이후 진입 미발생 원인 로그 분석** — 앙상블 conf 저하·TrendGate 차단·opt_pcr_slope_norm 극단값 3중 원인 특정
- [DONE 2026-06-04] **opt_pcr 원시 데이터 검증** — 외인 풋 매수 급증 실제 신호 확인 (데이터 이상 아님)
- [DONE 2026-06-04] **ScalerMonitorPanel D_FORCE 툴팁** — "오늘 refresh 이벤트" 카드에 A/B/C/D 트리거 종류 + D_FORCE 조건 HTML 툴팁 추가
- [DONE 2026-06-04] **안 1 MaskedFallback 구현** — `multi_horizon_model.py` `_predict_masked` + `last_masked_proba`; `main.py` 격리 블렌딩 + 채택 로직
- [DONE 2026-06-04] **안 2 PriceStructureBoost 구현** — `trend_persistence.py` `_price_structure()` + min_conf 0.38 부스트; `main.py` `_price_struct_buf` + TrendGate 전달

### 다음 할 일

- [NEXT 다음 장 중] **MaskedFallback 발동 확인**
  - SIGNAL.log에서 `[MaskedFallback]` 로그 확인 (격리 피처명·conf 전후·grade)
  - 채택 후 실제 가격 방향과 일치 여부 → 잘못 채택 케이스 있으면 CONF_GAIN 임계 상향 검토

- [NEXT 다음 장 중] **PriceStructureBoost 발동 확인**
  - SIGNAL.log에서 `가격구조 부스트 ON` + `min_conf 0.44→0.38` 로그 확인
  - 부스트 발동 후에도 conf < 0.38이면 — 0.38보다 더 낮추거나 conf_boost 추가 검토
  - 부스트 오발동(횡보 구간에서 HH-HL 5봉 연속 발생) 여부 확인

- [NEXT 추후] **안 3 — PCR 가중치 동적 감쇠 검토**
  - D_FORCE 유발 피처가 opt_pcr_* 계열이면 모델 입력에서 해당 피처 가중치 0.3배 감쇠
  - SGD 학습률 임시 0 처리 포함 — SGD 학습 불안정 가능성으로 별도 검증 필요

## 2026-06-04 (108차 세션 마무리) — CB⑤ 경고 완화 후속 확인

### 한일 요약

- [DONE 2026-06-04] **EffectReports 파이프라인 외부 분리** — minute pipeline 동기 `subprocess.run()` 제거, 전용 `QTimer` + background worker 추가 (`main.py`)
- [DONE 2026-06-04] **CB⑤ 1000~1300ms degraded soft-weight 적용** — HealthPolicy warning streak / ratio를 latency 구간별 가중 집계로 변경 (`main.py`)
- [DONE 2026-06-04] **ProgramTrade probe 반복 실패 루프 중단** — 정기 투자자 수집 경로에서 `include_program=False` 적용 (`main.py`, `collection/cybos/investor_data.py`)
- [DONE 2026-06-04] **ConstOut 직후 3분 heavy cooldown 추가** — 추가 scaler refresh / EffectReports / heavy panel refresh 유예 (`main.py`)
- [DONE 2026-06-04] **문법 검증** — `python -m py_compile main.py collection\cybos\investor_data.py`

### 다음 할 일

- [NEXT 다음 장 중] **CB⑤ 경고 감소 효과 검증**
  - WARN.log에서 `CB⑤` 경고 건수, `1000~1300ms` 경계값 경고 비중, degraded 진입 시각 확인
  - `warn_streak`가 soft-weight로 누적되는지 HealthPolicy 로그 확인

- [NEXT 다음 장 중] **EffectReports 비동기 worker 동작 확인**
  - 파이프라인 경고 시각과 `EffectReports` 실행 시각이 더 이상 직접 겹치지 않는지 확인
  - `worker already running` / cooldown skip 로그가 과도하지 않은지 확인

- [NEXT 다음 장 중] **ConstOut heavy cooldown 동작 확인**
  - ConstOut 직후 3분 동안 heavy panel refresh / scaler refresh skip 로그 확인
  - cooldown 종료 후 정상 재개되는지 확인

- [NEXT 추후] **EffectReports `list index out of range` 근본 수정**
  - 비동기 분리로 급한 불은 껐지만 traceback 기준으로 실제 원인 라인 특정 후 수정 필요

- [NEXT 추후] **ProgramTrade 재도입 여부 재평가**
  - 수동 probe 스크립트 결과와 대신증권 문서 기준으로 실제 운영 경로 복구 가능성 검토

## 2026-06-04 (107차 세션 마무리) — 재시동 확인 + EffectReports 분석

### 한일 요약

- [DONE 2026-06-04] **CybosApiConnector NameError 수정** — `_probe_dump_done` 참조 `CybosApiConnector` → `CybosAPI` (api_connector.py:921-922)
- [DONE 2026-06-04] **S2 파이프라인 지연 개선** — MetaConfidenceLearner._partial_fit() 6회/분 → 1회/분 throttle. `flush_fit()` 신규, `_fit_pending` 플래그 (meta_confidence.py, main.py)
- [DONE 2026-06-04] **S2 세부 타이밍 로그 추가** — `[S2] meta/learn/flush ms` DEBUG 로그, 500ms 초과 시 기록 (main.py)
- [DONE 2026-06-04] **107차+106차 실세션 전수 확인** — 10:53:33 재시동 후 투자자 수급(supported=True source=7221) ✅, S2≤1000ms ✅, OptionChain stale 복구 ✅, DivergencePanel 매분 정상 ✅
- [DONE 2026-06-04] **EffectReports traceback 로깅 추가** — main.py:4769 except 블록 traceback.format_exc() 추가, rc!=0 브랜치 stdout 추가

### 다음 할 일

- [NEXT 다음 장 중] **EffectReports 에러 근본 원인 특정**
  - WARN.log에서 `[EffectReports] run failed <script>:\nTraceback` 전문 확인
  - `list index out of range` 정확한 파일·라인 확인 후 수정
  - 스크립트 직접 실행 성공 확인 → 메인 파이프라인 무영향, 낮은 우선순위

- [NEXT 다음 장 중] **S2 flush_ms 모니터링**
  - DEBUG.log: `[S2] meta=Xms learn=Xms flush=Xms verified=N`
  - flush_ms > 500ms 지속 시 → _partial_fit() incremental 방식 검토
  - learn_ms > 1000ms 지속 시 → online_learner.learn() background 처리 검토

---

## 2026-06-04 (111? ?? ???) ? ??? ??? ?? ?? ??
### ?? ?? ??

- [DONE 2026-06-04] **??? ??? ?? 1? ?? ???**
  - `?? ???`
  - `?? conf ? ???? ??`
  - `mc ?? ??`
  - ? ?? ?? ?? ? ???? ??

- [DONE 2026-06-04] **?? conf ? ???? ?? 9? ??**
  - `??/conf/mc/?/dir/grade/gate/meta-tox/????`
  - 8?? ??, ?? ??, ?? ?? ??

- [DONE 2026-06-04] **?? ??? ??? ?? ??? ?? ??**
  - `QLabel` ? `QTextEdit`
  - ??? ? ? ??, ??/?? ??

- [DONE 2026-06-04] **???? ?? ?? ??**
  - `trades.db` + ?? `TRADE.log` fallback
  - ? ?? `?2?` ?? ??
  - ?? ?? ??? ??? `8. ????` ?? ??

### ?? ??

- [NEXT ?? ???] **8. ???? ???? ??**
  - ?? ?? ?? ???? `????=8. ????` ?? ??
  - ??? `??/??/??/????/??` ? ?? ??

- [NEXT ?? ???] **?? ?? ?? ?? ??**
  - `logs/YYYYMMDD_TRADE.log` ? `[????]`, `[??????]`, `[?????] ????` ??? ?? ?? ???? ??? ??
  - ?? ? ?? ?? ?? ?? ?? ??

- [NEXT ?? ???] **trades.db ?? ?? ??**
  - ?? ??? ???? `trades.db` 0??? ?? ?? ??
  - `entry_ts` ?? ??? `ensemble_decisions.ts` ?? ?? ??

- [NEXT ??] **??? ??? ?? ?? ??**
  - `gate_reason` ?? ?? ?? ??
  - `????` ? ??? ?? ?? ?? ?? ??

## 2026-06-04 (106차) — 다이버전스 패널 + 옵션 체인 수정

### 한일 요약

- [DONE 2026-06-04] **투자자 수급 TR 오사용 수정** — CpSyrNew7212(존재안함) → CpSyrNew7221, 입력 (0,1)→(0,ord('1')), 파싱 행=상품종류 열=투자자 전면 재작성 (api_connector.py)
- [DONE 2026-06-04] **probe 진단 로그 강화** — logger→system_logger, 헤더 24→32, fi 10→15, ri 20→30, 세션 1회 raw 덤프 (api_connector.py)
- [DONE 2026-06-04] **옵션 체인 ATM miss 자동 재로드** — stale 캐시 감지 시 CpUtil.CpOptionCode 즉시 재로드 (option_chain_snapshot.py)
- [DONE 2026-06-04] **옵션 체인 valid=0 처리** — _chain_raw=[] 초기화 → 다음 poll 강제 재로드 (option_chain_snapshot.py)
- [DONE 2026-06-04] **옵션 체인 장 시작 즉시 폴링** — 타이머 시작 즉시 _poll_option_chain() 1회 (broker_runtime_service.py)
- [DONE 2026-06-04] **옵션 체인 로그 SYSTEM 전환** — "OPTIONS" logger → system_logger (option_chain_snapshot.py)
- [DONE 2026-06-04] **stale 캐시 삭제** — data/option_chain.json (max strike 1340 < spot 1385)

### 다음 할 일

- [NEXT 필요 시] **_check_7212.py 직접 실행 (Cybos 로그인 + 장 중)**
  - CpSyrNew7221 rows 구조: ri=2(선물) fi=2/5/8 값 확인
  - CpSvr8119 프로그램 매매 헤더 레이아웃 확인

- [NEXT 추후] **프로그램 매매 TR (CpSvr8119) 파싱 검증**
  - _check_7212.py 결과에서 헤더 인덱스 실측 → request_program_investor 추정값 보정

---

## 2026-06-03 (103차) — 중복 피처 구조 개선 2종

### 한일 요약

- [DONE 2026-06-03] **[103-P1] Microstructure 중복 해소** — MetaGate lob_imbalance/vpin_proxy 제거, meta_confidence 피처 벡터 9→7 (learning/meta_confidence.py, strategy/entry/meta_gate.py)
- [DONE 2026-06-03] **[103-P2] Toxicity 중복 해소** — ExecutionGovernor toxicity_passability×0.15 제거, 가중 재분배 conf×0.40/quality×0.35/latency×0.25 (strategy/runtime/execution_governor.py, main.py)

### 다음 할 일

- [NEXT 다음 기동 시] **103차 실세션 확인**
  - `[MetaGate]` 로그: mlofi_norm 불리 구간에서 `action=skip` 빈도 감소, `action=reduce` 전환 확인
  - MetaConfidenceLearner `source=규칙기반` → 50샘플 후 `source=SGD` 전환 로그
  - `[ExecutionGovernor]` reduce/block 사유: `latency_warn_reduce` / `tradability_reduce` 기반인지 확인 (toxicity 아님)
  - `[ToxicityGate]` reduce 시 size_mult=0.50 단독 적용 (ExecGov 중복 없음)

- [NEXT 1주 후] **103-P1 효과 검증**
  - MetaGate skip 발생 분봉 수 감소 여부 (일일 리포트 또는 P3 카운터와 비교)
  - mlofi_norm 불리 구간 진입 발생 여부 관찰

---

## 2026-06-02 (102차) — 진입0 분석 + P0~P8

### 한일 요약

- [DONE 2026-06-02] **P0** feature/scaler 정합성 자동 검증 + ERR-FATAL 2회 연속 자동 복구 (multi_horizon_model.py, main.py)
- [DONE 2026-06-02] **P1** Checklist min_conf CRASH 패널티 분리 — _zone_base_mc + 최대 +4%p cap (main.py)
- [DONE 2026-06-02] **P2** 동적 mc 상한 캡 — MC_ABS_CEIL 0.75→0.62, MC_STEP_LIMIT 0.08→0.03, MC_ZONE_MAX=0.65 (settings.py, time_strategy_router.py)
- [DONE 2026-06-02] **P3** grade=C→X 신뢰도 차단 카운터 + 일일 리포트 CL신뢰도차단 항목 (checklist.py, main.py, daily_exporter.py)
- [DONE 2026-06-02] **P4** CB③ 4단계화 NORMAL/WATCH(35%)/RESTRICTED(30%) — C등급 RESTRICTED 차단 (settings.py, circuit_breaker.py, main.py)
- [DONE 2026-06-02] **P5** C등급 실험적 자동 진입 플래그 ENTRY_GRADE_C_AUTO_EXP=False 기본 (settings.py, main.py)
- [DONE 2026-06-02] **P6** ShadowSession BLOCKED 30분 알림 + 권장 대응 (shadow_session.py)
- [DONE 2026-06-02] **P7** 재기동 원인 로깅 STARTUP/MANUAL/AUTO_DISCONNECT (main.py)
- [DONE 2026-06-02] **P8** EOD 스케일러 재적합 E_EOD + 08:55 워밍업 스킵조건 완화 (main.py)

### 다음 할 일

- [NEXT 다음 기동 시] **P0~P8 실세션 확인**
  - P0: ERR-FATAL 연속 시 `[P0] 피처 불일치 N회 연속` 로그 + 즉시 재학습 발화
  - P1: CRASH 상태에서 `[P1] Checklist min_conf 분리: 0.XX→0.XX` 로그
  - P2: DynMC 갱신 후 zone_mc 0.65 초과 없음 확인
  - P3: 15:40 일일 리포트 `CL신뢰도차단: N회` 항목 존재
  - P4: acc30m<35% 구간에서 `[CB③-P4] NORMAL → WATCH` 전환 로그
  - P6: BLOCKED 30분 경과 시 Slack + 권장 대응 텍스트 확인
  - P7: `[Session] 재기동 #N | cause=MANUAL` INFO 로그
  - P8: 15:40 `[P8] EOD 스케일러 재적합 완료 n=500봉` 로그 + 다음날 09:00 scaler age < 30분

- [NEXT 의도적 실험 후] **P5 C등급 자동 진입 활성화 검토**
  - `ENTRY_GRADE_C_AUTO_EXP = True` 전환 조건: P0~P4 안정 확인 + TrendGate 발동 케이스 관찰
  - 활성화 후 C 실험 진입 건수 + 수익률 별도 추적

- [NEXT 1주 후] **P1~P2 임계값 효과 검증**
  - P3 카운터 (CL신뢰도차단)가 여전히 하루 50회+이면 min_conf 분리 폭 추가 확대 검토
  - P2: DynMC 0.62 이하 안착 여부 mc_history.db 확인

---

## 2026-06-02 (99·100차) — 저변동성 인식 피처 + GBM 붕괴 방어

### 한일 요약

- [DONE 2026-06-02] **`threshold_feasibility` 피처** — ATR/(1m_threshold×price), GBM이 FLAT 가능성 직접 학습 (feature_builder.py)
- [DONE 2026-06-02] **`micro_regime_code` 피처** — 직전 분 레짐 수치화(0=횡보~4=급변), 1분 lag 허용 (feature_builder.py, main.py)
- [DONE 2026-06-02] **GBM 상수 출력 감지 (ConstOut)** — 5분×range<0.5%p → weight=0+재정규화+SIGNAL 경보 (ensemble_decision.py)
- [DONE 2026-06-02] **SGD 바닥 회복 경로** — 30회+acc≥40% → 0.5%p 소량 회복, 최대 15% (online_learner.py)
- [DONE 2026-06-02] **ConstOut → 스케일러 재적합 훅** — D_FORCE daemon thread, 30분 쿨다운 (main.py)
- [DONE 2026-06-02] **reset_daily() 버그 수정** — _gbm_w/_bucket_learn_count 루프 위치 오류(for h→for bk) (online_learner.py)

### 다음 할 일

- [NEXT 다음 기동 시] **99·100차 실세션 확인**
  - `[ConstOut] 15m 상수 출력 5분 감지 → 앙상블 제외` SIGNAL WARNING 발화 확인
  - `[ConstOut] 상수 출력 확정 → 스케일러 재적합 시작` SYSTEM 로그 확인
  - `[OnlineLearner] long 바닥 회복 SGD=11%` — 바닥 장기 체류 시 회복 발화
  - threshold_feasibility, micro_regime_code DB 저장 확인

- [NEXT GBM 재학습 후] **threshold_feasibility + micro_regime_code 학습 효과 확인**
  - 다음 배치 재학습 후 [Bias] 로그에서 저변동성 구간 FL 예측 비율 변화 관찰
  - 15m 상수 출력 고착 빈도 감소 여부 (특히 오후 13:00~15:00 구간)

- [NEXT 향후] **shap_feature_registry에 신규 피처 2개 추가**
  - GBM 재학습 후 `threshold_feasibility`, `micro_regime_code` active_features에 수동 추가
  - 자동화 로직이 없으므로 수동 갱신 필요 (98차 NEXT 항목과 동일 이슈)

---

## 2026-06-02 (98차 계속) — 진입0 구조 개선 전면

### 한일 요약

- [DONE 2026-06-02] **mc 복원 버그 수정** — sqlite3.Row.get() 오류, 5개 zone 전체 복원
- [DONE 2026-06-02] **REGIME_MIN_CONFIDENCE** 기본값 0.52→0.42, MC_ABS_FLOOR 0.50→0.42
- [DONE 2026-06-02] **ShadowSession z 조건 완화** — 2→50, BLOCKED→LIVE 복구 추가
- [DONE 2026-06-02] **quality_investor_fetch_count** clip 60→5, z=+8 D_FORCE 반복 해소
- [DONE 2026-06-02] **Layer 2 발동조건 양방향** — abs() 전면 적용 (급등=급락)
- [DONE 2026-06-02] **Layer 2 복귀조건 양방향** — bounce+OFI 제거, ATR+z극단만 유지
- [DONE 2026-06-02] **CoherenceGate** FLAT 제외 계산 + 0.67→0.60 (4/6=0.667 수학 오류)
- [DONE 2026-06-02] **CB③ FLAT 예측 제외** + 임계값 0.35→0.28
- [DONE 2026-06-02] **PATH_LABEL_RATIO** 0.45→0.55, _CW_30M {FL:0.70}
- [DONE 2026-06-02] **툴팁 현행화** — 앙상블 등급·신호방향·신뢰도·Layer2·30m 카드

### 다음 할 일 (우선순위 순)

- [NEXT 다음 기동 시] **6/2 수정 사항 실세션 확인**
  - `[DynMC] 기동 복원: STABLE_TREND 0.540 → 0.460` 5개 zone 모두 확인
  - `[DynMC] 기동 복원 REGIME_MIN_CONF NEUTRAL 0.420 → 0.420` 로그
  - CoherenceGate 로그: `score=0.XX (N/M비FLAT)` — FLAT 제외 계산 확인
  - CB③ 로그: `CB③30m=XX%` — FLAT 예측 제외 후 정확도 변화 확인
  - ShadowSession: BLOCKED→LIVE 복구 로그 확인 (acc30m≥40% + core≥70)
  - Layer 2 발동 지표: `±0.5%|±1.0%` 표시 확인

- [NEXT GBM 재학습 후] **30m FLAT 편향 개선 효과 확인**
  - PATH_LABEL_RATIO 0.55 + _CW_30M {FL:0.70} 반영 후 재학습
  - `[Bias]` 로그에서 30m FL% 감소 확인 (기존 79% → 목표 40% 이하)

- [NEXT 주의] **shap_feature_registry 자동화 필요**
  - 피처 추가 시마다 수동으로 active_features 갱신 필요
  - batch_retrainer 재학습 완료 후 자동 반영 로직 검토

- [NEXT ~2026-06-09] **동적 mc 적응 효과 1주 검증**
  - 재학습 후 conf 분포(avg≈0.70)가 mc에 반영되는지 확인
  - 신호 통과율 15~35% 범위 안착 확인 (🎯 신뢰도 게이트 탭)

- [NEXT 2026-06-05] **Phase A 첫 자동 실행 확인**
  - 15:40 `[ThresholdRecal] 재보정 결과` 로그

---

## 2026-06-01 (98차) — 동적 min_conf + GBM 105피처 재학습

### 한일 요약

- [DONE 2026-06-01] **shap_feature_registry 갱신** — active_features 91→108개 (신규 17개 수동 추가)
- [DONE 2026-06-01] **GBM 105피처 재학습** — force=True, 26주, acc 전반 향상 (1m 0.362→0.419)
- [DONE 2026-06-01] **진입0 분석** — conf 평균 0.406(재학습 전)→0.698(재학습 후)
- [DONE 2026-06-01] **금일 실 데이터 진입 시뮬** — mc=0.65: 22건 77% +1,056만원
- [DONE 2026-06-01] **동적 mc 구현** — update_dynamic_mc() + 주기1/2 + mc_history.db
- [DONE 2026-06-01] **DynamicMcPanel** — 🎯 신뢰도 게이트 탭 신규
- [DONE 2026-06-01] **mc 즉시 재보정 실행** — STABLE_TREND 0.540→0.500

### 다음 할 일 (우선순위 순)

- [NEXT 다음 기동 시] **98차 동적 mc 실세션 확인**
  - 08:55 로그: `[DynMC] mc 재보정 완료 trigger=DAILY_WARMUP base=X.XXX`
  - GBM 재학습 완료 후: `[DynMC] mc 재보정 완료 trigger=RETRAIN`
  - 🎯 신뢰도 게이트 탭: mc 카드 5개 + 금일 추이 + 통과율 게이지 + 이력 표시 확인
  - mc_history.db에 이력 행 누적 확인

- [NEXT 다음 기동 시] **GBM 105피처 재학습 효과 실세션 확인**
  - SIGNAL 로그: `[Retrain] DB 로드 완료: X행 × 105피처` 확인
  - conf 분포 개선: avg 0.406→0.60+ 달성 여부
  - 진입 발생 여부 (mc=0.50 기준, grade A/B/C 분봉 확인)

- [NEXT 주의] **shap_feature_registry 자동화 필요**
  - 신규 피처 추가 시마다 수동으로 active_features 갱신해야 함
  - GBM 재학습 완료 후 raw_features의 최신 피처 키를 registry에 자동 반영하는 로직 추가 검토
  - 위치: `batch_retrainer.retrain_now()` 또는 `_save_feature_names()` 완료 후

- [NEXT 1주 후] **동적 mc 적응 효과 검증**
  - 재학습 후 새 conf 분포(avg≈0.70)가 다음날 08:55에 반영되는지 확인
  - 목표: STABLE_TREND mc가 0.50→0.62~0.67로 점진 상향
  - 신호 통과율 패널에서 15~35% 범위 안착 확인

---

## 2026-06-01 (97차) — F1 고도화 전면 구현

### 한일 요약

- [DONE 2026-06-01] **피처 17개 추가** — volume_profile.py 신규 + feature_builder.py + backfill_features.py
- [DONE 2026-06-01] **소급 190일 피처 갱신** — 71,155봉 `--update-features` 2회 완료
- [DONE 2026-06-01] **코히어런스 게이트** — COHERENCE_GATE_MIN=0.67, ensemble_decision.py
- [DONE 2026-06-01] **HorizonF1AdaptiveWeight** — F1 EMA 가중치, main.py STEP 1 연결
- [DONE 2026-06-01] **시간대 × 호라이즌 min_conf 2D 표** — MIN_CONF_TABLE, main.py STEP 6
- [DONE 2026-06-01] **호라이즌별 최적 σ_k** — optimize_sigma_k.py + SIGMA_K_PER_HORIZON
- [DONE 2026-06-01] **경로 조건부 레이블** — _path_conditioned_label, PATH_LABEL_RATIO=0.45
- [DONE 2026-06-01] **RF 이종 앙상블** — rf_horizon_model.py 신규, main.py blend×0.30
- [DONE 2026-06-01] **학습 레이블 고정화** — USE_FIXED_LABEL_THRESHOLD=True
- [DONE 2026-06-01] **MIN_TRAIN_BARS 15000** — 5000→15000 (40거래일)
- [DONE 2026-06-01] **GBM 파라미터 강화** — n_estimators=300, learning_rate=0.04
- [DONE 2026-06-01] **방안B: prediction_buffer sigma_at_t 저장** — 96차에서 이미 완료 확인

### 다음 할 일 (우선순위 순)

- [NEXT 다음 기동·재학습 시] **97차 신규 기능 실세션 확인**
  - GBM 재학습 후: `[Retrain] DB 로드 완료: X행 × Y피처 (Y ≥ 113개)` 피처 수 확인
  - RF 학습 로그: `[RF] 30m 학습 완료 (n=X OOB=YY.Y%)` — OOB ≥ 45% 목표
  - 코히어런스 게이트 로그: `[Ensemble] CoherenceGate 차단 score=0.XX` 빈도 확인
  - `[Bias]` 로그: 경로 조건부 레이블 적용 후 FL 비율 (기존 33% → 38~45% 예상)
  - `[P4] 호라이즌 conf 필터: 제외=[...]` 로그 — OPEN_VOLATILE 구간에서 15m/30m 제외 확인

- [NEXT path_ratio 모니터링 — 1주 후] **경로 조건부 레이블 효과 검증**
  - 진입 빈도가 30% 이상 감소하면 path_ratio=0.45 → 0.55로 완화 검토
  - FL 비율이 45% 초과 지속 시 path_ratio 상향 원인 분석

- [NEXT RF 모니터링 — 1주 후] **RF OOB score + 앙상블 기여 점검**
  - OOB < 35% 지속 시 RF 가중치 0.30 → 0.15로 축소 검토
  - `rf_horizons.pkl` 파일 존재 확인 (첫 재학습 후)

- [NEXT 2026-06-05] **Phase A 첫 자동 실행 확인** (기존 계속)
  - 15:40 `[ThresholdRecal] 재보정 결과` 로그
  - threshold_monitor.db 누적 확인

- [NEXT 2026-07-01] **monthly_cleanup.py 첫 실행**
  - `python scripts/monthly_cleanup.py --apply`
  - 5월 SYSTEM.log ~1.5GB 회수 예상

- [NEXT Phase E — 1주 후] **2순위 피처 Robust 재평가**
  - `ofi_norm`, `mlofi_norm`, `ofi_imbalance` 극단 z 빈도 재측정

- [NEXT ~2026-07-11] **Phase B(DriftDetector) — Brier Score DriftDetector 연결**

- [NEXT 실시간 90일 이상 확보 후] **P8: 2단계 예측 구조 A/B 테스트**
  - Stage 1: DIRECTIONAL vs FLAT / Stage 2: UP vs DOWN
  - 현재 반대 예측율 39~41% 구조적 해결의 유일한 남은 방법

---

## 2026-06-01 (95차) — 스케일러 Phase A·C 구현

### 한일 요약

- [DONE 2026-06-01] **SCALER_ROBUST_PLAN.md 신규** — 운영안(4종 트리거)·Robust 도입안(피처별)·DB/UI 설계 전체 (섹션 1~9)
- [DONE 2026-06-01] **Phase A: 08:55 스케일러 워밍업** — `load_features_for_warmup(500봉)` + `refit_scalers_only()` + main.py `_scaler_warmup_worker` daemon thread (4개 파일)
- [DONE 2026-06-01] **Phase C: Robust 전처리** — `apply_robust_preprocess()` 모듈 함수 신규. atr/avg_volume log1p, spread_ticks clip(0,20), mlofi_slope clip(±500). 학습·예측·워밍업 3경로 일관 적용 (4개 파일)

### 다음 할 일 (우선순위 순)

- [NEXT 다음 기동 시] **95차 실세션 확인**
  - 08:55 SYSTEM 로그: `[ScalerWarmup] 완료 n=500봉` 확인
  - `canary_stale_age_hours()` < 1h 이어야 함
  - GBM 재학습 없는 날 스케일러 단독 워밍업 동작 확인
  - atr/spread_ticks 극단 z 빈도 감소 확인 (SIGNAL 로그)

- [NEXT Phase E — 1주 후] **2순위 피처 Robust 재평가**
  - `ofi_norm`, `mlofi_norm`, `ofi_imbalance` 극단 z 빈도 재측정 (Phase A·C 1주 운영 후)
  - 워밍업 후에도 빈번하면 clip 보강 검토

---

## 2026-06-01 (94차) — 스케일러 강건화 완성 + 운영 클린업

### 한일 요약

- [DONE 2026-06-01] **Phase B: 정기/강제 스케일러 refresh** — `check_refresh_trigger()` B_OPEN(15분)·C_PERIODIC(60분)·D_FORCE(극단z) (settings.py + multi_horizon_model.py + main.py)
- [DONE 2026-06-01] **Phase D: cancel_add_ratio DB 클린업** — 11행 삭제, MIN_TRAIN_BARS 3000→5000 복원 (scripts/cleanup_cancel_add_ratio.py + batch_retrainer.py)
- [DONE 2026-06-01] **섹션 8: scaler_monitor.db 수집 레이어** — init_db·insert_events_batch·update_event_refresh·aggregate_daily·insert_daily (model/scaler_monitor_db.py + multi_horizon_model.py + main.py)
- [DONE 2026-06-01] **섹션 9: ScalerMonitorPanel UI** — 실시간·Top5·refresh이벤트·일별이력 (dashboard/panels/scaler_monitor_panel.py + main_dashboard.py)
- [DONE 2026-06-01] **SYSTEM.log 200MB/일 버그 수정** — `[CybosEvent]` + `[CybosRT-EVENT]` INFO→DEBUG (api_connector.py + realtime_data.py)
- [DONE 2026-06-01] **monthly_cleanup.py 신규** — 30일 로그·90일 shap·60일 예측 자동 정리
- [DONE 2026-06-01] **raw_data 백업·trades 백업 삭제** — 42.4MB 회수

### 다음 할 일 (우선순위 순)

- [NEXT 다음 기동 시] **94차 실세션 확인**
  - `[ScalerRefresh] trigger=A_WARMUP` 로그 (08:55)
  - `[ScalerRefresh] trigger=B_OPEN elapsed=6min` 로그 (09:15 최초)
  - SYSTEM.log 당일 5MB 이하 (버그 수정 효과 확인)
  - "🔬 스케일러" 탭 → 호라이즌 노후도 표시 확인
  - 15:40 `[ScalerMonitor] EOD 일별 집계 저장` 로그

- [NEXT 2026-06-05] **Phase A 첫 자동 실행 확인** (기존 계속)
  - 15:40 `[ThresholdRecal] 재보정 결과` 로그
  - threshold_monitor.db 누적 확인

- [NEXT 2026-07-01] **monthly_cleanup.py 첫 실행**
  - `python scripts/monthly_cleanup.py --apply`
  - 5월 SYSTEM.log ~1.5GB 회수 예상

- [NEXT 미구현 — 잔여] **방안B: prediction_buffer sigma_at_t 저장**
  - `predictions` 테이블 `sigma_at_t REAL` 컬럼 마이그레이션
  - `save_prediction()` `sigma_at_t` 파라미터 추가 + DB 저장
  - `verify_and_update()` 저장된 sigma_at_t 기반 threshold 사용

- [NEXT ~2026-07-11] **Phase B(DriftDetector) — Brier Score DriftDetector 연결**
  - DriftDetector 호라이즌별 인스턴스화 (param_drift_detector.py 재활용)
  - 3m 임계값 재산출 검토

- [NEXT Phase E — 1주 후] **2순위 피처 재평가**
  - `ofi_norm`, `mlofi_norm`, `ofi_imbalance` 극단 z 빈도 재측정 (Phase A 1주 운영 후)
  - 빈번하면 clip 보강 검토

---

## 2026-05-30 (91·92차) — rolling σ 방법3 Phase 1+2 구현 + ATR 제거

### 한일 요약

- [DONE 2026-05-30] **SIGMA_K=0.41, SIGMA_W=20, USE_ROLLING_SIGMA_THRESHOLD=True** (config/settings.py)
- [DONE 2026-05-30] **batch_retrainer 방법B** — 봉별 rolling σ×k 레이블 생성 (_load_from_db 수정)
- [DONE 2026-05-30] **sigma_buf 매분 갱신** + HORIZON_THRESHOLDS 매분 rolling σ×k 갱신 (main.py 파이프라인)
- [DONE 2026-05-30] **진입 게이트** — 09:20 미만 금지 / 09:20~09:29 A·size×0.5 / 09:30 표준 (main.py STEP 6)
- [DONE 2026-05-30] **PRE_RETRAIN_SIZE_MULT=0.6** + `_pre_retrain_done` 플래그 (main.py)
- [DONE 2026-05-30] **EOD sigma 저장** `_last_sigma_20` + 일일 리셋 (main.py daily_close)
- [DONE 2026-05-30] **ATR 동적 threshold 완전 제거** — `_log_threshold_monitor`, `_threshold_monitor_tick`, `HORIZON_THRESHOLD_MULT`, `HORIZON_THRESHOLD_OPEN_MULT`
- [DONE 2026-05-30] **ThresholdMonitorPanel** UI 패널 신규 (dashboard/panels)
- [DONE 2026-05-30] **docs/ROLLING_SIGMA_IMPL_PLAN.md** — Phase 0~3 구현 계획 문서

### 다음 할 일 (우선순위 순)

- [NEXT 재시작 시] **91·92차 실세션 확인**
  - `[EntryGate] sigma_20봉 미수집` 로그 (09:00~09:19)
  - `[EntryGate] GBM 첫 재학습 완료 — 사이즈 제한 해제` 로그
  - `[SGD] threshold 교체 후 완전 리셋 완료 (1회)` 로그 (SGD_FULL_RESET_PENDING)
  - `[Sigma] EOD sigma_20=0.0XXXX% 저장` 로그 (15:40)
  - `[Bias] 1m FL=XX%` — FL 35% 이하 확인 (이전 87~100% 대비)
  - "📐 임계값 모니터" 탭 표시 확인

- [NEXT 미구현 — P1 잔여] **방안B: prediction_buffer sigma_at_t 저장**
  - `predictions` 테이블 `sigma_at_t REAL` 컬럼 마이그레이션
  - `save_prediction()` `sigma_at_t` 파라미터 추가 + DB 저장
  - `verify_and_update()` 저장된 sigma_at_t 기반 threshold 사용
  - `main.py` STEP 5 예측 저장 시 `sigma_at_t=self._sigma_20` 전달

- [NEXT 2026-06-05] **Phase A 첫 자동 실행 확인**
  - 15:40 `[ThresholdRecal] 재보정 결과` 로그
  - k=0.41 기준 FLAT 비율이 26~39% 범위 유지 확인
  - threshold_monitor.db 누적 확인

- [NEXT ~2026-07-11] **Phase B 구현 — Brier Score DriftDetector 연결**
  - DriftDetector 호라이즌별 인스턴스화 (param_drift_detector.py 재활용)
  - 3m 임계값 재산출 검토 (현재 보류)

---

## 2026-05-30 (90차) — 임계값 재보정 + Phase A WFA 모니터

### 한일 요약

- [DONE 2026-05-30] **HORIZON_THRESHOLDS 재보정** — 1m→0.00041, 5m→0.00092, 10m→0.00148, 15m→0.00155, 30m→0.00196, 3m 현행 유지
- [DONE 2026-05-30] **HORIZON_THRESHOLDS_RESEARCH** — 비대칭 딕셔너리 신규, ATR 갱신 비대상
- [DONE 2026-05-30] **build_targets_asymmetric()** — 연구용 비대칭 레이블 생성 함수 신규
- [DONE 2026-05-30] **class_weight 재조정** — 1m/5m FL 0.85, 30m FL 1.00. multi_horizon_model + batch_retrainer 동기화
- [DONE 2026-05-30] **OnlineLearner.reset_full()** — SGD 완전 초기화 메서드 신규
- [DONE 2026-05-30] **SGD 1회 자동 리셋** — SGD_FULL_RESET_PENDING 플래그 + _on_gbm_retrain_done
- [DONE 2026-05-30] **ThresholdRecalibrator Phase A** — 신규, 매주 금요일 daily_close 연결
- [DONE 2026-05-30] **docs/THRESHOLD_WFA_MONITOR.md** — Phase A~C 설계 문서 신규

### 다음 할 일 (우선순위 순)

- [NEXT 2026-06-05] **Phase A 첫 자동 실행 확인**
  - 15:40 `[ThresholdRecal] 재보정 결과` 로그
  - 3m/30m UPDATE 경보 추이 관찰
  - `data/db/threshold_monitor.db` 누적 확인

- [NEXT ~2026-07-11] **Phase B 구현 — Brier Score DriftDetector 연결**
  - DriftDetector 호라이즌별 인스턴스화
  - 3m 임계값 재산출 검토

---

## 2026-05-29 (89차) — Qualification 세션 필터 + 호라이즌별 정확도 + 툴팁

### 한일 요약

- [DONE 2026-05-29] **세션 필터**: `_pred_ts_q >= self._session_start_ts` — 이전 세션 carry-over 예측 카운팅 제외 (main.py)
- [DONE 2026-05-29] **호라이즌별 정확도 버퍼**: `_horizon_acc_buf`, `horizon_accuracy(h)`, `reset_daily()` 확장 (learning/online_learner.py)
- [DONE 2026-05-29] **자격 현황 라벨 툴팁**: 카드 설명 + acc 정의 + recent_accuracy() 차이 + 30m 주의사항 (dashboard/main_dashboard.py)

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **88·89차 실세션 확인 (다음 기동 시)**
  - 세션 시작 시 모든 호라이즌 v0/t0 WAIT 출발 확인 (carry-over 없음)
  - 09:01+ 1m v1 → 09:03 v3 ACTIVE 전환, 10m v1은 10분 이후 확인
  - acc% — 5건 미만=0%, 5건+ 실제 적중률 갱신 확인
  - 라벨 호버 시 툴팁 표시 확인

- [NEXT Phase 3 진입 전] **`_restore_qualification_state()` 구현**
  - `prediction_buffer.py`에 `count_verified_today(horizon, date_str)` 헬퍼 추가
  - `main.py` `_restore_qualification_state()` 신규 — DB에서 당일 세션 이후 verified 수 복원
  - `connect_broker()` 장중 재시작 경로에서 호출

- [NEXT Phase 3 — 카드 1세션 확인 후] **앙상블 필터링 활성화 (A-3)**
  - `model/ensemble_decision.py` `compute()`: `active_horizons` 마스크 + 재정규화 ([결정A])
  - 합의도 패널티 분모 수정: `n_agree < n_active/2` ([결정B])
  - `main.py` STEP 6: `active_horizons = _get_active_horizons()` 전달
  - **주의**: Track A-3와 Track B(ExecutionGate) 동시 활성화 절대 금지

---

## 2026-05-29 (88차) — 호라이즌 자격 추적 Phase 1+2 구현

### 한일 요약

- [DONE 2026-05-29] **Phase 1 (A-1): `_horizon_runtime_state` 상태 추적** — `__init__` 딕셔너리, STEP 1 verified_cycles, STEP 2 trained_cycles 동기화, daily_close() 리셋 (main.py)
- [DONE 2026-05-29] **Phase 2 (A-2): 호라이즌 자격 현황 카드** — `EntryPanel._build()` 6카드 2×3 그리드, `update_qualification()` 메서드, MireukDashboard 위임 (dashboard/main_dashboard.py)
- [DONE 2026-05-29] **설정 상수 추가** — `HORIZON_QUALIFY_MIN_CYCLES=3`, `QUALIFY_QUALITY_MIN_SAMPLES=10` (config/settings.py)
- [DONE 2026-05-29] **버그 수정: `name 'settings' is not defined`** — `settings.` → `runtime_settings.` 2곳. 장중 재시작 후 매분 CRITICAL 에러 해소 (main.py)

---

## 2026-05-22 (87차) — Layer 2 UI 개선 + update_layer2() 파이프라인 연결

### 한일 요약

- [DONE 2026-05-22] **발동 지표 6개 재정비** — 시가-0.8&15m 제거, 당일수익률 3색 로직(빨강/오렌지/기본), 임계값 표시 개선 (dashboard/main_dashboard.py)
- [DONE 2026-05-22] **조건 체크 로그 단순화** — NORMAL/DAY_RISK_OFF/CRASH 3줄 고정 포맷 + 복귀 조건 ✔/✘ (dashboard/main_dashboard.py)
- [DONE 2026-05-22] **`_layer2_log` 초기값 설정** — 기동 직후 빈 박스 해소 (dashboard/main_dashboard.py)
- [DONE 2026-05-22] **`update_layer2()` 파이프라인 연결** — main.py STEP 4 직후 1줄 추가. 82차부터 미연결 상태 해소 (main.py)

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **87차 실세션 확인 (2026-05-23)**
  - 기동 직후 `_layer2_log` NORMAL 기본 텍스트 표시 (빈 박스 없음)
  - 장중 발동지표 실시간 갱신 확인 (당일 수익률 3색 발동 여부)
  - NORMAL 상태 조건 로그 3줄 표시 확인

---

## 2026-05-22 (86차) — P0 구현 + EOD 스케일러 초기화

### 한일 요약

- [DONE 2026-05-22] **SHS + EKS 신규** — `safety/system_health.py`. SHS 4가지 구성요소 가중 점수. EKS 09:05 1회 판정. `reset_daily()` 추가
- [DONE 2026-05-22] **SHS 슬랙 알림** — `notify_shs_alert()`, `notify_kill_switch()` (utils/notify.py)
- [DONE 2026-05-22] **SHS UI 배지** — 상단 헤더 `lbl_shs` + `update_shs_badge()` (dashboard/main_dashboard.py)
- [DONE 2026-05-22] **Warm Scaler Canary** — `canary_stale_age_hours()`, `canary_z_warn_count()` + `_load_all()` mtime 동기화 (multi_horizon_model.py)
- [DONE 2026-05-22] **main.py 연동** — Canary 08:55 검사·SHS 업데이트·EKS 판정·GAP_OPEN 기록 (main.py)
- [DONE 2026-05-22] **log_manager `**_kwargs`** — signal/system/trade TypeError 방어 가드 (logging_system/log_manager.py)
- [DONE 2026-05-22] **CORE 피처 진단 로그** — VWAP/CVD/OFI raw값 + 요구값 탈락 시 출력 (checklist.py)
- [DONE 2026-05-22] **EOD `_load_all()` 무조건 호출** — retrain 실패 시에도 최신 pkl 로드 (main.py daily_close)
- [DONE 2026-05-22] **`system_health.reset_daily()`** — EKS·GAP_OPEN 상태 다음날 이월 방지 (main.py daily_close)

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **86차 실세션 확인 (2026-05-23)**
  - `♥ SHS 100` 배지 상단 표시 (정상 기동)
  - `[Canary] scaler 노후=Xh z경고피처=N개` 로그 (08:55)
  - `[SHS-EKS] EKS 미발동` 로그 (09:05 직후 — 정상일이면 미발동)
  - `[Checklist] CORE 피처 ✗ ... | VWAP pos=±X.XXX` 형식 탈락 원인 로그
  - `[Model] 1m 로드 성공` 6개 호라이즌 (15:40 daily_close 후)

- [NEXT 필수 — P0 잔여] **재시작 방지 락 구현**
  - 5/22 재시작 12회 → conf 50% 붕괴의 직접 원인. OnlineLearner 매 재시작마다 초기화
  - BrokerSync rows=0 → connect_broker() 재호출 경로 특정 후 구현
  - `_restart_armistice_until`은 진입 차단만, 재시작 자체는 방지 안 함
  - 구현 전 connect_broker() 재호출 트리거 경로 grep 필요

- [NEXT 권장 — P0 잔여] **Scaler Auto Re-fit**
  - Canary가 노후 감지만, 자동 re-fit 없음
  - 기동 시 `raw_data.db` 최근 5일로 scaler `fit()` 재실행
  - z-score 경고 90% 감소, GBM conf +5~8%p 기대
  - Deep P0-2 제안: `multi_horizon_model.py` `_refit_scaler_if_stale()` 구현

- [NEXT 조사 후 결정 — Codex P0-4] **S2 병목 원인 확인**
  - S2=2364ms가 verified=0 구간(09:00)에서도 발생 → meta_gate.evaluate() 가능성
  - online_learner.learn() 배치화보다 meta_gate 경로 먼저 확인
  - 원인 특정 후 배치화 여부 결정

---

## 2026-05-22 (85차) — 모의투자 이상점 7·8 구조적 수정 4종

### 한일 요약

- [DONE 2026-05-22] **이상점 7-A: `_CW_1M`, `_CW_5M` FL 명시적 완화** — `{FL:0.60, UP:1.20, DN:1.20}`, `{FL:0.58, UP:1.21, DN:1.21}`. multi_horizon_model.py, batch_retrainer.py 동시 적용
- [DONE 2026-05-22] **이상점 7-D: CLOSE_VOLATILE 단기 0.6× 가중치** — ensemble_decision.py `time_zone` 파라미터, main.py `get_time_zone()` 전달
- [DONE 2026-05-22] **이상점 8-B: Platt 슬라이딩 윈도우 200건** — `WINDOW 500→200`, 재보정 주기 `% 50→% 20`
- [DONE 2026-05-22] **이상점 8-C: 10m/15m Platt 하한 `raw_conf×0.85`** — main.py `_apply_horizon_calibration()` 하한 보호

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **85차 실세션 확인 (2026-05-23)**
  - 1m/5m FL 편향: `[Bias]` 로그에서 FL 비율 75% 미만 달성 여부 (이상점 7-A)
  - `[Ensemble] CLOSE_VOLATILE 단기 0.6×` 로그 14:00~15:00 구간 발생 확인 (이상점 7-D)
  - 10m conf: `[Calib] 10m Platt 하한` 로그 발화 빈도 확인 → 하한 발동 시 conf 55%+ 유지 여부 (이상점 8-C)
  - 다음 GBM 재학습 후 1m/5m 호라이즌 FL 방향 비율 변화 SIGNAL 로그 확인 (이상점 7-A)

- [NEXT 향후] **`_CW_1M`, `_CW_5M` 실세션 효과 모니터링 (1주)**
  - 1m FL 비율 목표: ≤ 50% (현재 87%). 5m FL 비율 목표: ≤ 55% (현재 100%)
  - FL 편향 지속 시: FL=0.55 추가 완화 또는 HORIZON_THRESHOLDS 경계값 재검토

- [NEXT 향후] **CLOSE_VOLATILE 가중치 조정 효과 검증 (1주)**
  - 14:00~15:00 구간 진입 신호 발생 여부 + 방향성 비율 변화
  - 0.6× 축소로도 FL편향 미해소 시 0.4× 추가 완화 또는 CLOSE_VOLATILE 구간 진입 임계 상향 검토

## 2026-05-22 (84차) — 모의투자 이상점 3~6 구조적 수정 4종

### 한일 요약

- [DONE 2026-05-22] **이상점 3: `_CW_30M` FL 다운웨이팅 완화** — `{FL:0.5}` → `{FL:0.65, UP:1.18, DN:1.18}`. multi_horizon_model.py, batch_retrainer.py 동시 적용 (학습기 일관성)
- [DONE 2026-05-22] **이상점 4: SGD 정확도 윈도우·조정 주기 수정** — `ACCURACY_WINDOW=150` (실질 50분), `_ADJUST_EVERY=3` (분봉 단위 1회 조정). `_bucket_learn_count` 추가
- [DONE 2026-05-22] **이상점 5: Bias 통계 롤링 버퍼** — 30건 롤링 버퍼, UP/DN/FL 모두 추적, 15건+ 시 75% 초과 편향 감지
- [DONE 2026-05-22] **이상점 6-A: SGD 초기 GBM 전용 모드** — h_count < 30 시 w_gbm=0.95, w_sgd=0.05 (균일분포 희석 방지)
- [DONE 2026-05-22] **이상점 6-B: 앙상블 전용 Platt 보정기** — `ensemble_calibrator = PredictionCalibrator(method="platt")`. 1m 검증 시 `record_ensemble_outcome()` 호출. 3m fallback 유지
- [DONE 2026-05-22] **이상점 6-C: 합의도 패널티** — 6호라이즌 ≤2 합의 시 conf×0.92 패널티. 보너스 미포함 (편향 증폭 위험)
- [DONE 2026-05-22] **이상점 6-D: CORR_ADJ 30m 하향** — 30m 0.20→0.15, 나머지 균등 +0.01 재배분
- [DONE 2026-05-22] **앙상블 전용 calibrator 분리 검토** — 81차 NEXT 항목 완료 (100건 미만까지 3m fallback 유지)

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **84차 실세션 확인 (2026-05-23)**
  - 30m 예측: FL 상황에서 DN 오분류 발생 빈도 감소 확인 (이상점 3)
  - SGD 비중: 연속 실패 시에도 1분 내 14%p 급감 사라지는지 확인 (이상점 4)
  - `[Bias⚠]` 로그: 형식 `[Bias⚠] 30m 적중=X%(N건) UP=N DN=N FL=N [DN편향! 75%+]` 확인 (이상점 5)
  - conf 분포: ≥ 60% 도달 분봉 비율 이전 대비 증가 여부 SIGNAL 로그 확인 (이상점 6)
  - 앙상블 보정기: 100건 누적 후 `[Ensemble] ensemble_calibrator is_fitted=True` 여부 확인 (이상점 6-B)

- [NEXT 향후] **이상점 6-B 앙상블 보정기 100건 누적 후 효과 검증**
  - 100건 이상 누적(≈100분) 후 `ensemble_calibrator.is_fitted=True` 전환 확인
  - 3m fallback → 앙상블 전용 보정기 전환 전후 conf 분포 변화 비교
  - 과보정 발생 시(conf 너무 낮아짐) `PredictionCalibrator(method="platt")` 파라미터 조정 검토

- [NEXT 향후] **_CW_30M 실세션 효과 모니터링 (2주)**
  - 30m FL 비율 목표 ≥ 29% (이전 추정 ≈ 24% 미만 개선 여부 — 단기 지표)
  - 7연속 실패 재발 시: `_CW_30M FL` 추가 완화(0.65→0.75) 또는 30m 특화 별도 파라미터 검토

---

## 2026-05-22 (83차) — 탈진장 ATR ratio 문턱 재설계

### 한일 요약

- [DONE 2026-05-22] **탈진장 dead code 해소** — `ATR_EXHAUSTION_MULT=1.5` 삭제 → `ATR_EXHAUSTION_MIN=1.2`. 탈진 구간 `1.2~1.5`로 급변장과 독립 분리
- [DONE 2026-05-22] **양방향 대칭** — `bull_exhaustion` 파라미터 추가. SHORT MR 탈진(상승 압력 소진)도 탈진장으로 분류
- [DONE 2026-05-22] **`ofi_reversal_speed` 제거** — `push_1m_candle` / `_classify` 파라미터 + exhaustion_conds 조건에서 완전 삭제 (bear_exhaustion이 내포)
- [DONE 2026-05-22] **main.py 호출부 동기화** — `bull_exhaustion` 추가, `ofi_reversal_speed` 제거

### 다음 할 일

- [NEXT 장중] **83차 실세션 확인 (2026-05-23)**
  - `[MicroRegime] 혼합 → 탈진 (ADX=XX.X, ATR=X.XXXX, ratio=1.2X~1.4X)` 로그 첫 발화 확인
  - 발화 시 해당 분봉 SIGNAL 로그: `bear_exhaustion > 0` or `bull_exhaustion > 0` + `abs(vwap_position) ≥ 1.5` 동시 확인
  - 탈진장 진입 시 체크리스트 `min_conf_effective=0.56` / `entry_mode=MEAN_REVERSION` 적용 확인
  - 탈진장에서 VWAP 방향으로 역추세 진입 발생 여부 관찰

- [NEXT 향후] **ATR_EXHAUSTION_MIN 캘리브레이션 (2주 후)**
  - 탈진장 발동 빈도 집계 (목표: 하루 0~3회). 0회 지속 시 1.2 → 1.1 하향 검토
  - 발동 후 MEAN_REVERSION 승률 집계 (목표: ≥ 50%)

---

## 2026-05-22 (82차) — Layer 2 인트라데이 게이트 UI 패널 + L2 토글 영속성 및 즉시 적용

### 한일 요약

- [DONE 2026-05-22] **진입 관리 탭 Pre-flight 패널 양분 (5:6)** — 왼쪽=9개 체크리스트, 오른쪽=Layer 2 패널 3단
- [DONE 2026-05-22] **Layer 2 상태 카드** — L2 ON/OFF 버튼(체크블) + 레짐 색상(NORMAL=녹/DAY_RISK_OFF=주황/CRASH=빨) + 전환 레이블
- [DONE 2026-05-22] **Layer 2 7개 지표** — 당일 수익률·시가−0.8%&15m·15m·30m·ATR ratio·z극단·Contrarian. 발동 항목 빨간색 강조
- [DONE 2026-05-22] **Layer 2 조건 체크 로그** — QTextEdit(readonly) 진입허용·신뢰도강화·사이즈축소·복귀체크 4섹션
- [DONE 2026-05-22] **L2 게이트 영속성** — ui_prefs.json `layer2_gate_enabled`. 재시작 시 복원. blockSignals 처리
- [DONE 2026-05-22] **L2 즉시 적용** — `_l2_gate_on` 플래그 (getattr 폴백). min_conf_adjust·방향차단·size_mult 3곳 우회 분기

### 다음 할 일 (우선순위 순)

- [DONE 2026-05-22] **`update_layer2()` → main.py 파이프라인 연결** — STEP 4 직후 1줄 추가 (87차)

- [NEXT 장중] **82차 실세션 확인 (2026-05-23)**
  - 재시작 후 L2 ON/OFF 버튼 상태가 이전 설정 복원 (ui_prefs.json 읽기)
  - 장중 L2 OFF 토글 시 `[IntradayRegime] Layer 2 Gate UI=OFF (우회 모드)` WARNING 로그 확인
  - L2 OFF 상태 CRASH 레짐에서도 LONG/SHORT 차단 없이 진입 허용 확인
  - `update_layer2()` 연결 후: 레짐 전환 시 상태 카드 색상·7개 지표 발동 상태 실시간 갱신 확인

---

## 2026-05-22 (81차) — Platt 보정 기동 사전 fit + 앙상블 2차 압축

### 한일 요약

- [DONE 2026-05-22] **B1: `self.calibrator` 미선언** — `EnsembleDecision.__init__`에 `self.calibrator = None` 추가. `hasattr` 항상 False → 코드 미실행 버그 수정
- [DONE 2026-05-22] **B2: `.transform()` → `.calibrate()`** — `MultiHorizonCalibrator`에 없는 메서드명 수정
- [DONE 2026-05-22] **B3: grade/auto_entry 미갱신** — 보정 블록을 grade 계산 **전**으로 이동. 보정된 confidence 기준으로 grade/auto_entry 재계산
- [DONE 2026-05-22] **B4(근본): 기동 시 calibrator 0샘플** — `_preload_horizon_calibration()` 신규. DB 18,000건 로드 + `fit_all()`. 첫 tick부터 보정 활성
- [DONE 2026-05-22] **`ensemble.calibrator` 주입** — `main.py __init__`에서 `self.ensemble.calibrator = self.horizon_calibrator`
- [DONE 2026-05-22] **`confidence_raw` 필드 추가** — 보정 전 원본 보존 (result dict)

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **81차 실세션 확인 (2026-05-23)**
  - `[Calib] 기동 사전 학습 완료: N건` 로그 (N≥1000 필수)
  - 0건이면: `predictions` DB 경로 문제 또는 `actual IS NOT NULL` 레코드 없음 → 쿼리 확인
  - 기동 직후 `confidence` 분포가 이전 대비 낮아졌는지 SIGNAL 로그 확인
  - `result` dict에 `confidence_raw` 키 존재 확인
  - `grade`가 calibrated confidence 기준 재판정 (A→B 강등 케이스 발생 여부)

- [DONE 2026-05-22] **앙상블 전용 calibrator 분리 검토** — 84차에서 구현 완료. `ensemble_calibrator = PredictionCalibrator(method="platt")` 분리. 1m 검증 시 학습. 100건 미만까지 3m fallback 유지.

---

## 2026-05-21 (76~80차) — TrendPersistenceGate 대칭 구현 + Layer 2 완전 통합

### 한일 요약

- [DONE 2026-05-21] **76차: cvd_monotone_ratio 피처** — CVD 최근 20개 상승 이동 비율 피처 추가 (feature_builder.py)
- [DONE 2026-05-21] **77차: TrendGate UP 통합** — main.py import·초기화·STEP6·reset_daily 삽입. streak≥10분 시 min_conf 0.44 완화
- [DONE 2026-05-21] **78차: Layer 2 완전 통합** — min_conf_adjust / size_mult / CRASH A등급 숏 예외 3종 구현
- [DONE 2026-05-21] **79차: TrendGate DOWN 대칭** — UP+DN 듀얼 streak. hard_break 비대칭(-300/+200). return dict 확장
- [DONE 2026-05-21] **80차: 대시보드 깜빡임 UI** — 등급카드 테두리 UP=녹색/DN=오렌지 600ms 토글

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **76~80차 실세션 확인 (2026-05-22)**
  - UP streak: `[TrendGate] UP 추세 지속 모드 ON (streak=10)` 로그 확인
  - DN streak: `[TrendGate] DN 추세 지속 모드 ON (streak=10)` 로그 확인
  - 등급카드 깜빡임: UP 활성→녹색, DN 활성→오렌지, 비활성→기본색 복원 확인
  - Layer 2 min_conf_adjust: `[IntradayRegime] ... min_conf +N%p → 0.XX` 로그 확인
  - Layer 2 size_mult: `[IntradayRegime] ... 사이즈 축소 ×0.N → N계약` 로그 확인

- [NEXT 선택] **81차: apply_micro_regime_override() 추세장 min_conf 완화**
  - 현재 추세장(micro_regime) 시 size ×1.1만 있고, min_conf 인하 없음
  - 추세장 min_conf -0.06 적용, 최소 0.44 하한 고려
  - 구현 여부는 실세션 79차 효과 확인 후 결정

---

## 2026-05-21 (72차) — 방향 비대칭 편향 6종 수정

### 한일 요약

- [DONE 2026-05-21] **① OFI 역전 신호 양방향화** — `bull_reversal_signal` + `bear_reversal_signal` 분리. 구 `ofi_reversal_signal` deprecated alias 유지
- [DONE 2026-05-21] **② CVD 탈진 양방향화** — `bear_exhaustion` + `bull_exhaustion` 분리. SHORT MR 의미론 오류 수정 (bear→bull_exhaustion). 구 deprecated alias 유지
- [DONE 2026-05-21] **③ prev_bar_direction 3-state** — `prev_bar_bullish: bool` → `prev_bar_direction: int`. 도지(0) LONG·SHORT 모두 불통과
- [DONE 2026-05-21] **④ PCR 극단값 양방향화** — `pcr_extreme_bullish`(≤0.67) + `pcr_extreme_signed`([-1,+1]) 추가. 구 `pcr_extreme` deprecated
- [DONE 2026-05-21] **⑤ SP500 레짐 임계값 대칭화** — `< -1.0` → `< -0.5`
- [DONE 2026-05-21] **⑥ RL HOLD 페널티 제거** — `hold_penalty = 0.0`

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **72차 신규 신호 실세션 첫 확인 (2026-05-22)**
  - `bull_reversal_signal` / `bear_reversal_signal` SIGNAL 로그에서 각각 발화 확인
  - `bear_exhaustion` / `bull_exhaustion` SIGNAL 로그 발화 확인 (탈진 이벤트 발생 시)
  - 체크리스트 MEAN_REVERSION 분기: LONG MR → `bear_exhaustion>0`, SHORT MR → `bull_exhaustion>0` 발화
  - SP500 레짐: SYSTEM 로그에서 -0.5% 초과 하락 시 score=-1 확인
  - `opt_pcr_extreme_bullish` / `opt_pcr_extreme_signed` SIGNAL 로그 피처값 확인

- [NEXT 모델 재훈련 후] **deprecated 피처 제거 일정**
  - 제거 대상: `ofi_reversal_signal`, `cvd_exhaustion`, `exhaustion`, `exhaustion_signal`, `opt_pcr_extreme`
  - 제거 조건: GBM 모델이 신규 피처로 재훈련 완료 + 실세션 1주 이상 안정 확인 후
  - 제거 시 수정 파일: `features/technical/ofi_reversal.py`, `features/technical/cvd_exhaustion.py`, `features/feature_builder.py`, `features/options/option_features.py`, `collection/options/pcr_store.py`

- [NEXT 미정] **방향 편향 통계 집계 (1~2주 후)**
  - LONG 진입 시도 / SHORT 진입 시도 비율 (목표: 45~55% 균형)
  - MEAN_REVERSION LONG MR vs SHORT MR 균형 여부 집계
  - 편향 지속 시 추가 설계 원인 조사

---

## 2026-05-21 (71차) — 자동진입관리 UI 카드 구조 개편

### 한일 요약

- [DONE 2026-05-21] **앙상블 등급 카드** — 신뢰도 % 중복 제거, EnsembleDecision grade (A/B/C/X) 표시로 전환
- [DONE 2026-05-21] **체크리스트 등급 카드** — 라벨 "진입 등급" → "체크리스트 등급", 순수 `_cr["grade"]` 표시
- [DONE 2026-05-21] **최종진입 카드 신규** — 앙상블+체크리스트 종합 판정, "진입" 시 녹색 600ms 깜박임
- [DONE 2026-05-21] **레이아웃 재구성** — QGridLayout(3열 빈공간) → VBox+2×HBox, 수량 카드 stretch=1 균등 폭

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **71차 UI 실세션 확인 (2026-05-22)**
  - 앙상블 등급·체크리스트 등급이 서로 다른 값을 표시하는 분봉 관찰 (등급 분리 효과 확인)
  - 최종진입 "진입" 상태에서 녹색 깜박임 정상 작동 확인
  - 최종진입 "진입대기" 전환 시 깜박임 정지·테두리 복원 확인

---

## 2026-05-20 (69차) — signal() TypeError ERR-FATAL 수정 + traceback 로깅 강화

### 한일 요약

- [DONE 2026-05-20] **68차 개선 3항목 실세션 검증** — ERR-FATAL 소멸·신뢰도 미달 로그 정상·watchdog 거짓 경보 없음 모두 확인
- [DONE 2026-05-20] **`_Collector.signal` level 파라미터 추가** — `scripts/validate_health_policy_hotreload.py` `_Collector.signal(self, msg, level="INFO")`. monkey-patch 중 TypeError 방지
- [DONE 2026-05-20] **main.py signal() positional→keyword 변환** — `_hc_block`·IntradayRegime 롱·숏 차단 3곳 `"WARNING"` positional → `level="WARNING"` keyword
- [DONE 2026-05-20] **error_policy.py traceback 로깅 추가** — `import traceback` + RECOVERABLE·DEGRADED·FATAL 3케이스 모두 `traceback.format_exc()` 로깅. 다음 ERR-FATAL 발생 시 정확한 라인 파악 가능

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **69차 수정 실세션 확인 (2026-05-21)**
  - ERR-FATAL `signal() takes 2 positional arguments but 3 were given` 재발 없음 확인
  - `[보호] 고신뢰 연속오답 N회 — 신규 진입 차단` 로그 정상 출력 (TypeError 없음)
  - `[IntradayRegime] CRASH — 신규 롱/숏 금지` 로그 정상 출력 (TypeError 없음)
  - 다음 ERR-FATAL 발생 시 WARN.log에 traceback 포함 확인 (파일명·라인번호)

---

## 2026-05-20 (68차) — minute_pipeline ERR-FATAL 실제 근본 원인 최종 수정

### 한일 요약

- [DONE 2026-05-20] **checklist.py `entry_mode` UnboundLocalError 최종 수정** — `entry_mode = "TREND_FOLLOW"` 초기화를 `checks = {}` 바로 다음(line 77)으로 이동. 신뢰도 미달 조기 반환(line 89~96)보다 선행 할당 보장
- [참고] **81e0784 (`main.py`) 수정은 오진단** — UI 모드 변수(auto/hybrid/manual)를 고쳤으나 실제 버그는 별개(`checklist.py`의 TREND_FOLLOW/MEAN_REVERSION 변수). 양쪽 수정이 모두 코드에 남아 있으나 실제 효과는 checklist.py 수정

### 다음 할 일 (우선순위 순)

- [DONE 2026-05-20] **68차 수정 실세션 확인** — 11:46:31 재시작 후 3항목 모두 정상 확인 완료

---

## 2026-05-20 (67차) — 장중 로그 분석 + 이상점 수정

### 한일 요약

- [DONE 2026-05-20] **online_learner scaler 버그 수정** — `partial_fit()` 첫 샘플만 → 매 샘플마다 호출. 장중 피처 분포 변화 적응 가능
- [DONE 2026-05-20] **SYSTEM 로그 레이블 개선** — `정확도=X%` → `CB③30m=X%(N건)` / 샘플 없으면 `집계중`. `cb3_samples` 파라미터 추가
- [DONE 2026-05-20] **horizon별 [Bias] 편향 진단 로그 추가** — STEP 1 직후 호라이즌별 적중률 + UP편향/FL편향 자동 감지 태그
- [DONE 2026-05-20] **conf 클립 DEBUG 로그 추가** — `[Calib] clipped X.XXX→0.85` DEBUG 로그
- [DONE 2026-05-20] **SYSTEM 정확도=0.0% 원인 규명** — 세션 초반 30분 필터 공백(정상 안전장치) + 30m 실제 정확도 낮음(진실된 수치)

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **67차 수정사항 실세션 확인 (2026-05-21)**
  - SYSTEM 로그: `CB③30m=XX%(N건)` 또는 `집계중` 형식 표시 확인
  - `[Bias]` 로그: 매분 horizon별 적중률·UP편향/FL편향 태그 발생 확인
  - SGD비중: 이전보다 30%→10% 급감이 완화되는지 관찰 (scaler 수정 효과)

- [NEXT 미정] **5m bullish bias / 30m flat bias 근본 보정**
  - `[Bias]` 로그 1주 이상 관찰 후 패턴 확정
  - 5m: UP 예측 비율이 지속적으로 과대하면 calibrator UP threshold 상향
  - 30m: FL 예측 비율이 지속적으로 과대하면 FL threshold 조정 또는 class_weight 재설정

- [NEXT 미정] **6분 주기 처리시간 스파이크 원인 정밀 진단**
  - `[PipePerf]` WARN 로그의 단계별 시간(`S1=Xms S2=Xms ...`) 관찰
  - GBM 재학습이 동기 블로킹인지 확인 — 오발동 시 재학습 제외 로직 검토

---

## 2026-05-20 (66차) — SHAP 중요도·파라미터 상관계수 이상점 4종 수정

### 한일 요약

- [DONE 2026-05-20] **Fix 1: RESTORED값 LIVE 오인 버그** — `shap_tracker.update()` bool 반환 + `_refresh_shap_state()` 임계값 30→`SHAP_MIN_DATA_POINTS`(100) + 반환값으로 `_live_shap_ready` 제어
- [DONE 2026-05-20] **Fix 2: 구버전 `_update_shap_dashboard()` 중복 제거** — 데드코드 + 인코딩 깨진 문자열 포함 블록 전체 삭제
- [DONE 2026-05-20] **Fix 3: `_shap_feature_window` 재시작 복원** — `_restore_analysis_buffers()`에서 DB raw_features로 window 채움. 재시작 직후 30분 공백 제거
- [DONE 2026-05-20] **Fix 4: `short_names` 인코딩 교체** — `_build_param_corr_string()` 딕셔너리 키 깨진 바이트→정상 UTF-8 한글 6종

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **66차 수정사항 실세션 확인 (2026-05-21)**
  - 기동 직후 `[AnalysisRestore]` 로그: `live_shap=N`이 100 이상이면 window 복원 성공
  - `[SHAP] 중요도 갱신 완료` 로그: 분봉 100개 이상 확보 후 첫 발생인지 확인
  - 대시보드 SHAP 상태: 기동 직후 100건 미만이면 RESTORED, 100건 이상이면 LIVE 표시
  - 파라미터 상관계수 레이블: "CVD", "VWAP", "외인콜", "다이버전스", "프로그램" 정상 표시

- [NEXT 미정] **SHAP LIVE/RESTORED 대시보드 색상 구분 추가 검토**
  - 현재 텍스트 상태 표시만 있음. 색상(회색=RESTORED, 녹색=LIVE) 추가 여부 결정
  - 데이터 충분히 쌓인 후 판단

---

## 2026-05-20 (65차) — 진입 체크리스트 7종 개선

### 한일 요약

- [DONE 2026-05-20] **신뢰도 강제 X 게이트** — `checklist.py` `2_confidence` 실패 시 즉시 X 반환. conf=46%에서 8/9 A등급 나오던 버그 제거
- [DONE 2026-05-20] **min_conf 단일 출처 통일** — `get_zone_min_confidence()` 추가 + `actual_min_conf = max(레짐, 시간대)`. OPEN_VOLATILE에서 실제 63% 기준 적용
- [DONE 2026-05-20] **VWAP 역추세 예외 분기 활성화** — `checklist.evaluate()`에 `cvd_exhaustion`·`micro_regime` 전달. 사실상 죽어있던 MEAN_REVERSION 분기 복구
- [DONE 2026-05-20] **UI 신뢰도 레이블 동적화** — `_conf_chk_name_label` + `update_data()` 매분 갱신. "신뢰도 ≥ 58%" 하드코딩 제거
- [DONE 2026-05-20] **CVD·OFI 중립(0) 차단** — `>= 0` → `> 0`, `<= 0` → `< 0`. 중립 신호 CORE 통과 허점 제거
- [DONE 2026-05-20] **외인 방향 AND 강화** — `or` → `and`. 콜 약간 양수만으로 통과되던 조건 강화
- [DONE 2026-05-20] **손실률 분모 동적화** — 50_000_000 하드코딩 → `max(_ts_current_sizer_balance(self), 50_000_000)`

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **65차 수정사항 실세션 확인 (2026-05-21)**
  - SIGNAL 로그: `[Checklist] 신뢰도 미달 XX.X% < YY.Y% → 강제 X등급` 로그 발생 확인
  - OPEN_VOLATILE 구간 체크리스트 판정이 63% 기준 적용 확인 (58%가 아닌)
  - UI 진입 관리 탭: 시간대 전환 시 신뢰도 레이블 기준치 변경 확인
  - CVD 중립(0)값 발생 시 `4_cvd` X 처리 DEBUG 로그 확인

- [NEXT 실전 전환 전] **외인 방향 AND 강화 영향도 점검**
  - `6_foreign` 통과율이 이전 대비 얼마나 낮아지는지 1~2주 로그 집계
  - 과도하게 낮아지면(< 20%) foreign_call_net 임계값 완화 또는 가중치 재조정 고려

---

## 2026-05-20 (64차) — 09:34 재시작 점검 + 3종 이상점 수정

### 한일 요약

- [DONE 2026-05-20] **P1: 장중 재시작 WarmupRetrain CB⑤ 수정** — `connect_broker()` 장중 완료 시 즉시 GBM warmup 스레드 시작. 09:35 CB⑤ 5026ms 재발 방지
- [DONE 2026-05-20] **P2: `_gbm_retrain_running` `__init__` 초기화** — `False`로 명시적 초기화. `getattr` 방어 패턴 일관화
- [DONE 2026-05-20] **P3: OptionChain QTimer 분리** — STEP 4 `refresh()` 제거. `_option_chain_timer` QTimer 300s 신규. `_poll_option_chain()` 콜백 추가. 매 5분 3347ms 파이프라인 지연 해소

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **64차 수정사항 실세션 확인 (2026-05-21)**
  - SYSTEM 로그: `08:55:XX [PreRetrain]` + `[System] option chain timer start triggered` 확인
  - 장중 재시작 시: `[WarmupRetrain] 장중 재시작 — GBM 즉시 재학습 시작` 로그 확인 (STEP 3가 아닌 connect_broker 직후)
  - 재시작 후 첫 파이프라인 CB⑤ 없음 (< 5000ms)
  - `[OptionChain] 갱신 X.Xs` 로그가 파이프라인 PipePerf 타임라인 **밖**에서 발생
  - `[PipePerf]` S4 수치 100ms 이하 유지 (BlockRequest 루프 제거 확인)

---

## 2026-05-20 (63차) — 파이프라인 크래시 버그 4종 수정

### 한일 요약

- [DONE 2026-05-20] **log_manager.signal() TypeError 수정** — `level="INFO"` 기본값 추가. 09:14 파이프라인 매분 크래시 해소
- [DONE 2026-05-20] **GBM 재학습 08:55 PreRetrain 분리** — `pre_market_setup()` 끝에 비동기 재학습 트리거. 09:00 CB⑤ 충돌 방지
- [DONE 2026-05-20] **PCRStore 장초반 극단값 방어** — `PCR_MIN_CALL_ABS=1000` skip + `PCR_MAX=4.0` cap. opt_pcr_slope_norm=-5.87 매분 반복 해소
- [DONE 2026-05-20] **quality_investor_age_sec z=+45 방어** — `feature_builder.py` min(..., 300.0) cap. 09:00 첫 파이프라인 z-score 폭발 방지

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **63·64차 수정사항 실세션 확인 (2026-05-21)** — 위 64차 확인 항목으로 통합
  - SIGNAL 로그: `opt_pcr_slope_norm=-5.87` 매분 반복 사라짐 확인
  - 파이프라인: `[복구 실패]` 로그 없음 + 09:14 이후 정상 흐름 확인
  - SIGNAL 로그: IntradayRegime=CRASH 시 `[IntradayRegime] CRASH — 신규 롱 금지` 정상 출력 (TypeError 없음)
  - DEBUG 로그: `quality_investor_age_sec` 09:00 첫 파이프라인 z-score < +15 확인

- [NEXT 실전 전환 전] **잔고 TR 파싱 `rows=0` 버그 수정**
  - `[BrokerSync] 잔고 rows=0` 매분 반복 — 포지션 보유 시 TR 파싱 실패 가능성
  - Cybos CpTd0723 TR 응답 구조 재확인 + 파싱 로직 점검

- [NEXT 실전 전환 전] **프로그램 매매 TR 확인**
  - 현재 사용 중인 TR 미확인 상태. 실전 주문 전 반드시 확인

- [NEXT 미정] **opt_pcr_slope_norm 분포 안정화 확인**
  - 2~3일 실세션 후 SIGNAL 로그에서 opt_pcr_slope_norm 값 분포 점검
  - 여전히 극단값(-1.0, +1.0 고착) 발생 시 PCR_WINDOW(20) 또는 정규화 파라미터 조정

---

## 2026-05-19 (62차) — 매크로 레짐 2계층 강화 + 레짐 대시보드

### 한일 요약

- [DONE 2026-05-19] **macro_fetcher 첫 fetch=0 버그 수정** — `_first_fetch_done` 플래그. 초회 시딩만, 2회차부터 실 변화량 계산
- [DONE 2026-05-19] **IntradayTacticalRegime 신규** — `collection/macro/intraday_tactical_regime.py`. NORMAL/DAY_RISK_OFF/CRASH. 매분 day_ret·ATR·z_warn·contrarian 기반 전환
- [DONE 2026-05-19] **micro_regime ATR 둔감 수정** — ATR_VOLATILE_MULT 2.0→1.5. z_warn≥3 복합 조건 추가. 5/19 급변장 0회 → 개선
- [DONE 2026-05-19] **main.py Layer 2 파이프라인 통합** — import·인스턴스·매분 update·진입차단 2종·block reason 로그·reset_daily
- [DONE 2026-05-19] **RegimePanel 신규** — `dashboard/panels/regime_panel.py`. Layer1/2/Micro 3배지 + 진입정책 GridLayout + 이력 로그
- [DONE 2026-05-19] **"🌐 레짐" 대시보드 탭** — `mid_tabs.addTab`. Layer1/Micro 업데이트 훅 연결

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **62차 수정사항 실세션 확인**
  - "🌐 레짐" 탭: mid_tabs 내 탭 정상 표시, Layer1·Layer2·Micro 배지 색상 갱신 확인
  - Layer 2 전환 로그: 당일 하락 시 `[IntradayRegime] NORMAL → DAY_RISK_OFF` 로그 발생
  - 진입 차단: `[IntradayRegime] DAY_RISK_OFF — 신규 롱 금지` 또는 `CRASH — 신규 숏 금지` 로그
  - micro_regime 급변장: 장중 변동성 확대 구간에서 `[MicroRegime] 혼합 → 급변장` 전환 로그
  - macro_fetcher: 2회차 fetch chg 로그가 0.0이 아닌 실수치 확인

- [NEXT 미정] **IntradayTacticalRegime RECOVERY 조건 캘리브레이션**
  - bounce ≥ 0.5% + OFI 15m avg > 0 + ATR < 1.2 — 3조건 모두 충족 시 NORMAL 복귀
  - 실세션 데이터 2주 이상 후 RECOVERY 발동 빈도 점검 (너무 빠르면 조건 강화)

- [NEXT 미정] **Layer 2 진입정책 size_mult × 안전배수 조합 점검**
  - CRASH(×0.3) × core_health_mult(×0.5) × brier_mult(×0.5) = ×0.075 → 사실상 0계약 여부 확인
  - 너무 보수적이면 CRASH 발동 임계값 조정 검토

---

## 2026-05-19 (61차) — CB HALT 분석 + 대시보드 지표 버그 수정 + CB⑤ 재설계

### 한일 요약

- [DONE 2026-05-19] **예측 로그 direction 추가** — `main.py` 실패 로그에 `예측=DN 실제=UP` 방향 추가
- [DONE 2026-05-19] **정확도=0.0% 버그 수정** — `update_system_status()` `accuracy=_acc30m` 전달 누락 수정
- [DONE 2026-05-19] **API지연=0ms 버그 + CB⑤ 재설계** — `record_pipe_latency()` 신규. 1초 경고·5초 PAUSE. `record_api_latency()` 제거
- [DONE 2026-05-19] **모델 AI 카드 하드코딩 버그 수정** — `_model_vals` 참조 저장 + `update_model_cards()` 신규 + 매분 갱신
- [DONE 2026-05-19] **헬스 카드 "처리시간" 전환** — HealthPanel·LogPanel 양쪽 레이블·툴팁·스파크라인
- [DONE 2026-05-19] **HealthPanel 내부 임계값 정합** — 500→1000ms(경고), 1000→5000ms(임계)
- [DONE 2026-05-19] **CB⑤ 테스트 추가** — `test_circuit_breaker.py` 2케이스

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **61차 수정사항 실세션 확인**
  - SYSTEM 로그: `처리시간=Xms | 정확도=YY.Y%` 형식 확인 (0.0% 아님)
  - 예측 로그: `✗ 15m 예측 실패 (conf=73.9% 예측=DN 실제=UP)` 형식 확인
  - 모델 AI 카드: 매분 정확도·SGD비중·자가학습 실시간 갱신 확인
  - 처리시간 카드: 6 운영 헬스 탭 툴팁 hover 확인
  - CB⑤: 파이프라인 느릴 때 `[CB⑤] 파이프라인 Xms 경고` 로그 발생 여부

- [NEXT 미정] **CB⑤ 5초 PAUSE 실제 발동 케이스 모니터링**
  - GBM 재학습(5~30초) 시 파이프라인 시간 측정 — 혹시 재학습이 동기 블로킹이면 오발동 가능성
  - 오발동 시 GBM 재학습 완료 후 측정 제외 로직 검토

---

## 2026-05-19 (60차) — CB③ 분석 기반 안전장치 6종 + Shadow/Contrarian 구현

### 한일 요약

- [DONE 2026-05-19] **1순위: Mid-Conf Blind Spot Tracker** — `circuit_breaker.py` 60~85% 구간 7연속 오답 → strict 모드 발동. `settings.py` 3개 상수 추가
- [DONE 2026-05-19] **2순위: Brier Score 실시간 추적** — `circuit_breaker.py` 이동평균(10건), >0.35 경고, >0.45 사이즈 50% 패널티. `brier_size_mult` 속성 노출
- [DONE 2026-05-19] **3순위: 재시작 루프 브레이커** — `circuit_breaker.py` `_daily_halt_count` 추적. 2회→50%, 3회→완전관망. `restart_size_mult` / `is_restart_blocked()` 추가
- [DONE 2026-05-19] **4순위: 장 시작 5분 DNA 진단** — `safety/market_dna.py` 신규. 09:00~09:04 첫 5봉 4항목 진단, 3/4 이상 이상 → dna_mult=0.25
- [DONE 2026-05-19] **5순위: CORE Health Score → Sizer 연동** — `features/core_health.py` 신규. streak+z_warn 기반 0~100 점수. `position_sizer.py` 4개 안전 배수 파라미터 추가
- [DONE 2026-05-19] **6순위: Shadow Session 상태 머신** — `safety/shadow_session.py` 신규. acc30m≥40%+CoreHealth≥70+z_warn<2 → LIVE/BLOCKED
- [DONE 2026-05-19] **6순위: Contrarian Mode 상태 머신** — `safety/contrarian_mode.py` 신규. 3조건 WATCHING→ARMED→ACTIVE. 가상 역베팅 PnL 집계
- [DONE 2026-05-19] **6순위: 실험 게이트 대시보드 탭** — `experiment_gate_panel.py` 신규. "🧪 실험 게이트" 탭 추가
- [DONE 2026-05-19] **파이프라인 전체 문서화** — `docs/PIPELINE_FLOW.md` 신규. STEP 1~9 전체 흐름 + 안전 배수 조합 매트릭스

### 다음 할 일 (우선순위 순)

- [NEXT 장중] **60차 안전장치 실세션 첫 확인**
  - MarketDNA: 09:05에 `[DNA] score=N/4 → dna_mult=X` 로그 확인
  - CoreHealth: 매분 `[CoreHealth] score=N → size_mult=X` 로그 확인
  - Mid-Conf 추적: 60~85% 구간 오답 연속 시 `[CB] mid_conf_wrong_streak=N` 로그
  - Brier Score: 10건 누적 후 `brier_score=X.XX` 로그 확인
  - ShadowSession: 09:40 분기점에 `[Shadow] → LIVE` 또는 `BLOCKED` 로그
  - ContrarianMode: acc30m<25% 발생 시 `[Contrarian] ARMED` 상태 전환 확인
  - 실험 게이트 탭: mid_tabs 마지막 탭 정상 표시, 30초 주기 갱신 확인

- [NEXT 미정] **Shadow/Contrarian 가상 PnL 데이터 누적 후 실전 전환 검토**
  - ShadowSession LIVE 전환 후 2주 이상 acc30m ≥ 40% 유지 확인
  - ContrarianMode 가상 역베팅 승률 ≥ 55% 누적 시 실입금 소액 적용 검토

- [NEXT 미정] **CoreHealth 점수 임계값 캘리브레이션**
  - 실세션 데이터 2주 이상 누적 후 core_health_mult 임계값(70/85 기준) 조정 필요 여부 검토
  - 너무 빈번하게 0.5 발동 → 임계값 완화, 너무 드물면 → 강화

---

## 2026-05-19 (59차) — 손익추이 DB 초기화 버튼

### 한일 요약

- [DONE 2026-05-19] **DB초기화 버튼 UI 추가** — `MireukDashboard._rdo_row` 🔓+DB초기화 버튼, 기본 비활성, 잠금해제 체크 후 활성
- [DONE 2026-05-19] **`_on_db_reset_clicked()` 핸들러** — 확인 다이얼로그, 타임스탬프 백업, 3테이블 DELETE+VACUUM, 패널 즉시 갱신
- [DONE 2026-05-19] **패널 참조 경로 수정** — `_pnl_history_panel` → `log_panel.refresh_pnl_history([])`

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **59차 DB초기화 버튼 실세션 확인**
  - 🔓 체크 → "DB초기화" 버튼 빨간 활성 전환 확인
  - 클릭 → 확인 다이얼로그 Cancel 기본값 확인
  - OK 후: `trades_backup_YYYYMMDD_HHMMSS.db` 파일 생성 + 손익추이 탭 빈 상태 전환 확인
  - 초기화 후 🔓 자동 해제 + 버튼 비활성 복원 확인

- [NEXT 2026-05-19] **5/19 이후 오염없는 DB로 데이터 수집 유효성 평가**
  - 신규 체결 → trades 행 기록 확인
  - 일마감 → daily_stats / daily_broker_pnl 정상 집계 확인
  - 손익추이 탭 일별/주별/월별 숫자 HTS 대조

---

## 2026-05-18 (58차) — 안전장치 6종 구현

### 한일 요약

- [DONE 2026-05-18] **P0: PG+CB to_state_dict / from_state_dict** — `circuit_breaker.py`, `profit_guard.py`
- [DONE 2026-05-18] **P0: session_recovery_service — PG+CB 상태 복원** — `restore_daily_state()` 내 복원 블록 추가
- [DONE 2026-05-18] **P0: main.py — _write_session_state PG/CB 직렬화** — `_load_state_persist_flag()` + 저장 로직
- [DONE 2026-05-18] **P0: 상태유지 체크박스** — `chk_state_persist` QCheckBox, `_rdo_row` 우측 배치, ui_prefs 연동
- [DONE 2026-05-18] **P1-a: Restart Armistice** — 90초 + broker_sync ≥2 clean 전까지 진입 차단
- [DONE 2026-05-18] **P1-b: Position Integrity Checksum** — `_ts_check_position_integrity()` 신규, Slack 경보, 진입 차단
- [DONE 2026-05-18] **P2-b: trades.db 셋업 태그 5컬럼 마이그레이션** — `_migrate_trades_db()` 확장
- [DONE 2026-05-18] **P2-b: 진입 컨텍스트 저장 + _record_trade_result 5컬럼 INSERT 확장**
- [DONE 2026-05-18] **P2-b: setup_expectancy_panel.py 신규 생성** — 4섹션, 시간 필터, 1분 갱신
- [DONE 2026-05-18] **P2-b: mid_tabs "📊 셋업 기대값" 탭 추가**
- [DONE 2026-05-18] **P3-a: OnlineLearner 오염 학습 보호** — stuck 분봉 SGD 스킵
- [DONE 2026-05-18] **P3-b: Reverse Entry Clamp** — 청산 후 180초 반대 방향 차단

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **58차 안전장치 실세션 1차 확인**
  - Armistice: 기동 후 90초 내 신호 → `[Armistice] 재시작 유예 중` 로그, 90초 후 정상 진입
  - Integrity: FLAT 상태 진입 전 `[Integrity] OK` 또는 mismatch 감지 로그
  - ReverseClamp: 청산 직후 반대 방향 시도 시 `[ReverseClamp] 진입 차단` 로그
  - 상태유지: 재시작 후 `[Restore] ProfitGuard 상태 복원` + `[CB] 상태 복원` 로그
  - 셋업 기대값 탭: 탭 정상 표시, 거래 후 데이터 반영 여부 확인
  - SGD stuck 가드: stuck 발생 시 `[SGD] stuck 발생 분봉 — N건 학습 스킵` 로그

- [NEXT 미정] **셋업 기대값 패널 — 데이터 누적 후 인사이트 점검**
  - 2주 이상 거래 누적 후 meta_action / hurst_bucket별 승률 유의미한지 확인
  - 유의미한 패턴 발견 시 진입 필터 조건에 반영 검토

---

## 2026-05-18 (57차) — UI 체크박스 설정 유지 버그 수정

### 한일 요약

- [DONE 2026-05-18] **B120 Fix: 체크박스 재시작 시 True 초기화** — `_restore_ui_prefs` 내 `_on_symbol_changed` → `_update_symbol_label` 교체 (dashboard/main_dashboard.py L7814)
- [DONE 2026-05-18] **chk_slack 중복 시그널 제거** — `main.py` L4128~4130 `stateChanged` → `_save_ui_prefs` 연결 제거

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **57차 Fix 실세션 확인**
  - 중패널_Auto·우패널_Auto 해제 후 재시작 → 해제 상태 복원 확인
  - `ui_prefs.json`의 `mid_auto_enabled`, `right_auto_enabled` 값 유지 확인

---

## 2026-05-18 (56차) — 상단 배지 5종 점검·수정

### 한일 요약

- [DONE 2026-05-18] **B116 Fix: FLAT 배지 고정** — `update_position()`에 `lbl_pos` setText+setStyleSheet 추가
- [DONE 2026-05-18] **B117 Fix: 위클리 배지 목요일 전용** — `_calc_cycle_badge()` 월/목 양방향 + `[월]`/`[목]` 접두 형식
- [DONE 2026-05-18] **B118 Fix: 감마스퀴즈 배지 고정** — `_update_gamma_badge()` 신규, GEX 기반 판정, 초기값 "감마 —"
- [DONE 2026-05-18] **B119 Fix: usd_krw 인수 누락** — `update_supply_macro()` 호출에 `usd_krw` 추가
- [DONE 2026-05-18] **NEUTRAL 툴팁 오류 수정** — "매분 갱신" → "08:55 장전 1회 수집, 당일 고정"
- [DONE 2026-05-18] **L2 dead code 제거** — `_tier.check()` `if max_qty == 0:` 분기 제거
- [DONE 2026-05-18] **L2 툴팁 개선** — Tier 4 400만원 기준·상태값 명시

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **56차 배지 실세션 확인**
  - FLAT→LONG 진입 시 `lbl_pos` 배지 색상 전환 (녹색) 확인
  - 오늘 월요일(만기일) → `● [월]위클리 만기일` 배지 표시 확인
  - 09:05 이후 감마스퀴즈 배지: "감마 —" → GEX 수신 후 갱신 확인
  - 시스템 로그 `[Regime] ... | USD/KRW=±X.XX` (실수치) 확인

---

## 2026-05-18 (55차) — 옵션 체인 스냅샷 파이프라인 + B115 수정

### 한일 요약

- [DONE 2026-05-18] **OptionChainSnapshot 클래스 신규** — `collection/options/option_chain_snapshot.py`, 5분 폴링, PCR/ATM OI/GEX 7개 피처 반환
- [DONE 2026-05-18] **main.py STEP 4 통합** — import·init·connect_broker·STEP4·reset_daily 5곳 수정, _chain_refreshed 시에만 dashboard 업데이트
- [DONE 2026-05-18] **대시보드 옵션 섹션 추가** — DivergencePanel 하단 freshness progress bar + PCR/ATM PCR/GEX/ATM 콜 OI/ATM 풋 OI 카드 5개 + MainDashboard 위임 메서드
- [DONE 2026-05-18] **B115 Fix: _filter_front_month 만기 미처리** — KOSPI200 2번째 목요일 만기 계산 (`_option_expiry`), 만기 달 skip → 현물월(6월) 자동 선택

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **옵션 체인 실세션 첫 검증**
  - 시작 로그: `[OptionChain] COM 초기화 완료` (connect_broker 직후)
  - `[OptionChain] front month=2606 (만기=2026-06-11)` 로그 확인 (B115 수정 동작)
  - 09:05 이후: `[OptionChain] 갱신 X.Xs | PCR=N.NNN ATM_PCR=N.NNN GEX=N.NNB avail=True`
  - 대시보드 "다이버전스 + 포지션" 탭 하단 실수치 (PCR≠1.000, GEX≠0.0B)

---

## 2026-05-18 (54차) — B112/B114 개선

### 한일 요약

- [DONE 2026-05-18] **B112 Fix: stale broker_sync_reason 클리어** — `_ts_on_chejan_event`에서 청산 완전 체결 후 FLAT이면 `_broker_sync_last_error = "flat after exit"` (main.py L4806)
- [DONE 2026-05-18] **B114 진단: IntrabarTPSchedule 로그 추가** — `_clear_pending_order`에서 QTimer 스케줄 시 price/pos/p1/p2/p3 WARN 출력, price=0 시 취소 로그 (main.py L930)
- [DONE 2026-05-18] **B114 진단: IntrabarTPCheck 가드 로그 추가** — pending 존재·FLAT·price=0 각 케이스별 WARN 출력 (main.py L4029)

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **54차 Fix 실세션 확인**
  - B112: 청산 후 EntryAttempt `broker_sync_reason='flat after exit'` 확인
  - B114: `[IntrabarTPSchedule]` 로그 출력 확인 (TP1 체결 완료 직후)
  - B114: `[IntrabarTPCheck]` 로그 또는 skip 원인 로그 확인 → 근본 원인 파악 후 수정

---

## 2026-05-18 (53차) — 2차 목표 미청산 버그 2종 수정

### 한일 요약

- [DONE 2026-05-18] **대시보드 TP 오표시 수정** — `pending_stage` 기반 주문중 TP 행 강조 + 상위 TP "대기" 교체 (main_dashboard.py)
- [DONE 2026-05-18] **intra-bar TP 재점검 로직 추가** — `_clear_pending_order`에서 EXIT_PARTIAL 해소 시 300ms 후 TP 즉시 재점검 스케줄 (main.py)
- [DONE 2026-05-18] **`_ts_intrabar_tp_check` 신규 함수** — TP1→TP2→TP3 순차 점검, 각 단계 후 pending 재확인 (main.py)

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **53차 Fix 실세션 확인**
  - TP1 주문중(pending_stage=1) 상태에서 대시보드 TP2·TP3 행이 "대기"로 표시되는지 확인

---

## 2026-05-18 (52차) — 손익 패널 불일치 수정

### 한일 요약

- [DONE 2026-05-18] **B109 Fix: broker_daily_pnl 오염 차단** — `FLAT` 시에만 `upsert_daily_broker_pnl` 저장 (main.py L5111)
- [DONE 2026-05-18] **손익 추이 탭 즉시 갱신** — 저장 직후 `_refresh_pnl_history()` 호출 추가 (main.py L5113)
- [DONE 2026-05-18] **4개 패널 데이터 소스 분석** — 각 소스·불일치 원인 규명

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **52차 Fix 실세션 확인**
  - 거래 청산 직후 손익 추이 P/L 원 = PnL 탭 일일누적과 동일한지 확인
  - 포지션 보유 중 잔고 TR 호출 후 손익 추이 값이 변하지 않는지 확인
  - FLAT 후 잔고 TR 수신 시 손익 추이 자동 갱신되는지 확인

- [NEXT 2026-05-19] **실시간 잔고 vs HTS 129,750원 차이 추가 조사** (낮은 우선순위)
  - CpTd6197 header 인덱스 매핑이 Cybos 실제 반환 구조와 일치하는지 SYSTEM.log에서 재검증
  - `[CybosDailyPnlHeaders]` 로그에서 raw_headers dict 내용 확인

---

## 2026-05-18 (51차) — 부분청산 Race Condition 버그 3종 수정

### 한일 요약

- [DONE 2026-05-18] **B106 Fix: `_ts_execute_partial_exit()` Race Condition** — pending 선등록→주문→실패 롤백으로 수정 (main.py)
- [DONE 2026-05-18] **B107 Fix: `apply_entry_fill()` partial_done 리셋** — 신규 진입 시에만 리셋, 증량 시 보존 (position_tracker.py)
- [DONE 2026-05-18] **B108 Fix: Chejan order_no="" 오탐 매칭** — direction 교차 검증 추가 (main.py)
- [DONE 2026-05-18] **실로그 검증** — 10:00 TP1(+5.43pt) / 10:01 TP2(+8.69pt) 정상 확인

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **51차 Fix 지속 모니터링**
  - TP1/TP2/TP3 부분청산 흐름에서 `[PendingOrder] set`이 `[ChejanFlow] 접수` 보다 선행 기록되는지 확인
  - B107(증량 중 partial_done 보존) 실제 발동 케이스 발생 시 로그 확인
  - B108(direction 검증 차단) 발동 케이스: WARN 로그에서 `pending_matched=False` + 방향 불일치 메시지 확인

---

## 2026-05-17 (50차) — 5/15 거래 검토 기반 전략 핵심 수정 후속

### 한일 요약

- [DONE 2026-05-17] **CVD/VWAP/OFI 하드게이트** — checklist.py, CORE 3개 ✗ → Grade X 강제
- [DONE 2026-05-17] **EXIT 부분체결 즉시 긴급청산** — main.py, stuck 10초+반대 포지션 force_exit
- [DONE 2026-05-17] **MIN_TRAIN_BARS 3000 한시적 하향** — batch_retrainer.py
- [DONE 2026-05-17] **Hurst 실계산 연결** — feature_builder.py, 60봉 버퍼 + calculate_hurst 호출
- [DONE 2026-05-17] **CB② 2회 강화** — settings.py, CB_CONSEC_STOP_LIMIT 3→2
- [DONE 2026-05-17] **SizerMatch 로그 추가** — main.py, Sizer vs 실제 진입 gap

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **50차 수정사항 5/19 기동 실검증**
  - Hurst 실값 확인: 09:40 이후 로그에서 `hurst=0.5xx` (0.5 아닌 값) 확인
  - GBM 재학습 성공 확인: `[Retrain] 완료 | N초 | 성공=M/6 호라이즌` 로그
  - CVD 하드게이트 동작: `[Checklist] CORE 피처 ✗ [...] → 강제 X등급` 로그 발생 시 확인
  - CB② 과잉 발동 여부: 정상 트레이드 2회 손절 후 CB 발동 여부 모니터링
  - [SizerMatch] 로그: Sizer 제안 vs 실제 진입 gap 원인 파악

- [NEXT 2026-05-19] **CB② 2회 기준 2주 모니터링**
  - 오판 발동(수익 트레이드 중 2회 손절로 시스템 정지)이 주 2회 이상 발생 시
  - → CB_CONSEC_STOP_LIMIT 재검토 (2→3 복원 또는 쿨다운 연장 방안)

- [NEXT 2026-05-26] **MIN_TRAIN_BARS 5000 복원**
  - `raw_data.db` 5,000행 달성 예상일 (하루 ~260행 기준)
  - `learning/batch_retrainer.py` MIN_TRAIN_BARS = 3000 → 5000 원복

- [NEXT 향후] **micro-LOFI toxicity 진입 필터 구현** (5/15 거래 검토 개선안 4번)
  - `toxicity_score_ma > 0.5`일 때만 진입 허용, 또는 SHORT 진입 시 `mlofi_norm < 0` 조건 추가
  - 데이터 수집 중 (feature_builder에 이미 toxicity_score, mlofi_norm 포함)
  - 5/15 09:49 사례: tox_ma=0.1015, mlofi_norm=+0.021 (SHORT에 불리) — 필터 있었으면 차단

---

## 2026-05-16 (43차) — 손익 추이 패널 UI 개선 후속

### 한일 요약

- [DONE 2026-05-16] **소스 선택 체크박스** — 탭바 우측 코너, 순방향/역방향, 둘 다 체크 시 합산
- [DONE 2026-05-16] **헤더 `(실행/순)` 제거** — 일별·주별·월별 3개 헤더 배열 정리
- [DONE 2026-05-16] **셀 이중 표시 제거** — `_fmt_val` / `_fmt_single` 기반 단일 값
- [DONE 2026-05-16] **MDD·샤프·누적 체크박스 연동** — `_mdd_sel`, `_sharpe_sel` 신규
- [DONE 2026-05-16] **요약 카드 연동** — 총 손익·최대 MDD 선택 소스 기준 표시

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **43차 UI 실 검증**
  - 손익 추이 탭 진입 후 체크박스 표시 확인 (탭바 우측 코너)
  - "순방향" 단독 체크: P/L pt·원·누적 모두 exec 값만 표시
  - "역방향" 단독 체크: forward 값만 표시
  - 둘 다 체크: exec+forward 합산 표시
  - 체크박스 변경 시 테이블·요약 카드 즉시 갱신 확인

---

## 2026-05-16 (42차) — Cybos 잔고 Chejan 버그 수정 4종 후속

### 한일 요약

- [DONE 2026-05-16] **버그 근본 원인 분석** — 잔고 Chejan → EXIT pending 파괴 → 외부체결 → MANUAL 포지션 → CB② 발동 체인 해명
- [DONE 2026-05-16] **Fix 1: EXIT pending 보호** — main.py `_ts_sync_from_balance_payload`
- [DONE 2026-05-16] **Fix 2: TP 플래그 보존** — position_tracker.py `sync_from_broker` 동방향 조건
- [DONE 2026-05-16] **Fix 3: grade 보존** — position_tracker.py `sync_from_broker` 동방향 조건
- [DONE 2026-05-16] **Fix 4: EmergencyExit pending 선등록** — emergency_exit.py + main.py
- [DONE 2026-05-16] **복원 로그 가격 포맷 수정** — session_recovery_service.py `:.2f` 3곳

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **42차 Fix 1~4 모의투자 실검증**
  - 진입 후 잔고 Chejan 처리 로그 확인:
    - `[BrokerSync] 잔고 Chejan — EXIT pending 진행 중, pending 유지` 메시지 (Fix 1)
    - grade가 BROKER로 덮어써지지 않고 원래 등급(A/B/C) 유지 (Fix 3)
    - TP1 체결 후 `외부체결(HTS/수동)` 미발생 (Fix 1·2 통합)
  - CB④(ATR 3배) 또는 CB②(손절 3연속) 발동 시:
    - 슬랙 알림 수신 후 `[EmergencyExit] pending 등록` 로그 확인 (Fix 4)
    - 비상청산 체결이 `외부체결` 아닌 `비상청산` 사유로 기록되는지 확인
  - 복원 로그: `@ 1239.36` 형식 (소수점 2자리) 표시 확인

- [NEXT 2026-05-19] **Fix 1 엣지케이스 검증**
  - 잔고 Chejan이 `EXIT_PARTIAL` pending 도중 2회 이상 연속 도착하는 경우
  - pending `order_no` 없는 상태에서 잔고 Chejan 도착 시 pending 유지 여부

---

## 2026-05-16 (41차) — CB③ + HORIZON_THRESHOLDS 재보정 후속

### 한일 요약

- [DONE 2026-05-16] **HORIZON_THRESHOLDS 재보정** — 1200pt 기준 전체 약 1.6× 상향, config/settings.py 단일 수정 → 3파일 자동 전파
- [DONE 2026-05-16] **`_log_threshold_monitor()` 신설** — GBM 재학습 완료 시 + 30분 주기 로그 (static/ATR 비교, 안정화 감지)
- [DONE 2026-05-16] **`_CB_TIP` 슬랙 알림 섹션 추가** — 5개 트리거 슬랙 대응표 + 다크박스 예시
- [DONE 2026-05-16] **`param_title` 피처 윈도우 툴팁** — CORE 3종(청록)/선택 피처(황색)/외부 수집(회색) 테이블
- [DONE 2026-05-16] **`_HZ_TIP` 신규 + `hz_title` 연결** — 멀티 호라이즌 예측 6섹션 툴팁
- [DONE 2026-05-16] **CB③ 근본 원인 분석** — warn_count 구조적 취약 + threshold 너무 낮음 확인

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **GBM 재학습 적용 확인 (다음 기동 시)**
  - 다음날 08:45 기동 → warmup retrain 자동 발동 확인
  - 재학습 완료 후 `_log_threshold_monitor()` 로그 수신 확인
  - "모델 AI" 탭: `[THRESH] stable_count=N/6 ✅` 또는 `⚠ ATR전환권장` 로그 확인

- [NEXT 2026-05-19] **FLAT 비율 실 데이터 검증**
  - GBM 재학습 후 첫 장(2026-05-19)에서 30분 호라이즌 예측 중 FLAT 비율 확인
  - 목표: 29~37% (이전 추정 24% 미만 개선 여부)
  - `prediction_buffer.py` `verify_and_update` 로그에서 FLAT/UP/DOWN 분포 확인

- [NEXT 향후] **ATR 동적 방식 전환 검토**
  - 정적 재보정 후 CB③ 미발동 1~2주 확인 후 전환 검토
  - `threshold = max(base, atr/price × mult)` 방식
  - 핵심 주의: `batch_retrainer.py`·`prediction_buffer.py` 양쪽 동시 적용 필수 (학습-검증 threshold 일관성)
  - ATR period=14 이미 `feature_builder.py`에 구현됨 → `_last_features["atr"]` 재사용

---

## 2026-05-16 (40차) — 장전 시동 흐름 점검 + 슬랙 알림 후속

### 한일 요약

- [DONE 2026-05-16] **08:55 단일 블록 통합** — 기존 08:45+08:55 이중 블록 → 단일 08:55 블록
- [DONE 2026-05-16] **스냅샷 선워밍** — `pre_market_setup()` 끝에 `_prime_from_snapshot()`, `start()` skip 로직
- [DONE 2026-05-16] **GBM 재학습 데몬 스레드** — 메인 스레드 블로킹 제거
- [DONE 2026-05-16] **08:58 broker sync 선실행** — GAP_OPEN 구간 대비
- [DONE 2026-05-16] **`start_mireuk.bat` 세션 이중 확인** — preflight → 3s → 재확인
- [DONE 2026-05-16] **슬랙 단계별 알림 추가** — 6개 함수 + `_SLACK_ENABLED` 플래그
- [DONE 2026-05-16] **대시보드 `chk_slack` 체크박스** — `res_box` 왼쪽 정렬, `ui_prefs.json` 연동
- [DONE 2026-05-16] **CLAUDE.md 08:55 교정**

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-19] **40차 수정 사항 실검증 (다음 기동 시)**
  - 슬랙 수신 확인 순서:
    1. `notify_startup` — 기동 완료 슬랙 (연결 직후)
    2. `notify_premarket_ready` — 08:55 장전 준비 완료 슬랙
    3. `notify_first_tick` — 09:01 전후 첫 분봉 수신 슬랙
  - 실패 시 확인:
    - broker sync 미검증 → `notify_broker_sync_blocked` 수신 여부
    - 90s 파이프라인 미실행 → `notify_pipeline_delayed` 수신 여부
  - UI 확인: 대시보드 오른쪽 상단 `chk_slack` 체크박스 표시, 체크 해제 시 슬랙 발송 중단 확인
  - GBM 재학습 중 메인 스레드 블로킹 없는지 확인 (09:00 첫 틱 수신 지연 없음)

- [NEXT 2026-05-19] **39차 수정 사항 실검증 (롤오버 없는 날)**
  - `[CodeRoll]` 로그 없음 확인 (불필요한 교체 없음)
  - `[NormalProbe] 근월물 확정`, `[MiniProbe] 근월물 확정` 로그 확인
  - `[BrokerSync] verified=True`, `[CybosRT-TICK] #1` 로그 순서 확인
  - 콤보 UI가 프로브 결과 코드로 업데이트됐는지 육안 확인

- [NEXT 2026-06-12] **롤오버 당일 시나리오 점검**
  - 만기일: 2026-06-11 (2차 목요일)
  - 다음 기동(2026-06-12)에서 `[CodeRoll]` 로그 및 콤보 변경 확인

---

## 2026-05-15 (39차) — 선물 롤오버 자동화 전면 강화 후속

### 한일 요약

- [DONE 2026-05-15] **`_MARKET_SYMBOLS` 동적 생성 (`_build_market_symbols`)**
  - 하드코딩 제거, 기동 날짜 기준 자동 계산
  - 분기물(3·6·9·12월) / 월물 만기일(2차 목요일) 정확 계산

- [DONE 2026-05-15] **`set_selected_symbol()` 신설**
  - 브로커 프로브 결과로 콤보 즉시 동기화
  - 콤보에 없는 코드는 동적 삽입

- [DONE 2026-05-15] **`get_nearest_normal_futures_code()` 신설**
  - 일반선물(A01xxx) FutureMst 프로브 — 미니선물과 동일 방식

- [DONE 2026-05-15] **`_resolve_trade_code()` 일반선물 프로브 통합**
  - 일반선물도 만기 감지 + 근월물 자동 전환 + `[CodeRoll]` 경고

- [DONE 2026-05-15] **`check_rollover()` 장중 감시 + `_scheduler_tick()` 주기 호출**
  - 60 tick(30분)마다 근월물 재확인
  - 감지 시 WARNING + UI 갱신. 재구독은 재기동에 위임

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-16] **38·39차 수정 사항 다음 기동 실검증**
  - 확인 로그 순서:
    1. `[NormalProbe] 근월물 확정 code=A01...` — 일반선물 프로브 성공
    2. `[MiniProbe] 근월물 확정 code=A05...` — 미니선물 프로브 성공
    3. `[BrokerSync] verified=True block_new_entries=False` — brker sync 성공
    4. `[CybosRT-TICK] #1 code=A05...` — 틱 수신 시작
  - 롤오버 없는 날에는 `[CodeRoll]` 로그 없음 확인 (불필요한 교체 없음)
  - 콤보 UI가 프로브 결과 코드로 자동 업데이트됐는지 육안 확인

- [NEXT 2026-05-16] **롤오버 당일 시나리오 점검** (만기일 다음날 첫 기동 시)
  - 만기일: 매월 2차 목요일 (다음은 2026-06-11)
  - 기동 후 `[CodeRoll]` 로그 및 콤보 변경 확인 가능 날짜: 2026-06-12

---

## 2026-05-15 (37차) — 운영 헬스 중앙 패널 추가 후속

### 한일 요약

- [DONE 2026-05-15] **운영 헬스 중앙 패널 추가**
  - `dashboard/main_dashboard.py`의 `mid_tabs`에 `⚕️ 운영 헬스` 탭 삽입
  - 중앙 패널에서도 API 지연 / 피처 품질 / 캐시 나이 / 예외 밀도 확인 가능

- [DONE 2026-05-15] **런타임 헬스 동기화**
  - `update_runtime_health()`가 로그 패널과 중앙 헬스 패널을 동시에 갱신

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **중앙 헬스 탭 실제 렌더링 확인**
  - 탭 순서상 `⚕️ 운영 헬스`가 알파 리서치 봇 앞에 잘 보이는지 확인
  - 4개 메트릭 박스와 3라인 스파크라인이 해상도별로 잘리는지 점검

- [NEXT 2026-05-15] **Health Score 실제 산식 연결**
  - 현재 중앙 헬스 패널의 `Health Score`는 임시값이므로 런타임 계산값으로 교체
  - 지연/품질/예외 밀도 기반 종합 점수를 하나의 함수로 산정할지 결정

- [NEXT 2026-05-16] **기존 로그 패널과 중앙 패널 정보 중복정책 점검**
  - 로그 패널은 텔레메트리, 중앙 패널은 운영 요약으로 유지할지 재확인
  - 중복이 과하면 로그는 축약하고 중앙은 요약 유지하는 방향 검토

## 2026-05-15 (36차) — Cybos 자동 로그인 버그 수정 후 마감

### 한일 요약

- [DONE 2026-05-15] **모의투자 선택 창 탐지 버그 수정** — `_find_mock_dialog_hwnd()` 4차 탐색(EnumChildWindows + GetParent) 추가
- [DONE 2026-05-15] **min_wait 중 즉시 감지/클릭** — 매초 탐지로 대기 시간 단축
- [DONE 2026-05-15] **공지사항 팝업 처리 신설** — `_dismiss_notice_popups(timeout=10)` 모의투자 접속 직후 호출
- [DONE 2026-05-15] **로그인 흐름 문서화** — `docs/CYBOS_AUTOLOGIN_FLOW.md`

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-16] **4차 탐색 실 동작 확인**
  - 다음 자동 로그인 실행 시 콘솔에서 탐지 단계 확인
  - `[INFO] 4차 탐지: 자식 창에서 '모의투자 접속' 버튼 발견` 로그가 나오면 원인 확정
  - `[INFO] min_wait 중 모의투자 선택 창 감지:` 로그가 나오면 이상적

- [NEXT 2026-05-16] **공지사항 팝업 제목 패턴 확인**
  - 실제 팝업 제목이 "공지사항" 외 다른 값이면 `NOTICE_KEYWORDS` 상수에 추가

- [NEXT 2026-05-16] **로그인 완료 후 미륵이 정상 기동 확인**
  - `autologin()` 반환 후 `main.py` 이어받기 동작 확인

---

## 2026-05-15 (35차) — Day10-2/Day11 반영 후 마감

### 한일 요약

- [DONE 2026-05-15] **Degraded auto/manual 차단 정책 분리 구현**
  - `HEALTH_DEGRADED_BLOCK_AUTO_ENTRY`, `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` 반영
  - 수동 진입/자동 진입 각각 독립 차단 동작 연결

- [DONE 2026-05-15] **헬스 설정 핫리로드 구현**
  - `settings.py` mtime 감시 + `importlib.reload`로 무중단 반영
  - SYSTEM 로그에 핫리로드 반영 메시지 출력

- [DONE 2026-05-15] **헬스 탭 스파크라인 확장**
  - Health Score 단일 라인에서 지연/품질 2개 라인 추가(총 3라인)

- [DONE 2026-05-15] **핫리로드/차단 검증 하네스 실행 PASS**
  - `scripts/validate_health_policy_hotreload.py`
  - hotreload log 1회, auto/manual 차단 분리 확인, 45틱 시뮬레이션 통과

- [DONE 2026-05-15] **감사문서 ##10 하루 운용 체크리스트/사전점검 결과 반영**
  - 사전점검(07:38) 근거 로그 + 설정 스냅샷 + 운영 전 주의사항 기록

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **브로커 startup sync 정상화 재확인**
  - `verified=True`, `block_new_entries=False` 전환 시점 로그 확인
  - 전환 실패 시 balance TR timeout 원인(권한/계좌/장상태) 분리

- [NEXT 2026-05-15] **헬스 탭 수동 UI 체크 완료 처리**
  - 운영자가 대시보드 6 탭 진입/표시 정상 여부 확인 후 ##10 10.1 항목 체크

- [NEXT 2026-05-15] **장중 30~60분 실관찰로 ##10.2~10.5 체크 채우기**
  - HEALTH 상태 로그 주기성
  - Degraded enter/exit 전이
  - 자동/수동 차단 로그 실제 발생

- [NEXT 2026-05-15] **핫리로드 실운영 재검증(재시작 금지)**
  - 장중 `HEALTH_DEGRADED_BLOCK_MANUAL_ENTRY` 토글 후 5~10초 반영 로그 확인

- [NEXT 2026-05-16] **하루 운용 종료판정(10.6) 확정 및 5줄 요약 기록**
  - 필수 8개 이상 체크 + 치명 오류 0건 여부 최종 판정

## 2026-05-14 (34차) — 진입관리 탭 시간대 가이드 UI 강화 후속

### 한일 요약

- [DONE 2026-05-14] **진입관리 설명줄 실시간 시간대 가이드화** — zone/range/conf/size/entry 상태 실시간 표시
- [DONE 2026-05-14] **시간대 칩 UI 추가** — `GAP_OPEN`~`EXIT_ONLY` 6구간 버튼 칩 및 현재 구간 강조
- [DONE 2026-05-14] **A/B/C 등급 버튼 권장 표시 연동** — 현재 zone `size_mult` 기준 최근접 등급 추천, `권장`/`선택` 동시 표기
- [DONE 2026-05-14] **만기일/FOMC 오버라이드 배지 표시** — UI 설명줄에 적용중 배지 노출

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **진입관리 탭 PyQt 실제 렌더링 확인**
  - zone 칩 6개가 해상도별로 줄바꿈/잘림 없이 보이는지 확인
  - `권장`/`선택` 동시 표시가 과밀하지 않은지 확인

- [NEXT 2026-05-15] **권장 등급 매핑 규칙 장중 관찰**
  - `size_mult=0.8`이 B 권장으로 보이는 것이 운영 체감과 맞는지 확인
  - 필요 시 최근접 매핑 대신 명시 임계값 규칙으로 변경 검토

- [NEXT 2026-05-15] **오버라이드 배지 툴팁 추가 여부 결정**
  - `만기일 적용중` / `FOMC 적용중` 배지에 `conf 상향`, `size 축소` 수치를 툴팁으로 노출할지 판단

- [NEXT 2026-05-15] **UI 표시 경로와 실진입 경로 일치성 점검**
  - 현재 UI는 `TimeStrategyRouter` override 결과를 표시하지만, 실제 main.py STEP 6/7의 진입 파라미터에도 동일 체인이 연결되는지 재확인

## 2026-05-14 (33차) — Cybos 장외 startup crash 완화 후속

### 처리 요약

- [DONE 2026-05-14] **MacroFeatureTransformer / feature_builder 실제 반영 검증**
  - `feature_builder.build()`에 `option_data`, `macro_data` 머지 경로 존재 확인 (`features/feature_builder.py:274-279`)
- [DONE 2026-05-14] **장외 Cybos 실시간 구독 1차 차단**
  - `main.py`에서 장외에는 `RealtimeData.start()`와 수급 `QTimer`를 시작하지 않도록 가드 추가
- [DONE 2026-05-14] **MacroFetcher yfinance rate-limit 노이즈 완화**
  - `collection/macro/macro_fetcher.py`에 stdout/stderr 억제, `threads=False`, 15분 cooldown, fallback key 정렬 반영

### 다음 할 일 (우선순위 순)

- [DONE 2026-05-15] **`CpTd0723` / `FutureMst` 30초 timeout 근본 원인 분리 + 수정**
  - 원인 확정: 백그라운드 스레드에서 BlockRequest 실행 + 메인 스레드 done.wait() 완전 차단 → 메시지 펌프 없음 → 데드락
  - 수정: `_run_block_request`에 `done.wait(0.01)` + `PumpWaitingMessages()` 루프 적용 (`api_connector.py`)

- [DONE 2026-05-15] **미니선물 만기 롤오버 미처리 → 틱 0건 수정**
  - 원인 확정: UI에 저장된 A0565(2026-05-14 만기)를 검증 없이 그대로 구독
  - 수정: `_resolve_trade_code` 항상 근월물 프로브, `get_nearest_mini_futures_code`에 `price>0` 조건 skip 추가

- [NEXT 2026-05-15] **38차 수정 사항 다음 기동 실검증**
  - `[MiniProbe] 근월물 확정 code=A0566` 로그 확인 (만기 skip → 6월물 확정)
  - `[CodeRoll] UI=A0565 → 근월물=A0566` 롤오버 경고 로그 확인
  - `[BrokerSync] status verified=True block_new_entries=False` 확인 (타임아웃 없이 sync 완료)
  - `[CybosRT-START] snapshot end code=A0566 price=XXX.XX` 가격 정상 수신 확인
  - `[CybosRT-TICK] #1 code=A0566` 분봉 데이터 수신 확인

- [NEXT 2026-05-15] **장외 launcher 재실행으로 access violation 재현 여부 확인**
  - 기대 로그: `[DBG CK-5] RealtimeData.start() skipped (market closed)`
  - 실패 기준: `-1073741819` 재발생 또는 Qt loop 진입 직후 비정상 종료

- [NEXT 2026-05-15] **`QTableWidget` stylesheet parse warning 잔존 여부 확인**
  - 같은 경고가 계속 나면 balance table 외 다른 `QTableWidget` stylesheet 후보를 순차 비활성화해 원인 테이블 특정

- [NEXT 2026-05-15] **`apply_expiry_override()` / `apply_fomc_override()` main.py 실진입 경로 연결**
  - UI 표시 경로는 연결 완료. `TimeStrategyRouter`의 만기일/FOMC override가 실제 진입 파라미터에 적용되는지 확인

---

## 2026-05-14 (32차) — 2차 감사 P3 4종 수정

### 한일 요약

- [DONE 2026-05-14] **M5: Dynamic Sizing 0 수렴 차단** — `MIN_COMBINED_FRACTION=0.12`. 7팩터 곱 임계값 미만 시 _blocked() 반환.
- [DONE 2026-05-14] **M6: GAP_OPEN(09:00~09:05) 구간 신설** — `settings.py` · `time_utils.py` · `time_strategy_router.py` 동시 반영. min_conf=0.67, size=0.5, allow_entry=True.
- [DONE 2026-05-14] **M7: StandardScaler 노후화 감지** — fit 타임스탬프 기록, 90분 초과 WARNING, |z|>4 극단 피처 경고.
- [DONE 2026-05-14] **만기일/FOMC 대응** — `utils/time_utils.py` 월물 만기일·FOMC 함수 신설. `TimeStrategyRouter.apply_expiry_override()` / `apply_fomc_override()` 추가.

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **apply_expiry_override / apply_fomc_override — main.py 호출 연결**
  - STEP 6 또는 STEP 7에서 `TimeStrategyRouter`가 만기일/FOMC 오버라이드를 실제로 호출하는지 확인
  - 현재 대시보드 UI 표시 경로에는 연결 완료, 실진입 경로 누락 여부만 점검하면 됨

- [NEXT 2026-05-15] **MIN_COMBINED_FRACTION 임계값 장중 관찰**
  - 0.12 기준으로 B등급 횡보장 신호가 너무 많이 차단되는지 확인
  - 로그 `[DynSize] fraction=... < 0.12 → 사이즈 과소 차단` 발생 빈도 체크
  - 과차단 시 0.08~0.10 범위로 하향 조정 검토

- [NEXT 2026-05-15] **GAP_OPEN 구간 장중 실사용 검증**
  - 09:00~09:05 분봉에서 TimeRouter가 `zone=GAP_OPEN` 로그 출력하는지 확인
  - `min_confidence=0.67` 기준이 적절한지 관찰 (너무 빡빡하면 0.65로 완화)

- [NEXT 2026-05-15] **FOMC 날짜 목록 정확성 확인**
  - `utils/time_utils.py`의 `_FOMC_DATES_KST` 2026·2027년 날짜를 공식 Fed 캘린더와 대조
  - URL: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

---

## 2026-05-14 (30차) — 감사 + 버그 수정 + 스텁 구현

### 한일 요약

- [DONE 2026-05-14] **P0: FLAT→AUTO SHORT 잠재 버그** — `checklist.py` FLAT 조기 반환 추가
- [DONE 2026-05-14] **P1: feature_builder 예외처리** — 9개 계산 블록 try/except + safe bar.get()
- [DONE 2026-05-14] **P1: OFI stale state** — `flush_minute()` 말미 `_prev_*=None` 리셋
- [DONE 2026-05-14] **P1: ATR 버퍼 중앙값 평활** — circuit_breaker 지속 급등 감지 추가
- [DONE 2026-05-14] **P2: 더미 매크로 → 실 API 연동** — `MacroFetcher.get_features()` + ×100 단위 변환
- [DONE 2026-05-14] **P2: InvestorData api 미주입** — `kiwoom_broker.py` 수정
- [DONE 2026-05-14] **P2: 인코딩 깨짐 4개소** — `position_tracker.py` 정정
- [DONE 2026-05-14] **P3: EntryManager Dead Code** — `entry_manager.py` 삭제
- [DONE 2026-05-14] **P3: `_send_kiwoom_*` rename** — `_send_broker_*` (13개소)
- [DONE 2026-05-14] **P3: CVD 보합 틱 바이어스** — delta=0 (중립) 처리
- [DONE 2026-05-14] **MacroFeatureTransformer 구현** — `features/macro/macro_feature_transformer.py`
- [DONE 2026-05-14] **DailyConsolidator 구현** — `learning/self_learning/daily_consolidator.py`
- [DONE 2026-05-14] **DriftAdjuster 구현** — `learning/self_learning/drift_adjuster.py`
- [DONE 2026-05-14] **PCRStore 구현** — `collection/options/pcr_store.py`
- [DONE 2026-05-14] **OptionFeatureCalculator 구현** — `features/options/option_features.py`
- [DONE 2026-05-14] **main.py 연결** — STEP 4 피처 파이프라인 + STEP 1 record + daily_close() 갱신
- [DONE 2026-05-14] **ROADMAP.md 보류 기록** — research_bot/code_generators/ 선행조건·이유 명시

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **MacroFeatureTransformer → feature_builder 실제 반영 검증**
  - `feature_builder.build()` 내에서 `macro_data` / `option_data` 키워드가 실제로 수신·처리되는지 확인
  - `features.get("macro_vix")` 등 피처가 ML 입력 벡터에 포함되는지 확인

- [NEXT 2026-05-15] **DailyConsolidator 시간대(zone) 코드 확인**
  - `get_time_zone()` 반환값과 `DailyConsolidator.record(zone=...)` 호환 확인
  - zone="OPENING"/"LUNCH"/"CLOSING" 등 실제 상수 확인 (`utils/time_utils.py`)

- [NEXT 2026-05-15] **OnlineLearner.set_alpha() 인터페이스 존재 여부 확인**
  - `learning/online_learner.py`에 `set_alpha(alpha)` 미구현 시 추가 필요

- [NEXT 2026-05-15] **CB HALT 시나리오 장중 검증**
  - CB③ 발동 조건(30분 정확도 < 35% 2회 연속) 시뮬레이션
  - emergency_exit 콜백 → 포지션 즉시 청산 확인
  - CB HALT 중 수동 청산 버튼 동작 확인

- [NEXT 2026-05-15] **세션 재시작 후 GBM 재학습 로그 확인**
  - 재시작 후 첫 분봉 STEP 3에서 `[WarmupRetrain]` 로그 확인

- [NEXT 2026-05-15] **profit_guard_prefs.json 중복 임계값 정리** — [500000] 2개 중복 제거. 의도 재확인.

---

## 2026-05-14 (29차) — CB HALT 사후 조사 + 모델 신뢰도 개선

### 한일 요약

- [DONE 2026-05-14] **B84: EXIT pending stuck 체잔 이벤트 유실 대응** — `_ts_resolve_stuck_exit_pending`에 `expected_remaining` 비교 추가. Chejan 유실로 filled=3/4 고착 시 자동 소멸.
- [DONE 2026-05-14] **B85: CB HALT 후 포지션 미청산 수정** — `circuit_breaker._trigger_halt()`에 `emergency_exit` 콜백 호출 추가. CB②/③도 즉시 청산.
- [DONE 2026-05-14] **B86: CB HALT 중 수동 청산 불가 수정** — pending 체크 시 CB HALT면 강제 소멸 후 청산 진행 분기 추가.
- [DONE 2026-05-14] **C09: GBM conf 극단값 클리핑** — `CONF_CLIP = 0.92`. 초과분 나머지 두 클래스 균등 분배. conf=1.000 과신 방지.
- [DONE 2026-05-14] **C10: CB③ 동적 임계값** — conf ≥ 0.85 오류 5연속 시 임계값 0.35→0.50 자동 상향. `record_accuracy(confidence=)` 전달 경로 연결.
- [DONE 2026-05-14] **C11: 세션 재시작 GBM 즉시 재학습** — `_warmup_retrain_pending` 플래그. `connect_broker()` 후 set → STEP 3에서 `force=True` 재학습. 재학습 완료까지 진입 차단 유지.

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-15] **CB HALT 시나리오 장중 검증**
  - CB③ 발동 조건(30분 정확도 < 35% 2회 연속) 시뮬레이션
  - emergency_exit 콜백 → 포지션 즉시 청산 확인
  - CB HALT 중 수동 청산 버튼 동작 확인

- [NEXT 2026-05-15] **세션 재시작 후 GBM 재학습 로그 확인**
  - 재시작 후 첫 분봉 STEP 3에서 `[WarmupRetrain]` 로그 확인
  - 재학습 완료 후 `_broker_sync_block_new_entries=False` 전환 시점과 `_warmup_retrain_pending=False` 시점 확인

- [NEXT 2026-05-15] **profit_guard_prefs.json 중복 임계값 정리** — [500000] 2개 중복 제거. 의도 재확인.

---

## 2026-05-14 (28차) — L2 배지 + 모드 필터

### 한일 요약

- [DONE 2026-05-14] **L2 영구중단 배지 시각화** — `strategy/profit_guard.py`에 `get_l2_halt_info()` 메서드, `dashboard/main_dashboard.py`에 `lbl_l2_halt` 배지 + `update_l2_halt_badge()` 메서드 추가. CB 배지 오른쪽에 🔒 L2 중단 (N.NM원) 배지 표시.
- [DONE 2026-05-14] **모드 필터 2순위 구현** — `main.py` STEP 7에 모드필터 로직 추가. L2 통과 후 모드별 등급 필터링 (Auto=A급, Hybrid=A,B급, Manual=A,B,C급). 모드필터 차단 시 로그 기록.
- [DONE 2026-05-14] **진입 로직 우선순위 재정의** — L2(시스템 수익 보존) → 모드필터(사용자 신호 강도) 순서 확정. 각 단계 차단 사유 명확화.
- [DONE 2026-05-14] **Auto ON/OFF 배지 검증** — 완벽하게 구현/작동 중 (신호 연결, 상태 관리, 진입 로직 제어, 로그 기록 모두 ✅).

### 다음 할 일 (우선순위 순)

- [NEXT 2026-05-14] **profit_guard_prefs.json 정리**
  - 중복 임계값 [500000] 제거 (현재 [500000, 0.6, null] / [500000, 1.5, 0] 두 개)
  - 의도 검토: 50만원에서 영구중단할 것인가, 아니면 200만원까지 거래할 것인가 → 사용자 확인 후 설정

- [NEXT 2026-05-14] **모드 필터 장중 검증 (1~2시간)**
  - 시나리오 A: 50만원 상태에서 C급+B모드 신호 → 진입 차단 확인
  - 시나리오 B: 50만원 상태에서 C급+C모드 신호 → 진입 성공 확인
  - 시나리오 C: 100만원 상태에서 B급+B모드 신호 → L2 차단 확인

- [NEXT 2026-05-14] **L2 halt 배지 실시간 검증**
  - 200만원 도달 시 배지 즉시 표시 (🔒 L2 중단)
  - 일일 리셋(reset_daily) 시 배지 사라지는지 확인

- [NEXT 2026-05-15] **OptionMo 실시간 OI 검증 (4단계)** — 장중(09:00~15:30)에만 유효
  ```powershell
  python scripts/probe_cp_option_mo.py --ensure-login --code B0166A89 --watch-sec 15
  ```
  OI 실시간 갱신 Subscribe 동작 확인.

- [NEXT 2026-05-15] **지표를 Mireuk 피처로 통합**
  - `collection/options/`에 `option_chain_snapshot.py` 신설 — 정기 폴링 기반 수집
  - `features/options/`에 `option_features.py` 신설 — PCR·GEX·ATM OI 피처화
  - `feature_builder.py`에 옵션 피처 연결
  - STEP 4 피처 생성 단계에 옵션 지표 주입

- [NEXT 2026-05-15] **장중 PCR/GEX 시계열 검증**
  - 09:00~15:30 1분 간격 수집으로 시계열 안정성 확인
  - OI 잠정/확정 구분에 따른 노이즈 평가

- [NEXT 2026-05-15] **OptionMst 폴링 성능 최적화** — ATM ±30pt(48종목) = 2.9초. 매분 파이프라인(60초)에 적합. 배치 비동기 또는 5분 주기 완화 검토.

- [NEXT 2026-05-15] **외부 키움 리포지토리 구현: pywinauto autologin 스크립트 도입**
  - 대상: `auto_trader_kiwoom/start_kiwoom.bat`, `auto_trader_kiwoom/kiwoom_autologin.py`(신규)
  - 요구: 로그인 창 객체 탐색, foreground 보장, 컨트롤 직접 입력, 실패 시 명확한 exit code

- [NEXT 2026-05-15] **작업스케줄러 순서 독립 검증 (2방향 5회 반복)**
  - 시나리오 A: `start_mireuk.bat` 후 `start_kiwoom.bat`
  - 시나리오 B: `start_kiwoom.bat` 후 `start_mireuk.bat`
  - 기준: 10회 중 로그인 실패 0회, 재시도 없이 정상 진입

---

## 2026-05-14 (27차) — Cybos 옵션 지표 수집 (PCR/GEX/ATM OI) 구현

### 한일 요약

- [DONE 2026-05-14] **CpOptionCode 검증** — `scripts/probe_cp_option_code.py` 작성, 체인 4,624종목 수집 확인. `data/option_chain.json` 캐시 생성. 코드 형식=`B0166A89`(콜)/`C0166A89`(풋), `call_put`="콜"/"풋"(한글).
- [DONE 2026-05-14] **CpCalcOptGreeks 검증** — `scripts/probe_cp_calc_opt_greeks.py` 작성. `SetInputValue`/`BlockRequest` 아님 → **속성 할당 + `Calculate()`** 방식 확정. Delta/Gamma/Theta/Vega/Rho/IV 계산 정상.
- [DONE 2026-05-14] **OptionMst 필드맵 교차 검증** — `scripts/verify_option_mst_fieldmap.py` 작성. 10종목 × 2회 검증으로 HeaderValue 인덱스 확정.
- [DONE 2026-05-14] **통합 지표 수집** — `scripts/collect_option_metrics.py` 작성. PCR(OI)=0.54, ATM PCR=1.04, Total GEX=+35.3B. 48종목 2.9초.
- [DONE 2026-05-14] **AGENTS.md** — 한글판 작성 (실행 환경, 런처, 브로커 백엔드, 절대 원칙, 아키텍처, 세션 연속성)

### OptionMst 확정 필드맵

| HV | 의미 | 비고 |
|---|---|---|
| 6 | 행사가(strike) | 검증 완료 |
| 13 | 잔존일수 | ✅ |
| 15 | 콜/풋 구분코드 (51=콜, 50=풋) | ATM 구분 아님 |
| 37 | 전일 미결제약정 | ✅ |
| 93 | 현재가 | ✅ |
| 97 | 누적체결수량 | ✅ |
| 99 | 현재 미결제약정 | ✅ |
| 100 | OI 구분 | 미검증 |
| 108 | 내재변동성 (종목별) | 유력 |
| 109 | Delta (백분율, ÷100) | ✅ |
| 110 | Gamma (백분율, ÷100) | ✅ |
| 111 | Theta | ✅ |
| 113 | Rho | ✅ |
| 114 | 이론가 (추정) | 유력 |
| 115 | 변동성 (고정 참조값) | 모든 종목 동일 |

### 폐기된 문서 주장

- HV(17) ≠ 기초자산가 → 날짜값. spot은 외부 주입 필요.
- HV(15) ≠ ATM 구분 → 콜/풋 구분코드.

### 다음 할 일 (우선순위 순)

- [DONE 2026-05-18] **CpSysDib.CpSvrNew7222 프로브** — `niis.stk.7222` (주식 계열) 확인, 옵션 무관 → 폐기
- [DONE 2026-05-18] **CpSysDib.CpSvrNew7224 프로브** — `niis.stk.7224` (주식 계열) 확인, 옵션 무관 → 폐기
- [DONE 2026-05-18] **정수 ID 랜덤 탐색 공식 종료** — 7215A/B·7221·7222·7224 전부 주식 계열. Cybos COM에서 옵션 체인 OI 공개 경로 없음 확정. `CYBOS_OPTION_PROBE_2026-05-13.md` 종료 기록 완료.

- [DONE 2026-05-18] **OptionMst 폴링 OI 수집 경로 검증**
  - `dib_status=0`, `0027 조회 완료(option.mst)` — 정상 작동 확인
  - `oi_current=97`, `oi_prev=93` — 실제 OI 데이터 정상 반환, 전일 대비 변화 확인
  - `Dscbo1.OptionMo` Subscribe는 `DispatchWithEvents` metaclass conflict로 사용 불가 → 폴링 방식 확정
  - 장중 OI 변화 실시간 추적: 다음 영업일 09:00~15:30 재실행으로 변화량 확인

- [NEXT 2026-05-19] **장중 OI 변화 실시간 확인** (선택, 낮은 우선순위)
  ```powershell
  python probe_cp_option_mo.py --ensure-login --code B0166A89 --watch-sec 120 --interval 5
  ```
  - 폴링 중 OI 값이 바뀌는지 확인 → 폴링 기반 PCR/GEX 수집 완전 검증

- [DONE 2026-05-18] **지표를 Mireuk 피처로 통합**
  - `collection/options/option_chain_snapshot.py` 신설 — 5분 간격 OptionMst 폴링 클래스
  - `main.py` 3곳 수정: import + `self.option_chain_snap` 인스턴스 + STEP 4 refresh/merge + reset_daily
  - 추가된 피처 7개: `opt_chain_pcr`, `opt_atm_pcr`, `opt_atm_call_oi`, `opt_atm_put_oi`, `opt_gex_bn`, `opt_gex_sign`, `opt_chain_available`
  - `feature_builder.build(option_data=...)` 파이프에 자동 주입 (기존 6개 PCR 피처와 병합)

- [NEXT 2026-05-19] **옵션 체인 통합 실세션 검증**
  - `[OptionChain] COM 초기화 완료` 로그 확인 (connect_broker 완료 직후)
  - 09:05 이후 `[OptionChain] 갱신 N.Xs | PCR=x.xxx ATM_PCR=x.xxx GEX=x.xxB` 로그 확인
  - feature_builder 로그에서 `opt_chain_pcr`, `opt_gex_bn` 피처가 0이 아닌 값으로 주입되는지 확인
  - `opt_chain_available=1.0` 확인 (0.0이면 수집 실패)

- [NEXT 2026-05-14] **장중 PCR/GEX 시계열 검증**
  - 09:00~15:30 1분 간격 수집으로 시계열 안정성 확인
  - OI 잠정/확정 구분에 따른 노이즈 평가

- [NEXT 2026-05-14] **OptionMst 폴링 성능 최적화** — ATM ±30pt(48종목) = 2.9초. 매분 파이프라인(60초)에 적합. 배치 비동기 또는 5분 주기 완화 검토.

### 작성된 스크립트

| 스크립트 | 용도 |
|---|---|
| `scripts/probe_cp_option_code.py` | CpOptionCode 체인 조회 |
| `scripts/probe_cp_calc_opt_greeks.py` | CpCalcOptGreeks 그릭스 계산 |
| `scripts/probe_cp_option_mo.py` | OptionMo 실시간 OI 구독 |
| `scripts/verify_option_mst_fieldmap.py` | OptionMst 필드맵 교차 검증 |
| `scripts/collect_option_metrics.py` | PCR/GEX/ATM OI 통합 수집 |

---


- [DONE 2026-05-13] **키움/미륵이 실행순서 충돌 원인분석 및 개선안 문서화 (B83)**
  - `mireuk -> kiwoom` 실패 / `kiwoom -> mireuk` 성공 패턴을 Z-order/보안모듈/클립보드 경합 관점으로 정리
  - 절대좌표/SendKeys/클립보드 의존 제거, 창 객체 기반 자동화 전환안 확정

- [NEXT 2026-05-14] **외부 키움 리포지토리 구현: pywinauto autologin 스크립트 도입**
  - 대상: `auto_trader_kiwoom/start_kiwoom.bat`, `auto_trader_kiwoom/kiwoom_autologin.py`(신규)
  - 요구: 로그인 창 객체 탐색, foreground 보장, 컨트롤 직접 입력, 실패 시 명확한 exit code

- [NEXT 2026-05-14] **작업스케줄러 순서 독립 검증 (2방향 5회 반복)**
  - 시나리오 A: `start_mireuk.bat` 후 `start_kiwoom.bat`
  - 시나리오 B: `start_kiwoom.bat` 후 `start_mireuk.bat`
  - 기준: 10회 중 로그인 실패 0회, 재시도 없이 정상 진입

- [NEXT 2026-05-14] **비밀정보 주입 방식 전환 확인**
  - 자격정보 하드코딩 금지, 환경변수/보안저장소 기반으로 입력되는지 점검

---

## 2026-05-13 (22차) — 수정 후 검증 항목

- [DONE 2026-05-13] **B75~B78 통합 검증** — 장중 미니선물 분할체결 시나리오
  - 진입 주문(3계약 이상) → Chejan 콜백 순서 확인: 접수 → 체결1 → 체결2
  - `pending["filled_qty"]` 단계적 증가 → `filled_qty >= qty` 시 pending 소멸 확인
  - 포지션 수량이 주문 수량과 일치하는지 확인 (낙관적 오픈 VWAP 보정 포함)
  - EXIT 분할체결: CB/Kelly 기록 횟수 = 1회 (로그 확인)

- [DONE 2026-05-13] **즉시청산 UI 일치 검증**
  - 즉시청산 버튼 클릭 → Cybos HTS 0계약 && UI 실시간 잔고 0계약 동시 확인
  - 잔고 패널 갱신 지연 없이 즉시 반영되는지 확인 (2초 이내)
  - `is_final_fill` 폴백 로그: `status=""` 상황 시 `[Chejan] 상태= 주문번호=...` 로 확인

- [ ] **Cybos Chejan `status` 필드 실측**
  - 장중 실주문 후 `[Chejan] 상태=?` 로그에서 `status` 값이 "접수"/"체결"인지 ""인지 확인
  - ""인 경우 `GetHeaderValue(44)/(15)` 인덱스 오류로 실측 수정 필요

---

## 2026-05-13 (23차) — 청산관리 상태표시/탭복귀 개선 후 검증

- [DONE 2026-05-13] **ENTRY pending 목표 배지 `산정중` 적용**
  - 1/2/3차 목표 배지가 ENTRY 체결 진행 중 `감시중/도달` 대신 `산정중` 표시되는지 확인

- [DONE 2026-05-13] **부분청산 후 `주문중` 잔상 제거**
  - Chejan 체결 직후 `주문중 n/m` 진행 및 pending clear 즉시 해제 확인

- [DONE 2026-05-13] **시간청산 카운트다운 표시 연결**
  - `T-mm:ss` / `임박 mm:ss` / `발동` 상태 노출 확인

- [DONE 2026-05-13] **브로커 동기화 직후 탭 모드 정렬**
  - 보유포지션이면 청산관리, FLAT이면 진입관리 탭 즉시 표시 확인

- [NEXT 2026-05-14] **탭 자동복귀 유휴 판정 회귀 테스트**
  - 마우스 이동 없음 + 키보드 포커스 이동만 있는 경우 자동복귀가 과도하게 발동하지 않는지 점검
  - 20초 유휴 후에는 잔고 상태(보유/무보유) 기준 탭으로 정상 복귀하는지 확인

- [NEXT 2026-05-14] **청산 배지 상태-실주문 완전 일치 점검 (샘플 10건)**
  - TP1/TP2/TP3/하드스톱/시간청산 각각에서 배지 상태(`산정중/주문중/완료`)와 TRADE 로그 타임스탬프 일치 여부 확인

---

## 2026-05-13 (24차) — 봉차트 청산 마커 시인성 개선 후 검증

- [DONE 2026-05-13] **청산 배지 단순화(텍스트 중심) 적용**
  - 기존 청산 배지/칩 제거 후 텍스트 가독성 개선 반영

- [DONE 2026-05-13] **청산봉 소형 스탬프(T/S/P) 마커 재도입**
  - 청산 가격 좌표에 시각 앵커를 넣어 봉-라벨 연결성 복원

- [NEXT 2026-05-14] **청산 라벨 밀집 구간 겹침 완화 테스트**
  - 1분 내 다중 청산(부분청산 연속) 시 라벨 중첩/가독성 확인
  - 필요 시 라벨 충돌 회피(수직 스택/알파 페이드) 규칙 추가 검토

- [NEXT 2026-05-14] **`PX` 태그 명명 개선 여부 결정**
  - 사용자 이해도 기준으로 `PX` 유지 vs `PART`/`분청` 대체안 결정

---

## 2026-05-13 (21차) — 수정 후 검증 항목

- [DONE 2026-05-13] B72: `run_minute_pipeline` `candle` → `bar` NameError 수정 → status bar 정상화
- [DONE 2026-05-13] B73: position_state.json에 futures_code 저장/복원 + 재시작 코드 불일치 감지 + 체결 코드 이중 검증
- [DONE 2026-05-13] B74: 봉차트 이종 종목 혼재 — `code` 전환 감지 초기화 + `_trim_to_last_price_group()`

- [NEXT 2026-05-14] **HTS 잔고 수동 처리** (모의투자)
  - A0666 SHORT @ 1922.80 — 수동 청산
  - A0565 LONG @ 1177.3 — 수동 청산

- [NEXT 2026-05-14] **재시작 후 B73 방지책 동작 검증**
  - 미니선물 선택 상태로 재시작 → `[PositionCodeMismatch] CRITICAL` 로그 확인
  - position_state.json에 `"futures_code"` 항목 정상 저장 확인
  - 이후 정상 재시작(코드 일치) 시 CRITICAL 로그 미출력 확인

- [NEXT 2026-05-14] **봉차트 코드 전환 실동작 검증**
  - 재시작 후 A0565 첫 봉 수신 시 기존 캔들 초기화 → 단일 종목 Y축으로 정상 표시 확인
  - `reload_today()` `_trim_to_last_price_group()`: 혼재 DB 상태에서 최신 그룹만 로드 확인

- [NEXT 2026-05-14] **`_ts_on_chejan_event` (Kiwoom 구버전 함수, 3563번)**
  - 현재 미사용(4652번에서 `_cybos_safe` 버전으로 교체됨)이지만 체결 코드 검증 미적용 상태
  - 완전 제거 또는 동일 패치 적용 여부 결정

---

## 2026-05-12 버그 수정 (18차) — 검증 항목

- [DONE 2026-05-12] `scripts/cybos_autologin.py` — `sys.exit(0)` → `return True` (STEP 5 연결 대기 루프 활성화)
- [DONE 2026-05-12] `start_mireuk.bat` — `%ERRORLEVEL%` → `!ERRORLEVEL!` (CMD 지연 확장 버그 수정)
- [DONE 2026-05-12] `dashboard/main_dashboard.py` — 종목코드·시장구분 선택값 `ui_prefs.json` 영속화
- [DONE 2026-05-12] `dashboard/main_dashboard.py` — 시작 직후 기본값이 `ui_prefs.json` 을 덮어쓰던 복원 순서 버그 수정
- [DONE 2026-05-12] `config/constants.py` / `main.py` / `strategy/*` — 일반/미니선물 계약 스펙(`pt_value`, 주문 코드, 손익 계산) 런타임 동기화
- [DONE 2026-05-12] `dashboard/panels/profit_guard_panel.py` — `sqlite3.Row.get()` 크래시 수정 + `_rows_to_dicts()` + try/except 래핑

### 18차 후속 검증

- [V-18-1] 자동 로그인 재시작 후 확인
  - `start_mireuk.bat` 실행 시 `[OK] CybosPlus 연결 성공 (ServerType=1)` + `[INFO] CybosPlus already connected.` (preflight) 순서로 정상 진행되는지 확인
  - `[ERROR] Auto-login failed.` 오류 완전 소멸 확인

- [V-18-2] UI 영속성 확인
  - [DONE 2026-05-12] 인메모리 대시보드 재생성 스니펫으로 저장/복원 동작 확인
  - [NEXT 2026-05-13] 전체 런처 경로(`start_mireuk.bat`)에서 실제 UI 조작 후 재시작 복원 재확인

- [V-18-3] ProfitGuard 적용 버튼 정상 동작 확인
  - 설정 변경 후 Apply 클릭 → 프로그램 종료 없이 챔피언/챌린저 비교 갱신 확인
  - WARN 로그에 `[ProfitGuard] 시뮬레이션 오류` 미출력 확인

- [DONE 2026-05-13] 미니선물 실시간 구독 파이프라인 확립
  - Cybos COM 코드 체계 실증: CpFutureCode(일반선물 A01xxx), CpKFutureCode(코스닥150 A06xxx), 미니선물(A05xxx)은 FutureMst 프로브만 가능
  - 8자리 코드(A0565000) 무음 실패 수정 → 5자리 정규화(A0565)
  - `get_nearest_mini_futures_code()` FutureMst 프로브 방식 구현
  - `check_cybos_realtime.py --mini` 동작 검증 완료 (A0565 틱/호가 수신 확인)

- [NEXT 2026-05-14] 재시작 후 미니선물 end-to-end 운영 검증
  - 확인: 재시작 후 `[DBG CK-3] 근월물 코드=A0565 is_mini=True` 출력
  - 확인: `[Sizer] 미니선물 ... → N계약 (최소=3)` (일반선물 판정 아닌지)
  - 확인: 진입 신호 발생 시 최소 3계약 주문
  - 확인: `A05...` 선택 시 주문 코드, 수급 TR 코드, 평가손익, 청산손익, 일일 손익이 모두 `pt_value=50,000` 기준으로 일치하는지

- [NEXT 2026-05-13] `ui_prefs.json` 롤오버 정책 확정
  - 현재는 저장된 `symbol_code` 가 목록에 없으면 해당 시장 첫 종목으로 fallback
  - 근월/차월 의미 유지 정책이 필요한지 결정

### 19차 구현 완료 / 후속

- [DONE 2026-05-12] `dashboard/panels/profit_guard_panel.py` — 수익보존 탭 Apply 설정값 영속화 (`data/profit_guard_prefs.json` 저장/복원)
- [NEXT 2026-05-13] 수익보존 탭 재시작 복원 실운영 검증
  - 절차: L1/L2/L3/L4 값 변경 → `적용` → 프로그램 완전 종료/재실행
  - 확인: 모든 값이 직전 저장값으로 복원되고 기본값으로 리셋되지 않는지 확인
- [NEXT 2026-05-13] `data/profit_guard_prefs.json` 운영 정책 확정
  - 항목: 저장 파일 Git 추적 제외 여부(.gitignore)와 초기값 재생성 정책

---

## 2026-05-12 수익 보존 가드 (ProfitGuard) — 검증 항목

### 구현 완료 (17차)

- [DONE 2026-05-12] `strategy/profit_guard.py` — 4-Layer ProfitGuard 핵심 로직 + `ProfitGuardConfig` + `simulate()` 정적 메서드
- [DONE 2026-05-12] `dashboard/panels/profit_guard_panel.py` — "💰 수익 보존" 탭 (PnL DNA · 설정 · 챔피언-챌린저 비교 · 승급 제안)
- [DONE 2026-05-12] `main.py` — STEP 7 진입 전 `is_entry_allowed()` 게이트 + `on_trade_close()` + `on_entry()` + `reset_daily()` 연결
- [DONE 2026-05-12] `dashboard/main_dashboard.py` — "💰 수익 보존" 탭 추가 + `set_profit_guard()` / `refresh_profit_guard()` 어댑터

### ProfitGuard 검증 항목 (실 장 중 필요)

- [V-PG1] L1 Trail 발동 장중 확인
  - 발동 조건: peak ≥ 200만 + 현재 PnL ≤ peak × (1-0.35)
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L1-Trail` 로그 + 해당 분 진입 없음

- [V-PG2] L2 등급 게이트 차단 확인
  - 발동 조건: 수익 구간별 최소 size_mult 미달 (예: 200만+ 구간에서 B등급 시도 시 차단)
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L2-TierGate` + grade=X 강제 적용

- [V-PG3] L3 오후 리스크 압축 확인
  - 발동 조건: 13시 이후 + 수익 양수 + 3회 초과 진입 시도
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L3-AfternoonMode` + 이후 오후 진입 없음

- [V-PG4] L4 수익 보존 CB 2연속 손실 확인
  - 발동 조건: 일누적 ≥ 150만 + 연속 2회 손실 청산
  - 확인: SIGNAL.log `[ProfitGuard] 진입 차단: L4-ProfitCB` + 이후 당일 진입 없음

- [V-PG5] 💰 수익 보존 탭 UI 데이터 반영 확인
  - PnL DNA 막대에 금일 누적 PnL 선이 그려지는지
  - 챔피언 vs 챌린저 비교 테이블이 `simulate()` 결과로 갱신되는지
  - 설정 변경(Apply) 후 `config_changed` 신호로 ProfitGuard 파라미터 즉시 반영되는지

---

## 2026-05-12 챔피언-도전자 시스템 + MicroRegimeClassifier 연결

- [DONE 2026-05-12] `MicroRegimeClassifier` → `main.py` 연결 (ADX 실계산, 5-레짐, 탈진 감지)
- [DONE 2026-05-12] RegimeChampGate [§20] 구현 — 챔피언=None 레짐 진입 차단 (`main.py` STEP 6)
- [DONE 2026-05-12] `_MICRO_EN` 탈진 추가 + `strategy_params.py` EXHAUSTION 오버라이드 3종
- [DONE 2026-05-12] `dashboard/main_dashboard.py` `lbl_micro_regime` 헤더 배지 + `update_micro_regime()` 어댑터
- [DONE 2026-05-12] `challenger_panel.py` `_lbl_cur_regime` 상태바 + `update_micro_regime()` 메서드
- [DONE 2026-05-12] `CHALLENGER_SYSTEM_PLAN.md` 전면 재작성 (완료 체크·설계 상세·검증 계획)

### 챔피언-도전자 검증 항목 (실 데이터 필요)

- [V-C1] 탈진 레짐 실발동 확인 (장 중 SIGNAL.log `[MicroRegime] 레짐 변경 → 탈진` 확인)
- [V-C2] RegimeChampGate 차단 동작 확인 (탈진 레짐에서 진입 시도 시 `grade=X·[RegimeChampGate]` 로그 확인)
- [V-C3] Shadow WARNING 발송 확인 (일별 마감 후 경보 탭 WARNING 표시)
- [V-C4] 미시 레짐 헤더 배지 갱신 확인 (헤더 `lbl_micro_regime`가 매분 정확히 갱신되는지)

---

## 2026-05-12 로그 분석 기반 버그 수정

- [DONE 2026-05-12] MetaConf `loss="log_loss"` → `loss="log"` 수정 (`learning/meta_confidence.py`) — sklearn 1.0.2 호환
- [DONE 2026-05-12] `config/secrets.py` 계좌번호 `7034809431` → `333042073` 수정
- [DONE 2026-05-12] ExitCooldown 중복 로그 제거 (`main.py` `_exit_cooldown_applied_this_fill` 플래그)
- [DONE 2026-05-12] CB HALTED 상태 Sizer 억제 (`main.py` `is_entry_allowed()` 게이트)
- [DONE 2026-05-12] TRADE.log 한글 깨짐 3곳 수정 (`strategy/position/position_tracker.py` line 464/487/513)
- [DONE 2026-05-12] `api_connector.py` 잔고 sanity check — liquidation_eval=0 대체 시 WARNING, profit_rate 이상값 경고
- [DONE 2026-05-12] 경고 등급 재분류 1차 — `CybosInvestorRaw 후보 없음` 반복 WARNING → 레이트리밋 INFO (`collection/cybos/api_connector.py`)
- [DONE 2026-05-12] 경고 등급 재분류 1차 — `profit_rate 이상값` 재등급 (`>200%`만 WARNING, 50~200%는 레이트리밋 INFO)
- [DONE 2026-05-12] 경고 등급 재분류 2차 — `BalanceUI/BalanceRefresh` 반복 WARNING → 레이트리밋 INFO (`main.py`)

- [NEXT 2026-05-13] `CybosInvestorRaw 후보 없음` 09:00~10:44 갭 원인 조사
  - 7건 거래가 모두 수급 데이터 없는 구간에서 발생
  - `CpSysDib.CpSvrNew7212`가 장 시작 직후 미응답하는 조건 확인
  - 필요 시 warmup 대기(장 시작 후 N분 수급 신호 차단) 도입 검토

- [NEXT 2026-05-13] 2026-05-12 CB 발동 후 재시작 첫 장에서 MetaConf 정상 학습 확인
  - LEARNING.log에서 `MetaConf 학습 오류` 메시지 완전 소멸 확인
  - MetaConf `model_fitted=True` 및 `confidence_score` 범위 정상 확인

- [NEXT 2026-05-13] WARN/INFO 재분류 후 로그 품질 검증
  - 목표: WARN.log에서 분당 반복성 메시지 비중 50% 이상 감소
  - 확인: 장애성 이벤트(CB, 주문실패, 동기화 실패)가 WARN에서 누락되지 않는지 샘플링 점검

- [NEXT 2026-05-13] 레이트리밋 정책 상수화
  - 현재 산재한 간격값(30/60/120초, 10분)을 `config` 또는 공통 상수로 통합
  - 운영 모드(모의/실전)별 간격 프로파일 분리 검토

---

## 2026-05-11 자동 로그인

- [DONE 2026-05-11] `scripts/cybos_autologin.py` — `ncStarter.exe /prj:cp` 기반 모의투자 자동 로그인 정상 동작 확인
  - 실행파일 `_ncStarter_.exe` → `ncStarter.exe /prj:cp` 변경
  - 팝업 대기 10s → Enter → 3초 후 스크립트 종료 흐름 확정
  - 모의투자 접속 버튼 좌표 `(1416, 645)` 확정

- [DONE 2026-05-12] `start_mireuk.bat` 에서 autologin 스크립트 선행 호출 연결 검증 — `!ERRORLEVEL!` 지연 확장 수정으로 완료

---

## 2026-05-10 Cybos Plus follow-up

### 2026-05-11 log review update

- [DONE 2026-05-11] review latest `start_mireuk_cybos_test.bat` run logs for Cybos startup and realtime evidence
  - confirmed:
    - Cybos account fallback worked: configured `7034809431` -> runtime `333042073`
    - `CpTd0723` mock no-data (`97007`) was interpreted as flat without blocking startup
    - UI boot + Qt event loop entry completed through Cybos path
    - realtime-derived `MICRO` ticks were still being produced after `09:03`
  - caution:
    - `SYSTEM` log still said `FC0 실시간 틱 대기 중`, which is a Kiwoom-specific waiting message and can be misleading on Cybos
    - `MICRO-MINUTE` log kept repeating `ts=2026-05-11 09:03:00`, so Cybos minute-close / handoff behavior still needs explicit validation

### 2026-05-11 리팩토링 완료 선언

미륵이 브로커 백엔드가 **키움 OpenAPI+ → Cybos Plus** 로 전면 리팩토링 완료됐다.
키움 관련 TR/FID 코드는 이제 레거시이며, 신규 작업은 모두 Cybos Plus 기준으로 수행한다.

- [DONE 2026-05-11] 선물 투자자 수급 수집 (`request_investor_futures` / `request_program_investor`) 다중 후보 실구현
- [DONE 2026-05-11] 미결제약정(OI) `FutureCurOnly` 실시간 저장 (`realtime_data._last_oi`)
- [DONE 2026-05-11] `DivergencePanel` 선물 수급 섹션 추가 (외인/개인/기관/차익/비차익/OI 2×3 그리드)

### NEXT after 2026-05-11 review

- [DONE 2026-05-11] fix startup crash caused by `None` formatting in Cybos balance logging
- [DONE 2026-05-11] harden `MetaConf` training input normalization so ragged feature vectors do not reach fit/buffer
- [DONE 2026-05-11] switch sizer balance source from fixed fallback to latest Cybos summary
- [DONE 2026-05-11] route `CpTd6197` validation output into `SYSTEM.log`
- [DONE 2026-05-11] document Cybos daily-pnl source-of-truth rule (`CpTd6197` first, HTS reference-only)
- [DONE 2026-05-11] replace account-panel `포지션 복원` path with `잔고 새로고침` + `F5`
- [DONE 2026-05-11] force dashboard balance rows to clear immediately on final exit to `FLAT`

- [NEXT 2026-05-12] verify final-exit balance UI clears immediately on the next TP2 / full-close case
  - check:
    - `[BalanceUI] force flat rows reason=final_exit:...`
    - `[BalanceRefresh] trigger=ExitFillFlow mode=final retries=250ms,1200ms`
    - subsequent `BalanceUI ... rows=0`

- [NEXT 2026-05-12] confirm no stale cached balance row reappears after post-exit refresh retries
  - goal:
    - ensure `_last_balance_result` and dashboard rendering stay aligned after `FLAT`

- [NEXT 2026-05-12] verify whether Cybos realtime is truly flowing end-to-end or only partially flowing into micro/hoga paths
  - check:
    - `collection/cybos/realtime_data.py` tick callback count during market hours
    - dashboard current price panel changes from Cybos stream
    - whether minute bars are actually closing with advancing timestamps

- [DONE 2026-05-11] verify Cybos realtime receipt outside main UI with `scripts/check_cybos_realtime.py`
  - command:
    - `python scripts/check_cybos_realtime.py --listen-sec 20`
  - result:
    - `IsConnect=1`
    - `TradeInit=0`
    - realtime code `A0166`
    - tick count `71`
    - hoga count `228`
    - script returned `PASS`
  - interpretation:
    - `FutureCurOnly` / `FutureJpBid` broker receipt is confirmed
    - remaining issue scope moves to main runtime integration, minute-close progression, or status/log interpretation

- [NEXT 2026-05-12] replace Kiwoom-specific waiting/status wording in `main.py`
  - current issue:
    - `장중 — FC0 실시간 틱 대기 중` is shown even on Cybos runs
  - goal:
    - broker-aware waiting message so Cybos runs are not diagnosed with the wrong mental model

- [DONE 2026-05-11] make waiting-status wording broker-aware in `main.py`
  - result:
    - Kiwoom: `Kiwoom FC0 실시간 틱 대기 중`
    - Cybos: `Cybos 실시간 분봉 대기 중 (FutureCurOnly/FutureJpBid 수신 시 자동 진행)`

- [DONE 2026-05-11] fix Cybos minute pipeline timestamp repetition bug (MICRO-MINUTE ts=09:03:00)
  - root cause:
    - `run_minute_pipeline()` reset `_last_recovery_ts = ""` at line 871 on every call
    - recovery path (`_try_pipeline_recovery`) set guard → called pipeline → guard erased → could re-fire after 4 min
    - result: same 09:03 bar re-processed every ~4 min indefinitely
  - fix:
    - moved `_last_recovery_ts = ""` reset from `run_minute_pipeline()` to `_on_candle_closed()`
    - now only real bar-close events clear the guard; recovery calls leave it intact

- [NEXT 2026-05-12] run one Cybos-focused realtime probe script outside main UI
  - goal:
    - separate broker realtime receipt from main-loop / dashboard-state interpretation
  - expected:
    - `FutureCurOnly` ticks increase
    - `FutureJpBid` hoga events increase
    - last tick time and price continue advancing during KRX hours

- [DONE 2026-05-11] add `scripts/check_cybos_realtime.py` for Cybos-only realtime verification
  - scope:
    - `FutureCurOnly` tick count
    - `FutureJpBid` hoga count
    - progress prints during listen window
    - PASS/WARN/FAIL exit result for quick operator judgment

- [DONE 2026-05-11] add Cybos `BAR-CLOSE` system log emission
  - goal:
    - make minute close progression observable like Kiwoom path
  - file:
    - `collection/cybos/realtime_data.py`

### DONE today

- [DONE 2026-05-10] implement concrete `collection/cybos/` runtime path for connection, balance, snapshot, realtime, and fill wiring
- [DONE 2026-05-10] add `scripts/check_cybos_session.py` for admin 32-bit Cybos smoke testing
- [DONE 2026-05-10] add `start_mireuk_cybos_test.bat` for safe Cybos-only startup without changing default Kiwoom execution
- [DONE 2026-05-10] correct `FutureMst` field indices after live snapshot validation
- [DONE 2026-05-10] fix Cybos startup account mismatch by auto-switching runtime account to the signed-on broker account when `secrets.py` account is not present in session
- [DONE 2026-05-10] verify `main.py` can boot UI and enter Qt event loop through Cybos backend

### NEXT priority

- [NEXT 2026-05-12] verify live market realtime flow during KRX hours
  - confirm `FutureCurOnly` tick events increase
  - confirm `FutureJpBid` hoga events increase
  - confirm dashboard price panel updates from Cybos stream

- [NEXT 2026-05-12] run one mock futures order through `CpTd6831`
  - expected:
    - order request success
    - `CpFConclusion` event arrives
    - pending order / position / dashboard reflect fill correctly

- [NEXT 2026-05-12] validate Cybos fill payload against active `main.py` order state machine
  - check:
    - `trade_gubun`
    - `order_gubun`
    - `order_status`
    - `position_qty`
    - `closable_qty`

- [DONE 2026-05-11] replace Cybos investor-data placeholder with real Cybos investor/program TR mapping
  - `CpSysDib.CpSvrNew7212` (idx0=1, 1개월 누적): 선물/콜/풋 투자자별 순매수 확정
  - `get_panel_data()` rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias 실제값 연결
  - option_flow_supported 자동 활성화

- [NEXT 2026-05-12] run `_probe_8119_fields.py` during market hours (09:00~15:30)
  - goal: confirm h[0]=차익매수, h[2]=차익순매수, h[3]=비차익매수, h[5]=비차익순매수
  - command: `py37_32\python.exe -X utf8 scripts/_probe_8119_fields.py`
  - if layout differs: update arb_net/nonarb_net index in `request_program_investor()`

- [NEXT 2026-05-12] verify investor-flow pipeline update every minute
  - confirm: "대기" → actual values in divergence panel after first `fetch_all()`
  - check: `[CybosInvestorRaw] futures via CpSysDib.CpSvrNew7212` in SYSTEM.log

- [DONE 2026-05-11] fix dashboard stylesheet parse warnings
  - root cause:
    - `}}` at end of non-f-string in Python = literal two `}` chars, not f-string escape
    - Qt stylesheet parser received `QFrame{...;}}` (extra `}`) → parse warning
  - fixed locations in `dashboard/strategy_dashboard_tab.py`:
    - `_card()` function
    - `_HeaderCard.__init__()`
    - `_StageTable` `QTableWidget` stylesheet (×2 tables)
  - fix: removed extra `}` from the closing of each `QHeaderView::section{...}` and `QFrame{...}` block

- [DONE 2026-05-11] fix Cybos server label / realtime method wording in `main.py`
  - scope:
    - login info log (line ~720)
    - system startup log (line ~2608)
  - fix:
    - broker name checked via `broker.name == "cybos"`
    - Cybos: server label = `"Cybos 실서버"`, rt method = `"FutureCurOnly/Subscribe"`
    - Kiwoom: original `GetServerGubun` path retained

## 2026-05-08 역방향진입 / PnL 분리 / 학습 방화벽 후속

### [DONE 2026-05-08] 당일 자동종료 후 수동 재시작 시 중복 종료 재실행 방지
- **내용**:
  1. `auto_shutdown_done_date == today` 인 상태에서 장마감 이후 재시작하면 `_daily_close_done`까지 복구
  2. `daily_close()` 초입에서 같은 날짜 자동종료 완료 이력을 다시 확인해 재실행 차단
  3. 자동 종료 알림/프로그램 종료가 당일 1회만 실행되도록 이중 방어
- **범위**: `main.py`

### [DONE 2026-05-08] 봉차트 우측 여백/마커 시인성/토글 UX 개선
- **내용**:
  1. 차트 우측에 10봉 크기 여백 추가
  2. LONG/SHORT 진입 마커를 더 큰 배지형 스타일로 개선
  3. `LONG` 라벨은 위쪽, `SL` 라벨칩은 아래쪽으로 고정하고 마커 겹침 회피 로직 추가
  4. 단축키를 다시 누르면 봉차트 윈도우가 닫히는 토글 동작 적용
- **범위**: `dashboard/main_dashboard.py`

### [DONE 2026-05-08] 1계약 TP1 보호전환 선택형 UI + 수동청산 버튼 실주문 연결
- **내용**:
  1. 청산관리 탭에 `TP1 본절보호 / 본절+alpha / ATR 기반 보호이익` 버튼 및 툴팁 추가
  2. 1계약 TP1 도달 시 선택 모드에 따라 보호전환하도록 구현
  3. `33% / 50% / 전량 청산` 버튼을 실제 수동청산 주문으로 연결
  4. 1계약 보유 시 `33%`, `50%` 클릭을 자동 `전량청산`으로 승격
- **범위**: `dashboard/main_dashboard.py`, `main.py`, `strategy/position/position_tracker.py`

### [NEXT 2026-05-09] 수동청산 버튼 체결 검증
- **내용**:
  1. 2계약 이상 보유 상태에서 `33%`, `50%`, `전량 청산` 각각 1회씩 클릭
  2. WARN.log `[ManualExit] 요청 pct=... send_qty=... kind=...` 확인
  3. TRADE.log `[주문요청] 수동 ... 청산 ... 체결대기` 및 체결 후 PnL 갱신 확인
  4. `trades.db`에 부분청산 레코드가 정상 적재되는지 확인

### [NEXT 2026-05-09] 1계약 TP1 보호전환 3모드 장중 검증
- **내용**:
  1. `본절보호`, `본절+alpha`, `ATR 기반 보호이익`을 각각 한 번씩 선택
  2. WARN.log `[ExitConfig] ...`, `[SingleContractTP1] ... mode=...` 확인
  3. TP1 도달 후 stop price가 의도한 값으로 이동하는지 확인
  4. 재시작 후 `session_state.json` 복원값과 UI 선택 상태가 일치하는지 확인

### [NEXT 2026-05-09] 장마감 이후 수동 재시작 재현 검증
- **내용**:
  1. 같은 날짜 장마감 이후 프로그램을 수동 재시작
  2. 자동 종료 안내 문구와 `[System] 자동 종료 실행` 로그가 다시 나오지 않는지 확인
  3. `session_state.json`의 `auto_shutdown_done_date` 유지 여부 확인

### [NEXT 2026-05-09] 봉차트 마커 충돌/토글 UX 실운영 검증
- **내용**:
  1. LONG 진입과 SL 손절 마크가 같은 봉 또는 인접 봉에 찍히는 구간 확인
  2. 위/아래 강제 분리와 충돌 회피가 실제로 충분한지 시각 검증
  3. 봉차트 단축키를 연속 입력해 열기/닫기 토글이 안정적으로 반복되는지 확인

### [DONE 2026-05-08] 역방향진입 자동진입 전용 토글 구현
- **내용**: 진입관리 패널 상단에 `역방향 진입` 토글 추가, 자동진입 판단 방향만 반전
- **범위**: UI 토글, 세션 저장/복원, 주문 직전 방향 반전, 로그 반영

### [DONE 2026-05-08] 진입관리 패널 `원신호 / 실행신호` 동시 표시
- **내용**: 미륵이 원판단과 최종 실행 방향을 함께 표시
- **범위**: 진입관리 카드, 경고 문구, `TRADE/SIGNAL` 로그

### [DONE 2026-05-08] 손익 PnL / 손익 추이에 `실행 / 순방향` 병기
- **내용**: 손익 카드와 일별/주별/월별 손익 추이에 실행 손익과 순방향 손익을 동시에 표시
- **범위**: `dashboard/main_dashboard.py`, `trades` 저장 컬럼, 복원 경로

### [DONE 2026-05-08] 역방향진입이 학습/통계에 섞이지 않도록 방화벽 적용
- **내용**: 등급 통계, 레짐 통계, 추이 통계, daily PF, daily close snapshot을 순방향 기준으로 고정
- **범위**: `utils/db_utils.py`, `main.py`, `strategy/position/position_tracker.py`

### [NEXT 2026-05-09] 역방향진입 ON/OFF UI 실동작 검증
- **내용**:
  1. ON/OFF 클릭 시 진입관리 패널 `원신호 / 실행신호` 변화 확인
  2. `session_state.json` 재시작 복원 확인
  3. `TRADE/SIGNAL` 로그 `역방향진입=ON/OFF` 표기 확인

### [NEXT 2026-05-09] 실청산 1회 기준 `실행 / 순방향` 손익 수치 검증
- **내용**:
  1. 청산 후 손익 PnL 카드 `실행 / 순방향` 값 확인
  2. 손익 추이 탭 일별/주별/월별 누적과 요약 카드 값 확인
  3. `trades.db`의 `forward_*` 컬럼과 UI 값 대조

### [NEXT 2026-05-09] 학습/효과검증 패널 비오염 검증
- **내용**:
  1. 역방향진입 ON 상태 거래가 있어도 `fetch_grade_stats()`, `fetch_regime_stats()`, `fetch_trend_*()`가 순방향 기준으로 유지되는지 확인
  2. effect validation / learning / daily close 리포트가 역방향 실행손익에 끌려가지 않는지 점검

## 즉시 확인 필요 (추가됨 2026-05-08 6차 세션)

### [V52] PnL 수치 절반으로 줄었는지 확인 [DONE 2026-05-08]
- **내용**: B64 수정 후 1pt 수익 = 250,000원 (이전: 500,000원)으로 정확히 절반
- **방법**: TRADE 로그 `PnL=+Xpt (Y원)` 에서 `Y = X × qty × 250,000 - 수수료(왕복~79,500원)` 확인
- **기준**: 1계약 1pt 수익 시 → 250,000 - 79,500 ≈ **170,500원** 표시 (이전: 499,500원)
- **완료 근거**: `normalize_trade_pnl(1152.7, 1, 1.5) -> gross=375,000 / commission=8,645 / net=366,355` 확인. `fetch_today_trades('2026-05-08')` 합계도 정규화 기준 `-1,618,766원`으로 일치.

### [V57] 잔고 패널 실현손익 vs 손익 추이 오늘 값 일치 확인 [다음 재시작 후]
- **내용**: `OPW20006` summary blank 상황에서도 잔고 패널 `실현손익`과 `손익 추이` 오늘 일별 값이 같은지 확인
- **방법**:
  1. 미륵이 재시작
  2. 장중 또는 장후 `OPW20006` blank fallback 유도
  3. 잔고 패널 `실현손익`과 `손익 추이` 오늘 `P/L 원` 비교
- **기준**: 둘 다 `trades.db net_pnl_krw` 합계와 동일. 재시작 직후 `0`으로 잠깐 덮어쓰지 않아야 함

### [V58] 키움 HTS 실현손익 vs 내부 정규화 손익 차이 재대조 [다음 장중]
- **내용**: HTS `실현손익`과 내부 `net_pnl_krw` 합계 차이가 수수료/세금/브로커 기준 차이인지 재확인
- **방법**:
  1. HTS 실시간 잔고 `실현손익` 캡처
  2. `fetch_today_trades(today)` 합계와 비교
  3. WARN.log에서 fallback 대신 브로커 원문 summary가 들어온 시점 대조
- **기준**: 브로커 원문이 내려온 시점의 차이 규모와 방향을 기록. 차이가 지속되면 수수료 모델 또는 브로커 포함 비용 재조정

### [V59] trades.db migration 후 손익 추이 주/월 집계 이상 여부 확인 [다음 실행]
- **내용**: `entry_ts -> exit_ts` 기준 변경 후 주간/월간 누적 PnL이 기대대로 보이는지 확인
- **방법**: 대시보드 `손익 추이` 탭에서 일별/주별/월별 테이블 값과 `SELECT exit_ts, pnl_krw FROM trades` 집계 대조
- **기준**: 당일/주간/월간 누적이 동일한 정규화 손익 기준으로 이어지고, 청산일 기준으로 행이 배치됨

### [V53] CB③ 30m 피드 확인 [장 시작 2시간 후]
- **내용**: STEP 1에서 30m 호라이즌만 `record_accuracy()` 호출되는지, 20샘플 전에 HALT 없는지 확인
- **방법**: WARN.log `[CB③ 경고 1/2]` 또는 `[CB] 당일 시스템 정지 | 30분 정확도` 로그 시각 확인
- **기준**: 09:00 기준 20개 30m 검증은 오전 11:30~12:00경부터 가능. 그 전 HALT 없으면 정상

### [V54] 청산 후 ExitCooldown 차단 확인 [다음 TP/손절 청산 시]
- **내용**: TP청산 후 2분, 손절청산 후 3분 이내 STEP 7 진입 차단 로그 확인
- **방법**: WARN.log `[ExitCooldown] TP1 후 2분 재진입 금지 until HH:MM:SS` → 해당 시간 이전 `[진입]` 로그 없음 확인
- **기준**: 차단 이유 로그 `[차단] 청산 후 쿨다운 — N초 후 재진입 가능` 출력

### [V55] Hurst 차단 로그 확인 [장 중]
- **내용**: Hurst < 0.45 구간에서 `[차단] Hurst X.XXX < 0.45 — 횡보 레짐 진입 차단` 로그 확인
- **방법**: WARN.log 또는 SIGNAL 로그 grep
- **기준**: Hurst 값 로그에 표시 + 해당 분 진입 없음 확인

### [V56] ATR 차단 확인 [ATR 낮은 구간]
- **내용**: ATR < 1.0pt 구간에서 `[차단] ATR X.XXpt < 1.0pt — 변동성 부족` 로그 확인
- **참고**: 오늘(20260508) ATR=1.37pt였으므로 1.0pt 미만 구간은 더 약한 시장 — 차단 기대

---

## 즉시 확인 필요 (추가됨 2026-05-07 5차 세션)

### [DONE 2026-05-07] STRATEGY_PARAMS_GUIDE.md §1~§20 전체 준수 점검
- 93% 구현 확인. 실제 미구현 2건(strategy_events, shadow_ev) 이번 세션에서 구현 완료.
- VolatilityTargeter / DynamicSizer: 가이드 지시에 따라 "shadow test 후 적용" 의도적 보류 — 정상.

### [V49] shadow_candidate.json IPC 흐름 end-to-end 확인 [다음 장외 최적화 실행 후]
- **내용**: `param_optimizer.propose_for_shadow()` 실행 → `data/shadow_candidate.json` 생성 → 다음날 `daily_close()` → `_load_shadow_candidate()` → `ShadowEvaluator` 인스턴스화 로그 확인
- **방법**:
  1. CLI에서 `python backtest/param_optimizer.py --shadow` 실행
  2. `data/shadow_candidate.json` 파일 존재 확인 (candidate_version, candidate_params, wfa_sharpe 포함)
  3. 다음 일일 마감 후 WARN.log `[ShadowMode] ShadowEvaluator 초기화 완료` 확인
- **기준**: JSON 파일 생성 + 마감 로그에 shadow 초기화 출력

### [V50] strategy_events 테이블 기록 확인 [다음 버전 등록 또는 shadow 시작 시]
- **내용**: `strategy_registry.db`의 `strategy_events` 테이블에 `VERSION_REGISTERED`, `SHADOW_START`, `HOTSWAP_APPROVED/DENIED` 이벤트가 기록되는지 확인
- **방법**: `SELECT * FROM strategy_events ORDER BY id DESC LIMIT 10`
- **기준**: `event_type`, `event_at`, `message` 컬럼이 채워진 행 존재

### [V51] 전략 대시보드 이벤트 로그 표시 확인 [다음 실행]
- **내용**: `strategy_dashboard_tab.py` `_StrategyLog` 패널이 `strategy_events` 기반으로 갱신되는지
- **방법**: 대시보드 → 전략 탭 → 로그 패널에 한국어 이벤트 표시 확인
- **기준**: `버전 등록 | v1.0 | 2026-05-07 ...` 형태로 표시 (fallback: 버전 목록)

---

## 즉시 확인 필요 (추가됨 2026-05-07 4차 세션)

### [V47] 포지션 복원 버튼 동작 확인 [다음 모의투자 장중]
- **내용**: "포지션 복원" 버튼 클릭 → `PositionRestoreDialog` 표시 → 값 입력 후 복원 → 잔고 패널 갱신
- **방법**:
  1. 재시작 후 포지션 0.00 상태에서 버튼 클릭
  2. LONG / 진입가(pt) / 수량 / ATR 입력 후 "복원" 클릭
  3. WARN.log `[PositionRestore] 완료: ...  손절=X.XX  TP1=X.XX  TP2=X.XX` 확인
  4. 잔고 패널: 방향·진입가·평가손익 갱신 확인
- **기준**: WARN 로그 출력 + 패널 비FLAT 표시 + 쿨다운 미작동

### [V48] B60 수정 후 잔고 패널 수치 HTS 대조 확인 [다음 포지션 보유 중]
- **내용**: 합성 잔고행의 `총매매 / 평가손익 / 손익율` 이 HTS 수치와 ±5% 이내인지 확인
- **방법**: LONG 포지션 보유 중 HTS "선물 실시간 잔고" 패널 vs 미륵이 대시보드 잔고 패널 스크린샷 비교
- **기준**: 총매매 = entry_pt × qty × 250,000. 손익율(%) = pnl_krw / eval_krw × 100

### [V44/B62] 모의서버 startup sync FLAT 오염 해소 확인 [다음 재시작]
- **내용**: LONG 포지션 중 재시작 → `[BrokerSync] 모의투자 blank-rows → 저장 포지션 유지` WARN.log 확인
- **기준**: position_state.json `"status": "LONG"` 그대로 유지 (FLAT으로 덮어쓰지 않음)
- **실패 시**: GetServerGubun 호출 오류 여부 확인 (try/except → `_is_mock=False`로 fallback)

---

## 즉시 확인 필요 (추가됨 2026-05-07 3차 세션)

### [V42] SHORT 진입 Chejan 체결 확인 [다음 장중]
- **배경**: CB③(30분 정확도 <35%) 발동으로 이번 세션에서 SHORT 진입 없었음
- **내용**: SHORT ENTRY 주문 → Chejan 접수 → Chejan 체결 end-to-end 확인
- **방법**: WARN.log `[ChejanFlow] fill_qty>0 status=체결 kind=ENTRY SHORT` 확인
- **기준**: `[PendingOrder] clear` 가 타임아웃이 아닌 체결로 발생 (filled_qty>0 경로)

### [V43] B56 쿨다운 실제 차단 확인 [다음 ENTRY 미체결 시]
- **내용**: ENTRY 주문 미체결 소멸 후 `[EntryCooldown] ENTRY 미체결 소멸 → 2분 재진입 금지 until HH:MM:SS` WARN.log 출력 + 2분간 STEP 7 진입 차단
- **방법**: WARN.log에서 `[EntryCooldown]` 로그 확인 후 2분 이내 `[EntryAttempt]` 없음 확인
- **기준**: 이전처럼 매 2분마다 반복 진입 없음

### [B56 / BalanceChejanFlow] 조사 완료 [DONE 2026-05-07]
- 09:56~10:09 구간 gubun='1' 잔고 Chejan 이벤트 없음 확인 (WARN.log 전수 분석)
- balance Chejan FLAT 경로는 당시 미작동 → 비이슈 종료
- B56 적용으로 해당 경로도 이제 자동 쿨다운 처리됨

---

## 즉시 확인 필요 (추가됨 2026-05-06 추가 세션)

### [V35] B54 통합 파라미터 후 ENTRY/EXIT Chejan 체결 확인 [DONE 2026-05-07] (구: trade_type=4)
- **변경**: B47(trade_type=4)·B54(lOrdKind=1+slby_tp)로 두 번 수정됨. 현재 코드는 B54 기준
- **방법**: WARN.log `[ChejanFlow] fill_qty>0 status=체결` + `[PendingOrder] clear` 확인 (타임아웃 아닌 체결 clear)
- **확인 포인트**:
  - LONG 진입: `[주문요청] LONG` → Chejan 접수 → Chejan 체결 → `[PendingOrder] clear` (300s 이내)
  - SHORT 진입: `[주문요청] SHORT` → Chejan 접수(order_no 확인) → Chejan 체결 (B54 효과)
  - LONG EXIT: `[ExitAttempt]` → `[ExitSendOrderResult] ret=0` → Chejan 체결 → position FLAT
- **실패 시**: `[OrderDiag] SendOrderFO` 로그에서 slby_tp 값 확인 후 enc 파일 재조사

### [V32] SendOrderFO 실제 체결 확인 [DONE 2026-05-06]
- 진입 주문은 정상 체결됨 확인 (10:48, 10:50, 11:35 체결 로그). EXIT 주문 미체결은 trade_type=2(신규매도) 오류 때문. B47 수정으로 해결 (trade_type=4 매도청산 전환).

### [V33] Fix B 낙관적 오픈 진단 확인 [DONE 2026-05-06]
- 14:28:00 `[FixB] 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True` 로그 WARN.log에서 확인됨.

### [V34] 프로그램매매 FID 확정 [다음 장중]
- **내용**: `P00101` 타입='프로그램매매' FID 202/204/210/212/928/929 의미 확인
- **방법**: PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 재확인. FID 928/929는 프로그램 매수/매도 누적 순매수금액 추정
- **활용**: FID 확정 시 `_on_receive_real_data()`에 프로그램매매 실시간 파싱 경로 추가 가능

---

## 즉시 확인 필요 (추가됨 2026-05-06)

### [V30] OPW20006 BrokerSync 정상 동작 확인 [DONE 2026-05-06]
- SYSTEM.log에서 `[BrokerSync] OPW20006 rows=1` 확인됨. 레코드명 `선옵잔고상세현황` 수정 성공.

### [V31] Fix B 이중진입 방지 확인 [DONE 2026-05-06]
- 14:28:00 `[FixB] 낙관적 오픈 완료` 로그 확인됨. 이후 분봉에서 이중진입 없음 (LONG 상태 유지 중 재진입 차단 동작).

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간 2세션)

### [V26] Kiwoom SendOrder 실제 체결 확인 [SUPERSEDED → V32]
- SendOrder가 SendOrderFO로 교체됨 (2026-05-06). V32로 대체됨.

### [V27] TP1/TP2 부분 청산 API 동작 확인 [다음 장중 포지션 보유 후]
- **내용**: TP1 도달 시 `_execute_partial_exit(price, stage=1)` 호출 → 33% 청산 주문 전송
- **방법**: TRADE 로그 `[Position] 부분청산 N계약 @ XXXX | 잔여=M계약` 확인
- **기준**: `partial_1_done=True` + Kiwoom 체결 내역 + trades.db PARTIAL 레코드

### [V28] 주문/체결 탭 실데이터 메트릭 표시 확인 [다음 실행]
- **내용**: 상단 `당일 거래` / `평균 지연` / `최대 지연` / `수신 횟수` 가 실데이터로 갱신되는지
- **방법**: 대시보드 실행 → 주문/체결 탭 → 분봉 처리 후 수치 변화 확인
- **기준**: "——" 대신 숫자 표시 (지연 ms 단위, 수신 횟수 증가)

### [V29] 로그 좌측 정렬 시각 확인 [다음 실행]
- **내용**: 주문/체결·손익·모델AI 탭 로그가 좌측 정렬로 출력되는지
- **방법**: 대시보드 실행 후 각 탭에서 로그 텍스트 정렬 확인
- **기준**: 구분선만 중앙 정렬, 나머지 모든 로그 좌측 정렬

---

## 즉시 확인 필요 (추가됨 2026-05-04 야간)

### [V22] opt50008 행 구조 확인 — 투자자별 vs 시간별 [다음 장중]
- **배경**: KOA Studio에서 opt50008 = 프로그램매매추이차트요청 확인. 출력: 체결시간·투자자별순매수금액
- **미확인**: 행이 투자자 유형별(개인/외인/기관...)인지 vs 시간대별인지 구조 불명
- **방법**: 다음 장중 DATA.log에서 `[TR-DISCOVER] opt50008 첫수신 rows=N fields=[...]` 확인
  - rows=10이면 투자자별(INVESTOR_KEYS 순서) 가능성 높음
  - rows=수십~수백이면 시간별 시계열로 판단 → 파싱 로직 수정 필요
- **기준**: `program_foreign_net_krw` 피처가 0이 아닌 값으로 채워지면 파싱 성공

### [V25] fetch_program_investor() 정상 동작 확인 [다음 장중]
- **내용**: opt50008 호출 성공 + `_program_investor` 캐시에 값이 채워지는지
- **방법**: DATA.log `[Investor] 프로그램투자자별 rows=N | 외인=±X 개인=±Y (KRW)` 확인
- **기준**: rows > 0 AND 외인/개인 값 중 하나라도 0이 아님
- **실패 시**: screen_no 충돌 가능성 — 2013 → 다른 번호로 변경

### [V23] 프로그램매매 실시간 FID 캡처 [다음 장중]
- **내용**: code=`P00101` type=`프로그램매매` FID 스캔 — 차익/비차익 순매수 FID 번호 확인
- **방법**: 장중 PROBE.log `[PROBE-ALLRT-FIDS] type='프로그램매매'` 항목 확인
- **활용**: FID 확정되면 opt10060 TR 폴링 → 실시간 수신으로 교체 가능

### [V24] 투자자ticker 실서버 지원 확인 [실서버 전환 후]
- **내용**: 실서버 전환 후 `투자자ticker` 실시간 타입 동작 여부 확인
- **방법**: 실서버 연결 후 PROBE.log `[PROBE-ALLRT] type='투자자ticker'` 수신 확인
- **배경**: 모의투자 서버 — 8가지 코드 조합 전부 ret=0이나 데이터 없음. 실서버 전용 추정

---

## 즉시 확인 필요

### [V1] OPT50029 초기 분봉 로드 확인 [SUPERSEDED 2026-05-04]
- 모의투자 서버에서 OPT50029 rows=0 확인됨 — SetRealReg(A0166000) 전환으로 대체
- 실 서버 전환 시 OPT50029 초기 히스토리 로드 재확인 필요

### [V20] SGD 지속 학습 확인
- **내용**: 매분 LEARNING 로그에 `[SGD] N건 학습 | SGD비중=30% 50분정확도=xx%` 출력되는지
- **방법**: 5층 로그 > 학습 탭. 초기 학습 완료 이후 매분 갱신 확인
- **기준**: 50분정확도 값이 분 단위로 변화 (현재 1/3 확률 학습 시작 → 실데이터 누적 후 개선 기대)

### [V21] SGD 10m·30m 호라이즌 학습 확인
- **내용**: 10m·30m가 현재 미학습 — 해당 ts DB 레코드 없어서 건너뜀
- **방법**: 장 진행 1시간 후 LEARNING 로그에 `[OnlineLearner] 10m 초기 학습 완료` 출력 확인
- **기준**: 13:44 + 10분 = 13:54 분봉 처리 시 자동으로 학습됨

### [V19] OFI bid/ask 정상 수신 확인
- **내용**: `[DBG-F4]` 로그에서 `bid=XXX.XX ask=XXX.XX` 가 0이 아닌 값으로 표시되는지
- **방법**: 재시작 후 첫 분봉 확정 후 DEBUG 로그 확인
- **기준**: bid > 0 AND ask > 0 → `ofi.update_hoga()` 정상 호출됨
- **파일**: `collection/kiwoom/realtime_data.py` `_on_hoga_data()`

### [V18] 파이프라인 watchdog 정상 해제 확인 [DONE 2026-05-04]
- watchdog 임계값 90/150/240s 적용 + log_loss 크래시 해결로 파이프라인 정상 완료
- "1분 30초 미실행" 경보는 크래시 구간(13:36~13:41)에서만 발생 → 정상

### [V2] run_minute_pipeline 완전 검증 [DONE 2026-04-27]
- `on_candle_closed` 호출 확인됨, 파이프라인 진입 확인됨

### [V3] run_minute_pipeline 예측값 출력까지 완전 검증 [DONE 2026-04-28]
- tick→분봉→on_candle_closed→pipeline→LONG 1계약 @ 1008.2 확인
- [Ensemble] dir=+1 conf=76.8% grade=A / [Checklist] 6/9 통과 자동진입 확인
- 더미 모델 기반 — 예측값은 무의미, 파이프라인 연결만 확인

### [V4] STEP 8 청산 트리거 + trades.db 저장 확인 [DONE 2026-04-28]
- trades.db 2건: 12:44 -0.10pt 하드스톱, 12:46 -0.70pt 하드스톱 확인
- `[Position] 청산 LONG @ 1009.45 | PnL=-0.10pt` 로그 확인

### [V5] STEP 9 predictions.db 저장 확인 [DONE 2026-04-28]
- predictions.db 30행 확인 (12:29·12:30 각 6 호라이즌)

---

---

## 즉시 확인 필요 (추가됨 2026-04-29)

### [V9] 다이버전스 패널 외인 데이터 표시 확인
- **내용**: 재시작 후 "외인 콜순매수", "외인 풋순매수", "다이버전스" 카드가 실제 값 표시하는지
- **방법**: 파이프라인 실행 후 `[Investor]` 로그 + 대시보드 다이버전스 탭 확인
- **기준**: "——" 대신 숫자 표시 (시뮬: 랜덤, 실거래: TR 실데이터)

### [V10] 진입 관리 탭 체크리스트 표시 확인
- **내용**: 체크리스트 아이콘이 V/X/— 3가지 상태 올바르게 표시되는지
- **조건 1**: 장 중 FLAT 상태 → V/X 표시 (체크리스트 평가됨)
- **조건 2**: 포지션 보유 중 또는 EXIT_ONLY 구간 → — 표시 (평가 안 됨)
- **V10a**: "산출 수량" N계약 표시 확인 (기존: "——" 고정)
- **V10b**: "당일 진입 통계" 매분 갱신 확인 (진입 0회→N회 업데이트)

---

## 즉시 확인 필요 (추가됨 2026-04-28)

### [V6] ATR 플로어 적용 후 진입 품질 확인 [DONE 2026-04-28]
- stop_dist=0.75pt 로그에서 정확히 확인됨
- `[DBG-F4]` ATR floor + `[DBG-STOP]` 하드스톱 발동 경로 모두 검증

### [V7] 포지션 복원 로그 확인
- **내용**: LONG 중 재시작 → `[Position] 이전 포지션 복원: LONG 1계약 @ XXXX` 로그
- **기준**: 재시작 후 FLAT 상태가 아닌 기존 포지션 유지

### [V8] CVD tick test 효과 검증
- **내용**: buyvol/sllvol이 실제로 분리되는지 확인 (이전엔 항상 buyvol=100%)
- **방법**: `[DBG-F4]` 로그에서 `buyvol`/`sllvol` 값이 다양하게 분포하는지 확인
- **기준**: 상승 틱에서 buy_vol > 0, 하락 틱에서 sell_vol > 0으로 분리됨

---

## 즉시 확인 필요 (추가됨 2026-04-30 자가학습 연결 세션)

### [V11] SGD 학습 로그 확인 [DONE 2026-05-04]
- 13:44 재시작 2분 후 1m/3m/5m/15m 초기 학습 완료 확인
- 이전 세션 DB 레코드 활용 (features 예측 당시 저장 → 올바른 supervised learning)

### [V12] GBM 일일 마감 재학습 확인 (15:40)
- **내용**: `daily_close()` 호출 시 `[GBM] 일일 마감 재학습 완료` 또는 `건너뜀` 로그
- **방법**: 15:40 이후 학습 탭 로그 확인
- **기준**: raw_candles 5000행 미만이면 "건너뜀", 이후엔 재학습 완료

### [V13] features 전체 저장 확인
- **내용**: predictions.db의 features 컬럼이 이제 20개 이상 피처를 저장하는지 확인
- **방법**: `SELECT length(features) FROM predictions LIMIT 5` — 기존 20개(~400자) → 전체(~1000자 이상)

### [V14] 🎯 효과 검증기 패널 표시 확인
- **내용**: "🎯 효과 검증" 탭이 정상 렌더링되는지 확인
- **방법**: 대시보드 실행 → 중앙 탭 6번째 "🎯 효과 검증" 클릭
- **조건 1**: 체결 완료 거래 0건 시 → "데이터 수집 중 (0건 체결)" 배너 표시
- **조건 2**: 체결 완료 거래 10건 이상 시 → 캘리브레이션·등급별·레짐별 테이블 수치 표시
- **조건 3**: 5분 주기 갱신 (패널이 빈 "——" 상태에서 수치로 전환되는지)

---

## 즉시 확인 필요 (추가됨 2026-04-30 이번 세션)

### [V15] 자동 종료 슬랙 알림 + 프로그램 종료 확인
- **내용**: 15:40 `daily_close()` 완료 후 슬랙 알림 수신 + 15초 후 프로그램 실제 종료
- **방법**: 테스트용 시간 임시 변경 (`datetime.time(15, 40)` → 현재 시간) 또는 실제 15:40 대기
- **기준**: 슬랙 알림 2건(일일 요약 + 종료 안내) + 15초 후 대시보드 창 닫힘

### [V16] 성장 추이 탭 렌더링 확인
- **내용**: "📈 성장 추이" 탭 7번째 탭이 정상 표시되는지
- **방법**: 대시보드 실행 → 중앙 탭 7번째 "📈 성장 추이" 클릭
- **조건 1**: 체결 데이터 0건 시 → "데이터 없음" 표시
- **조건 2**: 체결 데이터 있으면 일별/주별/월별/연간 탭에 집계 행 표시
- **조건 3**: 시작 500ms 후 선조회 동작 확인 (콘솔 오류 없이)

### [V17] daily_stats 스냅샷 저장 확인
- **내용**: 15:40 일일 마감 후 `trades.db`의 `daily_stats` 테이블에 당일 행 삽입 확인
- **방법**: `SELECT * FROM daily_stats ORDER BY date DESC LIMIT 5`
- **기준**: 오늘 날짜의 행이 trades·wins·pnl_krw·sgd_accuracy 포함하여 저장

---

## 예정된 작업

### [T1] 모의투자 4주 운영
- **전제**: [V1], [V2] 확인 완료 후
- **기준** (4주 완료 시 실전 전환 가능):
  - 통산 수익률 양수
  - Circuit Breaker 1회 이상 정상 작동
  - 일일 수익률 변동성 안정적

### [T2] Circuit Breaker 5종 트리거 테스트
- 각 트리거를 의도적으로 발동시켜 정지·청산 동작 확인
- `safety/circuit_breaker.py` + `safety/emergency_exit.py`
- **주의**: 중복발동 버그 수정됨 (2026-04-30) — 이제 PAUSED/HALTED 상태에서 재발동 없음
- **확인 포인트**: 발동 1회만 슬랙 전송되는지 + 대시보드 SYSTEM탭/경보탭에 표시되는지

### [T3] Walk-Forward 검증 (26주 데이터 필요)
- **기준**: Sharpe ≥ 1.5, MDD ≤ 15%, 승률 ≥ 53%
- `backtest/walk_forward.py` — 8주 학습 / 1주 검증 반복
- 실거래 데이터 26주 확보 후 실행

### [T4] ResearchBot → main.py 연결 (장외 자동 리서치)
- `research_bot/alpha_scheduler.py` — 16:00 자동 실행 스케줄러
- main.py에 연결하여 장외 자동 활성화
- **주의**: 자동 통합은 절대 금지 — 팝업 알림 + 사용자 검토 후 수동 통합

### [T5] PPO 정책 검증 — Sharpe +0.4 목표
- 실거래 데이터 확보 후 `learning/rl/policy_evaluator.py`로 평가
- 정적 규칙 대비 Sharpe +0.4 이상 확인 후 실전 적용

---

## 알려진 잠재 이슈

### [P0] [DBG] 출력문 정리 예정
- `api_connector.py`, `realtime_data.py`, `main.py`에 디버그 print 잔존
- 파이프라인 안정 확인 후 일괄 제거 (시스템 안정 전 제거 금지)

### [P1] GetMasterCodeList("10") — 모의투자 서버 빈값
- 모의투자 서버에서 None/빈값 반환 가능 (실 서버에서는 정상)
- `GetFutureCodeByIndex(0)` 추가로 우선순위 보완됨 — 해결됨

### [P2] py37_32 패키지 호환성
- scipy 1.5.4 고정 필수 (1.7.x DLL 충돌)
- torch 설치 시 32-bit 호환 버전 확인 필요 (PPO GPU 가속 미사용 시 numpy fallback)

### [P3] 뉴스 감성 분석 — HF API 연결 실패 시 fallback
- `features/sentiment/kobert_sentiment.py`: HF API 오프라인 시 키워드 사전 fallback
- 실전 환경에서 fallback 동작 확인 필요

### [P4] 알파 풀 JSON 파일 증가
- `research_bot/alpha_pool.py`: MAX_ACTIVE=50 제한 있으나 퇴역 알파 파일 관리 정책 미확정

### [P6] FID_BID_PRICE=41 / FID_ASK_PRICE=51 명칭 역전 의심
- KOA 개발가이드에서 FID 41=매도1호가, 51=매수1호가 가능성 시사
- 현재 constants.py는 41=BID(매수), 51=ASK(매도)로 정의됨
- ofi.py에서 매수/매도 방향 계산에 사용 중 — 역전이면 OFI 방향 반전 버그
- **수정 전 반드시**: ofi.py 계산 방향 확인 후 결정 (섣부른 수정 금지)

### [P5] bid/ask = 0 — OFI 영구 0 [DONE 2026-05-04]
- 선물호가잔량 콜백 `_on_hoga_data()` 신설 + `sopt_type="1"` 추가 등록으로 해결
- 모의투자 서버에서 선물호가잔량 수신 확인됨 (로그에서 확인)
- **검증 필요**: [V19] 재시작 후 `[DBG-F4]` 에서 bid/ask 값 확인
## 2026-05-07 세션 후속

### DONE 처리
- [DONE 2026-05-07] **[B52]** ENTRY 타임아웃 시 낙관적 포지션 FLAT 복원 구현 (`main.py` L544). **[V39] 장중 동작 확인** ✅
- [DONE 2026-05-07] **[V35/V41]** B54(lOrdKind=1+slby_tp) 완전 검증 — LONG 진입/EXIT 즉시 체결. PnL 배수 500,000원/pt 확인
- [DONE 2026-05-07] **[B49]** EXIT 경로 진단 로그 추가 — 하드스톱/시간청산 앞뒤에 `[ExitAttempt]` + `[ExitSendOrderResult]` 추가
- [DONE 2026-05-07] **[B50]** price_hint float 오차 수정 — `round(exit_price, 2)` 적용 (하드스톱/시간청산)
- [DONE 2026-05-07] **[B53]** ENTRY 타임아웃 후 2분 쿨다운 구현 — `_entry_cooldown_until` 설정 + STEP 7 진입 조건 차단 + `[EntryCooldown]` 차단 로그 + `[차단] ENTRY 타임아웃 쿨다운` 이유 로그
- [DONE 2026-05-07] **BrokerSync CRITICAL → WARNING** — position_state.json 잔여로 매 시작 시 CRITICAL 출력되던 것 WARNING으로 완화 (blank rows FLAT 처리는 정상 동작)
- [DONE 2026-05-07] **[B54]** SendOrderFO 파라미터 통일 — `api_connector.send_order_fo(slby_tp="")`추가. 모든 진입/청산/긴급청산을 `lOrdKind=1(신규매매) + sSlbyTp` 방향 명시로 변경. trade_type=2(SHORT)가 new convention에서 "정정"으로 해석되어 서버 조용히 거부되는 원인 해결
- [DONE 2026-05-07] **[EntrySendResult]** `log_manager.system()` 추가 — `_ts_execute_entry` 내 ret 값이 대시보드 SYSTEM 탭에 표시됨 (기존: file logger만)

### [V41] B54 SHORT/EXIT Chejan 정상 수신 확인 [DONE 2026-05-07]
- LONG 진입 즉시 체결 (접수+체결 10:14:00 동시) ✅
- LONG EXIT 즉시 체결 (접수+체결 10:34:01 동시), `[ExitAttempt]`/`[ExitSendOrderResult]` 정상 ✅
- SHORT 진입은 이번 세션에서 미발생 (CB ③ 발동으로 당일 정지). SHORT Chejan 검증은 다음 세션

### 다음 실행 최우선 검증

### [V39] B52 ENTRY 타임아웃 복원 동작 확인 [다음 장중]
- **내용**: ENTRY 체결 안 됨 → 60s 타임아웃 → `[FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원` 로그 확인
- **기준**: WARN.log에 `[FixB] ENTRY 타임아웃` 로그 + 이후 position.status=FLAT + EXIT 루프 미발생
- **실패 시**: `_optimistic` 플래그 설정 시점 (`position_tracker.py`) 재확인 필요

### [V40] EXIT 경로 진단 로그 확인 [다음 포지션 청산 시]
- **내용**: 하드스톱/시간청산 발동 시 `[ExitAttempt]` → `[ExitSendOrderResult] ret=0` 로그 순서 확인
- **기준**: ret=0이면 `[PendingOrder] set EXIT_FULL`, ret≠0이면 `[Exit] ... 주문 실패` 로그
- **활용**: EXIT 무응답 시 ret 값으로 키움 API 오류 코드 즉시 특정 가능

## 2026-05-06 세션 후속

### DONE 처리
- [DONE 2026-05-06] BrokerSync startup 차단 원인 1차 규명
- [DONE 2026-05-06] 주문/체결/복원 디버그 관측점 대폭 추가
- [DONE 2026-05-06] 포지션 state 저장 메타(`last_update_reason`, `last_update_ts`) 추가

### 다음 실행 최우선 검증
- [V30] blank placeholder `OPW20006` 응답이 실제로 FLAT 판정으로 해석되는지 검증
- [V31] `ret=-302` 또는 주문 실패 상황에서 로컬 LONG 오픈/복원 불일치가 재발하는지 검증
- [V32] `EntryAttempt -> PendingOrder -> OrderMsgDiag -> ChejanFlow -> PositionDiag` end-to-end 인과관계 검증

### 새 작업
- [T6] startup sync 이후 신규 진입 gate 정책 재검토 (`verified=False`와 `blank row`를 분리)
- [T7] 디버그 로그 정리 단계 준비 (유효 관측점 유지, 과도한 로그는 다음 안정화 후 축소)
## 2026-05-06 세션 마감 반영

### [V36] 실시간 잔고 패널 UI 재구성 + 대괄호 제거 [DONE 2026-05-06]
- 좌측 컬럼 2단 분할, `실시간 잔고` 카드/게이지/합계 6개/잔고 테이블 추가 완료.
- 헤더 `계좌번호`, `전략명` 콤보 정렬 완료.
- 합계칸 `[ ]` 플레이스홀더 제거 완료.

### [V37] OPW20006 blank summary fallback 적용 [DONE 2026-05-06]
- `OPW20006` summary가 전부 blank일 때도 상단 패널이 비지 않도록 fallback 적용 완료.
- `총매매/총평가손익/총평가`는 잔고행 합산, `실현손익`은 `daily_stats().pnl_krw`, `총평가수익률/추정자산`은 계산값/0 기반으로 채움.

### [V38] 실시간 잔고 원본값 검증 + 전용 계좌합계 TR 분리 검토 [다음 세션]
- **내용**: `OPW20006`이 장후/무포지션에서 summary/rows를 모두 비우는 케이스가 확인되었으므로, 합계 6개를 전용 계좌합계 TR로 분리할지 검토.
- **방법**: 장중/장후 각각에서 `OPW20006-SUMMARY-BLANK`, `BalanceUIFallback` 로그와 화면값 비교.
- **기준**: 장중에도 summary blank가 반복되면 `총매매/총평가손익/실현손익/총평가/총평가수익률/추정자산` 전용 TR 추가 구현.
---

## 2026-05-07 Log Review Update (after 2026-05-06 10:14)

### DONE / outcome reflected

- [DONE 2026-05-07] **[V30] BrokerSync blank placeholder handling verified**
  - Evidence:
    - `2026-05-06 14:11:20 [BrokerSync] raw rows=1 nonempty_rows=0 all_blank_rows=True`
    - `2026-05-06 14:11:20 [BrokerSyncFlatPlaceholder] ... before='FLAT'`
    - `2026-05-06 14:11:20 [BrokerSync] status verified=True block_new_entries=False reason=blank/no holdings response interpreted as flat`
  - Conclusion:
    - blank placeholder row is no longer treated as hard mismatch
    - startup no longer blocks new entries in this case

- [DONE 2026-05-07] **[V32] Entry -> pending -> Chejan acceptance chain verified for live path**
  - Evidence:
    - `2026-05-06 14:28:00 [EntryAttempt]`
    - `2026-05-06 14:28:00 [EntrySendOrderResult] ret=0`
    - `2026-05-06 14:28:00 [PendingOrder] set kind='ENTRY'`
    - `2026-05-06 14:28:00 [ChejanFlow] ... status='접수' order_no='0076887'`
    - `2026-05-06 14:28:00 [ChejanMatch] pending_matched=True`
  - Conclusion:
    - request -> pending -> Chejan order acceptance path is now observable end-to-end
    - remaining gap is not "no Chejan at all" but delayed/missing fill on some orders

### Still open / narrowed by log review

- [OPEN 2026-05-07] **[V31] historical local/broker mismatch around 10:48:19 still not fully explained**
  - Evidence:
    - `2026-05-06 10:48:19 [WARN] [Entry] ... ret=-302`
    - `2026-05-06 10:48:19 [TRADE] [Position] 진입 LONG 1계약 @ 1124.1`
    - `2026-05-06 10:48:31 [Position] 이전 포지션 복원`
  - Current judgment:
    - this mismatch is historical and predates the later diagnostics/fixes
    - do not treat it as reproduced after the 14:11 restart

- [OPEN 2026-05-07] **[V41] SHORT entry and EXIT Chejan fill still need dedicated proof**
  - What is verified now:
    - LONG entry acceptance Chejan exists
    - LONG exit final fill Chejan exists at `2026-05-06 15:24:58`
  - What is still missing:
    - clean SHORT entry case with `status='접수'` and matched order number
    - clean SHORT exit fill case

- [OPEN 2026-05-07] **[V42] EXIT pending timeout loop root cause narrowed to fill latency / no immediate fill**
  - Evidence:
    - from `2026-05-06 14:29:00` to `15:24:01`, repeated:
      - `PartialExitAttempt` / `PartialExitSendOrderResult ret=0`
      - `PendingOrder set`
      - timeout clear after about 1-2 minutes
    - first actual exit acceptance/fill only appears at `2026-05-06 15:24:58`
  - Conclusion:
    - this is no longer pointing first at `trade_type` mismatch
    - likely remaining issue is one of:
      - mock-server fill/accept delay
      - wrong/ambiguous FO parameter combination on some exit paths
      - pending timeout policy being too aggressive before broker response

- [OPEN 2026-05-07] **[V43] ENTRY timeout clear still releases retry too early when only Chejan acceptance exists**
  - Evidence:
    - `2026-05-06 14:28:00` entry receives Chejan `status='접수'` with order number
    - but pending is cleared at `14:29:00` with `filled_qty=0`
    - system then moves on immediately into exit logic because optimistic LONG remains open
  - Risk:
    - acceptance without fill can still leave local state ahead of broker reality
  - Next check:
    - distinguish `accepted(order_no assigned)` from `filled(fill_qty > 0)` in timeout handling

- [OPEN 2026-05-07] **[V38] balance summary fallback still operationally necessary**
  - Evidence:
    - `2026-05-06 18:51:29 [BalanceUIFallback] summary blank from OPW20006; rows=0`
  - Conclusion:
    - startup flat interpretation is fixed
    - summary fields from `OPW20006` are still not reliable enough to retire fallback

### Immediate next tasks

- [T8] split pending order state into `accepted` vs `filled`
  - Goal:
    - when `order_no` is assigned by Chejan, mark accepted and do not recycle the order as if nothing happened
  - Priority:
    - highest

- [T9] review ENTRY/EXIT timeout policy
  - Goal:
    - stop 1-minute timeout clears from causing repeated resend loops while broker-side order is still live
  - Check against:
    - `14:28:00 -> 14:29:00` ENTRY
    - `14:29:00 -> 15:24:58` EXIT loop

- [T10] verify one clean SHORT scenario end-to-end
  - Need logs for:
    - `EntryAttempt`
    - `EntrySendOrderResult ret=0`
    - `ChejanFlow status='접수'`
    - `ChejanFlow status='체결'` or explicit non-fill evidence

- [T11] verify whether `gubun='4'` is now safely ignorable in active code path
  - Historical log still shows `gubun='4'` noise on 2026-05-06
  - Need next-run proof that logic ignores it without side effects

### 2026-05-07 balance UI wiring update

- [DONE 2026-05-07] **[B57] broker balance summary now uses auxiliary Kiwoom futures TRs**
  - `request_futures_balance()` now keeps `OPW20006` as canonical row source
  - added auxiliary summary enrichment from:
    - `OPW20007`: `약정금액합계`, `평가손익합계`, `청산가능수량`
    - `OPW20008`: `추정예탁총액` / `예탁총액`
    - `OPW20003`: `총손익`, `수익율`, `예탁총액`
  - goal:
    - HTS 상단 요약값이 비어도 미륵이 실시간잔고 UI summary가 따라오게 연결

- [NEXT 2026-05-07] **[V44] live verification on account balance panel**
  - confirm dashboard summary updates from broker values:
    - `실현손익`
    - `추정자산`
    - `총매매`
    - `총평가손익`
  - confirm position row still maps correctly for startup broker sync:
    - `종목코드`
    - `매매구분`
    - `잔고수량`
    - `주문가능수량`

- [NEXT 2026-05-07] **[V45] validate OPW20003 input convention in live/mock environment**
  - current assumption:
    - `시장구분="0"` with same-day `시작일자/종료일자`
  - if `OPW20003` returns blank/None in practice:
    - capture request/response log
    - verify exact Kiwoom convention from local enc / guide notes
    - adjust without breaking `OPW20006/20007/20008` path

- [CHECK 2026-05-07] **12:13 restart log verdict**
  - `2026-05-07 12:13:48` proves the new auxiliary probes are wired:
    - `OPW20007.*`
    - `OPW20008.*`
    - `OPW20003.*`
  - but all values are still blank at restart, so startup-only balance UI improvement is not yet confirmed

- [DONE 2026-05-07] **[B58] refresh balance UI immediately after normal fill flows**
  - added `_ts_refresh_dashboard_balance(self)` after:
    - `EntryFillFlow`
    - `ExitFillFlow` final
    - `ExitFillFlow` partial/remaining
  - reason:
    - 12:15~12:18 logs show fills are normal, but no balance refresh is triggered because `gubun='1'` balance Chejan is absent

- [NEXT 2026-05-07] **[V46] verify post-fill balance refresh logs after next run**
  - expected after next fill:
    - balance TR request/response logs right after `EntryFillFlow` or `ExitFillFlow`
    - dashboard summary no longer stuck at startup zeros
## 2026-05-08 Ensemble Upgrade session close-out

### DONE reflected today

- [DONE 2026-05-08] `ENSEMBLE_SIGNAL_UPGRADE_PLAN.md` 에 `Update Status`, `Next Work`, `Effect Validation Checklist` 반영
- [DONE 2026-05-08] 대시보드 중간 패널에 `A/B / Calibration / Meta Gate / Rollout` 효과 검증 탭 추가
- [DONE 2026-05-08] 네 리포트 자동 주기 실행 연결
  - `Calibration / Meta Gate / Rollout`: 15분
  - `A/B`: 30분
- [DONE 2026-05-08] `effect_monitor_history.json` 추이 스냅샷 저장 시작
- [DONE 2026-05-08] `EfficacyPanel` 탭 툴팁 오배선 버그 수정 및 실제 툴팁 표시 검증 완료
- [DONE 2026-05-08] `predictions` 원확률 저장, `ensemble_decisions` gating/toxicity/meta 저장, `MICRO-MINUTE <-> raw_features` 대조 경로까지 검증 완료

### NEXT priority

- [NEXT 2026-05-09] horizon별 `temperature scaling` 도입
  - 목표: `ECE 0.399783` 개선
  - 결과물: calibration before/after 비교 리포트

- [NEXT 2026-05-09] A/B negative delta 원인 분석
  - 현재: `pnl delta=-3.60pt`, `accuracy delta=-0.10%p`, `changed sample=53`
  - 목표: 어떤 gating / microstructure 신호가 손익 악화에 기여했는지 구간별 분석

- [NEXT 2026-05-09] `meta_labels` 추가 축적 후 threshold 재튜닝
  - 현재 표본: `34`
  - 목표: `take/reduce/skip` 임계값 재추천 및 실제 손실 회피 효과 검증

- [NEXT 2026-05-09] rollout 승격 재평가
  - 현재 추천 단계: `shadow`
  - 승격 조건: calibration 개선 + meta 표본 증가 + A/B 재개선 확인

- [NEXT 2026-05-09] toxicity gate 장중 발동률 집계
  - `pass/reduce/block` 저장분이 다음 장중부터 누적되므로 실제 분포 확인 필요

---

## 2026-05-16 세션 마감 (41차)

### DONE

- [DONE 2026-05-16] **[B51] DashboardAdapter.chk_slack 노출 누락 크래시 수정**
  - `dashboard/main_dashboard.py` `DashboardAdapter.__init__`에 `self.chk_slack = self._win.chk_slack` 추가
  - `_save_ui_prefs()` 위임 메서드 추가

- [DONE 2026-05-16] **HORIZON_THRESHOLDS 재보정**
  - 5월 초 고변동성 장세 기반 (σ_1min≈1.47pt) 기준으로 전체 약 2.5배 상향

- [DONE 2026-05-16] **EmergencyExit pending_registrar 추가**
  - CB/KillSwitch 비상청산 시 Chejan 오분류 방지 경로 완성

- [DONE 2026-05-16] **PositionTracker same-side sync 보강**
  - grade 보존, partial_done 플래그 보존

- [DONE 2026-05-16] **Threshold Monitor 추가**
  - GBM 재학습 완료/30분 주기로 ATR 동적 vs Static 비교 모델 AI탭 기록

### NEXT (2026-05-17 이후)

- [NEXT] **B51 수정 후 재기동 검증**
  - `start_mireuk.bat` 재실행 → `[System] Qt 이벤트 루프 진입` 확인
  - `py_compile` 문법 검증: `python -m py_compile dashboard\main_dashboard.py main.py safety\emergency_exit.py strategy\position\position_tracker.py config\settings.py`

- [NEXT] **Threshold 재보정 장중 검증**
  - 목표: 30분 호라이즌 FLAT 비율 29~37% 범위 달성 여부 로그 확인
  - `[Threshold Monitor]` 로그에서 ATR 동적값 vs Static 비교 확인

- [NEXT] **PnlHistoryPanel 체크박스 UI 동작 확인**
  - 순방향/역방향 체크박스 토글 시 일별/주별/월별 테이블 재갱신 확인

- [NEXT] **비상청산 pending_registrar 동작 확인**
  - CB/KillSwitch 발동 시 `[EmergencyExit] pending 등록` 로그 확인
  - Chejan 체결이 "외부체결"가 아닌 EXIT pending 매칭으로 처리되는지 확인

- [NEXT] **BrokerSync EXIT pending 보존 동작 확인**
  - EXIT 주문 진행 중 잔고 Chejan 유입 시 `[BrokerSync] 잔고 Chejan — EXIT pending 진행 중, pending 유지` 로그 확인

- [NEXT] **모의투자 장중 운영 지속**
  - Phase 5 진입 조건 향해 4주 통산 수익률 + CB 발동 검증 계속

---

## 2026-05-16 세션 마감 (46차)

### DONE

- [DONE 2026-05-16] **[B52] 역방향 체크박스 의미론 버그 수정**
  - _active_rows()로 reverse_entry_enabled 기준 필터링
  - _group(), _build_daily/weekly/monthly/summary 단순화

- [DONE 2026-05-16] **[B53] 미니선물 5배 과대계상 수정 (pt_value 종목코드 연동)**
  - normalize_trade_pnl(pt_value=) 파라미터화
  - _get_pt_value_from_prefs() 추가 — symbol_code 기준 자동 결정
  - TRADE_PNL_FORMULA_VERSION 3→4 bump — 기존 레코드 자동 재마이그레이션

- [DONE 2026-05-16] **[B54] 체크박스 상태 재시작 후 초기화 수정**
  - _save_ui_prefs() 읽고-병합-쓰기 방식으로 변경

- [DONE 2026-05-16] **[B55] 총 손익 중복 계산 수정**
  - broker_total 고유 날짜 집합 기준으로 변경

- [DONE 2026-05-16] **P/L 원 열 별표(★) 제거**

### NEXT (2026-05-17 이후)

- [NEXT] **v4 마이그레이션 재시작 후 확인**
  - 재시작 시 5/14 pnl_krw가 ~2.9M으로 갱신되는지 확인
  - 총 손익 수치가 일별 누적 마지막값과 일치하는지 확인

- [NEXT] **5/14 qty 과다 기록 분석**
  - 5/14 DB 2.9M vs 실제 ~1.5M: pt_value와 무관한 수량 과다 기록 가능성
  - qty=2인 거래들이 실제 2계약인지, 1계약이 2번 기록됐는지 HTS 체결 내역과 비교

- [NEXT] **PnlHistoryPanel 역방향 데이터 실제 검증**
  - 역방향 체크 단독 시 실제 역방향진입 거래만 표시되는지 확인
  - 역방향 진입이 없는 최근일은 0건으로 나오는지 확인

- [NEXT] **모의투자 중 운영 지속**
  - Phase 5 진입 조건 향해 4주 수익률 + CB 발동 검증 계속

---

## 2026-05-17 세션 마감 (47~48차 + DB 초기화)

### DONE

- [DONE 2026-05-17] **주별/월별 브로커 정산 + MDD 일별 집계 (47차)**
  - _mdd_daily(grp): 거래 단위 진동 제거, 일별 집계 MDD
  - W20 MDD: -6,997,034원 → -5,616,847원

- [DONE 2026-05-17] **주별/월별 pt-원 불일치 수정 (48차)**
  - 주별/월별 P/L 원: DB pnl_krw 일관 사용 (broker 혼용 제거)
  - W20: pt(-24.93pt) 원(-1,599,354원) 방향 일치

- [DONE 2026-05-17] **trades.db 전체 초기화**
  - 백업: data/db/trades_backup_20260517.db
  - 목적: 2026-05-19(월)부터 오염 없는 데이터로 손익추이 검증

### NEXT (2026-05-19 월요일 이후)

- [NEXT] **손익추이 유효성 검증 — 2026-05-19부터 5일간**
  - 체결 후 trades 테이블 행이 정확히 1건만 생성되는지 (qty 과다 기록 없는지)
  - pnl_pts × pt_value(50k) = pnl_krw 오차 5% 이내인지
  - pt 음수면 원도 음수인지 (방향 일치) 매일 확인
  - reverse_entry_enabled 필드 올바르게 기록되는지

- [NEXT] **주별/월별 누적 vs 일별 누적 최종값 일치 여부 확인**
  - 일별 탭 누적 마지막값 = 요약 헤더 총 손익인지
  - 주별 탭 누적이 일별 탭 누적과 다를 수 있음 (broker 정산 미적용) — 이 차이 문서화

- [NEXT] **qty 과다 기록 근본 원인 분석**
  - 5/14 DB qty=2 거래들이 실제 1계약이었는지 HTS 체결 내역과 비교
  - Chejan 분할체결 집계 로직 검토 (_ts_build_agg_exit_result)

- [NEXT] **모의투자 중 운영 지속**
  - Phase 5 진입 조건 향해 4주 수익률 양수 + CB 발동 검증 계속
## 2026-05-18 세션 마감 업데이트

### DONE

- [DONE 2026-05-18] GBM 배치 재학습 산출물을 `gbm_*.pkl + scaler_*.pkl + feature_names.pkl` 구조로 정렬
- [DONE 2026-05-18] 좌하단 `파라미터 상관계수`를 실제 recent feature history 기반 계산값으로 교체
- [DONE 2026-05-18] SHAP tracker / `shap_scores` / 중패널 SHAP 탭 런타임 배선
- [DONE 2026-05-18] 재시작 직후 restored/live 분석 버퍼 복원 경로 추가
- [DONE 2026-05-18] 중패널 `동적 피처 (SHAP)` 운영 플로우 카드 추가
- [DONE 2026-05-18] startup crash 2건 수정
  - `DB_DIR` import 누락 `NameError`
  - SHAP history shape mismatch `IndexError`

### NEXT

- [NEXT 2026-05-19] CYBOS Plus 연결 상태 점검
  - `U-CYBOS/CYBOS Plus is not connected` 런타임 예외 재현/해소
  - Cybos 로그인 세션, 선물 가능 상태, autologin/preflight 경로 확인

- [NEXT 2026-05-19] managed feature set 운영 검증
  - `추천 1 적용 + 재학습` 클릭 시 `data/db/shap_feature_registry.json` 반영 여부 확인
  - retrain 후 `feature_names.pkl`과 runtime `model.feature_names` 일치 확인

- [NEXT 2026-05-19] SHAP 3개 항목 복구 검증
  - `foreign_call_net`, `foreign_retail_divergence`, `program_non_arb_net`가 실제 active feature set과 `feature_names.pkl`에 포함되는지 확인
  - 좌하단/중패널에서 0.0% 고정 해소 여부 확인

- [NEXT 2026-05-19] 중패널 운영 플로우 UX 검증
  - 툴팁, 버튼 enabled/disabled 상태, review summary, cooldown/교체이력 표시가 실운영 시나리오와 맞는지 확인

- [DONE 2026-06-08] SHAP 탭 코드 정리
  - `dashboard/main_dashboard.py` 내 중복 `update_shap()` 정의 정리 (3개→1개, 죽은코드·중간버전 제거)
[DONE 2026-05-20] **68차: `entry_mode` 미초기화 치명 예외 수정**
- `run_minute_pipeline()` 공통 차단 로그 경로보다 앞에서 `entry_mode`/`allowed_grades`/`mode_filter_passed`를 안전 초기화하도록 조정

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
