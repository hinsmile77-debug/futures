# 기관·실무자 국면(Regime) 분류 체계와 장중 Day Type — 매크로 vs 장중

> 범위 구분: **매크로 국면**(수주–수개월, 자산배분·CTA 레벨)과 **장중/일간 Day Type**(세션 단위, Market Profile·Crabel 계열)을 분리해 기록한다.
> 출처 품질 표기: [1차]=회사·저자 원문/초록, [2차]=요약·교육사이트·포럼. 2차 출처의 수치는 검증 전 가설로 취급할 것.
> 조사 한계: 도구 호출 약 20회. Dalton·Crabel·Steidlmayer 원서 본문, Kritzman FAJ 전문, Man 논문 그림 수치는 직접 확인하지 못했다.

## 1. 자산운용사·헤지펀드의 매크로 국면 분류 (상태·입력·임계)

### Takeaway
기관 국면 모델은 크게 (a) 데이터 주도 비지도 군집(Two Sigma GMM 4국면), (b) 2상태 Markov-switching "정상 vs 이벤트"(Kritzman/Page/Turkington, State Street 계열), (c) 거시 사분면(Bridgewater 성장×인플레이션 "기대 대비 서프라이즈"), (d) 위험회피 스코어 연속척도(SSGA MRI 0–100%)로 나뉜다. 공통점은 **변동성·상관 구조의 이상도**가 핵심 입력이며, 대부분 "예측 모델이 아니라 현재 상태 식별 + 노출 조절" 용도로 쓰인다는 점이다.

