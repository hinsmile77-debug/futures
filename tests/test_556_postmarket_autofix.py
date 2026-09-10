# -*- coding: utf-8 -*-
"""[MW0601 556차 후속] 2026-09-10 장후 자동조치 회귀 테스트 — F-5 · G-4 · G-1.

────────────────────────────────────────────────────────────────────────────
이 세 건이 붙잡는 지문 (2026-09-10 실측)
────────────────────────────────────────────────────────────────────────────

**F-5 — Armistice 「고착」 ERROR 오탐.**
  14:41:01 장중 재기동, 61초 뒤인 14:42:02 에
  `[Armistice] 🔴 개장 30분 초과 고착 (time_ok=False sync=2/2 broker_verified=True
  block_new_entries=False)` ERROR. 그런데 `_restart_armistice_until` 의 대입 지점은
  `__init__` **단 1곳**이라 재연장 경로가 없고, `time_ok=False` 는 기동 후 90초
  이내에만 성립하는 **정상 워밍업**이다. 즉 09:30 이후 재기동하면 그 90초가
  통째로 거짓 ERROR 로 찍혔다. 진짜 고착(2026-08-31 47분 사고)은 `time_ok=True`
  인데 `sync_ok=False` 인 형태다.

**G-4 — 래치 사유가 남지 않는다.**
  09:00~14:40 `[L2-Tier4] … 당일 영구 중단` 384회. 그런데 "무엇이 500,000원을
  넘겼는가"가 어디에도 없어, 원인 거래를 특정하는 데 EOD 마감 로그와 DB 조회까지
  동원해야 했다.

**G-1 — 상태파일 이전 세대가 없다.**
  출처 불명 이월 포지션의 "언제 열렸는가"를 조사하려 했더니 `position_state.json`
  이 청산 직후 값(FLAT)으로 이미 덮어써져 있었다.

지키는 불변식:
  F5-1  time_ok=False + 워밍업 유예 안 → ERROR **없음** (오늘의 오탐)
  F5-2  time_ok=True  + sync 미달      → ERROR 있음  (2026-08-31 진짜 고착 보존)
  F5-3  time_ok=False 가 유예를 넘겨 지속 → ERROR 있음 (재연장 경로 대비 가드)
  F5-4  차단 판정(`in_armistice`) 은 경보와 무관하게 불변
  G4-1  래치 순간 스냅샷 1줄 · 구성 레그가 실린다
  G4-2  🔴 **라이브 반영 0** — contributors 유무가 판정을 바꾸지 않는다
  G4-3  미측정(None) 과 0건([]) 을 다른 문구로 말한다 (계측 4원칙 ②)
  G4-4  잘릴 때 잔여 개수를 남긴다 `… 외 N건`      (계측 4원칙 ③)
  G4-5  reset() 이 스냅샷을 미측정으로 되돌린다     (계측 4원칙 ④)
  G1-1  포지션 동일성이 바뀌면 이전 세대가 보존된다
  G1-2  같은 포지션의 반복 저장은 세대를 소모하지 않는다
  G1-3  보관 세대 수를 넘기면 오래된 것부터 지운다
  G1-4  `.rejected_*` 증거 파일은 정리 대상이 아니다
  G1-5  백업이 실패해도 저장 자체는 성공한다

실행: conda run -n py37_32 python -m pytest tests/test_556_postmarket_autofix.py
"""

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.runtime_mode import enable_test_mode  # noqa: E402

enable_test_mode()

import main  # noqa: E402  (~5s — 스텁 self 로 _ts_evaluate_armistice() 를 직접 구동)
from strategy import profit_guard as pg  # noqa: E402
from strategy.position import position_tracker as pt  # noqa: E402


# ══════════════════════════════════════════════════════════════════════════
# F-5 — Armistice 고착 경보 오탐
# ══════════════════════════════════════════════════════════════════════════

