# -*- coding: utf-8 -*-
"""MW0601 × MW0602 검증 캠페인 리포트 요약표 대조.

[MW0601 407차] 경로 하드코딩을 걷어냈다 — 각 PC 폴더
(docs/정기점검/금요일점검/<PC>/)의 **최신 날짜본**을 자동으로 짝지어 읽는다.
특정 주차를 보려면 --date1/--date2로 지정한다.

    python scripts/cmp_summary.py
    python scripts/cmp_summary.py --date1 20260801 --date2 20260801

⚠ 대조는 **같은 코드 세대로 생성된 리포트끼리** 해야 한다. 채널 집합이 다르면
(한쪽에만 있는 채널이 있으면) 그 차이는 PC 차이가 아니라 코드 세대 차이다 —
출력 상단의 "only" 줄이 둘 다 비어 있는지 먼저 확인할 것.
"""
import argparse
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.campaign_report_paths import latest  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROW = re.compile(r'^\| (\[[0-9A-B-]+\])([^|]*)\|([^|]*)\|(.*)\|\s*$')


def rows(p):
    d, order = {}, []
    for ln in io.open(p, encoding='utf-8'):
        m = ROW.match(ln)
        if m:
            k = m.group(1)
            if k in d:
                continue
            d[k] = (m.group(2).strip(), m.group(3).strip(), m.group(4).strip())
            order.append(k)
    return d, order


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pc1", default="MW0601")
    ap.add_argument("--pc2", default="MW0602")
    ap.add_argument("--date1", default=None, help="YYYYMMDD (기본: 최신본)")
    ap.add_argument("--date2", default=None, help="YYYYMMDD (기본: 최신본)")
    args = ap.parse_args()

    p1 = latest(args.pc1, "report", args.date1)
    p2 = latest(args.pc2, "report", args.date2)

    a, oa = rows(p1)
    b, ob = rows(p2)
    out = []
    out.append(u"%s: %s" % (args.pc1, os.path.basename(p1)))
    out.append(u"%s: %s" % (args.pc2, os.path.basename(p2)))
    out.append(u"")
    out.append(u"%s %d채널 / %s %d채널" % (args.pc1, len(a), args.pc2, len(b)))
    out.append(u"%s only: %s" % (args.pc1, u' '.join(k for k in oa if k not in b)))
    out.append(u"%s only: %s" % (args.pc2, u' '.join(k for k in ob if k not in a)))
    out.append(u"")
    out.append(u"| 채널 | %s | %s | 일치 |" % (args.pc1, args.pc2))
    out.append(u"|---|---|---|---|")
    same = diff = 0
    for k in oa:
        if k not in b:
            continue
        va, vb = a[k][1], b[k][1]
        ok = u"=" if va == vb else u"**X**"
        if va == vb:
            same += 1
        else:
            diff += 1
        out.append(u"| %s%s | %s | %s | %s |" % (k, a[k][0], va, vb, ok))
    out.append(u"")
    out.append(u"판정 일치 %d / 불일치 %d" % (same, diff))
    out.append(u"")
    out.append(u"=== 핵심수치 (판정 일치 채널 포함 전수) ===")
    for k in oa:
        if k not in b:
            continue
        out.append(u"%s%s" % (k, a[k][0]))
        out.append(u"  %s: %s | %s" % (args.pc1, a[k][1], a[k][2]))
        out.append(u"  %s: %s | %s" % (args.pc2, b[k][1], b[k][2]))

    sys.stdout.write(u"\n".join(out) + u"\n")


if __name__ == "__main__":
    main()
