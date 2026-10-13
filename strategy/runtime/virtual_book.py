# -*- coding: utf-8 -*-
"""[MW0602 거래주체분리 2단계] 가상 장부 — 실주문이 나가지 않는 주체의 실시간 가상 포지션.

언제 쓰이나 (사용자 결정 2026-10-14)
    · 거래주체로 선택되지 않은 주체(미륵 · 신동 · 피터)의 진입
    · 선택 주체라도 실서버 자동주문 잠금(`REAL_TRADING_ARMED` 등)에 막힌 진입
    → 주문 대신 여기서 가상으로 열고, 실제와 **같은 청산 사다리**로 장중 내내 관리한다.

격리 (사용자 결정 2026-10-14)
    · 가상 손절은 **CB②(연속 손절)에 세지 않는다** — CB 는 계좌 안전장치다.
    · 가상 거래는 **켈리·앙상블 학습에 넣지 않는다.**
    → 이 모듈은 `trades` 테이블 · CircuitBreaker · Kelly · `_post_exit` 를 **전혀 부르지 않는다.**
      격리는 약속이 아니라 구조다(회귀: tests/test_virtual_book.py).

청산 사다리 — 실제(`main._ts_check_exit_triggers`)를 따른다
    봉 평가 순서: 트레일링 갱신 → 하드스톱(종가 · 봉중=갱신 전 스톱) → 손절1차(종가)
                → TP1(봉 고저 = 틱 TP1 근사, 체결 = TP1 가) → TP2·TP3(종가)
                → 외부 목표(봉 고저, 체결 = 목표가) → 15:10 강제청산
    · 1계약 TP1 은 청산이 아니라 보호전환(`arm_tp1_single_contract_with_mode`) — 실제와 같다.
    · 2계약 이상 TP1 부분청산 뒤 잔량 손절 → 진입가(본전) — 실제 `_post_partial_exit` 와 같다.
    · 손절1차 체결은 `initial_quantity` 도 깎는다(실제 `shrink_initial`).
    · 외부 주체(피터·신동)는 `entry_source` 로 PositionTracker 의 외부 손절·목표 규칙을 그대로 탄다
      (ATR 손절·TP·트레일·손절계단이 꺼지고 손절 = ext_stop).
    · 미륵 가상 청산 뒤 재진입 쿨다운(익절 2분 · 손실 3분)도 실제와 같게 둔다. 외부 주체는 면제(실제와 같다).

근사인 곳 (실제와 다를 수 있다 — 결과를 실거래 성과로 읽지 말 것)
    · 체결: 진입 = 신호 가격, 청산 = 규칙 가격(스톱·TP·목표) 또는 그 시점 가격. 슬리피지 0.
    · 틱 경로는 2초 폴링 가격과 1분봉 고저로 근사한다.
    · 섀도 계측(손절1차 qty1 · 2단 · 유령스톱 등)과 역방향 클램프(P3-b)는 재현하지 않는다.
    · 계좌 단위 관문(증거금 · 무결성 · 브로커 동기화)은 실계좌 상태를 그대로 본다.

어디에 남나
    data/principal/<날짜>/virtual_book.json    열린 가상 포지션(재기동 복원용)
    data/principal/<날짜>/virtual_legs.jsonl   청산 레그(append-only). `final=True` 행이 포지션 마감
"""
import datetime

from config.constants import POSITION_FLAT, POSITION_LONG, EXTERNAL_ENTRY_SOURCES
from strategy.position.position_tracker import PositionTracker
from strategy.runtime import trade_principal as TP

RULE = 'virtual_v2(live ladder)'
STATE_NAME = 'virtual_book.json'
LEGS_NAME = 'virtual_legs.jsonl'

# 진입 출처(source) — trade_principal.SOURCE_PRINCIPAL 의 역
SOURCE_OF = dict(TP.PRINCIPAL_SOURCE)

_DT_FIELDS = ('entry_time', 'stop_updated_at', 'stop_shadow_tightened_at', 'synthetic_tp1_ts',
              'last_update_ts')
_FIELDS = ('status', 'entry_price', 'quantity', 'grade', 'regime', 'signal_direction',
           'entry_horizon', 'entry_source', 'entry_hurst_bucket', 'entry_extra_stop_mult',
           'stop_price', 'ext_stop', 'ext_target', 'ext_stop_src', 'tp1_price', 'tp2_price',
           'tp3_price', 'trailing_anchor_price', 'partial_1_done', 'partial_2_done',
           'partial_3_done', 'initial_quantity', 'entry_quantity', 'loss_tier1_price',
           'loss_tier1_done', 'synthetic_tp1_price', 'synthetic_tp1_pnl_pts',
           'synthetic_tp1_fraction', '_pos_acc_pnl_pts', '_pos_acc_fwd_pnl_pts',
           'last_update_reason') + _DT_FIELDS


