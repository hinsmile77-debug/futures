# -*- coding: utf-8 -*-
"""피터2 상태기계 — 트윗 사실 + 현재가 → 집행 의도. **순수**(Qt·COM·주문 없음).

입력
    ingest(tweet, engine, now, replay=False)   새 트윗 1건
    on_price(price, engine, now)               2초마다(대기 지시의 발동·만료 판정)
    on_peter2_closed(pnl_pts, now)             엔진이 피터2 포지션을 닫았다(일일 한도용)

engine(dict)
    status  'FLAT'|'LONG'|'SHORT'   엔진 포지션
    source  엔진 포지션의 entry_source(피터2면 'PETER2')
    pending 미체결 주문 존재 여부
    price   최신 미니 가격(없으면 None)
    stop / target   피터2 포지션의 현재 외부 손절·목표(미니가)

출력 — 의도(intent) 목록. main.py 가 게이트를 거쳐 집행한다.
    {'type': 'ENTER', 'side': 'LONG'|'SHORT', 'price', 'stop', 'target', 'sig', 'why'}
    {'type': 'SET_STOP', 'stop', 'sig', 'why'}
    {'type': 'SET_TARGET', 'target', 'sig', 'why'}
    {'type': 'EXIT', 'reason', 'sig', 'why'}

모든 판단은 `events` 에도 남긴다(signals.jsonl · 장중 md). 집행하지 않은 판단(기각·만료)도 남긴다 —
「왜 안 들어갔나」가 장후 복기의 절반이다.

가격 축
    피터가 = 그가 쓴 일반선물 가격. 미니가 = 피터가 + offset.
    의도의 price/stop/target 은 전부 **미니가**다.
"""
import datetime

from strategy.peter2.parse import parse_tweet

DEFAULTS = dict(
    chase=1.0, tol=0.2, arm_expire_min=10, arm_max_dist=8.0, plausible=40.0,
    default_stop=4.0, stop_cap=8.0, daily_stop_limit=2, daily_max_entries=6,
    open_hm='09:00', last_entry_hm='14:50', close_hm='15:10',
)

_SIDE_NAME = {'L': 'LONG', 'S': 'SHORT'}


def _hm(t):
    return t.strftime('%H:%M') if t else '--:--'


