"""
옵션 만기북(먼스리 · (목)위클리 · (월)위클리) 행사가별 GEX · 감마월 — [MW0601 623차]

왜 따로 있나
------------
`option_chain_worker` 의 `opt_gex_bn`/`opt_gex_sign` 은 **먼스리 한 북의 합계**이고,
`opt_gex_sign` 은 CORE 피처다. 거기에 위클리를 섞으면 피처의 뜻이 바뀐다(317차
train/serve skew 원칙). 그래서 이 모듈은 **차트 표시용 병행 경로**다 — 학습 피처에
들어가지 않고, 먼스리 합계도 바꾸지 않는다.

위클리 코드는 어디서 오나 (2026-09-23 실측)
--------------------------------------------
- `CpUtil.CpOptionCode` 는 **먼스리 전용**이다(4,600종목 = KIS 마스터 type 5/6).
  레지스트리의 `CpCodeMgr` 에도 위클리 목록 메서드가 없다(메서드 전수 확인).
- 행사가 인덱스가 **상장 순서**라 규칙으로 조립할 수 없다
  (먼스리 2610: 1117.5=`A49` · 1120=`A48` · 1122.5=`A50`, 같은 1120 이 위클리는 `A49`).
- ⇒ **KIS 종목 마스터**(공개 파일, 매일 갱신)를 목록 원천으로 쓴다.
  **Cybos 코드 = KRX 표준코드[3:11]** — 먼스리 4,602종목 전수 대조 **4,602/4,602 일치**.
  그 코드를 `Dscbo1.OptionMst` 에 넣으면 위클리도 OI·감마가 온다
  (`scripts/probe_weekly_option_mst.py`, 목위클 1120C OI 2,787 · 감마 0.92%).

상품종류(KIS 마스터 1열): 5/6 먼스리 C/P · L/M (목)위클리 C/P · N/O (월)위클리 C/P
"""
from __future__ import annotations

import calendar
import datetime as _dt
import io
import logging
import os
import re
import sqlite3
import urllib.request
import zipfile
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("OPTIONS")

MASTER_URL = "https://new.real.download.dws.co.kr/common/master/fo_idx_code_mts.mst.zip"
MASTER_NAME = "fo_idx_code_mts.mst"

BOOKS = ("monthly", "weekly_thu", "weekly_mon")
BOOK_LABEL = {"monthly": "먼스리", "weekly_thu": "목위클리", "weekly_mon": "월위클리"}
_PTYPES = {
    "monthly":    ("5", "6"),
    "weekly_thu": ("L", "M"),
    "weekly_mon": ("N", "O"),
}
_MONTHLY_RE = re.compile(r"[CP]\s+(\d{6})\s")          # "C 202610   745.0"
_WEEKLY_RE = re.compile(r"[CP]\s+(\d{4}W\d)\s")         # "위클리M C 2609W4 970.0"

OPTION_MULTIPLIER = 250_000
GEX_BN = 1e9


# ── 마스터 ────────────────────────────────────────────────────────────

def cybos_code(std_code: str) -> str:
    """KRX 표준코드 → Cybos 옵션코드. `KR4B09FEA490` → `B09FEA49`."""
    return std_code[3:11]


def parse_master_text(text: str) -> List[Dict]:
    """마스터 본문 → KOSPI200 옵션 3북 행만. 행: book·cp·label·strike·code."""
    out: List[Dict] = []
    for line in text.splitlines():
        f = line.split("|")
        if len(f) < 9 or f[8].strip() != "KOSPI200":
            continue
        ptype = f[0].strip()
        book = cp = None
        for b, (c_t, p_t) in _PTYPES.items():
            if ptype == c_t:
                book, cp = b, "C"
            elif ptype == p_t:
                book, cp = b, "P"
        if book is None:
            continue
        m = (_MONTHLY_RE if book == "monthly" else _WEEKLY_RE).search(f[3] + " ")
        if not m:
            continue
        label = m.group(1)
        if book == "monthly":
            label = label[2:]                       # 202610 → 2610 (CpOptionCode ym 과 같은 꼴)
        try:
            strike = float(f[5])
        except ValueError:
            continue
        out.append({"book": book, "cp": cp, "label": label,
                    "strike": strike, "code": cybos_code(f[2].strip())})
    return out


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> _dt.date:
    d = _dt.date(year, month, 1)
    d += _dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + _dt.timedelta(weeks=n - 1)


