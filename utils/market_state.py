# utils/market_state.py — 시장 상태 감지 (거래불능 구간)
"""가격상한 고착(limit-pin) 구간 감지 — 404차 후속5 / P0-B 신설.

## 무엇을 잡는가

가격이 일중 극단(상한가/하한가로 추정되는 가격)에 붙은 채 거래량이 붕괴한 구간.
2026-07-31 14:21~15:06이 실측 사례다(1036.28 고착, 분당 거래량 1~27, 세션
중앙값 344 대비, 29개 분봉이 `high == low`, 10개 분봉은 아예 결측).

## 왜 "상한가"라고 단정하지 않고 경험적으로 감지하는가

브로커는 당일 상한가/하한가를 실시간으로 내려준다(`config/constants.py`의
`FID_UPPER_LIMIT=305` / `FID_LOWER_LIMIT=306`). 그런데 이 두 상수는 **정의만
돼 있고 코드 어디에서도 사용되지 않는다** — 즉 정답을 받을 수 있는데 수집하지
않고 있다. 그 배선 전까지는 과거 데이터에 대해 확정값이 없으므로 분봉 형태로
추론한다. FID 배선이 끝나면 이 모듈의 판정은 확정값 대조로 대체·검증할 수 있다
(`dev_memory/NEXT_TODO.md` 404차 후속5 항목).

## 판정 3조건 (전부 실측 캘리브레이션)

1. `high == low == 일중극단` — 가격 미형성
2. `volume <= LIMIT_PIN_VOL_MAX` — 체결 붕괴
   실측 근거: 캠페인 7,167분봉 중 non-zero-range 분봉의 volume p1=79, 최소 4.
   zero-range 분봉 57개는 1개(vol 49)를 빼고 전부 30 이하 — 두 분포가 갈린다.
3. 그 극단이 **유동 분봉으로 뒷받침될 것** (`LIMIT_PIN_LIQUID_VOL_MIN` 이상
   거래된 분봉이 같은 가격을 터치했을 것)

3번은 **장 초반 유동성 공백을 상한가로 오탐하는 것을 막는 방어 조건**이다.
2026-07-31 09:00~09:04 zero-range 4개 분봉(932.66, vol 1·5·4·2)이 그 패턴으로,
이 가격은 그날 일중저가지만 터치 분봉 최대 volume이 29에 불과하다 — 상한가가
아니라 개장 직후 잔여 유동성 공백이다. 반면 진짜 상한가 1036.28은 volume 100
초과 분봉 13개(최대 642)가 터치했다. 29 vs 104의 3.5배 여유로 갈린다.

> **정직한 계측 주석**: 현재 캠페인 표본(7,167분봉)에서 3번 조건을 꺼도 결과는
> 바뀌지 않는다 — 위 09:00~09:04 사례가 4개 분봉뿐이라 2번 다음의 `min_bars=5`가
> 먼저 걸러내기 때문이다. 즉 3번은 지금 **무효과이며 방어용**이다. 같은 패턴이
> 5분봉 이상 이어지는 날에는 실제로 필요해지므로 유지한다(합성 표본 회귀 테스트로
> 동작을 확인해 두었다 — 아래 `__main__` 참조).

## 이 구간의 데이터를 어떻게 다뤄야 하는가 — 중요

**MFE/MAE 같은 max/min 연산에는 원리적으로 무해하다.** 가격이 상한에 붙으려면
먼저 유동적으로 그 가격에 도달해야 하고, 붙어 있는 동안은 `high == low`다. 즉
limit-pin 분봉은 **새로운 극단을 만들지 못하고 기존 극단을 반복**할 뿐이다.
2026-07-31 실측에서도 29개 고착 분봉을 전부 제거해도 MFE는 한 틱도 변하지 않았다.
(예외: 갭 상한가 직행 — 유동 분봉 없이 극단이 생길 수 있다. 이번 표본엔 없음)

**실제 오염은 counterfactual의 진입가·목표가 쪽이다.** 07-31 14:17 LONG 섀도 행이
`entry_price=1036.28`(상한가) / `tp1_price=1037.07`(상한 초과 = 도달 불가)로 기록돼
있었다 — 이기는 경우의 수가 구조적으로 0인 가상거래다. 그런 행을 "차단이 옳았다"의
근거로 집계하면 안 된다(`scripts/generate_validation_campaign_report.py` 참조).

**체결 방향(어느 쪽이 체결 가능했는가)은 추론하지 말 것.** 07-31 고착 구간의
`buy_vol`/`sell_vol`은 13개 분봉이 둘 다 0(미분류)이고, 호가는 역전돼 있었다
(bid1 1036.28 > ask1 1036.26, 12/36 분봉은 null). 이 데이터로 방향 비대칭 체결
가정을 세우면 열화된 피드에 과적합하는 꼴이 된다.
"""
from typing import Dict, List, Optional, Sequence

