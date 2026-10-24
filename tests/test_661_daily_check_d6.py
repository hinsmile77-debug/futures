"""[MW0602 661차 후속5 · D6] 신동 일일 점검 체계 — 수집기 · 장후 종합 메일 · 절 제목 계약.

  C1  수집기: 메일 주소를 가린다 · 중복 줄은 한 번 · settings 값 파싱
  C2  수집기: 실 저장소 2026-10-23 장후 다이제스트가 끝까지 만들어진다(DB 없으면 skip)
  M1  메일: 장후 절이 없으면 「점검 리포트 없음」 폴백 · 신동 리포트만 첨부
  M2  메일: 같은 제목 절이 여럿이면 파일 끝에 가까운 것(자동조치와 같은 규칙)
  M3  메일: 휴장일·이미 보낸 날은 보내지 않는다(send_mail 미호출) · 보내면 마커
  K1  절 제목 계약 — 스킬 문서가 요구하는 제목 = 메일이 찾는 제목
  S1  설정 — 15:40 메일 off · 종합 메일 on
  T1  설치기 ASCII·CRLF
"""
import datetime
import io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "scripts"))

import collect_shindong_evidence as CSE  # noqa: E402
from scripts import shindong_daily_mail as SDM  # noqa: E402


# ── C. 수집기 ────────────────────────────────────────────────────────────────

def test_C1_helpers():
    assert "<메일>" in CSE.tr("[ShindongMail] 발송 완료 → someone@example.com")
    assert "@" not in CSE.tr("a.b+c@naver.com 과 x@y.co.kr")
    hits = [("20261026_SYSTEM.log", "2026-10-26 09:01:00 [INFO] SYSTEM: [X] 같은 줄"),
            ("20261026_WARN.log", "2026-10-26 09:01:00 [WARNING] SYSTEM: [X] 같은 줄")]
    assert len(CSE.dedup(hits)) == 1
    v = CSE.setting_values(ROOT, ("MIREUK_ENGINE", "NO_SUCH_KEY_X"))
    assert v["MIREUK_ENGINE"].strip("'\"") in ("off", "full") and v["NO_SUCH_KEY_X"] == "(없음)"


def test_C2_real_repo_post_digest():
    if not os.path.exists(os.path.join(ROOT, "data", "db", "shindong.db")):
        pytest.skip("이 환경에 shindong.db 없음")
    txt = CSE.build(ROOT, datetime.date(2026, 10, 23), "post", "MW0602", "MW0602 (test)")
    for h in ("## 0. 자동 적신호", "## 1. 설정", "## 2. 로그 계수", "## 4. 신동 거래 — 3원 대사",
              "### 4-1. 케이스 표", "## 5. 장후 마감·작업", "## 6. 미결 관측", "## 7. 오늘 커밋"):
        assert h in txt
    assert "@" not in txt.split("## 7.")[0]          # 메일 주소가 증거에 남지 않는다


# ── M. 장후 종합 메일 ────────────────────────────────────────────────────────

REPORT = u"""# 신동 일일 점검 — MW0602 / 2026-10-26

# 장전(pre)
## 0. 한 줄 결론
장전 결론(이건 메일에 나오면 안 된다)
## 9. 사용자 조치
| 할 일 |
|---|
| 장전 조치(정정됨) |

# 장후(post)
## 0p. 한 줄 결론
장후 결론입니다.
## 2p. Fix 작업 구현계획
F-1 …
## 6p. 다음 거래일 관측
O-1 …
## 9p. 사용자 조치 (초안)
| 할 일 |
|---|
| 앞선 초안 |
## 9p. 사용자 조치 (여기만 보면 됩니다)
| 할 일 |
|---|
| 최종 조치 |
## 장후 자동조치 구현 결과 (17:40 · 자동)
구현 0건.
"""


