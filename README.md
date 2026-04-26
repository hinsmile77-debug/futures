# KOSPI 200 선물 방향 예측 시스템 — 한량이 (Futures Edition)

> **프로젝트 경로**: `C:\Users\82108\PycharmProjects\futures`  
> **기반 기술**: Python 3.8 (32-bit) + 키움증권 OpenAPI+  
> **최종 업데이트**: 2026-04

---

## 프로젝트 개요

KOSPI 200 선물의 **1분봉 실시간 데이터**를 수집·분석하여 매분 단위로 상승/하락 방향을 예측하고, 자동/수동 하이브리드 방식으로 선물 매수·매도에 진입하는 시스템.

### 핵심 설계 원칙

| 원칙 | 내용 |
|------|------|
| 예측 단위 | 1분봉 기준 1·3·5·10·15·30분 멀티 호라이즌 |
| 자가학습 | 분 단위 SGD 온라인 학습 + 30분 GBM 배치 재학습 |
| 진입 방식 | 하이브리드 (신뢰도 70%↑ + 외인 일치 → 자동 / 58~70% → 수동 확인) |
| **청산 원칙** | **당일 청산 절대원칙 — 15:10 강제 청산, 예외 없음** |
| 포지션 크기 | 켈리 공식 변형 (하프 켈리, 신뢰도·레짐 동적 조정) |

---

## 폴더 구조

