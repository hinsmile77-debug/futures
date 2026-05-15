from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Any, List

from PyQt5.QtCore import QTimer

from config.constants import get_contract_spec
from logging_system.log_manager import log_manager
from utils.time_utils import is_market_open

logger = logging.getLogger("SYSTEM")


@dataclass
class BrokerRuntimeContext:
    selected_account: str
    accounts: List[str]
    acc_raw: str
    server_label: str
    code: str
    market_open_now: bool


class BrokerRuntimeService:
    """Prepare broker runtime bootstrap state and start realtime/investor loops."""

    def login_and_prepare(self, system: Any) -> BrokerRuntimeContext | None:
        print("[DBG CK-1] login() 호출 직전", flush=True)
        if not system.broker.connect():
            logger.error("[System] 브로커 로그인 실패")
            return None

        system.broker.register_fill_callback(system._on_chejan_event)
        system.broker.register_msg_callback(system._on_order_message)
        system.kiwoom = system.broker.api

        acc_raw = system.broker.get_login_info("ACCNO")
        accounts = system.broker.get_account_list()
        selected_account = self._select_account(system, accounts)

        logger.info("[Account] ACCNO raw=%s", acc_raw)
        logger.info("[Account] parsed accounts=%s", accounts)
        system.dashboard.set_account_options(accounts, selected_account)
        print("[DBG CK-2] login() 성공", flush=True)

        broker_name = getattr(system.broker, "name", "")
        if broker_name == "cybos":
            server_label = "Cybos 실서버"
        else:
            server = system.broker.get_login_info("GetServerGubun")
            server_label = "모의투자" if server == "1" else "실서버"
            if server == "1":
                logger.info("[System] 모의투자 서버 접속 - A0166000 SetRealReg 실시간 수신 사용")
        print(f"[DBG CK-2b] broker={broker_name!r} 서버종류={server_label}", flush=True)

        code, broker_code, ui_code_raw, ui_code, is_mini = self._resolve_trade_code(system)
        print(
            f"[DBG CK-3] 금월물코드={code} (broker={broker_code} ui_raw={ui_code_raw!r} "
            f"ui={ui_code!r} is_mini={is_mini}) 서버={server_label}",
            flush=True,
        )

        system._futures_code = code
        spec = get_contract_spec(code)
        system._pt_value = spec["pt_value"]
        system.position.set_pt_value(system._pt_value)
        system.position.set_futures_code(code)
        system.sizer.set_pt_value(system._pt_value)
        print(f"[DBG CK-3b] 계약스펙={spec['label']} pt_value={system._pt_value:,}", flush=True)

        now = datetime.datetime.now()
        market_open_now = is_market_open(now)
        return BrokerRuntimeContext(
            selected_account=selected_account,
            accounts=accounts,
            acc_raw=str(acc_raw or ""),
            server_label=server_label,
            code=code,
            market_open_now=market_open_now,
        )

    def start_realtime_and_investor(self, system: Any, code: str, market_open_now: bool) -> None:
        system.realtime_data = system.broker.create_realtime_data(
            code=code,
            screen_no="3000",
            on_candle_closed=system._on_candle_closed,
            on_tick=system._on_tick_price_update,
            on_hoga=system._on_hoga_update,
            realtime_code=code,
            is_mock_server=False,
        )
        print("[DBG CK-4] RealtimeData 생성 완료", flush=True)

        now = datetime.datetime.now()
        if not market_open_now:
            log_manager.system(
                f"[System] 장외 시간({now.strftime('%H:%M:%S')})에는 Cybos 실시간 구독을 시작하지 않음",
                "INFO",
            )
            print("[DBG CK-5] RealtimeData.start() skipped (market closed)", flush=True)

        system.investor_data._api = system.broker.api
        system.investor_data.set_futures_code(code)
        system.broker.probe_investor_ticker(extra_codes=[code])

        system._investor_timer = QTimer()
        system._investor_timer.timeout.connect(system._fetch_investor_data)
        if market_open_now:
            self.ensure_market_open_runtime_started(system, reason="initial_connect")
        else:
            logger.info("[System] %s 장외 대기모드 - %s | 실시간/수급 루프는 09:00 이후 자동 시작", system.broker.name, code)

    def ensure_market_open_runtime_started(self, system: Any, reason: str = "market_open") -> None:
        """Ensure live subscriptions are active once the market opens."""
        realtime_data = getattr(system, "realtime_data", None)
        if realtime_data is not None and not self._is_realtime_running(realtime_data):
            realtime_data.start(load_history=True)
            print("[DBG CK-5] RealtimeData.start() 완료", flush=True)
            logger.info(
                "[System] %s realtime start triggered (%s) code=%s",
                system.broker.name,
                reason,
                getattr(realtime_data, "code", ""),
            )

        investor_timer = getattr(system, "_investor_timer", None)
        if investor_timer is not None and not investor_timer.isActive():
            investor_timer.start(60_000)
            logger.info(
                "[System] %s investor timer start triggered (%s) code=%s interval=60s",
                system.broker.name,
                reason,
                getattr(system, "_futures_code", ""),
            )
            system._fetch_investor_data()

    @staticmethod
    def _is_realtime_running(realtime_data: Any) -> bool:
        return bool(getattr(realtime_data, "_running", False))

    @staticmethod
    def _normalize_ui_code(ui_code_raw: str) -> str:
        if len(ui_code_raw) == 8 and ui_code_raw.endswith("000"):
            return ui_code_raw[:-3]
        return ui_code_raw

    def _resolve_trade_code(self, system: Any):
        """선택된 종목코드를 확정한다.

        미니선물(A05xxx)과 일반선물(A01xxx) 모두 FutureMst BlockRequest 프로브로 근월물을 확정한다.
        UI 저장값(ui_prefs.json)은 만기된 계약코드일 수 있으므로 프로브 결과를 우선한다.
        확정된 코드로 대시보드 콤보를 동기화한다.
        """
        broker_code = system.broker.get_nearest_futures_code()
        try:
            ui_code_raw = str(system.dashboard.get_selected_symbol() or "").strip()
        except Exception as sym_error:
            logger.debug("[Symbol] get_selected_symbol 실패: %s", sym_error)
            ui_code_raw = ""

        ui_code = self._normalize_ui_code(ui_code_raw)
        ui_norm = ui_code[1:] if ui_code.startswith("A") else ui_code
        is_mini_selected = ui_norm.startswith("05")

        if is_mini_selected:
            # 미니선물(A05xxx): FutureMst 프로브로 근월물 확정 — UI 저장값 무시
            probed = system.broker.get_nearest_mini_futures_code()
            if probed:
                if probed != ui_code:
                    logger.warning(
                        "[CodeRoll] 미니선물 코드 교체: UI=%s → 근월물=%s (만기 롤오버)",
                        ui_code, probed,
                    )
                code = probed
            else:
                logger.warning("[CodeRoll] 미니선물 프로브 실패 — UI 코드 사용: %s", ui_code)
                code = ui_code
        else:
            # 일반선물(A01xxx): FutureMst 프로브로 근월물 검증 — 만기 롤오버 자동 처리
            probed = system.broker.get_nearest_normal_futures_code()
            if probed:
                if probed != ui_code:
                    logger.warning(
                        "[CodeRoll] 일반선물 코드 교체: UI=%s → 근월물=%s (만기 롤오버)",
                        ui_code, probed,
                    )
                code = probed
            else:
                logger.warning(
                    "[CodeRoll] 일반선물 프로브 실패 — CpFutureCode/UI 사용: broker=%s ui=%s",
                    broker_code, ui_code,
                )
                code = broker_code or ui_code

        # 확정된 코드로 대시보드 콤보 동기화
        if code:
            try:
                system.dashboard.set_selected_symbol(code)
            except Exception as e:
                logger.debug("[CodeRoll] 대시보드 동기화 실패: %s", e)

        return code, broker_code, ui_code_raw, ui_code, is_mini_selected

    def check_rollover(self, system: Any) -> bool:
        """장중 롤오버 감시 — 현재 코드가 만기됐으면 WARNING 로그 + UI 갱신.

        15:10 강제청산으로 포지션이 이미 정리된 후라도 실시간 구독은 구 코드로 남아 있다.
        실시간 재구독은 다음 기동 시 자동으로 처리되므로 여기서는 알림만 낸다.
        Returns True if rollover detected.
        """
        current_code = getattr(system, "_futures_code", "")
        if not current_code:
            return False

        norm = current_code[1:] if current_code.startswith("A") else current_code
        is_mini = norm.startswith("05")

        try:
            if is_mini:
                probed = system.broker.get_nearest_mini_futures_code()
            else:
                probed = system.broker.get_nearest_normal_futures_code()
        except Exception as exc:
            logger.debug("[RolloverWatch] 프로브 실패: %s", exc)
            return False

        if not probed or probed == current_code:
            return False

        log_manager.system(
            "[RolloverWatch] 만기 롤오버 감지: 현재={curr} → 신규={new}"
            " — 15:10 강제청산 후 재기동 시 자동 전환됩니다".format(
                curr=current_code, new=probed
            ),
            "WARNING",
        )
        try:
            system.dashboard.set_selected_symbol(probed)
        except Exception as e:
            logger.debug("[RolloverWatch] 대시보드 동기화 실패: %s", e)
        return True

    @staticmethod
    def _select_account(system: Any, accounts: List[str]) -> str:
        from config import secrets as _secrets

        selected_account = str(_secrets.ACCOUNT_NO or "").strip()
        if accounts and selected_account not in accounts:
            fallback_account = str(accounts[0]).strip()
            logger.warning(
                "[Account] configured account %s not in broker session accounts=%s; using %s",
                selected_account,
                accounts,
                fallback_account,
            )
            selected_account = fallback_account
            system._apply_account_no(selected_account)
        return selected_account
