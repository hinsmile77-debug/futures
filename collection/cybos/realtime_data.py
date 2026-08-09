from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from typing import Callable, Deque, Dict, List, Optional

from collection.cybos.api_connector import CybosAPI, _safe_float, _safe_int, _safe_str
from utils.market_state import PRICE_LIMIT_STAGES   # [404차 후속8] 가격제한 3단계

logger = logging.getLogger(__name__)
sys_log = logging.getLogger("SYSTEM")
hoga_log = logging.getLogger("HOGA")

MAX_CANDLES = 500

FUTURE_CUR_ONLY_PROGID = "Dscbo1.FutureCurOnly"
FUTURE_JP_BID_PROGID = "CpSysDib.FutureJpBid"

# ── [MW0601 452차 / QDQ Phase 0] 체결구분 디코딩 ──────────────────────────────
# `Dscbo1.FutureCurOnly` `24_체결구분`은 문자 '1'(매수)/'2'(매도)의 **코드값 49/50을
# 숫자로** 반환한다. 대신 공식 캡처본(`docs/CyBos ref/Excel_Example/FutureCurOnly(SbPb).xls`)
# 이 `24_체결구분 = 50.0`으로 그대로 보여주고, 이 저장소 로그 실측 75,264건도
# `flag=49` 37,156 / `flag=50` 38,108 / 그 외 0건이다 — '1'·'2'는 한 번도 오지 않는다.
#
# 의미는 호가와 대조해 독립 확인했다(로그 44,919건):
#   flag=49 → 체결가=최우선매도호가 30.1% vs 최우선매수호가 1.1%  → 공격적 매수
#   flag=50 → 체결가=최우선매수호가 29.9% vs 최우선매도호가 1.2%  → 공격적 매도
#
# 정수 1/2(코드값 체계에서는 제어문자라 체결구분일 수 없다)도 함께 받는다 —
# 런타임/원천이 바뀌어 문자로 오더라도 견디게 하기 위함이며 49/50과 충돌하지 않는다.
_TRADE_SIDE_MAP = {
    "1": "BUY",  "49": "BUY",
    "2": "SELL", "50": "SELL",
}


def decode_trade_side(raw):
    # type: (object) -> Optional[str]
    """`24_체결구분` → 'BUY' | 'SELL' | None.

    🔴 **판정 불가면 None을 낸다 — 절대 매수로 폴백하지 않는다.**
    그 폴백(`is_buy_tick = price >= 직전가`, 보합틱을 매수로 흡수)이 매수비중
    63% 편향(44거래일 전부 50% 초과)의 원인이며, 그 편향이 CORE 피처 `cvd`를
    98.6% `+1.0` 고착으로 상수화시켰다.
    근거: `docs/Spec for feature/Validation for feature/QDQ_도입_손익분석_및_구현계획_2026-08-09.md` §2 발견 A
    """
    if raw is None:
        return None
    try:
        if isinstance(raw, bool):
            return None
        if isinstance(raw, (int, float)):
            raw = int(raw)
        text = str(raw).strip()
    except Exception:
        return None
    return _TRADE_SIDE_MAP.get(text)


