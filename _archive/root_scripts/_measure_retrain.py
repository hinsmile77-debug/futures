"""
EOD 재학습 소요 시간 실측 스크립트
---
목적:
  - full_cv=True (절단 없음) 재학습의 실제 소요 시간과 peak 메모리 실측
  - py37_32 / py310_64 양 환경에서 동일 스크립트 실행 → 비교
  - 윈도우 스케줄러 분리 실현 가능성 판단

실행법:
  py37_32   환경: conda run -n py37_32   python _measure_retrain.py
  py310_64  환경: conda run -n py310_64  python _measure_retrain.py
  결과 파일: _measure_retrain_result_{환경명}.txt
"""

import sys
import os
import gc
import time
import platform
import tracemalloc
import datetime
import logging

# ── 프로젝트 루트를 path에 추가 ──────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ── 로거 독립 설정 (main.py log_manager 없이) ───────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
# 학습 로거는 WARNING 이상만 (INFO 스팸 억제)
logging.getLogger("LEARNING").setLevel(logging.WARNING)
logging.getLogger("root").setLevel(logging.WARNING)

log = logging.getLogger("MEASURE")


# ── 환경 정보 수집 ──────────────────────────────────────────────────
def _env_info():
    bits = "64-bit" if sys.maxsize > 2**32 else "32-bit"
    try:
        import sklearn
        sk_ver = sklearn.__version__
    except ImportError:
        sk_ver = "미설치"
    try:
        import numpy as np
        np_ver = np.__version__
    except ImportError:
        np_ver = "미설치"
    return {
        "python":  f"{sys.version.split()[0]} {bits}",
        "os":      platform.platform(),
        "sklearn": sk_ver,
        "numpy":   np_ver,
        "bits":    bits,
    }


# ── peak 메모리 블록 측정 유틸 ─────────────────────────────────────
class _MemBlock:
    """with 블록 안에서 tracemalloc peak 메모리 측정."""
    def __init__(self, label):
        self.label = label
        self.peak_mb = 0.0

    def __enter__(self):
        gc.collect()
        tracemalloc.start()
        return self

    def __exit__(self, *_):
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.peak_mb = peak / 1024 / 1024


# ── 단계별 타이머 ───────────────────────────────────────────────────
class _Timer:
    def __init__(self):
        self._marks = []
        self._t0 = time.perf_counter()

    def mark(self, label):
        self._marks.append((label, time.perf_counter() - self._t0))

    def elapsed_since_last(self):
        if len(self._marks) < 2:
            return self._marks[-1][1] if self._marks else 0.0
        return self._marks[-1][1] - self._marks[-2][1]

    def report(self):
        lines = []
        prev = 0.0
        for label, t in self._marks:
            lines.append(f"  {label:<35} {t - prev:>7.1f}s  (누계 {t:>7.1f}s)")
            prev = t
        return "\n".join(lines)


