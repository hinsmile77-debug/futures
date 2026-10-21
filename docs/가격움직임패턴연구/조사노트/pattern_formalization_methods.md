# 가격경로 패턴 정형화·다음 패턴 예측 방법론 (Pattern formalization & next-pattern prediction)

> 범위: (a) 분봉/일봉 경로를 유한·해석가능한 패턴 어휘로 만드는 기법, (b) 현재 패턴+외생 수급 피처로 다음 구간/다음 날 패턴을 예측하는 기법, (c) 거짓 발견을 피하는 검증 방법론. 표본 제약: 1분봉 1–2년(약 300–500 거래일).
> 조사일 2026-10-21. 대부분 초록·서지·2차 요약 기반이며 원문 전문을 직접 확인한 것은 Wasserstein k-means(ar5iv HTML) 하나뿐이다 — 각 항목에 명시.

## (a) 분봉·일봉 경로를 이산 패턴 어휘로 바꾸는 기법 — 형태 기반 군집, 기호화, 모티프, 시그니처, 분포 군집, 군집 수 결정

### Takeaway
이 작업에 맞는 선택지는 다섯 계열이다. ① 형태 거리(k-Shape/DTW) 위 분할 군집, ② 기호화(SAX·서수 패턴), ③ 반복 하위구간(matrix profile 모티프), ④ 순서를 보존하는 요약(path signature), ⑤ 수익률 분포 군집(Wasserstein k-means). 300–500일 규모에서 k-Shape와 Wasserstein k-means는 계산상 문제가 없다. 다만 "하루 = 관측 1개"로 군집하면 표본이 수백 개뿐이라 k를 작게(대략 3–6) 잡고 안정성 검증을 해야 한다. 이 수치는 추론이며 문헌에서 확인한 값이 아니다.