class CybosRealtimeData:
    def __init__(
        self,
        api: CybosAPI,
        code: str,
        screen_no: str = "3000",
        on_candle_closed: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
        on_hoga: Optional[Callable] = None,
        realtime_code: Optional[str] = None,
        is_mock_server: bool = False,
    ):
        del screen_no, is_mock_server

        self.api = api
        self.code = code
        self._rt_code = realtime_code or code
        self._on_candle_closed = on_candle_closed
        self._on_tick = on_tick
        self._on_hoga = on_hoga

        self._candles = deque(maxlen=MAX_CANDLES)
        self._current_bar = None
        self._current_min = None
        self._running = False
        self._last_closed_min: Optional[int] = None  # 중복 BAR-CLOSE 감지용

        self._tick_subscription = None
        self._hoga_subscription = None

        self._last_price = 0.0
        self._last_cum_volume = 0
        self._last_bid1 = 0.0
        self._last_ask1 = 0.0
        self._last_bid_qty = 0
        self._last_ask_qty = 0
        self._last_oi = 0
        self._last_hoga_snapshot = {
            "bid_prices": [],
            "ask_prices": [],
            "bid_qtys": [],
            "ask_qtys": [],
        }
        self._tick_event_count = 0
        self._hoga_event_count = 0
        # ── [MW0601 452차 / QDQ Phase 0] 앵커 계측 상태 (소비 0, 적재 전용) ──────
        # 서버가 주는 정답지 `22_누적체결매도`/`23_누적체결매수`의 봉내 증분을 뽑는다.
        # 공식 캡처본에서 `13_누적거래량(1,525) = 22(342) + 23(1,183)` 항등식이 정확히
        # 성립함을 확인했다 — 즉 우리 분류 결과를 대조할 외부 정답지가 존재한다.
        self._last_cum_buy = 0
        self._last_cum_sell = 0
        # 기준선을 잡았는가. "누적값이 0"과 "아직 못 받았다"를 구분해야 한다 —
        # 그 구분을 잃어서 451차 program_* 유령 피처가 2개월간 안 잡혔다.
        self._anchor_primed = False
        # 원천이 이 필드를 준 적이 있는가. 한 번도 없으면 신규 열은 NULL로 남는다
        # (0으로 채우지 않는다 — `feedback_no_schema_fallback_in_collection`).
        self._anchor_available = False
        self._anchor_reset_count = 0      # 누적값 역행(재접속·세션리셋·월물교체) 횟수
        self._anchor_unavail_warned = False
        self._flag_decoded_ticks = 0      # 체결구분 디코딩 성공 틱 수 (진단용)
        self._flag_unknown_ticks = 0      # 〃 실패 틱 수 — 0이 아니면 원천/파서 재확인
        # [404차 후속6] 당일 상한가/하한가 (FutureMst 스냅샷에서 1회 확보, 0.0=미확보)
        self._upper_limit: float = 0.0
        self._lower_limit: float = 0.0
        self._base_price: float = 0.0   # 기준가격(전일 정산가격) — 단계 유도의 근거

    @property
    def daily_limits(self) -> Dict[str, float]:
        """[404차 후속6] 당일 상한가/하한가. 미확보 시 0.0.

        `_prime_from_snapshot()`이 FutureMst 스냅샷에서 채운다. 인덱스
        (`CYBOS_FUTUREMST_*_IDX`)가 실측 전이면 0.0이 유지되고, 소비처는
        "상한가 정보 없음"으로 처리해 기존 동작을 그대로 유지한다.

        `base`(기준가격 = 전일 정산가격)를 함께 낸다 — **소비처는 이쪽을 우선**해
        지금 유효한 단계를 산출한다. 가격제한폭은 장중에 ±8%→±15%→±20%로 확대되는데
        이 스냅샷은 기동 시(08:45~08:55, 항상 1단계) 1회뿐이라 upper/lower는 확대를
        반영하지 못한다. 기준가격은 하루 동안 고정이라 이 문제가 없다
        (규정 §1·§2, `utils/market_state.effective_price_limits`).
        """
        return {"upper": self._upper_limit, "lower": self._lower_limit,
                "base": self._base_price}

    @property
    def candles(self) -> Deque[Dict]:
        return self._candles

    @property
    def latest_closed(self) -> Optional[Dict]:
        return self._candles[-1] if self._candles else None

    @property
    def current_bar(self) -> Optional[Dict]:
        return self._current_bar

    def get_last_n(self, n: int) -> List[Dict]:
        candles = list(self._candles)
        return candles[-n:] if len(candles) >= n else candles

    def start(self, load_history: bool = True) -> None:
        del load_history

        if self._running:
            return

        # pre_market_setup()에서 이미 _prime_from_snapshot()을 실행한 경우 재호출 스킵.
        # 09:00 정각 BlockRequest 병목을 방지한다 (이상점 2 수정).
        if self._last_price > 0.0:
            sys_log.info(
                "[CybosRT-START] snapshot skipped (pre-warmed) code=%s price=%.2f bid1=%.2f ask1=%.2f",
                self._rt_code,
                self._last_price,
                self._last_bid1,
                self._last_ask1,
            )
        else:
            sys_log.info("[CybosRT-START] snapshot begin code=%s", self._rt_code)
            self._prime_from_snapshot()
            sys_log.info(
                "[CybosRT-START] snapshot end code=%s price=%.2f oi=%d bid1=%.2f ask1=%.2f",
                self._rt_code,
                self._last_price,
                self._last_oi,
                self._last_bid1,
                self._last_ask1,
            )
        sys_log.info("[CybosRT-START] tick subscribe begin code=%s", self._rt_code)
        self._tick_subscription = self.api.create_subscription(
            progid=FUTURE_CUR_ONLY_PROGID,
            input_values={0: self._rt_code},
            owner=self,
            event_name="tick",
            latest=False,
        )
        sys_log.info("[CybosRT-START] tick subscribe end code=%s", self._rt_code)
        sys_log.info("[CybosRT-START] hoga subscribe begin code=%s", self._rt_code)
        self._hoga_subscription = self.api.create_subscription(
            progid=FUTURE_JP_BID_PROGID,
            input_values={0: self._rt_code},
            owner=self,
            event_name="hoga",
            latest=False,
        )
        sys_log.info("[CybosRT-START] hoga subscribe end code=%s", self._rt_code)
        self._running = True
        logger.info("[CybosRT] start code=%s", self._rt_code)

    def stop(self) -> None:
        if not self._running:
            return
        if self._tick_subscription is not None:
            self._tick_subscription.unsubscribe()
            self._tick_subscription = None
        if self._hoga_subscription is not None:
            self._hoga_subscription.unsubscribe()
            self._hoga_subscription = None
        self._running = False
        logger.info("[CybosRT] stop code=%s", self._rt_code)

    def _handle_subscription_event(self, event_name: str, sink) -> None:
        sys_log.debug("[CybosRT-EVENT] dispatch event=%s code=%s", event_name, self._rt_code)
        if event_name == "tick" and self._tick_subscription is not None:
            self._handle_tick(self._tick_subscription.com_object)
        elif event_name == "hoga" and self._hoga_subscription is not None:
            self._handle_hoga(self._hoga_subscription.com_object)

    def _prime_from_snapshot(self) -> None:
        snapshot = self.api.request_futures_snapshot(self._rt_code)
        if not snapshot:
            return
        self._last_price = _safe_float(snapshot.get("price"))
        self._last_cum_volume = _safe_int(snapshot.get("cum_volume"))
        self._last_bid1 = _safe_float(snapshot.get("bid1"))
        self._last_ask1 = _safe_float(snapshot.get("ask1"))
        self._last_bid_qty = _safe_int(snapshot.get("bid_qty1"))
        self._last_ask_qty = _safe_int(snapshot.get("ask_qty1"))
        oi_init = _safe_int(snapshot.get("open_interest", 0))
        if oi_init > 0:
            self._last_oi = oi_init
        # [404차 후속6] 당일 상한가/하한가. 값이 서로 모순되면(상한<=하한, 또는 현재가가
        # 밖에 있음) 잘못된 인덱스를 읽은 것이므로 채택하지 않는다 — 2026-05-10 B51처럼
        # 인덱스 오매핑이 조용히 흘러드는 것을 막는 방어선이다.
        _up = _safe_float(snapshot.get("upper_limit", 0.0))
        _dn = _safe_float(snapshot.get("lower_limit", 0.0))
        _px = _safe_float(snapshot.get("price", 0.0))
        _base = _safe_float(snapshot.get("base_price", 0.0))
        if _up > 0 and _dn > 0 and _up > _dn and (not _px or _dn <= _px <= _up):
            self._upper_limit, self._lower_limit = _up, _dn
            logger.info("[DailyLimit] 상한가=%.2f 하한가=%.2f (현재가=%.2f)", _up, _dn, _px)
        elif _up or _dn:
            logger.warning(
                "[DailyLimit] 값 모순으로 미채택 — upper=%.2f lower=%.2f price=%.2f. "
                "CYBOS_FUTUREMST_*_LIMIT_IDX 인덱스를 재확인할 것"
                "(scripts/probe_cybos_limit_price.py)", _up, _dn, _px)
        # 기준가격은 상·하한과 독립적으로 채택한다 — 실제 판정은 이 값에서 단계를
        # 유도하므로, 상·하한 스냅샷이 모순이어도 기준가격만 있으면 게이트가 동작한다.
        # 교차검증: 상한 스냅샷이 있으면 기준가×1.20과 일치해야 한다(규정 3단계 상한).
        if _base > 0:
            self._base_price = _base
            if _up > 0:
                _expect = _base * (1.0 + PRICE_LIMIT_STAGES[-1])
                if abs(_up - _expect) > max(0.05, _expect * 0.001):
                    logger.warning(
                        "[DailyLimit] 기준가(%.2f)×1.20=%.2f 인데 상한 스냅샷은 %.2f "
                        "— 인덱스 매핑 재확인 필요", _base, _expect, _up)
            logger.info("[DailyLimit] 기준가=%.2f → 1단계 %.2f~%.2f / 3단계 %.2f~%.2f",
                        _base, _base * 0.92, _base * 1.08, _base * 0.80, _base * 1.20)

    def _handle_tick(self, obj) -> None:
        price = _safe_float(obj.GetHeaderValue(1))
        cum_volume = _safe_int(obj.GetHeaderValue(13))
        oi = _safe_int(obj.GetHeaderValue(14))
        raw_tick_time = _safe_str(obj.GetHeaderValue(15))
        tick_time = self._parse_tick_time(raw_tick_time)
        ask1 = _safe_float(obj.GetHeaderValue(18))
        bid1 = _safe_float(obj.GetHeaderValue(19))
        ask_qty1 = _safe_int(obj.GetHeaderValue(20))
        bid_qty1 = _safe_int(obj.GetHeaderValue(21))
        buy_sell_flag = _safe_str(obj.GetHeaderValue(24))

        volume = max(0, cum_volume - self._last_cum_volume) if self._last_cum_volume else 0
        self._last_cum_volume = cum_volume

        # ── [MW0601 452차 / QDQ Phase 0] 앵커·섀도 계측 ────────────────────────
        # 아래 블록은 **읽기와 지역 상태 갱신만** 한다. 기존 volume/buy_vol/sell_vol/
        # is_buy_tick 판정에 일절 영향을 주지 않는다(소비 0). 예외가 나도 신규 열만
        # 비고 틱 처리는 계속되도록 통째로 방어한다 — 감시 코드가 수집을 죽이면 안 된다.
        anchor_d_buy = None
        anchor_d_sell = None
        shadow_side = None
        try:
            anchor_d_buy, anchor_d_sell = self._read_trade_anchor(obj)
            shadow_side = decode_trade_side(obj.GetHeaderValue(24))
            if shadow_side is None:
                self._flag_unknown_ticks += 1
            else:
                self._flag_decoded_ticks += 1
        except Exception:
            sys_log.debug("[CVD-ANCHOR] 계측 실패 — 이번 틱만 건너뜀", exc_info=True)
        if oi > 0:
            self._last_oi = oi

        if bid1 > 0:
            self._last_bid1 = bid1
        if ask1 > 0:
            self._last_ask1 = ask1
        if bid_qty1 > 0:
            self._last_bid_qty = bid_qty1
        if ask_qty1 > 0:
            self._last_ask_qty = ask_qty1

        is_buy_tick = True
        if buy_sell_flag == "2":
            is_buy_tick = False
        elif buy_sell_flag not in ("1", "2"):
            is_buy_tick = price >= self._last_price if self._last_price else True

        self._last_price = price
        bar_ts = tick_time.replace(second=0, microsecond=0)
        bar_min = bar_ts.hour * 60 + bar_ts.minute

        # 버퍼 재생 틱 감지: 체결 시각이 현재보다 90초 이상 오래됐으면 실제 시각 사용.
        # Cybos 재구독 시 버퍼된 과거 틱들이 느린 속도로 재생되면 봉 전환이 영구 차단됨.
        _now = datetime.now()
        _stale_sec = (_now - tick_time).total_seconds()
        if _stale_sec > 90:
            _actual_bar_ts = _now.replace(second=0, microsecond=0)
            _actual_bar_min = _actual_bar_ts.hour * 60 + _actual_bar_ts.minute
            # [stale oscillation 근본 수정 — _last_closed_min 기준 단조증가]
            #
            # 이전 수정(_current_min 기준)의 버그:
            #   _close_current_bar()가 _current_min = None 으로 리셋하므로
            #   봉 전환 직후 다음 stale 틱에서 보정 조건이 항상 False → 역행 봉 재생성.
            #
            # 올바른 기준: _last_closed_min (닫힌 봉의 분 인덱스, None으로 리셋 안 됨).
            #   stale actual_bar_min <= _last_closed_min 이면 이미 닫힌 구간 →
            #   _last_closed_min + 1(현재 진행 중인 봉)으로 교정하여 역행 봉 생성 방지.
            _ref = self._last_closed_min
            if _ref is not None and _actual_bar_min <= _ref:
                _actual_bar_min = _ref + 1
                _actual_bar_ts = _actual_bar_ts.replace(
                    hour=_actual_bar_min // 60,
                    minute=_actual_bar_min % 60,
                )
            sys_log.warning(
                "[CybosRT-STALE] code=%s stale=%.0fs raw_time=%s → actual=%s",
                self._rt_code, _stale_sec,
                tick_time.strftime("%H:%M:%S"),
                _actual_bar_ts.strftime("%H:%M"),
            )
            bar_ts = _actual_bar_ts
            bar_min = _actual_bar_min

        self._tick_event_count += 1
        if self._tick_event_count <= 5 or self._tick_event_count % 100 == 0:
            sys_log.info(
                "[CybosRT-TICK] #%d code=%s raw_time=%s parsed=%s price=%.2f vol=%d "
                "bid1=%.2f ask1=%.2f flag=%s side=%s anchor=%s/%s",
                self._tick_event_count,
                self._rt_code,
                raw_tick_time,
                tick_time.strftime("%H:%M:%S"),
                price,
                volume,
                self._last_bid1,
                self._last_ask1,
                buy_sell_flag,
                # [452차] flag 원값과 디코딩 결과를 나란히 남긴다 — 원천이 코드값(49/50)이
                # 아닌 다른 형태로 바뀌면 side=None이 로그에 바로 드러난다.
                shadow_side or "?",
                anchor_d_buy if anchor_d_buy is not None else "-",
                anchor_d_sell if anchor_d_sell is not None else "-",
            )

        self._update_bar(
            bar_ts=bar_ts,
            bar_min=bar_min,
            price=price,
            volume=volume,
            bid1=self._last_bid1,
            ask1=self._last_ask1,
            bid_q=self._last_bid_qty,
            ask_q=self._last_ask_qty,
            oi=oi,
            is_buy_tick=is_buy_tick,
            anchor_d_buy=anchor_d_buy,
            anchor_d_sell=anchor_d_sell,
            shadow_side=shadow_side,
        )

    def _read_trade_anchor(self, obj):
        # type: (object) -> tuple
        """[MW0601 452차 / QDQ Phase 0] `22_누적체결매도`/`23_누적체결매수` 봉내 증분.

        반환: `(d_buy, d_sell)`. 쓸 수 없으면 `(None, None)`.

        **`0`을 내지 않는다.** 원천이 안 준 것을 0으로 채우면 "정상 수집인데 값이 0"과
        구분되지 않는다 — 451차 `program_*` 유령 피처가 정확히 그 방식으로 2개월간
        숨었다(`feedback_no_schema_fallback_in_collection`).

        누적값 역행은 `max(0, …)`으로 뭉개지 않고 **버리고 기준선만 재설정**한다.
        역행은 재접속·세션 리셋·월물 교체의 신호이고, 이 계층의 목적이 정확한 계측이라
        조용히 0으로 만들면 안 된다. (기존 `volume` 계산은 clamp 방식이지만 그쪽은
        Phase 0의 비목표라 손대지 않는다.)
        """
        # ⚠ 22가 매도, 23이 매수다. 순서를 뒤집으면 부호가 통째로 반전된다.
        cum_sell = _safe_int(obj.GetHeaderValue(22))
        cum_buy = _safe_int(obj.GetHeaderValue(23))

        if cum_buy > 0 or cum_sell > 0:
            self._anchor_available = True
        elif not self._anchor_available:
            # 장 시작 직후 진짜 0일 수 있으므로 여기서 단정하지 않는다.
            # 세션 내내 0이면 _close_current_bar()가 1회만 경고한다.
            return None, None

        d_buy = None
        d_sell = None
        if not self._anchor_primed:
            self._anchor_primed = True          # 기준선만 세우고 이번 증분은 버린다
        else:
            _db = cum_buy - self._last_cum_buy
            _ds = cum_sell - self._last_cum_sell
            if _db < 0 or _ds < 0:
                self._anchor_reset_count += 1
                sys_log.warning(
                    "[CVD-ANCHOR][RESET] code=%s 누적체결 역행 — 증분 폐기·기준선 재설정 "
                    "(buy %d→%d, sell %d→%d, 누적 %d회). 재접속·세션리셋·월물교체 신호.",
                    self._rt_code, self._last_cum_buy, cum_buy,
                    self._last_cum_sell, cum_sell, self._anchor_reset_count,
                )
            else:
                d_buy, d_sell = _db, _ds

        self._last_cum_buy = cum_buy
        self._last_cum_sell = cum_sell
        return d_buy, d_sell

    def _handle_hoga(self, obj) -> None:
        ask_prices = [_safe_float(obj.GetHeaderValue(idx)) for idx in (2, 3, 4, 5, 6)]
        ask_qtys = [_safe_int(obj.GetHeaderValue(idx)) for idx in (7, 8, 9, 10, 11)]
        bid_prices = [_safe_float(obj.GetHeaderValue(idx)) for idx in (19, 20, 21, 22, 23)]
        bid_qtys = [_safe_int(obj.GetHeaderValue(idx)) for idx in (24, 25, 26, 27, 28)]

        bid1 = bid_prices[0] if bid_prices else 0.0
        ask1 = ask_prices[0] if ask_prices else 0.0
        bid_q = bid_qtys[0] if bid_qtys else 0
        ask_q = ask_qtys[0] if ask_qtys else 0

        if bid1 > 0:
            self._last_bid1 = bid1
        if ask1 > 0:
            self._last_ask1 = ask1
        if bid_q > 0:
            self._last_bid_qty = bid_q
        if ask_q > 0:
            self._last_ask_qty = ask_q

        self._last_hoga_snapshot = {
            "bid_prices": bid_prices,
            "ask_prices": ask_prices,
            "bid_qtys": bid_qtys,
            "ask_qtys": ask_qtys,
        }
        self._hoga_event_count += 1

        active = sum(
            1 for i in range(5) if bid_prices[i] > 0 and ask_prices[i] > 0
        )
        level_parts = " ".join(
            "L%d: bid=%.2f/%d ask=%.2f/%d" % (
                i + 1,
                bid_prices[i], bid_qtys[i],
                ask_prices[i], ask_qtys[i],
            )
            for i in range(5)
        )
        hoga_log.debug(
            "[HOGA] code=%s active_levels=%d/5 %s",
            self._rt_code, active, level_parts,
        )

        if self._current_bar is not None:
            self._current_bar["bid1"] = self._last_bid1
            self._current_bar["ask1"] = self._last_ask1
            self._current_bar["bid_qty"] = self._last_bid_qty
            self._current_bar["ask_qty"] = self._last_ask_qty
            self._current_bar["hoga_levels"] = dict(self._last_hoga_snapshot)

        if self._on_hoga is not None:
            try:
                self._on_hoga(
                    self._last_bid1,
                    self._last_ask1,
                    self._last_bid_qty,
                    self._last_ask_qty,
                    dict(self._last_hoga_snapshot),
                )
            except TypeError:
                self._on_hoga(
                    self._last_bid1,
                    self._last_ask1,
                    self._last_bid_qty,
                    self._last_ask_qty,
                )

    def _update_bar(
        self,
        *,
        bar_ts: datetime,
        bar_min: int,
        price: float,
        volume: int,
        bid1: float,
        ask1: float,
        bid_q: int,
        ask_q: int,
        oi: int,
        is_buy_tick: bool,
        anchor_d_buy: Optional[int] = None,
        anchor_d_sell: Optional[int] = None,
        shadow_side: Optional[str] = None,
    ) -> None:
        if self._current_min is not None and bar_min != self._current_min:
            sys_log.info(
                "[CybosRT-ROLLOVER] code=%s from=%s to=%s",
                self._rt_code,
                self._current_bar["ts"].strftime("%H:%M") if self._current_bar else "?",
                bar_ts.strftime("%H:%M"),
            )
            self._close_current_bar()

        buy_v = volume if is_buy_tick else 0
        sell_v = 0 if is_buy_tick else volume

        if self._current_bar is None:
            self._current_bar = {
                "ts": bar_ts,
                "code": self.code,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume,
                "buy_vol": buy_v,
                "sell_vol": sell_v,
                "bid1": bid1,
                "ask1": ask1,
                "bid_qty": bid_q,
                "ask_qty": ask_q,
                "hoga_levels": dict(self._last_hoga_snapshot),
                "oi": oi,
                # [349차] 분당 틱수 급변장 사전 가드용 — 이 봉에서 수신한 틱 메시지 수
                # (체결량과 별개로, 주문흐름 자체의 폭주 여부를 보는 지표).
                "tick_count": 1,
                # [MW0601 452차 / QDQ Phase 0] 계측 4종. **None = 미계측**이며
                # DB에 NULL로 들어간다. 0으로 초기화하지 않는다 — "0이었다"와
                # "못 받았다"가 같아 보이면 감시 자체가 무의미해진다.
                "anchor_buy": None,
                "anchor_sell": None,
                "buy_vol_flag": None,
                "sell_vol_flag": None,
            }
            self._current_min = bar_min
        else:
            bar = self._current_bar
            bar["high"] = max(bar["high"], price)
            bar["low"] = min(bar["low"], price)
            bar["close"] = price
            bar["volume"] += volume
            bar["buy_vol"] = bar.get("buy_vol", 0) + buy_v
            bar["sell_vol"] = bar.get("sell_vol", 0) + sell_v
            bar["bid1"] = bid1
            bar["ask1"] = ask1
            bar["bid_qty"] = bid_q
            bar["ask_qty"] = ask_q
            bar["hoga_levels"] = dict(self._last_hoga_snapshot)
            bar["oi"] = oi
            bar["tick_count"] = bar.get("tick_count", 0) + 1

        # [MW0601 452차 / QDQ Phase 0] 쓸 수 있는 틱만 합산한다.
        # 봉 안에서 한 번도 못 받으면 None이 유지돼 NULL로 저장된다.
        # 일부만 받으면 `anchor_buy + anchor_sell < volume`이 되어 잔차가 스스로
        # 드러난다(Phase 2 리포트가 그 잔차를 읽는다) — 별도 열이 필요 없다.
        _bar = self._current_bar
        if anchor_d_buy is not None and anchor_d_sell is not None:
            _bar["anchor_buy"] = (_bar.get("anchor_buy") or 0) + anchor_d_buy
            _bar["anchor_sell"] = (_bar.get("anchor_sell") or 0) + anchor_d_sell
        if shadow_side is not None:
            _key = "buy_vol_flag" if shadow_side == "BUY" else "sell_vol_flag"
            _other = "sell_vol_flag" if shadow_side == "BUY" else "buy_vol_flag"
            _bar[_key] = (_bar.get(_key) or 0) + volume
            # 반대편도 0으로 확정한다 — 이 봉은 "체결구분을 받았다"는 상태이므로
            # 한쪽만 NULL로 남으면 판독 시 미계측으로 오독된다.
            _bar[_other] = _bar.get(_other) or 0

        if self._on_tick is not None:
            self._on_tick(dict(self._current_bar))

    def _close_current_bar(self) -> None:
        if self._current_bar is None:
            return
        closed = dict(self._current_bar)
        # Clear rollover state before invoking callbacks because the minute
        # pipeline can re-enter the Qt event loop and trigger nested ticks.
        self._current_bar = None
        self._current_min = None
        self._candles.append(closed)
        _closed_min = closed["ts"].hour * 60 + closed["ts"].minute
        # 중복 BAR-CLOSE 감지: 같은 분봉이 두 번 이상 닫히면 경고
        if self._last_closed_min is not None and _closed_min <= self._last_closed_min:
            sys_log.warning(
                "[BAR-CLOSE][DUPLICATE] ts=%s 이미 닫힌 봉 재발화 "
                "(last_closed=%02d:%02d, cur=%02d:%02d) — stale oscillation 가능성",
                closed["ts"].strftime("%H:%M"),
                self._last_closed_min // 60, self._last_closed_min % 60,
                _closed_min // 60, _closed_min % 60,
            )
        self._last_closed_min = _closed_min
        sys_log.info(
            "[BAR-CLOSE][CYBOS] ts=%s O=%.2f H=%.2f L=%.2f C=%.2f V=%d",
            closed["ts"].strftime("%H:%M"),
            closed["open"],
            closed["high"],
            closed["low"],
            closed["close"],
            closed["volume"],
        )
        self._log_anchor_diagnostics(closed)
        if self._on_candle_closed is not None:
            try:
                self._on_candle_closed(closed)
            except Exception:
                sys_log.exception("[BAR-CLOSE][CYBOS] on_candle_closed callback failed")

    def _log_anchor_diagnostics(self, closed: Dict) -> None:
        """[MW0601 452차 / QDQ Phase 0] 봉 마감 시 현행 vs 섀도 vs 앵커 1줄 대조.

        하루 약 385줄(`[BAR-CLOSE]`와 동급). 이 줄만 grep하면 라이브 첫날에
        "현행 buy_vol이 앵커보다 얼마나 부풀어 있는가"를 즉시 읽을 수 있다.

        진단 도구가 수집 경로를 죽이면 안 되므로 전부 방어한다.
        """
        try:
            if not self._anchor_available and not self._anchor_unavail_warned:
                self._anchor_unavail_warned = True
                sys_log.warning(
                    "[CVD-ANCHOR][UNAVAIL] code=%s 원천이 22_누적체결매도/23_누적체결매수를 "
                    "주지 않는다(세션 내 관측 0). QDQ Phase 0 앵커 열은 NULL로 남는다 — "
                    "필드 가용성 가설 반증이므로 Phase 3·4 재설계 필요.", self._rt_code,
                )
            _vol = closed.get("volume") or 0
            _a_buy, _a_sell = closed.get("anchor_buy"), closed.get("anchor_sell")
            _f_buy = closed.get("buy_vol_flag")
            _resid_a = None if _a_buy is None else _vol - (_a_buy + (_a_sell or 0))
            _resid_f = (None if _f_buy is None
                        else _vol - (_f_buy + (closed.get("sell_vol_flag") or 0)))
            sys_log.info(
                "[CVD-ANCHOR] ts=%s vol=%d | live_buy=%s shadow_buy=%s anchor_buy=%s | "
                "resid(anchor)=%s resid(shadow)=%s unknown_ticks=%d resets=%d",
                closed["ts"].strftime("%H:%M"), _vol,
                closed.get("buy_vol"),
                "-" if _f_buy is None else _f_buy,
                "-" if _a_buy is None else _a_buy,
                "-" if _resid_a is None else _resid_a,
                "-" if _resid_f is None else _resid_f,
                self._flag_unknown_ticks, self._anchor_reset_count,
            )
        except Exception:
            sys_log.debug("[CVD-ANCHOR] 진단 로그 실패", exc_info=True)

    @staticmethod
    def _parse_tick_time(raw_time: str) -> datetime:
        now = datetime.now()
        digits = "".join(ch for ch in _safe_str(raw_time) if ch.isdigit())
        if len(digits) in (5, 6):
            digits = digits.zfill(6)
        if len(digits) >= 6:
            try:
                hh = int(digits[0:2])
                mm = int(digits[2:4])
                ss = int(digits[4:6])
                return now.replace(hour=hh, minute=mm, second=ss, microsecond=0)
            except Exception:
                return now
        return now
