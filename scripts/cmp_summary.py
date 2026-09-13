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


def _same_channel(a, b):
    """두 행이 **같은 채널**인가 — 번호 충돌과 구분하기 위한 판정.

    리포트는 같은 채널을 요약표와 수치표 양쪽에 싣는다(예: `[25]` · `[3-B]` ·
    `[23-B]`). 뒤쪽 이름에 `⚠**부호 역전**` 같은 꼬리표가 붙기도 하므로 **접두
    일치**로 본다. 이름이 아예 다르면 서로 **다른 채널이 같은 번호를 쓴 것**이고,
    그것만 경보 대상이다 — 정상 반복까지 빨갛게 칠하면 경보가 무의미해진다.
    """
    a, b = a.strip(), b.strip()
    return a == b or a.startswith(b) or b.startswith(a)


def rows(p):
    """(채널 dict, 등장 순서, 중복 목록).

    🔴 [MW0602 564차] 종전에는 같은 번호가 두 번 나오면 `continue` 로 **조용히
    버렸다.** 2026-09-07~09-13 사이 `[58]`·`[59]` 가 실제로 겹쳤고(MW0602 526차
    후속 vs MW0601 541차), 그동안 이 도구는 MW0602 채널 2개를 대조에서 빠뜨린 채
    채널 수까지 2 적게 찍었다 — 게다가 CLAUDE.md 가 경고하는 "only 줄"에도 안
    걸린다(양쪽에 다 있는 번호라서). 번호를 고쳐도 다음 충돌 때 또 먹히므로
    **도구 쪽도 고친다.**

    이제 두 번째부터는 `[58]#2` 처럼 접미를 붙여 **양쪽 다 보존**하고, 중복 자체를
    호출부에 돌려준다. 계측 4원칙 ③ — 탈락시킬 거면 몇 개를 왜 탈락시켰는지 남겨라.
    """
    d, order, dups = {}, [], []
    for ln in io.open(p, encoding='utf-8'):
        m = ROW.match(ln)
        if not m:
            continue
        k = m.group(1)
        row = (m.group(2).strip(), m.group(3).strip(), m.group(4).strip())
        if k in d:
            if _same_channel(d[k][0], row[0]):
                continue          # 같은 채널이 다른 표에 또 나온 것 — 종전대로 첫 행을 쓴다
            dups.append((k, row[0]))
            i = 2
            while u"%s#%d" % (k, i) in d:
                i += 1
            k = u"%s#%d" % (k, i)
        d[k] = row
        order.append(k)
    return d, order, dups


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pc1", default="MW0601")
    ap.add_argument("--pc2", default="MW0602")
    ap.add_argument("--date1", default=None, help="YYYYMMDD (기본: 최신본)")
    ap.add_argument("--date2", default=None, help="YYYYMMDD (기본: 최신본)")
    args = ap.parse_args()

    p1 = latest(args.pc1, "report", args.date1)
    p2 = latest(args.pc2, "report", args.date2)

    a, oa, da = rows(p1)
    b, ob, db = rows(p2)
    out = []
    out.append(u"%s: %s" % (args.pc1, os.path.basename(p1)))
    out.append(u"%s: %s" % (args.pc2, os.path.basename(p2)))
    out.append(u"")
    out.append(u"%s %d채널 / %s %d채널" % (args.pc1, len(a), args.pc2, len(b)))
    out.append(u"%s only: %s" % (args.pc1, u' '.join(k for k in oa if k not in b)))
    out.append(u"%s only: %s" % (args.pc2, u' '.join(k for k in ob if k not in a)))
    # [MW0602 564차] 번호 중복은 "only" 줄로는 절대 드러나지 않는다 — 따로 찍는다.
    for pc, dd in ((args.pc1, da), (args.pc2, db)):
        if dd:
            out.append(u"🔴 %s 채널 번호 중복 %d건 — 대조가 왜곡된다. "
                       u"리포트 생성기의 번호 배정을 고칠 것: %s"
                       % (pc, len(dd), u' '.join(u"%s%s" % (k, n) for k, n in dd)))
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
