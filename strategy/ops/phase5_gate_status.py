# strategy/ops/phase5_gate_status.py — Phase 5 실전 전환 게이트 판정기
"""`CLAUDE.md` "실전 전환 기준 (Phase 5 진입 조건)" ①~⑨의 현재 상태를 산출한다.

대시보드 좌상단 배지가 이 결과를 읽는다. Qt에 의존하지 않으므로 단위테스트·스크립트에서
그대로 부를 수 있다(`python -m strategy.ops.phase5_gate_status`로 콘솔 출력도 된다).

왜 이 모듈이 생겼나 — 배지가 화석이 됐기 때문이다
--------------------------------------------------
교체 전 좌상단 배지는 `"Phase 3 예정"`이라는 **하드코딩 문자열**이었고 800ms마다
깜빡였다. 그런데 그 툴팁이 예고한 3개 항목 중

  ① Platt Scaling 호라이즌별 적용  → 458차 A1 후보②로 **기각**(재시도 금지 등재)
  ② anti_signal 역신호 학습 채널   → 457차 "역방향 알파는 없다" 실측으로 **기각**
  ③ MFE 기반 레이블 재설계         → Triple-Barrier 경로로 대체돼 캠페인 [1]에서 검증 중

이라, 운영자가 매일 보는 자리에서 **기각된 계획을 계속 예고**하고 있었다. 착수 조건도
구버전(Sharpe만 있고 MDD·승률·⑤~⑨ 누락)이었다. 계측 4원칙 ④가 말하는 "폴백이 정상값처럼
보인다"와 같은 결함이고, 대상이 DB 컬럼이 아니라 UI였을 뿐이다.

→ 그래서 문자열을 손으로 갈아끼우지 않고 **설정값에서 매번 다시 판정**한다.

세 가지 상태로 나누는 이유 (계측 4원칙 ②)
------------------------------------------
"미측정"과 "미충족"을 같은 값으로 표현하지 않는다.

  MET        충족 — 근거를 가지고 확인됨
  OPEN       미충족 — **재봤더니** 조건을 못 만족한다(예: `CB_CONSEC_STOP_LIMIT=9999`)
  UNMEASURED 미측정 — 코드가 알 수 없다. ①③④처럼 trades.db·WFA 실측이 필요한 것.

①③④를 자동으로 "미충족"이라 찍으면 재보지도 않은 것을 재봤다고 말하는 셈이다.
배지의 분자(N/9)는 **확인된 충족만** 센다.

자동 판정은 한쪽 방향으로만 확정한다
------------------------------------
설정값은 조건 위반을 **반증**할 수는 있어도 충족을 **입증**하지 못하는 경우가 있다.
예컨대 `CB_CONSEC_STOP_LIMIT`이 9999면 ⑤가 미충족인 것은 확실하지만, 2~3으로 되돌렸다고
해서 ⑤가 끝난 것은 아니다 — v9 계획 §0-1이 "복원 후 최소 1회 정상 발동 확인"을 함께
요구한다. 그런 경우 자동 판정은 `UNMEASURED`를 내고 판단을 사람에게 넘긴다.
사람이 확인했으면 `config/settings.py:PHASE5_GATE_DECISIONS`에 기록하고, 그 기록이
자동 판정을 덮어쓴다(툴팁에 `[수동]`으로 출처가 표시된다 — 계측 4원칙 ④).

깜빡임 정책
-----------
**상시 깜빡임은 신호가 아니다.** 경보 피로로 가치가 0이 되고, 실제로 기각된 계획을
두 달 넘게 깜빡이게 만든 것이 그 결과였다. 여기서는 `PHASE5_GATE_DECISIONS`에 `due`가
적힌 게이트가 **D-7 이내로 들어오거나 기한이 지났을 때만** 깜빡인다. 그 외에는 조용히
켜져만 있는다.
"""
from __future__ import annotations

import datetime as _dt
import logging
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── 상태 3종 ──────────────────────────────────────────────────────────────
MET = "met"                # 충족 (확인됨)
OPEN = "open"              # 미충족 (재봤더니 조건 미달)
UNMEASURED = "unmeasured"  # 미측정 (코드가 알 수 없음 — 수동 판정 필요)

