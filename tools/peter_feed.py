# -*- coding: utf-8 -*-
"""피터리 사료 입력 — GUI 붙여넣기 창과 **같은 경로**로 DB 에 넣고, **같은 파서**로 검증한다.

왜 있나
    「피터리 사료 붙여넣기」 창은 사람이 손으로 채우는 입구다. 날짜가 쌓이면
    같은 일을 반복하게 되고, 무엇보다 **저장한 뒤 화면을 열어봐야** 제대로
    들어갔는지 알 수 있다. 이 스크립트는 그 두 가지를 없앤다 —
    파일로 넣고, 저장 즉시 파서를 돌려 숫자로 확인한다.

절대 원칙
    ⛔ 파서를 **다시 구현하지 않는다.** main_dashboard.py 의 것을 그대로 쓴다.
       (PyQt5 가 없는 환경에서는 그 파일의 파서 구간 **원본 소스**를 떼어 실행한다.
        베끼는 게 아니라 같은 글자를 읽는 것이다 — 갈라질 수 없다.)
    ⛔ 레벨을 **만들어내지 않는다.** 그가 쓴 숫자를 옮길 뿐이다.
    ⛔ 오프셋을 **추정하지 않는다.** 인자로 받은 값을 그대로 쓴다.

쓰는 법
    python tools/peter_feed.py --date 2026-09-16 --lv lv.txt --tr tr.txt --offset -4.00
    python tools/peter_feed.py --date 2026-09-16 --dry --lv lv.txt --tr tr.txt
    python tools/peter_feed.py --date 2026-09-16 --show
    python tools/peter_feed.py --verify-all
"""
import argparse
import io
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MD = os.path.join(_ROOT, "dashboard", "main_dashboard.py")


def _load_parsers():
    """진짜 파서를 가져온다. 실패하면 **원본 소스 구간**을 떼어 실행한다."""
    try:
        from dashboard.main_dashboard import (      # noqa: F401
            parse_peter_orders, parse_peter_text, parse_peter_trades,
            PETER_DEFAULT_OFFSET)
        return dict(parse_peter_orders=parse_peter_orders,
                    parse_peter_text=parse_peter_text,
                    parse_peter_trades=parse_peter_trades,
                    PETER_DEFAULT_OFFSET=PETER_DEFAULT_OFFSET,
                    _via="import")
    except Exception:
        pass
    src = io.open(_MD, encoding="utf-8").read()
    _s, _e = "_PT_N = r'", "def peter_db_path"
    if _s not in src or _e not in src:
        raise SystemExit("main_dashboard.py 에서 파서 구간을 찾지 못했다 — 표식이 바뀌었다.")
    blk = src[src.index(_s):src.index(_e)]
    ns = {"re": re, "os": os}
    exec(compile(blk, "<main_dashboard:peter-parser>", "exec"), ns)
    ns["_via"] = "source-slice"
    return ns


def _db_path():
    """설정을 읽을 수 있으면 읽고, 아니면 프로젝트 기본 경로를 쓴다."""
    try:
        from config.settings import DB_DIR
        return os.path.join(DB_DIR, "peter_levels.db")
    except Exception:
        return os.path.join(_ROOT, "data", "db", "peter_levels.db")


PETER_DDL = """
CREATE TABLE IF NOT EXISTS peter_paste (
    date      TEXT PRIMARY KEY,
    offset    REAL NOT NULL DEFAULT 0,
    raw_lv    TEXT,
    raw_tr    TEXT,
    saved_at  TEXT
)
"""


def db_load(date):
    import sqlite3
    p = _db_path()
    if not os.path.exists(p):
        return None
    with sqlite3.connect(p) as c:
        c.row_factory = sqlite3.Row
        r = c.execute("SELECT * FROM peter_paste WHERE date=?", (date,)).fetchone()
    return dict(r) if r else None


def db_save(date, offset, raw_lv, raw_tr):
    import sqlite3
    import datetime
    with sqlite3.connect(_db_path()) as c:
        c.execute(PETER_DDL)
        c.execute("INSERT OR REPLACE INTO peter_paste(date,offset,raw_lv,raw_tr,saved_at)"
                  " VALUES(?,?,?,?,?)",
                  (date, float(offset or 0.0), raw_lv or "", raw_tr or "",
                   datetime.datetime.now().isoformat(timespec="seconds")))


