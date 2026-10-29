#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""신동 주체 일일 점검 — 증거 수집기 (MW0602 Sindong-V4 · 661차 후속5).

미륵 휴면(`MIREUK_ENGINE="off"`)에서 거래 주체는 신동 V4 다. 미륵 수집기
(`.claude/skills/mireuk-daily-check/scripts/collect_evidence.py`)는 미륵 판정 DB·재학습 마커를
필수로 보므로 휴면 중에는 거짓 적신호를 낸다. 이 수집기는 **신동이 실제로 쓰는 것만** 모은다.

공통 기반(DB 3단 폴백 읽기 · git 잠금 방지 호출 · PC 판별 · 거래일 판정 · 미결 관측 스캔)은
미륵 수집기를 **import 해서 재사용**한다 — 두 벌로 만들면 한쪽만 고쳐진다.

표준 라이브러리만 쓴다. Python 3.7 호환(py37_32) · Cowork 리눅스 샌드박스에서도 돈다
(Windows 전용 항목 — 예약작업 상태 — 은 그 환경에서 「미측정」으로 남긴다. 계측 4원칙 ②).

사용:
    python .claude/skills/shindong-daily-check/scripts/collect_shindong_evidence.py --phase pre --pc MW0602 --out-auto
    python .claude/skills/shindong-daily-check/scripts/collect_shindong_evidence.py --phase post --date 2026-10-26 --pc MW0602