_STATUS_LABEL = {
    MET: "충족",
    OPEN: "미충족",
    UNMEASURED: "미측정",
}
_VALID_STATUS = frozenset(_STATUS_LABEL)

# 판정 출처 (계측 4원칙 ④ — 폴백/수동 기록이 자동 실측처럼 보이지 않게)
SRC_AUTO = "auto"        # config/settings.py 실측
SRC_MANUAL = "manual"    # PHASE5_GATE_DECISIONS 수동 기록
SRC_PENDING = "pending"  # 자동 판정 대상이 아님 — trades.db·WFA 실측이 필요

_SOURCE_LABEL = {
    SRC_AUTO: "자동",
    SRC_MANUAL: "수동",
    SRC_PENDING: "실측필요",
}

#: 툴팁 한 줄 최대 폭. QToolTip은 평문을 자동 줄바꿈하지 않아, 긴 근거 한 줄이
#: 화면 밖까지 뻗는 툴팁을 만든다. 여기서 접어서 넘긴다.
_WRAP_COLS = 78

#: 게이트별 근거를 툴팁에 몇 줄까지 보일지. 9개를 전부 펴면 60줄이 넘어 세로로 화면을
#: 벗어난다. 잘린 근거는 전문 위치를 함께 안내한다(계측 4원칙 ③ — 절단은 가시화한다).
_MAX_NOTE_LINES = 2

TOTAL_GATES = 9

#: `due`가 이 일수 이내로 들어오면(또는 지났으면) 배지가 깜빡인다.
URGENT_WITHIN_DAYS = 7

#: 모의투자용 목표자본 기본값. 이 값 그대로면 ⑧ 조건1(실전 자본 재설정)이 안 된 것이다.
_SIM_TARGET_CAPITAL_KRW = 50_000_000

#: 절대원칙 ②가 요구하는 연속손절 한도 상한(이하이면 "복원된 값").
_CB2_RESTORED_MAX = 3

#: ① "모의투자 4주 통산" 의 4주 = 거래일 20일.
_TRADING_DAYS_4W = 20

#: 손익 실측 캐시 TTL(초). 배지는 1분 타이머에 물려 있어 매분 DB 를 때릴 이유가 없다.
_PNL_CACHE_TTL_SEC = 300
_pnl_cache = {"at": None, "val": None}


class GateState(object):
    """게이트 1개의 판정 결과."""

    __slots__ = ("num", "short", "title", "status", "source", "detail",
                 "note", "due", "days_left")

    def __init__(self, num, short, title, status, source, detail,
                 note="", due=None, days_left=None):
        self.num = num
        self.short = short
        self.title = title
        self.status = status
        self.source = source
        self.detail = detail
        self.note = note
        self.due = due                # datetime.date | None
        self.days_left = days_left    # int | None (음수 = 기한 경과)

    @property
    def is_met(self):
        return self.status == MET

    @property
    def is_urgent(self):
        """기한이 D-7 이내로 들어왔거나 지났고, 아직 충족되지 않았다."""
        if self.is_met or self.days_left is None:
            return False
        return self.days_left <= URGENT_WITHIN_DAYS

    def due_text(self):
        """D-표기. 기한이 없으면 빈 문자열."""
        if self.days_left is None:
            return ""
        if self.days_left < 0:
            return "D+%d 경과" % (-self.days_left)
        if self.days_left == 0:
            return "D-DAY"
        return "D-%d" % self.days_left

    def __repr__(self):
        return "<Gate %d %s %s/%s>" % (self.num, self.short, self.status, self.source)


# ── 설정값 접근 ────────────────────────────────────────────────────────────

def _get(settings, name):
    """설정 상수를 읽는다. 없으면 None — 폴백값을 지어내지 않는다(계측 4원칙 ④)."""
    return getattr(settings, name, None)