# ── 입력 정리 ────────────────────────────────────────────────────────
# 트윗을 그대로 복사하면 **본문 안에 빈 줄**이 섞여 온다. 파서는 빈 줄에서
# 블록을 닫으므로, 한 트윗이 두 덩이로 쪼개지고 앞 덩이는 시각을 잃는다
# (실측 2026-09-16 08:58 트윗). 그래서 **시각 줄 앞의 빈 줄만** 지운다.
_TS_LINE = re.compile(
    r'^\s*\d{1,2}:\d{2}\s*(AM|PM)\s*[·•]\s*[A-Za-z]{3}\s+\d{1,2},\s*\d{4}\s*$', re.I)


def tidy_lv(text):
    """트윗 블록 안의 빈 줄을 접는다. 블록 경계(시각 줄)는 건드리지 않는다."""
    out, buf = [], []
    for ln in (text or "").splitlines():
        if _TS_LINE.match(ln):
            out.extend([x for x in buf if x.strip()])
            out.append(ln.strip())
            out.append("")
            buf = []
            continue
        buf.append(ln.rstrip())
    out.extend([x for x in buf if x.strip()])
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


_TR_HM = re.compile(r'^(\s*)(\d):(\d{2})')


def tidy_tr(text):
    """거래 줄의 시:분을 두 자리로 맞춘다. `9:00` 과 `09:00` 이 섞이면 눈이 속는다."""
    out = []
    for ln in (text or "").splitlines():
        ln = ln.rstrip()
        if not ln.strip():
            continue
        ln = _TR_HM.sub(lambda m: "%s0%s:%s" % (m.group(1), m.group(2), m.group(3)), ln)
        ln = re.sub(r'/\s*(\d):(\d{2})', lambda m: "/ 0%s:%s" % (m.group(1), m.group(2)), ln)
        out.append(ln)
    return "\n".join(out) + "\n"


