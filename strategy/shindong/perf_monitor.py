# -*- coding: utf-8 -*-
"""[MW0601 717차 후속 / F-3 · G-4 — 사용자 승인 2026-10-26] 신동 경로 소요시간 · 건강 지표.

계기: 2026-10-26 「정규 재생 대조 60초 미갱신」 134회(12:50–15:04, 매분 1회 · 전부 정확히 60초 ·
매번 직후 「수집 회복」). 옵션흐름 수집이 실패했다는 문구와 달리 **수집은 매분 성공**했고, 수급
타이머 주기(60초)와 대체 대조 문턱(60초)이 같아 2초 폴링이 타이머보다 먼저 문턱을 밟는 경합이
의심된다. 이 모듈은 그 판정에 필요한 숫자만 모은다 — **판정·주문·수량에는 관여하지 않는다**(관찰 전용).

- 구간 소요시간(ms): `flow`(7222 수집) · `replay`(신동 재생) · `exec`(정규 집행 단계) ·
  `reconcile`(2초 슬롯 대체 대조 = DB 적재 + 보유 분기)
- 정규 대조 간격(초): 직전 정규 대조 → 이번 정규 대조. 60초 근방에 붙어 있으면 경합이다.
- 대체 대조 횟수: 문턱을 밟은 횟수.

요약은 `[ShindongPerf]` 한 줄로 주기마다 낸다. 표본이 없는 항목은 「미측정」(0 이 아니다 — 계측 4원칙 ②).
표준 라이브러리만 · Python 3.7 호환.
"""
from __future__ import annotations

import datetime as _dt

SECTIONS = ("flow", "replay", "exec", "reconcile")


class ShindongPerf(object):
    """하루 단위 누적. 날짜가 바뀌면 스스로 비운다."""

    def __init__(self, summary_every_sec: float = 600.0):
        self.summary_every_sec = float(summary_every_sec)
        self._day = None
        self._ms = {k: [] for k in SECTIONS}
        self._sync_gaps = []          # 정규 대조 간격(초)
        self._last_regular = None     # 직전 정규 대조 시각
        self._fallback_n = 0
        self._last_summary = None

    def _roll(self, now: _dt.datetime) -> None:
        d = now.date()
        if self._day != d:
            self._day = d
            self._ms = {k: [] for k in SECTIONS}
            self._sync_gaps = []
            self._last_regular = None
            self._fallback_n = 0
            self._last_summary = None

    def record_ms(self, section: str, ms: float, now: _dt.datetime) -> None:
        self._roll(now)
        if section in self._ms:
            self._ms[section].append(float(ms))

    def mark_regular_sync(self, now: _dt.datetime) -> None:
        self._roll(now)
        if self._last_regular is not None:
            self._sync_gaps.append((now - self._last_regular).total_seconds())
        self._last_regular = now

    def mark_fallback(self, now: _dt.datetime) -> None:
        self._roll(now)
        self._fallback_n += 1

    def summary_due(self, now: _dt.datetime) -> bool:
        self._roll(now)
        if self._last_summary is None:
            self._last_summary = now
            return False
        return (now - self._last_summary).total_seconds() >= self.summary_every_sec

    @staticmethod
    def _stat(xs, fmt):
        if not xs:
            return "미측정"
        s = sorted(xs)
        med = s[len(s) // 2]
        return ("n=%d 중앙 " + fmt + " 최대 " + fmt) % (len(s), med, s[-1])

    def snapshot(self) -> dict:
        gaps = self._sync_gaps
        near60 = sum(1 for g in gaps if 59.0 <= g <= 62.0)
        return {
            "ms": {k: list(v) for k, v in self._ms.items()},
            "sync_gaps": list(gaps),
            "sync_gaps_near60": near60,
            "fallback_n": self._fallback_n,
        }

    def format_summary(self, now: _dt.datetime) -> str:
        self._roll(now)
        self._last_summary = now
        parts = ["%s %s" % (k, self._stat(self._ms[k], "%.0fms")) for k in SECTIONS]
        gaps = self._sync_gaps
        near60 = sum(1 for g in gaps if 59.0 <= g <= 62.0)
        return ("[ShindongPerf] %s 누적 — %s | 정규 대조 간격 %s (59–62초 %d/%d) | 대체 대조 %d회"
                % (now.strftime("%H:%M"), " · ".join(parts), self._stat(gaps, "%.1f초"),
                   near60, len(gaps), self._fallback_n))