def _paths(tmp_path, monkeypatch, with_report=True, with_sd=True):
    rd = tmp_path / "rep"
    sd = tmp_path / "sd"
    rd.mkdir()
    sd.mkdir()
    if with_report:
        (rd / "MW0602-20261026-점검리포트.md").write_text(REPORT, encoding="utf-8")
    if with_sd:
        (sd / "신동_일일_MW0602_20261026.md").write_text(u"## 0. 한눈에\n**오늘의 한 줄** — 테스트\n## 1. 차트\n",
                                                     encoding="utf-8")
    monkeypatch.setattr(SDM, "REPORT_DIR", str(rd))
    import config.settings as S
    monkeypatch.setattr(S, "SHINDONG_DAILY_REPORT_DIR", str(sd), raising=False)
    monkeypatch.setattr(SDM, "broker_net", lambda day: (-123456.0, -123400.0))


def test_M1_fallback_without_post_section(tmp_path, monkeypatch):
    _paths(tmp_path, monkeypatch, with_report=False)
    subj, body, files = SDM.build("2026-10-26", "MW0602")
    assert "점검 리포트 없음" in subj and "-123,456원" in subj
    assert len(files) == 1 and files[0].endswith("신동_일일_MW0602_20261026.md")
    assert "Cowork 장후 점검이 돌지 않았거나" in body


def test_M2_sections_use_post_part_and_last_match(tmp_path, monkeypatch):
    _paths(tmp_path, monkeypatch)
    subj, body, files = SDM.build("2026-10-26", "MW0602")
    assert "점검 리포트 없음" not in subj and len(files) == 2
    assert "장후 결론입니다." in body and "장전 결론" not in body
    assert "최종 조치" in body and "앞선 초안" not in body and "장전 조치(정정됨)" not in body
    assert "구현 0건." in body and "O-1" in body


def test_M3_skip_holiday_and_duplicate(tmp_path, monkeypatch):
    _paths(tmp_path, monkeypatch)
    from utils import mailer
    sent = []
    monkeypatch.setattr(mailer, "send_mail", lambda subj, body, att, **k: sent.append(subj) or ["x"])
    monkeypatch.setattr(SDM, "to_attachments", lambda files: list(files))
    monkeypatch.setattr(SDM, "ROOT", str(tmp_path))
    (tmp_path / "data").mkdir()
    assert SDM.main(["--date", "2026-10-25", "--pc", "MW0602"]) == 0 and not sent      # 일요일
    import config.settings as S
    monkeypatch.setattr(S, "SHINDONG_DAILY_MAIL_ENABLED", True, raising=False)
    assert SDM.main(["--date", "2026-10-26", "--pc", "MW0602"]) == 0 and len(sent) == 1
    assert (tmp_path / "data" / "shindong_daily_mail_done_20261026.txt").exists()
    assert SDM.main(["--date", "2026-10-26", "--pc", "MW0602"]) == 0 and len(sent) == 1   # 중복 없음


# ── K. 절 제목 계약 ──────────────────────────────────────────────────────────

def test_K1_heading_contract():
    sk = io.open(os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "SKILL.md"), encoding="utf-8").read()
    src = io.open(os.path.join(ROOT, "scripts", "shindong_daily_mail.py"), encoding="utf-8").read()
    for word in ("한 줄 결론", "사용자 조치", "다음 거래일 관측"):
        assert "`%s`" % word in sk                 # 스킬이 제목으로 요구한다
        assert word in src                         # 메일이 그 제목으로 찾는다
    for word in ("Fix 작업 구현계획", "고도화 방안", "수익률 향상방안"):
        assert "`%s`" % word in sk                 # 자동조치가 찾는 제목
    assert "자동조치" in src                        # 자동조치 절(## 장후 자동조치 구현 결과)


# ── S · T ────────────────────────────────────────────────────────────────────

def test_S1_mail_settings():
    import config.settings as S
    assert S.SHINDONG_REPORT_MAIL_ENABLED is False
    assert S.SHINDONG_DAILY_MAIL_ENABLED is True


def test_T1_installer_ascii_crlf():
    for rel in ("TASK_SHINDONG_MAIL_INSTALL.bat", os.path.join("scripts", "shindong_mail_task.ps1")):
        b = open(os.path.join(ROOT, rel), "rb").read()
        b.decode("ascii")
        assert b"\r\n" in b and b.count(b"\n") == b.count(b"\r\n")
    ps = open(os.path.join(ROOT, "scripts", "shindong_mail_task.ps1"), encoding="ascii").read()
    assert "Shindong_DailyMail_1810" in ps and "shindong_daily_mail.py" in ps and "'18:10'" in ps
