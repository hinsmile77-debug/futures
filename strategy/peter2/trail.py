"""[MW0601 690차 후속] 피터2 이익보호 트레일(실거래) + 기존 규칙 섀도.

근거: `docs/미륵이고도화3/피터2/피터2_이익보호트레일_제안_MW0601-20261014.md`
      (피터 실거래 73건/29일 재생 — `scripts/peter2_trail_backtest.py`).

규칙(실거래)
    ATR   = 진입 시점 1분봉 ATR(14) — 포지션 수명 동안 고정
    무장  = 최대 유리폭(MFE) ≥ arm_atr × ATR            (기본 4.5)
    보호선 = 고점 − back_atr × ATR (매도는 대칭)        (기본 3.5)
    보호선은 **유리한 쪽으로만** 움직이고, 피터 손절(base_stop)보다 불리하면 쓰지 않는다.
    → 무장 순간 최소 +(arm−back)×ATR 이 잠긴다.

기존 규칙 섀도(NoTrailGhost)
    트레일이 실포지션을 먼저 내보낸 경우에만 생긴다. 그 뒤로 「트레일이 없었다면」 —
    피터 손절·목표·청산·반대 지시·15:10 — 을 따라가 반사실 손익을 남긴다.
    트레일이 청산에 관여하지 않은 포지션은 두 규칙의 결과가 같다(Δ=0 으로 기록).

🔴 이 모듈은 주문을 내지 않는다. 가격은 전부 **미니가**다.
"""
import json
import os

LONG, SHORT = "L", "S"


def _side_of(status):
    return {"LONG": LONG, "SHORT": SHORT, LONG: LONG, SHORT: SHORT}.get(status)


def _more_protective(side, a, b):
    """두 손절가 중 더 보호적인(진입 방향으로 더 올라간) 값. None 은 무시."""
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b) if side == LONG else min(a, b)


