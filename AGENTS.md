# AGENTS.md — 미륵이 (KOSPI 200 선물 자동매매)

> 마지막 갱신: 299차 (2026-07-07) 기준. 항상 CLAUDE.md 절대 원칙(§변경 가능한 한시 예외 포함)을 최신 소스로 우선한다.

## 실행 환경

- **Python 3.7 32-bit** (`conda env: py37_32`) — 절대 변경 불가, 키움/Cybos COM OCX 요구사항
- **Windows 전용** — COM/OCX 의존성 (CybosPlus 또는 키움 OpenAPI+)
- **`scipy==1.5.4`** 고정 — 1.7+ 버전은 32-bit DLL 충돌 발생
- **`scikit-learn==1.0.2`**, **`joblib==1.1.0`**, **`numpy==1.21.6`**, **`pandas==1.3.5`** — Python 3.7 지원 상한
- **`pyrightconfig.json`** — `pythonVersion: "3.7"`, `pythonPlatform: "Windows"` 설정

## 실행 방법

**절대 `python main.py`를 직접 실행하지 말 것.** 반드시 런처 사용:

```
start_mireuk.bat             # 실전용 런처 (BROKER_BACKEND=cybos 설정, conda 활성화, Qt 경로 설정)
start_mireuk_cybos_test.bat  # 테스트용 런처 (동일 구성, 명시적 테스트 변형)
```

.bat 파일이 처리하는 순서: conda 활성화 → Qt 플러그인 경로 → Cybos 사전 점검 → `python main.py`

## 브로커 백엔드

`BROKER_BACKEND` 환경변수로 선택 (기본값: `cybos`):

| 백엔드 | 파일 | 상태 |
|---|---|---|
| `cybos` | `collection/broker/cybos_broker.py` | 현재 메인 |
| `kiwoom` | `collection/broker/kiwoom_broker.py` | 레거시/대체 |

팩토리: `collection/broker/factory.py:create_broker()`. `TradingSystem`에서 `self.broker`(신규), `self.kiwoom`(레거시 별칭 = `self.broker.api`)로 접근.

## 절대 원칙 (from CLAUDE.md)

1. **오버나이트 금지** — 15:10 강제 청산, 예외 없음
2. **CORE 피처는 호라이즌 그룹별로 분리 (변경 불가)** — 단기(1·3·5m): CVD(`features/technical/cvd.py`)·VWAP(`features/technical/vwap.py`)·OFI(`features/technical/ofi.py`), 중기(10·15m): VWAP, 장기(30m): opt_chain_pcr. **30m 호라이즌은 296차부터 앙상블/CoherenceGate/CascadeCoherence에서 전면 퇴역**(full_cv acc=0.3052, 구조적으로 랜덤 이하) — 예측 계산 자체는 유지되나 진입 판단에는 미사용
3. **COM 콜백 안전** — `_on_receive_tr_data` 등 콜백 내부에서는 상태 저장 + `QEventLoop.quit()`만 허용. `dynamicCall`, `pyqtSignal.emit()` 금지 → `0xC0000409` 크래시 유발
4. **PyQt5 QApplication을 키움 OCX보다 먼저 생성** — `main.py:35-37` 참조
5. **GetRepeatCnt / GetCommData 파라미터 구분** — 2번째 인자가 `record_name` vs `rq_name`으로 다름
6. **알파 리서치 봇 자동 통합 절대 금지** — 사용자 검토 필수
7. **[모의투자 한정 한시 예외]** CB②(`CB_CONSEC_STOP_LIMIT=9999`, 사실상 비활성)와 CB③-P4(`CB3_P4_GRADE_BLOCK_ENABLED=False`)는 실투 전환 전 반드시 복원 검토 대상 — 상세 사유·복원 조건은 CLAUDE.md §절대 원칙 참조

## 아키텍처

- **진입점**: `main.py` → `TradingSystem` 클래스
- **매분 파이프라인**: `run_minute_pipeline(bar)` — 9단계 순차 실행 (CLAUDE.md §매분 실행 파이프라인 참조)
- **브로커 추상화**: `collection/broker/` — `BrokerAPI` 기반, `CybosBroker`, `KiwoomBroker`
- **설정**: `config/settings.py`(경로, 시간), `config/secrets.py`(gitignore, 반드시 존재해야 함), `config/constants.py`(TR코드, FID)
- **모든 경로**: `config/settings.py`의 `BASE_DIR` 기준 상대경로 — PC 간 프로필 이식 가능

