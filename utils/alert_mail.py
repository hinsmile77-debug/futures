# -*- coding: utf-8 -*-
"""[MW0602 2026-10-17] 긴급 이상 알림 메일 — `[긴급이상]` / `[이상해소]` (F-1009 형식 통일).

근거: docs/정기점검/매일점검/MW0602-20261017-긴급알림메일-종합검토.md
계기: 2026-10-15 실계좌 청산 거부 113분 동안 사람에게 닿은 알림이 0건이었다.

설계(사용자 결정 2026-10-17)
  · 사건 코드 = 등급 머리글자 + 번호 — S(실계좌 손실·오버나이트 위험) · A(즉시 인지) · B(다음 거래일 위험)
  · 사건 1회(에피소드)당 `[긴급이상]` 1통 + 해소 시 `[이상해소]` 1통. 반복 주기에는 다시 보내지 않는다
  · 에피소드 상태를 `data/alert_mail/<날짜>.json` 에 저장 — 재기동해도 같은 사건을 다시 보내지 않는다
  · 일회성 통지(`notice`)는 (코드, 키)당 하루 1통
  · 하루 상한(기본 30통). 넘으면 「상한 도달」 1통만 보내고 그 뒤는 로그만 남긴다
  · 메일과 Slack 을 **둘 다** 보낸다. 메일이 실패하면 Slack 에 실패 사실을 한 줄 더 남긴다
  · 수신자 = `utils/mailer.py` 환경변수(신동 일일리포트와 같은 주소). 대시보드 [메일] 체크가
    꺼져 있으면 mailer 가 `MailDisabled` 를 낸다 — 실패가 아니라 「꺼짐」으로 기록한다
  · 테스트 실행(`is_test_mode()`)에서는 실제로 보내지 않는다(`configure(sender=…)` 로 주입하면 그것만 쓴다)

스레드: SMTP 는 최대 30초 막힐 수 있다 — 메일마다 별도 스레드로 보낸다(Qt 메인 스레드·COM 콜백을
막지 않는다, 절대원칙 §4). 상태 갱신은 호출 스레드에서 잠금 아래 끝낸다.
⚠ **판정·차단·주문 경로와 무관한 알림 전용 모듈이다.** 어떤 예외도 호출부로 내보내지 않는다.

발송 주체
  · main.py          — S-01·S-02·S-03·S-06·S-07 · A-01~A-04 · B-02~B-04
  · freeze_sentinel  — S-04(동결 · F-1009) · S-05(장전 미기동)  ← main 이 죽었거나 안 떴으면 main 은 못 보낸다
  · retrain_eod      — B-01(EOD 재학습 실패)
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import threading
from typing import Callable, Dict, List, Optional, Sequence

logger = logging.getLogger("SYSTEM")

TAG_ALERT = "[긴급이상]"
TAG_RESOLVE = "[이상해소]"

# 코드 → (제목, 할 일). 제목은 메일 제목 앞부분, 할 일은 본문 체크리스트.
CATALOG: Dict[str, tuple] = {
    "S-01": ("청산 주문 거부·미체결", [
        "HTS 에서 해당 포지션을 **지정가**로 직접 청산 (가격제한 확대일엔 시장가가 거부된다)",
        "청산 뒤 [이상해소] 메일이 오는지 확인",
    ]),
    "S-02": ("15:10 강제청산 실패 — 오버나이트 위험", [
        "HTS 에서 보유 포지션을 즉시 확인하고 지정가로 청산",
        "15:45 장 마감 전까지 FLAT 확인",
    ]),
    "S-03": ("포지션 불일치·외부/미추적 체결", [
        "HTS 잔고와 미륵이 화면의 포지션(방향·수량·평단)을 대조",
        "미륵이가 모르는 포지션이면 HTS 에서 정리하거나 미륵이 재시작으로 동기화",
    ]),
    "S-04": ("미륵이 동결·비정상 종료", [
        "트레이딩 PC 화면 — 미륵이 창이 응답하는지",
        "HTS — 보유 포지션 확인 (동결 중에는 손절·15:10 강제청산이 돌지 않는다)",
        "응답이 없으면 미륵이를 재시작",
    ]),
    "S-05": ("장전 미기동·기동 실패", [
        "트레이딩 PC 에서 미륵이가 떠 있는지 확인",
        "기동 실패 사유(계좌 만료 preflight · Cybos 로그인 · 관리자 권한) 확인 후 재기동",
    ]),
    "S-06": ("브로커 연결 끊김", [
        "Cybos/CREON 로그인 상태 확인",
        "HTS 에서 보유 포지션 확인 (끊긴 동안 청산 주문이 나가지 않는다)",
    ]),
    # [MW0602 2026-10-24] 거부가 없어 S-01 이 안 뜨는 미청산(주문 미송신 · 미결 고착 · 경로 누락)까지 잡는다.
    #   주체·원인과 무관하게 「실시간가가 손절선 밖에 일정 시간 머무는데 포지션이 열려 있다」 하나로 판정.
    "S-07": ("손절선 통과 뒤 미청산", [
        "HTS 에서 해당 포지션을 **지정가**로 직접 청산 (상대 최우선 호가 근처)",
        "미륵이 화면 — 미결 주문이 걸려 있는지 · 청산 거부(S-01) 메일이 함께 왔는지",
        "청산 뒤 [이상해소] 메일이 오는지 확인",
    ]),
    "A-01": ("거래소 서킷브레이커(CB) 발동", [
        "보유 포지션이 있으면 재개 직후 HTS 에서 **지정가**로 정리 검토 (재개 후 가격제한폭 확대 → 시장가 거부 가능)",
        "재개 후 10분은 미륵·신동·피터 신규 진입이 차단된다",
    ]),
    "A-02": ("가격제한폭 확대 — 시장가 불가 구간", [
        "오늘 남은 청산은 지정가로 나간다(자동). 미체결이 이어지면 HTS 에서 직접 청산",
        "15:10 강제청산이 체결되는지 확인",
    ]),
    "A-03": ("미륵 서킷브레이커 발동", [
        "발동 트리거(정확도·연속손절·지연 등)와 포지션 상태 확인",
    ]),
    "A-04": ("큰 손실", [
        "해당 거래의 진입·청산 사유 확인",
        "당일 추가 진입을 멈출지 판단",
    ]),
    "B-01": ("EOD 재학습 실패", [
        "logs/retrain_eod_<날짜>.log 확인",
        "다음 거래일 장전 전에 수동 재학습(EOD_RETRAIN.bat, py310_64) — 모델 미교체가 CB③ 정지로 이어질 수 있다",
    ]),
    "B-02": ("주문가능수량 조회 실패 지속", [
        "증거금 상한(MarginCap)이 측정되지 않았다 — CpTd6722 입력 규격(실계좌) 확인",
    ]),
    "B-03": ("데이터 결손·맥점 전일 제외", [
        "분봉 결손 구간과 원인(재기동·연결) 확인",
        "맥점 전일 제외면 그날 08:50 맥점은 하루 낡은 값이다",
    ]),
    "B-04": ("실거래 설정 상태 이상", [
        "서버(실서버/모의) · 자동주문 잠금 · 거래주체 설정이 의도와 같은지 확인",
    ]),
}

SEVERITY = {"S": "S등급 — 실계좌 손실·오버나이트 위험", "A": "A등급 — 즉시 인지 필요",
            "B": "B등급 — 다음 거래일 운영 위험"}


def _default_state_dir() -> str:
    # 🔴 테스트가 경보 경로를 태우면 실제 상태 파일에 「S-01 열림」이 남아 그날 진짜 사건이
    #   「이미 보냄」으로 억제된다 — 테스트 모드는 임시 폴더를 쓴다.
    if _test_mode():
        import tempfile
        return os.path.join(tempfile.gettempdir(), "mireuk_alert_mail_test")
    try:
        from config.settings import DATA_DIR
        return os.path.join(DATA_DIR, "alert_mail")
    except Exception:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "alert_mail")


def _default_pc() -> str:
    try:
        from utils.db_utils import pc_id
        return pc_id()
    except Exception:
        return os.environ.get("COMPUTERNAME", "PC")


def _cfg(name, default):
    try:
        import config.settings as st
        return getattr(st, name, default)
    except Exception:
        return default


def _test_mode() -> bool:
    try:
        from utils.runtime_mode import is_test_mode
        return bool(is_test_mode())
    except Exception:
        return False


class AlertMailer(object):
    """에피소드·일회성 통지·상한·영속 상태를 관리한다. 모든 공개 메서드는 예외를 내보내지 않는다."""

    def __init__(self, state_dir: Optional[str] = None, pc: Optional[str] = None,
                 sender: Optional[Callable[[str, str], Sequence[str]]] = None,
                 slack: Optional[Callable[[str, str], None]] = None,
                 daily_cap: Optional[int] = None, enabled: Optional[bool] = None,
                 clock: Optional[Callable[[], datetime.datetime]] = None, threaded: bool = True,
                 proc: str = "main"):
        self.state_dir = state_dir or _default_state_dir()
        # 프로세스별 상태 파일 — main·센티넬·재학습이 같은 파일을 각자 메모리에 들고 덮어쓰면
        #   서로의 기록을 지운다(마지막 저장이 이긴다). 그래서 `<날짜>_<proc>.json` 으로 나눈다.
        self.proc = str(proc or "main")
        self.pc = pc or _default_pc()
        self._sender = sender
        self._slack = slack
        self.daily_cap = int(daily_cap if daily_cap is not None else _cfg("ALERT_MAIL_DAILY_CAP", 30))
        self.enabled = bool(enabled if enabled is not None else _cfg("ALERT_MAIL_ENABLED", True))
        self.slack_too = bool(_cfg("ALERT_MAIL_SLACK_TOO", True))
        self._clock = clock or datetime.datetime.now
        self._threaded = threaded
        self._lock = threading.RLock()
        self._send_lock = threading.Lock()
        self._day = None
        self._state = None
        self.sent_log: List[tuple] = []        # (제목, 결과) — 테스트·진단용

    # ── 상태 ──────────────────────────────────────────────────────────
    def _path(self, day: str) -> str:
        return os.path.join(self.state_dir, "%s_%s.json" % (day, self.proc))

    def _load(self) -> dict:
        day = self._clock().date().isoformat()
        if self._day == day and self._state is not None:
            return self._state
        st = {"open": {}, "oneshot": [], "sent": 0, "cap_notified": False, "history": []}
        try:
            with open(self._path(day), "r", encoding="utf-8") as f:
                st.update(json.load(f))
        except FileNotFoundError:
            pass
        except Exception as exc:
            logger.warning("[AlertMail] 상태 파일 읽기 실패 — 새로 시작: %s", exc)
        self._day, self._state = day, st
        return st

    def _save(self) -> None:
        try:
            os.makedirs(self.state_dir, exist_ok=True)
            tmp = self._path(self._day) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._state, f, ensure_ascii=False, indent=1)
            os.replace(tmp, self._path(self._day))
        except Exception as exc:
            logger.warning("[AlertMail] 상태 파일 저장 실패 (무해): %s", exc)

    @staticmethod
    def _key(code: str, key: str) -> str:
        return "%s|%s" % (code, key or "")

    def happened_today(self, code: str) -> bool:
        """오늘 이 코드가 한 번이라도 발생(경보·통지)했는가 — 해소된 것도 포함."""
        try:
            with self._lock:
                return code in self._load().get("history", [])
        except Exception:
            return False

    def is_open(self, code: str, key: str = "") -> bool:
        try:
            with self._lock:
                return self._key(code, key) in self._load()["open"]
        except Exception:
            return False

    # ── 형식 ──────────────────────────────────────────────────────────
    def build_alert(self, code: str, summary: str, details: Optional[Sequence[str]] = None,
                    context: Optional[Dict[str, str]] = None, now=None):
        now = now or self._clock()
        title, todo = CATALOG.get(code, (code, []))
        subject = "%s[%s][%s] %s — %s" % (TAG_ALERT, self.pc, code, title, summary)
        ctx = context or {}
        lines = ["발생 %s · PC %s · %s" % (now.strftime("%Y-%m-%d %H:%M:%S"), self.pc,
                                          SEVERITY.get(code[:1], code))]
        lines.append("서버 %s" % ctx.get("server", "미측정"))
        lines.append("포지션 %s" % ctx.get("position", "미측정"))
        lines += ["", "사건", "  " + str(summary)]
        lines += ["  · " + str(d) for d in (details or [])]
        if todo:
            lines += ["", "할 일"] + ["  %d. %s" % (i + 1, t) for i, t in enumerate(todo)]
        lines += ["", "— 미륵이 %s 자동 발송(%s). 같은 사건으로는 다시 보내지 않고, 해소되면 %s 메일을 보냅니다."
                  % (self.pc, code, TAG_RESOLVE)]
        return subject, "\n".join(lines)

    def build_resolve(self, code: str, opened_at: Optional[str], note: str = "", now=None):
        now = now or self._clock()
        title = CATALOG.get(code, (code, []))[0]
        dur = ""
        if opened_at:
            try:
                sec = (now - datetime.datetime.fromisoformat(opened_at)).total_seconds()
                dur = " — 지속 %d분" % max(0, int(round(sec / 60.0)))
            except Exception:
                dur = ""
        subject = "%s[%s][%s] %s 해소%s" % (TAG_RESOLVE, self.pc, code, title, dur)
        body = "\n".join([
            "%s · PC %s · %s 해소%s" % (now.strftime("%Y-%m-%d %H:%M:%S"), self.pc, code, dur),
            ("사유 " + note) if note else "",
            "발생 동안 놓친 손절·청산이 없었는지 HTS 의 포지션과 체결 내역을 확인하세요.",
            "",
            "— 미륵이 %s 자동 발송(%s)." % (self.pc, code),
        ])
        return subject, body

    # ── 공개 API ──────────────────────────────────────────────────────
    def raise_alert(self, code: str, summary: str, details: Optional[Sequence[str]] = None,
                    key: str = "", context: Optional[Dict[str, str]] = None) -> bool:
        """에피소드 시작. 이미 열려 있으면 False(다시 보내지 않는다)."""
        try:
            with self._lock:
                st = self._load()
                k = self._key(code, key)
                if k in st["open"]:
                    return False
                now = self._clock()
                st["open"][k] = {"at": now.isoformat(timespec="seconds"), "summary": str(summary)[:200]}
                st.setdefault("history", []).append(code)
                self._save()
            subject, body = self.build_alert(code, summary, details, context, now)
            self._dispatch(subject, body, level="CRITICAL" if code[:1] == "S" else "WARNING")
            return True
        except Exception as exc:
            logger.warning("[AlertMail] raise 실패 (무해) %s: %s", code, exc)
            return False

    def resolve(self, code: str, key: str = "", note: str = "") -> bool:
        """에피소드 종료. 열려 있지 않으면 False."""
        try:
            with self._lock:
                st = self._load()
                k = self._key(code, key)
                ep = st["open"].pop(k, None)
                if ep is None:
                    return False
                self._save()
            subject, body = self.build_resolve(code, ep.get("at"), note)
            self._dispatch(subject, body, level="WARNING")
            return True
        except Exception as exc:
            logger.warning("[AlertMail] resolve 실패 (무해) %s: %s", code, exc)
            return False

    def notice(self, code: str, summary: str, details: Optional[Sequence[str]] = None,
               key: str = "", context: Optional[Dict[str, str]] = None) -> bool:
        """일회성 통지 — (코드, 키)당 하루 1통. 해소 메일 없음."""
        try:
            with self._lock:
                st = self._load()
                k = self._key(code, key)
                if k in st["oneshot"]:
                    return False
                st["oneshot"].append(k)
                st.setdefault("history", []).append(code)
                self._save()
            subject, body = self.build_alert(code, summary, details, context)
            body = body.replace("해소되면 %s 메일을 보냅니다." % TAG_RESOLVE, "일회성 통지입니다.")
            self._dispatch(subject, body, level="CRITICAL" if code[:1] == "S" else "WARNING")
            return True
        except Exception as exc:
            logger.warning("[AlertMail] notice 실패 (무해) %s: %s", code, exc)
            return False

    # ── 발송 ──────────────────────────────────────────────────────────
    def _dispatch(self, subject: str, body: str, level: str) -> None:
        if not self.enabled:
            logger.info("[AlertMail] 비활성(ALERT_MAIL_ENABLED=False) — 생략 | %s", subject)
            self.sent_log.append((subject, "disabled"))
            return
        with self._lock:
            st = self._load()
            if st["sent"] >= self.daily_cap:
                if not st["cap_notified"]:
                    st["cap_notified"] = True
                    self._save()
                    cap_subj = "%s[%s][CAP] 하루 알림 상한 %d통 도달 — 이후는 로그만 남깁니다" % (
                        TAG_ALERT, self.pc, self.daily_cap)
                    self._send_now(cap_subj, "마지막으로 억제된 알림: " + subject, "CRITICAL")
                logger.warning("[AlertMail] 하루 상한 %d통 초과 — 메일 생략 | %s", self.daily_cap, subject)
                self.sent_log.append((subject, "capped"))
                return
            st["sent"] += 1
            self._save()
        self._send_now(subject, body, level)

    def _send_now(self, subject: str, body: str, level: str) -> None:
        if self.slack_too:
            self._slack_send(subject, body, level)
        if self._sender is None and _test_mode():
            logger.info("[AlertMail] 테스트 모드 — 메일 발송 생략 | %s", subject)
            self.sent_log.append((subject, "test_mode"))
            return
        if self._threaded:
            th = threading.Thread(target=self._mail_worker, args=(subject, body), name="AlertMail")
            th.daemon = False     # 프로세스가 끝나도 보내던 메일은 마저 보낸다
            th.start()
        else:
            self._mail_worker(subject, body)

    def _mail_worker(self, subject: str, body: str) -> None:
        with self._send_lock:
            try:
                if self._sender is not None:
                    rcpt = self._sender(subject, body)
                else:
                    from utils import mailer
                    rcpt = mailer.send_mail(subject, body)
                logger.info("[AlertMail] 메일 발송 성공 → %d명 | %s", len(rcpt or []), subject)
                self.sent_log.append((subject, "sent"))
            except Exception as exc:
                disabled = type(exc).__name__ == "MailDisabled"
                logger.warning("[AlertMail] 메일 %s(%s: %s) | %s",
                               "꺼짐" if disabled else "발송 실패", type(exc).__name__, exc, subject)
                self.sent_log.append((subject, "disabled_ui" if disabled else "failed"))
                if not disabled:
                    self._slack_send("[AlertMail] 메일 발송 실패 — " + subject, str(exc)[:200], "WARNING")

    def _slack_send(self, subject: str, body: str, level: str) -> None:
        try:
            first = [ln for ln in body.split("\n") if ln.strip()][:4]
            msg = subject + ("\n" + "\n".join(first) if first else "")
            if self._slack is not None:
                self._slack(msg, level)
                return
            from utils.notify import notify
            notify(msg, level)
        except Exception as exc:
            logger.warning("[AlertMail] Slack 발송 실패 (무해): %s", exc)


# ── 모듈 단일 인스턴스 ──────────────────────────────────────────────────
_INSTANCE: Optional[AlertMailer] = None
_INST_LOCK = threading.Lock()


def get_mailer() -> AlertMailer:
    global _INSTANCE
    with _INST_LOCK:
        if _INSTANCE is None:
            _INSTANCE = AlertMailer()
        return _INSTANCE


def configure(**kw) -> AlertMailer:
    """테스트·특수 프로세스용 — 새 인스턴스로 바꾼다."""
    global _INSTANCE
    with _INST_LOCK:
        _INSTANCE = AlertMailer(**kw)
        return _INSTANCE


def status_line(mailer: Optional[AlertMailer] = None) -> str:
    """기동 로그용 한 줄 — ON/OFF · 수신자 수 · 미설정 사유 · 상한 · Slack 병행(계측 4원칙 ④).

    수신자 **주소는 적지 않는다** — 로그가 공유될 수 있어 개수만 남긴다.
    """
    m = mailer or get_mailer()
    try:
        if not m.enabled:
            state = "OFF(ALERT_MAIL_ENABLED=False)"
        elif _test_mode() and m._sender is None:
            state = "OFF(테스트 모드)"
        else:
            from utils import mailer as _ml
            cfg, missing = _ml.smtp_config()
            if not cfg:
                state = "OFF(SMTP 미설정: %s)" % ", ".join(missing)
            elif not _ml.mail_enabled():
                state = "OFF(대시보드 [메일] 꺼짐)"
            else:
                state = "ON → 수신자 %d명" % len(cfg.get("to") or [])
    except Exception as exc:
        state = "미측정(%s)" % type(exc).__name__
    return "[AlertMail] 긴급 알림 메일 %s · 하루 상한 %d통 · Slack 병행 %s · PC %s" % (
        state, m.daily_cap, "ON" if m.slack_too else "OFF", m.pc)


def raise_alert(code, summary, details=None, key="", context=None) -> bool:
    return get_mailer().raise_alert(code, summary, details, key, context)


def resolve(code, key="", note="") -> bool:
    return get_mailer().resolve(code, key, note)


def notice(code, summary, details=None, key="", context=None) -> bool:
    return get_mailer().notice(code, summary, details, key, context)


def is_open(code, key="") -> bool:
    return get_mailer().is_open(code, key)


def happened_today(code) -> bool:
    return get_mailer().happened_today(code)
