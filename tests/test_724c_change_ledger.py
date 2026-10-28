# -*- coding: utf-8 -*-
"""[MW0601 724차 후속3] 신동 점검 §3-V 변경 반영 검증 — 수집기 대장(§8) 회귀.

목적: 바꾼 것이 실제로 반영됐는지 그날 닫는 루틴(2026-10-28 사용자 지시). 수집기가
① 커밋을 경로로 구분하고 ② 앞 리포트의 **마지막** 「변경 반영 검증」 절에서 닫히지 않은 행만 이월한다.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".claude", "skills", "shindong-daily-check", "scripts"))
import collect_shindong_evidence as M  # noqa: E402


def test_1_kind_order_and_docs_only():
    assert M._ledger_kind(["docs/a.md", "dev_memory/NEXT_TODO.md"]) == ["문서·산출물"]
    assert M._ledger_kind(["tools/maekjeom_ladder/ladder.html"]) == ["도구·화면·점검"]
    assert M._ledger_kind(["docs/x.md", "main.py", "tests/t.py"]) == ["실행경로", "도구·화면·점검", "문서·산출물"]
    assert M._ledger_kind(["README.txt"]) == ["기타"]


def test_2_open_rows_last_section_only(tmp_path):
    p = tmp_path / "r.md"
    io.open(str(p), "w", encoding="utf-8").write(u"\n".join([
        u"# 장전(pre)",
        u"## 0-V. 변경 반영 검증",
        u"| V | 커밋 | 무엇 | 기대 | 국면 | 판정 | 근거 |",
        u"| V-1028-1 | abc | x | y | 장후 | 🔄 | - |",
        u"# 장후(post)",
        u"## 0p-V. 변경 반영 검증",
        u"| V-1028-1 | abc | x | y | 장후 | ✅ | 로그 15:41 |",
        u"| V-1028-2 | def | x | y | 장중 | ⏳ 표본 없음 | - |",
        u"| V-1028-3 | ghi | x | y | 장후 | ❌ 미반영 | 로그 없음 |",
        u"## 1p. 이상점 정리보고",
        u"| V-9999-9 | zzz | 절 밖 | - | - | ❌ | - |",
    ]))
    rows = M._ledger_open_rows(str(p))
    assert [r.split("|")[1].strip() for r in rows] == ["V-1028-2", "V-1028-3"]


def test_3_missing_report_is_unmeasured_not_empty(tmp_path):
    assert M._ledger_open_rows(str(tmp_path / "none.md")) is None      # 계측 4원칙 ② — 미측정 ≠ 0
    p = tmp_path / "r.md"
    io.open(str(p), "w", encoding="utf-8").write(u"# 장전(pre)\n본문\n")
    assert M._ledger_open_rows(str(p)) == []
