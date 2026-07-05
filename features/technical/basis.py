# features/technical/basis.py — [260704 감사 P2] 선물-현물 베이시스
"""
베이시스 = 선물가 - KOSPI200 현물지수. 차익거래 압력의 직접 신호 —
"국내 선물 단기 방향의 고전적 강신호인데 미탑재"(감사 §6-3 순위 1).

콘탱고(선물>현물, 정상 상태) 확대/축소 및 변화율이 프로그램 매매(차익거래) 유입
압력을 선행 반영한다. 현물지수는 dscbo1.StockMst 폴링(1분 주기)으로 얻으므로
선물 체결 대비 다소 지연될 수 있음 — 초 단위 정밀도가 아니라 분 단위 추세용.
"""
from collections import deque
from typing import Dict, Optional


class BasisCalculator:
    """선물-현물 베이시스 및 변화율 계산."""

    def __init__(self, window: int = 20):
        self._prev_basis: Optional[float] = None
        self._history = deque(maxlen=window)

    def update(self, futures_price: float, spot_index: Optional[float]) -> Dict:
        """
        spot_index가 없으면(폴링 실패/미연결) ready=False로 마지막 유효값을 유지한다.
        0으로 리셋하면 급변 아티팩트가 생겨 스케일러 z-폭발을 유발할 수 있음
        (감사 §6-2 위생 지적 — 상수/결측 방치 금지 원칙과 동일하게, 값 자체는
        보존하고 ready 플래그로 신뢰도를 구분).
        """
        if not spot_index or spot_index <= 0 or not futures_price or futures_price <= 0:
            return {
                "basis_pt": self._history[-1] if self._history else 0.0,
                "basis_change_pt": 0.0,
                "basis_ready": False,
            }

        basis = futures_price - spot_index
        change = (basis - self._prev_basis) if self._prev_basis is not None else 0.0
        self._prev_basis = basis
        self._history.append(basis)

        return {
            "basis_pt": round(basis, 4),
            "basis_change_pt": round(change, 4),
            "basis_ready": True,
        }

    def reset_daily(self) -> None:
        self._prev_basis = None
        self._history.clear()
