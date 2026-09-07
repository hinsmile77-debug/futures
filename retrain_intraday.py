r"""
미륵이 장중 GBM 재학습 스크립트 (py310_64 전용)
-----------------------------------------------
32비트 main.py가 subprocess로 호출 — 64비트 환경에서 OOM 없이 실행.
EOD retrain_eod.py와 달리 intraday 경량 모드 지원.

사용:
    py310_64\python.exe retrain_intraday.py <result_json_path> <force:0|1> <intraday:0|1>

인수:
    result_json_path : 완료 결과를 쓸 JSON 파일 경로 (main.py가 poll로 읽음)
    force            : 0=성능 하락 시 교체 스킵, 1=강제 교체
    intraday         : 0=full 재학습(300그루/전체봉), 1=경량(100그루/20k봉)

완료 결과 JSON:
    {"ok": true/false, "error": "...", "elapsed_sec": N.N, "data_size": N, ...}

로그:
    logs/retrain_intraday_{YYYYMMDD_HHMMSS}.log
"""
import sys
import os
import gc
import time
import json
import datetime
import logging
import traceback

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ── [MW0601 537차] BLAS DLL 경로 보장 — **numpy import보다 먼저** ──────────────
# 이 스크립트는 `main.py`(py37_32)가 `Popen([PYTHON_64_EXEC, ...])`로 띄우며,
# 자식은 **py37_32의 환경을 상속**한다. 두 env의 MKL은 파일명이 달라
# (py37_32 `mkl_rt.1.dll` vs py310_64 `mkl_rt.3.dll`) 상속된 PATH로는 찾을 수 없고,
# BLAS를 밟는 순간 **stderr 한 줄 없이 프로세스가 즉사**한다(0xC06D007F).
# 448차가 `retrain_eod.py`에 넣은 것과 같은 조치인데 이쪽만 빠져 있었다.
# ⚠ 지금 사고가 없는 것은 장중 경량 모드가 HistGBM/RobustScaler만 써서
#   BLAS를 안 밟기 때문이다 — 상관·회귀·scipy.stats가 한 줄 들어오면 즉사한다.
# 근거: docs/정기점검/매일점검/MW0601-20260907-BLAS즉사-딥다이브.md
_dll_added = []
try:
    from utils.dll_bootstrap import ensure_conda_dll_path
    _dll_added = ensure_conda_dll_path()
except Exception as _dll_exc:                      # 부트스트랩 실패로 재학습을 막지 않는다
    _dll_added = ["<bootstrap 실패: %s>" % _dll_exc]

_NOW_STR  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
_LOG_PATH = os.path.join(_ROOT, "logs", f"retrain_intraday_{_NOW_STR}.log")
os.makedirs(os.path.join(_ROOT, "logs"), exist_ok=True)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_fh  = logging.FileHandler(_LOG_PATH, encoding="utf-8")
_fh.setFormatter(_fmt)
_ch  = logging.StreamHandler(sys.stdout)
_ch.setFormatter(_fmt)
logging.root.handlers = []
logging.root.setLevel(logging.INFO)
logging.root.addHandler(_fh)
logging.root.addHandler(_ch)
logging.getLogger("LEARNING").setLevel(logging.INFO)

log = logging.getLogger("RETRAIN_INTRADAY")


def _check_env():
    bits = "64-bit" if sys.maxsize > 2**32 else "32-bit"
    log.info("=" * 50)
    log.info("미륵이 장중 재학습 시작 | Python %s %s", sys.version.split()[0], bits)
    log.info("=" * 50)
    # [537차] 계측 4원칙 ④ — 조치가 실제로 적용됐는지 로그로 남긴다.
    #   "보강 N개" = 이 프로세스가 PATH를 고쳤다(정상 — 부모가 py37_32라 당연하다)
    #   "이미 충족" = 부모가 이미 py310_64 활성화 상태였다(수동 실행 등)
    #   "bootstrap 실패" = 모듈 import 실패 — BLAS를 밟으면 즉사할 수 있다
    log.info("[DLL] BLAS 경로 %s", ("보강 %d개: %s" % (len(_dll_added), _dll_added))
             if _dll_added else "이미 충족")
    if bits != "64-bit":
        log.error("32-bit Python 감지 — py310_64 환경으로 실행해야 합니다. 종료.")
        sys.exit(2)


def main():
    _check_env()

    # 인수 파싱
    if len(sys.argv) < 4:
        log.error("사용법: retrain_intraday.py <result_json> <force:0|1> <intraday:0|1>")
        sys.exit(1)

    result_json_path = sys.argv[1]
    force    = sys.argv[2].strip() == "1"
    intraday = sys.argv[3].strip() == "1"
    # [MW0602 457차] argv[4] = 교체 대상 호라이즌 CSV(선택). 없거나 빈 문자열이면
    # 전체 = 457차 이전 동작. 구버전 main.py가 4개 인수만 넘겨도 안전하다.
    horizons = None
    if len(sys.argv) >= 5:
        _hz_raw = sys.argv[4].strip()
        if _hz_raw:
            horizons = [h.strip() for h in _hz_raw.split(",") if h.strip()]

    log.info("파라미터: force=%s intraday=%s horizons=%s result_path=%s",
             force, intraday, horizons or "ALL", result_json_path)

    t0 = time.perf_counter()
    result = {"ok": False, "error": "unknown", "elapsed_sec": 0.0}

    try:
        from learning.batch_retrainer import BatchRetrainer

        gc.collect()
        retrainer = BatchRetrainer()
        result = retrainer.retrain_now(
            force=force, intraday=intraday, horizons=horizons,
        )
        result["elapsed_sec"] = round(time.perf_counter() - t0, 1)

        if result.get("ok"):
            log.info("재학습 완료 | %.1fs 데이터=%s행",
                     result["elapsed_sec"], result.get("data_size", "?"))
        else:
            log.warning("재학습 실패: %s", result.get("error", "?"))

    except Exception as _e:
        result = {
            "ok": False,
            "error": str(_e),
            "elapsed_sec": round(time.perf_counter() - t0, 1),
        }
        log.error("재학습 예외: %s\n%s", _e, traceback.format_exc())

    finally:
        # 결과 JSON 기록 — main.py가 poll() 후 읽음
        try:
            os.makedirs(os.path.dirname(result_json_path), exist_ok=True)
            with open(result_json_path, "w", encoding="utf-8") as _f:
                json.dump(result, _f, ensure_ascii=False)
            log.info("결과 JSON 저장: %s", result_json_path)
        except Exception as _we:
            log.error("결과 JSON 저장 실패: %s", _we)

    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
