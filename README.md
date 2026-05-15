# KOSPI 200 선물 자동매매 시스템 — 미륵이

- 프로젝트 경로: C:\Users\82108\PycharmProjects\futures
- 실행 환경: Python 3.7 32-bit (Windows 전용, COM/OCX)
- 기본 브로커 백엔드: cybos (BROKER_BACKEND)

## 핵심 원칙

- 15:10 강제 청산(오버나이트 금지)
- CORE 피처 3종(CVD/VWAP/OFI) 유지
- COM 콜백 안전 규칙 준수(콜백 내부 동적 호출 금지)

## 실행 방법

주의: 직접 python main.py 실행 대신 런처 사용 권장.

```bat
start_mireuk.bat
start_mireuk_cybos_test.bat
```

런처가 수행하는 기본 순서:

1. conda py37_32 활성화
2. Qt/브로커 실행환경 설정
3. Cybos 사전 점검
4. main.py 실행

## 현재 아키텍처 요약

- 진입점: main.py (TradingSystem)
- 브로커 추상화: collection/broker/
    - KiwoomBroker
    - CybosBroker
- 런타임 서비스 분리(진행 중): strategy/runtime/
    - broker_runtime_service.py
    - session_recovery_service.py
- 매분 파이프라인: 검증 -> 학습 -> 피처 -> 예측 -> 진입/청산 -> 기록
- 안전장치: safety/ (circuit_breaker, kill_switch, emergency_exit)

## 주요 디렉터리 (실존 기준)

- collection/: broker/cybos/kiwoom/macro/news/options 수집
- features/: technical/options/macro/sentiment + feature_builder
- model/: 멀티호라이즌 모델/앙상블
- learning/: 온라인/배치 학습, 보정, drift, self_learning
- strategy/: entry/exit/position/risk/runtime
- dashboard/: PyQt 대시보드
- backtest/: walk-forward, 슬리피지, 성과 지표
- data/: raw/processed/db/session 상태 파일
- logs/: 런타임 로그
- dev_memory/: 세션 기록 및 감사 문서

## 문서 안내

- 운영 규칙: AGENTS.md, CLAUDE.md
- 핵심 판단 규칙: CORE.md
- 로드맵: ROADMAP.md
- 설계 명세: PROJECT_DESIGN.md
- Cybos 리팩터링 계획: CYBOS_PLUS_REFACTOR_PLAN.md

## 초기 설정

1. 저장소 클론
2. requirements.txt 설치
3. config/secrets.py 작성(계좌/토큰)
4. 런처로 실행

## 현재 알려진 상태

- Cybos 병행 런타임 연결 완료
- 브로커/세션 복원 서비스 분리 1차 완료
- 예외 정책 3계층(recoverable/degraded/fatal) 도입 시작
- 장중 실시간/주문체결 실검증 및 문서 정리는 진행 중