# ── 판정 파라미터 (실측 캘리브레이션 — 위 docstring 근거 참조) ──────────────
LIMIT_PIN_VOL_MAX = 30          # 고착 분봉으로 볼 volume 상한
LIMIT_PIN_MIN_BARS = 5          # 하루/연속 최소 고착 분봉 수 — 우발적 1분 배제
LIMIT_PIN_LIQUID_VOL_MIN = 100  # "유동 분봉" 기준 volume
SESSION_OPEN_HHMM = "09:00"     # 프리장(08:45~09:00) 제외 — 상시 저유동이라 오탐원


def _get(bar, key, default=None):
    """dict / sqlite3.Row 양쪽에서 안전하게 값 추출."""
    try:
        v = bar[key]
    except (KeyError, IndexError, TypeError):
        return default
    return default if v is None else v


def _session_bars(bars: Sequence, session_open: str) -> List:
    return [b for b in bars if str(_get(b, "ts", ""))[11:16] >= session_open]


def _is_pinned(bar, extreme: float, vol_max: int) -> bool:
    hi = _get(bar, "high")
    lo = _get(bar, "low")
    if hi is None or lo is None:
        return False
    return float(hi) == float(lo) == float(extreme) and int(_get(bar, "volume", 0)) <= vol_max


def _corroborated(bars: Sequence, price: float, side: str, liquid_vol_min: int) -> bool:
    """극단 가격이 유동 분봉으로 뒷받침되는가 (장초반 유동성 공백 오탐 방지)."""
    field = "high" if side == "UP" else "low"
    for b in bars:
        v = _get(b, field)
        if v is None:
            continue
        if float(v) == float(price) and int(_get(b, "volume", 0)) >= liquid_vol_min:
            return True
    return False


def detect_limit_pin_bars(
    bars: Sequence,
    vol_max: int = LIMIT_PIN_VOL_MAX,
    min_bars: int = LIMIT_PIN_MIN_BARS,
    liquid_vol_min: int = LIMIT_PIN_LIQUID_VOL_MIN,
    session_open: str = SESSION_OPEN_HHMM,
) -> Dict[str, str]:
    """[오프라인] 하루치 분봉 → {ts: 'UP'|'DOWN'} 고착 분봉 맵.

    여러 날이 섞여 들어와도 **일자별로 분리해서** 판정한다(일중 극단은 날짜별
    개념이므로). 반환 맵은 전체 일자를 합친 것이다.

    Args:
        bars: ts/high/low/volume 을 갖는 dict 또는 sqlite3.Row 시퀀스
    """
    by_day: Dict[str, List] = {}
    for b in bars:
        ts = str(_get(b, "ts", ""))
        if len(ts) < 10:
            continue
        by_day.setdefault(ts[:10], []).append(b)

    flagged: Dict[str, str] = {}
    for _day, day_bars in by_day.items():
        sess = _session_bars(day_bars, session_open)
        if not sess:
            continue
        highs = [float(_get(b, "high")) for b in sess if _get(b, "high") is not None]
        lows = [float(_get(b, "low")) for b in sess if _get(b, "low") is not None]
        if not highs or not lows:
            continue
        day_high, day_low = max(highs), min(lows)

        for side, extreme in (("UP", day_high), ("DOWN", day_low)):
            pinned = [b for b in sess if _is_pinned(b, extreme, vol_max)]
            if len(pinned) < min_bars:
                continue
            if not _corroborated(sess, extreme, side, liquid_vol_min):
                continue    # 장초반 유동성 공백 등 — 상한가 아님
            for b in pinned:
                flagged[str(_get(b, "ts"))] = side
    return flagged


