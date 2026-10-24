# -*- coding: utf-8 -*-
"""[MW0602 신동 주체 리뉴얼] 신동 전용 EOD — 미륵 재학습과 분리한 장후 작업.

왜 있는가
---------
신동 V4 의 ATR14·맥점은 08:50 `premarket_levels` 산출이 만들고, 그 산출은 EOD 에 굳힌
**이력 캐시**(`data/premarket_levels_history.json`)만 읽는다. 그런데 그 캐시를 매일 갱신하는
`scripts/premarket_levels_eod.run_eod()` 는 **미륵 EOD 재학습 스크립트 안**(`retrain_eod.py` ·
`scripts/eod_retrain.py`)에서만 불려 왔다. 미륵을 휴면시키며 재학습 예약작업을 끄면 캐시가
조용히 낡는다 — 08:50 산출이 낡은 이력으로 계산되고, 08:50 이 실패한 날 V4 ATR 폴백 ②(재계산,
이력 마지막 10일 이내)가 막혀 신규 진입이 없어질 수 있다(계획서 §1 P4).

그래서 재학습과 **같은 일 중 신동이 쓰는 것만** 여기로 옮긴다:
  ① 맥점 이력 캐시 갱신 + 당일 채점          (`premarket_levels_eod.run_eod`)
  ② 연결선물(10100) 적재 신선도               (`regular_freshness.check`)
  ③ 옵션 투자자 흐름(7222) 마감 구간 신선도   (`option_flow_freshness.check`) — 신동 신호 원천

하지 않는 것: GBM 재학습 · 스케일러 재적합 · 검증 캠페인 리포트 · SHAP 심사(전부 미륵 전용).

규약
----
· 미륵 `daily_close` 완료 마커(`data/daily_close_done_YYYYMMDD.txt`)를 기다린 뒤 돈다(최대 20분) —
  마지막 분봉 쓰기가 DB 에 반영된 뒤 캐시를 갱신해야 한다(retrain_eod.py 와 같은 이유).
· 예외를 밖으로 던지지 않는다 — 각 단계는 독립이다. 실패는 「미측정」으로 남긴다(계측 4원칙 ②).
· 완료 마커 `data/shindong_eod_done_YYYYMMDD.txt` — 내일 장전 점검이 캐시 신선도와 함께 본다.
· 종료코드: 0 = 세 단계 모두 정상 · 1 = 하나 이상 결손/미측정 · 2 = 캐시 갱신 자체 실패.
· 장중 실행 금지 — `premarket_levels_eod` 와 같은 guard_intraday 원칙(456차, 대형 DB 장중 스캔 금지).

실행:
    python scripts/shindong_eod.py                 # 오늘(마감 마커 대기)
    python scripts/shindong_eod.py --no-wait       # 마커 대기 생략(수동 재실행)
    python scripts/shindong_eod.py --date 2026-10-26
예약작업: TASK_SHINDONG_EOD_INSTALL.bat (평일 15:55)
"""
import argparse
import datetime
import io
import logging
import os
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# [537차] conda 활성화 없이 예약작업이 python.exe 를 직접 부른다 — numpy 계열 import 보다 먼저.
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402

ensure_conda_dll_path()

_TODAY = datetime.date.today().strftime("%Y%m%d")
LOG_PATH = os.path.join(_ROOT, "logs", "shindong_eod_%s.log" % _TODAY)


def _setup_log():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    log = logging.getLogger("SHINDONG_EOD")
    if not log.handlers:
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fh.setFormatter(fmt)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        log.addHandler(fh)
        log.addHandler(sh)
        log.setLevel(logging.INFO)
    return log


def wait_for_daily_close(log, ymd, max_wait_min=20, poll_sec=30, sleep=time.sleep, now=None):
    """미륵 프로그램의 daily_close 완료 마커를 기다린다. → True=확인 / False=타임아웃(그래도 진행)."""
    marker = os.path.join(_ROOT, "data", "daily_close_done_%s.txt" % ymd)
    now = now or datetime.datetime.now
    deadline = now() + datetime.timedelta(minutes=max_wait_min)
    while now() < deadline:
        if os.path.exists(marker):
            log.info("[WaitDC] daily_close 완료 확인 — %s", marker)
            return True
        log.info("[WaitDC] daily_close 대기 중 (%s까지)", deadline.strftime("%H:%M:%S"))
        sleep(poll_sec)
    log.warning("[WaitDC] daily_close %d분 대기 타임아웃 — 마지막 분봉 미반영 가능성 있으나 진행", max_wait_min)
    return False