class Peter2Trail:
    """포지션 1개의 트레일 상태."""

    def __init__(self, arm_atr=4.5, back_atr=3.5):
        self.arm_atr = float(arm_atr)
        self.back_atr = float(back_atr)
        self.pos_key = None
        self.side = None
        self.entry = None
        self.atr = None
        self.base_stop = None      # 피터 규칙의 손절(트레일 없는 세계)
        self.target = None         # 피터 목표(섀도 승계용)
        self.peak_px = None        # 진입 방향 최고 유리 가격
        self.armed = False
        self.trail_stop = None     # 트레일 보호선(무장 후에만)
        self.armed_hm = None

    # ── 수명 ────────────────────────────────────────────────
    def start(self, pos_key, status, entry, atr, base_stop, target=None):
        """새 포지션. ATR 이 비정상이면 False — 호출부가 「트레일 미적용」을 로그로 남긴다."""
        side = _side_of(status)
        try:
            atr = float(atr)
        except (TypeError, ValueError):
            atr = None
        if side is None or entry is None or atr is None or atr <= 0:
            return False
        self.pos_key, self.side, self.entry, self.atr = pos_key, side, float(entry), atr
        self.base_stop = None if base_stop is None else float(base_stop)
        self.target = None if target is None else float(target)
        self.peak_px = float(entry)
        self.armed, self.trail_stop, self.armed_hm = False, None, None
        return True

    @property
    def arm_pt(self):
        return self.arm_atr * self.atr

    @property
    def back_pt(self):
        return self.back_atr * self.atr

    def mfe_pt(self):
        if self.peak_px is None:
            return 0.0
        return (self.peak_px - self.entry) if self.side == LONG else (self.entry - self.peak_px)

    # ── 갱신 ────────────────────────────────────────────────
    def on_price(self, price, hm=None):
        """가격 1개. 보호선이 **새로 올라갔으면** 그 값을, 아니면 None.

        순서는 백테스트와 같다 — 고점을 먼저 갱신하고 보호선을 다시 계산한다.
        (보호선 터치 청산은 호출부의 기존 틱 하드스톱이 한다 — 여기선 레벨만 낸다.)
        """
        if self.side is None or price is None or price <= 0:
            return None
        p = float(price)
        if self.side == LONG:
            self.peak_px = max(self.peak_px, p)
        else:
            self.peak_px = min(self.peak_px, p)
        if not self.armed and self.mfe_pt() >= self.arm_pt:
            self.armed, self.armed_hm = True, hm
        if not self.armed:
            return None
        lvl = self.peak_px - self.back_pt if self.side == LONG else self.peak_px + self.back_pt
        lvl = round(round(lvl / 0.02) * 0.02, 2)
        if self.trail_stop is None or _more_protective(self.side, lvl, self.trail_stop) != self.trail_stop:
            self.trail_stop = lvl
            return lvl
        return None

    def on_base_stop(self, new_base):
        """피터 손절 변경(SET_STOP). 트레일 무장 중이면 실제 적용값은 더 보호적인 쪽."""
        self.base_stop = None if new_base is None else float(new_base)
        return self.effective_stop()

    def effective_stop(self):
        if not self.armed:
            return self.base_stop
        return _more_protective(self.side, self.base_stop, self.trail_stop)

    def trail_binding(self):
        """지금 실손절을 트레일이 정하고 있는가(= 기존 규칙보다 먼저 나갈 수 있는가)."""
        if not self.armed or self.trail_stop is None:
            return False
        return self.effective_stop() == self.trail_stop and self.trail_stop != self.base_stop

    # ── 저장 ────────────────────────────────────────────────
    def to_dict(self):
        return {k: getattr(self, k) for k in (
            "arm_atr", "back_atr", "pos_key", "side", "entry", "atr", "base_stop", "target",
            "peak_px", "armed", "trail_stop", "armed_hm")}

    @classmethod
    def from_dict(cls, d):
        t = cls(d.get("arm_atr", 4.5), d.get("back_atr", 3.5))
        for k, v in (d or {}).items():
            if hasattr(t, k):
                setattr(t, k, v)
        return t


