# strategy/runtime/session_replay_service.py
"""세션 재생 — 기동 시 당일(또는 최근 거래일) 데이터를 DB 에서 패널로 되살린다.
[MW0601 614차]

두 상황을 **하나의 기전**으로 덮는다(사용자 지시 2026-09-21):

  · **장후 기동(복기)** — 15:35 이후·휴일 기동. 라이브가 영영 안 오므로 화면이
    통째로 비어 복기를 할 수 없었다. 되살린 뒤 「■ 복기」 배지를 단다.
  · **장중 재기동(복원)** — 기동 시각까지의 구간이 패널에서 사라진다(라이브는
    그 순간부터의 값만 민다). 되살리되 **배지는 달지 않는다** — 라이브가 곧 덮고,
    그때 배지가 남아 있으면 살아 있는 값을 죽은 값처럼 보이게 한다.

왜 게이트를 풀지 않는가
----------------------
`is_market_open()` 가드 4개(수급 TR·옵션 체인·지수 폴링·분봉 파이프라인)는 **옳다.**
장외에 TR 을 때리면 안 되고, 없는 틱으로 예측을 만들면 더 안 된다. 문제는
"수집하지 않는다"가 "화면에 아무것도 없다"로 직결된 것뿐이다 — DB 에는 다 있다.
그래서 **수집 경로는 그대로 두고 표시 경로만** 되살린다.

🔴 불변식 셋 — 이 파일에서 가장 중요한 부분이다
-----------------------------------------------
1. **라이브가 이긴다.** 재생은 `dashboard.replay_should_inject(key)` 가 참일 때만
   주입한다. 장중 재기동에서는 기동 직후 라이브 push 가 동시에 들어오는데,
   재생이 조금 늦으면 **더 새로운 값을 더 오래된 DB 값으로 덮어쓴다** —
   화면이 조용히 과거로 되돌아가고 예외는 나지 않는다.
2. **표시 계층만 건드린다.** `position`·`investor_data`·CB 상태를 쓰지 않는다.
   재생이 매매 상태를 오염시키면 안 된다.
3. **없는 것은 만들지 않는다.** 원천에 없는 패널은 **건드리지 않는다**(빈 dict 와
   0 을 구분한다 — 계측 4원칙 ②).

⚠ **단일 「스냅샷 시각」이 없다.** 원천마다 끝나는 시각이 다르다 — 실측
  `raw_features` 15:08(파이프라인 종료) vs `raw_program_trade` 15:34(수급 타이머).
  하나로 뭉뚱그리면 거짓말이 되므로 배지 툴팁에 원천별 마지막 시각을 나열한다.
"""
from __future__ import annotations

import datetime
import json
import logging
import sqlite3
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("SYSTEM")

_RAW_DB = "data/db/raw_data.db"
_PRED_DB = "data/db/predictions.db"

_H_MAP = {"1m": "1분", "3m": "3분", "5m": "5분",
          "10m": "10분", "15m": "15분", "30m": "30분"}


def _ro(path: str) -> sqlite3.Connection:
    return sqlite3.connect("file:%s?mode=ro" % path, uri=True, timeout=3.0)