def is_untradeable_now(
    bars: Sequence,
    vol_max: int = LIMIT_PIN_VOL_MAX,
    min_bars: int = LIMIT_PIN_MIN_BARS,
    session_open: str = SESSION_OPEN_HHMM,
) -> dict:
    """[라이브] 당일 분봉(시각 오름차순, 최신이 마지막) → 현재 거래불능 여부.

    ## 오프라인판과 의도적으로 다른 정의를 쓴다

    `detect_limit_pin_bars()`는 "이 가격이 그날의 가격상한이었나"를 묻는다 — 판정에
    **최종** 일중극단이 필요하므로 장 종료 후에만 답할 수 있다. 라이브가 물어야 할
    것은 그게 아니라 **"지금 체결이 가능한가"** 다. 규제 상한가든 점심 공백이든
    `high == low` + 거래량 붕괴가 N분 이어지면 어느 쪽이든 주문이 안 나간다.

    실측 근거(캠페인 6,886 세션분봉 재생): "누적극단 + 유동뒷받침"까지 요구한
    변형과 "연속 N분 zero-range + vol 상한"만 보는 이 변형이 **완전히 동일한
    결과**를 냈다(23분봉, 2026-07-13 12:36~12:37 · 07-31 14:26~15:06). 추가 조건이
    라이브 경로에서 아무 일도 하지 않으므로 단순한 정의를 택한다.

    2026-07-13 12:36~12:37 발동은 상한가가 아니다(1108.88이 12:38에 1098.92로 뚫림).
    그러나 그 6분간 vol 4~21의 zero-range였으므로 **차단 자체는 타당하다** — 이
    함수는 상한가 판별기가 아니라 거래가능성 판별기다.

    결측 분봉은 리스트에 없으므로 연속 판정에서 자연히 건너뛴다(07-31 14:24·14:31
    등이 결측이었지만 지장 없음). min_bars 만큼 쌓여야 발동하므로 라이브에서는
    구조적으로 수 분 지연된다 — 오탐보다 지연이 낫다는 보수적 설계다.

    Returns:
        {"blocked": bool, "run_len": int, "price": float|None,
         "at_session_extreme": 'UP'|'DOWN'|None, "reason": str}
        at_session_extreme 은 참고용 맥락일 뿐 판정에 쓰이지 않는다.
    """
    out = {"blocked": False, "run_len": 0, "price": None,
           "at_session_extreme": None, "reason": "거래불능 아님"}
    # 호출부(main.py)는 `fetch_recent_raw_candles(limit=N)`로 최근 N봉을 받는데 이 쿼리는
    # **날짜를 넘나든다.** 전일 장마감 근처 분봉이 섞이면 "연속 고착"이 날짜를 건너뛰어
    # 이어진 것처럼 보이므로, 가장 최근 일자만 남긴다.
    dated = [b for b in bars if len(str(_get(b, "ts", ""))) >= 10]
    if dated:
        today = max(str(_get(b, "ts"))[:10] for b in dated)
        bars = [b for b in dated if str(_get(b, "ts"))[:10] == today]
    sess = _session_bars(bars, session_open)
    if len(sess) < min_bars:
        out["reason"] = "세션 분봉 부족(%d < %d)" % (len(sess), min_bars)
        return out

    run, price = 0, None
    for b in reversed(sess):
        hi, lo = _get(b, "high"), _get(b, "low")
        if hi is None or lo is None:
            break
        if float(hi) == float(lo) and int(_get(b, "volume", 0)) <= vol_max:
            run += 1
            price = float(hi)
        else:
            break
    if run < min_bars:
        out["run_len"] = run
        return out

    highs = [float(_get(b, "high")) for b in sess if _get(b, "high") is not None]
    lows = [float(_get(b, "low")) for b in sess if _get(b, "low") is not None]
    at_ext = None
    if highs and price == max(highs):
        at_ext = "UP"
    elif lows and price == min(lows):
        at_ext = "DOWN"

    out.update({
        "blocked": True, "run_len": run, "price": price, "at_session_extreme": at_ext,
        "reason": "거래불능 %d분 연속 @%.2f (zero-range, vol<=%d)%s"
                  % (run, price, vol_max,
                     "" if at_ext is None else " — 세션 %s 극단" % at_ext),
    })
    return out


