"""
OptionChainSnapshot — 옵션 체인 피처 상태 관리.

COM BlockRequest 작업은 OptionChainWorker(QThread)가 담당.
이 클래스는 상태(chain_raw, features, last_refresh) 보관과
워커 기동 조건 판단만 수행한다.

사용 흐름:
    snap = OptionChainSnapshot()
    snap.initialize()                   # connect_broker() 완료 후 1회

    # QTimer 콜백(_poll_option_chain):
    if snap.is_due(spot) and not worker_running:
        snap.mark_refresh_started()
        worker = OptionChainWorker(snap.get_chain_raw(), spot, snap.cache_path, ...)
        worker.result_ready.connect(handler)
        worker.start()

    # 워커 완료 시그널:
    snap.on_worker_done(feats, chain_raw)

    # 파이프라인 STEP 4:
    chain_feats = snap.get_features()   # 최신 피처 (미갱신 시 이전 값)
"""
from __future__ import annotations

import json
import logging
import time
from typing import Dict, List

logger = logging.getLogger("OPTIONS")
system_logger = logging.getLogger("SYSTEM")


class OptionChainSnapshot:
    """
    옵션 체인 피처 상태 관리자.

    반환 피처 키 (feature_builder.build 의 option_data 에 병합):
      opt_chain_pcr       — 체인 전체 PCR (풋/콜 OI 비율)
      opt_atm_pcr         — ATM 행사가 기준 PCR
      opt_atm_call_oi     — ATM 콜 미결제약정
      opt_atm_put_oi      — ATM 풋 미결제약정
      opt_gex_bn          — 총 GEX (십억 원, 양수=딜러 감마롱)
      opt_gex_sign        — GEX 부호 (+1.0 / -1.0 / 0.0)
      opt_chain_available — 1.0 if 실데이터 수집 완료
    """

    def __init__(
        self,
        chain_cache_path: str = "data/option_chain.json",
        refresh_interval_min: int = 5,
        atm_window_pt: float = 30.0,
        pause_ms: int = 50,
    ) -> None:
        # 워커 생성 시 전달할 공개 파라미터
        self.cache_path = chain_cache_path
        self.atm_window = atm_window_pt
        self.pause_ms   = pause_ms

        self._interval_sec  = refresh_interval_min * 60
        self._chain_raw: List[Dict] = []
        self._last_refresh: float = 0.0
        self._last_features: Dict[str, float] = self._empty()
        self._ready = False

    # ── 기동 시 1회 ────────────────────────────────────────────────

    def initialize(self) -> None:
        """체인 캐시 파일 로드. COM 객체 생성은 OptionChainWorker가 담당."""
        self._chain_raw = self._load_chain_cache()
        self._ready = True
        if self._chain_raw:
            system_logger.info(
                "[OptionChain] 초기화 완료: 체인 캐시 %d 종목", len(self._chain_raw),
            )
        else:
            system_logger.info(
                "[OptionChain] 초기화 완료: 체인 캐시 없음 — 첫 워커 기동 시 CpOptionCode 수집",
            )

    # ── 워커 기동 조건 판단 (COM 없음) ────────────────────────────

    def is_due(self, spot: float) -> bool:
        """워커를 기동해야 하는 시점인지 확인."""
        if not self._ready or spot <= 0:
            return False
        return time.time() - self._last_refresh >= self._interval_sec

    def get_chain_raw(self) -> List[Dict]:
        """워커에게 전달할 체인 복사본 반환 (메인 스레드와 공유 없음)."""
        return list(self._chain_raw)

    def mark_refresh_started(self) -> None:
        """워커 기동 직전 호출 — 5분 인터벌 내 재기동 방지."""
        self._last_refresh = time.time()

    # ── 워커 완료 수신 (메인 스레드, Qt 시그널) ───────────────────

    def on_worker_done(self, feats: Dict, chain_raw: List[Dict]) -> None:
        """
        OptionChainWorker.result_ready 수신 시 호출 (메인 스레드).

        chain_raw가 빈 list일 때 _chain_raw를 갱신하지 않는다
        → 다음 워커가 CpOptionCode 재수집하도록 강제.
        """
        if chain_raw:
            self._chain_raw = chain_raw
        if feats:
            self._last_features = feats
            avail = bool(feats.get("opt_chain_available"))
            if not avail:
                system_logger.warning(
                    "[OptionChain] 데이터 수집 실패 (opt_chain_available=0) — 이전 피처 유지",
                )
        else:
            system_logger.warning("[OptionChain] 워커 결과 없음 — 이전 피처 유지")

    # ── 파이프라인 STEP 4 ─────────────────────────────────────────

    def get_features(self) -> Dict[str, float]:
        return dict(self._last_features)

    # ── 일일 리셋 ─────────────────────────────────────────────────

    def reset_daily(self) -> None:
        self._last_refresh = 0.0
        self._last_features = self._empty()
        logger.info("[OptionChain] 일일 리셋")

    # ── 내부 ───────────────────────────────────────────────────────

    def _load_chain_cache(self) -> List[Dict]:
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("chain", [])
        except Exception:
            return []

    @staticmethod
    def _empty() -> Dict[str, float]:
        return {
            "opt_chain_pcr":       0.0,
            "opt_atm_pcr":         0.0,
            "opt_atm_call_oi":     0.0,
            "opt_atm_put_oi":      0.0,
            "opt_gex_bn":          0.0,
            "opt_gex_sign":        0.0,
            "opt_chain_available": 0.0,
        }