### Cited Findings
**Two Sigma (Botte & Bao, 2021-10-06) [1차]**
- 방법: Gaussian Mixture Model(비지도). 각 국면 = 17차원 가우시안 분포, 기간마다 국면별 소속 확률 산출 — [Two Sigma, "A Machine Learning Approach to Regime Modeling"](https://www.twosigma.com/articles/a-machine-learning-approach-to-regime-modeling/)
- 입력: Two Sigma Factor Lens 미국판 17개 팩터 수익률(Crowding 팩터는 데이터 한계로 제외). 분석기간 1971–2020 — 같은 출처
- 국면 수 4는 교차검증 로그우도로 선택; 군집 수가 유일한 하이퍼파라미터 — 같은 출처
- **Crisis**: Equity·Credit 평균수익이 음수인 유일한 국면, Trend Following 큰 양(+)수익, 평균 절대 팩터 상관이 가장 높음. 예: 1987, 2008 GFC, 2020 COVID — 같은 출처
- **Steady State**: 큰 낙폭 없는 "정상·건강" 국면, Equity·Credit·대부분 스타일 팩터 양호, 1971년 이후 가장 빈번 — 같은 출처
- **Inflation**: Local Inflation 팩터 두 자릿수 평균수익, 1970–80년대에만 출현, 2020–21 확률 ≈ 0 — 같은 출처
- **Walking on Ice(WOI)**: 주식은 양호하나 변동성이 장기평균보다 높음, 팩터 변동성 평균 장기 대비 +1.6%p, Momentum 예외. Crisis와 Steady State 사이 전후에 출현 → 취약성/버블 신호. 예: 1990년대 말 닷컴, GFC·COVID 직후 — 같은 출처
- 저자 단서: 모델은 **예측적이지 않음**, 국면은 데이터 유도라 사전 정의된 환경과 1:1 대응하지 않음 — 같은 출처

**Kritzman, Page, Turkington (FAJ 2012) [1차 초록]**
- "Regime Shifts: Implications for Dynamic Strategies": 시장 난류(turbulence)·인플레이션·경제성장 3계열에 Markov-switching 적용, 각 계열에서 "normal"과 "event" 2국면 식별. Event 국면은 평균적으로 투자 환경이 불리하고 변동성이 큼. 동적 배분이 정적 배분을 백테스트에서 상회(특히 큰 손실 회피 목적 투자자) — [IDEAS/RePEc](https://ideas.repec.org/a/taf/ufajxx/v68y2012i3p22-39.html), [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2012/regime-shifts-implications-for-dynamic-strategies-corrected)

**Kritzman & Li (FAJ 2010) "Skulls, Financial Turbulence, and Risk Management" [1차 초록 + 2차]**
- 1927년 두개골 분석 방법(Mahalanobis 거리)을 금융 난류에 적용; 극단 가격변동, 상관자산의 디커플링, 비상관자산의 수렴을 포착 — [IDEAS/RePEc](https://ideas.repec.org/a/taf/ufajxx/v66y2010i5p30-41.html), [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/skulls-financial-turbulence-and-risk-management)
- 공식: d_t = (1/n)(r_t − μ)ᵀ Σ⁻¹ (r_t − μ), n=자산 수, μ·Σ=과거 기준기간 평균·공분산 — [Portfolio Optimizer blog](https://portfoliooptimizer.io/blog/the-turbulence-index-measuring-financial-risk/)
- **지속성**: 초기 스파이크 후 수 주간 높게 유지(persistent) → 필터로 쓸 근거. 용도: G10 통화 캐리 전략 노출을 난류지수에 반비례로 축소 — 같은 출처
- 임계 처리: Kritzman & Li는 **5분위(quintile)** 접근 사용(구체 컷 미확인) — 같은 출처
- 블로그 저자 자체 검증(2009-04 – 2022-03, 7개 자산군, 논문 아님): 난류 조정 SPY/SHY 전략 평균노출 ~50%, Sharpe ~2.20 vs 보유 ~1, 최대 주간낙폭 ~6% vs ~32%; 극단 강세장(COVID 후 회복)에서 뒤처짐 — 같은 출처

**Bridgewater All Weather [2차 — Bridgewater 원문 미확보]**
- 4환경: 성장 상승/하락 × 인플레이션 상승/하락. 핵심은 수준이 아니라 **시장 기대 대비 서프라이즈**("inflation lower than markets expected" = falling inflation) — [SSGA, "The All Weather Portfolio: Built for Any Forecast"](https://www.ssga.com/us/en/institutional/insights/the-all-weather-portfolio-built-for-any-forecast)
- 근거 논리: 가격은 집단 기대를 반영하므로 큰 가격 변화는 서프라이즈에서만 발생 — [Evidence Investor](https://www.evidenceinvestor.com/post/the-all-weather-portfolio-explained)
- 자산 매핑: 성장↑ = 주식·원자재·회사채·EM채; 성장↓ = 채권; 인플레↑ = 원자재·물가연동채; 인플레↓ = 명목채·주식. "같은 위험을 가진 4개 포트폴리오를 보유"(risk parity, 예측 불필요) — [ETF.com](https://www.etf.com/sections/features/bridgewaters-all-weather-etf-gains-traction-can-it-deliver)
- 60/40 포트폴리오 위험의 약 90%가 주식에서 나옴 → 위험 균형 근거 — 같은 출처
- 대중적 비중(30/40/15/7.5/7.5)은 Tony Robbins 버전이지 Bridgewater 공식 아님 — [Evidence Investor](https://www.evidenceinvestor.com/post/the-all-weather-portfolio-explained)

**State Street Global Advisors — Market Regime Indicator(MRI) [1차, 구성 상세 비공개]**
- 입력: 주식·통화 내재변동성 + 채권 스프레드(주식·채권·통화 시장 심리 요인) — [SSGA MRI Q4 2023 PDF](https://www.ssga.com/library-content/assets/pdf/north-america/mas/2023/inst-pdf-market-regime-indicator-q4-2023.pdf), [SSGA MRI Q1 2024](https://ssga.com/us/en/intermediary/insights/market-regime-indicator-q1-2024)
- 척도 0–100%, 5단계: Euphoria(≈0%) – Low Risk Aversion – Normal(평균 근방) – High Risk Aversion – Crisis(≈100%). 높은 값 = 변동성 급증·위험자산 하락 — 같은 출처
- 용도: 전술적 자산배분(TAA) 입력, 액티브 ETF 모델포트폴리오에서 **변동성 예측 조정** → 배분에 반영 — [SSGA, Understanding our active ETF model portfolios](https://www.ssga.com/library-content/products/model-portfolio/us/understanding-our-active-etf-model-portfolios.pdf)

### Inferences
- KOSPI200 1분봉 시스템 관점에서 이식 가능한 것은 (b)(d) 계열이다: 다변량 Mahalanobis "난류"(예: 선물 수익률·베이시스·외인수급·VKOSPI 변화의 결합 이상도)와 2상태(정상/이벤트) 분류. GMM은 국면 라벨이 데이터마다 바뀌어 해석·사전등록이 어렵다(Two Sigma도 비예측적이라 명시).
- Two Sigma WOI("수익은 양호하나 변동성↑")는 장중 "추세는 있으나 변동성 과다" 상태의 매크로 대응물로 볼 수 있다 — 추론이며 근거 없음.

### Gaps
- Kritzman & Li의 정확한 난류 임계(75분위 등)는 원문 미확보로 미확인.
- Goldman Sachs·JPMorgan·BlackRock·MSCI·AQR의 명시적 국면 분류 체계는 이번 조사에서 1차 자료를 찾지 못함(조사 미착수에 가까움).
- Bridgewater 원문("The All Weather Story") 직접 확인 못함.

## 2. CTA·추세추종 실무: 추세 vs 횡보 국면, crisis alpha, 변동성 타게팅

### Takeaway
CTA 문헌은 국면을 "추세추종이 버는 환경"으로 사후 분해한다 — 자산 수익률 분위(quintile)로 나누면 최악·최선 구간 모두에서 성과가 좋은 **smile(롱 스트래들 유사)** 형태가 반복 관측된다. 변동성 타게팅은 위험자산에서만 Sharpe를 개선(레버리지 효과)하고 모든 자산에서 꼬리위험을 줄인다.

### Cited Findings
- Moskowitz, Ooi, Pedersen (JFE 2012) "Time Series Momentum": 58개 선물, 과거 12개월 초과수익이 미래수익의 양(+) 예측변수; 검토한 **모든** 계약에서 12개월 TSMOM 수익이 양; 약 1년 지속 후 장기에서 부분 반전; 분산 포트폴리오는 표준 팩터 노출이 작고 **"extreme markets"에서 가장 좋은 성과** — [SSRN 초록](https://papers.ssrn.com/abstract=2089463), [AQR 데이터셋](https://www.aqr.com/insights/datasets/time-series-momentum-original-paper-data)
  - 충돌: CBS 석사논문은 원 논문에서 3개월 룩백이 최적이라 주장 — 저자 초록의 12개월 강조와 상충, 원 표 확인 필요 — [CBS thesis](https://research-api.cbs.dk/ws/portalfiles/portal/60699508/815971_Masters_thesis_final_Magnus_Bojesen.pdf)
- Man Group, Hamill·Rattray·van Hemert (2016) "Trend Following: Equity and Bond Crisis Alpha": 1960–2015 월간, 채권·원자재·통화·주가지수. **국면 정의 = 롤링 3개월 창을 주식(또는 채권) 시장 수익률 5분위로 정렬**, 최악/최선 분위를 스트레스/랠리 국면으로 사용. 결과: 최악·최선 주식 환경 모두 강세("equity smile"), "bond smile"은 더 뚜렷. 수익은 양의 왜도(특히 빠른 전략), 롱 스트래들 유사. 주식·채권 포지션을 비양(≤0)으로 제한하면 위기 성과↑, 평균 성과↓ — [Man Group](https://www.man.com/insights/trend-following-equity-and-bond-crisis-alpha)
- 경로 위험: 닷컴 국면에서 추세추종은 초기 약 10% 손실, 이후 다시 약 20% 낙폭을 겪은 뒤 위기 수익 — [Man Group, Why patience matters](https://www.man.com/it/insights/why-patience-matters-during-market-stress)
- Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, van Hemert (JPM 2018, 45(1):14–33) "The Impact of Volatility Targeting": Sharpe 개선은 **위험자산(주식·크레딧)에만**, 원인은 레버리지 효과(수익률–변동성 음의 관계); 채권·통화·원자재는 무시할 수준. 모든 자산에서 극단수익 확률 감소. 변동성 스케일링은 손실 후 포지션 축소라 TSMOM 유사 틸트를 만든다 — [Quantpedia 초록](https://quantpedia.com/the-impact-of-volatility-targeting-on-equities-bonds-commodities-and-currencies), [Duke Scholars](https://scholars.duke.edu/publication/1370354)
  - 방법: 지수감쇠 가중 실현 일간변동성으로 예측(여러 반감기 테스트) — [CXO Advisory](https://www.cxoadvisory.com/equity-premium/benefits-of-volatility-targeting-across-asset-classes)
  - 미국 주식 vol-of-vol 4.6% → 1.8%(10% 타깃, 1926–2017 일간, 60+ 자산) — [Bluerating 요약, 2차](https://www.bluerating.com/mercati/141117/volatility-targeting-improves-risk-adjusted-returns)

### Inferences
- 장중 시스템으로 옮기면, "추세 국면"을 사후 수익률 분위로 정의하는 Man 방식은 라벨 정의로 유용하나 실시간 분류기에는 직접 쓸 수 없다(미래 정보). 실시간 대응물은 추세강도(효율비·Hurst 등)와 실현변동성의 결합이다.
- 변동성 타게팅이 위험자산(지수선물)에서 유효하다는 결과는 KOSPI200 선물 사이징에 지수감쇠 실현변동성 기반 스케일러를 쓸 근거가 된다(추론).

### Gaps
- CTA 업계의 "추세강도" 지표 정의(예: 표준화 이동평균 차이, 효율비)의 기관 공식 문서를 찾지 못함.
- Man 논문의 분위별 수치는 그림에만 있어 미확인.

## 3. Auction Market Theory / Market Profile Day Type (Steidlmayer·Dalton)

### Takeaway
Day type은 **Initial Balance(IB, 첫 1시간 = 보통 30분 2기간) 대비 범위 확장(range extension)의 방향·크기와 종가 위치**로 정의된다. 정량 임계는 저자·플랫폼마다 비표준이며, 원전(Dalton)의 정확한 수치는 이번 조사에서 1차 확인하지 못했다. ES 빈도 통계는 포럼 기반(Brewer 2013)으로 대략 Normal Variation 40–54%, Neutral ~25%, Trend 약 16%(주 1회 수준)다.

### Cited Findings
**기본 용어**
- TPO = 시간 구간마다 가격이 지나간 레벨에 찍는 블록(시간 기준, 거래량 아님); POC = TPO가 가장 많은 가격행 — [eSignal](https://kb.esignal.com/hc/en-us/articles/6362181429403-eSignal-Market-Profile), [TradingView TPO](https://www.tradingview.com/support/solutions/43000713306-time-price-opportunity-tpo-indicator/)
- IB = 첫 1시간의 범위·위치([Wikipedia](https://en.wikipedia.org/wiki/Market_profile)) 또는 첫 2기간([CQG](https://help.cqg.com/cqgic/25/Documents/marketprofilemp.htm)); 30분 기간이면 동일
- Value Area = 세션 활동의 약 70%(≈1σ) 구간; POC에서 바깥으로 확장해 계산 — [eSignal](https://kb.esignal.com/hc/en-us/articles/6362181429403-eSignal-Market-Profile), [CQG](https://help.cqg.com/cqgic/25/Documents/marketprofilemp.htm)
- 지수선물 관례: IB는 정규 현물 개장 기준; IB 밖에서 수용된 가격 = range extension = 장기 시간프레임 참가자 활동 신호; 최종 범위/IB 비율로 day type 분류 — [LuxAlgo, Day-type taxonomy](https://www.luxalgo.com/library/concept/day-type-taxonomy/)

**Day Type 정의 [2차 — Dalton 원전 미확인]**
| 유형 | 균형/불균형 | 정의 | 출처 |
|---|---|---|---|
| Non-Trend | 균형 | 저거래량·좁은 범위, IB 안에서 진동, 범위 확장 없음 | [MarketCalls](https://www.marketcalls.in/market-profile/market-profile-different-types-of-profile-days.html) |
| Normal | 균형 | 넓은 IB가 세션 내내 유지, IB 안 양방향 회전, 확장 없음(또는 거의 없음) | MarketCalls; [LuxAlgo](https://www.luxalgo.com/library/concept/day-type-taxonomy/) |
| Normal Variation | 불균형(한쪽) | IB는 Normal보다 작고 Trend보다 큼; 한쪽으로 확장, 범위가 IB의 약 2배("range extension > 2× initial range"); 11–12시 이후 장기 참가자 확장 | MarketCalls; LuxAlgo |
| Trend | 불균형 | 좁은 IB → 한 방향으로 지속 확장, 회전 최소, 극단 근처 종가, 세로로 긴 프로파일 | MarketCalls; LuxAlgo |
| Double Distribution Trend | 불균형 | 작은 IB, 첫 회전은 IB에서, 두 번째 회전은 반대편 영역에서, 두 분포가 single print로 분리 | MarketCalls |
| Neutral Center | 균형 | IB가 Normal보다 작음, **양쪽** IB 돌파, 중앙 근처 종가(미해결 균형) | MarketCalls; LuxAlgo |
| Neutral Extreme | — | 양쪽 IB 돌파 후 한쪽 극단에서 종가, 이벤트일에 흔함 | MarketCalls |
| P-shape | — | 숏커버링; 초기범위에 single print, 하단에서 개장 후 상단에서 회전 | MarketCalls |
| b-shape | — | 롱 청산; 상단에서 개장 후 하단에서 회전 | MarketCalls |

- 경고: 임계는 표준화되지 않음; 24시간 시장은 IB 앵커 세션 선택에 의존 — [LuxAlgo](https://www.luxalgo.com/library/concept/day-type-taxonomy/)
- "진짜 Normal day는 생각보다 드물고, 트레이더가 균형일을 말할 때 실은 Normal Variation을 뜻하는 경우가 많다" — LuxAlgo/NexusFi 요약(2차)
- 충돌: MarketCalls는 Normal day가 "시장 전반 약 50–60%"라 주장(출처 미제시, 저자 경험) — [MarketCalls](https://www.marketcalls.in/market-profile/market-profile-different-types-of-profile-days.html); 반면 다른 출처는 Normal이 드물다고 함 → Normal/Normal Variation 정의 혼용 가능성

**Open Type (Dalton) [2차]**
- **Open-Drive**: 첫 체결부터 한 방향으로 강하게 이동, 시가를 되돌아 통과하지 않음; 현물 개장 첫 30분 지속적 방향성 — [LuxAlgo, Open types](https://www.luxalgo.com/library/concept/open-types/)
- **Open-Test-Drive**: 시가 한쪽(또는 인근 기준가, 예 전일 고/저)을 시험해 거래 없음 확인 후 반대 방향으로 이탈 — 같은 출처, [NexusFi thread](https://nexusfi.com/showthread.php?p=636636)
- **Open-Rejection-Reverse**: 초기 이동이 거부되고 시가를 되통과해 반대로 강해짐, 보통 첫 기간(30분) 내; Open-Test-Drive와 차이는 가격이 IB 안으로 되돌아온다는 점 — [Crowstack](https://crowstack.substack.com/p/five-easy-tapes-open-rejection-reverse)
- **Open-Auction**: 확신 없이 시가 주변 회전; 전일 Value Area 안/밖으로 세분; VA 안 Open-Auction은 균형·회전 세션 시사 — [LuxAlgo](https://www.luxalgo.com/library/concept/open-types/), NexusFi
- 해석 순서(관례): open type이 가장 이른 신호(장기 참가자 확신도), IB 형성 후 day type 후보를 좁히고 종가로 확정.

**ES 빈도 통계 [포럼/2차 — 방법론 일부 공개]**
- Shane Brewer(2013, ES 2년 장중데이터): Normal Variation = IB ≥ 5pt 이고 IB 한쪽만 돌파; Trend = RTH 범위 > 21pt(평균+1σ) 이고 고/저 25% 이내 종가(25%는 임의 선택). 빈도 약 **Normal Variation 54% / Neutral계 25% / Trend 16%**(주 1회 수준) — NexusFi 포럼 재인용 [NexusFi day types](https://nexusfi.com/a/market-structure/market-profile-day-types)(403으로 본문 직접 확인 불가, 검색 요약 기반)
- 같은 포스트: 2025년까지 3,000+일 신규 데이터에서 극단 꼬리 종가 약 26% — 같은 출처(미검증)
- 다른 기사: Normal Variation 약 40%, Trend day 월 3–4회(ES); ES 세션 50–55%가 균형일 — NexusFi 계열 기사(2차, 정의 상이로 직접 비교 불가)

### Inferences
- 1분봉 KOSPI200 시스템은 IB(09:00–10:00, KRX 정규장 기준)·IB 확장 배수·종가 위치(분위)·양쪽 돌파 여부의 4변수만으로 위 7–9유형을 결정론적으로 라벨링할 수 있다. Brewer처럼 **임계를 상품별 분포(평균+1σ 등)로 재보정**해야 하며 ES pt 값은 이식 불가.
- 실시간 분류는 종가 정보가 필요해 사후 라벨이 된다; 장중 실시간에는 "open type(첫 30분) → IB 폭 상대분위 → 확장 발생 시각"의 순차 확률 갱신 구조가 자연스럽다(추론).

### Gaps
- Dalton/Steidlmayer 원전의 정확한 정량 기준·빈도는 미확인(원서 필요). CME Group 공식 교육자료 미도달.
- Open type별 빈도·후속 day type 조건부 확률의 신뢰할 만한 통계 미발견.

## 4. 기타 실무 장중 분류 (Crabel, Raschke, Williams, Wyckoff, Gap)

### Takeaway
Crabel은 **범위 수축→확장 주기**(NR4/NR7)와 opening range breakout을 결합했고, Raschke는 매매 전 "추세일 vs 평균회귀일"을 먼저 판정하는 것을 원칙으로 삼는다. Wyckoff는 축적·마크업·분배·마크다운 4단계 + 거래범위 내부 Phase A–E. Gap fill 통계는 출처마다 정의(전일 종가 터치·반갭·기간)가 달라 신뢰도가 낮다.

### Cited Findings
- Crabel 저서 구성 5부: opening range breakout, 단기 가격패턴, 확장·수축 패턴, 패턴×확장수축 결합, 봉 내 시가·종가 — [소매 리스팅, 2차](https://rexcoursee.it.com/product/toby-crabel-day-trading-with-short-term-price-patterns-and-opening-range-breakout/)
- NR7 = 당일 범위가 직전 6일 각각보다 좁음; NR4는 4봉 비교로 덜 엄격; 플래그는 이진이며 정상 변동성 대비 얼마나 좁은지 무시; 방향 중립이라 양방향 브래킷 — [LuxAlgo NR4/NR7](https://www.luxalgo.com/library/concept/nr4-nr7-narrow-range-bars.md)
- ORB 집행: 시가 ± Stretch 에 매수/매도 스톱; Stretch = 평균 "noise"(시가와 더 가까운 극단 간 거리) × 배수 — [Oxford Strat, narrow range](https://oxfordstrat.com/trading-strategies/narrow-range/)
- Crabel은 2봉 NR 아이디어를 Wyckoff의 협폭·저거래량 지점(마크업/마크다운 직전)에 귀속(원서 p.167 인용) — 같은 출처
- Raschke: 추세일 = 일간 범위 확장 + 시가·종가가 반대 극단 근처; 매매 전 그날을 추세형/평균회귀형으로 분류(전날 밤 가능) — [OptionsTradingIQ, 2차](https://optionstradingiq.com/linda-raschke-rules-for-trading/)
- 추세일 특징(2차): 첫 30분이 하루 범위의 10% 미만인 경우가 많고 모멘텀이 이후 형성; 범위일은 중앙 근처 종가 — [DamnPropFirms](https://damnpropfirms.com/trading-guides/range-days-vs-trend-days-on-es-how-to-identify-them/)
- Wyckoff 4단계: Accumulation → Markup → Distribution → Markdown — [Bookmap](https://bookmap.com/en/blog/wyckoff-trading-strategy-understanding-market-cycles); 분배 Phase: A(선행 공급·매수 클라이맥스로 상승 정지) – B(composite operator가 2차 테스트에서 매도) – C(UTAD 최종 상단 탐색) – D(지속 하락·낮아지는 고점, LPSY) – E(마크다운) — [StockCharts, Context is King](https://articles.stockcharts.com/article/articles-wyckoff-2015-09-context-is-king/), [LuxAlgo Wyckoff distribution](https://www.luxalgo.com/library/concept/wyckoff-distribution-schematic/)
- Gap fill(ES): fill = 전일 16:00 ET 종가 터치, 반갭 별도; 5–6pt 미만 갭이 최상 결과(2009) — [Slope of Hope/TradeFlightPlan](https://slopeofhope.com/?p=7636); 최근 6개월 갭업 59%·갭다운 66% fill, 전체 fill은 11개 종목 대부분에서 일관성 없음/손실 — [Edgeful](https://www.edgeful.com/blog/posts/trading-gap-fills), [Edgeful half vs full](https://www.edgeful.com/blog/posts/half-gaps-vs-full-gaps); "82%가 정규장 첫 2.5시간 내 fill(2020–2025)" 단일 미검증 주장 — [Don's Trading Desk](https://tradingdesk.beehiiv.com/p/82-of-opening-gaps-fill-within-2-5-hours); 갭 크기 버킷(2pt 미만 >90% → 30pt 초과 <20%) 데이터 출처 미제시 — [NexusFi gap trading](https://nexusfi.com/a/strategies/gap-trading-futures)

### Inferences
- Crabel NR7은 이진 플래그 대신 "범위/ATR 분위"로 연속화하면 국면 피처로 쓰기 쉽다(LuxAlgo 비판 반영). Raschke의 "전날 밤 분류"는 전일 NR·전일 종가위치 등 사전 정보 기반 day-type prior를 의미한다.
- Gap 크기는 ES 절대 pt가 아니라 ATR 대비로 정규화해야 한다(TradingView 지표도 ATR 대비 분할 — 아래 Gaps 참조).

### Gaps
- Crabel 원서의 확장 확률·승률 표, Larry Williams의 day-type 정의(예: Oops, 변동성 돌파)는 이번 조사에서 1차 자료 미확보.
- Gap-and-go vs gap-fill의 엄밀한 학술 통계 미발견. ATR 대비 갭 fill 확률(2014–2024 ES 2,646일) 지표의 실수치는 미공개 — [TradingView 지표](https://www.tradingview.com/script/32pGGSWx-Gap-Fill-Probability-Statistics-ES-NQ)

## 5. 변동성 국면 실무: VIX 수준·기간구조, 실현 vs 내재, 국면→전략 매핑

### Takeaway
VIX/VIX3M 비율 > 1.0(역전, backwardation) = 단기 스트레스, < 1.0(contango) = 평온 기본상태; 2010년 이후 역전은 거래일의 약 8%에 불과하고 중앙 지속 약 2세션으로 짧다. 데스크 관행은 "contango = 숏볼/캐리·평균회귀, backwardation = 헤지·축소·추세/위기알파"로 요약되나 이를 뒷받침하는 엄밀한 비용차감 백테스트는 찾지 못했다.

### Cited Findings
- VIX/VIX3M > 1.0 = backwardation(단기 스트레스), 그 외 contango(평온); 일부는 < 0.90을 강한 contango로 구분 — [thetrading.tools](https://www.thetrading.tools/vix-term-structure), [FlashAlpha](https://flashalpha.com/concepts/vix-term-structure)
- 빈도: 2009-12-31 이후 contango 세션 92.3%, 역전 에피소드 103회, 역전 중앙 지속 약 2세션; 다른 출처는 2010년 이후 8% — 벤더 트래커(2차) [thetrading.tools](https://www.thetrading.tools/concepts/backwardation); FlashAlpha는 VIX9D–VIX6M 전체 곡선 기준 약 85% contango(측정 방식 상이) — [FlashAlpha](https://flashalpha.com/concepts/vix-term-structure)
- 전략 함의: contango에서 숏 VXX가 롤수익 획득, backwardation에서 급속 손실 → 역전은 단독 매매보다 헤지/스트레스 신호로 사용 — [thetrading.tools](https://www.thetrading.tools/concepts/contango)
- SSGA MRI는 내재변동성(주식·통화)을 핵심 입력으로 위험회피 국면을 산출해 변동성 예측을 조정 — [SSGA](https://ssga.com/us/en/intermediary/insights/market-regime-indicator-q1-2024)
- Two Sigma Crisis 국면에서 Trend Following 큰 양(+)수익, Man 연구의 최악 주식 분위 강세 → "고변동/위기 = 추세추종 유리"가 매크로 수준에서 일관 — [Two Sigma](https://www.twosigma.com/articles/a-machine-learning-approach-to-regime-modeling/), [Man Group](https://www.man.com/insights/trend-following-equity-and-bond-crisis-alpha)

### Inferences
- KOSPI200 대응: VKOSPI 수준 분위 + (가능하면) VKOSPI 근/차월 기간구조 또는 옵션 ATM IV 기간구조로 "평온/스트레스" 2상태를 만들 수 있다. 역전이 드물고 짧다는 ES 증거는, 스트레스 국면 표본이 매우 희소할 것임을 시사 → 사전등록 min_samples 설계 시 고려(추론).
- 실현변동성/내재변동성 비율(RV/IV) 국면은 이번 조사에서 1차 실무 정의를 찾지 못했다.

### Gaps
- RV vs IV 국면의 기관 공식 정의·임계, VIX 절대수준 국면(예: <15, 15–25, >30) 기관 문서 미확보.
- 국면→전략 매핑(추세/평균회귀/관망)의 비용 차감 실증 연구는 장중 단위로 찾지 못함.

## 6. Day type 효과성·빈도에 대한 공개 증거 종합

### Takeaway
장중 day type의 **빈도** 통계는 존재하나(ES: Trend ≈ 16%, Normal Variation 40–54%) 거의 전부 포럼·벤더 출처이며 정의가 달라 상호 비교 불가다. day type을 **사전 예측해 매매 성과를 낸다**는 동료심사 증거는 찾지 못했다. 매크로 수준(TSMOM, 변동성 타게팅, 난류 필터)은 학술 증거가 상대적으로 탄탄하다.

### Cited Findings
- Brewer(2013) ES: Trend 16% / Neutral 25% / Normal Variation 54%, Trend = 범위>평균+1σ & 극단 25% 이내 종가 — [NexusFi](https://nexusfi.com/a/market-structure/market-profile-day-types)(포럼 재인용)
- 대안 수치: Normal Variation 약 40%, Trend 월 3–4회; 균형일 50–55% — NexusFi 계열 기사(2차)
- Normal day 50–60% 주장(MarketCalls, 무출처) vs "Normal은 드물다"(LuxAlgo/NexusFi) — [MarketCalls](https://www.marketcalls.in/market-profile/market-profile-different-types-of-profile-days.html), [LuxAlgo](https://www.luxalgo.com/library/concept/day-type-taxonomy/)
- 매크로 증거: TSMOM 58개 선물 전부 12개월 양(+) 수익 — [SSRN](https://papers.ssrn.com/abstract=2089463); 변동성 타게팅 위험자산 Sharpe 개선 — [Quantpedia](https://quantpedia.com/the-impact-of-volatility-targeting-on-equities-bonds-commodities-and-currencies); 난류 필터 노출 조절로 성과 개선 — [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/skulls-financial-turbulence-and-risk-management)

### Inferences
- 실무 권고(추론): ES 빈도는 기대치 참고값일 뿐이며, KOSPI200 자체 데이터로 동일 정의(IB 폭 분위, 범위/IB 배수, 종가위치, 양측 돌파)를 고정·사전등록한 뒤 빈도와 다음날/잔여세션 조건부 수익을 재산출하는 것이 유일하게 신뢰 가능한 경로다. NexusFi 답변도 "자체 데이터 재계산"을 권고.
- Trend day가 주 1회(~16–20%) 수준이라면, "추세 국면에서만 진입" 규칙은 표본이 매우 빠르게 줄어든다 — 사전 확률이 낮은 국면을 게이트로 쓸 때 표본 적립 ETA를 먼저 계산할 것.

### Gaps
- 동료심사 학술지(JPM, JAI 등)의 Market Profile day type 실증 연구는 발견하지 못함.
- KOSPI200 선물 대상 day type 빈도 연구는 탐색하지 못함.
