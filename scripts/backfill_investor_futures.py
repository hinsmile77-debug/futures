# scripts/backfill_investor_futures.py
"""[MW0601 613차] `raw_investor_futures` 과거 구간 백필 — 로그압축 역변환.

613차가 선물 투자자 수급 원값 보존을 시작했지만, 그 전 구간은 **원값이 존재하지
않는다.** 다만 `raw_features` 에 같은 값의 **로그압축 피처**가 남아 있고, 그
압축이 정확히 가역이라 계약수 축은 되살릴 수 있다.

    features/feature_builder.py:  f = sign(x) * log1p(|x| / 1000)
    역변환:                       x = sign(f) * expm1(|f|) * 1000

되살릴 수 없는 것 — **금액 축(백만원)**. `raw_features` 에 `*_amt_mn` 이 없다.
그래서 백필 행에는 `_net_qty` 키만 실린다. 없는 것을 0 으로 채우지 않는다
(계측 4원칙 ②). 미결제약정도 백필하지 않는다 — `raw_candles.oi` 가 과거 전
구간에 이미 있고, provider 가 그쪽을 1차 원천으로 읽는다.

모든 백필 행은 `src` 에 표기된다 — **실측과 구분되지 않으면 안 된다.**
    · `derived`    — `*_measured` 플래그로 측정 확인됨 (2026-09-14~)
    · `derived_nf` — 플래그가 없던 구간(그 전). 비영값만 되살렸고 **측정 여부는
                     추론**이다. 정확히 0.0 인 분은 미측정과 구분 불가라 버렸다.

사용:
    python scripts/backfill_investor_futures.py                 # 전 구간
    python scripts/backfill_investor_futures.py --days 30
    python scripts/backfill_investor_futures.py --dry-run
"""
from __future__ import annotations

# 🔴 numpy 보다 먼저 — BLAS delay-load 실패로 프로세스가 즉사한다(537차).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dll_bootstrap import ensure_conda_dll_path                 # noqa: E402

ensure_conda_dll_path()

import argparse                                                       # noqa: E402
import datetime                                                       # noqa: E402
import json                                                           # noqa: E402
import math                                                           # noqa: E402
import sqlite3                                                        # noqa: E402

from utils.analysis_db import guard_intraday                          # noqa: E402

RAW_DB = os.path.join("data", "db", "raw_data.db")

# `raw_features` 키 → 저장 키. 이름에 단위를 박는다(계측 4원칙 ①).
_MAP = (
    ("foreign_futures_net",     "foreign_net_qty"),
    ("retail_futures_net",      "retail_net_qty"),
    ("institution_futures_net", "institution_net_qty"),
)


# 🔴 `raw_features` 에는 **압축 이전 시대**가 섞여 있다(실측: 2026-06-02·04·05·08
#    4거래일은 원값 그대로 — 최대 541,664). 그 값을 역변환하면 expm1 이 넘쳐
#    OverflowError 가 난다(실행 중 실제로 났다).
#    압축된 값은 |log1p(|x|/1000)| 이라 현실적 순매수(|x| ≤ 100만)에서 **7 을 넘지
#    않는다.** 그래서 하루 최댓값이 이 문턱을 넘으면 그날은 원값 시대다.
#    ⚠ 행 단위로 판정하면 안 된다 — 원값 시대의 작은 값(3계약)이 압축값으로
#      오인돼 3,000 계약으로 부풀려진다. **판정은 반드시 일자 단위다.**
_COMPRESSED_ABS_MAX = 15.0


def _inv_log(v: float) -> int:
    """sign(x)·log1p(|x|/1000) 의 역변환. 왕복 오차는 정수 반올림 안쪽이다."""
    return int(round(math.copysign(math.expm1(abs(float(v))) * 1000.0, v)))


