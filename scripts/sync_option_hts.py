# -*- coding: utf-8 -*-
"""HTS [9842] 내보내기 폴더(data/db/option_hts)를 원본 PC 에서 이 PC 로 단방향 미러한다.

[MW0601 686차 / 2026-10-12]

왜 필요한가
  [9842] 파일은 MW0601 의 HTS 에서 손으로 내보낸다. 폴더가 .gitignore(data/*) 대상이라
  git 으로는 넘어가지 않고, MW0602 의 사다리(tools/maekjeom_ladder)는 같은 상대경로를
  읽으므로 **파일만 같은 자리에 오면 코드는 그대로 동작한다.**

지키는 것
  1. **mtime 보존**(shutil.copy2) — scripts/foreign_flow_pit_review.py 는 파일 mtime 을
     「그 시점에 존재했나」 판정에 쓴다. git·일반 복사는 mtime 을 바꿔 PIT 를 조용히 깬다.
  2. **원자적 교체**(.part → os.replace) — 사다리가 반쪽 파일을 읽지 않는다.
  3. **정착 대기**(--settle 초) — 원본 mtime 이 그보다 최근이면 HTS 가 아직 쓰는 중일 수
     있어 이번 회차는 건너뛴다(건너뜀 개수를 로그에 남긴다 — 계측 4원칙 ③).
  4. **삭제 비전파** — 원본에서 지워져도 사본은 남긴다.
  5. **도착 시각 기록**(_sync_arrivals.json) — 이 PC 에서 파일을 실제로 쓸 수 있게 된 시각은
     원본 mtime 보다 늦다. 그 차이를 남겨 「mtime ≤ T 이면 T 에 있었다」를 이 PC 의 라이브
     판단에 그대로 쓰지 않게 한다(계측 4원칙 ②·④).
  6. **단일 기록자** — 사본 폴더에 _MIRROR_OF_<원본호스트>.txt 표식을 둔다.
     derive_9842_daily.py 는 이 표식이 있으면 쓰지 않는다(파생본은 원본 PC 에서만 만든다).
  7. **원본 PC 에서 실행 금지** — 원본 UNC 의 호스트가 이 PC 면 자기 자신을 덮어쓰므로 거부.

사용 (MW0602)
  python scripts/sync_option_hts.py                     # 1회
  python scripts/sync_option_hts.py --loop 60 --until 16:30
  OPTION_HTS_SYNC.bat                                    # 위 루프를 띄운다
  원본 경로: --src 또는 환경변수 MIREUK_OPTION_HTS_SRC (기본 \\\\DeskTop-MW0601\\option_hts)

종료코드: 0 정상 · 2 실행 거부(원본 PC) · 3 원본 접근 불가(1회 모드)
"""
from __future__ import print_function

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import socket
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = r"\\DeskTop-MW0601\option_hts"
DEFAULT_DST = os.path.join(ROOT, "data", "db", "option_hts")
ARRIVALS = "_sync_arrivals.json"
MARKER_PREFIX = "_MIRROR_OF_"
# 사다리가 읽는 이름 규칙(ladder_data._list_9842_files) + 파생 매니페스트만 옮긴다
_NAME_RE = re.compile(r"^(\d{6}(?:_\d{4})?(?:_[DP])?\.(?:xlsx|xls)|_derived_D\.json)$")


def _log(msg):
    # 예약작업은 stdout 을 남기지 않으므로 logs/<YYYYMMDD>_OPTION_HTS_SYNC.log 에도 쓴다
    now = _dt.datetime.now()
    line = "%s [OptHtsSync] %s" % (now.strftime("%H:%M:%S"), msg)
    print(line)
    sys.stdout.flush()
    try:
        d = os.path.join(ROOT, "logs")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "%s_OPTION_HTS_SYNC.log" % now.strftime("%Y%m%d")), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except (IOError, OSError):
        pass


def unc_host(path):
    m = re.match(r"^[\\/]{2}([^\\/]+)", path or "")
    return m.group(1) if m else None


def is_self_source(src, hostname=None):
    """원본 UNC 의 호스트가 이 PC 인가 (대소문자 무시, 도메인 접미 무시)."""
    h = unc_host(src)
    if not h:
        return False
    me = (hostname or socket.gethostname()).split(".")[0].lower()
    return h.split(".")[0].lower() in (me, "localhost", "127.0.0.1")


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (IOError, OSError, ValueError):
        return {}


def _write_json_atomic(path, obj):
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, path)


