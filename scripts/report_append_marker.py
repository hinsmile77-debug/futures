# -*- coding: utf-8 -*-
"""[MW0601 675차 후속 / G-1] 일일 점검 리포트 append 생존 마커.

## 왜 있는가

2026-10-09 장전(08:57 예정)·장중(12:25 예정) 점검 예약이 6시간 넘게 밀려
15:33 KST에 **19초 차이로 거의 동시에** 발화했다. 둘 다 같은 날짜의
`<PC>-<YYYYMMDD>-점검리포트.md`에 append 하는 세션이다. 그날은 휴장일이라
결론이 같아 무해했지만, 거래일에 반복되면 한 세션이 다른 세션의 절을 못 본 채
(§5-3 이월 처리 없이) 자기 절을 쓴다 — 그리고 **사후에 아무도 그 사실을 모른다.**

이 마커는 쓰기 경쟁을 **막지 않는다**(append 는 각자 한다). 막는 대신
「지금 같은 날짜 리포트에 다른 세션이 쓰는 중이다」를 **알고 기록하게** 한다.

## 쓰는 법

    python scripts/report_append_marker.py acquire --phase post --session <id>
    python scripts/report_append_marker.py check
    python scripts/report_append_marker.py release --phase post --session <id>

`acquire` 는 항상 자기 마커를 쓴다. 다른 세션의 **신선한** 마커가 있으면
그 목록을 출력하고 **rc=2** 를 돌려준다 — 그때 세션은 자기 절 맨 위에
「병행 세션 N개 감지: …」를 적는다. `check` 도 같은 판정(rc 0/2)만 한다.

## 스테일 처리

비정상 종료로 마커가 남으면 「항상 충돌 중」 오탐이 된다. 그래서 마커에 시작
시각을 쓰고 **2시간(`--max-age-sec`) 지난 마커는 무시**한다(지우지는 않는다 —
`acquire`/`release` 때 같은 날짜의 스테일 마커만 정리한다). 시각을 못 읽는
마커는 **판정 불가**로 따로 센다(신선으로도 스테일로도 위장하지 않는다 —
계측 4원칙 ②).

## 위치

`data/dailycheck_markers/<PC>-<YYYYMMDD>-<phase>-<session>.json` — `data/` 는
gitignore 대상이다(PC별 런타임 산출물, 커밋 금지). `.git/index.lock` 과는
무관한 별개 파일이다.

⚠ py3.7(py37_32) · py3.10(py310_64) 양쪽에서 도는 **의존성 없는 단일 파일**로
유지할 것.
"""

from __future__ import print_function

import argparse
import datetime as _dt
import json
import os
import platform
import re
import sys
import time

#: 이보다 오래된 마커는 비정상 종료 잔재로 보고 무시한다(초).
DEFAULT_MAX_AGE_SEC = 2 * 3600

PHASES = ("pre", "intra", "post", "other")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIR = os.path.join(_ROOT, "data", "dailycheck_markers")

_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


