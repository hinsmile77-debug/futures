# -*- coding: utf-8 -*-
"""[MW0602 2026-10-17] 긴급 알림 메일 설정 점검 — 시험 메일 1통 + Slack 1줄.

    conda run -n py37_32 python scripts/alert_mail_test.py            # 상태만 출력
    conda run -n py37_32 python scripts/alert_mail_test.py --send     # 실제로 1통 보낸다

제목은 `[시험][PC] 긴급 알림 메일 점검` — 실제 경보(`[긴급이상]`)와 섞이지 않게 한다.
에피소드 상태·하루 상한은 건드리지 않는다(상태 파일에 쓰지 않는다).
자격 증명은 환경변수(MIREUK_SMTP_USER / MIREUK_SMTP_PASSWORD / MIREUK_REPORT_MAIL_TO)에서만 읽고
출력하지 않는다 — 수신자도 개수만 적는다.
"""
import argparse
import datetime
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main(argv=None):
    ap = argparse.ArgumentParser(description="긴급 알림 메일 설정 점검")
    ap.add_argument("--send", action="store_true", help="시험 메일 1통과 Slack 1줄을 실제로 보낸다")
    args = ap.parse_args(argv)
    for _stream in ("stdout", "stderr"):
        try:
            getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    from utils import alert_mail as am
    m = am.AlertMailer(proc="selftest")
    print(am.status_line(m))
    print("카탈로그 %d종: %s" % (len(am.CATALOG), " ".join(sorted(am.CATALOG))))
    if not args.send:
        print("(--send 를 주면 시험 메일 1통을 보낸다)")
        return 0

    now = datetime.datetime.now()
    subject = "[시험][%s] 긴급 알림 메일 점검 %s" % (m.pc, now.strftime("%H:%M"))
    body = "\n".join([
        "%s · PC %s" % (now.strftime("%Y-%m-%d %H:%M:%S"), m.pc),
        "긴급 알림 메일(utils/alert_mail.py) 설정 점검용 시험 메일입니다. 조치할 것은 없습니다.",
        "실제 경보 제목은 [긴급이상][PC][코드] / [이상해소][PC][코드] 형식입니다.",
    ])
    rc = 0
    try:
        from utils import mailer
        rcpt = mailer.send_mail(subject, body)
        print("메일 발송 성공 → 수신자 %d명" % len(rcpt or []))
    except Exception as exc:
        print("메일 발송 실패: %s: %s" % (type(exc).__name__, exc))
        rc = 1
    if m.slack_too:
        try:
            from utils.notify import notify
            notify(subject, "INFO")
            print("Slack 1줄 요청 완료")
        except Exception as exc:
            print("Slack 실패: %s: %s" % (type(exc).__name__, exc))
    return rc


if __name__ == "__main__":
    sys.exit(main())
