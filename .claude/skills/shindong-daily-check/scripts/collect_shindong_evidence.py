#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""신동 주체 일일 점검 — 증거 수집기 (MW0601 Sindong2-V4 · 713차 B1).

원본: MW0602 Sindong-V4 `.claude/skills/shindong-daily-check/scripts/collect_shindong_evidence.py`(661차 후속5).
v9 판으로 옮기며 바꾼 것:
  · 신동 규격이 다르다 — v3(`SD-2026-10-21-v3` · R2/R3 · 1차/최종 레그 · 15:05) · 집행 기록
    `data/principal/<날짜>/shindong_exec.jsonl`(ENTER · EXIT_LEG1 · SET_STOP · CLOSED_ELSEWHERE …) · 로그 `[ShindongExec]`
  · 주체는 고정이 아니라 허용 집합 — `PRINCIPAL_ALLOWED`·`PRINCIPAL_DEFAULT` · 피터 선택 가능
  · 711차 손절거리 위험 수량(`[ShindongExec] 위험 기준 축소`) · 실전 자본 3층(`[Capital]`)
  · 미륵 수집기(`mireuk-daily-check/scripts/collect_evidence.py`)는 Sindong-V4 판의 공통 함수 대부분이
    없는 세대라 **자급식**으로 짰다 — 재사용은 `run_git`(잠금 방지)·`pc_id`·`find_repo_root` 셋뿐이다.

미륵 휴면(`MIREUK_ENGINE="off"`)에서 미륵 수집기는 재학습·SHAP·CB③·매분 9단계 로그를 필수로 봐서 거짓 적신호를 낸다.
이 수집기는 **신동·피터가 실제로 쓰는 것과 휴면 감시 항목만** 모은다.

표준 라이브러리만 쓴다. Python 3.7 호환 · Cowork 리눅스 샌드박스에서도 돈다
(Windows 전용 항목 — 예약작업 상태 — 은 그 환경에서 「미측정」으로 남긴다. 계측 4원칙 ②).

사용:
    python .claude/skills/shindong-daily-check/scripts/collect_shindong_evidence.py --phase pre --pc MW0601 --out-auto
    python .claude/skills/shindong-daily-check/scripts/collect_shindong_evidence.py --phase post --date 2026-10-26 --pc MW0601