class _VTracker(PositionTracker):
    """실제 PositionTracker 의 판정·계산을 그대로 쓰되 **상태 파일을 건드리지 않는다**.

    🔴 `PositionTracker._save_state()` 는 모듈 전역 `data/position_state.json` 에 쓴다 —
       가상 포지션이 그 파일을 덮으면 재기동 때 실계좌 포지션 복원이 오염된다
       (2026-06 검증 스크립트가 진입가 100.0 을 남긴 사고와 같은 경로).
    """

    def _save_state(self):
        return None

    def load_state(self):
        return False


def _iso(v):
    return v.isoformat() if isinstance(v, datetime.datetime) else v


def _parse_dt(v):
    if not v:
        return None
    try:
        return datetime.datetime.fromisoformat(str(v))
    except ValueError:
        return None


def _hm(now):
    return now.strftime('%H:%M')


class VirtualBook:
    """주체별 가상 포지션 1개씩. 모든 메서드는 예외를 밖으로 내지 않는 호출부를 전제로 한다."""

    def __init__(self, date, pt_value, force_exit='15:10', tp1_protect_mode='atr_profit',
                 protect_alpha=0.20, protect_atr_lock=0.25, persist=True):
        self.date = date
        self.pt_value = float(pt_value)
        self.force_exit = force_exit
        self.tp1_protect_mode = tp1_protect_mode
        self.protect_alpha = float(protect_alpha)
        self.protect_atr_lock = float(protect_atr_lock)
        self.persist = persist
        self.books = {}        # principal -> _VTracker
        self.meta = {}         # principal -> {origin, atr, ...}
        self.cooldown = {}     # principal -> datetime(재진입 가능 시각)
        self.last_price = None

    # ── 상태 ────────────────────────────────────────────────
    def _tracker(self, principal):
        t = self.books.get(principal)
        if t is None:
            t = _VTracker(pt_value=self.pt_value)
            self.books[principal] = t
        return t

    def status(self, principal):
        t = self.books.get(principal)
        return t.status if t is not None else POSITION_FLAT

    def is_flat(self, principal):
        return self.status(principal) == POSITION_FLAT

    def position(self, principal):
        """대시보드·피터 엔진용 요약. FLAT 이면 None."""
        t = self.books.get(principal)
        if t is None or t.status == POSITION_FLAT:
            return None
        return {'principal': principal, 'status': t.status, 'qty': int(t.quantity),
                'entry': t.entry_price, 'stop': t.stop_price, 'target': t.ext_target,
                'ext_stop': t.ext_stop, 'source': t.entry_source,
                'entry_ts': _iso(t.entry_time), 'origin': (self.meta.get(principal) or {}).get('origin')}

    def unrealized_krw(self, principal, price):
        t = self.books.get(principal)
        if t is None or t.status == POSITION_FLAT or not price:
            return None
        return t.unrealized_pnl_pts(float(price)) * self.pt_value

    # ── 진입 ────────────────────────────────────────────────
    def open(self, principal, direction, price, qty, atr, now, origin, grade='', entry_horizon=None,
             hurst_bucket=None, extra_stop_mult=1.0, ext_stop=None, ext_target=None, ext_src=None,
             why=''):
        """→ (ok, reason). 이미 보유 중 · 쿨다운이면 열지 않는다(실계좌가 단일 포지션인 것과 같다)."""
        if direction not in ('LONG', 'SHORT'):
            return False, 'invalid_direction'
        try:
            price, qty, atr = float(price), int(qty), float(atr or 0.0)
        except (TypeError, ValueError):
            return False, 'invalid_number'
        if qty <= 0 or price <= 0:
            return False, 'invalid_qty_or_price'
        if _hm(now) >= self.force_exit:
            return False, 'force_exit_time'
        if not self.is_flat(principal):
            return False, 'virtual_busy(%s)' % self.status(principal)
        cd = self.cooldown.get(principal)
        if cd is not None and now < cd:
            return False, 'virtual_cooldown(until %s)' % cd.strftime('%H:%M:%S')
        t = self._tracker(principal)
        t.entry_source = SOURCE_OF.get(principal)
        if t.entry_source in EXTERNAL_ENTRY_SOURCES:
            t.set_external_levels(stop=ext_stop, target=ext_target, src=ext_src, clear_target=True)
        else:
            t.clear_external_levels()
        _atr = atr if atr > 0 else 0.5
        t.open_position(direction, price, qty, _atr, grade=grade or '',
                        entry_horizon=entry_horizon, hurst_bucket=hurst_bucket,
                        extra_stop_mult=extra_stop_mult or 1.0)
        # 실제는 체결 보정(apply_entry_fill)이 레벨을 다시 계산한다 — TP3 는 그때만 채워진다
        t._recalculate_levels(_atr)
        t.entry_time = now
        t.stop_updated_at = now
        self.meta[principal] = {'origin': origin, 'atr': atr, 'why': why}
        self._save()
        return True, 'ok'

    # ── 외부 주체 지시 ──────────────────────────────────────
    def set_ext(self, principal, stop=None, target=None, src=None, now=None):
        t = self.books.get(principal)
        if t is None or t.status == POSITION_FLAT:
            return False
        t.set_external_levels(stop=stop, target=target, src=src)
        if now is not None:
            t.stop_updated_at = now
        self._save()
        return True

    def exit(self, principal, price, reason, now):
        """주체 지시에 의한 전량 청산(피터 미러 · 신동 미러). → 레그 목록."""
        t = self.books.get(principal)
        if t is None or t.status == POSITION_FLAT or not price:
            return []
        legs = [self._close(principal, float(price), reason, now)]
        self._save()
        return legs

    def exit_qty(self, principal, price, qty, reason, now):
        """주체 지시에 의한 부분 청산(v9 신동 1차 1계약 등). 잔량이 없어지면 전량 청산. → 레그 목록."""
        t = self.books.get(principal)
        if t is None or t.status == POSITION_FLAT or not price:
            return []
        qty = int(qty)
        if qty <= 0:
            return []
        if qty >= int(t.quantity):
            legs = [self._close(principal, float(price), reason, now)]
        else:
            legs = [self._partial(principal, t, float(price), qty, reason, now)]
        self._save()
        return legs

    # ── 평가 ────────────────────────────────────────────────
    def on_bar(self, bar, atr, now):
        """1분봉 마감 평가. bar = {ts(봉 시작 datetime), close, high, low}. → 레그 목록."""
        legs = []
        close = float(bar.get('close') or 0.0)
        if close <= 0:
            return legs
        self.last_price = close
        high = float(bar.get('high') or close)
        low = float(bar.get('low') or close)
        bar_start = bar.get('ts')
        if not isinstance(bar_start, datetime.datetime):
            bar_start = _parse_dt(str(bar_start).replace(' ', 'T')) if bar_start else None
        atr = float(atr or 0.0) or 0.5
        for p in list(self.books):
            t = self.books[p]
            if t.status == POSITION_FLAT:
                continue
            legs.extend(self._eval_bar(p, t, close, high, low, bar_start, atr, now))
        legs.extend(self._time_exit(now, close))
        if legs or any(t.status != POSITION_FLAT for t in self.books.values()):
            self._save()
        return legs

    def on_price(self, price, now):
        """2초 폴링 가격 — 외부 목표 · 틱 TP1 · 15:10. → 레그 목록."""
        legs = []
        if not price:
            return legs
        price = float(price)
        self.last_price = price
        for p in list(self.books):
            t = self.books[p]
            if t.status == POSITION_FLAT:
                continue
            if t.is_external():
                if t.is_ext_target_hit(price):
                    legs.append(self._close(p, float(t.ext_target), '가상:외부목표', now))
                continue
            if t.is_tp1_hit(price):
                legs.extend(self._tp(p, t, 1, float(t.tp1_price), now))
        legs.extend(self._time_exit(now, price))
        if legs:
            self._save()
        return legs

    def close_all(self, price, reason, now):
        legs = []
        px = float(price or self.last_price or 0.0)
        if px <= 0:
            return legs
        for p in list(self.books):
            if self.books[p].status != POSITION_FLAT:
                legs.append(self._close(p, px, reason, now))
        if legs:
            self._save()
        return legs

    # ── 내부 ────────────────────────────────────────────────
    def _eval_bar(self, p, t, close, high, low, bar_start, atr, now):
        legs = []
        long_ = t.status == POSITION_LONG
        prev_stop = t.stop_price
        t.update_trailing_stop(close, atr)
        if abs(t.stop_price - prev_stop) > 1e-9:
            t.stop_updated_at = now               # 실제 trailing 조이기 시각(벽시계 대신 평가 시각)
        # 진입 이전에 시작한 봉의 고저가는 진입 전 구간을 포함한다 — 고저 기반 판정(TP1 · 외부 목표)
        # 에서 뺀다. 봉중 스톱은 실제와 같은 423차 가드(stop_updated_at >= 봉 시작이면 생략)를 쓴다.
        intrabar_ok = bar_start is None or t.entry_time is None or t.entry_time < bar_start
        close_hit = t.is_stop_hit(close)
        intra_hit = t.is_stop_hit_intrabar(low, high, stop_price=prev_stop, bar_start=bar_start)
        if close_hit or intra_hit:
            eff = t.stop_price if close_hit else prev_stop
            px = max(eff, low) if long_ else min(eff, high)
            legs.append(self._close(p, px, '가상:하드스톱', now))
            return legs
        if t.is_loss_tier1_hit(close):
            cut = t.get_loss_tier1_exit_qty()
            if 0 < cut < t.quantity:
                # 실제 shrink_initial — initial 을 **먼저** 깎아야 partial_close 의 진행률 동기화가
                # 이 손절 레그를 TP1 달성으로 오인하지 않는다(실제 apply_exit_fill 순서와 같다).
                t.initial_quantity = max(0, int(t.initial_quantity) - cut)
                legs.append(self._partial(p, t, close, cut, '가상:손절1차 조기축소', now))
                t.loss_tier1_done = True
        if t.status != POSITION_FLAT:
            hit1 = intrabar_ok and ((high >= t.tp1_price) if long_ else (low <= t.tp1_price))
            if hit1 and not t.partial_1_done:
                legs.extend(self._tp(p, t, 1, float(t.tp1_price), now))
        for stage in (2, 3):
            if t.status == POSITION_FLAT:
                break
            if (t.is_tp2_hit(close) if stage == 2 else t.is_tp3_hit(close)):
                legs.extend(self._tp(p, t, stage, close, now))
        if t.status != POSITION_FLAT and t.is_external() and t.ext_target is not None:
            hit = intrabar_ok and ((high >= t.ext_target) if long_ else (low <= t.ext_target))
            if hit:
                legs.append(self._close(p, float(t.ext_target), '가상:외부목표', now))
        return legs

    def _tp(self, p, t, stage, px, now):
        if t.status == POSITION_FLAT:
            return []
        total = int(t.quantity)
        if total == 1 and stage == 1:
            atr = float((self.meta.get(p) or {}).get('atr') or 0.0) or 0.5
            t.arm_tp1_single_contract_with_mode(px, atr, mode=self.tp1_protect_mode,
                                                alpha_pts=self.protect_alpha,
                                                atr_lock_mult=self.protect_atr_lock)
            t.stop_updated_at = now
            return []
        q = t.get_stage_exit_qty(stage)
        if q <= 0:
            return []
        if q >= total or stage >= 3:
            return [self._close(p, px, '가상:TP%d(전량)' % stage, now)]
        leg = self._partial(p, t, px, q, '가상:TP%d 부분청산' % stage, now)
        if stage == 1 and t.status != POSITION_FLAT:
            mult = 1 if t.status == POSITION_LONG else -1
            if mult * (t.entry_price - t.stop_price) > 0:
                t.stop_price = t.entry_price          # 실제 tp1_breakeven 과 같다
                t.stop_updated_at = now
        return [leg]

    def _time_exit(self, now, price):
        if _hm(now) < self.force_exit or not price:
            return []
        out = []
        for p in list(self.books):
            if self.books[p].status != POSITION_FLAT:
                out.append(self._close(p, float(price), '가상:15:10 강제청산', now))
        return out

    def _leg(self, p, t, res, final, now):
        qty = int(res['quantity'])
        gross = float(res['pnl_pts']) * self.pt_value * qty
        meta = self.meta.get(p) or {}
        rec = {'date': self.date, 'principal': p, 'source': t.entry_source or SOURCE_OF.get(p),
               'origin': meta.get('origin'), 'rule': RULE,
               'entry_ts': _iso(t.entry_time) if t.entry_time else res.get('entry_ts'),
               'exit_ts': now.isoformat(timespec='seconds'), 'direction': res['direction'],
               'entry_px': round(float(res['entry_price']), 2), 'exit_px': round(float(res['exit_price']), 2),
               'qty': qty, 'pnl_pts': res['pnl_pts'], 'gross_krw': round(gross),
               'fee_krw': round(gross - float(res['pnl_krw'])), 'net_krw': round(float(res['pnl_krw'])),
               'reason': res['exit_reason'], 'final': final, 'grade': res.get('grade'),
               'entry_horizon': res.get('entry_horizon')}
        return rec

    def _partial(self, p, t, px, qty, reason, now):
        entry_time = t.entry_time
        res = t.partial_close(px, qty, reason)
        rec = self._leg(p, t, res, False, now)
        rec['entry_ts'] = _iso(entry_time)
        self._append(rec)
        return rec

    def _close(self, p, px, reason, now):
        t = self.books[p]
        entry_time = t.entry_time
        prior = float(t._pos_acc_pnl_pts)
        mult = 1 if t.status == POSITION_LONG else -1
        last_pts = (px - t.entry_price) * mult * int(t.quantity)
        res = t.close_position(px, reason)
        rec = self._leg(p, t, res, True, now)
        rec['entry_ts'] = _iso(entry_time)
        rec['pos_pnl_pts'] = round(prior + last_pts, 4)      # 포지션 단위(계측 4원칙 ①)
        self._append(rec)
        if p == TP.MIREUK:
            # 실제 _ts_apply_exit_cooldown — 익절 2분 · 손실 3분. 외부 주체는 실제에서도 면제다.
            self.cooldown[p] = now + datetime.timedelta(minutes=2 if rec['pos_pnl_pts'] > 0 else 3)
        self.meta.pop(p, None)
        return rec

    # ── 영속 ────────────────────────────────────────────────
    def _append(self, rec):
        if self.persist:
            TP.append_shadow(self.date, LEGS_NAME, rec)

    def snapshot(self):
        books = {}
        for p, t in self.books.items():
            if t.status == POSITION_FLAT:
                continue
            books[p] = {f: _iso(getattr(t, f, None)) for f in _FIELDS}
        return {'date': self.date, 'rule': RULE, 'books': books, 'meta': self.meta,
                'cooldown': {p: _iso(v) for p, v in self.cooldown.items()}}

    def restore(self, st):
        if not st or st.get('date') != self.date:
            return 0
        n = 0
        for p, d in (st.get('books') or {}).items():
            if p not in TP.PRINCIPALS or d.get('status') not in ('LONG', 'SHORT'):
                continue
            t = self._tracker(p)
            for f in _FIELDS:
                if f in d:
                    setattr(t, f, _parse_dt(d[f]) if f in _DT_FIELDS else d[f])
            n += 1
        self.meta = {p: m for p, m in (st.get('meta') or {}).items() if p in self.books}
        self.cooldown = {p: _parse_dt(v) for p, v in (st.get('cooldown') or {}).items() if _parse_dt(v)}
        return n

    def _save(self):
        if self.persist:
            TP.write_json(self.date, STATE_NAME, self.snapshot())


