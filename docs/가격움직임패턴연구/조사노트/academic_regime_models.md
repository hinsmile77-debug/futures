# 학계의 시장 국면(regime) 정의·분류·탐지 모델 — 지수선물 일봉·분봉 적용 관점

> 표기: [검증] = 이번 세션에 원문/초록을 직접 열어 수치를 확인. [서지] = 서지·URL은 정확하나 본문 수치는 이번 세션에 열람하지 못했고 연구자 사전지식에 의존 — 리포트 작성 시 "원문 확인 필요"로 다룰 것.
> 데이터 해상도: (D)=일/월봉, (I)=장중.

## 1. Markov-switching 모형 (Hamilton 1989; Ang & Bekaert; Guidolin & Timmermann) — 상태 수, 상태 정의, 상태 수 선택, 지속기간

### Takeaway
학계의 표준 결과는 "주식 국면은 평균보다 **변동성**으로 식별된다"이다. 2상태(저변동/고변동)가 기본값이고, 상태 수는 비표준 LR 검정 문제 때문에 검정보다 경제적 논거로 정하는 경우가 많다. 주식·채권을 함께 모델링하면 4상태(crash/slow growth/bull/recovery)가 필요하다는 결과가 대표적이다. 전이확률은 0.95–0.98 수준(월간)으로 국면은 매우 지속적이다.

