# challenger/variants/gp_rule.py — GOLDEN POWER 규칙 섀도 도전자 2종
"""[MW0601 553차 Phase 3] 「검증완료 진입청산규칙」을 섀도로 집행한다.

원문서: `docs/미륵이고도화3/Golden power/검증완료_진입청산규칙_정리.md` (2026-09-09)
사전등록: `config/settings.py:VALIDATION_CAMPAIGN["gp_rule_long_watch"|"gp_rule_short_watch"]`

🔴 **롱과 숏은 별개의 규칙이다. 조건을 섞지 말 것.**
   롱은 필터를 빼야 살고(추가조건 없음), 숏은 필터를 넣어야 산다(국면필터 필수).
   그래서 클래스를 둘로 나눈다 — 상태도 겹치지 않는다.

🔴 **실주문 없음.** `ChallengerEngine` 섀도 경로 전용이며 `REGIME_POOLS` 에 등록하지
   않는다(순위·자동승격 경로 자체가 없다 — 절대원칙 §6).

⚠ **파라미터를 여기서 바꾸지 말 것.** 사전등록이 정본이고 이 파일은 그것을 집행한다.
   관측 60거래일 중 변경은 사후 최적화다(313차 ④ · 458차 D6).
   `tests/test_553_gp_rule_challengers.py` 가 둘의 일치를 고정한다.

계측 규약
---------
· 진입하지 **않은** 이유를 `signal_meta.block` 에 남긴다 — 「신호가 없었다」와
  「조건을 못 봤다(미측정)」를 구분하기 위해서다(계측 4원칙 ②·③).
· 워밍업·재기동으로 판정 근거가 없는 분은 `unmeasured=True` 로 표시한다.
  그 분에 진입하면 **국면필터 없이 진입한 것**이 된다 — 숏에서는 −186.7pt 짜리 차이다.
"""
import logging

from challenger.variants.base_challenger import (
    BaseChallenger, ChallengerSignal, ExitReason,
)
from config.settings import (
    GP_CROSS_PERIOD, MA_REGIME_FAST, MA_REGIME_SLOW, VALIDATION_CAMPAIGN,
)

logger = logging.getLogger("CHALLENGER")

_LONG_CFG = VALIDATION_CAMPAIGN["gp_rule_long_watch"]
_SHORT_CFG = VALIDATION_CAMPAIGN["gp_rule_short_watch"]
_IDS = VALIDATION_CAMPAIGN["gp_rule_challenger_ids"]

_P = GP_CROSS_PERIOD
K_GB = "gp_buy_%d" % _P
K_GS = "gp_sell_%d" % _P
K_UP = "gp_cross_up_%d" % _P
K_DN = "gp_cross_dn_%d" % _P
K_READY = "gp_ready_%d" % _P


def _minutes_between(ts_a, ts_b):
    """'YYYY-MM-DD HH:MM:SS' 두 개의 분 차이. 파싱 실패 시 None(미측정)."""
    try:
        import datetime as _dt
        a = _dt.datetime.strptime(ts_a[:19], "%Y-%m-%d %H:%M:%S")
        b = _dt.datetime.strptime(ts_b[:19], "%Y-%m-%d %H:%M:%S")
        return (b - a).total_seconds() / 60.0
    except (TypeError, ValueError, IndexError):
        return None


class _GpRuleBase(BaseChallenger):
    """두 GP 규칙의 공통 골격. **조건은 서브클래스가 각자 정의한다.**"""

    GRADE_NA = True                 # 등급 개념이 없다 — 위장하지 않는다
    FORCE_EXIT_TIME = "15:05"       # 절대원칙 §1(15:10)보다 보수적
    SESSION_START = "09:20"
    SESSION_END = "14:50"

    def __init__(self):
        super(_GpRuleBase, self).__init__()
        self._f = {}                # 최신 봉 피처
        self._ts = ""
        self._day = ""
        self._bars_seen = 0         # 이 프로세스가 오늘 본 봉 수(워밍업 판정용)

    # ── 매분 관측 ────────────────────────────────────────────────
    def observe(self, features, context):
        ts = (context or {}).get("ts", "") or ""
        day = ts[:10]
        if day and day != self._day:
            self._day = day
            self._bars_seen = 0
            self._on_new_day()
        self._f = features or {}
        self._ts = ts
        self._bars_seen += 1
        self._on_bar()

    def _on_new_day(self):
        return None

    def _on_bar(self):
        return None

    # ── 공통 판정 ────────────────────────────────────────────────
    def _gp_ready(self):
        return bool(self._f.get(K_READY))

    def _in_window(self):
        hhmm = self._ts[11:16]
        return bool(hhmm) and self.SESSION_START <= hhmm <= self.SESSION_END

    def _num(self, key):
        try:
            v = self._f.get(key)
            return None if v is None else float(v)
        except (TypeError, ValueError):
            return None

    def _signal(self, direction, meta):
        return ChallengerSignal(
            ts=self._ts,
            challenger_id=self.challenger_id,
            direction=direction,
            # 🔴 GP 규칙에는 confidence 개념이 없다. 0.0 은 「확신 없음」이 아니라
            #   **미해당**이며, meta 가 그 사실을 명시한다(계측 4원칙 ②).
            confidence=0.0,
            grade="-",
            entry_price=None,
            signal_meta=dict(meta, rule=self.challenger_id,
                             grade_na=True, confidence_na=True),
        )