def nominal_expiry(book: str, label: str) -> Optional[_dt.date]:
    """라벨의 **명목** 만기일. 휴장으로 당겨진 만기는 반영하지 못한다.

    ⚠ 예: 2609W4 (목)위클리 명목 만기는 9/24(목)이지만 그날이 추석 휴장이다.
      그래서 이 값은 「가장 가까운 북 고르기」와 표시에만 쓴다 — 만기 판정의
      1차 근거는 **마스터에 아직 상장돼 있는가**다(만기 지난 종목은 다음날 빠진다).
    """
    try:
        year, month = 2000 + int(label[:2]), int(label[2:4])
        if book == "monthly":
            return _nth_weekday(year, month, 3, 2)          # 둘째 목요일
        n = int(label[5:])
        return _nth_weekday(year, month, 3 if book == "weekly_thu" else 0, n)
    except (ValueError, IndexError):
        return None


def select_nearest(rows: List[Dict], book: str,
                   today: _dt.date) -> Tuple[Optional[str], List[Dict]]:
    """그 북에서 만기가 가장 가까운(오늘 이후) 라벨과 그 라벨의 행."""
    labels = sorted({r["label"] for r in rows if r["book"] == book})
    for lab in labels:
        exp = nominal_expiry(book, lab)
        if exp is None or exp >= today:
            return lab, [r for r in rows if r["book"] == book and r["label"] == lab]
    return None, []


def load_master(cache_dir: str, today: _dt.date, fallback_paths=(),
                timeout: float = 20.0) -> Tuple[List[Dict], str]:
    """오늘자 마스터를 확보해 파싱한다. 반환 (행, 출처).

    출처: `download` · `cache`(오늘 이미 받음) · `stale:<경로>`(폴백 — 경고 대상).
    하루 1회만 내려받는다(`<cache_dir>/<MASTER_NAME>.date` 에 받은 날짜 기록).
    """
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, MASTER_NAME)
    stamp = path + ".date"
    today_s = today.isoformat()
    try:
        with open(stamp, "r", encoding="ascii") as f:
            got = f.read().strip()
    except OSError:
        got = ""
    src = "cache"
    if got != today_s or not os.path.exists(path):
        try:
            with urllib.request.urlopen(MASTER_URL, timeout=timeout) as r:
                blob = r.read()
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                data = zf.read(MASTER_NAME)
            with open(path, "wb") as f:
                f.write(data)
            with open(stamp, "w", encoding="ascii") as f:
                f.write(today_s)
            src = "download"
        except Exception as exc:
            logger.warning("[OptionBook] 마스터 다운로드 실패: %s — 폴백 시도", exc)
            cands = ([path] if os.path.exists(path) else []) + [p for p in fallback_paths if p and os.path.exists(p)]
            if not cands:
                return [], "none"
            # 가장 최근 파일을 쓴다 — 어느 쪽이 더 신선한지 모르므로 mtime 으로 고른다.
            path = max(cands, key=os.path.getmtime)
            src = "stale:%s" % path
    with open(path, "rb") as f:
        text = f.read().decode("cp949", errors="replace")
    return parse_master_text(text), src


# ── 계산 ──────────────────────────────────────────────────────────────

def filter_atm(rows: List[Dict], spot: float, window: float) -> List[Dict]:
    return [r for r in rows if spot - window <= r["strike"] <= spot + window]


def compute_book(snaps: List[Dict], spot: float) -> Tuple[Dict, List[Dict]]:
    """행사가별 GEX 와 감마월.

    snaps 행: cp('C'/'P')·strike·code·oi·gamma(실수 — ÷100 끝난 값)·error(선택).
    단위는 `option_chain_worker._compute_gex` 와 **같다**(γ·OI·승수·S / 1e9) —
    그래서 먼스리 북의 `gex_bn` 은 `opt_gex_bn` 과 같은 값이 나와야 한다(테스트로 고정).

    감마월: 콜월 = 콜 GEX 최대 행사가, 풋월 = 풋 GEX 최대 행사가.
    유효 관측이 0이면 합계·월을 **None** 으로 둔다(계측 4원칙 ② — 미측정 ≠ 0).
    """
    by_strike: Dict[float, Dict] = {}
    n_valid = 0
    for s in snaps:
        k = float(s["strike"])
        row = by_strike.setdefault(k, {"strike": k, "call_oi": None, "put_oi": None,
                                       "call_gamma": None, "put_gamma": None,
                                       "call_gex_bn": None, "put_gex_bn": None})
        if s.get("error"):
            continue
        n_valid += 1
        oi, g = int(s.get("oi") or 0), float(s.get("gamma") or 0.0)
        gex = g * oi * OPTION_MULTIPLIER * spot / GEX_BN
        side = "call" if s["cp"] == "C" else "put"
        row[side + "_oi"], row[side + "_gamma"], row[side + "_gex_bn"] = oi, g, gex
    strikes = [by_strike[k] for k in sorted(by_strike)]
    summary = {"n_target": len(snaps), "n_valid": n_valid,
               "gex_bn": None, "call_gex_bn": None, "put_gex_bn": None,
               "call_wall": None, "put_wall": None,
               "call_wall_gex_bn": None, "put_wall_gex_bn": None}
    if n_valid == 0:
        return summary, strikes
    c = [r for r in strikes if r["call_gex_bn"] is not None]
    p = [r for r in strikes if r["put_gex_bn"] is not None]
    summary["call_gex_bn"] = sum(r["call_gex_bn"] for r in c)
    summary["put_gex_bn"] = sum(r["put_gex_bn"] for r in p)
    summary["gex_bn"] = summary["call_gex_bn"] - summary["put_gex_bn"]
    if c:
        top = max(c, key=lambda r: r["call_gex_bn"])
        if top["call_gex_bn"] > 0:
            summary["call_wall"], summary["call_wall_gex_bn"] = top["strike"], top["call_gex_bn"]
    if p:
        top = max(p, key=lambda r: r["put_gex_bn"])
        if top["put_gex_bn"] > 0:
            summary["put_wall"], summary["put_wall_gex_bn"] = top["strike"], top["put_gex_bn"]
    return summary, strikes