# KRX 파생 일일 가격제한폭 3단계 (기준가격 = 전일 정산가격 대비).
# 근거: docs/CyBos ref/코스피200_미니선물_가격제한_규정.md §1
# 미니선물도 정규 코스피200선물과 동일하다(사이즈만 1/5).
PRICE_LIMIT_STAGES = (0.08, 0.15, 0.20)


def effective_price_limits(base: float, price: float,
                           session_high: float = 0.0,
                           session_low: float = 0.0) -> dict:
    """[404차 후속8] 기준가격과 현재가로 **지금 유효한** 상·하한을 산출한다.

    ## 왜 스냅샷 값을 그대로 쓰면 안 되는가

    가격제한폭은 고정이 아니라 **장중에 확대된다** — 상·하한가 도달 후 5분이 지나면
    다음 단계로 열린다(±8% → ±15% → ±20%). 그런데 이 시스템은 FutureMst 스냅샷을
    **기동 시 1회**만 읽는다(`_prime_from_snapshot`). 기동 시각(08:45~08:55)에는 항상
    1단계(±8%)이므로, 장중에 확대되면 캐시가 낡아 **정작 상한가 날에 기능이 조용히
    무력화**된다. COM 재조회는 BlockRequest가 최대 30초 파이프라인을 막을 수 있어
    매분 돌리기에 위험하다.

    기준가격은 하루 동안 바뀌지 않고 단계 비율은 규정 상수이므로, **추가 조회 없이
    산술로 유도**할 수 있다. 확대는 "이미 도달한 단계의 다음"으로만 열리므로, 지금
    유효한 상한은 **현재가 이상인 가장 낮은 단계**다.

    ## 방향별 독립

    규정 §2-① "확대는 **한 방향으로만** 적용 — 상승 쪽 제한폭이 열려도 하락 쪽은 기존
    단계 유지". 그래서 상·하한을 각자 계산한다. 2026-08-01 실측이 정확히 이 모습이었다
    (상한 +20% 확대 / 하한 -8% 1단계 유지).

    ## 왜 현재가가 아니라 세션 고가/저가로 단계를 정하는가 — 래칫

    한 번 확대된 제한폭은 **당일 중 축소되지 않는다.** 현재가만으로 재계산하면 가격이
    되돌릴 때 단계가 역행한다 — 07-31 재생에서 09:11에 3단계로 열린 뒤 09:17에 종가가
    993.10으로 밀리자 2단계로 되돌아갔고, 그 결과 LONG 차단이 353분봉 중 38개(10.8%)로
    과잉 발생했다. 실제로는 그 시점 상한이 1036.30이라 상방 여지가 충분했다.

    확대는 "제한선 **도달**"로 발동하므로 **세션 고가**가 그 도달 이력을 그대로 보존한다.
    고가 기준으로 단계를 정하면 별도 상태 없이 래칫이 성립한다(하한은 세션 저가).
    고가/저가가 없으면 현재가로 폴백한다.

    Args:
        base:         기준가격(전일 정산가격). FutureMst [13].
        price:        현재가 (고가/저가 미제공 시 폴백)
        session_high: 당일 세션 고가 — 상한 단계 판정용
        session_low:  당일 세션 저가 — 하한 단계 판정용
    Returns:
        {"upper": float, "lower": float, "upper_stage": int, "lower_stage": int}
        (base<=0 이면 전부 0.0 / 0)
    """
    out = {"upper": 0.0, "lower": 0.0, "upper_stage": 0, "lower_stage": 0}
    try:
        b, px = float(base or 0.0), float(price or 0.0)
        hi = float(session_high or 0.0) or px
        lo = float(session_low or 0.0) or px
    except (TypeError, ValueError):
        return out
    if b <= 0:
        return out
    hi = max(hi, px)          # 현재가가 기록된 고가를 넘어섰으면 그쪽이 최신이다
    lo = min(lo, px) if lo > 0 else px

    # 상한: 세션 고가 이상인 가장 낮은 단계. 전부 밑돌면 최종단계(더 열릴 곳이 없다).
    for n, r in enumerate(PRICE_LIMIT_STAGES, start=1):
        cap = b * (1.0 + r)
        if hi <= cap or n == len(PRICE_LIMIT_STAGES):
            out["upper"], out["upper_stage"] = cap, n
            break
    # 하한: 세션 저가 이하인 가장 높은 단계.
    for n, r in enumerate(PRICE_LIMIT_STAGES, start=1):
        flr = b * (1.0 - r)
        if lo >= flr or n == len(PRICE_LIMIT_STAGES):
            out["lower"], out["lower_stage"] = flr, n
            break
    return out