def _chk_flag_restored(settings, flag_name):
    """"False로 꺼둔 차단 게이트를 True로 복원했는가" 형태의 공통 판정.

    ⑥⑦⑨가 모두 이 모양이다. True면 복원 결정이 내려진 것이므로 충족으로 본다.
    False는 **확실한 미충족**이다 — 단, 복원이 아니라 "재설계"를 택하는 충족 경로도
    있고 그 경우 플래그는 False로 남으므로 레지스트리에 수동 기록해야 한다.
    """
    val = _get(settings, flag_name)
    if val is None:
        return UNMEASURED, "%s 미정의 — 설정 확인 필요" % flag_name
    if val:
        return MET, "%s=True (복원됨)" % flag_name
    # 대체 충족 경로("복원 대신 재설계")는 플래그를 False로 남기므로 레지스트리 기록이
    # 필요하다 — 그 안내는 게이트별 note에 있다. 여기 한 줄에 다 넣으면 툴팁이 늘어난다.
    return OPEN, "%s=False — 복원 안 됨" % flag_name


def _recent_daily_pnl(days=_TRADING_DAYS_4W):
    """최근 N거래일의 **일별 net 손익**(원). 실패하면 `None`.

    [MW0602 475차 후속] ①④는 지금까지 `checker=None`("trades.db 실측이 필요해 코드가
    판정할 수 없다")이었다. 그런데 ①의 판정식은 SQL 한 줄이다. 손으로 적은 수치를
    노트에 남기는 방식은 이 repo 에서 이미 실패했다 — 417차의 "379건 중 86건"이
    몇 주 동안 재인용됐고 CLAUDE.md 가 그것을 직접 경고하고 있다.

    ⚠ **0을 지어내지 않는다.** DB 가 없거나 질의가 실패하면 None 이고, 호출부는
    `UNMEASURED` 로 남긴다(계측 4원칙 ②: 미측정 != 0).
    ⚠ 시스템 자동 진입만 센다(`entry_source='SYSTEM_AUTO'`) — 수동 개입을 섞으면
    "모의투자 성과"가 아니게 된다.

    ⚠ **레그/포지션 단위 주의(417차·470차 C4').** 여기는 레그를 날짜로 합칠 뿐이라
    단위 문제가 없다 — 포지션은 15:10 강제청산 때문에 날짜를 넘지 못하므로 하루치
    레그 합 == 하루치 포지션 합이다. 금지된 것은 **승률·계약수별 통계를 레그로 세는
    것**이고, 이 함수는 그런 것을 만들지 않는다(일별 금액과 양수일 수만 낸다).
    """
    import time as _time
    now = _time.time()
    if (_pnl_cache["at"] is not None
            and now - _pnl_cache["at"] < _PNL_CACHE_TTL_SEC):
        return _pnl_cache["val"]

    rows = None
    try:
        import sqlite3 as _sq
        from config.settings import TRADES_DB as _db
        import os as _os
        if _os.path.exists(_db):
            _uri = "file:%s?mode=ro" % str(_db).replace("\\", "/")
            con = _sq.connect(_uri, uri=True, timeout=2.0)
            try:
                rows = con.execute(
                    "select date(exit_ts) d, sum(net_pnl_krw) "
                    "  from trades where entry_source='SYSTEM_AUTO' "
                    "   and exit_ts is not null "
                    " group by d order by d desc limit ?", (int(days),)).fetchall()
            finally:
                con.close()
    except Exception as e:                       # DB 파손·락·스키마 변경 전부 여기로
        logger.warning("[Phase5Gate] 손익 실측 실패 — %s: %s", type(e).__name__, e)
        rows = None

    val = None if rows is None else [float(r[1] or 0.0) for r in rows]
    _pnl_cache["at"], _pnl_cache["val"] = now, val
    return val


