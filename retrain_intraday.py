"""
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
