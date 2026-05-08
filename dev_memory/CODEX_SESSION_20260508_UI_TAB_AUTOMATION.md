# 2026-05-08 UI 탭 자동 운영 메모

## 작업 요약

- 프로그램 시작 직후 우측 패널 기본 탭을 `1 시스템`으로 고정.
- 레짐 확정 후 우측 패널을 `3 주문/체결`, 가운데 패널을 `진입 관리`로 자동 전환.
- 체결 진입 완료 또는 수동 포지션 복원 완료 시 가운데 패널을 `청산 관리`로 자동 전환.
- 최종 청산 완료 시 가운데 패널을 다시 `진입 관리`로 자동 복귀.
- 사용자가 우측/가운데 탭을 수동 전환해도 마우스가 탭 영역 위에 없어진 뒤 20초 경과 시 현재 운영 상태에 맞는 탭으로 자동 복귀.

## 구현 위치

- `dashboard/main_dashboard.py`
  - `UiAutoTabController` 추가
  - `DashboardAdapter`에 `set_ui_startup_mode()`, `set_ui_ready_mode()`, `set_ui_position_mode()` 추가
- `main.py`
  - 대시보드 초기화 직후 startup 모드 적용
  - 레짐 확정 시 ready 모드 적용
  - 체결 진입, 외부 진입 동기화, 수동 포지션 복원 시 position 모드 적용
  - 최종 청산 완료 시 ready 모드 적용

## 확인

- `python -m py_compile dashboard/main_dashboard.py main.py` 통과