def _chk_paper_profit(settings):
    """① 모의투자 4주 통산 수익률 양수 — **반증 전용** 자동 판정.

    이 모듈의 규율 그대로다: *"자동 판정은 한쪽 방향으로만 확정한다."*
    합이 0 이하면 **미충족이 확실하다**. 반대로 양수라고 해서 ①이 끝난 것은 아니다 —
    창이 롤링이라 내일 뒤집힐 수 있고, "4주"의 기산점을 정하는 것은 사람의 몫이다.
    그래서 양수면 수치를 보여 주고 판단은 넘긴다(`PHASE5_GATE_DECISIONS` 수동 기록).
    """
    pnl = _recent_daily_pnl()
    if pnl is None:
        return UNMEASURED, "trades.db 를 읽지 못했다 — **미측정**이지 미충족이 아니다"
    if not pnl:
        return UNMEASURED, "청산된 자동매매 거래가 없다 — 표본 0"
    total = sum(pnl)
    n_pos = sum(1 for x in pnl if x > 0)
    head = "최근 %d거래일 통산 %s원 (양수일 %d/%d)" % (
        len(pnl), "{:+,.0f}".format(total), n_pos, len(pnl))
    if len(pnl) < _TRADING_DAYS_4W:
        return UNMEASURED, "%s — 4주(%d거래일) 미달" % (head, _TRADING_DAYS_4W)
    if total <= 0:
        return OPEN, head
    return UNMEASURED, ("%s — 양수. 다만 롤링 창이라 확정은 수동 기록 필요"
                        " (④ 변동성과 함께 볼 것)" % head)


def _chk_daily_vol(settings):
    """④ 일일 수익률 변동성 안정적 — **합격선이 정의된 적이 없다.**

    ①③⑤~⑨와 달리 ④에는 숫자가 없다(③은 Sharpe 1.5 / MDD 15% / 승률 53%가 있다).
    기준이 없으면 어떤 실측으로도 충족/미충족을 말할 수 없으므로 **영구 UNMEASURED**다.
    여기서 임계를 지어내면 사전등록 원칙(§9)을 코드가 넘는 것이 된다.

    대신 **재료를 보여 준다** — 기준을 정할 때 쓸 수 있게. 2026-08-18 실측은
    표준편차가 평균의 10.6배, 양수일 35%였다. ①만 떼어 "충족"이라 읽으면 안 되는
    이유가 이 수치에 있다.
    """
    pnl = _recent_daily_pnl()
    if pnl is None:
        return UNMEASURED, "trades.db 를 읽지 못했다 — **미측정**"
    if len(pnl) < 2:
        return UNMEASURED, "표본 %d일 — 변동성 계산 불가" % len(pnl)
    n = len(pnl)
    mean = sum(pnl) / n
    var = sum((x - mean) ** 2 for x in pnl) / (n - 1)
    sd = var ** 0.5
    ratio = (sd / abs(mean)) if mean else None
    return UNMEASURED, (
        "최근 %d거래일 평균 %s원 · 표준편차 %s원%s · 양수일 %d/%d — "
        "⚠ ④는 **합격선이 정의된 적이 없다**. 판정하려면 기준부터 사전등록할 것"
        % (n, "{:+,.0f}".format(mean), "{:,.0f}".format(sd),
           ("(평균의 %.1f배)" % ratio) if ratio else "",
           sum(1 for x in pnl if x > 0), n))


def _chk_cb2(settings):
    """⑤ CB② 복원 — `CB_CONSEC_STOP_LIMIT` 9999 → 2~3."""
    lim = _get(settings, "CB_CONSEC_STOP_LIMIT")
    if lim is None:
        return UNMEASURED, "CB_CONSEC_STOP_LIMIT 미정의 — 설정 확인 필요"
    if lim > _CB2_RESTORED_MAX:
        return OPEN, ("CB_CONSEC_STOP_LIMIT=%d — 모의 유예 중"
                      "(절대원칙 ②는 3연속)" % lim)
    # 값은 되돌아왔지만 그것만으로는 끝이 아니다 — v9 계획 §0-1이 발동 1회 확인을 함께 요구.
    return UNMEASURED, ("CB_CONSEC_STOP_LIMIT=%d 복원됨 — "
                        "복원 후 정상 발동 1회 확인은 수동 기록 필요" % lim)


