# -*- coding: utf-8 -*-
"""[9842] CpSvr9842 점검 프로브 — 읽기전용 · DB 쓰기 없음 · 서버 요청 최대 8건

2026-10-22 실계좌 로그인(ServerType=2)에서 첫 성공 이후 남은 확인 사항을 한 번에 점검한다.
근거: docs/미륵이고도화3/9842_행사가별투자자_분단위수집_구현계획_MW0601-20261004.md §7

점검 항목
  [L1] 위클리 지원     — 응답 코드가 먼스리 마스터(CpOptionCode)에 없는가 · 미문서 월물값 '3'/'4' 응답
  [L2] 「추정」 대사    — (a) 12주체 합 = 0  (b) 기간 모드(종료일=직전 _P 날짜) vs HTS _P 파일 칸 대조
                          (c) 당일 Σ외인 콜·풋 vs option_flow.db 7222 mon_call/mon_put 외인 순매수
  [L3] 행사가 매핑     — 코드 → 행사가를 CpOptionCode 로 해석(문자열 파싱 금지) · 미매핑 개수 표기
  [T1] 등급/서버       — IsConnect · ServerType · 호스트명 기록 (MW0602 CREON 에서도 같은 스크립트로 실행)
  [T2] 커버리지        — 풋 · 차근월 · 선물 응답 여부

사용
  conda run -n py37_32 python scripts\\probe_cpsvr9842.py               # 전 항목(요청 8건)
  conda run -n py37_32 python scripts\\probe_cpsvr9842.py --end 20261021 # 기간 대조 날짜 지정
  conda run -n py37_32 python scripts\\probe_cpsvr9842.py --skip-weekly --skip-flow

산출
  logs/YYYYMMDD_PROBE.log           [CybosProbe][RAW] CpSvr9842 … 한 줄씩(기존 관례)
  logs/probe_9842_YYYYMMDD_HHMMSS.md   판정 요약
  logs/probe_9842_YYYYMMDD_HHMMSS.json 원시 응답(재대조용)
"""
from __future__ import print_function

import argparse
import datetime
import glob
import json
import os
import socket
import sqlite3
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

# cp949 콘솔에서 ≠ · ❌ · — 등을 print 하다 죽지 않게 한다(파일 산출물은 utf-8 그대로).
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

from html.parser import HTMLParser  # noqa: E402

HTS_DIR = os.path.join(ROOT, "data", "db", "option_hts")
FLOW_DB = os.path.join(ROOT, "data", "db", "option_flow.db")
LOG_DIR = os.path.join(ROOT, "logs")

INVESTORS = ["개인", "외국인", "기관계", "증권", "보험", "투신", "은행", "종금", "기금", "국가", "선물회사", "기타법인"]
# HTS 머리행 이름 → API 투자자 인덱스. 위치가 아니라 이름으로 찾는다(ladder_data._9842_NAME 과 같은 원칙).
HTS_NAME_TO_IDX = {"개인": 0, "외국인": 1, "기관계": 2, "금융투자": 3, "투신": 5}

MAX_REQUESTS = 8
NOW = datetime.datetime.now()
STAMP = NOW.strftime("%Y%m%d_%H%M%S")
PROBE_LOG = os.path.join(LOG_DIR, "%s_PROBE.log" % NOW.strftime("%Y%m%d"))

_report = []
_requests = [0]


