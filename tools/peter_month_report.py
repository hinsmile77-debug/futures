# -*- coding: utf-8 -*-
"""피터 사료 월간 보고서 — `peter_paste` 에 적재된 그대로를 문서로 낸다.

왜 스크립트인가
    문서를 손으로 쓰면 DB 와 갈라진다. 여기서는 **DB 가 원본**이고 문서는 그
    투영이다. 사료를 고쳤으면 이걸 다시 돌리면 된다 — 문서만 고치는 일은 없다.
    (반대로 문서를 고쳤다면 그 수정은 `data/peter_feed/*_{lv,tr}.txt` 와 DB 에
     먼저 반영해야 한다. 문서는 출력이지 입력이 아니다.)

⛔ 손익(PNL)은 **피터리 본인이 공개한 값**이다. 계산하지 않는다 — 그가 말한
   숫자를 옮겨 적을 뿐이다. 없는 달은 비워 둔다.

실행:
    python tools/peter_month_report.py 2026-08 --out <파일>
"""
import argparse
import datetime
import io
import os
import re
import sqlite3
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'tools'))
import peter_feed as pf                                              # noqa: E402

WD = ['월', '화', '수', '목', '금', '토', '일']
TS = re.compile(r'^\s*\d{1,2}:\d{2}\s*(AM|PM)\s*[·•]', re.I)

# 피터리가 2026-08-31 10:27 에 직접 공개한 일별 손익. 계산값이 아니다.
PNL = {
 '2026-08-04': ('+46P',   '5P 손절 2회 -10P / 965 매수 → 995 청산 +30P / 974 매수 → 1000 청산 +26P'),
 '2026-08-11': ('+3~+6.5P', '매도 손절 -6~-8P / 이후 매수 청산 +11~+12.5P'),
 '2026-08-12': ('+11P',   '1012 매수 → 1023 청산'),
 '2026-08-13': ('+13P',   '첫 매매 +9P / 추가 매매 +4P'),
 '2026-08-14': ('-6~-8P', '손절 합계 -16~-18P / 마지막 익절 +10P'),
 '2026-08-18': ('-17P',   '5P 손절 / 8P 손절 / 4P 손절'),
 '2026-08-19': ('+14P',   '1010 매수 → 1024 청산'),
 '2026-08-20': ('+40P',   '1041 매수 → 1081 청산'),
 '2026-08-24': ('-4P',    '1082 매수 → 1077 손절 / 재매수 후 수익, 당일 공개 손익 -4P'),
 '2026-08-25': ('+8P',    '1029 매수 후 손절 -5P / 1010 매수 → 1023 청산 +13P'),
 '2026-08-26': ('+7P',    '1085 매도 → 1078 청산'),
 '2026-08-27': ('+6P',    '1105 매수 → 1100 손절 -5P / 1102 매도 → 1091 청산 +11P'),
 '2026-08-31': ('+11P',   '1051 매도 → 1040 청산'),
}
HEAD = {
 '2026-08': [
  "**손익** 피터리가 2026-08-31 10:27 에 직접 공개한 일별 내역 — 계산값이 아니다\n",
  "\n> ⚠ **8/18 장중 트윗과 8/11 10:17 이전 트윗은 X 에 남아 있지 않다.** 삭제된 것으로 보인다.",
  "> 두 날 모두 손실이 컸던 날이다. 본인 요약만 남아 있어 그대로 적는다.\n",
  "\n## 월간 요약 — 본인 공개 기준\n",
  "| 항목 | 값 |\n|---|---|",
  "| 실시간 중계 매매일 | 13일 |",
  "| 수익 / 손실 | 10일 / 3일 (승률 77%) |",
  "| 누적 | **+130P ~ +135.5P** (본인 환산 수익률 65~70%) |",
  "| 최대 수익 | +46P (8/4) |",
  "| 최대 손실 | -17P (8/18) |",
 ],
}


