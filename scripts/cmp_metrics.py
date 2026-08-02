# -*- coding: utf-8 -*-
"""metrics JSON 레벨 전수 대조 — 부호 역전 / 상대차 / 표본·구조 비대칭 탐지.

[MW0601 407차] 경로 하드코딩을 걷어냈다 — 각 PC 폴더의 **최신 날짜본**을 자동 선택.

    python scripts/cmp_metrics.py
    python scripts/cmp_metrics.py --date1 20260801 --date2 20260801

부호 역전은 313차 원칙상 **단일 PC 근거로 채택 금지** 대상이다. 다만 원인이
(a) 진짜 표본 노이즈인지 (b) PC 로컬 설정 차이인지 (c) A/B 기준선 오염인지는
이 스크립트가 구분해 주지 않는다 — 0802 대조문서 §2~§3의 분류를 함께 볼 것.
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.campaign_report_paths import latest  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    unicode
except NameError:
    unicode = str

_SAMPLE_KEYS = ("n", "count", "samples", "n_total", "days")


def flat(o, pre, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            flat(v, pre + u"." + unicode(k) if pre else unicode(k), acc)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            flat(v, u"%s[%d]" % (pre, i), acc)
    else:
        acc[pre] = o
    return acc


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pc1", default="MW0601")
    ap.add_argument("--pc2", default="MW0602")
    ap.add_argument("--date1", default=None, help="YYYYMMDD (기본: 최신본)")
    ap.add_argument("--date2", default=None, help="YYYYMMDD (기본: 최신본)")
    ap.add_argument("--rel", type=float, default=0.5,
                    help="'상대차 큼'으로 볼 기준 (기본 0.5 = 50%%)")
    args = ap.parse_args()

    j1 = latest(args.pc1, "metrics", args.date1)
    j2 = latest(args.pc2, "metrics", args.date2)
    a = json.load(io.open(j1, encoding='utf-8'))
    b = json.load(io.open(j2, encoding='utf-8'))

    fa, fb = flat(a, u"", {}), flat(b, u"", {})
    keys = sorted(set(fa) & set(fb))
    only_a = sorted(set(fa) - set(fb))
    only_b = sorted(set(fb) - set(fa))

    inv, big, samp = [], [], []
    for k in keys:
        x, y = fa[k], fb[k]
        if isinstance(x, bool) or isinstance(y, bool):
            continue
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            continue
        if x == 0 and y == 0:
            continue
        if x * y < 0:
            inv.append((k, x, y))
            continue
        if k.split(u".")[-1] in _SAMPLE_KEYS:
            if x != y:
                samp.append((k, x, y))
            continue
        m = max(abs(x), abs(y))
        if m > 0 and abs(x - y) / m >= args.rel:
            big.append((k, x, y))

    out = []
    out.append(u"%s: %s" % (args.pc1, os.path.basename(j1)))
    out.append(u"%s: %s" % (args.pc2, os.path.basename(j2)))
    out.append(u"")
    out.append(u"공통 수치 키 %d / %s 전용 %d / %s 전용 %d"
               % (len(keys), args.pc1, len(only_a), args.pc2, len(only_b)))

    def _dump(title, items):
        out.append(u"")
        out.append(u"### %s %d건" % (title, len(items)))
        for k, x, y in items:
            out.append(u"  %-58s %s=%-14s %s=%s" % (k, args.pc1, x, args.pc2, y))

    _dump(u"부호 역전", inv)
    _dump(u"상대차 >=%d%%" % int(args.rel * 100), big)
    _dump(u"표본수 차이", samp)
    out.append(u"")
    out.append(u"### 구조 비대칭 (한쪽에만 있는 키)")
    out.append(u"  %s only: %s" % (args.pc1, u", ".join(only_a[:60])))
    out.append(u"  %s only: %s" % (args.pc2, u", ".join(only_b[:60])))
    sys.stdout.write(u"\n".join(out) + u"\n")


if __name__ == "__main__":
    main()
