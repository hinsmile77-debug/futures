"""[MW0602 666차 후속 · F-SD-2 / F-SD-3] 신동 일일 점검 도구의 「오늘」을 KST 로 고정.

Cowork 샌드박스 시계가 UTC 라 KST 00:00~09:00 세션(장전 08:51 포함)이 전일을 오늘로 오판했다.

  K1  --date 생략 시 날짜는 KST 기준이다(UTC 23:51 = KST 다음날 08:51)
  K2  수집기 안에 맨손 datetime.now() 가 남아 있지 않다(전부 _now_kst 경유)
  K3  SKILL.md 「배포 첫날」 판정 git 명령의 --since 에 +0900 이 붙어 있다
  K4  KST 는 고정 +9 (DST 없음) — py37 호환(zoneinfo 미사용)
"""
import datetime
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, ".claude", "skills", "shindong-daily-check")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(SK, "scripts"))

import collect_shindong_evidence as CSE  # noqa: E402

SRC = os.path.join(SK, "scripts", "collect_shindong_evidence.py")


class _FakeDT(datetime.datetime):
    """UTC 2026-10-26 23:51 에 멈춘 시계 — KST 로는 10-27 08:51(장전)."""
    @classmethod
    def now(cls, tz=None):
        base = datetime.datetime(2026, 10, 26, 23, 51, tzinfo=datetime.timezone.utc)
        if tz is None:
            return base.replace(tzinfo=None)      # 샌드박스 = UTC 시계
        return base.astimezone(tz)


def test_K1_default_day_is_kst(monkeypatch):
    monkeypatch.setattr(CSE, "datetime", _FakeDT)
    assert CSE._now_kst().date() == datetime.date(2026, 10, 27)
    assert CSE._now_kst().strftime("%H:%M") == "08:51"
    # 대조: 고치기 전 방식은 전일을 낸다
    assert _FakeDT.now().date() == datetime.date(2026, 10, 26)


def test_K2_no_bare_now_in_collector():
    with io.open(SRC, encoding="utf-8") as f:
        src = f.read()
    bare = [ln for ln in src.splitlines()
            if re.search(r"datetime\.now\(\s*\)", ln) and not ln.lstrip().startswith("#")]
    assert bare == [], bare


def test_K3_skill_since_has_kst_offset():
    with io.open(os.path.join(SK, "SKILL.md"), encoding="utf-8") as f:
        md = f.read()
    sinces = re.findall(r'--since="([^"]+)"', md)
    assert sinces, "배포 첫날 판정 명령이 사라졌다"
    for s in sinces:
        assert "+0900" in s, s


def test_K4_kst_fixed_offset():
    assert CSE.KST.utcoffset(None) == datetime.timedelta(hours=9)
    with io.open(SRC, encoding="utf-8") as f:
        assert "zoneinfo" not in f.read().replace("zoneinfo 는", "")
