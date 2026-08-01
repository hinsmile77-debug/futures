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
        limits:    {"upper": float, "lower": float} — 0.0/None이면 정보 없음 → 차단 안 함
        direction: "LONG" | "SHORT" (대소문자 무관)
        tick:      호가 단위. >0이면 "상한가 1틱 이내"까지 포함해 판정한다
                   (정확히 상한가에 붙기 직전도 상방 여지가 1틱뿐이라 의미가 없다)

    Returns:
        {"blocked": bool, "reason": str, "limit": float|None}
    """
    out = {"blocked": False, "reason": "", "limit": None}
    try:
        px = float(price or 0.0)
    except (TypeError, ValueError):
        return out
    if px <= 0 or not limits:
        return out
    d = str(direction or "").upper()
    eps = max(0.0, float(tick or 0.0))

    up = float(limits.get("upper") or 0.0)
    dn = float(limits.get("lower") or 0.0)
    if d == "LONG" and up > 0 and px >= up - eps:
        out.update({"blocked": True, "limit": up,
                    "reason": "상한가 %.2f 도달(현재가 %.2f) — LONG 상방 여지 없음" % (up, px)})
    elif d == "SHORT" and dn > 0 and px <= dn + eps:
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
    print("utils/market_state.py 자체 테스트 통과")
