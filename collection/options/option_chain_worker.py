"""
OptionChainWorker — 옵션 체인 BlockRequest를 QThread에서 실행.

Cybos Plus 메시지 라우팅 특성:
  BlockRequest 응답이 메인 스레드의 Windows 메시지 큐를 경유한다.
  메인 스레드(Qt 이벤트 루프)가 블록되지 않아야 응답이 전달된다.
  QThread 분리 후 Qt 이벤트 루프가 정상 동작하므로 응답 수신 보장.
  (api_connector.py _run_block_request 주석 참조 — done.wait() 금지 이유)

COM STA 규칙:
  Dscbo1.OptionMst 객체를 워커 스레드 내부에서 생성·사용.
  메인 스레드의 COM 객체와 공유하지 않는다.
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import time
from typing import Any, Dict, List, Tuple

from PyQt5.QtCore import QThread, pyqtSignal

logger = logging.getLogger("OPTIONS")
system_logger = logging.getLogger("SYSTEM")

_HV_OI    = 99   # OptionMst GetHeaderValue 인덱스 — 미결제약정
_HV_GAMMA = 110  # Gamma — **백분율로 온다**. 반드시 `_GREEK_PCT`로 나눠 쓸 것(612차).

# 🔴 [MW0601 612차] OptionMst Greeks 는 백분율이다 — 249차 도입 이래 나눈 적이 없었다.
#
# `_HV_GAMMA` 주석은 처음부터 "(백분율, ÷100)"이라 적혀 있었는데 `_compute_gex`도
# `scripts/collect_option_metrics.py`도 그 ÷100 을 적용하지 않았다(`git log -S "gamma / 100"`
# = 0건). 그래서 `opt_gex_bn` 이 **100배 부풀려진 채** 2026-05 부터 흘렀다.
#
# 근거 — `data/option_metrics.json`(2026-05-14, 48종목 실수집):
#   · `delta` 필드 범위 −52.63 ~ +59.43  → 0~1 이 아니라 0~100. **Greeks 는 백분율.**
#   · ATM(strike 1220.0) `gamma` 필드 0.2100
#     vs Black-Scholes 이론 감마 1/(S·σ·√(2πT)) = 0.002018
#     (S=1220.17, σ=56.51%, T=30/365)        → **비율 104.1**
#
# ⚠ **"GEX IC 재현 실패(0.198 → 0.013)의 원인이 이 버그"라고 쓰지 말 것.**
#   ÷100 은 순수 선형 변환이라 **Spearman/IC 는 불변**이다. F4 판정은 그대로 유효하다.
#   실제로 바뀌는 것은 ① 표시값 ② 절대 임계(감마 배지) ③ DB 컬럼 스케일 셋뿐이다.
#
# ⚠ **학습 영향 없음** — `model/horizons/feature_names.pkl`(97키 동결 슈퍼셋)과 호라이즌별
#   6개 피처셋(1m 8 · 3m 12 · 5m 12 · 10m 11 · 15m 13 · 30m 11) 전수 확인에서
#   옵션 체인 키는 **하나도 포함돼 있지 않다**. train/serve skew 우려 없음(317차 원칙).
_GREEK_PCT = 100.0

_OPTION_MULTIPLIER = 250_000
_GEX_BN = 1e9

# ── [MW0601 478차 후속 / FZ-4] 이상 소요 가드 ──────────────────────────────────
# 2026-08-19 13:41:21~13:51:22, 이 워커의 BlockRequest 루프가 **601,493ms**(평소
# 1,500ms의 400배) 걸렸다. 메인 스레드가 동결돼 Cybos 응답 라우팅이 죽자 24종목이
# 각각 내부 타임아웃(~25초)까지 늘어진 것이다. 그때 반환된 피처는
# `PCR=0.103 ATM_PCR=1.000 GEX=+169.19B` — 같은 날 정상 범위(PCR≈1.0, GEX ±40B)를
# 완전히 벗어난 **병리값**이었다.
#
# 🔴 그 값이 저장되지 않은 것은 설계가 막아서가 아니라 **우연**이다. `result_ready`는
#    Qt 큐드 시그널이라 죽은 메인 루프에 영영 배달되지 못했을 뿐이다. 메인이 살아
#    있는 부분 지연(네트워크 저하·서버 피크)에서는 같은 병리값이 그대로
#    `opt_chain_pcr`·`opt_gex_bn` 피처로 흘러 들어간다.
#
# 두 겹으로 막는다:
#   ① 수집 중단 임계 — 누적 경과가 넘으면 남은 종목을 포기한다. 죽은/막힌 상대에게
#      COM 요청을 계속 던지지 않는다(오늘은 10분간 던졌다).
#   ② 결과 폐기 임계 — 전체 소요가 넘으면 피처를 **버리고** 빈 dict를 반환한다.
#      `OptionChainSnapshot.on_worker_done`이 빈 dict를 "이전 피처 유지"로 처리하므로
#      (계측 4원칙 ② — 미측정을 0으로 위장하지 않는다) 안전하게 스킵된다.
#
# 값 근거: 정상 완료 실측이 1,461~1,628ms(2026-08-19 30회)다. 60초는 그 40배,
# 30초는 20배 — 서버 지연 몇 배는 통과시키고 오늘 같은 병리(601초)만 잡는다.
_COLLECT_ABORT_SEC = 60.0     # ① 이 시간 넘으면 남은 종목 수집 중단
_RESULT_DISCARD_SEC = 30.0    # ② 전체 소요가 이 시간 넘으면 결과 폐기


# ── 타입 헬퍼 ──────────────────────────────────────────────────────

def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _f(v: Any, d: float = 0.0) -> float:
    try:
        t = _s(v).replace(",", "")
        return float(t) if t else d
    except Exception:
        return d


def _i(v: Any, d: int = 0) -> int:
    try:
        t = _s(v).replace(",", "")
        return int(float(t)) if t else d
    except Exception:
        return d


def _is_call(row: Dict) -> bool:
    cp = _s(row.get("call_put", ""))
    return "콜" in cp or cp.upper().startswith("C")


def _is_put(row: Dict) -> bool:
    cp = _s(row.get("call_put", ""))
    return "풋" in cp or cp.upper().startswith("P")


# ── 순수 Python 헬퍼 (COM 없음, 모듈 레벨 함수) ──────────────────────

def _filter_front_month(chain: List[Dict]) -> List[Dict]:
    today = _dt.date.today()
    yms = sorted(set(r["ym"] for r in chain if r.get("ym")))
    for ym in yms:
        try:
            year  = 2000 + int(ym[:2])
            month = int(ym[2:])
            expiry = _option_expiry(year, month)
            if today <= expiry:
                return [r for r in chain if r.get("ym") == ym]
        except Exception:
            pass
    return [r for r in chain if r.get("ym") == yms[0]] if yms else chain


def _option_expiry(year: int, month: int) -> _dt.date:
    """KOSPI200 옵션 만기일 = 해당 월 2번째 목요일."""
    d = _dt.date(year, month, 1)
    days_to_thu = (3 - d.weekday()) % 7
    first_thu = d + _dt.timedelta(days=days_to_thu)
    return first_thu + _dt.timedelta(weeks=1)


def _filter_atm(chain: List[Dict], spot: float, window: float) -> List[Dict]:
    lo, hi = spot - window, spot + window
    return [r for r in chain if lo <= r.get("strike", 0) <= hi]


def _compute(snapshots: List[Dict], spot: float) -> Dict[str, float]:
    pcr_oi = _compute_pcr(snapshots)
    atm_c_oi, atm_p_oi, atm_pcr = _compute_atm_oi(snapshots, spot)
    gex_bn, gex_sign = _compute_gex(snapshots, spot)
    return {
        "opt_chain_pcr":       round(pcr_oi, 4),
        "opt_atm_pcr":         round(atm_pcr, 4),
        "opt_atm_call_oi":     float(atm_c_oi),
        "opt_atm_put_oi":      float(atm_p_oi),
        "opt_gex_bn":          round(gex_bn, 4),
        "opt_gex_sign":        float(gex_sign),
        "opt_chain_available": 1.0,
    }


def _compute_pcr(snapshots: List[Dict]) -> float:
    call_oi = sum(s.get("oi", 0) for s in snapshots if _is_call(s) and not s.get("error"))
    put_oi  = sum(s.get("oi", 0) for s in snapshots if _is_put(s)  and not s.get("error"))
    return put_oi / call_oi if call_oi > 0 else 1.0


def _compute_atm_oi(snapshots: List[Dict], spot: float) -> Tuple[int, int, float]:
    calls = [s for s in snapshots if _is_call(s) and not s.get("error")]
    puts  = [s for s in snapshots if _is_put(s)  and not s.get("error")]
    atm_c = min(calls, key=lambda s: abs(s["strike"] - spot)) if calls else None
    atm_p = min(puts,  key=lambda s: abs(s["strike"] - spot)) if puts else None
    c_oi  = atm_c.get("oi", 0) if atm_c else 0
    p_oi  = atm_p.get("oi", 0) if atm_p else 0
    pcr   = p_oi / c_oi if c_oi > 0 else 1.0
    return c_oi, p_oi, pcr


def _compute_gex(snapshots: List[Dict], spot: float) -> Tuple[float, float]:
    call_gex = put_gex = 0.0
    for s in snapshots:
        if s.get("error") or s.get("oi", 0) <= 0:
            continue
        unit = s.get("gamma", 0.0) * s["oi"] * _OPTION_MULTIPLIER * spot
        if _is_call(s):
            call_gex += unit
        elif _is_put(s):
            put_gex += unit
    total = call_gex - put_gex
    gex_bn = total / _GEX_BN
    sign = 1.0 if total > 0 else (-1.0 if total < 0 else 0.0)
    return gex_bn, sign


# ── [MW0601 623차] 만기북 수집 (먼스리 재사용 + 위클리 2북) ─────────────

def _wait_quota(cy: Any, reserve: int, deadline: float) -> bool:
    """시세 잔여 한도가 reserve 이상이 될 때까지 기다린다. 예산 초과면 False."""
    while True:
        try:
            remain = int(cy.GetLimitRemainCount(1))
        except Exception:
            return True                     # 측정 불가 — pause_ms 가 최소한의 보호
        if remain >= reserve:
            return True
        if time.perf_counter() > deadline:
            return False
        try:
            ms = int(cy.LimitRequestRemainTime)
        except Exception:
            ms = 500
        time.sleep(min(max(ms, 200), 1000) / 1000.0)


def collect_option_books(mst_obj: Any, cy: Any, spot: float, monthly_snaps: List[Dict],
                         monthly_ym: str, ts: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """먼스리 스냅샷(이미 받음) + 위클리 2북 조회 → DB 저장 → 요약 반환.

    워커 스레드 전용(COM 객체는 호출자 스레드 소유). 스크립트에서도 그대로 부른다.
    반환: {"ts", "spot", "master_src", "books": {book: summary}}
    """
    from collection.options import option_book as ob

    t0 = time.perf_counter()
    today = _dt.date.today()
    books: Dict[str, Dict] = {}

    # 먼스리 — 추가 조회 없음. cp 표기를 'C'/'P' 로 정규화만 한다.
    m_snaps = []
    for s in monthly_snaps:
        cp = "C" if _is_call(s) else ("P" if _is_put(s) else "")
        if cp:
            m_snaps.append(dict(s, cp=cp))
    summ, strikes = ob.compute_book(m_snaps, spot)
    _exp = None
    try:
        _exp = _option_expiry(2000 + int(monthly_ym[:2]), int(monthly_ym[2:])).isoformat()
    except Exception:
        pass
    summ.update(label=monthly_ym, expiry=_exp, spot=spot, master_src="CpOptionCode")
    books["monthly"] = {"summary": summ, "strikes": strikes}

    rows, src = ob.load_master(cfg["master_dir"], today, cfg.get("fallbacks", ()))
    if src.startswith("stale") or src == "none":
        system_logger.warning("[OptionBook] 마스터 원천=%s — 위클리 목록이 오늘 것이 아닐 수 있다", src)
    deadline = t0 + float(cfg.get("budget_sec", 150.0))
    for book in ("weekly_thu", "weekly_mon"):
        label, sel = ob.select_nearest(rows, book, today)
        target = ob.filter_atm(sel, spot, float(cfg.get("window", 30.0)))
        snaps: List[Dict] = []
        for r in target:
            snap = dict(r)
            # 예산은 **매 요청 전에** 본다. `_wait_quota` 안에서만 보면 한도가 넉넉할 때
            #   예산이 무시된다 — BlockRequest 자체가 느린 경우(2026-08-19 동결 때 건당 ~25초)
            #   96건을 끝까지 던진다. FZ-4 ①과 같은 원리(막힌 상대에게 계속 던지지 않는다).
            if (time.perf_counter() > deadline
                    or not _wait_quota(cy, int(cfg.get("reserve", 25)), deadline)):
                snap["error"] = "budget_exceeded"
                snaps.append(snap)
                continue
            try:
                mst_obj.SetInputValue(0, r["code"])
                mst_obj.BlockRequest()
                st = _i(mst_obj.GetDibStatus())
                if st != 0:
                    snap["error"] = "dib_status=%d" % st
                else:
                    snap["oi"] = _i(mst_obj.GetHeaderValue(_HV_OI))
                    snap["gamma"] = _f(mst_obj.GetHeaderValue(_HV_GAMMA)) / _GREEK_PCT
            except Exception as exc:
                snap["error"] = str(exc)
            snaps.append(snap)
            time.sleep(0.05)                # 기존 먼스리 루프 pause_ms 와 같은 간격
        summ, strikes = ob.compute_book(snaps, spot)
        exp = ob.nominal_expiry(book, label) if label else None
        summ.update(label=label, expiry=exp.isoformat() if exp else None,
                    spot=spot, master_src=src)
        books[book] = {"summary": summ, "strikes": strikes}

    elapsed = int((time.perf_counter() - t0) * 1000)
    for b in books.values():
        b["summary"]["elapsed_ms"] = elapsed
    try:
        ob.save_books(cfg["db_path"], ts, books)
    except Exception as exc:
        system_logger.warning("[OptionBook] 저장 실패: %s", exc)
    system_logger.info(
        "[OptionBook] 완료 %dms master=%s | %s", elapsed, src,
        " | ".join(
            "%s %s n=%d/%d GEX=%s 콜월=%s 풋월=%s" % (
                ob.BOOK_LABEL[k], v["summary"].get("label"), v["summary"]["n_valid"],
                v["summary"]["n_target"],
                "%.2fB" % v["summary"]["gex_bn"] if v["summary"]["gex_bn"] is not None else "미측정",
                v["summary"]["call_wall"], v["summary"]["put_wall"])
            for k, v in books.items()),
    )
    return {"ts": ts, "spot": spot, "master_src": src,
            "books": {k: v["summary"] for k, v in books.items()}}


# ── OptionChainWorker ───────────────────────────────────────────────

class OptionChainWorker(QThread):
    """
    ATM 옵션 BlockRequest 루프를 메인 스레드에서 분리.

    result_ready(feats, chain_raw):
      feats     — 계산된 피처 dict. 실패 시 빈 dict.
      chain_raw — 수집·갱신된 체인 목록. stale 재로드 없으면 입력 그대로.
                  빈 list → 다음 워커 기동 시 CpOptionCode 재수집 지시.
    """

    result_ready = pyqtSignal(object, object)   # (dict, list) — PyQt_PyObject 사용
    # [623차] 만기북 요약 — result_ready **다음에** 온다(먼스리 피처를 늦추지 않는다).
    book_ready = pyqtSignal(object)

    def __init__(
        self,
        chain_raw: List[Dict],
        spot: float,
        cache_path: str,
        atm_window_pt: float = 30.0,
        pause_ms: int = 50,
        parent=None,
        force_chain_reload: bool = False,
        book_cfg: Dict[str, Any] = None,
    ) -> None:
        super().__init__(parent)
        self._chain_raw   = list(chain_raw)   # 복사본 — 메인 스레드와 공유 없음
        self._spot        = spot
        self._cache_path  = cache_path
        self._atm_window  = atm_window_pt
        self._pause_ms    = pause_ms
        # [MW0601 612차] 거래일이 바뀌어 체인 **코드 목록**을 다시 받아야 하는가.
        # 판정은 메인 스레드(OptionChainSnapshot.chain_reload_due)가 한다 —
        # 워커는 시키는 대로 받기만 한다.
        self._force_reload = bool(force_chain_reload)
        # [623차] None 이면 만기북 수집 안 함. _execute 가 먼스리 성공 시 _book_ctx 를 채운다.
        self._book_cfg = book_cfg
        self._book_ctx: Dict[str, Any] = None

    # ── QThread 진입점 ─────────────────────────────────────────────

    def run(self) -> None:
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception as exc:
            system_logger.warning("[OptionChain][Worker] CoInitialize 실패: %s", exc)
            self.result_ready.emit({}, self._chain_raw)
            return

        feats: Dict[str, float] = {}
        chain_raw: List[Dict] = self._chain_raw
        try:
            try:
                feats, chain_raw = self._execute()
            except Exception as exc:
                system_logger.warning(
                    "[OptionChain][Worker] 예외: %s", exc, exc_info=True,
                )
            self.result_ready.emit(feats, chain_raw)
            # [623차] 먼스리 피처를 내보낸 뒤에 만기북. 실패해도 피처 경로와 무관하다.
            if self._book_cfg and self._book_ctx:
                try:
                    from win32com.client import Dispatch
                    c = self._book_ctx
                    summary = collect_option_books(
                        c["mst"], Dispatch("CpUtil.CpCybos"), c["spot"], c["snaps"],
                        c["ym"], c["ts"], self._book_cfg)
                    self.book_ready.emit(summary)
                except Exception as exc:
                    system_logger.warning(
                        "[OptionBook] 예외: %s", exc, exc_info=True,
                    )
        finally:
            self._book_ctx = None           # COM 객체 참조를 CoUninitialize 전에 놓는다
            try:
                import pythoncom as _pc
                _pc.CoUninitialize()
            except Exception:
                pass

    # ── 핵심 실행 (워커 스레드) ────────────────────────────────────

    def _execute(self) -> Tuple[Dict[str, float], List[Dict]]:
        t0 = time.perf_counter()

        chain_raw = self._chain_raw

        # [MW0601 612차] 거래일이 바뀌었으면 코드 목록부터 다시 받는다.
        # ⚠ 실패해도 낡은 목록을 **버리지 않는다** — 코드 목록은 관측치가 아니라
        #   조회 대상이라, 없으면 그날 옵션 피처가 통째로 사라진다. 낡은 쪽이 낫다.
        #   다만 조용히 넘어가지 않는다(계측 4원칙 ④).
        if self._force_reload and chain_raw:
            _fresh = self._fetch_chain()
            if _fresh:
                system_logger.info(
                    "[OptionChain][Worker] 체인 코드 목록 재수집 — %d → %d 종목",
                    len(chain_raw), len(_fresh),
                )
                chain_raw = _fresh
            else:
                system_logger.warning(
                    "[OptionChain][Worker] 체인 코드 목록 재수집 실패 — 낡은 캐시 %d 종목 유지. "
                    "행사가 격자가 현재 상장분과 다를 수 있다(612차)",
                    len(chain_raw),
                )

        if not chain_raw:
            chain_raw = self._fetch_chain()
            if not chain_raw:
                return {}, []

        front  = _filter_front_month(chain_raw)
        target = _filter_atm(front, self._spot, self._atm_window)

        if not target:
            system_logger.warning(
                "[OptionChain][Worker] ATM 대상 없음 spot=%.1f window=%.0f — stale, 재로드",
                self._spot, self._atm_window,
            )
            chain_raw = self._fetch_chain()
            if not chain_raw:
                return {}, []
            front  = _filter_front_month(chain_raw)
            target = _filter_atm(front, self._spot, self._atm_window)
            if not target:
                system_logger.warning(
                    "[OptionChain][Worker] 재로드 후에도 ATM 대상 없음 spot=%.1f — 수집 불가",
                    self._spot,
                )
                return {}, chain_raw

        from win32com.client import Dispatch
        mst_obj = Dispatch("Dscbo1.OptionMst")
        snapshots = self._collect_snapshots(mst_obj, target)

        # [FZ-4 ②] 이상 소요 — 결과 폐기. 값을 안 쓰는 것이 병리값을 쓰는 것보다 낫다.
        _elapsed_guard = (time.perf_counter() - t0) * 1000
        if _elapsed_guard > _RESULT_DISCARD_SEC * 1000:
            _aborted = sum(1 for s in snapshots if s.get("error") == "collect_abort_slow")
            system_logger.warning(
                "[OptionChain][Worker] 이상 소요 %.0fms > %.0fms — **결과 폐기**(이전 피처 유지) "
                "target=%d aborted=%d | 2026-08-19 동결 시 601,493ms/PCR=0.103/GEX=169B 병리값 재발 방지",
                _elapsed_guard, _RESULT_DISCARD_SEC * 1000, len(target), _aborted,
            )
            return {}, chain_raw

        valid = [s for s in snapshots if not s.get("error")]
        if not valid:
            errors = [s.get("error", "?") for s in snapshots[:3]]
            system_logger.warning(
                "[OptionChain][Worker] 스냅샷 전체 실패 target=%d errors=%s — 코드 만료 가능성",
                len(target), errors,
            )
            # 빈 list 반환 → Snapshot이 _chain_raw를 갱신하지 않음
            # → 다음 워커에서 CpOptionCode 재수집
            return {}, []

        feats = _compute(snapshots, self._spot)
        if self._book_cfg:
            self._book_ctx = {
                "mst": mst_obj, "spot": self._spot, "snaps": snapshots,
                "ym": target[0].get("ym", ""),
                "ts": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        elapsed = (time.perf_counter() - t0) * 1000
        system_logger.info(
            "[OptionChain][Worker] 완료 %.0fms | target=%d valid=%d "
            "PCR=%.3f ATM_PCR=%.3f GEX=%.2fB",
            elapsed, len(target), len(valid),
            feats.get("opt_chain_pcr", 0),
            feats.get("opt_atm_pcr", 0),
            feats.get("opt_gex_bn", 0),
        )
        return feats, chain_raw

    def _collect_snapshots(self, mst_obj: Any, target: List[Dict]) -> List[Dict]:
        """OptionMst BlockRequest 루프 — 워커 스레드 전용.

        [FZ-4 ①] 누적 경과가 `_COLLECT_ABORT_SEC`를 넘으면 남은 종목을 요청하지 않고
        `error="collect_abort_slow"`로 표시만 한다. 행을 빠뜨리지 않고 **탈락을
        가시화**하기 위해서다(계측 4원칙 ③) — 리스트 길이가 줄면 호출부가 "대상이
        원래 적었다"로 오독한다.
        """
        out: List[Dict] = []
        _loop_t0 = time.perf_counter()
        _aborted = False
        for row in target:
            code = row["code"]
            snap: Dict[str, Any] = {
                "code":     code,
                "call_put": row.get("call_put", ""),
                "strike":   row.get("strike", 0.0),
            }
            if _aborted or (time.perf_counter() - _loop_t0) > _COLLECT_ABORT_SEC:
                if not _aborted:
                    _aborted = True
                    system_logger.warning(
                        "[OptionChain][Worker] 수집 %.0fs 초과 — 잔여 종목 요청 중단 "
                        "(완료 %d / 전체 %d). 막힌 상대에게 COM 요청을 계속 던지지 않는다",
                        _COLLECT_ABORT_SEC, len(out), len(target),
                    )
                snap["error"] = "collect_abort_slow"
                out.append(snap)
                continue
            try:
                mst_obj.SetInputValue(0, code)
                mst_obj.BlockRequest()
                if _i(mst_obj.GetDibStatus()) != 0:
                    snap["error"] = f"dib_status={_i(mst_obj.GetDibStatus())}"
                else:
                    snap["oi"]    = _i(mst_obj.GetHeaderValue(_HV_OI))
                    # [612차] 백분율 → 실수. 이 한 줄이 빠져 GEX 가 100배였다.
                    snap["gamma"] = _f(mst_obj.GetHeaderValue(_HV_GAMMA)) / _GREEK_PCT
            except Exception as exc:
                snap["error"] = str(exc)
            out.append(snap)
            if self._pause_ms > 0:
                time.sleep(self._pause_ms / 1000.0)
        return out

    def _fetch_chain(self) -> List[Dict]:
        """CpOptionCode로 옵션 코드 목록 수집 후 캐시 저장."""
        try:
            from win32com.client import Dispatch
            chain_obj = Dispatch("CpUtil.CpOptionCode")
            count = chain_obj.GetCount()
            chain: List[Dict] = []
            for idx in range(count):
                try:
                    chain.append({
                        "code":     _s(chain_obj.GetData(0, idx)),
                        "call_put": _s(chain_obj.GetData(2, idx)).upper(),
                        "ym":       _s(chain_obj.GetData(3, idx)),
                        "strike":   _f(chain_obj.GetData(4, idx)),
                    })
                except Exception:
                    pass
            logger.info("[OptionChain][Worker] CpOptionCode 수집 완료: %d 종목", len(chain))
            self._save_chain_cache(chain)
            return chain
        except Exception as exc:
            logger.warning("[OptionChain][Worker] 체인 수집 실패: %s", exc)
            return []

    def _save_chain_cache(self, chain: List[Dict]) -> None:
        try:
            dir_ = os.path.dirname(self._cache_path)
            if dir_:
                os.makedirs(dir_, exist_ok=True)
            with open(self._cache_path, "w", encoding="utf-8") as f:
                # [MW0601 612차] `saved_at` 을 함께 쓴다 — 파일 mtime 은 복사·체크아웃에
                # 쉽게 흔들려서 "언제 받은 목록인가"의 1차 근거가 못 된다.
                json.dump(
                    {"saved_at": _dt.date.today().isoformat(), "chain": chain},
                    f, ensure_ascii=False, indent=2,
                )
        except Exception:
            pass
