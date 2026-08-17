# 미륵이 (futures) 현재 개발 상태

> 마지막 업데이트: 2026-07-27 (390차) — 정기점검(일일점검) 수행 + 이 파일의
> 마지막 업데이트: 2026-08-17 (MW0601 472차) — UI 좌상단 배지를 Phase 5 전환 게이트
> 마지막 업데이트: 2026-08-17 (MW0601 473차) — 구조적 교착 2건(F-8·D8) 해소 시도 +
> D9 도달성. **매매 정책 변경 0건 — 전부 계측·테스트다.** 전체 **434 passed / 0 failed**
> (신규 28). 2026-08-17은 임시휴일 = 휴장이라 비거래일 창.
>
> 🔴 **F-8은 교착이 아니었다.** `spread_extreme_shadow` 불리언이 안 남는 것은 사실이나
> (소비처 0곳), **`spread_ticks` 원값은 처음부터 `ensemble_decisions.features`(141키
> JSON)에 매분 있었다** — 24,113행·max 104.9998·≥20틱 911행(37거래일).
> 결손은 데이터가 아니라 **질의 가능한 컬럼**이었다 → Phase B로 2컬럼 배선(arity 50→52).
>
> 🔴 **그런데 ⑨는 기다려도 닫히지 않는다.** 사전등록 후 소급 판정 = **INSUFFICIENT**.
> 911건은 **분봉**이고 손익 판정에 필요한 건 **진입**인데 `≥20틱 진입 = 6포지션/4거래일`
> 뿐이다(0.094건/거래일 → min_samples 도달 **ETA 7.1개월**). 311차의 "n=8~19" 는 진입
> 기준으로 옳았다. ⚠ 문턱을 낮춰 판정하지 말 것(458차 D6 동일 위반).
> 또 ⑨ 근거 한 축("block 무발동")은 **419차 재보정(0.78→0.45)으로 소멸**했다
> — `W18~W28 0건 → W29~W32 510건`. → ⑨의 거처가 주간회의 안건이 됐다.
>
> 🔴 **D9 — 도달 불가는 30m만이 아니다.** `select_entry_horizon()`이 `1m/3m/5m`만
> 반환해(경계 3개) **중기(10m·15m)·장기(30m) CORE 그룹이 구조적으로 도달 불가**다.
> 458차는 이를 표본 부재로 읽었으나 원인은 코드 구조다(471차 F-1과 같은 유형).
> 하필 앙상블 가중 최대 두 호라이즌이 10m(0.29)·15m(0.28)로 **합 57%**가 그 그룹이다.
> 처분은 §3 절대원칙이라 결정하지 않고 도달성 테스트로 현재 상태를 선언 고정했다.
>
> 🟡 **D8은 「대기」로 결론. 초안 권고(인프라 리허설)를 철회했다.**
> ① 학습창 단축은 **실행 불가**(opt_* 96%를 얻으려면 8,716봉 = MIN_TRAIN_BARS의 58%).
> ② 2종 즉시는 **알파 근거 없음** — 기록 rho와 **부호 반대**(`cvd_monotone_ratio`
> +0.031 → **−0.0115**). `threshold_feasibility`·`basis_pt` 선례와 같은 패턴이라
> **레지스트리 rho 전반이 낡았다**(26주 WFA 배터리 안건).
> ③ "97→N 경로 미검증"이 **틀렸다** — 292차가 MW0602에서 이미 했고(기계적 성공),
> ScalerWarmup 0-패딩 → long 정확도 14~20% 급락 등 사고가 이어졌다. 미지가 아니라
> **기지의 위험**이다. 정보가 필요하면 `BatchRetrainer(model_dir=, scaler_dir=)`로
> **샌드박스 재학습**(위험 0)을 쓴다. `--apply`는 331차 관례(CLAUDE.md §6) 위반이라
> `--governance-approved` 필수로 막았다.
>
> 🔴 **더 큰 발견 — 피처 슈퍼셋은 git으로 전파될 수 없다(D8보다 선행).**
> `data/db/shap_feature_registry.json`은 `.gitignore:20 data/` 대상이고, 브랜치 분기점
> **291차 `5e1426c`** 직후 **292차**가 97→105를 `dev`에서 했다. 즉 MW0601은 한 번도
> 105가 된 적이 없다. "양 PC 동시 적용"(D12·F9)은 고칠 동기화 실패가 아니라
> **존재하지 않는 절차**다. (같은 날 예약 장전점검이 독립적으로 같은 뿌리의 다른 증상을
> P1으로 올렸다 — 469차 스킬만 v9-dev에 있고 462·468차 대상 코드는 없음)
>
> 🟡 **[1] 테스트가 458차 만성도 계측을 삭제하고 있었다.** `test_457_daily_fixes.py`가
> `_CHRONIC_PATH`를 격리하지 않아 가짜 missing 목록이 실제 파일에 기록됐고(30m 16종 중
> 11종이 97 슈퍼셋에 이미 있는 피처), "복귀 피처 제거" 로직이 **진짜 기록을 지웠다**.
> 개별 테스트가 아니라 **conftest autouse 격리**로 고쳤다. 오염분은 백업 후 삭제.
> 부수: **E6 해소**(457차 테스트가 pytest에서만 죽던 것) · **[코드버그] `math.comb`은
> py3.8+인데 런타임은 3.7** — 표본이 차는 7개월 뒤 처음 터질 코드를 테스트가 잡았다.
> 상세: `DECISION_LOG.md` 2026-08-17(473차), `NEXT_TODO.md` 473차 F1~F10.
>
> 이전 업데이트: 2026-08-17 (MW0601 472차) — UI 좌상단 배지를 Phase 5 전환 게이트
> 자동 판정으로 교체. **매매 정책 변경 0건**(UI 표시와 판정기만). 신규 20 tests.
>
> 🔴 **좌상단 "Phase 3 예정" 배지가 두 달 넘게 기각된 계획을 예고하고 있었다.**
> 하드코딩 문자열이었고, 툴팁이 예고한 3항목 중 ①Platt Scaling은 **458차에**,
> ②anti_signal 역신호 채널은 **457차에** 각각 기각(둘 다 NEXT_TODO "하지 말 것" 등재),
> ③MFE 레이블은 Triple-Barrier로 대체됐다. 착수 조건도 Sharpe만 있고 **MDD·승률·
> 전환기준 ⑤~⑨가 통째로 누락**된 구버전이었다. 계측 4원칙 ④("폴백이 정상값처럼
> 보인다")와 같은 결함이며 대상이 DB 컬럼이 아니라 UI였을 뿐이다.
> → `strategy/ops/phase5_gate_status.py`가 CLAUDE.md 전환기준 ①~⑨를 **settings.py
> 실측 + 결정 레지스트리**(`PHASE5_GATE_DECISIONS`)로 매번 재판정한다.
>
> **현재 게이트 실측: 충족 0 / 미충족 5 / 미측정 4 (0/9).** ⑤⑥⑦⑧⑨는 설정값으로
> 미충족 확정, ①②③④는 trades.db·WFA 실측이 필요해 **미측정**이다 —
> "미측정"을 "미충족"으로 세지 않는다(계측 4원칙 ②). 자동 판정은 **한쪽 방향으로만**
> 확정한다: `CB_CONSEC_STOP_LIMIT`을 2~3으로 되돌려도 ⑤는 MET이 아니라 UNMEASURED다
> (v9 계획 §0-1이 "복원 후 발동 1회 확인"을 함께 요구). ⑧도 목표자본이 바뀌면
> MAX_CONTRACTS 재산출 여부를 코드가 모르므로 UNMEASURED다.
>
> **깜빡임은 기한 있는 게이트에만** — `due` D-7 이내/경과 시에만. 현재 유일한 `due`는
> ⑤ CB② 재검토 **2026-08-29**(오늘 D-12, 조용) → **2026-08-22부터 자동 개시** 예정.
>
> 🟡 **선행 결함 발견(이번 변경과 무관)**: `tests/test_457_guard_meta_and_scope.py`가
> **pytest에서만** 실패한다 — `_bind()`가 `__main__`에서만 호출돼 `_Stub`에 메서드가
> 안 붙는다. 직접 실행은 통과. 즉 457차 P4 가드 유효성 판정이 스위트에서
> **빨간불이면서 아무것도 지키지 않는 상태**다(NEXT_TODO E6).
> 전체 **405 passed / 1 failed(그 선행 결함)**.
> 상세: `DECISION_LOG.md` 2026-08-17(472차), `NEXT_TODO.md` 472차 E1~E6.
>
> 이전 업데이트: 2026-08-12 (MW0601 458차 후속) — 미구현 제안 P0·P3 구현.
> 전체 **308 passed**. **매매 정책 변경 0건.**
> **P0(B1 나머지 절반)**: 457차가 스왑만 고쳤고(559→41~84ms), 워커가 **파이프라인과
> 같은 분에** 떠서 언피클 2.1~2.5초가 GIL을 물어 S0~S6를 **동시에 3~8배** 늦추고
> 있었다. 언피클만 조용한 창(:15)으로 이동 — `MODEL_RELOAD_QUIET_WINDOW`, 롤백
> `enabled=False`. **스왑 지연 0**(원래도 다음 분 drain이 받아감, 실측 :01→:15.0 시작
> →:17.1 종료). 합격선은 다음 거래일 **선로드 분 S0<200ms + CB⑤ 0건**(D7-G).
> **P3**: 조기축소 3건이 전부 진입 후 11~47초(2건은 직후 반등)라 `elapsed_sec` 축을
> tier1·tier2에 신설. **판정 문턱은 일부러 비웠다**(사후적합 방지) — 표본 도달 후
> 주간회의에서 합격선을 **먼저** 정한다. tier2 `ts` 분절단(425차 tier1만 수정)도 정정.
> 🔴 **P1 "Purged CV 재사용"은 전제 오류로 기각** — CV는 454차부터 **이미 퍼징돼
> 있다**(LeakGuard 포함). 그런데도 cv가 최신 OOS 대비 3m −12.2pp 부풀려지므로 원인은
> 누출이 아니라 **레짐 혼합**이다. 처방은 이미 배포된 P1-A·P1-C. **재론 금지.**
>
> 이전 업데이트: 2026-08-12 (MW0601 458차) — 0812 일일점검 + 이상점 3건 딥다이브·조치.
> **매매 6포지션 4승 2패 +170,448원**(포지션 단위). 457차 게이트 14개 중 **13개 통과,
> B1만 미달**. CB 발동 0건. 전체 **293 passed**. **매매 정책 변경 0건 — 전부 계측이다.**
>
> 🔴 **가장 중요한 발견: 456차 가드 전환조건이 원리적으로 달성 불가였다.**
> "오염 0봉 5거래일 연속"은 장중 재학습이 매일 cutoff를 밀어올리는 한 성립할 수 있는
> 날이 없다(실측 홀드아웃 1,850봉 중 **1,691봉=91% 항상 오염**). F6·F7이 각각은
> 설계대로 작동했는데 합성되면 **EOD 교체 6/6이 매일 무검증 통과**(ghost_bypass)한다.
> 지금 EOD 모델 교체에 작동하는 품질 검증은 **하나도 없다**. 부수로 CV 인플레이션
> 실측(3m cv .4215 vs 최신 OOS **.3000**, −12pp) — ⑤안의 "CV 검증"이 그만큼 낙관적이다.
> → **P1-A 깨끗한 꼬리 매치드 대조** 배포(오염일에도 살아남는 유일한 공정 표본,
> `guard_shadow_log` clean_* 4열 누적). **판정 경로는 무변경** — `acc_txt` 유지.
> 자체 정정: 딥다이브 초안의 검정력이 2배 낙관이라 전환 문턱을 5→**10거래일**로
> 상향 사전등록(`EOD_GUARD_CLEAN_TAIL`, 1일 CI ±7.3pp / 10일 ±2.3pp).
>
> 🔴 **A1 "절편" 가설 기각.** 30거래일 walk-forward 카운터팩추얼에서 prior 보정의
> 정확도 이득이 **±0.8pp 잡음**이고 DN 예측이 오히려 **증가**했다 → 편향은 절편이
> 아니라 **조건부 구조**에 있다. **A1 후보 ①②③(가중 재산출·Platt·보정기 해제)은
> 정확도 회복 수단으로 전부 기각** — 재시도 금지(NEXT_TODO "하지 말 것"). 더 나쁜
> 사실: P(적중|DN예측) ≈ 베이스레이트로 **방향 예측이 무정보**다(5m .334 vs .34).
> 처방은 캘리브레이션이 아니라 **신호**이므로 455차 배터리가 유일한 정직한 경로.
> 오늘 방어선은 실증됐다 — SHORT 신호 168건 중 체크리스트가 54/55 차단, 뚫린 1건이
> 당일 손실의 81%(−145,072원). **오늘 흑자는 모델이 아니라 체크리스트가 만들었다.**
>
> 🟡 **opt_chain_pcr은 수집 문제가 아니었다.** 라이브 값 정상(30m 0.5953, 07-15부터
> 92%). 원인은 학습 X의 **97개 동결 슈퍼셋**(`use_feat_names`)이라 새 피처가 컬럼조차
> 못 얻는 구조 — 260704 감사 P3의 합집합 수정이 **배포일 이래 실효 0**이었다(바로
> 아랫줄이 덮어씀). 단 동결 자체는 추론 공간 일치를 위한 의도적 설계다. 30m CORE는
> **이중 사문화**(IC −0.0066 n=209 · 장기 그룹 체크리스트 발동 **사상 0건**) —
> `CLAUDE.md` §3에 상태 명기(P2-A), 처분은 F9. `[FeatureReg]`에 만성도 병기(P2-C).
>
> **B1은 미달이 아니라 원인 이동**: 스왑은 41~84ms로 해결됐으나 **선로드 분**에
> S0 1,714~1,904ms + S1·S4·S5·S6 **동시 3~8배**(자원 경합 = 자기 워커의 GIL 점유).
> 457차 G9 규칙대로 재조사 회부 — 권고는 **선로드 시각 이동(②) 먼저**.
> 313차 검증: `loss_tier1_qty1_shadow` 누적 +18.810pt이나 **일자 부호검정 p=0.3438
> 비유의 → 채택 보류**(이상치 의존 아님, 거래일이 병목).
> 상세: `DECISION_LOG.md` 2026-08-12(458차), `docs/정기점검/매일점검/
> MW0601-20260812-점검리포트.md` + `…-이상점3건-딥다이브.md`.
>
> 이전 업데이트: 2026-08-11 (MW0601 457차) — 0811 일일점검 + Fix 파동 W-A~W-E 구현.
> **456차 Wave 3(F6·F7)이 배포됐으나 목적 미달성이었음을 확인하고 완결**했다:
> ① F6 — `retrain_eod.py`가 `_load_from_db()`로 채운 `_train_row_ts`를
> `retrain_now(X=...)` 주입 경로가 무조건 폐기해(batch_retrainer.py:543) 오염 검출이
> 6/6 호라이즌 "미상"만 반환 → **행 수 일치 불변식**으로 정상화.
> ② F7 — `_ghost` 플래그가 로그만 되고 판정에 미반영이라 **3m EOD 교체가 7거래일
> 연속 보류**(08-03~08-11) → 사용자 결정 **⑤안**(`EOD_GUARD_GHOST_POLICY="replace"`).
> 그 외: 모델 리로드 비동기화(S0 **559ms → 3.6ms**, CB⑤ 임계의 93%까지 붙던 스파이크
> 제거) · SHAP 워커 이관(매분 460~520ms 임계경로 제거) · `_entry_horizon_pre`/
> `_entry_horizon` **할당부 0개** 결함 수정(`meta_gate_horizon` 370/370건이 '1m'
> 고정이었음) · `daily_stats.sgd_accuracy/verified_count` 8일 연속 폴백값 수정.
> 진단: SHORT 편향(60거래일 n=85,263)의 원인이 **모델 절편**으로 확정 — 라벨은 균형,
> 확률만 전 호라이즌 DN 편중. **역방향 알파는 없다**(반전 시 적중률 하락).
> 자체 정정: "부분청산이 수수료를 2배화" 전제는 **거짓**(레그 분할과 무관, 실측 차이 0원).
> 이어서 **고도화 G4~G9** 배포 — 전부 계측·규약이고 **매매 정책 변경 0건**이다:
> G4 방향편향 상시감시 채널[50] · G5 모델건강도(`scaler_daily` 7컬럼, 앙상블 유효
> 가동률 08-11 **74.3%**) · G8 `CLAUDE.md` **계측 4원칙** 신설 + 폴백 자동검출.
> **의도적 축소 3건** — G6은 A3로 흡수(소급 실측이 `quantile_expected_pt`의 예측력을
> 기각: rho=0.156, 3분위 격차 −2.4%p) / G7은 섀도만(ConstOut 구간 × 진입 시도
> 교집합 **0건** — 효과 미확인) / G9는 관측만(B1이 원인을 없앴을 수 있음).
> G8 검출기가 배포 즉시 `_futures_code`를 잡았으나 조사 결과 교차모듈 주입인
> 정상 경로였고, 457차 이전 main.py로 역검증해 검출기 실효를 확인했다.
> 전체 테스트 **279 passed**. 상세: `DECISION_LOG.md` 2026-08-11(457차 + 후속),
> `docs/정기점검/매일점검/MW0601-20260811-점검리포트.md`.
>
> 이전 업데이트: 2026-07-27 (390차) — 정기점검(일일점검) 수행 + 이 파일의
> 337차(07-15) 이후 52차분(338~389차) 미반영 공백 발견·해소. 아래
> "338~389차 커밋(git log) 요약 브릿지" 섹션에 그 52개 세션의 커밋 메시지를
> 압축 색인으로 추가(각 세션의 상세 서사는 여전히 `DECISION_LOG.md`/
> `SESSION_LOG.md`에 있음 — 여기 표는 "이 파일이 가장 먼저 읽혀야 한다"는
> 취지를 지키기 위한 최소 색인일 뿐, 재작성이 아님). 오늘(390차) 자체
> 점검에서는: 매크로 RISK_ON인데 KOSPI200이 자체 급락(개장~조사시점 약
> -3.5%)해 `IntradayRegime`이 CRASH로 장중 대부분 유지, C등급 후보 25건 중
> 24건이 게이트 차단·1건만 체결(A급 SHORT, 하드스톱 -12,595원 손절), CB①~⑤
> 미발동·에러 0건 확인. 발견된 이상점 중 실제 버그 1건 확정 수정:
> `dashboard/panels/setup_expectancy_panel.py`가 실사용 DB
> (`config.settings.TRADES_DB` = `data/db/trades.db`)가 아니라 방치된 빈 파일
> `data/trades.db`(2026-05-18 최초 커밋 b32c6dc부터, 0바이트)를 하드코딩
> 참조해 "셋업 기대값" 패널이 두 달 넘게 항상 빈 결과만 반환하던 조용한 버그
> — `TRADES_DB` import로 교체. 상세: `NEXT_TODO.md`/`DECISION_LOG.md`
> 2026-07-27(390차) 항목.
>
> 이전 업데이트: 2026-07-15 (337차) — 대시보드 중간 패널 "동적피처" 탭 데이터가
> 몇 시간째 갱신되지 않는 문제 수정. `featureset by horizon/horizon_feature_sets.json`의
> `"1m".include`가 2026-07-13/14 딥다이브에서 신규 피처 목록으로 갱신됐으나
> (문서 자체에 "P0-1 완료 전까지 미탑재 상태 유지"라 명시) 실제 배포된
> `gbm_1m.pkl`은 구 12피처 세트로 학습된 채였음. `main.py:_ensure_shap_tracker()`가
> 배포 모델이 아니라 이 레지스트리로 ShapTracker 피처셋(8개)을 구성해 실제
> 모델(12피처 기대)과 shape mismatch가 발생, `permutation_importance()`가
> 매분 조용히(DEBUG 레벨) 실패 → "동적 SHAP TOP3"/"전체 피처 순위" 패널이
> 08:41부터 3시간+ 갱신 안 됨(`logs/20260715_LEARNING.log` 실측 확인).
> `self.model.horizon_feature_names["1m"]`(모델 로드 시 `n_features_in_`으로
> 이미 검증된 실제 배포 피처셋)을 우선 사용하도록 수정하고,
> `_permutation_importance_fallback()`에 shape 사전체크 + WARNING 로그 상향을
> 추가(향후 재발 시 즉시 드러나도록). `_shap_labeled_window["1m"]`가 이미
> 누적돼 있어 재적립 대기 없이 즉시 효과가 나야 함. **라이브 미검증** — 다음
> 실 UI 기동/장중에서 동적피처 탭이 채워지는지, `[SHAP] 중요도 계산 불가`
> 경고가 사라지는지 확인 필요. 상세: `DECISION_LOG.md`/`NEXT_TODO.md`
> 2026-07-15(337차) 항목.
>
> 이전 업데이트: 2026-07-15 (335차) — 대시보드 "진입단계추적" 위젯의 "모드필터"
> 차단사유가 X등급 신호를 항상 오분류하던 라벨링 버그 수정. `allowed_grades`
> (auto→A, hybrid→A/B, manual→A/B/C)가 어느 모드에도 "X"를 포함하지 않아,
> `_final_grade=="X"`일 때 `mode_filter_passed`가 모드 설정과 무관하게 항상
> False가 됨 — 그런데 `main.py:6920` `elif not mode_filter_passed:`가 진짜
> 사유(체크리스트 미통과 항목·`8_time` 시간대 차단)를 담당하는
> `elif _final_grade == "X":`(6930)보다 먼저 와서, X등급 차단이 전부 "모드필터
> 불일치"로 잘못 표시되고 있었음. `dev_memory/DECISION_LOG.md` 2026-07-12(311차
> 후속2)의 "OTHER 126건이 '모드필터: X급 신호 vs manual 모드'로 잡힘" 관찰이
> 이미 이 패턴을 포착했었으나 근본원인(elif 순서)까지는 짚지 않았었음. 실제
> 진입 실행 경로(`main.py:7027`의 `grade!="X"` 가드)와는 무관한 표시/로그
> 라벨링 버그 — 조건에 `and _final_grade != "X"` 추가로 수정, X등급은 이제
> 6930의 등급X 분기로 넘어가 진짜 사유가 노출됨. **라이브 미검증** — 다음
> 실 UI 기동 후 X등급 신호가 "STEP7 차단" 사유란에 "Chk X — ..." 형태로
> 정확히 뜨는지 육안 확인 필요. 커밋: `8401d5c`(코드 수정, 차수 표기 없이
> 선커밋됨). 상세: `DECISION_LOG.md`/`NEXT_TODO.md` 2026-07-15(335차) 항목,
> `docs/미륵이고도화/모드필터_X등급_오분류_수정_2026-07-15.md`.
>
> 이전 업데이트: 2026-07-15 (334차) — 대시보드 좌측 중단 "1분~30분" 호라이즌
> on/off 체크박스 카드 제거, `config/settings.py:HORIZON_ENABLED`로 일원화.
> 이 체크박스는 단순 표시용이 아니라 `main.py:5396-5407`에서
> `pred_panel.get_enabled_horizons()`로 실제 앙상블 진입 판단(호라이즌 수동
> 배제)에 쓰이던 기능이라, 무단 제거 대신 사용자 확인(AskUserQuestion) 후
> 기능까지 함께 제거→설정화로 진행. `PredictionPanel`의 체크박스 그리드·
> 툴팁·`ui_prefs.json` 저장/로드·이미 죽어있던 invisible 프레임 루프까지
> 정리(~240줄 삭제), `get_enabled_horizons()`는 `HORIZON_ENABLED` 읽기로
> 단순화(`main.py` 호출부 무변경). 좌측 스플리터 크기
> `[200,500,280]`→`[200,420,360]`로 재배분해 "진입단계" 카드(conf_trend_card)
> 확장. `QT_QPA_PLATFORM=offscreen` 스모크테스트로 대시보드 전체 생성 +
> 호라이즌 배제 시 투표 결과 변화까지 직접 실행 확인. **라이브 미검증** —
> 다음 실 UI 기동 시 카드 배치·`HORIZON_ENABLED` False 반영 여부 육안 확인
> 필요. 상세: `DECISION_LOG.md`/`NEXT_TODO.md` 2026-07-15(334차) 항목.
>
> 마지막 정규 기동 확인: 2026-07-13 (315차) — 08:41 기동~EOD+P8(15:48) 전일 로그
> 전수 점검, 신규 버그 없음. 313차/314차가 그날 발견·수정한 4건(MaskedFallback
> 크래시·P4 로그 %s 미치환·intraday old_acc=nan·FATAL 자동복구 부재)이 이후
> 하루 종일 재발 없음 확인. 오늘 -8.4% 급락으로 13:33경 실제 KRX 서킷브레이커가
> 발동해 분봉 수신이 끊겼고 프로세스가 watchdog에 의해 재기동(포지션 FLAT이라
> 무해) — 상세: `SESSION_LOG.md`/`NEXT_TODO.md` 315차 항목. 실체결은 하루 종일
> 0건(정상적인 MetaGate 최소신뢰도 미달, 오탐 아님).
>
> **304차 daily_close() Qt 크로스스레드 크래시 수정 — 라이브 검증 완료
> (2026-07-13)**: 오늘 15:40:27~15:40:44 daily_close가 크래시 없이 정상
> 종료됨을 확인. 15:48 EOD 재학습도 6/6 호라이즌 정상 교체 + P8 스케일러
> 재적합까지 에러 없이 완료.
> 이 파일이 가장 먼저 읽혀야 한다.

---

## 338~389차 커밋 요약 브릿지 (2026-07-15~07-26, 압축 색인 — 390차 작성)

> 이 표는 337차 이후 이 파일 상단 요약이 52차분 갱신되지 않았던 공백을 메우기
> 위한 **최소 색인**이다. 각 항목은 해당 커밋 메시지를 그대로 옮긴 것으로,
> 세부 근거·수치·라이브 검증 여부는 `DECISION_LOG.md`/`SESSION_LOG.md`의 해당
> 차수 항목 또는 `git show <hash>`로 확인할 것 — 이 표만 보고 세부 결정을
> 내리지 말 것.

| 차수 | 커밋 | 요약 |
|---|---|---|
| 338 | c135947 | 다이버전스+포지션 탭 미갱신 딥다이브 — 양매수/양매도 0-덮어쓰기 회귀 수정, ITM/OTM N/A 표시, VKOSPI 실측 검증 |
| 339 | 99ebe3f | 7/15 진입 딥다이브 — TP1 보호모드 기본값 전환 + 신호소멸청산 섀도우 복구 |
| 340 | 66f696f | 사이징 파라미터 상향(5천만원/3%) + TP1 회계적 분할청산(synthetic partial) |
| 341 | 53bcded | 유령 하드스톱 수정 — 트레일링 갱신 후 스톱 과거 봉고저가 소급적용 버그 |
| 342 | b2ab04f | KellyAdvisedSkip 계측→게이트 승격 검토 — 주간 검증캠페인 [8]번 항목 신설 |
| 343 | d3423a9 | 연장 추격 필터(anti-chasing) — EntryChecklist 10번 항목 신설 |
| 344 | fc89725 | FQAdj 완화 방향 오류 수정 — 실측 정확도 게이트 추가 |
| 345 | 55a9ed8 | 마감 근접 신규진입 컷 — 14:50으로 10분 앞당김 |
| 346 | f7755d8 | EOD 모델 교체 가드 — CV acc/OOB 하락 시 교체 보류 + 참고용 저장 + 알림 |
| 347 | 303c83c | 336차 잔여 — entry_block_reason 오탐 경고 + 빈 사유 8건 근본 해결 |
| 348 | 1e64e20 | 틱 하드스톱 최대 60초 지연 제거 — QTimer.singleShot(0, ...) 즉시 처리 위임 |
| 349 | 85fd77e | 급변장 사전 가드 — 분당 틱수·1분 변화폭 동시 초과 시 스킵/사이즈축소+스톱확대 |
| 350 | cac3d5b | 349차 후속 — 몬키패치 그림자 죽은 코드 4곳 제거 |
| 351 | 5ef5d63 | ZeroDiag 이상값피처 로그에 "(candidate)" 태그 추가 |
| 352 | 8a07a60 | HORIZON_TIME_POLICY 09:05~09:10 사각지대 수정 — "1m만" → "3m만" |
| 353 | d6536c1 | 확신도 고착 임시 부스트 — 5m 고착 시 3m 가중치 이전 (P2-b 옵션 c) |
| 354 | a467181 | OPEN_VOLATILE 시가이격 필터 재설계 보류 + 주간 검증캠페인 [8]번 채널 신설안 등록 |
| 355 | 5754ed2 | 354차 구현 — 주간 검증캠페인 [9]번 open_gap_shadow 채널 실장 |
| 356 | a76b121 | Slack 워크스페이스/토큰/채널 교체 (330차 message_limit_exceeded 조치) |
| 357 | bbb45ac / f29d2b6 | 주간회의 판정 + [2]/[3] 캠페인 채널 부활(스코어러 환경불일치 수정·NO-DATA 생존점검·7/17 휴장 소급) + PC 구분 정정(이 PC=MW0602) |
| 358 | fa44583 / a85d934 / 0e72d03 / 0a91540 | MW0601 주간회의 판정 독립 재현 + 스케일러 격리 버그·WarmupRetrain 자기스킵 버그 수정 + 스케일러 손상 없음(97피처 일관) 확인 |
| 359 | 83b9749 | 0720 정기점검 후속 3건 — pre_market_stage2 비동기화, 레짐 불안정도 섀도 게이트, PreRetrain 영업일 로그 |
| 360 | 49e2dab / 8abb100 | 손절 계단화(Loss Tier1) 구현(339차 미착수 부채 해소) + 역추세 진입 캡(Countertrend Cap) 구현 |
| 361 | b1ec3b7 | TP3 도달 0건 원인 규명 + qty=2 재배분 섀도 A/B(tp2_hold_shadow) 구현 |
| 362 | 6e857b1 / 6622f02 | 청산 P1~P6 문서-코드 불일치 정리 중 AttributeError 버그 수정 + exit_manager.py 제거 + Hurst 재검증을 26주 재검증 등록부에 편입 |
| 363 | 2239db4 / 0cde21f | 손절계단화 사각지대 2건 해소(tick-level 확장 + qty=1 대체안 섀도) + 0721 딥다이브 제안 2건 캠페인 편입 |
| 364 | a328f2b | 0721 정기점검 딥다이브 — tp2_hold_shadow 표본 0건 구조적 원인 규명 + 363차 커밋 라이브 미반영 확인 |
| 365 | c5db614 | 손익 추이 패널 주별/월별 브로커 정산값 미반영 버그 수정 |
| 366~367 | ba32192 | A/C등급 순EV 역전 근본원인 규명 + GradeEVGuard·검증캠페인[13]~[15] 신설 |
| 368 | 07b9e4a / 7ed019f | MW0601 대형 손실 딥다이브 — ChaseForeignComboGuard(섀도) + 검증캠페인[16] + 체크리스트 항목별 순EV 회귀분석 스크립트 |
| 369 | 0427f50 | 0723 정기점검 — 운영 이상 없음 확인 + 청산 체결 슬리피지 계측 채널[17] 신설 |
| 370 | 1b9f91b | OPEN_VOLATILE/SHS-EKS/거래소CB관망 실행게이트 미배선 버그 수정 |
| 371 | 56ca3fc | PSI 상시 CRITICAL 고착 원인 규명·수정 — 균등폭bin 메가빈 + 라이브버퍼 미영속 |
| 372 | f793b51 | PSI 임계값 손익검증+313차 방식 재보정 시도 — 근거 부족으로 보류(기존값 유지) |
| 373 | 1c3c1f6 | 5m 호라이즌 IC 딥다이브 최초 실측 — 오늘 실거래 전부가 쓴 호라이즌인데 미착수 상태였음 |
| 374 | 9337375 | select_entry_horizon() 3-way 분류기 "5m" 고정 버그 재보정 |
| 375 | afe8a10 | entry_horizon 경계값 주간 재보정 모니터 신설(자동 반영 없음) |
| 376 | d4d3c72 | 5m 무정보 피처 4개 제거 구현 + purged WFA CV 검증(결과 혼조) |
| 377 | 79843ee / 7ed019f | ChaseForeignComboGuard 표본에 0723 발동 3건 정식 편입(n=5→8) |
| 378 | eb7297c | 377차 "EOD 체인 미연결" 결론 정정 — 07-15에 이미 수정됨 |
| 379 | e2e866b | RegimeExhaustionGate(섀도) 신규 구현 — 검증캠페인 [18] regime_exhaustion_watch |
| 380 | 586a093 | toxicity_score 계측 재설계 — atr/spread/queue/cancel stress 5종 재보정 + cancel_churn_ratio 신규 |
| 381 | 16b2fda / f7757d3 | 검증캠페인 6스크립트 mojibake 근본원인 수정(stderr UTF-8 미설정) + EOD 재학습 킬 딥다이브 + ExecutionTimeLimit 상향 실측 확인 |
| 382 | 68887aa | ThresholdRecalibrator에 run_if_due() 패턴 적용(375차 사각지대 해소) |
| 383~384 | cd0511a | 검증캠페인 [1] Triple-Barrier 채널 판정 유지(carry-forward) 구현 — 383차 구조결함 해법 |
| 385 | 62c7a71 | toxicity_block_shadow 신설 — ToxicityGate action="block" counterfactual 채널(검증캠페인 [19]) |
| 386 | 5e216a9 | "📐 재보정 모니터" 통합 탭 신설 — 5개 재보정/재검증 모니터를 한 화면에 |
| 387 | 1d0d12b | HORIZON_THRESHOLDS·entry_horizon 경계값 주간 재보정 반영 |
| 388 | 744d0fe | docs 정기점검·레슨런·참조자료 업데이트 |
| 389 | 32efc44 | 고도화2 계획 진행점검 5항목 실측 검증 + 분해분석 + H4 그라운드워크 |

---

## 2026-07-14 (332차) — 장후(18:28) 디버그 재기동 크래시 2건 진단·수정

①`main.py:_restore_analysis_buffers()`가 `self.model.feature_names`(전체
슈퍼셋)로 SHAP 복원 벡터를 만들어 `self._shap_tracker`(1m 서브셋)와 어긋나
`IndexError`로 `TradingSystem.__init__` 자체가 실패하던 버그 수정.
②그 수정 후에도 Python 예외 없이 프로세스가 조용히 죽어 `crash_fault.log`를
보니 `0xc0000374`(STATUS_HEAP_CORRUPTION) 네이티브 크래시 확인 — shap 0.41
`TreeExplainer`가 `HistGradientBoostingClassifier`(배치 재학습 주 경로 모델)를
정상 예외 대신 힙 손상으로 처리, `try/except`로 못 잡던 경로였음.
`_calc_importance()`에 `hasattr(model, "estimators_")` 가드 추가로 회피.
라이브 검증 여부: `DECISION_LOG.md`/`NEXT_TODO.md` 2026-07-14(332차) 항목 참조.

---

## 2026-07-08 (304차 후속 — daily_close() 백그라운드 스레드 Qt 위젯 직접조작 access violation 크래시 루프 수정)

**계기**: 15:40 종료 흐름 점검 중 `logs/20260708_SYSTEM.log`에서 daily_close()가
15:40:29→15:41:25→15:42:20→15:43:15에 걸쳐 4회 연속 크래시-재시작을 반복하는 것을
실측(15:44:25에 우연히 통과해 정상 종료 — 재시작 불필요, 포지션 FLAT 확인).

**원인**: `crash_fault.log`에서 access violation 스택 확인 —
`daily_close()`(백그라운드 스레드 `_run_daily_close`) → `dashboard.update_strategy_ops`
→ `set_fingerprint_level` → `refresh`(QWidget.setText/setStyleSheet). daily_close()가
대시보드 Qt 위젯을 GUI 스레드 밖에서 직접 조작 — PyQt 미정의 동작. 같은 근본원인이
`logging_system/log_manager.py`의 `_warn_cross_thread` 계측(302차, 0707 크래시
딥다이브)에도 이미 지목돼 있었으나 계측만 하고 실제 배선은 안 된 상태였음.

**변경**: `main.py`에 `_daily_close_ui_sig`(Qt `QueuedConnection`, `_shutdown_sig`와
동일 패턴) 신설 — `daily_close()` 내 `update_exchange_cb_badge`/`update_strategy_ops`/
`update_trend`/`_refresh_pnl_history` 4곳을 메인 스레드로 위임. `log_manager.py`의
`log()` 콜백 디스패치도 non-main 스레드 호출 시 `QueuedConnection` 브릿지로 메인
스레드에 위임하도록 근본 수정(daily_close 외 GBM 재학습·DB 라이터 등 다른 백그라운드
스레드의 동일 크래시 경로도 함께 차단).

**검증**: offscreen PyQt 스모크테스트로 백그라운드 스레드 emit → 메인 스레드 실행
확인, `main.py`/`log_manager.py` import 정상. **라이브 미검증** — 다음 재기동 후
daily_close가 크래시 없이 완주하는지 확인 필요.

상세: `dev_memory/SESSION_LOG.md`·`DECISION_LOG.md` 304차 후속.

---

## 2026-07-08 (304차 — 진입관리 탭 UI 정리: 원신호/실행신호 폭 축소+차단사유/레짐 이전, 상태스트립·자격현황 카드 제거, 방향인디케이터 카드 축소)

**계기**: 사용자가 진입관리 탭·상단 상태스트립·좌측 방향인디케이터 스크린샷을 순차
제시하며 UI 정리 4건 요청.

**변경** (상세: `dev_memory/SESSION_LOG.md` 304차):
1. `EntryPanel` row0에 차단사유+레짐 2줄 카드 신설(원신호 카드 자리), 원신호/실행신호
   폭을 stretch 2:1:1로 절반 축소하며 우측 정렬. `update_data()`에 hurst/atr/regime
   배선 추가.
2. `StatusStripPanel` 클래스·인스턴스화·`DashboardAdapter` 미러링 4곳 전체 제거
   (헤더 배지·진입관리 탭에 이미 중복 노출되던 정보라 손실 없음).
3. 호라이즌 자격 현황(Qualification Monitor) 카드·`update_qualification()` 경로 전체
   제거(`main.py:5514` 호출부 포함). `_horizon_runtime_state` 자체는 다른 로직에서
   계속 사용되어 유지.
4. `DirectionIndicatorWidget._build_lamp()` 고정 높이 130→92px, 폰트/여백 비례 축소.

**미검증**: 오프스크린(`QT_QPA_PLATFORM=offscreen`) 렌더링으로 stretch 비율·텍스트·
sizeHint 수치만 확인, `py_compile` 통과. **라이브 미검증** — 실제 창 기동 후 육안
확인 필요.

상세: `dev_memory/SESSION_LOG.md` 304차.

---

## 2026-07-08 (303차 후속 — HealthPolicy Degraded Mode 오발동 수정: exceptions_10m 정책로그 오집계)

**계기**: 사용자 보고 — C등급 자동진입 켜둔 상태에서 13:02~14:21 내내
`degraded_conf=33~37% < min=62.0%`로 자동진입 반복 차단.

**원인**: `exception_density_10m`(main.py:1513)이 실제 예외가 아니라 SYSTEM 레이어
WARNING+ERROR+CRITICAL 로그 줄 수를 그대로 집계. 09:49부터 매분 찍히는
`[RegimeFingerprint] PSI CRITICAL`(계측 결함으로 상시 CRITICAL 고착, 303차에서
진입차단만 비활성화해둔 상태)이 10분 창에서 단독 10건 이상 쌓여 CRIT 임계(12)
초과 → 09:58:57 Degraded Mode 진입 후 자기순환(Health 자신의 CRITICAL 로그도
집계됨)으로 하루 종일 해제 안 됨. Degraded Mode 중엔 등급(A/B/C) 필터보다 먼저
고정 `HEALTH_DEGRADED_MIN_CONF=0.62` 체크가 실행되어, UI의 "C등급 자동진입" 설정과
무관하게 conf 33~37% 신호가 전부 차단됨.

**변경**: `config/settings.py`(`HEALTH_EXCEPTION_EXCLUDE_TAGS` 9종 신설),
`logging_system/log_manager.py`(`get_level_counts` exclude_prefixes 파라미터),
`main.py`(두 호출부 배선: `_emit_runtime_health`, 6149행 lookahead).

**미검증**: `ast.parse` 통과만 확인. **라이브 미검증** — 앱 재시작 필요(핫리로드
미적용 대상: 신규 import).

상세: `dev_memory/SESSION_LOG.md`·`DECISION_LOG.md` 303차 후속 항목.

---

## 2026-07-08 (303차 — ATR 게이트 상한 만기주 예외 + 재보정 제안 모니터 신설)

**계기**: 07-08 만기(7/9) 전날 딥다이브에서 ATR 피크 10.22pt가 절대상한(6.0pt)을
크게 초과해 신규진입 다수 차단 확인. "1~2주 롤링 캡"으로 완전 자동화하는 안은
시뮬레이션 결과 변동성 상승 초입에 오히려 차단율이 더 커지는 역효과가 확인되어
기각하고, 사용자 결정으로 ①만기 캘린더 예외 ②저빈도 사람검토 재보정(알파봇과
동일 "제안만, 자동반영 금지" 원칙)으로 대체.

**변경**:
1. `features/technical/expiry.py`: `is_near_monthly_expiry()` 신규(만기 D-2~D+1
   판정). `config/settings.py`: `ATR_EXPIRY_CEILING_*` 4종 추가.
   `main.py:6115` 부근 ATR 적응형 상한 계산에서 만기 D-2~D+1이면 절대상한
   6.0→9.0pt(×1.5) 일시 확대. 대시보드 툴팁 갱신.
2. `learning/atr_ceiling_recalibrator.py` 신규 (`ThresholdRecalibrator` 패턴
   재사용) — 최근 15거래일(만기 제외) ATR로 floor/ceiling 제안값 산출,
   `atr_ceiling_monitor.db` 기록, WATCHLIST 이상 시 Slack 알림만
   (`utils.notify`). **자동 반영 없음** — config/settings.py 수동 수정 필요.
   `daily_close()` 금요일 게이트 + 내부 10일 간격 게이트로 사실상 1~2주 주기
   (`main.py:8251`).

**미검증**: 5개 파일 `py_compile` 통과, 재보정기 드라이런(임시 DB)으로 만기 제외
로직·간격 게이트 확인. **라이브 미검증** — 다음 금요일 EOD Slack 알림 수신 여부,
다음 만기(8월 둘째 목요일) 전후 실제 게이트 완화 동작 확인 필요.

상세: `dev_memory/SESSION_LOG.md` 303차.

---

## 2026-07-07 (301차 — Hurst 산출 흐름 점검 및 배선 수정)

**계기**: 사용자 요청으로 hurst(허스트 지수) 산출부터 소비처까지 전체 흐름 점검.

**발견 및 수정** (상세: `dev_memory/DECISION_LOG.md` 301차 항목):
1. `hurst_override` 플래그(탈진 레짐 시 Hurst 차단 무효화 의도)가 산출만 되고
   `main.py`에서 소비되지 않던 배선 누락 → `_hurst_ok` 게이트에
   `current_micro_regime == REGIME_EXHAUSTION` 조건 추가(`main.py:6055-6059`)
2. `scripts/backfill_features.py`가 실거래(`calculate_hurst()`)와 다른 자체
   공식(`_hurst_rs()`)으로 hurst를 계산해온 train/serve skew 수정 — 공용 함수로 교체
3. `strategy/shadow_evaluator.py`의 Hurst 게이트 경계값(`<=`→`<`)을 실거래
   게이트(`>=`)와 일치
4. `features/technical/hurst_exponent.py`의 미사용 헬퍼
   `classify_market_state()`/`hurst_with_regime_synergy()` 삭제(죽은 코드)

**미검증**: 4개 파일 문법 검사만 통과, 라이브 동작 미확인. 다음 기동 후
① 탈진 레짐 로그 시 Hurst 우회 실제 동작, ② backfill 재실행 시 hurst 분포
정합성 확인 필요.

**손대지 않은 것**: `hurst_exponent.py` `__main__` 자체테스트의 추세 시뮬레이션
데모 결함(결정론적 드리프트라 H≈0으로 나옴) — 프로덕션 미접촉, 순수 데모 가치라
사용자 판단으로 보류.

---

## 2026-07-07 (300차 — 루트/docs 문서·스크립트 정리)

**계기**: 루트와 `docs/`에 개발 초기부터 쌓인 계획서·리뷰·1회성 스크립트가
정리 안 된 채 남아있어 사용자가 정리 요청. planning mode로 범위를 확정한 뒤
승인받아 실행.

**한 일**:
- 루트에 `_archive/`(root_scripts/plans/sub_docs/docs) 신설 후 완료된 계획·리뷰
  문서와 1회성 진단 스크립트 이동, 죽은 중복 파일(`adaptive_kelly.py`·
  `hurst_exponent.py`·`Mouse.py`) 삭제, `backup_pull/` 삭제
- `CLAUDE.md`/`README.md`/`AGENTS.md`/`CORE.md`/`ENSEMBLE_SIGNAL_UPGRADE_PLAN.md`/
  `STRATEGY_PARAMS_GUIDE.md` 갱신 — 30m 호라이즌 퇴역·CB②/CB③-P4 한시 예외·
  Codex→Claude Code 전환 반영, PC 하드코딩 경로 제거
- `MIREUKI_OVERVIEW.md` 전면 재작성 (구식 2026-05-08 버전 → 299차 기준)
- 상세 내역은 `dev_memory/SESSION_LOG.md` 2026-07-07 (300차) 항목 참조

**미결 메모(액션 아님)**: `maitreya_dist` 브랜치 존치 여부, `docs/정기점검/
PERIODIC_INSPECTION_PLAN.md` 자동화 여부 — 다음 세션에서 결정 필요

---

## 2026-07-07 (299차 — docs/MW0601 대조 → EOD 리포터 코드버그 4건 구현)

**계기**: 사용자가 다른 PC(MW0601)에서 작성된 EOD 리포터 딥다이브 문서
(`docs/MW0601/`, 커밋 안 된 채 이 PC에 복사되어 있었음)를 이 PC(MW0602)와
대조 요청 → 4개 코드 레벨 버그가 이 PC엔 반영 안 된 채 그대로 있음을 확인 →
"MW0601 수준으로 개선 구현해" 요청.

**핵심 판단**: 이 PC(MW0602, `machine.cfg: BROKER=creon`)의 298차는 "활성
버전 이원화"(§1) 버그를 `data/db/strategy_registry.db`의 `is_current` 값만
정정하는 방식으로 막았는데, `main.py`/`hotswap_gate.py`가 여전히
`PARAM_HISTORY[-1]`을 registry와 별도로 읽는 **구조적 원인**은 그대로였다.
CUSUM 항목(298차 ③)도 "update() 호출은 있다"까지만 확인하고 "인메모리
싱글턴 재기동 리셋"으로 결론을 좁혔는데, 실제로는 `ref_mean=0.0/ref_std=1.0`
기본값이 한 번도 보정된 적이 없어 원화 손익이 그대로 z-score가 되는 게
근본 원인이었다(다른 PC의 독립 딥다이브가 이 부분까지 짚어냄). PSI(§6)와
stuck_exit_flat grade/entry_horizon(§3)은 이 PC에서 아예 다뤄진 적이 없었다.

**구현**:
- `main.py`(라이브 스냅샷 기록) + `strategy/ops/hotswap_gate.py`(다음 버전
  넘버링) — `registry.get_current_version()`을 유일한 활성 버전 소스로 통일.
- `main.py:_ts_resolve_stuck_exit_pending` — `grade`/`entry_horizon`을
  `pending`(EXIT 주문, 항상 빈값)이 아니라 `self.position`에서 읽도록 수정.
- `strategy/param_drift_detector.py` — `calibrate_from_live_history()` 신설,
  `get_drift_detector()` 싱글턴 생성 시 자동 호출. registry 실측 라이브
  이력으로 CUSUM `ref_mean`/`ref_std` 보정.
- `strategy/regime_fingerprint.py` — `_try_bootstrap_baseline()` 신설,
  `update_live()`에서 학습분포 없으면 Live 버퍼 50개 이상 쌓일 때 자동
  기준선 승격.

**검증**: 격리된 스크립트(`data/regime_fingerprint.json` 등 실 상태파일
미접촉)로 §5·§6 동작 확인 — PSI는 부트스트랩 전후 `has_training_data`
False→True 전환 및 분포이동 시 WATCHLIST→CRITICAL 정상 전환, CUSUM은 보정
전후 동일 손실액이 CRITICAL→CLEAR로 바뀜을 확인. 실제(읽기전용) DB로
`get_current_version()`이 `v1.0`/`live_days=32`를 정확히 반환함도 확인.
§1·§3은 코드 리뷰 + 이 읽기전용 확인 수준 — 실거래 흐름 자체는 라이브
미검증.

**남은 사항**: CUSUM 인메모리 영속화(298차 ③-a)는 이번 범위 밖으로 남음.
wr/pf DriftDetector의 `ref_std` 하한(1.0)이 0~1 스케일엔 과도하게 클 수
있다는 점도 미해결(상세는 `NEXT_TODO.md` 299차 참조). 다음 기동일 EOD
리포트로 라이브 검증 필요.

---

## 2026-07-06 (298차 — daily_exporter 딥다이브 → v1.2 유령버전 버그 발견·수정)

**계기**: 사용자가 daily_exporter EOD 리포트 4건(07-01~07-03, 07-06)을 비교
요청하며 이상점 딥다이브를 지시 — "버전 v1.2 (1일차)"가 4일 내내 고정인
것에서 출발해 DB까지 추적.

**핵심 판단**: `strategy_versions.is_current`가 가리키던 "v1.2"는
`scripts/qa_strategy_seeder.py --seed`가 2026-05-07 18:37 한 타임스탬프로
남긴 QA 더미 데이터였고, 실거래(05-08~) 일별 PnL은 전부 `config/strategy_
params.py`의 실제 PARAM_HISTORY를 따라 "v1.0"으로 기록되고 있었다. 그 결과
`_get_live_days()`가 v1.2의 단일 seed row만 세어 2달간 "1일차"에 고정 →
`_compute_verdict()`가 `live_days<5`면 무조건 INSUFFICIENT → 버전 판정·CUSUM
드리프트·권고 로직 전체가 실거래 32일치 성과를 전혀 반영 못 함.
`strategy_events` 로그 대조 결과 2026-05-08부터 거의 매 거래일 v1.2 기준
ROLLBACK_REVIEW/WATCH 액션이 이 phantom 데이터만으로 반복 기록돼 있었음.

별개로 CUSUM 드리프트 감시를 조사했는데, **최초 결론("배선 자체가 없다")은
오류였다** — `main.py:8310-8325`에 `get_drift_detector().update(daily_pnl=
forward_stats["pnl_krw"], ...)` 실호출이 존재한다(멀티라인 호출이라 최초
grep이 놓침, 정정 경위는 `DECISION_LOG.md` 298차 참조). 진짜 문제는
`MultiMetricDriftDetector`가 인메모리 싱글턴이고 디스크 영속화 로직이
없어서, 이 시스템처럼 매일 재기동되는 운영이면 CUSUM의 20거래일 누적이
매일 리셋될 수 있다는 것. 07-01 리포트의 `CUSUM CRITICAL (1181230.50)`은
조작이 아니라 그날의 실제 daily_pnl이 `ref_std` 하한(1.0) 때문에 그대로
z-score처럼 커져 찍힌 것으로 추정(ref_std 산정 로직 별도 확인 필요).

**조치**:
- `data/db/strategy_registry.db` 백업(`*.bak_20260706_220230`) 후 v1.1/v1.2
  관련 레코드(`strategy_versions`·`strategy_param_changes`·
  `strategy_stage_results`·`strategy_live_snapshots`) 전부 삭제, v1.0을
  `is_current=1`로 복원. v1.0의 2026-05-07 seed 오염 스냅샷(더미 55,000원)도
  제거 — 실거래는 05-08부터가 진짜 시작.
- `strategy_events`의 v1.2 태그 이력은 감사 기록으로 보존(삭제 안 함) — 그
  기간 이벤트는 phantom 데이터 기반 오판단이었다는 점을 감안해서 읽을 것.
- 코드 변경 없음(순수 DB 데이터 정리) — `main.py`의 `_active_ver =
  PARAM_HISTORY[-1]["version"]`는 이미 v1.0을 가리키고 있었으므로 원인은
  `strategy_versions.is_current` 쪽 데이터 불일치뿐이었음.

**검증**: 수정 후 `StrategyRegistry().get_current_version()` / `DailyExporter
().build_report()`를 실제 재실행 — 버전 v1.0(32일차), 판정 UNDERPERFORM
(Live MDD=58.6%, WFA 기준 14.2%보다 크게 나쁨), 롤링20일 누적 +6,136,142원,
권고 "🔄 교체 후보 탐색"으로 실제 상태가 처음으로 드러남.

**주의(미해결)**: `backup_pull/db/strategy_registry.db`는 손대지 않음 — 수정
전 상태(phantom v1.2)를 그대로 갖고 있어 `MW0602 pull guide.txt` 절차를
재실행하면 이 수정이 덮어써질 수 있음. **UNDERPERFORM 판정 자체는 버그가
아니라 처음 드러난 진짜 신호이므로, 다음 세션에서 반드시 검토할 것**
(`NEXT_TODO.md` 298차 항목 참조).

**병행 조사(미완)**: 사용자가 "dev-v9(`origin/v9-dev`) → MW0601 cherry-pick
문제 없나" 질문 → 격리 worktree에서 dry-run cherry-pick 테스트 진행 중
`config/settings.py` 충돌 지점에서 사용자 요청으로 중단(`dev_memory update`로
전환). 상세 진행상황은 `NEXT_TODO.md` 298차 항목 참조.

---

## 2026-07-06 (297차 — 진입0 딥다이브 + P0 배선버그 2건 수정 + 재발방지 계측 6종)

**계기**: 사용자가 금일 진입 0건의 원인 딥다이브와 260705 감사문서 개선안의
실효성 평가를 요청 → P0 긴급수정 2건 지시 → 감사 매트릭스 정정 지시 → P1
계측 2건 지시 → 추가개선안 2건 지시 → 딥다이브 결과 종합정리 문서화 지시.

**핵심 판단**: 오늘 진입0의 1차 원인은 conf 분포 하락(중앙값 31.5%, p90 35.5%
vs mc 36.5~37.5%) + Hurst 횡보 차단이지만, 딥다이브 과정에서 이 원인 분석과는
별개로 **실제 배선 버그 2건**을 발견했다 — (1) FQAdj의 min_conf 완화가 268차
이후 로그만 찍히고 실효 0으로 무효화(zone_mc가 앙상블 등급 결정에 반영 안 됨),
(2) CB③-P4가 296차 퇴역 확정된 30m 정확도를 계속 소비해 무관한 C등급까지 상시
차단(CB_ACC_RESTRICTED_MIN=0.30이 30m 확정 성능 0.3052와 거의 같아 상시 발동).
전자는 하루 271분 conf미달 중 상당수가 완화 대상이었을 수 있고, 후자는 296차
"하나의 퇴역이 여러 경로에 구멍을 남긴다"는 교훈이 CB③에서도 재현된 사례.

**조치**:
- `model/ensemble_decision.py`: 등급 결정 로직이 `zone_mc`(FQAdj 반영값)를
  RISK_ON/NEUTRAL에서 실제로 사용하도록 수정. RISK_OFF만 레짐 강화(`max`) 유지.
- `config/settings.py`: `CB3_P4_GRADE_BLOCK_ENABLED=False`(C등급 차단만 비활성,
  accuracy_buf 누적·acc30m_stage 추적은 유지) + `ENTRY_STARVATION_WEEKLY_MIN`/
  `ENTRY_STARVATION_MITIGATION_LADDER`(표본기아 완화 사다리 사전등록) +
  `MC_CONF_GAP_ALERT_*`(mc-conf 괴리 2단계 경보) +
  `VALIDATION_CAMPAIGN["hurst_gate_shadow"]`(Hurst counterfactual 판정기준).
- `CLAUDE.md`: 절대원칙 §2에 CB②와 동일 패턴으로 CB③-P4 예외 문서화(날짜
  있음) + Phase 5 진입조건 체크리스트 ⑥번(재검토 항목) 등록.
- `docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md`: §1 매트릭스 6b행
  신설(구형 MetaGate ON·하드차단 등재 — 신형 entry_quality_prob 섀도우와 이름
  충돌로 누락돼 있었음), §3-2b·§3-6·§3-7·§3-8 신설, §4-1·§4-2 갱신.
- `utils/db_utils.py`: `hurst_gate_shadow` 테이블(Hurst counterfactual),
  `fetch_entry_candidate_gap()`(mc-conf 괴리), `fetch_daily_entry_funnel()`
  (진입 퍼널 5단 재구성), `ensemble_decisions.coherence_blocked` 컬럼 신설
  (구현 중 발견: 기존엔 이 값이 DB에 없어 `grade=='X' & regime_ok==1`로
  역추정했더니 conf미달과 동시발생 케이스를 누락함을 로그 대조로 확인).
- `learning/prediction_buffer.py`: `coherence_blocked` STEP9 저장 배선.
- `scripts/generate_validation_campaign_report.py`: `resolve_and_eval_
  hurst_gate()`(§3-6 KPI), `eval_sample_starvation()`(§3-8 사다리 위치 자동
  판단 — Hurst 임계값 실측으로 3단계 적용 여부까지 자동 감지), 리포트 [0]·[6]
  섹션 추가.
- `strategy/ops/daily_exporter.py`: mc-conf 괴리 + 진입 퍼널 일일 섹션 추가.
- `scripts/run_microstructure_ab_backtest.py`: FQAdj 수정에 따른 회귀 방지
  (zone_mc 명시 전달).
- `docs/진입0/260706_진입0_딥다이브_및_개선구현.md`: 신규 — 딥다이브 전 과정과
  구현 6항목 종합 정리.

**유지되는 것**: CB③ 자체(절대원칙), Hurst 게이트 자체(추세추종 설계 핵심
필터), 구형 MetaGate 자체(§3-2b 판정 전까지 존치) — 이번 세션은 이들을
비활성/제거하지 않고 "퇴역된 30m을 계속 먹이던 소비 경로 1건"과 "완화가
무효화되던 배선 1건"만 고쳤다.

**검증**: `pytest tests/` 10건 통과, 수정 파일 전체 `py_compile` 통과. 신규
함수(hurst_gate_shadow resolve, entry_candidate_gap, daily_entry_funnel,
sample_starvation, coherence_blocked 저장)는 전부 실제 DB(오늘 데이터 포함)로
end-to-end 테스트, 합성 데이터로 STOP/TP1/NEITHER counterfactual 로직 수동
계산 대조 일치 확인(테스트 데이터는 정리함). **라이브 실기동 검증은 아직
없음** — 다음 기동 후 conf 분포 회복 여부(7/3 수준 복귀 — "모델 문제 vs 데이터
문제" 판별의 첫 근거)와 P0 수정 효과·신규 계측 로그 정상 출력을 확인해야 함
(`NEXT_TODO.md` 297차 항목 ①~⑧ 참조).

---

## 2026-07-06 (296차 — 30m 호라이즌 퇴역 최종 확정)

**계기**: 사용자가 금일 운영 점검 결과(EOD full_cv acc=0.3052, 290차가 사전 등록한
목표 0.38~0.41 미달)를 근거로 30m 퇴역을 지시.

**핵심 판단**: 292차에서 need_add 피처 8개(opt_gex_bn 등)를 registry에 반영하고
같은 날 15:46 EOD full_cv 재학습(26주·40,011행·105피처)까지 거쳤음에도 30m CV
acc=0.3052 — 260707 보고서의 재활성화 기준(≥0.33)과 290차 목표 구간(0.38~0.41)
모두 미달, 3클래스 랜덤(0.333)보다 낮다. "피처 부족"이라는 그동안의 가설이 이번
EOD로 최종 소진됐으므로 재활성화를 철회하고 영구 퇴역으로 확정.

**조치**:
- `model/ensemble_decision.py`: `compute_cascade_coherence()` cascade 목록에서
  30m 제거, CoherenceGate `_active_h` 분모에서도 30m 제외(`_bias_overrides`에 추가).
  기존에 이미 가중합에서는 무조건 0으로 강제되고 있었으나(`cur_weights["30m"]=0.0`,
  250차), 그 우회로였던 이 두 게이트는 이번에 처음 차단.
- `config/settings.py`: `ENSEMBLE_WEIGHTS`/`ENSEMBLE_WEIGHTS_CORR_ADJ`의 30m을 0.0
  으로 명시(런타임은 이미 강제 0이었으나 설정값을 실제와 일치시킴), 나머지 5개
  호라이즌에 +0.03씩 균등 재분배(합 1.00 유지, `runpy`로 실측 검증 완료).
- `safety/circuit_breaker.py`: CB③ 30m HALT 비활성화 주석을 "296차부로 영구"로 갱신
  (기능 변경 없음 — 250차부터 이미 비활성).
- `docs/260707_FEATURE_ADD_TIMING_REPORT.md`: 재활성화 조건 섹션 위에 296차 최종
  판정 추가, 조건 미충족 확정 기록.
- `ROADMAP.md`: "260704 감사 로드맵 — 30m 호라이즌 퇴역 심사" 체크리스트 마지막 항목
  완료 처리 + 296차 최종 확정 서브섹션 추가.

**유지되는 것**: predict_proba·GBM/RF 학습·CB③ P4 stage 모니터링은 연구/재평가용으로
계속 유지 — 퇴역은 "의사결정 반영 차단"이지 예측/학습 중단이 아님.

**검증**: `py_compile` 3개 파일 통과, `runpy`로 `config/settings.py` 실행해
`ENSEMBLE_WEIGHTS`/`ENSEMBLE_WEIGHTS_CORR_ADJ` 합계 1.0 확인. **라이브 실기동
검증은 아직 없음** — 앱이 꺼져 있는 상태에서 소스만 수정. 다음 기동 후 CascadeCoherence
/CoherenceGate 로그에서 30m 노이즈로 인한 오차단이 사라지는지 확인 필요(`NEXT_TODO.md`
296차 참조).

---

## 2026-07-06 (295차 — KOSPI200/VKOSPI 폴링 수정 완료: `dscbo1.StockMst` → `CpSysDib.MarketEye`)

**계기**: 294차에서 준비한 `probe_cp_market_eye.py`를 사용자가 관리자 권한 셸에서 실행, 정상 조회 확인.

**핵심 발견**: `CpSysDib.MarketEye`에 기존 코드(K2G01P/O2901P) 그대로 조회하니 종목명·현재가가 정상 반환됨(코스피 200=1291.43, 코스피200 변동성=86.54, 대조군 삼성전자도 일치) — 코드는 처음부터 맞았고 `dscbo1.StockMst`가 지수 자체를 지원 안 하는 TR이었다는 294차 결론이 최종 확정.

**조치**: `collection/cybos/api_connector.py:1032`의 `get_index_price()`를 `CpSysDib.MarketEye` 기반으로 재작성 완료(`py_compile` 통과, 호출부 시그니처 동일해 다른 파일 변경 불필요).

**남은 일**: 이 수정은 소스 파일 변경일 뿐 **현재 실행 중인 main.py 프로세스에는 아직 반영 안 됨** — 다음 재기동 후 `[CybosIndex] 종목명 검증 실패` 로그 소멸 및 `basis_ready`/`vkospi_ready` 전환 확인 필요(`NEXT_TODO.md` 참조).

---

## 2026-07-06 (294차 — KOSPI200/VKOSPI: `dscbo1.StockMst` 지수 미지원 확정, `CpSysDib.MarketEye` 전환 검증 대기)

**계기**: 293차 "U180 코드 후보" 가설을 사용자가 관리자 권한 셸에서 직접 검증.

**핵심 발견**: `U180`/`K2G01P`/`O2901P` 전부 `dscbo1.StockMst`에서 `71103 조회결과가 없습니다`로 동일 실패, 대조군 `A005930`(삼성전자)은 정상 응답 — **`dscbo1.StockMst`는 코드 형식과 무관하게 지수를 아예 지원하지 않는 개별종목 전용 TR**로 확정. "코드가 틀렸다"는 293차 가설은 폐기, "TR 선택이 틀렸다"가 결론.

**다음 후보**: `CpSysDib.MarketEye`(주식·지수·선물옵션 통합 조회, 문서상 지수 지원 명시) — 진단 스크립트 `scripts/probe_cp_market_eye.py` 작성 완료, 사용자의 관리자 권한 실행 결과 대기 중. 확인되면 `get_index_price()`를 StockMst 기반에서 MarketEye 기반(`SetInputValue(0, field_id_list)` + `SetInputValue(1, code_list)` + `GetDataValue(pos, row)`)으로 재작성 예정.

---

## 2026-07-06 (293차 — KOSPI200/VKOSPI 폴링 100% 실패 조사: U180 후보 확보, 라이브 검증은 미완)

**계기**: 292차에서 발견한 `_poll_kospi200_index()` 100% 실패 버그 딥다이브.

**핵심 발견**: `K2G01P`/`O2901P`(현재 코드)는 실제 KRX 표준 업종지수 코드가 맞지만(stockplus.com 확인), Cybos Plus의 `dscbo1.StockMst` COM TR은 대신증권 자체 "U"-prefix 코드 체계(KOSPI200=**U180**, 웹 검색 2건 확인)를 기대하는 것으로 추정 — GUI 종목코드검색 표시 코드와 COM API 입력 코드가 다를 수 있다는 것이 가장 유력한 가설.

**막힘**: `scripts/probe_cp_stock_mst.py`(신규 진단 스크립트)로 실제 검증 시도했으나 이 세션 셸이 비관리자 권한이라 `CpUtil.CpCybos.IsConnect=False`로 COM 연결 자체가 거부됨 — 라이브 main.py/Cybos Plus는 관리자 권한으로 실행 중인 것으로 추정.

**코드 변경 없음**: 확인 안 된 값으로 임의 교체하지 않음. 사용자가 관리자 권한 셸에서 `probe_cp_stock_mst.py --code U180`을 직접 실행해 검증 필요(`NEXT_TODO.md` 292차 ④).

---

## 2026-07-06 (292차 — 진입0/conf<mc 딥다이브 → 옵션체인 등 8개 피처 registry 반영)

**계기**: 7/6 진입 0건 + conf<mc 반복 원인 딥다이브 요청.

**핵심 발견**: 30m(+15m/10m/5m) 모델의 `acc30m`이 0~23.3%(랜덤 이하)로 붕괴된 근본 원인은 `opt_chain_pcr`/`opt_gex_bn` 등 옵션체인 파생 피처와 `micro_regime_code`·`queue_directional_depletion`·`threshold_feasibility`가 문서(`docs/260707_FEATURE_ADD_TIMING_REPORT.md`)상 이미 활성화 예정/완료로 기록됐음에도 `data/db/shap_feature_registry.json`의 `active_features`에는 실제로 반영되지 않은 채 방치된 것. 실측 결과 8개 모두 4,000행 활성화 기준을 이미 초과(최대 micro_regime_code 4,933행, queue_directional_depletion 6,693행, threshold_feasibility 7,561행).

**조치**: `active_features` 97→105개로 확장, `horizon_feature_sets.json` 15개 호라이즌별 `pkl` 태그 정정. `batch_retrainer.py`가 재학습마다 registry를 디스크에서 새로 읽으므로 다음 자동 재학습부터 반영(라이브 프로세스 무중단).

**미해결(별건)**: 7/4 신규 추가된 KOSPI200/VKOSPI 실시간 폴링(`main.py:2701` `_poll_kospi200_index()`)이 7/6 하루 종일 100% 실패(`[CybosIndex] 종목명 검증 실패`) — `NEXT_TODO.md` 292차 ④ 참조.

**다음 확인 필요**: acc30m 회복 여부, EOD full_cv 재학습 후 30m 역방향 필터/CB③ 재활성화 조건(CV acc≥0.33) 충족 여부(`NEXT_TODO.md` 292차 ①~③).

---

## 2026-07-05 (290차 — 260704 종합감사 실행 로드맵 P0~P3 전체 구현)

**계기**: `docs/260704_SYSTEM_AUDIT_UPGRADE_PROPOSAL.md` §8 실행 로드맵을 P0→P1→P2→P3
순서로 단계별 구현(사용자가 매 항목 확인 후 다음 진행 지시).

**핵심 결과**: P0~P3 전 항목 구현 완료(탭 15개→4그룹 재편만 headless 환경 시각확인
불가로 사용자 직접 진행으로 보류). 상세 내역·검증 방법은 `ROADMAP.md`의 "260704 감사
로드맵 — ..." 각 섹션과 `SESSION_LOG.md` 290차 항목 참조. 이 세션에서 새로 발견한
중요 사실들:

1. **`strategy/exit/exit_manager.py`는 실거래 미사용 죽은 코드** — 실제 청산 로직은
   `main.py:_check_exit_triggers()`/`_ts_check_exit_triggers()`에 인라인 구현되어
   있음. 감사 보고서가 이 죽은 파일을 근거로 "트레일링 갱신 순서" 결함을 지적했으나,
   실제 코드는 이미 정상(트레일링이 하드스톱/TP/시간청산보다 항상 먼저 갱신)이었음 —
   **감사가 죽은 코드를 보고 오판한 사례**.
2. **`CHAMPION_BASELINE_ID`는 자체 shadow 거래 이력이 없는 콜드스타트 구조** —
   `challenger_engine.py`가 5개 variant만 등록하고 챔피언 자신은 등록하지 않음. 최초
   승격 전까지 부트스트랩/heartbeat 판정이 "표본부족"만 반환하는 것이 정상.
3. **30m need_add 피처(opt_gex_bn 등)가 실은 이미 수집 중이었다** — `horizon_feature_sets.json`
   표시(need_add)만 stale. 진짜 원인은 `learning/batch_retrainer.py:_retrain_phase2()`가
   호라이즌별 학습피처명을 "가장 키가 많은 단일 행"으로 잘못 결정하던 버그(합집합으로
   수정) — 30m뿐 아니라 옵션체인 피처를 쓰는 전 호라이즌에 잠재적 영향.
4. **KOSPI200 지수 코드는 네임스페이스에 따라 다르다** — `dscbo1.StockMst`(일반시세)엔
   `K2G01P`, 선물차트 문맥엔 `00800`. 처음 00800으로 구현했다가 사용자 2차 스크린샷으로
   정정. VKOSPI는 `O2901P`.
5. **`Dscbo1.CpSvr8111`(프로그램매매) 기존 필드매핑이 틀려 있었다** — guess 매핑(idx0~5)을
   공식문서 기준(idx19/37)으로 재작성, 입력값도 `ord('1')` 관례로 수정. 사용자가 관리자
   권한 Creon Plus 세션에서 실측 검증.
6. **이 headless 개발 세션에서도 PyQt 대시보드를 `QT_QPA_PLATFORM=offscreen`으로 실제
   생성해 스모크테스트할 수 있다** — 이전엔 "GUI라 확인 불가"로 가정했던 게 틀렸음.
   레이아웃/가독성까지는 확인 못 하지만 위젯 생성·업데이트 로직은 검증 가능.

**부수 사고(내 실수) — position_state.json 오염**: P2 검증 스크립트가
`PositionTracker()`(운영 앱과 동일한 저장 경로 공유)로 직접 `open_position()`을 호출한 뒤
`force_flat()`을 누락 — 가짜 LONG 100.00 포지션이 파일에 남아 실제 운영 대시보드에
노출됨(사용자 스크린샷으로 발견, 실제 브로커는 FLAT 확인 후 `force_flat()`으로 복구).
재발방지 메모리 기록. 곁가지로 `PositionRestoreDialog`의 진입가 스핀박스 clamp 버그
(`setRange(100.0,...)` + `setValue(0.0)` → Qt가 100.0으로 조용히 clamp)도 발견·수정.

**검증**: `py_compile` 전체 통과, `pytest tests/` 전체 통과(세션 시작 전부터 있던 무관
실패 1건 제외), 신규 스크립트들은 개발DB 실측 검증, 챌린저 관련은 합성DB 검증,
대시보드는 offscreen 스모크테스트. Cybos TR 3종(프로그램매매·외국인선물·지수시세)은
사용자가 관리자권한 세션에서 실측 검증. **지정가 우선 집행은 이 개발환경에서 실브로커
검증 불가 — 기본 OFF, 모의투자에서 사용자 수동검증 필요**(`NEXT_TODO.md` 290차).

**변경 파일**: 24개 기존 파일 수정 + 신규 파일 다수(`features/technical/basis.py`,
`features/technical/expiry.py`, `learning/meta_label_classifier.py`,
`learning/quantile_regressor.py`, `challenger/variants/champion_tp1_skip_trail.py`,
`scripts/analyze_mae_mfe.py` 등). 전체 목록은 `SESSION_LOG.md` 290차 참조.

---

## 2026-07-03 (289차 — 틱 단위 하드스톱 AttributeError 수정: is_halted() → state != CB_STATE_HALTED)

**계기**: [266차] 틱 단위 하드스톱 감지 기능이 실제로 발동하는지 점검.

**핵심 발견**: `main.py:2747`(틱 콜백)과 `main.py:3580`(S0-C 소비부)이 `CircuitBreaker` 클래스에 존재하지 않는 `is_halted()` 메서드를 호출 — 동명 메서드는 별개 클래스인 `strategy/profit_guard.py`에만 존재. 매 틱마다 AttributeError로 스킵되어 틱 하드스톱 감지가 사실상 무력화 상태였음.

**수정**: 코드베이스에서 이미 쓰이던 `self.circuit_breaker.state != CB_STATE_HALTED` 패턴으로 두 지점 교체(`config.constants`의 `CB_STATE_HALTED`는 이미 import되어 있어 추가 작업 불필요).

**검증**: `py_compile`(py37_32) 통과. **실거래/모의투자에서 틱 하드스톱 실제 발동 여부는 미검증** — `NEXT_TODO.md` 289차 참조.

**변경 파일**: `main.py` (코드 수정은 288차 커밋 `fec17c4`에 이미 반영됨, 이 항목은 사후 문서화).

---

## 2026-07-03 (288차 — SGD 온라인학습 구조 재설계: 콜드스타트 루프 제거·봉단위 dedup·레이블 재보정·피처/클래스 분리·비활성 호라이즌 명시)

**계기**: 자가학습 UI에서 1m/3m/5m/10m가 "미학습 0건"으로 표시된 것을 계기로 딥다이브 → SGD가 GBM과 레이블 정의·피처셋·학습주기를 공유하면서 생긴 구조적 문제 5개를 순차 발견·수정.

**핵심 발견**:
1. GBM 장중 재학습(하루 최대 23회)마다 `online_learner.reset_daily()`가 호출돼 SGD 표본이 `_MIN_SAMPLES=15`를 넘기지 못하고 매번 리셋되는 **영구 콜드스타트 루프**.
2. 30m은 매분 학습하는데 인접 표본의 30분 수익률 윈도우가 29/30 겹쳐 사실상 같은 레이블을 반복 주입 — SGD 단방향 붕괴(오늘 8회)의 구조적 원인.
3. 고정 `HORIZON_THRESHOLDS`(GBM 학습 레이블)가 5주 전 재보정 이후 변동성 확대로 드리프트해 실측 FLAT 18.6~25.5%(목표 34% 미달) — 반면 rolling σ(실시간 검증·SGD 레이블)는 매분 재계산돼 자연 추종 중이었음. 두 정의가 벌어져 있었음.
4. 호라이즌별 피처 IC 실측 결과 최고 IC가 1m 0.039~30m 0.198 수준 — SGD가 GBM과 같은 11~15개 피처(비선형 상호작용 전용 포함)를 선형으로 쓰는 게 오히려 잡음을 늘림.
5. 1m(신호 사실상 0)·15m/30m(독립 학습표본 하루 13~26건)는 온라인학습이 기여할 수 없는 구조 — 계속 붙잡고 있는 게 오히려 앙상블을 오염시킬 위험.

**결정 및 구현 (P0~P5, 상세는 `SESSION_LOG.md`/`DECISION_LOG.md` 288차)**:
- P0: 재학습 시 `reset_daily()` 제거 (콜드스타트 루프 차단)
- P1: 호라이즌별 봉단위 dedup (레이블 해머링 차단)
- P4: `HORIZON_THRESHOLDS` 재보정 + `ThresholdRecalibrator`를 21거래일 롤링 윈도우로 수정(기존엔 11개월 전체 평균이라 반대방향 경보를 냈었음) + `SGD_FULL_RESET_PENDING=True` 예약
- P2: SGD 전용 피처셋(`SGD_FEATURE_NAMES_BY_HORIZON`, IC 상위 5개) 분리
- P3: SGD를 3클래스→UP/DN 이진분류로 전환, FLAT은 GBM/threshold 몫으로 완전히 넘김
- P5: `SGD_BLEND_DISABLED_HORIZONS={1m,15m,30m}` — 학습은 계속하되 앙상블 블렌딩에서 제외("정직한 손절")

**검증**: 컴파일 전체 통과, `ThresholdRecalibrator` 재실행 검증(FLAT 정상범위 복귀), `OnlineLearner` 단위 스모크 테스트 다수 통과. **실거래 파이프라인 통합 실행(장중)은 미실시** — `NEXT_TODO.md` 288차 검증 항목 필요.

**변경 파일**: `config/settings.py`, `main.py`, `learning/online_learner.py`, `learning/threshold_recalibrator.py`, `dashboard/main_dashboard.py`, `docs/정기점검/LABEL_THRESHOLD_RECALIBRATION_GUIDE.md`(신규 — 레이블·threshold 파라미터 검토주기·재설정 가이드).

---

## 2026-07-03 (287차 — 청산 완료 후 브로커 잔고 1계약 잔존 사고 딥다이브 + 하드스톱·시간청산 pending 선등록 수정)

**계기**: 사용자가 "[청산 완료] PnL=-0.19pt" 로그가 찍힌 뒤에도 UI 실시간 잔고에 1계약이 남아있는 것을 발견 — 딥다이브 요청.

**로그 재구성**: 13:20:01 LONG 8계약 진입(주문 4165) 후 13:28:01 SHORT 청산(주문 4265) 진행 중 7건의 부분체결이 전부 `사유=미추적체결(pending_miss)`로 처리됨 → 마지막에 별도 하드스톱 주문(4331)이 1계약을 추가로 매도하며 "청산 완료" 기록.

**근본 원인**: `_execute_partial_exit`(TP청산, `main.py:9295-9296`)와 수동청산(`main.py:2020-2021`)은 "BlockRequest() 내부 메시지 펌프로 체결 콜백이 주문 전송 도중 먼저 도착하는 race condition"을 막기 위해 `_set_pending_order()`를 주문 전송 **전에** 먼저 호출하도록 이미 수정되어 있었으나, **하드스톱**(`main.py:9362` 부근)과 **15:10 시간청산**(`main.py:9413` 부근)은 이 수정이 누락된 채 `_send_broker_exit_order()`를 먼저 호출하고 그 반환 후에야 `_set_pending_order()`를 호출하고 있었음. 하드스톱 주문 도중 체결 콜백이 먼저 도착하면 `self._pending_order`가 아직 None이라 `_ts_handle_external_fill`("미추적체결/pending_miss")로 새고, 그 사이 `self.position.quantity`가 내부적으로 계속 줄어든 뒤 뒤늦게 낮아진 수량으로 pending이 등록됨. 이 시점에 같은 스톱히트 조건이 재평가되면(`_has_pending_order()` 가드가 그 사이엔 무력함) 중복 청산 주문이 한 번 더 나가 브로커에 잔고가 남게 됨.

**수정** (`main.py:9362-9396` 하드스톱, `main.py:9413-9445` 시간청산): 두 경로 모두 `_set_pending_order()`를 `_send_broker_exit_order()` 호출 **전으로** 이동. 수량/방향을 로컬 변수로 먼저 캡처해 콜백 도중 값이 바뀌어도 주문 크기가 흔들리지 않게 함. 주문 실패(`ret != 0`) 시 `_clear_pending_order()` 롤백도 추가(기존엔 실패해도 pending을 정리하지 않았음).

**미검증**: 실거래/모의투자 환경 접근 불가로 코드 수정만 완료 — 다음 장중 하드스톱 또는 15:10 시간청산이 실제로 발동하는 케이스에서 (a) 체결 콜백이 정상적으로 pending에 매칭되어 "미추적체결(pending_miss)"이 더 이상 뜨지 않는지, (b) 중복 청산 주문이 재발하지 않는지 로그 확인 필요.

**변경 파일**: `main.py`.

---

## 2026-07-03 (286차 — stuck exit 손익 quantity배 부풀림 버그 딥다이브 + 수정)

**계기**: 285차 백테스트 중 발견한 `exit_reason='stuck_exit_flat'/'stuck_exit_remainder'` 3건(최대손실 -1,227,356원 포함, grade 공백·계약수 이상)을 별도 딥다이브 요청.

**원인**: 분할체결 콜백 일부 누락 + 브로커 FLAT 확인 시 발동하는 `_ts_resolve_stuck_exit_pending()`(`main.py:10173`)이, 부분체결 집계 함수 `_ts_agg_exit_fill()`(`main.py:9824-9838`, per-contract pnl_pts를 fill_qty로 가중합산해 누적)의 결과 `agg_exit_pnl_pts`를 **체결수량(`agg_qty`)으로 나누지 않고** 그대로 `_record_trade_result()`에 pnl_pts로 넘김. 이 값이 `normalize_trade_pnl()`(`utils/db_utils.py:98`, `gross_pnl_krw = pnl_pts × pt_value × quantity`)에서 quantity와 다시 곱해져 **손익이 정확히 quantity배로 부풀려짐**. 정상 경로인 `_ts_build_agg_exit_result()`(`main.py:9841-9857`)는 이미 `raw_pts / agg_qty`로 정상 나눗셈을 하고 있어(주석에도 명시) 이 폴백 경로만 빠뜨린 것.

**검증**: `normalize_trade_pnl()` 직접 호출로 재현 — 07-01 13:00 LONG 6계약(5건 집계) 버그값 -5,987,676원(실제 DB와 원 단위 일치), 수정 후 -1,205,676원(로그 수기합산 -1,205,675원과 일치). 07-01 11:42 SHORT 2계약도 동일 검증(-1,227,356원 → -615,686원).

**수정**: `main.py:10206-10221, 10250` — `_sq_pnl_pts`/`_sq_fwd_pts`를 `_sq_filled`로 나눠 per-contract 값으로 복원 후 사용.

**미해결**: `trades.db`의 과거 오기록 3건(06-22 13:23, 07-01 11:42, 07-01 13:00) 보정 여부 — 일일 통계 파생값과의 정합성 우려로 사용자 확인 후 별도 진행 결정 대기 중.

**변경 파일**: `main.py`.

---

## 2026-07-03 (285차 — 앙상블 CoherenceGate·체크리스트 등급 이중판정 딥다이브 + C등급 이중차단 규칙 추가)

**계기**: 11:45 SHORT 진입(-5.24pt 손실)이 장중 재시작(11:39) 직후 발생 — 재시작 직후 불안정한 상태에서 어떻게 진입이 가능했는지 딥다이브 요청.

**딥다이브 결과**: 재시작으로 `OnlineLearner`(SGD)·호라이즌 완성봉 캐시(`_hz_feat_cache`)·`HorizonDecorrelator`/`F1AdaptiveWeight` 가중치가 전부 인메모리 상태라 초기화됨(디스크 저장/복원 코드 없음). Restart Armistice(90초+브로커 sync 2회)는 정상 해제됐지만 이 상태는 체크 대상이 아님. 실제 11:45 신호는 앙상블 자체가 CoherenceGate(호라이즌 방향 비합의, `ensemble_decision.py:754-807`)로 `grade=X` 판정했음에도, STEP7 체크리스트(`checklist.py`)가 독립적으로 재평가해 C등급(268차-P4 CVD+OFI 동시역행 강등)으로 `auto_entry`를 허용해 체결됨 — 두 게이트가 서로의 판정을 전혀 참조하지 않는 구조였음(`main.py:5456` 진입조건엔 `direction`/`position`만 있고 `grade`는 없음).

**백테스트(5/8~7/3 전체)**: `ensemble_decisions`에서 `grade='X' AND checklist_reason LIKE 'Coherence%'`(196건 후보) → `trades.db` 실체결 매칭(`MANUAL`·`stuck_exit_*` 이상거래 제외, 순수 표본 15건). **체크리스트 A/B등급 14건은 13승1패(+378만원, 승률92.9%)**로 견조했으나 **C등급은 유일 표본(오늘 11:45)이 손실(-26만원)**. "앙상블 X면 무조건 차단"은 A등급 우수 표본을 죽이므로 기각, "coherence_blocked + 체크리스트 C등급 동시발생"만 좁게 타겟팅.

**구현**: `main.py:5633-5644` — CB③-P4 C등급차단 블록 바로 뒤에 `[285차-P5]` 규칙 추가. `_final_grade=="C" and decision.get("coherence_blocked")`일 때만 `_final_grade="X"`로 강제. A/B등급, coherence 정상인 C등급은 영향 없음.

**부가 발견(미조치)**: 백테스트 매칭 중 `exit_reason='stuck_exit_flat'/'stuck_exit_remainder'`(대량계약·grade 공백) 3건이 이 기간 최대 손실(-1,227,356원 포함)을 낸 것 확인 — 오늘 논의와 무관한 별도 청산 메커니즘 버그로 추정, 별도 딥다이브 필요(사용자 확인 대기).

**변경 파일**: `main.py`. **미검증**: 다음 장중 C등급+coherence_blocked 동시발생 시 `[P5]` 로그 확인, A/B 자동진입 영향 없음 확인 필요 — `NEXT_TODO.md` 285차.

---

## 2026-07-03 (284차 — OPEN_VOL 시가이격 gap_chk N/A 재발 오인 조사 → 표시 상태 4분리)

**계기**: 사용자가 패널에서 `OPEN_VOL 시가이격` = N/A 확인 → 281차(`c7a8cdd`)에서 고친 버그의 재발 의심.

**조사 결과 — 재발 아님**: 281차 픽스(`self._session_open_price` 3경로 대입)는 오늘도 정상 작동(`logs/20260703_SYSTEM.log` 08:53 프리장 캡처, 11:39 재시작 복원 확인, `session_state.json today_open=1231.0`). 사용자가 본 N/A는 ATR=2.77pt가 찍힌 **11:58**(`time_zone=OTHER`, OPEN_VOLATILE 구간 09:05~10:30 밖) 시점 — 필터 미적용이 정상 표시된 것. 문제는 "필터 버그로 인한 N/A"와 "필터 미적용이라 N/A"가 화면상 구분 불가능했던 것.

**수정** (`main.py:6258-6265`): `_gap_chk_val`을 4개 상태로 분리.
- `time_zone != OPEN_VOLATILE` → `구간외` (09:05~10:30 전용)
- 구간 내 + `entry_mode != TREND_FOLLOW` → `모드외(TREND_FOLLOW Only)` (MR은 이격 자체가 진입 조건이라 필터 제외)
- 구간 내 + TREND_FOLLOW + 시가 미캡처(`_session_open_price<=0`) → `N/A (시가 미캡처)` — 이제 이것만 진짜 이상 신호
- 전부 충족 → 실제 이격 `{pt}pt` 표시

`dashboard/main_dashboard.py:3918-3925` 툴팁도 4개 상태 설명 동기화.

**변경 파일**: `main.py`, `dashboard/main_dashboard.py`. `_checks_ui["gap_chk"]`(V/X 아이콘용 boolean `_open_gap_ok`)는 별도 로직이라 미변경.

---

## 2026-07-03 (283차 — 증거금 미반영 진입거부 사고 딥다이브 + 재발방지 2건)

**결론**: 10:28:59 LONG 3계약 A급(체크리스트 9/9, 전체 게이트 통과) 신호가 `[진입체크]`
로그까지 찍혔는데 미체결 → 로그 추적 결과 `CpTd6831`(선물주문) `BlockRequest()`가
`ret=-1`로 거부(타임아웃 아님). 최대허용수량(대시보드 설정)만 반영했을 뿐 실제 계좌
증거금은 전혀 확인하지 않고 산출수량을 그대로 주문에 실었던 것이 원인. 추가로 거부
사유(GetDibStatus/GetDibMsg1)를 남기던 로그가 `logging.getLogger(__name__)`(파일
핸들러 미연결)로만 기록돼 SYSTEM/TRADE/WARN/DEBUG 어디에도 남지 않았던 것도 확인.

**구현 (사용자 요청 2건)**:
1. `collection/cybos/api_connector.py`의 주문 실패 로그를 `system_logger`로 교체해
   ret/status/msg가 SYSTEM.log에 남도록 수정 + `get_last_order_error()` 신설.
2. CYBOS `CpTd6722`(선물 신규주문가능수량조회) 신규 연동 — `_ts_margin_capped_qty()`가
   최대허용수량 클리핑 직후 실제 증거금 기준 가능수량으로 산출수량을 한 번 더 캡핑
   (0이면 진입 차단). 대시보드 "진입 수량" 카드에 `qty_entry_final` 파라미터를 신설해
   실제 진입에 쓰이는 최종수량을 그대로 표시.

**코드 수정**: `collection/cybos/api_connector.py`, `collection/broker/cybos_broker.py`,
`collection/broker/base.py`, `main.py`(`_ts_margin_capped_qty`, `_qty_auto` 산출부,
`_ts_execute_entry`), `dashboard/main_dashboard.py`(`EntryPanel.update_data`).

**미해결/범위 외**: `CpTd6722` 실거래 환경 첫 호출 시 실제 반환값(입력 필드·출력 인덱스)
검증 미실시 — 공식 문서(cybosplus.github.io) 기준으로만 구현. 다음 장중 A급 자동진입
발생 시 `[EntrySendResult]` status/msg 및 "진입 수량" 카드 확인 필요 — `NEXT_TODO.md`
283차.

---

## 2026-07-02 (281차 — start_mireuk.bat 15:10 이후 재시작 완전 차단 → CHOICE Y 확인 재시작 허용)

**결론**: 사용자 보고 로그(`launcher_20260702_084001_12594.log`)에서 08:40(장전) 기동
세션이 390분 실행 후 15:10 근처에 종료됐는데, `_debug_afterhours` 플래그가 없다는 이유로
무조건 "재시작 안 함" 처리된 것 확인. 이 플래그는 272차(`37e35c1`)에서 **배치 최초 실행
시각**이 15:10 이후일 때만 설정되므로, 장전/장중에 시작해 하루 종일 돌다 15:10 근처에서
디버깅 등으로 죽은 세션은 애초에 플래그를 가질 수 없어 정상 EOD 종료와 디버깅 크래시를
구분하지 못하는 구조적 공백이었음.

RESTART_LOOP 내부 15:10 체크를, 최초 "장후 실행" 프롬프트와 동일한
`CHOICE /C YN /T 10 /D N` 패턴(10초 후 기본 N, 오버나이트 금지 기본값 유지)으로 교체 —
`_exit_normally` 정상종료 플래그가 없는 상태에서 15:10 이후 종료 시 "의도적 재시작입니까?"
확인 후 Y면 `_debug_afterhours`를 생성해 계속 재시작, N/타임아웃이면 기존과 동일하게 종료.

**주의 (재확인)**: 첫 구현에서 `IF (...)` 블록 안에 `GOTO :restart_done`을 그대로 넣었다가
`feedback_cmd_bat_patterns.md`(MW0602 실전 버그: 괄호 블록 내 GOTO가 CMD jump table을
오염시켜 이후 모든 GOTO가 엉뚱한 위치로 점프)와 동일한 패턴임을 인지하고 즉시 수정.
`_AFTERHOURS_DENY` 플래그 변수로 우회해, GOTO는 항상 괄호 밖 단일행
(`IF DEFINED _AFTERHOURS_DENY GOTO :restart_done`)에서만 실행되도록 재구성.

**코드 수정**: `start_mireuk.bat` RESTART_LOOP 내 15:10 체크 블록 (Step 7,
`data\_exit_normally` 확인 직후). `LAUNCH_API.bat`는 이 재시작 루프 자체가 없어 영향 없음.

**미해결/범위 외**: 같은 루프의 "재시작 5회 초과" 분기(`IF !_RESTART_CNT! GTR 5 (...GOTO
:restart_done...)`)도 동일한 괄호-내-GOTO 패턴을 쓰고 있으나 기존 코드라 이번 범위에서는
손대지 않음 — 실전에서 5회 초과 시나리오가 실제로 걸렸을 때 jump table 오염 재발 여부
확인 필요. **실기동(장중 크래시 후 15:10 경과 + 수동 Y 응답) 검증 필요** —
`NEXT_TODO.md` 281차.

---

## 2026-07-02 (273차 — PYTHON_64_EXEC PC별 경로 하드코딩 수정)

### 배경

사용자 보고: 14:39~14:45 자동진입 반복 차단(`degraded_conf=39%, min=62%`) + 대시보드 "역방향 진입" 버튼 깜빡임. 로그 추적 결과 두 증상 모두 동일 근본 원인.

### 근본 원인

`config/settings.py`의 `PYTHON_64_EXEC`가 `C:\Users\82108\anaconda3\envs\py310_64\python.exe`로 하드코딩되어 있었음(다른 PC 사용자 경로). 이 PC(`pc1`)에서는 장중 GBM 경량 재학습(`DriftRetrain`)이 트리거될 때마다 `FileNotFoundError`로 즉시 실패 → `[GBM-64] py310_64 Python 없음` ERROR 반복 → `exception_density_10m` 급증 → Health Degraded Mode 자동 진입(최소신뢰도 0.62 요구) → 실제 신뢰도 39%대 신호가 전부 차단됨. 동시에 acc30m이 13%대까지 붕괴하면서(재학습 실패로 자가교정 불가) ContrarianModeTracker가 ACTIVE로 전환되어 "역방향 진입" 버튼 깜빡임 발생(이 자체는 의도된 경고 UI).

### 수정 (커밋 예정)

| 파일 | 변경 |
|---|---|
| `config/settings.py` | `PYTHON_64_EXEC` → `os.environ.get("MIREUK_PYTHON_64_EXEC", os.path.join(os.path.expanduser("~"), "anaconda3", "envs", "py310_64", "python.exe"))` |

### 상태

| 항목 | 상태 |
|---|---|
| 경로 하드코딩 제거 | **완료** — 홈 디렉토리 기준 동적 해석 + env override |
| 이 PC(`pc1`) 검증 | **완료** — 해석된 경로에 python.exe 존재 확인 |
| 다른 PC(`82108`) 실기동 검증 | **미완료** — 다음 그 PC 기동 시 GBM-64 ERROR 미발생 확인 필요 |
| dev_memory 265~272차 공백 | **미해결** — git log에는 존재하나 dev_memory 4종 파일 미기록, 별도 백필 여부 미결정 |

### 관련 문서

- 상세 로그 재구성: `SESSION_LOG.md` 273차 항목
- 동일 패턴 선례: `register_eod_scheduler.ps1` PC별 경로 하드코딩 (커밋 `ba07c46`, `.gitignore` 처리)
## 2026-07-02 (280차 — 자가학습 탭 표시 버그 4종 수정)

**결론**: 사용자가 중간패널 "🧠 자가학습" 탭 스크린샷에서 지적한 4가지 이상점을 조사 후 모두
수정. ① 1분/3분/15분/30분이 "미학습" 배지인데 학습 건수(2·35·78건 등)가 남아있던 원인 —
`sgd_fitted`(현재 모델 학습여부, BiasReset 시 False로 리셋)와 `sgd_sample_counts`
(`OnlineLearner._horizon_counts`, `DECISION_LOG.md` 1593행 설계상 qualify용 lifetime
누적치라 리셋 안 됨)가 서로 다른 축이라 배지·건수가 어긋나 보였던 것. 실제 리셋 로직은
qualify 게이트 유지를 위한 의도된 설계라 그대로 두고, 대시보드 표시만 "리셋됨"(주황,
cnt>0인데 미학습) / "미학습"(cnt=0) / "학습됨"으로 3분기해 오인 해소. ② 5분/10분이 "학습됨"
인데 정확도 0.0%로 보이던 원인 — `horizon_accuracy()`가 정확도 버퍼 표본 5건 미만이면
방어적으로 0.0을 반환(실제 0%가 아니라 "판정불가")하는데 UI가 그대로 찍어 오인. 표본 수를
`horizon_acc_samples()`로 노출해 `is_fit and n>=5`일 때만 실제 %를 표시, 미달 시
"—.—%(n건)"으로 구분. ③ GBM 배치 재학습 횟수가 항상 "0회"로 고정된 것 — 실제 재학습은
`_start_gbm_retrain_subprocess()`가 매번 새 `BatchRetrainer` 인스턴스를 py310_64
서브프로세스(`retrain_intraday.py`)에서 실행하는데, `_on_gbm_retrain_done()`이 그 서브
프로세스와 무관한 메인 프로세스 자신의(한 번도 증가한 적 없는) `self.batch_retrainer.
_retrain_count`를 읽어 영구히 0이었던 명백한 버그. `session_state.json`의 누적값에 +1하는
방식으로 교체. 추가로 매일 15:45 장외 스케줄러가 실행하는 `retrain_eod.py`(full CV
재학습)는 완료 마커 파일만 기록하고 `session_state.json`을 전혀 건드리지 않아 대시보드
카운트에 반영되지 않던 것도 함께 수정(동일 키에 +1). ④ CB③ 30m 정확도 강조색 임계값이
`cb_n>=5`로 하드코딩되어, 실제 HALT 판정 최소표본 `CB_ACC30M_MIN_SAMPLES=30`(277차 가드)
과 달라 5~29건 구간의 무의미한 값이 위험처럼 빨갛게 보이던 UX 문제 — 임계값을 30으로 정렬.

**코드 수정**: `learning/online_learner.py`에 `horizon_acc_samples(hz)` 추가.
`main.py::_gather_learning_stats()`에 `horizon_acc_samples` 필드 추가,
`_on_gbm_retrain_done()`의 재학습 카운터를 세션 누적(+1) 방식으로 교체 + `batch_retrainer.
_retrain_count`도 동기화. `retrain_eod.py`에 완료 마커 기록 직후 동일한 session_state 키
(`gbm_last_retrain`/`gbm_total_retrain_count`) 갱신 추가. `dashboard/main_dashboard.py`
SGD 호라이즌 카드 렌더링을 "학습됨/리셋됨/미학습" 3분기 + 정확도 판정불가 구분 표시로 교체,
CB③ 강조색 임계값을 `CB_ACC30M_MIN_SAMPLES` import로 정렬. `python -m py_compile`로 4개
파일 구문 검증 완료. **실제 대시보드 창에서 배지·정확도·재학습 횟수 표시 육안 확인 필요**
(오프스크린 렌더 테스트 미실시) — `NEXT_TODO.md` 280차.

**미해결/범위 외**: `scripts/eod_retrain.py`(수동/백업용, `EOD_RETRAIN.bat` 대상)는
session_state를 건드리지 않는 상태 그대로 둠 — 앱이 꺼진 날 수동 실행하는 보조 스크립트라
매일 15:45 자동 스케줄(`retrain_eod.py`)과 이중 카운트될 위험을 피하기 위해 의도적으로 미수정.
필요 시 별도 검토.

---

## 2026-07-02 (279차 — drift_adjuster 대시보드 표시 추가)

**결론**: `DriftAdjuster`의 `DRIFT_UP`/`RECOVERY_DOWN`/`HOLD`/`SKIP_LOW_SAMPLE` 판정이
로그·JSON 상태 파일에만 남고 대시보드 어디에도 표시되지 않던 것을 확인, `LearningPanel`
("🧠 자가학습 모니터")의 CB③ 라인 바로 아래에 `SGD alpha: 0.00150  정확도 하락→alpha↑
\| 이력: █▅▃██▁█▅██` 형태 라벨을 추가해 노출.

**코드 수정**: `drift_adjuster.py`에 `_last_action` 영속화 + `get_status()` 조회 메서드
추가. `main.py::_gather_learning_stats()`에 `drift_alpha`/`drift_action`/`drift_history`
필드 추가. `dashboard/main_dashboard.py`에 `_lbl_drift` 라벨(액션별 색상 매핑 + 툴팁)
추가. PyQt5 오프스크린 렌더 테스트로 6가지 경로(액션 4종 + 알 수 없는 값 + 필드 누락
기본값) 모두 확인. **실제 대시보드 창 육안 확인·EOD 반영 확인 필요** —
`NEXT_TODO.md` 279차. 상세: `SESSION_LOG.md` 279차.

---

## 2026-07-02 (278차 — drift_adjuster 최소 표본 가드 추가)

**결론**: `DriftAdjuster.record_accuracy()`가 당일 정확도를 표본 수 무관하게 그대로
10일 이력에 반영해, 검증 표본이 소수인 날(1/3=33%, 1/2=50% 등)의 극단값이 alpha 조정
로직(3일 연속 하락/2일 연속 회복 판정)을 왜곡시키던 문제 수정. `275차 발견 목록`의
"drift_adjuster acc_history 노이즈" 항목 후속 조치.

**코드 수정**: `learning/online_learner.py`에 `sample_count` 프로퍼티(당일 누적 검증
표본 수) 추가. `learning/self_learning/drift_adjuster.py`에 `MIN_SAMPLES_REQUIRED=15`
가드 추가 — 미달 시 `SKIP_LOW_SAMPLE`로 이력 기록·alpha 조정 스킵, 기존 alpha 유지.
`main.py::daily_close()`에서 `n_samples=`로 전달하도록 연결. 단위 테스트로 스킵/기록
경로 확인. **다음 거래일 EOD 로그 검증 필요** — `NEXT_TODO.md` 278차. 상세:
`SESSION_LOG.md` 278차, `DECISION_LOG.md` 278차.

---

## 2026-07-02 (277차 — CB③ 오늘 미발동 원인 확정 + 버퍼 기아 방지 수정)

**결론**: CB③(30분 정확도<35%→당일 정지) HALT 트리거는 2026-06-25부터 코드에서 완전히
비활성화된 상태(`circuit_breaker.py:315`, 사유: 30m need_add 피처 미탑재 + 구조적 acc
저하 오발동 반복). 오늘도 acc30m이 5.9~26.1%까지 떨어졌지만 state=NORMAL 유지로 실측
확인 — 버그 아니라 06-25 결정 그대로. 비활성화 사유 중 "피처 미탑재"는 178차(06-15)로
이미 해소됐으나(`opt_gex_bn`·`opt_chain_pcr` 매분 정상 수집 확인), "acc 회복"은 276차
결론(모델이 몇 주째 랜덤급 정확도)대로 미충족 상태라 재활성화 안 됨.

**사용자 결정**: CB③ 재활성화는 30m 정확도 회복 후로 보류(`DECISION_LOG.md` 277차).
재활성화 트리거: 30m accuracy≥0.35 5거래일 연속 + conf_inversion 미발동
(`NEXT_TODO.md` 277차).

**코드 수정(선행 과제, 같은 날 즉시 처리)**: acc30m 버퍼가 스케일러 재적합마다
(~30분 간격, 오늘 하루 종일 반복) 무조건 `clear()`돼 `MIN_SAMPLES=30`에 도달하기 전에
계속 리셋되는 영구 기아 상태였음(오늘 `[CB③-P4]` 단계 전환 로그 0건으로 실측 확인).
`safety/circuit_breaker.py::reset_acc30m_buffer()`를 표본<30이면 리셋 스킵하도록 수정,
`main.py` 호출부 로그도 동기화. **다음 거래일 검증 필요** — `NEXT_TODO.md` 277차 검증
항목 참고. 상세: `SESSION_LOG.md` 277차.

---

## 2026-07-02 (276차 — conf 하락 근본원인 딥다이브 완료)

**결론**: 06-29 이후 conf 하락은 EOD 재학습/canary/scaler 데이터 품질 문제가 **아님**
(둘 다 로그 확인 결과 정상). `predictions.db` 5m 일별 accuracy를 06-01~07-02 전체로
직접 쿼리한 결과 정확도는 06-29 전후로 꺾이지 않고 6월 내내 랜덤 근방(25~40%)을
요동쳤음 — 즉 모델은 몇 주째 실질적 방향성 엣지가 거의 없었고, 이전의 느슨한 Platt
보정(C=0.05)이 이를 가려 conf를 0.44~0.50대로 부풀려 보여주고 있었을 뿐. 261차(06-29)
Platt 강화(WINDOW 100→200, C 0.05→0.02)가 의도대로 작동해 conf를 실제 정확도 수준으로
끌어내렸고, 07-01~07-02 추가 하락은 06-25 Q3 배포정책(3m/5m 완성봉 시점만 배포)으로
줄어든 표본 속도 탓에 WINDOW=200 완전 수렴까지 ~2.8~3거래일 걸린 지연 효과. 코드 변경
없음(조사만 수행). 상세: `SESSION_LOG.md` 276차, `NEXT_TODO.md` 275차 ①.

**남은 우선순위**: NEXT_TODO 275차 ②(CB③ 30분 정확도<35% 상시 발동해야 정상인데 실제
오늘 발동했는지 미확인)가 이번 조사와 직결 — 다음 세션 최우선 후보.

---

## 2026-07-02 (275차 — conf/mc 통과율 0 딥다이브: 모델 신뢰도 붕괴 진단 + 리포트 버그 2종 수정)

### 배경

사용자 보고: "금일 conf 평균이 mc 기준보다 낮아 통과율이 거의 0". 딥다이브 결과 오늘만의
문제가 아니라 06-29 이후 conf 평균이 지속 하락(0.45→0.39대) 중이었고, `calibration_report.md`
최근구간 accuracy가 **32.78%**(3분류 랜덤 베이스라인 33.3%와 사실상 동일)에 **calibration bin
역전**(고신뢰 0.8~0.9 acc=31.36% < 저신뢰 0.3~0.4 acc=33.64%)까지 확인됨. 즉 conf가 mc보다
낮은 건 게이트 임계 문제가 아니라 **모델이 방향성 엣지를 잃었고 Platt 보정기가 그걸 정직하게
반영해 conf를 낮추고 있는 것** — mc를 낮추는 미봉책은 위험(역상관 모델에 진입 허용).

딥다이브 중 진단용 스크립트 2개에서 버그 발견, 사용자 요청으로 즉시 수정:

### 수정 (커밋 d9bf4f0)

| 파일 | 변경 |
|---|---|
| `scripts/generate_meta_gate_tuning_report.py` | `meta_labels` 소스 그리드서치가 `row["meta_confidence"]`(존재하지 않는 컬럼)를 찾다 실패해 매번 raw `predictions.confidence`로 조용히 폴백하던 버그 수정. `ensemble_decisions.meta_confidence`(실제 blended_conf)를 `ts` 기준 `MAX(id)` 서브쿼리로 LEFT JOIN해 진짜 메타 신뢰도로 튜닝하도록 변경. 재생성 결과 avg=0.46→0.2171(flat_signal 시 설계상 0.0 다수 포함, 정상), best grid match율 73.6%→76.4% |
| `scripts/generate_rollout_readiness_report.py` | `generate_calibration_report.py`가 이미 계산해두고 방치하던 `conf_inversion`(고신뢰 구간이 저신뢰보다 3%p 이상 덜 정확하면 발동)을 `decide_stage()` 최상단 가드로 연결. ECE/PnL이 좋아도 역전 감지 시 `small_size` 승격을 막고 `shadow`로 강제. 체크리스트에 `Confidence inversion: none/DETECTED` 라인 추가 |

### 발견했으나 손대지 않은 것 (다음 세션 후보)

- **conf_inversion 근소 미달**: 현재 gap=**2.85%p**로 발동 임계 3%p 바로 아래라 오늘은
  여전히 `small_size` 유지 — 273차 EKS 마진 이슈와 동일 패턴(임계 바로 밑에서 안전장치 안 걸림).
  임계값을 낮출지는 근본 원인 조사 후 판단 예정
- **conf 하락의 근본 원인 미조사**: 06-29 전후로 무엇이 모델을 랜덤 수준까지 깎았는지
  (EOD 재학습 데이터 품질? canary z경고 피처? scaler refit?) 아직 특정 못함
- **CB③(30분 정확도<35%→당일 정지)이 왜 상시 발동 안 하는지 미확인**: 30m 호라이즌 누적
  accuracy가 32.88%로 이미 CB③ 임계 밑인데 오늘 CB③ HALT 로그 유무 미확인
- **drift_adjuster acc_history 노이즈**: 최근 10개 값이 0.156~0.5로 요동 — 표본 부족 구간
  가드 없이 alpha=0.0076로만 완만히 적응 중, 최소 표본수 가드 검토 여지

상세: `dev_memory/SESSION_LOG.md` 275차, `dev_memory/DECISION_LOG.md` 275차, `dev_memory/NEXT_TODO.md` 275차.

---

## 2026-07-02 (274차 — 진입0 딥다이브 + ATR 적응형 상한 · Hurst/MR 조건부 완화)

### 배경

07-02 09:00~12:30 장중 진입 0건. 로그 딥다이브로 등급 A/B 도달 신호 9건 전부가 각기 다른
게이트(EKS 2건 정상 / ATR상한 5건 / Hurst 2건)에서 막힌 것을 확인. 그중 ATR_MAX_ENTRY=3.5pt
정적 상한이 최근 7거래일 ATR 중앙값(3.5~6.2pt)에 만성적으로 걸리는 구조적 문제, Hurst 게이트가
MEAN_REVERSION 모드까지 함께 막아 횡보장에 대응 전략이 사실상 죽어있는 문제 2가지를 확인·수정.
상세: `dev_memory/SESSION_LOG.md` 274차, `dev_memory/DECISION_LOG.md` 274차.

### 핵심 변경 (커밋 예정)

| 파일 | 변경 |
|---|---|
| `config/settings.py` | `ATR_ADAPTIVE_MAX_WINDOW/MULT/CEILING/MIN_SAMPLES` 추가 — ATR 상한 적응형화. `MR_EXHAUSTION_MIN_WEAK=0.60`·`MR_WEAK_SIZE_MULT=0.5` 추가 |
| `main.py` | `self._atr_recent_window`(60분 롤링) 신설. `_atr_ok` 상한을 `clamp(3.5, 최근60분평균×1.25, 6.0)`으로 동적화. `_hurst_ok`에 `entry_mode=="MEAN_REVERSION"` 예외 추가 |
| `strategy/entry/checklist.py` | MR VWAP 체크를 정상(≥0.70)/약한(0.60~0.70, 사이즈×0.5) 2단계로 분리 |

### 검증 예정 (NEXT_TODO 274차 참고)

- 적응형 ATR 상한 로그(`적응형, 정적=3.5`)에서 실제 상한값이 올라가는지
- `모드=MEAN_REVERSION` 로그가 실제로 찍히기 시작하는지 (최근 2일 0회였음)
- 약한 MR 사이즈 축소가 TRADE 로그와 대조해 정확히 반영되는지

---

## 2026-07-02 (273차 — EKS 발동 히스테리시스 + 프리장 refit·S6·ConfTrend 진단 강화)

> 265~272차는 이 파일에 기록되지 않음 (git log에는 존재 — MW0601/MW0602 배처 통합·자동로그인
> 리네임 등 인프라 작업 위주로 추정, 필요 시 `git log --oneline` 참고). 264차 이후 공백.

### 배경

07-02 장중 09:05 EKS(Early Kill Switch) 발동 → 09:33까지 관망 지속. 당일 WARN/SYSTEM 로그
전체를 딥다이브해 인과관계를 추적한 결과, 264차에서 고친 cold-start 오판별 버그와는
별개로 **08:59 Phase4(마지막 프리장 refit)가 11→11개로 완전히 무효**했고, GAP_OPEN conf_max가
mc 대비 **0.5%p 근소 미달**(36.4% vs 36.9%)로 EKS가 발동한 것을 확인. 부수적으로 STEP6
파이프라인 병목과 ConfTrendWidget 진단 로그 미출력(LOG_LEVEL 버그)도 함께 발견.

### 핵심 변경 (커밋 5b8ddc4)

| 파일 | 변경 |
|---|---|
| `safety/system_health.py` | `EKS_TRIGGER_MARGIN=0.02` 추가. 발동 조건을 `conf_max < mc`→`conf_max < mc-margin`으로 변경(히스테리시스). 마진 내 근소 미달은 발동 대신 WARNING으로 노출. 회복(해제) 조건은 미변경 |
| `model/multi_horizon_model.py` | `canary_z_warn_count`/`canary_z_warn_features` 공용 헬퍼 `_canary_z_warn_mask` 분리 + `canary_z_warn_features()` 신규(피처명 리스트 반환) |
| `main.py` | `_canary_load_z_warn_features()` 추가. PreMarket Phase refit 로그에 `잔존=피처1,피처2` (refit 전후 모두 z경고인 피처) 추가. STEP6 구간별(`ensemble`/`checklist_pre`/`meta_gate`/`gates`/`dashboard`/`tail`) 세부 타이머 `[S6Detail]` 매분 INFO 기록 |
| `dashboard/panels/conf_trend_widget.py` | `_do_refresh()` 세부 스텝 타이밍을 버퍼링 후 SLOW(>200ms) 시 WARNING 한 줄에 breakdown 포함 — 기존 `.debug()` 호출은 SYSTEM 로거가 `LOG_LEVEL=INFO`라 전부 드롭되고 있었음 |

### 발견한 이상점 (내일 로그로 원인 특정 예정)

- **Phase4 refit 무효화**: Phase1~3(3·5·10봉)은 z경고를 16→6, 12→6, 14→10으로 억제했는데
  Phase4(14봉, 오늘 비중 47%)만 11→11로 무변화. 오늘 비중이 클수록 억제력이 떨어지는 역설 —
  `잔존=` 로그로 내일부터 어떤 피처가 반복 걸리는지 확인
- **STEP6 병목**: PipePerf 로그의 `S6` 라벨(=STEP6 앙상블 진입판단 본문)이 전체 파이프라인의
  79~83%를 차지 (09:07 938/1193ms, 09:32 855/1036ms). 09:10 장시작버스트 면제 구간 이후에도
  재현 — 상시 병목으로 추정, `[S6Detail]`로 세부 구간 분해 예정
- **ConfTrendWidget**: 199차에서 `MAX_ROWS=30`+in-place 업데이트로 고쳤음에도 09:30~09:33
  4분 연속 328~422ms — 캡은 걸려 있는데(rows=30) 왜 느린지는 이번 로그 레벨 수정 후
  breakdown으로 확인 필요

### 운영 주의

- EKS 발동 임계가 낮아졌으므로(=발동하기 더 어려워짐) 향후 실제로 저신뢰 구간에서
  EKS가 필요했는데 마진 때문에 안 켜지는 사례가 있는지 함께 관찰할 것
- `[S6Detail]`·`[LiveDBG] ConfTrend SLOW ... |`·`[PreMarket] Phase... 잔존=...` 로그는
  진단용으로 매 분/이벤트 INFO 기록됨 — 원인 특정 후 제거 검토 (199차 LiveDBG와 동일 패턴)

---

## 2026-07-01 (264차 — EKS 오발동·z경고 과측정 3종 근본 수정)

### 핵심 변경 (커밋 332e6c4)

| 파일 | 변경 |
|---|---|
| `safety/system_health.py` | `_gap_open_policy_blocked_count` 추가. `_is_cold_start` 로직 수정: `delayed+policy_blocked>=bar_count` |
| `model/multi_horizon_model.py` | `canary_z_warn_count`에 `_Z_WARN_EXEMPT` 필터 적용 |
| `main.py` | `_gap_horizon_blocked=decision.get("active_horizons_blocked")` → `record_gap_open_bar` 전달. Canary refit 완료 후 `_last_canary_z_warn` 갱신 |

### 운영 주의

- EKS 오발동 수정: 내일 장 시작 시 `[SHS-EKS] EKS 미발동 — cold-start (conf_max=0%% delayed=1 policy_blocked=4 / 5봉)` 로그로 정상 확인
- Canary z-warn: 오늘 이후 08:55 Canary 값이 ~10 내외로 감소 예상 (14→10 정정)
- 30봉 window(247차)는 여전히 유효하나 오늘 z=14 원인이 _Z_WARN_EXEMPT 누락이었음 — 근본 수정 완료

---

## 2026-06-30 (263차 — EOD 재학습 pkl 경합 방지)

### 배경

15:40 daily_close() 진입 시 STEP 3 장중 GBM 배치 재학습이 진행 중이었고,
15:45 MireukiEODRetrain(윈도우 스케줄러)이 동시 실행되어 pkl 경합 위험 존재.
오늘 로그(retrain_eod_20260630.log)로 실증 확인 후 구조적 해결.

### 수정 내용 (커밋 5aed765)

| 파일 | 변경 |
|---|---|
| `retrain_eod.py` | `_wait_for_daily_close()` 함수 추가 — `data/_exit_normally` 오늘 날짜 확인, 최대 20분 폴링(30초 간격), 타임아웃 시 슬랙 경보 후 강제 진행 |

### 운영 조치

- **윈도우 스케줄러**: `MireukiEODRetrain` 15:45 → **16:10** 수동 변경 완료
- 코드: `_wait_for_daily_close(max_wait_min=20)`가 16:10에도 daily_close 미완료 시 추가 대기

### 완료 마커 확인 구조

```
daily_close() 마지막 단계
  → data/_exit_normally 기록 (reason + ISO timestamp)

retrain_eod.py _wait_for_daily_close()
  → _exit_normally 존재 AND 오늘 날짜로 시작 → 즉시 통과
  → 없으면 30초마다 재확인 (최대 20분)
```

### 오늘 EOD 재학습 결과 (정상 완료)

- 15:45:04 시작 (경합 상태였으나 결과적으로 정상)
- 6/6 호라이즌 교체 완료, 합계 181초
- P8 스케일러 재적합 완료, session_state 기록 완료

---

## 2026-06-30 (262차 — SHORT 진입·손실청산 감사 개선 4종)

### 배경

09:44 short 진입과 손실 청산 감사 요청 → 코드 딥다이브 후 7개 이슈 발견, 우선순위별 구현:
- MR SHORT의 bull_exhaustion 임계 부재 (P1)
- TP1 부분청산 후 잔여분 손절 미이동 (P1) — EV 역전 구조적 결함
- #7 직전봉 체크가 MR 모드와 충돌 (P2)
- 0~0.5ATR 수익 구간 트레일링 무방비 지대 (P2)

### 수정 내용 (커밋 b28a0cb)

| # | 파일 | 변경 | 효과 |
|---|---|---|---|
| ① | `config/settings.py` | `MR_EXHAUSTION_MIN = 0.70` 신규 상수 | 0.60(vol 1.8×) → 0.70(vol 2.1×) 중강도 이상만 허용 |
| ② | `strategy/entry/checklist.py` | MR 탈진 임계 `> 0.0` → `>= MR_EXHAUSTION_MIN` | 약한 탈진(volume barely 1.8×) MR 오진입 제거 |
| ③ | `strategy/entry/checklist.py` | #7 직전봉: MEAN_REVERSION 모드 분기 추가 | MR LONG: 음봉·도지 허용 / MR SHORT: 양봉·도지 허용 |
| ④ | `strategy/position/position_tracker.py` | `update_trailing_stop` 0.5ATR 단계 추가 | 0.5~1.0ATR 구간 손절 -1.5ATR → -0.75ATR 축소 |
| ⑤ | `strategy/position/position_tracker.py` | `get_trailing_reference_price` 0.5ATR 동기화 | 참조가 update와 일치하도록 보정 |
| ⑥ | `main.py` | `_post_partial_exit(stage=1)` 후 손절 손익분기 이동 | TP1 체결 확인 후 잔여분 손절 → 진입가 자동 이동 |

### 설계 근거

**exhaustion 값 구조**: `exh_val = min(vol / (avg_vol × 3.0), 1.0)` + `vol_surge (vol > avg × 1.8)` gate
- 발동 시 최솟값: `1.8/3.0 = 0.60`. 즉 값은 항상 0.0 또는 0.60~1.0
- `> 0.0`과 `>= 0.60`은 동등 → 0.70 임계로 중강도 이상만 선별

**TP1 잔여분 손절 이동 EV 근거**:
```
진입 @ 400pt, 손절 @ 397.75 (-1.5 ATR=2.25pt), TP1 @ 401pt (+1.0 ATR)
TP1 33% 청산: +1pt × 0.33 = +0.33pt
잔여 67% 최대손실(이동 전): -2.25pt × 0.67 = -1.51pt → 순 -1.18pt 역전
잔여 67% 최대손실(이동 후): 0pt × 0.67 = 0pt → 최악 0pt (손익분기)
```

**0.5ATR 무방비 지대**:
- 기존: 수익 0~1ATR 구간 손절 고정(-1.5ATR) → 최대 총손실 2.0 ATR 가능
- 개선: 0.5ATR 구간에서 -0.75ATR로 이동 → 최대 총손실 1.25 ATR로 제한

### P3 확인 (1계약 TP1 arm) — 기구현

`main.py:8829-8860` `_ts_execute_partial_exit`에서 `total_qty==1 and stage==1` 분기로 이미 처리:
```python
protect = self.position.arm_tp1_single_contract_with_mode(price, atr, mode=protect_mode)
```
`_tp1_protect_mode` 기본값 `"breakeven"` → 손절 진입가 이동. 별도 수정 불필요.

### 잔여 이슈 (미구현)

- **P6**: 분봉 bar_high/low 기반 실시간 손절 — 현재 분봉 종가 기준이므로 intrabar 급변 시 손절 지연. 실시간 틱 피드 연동 필요 (중장기 과제)

---

## 2026-06-29 (261차 — HCGuard + Platt tail 압축 + 역전 경보)

### 배경

EOD 재학습 + P8 완료 후 calibration 분석:
- conf 0.7+ 실측 정확도 **29-31%** (conf 0.3~0.5 구간 33%보다 낮음) — 신뢰도 역전
- Grade A 자동진입이 Grade B보다 오히려 정확도 낮은 신호에 실행
- Platt WINDOW=100 시 tail(0.6+) 샘플 ~7건 → 보정 불안정
- ECE high_bins = 0.38 (0.6+ 구간)

### 수정 내용 3종 (커밋 482cb05)

| # | 파일 | 변경 | 효과 |
|---|---|---|---|
| ① | `model/ensemble_decision.py` | `HCGuard`: conf≥0.65 최근 50건 acc 추적, acc<42% → Grade A→B 강등 | 역전 구간 A급 자동진입 차단 |
| ② | `learning/calibration.py` | WINDOW 100→200, C 0.05→0.02, 재보정 주기 10→5 | tail 샘플 확보 + 압축 강화 |
| ③ | `scripts/generate_calibration_report.py` | `_check_confidence_inversion()`, conf_inversion JSON 키, 리포트 경고 섹션 | 역전 상태 자동 감지·보고 |

### HCGuard 동작 규칙

- `_HC_GUARD_WINDOW = 50`: 최근 50건 고신뢰 예측 버퍼
- `_HC_GUARD_MIN_N = 20`: 20건 이상 쌓여야 가드 활성 (cold start 보호)
- `_HC_GUARD_CONF_THR = 0.65`: 고신뢰 판단 기준
- `_HC_GUARD_ACC_THR = 0.42`: 이 정확도 미달 시 Grade A → B 강등
- `reset_daily()`에서 버퍼 유지 (일일 공백에도 누적 유효)
- `record_ensemble_outcome(raw_conf, correct)` 호출 시 자동 업데이트

### 현재 데이터 기준

- 역전 감지: `high_acc=29.5%` vs `low_acc=32.8%` (gap=3.3%) → **경보 발동**
- 다음 장 시작 후 20건 누적되면 HCGuard 자동 발동 예정
- Platt 변경 효과는 내일 이후 ECE 추이로 확인

---

## 2026-06-29 (260차 — Extreme 피처 Top5 이상점 5종 수정)

### 배경

오늘 누적 extreme 피처 Top5 딥다이브 결과, 구조적 z-score 폭발 4종 + 스케일러 기준 역전 1종 확인.

| 순위 | 피처 | 이상 유형 | 오늘 max|z| |
|---|---|---|---|
| 1 | `atr_expansion_rate` | unbounded 입력 (z=18.32) | 18.32 |
| 2 | `bull_reversal_signal` | 쿨다운 없는 과발동 (30회) | 10.96 |
| 3 | `toxicity_spread_stress` | 스케일러 μ=0.978 역전 | 9.89 |
| 4 | `hurst_ready` | binary 플래그 z≈4.5 오발동 | 5.61 |
| 5 | `is_close_volatile` | 시간 binary 플래그 z≈5.5 오발동 | 7.39 |

### 수정 내용 4종 (파일 3개)

| # | 파일 | 변경 | 효과 |
|---|---|---|---|
| ① | `features/feature_builder.py:346-348` | `atr_expansion_rate` `np.clip(-0.5, 0.5)` + `_prev_atr > 1e-6` | max|z| 18.32 → 최대 7.9로 억제 |
| ② | `features/technical/ofi_reversal.py` | `bull_reversal_signal` warmup 억제(20봉 미만) + 5봉 쿨다운 | 오늘 30회 → 이론 최대 15회 이하 |
| ③ | `model/multi_horizon_model.py` | `_MACRO_SCALE_FLOOR["toxicity_spread_stress"] = 0.25` | z=(0-0.978)/0.25=-3.9 → extreme 4.0 미만 보장 |
| ④ | `model/multi_horizon_model.py` | `_Z_WARN_EXEMPT`에 `hurst_ready`, `is_close_volatile`, `is_open_volatile` 추가 | binary/시간 플래그 경보 노이즈 제거 |

### 주의사항

- `toxicity_spread_stress` μ=0.978 고착은 235차 tick_size 수정 이전 훈련 데이터 기반. 다음 EOD 재학습 후 μ 정상화(≈0.05) 확인 필요.
- `atr_expansion_rate` clip=0.5는 ATR이 1분 만에 50% 이상 변화하는 경우 클리핑 — 극단 변동성 장세에서 정보 손실 감수.
- `bull_reversal_signal` COOLDOWN_BARS=5는 장 시작 직후 신호 연속 발동 억제. 단기 반전 잡기 목적이므로 5분이 적절하나 실전 검증 필요.

---

## 2026-06-29 (259차 — bull_reversal_signal 이진 피처 z>4 과발동 + HealthPolicy 동적화)

### 배경

11:04:58 `bull_reversal_signal=1` 발동으로 전 호라이즌 z=+5.89 동시 발생.
→ conf 36.0% 26분 고착 + HealthPolicy Degraded Mode 상시 차단 → 진입 0회.
11:13~11:18 MetaGate=take 신호 있었으나 HealthPolicy(62.0% 고정)에 의해 최종 차단.

### 피처 분석

`bull_reversal_signal`: OFI 반전 이진(0/1) 신호. 발동 빈도 낮아 GBM 스케일러 σ≈0.17 학습 → 발동 시 항상 z=(1-μ)/σ≈5.89. 전 호라이즌이 같은 분봉 OFI 입력 → 동시 발생 구조적 불가피. ScalerFloor 미적용은 올바른 동작(σ 충분)이나 이진 특성으로 인한 구조적 z 폭발은 별도 처리 필요.

### 수정 내용 4종 (커밋 3281067)

| # | 파일 | 변경 | 효과 |
|---|---|---|---|
| ① | `model/multi_horizon_model.py` | `_MACRO_SCALE_FLOOR["bull_reversal_signal"] = 0.45` | 다음 재학습부터 z≤2.2 보장 |
| ② | `model/multi_horizon_model.py` | `_Z_WARN_EXEMPT` + extreme_mask 필터 | 현 세션부터 z>4 WARNING 즉시 제거 |
| ③ | `main.py` | HealthPolicy `_dg_mc = max(actual_min_conf, 0.30)` | zone_mc 0.357 → conf 0.360 Degraded 통과 |
| ④ | `main.py` | DynMC ConstOut 15% 필터 (`_recalibrate_mc`) | 고착 conf 제외 후 p65 계산 |

### 추가 발견 — 257차 수정 효과 실증

11:31:58 DynMC RETRAIN에서 MC_PERCENTILE 수정(②) 효과 최초 확인:
- STABLE_TREND 0.420→**0.357** (이전: 0.03/회 × 30분 → 5시간 소요, 이제: 0.08 STEP_LIMIT 내 즉시)
- grade=C 최초 출현 (conf=36.0% > zone_mc=0.357)

---

## 2026-06-29 (258차 — save_horizon_features 4인자 버그 수정)

### 배경

오늘 09:02부터 매분 `[DBQueue] 쓰기 실패 (op=horizon_features): save_horizon_features() takes 3 positional arguments but 4 were given` 86회 발생. horizon_features DB 쓰기 전일 실패.

### 원인

`main.py`에서 DBQueue/fallback 경로 모두 `_regime`을 4번째 인자로 전달했으나 `db_utils.save_horizon_features(ts, horizon, features)`는 3 positional 인자만 받음. 함수 시그니처/DB 스키마에 반영 안 된 미완성 구현.

### 수정 (커밋 ea5f4f7)

- `main.py:1577` DBQueue 소비 경로: `_regime` 인자 제거
- `main.py:4148` 동기 fallback 경로: `_regime` 인자 제거
- `_regime`은 raw_features_horizon 테이블(ts/horizon/features 3컬럼)에 애초에 없었음 → 스키마 변경 불필요

---

## 2026-06-29 (257차 — DynMC MC 기준 상향 원인 5종 수정)

### 배경

6/29 모의투자 장 시작 후 전일 대비 MC 기준이 대폭 상향돼 오전 내내 진입 0회 발생.
앙상블 conf 추이 딥다이브 + 6/25 vs 6/29 MC 흐름 비교를 통해 원인 5종 특정·수정.

### 핵심 발견

| 발견 | 내용 |
|---|---|
| mc_history DB 경로 오류 | `data/mc_history.db`(0 bytes) vs 실제 `data/db/mc_history.db` — 기동 복원 실패로 코드 기본값(0.54~0.67) 사용 |
| MC_PERCENTILE 버그 | `MC_PERCENTILE=0.65`를 `/100`해 0.65%분위(≈최솟값 0.17) 사용 — 65분위가 아닌 최솟값이 p65로 계산됨 |
| MC_STEP_LIMIT 0.03 — 수렴 지연 | 코드 기본값(0.54)→목표(0.25)까지 0.03/회×30분 = 5시간 소요. 장 중 절대 도달 불가 |
| GAP_OPEN cold-start EKS 과발동 | active_horizons 초기화 지연으로 conf=0% 5봉 → EKS 발동. 모델 붕괴 아닌 정상 cold-start |
| EKS 회복 로그 불투명 | `try_eks_recovery()` 실패 원인이 INFO 레벨에 묻혀 진단 어려움 |

### 6/25 vs 6/29 MC 실측 비교

| 항목 | 6/25 | 6/29 |
|---|---|---|
| 기동 MC (STABLE_TREND) | **0.250** (mc_history 복원 성공) | **0.540** (복원 실패 → 코드 기본값) |
| EKS 발동 | 없음 | 09:05 발동, 미해제 |
| 진입 | 수동 2회 + 자동 1회 | **0회** |
| 오전 conf | 17~35% | 31.0% 고착 (전 호라이즌 ConstOut) |
| MetaGate take_thr | 0.450 (min_conf=0.25) | 0.570 (min_conf=0.57) |

### 수정 내용 (커밋 f4b7806)

| # | 파일 | 변경 |
|---|---|---|
| ① | `config/settings.py` | `MC_STEP_LIMIT` 0.03→**0.08** |
| ② | `strategy/entry/time_strategy_router.py` | `idx_p65` 계산: `/ 100` 제거 → n=2086 기준 idx 13→1355 |
| ③ | `strategy/entry/time_strategy_router.py` | `_restore_mc_from_history()` 빈 DB 시 0.35 안전 fallback |
| ④ | `safety/system_health.py` | `evaluate_early_kill_switch()` cold-start 감별(conf=0%+delayed=0) → EKS 미발동 |
| ⑤ | `safety/system_health.py` | `can_attempt_recovery()` 시작 로그 + `try_eks_recovery()` 실패 원인 WARNING 출력 |

### 내일 기동 예상 동작

- mc_history DB에 오늘 0.42 기록 저장 → 기동 시 복원 성공 → STABLE_TREND 0.42로 시작
- MC_PERCENTILE 수정으로 p65≈0.38~0.42 → base_mc 현실적 계산 (STEP_LIMIT 거의 불필요)
- GAP_OPEN cold-start conf=0%여도 EKS 미발동 → 오전 자동진입 차단 해소

---

## 2026-06-29 (256차 — EKS "당일 관망 선언" 메시지 정정)

### 배경

장기 중단(약 41일) 후 재시작 시 로그:
- `[Canary] scaler 노후=999h` → B_INTRADAY refit 트리거
- `[SHS-EKS] Early Kill Switch 발동 — 당일 관망 선언. conf_max=0.0% bars=5`
- `[ConstOut] ['1m'] 상수 출력 확정 → 스케일러 재적합 시작`

EKS 코드를 확인한 결과 **자동 회복 메커니즘이 이미 구현돼 있음**:
- `can_attempt_recovery()` → 09:20부터 30분 간격, 11:30 이전까지
- `try_eks_recovery()` → scaler_age<1h + conf 10봉 중 3봉 이상 + z경고<15 → `_eks_active=False`

그런데 모든 로그 메시지가 "당일 관망 선언"으로 표시돼 영구 차단처럼 보이는 오해 유발.

### 이상점 정리

| # | 이상 | 원인 | 판단 |
|---|---|---|---|
| 1 | scaler 노후=999h | 장기 중단 후 재시작 | 정상 케이스, B_INTRADAY refit 트리거됨 |
| 2 | EKS conf_max=0.0% | scaler 노후 → 상수출력 → GAP_OPEN conf 0% | 발동 올바름, 메시지가 문제 |
| 3 | ConstOut 09:09 | B_INTRADAY 완료 전 ConstOut 감지 → 2차 refit | `_scaler_refresh_running` guard로 중복 방지 확인 |

### 수정 내용

| 파일 | 변경 |
|---|---|
| `safety/system_health.py` | 모듈 docstring + `evaluate_early_kill_switch` 로그: "당일 관망 선언" → "일시 관망 (30분 간격 자동 회복 평가, 마감 11:30)" |
| `main.py` CRITICAL 로그 | "당일 관망 선언" → "일시 관망 → 스케일러·conf 회복 시 자동 재개 (09:20부터 30분 간격 평가)" |
| `main.py` 매분 차단 로그 | "당일 관망 — 자동진입 차단" → "EKS 활성 — 자동진입 차단 (conf 회복 대기)" |
| `utils/notify.py` | 슬랙 발동 메시지 수정 + **EKS 해제 시 슬랙 알림 신설** (`notify_kill_switch_cleared`) |
| `dashboard/main_dashboard.py` | SHS 툴팁 "당일 관망일 선언" → "일시 관망 (자동 재개 대기)" + 회복 스케줄 설명 추가 |

### 핵심 확인

- EKS 자동 해제: `try_eks_recovery()` → `_eks_active=False` → 진입 재개 정상 작동 확인
- EKS 해제 후 GBM 재학습 트리거도 기존대로 유지 (232차 구현)
- **EKS 해제 Slack 알림 신설** — 발동(CRITICAL)은 있었으나 해제 알림 없었음. `notify_kill_switch_cleared(scaler_age_h, conf_hits, conf_window)` 추가

---

## 2026-06-28 (255차 — CREON Plus 자동 로그인 완전 구현)

### 배경

`cybos_autologin.py`가 CREON Plus 로그인 창에서 CREON Plus 선택·자격증명 입력·모의투자 접속을 하지 못하는 문제. CREON 로그인 창은 전체가 owner-drawn(GDI)이라 Win32 표준 API로 텍스트·버튼 탐지 불가. 실증적 디버깅(스크린샷, 픽셀 스캔, 히트테스트)으로 좌표를 확정하고 구현.

### 핵심 발견 (CREON UI 구조)

| 항목 | 내용 |
|---|---|
| 좌측 Afx 패널 | `WM_NCHITTEST = HTRANSPARENT(-1)` — 모든 마우스가 부모로 전달 |
| 부모 login_hwnd 전체 | `WM_NCHITTEST = HTCAPTION` — 커스텀 타이틀바 영역 |
| 드롭다운/버튼 | owner-drawn GDI 렌더링, Win32 텍스트 탐지 불가 |
| 모의투자 선택 팝업 | in-window GDI 오버레이, `EnumWindows` 불가 |

### 실증 확인 좌표 (패널 origin 기준)

| 단계 | 좌표 | 비고 |
|---|---|---|
| CREON Plus 드롭다운 열기 | panel+(90, 15) 클릭 | HTCAPTION 영역, 1회만 클릭 |
| CREON Plus 항목 선택 | panel+(65, 85) hover 400ms → 클릭 | 픽셀 스캔으로 확인 |
| "아이디" 탭 클릭 | panel+(295, 215) | Edit 컨트롤 가시화 |
| 모의투자로그인 버튼 | window_x+182, PW_bottom+72 ≈ screen y=780 | owner-drawn 버튼 |
| 모의투자 접속 팝업 | window_origin+(365, 317) | in-window 오버레이 |

### 구현 함수 (`scripts/cybos_autologin.py`)

| 함수 | 역할 |
|---|---|
| `_select_creon_plus_by_coordinate(hwnd)` | CREON Plus 드롭다운 선택 (좌표) |
| `_click_creon_id_tab(hwnd)` | "아이디" 탭 클릭 → Edit 가시화 |
| `_click_creon_login_button(hwnd)` | 모의투자로그인 버튼 좌표 클릭 |
| `_click_creon_mock_access(hwnd)` | 모의투자 접속 팝업 좌표 클릭 |
| `_clear_and_input(edit_hwnd, text)` | EM_SETSEL+WM_CLEAR → WM_SETTEXT |

### 자격증명 분리

| Target | User | 브로커 |
|---|---|---|
| `cybosplus` | smart5na | CYBOS (기존, 유지) |
| `creonplus` | smart6na | CREON (신규) |

- `CRED_TARGET`: CREON일 때 `"creonplus"`, CYBOS일 때 `"cybosplus"` 자동 분기

### 기타 수정

- em-dash(`—`) 전체 `--` 교체 (cp949 인코딩 오류 방지)
- UTF-8 stdout 강제 설정 (직접 실행 시 보장)
- `CREON_PLUS.bat` 실행 파일 힌트 업데이트

### 검증 결과

`CybosPlus 연결 성공 (ServerType=1)` — 모의투자 로그인 완료 실증

### 커밋

`5b1c033` (255차)

---

## 2026-06-26 (254차 — 거래소 서킷브레이커 감지·대응·대시보드 표시)

### 배경

6/26 KOSPI 8% 이상 하락으로 KRX 거래소 서킷브레이커(CB 1단계) 발동. 미륵이 파이프라인 4분 미실행 WARN 발생. KRX CB 메커니즘: 20분 거래 중단 → 10분 단일가매매 → 정규매매 재개 (총 30분).

### 구현 내용

**조기 감지 (main.py)**
- 분봉 240초(4분) 미수신 + `broker.is_connected=True` → 거래소 CB 즉시 확정 (기존 300초에서 앞당김)
- Cybos 서버 연결 정상인데 분봉 없음 = 네트워크 아닌 거래소 중단 판별
- Cybos 연결 이상(False)이면 기존 긴급 복구 로직 실행

**CB 발동 시 처리**
- Slack 알림에 예상 재개 시각 추가 (발동 감지 시각 +30분, KRX 기준)
- 30분 생존 알림 시 `_gap_min==30` → "재개 임박" 메시지 분기

**CB 해제 직후 처리**
- 포지션 보유 시 CB 해제 첫 분봉 close 기준 `force_exit()` 즉시 실행
- 관망 기간 **10분** 설정 (단일가매매 10분 전 구간 커버, 기존 5분 → 수정)
- 관망 중 STEP 7 게이트 `_ecb_observation_ok` 차단 + 매분 잔여 시간 갱신

**CB 3단계(장 조기 종료) 대비**
- `daily_close()`에 `_exchange_cb_mode / _ecb_observation_until` 강제 리셋 추가
- CB 3단계 발동 시 다음날까지 CB 모드 잔류 방지

**대시보드 거래소 CB 배지 (main_dashboard.py)**
- `lbl_ecb` 배지 신설 — `lbl_regime`(매크로레짐) 왼쪽, 정상 시 숨김(`setVisible(False)`)
- CB 발동: 진한 빨강(`#7a0000`) + 빨간 테두리, "KRX CB ⏸ / 재개≈HH:MM"
- 관망 중: 진한 주황(`#7a3800`) + 주황 테두리, "관망 N분 / HH:MM 재개" (매분 카운트다운)
- 정상 복귀 시: `setVisible(False)` 자동 복구
- `DashboardController.update_exchange_cb_badge(state, resume_est, until_dt)` 메서드 신설

### 수정 파일

| 파일 | 변경 |
|---|---|
| `main.py` | CB 조기 감지, 포지션 즉시 청산, 관망 10분, daily_close 리셋, 대시보드 호출 |
| `dashboard/main_dashboard.py` | `lbl_ecb` 배지 생성·배치, `update_exchange_cb_badge()` 메서드 |

### 커밋

`a320849` (254차)

---

## 2026-06-26 (253차 — 6/26 장중 분석 7종 수정)

### 배경

6/26 모의투자 첫 장: 09:05 EKS 발동(당일 관망), 09:11·09:21 OptionChainWorker 크래시 2회, 09:01·09:23 CB⑤ 기준 초과 블로킹 발생. 장 종료 후 원인 딥다이브 및 전량 수정.

### 수정 내용 7종

| # | 파일 | 수정 | 원인 |
|---|---|---|---|
| ① | `main.py` | `_poll_option_chain` RuntimeError try/except | deleteLater() 후 C++ 소멸, Python wrapper 살아있어 크래시 |
| ② | `main.py` | `_fetch_investor_data` 09:00~09:02 skip guard | BlockRequest(CpSysDib.CpSvrNew7221) 서버 피크 7,187ms 블로킹 |
| ③ | `session_recovery_service.py` | `_apply` 4단계 QTimer 체인 (10ms 양보) | 재시작 패널 복원 14,828ms 연속 블로킹 |
| ④ | `config/settings.py` | `quality_investor_age_sec` clip 버그 수정 (0.0,180.0)→(0.0,0.60) | /300 정규화값에 원시 초 clip → 무효였던 버그 |
| ⑤ | `config/settings.py` | `toxicity_atr_stress` (0.0,0.75) 추가 | 고변동성 장 z>4 → EKS 과발동 기여 |
| ⑥ | `model/multi_horizon_model.py` | ScalerFloor quality/toxicity σ 하한 추가, trigger_type별 로그 레벨 분리 | pre-market 72 WARNING 폭증 → INFO 전환, 장중 D_FORCE는 WARNING 유지 |
| ⑦ | `retrain_eod.py` | P8 완료 시 `eod_retrain_ok_date` 추가 기록 | daily_close(15:40) vs EOD 완료(15:47) 레이스 → PreRetrain 매일 fallback 의존 |

### 분석에서 기각된 것

- **InvestorWorker QThread 분리**: COM STA 위반 위험 + ②로 주요 구간 커버됨 → 불필요
- **SHAP 백그라운드화**: ③으로 주요 블로킹 해결됨 + VP cold-start 위험 → 불필요
- **ScalerFloor mean=0 적용(개선안 B)**: `macro_us10y_chg` mean=-0.483 → z=-4.83 극단 발생 확인 → 기각. 실측 테스트(py37_32 scaler pkl 직접 로드)로 검증.

### EKS 발동 근본 원인 (6/26)

오늘 특이: 1447(08:45) → 1404(09:33) 급락 -43pt, VIX=18.6 평상. CORE 피처가 conf=0.0% 5봉 → EKS 발동. 수정 ④⑤⑥으로 내일부터 z경고 구조적 억제.

### 커밋

`8952dd7` (253차)

---

## 2026-06-25 (252차 — macro_risk_off CORE 해제)

### 변경 내용

**`macro_risk_off`를 CORE 면제 목록에서 제거 (유령 CORE 정리).**

근거:
- **모델 미포함**: 전 호라이즌 `feature_names_hz.pkl` 확인 → 어디에도 없음
- **GBM gain = 0**: HistGBM split gain 순위 해당 없음
- **SHAP = 0**: shap_tracker.db mean_abs ≈ 0.000000 (108개 중 95위)
- **체크리스트·SGD 경로**: `checklist.py`, `online_learner.py` 모두 미참조 확인
- **ScalerFloor 발동은 정상**: global scaler(97개) σ=0.4221 → 0.50 보호는 작동했으나 예측 경로에 무관

### 수정 파일

| 파일 | 변경 |
|---|---|
| `config/settings.py` | `CORE_MASK_EXEMPT_BY_GROUP["mid"]["long"]`에서 `macro_risk_off` 제거 |
| `model/multi_horizon_model.py` | `_CORE_MASK_EXEMPT` frozenset에서 제거, `_MACRO_SCALE_FLOOR`에서 제거 |
| `CLAUDE.md` | CORE 테이블 주석에 2026-06-25 해제 이력 추가 |

### 유지한 것

- `MacroFeatureTransformer`의 `macro_risk_off` 계산 — 추후 모델 재투입 여지 보존
- `active_features`의 `macro_risk_off` 항목 — SHAP 심사 대상으로 유지

### 함께 분석한 것 (변경 없음)

- **`macro_krw_chg`**: 10m gain 3.4%(7위/11), 30m gain 6.3%(6위/11). ScalerFloor σ=0.0776→0.10 정상 작동. **유지**.

---

## 2026-06-25 (251차 — macro_vix CORE 강등)

### 변경 내용

**`macro_vix`를 중기/장기 CORE에서 제거하고 단순 보조 피처로 강등.**

근거:
- **일봉 상수**: Cboe CDN 일봉 VIX close → 장 내 분봉 500봉에서 std ≈ 0~0.03
- **SHAP 기여 ≈ 0**: 주 24 = 0.000669, 주 25–26 = 0.000 (97개 피처 중 사실상 최하위)
- **체크리스트 임계 비현실**: VIX 27.5 기준 → 평상시 항상 통과 → 무의미한 조건
- **ScaleFloor(0.10) 무력화 부작용**: identity 강제(raw_std<0.05) 후 scale=1.0 → ScaleFloor 조건 미충족 → "[ScalerRefresh] CORE 'macro_vix' raw_std=0.03 → identity" 경보 반복

### 수정 파일

| 파일 | 변경 |
|---|---|
| `config/settings.py` | `CORE_FEATURES_BY_GROUP["mid/long"]` macro 키 제거, `CORE_MASK_EXEMPT_BY_GROUP["mid/long"]` macro_vix 제거 |
| `model/multi_horizon_model.py` | `_CORE_MASK_EXEMPT` frozenset에서 macro_vix 제거. `_MACRO_SCALE_FLOOR["macro_vix"]=0.10` 유지 |
| `strategy/entry/checklist.py` | 중기(10m·15m) slot `4_cvd` → `True` 고정 (항상 면제) |
| `CLAUDE.md` | CORE 테이블에서 macro_vix 행 2개 제거 |

### 유지한 것

- `active_features`의 `macro_vix` — GBM 피처셋 유지 (재학습 불필요)
- `_MACRO_SCALE_FLOOR["macro_vix"] = 0.10` — 미래 VIX 급변 시 z 폭발 방어
- `checklist.py` `macro_vix` 파라미터 — 대시보드 VIX 표시에 계속 사용

### 기대 효과

- "[ScalerRefresh] CORE 'macro_vix' raw_std≈0 → identity 강제" 경보 소멸
- 중기 체크리스트 slot 4: 사실상 항상 통과이던 것이 명시적으로 면제로 전환 (실질 무변화)

---

## 2026-06-25 (250차 — 30m/CB③ 임시 비활성화·CORE cvd_delta_norm 교체)

### 현재 운영 상태

| 항목 | 상태 |
|---|---|
| **30m 역방향 필터** | **비활성** — acc=0.2796(랜덤 이하), need_add 7개 미탑재 |
| **CB③ acc30m HALT** | **억제 중** — 버퍼/P4 추적 유지, HALT/경고 미발동 |
| **CORE CVD 피처** | `cvd_direction` → **`cvd_delta_norm`** 교체 완료 |
| **feature_names_hz.pkl** | EOD retrain 후 전 호라이즌 정합 (6/6 일치) |
| **30m CV acc** | 0.2796 (EOD full_cv 기준) |
| **ERR-FATAL** | 방어 코드 추가 — 재발 시 fallback 반환 (HALT 아님) |

### 임시 비활성화 재활성화 조건 (≈2026-07-02)

1. `opt_gex_bn` / `opt_chain_pcr` 각 4,000행 달성 확인
2. `shap_feature_registry.json` + `horizon_feature_sets.json` need_add → in_pkl 업데이트
3. EOD 재학습 (full_cv=True) → 30m CV acc ≥ 0.33 확인
4. `ensemble_decision.py` Q3 블록 + `circuit_breaker.py` CB③ 재활성화

### cvd_direction 중기 개선 예정 (≈2026-07-14)

`CVDCalculator` 누적 방식 → delta-of-cumulative 전환. 상세: `docs/260715_CVD_DIRECTION_ANALYSIS.md`

### horizon_feature_sets.json 현행 need_add 목록

| 호라이즌 | need_add 피처 |
|---|---|
| 1m | `queue_directional_depletion`, `micro_regime_code` |
| 3m | `cvd_monotone_ratio` |
| 5m | `opt_chain_pcr`, `cvd_monotone_ratio` |
| 10m | `opt_atm_put_oi`, `opt_gex_sign`, `cvd_monotone_ratio`, `micro_regime_code` |
| 15m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_put_oi`, `threshold_feasibility`, `opt_pcr_extreme_bearish` |
| 30m | `opt_gex_bn`, `opt_chain_pcr`, `opt_atm_call_oi`, `opt_atm_pcr`, `threshold_feasibility`, `opt_pcr_extreme_bearish`, `micro_regime_code` |

> `threshold_feasibility`·`queue_directional_depletion`: 06-23 in_pkl 전환 시도 → 06-25 실 pkl 미포함 확인 후 need_add 재정정

---

## 2026-06-25 (249차 — poll_option_chain BlockRequest QThread 분리)

### 문제

`_poll_option_chain()` (QTimer 300s 콜백)이 메인 스레드에서 `Dscbo1.OptionMst.BlockRequest()`를 ATM ±30pt 종목 수(~24개)만큼 루프 실행 → **~3초 메인 스레드 점유**. 틱 수신·파이프라인·UI가 3초간 정지.

### 수정 (249차, 커밋 `745e444`)

| 파일 | 변경 내용 |
|---|---|
| `collection/options/option_chain_worker.py` (신규) | `OptionChainWorker(QThread)` — CoInitialize 후 Dscbo1.OptionMst BlockRequest 루프, result_ready 시그널로 feats/chain_raw 반환 |
| `collection/options/option_chain_snapshot.py` | COM 코드 전부 제거. `is_due()` / `get_chain_raw()` / `mark_refresh_started()` / `on_worker_done()` 추가. 상태 관리 전용 |
| `main.py` | `_poll_option_chain()`: 조건 체크 후 워커 기동 (~0ms). `_on_option_chain_done()`: result_ready 수신 |

### 핵심 설계 결정

**Cybos COM 메시지 라우팅**: BlockRequest 응답이 메인 스레드 Windows 메시지 큐를 경유 (api_connector.py 주석). QThread에서 호출 시 메인 Qt 이벤트 루프가 정상 펌핑 → 데드락 없음.

**COM STA 규칙**: `Dscbo1.OptionMst`를 워커 스레드 내에서 새로 `Dispatch()` — 메인 스레드 객체와 공유 안 함.

**이중 기동 방어**: `isRunning()` 체크 + `mark_refresh_started()` (5분 인터벌 락).

**실패 격리**: 워커 실패 시 빈 dict/빈 list 반환 → 이전 피처 유지, `_chain_raw` 무효화로 다음 기동 시 CpOptionCode 재수집.

### 검증 결과

순수 Python 로직 테스트 12개 + end-to-end 시나리오 6개 전부 통과 (COM 없는 환경).

---

## 2026-06-25 (248차 — EXIT stuck 무한루프 수정 + ManualExit override 확장)

### 발단

20260625_WARN.log에서 14:11~14:14 동안 `EXIT 부분체결 stuck` 경고가 매분 반복되며 수동 청산까지 차단된 현상을 딥다이브.

order_no=4280 (TP1 청산 2계약 주문, 1계약 체결 후 stuck). WARN 로그: `"EXIT partial fill timeout -> 브로커 잔량 확인 LONG 3 @ 1462.37, pending 유지"` 가 4분 이상 반복. 운영자 수동 청산(14:11:41, 14:12:05) 모두 차단.

### 근본 원인 (3가지 버그)

**Bug 1 — `last_fill_at` 무한 리셋** ([main.py:9771 이전](main.py)):
`_ts_resolve_stuck_exit_pending`이 브로커 잔량 확인 후 "아직 포지션 있음" 판단하면 `pending["last_fill_at"] = now()` 리셋 후 True 반환. 다음 분봉에서 `_since_last_fill ≈ 60s > 10s` → 동일 로직 재실행 → **무한 루프**.

**Bug 2 — ManualExit 차단** ([main.py:1916 이전](main.py)):
`_on_manual_exit_requested`가 `_has_pending_order()=True`이면 CB HALT일 때만 override 허용. 브로커가 잔량을 확인해준 stuck EXIT pending은 운영자가 아무것도 할 수 없음.

**Bug 3 — 오해 로그** ([main.py:3540 이전](main.py)):
"pending 소멸, 잔여 포지션 긴급청산 시도"라고 찍히지만 실제로는 조회 결과에 따라 소멸 여부가 결정되는 구조. `_ts_resolve_stuck_exit_pending`이 True 반환하면 소멸도 청산도 없음.

### 추가 발견 — Chejan 부분 유실 탐지 한계

오늘 케이스의 진짜 원인: order 4280 2계약이 **거래소에서 모두 체결** (broker 잔고=3), 그러나 **2번째 Chejan만 유실** (엔진 인식=1). `expected_remaining = prev_pos_qty - pending.qty` 검사는 전량 Chejan 유실만 탐지 가능. 부분 유실 시 prev_pos_qty가 이미 drift → 탐지 실패. → 3-confirm 카운터가 실질 fallback으로 커버.

### 수정 (248차, 커밋 `26f3d9f`)

| 위치 | 변경 내용 |
|---|---|
| `main.py:9779+` | `last_fill_at` 리셋 제거 → `_broker_confirm_count` 카운터. 3회 누적 시 CRITICAL 경고 + `_clear_pending_order()`. `_clear_pending_order`가 EXIT_PARTIAL 해소 시 IntrabarTPSchedule(300ms 후 TP 재점검) 자동 발동 |
| `main.py:1916+` | ManualExit: `_broker_confirm_count >= 1`(브로커 확인 완료)이면 stuck EXIT pending 강제 소멸 후 수동 청산 허용 |
| `main.py:3540` | 오해 로그 수정: "브로커 잔고 조회 후 처리 (소멸 여부는 조회 결과에 따름)" |

### 오늘 로그 기준 효과 시뮬레이션

| 시각 | 현재(수정前) | 수정後 |
|---|---|---|
| 14:11:00 | pending 유지, last_fill_at 리셋 | `_broker_confirm_count=1` |
| 14:11:41 | 수동 청산 차단 | `_stuck_exit=True` → **수동 청산 허용** |
| 14:12:00 | 동일 반복 | `_broker_confirm_count=2` |
| 14:13:00 | 동일 반복 | `_broker_confirm_count=3` → **자동 pending 소멸 + TP 재점검** |
| 14:14+ | 무한 지속 | 정상 종료 |

### 외부진입 청산 UI 분석 (4676/4678/4694)

- 외부진입 4676, 4678: `_ts_handle_external_fill` → `apply_entry_fill` → 평균가 재계산(1464.051, 1465.4008) 정확. 250ms/1200ms QTimer balance refresh. ✅
- 외부 청산 4694 (5계약 pending_miss): 비최종 4회는 `_ts_record_nonfinal_exit`(PnL 탭 즉시 갱신, 잔고 패널 갱신 없음), 최종 1회에서 `_ts_force_balance_flat_ui` + QTimer(250ms, 1200ms). 1~2초 지연은 허용 범위. ✅
- pending 4280 잔류: 4694 청산 완료 후에도 4280 pending 살아있음. position=FLAT이므로 balance 합성 억제 미적용. 14:25:00 다음 분봉에서 broker FLAT 확인 후 자동 소멸. ✅

### 향후 개선 권고

`pending['position_before_qty']` (int)를 `_set_pending_order` 시 저장, `expected_remaining` 계산 시 `prev_pos_qty` 대신 사용 → 부분 Chejan 유실도 1회 만에 탐지 가능. 현재는 3-confirm fallback으로 커버 중.

---

## 2026-06-25 (247차 — 프리장 scaler 재적합 window 단기화)

### 발단

20260625_WARN.log에서 EarlyWarmup 완료 후에도 z경고 폭증(23개)이 해결되지 않고 본장에 escape. 5일치 로그 및 실데이터 시뮬레이션으로 딥다이브.

### 근본 원인

모든 pre-market refit 경로(EarlyWarmup/PRE_MARKET_REFIT_STEPS/Canary/ScalerWarmup)가 `lookback_bars=500(SCALER_WARMUP_LOOKBACK_BARS)`을 동일하게 사용. 08:55 기준 500봉 = 어제 490봉 + 오늘 pre-market 10봉(2%) → scaler가 어제 분포 기준으로 재적합되어도 오늘 갭오픈 피처 z경고가 고착.

**실측 증거 (SYSTEM.log)**:
- 6/24: Phase1~3 refit 4회, z경고 `16→16→16→16` (0% 변화)
- 6/25: Phase1~3 + Canary 5회, z경고 `18→18→18→19→17` (1봉 개선)
- 결과: 6/24 EKS 발동 (`z경고33개+conf0%미달`)

### 수정 (247차, 커밋 `169b793`)

| 항목 | 내용 |
|---|---|
| `config/settings.py` | `PRE_MARKET_SCALER_BARS = 30` 신규 추가. `SCALER_WARMUP_LOOKBACK_BARS=500`은 장중 정기 refit 전용 유지 |
| `main.py` (5개 경로) | EarlyWarmup / PRE_MARKET_REFIT_STEPS worker / Canary refit / ScalerWarmup → `lookback_bars=PRE_MARKET_SCALER_BARS(30)` 변경 |
| Canary refit | 완료 후 z경고 재측정 로그 추가 (`z경고 →N개 ✓임계이하` or `⚠z경고 지속`) |

### 30봉 구성 (실측)

| 시점 | 어제 구간 | 오늘 PM | 오늘 비율 |
|---|---|---|---|
| EarlyWarmup 08:45 | 14:40~15:09 (30봉) | 0봉 | 0% |
| bar3 08:48 | 14:43~15:09 (27봉) | 3봉 | 10% |
| bar10/Canary 08:55 | 14:50~15:09 (20봉) | 10봉 | 33% |
| bar14 08:59 | 14:54~15:09 (16봉) | 14봉 | **47%** |

어제 종가구간(14:40~15:09)은 pre-market과 미시구조 유사(저유동성·포지션 정리) → scaler mean이 오늘 분포에 빠르게 수렴.

### 검증 결과

**시뮬레이션 (5일 실데이터 기반)**:

| window | bar5이후 z<12 달성율 | 6/23 | 6/24 | 6/25 |
|---|---|---|---|---|
| 500봉(기존) | 0% | 20 | 29 | 14 |
| 60봉(1차시도) | 33% | 13 | 16 | 11 |
| **30봉(채택)** | **100%** | **5** | **4** | **8** |

60봉 불채택: 6/25 bar3에서 z 악화 회귀(14→26). 30봉은 전 케이스 bar5 이후 임계(12) 이하.

### 호환성

- CORE 피처 영향 없음 (`cvd_direction` zero-std는 30봉·60봉 동일)
- `opt_pcr_*` 7개 추가 zero-std → 비CORE, `scale_=1.0` 안전 처리
- 장중 `D_FORCE/B_OPEN/ExchangeCB/B_INTRADAY` refit: `SCALER_WARMUP_LOOKBACK_BARS=500` 유지
- D_FORCE(약 90분 후) 재적합으로 pre-market scaler 자동 복원

---

## 2026-06-25 (246차 — Phase C pkl-모델 불일치 근본 수정)

### 발단

245차 수정(SGD 방어 코드) 이후에도 09:00~10:36 동안 ERR-FATAL이 지속됐음을 WARN.log 딥다이브로 확인.
245차는 증상(ERR-FATAL 크래시)을 막았지만 근본 원인(불일치 상태 자체)은 미해결이었다.

### 근본 원인 (20260625_WARN.log 분석)

**타임아웃 SIGKILL이 모델·pkl 원자성을 파괴하는 시나리오**:

```
09:16:48  장중 재시작 → WarmupRetrain 기동
           (내부: _train_horizon → gbm_{h}.pkl 저장 완료)
09:27:59  GBM-64 10분 타임아웃 강제 해제 (subprocess SIGKILL)
           ↓ _save_feature_names() 미실행
           gbm_{h}.pkl = 새 97개 모델
           feature_names_{h}.pkl = 기존 12개 (미갱신)
           → 다음 _load_all(): _hz_feat_indices=12 + clf.n_features_in_=97 → 불일치
```

**장전 Canary refit 흐름 버그**:
- 08:55 z경고 23개 → Canary refit 기동 → `_scaler_refresh_running=True`
- ScalerWarmup: `_scaler_refresh_running=True` → else 분기 → `_warmup_done_event.set()` 즉시 (refit 완료 안 기다림)
- Canary refit 완료해도 `_pre_market_scaler_refitted` 미설정 → 재시작 로그 `pre_market_scaler=False`

### 수정 (246차, 커밋 `1242963`)

| Fix | 파일 | 내용 |
|---|---|---|
| FIX-A | `model/multi_horizon_model.py` | `_load_all()`에서 pkl·GBM 피처 수 비교 → 불일치 시 `.mismatch_bak` 백업 후 97개 fallback (`os.replace` — Windows 안전) |
| FIX-B | `learning/batch_retrainer.py` | `_save_model()` 내부에서 모델 저장 직후 `feature_names_{h}.pkl`도 원자적 동시 저장. 피처 수 변경 감지 경고 로그 추가. `replaced=False`시 외부 `_save_feature_names` 차단 (EOD·인트라 두 경로) |
| FIX-C | `main.py` | Canary refit 성공 시 `_pre_market_scaler_refitted=True` 설정 |
| FIX-D | `main.py` | `_scaler_refresh_running=True`일 때 즉시 event set 대신 `_wait_refit_done` 스레드로 완료 대기 후 set. 대기 상한 85초 (wait timeout 90초 대비 마진 5초) |

### 커밋 이력 교차검증 결과

- 245차 커밋은 **11:04**에 적용됨 → 09:00~10:36 ERR-FATAL은 수정 전 코드에서 발생한 것 확인
- 불일치의 직접 원인: **243차(08:03)** — Phase 2 경로에 `_save_feature_names` 최초 추가 → 같은 날 09:27 SIGKILL로 즉시 불일치 발생
- Canary/ScalerWarmup 영역에서 104·105·201·203·245·246차까지 동일 구조 버그 6회 반복 → 비동기 스레드 완료-플래그 경쟁이 구조적 취약점

---

## 2026-06-25 (245차 — SGD 스케일러 피처 수 불일치 ERR-FATAL 버그 수정)

### 증상

장중 운영 중 아래 에러가 매 분봉마다 반복 발생 (09:50~10:15+), 자동진입 OFF + 15분 쿨다운 누적:

```
[ERR-FATAL] minute_pipeline: X has 11 features, but StandardScaler is expecting 97 features
```

에러 숫자: 11 (10m/30m), 12 (1m/3m), 15 (5m/15m) — `feature_names_hz_*.pkl` 크기와 정확히 일치.

### 근본 원인 (로그 traceback 확인)

```
main.py:6272  run_minute_pipeline  (SGD 지연 학습 구간)
  → online_learner.py:136  learn()
      → scaler.partial_fit(x2d)   ← ValueError 발생
```

**에러 체인**:
1. `_hz_feat_indices`가 없거나 특정 호라이즌이 없는 타이밍에 SGD 학습 실행
2. `_h_idx_learn = None` → `_dx_learn = _dx_full` (97개 전체) → `scaler.partial_fit(97개)` → 스케일러 97개로 굳음
3. 이후 `_hz_feat_indices` 복원 → Phase C 슬라이싱 피처 11~15개 투입
4. `scaler.partial_fit(11개)` but `scaler.n_features_in_=97` → **ValueError 반복**

`online_learner.learn()`에는 피처 수 방어 코드가 없었음.

### 수정 (`learning/online_learner.py`)

`learn()` 내 `scaler.partial_fit()` 호출 전, `n_features_in_` 불일치 시 `_do_sgd_reset()` 자동 실행:

```python
if hasattr(scaler, "n_features_in_") and scaler.n_features_in_ != x2d.shape[1]:
    logger.warning("[OnlineLearner] %s 피처 수 불일치(scaler=%d, x=%d) → 리셋", ...)
    self._do_sgd_reset(horizon)
    scaler = self.scalers[horizon]
```

재시작 후 첫 불일치 감지 시 경고 로그 1회 출력 후 이후 ERR-FATAL 없이 정상 실행.

**커밋**: (245차)

---

## 2026-06-24 (242차 — V8 Phase 2 완료 점검 + 재학습 재실행)

### 배경 — V8 구현 상태 커밋 이력 전수 점검

커밋 이력으로 Phase 2 재학습 공백 기간 확인:
- 6/8 (121차): Backfill + `eod_retrain.py --phase2 --weeks 10` 최초 실행 완료
- 6/11 (163차): HistGBM 전환으로 전 모델 재학습 — `EOD_RETRAIN.bat`에 `--phase2` 없어 레거시 경로로 덮어씌워짐
- 6/17~6/24: py310_64 스케줄러로 매일 레거시 경로 재학습 → Phase 2 모델 사실상 초기화 상태

### 수정 1: EOD_RETRAIN.bat `--phase2` 영구 추가

```bat
- python scripts\eod_retrain.py --weeks 10
+ python scripts\eod_retrain.py --phase2 --weeks 10
```

**커밋**: 1293022

### 수정 2: Phase 2 재학습 재실행 (22:14~22:17)

```
python scripts\eod_retrain.py --phase2 --weeks 10
```

| 호라이즌 | 구 정확도 | 신 정확도 | 개선 |
|---|---|---|---|
| 1m | — | — | 건너뜀 (raw_features_horizon에 1m 없음, 설계 정상) |
| 3m | 0.4474 | 0.5245 | +7.7%p |
| 5m | 0.3921 | 0.5370 | +14.5%p |
| 10m | 0.4222 | 0.5541 | +13.2%p |
| **15m** | 0.3305 | **0.6165** | **+28.6%p** |
| **30m** | 0.2909 | **0.5984** | **+30.7%p** |

5/6 호라이즌 교체 완료, 소요 2.3분. 30m FLAT 편향 구조적 해소 효과 발현.

### 수정 3: TRAINING_WINDOW_BARS 구현 (`learning/batch_retrainer.py`)

V8 Phase 2-D 항목. 호라이즌별 학습 데이터 상한 상수 + `_retrain_phase2` 내 트림 로직.

```python
TRAINING_WINDOW_BARS = {
    "1m": None, "3m": 5000, "5m": 3000,
    "10m": None, "15m": None, "30m": None,
}
```

- V8 원안(90/60/48)은 배치 MIN_BARS 미달로 실효 없어 현실적 값으로 조정
- 현재(3m=5330봉): window=5000 조건 충족 → 최신 5000봉 우선 트림 활성화
- Stage 3(50일+) 이후 단기 모델 최근 레짐 집중 효과 발현

**커밋**: 1e32131

### V8 잔여 항목 최종 판정

| 항목 | 판정 |
|---|---|
| SGD 호라이즌별 feat_vec | **구현 불필요** — B군 교체 방식(main.py:6190~6222)이 미래 오염 없는 최종 설계 |
| multi_timeframe.py deprecate | **Stage 2(~7/8) 때 삭제** — 현재 프로젝트 전체 임포트 없음, dead code |

### V8 전체 완료 상태 (2026-06-24 기준)

- Phase 0·1·2 코드 전 항목 완료
- Phase 2 재학습: Stage 1 완료 (6/8 최초 + 6/24 재실행)
- Phase 3: Platt Scaling·역방향 서브모델·MFE 레이블 → 안정화 후 대기

**커밋**: e7c5e90, e872899 (V8 문서 업데이트)

---

## 2026-06-24 (241차-b — 1m SGD DN 편향 모니터링 강화)

### 배경 — 1m 정확도 하락 원인 딥다이브

6/8 완성봉 커밋 전후 비교: 1m acc 0.389 → 0.342 (−0.047).
N분봉 피처 오염 가설을 검증한 결과 **기각**:
- `feature_names_1m.pkl` 존재 (12개, opt 피처 없음)
- GBM `n_features_in_=12` ✅ JSON 슬라이싱 정상 작동

**진짜 원인 — SGD 온라인 학습 DN 편향 누적:**

```
날짜    예측DN%  실제DN%   Δ       acc
6/16    59.9%   27.7%   +32.2%⚠  0.270
6/17    47.8%   19.9%   +27.8%⚠  0.306
6/18    59.2%   21.6%   +37.6%⚠  0.291
6/24    63.3%   35.7%   +27.5%⚠  0.288
```

이 날들: 예측 FLAT 6~11%, 실제 FLAT 30~43% → 시장 횡보 봉을 DN으로 오분류.
기존 BiasReset 임계(0.70)와 로그 경보(0.75)가 모두 이 범위(0.47~0.64) 위에 있어 완전 무감지.

### 수정 4종 (`main.py`, 241차 = 62e66b4)

#### ① `_bias_buf` maxlen 호라이즌별 분리

```python
_BIAS_MAXLEN = {"1m": 45, "3m": 30, "5m": 30,
                "10m": 20, "15m": 15, "30m": 10}
```

1m=45분: SGD 누적 편향을 더 넓은 증거 기반으로 감지.

#### ② 로그 경보 임계 하향

```python
# 기존: 0.75 (UP/DN/FL 동일)
if _up_r >= 0.60:  _bias_tag = "[UP편향⚠ XX%]"
elif _dn_r >= 0.60: _bias_tag = "[DN편향⚠ XX%]"
elif _fl_r >= 0.65: _bias_tag = "[FL편향⚠ XX%]"  # FL만 0.65
```

실측 편향 범위(0.47~0.64) 가시화. FL은 자연 발생 빈번해 0.65 유지.

#### ③ BiasReset 임계 1m 전용 하향

```python
_BIAS_RESET_THR = {"1m": 0.62}   # 나머지 0.70 유지
_bias_thr_h = _BIAS_RESET_THR.get(_h, 0.70)
```

6/24 DN 63.3% → 0.62 이상이므로 BiasReset 발동 가능.

#### ④ 1m acc 임계 + streak 조정

```python
_acc_ok_for_bias = _acc_h < (0.50 if _h == "1m" else 0.55)
_dn_up_streak = 8 if _h == "1m" else 5   # 오발동 방지
```

임계 하향(0.62) 보상: streak 8분으로 연장, acc 0.55→0.50으로 강화.

### 발동 조건 비교

| 날짜 | DN% | 기존 반응 | 수정 후 반응 |
|---|---|---|---|
| 6/16 59.9% | 미발동 | `[DN편향⚠]` 로그 |
| 6/18 59.2% | 미발동 | `[DN편향⚠]` 로그 |
| 6/24 63.3% acc<0.50 8분 | 미발동 | **BiasReset + SGD reset** |

### 내일 로그 확인 포인트

- `[DN편향⚠ XX%]` 출력 시작: 로그 경보 정상
- 8분 지속 + acc<0.50: `[BiasReset] 1m DN편향 → uniform fallback 적용`
- 1m acc 개선 여부 (목표: 0.342 → 0.360+)

**커밋**: 241차-b (62e66b4)

---

## 2026-06-24 (241차 — 장마감 종료·EOD 흐름 점검 + EOD_RETRAIN.bat py310_64 수정)

### 작업 내용

장마감 후 프로그램 종료 흐름과 EOD 흐름 전체를 점검(코드 리뷰·실측 상태 확인).

**종료 흐름 확인 (코드 리뷰)**:
- 15:10 강제 청산 → 15:18 FINAL_CLOSE 안전망 → 15:40 DailyClose 스레드 기동 → `_shutdown_sig.request.emit()` → QTimer 15초 → `_qt_app.quit()` → 런처 `_exit_normally` 감지 → AUTO-RESTART 중단
- `daily_close()` 내부 순서 22단계 전체 확인 (통계·보정기 저장·리셋·DBWriter 플러시·WAL 체크포인트 등)

**오늘(2026-06-24) 실측 상태**:
- `auto_shutdown_done_date = 2026-06-24` — 자동 종료 정상
- `eod_retrain_ok_date = 공백` — daily_close(15:40)가 마커 체크 시 retrain_eod.py 미완료(완료 15:48:17), 설계상 정상. 내일 PreRetrain fallback(마커 파일 1~5일 전 탐색)으로 자동 보완
- `p8_last_success_date = 2026-06-24` — P8 스케일러 재적합 완료
- EOD 마커: 6/6 호라이즌 교체, 193.8초

**수정: EOD_RETRAIN.bat py310_64 수정 (커밋 2de2afc)**:
- `EOD_RETRAIN.bat:17` `conda activate py37_32` → `py310_64` (191차 결정 실제 반영)
- `CLAUDE.md` 운영 환경 섹션에 note 추가 — EOD_RETRAIN.bat·scripts/eod_retrain.py 모두 py310_64 전용임을 명시, 재거론 방지

**커밋**: 241차 (2de2afc)

---

## 2026-06-24 (240차 — MetaConf CONF_HIGH 재보정 + 임계값 하향)

### 배경 — MetaConf 딥다이브 분석

최근 10일 `ensemble_decisions.meta_confidence` (= blended_conf) 분포:
- 평균=0.38, P75=0.42, P90=0.46, P95=0.49, 최대=0.63
- 기존 take_thr(A=0.50, C=0.52) 달성: P90~P95 수준 → 구조적으로 불가

meta_action 분포: skip 49.5% / reduce 49.4% / take **1.1%** (17건, 전부 규칙 기반 fallback)

**근본 원인**: `CONF_HIGH=0.60`이 실측 avg_ens_conf(0.37)보다 높아
- Q3(맞음+고신뢰, conf≥0.60): **0.2%** — 거의 발생 안 함
- Q1(틀림+저신뢰): **67.1%** 지배
- → LR 출력이 0.33~0.67 협소 구간에 고착, 변별력 없음
- → take_thr에 도달하는 신호 = 0건

### 수정 1: CONF_HIGH 재보정 (`learning/meta_confidence.py:69`)

```python
# 기존
CONF_HIGH = 0.60

# 수정: avg_ens_conf(0.37) 기준 — 최대 쌍봉 분리점
CONF_HIGH = 0.37
```

CONF_HIGH=0.37 적용 시 품질 레이블 분포:
- Q0(틀림+고신뢰): ~65% → weight 0.0 (나쁜 신호 0점)
- Q3(맞음+고신뢰): ~28% → weight 1.0 (좋은 신호 만점)
→ 쌍봉 분포: LR이 0.0 vs 1.0 극단값 학습 → 변별력 10배 기대

### 수정 2: `_FEATURE_VERSION` 4→5 (`learning/meta_confidence.py:73`)

CONF_HIGH 변경 = 레이블 분포 완전 재편 → 구버전 pkl warm-start 자동 거부.
버전 불일치 감지 시 cold-start 강제 (기존 load() 로직 재활용).

### 수정 3: 임계값 하향 (`strategy/entry/meta_gate.py`)

| 등급 | take_floor 전→후 | take_ceil 전→후 | reduce_base 전→후 |
|---|---|---|---|
| A | 0.50 → **0.43** | 0.67 → **0.55** | 0.33 → **0.27** |
| B | 0.51 → **0.44** | 0.68 → **0.56** | 0.34 → **0.28** |
| C | 0.52 → **0.45** | 0.70 → **0.57** | 0.36 → **0.30** |

CONF_HIGH=0.37 후 좋은 신호 blended_C ≈ 0.60×0.37 + 0.40×0.80 = 0.54 → take_ceil=0.57 달성 가능.

### 수정 4: meta_conf_state.pkl 삭제

구버전 레이블(Q1/Q2 편중) 오염 제거. 다음 기동 cold-start → 30봉 후 재학습.

### 예상 효과 (3~5거래일 후 확인)

- meta_action take 비율 1% → **5~15%** 달성
- blended_conf P90 0.46 → **0.50+** 도달
- reduce 50% → 더 의미 있는 size 조절로 작동

**커밋**: 240차 (a36c04b)

---

## 2026-06-24 (239차 — C급 자동진입 conf_floor 차단)

### 배경

C등급 `auto_entry=False`이므로 `checklist.py`의 conf_floor 체크(`if auto_entry and conf < 0.33`)가
실행되지 않음. P5 C급 실험 경로(`main.py:5909`)가 conf_floor 없이 직접 진입.
오늘 6/24 14:04 (conf=0.2701, C등급) 진입이 이 경로로 실행 → -1,271,185원 손실.

최근 5일 영향 분석:
- C급 실행 11건 중 floor 미달(conf<0.33): 4건
- 차단 대상 PnL: **-1,986,557원** (승률 1/3)
- floor 통과 건 PnL: **+1,108,312원** (승률 9/13)

### 수정 (`main.py`)

1. `ENS_CONF_FLOOR_FOR_AUTO` import 추가
2. C급 경로 내 hurst_ready 체크 다음에 `elif confidence < ENS_CONF_FLOOR_FOR_AUTO:` 차단 추가

```python
# C급 P5 경로 진입 필터 순서
#   ① hurst_ready=False → 차단 (237차)
#   ② conf < 0.33       → 차단 (239차) ← 신규
#   ③ 둘 다 통과         → _execute_entry
```

**커밋**: 239차 (6ff7bc6)

---

## 2026-06-24 (238차 — Platt 보정기 피드백 루프 버그 수정)

### 배경 — ensemble_calibrator.pkl 분석

Platt A/B 값 확인 결과:
- A = -0.0016 (사실상 0), B = -1.3245
- conf 0.30~0.80 전체 구간에서 출력 = **0.21 상수**
- 훈련 데이터(probs): 0.2099~0.2901 범위 (정상이라면 0.30~0.85 범위여야 함)

### 근본 원인 — calibrated conf 피드백 루프

```
STEP 6: raw_conf 0.44 → calibrate() → 0.21
        _ensemble_conf_cache[ts] = 0.21  ← calibrated 값 저장 (버그)
STEP 1: record_ensemble_outcome(0.21, correct)  ← calibrator가 자신의 출력으로 학습
fit(): probs=[0.21,0.21,...] 범위 없음 → A≈0 → 다음에도 0.21 → 무한 루프
```

`decision["confidence"]` (calibrated)를 캐시에 넣었는데,
이것이 1분 뒤 calibrator의 훈련 입력으로 들어가는 구조적 버그.

### 수정 (`main.py:4749`)

```python
# 기존 (버그): calibrated conf 저장 → 피드백 루프
self._ensemble_conf_cache[ts] = (float(confidence), ...)

# 수정: raw conf 저장 → calibrator가 원본 확률로 학습
self._ensemble_conf_cache[ts] = (
    float(decision.get("confidence_raw", confidence)), ...
)
```

`decision["confidence_raw"]`는 `ensemble_decision.py:840`에서 Platt 통과 전 원본값.

### 오염된 pkl 삭제

`data/ensemble_calibrator.pkl` 삭제 (훈련 데이터 probs가 0.21~0.29 오염 상태).
다음 기동 시 cold-start → 80건 누적 후 정상 재학습.
cold-start 기간(~80분): 3m 호라이즌 fallback calibrator 또는 raw_conf 그대로 사용.

### 예상 효과

- 수일 내 Platt A가 의미 있는 음수 기울기로 수렴 (raw conf 높을수록 보정 눌러줌)
- calibration_metrics.json ECE 0.13 → 장기적으로 0.06 이하 목표
- 진입 임계값이 실제 정확도와 연동되기 시작

**커밋**: 238차

---

## 2026-06-24 (237차 — Hurst 미계산 자동진입 차단)

### 배경 — 6/8 완성봉 커밋 전후 딥다이브 분석 결과

6/8 N분봉 완성봉 구조(120차) 커밋 이후 6/10~6/12에 발생한 -2,923,240원 손실(전체 누적 손실의 162%)을
trades DB `hurst_bucket=""` 공백 7건이 설명함.

- hurst_bucket이 ""인 것은 `_entry_hurst_bucket` 초기값("")에서 변경되지 않은 채 진입된 것
- `_entry_hour_bucket=0`도 동일 (초기값 0, 실거래는 9~15시이므로 0은 미설정 상태)
- 두 값 모두 공백/0인 거래 = P2-b 셋업 컨텍스트 블록을 우회한 진입 (수동 또는 C급 경로)

근본 원인: C급 실험 진입 경로(5905~)에 P2-b setter가 없었음 + Hurst 실계산 완료 여부를 
feature_builder가 외부에 알리지 않아 워밍업 미완료 상태에서 진입 가능.

### 수정 1: `features["hurst_ready"]` 플래그 추가 (`features/feature_builder.py:354`)

```python
# 기존
features["hurst"] = calculate_hurst(...)  # 예외 시 0.5 반환

# 수정
features["hurst"] = calculate_hurst(...)
features["hurst_ready"] = True   # 실계산 성공
# except:
features["hurst"] = 0.5
features["hurst_ready"] = False  # 데이터 부족·오류 → 미계산
```

`calculate_hurst`가 정상 계산됐는지 여부를 feature dict에 명시.
예외 분기(데이터 부족, NaN 등)는 hurst_ready=False로 표시.

### 수정 2: A/B 자동진입 경로에 hurst_ready 차단 (`main.py:5875`)

```python
else:  # JointGateBlock 미발동
    # [237차] Hurst 미계산 차단
    if not features.get("hurst_ready", False):
        log "차단 — 워밍업 중 자동진입 차단"
    else:
        _qty_auto 클리핑 → _execute_entry
```

### 수정 3: C급 실험 경로에 P2-b setter + hurst_ready 차단 (`main.py:5916`)

```python
# [237차] P2-b 셋업 컨텍스트 추가 (기존 C급 경로에 누락)
self._entry_hurst_bucket = "trend"/"neutral"/"mean-revert"
self._entry_hour_bucket = now().hour
self._entry_was_restart = ...
self._entry_had_partial = 0
# [237차] Hurst 미계산 시 C급도 차단
if not features.get("hurst_ready", False):
    log "C급 자동진입 차단"
else:
    _execute_entry
```

### 예상 효과

- hurst="" / hour=0 공백 거래 재발 방지
- 워밍업 미완료 구간(장 시작 약 40봉 이내) 자동진입 차단
- 차단 시 SIGNAL 로그: `[차단] Hurst 미계산 — 워밍업 중 자동진입 차단 (hurst=0.500)`

**커밋**: 237차

---

## 2026-06-24 (236차 — 저신뢰 자동진입 차단 3중 안전장치)

### 배경 — 6/24 일중 거래 분석

일중 3건 거래 중 Case 3 (14:04 LONG conf=27%, -1,271,185원)가 최대 손실.  
5거래일 SIGNAL 로그 분석 결과 conf<35% 신호의 기댓값 = **-34K/건** (승률55%지만 손실이 이익보다 38% 큼).

### 수정 1: ENS_CONF_FLOOR_FOR_AUTO = 0.33 (`config/settings.py`)

conf<33% 시 체크리스트 A/B 등급이어도 `auto_entry=False` 강제.
대시보드에는 원래 등급(A/B) 표시 → 수동 확인은 가능, 자동 실행만 차단.

### 수정 2: Degraded Mode 1-사이클 지연 버그 수정 (`main.py`)

`_emit_runtime_health`가 파이프라인 끝(STEP 9)에서 호출되어 진입 체크(STEP 6)보다 항상 1사이클 늦는 구조적 결함 수정.

- `_is_degraded_entry_blocked`에 `latency_ms, quality_score, cache_age_sec, exception_density_10m` 파라미터 추가
- lookahead: `_health_warn_streak + 현재사이클 가중치 ≥ enter_thresh` 이면 선제 차단
- `self._last_pipe_ms` 파이프라인 끝에서 매 사이클 저장

### 수정 3: MetaGate×ToxicityGate 동시 reduce 차단 (`main.py`)

`_meta_size × _tox_size < 0.50` + 두 게이트 모두 `reduce` → `_joint_blocked=True`, `_execute_entry` 스킵.  
6/24 14:04 케이스: meta=0.58, tox=0.70 → 합산 0.406 → 차단.

**커밋**: 236차 (894151b)

---

## 2026-06-24 (235차-d — connect_broker pt_value 갱신 누락 수정)

### 배경 — 재시작 후 이상점 점검에서 발견

235차 시리즈(미니선물 전용 설정 교정) 커밋 5개 검증 중 `connect_broker` 구현 누락 발견.

### 수정 1: `self._pt_value` + `position.set_pt_value()` 갱신 누락 (`main.py`)

`connect_broker` 내 계약 스펙 적용 블록에서 `set_tick_size`만 호출되고
`self._pt_value` 및 `self.position.set_pt_value()` 갱신이 누락되어 있었음.

```python
# 기존 (누락)
self.feature_builder.set_tick_size(_spec["tick_size"])

# 수정
self.feature_builder.set_tick_size(_spec["tick_size"])
self._pt_value = _spec["pt_value"]          # 추가
self.position.set_pt_value(self._pt_value)  # 추가
```

주석에는 "connect_broker에서 get_contract_spec으로 재확정"이라 명시되어 있었으나
실제 구현이 없던 상태. 현재 미니선물 운영에서는 초기값 50,000이 정확해 실영향 없음.
미륵이2(일반선물) 기동 시 pt_value가 50,000으로 고정되어 PnL 5배 오류 발생할 뻔.

### 수정 2: feature_builder.py line 34 주석 교정

"기본값은 일반선물(0.05)이나" → "기본값은 미니선물(0.02);" (235차-b 교체 후 미갱신)

### 수정 3: main.py 미사용 임포트 제거

`FUTURES_PT_VALUE` — 235차-b에서 초기화를 MINI_FUTURES_PT_VALUE로 바꾼 뒤 임포트 잔존.

**커밋**: 235차-d (3169a8d)

---

## 2026-06-24 (234차 — 재시동 프로세스 미종료 버그 수정 + 종목변경 배지)

### 배경 — X버튼 재시작 후 프로세스 미종료 원인

오늘 08:40 자동 스케줄러 기동 시 GUARD에서 기존 main.py 프로세스(전날 세션)가 살아있어 취소됨.
229차-b에서 도입한 `super().closeEvent(event)`만으로는 차트 다이얼로그 등 다른 Qt 윈도우가 남아있을 때
`quitOnLastWindowClosed` 자동 종료가 트리거되지 않아 Python 프로세스가 살아있게 되는 구조적 결함 확인.

### 수정 1: closeEvent QApplication.quit() 명시 호출 (`dashboard/main_dashboard.py`)

```python
# 기존: super().closeEvent(event)
# 수정:
super().closeEvent(event)          # Qt WA_DeleteOnClose 등 기본 처리 보존
QApplication.instance().quit()    # 이벤트 루프 강제 종료 (다른 윈도우 무관)
```

### 수정 2: run() exec_() 후 sys.exit(0) 추가 (`main.py`)

```python
_qt_app.exec_()
import sys as _sys
_sys.exit(0)  # COM 비데몬 스레드가 프로세스 붙잡는 경우 방지
```

### 수정 3: 종목변경 재시작 배지 (`dashboard/main_dashboard.py`, `main.py`)

- `lbl_code_change` 배지: 기동 코드 ≠ UI 선택 코드일 때만 표시
- 클릭 → FLAT 확인 + 15:10 이전 체크 후 `quit()` (AUTO-RESTART 경유 재시작)
- `_exit_normally` 미생성 → 런처 AUTO-RESTART 발동

**커밋**: 234차 (64ad55e)

---

## 2026-06-24 (233차 — DailyClose _exit_normally 즉시 생성 + GUARD 장전 자동 Y)

### 배경

오늘 08:40 스케줄러 자동 기동 시 GUARD 기본값이 N(10초, 228차-c)이어서
기존 프로세스가 있을 때 자동 취소됨 → 재시동 실패.

### 수정 1: DailyClose 즉시 플래그 생성 (`main.py`)

`daily_close()` 완료 즉시 `_write_exit_normally_flag("daily_close")` 호출.
기존 경로(_auto_shutdown Qt 타이머 15초 지연)는 타이머 미실행/예외 시 플래그 누락 가능.

### 수정 2: GUARD 장전/장중 분기 (`start_mireuk_Cybos.bat`)

- 장전(09:00 이전): CHOICE /D **Y** 10초 자동 → 스케줄러 무인 기동
- 장중(09:00 이후): 타임아웃 없이 사용자 직접 선택 (실수 방지)

**커밋**: 233차 (3d33950)

---

## 2026-06-24 (232차 — macro_risk_off·on·event_flag ScaleFloor 추가)

### 배경 — 금일 장 시작 EKS 발동 원인 딥다이브

오늘(06-24) 09:05:57 EKS(Early Kill Switch) 발동 → 당일 관망 선언.
원인 분석 중 `macro_risk_off` z=+15.78σ가 D_FORCE 연속 트리거 악순환 원인임을 확인.

### 근본 원인

`macro_risk_off`는 이진(0/1) 피처 (`vix>28 or sp500<-1%`).
192차에서 AutoMask CORE 면제는 추가했으나 `_MACRO_SCALE_FLOOR` 등록이 누락됨.

발동 시퀀스:
```
warmup 500봉: risk_off=0 전부 → raw_std=0.0000 → identity 강제 ✅
B_OPEN 재적합: raw_std=0.0447 < 0.05 임계 → identity 강제 ✅
D_FORCE 재적합(09:01): risk_off=1 봉 1~2개 → raw_std=0.063 > 0.05
  → identity 강제 해제, ScaleFloor 미등록
  → z = (1.0 - ≈0.004) / 0.063 ≈ +15.8σ (로그 +15.78σ 일치)
  → 5분마다 D_FORCE 재트리거 악순환
  → EKS 발동 원인 중 하나
```

### 수정 (`model/multi_horizon_model.py:178`)

`_MACRO_SCALE_FLOOR`에 이진 피처 3종 추가:

```python
"macro_risk_off":   0.50,   # 이진(0/1) — 희귀 발동 시 σ≈0.06 → z≈16 폭발 방지
"macro_risk_on":    0.50,   # 이진(0/1) — 동일 구조
"macro_event_flag": 0.50,   # 이진(0/1) — 동일 구조
```

floor=0.5 근거: 이진 피처 이론 최대 σ=0.5(p=0.5) → z=(1−mean)/0.5 ≤ 2.0 (AutoMask 임계 4.0 미만).

### 반영 시점

재시작 불필요. 다음 ScalerRefresh(D_FORCE 또는 C_PERIODIC 30분 주기) 시 `_apply_macro_scale_floor()` 자동 적용.

### 예상 효과 (내일 로그 확인 포인트)

- `[ScalerFloor] macro_risk_off scale=0.063 → floor=0.50 적용` 출현 (급락 당일)
- `macro_risk_off` z-score ≤ 2.0 (이전 +15.78σ)
- D_FORCE 연속 트리거 없음 (macro_risk_off consec=5 트리거 미발생)
- EKS 발동 억제 (장 초반 급락 시에도 z경고 수 감소)

**커밋**: 232차 (4238538)

---

## 2026-06-24 (232차-b — EKS 해제 직후 GBM 재학습 트리거)

### 배경 — WarmupRetrain 미실행 구조 분석

코드 추적 결과: 장전(08:00~08:59) 기동 시 `_warmup_retrain_pending=True`가 설정되지만,
`pre_market_setup()` 내 장중 재시작 블록(L2368) 조건 `09:00 <= t`에 미달 → 미실행.
08:55 PreRetrain 블록(L3101)이 `_warmup_retrain_pending`을 소비하면서 `_eod_retrain_ok=True`
(전날 EOD 성공) 이유로 스킵 → STEP3에서도 `_warmup_forced=False` → 하루 종일 전날 모델 유지.

이 자체는 버그 아님(설계대로). 단, EKS 관망 중 DriftRetrain도 미발동(acc30m 미축적)되어
EKS 해제 후 첫 진입까지 당일 데이터 미반영 공백이 생기는 잠재 이슈.

### 수정 (`main.py:5309`)

`try_eks_recovery()` True 반환 직후(EKS 해제 확정 시점) GBM 경량 재학습 즉시 트리거:

```python
if not getattr(self, "_gbm_retrain_running", False):
    self.dashboard.set_model_status("GBM 재학습중(EKS해제)...")
    log_manager.system("[SHS-EKS] EKS 해제 → GBM 경량 재학습 시작 (관망 구간 데이터 반영)", "INFO")
    self._start_gbm_retrain_subprocess(
        force=False, reason="EKS 해제 후 즉시 재학습", is_warmup=False, intraday=True,
    )
```

중복 실행 차단은 `_start_gbm_retrain_subprocess()` 내부(`_gbm_retrain_running` 체크)에서 처리.

### 예상 효과 (내일 로그 확인 포인트)

- `[SHS-EKS] EKS 해제 → GBM 경량 재학습 시작` 출현 (EKS 해제 시)
- `[GBM-64] subprocess 완료 (returncode=0)` 출현
- EKS 해제 후 첫 진입 시 당일 데이터 반영 모델 사용

**커밋**: 232차-b (ca55a8c)

---

## 2026-06-24 (233차 — DailyClose _exit_normally 즉시 생성 + GUARD 장전 자동 Y)

### 배경 — 08:40 자동 스케줄러 GUARD 취소 원인 분석

PC 환경: EOD 후 power off → 08:30 power on → 08:40 자동 스케줄러 실행.
launcher_20260624_084001 로그에서 GUARD가 기존 main.py 감지 → 10초 N 기본값 → 자동 취소.
08:47:14 사용자가 수동으로 Y 선택 후 정상 기동.

전날 DailyClose 후 `_exit_normally` 파일이 생성됐어야 하는데, `_auto_shutdown()`이
Qt 타이머(15초 지연) 경유이므로 타이머 미실행·예외 시 플래그 누락 가능.
플래그 없으면 런처가 `15:10 이후 종료 → 재시작 안 함`으로 처리하고 종료되지만,
잔류 프로세스(스케줄러 중복 기동 등)가 있을 때 GUARD에 걸림.

### 수정 1 (`main.py:7317`)

`daily_close()` 마지막 `emit()` 직전에 즉시 플래그 생성:
```python
self._write_exit_normally_flag("daily_close")
_shutdown_sig.request.emit()
```

### 수정 2 (`start_mireuk_Cybos.bat:270`)

GUARD CHOICE를 현재 시각 기준으로 분기:
- 09:00 이전(장전): `CHOICE /D Y /T 10` — 10초 후 자동 Y, 스케줄러 무인 처리
- 09:00 이후(장중): `CHOICE /N` (타임아웃 없음) — 사용자 직접 선택, 실수 방지

### 예상 효과 (내일 로그 확인 포인트)

- `[Shutdown] 정상 종료 플래그 기록: data/_exit_normally (daily_close)` 출현
- 다음날 런처에서 `[AUTO-RESTART] 정상 종료 감지 (daily_close) -- 재시작 안 함` 출현
- 08:40 자동 스케줄러 GUARD 통과 (`[GUARD] 기존 main.py 없음 — 단일 인스턴스 확인.`)

**커밋**: 233차 (3d33950)

---

## 2026-06-24 (234차 — 종목변경 재시작 배지)

UI 종목코드/시장구분 변경 후 런타임 `_futures_code`가 갱신되지 않는 버그에 대한 안전 개선.
즉시 적용 불가(pt_value 5배 차이·COM 재구독 크래시·DB 혼재 위험) → 재시작 경유 안전 경로 구현.

- `MireukDashboard.sig_code_change_restart_requested` pyqtSignal
- `_active_futures_code` 상태 변수 + `set_active_futures_code()`
- `lbl_code_change` 배지 (lbl_shadow 옆, 평소 숨김, 기동코드≠UI코드 시 출현)
- `_on_code_change_restart_requested()`: 포지션FLAT + 15:10이전 이중 체크 → quit()
- `DashboardAdapter` 위임 + 시그널 노출

**커밋**: 234차 (64ad55e)

---

## 2026-06-24 (235차 — TICK_SIZE 동적 주입 + 종목전환 안전절차 다이얼로그)

### TICK_SIZE 하드코딩 버그 수정

`config/settings.py` `TICK_SIZE = 0.05`(일반선물)가 미니선물 운영 시에도 그대로 적용됐음.
미니선물 틱 = 0.02pt → spread_ticks가 2.5배 과소계산 → toxicity_spread_stress 항상 0 → 독성 주문 감지 둔화.

`features/feature_builder.py`:
- `_tick_size` 인스턴스 변수 (기본 0.05)
- `set_tick_size(tick_size)` 메서드
- `spread_ticks = (ask1-bid1) / self._tick_size` (전역 상수 → 인스턴스 변수)

`main.py` `connect_broker()` 코드 확정 직후:
- `get_contract_spec(code)["tick_size"]` → `feature_builder.set_tick_size()` 호출
- 미니선물 기동 시 0.02, 일반선물 기동 시 0.05 자동 적용

### 종목전환 안전절차 확인 다이얼로그

`_on_code_change_restart_requested()` 조건 통과 후 Yes/No 확인창:
- 현재·변경 종목 및 레이블 비교
- 틱 사이즈·pt_value 변경 여부 명시
- spread_ticks·toxicity 전환 기간 경고
- DB 혼재(raw_candles 종목코드 없음)로 GBM 일시 저하 안내
- 모의투자 1주일 이상 검증 권장

### 예상 효과 (내일 로그 확인 포인트)

- `[FeatureBuilder] 계약스펙 적용: 미니선물 tick_size=0.02 pt_value=50,000` 출현
- spread_ticks가 2틱(0.04pt) 스프레드 시 0.8 → 2.0으로 정상화
- toxicity_spread_stress가 실제 호가 상황 반영

**커밋**: 235차 (c836e5e)

---

## 2026-06-23 (231차 — EOD 점검 3종 수정)

### 수정 1: macro_fetcher sp500_chg 간헐적 0 fallback 방지

`collection/macro/macro_fetcher.py` `__init__`에 `_last_chg: Dict[str, float] = {}` 추가.
`_fetch_all()` chg 계산부: prev 취득 성공 시 `_last_chg[key]`에 저장, prev 미취득 시 0 강제 → `_last_chg.get(key, 0.0)` 재사용.

### 수정 2: ScalerWarmup 피처 수 불일치 (120→97) 수정

`learning/batch_retrainer.py` `load_features_for_warmup()`:
- 기존: DB 500봉 중 최대 키 수 봉의 피처명(120개) → X(500,120) → refit에서 97개로 재정렬
- 수정: `feature_names.pkl`(97개) 우선 로드 → X(500,97) 직접 구성 → 재정렬 스킵
- pkl 없는 경우(최초 실행) DB 최대 키 봉 fallback 유지

### 피처셋 업데이트

`featureset by horizon/horizon_feature_sets.json`:
- 활성화(need_add→in_pkl): `threshold_feasibility`(5,101행, 15m·30m), `queue_directional_depletion`(4,253행, 1m)
- 삭제: `bear_reversal_signal`(3m include 미반영 정리), `bull_reversal_signal`(145행,0.2%), `bull_exhaustion_signal`(2행,0.0%)
- 내일(06-24) EOD 재학습에서 1m:13개, 15m:16개, 30m:12개로 슬라이싱 증가 예상

**커밋**: 231차

---

## 2026-06-23 (226차 — GBM 재학습 64비트 subprocess 이관)

### 배경 — 금일 12시 재시작 후 OOM 반복 확인

225차 커밋 후 12:00 재시작으로 sigma·QTimer 수정 효과 확인됐으나,
GBM 재학습이 12:01·12:24·12:54·13:29·13:52 모두 OOM으로 실패:
```
Unable to allocate 14.8 MiB for an array with shape (39876, 97) and data type float32
```
32비트 Python 3.7의 메모리 단편화 한계. 재학습 없이 구형 모델 유지 → 30m ConstOut 반복.

### 해결: py310_64 서브프로세스 재학습

```
retrain_intraday.py (신규)
  py310_64 (Python 3.10 64-bit) 전용
  retrain_now(force, intraday) 실행 → 결과 JSON 기록
  EOD retrain_eod.py 와 동일 환경 (pickle protocol=4 호환)

main.py 구조 변경
  _start_gbm_retrain_subprocess() 신규 헬퍼
  PreRetrain(08:55), WarmupRetrain(장중재시작), STEP3(주기/드리프트),
  _start_manual_retrain() 4곳 모두 subprocess 이관
  S0-A: subprocess.poll() 완료 감지 → _on_gbm_retrain_done() 호출
  S0-B: deferred_callbacks 큐는 const_out_done 전용 유지

config/settings.py: PYTHON_64_EXEC = py310_64 경로 추가
```

### 예상 효과 (내일 로그 확인 포인트)

- `[GBM-64] 64비트 서브프로세스 재학습 시작 | force=... pid=N` 출현
- `[GBM-64] subprocess 완료 (returncode=0)` 출현
- `[GBM] 배치 재학습 완료 | Xs` 출현 (OOM 없이)
- 30m ConstOut 발생 감소 (모델 정상 교체 시)
- `retrain_intraday_{YYYYMMDD_HHMMSS}.log` 생성 확인

**커밋**: 226차 (054c21d)

---

## 2026-06-23 (225차 — sigma=0 고착·QTimer 미전달·CB③ 재트리거 수정)

### 배경 — 금일 장중 로그 딥다이브

20260623 LEARNING.log / SYSTEM.log 분석으로 종일 CB③ HALT(10:22~장마감) 미해제 원인 규명.

### 근본 원인 체인

```
sigma=0 고착 (신규 버그)
  → sigma 기반 피처 상수
  → GBM 30m ConstOut 순환
  → ConstOut refit 후 QTimer 미전달 (기존 버그)
  → _on_const_out_refit_done() 미실행
  → reset_acc30m_buffer() 미호출 / GBM 재학습 미트리거
  → 10:15 refit 후에도 30m 7연속 실패
  → CB③ 재트리거 (버퍼 리셋 후 샘플 부족 방어 없음)
  → 10:22 HALT → lift_cb3_halt() 미호출 → 종일 정지
```

**추가 피해**: 08:55 PreRetrain도 QTimer 미전달 → 모델 미교체 → 누적 예측 품질 저하.

### 수정 1: sigma=0 고착 수정 [P0] (main.py)

**버그**: `_on_tick_price_update()`(bar 수신 즉시)가 `self._last_pipeline_price = close[T]`로 덮어씀. 파이프라인 라인 3187에서 `_prev = self._last_pipeline_price` 캡처 시 prev == cur → ret=0 고착.

**수정**: `self._sigma_prev_price: float = 0.0` 전용 변수 신설. 파이프라인 **말미**(`notify_pipeline_ran()` 직전)에서만 갱신. sigma 계산에서 이 변수만 참조.

### 수정 2: QTimer daemon thread → deferred 큐 [P1] (main.py)

**버그**: PyQt5에서 daemon thread의 `QTimer.singleShot(0, ...)` 메인 이벤트 루프 전달 미보장 → GBM worker 4곳 + ConstOut worker 1곳 콜백 전부 미실행.

**수정**: 모든 worker → `self._deferred_callbacks.put(tag, ...)`. 매분 파이프라인 S0 첫 블록에서 큐 drain → 메인 스레드 안전 실행.

### 수정 3: CB③ 버퍼 리셋 후 쿨다운 [P2] (circuit_breaker.py)

**버그**: `reset_acc30m_buffer()` 직후 7샘플 만에 7연속 오답 → 즉시 재HALT.

**수정**: 리셋 시 `_cb3_reset_cooldown_samples = 15`. 15샘플 누적 전 warn_count 억제.

### 수정 4: CB③ HALT 주기적 재시도 [P3] (main.py)

S0에서 15분마다 `HALTED & cause==cb3 & 재학습 미실행` 시 `lift_cb3_halt()` 재시도 — P1 누락 최후 안전망.

### 수정 5: GBM 재학습 타임아웃 30분 → 10분 [P4] (main.py)

PreRetrain 통상 ~3분 완료. 30분 → 10분으로 단축해 조기 해제 후 ConstOut 정상 경로 복귀 보장.

### 예상 효과 (내일 로그 확인 포인트)

- `[sigma] sigma_at_t=X.XXXX% nonzero=Y` — nonzero > 0 출력 확인 (0이면 버그 재발)
- `[DeferredCB]` 오류 없음 + `[CB③→RESUME]` 정상 해제 흐름
- `[CB③] acc30m 버퍼 리셋 (스케일러 재적합 완료 — 이전 예측 무효화, 쿨다운=15샘플)` 출력
- ConstOut 후 CB③ 재트리거 없이 거래 재개

**커밋**: 225차 (58b3c1b)

---

## 2026-06-23 (224차 — SGD 붕괴 복구 임계 완화 + BiasReset 연계 SGD 리셋)

### 배경 — 5m DN 편향 로그 분석

오늘 장중 5m DN 편향 흐름을 분석한 결과 두 가지 구조적 문제 발견:

1. **SGD 붕괴 자동복구 미발동**: 5m DN=83% 편향임에도 SGD 출력이 95% 임계에 미달 → 복구 불발
2. **BiasReset 후 UP 고착**: BiasReset이 09:58에 발동 후 `boost_sgd_for_bias`가 SGD 가중치를 올렸는데, 오염된 파라미터 상태에서 UP 방향으로 고착되어 10:03~10:19 conf=34.0% UP 연속 실패

### 데이터 근거 (4일치 로그 분석)

발동된 붕괴 복구 케이스 11건의 직전 Bias% 분포:
- 최솟값 76%, 평균 87.4%, 중앙값 87%
- 미발동 케이스: 5m DN=83% (오늘)

### 수정 1: SGD 붕괴 임계 완화 (online_learner.py)

| 항목 | 이전 | 이후 |
|---|---|---|
| `_COLLAPSE_THR` | 0.95 (하드코딩) | **0.80** (클래스 상수) |
| `_COLLAPSE_TICKS` | 15분 (하드코딩) | **12분** (클래스 상수) |
| 리셋 로직 | 인라인 중복 | `_do_sgd_reset()` 공통 메서드 |

### 수정 2: BiasReset 시 SGD 전체 리셋 (online_learner.py + main.py)

- `reset_sgd_for_bias(horizon)` 신규 메서드 추가: 모델·스케일러·가중치 전체 초기화
- `main.py` L3545: `boost_sgd_for_bias` → `reset_sgd_for_bias` 교체
- BiasReset uniform fallback 기간 중 SGD 공백이 동기화되어 UP 고착 부작용 제거

### 예상 효과 (내일 로그 확인 포인트)

- `[OnlineLearner] 5m SGD DN붕괴 자동 복구 (≥80% 12분 지속) → 모델·스케일러 리셋`
- `[OnlineLearner] 5m BiasReset 연계 SGD 리셋 → 모델·스케일러·가중치 초기화`

**커밋**: 224차 (c9c2d74)

---

## 2026-06-23 (223차 — BiasReset uniform fallback 고착 버그 수정)

### 배경 — 장중 10m·3m FL편향 고착 확인

오늘 장중(09:42~) 10m 호라이즌에서 BiasReset이 발동됐음에도 uniform fallback이 해제되지 않고
계속 `[Bias⚠] FL편향 80~87%` 경고가 반복 출력됨. 3m도 09:49부터 같은 패턴 진입.

### 버그 원인 (2가지 연쇄)

**원인 1**: BiasReset 발동 시 `_bias_buf`를 클리어하지 않아 이전 FL 26건이 잔존
→ 해제 조건 `_dir_bias_r < 0.60` 영구 미달

**원인 2**: uniform fallback 적용 후 저장된 예측(direction=0=FLAT)이 10분 후 verified될 때 FL로 카운트
→ bias_buf가 자연 교체되어도 FL 비율이 유지되어 해제 불가

### 수정 (main.py, 6곳)

| 위치 | 변경 내용 |
|---|---|
| `__init__` ~L491 | `_bias_override_timer: dict` 추가 |
| bias_buf 기록 ~L3447 | override active 호라이즌 verified 기록 스킵 |
| 편향 판정 루프 앞 ~L3458 | 타이머 감소 + 0 도달 시 자동 해제 로그 |
| BiasReset 발동 ~L3529 | `buf.clear()` + `streak=0` + `timer=20` 설정 |
| GBM 재학습 리셋 ~L2772 | `_bias_override_timer` 초기화 추가 |
| 일간 리셋 ~L6962 | `_bias_override_timer` 초기화 추가 |

### 수정 후 동작

- BiasReset 발동 즉시 `_bias_buf` 클리어 → `[Bias⚠]` 반복 경고 즉시 중단
- override active 중 verified 예측 buf 제외 → uniform(FL) 쌓임 차단
- 20분 타이머 자동 해제 → 영구 고착 방지
- GBM 재학습 발생 시 기존대로 즉시 강제 해제

### 오늘 거래 결과 (참고)

- 1차 (09:21): SHORT 2계약 @ 1465.84 → TP1+TP2 = +760,602원
- 2차 (09:30): SHORT 1계약 @ 1455.80 → 하드스톱 = -92,184원
- 당일 누적: **+668,418원**

**커밋**: 223차 (ca33da8)

---

## 2026-06-23 (222차 — EOD 마커 파일명 불일치 + retrain_str NameError 수정)

### 배경 — 장전 점검 중 두 버그 발견

오늘 장전 점검에서 PreRetrain이 불필요하게 발동된 원인 추적.
마커 파일 `eod_retrain_done_20260622.txt`가 실재함에도 `_eod_retrain_ok = False`로 유지 →
매일 PreRetrain 강제 실행되는 구조였음.

### Bug 1 — retrain_str NameError (DailyClose 비정상 종료)

**현상**: 어제(6/22) 15:40 `daily_close()` 종료 시 `NameError: name 'retrain_str' is not defined`.
DailyClose가 exception으로 중단 → `_schedule_shutdown` 경유 자동 종료는 정상 실행됨.

**원인**: `main.py:7135` notify() f-string에서 `retrain_str` 변수를 사용했으나 정의문 누락.

**수정**:

| 파일 | 위치 | 변경 |
|---|---|---|
| `main.py` | `daily_close()` notify() 직전 ~L7127 | `retrain_str` 정의 추가 — `_eod_retrain_ok` 참조해 "완료(스케줄러)" / "미완료(내일 PreRetrain 보완)" 분기 |

### Bug 2 — EOD 마커 파일명 형식 불일치 (PreRetrain 항상 강제 실행)

**현상**: `retrain_eod.py`가 성공해도 `main.py`가 마커 파일을 찾지 못함
→ `_eod_retrain_ok` 항상 False → PreRetrain 불필요 실행 (매일).

**원인**: 파일명 날짜 형식 불일치

| 위치 | 형식 | 실제 파일명 예시 |
|---|---|---|
| `retrain_eod.py:29` | `strftime("%Y%m%d")` | `eod_retrain_done_20260622.txt` |
| `main.py:3015` PreRetrain 폴백 | `isoformat()` | `eod_retrain_done_2026-06-22.txt` (못 찾음) |
| `main.py:6805` daily_close 조회 | `isoformat()` | `eod_retrain_done_2026-06-22.txt` (못 찾음) |

`retrain_eod.py`가 하이픈 없이 생성하지만, `main.py`는 하이픈 있는 이름을 찾아서 **항상 미발견**.

**수정**:

| 파일 | 위치 | 변경 |
|---|---|---|
| `main.py` | `pre_market_setup()` PreRetrain 폴백 ~L3015 | `_prev.isoformat()` → `_prev.strftime('%Y%m%d')` |
| `main.py` | `daily_close()` 마커 조회 ~L6805 | `datetime.date.today().isoformat()` → `datetime.date.today().strftime('%Y%m%d')` |

### 연쇄 영향 (수정 전)

```
retrain_eod.py 15:48 완료 → 마커 파일 생성 (하이픈 없음)
daily_close() 15:40 → 마커 조회 (하이픈 있음) → 못 찾음 → eod_retrain_ok_date 저장 안 됨
pre_market_setup() 08:55 → session_state 공백 → 폴백 마커 조회 (하이픈 있음) → 못 찾음
→ PreRetrain 불필요 실행 (매일 반복)
```

> **주의**: 이 버그는 retrain_str NameError와 독립적. NameError 없었어도 하이픈 불일치로 동일하게 발생.

### 검증 포인트 (내일 장전)

- [ ] **[PreRetrain] EOD 마커 파일 직접 확인 (1일 전: 2026-06-23)** 로그 출현 확인
- [ ] **[PreRetrain] 08:55 사전 재학습 스킵** 로그 출현 확인 (PreRetrain 불필요 실행 없음)
- [ ] **DailyClose retrain_str** — 오늘 15:40 `"재학습: 완료 (스케줄러)"` 또는 `"재학습: 미완료 (내일 PreRetrain 보완)"` 알림 정상 출력

**커밋**: 222차 (오늘)

---

## 2026-06-22 (221차 — BlockRequest 레이스 컨디션 분할체결 qty 누락 방어)

### 배경 — 14:46 진입 로그 순서 이상 딥다이브

14:46 매도진입 후 14:56 재진입이 "청산 전 재진입"인지 딥다이브 요청.
TRADE/SIGNAL/SYSTEM 로그 교차분석 결과:

- **14:56 재진입은 정상**: 14:52:52 청산 완료 후 쿨다운 경과 + B등급 독립 신호
- **14:46 진입에서 레이스 컨디션 발생**: Chejan이 `open_position()` 전에 먼저 처리됨
  - `[Position] 진입 SHORT` 로그 없이 `[체결진입]`이 먼저 나온 것이 증거
  - 실제 체결은 1계약 (브로커 잔고 확인: `14:46:52 position=SHORT 1계약`) → 오늘은 무해

### 근본 원인

Cybos `BlockRequest()`는 COM 이벤트 루프를 pump하므로 `_send_broker_entry_order()` 반환 전에
Chejan 콜백이 먼저 실행될 수 있다 (`[Fix-PendingFirst]` 주석에도 기술됨).

이때 `pending["optimistic_opened"]=True`는 이미 설정됐지만 `open_position()`은 아직 미호출.
`_ts_handle_entry_fill_cybos_safe`의 VWAP 보정 분기 진입 조건:

```python
pending["optimistic_opened"] = True  AND  status == entry_direction  AND  _optimistic = False
```

- 첫 체결: `status=FLAT ≠ SHORT` → else → `apply_entry_fill(FLAT→SHORT)` → qty=1
- 2번째+ 체결: `status=SHORT, _optimistic=False` → **보정 분기** → VWAP만 업데이트, qty 증가 없음

→ **실전에서 4계약 전량 체결 + 레이스 컨디션이 겹치면 position.qty=1, 브로커 잔고=4 불일치 발생**

### 수정 내용 (221차)

| 파일 | 위치 | 변경 |
|---|---|---|
| `main.py` | `_ts_execute_entry` FixB 블록 ~L10299 | `open_position()` 성공 직후 `_pending_order["open_position_done"] = True` 설정 |
| `main.py` | `_ts_handle_entry_fill_cybos_safe` 보정 분기 ~L10397 | 조건에 `pending.get("open_position_done")` 추가 |

### 케이스별 동작

| 케이스 | `open_position_done` | 분기 | qty 처리 |
|---|---|---|---|
| 정상 분할체결 | `True` | VWAP 보정 분기 | qty 그대로 (기존 동작) |
| 레이스 컨디션 + 전량 체결 | `False` | else → `apply_entry_fill` 증량 | qty 올바르게 누적 |
| 레이스 컨디션 + 부분 체결 | `False` | else → `apply_entry_fill` 신규/증량 | qty 실체결 수량으로 관리 |

> **왜 단순 `quantity += fill_qty`가 안 되는가**: 정상 케이스에서 `open_position(qty=4)` 후
> 분할 Chejan마다 `+=1`을 하면 4+1+1+1=7이 되는 이중 카운팅 발생.
> `open_position_done` 플래그로 두 케이스를 명확히 구분해야 한다.

**커밋**: `9ad777c` (221차)

---

## 2026-06-22 (220차 — 15:10 강제청산 FLAT불일치 + 15:18 FINAL_CLOSE 안전망)

### 배경 — 오늘 15:20 Cybos 잔고 3계약 미청산 사고

14:56:52 SHORT 3계약 진입 후 14:58~15:00 사이 3×1계약 순차 청산
→ ChejanFlow 체결 확인 → 시스템 내부 position=FLAT 선언.
그러나 Cybos 실제 잔고는 여전히 3계약 보유.
15:10 강제청산이 `_send_broker_exit_order(qty=0)` 호출
→ FLAT 가드(`position.status == "FLAT" → return -1`) 에 막혀 아무것도 하지 않음.
→ 15:20에도 3계약 잔류 (오버나이트 위험).

### 근본 원인

**FLAT 가드**: `_send_broker_exit_order` 내부에 `position.status == "FLAT" → return -1` 가드 존재.
**qty=0 호출**: 시스템이 FLAT으로 착각하므로 `position.quantity=0` → qty=0 주문 → 가드에 걸림.
**broker 잔고 무시**: 15:10 강제청산 경로가 `_integrity_broker_qty`(마지막 잔고조회 캐시)를
참조하지 않아 broker 실수량을 알 방법이 없었음.

### 수정 내용 (220차)

| 파일 | 위치 | 변경 |
|---|---|---|
| `strategy/exit/time_exit.py` | `TimeExitManager` | `should_final_close()` 추가 — 15:18 FINAL_CLOSE 발동 여부 |
| `main.py` | `__init__` ~L474 | `_final_close_done: bool = False` 플래그 추가 |
| `main.py` | `_ts_check_exit_triggers` ~L8174 | 15:10 강제청산: `_integrity_broker_qty` 폴백 + FLAT 시 BrokerDirect 분기 |
| `main.py` | `_check_exit_triggers` ~L6248 | 분봉 기반 15:10 강제청산 동일 패턴 적용 |
| `main.py` | `_ts_check_exit_triggers` ~L8222 | 15:18 FINAL_CLOSE 블록 추가 — `_ts_broker_direct_force_exit` 호출 |
| `main.py` | `_ts_broker_direct_force_exit` ~L9181 | 신규 함수 — `request_futures_balance` 직접 조회 후 `send_market_order` 호출 |

### `_ts_broker_direct_force_exit` 동작

1. `request_futures_balance(account_no)` 직접 TR 조회
2. 해당 종목코드 행 탐색 → `잔고수량`, `구분(매도/매수)` 파싱
3. `send_market_order(BUY/SELL, qty)` 직접 호출 (FLAT 가드 완전 우회)
4. 잔고 없으면 "진짜 FLAT" INFO 로그 후 False 반환 (무해)

### 오늘 사고 재현 시 예상 동작

```
15:10:xx  should_force_exit() = True
          position.status = "FLAT" / _integrity_broker_qty = 3
          → BrokerDirect 분기: request_futures_balance 조회
          → broker SHORT 3계약 확인 → BUY 3계약 직접주문
          [BrokerDirectExit] 15:10 FLAT불일치 강제청산 — broker SHORT 3계약 → BUY 직접주문

15:18:xx  should_final_close() = True, _final_close_done = False
          → _ts_broker_direct_force_exit 재실행
          → broker 잔고 0 확인 → "진짜 FLAT" INFO → _final_close_done = True
```

**커밋**: `f412df8` (220차)

---

## 2026-06-22 (219차 — 브로커 잔여계약 PnL 누락·Sizer 잔고·TRADE 로그 3버그 수정)

### 배경 — 딥다이브 분석으로 발견

실시간 잔고 패널(금일손익 -96,999원)과 엔진 누적 손익(-353,129원)의 괴리를 CpTd6197 헤더 원시값과
TRADE 로그를 교차 분석해 3개 버그를 확정.

### 문제 현상

| 버그 | 현상 |
|---|---|
| Bug1 | 다계약 청산 주문 시 Chejan 콜백 일부 미수신 → 잔여계약이 PnL 없이 소멸, 엔진 누적 손익 왜곡 |
| Bug2 | Sizer 잔고가 종일 481,366,885원 고정 — 거래 후 손익이 Sizer에 미반영, 과대 포지션 크기 산출 가능 |
| Bug3 | 포지션이 브로커 기준 FLAT으로 강제될 때 TRADE 로그 공백 — 사후 추적 불가 |

### 근본 원인

**[Bug1]** `_ts_resolve_stuck_exit_pending`의 `broker_row is None` 분기에서 `sync_flat_from_broker()`가
`position.quantity > 0`인 상태로 호출됨. `sync_flat_from_broker()`는 PnL 계산 없이 `_reset_position()`만 실행.

오늘 케이스: 2계약 하드스톱 주문 → Chejan 이벤트 1회만 수신(1계약) → 잔여 1계약 PnL ~+242,000원 소멸
→ 엔진(-353,129) vs 브로커(-96,999) 256,130원 괴리의 주원인.

**[Bug2]** `_ts_extract_sizer_balance`가 `총매매`(예탁금=header1, 정적)를 우선 탐색.
Cybos CpTd6197의 `총평가수익률`(익일예탁금=header2)이 당일 실현손익 반영 실시간 잔고인데 순서가 뒤였음.

**[Bug3]** `sync_flat_from_broker()` 자체는 `[Position] 브로커 기준 동기화: FLAT` 로그를 남기지만,
어느 계약이, 어떤 이유로 FLAT이 됐는지 TRADE 탭에서 파악 불가능했음.

### 수정 내용 (219차)

| 파일 | 위치 | 변경 |
|---|---|---|
| `main.py` | `_ts_resolve_stuck_exit_pending` ~L9001 | Bug1: `close_position(exit_price, "stuck_exit_remainder")` + DB 기록 + PnL 로그 |
| `main.py` | `_ts_extract_sizer_balance` ~L9300 | Bug2: 키 탐색 순서 `총평가수익률→총매매→추정자산` 으로 변경 |
| `main.py` | `_ts_sync_position_from_broker` blank-as-flat 분기 | Bug3: `log_manager.trade("[BrokerSync] blank-as-flat 강제:...")` 추가 |

**Bug1 동작**: 잔여계약 발견 → 추정가(`_sq_avg_price` 우선, 없으면 `_last_pipeline_price`) → `close_position()` 호출
→ `_daily_pnl_pts` / `_daily_commission` 정상 업데이트 → trades DB 기록 → PnL 탭 표시

**커밋**: `4d2b8bf` (219차)

---

## 2026-06-22 (218차 — DriftRetrain 32-bit OOM 수정 + 재시도 쿨다운)

### 문제 현상

```
[13:50~14:07] [DriftRetrain] GBM 경량 재학습 시작 (acc30m=0.0% n=15~30 경과=4159~4174분)
→ 매분 재트리거, 17회 연속. _last_retrain 갱신 안 됨 (경과가 1분씩 증가)
[14:07] [CB] 당일 시스템 정지 | 30분 정확도 0.0%
```

- 30m GBM 모델 UP편향 80% 고착 (acc30m=10%→0.0%)
- DriftRetrain이 매분 시작되지만 즉시 실패 → `_last_retrain` 미갱신 → 무한 루프

### 근본 원인

**[P0] 32-bit Python OOM (메모리 단편화)**

```
[WARNING] [Retrain] DB 로드 오류:
  Unable to allocate 14.8 MiB for an array with shape (39922, 97) and data type float32
[WARNING] [Retrain] 학습 데이터 부족 (0 < 15000)
```

- `_load_from_db()`가 39,880행을 dict 리스트로 정상 로드 후 `np.array(..., float32)` 변환 시 OOM
- 기존 `retrain_now()` 내 20,000행 슬라이싱은 **np.array 생성 이후** → 이미 늦음
- 변환 실패 → `X=None` → `"학습 데이터 부족"` 반환 → `_last_retrain` 미갱신
- 11:22부터 14:07까지 165회 이상 동일 패턴 반복

**[P2] 실패 쿨다운 부재**
- `_last_retrain` 미갱신 시 `_dr_mins`가 계속 증가 → 다음 분 조건 즉시 재충족

### 수정 내용 (218차)

| 파일 | 변경 |
|---|---|
| `learning/batch_retrainer.py` | `_load_from_db(intraday=False)` 파라미터 추가, CUSUM 후 np.array 전 20,000행 사전 제한 |
| `main.py` | `_drift_retrain_last_attempt` 플래그 추가, 조건A/B에 5분 쿨다운 체크 |

**P0 효과**: 39,880행→20,000행 사전 제한 → np.array 14.8 MiB→7.4 MiB → 할당 성공
**P2 효과**: 재학습 실패 시에도 5분 쿨다운 보장 (OOM 재발 시 안전망)

**커밋**: `f2cb738` (218차)

---

## 2026-06-22 (217차 — 호라이즌 자격 조건 수정 + GDI 크래시 방지 + 런처 자동 재시작)

### 문제 현상

1. 호라이즌 자격 현황(사이클 추적)에서 1m/3m/10m가 영구 WAIT 상태
2. 장중 재시작 후 `createDIB: CreateDIBSection failed (3030x1460, format: 6)` 즉시 크래시
3. 크래시 후 런처가 자동 재시작하지 않아 수동 개입 필요

### 근본 원인

**① WAIT 고착**: SGD 학습 conf 필터(0.52)가 단기 호라이즌에 과도하게 엄격
- 1m/3m: BiasReset으로 conf=1/3 강제 또는 GBM 자체 저신뢰 → trained_cycles 영구 0
- 10m: BAR_CACHE_DECAY(0.93^age) 감쇠 중첩 → trained_cycles ≤1

**② GDI 크래시**: ui_prefs.json에 저장된 `w=3030, h=1460` (논리픽셀)
- DPI 150% 자동 스케일: 4547×2124 물리픽셀 DIB = 38.6 MB 연속 블록 필요
- 3시간+ GBM 재학습 후 32-bit 가상주소 단편화 → CreateDIBSection FAILED → crash
- (08:40 첫 기동은 신선한 프로세스라 성공, 12:25 재시작 시 단편화로 실패)

**③ 런처**: crash 후 자동 재시작 로직 없음 + 로그 한글 UTF-16 깨짐

### 수정 내용 (217차)

| 파일 | 변경 |
|---|---|
| `config/settings.py` | `HORIZON_QUALIFY_MIN_TRAINED` 딕셔너리 추가 |
| `main.py` | verified/trained 자격 판정 2곳에 `_need_trained` 분리 적용 |
| `dashboard/main_dashboard.py` | `_CHART_MAX_LOGICAL_W/H=1920/1060` + restore/close/paintEvent 3중 가드 |
| `data/ui_prefs.json` | bad 값 w=3030→1920, h=1460→1060 즉시 교정 |
| `start_mireuk_Cybos.bat` | 장중 자동 재시작 루프(최대 5회) + PYTHONUTF8=1 |

**HORIZON_QUALIFY_MIN_TRAINED:**
```python
{"1m": 0, "3m": 0, "10m": 1, "5m": 3, "15m": 3, "30m": 3}
```
→ 재시작 3분 후 1m/3m ACTIVE 전환 예상

**GDI 보호 3중 레이어:**
- Layer 1: `restore_saved_geometry`에서 setGeometry 전 cap (1차 방어)
- Layer 2: `closeEvent`에서 저장 시 cap (재유입 차단)
- Layer 3: `paintEvent` 가드 6000×4000 → 3000×2000 (2차 방어)

**커밋**: `752a8c9` (217차)

---

## 2026-06-22 (216차 — CB③ HALT 원인해소 후 거래 재개)

### 문제 현상

```
[CRITICAL] [CB] 당일 시스템 정지 | 30분 정확도 10.0%
[WARN] [ConstOut] ['30m', '3m'] 상수 출력 확정 → 스케일러 재적합 시작
```

CB③ 발동 후 스케일러 재적합 + GBM 재학습으로 원인이 해소돼도 `_state = "HALTED"` 고정 → 당일 내내 거래 불가.

### 근본 원인

`_on_const_out_refit_done()` → `reset_acc30m_buffer()` 는 acc 버퍼만 지우고 `_state`를 HALTED → NORMAL 로 복귀시키지 않음. HALT 해제 경로가 `reset_daily()`(다음 날 장 시작) 외에 없었음.

### 수정 내용 (216차)

| 파일 | 변경 |
|---|---|
| `safety/circuit_breaker.py` | `_halt_cause` 필드 + `_trigger_halt(cause=)` + `lift_cb3_halt()` 신규 메서드 |
| `main.py` | `_on_gbm_retrain_done` 성공 블록에 `lift_cb3_halt()` 호출 |

**`lift_cb3_halt()` 해제 조건:**
- `state == HALTED` AND `_halt_cause == "cb3"` (CB②·연속손절 HALT는 해제 불가)
- `daily_halt_count < 3` (3회 이상 = 완전 관망 정책 유지)

**해제 시점**: GBM 재학습 완료 후 (`_on_gbm_retrain_done` 성공 블록)
— scaler refit만으로는 GBM 트리 미변경 → ConstOut 재발 가능하므로 재학습까지 기다림

**커밋**: `059bbe4` (216차)

---

## 2026-06-22 (215차 — minute_chart 예외 가드 + 좌측패널 카드 업데이트 불가 근인 확인)

### 문제 현상

좌측패널 두 카드가 종일 업데이트 안 됨:
- `DirectionIndicatorWidget` (1m~30m 방향, 합의) → "대기" / "—"
- `ConfTrendWidget` (금일 conf → 진입단계 추적) → 데이터 없음

### 근본 원인 (로그 분석으로 확정)

**1차 세션(09:00~10:32)**에 DB 저장 0건:
```
[ERR-FATAL] minute_pipeline: 'DashboardAdapter' object has no attribute 'minute_chart_set_direction'
```
214차 fix가 코드에 적용됐으나 프로그램은 수정 前 코드로 기동 중 → 매분 AttributeError
→ `run_minute_pipeline`이 라인 4399에서 예외 → **STEP9(`save_step9_batch`) 미도달**
→ `ensemble_decisions` 0건, `predictions` 0건
→ 두 위젯 모두 DB 쿼리 결과 없음 → 정상적으로 "—" 표시

10:32 재시작 후 → 45건 정상 저장 / 두 위젯 정상 복구.

### 수정 내용 (215차)

**방어 try-except 추가** — 차트 갱신 실패가 파이프라인 크리티컬 경로 차단 방지

| 위치 | 대상 |
|---|---|
| `main.py` ~3896 | `dashboard.minute_chart_set_regime(ts, regime)` |
| `main.py` ~4402 | `dashboard.minute_chart_set_direction(ts, direction)` |

기존 `minute_chart_candle_closed`(라인 2651)와 동일 패턴. DEBUG 로그 출력.

**커밋**: `1b2bbcd` (215차)

### 위젯 코드 상태

`DirectionIndicatorWidget`, `ConfTrendWidget` 자체 코드는 정상.
DB에 데이터가 있으면 각각 10초/30초 타이머로 자동 갱신됨.

---

## 2026-06-22 (214차 — ERR-FATAL 수정 + 프리장 Phase 재설계)

### 문제 배경 (6/22 장초반 로그 분석)

6/22 정규장 09:00~09:07 매분 반복:
```
[ERR-FATAL] minute_pipeline: 'DashboardAdapter' object has no attribute 'minute_chart_set_direction'
→ 자동진입 OFF + 15분 타임아웃 (매분 갱신 → 진입 영구 차단)
```

추가 발견: 201차 PRE_MARKET_REFIT_STEPS {1,5,10,14} 실측
- Phase1(1봉): z경고 6→14개 역효과 (1봉 통계 불안정)
- Phase2(5봉): z경고 15→15개 무효과
- Phase3·4: 발동 안됨 (Cybos RT 구독 08:55 → 최대 4~6봉만 수집)

### 수정 내용

| 우선순위 | 내용 | 파일 |
|---|---|---|
| **P0** | `_adapter_minute_chart_set_direction` 추가 + `DashboardAdapter` 바인딩 | `dashboard/main_dashboard.py` |
| **P1-①** | `PRE_MARKET_REFIT_STEPS` `{1,5,10,14}` → `{3,5,10,14}` (1봉 역효과 제거) | `config/settings.py` |
| **P1-②** | Cybos RT 실시간 구독 08:45 선행 시작 (EarlyWarmup 트리거 직후) | `main.py` |
| **P2-①** | `_pm_refit_worker` z경고 악화(+3개↑) 시 WARNING 로그 | `main.py` |
| **P2-②** | ChartDBG paintEvent 임계 10ms → 30ms (WARN 로그 스팸 103KB 제거) | `dashboard/main_dashboard.py` |

### P0 근본 원인

210차(X축 방향예측 레인)에서 `main.py`에 `self.dashboard.minute_chart_set_direction(ts, direction)` 호출을 추가했지만, `DashboardAdapter` 어댑터 함수 등록을 누락. `MireukDashboard`에는 메서드가 있어 단독 실행 시 정상이나 `DashboardAdapter` 경유 시 AttributeError.

### 프리장 Phase 설계 변경

```
기존: {1, 5, 10, 14}봉 (1봉 역효과 + 5봉 이상 발동 불가)
개선: {3, 5, 10, 14}봉 + Cybos RT 08:45 선행 구독

결과 (내일 예상):
08:45 Cybos RT 구독 시작
08:47 Phase1(3봉) 기동·완료  ← z경고 안정적 감소 예상
08:49 Phase2(5봉)
08:54 Phase3(10봉)
08:58 Phase4(14봉) ← 09:00 직전 최종 확정
```

커밋: `995a2d4` (214차)

---

## 2026-06-19 (211~213차 — 1분봉 차트 자동팝업 복원 완전 해결)

### 핵심 발화점 (log 분석으로 확정)

```
QWindowsWindow::setGeometry: Unable to set geometry 3030x1460+3369-8
→ Resulting: 4547x2124+3372+6
```

보조 모니터 avail.top()=-7인 환경에서:
- 저장값 y=-7 → Qt 프레임 계산으로 y=-8 요청 → avail.top()=-7 밖 1px
- Python 3.7 32-bit(96DPI) + 보조모니터 144DPI(150%) → Windows DPI 가상화
- 3030×1.5=4547, 1460×1.5=2190 → 4547×2124로 강제 확대
- 이후 매분 paintEvent 4513×2060 반복 (17:26~17:50, 20회+)

### 수정 이력

| 차수 | 수정 | 커밋 |
|---|---|---|
| 207차 | QTimer.singleShot→pyqtSignal, _reload_today_bg 데이터 복원 | 240e9c6 |
| 208차-추가 | closeEvent 90%/isMaximized 체크, MireukDashboard.closeEvent | 236ac7f |
| 209차 | 90% threshold → _center_on_second_screen fallback | fe194c1 |
| 210차 | paintEvent 6000px guard, 90% 체크 전면 제거 | f53f4e9 |
| 211차 | pre-show restore_saved_geometry (HWND 생성 모니터 지정) | 27dafe1 |
| **212차** | **y<0 → y=0 보정 (DPI 1.5× 근본 차단)** | **76d14b6** |
| 213차 | pickle protocol=4, ConfTrend 로그 정제, 런처 로그 | 0274cd4 |

### 현재 geometry 처리 규칙 (최종)

- `closeEvent`: isMaximized() → 저장 스킵. width>avail.width → 스킵. 그 외 저장.
- `restore_saved_geometry`: y<0 → y=0 보정 + WARNING 로그. 화면 밖 → _center_on_second_screen.
- `toggle_minute_chart_dialog`: restore_saved_geometry() pre-show + singleShot(0) post-show.
- `paintEvent guard`: width>6000 or height>4000 (이전 3000/2000 → 차트 차단 버그)

---

## 2026-06-19 (210차 — X축 방향예측·레짐 레인)

### 변경 내용

`MinuteChartCanvas` (좌측패널 봉차트 `main_dashboard.py`) X축 위 두 개의 색상 레인 추가.

| 레인 | 위치 | 색상 | 현재봉 |
|---|---|---|---|
| 방향예측 | 레짐 바 위 4px | UP=녹(`#3fb950`) / DOWN=적(`#f85149`) / FLAT=회(`#444c56`) | 빈칸 (삼각형 마커가 표시 중) |
| 레짐 | X축 직상 4px (기존) | 추세장=녹 / 횡보장=황 / 급변장=적 / 혼합=청보라 / 탈진=보라 | 빈칸 |

**방향예측 규칙**: 매분 STEP 6 앙상블 방향 확정 즉시 `_dir_map[ts] = direction` 기록 → 닫힌 봉에 색상 표시.

### 변경 파일

| 파일 | 변경 |
|---|---|
| `dashboard/main_dashboard.py` | `_dir_map`, `set_direction_at`, `_draw_direction_bar` 추가; 세션 복원 2곳에 `_dir_map` 복원; `minute_chart_set_direction` 퍼블릭 메서드 |
| `utils/db_utils.py` | `fetch_direction_today()` 추가 — `ensemble_decisions → {ts: int}` |
| `main.py` | STEP6 방향 확정 직후 `self.dashboard.minute_chart_set_direction(ts, direction)` 호출 |
| `dashboard/panels/candle_chart_dialog.py` | 팝업 봉차트에도 동일 인디케이터 (3-axes 레이아웃, `_fetch_candle_decisions`, 현재봉 빈칸) |

### 재시작 복원

`ensemble_decisions`에 매분 자동 기록 → `fetch_direction_today()` 로 당일 이력 전체 복원.  
레짐은 기존대로 `regime_history` → `fetch_regime_today()` 복원.

### 커밋: 210차 (2e9b9f0)

---

## 2026-06-19 (208차 — 멀티 호라이즌 예측 카드 제거)

### 변경 내용

`PredictionPanel._build()` (`dashboard/main_dashboard.py`)

| 항목 | 처리 |
|---|---|
| "멀티 호라이즌 예측 ( 1·3·5·10·15·30분 )" 타이틀 | 제거 |
| 6개 예측 카드 프레임 (▲/▼/%) | 레이아웃 미표시 (update_data 로직 보존용 참조는 유지) |
| 6개 호라이즌 On/Off 체크박스 | 유지 — cb_wrap에 이름 레이블(1분·3분…) 추가, hgrid row 0 배치 |
| 모델 상태 행 (_model_row) | 레이아웃에서 제거 (위젯 객체 보존 → setVisible 호출 오류 없음) |

**커밋**: 208차 (3c7af18)

---

## 2026-06-19 (208차-추가 — 1분봉 차트 자동팝업 창 크기 복원 버그 3종 수정)

### 문제 배경

프로그램 시작 + 자동팝업 설정 시:
- 위치: 차트 종료 시 위치로 복원됨 ✓
- 크기: **차트 종료 크기가 아닌 "상당히 큰 사이즈"** ✗ (w=2880 = 제2모니터 전체 폭)

### 근본 원인

```
ui_prefs.json에 저장된 chart_dialog_geometry: {"x":3513, "y":294, "w":2880, "h":1154}
w=2880 = 제2모니터 전체 폭 → 이전 세션에서 최대화 상태로 저장된 geometry

restore_saved_geometry():
  w = min(2880, avail.width()=2880)  → 클램핑 없음 (화면 = 저장값 동일)
  bounds check 통과 → setGeometry(3513, 294, 2880, 1154) 그대로 적용
  → 위치 맞음 / 크기 전체화면 폭 = "상당히 큰 사이즈"
```

부가: `MireukDashboard.closeEvent`가 숨겨진 다이얼로그에도 `close()` 호출
  → `__init__` 초기 크기(S.p(1180)×S.p(700))가 저장되는 경우 있음

### 수정 내용

| 파일 | 수정 |
|---|---|
| `MinuteChartDialog.closeEvent` | `isMaximized()` 체크 → 최대화 상태면 저장 스킵 |
| `restore_saved_geometry` | 화면의 88% 상한 추가 (`max_w`, `max_h`) → 최대화 크기 복원 방지 |
| `MireukDashboard.closeEvent` | `isVisible()` 체크 → 숨긴 상태에서 close() 호출 방지 |
| `data/ui_prefs.json` | `chart_dialog_geometry` 초기화 → 다음 기동 시 `_center_on_second_screen` fallback |

**커밋**: 208차-추가 (236ac7f)

---

## 2026-06-19 (207차 — 1분봉 차트 복원 4종 수정)

### 문제 배경

14:29 장중 재시동 후 두 가지 현상 확인:
1. 1분봉 차트(Ctrl+Shift+X) 재열기 시 당일 봉데이터·거래 이력 표시 안 됨
2. 윈도우 위치·크기 미복원 (저장된 geometry 무시됨)

### 근본 원인 분석

```
[데이터 미복원 — 주원인]
_reload_today_bg()  ← threading.Thread (Qt 이벤트 루프 없음)
  └─ QTimer.singleShot(0, lambda: _apply_reload_result(...))
       └─ 타이머가 호출 스레드(배경 스레드)에 귀속됨
       └─ Qt 이벤트 루프 없는 스레드 → 타이머 영원히 발동 안 됨
       └─ _apply_reload_result() 미호출 → 차트 빈 화면

[윈도우 위치 미저장 — 주원인]
MireukDashboard.closeEvent() → 존재 안 함
  → 메인 프로그램 종료 시 Qt 부모-자식 소멸 경로에서
     MinuteChartDialog.closeEvent() 미호출
  → chart_dialog_geometry → ui_prefs.json 미저장
  → 다음 기동 시 저장값 없음 → 제2모니터 중앙 배치

[자동팝업 geometry 무시]
toggle_minute_chart_dialog(auto_popup=True)
  → _center_on_second_screen() 고정 호출 (restore_saved_geometry 미사용)
```

### 수정 내용 (207차)

**`dashboard/main_dashboard.py`**

| 항목 | 수정 |
|---|---|
| `_sig_reload_done = pyqtSignal(list, list, list)` 클래스 속성 추가 | cross-thread 안전 전달 |
| `__init__`에서 `_sig_reload_done.connect(_apply_reload_result)` | 시그널-슬롯 연결 |
| `_reload_today_bg`: `QTimer.singleShot(lambda)` → `_sig_reload_done.emit()` | 핵심 수정 |
| `_reload_today_bg`: 불필요한 `from PyQt5.QtCore import QTimer` 제거 | 정리 |
| `_apply_reload_result`: `reset_session` + `_regime_map` 복원 + `_post_reload_hook` 원자 처리 | 신규 |
| `_start_reload_thread`: `_reload_running` 플래그로 동시 실행 방지 | 신규 |
| `toggle_minute_chart_dialog`: 재열기 시 `_start_reload_thread()` 호출 추가 | 신규 |
| `toggle_minute_chart_dialog`: `auto_popup` 분기 제거 → 항상 `restore_saved_geometry()` | 수정 |
| `MireukDashboard.closeEvent()` 신규 추가 | geometry 저장 보장 |
| `_post_reload_hook` 필드 + `set_minute_chart_post_reload_hook` 어댑터 | active position 재동기화 훅 |

**`main.py`**

| 항목 | 수정 |
|---|---|
| `_chart_reload_hook` 등록 (`set_minute_chart_post_reload_hook`) | 재시동 시 active position 마커 복원 |

### 수정 전후 복원 현황

| 항목 | 수정 전 | 수정 후 |
|---|---|---|
| 당일 분봉 데이터 | ❌ QTimer.singleShot 미발동 | ✅ pyqtSignal emit |
| 완료 거래 이력 | ❌ 동일 이유 | ✅ |
| 레짐 색상 바 | ❌ reset 후 미복원 | ✅ _apply_reload_result |
| 활성 포지션 마커 | ❌ reset_session 경쟁 조건 | ✅ _chart_reload_hook |
| 윈도우 위치·크기 (수동) | ✅ restore_saved_geometry | ✅ 동일 |
| 윈도우 위치·크기 (자동팝업) | ❌ 항상 제2모니터 중앙 | ✅ restore_saved_geometry |
| 윈도우 위치 저장 (메인 종료) | ❌ closeEvent 미호출 | ✅ MireukDashboard.closeEvent |

---

## 2026-06-19 (206차 — poc_distance z폭발 근본 수정: VP 버퍼 DB 복원)

### 문제 배경

12:32 장중 재시작 후 `poc_distance z 폭발` 관찰.

### 근본 원인

```
프로세스 재시작
  → VolumeProfileCalculator.__init__() → 빈 deque(maxlen=60)
  → _restore_analysis_buffers(): SHAP/Corr 복원 O, VP 버퍼 복원 X (누락)
  → 재시작 후 bars 1~9: poc_distance = 0.0 (default, len < 10)
  → bars 10~59: 짧은 윈도우로 계산 → POC 불안정
  → 장중 5+ 포인트 이동 시: poc_distance > 0.0167 → z > 4

부가: 스케일러 std(0.00417)가 구조적으로 낮게 학습됨
  → cold-start 0.0값이 raw_data.db에 쌓여 std 하향 오염
  → 정상 full-window값도 z 임계에 가까워짐
```

스케일러 실측: `mean=-0.000185, std=0.004173` → z>4 조건: poc_distance > ±0.0167 (±5.5포인트)

Fix 2 (clip ±0.040) 검토 후 **기각**: Fix 1 완료 후 z>4 케이스는 진성 시장 신호(5.5포인트+ 이격) → 클리핑 시 신호 손실. 이득 없음.

### 수정 내용 (206차)

**`utils/db_utils.py`**: `fetch_recent_raw_candles(limit=60)` 추가
- `raw_candles` 테이블에서 최근 60봉 `high/low/close/volume` oldest→newest 반환

**`main.py`** `_restore_analysis_buffers()`:
- `fetch_recent_raw_candles` import 추가
- SHAP 복원 블록 직후 VP 버퍼 복원 코드 추가
  - 최근 60봉 로드 → `_vol_profile.update()` 순서대로 투입
  - 실패 시 cold start 유지 (예외 무시, warn 로그)
  - `[AnalysisRestore]` 로그에 `vp_bars=N` 추가

### 예상 효과

- 재시작 직후 첫 분봉부터 60봉 성숙 VP 윈도우 사용
- `poc_distance` cold-start 기본값(0.0) 완전 소멸
- z폭발 원천 차단 (DB 비어있으면 cold start 유지, 기존 동작 그대로)
- 로그: `[VPRestore] VP 버퍼 복원 완료: 60봉`

---

## 2026-06-19 (205차 — 5m FL편향·30m acc 10%·SGD 15% 악순환 구조 수정)

### 문제 배경

장중 관찰 (11:52 기준):
- `5m FL편향 80%` 지속
- `30m 정확도 10%` (UP=10, DN=13, FL=7 — 방향 혼재, 둘 다 틀림) → DriftRetrain 발동
- `SGD 비중 15~16%` (기본값 30%, min 10%)

### 근본 원인 (악순환 루프)

```
GBM 30m acc=10% (UP/DN 혼재)
  → DriftRetrain 발동 → 경량 재학습
  → 재학습 완료해도 BiasReset/SGD 상태 구 GBM 기준 그대로 유지 ← 버그
  → 5m uniform fallback 고착 + SGD 15% 유지
  → GBM FL 편향 교정 불가
  → 다시 acc 낮음 → 루프 반복
```

부가 원인:
1. **SGD CUT_THR 30m=0.52** — 랜덤워크 근사 구간에서 52% 달성 구조적 불가 → 매분 -0.02씩 바닥 수렴
2. **DriftRetrain 60분 대기** — acc=10% 극단 혼란에도 60분 기다려야 함
3. **PATH_LABEL_RATIO 전역 0.55** — 30m 훈련 데이터에서 FL 레이블 과소 생성 → GBM이 UP/DN 과잉 예측

### 수정 내용 (205차)

**제안1**: `main.py` `_on_gbm_retrain_done` — 재학습 성공 시 BiasReset·SGD 상태 초기화
```python
self._bias_override_horizons.clear()
self._bias_fl_streak = {h: 0 for h in HORIZONS}
for _bh in HORIZONS: self._bias_buf[_bh].clear()
self.online_learner.reset_daily()
```

**제안2**: `online_learner.py` — `_CUT_THR["30m"]` 0.52 → 0.42

**제안3**: `main.py` DriftRetrain 조건B 추가
- acc30m < 15% + n>=15 + 30분 경과 → 조기 재학습 (60분 대기 생략)

**제안4**: `learning/batch_retrainer.py` — `PATH_LABEL_RATIO_BY_HZ` 호라이즌별 분리
- 1m:0.60 / 3m:0.58 / 5m:0.55 / 10m:0.52 / 15m:0.50 / **30m:0.45** (FL 허용 기준 완화)
- Phase2 레이블 루프 + 메인 retrain 루프 두 곳 모두 적용

### 예상 효과

- DriftRetrain 완료 직후 `[BiasReset]` uniform fallback 즉시 해제 → 5m 기여 복구
- SGD 30%로 즉각 복구 → GBM 대항력 회복
- acc=10% 극단 혼란 시 30분 후 재학습 발동 (기존 60분)
- 다음 GBM 재학습 시 30m FL 레이블 증가 → UP/DN 과잉 예측 완화

---

## 2026-06-19 (203차 — EKS z_ok 영구 차단 버그 수정)

### 문제 배경

6/19 장중 EKS 발동(09:05) 후 회복 불가 — `z_ok=False(z=18)` 5회 반복(09:20~11:24).

### 근본 원인

`_last_canary_z_warn` stale 고착 버그.

```
Canary 블록이 pre_market_setup() [08:55, 1회만 실행] 안에 있음.
  → _last_canary_z_warn = 18 (전날 스케일러 기준)

이후 PreMarket refit 완료 → 실제 z=4로 감소
  → SHS _z_warn_count: 4 (매분 update_z_warn 갱신, 정상)
  → _last_canary_z_warn: 18 (갱신 없음, 고착)

EKS 회복 평가 (30분마다):
  _p3_z_warn = getattr(self, "_last_canary_z_warn", 0)  ← 18 stale
  z_ok = 18 < 15 = False  → 회복 불가

conf_hits=10/10(필요 3), scaler_ok=True 모두 충족 중
→ z_ok 1개 조건만으로 하루 종일 차단
```

### 수정 내용 (main.py:5054, 1줄)

```python
# 수정 전
_p3_z_warn = getattr(self, "_last_canary_z_warn", 0)

# 수정 후
_p3_z_warn = getattr(self.model, "last_z_warn_count", 0)
```

`model.last_z_warn_count`는 매분 `predict_proba()` 실행 시 실시간 갱신됨.  
`safety/system_health.py` 독스트링 `< 5` → `< 15` 불일치도 함께 수정.

### 예상 효과

내일 EKS 발동 시에도 30분 후 회복 시 `z_ok = 4 < 15 = True` → 자동 해제 가능.  
`[SHS-EKS] EKS 자동 해제 (회복 #1)` 로그 출현 확인 필요.

---

## 2026-06-19 (201차 — 프리장 갭오픈 즉시 반영 점진 scaler 재적합)

### 문제 배경

6/19 장초반 로그:
- `[EarlyWarmup]` scaler 노후=16h → 08:45 선행 warmup (전날 DB 기준)
- `[Canary]` z경고=18개 ≥ 임계 12개 → 08:55 장전 재적합 시작
- `[PreMarket]` 3봉 z경고=10개 → 08:57:58 재적합
- `[SHS-EKS]` conf_max=0.0% bars=5 → **당일 관망 선언**
- `[ConstOut]` ['1m'] 상수 출력 확정 → 09:21 scaler 재적합

재적합이 3회 실행됐음에도 EKS 발동 → 딥다이브 결과 구조적 결함 발견.

### 근본 원인

**`_on_pre_market_bar()`가 피처를 계산하고도 `raw_data.db`에 저장하지 않음.**

```
기존 흐름:
프리장 봉 → 피처 계산(predict_proba용) → 버려짐
재적합 호출 → load_features_for_warmup() → raw_data.db (전날 데이터만)

결과: EarlyWarmup·Canary refit·PreMarket refit 모두 "전날 DB"가 입력
      → 오늘 갭오픈 분포 미반영 → z경고 18개 → conf≈50% → EKS
```

이것은 104차 EarlyWarmup 도입 이후 166차 프리장 파이프라인 전체 구현까지
7세대에 걸쳐 누적된 Escaped 패턴의 종착지.

### 개선 이력 요약 (Escape 체인)

| 세대 | 커밋 | 해결 | Escaped 이유 |
|---|---|---|---|
| 1 | 104차 | 24h 노후 scaler 사전 갱신 | 17h 케이스 미커버 |
| 2 | 112차 | 4h → 매일 발동 보장 | 전날 DB 기준 → 갭오픈 분포 괴리 |
| 3 | 143차 | Canary 즉시 재적합 추가 | 과거 DB 기준 동일 문제 |
| 4 | 166차 | 프리장 봉 + GapOffset 선행 | DB 저장 안 함 → 재적합 미흡수 |
| 5 | 177차 | EKS 회복 z=15로 완화 | 갭오픈 클 때 z>15 여전히 발동 |
| **6** | **201차** | **프리장 봉 DB 저장 + 점진 재적합** | — |

### 수정 내용

**`config/settings.py`**
```python
PRE_MARKET_REFIT_MIN_BARS = 3           # 삭제
PRE_MARKET_REFIT_STEPS = frozenset({1, 5, 10, 14})  # 신규
```

**`main.py` — `_on_pre_market_bar()`**

핵심 추가:
```python
save_candle_and_features(candle, _pm_ts, _pm_feats)  # ← 동기 저장
```

점진 재적합 구조 (1회 완료 플래그 → STEPS 4회):
- Phase1 (1봉/08:45): 갭오픈 즉시 반영 + ScalerWarmup 스킵 예약
- Phase2 (5봉/08:49): 분포 안정화
- Phase3 (10봉/08:54): 충분한 샘플 수렴
- Phase4 (14봉/08:58): 09:00 직전 최종 확정
- 각 Phase 완료 시 z경고 before→after 비교 로그

### 예상 효과

```
08:45~08:58: 전날DB(500봉) + 프리장봉 누적 → scaler 점진 수렴
09:00 GAP_OPEN: z경고 목표 ≤5개 → conf 정상화 → EKS 미발동
```

---

## 2026-06-19 (200차 — PreRetrain 타이밍 레이스 수정)

`daily_close(15:40)` 시점에 `retrain_eod.py`(15:45~15:57 완료)의 마커 파일이 없어
`eod_retrain_ok_date`가 session_state에 미저장 → 다음날 PreRetrain 오판.

**수정**: `pre_market_setup()`에 fallback 추가 — session_state 미기록 시
`data/eod_retrain_done_*.txt` 마커 파일 직접 검색(1~5일 이내).

커밋: `59a7195`

---

## 2026-06-18 (199차 — UI 응답없음·파이프라인 멈춤 근본 수정)

### 문제 배경

금일 장중(12:17~14:18) 파이프라인이 반복 멈추고 시스템이 8회 재시작됨.
원인 추적 결과 **오늘 신설한 `conf_trend_widget.py`** (신뢰도게이트 금일 conf→진입단계 추적 카드)가 주범으로 확인.

### 인과관계 (증명)

`ConfTrendWidget.refresh()` — 30초 타이머 — 전체 ensemble_decisions 테이블 렌더링:

| 시각 | 당일 행수 | setItem() | 블로킹 | 결과 |
|---|---|---|---|---|
| 09:00 | 1행 | 10회 | 0.0초 | 정상 |
| 12:17 | 195행 | 1,950회 | **7.8초** | 최초 5분 공백 |
| 12:54 | 220행 | 2,200회 | **8.8초** | 14분 공백 + 재시작 |
| 14:16 | 266행 | 2,660회 | **10.6초** | 연속 재시작 |

30초 중 7-10초 Qt 메인스레드 점유 → COM 콜백(`FutureCurOnly`) 수신 지연 → `_on_candle_closed()` 불규칙 → 파이프라인 멈춤.

### 수정 내용

**conf_trend_widget.py** (근본 수정):
- `MAX_ROWS=30` (전체→최근 30봉, setItem 600회 → 300회)
- In-place 업데이트: 두 번째 이후 `setItem()` 없이 `item().setText()` 재사용
- `setUpdatesEnabled(False/True)` 배치 렌더링
- `substr(ts,1,10)=?` → `ts >= ? AND ts < ?` (인덱스 활성화)
- `setStyleSheet` 조건부 적용

**MinuteChartDialog** (1분봉 차트 응답없음):
- `reload_today()` 메인스레드 블로킹 → `QTimer.singleShot(0, _start_reload_thread)` 비동기화
- `mouseMoveEvent` 16ms throttle (60fps 상한)
- `paintEvent` 거대 캔버스 가드 (>3000px 즉시 반환)
- `restore_saved_geometry` 범위 초과 시 복원 스킵
- `setSpan(0,0,1,1)` → `clearSpans()`

**장외 BlockRequest 블로킹 방지** (main.py):
- `_ts_refresh_dashboard_balance_inner` 장외 즉시 반환
- `_ts_sync_position_from_broker` 스케줄러 경로 장외 가드

**`restore_panels_from_history` 백그라운드화** (session_recovery_service.py):
- 무거운 DB 쿼리(`_gather_efficacy_stats` 등) → 백그라운드 스레드
- 완료 후 QTimer.singleShot으로 UI 업데이트 (메인스레드 안전)

**substr 쿼리 인덱스 활성화** (전체):
- `ensemble_decisions`, `predictions`, `raw_candles`, `mc_history` 등
- `WHERE substr(ts,1,10)=?` → `WHERE ts >= ? AND ts < ?`
- `predictions.db` 439MB, `idx_ensemble_ts` 인덱스 존재하나 함수 적용으로 무력화됐던 것 수정

### LiveDBG 진단 코드 (장중 검증 후 제거)

다음 로그 태그로 추가 이슈 모니터링:
- `[LiveDBG] _tick_header 간격 Xms` — 메인스레드 블로킹 직접 검출
- `[LiveDBG] ConfTrend step1~6 Xms` — 각 단계 타이밍
- `[ChartDBG] paintEvent slow Xms` — 차트 렌더링 병목
- `[LiveDBG] request_futures_balance 호출` — BlockRequest 경로 추적

### 신규 파일 (git 추적 시작)

- `dashboard/panels/conf_trend_widget.py` — 신뢰도게이트 금일 conf→진입단계 추적
- `dashboard/panels/candle_chart_dialog.py` — 봉차트 방향 인디케이터 (matplotlib)
- `dashboard/panels/direction_indicator_dialog.py` — 호라이즌 합창판 방향 인디케이터

---

## 2026-06-18 (197차 — P8 스케일러 재적합 retrain_eod.py 재배치)

### 문제 배경

`daily_close()`(15:40)에서 P8 스케일러 재적합이 실행되지만, 이후 실행되는
`retrain_eod.py`(15:45)가 26주 기준 스케일러를 포함한 pkl을 저장해 P8 효과를 매일 덮어씼음.
두 스크립트가 동일한 `model/scaler/scaler_{hz}.pkl` 경로에 저장하므로 나중 실행이 최종 상태.

### 해결 방안 (A안 채택)

| 파일 | 변경 |
|---|---|
| `retrain_eod.py` | `p8_scaler_refit()` 추가 — GBM 재학습 완료 직후 500봉 스케일러 최종화. `session_state.json`에 `p8_last_success_date` 기록 |
| `main.py` daily_close() | P8 블록(57줄) 제거 → 재배치 사유 주석으로 교체 |
| `model/multi_horizon_model.py` | 로그 포맷 `100%` → `100%%` 버그 수정 (`--- Logging error ---` 스팸 원인) |
| `scripts/catch_up_eod.py` | `trigger_reason` 문구 실제 용도(수동 복구)로 수정. 신규 git 추적 시작 |

### 올바른 EOD 실행 흐름 (197차 이후)

```
15:40  daily_close()
         ├─ (GBM 재학습: in-process, OOM 가능 → 실패해도 잔여 단계 계속)
         ├─ DBWriter 플러시
         ├─ WAL checkpoint (6개 DB)   ← DB 쓰기 완료 후 → 올바른 위치
         └─ auto-shutdown (~15:41)

15:45  retrain_eod.py (py310_64)
         ├─ GBM 재학습 full (26주, full_cv=True)
         └─ p8_scaler_refit()         ← 500봉 최신 스케일러 최종화 ✅
```

### 오늘(2026-06-18) 장마감 작업 현황

- Windows Task Scheduler(`MireukiEODRetrain`) 미실행 (LastTaskResult: 267011)
- 수동으로 처리:
  - `retrain_eod.py` (py310_64): 6/6 호라이즌 교체, 합계 194.3s → `eod_retrain_done_20260618.txt` 생성
  - `catch_up_eod.py --skip-retrain` (py37_32): P8 ✅ WAL 6/6 ✅
- 스케줄러 미실행 원인 조사 필요 (내일 실행 전 확인)

---

## 2026-06-17 (191차 — EOD 재학습 OOM 해결 + py310_64 장외 스케줄러 분리)

### 문제 배경

매일 15:40 `daily_close()` 내 EOD 재학습이 py37_32(32-bit Python) 메모리 단편화로
`StandardScaler.fit_transform` 중 22.2 MiB 연속 블록 할당 실패 → 재학습 스킵 반복.
RF 이종 앙상블도 사실상 매일 미학습 상태였음.

### 해결 방안 및 구현

| 파일 | 변경 |
|---|---|
| `learning/batch_retrainer.py` | `_save_model` + `_save_feature_names` 4곳에 `pickle.dump(..., protocol=4)` 추가 — py37_32 로드 호환 |
| `retrain_eod.py` (신규) | py310_64 전용 장외 독립 재학습 스크립트. 완료 마커 `data/eod_retrain_done_{YYYYMMDD}.txt` 생성 |
| `register_eod_scheduler.ps1` (신규) | 윈도우 스케줄러 매일 **15:45** 자동 등록 스크립트 |

### 실측 결과 (py310_64 / sklearn 1.0.2 / 40,080행×97열)

```
데이터 로드:  39.9s
재학습:      169.2s  (GBM 6/6 + RF 6/6 호라이즌)
합계:        209.4s  (약 3분 30초)
peak 메모리: ~200 MB  (OOM 없음)
```

- full_cv=True / False 차이: **0.7초** — 절단 없이 full 재학습해도 CUSUM 필터 효과로 동일
- py37_32에서 pkl 로드 호환 확인: 6/6 호라이즌 모두 OK (protocol=4 적용)

### py310_64 환경 정보

```
경로:    C:\Users\82108\anaconda3\envs\py310_64\python.exe
Python:  3.10.20 64-bit
sklearn: 1.0.2  (py37_32와 동일 버전 → pkl 완전 호환)
numpy:   1.26.4
```

### 스케줄러 등록 완료

```
태스크명:  MireukiEODRetrain
실행 시각: 매일 15:45
다음 실행: 2026-06-18 15:45
상태:      Ready
```

### 내일 확인 포인트

- `Get-ScheduledTask -TaskName "MireukiEODRetrain" | Get-ScheduledTaskInfo` → `LastTaskResult: 0`
- `data/eod_retrain_done_20260618.txt` 생성 확인
- `logs/retrain_eod_20260618.log` 에서 `6/6 호라이즌 교체` 확인
- main.py `[EarlyWarmup] scaler 노후` 경고 소멸 여부

---

## 2026-06-17 (190차 — SGD 학습 B군 피처 N분봉 교정)

### 현재 시스템 상태

| 항목 | 상태 |
|---|---|
| SGD 학습 B군 피처 교정 | `main.py:5659-5686` — 장기 호라이즌(10m·15m·30m) SGD learn() 시 봉 크기 의존 피처를 DB 저장 1분봉값 대신 `_hz_feat_cache` N분봉값으로 교체. A군(옵션·매크로·VWAP)은 현행 유지. 캐시 없는 초기 구간은 교정 스킵. |

**교정 대상 피처:**
- 10m: `hurst`, `mlofi_slope`, `vwap_momentum`, `cvd_monotone_ratio`
- 15m: `volume_acceleration`, `avg_volume`, `atr_ratio`, `toxicity_atr_stress`
- 30m: `atr_ratio`, `toxicity_score_ma`, `queue_signal_ma`, `toxicity_atr_stress`, `threshold_feasibility`

### 배경 (189~190차 연속 분석)

SGD는 예측 시 N분봉 피처(`_hz_feat_vecs`)를 사용하지만 학습 시 DB 저장 1분봉 피처를 사용해 왔음. 피처 이름(NAME)은 `horizon_feature_sets.json`으로 고정되어 있으나, 봉 크기 의존 피처(B군)는 1m값 ≠ Nm값:
- `hurst` 1m 20봉 ≠ 10m 20봉 (프랙탈 시간척도 완전히 다름)
- `volume_acceleration` 1m 거래량 vs 15m 거래량 (절대값 15배 차이)
- `atr_ratio` 1m ATR vs Nm ATR (스케일 상이)

이로 인해 SGD가 1m 틱 잡음과 장기 레이블 간 허위 상관을 학습 → acc 저하 및 collapse 원인 중 하나.

A군(옵션 체인, 일봉 매크로, 일간 VWAP/POC)은 봉 크기 무관하여 현행 유지.
A안(DB에 N분봉 피처 저장) 전체 구현은 Phase C 재학습 완료 + 모의투자 4주 후로 일정 확정. (`docs/260617_SGD_NMIN_FEATURE_CORRECTION_PLAN.md` 참조)

### 다음 장 모니터링

1. 10m/15m/30m SGD acc 변화 관찰 — B군 교정 효과로 acc가 이전 대비 개선되는지
2. `_hz_feat_cache` 미존재 구간(장 초반 N분) 스킵이 정상 동작하는지

---

## 2026-06-17 (189차 — SGD UP/DN 붕괴 감지 + BAR_CACHE_DECAY 적용 + FULL_RESET_PENDING 수정)

### 현재 시스템 상태

| 항목 | 상태 |
|---|---|
| SGD 단방향 붕괴 감지 | `learning/online_learner.py` — FL 단독 감지 → UP/DN/FL 3방향 통합. `u=1.000` / `d=1.000` 15분 지속 시 해당 호라이즌 SGD 자동 리셋. 오늘 30m UP(19분) + 5m/10m DN(4~9분) 붕괴가 자동 복구 없이 방치된 것이 계기 |
| SGD_FULL_RESET_PENDING | `config/settings.py:109` `True → False`. 재시작마다 첫 GBM 재학습 시 `reset_full()` 반복 발동 → acc_buf 소실·SGD비중 30% 초기화 문제 해소. 오늘 14:21 재학습 완료 시 SGD 완전 초기화가 발생한 근본 원인 |
| BAR_CACHE_DECAY 적용 | `main.py:3916-3920` — 정의만 되고 미사용이던 `_BAR_CACHE_DECAY`를 실제 적용. bar_age 경과 시 캐시 피처값 점진 감쇠 (30m: 0.97^age). conf 고착 + SGD collapse 동시 완화 |

### 세션 중 발견된 이슈 (수정 완료)

| 이슈 | 원인 | 수정 |
|---|---|---|
| `15m sgd=u=0.998 11분 고착` | UP 붕괴 감지 없음 (FL만 감지) | UP/DN/FL 3방향 감지로 통합 |
| 14:21 SGD 갑자기 초기화 | `SGD_FULL_RESET_PENDING=True` 파일에 잔존 | False로 수정 |
| `[CONF⚠] 30m bar_age=19` conf 고착 | `_BAR_CACHE_DECAY` 미적용 | 실제 적용 |

### 오늘 50분정확도 분포 분석 (참고)

- 총 358분 관측, 평균 42.0% (기준 48% 미달)
- 0.0% 32분(8.9%): SGD 붕괴 구간
- 50.0% 41분(11.5%): fallback(acc_buf 비어있음) — 초기 P2-D 전체 차단 또는 SGD 리셋 직후
- P2-D 필터(conf<0.52)가 오늘 전체 예측의 89.4%를 차단 → 실학습 극히 희소
- "50분정확도" 라벨은 ACCURACY_WINDOW=100 기준 실제 100분 윈도우 (명칭 불일치)

### 다음 장 최우선 확인

1. `[OnlineLearner] Xm SGD UP붕괴 자동 복구` / `DN붕괴 자동 복구` 로그 정상 출력 확인
2. `[CONF⚠] Xm bar_age=N` 고착 분수가 이전 대비 감소하는지 확인 (BAR_CACHE_DECAY 효과)
3. `SGD_FULL_RESET_PENDING` 관련 재시작 후 `[SGD] threshold 교체 후 완전 리셋 완료` 로그 미출력 확인

---

## 2026-06-16 (182차 — EOD MemoryError 복구 + validate_and_resync() 허위 정합성오류 버그 수정)

### 현재 시스템 상태

| 항목 | 상태 |
|---|---|
| 오늘자 EOD (15:40) | MemoryError로 중단됐던 것을 `scripts/catch_up_eod.py`로 수동 복구 완료 — GBM 재학습(40,093행, 6/6 호라이즌) + P8 스케일러 재적합(6/6) + WAL 체크포인트(6/6 DB) 전부 OK |
| `daily_close()` EOD 재학습 예외 내구성 | `retrain_now()` 호출을 try/except로 감싸 MemoryError 등 예외 발생해도 P8·Platt·MetaConf 저장·일일 리셋·WAL 체크포인트는 계속 진행되도록 수정 (`main.py:6546`) |
| `validate_and_resync()` 허위 정합성오류 버그 | 수정 완료 — 스케일러(항상 전체 97개 기준)를 Phase C 슬라이싱된 호라이즌별 피처수(12~15개)와 비교해 영구 불일치로 오판하던 버그. 전 6개 호라이즌이 매 재학습/재시작마다 거짓으로 `_is_fitted=False`(→FLAT 디폴트 예측 대체) + `resync_mismatch` 재학습 무한 재트리거 — 오늘 7회 발생, 일부는 6분 간격 페어로 GBM 재학습이 비계획적으로 반복됨 (`model/multi_horizon_model.py:805`) |
| 검증 | 수정 후 `MultiHorizonModel()` 직접 인스턴스화해 `validate_and_resync()` 재호출 — `BAD HORIZONS: []`, 6개 호라이즌 전부 `fitted=True` 확인. 라이브 미반영(재시작 필요) |

### 활성 알려진 이슈

- **오늘 GBM 모델 신뢰도 불확실 구간**: `resync_mismatch` 루프로 인해 09:01~13:03 사이 여러 차례 6개 호라이즌이 일시적으로 FLAT 디폴트(33.3%)로 대체됐을 가능성 — SGD 블렌딩이 가렸을 수 있어 그 구간 진입/판단 로그를 재검토할 여지 있음
- **PipePerf "[GBM재학습중]" 정체와의 연관**: 오늘 앞서 분석한 09:26-09:28, 11:14-11:15 STEP1 정체가 이 버그로 인한 비계획 재학습과 겹쳤을 가능성

### 다음 장 최우선 확인

1. `[Model] 정합성 오류` 로그 재발 없음 확인 (재시작·재학습 후)
2. `resync_mismatch` 사유의 비계획 GBM 재학습 재발 없음 확인
3. EOD(15:40) 재학습이 MemoryError로 실패해도 `[P8] EOD 스케일러 재적합 완료`·`[WAL] 체크포인트 완료`가 이어서 출력되는지 확인

---

## 2026-06-16 (181차 — time_zone 크래시 수정 + 진입단계 추적 카드 전면 개선 + 로그 파일화)

### 현재 시스템 상태

| 항목 | 상태 |
|---|---|
| `time_zone` UnboundLocalError | 수정 완료 — STEP6의 체크리스트 선행평가·MetaGate 호출이 `_tz`(이미 할당됨)를 쓰도록 교정. 라이브 미반영(재시작 필요) |
| 신뢰도게이트 "진입단계 추적" 카드 | STEP7 마스터 게이트 16조건 + 차단사유까지 반영하는 10단계 체계로 전면 개선 (`dashboard/panels/dynamic_mc_panel.py`) |
| `ensemble_decisions` DB | `entry_gate_json/entry_final_ok/entry_qty/entry_mode/entry_executed/entry_block_reason` 6컬럼 추가 (재시작 시 자동 마이그레이션) |
| `LogManager` | 대시보드 버퍼 전용이던 `log_manager.signal/system/trade/health`가 이제 SYSTEM/SIGNAL/TRADE/LEARNING `.log` 파일에도 동시 기록됨 |
| 검증 | `python -m py_compile` 5개 파일 통과. PyQt5 UI 렌더링·라이브 동작은 미검증(재시작 필요) |

### 활성 알려진 이슈 (이번 세션 신규)

- **대시보드 신규 컬럼 시각 미확인**: "차단사유"/단계 9·10/게이트 툴팁이 실제 UI에서 의도대로 그려지는지 다음 재시작 후 확인 필요
- **STEP7 게이트 데이터는 재시작 이후 분봉부터 채워짐**: 재시작 전 과거 행은 `entry_final_ok` 등이 NULL → 패널이 구버전 7단계("진입후보")로 자동 폴백(의도된 동작)

### 다음 장 최우선 확인

1. 재시작 직후 `[ERR-FATAL] minute_pipeline: local variable 'time_zone'` 크래시 미재발 확인
2. 신뢰도게이트 탭 "금일 Conf → 진입단계 추적" 카드에 "차단사유" 컬럼·9/10단계·게이트 툴팁이 정상 표시되는지 확인
3. Hurst<0.45 등으로 STEP7 차단되는 분봉이 실제로 "8. STEP7 차단" + 정확한 사유 텍스트로 표시되는지 확인
4. `.log` 파일(`SIGNAL.log` 등)에서 `[차단] Hurst...` 등 기존엔 대시보드에만 있던 메시지가 grep으로 확인되는지 점검

---

## 2026-06-16 (180차 — CB 파이프라인 정체 진단 + 워치독 무한루프 버그 수정)

### 현재 시스템 상태

| 항목 | 상태 |
|---|---|
| PipePerf 라벨 | `_all_steps_str` 오프셋 수정 — `S2=Xms`가 진짜 STEP2(SGD)를 가리킴 (종전엔 STEP1 검증 시간이 S2로 오표기) |
| `verify_and_update()` | raw_fetch/pred_select/pred_update/pred_insert 4구간 서브타이밍 계측 추가 (300ms 초과 시 `[Buffer-Timing]` 로그) |
| `verify_and_update()` DB 접근 | `_db_write_lock`으로 직렬화 + busy_timeout 10s→3s (fail-fast) |
| 파이프라인 워치독 | `is_force_exit_time(now)` 가드 추가 — 15:10 강제청산 이후 워치독·복구시도 비활성화 |
| 검증 | `main.py`/`learning/prediction_buffer.py`/`utils/db_utils.py` `ast.parse` 통과. 라이브 미반영(재시작 필요) |

### 활성 알려진 이슈 (이번 세션 신규)

- **PipePerf 정체 근본 원인 미확정**: sub-timing 계측은 추가했으나 다음 정체 재발 전까지 `[Buffer-Timing]`으로 raw_fetch/pred_select/pred_update/pred_insert 중 실제 병목 확인 안 됨
- **timeout=3.0 단축 부작용 모니터링 필요**: 너무 자주 실패(검증 스킵)하면 상향 검토

### 다음 장 최우선 확인

1. `[PipePerf]` 로그에서 `S1=Xms`로 정상 라벨링 확인 (정체 시 S1이 커야 정상 — STEP1=검증)
2. `[Buffer-Timing] total=...` 로그 발생 시 raw_fetch/pred_select/pred_update/pred_insert 중 병목 구간 확인
3. 15:10 이후 "파이프라인 N분 미실행" 경보가 반복되지 않는지, 강제청산 후 `run_minute_pipeline` 추가 실행 로그가 없는지 확인
4. `[Buffer] verify_and_update 배치 오류` (timeout) 빈도 — 잦으면 timeout 상향 검토

---

## 2026-06-16 (179차 — Phase C 슬라이싱 버그 + SGD + CORE + UI)

### 현재 시스템 상태

| 항목 | 상태 |
|---|---|
| 피처셋 (GBM) | 97개 공유 + Phase C 호라이즌별 슬라이싱 정상 동작 |
| 스케일러 | 97개짜리 정상 저장 (12개 오류 해소) |
| ScalerRefresh | A_WARMUP·B_INTRADAY·C_PERIODIC 전 호라이즌 정상 갱신 확인 |
| SGD | P0(피처슬라이싱)·P1-B(호라이즌별 가중치)·P1-C(FLAT억제)·P2-D(고신뢰도필터)·P2-E(초기부스트) 적용 |
| CORE | 단기/중기/장기 그룹별 분리 (settings·checklist·model·dashboard 전 반영) |
| FeaturePanel | Phase A·B·C 구현 완료 (CORE × 호라이즌 매트릭스 포함) |
| 진입 최적화 | STABLE_TREND min_conf 48% + 편향패널티 TrendGate 연동 + reduce_thr 완화 |
| 모의투자 실거래 | 11:43 TP3 청산 +1.5pt / +72,914원 |

### 활성 알려진 이슈

- **feat=121 vs managed=97**: ScalerWarmup 피처 수 불일치 (registry 갱신 필요)
- **quality_investor_fetch_count D_FORCE 반복**: 매 5분마다 consec=5 → 이진 피처 차단 검토
- **ConstOut 해소 지연**: 재시작 후 순환 ConstOut 14분 지속 (CONST_OUT_MIN_BARS 3분 검토)
- **S2 지연**: 분봉 교체 직후 TickUI 폭발 + DB WAL 경합 (근본 해결 미완)

### 다음 장 최우선 확인

1. SGD `[OnlineLearner] 1m 가중치 조정 SGD=XX%` 로그 형식 (호라이즌별 독립)
2. STABLE_TREND 구간 `[P1] Checklist min_conf 분리: 0.XX→0.48` 로그
3. TrendGate ON 구간 편향패널티 로그 없음
4. ERR-FATAL 없음

---

## 2026-06-15 (178차 — 호라이즌별 피처셋 인프라 + opt_chain 버그 수정)

### 작업 개요

기획안(`featureset by horizon/미륵이_호라이즌별_최적피처셋_기획안.docx`) 기반
Phase A~D 구현 + opt_chain_snapshot 수집 버그 3종 수정.

### 완료된 변경

| Phase | 파일 | 핵심 내용 |
|---|---|---|
| A (macro 복구) | `collection/macro/macro_fetcher.py` | yfinance 429 대응 → Cboe CDN(VIX) / Yahoo v8 daily(S&P) / Treasury XML(US10Y) / Naver+frankfurter(KRW) 교체. source_code=4.0 달성 |
| B (JSON 작성) | `featureset by horizon/horizon_feature_sets.json` | 6개 호라이즌 × include/exclude 명세. 12개 need_add 피처 식별 |
| C (인프라) | `features/horizon_feature_registry.py` (신규) | JSON 로드, get_available_feature_set(), 컬럼 슬라이싱 |
| C | `learning/batch_retrainer.py` | _save/_load_feature_names(horizon_key), retrain 루프 X 슬라이싱 |
| C | `model/multi_horizon_model.py` | horizon_feature_names dict + _hz_feat_indices 사전계산, predict_proba 슬라이싱, validate_and_resync 호라이즌별 검증 |
| C | `main.py` STEP5 | 주석 추가 (실질 변경 없음 — 모델 내부 슬라이싱) |
| D (검증) | `featureset by horizon/validation_results.md` | Walk-Forward 결과 저장 |
| Bugfix | `main.py` L3537 | _chain_feats → _option_combined 병합 (opt_chain_pcr/gex_bn/atm_* 미전달 버그) |
| Bugfix | `main.py` run() | _investor_timer(60s) + _option_chain_timer(300s) QTimer 생성·시작 코드 추가 |

### Phase D Walk-Forward 결과 (핵심)

| 전략 | 10m | 15m | 30m | 판정 |
|---|---|---|---|---|
| 공유 97개 | 0.4104 | 0.3957 | 0.3911 | 베이스라인 |
| Registry strict | 0.4073 | 0.3909 | **0.3538** | **REGRESS** |

**원인**: opt_gex_bn(ρ=0.290), opt_chain_pcr(ρ=0.245) 등 핵심 신호 DB 미수집.  
**결정**: opt 4주 축적 후 Phase D 재검증 시까지 **공유 97개 피처셋 유지**.

### opt_chain 버그 수정 효과 (다음 장부터 적용)

- `opt_chain_pcr`, `opt_gex_bn`, `opt_gex_sign`, `opt_atm_put_oi`, `opt_atm_call_oi`, `opt_atm_pcr`가 raw_features에 저장 시작
- 수급 데이터(investor_net) 장중 60초마다 주기 갱신 시작

### 현재 피처셋 상태

- 공유 pkl: 97개 (production 사용 중)
- per-horizon pkl: 미존재 (opt 수집 안정화 후 retrain 시 생성 예정)
- raw_features DB: 118개 피처 수집 중 (opt_chain_pcr 등 추가됨 — 다음 장부터)

### 다음 장 확인 사항

1. `[OptionChain] 갱신 X.Xs | PCR=X.XXX ATM_PCR=X.XXX GEX=X.XXB avail=True` 로그 확인 (5분마다)
2. `raw_features`에 `opt_chain_pcr`, `opt_gex_bn` 키 저장 여부 (장 종료 후 DB 조회)
3. `[Macro] 갱신 | VIX=XX.XX SP500chg=+0.XXXX` 로그 확인 (fallback_used=0.0)

---

## 2026-06-15 (177차 — C_PERIODIC 독립 타이머 + P1-A 강화 + EKS z조건 완화)

### 배경 (20260615 로그 분석)

| 이상점 | 수치 | 원인 |
|---|---|---|
| C_PERIODIC 미발동 | 10:25까지 전무 | D_FORCE가 `_last_scaler_refit_at` 리셋 + B/C 경로 조기 차단 |
| _gbm_retrain_running 30분 타임아웃 | 09:53 완료 → 10:25 강제 해제 | ok=True 시 P1-A 리셋 스킵, QTimer daemon-thread 발화 불안정 |
| EKS z_ok=False 지속 | z=22 (3회 연속) | `z_warn_count < 5` 기준이 장 시작 극단 z 스파이크로 달성 불가 |

### 수정 내용

| 수정 | 파일 | 핵심 변경 |
|---|---|---|
| P0-A | `model/multi_horizon_model.py` | `_last_periodic_refit_at` 신규 — D_FORCE와 B/C PERIODIC 타이머 분리. D_FORCE가 60분 카운터 리셋 불가 |
| P0-B | `main.py` 3곳 + `_on_gbm_retrain_done` | ok/fail 무관 worker에서 `_gbm_retrain_running = False` 즉시 리셋. `_gbm_retrain_started_at = None` 콜백에 추가 |
| P0-C | `safety/system_health.py` | EKS 회복 z조건 `z_warn_count < 5` → `< 15` (실측 z=22 기준) |

### 다음 장 확인 사항

- `[ScalerRefresh] trigger=C_PERIODIC` 로그 확인 (D_FORCE 연속 중에도 60분마다 발동)
- `[GBM] 재학습 플래그 30분 타임아웃 강제 해제` 로그 **없음** 확인
- `[SHS-EKS] EKS 자동 해제 ... z_warn=22` — z=22여도 conf_hits 충족 시 해제 확인

---

## 2026-06-11 (156차 — GBM 플래그 고착 + ScalerRefresh 3종 수정)

### 배경 (20260611 SIGNAL/LEARNING 로그 분석)

| 이상점 | 수치 | 원인 |
|---|---|---|
| macro_vix z폭발 | z=+35.24 | 학습기간 VIX 저변동 → σ 극소화 (155차 _MACRO_SCALE_FLOOR로 해결됨) |
| 스케일러 98분 미갱신 | 09:00~10:38 갱신 없음 | `_gbm_retrain_running` 고착 → Phase B 전 구간 차단 |
| GBM 재학습 하루 0회 | LEARNING.log에 `[Retrain] 완료` 없음 | feat_rows 조기 체크 통과 → 미래가격 제거 후 14766 < 15000 실패 |
| MetaConf 과소 | 5연속 41~47% | conf 기반이 stale scaler → z폭발로 GBM 혼란 |
| 진입 0건 | 하루 종일 | 위 연쇄 |

### 수정 내용 (P1/P2/P3)

| 수정 | 파일 | 핵심 변경 |
|---|---|---|
| P1-A | `main.py` 4곳 | `ok=False` 시 `_gbm_retrain_running = False` worker thread 즉시 리셋 |
| P1-B | `main.py` 5곳+1곳 | `_gbm_retrain_started_at` 추적 + Phase B 직전 30분 타임아웃 강제 해제 |
| P2 | `batch_retrainer.py` | feat_rows 기준 조기 체크 삭제 → 미래가격 제거 후 records 기준 단일 체크 |
| P3 | `main.py` Phase B | B/C_PERIODIC — `_gbm_retrain_running` 무관 독립 실행. D_FORCE만 내부 skip |

### 다음 장 확인 사항

- `[Retrain] 배치 재학습 시작 (weeks_back=26)` + 미래가격 제거 후 15000+ 행 확인 (P2)
- `[ScalerRefresh]` C_PERIODIC 60분 내 발동 확인 (P3)
- 스케일러 미갱신 60분 초과 경고 없음

---

## 2026-06-11 (155차 — EKS·conf100%·SHAP 3종 수정)

### [A] EKS min_conf 통합

**파일:** `safety/system_health.py`, `main.py`

**문제:** EKS 발동 기준이 고정 `EKS_CONF_THRESHOLD=0.45`인데 DynMC GAP_OPEN mc=0.346. 기준 불일치 → EKS가 실제 운영 기준(34.6%)보다 훨씬 높은 45%에서 발동/회복 판단.

**수정:**
- `evaluate_early_kill_switch(gap_open_mc: float = EKS_CONF_THRESHOLD)` 파라미터 추가
- `main.py` 호출 시 `gap_open_mc=get_zone_min_confidence("GAP_OPEN")` 전달
- 회복 `_threshold = max(current_mc, 0.42)` → `_threshold = current_mc` (0.42 floor 제거, window 3/10 조건이 노이즈 방어)

### [B] conf=100% FLAT 탈출 Fix 3종

**파일:** `model/ensemble_decision.py`, `model/multi_horizon_model.py`

**탈출 경로:** GBM `up=0.00004, down=0.00004, flat=0.70`. CONF_CLIP(0.80) 미발동 → `round(up,4)=0.0` → `flat_score=max(0,1-0-0)=1.0` → calibration·cap 우회 → conf=100%.

| Fix | 파일 | 내용 |
|---|---|---|
| Fix1 | `ensemble_decision.py` | flat_score 직접 가중합. `1-up-down` 수식 제거 + 정규화 |
| Fix2 | `ensemble_decision.py` | FLAT 방향 0.85 cap 추가 (UP/DN과 동일 처리) |
| Fix3 | `multi_horizon_model.py` | `_PROB_FLOOR=0.0001` — `predict_proba` + `_predict_masked` 양쪽에 극소값 floor |

### [C] SHAP TreeExplainer 폴백 개선

**파일:** `learning/shap/shap_tracker.py`

**문제:** shap 0.41.0 + 3-class GBM 비호환. `TreeExplainer`·`shap.Explainer` 둘 다 실패.

**수정 (3-tier fallback):**
1. Tier 1: TreeExplainer (기존 — 실패 시 WARNING→INFO 다운그레이드, 1회만)
2. Tier 2 (NEW): `model.estimators_[i][k].feature_importances_` per-class 평균 → `max(axis=0)`. global avg 대비 상관 0.7753, 방향별 신호 포착
3. Tier 3: global `feature_importances_` (기존 최종 fallback)

**신규 기능:**
- `get_class_ranking(class_labels=["UP","DN","FL"])` — 방향별 피처 중요도 순위 반환
- `weekly_review()` `direction_top` dict 추가 + 로그 `방향별분석=ON`

### 다음 장 확인 사항

- `[SHS-EKS] 기준=XX.X%` 로그 — DynMC mc와 일치 확인 (고정 45% 아님)
- `[SHS-EKS] 회복 기준=XX.X%` — max(mc,0.42) 없이 mc 직접 사용 확인
- conf=100% 재발 없음 (SIGNAL.log 전수)
- SHAP weekly_review `방향별분석=ON` + `direction_top` 키 출력 확인

---

## 2026-06-10 (147차 — 장중 Retrain acc 하락 근본 원인 2종 수정)

### 발견 배경 (20260610 LEARNING 로그)

| 관측 | 수치 |
|---|---|
| 10m acc 추이 | 0.6169 → 0.6057 → 0.6044 (장중 하락) |
| EOD 10m acc | 0.6044 → 0.8051 (폭등) |
| EOD 30m acc | 0.6190 → 0.8905 (폭등) |
| DriftAdjuster 실측 acc | 22~50% (CV 89%와 대조적) |

### BUG-A (P0): force=True 하향 래칫 — 코드버그

**위치:** `main.py:2156(_intraday_retrain_worker)`, `main.py:3075(STEP 3 warmup)`

**메커니즘:**
- `_train_horizon:381` 조건: `if force or cv_acc > old_acc - 0.01`
- force=True이면 cv_acc가 old_acc-1% 아래여도 강제 저장
- 10m 예시: cv_acc=0.6057 < old_acc-0.01=0.6069 → 기존 0.6169 모델 덮어쓰기
- 다음 Retrain의 old_acc=0.6057 → 기준점 하향 → 하향 래칫

**수정:** `force=True` → `force=False` 2곳
- 08:55 pre-market(`_pre_retrain_worker:2578`)만 force=True 유지
  - 이유: 전날 EOD 과장 acc(10m 0.80 등)를 정상화하려면 force=True 필요

**효과 (수정 후 예상):**
- Retrain 2(11:36): 10m cv_acc=0.6057 → old_acc=0.6169 유지 (0.6057 < 0.6069 → 유지)
- 장중 내내 0.6169 모델 보존

### BUG-B (P1): 미래 가격 없는 행 FLAT 오염 — 알고리즘버그

**위치:** `batch_retrainer.py:_load_from_db`

**메커니즘:**
- `_load_from_db`는 `WHERE ts >= cutoff` → 오늘 데이터 포함
- 오늘 T시점 Retrain에서: 오늘 rows 중 `ts > now-30min` 인 행은 30m 후 가격 없음
- `_path_conditioned_label` → FLAT 반환 (실제는 UP/DOWN일 수 있음)
- 이 FLAT 행들이 TimeSeriesSplit 마지막 validation fold에 포함 → acc 하락
- EOD 역현상: 오늘 완전한 레이블 → val fold acc 89%로 폭등 (DriftAdjuster 22%와 gap)

**수정:** `_load_from_db:737` 이전에 close_map 기반 필터 추가
```python
_max_h_min = max(HORIZONS.values())  # 30
records = [(ts, feat) for ts, feat in records
    if (ts + 30min) in close_map]  # 미래 가격 없는 행 제외
```

**효과:**
- 장중: 오늘 마지막 ~30행 제거 → FLAT 오염 제거 → cv_acc 안정화
- EOD: 14:41-15:10 구간 ~29행 제거 → 89% 폭등 억제

### 다음 장 확인 사항

- 장중 세션 재시작 후 Retrain 로그에서 `[Retrain] {hz} 유지` 출력 확인 (acc 하락 시)
- `[Retrain] 미래 가격 불완전 행 X개 제거 (max_horizon=30m 후 종가 없음)` 로그 확인
- EOD Retrain acc가 0.65 미만으로 안정화되는지 확인
- DriftAdjuster 실측 acc와 CV acc 간격이 줄어드는지 모니터링

---

## 2026-06-10 (146차 — MetaConf class_weight 버그 + RF OOB 근본 원인 3종)

### 문제 발견 (20260610 LEARNING 로그 딥다이브)

| 이상점 | 증거 | 근본 원인 |
|---|---|---|
| MetaConf 학습 오류 매분 반복 | `[MetaConf] 학습 오류: class_weight 'balanced' is not supported for partial_fit` — 09:24부터 세션 끝까지 200회+ | sklearn `SGDClassifier(class_weight="balanced")` + `partial_fit()` 비호환 |
| RF OOB 전 호라이즌 랜덤 수준 | 1m=46.2%, 3m=37.5%, 5m=39.4%, 10m=45.0%, 15m=45.9%, 30m=48.1% (3-class random=33%) | BUG #1: 추론 시 `apply_robust_preprocess` 미적용 (train/test 불일치) + BUG #2: 저성능 RF 고정 30% 앙상블 오염 |
| SHAP 주간 심사 중복 | 12:44~12:52 구간 매분 2회 출력 | 2차 Retrain 세션(11:04)이 145차 수정 미반영 구버전 실행 — 12:52 3차 세션부터 정상 |

### BUG #1 (P0): MetaConf `class_weight='balanced'` + `partial_fit` 비호환

**증상:** 09:24~세션 끝까지 매분 동일 오류 → MetaConf SGD 학습 완전 중단 (MetaGate 확률 품질 저하)

**원인:** sklearn `SGDClassifier`는 `class_weight="balanced"` 지정 시 `partial_fit()` 에서 예외 발생. `fit()`에서만 동작함.

**수정 (`learning/meta_confidence.py`):**
- `class_weight="balanced"` 제거 (SGDClassifier 생성자 2곳: `__init__`, `_reset_model`)
- `_make_sample_weight(y)` 정적 메서드 추가: `compute_class_weight('balanced', ...)` → `sample_weight` 배열 계산
- `_partial_fit_incremental`, `_partial_fit` 양쪽에서 `sw = self._make_sample_weight(y)` → `partial_fit(..., sample_weight=sw)` 전달

### BUG #2 (P0): RF 추론 시 `apply_robust_preprocess` 미적용

**증상:** RF는 학습 시 `apply_robust_preprocess(X)` (atr/avg_volume log1p, clip) 적용 후 학습하지만, 추론 시 raw `feat_vec` 그대로 입력 → 스케일 불일치 → OOB 실제 정확도보다 추론 정확도 훨씬 낮음

**수정 (`model/rf_horizon_model.py` `predict_proba_single`):**
```python
from model.multi_horizon_model import apply_robust_preprocess
x2d = x.reshape(1, -1)
if self.feature_names:
    x2d = apply_robust_preprocess(x2d, self.feature_names)
```

### BUG #3 (P1): 저성능 RF 고정 30% 앙상블 오염

**증상:** 3m(37.5%), 5m(39.4%) RF OOB가 랜덤+4~6pp 수준인데 GBM+SGD 앙상블에 30% 고정 혼합 → 앙상블 성능 저하

**수정 (`main.py` STEP 5 RF 블렌딩):**
```python
_oob_hz = self.rf_model.get_oob_scores().get(h_name, 0.0)
_w_rf = 0.30 if _oob_hz >= 0.45 else 0.0  # 45% 미만 = RF 제외
```
- OOB < 45% (랜덤+12pp 미만): 해당 호라이즌 RF 블렌딩 비활성화
- 현재 기준: 3m, 5m 제외 / 1m, 10m, 15m, 30m 30% 유지

### 기타 이상점 (수정 불필요)

| 이상점 | 판단 | 이유 |
|---|---|---|
| OnlineLearner SGD 가중치 Retrain마다 리셋 (short/long 28%→10%) | 아키텍처 설계 — 변경 불필요 | Retrain 세션이 가중치를 재평가하는 정상 동작 |
| Retrain acc 미세 하강 (5m: 0.6123→0.6057→0.6052) | 정상 범위 — 조치 불필요 | 동일 cutoff(2026-04-01) 데이터로 반복 재학습 시 미세 진동 |
| RF OOB 방법론적 한계 (random holdout vs temporal) | 알려진 한계 — 코드 버그 아님 | RF OOB는 시간 정보 무시 — GBM은 TimeSeriesSplit으로 보완 |

### 수정 파일 요약

| 파일 | 변경 내용 |
|---|---|
| `learning/meta_confidence.py` | SGDClassifier `class_weight="balanced"` 제거 + `_make_sample_weight` + `sample_weight=sw` 전달 |
| `model/rf_horizon_model.py` | `predict_proba_single`: `apply_robust_preprocess` 추론 전 적용 |
| `main.py` | RF 블렌딩: 고정 30% → OOB ≥ 0.45 조건부 30% (미달 시 0%) |

### 다음 장 확인 사항

- `[MetaConf]` 학습 오류 로그 미발생 확인
- RF 추론 오류 없음 (`[RF] … 예측 오류` 로그 미발생)
- OOB 낮은 호라이즌 RF 블렌딩 skip 로그 없음 (동적 가중치 0은 로그 없음, 정상)
- 다음 Retrain 후 RF OOB 45% 이상 호라이즌이 앙상블에 반영되는지 확인

---

## 2026-06-10 (144차 — 파이프라인 지연 134차 escape 5종 근본 수정)

### 문제 원인 (20260610 로그 딥다이브)

| 현상 | 근본 원인 | escape 이유 |
|---|---|---|
| 09:47 17,569ms 극단 지연 | ConstOut scaler refit(daemon) + GBM 재학습(daemon) 동시 raw_data.db 접근 → I/O + GIL 경합 | 134차: scaler_monitor.db만 WAL 처리 / 136차: online_learner만 크리티컬 경로 제거 |
| ConstOut ['15m'] 2회 반복 (09:21, 10:04) | scaler만 재적합 → GBM 트리 구조 미변경 → 30분 쿨다운 후 재발 | 100차 ConstOut 설계 가정 오류 |
| CB③ 당일 정지 (EKS 발동 후에도) | EKS 활성(관망 선언) 상태에서 CB③이 추가 당일 정지 → 중복 제약 | CB③ / EKS 연결 고리 미설계 |
| 17s 지연 STEP breakdown 불가 | PipePerf CB임박 로그가 logger.warning → SYSTEM 로그에 미출력 | 134차 Fix 6 채널 오배치 |

### 개선 내용 (144차)

| 항목 | 상태 | 파일 |
|---|---|---|
| [P0-A] scaler refit + GBM 재학습 상호 잠금 — Phase B / D_PRICE_MOMENTUM / ConstOut 3곳 | **완료** ✅ | `main.py:3482,3530,3700` |
| [P0-B] ConstOut 재적합 완료 후 GBM 재학습 자동 연계 (`_on_const_out_refit_done`) | **완료** ✅ | `main.py:1345,3718` |
| [P1-A] EKS 활성 시 CB③ HALT 스킵 (`record_accuracy` eks_active 파라미터) | **완료** ✅ | `circuit_breaker.py:202`, `main.py:2838` |
| [P2-B] ConstOut 완료 후 acc30m 버퍼 리셋 (`reset_acc30m_buffer`) | **완료** ✅ | `circuit_breaker.py:474` |
| [Layer0] PipePerf CB임박 로그 SYSTEM 채널 추가 | **완료** ✅ | `main.py:4822` |

### 다음 장 확인 사항

- GBM 재학습 중 scaler refit 트리거 skip 로그 없음 확인 (정상이면 skip 로그 없어야 함)
- ConstOut 발생 시 `[ConstOut] {hz} → GBM 재학습 예약` 로그 확인
- ConstOut 발생 시 `[CB③] acc30m 버퍼 리셋` 로그 확인
- EKS 발동 상태에서 CB③ 경고/HALT 로그 미발생 확인
- 극단 지연 발생 시 `[PipePerf][CB임박] total=Xms | S1=Xms S2=Xms ...` SYSTEM 로그 출력 확인

---

## 2026-06-10 (145차 — horizon_proba={} 빈 예측 근본 원인 수정)

### 문제 원인 딥다이브 결과

**증상:** ConstOut 발생 → scaler refit 완료 후 `conf=100%, dir=FLAT`이 1시간+ 지속

**143차에서 escape된 이유:**
- 143차 수정(CONF_CLIP, temperature scaling, ShortHorizonOverride/TrendBoost 정규화)은 "GBM이 극단 확률을 반환하는 경우"를 전제로 함
- 실제 근본 원인은 "GBM이 아무것도 반환하지 않는 경우" (`horizon_proba={}`) → 완전히 다른 경로

**진짜 근본 원인 (145차 발견):**

`model/multi_horizon_model.py` 섹션 8 모니터링 코드의 `continue` 위치 오류:

```python
# 버그 코드 (이전)
if monitor_ts and scaler:
    ...
    if not (extreme_count > 0 or age > 90):
        continue  ← for 루프 전체 continue → 예측 코드(line 383~) 스킵됨
    _monitor_rows.append(...)
    
classes = list(clf.classes_)   ← continue 발동 시 여기도 건너뜀
results[horizon] = {...}       ← 미설정 → results = {} → horizon_proba = {}
```

**역설적 트리거 연쇄:**
- 09:03~10:04: 스케일러 노후/극단 z-score 존재 → `extreme_count > 0 = True` → continue 미발동 → 정상 예측
- 10:04:01: ConstOut D_FORCE refit 완료 → 스케일러 정상화 → `extreme_count=0, age=1분` → continue 발동!
- 결과: `horizon_proba={}` → `flat_score=1.0` → `conf=100%, dir=FLAT` 1시간 지속

**핵심 아이러니:** ConstOut을 감지하고 스케일러를 "고칠수록" 예측이 멈춥니다.

### 수정 내용 (145차)

| 항목 | 상태 | 파일 |
|---|---|---|
| `continue` → 조건부 `_needs_insert` if 블록으로 교체 — 예측 코드는 항상 실행 | **완료** ✅ | `model/multi_horizon_model.py:338-385` |

### 다음 장 확인 사항

- ConstOut 발생 후에도 `[DBG-F6] horizons: 1m:...` 6개 정상 출력 확인
- ConstOut 발생 후 `conf=100%` 이상점 미발생 확인
- `[ScalerMonitor]` 로그가 extreme/노후화 시에만 출력되는지 확인

---

## 2026-06-10 (142차 — EOD 자동종료 흐름 안전화)

### 개선 내용

| 항목 | 상태 | 파일 |
|---|---|---|
| `_ShutdownSignal(QObject)` + `QueuedConnection` — QTimer 비-Qt 스레드 호출 근본 수정 | **완료** ✅ | `main.py:170-179, 349-350` |
| `_schedule_shutdown()` 신규 — 메인 스레드에서 Qt 위젯·QTimer 처리 | **완료** ✅ | `main.py:6027-6039` |
| `_run_daily_close` 예외 처리 — `_emit_done` 플래그로 종료 보장 | **완료** ✅ | `main.py:6602-6615` |
| DBWriter 큐 플러시 — `put(None)` + `join()` WAL 체크포인트 직전 | **완료** ✅ | `main.py:5983-5992` |
| WAL 체크포인트 6개 DB 전체 (`EOD_WAL_CHECKPOINT_DBS`) | **완료** ✅ | `config/settings.py:33-37` |
| EOD `retrain_now(force=False)` 명시 | **완료** ✅ | `main.py:5674` |

### 다음 장 확인 사항

- 15:40 이후 `[System] 자동 종료 실행` 로그 반드시 출력 (자동종료 미발동 재발 없음)
- `[DBQueue] EOD 플러시 완료` + `[WAL] 체크포인트 완료` 6개 DB 모두 로그 확인
- 예외 경로: `[DailyClose] 예외 발생 — 강제 종료 예약` 로그 + 프로그램 정상 종료

---

## 2026-06-09 (138차 — MetaGate 구조 수정 2종)

### 문제 원인 (20260609 SIGNAL 로그 딥다이브)

| 이상점 | 증거 | 원인 |
|---|---|---|
| MetaGate 518건 전부 skip | reduce/take=0건, skip=518건 | (A) reduce_thr=0.80×min_conf=0.456 → blended 분포 최대 0.502, 중앙 0.279로 대부분 미달 |
| SGD 붕괴 floor 불작동 | 15:21: raw=0.062 → rule=0.062 (동일값) | (B) rule_based도 급변장+낮은정확도 조합에서 0.06 반환 → 절대하한 없음 |
| SGD 붕괴 감지 지연 | 10:36 붕괴 후 ~10분간 meta_raw≈0 지속 | (C) _is_collapsed() 30회 누적 필요 → 약 10분 지연 |

**blended 분포 (오늘 기준):** min=0.196 / 중앙=0.279 / 최대=0.615 / 평균=0.298

### 개선 내용 (138차)

| 항목 | 상태 | 파일 |
|---|---|---|
| SGD 붕괴 floor: 임계 0.15→0.20, 절대 하한 0.25 추가 | **완료** ✅ | `meta_gate.py:63` |
| reduce_thr: 0.80×→0.75× (ens=0.570,meta=0.25→blended=0.442≥0.428) | **완료** ✅ | `meta_gate.py:86` |
| _is_collapsed() 조기 감지: 10회/0.10 추가 (약 3분 단축) | **완료** ✅ | `meta_confidence.py:138` |

**수정 효과 시뮬 (오늘 518건 replay):** skip 518→460, reduce 0→58 (11.2% 통과)

### 다음 장 확인 사항

- MetaGate: reduce 또는 take 액션 발생 여부 (오늘은 0건이었음)
- SGD 붕괴 발생 시 floor log: `SGD 붕괴 보완: raw=0.0XX → floor=0.250`
- blended 분포가 0.43+ 범위로 상승하는지 (hurst 수정 효과 + 더 많은 학습 데이터)
- meta_raw 하루 추이: 시작 0.5+ → 저하 폭 감소 (SGD 조기 리셋으로 회복 빠름)

---

## 2026-06-09 (137차 — cvd_dir/hurst/latency 3종 근본 수정)

### 문제 원인 (20260609 로그 딥다이브)

| 버그 | 증거 | 원인 | 파일 |
|---|---|---|---|
| cvd_dir=+0 전 장 고착 | DBG-F4 cvd_dir=+0, 체크리스트 cvd=✗ 100% | `int(±0.5) = 0` — Python 소수점 버림 | `main.py:3979,3116` |
| hurst=0.500 2시간→0.070 급변 | 09:00~11:01 고착, 이후 극단값 | `sqrt(std)` 중첩 → 기울기 H/2 underestimate | `hurst_exponent.py` |
| latency=0.000s 전 장 고착 | DBG-CB latency=0.000s | Cybos: record_api_latency 미호출 → _last_latency 미갱신 | `circuit_breaker.py` |

### 개선 내용 (137차)

| 항목 | 상태 | 파일 |
|---|---|---|
| `_dir_sign()` 헬퍼 추가 — 부호 기반 변환 (크기 무관) | **완료** ✅ | `main.py` |
| DBG-F4 로그: `int()` → `_dir_sign()` | **완료** ✅ | `main.py:3116` |
| 체크리스트 전달: `int()` → `_dir_sign()` | **완료** ✅ | `main.py:3988` |
| hurst `sqrt(std)` → `std` + `1e-10` floor | **완료** ✅ | `hurst_exponent.py` |
| `record_pipe_latency` → `_last_latency` 갱신 | **완료** ✅ | `circuit_breaker.py` |

### 다음 장 확인 사항

- DBG-F4에서 `cvd_dir=+1` 또는 `-1` 출력 (더 이상 +0 고착 아님)
- 체크리스트 `cvd=✓` 비율 상승 확인
- hurst 값이 0.35~0.65 정상 범위에서 변화 (더 이상 0.500 또는 0.07 고착 아님)
- DBG-CB `latency=0.XXXs` 실측값 출력 (더 이상 0.000s 고착 아님)
- 진입 발생 여부 (cvd 복원 + hurst 정상화 → grade=A 유지 → conf 임계 통과 기대)

---

## 2026-06-09 (136차 — S2 파이프라인 지연 근본 수정)

### 문제 원인 (딥다이브 결론)

| 원인 | 증거 | 파일 |
|---|---|---|
| online_learner.learn() 이 크리티컬 경로(S2)에서 동기 실행 | 13:54 S2=7201ms, 14:03 S2=5815ms — GBM 배치 재학습 중 Python GC/CPU 포화 | `main.py` |
| S2 서브-타이밍이 SYSTEM logger.debug()로 전송 → INFO 필터링 → 실종 | DEBUG.log에 [S2] 로그 없음 | `main.py` |
| _save_model() 원자 쓰기 없음 | open(path,"wb") 직접 쓰기 → 경합 시 불완전 파일 읽기 리스크 | `batch_retrainer.py`, `rf_horizon_model.py` |

### 개선 내용 (136차)

| 항목 | 상태 | 파일 |
|---|---|---|
| [S2-A] online_learner.learn() → "end" 이후로 이동 | **완료** ✅ | `main.py` |
| [S2-B] S2 sub-타이밍 debug_log 로 교정 (DEBUG.log) | **완료** ✅ | `main.py` |
| [S2-C] S2 > 1000ms 시 SYSTEM WARN 출력 | **완료** ✅ | `main.py` |
| [S2-D] _save_model() · RF.save_all() 원자 쓰기 | **완료** ✅ | `batch_retrainer.py`, `rf_horizon_model.py` |

### 다음 장 확인 사항

- CB⑤ 5000ms 트리거 재발 없음 (S2 이제 < 100ms 예상)
- `[SGD-deferred] NNNms` DEBUG.log 에 학습 지연 시간 확인
- 만약 SGD-deferred 가 2000ms 초과 시 → SYSTEM WARN 로그 발생
- 135차 확인사항도 함께: D_FORCE cvd_direction 발동 없음, MetaGate reduce/take 등장

---

## 2026-06-09 (135차 — Meta skip·conf=100% 4종 근본 원인 수정)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| MetaGate reduce_thr 공식 수정 (`max(0.38, min_conf)`) | **완료** ✅ | `strategy/entry/meta_gate.py` |
| actual_min_conf MetaGate 전달 (STEP 6) | **완료** ✅ | `main.py` |
| SGD 붕괴 보완 — rule-based floor (meta_conf<0.15) | **완료** ✅ | `strategy/entry/meta_gate.py` |
| MetaConfidenceLearner 붕괴 자동 감지·복구 | **완료** ✅ | `learning/meta_confidence.py` |
| AutoMask CORE 피처 면제 (`_CORE_MASK_EXEMPT`) | **완료** ✅ | `model/multi_horizon_model.py` |
| cvd_direction·cvd → `DFORCE_EXCLUDE_FEATURES` 추가 | **완료** ✅ | `config/settings.py` |
| refit_scalers_only() CORE 피처 scale 보호 (`scale_<0.05`) | **완료** ✅ | `model/multi_horizon_model.py` |

### 오늘 장 이상 패턴 (6/9 실측, 135차 패치 전)

```
[Meta skip] reduce_thr > blended → 전 분봉 meta skip
  원인 1: reduce_thr 오프셋(+0.04) → 임계 0.438 > blended 0.42
  원인 2: actual_min_conf=0.398 vs UI mc=0.390 불일치 → 더 높은 임계 사용
  원인 3: SGD 붕괴 → meta_raw=0.000 → blended=ens×0.6만 → reduce_thr 미달

[conf=100%] 12:50~13:11+ 21분간 dir=+0 conf=100.0% grade=X
  원인: D_FORCE ScalerRefresh(12:49) → 500봉 all cvd=-1 → std=0 → scale=1
        transform(-1)=0 → GBM "중립 CVD" → FLAT 100%
```

### 내일 장 확인 사항

- D_FORCE 로그에서 `feat=cvd_direction` / `feat=cvd` 발동 없음 확인
- AutoMask 로그에서 `cvd_direction` 격리 없음 확인 (_CORE_MASK_EXEMPT 효과)
- conf=100% FLAT 고착 재발 없음
- C_PERIODIC/A_WARMUP 시 `[ScalerRefresh] CORE 'cvd_direction' std≈0 → 이전 scale 복원` 로그 (scale 보호 동작)
- MetaGate: `reduce_thr` 적정 범위(min_conf ± 0) 확인, skip 비율 정상화

---

## 2026-06-09 (134차 — 파이프라인 지연 CB⑤ 2종 제거: STEP4 비동기 + scaler_monitor WAL)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| Fix 3: STEP 4 candle/horizon_features DB 큐 비동기화 | **완료** ✅ | `main.py` |
| Fix 4: daily_close WAL 체크포인트 | **완료** ✅ | `main.py` |
| Fix 6: PipePerf CB임박 스텝별 breakdown 로그 | **완료** ✅ | `main.py` |
| Fix 7: scaler_monitor INSERT 큐 비동기화 (`last_monitor_rows`) | **완료** ✅ | `main.py`, `model/multi_horizon_model.py` |
| Fix 8: `scaler_monitor.db` WAL 모드 (`journal_mode=WAL`) | **완료** ✅ | `model/scaler_monitor_db.py` |
| Fix 9: monitor rows 조건부 수집 (extreme>0 or age>90m) | **완료** ✅ | `model/multi_horizon_model.py` |

### 10:23 CB⑤ (5943ms) 근본 원인 분석

```
10:22±  배경 Phase C/ConstOut 재적합 → update_event_refresh() 호출
        → scaler_monitor.db EXCLUSIVE lock 획득 (DELETE journal mode)
10:23   STEP 5 predict_proba() 내부 insert_events_batch() 동기 호출
        → EXCLUSIVE lock 대기 (timeout=5s) → 5943ms 발생
10:24   HealthPolicy Degraded Mode 진입 (warn_streak=2)
10:25   2028ms 경고 (디스크 I/O 아직 높음)
```

### 내일 장 확인 사항

- `[PipePerf][CB임박]` 로그에서 어느 STEP이 느린지 확인 (Fix 6)
- CB⑤ 5943ms 재발 없음 확인 (Fix 7/8 효과)
- `[DBQueue] 큐 포화` fallback 로그 없음 확인 (정상 비동기 처리)
- Degraded Mode 진입 없음 확인

---

## 2026-06-09 (133차 — 이진 피처 D_FORCE 반복 차단 + EKS 재시작 안정화)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| `is_open_volatile` D_FORCE 트리거 제외 | **완료** ✅ | `model/multi_horizon_model.py` |
| `opt_pcr_bullish/bearish` D_FORCE 제외 + CLIP | **완료** ✅ | `config/settings.py`, `model/multi_horizon_model.py` |
| EKS 재시작 후 09:15+ 봉 없으면 미발동 확정 | **완료** ✅ | `safety/system_health.py` |

### 6/9 진입0 원인 분석 (132차 패치 이후 잔존 문제)

```
08:45  1차 기동 (132차 패치 前 코드) → 'min_conf' KeyError × 5 → EKS 발동
09:13  재시작 (132차 패치 적용)
09:13+ is_open_volatile z=+15.78 → D_FORCE 매분 발동 → 스케일러 불안정
       → CoherenceGate 차단 반복 (방향 합의 불가)
       CB⑤ S2=5~9초 → 5분 정지 13회
       conf 39~43% (actual_mc ≈ 41%) → 간신히 미달
       OnlineLearner 50분 정확도 27~38% 폭락 → SGD 가중치 최소
재시작 5회 → GAP_OPEN 봉 카운터 0 반복 → EKS 판정 유예 메시지 반복
```

### 내일 장 확인 사항

- `is_open_volatile`, `opt_pcr_bullish` D_FORCE 로그에서 제외됐는지 확인
  (극단 z 경고는 나와도 D_FORCE 발동 없어야 함)
- CoherenceGate 차단 횟수 감소 확인
- 재시작 후 `[SHS-EKS] 재시작 후 GAP_OPEN 봉 없음 (09:15 이후) — EKS 미발동 확정` 로그 확인

---

## 2026-06-09 (132차 — 장전/장시작 연쇄 오류 7종 패치)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| `'min_conf'` KeyError (ERR-FATAL 근본 원인) 수정 | **완료** ✅ | `model/ensemble_decision.py:290` |
| main.py decision.get() 안전 접근 (방어 레이어) | **완료** ✅ | `main.py:3606` |
| Canary z경고 EarlyWarmup 후 임계 5→12 완화 | **완료** ✅ | `main.py:2325` |
| CB⑤ 장 시작 완화 구간 09:00~09:10 (9000ms) | **완료** ✅ | `safety/circuit_breaker.py:408` |
| EKS 최솟 bars=3 조건 (bars<3 발동 유예) | **완료** ✅ | `safety/system_health.py:84` |
| Degraded Mode 09:00~09:10 진입 유예 | **완료** ✅ | `main.py:1231` |
| **GBM 재학습** — 131차 패치 미반영 (131차 이월) | **미완료** ⏳ | 앱 재시작 후 "현재 세트 재학습" 클릭 |

### 오늘 장 연쇄 실패 흐름 (재발 방지 참고)

```
08:45  EarlyWarmup: 전날 데이터로 scaler refit (노후=16h → 0h)
08:55  Canary: z경고=12개 (전날 scaler ↔ 당일 피처 분포 괴리) → 허위 알림
09:00  파이프라인 6133ms → CB⑤ 5분 정지 (동시 스레드 부하)
09:01  ERR-FATAL: decision["min_conf"] KeyError (조기 반환 dict 누락 키)
09:02  동일 오류 반복 → GAP_OPEN bars=1 누락
09:06  EKS 발동(bars=1, conf=39.6%) + Degraded Mode 진입 → 당일 관망
```

→ 수정 1~7 적용 후 동일 패턴 재발 시 각 단계에서 차단됨.

### 내일 장 확인 사항

- `[Canary]` z경고피처 12개 미만이면 `⚠ z경고 폭증` 알림 미발생 확인
- `[CB⑤]` 09:00~09:10 `[장시작 버스트]` 태그 경고만, PAUSE 미발동 확인
- `[SHS-EKS] EKS 판정 유예 — GAP_OPEN 봉 부족` 로그 (bars<3 시)
- `[HealthPolicy] Degraded Mode 진입 유예 — 장 시작 초기` 로그 (09:10 전)
- ERR-FATAL `'min_conf'` 재발 없음

---

## 2026-06-08 (131차 — 진입0 탈출 5종 패치)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| CascadeCoherence FL 제외 패치 | **완료** ✅ | `model/ensemble_decision.py` |
| CascadeCoherence 임계값 0.34→0.25 | **완료** ✅ | `model/ensemble_decision.py` |
| MC_ABS_FLOOR 0.42→0.25 + REGIME_MIN_CONF 동기화 | **완료** ✅ | `config/settings.py` |
| BiasReset coldstart FL 기준 10분→5분 | **완료** ✅ | `main.py` |
| CORE CVD/OFI 강제X → pass_count-1 완화 | **완료** ✅ | `strategy/entry/checklist.py` |
| _restore_mc_from_history SELECT base_mc 누락 버그 수정 | **완료** ✅ | `strategy/entry/time_strategy_router.py` |
| **GBM 재학습** — 패치 반영 필요 | **미완료** ⏳ | 앱 재시작 후 "현재 세트 재학습" 버튼 클릭 |

### 6/8 진입0 원인 분석 결과

| 원인 | 건수 | 차단 비율 | 패치 |
|---|---|---|---|
| CascadeCoherence 차단 (FL 끼임) | 125건 | 37% | ②⑥ 완료 |
| 신뢰도 미달 (conf 33% vs mc 42%) | 161건 | 48% | ③ 완료 (MC_FLOOR 0.25) |
| CORE 피처 불일치 (CVD/OFI) | 22건 | 7% | ⑦ 완료 |
| 나머지 (FL 방향, etc.) | 27건 | 8% | — |

### 5종 패치 상세

| 패치 | 변경 전 | 변경 후 | 기대 효과 |
|---|---|---|---|
| ② Coherence FL 제외 | FL 끼면 즉시 break | directional만 집계 | 오늘 케이스 0.17→1.00 |
| ⑥ Coherence 임계값 | 0.34 | 0.25 | 차단 범위 축소 |
| ③ MC_ABS_FLOOR | 0.42 | 0.25 | 실 conf(27%) 수렴 허용 |
| ④ BiasReset coldstart | FL: 항상 10분 | coldstart: 5분 | 재기동 직후 즉각 대응 |
| ⑦ CORE CVD/OFI | 실패→강제X | VWAP만 강제X, CVD/OFI는 등급하락 | 기회 손실 방지 |

### MC_ABS_FLOOR 하강 경로 (주의)

MC_FLOOR=0.25지만 즉시 반영이 아님. 재학습마다 step_limit=0.03씩 단계적 하강:
- 현재: mc=0.42 (mc_history.db 복원값)
- 재학습 1회: 0.42-0.03=0.39
- 재학습 2회: 0.39-0.03=0.36
- ...→ conf_p65=0.279 수렴까지 약 5~6회 재학습 필요

`[DynMC] step clamp 적용` 로그로 정상 하강 확인 가능.

---

## 2026-06-08 (130차 — CVD SHAP 복구 + SHAP 추천 3단 개선 + 코드 정리)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| CVD signal_strength 단위 불일치 버그 수정 | **완료** ✅ | `features/technical/cvd.py` |
| buy_vol fallback (vol/2 → 가격기반 추정) | **완료** ✅ | `features/feature_builder.py` |
| cvd_divergence 부호 수정 (동방향=양수, 다이버전스=음수) | **완료** ✅ | `features/feature_builder.py` |
| raw_data.db 72,591봉 소급 재계산 | **완료** ✅ | `data/db/raw_data.db` |
| "현재 세트 재학습" 버튼 수정 (_on_gbm_retrain_done 상태 복원) | **완료** ✅ | `main.py` |
| SHAP 추천 알고리즘 3단 개선 | **완료** ✅ | `learning/shap/shap_tracker.py` |
| update_shap 3중 정의 → 1개로 통합 | **완료** ✅ | `dashboard/main_dashboard.py` |
| **GBM 재학습** — cvd_divergence 연속값 DB 반영 필요 | **미완료** ⏳ | 앱 재시작 후 "현재 세트 재학습" 버튼 클릭 |
| `_up_r` UnboundLocalError 조사 | **완료** ✅ (129차에서 수정됨) | `main.py:2777` |

### cvd_divergence 복구 결과

| 항목 | 수정 전 | 수정 후 |
|---|---|---|
| unique값 수 | 2개 (0.0 / -1.0) | 1,789개 |
| 값 범위 | {0.0, -1.0} | -1.0 ~ +1.0 |
| 이진값(±1.0) 비율 | 99.1%/0.9% | 1/500봉 미만 |
| SHAP 기여 (예상) | 0.0%, rank 63/101 | 재학습 후 개선 예상 |

### SHAP 추천 개선 결과 (즉시 효과)

- 이전: "추천 없음: 추천 후보 없음" (12개 엔트리가 모두 week 24 → declining 감지 불가)
- 이후: 3개 후보 즉시 감지 (기여도 미달 avg×0.3 이하 절대값 기준)
  - `prev_day_same_hour_ret` (rank 101, 0.0%)
  - `quality_investor_stale` (rank 100, 0.0%)
  - `macro_event_flag` (rank 99, 0.0%)
- 각 후보마다 다른 교체 후보 반환 (already_suggested set으로 중복 제거)

### 확인해야 할 사항 (다음 장 전)

- 앱 재시작 → "현재 세트 재학습" 클릭 → 버튼 enabled 복원 확인
- GBM 재학습 완료 후 SHAP 탭에서 cvd_divergence rank 상승 확인
- ~~`_up_r` UnboundLocalError~~: 129차에서 수정 완료 (재발 없음)

---

## 2026-06-08 (129차 — 3m/5m FL 편향 구조 버그 수정)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| F1AdaptiveWeight.update() FL 스킵 버그 수정 | **완료** ✅ | `model/ensemble_decision.py:139` |
| _fl_streak 임계값 70%→50% | **완료** ✅ | `model/ensemble_decision.py:322` |
| BiasReset 발동 조건 완화 (FL 20→10분, tot≥20→15, 80%) | **완료** ✅ | `main.py:2797-2799` |

### 확인해야 할 로그 (다음 장)

- `[EarlyDirDamp] 3m FL=XX% 10min → weight×0.2` — 버그 2 발동 확인
- `[BiasReset] 3m FL편향 XX% 10분 지속 → uniform fallback 적용` — main.py 발동 확인
- 3m/5m Bias⚠ 소멸 후 15m/30m DN 신호 기반 진입 발생 여부

---

## 2026-06-08 (125차 — Extreme 피처 5종 z-score 억제)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| `vwap_momentum` np.clip(±2.0) | **완료** ✅ | `features/feature_builder.py:536` |
| `opt_pcr_extreme` × 0.5 반감 | **완료** ✅ | `features/options/option_features.py:65` |
| `ret_1m/5m/15m` ±1%/2%/5% 클리핑 | **완료** ✅ | `features/feature_builder.py:496` |
| `cvd_direction` × 0.5 | **완료** ✅ | `features/feature_builder.py:146` |
| 수급 8개 피처 로그 압축 | **완료** ✅ | `features/feature_builder.py:370` |

### 잔여 extreme 피처 조치 사항

- `opt_pcr_extreme` 완전 삭제: GBM 재학습 + 실세션 1주 안정 확인 후 진행 (NEXT_TODO 조건 유지)

---

## 2026-06-08 (124차 — v8.0 Phase 0: 시간대 정책·캐스케이드 게이트·FL 감쇠·entry_ok 등)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| `TICK_SIZE = 0.05` 설정화 | **완료** ✅ | `config/settings.py` |
| `HORIZON_TIME_POLICY` / `HORIZON_COLDSTART_MIN_PASS` | **완료** ✅ | `config/settings.py` |
| `compute_cascade_coherence()` — 장기→단기 방향 흐름 검증 | **완료** ✅ | `model/ensemble_decision.py` |
| `select_entry_horizon()` — ATR 레짐별 최적 호라이즌 선택 | **완료** ✅ | `model/ensemble_decision.py` |
| FL 조기 감쇠 (`_fl_streak`) — FL 70%+ 10분→weight×0.2 | **완료** ✅ | `model/ensemble_decision.py` |
| `active_horizons` 시간대 정책 앙상블 적용 | **완료** ✅ | `model/ensemble_decision.py` |
| CascadeCoherence gate (< 0.34 차단) | **완료** ✅ | `model/ensemble_decision.py` |
| `entry_ok` 파라미터 — 0.0이면 즉시 X등급 | **완료** ✅ | `strategy/entry/checklist.py` |
| `is_market_open` / `minutes_to_close` 만기일 15:20 수정 | **완료** ✅ | `utils/time_utils.py` |
| `scaler_events` raw_value/pre_value/scaler_mean/scaler_std 컬럼 | **완료** ✅ | `model/scaler_monitor_db.py` |
| ScalerMonitorPanel Top5 6컬럼 확장 (raw→pre, μ/σ, 최근) | **완료** ✅ | `dashboard/panels/scaler_monitor_panel.py` |
| CYBOS_PLUS.bat STEP 0 (close_other_windows.ps1) | **완료** ✅ | `CYBOS_PLUS.bat`, `scripts/close_other_windows.ps1` |
| `docs/260607_MIREUK_V8_IMPLEMENTATION_PLAN.md` 신규 | **완료** ✅ | `docs/` |
| **main.py 연결** — `active_horizons` 계산 → `EnsembleDecision.compute()` 전달 | **미구현** ⏳ | `main.py` |
| **main.py 연결** — `entry_ok` 계산 → `EntryChecklist.check()` 전달 | **미구현** ⏳ | `main.py` |
| **feature_builder.py** — `prev_day_same_hour_ret` 버그 / `ema_cross` 연속 / `avg_volume` 분리 등 | **미구현** ⏳ | `features/feature_builder.py` |

### Phase 0 구현 항목 vs V8 계획서 우선순위

| V8 우선순위 | 항목 | 완료 |
|---|---|---|
| S0 | `vwap_momentum` 버그 (119차) | ✅ |
| S0 | `prev_day_same_hour_ret` 버그 | ⏳ 다음 세션 |
| 1 | 피처 반감기 적응 정규화 | ⏳ |
| 2 | 호라이즌 응집도 게이트 (CoherenceGate + CascadeGate) | ✅ |
| 3 | 시간대별 호라이즌 활성화 (HORIZON_TIME_POLICY) | ✅ (설정 완료, main.py 연결 ⏳) |
| 4 | ATR 레짐별 호라이즌 자동전환 (`select_entry_horizon`) | ✅ (함수 완료, main.py 연결 ⏳) |
| 5 | `entry_ok` 규칙 기반 게이팅 | ✅ (checklist 완료, main.py 연결 ⏳) |
| 6 | FeatureBuilder 6개 항목 | ⏳ 다음 세션 |

### 커밋

- `124차 커밋 완료` 2026-06-08

### 다음 장에서 확인할 것

1. `cascade_blocked` 로그 확인: 하위만 방향 있고 상위 FLAT 시 차단
2. `_fl_streak` 로그: FL 70%+ 10분 연속 시 `[EarlyFLDamp]` 출력
3. STEP 0 pre-launch: 다른 창 최소화 후 Cybos 정상 로그인 확인
4. 만기일(3·6·9·12월 두 번째 목요일) `is_market_open` 15:20 마감 동작

---

## 2026-06-08 (121~123차 — Phase 2 버그 수정 + UI v8.0 + 대시보드 개선)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **Phase 2 백필** (`aggregate_and_backfill.py --weeks 10`) | **완료** ✅ | `scripts/aggregate_and_backfill.py` |
| **Phase 2 재학습** (버그 3건 수정 후 재실행) | **완료** ✅ | `learning/batch_retrainer.py` |
| **feature_names.pkl 무결성** | **복원 완료** ✅ 105 features | `model/horizons/feature_names.pkl` |
| **전 호라이즌 차원 일치** | **완료** ✅ 모두 105 | `model/horizons/gbm_*.pkl` |
| **30m 모델 성능 복원** | **완료** ✅ 0.4902→0.5864 | Phase 1 재학습으로 복원 |
| UI v8.0 표시 | **완료** ✅ | `dashboard/main_dashboard.py` |
| Phase 3 깜박임 배지 | **완료** ✅ | `dashboard/main_dashboard.py` |
| **Phase 2 bar_age 시각화** | **완료** ✅ | `dashboard/main_dashboard.py`, `main.py` |
| **lbl_futures_code 동적화** | **완료** ✅ | `dashboard/main_dashboard.py` |

### Phase 2 현재 운영 구조

```
백필: raw_features JOIN → 105+피처 저장 (raw_features_horizon 테이블)
학습: feature_names.pkl 105개 고정 (use_feat_names = _existing_feat_names)
추론: BAR_CACHE_DECAY 감쇠 → dashboard bar_ages 전달 → 카드 표시
```

### 대시보드 현황 (v8.0)

| 패널 | 표시 내용 | 이슈 |
|---|---|---|
| PredictionPanel 호라이즌 카드 | 방향↑/↓/횡보 + 확률% + `{age}m전` (stale시 주황) | ✅ v8.0 신규 |
| 상단 종목코드 | 근월물 동적 계산 (F202606 하드코딩 제거) | ✅ v8.0 신규 |
| Phase 3 배지 | 800ms 깜박임, 착수 조건 툴팁 | ✅ v8.0 신규 |

### 커밋

- `ad44efe` — 121차: Phase 2 백필/재학습 3종 버그 수정
- `e5d5474` — 122차: UI v7.0→v8.0 + Phase 3 깜박임 배지
- `123차 커밋 예정` — 대시보드 bar_age 시각화 + lbl_futures_code 동적화

### 다음 장에서 확인할 것

1. 기동 후 `[Phase2-STEP4]` 오류 없음 확인
2. 3m봉 완성 시 PredictionPanel 카드에 `"58.3% 2m전"` 표시 확인
3. 30m봉 16분 경과 시 카드 테두리 주황 dashed 확인
4. BAR_CACHE_DECAY: 30m봉 미완성 구간 confidence 점진 감소 확인
5. `validate_horizon_scaler_consistency()` 불일치 경보 없음 확인
   > 🔴 **[463차 후속, 2026-08-12 정정] 이 확인 항목은 무의미했다.** 경보가 없던 것은
   > 스케일러가 일관돼서가 아니라 **경보가 발생할 수 없어서**다 — 이 메서드는 호출자
   > 0건이고 `_scaler_meta` write도 0건이라 루프 본문이 절대 실행되지 않는다.
   > 상세·재개 조건은 `model/multi_horizon_model.py`의 해당 메서드 docstring 참조.

---

## 2026-06-07 (120차 — Phase 2 호라이즌별 완성봉 입력 구조 구현)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| `BarAggregator` 신규 — 1m봉→N분봉 집계 | **완료** ✅ | `features/bar_aggregator.py` |
| `feats_to_vec` / `build_for_horizon` 추가 | **완료** ✅ | `features/feature_builder.py` |
| DB 스키마 확장 — `raw_features_horizon`, `raw_candles_aggregated`, buy_vol/sell_vol | **완료** ✅ | `utils/db_utils.py` |
| `validate_horizon_scaler_consistency` / `predict_proba_multi` 추가 | ~~**완료** ✅~~ → 🔴 **정정(463차 후속)** | `model/multi_horizon_model.py` |
| `MIN_TRAIN_BARS_PER_HORIZON` + `_retrain_phase2` + `--phase2` 플래그 | **완료** ✅ | `learning/batch_retrainer.py`, `scripts/eod_retrain.py` |
| `main.py` STEP 4/5 Phase 2 로직 + `_hz_feat_cache` + `BAR_CACHE_DECAY` | **완료** ✅ | `main.py` |
| `scripts/aggregate_and_backfill.py` 신규 — 기존 72k봉 소급 적용 스크립트 | **완료** ✅ | `scripts/aggregate_and_backfill.py` |
| 테스트 6종 통과 확인 | **완료** ✅ | `scripts/_test_phase2.py` (삭제됨) |
| **백필 실행** (`aggregate_and_backfill.py --weeks 10`) | **완료** ✅ (2026-06-08, 버그 수정 후 재실행) | `scripts/aggregate_and_backfill.py` |
| **Phase 2 재학습** (`eod_retrain.py --phase2 --weeks 10`) | **완료** ✅ (2026-06-08, 버그 3건 수정 후) | `learning/batch_retrainer.py` |

### 구조 변경 요약

**Phase 1-1 → Phase 2 전환 핵심**:
- 이전: 모든 호라이즌이 동일한 1분봉 피처벡터 공유, halflife 감쇠만 적용
- 이후: 각 호라이즌 모델이 실제 N분봉 OHLCV에서 산출한 피처벡터를 독립적으로 수신

**주요 상수**:
```python
BAR_CACHE_DECAY = {3: 0.97, 5: 0.95, 10: 0.93, 15: 0.92, 30: 0.90}
MIN_TRAIN_BARS_PER_HORIZON = {"1m":15000,"3m":5000,"5m":3000,"10m":1500,"15m":1000,"30m":500}
```

**DB 신규 테이블**:
- `raw_features_horizon (ts, horizon, features)` — N분봉 완성 시 피처 JSON 저장
- `raw_candles_aggregated (ts, horizon, ...)` — 집계봉 캐시
- `raw_candles.buy_vol / sell_vol` — 미래 OFI/CVD tick 데이터용 예약 컬럼

### 커밋
- `b340c30` — 120차: Phase 2 호라이즌별 완성봉 입력 구조 구현 (9 files, +888/-54)

### 다음 장에서 확인할 것

1. `python scripts/aggregate_and_backfill.py --weeks 10` 실행 → raw_features_horizon 행 수 확인
2. `python scripts/eod_retrain.py --phase2 --weeks 10 --force` 실행 → 6/6 호라이즌 재학습 성공 확인
3. 기동 후 `[Phase2-STEP4]` 오류 없음 + STEP5 `_hz_feat_cache` 갱신 로그 확인
4. `validate_horizon_scaler_consistency()` 불일치 경보 없음 확인
5. Stage 2 준비: buy_vol/sell_vol 데이터 축적 (약 +30일 후 1m/3m OFI/CVD 재학습 가능)

---

## 2026-06-06 (119차 — FeatureBuilder 양방향성 버그 수정)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| `vwap_momentum` 항상 0 버그 수정 | **완료** ✅ | `features/feature_builder.py` |
| `ofi_imbalance` 방향 손실 수정 | **완료** ✅ | `features/technical/ofi.py` |
| `volume_acceleration` 클리핑 누락 수정 | **완료** ✅ | `features/feature_builder.py` |
| `queue_directional_depletion` 신규 피처 | **완료** ✅ | `features/technical/queue_dynamics.py`, `features/feature_builder.py` |
| GBM 재학습 (신규 피처 반영) | **미실시** — 다음 장 전 재학습 필요 | — |

### 수정 내역 요약

**1. vwap_momentum 항상 0 버그** (`feature_builder.py:519`)
- `features.get("vwap", 0.0)` → Phase 2-D에서 `features["vwap"]` 제거됐으나 참조 잔존
- `_vwap_history`에 0.0만 쌓여 `_vh[-5] > 0` 조건 미통과 → 항상 0.0
- 수정: `features.get("vwap_position", 0.0)` + `_vh[-1] - _vh[-5]` (5분 변화량)

**2. ofi_imbalance 방향 손실** (`ofi.py:125`)
- `abs(ofi_norm)` 사용 → 매수압 +2.0 = 매도압 -2.0 = 0.67 (방향 소멸)
- 수정: `np.clip(ofi_norm / 3.0, -1.0, 1.0)` — 부호 유지, 범위 [-1, 1]

**3. volume_acceleration 클리핑 없음** (`feature_builder.py:514`)
- 거래량 급등 시 최대 9.0+ → StandardScaler z-score 폭발
- 수정: `np.clip(..., -3.0, 3.0)` 추가

**4. queue_directional_depletion 신규 피처** (`queue_dynamics.py:91`)
- 기존 depletion_ratio/refill_ratio: bid+ask 합산 → 방향 없음
- 신규: `(depletion_ask - depletion_bid) / depletion_total` → [-1, 1]
- 양수 = 매도호가 고갈 우세(매수압), 음수 = 매수호가 고갈 우세(매도압)
- 빈 tick_stats 경로 기본값 0.0 처리 완료

### 다음 장에서 확인할 것

1. GBM 재학습 후 `queue_directional_depletion` 피처 DB 저장 확인
2. SHAP에서 `vwap_momentum` 비제로값 출현 (기존엔 항상 0)
3. `ofi_imbalance` 분포가 [-1, 1] 대칭으로 바뀌었는지 (기존엔 [0, 1])
4. shap_feature_registry에 `queue_directional_depletion` 수동 추가 필요

---

## 2026-06-05 (118차 — daily_close Qt 메인 스레드 블로킹 버그 수정)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **UI 먹통 버그 수정** — daily_close 백그라운드 스레드 분리 | **완료** ✅ | `main.py` |

### 버그 요약

**증상**: 미륵이 기동 후 ~38초 뒤 UI 완전 먹통. 마우스 호버 시점과 겹쳐 "마우스 호버가 원인"으로 오진.

**실제 원인**:
```
_scheduler (30초 QTimer, 메인 스레드)
  → _scheduler_tick() 첫 발동 (17:27:31, now≥15:40 조건 충족)
  → daily_close() 동기 호출
  → retrain_now(weeks_back=10) 동기 실행  ← Qt 이벤트 루프 완전 차단
  → UI 먹통 (타이머·마우스·페인트 이벤트 모두 불처리)
```

로그 마지막: `[FeatureBuilder] 전일 종가 버퍼 갱신 17:27:32` → 이후 완전 침묵.
python.exe 440MB 살아 있으나 Qt 이벤트 루프 정지.
"마우스 올리면 무한 루프"는 오진 — 기동 38초 후 자동 발생.

**수정** (`main.py` `_scheduler_tick`):
1. Qt 타이머(`_investor_timer`, `_option_chain_timer`) → 스레드 분기 전 메인 스레드에서 stop
2. `_daily_close_running` 플래그로 중복 진입 방지
3. `_daily_close_done = True` 즉시 선점
4. `daily_close()` 전체를 `DailyClose` 데몬 스레드로 실행
5. `_pre_market_done/stage1_done` 리셋은 스레드 finally에서 처리

### 다음 장에서 확인할 것

1. 기동 후 38초 뒤에도 UI 정상 응답 확인
2. `[Daily] 마감 통계` → `[FeatureBuilder] 전일 종가 버퍼 갱신` 로그 후 UI 미먹통
3. `[Retrain] 배치 재학습 시작` 로그가 백그라운드에서 출력되면 정상

---

## 2026-06-05 (117차 — 종료 흐름 구조 수정 + microprice 버그 방어)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **microprice debug log KeyError 방어** | **완료** ✅ | `features/feature_builder.py` |
| **STEP 3/EOD 재학습 직렬화** | **완료** ✅ | `main.py` |
| **116차 DB 배치화 효과 실측** | **미실시** — 다음 장 PipePerf 로그 확인 필요 | — |
| **EffectReports IndexError 116차 수정 확인** | **미실시** — 다음 장 WARN.log 확인 | — |

### 오늘 장 이상점 요약

| 시각 | 이상점 | 상태 |
|---|---|---|
| 13:47~13:54 | microprice KeyError ERR-FATAL 8회 | ✅ 수정 완료 |
| 15:29~15:50 | STEP 3/EOD 경합 → 15m/30m/RF EOD 미반영 | ✅ 직렬화로 근본 수정 |
| 12:43~14:30 | S2 5000ms+ / 13242ms 최대 | ⏳ 116차 배치화 효과 내일 확인 |
| 하루 종일 | EffectReports IndexError | ⏳ 116차 수정 효과 내일 확인 |

### STEP 3/EOD 직렬화 구현 요약

**구조**: `threading.Event` 기반

```
재학습 시작 4곳: _gbm_retrain_done_event.clear()
완료 콜백(_on_gbm_retrain_done): _gbm_retrain_done_event.set()
daily_close() 진입 시:
  _gbm_retrain_running == True
    → Event.wait(timeout=40분)
    → 완료 후 EOD retrain_now() 동기 실행
```

**효과**: STEP 3 완료 → EOD 재학습 → P8 스케일러 → 종료 순서 보장.
전 호라이즌 pkl이 EOD 기준 단일 세션 결과로 완성됨.

### EarlyWarmup/PreRetrain 흐름 정리

```
08:45 가동
  → _warmup_retrain_pending = True (장외이므로 즉시 재학습 안 함)
  → EarlyWarmup: canary_stale_age > 4h → refit_scalers_only (daemon)

08:55 pre_market_setup()
  → Canary 체크: EarlyWarmup 완료 시 age 짧음 → stale=False → 90초 대기 없음
  → ScalerWarmup: daemon thread (EarlyWarmup과 독립)
  → PreRetrain: _warmup_retrain_pending=True → retrain_now(force=True) daemon

결론: EarlyWarmup = Canary 통과 + 08:55 대기 시간 단축이 목적
      PreRetrain = GBM 전체 재학습 (재시동 후만)
      EarlyWarmup → ScalerWarmup + PreRetrain 병렬 시작
```

### 다음 장에서 확인할 것

1. `[DailyClose] STEP 3 재학습 진행 중 — EOD 재학습 전 완료 대기` 로그 발동 여부
2. 전 호라이즌 pkl 수정 시각이 15:40 이후 동일 세션으로 완성되는지
3. `[P8] EOD 스케일러 재적합 완료` + `session_state["p8_last_success_date"]` 기록
4. `[PipePerf] total=Xms` 2500ms 이하 (116차 배치화 효과)
5. `[EffectReports] run failed` 재발 없음 (116차 IndexError 수정 효과)

---

## 2026-06-05 (116차 — subprocess/DB 병목 수정 + 로그 레벨 정비)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **EffectReports subprocess IndexError** | **완료** ✅ | `main.py` `_run_effect_report_script` |
| **ConstOut 스팸 억제** | **완료** ✅ | `scripts/run_microstructure_ab_backtest.py` |
| **DB 연결 배치화 (파이프라인 병목)** | **완료** ✅ | `prediction_buffer.py`, `db_utils.py`, `main.py` |
| **BrokerSync 로그 레벨 조정** | **완료** ✅ | `main.py`, `dashboard/main_dashboard.py` |
| **파이프라인 시간 실측 검증** | **미실시** — 다음 장 PipePerf 로그 확인 필요 | — |

### DB 배치화 요약

| 단계 | 이전 연결 수 | 이후 연결 수 | 예상 개선 |
|---|---|---|---|
| STEP 1 `verify_and_update` | 24회 (~6250ms) | 2회 | → ~520ms |
| STEP 4 `save_candle_and_features` | 2회 (~700ms) | 1회 | → ~260ms |
| STEP 9 `save_step9_batch` | 7회 (~1753ms) | 1회 | → ~260ms |
| **합계** | **13242ms** | **~2500ms** | CB 5초 기준 이하 |

### BrokerSync 로그 기준

- `before=FLAT + rows=0` → DEBUG/INFO (모의투자 정상 무포지션 응답)
- `before!=FLAT + rows=0` → WARNING 유지 (실전 포지션 중 공란 = 이상 상황)

---

## 2026-06-05 (115차 — Extreme 피처 절대값→상대값 정규화 전면 구현)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **Phase 1: SCALER_CLIP_FEATURES 확장** | **완료** ✅ | `config/settings.py` |
| **Phase 2-A/B: macro_vix_abs, feature_recoverable_errors 제거** | **완료** ✅ | `macro_feature_transformer.py`, `feature_builder.py`, `registry.json` |
| **Phase 4: Gap Offset 구현** | **완료** ✅ | `model/multi_horizon_model.py`, `main.py` |
| **Phase 2-C/D: microprice/vwap 절대값 제거** | **완료** ✅ | `feature_builder.py`, `registry.json` |
| **Phase 3-A: cvd/cvd_slope 일중 정규화** | **완료** ✅ | `features/technical/cvd.py`, `feature_builder.py` |
| **Phase 3-B: queue 비율화** | **완료** ✅ | `features/technical/queue_dynamics.py`, `feature_builder.py` |
| **GBM 재훈련** | **완료** ✅ 16,406행×105피처 6/6 성공 | — |
| **Phase 2-E: *_age_sec 제거** | **보류** — 1주일 clip 안정 확인 후 | — |
| **Phase 3-C: B축 수급 OI 비율화** | **보류** — 설계 검토 필요 | — |

### 주의 사항

- **feat=118(ScalerWarmup) vs feat=105(GBM) 불일치**: 오늘 DB 잔존 이전 피처 데이터 때문. 내일~모레 자연 해소 예정. D_FORCE refit 발생 시 scaler 왜곡 가능.
- **cvd/queue DB 혼재**: 과거 DB 절대값 + 오늘 이후 정규화값. 2~3일 후 완전 교체.
- **재훈련 30분 소요**: 장 중 강제 재훈련은 CB⑤ 위험. EOD(15:40) 자동 재훈련 권장.
- **weeks_back=10 반영됨**: `main.py daily_close`, `batch_retrainer` 기본값 모두 10으로 변경.

### 구현 계획서 / 스크립트

- `docs/260605_FEATURE_NORMALIZATION_PLAN.md` — 피처 분류, 구현 계획, 재훈련 방법
- `scripts/eod_retrain.py` — 장 마감 후 독립 실행 EOD 재학습 스크립트
- `EOD_RETRAIN.bat` — 더블클릭 실행 배치 파일

---

## 2026-06-05 (114차 — 재학습 피처셋 불일치 사고 분석 + P0~P4 개선)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **P0: registry 수동 복구** (87→105개) | **완료** ✅ feat=105 복귀 확인 | `data/db/shap_feature_registry.json` |
| **P1: ScalerWarmup managed_feats 필터 제거** | **완료** | `learning/batch_retrainer.py:436` |
| **P2: 재학습 실패 시 registry 롤백** | **완료** | `main.py` |
| **P3: 시작 시 registry ↔ pkl 정합성 경고** | **완료** | `model/multi_horizon_model.py` |
| **P4: weeks_back 8→10** | **완료** | `learning/batch_retrainer.py`, `main.py` 3곳 |
| **다음 재학습 정상 여부 확인** | **미실시** — 다음 기동 시 | — |

### 사고 원인 계층 (12:19:53~13:03)

| 레이어 | 원인 |
|---|---|
| L1 | `load_features_for_warmup`이 registry.active_features(87개)로 raw feat 필터 |
| L2 | `refit_scalers_only`에서 85→105 0-패딩 → scaler 왜곡 |
| L3 | `_on_reset_feature_set_requested`가 active_features 먼저 저장, 재학습 실패 시 롤백 없음 |
| L4 | `weeks_back=8` 실측 12,605봉 < MIN_TRAIN_BARS 15,000 → 재학습 구조적 실패 |

### 다음에 확인할 것

1. 다음 기동 시 `[Model] 시작 시 정합성 오류` 로그 없음 확인 (P3)
2. 다음 재학습 시 `[Retrain] 배치 재학습 시작 (weeks_back=10)` + 피처 15,000+ 확인 (P4)
3. reset to baseline 후 재학습 실패 시 `[FeatureOps] 재학습 실패 — active_features 롤백 N개 복원` WARN 로그 (P2)

---

## 2026-06-05 (113차 — FL 편향 고착 4종 구조 개선)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **P1: 10m/15m class_weight 명시 설정** | **완료** | `learning/batch_retrainer.py` |
| **P2: FL 편향 고착 → uniform fallback** | **완료** | `main.py` (init+bias block+STEP5+reset) |
| **P3: CB③ 해제 마진 0.05→0.03** | **완료** | `config/settings.py` |
| **P5: 15m FL 편향 독립 CB 이벤트** | **완료** | `safety/circuit_breaker.py`, `main.py` |
| **구문 검증** | **완료** ✅ | 4개 파일 ast.parse |
| **실세션 효과 검증** | **미실시** — 다음 장 로그 확인 필요 | — |

### 오늘 장 이상점 요약 (2026-06-05 실세션)

| 시간 | 이상점 | 원인 |
|---|---|---|
| 09:00~10:18 | 10m/15m FL 100% 고착 | `balanced` class_weight → FL 억압 불가 |
| 09:11~09:12 | 처리 18s/45s 지연 | EKS 발동 후 스케일러 재적합 파이프라인 경합 |
| 10:18 | CB③ HALTED (30m 정확도 0%) | 30m UP 편향 + 급락장 완전 미스 |
| 10:30 | 세션 최저점 반전 완전 미스 | CB=HALTED + 전 호라이즌 FL 예측 |
| 10:18~ | CB③ 33~50% 진동 → 해제 불가 | 해제 마진 5%p 과대 (33% 경계 진동) |
| 세션 전체 | MaskedFallback 미발동 | z-score 4.0 조건 미충족 (모델 내부 구조 문제) |

### 구현 내용 요약

**P1** `learning/batch_retrainer.py`:
- `_CW_10M = {FL:0.80, UP:1.10, DN:1.10}` 신규
- `_CW_15M = {FL:0.75, UP:1.15, DN:1.15}` 신규
- `_make_sample_weight()` 10m/15m 명시 분기 추가 (balanced 제거)

**P2** `main.py`:
- `__init__`: `_bias_fl_streak`, `_bias_override_horizons` 추가
- bias 감지 블록: FL 90%+ 20분 지속 → `_bias_override_horizons` 등록 + `[BiasReset]` 로그
- STEP 5: override 호라이즌 → `{1/3,1/3,1/3}` 치환
- `reset_daily()`: 두 변수 일간 리셋

**P3** `config/settings.py`:
- `CB_CB3_WARN_RESET_MARGIN = 0.05 → 0.03`

**P5** `safety/circuit_breaker.py`:
- `_horizon_fl_bias_streak`, `_horizon_fl_bias_warned` 추가
- `record_horizon_fl_bias(horizon, fl_ratio, streak)` 신규: 30분 지속 시 CRITICAL + Slack
- `reset_daily()` 리셋

### 다음 장에서 확인할 것

1. `[BiasReset] 10m FL편향 XX% 20분 지속 → uniform fallback 적용` 로그 발동 여부
2. `[BiasReset] 15m FL편향 XX% 20분 지속 → uniform fallback 적용` 로그 발동 여부
3. `[CB-FLBias] 15m FL편향 XX% 30분 고착` Slack 경보 수신 여부
4. GBM 재학습 후 10m/15m FL 편향 감소 여부 (`[Bias]` 로그에서 FL 비율 확인)
5. CB③ 해제 마진 완화 효과: 31~33% 구간에서 경고 카운터 리셋 발생 여부

---

## 2026-06-05 (112차 — 신규 버그 3종 수정)

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **P1: EarlyWarmup 임계값 24h→4h** | **완료** | config/settings.py, main.py |
| **P2: CB③ 최솟 샘플 수 25→30 + n= 로그** | **완료** | config/settings.py, safety/circuit_breaker.py |
| **P6: Contrarian CLEARED streak 리셋** | **완료** | safety/contrarian_mode.py |
| **실세션 효과 검증** | **미실시** — 다음 장 로그 확인 필요 | — |

### 오늘 장 로그 요약 (2026-06-05)

- scaler_age=17h → EarlyWarmup 24h 조건 미발동 → EKS 발동 → 파이프라인 지연 → acc30m 붕괴 → CB③ 당일 정지
- 실거래 없음(모의투자 + ShadowSession BLOCKED + CB③ 정지)
- 안전장치 전반 정상 작동 확인 ✅

### 다음 장에서 확인할 것

1. [EarlyWarmup] 로그 — 08:45에 발동 여부 (4h 조건)
2. [CB③] 로그 — 샘플 수 
= 표시 확인
3. Contrarian ACTIVE 후 CLEARED → 즉시 재발동 없는지 확인

## 2026-06-04 (111? ?? ???) ? ??? ??? ?? ???? ?? ?? + ???? ?? ??

### ?? ??

| ?? | ?? | ?? |
|---|---|---|
| **??? ??? ?? 1? ???** | **??** | `dashboard/panels/dynamic_mc_panel.py` |
| **?? conf ? ???? ?? 9? ??** | **??** | `dashboard/panels/dynamic_mc_panel.py` |
| **8?? ?? + ?? ?? + ??** | **??** | `dashboard/panels/dynamic_mc_panel.py` |
| **?? ??? ??? ?? ??? ?? ??** | **??** | `dashboard/panels/dynamic_mc_panel.py` |
| **???? ?? ?? (trades.db + TRADE.log fallback)** | **??** | `dashboard/panels/dynamic_mc_panel.py` |
| **?? ??** | **??** | `python -m py_compile dashboard\panels\dynamic_mc_panel.py` |
| **???? ???? ?? ??** | **???** | ?? ?? ??? ?? |

### ?? ?? ??

- `?? ???`? `conf >= mc` ??? 1? ??? ?????.
- `?? conf ? ???? ??`? ?? ??? ??? ??? ???? `1~8??`? ?? ????.
- `8. ????`? ?? ???? ???? ????, ??? `trades.db`? ?? `TRADE.log` fallback ??.
- ?? ??? `YYYY-MM-DD HH:MM` ???? `?2?` ?? ???? ??? ???.

### ?? ??? ??

- 2026-06-04 `ensemble_decisions`: 387?
- 2026-06-04 `trades.db` ??: 0?
- 2026-06-04 `TRADE.log` ????/???? ??: 0?
- ??? ?? ???? `8. ????`? ??? ?? ??? **?? ?? ?? ??**

### ?? ???? ?? ? ?

1. ?? ??? ??? ? `8. ????` ?? ????? ??? ??
2. `TRADE.log` ?? ??? ?? ?? ????? ????? ???? ?? ??
3. ?? ? `trades.db` ?? ?? ??? ??? ?? ?? ?? ?? ?? ??

---

## 2026-06-04 (110차 세션 마무리) — 진입0 로그 분석 + 개선 6종 전면 구현

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **① opt_pcr_slope_norm SCALER_CLIP_FEATURES 추가** | **완료** | `config/settings.py` |
| **② EKS P3 해제 임계값 0.50 → max(mc, 0.42)** | **완료** | `safety/system_health.py`, `main.py` |
| **③ CoherenceGate GAP_OPEN/TrendGate 차등 0.60→0.50** | **완료** | `model/ensemble_decision.py` |
| **④ FLAT 연속 시 ShortHorizonOverride (1m/3m+OFI/CVD)** | **완료** | `model/ensemble_decision.py` |
| **⑤ Platt 보정기 디스크 영속화 (save/load)** | **완료** | `learning/calibration.py`, `main.py`, `config/settings.py` |
| **⑥ opt_pcr_* D_FORCE 연동 30분 0.3× 감쇠** | **완료** | `model/multi_horizon_model.py` |
| **구문 검증** | **완료** ✅ | 5개 파일 `ast.parse` |
| **실세션 효과 검증** | **미실시** — 다음 장 로그 확인 필요 | — |

### 오늘 진입0 원인 분석 요약 (로그 기반)

| 레벨 | 원인 | 내용 |
|---|---|---|
| L1 | EKS 09:05 발동 | conf_max=40.2%, core_pass=0/5봉 → 오전 전체 차단 |
| L1 | conf 만성 미달 | 평균 39.7% vs mc 43.0~43.9% (갭 -3.3%p) |
| L1 | conf↑=dir=FLAT | 12:45~13:15 conf 43~45% 달성했으나 전부 dir=+0 |
| L2 | opt_pcr_slope_norm 반복 이상값 | z=+9.21까지 폭발, D_FORCE 후에도 재발, OFI와 충돌 |
| L2 | CoherenceGate 과잉 차단 | 합의도 0.25~0.50 (임계값 0.60 미달) |
| L3 | 캘리브레이션 불량 | ECE=0.250, conf=45%에서 실제 acc=36% |

### 다음 장에서 확인할 것

1. `[PCR-Dampen]` 로그 — opt_pcr D_FORCE 후 30분 감쇠 발동 여부
2. `[ShortHorizonOverride]` 로그 — FLAT 5봉+ 연속 시 1m/3m 방향 채택 여부
3. `[SHS-EKS] EKS 자동 해제 ... (임계=43.0%)` — P3 완화 조건으로 해제 여부
4. `[CoherenceGate 차단 ... zone=GAP_OPEN min=0.50]` — 차등 임계값 적용 확인
5. `[Calibration] 앙상블 보정기 복원 완료` — 기동 시 pkl 복원 확인

---

## 2026-06-04 (109차 세션 마무리) — 진입 미발생 분석 + 방향성 감지 개선 2종

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **[안 1] MaskedFallback — 이상값 피처 격리 예측** | **완료** | `model/multi_horizon_model.py`, `main.py` |
| **[안 2] PriceStructureBoost — 가격 구조 TrendGate 부스트** | **완료** | `strategy/entry/trend_persistence.py`, `main.py` |
| **ScalerMonitorPanel D_FORCE 툴팁** | **완료** | `dashboard/panels/scaler_monitor_panel.py` |
| **구문 검증** | **완료** ✅ | `python -c "ast.parse(...)"` 3개 파일 |
| **실세션 효과 검증** | **미실시** — 다음 장 로그 확인 필요 | — |

### 안 1 — MaskedFallback 동작 요약

- 발동 조건: 동일 피처 `|z|>4` 연속 **5분** 이상 (streak ≥ 5) + 이번에도 극단
- 동작: 해당 피처를 0으로 치환 후 GBM만 재호출 → SGD 블렌딩 → `ensemble.compute`
- 채택 조건: 정상 dir=FLAT + masked_conf − raw_conf **≥ 5%p**
- 로그 키워드: `[MaskedFallback]`

### 안 2 — PriceStructureBoost 동작 요약

- 발동 조건: HH-HL (또는 LH-LL) **5봉** 연속 + streak ≥ 5 + OFI/CVD 동의
- 동작: `min_conf_override` 0.44 → **0.38** 추가 완화
- `_price_struct_buf = deque(maxlen=8)` 매분 bar high/low 적재
- 로그 키워드: `[TrendGate] ... [가격구조부스트]`, `[TrendGate] 가격구조 부스트 ON`

### 다음 장에서 확인할 것

1. opt_pcr_slope_norm 극단 상황에서 `[MaskedFallback]` 로그 발동 여부
2. 상승 추세 구간에서 `가격구조 부스트 ON` + `min_conf 0.44→0.38` 로그 발동 여부
3. 부스트 후에도 conf가 0.38 미달인 경우 — 0.38보다 더 낮춰야 할지 검토
4. MaskedFallback이 잘못 채택되는 케이스(격리 피처가 실제 유효 신호였던 경우) 모니터링

---

## 2026-06-04 (108차 세션 마무리) — CB⑤ 경고 지속 완화 4종 적용

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **EffectReports 파이프라인 분리** | **완료** — 전용 타이머/워커로 이동 | `main.py` |
| **HealthPolicy soft degraded weighting** | **완료** — CB⑤ 1000~1300ms 경고는 낮은 가중치 집계 | `main.py` |
| **ProgramTrade probe 반복 실패 루프 중단** | **완료** — 운영 투자자 타이머에서 비활성 | `main.py`, `collection/cybos/investor_data.py` |
| **ConstOut 3분 heavy cooldown** | **완료** — 추가 refit/report/heavy panel refresh 유예 | `main.py` |
| **문법 검증** | **완료** ✅ | `python -m py_compile main.py collection\cybos\investor_data.py` |
| **장중 실운영 검증** | **미실시** — 다음 장에서 로그 확인 필요 | — |

### 운영 해석

- CB⑤ 반복의 주원인이던 EffectReports 동기 호출은 메인 minute pipeline 밖으로 이동했다.
- HealthPolicy는 이제 경계값 수준의 성능 warning을 full degraded signal로 동일 취급하지 않는다.
- ProgramTrade는 공식 해결 전까지 운영 timer에서 빼고, 수동 probe 스크립트로만 점검하는 상태다.
- ConstOut가 뜬 직후 3분은 무거운 후속 작업을 일부러 늦춰 부하 중첩을 피한다.

### 다음 장에서 확인할 것

1. WARN.log에서 `CB⑤` total/warn_streak/degraded 진입 빈도 감소 여부
2. `EffectReports` 로그가 worker에서만 찍히고 파이프라인 지연과 분리되는지
3. ProgramTrade 관련 `dispatch failed (-2147221005)` 반복 로그가 사라졌는지
4. ConstOut 직후 `heavy cooldown active` 계열 skip 로그가 정상적으로 찍히는지

---

## 2026-06-04 (107차 세션 마무리) — 재시동 후 전수 확인 + EffectReports 분석

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **[버그] CybosApiConnector NameError 수정** | **완료·검증됨** ✅ | `collection/cybos/api_connector.py:921-922` |
| **[성능] S2 파이프라인 지연 개선** | **완료·검증됨** ✅ | `learning/meta_confidence.py`, `main.py` |
| **투자자 수급** — 10:53:33~ `source=CpSyrNew7221 supported=True` | **검증됨** ✅ | DATA.log |
| **S2 속도** — 재시동 후 PipePerf WARN 0건 (≤1000ms) | **검증됨** ✅ | WARN.log |
| **OptionChain stale 복구** — 10:18 감지→refresh, 이후 매 10분 갱신 | **검증됨** ✅ | SYSTEM.log |
| **EffectReports 에러 진단 로그 추가** — traceback.format_exc() 추가 | **완료** | `main.py:4769` |
| **EffectReports list index 에러 근본 원인** | **미특정** — 다음 장 중 traceback 확인 필요 | — |

### 실세션 점검 결과 (10:53:33 재시동 기준)

| 항목 | 결과 |
|---|---|
| 투자자 수급 | ✅ 10:53:33~ supported=True, source=7221 |
| S2 속도 | ✅ 재시동 후 PipePerf WARN 0건 (전: 3.7~7s/분) |
| DivergencePanel | ✅ 매분 div=+XXX, futures(fi/rt/inst) 정상 |
| OptionChain stale 복구 | ✅ 10:18 감지→refresh, 이후 정상 갱신 |
| EffectReports | ⚠️ list index out of range — 직접 실행 성공, 메인 파이프라인 영향 없음 |
| ProgramTrade probe | ⚠️ -2147221005 실패 (known, 프로그램매매 TR 미연결) |
| 진입 발생 | ❌ conf 33~42% < mc 43.9%, grade=X (장 중 확인 범위 밖) |

### EffectReports 에러 현황

- `generate_rollout_readiness_report.py`, `run_microstructure_ab_backtest.py` — 장 중 15분 주기 실패
- 두 스크립트 직접 실행 시 **성공** → 스크립트 코드 자체는 정상
- main.py subprocess.run() 호출 시에만 `IndexError: list index out of range` 발생 (원인 미특정)
- **조치**: main.py:4769 except 블록에 `traceback.format_exc()` + `rc!=0` 브랜치에 stdout 추가
- 메인 파이프라인 무영향. 리포트만 생성 안 되는 것.

---

## 2026-06-04 (106차) — 다이버전스 패널 투자자 수급 + 옵션 체인 미수집 수정

### 배경

UI 다이버전스 패널에서 외인/개인/기관 선물 순매수가 전부 "대기" + 옵션 체인이 "미수집" 상태.
로그 분석 + 대신증권 자료실 직접 조회로 근본 원인 2종 확인.

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **투자자 수급 TR 오사용 수정** — 7212 → 7221, 파싱 로직 전면 재작성 | **완료** | `collection/cybos/api_connector.py` |
| **probe 진단 로그 강화** — system_logger, raw 덤프, 범위 확장 | **완료** | `collection/cybos/api_connector.py` |
| **옵션 체인 ATM miss → 자동 재로드** | **완료** | `collection/options/option_chain_snapshot.py` |
| **옵션 체인 장 시작 즉시 폴링** | **완료** | `strategy/runtime/broker_runtime_service.py` |
| **옵션 체인 로그 SYSTEM으로 전환** | **완료** | `collection/options/option_chain_snapshot.py` |
| **stale 캐시 삭제** | **완료** | `data/option_chain.json` (삭제됨) |
| 다음 기동 시 실세션 확인 | **미완료** | — |

### 수정 내용

**투자자 수급 TR (api_connector.py)**:
- 기존: `CpSysDib.CpSvrNew7212` (존재하지 않는 TR명) + `(0, 1)` 입력
- 수정: `CpSysDib.CpSvrNew7221` (대신증권 자료실 seq=85 확인) + `(0, ord('1'))` 입력
- 파싱 구조 변경: "행=투자자명" → "행=상품종류(ri), 열=투자자(fi)"
  - ri=2(선물): fi=2(개인순), fi=5(외인순), fi=8(기관순)
  - ri=3(옵션콜), ri=4(옵션풋)도 동일 열 구조로 콜/풋 넷 수집

**옵션 체인 (option_chain_snapshot.py)**:
- 원인: 2026-05-13 캐시 max strike=1340 < 현재 spot=1385 → ATM 필터 0개
- ATM 필터 miss → 즉시 `CpUtil.CpOptionCode` 재로드 + 재필터 (자동 복구)
- valid snapshots=0 → `_chain_raw=[]` 초기화 (다음 poll 강제 재로드)
- initialize/refresh 로그를 `system_logger` 전환 → SYSTEM.log 가시화

**broker_runtime_service.py**:
- 옵션 체인 타이머 시작 즉시 `_poll_option_chain()` 1회 호출 추가 (기존: 300초 후 첫 호출)

### 다음 기동 시 확인

1. `[CybosProbe] CpSysDib.CpSvrNew7221 ok` + `[CybosProbe][RAW]` 덤프 (SYSTEM.log)
2. `[CybosInvestor] futures supported=True source=CpSysDib.CpSvrNew7221 foreign=±XXX` (DATA.log)
3. `[OptionChain] 갱신 ... avail=True` (SYSTEM.log, 09:00 직후)
4. 패널 UI: 외인/개인/기관 수치 + 옵션 체인 "경신: HH:MM" 표시

---

## 2026-06-04 (105차) — EKS 노후화 A+B+C 추가 개선

### 배경

P1~P4로 EKS 발동 후 대응은 완성됐으나, 스케일러 노후화 원인이 전날 P8 실패뿐 아니라
**휴장일 / 프로그램 중간 멈춤 / 주말 갭** 등 P8이 아예 실행 안 된 케이스를 포함하므로 추가 보완.

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **A안** 08:45 얼리버드 warmup — scaler age > 24h 시 pre_market_setup 이전 선행 갱신 | **완료** | `main.py` |
| **B안** P8 실패 30초 후 즉시 재시도 1회 + 재시도 실패 시 슬랙 알림 | **완료** | `main.py` |
| **C1** P8 성공 시 `session_state["p8_last_success_date"]` 기록 | **완료** | `main.py` |
| **C2** EKS 발동 시 원인 추론 → `system_health._eks_reason` 저장 | **완료** | `safety/system_health.py`, `main.py` |
| **C3** SHS 배지 "⛔ 관망일" 아래 원인 2줄 표시 | **완료** | `dashboard/main_dashboard.py` |
| 다음 기동 시 실세션 확인 | **미완료** | — |

### 수정 내용

**A안** (`main.py` `_scheduler_tick()`):
- 08:45~08:55 구간 heartbeat에서 `canary_stale_age_hours() > 24h` 감지
- 감지 시 daemon thread로 warmup 즉시 시작 (`_early_warmup_started` 플래그로 1회 보장)
- 08:55 canary 체크 시점엔 이미 완료 → P2 90초 대기 사실상 0초
- 커버 범위: 전날 P8 실패·휴장일·중간 멈춤·주말 갭 등 원인 무관

**B안** (`main.py` daily_close P8 블록):
- `for _p8_try in range(2)` 루프: 최초 1회 + 30초 후 재시도 1회
- 재시도 성공 시 `[P8] 재시도 성공` 로그
- 재시도까지 실패 시 슬랙 알림 (`"내일 08:45 EarlyWarmup이 보완"` 안내 포함)
- 데이터 없음 케이스는 재시도 없이 즉시 break

**C1** (`main.py` P8 성공 블록):
- P8 재적합 성공 시 `session_state["p8_last_success_date"] = today` 기록
- EKS 원인 추론 시 전날 P8 성공 여부 판별에 사용

**C2** (`safety/system_health.py` + `main.py`):
- `SystemHealthScore._eks_reason: str` 필드 추가 (`__init__` + `reset_daily()`)
- EKS 발동 직후 `session_state["p8_last_success_date"]` vs 전날 비교:
  - 전날 P8 기록 없음 + 월요일 → `"주말갭(Nh)"`
  - 전날 P8 기록 없음 + 그 외 → `"휴장/중단갭(Nh)"`
  - 전날 P8 있었는데 노후 → `"스케일러Nh노후"`
  - scaler age < 24h → `"confN%미달"`
- `[SHS-EKS] 원인: ...` WARN 로그 + `_eks_reason` 저장
- `update_shs_badge()` 호출부에 `eks_reason=` 파라미터 추가

**C3** (`dashboard/main_dashboard.py`):
- `update_shs_badge(shs, entry_blocked, kill_switch, eks_reason="")` 시그니처 변경
- kill_switch=True 시 `eks_reason` 있으면 `"⛔ 관망일\n{eks_reason}"` 2줄 표시
- `setWordWrap(True)` + `setAlignment(Qt.AlignCenter)` 적용

### 다음 기동 시 실세션 확인

1. **A안**: 08:45~08:55 구간 `[EarlyWarmup] scaler 노후=Xh → 08:45 선행 warmup 시작` 로그 (노후 시만)
2. **A안**: 이후 `[EarlyWarmup] 완료 n=N봉` 로그 확인 → 08:55 Canary 체크에서 age < 1h 확인
3. **B안**: P8 실패 시 `[P8] EOD 재적합 실패 — 30초 후 재시도` → `완료 [재시도 성공]` 로그
4. **C1**: P8 성공 후 `data/session_state.json`에 `"p8_last_success_date": "YYYY-MM-DD"` 기록 확인
5. **C2+C3**: EKS 발동 시 배지에 `"⛔ 관망일\n스케일러41h노후"` (또는 `주말갭`/`conf40%미달`) 표시

---

## 2026-06-04 (104차) — Canary/EKS 구조 개선 P1~P4

### 배경

08:55 Canary 노후=41h 경고 + 09:05 EKS 발동(conf_max=40.2%)으로 당일 관망.
원인: 전날 P8 EOD 재적합 실패(무음) + warmup 비동기 완료 미보장 + EKS 회복 불가 구조.

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **P1** P8 EOD 실패 → 슬랙 알림 추가 | **완료** | `main.py` |
| **P2** Canary stale 시 warmup 완료 이벤트 대기 (최대 90초) | **완료** | `main.py` |
| **P3** EKS 발동 후 09:20+ 회복 창 — `try_eks_recovery()` | **완료** | `safety/system_health.py`, `main.py` |
| **P4** EKS core_pass AND → CORE 2/3 다수결 완화 | **완료** | `main.py` |
| 다음 기동 시 실세션 확인 | **미완료** | — |

### 수정 내용

**P1** (`main.py` P8 except 블록):
- 기존 "무해" logger.warning → 실패 시 슬랙 알림 추가
- 전날 P8 실패를 당일 08:55 전에 인지 가능

**P2** (`main.py` pre_market_setup):
- `_canary_stale` 초기값을 try 블록 밖에서 선언
- warmup worker에 `threading.Event` + `finally: _evt.set()` 추가
- GBM 재학습 중 스킵 시 `_warmup_done_event.set()` 즉시 처리
- `_canary_stale=True` 시 최대 90초 동기 대기 (08:55~09:00 여유 활용)

**P3** (`safety/system_health.py` + `main.py`):
- `_eks_recovery_checked` 플래그 추가 (`__init__` + `reset_daily()`)
- `try_eks_recovery(scaler_age_hours, recent_conf)` 메서드 신규
  - 조건: scaler_age < 1h AND conf >= 50% → `_eks_active = False`
  - 1회 시도 후 `_eks_recovery_checked = True` 잠금
- main.py STEP 7: ts >= 09:20 + `_eks_recovery_checked=False` 시 1회 호출

**P4** (`main.py` GAP_OPEN 블록):
- 기존: `VWAP AND CVD AND OFI` (3개 전부 통과)
- 변경: `_core_votes >= 2` (3개 중 2개 이상 통과)
- 이유: GAP_OPEN 거래량 부족으로 CORE 1개 실패가 잦아 EKS 과발동 유발

### 다음 기동 시 실세션 확인

1. **P1**: 다음날 P8 실패 시 슬랙 `⚠️ P8 EOD 스케일러 재적합 실패` 수신 확인
2. **P2**: Canary stale 경고 후 `[Canary] stale 감지 — warmup 완료 대기 시작 (최대 90초)` 로그 확인, 이후 `[Canary] warmup 완료 대기 종료 — GAP_OPEN 진입` 확인
3. **P3**: EKS 발동 후 09:20 이후 `[SHS-EKS] EKS 자동 해제 확정` 또는 `EKS 유지 — 회복 조건 미충족` 로그 확인
4. **P4**: GAP_OPEN 구간에서 CORE 2개 이상 통과 시 `core_pass` 카운트 증가 → EKS 발동 억제 확인

---

## 2026-06-03 (103차) — 중복 피처 구조 개선 2종

### 배경

방향모델(GBM+SGD+RF+EnsembleGater)과 진입모델(Checklist+MetaGate+ExecutionGovernor+ToxicityGate) 사이의 중복 데이터 사용 3종 분석. 우선순위 1·2 수정 완료.

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **[103-P1] Microstructure 중복 해소** — MetaGate에서 mlofi_norm/cancel_add_ratio 제거 | **완료** | `learning/meta_confidence.py`, `strategy/entry/meta_gate.py` |
| **[103-P2] Toxicity 중복 해소** — ExecutionGovernor toxicity 항 제거, 가중 재분배 | **완료** | `strategy/runtime/execution_governor.py`, `main.py` |
| 다음 기동 시 실세션 확인 | **미완료** | — |

### 수정 내용

**[103-P1] MetaGate 피처 분리:**
- `meta_gate.py`: `lob_imbalance(mlofi_norm)`, `vpin_proxy(cancel_add_ratio)` 계산·전달 제거
- `meta_confidence.py`: 피처 벡터 9→7, len 검사 업데이트, `_rule_based_confidence` vpin 조건 삭제

**[103-P2] ExecutionGovernor 가중치:**
- 구: `conf×0.35 + quality×0.30 + latency×0.20 + toxicity_pass×0.15`
- 신: `conf×0.40 + quality×0.35 + latency×0.25` (toxicity는 ToxicityGate 전담)

### 다음 기동 시 실세션 확인

1. **[103-P1]** `[MetaGate] action=reduce` 빈도 증가 확인 (mlofi_norm 불리 구간의 skip→reduce 전환)
2. **[103-P1]** MetaConfidenceLearner: 기동 후 `source=규칙기반`으로 시작 → 50샘플 후 `source=SGD` 전환
3. **[103-P2]** `[ToxicityGate] action=reduce score=0.XX size_mult=0.50` 단독 로그 (ExecGov와 중복 없음)
4. **[103-P2]** `[ExecutionGovernor]` reduce/block 사유가 latency/quality 기반인지 확인

---

## 2026-06-02 (102차) — 진입0 원인 분석 + 안전장치 P0~P8 구현

### 배경

금일 장중 진입 0건 원인을 로그 3중 분석(SIGNAL/SYSTEM/WARN) 후 구조적 개선 8종 구현.

**확인된 충격 타임라인**:
- 09:01~09:14: ERR-FATAL 14회 (105 vs 106 피처 불일치) → 파이프라인 완전 불능
- 09:16: SHS=42, IntradayRegime CRASH, z_warn=34 → L2 +12%p
- 09:31: 파이프라인 16,616ms → CB PAUSED
- 09:50: ShadowSession BLOCKED (acc30m=30.0%)
- 11:51: CB③ 당일 정지 (acc30m=26.9% < 28%)
- grade 분포: A=0, B=0, C=5, X=364 → 자동진입 조건 하루 전혀 미충족

**2차 원인 (구조적)**:
- CRASH +12%p → actual_min_conf → Checklist에 그대로 전달 → grade=C 강제 X
- 동적 mc 급등(64%→72%) → conf 46%와 격차 과대
- 스케일러 age 641분 → 09:00 극단 z-score 34개 폭발

### 현재 상태

| 항목 | 상태 | 파일 |
|---|---|---|
| **P0** feature/scaler 정합성 자동 검증 + 연속 ERR-FATAL 자동 복구 | **완료** | `multi_horizon_model.py`, `main.py` |
| **P1** Checklist min_conf CRASH 패널티 분리 (최대 +4%p cap) | **완료** | `main.py` |
| **P2** 동적 mc 상한 캡 + 속도 제한 | **완료** | `settings.py`, `time_strategy_router.py` |
| **P3** grade=C→X Checklist 신뢰도 차단 카운터 + 일일 리포트 반영 | **완료** | `checklist.py`, `main.py`, `daily_exporter.py` |
| **P4** CB③ 4단계화 (NORMAL/WATCH/RESTRICTED/HALTED) | **완료** | `settings.py`, `circuit_breaker.py`, `main.py` |
| **P5** C등급 실험적 자동 진입 플래그 (기본 OFF) | **완료** | `settings.py`, `main.py` |
| **P6** ShadowSession BLOCKED 30분 지속 알림 + 권장 대응 | **완료** | `shadow_session.py` |
| **P7** 재기동 원인 로깅 (STARTUP/MANUAL/AUTO_DISCONNECT) | **완료** | `main.py` |
| **P8** EOD 스케일러 재적합 (daily_close 후 E_EOD 트리거) | **완료** | `main.py` |
| 다음 기동 실세션 확인 | **미완료** | — |

### 파라미터 상수 (P2 변경분)

| 상수 | 이전값 | 신규값 | 파일 |
|---|---|---|---|
| `MC_ABS_CEIL` | 0.75 | **0.62** | `config/settings.py` |
| `MC_ZONE_MAX` | (없음) | **0.65** | `config/settings.py` |
| `MC_STEP_LIMIT` | 0.08 | **0.03** | `config/settings.py` |
| `CB_ACC_WATCH_MIN` | (없음) | **0.35** | `config/settings.py` |
| `CB_ACC_RESTRICTED_MIN` | (없음) | **0.30** | `config/settings.py` |

### P5 활성화 방법

```python
# config/settings.py
ENTRY_GRADE_C_AUTO_EXP = True   # False가 기본값 — 명시 변경 필요
```
조건: TrendGate active + STABLE_TREND/LUNCH_RECOVERY + CB NORMAL + not RESTRICTED

### 다음 기동 시 실세션 확인

1. **P0**: ERR-FATAL 연속 2회 시 `[P0] 피처 불일치 N회 연속 — 비활성화/즉시 재학습 요청` 로그
2. **P1**: `[P1] Checklist min_conf 분리: 0.72→0.51` 로그 (CRASH 상태에서)
3. **P2**: DynMC 갱신 시 zone_mc가 0.65 이상으로 올라가지 않는지 확인
4. **P3**: 일일 리포트 말미 `CL신뢰도차단: N회` 항목 확인
5. **P4**: acc30m<35% 시 `[CB③-P4] acc30m 단계 전환: NORMAL → WATCH` 로그
6. **P6**: BLOCKED 30분 경과 시 Slack 알림 + 권장 대응 라인 포함 확인
7. **P7**: `[Session] 재기동 #N | cause=MANUAL` INFO / `AUTO_DISCONNECT` WARNING 로그
8. **P8**: 15:40 `[P8] EOD 스케일러 재적합 완료 n=500봉` SYSTEM 로그

---

## 2026-06-02 (101차) — 원웨이 추세장 신뢰도 미추종 구조 개선

### 배경

6/2 13:39 이후 원웨이 상승장 (~65pt)에서 conf가 0.30~0.48에 머물며 진입 0건.
로그 분석 결과 핵심 원인은 **conf 게이트가 아닌 방향 확정 실패** (dir=FLAT 고착).
- 3m 실제 UP 63.5% 구간에서 예측 0% / 5m 실제 UP 75% 구간에서 DOWN/FLAT 편향
- 15m+30m 가중치 합 0.79가 FLAT/DOWN → flat_score > up_score → dir=0
- TrendGate가 13:55·14:37에 ON이어도 dir==+1일 때만 min_conf 완화 → dir=0이면 무력
- 스케일러: 13:39 급등 후 z-score 탐지 13:57 → 리프레시 13:59 (20분 지연)
- 14:29·14:34: 5m ConstOut까지 발동해 추가 발목

### 현재 상태

| 항목 | 상태 |
|---|---|
| **P0-A TrendBoost** — TrendGate active 시 up/dn_score +0.07 직접 보정 | **완료** — ensemble_decision.py |
| **P0-B FlatCap** — TrendGate active 시 flat_score > 0.38 → 상한 + 재정규화 | **완료** — ensemble_decision.py |
| **P0-C CLOSE_VOLATILE 예외** — TrendGate active 시 단기 0.6× 축소 비적용 | **완료** — ensemble_decision.py |
| **P0-D 합의도 패널티 면제** — TrendGate active + 방향 일치 시 ×0.92 패널티 면제 | **완료** — ensemble_decision.py |
| **P1 D_PRICE_MOMENTUM** — 5분 급변(>0.23%) 감지 시 스케일러 즉시 트리거 | **완료** — main.py |
| 다음 기동 시 실세션 확인 | **미완료** |

### 실세션 확인 사항 (다음 기동)

1. TrendGate ON 로그 발화 확인: `[TrendGate] UP 추세 지속 모드 ON (streak=10)`
2. **TrendBoost 발화**: `[TrendBoost] UP streak active: up 0.3XX→0.4XX flat→0.XXX` (DEBUG)
3. **FlatCap 발화**: `[FlatCap] flat 0.5XX→0.38 (추세 보호)` (DEBUG) — flat이 0.38 이상일 때만
4. **합의도 패널티 면제**: `[Ensemble] 합의도 패널티 면제 (TrendGate active) n_agree=X/6` (DEBUG)
5. **D_PRICE_MOMENTUM 발화**: `[ScalerRefresh] 5분 누적 수익률 +0.XXX% → D_PRICE_MOMENTUM 트리거` (SYSTEM WARNING)
6. CLOSE_VOLATILE 구간 + TrendGate ON → 단기 0.6× 축소 로그 없음 확인
7. 원웨이 추세 중 dir=+1 확정 + 진입 발생 여부

### 수정 파일 (101차)

| 파일 | 변경 내용 |
|---|---|
| `model/ensemble_decision.py` | 클래스 상수 4종(`_TREND_UP_BOOST` 등), P0-A TrendBoost 블록, P0-B FlatCap 블록, P0-C CLOSE_VOLATILE 조건, P0-D 합의도 패널티 면제, `trend_boost_applied` 결과 키 |
| `main.py` | `_price_momentum_refit_until` 변수, D_PRICE_MOMENTUM 트리거 블록 (Phase B 직후) |

### 파라미터 상수 (튜닝 기준점)

| 상수 | 값 | 위치 | 조정 방향 |
|---|---|---|---|
| `_TREND_UP_BOOST` | 0.07 | ensemble_decision.py | 방향 확정 너무 쉬우면 줄임 |
| `_TREND_DN_BOOST` | 0.07 | ensemble_decision.py | 동상 |
| `_TREND_SCORE_CAP` | 0.58 | ensemble_decision.py | 과신 방지선 |
| `_FLAT_CAP_ON_TREND` | 0.38 | ensemble_decision.py | 너무 자주 진입이면 높임 |
| `_PRICE_MOMENTUM_MULT` | 2.5× | main.py | 잦은 오발화면 높임 |
| D_PRICE_MOMENTUM 쿨다운 | 20분 | main.py | 추세 지속 중 반복 원하면 줄임 |

---

## 2026-06-02 (99·100차) — 저변동성 인식 피처 + GBM 붕괴 방어

### 배경

6/2 장 중 로그 분석: 15m GBM이 39.3% UP → 44.1% FL로 각각 20·25분 고착.
GBM 스케일러 노후로 모든 피처가 동일 리프에 떨어지는 상수 출력 붕괴.
SGD비중 10% 바닥 고착. 저변동성 구간 FLAT 예측 실패 구조적 원인 규명 후 5종 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **`threshold_feasibility` 피처** — ATR/(1m_threshold×price), <1=FLAT 우세 | **완료** — feature_builder.py |
| **`micro_regime_code` 피처** — 직전분 레짐 수치화(0~4) | **완료** — feature_builder.py |
| **GBM 상수 출력 감지 (ConstOut)** — 5분×range<0.5%p → 앙상블 weight=0 | **완료** — ensemble_decision.py |
| **SGD 바닥 회복** — 30회 고착+acc≥40% → 0.5%p 회복(최대15%) | **완료** — online_learner.py |
| **ConstOut → 스케일러 재적합 훅** — D_FORCE daemon thread, 30분 쿨다운 | **완료** — main.py |
| **reset_daily() 버그 수정** — _gbm_w/_bucket_learn_count 루프 위치 오류 | **완료** — online_learner.py |
| 다음 기동 시 실세션 확인 | **미완료** |

### 실세션 확인 사항 (다음 기동)

1. `[ConstOut] 15m 상수 출력 5분 감지 (range=0.XXXX) → 앙상블 제외` SIGNAL WARNING 로그 발화 여부
2. `[ConstOut] 15m 상수 출력 해소 → 앙상블 복귀` 로그로 자동 복귀 확인
3. `[ConstOut] 상수 출력 확정 → 스케일러 재적합 시작` SYSTEM 로그 + `[ScalerRefresh]` 완료 로그
4. `[OnlineLearner] long 바닥 회복 SGD=11% GBM=89%` — 바닥 장기 고착 시 회복 발화 확인
5. `threshold_feasibility`, `micro_regime_code` — SIGNAL 로그 또는 DB에서 피처 저장 확인

### 수정 파일 (99·100차)

| 파일 | 변경 내용 |
|---|---|
| `features/feature_builder.py` | `threshold_feasibility`, `micro_regime_code` 피처, `build()` `micro_regime` 파라미터, `HORIZON_THRESHOLDS` import |
| `model/ensemble_decision.py` | ConstOut 감지 블록, `_hz_conf_hist`, `_hz_stuck`, `const_output_horizons` 결과 키, `reset_daily()` 확장 |
| `learning/online_learner.py` | 바닥 회복 상수 4종, `_floor_ticks`, `_adjust_weights()` 재작성, `reset_daily()` 버그 수정 |
| `main.py` | `micro_regime` 전달, `_const_out_refit_until`, ConstOut→refit 훅, daily_close 리셋 |

---

## 2026-06-02 (98차 계속) — 진입0 구조 개선 전면

### 배경

6/2 장 중 진입0 지속. mc 복원 버그, CoherenceGate 과잉 차단, Layer 2 단방향 편향,
CB③ FLAT 고착 등 구조적 문제 다수 발견·수정.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **GBM 105피처 재학습** — shap_feature_registry 91→108개 후 재실행 | **완료** |
| **mc 복원 버그 수정** — sqlite3.Row.get() → 직접 접근, 모든 zone 복원 | **완료** |
| **REGIME_MIN_CONFIDENCE 기본값** 0.52→0.42 (동적 mc와 동기화) | **완료** |
| **MC_ABS_FLOOR** 0.50→0.42 (SGD 블렌딩 희석 고려) | **완료** |
| **ShadowSession z 조건 완화** — _GATE_ZSCORE_WARN 2→50, BLOCKED 복구 추가 | **완료** |
| **quality_investor_fetch_count** clip 60→5 + SCALER_CLIP_FEATURES 추가 | **완료** |
| **Layer 2 복귀 조건 양방향** — bounce/OFI 제거, ATR+z극단만 유지 | **완료** |
| **Layer 2 발동 조건 양방향** — abs() 적용 (급등=급락 동일 처리) | **완료** |
| **CoherenceGate** FLAT 제외 계산 + COHERENCE_GATE_MIN 0.67→0.60 | **완료** |
| **CB③ FLAT 예측 제외** + CB_ACCURACY_MIN_30M 0.35→0.28 | **완료** |
| **PATH_LABEL_RATIO** 0.45→0.55 + _CW_30M {FL:0.70} (FLAT 편향 억제) | **완료** |
| **mc 이력 ts 형식** — mmdd-hhmm (0602-0935) | **완료** |
| **툴팁 현행화** — 앙상블 등급·신호방향·신뢰도·Layer2 Gate | **완료** |
| 다음 기동 시 CoherenceGate 통과 + 진입 발생 여부 확인 | **미완료** |

### 핵심 수정 정리

```
진입 차단 경로 (수정 전→후):

[앙상블]
  REGIME_MIN_CONF: 0.52 → 0.42 (동적 base_mc와 동기화)
  CoherenceGate: FLAT 포함 3/6=0.50차단 → FLAT 제외 3/4=0.75 통과
  임계값: 0.67 → 0.60 (4/6=0.667 수학 오류 수정)

[체크리스트]
  actual_min_conf = max(0.42, ZONE_MC) → ZONE_MC 기준으로 낮아짐

[CB③]
  FLAT 예측 제외 후 방향성(UP/DN)만 집계
  임계값 0.35 → 0.28 (랜덤 50% 기준 재설정)

[Layer 2]
  CRASH 발동: 하락만 → abs() 양방향
  CRASH 복귀: bounce+OFI 제거 → ATR+z극단만 (방향 중립)

[ShadowSession]
  z_warn 조건: < 2 → < 50 (급변장 대비)
  BLOCKED 상태에서 acc30m + core_health 충족 시 복구 가능
```

### 수정 파일 (6/2)

| 파일 | 변경 |
|---|---|
| `config/settings.py` | MC_ABS_FLOOR 0.42, REGIME_MIN_CONF 0.42, COHERENCE_GATE_MIN 0.60, CB_ACCURACY_MIN_30M 0.28 |
| `strategy/entry/time_strategy_router.py` | _restore_mc_from_history() sqlite3.Row 버그 수정 |
| `safety/shadow_session.py` | z 조건 완화 + BLOCKED→LIVE 복구 |
| `collection/cybos/investor_data.py` | fetch_count clip 60→5 |
| `collection/macro/intraday_tactical_regime.py` | Layer2 발동/복귀 양방향 수정 |
| `model/ensemble_decision.py` | CoherenceGate FLAT 제외 |
| `learning/batch_retrainer.py` | PATH_LABEL_RATIO 0.55, _CW_30M FL:0.70 |
| `main.py` | CB③ FLAT 제외 (direction!=0) |
| `dashboard/main_dashboard.py` | Layer2 툴팁 + 발동지표 ± 표시 + 앙상블/신뢰도 툴팁 |
| `dashboard/panels/dynamic_mc_panel.py` | mc 이력 ts mmdd-hhmm 형식 |

---

## 2026-06-01 (98차) — 동적 min_conf 구현 + GBM 재학습

### 배경

97차 이후 GBM이 신규 피처(17개) 미포함 상태로 재학습됨 → conf 평균 0.406 → 진입0 지속.
원인 분석 → 재학습 → 구조적 진입0 방지 위해 동적 mc 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **GBM 105피처 재학습 완료** — 1m/3m/5m/10m/15m/30m 전 교체 (force=True) | **완료** |
| **RF 재학습 완료** — rf_horizons.pkl (88피처 기반, 다음 재학습 시 105피처 갱신) | **완료** |
| **shap_feature_registry 갱신** — 91 → 108개 (신규 17개 수동 추가) | **완료** |
| **동적 mc 구현** — update_dynamic_mc() + 주기1(재학습) + 주기2(08:55) | **완료** |
| **mc_history.db** — mc 변경 이력 저장 모듈 (model/mc_history_db.py) | **완료** |
| **DynamicMcPanel UI** — 🎯 신뢰도 게이트 탭 신규 | **완료** |
| **mc 재보정 실행** — 최근 3,789봉 기준 base_mc=0.50 적용 | **완료** |
| 다음 기동 시 주기1/2 동작 확인 | **미완료 — 다음 기동** |
| 다음 GBM 재학습 시 105피처 확인 | **미완료 — 다음 재학습** |

### 재학습 결과 (105개 피처, force=True, 26주)

| 호라이즌 | 이전 acc | 재학습 후 acc | RF OOB |
|---|---|---|---|
| 1m | 0.362 | **0.419** | 0.483 |
| 3m | 0.465 | 0.468 | 0.397 |
| 5m | 0.473 | **0.504** | 0.394 |
| 10m | 0.406 | 0.398 | 0.435 |
| 15m | 0.372 | **0.387** | 0.429 |
| 30m | 0.478 | **0.512** | 0.461 |

### 진입0 분석 결과 (금일 데이터 기준)

| 조건 | 진입 수 | 승률 | 총손익 |
|---|---|---|---|
| 재학습 전 mc=0.57 | 0건 | — | — |
| 재학습 후 mc=0.65 | 22건 | 77% | +1,056만원 |
| 재학습 후 mc=0.70 | 17건 | 82% | +888만원 |

### 수정/신규 파일 (98차)

| 파일 | 내용 |
|---|---|
| `docs/260601_DYNAMIC_MIN_CONF_PLAN.md` | 동적 mc 설계 문서 |
| `model/mc_history_db.py` | mc 변경 이력 DB 모듈 |
| `strategy/entry/time_strategy_router.py` | `update_dynamic_mc()` + `_ZONE_MC_MULT` |
| `config/settings.py` | MC_PERCENTILE/FLOOR/CEIL/EMA_ALPHA 등 상수 |
| `main.py` | `_recalibrate_mc()` + 주기1(재학습 콜백) + 주기2(워밍업) |
| `dashboard/panels/dynamic_mc_panel.py` | 🎯 신뢰도 게이트 탭 |
| `dashboard/main_dashboard.py` | 탭 추가 |
| `scripts/recalibrate_min_conf.py` | mc 분포 측정 + 수동 재보정 스크립트 |

### 98차 다음 기동 확인 사항

1. 08:55 로그: `[DynMC] mc 재보정 완료 trigger=DAILY_WARMUP base=X.XXX` (주기2)
2. 🎯 신뢰도 게이트 탭 표시 확인 (mc 카드 5개 + 추이 + 이력)
3. GBM 재학습 완료 시: `[DynMC] mc 재보정 완료 trigger=RETRAIN` (주기1)
4. mc_history.db에 이력 누적 확인

---

## 2026-06-01 (97차) — F1 고도화 전면 구현

### 배경

F1_IMPROVEMENT_MASTER_PLAN.md 기반 로드맵 P1~P6c 전체 구현.  
근본원인 5가지 중 4가지 대응 완료 (2단계 예측 구조만 장기 과제로 잔존).

### 현재 상태

| 항목 | 상태 |
|---|---|
| **피처 17개 추가** — volume_profile.py 신규, feature_builder.py + backfill_features.py 수정 | **완료** |
| **소급 190일 피처 갱신** — 71,155봉 `--update-features` 2회 실행 | **완료** |
| **코히어런스 게이트** — COHERENCE_GATE_MIN=0.67, ensemble_decision.py | **완료** |
| **HorizonF1AdaptiveWeight** — F1 EMA 기반 가중치, main.py STEP 1 연결 | **완료** |
| **시간대 × 호라이즌 min_conf 2D 표** — MIN_CONF_TABLE, main.py STEP 6 | **완료** |
| **호라이즌별 최적 σ_k** — optimize_sigma_k.py + SIGMA_K_PER_HORIZON (10m/15m=0.38, 30m=0.33) | **완료** |
| **경로 조건부 레이블** — PATH_LABEL_RATIO=0.45, batch_retrainer | **완료** |
| **RF 이종 앙상블** — rf_horizon_model.py 신규, main.py STEP 5 blend(×0.30) | **완료** |
| **학습 레이블 고정화** — USE_FIXED_LABEL_THRESHOLD=True | **완료** |
| **MIN_TRAIN_BARS 15000** — 5000(13일)→15000(40일) | **완료** |
| **GBM 파라미터 강화** — n_estimators=300, learning_rate=0.04 | **완료** |
| **다음 GBM 재학습 시 신규 피처 17개 포함 확인** | **미완료 — 다음 기동** |
| **RF OOB score 로그 확인** (첫 재학습 후) | **미완료 — 다음 기동** |

### 신규 파일 (97차)

| 파일 | 내용 |
|---|---|
| `features/technical/volume_profile.py` | POC / Value Area 계산기 (n=60봉, bins=20) |
| `model/rf_horizon_model.py` | RF 이종 앙상블 (n=150, balanced, OOB) |
| `scripts/optimize_sigma_k.py` | 호라이즌별 최적 σ_k 탐색 스크립트 |
| `docs/F1_IMPROVEMENT_MASTER_PLAN.md` | F1 고도화 마스터 플랜 (최종 업데이트) |

### 수정 파일 (97차)

| 파일 | 핵심 변경 |
|---|---|
| `config/settings.py` | MIN_CONF_TABLE, SIGMA_K_PER_HORIZON, COHERENCE_GATE_MIN, USE_FIXED_LABEL_THRESHOLD, GBM_PARAMS |
| `features/feature_builder.py` | 피처 17개 추가 (time, momentum, EMA, BB, CVD delta, VP, volume_acc, vwap_momentum, prev_day) |
| `scripts/backfill_features.py` | 피처 17개 소급 계산 + `--update-features` 모드 |
| `learning/batch_retrainer.py` | USE_FIXED_LABEL_THRESHOLD + SIGMA_K_PER_HORIZON + _path_conditioned_label + RF 학습 + MIN_TRAIN_BARS=15000 + n_estimators=300 |
| `model/ensemble_decision.py` | HorizonF1AdaptiveWeight + 코히어런스 게이트 |
| `strategy/entry/time_strategy_router.py` | get_horizon_min_confs() 추가 |
| `main.py` | P4 호라이즌 conf 필터 + RF blend + F1 누적 + 피처 갱신 연결 |

### 97차 다음 기동 확인 사항

1. GBM 재학습 후 SIGNAL 로그: `[Retrain] DB 로드 완료: X행 × Y피처 (Y ≥ 113개)` 확인
2. RF 학습 로그: `[RF] 1m 학습 완료 (n=X OOB=YY.Y%)` 6개 호라이즌 확인
3. 코히어런스 게이트 로그: `[Ensemble] CoherenceGate 차단 score=0.XX` 발생 여부
4. FLAT 비율 변화: 경로 조건부 레이블 적용 후 `[Bias]` 로그에서 FL 비율 확인 (기존 33% → 38~45% 예상)
5. F1 적응형 가중치: `[Retrain]` 이후 30m 가중치 감소 여부 DEBUG 로그

---

## 2026-06-01 (95차) — 스케일러 Phase A·C 구현 (워밍업 + Robust 전처리)

### 배경

2026-06-01 진입 0건 근본원인(스케일러 65시간 노후화 → ATR z=+5.04 → grade=X 전일 지속 → CB③ 당일 정지) 후속 조치. SCALER_ROBUST_PLAN.md 작성 후 Phase A(장전 워밍업)·C(Robust 전처리) 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **SCALER_ROBUST_PLAN.md 신규** — 운영안·Robust 도입·DB/UI 설계 전체 (섹션 1~9) | **완료** |
| **Phase A: 08:55 스케일러 워밍업** — `load_features_for_warmup()` + `refit_scalers_only()` + main.py daemon thread | **완료** |
| **Phase C: Robust 전처리** — `apply_robust_preprocess()` atr/avg_volume log1p, spread_ticks/mlofi_slope clip | **완료** — 학습·예측·워밍업 3경로 일관 적용 |
| 실세션 확인 (08:55 `[ScalerWarmup] 완료` 로그) | **미완료** — 다음 기동 시 |

### 수정 파일 (95차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | `SCALER_WARMUP_LOOKBACK_BARS=500`, `SCALER_WARN_MINUTES=90`, `SCALER_LOG1P_FEATURES`, `SCALER_CLIP_FEATURES` 추가 |
| `model/multi_horizon_model.py` | `apply_robust_preprocess()` 모듈 함수 신규 + `refit_scalers_only()` 신규 + `fit()`·`predict_proba()` 전처리 적용 |
| `learning/batch_retrainer.py` | `load_features_for_warmup()` 신규 + `retrain_now()` Robust 전처리 적용 |
| `main.py` | `pre_market_setup()` — `_scaler_warmup_worker` daemon thread 삽입 |
| `docs/SCALER_ROBUST_PLAN.md` | **신규** — 운영안·Robust·DB/UI 설계 전체 |

### 95차 실세션 확인 사항

1. `[ScalerWarmup] 완료 n=500봉 horizons=[...] 0.XXs` 로그 (08:55 SYSTEM)
2. `canary_stale_age_hours()` < 1h (워밍업 완료 이후)
3. GBM 재학습 없는 날(일반 화~금): 스케일러 단독 워밍업 동작 확인
4. atr/spread_ticks 극단 z 빈도 이전 대비 감소 확인 (SIGNAL 로그)

---

## 2026-06-01 (94차) — 스케일러 강건화 완성 + 운영 클린업

### 배경

2026-06-01 진입 0건 근본원인(스케일러 65시간 노후화 → grade=X) 후속 조치. SCALER_ROBUST_PLAN.md Phase B·D + 섹션 8·9 전체 구현. 동시에 SYSTEM.log 200MB/일 버그 수정 및 정기 클린업 인프라 구축.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **Phase B: 정기/강제 refresh** — `check_refresh_trigger()` (B_OPEN 15분·C_PERIODIC 60분·D_FORCE 극단z) | **완료** — model/multi_horizon_model.py + main.py |
| **Phase D: cancel_add_ratio DB 클린업** — 11행 삭제(최대 7.49억 이상치) | **완료** — scripts/cleanup_cancel_add_ratio.py |
| **MIN_TRAIN_BARS 5000 복원** — Phase D 완료 후 3000→5000 | **완료** — learning/batch_retrainer.py |
| **섹션 8: scaler_monitor.db 수집** — predict_proba INSERT + refresh UPDATE + daily_close EOD | **완료** — model/scaler_monitor_db.py + multi_horizon_model.py + main.py |
| **섹션 9: ScalerMonitorPanel UI** — "🔬 스케일러" 탭 | **완료** — dashboard/panels/scaler_monitor_panel.py |
| **SYSTEM.log 200MB/일 버그 수정** — 호가 이벤트 INFO→DEBUG | **완료** — api_connector.py + realtime_data.py |
| **monthly_cleanup.py** — 30일 로그·90일 shap·60일 예측 자동 정리 | **완료** — scripts/monthly_cleanup.py |
| 실세션 확인 (scaler_monitor.db 누적 + 패널 표시) | **미완료** — 다음 기동 시 |

### 수정 파일 (94차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | Phase B 상수 6개 + `SCALER_MONITOR_DB` 경로 추가 |
| `model/scaler_monitor_db.py` | **신규** — scaler_monitor.db CRUD 전체 |
| `model/multi_horizon_model.py` | Phase B `check_refresh_trigger` + `__init__` 상태변수 + `predict_proba(monitor_ts=)` INSERT + `refit_scalers_only(trigger_ts=,trigger_type=,trigger_reason=)` UPDATE |
| `learning/batch_retrainer.py` | MIN_TRAIN_BARS 3000→5000 복원 |
| `main.py` | `_grade_x_count` + `_scaler_refresh_running` + Phase B 스레드 + `daily_close()` EOD INSERT |
| `dashboard/panels/scaler_monitor_panel.py` | **신규** — ScalerMonitorPanel (60초 갱신) |
| `dashboard/main_dashboard.py` | "🔬 스케일러" 탭 추가 |
| `collection/cybos/api_connector.py` | `[CybosEvent] recv begin/end` INFO→DEBUG |
| `collection/cybos/realtime_data.py` | `[CybosRT-EVENT] dispatch` INFO→DEBUG |
| `scripts/cleanup_cancel_add_ratio.py` | **신규** — Phase D DB 클린업 스크립트 |
| `scripts/monthly_cleanup.py` | **신규** — 월 1회 정기 클린업 |

### 94차 실세션 확인 사항

1. `[ScalerRefresh] trigger=A_WARMUP` 로그 (08:55 워밍업)
2. `[ScalerRefresh] trigger=B_OPEN elapsed=6min` 로그 (09:15 최초 정기 트리거)
3. `[ScalerMonitor]` 로그 발생 (극단 z 또는 노후 90분+ 시)
4. SYSTEM.log 크기: 당일 5MB 이하 (이전 200MB 대비)
5. "🔬 스케일러" 탭 → 호라이즌별 노후도 실시간 갱신 확인
6. 15:40 `[ScalerMonitor] EOD 일별 집계 저장` 로그

---

## 2026-05-30 (91·92차) — rolling σ 방법3 Phase 1+2 구현 + ATR 완전 제거

### 배경

5/19~5/29 진입 0 근본 원인(저변동성 장세 → FLAT 레이블 50~70% 폭증 → confidence 붕괴)을 해결하기 위해 방법3(rolling sigma × k=0.41) 단독 채택. Phase 1(핵심 로직 구현) + Phase 2(ATR 점진 제거 완료).

### 현재 상태

| 항목 | 상태 |
|---|---|
| **SIGMA_K=0.41, SIGMA_W=20** + `USE_ROLLING_SIGMA_THRESHOLD=True` | **완료** — config/settings.py |
| **batch_retrainer 방법B** — 봉별 rolling σ×k 레이블 생성 | **완료** — learning/batch_retrainer.py |
| **sigma_buf 매분 갱신** + HORIZON_THRESHOLDS 실시간 갱신 | **완료** — main.py 파이프라인 |
| **진입 게이트** — 09:00~09:19 금지 / 09:20~09:29 A등급·size×0.5 / 09:30 표준 | **완료** — main.py STEP 6 |
| **PRE_RETRAIN_SIZE_MULT=0.6** — GBM 첫 재학습 완료 전 보수 진입 | **완료** — main.py |
| **EOD sigma 저장** (_last_sigma_20) + 일일 리셋 | **완료** — main.py daily_close |
| **ATR 동적 threshold 완전 제거** — _log_threshold_monitor, tick 카운터, MULT 상수 | **완료** — main.py + settings.py |
| **ThresholdMonitorPanel** UI 대시보드 추가 | **완료** — dashboard (미커밋) |
| 프로그램 재시작 후 실세션 확인 | **미완료** — 다음 기동 시 |
| P1 방안B — prediction_buffer sigma_at_t 저장 | **미구현** — NEXT 잔여 |

### 수정 파일 (91·92차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | SIGMA_K/W/MIN/USE_ROLLING/PRE_RETRAIN 추가, ATR MULT 제거 |
| `learning/batch_retrainer.py` | 방법B 봉별 rolling σ 레이블 생성 |
| `main.py` | sigma 파이프라인 + 진입 게이트 + pre_retrain 제어 + ATR 제거 |
| `dashboard/panels/threshold_monitor_panel.py` | **신규** — Phase A 모니터 UI |
| `dashboard/main_dashboard.py` | "📐 임계값 모니터" 탭 추가 |
| `docs/ROLLING_SIGMA_IMPL_PLAN.md` | **신규** — Phase 0~3 구현 계획 |

### 91·92차 실세션 확인 사항

1. `[EntryGate] sigma_20봉 미수집 — 진입 대기 (09:20 해제)` 로그 (09:00~09:19)
2. `[EntryGate] GBM 첫 재학습 완료 — 사이즈 제한 해제` 로그
3. `[Sigma] EOD sigma_20=0.0XXXX% 저장` 로그 (15:40 daily_close)
4. `[Bias] 1m FL=XX%` — FL 35% 이하 확인 (이전 87~100% 대비)
5. 09:30 이후 A/B 등급 진입 신호 발생 확인
6. "📐 임계값 모니터" 탭 표시 확인

---

## 2026-05-30 (90차) — 임계값 데이터 기반 재보정 + 운영/연구 병렬 구조 + Phase A WFA 모니터

### 배경

2026-04-28~05-29 DB 기반 분석으로 현행 `HORIZON_THRESHOLDS`가 15m +42%, 30m +63% 과다 설정되어 FLAT 레이블 품질 심각 왜곡 확인. 임계값 현실화 + 운영(대칭)/연구(비대칭) 병렬 구조 + Phase A 자동 재보정 모니터 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **HORIZON_THRESHOLDS 재보정** (1m/5m/10m/15m/30m, 3m 현행 유지) | **완료** — config/settings.py |
| **HORIZON_THRESHOLDS_RESEARCH** (비대칭, 연구용 고정, ATR 갱신 비대상) | **완료** — config/settings.py |
| **SGD_FULL_RESET_PENDING 플래그** (다음 GBM 재학습 완료 시 1회 reset_full) | **완료** — config/settings.py + main.py |
| **build_targets_asymmetric()** (연구용 비대칭 레이블 생성) | **완료** — model/target_builder.py |
| **class_weight 재조정** (1m/5m FL 0.85, 30m FL 1.00) | **완료** — multi_horizon_model.py + batch_retrainer.py |
| **OnlineLearner.reset_full()** (SGD 완전 초기화) | **완료** — learning/online_learner.py |
| **ThresholdRecalibrator** Phase A 롤링 재보정 모니터 | **완료** — learning/threshold_recalibrator.py (신규) |
| **daily_close 금요일 Phase A 연결** | **완료** — main.py |
| **docs/THRESHOLD_WFA_MONITOR.md** 설계 문서 | **완료** |
| 프로그램 재시작 후 실세션 확인 | **미완료** — 다음 기동 시 |

### 수정 파일 (90차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | HORIZON_THRESHOLDS 재보정 + RESEARCH + SGD_FULL_RESET_PENDING |
| `model/target_builder.py` | `build_targets_asymmetric()` 신규 |
| `model/multi_horizon_model.py` | class_weight 1m/5m/30m 재조정 |
| `learning/batch_retrainer.py` | class_weight multi_horizon_model과 동기화 |
| `learning/online_learner.py` | `reset_full()` 신규 |
| `main.py` | ThresholdRecalibrator 초기화 + SGD_FULL_RESET_PENDING 처리 + Phase A 연결 |
| `learning/threshold_recalibrator.py` | **신규** — Phase A 롤링 재보정 모니터 |
| `docs/THRESHOLD_WFA_MONITOR.md` | **신규** — WFA 모니터 설계 문서 |

### 90차 실세션 확인 사항

1. 재시작 후 첫 GBM 재학습 완료 시 `[SGD] threshold 교체 후 완전 리셋 완료 (1회)` 로그
2. 이후 재학습에서 SGD 리셋 없음 (1회만 실행 확인)
3. 새 threshold 기준 [Threshold] ATR 로그에서 15m/30m 발동 빈도 증가 확인
4. 다음 금요일(2026-06-05) `[ThresholdRecal] 재보정 결과` 로그 확인

---

## 2026-05-29 (89차) — Qualification 세션 필터 + 호라이즌별 정확도 + 툴팁

### 배경

88차 구현 직후 실세션 스크린샷 확인 결과 2가지 이슈 발견:
1. 10m/15m/30m이 세션 시작 직후에도 v4/t4 (ACTIVE) — 이전 세션 carry-over 예측이 카운팅된 것
2. acc=0% 고착 — `OnlineLearner`에 호라이즌별 정확도 메서드가 없어 항상 0

### 현재 상태

| 항목 | 상태 |
|---|---|
| **세션 필터**: `_pred_ts_q >= self._session_start_ts` — 이전 세션 carry-over 예측 카운팅 제외 | **완료** — main.py |
| **호라이즌별 정확도 버퍼**: `_horizon_acc_buf` + `horizon_accuracy(h)` + `reset_daily()` 업데이트 | **완료** — learning/online_learner.py |
| **툴팁**: "호라이즌 자격 현황" 라벨에 카드 설명 + acc 정의 + recent_accuracy() 차이 | **완료** — dashboard/main_dashboard.py |
| 실세션 확인 | **미완료** — 다음 기동 시 |

### 수정 파일 (89차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | STEP 1 qualification 카운팅에 `_pred_ts_q >= self._session_start_ts` 필터 추가 |
| `learning/online_learner.py` | `_horizon_acc_buf` 딕셔너리, `learn()` 호라이즌 버퍼 기록, `horizon_accuracy(h)` 신규, `reset_daily()` 확장 |
| `dashboard/main_dashboard.py` | "호라이즌 자격 현황" 라벨 툴팁 (카드 상태·acc 정의·recent_accuracy 차이·30m 주의사항·Phase 상태) |

### 89차 실세션 확인 사항

1. 세션 시작 시 모든 호라이즌 v0/t0 (WAIT) 출발 확인 — 이전 세션 carry-over 없음
2. 09:01+ 1m v1 → 09:03 v3 ACTIVE 전환 확인
3. 10m v1 전환이 10분 이후에 발생하는지 확인
4. acc% — 5건 누적 전 0%, 5건 이후 실제 적중률로 갱신 확인
5. 라벨 호버 시 툴팁 표시 확인

---

## 2026-05-29 (88차) — 호라이즌 자격 추적 Phase 1+2 구현

### 배경

`docs/HORIZON_QUALIFICATION_IMPLEMENTATION_PLAN.md` 및 `docs/HIGHER_DIRECTION_AND_LOWER_EXECUTION_ENGINE_PLAN.md` 설계 기반. 멀티호라이즌 앙상블에서 세션 초반 미검증 호라이즌이 과신 conf를 내는 문제 해결 목적. 오늘은 상태 추적(Phase 1)과 대시보드 dry-run(Phase 2)만 구현 — 앙상블 필터링은 미활성.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **Phase 1 (A-1)**: `_horizon_runtime_state` 상태 추적 + STEP 1 verified_cycles + STEP 2 trained_cycles 동기화 + daily_close() 리셋 | **완료** — main.py |
| **Phase 2 (A-2)**: 호라이즌 자격 현황 카드 6개 (2×3) + `update_qualification()` + MireukDashboard 위임 | **완료** — dashboard/main_dashboard.py |
| **설정 상수**: `HORIZON_QUALIFY_MIN_CYCLES=3`, `QUALIFY_QUALITY_MIN_SAMPLES=10` | **완료** — config/settings.py |
| **버그 수정**: `settings.` → `runtime_settings.` 2곳 — CRITICAL `name 'settings' is not defined` 해소 | **완료** — main.py |
| 실세션 확인 | **미완료** — 다음 기동 시 |
| Phase 3 (A-3): 앙상블 필터링 활성화 | **미구현** — 카드 1세션 안정 확인 후 |
| 장중 재시작 복원 (`_restore_qualification_state()`) | **미구현** — Phase 3 직전 |

### 수정 파일 (88차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `_horizon_runtime_state` (`__init__`), STEP 1 verified_cycles 추적, STEP 2 trained_cycles 동기화, STEP 6 `update_qualification()` 호출, `daily_close()` 리셋, `settings.` → `runtime_settings.` 2곳 |
| `dashboard/main_dashboard.py` | `_qualify_cards` (`__init__`), `_build()` 자격 카드 6개, `EntryPanel.update_qualification()`, `MireukDashboard.update_qualification()` 위임 |
| `config/settings.py` | `HORIZON_QUALIFY_MIN_CYCLES=3`, `QUALIFY_QUALITY_MIN_SAMPLES=10` 추가 |

### 88차 실세션 확인 사항

1. `[Qualify] 1m verified=N/3 trained=N/3` DEBUG 로그 매분 출력 확인
2. 09:06+ 1m/3m `qualified=True` 전환 `[Qualify] X 자격 획득` SIGNAL 로그 확인
3. 대시보드 호라이즌 자격 카드 WAIT(회색) → ACTIVE(녹색) 전환 확인
4. 15:10 daily_close 후 전 호라이즌 WAIT(0/3) 리셋 확인
5. 앙상블 비중/진입 로직 **변화 없음** 확인 (Phase 1·2는 상태 추적 + UI만)

---

## 2026-05-22 (87차) — Layer 2 UI 개선 + update_layer2() 파이프라인 연결

### 현재 상태

| 항목 | 상태 |
|---|---|
| **발동 지표 6개 재정비**: 시가-0.8&15m 제거, 임계값 표시 개선, 3색 로직 | **완료** — dashboard/main_dashboard.py |
| **조건 체크 로그 단순화**: 3줄 고정 포맷 + 복귀 조건 (DAY_RISK_OFF/CRASH 시) | **완료** — dashboard/main_dashboard.py |
| **`_layer2_log` 초기값**: 기동 직후 빈 박스 해소 | **완료** — dashboard/main_dashboard.py |
| **`update_layer2()` 파이프라인 연결**: main.py STEP 4 직후 1줄 추가 | **완료** — main.py (82차부터 미연결 해소) |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 |

### 수정 파일 (87차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | 발동지표 6개 재정비 + 3색 로직 / 조건 로그 포맷 단순화 / `_layer2_log` 초기값 |
| `main.py` | `update_layer2()` 호출 1줄 추가 (STEP 4 직후) |

### 87차 실세션 확인 사항 (2026-05-23)

1. **발동 지표**: 장중 당일 수익률이 −0.8%~−1.0% 구간이면 오렌지, −1.0% 초과 시 빨강
2. **조건 로그**: NORMAL 상태에서 3줄 고정 텍스트 표시 확인
3. **레짐 전환**: DAY_RISK_OFF 진입 시 발동 지표 빨강 + 복귀 조건 ✔/✘ 표시
4. **기동 직후**: `_layer2_log`에 NORMAL 기본 텍스트 표시 (비어있지 않음)

---

## 2026-05-22 (86차) — 5/22 진입 0 P0 구현 + EOD 스케일러 초기화

### 배경

Deep·Codex 5/22 진입 0 원인 분석 리뷰 기반 P0 5종 구현. signal() TypeError 재발 차단, SHS/EKS 시스템 건강 감시, Warm Scaler Canary, CORE 진단 로그. EOD 스케일러 초기화 3종 추가 수정.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **SHS + EKS**: `safety/system_health.py` 신규 | **완료** |
| **SHS Slack 알림**: `notify_shs_alert()`, `notify_kill_switch()` | **완료** — utils/notify.py |
| **SHS UI 배지**: `lbl_shs` 상단 헤더 + `update_shs_badge()` | **완료** — dashboard/main_dashboard.py |
| **Warm Scaler Canary**: `canary_stale_age_hours()`, `canary_z_warn_count()` | **완료** — model/multi_horizon_model.py |
| **`_load_all()` mtime 동기화**: `_scaler_fitted_at[h]` = pkl mtime | **완료** — model/multi_horizon_model.py |
| **main.py Canary·SHS·EKS 연동**: 08:55 검사·GAP_OPEN·EKS 판정 | **완료** — main.py |
| **log_manager `**_kwargs`**: signal/system/trade TypeError 방어 | **완료** — logging_system/log_manager.py |
| **CORE 진단 로그**: VWAP/CVD/OFI raw값 탈락 시 출력 | **완료** — strategy/entry/checklist.py |
| **EOD `_load_all()` 무조건 호출**: retrain 실패에도 최신 pkl 적용 | **완료** — main.py daily_close() |
| **`system_health.reset_daily()`**: EKS·GAP_OPEN 일일 초기화 | **완료** — safety/system_health.py + main.py |
| **재시작 방지 락**: BrokerSync→connect_broker() 재호출 차단 | **❌ 미구현** — 잔여 P0 최우선 |
| **Scaler Auto Re-fit**: 기동 시 최근 5일 데이터로 scaler 재학습 | **❌ 미구현** — Canary 감지만 |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 |

### 수정 파일 (86차)

| 파일 | 변경 내용 |
|---|---|
| `safety/system_health.py` | **신규** — SHS 계산 + EKS 상태 머신 + `reset_daily()` |
| `utils/notify.py` | `notify_shs_alert()`, `notify_kill_switch()` 추가 |
| `dashboard/main_dashboard.py` | `lbl_shs` 배지 + `update_shs_badge()` |
| `model/multi_horizon_model.py` | Canary 2메서드 + `_load_all()` mtime 동기화 |
| `logging_system/log_manager.py` | signal/system/trade `**_kwargs` 방어 가드 |
| `strategy/entry/checklist.py` | CORE 탈락 raw값 진단 로그 |
| `main.py` | Canary·SHS·EKS 연동 + EOD `_load_all()` + `system_health.reset_daily()` |

### 86차 실세션 확인 사항 (2026-05-23)

1. **SHS 배지**: 상단 헤더 `♥ SHS 100` (정상) 또는 `⚠ SHS N` (경고) 표시
2. **Canary**: `[Canary] scaler 노후=Xh z경고피처=N개` 로그 (08:55)
3. **EKS 판정**: `[SHS-EKS] EKS 미발동. conf_max=XX.X% core_pass=N/5봉` 로그 (09:05 직후)
4. **CORE 진단**: `[Checklist] CORE 피처 ✗ ... | VWAP pos=±X.XXX need >0` 형식 확인
5. **EOD**: 15:40 `daily_close()` 후 `[Model] X 로드 성공` 6개 호라이즌 재로드 확인

---

## 2026-05-22 (85차) — 모의투자 세션 이상점 7·8 deep dive + 구조적 수정 4종

### 배경

14:53~15:09 모의투자 세션 로그에서 이상점 7·8 발견. 1m/5m FL 편향 87%/100%(이상점 7), 10m conf 50~55% 과도 압축(이상점 8)을 deep dive 분석 후 5개 파일에 걸쳐 수정 4종 구현. 커밋 `67f974e`.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **이상점 7-A**: `_CW_1M={FL:0.60}`, `_CW_5M={FL:0.58}` 명시적 FL 완화 | **완료** — multi_horizon_model.py, batch_retrainer.py |
| **이상점 7-D**: CLOSE_VOLATILE 단기(1m/3m/5m) 0.6× 가중치 축소 + time_zone 파라미터 | **완료** — ensemble_decision.py, main.py |
| **이상점 8-B**: `WINDOW=200`(500→), 재보정 주기 `%20`(50→) | **완료** — calibration.py |
| **이상점 8-C**: 10m/15m Platt 하한 `raw_conf×0.85` | **완료** — main.py `_apply_horizon_calibration()` |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (85차)

| 파일 | 변경 내용 |
|---|---|
| `model/multi_horizon_model.py` | `_CW_1M={FL:0.60, UP:1.20, DN:1.20}`, `_CW_5M={FL:0.58, UP:1.21, DN:1.21}` 추가 |
| `learning/batch_retrainer.py` | `_CW_1M`, `_CW_5M` 동일하게 추가 (학습기 일관성) |
| `learning/calibration.py` | `WINDOW=200`, 재보정 `% 20` |
| `model/ensemble_decision.py` | `time_zone` 파라미터 추가, CLOSE_VOLATILE 단기 0.6× 재정규화 |
| `main.py` | 10m/15m Platt 하한, `ensemble.compute()` `time_zone` 전달 |

### 85차 실세션 확인 사항 (2026-05-23)

1. **이상점 7 개선**: 1m/5m FL 비율 감소 확인 — `[Bias]` 로그에서 FL 편향 75% 미만 달성 여부
2. **이상점 7-D**: `[Ensemble] CLOSE_VOLATILE 단기 0.6×` 로그 14:00~15:00 구간 발생 확인
3. **이상점 8-B**: 다음 GBM 재학습 후 Platt 200건 윈도우로 현재 구간 반영 속도 향상
4. **이상점 8-C**: 10m conf가 `raw_conf × 0.85` 이하로 압축되지 않는지 확인 — 로그 `[Calib] 10m Platt 하한` 발화 빈도

---

## 2026-05-22 (84차) — 모의투자 세션 이상점 3~6 deep dive + 구조적 수정 4종

### 배경

12:11~12:48 모의투자 세션 로그에서 이상점 3~6을 발견. 30m 예측 7연속 실패(이상점 3), 50분 정확도 급락(이상점 4), Bias 통계 의미 없음(이상점 5), conf 전체 구간 60% 미달(이상점 6)을 deep dive 분석 후 5개 파일에 걸쳐 수정 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| **이상점 3**: `_CW_30M = {FL:0.65, UP:1.18, DN:1.18}` FL 다운웨이팅 완화 | **완료** — multi_horizon_model.py, batch_retrainer.py |
| **이상점 4**: `ACCURACY_WINDOW=150`, `_ADJUST_EVERY=3` 분봉 단위 조정 | **완료** — online_learner.py |
| **이상점 5**: 30건 롤링 Bias 버퍼, UP/DN/FL 추적, 15건+ 시 75% 편향 감지 | **완료** — main.py |
| **이상점 6-A**: SGD 초기(< 30건) GBM 전용 모드 `w_gbm=0.95` | **완료** — online_learner.py |
| **이상점 6-B**: 앙상블 전용 `PredictionCalibrator` 분리. 1m 검증으로 학습 | **완료** — ensemble_decision.py, main.py |
| **이상점 6-C**: 6호라이즌 ≤2 합의 시 conf×0.92 패널티 (보너스 미포함) | **완료** — ensemble_decision.py |
| **이상점 6-D**: `ENSEMBLE_WEIGHTS_CORR_ADJ` 30m 0.20→0.15 | **완료** — config/settings.py |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (84차)

| 파일 | 변경 내용 |
|---|---|
| `model/multi_horizon_model.py` | `_CW_30M = {FL:0.65, UP:1.18, DN:1.18}` |
| `learning/batch_retrainer.py` | `_CW_30M` 동일하게 수정 (학습기 일관성) |
| `learning/online_learner.py` | `ACCURACY_WINDOW=150`, `_ADJUST_EVERY=3`, `_bucket_learn_count`, `blend_with_gbm()` 초기 GBM 전용 모드 |
| `model/ensemble_decision.py` | `ensemble_calibrator` 추가, 합의도 패널티, Platt 보정 로직 개선, `record_ensemble_outcome()` |
| `config/settings.py` | `ENSEMBLE_WEIGHTS_CORR_ADJ` 30m 0.20→0.15 재배분 |
| `main.py` | `_bias_buf` 롤링 버퍼, `_ensemble_conf_cache`, STEP 1 Bias 통계 재작성, 앙상블 보정기 학습 연결 |

### 84차 실세션 확인 사항 (2026-05-23)

1. **이상점 3 개선**: 30m 예측에서 FL 상황 DN 오분류 발생 빈도 감소 확인
2. **이상점 4 개선**: 50분 정확도 급락 추이 완화 (연속 실패에도 SGD 비중 점진적 감소)
3. **이상점 5 개선**: `[Bias⚠] 30m 적중=?%(N건) DN편향! 75%+` 형식 로그 발생 확인
4. **이상점 6 개선**: conf ≥ 60% 도달하는 분봉 비율이 이전 대비 증가하는지 SIGNAL 로그 확인
5. **앙상블 보정기**: 1m 검증 시 `ensemble_calibrator.record()` 호출. 100건 누적 후 `is_fitted=True` 전환 확인

---

## 2026-05-22 (83차) — 탈진장 ATR ratio 문턱 재설계

### 배경

`MicroRegimeClassifier._classify()`에서 탈진장(`REGIME_EXHAUSTION`)과 급변장(`REGIME_VOLATILE`)이 동일한 ATR 문턱(`1.5`)을 공유. 급변장 판정이 먼저 실행되므로 탈진장은 사실상 dead code — 장중 한 번도 발동 불가. `ofi_reversal_speed` 조건도 `bear_exhaustion`이 이미 내포한 정보라 불필요한 추가 차단 역할.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `ATR_EXHAUSTION_MULT = 1.5` → `ATR_EXHAUSTION_MIN = 1.2` (독립 하한) | **완료** |
| exhaustion 구간: `1.2 ≤ atr_ratio < 1.5` (급변장과 겹침 없음) | **완료** |
| 양방향 대칭: `bull_exhaustion` 파라미터 추가 (SHORT MR 탈진 포착) | **완료** |
| `ofi_reversal_speed` 파라미터·조건 제거 (중복 필터) | **완료** |
| `main.py` 호출부 동기화 (`bull_exhaustion` 추가, `ofi_reversal_speed` 제거) | **완료** |
| 실세션 확인 | **미완료** — 2026-05-23 탈진장 로그 첫 발화 확인 필요 |

### 수정 파일 (83차)

| 파일 | 변경 내용 |
|---|---|
| `collection/macro/micro_regime.py` | `ATR_EXHAUSTION_MIN=1.2`, `push_1m_candle`·`_classify` 파라미터 재설계, exhaustion_conds 독립 구간 + 양방향 |
| `main.py` | `push_1m_candle()` 호출부: `bull_exhaustion` 추가, `ofi_reversal_speed` 제거 |

---

## 2026-05-22 (82차) — Layer 2 인트라데이 게이트 UI 패널 + L2 토글 영속성 및 즉시 적용

### 배경

Layer 2 IntradayTacticalRegime이 코드로 구현·통합(78차)되었으나, 대시보드에서 레짐 상태나 7개 지표 발동 여부를 확인할 방법이 없었음. L2 ON/OFF 토글도 재시작 시 초기화되고 장중 적용이 안 되는 문제 존재.

### 현재 상태

| 항목 | 상태 |
|---|---|
| 진입 관리 탭 Pre-flight 패널 좌우 양분 (5:6) | **완료** |
| Layer 2 상태 카드 (ON/OFF 버튼 + 레짐 색상 + 전환 레이블) | **완료** |
| Layer 2 7개 지표 표시 (발동 항목 빨간색 강조) | **완료** |
| Layer 2 조건 체크 로그 (진입허용·신뢰도강화·사이즈축소·복귀체크) | **완료** |
| L2 게이트 설정 영속성 (ui_prefs.json `layer2_gate_enabled`) | **완료** |
| L2 토글 장중 즉시 적용 — 3개 게이팅 포인트 `_l2_gate_on` 분기 | **완료** |
| `update_layer2(status_dict)` → main.py 파이프라인 연결 | **미완료** — STEP 6 또는 STEP 9에서 호출 코드 추가 필요 |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (82차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | Layer 2 패널 3단 UI, `is_layer2_gate_enabled()`, `update_layer2()`, 영속성 메서드, `sig_layer2_gate_toggled` |
| `main.py` | `_l2_gate_on` 분기 (3개 게이팅 포인트), `_on_layer2_gate_ui_toggled` 핸들러, 시그널 연결 |

---

## 2026-05-22 (81차) — Platt 보정 기동 사전 fit + 앙상블 2차 압축

### 배경

GBM 과신 출력(99.9% 확신 → 실제 40%)의 근본 원인: `horizon_calibrator`가 매 기동마다 0샘플 fresh 상태로 시작. DB에 24,626건의 검증 예측이 있어도 로드 코드가 없어 첫 ~100 tick 동안 보정이 비활성. 제안된 코드에는 4가지 추가 버그도 있었음.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `_preload_horizon_calibration()` 신규 메서드 | **완료** — 기동 시 DB 18,000건 로드 + `fit_all()` |
| `ensemble.calibrator` 주입 | **완료** — `main.py __init__` 에서 `self.ensemble.calibrator = self.horizon_calibrator` |
| `EnsembleDecision.__init__` `self.calibrator = None` | **완료** |
| Platt 보정 블록 위치 수정 | **완료** — stuck-breaker 후, **grade 계산 전** 삽입 |
| `confidence_raw` 필드 추가 | **완료** — `result` dict에 보정 전 원본 보존 |
| `transform()` → `calibrate()` 버그 수정 | **완료** |
| 실세션 확인 | **미완료** — 2026-05-23 기동 시 확인 필요 |

### 수정 파일 (81차)

| 파일 | 변경 내용 |
|---|---|
| `model/ensemble_decision.py` | `self.calibrator = None`, Platt 보정 블록 (grade 전), `confidence_raw` |
| `main.py` | `_preload_horizon_calibration()` 신규, `ensemble.calibrator` 주입 |

---

## 2026-05-21 (76~80차) — TrendPersistenceGate 대칭 구현 + Layer 2 통합 + 대시보드

### 배경

72차에서 방향 비대칭 편향 6종 수정 완료 후, 원웨이 추세장(상승/하락 한 방향으로 쭉 가는 날) 진입 부재 문제를 해결하기 위해 TrendPersistenceGate를 설계·구현·통합함.

### 76차 — CVD 단조성 비율 피처 추가

| 항목 | 상태 |
|---|---|
| `cvd_monotone_ratio` 피처 | **완료** — CVD 최근 20개 값 중 상승 이동 비율 (0~1) |
| `_cvd_history: deque(maxlen=21)` | **완료** — feature_builder 초기화에 추가 |
| GBM 피처 입력 | **완료** — 추세장 명시적 신호로 GBM 학습 지원 |

### 77차 — TrendPersistenceGate UP-only 최초 통합

| 항목 | 상태 |
|---|---|
| `TrendPersistenceGate` import | **완료** — `main.py` line ~104 |
| `self.trend_gate` 초기화 | **완료** — `__init__` line ~190 |
| STEP 6 TrendGate 블록 | **완료** — UP streak 활성 시 해당 방향 actual_min_conf 완화 |
| `reset_daily()` | **완료** — 일일 마감 라인 ~4182 |

### 78차 — Layer 2 IntradayTacticalRegime 완전 통합

| 항목 | 상태 |
|---|---|
| `min_conf_adjust()` 적용 | **완료** — DAY_RISK_OFF +5%p, CRASH +12%p (TrendGate 이후 적용) |
| `size_mult()` 적용 | **완료** — DAY_RISK_OFF ×0.5, CRASH ×0.3 (Toxicity gate 이후) |
| CRASH A등급 숏 예외 | **완료** — `allow_crash_grade_a_short()` + A등급 조건 조합 |

### 79차 — TrendPersistenceGate DOWN 대칭 구현

| 항목 | 상태 |
|---|---|
| UP/DN 듀얼 streak | **완료** — `_up_streak` / `_dn_streak` 독립 카운터 |
| DOWN 조건 | **완료** — `above_vwap=0 AND cvd_direction=-1` |
| hard_break 비대칭 | **완료** — UP=-300, DN=+200 (숏스퀴즈가 더 빠르고 파괴적) |
| return dict 변경 | **완료** — `up_active/up_streak/dn_active/dn_streak/min_conf_override` |

### 80차 — 대시보드 등급카드 깜빡임 UI

| 항목 | 상태 |
|---|---|
| `_trend_blink_timer` (600ms) | **완료** — `EntryPanel.__init__` |
| `_ens_grade_frame` / `_chk_grade_frame` 저장 | **완료** — `_build()` 루프 내 |
| `_on_trend_blink_tick()` | **완료** — UP=녹색(#3FB950), DN=오렌지(#D29922) 깜빡임 |
| `set_trend_gate_mode(mode)` | **완료** — EntryPanel + MainDashboard 위임 |
| main.py `set_trend_gate_mode()` 호출 | **완료** — STEP 6 TrendGate 블록 후 |

### 실세션 확인 사항 (2026-05-22)

1. UP streak 발동: `[TrendGate] UP 추세 지속 모드 ON (streak=10)` 로그 확인
2. DN streak 발동: `[TrendGate] DN 추세 지속 모드 ON (streak=10)` 로그 확인
3. 등급 카드 깜빡임: UP 활성→녹색, DN 활성→오렌지, 비활성→기본색 복원
4. Layer 2 min_conf_adjust: `[IntradayRegime] DAY_RISK_OFF — min_conf +5%p → 0.55` 형식 로그
5. Layer 2 size_mult: `[IntradayRegime] DAY_RISK_OFF 사이즈 축소 ×0.5 → N계약` 로그
6. CRASH A등급 숏 예외: `[IntradayRegime] CRASH — A등급 숏 추세추종 예외 허용` 로그

### 수정 파일 (76~80차)

| 파일 | 변경 내용 |
|---|---|
| `features/feature_builder.py` | `cvd_monotone_ratio` 피처 추가 |
| `strategy/entry/trend_persistence.py` | UP-only → UP+DN 듀얼 streak 전면 재작성 |
| `main.py` | TrendGate import·초기화·STEP6·reset_daily, Layer2 min_conf_adjust·size_mult·CRASH예외 |
| `dashboard/main_dashboard.py` | 등급 카드 깜빡임 (UP=녹, DN=오) + set_trend_gate_mode |

---

## 2026-05-21 (73차) — 레짐 확정 08:58 2단계 분리

### 배경

매일 08:55 첫 macro fetch에서 `MacroFetcher._first_fetch_done` 메커니즘에 의해
SP500·KRW chg가 항상 0.0으로 나옴. 그 직후 레짐을 확정하면 VIX 단독 결정 구조가 됨.
2회차 fetch(08:58~)에서 실제 값이 나오지만 레짐은 이미 고정된 상태였음.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `pre_market_setup()` 1단계화 | **완료** — seed fetch + PreRetrain만, 레짐 확정 제거 |
| `_pre_market_stage2()` 신규 | **완료** — 08:58 2회차 fetch + 레짐 확정 + 대시보드 + 알림 |
| `_heartbeat` 2단계 분리 | **완료** — stage1(08:55) / stage2(08:58~09:05) 조건 분리 |
| 실세션 검증 | **미완료** — 2026-05-22 장중 확인 필요 |

### 수정 파일 (73차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `pre_market_setup()`: 레짐 확정 로직 제거, seed fetch + PreRetrain만 |
| `main.py` | `_pre_market_stage2()` 신규 — 2회차 fetch + 레짐 확정 |
| `main.py` | `_heartbeat`: `_pre_market_stage1_done` 플래그 추가, 08:58 stage2 조건 삽입 |
| `main.py` | `connect_broker()` + 일일 마감: `_pre_market_stage1_done = False` 리셋 추가 |

### 변경 전후 타임라인

```
[변경 전]
08:55  pre_market_setup()
         → seed fetch (SP500=0%, KRW=0%)
         → 레짐 확정 (VIX만 반영) ← 문제
         → PreRetrain 시작
         → realtime 구독 시작

[변경 후]
08:55  pre_market_setup() [1단계]
         → seed fetch (SP500=0%, KRW=0%)
         → PreRetrain 시작
         → realtime 구독 시작

08:58  _pre_market_stage2() [2단계]
         → manual_fetch() 강제 2회차
         → 레짐 확정 (SP500·KRW 실수치 반영) ← 개선
         → 대시보드 업데이트
         → notify_premarket_ready()
```

### 실세션 확인 사항

1. `08:55:XX [System] 매크로 seed fetch 완료 — 레짐 확정은 08:58 2단계로 연기` 로그 확인
2. `08:58:XX [System] 매크로 수집 완료 | VIX=XX SP500=%+.2f%% KRW=%+.2f%%` — 실수치 확인 (SP500≠0.00%)
3. `08:58:XX [System] 레짐 확정: XXX | ...` 로그 확인
4. GAP_OPEN 구간(09:00~09:05) 진입 전에 레짐이 정상 확정됐는지 확인

---

## 2026-05-21 (72차) — 방향 비대칭 편향 6종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| OFI 역전 신호 양방향화 | **완료** — `bull_reversal_signal` + `bear_reversal_signal` 분리, 구 `ofi_reversal_signal` deprecated |
| CVD 탈진 양방향화 | **완료** — `bear_exhaustion` + `bull_exhaustion` 분리, 구 `cvd_exhaustion`/`exhaustion` deprecated |
| prev_bar_direction 3-state | **완료** — `prev_bar_bullish: bool` → `prev_bar_direction: int`(+1/0/-1), 도지 양쪽 불통과 |
| PCR 극단값 양방향화 | **완료** — `pcr_extreme_bearish` + `pcr_extreme_bullish`(≤0.67) + `pcr_extreme_signed`(연속값) 추가 |
| S&P500 레짐 임계값 대칭화 | **완료** — `< -1.0` → `< -0.5` (상승 +0.5%와 대칭) |
| RL HOLD 페널티 제거 | **완료** — `hold_penalty = 0.0` (CB·체크리스트 외부 제어와 중복 제거) |
| 실세션 검증 | **미완료** — 2026-05-22 장중 새 신호 동작 확인 필요 |
| deprecated 피처 제거 | **보류** — 모델 재훈련 후 구 피처 수렴 확인 뒤 제거 예정 |

### 수정 파일 (72차)

| 파일 | 변경 내용 |
|---|---|
| `features/technical/cvd_exhaustion.py` | `bear_exhaustion` + `bull_exhaustion` 양방향 탈진 계산 추가, 구 alias 유지 |
| `features/technical/ofi_reversal.py` | `bull_reversal_signal` + `bear_reversal_signal` 분리, 구 `signal` deprecated |
| `features/feature_builder.py` | 신규 6개 피처 등록 + 구 deprecated 피처 alias 유지 |
| `strategy/entry/checklist.py` | 파라미터 `bear_exhaustion` + `bull_exhaustion` 분리, `prev_bar_direction` int 3-state |
| `main.py` | 체크리스트 호출 파라미터 갱신, `prev_bar_direction` 계산 인라인 추가 |
| `collection/macro/micro_regime.py` | `cvd_exhaustion` → `bear_exhaustion` 파라미터 변경 |
| `challenger/variants/vwap_reversal.py` | `cvd_exhaustion` → `bear_exhaustion` (하락 압력 소진 의미 명확화) |
| `challenger/variants/exhaustion_regime.py` | `cvd_exhaustion` → `bear_exhaustion` 피처 조회 변경 |
| `collection/options/pcr_store.py` | `PCR_EXTREME_BULLISH_THRESHOLD=0.67` 신규, `pcr_extreme_bearish/bullish/signed` 추가 |
| `features/options/option_features.py` | 신규 3개 PCR 극단 피처 pass-through, `empty()` 갱신 |
| `collection/macro/regime_classifier.py` | SP500 하락 임계값 `< -1.0` → `< -0.5` |
| `learning/rl/reward_design.py` | HOLD 페널티 `0.001` → `0.0` 제거 |

### SHORT MR 핵심 수정 (의미론 오류)

```python
# 수정 전 (버그): SHORT MR에 하락 압력 소진 조건 → 의미 역전
if vwap_position > 1.5 and bear_exhaustion > 0.0:
    entry_mode = "MEAN_REVERSION"

# 수정 후: SHORT MR에 상승 압력 소진 조건 → 의미 정확
if vwap_position > 1.5 and bull_exhaustion > 0.0:
    entry_mode = "MEAN_REVERSION"
```

---

## 2026-05-21 (71차) — 자동진입관리 UI 카드 구조 개편

### 현재 상태

| 항목 | 상태 |
|---|---|
| 자동진입관리 패널 카드 구조 | **완료** — 앙상블 등급·체크리스트 등급·최종진입 3카드 분리 |
| 레이아웃 빈 공간 | **해소** — QGridLayout → VBox+HBox 재구성 |
| 최종진입 깜박임 | **구현** — 600ms QTimer, 진입 조건 시 녹색 테두리 blink |
| 수량 카드 균등 폭 | **완료** — stretch=1 균등 분배 |

### 수정 파일 (71차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | EntryPanel: 신뢰도→앙상블등급 카드, 진입등급→체크리스트등급 라벨, 최종진입 카드 신규, 레이아웃 재구성, blink 타이머 추가 |
| `main.py` | `update_entry()` 호출에 `ensemble_grade`, `checklist_grade`, `final_entry` 파라미터 추가 |

### 카드별 데이터 소스

| 카드 | 소스 |
|---|---|
| 앙상블 등급 | `decision["grade"]` (EnsembleDecision, 게이트 적용 전) |
| 체크리스트 등급 | `_cr["grade"]` (EntryChecklist, 게이트 적용 전 순수 체크리스트 결과) |
| 최종진입 | `direction!=0 AND _final_grade in ("A","B")` (모든 게이트 적용 후) |

---

## 2026-05-20 (69차) — signal() TypeError ERR-FATAL 수정 + traceback 로깅 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 68차 개선 3항목 실세션 검증 (11:46:31~) | **완료** — ERR-FATAL 소멸·신뢰도 미달 로그 정상·watchdog 거짓 경보 없음 |
| `signal() takes 2 positional arguments but 3 were given` | **수정 완료** — 3개 파일 수정 |
| ERR-FATAL 발생 시 traceback 가시성 | **개선** — RECOVERABLE·DEGRADED·FATAL 모두 traceback.format_exc() 추가 |
| 69차 수정 실세션 재검증 | **미완료** — 2026-05-21 장중 확인 필요 |

### 수정 파일 (69차)

| 파일 | 변경 내용 |
|---|---|
| `utils/error_policy.py` | `import traceback` 추가. RECOVERABLE·DEGRADED·FATAL 3케이스 모두 `\n%s, traceback.format_exc()` 로깅 |
| `scripts/validate_health_policy_hotreload.py` | `_Collector.signal(self, msg)` → `_Collector.signal(self, msg, level="INFO")` — monkey-patch 중 TypeError 방지 |
| `main.py` | `_hc_block`·IntradayRegime 롱차단·숏차단 3곳 `log_manager.signal(msg, "WARNING")` → `log_manager.signal(msg, level="WARNING")` keyword 인수 변경 |

### 버그 핵심 구조 (수정 전)

```
validate_health_policy_hotreload.py 실행 중:
  log_manager.signal = collector.signal   # monkey-patch
  collector.signal(self, msg)             # level 파라미터 없음

main.py pipeline:
  IntradayRegime CRASH + direction=LONG →
    log_manager.signal(msg, "WARNING")   # positional 3번째 인수
    → TypeError: takes 2 positional arguments but 3 were given
    → ERR-FATAL minute_pipeline 매분 크래시
```

### 운영 메모

- traceback 추가로 다음 ERR-FATAL 시 WARN.log에 파일명·라인 번호 포함 → 디버깅 속도 대폭 향상
- `validate_health_policy_hotreload.py`는 개발 스크립트. 장중 실행 시 monkey-patch 기간이 pipeline 실행과 겹치지 않도록 주의

---

## 2026-05-20 (68차) — minute_pipeline ERR-FATAL 실제 근본 원인 최종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| 11:04 재시작 자체 | **정상** — tick/hoga/realtime 구독 완료, 데이터 유입 확인 |
| `minute_pipeline` 치명 예외 원인 | **최종 규명 완료** — `checklist.py:95` `entry_mode` 할당 전 참조 (UnboundLocalError) |
| 1차 수정 81e0784 (`main.py`) | **오진단** — UI 모드 변수(auto/hybrid/manual)를 수정했으나 실제 버그는 별개 파일 |
| watchdog 90초/150초 경보 | **원인 규명 완료** — 파이프라인 예외로 `notify_pipeline_ran()` 미도달 → 허위 지연 경보 |
| `checklist.py` 최종 수정 | **완료** — `entry_mode = "TREND_FOLLOW"` 초기화를 `checks = {}` 바로 다음으로 이동 |
| 실세션 재검증 | **미완료** — 2026-05-21 장중 grade=X 분봉에서 ERR-FATAL 소멸 확인 필요 |

### 수정 파일 (68차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` (81e0784, 오진단) | `entry_mode="manual"` 기본값 추가 — UI 진입모드 변수 수정 (실제 버그와 무관) |
| `strategy/entry/checklist.py` | `entry_mode = "TREND_FOLLOW"` 초기화를 `checks = {}` 바로 뒤(line 77)로 이동 — 신뢰도 미달 조기 반환(line 89~96)보다 선행 할당 보장 |

### 버그 핵심 구조 (수정 전)

```
checklist.py evaluate():
  checks = {}
  if not checks["2_confidence"]:   # conf=43.4% < 58% → 항상 True
    return {"entry_mode": entry_mode}  # line 95: 미할당 참조 → UnboundLocalError
  entry_mode = "TREND_FOLLOW"      # line 100: 할당이 여기 있어 로컬 변수로 지정됨
```

### 운영 메모

- `conf < min_conf` 인 분봉(X등급) 전체에서 100% 재현. 장 중 신뢰도 낮은 구간에서 파이프라인이 매분 예외 종료.
- watchdog "분봉 수신 지연 의심" 문구는 분봉 미수신이 아닌 예외 중단 케이스에서도 발생. 추후 분리 표기 개선 검토.

---

## 2026-05-20 (67차) — 장중 로그 분석 + 이상점 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| online_learner scaler partial_fit 버그 수정 | **완료** — 매 샘플마다 `partial_fit()` 호출로 변경 |
| SYSTEM 로그 CB③30m 명확화 | **완료** — `정확도=X%` → `CB③30m=X%(N건)` / `집계중` 표시 |
| horizon별 [Bias] 편향 진단 로그 추가 | **완료** — STEP 1 직후 호라이즌별 UP/FL편향 자동 감지 |
| conf 클립 DEBUG 로그 추가 | **완료** — `[Calib] clipped` DEBUG 로그 |
| SYSTEM 정확도=0.0% 원인 규명 | **완료** — 세션 초반 30분 필터 공백(정상) + 30m 실제 정확도 낮음 |
| 5m bullish bias / 30m flat bias 근본 수정 | **미완료** — [Bias] 로그로 관찰 후 calibration 재보정 필요 |
| 6분 주기 처리시간 스파이크 원인 | **미완료** — GBM 재학습 연관 추정, 단계별 타이머 관찰 필요 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (67차)

| 파일 | 변경 내용 |
|---|---|
| `learning/online_learner.py` | scaler `partial_fit()` 매 샘플마다 호출 (조건 제거) |
| `dashboard/main_dashboard.py` | `update_system_status()` `cb3_samples` 파라미터 추가. SYSTEM 로그 `CB③30m=X%(N건)` 형식 |
| `main.py` | `update_system_status(cb3_samples=...)` 전달 추가. `[Bias]` horizon 편향 진단 로그 (STEP 1 직후). conf 클립 시 `[Calib] clipped` DEBUG 로그 |

---

## 2026-05-20 (66차) — SHAP 중요도·파라미터 상관계수 이상점 점검 및 4종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| RESTORED값 LIVE 오인 버그 (임계값 30 vs 100 불일치) | **완료** — `update()` bool 반환 + `_refresh_shap_state()` 임계값 `SHAP_MIN_DATA_POINTS`로 통일 |
| 구버전 `_update_shap_dashboard()` 중복 메서드 제거 | **완료** — 데드코드 + 인코딩 깨진 문자열 포함 블록 삭제 |
| `_shap_feature_window` 재시작 후 미복원 (30분 공백) | **완료** — `_restore_analysis_buffers()`에 DB 복원 추가 |
| `_build_param_corr_string()` `short_names` 인코딩 깨짐 | **완료** — 정상 UTF-8 한글로 교체 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (66차)

| 파일 | 변경 내용 |
|---|---|
| `learning/shap/shap_tracker.py` | `update()` 반환형 → `bool` (실계산 True, 데이터 부족·실패 False) |
| `main.py` | `SHAP_MIN_DATA_POINTS` import 추가 |
| `main.py` | `_refresh_shap_state()`: 임계값 30→`SHAP_MIN_DATA_POINTS`(100), `update()` 반환값으로 `_live_shap_ready` 제어 |
| `main.py` | 구버전 `_update_shap_dashboard()` (line 820~861) 제거 (데드코드) |
| `main.py` | `_restore_analysis_buffers()`: `_shap_feature_window` DB 데이터로 복원 추가 |
| `main.py` | `_build_param_corr_string()`: `short_names` 키 인코딩 깨짐 → 정상 한글 교체 |

### 핵심 버그 흐름 (수정 전)

```
재시작 후 30개 live 분봉 쌓임
  → _refresh_shap_state(): len(window)=30 >= 30 → update() 호출
  → shap_tracker.update(): len(X)=30 < 100 → return (계산 안 함)
  → get_current_ranking() → 복원값 반환
  → _live_shap_ready = True  ← 버그: 실계산 없이 True
  → 대시보드: 복원값이 "LIVE" 표시
  → save_shap_scores(): 복원값을 LIVE로 DB 저장
```

### 66차 실세션 확인 사항 (2026-05-21)

1. DB에 100건 이상 raw_features가 있으면 기동 직후 SHAP live 계산 성공하는지 확인
2. 100건 미만 구간에서 대시보드에 LIVE 표시 안 나타나는지 확인
3. 파라미터 상관계수 레이블 정상 한글 표시(CVD, VWAP, 외인콜 등) 확인

---

## 2026-05-20 (65차) — 신뢰도·VWAP 흐름 분석 + 진입 체크리스트 7종 개선

### 현재 상태

| 항목 | 상태 |
|---|---|
| 신뢰도 강제 X 게이트 | **완료** — `2_confidence` 실패 시 CORE와 동일하게 즉시 X 반환 |
| min_conf 단일 출처 통일 | **완료** — `actual_min_conf = max(레짐 기준, 시간대 기준)`. 체크리스트·대시보드 전 구간 적용 |
| VWAP 역추세 예외 분기 활성화 | **완료** — `checklist.evaluate()` 호출에 `cvd_exhaustion`·`micro_regime` 추가. MEAN_REVERSION 분기 실제 작동 |
| UI 신뢰도 레이블 동적화 | **완료** — `_conf_chk_name_label` 저장 → 매분 `"신뢰도 ≥ {min_conf:.0%}"` 갱신 |
| CVD·OFI 중립(0) 차단 | **완료** — `>= 0` → `> 0` (중립 신호가 CORE 통과하던 허점 제거) |
| 외인 방향 AND 강화 | **완료** — `or` → `and`. 콜/풋 양수 AND 상대우위 모두 필요 |
| 손실률 분모 동적화 | **완료** — `50_000_000` → `max(_ts_current_sizer_balance(self), 50_000_000)` |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (65차)

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | 신뢰도 강제 X 반환 블록 추가 + CVD·OFI `> 0`/`< 0` 수정 + 외인 방향 `and` |
| `strategy/entry/time_strategy_router.py` | `get_zone_min_confidence(zone)` 헬퍼 추가 |
| `main.py` | `get_zone_min_confidence` import + `actual_min_conf` 계산 (decision 직후) + `checklist.evaluate()` cvd_exhaustion·micro_regime 추가 + 손실률 분모 동적화 |
| `dashboard/main_dashboard.py` | `_conf_chk_name_label` 저장 + `update_data()` 레이블 동적 갱신 |

### min_conf 흐름 (65차 이후)

```
ensemble_decision.py
  → decision["min_conf"] = REGIME_MIN_CONFIDENCE[레짐]
    (RISK_ON=0.52, NEUTRAL=0.58, RISK_OFF=0.65)

main.py (decision 직후)
  → actual_min_conf = max(decision["min_conf"], get_zone_min_confidence(time_zone))
    (OPEN_VOLATILE=0.63, GAP_OPEN=0.67, STABLE_TREND=0.58, ...)

checklist.evaluate(min_confidence=actual_min_conf)
  → 신뢰도 미달 시 즉시 X 반환

dashboard.update_data(min_conf=actual_min_conf)
  → 신뢰도 색상 + 레이블 모두 actual_min_conf 기준
```

---

## 2026-05-20 (64차) — 09:34 재시작 점검 + 3종 이상점 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| 장중 재시작 warmup 재학습 CB⑤ | **완료** — `connect_broker()` 장중(09:00~15:10) 완료 시 즉시 GBM 재학습 시작. 첫 파이프라인 STEP 3 skip 보장 |
| `_gbm_retrain_running` 초기화 | **완료** — `__init__`에 `False` 명시적 초기화. `getattr` 방어 패턴 불필요 |
| `_last_close` 초기화 | **완료** — `__init__`에 `0.0` 추가. `_poll_option_chain` QTimer 콜백에서 사용 |
| OptionChain BlockRequest 루프 파이프라인 분리 | **완료** — STEP 4 `refresh()` → `get_features()` 캐시 읽기만. QTimer 300s 별도 폴링 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (64차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `connect_broker()`: 장중 재시작 즉시 GBM warmup 재학습 스레드 시작 블록 추가 |
| `main.py` | `__init__`: `_gbm_retrain_running: bool = False`, `_last_close: float = 0.0` 초기화 |
| `main.py` | `run_minute_pipeline()` STEP 4: `refresh()` 제거, `self._last_close = close` 추가 |
| `main.py` | `_poll_option_chain()` QTimer 콜백 신규 추가 |
| `main.py` | `daily_close()`: `_option_chain_timer.stop()` 추가 |
| `strategy/runtime/broker_runtime_service.py` | `_option_chain_timer` QTimer 생성 + `ensure_market_open_runtime_started()`에서 `start(300_000)` |

### OptionChain QTimer 분리 구조 (64차 신규)

```
장 시작(09:00) → ensure_market_open_runtime_started()
  → _option_chain_timer.start(300_000)   # 5분마다 메인 스레드 QTimer

STEP 4 (매분):
  → option_chain_snap.get_features()     # 캐시 읽기, 0ms

_poll_option_chain() (매 5분, QTimer 콜백):
  → option_chain_snap.refresh(spot=_last_close)  # BlockRequest 루프 (파이프라인 외부)
  → dashboard.update_option_chain()
```

---

## 2026-05-20 (63차) — 파이프라인 크래시 버그 4종 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| log_manager.signal() TypeError 크래시 | **완료** — `level="INFO"` 기본값 추가. 09:14 이후 매분 파이프라인 재귀 실패 해소 |
| GBM 재학습 08:55 분리 | **완료** — `pre_market_setup()` 끝에서 PreRetrain 블록. 09:00 첫 파이프라인 CB⑤ 충돌 방지 |
| PCR 장초반 극단값 — PCRStore 방어 | **완료** — `PCR_MIN_CALL_ABS=1000` skip, `PCR_MAX=4.0` cap. opt_pcr_slope_norm=-5.87 매분 반복 해소 |
| quality_investor_age_sec z=+45 방어 | **완료** — `min(..., 300.0)` cap. 09:00 첫 파이프라인 z-score 폭발 방지 |
| 실세션 동작 확인 | **미완료** — 다음 장(2026-05-21) 기동 필요 |

### 수정 파일 (63차)

| 파일 | 변경 내용 |
|---|---|
| `logging_system/log_manager.py` | `signal(msg, level="INFO")` — level 기본값 추가. `log_manager.signal(msg, "WARNING")` 3곳 호출 복구 |
| `main.py` | `pre_market_setup()` 끝에 `[PreRetrain]` 블록 추가. 08:55 GBM 재학습 트리거 |
| `collection/options/pcr_store.py` | `PCR_MIN_CALL_ABS=1000`, `PCR_MAX=4.0` 추가. `update()` call_abs 최소값 방어 + PCR 상한 적용 |
| `features/feature_builder.py` | `quality_investor_age_sec = min(..., 300.0)` cap 추가 |

### 63차 실세션 확인 사항 (2026-05-21)

1. **[PreRetrain]** SYSTEM 로그: `08:55:XX [PreRetrain] 08:55 GBM 사전 재학습 시작` 로그 발생
2. **CB⑤ 없음**: 09:00 첫 파이프라인 처리시간 < 5000ms (PreRetrain 이미 진행 중 → STEP 3 skip)
3. **opt_pcr_slope_norm 정상화**: 09:02부터 `-5.87` 반복 사라짐 (또는 pcr_available=0으로 중립)
4. **파이프라인 무크래시**: `[복구 실패]` 로그 없음. 09:14 이후에도 정상 흐름
5. **IntradayRegime=CRASH 차단 로그**: 이제 TypeError 없이 `[IntradayRegime] CRASH — 신규 롱 금지` 정상 출력
6. **quality_investor_age_sec**: 09:00 첫 파이프라인 z-score < +15 (min(840, 300) = 300 → z 정상화)

### 오늘(5/20) 확인된 잠재 버그 (미수정)

| 버그 | 증상 | 우선순위 |
|---|---|---|
| 잔고 TR 파싱 `rows=0` | `[BrokerSync] 잔고 rows=0` — 포지션 미인식 가능성 | 실전 전환 전 필수 수정 |
| 프로그램 매매 TR | 사용 TR 미확인 상태 | 실전 전환 전 필수 확인 |

---

## 2026-05-19 (62차) — 매크로 레짐 종합 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| IntradayTacticalRegime (Layer 2) | **완료** — `intraday_tactical_regime.py` 신규. NORMAL/DAY_RISK_OFF/CRASH |
| main.py Layer 2 파이프라인 통합 | **완료** — 매분 update + 진입 차단 + reset_daily |
| micro_regime ATR 둔감 수정 | **완료** — 2.0→1.5 + z_warn≥3 복합 조건 |
| macro_fetcher 첫 fetch=0 버그 | **완료** — `_first_fetch_done` 분기로 NEUTRAL 편향 제거 |
| RegimePanel 레짐 모니터 위젯 | **완료** — Layer1/2/Micro 3배지 + 진입정책 + 이력 로그 |
| "🌐 레짐" 대시보드 탭 | **완료** — `mid_tabs` 탭 추가, Layer1·Micro 업데이트 훅 연결 |
| 실세션 동작 확인 | **미완료** — 다음 장 기동 필요 |

### 신규 파일 (62차)

| 파일 | 내용 |
|---|---|
| `collection/macro/intraday_tactical_regime.py` | IntradayTacticalRegime: DAY_RISK_OFF/CRASH 진입정책 분류기 |
| `dashboard/panels/regime_panel.py` | RegimePanel: 3계층 레짐 실시간 모니터 위젯 |

### 수정 파일 (62차)

| 파일 | 변경 내용 |
|---|---|
| `collection/macro/macro_fetcher.py` | `_first_fetch_done` 플래그. 초회 시딩 전용 경로 |
| `collection/macro/micro_regime.py` | ATR_VOLATILE_MULT 2.0→1.5, z_warn_count 파라미터, 복합 급변 조건 |
| `main.py` | IntradayTacticalRegime import·인스턴스·파이프라인·차단·reset |
| `dashboard/main_dashboard.py` | "🌐 레짐" 탭, `update_layer1/micro()` 훅 |

### Layer 2 정책 요약

| 레짐 | 롱 | 숏 | 사이즈 | 신뢰도보정 |
|---|---|---|---|---|
| NORMAL | 허용 | 허용 | ×1.0 | +0%p |
| DAY_RISK_OFF | **금지** | 허용 | ×0.5 | +5%p |
| CRASH | **금지** | **금지** | ×0.3 | +12%p |

### 62차 실세션 확인 사항

1. **"🌐 레짐" 탭**: Layer1/Layer2/Micro 3배지 정상 표시
2. **Layer 2 전환 로그**: `[IntradayRegime] NORMAL → DAY_RISK_OFF` (하락장 시)
3. **진입 차단 로그**: `[IntradayRegime] DAY_RISK_OFF — 신규 롱 금지`
4. **micro 급변장**: 장중 ATR 확대 구간에서 `급변장` 판정 확인
5. **macro_fetcher**: 2회차 fetch chg 실수치 (≠ 0.0) 로그 확인

---

## 2026-05-19 (61차) — CB HALT 분석 + 지표 버그 수정 + CB⑤ 재설계

### 현재 상태

| 항목 | 상태 |
|---|---|
| CB HALT 분석 (11:11~12:19) | **완료** — 50분정확도 26%→21% 하락, 15m/10m 역추세 고확신 연속 오답 패턴 |
| 예측 로그 direction 추가 | **완료** — `main.py` 실패 시 `예측=DN 실제=UP` 방향 정보 추가 |
| 정확도=0.0% 버그 수정 | **완료** — `update_system_status()` `accuracy=_acc30m` 전달 추가 |
| API지연=0ms 버그 수정 + CB⑤ 재설계 | **완료** — `record_pipe_latency()` 신규. 1초 경고·5초 PAUSE |
| 모델 AI 카드 하드코딩 버그 수정 | **완료** — `_model_vals` 참조 저장 + `update_model_cards()` 신규 + 매분 갱신 |
| 헬스 카드 "처리시간" 전환 | **완료** — HealthPanel·LogPanel 양쪽 레이블·툴팁·스파크라인 모두 |
| CB⑤ 테스트 추가 | **완료** — `tests/test_circuit_breaker.py` 2케이스 추가 |
| 실세션 동작 확인 | **미완료** — 다음 장 기동 필요 |

### 수정 파일 (61차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | `CB_PIPE_WARN_MS=1000`, `CB_PIPE_PAUSE_MS=5000` 추가. `HEALTH_LATENCY_WARN_MS` 2500→1000 |
| `safety/circuit_breaker.py` | `record_pipe_latency()` 신규. `CB_PIPE_WARN_MS·PAUSE_MS` import 추가 |
| `main.py` | `_pipe_t0` 타이머, `_pipe_ms` 계산, `record_pipe_latency` 연결. `record_api_latency` 제거. 예측 로그 direction 추가. `update_model_cards` 매분 호출. `accuracy=_acc30m` 전달 |
| `dashboard/main_dashboard.py` | `HealthPanel`: "처리시간" 전환·툴팁·내부 임계값(500→1000, 1000→5000). `LogPanel`: 동일. `update_model_cards()` 신규 (LogPanel + MireukDashboard). `_model_vals` 참조 저장 |
| `tests/test_circuit_breaker.py` | `record_pipe_latency` 경고·정지 2케이스 추가 |

### 61차 실세션 확인 사항

1. **처리시간 카드**: 6 운영 헬스 탭 "처리시간" 표시 + 툴팁 확인 (호버 시 임계값 안내)
2. **SYSTEM 로그**: `CB=NORMAL | 처리시간=Xms | 정확도=YY.Y%` 형식 확인
3. **모델 AI 카드**: 매분 `정확도(50분)·SGD비중·자가학습` 실시간 갱신 확인
4. **예측 로그**: `✗ 15m 예측 실패 (conf=73.9% 예측=DN 실제=UP)` 형식 확인
5. **CB⑤**: 파이프라인 1초 초과 시 `[CB⑤] 파이프라인 Xms 경고` 로그 발생 여부

---

## 2026-05-19 (60차) — 5/19 CB③ 심층분석 기반 안전장치 6종 + Shadow/Contrarian 구현

### 현재 상태

| 항목 | 상태 |
|---|---|
| 1순위: Mid-Conf Blind Spot Tracker | **완료** — `circuit_breaker.py` 60~85% 구간 7연속 오답 → strict 모드 발동 |
| 2순위: Brier Score 실시간 추적 | **완료** — `circuit_breaker.py` 이동평균(10건). >0.35 경고, >0.45 사이즈 50% 패널티 |
| 3순위: 재시작 루프 브레이커 | **완료** — `circuit_breaker.py` _daily_halt_count 2회→50%, 3회→완전관망 |
| 4순위: 장 시작 5분 DNA 진단 | **완료** — `safety/market_dna.py` 신규. 4항목 3/4 이상 이상 → dna_mult=0.25 |
| 5순위: CORE Health Score → Sizer 연동 | **완료** — `features/core_health.py` 신규. 4개 안전 배수 position_sizer 연결 |
| 6순위: Shadow Session 상태 머신 | **완료** — `safety/shadow_session.py` 신규. SHADOW→LIVE/BLOCKED 게이트 |
| 6순위: Contrarian Mode 상태 머신 | **완료** — `safety/contrarian_mode.py` 신규. 3조건 WATCHING→ARMED→ACTIVE |
| 6순위: 실험 게이트 대시보드 탭 | **완료** — `experiment_gate_panel.py` 신규 + main_dashboard "🧪 실험 게이트" 탭 |
| 파이프라인 전체 문서화 | **완료** — `docs/PIPELINE_FLOW.md` 신규. STEP 1~9 전체 흐름 |
| 실세션 동작 확인 | **미완료** — 다음 장 중 첫 기동 필요 |

### 수정 파일 (60차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | CB 신규 상수 9개 (Mid-Conf 3, Brier 3, HALT 2 + 기존) |
| `safety/circuit_breaker.py` | Mid-Conf·Brier·재시작루프 3종 추가. status/state_dict/reset 전체 반영 |
| `safety/market_dna.py` | **신규** — 장 시작 5분 DNA 진단기 |
| `safety/shadow_session.py` | **신규** — Shadow Session 상태 머신 (SHADOW/LIVE/BLOCKED) |
| `safety/contrarian_mode.py` | **신규** — Contrarian Mode 상태 머신 (WATCHING/ARMED/ACTIVE/CLEARED) |
| `features/core_health.py` | **신규** — CORE 피처 건강 점수 0~100 계산기 |
| `model/multi_horizon_model.py` | `last_z_warn_count` 노출, 예측 결과에 `extreme_count` 포함 |
| `strategy/entry/position_sizer.py` | 안전 배수 4종 파라미터 추가 (core_health/brier/restart/dna) |
| `dashboard/panels/experiment_gate_panel.py` | **신규** — Shadow + Contrarian 모니터 UI |
| `dashboard/main_dashboard.py` | "🧪 실험 게이트" 탭 mid_tabs 마지막에 추가 |
| `main.py` | MarketDNA·CoreHealth·Shadow·Contrarian 초기화·매분업데이트·Sizer연결·reset_daily |
| `docs/PIPELINE_FLOW.md` | **신규** — 매분 파이프라인 전체 흐름 문서 |

### 안전 배수 조합 (5/19 재현 시 예상값)

```
core_health_mult × brier_mult × restart_mult × dna_mult
= 0.5 × 0.5 × 0.5 × 0.25 = 0.031 → 사실상 0계약
```

### 다음 기동 확인 사항

1. **Mid-Conf 추적**: 60~85% 구간 오답 연속 시 `[CB] mid_conf_wrong_streak=N` 로그
2. **Brier Score**: 10건 이동평균 >0.35 → `[CB] Brier 경고`, >0.45 → `brier_size_mult=0.5`
3. **재시작 루프 브레이커**: 일별 halt 2회 차 → 사이즈 50%, 3회 차 → 완전관망
4. **MarketDNA**: 09:05에 `[DNA] score=N/4 → dna_mult=X` 로그
5. **CoreHealth**: 매분 `[CoreHealth] score=N → size_mult=X` 로그
6. **ShadowSession**: 09:40 이전 게이트 통과 → `[Shadow] → LIVE` 또는 `BLOCKED`
7. **ContrarianMode**: acc30m<25% 발생 시 `[Contrarian] ARMED` 상태 전환
8. **실험 게이트 탭**: mid_tabs 마지막 탭 정상 표시, 30초 주기 자동 갱신

---

## 2026-05-18 (58차) — 안전장치 6종 구현

### 현재 상태

| 항목 | 상태 |
|---|---|
| P0: PG+CB 상태 영속화 | **완료** — `to/from_state_dict()` 구현, `session_state.json`에 저장/복원 |
| P0: "상태유지" 체크박스 | **완료** — 모의투자/실서버 동일 행 우측. `ui_prefs.json` 연동 |
| P1-a: Restart Armistice | **완료** — 재시작 후 90초 + 브로커 sync ≥2회 clean 전까지 진입 차단 |
| P1-b: Position Integrity Checksum | **완료** — engine/broker/pending 삼각 검증, 불일치 2회 경보, 3회 진입 차단 |
| P2-b: Setup Expectancy Ledger | **완료** — trades.db 5컬럼 추가, 진입 컨텍스트 저장, INSERT 확장 |
| P2-b: 셋업 기대값 패널 | **완료** — `setup_expectancy_panel.py` 신규, mid_tabs "📊 셋업 기대값" 탭 추가 |
| P3-a: OnlineLearner 오염 학습 보호 | **완료** — stuck 분봉 SGD 학습 전체 스킵 |
| P3-b: Reverse Entry Clamp | **완료** — 청산 후 180초 반대 방향 진입 차단 |
| 5/19 실세션 동작 확인 | **미완료** — 최초 기동 필요 |

### 수정 파일 (58차)

| 파일 | 변경 내용 |
|---|---|
| `safety/circuit_breaker.py` | `to_state_dict()` / `from_state_dict()` |
| `strategy/profit_guard.py` | `to_state_dict()` / `from_state_dict()` |
| `strategy/runtime/session_recovery_service.py` | PG+CB 상태 복원 블록 |
| `utils/db_utils.py` | 셋업 태그 5컬럼 마이그레이션 |
| `main.py` | 안전장치 6종 전체 |
| `dashboard/main_dashboard.py` | `chk_state_persist` + `setup_expectancy_panel` 탭 |
| `dashboard/panels/setup_expectancy_panel.py` | 신규 생성 |

### 5/19 기동 확인 사항

1. **상태유지**: ProfitGuard/CB가 HALT 상태인 채로 재시작 → 상태 유지 확인 (`[Restore] ProfitGuard 상태 복원` / `[CB] 상태 복원` 로그)
2. **상태유지 Off**: 체크박스 해제 후 재시작 → PG/CB 초기화 확인
3. **Armistice**: 재시작 직후 signal 발생해도 진입 없음. 90초 경과 + sync 2회 후 진입 허용
4. **Integrity**: FLAT 진입 전 `[Integrity]` 로그 — mismatch=0, integrity_fail=0 확인
5. **Reverse Clamp**: 청산 직후 반대 신호 시 `[ReverseClamp] 진입 차단` 로그
6. **셋업 기대값 탭**: mid_tabs 마지막 탭 표시, 거래 데이터 없으면 빈 테이블 표시
7. **SGD stuck 가드**: ENTRY/EXIT stuck 분봉 STEP 2 로그에 `[SGD] stuck 발생 분봉 — N건 학습 스킵`

---

## 2026-05-18 (57차) — UI 체크박스 설정 유지 버그 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| B120 Fix: 체크박스 재시작 시 True 초기화 | **완료** — `_restore_ui_prefs` 내 `_on_symbol_changed` → `_update_symbol_label` 교체 |
| chk_slack 중복 시그널 제거 | **완료** — `main.py` L4128~4130 `stateChanged` → `_save_ui_prefs` 연결 제거 |
| 5/19 실세션 동작 확인 | **미완료** — 체크박스 해제 후 재시작 시 복원 여부 확인 |

### 수정 파일 (57차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `_restore_ui_prefs()` L7814: `_on_symbol_changed` → `_update_symbol_label` |
| `main.py` | L4128~4130: `chk_slack.stateChanged` → `_save_ui_prefs` 중복 연결 제거 |

### 5/19 확인 사항

1. 중패널_Auto·우패널_Auto 체크 해제 후 재시작 → 해제 상태로 복원되는지 확인
2. `ui_prefs.json`에 `mid_auto_enabled: false, right_auto_enabled: false` 유지되는지 확인

---

## 2026-05-18 (56차) — 상단 배지 5종 점검·수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| FLAT 배지 (`lbl_pos`) | **완료** — `update_position()`에서 LONG/SHORT/FLAT 색상 갱신 |
| 위클리 배지 (`lbl_cycle`) | **완료** — `_calc_cycle_badge()` 월/목 양방향, `[월]위클리`/`[목]위클리`/`[목]월간` 형식 |
| 감마스퀴즈 배지 (`lbl_gamma`) | **완료** — `_update_gamma_badge()` 추가, GEX 기반 3상태 판정, 초기값 "감마 —" |
| NEUTRAL 배지 (`lbl_regime`) | **완료** — 툴팁 "매분 갱신" 오류 수정 + `usd_krw` 인수 누락 수정 |
| L2 배지 (`lbl_l2_halt`) | **완료** — dead code 제거 + 툴팁 400만원 기준 명시 |
| 배지 실세션 동작 확인 | **미완료** — 5/19 장중 첫 확인 예정 |

### 수정 파일 (56차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `update_position()`: `lbl_pos` 갱신 추가 |
| `dashboard/main_dashboard.py` | `_calc_cycle_badge()`: 월/목 양방향 만기 계산 |
| `dashboard/main_dashboard.py` | `update_option_chain()` + `_update_gamma_badge()` 신규, 초기값 "감마 —" |
| `dashboard/main_dashboard.py` | `lbl_regime` 툴팁 "08:55 1회 수집 당일 고정" 수정 |
| `dashboard/main_dashboard.py` | `lbl_l2_halt` 툴팁 Tier4 400만원 명시 |
| `main.py` | `update_supply_macro()` 호출에 `usd_krw` 인수 추가 |
| `strategy/profit_guard.py` | `_tier.check()` dead code `if max_qty == 0:` 제거 |

### 5/19 기동 확인 사항

1. FLAT → LONG 진입 시 배지 색상 전환 (녹색=LONG, 빨강=SHORT, 회색=FLAT)
2. 위클리 배지: 오늘이 월요일(만기일) → `● [월]위클리 만기일` 표시
3. 09:05 이후 감마스퀴즈 배지: "감마 —" → "감마스퀴즈"/"감마플립"/"중립" 전환
4. 시스템 로그에서 `[Regime] ... | USD/KRW=±X.XX` (0.00이 아닌 실수치)

---

## 2026-05-18 (55차) — 옵션 체인 스냅샷 파이프라인 완성 + B115 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| OptionChainSnapshot 클래스 구현 | **완료** — `collection/options/option_chain_snapshot.py` |
| main.py STEP 4 통합 | **완료** — refresh·get_features·dashboard 업데이트 연결 |
| 대시보드 옵션 섹션 UI | **완료** — freshness bar + PCR/GEX 카드 5개 |
| B115 Fix: front month 만기 계산 | **완료** — `_filter_front_month` 2번째 목요일 기준 만기 달 skip |
| 옵션 체인 실데이터 검증 | **미완료** — 5/19 장중 첫 검증 예정 |

### 수정 파일 (55차)

| 파일 | 변경 내용 |
|---|---|
| `collection/options/option_chain_snapshot.py` | 신규 — OptionChainSnapshot 클래스 (5분 폴링 PCR/ATM OI/GEX) + B115 _filter_front_month 만기 계산 |
| `main.py` | import 추가, `__init__` 초기화, `connect_broker` initialize(), STEP4 refresh/get_features/dashboard update, `reset_daily()` |
| `dashboard/main_dashboard.py` | DivergencePanel 옵션 섹션 + freshness bar + update_option_chain() + MainDashboard 위임 메서드 |

### 5/19 기동 확인 사항

1. `[OptionChain] COM 초기화 완료` — connect_broker() 완료 직후 로그
2. `[OptionChain] front month=2606 (만기=2026-06-11)` — B115 수정 동작 확인
3. 09:05 이후 `[OptionChain] 갱신 ... avail=True` — 실데이터 수집 확인
4. 대시보드 하단 옵션 섹션 실수치 표시 (PCR≠1.000, GEX≠0.0B)

---

## 2026-05-18 (54차) — B112/B114 개선

### 현재 상태

| 항목 | 상태 |
|---|---|
| B112 Fix: stale broker_sync_reason 클리어 | **완료** — FLAT 전환 시 `_broker_sync_last_error = "flat after exit"` |
| B114 진단: IntrabarTPSchedule 로그 추가 | **완료** — QTimer 스케줄 시 price/pos/p1p2p3 WARN 출력 |
| B114 진단: IntrabarTPCheck 가드 로그 추가 | **완료** — pending 존재/FLAT/price=0 각 케이스 WARN 출력 |
| B114 근본 원인 수정 | **미완료** — 5/19 세션 로그 확인 후 원인 특정 필요 |
| B113: ProfitGuard 재시작 소멸 | **유지** — 시험가동 중, 모의투자 완료 후 수정 예정 |

### 수정 파일 (54차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` (L4803~4807) | `_ts_on_chejan_event`: 청산 완전 체결 후 FLAT이면 `_broker_sync_last_error = "flat after exit"` |
| `main.py` (L930~943) | `_clear_pending_order`: QTimer 스케줄 시 `[IntrabarTPSchedule]` WARN 로그 추가 |
| `main.py` (L4029~4041) | `_ts_intrabar_tp_check`: 가드 실패 케이스별 WARN 로그 추가 |

### 5/19 기동 확인 사항

1. **B112**: 청산 후 EntryAttempt 로그에서 `broker_sync_reason='flat after exit'` 확인
2. **B114**: TP1 체결 직후 `[IntrabarTPSchedule]` 로그 출력 여부 확인
3. **B114**: `[IntrabarTPCheck]` 또는 `[IntrabarTPCheck] skip:` 로그로 근본 원인 특정
4. **53차 Fix**: `[IntrabarTPCheck]` 정상 발동 + TP1 완료 후 TP2 즉시 점검 확인 (5/18 세션 미적용, 5/19 첫 검증)

---

## 2026-05-18 (53차) — 2차 목표 도달 후 미청산 버그 2종 수정

### 배경

실세션 중 2차 목표(TP2)가 "도달"로 표시됐음에도 청산이 실행되지 않는 현상 제보. 코드 분석으로 두 가지 독립 버그 확인 및 수정 완료.

### 근본 원인 요약

| 버그 | 원인 |
|---|---|
| TP2·TP3 "도달" 오표시 | `pending_stage` 무시 — TP1 주문중임에도 상위 TP에 초록 "도달" 표시 → 운영자 혼동 |
| Pending 해소 후 TP 1분 지연 | `_clear_pending_order()` 이후 다음 분봉 파이프라인까지 대기 → TP3 위 가격이어도 최대 1분 청산 불가 |

### 현재 상태

| 항목 | 상태 |
|---|---|
| Fix 1: `_ts_intrabar_tp_check` 신규 함수 | **완료** — EXIT_PARTIAL 해소 즉시 300ms QTimer로 TP 재점검 |
| Fix 2: `_clear_pending_order` 수정 | **완료** — `_cleared_kind` 캡처 후 EXIT_PARTIAL·EXIT_MANUAL_PARTIAL 시 intrabar check 스케줄 |
| Fix 3: 대시보드 pending 표시 개선 | **완료** — `pending_stage` 기반 해당 TP 행에 "주문중", 미발동 상위 TP는 "대기" |
| 5/19 실세션 동작 확인 | **미완료** — `[IntrabarTPCheck]` 로그 + 대시보드 상태 확인 필요 |

### 수정 파일 (53차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `_clear_pending_order()`: `_cleared_kind` 캡처 + EXIT_PARTIAL 해소 시 300ms 후 `_ts_intrabar_tp_check` QTimer 스케줄 |
| `main.py` | `_ts_intrabar_tp_check()` 신규 함수 — pending 없음 확인 후 TP1→TP2→TP3 순차 재점검 |
| `main.py` | `TradingSystem._intrabar_tp_check = _ts_intrabar_tp_check` 등록 |
| `dashboard/main_dashboard.py` | 청산 트리거 배지 — `pending_stage` 기반으로 주문중 TP 행 강조 + 상위 미발동 TP "대기" 교체 |

### 5/19 기동 확인 사항

1. **`[IntrabarTPCheck]` 로그**: TP1 체결 완료(pending 클리어) 직후 300ms 내 로그 출력 확인
2. **대시보드 상태**: TP1 주문중(pending_stage=1) 시 TP2·TP3 행이 "도달"(초록) 아닌 "대기"로 표시되는지
3. **TP2 즉시 발동**: TP1 완료 후 다음 분봉까지 기다리지 않고 TP2가 바로 발동하는지

---

## 2026-05-18 (52차) — 손익 패널 4종 불일치 수정

### 배경

실세션 중 실시간 잔고(3,006,750원) / 손익 PnL 탭(2,261,018원) / 손익 추이 탭(3,555,000원) / HTS(2,877,000원) 네 패널이 모두 다른 값을 표시. 원인 분석 후 수정 완료.

### 현재 상태

| 항목 | 상태 |
|---|---|
| B109 Fix: `broker_daily_pnl` 포지션 보유 중 오염 차단 | **완료** — `position.status=="FLAT"` 조건 추가 |
| 손익 추이 탭 즉시 갱신 (`_refresh_pnl_history`) | **완료** — FLAT 확인 후 저장 직후 호출 |
| 5/19 실세션 동작 확인 | **미완료** — 다음 장 확인 필요 |

### 수정 파일 (52차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` (L5101~5116) | `upsert_daily_broker_pnl(_today_str, ...)` — `FLAT` 시에만 저장 + 저장 직후 `_refresh_pnl_history()` 호출 |

### 패널별 데이터 소스 정리

| 패널 | 소스 | 특이사항 |
|---|---|---|
| 실시간 잔고 금일손익 | Cybos `CpTd6197` header[6] `today_pnl` | 포지션 보유 중 미실현 포함 가능 |
| 손익 PnL 탭 일일누적 | `position_tracker._daily_pnl_pts × pt_value - commission` | 엔진 메모리, 가장 신뢰 |
| 손익 추이 탭 P/L 원 | `broker_daily_pnl` 테이블 우선, 없으면 `trades.db net_pnl_krw` 합산 | 52차 수정으로 FLAT 시에만 갱신 |
| HTS 금일손익 | Cybos HTS 자체 TR | 수수료 처리 기준 다름 |

---

## 2026-05-18 (51차) — 부분청산 Race Condition 버그 3종 수정

### 배경

실거래 로그에서 `[PNL] 체결진입`만 반복되고 부분청산 로그가 나오지 않는 현상 발생. 코드 분석으로 TP 부분청산 흐름에서 Cybos BlockRequest Race Condition 등 버그 3종 확인 및 수정.

### 현재 상태

| 항목 | 상태 |
|---|---|
| B106 Fix: `_ts_execute_partial_exit()` Race Condition | **완료** — pending 선등록 → 주문 → 실패 시 롤백으로 수정 |
| B107 Fix: `apply_entry_fill()` partial_done 불필요 리셋 | **완료** — 신규 포지션(FLAT→진입)일 때만 리셋, 분할체결·증량 시 보존 |
| B108 Fix: Chejan order_no="" 오탐 매칭 | **완료** — ENTRY/EXIT 방향 교차 검증 추가 |
| 실로그 검증 (10:00 TP1, 10:01 TP2) | **완료** — `[PendingOrder] set` → BlockRequest 중 Chejan 정상 매칭 확인 |

### 수정 파일 (51차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `_ts_execute_partial_exit()`: pending 선등록 후 주문, ret≠0 시 `_clear_pending_order()` 롤백 |
| `main.py` | `_ts_on_chejan_event_cybos_safe()`: order_no="" 매칭 시 direction 교차 검증 (_dir_ok 조건) |
| `strategy/position/position_tracker.py` | `apply_entry_fill()`: `_is_new_position` 플래그 추가, 증량 체결 시 partial_done 보존 |

### 검증 결과 (2026-05-18 실세션)

- 09:59 LONG 4계약 분할체결(1+1+1+1) 진입
- 10:00 **TP1 부분청산 정상 실행** — 1계약 @ 1156.92, +5.43pt ✅
- 10:01 **TP2 부분청산 정상 실행** — 1계약 @ 1160.18, +8.69pt ✅
- 10:04 하드스톱 전량청산 — 2계약 @ 1154.91(평균) ✅
- `[PendingOrder] set`이 `[ChejanFlow] 접수` 보다 먼저 기록됨으로 Race Condition 해소 확인

---

## 2026-05-17 (50차) — 5/15 거래 검토 기반 전략 핵심 수정 6종

### 배경

5/15 거래 리뷰(Deep 분석)에서 이상점 5종·개선안 7종이 도출됨. 5/16~5/17 커밋(40~49차)은 대시보드·Cybos 연동 위주였고 전략 핵심 파일은 미수정. 50차에서 우선순위 순으로 일괄 구현.

### 현재 상태

| 항목 | 상태 |
|---|---|
| CVD/VWAP/OFI 하드게이트 (checklist.py) | **완료** — CORE 3개 중 하나라도 ✗ → Grade X 강제 |
| EXIT 부분체결 즉시 긴급청산 (main.py) | **완료** — stuck 감지 30초→10초 + 반대 포지션 force_exit |
| Hurst 실계산 연결 (feature_builder.py) | **완료** — 60봉 버퍼, ATR 블록 뒤 삽입 (09:40부터 실값) |
| MIN_TRAIN_BARS 3000 한시적 하향 (batch_retrainer.py) | **완료** — 복원 목표 2026-05-26 |
| CB② 2회 강화 (settings.py) | **완료** — CB_CONSEC_STOP_LIMIT 3→2 |
| SizerMatch 로그 (main.py) | **완료** — Sizer 원본 vs 실제 진입 gap 기록 |
| 5/19 모의투자 실검증 | **미완료** — 다음 장 확인 필요 |
| MIN_TRAIN_BARS 5000 복원 | **미완료** — 2026-05-26 이후 |
| CB② 2회 기준 과잉 발동 모니터링 | **미완료** — 2주 관찰 |

### 수정 파일 (50차)

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | CORE 3개 하드게이트 — pass_count 후 즉시 X등급 반환 |
| `main.py` | EXIT stuck 타임아웃 30s→10s + 반대 포지션 force_exit |
| `main.py` | [SizerMatch] 로그 — `_qty_sizer_raw` 저장 후 진입 직전 gap 출력 |
| `features/feature_builder.py` | `calculate_hurst` import + `_close_history` deque(60) + Hurst 블록 |
| `learning/batch_retrainer.py` | `MIN_TRAIN_BARS` 5000→3000 (주석에 복원 목표일 명시) |
| `config/settings.py` | `CB_CONSEC_STOP_LIMIT` 3→2 |

### raw_data.db 현황 (GBM 학습 소스)

| 항목 | 값 |
|---|---|
| raw_candles | 3,432행 (2026-04-28 ~ 2026-05-15) |
| raw_features | 3,432행 |
| MIN_TRAIN_BARS | **3,000** (한시적, 원래 5,000) |
| 5/19 이후 재학습 | 가능 (3,432 ≥ 3,000) |
| 5,000행 달성 예상 | 2026-05-26경 |

### 주의 — 5/19 기동 확인 필요 사항

1. **Hurst 실값 확인**: 09:40 이후 `hurst=0.5xx` (0.5 이외 값) 로그 확인
2. **GBM 재학습 성공**: `[Retrain] 완료 | N초 | 성공=M/6 호라이즌` 로그 확인
3. **CB② 과잉 발동 여부**: 정상 트레이드 중 2회 손절로 CB 발동 시 파라미터 재검토
4. **[SizerMatch] 로그**: Sizer 제안 vs 실제 진입 gap 원인 추적

---

## 2026-05-16 (43차) — 손익 추이 패널 UI 개선

### 현재 상태

| 항목 | 상태 |
|---|---|
| 소스 선택 체크박스 (순방향/역방향) | **완료** — 탭바 우측 코너 배치 |
| 헤더 `(실행/순)` 표기 제거 | **완료** — 일별·주별·월별 모두 |
| 셀 "실행 xxx / 순 yyy" → 단일 값 | **완료** — `_fmt_val` / `_fmt_single` |
| MDD·샤프·누적 체크박스 연동 | **완료** — `_mdd_sel`, `_sharpe_sel` |
| 요약 카드 (총 손익·MDD) 연동 | **완료** |
| 실 UI 검증 | **미완료** — 다음 기동 시 확인 필요 |

### 수정 파일 (43차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `PnlHistoryPanel`: 체크박스 추가, 헤더 정리, 셀 단일값 표시, 신규 헬퍼 7개 |

---

## 2026-05-16 (42차) — Cybos 잔고 Chejan 버그 수정 4종

### 발견된 버그 근본 원인

```
[발동 체인]
진입 → 잔고 Chejan(gubun=1) 도착
  → sync_from_broker(grade="BROKER") — grade·TP 플래그 덮어씀 [B102, B103]
  → _clear_pending_order() — EXIT pending 파괴 [B101]
  → TP1 체결 Chejan → pending=None → _ts_handle_external_fill
  → remaining_fill > 0 → 반대 방향 MANUAL 포지션 생성
  → 즉시 하드스탑 → record_stop_loss() → CB② 발동 [B100 연관]
  → EmergencyExit.execute() → pending 미등록 → 3건 외부체결 [B104]
```

### 현재 상태

| 항목 | 상태 |
|---|---|
| Fix 1: EXIT pending 보호 (`_ts_sync_from_balance_payload`) | **완료** — main.py |
| Fix 2: TP 플래그 보존 (`sync_from_broker`) | **완료** — position_tracker.py |
| Fix 3: grade 보존 (`sync_from_broker`) | **완료** — position_tracker.py |
| Fix 4: EmergencyExit pending 선등록 | **완료** — emergency_exit.py + main.py |
| 가격 포맷 버그 (`session_recovery_service.py`) | **완료** — `{entry_p:.2f}` / `{exit_p:.2f}` |
| 4종 수정 모의투자 실검증 | **미완료** — 다음 장(2026-05-19) 확인 필요 |

### 수정 파일 (42차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | `_ts_sync_from_balance_payload`: EXIT pending 진행 중이면 `_clear_pending_order()` 생략 |
| `main.py` | `EmergencyExit` 초기화: `pending_registrar=self._set_pending_order` 전달 |
| `strategy/position/position_tracker.py` | `sync_from_broker`: 동방향 sync 시 TP 플래그 보존 + grade 보존 |
| `safety/emergency_exit.py` | `pending_registrar` 파라미터 추가 + 발주 전 EXIT_FULL pending 등록 |
| `strategy/runtime/session_recovery_service.py` | 복원 로그 가격 포맷 `{entry_p:.2f}` / `{exit_p:.2f}` 3곳 |

### Fix별 동작 요약

| Fix | 문제 | 해결 |
|---|---|---|
| Fix 1 | 잔고 Chejan이 EXIT pending을 즉시 파괴 | EXIT 계열 pending이면 clear 생략, 로그만 남김 |
| Fix 2 | 동방향 sync가 TP1/2/3_done 플래그 초기화 | `same_side_sync`이면 TP 플래그 유지 |
| Fix 3 | 동방향 sync가 grade=A를 BROKER로 덮어씀 | `same_side_sync`이면 기존 grade 보존 |
| Fix 4 | EmergencyExit 발주 전 pending 미등록 → 비상청산 체결이 외부체결로 분류 | 발주 전 `EXIT_FULL` pending 등록 |

---

## 2026-05-16 (41차) — CB③ 분석 + HORIZON_THRESHOLDS 재보정 + 모니터링·툴팁

### 현재 상태

| 항목 | 상태 |
|---|---|
| HORIZON_THRESHOLDS 재보정 | **완료** — 1200pt 시장 기준 전체 약 1.6× 상향 (FLAT 29~37% 목표) |
| `_log_threshold_monitor()` | **완료** — GBM 재학습 완료 시 + 30분 주기 호출 |
| `_threshold_monitor_tick` | **완료** — main.py line 286 |
| `_CB_TIP` 슬랙 알림 섹션 | **완료** — 5개 트리거 대응표 + 다크박스 포함 |
| `param_title` 피처 윈도우 툴팁 | **완료** — CORE/선택/외부 3색 분류 테이블 |
| `_HZ_TIP` + `hz_title` 연결 | **완료** — 6섹션 툴팁 (호라이즌 개념·threshold·acc·모니터링) |
| GBM 재학습 적용 | **미완료** — 다음날 08:45 기동 시 warmup retrain 자동 발동 예정 |
| ATR 동적 방식 전환 | **미완료** — 정적 재보정 안정화 확인 후 전환 검토 |

### HORIZON_THRESHOLDS 현재값 (2026-05-16 재보정)

| 호라이즌 | 구값 | 신값 | 1200pt 기준 pt |
|---|---|---|---|
| 1m  | 0.0002 | **0.0005** | 0.60pt (12틱) |
| 3m  | 0.0003 | **0.0008** | 0.96pt (19틱) |
| 5m  | 0.0004 | **0.0011** | 1.32pt (26틱) |
| 10m | 0.0006 | **0.0016** | 1.92pt (38틱) |
| 15m | 0.0008 | **0.0022** | 2.64pt (53틱) |
| 30m | 0.0012 | **0.0032** | 3.84pt (77틱) |

> σ_1min≈1.47pt 기준, threshold≈0.4~0.5σ → FLAT 29~37% (3택 랜덤 33% 근접)

### 수정 파일 (41차)

| 파일 | 변경 내용 |
|---|---|
| `config/settings.py` | HORIZON_THRESHOLDS 전체 재보정 |
| `main.py` | `_threshold_monitor_tick`, `_log_threshold_monitor()`, GBM 콜백·파이프라인 30분 주기 호출 |
| `dashboard/main_dashboard.py` | `_CB_TIP` 슬랙 섹션, `param_title` 피처 윈도우 테이블, `_HZ_TIP` + `hz_title` 연결 |

### threshold 전파 구조

```
config/settings.py (HORIZON_THRESHOLDS)
  ├── learning/batch_retrainer.py     (학습 라벨 생성)
  ├── learning/prediction_buffer.py   (검증 채점)
  └── learning/target_builder.py      (단독 타겟 계산)
→ settings.py 1곳 수정으로 전파 완료. GBM 재학습 필수.
```

---

## 2026-05-16 (40차) — 장전 시동 흐름 + 슬랙 알림 + 대시보드 체크박스

### 현재 상태

| 항목 | 상태 |
|---|---|
| `pre_market_setup` 타이밍 | **완료** — 08:55 단일 블록 (기존 08:45+08:55 이중 블록 통합) |
| 스냅샷 워밍업 (`_prime_from_snapshot`) | **완료** — `pre_market_setup()` 끝에 선워밍, `start()` 진입 시 skip 로직 |
| GBM 재학습 데몬 스레드 | **완료** — `threading.Thread(daemon=True)` + `QTimer.singleShot(0, _on_gbm_retrain_done)` |
| 08:58 broker sync 선실행 | **완료** — `_pre_sync_attempted` 플래그로 중복 방지 |
| `start_mireuk.bat` 세션 이중 확인 | **완료** — preflight → 3s 대기 → 재확인 |
| 슬랙 알림 (`utils/notify.py`) | **완료** — `_SLACK_ENABLED`, 6개 단계별 함수 추가 |
| `main.py` 슬랙 연동 | **완료** — 기동·장전·첫틱·sync 미검증·연결끊김·90s 지연 |
| 대시보드 `chk_slack` 체크박스 | **완료** — `res_box` 왼쪽 정렬, `ui_prefs.json` 저장·복원 |
| CLAUDE.md 08:55 교정 | **완료** |
| 40차 수정 실검증 | **미완료** — 다음 기동 시 슬랙 알림 수신 + 첫 틱 슬랙 확인 필요 |

### 수정 파일 (40차)

| 파일 | 변경 내용 |
|---|---|
| `main.py` | 08:55 통합 블록, 스냅샷 워밍업, GBM 데몬 스레드, 08:58 broker sync, 슬랙 연동 전체, `chk_slack` 연결 |
| `collection/cybos/realtime_data.py` | `start()` — `_last_price > 0`이면 `_prime_from_snapshot` skip |
| `utils/notify.py` | `_SLACK_ENABLED` 플래그 + 제어 함수 + 6개 단계별 알림 함수 |
| `dashboard/main_dashboard.py` | `chk_slack` QCheckBox 추가, `res_box` 왼쪽 정렬, `_save_ui_prefs`·`_restore_ui_prefs` slack 저장/복원 |
| `start_mireuk.bat` | preflight 후 3s + Cybos 세션 재확인 구간 추가 |
| `CLAUDE.md` | 파이프라인 08:45 → 08:55 교정 |

---

## 2026-05-15 (39차) — 선물 롤오버 자동화 전면 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| `_MARKET_SYMBOLS` 동적 생성 | **완료** — `_build_market_symbols()` 기동 날짜 기준 자동 계산, 하드코딩 제거 |
| `set_selected_symbol()` | **완료** — 프로브 후 대시보드 콤보 즉시 동기화 |
| 일반선물(A01xxx) FutureMst 프로브 | **완료** — `get_nearest_normal_futures_code()` 추가 |
| `_resolve_trade_code()` 일반선물 지원 | **완료** — 미니선물과 동일 방식으로 근월물 프로브 + UI 동기화 |
| `check_rollover()` 장중 감시 | **완료** — 60 tick(30분)마다 근월물 재확인, WARNING + UI 갱신 |
| `_rollover_detected` 반복 알림 억제 | **완료** — 감지 후 재탐지 억제, 장 시작 시 초기화 |
| 38차 수정 실검증 | **미완료** — `[NormalProbe/MiniProbe]`, `[CodeRoll]`, `verified=True`, tick #1 확인 필요 |

### 수정 파일 (39차)

| 파일 | 변경 내용 |
|---|---|
| `dashboard/main_dashboard.py` | `_build_market_symbols()`, `_nth_thursday()`, `_next_valid_contracts()`, `_futures_code8()` 추가. `set_selected_symbol()` MireukDashboard + DashboardAdapter |
| `collection/cybos/api_connector.py` | `get_nearest_normal_futures_code()` 추가 (A01xxx FutureMst 프로브) |
| `strategy/runtime/broker_runtime_service.py` | `_resolve_trade_code()` 일반선물 프로브 추가 + UI 동기화. `check_rollover()` 신설 |
| `main.py` | `_scheduler_tick()` 60 tick(30분) 롤오버 감시 + `_rollover_detected` 플래그 |

### 중요 운영 규칙 (39차 추가)

- **심볼 목록은 기동 시 자동 갱신**: `_MARKET_SYMBOLS`는 `_build_market_symbols()` 반환값 → 소스코드 수정 없이 매월/분기 롤오버 반영
- **일반선물도 FutureMst 프로브**: A01xxx(분기물)도 `price > 0` 검증 → UI 저장값 만기 시 자동 교체
- **UI 콤보는 항상 실제 거래 코드**: `_resolve_trade_code()` 확정 후 `set_selected_symbol()` 호출로 UI = 실제 거래 코드

---

## 2026-05-15 (38차) — BlockRequest 데드락 + 롤오버 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| `_run_block_request` COM STA 데드락 | **수정 완료** — `done.wait(0.01)` + `PumpWaitingMessages()` 루프로 교체 |
| `CpTd0723` / `FutureMst` 30초 타임아웃 | **수정 완료** — 메시지 펌핑 후 ~1초 내 완료 예상 |
| 미니선물 만기 롤오버 미처리 | **수정 완료** — `_resolve_trade_code`가 항상 프로브, A0565→A0566 자동 전환 |
| `get_nearest_mini_futures_code` 만기 skip | **수정 완료** — `price > 0` 조건, 만기 코드 자동 건너뜀 |
| broker sync 장중 재시도 | **추가 완료** — startup 실패 시 3분 간격 자동 재시도 |

### 중요 운영 규칙 (Cybos COM)

- **BlockRequest는 메인 스레드 메시지 펌프 필요**: 백그라운드 스레드에서 단독 호출 시 항상 타임아웃. `_run_block_request`가 메인 스레드에서 10ms 간격 펌핑으로 해결.
- **미니선물 코드는 항상 프로브**: 미니선물(A05xxx)은 월물 만기(2차 목요일) 다음날부터 근월물이 바뀐다. UI 저장값을 신뢰하지 않는다.

---

## 2026-05-15 (37차) — 운영 헬스 중앙 패널 추가

### 현재 상태

| 항목 | 상태 |
|---|---|
| 중앙 패널 운영 헬스 | **완료** — `mid_tabs`에 `⚕️ 운영 헬스` 탭 추가 |
| 로그 패널 운영 헬스 | **유지** — 하단 `6 운영 헬스`는 텔레메트리 로그용으로 계속 사용 |
| 중앙 헬스 동기화 | **완료** — `update_runtime_health()`가 로그 패널과 중앙 패널을 동시 갱신 |
| 중앙 헬스 스파크라인 | **완료** — Health Score / 지연 / 품질 3라인 표시 |
| Health Score 계산 | **주의** — 현재는 임시값을 넣고 있어 추후 실제 산식 연결 필요 |

### 운영 판단 포인트

- 이제 헬스 뷰는 로그 창에만 있는 것이 아니라 중앙 패널에서도 즉시 확인 가능하다
- 운영자가 보는 요약 뷰와 로그성 뷰를 분리해 가독성을 확보했다
- 다음 보완점은 중앙 헬스의 `Health Score`를 실제 런타임 계산값으로 바꾸는 것이다

## 2026-05-15 (36차) — Cybos 자동 로그인 버그 수정

### 현재 상태

| 항목 | 상태 |
|---|---|
| 모의투자 선택 창 탐지 (`candidates=[]` 버그) | **수정 완료** — `EnumChildWindows` 4차 탐색 추가, 자식 창 생성 케이스 대응 |
| min_wait 중 즉시 감지 | **수정 완료** — 20초 맹목적 대기 → 매초 탐지/즉시 클릭 |
| 공지사항 팝업 처리 | **신설 완료** — `_dismiss_notice_popups(timeout=10)` 모의투자 접속 직후 호출 |
| 로그인 흐름 문서화 | **완료** — `docs/CYBOS_AUTOLOGIN_FLOW.md` 작성 |
| 4차 탐색 실 동작 확인 | **미완료** — 다음 로그인 실행 시 `[INFO] 4차 탐지:` 로그 출력 여부 확인 필요 |
| 공지사항 팝업 제목 패턴 확인 | **미완료** — 실제 팝업 제목이 "공지사항" 외 다른 패턴이면 `NOTICE_KEYWORDS` 확장 필요 |

### 핵심 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `scripts/cybos_autologin.py` | `_find_mock_dialog_hwnd`, `_click_mock_access_in_window`, `_close_dialog_window`, `_dismiss_notice_popups` 신설. min_wait 매초 탐지 적용. |
| `docs/CYBOS_AUTOLOGIN_FLOW.md` | 전체 로그인 흐름 다이어그램 + 단계별 상세 문서 |

---

## 2026-05-15 (35차) — 운영 헬스 고도화 + 하루 운용 검증 준비

### 현재 상태

| 항목 | 상태 |
|---|---|
| Degraded auto/manual 차단 정책 분리 | **완료** — auto/manual 각각 독립 옵션으로 동작 |
| 헬스 설정 핫리로드 | **완료** — `settings.py` 변경 시 재시작 없이 반영 |
| 헬스 스파크라인 확장 | **완료** — Health Score + 지연 + 품질 3라인 표시 |
| 핫리로드/차단 하네스 검증 | **완료** — `validate_health_policy_hotreload.py` 결과 PASS |
| 감사문서 ##10 하루 운용 체크리스트 | **완료** — 항목 추가 및 07:38 사전점검 반영 |
| 브로커 startup sync 상태 | **주의** — `verified=False`, `block_new_entries=True` (07:38 기준) |
| 헬스 탭 수동 UI 진입 확인 | **미완료** — 운영자 화면 확인 필요 |

### 운영 판단 포인트

- 지금 상태에서 자동진입은 브로커 sync 미검증 조건으로 차단되어 있음
- Day10-2/Day11 장중 검증(10.2~10.5)은 sync 정상화 이후 판정하는 것이 유효함
- 핫리로드 정책 검증은 하네스 기준으로는 정상이나, 장중 실제 로그 동작 확인이 추가 필요

## 2026-05-14 (34차) — 진입관리 탭 시간대 가이드 UI 강화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 진입관리 설명줄 | **완료** — 현재 zone, 시간 범위, `conf≥`, `size×`, 진입 허용 여부를 실시간 표시 |
| 시간대 버튼 칩 | **완료** — `GAP_OPEN`~`EXIT_ONLY` 6구간을 색상 칩으로 시각화, 현재 구간 강조 |
| A/B/C 등급 버튼 권장 표시 | **완료** — 현재 zone의 `size_mult` 기준으로 권장 등급을 자동 강조 |
| 수동 선택 구분 | **완료** — 권장(`권장`)과 사용자 선택(`선택`)을 동시에 구분 표시 |
| 만기일/FOMC 오버라이드 배지 | **완료** — UI 설명줄에 `만기일 적용중` / `만기 전일 적용중` / `FOMC 적용중` 배지 노출 |
| 실제 UI 런타임 확인 | **미완료** — PyQt 화면에서 시인성과 배지 위치 확인 필요 |

### 구현 메모

- 표시값 소스는 정적 상수가 아니라 `TimeStrategyRouter.route()` + `apply_expiry_override()` + `apply_fomc_override()` 체인이다
- 권장 등급은 `ENTRY_GRADE`의 `size_mult`와 현재 zone `size_mult`의 최근접 매핑으로 계산한다
- 자동 생성 런타임 상태 파일 `data/session_state.json`은 변경되었지만 세션 카운터 증가 성격이라 코드 변경 사항과 분리 관리한다

## 2026-05-14 (33차) — Cybos 장외 startup crash 완화

### 현재 상태

| 항목 | 상태 |
|---|---|
| 장외 Cybos startup crash | **1차 완화 적용 완료** — 장외에는 `RealtimeData.start()`와 수급 `QTimer`를 시작하지 않도록 가드 추가 |
| MacroFetcher startup noise | **완화 완료** — yfinance 실패 콘솔 노이즈 억제, 15분 cooldown, fallback key 정렬 |
| 잔고 `QTableWidget` stylesheet warning | **부분 완화** — 문제 구간 stylesheet 단순화. 재실행으로 완전 해소 여부 확인 필요 |
| 장외 launcher 재검증 | **미완료** — 최신 패치 후 `start_mireuk.bat` 야간 재실행 확인 필요 |

### 로그 기준 결론

- 장중 재기동(`2026-05-14 14:09:23`)은 `startup sync -> realtime start -> tick/hoga 수신`까지 정상 진행
- 야간 재기동(`2026-05-14 20:18:19`, `20:20:15`, `20:26:13`)은 공통적으로 `CpTd0723`와 `FutureMst` timeout 뒤 `-1073741819` 종료
- 따라서 현재 판단은 **장외 timeout 상태에서 실시간 구독까지 강행하던 경로가 가장 위험한 지점**이라는 것

### 남은 리스크

- `CpTd0723` / `FutureMst` timeout 자체의 근본 원인은 아직 미해결
- 장외 guard로 crash는 막을 가능성이 높지만, 장중 reconnect나 pre-open 구간에서 같은 패턴이 재현되는지는 아직 미검증
- `QTableWidget` parse warning이 다른 테이블 stylesheet에서 계속 날 수 있음

---

## 2026-05-14 (32차) — 2차 감사 P3 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/dynamic_sizing.py` | M5: `MIN_COMBINED_FRACTION=0.12` — 7팩터 곱 0.12 미만 시 `_blocked()` 반환 |
| `config/settings.py` | M6: `TIME_ZONES`에 `GAP_OPEN("09:00","09:05")` 추가 (v6.6) |
| `utils/time_utils.py` | M6: `get_time_zone()` GAP_OPEN 분기 추가 / 만기일: `get_monthly_expiry_date()` · `days_to_monthly_expiry()` · `is_expiry_day()` · FOMC 목록 · `is_fomc_day()` 추가 |
| `strategy/entry/time_strategy_router.py` | M6: `GAP_OPEN` 파라미터 추가 / 만기일: `apply_expiry_override()` · `apply_fomc_override()` 추가 |
| `model/multi_horizon_model.py` | M7: `_scaler_fitted_at` 기록 + `predict_proba()` 내 90분 경과 경고 + |z|>4 극단 피처 경고 |

### P3 완료 현황 (2차 감사 기준)

| 항목 | 상태 |
|---|---|
| M5 Dynamic Sizing 0 수렴 | ✅ 완료 — MIN_COMBINED_FRACTION=0.12 차단 |
| M6 09:00-09:05 미분류 | ✅ 완료 — GAP_OPEN 구간 신설 (min_conf=0.67, size×0.5) |
| M7 StandardScaler 노후화 | ✅ 완료 — 90분 경과 WARNING + 극단 z-score 경고 |
| 만기일/FOMC 대응 부재 | ✅ 완료 — 월물 만기일 함수 + FOMC 목록 + TimeRouter 오버라이드 |

---

## 2026-05-14 (31차) — 2차 감사 P1 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `utils/time_utils.py` | C3: `KST` 타임존 상수 + `now_kst()` 헬퍼 추가, 모든 내부 `datetime.now()` 교체 |
| `safety/circuit_breaker.py` | C3: `now_kst()` 사용 |
| `strategy/exit/time_exit.py` | C3: `now_kst()` — 15:10 강제청산 KST 보장 |
| `safety/kill_switch.py` | C3: `now_kst()` |
| `strategy/entry/meta_gate.py` | C3: `now_kst()` |
| `strategy/profit_guard.py` | C3: `now_kst()` |
| `strategy/entry/time_strategy_router.py` | C3: `now_kst()` |
| `strategy/exit/exit_manager.py` | C3: `now_kst()` |
| `strategy/position/position_tracker.py` | C3: `now_kst()` (20곳) |
| `strategy/entry/staged_entry.py` | C3: `now_kst()` |
| `config/settings.py` | M1: `GBM_MIN_SAMPLES_LEAF = 10` 상수 추가 |
| `model/multi_horizon_model.py` | M1: `GBM_MIN_SAMPLES_LEAF` 임포트 → 파라미터 통일 |
| `learning/batch_retrainer.py` | M1: `GBM_MIN_SAMPLES_LEAF` 임포트 → 10으로 통일 (기존 20 → 10) |
| `main.py` | H1: silent except 8곳 → logger.debug/warning 추가 |
| `main.py` | H4: `_last_gate_signals`, `_last_gate_direction` 저장 + `_on_core_feature_fail` 메서드 |
| `main.py` | H4: `_post_exit()` → EnsembleGater 피드백 연결 |
| `features/feature_builder.py` | H2: CVD/VWAP/OFI 연속 실패 카운터 + 3회 시 ERROR 경보 + `_on_core_fail` 콜백 |
| `model/ensemble_gater.py` | H4: `record_outcome()` + `_load_weights()` + `_save_weights()` — 온라인 학습 |
| `model/ensemble_decision.py` | H4: `record_trade_outcome()` 위임 메서드 추가 |

### P1 완료 현황 (2차 감사 기준)

| 우선순위 | 항목 | 상태 |
|---|---|---|
| P1 (C3) | KST 타임존 전체 적용 | ✅ 완료 — 10개 핵심 모듈 `now_kst()` 교체 |
| P1 (H1) | `except Exception: pass` 장애 은폐 제거 | ✅ 완료 — 8곳 logger 추가 |
| P1 (H2) | CORE 피처 0 폴백 → ERROR 경보 | ✅ 완료 — 3회 연속 실패 시 ERROR + Slack |
| P1 (M1) | GBM 파라미터 불일치 | ✅ 완료 — `GBM_MIN_SAMPLES_LEAF=10` 공유 상수 |
| P1 (H4) | EnsembleGater 고정 가중치 | ✅ 완료 — 거래 결과 기반 온라인 학습 (lr=0.005) |

---

## 2026-05-14 (30차) — 감사 기반 전체 버그 수정 + 스텁 모듈 구현

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `strategy/entry/checklist.py` | P0: FLAT 방향 조기 반환 (X등급, auto_entry=False) — FLAT→AUTO SHORT 잠재 버그 차단 |
| `features/feature_builder.py` | P1: safe bar.get() + 9개 계산 블록 try/except + 기본값 fallback |
| `features/technical/ofi.py` | P1: `flush_minute()` 말미 `_prev_*=None` 리셋 — stale delta 방지 |
| `safety/circuit_breaker.py` | P1: ATR 버퍼 중앙값 기반 지속 급등 감지 추가 (`import statistics`) |
| `main.py` | P2: 더미 매크로→실 API 연동, `_send_kiwoom_*`→`_send_broker_*` rename 13개소, Dead Code 제거, 스텁 5개 연결 |
| `collection/broker/kiwoom_broker.py` | P2: InvestorData에 api 주입 |
| `strategy/position/position_tracker.py` | P2: 인코딩 깨짐 4개소 수정 |
| `features/technical/cvd.py` | P3: 보합 틱 delta=0 (Long 바이어스 제거) |

### 신규 생성 파일

| 파일 | 내용 |
|---|---|
| `features/macro/macro_feature_transformer.py` | VIX·SP500 등 9개 정규화 피처 |
| `learning/self_learning/daily_consolidator.py` | 시간대별 정확도 → confidence 패널티 |
| `learning/self_learning/drift_adjuster.py` | SGD alpha 동적 조정 (드리프트 감지) |
| `collection/options/pcr_store.py` | 외인 PCR 20분 롤링 저장소 |
| `features/options/option_features.py` | PCR → 6개 ML 피처 |

### 삭제된 파일

| 파일 | 이유 |
|---|---|
| `strategy/entry/entry_manager.py` | Dead Code — main.py에서 한 번도 인스턴스화 안 됨. Kiwoom 전용 API 서명으로 Cybos 미호환. |

### 현재 피처 파이프라인 (STEP 4 갱신 후)

```
investor_data.get_features()  → supply_feats
pcr_store.update(supply_feats)
macro_fetcher.get_features()  → macro_transformer.transform() → _macro_feats
option_feat_calc.transform(pcr_store.get_features()) → _option_feats
feature_builder.build(bar, supply_demand=supply_feats, macro_data=_macro_feats, option_data=_option_feats)
```

### 현재 일일 마감 (15:40) 파이프라인 갱신 후

```
daily_consolidator.consolidate()          ← 시간대별 패널티 계산
drift_adjuster.record_accuracy(acc)       ← SGD alpha 갱신
online_learner.set_alpha(new_alpha)       ← 즉시 반영
pcr_store.reset_daily()                   ← 신규 추가
```

---

## 2026-05-14 (29차) — CB HALT 사후 조사 + 모델 신뢰도 개선

### 수정된 파일

| 파일 | 변경 내용 |
|---|---|
| `main.py` | B84: EXIT pending stuck Chejan 유실 대응 (`expected_remaining` 비교) |
| `main.py` | B86: CB HALT 중 수동 청산 불가 수정 (pending 강제 소멸 분기) |
| `main.py` | C10: `record_accuracy(confidence=_conf)` 전달 |
| `main.py` | C11: `_warmup_retrain_pending` 플래그 + STEP 3 `force=True` 재학습 트리거 |
| `safety/circuit_breaker.py` | B85: `_trigger_halt()` → `emergency_exit` 콜백 호출 추가 |
| `safety/circuit_breaker.py` | C10: `_high_conf_wrong_streak` 카운터 + 동적 임계값 (0.35→0.50) |
| `model/multi_horizon_model.py` | C09: `CONF_CLIP = 0.92` 극단 확률 클리핑 |
| `config/settings.py` | C10 상수 3개: `CB_HIGH_CONF_WRONG_LIMIT`, `CB_HIGH_CONF_THRESHOLD`, `CB_ACCURACY_MIN_30M_STRICT` |

### 현재 안전장치 상태

| 항목 | 상태 |
|---|---|
| CB② 연속 손절 → emergency_exit | ✅ 정상 (이번 회차 B85 수정) |
| CB③ 정확도 저하 → emergency_exit | ✅ 정상 (이번 회차 B85 수정) |
| CB③ 과신 오류 동적 임계값 | ✅ 신규 구현 (C10) |
| GBM 극단 확률 클리핑 (0.92) | ✅ 신규 구현 (C09) |
| 세션 재시작 후 GBM 즉시 재학습 | ✅ 신규 구현 (C11) |
| EXIT pending stuck 자동 복구 | ✅ 정상 (이번 회차 B84 수정) |

### 주요 설계 변경

- **CB HALT 발동 범위 확대**: CB⑤(API 지연)만 emergency_exit 호출하던 것을 CB②/③ 발동 시에도 즉시 청산 (B85)
- **세션 재시작 보호**: 재시작 직후 구식 GBM으로 인한 방향 고착 방지. `_broker_sync_block_new_entries=True` 유지 중에 재학습 수행 → 완료 후 진입 허용 (C11)
- **conf 상한선**: GBM이 학습 분포 외 입력에서 conf=1.000 반환하는 현상 → 0.92로 클리핑, 초과분 나머지 클래스 균등 분배 (C09)

---

## 2026-05-14 (28차) — L2 배지 UI + 모드 필터

### 신규 구현

| 파일 | 내용 |
|---|---|
| `strategy/profit_guard.py` | `_TierGate.halt_threshold`, `_TierGate.halt_tier` 프로퍼티 + `ProfitGuard.get_l2_halt_info()` 메서드 |
| `dashboard/main_dashboard.py` | `self.lbl_l2_halt` 배지 + `update_l2_halt_badge()` 메서드 |
| `main.py` | STEP 9 후 L2 halt 매분 동기화 + STEP 7 모드필터 2순위 추가 |

### 진입 로직 우선순위 (최종 정의)

```
신호 발생 (STEP 6)
    ↓
[1순위] L2 ProfitGuard 체크 ← 수익 보존 (시스템)
    ├─ 1-1: Trail Stop (L1)
    ├─ 1-2: Tier Gate (L2) ← L2 halt latch
    ├─ 1-3: Afternoon Mode (L3)
    └─ 1-4: Profit CB (L4)
    ↓
    통과했다면 ↓
[2순위] 모드 필터 체크 ← 신호 강도 (사용자)
    ├─ "auto": A급만
    ├─ "hybrid": A, B급 (기본값)
    └─ "manual": A, B, C급
    ↓
    둘 다 통과 → 진입 ✅
    L2 차단 → 진입 불가 (원인: [차단] L2 ...)
    모드필터 차단 → 진입 불가 (원인: [모드필터] ... 불일치)
```

### 현재 진입관리 탭 상태

| UI 요소 | 구현 상태 | 기능 |
|---|---|---|
| Auto ON/OFF | ✅ 완벽 | 자동/수동 진입 전환, 로그 기록 |
| A/B/C 등급진입 버튼 | ✅ 이번 회차 완성 | 모드별 등급 필터링 (L2 다음) |
| 역방향 진입 | ✅ 완벽 | 신호 반대로 진입 |

### L2 Tier Gate 최종 설정 이해

```
금일 수익 < 50만원
  → L2 적용 안 함 (기본 min_mult 미정)
  → 진입관리 탭 모드 필터만 작용

금일 수익 50~100만원
  → L2: min_mult=0.6 (C급 이상)
  → 진입관리 탭: 모드 필터 적용
  → 예: C급+B모드 → L2 통과 → 모드 차단 ❌

금일 수익 100~200만원
  → L2: min_mult=1.0 (A급만)
  → 진입관리 탭: 모드 필터 적용
  → 예: B급+B모드 → L2 차단 ❌

금일 수익 ≥ 200만원
  → L2: max_qty=0 (거래 완전 중단)
  → 대시보드: 🔒 L2 중단 (N.NM원) 배지 표시
  → 진입 불가능 (L1~L4 모두)
```

### 배지 표시 규칙

| 배지 | 위치 | 조건 | 표시 내용 |
|---|---|---|---|
| CB 배지 | 상단 중앙 | CB 상태 | "CB NORMAL" / "⛔ CB HALT" / "⏸ CB PAUSE" |
| **L2 배지** | **CB 오른쪽** | **L2 halt 활성** | **🔒 L2 중단 (N.NM원)** |
| L2 배지 | CB 오른쪽 | L2 halt 비활성 | (숨김) |

---

## 2026-05-14 (27차) — Cybos 옵션 지표 수집

### 신규 파일

| 파일 | 내용 |
|---|---|
| `scripts/probe_cp_option_code.py` | CpOptionCode 체인 조회 (4,624종목) |
| `scripts/probe_cp_calc_opt_greeks.py` | CpCalcOptGreeks 그릭스 계산 (속성 할당 + Calculate 방식) |
| `scripts/probe_cp_option_mo.py` | OptionMo 실시간 OI 구독 (장중 필요) |
| `scripts/verify_option_mst_fieldmap.py` | OptionMst HeaderValue 필드맵 교차 검증 |
| `scripts/collect_option_metrics.py` | PCR/GEX/ATM OI 통합 수집 (48종목 2.9초) |
| `AGENTS.md` | 한글판 에이전트 가이드 |

### 핵심 결과 (2026-05-13 장후, 2606월물)

| 지표 | 값 | 해석 |
|---|---|---|
| PCR (OI) | 0.54 | 콜 우위, 강세 |
| ATM PCR | 1.04 | 중립 |
| Total GEX | +35.3B원 | 감마 롱 |

### 확정 필드맵

HV(6)=행사가, HV(13)=잔존일수, HV(93)=현재가, HV(97)=체결량, HV(99)=OI, HV(37)=전일OI, HV(109)=Delta, HV(110)=Gamma, HV(111)=Theta, HV(113)=Rho. HV(17)≠spot(날짜), HV(15)≠ATM(콜/풋코드).

### 다음

1. OptionMo 장중 검증 (4단계)
2. collection/options/ + features/options/ 신설 → Mireuk 피처 통합
3. PCR/GEX 시계열 안정성 검증
4. OptionMst 폴링 최적화

---

## 2026-05-13 (26차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dev_memory/SESSION_LOG.md` | 작업스케줄러 순서의존 로그인 충돌(B83) 원인/개선안 기록 |
| `dev_memory/CURRENT_STATE.md` | 26차 상태 반영 |
| `dev_memory/NEXT_TODO.md` | 외부 키움 리포지토리 구현/검증 TODO 추가 |
| `dev_memory/DECISION_LOG.md` | D58/B83 설계결정/버그 기록 |

### 핵심 운영 상태

- `futures` 리포지토리 내부 코드는 이번 턴에서 변경하지 않았고, 개선안은 외부 키움 프로젝트 적용 항목으로 정리했다.
- 실행순서 충돌의 실질 해법은 절대좌표/클립보드 매크로 제거 및 창 객체 기반 자동화 전환이다.
- 보안상 키움 계정정보는 스크립트 하드코딩 금지, 환경변수/보안 저장소 주입 방식으로 관리해야 한다.

---

## 2026-05-13 (25차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `strategy/position/position_tracker.py` | TP3/3단계 부분청산, `initial_quantity`, `partial_3_done`, stage plan/target helpers, `trailing_anchor_price`, `peek_saved_entry_time()` 추가 |
| `strategy/position/position_tracker.py` (`sync_from_broker`) | same-side broker sync 시 `entry_time`, `stop_price`, `trailing_anchor_price`, 원진입 수량 보존 |
| `strategy/position/position_tracker.py` (`update_trailing_stop`) | 2ATR 구간 trailing stop을 `current_price`가 아니라 `trailing_anchor_price` 기준으로 추적 |
| `dashboard/main_dashboard.py` | 청산관리 패널 `트레일링 기준`/`현재 실행 스톱` 분리, 3차 목표 34% 및 원진입 수량 기준 stage 게이지 반영 |
| `dashboard/main_dashboard.py` (`sync_active_trade`) | 진입마커 sync 시 기존 `entry_ts` 보존, 새 진입/방향전환 때만 신규 마커 생성 |
| `main.py` | 청산관리 패널 payload에 `trail_basis`, `stage_plan`, `pt_value` 전달 |
| `main.py` | stuck exit timeout 시 브로커 잔고 우선 재검증 후 pending 유지/해제 |
| `main.py` | 외부진입 동기화 직후 `250ms / 1200ms` 잔고 재조회 트리거 추가 |

### 설계/운영 규칙

- same-side broker sync는 trailing stop을 되돌리지 않는다.
- 청산관리 패널의 `트레일링 기준`은 `현재 실행 스톱` 복제값이 아니라 별도 기준값이다.
- 진입마커는 진입시각 고정이다. active position sync나 startup restore가 들어와도 기존 `entry_ts`를 우선 보존한다.
- 외부체결은 Chejan만 신뢰하지 않고, 다계약 외부진입/청산 뒤에는 브로커 잔고 재조회로 최종 수량을 보정한다.

### 현재 운영 상태

- 청산관리 탭은 `TP1/TP2/TP3 = 33/33/34`를 원진입 수량 기준으로 유지하며, 수동 부분청산 후에도 stage 완료 상태를 유지한다.
- `PositionTracker.stop_price`는 trailing update로 유리한 방향으로만 이동해야 하며, same-side broker sync 시 초기 하드스톱으로 되돌아가지 않도록 보강돼 있다.
- 분봉차트 active trade는 진입 분봉에 마커가 고정되고, 점선 span만 현재 분봉까지 연장되는 모델을 사용한다.
- 외부체결(HTS/수동) 다계약 사례는 로컬 체결 누락 가능성이 있어, 후속 잔고 refresh 로그로 브로커 수량 일치 여부를 확인해야 한다.

## 2026-05-13 (24차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_marker`) | 청산 아이콘 배지 중심 렌더링에서 텍스트 중심 렌더링으로 단순화 |
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_stamp` 신설) | 청산봉 위치 식별용 소형 스탬프(T/S/P) 마커 추가 |
| `dashboard/main_dashboard.py` (`MinuteChartCanvas._draw_exit_marker`) | TP/SL/PX 색상 팔레트 재정의 + 텍스트 오프셋 조정 |

### 핵심 안전 규칙 (24차 추가)

- **청산 시각정보 우선순위**: 봉 위치 식별(스탬프) + 텍스트 정보(태그/손익/시각)를 함께 제공한다.
- **색상 의미 고정**: TP는 녹색 계열, SL은 적색 계열, PARTIAL/PX는 중성 회색 계열로 고정한다.

---

## 2026-05-13 (23차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` (`run_minute_pipeline`) | 청산 패널 payload 확장: `pending_*`, `time_exit_countdown_sec` 전달 |
| `main.py` (`_ts_push_exit_panel_now` 신설) | Chejan 체결 직후 청산 패널 즉시 갱신 (매분 갱신 대기 제거) |
| `main.py` (`_clear_pending_order`, `_ts_on_chejan_event_cybos_safe`) | pending 소멸/체결 처리 직후 즉시 패널 갱신 호출 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | 배지 enum 기반 상태 렌더링 + 시간청산 카운트다운 표시 + pending EXIT `주문중 n/m` 표시 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | ENTRY pending 시 1/2/3차 목표 배지 `산정중` 강제, 목표 도달 판정 잠금 |
| `dashboard/main_dashboard.py` (`ExitPanel.update_data`) | tp1/tp2/tp3 비정상값(<=0) 방어 정규화 |
| `main.py` (`connect_broker`) | 브로커 동기화 직후 포지션 상태 기반 탭 모드 즉시 정렬 |
| `dashboard/main_dashboard.py` (`UiAutoTabController`) | 수동 탭 전환 유휴 판정에 `hasFocus`/`focusWidget` 반영 |

### 핵심 안전 규칙 (23차 추가)

- **청산 패널 실시간성**: Chejan 체결 이벤트 후 상태 배지는 즉시 갱신한다. 분봉 주기 갱신만으로 주문상태를 표현하지 않는다.
- **ENTRY pending 목표 배지 정책**: ENTRY pending 동안 1/2/3차 목표 배지는 `산정중`만 허용. `도달/완료` 표시는 금지.
- **탭 모드 정렬**: 브로커 동기화 직후 포지션 상태와 탭 모드(청산/진입)는 즉시 일치시킨다.

---

## 2026-05-13 (22차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` (Cybos/Kiwoom 핸들러) | `or unfilled_qty == 0` 제거 — 부분체결 pending 조기 소멸 방지 (B75) |
| `main.py` (`_set_pending_order` 후) | `optimistic_opened`/`partial_fill_count` 플래그 추가 — 낙관적 오픈 분할체결 VWAP 보정 (B76) |
| `main.py` (`_ts_handle_exit_fill`) | `_ts_agg_exit_fill` / `_ts_build_agg_exit_result` 헬퍼 + `is_last_fill` 분기 — EXIT 분할체결 CB/Kelly 단1회 기록 (B77) |
| `main.py` (`_on_manual_exit_requested`) | `_set_pending_order`를 `_send_kiwoom_exit_order` 전으로 이동, 실패 시 `_clear_pending_order` 롤백 (B78-race) |
| `main.py` (`_ts_on_chejan_event_cybos_safe`) | `is_final_fill` 폴백: `status=""` + `fill_qty>0` + `fill_price>0` → 체결로 간주 (B78-status) |
| `main.py` (`_ts_handle_external_fill`) | 최종 청산 후 `_ts_force_balance_flat_ui` + `QTimer(250ms, 1200ms)` 추가 (B78-external) |
| `main.py` (`_ts_push_balance_to_dashboard`) | pending EXIT 존재 시 합성 1계약 행 생성 억제 (B78-synthetic) |
| `dashboard/main_dashboard.py` | `WindowStaysOnTopHint` 제거 — 미륵이 창 최상위 고정 해제 |

### 핵심 안전 규칙 (22차 추가)

- **pending 등록 순서**: 청산 주문 `_set_pending_order` → `_send_order` 순서 (역전 금지). 실패 시 즉시 `_clear_pending_order`
- **Cybos unfilled_qty**: 항상 0 반환 → `or unfilled_qty == 0` 조건 사용 금지. `filled_qty >= qty`만으로 완결 판정
- **EXIT 분할체결 통계**: `is_last_fill`에서만 CB/Kelly 기록. 중간 체결은 로그만

---

## 2026-05-13 (21차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py:1776` | `candle` → `bar` NameError 수정 (B72) |
| `main.py:connect_broker()` | `_futures_code` 확정 후 `position._loaded_futures_code`와 비교 — 불일치 시 강제 FLAT + CRITICAL 로그 (B73) |
| `main.py:_ts_on_chejan_event_cybos_safe` | 체결 이벤트 code ≠ `_futures_code` 시 WARNING + 포지션 반영 거부 (B73) |
| `strategy/position/position_tracker.py` | `_futures_code`/`_loaded_futures_code` 필드, `set_futures_code()`, `force_flat()` 추가. `_save_state()`에 `futures_code` 저장, `load_state()`에서 복원 (B73/D50) |
| `collection/cybos/realtime_data.py` | 캔들 dict에 `"code": self.code` 추가 (B74) |
| `dashboard/main_dashboard.py` | `MinuteChartCanvas._instrument_code` 추가. `on_candle_closed()` — 코드 전환 시 차트 초기화. `_trim_to_last_price_group()` + `reload_today()` 필터 (B74/D51) |

### 핵심 안전 규칙 (21차 추가)

- **재시작 시 코드 불일치 → 강제 FLAT**: `connect_broker()` 완료 후 저장 포지션 코드와 `_futures_code` 비교. 불일치면 포지션 CRITICAL 초기화. HTS에서 해당 종목 수동 확인 필수
- **체결 코드 이중 검증**: `_ts_on_chejan_event_cybos_safe`에서 payload code ≠ `_futures_code` 시 포지션 반영 거부
- **봉차트 코드 전환 감지**: 실시간 캔들에 `code` 포함. `on_candle_closed()`에서 코드 변경 감지 시 기존 캔들 초기화

### 현재 운영 상태

- 오늘 발생한 A0666/A0565 불일치 사고: HTS에서 두 포지션 수동 처리 필요 (모의투자)
  - A0666 SHORT @ 1922.80 — 미청산 상태
  - A0565 LONG @ 1177.3 — 실수로 생성됨
- 미니선물(A0565) 선택 후 재시작 → `[PositionCodeMismatch]` 로그 + 강제 FLAT으로 추가 사고 방지
- 봉차트: 다음 정상 세션부터 단일 종목 캔들만 표시됨

---

## 2026-05-13 (20차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` | 8자리 UI 코드 정규화 (`A0565000→A0565`, 끝 "000" 제거). 미니선물 fallback을 `get_nearest_mini_futures_code()`(FutureMst 프로브)로 교체 |
| `collection/cybos/api_connector.py` | `CpUtil.CpKFutureCode` 사용 완전 제거. `get_nearest_mini_futures_code()` FutureMst 프로브 방식으로 재구현 |
| `collection/broker/cybos_broker.py` | `get_nearest_mini_futures_code()` 위임 메서드 추가 |
| `scripts/check_cybos_realtime.py` | `--mini` 플래그를 FutureMst 프로브 방식으로 교체. FutureMst name 표시 추가 |
| `dashboard/main_dashboard.py` | `WindowStaysOnTopHint` 추가 — 미륵이 UI를 항상 최상위 창으로 유지 |
| `scripts/cybos_autologin.py` | "공지사항" 다이얼로그 자동 닫기 추가. `_handle_mock_select_dialog()` 레거시 함수 제거 |

### 핵심 지식 (Cybos COM 코드 체계 — 2026-05-13 실증)

- `CpUtil.CpFutureCode`: KOSPI200 **일반선물(A01xxx)** 만 열거
- `CpUtil.CpKFutureCode`: **코스닥150 선물(A06xxx)** 만 열거 — 절대 미니선물 탐색에 사용 금지
- **KOSPI200 미니선물(A05xxx)**: 열거 COM 없음. `Dscbo1.FutureMst` 프로브만 가능
- 코드 규칙: `A05 + 연도끝자리 + 월(hex)` — 2026-05=A0565, 2026-06=A0566, 2026-12=A056C
- Cybos COM 실시간 구독(FutureCurOnly)은 **5자리 코드만 수락**. 8자리 코드(A0565000)는 무음 실패

### 현재 운영 상태 (20차 시점 기록)

- 미니선물 실시간 구독: `A0565` 5자리 코드로 정상 구독
- 봇 재시작 후 `[DBG CK-3] 근월물 코드=A0565 is_mini=True` 확인 필수

---

## 2026-05-12 버그 수정 (19차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `dashboard/panels/profit_guard_panel.py` | 수익보존 탭 Apply 설정을 `data/profit_guard_prefs.json`에 저장/복원하도록 영속화 추가 |

### 핵심 변경

- `Apply` 시 `ProfitGuardConfig`를 JSON으로 즉시 저장
- 패널 생성 시 저장값을 UI에 먼저 반영
- `set_profit_guard()` 호출 시 저장값이 있으면 guard 기본값 대신 저장 config를 우선 주입
- 저장 파일이 없거나 파싱 실패 시 기본 config로 안전 폴백

### 현재 운영 상태

- 수익보존 탭의 L1/L2/L3/L4 하단 설정값은 재시작 후에도 유지된다.
- 영속 파일 경로: `data/profit_guard_prefs.json`

---

## 2026-05-12 버그 수정 (18차)

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `scripts/cybos_autologin.py` | `_handle_mock_select_dialog()` 내 `sys.exit(0)` → `return True` — STEP 5 연결 대기 루프 실행되도록 수정 |
| `start_mireuk.bat` | 자동 로그인 성공 후에도 에러 출력되는 `%ERRORLEVEL%` 지연 확장 버그 → `!ERRORLEVEL!` 로 수정 |
| `dashboard/main_dashboard.py` | 종목코드·시장구분 선택값을 `data/ui_prefs.json` 에 저장/복원 (`_save_ui_prefs`, `_restore_ui_prefs`) |
| `config/constants.py` | `get_contract_spec()` 추가 — 일반선물/미니선물 계약 스펙(`pt_value`, `tick_size`, `tick_value`) 반환 |
| `main.py` | UI 선택 종목코드 기준으로 계약 스펙 확정 후 `_pt_value` 를 런타임 전역에 전파 |
| `strategy/position/position_tracker.py` | 인스턴스별 `pt_value` 기반 손익/수수료 계산 |
| `strategy/entry/position_sizer.py` | `pt_value` 기반 리스크 계산 + 미니선물 최소 3계약 규칙 |
| `strategy/entry/entry_manager.py` | 주문 코드 하드코딩 제거, 현재 선택 종목코드 사용 |
| `strategy/exit/exit_manager.py` | 청산 주문 코드/손익 KRW 계산을 현재 계약 스펙 기준으로 통일 |
| `collection/kiwoom/investor_data.py` | 수급 TR 조회 종목코드를 현재 선택 코드와 동기화 |
| `collection/cybos/investor_data.py` | 브로커 인터페이스 호환용 `set_futures_code()` 추가 |
| `dashboard/panels/profit_guard_panel.py` | `sqlite3.Row.get()` Python 3.7 미지원 → `_rows_to_dicts()` 변환 + `_run_simulation_inner()` 분리 + try/except 래핑 |

### 주요 패턴 (재사용 가능)

- **`sqlite3.Row` → `dict` 변환**: Python 3.7에서 `row.get()` 미지원. `dict(row)` 로 변환 후 사용. `_rows_to_dicts()` helper 참고.
- **Windows CMD 지연 확장**: 중첩 `IF` 블록 내 `%ERRORLEVEL%` 는 파싱 시점 고정. 반드시 `!ERRORLEVEL!` 사용 (`SETLOCAL EnableDelayedExpansion` 전제).
- **Qt blockSignals**: 콤보 복원 중 save-during-restore 피드백 루프 방지에 필수.
- **계약 스펙 단일 소스**: 일반/미니선물 구분은 브로커 기본 근월물이 아니라 최종 UI 선택 종목코드에서 한 번만 결정해야 함.

### 현재 운영 상태

- `data/ui_prefs.json` 은 `version`, `market`, `symbol_code`, `symbol_text` 구조로 저장된다.
- 시작 직후 기본 콤보값이 저장 파일을 덮어쓰던 버그는 `_update_symbol_label()` 분리로 해결됐다.
- 현재 저장 파일 기준 마지막 선택값은 `KOSPI200 미니선물 / A0565000` 이다.
- 미니선물 선택 시 손익/사이징/주문 코드/수급 조회 코드가 모두 동일 선택 코드 기준으로 동기화된다.

---

## 2026-05-12 수익 보존 가드 시스템 (ProfitGuard 4-Layer)

### 신규 파일

| 파일 | 역할 |
|---|---|
| `strategy/profit_guard.py` | 4-Layer 수익 보존 핵심 로직 |
| `dashboard/panels/profit_guard_panel.py` | "💰 수익 보존" 대시보드 탭 |

### 4-Layer 설계

| 레이어 | 클래스 | 발동 조건 | 파라미터 기본값 |
|---|---|---|---|
| L1 | `_TrailingGuard` | peak ≥ trail_activation_krw(200만) + 현재 < peak × (1-trail_ratio(35%)) | trail_activation=2_000_000, trail_ratio=0.35 |
| L2 | `_TierGate` | 구간별 최소 size_mult 미달 시 차단, 400만+ = max_qty=0 (완전 정지) | tiers: 0/100/200/300/400만 |
| L3 | `_AfternoonMode` | 오후 기준 시간 이후 + 수익 발생 + 진입 횟수 초과 | cutoff_hour=13, max_trades=3 |
| L4 | `_ProfitCB` | 수익 중 N연속 손실 | profit_cb_consec_loss=2, trigger_threshold=150만 |

### main.py 연결 포인트

| 위치 | 동작 |
|---|---|
| `__init__()` | `self.profit_guard = ProfitGuard()` 초기화 |
| STEP 7 진입 전 | `is_entry_allowed(daily_pnl, size_mult)` → grade=X 강제 적용 |
| `_post_exit()` | `on_trade_close(pnl_krw, daily_pnl)` → L4 CB 갱신 |
| `_execute_entry()` | `on_entry()` → L3 오후 카운터 갱신 |
| `daily_close()` | `reset_daily()` → 전체 상태 초기화 |
| `_refresh_pnl_history()` | `dashboard.refresh_profit_guard(pnl, trades)` |

### 대시보드 탭 구성 ("💰 수익 보존")

- **상태 섹션**: L1~L4 레이어 배지 + 핵심 지표 5개 + PnL DNA 시각화 (pyqtSignal 연동)
- **설정 섹션**: QSlider(trail_ratio) + QSpinBox(임계값·기준) + Apply/Reset 버튼
- **비교 섹션**: 챔피언 vs 챌린저 6행 테이블 + 차단 거래 목록
- **제안 섹션**: 3-variant 챌린저 제안표 + 황금 시간대 막대 차트 + 차단 로그

### simulate() 활용

`ProfitGuard.simulate(trades, cfg)` 정적 메서드로 과거 거래 리스트를 대입해 챔피언(가드 없음) vs 챌린저(가드 적용) 총손익·MDD·차단수를 비교할 수 있다.

---

## 2026-05-12 챔피언-도전자 시스템 (Phase C-1 ~ C-8 + 레짐 전문가 확장)

### 신규 파일 목록

| 파일 | 역할 |
|---|---|
| `challenger/__init__.py` | 패키지 init |
| `challenger/variants/__init__.py` | 패키지 init |
| `challenger/variants/base_challenger.py` | 추상 기저: `ChallengerSignal`, `ChallengerTrade`, `BaseChallenger` |
| `challenger/challenger_db.py` | SQLite CRUD (`challenger.db`) — 6개 테이블 |
| `challenger/challenger_registry.py` | 도전자 풀 + 레짐별 챔피언 포인터 관리 |
| `challenger/challenger_engine.py` | Shadow 실행 오케스트레이터 (매분 훅, <5ms 목표) |
| `challenger/promotion_manager.py` | 전역 승격 + 레짐 전문가 승격 (수동 승인 필수) |
| `challenger/variants/cvd_exhaustion.py` | CVD 탈진 도전자 (A) |
| `challenger/variants/ofi_reversal.py` | OFI 반전 도전자 (B) |
| `challenger/variants/vwap_reversal.py` | VWAP 반전 도전자 (C) |
| `challenger/variants/exhaustion_regime.py` | 탈진 레짐 특화 도전자 (D) |
| `challenger/variants/absorption.py` | 흡수 감지 도전자 (E, FutureJpBid 필요) |
| `features/technical/cvd_exhaustion.py` | CVD 탈진 피처 계산기 |
| `features/technical/ofi_reversal.py` | OFI 반전 피처 계산기 |
| `dashboard/panels/__init__.py` | 패키지 init |
| `dashboard/panels/challenger_panel.py` | 도전자 모니터 패널 (레짐 전문가 승위표 + 전체 성과) |

### 핵심 설계 결정

- **레짐 전문가 풀**: `탈진 → [A_CVD, C_VWAP, D_EXHAUSTION]` / `추세·횡보·혼합 → CHAMPION_BASELINE` / `급변장 → []`
- **승격 기준**: 레짐 내 거래 수 기반 (`min_regime_trades: 20`) — 달력일 무관
- **자동 승격 금지**: Shadow 1위 변경 시 대시보드 WARNING만 발송, 실거래 전환은 수동 승인
- **레짐 챔피언 게이트** (`main.py [§20]`): `탈진` 레짐에서 챔피언=None이면 진입 차단

### DB 스키마 (`challenger.db`)

```
challenger_signals       — 매분 신호 (regime 컬럼 포함)
challenger_trades        — 가상 거래 (regime 컬럼 포함)
challenger_daily_metrics — 전체 일별 집계
challenger_regime_metrics— 레짐별 누적 집계 (trade_count 기반 승격 판단)
regime_rank_history      — 레짐별 1위 변경 이력
champion_history         — 챔피언 교체 이력
```

### main.py 연결 포인트

| 위치 | 동작 |
|---|---|
| `__init__()` | `ChallengerEngine` + `PromotionManager` 초기화 (실패 시 None) |
| STEP 9 이후 | `challenger_engine.run_shadow()` — 5ms 가드 포함 |
| STEP 6 [§20] | 레짐 챔피언 게이트 — 챔피언=None 레짐 진입 차단 |
| `daily_close()` | `update_daily_metrics()` — 레짐별 순위 계산 + WARNING 발송 |
| `DashboardAdapter` | `set_challenger_engine()` — 패널에 엔진 주입 |

### 잔여 연결 작업

- `탈진` 레짐 챔피언이 특정 도전자로 승격됐을 때, 해당 도전자의 신호를 앙상블 `direction`으로 오버라이드하는 로직 (현재: 앙상블 신호 유지 + 로그만)
- `AbsorptionChallenger` — `FutureJpBid` 호가 구독 연결 (`update_hoga()` 훅)
- `탈진` 레짐 피처 (`cvd_exhaustion`, `ofi_reversal_speed`) feature_builder 실데이터 검증

---

## 2026-05-11 Cybos Plus 리팩토링 완료 (브로커 전환 마일스톤)

미륵이의 데이터 수집·자동매매 백엔드가 **키움 OpenAPI+ → Cybos Plus(대신증권)** 으로 전면 리팩토링됐다.

| 구분 | 이전 (키움) | 현재 (Cybos Plus) |
|---|---|---|
| 실시간 틱 | `OPT50029` SetRealReg | `Dscbo1.FutureCurOnly` Subscribe |
| 호가 | `FID` 기반 실시간 | `CpSysDib.FutureJpBid` Subscribe |
| 잔고 | `OPW20006` TR | `CpTrade.CpTd0723` BlockRequest |
| 일일손익 | `OPW20003/7/8` TR | `CpTrade.CpTd6197` BlockRequest |
| 주문 | `SendOrderFO` | `CpTrade.CpTd6831` BlockRequest |
| 체결 이벤트 | `OnReceiveChejanData` | `Dscbo1.CpFConclusion` Subscribe |
| 투자자 수급 | `opt10059`, `opt50008` | **`CpSysDib.CpSvrNew7212` (idx0=1) 확정** — 선물/콜/풋 투자자별 순매수 제공 |
| 선물 스냅샷 | `OPT10001` | `Dscbo1.FutureMst` BlockRequest |
| 브로커 팩토리 | `KiwoomBroker` 하드코딩 | `create_broker()` → 기본 `cybos` |

### 11차 세션에서 추가된 것 (2026-05-11)

- `collection/cybos/api_connector.py`: `_probe_investor_tr()` 헬퍼 + `request_investor_futures()` / `request_program_investor()` 다중 후보 실구현
- `collection/cybos/investor_data.py`: `_open_interest`, `program_arb`, `program_nonarb` 필드 추가 및 `get_panel_data()` 확장
- `collection/cybos/realtime_data.py`: `_last_oi` — `FutureCurOnly` 헤더 14번 미결제약정 실시간 저장
- `dashboard/main_dashboard.py`: `DivergencePanel`에 **선물 투자자 수급** 섹션 추가 (외인/개인/기관 순매수 + 프로그램 차익/비차익 + 미결제약정 2×3 그리드)
- `main.py`: `_fetch_investor_data()`에서 `realtime_data._last_oi` → `investor_data._open_interest` 동기화

### 12차 세션에서 추가된 것 (2026-05-11)

- `collection/cybos/api_connector.py`:
  - `_FUTURES_INVESTOR_NAME_MAP` 추가 (한글 투자자명 → INVESTOR_KEYS)
  - `request_investor_futures()` candidates 1순위: `CpSysDib.CpSvrNew7212 [(0,1)]`
  - New7212 전용 파싱 분기: row[3]=선물, row[6]=콜, row[9]=풋 순매수
  - `request_program_investor()` candidates: `Dscbo1.CpSvr8119`, `Dscbo1.CpSvrNew8119` 추가. 전체 0 시 skip.
- `collection/cybos/investor_data.py`:
  - `fetch_futures_investor()`: call_nets/put_nets → `_call/_put` 반영, `option_flow_supported` 자동 활성화
  - `get_panel_data()`: rt_call/rt_put/fi_call/fi_put/rt_bias/fi_bias **하드코딩 0 → 실제값** [B54 수정]
  - 상태 텍스트: option_flow_supported 시 자동 갱신
- `dashboard/main_dashboard.py`: 역발상 신호 색상 반전 (`'매수'`→빨간색, `'매도'`→초록색) [D33]
- `config/constants.py`: `CORE_FEATURES` `"ofi_imbalance"` → `"ofi_norm"` [B55 수정]
- 신규 스크립트: `scripts/run_cybos_investor_discovery.py`, `scripts/_probe_7212_dates.py`, `scripts/_probe_8119_fields.py`

### 잔여 검증 항목

- `_probe_8119_fields.py` 장 중(09:00~15:30) 실행 → `Dscbo1.CpSvr8119` h[0~5] 레이아웃 확인
- 실제 파이프라인 매분 업데이트 시 투자자 수급 데이터 흐름 확인 ("대기" → 실수치 전환)
- 장중 `FutureCurOnly` 분봉 timestamp 진행 확인
- `CpTd6831` 모의 주문 체결 end-to-end 검증
- `CybosInvestorRaw 후보 없음` 09:00~10:44 갭 원인 조사 (7건 거래가 모두 이 구간에서 발생)

---

## 2026-05-12 버그 수정 현황

| 버그 | 파일 | 상태 |
|---|---|---|
| MetaConf `loss="log_loss"` (sklearn 1.0.2 호환성) | `learning/meta_confidence.py` | ✅ 수정 완료 |
| 계좌번호 Kiwoom 잔여값 `7034809431` | `config/secrets.py` | ✅ 수정 완료 (gitignore, 미커밋) |
| ExitCooldown 중복 로그 (2회/청산) | `main.py` | ✅ 수정 완료 |
| CB HALTED 이후 Sizer 계속 실행 | `main.py` | ✅ 수정 완료 |
| TRADE.log 한글 깨짐 3곳 | `strategy/position/position_tracker.py` | ✅ 수정 완료 |
| `liquidation_eval=0` 대체 시 경고 없음 | `collection/cybos/api_connector.py` | ✅ 수정 완료 |
| `CybosInvestorRaw 후보 없음` 분당 WARNING 폭주 | `collection/cybos/api_connector.py` | ✅ 수정 완료 (레이트리밋 INFO, 10분 간격) |
| `profit_rate 이상값` 반복 WARNING 폭주 | `collection/cybos/api_connector.py` | ✅ 수정 완료 (`>200%`만 WARNING, 나머지 레이트리밋 INFO) |
| `BalanceUI/BalanceRefresh` 진단 로그 WARNING 과다 | `main.py` | ✅ 수정 완료 (반복성 로그 레이트리밋 INFO) |

### 2026-05-12 경고 재분류 운영 원칙

- 반복성 진단 로그는 INFO(레이트리밋)로 유지하고, 장애성/조치 필요 이벤트만 WARNING 이상으로 유지한다.
- 현재 적용 범위:
  - `CybosInvestorRaw ... 후보 없음`
  - `CybosDailyPnl profit_rate 이상값`
  - `BalanceUI/BalanceRefresh`의 주기성 상태 로그
- WARNING 유지 항목 예시:
  - 브로커 요청 실패(`request returned None`)
  - 필수 입력 누락(`empty account number`)
  - CB/주문 불일치/강제 리스크 이벤트

### MetaConf 오류 인과관계 (2026-05-12 장 중 확인)

```
MetaConf loss="log_loss" 미지원 오류 (sklearn 1.0.2)
→ 6개 호라이즌 × 모든 분봉 학습 실패
→ SGD 온라인학습 미동작 (weight 44%→10%→30% 진동)
→ 메타 신뢰도 보정 없는 앙상블
→ 30분 정확도 19% (CB 임계 35% 미달)
→ CB ③ 10:20:59 당일 정지
```

---

## 2026-05-11 Cybos balance / daily pnl / exit UI state

| Item | Current status |
|---|---|
| Meta confidence training | invalid/ragged feature vectors are filtered before fit/buffer; repeated `MetaConf` shape error is no longer observed in restart logs |
| Position sizing balance source | `PositionSizer` now consumes the latest broker balance summary instead of relying on the old fixed `100,000,000` KRW fallback |
| Cybos daily pnl summary | `CpTd6197` is wired into broker balance flow and logs validation details into `SYSTEM.log` |
| Source of truth for Cybos summary mapping | raw `SYSTEM.log` / `CpTd6197` headers are authoritative; HTS is reference-only |
| Current validated Cybos header mapping | `1=예탁현금`, `2=익일가예탁현금`, `5=전일손익`, `6=금일손익`, `9=청산후총평가금액` |
| Current mock-environment observation | `header 2 == header 9`, `header 5 == 0` |
| Dashboard balance refresh UX | account panel now uses `잔고 새로고침` and `F5` for balance-only refresh |
| Final exit UI sync | on confirmed final exit to `FLAT`, dashboard balance rows are now cleared immediately before broker refresh retries |

### Current operational interpretation

- If HTS and Cybos raw summary look different, trust the logged `CpTd6197` payload first.
- A stale balance row after exit is treated as a UI sync defect, not as proof that the position is still open.
- Broker refresh after final exit is intentionally retried because Cybos COM timing can lag immediately after fill confirmation.

## 2026-05-10 Cybos Plus status update

| Item | Current status |
|---|---|
| Broker abstraction | `main.py` now runs through `create_broker()` and can launch either Kiwoom or Cybos broker backends |
| Cybos connection | `CybosAPI` can connect successfully on 32-bit Python + pywin32 with active CybosPlus SignOn |
| Cybos balance sync | `CpTd0723` startup sync works; empty mock balance is interpreted as `FLAT` |
| Cybos snapshot | `FutureMst` field mapping has been corrected against live snapshot output |
| Cybos realtime wiring | `FutureCurOnly` and `FutureJpBid` subscription wrappers are implemented and startup successfully |
| Cybos order/fill wiring | `CpTd6831` order path and `CpFConclusion` fill event path are implemented, but full live mock validation is still pending |
| Cybos account selection | runtime now falls back to the currently signed-on Cybos account if `config/secrets.py` contains an account not present in the active broker session |
| Investor flow on Cybos | still placeholder / zero-data implementation |
| Test launcher | `start_mireuk_cybos_test.bat` available for safe Cybos-only trial runs without changing default Kiwoom startup |
| Session checker | `scripts/check_cybos_session.py` available for connection/balance/snapshot/realtime/order smoke tests |

### Cybos-specific known gaps

- Live market verification is still incomplete because the latest trial run was performed on `2026-05-10`, a Sunday, with market state `99`.
- Dashboard stylesheet parsing warnings are still present during startup and should be separated from broker/runtime debugging.
- Server label compatibility currently returns a Kiwoom-compatible `"0"` into main flow to avoid false mock-only branches; this should be replaced with a Cybos-native label strategy later.

## 2026-05-08 최신 반영 - 장마감 자동종료/봉차트 UX 보강
| 항목 | 현재 상태 |
|---|---|
| 당일 자동종료 재실행 방지 | 같은 날짜에 자동종료가 이미 끝난 뒤 수동 재시작해도 `daily_close()`와 `_auto_shutdown()`이 다시 실행되지 않도록 복구/가드 이중 방어 적용 |
| 자동종료 상태 복원 | `data/session_state.json`의 `auto_shutdown_done_date`가 오늘이고 장마감 이후면 `_daily_close_done = True`까지 함께 복원 |
| 차트 우측 여백 | 봉차트/분차트 마지막 봉 오른쪽에 10봉 크기 패딩을 줘서 마커와 라벨이 가장자리에 붙지 않음 |
| 진입 마커 시인성 | LONG/SHORT 진입 마커를 더 큰 배지형 스타일로 변경하고, 겹침 회피 로직 추가 |
| LONG/SL 라벨 분리 | `LONG` 라벨은 항상 위쪽, `SL` 라벨칩은 항상 아래쪽으로 더 강하게 분리 |
| 봉차트 단축키 | 단축키 재입력 시 봉차트 윈도우가 닫히는 토글 방식으로 변경 |

### 현재 운영 해석

- 장마감 자동종료는 이제 "당일 1회성 작업"으로 더 강하게 고정되어, 수동 재시작이 후속 종료를 다시 트리거하지 않도록 설계됐다.
- 봉차트는 단순 조회창이 아니라 진입/손절 맥락을 빠르게 읽는 운영 도구로 방향을 더 분명히 잡았다.
- 특히 `LONG` 진입과 `SL` 마커가 같은 봉에 붙는 상황에서 위/아래 레이어를 강제로 분리해 장중 판독 부담을 줄였다.

### 아직 운영 확인 필요한 항목

- 같은 날짜 `15:40` 이후 수동 재시작 시 자동 종료 알림/프로그램 종료가 재실행되지 않는지 확인 필요
- 실제 장중 데이터에서 진입/손절 마커가 여러 개 겹칠 때 현재 충돌 회피 강도가 충분한지 확인 필요
- 봉차트 단축키 토글이 포커스 상태와 무관하게 일관되게 동작하는지 확인 필요

---

## 2026-05-08 최신 반영 - 청산관리 고도화

| 항목 | 현재 상태 |
|---|---|
| 1계약 TP1 처리 | 더 이상 `TP1(전량)`으로 바로 끝나지 않음. `본절보호 / 본절+alpha / ATR 기반 보호이익` 중 선택한 보호전환 모드가 적용됨 |
| TP1 보호전환 UI | 청산관리 탭에서 클릭형 버튼 3개로 선택 가능. 각 버튼에 설명 툴팁 부착 완료 |
| 보호전환 설정 저장 | `data/session_state.json`의 `tp1_single_contract_mode`로 저장/복원 |
| 수동청산 버튼 | 청산관리 탭 `33% / 50% / 전량 청산` 버튼이 실제 주문으로 연결됨 |
| 1계약 수동청산 예외 | 1계약에서 `33%` 또는 `50%` 클릭 시 자동으로 `전량청산`으로 승격 |
| 수동 부분청산 후처리 | `EXIT_MANUAL_PARTIAL` pending kind로 분리되어 자동 TP1/TP2 단계 처리와 충돌하지 않음 |
| 한글 표시 안정화 | 신규 청산관리 탭 문자열은 유니코드 이스케이프 기반으로 넣어 인코딩 깨짐 재발 가능성을 낮춤 |

### 현재 운영 해석

- 청산관리 탭은 이제 상태 표시만 하는 패널이 아니라, TP1 보호전환 설정과 수동청산 실행까지 담당하는 운영 패널이다.
- 1계약 기대값 악화의 핵심이던 `TP1 전량청산` 구조는 제거되었고, 같은 1계약이라도 보호방식을 장중에 바꿔 비교할 수 있다.
- 수동청산은 시장가 기준이므로, 사용 목적은 "전략 청산 대체"보다는 "운영 개입용 안전장치"에 가깝다.

### 아직 남은 확인 사항

- 실제 장중에 TP1 보호전환 3모드가 각각 의도한 스톱 위치로 이동하는지 검증 필요
- `33% / 50% / 전량 청산` 버튼 클릭 후 Kiwoom 체결과 dashboard PnL 갱신이 일관되게 들어오는지 검증 필요
- 1계약 상태에서 `33% / 50%` 클릭 시 WARN/TRADE 로그에 전량승격 의도가 충분히 드러나는지 추가 확인 필요

---

## 2026-05-08 최신 반영 - 역방향진입 실행 오버레이 / 순방향 학습 방화벽

| 항목 | 현재 상태 |
|---|---|
| 역방향진입 토글 | 진입관리 패널 상단에 `역방향 진입` 토글 추가 완료. 자동진입 판단에만 적용되고 수동진입 버튼에는 적용되지 않음 |
| 원신호/실행신호 표시 | 진입관리 패널에 `원신호`, `실행신호` 동시 표시 완료 |
| 로그 반영 | `TRADE`, `SIGNAL` 로그에 `원신호`, `실행신호`, `역방향진입=ON/OFF` 기록 완료 |
| 세션 유지 | `data/session_state.json`에 `reverse_entry_enabled` 저장/복원 완료 |
| 손익 PnL 카드 | `실행 / 순방향` 손익을 동시에 표시하도록 확장 완료 |
| 손익 추이 탭 | 일별/주별/월별 표와 요약 카드에 `실행 / 순` 병기 완료 |
| trades 저장 구조 | `raw_direction`, `executed_direction`, `reverse_entry_enabled`, `forward_*` 컬럼 저장 완료 |
| 학습/통계 방화벽 | 등급 통계, 레짐 통계, 추이 통계, daily PF, daily close snapshot이 순방향 손익 기준으로 동작하도록 수정 완료 |

### 현재 운영 해석

- 순방향 시그널은 전략 본체다.
- 역방향진입은 전략 변경이 아니라 `최종 실행 오버레이 + PnL 비교 수단`이다.
- 따라서 수집/학습/통계/효과검증은 순방향 기준을 유지하고, UI와 주문 실행에서만 역방향 결과를 분리해 본다.

### 남아 있는 확인 포인트

- 실제 UI에서 `역방향진입` ON/OFF 후 진입관리 패널 문구가 기대대로 바뀌는지 확인 필요
- 실제 청산 1회 이상 후 손익 PnL 카드와 손익 추이 탭의 `실행 / 순방향` 값이 모두 채워지는지 확인 필요
- 효과검증 패널 수치가 역방향 실행 손익에 오염되지 않는지 다음 세션 실거래/모의 로그로 최종 검증 필요

## 운영 환경

| 항목 | 값 |
|---|---|
| Python | 3.7 32-bit (`py37_32`) |
| 선물 분봉 TR | OPT50029 (수정 완료 — 구: OPT10080) |
| 모드 | 모의투자 (실전 미전환) |

---

## Phase 완료 현황

| Phase | 코드 | 검증 상태 |
|---|---|---|
| Phase 0 — 설계·인프라 | ✅ | ✅ 완료 |
| Phase 1 — 핵심 시스템 | ✅ | ⏳ 모의계좌 실시간 동작 확인 필요 |
| Phase 2 — 안전장치·백테스트 | ✅ | ⏳ CB 5종 테스트 + 26주 WF 데이터 필요 |
| Phase 3 — 알파 강화 | ✅ | ⏳ 실데이터 정확도 검증 필요 |
| Phase 4 — 차별화 (RL·베이지안·뉴스) | ✅ | ⏳ 실거래 데이터 검증 필요 |
| Phase 5 — 실전 운영 | — | 미진입 |
| Phase 6 — 알파 리서치 봇 | ✅ (유전자 진화 완료) | ⏳ main.py 연결 미완 |

---

## 2026-05-08 세션 주요 수정 (6차) — PnL 승수 수정 + CB③ 개선 + 진입 게이트 보강

### 핵심 변경 사항

**버그 수정 2건 (수익률 직결)**

| 버그 | 원인 | 수정 파일 |
|---|---|---|
| **[B64] PnL 2× 과대 계산** | `FUTURES_MULTIPLIER = 500_000` — KOSPI200 선물 승수는 250,000원/pt | `config/constants.py` FUTURES_MULTIPLIER·FUTURES_TICK_VALUE 수정, `FUTURES_PT_VALUE` 신설. `main.py` 전수 교체 |
| **[B65] 수수료 미반영** | `close_position()` / `partial_close()` / `apply_exit_fill()`에서 pnl_krw 계산 시 수수료(왕복 ~79,500원/계약) 미차감 | `position_tracker.py` — `_calc_commission()` 추가, 3개 청산 경로 모두 적용. `FUTURES_COMMISSION_RATE = 0.000015` settings.py에 추가 |

**CB③ 개선 2건**

| 항목 | 수정 |
|---|---|
| **30m 전용 정확도 피드** | `main.py` STEP 1 `record_accuracy()` 호출에 `v["horizon"] == "30m"` 필터 추가. 기존: 6개 호라이즌 혼합 → 3샘플에서 HALT 발동 |
| **2회 연속 미달 시 HALT** | `circuit_breaker.py` — 1회 미달: WARNING+Slack만, 2회 연속 미달: HALT. 최소 20샘플 확보 후 발동 |

**진입 게이트 보강 3건 (20260508 WARN.log 분석 결과)**

| 조건 | 설명 | 효과 |
|---|---|---|
| **Hurst < 0.45 차단** | `main.py` STEP 7에 `features.get("hurst") >= HURST_RANGE_THRESHOLD` 추가. settings.py에 이미 있던 상수가 실제 게이트에 미연결이었음 | 횡보 레짐 진입 차단 |
| **청산 후 쿨다운** | `_post_exit()` — TP청산 후 2분, 손절청산 후 3분 재진입 금지 (`_exit_cooldown_until`) | 10:13 TP→10:14 즉시재진입, 10:24 스톱→10:25 재진입 패턴 차단 |
| **ATR < 1.0pt 차단** | `ATR_MIN_ENTRY = 1.0` settings.py 추가, STEP 7에 `atr >= ATR_MIN_ENTRY` 조건 추가 | 변동성 부족 구간(ATR=1.37pt) 진입으로 인한 휩쏘 손절 방지 |

### 20260508 WARN.log 분석 요약

| 시각 | 이벤트 | 수정 전 | 수정 후 |
|---|---|---|---|
| 09:34 | CB③ HALT (3샘플, 전 호라이즌 혼합) | 시스템 정지 → 오전 기회 손실 | **방어됨** — 30m 필터 + 20샘플 최소 |
| 10:14 | TP1(10:13) 후 1분 재진입 | 진입 실행 | **차단** — ExitCooldown 2분 |
| 10:24 | 스톱 후 10:25 즉시 재진입 | 진입 실행 → CB② 2/3 도달 | **차단** — ExitCooldown 3분 |

---

## 2026-05-08 세션 주요 수정 (8차) — PnL 기준 통일 + trades.db 정규화 + 잔고/손익 추이 일치화

### 핵심 변경 사항

**PnL 정규화 4건**

| 항목 | 원인 | 수정 |
|---|---|---|
| **`trades.db` 혼합 손익 정규화** | 같은 날짜 거래 안에 `500,000원/pt` 구식 값과 `250,000원/pt - 수수료` 신규 값이 혼재 | `utils/db_utils.py` migration 추가. 기존 `trades.pnl_krw`를 현재 공식으로 일괄 재계산 |
| **정규화 컬럼 추가** | `pnl_krw` 단일 컬럼만으로는 계산 버전/수수료 분리 불가 | `gross_pnl_krw`, `commission_krw`, `net_pnl_krw`, `formula_version` 추가 |
| **거래 저장 경로 통일** | 일부 경로는 구식 저장값을 그대로 INSERT할 위험 | `main.py` 3개 `INSERT INTO trades` 경로 모두 `normalize_trade_pnl()` 사용 |
| **손익 추이 날짜 기준 수정** | 실현손익인데 `entry_ts` 기준 일자 집계 사용 | `fetch_today_trades()`, `fetch_pnl_history()`, `PnlHistoryPanel.refresh()`를 `exit_ts` 기준으로 보정 |

**잔고 패널 안정화 3건**

| 항목 | 수정 |
|---|---|
| **실현손익 fallback 우선순위 보정** | `오늘 정규화 거래합계 -> 마지막 정상 브로커 실현손익 캐시 -> PositionTracker.daily_stats()` 순으로 적용 |
| **TR blank 시 0 덮어쓰기 완화** | `OPW20006` summary blank일 때 직전 정상 브로커 `실현손익`을 당일 캐시로 유지 |
| **재시작 복원 중복 누적 방지** | `_restore_daily_state()`에서 `restore_daily_stats()` 호출 전에 `self.position.reset_daily()` 실행 |

**일일 통계 보정 1건**

| 항목 | 수정 |
|---|---|
| **수수료 리셋 누락** | `PositionTracker.reset_daily()`에 `_daily_commission = 0.0` 추가 |

### 현재 운영 기준

- `손익 추이`의 오늘 값은 이제 `trades.db`의 `net_pnl_krw` 합계와 일치해야 한다.
- 잔고 패널 `실현손익` fallback도 같은 정규화 기준을 사용하므로, 브로커 원문 공란 시 내부 UI끼리 값이 갈라지지 않아야 한다.
- `trades` 테이블의 손익 계산 기준 버전은 `formula_version = 2` 이다.

### 세션 검증 결과

- `fetch_today_trades('2026-05-08')` 합계: `-1,618,766원`
- `trades` 오늘 27건 전체 `formula_version = 2` 정규화 완료
- 정규화 샘플:
  - `pnl_pts=+1.50`
  - `gross_pnl_krw=375,000`
  - `commission_krw=8,645`
  - `net_pnl_krw=366,355`

---

## 2026-05-07 세션 주요 수정 (5차) — Phase 5 QA + strategy_events + shadow IPC

### 핵심 변경 사항

**Phase 5 컴포넌트 구조 (STRATEGY_PARAMS_GUIDE §1~§20 93% 구현 완료)**

| 컴포넌트 | 파일 | 상태 |
|---|---|---|
| StrategyRegistry + strategy_events 테이블 | `config/strategy_registry.py` | ✅ 완료 |
| Shadow candidate IPC (JSON 파일) | `data/shadow_candidate.json` | ✅ 완료 |
| ShadowEvaluator 초기화 (`start_shadow_mode`) | `main.py` | ✅ 완료 |
| HotSwapGate 이벤트 기록 | `strategy/ops/hotswap_gate.py` | ✅ 완료 |
| 전략 대시보드 이벤트 로그 표시 | `dashboard/strategy_dashboard_tab.py` | ✅ 완료 |

**Shadow candidate 흐름**:
```
param_optimizer.propose_for_shadow()
  → data/shadow_candidate.json 기록 (live 파라미터 변경 없음)
    → daily_close() → _load_shadow_candidate()
      → start_shadow_mode() → ShadowEvaluator 인스턴스화
        → (2주 후) HotSwapGate.attempt()
          → 통과: _execute_hotswap() → PARAM_CURRENT 업데이트 + JSON 삭제
          → 거부: log_event("HOTSWAP_DENIED") + 1주 추가 관찰
```

**QA 버그 3종 수정**:
- `%+,.0f` → `%+.0f` (Python 3.7 `%` 포매팅 comma 미지원)
- `det.get_level()` → `max(det.get_levels().values())` (`MultiMetricDriftDetector` API)
- QA 세더 cp949 콘솔 UnicodeEncodeError fallback 추가

---

## 2026-05-07 세션 주요 수정 (4차) — B60~B63 잔고 패널 수치 수정 + 모의서버 포지션 복원 버튼

### 오늘 세션 요약

**계기**: HTS 실시간 잔고와 미륵이 대시보드 잔고 패널 수치 불일치 (총매매 576,500원 vs HTS 288,250,000원).
재시작 후 대시보드 전체 0.00 표시 문제도 동시에 진단.

| 버그 | 원인 | 수정 |
|---|---|---|
| **[B60] 합성 잔고행 PnL 배수 오류** | `_eval_krw = entry × qty × 500_000/1000 = 500원/pt`  KOSPI200 승수=250,000원/pt | `× 250_000` 직접 계산. `_pnl_krw`도 동일 수정 |
| **[B61] 총평가손익 blank (pnl=0 시)** | guard `if pnl_sum or not rows`가 pnl=0+rows=비어있지않음 → False → 미설정 | `if not str(summary.get(...) or "").strip():` — 조건 단순화 |
| **[B61-2] 청산가능 컬럼 blank** | 합성행 key `"청산가능"` ≠ dashboard col-3 key `"주문가능수량"` | key → `"주문가능수량": str(_qty)` |
| **[B62] 모의서버 startup sync FLAT 오염** | 재시작 시 OPW20006 blank rows → FLAT 강제 기록 → position_state.json 덮어씀 → 다음 재시작 FLAT 시작 | `GetServerGubun=="1"` 판정 추가. 모의+blank+비FLAT → FLAT 결정 skip |
| **[B63] 포지션 수동 복원 버튼 설계** | 재시작 후 모의서버 blank로 포지션 정보 소실 시 복구 수단 없음 | `PositionRestoreDialog` + `AccountInfoPanel.btn_position_restore` 신설 |

### 핵심 확인 사항 (오늘 세션)

- **KOSPI200 선물 계약 승수 = 250,000원/pt** (2017년 이후). 기존 코드가 `500_000/1000=500`으로 500배 틀렸음.
- **모의투자 서버 OPW20006 응답 = 항상 blank**. row 구조는 있지만 모든 필드가 빈 문자열. 정상 동작.
- **15:10 강제청산 정상 작동 확인**: `position_state.json` `last_update_reason="apply_exit_fill_final:15:10 강제청산"` 2026-05-07 15:25:59 기록.

### 수정 후 잔고 패널 동작 흐름

```
startup sync → OPW20006 blank rows
  → GetServerGubun == "1" (모의서버) AND position != FLAT
    → FLAT 결정 skip → 저장 포지션 유지 [B62]
  → _ts_push_balance_to_dashboard():
      _has_real_row = False → 합성 잔고행 생성 [B60]
      _eval_krw = entry × qty × 250_000 (pt→KRW)
      _pnl_krw = pnl_pts × 250_000
      "주문가능수량": str(_qty)  [B61-2]
  → summary guard: str(v or "").strip() 체크 [B61]
  → 대시보드 잔고 패널 갱신

수동 복원 버튼 [B63]:
  "포지션 복원" 버튼 클릭 → PositionRestoreDialog (방향/가격/수량/ATR)
  → sig_position_restore.emit() → _manual_position_restore()
  → position.sync_from_broker() → _recalculate_levels(atr)
  → QTimer.singleShot(300ms) → _ts_refresh_dashboard_balance()
```

### 수정된 파일

| 파일 | 수정 내용 |
|---|---|
| `main.py` | `_ts_push_balance_to_dashboard`: B60/B61 수정. `_ts_sync_position_from_broker`: B62 모의서버 분기. `_ts_manual_position_restore`: B63 신설. monkey-patch 추가 |
| `dashboard/main_dashboard.py` | `PositionRestoreDialog` 신설. `AccountInfoPanel`: `sig_position_restore` signal + `btn_position_restore` + tooltip. `DashboardFacade`: signal 노출 |

---

## 2026-05-07 세션 주요 수정 (3) — B56: ENTRY 재진입 루프 쿨다운 중앙화

### 오늘 세션 요약 (오후)

**발생 현상**: 09:56~10:07 구간에서 ENTRY 주문이 2분마다 8회 반복 발생.
B52·B53(쿨다운 설정) 코드가 이미 있었지만 `_entry_cooldown_until`이 실제로 설정되지 않는 케이스가 존재했음:
1. B52 쿨다운이 `_optimistic==True` 조건에만 종속 → `_optimistic=False`이면 쿨다운 미설정
2. `_ts_on_order_message` 거부 경로에서 `_clear_pending_order()` 호출 시 쿨다운 없음
3. balance Chejan FLAT 경로(`_ts_sync_from_balance_payload`)도 쿨다운 없음

**근본 수정 [B56]**: 쿨다운 설정 로직을 `_clear_pending_order()`에 중앙화.
ENTRY 미체결(`filled_qty=0`) 소멸이면 **어떤 경로든** 2분 쿨다운 자동 설정.

| 항목 | 수정 내용 |
|---|---|
| **[B56] `_clear_pending_order()` 중앙화** | `kind=="ENTRY" and filled_qty==0`이면 `_entry_cooldown_until = now+2min`. B52/order_reject/balance_FLAT 등 모든 경로 커버 |
| **[B52] `_optimistic` 의존 분리** | `_reset_position()`은 여전히 `_optimistic==True` 조건. 쿨다운은 무조건 설정 (B56 중앙화로 이중 설정이지만 무해) |
| **[B56] balance Chejan FLAT 경로 주석 추가** | `_ts_sync_from_balance_payload` qty<=0 분기에 B56 자동 적용 설명 추가 |

### 수정 후 `_clear_pending_order()` 흐름

```python
def _clear_pending_order(self) -> None:
    if self._pending_order is not None:
        logger.warning("[PendingOrder] clear %s", self._pending_order)
        # [B56] ENTRY 미체결 소멸 → 어떤 경로든 2분 재진입 금지
        if (self._pending_order.get("kind") == "ENTRY"
                and self._pending_order.get("filled_qty", 0) == 0):
            self._entry_cooldown_until = now + 2min
            logger.warning("[EntryCooldown] ... until HH:MM:SS")
    self._pending_order = None
```

### 추가 확인 사항

- **[V42] SHORT 진입 Chejan 수신 확인**: CB③ 발동으로 이번 세션에서 SHORT 미발생. 다음 세션 확인
- **[V39] ENTRY 타임아웃 복원 로그**: `[FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원` 대시보드 SYSTEM 탭 확인
- **[BalanceChejanFlow] 조사 완료**: 09:56~10:09 구간에 gubun='1' 잔고 Chejan 이벤트 없음 확인 → 비이슈 종료

---

## 2026-05-07 세션 주요 수정 (B52·B49·B50 — EXIT 루프 근본 원인 수정)

### 오늘 세션 요약

**발생 현상**: ENTRY 주문(09:01, trade_type=1) 접수만 되고 체결 없음 (모의투자 서버 09:00 고변동성 구간).
낙관적 오픈으로 로컬 position=LONG → 60s ENTRY 타임아웃 → pending 해제만 되고 position 유지 →
하드스톱 반복 발동 → EXIT trade_type=4 → Kiwoom 측 포지션 없으므로 Chejan 무응답 → 2분 루프.

| 항목 | 수정 내용 |
|---|---|
| **[B49] EXIT 진단 로그 추가** | `_ts_check_exit_triggers()` — 하드스톱/시간청산 `[ExitAttempt]` + `[ExitSendOrderResult]` |
| **[B50] price_hint float 오차** | `price_hint=round(exit_price, 2)` 적용 |
| **[B52] ENTRY 타임아웃 포지션 복원** | 60s 타임아웃 + `_optimistic==True` → `_reset_position()` + `[FixB]` 경보 |
| **[B53] 타임아웃 후 2분 쿨다운** | `_entry_cooldown_until = now+2min` → STEP 7 진입 차단 |
| **[B54] SendOrderFO 파라미터 통일** | `lOrdKind=1(신규매매) + sSlbyTp` 방향 명시. trade_type=2(SHORT)가 new convention에서 "정정"으로 해석되어 서버 거부되던 문제 수정. 진입/청산/긴급청산 모두 적용 |
| **[B55] accepted vs filled 타임아웃 분리** | `order_no==""` → 60s (미접수), `order_no!=""` → 300s (접수 대기). `pending["accepted_at"]` 타임스탬프 기록 추가 |
| **BrokerSync CRITICAL→WARNING** | position_state.json 잔여 FLAT 처리는 정상 동작이므로 WARNING으로 완화 |
| **[EntrySendResult]** | `log_manager.system()` 추가 → dashboard에서 ret 즉시 확인 가능 |

### 수정 후 ENTRY 타임아웃 흐름

```
낙관적 오픈 → position=LONG, _optimistic=True
ENTRY 60s 타임아웃 체크
→ kind=="ENTRY" AND _optimistic==True:
    [FixB] ENTRY 타임아웃 → 낙관적 포지션 FLAT 복원 (WARN)
    position._reset_position()  ← position=FLAT, entry_price=0
    _clear_pending_order()
→ 이후 하드스톱 발동 안 됨 (position=FLAT)
```

### 추가 확인 사항 (미해결)

- **[V41] B54 SHORT 진입 + EXIT Chejan 수신 확인**: 재시작 후 SHORT 진입 Chejan 수신 여부, LONG 진입 후 EXIT Chejan 수신 여부 확인
- **ENTRY 미체결 원인**: 모의투자 서버 장 초반(09:00~10:10) 고변동성 구간 + 틱 간헐적 수신 문제. 실서버 전환 시 재확인
- **HTS 미처리 주문**: 30907(LONG, 미체결)는 HTS에서 수동 취소 필요 (재시작 전)

---

## 2026-05-06 세션 주요 수정 (Fix B + OPW20006 enc 분석)

| 항목 | 수정 내용 |
|---|---|
| **[B45] OPW20006 레코드명 오타 수정** | `api_connector.py` `_MULTI_RECORD = "선옵잔고상세현황"` (現況·황). 기존 `현활`(活) 오타로 모든 GetCommData 반환값이 blank였음. enc 파일 직접 분석으로 확정 |
| **OPW20006 필드 목록 수정** | `보유수량` 삭제 (OPW20006에 없음), `잔고수량` 유지 (enc offset 66 확인). CS "잔고수량 없음" 오답으로 제거했던 것을 복원. `조회건수` 교차검증 추가 |
| **Fix B — 낙관적 포지션 오픈** | `position_tracker.py`에 `_optimistic` 플래그 + `apply_entry_fill()` 보정 경로 추가. `main.py` line 2660(production)에 `position.open_position()` + `_optimistic=True` 삽입. 모의투자 이중진입 방지 |
| **TR 조사 절차 수립** | `dev_memory/kiwoom_api_tr_investigation.md` 신설. enc 파일(ZIP+CP949) 읽기 절차, GetRepeatCnt/GetCommData 패턴, OPW20006 함정 표 포함 |

### [B46] SendOrderFO 전환 (추가 수정)

| 항목 | 내용 |
|---|---|
| **증상** | `[RC4109] 모의투자 종목코드가 존재하지 않습니다` — `KOA_NORMAL_SELL_KP_ORD` 발생 |
| **원인** | `SendOrder`는 주식 전용. 선물은 `SendOrderFO` 사용 필수 |
| **Fix** | `api_connector.py` `send_order_fo()` 신설. main.py 진입/청산/긴급청산 헬퍼 전환 |
| **`send_order_fo` 파라미터** | `hoga_gb="3"` (선물시장가) / `trade_type` 1=매수, 2=매도 |

**Fix B 진단 로그**: `[FixB] 낙관적 오픈 완료 direction=LONG status=LONG qty=1 optimistic=True` — 2026-05-06 WARN.log에서 정상 확인됨.

### [B47] SendOrderFO trade_type 청산 오류 수정 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 14:28 LONG 진입 후 TP1/하드스톱/15:10 강제청산 주문이 60분간 체결 안 됨. EXIT pending 60초마다 set/clear 반복 |
| **원인** | `_send_kiwoom_exit_order`에서 `trade_type=2`(매도 개시=신규 SHORT) 사용. 선물 LONG 청산은 `trade_type=4`(매도 청산) 필수. 모의투자 서버에서 신규매도로 해석 → 체결 처리 안 됨 |
| **Fix** | `trade_type = 4 if LONG else 3` (매도청산/매수청산). `_KiwoomOrderAdapter.send_market_order()`도 동일하게 수정 |

### [B48] gubun='4' 노이즈 이벤트 차단 (2026-05-06 추가)

| 항목 | 내용 |
|---|---|
| **증상** | 매 주문마다 `gubun='4'`, `order_no=''`, `fill_qty=0`, `status=''` 이벤트 추가 도착. ChejanFlow/ChejanMatch 로그 오염 |
| **Fix** | `_ts_on_chejan_event` 진입부에 `if _gubun not in ("0", "1"): return` 추가 |

### 현재 주문 흐름 (B46·B47·Fix B 모두 적용 후)

```
_execute_entry()
→ SendOrderFO COM API, trade_type=1(LONG)/2(SHORT)   ← [B46] 선물 주문 함수
→ _set_pending_order(ENTRY)
→ position.open_position(direction, price, qty)        ← 낙관적 오픈 (Fix B)
→ position._optimistic = True

_send_kiwoom_exit_order()
→ SendOrderFO COM API, trade_type=4(LONG청산)/3(SHORT청산)   ← [B47] 청산 타입 수정

OnReceiveChejanData 콜백
→ gubun='4' → early return (노이즈 차단) [B48]
→ gubun='0' fill_qty=0 → 접수 이벤트 (pending 유지)
→ gubun='0' fill_qty>0 → 체결 이벤트 → apply_entry_fill()/apply_exit_fill()

[Chejan 진입 체결 시]
→ apply_entry_fill() → _optimistic=True + 방향 일치 → 가격 보정만 (수량 불변)

[Chejan 미수신(모의투자 일부)]
→ 낙관적 포지션 그대로 유지 → 이중진입 없음
```

### OPW20006 교훈

```
enc 파일: C:\OpenAPI\data\opw20006.enc (ZIP → OPW20006.dat CP949)
올바른 레코드명: 선옵잔고상세현황 / 선옵잔고상세현황합계
확인된 필드: 종목코드, 종목명, 매매일자, 매매구분("매수"=LONG/"매도"=SHORT),
             잔고수량(offset 66), 매입단가, 매매금액, 현재가, 평가손익, 손익율, 평가금액
키움 CS 오답: "잔고수량 없음" → enc 파일로 반증. CS 답변 맹신 금지.
```

---

## 2026-05-04 세션 주요 수정 (야간 2세션 — Kiwoom API 주문 연결 + 부분 청산 완성)

| 항목 | 수정 내용 |
|---|---|
| **[B42] Kiwoom 주문 전달 누락 수정** | `api_connector.py` `send_order()` 신설. `entry_manager.py`/`exit_manager.py` `acc_no=""` → `_secrets.ACCOUNT_NO`. main.py에 `_send_kiwoom_entry_order()` / `_send_kiwoom_exit_order()` 헬퍼 추가 → 진입/청산 모든 경로에서 실 API 호출 |
| **부분 청산 완성 (TP1/TP2)** | `PositionTracker.partial_close(exit_price, qty, reason)` 신설. `_execute_partial_exit(price, stage)` + `_post_partial_exit(result, stage)` — PARTIAL_EXIT_RATIOS 기반 API→DB→대시보드 전체 연결 |
| **`_KiwoomOrderAdapter` 신설** | main.py 모듈레벨 어댑터 클래스. `EmergencyExit.set_order_manager()` 에 주입 — CB/KillSwitch 긴급청산도 실 API로 연결 |
| **주문/체결 탭 실데이터 메트릭** | LatencySync.summary() → `update_order_metrics(trades, avg_lat_ms, peak_lat_ms, samples)` 매분 갱신. 하드코딩 더미값 제거 |
| **로그 좌측 정렬** | `QTextCursor` + `QTextBlockFormat.setAlignment(Qt.AlignLeft)` 기반 `_insert_html_left()` / `_insert_html_center()` static 메서드. append()/append_restore()/append_separator() 전부 교체 |

### 수정 후 주문 흐름

```
run_minute_pipeline()
→ STEP 7 진입: _send_kiwoom_entry_order(direction, qty) → SendOrder COM API
→                position.open_position(...)
→ STEP 8 청산:
    손절/15:10/트레일: _send_kiwoom_exit_order(qty) → SendOrder COM API
                       position.close_position(...)
    TP1/TP2:           _execute_partial_exit(price, stage)
                       → _send_kiwoom_exit_order(partial_qty) → SendOrder COM API
                       → position.partial_close(...)
                       → _post_partial_exit(result, stage)
CB/KillSwitch:     _KiwoomOrderAdapter.send_market_order() → SendOrder COM API
```

### OnReceiveChejanData 콜백 현황

- ✅ **구현 완료**: `_ts_on_chejan_event()` — gubun='0'(주문/체결) 처리. fill_qty>0 체결 이벤트로 포지션 보정
- ✅ **B47 수정**: trade_type 청산 타입 오류 수정 → EXIT 체결 정상화 (다음 장중 [V35] 확인 필요)
- ✅ **B48 수정**: gubun='4' 노이즈 이벤트 early return 차단
- ⏳ **미확인**: trade_type=4 수정 후 EXIT 체결 Chejan 즉시 수신 → [V35] 다음 장중 확인

---

## 2026-05-04 세션 주요 수정 (야간 — FID 탐색·PROBE 진단·수급 TR 수정)

| 항목 | 수정 내용 |
|---|---|
| **[B40] FID_OI = 291 → 195 수정** | `config/constants.py` + `option_data.py` 하드코딩 2곳. FID 291 = 예상체결가(선물호가잔량), FID 195 = 미결제약정(선물시세). PROBE 스캔으로 확정 |
| **신규 FID 상수 5개 추가** | `FID_EXPECTED_PRICE=291`, `FID_KOSPI200_IDX=197`, `FID_BASIS=183`, `FID_UPPER_LIMIT=305`, `FID_LOWER_LIMIT=306` |
| **TR_INVESTOR_OPTIONS 수정** | opt50014(선물가격대별비중차트요청·잘못 사용) → opt50008(투자자별매도수금액요청) |
| **PROBE 진단 인프라** | LAYER_PROBE 추가, PROBE-ALLRT 전수 FID 스캔, probe_investor_ticker(). 스캔 범위 1~99로 확장 |
| **투자자ticker 모의투자 미지원 확인** | 8가지 코드/타입 조합 전부 ret=0이나 데이터 수신 없음 → 실서버 전환 시 재테스트 필요 |

### 확정된 FID 매핑 (선물시세 기준)

| FID | 값 | 의미 |
|---|---|---|
| 10 | +1049.65 | 현재가 |
| 15 | 거래량 | 거래량 |
| 41 | 매도1호가 | (선물호가잔량에서 수신) |
| 51 | 매수1호가 | (선물호가잔량에서 수신) |
| 195 | 207357 | **미결제약정** (진짜 OI) |
| 197 | +1049.66 | KOSPI200 지수 현재가 |
| 183 | +1.04 | 시장베이시스 |
| 291 | +1020.60 | 예상체결가 (OI 아님! — 선물호가잔량 기준) |
| 305 | +1078.35 | 선물 당일 상한가 |
| 306 | -918.65 | 선물 당일 하한가 |

---

## 2026-05-04 세션 주요 수정 (저녁 — 다이버전스 패널 수급 데이터 흐름)

| 항목 | 수정 내용 |
|---|---|
| **수급 TR 수집 구조 전환** | `investor_data.fetch_all()` → COM 콜백 체인(run_minute_pipeline) 외부로 이동. `_investor_timer` QTimer 60s 신설. STEP4에서 직접 호출 시 0xC0000409 스택 오버런 위험 해소 |
| **investor_data.fetch_*() 수정** | `self._api.set_input_value()`+`comm_rq_data()` (존재하지 않는 메서드) → `self._api.request_tr()` 전환. TR 응답 rows를 인라인으로 직접 파싱 |
| **api_connector._parse_tr_row 확장** | OPT50029만 지원 → opt10059(`순매수`), opt50014(`콜순매수`/`풋순매수`), opt10060(`차익순매수`/`비차익순매수`) 필드 추가 |
| **logger.py DATA 레이어 추가** | `LAYER_DATA="DATA"` 신설. investor_data 오류가 파일 핸들러 없이 사라지던 문제 해결 |
| **투자자 포지션 매트릭스 개선** | `rt_strd`/`fi_strangle` 하드코딩 0 → 실제 `abs(콜)+abs(풋)` 총합 표시 |
| **옵션 구간별 거래량 UI 연결** | `DivergencePanel.update_data()` oz_* 위젯 갱신 구현. `get_zone_data()` 신설 — ATM=현재 전체 수집 데이터 기반 투자자별 %, ITM/OTM=0 (추후 개선) |
| **_fill_dummy_options 기관 추가** | `institution` 더미 추가 → zone % 합계 정상화 |

### 수정 후 수급 데이터 흐름

```
[QTimer 60s]
→ _fetch_investor_data()
→ investor_data.fetch_all()
→   fetch_futures(): request_tr(opt10059) → rows 파싱 → _futures 캐시 갱신
→   fetch_options(): request_tr(opt50014) → rows 파싱 → _call/_put 캐시 갱신
→   fetch_program(): request_tr(opt10060) → rows 파싱 → _program_* 캐시 갱신
→ DATA.log 기록

[run_minute_pipeline - COM 콜백 체인 내]
STEP4: get_features() → 캐시 읽기만 (TR 호출 없음)
       get_zone_data() → 캐시 기반 zone % 계산
→ update_divergence({..., "zones": {...}})
→ DivergencePanel.update_data() → 바이어스 바 + 포지션 카드 + oz_* zone 바 갱신
```

### 남은 한계
- ITM/OTM 구간: opt50014는 전체 합산만 제공 → ATM에 전체 표시, ITM/OTM=0
  - 정확한 구분은 행사가별 개별 TR 조회(여러 번) 필요 (추후 구현)

---

## 2026-05-04 세션 주요 수정 (오후 — 부트스트랩·SGD·UI)

| 항목 | 수정 내용 |
|---|---|
| **[B37] SGD log_loss → log** | `online_learner.py` `loss="log_loss"` → `"log"`. sklearn 1.0.2 호환. 매분 ValueError 크래시 해결 |
| **부트스트랩 치킨에그 해결** | STEP 5 early return 제거 → 미학습 시 1/3 균등 예측 → STEP 9 DB 저장 → SGD 학습 활성화 |
| **watchdog 임계값** | 60/120/180s → 90/150/240s (1분봉 30s 버퍼) |
| **`_last_recovery_ts` 중복 복구 방지** | 동일 ts 반복 복구 스킵 + `run_minute_pipeline` 진입 시 초기화 |
| **Guard-C1/C2 `notify_pipeline_ran()`** | 비정상 분봉 차단 return 경로에 watchdog 카운터 리셋 추가 |
| **`_dir_ko` NameError 수정** | STEP 7 진입 시 변수 정의 추가 |
| **파라미터 중요도·상관계수 툴팁** | SHAP 개념·업데이트 조건 툴팁 추가 |
| **대시보드 섹션 간격** | 섹션 구분선 앞 16px·뒤 12px로 시인성 향상 |

### SGD 학습 파이프라인 현황 (2026-05-04 13:44 확인)

```
[OnlineLearner] 1m/3m/5m/15m 초기 학습 완료 ← log_loss 수정 + 부트스트랩 정상화
10m·30m: 이전 세션 미실행 구간 ts 없음 → 장 진행 중 자동 채워짐
```

---

## 2026-05-04 세션 주요 수정 (B14 OFI 수정 — 선물호가잔량 콜백)

| 항목 | 수정 내용 |
|---|---|
| **B14 OFI 영구 0 수정** | `선물호가잔량` 콜백 `_on_hoga_data()` 신설. bid/ask를 `_last_bid1/ask1`에 저장, `_current_bar` 동기화, `on_hoga` 콜백으로 OFI 누적 |
| **`sopt_type` 파라미터 추가** | `api_connector.register_realtime()` — `"1"` 전달 시 기존 등록 유지하고 추가 등록 (선물호가잔량 등록에 사용) |
| **OFI 경로 분리** | `_on_tick_price_update`에서 OFI 제거 → `_on_hoga_update()` 전담. 선물시세 틱이 아닌 실제 호가 이벤트마다 OFI 누적 |

### 수정 후 데이터 흐름

```
선물시세    → _on_real_data()  → price/vol 조립 → bar 업데이트
선물호가잔량 → _on_hoga_data() → bid/ask 읽기  → _last_bid1/ask1 저장
                                              → _current_bar bid/ask 동기화
                                              → _on_hoga_update() → ofi.update_hoga()
```

---

## 2026-05-04 세션 주요 수정 (모의투자 SetRealReg + WARN 로그 분리 + 파이프라인 watchdog 수정)

| 항목 | 수정 내용 |
|---|---|
| **WARN 로그 분리** | `utils/logger.py` — `_MaxLevelFilter(WARNING)` 추가. SYSTEM 파일핸들러는 INFO만 기록. `YYYYMMDD_WARN.log` 별도 핸들러 추가. 대시보드 경보탭만 WARN+ 표시 |
| **OPT50029 → SetRealReg 전환** | 모의투자 서버에서 OPT50029 rows=0 — 실시간 데이터 미제공. `is_mock_server=False` + `realtime_code=A0166000`으로 SetRealReg 활성화 |
| **SetRealReg 코드 수정 (B33)** | 기존 `rt_code=101W06` → `realtime_code=A0166000`. 콜백 필터 code 불일치 해결 |
| **파이프라인 watchdog 수정 (B35)** | `run_minute_pipeline()` 모델 미학습 early return 전에 `notify_pipeline_ran()` 추가. 기존: line 426 return → line 667 미도달 → watchdog 영구 발동 |
| **진단 로깅 추가** | `[RT-CB]` `[RT-DATA]` `[RT-RAW]` `[RT-BAR]` `[BAR-CLOSE]` SYSTEM.log 기록. 실시간 분봉 수신 경로 end-to-end 확인 가능 |

### 모의투자 실시간 분봉 수신 확인 결과 (2026-05-04 로그)

```
[RT-CB] code='A0166000' type='선물시세' 등록키=[('A0166000', '선물시세')]
[RT-RAW] raw_price='+1038.55' raw_vol='+1'
[BAR-CLOSE] ts=11:22 O=1038.55 H=1038.80 L=1038.45 C=1038.80 V=25  ✅ 매 분 정상
```

---

## 2026-04-30 세션 주요 수정 (SIMULATION 제거 + 자동 종료 + 성장 추이 대시보드)

| 항목 | 수정 내용 |
|---|---|
| **SIMULATION 코드 전면 제거** | `--mode` argparse / `self.mode` / 더미 모델 주입 / `_sim_timer` / `force_ready_for_test()` / `TRADE_MODE` 상수 제거. 단일 실전 경로만 유지 |
| **일일 마감 자동 종료** | `daily_close()` 완료 → 슬랙 종료 알림(거래수·승률·PnL·재학습·다음시작) → 15초 후 `_qt_app.quit()`. `_auto_shutdown()` 신설 |
| **패널 이전 데이터 지속** | `_restore_panels_from_history()` — 시작 500ms 후 DB 이력으로 자가학습·효과검증·추이 패널 선조회. 파이프라인 첫 실행 전 빈값 방지 |
| **daily_stats 스냅샷 저장** | `daily_close()` 내 `save_daily_stats()` — SGD정확도·검증건수·PnL을 `daily_stats` 테이블에 영속 |
| **📈 성장 추이 탭 신설** | `TrendPanel` — 일별(30일)/주별(12주)/월별(12개월)/연간 4탭. 스파크라인(PnL·승률·SGD정확도) + 스크롤 테이블. 탭 순서: …자가학습/효과검증/**성장추이**/알파봇 |
| **DB 집계 쿼리 4종** | `fetch_trend_daily/weekly/monthly/yearly()` + `daily_stats` 테이블 + `save_daily_stats()` |

---

## 현재 대시보드 탭 구조

### 중앙 탭 (mid_tabs) — 8개
| 번호 | 탭 이름 | 클래스 |
|---|---|---|
| 1 | 다이버전스 + 포지션 | `DivergencePanel` |
| 2 | 동적 피처 (SHAP) | `FeaturePanel` |
| 3 | 청산 관리 | `ExitPanel` |
| 4 | 진입 관리 | `EntryPanel` |
| 5 | 🧠 자가학습 | `LearningPanel` |
| 6 | 🎯 효과 검증 | `EfficacyPanel` |
| **7** | **📈 성장 추이** | **`TrendPanel`** (신규) |
| 8 | 알파 리서치 봇 | `AlphaPanel` |

### 우측 5층 로그 탭 — 6개
| 탭 | 내용 |
|---|---|
| 1 시스템/경보 | SYSTEM/WARNING 레벨 통합 (2 경보탭 공유) |
| 2 경보 | WARN/ERROR/CRITICAL 전용 |
| 3 주문/체결 | TRADE 레이어 + FILL/PENDING 태그 |
| 4 손익 | PnL 로그 + 미실현·일일·VaR 수치 |
| 5 모델 AI | LEARNING/MODEL 레이어 |
| 6 📊 손익 추이 | 일별·주별·월별 누적 P&L 테이블 (기존 PnlHistoryPanel) |

---

## 2026-04-30 세션 주요 수정 (파이프라인 감시 경보 버그 2종 수정 + 분봉 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **경보 누락 버그 1** | `_tick_header()` — `_watchdog_alerted.add(threshold)` 가 콜백 체크 **이전**에 실행되어, 콜백 미등록 시 임계값을 소비하고 나중에 콜백 등록 후에도 영구 누락. **수정**: 콜백 실행 후에만 소비(`add` 위치 교체) |
| **경보 누락 버그 2** | `append_sys_log_tagged()` — `level="WARNING"` 체크 조건이 `("WARN", "ERROR", "CRITICAL")` 이라 `"WARNING"` 이 불일치 → SYSTEM 태그로 처리되어 경보 탭 미표시. **수정**: `{"WARNING": "WARN"}.get(level, level)` 정규화 추가 |
| **분봉 라벨 툴팁** | `_PIPE_HEALTH_TIP` 상수 추가 — 파이프라인 심박 막대 기능 + 3단계 자동 조치(60/120/180초) + 긴급복구 루틴 + 원인 목록. 분봉 라벨·진행 바·경과 라벨 3개 위젯 연결 |

### 버그 발생 경위 (실제 시퀀스)

```
1. __init__: _header_timer 시작 → _pipe_elapsed_s 증가 시작
2. connect_kiwoom() 진행 중 (수십 초 소요)
   → 60/120초 도달 시 threshold 소비되나 callback=None → 알림 없음
3. set_pipeline_watchdog_cb() 호출 → callback 등록
4. pipeline 정상 실행 → notify_pipeline_ran() → _watchdog_alerted.clear()
5. pipeline 재정지 → 60초 후 threshold 60 재진입
   → 이때 callback 존재해야 발동되는데...
   → _pipe_elapsed_s += 1 로직에서 threshold 60을 콜백 없이 소비했다면 영구 누락!
```

---

## 2026-04-30 세션 주요 수정 (비정상 분봉 가드 + 진입 신뢰성 강화)

| 항목 | 수정 내용 |
|---|---|
| **Guard-C1 가격 0 차단** | `run_minute_pipeline()` 앞단 — close/high/low ≤ 0 이면 경보 로그 후 즉시 return. ATR 음수·손절가 오작동 원천 차단 |
| **Guard-C2 고가<저가 차단** | high < low 역전 분봉 경보 후 즉시 return. 음의 TR → ATR 오염 방지 |
| **Guard-C3 volume=0 진입 차단** | volume=0 경보 로그 + `_bar_volume_zero` 플래그 설정. STEP 7 진입 조건에 `and not _bar_volume_zero` 추가. 청산은 차단 안 함(가격 기반) |
| **Guard-F1 CORE 피처 NaN/Inf 교정** | STEP 4 후 vwap_position / cvd_direction / ofi_pressure 에 NaN·Inf 검출 시 0으로 교정 + 경보 로그 |
| **daily_loss_pct 계산 수정** | 기존: `abs(pnl_pts) / 1_000` (실질적으로 항상 통과) → 수정: `max(-pnl_krw, 0) / 50_000_000` (5천만원 기준 실손실률). 체크리스트 9번 리스크 한도 실질화 |
| **`import math` 추가** | main.py 최상단 — Guard-F1 NaN/Inf 검사용 |

### 가드 점검 결과 요약 (조사 기반)

| 구간 | 수정 전 | 수정 후 |
|---|---|---|
| 분봉 수신 (realtime_data) | abs() 변환만 | 변경 없음 (수신 레이어는 OK) |
| 파이프라인 앞단 (main.py) | **없음** | **C1/C2/C3 가드 추가** |
| CORE 피처 (STEP 4 후) | **없음** | **F1 NaN/Inf 교정** |
| 진입 조건 (STEP 7) | CB+시간+등급+수량 | **volume=0 차단 추가** |
| 청산 조건 (STEP 8) | 완전 (변경 없음) | 변경 없음 |
| 리스크 한도 (체크리스트 9) | **pts/1000 — 항상 통과** | **KRW/5천만 — 실질 2% 한도** |
| Circuit Breaker | 완전 (변경 없음) | 변경 없음 |

### 남은 한계 (개선 불가·저우선)

- OFI/CVD 극단값 제한 없음 — signal_strength 과대 가능 (CB④ ATR 3배 트리거로 간접 방어)
- account_balance 하드코딩(5천만) — 실제 잔고 연동 시 개선 필요
- ATR floor(0.5pt)로 비정상 소ATR 방어는 유지

---

## 2026-04-30 세션 주요 수정 (파이프라인 생존 감시 + 자동 복구)

| 항목 | 수정 내용 |
|---|---|
| **파이프라인 감시 콜백** | `main_dashboard.py` — `MireukDashboard._watchdog_alerted` (set) + `_pipeline_recovery_cb` 추가. `_tick_header()`에서 60/120/180초 임계값 초과 시 1회만 콜백 발동. `notify_pipeline_ran()` 시 플래그 초기화 |
| **`set_pipeline_watchdog_cb()`** | `DashboardAdapter`에 추가 — main.py → dashboard 역방향 콜백 등록 인터페이스 |
| **`_on_pipeline_watchdog()`** | `main.py` — 60s: 경보 로그(WARNING), 120s: 경보 + 슬랙, 180s: 경보 + 슬랙 + 강제 복구 |
| **`_try_pipeline_recovery()`** | `main.py` — `raw_candles` DB 최신 분봉(10분 이내) 읽어 `run_minute_pipeline()` 강제 재실행. 포지션 보유 중 장기 정지 시 추가 경보 |
| **`log_manager.warn` 오류 수정** | `warn()` 메서드 없음 → 전체 `log_manager.system(msg, "WARNING")` 으로 교체. SYSTEM layer + WARNING level → `append_sys_log_tagged` → 1 시스템·2 경보 탭 동시 기록 |

### 파이프라인 감시 3단계 동작

| 경과 | 동작 |
|---|---|
| **60초** | 경보 탭 경고 — 분봉 수신 지연, 장 시간 확인 안내 |
| **120초** | 경보 탭 경고 + 슬랙 알림 — 60초 내 미복구 시 자동 조치 예고 |
| **180초** | 경보 탭 + 슬랙 + `_try_pipeline_recovery()` 자동 실행 |

### 복구 루틴 조건 분기

- `raw_candles` 없음 → 경보 로그 후 종료 (포지션 있으면 추가 경보)
- 최신 분봉 > 10분 전 → 복구 포기 (장외 시간 판단)
- 최신 분봉 ≤ 10분 → `run_minute_pipeline(bar)` 강제 실행 → `notify_pipeline_ran()` 자동 호출 → 감시 플래그 리셋

---

## 2026-04-30 세션 주요 수정 (PnL 재시작 복원 수정 + 분봉 모니터 툴팁)

| 항목 | 수정 내용 |
|---|---|
| **PnL 재시작 복원 [B30]** | `main.py` `_restore_daily_state()` — `restore_daily_stats()` 호출 후 `dashboard.update_pnl_metrics(0.0, daily_pnl_krw, 0.0)` 추가. 재시작 후 미실현손익·일일누적·VaR 패널이 "——원" 로 리셋되던 버그 수정 |
| **분봉 모니터 툴팁** | `dashboard/main_dashboard.py` — `_CANDLE_MONITOR_TIP` 상수 추가. "다음 분봉 ▷" 라벨·진행 바·초 라벨, "↑ 마지막 갱신" 라벨·경과 라벨 5개 위젯에 동일 툴팁 연결. 라벨에 점선 밑줄(cursor:help) 표시 |

### PnL 복원 버그 근본 원인 (B30)
- `_restore_daily_state()`에서 `position.restore_daily_stats(rows)` 로 내부 통계(`_daily_pnl_pts` 등)는 정상 복원
- 그러나 UI 패널에 `dashboard.update_pnl_metrics()` 호출이 없어 화면은 초기값 "——원" 유지
- 수정: `daily_stats()` 로 복원된 값을 읽어 즉시 패널 반영. 미실현/VaR는 0 (첫 분봉 수신 후 갱신됨)

---

## 2026-04-30 세션 주요 수정 (CB 중복발동 수정 + 슬랙 타임스탬프)

| 항목 | 수정 내용 |
|---|---|
| **CB 중복 슬랙 발동 수정** | `_trigger_halt()` — HALTED 상태 조기 반환 체크 추가 (기존: 체크 없음 → 정확도 35% 미만 지속 시 매분 슬랙 재전송) |
| **CB `_trigger_pause()` 방어** | PAUSED 상태에서도 재발동 방지. 기존엔 `HALTED`만 막음 → `PAUSED·HALTED` 모두 차단 |
| **CB 트리거⑤ API지연 방어** | `record_api_latency()` — PAUSED·HALTED 상태에서 슬랙·청산 콜백 중복 호출 방지 조건 추가 |
| **CB → UI 로그 연결** | `circuit_breaker.py`가 `logger.getLogger("SYSTEM")`만 사용해 UI 미출력. `log_manager` import 추가 + `_trigger_pause/halt`, `_check_pause_expiry`, `reset_daily` 전부 `log_manager.system()` 호출 추가 → 대시보드 SYSTEM/경보 탭 표시 |
| **슬랙 타임스탬프** | `utils/notify.py` — `notify()` 내 `[HH:MM:SS]` 자동 첨부. 모든 알림에 전송 시각 표시 |
| **슬랙 주문·체결 함수 추가** | `notify_order()`, `notify_execution()` 함수 신설 (방향·수량·가격·손익 포함) |

### CB 중복 발동 원인 (근본 원인 분석)
- **트리거③ 정확도**: 30분 정확도 < 35% 동안 매분 `record_accuracy()` → `_trigger_halt()` 호출. 기존엔 HALTED 체크 없어 매분 슬랙 재전송
- **트리거④ ATR**: ATR 3배 초과 지속 시 매분 `_trigger_pause()` 호출. 기존엔 PAUSED 상태에서도 재발동 + `_pause_until` 갱신 + 슬랙 재전송
- **UI 미출력**: `circuit_breaker.py`의 `logger`는 파일/콘솔 전용 (`logging.getLogger`). 대시보드 `log_manager`와 별개 시스템이라 UI에 아무것도 안 보임

---

## 2026-04-30 세션 주요 수정 (자가학습 연결)

| 항목 | 수정 내용 |
|---|---|
| **STEP 2 SGD 연결** | `main.py` STEP 2 — STEP 1 검증 결과(verified)의 피처 dict로 `OnlineLearner.learn()` 호출. 매 검증건마다 즉시 `partial_fit` |
| **STEP 3 GBM 연결** | `main.py` STEP 3 — `should_retrain_weekly()` / `should_retrain_monthly()` 조건 충족 시 `batch_retrainer.retrain_now()` 호출 후 `model._load_all()`로 즉시 반영 |
| **SGD 블렌딩 적용** | `main.py` STEP 5 — GBM `predict_proba()` 직후 호라이즌별 `online_learner.blend_with_gbm()` 적용. SGD 미학습(fitted=False) 시엔 GBM 단독 사용 |
| **features 전체 저장** | `main.py` STEP 9 — `list(features.items())[:20]` → 전체 피처 저장 (SGD 학습 입력 완전성 확보) |
| **daily_close 재학습** | `main.py` 15:40 마감 시 `batch_retrainer.retrain_now(weeks_back=8)` 호출 후 모델 reload |
| **BatchRetrainer 초기화** | `main.py __init__` — `self.batch_retrainer = BatchRetrainer()` 추가 |
| **_load_from_db 재작성** | `batch_retrainer.py` — pandas 의존 제거, `raw_features`/`raw_candles` 테이블 직접 읽기. numpy 기반 X 행렬 + `build_single_target()` 라벨 생성 |
| **prediction_buffer features** | `prediction_buffer.py` `verify_and_update()` — SELECT에 `features` 컬럼 추가, 반환 dict에 JSON 파싱된 `features` 포함 |

---

## 🎯 학습 효과 검증기 패널 (신규 — 2026-04-30)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 6번째 "🎯 효과 검증" (🧠자가학습 탭 오른쪽) |
| **EfficacyPanel** | `dashboard/main_dashboard.py` `class EfficacyPanel` |
| **update_efficacy()** | `DashboardAdapter.update_efficacy(data)` → `efficacy_panel.update_data(data)` |
| **_gather_efficacy_stats()** | `main.py` — DB 쿼리 후 5분마다 호출 (`_efficacy_tick % 5 == 1`) |
| **DB 쿼리 4종** | `utils/db_utils.py` — `fetch_calibration_bins` / `fetch_grade_stats` / `fetch_regime_stats` / `fetch_accuracy_history` |

### 패널 4-Section 구성
1. **신뢰도 캘리브레이션** — confidence 구간별 실제 적중률 테이블 (✓ 우수 / ▲ 과소신뢰 / ▼ 과신)
2. **등급별 매매 성과** — A/B/C/X/? 등급별 건수·승률·평균pts·합계pts
3. **학습 성장 곡선** — `▁▂▃▄▅▆▇█` 스파크라인 + 초기 50회 vs 최근 50회 Δ
4. **레짐별 성과** — RISK_ON/NEUTRAL/RISK_OFF 승률 게이지 바 + 평균pts

### KPI 상단 배지 4개
- 전체 승률 / A등급 승률 / 캘리브레이션 점수 / 학습 효과 Δ

### 종합 평가 배너 기준
- A등급 승률 ≥60% + 전체 ≥53% → ✅ 학습 효과 확인
- 전체 ≥50% → ⚡ 개선 중
- 전체 <50% → ⚠️ 모델 재점검 권장

---

## 🧠 자가학습 모니터 패널 (신규)

| 항목 | 내용 |
|---|---|
| **위치** | 중앙 탭 5번째 "🧠 자가학습" |
| **LearningPanel** | `dashboard/main_dashboard.py` `class LearningPanel` |
| **update_learning()** | `DashboardAdapter.update_learning(data)` → `learn_panel.update_data(data)` |
| **_gather_learning_stats()** | `main.py` — SGD/GBM/버퍼 통계 수집 후 매분 호출 |
| **_verified_today** | 당일 검증 건수 누적 카운터 (15:40 리셋) |
| **_horizon_counts** | `OnlineLearner._horizon_counts` — 호라이즌별 학습 건수 |

### 패널 구성
1. **요약 카드 4개** — 오늘 검증 건수 / SGD 50분 정확도(색상) / GBM 마지막 재학습 / 데이터 축적%
2. **SGD 섹션** — GBM↔SGD 블렌딩 그라데이션 바 + 6개 호라이즌 카드(정확도/학습건수/배지)
3. **GBM 섹션** — 마지막 재학습 / 재학습 횟수 / 다음 스케줄 + 5000행 축적 진행 바
4. **예측 버퍼 테이블** — 6 호라이즌 × (정확도 / 게이지 / 추세▲▼━)

### 정확도 색상 기준
- ≥62%: 초록 (SGD 비중 증가 중)
- 55~62%: 청록
- 48~55%: 주황
- <48%: 빨강 (SGD 비중 감소 중)

---

## 자가학습 파이프라인 현재 상태

| 항목 | 상태 |
|---|---|
| SGD 온라인 학습 (STEP 2) | ✅ **연결 완료** |
| GBM 배치 재학습 (STEP 3) | ✅ **연결 완료** (주간/월간 + 일일 마감) |
| SGD 블렌딩 (STEP 5) | ✅ **연결 완료** |
| features 전체 저장 (STEP 9) | ✅ **수정 완료** |
| BatchRetrainer DB 로드 | ✅ **raw_features 연동 완료** |
| 실제 학습 가동 조건 | ⏳ raw_candles 5000행 축적 필요 (2026-04-28 시작, 약 2.5주) |

---

## 2026-04-28 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| PredictionPanel dict reset 재발 수정 | `__init__` 277~279 줄의 reset이 `_build()` 호출 후에 위치해 항상 빈 dict → 선언을 `_build()` 앞으로 이동, `_build()` 내 중복 초기화 제거 |
| 시뮬레이션 타이머 조건부 시작 | `kiwoom=None`일 때만 `_start_sim_timer()` 호출. `update_price()` 첫 수신 시 `_stop_sim_timer()` 자동 호출 |
| sim timer 참조 저장 | `self._sim_timer`로 저장 (`stop()` 호출 가능하도록) |
| force_ready_for_test() 추가 | SIMULATION 모드 파이프라인 통과 검증용 더미 GBM 모델 주입 (`.pkl` 저장 없음) |
| 파이프라인 전체 검증 완료 [V3] | tick→분봉→pipeline→LONG 1계약 @ 1008.2 / 12:29 확인 |
| predictions.db 저장 확인 [V5] | 12:29·12:30 각 6 호라이즌 = 30행 확인 |
| trades.db 저장 누락 수정 | `_post_exit()`에 trades.db INSERT 추가. `position_tracker.close_position()` result에 `entry_ts`·`grade` 추가 |
| 대시보드 가격 동기화 | `run_minute_pipeline()` 진입 시 `dashboard.update_price(bar['close'])` 호출 추가 (기존엔 시뮬 타이머 ~388만 표시됨) |

## 2026-04-30 세션 주요 수정 (저녁)

| 항목 | 수정 내용 |
|---|---|
| 손익 추이 패널 신설 | 5층 로그 6번째 탭 "📊 손익 추이". 일별(60일)·주별(13주)·월별 `QTableWidget` 누적 P&L 테이블 + 요약 카드 6개 |
| 수익/손실 행 배경 | 수익일 연한 초록 / 손실일 연한 빨강 / 당일 황색 볼드 강조 |
| 월별 샤프 지수 | 월 내 일별 PnL 기반 연율화 샤프(√252), 색상 조건부(초록/노랑/빨강) |
| 주별 MDD | 주간 내 순차 누적 기준 최대 낙폭(원) 표시 |
| `fetch_pnl_history()` | db_utils.py 추가 — 체결 완료 거래 최근 90일 SELECT |
| `_refresh_pnl_history()` | main.py 추가 — _post_exit / daily_close / _restore_daily_state 3곳 자동 갱신 |

## 2026-04-30 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| PnL 탭 즉시 갱신 [B27/B28] | `_post_exit()` / `_execute_entry()` 내 `update_pnl_metrics()` + `append_pnl_log()` 직접 호출 추가 |
| ScreenScale 전면 재작성 | `fit_scale=min(sw/1680,sh/1000)` + `dpi_bonus=(dpr-1)×0.10`. 3840×2160@150%→1.45× 자동 적용 |
| 폰트 시인성 개선 | QTextEdit/배지/버튼 전 하드코딩 px → `S.f()` 교체, 5층 로그 12px 기준 |
| 재시작 연속성 [B29] | `trades.db` 당일 거래 → 주문/체결·손익 탭 `[복원]` 이탤릭 재표시, 세션 카운터(`session_state.json`), `restore_daily_stats()` 통계 재적산 |

## 2026-04-30 세션 주요 수정 (오전)

| 항목 | 수정 내용 |
|---|---|
| FILL 이상가격 이상점 진단 | 대시보드 `_sim_tick()` 시뮬 타이머가 키움 연결 전 창1 주문/체결 탭에 `FILL 매도 5계약 @388.48` 가짜 로그를 출력하는 것으로 확인 — 실제 거래 무관 |
| 시뮬 모드 완전 분리 [B26] | `MireukDashboard.__init__(sim_mode=True)` 파라미터 추가. `live` 모드(`sim_mode=False`)면 시뮬 타이머 자체 미생성. `DashboardAdapter` / `create_dashboard()` 동일하게 `sim_mode` 전파 |
| main.py 모드 연동 | `create_dashboard(sim_mode=(self.mode == "SIMULATION"))` 전달. `stop_sim_timer()` 호출을 `if self.mode == "SIMULATION":` 조건 내부로 이동 (live 모드에서 불필요한 호출 제거) |
| [SIM] 태그 추가 | `_sim_tick()` FILL/PENDING 로그 앞에 `[SIM]` 접두사 추가 — 시뮬 로그와 실거래 로그 육안 구분 가능 |

## 2026-04-29 세션 주요 수정 (오후 추가)

| 항목 | 수정 내용 |
|---|---|
| 멀티 호라이즌 `_preds_ui` 확률 오류 수정 | `main.py` STEP 5→UI 변환 시 `1-confidence` 근사 → `r["up"]`/`r["down"]`/`r["flat"]` 직접 참조로 교체. 3클래스 합≠1 오류 제거 |
| 시뮬레이션 호라이즌 다양성 수정 | `main_dashboard.py` `_sim_tick`: 단일 trend 기반 → 호라이즌별 σ `[0.06~0.20]` 독립 노이즈 적용 (장기일수록 불확실성 증가). `hold` 키 → `flat`으로 실거래 경로와 통일 |

## 2026-04-29 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 주문/체결 탭 툴팁 | `dashboard/main_dashboard.py`: `_ORDER_TAB_TIP` 상수 추가 + `QToolTip` CSS + `setTabToolTip()` — 진입 흐름(①~⑤) + 청산 흐름(P1~P6) HTML 툴팁 |
| 외인 데이터 "-" 수정 [B16] | `InvestorData` 미임포트·미인스턴스화 확인 → `main.py` import 추가, `__init__`에 인스턴스화, STEP 4에 `fetch_all()` + `supply_demand=supply_feats` 전달 |
| 다이버전스 패널 배선 [B17] | `dashboard.update_divergence()` 미호출 → STEP 4 직후 rt_bias/fi_bias/contrarian/div_score 계산 후 매분 호출 |
| 외인 카드 업데이트 누락 [B18] | `DivergencePanel.update_data()`: fi_call/fi_put/fi_strangle 카드 setText 3줄 추가 |
| investor_data api 주입 | `connect_kiwoom()` 내 `self.investor_data._api = self.kiwoom` 추가 (실거래 시 TR 폴링 활성화) |
| investor_data 일일 리셋 | `daily_close()`에 `self.investor_data.reset_daily()` 추가 |
| 체크리스트 전부 X 버그 [B19] | 체크리스트 평가를 CB·시간 조건 블록 밖으로 분리 → FLAT+방향 있으면 항상 평가, 대시보드 항상 갱신 |
| 체크 미평가 시 X 표시 [B20] | `update_data()`: `checks.get(attr, None)` → None이면 회색 "—" 표시 (기존: False → 빨간 X) |
| 산출 수량 —— [B21] | `update_entry(qty=0)` 파라미터 추가 + `e_qty` 라벨 갱신 로직 추가 |
| 당일 진입 통계 고정 [B22] | `EntryPanel.update_stats()` + `DashboardAdapter.update_entry_stats()` 추가, STEP 9 후 매분 `position.daily_stats()` 기반 갱신 |
| 청산 패널 데이터 배선 [B23] | `main.py` STEP 8 직후 `update_position()` 추가 — PositionTracker 실제 값(`stop_price`, `tp1_price`, `tp2_price`, `entry_time`, `partial_1/2_done`) 전달 |
| ExitPanel.update_data() 재작성 [B24] | FLAT 상태 → `_reset_display()` "——" 표시 / LONG·SHORT: 실제 스톱·목표가 사용, 보유 시간 계산, PnL KRW 방향 반영, 부분청산 바 갱신 |
| 시뮬 루프 청산 패널 수정 [B25] | `status='LONG'` + `stop`/`tp1`/`tp2` 구조화, `partial1`/`partial2` 틱 기반 시뮬 |

## 2026-04-28 세션 주요 수정 (오후)

| 항목 | 수정 내용 |
|---|---|
| Path B DB 인프라 구축 | `utils/db_utils.py`에 `raw_candles`/`raw_features` 테이블 + save/get 함수 4개 추가. `config/settings.py`에 `RAW_DATA_DB` 경로 추가. STEP 4에서 매분 분봉·피처 저장 시작 — 13거래일 후 실제 모델 학습 가능 |
| CVD 틱 방향 수정 [B13] | FC0 FID10 부호(전일대비 방향)를 틱 방향으로 오해 → tick test(prev_price 비교, Lee-Ready 근사)로 교체. `realtime_data.py`에 `_prev_tick_price` 추가, bar dict에 `buy_vol`/`sell_vol` 누적 |
| 손절 exit price 보정 [B15] | `_check_exit_triggers(bar=)`에 bar 파라미터 추가. LONG 손절 시 `exit_price = max(stop_price, bar_low)` — close가가 아닌 손절가 기준 |
| 디버그 로그 8포인트 추가 | [DBG-F4] ATR+핵심피처 / [DBG-F6] 호라이즌예측 / [DBG-CB] CB상태 / [DBG-F7] 진입조건 / [DBG-F7a] 체크리스트 / [DBG-F7b] 사이저 / [DBG-F8] 포지션PnL / [DBG-STOP] 하드스톱 |
| DEBUG 레이어 레벨 수정 | `utils/logger.py`: LOG_LEVEL=INFO여서 DEBUG 레이어도 INFO → debug() 차단. `logging.DEBUG` 고정으로 수정 |
| 대시보드 신뢰도 갱신 | `PredictionPanel.update_data(conf=)` 파라미터 추가 → `lbl_conf` "신뢰도 76.8%" 표시 |
| 대시보드 호라이즌/체크리스트 갱신 | `run_minute_pipeline`에서 `update_prediction()` + `update_entry()` 매분 호출 추가 |
| 대시보드 5층 로그 배선 | `main.py __init__`에서 `log_manager.subscribe()` SYSTEM/TRADE/LEARNING 콜백 등록 |
| 대시보드 PnL 실시간 갱신 | `LogPanel.update_pnl_metrics()` 추가 + `_pnl_vals`/`_pnl_bars` dict 저장 (이전엔 로컬 변수 → 업데이트 불가) |
| 실거래 검증 결과 | LONG @1008.40 stop=1007.65, ATR floor stop_dist=0.75pt 확인 [V6 DONE], 체크리스트 8/9 통과 |

## 2026-04-27 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| 근월물 코드 | `GetFutureCodeByIndex(0)` 0순위 추가 → `A0166000` 확정 (구: 날짜계산 fallback `101W06`) |
| 실시간 타입명 | `RT_FUTURES="FC0"` → `"선물시세"`, `RT_FUTURES_HOGA="FH0"` → `"선물호가잔량"` |
| GetRepeatCnt | `or rq_name` fallback 제거 → `""` 빈 문자열 그대로 전달 |
| EmergencyExit | `get_position()` 없음 → 속성 직접 읽기 + `set_futures_code()` 추가 |
| run_minute_pipeline | candle `ts`(datetime) → `strftime` 문자열 변환 |
| 대시보드 | PredictionPanel `_build()` 맨 앞에서 dict 초기화 (IDE 순서 복구 방지) |
| 대시보드 | `mk_val_label` `align` 파라미터 추가 |
| 대시보드 | 헤더 우측 커밋 해시 표시 (해상도 아래) |

## 2026-04-26 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| TR 코드 | OPT10080 → **OPT50029** (`config/constants.py`) |
| COM 콜백 | 메타데이터만 저장 + QEventLoop.quit(), 실제 API 호출은 exec_() 복귀 후 |
| GetRepeatCnt | 2번째 파라미터: rq_name → **record_name** |
| 근월물 조회 | GetFutureList() 우선 → GetMasterCodeList("10") → 날짜 계산 fallback |
| GetCommDataEx | → **GetCommData** (서명 오류 수정) |
| 대시보드 | `create_dashboard()` 시작 시 show(), 5분마다 대기 상태 로그 |

---

## 현재 차단 이슈

| 이슈 | 원인 | 상태 |
|---|---|---|
| OFI 영구 0 (B14) | 선물호가잔량 콜백 신설 + `sopt_type="1"` 추가 등록으로 해결 | ✅ 해결 |
| CVD tick test 효과 | 다음 실행에서 buy_vol/sell_vol이 실제 분리되는지 [V8] 확인 필요 | ⏳ 검증 대기 |
| OPT50029 초기 분봉 rows=0 | 모의투자 서버에서 OPT50029 미지원 확인. SetRealReg(A0166000)으로 전환 완료 | ✅ 해결 |
| [DBG] 출력문 정리 | 디버그 print 잔존 | 🔧 안정화 후 제거 |
| Walk-Forward 26주 | 실거래 데이터 미확보 | ⏳ 장기 과제 |
| Path B 모델 학습 | 13거래일 raw_candles 축적 후 가능 (2026-04-28 축적 시작) | ⏳ 약 2.5주 후 |

---

## 성능 목표

| 버전 | 정확도 | Sharpe | MDD |
|---|---|---|---|
| v6 (기준) | 75~80% | 2.5~3.0 | — |
| v6.5 (현재) | 80~85% | 3.0~3.5 | — |
| v7.0 (목표) | 82~88% | 3.5~4.0 | -30% |

---

## 형제 프로젝트 참조

- 한량이(주식 자동매매): `auto_trader_kiwoom/dev_memory/CURRENT_STATE.md`
## 2026-05-06 최신 반영

| 항목 | 상태 |
|---|---|
| 체결 소스 오브 트루스 | `OnReceiveChejanData` + pending order 매칭 경로를 기준으로 추적하도록 보강됨 |
| startup broker sync | `OPW20006` blank placeholder row-only 응답을 hard mismatch가 아니라 FLAT 후보로 해석하도록 보정됨 |
| futures balance 진단 | `OPW20006-REQ`, `OPW20006-RESP`, `OPW20006-DIAG` 추가 |
| 주문 경로 진단 | `EntryAttempt`, `EntrySendOrderResult`, `PendingOrder`, `EntryPendingCreated`, `OrderMsgDiag` 추가 |
| Chejan/잔고 진단 | `ChejanDiag`, `ChejanFlow`, `ChejanMatch`, `ChejanDedup`, `EntryFillFlow`, `ExitFillFlow`, `BalanceChejanFlow`, `BrokerSyncFlatPlaceholder` 추가 |
| 포지션 복원 메타 | `position_state.json`에 `last_update_reason`, `last_update_ts` 저장 및 `PositionDiag` 복원 로그 추가 |
| 오늘 확인된 유력 원인 | startup sync 차단은 blank placeholder row 오판 가능성이 가장 높음 |
| 잔여 리스크 | `2026-05-06 10:48:19` 불일치의 정확한 과거 원인은 다음 실행 로그로 최종 증명 필요 |
| 운영 리스크 | CB 저정확도 halt 및 strategy gate 정책은 별도 검토 필요 |
# 2026-05-06 추가 업데이트 (실시간 잔고 패널 연결/보정)

| 항목 | 현재 상태 |
|---|---|
| 좌측 상단 UI | `계좌번호` / `전략명` 콤보와 저장 버튼이 헤더 하단에 정렬되어 있음 |
| 좌측 컬럼 구조 | 상단 `실시간 잔고`, 하단 `멀티 호라이즌 예측 + 파라미터 분석` 2단 분할 완료 |
| 실시간 잔고 패널 | 라이브 게이지 + 합계 6개 + 종목별 잔고 테이블 UI 추가 완료 |
| 잔고 데이터 연결 | `OPW20006` 결과가 startup sync 직후와 잔고 Chejan 이후 대시보드로 전파되도록 연결 완료 |
| 공란 응답 보정 | `OPW20006` summary가 전부 blank일 때 잔고행 합산 + `daily_stats()` 기반 fallback 표시 적용 |
| 진단 로그 | `[OPW20006-SUMMARY-BLANK]`, `[BalanceUIFallback]` 추가 |
| 현재 한계 | `OPW20006` 단독으로는 합계 6개가 항상 채워지지 않음. 장후/무포지션에서 `rows=0`, summary blank 케이스 존재 |

### 최신 확인 로그

- `2026-05-06 18:51:29 [BalanceUIFallback] summary blank from OPW20006 ... applied={'총매매': '0', '총평가손익': '0', '실현손익': '0', '총평가': '0', '총평가수익률': '0.00', '추정자산': '0'}`
- 현재 상단 패널은 더 이상 빈 대괄호를 표시하지 않고, 값이 없으면 공란/0 fallback으로 유지됨.
## 2026-05-08 최신 반영 - Ensemble Upgrade / Effect Validation

| 항목 | 현재 상태 |
|---|---|
| Sprint 1 | 완료. baseline 저장, 5레벨 호가 수신 검증, `MLOFI / microprice / queue dynamics` 구현 및 실시간 로그 검증 완료 |
| Sprint 2 | 완료. `FeatureBuilder` 연결, `adaptive gating` 프로토타입 반영, baseline vs enhanced A/B 백테스트 스크립트/리포트 생성 완료 |
| Sprint 3 | 대부분 완료. `meta_labels`, `meta gate`, calibration 리포트 자동 생성, `ensemble_decisions` 저장 강화 완료 |
| Sprint 4 | 부분 완료. `toxicity gate`, rollout readiness 리포트, shadow 운영 기준 추가 완료 |
| 원확률 저장 | `predictions` 테이블에 `up_prob/down_prob/flat_prob` 저장 경로 및 migration 완료. 재시작 이후 신규 예측은 원확률 저장 확인 |
| 효과 검증 UI | 대시보드 중간 패널에 `A/B / Calibration / Meta Gate / Rollout` 탭 추가 완료 |
| 자동 리포트 주기 실행 | `main.py`에서 `Calibration/Meta/Rollout=15분`, `A/B=30분` 주기로 리포트 자동 재생성 및 스냅샷 누적 |
| 이력 저장 | `effect_monitor_history.json` 에 효과 검증 추이 스냅샷 누적 시작 |
| 탭 툴팁 | `EfficacyPanel` 탭바에 직접 툴팁 부착하도록 수정 완료. 초기 오배선 버그 수정됨 |
| 현재 운영 판단 | rollout 추천 단계는 아직 `shadow` |

### 현재 관측 지표 (2026-05-08 세션 마감 기준)

- `A/B pnl delta`: `-3.60pt`
- `A/B accuracy delta`: `-0.10%p`
- `Calibration ECE`: `0.399783`
- `Meta labels`: `34`
- `Meta best match rate`: `41.18%`
- `Rollout stage`: `shadow`

### 현재 판단

- 기능 구현/배선 자체는 큰 축에서 완료됨
- 다만 실전 승격 관점에서는 `Calibration` 과 `A/B delta` 가 아직 약점
- 다음 우선순위는 `temperature scaling 기반 calibration 개선`, `changed sample 53건 분석`, `meta label 추가 축적 후 rollout 재평가`

---

## 2026-05-11 Cybos 자동 로그인 확정

| 항목 | 값 |
|---|---|
| 스크립트 | `scripts/cybos_autologin.py` |
| 실행 파일 | `C:\DAISHIN\STARTER\ncStarter.exe /prj:cp` |
| 비밀번호 | `PASSWORD_OVERRIDE = "amazin16"` (하드코딩) |
| 비밀번호 입력 좌표 | `(971, 695)` |
| 모의투자 접속 버튼 | `(1416, 645)` |
| 팝업 최소 대기 | 10초 |
| Enter 후 처리 | 3초 후 `sys.exit(0)` (창 탐지 → 버튼 클릭 → 소멸 시 즉시 종료) |
| **상태** | ✅ 정상 동작 확인 (2026-05-11) |

---

---

## 2026-05-16 업데이트 (41차)

### Threshold 재보정

| 항목 | 이전값 | 변경값 | 비고 |
|---|---|---|---|
| 1m threshold | 0.0002 (0.02%) | 0.0005 (0.05%) | 12틱 |
| 3m threshold | 0.0003 (0.03%) | 0.0008 (0.08%) | 19틱 |
| 5m threshold | 0.0004 (0.04%) | 0.0011 (0.11%) | 26틱 |
| 10m threshold | 0.0006 (0.06%) | 0.0016 (0.16%) | 38틱 |
| 15m threshold | 0.0008 (0.08%) | 0.0022 (0.22%) | 53틱 |
| 30m threshold | 0.0012 (0.12%) | 0.0032 (0.32%) | 77틱 |

근거: 5월 초 일중 고저폭 ~96pt 기준 σ_1min≈1.47pt → 각 threshold ≈ 0.4~0.5σ (FLAT 비율 29~37% 목표)

### Dashboard 상태

| 항목 | 현재 상태 |
|---|---|
| PnlHistoryPanel 체크박스 | 순방향/역방향 토글 체크박스 추가 (탭바 우측 코너) |
| PredictionPanel 툴팁 | HTML 리치 포맷 전환 (SHAP 윈도우 테이블, HZ 설명 전체 재작성) |
| CB 툴팁 | 슬랙 알림 내용 ③항목 추가 |
| `DashboardAdapter.chk_slack` | ✅ 노출 수정 완료 (B51 핫픽스) |

### Threshold Monitor

- `_log_threshold_monitor()` 추가 — GBM 재학습 완료 시 + 30분 주기로 ATR 동적 threshold vs Static 비교 기록
- 모델 AI탭에 `✅ 안정` / `⚠ 초과` 판정 자동 기록

### EmergencyExit pending_registrar

- CB/KillSwitch 비상청산 주문 시 `pending_registrar` 콜백으로 `EXIT_FULL` pending 선등록
- Chejan 체결이 "외부체결(HTS/수동)"로 오분류되지 않도록 방지

### PositionTracker same-side sync 보강

- same-side broker sync 시 기존 신호 등급(A/B/C) 보존 — BROKER로 덮어쓰기 방지
- 이미 실행된 TP 플래그(partial_1/2/3_done) 보존 — Chejan이 와도 재발동 방지

### 현재 기동 상태

| 항목 | 상태 |
|---|---|
| 자동 로그인 | ✅ 정상 (`start_mireuk.bat`) |
| Cybos 연결 | ✅ 성공 (ServerType=1 모의투자) |
| B51 크래시 | ✅ 수정 완료 |
| Qt 이벤트 루프 | 재기동 후 확인 필요 |

---

## 2026-05-16 업데이트 (46차)

### PnlHistoryPanel 버그 4종 수정

| 항목 | 이전 | 이후 |
|---|---|---|
| 역방향 체크박스 | forward_pnl 전체 표시 (의미론 오류) | reverse_entry_enabled=1 행만 필터링 |
| 순+역 모두 체크 | exec+fwd 합산 (2배) | 전체 행의 pnl_krw (정상) |
| 총 손익 | broker P&L × 거래 수 중복합산 | 고유 날짜 단위 1회 합산 |
| 체크박스 재시작 | _save_ui_prefs()가 pnl_cb_* 키 삭제 | 읽고-병합-쓰기로 키 보존 |
| P/L 원 별표 | "6,267,000원 ★" | "6,267,000원" |

### 미니선물 pt_value 버그 수정 (B53)

| 항목 | 변경 |
|---|---|
| TRADE_PNL_FORMULA_VERSION | 3 → 4 (기존 레코드 재마이그레이션 강제) |
| normalize_trade_pnl | pt_value 파라미터 추가 (기본값 250,000) |
| _get_pt_value_from_prefs() | ui_prefs.json → symbol_code → get_contract_spec()["pt_value"] |
| _migrate_trades_db | _get_pt_value_from_prefs()로 pt_value 결정 |
| main._trade_metrics_pair | self._pt_value 전달 |

재시작 시 v4 마이그레이션 자동 실행 → 5/14 기준 14.5M→2.9M (5배 정상화).

### 잔여 이슈

- 5/14 2.9M vs 실제 ~1.5M: qty 과다 기록 문제 별도 분석 필요

---

## 2026-05-17 업데이트 (47~48차 + DB 초기화)

### trades.db 초기화

| 항목 | 내용 |
|---|---|
| 초기화 일시 | 2026-05-17 |
| 백업 파일 | data/db/trades_backup_20260517.db (92KB) |
| 초기화 내용 | trades 191건, daily_stats 10행, daily_broker_pnl 2행 전체 삭제 |
| 목적 | 2026-05-19(월)부터 오염 없는 DB로 손익추이 유효성 검증 |
| 검증 포인트 | 신규 체결 거래가 pt_value=50k 기준으로 정확히 기록되는지, qty 과다 기록 없는지 |

### 손익추이 주별/월별 탭 설계 확정

| 탭 | P/L 원 소스 | MDD |
|---|---|---|
| 일별 | broker 정산 우선, 없으면 DB | 일별 DB (broker 있는 날 broker 적용) |
| 주별 | DB pnl_krw 일관 | 일별 DB 집계 (trade 진동 제거) |
| 월별 | DB pnl_krw 일관 | Sharpe만 표시 |
| 요약 헤더 | broker 정산 고유 날짜 합산 | 전체 MDD (_mdd) |

### 현재 기동 상태

| 항목 | 상태 |
|---|---|
| trades.db | 초기화 완료 (0건) |
| 백업 | data/db/trades_backup_20260517.db |
| 다음 첫 거래 | 2026-05-19(월) 시작 예정 |
| 검증 모드 | 오염 없는 DB로 손익추이 유효성 평가 |
## 2026-05-18 상태 업데이트 (GBM/SHAP 운영 패치)

### 1. GBM 재학습 산출물/런타임 정합성
- `learning/batch_retrainer.py`가 이제 `gbm_*.pkl`, `scaler_*.pkl`, `feature_names.pkl`를 함께 저장한다.
- `MultiHorizonModel._load_all()`과 배치 재학습 산출물 포맷이 일치하도록 맞춰져, warmup/manual retrain 후 런타임 reload 경로가 정상화됐다.

### 2. 좌하단 멀티 호라이즌 예측 패널
- `파라미터 상관계수`는 importance 요약 문자열이 아니라 최근 feature history 기반 실제 상관계수 문자열(`rho`)을 사용한다.
- `파라미터 중요도`는 SHAP cache가 있으면 SHAP 기준으로 덮어쓰도록 배선됐다.
- 단, 현재 운영 모델의 `feature_names.pkl`에 따라 일부 피처(`foreign_call_net`, `foreign_retail_divergence`, `program_non_arb_net`)가 SHAP 대상에서 빠질 수 있으므로 다음 managed-set 재학습 검증이 필요하다.

### 3. 재시작 직후 restored/live 분리
- 재시작 시 `raw_features` 기반 복원값과 당일 live 버퍼를 분리하는 로직이 들어갔다.
- 상관계수와 SHAP는 저장 데이터로 즉시 복원 가능하며, 이후 live buffer가 쌓이면 실시간 계산으로 전환된다.

### 4. 중패널 `동적 피처 (SHAP)` 상태
- CORE 3개/동적 TOP3/전체 피처 순위/쿨다운/교체 이력 패널이 실제 `ShapTracker` 데이터와 연결됐다.
- 운영 플로우 카드 추가:
  - `추천 1 적용 + 재학습`
  - `현재 세트 재학습`
  - `세트 원복`
- managed feature set은 `data/db/shap_feature_registry.json`으로 관리하며, retrain 시 batch retrainer가 이를 읽어 active feature set 기준으로 학습한다.

### 5. 오늘 확인된 startup 이슈와 현재 최종 블로커
- 수정 완료:
  - `DB_DIR` import 누락 `NameError`
  - `shap_tracker_history.json` 과 현재 feature length 불일치로 인한 `IndexError`
- 현재 최종 블로커:
  - SHAP/UI 패치가 아니라 `U-CYBOS/CYBOS Plus is not connected` 브로커 세션 미연결
  - 앱은 SHAP 패치 구간을 통과한 뒤 broker connect 단계에서 종료된다.
## 2026-05-22 (82차) — Micro Regime Warmup UI

### 배경

10:03:43 헤더 `횡보장` 표시를 추적한 결과, 실제로는 `10:03:00` 1분봉 갱신 시점의 미시 레짐이 유지된 것이었고, 당시 `ADX=15.0` 은 실측이 아니라 버퍼 부족 fallback 값이었다. 장중 재시작/초기 분봉 구간에 미시 레짐 해석 신뢰도가 낮다는 점을 UI에서 드러낼 필요가 확인되었다.

### 현재 상태

| 항목 | 상태 |
|---|---|
| `MicroRegimeClassifier` 워밍업 메타 | **완료** — `L1 TR/ATR seed` / `L2 ADX warmup` / `L3 ATR avg warmup` / `READY` 계산 |
| 헤더 워밍업 표시 | **완료** — `lbl_micro_regime` 아래 상태 문구 + progress bar 추가 |
| 남은 시간 표시 | **완료** — `remaining_bars` 기준 `N분 남음` 노출 |
| 장중 재시작 초기 해석 보조 | **완료** — 워밍업 중에는 상단에서 레짐 과신 방지 |
| ATR avg 준비용 버퍼 길이 수정 | **완료** — close/high/low buffer 상한 확장 |
| 실 UI 런처 검증 | **미완료** — 다음 기동 시 헤더 배치와 가독성 확인 필요 |

### 구현 파일 (82차)

| 파일 | 변경 내용 |
|---|---|
| `collection/macro/micro_regime.py` | 워밍업 상태 계산 + 버퍼 길이 수정 + 파일 정리 |
| `main.py` | `dashboard.update_micro_regime_warmup(_mr.get("warmup"))` 호출 |
| `dashboard/main_dashboard.py` | 미시 레짐 배지 아래 워밍업 상태 라벨 / progress bar 추가 |

### 다음 확인 사항

1. `start_mireuk.bat` 재기동 후 헤더에서 워밍업 바가 정상 위치/색상으로 보이는지 확인
2. 장중 재시작 직후 `L1 → L2 → L3 → READY` 전환이 실제 시간 흐름과 맞는지 SYSTEM/UI 로그 대조
3. 워밍업 완료 전 `횡보장/추세장` 텍스트는 유지되더라도 사용자 해석이 충분히 보정되는지 판단

---
