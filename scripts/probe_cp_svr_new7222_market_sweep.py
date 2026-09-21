# -*- coding: utf-8 -*-
"""CpSvrNew7222(시간대별 투자자매매추이) 시장코드 스윕 — 위클리 상품군 코드 탐색.

대상은 위클리 4종 전부다: (월)콜·(월)풋·(목)콜·(목)풋.
앵커 7세트가 각 시장코드마다 **전부** 대조되므로 한 번의 스윕으로
(1) 명세 매핑 검증(E·F·B) 과 (2) 위클리 4종 코드 탐색이 동시에 끝난다.
어느 세트도 맞지 않으면 **명세 A~Z 라벨에 없는데 응답이 오는 코드**
(아래 요약의 "미지 코드")로 후보를 좁힌 뒤, 키움 화면에서 그 상품을 띄워
같은 시각 값과 대조해 확정한다.

배경(2026-09-21 조사):
    (월)K200위클리 옵션의 분단위 투자자별 누적 순매수를 미륵이가 수집하고 있지 않다는
    것이 확인됐다. 현행 `CpSvrNew7221`(ri=4 "옵션풋")은 **대상(풋 전체) · 단위(금액) ·
    주체(외국인만)** 가 모두 다르다 — 정답지 79분과 값 일치 0건, 개인 부호 일치 9/79.

🔴 정답지는 **키움 화면 캡처**다(2026-09-21 오전, 사용자 제공).
   수집은 Cybos 로 하고, 수집값을 그 캡처로 **검증**한다. 키움 TR 을 쓰는 게 아니다.

   ⚠ 그래서 "앵커가 안 맞는다"가 두 가지로 갈릴 수 있다 — 시장코드가 틀렸거나,
     두 증권사 값이 애초에 다르거나. **후자는 배제됐다**:
     같은 날 Cybos `7221 ri=0`(거래소주식) 과 키움 KOSPI 현물 화면을 대조한 결과
     09:02 · 10:00 두 시점 × 개인/외국인/기관 = **6/6 정확 일치**
     (단위만 백만원 vs 억원, 정확히 100배). 양사가 KRX 원천을 그대로 중계한다.
     ⇒ 앵커 불일치는 **시장코드가 틀린 것**으로 해석해도 된다.

    `CpSvrNew7222`(시간대별 투자자매매추이, 대신 공식 명세)의 입력이 정답지의 축과
    그대로 대응한다 — 상품 · 투자자 · 누적/증감 · 계약/금액:
        type 0 (char)  시장구분   'D'선물 'E'콜옵션 'F'풋옵션 ...
        type 1 (short) 투자자구분  1=개인 2=외국인 3=기관계 4=금융투자
        type 2 (char)  '1'누적 / '2'증감          <- 화면 = 누적
        type 4 (char)  '1'계약 / '2'금액 (옵션만)  <- 화면 = 수량(계약)
    출력 (시장 지정 시): 0시간 1매도수량 2매도금액 3매수수량 4매수금액
                        5순매수수량 6순매수금액

문제: 공식 문서는 2014-07-18 스냅샷이라 **위클리 옵션 코드가 없다**
    (K200 위클리옵션은 목요일물 2019년 · 월요일물 2023년 상장).
    명세의 A~Z 중 **H · I · L · M 이 미할당**이고, KRX 의 K200 위클리 상품이
    (월)(목) x 콜/풋 = 4종이라 수가 맞는다 — 가설일 뿐이므로 실측으로 판정한다.
    (상품 구성은 KRX 것이라 증권사와 무관하다. 다만 Cybos 가 그 4종에 어떤 코드를
     배정했는지, 코드를 배정하기는 했는지는 이 스윕 전에는 알 수 없다.)

판정 방법: 2026-09-21 오전 키움 화면 캡처가 **정답지**다. 7222는 시간별 행을 통째로
    주므로, 어떤 시장코드의 응답이 아래 앵커와 일치하면 그 코드가 위클리 풋이다.

사용:
    conda run -n py37_32 python scripts/probe_cp_svr_new7222_market_sweep.py
    conda run -n py37_32 python scripts/probe_cp_svr_new7222_market_sweep.py --codes DEF --investor 2
    (32-bit 필수 · 장 마감 후 전용)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dll_bootstrap import ensure_conda_dll_path   # noqa: E402  (numpy 보다 먼저)

ensure_conda_dll_path()

import argparse      # noqa: E402
import json          # noqa: E402
import platform      # noqa: E402
import struct        # noqa: E402
import time          # noqa: E402
from typing import Any, Dict, List   # noqa: E402

from utils.analysis_db import guard_intraday   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ensure_cybos_login import ensure_cybos_login   # noqa: E402

# 2026-09-21 키움 화면 캡처 정답지 — 개인 · 누적 · 수량(계약)
# 콜·풋 두 세트다. 각 시장코드마다 **두 세트를 모두** 대조하므로 한 번의 스윕으로
# (월)콜·(월)풋 두 코드가 동시에 확정된다.
# 식별력 메모: 풋은 오전 내내 단조증가(+2,917→+5,539)인데 콜은 10:00 +4,215 에서
# 10:22 +3,386 으로 **꺾인다**. 패턴이 달라 서로 오탐될 여지가 작다.
# ⚠ 세트마다 **채점 필드가 다르다**. 옵션 화면은 수량(계약)=필드5, KOSPI 현물 화면은
#   금액(억)=필드6 으로 잡았다. 값 형식이 (채점필드, {HHMM: 값}) 인 이유다.
ANCHOR_DATE = "2026-09-21"
ANCHOR_SETS = {
    "(월)위클리 풋": ("net_qty", {905: 2917, 930: 3929, 950: 4503, 1000: 4800, 1022: 5539}),
    "(월)위클리 콜": ("net_qty", {905: 1751, 930: 2945, 950: 3964, 1000: 4215, 1022: 3386}),
    # 정규 월물 = 명세상 시장코드 'E'(콜) · 'F'(풋).
    # **위클리를 찾기 전에 이 둘부터 맞아야 한다** — 맞으면 명세의 시장코드 매핑이
    # 살아 있다는 뜻이고, 그때 위클리는 "미지 코드" 목록에 있다고 좁힐 수 있다.
    # 어긋나면 매핑 자체를 의심해야 하므로 위클리 탐색은 그다음이다.
    # ⚠ 값이 작아(±300) 우연 일치 여지가 위클리보다 크다. 5개 전부 맞을 때만 인정할 것.
    "먼스리 풋(F검증)": ("net_qty", {905: -212, 930: -2, 950: 64, 1000: 60, 1022: -86}),
    "먼스리 콜(E검증)": ("net_qty", {905: 112, 930: 138, 950: 242, 1000: 224, 1022: -12}),
    # ⚠ 목위클리는 값 범위가 좁고(-31~-82) 변화가 완만해 **우연 일치 위험이 가장 크다.**
    #   5개 전부 맞아도 다른 세트보다 신뢰를 낮게 잡고, 확정 전에 화면과 한 번 더 대조할 것.
    #   실측상 이 상품은 기관계가 하루 종일 0 이고 개인 ≈ −외국인 이라 정보량도 최소다(0.8%).
    "(목)위클리 콜": ("net_qty", {905: -31, 930: -71, 950: -82, 1000: -50, 1022: -74}),
    # (목)풋은 (목)콜보다 낫다 — 값 범위가 −51~−268 로 넓고 단조감소라 변별력이 있다.
    "(목)위클리 풋": ("net_qty", {905: -51, 930: -152, 950: -208, 1000: -232, 1022: -268}),
    # KOSPI 현물 = 명세상 시장코드 'B'(거래소). **성격이 다른 검증이다** —
    #   ① 단위가 금액(억)이라 채점 필드가 net_amt(필드6)다
    #   ② 화면 행 간격이 **2분**이다(옵션은 1분). 그래서 앵커 시각도 짝수 분만 쓴다.
    #      스윕 응답이 1분 간격으로 오면 앵커는 맞아도 간격은 화면과 다른 것이니,
    #      배선 전에 행 간격을 따로 확인할 것.
    "KOSPI 현물(B검증)": ("net_amt", {906: -1351, 930: -4549, 950: -5131,
                                      1000: -5470, 1022: -9420}),
}

# 옵션 종목코드 체계 — 2026-09-21 실물 6종 대조로 해독.
#   B 01 66 A01   정규 월물   콜  2606   행사가 1000.0
#   C 01 6A A45   정규 월물   풋  2610   행사가 1110.0  최종거래일 2026/10/08
#   B 09 FE A45   위클리(목)  콜  09W4   행사가 1110.0  최종거래일 2026/09/23
#   C 09 FE A45   위클리(목)  풋  09W4   행사가 1110.0  최종거래일 2026/09/23
#   B AF BY A45   위클리(월)  콜  09W3   행사가 1110.0  최종거래일 2026/09/21
#   B AF BZ A45   위클리(월)  콜  09W4   행사가 1110.0  최종거래일 2026/09/28
#
#   [1]    B=콜 / C=풋
#          ← 목위클리 콜·풋 쌍(B09FEA45 / C09FEA45)이 **같은 만기·같은 행사가**에서
#            첫 글자만 갈리는 것으로 확정. 정규 월물뿐 아니라 위클리에서도 성립한다.
#   [2-3]  상품군: '01'=정규 월물 / '09'=위클리(목) / 'AF'=위클리(월)
#          ← KRX 파생 단축코드의 앞자리를 치환한 것으로 보인다
#            (201/301=정규, 209/309=목위클리, 2AF/3AF=월위클리 → 2=B, 3=C).
#   [4-5]  만기 식별자. 정규는 연+월('6'+'A'=2026년 10월, A=10).
#          위클리는 주차별로 갈린다(월: 09W3='BY' 09W4='BZ' / 목: 09W4='FE').
#          ⚠ 같은 "09W4"라도 월/목이 다르다 — 상품군마다 별도 체계다.
#            두 점(월)·한 점(목)만 관측했으므로 연말 넘김 규칙은 미확인.
#   [6-8]  행사가: **상품군·만기와 무관하게 공통**. 1110.0 이 위 5종 모두 'A45'
#
# ⇒ 위클리(월) 풋 = 'CAF…'. B/C 대칭이 위클리에서 실물로 확인됐으므로 이제
#   가설이 아니라 대칭의 귀결이다. 그래도 실물 조회는 아래 --enum-codes 가 한다.
# ⚠ 판정은 접두 단위로 할 것. 개별 종목 존재로 판정하면 만기 소멸과 혼동된다
#   (계측 4원칙 ②: 없는 것과 사라진 것은 다르다).
MONTHLY_PREFIXES = {
    "B01": "정규 월물 콜",
    "C01": "정규 월물 풋",
}
WEEKLY_PREFIXES = {
    "BAF": "위클리(월) 콜",
    "CAF": "위클리(월) 풋",
    "B09": "위클리(목) 콜",
    "C09": "위클리(목) 풋",
}
# 열거에서 실재를 확인할 종목 — 실물 4 + 조립검증 1.
# 전부 **차주 이후 만기**다. 09W3(BAFBYA45)은 2026-09-21 만기라 장 마감 후
# 마스터에서 빠질 수 있고, 그걸 "위클리 미지원"으로 오독하기 쉬워 제외했다.
PROBE_CODES = [
    ("BAFBZA45", "위클리(월) 콜 09W4 K=1110.0", "실물"),
    ("CAFBZA45", "위클리(월) 풋 09W4 K=1110.0", "조립검증"),
    ("B09FEA45", "위클리(목) 콜 09W4 K=1110.0", "실물"),
    ("C09FEA45", "위클리(목) 풋 09W4 K=1110.0", "실물"),
]

# 🔴 2026-09-21 라이브 실측으로 확정된 시장코드 (키움 캡처 정답지 대조, 5/5 또는 4/5).
#   4/5 는 그 시각 행이 Cybos 응답에 없어서지 값이 틀린 게 아니다 — 확인된 행은 전부 일치.
#
#   '&' ord=38  (월)위클리 풋   5/5      '?' ord=63  (월)위클리 콜   5/5
#   'R' ord=82  (목)위클리 풋   5/5      'Q' ord=81  (목)위클리 콜   4/5
#   'F' ord=70  먼스리 풋       5/5      'E' ord=69  먼스리 콜       5/5
#   'B' ord=66  KOSPI 현물     4/5 (금액=필드6, 백만원 → 억 환산 후 일치)
#
# ⚠ **(월)위클리는 명세 A~Z 밖의 특수문자다.** 2014 스냅샷 명세로는 찾을 수 없었고,
#   A~Z · a~z · 0~9 를 전부 훑어도 안 나왔다. 확장 문자 스캔(ord 33~255)에서 나왔다.
#   → 앞으로 새 상품군을 찾을 때도 **A~Z 로 범위를 한정하지 말 것.**
CONFIRMED_MARKET_CODES = {
    "&": "(월)위클리 풋", "?": "(월)위클리 콜",
    "R": "(목)위클리 풋", "Q": "(목)위클리 콜",
    "F": "먼스리 풋", "E": "먼스리 콜", "B": "KOSPI 현물",
}
MARKET_LABELS = {
    "A": "전체", "B": "거래소=KOSPI현물✔", "C": "코스닥", "D": "선물",
    "E": "콜옵션=먼스리콜✔", "F": "풋옵션=먼스리풋✔",
    "G": "스타지수선물", "J": "주식콜옵션", "K": "주식풋옵션",
    "Q": "(목)위클리 콜✔", "R": "(목)위클리 풋✔",
    "&": "(월)위클리 풋✔", "?": "(월)위클리 콜✔",
    "Z": "CME선물",
}
INVESTOR_LABELS = {0: "전체", 1: "개인", 2: "외국인", 3: "기관계", 4: "금융투자"}


def _ensure_runtime() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("Windows only")
    if struct.calcsize("P") != 4:
        raise RuntimeError("CpSvrNew7222 COM requires 32-bit Python (conda env: py37_32)")


def _safe_int(v: Any) -> int:
    try:
        return int(str(v).strip().replace(",", ""))
    except Exception:
        return 0


# 한 번의 조회는 **18행**만 준다(실측). 옵션은 1분 간격이라 18분치뿐이고,
# 현물은 1~2분 불규칙이라 26분쯤 된다. 그래서 과거 앵커를 보려면 type 3(조회 시각,
# HHMM)으로 페이징해야 한다 — type 3 은 **그 시각 직전** 18행을 준다.
# 아래 값들은 앵커 5개(0905·0930·0950·1000·1022)를 모두 덮도록 고른 것이다.
ANCHOR_PAGES = (1023, 1001, 951, 931, 907)


def probe_market(code: str, investor: int, cumulative: str, unit: str,
                 max_rows: int = 400, pages=(None,)) -> Dict[str, Any]:
    """시장코드 하나를 조회해 시간별 행을 반환한다.

    pages: type 3 에 넣을 시각 목록. (None,) 이면 최근 18행만.
    """
    from win32com.client import Dispatch

    out: Dict[str, Any] = {"code": code, "label": MARKET_LABELS.get(code, "?")}
    merged: Dict[int, Dict[str, Any]] = {}
    last_err = None
    for pg in pages:
        try:
            one = _probe_one(code, investor, cumulative, unit, pg, max_rows)
        except Exception as exc:                  # noqa: BLE001
            last_err = exc
            continue
        if one.get("error"):
            last_err = one["error"]
            continue
        for r in one.get("rows", []):
            merged[r["t"]] = r
        out.setdefault("status", one.get("status"))
    if merged:
        out["rows"] = [merged[k] for k in sorted(merged, reverse=True)]
        out["row_count"] = len(merged)
        out["ok"] = True
    else:
        out["ok"] = False
        if last_err is not None:
            out["error"] = "%s" % (last_err,)
    return out


def _probe_one(code: str, investor: int, cumulative: str, unit: str,
               t3, max_rows: int) -> Dict[str, Any]:
    from win32com.client import Dispatch

    out: Dict[str, Any] = {}
    try:
        obj = Dispatch("CpSysDib.CpSvrNew7222")
        obj.SetInputValue(0, ord(code))
        obj.SetInputValue(1, investor)
        obj.SetInputValue(2, ord(cumulative))
        obj.SetInputValue(4, ord(unit))
        if t3 is not None:
            obj.SetInputValue(3, t3)
        ret = obj.BlockRequest()
        status = _safe_int(obj.GetDibStatus())
        msg = str(obj.GetDibMsg1() or "").strip()
        out.update({"ret": ret, "status": status, "msg": msg})
        if ret not in (0, None) or status != 0:
            out["ok"] = False
            return out

        cnt = _safe_int(obj.GetHeaderValue(0))
        out["row_count"] = cnt
        rows: List[Dict[str, Any]] = []
        for i in range(min(cnt, max_rows)):
            try:
                rows.append({
                    "t":        _safe_int(obj.GetDataValue(0, i)),
                    "sell_qty": _safe_int(obj.GetDataValue(1, i)),
                    "buy_qty":  _safe_int(obj.GetDataValue(3, i)),
                    "net_qty":  _safe_int(obj.GetDataValue(5, i)),
                    "net_amt":  _safe_int(obj.GetDataValue(6, i)),
                })
            except Exception:
                break
        out["rows"] = rows
        out["ok"] = bool(rows)
    except Exception as exc:                      # noqa: BLE001
        out["ok"] = False
        out["error"] = "%s" % (exc,)
    return out


def score_against_anchors(rows, anchors, field="net_qty"):
    """정답지 앵커와 대조. 시간 필드는 HHMM 또는 HHMMSS 양쪽을 허용한다.

    field: 채점에 쓸 열 — 옵션 화면은 수량 'net_qty', KOSPI 현물 화면은 금액 'net_amt'.
    """
    by_t: Dict[int, int] = {}
    for r in rows:
        t = r["t"]
        if t > 10000:          # HHMMSS -> HHMM
            t //= 100
        v = r[field]
        if field == "net_amt":
            v = int(round(v / 100.0))   # 백만원 -> 억원 (화면 단위)
        by_t[t] = v
    # 🔴 "행없음"과 "값 불일치"를 같은 칸에 세지 않는다 (계측 4원칙 ②: 미측정 ≠ 0).
    #   Cybos 응답의 행 간격은 불규칙해서(옵션 1분 / 현물 1~2분) 앵커 시각 자체가
    #   없는 경우가 정상적으로 생긴다 — 그걸 불일치로 세면 맞는 코드가 탈락한다.
    #   실제로 2026-09-21 'Q'(목위클리 콜)·'B'(KOSPI 현물)이 이 때문에 오탈락했다.
    hit, mismatch, absent, detail = 0, 0, 0, []
    for t, expect in sorted(anchors.items()):
        got = by_t.get(t)
        if got is None:
            detail.append("%04d: 행없음 — 미측정 (기대 %+d)" % (t, expect))
            absent += 1
        elif got == expect:
            detail.append("%04d: %+d  [일치]" % (t, got))
            hit += 1
        else:
            detail.append("%04d: %+d (기대 %+d, 차 %+d)" % (t, got, expect, got - expect))
            mismatch += 1
    # 확정 조건: 값이 어긋난 행이 하나도 없고, 확인된 행이 3개 이상.
    confirmed = (mismatch == 0 and hit >= 3)
    return {"hit": hit, "miss": mismatch, "absent": absent,
            "confirmed": confirmed, "detail": detail}


def enumerate_option_codes(probe_codes=()) -> Dict[str, Any]:
    """CpUtil.CpOptionCode 열거 — 위클리 옵션이 포함되는지 판정한다.

    2026-09-21 실측 배경: 캐시 `data/option_chain.json`(2026-06-04자, 5,242종목)은
    접두가 **B01(콜) · C01(풋) 두 개뿐**이고 위클리는 0건이었다. 사용자 화면에서
    확인된 위클리(월) 콜 `BAFBYA45`의 접두 `BAF`가 없다.
    캐시가 낡은 탓인지, CpOptionCode 가 원래 월물만 주는지는 이 열거로 판정한다.
    후자라면 종목 단위 폴백 경로(CpSvr7254)도 종목 목록을 따로 구해야 한다.
    """
    from win32com.client import Dispatch

    out: Dict[str, Any] = {}
    try:
        obj = Dispatch("CpUtil.CpOptionCode")
        cnt = _safe_int(obj.GetCount())
        prefixes: Dict[str, int] = {}
        wanted = set(c for c in probe_codes if c)
        found: Dict[str, str] = {}
        samples: Dict[str, str] = {}
        for i in range(cnt):
            try:
                code = str(obj.GetData(0, i) or "").strip()
            except Exception:
                continue
            if not code:
                continue
            p = code[:3]
            prefixes[p] = prefixes.get(p, 0) + 1
            if p not in samples:
                try:
                    samples[p] = "%s / %s" % (code, obj.GetData(1, i))
                except Exception:
                    samples[p] = code
            if code in wanted:
                try:
                    found[code] = str(obj.GetData(1, i) or "").strip()
                except Exception:
                    found[code] = "(이름 조회 실패)"
        out.update({"count": cnt, "prefixes": prefixes,
                    "samples": samples, "probe_found": found})
    except Exception as exc:                      # noqa: BLE001
        out["error"] = "%s" % (exc,)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="CpSvrNew7222 시장코드 스윕")
    ap.add_argument("--enum-codes", action="store_true",
                    help="CpOptionCode 열거로 위클리 종목 포함 여부까지 함께 확인")
    ap.add_argument("--extra-code", action="append", default=[],
                    help="열거에서 존재를 확인할 종목코드 추가 (반복 지정 가능). "
                         "기본 4종(PROBE_CODES)은 항상 확인한다")
    ap.add_argument("--codes",
                    default="&?QRFEB",
                    help="스윕할 시장코드 문자열 (기본: 2026-09-21 확정 7종 &?QRFEB). "
                         "새 상품군을 찾을 때만 A~Z 등으로 넓힐 것")
    ap.add_argument("--investor", type=int, default=1, help="투자자 구분 (기본 1=개인)")
    ap.add_argument("--cumulative", default="1", choices=["1", "2"], help="1=누적(기본) 2=증감")
    ap.add_argument("--unit", default="1", choices=["1", "2"], help="1=계약(기본) 2=금액")
    ap.add_argument("--sleep", type=float, default=0.4, help="요청 간 대기(초)")
    ap.add_argument("--json-out", default="", help="결과 JSON 저장 경로")
    ap.add_argument("--no-anchor", action="store_true", help="정답지 대조 생략")
    args = ap.parse_args()

    # COM 프로브는 라이브 세션과 Cybos 요청 한도를 공유한다 — 장중 실행 금지.
    guard_intraday("probe_cp_svr_new7222_market_sweep")
    _ensure_runtime()
    # 라이브 세션이 이미 붙어 있으면 로그인 절차를 타지 않는다.
    # `ensure_cybos_login()` 은 pywinauto 자동로그인 경로를 거치는데, 그 패키지가
    # 없는 환경에서는 실패한다 — 그런데 이 스크립트는 **이미 떠 있는 Cybos 세션에
    # 얹혀 조회만** 하므로 로그인 자체가 필요 없다.
    # COM 아파트먼트를 먼저 연다 — 이걸 빠뜨리면 Dispatch 가
    # -2147221008 "CoInitialize가 호출되지 않았습니다" 로 실패한다
    # (미륵이 PROBE 로그 08:58:13 에 같은 실패가 기록돼 있다).
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except Exception as exc:                      # noqa: BLE001
        print("[WARN] CoInitialize 실패: %s" % (exc,))

    connected = False
    try:
        from win32com.client import Dispatch
        connected = int(Dispatch("CpUtil.CpCybos").IsConnect) == 1
        print("[INFO] Cybos 기존 세션 연결 상태 = %s" % connected)
    except Exception as exc:                      # noqa: BLE001
        # 폴백을 조용히 삼키지 않는다 (계측 4원칙 ④)
        print("[WARN] IsConnect 조회 실패 → 로그인 절차로 폴백: %s" % (exc,))
    if not connected and not ensure_cybos_login():
        print("[FAIL] Cybos 연결 실패")
        return 1

    if args.enum_codes:
        print("=" * 78)
        print("[사전] CpUtil.CpOptionCode 열거 — 위클리 종목 포함 여부")
        print("=" * 78)
        want = [c for c, _, _ in PROBE_CODES] + list(args.extra_code)
        en = enumerate_option_codes(want)
        if en.get("error"):
            print("  열거 실패: %s" % en["error"])
        else:
            pf = en["prefixes"]
            print("  총 %d 종목 · 접두 %d종" % (en["count"], len(pf)))
            for p, c in sorted(pf.items(), key=lambda kv: -kv[1]):
                known = MONTHLY_PREFIXES.get(p) or WEEKLY_PREFIXES.get(p) or ""
                print("    %-5s %5d종목  %-14s 예: %s"
                      % (p, c, known, en["samples"].get(p, "")))

            # 판정은 **접두 단위**로 한다 — 개별 종목은 만기로 사라지지만
            # 접두는 차주물이 남아 있는 한 잡힌다.
            print("  위클리 접두 4종:")
            missing = []
            for p, label in WEEKLY_PREFIXES.items():
                n = pf.get(p, 0)
                print("    %-5s %-14s %5d종목%s" % (p, label, n, "" if n else "   <-- 없음"))
                if not n:
                    missing.append(p)
            if not missing:
                print("  [판정] CpOptionCode 가 위클리 4종을 모두 준다 — "
                      "종목 단위 폴백 경로가 열린다.")
            elif len(missing) == len(WEEKLY_PREFIXES):
                print("  [판정] CpOptionCode 는 월물만 준다(위클리 접두 0건). "
                      "종목 단위로 가려면 코드 생성 규칙을 따로 확보해야 한다.")
            else:
                cand = sorted(p for p in pf
                              if p not in MONTHLY_PREFIXES and p not in WEEKLY_PREFIXES)
                print("  [주의] 위클리 접두 일부만 잡힌다(누락 %s). "
                      "분류되지 않은 접두: %s" % (", ".join(missing), cand or "없음"))

            fd = en.get("probe_found") or {}
            print("  종목 실재 확인:")
            for code, label, tag in PROBE_CODES:
                print("    %-9s %-26s (%s) = %s"
                      % (code, label, tag, fd.get(code, "없음")))
            for code in args.extra_code:
                print("    %-9s %-26s (%s) = %s"
                      % (code, "", "추가", fd.get(code, "없음")))
            assembled = [c for c, _, tag in PROBE_CODES if tag == "조립검증"]
            if assembled and all(c in fd for c in assembled):
                print("  [확정] 코드 조립 규칙이 맞다 — 위클리 전 종목을 "
                      "코드 생성으로 만들 수 있다(CpSvr7254 종목 단위 경로).")
        print()

    anchor_sets = {} if args.no_anchor else ANCHOR_SETS
    print("CpSvrNew7222 스윕 — 투자자=%d(%s) 누적=%s 단위=%s"
          % (args.investor, INVESTOR_LABELS.get(args.investor, "?"),
             args.cumulative, "계약" if args.unit == "1" else "금액"))
    for nm, (fld, a) in anchor_sets.items():
        print("정답지 [%s] %s·개인·누적·%s — %s"
              % (nm, ANCHOR_DATE, "계약" if fld == "net_qty" else "금액(억)",
                 ", ".join("%04d=%+d" % kv for kv in sorted(a.items()))))
    print("-" * 78)

    results: List[Dict[str, Any]] = []
    winners: Dict[str, List[str]] = {nm: [] for nm in anchor_sets}
    for code in args.codes:
        r = probe_market(code, args.investor, args.cumulative, args.unit,
                         pages=ANCHOR_PAGES if anchor_sets else (None,))
        results.append(r)
        if not r.get("ok"):
            detail = r.get("msg") or r.get("error", "")
            print("  %s %-20s : 응답없음 (status=%s %s)"
                  % (code, r["label"], r.get("status"), detail[:40]))
        else:
            rows = r["rows"]
            last = rows[0] if rows else {}
            line = ("  %s %-20s : rows=%-4d 최신 t=%s 순매수수량=%+d"
                    % (code, r["label"], len(rows), last.get("t"),
                       last.get("net_qty", 0)))
            r["anchors"] = {}
            for nm, (fld, a) in anchor_sets.items():
                sc = score_against_anchors(rows, a, fld)
                r["anchors"][nm] = sc
                line += "  | %s %d/%d%s" % (nm[-1], sc["hit"], len(a),
                                            "" if not sc["absent"] else "(결측%d)" % sc["absent"])
                if sc["confirmed"]:
                    line += "  <<< %s 전부일치" % nm
                    winners[nm].append(code)
            print(line)
        time.sleep(args.sleep)

    print("-" * 78)
    # 2014년 명세에 라벨이 없는데 응답이 오는 코드 = 그 이후 신설 상품군.
    # 위클리 4종·주식선물 등이 여기 있다 — 앵커가 없는 3종의 후보 목록이다.
    unknown = [r for r in results
               if r.get("ok") and r["code"] not in MARKET_LABELS]
    if unknown:
        print("[미지 코드] 명세에 라벨이 없는데 응답한 시장코드 — 위클리 후보:")
        for r in unknown:
            last = r["rows"][0] if r["rows"] else {}
            print("    '%s'  rows=%-4d 최신 t=%s 순매수수량=%+d"
                  % (r["code"], len(r["rows"]), last.get("t"), last.get("net_qty", 0)))
        print("    → 화면에서 해당 상품을 띄워 같은 시각 값과 대조하면 확정된다.")
        print("-" * 78)
    for nm in anchor_sets:
        if winners[nm]:
            print("[확정] %s 시장코드 = %s"
                  % (nm, ", ".join("'%s'" % c for c in winners[nm])))
            for c in winners[nm]:
                r = next(x for x in results if x["code"] == c)
                for d in r["anchors"][nm]["detail"]:
                    print("    %s" % d)
        else:
            scored = [x for x in results if x.get("anchors", {}).get(nm)]
            best = max(scored, key=lambda x: x["anchors"][nm]["hit"]) if scored else None
            print("[미발견] %s — 값이 어긋나지 않으면서 3개 이상 일치한 코드가 없다." % nm)
            if best and best["anchors"][nm]["hit"]:
                print("   최고 근접: '%s' %s — %d개 일치"
                      % (best["code"], best["label"], best["anchors"][nm]["hit"]))
    if anchor_sets and not any(winners.values()):
        print("   다음 수순: (1) 7222 시장코드로는 위클리를 지정할 수 없고, 종목코드 기반")
        print("                 TR(CpSvr7254 등)로 위클리 전 행사가를 합산해야 할 가능성")
        print("             (2) SetInputValue(3, 시각)으로 과거 구간을 받아야 하는지 확인")
        print("             (3) CpSvr7210T(투자자별 종합 잠정 시간대별) 대체 후보 검증")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("JSON 저장: %s" % args.json_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