def build(month, dbpath):
    P = pf._load_parsers()
    con = sqlite3.connect("file:%s?mode=ro" % dbpath.replace('\\', '/'), uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT * FROM peter_paste WHERE date LIKE ? ORDER BY date", (month + '%',))]
    if not rows:
        raise SystemExit("%s 사료가 DB 에 없다." % month)
    y, m = month.split('-')
    o = ["# 피터리(@PeterLeejoa) %s년 %s월 선물매매 기록\n" % (y, int(m))]
    o.append("**출처** X 검색 `from:PeterLeejoa` (Latest) · **계약** 정규 KOSPI200 선물 · **시각** KST\n")
    o.append("**오프셋** 각 날짜의 `median(미륵이 계약 − 정규 10100)`, 정규장 오전 09:00–11:30 실측\n")
    o.append("**원본** `data/db/peter_levels.db:peter_paste` · 입력 `data/peter_feed/%s-*_{lv,tr}.txt`\n" % month)
    o += HEAD.get(month, [])
    o.append("\n## 일자별\n")
    for r in rows:
        d = r['date']
        dt = datetime.date(*[int(x) for x in d.split('-')])
        pnl, note = PNL.get(d, ('—', ''))
        od, rs, ax, uk = P['parse_peter_orders'](r['raw_lv'] or '', r['offset'], d)
        tr, err = P['parse_peter_trades'](r['raw_tr'] or '', r['offset'], d)
        o.append("\n### %s (%s)  ·  **%s**" % (d[5:].replace('-', '/'), WD[dt.weekday()], pnl))
        o.append("\n본인 요약: %s  \n미륵이 오프셋: **%+.2f**\n" % (note, r['offset']))
        o.append("| 시각 | 원문 |\n|---|---|")
        buf = []
        for ln in (r['raw_lv'] or '').splitlines():
            if TS.match(ln):
                t = ln.split('·')[0].strip()
                h, mi = t.split(':'); mi, ap = mi.split()
                h = int(h) + (12 if ap.upper() == 'PM' and int(h) != 12 else 0)
                if ap.upper() == 'AM' and int(h) == 12:
                    h = 0
                o.append("| %02d:%s | %s |" % (h, mi, " ".join(buf).replace('|', '/')))
                buf = []
            elif ln.strip():
                buf.append(ln.strip())
        if tr:
            o.append("\n**거래** — 오프셋 반영 **차트가격**(그의 정규 숫자 %+.2f)\n" % r['offset'])
            o.append("| 진입 | 방향 | 진입가 | 청산 | 청산가 | 손익 | 사유 |\n|---|---|---|---|---|---|---|")
            for t in tr:
                pl = None
                if t['exit_price'] is not None:
                    pl = ((t['exit_price'] - t['entry_price']) if t['direction'] == 'LONG'
                          else (t['entry_price'] - t['exit_price']))
                o.append("| %s | %s | %g | %s | %s | %s | %s |" % (
                    t['entry_hm'], '매수' if t['direction'] == 'LONG' else '매도',
                    t['entry_price'], t['exit_hm'] or '미결',
                    ('%g' % t['exit_price']) if t['exit_price'] is not None else '—',
                    ('%+.2fp' % pl) if pl is not None else '—', t['why']))
        else:
            o.append("\n**거래** — 체결 시각이 트윗에 없어 적지 않는다(추론하지 않는다).\n")
        o.append("\n미륵이 파서 판정: 지시 %d · 예고 %d · 결과 %d · 미분류 %d · 거래 %d%s"
                 % (len(od), len(ax), len(rs), len(uk), len(tr),
                    ("  · ⚠형식오류 %d" % len(err)) if err else ""))
    o.append("\n---\n")
    o.append("## 미륵이에서 보는 법\n")
    o.append("복기 차트에서 해당 날짜를 열고 「피터맥점」·「거래피터」 토글을 켠다.")
    o.append("문서를 고쳤다면 `data/peter_feed/*_{lv,tr}.txt` 와 DB 에 먼저 반영하고")
    o.append("`python tools/peter_month_report.py %s --out <파일>` 로 다시 낸다 —\n" % month)
    o.append("**문서는 출력이지 입력이 아니다.**\n")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("month", help="YYYY-MM")
    ap.add_argument("--out", required=True)
    ap.add_argument("--db", default=os.path.join(_ROOT, 'data', 'db', 'peter_levels.db'))
    a = ap.parse_args()
    txt = build(a.month, a.db)
    io.open(a.out, 'w', encoding='utf-8').write(txt)
    print("생성: %s (%d자)" % (a.out, len(txt)))


if __name__ == "__main__":
    main()