class _StubSelf(object):
    """`_ts_evaluate_armistice()` 가 실제로 만지는 속성만 갖는다.

    ⚠ `getattr(self, "_x", 기본값)` 로 읽지 않는다 — 이름이 바뀌면 AttributeError 로
      터져야 한다(계측 4원칙 ④).
    """

    def __init__(self, started_at, sync_count=0,
                 verified=False, block_new_entries=True, started_at_override=None):
        self._restart_armistice_until = started_at + datetime.timedelta(seconds=90)
        self._restart_armistice_started_at = (
            started_at if started_at_override is None else started_at_override
        )
        self._restart_armistice_sync_count = sync_count
        self._armistice_promoted_logged = False
        self._armistice_stuck_last_log = None
        self._broker_sync_verified = verified
        self._broker_sync_block_new_entries = block_new_entries


class _LogSpy(object):
    def __init__(self):
        self.records = []

    def system(self, msg, level="INFO", **_kw):
        self.records.append((msg, level))

    def signal(self, msg, **_kw):
        self.records.append((msg, "SIGNAL"))

    def levels(self, level):
        return [m for m, lv in self.records if lv == level]


def _run_armistice(stub, now_dt):
    spy = _LogSpy()
    orig = main.log_manager
    main.log_manager = spy
    try:
        time_ok, in_armistice = main._ts_evaluate_armistice(stub, now_dt)
    finally:
        main.log_manager = orig
    return time_ok, in_armistice, spy


#: 2026-09-10 세 번째 재기동 — `미륵이 초기화` 로그 시각.
_RESTART_0910 = datetime.datetime(2026, 9, 10, 14, 41, 1)


def test_f5_1_warmup_after_open_is_not_stuck():
    """오늘의 오탐 그대로 재현 — 재기동 61초 뒤에는 ERROR 가 없어야 한다."""
    # blank-as-flat 경로가 카운터를 즉시 2로 올린 상태(실측 sync=2/2).
    stub = _StubSelf(_RESTART_0910, sync_count=2,
                     verified=True, block_new_entries=False)
    now = datetime.datetime(2026, 9, 10, 14, 42, 2)   # 실측 ERROR 시각
    time_ok, in_arm, spy = _run_armistice(stub, now)

    assert time_ok is False, "90초 전이므로 time_ok 는 False 가 맞다"
    assert in_arm is True, "F5-4: 차단 판정 자체는 종전과 같아야 한다"
    assert spy.levels("ERROR") == [], "F5-1: 정상 워밍업을 고착이라 부르면 안 된다"


def test_f5_2_real_stuck_still_alerts():
    """2026-08-31 47분 사고 — time_ok=True 인데 sync 가 안 오른 진짜 고착."""
    open_at = datetime.datetime(2026, 8, 31, 8, 40, 57)
    stub = _StubSelf(open_at, sync_count=0, verified=False, block_new_entries=True)
    _, in_arm, spy = _run_armistice(stub, datetime.datetime(2026, 8, 31, 9, 31, 0))

    assert in_arm is True
    errs = spy.levels("ERROR")
    assert len(errs) == 1, "F5-2: 진짜 고착 경보가 죽으면 안 된다"
    assert "[sync]" in errs[0], "고착 종류를 이름에 박는다"
    assert "sync=0/2" in errs[0] and "broker_verified=False" in errs[0]


def test_f5_3_persistent_time_block_still_alerts():
    """가드 보존 — 훗날 `_restart_armistice_until` 재연장 경로가 생기면 이쪽이 잡는다."""
    # 유예 시작이 아주 오래 전인데 아직 time_ok=False → 비정상 지속.
    now = datetime.datetime(2026, 9, 10, 14, 42, 2)
    stub = _StubSelf(now, sync_count=2, verified=True, block_new_entries=False,
                     started_at_override=now - datetime.timedelta(seconds=3600))
    time_ok, in_arm, spy = _run_armistice(stub, now)

    assert time_ok is False and in_arm is True
    errs = spy.levels("ERROR")
    assert len(errs) == 1, "F5-3: 유예를 넘긴 time_ok=False 는 여전히 경보 대상"
    assert "[time]" in errs[0]


