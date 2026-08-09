# -*- coding: utf-8 -*-
"""수집 원천이 **실제로 채운 키**를 추적해 '유령 필드'를 조기 경보한다.

## 왜 필요한가 — 2026-08-09(451차) 사고

`Dscbo1.CpSvr8111`(프로그램매매 종합매매현황)은 프로그램매매를 **차익/비차익**으로만
분해한다. 투자자별(개인·기관·외인) 필드는 이 TR에 **존재하지 않는다**. 그런데 소비
계층이 `nets.get(key, 기존값)` 폴백으로 스키마를 억지로 완성하면서
`program_individual_net_krw` / `program_institution_net_krw`를 상수 0으로 매분 emit했고,
동시에 `quality_investor_program_supported = 1`을 보고했다.

바깥에서 보면 **"수집 성공 + 값 0"** 이라 정상 시장 상황과 구분되지 않는다. 그래서
2개월 넘게(2026-05~07) 아무도 알아채지 못했고, Phase 0 감사에서야 드러났다.

## 원칙

> **수집 계층은 원천이 실제 제공한 키만 emit한다.**
> 스키마 모양을 맞추려고 `.get(key, 0)` 폴백을 두지 않는다.

폴백이 정당한 경우(예: 이번 조회가 실패했을 때 **직전 성공값**을 유지하는 연속성
목적)에는 이 추적기를 붙인다. "이번엔 안 왔다"와 "한 번도 온 적이 없다"는 전혀 다른
상태인데, 폴백은 둘을 똑같이 보이게 만든다 — 추적기가 후자만 골라 경보한다.

## 사용

    tracker = ProvenanceTracker("CybosProgram", warn_after=10)
    ...
    tracker.observe(nets.keys())                       # 매 조회
    tracker.maybe_warn(logger, EXPECTED_KEYS, supported)

경보는 **키 조합당 1회만** 나간다(로그 폭주 방지). 이 모듈은 어떤 경우에도 예외를
올리지 않는다 — 감시 도구가 수집 경로를 죽이면 안 된다.

관련: `scripts/feature_health_report.py`의 PHANTOM 판정(오프라인 상시 감시).
이쪽은 당일 라이브 카나리아, 저쪽은 전 피처 일괄 그물이다.
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Set


class ProvenanceTracker:
    """원천이 채운 적 있는 키의 합집합을 누적한다."""

    def __init__(self, name: str, warn_after: int = 10) -> None:
        self.name = name
        self.warn_after = max(int(warn_after), 1)
        self.observations = 0
        self.seen: Set[str] = set()
        self._warned: Set[str] = set()

    def observe(self, provided_keys: Optional[Iterable[str]]) -> List[str]:
        """이번 조회가 실제로 채운 키를 기록하고, **처음 본 키**를 반환한다.

        (값이 0이어도 '채웠다'로 본다 — 유령 필드 판별의 기준은 값이 아니라
        원천이 그 필드를 응답에 담았는지 여부다.)
        """
        fresh: List[str] = []
        try:
            self.observations += 1
            for key in (provided_keys or ()):
                name = str(key)
                if name not in self.seen:
                    self.seen.add(name)
                    fresh.append(name)
        except Exception:
            pass
        return fresh

    def notice_new(self, logger, provided_keys: Optional[Iterable[str]]) -> List[str]:
        """`observe()` + 처음 보는 키가 오면 INFO 1회.

        경보(`maybe_warn`)의 반대 방향이다. "원래 안 오던 필드가 오기 시작했다"는
        원천 교체·서버측 변경의 신호이며, 그 필드로 피처를 되살릴 수 있다는 뜻이라
        놓치면 손해다. 첫 조회의 기준선은 알리지 않는다(전부 '처음'이라 무의미).
        """
        try:
            first_ever = self.observations == 0
            fresh = self.observe(provided_keys)
            if fresh and not first_ever and logger is not None:
                logger.info(
                    "[Provenance] %s: 이전에 없던 키가 원천에서 도착함 → %s. "
                    "관련 피처를 되살릴 수 있는지 확인할 것.",
                    self.name, fresh,
                )
            return fresh
        except Exception:
            return []

    def never_provided(self, expected_keys: Iterable[str]) -> List[str]:
        """`observe()`가 한 번도 본 적 없는 기대 키 목록."""
        try:
            return sorted(k for k in expected_keys if k not in self.seen)
        except Exception:
            return []

    def maybe_warn(
        self,
        logger,
        expected_keys: Iterable[str],
        supported: bool = True,
    ) -> List[str]:
        """표본이 충분히 쌓였는데 여전히 빈 키가 있으면 1회 경보하고 그 목록을 반환한다.

        `supported=False`(원천 자체가 실패 중)면 경보하지 않는다 — 그건 유령 필드가
        아니라 그냥 수집 실패이고, 이미 별도 경로로 보고되고 있다.
        """
        try:
            if not supported or self.observations < self.warn_after:
                return []
            missing = self.never_provided(expected_keys)
            if not missing:
                return []
            sig = ",".join(missing)
            if sig in self._warned:
                return missing
            self._warned.add(sig)
            if logger is not None:
                logger.warning(
                    "[Provenance] %s: 원천이 %d회 응답하는 동안 한 번도 채우지 않은 키 %d개 "
                    "→ %s. 스키마 폴백으로 상수값이 emit되고 있지 않은지 확인할 것 "
                    "(collection/provenance.py 참조).",
                    self.name, self.observations, len(missing), missing,
                )
            return missing
        except Exception:
            return []

    def reset(self) -> None:
        """일일 리셋 — 관측 횟수만 초기화하고 '본 적 있음' 이력은 유지한다.

        이력까지 지우면 매일 아침 경보 카운트다운이 처음부터 다시 시작돼, 하루 안에
        경보 임계에 도달하지 못하는 저빈도 원천에서 영영 경보가 나지 않는다.
        """
        self.observations = 0