```
futures/
│
├── README.md                   ← 이 파일 (프로젝트 전체 설명)
├── main.py                     ← 메인 실행 진입점
├── requirements.txt            ← 의존성 패키지
│
├── config/                     ← 설정 파일
│   ├── settings.py             ← API 키, 계좌 정보, 전역 설정
│   └── constants.py            ← 상수 정의 (만기코드, 피처명 등)
│
├── collection/                 ← 데이터 수집 모듈
│   ├── kiwoom/                 ← 키움 OpenAPI+ 연동
│   │   ├── api_connector.py    ← API 연결·초기화
│   │   ├── realtime_data.py    ← 실시간 1분봉 수신
│   │   ├── investor_data.py    ← 투자자별 수급 수집
│   │   └── option_data.py      ← 옵션 체결·잔고 수집
│   ├── macro/                  ← 매크로 지표 수집
│   │   ├── macro_fetcher.py    ← 환율·금리·VIX·S&P500 선물
│   │   └── regime_classifier.py← 시장 레짐 분류 (RISK_ON/OFF/NEUTRAL)
│   ├── news/                   ← 뉴스 수집 (v5 Phase 4)
│   │   └── news_fetcher.py     ← 한경·매경·블룸버그 헤드라인
│   └── options/                ← 옵션 플로우 분석
│       ├── option_flow.py      ← ITM/ATM/OTM 구간별 집계
│       ├── divergence.py       ← 외인-개인 다이버전스 지수
│       └── weekly_cycle.py     ← 위클리 만기 사이클 관리
│
├── features/                   ← 피처 생성 모듈
│   ├── technical/              ← 기술적 지표 (고정 CORE 3개 + v5 추가)
│   │   ├── cvd.py              ← CVD 다이버전스 ★ CORE
│   │   ├── vwap.py             ← VWAP + 밴드 ★ CORE
│   │   ├── ofi.py              ← Order Flow Imbalance ★ CORE
│   │   ├── microprice.py       ← Microprice (v5 - 헤지펀드 표준)
│   │   ├── lob_imbalance.py    ← LOB Imbalance Decay (v5)
│   │   ├── tick_rule.py        ← 틱 불균형
│   │   ├── atr.py              ← ATR 변동성 레짐
│   │   ├── ama.py              ← 적응형 모멘텀 (추세 효율성 ER)
│   │   ├── market_profile.py   ← POC·Value Area
│   │   └── kyle_lambda.py      ← 시장 두께 측정
│   ├── supply_demand/          ← 수급 피처
│   │   ├── investor_features.py← 외인·기관·개인·프로그램 순매수
│   │   ├── program_trade.py    ← 프로그램 차익·비차익
│   │   └── herding.py          ← 군집 행동 감지 (v5)
│   ├── options/                ← 옵션 플로우 피처
│   │   ├── option_features.py  ← PCR·베이시스·미결제약정
│   │   ├── divergence_features.py← 역발상 신호·다이버전스 지수
│   │   └── weekly_features.py  ← 위클리 만기 가중치
│   ├── macro/                  ← 매크로 피처
│   │   └── macro_features.py   ← SP500선물·VIX·환율·금리
│   ├── sentiment/              ← 뉴스 감성 분석 (v5 Phase 4)
│   │   ├── kobert_sentiment.py
│   │   └── news_features.py
│   └── feature_builder.py      ← 전체 피처 통합 빌더
│
├── model/                      ← 예측 모델
│   ├── multi_horizon_model.py  ← GBM 6개 호라이즌 모델
│   ├── target_builder.py       ← 타겟 라벨 생성 (±threshold)
│   ├── ensemble_decision.py    ← 앙상블 가중합 + 진입 등급 판정
│   ├── regime_specific.py      ← 레짐별 전용 모델 (v5)
│   ├── horizons/               ← 학습된 모델 파일 저장 (.pkl)
│   └── scaler/                 ← 정규화 스케일러 저장 (.pkl)
│
├── learning/                   ← 자가학습 시스템
│   ├── online_learner.py       ← SGD 분 단위 온라인 학습
│   ├── batch_retrainer.py      ← GBM 30분 배치 재학습
│   ├── prediction_buffer.py    ← 예측·실제결과 버퍼 (SQLite)
│   ├── meta_confidence.py      ← 메타 신뢰도 학습기 (v5)
│   ├── bayesian_updater.py     ← 베이지안 업데이트 (v5)
│   ├── shap/
│   │   ├── shap_tracker.py     ← SHAP 기여도 실시간 누적
│   │   └── feature_selector.py ← 동적 피처 교체 심사
│   ├── self_learning/
│   │   ├── accuracy_reporter.py← 호라이즌별 정확도 리포트
│   │   └── performance_auditor.py← 교체 성과 감사·롤백
│   └── rl/                     ← 강화학습 (v5 Phase 4)
│       ├── environment.py
│       ├── ppo_agent.py
│       └── reward_design.py
│
├── safety/                     ← 안전장치 (v5 - 필수)
│   ├── circuit_breaker.py      ← 5종 트리거 비상 정지
│   ├── kill_switch.py          ← 즉시 시스템 중단
│   └── emergency_exit.py       ← 전 포지션 시장가 청산
│
├── strategy/                   ← 매매 전략
│   ├── entry/
│   │   ├── entry_manager.py    ← 진입 관리 (체크리스트·등급·수량)
│   │   ├── checklist.py        ← 9개 사전 체크리스트
│   │   ├── position_sizer.py   ← 켈리 포지션 사이즈 계산
│   │   └── entry_filter.py     ← 시간·레짐·연속손절 필터
│   ├── exit/
│   │   ├── exit_manager.py     ← 청산 통합 관리
│   │   ├── stop_loss.py        ← 하드스톱·구조적손절·VWAP손절
│   │   ├── take_profit.py      ← ATR·VWAP밴드·POC 목표청산
│   │   ├── trailing_stop.py    ← 트레일링 스톱 (수익 추적)
│   │   ├── signal_exit.py      ← 신호 반전·SHAP 붕괴 청산
│   │   └── time_exit.py        ← 시간 강제 청산 (15:10 절대원칙)
│   └── position/
│       ├── position_tracker.py ← 현재 포지션 상태 추적
│       └── partial_exit.py     ← 부분 청산 3단계 관리
│
├── dashboard/                  ← 실시간 대시보드
│   ├── main_dashboard.py       ← 대시보드 메인 (PyQt5 또는 웹)
│   ├── prediction_panel.py     ← 멀티 호라이즌 예측 패널
│   ├── entry_panel.py          ← 진입 관리 패널
│   ├── exit_panel.py           ← 청산 관리 패널
│   ├── feature_panel.py        ← SHAP 피처 중요도 패널
│   ├── option_panel.py         ← 옵션 플로우·다이버전스 패널
│   └── cycle_panel.py          ← 위클리 만기 사이클 패널
│
├── backtest/                   ← 백테스트 (v5 강화)
│   ├── backtest_engine.py      ← 백테스트 실행 엔진
│   ├── data_loader.py          ← 과거 데이터 로딩
│   ├── walk_forward.py         ← Walk-Forward 검증 (v5)
│   ├── slippage_simulator.py   ← 슬리피지 시뮬레이터 (v5)
│   ├── transaction_cost.py     ← 수수료·세금 모델링 (v5)
│   ├── performance_metrics.py  ← 성과 지표 계산
│   └── report_generator.py     ← 백테스트 리포트 생성
│
├── data/                       ← 데이터 저장소
│   ├── raw/                    ← 원본 수집 데이터 (CSV)
│   ├── processed/              ← 전처리된 피처 데이터
│   └── db/                     ← SQLite DB 파일
│       ├── predictions.db      ← 예측 로그 및 실제 결과
│       ├── shap_tracker.db     ← SHAP 기여도 누적
│       └── trades.db           ← 매매 이력
│
├── utils/                      ← 공통 유틸리티
│   ├── logger.py               ← 로깅 설정
│   ├── time_utils.py           ← 시간·만기일 계산
│   ├── db_utils.py             ← SQLite 공통 함수
│   └── notify.py               ← 알림 (카카오톡·SMS)
│
├── logs/                       ← 실행 로그 파일
└── docs/                       ← 설계 문서
    ├── PROJECT_DESIGN.md       ← 전체 설계 명세 (이 문서)
    ├── API_GUIDE.md            ← 키움 API 사용 가이드
    ├── PARAMETER_GUIDE.md      ← 파라미터 설명서
    └── BACKTEST_REPORT.md      ← 백테스트 결과
```