def _scan_compression_era(con, sql, params):
    """일자별 `foreign_futures_net` 최댓값으로 압축 시대 여부를 판정한다.

    Returns: {"YYYY-MM-DD": True(압축) | False(원값)}
    """
    era = {}
    for ts, fj in con.execute(sql, params):
        try:
            f = json.loads(fj)
        except Exception:                                       # noqa: BLE001
            continue
        day = ts[:10]
        for src_key, _dst in _MAP:
            v = f.get(src_key)
            if v is None:
                continue
            a = abs(float(v))
            if a > era.get(day, 0.0):
                era[day] = a
    return dict((d, a <= _COMPRESSED_ABS_MAX) for d, a in era.items())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0,
                    help="최근 N일만 (0=전 구간)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db", default=RAW_DB)
    args = ap.parse_args()

    # 라이브 DB 전수 스캔이다 — 장중이면 CB⑤ 를 부른다(456차).
    guard_intraday("backfill_investor_futures")

    lo = ""
    if args.days > 0:
        lo = (datetime.date.today()
              - datetime.timedelta(days=args.days)).isoformat()

    con = sqlite3.connect(args.db, timeout=30.0)
    con.execute("PRAGMA journal_mode=WAL")
    # 613차 이전 DB 에는 테이블이 없다 — 여기서 만들지 않고 정식 경로를 태운다.
    try:
        con.execute("SELECT 1 FROM raw_investor_futures LIMIT 1")
    except sqlite3.Error:
        con.close()
        print("raw_investor_futures 테이블이 없다. "
              "먼저 utils/db_utils.init_raw_data_db() 를 태울 것(미륵이 기동 1회면 된다).")
        return 2

    sql = "SELECT ts, features FROM raw_features"
    params = ()
    if lo:
        sql += " WHERE ts>=?"
        params = (lo,)
    sql += " ORDER BY ts"

    era = _scan_compression_era(con, sql, params)
    n_raw_era = sum(1 for v in era.values() if not v)
    if n_raw_era:
        print("압축 이전 시대 %d거래일 감지 — 그 날들은 역변환 없이 원값을 쓴다"
              % n_raw_era)

    n_scan = n_write = n_skip_measured = n_skip_exist = 0
    rows = []
    # 이미 있는 ts 는 건드리지 않는다 — **실측(live) 을 파생으로 덮으면 안 된다.**
    have = set(r[0] for r in con.execute("SELECT ts FROM raw_investor_futures"))

    for ts, fj in con.execute(sql, params):
        n_scan += 1
        if ts in have:
            n_skip_exist += 1
            continue
        try:
            f = json.loads(fj)
        except Exception:                                       # noqa: BLE001
            continue
        fields = {}
        inferred = False
        for src_key, dst_key in _MAP:
            v = f.get(src_key)
            if v is None:
                continue
            flag_key = src_key + "_measured"
            if flag_key in f:
                # 🔴 플래그가 있으면 그것만 믿는다. 0 은 "그 분에 원천이 안 왔다"
                #    이지 "순매수 0계약"이 아니다 — 그걸 0 으로 쓰면 451차의
                #    유령 피처를 백필로 재현하는 꼴이다.
                if float(f.get(flag_key) or 0.0) <= 0.0:
                    continue
            else:
                # 🔴 `*_measured` 는 2026-09-14 부터만 기록된다(612차). 그 전 행은
                #    측정 여부를 **알 수 없다.** 다만 값이 정확히 0.0 이 아니면
                #    원천이 준 값일 수밖에 없다(이월 폴백의 초기값이 0 이다).
                #    그래서 비영값만 되살리고 `src` 를 달리 찍어 **추론이었음을
                #    남긴다** — 0.0 은 판별 불가라 버린다(계측 4원칙 ②·④).
                if float(v) == 0.0:
                    continue
                inferred = True
            fields[dst_key] = (_inv_log(v) if era.get(ts[:10], True)
                               else int(round(float(v))))
        if not fields:
            n_skip_measured += 1
            continue
        rows.append((ts, json.dumps(fields, ensure_ascii=False, sort_keys=True),
                     "derived_nf" if inferred else "derived"))
        n_write += 1

    if args.dry_run:
        print("[dry-run] 스캔 %d · 기록예정 %d · 기존 %d · 미측정 %d"
              % (n_scan, n_write, n_skip_exist, n_skip_measured))
        if rows:
            print("  첫 행:", rows[0])
            print("  끝 행:", rows[-1])
        con.close()
        return 0

    con.executemany(
        "INSERT OR IGNORE INTO raw_investor_futures (ts, fields, src) "
        "VALUES (?, ?, ?)", rows)
    con.commit()
    con.close()
    n_nf = sum(1 for r in rows if r[2] == "derived_nf")
    print("백필 완료 — 스캔 %d · 기록 %d(derived %d / derived_nf %d) · "
          "기존 %d · 판별불가 %d"
          % (n_scan, n_write, n_write - n_nf, n_nf, n_skip_exist,
             n_skip_measured))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
