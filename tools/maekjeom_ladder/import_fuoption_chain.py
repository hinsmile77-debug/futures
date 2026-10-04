# -*- coding: utf-8 -*-
"""메시아(fuoption) KIS 옵션 체인 parquet → 사다리용 행사가 OI DB (option_book_fuo.db).

[MW0601 656차 / 2026-10-04]

왜
  미륵이 `option_book.db`(행사가별 OI·감마)는 2026-09-23 14:34 에 수집을 시작했다(종일은 09-28부터).
  그 전 날짜는 사다리의 OI 히트맵·옵션층·벽·베이시스가 비었다. 메시아가 2026-08-05 부터
  같은 재료(행사가별 미결제약정 `hts_otst_stpl_qty` · 감마 `gama` · KOSPI200 `idx3_bstp_nmix_prpr`)를
  약 5분 간격으로 쌓아 두었으므로 그것을 미륵이 스키마로 옮긴다.

정의 — 미륵이 `collection/options/option_book.py` 와 같게
  콜월 = 콜 GEX(γ·OI·승수·S) 최대 행사가, 풋월 = 풋 GEX 최대 행사가. 월 위치는 승수·S 와 무관
  (같은 시각 같은 S·승수라 argmax 가 같다)하므로 γ·OI 로 정한다.
  스냅샷 시각 = 수집 주기를 5분 칸으로 내림(종목마다 몇 초씩 다르게 폴링되기 때문). 칸 안에서는
  종목별 마지막 관측을 쓴다.

⚠ 메시아 체인은 ATM 주변 창(약 26–37 행사가)만 담는다 — 미륵이 북(28–37 행사가)과 폭이 비슷하다.
⚠ pyarrow 가 있는 환경에서 돈다(streamlit_env_modern). 차트 서버는 결과 SQLite 만 읽는다.

사용
  C:\\Users\\82108\\anaconda3\\envs\\streamlit_env_modern\\python.exe tools\\maekjeom_ladder\\import_fuoption_chain.py
  (이미 들어간 날짜는 다시 덮어쓴다 — 멱등)
"""
import glob
import os
import sqlite3
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(os.path.dirname(ROOT), "fuoption", "data", "option_chain")
DST = os.path.join(ROOT, "data", "db", "option_book_fuo.db")
BOOK = {"regular": "monthly", "weekly_mon": "weekly_mon", "weekly_thu": "weekly_thu"}
COLS = ["ts_kst", "symbol", "option_type", "strike", "expiry_date", "hts_otst_stpl_qty", "gama", "idx3_bstp_nmix_prpr"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS option_book_snap (
    ts TEXT NOT NULL, book TEXT NOT NULL, spot REAL, n_valid INTEGER, expiry TEXT,
    call_wall REAL, put_wall REAL, src TEXT, PRIMARY KEY (ts, book));
CREATE TABLE IF NOT EXISTS option_book_strike (
    ts TEXT NOT NULL, book TEXT NOT NULL, strike REAL NOT NULL, call_oi INTEGER, put_oi INTEGER,
    PRIMARY KEY (ts, book, strike));
"""


def _expiry(df):
    """만기 — 초기 파일엔 expiry_date 가 없어 futs_last_tr_date(YYYYMMDD)로 대신한다."""
    if "expiry_date" in df.columns and df.expiry_date.notna().any():
        return df.expiry_date.astype(str)
    if "futs_last_tr_date" in df.columns:
        v = df.futs_last_tr_date.dropna().astype("int64").astype(str)
        return (v.str[:4] + "-" + v.str[4:6] + "-" + v.str[6:8]).reindex(df.index)
    return pd.Series([None] * len(df), index=df.index)


def convert(path, book):
    import pyarrow.parquet as pq
    have = set(pq.read_schema(path).names)
    need = {"ts_kst", "symbol", "option_type", "strike", "hts_otst_stpl_qty", "gama"}
    if not need <= have:
        print("  건너뜀 %s — 필수 열 없음 %s" % (os.path.basename(path), sorted(need - have)))
        return [], []
    df = pd.read_parquet(path, columns=[c for c in COLS + ["futs_last_tr_date"] if c in have])
    if df.empty:
        return [], []
    df["expiry_date"] = _expiry(df)
    if "idx3_bstp_nmix_prpr" not in df.columns:
        df["idx3_bstp_nmix_prpr"] = float("nan")
    t = df.ts_kst.dt.tz_convert("Asia/Seoul")
    day = t.dt.strftime("%Y-%m-%d").iloc[0]
    m = t.dt.hour * 60 + t.dt.minute
    df = df.assign(bucket=(m // 5) * 5, t=t).sort_values("t")
    snaps, strikes = [], []
    for b, g in df.groupby("bucket"):
        last = g.groupby("symbol").tail(1)
        ts = "%s %02d:%02d:00" % (day, b // 60, b % 60)
        piv = {}
        for _, r in last.iterrows():
            k = float(r.strike)
            row = piv.setdefault(k, {"C": None, "P": None, "gC": 0.0, "gP": 0.0})
            oi = None if pd.isna(r.hts_otst_stpl_qty) else int(r.hts_otst_stpl_qty)
            row[r.option_type] = oi
            row["g" + r.option_type] = float(r.gama or 0.0) * (oi or 0)
        if not piv:
            continue
        cw = max(piv, key=lambda k: piv[k]["gC"]); pw = max(piv, key=lambda k: piv[k]["gP"])
        spot = float(g.idx3_bstp_nmix_prpr.median()) if g.idx3_bstp_nmix_prpr.notna().any() else None
        snaps.append((ts, book, spot, int(len(last)), str(last.expiry_date.iloc[-1]),
                      cw if piv[cw]["gC"] > 0 else None, pw if piv[pw]["gP"] > 0 else None, "fuoption/" + os.path.basename(path)))
        strikes += [(ts, book, k, v["C"], v["P"]) for k, v in sorted(piv.items())]
    return snaps, strikes


def main():
    for s in ("stdout", "stderr"):
        try:
            getattr(sys, s).reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    con = sqlite3.connect(DST)
    con.executescript(SCHEMA)
    total = 0
    for src_dir, book in BOOK.items():
        for f in sorted(glob.glob(os.path.join(SRC, src_dir, "*.parquet"))):
            day = os.path.basename(f)[:10]
            snaps, strikes = convert(f, book)
            with con:
                con.execute("DELETE FROM option_book_snap WHERE ts LIKE ? AND book=?", (day + "%", book))
                con.execute("DELETE FROM option_book_strike WHERE ts LIKE ? AND book=?", (day + "%", book))
                con.executemany("INSERT INTO option_book_snap VALUES (?,?,?,?,?,?,?,?)", snaps)
                con.executemany("INSERT INTO option_book_strike VALUES (?,?,?,?,?)", strikes)
            total += len(strikes)
            print("%s %-10s 스냅샷 %3d · 행사가행 %5d" % (day, book, len(snaps), len(strikes)))
    con.close()
    print("완료 — %s (행사가행 %d)" % (DST, total))


if __name__ == "__main__":
    main()