def is_at_daily_limit(price, limits, direction, tick: float = 0.0) -> dict:
    """[404차 후속6] 진입 방향이 당일 가격제한선에 막혀 있는가.

    ## `is_untradeable_now()`가 못 잡는 구멍을 메운다

    거래불능 감지는 "체결이 붕괴한 뒤"에야 발동한다(연속 N분 필요). 그래서 **아직
    유동적인 상태에서 상한가에 진입**하는 것은 못 막는다 — 2026-07-31 14:17 LONG이
    정확히 그 사례로, 그 분봉은 vol 109로 멀쩡했고 게이트는 14:26부터 발동했다.
    그때 진입했다면 TP1(1037.07)이 상한(1036.28) 밖이라 채워질 수 없고 스톱만 맞는
    구조였다(섀도 counterfactual 실측 −2.366pt).

    이 함수는 그 구멍을 **방향별로** 막는다: 상한가에서 LONG은 상방 여지가 물리적으로
    0이므로 차단하고, SHORT는 막지 않는다(되돌림 베팅은 상한선과 무관하다). 하한가는 반대.

    Args:
        price:     현재가
        limits:    {"upper": float, "lower": float, "base": float}
                   `base`(기준가격)가 있으면 **그쪽을 우선**해 지금 유효한 단계를
                   산출한다(`effective_price_limits`). 기동 시 1회 읽은 upper/lower는
                   장중 단계 확대를 반영하지 못하기 때문이다. 전부 0.0/None이면
                   정보 없음으로 보고 차단하지 않는다.
        direction: "LONG" | "SHORT" (대소문자 무관)
        tick:      호가 단위. >0이면 "상한가 1틱 이내"까지 포함해 판정한다
                   (정확히 상한가에 붙기 직전도 상방 여지가 1틱뿐이라 의미가 없다)

    Returns:
        {"blocked": bool, "reason": str, "limit": float|None, "source": str}
    """
    out = {"blocked": False, "reason": "", "limit": None, "source": ""}
    try:
        px = float(price or 0.0)
    except (TypeError, ValueError):
        return out
    if px <= 0 or not limits:
        return out
    d = str(direction or "").upper()
    eps = max(0.0, float(tick or 0.0))

    eff = effective_price_limits(
        limits.get("base"), px,
        session_high=limits.get("session_high") or 0.0,
        session_low=limits.get("session_low") or 0.0)
    if eff["upper"] > 0:
        up, dn = eff["upper"], eff["lower"]
        out["source"] = "기준가 유도(%d/%d단계)" % (eff["upper_stage"], eff["lower_stage"])
    else:
        up = float(limits.get("upper") or 0.0)
        dn = float(limits.get("lower") or 0.0)
        out["source"] = "스냅샷 캐시"

    # ── 초과 방어: 가격이 제한선을 **넘어서** 있으면 차단하지 않는다 ──────────
    # 진짜 제한선은 정의상 넘을 수 없다. 넘었다면 그 값이 오래됐거나(단계 확대 미반영)
    # 이 종목에 안 맞는 값이라는 뜻이므로, 그걸 근거로 막으면 오차단이 된다.
    #
    # 왜 필요한가 — 2026-08-01 실측에서 [17]=기준가×1.20(확대됨) / [18]=기준가×0.92
    # (1단계)로 **비대칭**이었다. 상한은 그날 실제로 닿아서 3단계까지 확대됐고 하한은
    # 닿지 않아 1단계에 머문 것으로 보이는데, "닿은 쪽만 확대"인지 "양쪽 확대인데 보고만
    # 이런지"는 확인되지 않았다. 만약 하한이 −8%로 고정이라면 07-28(−11.64%) 같은
    # 폭락일에 종가가 하한선 아래에 놓여 SHORT가 하루 종일 잘못 막힌다.
    # 이 가드가 있으면 그 경우 px < dn 이 되어 자동으로 차단이 해제되므로,
    # 하한 필드의 동적 여부를 몰라도 안전하다.
    if d == "LONG" and up > 0:
        if px > up:
            out["reason"] = "상한가(%.2f)를 현재가(%.2f)가 초과 — 값 신뢰 불가, 차단 안 함" % (up, px)
        elif px >= up - eps:
            out.update({"blocked": True, "limit": up,
                        "reason": "상한가 %.2f 도달(현재가 %.2f) — LONG 상방 여지 없음" % (up, px)})
    elif d == "SHORT" and dn > 0:
        if px < dn:
            out["reason"] = "하한가(%.2f)를 현재가(%.2f)가 하회 — 값 신뢰 불가, 차단 안 함" % (dn, px)
        elif px <= dn + eps:
            out.update({"blocked": True, "limit": dn,
                        "reason": "하한가 %.2f 도달(현재가 %.2f) — SHORT 하방 여지 없음" % (dn, px)})
    return out