산출(--out-auto): docs/정기점검/매일점검/evidence_sd_<PC>-<YYYYMMDD>_<phase>.md — 기존 파일은 덮어쓰지 않는다.
"""
from __future__ import print_function

import argparse
import io
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import date as _date
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
_CE_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "mireuk-daily-check", "scripts"))
if _CE_DIR not in sys.path:
    sys.path.insert(0, _CE_DIR)
import collect_evidence as CE  # noqa: E402  — run_git(잠금 방지) · pc_id · find_repo_root 재사용

EXPECT_BRANCH = "Sindong2-V4"
SWITCH_DAY = "2026-10-26"          # 미륵 휴면 전환일(713차) — 711차 X 1.5% 10거래일 판정 창 시작과 같다
RISK_JUDGE_DAYS = 10               # 711차: 10거래일 실측 뒤 X 2.0% 승격 여부 결정(사용자 결정)
NEXT_TODO_SCAN_LINES = 400

# (라벨, 정규식, 기대, 적용 국면) · 기대: "0"=0건이어야 정상, "1+"=1건 이상, None=관찰
COUNT_PATTERNS = (
    ("기동 — 신동 주체 초기화(미륵 엔진 off)", r"신동 주체 초기화 \(미륵 엔진 off\)", "1+", "all"),
    ("`[Engine] 미륵 엔진=off`", r"\[Engine\] 미륵 엔진=off", "1+", "all"),
    ("**미륵 진입 거부 `[MireukOff]`** (1건이라도 = 도달 경로 결함)", r"\[MireukOff\]", "0", "all"),
    ("08:45 휴면 분기 `[EarlyWarmup] 미륵 휴면`", r"\[EarlyWarmup\] 미륵 휴면", "1+", "all"),
    ("08:45 실시간 선행 구독", r"\[EarlyWarmup\] Cybos RT 08:45 선행 구독", "1+", "all"),
    ("08:55 장전 `[PreOpen] 미륵 휴면`", r"\[PreOpen\] 미륵 휴면", "1+", "intra"),
    ("경량 패스 `[LightPass] 경량 ATR … 시작`", r"\[LightPass\] 경량 ATR \d{4}-\d\d-\d\d 시작", "1+", "intra"),
    ("경량 패스 1초 초과", r"\[LightPass\] total=\d+ms .*1초 초과", None, "intra"),
    ("경량 패스 중복 분봉 차단", r"\[LightPass\] 중복 분봉", None, "intra"),
    ("재학습 생략 `[GBM-64] 미륵 휴면`(있으면 정상)", r"\[GBM-64\] 미륵 휴면", None, "all"),
    ("주체 전환·거부 `[Principal]`", r"\[Principal\] (?:거래주체 전환|전환 거부)", None, "all"),
    ("신동 진입 `[ShindongExec] 진입`", r"\[ShindongExec\] 진입 R", None, "intra"),
    ("신동 진입 기각", r"\[ShindongExec\] .* 진입 기각", None, "intra"),
    ("711차 위험 기준 축소", r"\[ShindongExec\] 위험 기준 축소", None, "intra"),
    ("711차 위험수량 미측정", r"위험수량 미측정", None, "intra"),
    ("주문가능수량 미측정(CpTd6722)", r"\[ShindongExec\] 주문가능수량 미측정", None, "intra"),
    ("**신동 청산 주문 실패**", r"\[ShindongExec\] 청산 주문 실패", "0", "intra"),
    ("**신동 집행 단계·폴링 예외**", r"\[ShindongExec\] (?:집행 단계 예외|폴링 예외)", "0", "intra"),
    ("정규 재생 대조 미갱신(옵션흐름 지연)", r"\[ShindongExec\] 정규 재생 대조 \d+초 미갱신", None, "intra"),
    ("철회 섀도 `[ShindongRetractShadow]`", r"\[ShindongRetractShadow\]", None, "intra"),
    ("긴급 알림 메일 발송", r"\[AlertMail\] 메일 발송 성공", None, "all"),
    ("재기동(세션)", r"\[Session\] 재기동 #", None, "all"),
    ("Traceback", r"Traceback \(most recent call last\)", "0", "all"),
)
POST_PATTERNS = (
    ("장후 `[DailyClose] 미륵 휴면`", r"\[DailyClose\] 미륵 휴면", "1+"),
    ("신동 일일 리포트 `[ShindongReport]`", r"\[ShindongReport\] .*신동_일일", "1+"),
    ("15:40 신동 메일(15:40 메일은 B6 로 끔 — 0 이 정상)", r"\[ShindongMail\] 발송 완료", None),
    ("15:11 강제청산 점검", r"\[SchedForceExit\] 15:1\d 점검", "1+"),
    ("15:10 안전망 발동(ERROR)", r"\[SchedForceExit\].*안전망 발동", "0"),
    ("net 대사 `[NetRecon]`", r"\[NetRecon\]", "1+"),
)
KNOWN_CRITICAL = (r"SIZING_TARGET_CAPITAL_ENABLED=True",)
_PHASE_RANK = {"pre": 0, "intra": 1, "post": 2}
_MAIL_RX = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


# ------------------------------------------------------------------ 기초
def _read_lines(path):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()
    except Exception:
        return None


def tr(s, n=200):
    s = _MAIL_RX.sub("<메일>", s)        # 증거 파일은 커밋된다 — 주소를 남기지 않는다
    s = s.replace("|", "\\|")
    return s if len(s) <= n else s[:n] + "…"


def db_rows(root, rel, sql, args=()):
    """읽기 전용 조회 → 행 목록. 실패 = None(미측정 — 0 행과 구분한다)."""
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    try:
        con = sqlite3.connect("file:%s?mode=ro" % p.replace("\\", "/"), uri=True, timeout=5)
        try:
            return con.execute(sql, args).fetchall()
        finally:
            con.close()
    except Exception:
        return None


def is_trading_day(root, d):
    if d.weekday() >= 5:
        return False, "주말"
    try:
        if root not in sys.path:
            sys.path.insert(0, root)
        from config.krx_holidays import is_krx_holiday
        return (False, "KRX 휴장") if is_krx_holiday(d) else (True, "평일")
    except Exception as e:
        return True, "평일(휴장표 미측정: %s)" % e


def prev_trading_day(root, d):
    x = d - timedelta(days=1)
    for _ in range(10):
        if is_trading_day(root, x)[0]:
            return x
        x -= timedelta(days=1)
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


def launcher_logs(root, day):
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


def grep(logs, pat):
    rx = re.compile(pat)
    hits = [(n, ln) for n, lines in logs.items() for ln in lines if rx.search(ln)]
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


def setting_values(root, names):
    lines = _read_lines(os.path.join(root, "config", "settings.py")) or []
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
    return " / ".join(l.strip() for l in (_read_lines(p) or []) if l.strip())[:200]


def win_tasks():
    """Windows 예약작업 상태 — Windows 가 아니면 None(미측정)."""
    if os.name != "nt":
        return None
    out = {}
    for tn in (r"\Sindong", r"\MireukiEODRetrain", r"\Mireuk\Shindong_EOD_1555", r"\Mireuk\Shindong_DailyMail_1810"):
        try:
            p = subprocess.Popen(["schtasks", "/query", "/tn", tn, "/fo", "LIST", "/v"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o, _e = p.communicate(timeout=20)
            txt = o.decode("cp949", "replace")
            if p.returncode != 0:
                out[tn] = "없음"
                continue
            lr = re.search(r"^(?:마지막 결과|Last Result):\s*(.+)$", txt, re.M)
            sch = re.search(r"^(?:예약된 작업 상태|Scheduled Task State):\s*(.+)$", txt, re.M)
            out[tn] = "%s · 마지막 결과 %s" % ((sch.group(1).strip() if sch else "?"),
                                          (lr.group(1).strip() if lr else "?"))
        except Exception as e:
            out[tn] = "조회 실패: %s" % e
    return out


# ------------------------------------------------------------------ 신동 대사
def positions(root, day):
    """trades.db 당일 행 → 포지션 단위(entry_ts·출처 묶음). → (신동, 피터, 그 밖) 또는 (None,)*3."""
    rows = db_rows(root, "data/db/trades.db",
                   "SELECT entry_ts, exit_ts, direction, entry_price, exit_price, quantity, "
                   "net_pnl_krw, exit_reason, entry_source, entry_qty FROM trades "
                   "WHERE entry_ts >= ? AND entry_ts < ? ORDER BY id",
                   (day.isoformat(), (day + timedelta(days=1)).isoformat()))
    if rows is None:
        return None, None, None
    b = {"SHINDONG": {}, "PETER2": {}, "other": {}}
    for r in rows:
        src = r[8] or "?"
        bucket = b[src] if src in b else b["other"]
        p = bucket.setdefault((r[0], src), {"entry_ts": r[0], "src": src, "dir": r[2], "entry_px": r[3],
                                            "legs": 0, "qty": 0, "net": 0.0, "exit_ts": r[1], "exit_px_w": 0.0,
                                            "reasons": [], "entry_qty": r[9]})
        p["legs"] += 1
        p["qty"] += int(r[5] or 0)
        p["net"] += float(r[6] or 0.0)
        p["exit_ts"] = max(p["exit_ts"] or "", r[1] or "")
        p["exit_px_w"] += float(r[4] or 0.0) * int(r[5] or 0)
        if r[7] and r[7] not in p["reasons"]:
            p["reasons"].append(r[7])
    out = []
    for k in ("SHINDONG", "PETER2", "other"):
        lst = list(b[k].values())
        for p in lst:
            p["exit_px"] = (p["exit_px_w"] / p["qty"]) if p["qty"] else None
        out.append(lst)
    return tuple(out)


def shindong_trades(root, day):
    return db_rows(root, "data/db/shindong.db",
                   "SELECT variant, trade_key, side, entry_ts, entry_px, stop_init, status, leg1_reason, "
                   "leg1_exit_ts, leg1_exit_px, net_krw, source, spec_version, leg2_reason, leg2_exit_px "
                   "FROM shindong_trades WHERE trade_date = ? ORDER BY variant, entry_ts", (day.isoformat(),))


def exec_events(root, day):
    p = os.path.join(root, "data", "principal", day.isoformat(), "shindong_exec.jsonl")
    lines = _read_lines(p)
    if lines is None:
        return None
    ev = {}
    for ln in lines:
        try:
            k = json.loads(ln).get("kind") or "?"
        except ValueError:
            k = "(깨진 줄)"
        ev[k] = ev.get(k, 0) + 1
    return ev


def broker_net(root, day):
    rows = db_rows(root, "data/db/trades.db",
                   "SELECT pnl_krw, pnl_net_krw, broker_net_krw, broker_net_source FROM daily_broker_pnl WHERE date = ?",
                   (day.isoformat(),))
    if rows is None:
        return None
    return rows[0] if rows else ()


def principal_now(root):
    try:
        with io.open(os.path.join(root, "data", "trade_principal.json"), encoding="utf-8") as f:
            d = json.load(f)
        return "%s (set_at %s · %s)" % (d.get("principal"), d.get("set_at"), d.get("reason"))
    except Exception as e:
        return "미측정(%s)" % e


def risk_window(root, day):
    rows = db_rows(root, "data/db/shindong.db",
                   "SELECT COUNT(DISTINCT trade_date), COUNT(*) FROM shindong_trades "
                   "WHERE variant='MAIN' AND source='live' AND trade_date>=? AND trade_date<=?",
                   (SWITCH_DAY, day.isoformat()))
    return rows[0] if rows else None


# ------------------------------------------------------------------ 렌더
def build(root, day, phase, pcid, pclabel):
    A = []
    a = A.append
    now = datetime.now()
    ok_td, why_td = is_trading_day(root, day)
    prev = prev_trading_day(root, day)
    logs = today_logs(root, day)
    flags = []
    rank = _PHASE_RANK[phase]

    a("# 신동 일일 점검 증거 — %s / %s / %s" % (pcid, day.isoformat(), phase))
    a("")
    a("- 수집 시각: %s · PC: %s · 거래일: %s (%s) · 직전 거래일: %s"
      % (now.strftime("%Y-%m-%d %H:%M:%S"), pclabel, "예" if ok_td else "아니오", why_td,
         prev.isoformat() if prev else "?"))
    br = CE.run_git(root, ["branch", "--show-current"]).strip()
    head = CE.run_git(root, ["log", "-1", "--format=%h %ci %s"])
    a("- 브랜치: `%s` · HEAD: %s" % (br, tr(head, 140)))
    if br != EXPECT_BRANCH:
        flags.append("브랜치가 `%s` 가 아니다(`%s`) — MW0601 운영 브랜치는 `%s`, `v9-dev` 는 미륵 보존용(CLAUDE.md 「브랜치 역할 (MW0601)」)"
                     % (EXPECT_BRANCH, br, EXPECT_BRANCH))
    lk = os.path.exists(os.path.join(root, ".git", "index.lock"))
    a("- `.git/index.lock`: %s" % ("**있음**" if lk else "없음"))
    a("- 당일 로그 파일: %d개%s" % (len(logs), "" if logs else " — **없음**(휴장이면 정상)"))
    a("- 현재 거래주체 파일: %s" % tr(principal_now(root), 120))
    a("")

    # §1 설정
    keys = ("MIREUK_ENGINE", "PRINCIPAL_ALLOWED", "PRINCIPAL_DEFAULT", "LIGHT_PASS_DRY_RUN",
            "PRINCIPAL_SHINDONG_ENABLED", "SHINDONG_LIVE_QTY", "SHINDONG_STOP_RISK_QTY_ENABLED",
            "SHINDONG_STOP_RISK_PCT", "MAX_CONTRACTS", "LIVE_OPERATING_CAPITAL_KRW", "CB_CONSEC_STOP_LIMIT",
            "PETER2_FOLLOW_MODE", "SHINDONG_REPORT_MAIL_ENABLED", "SHINDONG_DAILY_MAIL_ENABLED")
    sv = setting_values(root, keys)
    a("## 1. 설정 (config/settings.py — 엔진·주체는 기동 시 1회 읽힌다)")
    a("")
    a("| 키 | 값 |")
    a("|---|---|")
    for k in keys:
        a("| `%s` | `%s` |" % (k, tr(sv[k], 60)))
    if sv["MIREUK_ENGINE"].strip("'\"") != "off":
        flags.append("`MIREUK_ENGINE` 이 `off` 가 아니다(`%s`) — 신동 점검 대상이 아니다. 미륵 점검(`mireuk-daily-check`)을 쓸 것"
                     % sv["MIREUK_ENGINE"])
    if "MIREUK" in sv["PRINCIPAL_ALLOWED"] or "SHINDONG" not in sv["PRINCIPAL_ALLOWED"]:
        flags.append("`PRINCIPAL_ALLOWED` 가 신동 주체 구성이 아니다(`%s`)" % sv["PRINCIPAL_ALLOWED"])
    a("")

    # §2 로그 계수
    a("## 2. 로그 계수 (당일 · 중복 기록은 1회로)")
    a("")
    a("| 항목 | 건수 | 기대 | 판정 | 첫 줄 |")
    a("|---|---|---|---|---|")
    pats = [(l, p, e) for (l, p, e, ph) in COUNT_PATTERNS if ph == "all" or rank >= _PHASE_RANK[ph]]
    if phase == "post":
        pats += list(POST_PATTERNS)
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
            flags.append("%s — %d건(기대 %s)" % (re.sub(r"\*\*", "", label), n, exp))
        a("| %s | %d | %s | %s | %s |" % (label, n, exp or "-", verdict, tr(h[0][1][11:], 110) if h else ""))
    lh = dedup(grep(launcher_logs(root, day), r"\[SindongCheck\] result="))
    a("| 런처 입구 점검 `[SindongCheck] result=` (logs/Mireuk_batch) | %d | 1+ | %s | %s |"
      % (len(lh), "정상" if lh and "result=pass" in lh[-1][1] else ("**이상**" if lh else ("**누락**" if ok_td else "휴장")),
         tr(lh[-1][1], 80) if lh else ""))
    if ok_td and (not lh or "result=pass" not in lh[-1][1]):
        flags.append("런처 입구 점검 통과 기록 없음 — `\\Sindong`(start_Sindong.bat) 으로 기동되지 않았을 수 있다")
    errs = dedup(grep(logs, r"\[(?:ERROR|CRITICAL)\]"))
    known = [h for h in errs if any(re.search(k, h[1]) for k in KNOWN_CRITICAL)]
    # HealthPolicy 매분 판정 줄은 한 상태가 수십 줄로 반복된다 — 따로 세고 첫·끝 시각만 남긴다(목록을 덮지 않게)
    health = [h for h in errs if "[Health] level=CRITICAL" in h[1] and h not in known]
    unknown = [h for h in errs if h not in known and h not in health]
    a("")
    a("- ERROR/CRITICAL: 전체 %d줄 · 확정된 고정 경고 %d줄 · HealthPolicy CRITICAL %d줄%s · **그 밖 %d줄**"
      % (len(errs), len(known), len(health),
         (" (%s–%s)" % (health[0][1][11:16], health[-1][1][11:16])) if health else "", len(unknown)))
    for _n, ln in unknown[:12]:
        a("  - `%s`" % tr(ln, 220))
    if len(unknown) > 12:
        a("  - … 외 %d줄" % (len(unknown) - 12))
    a("")

    # §3 장전 축
    a("## 3. 장전 준비 (전일 신동 EOD · 맥점 · 자본 · 동기화 · 예약작업)")
    a("")
    if prev:
        mk = read_marker(root, "data/shindong_eod_done_%s.txt" % prev.strftime("%Y%m%d"))
        a("- 전일(%s) 신동 EOD 마커: %s" % (prev.isoformat(), ("`%s`" % mk) if mk else "**없음**"))
        if prev.isoformat() >= SWITCH_DAY and (not mk or "exit=0" not in mk):
            flags.append("전일 신동 EOD 마커가 없거나 exit≠0 — 08:50 맥점·ATR14 가 낡은 이력으로 산출됐을 수 있다")
    try:
        with io.open(os.path.join(root, "data", "premarket_levels_history.json"), encoding="utf-8") as f:
            ld = json.load(f).get("last_date")
        a("- 맥점 이력 캐시 `last_date`: `%s`%s" % (ld, "" if (prev and ld == prev.isoformat()) or ld == day.isoformat()
                                                  else " — **전 거래일이 아니다**"))
    except Exception as e:
        a("- 맥점 이력 캐시: 미측정(%s)" % e)
    for lab, pat in (("08:50 맥점", r"\[LEVELS 08:50\] ref="), ("09:30 맥점", r"\[LEVELS 09:30\] ref="),
                     ("자본(기준자본·실운영금)", r"\[Capital\] 기준자본="),
                     ("ProfitGuard 원화 임계", r"\[ProfitGuard\] 원화 임계 배율"),
                     ("브로커 동기화", r"\[BrokerSync\] startup sync"),
                     ("피터2 모드", r"\[Peter2\] 모드=")):
        h = dedup(grep(logs, pat))
        a("- %s: %s" % (lab, ("`%s`" % tr(h[-1][1][11:], 170)) if h else "없음"))
    t = win_tasks()
    if t is None:
        a("- 예약작업 상태: 미측정(Windows 가 아님 — Cowork 샌드박스)")
    else:
        for k, v in t.items():
            a("- 예약작업 `%s`: %s" % (k, v))
    a("")

    # §4 신동·피터 거래
    if rank >= 1:
        a("## 4. 신동 거래 — 3원 대사 (포지션 단위)")
        a("")
        ent = dedup(grep(logs, r"\[ShindongExec\] 진입 R"))
        stp = dedup(grep(logs, r"\[ShindongExec\] 손절 "))
        sd_pos, pt_pos, other = positions(root, day)
        mains = shindong_trades(root, day)
        live_main = [r for r in (mains or []) if r[0] == "MAIN" and r[11] == "live"]
        bn = broker_net(root, day)
        ev = exec_events(root, day)
        a("| 원천 | 값 |")
        a("|---|---|")
        a("| 로그 `[ShindongExec] 진입` | %d건 |" % len(ent))
        a("| 집행 기록 `shindong_exec.jsonl` | %s |" % ("없음(미측정)" if ev is None else
                                                    " · ".join("%s %d" % (k, v) for k, v in sorted(ev.items())) or "0줄"))
        a("| `shindong.db` MAIN(live) | %s |" % ("미측정" if mains is None else "%d건" % len(live_main)))
        a("| `trades.db` SHINDONG 포지션 | %s |" % ("미측정" if sd_pos is None else "%d포지션 · net %s원" % (
            len(sd_pos), format(int(round(sum(p["net"] for p in sd_pos))), ","))))
        if pt_pos:
            a("| `trades.db` PETER2 포지션 | %d포지션 · net %s원 |" % (len(pt_pos), format(int(round(sum(p["net"] for p in pt_pos))), ",")))
        if other:
            a("| `trades.db` 그 밖 출처 | %s |" % ", ".join("%s %s원" % (p["src"], format(int(round(p["net"])), ","))
                                                       for p in other))
            if any(p["src"] == "SYSTEM_AUTO" for p in other):
                flags.append("trades.db 에 SYSTEM_AUTO(미륵) 포지션이 있다 — 휴면 중 미륵 진입은 거부돼야 한다(`[MireukOff]` 대조)")
        if bn is None:
            a("| 브로커 net(CpTd6197) | 미측정 |")
        elif not bn:
            a("| 브로커 net(CpTd6197) | 행 없음(15:40 이전이거나 미적재) |")
        else:
            a("| 브로커 net(CpTd6197) | broker_net **%s원**(%s) · 엔진 net %s원 · gross %s원 |"
              % (format(int(bn[2] or 0), ","), bn[3] or "?", format(int(bn[1] or 0), ","), format(int(bn[0] or 0), ",")))
        a("")
        if sd_pos is not None and mains is not None and (len(ent) != len(live_main) or len(sd_pos) != len(live_main)):
            flags.append("3원 대사 불일치 — 로그 진입 %d · shindong.db MAIN live %d · trades.db 신동 포지션 %d"
                         % (len(ent), len(live_main), len(sd_pos)))
        if bn and sd_pos is not None:
            all_net = sum(p["net"] for p in sd_pos) + sum(p["net"] for p in (pt_pos or [])) + sum(p["net"] for p in (other or []))
            diff = (bn[2] or 0) - all_net
            a("- 브로커 net − trades 전 출처 net = %s원%s" % (format(int(round(diff)), ","),
                                                         " (±5,000원 초과 — 확인)" if abs(diff) > 5000 else ""))
            if abs(diff) > 5000:
                flags.append("브로커 net 과 trades net 차 %s원" % format(int(round(diff)), ","))
        a("")
        a("### 4-1. 케이스 표 (재생 규격 vs 실체결)")
        a("")
        a("| 키 | 방향 | 규격 진입 | 실 진입 | 진입 슬립pt(불리+) | 실 수량 | 재생 1차/최종 | 실 청산(가중) | 사유(재생 1차·최종 / 실) | 재생 net | 실 net |")
        a("|---|---|---|---|---|---|---|---|---|---|---|")
        used = set()
        for r in live_main:
            side = int(r[2] or 0)
            m = None
            for i, p in enumerate(sd_pos or []):
                if i in used:
                    continue
                try:
                    dt = abs((datetime.strptime(p["entry_ts"][:19], "%Y-%m-%d %H:%M:%S")
                              - datetime.strptime(str(r[3])[:19], "%Y-%m-%d %H:%M:%S")).total_seconds())
                except ValueError:
                    continue
                if dt <= 180:
                    m = p
                    used.add(i)
                    break
            es = (side * ((m["entry_px"] or 0) - (r[4] or 0))) if m else None
            a("| `%s` | %s | %s | %s | %s | %s | %s / %s | %s | %s·%s / %s | %s | %s |" % (
                r[1], "LONG" if side > 0 else "SHORT", r[4], ("%.2f" % m["entry_px"]) if m else "-",
                ("%+.2f" % es) if es is not None else "-", (m["entry_qty"] or m["qty"]) if m else "-",
                r[9] if r[9] else "-", r[14] if r[14] else "-",
                ("%.2f" % m["exit_px"]) if m and m.get("exit_px") else "-",
                r[7] or "-", r[13] or "-", ",".join(m["reasons"]) if m else "-",
                format(int(round(r[10] or 0)), ","), format(int(round(m["net"])), ",") if m else "-"))
        if not live_main:
            a("| (오늘 MAIN 실거래 없음) | | | | | | | | | | |")
        a("")
        a("- 손절 갱신 로그 %d줄 · 실 수량 1계약 거래는 규격 2레그가 아니라 「1차 목표 전량 익절」로 집행된다(685·711차)" % len(stp))
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
        a("### 4-3. 711차 위험 수량 집행")
        a("")
        for lab, pat in (("위험 기준 축소", r"\[ShindongExec\] 위험 기준 축소"), ("위험수량 미측정", r"위험수량 미측정"),
                         ("증거금 기준 축소", r"\[ShindongExec\] 증거금 기준 축소")):
            h = dedup(grep(logs, pat))
            a("- %s: %d건%s" % (lab, len(h), (" — 예: `%s`" % tr(h[0][1][11:], 150)) if h else ""))
        a("")

    # §5 장후
    if phase == "post":
        a("## 5. 장후 마감·작업")
        a("")
        tok = day.strftime("%Y%m%d")
        for lab, rel in (("신동 EOD 마커(15:55)", "data/shindong_eod_done_%s.txt" % tok),
                         ("daily_close 마커(15:40)", "data/daily_close_done_%s.txt" % tok),
                         ("신동 종합 메일 마커(18:10 — 이 점검 뒤)", "data/shindong_daily_mail_done_%s.txt" % tok)):
            mk = read_marker(root, rel)
            a("- %s: %s" % (lab, ("`%s`" % mk) if mk else "없음"))
        rp = os.path.join(root, "docs", "신동거래", "일일", "신동_일일_%s_%s.md" % (pcid, tok))
        a("- 신동 일일 리포트: %s" % ("`%s`" % os.path.relpath(rp, root) if os.path.exists(rp) else "**없음**"))
        rw = risk_window(root, day)
        if rw:
            a("- 711차 X 1.5%% 판정 창: 전환(%s) 이후 MAIN 실거래 %s거래일 / %d거래일 · %s거래"
              % (SWITCH_DAY, rw[0] or 0, RISK_JUDGE_DAYS, rw[1] or 0))
        a("")

    # §6 미결 관측
    a("## 6. 미결 관측 · 장중 확인 항목 (NEXT_TODO 상단)")
    a("")
    nt = (_read_lines(os.path.join(root, "dev_memory", "NEXT_TODO.md")) or [])
    nt = nt[-NEXT_TODO_SCAN_LINES:]           # v9 NEXT_TODO 는 최신 절이 **아래**에 쌓인다
    open_items = [l for l in nt if l.lstrip().startswith("- [ ]")]
    tagged = {t: [l for l in open_items if t in l] for t in ("[로그]", "[경보]", "[화면]")}
    untag_intra = [l for l in open_items if "장중" in l and not any(t in l for t in tagged)]
    a("- NEXT_TODO 끝 %d줄의 열린 항목 %d건 · 태그 `[로그]` %d · `[경보]` %d · `[화면]` %d · **태그 없는 「장중」 항목 %d건**"
      % (NEXT_TODO_SCAN_LINES, len(open_items), len(tagged["[로그]"]), len(tagged["[경보]"]), len(tagged["[화면]"]),
         len(untag_intra)))
    for l in (tagged["[로그]"] + tagged["[경보]"] + tagged["[화면]"] + untag_intra)[:15]:
        a("  - %s" % tr(l.strip(), 170))
    a("")

    # §7 git
    a("## 7. 오늘 커밋")
    a("")
    lg = CE.run_git(root, ["log", "--format=%ci %h %s", "--since=%s 00:00" % day.isoformat(),
                           "--until=%s 00:00" % (day + timedelta(days=1)).isoformat()])
    for l in (lg.splitlines() if lg else [])[:20]:
        a("- %s" % tr(l, 160))
    if not lg:
        a("- 없음")
    a("")

    head_ = ["## 0. 자동 적신호 (출발점이지 결론이 아니다)", ""]
    if not ok_td:
        head_.append("- 휴장일(%s) — 당일 로그·거래 부재에서 파생되는 항목은 결함이 아니다" % why_td)
    head_ += ["- %s" % f for f in flags] or ["- 없음"]
    head_.append("")
    i = A.index("## 1. 설정 (config/settings.py — 엔진·주체는 기동 시 1회 읽힌다)")
    return "\n".join(A[:i] + head_ + A[i:]) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="신동 주체 일일 점검 증거 수집기 (MW0601 Sindong2-V4)")
    ap.add_argument("--phase", choices=("pre", "intra", "post"), required=True)
    ap.add_argument("--date", default=None)
    ap.add_argument("--pc", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--out-auto", action="store_true")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if a.pc:
        CE.set_pc_override(a.pc)
    root = CE.find_repo_root(os.getcwd()) or CE.find_repo_root(_HERE)
    day = datetime.strptime(a.date, "%Y-%m-%d").date() if a.date else datetime.now().date()
    pcid, pclabel = CE.pc_id()
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
