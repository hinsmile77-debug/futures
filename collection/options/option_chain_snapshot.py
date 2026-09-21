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

import datetime as _dt
import json
import logging
import os
import time
from typing import Dict, List, Optional

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
        # [MW0601 612차] 체인 **코드 목록**이 언제 수집된 것인가. 피처 신선도
        # (`_last_refresh`, 5분)와는 별개 축이다 — 아래 chain_reload_due() 참조.
        self._chain_saved_at: Optional[str] = None

    # ── 기동 시 1회 ────────────────────────────────────────────────

    def initialize(self) -> None:
        """체인 캐시 파일 로드. COM 객체 생성은 OptionChainWorker가 담당."""
        self._chain_raw = self._load_chain_cache()
        self._ready = True
        if self._chain_raw:
            system_logger.info(
                "[OptionChain] 초기화 완료: 체인 캐시 %d 종목 (수집일=%s, 재수집필요=%s)",
                len(self._chain_raw), self._chain_saved_at or "미상",
                self.chain_reload_due(),
            )
        else:
            system_logger.info(
                "[OptionChain] 초기화 완료: 체인 캐시 없음 — 첫 워커 기동 시 CpOptionCode 수집",
            )

    # ── 워커 기동 조건 판단 (COM 없음) ────────────────────────────

    # [MW0601 612차] 타이머 지터 여유. 아래 is_due() 참조.
    _DUE_TOLERANCE_SEC = 5.0

    def is_due(self, spot: float) -> bool:
        """워커를 기동해야 하는 시점인지 확인.

        🔴 [MW0601 612차] 「5분 폴링」이 실제로는 대개 10분이었다.
        2026-09-21 실측 완료 간격 31개: **5분 8 / 10분 16 / 9분 3 / 14분 2 / 그 외 2.**

        원인은 **경계 레이스**다. `QTimer.setInterval(300_000)`은 정확히 300초마다
        도는데(완료 로그의 초가 하루 종일 `:28`로 동일했다) 여기 비교가 여유 없는
        `>= 300` 이었다. Qt 타이머 클럭과 `time.time()`(시스템 시계, NTP 보정에
        흔들린다) 사이 **수 ms 차이**만 나도 한 틱이 통째로 버려지고, 그러면
        다음 기회는 300초 뒤다 — 정확히 관측된 5/10분 교대 패턴이다.

        두 가지를 함께 고친다:
          ① `time.time()` → `time.monotonic()` — 시스템 시계 보정과 무관해진다.
          ② 여유 `_DUE_TOLERANCE_SEC` — 타이머가 미세하게 일찍 읽혀도 버리지 않는다.
             5초는 300초의 1.7%라 폴링 빈도에 사실상 영향이 없다.

        ⚠ 어느 분기가 반환했는지는 **로그가 없어 직접 확인하지 못했다**(호출부
          `_poll_option_chain`의 스킵 로그가 debug 라 파일에 안 남는다). 그래서
          호출부에 스로틀 INFO 를 함께 올렸다 — 다음엔 추론이 아니라 측정으로
          판정된다(계측 4원칙 ③).
        """
        if not self._ready or spot <= 0:
            return False
        return self.seconds_since_refresh() >= self._interval_sec - self._DUE_TOLERANCE_SEC

    def seconds_since_refresh(self) -> float:
        """마지막 워커 기동 이후 경과(초). 한 번도 안 돌았으면 매우 큰 값."""
        if self._last_refresh <= 0:
            return float("inf")
        return time.monotonic() - self._last_refresh

    @property
    def interval_sec(self) -> int:
        """설정된 폴링 주기(초). 대시보드 신선도 게이지가 이 값을 쓴다 —
        패널이 300 을 하드코딩하고 있어 주기를 바꾸면 게이지가 거짓말을 했다(612차)."""
        return self._interval_sec

    def chain_reload_due(self) -> bool:
        """체인 **코드 목록**을 CpOptionCode 로 다시 받아야 하는가.

        🔴 [MW0601 612차] 종전에는 재수집 조건이 `_execute()` 의 "캐시가 비었거나
        ATM 대상이 0건" 뿐이었다. 그런데 낡은 목록에도 유효 코드가 남아 있으면
        대상이 0건이 되지 않으므로 **그 조건은 영원히 성립하지 않는다.**

        실측(2026-09-21): `data/option_chain.json` 의 마지막 기록이 **2026-06-04**
        였다. 3.5개월 전 목록이라 근월물이 된 10월물에 그 사이 추가 상장된
        **2.5pt 행사가가 통째로 빠져 있었다** — 현재가 1110 근방 캐시 행사가가
        1080·1085·1090… 5pt 간격이다(원월물 시절 상장분). 위클리 옵션 코드도 전무.
        그 위에서 계산된 `opt_chain_pcr`·`opt_gex_bn`·ATM OI 는 **행사가 격자가
        절반인 부분집합**의 값이다.

        ⇒ 거래일이 바뀌면 목록을 다시 받는다. 판정은 캐시의 `saved_at`(없으면
          파일 mtime) 날짜 대 오늘 날짜다. 하루 1회이므로 COM 비용은 무시할 수준.
        ⚠ 재수집에 실패해도 낡은 목록을 **버리지 않는다** — 워커가 폴백한다.
          "낡은 값"보다 "값 없음"이 나은 상황이 아니다(여긴 코드 목록이지 관측치가
          아니다). 대신 실패는 WARNING 으로 남는다(계측 4원칙 ④).
        """
        if not self._ready:
            return False
        saved = self._chain_saved_at or self._cache_mtime_date()
        if not saved:
            return True          # 언제 받았는지 모른다 → 받는다(미측정 ≠ 최신)
        return saved != _dt.date.today().isoformat()

    def get_chain_raw(self) -> List[Dict]:
        """워커에게 전달할 체인 복사본 반환 (메인 스레드와 공유 없음)."""
        return list(self._chain_raw)

    def mark_refresh_started(self) -> None:
        """워커 기동 직전 호출 — 인터벌 내 재기동 방지.

        [612차] `time.time()` → `time.monotonic()`. is_due() 와 **같은 시계**를
        써야 한다 — 섞으면 시스템 시계 보정이 그대로 경과시간 오차가 된다.
        """
        self._last_refresh = time.monotonic()

    # ── 워커 완료 수신 (메인 스레드, Qt 시그널) ───────────────────

    def on_worker_done(self, feats: Dict, chain_raw: List[Dict]) -> None:
        """
        OptionChainWorker.result_ready 수신 시 호출 (메인 스레드).

        chain_raw가 빈 list일 때 _chain_raw를 갱신하지 않는다
        → 다음 워커가 CpOptionCode 재수집하도록 강제.
        """
        if chain_raw:
            self._chain_raw = chain_raw
            # [612차] 워커가 재수집에 성공했으면 `_save_chain_cache`가 방금 파일을
            # 다시 썼다. 590KB JSON 을 매번 파싱하지 않고 mtime 날짜만 다시 읽는다.
            self._chain_saved_at = self._cache_mtime_date()
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
            # [612차] `saved_at` 은 612차부터 기록된다. 그 이전에 쓰인 캐시에는 없고,
            # 그때는 파일 mtime 으로 떨어진다 — 둘 다 없으면 chain_reload_due()가 True.
            self._chain_saved_at = data.get("saved_at") or self._cache_mtime_date()
            return data.get("chain", [])
        except Exception:
            self._chain_saved_at = None
            return []

    def _cache_mtime_date(self) -> Optional[str]:
        """캐시 파일 수정일(YYYY-MM-DD). 파일이 없으면 None."""
        try:
            return _dt.date.fromtimestamp(
                os.path.getmtime(self.cache_path)
            ).isoformat()
        except Exception:
            return None

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