# ── 재학습 1회 실행 및 측정 ─────────────────────────────────────────
def _run_once(full_cv: bool, timer: _Timer, tag: str):
    from learning.batch_retrainer import BatchRetrainer
    from config.settings import RETRAIN_WEEKS_BACK

    retrainer = BatchRetrainer()

    # 1. 데이터 로드
    gc.collect()
    t1 = time.perf_counter()
    with _MemBlock("load") as mem_load:
        X, y_dict, feature_names = retrainer._load_from_db(RETRAIN_WEEKS_BACK)
    timer.mark(f"{tag} 데이터 로드")
    t_load = time.perf_counter() - t1

    if X is None:
        return {"ok": False, "error": "DB 데이터 없음"}

    n_rows, n_cols = X.shape
    horizons = list(y_dict.keys()) if y_dict else []

    log.info(
        "[%s] 데이터 로드 완료: X=%d×%d  호라이즌=%s  소요=%.1fs  peak=%.1fMB",
        tag, n_rows, n_cols, horizons, t_load, mem_load.peak_mb,
    )

    # 2. 재학습 (호라이즌별 타이밍은 내부에서 로깅)
    gc.collect()
    with _MemBlock("retrain") as mem_retrain:
        t2 = time.perf_counter()
        try:
            result = retrainer.retrain_now(
                X=X,
                y_dict=y_dict,
                feature_names=feature_names,
                force=True,
                intraday=False,
                full_cv=full_cv,
            )
        except MemoryError as e:
            result = {"ok": False, "error": f"MemoryError: {e}"}
        except Exception as e:
            result = {"ok": False, "error": str(e)}
        t_retrain = time.perf_counter() - t2

    timer.mark(f"{tag} 재학습 완료")

    log.info(
        "[%s] 재학습 완료: ok=%s  소요=%.1fs  peak=%.1fMB",
        tag, result.get("ok"), t_retrain, mem_retrain.peak_mb,
    )

    return {
        "ok":            result.get("ok"),
        "error":         result.get("error"),
        "n_rows":        n_rows,
        "n_cols":        n_cols,
        "t_load_s":      round(t_load, 1),
        "t_retrain_s":   round(t_retrain, 1),
        "peak_load_mb":  round(mem_load.peak_mb, 1),
        "peak_train_mb": round(mem_retrain.peak_mb, 1),
        "horizons":      horizons,
        "full_cv":       full_cv,
    }


# ── 메인 ────────────────────────────────────────────────────────────
def main():
    env = _env_info()
    env_tag = "32bit" if env["bits"] == "32-bit" else "64bit"
    result_path = os.path.join(
        _ROOT,
        f"_measure_retrain_result_{env_tag}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
    )

    header = (
        f"{'='*60}\n"
        f"EOD 재학습 소요 시간 실측\n"
        f"실행일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Python:  {env['python']}\n"
        f"sklearn: {env['sklearn']}\n"
        f"numpy:   {env['numpy']}\n"
        f"OS:      {env['os']}\n"
        f"{'='*60}\n"
    )
    print(header)

    timer = _Timer()
    timer.mark("시작")
    results = []

    # ── Case 1: full_cv=False (현재 장중 캡 20k 적용) ───────────────
    print("[CASE 1] full_cv=False (현행 장중 캡 20k)")
    r1 = _run_once(full_cv=False, timer=timer, tag="C1")
    results.append(r1)

    # ── Case 2: full_cv=True (EOD 캡 해제 — 현재 OOM 발생 케이스) ──
    print("\n[CASE 2] full_cv=True (EOD 전체 데이터, 절단 없음)")
    r2 = _run_once(full_cv=True, timer=timer, tag="C2")
    results.append(r2)

    timer.mark("전체 완료")

    # ── 결과 보고서 ─────────────────────────────────────────────────
    def _fmt(r, case_label):
        if not r.get("ok"):
            status = f"실패: {r.get('error', '?')}"
        else:
            status = "성공"
        return (
            f"\n[{case_label}]\n"
            f"  상태:          {status}\n"
            f"  데이터:        {r.get('n_rows','?')}행 × {r.get('n_cols','?')}열\n"
            f"  full_cv:       {r.get('full_cv')}\n"
            f"  데이터 로드:   {r.get('t_load_s','?')}s  (peak {r.get('peak_load_mb','?')} MB)\n"
            f"  재학습:        {r.get('t_retrain_s','?')}s  (peak {r.get('peak_train_mb','?')} MB)\n"
            f"  합계:          {round((r.get('t_load_s') or 0) + (r.get('t_retrain_s') or 0), 1)}s\n"
        )

    report = (
        header
        + "\n단계별 타이밍:\n" + timer.report() + "\n"
        + _fmt(r1, "CASE 1: full_cv=False (장중 캡 20k)")
        + _fmt(r2, "CASE 2: full_cv=True  (절단 없음)")
        + f"\n결과 파일: {result_path}\n"
        + f"{'='*60}\n"
    )

    print(report)

    with open(result_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n[완료] 결과 저장: {result_path}")


if __name__ == "__main__":
    main()