class NoTrailGhost:
    """기존 규칙(트레일 없음) 섀도 — 트레일이 먼저 내보낸 포지션의 반사실."""

    def __init__(self, pos_key, side, entry, stop, target, start_hm,
                 real_exit_px, real_pnl_pts, atr=None, peak_px=None):
        self.pos_key = pos_key
        self.side = _side_of(side)
        self.entry = float(entry)
        self.stop = None if stop is None else float(stop)
        self.target = None if target is None else float(target)
        self.start_hm = start_hm
        self.real_exit_px = None if real_exit_px is None else float(real_exit_px)
        self.real_pnl_pts = None if real_pnl_pts is None else float(real_pnl_pts)
        self.atr = atr
        self.peak_px = peak_px
        self.done = False
        self.exit_px = None
        self.exit_hm = None
        self.exit_why = None
        self.last_px = None

    def _close(self, px, hm, why):
        self.done, self.exit_px, self.exit_hm, self.exit_why = True, float(px), hm, why

    def pnl_pts(self):
        if self.exit_px is None:
            return None
        return (self.exit_px - self.entry) if self.side == LONG else (self.entry - self.exit_px)

    def on_price(self, price, hm, force_exit_hm="15:10"):
        """가격·시각. 닫혔으면 True. 손절·목표는 그 레벨에서 체결됐다고 본다(틱 스톱 근사)."""
        if self.done or price is None or price <= 0:
            return self.done
        p = float(price)
        self.last_px = p
        if self.stop is not None and ((self.side == LONG and p <= self.stop)
                                      or (self.side == SHORT and p >= self.stop)):
            self._close(self.stop, hm, "피터손절")
        elif self.target is not None and ((self.side == LONG and p >= self.target)
                                          or (self.side == SHORT and p <= self.target)):
            self._close(self.target, hm, "피터목표")
        elif hm is not None and hm >= force_exit_hm:
            self._close(p, hm, "15:10 강제청산")
        return self.done

    def on_facts(self, facts, price, hm, to_mini, stop_cap=8.0):
        """피터 트윗 사실 목록 — 실보유였다면 follower 가 냈을 의도를 같은 규칙으로 흉내 낸다
        (`follower._follow_apply` holding 분기 · `main._peter2_execute` SET_STOP 캡)."""
        if self.done:
            return True
        px = price if price else self.last_px
        near = lambda a, b: a is not None and b is not None and abs(a - b) <= 1.5
        for f in facts or []:
            t = f.get("type")
            if t == "exit":
                if px:
                    self._close(px, hm, "피터청산(%s)" % (f.get("kind") or "-"))
                return self.done
            if t == "entry" and f.get("side") and f["side"] != self.side:
                if px:
                    self._close(px, hm, "피터반대지시")
                return self.done
            if t == "fill":
                lm = to_mini(f.get("level")) if f.get("level") is not None else None
                opp = f.get("side") and f["side"] != self.side
                if (near(lm, self.target) or near(lm, self.stop) or opp) and px:
                    self._close(px, hm, "피터체결")
                    return self.done
            elif t == "stop" and f.get("level") is not None:
                sm = to_mini(f["level"])
                if sm is not None:
                    if self.side == LONG and sm < self.entry - stop_cap:
                        sm = round(self.entry - stop_cap, 2)
                    elif self.side == SHORT and sm > self.entry + stop_cap:
                        sm = round(self.entry + stop_cap, 2)
                    self.stop = sm
            elif t == "tighten" and f.get("level") is not None and px:
                sm = to_mini(f["level"])
                if sm is not None:
                    ok_now = (self.side == LONG and sm < px) or (self.side == SHORT and sm > px)
                    tighter = self.stop is None or _more_protective(self.side, sm, self.stop) == sm
                    if ok_now and tighter:
                        self.stop = sm
            elif t == "target" and f.get("level") is not None:
                tm = to_mini(f["level"])
                if tm is not None:
                    self.target = tm
        return self.done

    def to_dict(self):
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, d):
        g = cls(d["pos_key"], d["side"], d["entry"], d.get("stop"), d.get("target"),
                d.get("start_hm"), d.get("real_exit_px"), d.get("real_pnl_pts"),
                d.get("atr"), d.get("peak_px"))
        for k, v in d.items():
            setattr(g, k, v)
        return g


# ── 영속(재기동 생존) ────────────────────────────────────────────
def state_path(live_dir, date):
    return os.path.join(live_dir, "trail_state_%s.json" % date)


def save_state(live_dir, date, trail, ghosts):
    """ghosts = 진행 중인 섀도 목록(트레일 청산이 연달아 나면 여러 개가 동시에 돈다)."""
    os.makedirs(live_dir, exist_ok=True)
    path = state_path(live_dir, date)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({"date": date,
                   "trail": trail.to_dict() if trail is not None else None,
                   "ghosts": [g.to_dict() for g in (ghosts or []) if not g.done]},
                  fh, ensure_ascii=False)
    os.replace(tmp, path)


def load_state(live_dir, date):
    """(trail|None, [ghost…]). 파일이 없거나 깨졌으면 (None, [])."""
    try:
        with open(state_path(live_dir, date), encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return None, []
    tr = Peter2Trail.from_dict(d["trail"]) if d.get("trail") else None
    ghs = [NoTrailGhost.from_dict(g) for g in (d.get("ghosts") or [])]
    return tr, ghs


def append_result(live_dir, rec):
    """포지션 1건의 실거래(트레일) vs 섀도(기존 규칙) 비교 기록."""
    os.makedirs(live_dir, exist_ok=True)
    with open(os.path.join(live_dir, "trail_shadow.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