## 주요 모듈

| 디렉토리 | 목적 |
|---|---|
| `collection/` | 데이터 수집 (브로커, 매크로, 뉴스, 옵션) |
| `features/` | 피처 엔지니어링 (기술적, 수급, 옵션, 매크로, 감성) |
| `model/` | 멀티 호라이즌 GBM 예측 + 앙상블 판단 |
| `learning/` | 온라인 SGD, 배치 재학습, 보정, SHAP, 강화학습 |
| `strategy/` | 진입/청산/포지션 관리 |
| `safety/` | 서킷 브레이커(5종 트리거), 킬스위치, 비상청산 |
| `backtest/` | Walk-Forward, 슬리피지, 성과 지표 |
| `dashboard/` | PyQt5 실시간 대시보드 |
| `research_bot/` | 알파 발굴 봇 (자동 통합 비활성화) |

## 테스트

- `tests/` — 회귀 테스트(424차~). COM/PyQt 의존 없는 모듈만 대상이며, pytest 스타일
  (`test_473_*` 등)과 단독 실행 스타일(`python tests/test_468_*.py`)이 혼재한다.
  (구버전 서술 "테스트 프레임워크 전혀 없음"은 2026-06 이후 사실이 아니다 — 476차 정정.)
- **도달성 불변식 테스트 명명 규약 (476차 G-5)**: 게이트·등급·임계 등 "코드에 있으니
  지켜진다"고 전제되는 분기를 새로 만들 때는 `tests/test_*_reachability.py` 형식의
  도달성 테스트를 함께 둔다. 정의가 바뀌면 테스트가 깨져 관련 문서(CLAUDE.md 등)의
  갱신을 강제하는 방식이다 — 선례: `test_471_force_exit_reachability.py`(15:10 경로) ·
  `test_473_core_group_reachability.py`(CORE 그룹) · `test_476_grade_reachability.py`
  (앙상블 등급 A/B). ⚠ 라이브 **분포**에 의존하는 단언은 CI에서 불안정하므로 점검
  도구(일일 점검 수집기 §12b 임계-분포 대조)에 두고, 테스트는 **정의 대조**만 한다.
- 오프라인 검증 보조: 실시간 시뮬레이션 모드(`python main.py --mode simulation`) ·
  `backtest/walk_forward.py` · Cybos/Kiwoom 실거래 직접 운영

## DB 파일

`data/db/` 아래 SQLite 데이터베이스:
- `predictions.db` — 예측 로그 및 실제 결과
- `shap_tracker.db` — SHAP 기여도 누적
- `trades.db` — 매매 이력
- `challenger.db` — 챔피언-도전자 평가
- `raw_data.db` — 학습 데이터

## 세션 연속성

`dev_memory/`에 세션 로그, 현재 상태, 다음 할 일이 추적됨. 작업 재개 시 읽는 순서:
1. `CLAUDE.md` (절대 원칙 + 한시 예외 현황)
2. `dev_memory/CURRENT_STATE.md`
3. `dev_memory/NEXT_TODO.md`
4. `logs/` 최신 파일

> `dev_memory/CODEX_STARTUP_ROUTINE.md`는 Codex 협업 시절(~5월) 루틴으로 2026-05-11 이후 갱신 없음 — 현재는 Claude Code 기반으로 운영되므로 위 순서를 따른다.

## Git

- 리모트: `https://github.com/hinsmile77-debug/futures`
- 브랜치: `main`(배포), `develop`(개발), `feature/*`(기능별)
- **`config/secrets.py`는 gitignore 대상** — 각 PC에서 수동 생성 필요
- 데이터, 모델, 로그 디렉토리는 gitignore (대용량)

## 참고 문서

- `CLAUDE.md` — 전체 운영 규칙, 파이프라인, Phase 현황
- `CORE.md` — 핵심 판단 규칙 (매매 근거, 확률 임계값)
- `ROADMAP.md` — 단계별 구현 계획과 마일스톤 체크리스트
- `_archive/plans/PROJECT_DESIGN.md` — 2026-04 v1.0 설계 명세 (30m 호라이즌 등 구식 내용 포함, 사료적 참고용만)