def run(date_str=None, wait=True, log=None, steps=None):
    """세 단계 실행 → dict(levels, regular, option_flow, exit_code). steps 는 테스트 주입용."""
    log = log or _setup_log()
    date_str = date_str or datetime.date.today().isoformat()
    ymd = date_str.replace("-", "")
    out = {"date": date_str, "levels": None, "regular": None, "option_flow": None}
    if steps is None:
        from scripts.premarket_levels_eod import run_eod as _levels
        from scripts.regular_freshness import check as _reg
        from scripts.option_flow_freshness import check as _of
        steps = {"levels": lambda: _levels(date_str=date_str, log=log), "regular": _reg, "option_flow": _of}
    if wait:
        wait_for_daily_close(log, ymd)
    log.info("[ShindongEOD] 시작 %s — 맥점 이력 캐시 · 연결선물 신선도 · 7222 흐름 신선도 (미륵 재학습과 분리)",
             date_str)

    code = 0
    # ① 맥점 이력 캐시 — 신동 ATR14·맥점의 원천. 실패하면 종료코드 2.
    try:
        r = steps["levels"]()
        out["levels"] = r
        ref = (r or {}).get("refreshed")
        if not ref:
            log.error("[ShindongEOD] 맥점 이력 캐시 갱신 결과 없음 — 내일 08:50 ATR14 가 낡은 이력으로 산출된다")
            code = 2
        else:
            log.info("[ShindongEOD] 맥점 이력 캐시 last_date=%s · 세션 %s",
                     ref.get("last_date"), ref.get("sessions"))
            if str(ref.get("last_date") or "") != date_str:
                log.warning("[ShindongEOD] 캐시 last_date(%s) ≠ 오늘(%s) — 오늘 봉이 품질 제외됐거나 raw_candles 결손",
                            ref.get("last_date"), date_str)
                code = max(code, 1)
    except Exception as e:
        log.error("[ShindongEOD] 맥점 EOD 단계 실패 — 미측정: %r", e)
        code = 2
    # ②·③ 신선도 — 결과만 본다(수집은 각자의 예약작업). 미측정 ≠ 결손 없음.
    for key, tag in (("regular", "[RegularFresh]"), ("option_flow", "[OptionFlowFresh]")):
        try:
            r = steps[key]()
            out[key] = r
            if r.get("status") == "ok":
                log.info("%s", r.get("line"))
            else:
                log.warning("%s", r.get("line"))
                code = max(code, 1)
        except Exception as e:
            log.warning("%s 검사 실패 — 미측정이다(「결손 없음」이 아니다): %r", tag, e)
            code = max(code, 1)

    out["exit_code"] = code
    try:
        mk = os.path.join(_ROOT, "data", "shindong_eod_done_%s.txt" % ymd)
        with io.open(mk, "w", encoding="utf-8") as f:
            f.write("completed: %s exit=%d\n" % (datetime.datetime.now().isoformat(timespec="seconds"), code))
    except Exception as e:
        log.warning("[ShindongEOD] 완료 마커 기록 실패: %r", e)
    log.info("[ShindongEOD] 종료 exit=%d", code)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="신동 전용 EOD(맥점 이력 캐시 · 신선도)")
    ap.add_argument("--date", default=None)
    ap.add_argument("--no-wait", action="store_true")
    a = ap.parse_args(argv)
    now = datetime.datetime.now()
    if a.date is None and datetime.time(8, 40) <= now.time() < datetime.time(15, 40):
        print("[ShindongEOD] 장중 실행 금지(15:40 이후) — 대형 DB 장중 스캔 규약(456차)")
        return 2
    return run(a.date, wait=not a.no_wait)["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