def test_f5_4_alert_gate_does_not_touch_block_verdict():
    """🔴 경보 게이트가 진입 차단 판정을 건드리지 않는다."""
    import inspect
    src = inspect.getsource(main._ts_evaluate_armistice)
    assert "not (time_ok and sync_ok)" in src, "판정식은 그대로여야 한다"
    # `in_armistice` 는 경보 분기 이후 어디서도 재대입되지 않는다.
    after = src.split("_stuck_kind = None", 1)[1]
    assert "in_armistice =" not in after, \
        "F5-4: 경보 블록이 차단 판정을 덮어쓰면 안 된다"


def test_f5_5_grace_constant_is_far_beyond_warmup():
    """유예는 90초 창을 넉넉히 넘겨야 한다 — 너무 짧으면 오탐이 되살아난다."""
    assert main._ARMISTICE_WARMUP_GRACE_SEC >= 90 * 5


# ══════════════════════════════════════════════════════════════════════════
# G-4 — ProfitGuard 래치 사유 스냅샷
# ══════════════════════════════════════════════════════════════════════════

def _tier_cfg():
    return pg.ProfitGuardConfig()


def _stop_threshold(cfg):
    """`profit_tiers` 에서 거래중단(max_qty == 0) 임계를 찾는다."""
    for threshold, _mult, max_qty in cfg.profit_tiers:
        if max_qty == 0:
            return float(threshold)
    raise AssertionError("거래중단 티어가 설정에 없다 — 테스트 전제가 깨졌다")


_LEGS = [
    {"id": 572, "entry_ts": "2026-09-10 08:02:01",
     "entry_source": "PHANTOM_STATE_ARTIFACT", "net_krw": 3469797.0},
    {"id": 573, "entry_ts": "2026-09-10 08:02:01",
     "entry_source": "PHANTOM_STATE_ARTIFACT", "net_krw": 3451797.0},
]


def _latch(contributors, spy=None):
    """거래중단 임계를 넘겨 래치시키고 (gate, spy) 를 돌려준다."""
    spy = spy or _LogSpy()
    cfg = _tier_cfg()
    gate = pg._TierGate()
    orig = pg.log_manager
    pg.log_manager = spy
    try:
        out = gate.check(_stop_threshold(cfg) + 1.0, 1.0, cfg,
                         contributors=contributors)
    finally:
        pg.log_manager = orig
    return gate, out, spy


def test_g4_1_snapshot_logged_once_with_contributors():
    gate, out, spy = _latch(_LEGS)
    assert out[0] is True and gate.is_halted is True

    snaps = [m for m in spy.levels("SIGNAL") if "[LatchSnapshot]" in m]
    assert len(snaps) == 1, "G4-1: 래치 순간 한 줄"
    assert "PHANTOM_STATE_ARTIFACT" in snaps[0], "구성 레그의 출처가 실려야 한다"
    assert "id=572" in snaps[0] and "id=573" in snaps[0]
    assert gate.halt_snapshot is not None and "구성레그=2건" in gate.halt_snapshot

    # 이미 래치된 뒤 재호출은 스냅샷을 다시 찍지 않는다(로그 폭주 방지).
    spy2 = _LogSpy()
    orig = pg.log_manager
    pg.log_manager = spy2
    try:
        gate.check(999.0, 1.0, _tier_cfg(), contributors=_LEGS)
    finally:
        pg.log_manager = orig
    assert [m for m in spy2.levels("SIGNAL") if "[LatchSnapshot]" in m] == []


def test_g4_2_contributors_do_not_change_any_verdict():
    """🔴 라이브 반영 0 — 계측 인자가 판정을 바꾸면 안 된다."""
    cfg = _tier_cfg()
    stop = _stop_threshold(cfg)
    probes = [
        (-500000.0, 0.4), (-500000.0, 1.0), (0.0, 0.5), (0.0, 1.0),
        (1_000_000.0, 0.8), (1_000_000.0, 1.5),
        (stop - 1.0, 1.0), (stop, 1.0), (stop + 1.0, 0.1),
    ]
    for pnl, mult in probes:
        orig = pg.log_manager
        pg.log_manager = _LogSpy()
        try:
            a = pg._TierGate().check(pnl, mult, _tier_cfg(), contributors=None)
            b = pg._TierGate().check(pnl, mult, _tier_cfg(), contributors=_LEGS)
            c = pg._TierGate().check(pnl, mult, _tier_cfg(), contributors=[])
        finally:
            pg.log_manager = orig
        assert a == b == c, \
            "G4-2: pnl=%r mult=%r 에서 판정이 갈렸다 — %r / %r / %r" % (pnl, mult, a, b, c)

    # ProfitGuard 상위 API 도 같아야 한다.
    for pnl, mult in probes:
        orig = pg.log_manager
        pg.log_manager = _LogSpy()
        try:
            g1 = pg.ProfitGuard()
            g2 = pg.ProfitGuard()
            r1 = g1.is_entry_allowed(pnl, mult, pnl_source="engine_system_only")
            r2 = g2.is_entry_allowed(pnl, mult, pnl_source="engine_system_only",
                                     pnl_contributors=_LEGS)
        finally:
            pg.log_manager = orig
        assert r1 == r2, "G4-2: is_entry_allowed 가 갈렸다 — %r vs %r" % (r1, r2)


