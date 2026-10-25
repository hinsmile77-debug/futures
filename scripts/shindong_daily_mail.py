# -*- coding: utf-8 -*-
"""[MW0601 713차 B6] 신동 장후 종합 메일 — 하루 한 통(평일 18:10 예약작업).

원본: MW0602 Sindong-V4 scripts/shindong_daily_mail.py(661차 후속5 D6) — v9 경로(docs/신동거래/일일)로 이식.

왜 있는가
---------
장후 산출이 셋으로 흩어져 있었다 — 15:40 `[ShindongReport]`(기계적 사실, 즉시 메일) · 16:15 Cowork 장후
점검(해석) · 17:23 자동조치(Fix 구현). 메일은 첫 번째만 갔고, 정작 「사용자 조치」와 「무엇을 고쳤나」는
리포트 파일을 열어야 보였다. 이 스크립트가 **맨 끝에** 셋을 한 통으로 묶는다(15:40 메일은 끈다 —
`SHINDONG_REPORT_MAIL_ENABLED=False`).

본문: ① 한 줄 결론 ② 손익(브로커 net 우선) ③ 사용자 조치 ④ 자동조치 결과 ⑤ 신동 리포트 요약
첨부: 장후 점검 리포트 PDF + 신동 일일 리포트 PDF (PDF 실패 시 md 그대로)

폴백(계측 4원칙 ④): 오늘 점검 리포트에 장후 절이 없으면(Cowork 실패·지연) 신동 리포트만으로 보내고
제목에 「점검 리포트 없음」을 붙인다 — 메일이 안 오는 날을 만들지 않는다.
중복 방지: `data/shindong_daily_mail_done_YYYYMMDD.txt` 가 있으면 보내지 않는다(`--force` 로 재발송).
휴장일은 보내지 않는다.

실행:
    python scripts/shindong_daily_mail.py                 # 오늘
    python scripts/shindong_daily_mail.py --date 2026-10-26 --dry-run   # 본문만 출력
예약작업: TASK_SHINDONG_MAIL_INSTALL.bat (평일 18:10)
"""
import argparse
import datetime as _dt
import io
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

REPORT_DIR = os.path.join(ROOT, "docs", "정기점검", "매일점검")
_LOG_DAY = [None]


