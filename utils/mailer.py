# -*- coding: utf-8 -*-
"""[MW0601 632차 후속] SMTP 메일 발송 — 리포트 첨부용.

🔴 자격 정보는 **이 PC 의 환경변수에만** 둔다. 코드·설정·저장소에 쓰지 않는다(저장소는 GitHub 에 올라간다).

| 환경변수 | 뜻 | 필수 |
|---|---|---|
| MIREUK_SMTP_USER     | 보내는 계정(예: xxx@naver.com / xxx@gmail.com) | ✅ |
| MIREUK_SMTP_PASSWORD | 그 계정의 **앱 비밀번호**(로그인 비밀번호 아님)     | ✅ |
| MIREUK_REPORT_MAIL_TO | 받는 주소(쉼표로 여럿)                            | ✅ |
| MIREUK_SMTP_HOST     | 생략 시 계정 도메인으로 추론(naver/gmail/daum)     |    |
| MIREUK_SMTP_PORT     | 생략 시 465(SSL). 587 이면 STARTTLS                 |    |

설정이 빠졌으면 `smtp_config()` 가 None 과 빠진 이름을 돌려준다 — 조용히 건너뛰지 않고 이유를 남긴다
(계측 4원칙 ④). 비밀번호는 로그·예외 메시지에 절대 싣지 않는다.
"""
import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Dict, List, Optional, Sequence, Tuple

_HOSTS = {"naver.com": "smtp.naver.com", "gmail.com": "smtp.gmail.com",
          "daum.net": "smtp.daum.net", "hanmail.net": "smtp.daum.net"}


def smtp_config() -> Tuple[Optional[Dict[str, object]], List[str]]:
    user = os.environ.get("MIREUK_SMTP_USER", "").strip()
    pw = os.environ.get("MIREUK_SMTP_PASSWORD", "")
    to = [x.strip() for x in os.environ.get("MIREUK_REPORT_MAIL_TO", "").split(",") if x.strip()]
    missing = [k for k, v in (("MIREUK_SMTP_USER", user), ("MIREUK_SMTP_PASSWORD", pw),
                              ("MIREUK_REPORT_MAIL_TO", to)) if not v]
    host = os.environ.get("MIREUK_SMTP_HOST", "").strip()
    if not host and user:
        host = _HOSTS.get(user.rsplit("@", 1)[-1].lower(), "")
        if not host:
            missing.append("MIREUK_SMTP_HOST(도메인 추론 불가)")
    if missing:
        return None, missing
    port = int(os.environ.get("MIREUK_SMTP_PORT", "465") or 465)
    return {"user": user, "password": pw, "to": to, "host": host, "port": port}, []


def send_mail(subject: str, body: str, attachments: Sequence[str] = (),
              to: Optional[Sequence[str]] = None, cfg: Optional[Dict[str, object]] = None,
              timeout: float = 30.0) -> List[str]:
    """보내고 받는 사람 목록을 돌려준다. 설정이 없으면 RuntimeError(빠진 이름만 — 값은 싣지 않는다)."""
    if cfg is None:
        cfg, missing = smtp_config()
        if cfg is None:
            raise RuntimeError("SMTP 미설정: " + ", ".join(missing))
    rcpt = list(to or cfg["to"])
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = str(cfg["user"])
    msg["To"] = ", ".join(rcpt)
    msg.set_content(body)
    for p in attachments:
        ctype = mimetypes.guess_type(p)[0] or "application/octet-stream"
        main, sub = ctype.split("/", 1)
        with open(p, "rb") as f:
            msg.add_attachment(f.read(), maintype=main, subtype=sub, filename=os.path.basename(p))
    ctx = ssl.create_default_context()
    if int(cfg["port"]) == 465:
        with smtplib.SMTP_SSL(str(cfg["host"]), 465, context=ctx, timeout=timeout) as s:
            s.login(str(cfg["user"]), str(cfg["password"]))
            s.send_message(msg, to_addrs=rcpt)
    else:
        with smtplib.SMTP(str(cfg["host"]), int(cfg["port"]), timeout=timeout) as s:
            s.starttls(context=ctx)
            s.login(str(cfg["user"]), str(cfg["password"]))
            s.send_message(msg, to_addrs=rcpt)
    return rcpt
