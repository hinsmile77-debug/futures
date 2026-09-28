# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] 신동 일일 리포트 → PDF → 메일.

`main.py:daily_close` 가 리포트 생성 직후 **백그라운드 스레드**에서 `send_daily` 를 부른다
(`SHINDONG_REPORT_MAIL_ENABLED`). Qt 를 건드리지 않는다 — 파일 읽기·브라우저 인쇄·SMTP 뿐이다.
자격 정보는 환경변수(`utils/mailer.py` 머리말). 수동: `python scripts/shindong_report_mail.py YYYY-MM-DD`.
"""
import os
import re

from utils import mailer
from utils.report_pdf import md_to_pdf


def _summary(md_text: str) -> str:
    """메일 본문 — 리포트 §0 의 표 두 개와 「오늘의 한 줄」을 평문으로."""
    sec = md_text.split("## 1. 차트")[0]
    out = []
    for line in sec.splitlines():
        if line.startswith("|---"):
            continue
        if line.startswith("|"):
            out.append("  " + " / ".join(c.strip() for c in line.strip("|").split("|")))
        elif line.startswith("**오늘의 한 줄**"):
            out.append("")
            out.append(re.sub(r"\*\*", "", line))
    return "\n".join(out)


def send_daily(trade_date: str, report_dir: str, to=None, pc=None) -> str:
    """md → PDF → 메일. 반환: 받는 사람 문자열. 리포트가 없으면 FileNotFoundError."""
    from strategy.shindong.daily_report import report_stem
    if pc is None:
        from utils.db_utils import pc_id
        pc = pc_id()
    md = os.path.join(report_dir, report_stem(trade_date, pc) + ".md")
    if not os.path.exists(md):
        raise FileNotFoundError("리포트 없음: %s" % md)
    pdf = md_to_pdf(md)
    with open(md, encoding="utf-8") as f:
        text = f.read()
    body = ("[%s] 신동 일일 리포트 %s — %s PC 의 리포트다. 전문은 첨부 PDF.\n\n%s\n\n"
            "※ 가상거래(주문 없음). 판정 전 집계이므로 규격 변경 근거로 쓰지 말 것.\n— 미륵이 %s 자동 발송"
            % (pc, trade_date, pc, _summary(text), pc))
    rcpt = mailer.send_mail("[신동][%s] 일일 리포트 %s" % (pc, trade_date), body, [pdf], to=to)
    return ", ".join(rcpt)
