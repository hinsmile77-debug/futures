# -*- coding: utf-8 -*-
"""[MW0602 2026-10-17] utils/alert_mail.py — 긴급 이상 알림 메일 공통 모듈.

고정하는 불변식
  · 제목 `[긴급이상][PC][코드] 제목 — 요약` / `[이상해소][PC][코드] 제목 해소 — 지속 N분`
  · 에피소드 1회당 경보 1통 · 해소 1통 · 열린 동안 반복 발송 없음 · 해소 뒤 재발은 다시 1통
  · 상태 파일 영속 — 새 인스턴스(재기동)도 같은 에피소드를 다시 보내지 않는다
  · 일회성 통지는 (코드, 키)당 하루 1통
  · 하루 상한 — 넘으면 「상한 도달」 1통 후 생략
  · 메일과 Slack 둘 다 · 메일 실패 시 Slack 에 실패 한 줄 · [메일] 꺼짐은 실패로 세지 않는다
  · 본문에 서버·포지션·할 일
  · 테스트 모드에서 주입 없으면 실제 발송 없음
  · 카탈로그 코드는 S/A/B 머리글자
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

from utils import alert_mail as AM  # noqa: E402


class _Clock(object):
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def _mk(tmp_path, clock=None, cap=30, sender_raises=None):
    mails, slacks = [], []

    def sender(subj, body):
        if sender_raises is not None:
            raise sender_raises
        mails.append((subj, body))
        return ["x@y"]

    m = AM.AlertMailer(state_dir=str(tmp_path), pc="MW0602", sender=sender,
                       slack=lambda msg, lv: slacks.append((msg, lv)), daily_cap=cap, enabled=True,
                       clock=clock or _Clock(datetime.datetime(2026, 10, 15, 10, 24, 43)), threaded=False)
    return m, mails, slacks


def test_catalog_codes_use_grade_prefix():
    assert AM.CATALOG and all(c[:1] in "SAB" and c[1] == "-" for c in AM.CATALOG)
    for c in ("S-01", "S-02", "S-03", "S-04", "S-05", "S-06", "A-01", "A-02", "A-03", "A-04",
              "B-01", "B-02", "B-03", "B-04"):
        assert c in AM.CATALOG, c


def test_episode_one_alert_one_resolve(tmp_path):
    clk = _Clock(datetime.datetime(2026, 10, 15, 10, 24, 43))
    m, mails, slacks = _mk(tmp_path, clk)
    ctx = {"server": "Cybos 실서버(실계좌)", "position": "SHORT 1계약 @869.70"}
    assert m.raise_alert("S-01", "SHORT 1계약 미청산", ["주문 549 거부 0707"], context=ctx)
    assert not m.raise_alert("S-01", "또"), "열린 동안 반복 발송 없음"
    assert m.is_open("S-01")
    subj, body = mails[0]
    assert subj == "[긴급이상][MW0602][S-01] 청산 주문 거부·미체결 — SHORT 1계약 미청산"
    assert "Cybos 실서버(실계좌)" in body and "SHORT 1계약 @869.70" in body and "할 일" in body
    clk.t = clk.t + datetime.timedelta(minutes=113)
    assert m.resolve("S-01", note="청산 체결")
    assert mails[1][0] == "[이상해소][MW0602][S-01] 청산 주문 거부·미체결 해소 — 지속 113분"
    assert not m.resolve("S-01"), "닫힌 에피소드는 다시 해소 메일을 보내지 않는다"
    assert len(slacks) == 2, "메일과 Slack 둘 다"
    assert m.raise_alert("S-01", "재발"), "해소 뒤 재발은 다시 1통"


def test_state_persists_across_restart(tmp_path):
    m, mails, _ = _mk(tmp_path)
    m.raise_alert("A-01", "12:42 거래 중단")
    m2, mails2, _ = _mk(tmp_path)                 # 재기동
    assert not m2.raise_alert("A-01", "12:42 거래 중단"), "재기동해도 같은 사건을 다시 보내지 않는다"
    assert m2.resolve("A-01")
    assert len(mails) == 1 and len(mails2) == 1


def test_keys_separate_episodes(tmp_path):
    m, mails, _ = _mk(tmp_path)
    assert m.raise_alert("S-03", "외부 체결", key="order:1002")
    assert m.raise_alert("S-03", "외부 체결", key="order:1003")
    assert len(mails) == 2


def test_notice_once_per_day(tmp_path):
    clk = _Clock(datetime.datetime(2026, 10, 15, 15, 46))
    m, mails, _ = _mk(tmp_path, clk)
    assert m.notice("B-03", "영구 결손 9봉", key="bargap")
    assert not m.notice("B-03", "영구 결손 9봉", key="bargap")
    assert "일회성 통지" in mails[0][1] and "[이상해소] 메일을 보냅니다" not in mails[0][1]
    clk.t = clk.t + datetime.timedelta(days=1)
    assert m.notice("B-03", "다음 날", key="bargap"), "날이 바뀌면 다시"


def test_daily_cap(tmp_path):
    m, mails, _ = _mk(tmp_path, cap=3)
    for i in range(6):
        m.notice("A-04", "손실 %d" % i, key=str(i))
    subjects = [s for s, _ in mails]
    assert len(subjects) == 4, subjects
    assert "[CAP]" in subjects[-1] and sum("[CAP]" in s for s in subjects) == 1


def test_mail_failure_falls_back_to_slack(tmp_path):
    m, mails, slacks = _mk(tmp_path, sender_raises=OSError("smtp down"))
    m.raise_alert("S-06", "60초 끊김")
    assert any("메일 발송 실패" in s for s, _ in slacks), slacks
    assert m.sent_log[-1][1] == "failed"


def test_mail_disabled_is_not_failure(tmp_path):
    class MailDisabled(RuntimeError):
        pass
    m, mails, slacks = _mk(tmp_path, sender_raises=MailDisabled("off"))
    m.raise_alert("S-06", "60초 끊김")
    assert m.sent_log[-1][1] == "disabled_ui"
    assert not any("메일 발송 실패" in s for s, _ in slacks), "[메일] 꺼짐은 실패로 알리지 않는다"


def test_test_mode_without_injection_sends_nothing(tmp_path):
    m = AM.AlertMailer(state_dir=str(tmp_path), pc="MW0602", slack=lambda *a: None,
                       enabled=True, threaded=False)
    m.raise_alert("S-02", "15:12 SHORT 1계약 잔존")
    assert m.sent_log[-1][1] == "test_mode"


def test_never_raises(tmp_path):
    m = AM.AlertMailer(state_dir=str(tmp_path / "x"), pc="P", sender=lambda s, b: 1 / 0,
                       slack=lambda *a: 1 / 0, enabled=True, threaded=False)
    assert m.raise_alert("S-01", "x") in (True, False)
    assert m.notice("B-01", "x") in (True, False)
    assert m.resolve("S-01") in (True, False)
