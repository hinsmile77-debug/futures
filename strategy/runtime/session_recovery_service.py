from __future__ import annotations

import datetime
import logging
from typing import Any

from PyQt5.QtCore import QTimer

from logging_system.log_manager import log_manager
from utils.db_utils import fetch_today_trades

logger = logging.getLogger("SYSTEM")


class SessionRecoveryService:
    """Restore session counters, daily trade history, and startup panels."""

    def restore_on_startup(self, system: Any) -> None:
        system._session_no = self.increment_session(system)
        self.restore_daily_state(system)
        QTimer.singleShot(500, lambda: self.restore_panels_from_history(system))

    def increment_session(self, system: Any) -> int:
        data = system._read_session_state()
        today = datetime.date.today().isoformat()
        if data.get("date") != today:
            data = {
                "date": today,
                "count": 0,
                "reverse_entry_enabled": bool(data.get("reverse_entry_enabled", False)),
                "tp1_single_contract_mode": str(
                    data.get("tp1_single_contract_mode", "breakeven") or "breakeven"
                ).strip().lower(),
                "auto_shutdown_done_date": "",
            }

        data["count"] = data.get("count", 0) + 1
        data["reverse_entry_enabled"] = bool(system._reverse_entry_enabled)
        data["tp1_single_contract_mode"] = str(
            getattr(system, "_tp1_protect_mode", "breakeven") or "breakeven"
        ).strip().lower()
        system._write_session_state(data)
        return int(data["count"])

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
