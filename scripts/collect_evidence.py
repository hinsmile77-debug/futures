#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""미륵이 일일 점검 증거 수집기 — 런처.

본체는 `.claude/skills/mireuk-daily-check/scripts/collect_evidence.py` 에 있다.
스킬 문서와 스크립트를 한 곳에 묶어두기 위해서다.

이 파일은 손에 익은 `scripts/` 경로와 작업 스케줄러에서 본체를 그대로 부를 수 있게
해주는 얇은 껍데기다. **로직은 여기에 두지 않는다** — 고칠 일이 생기면 본체를 고친다.

    python scripts/collect_evidence.py --discover
    python scripts/collect_evidence.py --phase post --date 2026-08-11
"""

from __future__ import annotations

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL = os.path.join(ROOT, ".claude", "skills", "mireuk-daily-check",
                    "scripts", "collect_evidence.py")

if not os.path.exists(REAL):
    raise SystemExit(
        "수집기 본체를 찾지 못했다: %s\n"
        "mireuk-daily-check 스킬이 설치돼 있는지 확인하라." % REAL
    )

if "--root" not in sys.argv:
    sys.argv += ["--root", ROOT]
sys.argv[0] = REAL

runpy.run_path(REAL, run_name="__main__")
