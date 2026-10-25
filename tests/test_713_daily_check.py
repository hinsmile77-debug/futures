"""[MW0601 713차 B1·B6] 신동 일일 점검 체계 — 수집기 · 장후 종합 메일 · 절 제목 계약.

원본: MW0601 Sindong-V4 tests/test_661_daily_check_d6.py — v9(MW0601) 이식 + 추가 단언(C3 · M4 · K2 · K3).

  C1  수집기: 메일 주소를 가린다 · 중복 줄은 한 번 · settings 값 파싱
  C2  수집기: 실 저장소 2026-10-23 장후 다이제스트가 끝까지 만들어진다(DB 없으면 skip)
  M1  메일: 장후 절이 없으면 「점검 리포트 없음」 폴백 · 신동 리포트만 첨부
  M2  메일: 같은 제목 절이 여럿이면 파일 끝에 가까운 것(자동조치와 같은 규칙)
  M3  메일: 휴장일·이미 보낸 날은 보내지 않는다(send_mail 미호출) · 보내면 마커
  K1  절 제목 계약 — 스킬 문서가 요구하는 제목 = 메일이 찾는 제목
  S1  설정 — 15:40 메일 off · 종합 메일 on
  T1  설치기 ASCII·CRLF
  C3  수집기: 휴면 감시 패턴(`[MireukOff]` 0 · `[Engine]` · `[LightPass]`) · 브랜치 기대 `Sindong2-V4` · HealthPolicy 반복 분리
  M4  메일: 휴면 전 미륵 형식 장후 머리(`## 제3부`)도 장후 절로 읽는다
  K2  정본 `mireuk-daily-check` 맨 위에 휴면이면 `shindong-daily-check` 로 가라는 안내
  K3  신동 스킬 C등급 목록에 신동 실집행 경로·엔진/주체 설정
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
    txt = CSE.build(ROOT, datetime.date(2026, 10, 23), "post", "MW0601", "MW0601 (test)")
    for h in ("## 0. 자동 적신호", "## 1. 설정", "## 2. 로그 계수", "## 4. 신동 거래 — 3원 대사",
              "### 4-1. 케이스 표", "## 5. 장후 마감·작업", "## 6. 미결 관측", "## 7. 오늘 커밋"):
        assert h in txt
    # 메일 주소가 증거에 남지 않는다 — v9 신동 진입 로그는 가격을 `@834.22` 로 적으므로 '@' 자체가 아니라 주소 형식을 본다
    import re
    assert not re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", txt.split("## 7.")[0])


# ── M. 장후 종합 메일 ────────────────────────────────────────────────────────

REPORT = u"""# 신동 일일 점검 — MW0601 / 2026-10-26

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
        (rd / "MW0601-20261026-점검리포트.md").write_text(REPORT, encoding="utf-8")
    if with_sd:
        (sd / "신동_일일_MW0601_20261026.md").write_text(u"## 0. 한눈에\n**오늘의 한 줄** — 테스트\n## 1. 차트\n",
                                                     encoding="utf-8")
    monkeypatch.setattr(SDM, "REPORT_DIR", str(rd))
    import config.settings as S
    monkeypatch.setattr(S, "SHINDONG_DAILY_REPORT_DIR", str(sd), raising=False)
    monkeypatch.setattr(SDM, "broker_net", lambda day: (-123456.0, -123400.0))


def test_M1_fallback_without_post_section(tmp_path, monkeypatch):
    _paths(tmp_path, monkeypatch, with_report=False)
    subj, body, files = SDM.build("2026-10-26", "MW0601")
    assert "점검 리포트 없음" in subj and "-123,456원" in subj
    assert len(files) == 1 and files[0].endswith("신동_일일_MW0601_20261026.md")
    assert "Cowork 장후 점검이 돌지 않았거나" in body


def test_M2_sections_use_post_part_and_last_match(tmp_path, monkeypatch):
    _paths(tmp_path, monkeypatch)
    subj, body, files = SDM.build("2026-10-26", "MW0601")
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
    assert SDM.main(["--date", "2026-10-25", "--pc", "MW0601"]) == 0 and not sent      # 일요일
    import config.settings as S
    monkeypatch.setattr(S, "SHINDONG_DAILY_MAIL_ENABLED", True, raising=False)
    assert SDM.main(["--date", "2026-10-26", "--pc", "MW0601"]) == 0 and len(sent) == 1
    assert (tmp_path / "data" / "shindong_daily_mail_done_20261026.txt").exists()
    assert SDM.main(["--date", "2026-10-26", "--pc", "MW0601"]) == 0 and len(sent) == 1   # 중복 없음


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


# ── v9 추가 ──────────────────────────────────────────────────────────────────

def test_C3_dormant_watch_patterns():
    labels = " ".join(p[0] + p[1] for p in CSE.COUNT_PATTERNS)
    for frag in (r"\[MireukOff\]", r"\[Engine\] 미륵 엔진=off", r"\[LightPass\] 경량 ATR", r"\[EarlyWarmup\] 미륵 휴면"):
        assert frag in labels, frag
    mo = [p for p in CSE.COUNT_PATTERNS if "MireukOff" in p[1]][0]
    assert mo[2] == "0"                               # 1건이라도 있으면 이상
    assert CSE.EXPECT_BRANCH == "Sindong2-V4"
    assert any("DailyClose" in p[1] and p[2] == "1+" for p in CSE.POST_PATTERNS)
    src = io.open(os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "scripts",
                               "collect_shindong_evidence.py"), encoding="utf-8").read()
    assert "[Health] level=CRITICAL" in src           # 반복 줄을 따로 센다


def test_M4_mireuk_format_post_heading():
    md = u"""# 미륵이 일일 점검 — MW0601
## 제1부. 장전
## 사용자 조치
장전
## 제3부. 장후
## 사용자 조치
장후 조치
"""
    post = SDM.post_part(md)
    assert post is not None and post.startswith(u"## 제3부")
    assert u"장후 조치" in SDM.section(post, u"사용자 조치")


def test_K2_mireuk_skill_points_to_shindong_when_dormant():
    sk = io.open(os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check", "SKILL.md"), encoding="utf-8").read()
    head = sk[:2500]
    assert 'MIREUK_ENGINE="off"' in head and "shindong-daily-check" in head


def test_K3_shindong_skill_c_grade_and_branch():
    sk = io.open(os.path.join(ROOT, ".claude", "skills", "shindong-daily-check", "SKILL.md"), encoding="utf-8").read()
    i = sk.index("**C 로 쓸 것**")
    blk = sk[i:i + 900]
    for frag in ("live_legs.py", "spec.py", "_shindong_*", "MIREUK_ENGINE", "PRINCIPAL_*", "SHINDONG_*"):
        assert frag in blk, frag
    assert "`Sindong2-V4`" in sk and "SD-2026-10-21-v3" in sk
    assert "배포 첫날" in sk                           # 장중은 배포 첫날만(B3)
