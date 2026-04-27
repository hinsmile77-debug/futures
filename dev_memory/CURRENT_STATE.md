# 미륵이 (futures) 현재 개발 상태

> 마지막 업데이트: 2026-04-27
> 이 파일이 가장 먼저 읽혀야 한다.

---

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

## 2026-04-26 세션 주요 수정

| 항목 | 수정 내용 |
|---|---|
| TR 코드 | OPT10080 → **OPT50029** (`config/constants.py`) |
| COM 콜백 | 메타데이터만 저장 + QEventLoop.quit(), 실제 API 호출은 exec_() 복귀 후 |
| GetRepeatCnt | 2번째 파라미터: rq_name → **record_name** (fallback: `meta.get("record_name") or rq_name`) |
| 근월물 조회 | GetFutureList() 우선 → GetMasterCodeList("10") → 날짜 계산 fallback |
| GetCommDataEx | → **GetCommData** (서명 오류 수정) |
| 대시보드 | `create_dashboard()` 시작 시 show(), 5분마다 대기 상태 로그 |

---

## 현재 차단 이슈

| 이슈 | 원인 | 상태 |
|---|---|---|
| GetRepeatCnt = 0 | record_name 수정 후 최종 확인 필요 | ⚠️ 검증 대기 |
| 모의투자 미실행 | 실시간 분봉 수신 → 파이프라인 동작 미확인 | ⏳ |
| Walk-Forward 26주 | 실거래 데이터 미확보 | ⏳ 장기 과제 |

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
