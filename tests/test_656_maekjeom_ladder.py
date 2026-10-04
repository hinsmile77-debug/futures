# -*- coding: utf-8 -*-
"""[MW0601 656차] 맥점 × 옵션 사다리 로컬 서버 — 실시간 분 단위 + 날짜별 복기.

고정하는 것
-----------
A. 터치 판정 — 사전 고정 규칙(3pt·15봉) 그대로, 판정 창이 덜 끝난 실시간 터치는 「진행중」.
B. 라이브 1분봉 증분 캐시 — 두 번째 호출부터 봉이 줄지 않는다(개발 중 실제로 384→2 회귀가 났다).
C. 456차 — 모든 DB 를 `mode=ro` 로 열고, 장중 raw_data.db 접근은 ts 범위 증분 조회 하나뿐.
D. 서버는 127.0.0.1 에만 묶는다 — 다른 PC 에서 접속되면 안 된다.
E. 9842 표준 라이브러리 파서 — 파일 모드(_D/_P · 옛 파일 판독표), 머리행 이름으로 열 찾기, 단위(계약/금액) 판정.
G. _P 차분으로 _D 복원 — 자기검증 통과 시에만 쓰고, 진짜 _D 는 덮어쓰지 않고, 빈 파일을 남기지 않는다.
F. 화면 — 10/2 전용 하드코딩(가격축 1084–1124 · 행사가 1075–1130 · 「1118」 문구)이 남지 않는다.

실행:
    conda run -n py37_32 python -m pytest tests/test_656_maekjeom_ladder.py -v   (서버 실행은 py310_64 — 피터 파서가 ast.get_source_segment 를 쓴다)
"""
import os
import re
import sqlite3
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "tools", "maekjeom_ladder")
sys.path.insert(0, _DIR)
import ladder_data as L  # noqa: E402


def _src(name):
    with open(os.path.join(_DIR, name), encoding="utf-8") as f:
        return f.read()