def load(date, pt_value, **kw):
    """그날 장부를 만들고 저장본이 있으면 복원한다."""
    vb = VirtualBook(date, pt_value, **kw)
    vb.restore(TP.read_json(date, STATE_NAME, None))
    return vb


def day_legs(date):
    return TP.read_jsonl(date, LEGS_NAME)


def day_positions(date):
    """레그 → 포지션(principal, entry_ts 묶음). 화면·장후 집계용."""
    pos = {}
    for r in day_legs(date):
        k = (r.get('principal'), r.get('entry_ts'))
        d = pos.setdefault(k, {'principal': r.get('principal'), 'entry_ts': r.get('entry_ts'),
                               'direction': r.get('direction'), 'entry': r.get('entry_px'),
                               'qty': 0, 'net': 0, 'exit': None, 'exit_ts': '', 'reason': '',
                               'closed': False, 'origin': r.get('origin')})
        d['qty'] += int(r.get('qty') or 0)
        d['net'] += int(r.get('net_krw') or 0)
        if str(r.get('exit_ts') or '') >= d['exit_ts']:
            d['exit_ts'] = str(r.get('exit_ts') or '')
            d['exit'] = r.get('exit_px')
            d['reason'] = r.get('reason') or ''
        if r.get('final'):
            d['closed'] = True
    return sorted(pos.values(), key=lambda x: str(x['entry_ts']))