def _chk_sizing(settings):
    """⑧ 사이징 재설계 — 조건1(실전 자본) + 조건2(MAX_CONTRACTS 재검토)."""
    enabled = _get(settings, "SIZING_TARGET_CAPITAL_ENABLED")
    krw = _get(settings, "SIZING_TARGET_CAPITAL_KRW")
    cap = _get(settings, "MAX_CONTRACTS")
    cap_txt = "MAX_CONTRACTS=%s" % ("?" if cap is None else cap)

    if enabled is None or krw is None:
        return UNMEASURED, "SIZING_TARGET_CAPITAL_* 미정의 — 설정 확인 필요"
    if enabled and krw == _SIM_TARGET_CAPITAL_KRW:
        return OPEN, ("조건1 미충족 — 목표자본이 모의 기본값 %s원 그대로 (%s, 조건2는 431차 충족)"
                      % ("{:,}".format(krw), cap_txt))
    # 값이 바뀌었다 = 조건1이 끝났다고 단정할 수 없다. 실전 자본 확정 여부도,
    # 그에 맞춘 MAX_CONTRACTS 재산출 여부도 코드가 알 수 없다.
    state = ("enabled=False(실잔고 사용)" if not enabled
             else "목표자본 %s원" % "{:,}".format(krw))
    return UNMEASURED, ("%s — 모의 기본값에서 벗어남. 실전 자본 확정과 %s 재산출을 "
                        "함께 확인할 것" % (state, cap_txt))


def _chk_cb3_p4(settings):
    return _chk_flag_restored(settings, "CB3_P4_GRADE_BLOCK_ENABLED")


def _chk_fp_critical(settings):
    return _chk_flag_restored(settings, "FP_CRITICAL_GRADE_BLOCK_ENABLED")


def _chk_tox_spread(settings):
    return _chk_flag_restored(settings, "TOXICITY_SEVERE_SPREAD_BLOCK_ENABLED")


# ── 게이트 정의 (정본은 CLAUDE.md "실전 전환 기준") ─────────────────────────
# (번호, 짧은이름, 제목, 자동판정함수 | None)
# 자동판정함수가 None인 것은 trades.db·WFA 실측이 필요해 코드가 판정할 수 없는 게이트다.
_GATE_SPECS = (
    # [MW0602 475차 후속] ①④에 실측 배선. **충족을 자동으로 선언하지 않는다** —
    # ①은 합이 0 이하일 때만 OPEN(반증), ④는 합격선이 없어 영구 UNMEASURED.
    # 손으로 적은 수치가 몇 주씩 재인용되는 사고를 막는 것이 목적이다(417차 전례).
    (1, "수익률", "모의투자 4주 통산 수익률 양수", _chk_paper_profit),
    (2, "CB작동", "Circuit Breaker 정상 작동 + 15:10 강제청산 실집행 1회", None),
    (3, "WFA26주", "Walk-Forward 26주 통과 (Sharpe>=1.5 / MDD<=15% 자본대비 / 승률>=53%)", None),
    (4, "변동성", "일일 수익률 변동성 안정", _chk_daily_vol),
    (5, "CB2복원", "CB② 복원 (CB_CONSEC_STOP_LIMIT 9999 -> 2~3)", _chk_cb2),
    (6, "CB3-P4", "CB③-P4 재검토 (C등급 차단 복원 여부 결정)", _chk_cb3_p4),
    (7, "FP-CRIT", "FP-CRITICAL 재검토 (PSI 계측 재설계 후 복원)", _chk_fp_critical),
    (8, "사이징", "사이징 재설계 (실전 자본 + MAX_CONTRACTS 재산출)", _chk_sizing),
    (9, "TOX-SPD", "TOX-SEVERE-SPREAD 재검토 (선행: 섀도 계측 배선)", _chk_tox_spread),
)

_CIRCLED = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤",
            6: "⑥", 7: "⑦", 8: "⑧", 9: "⑨"}


def _parse_due(raw, today):
    """`"YYYY-MM-DD"` → (date, days_left). 형식이 깨졌으면 조용히 무시하지 않고 경고."""
    if not raw:
        return None, None
    try:
        due = _dt.date(*[int(x) for x in str(raw).split("-")])
    except (ValueError, TypeError):
        logger.warning("[Phase5Gate] due 날짜 형식 오류 — 무시: %r", raw)
        return None, None
    return due, (due - today).days


