# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] 신동 일일 리포트 md → PDF. 본체는 `utils/report_pdf.py`.

사용:
    python scripts/shindong_report_pdf.py 2026-09-28
    python scripts/shindong_report_pdf.py docs/신동거래/일일/신동_일일_20260928.md
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import SHINDONG_DAILY_REPORT_DIR  # noqa: E402
from utils.report_pdf import md_to_pdf  # noqa: E402


def main(argv=None) -> int:
    for a in (argv if argv is not None else sys.argv[1:]) or []:
        p = a if a.endswith(".md") else os.path.join(SHINDONG_DAILY_REPORT_DIR, "신동_일일_%s.md" % a.replace("-", ""))
        print(md_to_pdf(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