def pc_id():
    """`utils.db_utils.pc_id()` 와 같은 규칙 — 의존성 없이 복제한다."""
    host = platform.node() or ""
    m = re.search(r"(MW\d{4})", host, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return host[:32] if host else "UNKNOWN"


def _safe(s):
    s = _SAFE.sub("_", s or "")
    return s[:64] or "unknown"


def marker_path(marker_dir, pc, date, phase, session):
    name = "%s-%s-%s-%s.json" % (_safe(pc), date, _safe(phase), _safe(session))
    return os.path.join(marker_dir, name)


def scan(marker_dir, pc, date, now=None, max_age_sec=DEFAULT_MAX_AGE_SEC,
         exclude_path=None):
    """같은 PC·날짜 마커를 fresh / stale / unreadable 로 나눈다."""
    now = time.time() if now is None else now
    out = {"fresh": [], "stale": [], "unreadable": []}
    if not os.path.isdir(marker_dir):
        return out
    prefix = "%s-%s-" % (_safe(pc), date)
    for fn in sorted(os.listdir(marker_dir)):
        if not (fn.startswith(prefix) and fn.endswith(".json")):
            continue
        p = os.path.join(marker_dir, fn)
        if exclude_path and os.path.abspath(p) == os.path.abspath(exclude_path):
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                rec = json.load(f)
            started = float(rec["started_epoch"])
        except Exception:
            out["unreadable"].append({"path": p})
            continue
        rec["path"] = p
        rec["age_sec"] = round(now - started, 1)
        if rec["age_sec"] > max_age_sec:
            out["stale"].append(rec)
        else:
            out["fresh"].append(rec)
    return out


def _prune_stale(found):
    removed = 0
    for rec in found["stale"]:
        try:
            os.remove(rec["path"])
            removed += 1
        except OSError:
            pass
    return removed


def acquire(marker_dir, pc, date, phase, session, now=None,
            max_age_sec=DEFAULT_MAX_AGE_SEC):
    now = time.time() if now is None else now
    if not os.path.isdir(marker_dir):
        os.makedirs(marker_dir)
    path = marker_path(marker_dir, pc, date, phase, session)
    found = scan(marker_dir, pc, date, now=now, max_age_sec=max_age_sec,
                 exclude_path=path)
    pruned = _prune_stale(found)
    rec = {
        "pc": pc, "date": date, "phase": phase, "session": session,
        "pid": os.getpid(),
        "started_epoch": now,
        "started_at": _dt.datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False)
    return {"path": path, "others": found["fresh"],
            "unreadable": found["unreadable"], "pruned_stale": pruned}


def release(marker_dir, pc, date, phase, session):
    path = marker_path(marker_dir, pc, date, phase, session)
    try:
        os.remove(path)
        return True
    except OSError:
        return False


def _fmt(rec):
    return "%s 국면 · 세션 %s · 시작 %s (%.0f초 전)" % (
        rec.get("phase"), rec.get("session"), rec.get("started_at"),
        rec.get("age_sec", 0))


def main(argv=None):
    ap = argparse.ArgumentParser(description="일일 점검 리포트 append 생존 마커")
    ap.add_argument("action", choices=("acquire", "release", "check"))
    ap.add_argument("--phase", default="other", choices=PHASES)
    ap.add_argument("--session", default="")
    ap.add_argument("--date", default=_dt.date.today().strftime("%Y%m%d"))
    ap.add_argument("--pc", default=None)
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--max-age-sec", type=int, default=DEFAULT_MAX_AGE_SEC)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    pc = a.pc or pc_id()
    session = a.session or ("pid%d" % os.getpid())

    if a.action == "release":
        ok = release(a.dir, pc, a.date, a.phase, session)
        print("마커 해제" if ok else "해제할 마커 없음")
        return 0

    if a.action == "acquire":
        res = acquire(a.dir, pc, a.date, a.phase, session,
                      max_age_sec=a.max_age_sec)
        others, unreadable = res["others"], res["unreadable"]
    else:
        found = scan(a.dir, pc, a.date, max_age_sec=a.max_age_sec)
        others, unreadable = found["fresh"], found["unreadable"]
        res = {"others": others, "unreadable": unreadable}

    if a.json:
        print(json.dumps(res, ensure_ascii=False, default=str))
    else:
        if others:
            print("병행 세션 %d개 감지 (%s %s 리포트):" % (len(others), pc, a.date))
            for rec in others:
                print("  - " + _fmt(rec))
        else:
            print("병행 세션 없음 (%s %s)" % (pc, a.date))
        if unreadable:
            print("판정 불가 마커 %d개 (시각을 못 읽음): %s" % (
                len(unreadable), ", ".join(os.path.basename(u["path"]) for u in unreadable)))
    return 2 if others else 0


if __name__ == "__main__":
    sys.exit(main())