class Peter2Follower(object):

    def __init__(self, date, offset, offset_src='', offset_safe=True, cfg=None):
        self.date = date
        self.offset = offset
        self.offset_src = offset_src
        self.offset_safe = bool(offset_safe)
        self.cfg = dict(DEFAULTS)
        self.cfg.update(cfg or {})
        self.armed = None            # 대기 지시
        self.peter = None            # 그의 포지션(그가 트윗한 대로) — 차트·거래줄용
        self.peter_pending = None    # 그의 미체결 지시
        self.peter_trades = []       # 그의 완료 거래(피터가)
        self.consumed = set()        # 이미 집행(ENTER)한 지시 id — 재기동 중복 진입 방지
        self.entries = 0
        self.losses = 0
        self.closed = 0              # 피터2 청산 완료 포지션 수
        self.realized_pts = 0.0
        self.realized_krw = 0.0
        self.halted = None           # 당일 추종 정지 사유
        self.events = []             # 이번 호출에서 생긴 이벤트(호출부가 비운다)
        self.last_fill_offset = None  # 그의 체결가로 역산한 오프셋(모니터링)

    # ── 상태 저장/복원 ────────────────────────────────────────
    def snapshot(self):
        return {'consumed': sorted(self.consumed), 'entries': self.entries,
                'losses': self.losses, 'halted': self.halted, 'closed': self.closed,
                'realized_pts': round(self.realized_pts, 4),
                'realized_krw': round(self.realized_krw, 0)}

    def restore(self, st):
        st = st or {}
        self.consumed = set(st.get('consumed') or [])
        self.entries = int(st.get('entries') or 0)
        self.losses = int(st.get('losses') or 0)
        self.halted = st.get('halted')
        self.closed = int(st.get('closed') or 0)
        self.realized_pts = float(st.get('realized_pts') or 0.0)
        self.realized_krw = float(st.get('realized_krw') or 0.0)

    # ── 내부 도구 ─────────────────────────────────────────────
    def _ev(self, kind, now, **kw):
        e = {'kind': kind, 'hm': _hm(now)}
        e.update(kw)
        self.events.append(e)
        return e

    def _m(self, peter_px):
        """피터가 → 미니가(0.02 틱 반올림)."""
        if peter_px is None or self.offset is None:
            return None
        return round(round((peter_px + self.offset) / 0.02) * 0.02, 2)

    def _plausible(self, peter_px, price):
        if peter_px is None:
            return False
        if price is None or self.offset is None:
            return 500.0 <= peter_px <= 2500.0
        return abs((peter_px + self.offset) - price) <= self.cfg['plausible']

    def _default_stop(self, side, entry_m):
        d = self.cfg['default_stop']
        return round(entry_m - d, 2) if side == 'L' else round(entry_m + d, 2)

    def _cap_stop(self, side, entry_m, stop_m):
        cap = self.cfg['stop_cap']
        if side == 'L':
            if stop_m >= entry_m:
                return None, 'wrong_side'
            if entry_m - stop_m > cap:
                return round(entry_m - cap, 2), 'capped'
        else:
            if stop_m <= entry_m:
                return None, 'wrong_side'
            if stop_m - entry_m > cap:
                return round(entry_m + cap, 2), 'capped'
        return stop_m, None

    def _holding(self, engine):
        return engine.get('status') in ('LONG', 'SHORT') and engine.get('source') == 'PETER2'

    def _in_session(self, now):
        hm = _hm(now)
        return '08:30' <= hm < self.cfg['close_hm']

    # ── 트윗 ─────────────────────────────────────────────────
    def ingest(self, tweet, engine, now, replay=False):
        """트윗 1건. replay=True 는 재기동 복원 — 그의 상태만 되살리고 주문 의도는 내지 않는다
        (단, 아직 유효한 대기 지시는 되살린다)."""
        intents = []
        tid = str(tweet.get('id') or '')
        from strategy.peter2.store import tweet_kst
        tt = tweet_kst(tweet.get('dt'))
        if tt is None or tt.date().isoformat() != self.date:
            return intents
        res = parse_tweet(tweet.get('text') or '')
        if res.get('ignore') or not res['facts']:
            if res.get('ignore') and not replay:
                self._ev('IGNORE', tt, sig=tid, why=res['ignore'],
                         raw=(tweet.get('text') or '')[:60])
            return intents
        price = engine.get('price')
        if not replay:
            self._ev('TWEET', tt, sig=tid, raw=(tweet.get('text') or '').replace('\n', ' / ')[:120],
                     facts=[{k: v for k, v in f.items() if k not in ('lo', 'hi')}
                            for f in res['facts']])
        # 그의 상태 먼저(차트·거래줄) — 우리 집행과 무관하게 「그가 말한 것」을 기록한다
        for f in res['facts']:
            self._peter_apply(f, tt, tid)
        if not self._in_session(tt) and not replay:
            self._ev('SKIP', tt, sig=tid, why='session_closed')
            return intents
        for f in res['facts']:
            intents.extend(self._follow_apply(f, tt, tid, engine, price, now, replay))
        if replay:
            return []
        return intents

    # 그의 포지션 ------------------------------------------------
    def _peter_apply(self, f, tt, tid):
        t = f['type']
        if t == 'entry':
            if self.peter and self.peter['side'] == f['side']:
                return           # 보유 중 같은 방향 재지시(변경·수정) — 그의 포지션은 그대로
            self.peter_pending = {'side': f['side'], 'level': f['level'], 'hm': _hm(tt),
                                  'stop': None, 'target': None}
        elif t == 'fill':
            if self.peter is None:
                pend = self.peter_pending or {}
                side = f.get('side') or pend.get('side')
                lvl = f.get('level') if f.get('level') is not None else pend.get('level')
                if side and lvl is not None:
                    self.peter = {'side': side, 'entry': lvl, 'hm': _hm(tt),
                                  'stop': pend.get('stop'), 'target': pend.get('target')}
                    self.peter_pending = None
            else:
                lvl = f.get('level')
                tgt = self.peter.get('target')
                opp = f.get('side') and f['side'] != self.peter['side']
                if lvl is not None and ((tgt is not None and abs(lvl - tgt) <= 1.5) or opp):
                    self._peter_close(lvl, tt)
        elif t == 'exit':
            if self.peter is not None:
                lvl = f.get('level')
                if lvl is None:
                    lvl = self.peter.get('stop') if f.get('kind') == 'stop' else self.peter.get('target')
                self._peter_close(lvl, tt, kind=f.get('kind'))
            self.peter_pending = None
        elif t == 'stop' and f.get('level') is not None:
            tgt = self.peter if self.peter is not None else self.peter_pending
            if tgt is not None:
                tgt['stop'] = f['level']
        elif t == 'tighten':
            if self.peter is not None:
                s = self.peter.get('stop')
                if s is None or (self.peter['side'] == 'L' and f['level'] > s) \
                        or (self.peter['side'] == 'S' and f['level'] < s):
                    self.peter['stop'] = f['level']
        elif t == 'target':
            tgt = self.peter if self.peter is not None else self.peter_pending
            if tgt is not None:
                tgt['target'] = f['level']
        elif t == 'cancel':
            self.peter_pending = None

    def _peter_close(self, lvl, tt, kind=None):
        p = self.peter
        self.peter = None
        if lvl is None:
            why = '미상'
        else:
            pnl = (lvl - p['entry']) if p['side'] == 'L' else (p['entry'] - lvl)
            why = '수익' if pnl > 0 else ('손절' if pnl < 0 else '본전')
        self.peter_trades.append({'side': p['side'], 'entry': p['entry'], 'hm': p['hm'],
                                  'exit': lvl, 'exit_hm': _hm(tt), 'why': why})

    def peter_tr_text(self):
        """그의 거래줄 — `_tr.txt` 형식(피터가). 열린 포지션은 「- 미결」."""
        lines = []
        for x in self.peter_trades:
            if x['exit'] is None:
                lines.append('%s %s %g / - 미결' % (x['hm'], x['side'], x['entry']))
            else:
                lines.append('%s %s %g / %s X %g %s' % (x['hm'], x['side'], x['entry'],
                                                      x['exit_hm'], x['exit'], x['why']))
        if self.peter is not None:
            lines.append('%s %s %g / - 미결' % (self.peter['hm'], self.peter['side'],
                                               self.peter['entry']))
        return '\n'.join(lines)

    # 우리 추종 -------------------------------------------------
    def _follow_apply(self, f, tt, tid, engine, price, now, replay):
        out = []
        t = f['type']
        holding = self._holding(engine)
        hold_side = {'LONG': 'L', 'SHORT': 'S'}.get(engine.get('status'))

        if t == 'cancel':
            if self.armed:
                self._ev('DISARM', tt, sig=self.armed['sig'], why='peter_cancel')
                self.armed = None
            return out

        if t == 'exit':
            if self.armed:
                self._ev('DISARM', tt, sig=self.armed['sig'], why='peter_exited')
                self.armed = None
            if holding and not replay:
                out.append({'type': 'EXIT', 'sig': tid,
                            'reason': '피터2미러(%s)' % ('손절' if f.get('kind') == 'stop' else '청산'),
                            'why': 'peter_exit %s' % (f.get('level'),)})
            return out

        if t == 'entry':
            if not self._plausible(f['level'], price):
                self._ev('REJECT', tt, sig=tid, why='implausible_price', level=f['level'])
                return out
            if holding and hold_side == f['side']:
                # 같은 방향 재지시 — 포지션 유지, 손절·목표만 뒤따르는 사실이 갱신한다
                self._ev('KEEP', tt, sig=tid, why='same_side_while_holding')
                return out
            if holding and hold_side != f['side'] and not replay:
                out.append({'type': 'EXIT', 'sig': tid, 'reason': '피터2반대지시',
                            'why': 'opposite_entry'})
            if tid in self.consumed:
                return out
            e = self._arm(f, tt, tid, price, now if not replay else now)
            if e is None:
                return out
            return out

        if t == 'fill':
            lvl = f.get('level')
            if lvl is not None and price is not None and self.offset is not None and not replay:
                self.last_fill_offset = round(price - lvl, 2)
                self._ev('FILL_OFFSET', tt, sig=tid, implied=self.last_fill_offset,
                         used=self.offset)
            if holding:
                tgt = engine.get('target')
                stp = engine.get('stop')
                lm = self._m(lvl) if lvl is not None else None
                near = lambda a, b: a is not None and b is not None and abs(a - b) <= 1.5
                opp = f.get('side') and f['side'] != hold_side
                if (near(lm, tgt) or near(lm, stp) or opp) and not replay:
                    out.append({'type': 'EXIT', 'sig': tid, 'reason': '피터2미러(체결)',
                                'why': 'fill_at_target_or_stop'})
                return out
            if self.armed and (f.get('side') in (None, self.armed['side'])):
                # 그는 이미 들어갔다 — 돌파 조건을 「현재가 근처면 진입」으로 푼다
                self.armed['mode'] = 'limit'
                self.armed['confirmed'] = True
                self._ev('CONFIRM', tt, sig=self.armed['sig'], by=tid)
                return out
            side = f.get('side') or (self.peter or {}).get('side')
            if side and lvl is not None and tid not in self.consumed and not self.armed:
                # 지시 트윗 없이 체결만 왔다 — 체결가를 지정가로 대기
                pseudo = {'side': side, 'level': lvl, 'lo': lvl, 'hi': lvl, 'mode': 'limit'}
                if self._plausible(lvl, price):
                    self._arm(pseudo, tt, tid, price, now)
            return out

        if t == 'stop':
            if f.get('level') is None:
                return out
            sm = self._m(f['level'])
            if holding:
                if not replay:
                    out.append({'type': 'SET_STOP', 'stop': sm, 'sig': tid,
                                'why': 'peter_stop %g' % f['level']})
            elif self.armed:
                self.armed['stop_m'] = sm
                self.armed['stop_src'] = 'peter'
            return out

        if t == 'tighten':
            if holding and price is not None and not replay:
                sm = self._m(f['level'])
                cur = engine.get('stop')
                ok_now = (hold_side == 'L' and sm < price) or (hold_side == 'S' and sm > price)
                tighter = cur is None or (hold_side == 'L' and sm > cur) or (hold_side == 'S' and sm < cur)
                if ok_now and tighter:
                    out.append({'type': 'SET_STOP', 'stop': sm, 'sig': tid,
                                'why': 'peter_conditional_exit %g' % f['level']})
                else:
                    self._ev('SKIP', tt, sig=tid, why='tighten_not_applicable',
                             level=sm, price=price, stop=cur)
            return out

        if t == 'target':
            tm = self._m(f['level'])
            if holding:
                if not replay:
                    out.append({'type': 'SET_TARGET', 'target': tm, 'sig': tid,
                                'why': 'peter_target %g' % f['level']})
            elif self.armed:
                self.armed['target_m'] = tm
            return out
        return out

    def _arm(self, f, tt, tid, price, now):
        if self.offset is None:
            self._ev('REJECT', tt, sig=tid, why='no_offset')
            return None
        side = f['side']
        lo_m, hi_m = self._m(f['lo']), self._m(f['hi'])
        lvl_m = self._m(f['level'])
        if price is not None and abs(lvl_m - price) > self.cfg['arm_max_dist']:
            self._ev('REJECT', tt, sig=tid, why='too_far', level=lvl_m, price=price)
            return None
        base = max(tt, datetime.datetime.combine(tt.date(), datetime.time(9, 0)))
        stop_m, stop_src = None, 'default'
        # 같은 트윗의 손절은 ingest 가 이어서 넣는다 — 여기선 기본값으로 연다
        stop_m = self._default_stop(side, lvl_m)
        old = self.armed
        self.armed = {'sig': tid, 'side': side, 'lo_m': lo_m, 'hi_m': hi_m, 'level_m': lvl_m,
                      'peter_level': f['level'], 'mode': f['mode'], 'stop_m': stop_m,
                      'stop_src': stop_src, 'target_m': None, 'armed_at': _hm(tt),
                      'expire': base + datetime.timedelta(minutes=self.cfg['arm_expire_min']),
                      'confirmed': False}
        if old is not None and old['sig'] != tid:
            self._ev('DISARM', tt, sig=old['sig'], why='replaced_by %s' % tid)
        self._ev('ARM', tt, sig=tid, side=_SIDE_NAME[side], mode=f['mode'],
                 peter=f['level'], mini=lvl_m, offset=self.offset)
        return self.armed

    # ── 가격 ─────────────────────────────────────────────────
    def on_price(self, engine, now):
        intents = []
        a = self.armed
        price = engine.get('price')
        if a is None or price is None:
            return intents
        if now >= a['expire']:
            self._ev('EXPIRE', now, sig=a['sig'], level=a['level_m'], price=price)
            self.armed = None
            return intents
        hm = _hm(now)
        if hm < self.cfg['open_hm']:
            return intents
        if hm >= self.cfg['last_entry_hm']:
            self._ev('DISARM', now, sig=a['sig'], why='after_last_entry_time')
            self.armed = None
            return intents
        if engine.get('status') in ('LONG', 'SHORT') and engine.get('source') != 'PETER2':
            self._ev('DISARM', now, sig=a['sig'], why='engine_busy(미륵이 보유)')
            self.armed = None
            return intents
        if engine.get('status') != 'FLAT' or engine.get('pending'):
            return intents        # 피터2 반대 포지션 청산 대기 중 — 다음 폴링
        side = a['side']
        stop = a['stop_m']
        if (side == 'L' and price <= stop) or (side == 'S' and price >= stop):
            self._ev('DISARM', now, sig=a['sig'], why='stop_before_entry', price=price, stop=stop)
            self.armed = None
            return intents
        ch, tol = self.cfg['chase'], self.cfg['tol']
        lo, hi = a['lo_m'], a['hi_m']
        if a['mode'] == 'brk_up':
            hit = (lo - tol) <= price <= (hi + ch)
        elif a['mode'] == 'brk_dn':
            hit = (lo - ch) <= price <= (hi + tol)
        elif side == 'L':
            hit = price <= hi + ch
        else:
            hit = price >= lo - ch
        if a.get('confirmed') and not hit:
            # 그가 체결했다 — 지시가 ±chase 안이면 따라간다
            hit = abs(price - a['level_m']) <= ch
        if not hit:
            return intents
        if self.halted:
            self._ev('DISARM', now, sig=a['sig'], why='halted:%s' % self.halted)
            self.armed = None
            return intents
        if self.entries >= self.cfg['daily_max_entries']:
            self.halted = 'daily_max_entries'
            self._ev('HALT', now, why=self.halted)
            self.armed = None
            return intents
        if not self.offset_safe:
            self._ev('DISARM', now, sig=a['sig'], why='offset_unsafe(만기 이후 첫 실측 전)')
            self.armed = None
            return intents
        stop_m, stop_src = a['stop_m'], a['stop_src']
        chk, note = self._cap_stop(side, price, stop_m)
        if chk is None:
            # 지시 손절이 진입가의 반대편에 있다(오프셋·오독) — 기본 손절로 연다
            stop_m, stop_src = self._default_stop(side, price), 'default(%s)' % note
        elif note:
            stop_m, stop_src = chk, '%s(%s)' % (stop_src, note)
        tgt = a['target_m']
        if tgt is not None and ((side == 'L' and tgt <= price) or (side == 'S' and tgt >= price)):
            tgt = None
        self.armed = None
        self.consumed.add(a['sig'])
        intents.append({'type': 'ENTER', 'side': _SIDE_NAME[side], 'price': price,
                        'stop': stop_m, 'target': tgt, 'sig': a['sig'],
                        'stop_src': stop_src,
                        'why': '%s %s 지시 %g(미니 %g) 현재 %g' % (
                            a['mode'], _SIDE_NAME[side], a['peter_level'], a['level_m'], price)})
        return intents

    def mark_entered(self):
        self.entries += 1

    def on_peter2_closed(self, pnl_pts, now, pnl_krw=None):
        self.closed += 1
        self.realized_pts += float(pnl_pts or 0.0)
        self.realized_krw += float(pnl_krw or 0.0)
        if pnl_pts is not None and pnl_pts < 0:
            self.losses += 1
            if self.losses >= self.cfg['daily_stop_limit'] and not self.halted:
                self.halted = 'daily_stop_limit(%d)' % self.losses
                self._ev('HALT', now, why=self.halted)
                if self.armed:
                    self.armed = None