def _log(msg):
    """화면 + logs/shindong_daily_mail_<날짜>.log — 예약작업은 stdout 이 남지 않는다."""
    print(msg)
    try:
        d = os.path.join(ROOT, "logs")
        os.makedirs(d, exist_ok=True)
        tok = (_LOG_DAY[0] or _dt.date.today().isoformat()).replace("-", "")
        with io.open(os.path.join(d, "shindong_daily_mail_%s.log" % tok), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (_dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
    except Exception:
        pass


def _read(p):
    with io.open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def _plain(s):
    s = re.sub(r"\*\*|`", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s.strip()


def post_part(md):
    """점검 리포트에서 장후 절(`# 장후` 이후)만. 없으면 None."""
    # [MW0601 713차] 미륵 형식 리포트(휴면 전 · 되살림 뒤)의 장후 머리 `## 제3부. 장후` 도 받는다.
    m = re.search(r"^(?:# 장후|## 제3부)[^\n]*$", md, re.M)
    return md[m.start():] if m else None


def section(md, title_rx, max_lines=40):
    """`## …title…` 절 본문(다음 `## ` 전까지). 같은 제목이 여럿이면 **파일 끝에 가장 가까운 것** —
    국면마다 append 되므로 앞의 것은 정정됐을 수 있다(17:23 자동조치와 같은 규칙)."""
    ms = list(re.finditer(r"^##+ [^\n]*(?:%s)[^\n]*$" % title_rx, md, re.M))
    if not ms:
        return None
    m = ms[-1]
    rest = md[m.end():]
    n = re.search(r"^##? ", rest, re.M)
    body = rest[:n.start()] if n else rest
    lines = [l for l in body.strip().splitlines() if l.strip() and not l.startswith("|---")]
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["… (이하 %d줄은 첨부 PDF)" % (len(lines) - max_lines)]
    return _plain("\n".join(lines))


def broker_net(day):
    try:
        from config.settings import TRADES_DB
    except Exception:
        TRADES_DB = os.path.join(ROOT, "data", "db", "trades.db")
    try:
        con = sqlite3.connect("file:%s?mode=ro" % TRADES_DB.replace("\\", "/"), uri=True, timeout=5)
        r = con.execute("SELECT broker_net_krw, pnl_net_krw FROM daily_broker_pnl WHERE date=?", (day,)).fetchone()
        con.close()
        return r
    except Exception:
        return None


def is_trading_day(d):
    if d.weekday() >= 5:
        return False
    try:
        from config.krx_holidays import is_krx_holiday
        return not is_krx_holiday(d)
    except Exception:
        return True


def build(day, pc):
    ymd = day.replace("-", "")
    rp = os.path.join(REPORT_DIR, "%s-%s-점검리포트.md" % (pc, ymd))
    try:
        from config.settings import SHINDONG_DAILY_REPORT_DIR as SDIR
    except Exception:
        SDIR = os.path.join(ROOT, "docs", "신동거래", "일일")
    sp = os.path.join(SDIR, "신동_일일_%s_%s.md" % (pc, ymd))
    post = post_part(_read(rp)) if os.path.exists(rp) else None
    have_sd = os.path.exists(sp)
    bn = broker_net(day)
    pnl = ("실현 %s원" % format(int(bn[0]), ",")) if bn and bn[0] is not None else "실현 미측정"
    tags = []
    if post is None:
        tags.append("점검 리포트 없음")
    if not have_sd:
        tags.append("신동 리포트 없음")
    subject = "[신동][%s] 장후 종합 %s — %s%s" % (pc, day, pnl, (" · " + " · ".join(tags)) if tags else "")
    B = ["[%s] 신동 장후 종합 %s" % (pc, day), ""]
    if post is None:
        B += ["⚠ 오늘 장후 점검 리포트(%s)에 장후 절이 없다 — Cowork 장후 점검이 돌지 않았거나 늦었다." % os.path.basename(rp),
              "  신동 일일 리포트만으로 보낸다. 점검은 수동으로 돌릴 것(「신동 장후 점검」).", ""]
    else:
        one = section(post, r"한 줄 결론", 12)
        if one:
            B += ["■ 한 줄 결론", one, ""]
    B += ["■ 손익", "  브로커 net %s · 엔진 net %s" % (
        format(int(bn[0]), ",") + "원" if bn and bn[0] is not None else "미측정",
        format(int(bn[1]), ",") + "원" if bn and bn[1] is not None else "미측정"), ""]
    if post is not None:
        for title, rx in (("사용자 조치", r"사용자 조치"), ("자동조치 결과", r"자동조치"),
                          ("다음 거래일 관측", r"다음 거래일 관측")):
            s = section(post, rx, 30)
            B += ["■ " + title, s if s else "  (해당 절 없음)", ""]
    if have_sd:
        try:
            from strategy.shindong.report_mail import _summary
            B += ["■ 신동 일일 리포트 요약", _summary(_read(sp)), ""]
        except Exception as e:
            B += ["■ 신동 일일 리포트 요약 — 추출 실패: %s" % e, ""]
    B += ["※ 실거래 계좌 기준. 재생 net 과 실체결 net 은 슬립만큼 다르다 — 판정 전 집계로 규격 변경 근거로 쓰지 말 것.",
          "— 미륵이 %s 자동 발송 (scripts/shindong_daily_mail.py)" % pc]
    files = [p for p in ((rp if post is not None else None), (sp if have_sd else None)) if p]
    return subject, "\n".join(B), files


def to_attachments(files):
    out = []
    try:
        from utils.report_pdf import md_to_pdf
    except Exception:
        md_to_pdf = None
    for p in files:
        try:
            out.append(md_to_pdf(p) if md_to_pdf else p)
        except Exception as e:
            _log("[ShindongDailyMail] PDF 실패 — md 첨부로 대신: %s (%s)" % (os.path.basename(p), e))
            out.append(p)
    return out


def main(argv=None):
    try:
        return _main(argv)
    except Exception as e:
        import traceback
        _log("[ShindongDailyMail] 실패: %r\n%s" % (e, traceback.format_exc()))
        return 1


def _main(argv=None):
    ap = argparse.ArgumentParser(description="신동 장후 종합 메일")
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument("--pc", default=None)
    ap.add_argument("--force", action="store_true", help="휴장일·이미 보낸 날에도 보낸다")
    ap.add_argument("--dry-run", action="store_true", help="보내지 않고 제목·본문·첨부만 출력")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    from config import settings as S
    d = _dt.date.fromisoformat(a.date)
    _LOG_DAY[0] = a.date
    if not a.force and not is_trading_day(d):
        _log("[ShindongDailyMail] 휴장일(%s) — 보내지 않는다" % a.date)
        return 0
    if not a.force and not a.dry_run and not getattr(S, "SHINDONG_DAILY_MAIL_ENABLED", False):
        _log("[ShindongDailyMail] SHINDONG_DAILY_MAIL_ENABLED=False — 보내지 않는다")
        return 0
    pc = a.pc
    if not pc:
        from utils.db_utils import pc_id
        pc = pc_id()
    mk = os.path.join(ROOT, "data", "shindong_daily_mail_done_%s.txt" % a.date.replace("-", ""))
    if os.path.exists(mk) and not a.force and not a.dry_run:
        _log("[ShindongDailyMail] 이미 보냄 — %s (--force 로 재발송)" % mk)
        return 0
    subject, body, files = build(a.date, pc)
    if a.dry_run:
        print(subject)
        print("-" * 60)
        print(body)
        print("-" * 60)
        print("첨부(md): %s" % (", ".join(os.path.basename(f) for f in files) or "없음"))
        return 0
    from utils import mailer
    rcpt = mailer.send_mail(subject, body, to_attachments(files))
    with io.open(mk, "w", encoding="utf-8") as f:
        f.write("sent: %s · 받는 %d명 · %s\n" % (_dt.datetime.now().isoformat(timespec="seconds"), len(rcpt), subject))
    _log("[ShindongDailyMail] 발송 완료 → %d명 · %s" % (len(rcpt), subject))
    return 0


if __name__ == "__main__":
    sys.exit(main())