### Cited Findings
**서베이**
- Aghabozorgi, Shirkhorshidi & Wah (2015), "Time-series clustering – A decade review", *Information Systems* 53:16–38, DOI 10.1016/j.is.2015.04.007. 시계열 군집의 네 구성요소(표현 representation · 거리 distance measure · 군집 알고리즘 · 평가 evaluation measure)를 축으로 정리한다. 스냅샷 시점 인용 875회. — [Scinapse](https://www.scinapse.io/papers/1894414046); [전문 PDF 사본](https://wiki.smu.edu.sg/18191isss608g1/img_auth.php/f/fd/Time_Series_Clustering_A_Decade_Review.pdf)
- 후속 서베이 "Bridging the Gap: A Decade Review of Time-Series Clustering Methods" (arXiv 2412.20582, 2024). 원문 미확인. — [arXiv](https://arxiv.org/abs/2412.20582v1)

**k-Shape (형태 기반 분할 군집)**
- Paparrizos & Gravano, "k-Shape: Efficient and Accurate Clustering of Time Series", SIGMOD 2015. 저널 확장판은 "Fast and Accurate Time-Series Clustering", *TODS* 2017.
  - 거리: 정규화 교차상관(shape-based distance)으로, 위상 이동(shift)에 불변이다.
  - 중심: 이 거리에 맞춘 centroid 계산을 별도로 유도했다.
  - 성능: 분할·계층·스펙트럴 방법 중 "확장 가능한 모든 방법보다 정확"했다. 비슷한 정확도를 낸 유일한 비확장 조합은 거리 튜닝이 필요하고 "두 자릿수(100배) 느리다".
  - DOI는 출처마다 2723372.2723779와 2723372.2737793으로 엇갈려 미해결이다.
  - 구현: Python `kshape`, `aeon.clustering.TimeSeriesKShape`. — [TODS 2017 PDF](https://www.cs.columbia.edu/~gravano/Papers/2017/tods17.pdf); [SIGMOD Record 2016](https://www.cs.columbia.edu/~gravano/Papers/2016/sigmod-record16.pdf); [aeon 문서](https://www.aeon-toolkit.org/en/v1.4.0/api_reference/auto_generated/aeon.clustering.TimeSeriesKShape.html); [GitHub kshape](https://github.com/adam-dziedzic/kshape)

**장중 금융시계열 군집 (직접 사례)**
- Shi, Li, Du & Dai (2021), "Clustering framework based on multi-scale analysis of intraday financial time series", *Physica A* 567:125728.
  - 다중 스케일 유사도와 군집 품질 지표를 묶은 프레임워크를 제안하고 여러 군집 알고리즘으로 시험했다.
  - 데이터는 CSI 300 · S&P 500 · Nikkei 225이며, 장중 시계열의 "서로 다른 클래스를 명확히 구분"했다고 보고한다.
  - 초록만 확인했다(구체 기법·수치 미확인). — [IDEAS/RePEc](https://ideas.repec.org/a/eee/phsmap/v567y2021ics0378437120310268.html)
- 함수형 데이터 분석(FDA) 곡선 군집: 곡선 집합을 소수 군집으로 나눠 관측공간을 축소하며, 곡선 자체나 **도함수**에도 적용할 수 있다. 예시는 eBay 경매이고 금융 장중곡선은 아니다. — [Jank & Shmueli, arXiv math/0609173](https://arxiv.org/pdf/math/0609173)
- 전력가격 "일 유형" 군집(k-means·fuzzy c-means): 평일/주말·공휴일이 주된 분리였고 같은 계절의 날끼리 유사도가 컸다. 일 유형 군집이 달력 효과를 먼저 잡아낸다는 사례다. — [Martínez Álvarez et al., idUS](https://idus.us.es/handle/11441/39731)

**SAX (기호 집계 근사)**
- Lin, Keogh, Lonardi & Chiu (2003), "A Symbolic Representation of Time Series, with Implications for Streaming Algorithms".
  - 절차: z-정규화 → PAA(구간 평균) → 가우시안 등확률 분기점으로 기호 매핑.
  - "유클리드 거리의 하한(lower bound)을 보장하는 최초의 기호 표현"이다. MINDIST가 PAA 거리의 하한성을 물려받아 false dismissal이 없다. — [원논문 PDF](https://www.cs.ucr.edu/~eamonn/SAX.pdf); [Keogh/Lin 강의](https://www.cs.unm.edu/~mueen/Teaching/CS591/Lectures/SAX_representation.pdf); [SAX 변형 논문 arXiv 1301.5871](https://arxiv.org/pdf/1301.5871); [R TSclust MINDIST](https://search.r-project.org/CRAN/refmans/TSclust/html/SAX.html)

**서수 패턴 (Bandt–Pompe) — 이산 어휘 + 예측가능성 진단 겸용**
- Zunino et al. (2009), "Forbidden patterns, permutation entropy and stock market inefficiency", *Physica A* 388(14):2854–2864.
  - 길이 D 창의 순위 순서를 패턴(기호)으로 삼는다(D! 종류).
  - 비효율성은 금지 패턴 수와 **양의 상관**, 정규화 순열엔트로피와 **음의 상관**이다. 이 두 도구로 시장 발전 단계를 판별할 수 있다고 본다.
  - 흔한 설정은 일간 수익률 D=5(한 주). — [IDEAS](https://ideas.repec.org/a/eee/phsmap/v388y2009i14p2854-2864.html); [후속 해설 arXiv 1801.07941](https://arxiv.org/pdf/1801.07941)
- 금지 패턴 "개수"는 노이즈에 매우 민감하다(비존재는 너무 엄격한 기준). 그래서 후속 연구는 순열엔트로피 분포를 선호한다. — [arXiv 1801.07941](https://arxiv.org/pdf/1801.07941)
- 폴란드 WIG 적용(Graff & Kaczkowska 2013): 선진도 신흥도 아닌 "하이브리드" 시장으로 분류됐다. — [Gdańsk Tech](https://pub.pg.edu.pl/en/download/125894-the-efficiency-of-polish-stock-market-ordinal-patterns-approach)

**Matrix Profile (모티프·디스코드·세그먼트)**
- Yeh, Zhu, Ulanova, Begum, Ding, Dau, Silva, Mueen & Keogh (2016), "Matrix Profile I: All Pairs Similarity Joins for Time Series…", IEEE ICDM 2016, pp.1317–1322, DOI 10.1109/ICDM.2016.0179.
  - 하위구간 self-join을 정확하고 확장 가능하게 푼다. 창 길이 외 파라미터가 없다.
  - 각 하위구간의 최근접 거리와 위치를 저장한다. 값이 가장 낮은 항목이 모티프, 가장 높은 항목이 디스코드다.
  - 다변량에도 적용된다. 저널판은 DMKD 32(1):83–123 (2018). — [DMKD 저널판 PDF](https://www.cs.ucr.edu/~eamonn/MP_journal.pdf); [arXiv 1811.03064](https://ar5iv.arxiv.org/html/1811.03064); [R matrixProfile](https://r-packages.io/packages/matrixProfile)

**Path signature (경로 서명)**
- "Extracting information from the signature of a financial data stream" (arXiv 1307.7244; Gyurkó, Lyons, Kontkowski, Field 2014로 인용됨).
  - 소수의 서명 계수만으로 금융 데이터 스트림을 분류·예측할 수 있다고 주장한다.
  - 실험: WTI 원유 시장 행태, FTSE 100 선물의 모주문 충격.
  - 저자 목록은 검색 결과로 직접 확인하지 못했다. 다른 논문이 "Gyurkó et al. (2014), Lasso+서명 피처"로 인용한다. — [arXiv 1307.7244](https://arxiv.org/abs/1307.7244); [arXiv 1911.13211](https://arxiv.org/pdf/1911.13211.pdf)
- 여러 데이터셋에서 **lead-lag 임베딩**이 가장 좋았다. — [arXiv 1911.13211](https://arxiv.org/pdf/1911.13211.pdf)
- 입문서: Sturm (2025). 통상 통계량은 사건 순서를 무시하지만 서명은 순서를 보존한다. — [arXiv 2506.01815](https://arxiv.org/pdf/2506.01815)
- 분봉 선물 페어트레이딩에 서명 지표를 쓴 사례가 있다. — [arXiv 2505.05332](https://arxiv.org/html/2505.05332v1)

**Wasserstein k-means (분포 기반 국면 군집) — 원문 HTML 확인**
- Horvath, Issa & Muguruza, "Clustering Market Regimes using the Wasserstein Distance", arXiv 2110.11848 (2021), *J. Computational Finance* 28(1), 2024.
  - 각 수익률 창을 경험분포로 보고 p-Wasserstein 거리로 k-means를 돌린다. 모형 가정이 없다.
  - 합성 데이터: 모멘트 기반 k-means는 비가우시안에서 열등했고, HMM은 국면을 분리하지 못했다.
  - 실데이터: SPY **1시간** 로그수익률, 2005-01-03–2020-12-31. 창 h1=35, 오프셋 h2=28(7칸씩 이동, 대략 주 단위). 각 수익률은 최대 5개 창에 중복 소속된다. **k=2**(강세/약세).
  - 군집 자기유사도(MMD, 낮을수록 좋음): WK-means 0.0395 / 0.2304 vs 모멘트 k-means 0.0631 / 1.1961.
  - 그런데 전통 지표는 반대로 나왔다. Davies-Bouldin WK 1.1075 vs MK 0.8604, 평균 실루엣 WK 0.5093 vs MK 0.8008. 저자도 이 지표들이 방법 간 비교에 부적합하다고 경고한다.
  - 합성 실험 정확도는 50회 시뮬레이션 평균이다. — [ar5iv 전문](https://ar5iv.arxiv.org/html/2110.11848); [arXiv abs](https://arxiv.org/abs/2110.11848v1); [SSRN](https://papers.ssrn.com/abstract=3947905); [J. Comp. Finance](https://www.risk.net/journal-of-computational-finance/volume-28-number-1-june-2024)

**군집 수 k 결정**
- Gap statistic: Tibshirani, Walther & Hastie (2001), *JRSS-B* 63:411–423.
  - 군집 내 분산 감소를 참조 귀무분포와 비교하며, 어떤 군집 알고리즘에도 쓸 수 있다.
  - 원래 규칙은 Gap(k) ≥ Gap(k+1) − s(k+1)을 만족하는 최소 k다. 모든 표준편차가 차분보다 크면 k=1을 고른다.
  - R `cluster::clusGap`의 기본 규칙("firstSEmax", Maechler 2012)은 원 제안과 다르다. — [IDEAS](https://ideas.repec.org/a/bla/jorssb/v63y2001i2p411-423.html); [clusGap 문서](https://rdrr.io/cran/cluster/man/clusGap.html)

### Inferences
- **표본 규모(300–500일)**: "하루 경로 1개 = 관측 1개"면 N≈300–500이다. k-Shape·DTW-k-medoids의 O(N²) 거리행렬도 수십만 쌍이라 문제없다. 병목은 계산이 아니라 **군집당 표본 수**다. k=6이면 군집당 평균 50–80일이고, 그 위에 6×6 전이행렬을 올리면 셀당 평균 약 8–14 전이에 그친다. 다음 날 패턴 예측까지 가려면 k를 **3–5**로 억제하는 편이 합리적이다(추론).
- **창 단위 어휘(장중 세그먼트)**: 장중을 30분 세그먼트로 쪼개면 하루 약 13개, 500일이면 약 6,500 관측이다. 세그먼트 단위 어휘와 전이는 표본 면에서 훨씬 유리하다. 다만 같은 날 세그먼트끼리 상관이 있어 유효 표본은 이보다 작다(추론).
- **평가지표 함정**: Wasserstein 논문에서 MMD는 WK 우위, 실루엣·DB는 MK 우위로 반대 결론이 나왔다. **거리 정의가 다른 방법끼리 실루엣으로 비교하면 안 된다.** 고정된 공통 기준(예: 이후 패턴의 예측력, 부트스트랩 안정성)으로 비교해야 한다.
- **k-Shape vs DTW**: k-Shape는 z-정규화+교차상관이라 **진폭(변동폭) 정보를 버린다.** "추세일 vs 횡보일"처럼 진폭이 핵심인 분류라면 형태 군집과 별도로 진폭 축(범위/ATR, 실현변동성)을 함께 써야 한다(추론, 방법 정의에서 도출).
- **서수 패턴**은 어휘(D! 기호)와 예측가능성 진단(순열엔트로피)을 한 번에 준다. 1분봉에서 D=3–5 정도면 표본이 충분하다(추론).

### Gaps
- DTW + k-medoids를 장중 선물 경로에 적용하고 수치까지 보고한 1차 문헌은 찾지 못했다.
- FDA로 금융 **장중 곡선**을 군집한 1차 문헌(예: 장중 변동성 곡선 함수형 군집)은 이번 검색에서 확보하지 못했다.
- 군집 안정성 기반 k 선택(Ben-Hur et al. 2002 등)은 검색 결과가 없어 미인용이다.
- k-Shape 원논문의 데이터셋 수·정확도 수치는 미확인(원문 미열람)이다.
- Shi et al. (2021)의 다중 스케일 기법과 품질지수 세부 내용은 미확인이다(유료).

## (b) 규칙 기반 분류(Market Profile 일 유형) vs 학습 기반 분류 — 하이브리드 비교 문헌

### Takeaway
Market Profile 일 유형(Steidlmayer·Dalton)은 정의가 저자마다 다르다. 빈도 주장("정상일 50–60%")도 근거가 없다. 규칙 분류와 비지도 군집을 같은 데이터에서 직접 비교한 학술 문헌은 찾지 못했다.

### Cited Findings
- 일 유형은 초기 균형(IB, 첫 60분 범위) 대비 확장 정도와 종가 위치로 분류한다: Trend / Normal / Normal Variation / Neutral / Neutral Extreme. — [Linnsoft DayTypes](https://www.linnsoft.com/techind/day-types-rtx); [LuxAlgo Day-type Taxonomy](https://www.luxalgo.com/library/concept/day-type-taxonomy/)
- "Normal day가 가장 흔해 약 50–60%"라는 주장이 있으나 데이터·방법이 제시되지 않았다(미검증). — [marketcalls](https://www.marketcalls.in/market-profile/market-profile-different-types-of-profile-days.html)
- 분류는 **종가가 나와야 확정**되고, 확장 배수 같은 기계적 정의가 저자마다 다르다. — [LuxAlgo](https://www.luxalgo.com/library/concept/day-type-taxonomy/)
- 개인 트레이더의 ES 규칙 예: Normal = IB 양쪽 미돌파 & IB ≥ 5pt. Trend = RTH 범위 > 21pt & 종가가 RTH 범위 상·하단 25% 이내. 임계는 본인 연구로 정했고 표준이 아니다. — [NexusFi](https://nexusfi.com/a/market-structure/market-profile-day-types)

### Inferences
- 규칙 분류는 **해석가능성과 안정적 정의**가 장점이다. 반면 정의가 종가에 의존해 **장중 실시간 판별이 불가능**하다. 다음 날 예측의 "타깃 어휘"로는 쓸 수 있지만, 장중 진행 중 패턴 판정에는 부분 경로로 판별하는 별도 분류기가 필요하다(추론).
- 현실적인 하이브리드는 두 단계다(추론, 문헌 근거 없음).
  1. 규칙(IB 확장·종가 위치·범위/ATR)으로 소수 유형을 정의한다.
  2. 각 유형 안에서 k-Shape/SAX로 하위 형태를 나누거나, 비지도 군집 결과를 규칙 유형과 교차표(ARI/NMI)로 대조해 "규칙이 놓친 군집"을 찾는다.
- 지수 수준이 바뀌면 절대 pt 임계(예: "21pt")가 드리프트한다. 이 프로젝트의 ATR_MIN_ENTRY 사례와 같은 유형이다. 범위는 ATR이나 bp로 상대화해야 한다(추론).

### Gaps
- 규칙 기반 일 유형과 비지도 군집을 비교한 동료심사 연구, Market Profile 일 유형의 빈도·전이 확률에 대한 독립 실증은 이번 검색에서 하나도 찾지 못했다.

## (c) 다음 구간·다음 날 패턴 예측 — Markov 전이, IOHMM/HSMM, 분류기, 아날로그(최근접 이웃), conformal 예측

### Takeaway
외생 변수를 넣는 HMM 계열(IOHMM, 공변량 HMM)은 선행 실증이 있다. 다만 **평균(방향) 예측은 역사적 평균을 못 이겼고 고차 모멘트(변동성)에서만 이겼다.** 장중 구간 간 예측가능성의 가장 확실한 실증은 "첫 30분 → 마지막 30분" 장중 모멘텀으로, 미국·중국 선물에서 확인됐다(R²≈2%, 작다). 아날로그(kNN) 예측은 단순 AR을 못 이긴 사례가 있어 증거가 혼재한다. 범주 예측 확률의 보정에는 conformal 예측 집합(APS)을 쓸 수 있다.

### Cited Findings
**IOHMM / 공변량 HMM**
- Bengio, Ducharme & Lauzon (CIRANO 2002s-48), "Experiments on the Application of IOHMMs to Model Financial Returns Series".
  - IOHMM은 방출(필요하면 전이) 확률이 입력 시퀀스에 의존하는 HMM이다. 외생 공변량을 넣는 표준 구조다.
  - 시장·업종 지수 수익률에서 **평균은 역사적 평균이 이겼고**, IOHMM은 **고차 모멘트**에서 표본외 우도가 유의하게 좋았다. — [CIRANO](https://cirano.qc.ca/en/summaries/2002s-48); [PDF](https://depot.erudit.org/dspace/bitstream/000146dd/1/2002s-48.pdf)
- Banachewicz, van der Vaart & Lucas: 부도 국면 HMM에 공변량을 넣었다. GDP 성장률·기간구조·주식수익률이 **전이확률**에 영향을 줬고, 효과는 산업마다 달랐다. — [VU Amsterdam](https://research.vu.nl/en/publications/modeling-portfolio-defaults-using-hidden-markov-models-with-covar/)
- Brusa et al. (2025): 시변 공변량과 시차 반응을 넣은 HMM 조기경보. 결측 공변량은 더미로 처리하고 표본 내·외 예측을 모두 평가했다. — [BOA Unimib](https://boa.unimib.it/handle/10281/546241)
- Horvath et al.의 합성 실험에서 HMM은 비가우시안 국면을 분리하지 못했다. — [ar5iv](https://ar5iv.arxiv.org/html/2110.11848)

**장중 구간 → 구간 예측의 실증 기준선 (장중 모멘텀)**
- Gao, Han, Li & Zhou (2018), "Market Intraday Momentum", *JFE* 129:394–414.
  - SPY 1993–2013에서 **전일 종가 기준 첫 30분 수익률이 마지막 30분 수익률을 예측**한다.
  - 고변동일·고거래량일·경기침체기·주요 매크로 발표일에 효과가 더 강하다.
  - 다른 활발한 ETF 10종과 **해외 주가지수선물 2종**에도 존재한다.
  - 설명으로 불규칙 리밸런싱(Bogousslavsky 2016)과 장마감 늦은 정보거래를 든다. — [WUSTL](https://profiles.wustl.edu/en/publications/market-intraday-momentum/); [SUFE 초록](https://academicnewsletter.sufe.edu.cn/info/356150)
  - 2014 워킹페이퍼판의 SPY 표본내 R²는 약 0.02(2%)다. 출판판 수치는 미확인. — [워킹페이퍼 사본](https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf)
- Jin, Kearney, Li & Yang (2020), "Intraday time-series momentum: Evidence from China", *J. Futures Markets* 40(4):632–650.
  - 중국 상품선물 4종(구리·철강·대두·대두박)에서 첫 30분이 마지막 30분을 **모두 양(+)으로 예측**한다.
  - 금속은 고거래량·고변동 첫 세션에서 가장 강하고, 전략이 매수보유를 상회한다. — [IDEAS](https://ideas.repec.org/a/wly/jfutmk/v40y2020i4p632-650.html)
- 반례: 아시아·태평양 시장에서는 장중 모멘텀이 미국만큼 보편적이지 않았다. Liu & Tse (2017)에서는 첫 30분은 예측력이 없고 **오버나이트 수익률**이 마지막 30분을 예측했다. — [Monash/Nottingham 재현 논문](https://nottingham-repository.worktribe.com/OutputFile/5273196); [AUT 발표](https://acfr.aut.ac.nz/__data/assets/pdf_file/0008/686816/4a-Z-Ivy-Zhou.pdf)
- KOSPI 200 선물을 직접 다룬 장중 모멘텀 연구는 이번 검색에서 찾지 못했다(아래 Gaps).

**아날로그 / 최근접 이웃 예측**
- 아테네 증시: 최근접 이웃 예측이 단순 AR보다 정확하지 않았다. 표본내 비선형성이 표본외에서 확인되지 않은 것이다. — [CORE](https://core.ac.uk/works/2500616)
- 상품시장 비선형 단기예측(Economics Letters 65(3), 1999) 등이 있으나 결과 수치는 미확인이다. — [IDEAS](https://ideas.repec.org/a/eee/ecolet/v65y1999i3p293-299.html)
- BIS 워킹페이퍼 57(최근접 이웃, 채권 포트폴리오 초과수익)은 랜덤워크와 비교했지만 결과를 확인하지 못했다. — [BIS](https://www.bis.org/publ/work57.pdf)
- 주식 횡단면 "이웃 자산" 방법은 표본외 연 Sharpe 1.15를 보고했다(94개 특성, 미출판 워킹페이퍼). 가격 패턴 아날로그가 아니다. — [AEA 2024](https://aeaweb.org/conference/2024/program/paper/hE52eEYE)

**Conformal 예측 (범주 확률 보정)**
- Romano, Sesia & Candès (2020), "Classification with Valid and Adaptive Coverage", NeurIPS 2020, arXiv 2006.02544.
  - 범주형(비순서) 라벨을 위한 새 conformity score(APS)를 제안한다.
  - 임의의 분류기를 감싸 **유한표본 주변(marginal) 커버리지**를 보장하고, 근사적 조건부 커버리지에 적응한다.
  - split conformal · CV+ · jackknife+와 결합할 수 있다. — [NeurIPS](https://proceedings.neurips.cc/paper/2020/hash/244edd7e85dc81602b7615cd705545f5-Abstract.html); [arXiv](https://arxiv.org/abs/2006.02544)

### Inferences
- **예측 사다리(추론)**: ① 기준선(유형별 기저율, 지속성 "어제 유형 = 오늘 유형") → ② 1차 Markov 전이행렬(라플라스/디리클레 평활) → ③ 다항 로지스틱(현재 유형 원-핫 + 외인 선물 순매수·오버나이트 갭 등) → ④ GBM → ⑤ IOHMM.
  - 300–500일에서는 ③까지가 표본 대비 안전하다.
  - 2차 Markov는 상태 k²개라 k=4면 16 조건, 조건당 약 20–30일로 이미 희소하다.
- **장중 세그먼트 전이**(예: 오전 패턴 → 오후 패턴)는 Gao et al. 계열 실증이 직접 받쳐주는 유일한 축이다. 다만 효과 크기가 R² 약 2% 수준이므로 "다음 패턴 예측 정확도"는 기저율보다 아주 조금 높은 정도로 기대해야 한다(추론).
- IOHMM 실증은 **방향은 못 맞히고 변동성 국면은 맞혔다.** 그러니 패턴 어휘를 "방향 × 변동폭"으로 짤 때 **변동폭 축 예측이 방향 축보다 쉬울 것**이다(추론, Bengio et al.과 일치).
- conformal 집합은 "다음 패턴 = {추세상승, 정상}"처럼 집합으로 내준다. 집합 크기 자체가 불확실성 지표가 되고, 집합이 전체 유형을 포함하는 날은 "판단 불가"로 처리할 수 있다(추론). 교환가능성 가정이 시계열에서 깨지므로 시간 순 split·롤링 보정이 필요하다(추론).

### Gaps
- HSMM(체류시간 반-마르코프)을 일 유형이나 장중 국면에 적용한 금융 1차 문헌은 이번 검색에서 확보하지 못했다.
- 일 유형 간 Markov 전이행렬을 실측 보고한 학술 연구, 그리고 KOSPI 200 선물 장중 모멘텀/전이 실증은 찾지 못했다.
- 선물에서 패턴 아날로그(kNN) 예측이 비용 차감 후 표본외 가치가 있다는 신뢰할 만한 증거도 찾지 못했다(실무 벤더 글만 존재).

## (d) 검증 방법론 — 거짓 발견 회피, 기준선, 점수 규칙

### Takeaway
라벨링은 triple-barrier/meta-labeling, 교차검증은 purged·embargoed CV와 CPCV를 쓴다. 다중검정은 deflated Sharpe ratio, PBO(CSCV), Harvey–Liu–Zhu의 t>3.0 기준을 함께 건다. 범주 예측 평가는 strictly proper 점수(log loss, Brier)로 하고 **기저율·지속성 기준선 대비 skill**로 보고한다.

### Cited Findings
- **Purged/embargoed CV** (López de Prado, *Advances in Financial Machine Learning*, 2018; 개념은 2017).
  - 테스트 라벨 구간과 겹치는 학습 관측을 제거(purge)한다.
  - 테스트 폴드 뒤에 비율 기반 embargo를 둔다. — [Wikipedia: Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation)
- **CPCV**: 여러 학습·테스트 블록 조합에 purge·embargo를 적용해 **단일이 아닌 다수의 백테스트 경로**를 만든다. mizarlabs 구현은 AFML 기술을 따라 n_test_splits개 폴드를 테스트로 쓴다. — [mizarlabs 문서](https://mizarlabs.readthedocs.io/en/stable/mizarlabs.model.html); [LuxAlgo 해설](https://www.luxalgo.com/library/concept/purged-cross-validation/)
- **Triple-barrier**: 이익 장벽 · 손실 장벽 · 시간 장벽 중 무엇에 먼저 닿는지로 라벨을 붙인다. **Meta-labeling**은 1차 신호가 이익이었는지를 라벨로 삼아, 방향이 아니라 "실행 여부·사이즈"를 학습한다. 겹치는 triple-barrier 라벨이 일반 k-fold에서 누수를 만들기 때문에 purge가 필요하다. — [LuxAlgo 라벨 정의](https://www.luxalgo.com/library/concept/label-definition-and-prediction-horizon/); [Trading Strategy 문서](https://tradingstrategy.ai/docs/learn/machine-learning.html)
- **Deflated Sharpe Ratio**: Bailey & López de Prado (2014), *J. Portfolio Management* 40(5). 다중시행 선택편향과 비정규 수익률(왜도·첨도)을 함께 보정한다. 입력은 시행 수와 시행 간 Sharpe 분산이다. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- **PBO / CSCV**: Bailey, Borwein, López de Prado & Zhu, *J. Computational Finance* (2015/2017로 연도 표기가 엇갈림).
  - N개 시행의 성과를 S개 블록으로 나눠 절반 학습·절반 테스트의 모든 조합을 열거한다.
  - PBO는 표본내 최우수 전략이 표본외에서 중앙값 이하인 조합의 비율이다.
  - 홀드아웃은 투자 백테스트에서 신뢰성이 떨어진다고 주장한다. — [SSRN 2326253](https://papers.ssrn.com/abstract=2326253); [eScholarship PDF](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf); [Borwein PDF](https://carmamaths.org/jon/backtest2.pdf)
- **다중검정**: Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns", *RFS* 29(1):5–68.
  - 수백 개 팩터 데이터마이닝 하에서 새 팩터는 **t > 3.0**을 넘어야 한다(통상 2.0 아님).
  - 검정 간 상관과 결측을 고려한 다중검정 틀을 쓴다.
  - "금융경제학에서 주장된 발견의 대부분은 거짓일 가능성이 높다"고 결론짓는다. — [NBER w20592](https://www.nber.org/papers/w20592); [SSRN](https://papers.ssrn.com/abstract=2513152)
  - 반론: Chen (arXiv 2206.15365) "Most claimed statistical findings in cross-sectional return predictability are likely true". 같은 문제를 다르게 추정하면 결론이 갈린다. — [arXiv 2206.15365](https://arxiv.org/pdf/2206.15365)
- **점수 규칙**: Gneiting & Raftery (2007), "Strictly Proper Scoring Rules, Prediction, and Estimation", *JASA* 102(477):359–378.
  - 진짜 믿음을 보고할 때 기대점수가 최적인 규칙이 proper이고, 그 최적이 유일하면 strictly proper다.
  - 로그·구형·이차(quadratic) 점수와 CRPS를 다루며, 범주형에 대한 Savage 표현을 정식화했다.
  - Brier는 범주형 이차 점수에 해당한다. 원문에서 이름으로 다뤘는지는 미확인이다. — [DTIC 기술보고서](https://apps.dtic.mil/sti/pdfs/ADA459827.pdf); [SUFE](https://academicnewsletter.sufe.edu.cn/info/445563)

### Inferences
- **패턴 연구용 검증 프로토콜(추론)**
  1. 어휘(군집/규칙)는 **학습 폴드 안에서만** 적합한다. 전체 기간에 군집하고 나서 CV를 돌리면 군집 중심이 미래를 본다(누수).
  2. 다음 날 예측은 라벨이 하루 단위로 겹치지 않아 purge가 가볍다. 반면 장중 세그먼트·다호라이즌 라벨은 겹쳐서 purge·embargo가 필수다.
  3. 시도한 어휘 정의(k, 창 길이, 규칙 임계)의 **수를 모두 기록**한다. 그래야 DSR·PBO의 시행 수 N을 정직하게 넣을 수 있다.
  4. 지표는 log loss·Brier를 **기저율 예측기 대비 skill score**(1 − 모형/기준선)로 보고하고, 지속성("어제 유형 반복") 기준선도 병기한다. 신뢰도 도표(calibration)를 함께 제출한다.
  5. 사전등록 기준을 고정한다. 이 프로젝트의 VALIDATION_CAMPAIGN 관행과 일치한다.
- **표본 규모와 검정력(추론)**: 500일에서 k=4 다음 날 유형 예측의 정확도 차 5%p를 검출하려면, 이항 표준오차가 약 √(0.25×0.75/500) ≈ 1.9%p이므로 대략 2.6σ다. Harvey et al.의 t>3.0을 적용하면 **경계선**이다. 장중 세그먼트(관측 수천 개, 상관 보정 후)가 검정력 면에서 유리하다.

### Gaps
- 장중 "패턴" 예측의 이론적·실증적 예측가능성 상한(예: 이 정도 R²가 한계라는 결과)을 직접 다룬 문헌은 장중 모멘텀 R²≈2% 외에 찾지 못했다.
- 범주형 패턴 예측에 Brier/log-loss skill을 보고한 금융 선행연구의 구체 수치는 확보하지 못했다.
- DSR·PBO의 정확한 공식과 CPCV 경로 수 공식은 원문을 확인하지 못했다(2차 요약 기반).
