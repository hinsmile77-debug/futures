from __future__ import annotations

import datetime
import logging
from typing import Any

from PyQt5.QtCore import QTimer

from logging_system.log_manager import log_manager
from utils.db_utils import (fetch_today_trades, sum_today_system_net_krw,
                            system_leg_details)

logger = logging.getLogger("SYSTEM")


class SessionRecoveryService:
    """Restore session counters, daily trade history, and startup panels."""

    def restore_on_startup(self, system: Any) -> None:
        system._session_no = self.increment_session(system)
        self.restore_daily_state(system)
        # restore_panels_from_history의 DB 쿼리(_gather_efficacy_stats 등)를
        # 백그라운드 스레드에서 실행 후 Qt 메인 스레드에서 UI 업데이트 적용.
        # 메인 스레드에서 직접 실행 시 4s+ 블로킹 → _tick_header 지연 → live 멈춤.
        QTimer.singleShot(500, lambda: self._restore_panels_bg(system))

    def _restore_panels_bg(self, system: Any) -> None:
        import threading as _thr
        _thr.Thread(target=self._restore_panels_worker, args=(system,), daemon=True).start()

    def _restore_panels_worker(self, system: Any) -> None:
        """restore_panels_from_history의 무거운 DB 쿼리를 백그라운드에서 실행."""
        from PyQt5.QtCore import QTimer as _QTimer
        import time as _t
        _t0 = _t.monotonic()
        try:
            learning  = system._gather_learning_stats()
            efficacy  = system._gather_efficacy_stats()
            trend     = system._gather_trend_stats()
        except Exception as _e:
            import logging as _log
            _log.getLogger("SYSTEM").warning("[Restore] 패널 데이터 수집 실패: %s", _e)
            learning, efficacy, trend = None, None, None
        _gather_ms = (_t.monotonic() - _t0) * 1000
        import logging as _log
        _log.getLogger("SYSTEM").debug(
            "[LiveDBG] _restore_panels_worker DB 수집 %.0fms", _gather_ms
        )
        if _gather_ms > 2000:
            _log.getLogger("SYSTEM").warning(
                "[LiveDBG] _restore_panels_worker 지연 %.0fms — live 중단 원인 분석용",
                _gather_ms,
            )
        # UI 업데이트는 메인 스레드에서 실행 — 4단계 QTimer 체인
        # 이유: 기존 단일 _apply()는 update_learning+efficacy+trend+pnl_history 합산 ~14초
        #   → 메인 스레드 14,828ms 블로킹 실증(6/26 09:23, 재시작 직후 CB⑤ 위험)
        # 각 단계 사이 10ms 양보 → _tick_header가 중간에 발화해 블로킹 검출 간격 ≤4s로 분산.
        import time as _ta
        _log.getLogger("SYSTEM").warning("[LiveDBG] _apply 시작 (4단계 체인)")

        def _stage4():
            try:
                _s = _ta.monotonic()
                system._refresh_pnl_history()
                _log.getLogger("SYSTEM").warning("[LiveDBG] _apply pnl_history %.0fms 총%.0fms",
                                                 (_ta.monotonic()-_s)*1000, (_ta.monotonic()-_t0)*1000)
            except Exception as _ue:
                _log.getLogger("SYSTEM").debug("[Restore] pnl_history 실패: %s", _ue)

        def _stage3():
            try:
                _s = _ta.monotonic()
                if trend:
                    system.dashboard.update_trend(trend)
                _log.getLogger("SYSTEM").warning("[LiveDBG] _apply update_trend %.0fms", (_ta.monotonic()-_s)*1000)
            except Exception as _ue:
                _log.getLogger("SYSTEM").debug("[Restore] update_trend 실패: %s", _ue)
            _QTimer.singleShot(10, _stage4)

        def _stage2():
            try:
                _s = _ta.monotonic()
                if efficacy:
                    system.dashboard.update_efficacy(efficacy)
                _log.getLogger("SYSTEM").warning("[LiveDBG] _apply update_efficacy %.0fms", (_ta.monotonic()-_s)*1000)
            except Exception as _ue:
                _log.getLogger("SYSTEM").debug("[Restore] update_efficacy 실패: %s", _ue)
            _QTimer.singleShot(10, _stage3)

        def _stage1():
            try:
                _s = _ta.monotonic()
                if learning:
                    system.dashboard.update_learning(learning)
                _log.getLogger("SYSTEM").warning("[LiveDBG] _apply update_learning %.0fms", (_ta.monotonic()-_s)*1000)
            except Exception as _ue:
                _log.getLogger("SYSTEM").debug("[Restore] update_learning 실패: %s", _ue)
            _QTimer.singleShot(10, _stage2)

        # 🔴 [MW0601 504차 후속] 여기는 **워커 스레드**다(_restore_panels_bg 가
        # threading.Thread 로 띄운다). 그 스레드에는 Qt 이벤트 루프가 없어서
        # `QTimer.singleShot(0, _stage1)` 이 **한 번도 발화하지 않았다** — 타이머는
        # 호출한 스레드에 붙는데 그 스레드가 이벤트 루프를 돌리지 않기 때문이다.
        #
        # 증상: `[LiveDBG] _apply 시작 (4단계 체인)` 은 매 기동마다 찍히는데
        # `_apply update_learning`·`update_efficacy`·`update_trend`·`pnl_history`
        # 완료 로그가 **전 기간 로그에 단 한 줄도 없다**(2026-08-31 전수 확인).
        # ⇒ 기동 시 패널 4종(자가학습·효과검증·추이·손익추이)이 복원된 적이 없다.
        # 거래일에는 이후 이벤트 구동 갱신(_record_trade_result·daily_close 등)이
        # 채워줘서 드러나지 않았고, 거래가 없는 날에만 빈 화면으로 보였다.
        # (재현: 워커 스레드에서 singleShot 예약 → 발화 False / 메인 → True)
        #
        # 고치는 방법은 304차 후속이 만들고 490차 F-L 이 helper 로 감싼 통로를
        # 그대로 쓰는 것이다 — 새 기전을 만들지 않는다. `_stage1` 이 메인 스레드에서
        # 돌기 시작하면 그 안의 `singleShot(10, _stage2)` 는 정상 동작한다.
        system._dashboard_call(_stage1)

    # ── [MW0601 538차 / G-1 + F-1 보강 계측] 날짜 전환 자체를 로그로 남긴다 ──────
    # 아래 `increment_session()` 의 날짜 전환 분기는 새 딕셔너리를 **통째로** 만든다.
    # 그래서 전날 EOD 가 써둔 완료 마커 2종이 여기서 조용히 사라진다는 것이 유력
    # 가설이었는데(0904·0907 리포트 이상점 1-1), 532차가 그 가설의 확인 수단으로
    # 사전등록한 `main.py:_write_session_state()` 의 `[SessionStateDrop]` WARNING 은
    # 09-03·09-04·09-07 **세 거래일 연속 한 번도 나오지 않았다**(0907 리포트 1-4).
    # 532차 자신의 문구대로 읽으면 그 부재는 "원인이 다른 곳"이라는 신호인데,
    # 0907 장전은 재현 횟수만으로 "확정"을 선언했다 — 판정 근거가 갈린 상태다.
    #
    # 그래서 여기서 하는 일은 **원인을 고치는 것이 아니라 전환 순간을 직접 재는 것**
    # 뿐이다. F-1 본체(마커 이어받기)는 사용자 승인 대기다(0907 리포트 「사용자 조치 3」).
    # 이어받은 키와 버려진 키를 **양쪽 다** 남기므로(계측 4원칙 ⑤ — 대사는 모든 축을
    # 건다), 다음 기동 로그 한 줄로 "여기서 지워지는가 / 다른 곳인가"가 갈린다.
    #
    # ⚠ 동작은 바꾸지 않는다 — 버려지던 키는 이 변경 뒤에도 똑같이 버려진다.
    # ⚠ 사각지대 하나는 남는다: `_read_session_state()` 가 파일 읽기에 실패하면
    #   **오늘 날짜**를 담은 기본 dict 를 돌려주므로 이 분기 자체를 타지 않는다.
    #   그 경우는 여기서 관측되지 않는다(고치려면 읽기 폴백을 바꿔야 하는데 그것은
    #   동작 변경이라 이 계측 작업의 범위 밖이다 — 계측 4원칙 ④의 미해소 잔여분).
    _MARKER_KEYS = ("p8_last_success_date", "eod_retrain_ok_date")

    def increment_session(self, system: Any) -> int:
        data = system._read_session_state()
        today = datetime.date.today().isoformat()
        if data.get("date") != today:
            prev = data
            data = {
                "date": today,
                "count": 0,
                "reverse_entry_enabled": bool(data.get("reverse_entry_enabled", False)),
                "tp1_single_contract_mode": str(
                    data.get("tp1_single_contract_mode", "atr_profit") or "atr_profit"
                ).strip().lower(),
                "auto_shutdown_done_date": "",
            }
            self._log_session_rollover(prev, data)

        data["count"] = data.get("count", 0) + 1
        data["reverse_entry_enabled"] = bool(system._reverse_entry_enabled)
        data["tp1_single_contract_mode"] = str(
            getattr(system, "_tp1_protect_mode", "atr_profit") or "atr_profit"
        ).strip().lower()
        system._write_session_state(data)
        return int(data["count"])

    def _log_session_rollover(self, prev: dict, new: dict) -> None:
        """[MW0601 538차 / G-1] 날짜 전환 시 이어받은 키·버려진 키를 남긴다.

        정상 전환도 INFO 로 남긴다 — "무엇이 사라졌는가"는 사라진 뒤만 봐서는 알 수
        없고, 직전에 무엇이 있었는지가 같은 줄에 있어야 특정된다(532차 G-1 과 같은 취지).

        ⚠ 로그는 모듈 로거(`logger`)로만 낸다. `log_manager` 로 WARNING 을 내면
          `exceptions_10m` 에 합산돼 헬스 degraded 를 자체 유발한다(F-17 전례).
        ⚠ 이 함수는 어떤 예외도 밖으로 내보내지 않는다 — 계측이 기동을 막으면 안 된다.
        """
        try:
            prev_date = str(prev.get("date") or "미측정")
            new_date = str(new.get("date") or "미측정")
            prev_keys = set(prev.keys())
            new_keys = set(new.keys())
            carried = sorted(prev_keys & new_keys)
            dropped = sorted(prev_keys - new_keys)
            logger.info(
                "[SessionRollover] %s → %s 전환 — 이어받은 키(%d개)=%s / "
                "새로 초기화된 키(%d개)=%s",
                prev_date, new_date,
                len(carried), (carried or "없음"),
                len(dropped), (dropped or "없음"),
            )
            lost = [k for k in self._MARKER_KEYS if prev.get(k) and not new.get(k)]
            if lost:
                logger.warning(
                    "[SessionStateDrop] 완료 마커 소실 %s — 날짜 전환(%s → %s)이 새 "
                    "딕셔너리를 만들면서 이어받지 않았다 (호출부=%s). F-1 미적용 "
                    "상태에서는 이것이 현재 동작이며, 이 줄의 출현 자체가 0907 리포트 "
                    "이상점 1-4(판정 근거 정합성)의 확인 수단이다",
                    lost, prev_date, new_date,
                    "session_recovery_service.py:increment_session",
                )
        except Exception as _roll_e:
            logger.debug("[SessionRollover] 전환 계측 실패(무해): %s", _roll_e)

    def restore_daily_state(self, system: Any) -> None:
        today_str = datetime.date.today().isoformat()
        rows = fetch_today_trades(today_str)
        if not rows:
            return

        session_no = int(getattr(system, "_session_no", 0) or 0)
        system.dashboard.append_trade_separator(
            f"── 세션 #{session_no} 시작 — 이전 거래 {len(rows)}건 복원 ({today_str}) ──"
        )
        system.dashboard.append_pnl_separator(
            f"── 세션 #{session_no} 시작 — 이전 거래 {len(rows)}건 복원 ({today_str}) ──"
        )

        cumulative_pnl_krw = 0.0
        cumulative_forward_pnl_krw = 0.0
        for row in rows:
            direction = row["direction"] or "?"
            entry_p = row["entry_price"] or 0.0
            exit_p = row["exit_price"]
            qty = row["quantity"] or 1
            pnl_pts = row["pnl_pts"] or 0.0
            pnl_krw = row["pnl_krw"] or 0.0
            forward_pnl_pts = row["forward_pnl_pts"] or pnl_pts
            forward_pnl_krw = row["forward_pnl_krw"] or pnl_krw
            reason = row["exit_reason"] or ""
            grade = row["grade"] or ""
            entry_ts = (row["entry_ts"] or "")[:16]
            exit_ts = (row["exit_ts"] or "")[:16]

            if exit_p is not None:
                cumulative_pnl_krw += pnl_krw
                cumulative_forward_pnl_krw += forward_pnl_krw
                system.dashboard.append_restore_trade(
                    msg=f"진입 {direction} {qty}계약 @ {entry_p:.2f}  등급={grade}",
                    ts=entry_ts[11:] if len(entry_ts) > 11 else entry_ts,
                )
                system.dashboard.append_restore_trade(
                    msg=f"청산 {direction} {qty}계약 @ {exit_p:.2f}  ({reason})",
                    ts=exit_ts[11:] if len(exit_ts) > 11 else exit_ts,
                    val=(
                        f"실행 {pnl_pts:+.2f}pt  {pnl_krw:+,.0f}원 | "
                        f"순방향 {forward_pnl_pts:+.2f}pt  {forward_pnl_krw:+,.0f}원"
                    ),
                )
                system.dashboard.append_restore_pnl(
                    msg=f"청산 | {direction} {qty}계약 @ {exit_p:.2f}  ({reason})",
                    ts=exit_ts[11:] if len(exit_ts) > 11 else exit_ts,
                    val=(
                        f"실행 {pnl_pts:+.2f}pt  {pnl_krw:+,.0f}원 (누적 {cumulative_pnl_krw:+,.0f}원) | "
                        f"순방향 {forward_pnl_pts:+.2f}pt  {forward_pnl_krw:+,.0f}원 "
                        f"(누적 {cumulative_forward_pnl_krw:+,.0f}원)"
                    ),
                )
            else:
                system.dashboard.append_restore_trade(
                    msg=f"[미청산] 진입 {direction} {qty}계약 @ {entry_p:.2f}  등급={grade}",
                    ts=entry_ts[11:] if len(entry_ts) > 11 else entry_ts,
                )

        system.position.reset_daily()
        system.position.restore_daily_stats(rows)

        # ── [MW0601 546차] ProfitGuard 판정용 **시스템 한정** 누적기 복원 ──────
        # 라이브 경로는 `_record_trade_result()` 에서 매 청산 레그마다 더하지만,
        # 세션이 재시작되면 그 누적이 통째로 사라진다. 여기서 당일 행으로 1회
        # 복원하지 않으면 재시작 직후 ProfitGuard 가 **당일 손익 0원**으로 판정해
        # 이미 걸렸어야 할 보호가 풀린다(래치 자체는 아래 profit_guard 상태
        # 복원이 살리지만, L1 피크·L2 티어는 이 값으로 다시 계산된다).
        # ⚠ 여기서만 DB 를 읽는다 — 매분 조회는 456차 장중 DB 금지에 걸린다.
        try:
            _sys = sum_today_system_net_krw(rows)
            system._sys_daily_net_krw    = float(_sys["net_krw"])
            system._sys_daily_legs       = int(_sys["legs"])
            system._sys_daily_other_krw  = float(_sys["other_net_krw"])
            system._sys_daily_other_legs = int(_sys["other_legs"])
            system._sys_daily_date       = today_str
            # [MW0601 556차 후속 / G-4] 래치 스냅샷 원장도 함께 복원한다.
            # 합계만 되살리고 원장을 비워 두면, 재기동 직후 걸리는 래치가
            # **매번 「0건(구성 레그 없음)」**이라고 말한다 — 2026-09-10 12:17
            # 재기동 직후의 재latch 가 정확히 그런 경우였다(합계 +6,921,594원이
            # 되살아나 즉시 래치됐는데 그 구성이 어디에도 안 남았다).
            # ⚠ 위 `sum_today_system_net_krw()` 와 **같은 화이트리스트**로 고른다.
            #   여기서 갈리면 스냅샷 구성과 합계가 어긋난다.
            system._sys_daily_legs_detail = system_leg_details(rows)
            # ⚠ `%` 포매팅은 천단위 콤마(`%,.0f`)를 지원하지 않는다 — ValueError.
            #   포맷을 먼저 만들어 넘긴다.
            logger.info(
                "[Restore] ProfitGuard 시스템손익 복원: sys={:+,.0f}원({}레그) "
                "외부={:+,.0f}원({}레그) 출처미기록={}레그".format(
                    _sys["net_krw"], _sys["legs"],
                    _sys["other_net_krw"], _sys["other_legs"], _sys["unknown_legs"])
            )
        except Exception as _sys_e:
            # 복원 실패를 조용히 넘기면 ProfitGuard 가 0원으로 판정한다 —
            # 폴백을 쓴 사실을 남긴다(계측 4원칙 ④).
            logger.warning(
                "[Restore] ProfitGuard 시스템손익 복원 실패 — 0원에서 시작한다: %s", _sys_e)

        # ── ProfitGuard + CircuitBreaker 상태 복원 ────────────────────────────
        # ui_prefs의 state_persist_enabled 플래그가 True일 때만 복원.
        # False 이면 개발/디버그 목적 재시작이므로 상태를 초기화한 채로 유지.
        _state_persist = bool(getattr(system, "_state_persist_enabled", True))
        if _state_persist:
            _session_data = system._read_session_state()
            _today = datetime.date.today().isoformat()
            if _session_data.get("date") == _today:
                _pg_state = _session_data.get("profit_guard_state")
                if _pg_state and hasattr(system, "profit_guard"):
                    try:
                        system.profit_guard.from_state_dict(_pg_state)
                    except Exception as _pge:
                        logger.warning("[Restore] ProfitGuard 상태 복원 실패: %s", _pge)
                _cb_state = _session_data.get("circuit_breaker_state")
                if _cb_state and hasattr(system, "circuit_breaker"):
                    try:
                        system.circuit_breaker.from_state_dict(_cb_state)
                    except Exception as _cbe:
                        logger.warning("[Restore] CircuitBreaker 상태 복원 실패: %s", _cbe)

        daily = system.position.daily_stats()
        forward_daily = system.position.daily_forward_stats()
        system.dashboard.update_pnl_metrics(
            0.0,
            daily["pnl_krw"],
            0.0,
            forward_unrealized_krw=0.0,
            forward_daily_pnl_krw=forward_daily["pnl_krw"],
        )

        logger.info("[Restore] 당일 거래 %d건 복원 완료 | 누적 PnL=%+.0f원", len(rows), cumulative_pnl_krw)
        log_manager.system(
            f"재시작 복원 완료 | 거래 {len(rows)}건 | 누적 PnL={cumulative_pnl_krw:+,.0f}원"
        )
        system._refresh_pnl_history()

    def restore_panels_from_history(self, system: Any) -> None:
        try:
            system.dashboard.update_learning(system._gather_learning_stats())
        except Exception as exc:
            logger.debug("[Restore] 자가학습 패널 선조회 실패: %s", exc)
        try:
            system.dashboard.update_efficacy(system._gather_efficacy_stats())
        except Exception as exc:
            logger.debug("[Restore] 효과검증 패널 선조회 실패: %s", exc)
        try:
            system.dashboard.update_trend(system._gather_trend_stats())
        except Exception as exc:
            logger.debug("[Restore] 추이 패널 선조회 실패: %s", exc)
        try:
            system._refresh_pnl_history()
        except Exception as exc:
            logger.debug("[Restore] 손익 추이 패널 선조회 실패: %s", exc)