# ── 저장 ──────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS option_book_snap (
    ts TEXT NOT NULL, book TEXT NOT NULL, label TEXT, expiry TEXT,
    spot REAL, n_target INTEGER, n_valid INTEGER,
    gex_bn REAL, call_gex_bn REAL, put_gex_bn REAL,
    call_wall REAL, put_wall REAL, call_wall_gex_bn REAL, put_wall_gex_bn REAL,
    master_src TEXT, elapsed_ms INTEGER,
    PRIMARY KEY (ts, book)
);
CREATE TABLE IF NOT EXISTS option_book_strike (
    ts TEXT NOT NULL, book TEXT NOT NULL, strike REAL NOT NULL,
    call_oi INTEGER, put_oi INTEGER, call_gamma REAL, put_gamma REAL,
    call_gex_bn REAL, put_gex_bn REAL,
    PRIMARY KEY (ts, book, strike)
);
"""
_SNAP_COLS = ("label", "expiry", "spot", "n_target", "n_valid", "gex_bn", "call_gex_bn",
              "put_gex_bn", "call_wall", "put_wall", "call_wall_gex_bn", "put_wall_gex_bn",
              "master_src", "elapsed_ms")
_STRIKE_COLS = ("strike", "call_oi", "put_oi", "call_gamma", "put_gamma",
                "call_gex_bn", "put_gex_bn")


def _connect(db_path: str) -> sqlite3.Connection:
    d = os.path.dirname(db_path)
    if d:
        os.makedirs(d, exist_ok=True)
    con = sqlite3.connect(db_path, timeout=5.0)
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(_SCHEMA)
    return con


def save_books(db_path: str, ts: str, books: Dict[str, Dict]) -> None:
    """books[book] = {"summary": {...}, "strikes": [...]} — summary 에 label·expiry·spot 등."""
    con = _connect(db_path)
    try:
        with con:
            for book, b in books.items():
                s = b["summary"]
                con.execute(
                    "INSERT OR REPLACE INTO option_book_snap (ts, book, %s) VALUES (?, ?, %s)"
                    % (", ".join(_SNAP_COLS), ", ".join("?" * len(_SNAP_COLS))),
                    [ts, book] + [s.get(c) for c in _SNAP_COLS])
                con.executemany(
                    "INSERT OR REPLACE INTO option_book_strike (ts, book, %s) VALUES (?, ?, %s)"
                    % (", ".join(_STRIKE_COLS), ", ".join("?" * len(_STRIKE_COLS))),
                    [[ts, book] + [r.get(c) for c in _STRIKE_COLS] for r in b["strikes"]])
    finally:
        con.close()


def load_day_snaps(db_path: str, date_str: str) -> Dict[str, List[Dict]]:
    """그 날짜의 북별 스냅샷 시계열 — 차트용. 파일이 없으면 빈 dict."""
    if not os.path.exists(db_path):
        return {}
    con = sqlite3.connect("file:%s?mode=ro" % db_path, uri=True, timeout=2.0)
    try:
        cur = con.execute(
            "SELECT ts, book, %s FROM option_book_snap WHERE ts LIKE ? ORDER BY ts"
            % ", ".join(_SNAP_COLS), (date_str + "%",))
        out: Dict[str, List[Dict]] = {}
        for row in cur.fetchall():
            d = dict(zip(("ts", "book") + _SNAP_COLS, row))
            out.setdefault(d["book"], []).append(d)
        return out
    except sqlite3.Error:
        return {}
    finally:
        con.close()