def ensure_marker(dst, src):
    host = unc_host(src) or "LOCAL"
    p = os.path.join(dst, "%s%s.txt" % (MARKER_PREFIX, host.upper()))
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("이 폴더는 %s 의 읽기전용 미러다 (scripts/sync_option_hts.py).\n"
                     "여기에 직접 쓰지 말 것 — 다음 동기화가 원본 기준으로 덮어쓴다.\n"
                     "derive_9842_daily.py 는 이 표식이 있으면 실행을 거부한다.\n" % src)


def sync_once(src, dst, settle=5.0, dry_run=False, now=None):
    """→ dict(copied=[...], settling=[...], unchanged=n, ignored=n). 원본 접근 불가면 OSError."""
    now = time.time() if now is None else now
    entries = list(os.scandir(src))                 # 접근 불가면 여기서 OSError
    if not dry_run:
        os.makedirs(dst, exist_ok=True)
        ensure_marker(dst, src)
    arr_path = os.path.join(dst, ARRIVALS)
    arrivals = _load_json(arr_path)
    res = dict(copied=[], settling=[], unchanged=0, ignored=0)
    for e in sorted(entries, key=lambda x: x.name):
        if not e.is_file() or not _NAME_RE.match(e.name):
            res["ignored"] += 1
            continue
        st = e.stat()
        if now - st.st_mtime < settle:
            res["settling"].append(e.name)
            continue
        target = os.path.join(dst, e.name)
        if os.path.exists(target):
            ts = os.stat(target)
            if ts.st_size == st.st_size and abs(ts.st_mtime - st.st_mtime) < 0.01:
                res["unchanged"] += 1
                continue
        res["copied"].append(e.name)
        if dry_run:
            continue
        tmp = target + ".part"
        shutil.copy2(e.path, tmp)                   # copy2 = mtime 보존 (PIT 보호)
        os.replace(tmp, target)
        arrivals[e.name] = dict(src_mtime=round(st.st_mtime, 3), arrived=round(time.time(), 3),
                                lag_sec=round(time.time() - st.st_mtime, 1), size=st.st_size)
    if res["copied"] and not dry_run:
        _write_json_atomic(arr_path, arrivals)
    return res


def _summary(r):
    s = "copied=%d unchanged=%d settling=%d ignored=%d" % (
        len(r["copied"]), r["unchanged"], len(r["settling"]), r["ignored"])
    if r["copied"]:
        s += " | " + ", ".join(r["copied"][:6]) + (" … 외 %d개" % (len(r["copied"]) - 6) if len(r["copied"]) > 6 else "")
    if r["settling"]:
        s += " | 정착대기: " + ", ".join(r["settling"])
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.environ.get("MIREUK_OPTION_HTS_SRC", DEFAULT_SRC))
    ap.add_argument("--dst", default=DEFAULT_DST)
    ap.add_argument("--settle", type=float, default=5.0, help="원본 mtime 이 이 초 이내면 이번 회차 건너뜀")
    ap.add_argument("--loop", type=float, default=0, help="N초 간격 반복 (0=1회)")
    ap.add_argument("--until", default="16:30", help="--loop 종료 시각 HH:MM")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    for s in ("stdout", "stderr"):
        try:
            getattr(sys, s).reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if is_self_source(a.src):
        _log("거부: 원본 %s 의 호스트가 이 PC(%s)다 — 원본 PC 에서는 돌리지 않는다" % (a.src, socket.gethostname()))
        return 2
    if os.path.normcase(os.path.abspath(a.src)) == os.path.normcase(os.path.abspath(a.dst)):
        _log("거부: src 와 dst 가 같다")
        return 2

    _log("src=%s dst=%s settle=%.0fs loop=%s%s" % (a.src, a.dst, a.settle, a.loop or "1회",
                                                   (" until=" + a.until) if a.loop else ""))
    last_err = None
    while True:
        try:
            r = sync_once(a.src, a.dst, settle=a.settle, dry_run=a.dry_run)
            if last_err:
                _log("원본 접근 복구")
                last_err = None
            if r["copied"] or r["settling"] or not a.loop:
                _log(_summary(r))
        except OSError as ex:
            msg = "원본 접근 불가: %s" % ex
            if msg != last_err:                     # 같은 오류는 한 번만 찍는다
                _log(msg)
                last_err = msg
            if not a.loop:
                return 3
        if not a.loop or _dt.datetime.now().strftime("%H:%M") >= a.until:
            break
        time.sleep(a.loop)
    if a.loop:
        _log("종료 (%s 도달)" % a.until)
    return 0


if __name__ == "__main__":
    sys.exit(main())