class GpLongGb90Challenger(_GpRuleBase):
    """롱 — GB 0.5 상향돌파 · 90분 보유 · 추가조건 없음.

    🔴 **필터를 붙이지 말 것.** 원문서 기각 목록: 직전압축(GB·GS≤0.5 & 스프레드≤0.5)과
      반대선 수렴을 붙이면 신호 2,620 → 1,099 로 줄면서 **300pt 를 파괴**한다
      (90분 +432 → +131). 「개선」하고 싶으면 그건 다른 규칙이므로 새 채널을 판다.

    ⚠ 이 규칙은 알파가 아니다 — 손익의 59%가 시장 드리프트(β=+0.463, t=10.87)이고
      α 는 t=1.46 으로 유의하지 않다. 사전등록의 1차 합격선이 총손익이 아니라
      **동일노출 단순보유 대조군 우위**인 이유다.
    """

    challenger_id = _IDS["long"]
    name_kr = "GP롱 - GB단순돌파 90분"
    HOLD_MINUTES = int(_LONG_CFG["hold_minutes"])

    def generate_signal(self, features, context):
        meta = {}
        if not self._gp_ready():
            # 워밍업(20봉)·재기동 직후 — 「신호 없음」이 아니라 **미측정**이다.
            meta.update(block="gp_unready", unmeasured=True)
            return self._signal(0, meta)
        if not self._in_window():
            meta.update(block="out_of_window",
                        window="%s~%s" % (self.SESSION_START, self.SESSION_END))
            return self._signal(0, meta)

        cross = self._num(K_UP)
        meta.update(gp_cross_up=cross, gb=self._num(K_GB), gs=self._num(K_GS))
        if not cross:
            meta.update(block="no_cross")
            return self._signal(0, meta)
        return self._signal(1, meta)

    def should_exit(self, trade, current_price, current_ts, atr=None):
        """90분 시간청산 단독. 손절 없음 — 시간손절이 그 역할을 한다.

        ⚠ 15:05 강제청산은 **엔진**이 `FORCE_EXIT_TIME` 으로 처리한다.
        """
        held = _minutes_between(trade.entry_ts, current_ts)
        if held is None:
            # ts 를 못 읽으면 보유 시간을 모른다 — 닫지도, 「아직 멀었다」고 하지도 않는다.
            logger.warning("[GP롱] 보유시간 계산 불가 entry=%s now=%s",
                           trade.entry_ts, current_ts)
            return None
        return ExitReason.TIME if held >= self.HOLD_MINUTES else None


