# -*- coding: utf-8 -*-
"""[9842] 당일 순매수(_D)를 기간 보유(_P) 차분으로 복원한다.

[MW0601 656차 / 2026-10-04]

근거 — 2026-10-02 실측(계약 단위 내보내기)
    P(10/2) − P(10/1) == D(10/2)  : 341 행사가 × 8칸 = 2,728칸 **전부 정확 일치**
  즉 「기간 보유계약」은 당일 순매수의 누적이고, 전 거래일 _P 를 빼면 그날 _D 가 된다.

안전장치
  1. 진짜 _D 가 있는 날은 덮어쓰지 않는다 — 대신 그날을 **자기검증**에 쓴다.
     자기검증에서 한 칸이라도 어긋나면 **아무것도 쓰지 않는다**(--force 로만 무시).
  2. 두 _P 의 머리행·행사가 목록이 다르면 그날은 건너뛴다(사유 출력).
  3. 직전 거래일은 KRX 달력(utils.time_utils.is_trading_day)으로 찾는다. 그날 _P 가
     없으면 건너뛴다 — 더 이전 _P 로 빼면 여러 날 합계가 하루치로 위장된다.
  4. 생성 파일 머리에 HTML 주석으로, 폴더의 `_derived_D.json` 에 원천·검증 결과를 남긴다.

사용
  python tools/maekjeom_ladder/derive_9842_daily.py --dry-run
  python tools/maekjeom_ladder/derive_9842_daily.py
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ladder_data as L  # noqa: E402

sys.path.insert(0, L.ROOT)


def _cells(fn):
    p = os.path.join(L.DOCS_9842, fn)
    rows = L._read_xlsx(p) if fn.endswith(".xlsx") else L._read_xls_html(p)
    head = [str(h or "").strip() for h in rows[0][:11]]
    body = [[str(x or "").strip() for x in r[:11]] for r in rows[1:] if len(r) >= 11]
    return head, body


def _prev_trading_day(d):
    from utils.time_utils import is_trading_day
    x = d - _dt.timedelta(days=1)
    for _ in range(15):
        if is_trading_day(_dt.datetime.combine(x, _dt.time(12))):
            return x
        x -= _dt.timedelta(days=1)
    return None


def _fmt(v):
    return str(int(v)) if float(v).is_integer() else ("%.2f" % v).rstrip("0").rstrip(".")


def derive(p_today, p_prev):
    """→ (head, rows) 또는 예외. 행 순서는 오늘 _P 를 따른다."""
    h1, b1 = _cells(p_today)
    h0, b0 = _cells(p_prev)
    if h1 != h0:
        raise ValueError("머리행 다름: %s vs %s" % (h1, h0))
    num_cols = [i for i, h in enumerate(h1) if h not in ("현재가", "행사가")]
    prev = {r[5]: r for r in b0}
    if [r[5] for r in b1] != [r[5] for r in b0]:
        raise ValueError("행사가 목록·순서 다름 (%d vs %d행)" % (len(b1), len(b0)))
    out = []
    for r in b1:
        q = prev[r[5]]
        row = list(r)
        for i in num_cols:
            a, b = L._num(r[i]), L._num(q[i])
            if a is None or b is None:
                raise ValueError("숫자 아님: 행사가 %s 열 %s (%r, %r)" % (r[5], h1[i], r[i], q[i]))
            row[i] = _fmt(a - b)
        out.append(row)
    return h1, out


def write_xls(path, head, rows, note):
    td = "<td style='text-align:center'>%s</td>"
    lines = ["<head><META HTTP-EQUIV='Content-Type' CONTENT=\"text/html; charset=euc-kr\"></head>",
             "<!-- %s -->" % note, "<body>", "<table cellspacing=0 border=1>",
             "<tr>%s</tr>" % "".join(td % h for h in head)]
    lines += ["<tr>%s</tr>" % "".join(td % c for c in r) for r in rows]
    lines += ["</table>", "</body>", ""]
    # 인코딩을 **먼저** 끝내고 파일을 연다 — 열고 나서 실패하면 0바이트 파일이 남아
    # 다음 실행에서 「진짜 _D」로 오인된다(2026-10-04 실제로 났다).
    data = "\r\n".join(lines).encode("euc-kr")
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="자기검증 불일치를 무시한다(권장하지 않음)")
    a = ap.parse_args()
    for s in ("stdout", "stderr"):
        try:
            getattr(sys, s).reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    files = L._list_9842_files()
    P = {f["date"]: f["fn"] for f in files if f["mode"] == "P"}
    Dreal = {f["date"]: f["fn"] for f in files if f["mode"] == "D"}
    man_path = os.path.join(L.DOCS_9842, "_derived_D.json")
    manifest = L._derived_manifest()
    Dreal = {d: fn for d, fn in Dreal.items() if fn not in manifest}     # 생성본은 「진짜」가 아니다

    plan, skipped = [], []
    for d in sorted(P):
        prev = _prev_trading_day(_dt.date.fromisoformat(d))
        pd = prev.isoformat() if prev else None
        if pd not in P:
            skipped.append((d, "직전 거래일 %s 의 _P 없음" % pd)); continue
        plan.append((d, pd))

    # 1) 자기검증 — 진짜 _D 가 있는 날
    verified, bad = [], []
    for d, pd in plan:
        if d not in Dreal:
            continue
        h, rows = derive(P[d], P[pd])
        hr, br = _cells(Dreal[d])
        n = sum(len(r) for r in rows)
        diff = [(r[5], h[i], r[i], s[i]) for r, s in zip(rows, br) for i in range(11)
                if h[i] != "현재가" and L._num(r[i]) != L._num(s[i])]
        if hr != h or len(br) != len(rows) or diff:
            bad.append((d, diff[:5], hr == h, len(br), len(rows)))
        else:
            verified.append("%s 일치 %d/%d칸 (%s - %s = %s)" % (d, n, n, P[d], P[pd], Dreal[d]))
    for v in verified:
        print("[자기검증] " + v)
    for b in bad:
        print("[자기검증 실패] %s 예시 %s 머리행일치=%s 행수 %s/%s" % b)
    if not verified:
        print("[자기검증] 진짜 _D 가 있는 날이 없다 — 검증 없이 쓰지 않는다(--force 로만 진행)")
    if (bad or not verified) and not a.force:
        print("중단 — 아무것도 쓰지 않았다.")
        return 2

    # 2) 생성
    wrote = []
    for d, pd in plan:
        if d in Dreal:
            continue
        yymmdd = d[2:4] + d[5:7] + d[8:10]
        fn = "%s_D.xls" % yymmdd
        try:
            h, rows = derive(P[d], P[pd])
        except Exception as e:
            skipped.append((d, "차분 실패: %s" % e)); continue
        note = ("DERIVED by tools/maekjeom_ladder/derive_9842_daily.py %s : %s - %s. "
                "Not an HTS export. Verified rule: %s"
                % (_dt.datetime.now().isoformat(timespec="seconds"), P[d], P[pd], "; ".join(verified))).replace("−", "-")
        note = note.encode("ascii", "replace").decode("ascii")   # HTML 주석은 ASCII 만(euc-kr 안전)
        if not a.dry_run:
            write_xls(os.path.join(L.DOCS_9842, fn), h, rows, note)
            manifest[fn] = dict(date=d, minuend=P[d], subtrahend=P[pd], rows=len(rows),
                                generated_at=_dt.datetime.now().isoformat(timespec="seconds"), verified=verified)
        wrote.append((d, fn, P[d], P[pd], len(rows)))
    if not a.dry_run and wrote:
        with open(man_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=1)

    print("\n%s %d개" % ("생성 예정" if a.dry_run else "생성", len(wrote)))
    for d, fn, p1, p0, n in wrote:
        print("  %s  %s = %s − %s  (%d행)" % (d, fn, p1, p0, n))
    for d, why in skipped:
        print("  건너뜀 %s — %s" % (d, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
