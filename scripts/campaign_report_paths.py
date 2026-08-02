# -*- coding: utf-8 -*-
"""[MW0601 407차] 주간 검증 리포트 산출물 경로 규약 — 공용 헬퍼.

`generate_validation_campaign_report.py`가 407차부터 PC별 폴더에 **날짜본**으로 쓴다:

    docs/정기점검/금요일점검/<PC명>/validation_campaign_report_YYYYMMDD.md
                                  /validation_campaign_metrics_YYYYMMDD.json

접미사가 붙는 변형도 허용한다(예: `..._20260801_pre405.md` — 특정 커밋 전 스냅샷).
날짜는 파일명의 첫 8자리 숫자에서 뽑고, 없으면 mtime으로 대체한다.
"""
from __future__ import annotations

import datetime
import glob
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEEKLY_DIR = os.path.join(BASE_DIR, "docs", "정기점검", "금요일점검")

_DATE_RE = re.compile(r"(\d{8})")


def pc_dir(pc: str) -> str:
    return os.path.join(WEEKLY_DIR, pc)


def _sort_key(path: str):
    """(날짜, 파일명) — 날짜가 같으면 파일명 사전순(접미사 있는 쪽이 뒤)."""
    m = _DATE_RE.search(os.path.basename(path))
    if m:
        return (m.group(1), os.path.basename(path))
    ts = datetime.date.fromtimestamp(os.path.getmtime(path))
    return (ts.strftime("%Y%m%d"), os.path.basename(path))


def list_reports(pc: str, kind: str = "report") -> list:
    """PC 폴더의 리포트/메트릭 파일을 날짜 오름차순으로."""
    ext = "md" if kind == "report" else "json"
    pat = os.path.join(pc_dir(pc), "validation_campaign_%s_*.%s" % (kind, ext))
    return sorted(glob.glob(pat), key=_sort_key)


# [MW0601 408차] FIFO 정리 대상 — **접미사 없는 정확한 형태만**.
# `..._20260801_pre405.md` 처럼 사람이 이름을 붙여 남긴 스냅샷과 주간회의 검토보고는
# 자동 삭제 대상이 아니다. 자동 생성물만 자동으로 지운다.
_STRICT_RE = re.compile(
    r"^validation_campaign_(report|metrics)_(\d{8})\.(md|json)$")


def prune(pc: str, keep: int, dry_run: bool = False) -> list:
    """PC 폴더에서 최근 `keep`개 날짜만 남기고 오래된 자동생성물을 지운다.

    - `keep <= 0`이면 아무것도 지우지 않는다(킬스위치).
    - 날짜 단위로 묶어서 md/json을 **함께** 지운다 — 한쪽만 남으면 대조가 깨진다.
    - 접미사가 붙은 파일·검토보고 md는 `_STRICT_RE`에 걸리지 않아 보존된다.
    - 폴더가 없으면 조용히 빈 리스트(새 PC 첫 실행).

    반환: 지운(또는 dry_run이면 지울) 경로 리스트.
    """
    if keep is None or keep <= 0:
        return []
    d = pc_dir(pc)
    if not os.path.isdir(d):
        return []

    by_date = {}
    for name in os.listdir(d):
        m = _STRICT_RE.match(name)
        if m:
            by_date.setdefault(m.group(2), []).append(os.path.join(d, name))
    if len(by_date) <= keep:
        return []

    doomed = []
    for date in sorted(by_date)[:-keep]:      # 최신 keep개를 제외한 나머지
        doomed.extend(sorted(by_date[date]))
    if dry_run:
        return doomed

    deleted = []
    for p in doomed:
        try:
            os.remove(p)
            deleted.append(p)
        except OSError:
            pass      # 잠김·권한 등 — 다음 주에 다시 시도된다. 실패가 리포트를 막으면 안 된다.
    return deleted


def latest(pc: str, kind: str = "report", date: str = None) -> str:
    """가장 최근 산출물 경로. date('YYYYMMDD') 지정 시 그 날짜의 것.

    찾지 못하면 FileNotFoundError — 조용히 빈 결과를 내는 것보다 낫다
    (0802 대조에서 "파일이 없다"를 늦게 깨달아 시간을 버린 전례).
    """
    files = list_reports(pc, kind)
    if date:
        files = [f for f in files if date in os.path.basename(f)]
    if not files:
        raise FileNotFoundError(
            "%s에 %s 산출물이 없다%s — 해당 PC에서 "
            "scripts/generate_validation_campaign_report.py를 실행했는지, "
            "또는 그 PC의 커밋을 pull 했는지 확인할 것."
            % (pc_dir(pc), kind, (" (date=%s)" % date) if date else ""))
    return files[-1]