def test_g4_3_unmeasured_is_not_zero():
    """계측 4원칙 ② — 「안 봤다」와 「0건이다」를 같은 문구로 말하지 않는다."""
    none_txt = pg._format_latch_contributors(None)
    zero_txt = pg._format_latch_contributors([])
    assert "미측정" in none_txt
    assert "미측정" not in zero_txt and "0건" in zero_txt
    assert none_txt != zero_txt


def test_g4_4_truncation_states_remainder():
    """계측 4원칙 ③ — 자를 때 잔여 개수를 남긴다(457차 C6 재발 방지)."""
    many = [dict(_LEGS[0], id=i) for i in range(_LEGS and 20 or 20)]
    txt = pg._format_latch_contributors(many)
    rest = len(many) - pg._LATCH_SNAPSHOT_MAX_LEGS
    assert "… 외 %d건" % rest in txt
    assert txt.startswith("%d건" % len(many)), "총 건수도 같은 줄에 있어야 한다"


def test_g4_5_reset_clears_snapshot():
    gate, _, _ = _latch(_LEGS)
    assert gate.halt_snapshot is not None
    gate.reset()
    assert gate.halt_snapshot is None, "G4-5: 어제 사유를 오늘 것으로 읽게 두지 않는다"
    assert gate.is_halted is False


def test_g4_6_status_dict_exposes_snapshot():
    g = pg.ProfitGuard()
    st = g.status_dict(0.0)
    assert "tier_halt_snapshot" in st
    assert st["tier_halt_snapshot"] is None, "래치 전에는 미측정(None)"


# ══════════════════════════════════════════════════════════════════════════
# G-1 — position_state.json 회전 백업
# ══════════════════════════════════════════════════════════════════════════

def _gen_files(dirpath, statefile):
    base = os.path.basename(statefile) + pt._STATE_BACKUP_PREFIX
    return sorted(n for n in os.listdir(dirpath) if n.startswith(base))


def _write_state(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)


def _state(status, entry_price, quantity, entry_time):
    return {"status": status, "entry_price": entry_price,
            "quantity": quantity, "entry_time": entry_time}


def _with_state_file(tmp_path, fn):
    """`_STATE_FILE` 을 tmp 로 갈아끼우고 fn(statefile) 실행."""
    statefile = os.path.join(str(tmp_path), "position_state.json")
    orig = pt._STATE_FILE
    pt._STATE_FILE = statefile
    try:
        return fn(statefile)
    finally:
        pt._STATE_FILE = orig


def test_g1_1_rotates_on_identity_change(tmp_path):
    def body(statefile):
        _write_state(statefile, _state("LONG", 1040.0, 2, "2026-09-10T08:02:01"))
        pt._rotate_state_backup(_state("FLAT", None, 0, None))
        gens = _gen_files(os.path.dirname(statefile), statefile)
        assert len(gens) == 1, "G1-1: 이전 세대가 보존돼야 한다"
        with open(os.path.join(os.path.dirname(statefile), gens[0]),
                  encoding="utf-8") as f:
            kept = json.load(f)
        # 오늘 잃어버렸던 바로 그 증거 — "언제 이 포지션이 열렸는가".
        assert kept["entry_price"] == 1040.0 and kept["quantity"] == 2
        assert kept["entry_time"] == "2026-09-10T08:02:01"
    _with_state_file(tmp_path, body)


