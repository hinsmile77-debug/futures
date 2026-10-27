"""[MW0602 F-SD-3 확장 → Sindong2-V4 이식] 신동 점검 도구의 git 시간 경계를 KST 로 고정.

Cowork 샌드박스 시계가 UTC 라 시간대 없는 `--since="YYYY-MM-DD HH:MM"` 은 9시간 늦게 잡힌다.

  B1  SKILL.md 의 모든 --since 예시에 +0900
  B2  수집기 §7 「오늘 커밋」 --since/--until 이 KST 경계(CE.kst_day_bound)를 쓴다
  B3  CE.kst_day_bound 가 +0900 을 붙인다
  B4  수집기에 맨손 datetime.now() 가 없다(717차 now_kst 유지)
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, ".claude", "skills", "shindong-daily-check")
SRC = os.path.join(SK, "scripts", "collect_shindong_evidence.py")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check", "scripts"))


def _read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def test_B1_skill_since_has_kst_offset():
    sinces = re.findall(r'--since="([^"]+)"', _read(os.path.join(SK, "SKILL.md")))
    assert sinces, "SKILL.md 의 git --since 예시가 사라졌다"
    for s in sinces:
        assert "+0900" in s, s


def test_B2_collector_today_commits_use_kst_bound():
    src = _read(SRC)
    assert '"--since=%s 00:00" %' not in src and '"--until=%s 00:00" %' not in src
    assert '"--since=" + CE.kst_day_bound(' in src
    assert '"--until=" + CE.kst_day_bound(' in src


def test_B3_kst_day_bound_offset():
    import collect_evidence as CE
    assert CE.kst_day_bound("2026-10-27").endswith("+0900")


def test_B4_no_bare_now():
    bare = [ln for ln in _read(SRC).splitlines()
            if re.search(r"datetime\.now\(\s*\)", ln) and not ln.lstrip().startswith("#")
            and "`" not in ln]
    assert bare == [], bare