class SessionReplayService:
    """기동 시 1회, 백그라운드에서 모아 메인 스레드에서 주입한다."""

    # 기동 직후는 이미 붐빈다 — 브로커 동기화·모델 로드·`restore_on_startup`
    # (백그라운드 DB 수집 + 4단계 UI 체인)이 같이 돈다. 그 뒤로 비킨다.
    START_DELAY_MS = 9_000
    # UI 주입 사이 양보 — 한 번에 밀어 넣으면 메인 스레드가 길게 막힌다
    # (2026-06-26 재시작 직후 14.8초 블로킹 전례. `_restore_panels_worker` 주석 참조).
    STEP_GAP_MS = 60
    # 「마지막 유효 행」을 찾을 때 거슬러 올라갈 최대 행 수. 하루 약 390행이므로
    # 90 이면 장 마감 직전 1시간 반을 덮는다. 전수 스캔을 만들지 않기 위한 상한이다.
    _LOOKBACK = 90

    def schedule(self, system: Any) -> None:
        """기동 경로에서 한 번 부른다. 어떤 예외도 밖으로 내보내지 않는다."""
        try:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(self.START_DELAY_MS, lambda: self._spawn(system))
        except Exception as exc:                                # noqa: BLE001
            logger.warning("[Replay] 예약 실패(무시): %s", exc)

    # ── 수집(백그라운드) ──────────────────────────────────────────────────
    def _spawn(self, system: Any) -> None:
        import threading
        threading.Thread(target=self._worker, args=(system,), daemon=True).start()

    def _worker(self, system: Any) -> None:
        try:
            mode, date = self._decide(system)
            if date is None:
                logger.info("[Replay] 대상 날짜 없음 — 재생하지 않는다")
                return
            payload = self._collect(date)
            if not payload:
                logger.info("[Replay] %s 원천 없음 — 패널을 건드리지 않는다", date)
                return
            # 🔴 **넘기기 직전에 남긴다.** 614차 초판은 여기서 주입이 조용히
            #    사라졌는데 로그가 한 줄도 없어 "돌긴 했나"조차 알 수 없었다.
            #    이 줄이 있으면 다음에 같은 일이 나도 **어디까지 갔는지** 보인다
            #    (계측 4원칙 ④ — 폴백·실패가 쓰였으면 그 사실을 남겨라).
            logger.info("[Replay] %s %s — %d패널 수집, 메인 스레드로 넘긴다 [%s]",
                        mode, date, len(payload), " ".join(sorted(payload)))
            # 🔴 **여기는 워커 스레드다 — `QTimer.singleShot` 을 쓰면 안 된다.**
            #
            # 타이머는 호출한 스레드에 붙는데 이 스레드에는 Qt 이벤트 루프가 없어
            # **한 번도 발화하지 않는다.** 예외도 로그도 없이 조용히 사라진다.
            #
            # 614차 초판이 정확히 이걸로 죽었다 — 2026-09-21 16:41 재기동에서
            # `[Replay]` 로그가 **한 줄도** 남지 않았고 화면은 10행 전부 「미수집」
            # 이었다. 504차 후속이 `_restore_panels_worker` 에서 **같은 함수·같은
            # 유형**을 이미 겪고 고쳐뒀는데(그때는 기동 시 4패널이 복원된 적이
            # 없었다는 게 전 기간 로그 전수 확인으로 드러났다) 그 교훈을 놓쳤다.
            #
            # ⇒ 304차 후속이 만들고 490차 F-L 이 helper 로 감싼 통로를 그대로 쓴다.
            #   `_apply` 가 메인 스레드에서 돌기 시작하면 그 안의 단계별
            #   `singleShot` 은 정상 동작한다.
            system._dashboard_call(
                lambda: self._apply(system, mode, date, payload))
        except Exception as exc:                                # noqa: BLE001
            logger.warning("[Replay] 수집 실패(무시): %s", exc, exc_info=True)

    def _decide(self, system: Any) -> Tuple[str, Optional[str]]:
        """(mode, 대상날짜). mode = 'post_market' | 'intraday'."""
        from utils.time_utils import is_trading_session

        now = datetime.datetime.now()
        today = now.date().isoformat()
        if is_trading_session(now):
            # 장중 재기동 — 오늘만 본다. 데이터가 없으면(09:00 직후 첫 기동)
            # 되살릴 것이 없으니 그냥 안 한다.
            return "intraday", today if self._has_data(today) else None
        if self._has_data(today):
            return "post_market", today
        return "post_market", self._latest_date()

    def _has_data(self, date: str) -> bool:
        try:
            con = _ro(_RAW_DB)
            r = con.execute(
                "SELECT 1 FROM raw_candles WHERE ts>=? AND ts<=? LIMIT 1",
                ("%s 00:00:00" % date, "%s 23:59:59" % date)).fetchone()
            con.close()
            return r is not None
        except Exception:                                       # noqa: BLE001
            return False

    def _latest_date(self) -> Optional[str]:
        try:
            con = _ro(_RAW_DB)
            r = con.execute("SELECT max(ts) FROM raw_candles").fetchone()
            con.close()
            return r[0][:10] if r and r[0] else None
        except Exception:                                       # noqa: BLE001
            return None

    # ── 원천 읽기 ─────────────────────────────────────────────────────────
    def _collect(self, date: str) -> Dict[str, Any]:
        """패널별 payload + 그 원천의 마지막 시각.

        ⚠ 전부 **마지막 행 위주**의 경계 질의다. 장중에도 도는 경로라
          전수 스캔을 하면 456차(CB⑤ 자가유발)를 재현한다.
        """
        lo, hi = "%s 00:00:00" % date, "%s 23:59:59" % date
        out: Dict[str, Any] = {}

        # ① 피처 — 🔴 **마지막 행이 아니라 마지막 「유효」 행**을 쓴다.
        #
        # 그냥 마지막 행을 쓰면 0 을 되살린다. 실측 2026-09-21: 15:02~15:08 6개
        # 행이 재기동 직후라 `opt_chain_available=0 · rv_iv_spread_ready=False ·
        # vkospi=0` 이고, 마지막 유효 행은 **15:00** 이다. 하필 재기동 직후가
        # 그날 마지막 행이 되는 일은 흔하다 — 사람이 장 끝나고 껐다 켜기 때문이다.
        #
        # ⚠ "복원했는데 0" 은 **안 한 것보다 나쁘다.** 빈 화면은 없다는 걸
        #   알려주지만 0 은 실측처럼 보인다(계측 4원칙 ②).
        # ⚠ 그렇다고 아무 행이나 거슬러 올라가지 않는다 — 스캔을 최근 `_LOOKBACK`
        #   행으로 묶어 전수 스캔(456차 CB⑤)을 만들지 않는다.
        rows = []
        try:
            con = _ro(_RAW_DB)
            rows = con.execute(
                "SELECT ts, features FROM raw_features WHERE ts>=? AND ts<=? "
                "ORDER BY ts DESC LIMIT ?", (lo, hi, self._LOOKBACK)).fetchall()
            con.close()
        except Exception as exc:                                # noqa: BLE001
            logger.debug("[Replay] raw_features 스킵: %s", exc)

        def _pick(flag: str):
            """최근 행부터 훑어 그 플래그가 선 첫 행. 없으면 (None, None)."""
            for ts, fj in rows:
                try:
                    d = json.loads(fj)
                except Exception:                               # noqa: BLE001
                    continue
                if float(d.get(flag) or 0.0) > 0.0:
                    return d, ts[11:16]
            return None, None

        _rv, _rv_ts = _pick("rv_iv_spread_ready")
        if _rv is not None:
            out["rv_iv"] = (_rv, _rv_ts)
        _ch, _ch_ts = _pick("opt_chain_available")
        if _ch is not None:
            # 체인 카드는 `opt_*` 키만 본다 — 어떤 키를 쓰는지 보이게 추려 넘긴다.
            out["option_chain"] = (
                dict((k, v) for k, v in _ch.items() if k.startswith("opt_")),
                _ch_ts)

        # ② 현재가 — 그날 마지막 종가
        try:
            con = _ro(_RAW_DB)
            r = con.execute(
                "SELECT ts, close FROM raw_candles WHERE ts>=? AND ts<=? "
                "ORDER BY ts DESC LIMIT 1", (lo, hi)).fetchone()
            con.close()
            if r and r[1]:
                out["price"] = (float(r[1]), r[0][11:16])
        except Exception as exc:                                # noqa: BLE001
            logger.debug("[Replay] raw_candles 스킵: %s", exc)

        # ③ 예측 6호라이즌 — 그날 마지막 분
        try:
            con = _ro(_PRED_DB)
            last = con.execute(
                "SELECT max(ts) FROM predictions WHERE ts>=? AND ts<=?",
                (lo, hi)).fetchone()
            if last and last[0]:
                rows = con.execute(
                    "SELECT horizon, direction, up_prob, down_prob, flat_prob, "
                    "confidence FROM predictions WHERE ts=?", (last[0],)).fetchall()
                preds = {}
                conf = None
                for hz, d, up, dn, fl, cf in rows:
                    preds[_H_MAP.get(hz, hz)] = {
                        "signal": int(d or 0), "up": float(up or 0.0),
                        "dn": float(dn or 0.0), "flat": float(fl or 0.0)}
                    if hz == "1m":
                        conf = float(cf or 0.0)
                if preds:
                    out["prediction"] = ((preds, conf), last[0][11:16])
            con.close()
        except Exception as exc:                                # noqa: BLE001
            logger.debug("[Replay] predictions 스킵: %s", exc)

        # ④ 시계열 2종 — 이미 날짜 인자를 받는 provider 가 있다(611·613차)
        try:
            from collection.cybos.futures_flow_series import (
                get_futures_session_delta)
            fut = get_futures_session_delta(date)
            if fut.get("products"):
                out["futures_flow"] = (fut, fut.get("last_time"))
        except Exception as exc:                                # noqa: BLE001
            logger.debug("[Replay] 선물 시계열 스킵: %s", exc)
        try:
            from collection.cybos.weekly_option_flow import WeeklyOptionFlow
            from config import settings as _st
            opt = WeeklyOptionFlow(getattr(
                _st, "WEEKLY_OPTION_FLOW_DB", "data/db/option_flow.db")
            ).get_individual_session_delta(date)
            if opt.get("products"):
                out["option_flow"] = (opt, opt.get("last_time"))
        except Exception as exc:                                # noqa: BLE001
            logger.debug("[Replay] 옵션 시계열 스킵: %s", exc)

        return out

    # ── 주입(메인 스레드) ─────────────────────────────────────────────────
    def _apply(self, system: Any, mode: str, date: str,
               payload: Dict[str, Any]) -> None:
        from PyQt5.QtCore import QTimer

        dash = getattr(system, "dashboard", None)
        if dash is None:
            return

        steps = []
        for key in ("price", "prediction", "rv_iv", "option_chain",
                    "option_flow", "futures_flow"):
            if key in payload:
                steps.append(key)

        done = []

        def _one(i: int) -> None:
            if i >= len(steps):
                self._finish(dash, mode, date, done, payload)
                return
            key = steps[i]
            try:
                if not dash.replay_should_inject(key):
                    # 🔴 라이브가 이미 이 패널을 갱신했다 — 덮지 않는다.
                    logger.info("[Replay] %s 스킵 — 라이브가 이미 갱신했다", key)
                else:
                    # 주입도 같은 `update_*` 를 타므로 재생임을 알린다 —
                    # 안 그러면 재생이 스스로를 라이브로 기록한다.
                    dash.replay_begin()
                    try:
                        self._inject(dash, key, payload[key][0])
                    finally:
                        dash.replay_end()
                    done.append(key)
            except Exception as exc:                            # noqa: BLE001
                logger.warning("[Replay] %s 주입 실패(무시): %s", key, exc)
                try:
                    dash.replay_end()
                except Exception:                               # noqa: BLE001
                    pass
            QTimer.singleShot(self.STEP_GAP_MS, lambda: _one(i + 1))

        _one(0)

    def _inject(self, dash: Any, key: str, data: Any) -> None:
        if key == "price":
            dash.update_price(float(data), 0.0)
        elif key == "prediction":
            preds, conf = data
            dash.update_prediction(0.0, preds, {}, conf)
        elif key == "rv_iv":
            dash.update_rv_iv_spread(data)
        elif key == "option_chain":
            dash.update_option_chain(data)
        elif key == "option_flow":
            dash.update_option_flow_delta(data)
        elif key == "futures_flow":
            dash.update_futures_flow_delta(data)

    def _finish(self, dash: Any, mode: str, date: str, done, payload) -> None:
        if not done:
            logger.info("[Replay] 주입할 패널 없음 (mode=%s date=%s)", mode, date)
            return
        # 원천별 마지막 시각 — **하나로 뭉뚱그리지 않는다.**
        src = " · ".join("%s %s" % (k, payload[k][1] or "—") for k in done)
        logger.info("[Replay] %s %s — %d패널 주입 [%s]", mode, date, len(done), src)
        if mode == "post_market":
            dash.set_replay_badge(
                "■ 복기 · %s" % date,
                "장후 기동이라 라이브 갱신이 없다. DB 에서 되살린 값이다.\n"
                "원천마다 끝난 시각이 다르다 — %s\n"
                "장이 열려 라이브가 들어오면 이 배지는 사라진다." % src,
            )
        else:
            # 장중 복원 — 배지를 달지 않는다. 라이브가 곧 덮는다.
            dash.set_replay_badge("")

    def clear_badge(self, system: Any) -> None:
        """라이브가 들어오기 시작하면 복기 배지를 내린다."""
        try:
            system.dashboard.set_replay_badge("")
        except Exception:                                       # noqa: BLE001
            pass