산출(--out-auto): docs/정기점검/매일점검/evidence_sd_<PC>-<YYYYMMDD>_<phase>.md — 기존 파일은 덮어쓰지 않는다.
"""
from __future__ import print_function

import argparse
import io
import json
import os
import re
import statistics
import subprocess
import sys
from datetime import date as _date
from datetime import datetime, timedelta, timezone

# [F-SD-2 · 666차 후속] 「오늘」은 항상 KST 로 잡는다. Cowork 샌드박스 시계가 UTC 라
# datetime.now() 를 그대로 쓰면 KST 00:00~09:00(장전 08:51 포함) 세션이 전일을 오늘로 오판했다
# (664차 재현: evidence_sd_MW0602-20261026_pre_2.md). 한국은 DST 가 없어 고정 +9 로 충분하다
# (zoneinfo 는 3.9+ 라 py37_32 에서 못 쓴다).
KST = timezone(timedelta(hours=9))


def _now_kst():
    """KST 현재 시각(naive) — 표시·날짜 산출 공통."""
    return datetime.now(KST).replace(tzinfo=None)


_HERE = os.path.dirname(os.path.abspath(__file__))
_CE_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "mireuk-daily-check", "scripts"))
if _CE_DIR not in sys.path:
    sys.path.insert(0, _CE_DIR)
import collect_evidence as CE  # noqa: E402  — 공통 기반 재사용

V4_START = "2026-10-26"          # SPEC_VERSION SD-2026-10-26-v4 — 사전등록 판정 창 시작
V4_JUDGE_DAYS = 20               # V4 vs V3 되돌림 판정 창(거래일)
BE_SLIP_N = 20                   # 본전청산 슬립 판정 표본(scripts/shindong_v4_be_slip.py)

# 로그에서 셀 패턴 — (라벨, 정규식, 기대) · 기대: "0"=0건이어야 정상, "1+"=1건 이상, None=관찰
COUNT_PATTERNS = (
    ("미륵 엔진 off 기동", r"\[Engine\] 미륵 엔진=off", "1+"),
    ("주체 신동 고정", r"\[Principal\] PRINCIPAL_LOCK", "1+"),
    ("미륵 진입 거부 `[MireukOff]`", r"\[MireukOff\]", "0"),
    ("경량 패스 ATR 시작 `[LightPass]`", r"\[LightPass\] 경량 ATR", "1+"),
    ("입력 지연 `[FlowStale]` (진입 쪽, 섀도)", r"\[FlowStale\] 신동 입력 지연 \d", None),
    ("보유 중 입력 지연 `[FlowStaleHold]` 발생", r"\[FlowStaleHold\] 신동 보유 중 입력 지연 (?:\d|미측정)", None),
    ("7222 수집 실패 중 시간청산", r"7222 수집 실패 중", None),
    ("진입봉 오래돼 쫓지 않음(2분 규칙)", r"진입봉이 오래돼 쫓지 않음", None),
    ("신동 진입 기각", r"\[ShindongLive\] .* 진입 기각", None),
    ("옵션 체인 워커 완료", r"\[OptionChain\]\[Worker\] 완료", None),
    ("옵션 체인 워치독", r"\[OptionChain\]\[Watchdog\]", "0"),
    ("AlertMail 발송", r"\[AlertMail\] 메일 발송 성공", None),
    ("재기동(세션)", r"\[Session\] 재기동 #", None),
    ("크래시 서명 신규", r"\[FaultHandler\] 크래시 서명 보존 — 신규 [1-9]", "0"),
    ("Traceback", r"Traceback \(most recent call last\)", "0"),
)
POST_PATTERNS = (
    ("장후 마감 — 미륵 휴면 1줄", r"\[DailyClose\] 미륵 휴면", "1+"),
    ("신동 일일 리포트 생성", r"\[ShindongReport\] .*신동_일일", "1+"),
    ("신동 리포트 메일(15:40)", r"\[ShindongMail\] 발송 완료", None),
    ("15:11 강제청산 점검", r"\[SchedForceExit\] 15:1\d 점검", "1+"),
    ("15:10 안전망 발동(ERROR)", r"\[SchedForceExit\].*안전망 발동", "0"),
)
# 고정적으로 찍히는(사용자 결정으로 확정된) CRITICAL — ERROR/CRITICAL 집계에서 따로 센다
KNOWN_CRITICAL = (r"SIZING_TARGET_CAPITAL_ENABLED=True",)


# ------------------------------------------------------------------ 기초
def _read_lines(path):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except Exception:
        return None


def today_logs(root, day):
    d = os.path.join(root, "logs")
    tok = day.strftime("%Y%m%d")
    out = {}
    try:
        for n in sorted(os.listdir(d)):
            if n.startswith(tok + "_") and n.endswith(".log") and "_HOGA" not in n:
                lines = _read_lines(os.path.join(d, n))
                if lines is not None:
                    out[n] = lines
    except OSError:
        pass
    return out


def grep(logs, pat, files=None):
    rx = re.compile(pat)
    hits = []
    for n, lines in logs.items():
        if files and not any(f in n for f in files):
            continue
        for ln in lines:
            if rx.search(ln):
                hits.append((n, ln))
    hits.sort(key=lambda x: x[1][:19])
    return hits


def dedup(hits):
    """같은 줄이 SYSTEM·WARN 등 여러 파일에 중복 기록된다 — 본문 기준으로 한 번만 센다."""
    seen, out = set(), []
    for n, ln in hits:
        k = re.sub(r"^\S+ \S+ \[\w+\] \w+: ", "", ln) + ln[:19]
        if k in seen:
            continue
        seen.add(k)
        out.append((n, ln))
    return out


_MAIL_RX = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
NEXT_TODO_SCAN_LINES = 400       # NEXT_TODO 는 최신 절이 위에 쌓인다 — 전체(3천 건+)를 훑으면 잡음이다


def tr(s, n=200):
    s = _MAIL_RX.sub("<메일>", s)        # 증거 파일은 커밋된다 — 주소를 남기지 않는다
    s = s.replace("|", "\\|")
    return s if len(s) <= n else s[:n] + "…"


def setting_values(root, names):
    p = os.path.join(root, "config", "settings.py")
    lines = _read_lines(p) or []
    vals = {}
    for nm in names:
        rx = re.compile(r"^%s\s*(?::[^=]+)?=\s*(.+?)\s*(?:#.*)?$" % re.escape(nm))
        for ln in lines:
            m = rx.match(ln)
            if m:
                vals[nm] = m.group(1)
        vals.setdefault(nm, "(없음)")
    return vals


def read_marker(root, rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    lines = _read_lines(p) or []
    return " / ".join(l.strip() for l in lines if l.strip())[:200]


def win_tasks():
    """Windows 예약작업 상태 — Windows 가 아니면 None(미측정)."""
    if os.name != "nt":
        return None
    out = {}
    for tn in (r"\Maitreya_EODretrain", r"\Mireuk\Shindong_EOD_1555", r"\Mireuk\Shindong_DailyMail_1810"):
        try:
            p = subprocess.Popen(["schtasks", "/query", "/tn", tn, "/fo", "LIST", "/v"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o, _e = p.communicate(timeout=20)
            txt = o.decode("cp949", "replace")
            if p.returncode != 0:
                out[tn] = "없음"
                continue
            st = re.search(r"^(?:상태|Status):\s*(.+)$", txt, re.M)
            lr = re.search(r"^(?:마지막 결과|Last Result):\s*(.+)$", txt, re.M)
            sch = re.search(r"^(?:예약된 작업 상태|Scheduled Task State):\s*(.+)$", txt, re.M)
            out[tn] = "%s · %s · 마지막 결과 %s" % (
                (sch.group(1).strip() if sch else "?"), (st.group(1).strip() if st else "?"),
                (lr.group(1).strip() if lr else "?"))
        except Exception as e:
            out[tn] = "조회 실패: %s" % e
    return out


def launcher_logs(root, day):
    """[724차 이식] 당일 런처 로그(logs/Mireuk_batch/launcher_<날짜>*)."""
    d = os.path.join(root, "logs", "Mireuk_batch")
    tok = day.strftime("%Y%m%d")
    out = {}
    try:
        for n in sorted(os.listdir(d)):
            if n.startswith("launcher_" + tok):
                lines = _read_lines(os.path.join(d, n))
                if lines is not None:
                    out[n] = lines
    except OSError:
        pass
    return out


def live_main_procs(root):
    """[MW0601 724차 이식] 이 작업 폴더의 실행 중 main.py — 런처 GUARD 원라이너와 같은 규칙
    (명령줄의 main.py 를 cwd 기준 절대경로로 풀어 <root>/main.py 와 비교).
    → (목록, None) 또는 (None, 미측정 사유). psutil 이 없거나 Windows 가 아니면 미측정(계측 4원칙 ②)."""
    if os.name != "nt":
        return None, "Windows 가 아님"
    try:
        import psutil
    except Exception as e:
        return None, "psutil 없음(%s)" % e
    tgt = os.path.normcase(os.path.abspath(os.path.join(root, "main.py")))
    out, unread = [], 0
    for p in psutil.process_iter(["pid", "name", "cmdline", "create_time", "cwd"]):
        info = p.info or {}
        if "python" not in (info.get("name") or "").lower():
            continue
        cmd = info.get("cmdline")
        if cmd is None:
            unread += 1
            continue
        res = [os.path.normcase(c if os.path.isabs(c) else os.path.join(info.get("cwd") or "?", c))
               for c in cmd if (c or "").lower().endswith("main.py")]
        if tgt in res:
            out.append({"pid": info.get("pid"),
                        "started": datetime.fromtimestamp(info.get("create_time") or 0).strftime("%Y-%m-%d %H:%M:%S")})
    return out, ("명령줄 판독불가 %d건(권한/비트폭) — 수가 모자랄 수 있다" % unread) if unread else None


def mireuk_launcher_tasks():
    """[MW0601 724차 이식] 실행 파일이 start_mireuk.bat 인 예약작업 — 이름이 아니라 동작으로 찾는다.
    → [(이름, 상태)] 또는 None(미측정)."""
    if os.name != "nt":
        return None
    ps = ("[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
          "Get-ScheduledTask | Where-Object { $_.Actions | Where-Object { $_.Execute -and "
          "$_.Execute.ToLower().EndsWith('start_mireuk.bat') } } | "
          "ForEach-Object { $_.TaskPath + $_.TaskName + '|' + $_.State }")
    try:
        p = subprocess.Popen(["powershell", "-NoProfile", "-Command", ps],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o, _e = p.communicate(timeout=60)
        if p.returncode != 0:
            return None
        rows = [l.strip() for l in o.decode("utf-8", "replace").splitlines() if "|" in l]
        return [tuple(r.rsplit("|", 1)) for r in rows]
    except Exception:
        return None


def launcher_kinds(root, day):
    """[MW0601 724차 이식] 당일 런처 로그를 머리말로 가른다 — `Sindong (` / `Mireuk (`.
    → [(파일, 종류, 휴면거부여부)]. 미륵 런처가 떴다는 것 자체가 미륵 런처 작업이 켜져 있었다는 증거다."""
    out = []
    for n, lines in launcher_logs(root, day).items():
        head = " ".join(lines[:4])
        kind = "Sindong" if "Sindong (" in head else ("Mireuk" if "Mireuk (" in head else "?")
        refused = any("[MireukGate] REFUSE" in l for l in lines)
        out.append((n, kind, refused))
    return out


# ------------------------------------------------------------------ 신동 대사
# [673차 후속12 · 2026-10-29 사용자 지시] 커밋 반영 — 실행 중인 main.py 가 최신 실행경로 커밋을 물고 있나.
#   §3-V(변경 반영 검증)는 「효과가 보이는가」를 판정한다. 그 전제인 「그 코드가 프로세스에 올라갔는가」를
#   먼저 기계적으로 가른다 — 장중 수정 후 재기동을 안 했으면 효과가 없는 게 당연하고, 그걸 ❌(미반영 결함)로
#   판정하면 틀린다. 프로세스가 새로 읽는 코드만 센다: 별도 프로세스로 매번 새로 뜨는 scripts/·tools/ 와
#   tests/·.claude/·docs/ 는 제외.
_RUNTIME_EXCLUDE = ("tests/", "scripts/", "tools/", ".claude/", "docs/", "dev_memory/", "_archive/", "_to_delete/")
_BOOT_LOG_RX = r"\[Notify\] .*기동 완료"


def _is_runtime_path(p):
    return p.endswith(".py") and not p.startswith(_RUNTIME_EXCLUDE)


def _kst_str(epoch):
    return datetime.fromtimestamp(epoch, KST).strftime("%Y-%m-%d %H:%M:%S")


def _git_ok(s):
    return s is not None and not s.startswith("(git ")


def runtime_commits(root, n=80):
    """최근 n커밋 중 실행경로(.py) 를 바꾼 것 → [dict(h, ct, ci, s, paths)] (최신 먼저) 또는 None(미측정)."""
    lg = CE.run_git(root, ["log", "-%d" % n, "--name-only", "--format=@@%h|%ct|%ci|%s"])
    if not _git_ok(lg):
        return None
    out = []
    for l in lg.splitlines():
        if l.startswith("@@"):
            h, ct, _ci, s = (l[2:].split("|", 3) + ["", "", ""])[:4]
            # 표시는 epoch → KST. %ci 를 잘라 쓰면 안 된다 — 커밋이 +0000 으로 기록된 날이 있다(2026-10-29: 19:25 KST 커밋이 `10:25 +0000`)
            out.append(dict(h=h, ct=int(ct or 0), ci=_kst_str(int(ct or 0)), s=s, paths=[]))
        elif l.strip() and out:
            out[-1]["paths"].append(l.strip().strip('"'))
    return [c for c in out if any(_is_runtime_path(p) for p in c["paths"])]


def boot_time(root, day, procs, logs):
    """실행 중 main.py 의 기동 시각 → (epoch, 출처) 또는 (None, 사유).
    psutil 프로세스 시각이 정본, 못 재면(샌드박스·명령줄 판독불가) 당일 마지막 「기동 완료」 로그로 대신한다."""
    if procs:
        ts = []
        for r in procs:
            try:
                ts.append(datetime.strptime(r["started"], "%Y-%m-%d %H:%M:%S"))
            except Exception:
                pass
        if ts:
            t = min(ts)                                   # 여러 벌이면 가장 오래된 쪽(보수적)
            return t.replace(tzinfo=KST).timestamp(), "프로세스 시각(PID %s)" % ",".join(str(r["pid"]) for r in procs)
    h = dedup(grep(logs, _BOOT_LOG_RX, files=("_SYSTEM",)))
    if h:
        try:
            t = datetime.strptime(h[-1][1][:19], "%Y-%m-%d %H:%M:%S")
            return t.replace(tzinfo=KST).timestamp(), "당일 마지막 「기동 완료」 로그(%s · 프로세스 미측정)" % h[-1][1][11:19]
        except Exception:
            pass
    return None, "실행 중 프로세스·당일 기동 로그 모두 없음"


def dirty_runtime(root):
    """커밋 안 된 실행경로 .py 변경 → [줄] 또는 None(미측정). 샌드박스 마운트는 CRLF 차이로 수백 건 오탐이라 Windows 에서만 잰다."""
    if os.name != "nt":
        return None
    st = CE.run_git(root, ["status", "--porcelain", "--untracked-files=all"])
    if not _git_ok(st):
        return None
    out = []
    for l in st.splitlines():
        # `XY path` — run_git 이 출력 전체를 strip 해 첫 줄의 앞 공백(` M`)이 사라진다. 고정 오프셋으로 자르지 말 것.
        m = re.match(r"^\s*\S{1,2}\s+(?:.* -> )?(.+)$", l)
        if m and _is_runtime_path(m.group(1).strip().strip('"')):
            out.append(l.strip())
    return out


def shindong_positions(root, day):
    """trades.db 신동 행 → 포지션 단위(entry_ts 묶음). None = 미측정."""
    rows = CE.db_rows(root, "data/db/trades.db",
                      "SELECT entry_ts, exit_ts, direction, entry_price, exit_price, quantity, "
                      "net_pnl_krw, exit_reason, entry_source, entry_qty FROM trades "
                      "WHERE entry_ts >= ? AND entry_ts < ? ORDER BY id",
                      (day.isoformat(), (day + timedelta(days=1)).isoformat()))
    if rows is None:
        return None, None
    pos, other = {}, {}
    for r in rows:
        bucket = pos if (r[8] or "") == "SHINDONG" else other
        k = (r[0], r[8] or "?")
        p = bucket.setdefault(k, {"entry_ts": r[0], "src": r[8] or "?", "dir": r[2], "entry_px": r[3],
                                  "legs": 0, "qty": 0, "net": 0.0, "exit_ts": r[1], "exit_px_w": 0.0,
                                  "reasons": [], "entry_qty": r[9]})
        p["legs"] += 1
        p["qty"] += int(r[5] or 0)
        p["net"] += float(r[6] or 0.0)
        p["exit_ts"] = max(p["exit_ts"] or "", r[1] or "")
        p["exit_px_w"] += float(r[4] or 0.0) * int(r[5] or 0)
        if r[7] and r[7] not in p["reasons"]:
            p["reasons"].append(r[7])
    for b in (pos, other):
        for p in b.values():
            p["exit_px"] = (p["exit_px_w"] / p["qty"]) if p["qty"] else None
    return list(pos.values()), list(other.values())


def shindong_main(root, day):
    rows = CE.db_rows(root, "data/db/shindong.db",
                      "SELECT variant, trade_key, side, entry_ts, entry_px, stop_init, status, leg1_reason, "
                      "leg1_exit_ts, leg1_exit_px, net_krw, source, spec_version FROM shindong_trades "
                      "WHERE trade_date = ? ORDER BY variant, entry_ts", (day.isoformat(),))
    return rows


def broker_net(root, day):
    rows = CE.db_rows(root, "data/db/trades.db",
                      "SELECT pnl_krw, pnl_net_krw, broker_net_krw, deposit_cash_krw, next_day_deposit_cash_krw "
                      "FROM daily_broker_pnl WHERE date = ?", (day.isoformat(),))
    if rows is None:
        return None
    return rows[0] if rows else ()


def flow_arrival(root, day):
    """7222 첫 도착 지연(661차 후속3 이후 행만) — 신동 상품 개인 행 기준."""
    try:
        if root not in sys.path:
            sys.path.insert(0, root)
        from strategy.shindong.runner import select_flow_product
        product = select_flow_product(day)[0]
    except Exception as e:
        return {"measured": False, "why": "상품 판별 실패: %s" % e}
    rows = CE.db_rows(root, "data/db/option_flow.db",
                      "SELECT bar_time, MIN(collected_at), MAX(last_collected_at) FROM option_investor_flow "
                      "WHERE trade_date=? AND product LIKE ? AND investor='individual' "
                      "AND last_collected_at IS NOT NULL GROUP BY bar_time", (day.isoformat(), product + "%"))
    if rows is None:
        return {"measured": False, "why": "option_flow.db 조회 실패(또는 last_collected_at 컬럼 없음 — 재기동 전)"}
    lags = []
    for bt, ca, _la in rows:
        try:
            t = datetime.strptime(str(ca)[:19], "%Y-%m-%dT%H:%M:%S")
            b = datetime.combine(day, datetime.strptime(bt, "%H:%M").time())
        except Exception:
            continue
        if not ("09:00" <= bt <= "15:05"):
            continue
        # 분봉 bar_time 은 그 분의 시작 — 그 분이 끝난 뒤(b+1분) 몇 초 만에 행이 처음 보였나.
        lags.append((t - (b + timedelta(minutes=1))).total_seconds())
    if not lags:
        return {"measured": False, "product": product,
                "why": "오늘 장중 행 중 last_collected_at 이 채워진 행 없음(재기동 전 코드로 수집됐을 수 있다)"}
    s = sorted(lags)
    q = lambda f: s[min(len(s) - 1, int(f * (len(s) - 1)))]
    return {"measured": True, "product": product, "n": len(s), "p50": q(0.5), "p90": q(0.9),
            "max": s[-1], "ge120": sum(1 for x in s if x >= 120)}


def aligned_days(root, day):
    """V4 채점 시작~오늘 중 R1 정렬 아래 신동 재생이 돈 날(shindong_cadence.json align=True)."""
    base = os.path.join(root, "data", "principal")
    out = []
    try:
        names = sorted(os.listdir(base))
    except Exception:
        return out
    for n in names:
        if not (V4_START <= n <= day.isoformat()):
            continue
        try:
            with io.open(os.path.join(base, n, "shindong_cadence.json"), encoding="utf-8") as f:
                if json.load(f).get("align") is True:
                    out.append(n)
        except Exception:
            continue
    return out


def prereg_progress(root, day):
    rows = CE.db_rows(root, "data/db/shindong.db",
                      "SELECT COUNT(DISTINCT trade_date), "
                      "SUM(CASE WHEN leg1_reason='BE' THEN 1 ELSE 0 END), COUNT(*) FROM shindong_trades "
                      "WHERE variant='MAIN' AND source='live' AND trade_date>=? AND trade_date<=?",
                      (V4_START, day.isoformat()))
    return rows[0] if rows else None


# 리포트 국면 절 — 「증거는 모였는데 리포트에 절이 안 들어갔다」 검출 (F-SD-1, 2026-10-26 장중 절 누락)
PHASE_ORDER = ("pre", "intra", "post")
PHASE_HEADINGS = {"pre": u"# 장전(pre)", "intra": u"# 장중(intra)", "post": u"# 장후(post)"}


def report_phase_sections(root, day, pcid):
    """국면별 {evidence: 증거 파일 수, section: 리포트에 절 헤딩이 있는가(None=리포트 없음)}."""
    d = os.path.join(root, "docs", "정기점검", "매일점검")
    tok = day.strftime("%Y%m%d")
    lines = _read_lines(os.path.join(d, "%s-%s-점검리포트.md" % (pcid, tok)))
    try:
        names = os.listdir(d)
    except Exception:
        names = []
    out = {}
    for ph in PHASE_ORDER:
        pre_ = "evidence_sd_%s-%s_%s" % (pcid, tok, ph)
        ev = sum(1 for n in names if n.startswith(pre_) and n.endswith(".md"))
        sec = None if lines is None else any(l.strip() == PHASE_HEADINGS[ph] for l in lines)
        out[ph] = {"evidence": ev, "section": sec}
    return out


def missing_phase_sections(root, day, pcid, phases):
    """증거 파일은 있는데 리포트에 절 헤딩이 없는 국면 목록."""
    st = report_phase_sections(root, day, pcid)
    return [ph for ph in phases if st[ph]["evidence"] and not st[ph]["section"]]


# ------------------------------------------------------------------ 렌더
def build(root, day, phase, pcid, pclabel):
    A = []
    a = A.append
    now = _now_kst()
    ok_td, why_td = CE.is_trading_day(root, day)
    prev = CE.prev_trading_day(root, day)
    logs = today_logs(root, day)
    flags = []

    a("# 신동 일일 점검 증거 — %s / %s / %s" % (pcid, day.isoformat(), phase))
    a("")
    a("- 수집 시각: %s · PC: %s · 거래일: %s (%s) · 직전 거래일: %s"
      % (now.strftime("%Y-%m-%d %H:%M:%S"), pclabel, "예" if ok_td else "아니오", why_td,
         prev.isoformat() if prev else "?"))
    br = CE.run_git(root, ["branch", "--show-current"])
    head = CE.run_git(root, ["log", "-1", "--format=%h %ci %s"])
    a("- 브랜치: `%s` · HEAD: %s" % (br, tr(head, 140)))
    if br.strip() != "Sindong-V4":
        flags.append("브랜치가 `Sindong-V4` 가 아니다(`%s`) — 신동 운영 브랜치는 `Sindong-V4`, `dev` 는 미륵 보존용(CLAUDE.md 「브랜치 역할」)" % br)
    lk = CE.git_lock_state(root)
    a("- `.git/index.lock`: %s" % ("미측정(%s)" % lk.get("why") if not lk.get("measured")
                                  else ("**있음** · 나이 %s" % CE.fmt_age(lk.get("age_sec")) if lk.get("exists") else "없음")))
    a("- 당일 로그 파일: %d개%s" % (len(logs), "" if logs else " — **없음**(휴장이면 정상)"))
    a("")
    # §1 설정
    keys = ("MIREUK_ENGINE", "PRINCIPAL_LOCK", "LIGHT_PASS_DRY_RUN", "SHINDONG_LIVE_QTY", "MAX_CONTRACTS",
            "SIZING_TARGET_CAPITAL_KRW", "CB_CONSEC_STOP_LIMIT", "SHINDONG_FLOW_STALE_GUARD",
            "SHINDONG_HOLD_FLOW_WATCH", "SHINDONG_HOLD_FLOW_STALE_MIN", "SHINDONG_REPORT_MAIL_ENABLED",
            "SHINDONG_DAILY_MAIL_ENABLED")
    sv = setting_values(root, keys)
    a("## 1. 설정 (config/settings.py — 기동 시 1회 읽힌다)")
    a("")
    a("| 키 | 값 |")
    a("|---|---|")
    for k in keys:
        a("| `%s` | `%s` |" % (k, tr(sv[k], 60)))
    if sv["MIREUK_ENGINE"].strip("'\"") != "off":
        flags.append("`MIREUK_ENGINE` 이 `off` 가 아니다(`%s`) — 신동 점검 대상이 아니다. 미륵 점검(`mireuk-daily-check`)을 쓸 것" % sv["MIREUK_ENGINE"])
    if sv["PRINCIPAL_LOCK"].strip("'\"") != "SHINDONG":
        flags.append("`PRINCIPAL_LOCK` 이 `SHINDONG` 이 아니다(`%s`)" % sv["PRINCIPAL_LOCK"])
    a("")
    # §2 로그 계수
    a("## 2. 로그 계수 (당일 · 중복 기록은 1회로)")
    a("")
    a("| 항목 | 건수 | 기대 | 판정 | 첫 줄 |")
    a("|---|---|---|---|---|")
    pats = COUNT_PATTERNS + (POST_PATTERNS if phase == "post" else ())
    for label, pat, exp in pats:
        h = dedup(grep(logs, pat))
        n = len(h)
        if exp == "0":
            verdict = "정상" if n == 0 else "**이상**"
        elif exp == "1+":
            verdict = "정상" if n >= 1 else ("**누락**" if ok_td and logs else "휴장/로그 없음")
        else:
            verdict = "관찰"
        if verdict in ("**이상**", "**누락**"):
            flags.append("%s — %d건(기대 %s)" % (label, n, exp))
        a("| %s | %d | %s | %s | %s |" % (label, n, exp or "-", verdict, tr(h[0][1][11:], 110) if h else ""))
    errs = dedup(grep(logs, r"\[(?:ERROR|CRITICAL)\]"))
    known = [h for h in errs if any(re.search(k, h[1]) for k in KNOWN_CRITICAL)]
    unknown = [h for h in errs if h not in known]
    a("")
    a("- ERROR/CRITICAL: 전체 %d줄 · 확정된 고정 경고 %d줄(`SIZING_TARGET_CAPITAL_ENABLED` — 2026-10-13 사용자 결정) · **그 밖 %d줄**"
      % (len(errs), len(known), len(unknown)))
    for _n, ln in unknown[:12]:
        a("  - `%s`" % tr(ln, 220))
    if len(unknown) > 12:
        a("  - … 외 %d줄" % (len(unknown) - 12))
    a("")
    # §3 장전 축
    a("## 3. 장전 준비 (전일 신동 EOD · 맥점 · 자본 · 동기화)")
    a("")
    if prev:
        mk = read_marker(root, "data/shindong_eod_done_%s.txt" % prev.strftime("%Y%m%d"))
        a("- 전일(%s) 신동 EOD 마커: %s" % (prev.isoformat(), ("`%s`" % mk) if mk else "**없음**"))
        if not mk or "exit=0" not in (mk or ""):
            flags.append("전일 신동 EOD 마커가 없거나 exit≠0 — 08:50 ATR14·맥점이 낡은 이력으로 산출됐을 수 있다")
    try:
        with io.open(os.path.join(root, "data", "premarket_levels_history.json"), encoding="utf-8") as f:
            ld = json.load(f).get("last_date")
        a("- 맥점 이력 캐시 `last_date`: `%s`%s" % (ld, "" if (prev and ld == prev.isoformat()) or ld == day.isoformat()
                                                  else " — **전 거래일이 아니다**"))
    except Exception as e:
        a("- 맥점 이력 캐시: 미측정(%s)" % e)
    for lab, pat in (("08:50 맥점", r"\[LEVELS 08:50\] ref="), ("09:30 맥점", r"\[LEVELS 09:30\] ref="),
                     ("V4 ATR14", r"\[Shindong\] V4 ATR14"), ("장시작 가능수량", r"\[Capital\] 장시작 가능수량"),
                     ("ProfitGuard 임계", r"\[ProfitGuard\] 원화 임계 배율"),
                     ("브로커 동기화", r"\[BrokerSync\] startup sync")):
        h = dedup(grep(logs, pat))
        a("- %s: %s" % (lab, ("`%s`" % tr(h[-1][1][11:], 170)) if h else "없음"))
    t = win_tasks()
    if t is None:
        a("- 예약작업 상태: 미측정(Windows 가 아님 — Cowork 샌드박스)")
    else:
        for k, v in t.items():
            a("- 예약작업 `%s`: %s" % (k, v))
        if "Maitreya" in str(t) and "사용" in t.get(r"\Maitreya_EODretrain", "") and "사용 안 함" not in t.get(r"\Maitreya_EODretrain", ""):
            flags.append("미륵 재학습 예약작업 `\\Maitreya_EODretrain` 이 꺼져 있지 않다 — 휴면 중 미륵 모델을 덮어쓴다")
    a("")

    # §3-b 단일 인스턴스 [MW0601 724차 이식 — MW0601 2026-10-27 08:40 이중 기동]
    a("### 3-b. 단일 인스턴스 (main.py 1벌 · 미륵 런처 휴면)")
    a("")
    procs, why = live_main_procs(root)
    if procs is None:
        a("- 실행 중 main.py: 미측정(%s)" % why)
    else:
        a("- 실행 중 main.py: **%d개**%s" % (len(procs), (" — %s" % why) if why else ""))
        for r in procs:
            a("  - PID=%s started=%s" % (r.get("pid"), r.get("started")))
        if len(procs) > 1:
            flags.append("main.py 가 %d개 실행 중 — 신동 실주문 중복 위험. 늦게 뜬 쪽(런처 포함)을 즉시 종료할 것" % len(procs))
        elif not procs and phase == "pre" and ok_td and day == now.date() and now.hour < 16:
            flags.append("장전인데 실행 중 main.py 가 없다 — 신동 런처 기동 실패 여부 확인")
    mt = mireuk_launcher_tasks()
    if mt is None:
        a("- 미륵 런처 예약작업(start_mireuk.bat): 미측정")
    elif not mt:
        a("- 미륵 런처 예약작업(start_mireuk.bat): 없음")
    for nm, st in (mt or []):
        a("- 미륵 런처 예약작업 `%s`: %s" % (nm, st))
        if st.strip().lower() != "disabled":
            flags.append("미륵 런처 예약작업 `%s` 상태가 `%s` — 휴면 중엔 Disabled 여야 한다(MW0601 10-27 이중 기동 원인)" % (nm, st))
    lk = launcher_kinds(root, day)
    a("- 당일 런처 로그: %s" % (", ".join("%s=%s%s" % (n, k, "(휴면 거부)" if rf else "") for n, k, rf in lk) or "없음"))
    for n, k, rf in lk:
        if k == "Mireuk":
            flags.append("미륵 런처가 떴다(`%s`)%s — 미륵 런처 예약작업이 켜져 있었다"
                         % (n, " · 휴면 게이트가 거부함" if rf else " · **main.py 까지 기동됐을 수 있다**"))
    dup = dedup(grep(logs, r"\[SingleInstance\] 중복 기동 거부"))
    a("- `[SingleInstance] 중복 기동 거부`: %d건%s" % (len(dup), (" — `%s`" % tr(dup[0][1][11:], 150)) if dup else ""))
    if dup:
        flags.append("main.py 중복 기동 시도 %d건 — 뮤텍스가 막았다. 어느 경로로 두 번 떴는지 확인할 것" % len(dup))
    a("")
    _commit_reflection(A, flags, root, day, phase, now, procs, logs)
    # §4 신동 거래·대사
    if phase in ("intra", "post"):
        a("## 4. 신동 거래 — 3원 대사 (포지션 단위)")
        a("")
        ent = dedup(grep(logs, r"\[ShindongLive\] 진입 (?:LONG|SHORT)"))
        stp = dedup(grep(logs, r"\[ShindongLive\] 손절 "))
        fil = dedup(grep(logs, r"\[Position\] 체결청산"))
        pos, other = shindong_positions(root, day)
        mains = shindong_main(root, day)
        live_main = [r for r in (mains or []) if r[0] == "MAIN" and r[11] == "live"]
        bn = broker_net(root, day)
        a("| 원천 | 값 |")
        a("|---|---|")
        a("| 로그 `[ShindongLive] 진입` | %d건 |" % len(ent))
        a("| `shindong.db` MAIN(live) | %s |" % ("미측정" if mains is None else "%d건" % len(live_main)))
        a("| `trades.db` SHINDONG 포지션 | %s |" % ("미측정" if pos is None else "%d포지션 · net %s원" % (
            len(pos), format(int(round(sum(p["net"] for p in pos))), ","))))
        if other:
            a("| `trades.db` 그 밖 출처 | %s |" % ", ".join("%s %s원" % (p["src"], format(int(round(p["net"])), ","))
                                                       for p in other))
        if bn is None:
            a("| 브로커 net(CpTd6197) | 미측정 |")
        elif not bn:
            a("| 브로커 net(CpTd6197) | 행 없음(장후 15:40 이전이거나 미적재) |")
        else:
            a("| 브로커 net(CpTd6197) | broker_net **%s원** · 엔진 net %s원 · gross %s원 |"
              % (format(int(bn[2] or 0), ","), format(int(bn[1] or 0), ","), format(int(bn[0] or 0), ",")))
        a("")
        if pos is not None and mains is not None and len(ent) != len(live_main) or (pos is not None and len(pos) != len(live_main)):
            flags.append("3원 대사 불일치 — 로그 진입 %d · shindong.db MAIN live %d · trades.db 신동 포지션 %s"
                         % (len(ent), len(live_main), "?" if pos is None else len(pos)))
        if bn and pos is not None and not other:
            diff = (bn[2] or 0) - sum(p["net"] for p in pos)
            a("- 브로커 net − trades 신동 net = %s원%s" % (format(int(round(diff)), ","),
                                                       " (±5,000원 초과 — 확인)" if abs(diff) > 5000 else ""))
            if abs(diff) > 5000:
                flags.append("브로커 net 과 trades 신동 net 차 %s원" % format(int(round(diff)), ","))
        a("")
        a("### 4-1. 케이스 표 (재생 규격 vs 실체결)")
        a("")
        a("| 키 | 방향 | 규격 진입 | 실 진입 | 진입 슬립pt(불리+) | 재생 청산 | 실 청산 | 청산 슬립pt(불리+) | 사유(재생/실) | 재생 net | 실 net |")
        a("|---|---|---|---|---|---|---|---|---|---|---|")
        used = set()
        for r in live_main:
            side = int(r[2] or 0)
            m = None
            for i, p in enumerate(pos or []):
                if i in used:
                    continue
                if abs((datetime.strptime(p["entry_ts"][:19], "%Y-%m-%d %H:%M:%S")
                        - datetime.strptime(str(r[3])[:19], "%Y-%m-%d %H:%M:%S")).total_seconds()) <= 180:
                    m = p
                    used.add(i)
                    break
            es = (side * ((m["entry_px"] or 0) - (r[4] or 0))) if m else None
            xs = (-side * ((m["exit_px"] or 0) - (r[9] or 0))) if (m and r[9] and m.get("exit_px")) else None
            a("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s |" % (
                r[1], "LONG" if side > 0 else "SHORT", r[4], ("%.2f" % m["entry_px"]) if m else "-",
                ("%+.2f" % es) if es is not None else "-", r[9] if r[9] else "-",
                ("%.2f" % m["exit_px"]) if m and m.get("exit_px") else "-", ("%+.2f" % xs) if xs is not None else "-",
                r[7] or r[6], ",".join(m["reasons"]) if m else "-",
                format(int(round(r[10] or 0)), ","), format(int(round(m["net"])), ",") if m else "-"))
        if not live_main:
            a("| (오늘 MAIN 실거래 없음) | | | | | | | | | | |")
        a("")
        a("- 손절 갱신 로그 %d줄 · 체결청산 로그 %d줄" % (len(stp), len(fil)))
        a("")
        a("### 4-2. 섀도 대조 (같은 날 변형별 재생 net)")
        a("")
        var = {}
        for r in (mains or []):
            v = var.setdefault(r[0], [0, 0.0])
            v[0] += 1
            v[1] += float(r[10] or 0.0)
        for k in sorted(var):
            a("- `%s`: %d거래 · %s원" % (k, var[k][0], format(int(round(var[k][1])), ",")))
        if not var:
            a("- 기록 없음")
        a("")
        a("### 4-3. 7222 첫 도착 지연 (661차 후속3 — 재기동 뒤 행만)")
        a("")
        fa = flow_arrival(root, day)
        if fa.get("measured"):
            a("- 상품 `%s` · %d분 · 분 마감 후 첫 도착 p50 %.0f초 · p90 %.0f초 · 최대 %.0f초 · 2분 이상 %d분"
              % (fa["product"], fa["n"], fa["p50"], fa["p90"], fa["max"], fa["ge120"]))
        else:
            a("- 미측정 — %s" % fa.get("why"))
        a("")
    # §5 장후
    if phase == "post":
        a("## 5. 장후 마감·작업")
        a("")
        tok = day.strftime("%Y%m%d")
        for lab, rel in (("신동 EOD 마커", "data/shindong_eod_done_%s.txt" % tok),
                         ("daily_close 마커", "data/daily_close_done_%s.txt" % tok),
                         ("신동 종합 메일 마커", "data/shindong_daily_mail_done_%s.txt" % tok)):
            mk = read_marker(root, rel)
            a("- %s: %s" % (lab, ("`%s`" % mk) if mk else "없음"))
        rp = os.path.join(root, "docs", "신동거래_V2", "일일", "신동_일일_%s_%s.md" % (pcid, tok))
        a("- 신동 일일 리포트: %s" % ("`%s`" % os.path.relpath(rp, root) if os.path.exists(rp) else "**없음**"))
        pg = prereg_progress(root, day)
        if pg:
            a("- 사전등록 진행: V4 실거래 %s거래일 / 판정 창 %d거래일 · MAIN live %s거래 · 본전청산 %s건 / 슬립 판정 %d건"
              % (pg[0] or 0, V4_JUDGE_DAYS, pg[2] or 0, pg[1] or 0, BE_SLIP_N))
        # [673차 후속7 · 사용자 결정 2026-10-29] 본전청산 슬립은 R1(수급 타이머 정렬) 전/후 구간별로 판정한다 —
        #   구간 표본·판정은 `python scripts/shindong_v4_be_slip.py` 와 신동 일일 리포트 §2-1 이 정본이다.
        al = aligned_days(root, day)
        a("- 본전청산 슬립 구간: R1 정렬 후 기록일 %d일%s — 판정은 구간별(정렬 후가 기준 · 합치지 않음), 상세 `scripts/shindong_v4_be_slip.py`"
          % (len(al), (" (첫날 %s)" % al[0]) if al else ""))
        a("")
    # §6 미결 관측
    a("## 6. 미결 관측 · 장중 확인 항목")
    a("")
    try:
        pend = CE.scan_pending_observations(root, CE.load_config(root), day)
        rows = pend.get("rows") or []
        a("- 판정 기준 로그가 오늘 자에 있는 미결 관측: %d건%s" % (len(rows), "" if pend.get("measured") else " (미측정)"))
        for r in rows[:10]:
            a("  - `%s` (%s · %d거래일 경과) — 태그 `%s` — %s"
              % (r["id"], "한정어까지 일치" if r.get("match") == "strong" else "태그만 일치 — 충족 아님이 기본",
                 r["age_days"], "`, `".join(r["tags"]), tr(r["line"], 120)))
        if len(rows) > 10:
            a("  - … 외 %d건" % (len(rows) - 10))
        pr = pend.get("prose_resolved") or []
        if pr:
            a("- 본문엔 해소 기록이 있는데 체크박스가 열린 관측: %d건 — 원 줄을 `[x]` 로 닫을 것" % len(pr))
    except Exception as e:
        a("- 미결 관측 스캔 미측정: %s" % e)
    nt = (_read_lines(os.path.join(root, "dev_memory", "NEXT_TODO.md")) or [])[:NEXT_TODO_SCAN_LINES]
    open_items = [l for l in nt if l.lstrip().startswith("- [ ]")]
    tagged = {t: [l for l in open_items if t in l] for t in ("[로그]", "[경보]", "[화면]")}
    untag_intra = [l for l in open_items if "장중" in l and not any(t in l for t in tagged)]
    a("- NEXT_TODO 상단 %d줄의 열린 항목 %d건 · 태그 `[로그]` %d · `[경보]` %d · `[화면]` %d · **태그 없는 「장중」 항목 %d건**"
      % (NEXT_TODO_SCAN_LINES, len(open_items), len(tagged["[로그]"]), len(tagged["[경보]"]), len(tagged["[화면]"]), len(untag_intra)))
    for l in (tagged["[로그]"] + tagged["[경보]"] + tagged["[화면]"] + untag_intra)[:15]:
        a("  - %s" % tr(l.strip(), 170))
    a("")
    # §7 git
    a("## 7. 오늘 커밋")
    a("")
    # [F-SD-3 확장 · 666차 후속3] 경계에 +0900 — 없으면 UTC 샌드박스가 KST 09:00~익일 09:00 을
    # 「오늘」로 읽어 KST 00:00~09:00 커밋을 빠뜨린다(재현: Sindong2-V4 c36f450 04:55 KST 누락).
    lg = CE.run_git(root, ["log", "--format=%ct %h %s", "--since=%s 00:00 +0900" % day.isoformat(),
                           "--until=%s 00:00 +0900" % (day + timedelta(days=1)).isoformat()])
    for l in (lg.splitlines() if lg else [])[:20]:
        ct, _, rest = l.partition(" ")
        a("- %s %s" % (_kst_str(int(ct)) + " KST" if ct.isdigit() else ct, tr(rest, 160)))
    if not lg:
        a("- 없음")
    a("")
    # §8 변경 반영 검증 — 대장 후보(스킬 §3-V). 판정은 점검 세션이 한다 — 여기서는 대상만 기계적으로 모은다.
    _change_ledger(A, root, day, prev, pcid)
    # 앞 국면 절 누락 — 오늘의 앞 국면, 장전이면 직전 거래일 전 국면
    checks = [(day, PHASE_ORDER[:PHASE_ORDER.index(phase)])]
    if phase == "pre" and prev:
        checks.append((prev, PHASE_ORDER))
    for dd, phs in checks:
        for ph in missing_phase_sections(root, dd, pcid, phs):
            flags.append("%s 리포트에 `%s` 절이 없다 — 증거 파일(`evidence_sd_%s-%s_%s`)은 있다. 그 국면 세션이 append 에 실패했다(F-SD-1)"
                         % (dd.isoformat(), PHASE_HEADINGS[ph], pcid, dd.strftime("%Y%m%d"), ph))
    # §0 적신호를 맨 위로
    head_ = ["## 0. 자동 적신호 (출발점이지 결론이 아니다)", ""]
    if not ok_td:
        head_.append("- 휴장일(%s) — 당일 로그·거래 부재에서 파생되는 항목은 결함이 아니다" % why_td)
    head_ += ["- %s" % f for f in flags] or ["- 없음"]
    head_.append("")
    i = A.index("## 1. 설정 (config/settings.py — 기동 시 1회 읽힌다)")
    return "\n".join(A[:i] + head_ + A[i:]) + "\n"


def _commit_reflection(A, flags, root, day, phase, now, procs, logs):
    """§3-c 커밋 반영(스킬 §3-R) — 실행 코드 = HEAD 인가. 판정 전제를 기계적으로 가른다."""
    a = A.append
    a("### 3-c. 커밋 반영 — 실행 중 main.py 가 최신 실행경로 커밋을 물고 있나 (스킬 §3-R)")
    a("")
    bt, src = boot_time(root, day, procs, logs)
    a("- 기동 시각: %s" % (("%s KST · 출처 %s" % (datetime.fromtimestamp(bt, KST).strftime("%Y-%m-%d %H:%M:%S"), src))
                         if bt else "미측정 — %s" % src))
    rc = runtime_commits(root)
    if rc is None:
        a("- 실행경로 커밋: git 미측정")
    elif not rc:
        a("- 실행경로 커밋: 최근 80커밋 중 없음")
    else:
        last = rc[0]
        a("- 마지막 실행경로 커밋: `%s` %s — %s" % (last["h"], last["ci"], tr(last["s"], 100)))
        if bt:
            pend = [c for c in rc if c["ct"] > bt]
            if not pend:
                a("- **반영됨** — 기동이 마지막 실행경로 커밋보다 뒤다(실행 코드 = HEAD 의 실행경로)")
            else:
                # 장후 판정 기준 시각 15:10 — 그 뒤 커밋은 오늘 반영될 수 없다(다음 기동 때 반영, 정상)
                cut = datetime(day.year, day.month, day.day, 15, 10, tzinfo=KST).timestamp()
                late = [c for c in pend if c["ct"] >= cut and phase == "post"]
                miss = [c for c in pend if c not in late]
                a("- 기동 뒤 실행경로 커밋 %d건 — 미반영 %d건 · 15:10 이후(다음 기동 반영 예정, 정상) %d건"
                  % (len(pend), len(miss), len(late)))
                a("")
                a("| 커밋 | 시각 | 상태 | 제목 | 실행경로 파일 |")
                a("|---|---|---|---|---|")
                for c in pend:
                    rp = [p for p in c["paths"] if _is_runtime_path(p)]
                    a("| %s | %s | %s | %s | %s |" % (
                        c["h"], c["ci"][5:16], "다음 기동" if c in late else "**미반영**", tr(c["s"], 80).replace("|", "/"),
                        ", ".join("`%s`" % p for p in rp[:3]) + (" … 외 %d개" % (len(rp) - 3) if len(rp) > 3 else "")))
                a("")
                if miss:
                    flags.append("실행 중 main.py(기동 %s)가 실행경로 커밋 %d건(%s) 이전 코드다 — %s"
                                 % (datetime.fromtimestamp(bt, KST).strftime("%m-%d %H:%M"), len(miss),
                                    ", ".join(c["h"] for c in miss[:5]),
                                    "FLAT 확인 후 재기동이 필요하다(신동 엔진 스위치는 기동 시 1회만 읽힌다)" if phase != "post"
                                    else "오늘 장중 그 변경은 돌지 않았다. §3-V 해당 행은 ❌ 가 아니라 「미기동」(↩ 다음 기동 뒤 재판정)"))
    dr = dirty_runtime(root)
    if dr is None:
        a("- 커밋 안 된 실행경로 변경: 미측정(Windows 가 아님 — 샌드박스 CRLF 오탐)")
    else:
        a("- 커밋 안 된 실행경로 변경: %d건" % len(dr))
        for l in dr[:10]:
            a("  - `%s`" % tr(l, 150))
        if len(dr) > 10:
            a("  - … 외 %d건" % (len(dr) - 10))
        if dr:
            flags.append("커밋 안 된 실행경로 .py 변경 %d건 — 실행 코드가 HEAD 와 다를 수 있다(기동 뒤 수정이면 미반영, 기동 전이면 미커밋 코드로 거래 중)" % len(dr))
    ab = CE.run_git(root, ["rev-list", "--left-right", "--count", "HEAD...@{u}"])
    if _git_ok(ab) and len(ab.split()) == 2:
        ahead, behind = (int(x) for x in ab.split())
        a("- 원격 대비(로컬 추적 참조 기준 · fetch 안 함): 앞섬 %d · 뒤짐 %d%s"
          % (ahead, behind, " — **push 안 된 커밋**" if ahead else ""))
        if behind:
            flags.append("로컬 브랜치가 추적 원격보다 %d커밋 뒤다 — 다른 세션의 push 를 받지 않은 채 기동했을 수 있다" % behind)
    else:
        a("- 원격 대비: 미측정(%s)" % tr(ab or "", 80))
    a("")


# [MW0601 724차 후속3 이식] 변경 반영 검증 대장(스킬 §3-V) — 경로 구분. 위에서부터 처음 맞는 것.
_LEDGER_KINDS = (
    ("실행경로", ("main.py", "strategy/", "safety/", "collection/", "config/", "start_", "TASK_")),
    ("도구·화면·점검", ("tools/", "scripts/", "dashboard/", ".claude/", "utils/", "tests/")),
    ("문서·산출물", ("docs/", "dev_memory/", "CLAUDE.md", "CORE.md", "ROADMAP.md")),
)
_LEDGER_OPEN_MARKS = ("❌", "⏳", "🔄", "미결", "미확인")


def _ledger_kind(paths):
    kinds = []
    for p in paths:
        k = next((nm for nm, pre in _LEDGER_KINDS if p.startswith(pre)), "기타")
        if k not in kinds:
            kinds.append(k)
    order = [nm for nm, _ in _LEDGER_KINDS] + ["기타"]
    return sorted(kinds, key=order.index)


def _ledger_open_rows(path):
    """리포트에서 **마지막** 「변경 반영 검증」 절의 `| V-` 행 중 아직 닫히지 않은 것(✅ 아닌 것)."""
    lines = _read_lines(path)
    if not lines:
        return None                                   # 파일 없음 — 미측정(빈 목록과 다르다)
    starts = [i for i, l in enumerate(lines) if l.startswith("#") and "변경 반영 검증" in l]
    if not starts:
        return []
    i0 = starts[-1]
    lvl = len(lines[i0]) - len(lines[i0].lstrip("#"))
    out = []
    for l in lines[i0 + 1:]:
        if l.startswith("#") and len(l) - len(l.lstrip("#")) <= lvl:
            break
        if l.lstrip().startswith("| V-") and any(m in l for m in _LEDGER_OPEN_MARKS):
            out.append(l.strip())
    return out


def _change_ledger(A, root, day, prev, pcid):
    a = A.append
    a("## 8. 변경 반영 검증 — 대장 후보 (스킬 §3-V)")
    a("")
    if prev is None:
        a("- 직전 거래일 미측정 — 대상 창을 정하지 못했다")
        a("")
        return
    since = "%s 15:40:00 +0900" % prev.isoformat()
    lg = CE.run_git(root, ["log", "--reverse", "--name-only", "--format=@@%h|%ct|%s", "--since=" + since,
                           "--until=%s 00:00 +0900" % (day + timedelta(days=1)).isoformat()])
    commits = []
    for l in (lg or "").splitlines():
        if l.startswith("@@"):
            h, ct, s = (l[2:].split("|", 2) + ["", ""])[:3]
            commits.append(dict(h=h, ci=_kst_str(int(ct or 0))[5:16] if ct.isdigit() else "?", s=s, paths=[]))
        elif l.strip() and commits:
            commits[-1]["paths"].append(l.strip().strip('"'))
    a("- 창: 직전 거래일 %s 15:40 KST 이후 — 어제 장후 자동조치(17:23)·저녁·밤·오늘 커밋을 모두 덮는다" % prev.isoformat())
    if not commits:
        a("- 대상 커밋 0건" + ("" if lg is not None else " (git 미측정)"))
    else:
        tgt = [c for c in commits if _ledger_kind(c["paths"]) != ["문서·산출물"]]
        a("- 커밋 %d건 · 검증 대상(코드·도구 포함) **%d건** · 문서·산출물만 %d건(대장 제외 — 점검 산출물 커밋 등)"
          % (len(commits), len(tgt), len(commits) - len(tgt)))
        a("")
        a("| 커밋 | 시각 | 구분 | 제목 | 바꾼 파일(코드) |")
        a("|---|---|---|---|---|")
        for c in tgt:
            code = [p for p in c["paths"] if not p.startswith(("docs/", "dev_memory/"))]
            shown = ", ".join("`%s`" % p for p in code[:3]) + (" … 외 %d개" % (len(code) - 3) if len(code) > 3 else "")
            a("| %s | %s | %s | %s | %s |" % (c["h"], c["ci"], "·".join(_ledger_kind(c["paths"])),
                                             tr(c["s"], 90).replace("|", "/"), shown or "—"))
    a("")
    rep = os.path.join(root, "docs", "정기점검", "매일점검")
    for label, d in (("직전 거래일", prev), ("오늘 앞 국면", day)):
        p = os.path.join(rep, "%s-%s-점검리포트.md" % (pcid, d.strftime("%Y%m%d")))
        rows = _ledger_open_rows(p)
        if rows is None:
            a("- %s(%s) 리포트 없음 — 이월 미결 미측정" % (label, d.isoformat()))
        elif not rows:
            a("- %s(%s) 「변경 반영 검증」 열린 행 0건" % (label, d.isoformat()))
        else:
            a("- %s(%s) 「변경 반영 검증」 **열린 행 %d건** — 오늘 대장에 이월해 다시 판정한다" % (label, d.isoformat(), len(rows)))
            for r in rows[:15]:
                a("  - %s" % tr(r, 200))
            if len(rows) > 15:
                a("  - … 외 %d건" % (len(rows) - 15))
    a("")


def main(argv=None):
    ap = argparse.ArgumentParser(description="신동 주체 일일 점검 증거 수집기")
    ap.add_argument("--phase", choices=("pre", "intra", "post"), required=True)
    ap.add_argument("--date", default=None)
    ap.add_argument("--pc", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--out-auto", action="store_true")
    ap.add_argument("--verify-append", action="store_true",
                    help="리포트를 쓴 뒤 그 국면 절 헤딩이 실제로 들어갔는지만 확인(없으면 exit 1). 수집은 하지 않는다")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if a.pc:
        CE._PC_OVERRIDE = CE._norm_pc(a.pc)
    root = CE.find_repo_root(os.getcwd()) or CE.find_repo_root(_HERE)
    day = _date.fromisoformat(a.date) if a.date else _now_kst().date()
    pcid, pclabel = CE.pc_id()
    if a.verify_append:
        st = report_phase_sections(root, day, pcid)[a.phase]
        ok = bool(st["section"])
        print("[collect_shindong_evidence] verify-append %s %s: %s (증거 파일 %d개 · 리포트 %s)"
              % (day.isoformat(), a.phase, "OK" if ok else "FAIL — `%s` 절 없음" % PHASE_HEADINGS[a.phase],
                 st["evidence"], "없음" if st["section"] is None else "있음"))
        return 0 if ok else 1
    txt = build(root, day, a.phase, pcid, pclabel)
    out = a.out
    if a.out_auto:
        d = os.path.join(root, "docs", "정기점검", "매일점검")
        base = os.path.join(d, "evidence_sd_%s-%s_%s" % (pcid, day.strftime("%Y%m%d"), a.phase))
        out, k = base + ".md", 2
        while os.path.exists(out):               # 덮어쓰지 않는다
            out, k = "%s_%d.md" % (base, k), k + 1
    if out:
        with io.open(out, "w", encoding="utf-8") as f:
            f.write(txt)
        print("[collect_shindong_evidence] 저장: %s" % out)
    else:
        print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