if __name__ == "__main__":
    # 3번 조건(유동 뒷받침)이 실제로 동작하는지 합성 표본 회귀 테스트.
    # 실데이터에서는 min_bars가 먼저 걸러 무효과라 이 경로가 검증되지 않는다.
    def _bar(hhmm, hi, lo, vol):
        return {"ts": "2026-01-02 %s:00" % hhmm, "high": hi, "low": lo, "volume": vol}

    # 개장 직후 유동성 공백이 5분봉 이어지는 날 — 상한가로 오탐하면 안 된다.
    gap = ([_bar("09:0%d" % i, 100.0, 100.0, 3) for i in range(5)]
           + [_bar("09:1%d" % i, 110.0 + i, 99.0, 500) for i in range(5)])
    assert detect_limit_pin_bars(gap) == {}, "장초반 공백을 고착으로 오탐"

    # 같은 형태지만 그 가격을 유동 분봉이 터치한 경우 — 진짜 고착으로 잡아야 한다.
    real = ([_bar("09:1%d" % i, 110.0, 99.0, 500) for i in range(5)]
            + [_bar("14:2%d" % i, 110.0, 110.0, 3) for i in range(5)])
    got = detect_limit_pin_bars(real)
    assert len(got) == 5 and set(got.values()) == {"UP"}, got

    # 라이브 판정
    assert is_untradeable_now(gap[:5])["blocked"] is True   # 거래불능은 맞다
    assert is_untradeable_now(real)["blocked"] is True
    assert is_untradeable_now(real)["at_session_extreme"] == "UP"
    assert is_untradeable_now(real[:5])["blocked"] is False  # 정상 거래 구간

    # 날짜 혼입 방어 — 전일 고착 4봉 + 당일 정상 1봉이면 발동하면 안 된다.
    # (fetch_recent_raw_candles 가 날짜를 넘나들어 실제로 발생 가능한 입력)
    mixed = ([{"ts": "2026-01-01 14:2%d:00" % i, "high": 110.0, "low": 110.0, "volume": 3}
              for i in range(4)]
             + [{"ts": "2026-01-02 09:05:00", "high": 111.0, "low": 108.0, "volume": 500}])
    assert is_untradeable_now(mixed)["blocked"] is False, "전일 분봉이 당일 판정에 혼입"

    # is_at_daily_limit — 07-31 14:17 실제 케이스 재현 (상한 1036.28, 진입가 1036.28)
    L = {"upper": 1036.28, "lower": 863.56}
    assert is_at_daily_limit(1036.28, L, "LONG")["blocked"] is True
    assert is_at_daily_limit(1036.28, L, "SHORT")["blocked"] is False  # 되돌림은 무관
    assert is_at_daily_limit(1034.45, L, "LONG")["blocked"] is False   # 14:07 진입은 정상
    assert is_at_daily_limit(1036.26, L, "LONG", tick=0.02)["blocked"] is True  # 1틱 이내
    assert is_at_daily_limit(1036.26, L, "LONG", tick=0.0)["blocked"] is False
    assert is_at_daily_limit(863.56, L, "SHORT")["blocked"] is True
    # 정보 없음(인덱스 미실측) → 절대 차단하지 않는다
    assert is_at_daily_limit(1036.28, {"upper": 0.0, "lower": 0.0}, "LONG")["blocked"] is False
    assert is_at_daily_limit(1036.28, None, "LONG")["blocked"] is False

    # ── 단계 확대 유도 (규정 §1·§2) — 2026-07-31 A0568000 실측 재현 ──────────
    B = 863.58                       # 기준가(전일 정산가) = FutureMst [13]
    e = effective_price_limits(B, B * 1.08)      # 시가 = 1단계 상한에 붙은 상태
    assert e["upper_stage"] == 1 and abs(e["upper"] - B * 1.08) < 1e-9, e
    e = effective_price_limits(B, B * 1.10)      # 1단계 돌파 → 2단계가 유효
    assert e["upper_stage"] == 2, e
    e = effective_price_limits(B, B * 1.20)      # 최종단계 도달
    assert e["upper_stage"] == 3 and abs(e["upper"] - B * 1.20) < 1e-9, e
    # 하한은 상승과 무관하게 1단계 유지 — 규정 "같은 방향으로만 확대"
    assert effective_price_limits(B, B * 1.20)["lower_stage"] == 1

    # 래칫 — 한 번 3단계로 열리면 가격이 되돌려도 축소되지 않는다.
    # 07-31 09:11 고가 997.26(2단계 상한 993.12 초과)으로 3단계 개방 후,
    # 09:17 종가가 993.10으로 밀렸을 때 2단계로 역행하면 안 된다.
    e = effective_price_limits(B, 993.10, session_high=997.26)
    assert e["upper_stage"] == 3, ("래칫 실패 — 단계 역행", e)
    assert is_at_daily_limit(993.10, {"base": B, "session_high": 997.26},
                             "LONG", tick=0.02)["blocked"] is False, "역행으로 인한 과잉차단"

    BL = {"base": B}
    # 09:00~09:04 실측 재현: 932.66(=+8%)에 고착 → LONG 상방 없음
    assert is_at_daily_limit(B * 1.08, BL, "LONG")["blocked"] is True
    # 09:05 돌파 후에는 2단계까지 여지가 생겨 차단 해제
    assert is_at_daily_limit(B * 1.10, BL, "LONG")["blocked"] is False
    # 종가 1036.28(=+20%, 최종단계) → 다시 차단
    assert is_at_daily_limit(B * 1.20, BL, "LONG")["blocked"] is True
    # 같은 시점에 SHORT는 하한(-8%)과 한참 떨어져 있어 통과
    assert is_at_daily_limit(B * 1.20, BL, "SHORT")["blocked"] is False
    # base가 있으면 낡은 스냅샷 upper(1단계)보다 우선한다 — 이 케이스가 핵심
    stale = {"base": B, "upper": B * 1.08, "lower": B * 0.92}
    assert is_at_daily_limit(B * 1.15, stale, "LONG")["blocked"] is True   # 2단계 상한
    assert is_at_daily_limit(B * 1.12, stale, "LONG")["blocked"] is False  # 2단계 여지 있음
    assert "기준가 유도" in is_at_daily_limit(B * 1.12, stale, "LONG")["source"]

    # 초과 방어 — 제한선을 넘어선 값이면 신뢰 불가로 보고 차단하지 않는다.
    # 07-28(-11.64%) 재현: 기준가 1070.62 기준 하한이 -8%(984.97)로 고정돼 있었다면
    # 종가 946.02 는 그 아래다. 이때 SHORT 를 막으면 폭락일 내내 오차단이 된다.
    L28 = {"upper": 1070.62 * 1.20, "lower": 1070.62 * 0.92}
    assert is_at_daily_limit(946.02, L28, "SHORT")["blocked"] is False, "폭락일 SHORT 오차단"
    assert is_at_daily_limit(1200.00, L, "LONG")["blocked"] is False, "상한 초과 시 차단 금지"
    print("utils/market_state.py 자체 테스트 통과")