class GpShortSqz60Challenger(_GpRuleBase):
    """숏 — 압축 → GS 0.5 상향돌파 · 하락추세 한정 · 60분 / GS≥1.2.

    🔴 **국면필터(MA20<MA60)는 선택이 아니다.** MA20>MA60 구간만 떼면
      −186.7pt (t=−2.71, 유의한 손실) — 필터를 빼는 순간 전략이 마이너스로 뒤집힌다.
      그래서 필터를 **읽을 수 없으면 진입하지 않는다**(계측 4원칙 ②):
      `ma_cont_ready=False` 인 분에 진입하면 필터 없이 진입한 것이 된다.

    ⚠ `ma_basis="cont"` 확정(2026-09-10 사용자 결정) — 연속 이동평균을 쓴다.
    """

    challenger_id = _IDS["short"]
    name_kr = "GP숏 - 압축돌파 하락추세 60분"
    HOLD_MINUTES = int(_SHORT_CFG["hold_minutes"])
    EXIT_GS = float(_SHORT_CFG["exit_gs_target"])
    SQZ_GB_MAX = float(_SHORT_CFG["squeeze_gb_max"])
    SQZ_GS_MAX = float(_SHORT_CFG["squeeze_gs_max"])
    SQZ_SPREAD_MAX = float(_SHORT_CFG["squeeze_spread_max"])
    SQZ_VALID_BARS = int(_SHORT_CFG["squeeze_valid_bars"])
    TRIGGER_GB_MAX = float(_SHORT_CFG["trigger_gb_max"])
    MAX_PER_DAY = int(_SHORT_CFG["max_per_day"])
    MA_BASIS = _SHORT_CFG["ma_basis"]

    K_MA_DOWN = "ma_regime_down_%s" % _SHORT_CFG["ma_basis"]
    K_MA_READY = "ma_%s_ready" % _SHORT_CFG["ma_basis"]

    def __init__(self):
        super(GpShortSqz60Challenger, self).__init__()
        self._sqz_bar = None        # 마지막 압축 발생 봉 번호(세션 내 순번)
        self._bar_no = 0

    def _on_new_day(self):
        self._sqz_bar = None
        self._bar_no = 0

    def _on_bar(self):
        """압축 상태를 매분 갱신한다. **트리거보다 먼저** 관측돼야 한다."""
        self._bar_no += 1
        gb, gs = self._num(K_GB), self._num(K_GS)
        if not self._gp_ready() or gb is None or gs is None:
            return
        if (gb <= self.SQZ_GB_MAX and gs <= self.SQZ_GS_MAX
                and abs(gb - gs) <= self.SQZ_SPREAD_MAX):
            self._sqz_bar = self._bar_no

    def _sqz_window_warm(self):
        """압축 상태를 판정할 만큼 이 프로세스가 봉을 봤는가.

        🔴 재기동이 압축 이력을 지운다. 그 직후 트리거가 떠도 「압축이 없었다」가
          아니라 **모른다**이므로 진입하지 않고 `unmeasured` 로 기록한다.
        """
        return self._bars_seen > self.SQZ_VALID_BARS

    def generate_signal(self, features, context):
        meta = {"ma_basis": self.MA_BASIS}
        if not self._gp_ready():
            meta.update(block="gp_unready", unmeasured=True)
            return self._signal(0, meta)
        if not self._in_window():
            meta.update(block="out_of_window")
            return self._signal(0, meta)

        cross = self._num(K_DN)
        gb = self._num(K_GB)
        meta.update(gp_cross_dn=cross, gb=gb, gs=self._num(K_GS),
                    sqz_bar=self._sqz_bar, bar_no=self._bar_no)
        if not cross:
            meta.update(block="no_cross")
            return self._signal(0, meta)

        # ② 반대선 수렴
        if gb is None or gb > self.TRIGGER_GB_MAX:
            meta.update(block="gb_not_converged", gb_max=self.TRIGGER_GB_MAX)
            return self._signal(0, meta)

        # ① 압축이 10봉 이내에 있었는가
        if not self._sqz_window_warm():
            meta.update(block="sqz_state_unknown", unmeasured=True,
                        bars_seen=self._bars_seen)
            return self._signal(0, meta)
        if self._sqz_bar is None or (self._bar_no - self._sqz_bar) > self.SQZ_VALID_BARS:
            meta.update(block="no_recent_squeeze", valid_bars=self.SQZ_VALID_BARS)
            return self._signal(0, meta)

        # ③ 국면필터 — 읽을 수 없으면 진입하지 않는다
        if not self._f.get(self.K_MA_READY):
            meta.update(block="ma_unready", unmeasured=True,
                        ma_fast=MA_REGIME_FAST, ma_slow=MA_REGIME_SLOW)
            return self._signal(0, meta)
        ma_down = self._num(self.K_MA_DOWN)
        meta.update(ma_regime_down=ma_down)
        if not ma_down:
            meta.update(block="regime_not_down")
            return self._signal(0, meta)

        return self._signal(-1, meta)

    def should_exit(self, trade, current_price, current_ts, atr=None):
        """GS ≥ 1.2 도달 · 60분 시간손절. 반대선(GB) 손절은 **쓰지 않는다**.

        원문서: GS 1.5 는 분포의 91백분위라 도달 자체가 어려워 청산의 47%가 시간만료로
        끝났다. 1.2 는 약 82백분위로 실제로 작동한다.
        """
        gs = self._num(K_GS)
        if gs is not None and gs >= self.EXIT_GS:
            return ExitReason.TP1
        held = _minutes_between(trade.entry_ts, current_ts)
        if held is None:
            logger.warning("[GP숏] 보유시간 계산 불가 entry=%s now=%s",
                           trade.entry_ts, current_ts)
            return None
        return ExitReason.TIME if held >= self.HOLD_MINUTES else None