def _bars(prices):
    """종가 목록 → [hm, o, h, l, c] (고·저 = 종가 ±0.2)."""
    out, t = [], 9 * 60
    for p in prices:
        out.append(["%02d:%02d" % (t // 60, t % 60), p, p + 0.2, p - 0.2, p])
        t += 1
    return out


def _lvl(price, start="09:00"):
    return dict(stage="0850", start=start, kind="구조", price=price, label="x", side="up", merge=False)


# ── A. 터치 판정 ──────────────────────────────────────────────────────────
def test_touch_breakout_and_pullback():
    cs = _bars([95, 97, 99, 100, 101, 102, 103.5, 104])          # ▲ 접근 후 3pt 관통 → 돌파
    lv = L.judge_touches([_lvl(100.0, "09:01")], cs)
    assert lv[0]["approach"] == "▲" and lv[0]["outcome"] == "돌파" and lv[0]["resolve"] == "09:06"
    cs = _bars([95, 97, 99, 100, 99, 98, 96.5])                   # 3pt 되돌아감 → 되돌림
    lv = L.judge_touches([_lvl(100.0, "09:01")], cs)
    assert lv[0]["outcome"] == "되돌림"


def test_unfinished_window_is_in_progress_not_station():
    """실시간 — 판정 창 15봉이 아직 안 끝났으면 「정거장」이라 부르면 안 된다."""
    cs = _bars([95, 97, 99, 100, 100.5, 99.8])
    lv = L.judge_touches([_lvl(100.0, "09:01")], cs)
    assert lv[0]["outcome"] == "진행중"
    cs = _bars([95, 97, 99] + [100.0] * 20)
    lv = L.judge_touches([_lvl(100.0, "09:01")], cs)
    assert lv[0]["outcome"] == "정거장"


def test_level_before_its_start_is_not_touched():
    cs = _bars([100, 100, 100, 95, 99, 100.1, 104])
    lv = L.judge_touches([_lvl(100.0, "09:04")], cs)
    assert lv[0]["touch"] == "09:05"                              # 맥점 계산 전 터치는 세지 않는다


# ── B. 라이브 증분 캐시 ───────────────────────────────────────────────────
def test_live_incremental_cache_keeps_all_bars(tmp_path, monkeypatch):
    db = tmp_path / "raw_data.db"
    con = sqlite3.connect(str(db))
    con.execute("CREATE TABLE raw_candles (ts TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL)")
    for i in range(30):
        con.execute("INSERT INTO raw_candles VALUES (?,1,2,0.5,1.5)", ("2026-10-06 09:%02d:00" % i,))
    con.commit()
    monkeypatch.setattr(L, "DB", str(tmp_path))
    L._live_cache.update(date=None, rows=[], last_ts=None)
    a, src = L._candles_live("2026-10-06")
    con.execute("INSERT INTO raw_candles VALUES ('2026-10-06 09:30:00',1,2,0.5,1.7)")
    con.execute("UPDATE raw_candles SET close=9.9 WHERE ts='2026-10-06 09:29:00'")   # 덜 찬 봉 갱신
    con.commit(); con.close()
    b, _ = L._candles_live("2026-10-06")
    c, _ = L._candles_live("2026-10-06")
    assert src == "raw_candles(live)" and len(a) == 30
    assert len(b) == 31 and len(c) == 31                          # 384→2 회귀의 지문
    assert b[29][4] == 9.9                                        # 마지막 봉은 다시 받아 덮어쓴다


# ── C. 읽기전용 · 456차 ───────────────────────────────────────────────────
def test_all_db_access_is_read_only():
    s = _src("ladder_data.py")
    assert "mode=ro" in s
    assert "sqlite3.connect(" in s and s.count("sqlite3.connect(") == 1, "모든 연결은 _ro() 하나로"
    assert not re.search(r"\b(INSERT|UPDATE|DELETE|CREATE|DROP)\b", s.replace("raw_candles WHERE", ""))


def test_live_raw_query_is_ts_range_only():
    s = _src("ladder_data.py")
    q = re.findall(r'"(SELECT[^"]*raw_candles[^"]*)"', s)
    assert q, "raw_candles 조회를 못 찾음"
    for x in q:
        assert "ts >= ?" in x and "ts <= ?" in x, "장중 raw_data.db 는 ts 범위 증분 조회만"
        assert "COUNT" not in x.upper() and "GROUP" not in x.upper()


# ── D. 서버 바인딩 ────────────────────────────────────────────────────────
def test_server_binds_localhost_only():
    s = _src("server.py")
    assert 'ThreadingHTTPServer(("127.0.0.1", a.port)' in s
    assert "0.0.0.0" not in s


def test_bad_date_is_rejected_before_any_db_access():
    s = _src("server.py")
    i_rx, i_build = s.find("if not _DATE_RX.match(day)"), s.find("_day_json(day)", s.find("if not _DATE_RX.match(day)"))
    assert 0 < i_rx < i_build


# ── E. 9842 파일 ──────────────────────────────────────────────────────────
def test_9842_mode_from_suffix_and_legacy_table(tmp_path, monkeypatch):
    for fn in ("261006_D.xlsx", "261006_P.xls", "261001.xlsx", "261002.xlsx", "261003.xlsx", "memo.txt"):
        (tmp_path / fn).write_bytes(b"x")
    monkeypatch.setattr(L, "DOCS_9842", str(tmp_path))
    got = {f["fn"]: f["mode"] for f in L._list_9842_files()}
    assert got["261006_D.xlsx"] == "D" and got["261006_P.xls"] == "P"
    assert got["261001.xlsx"] == "P" and got["261002.xlsx"] == "D"   # 2026-10-02 판독표
    assert got["261003.xlsx"] is None                                # 모르면 모른다 — 추측하지 않는다
    assert "memo.txt" not in got


def _xls(path, head, rows):
    tr = lambda cells: "<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in cells)
    path.write_bytes(("<table>%s</table>" % "".join([tr(head)] + [tr(r) for r in rows])).encode("euc-kr"))


_HEAD_OLD = ["투신", "금융투자", "외국인", "개인", "현재가", "행사가", "현재가", "개인", "외국인", "금융투자", "투신"]
_HEAD_NEW = ["기관계", "금융투자", "외국인", "개인", "현재가", "행사가", "현재가", "개인", "외국인", "금융투자", "기관계"]


def test_9842_amount_file_old_layout(tmp_path):
    """2026-10-02 내보내기 — 투신 열 · 금액(소수점 섞임, 십만원) → 억원, 기관 ≈ 금투+투신."""
    p = tmp_path / "261002_D.xls"
    _xls(p, _HEAD_OLD, [["0", "1,500", "-4,909", "6371.5", "9.1", "1100", "8.0", "3265", "1896", "-5640", "0"]])
    d, unit, note = L.read_9842_meta(str(p))
    assert unit == "krw_eok" and "기관계 열 없음" in note
    assert d["1100.0"]["c_for"] == -4.909 and d["1100.0"]["c_ins"] == 1.5 and d["1100.0"]["p_ins"] == -5.64


def test_9842_contract_file_new_layout(tmp_path):
    """2026-10-04 내보내기 — 기관계 열 · 계약(전부 정수). 위치로 읽으면 기관이 이중 계산된다."""
    p = tmp_path / "261002_D.xls"
    _xls(p, _HEAD_NEW, [["-7", "-9", "-135", "142", "9.1", "1100", "8.0", "38", "-41", "4", "3"]])
    d, unit, note = L.read_9842_meta(str(p))
    assert unit == "contract" and note == "기관 = 기관계"
    assert d["1100.0"] == dict(c_for=-135.0, c_ind=142.0, c_fin=-9.0, c_ins=-7.0, p_for=-41.0, p_ind=38.0, p_fin=4.0, p_ins=3.0)


def test_9842_unknown_header_is_refused(tmp_path):
    p = tmp_path / "261002_D.xls"
    _xls(p, ["보험"] + _HEAD_NEW[1:], [["1"] * 5 + ["1100"] + ["1"] * 5])
    with pytest.raises(ValueError):
        L.read_9842_meta(str(p))


# ── G. _P 차분으로 _D 복원 ────────────────────────────────────────────────
@pytest.fixture
def derive_env(tmp_path, monkeypatch):
    pytest.importorskip("utils.time_utils")
    import derive_9842_daily as DV
    monkeypatch.setattr(L, "DOCS_9842", str(tmp_path))
    row = lambda k, v: [str(v)] * 4 + ["9.1", k, "8.0"] + [str(v)] * 4
    return DV, tmp_path, row


def test_derive_writes_after_self_check(derive_env, monkeypatch):
    DV, d, row = derive_env
    _xls(d / "261001_P.xls", _HEAD_NEW, [row("1100", 10), row("1102.5", 1)])
    _xls(d / "261002_P.xls", _HEAD_NEW, [row("1100", 13), row("1102.5", 0)])
    _xls(d / "261002_D.xls", _HEAD_NEW, [row("1100", 3), row("1102.5", -1)])        # 진짜 — 검증용
    _xls(d / "260930_P.xls", _HEAD_NEW, [row("1100", 4), row("1102.5", 1)])
    monkeypatch.setattr(sys, "argv", ["derive"])
    assert DV.main() == 0
    got = L.read_9842(str(d / "261001_D.xls"))
    assert got["1100.0"]["c_for"] == 6.0 and got["1102.5"]["p_ind"] == 0.0
    assert L.read_9842(str(d / "261002_D.xls"))["1100.0"]["c_for"] == 3.0      # 진짜는 덮어쓰지 않는다
    assert "261001_D.xls" in L._derived_manifest()


def test_derive_refuses_when_self_check_fails(derive_env, monkeypatch):
    DV, d, row = derive_env
    _xls(d / "261001_P.xls", _HEAD_NEW, [row("1100", 10)])
    _xls(d / "261002_P.xls", _HEAD_NEW, [row("1100", 13)])
    _xls(d / "261002_D.xls", _HEAD_NEW, [row("1100", 99)])                         # 규칙이 안 맞는 날
    _xls(d / "260930_P.xls", _HEAD_NEW, [row("1100", 4)])
    monkeypatch.setattr(sys, "argv", ["derive"])
    assert DV.main() == 2
    assert not (d / "261001_D.xls").exists()


def test_derive_never_leaves_empty_file(derive_env, monkeypatch):
    """인코딩 실패가 파일을 연 뒤에 나면 0바이트 _D 가 남아 다음 실행이 「진짜」로 오인한다(실제로 났다)."""
    DV, d, _ = derive_env
    target = d / "260101_D.xls"
    with pytest.raises(UnicodeEncodeError):
        DV.write_xls(str(target), ["−"], [], "x")
    assert not target.exists()                          # 인코딩이 파일을 열기 전에 실패한다
    assert not (d / "260101_D.xls.tmp").exists()


def test_real_files_obey_the_rule():
    """실파일이 있으면 — P(10/2) − P(10/1) == D(10/2) 전 칸(2026-10-04 실측 2,728/2,728)."""
    need = [os.path.join(L.DOCS_9842, f) for f in ("261001_P.xls", "261002_P.xls", "261002_D.xls")]
    if not all(os.path.exists(p) for p in need):
        pytest.skip("9842 실파일 없음(이 PC 전용)")
    p1, p2, d2 = (L.read_9842(p) for p in need)
    bad = [(k, c) for k in d2 for c in d2[k] if k in p1 and abs((p2[k][c] - p1[k][c]) - d2[k][c]) > 1e-9]
    assert not bad, bad[:5]


# ── F. 화면에 10/2 하드코딩이 남지 않는다 ─────────────────────────────────
def test_page_has_no_single_day_hardcoding():
    s = _src("ladder.html")
    assert "__DATA__" not in s and "ladder1002" not in s
    assert "yMin = 1084" not in s and "1075" not in s and "1118은" not in s
    assert "/api/day?date=" in s and "/api/dates" in s
    assert "schedule()" in s and "D.live" in s                      # 실시간이면 다시 부른다


# ── H. 행사가 OI 원천 — 미륵이 option_book 우선, 부족하면 메시아 체인 ─────────
def _mk_book(path, n_snaps, start_min=9 * 60 + 1, wall=1100.0, spot=1100.0):
    con = sqlite3.connect(str(path))
    con.execute("CREATE TABLE option_book_snap (ts TEXT, book TEXT, spot REAL, call_wall REAL, put_wall REAL, n_valid INTEGER, expiry TEXT)")
    con.execute("CREATE TABLE option_book_strike (ts TEXT, book TEXT, strike REAL, call_oi INTEGER, put_oi INTEGER)")
    for i in range(n_snaps):
        m = start_min + 5 * i
        ts = "2026-09-22 %02d:%02d:00" % (m // 60, m % 60)
        con.execute("INSERT INTO option_book_snap VALUES (?, 'monthly', ?, ?, ?, 40, '2026-10-08')", (ts, spot, wall, wall))
        con.execute("INSERT INTO option_book_strike VALUES (?, 'monthly', 1100, ?, 5)", (ts, 10 + i))
    con.commit(); con.close()


def test_book_source_prefers_mireuk_when_complete(tmp_path, monkeypatch):
    _mk_book(tmp_path / "option_book.db", 30, wall=1100.0)
    _mk_book(tmp_path / "option_book_fuo.db", 80, start_min=8 * 60 + 25, wall=1150.0)
    monkeypatch.setattr(L, "DB", str(tmp_path))
    out, times, basis = L.books("2026-09-22", [["09:01", 1, 1, 1, 1101.0]])
    assert out["monthly"]["src"].startswith("미륵이") and out["monthly"]["wall_close"] == [1100.0, 1100.0]
    assert basis == 1.0


def test_book_source_falls_back_to_messiah_when_partial(tmp_path, monkeypatch):
    """9/23 처럼 미륵이 수집이 장중에 시작한 날 — 스냅샷이 BOOK_MIN_SNAPS 미만이면 메시아 종일분을 쓴다."""
    _mk_book(tmp_path / "option_book.db", 4, start_min=14 * 60 + 34)
    _mk_book(tmp_path / "option_book_fuo.db", 80, start_min=8 * 60 + 25, wall=1150.0)
    monkeypatch.setattr(L, "DB", str(tmp_path))
    out, times, basis = L.books("2026-09-22", [])
    assert out["monthly"]["src"].startswith("메시아") and out["monthly"]["times"][0] == "08:25"
    assert out["monthly"]["wall_close"] == [1150.0, 1150.0]
    assert basis is None                                     # 1분봉이 없으면 베이시스는 미측정 — 0 이 아니다
    assert out["weekly_mon"]["absent"] is True


def test_page_has_no_fixed_baseline_time():
    assert "09:01" not in _src("ladder.html")                 # 메시아 원천은 첫 스냅샷이 08:2x 다


def test_oi_layer_has_all_three_books():
    """옵션층 OI 버튼 — 먼스리·월위클리·목위클리 셋 다(2026-10-04 목위클리 추가)."""
    s = _src("ladder.html")
    assert "['wkt','목위클리 OI']" in s
    assert "wkt: ['weekly_thu', '목위클리']" in s
