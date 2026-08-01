# scripts/probe_cybos_limit_price.py — Dscbo1.FutureMst 상한가/하한가 필드 탐색
"""[404차 후속6] 선물 당일 상한가·하한가의 GetHeaderValue 인덱스를 실측으로 찾는다.

## 왜 프로브가 필요한가

`config/constants.py`의 `FID_UPPER_LIMIT(305)`/`FID_LOWER_LIMIT(306)`은 **키움 FID**다.
이 시스템의 라이브 백엔드는 Cybos(`BROKER_BACKEND` 기본값)이고, Cybos는 FID가 아니라
`GetHeaderValue(index)`를 쓴다 — 두 상수는 `collection/kiwoom/*`(휴면 경로)에서만
의미가 있으므로 그대로 배선하면 죽은 코드가 된다.

Cybos 등가 경로는 이미 쓰고 있는 `Dscbo1.FutureMst`(=`request_futures_snapshot`)다.
BlockRequest(TR)라 절대원칙 §4(COM 콜백 내 dynamicCall/emit 금지) 제약 밖이라 안전하다.
다만 상한가/하한가의 인덱스가 알려져 있지 않다. 기존 인덱스(71=현재가, 80=미결제약정,
115=market_state …)도 2026-05-10에 **라이브 스냅샷 실측으로 교정**된 값이다
(`dev_memory/DECISION_LOG.md` B51 — 잘못된 인덱스로 엉뚱한 값을 읽던 버그).
추측 배선은 진입 게이트를 엉뚱한 값으로 차단시키므로 금지한다.

## 사용법 (py37_32 + Cybos Plus 로그인 + 관리자 권한 필요)

    python scripts/probe_cybos_limit_price.py            # 근월물 자동 탐색
    python scripts/probe_cybos_limit_price.py A01WC000   # 코드 직접 지정

## 판별 근거

상한가/하한가는 다음 성질을 만족한다:
  - 가격 스케일 (현재가의 0.5~2배 범위)
  - upper > 현재가 > lower  이고 upper ≠ lower
  - 기준가 대비 대칭에 가깝다 (KRX 파생 가격제한폭 ±8/15/20% 단계)
후보를 전부 나열하고 위 성질로 순위를 매겨 출력한다 — **자동 확정하지 않는다.**
사람이 눈으로 확인한 뒤 `config/settings.py`의 인덱스 상수에 적어 넣는 것이 마지막 단계다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAX_IDX = 140          # FutureMst 헤더 인덱스 탐색 상한 (기존 최대 사용값 115보다 넉넉히)
_KNOWN = {
    0: "종목코드", 37: "ask1", 42: "ask_qty1", 54: "bid1", 59: "bid_qty1",
    71: "현재가", 72: "시가", 73: "고가", 74: "저가", 75: "누적거래량",
    80: "미결제약정", 82: "체결시각", 83: "처리시각", 115: "market_state",
}


def main():
    from collection.cybos.api_connector import (
        CybosAPI, _run_block_request, _normalize_code,
    )
    import win32com.client as win32

    cyb = win32.Dispatch("CpUtil.CpCybos")
    if not cyb.IsConnect:
        print("[중단] Cybos Plus 미연결(IsConnect=0). 로그인 + 관리자 권한으로 실행할 것.")
        return 1

    code = sys.argv[1] if len(sys.argv) > 1 else None
    if not code:
        api = CybosAPI()
        code = api.get_nearest_futures_code()
        print("근월물 자동 탐색: %s" % code)
    code = _normalize_code(code)

    def _dump(obj):
        out = {}
        for i in range(MAX_IDX + 1):
            try:
                out[i] = obj.GetHeaderValue(i)
            except Exception:
                pass          # 미정의 인덱스 — 조용히 건너뛴다
        return out

    ret, status, msg, data = _run_block_request(
        progid="Dscbo1.FutureMst", input_pairs=[(0, code)], data_reader=_dump)
    if ret not in (0, None) or status != 0 or not data:
        print("[중단] BlockRequest 실패 ret=%s status=%s msg=%s" % (ret, status, msg))
        return 1

    cur = _to_f(data.get(71))
    high, low = _to_f(data.get(73)), _to_f(data.get(74))
    print("\n종목=%s 현재가=%s 고가=%s 저가=%s" % (data.get(0), cur, high, low))
    if not cur:
        print("[중단] 현재가(71)를 못 읽었다 — 인덱스 매핑 자체가 어긋났을 수 있다.")
        return 1

    print("\n=== 전체 헤더 덤프 (값이 있는 인덱스만) ===")
    for i in sorted(data):
        v = data[i]
        if v in (None, "", 0):
            continue
        tag = ("  ← %s" % _KNOWN[i]) if i in _KNOWN else ""
        print("  [%3d] %-24r%s" % (i, v, tag))

    # 상한/하한 후보 추출
    prices = {i: _to_f(v) for i, v in data.items()
              if i not in _KNOWN and _is_price_like(_to_f(v), cur)}
    ups = sorted(((i, v) for i, v in prices.items() if v > cur), key=lambda t: t[1])
    dns = sorted(((i, v) for i, v in prices.items() if v < cur), key=lambda t: -t[1])

    print("\n=== 상한가 후보 (현재가 초과, 가격 스케일) ===")
    for i, v in ups:
        print("  [%3d] %10.2f   현재가 대비 %+.2f%%" % (i, v, 100 * (v / cur - 1)))
    print("\n=== 하한가 후보 (현재가 미만, 가격 스케일) ===")
    for i, v in dns:
        print("  [%3d] %10.2f   현재가 대비 %+.2f%%" % (i, v, 100 * (v / cur - 1)))

    print("\n=== 대칭성 점검 (상한·하한은 기준가 중심 대칭에 가깝다) ===")
    best = None
    for iu, vu in ups:
        for idn, vd in dns:
            base = (vu + vd) / 2.0
            if base <= 0:
                continue
            width = (vu - base) / base
            skew = abs((vu - base) - (base - vd)) / base
            if 0.03 <= width <= 0.35 and skew < 0.02:
                print("  상한[%d]=%.2f  하한[%d]=%.2f  →  기준가≈%.2f  제한폭 ±%.1f%%"
                      % (iu, vu, idn, vd, base, 100 * width))
                if best is None:
                    best = (iu, idn)

    print("\n" + "=" * 66)
    if best:
        print("가장 유력: CYBOS_FUTUREMST_UPPER_LIMIT_IDX = %d" % best[0])
        print("           CYBOS_FUTUREMST_LOWER_LIMIT_IDX = %d" % best[1])
        print("\n위 두 값을 눈으로 확인한 뒤 config/settings.py 에 적어 넣을 것.")
        print("(자동 확정하지 않는다 — 2026-05-10 B51 잘못된 인덱스 사고 재발 방지)")
    else:
        print("대칭 후보 없음. 위 덤프를 직접 확인할 것 — FutureMst가 상한/하한을")
        print("제공하지 않을 수도 있다. 그 경우 Dscbo1.FutureCurOnly 나 별도 TR을 조사한다.")
    return 0


def _to_f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _is_price_like(v, cur):
    return bool(v) and 0.5 * cur <= v <= 2.0 * cur and v != cur


if __name__ == "__main__":
    sys.exit(main())