def test_g1_2_no_rotation_when_identity_unchanged(tmp_path):
    def body(statefile):
        same = _state("LONG", 1040.0, 2, "2026-09-10T08:02:01")
        _write_state(statefile, same)
        for _ in range(30):          # 트레일링 조정으로 매분 저장되는 상황
            pt._rotate_state_backup(dict(same, stop_price=1037.75))
        assert _gen_files(os.path.dirname(statefile), statefile) == [], \
            "G1-2: 같은 포지션 반복 저장이 링을 소모하면 정작 직전 세대가 밀려난다"
    _with_state_file(tmp_path, body)


def test_g1_3_keeps_only_n_generations(tmp_path):
    def body(statefile):
        d = os.path.dirname(statefile)
        for i in range(pt._STATE_BACKUP_KEEP + 3):
            _write_state(statefile, _state("LONG", 1000.0 + i, 1, "t%d" % i))
            # 파일명이 초 단위라 같은 초에 몰리면 덮어써진다 — 스탬프를 벌린다.
            pt._rotate_state_backup(_state("LONG", 2000.0 + i, 1, "n%d" % i))
            _bump_stamp(d, statefile, i)
        gens = _gen_files(d, statefile)
        assert len(gens) <= pt._STATE_BACKUP_KEEP, \
            "G1-3: 보관 세대 수를 넘겼다 — %r" % gens
    _with_state_file(tmp_path, body)


def _bump_stamp(dirpath, statefile, i):
    """같은 초에 만들어진 백업이 서로 덮어쓰지 않도록 이름을 벌린다(테스트 편의)."""
    base = os.path.basename(statefile) + pt._STATE_BACKUP_PREFIX
    for n in os.listdir(dirpath):
        if n.startswith(base) and not n.endswith("_%02d" % i):
            src = os.path.join(dirpath, n)
            dst = os.path.join(dirpath, "%s_%02d" % (n, i))
            if not os.path.exists(dst):
                os.rename(src, dst)
            break


def test_g1_4_rejected_evidence_is_not_pruned(tmp_path):
    """`_reject_restore()` 가 남긴 증거를 회전 정리가 지우면 안 된다."""
    def body(statefile):
        d = os.path.dirname(statefile)
        evidence = statefile + ".rejected_20260910_084000"
        _write_state(evidence, {"증거": True})
        for i in range(pt._STATE_BACKUP_KEEP + 3):
            _write_state(statefile, _state("LONG", 1000.0 + i, 1, "t%d" % i))
            pt._rotate_state_backup(_state("FLAT", None, 0, None))
            _bump_stamp(d, statefile, i)
        assert os.path.exists(evidence), "G1-4: 격리 증거가 지워졌다"
    _with_state_file(tmp_path, body)


def test_g1_5_backup_failure_does_not_block_save(tmp_path):
    """백업이 깨져도 상태 저장 자체는 성공해야 한다 — 계측이 본업을 막지 않는다."""
    def body(statefile):
        _write_state(statefile, _state("LONG", 1040.0, 2, "t"))
        orig_copy = pt.shutil.copy2

        def _boom(*_a, **_kw):
            raise IOError("디스크 가득 참(시험)")

        pt.shutil.copy2 = _boom
        try:
            pt._rotate_state_backup(_state("FLAT", None, 0, None))   # 예외가 새면 안 됨
        finally:
            pt.shutil.copy2 = orig_copy
        assert _gen_files(os.path.dirname(statefile), statefile) == []
    _with_state_file(tmp_path, body)


def test_g1_6_save_state_calls_rotation():
    """배선 확인 — 함수만 있고 호출이 없으면 죽은 코드다(FP-CRITICAL 계열)."""
    import inspect
    src = inspect.getsource(pt.PositionTracker._save_state)
    assert "_rotate_state_backup(state)" in src
    i_rot = src.index("_rotate_state_backup(state)")
    i_open = src.index('open(_STATE_FILE, "w"')
    assert i_rot < i_open, "회전은 **덮어쓰기 전**이어야 한다"