### Cited Findings
- (D, 월간) Ang & Timmermann 서베이가 S&P500 초과수익률(1953:01–2010:12, 월간)에 2상태 MS 모형을 추정: 고변동 국면 σ0=4.89%/월, 평균 μ0=0.33%; 저변동 국면 σ1=2.45%/월, μ1=0.90%; 전이확률 P=0.9770, Q=0.9512. 평균 동일성 μ0=μ1은 기각 못 함(p=0.106), 변동성 동일성은 기각(p=0.016) → "regimes are mostly identified by volatility". [검증] — [Ang & Timmermann (2011), "Regime Changes and Financial Markets", NBER WP 17182](https://www.nber.org/papers/w17182)
  - 위 P·Q에서 기대지속기간 1/(1−p) ≈ 43.5개월(P)·20.5개월(Q) (연구자 계산, P=p00·Q=p11 매핑은 서베이 표기 가정).
- 고변동 국면은 평균적으로 낮은 수익률 → 약세장에 대응; 이 패턴은 Hamilton & Susmel(1994) 이후 일관됨. 모형이 유발하는 제곱수익률 1차 자기상관 0.77(수준 자기상관은 ≈0) — 레짐 지속성이 변동성 군집을 만든다. [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)
- 1997–2003이 단일 "고변동 국면"으로 분류되어 **닷컴 강세장과 이후 붕괴를 모두 포함** — 변동성 국면 ≠ 방향(강세/약세) 국면. [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)
- 상태 수 선택: "It is not uncommon to simply fix the number of regimes at some value, typically two". 단일 국면 귀무가설 하에서 다른 국면 파라미터가 식별되지 않아(nuisance parameter) 통상 LR 통계량이 χ² 분포를 따르지 않음 — Davies(1977), Hansen(1992), Cho & White(2007), Garcia(1998) 참조; 대안으로 Hamilton(1996) 잔차 검정. [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)
- 레짐 모형은 점프 모형을 특수형으로 포함: 점프 = 다음 기에 즉시 이탈하는 국면(p10≈1). Rietz(1988) 3국면(정상 2 + crash 1, crash 잔류확률 0). [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)
- Hamilton(1989) GNP 2국면 모형의 재현에서 기대지속기간: 침체 ≈4.1분기, 확장 ≈10.4분기 (statsmodels 재현값 — Hamilton 원표 아님). [검증·2차] — [statsmodels Markov AR 예제](https://www.statsmodels.org/v0.14.4/examples/notebooks/generated/markov_autoregression.html); 원논문: Hamilton (1989), Econometrica 57(2), 357–384.
- Guidolin & Timmermann(2006, J. Applied Econometrics): 개별 자산은 2–3상태로 충분하지만 주식·채권 결합분포에는 **4상태(crash, slow growth, bull, recovery)** 필요. crash 국면은 약 50% 확률로 recovery로 이탈(되돌림). 후속(2007, JEDC) "Asset allocation under multivariate regime switching" — 국면별 최적 포트폴리오가 크게 달라지고 OOS에서 경제적 가치. [초록 수준 검증] — [Guidolin & Timmermann JAE 데이터 아카이브](https://journaldata.zbw.eu/dataset/an-econometric-model-of-nonlinear-dynamics-in-the-joint-distribution-of-stock-and-bond-returns); [Bocconi IRIS](https://iris.unibocconi.it/handle/11565/3732701)
- Ang & Bekaert: "International Asset Allocation with Regime Shifts", RFS 15(4) 1137–1187 (2002); "How do Regimes Affect Asset Allocation?", FAJ 60(2) 86–99 (2004). 2국면(정상/약세·고상관) 구조. [서지] — [Bekaert 논문 목록 PDF](https://business.columbia.edu/sites/default/files-efs/imce-uploads/gbekaert/papers/inquire.pdf); [NBER w10080](https://www.nber.org/papers/w10080.pdf)

### Inferences
- 1분봉 KOSPI200 선물에 MS를 적용하면, 평균(방향) 차이는 통계적으로 식별이 약하고 변동성 차이가 국면을 결정할 가능성이 높다 — "추세/횡보" 방향 국면을 원하면 MS 단독으로는 부족하고 방향성 피처(수익률 부호·Sortino 등)를 넣은 점프모형 등이 필요.
- 상태 수는 2(저/고 변동)로 시작하고, 3번째 상태(crash/점프)는 p_stay≈0인 일시 국면으로 둘 근거가 있다.

### Gaps
- Ang & Bekaert 원표의 정확한 전이확률·기대지속기간은 이번에 확인 못 함.
- BIC로 상태 수를 정한 금융 분봉 연구의 구체 수치(예: 3 vs 4 상태 BIC 차이)는 찾지 못함.
- Guidolin–Timmermann 4상태의 각 상태 평균·변동성·지속기간 수치는 초록만 확인.

## 2. HMM / Gaussian mixture / 통계적 점프모형(Statistical Jump Model) — 왜 점프모형이 지속성에서 우월한가

### Takeaway
점프모형(JM)은 k-means 목적함수에 "상태 전환 1회당 λ" 페널티를 더해 국면 지속성을 직접 통제한다. 일봉 주가지수 3종(1990–2023, 10bp 비용·1일 지연)에서 JM은 HMM보다 전환 횟수가 훨씬 적고 Sharpe·MDD가 일관되게 우월했다.

### Cited Findings
- JM 목적함수: min Σ_t ½‖x_t − θ_{s_t}‖² + λ Σ_t 𝟙{s_{t−1} ≠ s_t}. λ=0이면 k-means로 환원. K=2(강세 s=0 = 학습기 누적초과수익 높은 상태, 약세 s=1). 좌표하강 + 동적계획, 10회 랜덤 시작. 예시 λ=50, 통상 50–100. [검증] — [Shu, Yu & Mulvey (2024), "Downside Risk Reduction Using Regime-Switching Signals: A Statistical Jump Model Approach", arXiv 2402.05272](https://arxiv.org/html/2402.05272v3)
- 피처(3개, EWM): 하방편차 halflife 10일, Sortino halflife 20일, Sortino halflife 60일. (D) [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)
- λ 선택: 시계열 교차검증, 매월 갱신, 8년 검증창; 각 λ로 0/1 전략을 1일 지연·편도 10bp로 돌려 검증 Sharpe 최대 λ 채택. 파라미터는 6개월마다 3,000일(~12년) 창으로 재적합. [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)
- 연간 전환 횟수(1982–2023): HMM 8.5(평활 k=0)→6.6(k=2)→4.9(k=4)→3.2(k=8)→2.0(k=20); JM 9.7(λ=0)→2.7(λ=5)→1.7(λ=15)→0.8(λ=35)→0.5(λ=70)→0.4(λ=150). [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)
- OOS 1990–2023(편도 10bp, 1일 지연) Sharpe/MDD: S&P500 B&H 0.48/−55.2%, HMM 0.54/−28.9%, **JM 0.68/−26.6%**; DAX 0.30/−72.7%, 0.35/−40.5%, **0.44/−39.4%**; Nikkei 0.12/−79.1%, 0.19/−48.6%, **0.31/−45.3%**. 지연 1·5·10일 JM Sharpe S&P 0.68/0.71/0.70 vs HMM 0.54/0.55/0.51; DAX JM 0.44/0.38/0.29 vs HMM 0.35/0.25/0.12. [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)
- 지속성의 근거: 국면 전략은 국면을 "예측"하는 것이 아니라 전환 직후 식별하고 그 지속성에서 이익을 얻는 구조(Nystrup et al. 2015 인용); 자주 뒤집히는 신호는 거래 지연이 들어가면 쓸모 없음. [검증] — [Shu et al. arXiv PDF](https://arxiv.org/pdf/2402.05272)
- 원천 논문(서지): Nystrup, Lindström & Madsen (2020), "Learning hidden Markov models with persistent states by penalizing jumps", *Expert Systems with Applications* 150:113307; Nystrup, Kolm & Lindström (2021), "Feature selection in jump models", *ESWA* 184:115558; Nystrup, Kolm & Lindström (2020), "Greedy online classification of persistent market states using realized intraday volatility features", *J. Financial Data Science* 2(3):25–39 (**장중 실현변동성 피처** 사용 — 분봉 시스템에 가장 근접); Bemporad et al. (2018), "Fitting jump models", *Automatica* 96:11–21. [서지, Shu et al. 참고문헌에서 검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)
- Nystrup 발표 초록: 점프 페널티 추정은 전이율을 직접 통제, 초기값 민감도 낮음, 상태 수 증가 시 성능 우위, 조건부분포 오지정에 강건; 상태 지속성을 제대로 추정하면 거래비용이 크게 감소. [검증] — [NYU CIMS 세미나 "Learning Hidden Markov Models by Penalizing Jumps"](https://cims.nyu.edu/dynamic/events/2422)
- Sparse JM(Lindström): 암호자산에서 HMM보다 더 적고 더 지속적인 상태. [검증·초록] — [KTH 세미나](https://www.kth.se/math/kalender/erik-lindstrom-what-drives-cryptocurrency-returns-learning-market-regimes-through-the-sparse-statistical-jump-model-1.1224113)
- Continuous JM(Aydinhan, Kolm, Mulvey & Shu 2024, *Annals of OR*): 국면 확률을 출력하고 "mode loss"로 순수 국면 쪽으로 유도; 국면 불균형·소표본에서 개선이 가장 큼. [검증·초록] — [SSRN 4556048](https://papers.ssrn.com/abstract=4556048)

### Inferences
- 1분봉에서 "국면이 분 단위로 깜빡이는" 문제(CB① 신호 반전과 동형)는 λ 페널티가 직접 겨냥하는 결함이다. λ를 정확도가 아니라 **비용·지연을 반영한 전략 성과로 CV**하는 Shu et al. 절차가 그대로 이식 가능.
- HMM에 사후 평활(rolling mean k)을 더해도 전환 횟수는 줄지만 JM과 같은 성과는 안 나왔다 — "HMM + 사후 히스테리시스"보다 "학습 목적함수 자체에 지속성"이 유리하다는 증거(일봉 기준).

### Gaps
- 분봉 데이터에서 JM vs HMM OOS 비교 수치는 찾지 못함(Nystrup 2020 JFDS가 장중 실현변동성 피처를 쓰지만 본문 미열람).
- Shu et al.의 λ 후보 그리드는 본문에 명시 안 됨.

## 3. 추세 vs 평균회귀 국면 — Hurst, 분산비 검정, 자기상관, Kaufman ER, ADX

### Takeaway
학계 정식 검정은 Lo–MacKinlay 분산비(VR) 검정이고, Hurst R/S는 소표본 상향/하향 편향이 커서 Anis–Lloyd 기대값 보정 없이 0.5 기준선과 비교하면 안 된다. ER·ADX는 실무 지표로 학술적 임계 근거가 약하다.

### Cited Findings
- 원시 R/S 기울기는 짧은 시계열에서 0.5에서 유의하게 이탈하는 편향; Anis–Lloyd가 백색잡음 하 R/S 기대값을 감마함수로 도출, 보정 H = 0.5 + (관측 − 기대 로그로그 기울기). Weron(2002)이 Anis–Lloyd 보정 R/S의 부트스트랩 95% 구간(표본 길이 의존) 제시. 대부분의 Hurst 추정량은 점근분포 이론이 없음. [검증·2차] — [Wikipedia: Hurst exponent](https://en.wikipedia.org/wiki/Hurst_exponent); [Conniffe (2000) ESRI](https://www.esri.ie/system/files/media/file-uploads/2015-07/JACB2000_Conniffe.pdf); 구현: [R pracma::hurstexp](https://rdrr.io/cran/pracma/man/hurst.html)
- 보정 방식이 출처마다 다름(기대 R/S를 빼고 회귀 vs 기울기에 0.5를 더함) — 구현 전 원문 확인 필요. [검증] — [Wikipedia](https://en.wikipedia.org/wiki/Hurst_exponent); [metricgate](https://metricgate.com/docs/hurst-exponent/)
- 가격(적분 계열)에 적용하면 H가 1 쪽으로 밀림 — 반드시 수익률에. [검증·2차] — [screamer RollingHurst 문서](https://screamer.readthedocs.io/en/latest/functions_rolling/RollingHurst.html)
- Lo & MacKinlay (1988), "Stock Market Prices Do Not Follow Random Walks: Evidence from a Simple Specification Test", RFS 1(1):41–66 — VR(q)=Var(q기 수익)/(q·Var(1기)); 랜덤워크 하 VR=1, 이분산 강건 z*(q) 통계량. VR>1 추세(양의 자기상관), VR<1 평균회귀. [서지] — [RFS DOI 10.1093/rfs/1.1.41](https://doi.org/10.1093/rfs/1.1.41)
- Kaufman Efficiency Ratio ER = |P_t − P_{t−n}| / Σ|ΔP| (0–1), KAMA의 구성요소(Kaufman, *Trading Systems and Methods*); ADX(Wilder 1978) 관행 임계 >25 추세 / <20 무추세. 둘 다 동료심사 통계 근거가 있는 임계는 아님. [서지·실무관행] — 학술 출처 확인 못 함 (Gaps 참조)

### Inferences
- 프로젝트 CLAUDE.md의 317차 결과(N=60 Hurst가 랜덤워크를 H≈0.33–0.36으로 오독)는 위 소표본 편향 문헌과 정확히 일치한다. 정식 국면 정의로는 "H > 0.5"가 아니라 **"H − E_AL[H|N] > 부트스트랩 상한"** 또는 VR z*-검정 유의성을 기준으로 삼는 것이 학술적으로 방어 가능.
- 분봉 VR은 장중 U자 변동성(§8) 때문에 이분산 강건 z*를 써야 한다.

### Gaps
- ER·ADX 임계의 학술 검증 연구, 분봉 KOSPI200에서의 VR 실증은 찾지 못함.
- Lo–MacKinlay 원 표의 VR 수치는 이번에 열람하지 못함.

## 4. 변동성 국면 · 금융 난류(Turbulence) · 흡수비율

### Takeaway
Kritzman & Li(2010)의 turbulence = 수익률 벡터의 Mahalanobis 거리. 난류 국면에서 위험자산 수익이 크게 낮고 난류는 수 주간 지속된다. 실무 정의는 "turbulence 상위 분위(통상 75% 또는 90%)".

### Cited Findings
- Kritzman & Li (2010), "Skulls, Financial Turbulence, and Risk Management", *Financial Analysts Journal* 66(5):30–41. turbulence d_t = (y_t − μ)′Σ⁻¹(y_t − μ) — Mahalanobis(두개골 분석용) 거리와 사실상 동일. 급등 시점이 1970년대 말–80년대 초 스태그플레이션, 1987 폭락, 걸프전, 2008 위기와 일치. 난류기에 위험자산 수익이 현저히 낮고, **난류는 시작 후 수 주간 지속**. 난류기 공분산으로 VaR 스트레스테스트. [검증·초록] — [IDEAS/RePEc](https://ideas.repec.org/a/taf/ufajxx/v66y2010i5p30-41.html); [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/skulls-financial-turbulence-and-risk-management); [Alpha Architect 요약](https://alphaarchitect.com/skulls-financial-turbulence-and-risk-management/)
- 확장: VAR 기반 turbulence 및 부호화(signed) turbulence로 강세/약세 전환 탐지(2021 히토쓰바시 WP). [검증·초록] — [HUB-FS WP FS-2021-E-001](https://www.fs.hub.hit-u.ac.jp/inc/files/staff-research/workingpaper/FS-2021-E-001.pdf)
- 흡수비율(Kritzman, Li, Page & Rigobon 2011, "Principal Components as a Measure of Systemic Risk", J. Portfolio Management 37(4)): 상위 고유벡터(자산수의 약 1/5)가 설명하는 분산 비율. [서지]
- MS 모형에서 고변동 국면은 GARCH보다 급격한 변동성 전환을 포착(Hamilton & Susmel 1994 SWARCH, Gray 1996 RS-GARCH) — GARCH는 변화가 "너무 점진적". [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)

### Inferences
- 단일 자산(KOSPI200 선물)이라도 피처 벡터(수익률·실현변동성·거래량·베이시스·외인 순매수 등)에 Mahalanobis 거리를 적용하면 turbulence 국면을 정의할 수 있다. 다만 피처 공분산을 장중 시각별로 다르게 둬야 U자 계절성이 turbulence로 오인되지 않는다.
- 프로젝트의 FP-CRITICAL PSI(분포 거리)와 개념상 같은 계열 — PSI 대신 Mahalanobis 분위가 학술적으로 더 표준.

### Gaps
- Kritzman–Li 원문의 난류 임계 분위(75%?)·지속 일수 정확 수치는 회원 전용이라 미확인.
- VIX 분위 기반 국면(예: VIX>20/30) 학술 정의, VKOSPI 국면 연구는 이번 범위에서 찾지 못함.

## 5. 변화점 탐지(BOCPD, PELT, CUSUM) — 국면 경계

### Takeaway
변화점 방법은 "국면 재발"을 가정하지 않는 경계 탐지로, 온라인용 BOCPD와 오프라인 최적분할 PELT가 표준. 이번 세션에서는 서지만 확보했다.

### Cited Findings
- Adams & MacKay (2007), "Bayesian Online Changepoint Detection" — run length r_t의 사후분포를 재귀 갱신, hazard H(τ)(상수 hazard = 기하분포 국면 길이, 1/λ = 기대 국면 길이), 계산량 O(t)/스텝(가지치기 시 상수). [서지] — [arXiv 0710.3742](https://arxiv.org/abs/0710.3742)
- Killick, Fearnhead & Eckley (2012), "Optimal detection of changepoints with a linear computational cost" (PELT), JASA 107(500):1590–1598 — 페널티 비용 최소화의 정확해를 (조건 하) 선형 시간에; 페널티는 BIC/SIC형 (p·log n) 흔히 사용. [서지] — [arXiv 1101.1438](https://arxiv.org/abs/1101.1438)
- CUSUM: Page (1954), Biometrika 41 — 누적 편차가 임계 h를 넘을 때 경보; ARL(평균 경보 간격)로 임계 설계. [서지]
- 레짐 전이확률은 국면 지속기간에 의존할 수 있음(duration-dependent MS, Durland & McCurdy 1994). [검증·참고문헌] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)

### Inferences
- BOCPD의 상수 hazard는 MS의 기하분포 지속기간과 수학적으로 동형 — 1/λ를 "분 단위 기대 국면 길이"로 사전 지정할 수 있어 해석이 쉽다.
- 장중 U자 변동성을 제거(정규화)하지 않으면 개장·마감마다 변화점이 기계적으로 검출된다.

### Gaps
- 금융 분봉에서 BOCPD/PELT의 OOS 매매 성과 실증은 이번에 찾지 못함.

## 6. 비지도 군집 — k-means, Wasserstein k-means, path signature

### Takeaway
Horvath–Issa–Muguruza는 수익률 구간을 경험분포로 보고 p-Wasserstein 거리로 k-means를 수행(WK-means), 합성·실데이터에서 모멘트 기반·HMM 대비 우월하다고 보고.

### Cited Findings
- Horvath, Issa & Muguruza, "Clustering Market Regimes using the Wasserstein Distance", arXiv 2110.11848 (2021) → *Journal of Computational Finance* 28(1), 2024. 시계열 구간 = 확률분포, p-Wasserstein 거리; 모형 가정 불필요. 평가: 군집 내·간 MMD. 합성(국면 변화 기지) 및 실데이터에서 모든 대안보다 "greatly outperforms"; 비정규 수익률에서 모멘트 기반 접근, 합성에서 HMM보다 우수. 향후 과제: fuzzy·계층적 군집. [검증·초록] — [arXiv 2110.11848](https://arxiv.org/abs/2110.11848v1); [SSRN 3947905](https://papers.ssrn.com/abstract=3947905); [J. Comput. Finance 28(1)](https://www.risk.net/journal-of-computational-finance/volume-28-number-1-june-2024)
- JM은 λ=0일 때 k-means와 동일 — k-means 국면 군집은 시간 지속성 제약이 없어 전환이 잦음(연 9.7회). [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)

### Inferences
- WK-means는 구간 길이(예: 30–60분 롤링 창)의 분봉 수익률 분포를 그대로 군집할 수 있어 분봉에 바로 적용 가능하나, 지속성 제약이 없으므로 JM식 전환 페널티나 사후 최소 지속 규칙을 결합해야 실매매 가능.

### Gaps
- path signature 기반 국면 군집(Issa, Horvath 등 2023) 수치는 이번에 확인 못 함.
- WK-means의 매매 OOS 성과는 논문 범위 밖(군집 품질만 평가).

## 7. 강세/약세 연대 결정 규칙 (Pagan & Sossounov 2003; Lunde & Timmermann 2004)

### Takeaway
PS(2003)는 Bry–Boschan 경기순환 알고리즘을 월간 주가에 적용(후보 정점·저점 + 최소 국면·순환 기간 검열, 급변 시 예외). LT(2004)는 누적 수익 임계(기본 20%)로 정점·저점을 정의하며 비대칭 임계도 탐색.

### Cited Findings
- Pagan & Sossounov (2003), "A Simple Framework for Analyzing Bull and Bear Markets", *J. Applied Econometrics* 18(1):23–46. 월간 주가에 Bry–Boschan 적용: 후보 정점·저점 식별 후 국면·완전순환의 최소 기간 검열, 급격한 변동 시 예외 규칙. 한 2차 출처는 창을 "양쪽 6개월"로 기술(PS 2003 p.25 인용). 흔히 인용되는 파라미터(창 8개월, 최소 국면 4개월, 최소 순환 16개월, 20% 이상 변동 시 최소기간 예외)는 오픈소스 구현에서만 확인 — **창 길이 6 vs 8개월 출처 상충**. [부분 검증] — [ResearchGate: PS 2003](https://www.researchgate.net/publication/2391586_A_Simple_Framework_for_Analyzing_Bull_and_Bear_Markets); [Toronto WP "Extracting bull and bear markets from stock returns"](https://www.economics.utoronto.ca/public/workingPapers/tecipa-369.pdf); [GitHub 구현 PR](https://github.com/adarbari/algo-trading/pull/208)
- Lunde & Timmermann (2004), "Duration Dependence in Stock Prices: An Analysis of Bull and Bear Markets", *JBES* 22(3):253–273. 누적수익 20% 임계로 정점·저점 정의, 대안·비대칭 임계도 탐색. 국면 종료확률(hazard)을 국면 나이와 금리 등 상태변수 함수로 모형화: 랜덤워크는 강세·약세 모두 기각, GARCH는 적합은 낫지만 매우 긴 강세장과 불일치, 금리 상승 시 약세장 hazard 하락(하락 지속). [검증·초록/2차] — [CEPR DP4104](https://cepr.org/publications/DP4104); [Toronto WP tecipa-402 "Bull Corrections and Bear Rallies"](https://www.economics.utoronto.ca/public/workingPapers/tecipa-402.pdf); 구현: [R bbdetection](https://cran.r-universe.dev/bbdetection/doc/manual.pdf)
- 강세/약세 판별·예측 비교(Kole & van Dijk, "How to Identify and Predict Bull and Bear Markets?"): 규칙 기반 vs MS 비교. [서지] — [ERIM PDF](https://www.erim.eur.nl/fileadmin/erim_content/documents/BullBear3.pdf)
- 이들 규칙은 **사후(ex post)** 연대 결정 — 정점은 20% 하락이 확인된 뒤에야 확정된다. MS 국면은 서사적 국면을 사후 설명하지만 실시간 예측에도 쓸 수 있다는 것이 MS의 장점. [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)

### Inferences
- 월간 20% 규칙을 분봉으로 옮기려면 임계를 변동성 단위(예: k×ATR 또는 실현σ×√T)로 스케일해야 한다 — 절대 % 임계는 프로젝트 539차 ATR_MIN_ENTRY 문제(절대 pt 임계의 실효강도 드리프트)와 같은 결함을 낳는다.
- 사후 연대 규칙은 **라벨(정답지) 생성용**으로 쓰고, 실시간 분류기는 별도로 두는 것이 학계 관행과 맞는다 — 라벨 생성기를 실시간 피처로 쓰면 look-ahead.

### Gaps
- LT 비대칭 임계(예: 강세 20%/약세 15%)의 정확 값, 평균 강세·약세 지속기간 수치는 원문 미열람(MPRA 원문 접속 실패).

## 8. 장중 국면 — U자 변동성, 장중 모멘텀, 시각 효과

### Takeaway
장중 변동성·거래량의 U자 계절성은 국면이 아니라 **결정론적 시각 성분**이므로 국면 분류 전에 제거해야 한다(Andersen–Bollerslev). 장중 모멘텀은 지수선물 17종 1974–2020에서 견고하며, "개장~마감 30분 전 수익(rROD)"이 마지막 30분을 예측(OOS R² 2.88%, 전략 Sharpe 1.73). 감마 헤지가 원인으로 제시되며 다음 날들에 되돌림.

### Cited Findings
- Andersen & Bollerslev (1997), "Intraday Periodicity and Volatility Persistence in Financial Markets", *J. Empirical Finance* 4(2–3):115–158 — 외환·주식시장 수익률 변동성에 "pervasive intraday periodicity"; 이를 걸러내야 장중 변동성 동학이 드러남. S&P500 지수선물 수익률이 장초·장말에 높음(2차 인용). [검증·초록] — [Duke 교수 DB](https://fds.duke.edu/db/aas/Economics/faculty/boller/publications/237974); [Kellogg](https://www.kellogg.northwestern.edu/academics-research/research/detail/1997/intraday-periodicity-and-volatility-persistence-in-financial-markets/); [Heston-Korajczyk-Sadka 2차 인용 arXiv 1005.3535](https://arxiv.org/pdf/1005.3535)
- 일본 주식은 점심휴장 때문에 "이중 U자(doubly U-shaped)" 변동성; 예정된 거시발표는 일별 변동성 변동을 거의 설명 못 함(Andersen, Bollerslev & Cai 2000). [검증·초록] — [CityU 레코드](https://scholars.cityu.edu.hk/en/publications/intraday-and-interday-volatility-in-the-japanese-stock-market/)
- Wood, McInish & Ord (1985), "An Investigation of Transactions Data for NYSE Stocks", J. Finance 40(3):723–739 — 장중 수익률·변동성 U자의 고전 문헌. [서지]
- Gao, Han, Li & Zhou (2018), "Market Intraday Momentum", *JFE* 129(2):394–414: SPY 1993–2013, 전일종가→첫 30분 수익이 마지막 30분 수익을 예측; 변동성 큰 날·거래량 큰 날·경기침체·주요 거시발표일에 강함; 10개 다른 ETF에서도 존재; 설명은 Bogousslavsky(2016) 비빈번 리밸런싱 + 늦게 정보받은 거래자. 초기 원고 R² 약 2%(요약 출처). [검증·초록/2차] — [WUSTL 프로필](https://profiles.wustl.edu/en/publications/market-intraday-momentum/); [Alpha Architect](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/)
- Baltussen, Da, Lammers & Martens (2021), "Hedging Demand and Market Intraday Momentum", *JFE* 142(1):377–403: 지수선물 17종(북미 6·유럽 8·아시아/호주 3 — Nikkei225 SGX, TOPIX, ASX SPI200; **KOSPI200 미포함**), 채권 16, 원자재 21, 통화 8, 1974-12 – 2020-05. 지수선물 풀링 회귀: rONFH(첫 30분) 기울기 4.86(t≈6.5), R² 1.49%, **OOS R² −1.71%**; rROD(마감 30분 전까지) R² 2.45%, **OOS R² 2.88%**(최고). 즉 확장 표본에서 Gao 신호(첫 30분)는 OOS에서 무너지고 rROD가 우월. 지수선물 타이밍 전략(1/N): rONFH Sharpe 1.07(적중 55%), rONFH·rROD 동일부호 1.60(61%), **rROD 1.73(55%)**, 마지막 30분 상시 매수 0.11. 자산군 Sharpe 0.87–1.73. 1974–1999·2000–2020 양 하위표본 모두 존재. 원인: 옵션 마켓메이커·레버리지 ETF의 short gamma 헤지(가격 방향 매매), 예측력은 다음 수일 간 되돌림. [검증 — 원문 PDF] — [IDEAS](https://ideas.repec.org/a/eee/jfinec/v142y2021i1p377-403.html); [저자 PDF](https://academicweb.nd.edu/~zda/intramom.pdf)
- 같은 논문: 통화선물에서 효과가 가장 약한 이유를 U자 거래량 패턴이 가장 덜 뚜렷하기 때문으로 해석 — 장중 모멘텀은 U자 유동성 구조와 결부. [검증] — [저자 PDF](https://academicweb.nd.edu/~zda/intramom.pdf)

### Inferences
- KOSPI200 선물은 위클리·먼스리 옵션 시장이 크므로 딜러 감마 부호(net gamma exposure)가 장중 모멘텀 vs 평균회귀 국면의 학술적 근거가 있는 상태변수다 — Baltussen et al.은 감마 노출이 음(−)일 때 모멘텀이 강하다고 연결(감마 노출 구간별 수치는 이번에 표 판독 실패).
- 첫 30분 단독 신호는 장기 표본 OOS에서 음의 R²였으므로, 개장 국면만으로 마감 방향을 정하는 규칙은 학술적으로 약하다.
- 분봉 국면 분류의 1단계는 시각별 변동성 정규화(Andersen–Bollerslev 필터)여야 하며, 프로젝트 500차의 `cvd_divergence` 시계 오염 같은 "시각을 읽는 피처" 문제와 직결.

### Gaps
- Baltussen et al. 표의 감마 노출 구간별 계수, 개별 계약(Nikkei/TOPIX) 결과는 PDF 텍스트 레이아웃 손상으로 정확 판독 못 함.
- KOSPI200 선물 장중 모멘텀·opening range 학술 실증은 이번에 찾지 못함.
- Opening range breakout 학술 연구(예: Holmberg, Lönnbark & Lundström 2013) 수치는 미확인.

## 9. 국면 분류가 OOS 예측·매매를 실제로 개선하는가 — 실패 양상

### Takeaway
일봉 지수에서는 지속성 통제형 국면 신호(JM)가 비용·지연 반영 OOS에서 위험조정 성과를 개선한 증거가 있다. 그러나 평활확률의 look-ahead, 평균 식별의 어려움, 상태 수 검정의 비표준성, 신호 깜빡임이 대표 실패 양상이다.

### Cited Findings
- JM 국면 신호가 1990–2023 3개 지수 모두에서 B&H·HMM 대비 Sharpe↑·MDD 절반 수준(비용 10bp·1일 지연 포함). [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)
- HMM 신호는 지연에 취약: DAX Sharpe 지연 1→10일 0.35→0.12, Nikkei 0.19→0.07. [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3)
- 평활확률 Pr(s_t|I_T)는 **전체 표본을 조건부**로 함(서베이 Figure 4 정의) — 실시간에는 필터 확률 Pr(s_t|I_t)만 사용 가능. 서베이의 국면 그림은 평활확률이다. [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)
- 국면별 평균은 각 국면 관측치가 전체보다 적어 더 식별이 어렵고, S&P500 2국면에서 평균 차이 비유의(p=0.106). 국면별 기대수익은 국면 전환확률·실시간 학습을 반영한 사전 기대수익이 아님. [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)
- 수익률 예측력 자체가 국면 의존: Henkel, Martin & Nardari(2011) RS-VAR에서 예측력은 확장기 매우 약하고 침체기 강함. [검증] — [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)
- Guidolin–Timmermann 4상태 모형의 OOS 테스트에서 국면 모델링이 경제적 가치 추가(초록). [검증·초록] — [Bocconi IRIS](https://iris.unibocconi.it/handle/11565/3732701)
- 장중 신호도 OOS에서 뒤집힐 수 있음: 첫 30분 신호 지수선물 풀링 OOS R² −1.71%. [검증] — [Baltussen et al. (2021)](https://academicweb.nd.edu/~zda/intramom.pdf)
- 국면 라벨 순서 문제(label switching): JM/Shu et al.은 "학습기 누적초과수익이 높은 상태 = 강세"로 매 재적합 후 라벨을 정렬, Ang–Timmermann은 "s=0 = 고변동"으로 정렬 — 재학습마다 정렬 규칙이 필요. [검증] — [Shu et al. (2024)](https://arxiv.org/html/2402.05272v3); [Ang & Timmermann (2011)](https://www.nber.org/papers/w17182)

### Inferences
- 실시간 시스템 이식 체크리스트: ① 필터 확률만 사용(평활 금지) ② 재적합마다 라벨 정렬 규칙 고정 ③ 지속성 페널티/λ를 비용·지연 포함 전략 성과로 CV ④ 국면 사후 연대 규칙(PS/LT)은 라벨용으로만 ⑤ 시각 계절성 선제거.
- 분봉 해상도에서 위 일봉 OOS 결과가 재현된다는 학술 증거는 이번에 찾지 못했으므로, 국면 정의 채택은 프로젝트 자체 사전등록 검증(캠페인 채널)으로 판정해야 한다.

### Gaps
- 분봉 국면 분류기의 OOS 매매 개선을 보인 동료심사 연구, 2015–2025 국면 탐지 서베이 논문(예: 머신러닝 국면 탐지 리뷰)은 도구 호출 한도로 확보 못 함.
- 국면 모델 과적합(상태 수 과다)에 관한 정량 실증(예: 3상태 이상에서 OOS 악화 수치) 미확보.