def evaluate(settings=None, today=None):
    """9개 게이트를 판정해 `GateState` 리스트로 돌려준다(번호 오름차순)."""
    if settings is None:
        from config import settings as _settings
        settings = _settings
    if today is None:
        today = _dt.date.today()

    registry = _get(settings, "PHASE5_GATE_DECISIONS") or {}
    out = []

    for num, short, title, checker in _GATE_SPECS:
        entry = registry.get(num) or {}
        note = str(entry.get("note") or "")
        due, days_left = _parse_due(entry.get("due"), today)

        # ① 자동 판정 (있으면)
        if checker is None:
            status, detail = UNMEASURED, "설정값으로 판정할 수 없는 게이트 — 실측 결과를 기록할 것"
            source = SRC_PENDING
        else:
            status, detail = checker(settings)
            source = SRC_AUTO

        # ② 수동 기록이 있으면 덮어쓴다 — 출처를 남긴다
        manual = entry.get("status")
        if manual is not None:
            if manual in _VALID_STATUS:
                when = entry.get("date")
                status = manual
                source = SRC_MANUAL
                detail = "수동 기록%s — 자동판정(%s)을 대체" % (
                    " %s" % when if when else "", detail)
            else:
                logger.warning(
                    "[Phase5Gate] 게이트 %d의 status 값이 잘못됐다(%r) — 자동 판정을 유지한다. "
                    "허용값: %s", num, manual, sorted(_VALID_STATUS))

        out.append(GateState(
            num=num, short=short, title=title, status=status, source=source,
            detail=detail, note=note, due=due, days_left=days_left,
        ))

    return out


def _disp_width(s):
    """표시 폭. 한글·전각 문자는 2칸으로 센다 — `len()`으로 접으면 한글 줄이 두 배로 뻗는다."""
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in s)


def _plain(text):
    """마크다운 강조 기호를 걷어낸다 — QToolTip은 평문이라 `**`가 그대로 보인다.

    근거 문장은 `settings.py`·dev_memory와 같은 문체로 쓰여 있어 `**`/백틱이 섞인다.
    보관용 원문은 그대로 두고 **표시할 때만** 벗긴다.
    """
    return str(text).replace("**", "").replace("`", "")


def _chop(word, limit):
    """공백 없이 폭을 넘는 토큰을 강제로 자른다.

    한국어 근거 문장은 공백이 드물 수 있고(경로·식별자·긴 합성어), 그런 토큰 하나가
    툴팁을 화면 밖까지 밀어낸다. 공백 경계가 없으면 폭 기준으로 끊는다.
    """
    if _disp_width(word) <= limit:
        return [word]
    out, cur, cur_w = [], "", 0
    for ch in word:
        w = _disp_width(ch)
        if cur and cur_w + w > limit:
            out.append(cur)
            cur, cur_w = ch, w
        else:
            cur += ch
            cur_w += w
    if cur:
        out.append(cur)
    return out


def _wrap(text, indent="      "):
    """문장을 툴팁 폭에 맞춰 접는다. 공백 경계 우선, 없으면 폭 기준으로 강제 절단."""
    limit = max(20, _WRAP_COLS - _disp_width(indent))
    words = []
    for raw in _plain(text).split(" "):
        words.extend(_chop(raw, limit))

    out, cur, cur_w = [], [], 0
    for word in words:
        w = _disp_width(word)
        if cur and cur_w + 1 + w > limit:
            out.append(indent + " ".join(cur))
            cur, cur_w = [word], w
        else:
            cur_w += (1 + w) if cur else w
            cur.append(word)
    if cur:
        out.append(indent + " ".join(cur))
    return out or [indent]


def summarize(gates):
    """상태별 개수 — `{"met": n, "open": n, "unmeasured": n}`."""
    counts = {MET: 0, OPEN: 0, UNMEASURED: 0}
    for g in gates:
        counts[g.status] = counts.get(g.status, 0) + 1
    return counts