# ── 검증 ─────────────────────────────────────────────────────────────
def verify(date, offset, raw_lv, raw_tr, P, quiet=False):
    """저장된 그대로를 **화면과 같은 순서로** 다시 계산해 보여준다."""
    od, rs, ax, uk = P["parse_peter_orders"](raw_lv or "", offset, date)
    src = "\n".join([x["raw"] for x in od] + [x["raw"] for x in ax]
                    + [x["raw"] for x in uk])
    lv = P["parse_peter_text"](src, offset)
    tr, err = P["parse_peter_trades"](raw_tr or "", offset, date)
    if not quiet:
        K = {'level_pub': '레벨공개', 'entry_brk': '진입(돌파)', 'entry_dip': '진입(눌림)',
             'entry': '진입', 'entry_sell': '진입(매도)', 'fill_buy': '매수체결',
             'fill_exit': '청산체결', 'stop': '손절', 'target': '목표',
             'half': '절반', 'exit_cond': '조기청산'}
        print("── %s · 오프셋 %+.2f ─────────────────────" % (date, offset))
        print("지시 %d건" % len(od))
        for o in od:
            print("   %-5s %-9s 진입 %.2f  손절 %s  목표 %s   | %s"
                  % (o["hm"] or "--:--", K.get(o["kind"], o["kind"]), o["entry"],
                     ("%.2f" % o["stop"]) if o["stop"] else "--",
                     ("%.2f" % o["target"]) if o["target"] else "--", o["raw"][:46]))
        AK = {'target': '목표', 'exit_cond': '조기청산', 'stop': '손절',
              'half': '절반', 'level_pub': '레벨'}
        print("예고 %d건 (진입 없이 목표·손절만 말한 줄 — 피터맥점)" % len(ax))
        for a in ax:
            print("   %-5s %s   | %s"
                  % (a["hm"] or "--:--",
                     " · ".join("%s %g" % (AK.get(m["kind"], m["kind"]), m["level_adj"])
                                for m in a["marks"]), a["raw"][:40]))
        print("결과 %d건 (선으로 안 그림)" % len(rs))
        for x in rs:
            print("   %-5s %s" % (x["hm"] or "--:--", x["raw"][:56]))
        print("미분류 %d건 (레벨은 뽑되 깃발은 안 꽂음)" % len(uk))
        for x in uk:
            print("   %-5s %s" % (x["hm"] or "--:--", x["raw"][:56]))
        print("레벨선 %d개" % len(lv))
        for h in lv:
            print("   %-9s 그의값 %-8.2f → 차트 %.2f" % (K.get(h["kind"], h["kind"]),
                                                     h["level"], h["level_adj"]))
        print("거래 %d건%s" % (len(tr), (" · ⚠형식오류 %d줄" % len(err)) if err else ""))
        for t in tr:
            print("   %s %s %.2f → %s %s  %s"
                  % (t["entry_hm"], t["direction"], t["entry_price"],
                     t["exit_hm"] or "미결",
                     ("%.2f" % t["exit_price"]) if t["exit_price"] is not None else "--",
                     t["why"]))
        for e in err:
            print("   ⚠ 형식오류: %s" % e)
    return dict(orders=len(od), results=len(rs), aux=len(ax), unknown=len(uk),
                levels=len(lv), trades=len(tr), errors=len(err))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD")
    ap.add_argument("--lv", help="① 지시 트윗 원문 파일")
    ap.add_argument("--tr", help="② 거래 파일")
    ap.add_argument("--offset", type=float, default=None)
    ap.add_argument("--dry", action="store_true", help="저장하지 않고 검증만")
    ap.add_argument("--show", action="store_true", help="DB 에 있는 그날치를 검증 출력")
    ap.add_argument("--verify-all", action="store_true", help="DB 의 모든 날짜 요약")
    ap.add_argument("--no-tidy", action="store_true", help="입력 정리를 끈다")
    a = ap.parse_args()

    P = _load_parsers()
    dflt = P.get("PETER_DEFAULT_OFFSET", -4.00)
    print("[파서 %s] DB %s" % (P.get("_via", "?"), _db_path()))

    if a.verify_all:
        import sqlite3
        with sqlite3.connect(_db_path()) as c:
            c.row_factory = sqlite3.Row
            rows = [dict(r) for r in c.execute("SELECT * FROM peter_paste ORDER BY date")]
        for r in rows:
            s = verify(r["date"], float(r["offset"] or 0), r["raw_lv"], r["raw_tr"], P, quiet=True)
            print("%s  오프셋 %+.2f  지시%d 예고%d 결과%d 미분류%d 레벨선%d 거래%d%s"
                  % (r["date"], float(r["offset"] or 0), s["orders"], s["aux"],
                     s["results"], s["unknown"], s["levels"], s["trades"],
                     ("  ⚠형식오류%d" % s["errors"]) if s["errors"] else ""))
        return

    if not a.date:
        raise SystemExit("--date 가 필요하다")

    if a.show:
        row = db_load(a.date)
        if not row:
            raise SystemExit("%s 사료 없음" % a.date)
        verify(a.date, float(row["offset"] or 0), row["raw_lv"], row["raw_tr"], P)
        print("저장시각 %s" % row.get("saved_at"))
        return

    row = db_load(a.date) or {}
    raw_lv = io.open(a.lv, encoding="utf-8").read() if a.lv else (row.get("raw_lv") or "")
    raw_tr = io.open(a.tr, encoding="utf-8").read() if a.tr else (row.get("raw_tr") or "")
    if not a.no_tidy:
        raw_lv, raw_tr = tidy_lv(raw_lv), tidy_tr(raw_tr)
    # 오프셋 우선순위 — 인자 > 그날 저장값 > 기본값. 추정은 어디에도 없다.
    off = a.offset if a.offset is not None else (
        float(row["offset"]) if row.get("offset") is not None else dflt)

    verify(a.date, off, raw_lv, raw_tr, P)
    if a.dry:
        print("\n[dry] 저장하지 않았다.")
        return
    db_save(a.date, off, raw_lv, raw_tr)
    print("\n저장 완료 → %s  (%s, 오프셋 %+.2f)" % (_db_path(), a.date, off))
    print("차트에서 %s 선택 후 「피터맥점」·「거래피터」 토글을 켜라." % a.date)


if __name__ == "__main__":
    main()