def log(msg):
    line = "%s [INFO] PROBE: [CybosProbe][RAW] CpSvr9842 %s" % (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with open(PROBE_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def rep(line=""):
    _report.append(line)


# ── Cybos ────────────────────────────────────────────────────────────────

def cybos():
    import win32com.client as wc
    return wc, wc.Dispatch("CpUtil.CpCybos")


def wait_limit(cy, need=5):
    """조회 한도(type1)가 need 미만이면 재충전까지 기다린다 — 라이브와 한도를 나눠 쓴다."""
    for _ in range(30):
        remain = cy.GetLimitRemainCount(1)
        if remain >= need:
            return remain
        ms = cy.LimitRequestRemainTime
        log("limit wait remain=%s remain_ms=%s" % (remain, ms))
        time.sleep(max(ms, 500) / 1000.0 + 0.2)
    return cy.GetLimitRemainCount(1)


def _arr(v):
    try:
        return [x for x in v]
    except TypeError:
        return [v]


def request(wc, cy, label, market, month, period, end=None):
    """CpSvr9842 1회. 반환: dict(ok, msg, rows=[{code, qty, avg, amt, pnl}]) — 실패를 0행으로 위장하지 않는다."""
    if _requests[0] >= MAX_REQUESTS:
        return dict(ok=False, msg="SKIP 요청 상한 %d 도달" % MAX_REQUESTS, rows=None)
    remain = wait_limit(cy)
    obj = wc.Dispatch("CpSysDib.CpSvr9842")
    obj.SetInputValue(0, ord(market))
    obj.SetInputValue(1, ord(month))
    obj.SetInputValue(2, ord(period))
    if end is not None:
        obj.SetInputValue(3, int(end))
    _requests[0] += 1
    t0 = time.time()
    try:
        obj.BlockRequest()
    except Exception as e:  # 등급 차단은 InputCheck 예외로 온다
        log("%s EXCEPTION %r remain_before=%s" % (label, e, remain))
        return dict(ok=False, msg="EXCEPTION %r" % (e,), rows=None)
    ms = (time.time() - t0) * 1000
    st = obj.GetDibStatus()
    msg = str(obj.GetDibMsg1() or "").strip()
    log("%s input=(%s,%s,%s,%s) status=%s msg=%s elapsed_ms=%.0f remain_after=%s"
        % (label, market, month, period, end, st, msg, ms, cy.GetLimitRemainCount(1)))
    if st != 0:
        return dict(ok=False, msg="status=%s %s" % (st, msg), rows=None)
    rows = []
    pages = 0
    while True:
        pages += 1
        n = obj.GetHeaderValue(0)
        for i in range(n):
            rows.append(dict(code=str(obj.GetDataValue(0, i)).strip(),
                             qty=_arr(obj.GetDataValue(1, i)), avg=_arr(obj.GetDataValue(2, i)),
                             amt=_arr(obj.GetDataValue(3, i)), pnl=_arr(obj.GetDataValue(4, i))))
        # 명세는 「연속조회 없음」이지만 2026-10-22 차근월(12월물)이 400행 + 71102 「조회가 계속됩니다」로 왔다.
        if not obj.Continue:
            break
        if _requests[0] >= MAX_REQUESTS + 4:
            log("%s 연속조회 중단 — 요청 상한(+4) 도달, %d쪽 %d행에서 절단" % (label, pages, len(rows)))
            msg += " [절단: 연속조회 남음]"
            break
        wait_limit(cy)
        _requests[0] += 1
        obj.BlockRequest()
    log("%s rows=%d pages=%d" % (label, len(rows), pages))
    return dict(ok=True, msg=msg, rows=rows, pages=pages)


def option_master(wc):
    """CpOptionCode(먼스리 전용, 서버 요청 아님) → {code: (cp, ym, strike)}"""
    m = {}
    obj = wc.Dispatch("CpUtil.CpOptionCode")
    for i in range(obj.GetCount()):
        try:
            code = str(obj.GetData(0, i)).strip()
            m[code] = (str(obj.GetData(2, i)).strip().upper(), str(obj.GetData(3, i)).strip(),
                       float(obj.GetData(4, i)))
        except Exception:
            pass
    return m


# ── HTS 파일 ─────────────────────────────────────────────────────────────

class _TableParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.rows, self._row, self._cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._row is not None and self._cell is not None:
            self._row.append(self._cell.strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell += data


def _num(x):
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return None


def read_hts(path):
    """→ ({strike: {('C'|'P', idx): value}}, unit, head). unit: contract | amount(십만원)"""
    p = _TableParser()
    with open(path, "rb") as f:
        p.feed(f.read().decode("euc-kr", errors="replace"))
    rows = [r for r in p.rows if r]
    head = rows[0][:11]
    if len(head) < 11 or head[5] != "행사가":
        raise ValueError("머리행이 [9842] 배치가 아니다: %s" % head)
    cols = []
    for j, name in enumerate(head):
        if j == 5 or name == "현재가":
            continue
        if name not in HTS_NAME_TO_IDX:
            raise ValueError("모르는 열 이름: %s" % name)
        cols.append((j, "C" if j < 5 else "P", HTS_NAME_TO_IDX[name]))
    out, vals = {}, []
    for r in rows[1:]:
        if len(r) < 11 or _num(r[5]) is None:
            continue
        d = {}
        for j, cp, idx in cols:
            v = _num(r[j])
            if v is not None:
                d[(cp, idx)] = v
                vals.append(v)
        out[_num(r[5])] = d
    unit = "contract" if vals and all(float(v).is_integer() for v in vals) else "amount"
    return out, unit, head


def latest_p_before(today):
    best = None
    for fn in glob.glob(os.path.join(HTS_DIR, "??????_P.xls")):
        y = os.path.basename(fn)[:6]
        d = "20" + y
        if d < today and (best is None or d > best[0]):
            best = (d, fn)
    return best


# ── 점검 ─────────────────────────────────────────────────────────────────

def check_sum_zero(label, res):
    # 인덱스 2 기관계 = Σ(3..10) 소계다(2026-10-22 전 행 실측). 12칸을 다 더하면 기관이 이중계상된다.
    bad = [r["code"] for r in res["rows"]
           if sum(r["qty"]) - r["qty"][2] != 0 or r["qty"][2] != sum(r["qty"][3:11])]
    n = len(res["rows"])
    rep("- `%s` 주체 합(기관계 제외) ≠ 0 또는 기관계 ≠ Σ(증권–선물회사): **%d / %d행**%s" % (
        label, len(bad), n, (" — 예: %s" % ", ".join(bad[:5]) + (" … 외 %d개" % (len(bad) - 5) if len(bad) > 5 else "")) if bad else ""))
    return len(bad)


def map_strikes(label, res, master, cp_expect):
    out, unmapped, wrong_cp = {}, [], []
    for r in res["rows"]:
        m = master.get(r["code"])
        if m is None:
            unmapped.append(r["code"])
            continue
        if cp_expect and not m[0].startswith(cp_expect):
            wrong_cp.append(r["code"])
        out[m[2]] = r
    yms = sorted(set(master[r["code"]][1] for r in res["rows"] if r["code"] in master))
    strikes = sorted(out)
    order_ok = [master[r["code"]][2] for r in res["rows"] if r["code"] in master]
    rep("- `%s` 행사가 매핑: %d행 중 매핑 **%d** · 미매핑 **%d**%s · 월물 %s · 범위 %s–%s · 응답순서=행사가 오름차순 %s · 콜풋 불일치 %d"
        % (label, len(res["rows"]), len(out), len(unmapped),
           (" (예: %s%s)" % (", ".join(unmapped[:5]), " … 외 %d개" % (len(unmapped) - 5) if len(unmapped) > 5 else "")) if unmapped else "",
           yms, strikes[0] if strikes else "-", strikes[-1] if strikes else "-",
           "예" if order_ok == sorted(order_ok) else "**아니오**", len(wrong_cp)))
    return out, unmapped


def compare_hts(label, by_strike, hts, unit, cp):
    field = "qty" if unit == "contract" else "amt"
    n = same = 0
    diffs, only_api, only_hts = [], [], []
    for k in sorted(set(by_strike) | set(hts)):
        if k not in hts:
            only_api.append(k)
            continue
        if k not in by_strike:
            only_hts.append(k)
            continue
        for (side, idx), hv in hts[k].items():
            if side != cp:
                continue
            av = by_strike[k][field][idx]
            n += 1
            if abs(av - hv) < 1e-6 if unit == "contract" else abs(av - hv) < 0.01:
                same += 1
            else:
                diffs.append((k, INVESTORS[idx], av, hv))
    rep("- `%s` vs HTS(%s, 필드 `%s`): 일치 **%d / %d칸**%s · API에만 행사가 %d · HTS에만 %d"
        % (label, unit, field, same, n, (" (%.1f%%)" % (100.0 * same / n)) if n else "",
           len(only_api), len(only_hts)))
    if diffs:
        diffs.sort(key=lambda x: -abs(x[2] - x[3]))
        rep("  - 불일치 상위: " + "; ".join("%s %s API=%s HTS=%s" % d for d in diffs[:8])
            + (" … 외 %d칸" % (len(diffs) - 8) if len(diffs) > 8 else ""))
    return same, n


def flow_crosscheck(today, call_res, put_res):
    """7222 먼스리 콜·풋 외인 당일 누적 순매수(최신 분) vs Σ행사가 외인 당일 보유계약. 당일 PK 범위 1행씩."""
    if not os.path.exists(FLOW_DB):
        rep("- 7222 대사: `option_flow.db` 없음 — **미측정**")
        return
    con = sqlite3.connect("file:%s?mode=ro" % FLOW_DB, uri=True)
    try:
        for label, res, prod in (("콜", call_res, "mon_call"), ("풋", put_res, "mon_put")):
            if not res or not res["ok"]:
                rep("- 7222 대사(%s): 9842 응답 없음 — **미측정**" % label)
                continue
            row = con.execute(
                "SELECT bar_time, net_qty FROM option_investor_flow WHERE trade_date=? AND product=? "
                "AND investor='foreign' ORDER BY bar_time DESC LIMIT 1", (today, prod)).fetchone()
            s = sum(r["qty"][1] for r in res["rows"])
            if row is None:
                rep("- 7222 대사(%s): `%s` 당일 행 없음 — **미측정** (9842 Σ외인=%d)" % (label, prod, s))
            else:
                rep("- 7222 대사(%s): 9842 Σ외인 당일 **%+d** vs 7222 `%s` 외인 %s **%+d** → 차 %+d"
                    % (label, s, prod, row[0], row[1], s - row[1]))
    finally:
        con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--end", help="기간 모드 종료일 YYYYMMDD (기본: 오늘 이전 최신 _P 파일 날짜)")
    ap.add_argument("--skip-weekly", action="store_true", help="미문서 월물값 '3'/'4' 요청 생략(-2건)")
    ap.add_argument("--skip-flow", action="store_true", help="option_flow.db 7222 대사 생략")
    a = ap.parse_args()

    today = NOW.strftime("%Y-%m-%d")
    wc, cy = cybos()
    host = socket.gethostname()
    log("pre host=%s connect=%s server_type=%s remain(1)=%s" % (
        host, cy.IsConnect, cy.ServerType, cy.GetLimitRemainCount(1)))
    rep("# CpSvr9842 점검 — %s" % NOW.strftime("%Y-%m-%d %H:%M:%S"))
    rep()
    rep("## T1. 연결")
    rep("- 호스트 `%s` · IsConnect=%s · ServerType=%s (1=CYBOS Plus 서버 / 2=HTS 보통서버 — 2026-10-22 성공 시 2)"
        % (host, cy.IsConnect, cy.ServerType))
    if cy.IsConnect != 1:
        rep("- **연결 없음 — 중단**")
        return finish({})

    master = option_master(wc)
    rep("- CpOptionCode 먼스리 마스터 %d종목 (서버 요청 아님)" % len(master))

    end = a.end
    p_file = None
    if end:
        cand = os.path.join(HTS_DIR, "%s_P.xls" % end[2:])
        p_file = cand if os.path.exists(cand) else None
    else:
        lp = latest_p_before(NOW.strftime("%Y%m%d"))
        if lp:
            end, p_file = lp
    raw = {}

    # ── 요청 ──
    plan = [
        ("call_day", "2", "1", "1", None),
        ("put_day", "3", "1", "1", None),
        ("call_period", "2", "1", "2", end),
        ("put_period", "3", "1", "2", end),
        ("call_day_next", "2", "2", "1", None),
        ("fut_day", "1", "1", "1", None),
    ]
    if not a.skip_weekly:
        plan += [("call_day_m3", "2", "3", "1", None), ("call_day_m4", "2", "4", "1", None)]
    if end is None:
        plan = [p for p in plan if p[3] != "2"]
        rep("- 기간 모드 종료일을 정하지 못함(_P 파일 없음) — 기간 요청 생략")
    for label, mk, mo, pe, en in plan:
        raw[label] = request(wc, cy, label, mk, mo, pe, en)
        time.sleep(0.3)

    # ── T2 커버리지 ──
    rep()
    rep("## T2. 커버리지 (요청 %d건)" % _requests[0])
    rep("| 요청 | 결과 | 행 |")
    rep("|---|---|---|")
    for label, *_ in plan:
        r = raw[label]
        rep("| `%s` | %s | %s |" % (label, "OK" if r["ok"] else "❌ " + r["msg"].replace("|", "/"),
                                    len(r["rows"]) if r["rows"] is not None else "미측정"))

    # ── L3 매핑 · L2(a) 합 0 ──
    rep()
    rep("## L3. 행사가 매핑 · L2(a) 주체 합")
    mapped = {}
    for label, cp in (("call_day", "C"), ("put_day", "P"), ("call_period", "C"), ("put_period", "P"),
                      ("call_day_next", "C")):
        r = raw.get(label)
        if r and r["ok"]:
            mapped[label], _ = map_strikes(label, r, master, None)
            check_sum_zero(label, r)
    fut = raw.get("fut_day")
    if fut and fut["ok"]:
        rep("- `fut_day` 코드: %s" % ", ".join(x["code"] for x in fut["rows"][:10]))
        check_sum_zero("fut_day", fut)

    # ── L1 위클리 ──
    rep()
    rep("## L1. 위클리 지원")
    for label in ("call_day", "put_day", "call_day_next"):
        r = raw.get(label)
        if r and r["ok"]:
            nm = [x["code"] for x in r["rows"] if x["code"] not in master]
            rep("- `%s`: 먼스리 마스터에 없는 코드 **%d개**%s" % (
                label, len(nm), (" (위클리 후보: %s)" % ", ".join(nm[:10])) if nm else " — 전부 먼스리"))
    for label in ("call_day_m3", "call_day_m4"):
        r = raw.get(label)
        if r is None:
            continue
        if r["ok"]:
            nm = [x["code"] for x in r["rows"] if x["code"] not in master]
            rep("- `%s`(미문서 월물값): **응답 %d행** · 먼스리 아닌 코드 %d개 %s" % (
                label, len(r["rows"]), len(nm), nm[:10]))
        else:
            rep("- `%s`(미문서 월물값): ❌ %s" % (label, r["msg"]))

    # ── L2(b) HTS 대조 ──
    rep()
    rep("## L2(b). 기간 모드 vs HTS `_P` (종료일 %s)" % end)
    if p_file:
        hts, unit, head = read_hts(p_file)
        rep("- 파일 `%s` · 단위 %s · 머리행 %s" % (os.path.basename(p_file), unit, "|".join(head)))
        for label, cp in (("call_period", "C"), ("put_period", "P")):
            if label in mapped:
                compare_hts(label, mapped[label], hts, unit, cp)
            else:
                rep("- `%s` 응답 없음 — **미측정**" % label)
    else:
        rep("- 대조할 `_P` 파일 없음 — **미측정**")
    rep("- 당일 모드 대조는 같은 분의 HTS 장중 내보내기(`YYMMDD_HHMM_D`)가 필요하다 — 아래 수동 절차")
    today_d = sorted(glob.glob(os.path.join(HTS_DIR, "%s_????_D.xls" % NOW.strftime("%y%m%d"))))
    if today_d and "call_day" in mapped:
        fn = today_d[-1]
        hts, unit, _ = read_hts(fn)
        rep("- 참고: 오늘 최신 장중 파일 `%s`와 대조(시각 차이만큼 어긋나는 것이 정상)" % os.path.basename(fn))
        compare_hts("call_day", mapped["call_day"], hts, unit, "C")
        if "put_day" in mapped:
            compare_hts("put_day", mapped["put_day"], hts, unit, "P")

    # ── L2(c) 7222 ──
    rep()
    rep("## L2(c). 7222 상품 합계 대사")
    if a.skip_flow:
        rep("- 생략(--skip-flow)")
    else:
        flow_crosscheck(today, raw.get("call_day"), raw.get("put_day"))

    rep()
    rep("## 해석 메모")
    rep("- 기간 모드가 HTS `_P`와 전 칸 일치하면 API = HTS 화면 같은 원천(「추정」이라도 화면과 동일).")
    rep("- 7222 대사 차가 크면: 9842는 증권사 추정치이거나 7222와 집계 기준이 다르다 — 둘 다 기록하고 판정 보류.")
    rep("- 미매핑 코드가 있으면 행사가를 문자열로 추측하지 말 것(1000 이상 행사가 코드는 상장 순서).")
    return finish(raw)


def finish(raw):
    md = os.path.join(LOG_DIR, "probe_9842_%s.md" % STAMP)
    js = os.path.join(LOG_DIR, "probe_9842_%s.json" % STAMP)
    with open(md, "w", encoding="utf-8") as f:
        f.write("\n".join(_report) + "\n")
    with open(js, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False)
    print("\n" + "\n".join(_report))
    print("\n[saved] %s\n[saved] %s\n[requests] %d" % (md, js, _requests[0]))


if __name__ == "__main__":
    main()