---

## Git 저장소

```
https://github.com/hinsmile77-debug/futures
Branch: main (배포) / develop (개발) / feature/* (기능별)
```

## PC 간 호환성 원칙

모든 경로는 `BASE_DIR` 기준 상대경로로 계산됩니다.
사용자명이 달라도 (`82108` → `trader` 등) 코드 수정 없이 동일 동작합니다.

```python
# config/settings.py — 어느 PC에서나 자동 계산
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 결과: C:\Users\{누구든}\PycharmProjects\futures
```

## 새 PC 배포 (3단계)

```bash
# 1. 클론
cd C:\Users\{사용자명}\PycharmProjects
git clone https://github.com/hinsmile77-debug/futures.git && cd futures

# 2. 환경 설정
pip install -r requirements.txt
python utils/setup_dirs.py          # 폴더 생성 + secrets.py 자동 복사
# config/secrets.py 열어서 계좌번호·API 키 입력

# 3. 실행 (모의투자 먼저)
python main.py
```

## 기존 PC 업데이트

```bash
git pull origin main
pip install -r requirements.txt     # 새 패키지 반영
```

---

## 개발 단계 로드맵 (v5)

| 단계 | 내용 | 기간 | 상태 |
|------|------|------|------|
| Phase 0 | 설계 + 인프라 (폴더·Git·문서) | - | ✅ 완료 |
| Phase 1 | 핵심 시스템 구축 (수집·피처·모델·전략) | 4주 | 🔲 진행 예정 |
| Phase 2 | 안전장치 + 검증 (Circuit Breaker·슬리피지·Walk-Forward) | 3주 | 🔲 |
| Phase 3 | 알파 강화 (Microprice·LOBID·메타신뢰도·변동성표적화) | 4주 | 🔲 |
| Phase 4 | 차별화 (강화학습·베이지안·뉴스 감성) | 8주 | 🔲 |
| Phase 5 | 실전 운영 (모의 4주 → 실전 30% → 정상 사이즈) | 지속 | 🔲 |

> Phase 2 안전장치는 절대 건너뛰지 않습니다. 망하지 않는 시스템이 우선.

---

> 상세 설계는 `docs/PROJECT_DESIGN.md`, 단계별 일정은 `docs/ROADMAP.md` 참조
