# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] 신동 일일 리포트를 PDF 로 만들어 메일로 보낸다.

본체는 `strategy/shindong/report_mail.py`. 라이브는 `main.py:daily_close` 가 백그라운드 스레드로 부른다
(`SHINDONG_REPORT_MAIL_ENABLED`). SMTP 자격 정보는 환경변수 — `utils/mailer.py` 머리말 참조.

사용:
    python scripts/shindong_report_mail.py                    # 오늘
    python scripts/shindong_report_mail.py 2026-09-28
    python scripts/shindong_report_mail.py 2026-09-28 --check # 설정만 점검(보내지 않음)
"""
import argparse
import datetime as _dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils import mailer  # noqa: E402
from strategy.shindong.report_mail import send_daily  # noqa: E402


def main(argv=None) -> int:
    from config.settings import SHINDONG_DAILY_REPORT_DIR
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("date", nargs="?", default=_dt.date.today().isoformat())
    ap.add_argument("--check", action="store_true", help="SMTP 설정만 점검")
    a = ap.parse_args(argv)
    cfg, missing = mailer.smtp_config()
    if cfg is None:
        print("SMTP 미설정 — 빠진 환경변수: %s" % ", ".join(missing))
        return 2
    print("SMTP %s:%s · 보내는 %s · 받는 %s" % (cfg["host"], cfg["port"], cfg["user"], ", ".join(cfg["to"])))
    if a.check:
        return 0
    print("발송 완료 → %s" % send_daily(a.date, SHINDONG_DAILY_REPORT_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