def build_tooltip(gates):
    """배지 툴팁 본문. 상태·출처·기한·근거를 게이트별로 한 덩어리씩."""
    c = summarize(gates)
    lines = [
        "Phase 5 실전 전환 게이트  —  충족 %d / 미충족 %d / 미측정 %d  (총 %d)"
        % (c[MET], c[OPEN], c[UNMEASURED], TOTAL_GATES),
        "",
    ]
    for head in (
        "정본: CLAUDE.md \"실전 전환 기준 (Phase 5 진입 조건)\" ①~⑨",
        "판정 원천: [자동]=config/settings.py 실측 / [수동]=PHASE5_GATE_DECISIONS 기록",
        "⚠ [미측정]은 \"미충족\"이 아니라 \"코드가 알 수 없음\"이다 (계측 4원칙 ②).",
    ):
        lines.extend(_wrap(head, indent=""))
    lines.append("")
    truncated = []
    for g in gates:
        src = _SOURCE_LABEL.get(g.source, g.source)
        head = "[%s] %s %s" % (_STATUS_LABEL[g.status], _CIRCLED.get(g.num, str(g.num)), g.title)
        due_txt = g.due_text()
        if due_txt:
            head += "   ({} {})".format(g.due.isoformat(), due_txt)
        lines.append(head)

        # 실측 대기 게이트의 자동판정 문구는 9개 중 4개가 같은 보일러플레이트다 —
        # 근거(note)가 있으면 그쪽이 더 많은 것을 말하므로 한 줄로 줄인다.
        if g.source == SRC_PENDING and g.note:
            lines.append("      [%s]" % src)
        else:
            lines.extend(_wrap("[%s] %s" % (src, g.detail)))

        if g.note:
            body = _wrap(g.note)
            if len(body) > _MAX_NOTE_LINES:
                body = body[:_MAX_NOTE_LINES]
                body[-1] = body[-1] + " …"
                truncated.append(g.num)
            lines.extend(body)
        lines.append("")

    if truncated:
        lines.extend(_wrap(
            "근거 전문은 config/settings.py:PHASE5_GATE_DECISIONS 에 있다 (줄인 항목: %s)."
            % ", ".join(_CIRCLED.get(n, str(n)) for n in truncated), indent=""))

    urgent = [g for g in gates if g.is_urgent]
    if urgent:
        tail = ("● 깜빡임 사유 — 기한 %d일 이내: %s"
                % (URGENT_WITHIN_DAYS,
                   ", ".join("%s %s" % (g.short, g.due_text()) for g in urgent)))
    else:
        tail = ("깜빡임은 기한이 %d일 이내로 들어온 게이트가 있을 때만 발생한다."
                % URGENT_WITHIN_DAYS)
    lines.extend(_wrap(tail, indent=""))
    return "\n".join(lines)


def badge(settings=None, today=None):
    """대시보드 배지용 `(text, level, tooltip, urgent)`.

    `level`은 UI 팔레트를 모르는 채로 색을 정하기 위한 의미 단계다 —
    ``"ok"``(전부 충족) / ``"warn"``(평시) / ``"urgent"``(기한 임박·경과).
    """
    gates = evaluate(settings=settings, today=today)
    c = summarize(gates)
    urgent_gates = [g for g in gates if g.is_urgent]
    urgent = bool(urgent_gates)

    text = "Phase 5 게이트 %d/%d" % (c[MET], TOTAL_GATES)
    if urgent:
        # 가장 급한 것 하나만 배지에 — 나머지는 툴팁에 있다.
        nearest = min(urgent_gates, key=lambda g: g.days_left)
        text = "● %s · %s %s" % (text, nearest.short, nearest.due_text())

    if c[MET] == TOTAL_GATES:
        level = "ok"
    elif urgent:
        level = "urgent"
    else:
        level = "warn"

    return text, level, build_tooltip(gates), urgent


def _main():
    gates = evaluate()
    text, level, tip, urgent = badge()
    print("배지: %s   (level=%s, urgent=%s)" % (text, level, urgent))
    print("-" * 70)
    print(tip)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
