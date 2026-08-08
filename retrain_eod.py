"""
미륵이 EOD 재학습 스크립트 (py310_64 전용)
---
윈도우 스케줄러에서 매일 15:45 자동 실행.
main.py 종료 후 독립 프로세스로 full 재학습 수행.

실행 환경: py310_64 (Python 3.10 64-bit, scikit-learn=1.0.2)
저장 형식: pickle protocol=4 → py37_32 main.py 로드 호환

로그: logs/retrain_eod_{YYYYMMDD}.log
완료 마커: data/eod_retrain_done_{YYYYMMDD}.txt
  → main.py EarlyWarmup에서 이 파일 확인 → 불필요 warmup 스킵
"""

import sys
import os
import gc
import time
import datetime
import json
import logging
import traceback

# ── 프로젝트 루트 설정 ────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ── [MW0601 448차] BLAS DLL 경로 보장 — **numpy import보다 먼저** ──────────────
# 이 파일은 작업 스케줄러 `MireukiEODRetrain`의 직접 실행 대상이고, 스케줄러는
# **conda 활성화 없이** py310_64\python.exe를 부른다. 그러면 그 env의 Library\bin이
# PATH에 없어 MKL delay-load가 실패하고 **프로세스가 stderr 한 줄 없이 즉사**한다
# (0xC06D007F). 08-01·08-07 주간 리포트 2회 결번의 원인이 이것이다.
# ⚠ 자식 프로세스(campaign_steps가 띄우는 리포트 생성기 등)도 os.environ 상속으로
#   함께 보호된다 — 실제로 죽은 것이 그 자식이었다.
# 상세·실측은 utils/dll_bootstrap.py 참조.
from utils.dll_bootstrap import ensure_conda_dll_path  # noqa: E402
ensure_conda_dll_path()

_TODAY = datetime.datetime.now().strftime("%Y%m%d")
_LOG_PATH    = os.path.join(_ROOT, "logs", f"retrain_eod_{_TODAY}.log")
_MARKER_PATH = os.path.join(_ROOT, "data", f"eod_retrain_done_{_TODAY}.txt")
_FAIL_PATH   = os.path.join(_ROOT, "data", f"eod_retrain_fail_{_TODAY}.txt")

os.makedirs(os.path.join(_ROOT, "logs"), exist_ok=True)
os.makedirs(os.path.join(_ROOT, "data"), exist_ok=True)

# ── 로거 독립 설정 ────────────────────────────────────────────────
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_fh  = logging.FileHandler(_LOG_PATH, encoding="utf-8")
_fh.setFormatter(_fmt)
_ch  = logging.StreamHandler(sys.stdout)
_ch.setFormatter(_fmt)

logging.root.handlers = []
logging.root.setLevel(logging.INFO)
logging.root.addHandler(_fh)
logging.root.addHandler(_ch)

# 하위 모듈 로거 레벨 제어
logging.getLogger("LEARNING").setLevel(logging.INFO)

log = logging.getLogger("EOD_RETRAIN")


# ── 환경 검증 ─────────────────────────────────────────────────────
def _check_env():
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

    log.info("=" * 55)
    log.info("미륵이 EOD 재학습 시작")
    log.info("Python : %s %s", sys.version.split()[0], bits)
    log.info("sklearn: %s", sk_ver)
    log.info("numpy  : %s", np_ver)
    log.info("=" * 55)

    if bits != "64-bit":
        log.error("32-bit Python 감지 — py310_64 환경으로 실행해야 합니다. 종료.")
        sys.exit(2)


# ── 알림 ──────────────────────────────────────────────────────
def _notify_fail(msg: str):
    try:
        from utils.notify import notify as _nfy
        _nfy(f"[EOD재학습] 실패: {msg}", "ERROR")
    except Exception:
        pass


def _notify_eod_done(horizons_ok: int, horizons_total: int, t_total: float):
    """EOD 재학습 완료 + calibration 역전 상태를 Slack으로 통보."""
    try:
        from utils.notify import notify as _nfy

        # calibration_metrics.json에서 역전 상태 확인
        _metrics_path = os.path.join(_ROOT, "calibration_metrics.json")
        _inv_line = ""
        if os.path.exists(_metrics_path):
            try:
                with open(_metrics_path, "r", encoding="utf-8") as _f:
                    _m = json.load(_f)
                _inv = _m.get("conf_inversion") or {}
                if _inv.get("inverted"):
                    _hi  = float(_inv.get("high_acc", 0.0) or 0.0)
                    _lo  = float(_inv.get("low_acc",  0.0) or 0.0)
                    _gap = float(_inv.get("gap",      0.0) or 0.0)
                    _ece = float(_inv.get("ece_high", 0.0) or 0.0)
                    _inv_line = (
                        f"\n⚠️ 신뢰도 역전 감지\n"
                        f"  고신뢰(0.6+) acc {_hi:.1%} < 저신뢰 {_lo:.1%} (gap -{_gap:.1%}p)\n"
                        f"  ECE_high {_ece:.3f} | HCGuard 자동 차단 중"
                    )
                else:
                    _ece_overall = float((_m.get("overall") or {}).get("ece", 0.0) or 0.0)
                    _inv_line = f"\n캘리브레이션 ECE {_ece_overall:.3f} (역전 없음 ✅)"
            except Exception:
                pass

        _nfy(
            f"EOD 재학습 완료 ✅\n"
            f"호라이즌 {horizons_ok}/{horizons_total} 교체 | 소요 {t_total:.0f}s"
            f"{_inv_line}",
            "INFO",
        )
    except Exception:
        pass


# ── P8: EOD 스케일러 재적합 ──────────────────────────────────────
def p8_scaler_refit() -> bool:
    """GBM 재학습 직후 최신 500봉 기준으로 스케일러 재적합.

    retrain_now()는 26주 데이터 기준 스케일러를 pkl에 포함해 저장한다.
    daily_close()에서 P8이 먼저 실행되면 이 재학습이 나중에 덮어쓰므로
    P8 효과가 무효화됐던 문제를 여기(재학습 직후)로 이동해 해결.
    재학습 성공/실패 무관하게 실행 — 실패 시에도 기존 pkl 기준으로 재적합.
    """
    try:
        from learning.batch_retrainer import BatchRetrainer
        from model.multi_horizon_model import MultiHorizonModel
        from config.settings import SCALER_WARMUP_LOOKBACK_BARS

        retrainer = BatchRetrainer()
        X, feature_names = retrainer.load_features_for_warmup(
            lookback_bars=SCALER_WARMUP_LOOKBACK_BARS
        )
        if X is None or len(X) == 0:
            log.warning("[P8] 스케일러 재적합 스킵 — 데이터 없음")
            return False

        model = MultiHorizonModel()
        result = model.refit_scalers_only(
            X,
            feature_names,
            trigger_ts    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            trigger_type  = "E_EOD",
            trigger_reason= "retrain_eod.py P8 — GBM 재학습 직후 500봉 스케일러 최종화",
        )
        elapsed  = (result or {}).get("elapsed_sec", 0)
        horizons = (result or {}).get("horizons", [])
        log.info(
            "[P8] 스케일러 재적합 완료 n=%d봉 elapsed=%.2fs horizons=%s",
            len(X), elapsed, horizons,
        )

        # session_state 기록:
        #   p8_last_success_date → 내일 EarlyWarmup·EKS 원인 진단용
        #   eod_retrain_ok_date  → 내일 08:55 PreRetrain 스킵 판단용 (main.py:3224)
        # 구조적 문제: daily_close()(15:40)는 EOD 완료 전 체크라 마커가 없어 eod_retrain_ok_date를
        # 기록 못함 → PreRetrain이 매일 fallback(마커파일 직접확인)에 의존하게 됨.
        # 근본 수정: retrain_eod.py 완료 시점(15:47+)에 두 키를 모두 기록.
        try:
            _ss_path = os.path.join(_ROOT, "data", "session_state.json")
            _ss: dict = {}
            if os.path.exists(_ss_path):
                with open(_ss_path, "r", encoding="utf-8") as _f:
                    _ss = json.load(_f)
            _today = datetime.date.today().isoformat()
            _ss["p8_last_success_date"] = _today
            _ss["eod_retrain_ok_date"]  = _today   # main.py PreRetrain 스킵용 (daily_close 레이스 해소)
            with open(_ss_path, "w", encoding="utf-8") as _f:
                json.dump(_ss, _f, ensure_ascii=False, indent=2)
            log.info("[P8] session_state p8_last_success_date + eod_retrain_ok_date 기록 완료")
        except Exception as _sse:
            log.warning("[P8] session_state 기록 실패 (무해): %s", _sse)

        return True

    except Exception as exc:
        log.warning("[P8] 스케일러 재적합 예외 (무해): %s", exc)
        return False


# ── daily_close() 완료 대기 ──────────────────────────────────────
def _wait_for_daily_close(max_wait_min: int = 20, poll_sec: int = 30) -> bool:
    """main.py daily_close() 완료를 확인 후 반환 — pkl 경합 방지.

    daily_close() 마지막에 data/daily_close_done_YYYYMMDD.txt 를 기록한다.
    launcher가 삭제하는 _exit_normally 와 달리 이 파일은 launcher가 건드리지 않아
    EOD 재학습(16:10)이 안정적으로 감지할 수 있다.

    반환값: True=정상 완료 확인, False=타임아웃 후 강제 진행
    """
    _today = datetime.date.today().strftime("%Y%m%d")
    _marker = os.path.join(_ROOT, "data", f"daily_close_done_{_today}.txt")
    _deadline = datetime.datetime.now() + datetime.timedelta(minutes=max_wait_min)

    log.info(
        "[WaitDC] daily_close() 완료 대기 시작 (최대 %d분, %s까지)",
        max_wait_min, _deadline.strftime("%H:%M:%S"),
    )

    while datetime.datetime.now() < _deadline:
        if os.path.exists(_marker):
            try:
                with open(_marker, "r", encoding="utf-8") as _f:
                    _ts = _f.read().strip()
                log.info("[WaitDC] daily_close() 완료 확인 (%s) — EOD 재학습 시작", _ts)
                return True
            except Exception as _e:
                log.debug("[WaitDC] 마커 읽기 실패 (재시도): %s", _e)

        remaining = (_deadline - datetime.datetime.now()).seconds // 60
        log.info(
            "[WaitDC] daily_close() 대기 중 — 잔여 %d분 (%s까지)",
            remaining, _deadline.strftime("%H:%M:%S"),
        )
        time.sleep(poll_sec)

    log.warning(
        "[WaitDC] daily_close() %d분 대기 타임아웃 — pkl 경합 위험 있으나 강제 진행",
        max_wait_min,
    )
    try:
        from utils.notify import notify as _nfy
        _nfy(
            f"⚠️ EOD재학습 — daily_close() {max_wait_min}분 대기 타임아웃\n"
            "STEP 3 장중 재학습 미완료 상태로 강제 진행 (pkl 경합 가능성)",
            "WARNING",
        )
    except Exception:
        pass
    return False


# ── [333차 후속] 검증 캠페인 주간 스텝 ────────────────────────────
# docs/260705_OFFENSE_READINESS_AUDIT_AND_NEXT_PHASE.md §4-1이 "매주 금 EOD 체인에
# 연결"하도록 설계했으나, 실제 Windows 작업 스케줄러(Maitreya_EODretrain)는 이 파일
# (retrain_eod.py)을 실행할 뿐 scripts/eod_retrain.py(캠페인 체인 보유, 수동/Phase2
# 재학습용 별개 스크립트라 삭제 불가)는 스케줄된 적이 없어 §4-1 자동화가 죽어있었음
# (07-05 단 1회, 0바이트 로그). 로직은 scripts/campaign_steps.py 공용 모듈로 분리해
# 두 스크립트가 함께 참조한다(333차 후속4, 중복 방지 — 후속3의 휴장일 보정을 두
# 파일에 각각 손으로 적용해야 했던 유지보수 비용을 확인하고 리팩터링).
from scripts.campaign_steps import campaign_due as _campaign_due
from scripts.campaign_steps import run_campaign_steps as _run_campaign_steps_impl


def _run_campaign_steps():
    _run_campaign_steps_impl(log, _ROOT)


# ── 메인 재학습 ───────────────────────────────────────────────────
def main():
    _check_env()

    # 중복 실행 방지: 완료 마커가 이미 존재하면 스킵
    if os.path.exists(_MARKER_PATH):
        log.info("완료 마커 존재 — 오늘 재학습 이미 완료됨. 종료.")
        sys.exit(0)

    # daily_close() 완료 대기 — STEP 3 장중 GBM 재학습과 pkl 경합 방지
    # _exit_normally 파일(daily_close 마지막에 기록)의 오늘 날짜를 확인.
    # 스케줄러가 16:10에 실행되더라도 daily_close가 늦으면 추가 대기.
    _wait_for_daily_close(max_wait_min=20, poll_sec=30)

    t_start = time.perf_counter()

    try:
        from learning.batch_retrainer import BatchRetrainer
        from config.settings import RETRAIN_WEEKS_BACK

        retrainer = BatchRetrainer()

        log.info("데이터 로드 시작 (weeks_back=%d)", RETRAIN_WEEKS_BACK)
        gc.collect()
        t1 = time.perf_counter()
        X, y_dict, feature_names = retrainer._load_from_db(RETRAIN_WEEKS_BACK)
        t_load = time.perf_counter() - t1

        if X is None:
            raise RuntimeError("DB 데이터 없음 — raw_data.db 확인 필요")

        log.info(
            "데이터 로드 완료: %d행 × %d열  (%.1fs)",
            X.shape[0], X.shape[1], t_load,
        )

        gc.collect()
        # [346차] force=True → False. 기존엔 CV acc가 구모델보다 크게 나빠져도
        # 무조건 교체됐다(0715진입청산검토.md 딥다이브 — 1m/3m/5m CV acc 하락에도
        # 강제 교체된 사례 확인). force=False로 바꾸면 batch_retrainer.py의
        # 호라이즌별 EOD 모델가드(EOD_MODEL_GUARD_DROP_TOLERANCE)가 살아나
        # 하락폭이 허용치를 넘는 호라이즌만 구모델 유지 + 참고용 저장 + 알림한다.
        log.info(
            "재학습 시작: force=False(346차 EOD 모델가드 적용), intraday=False, full_cv=True  "
            "(절단 없음, 300그루, 3-fold CV)"
        )
        t2 = time.perf_counter()
        result = retrainer.retrain_now(
            X=X,
            y_dict=y_dict,
            feature_names=feature_names,
            force=False,
            intraday=False,
            full_cv=True,
        )
        t_retrain = time.perf_counter() - t2
        t_total   = time.perf_counter() - t_start

        if not result.get("ok"):
            raise RuntimeError(f"retrain_now 실패: {result.get('error')}")

        horizons_ok = sum(
            1 for r in result.get("horizons", {}).values() if r.get("replaced")
        )
        # [346차] 가드로 교체가 보류된 호라이즌 수 — 0이 정상, >0이면 요약에서
        # 바로 눈에 띄도록 별도 표기(전체 로그를 훑지 않아도 발동 여부를 알 수 있게).
        horizons_guarded = sum(
            1 for r in result.get("horizons", {}).values() if r.get("guard_rejected")
        )
        log.info(
            "재학습 완료: 호라이즌 교체=%d/%d  가드보류=%d  재학습=%.1fs  로드=%.1fs  합계=%.1fs",
            horizons_ok,
            len(result.get("horizons", {})),
            horizons_guarded,
            t_retrain,
            t_load,
            t_total,
        )

        # 완료 마커 기록
        with open(_MARKER_PATH, "w", encoding="utf-8") as f:
            f.write(
                f"completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"rows: {X.shape[0]}\n"
                f"cols: {X.shape[1]}\n"
                f"horizons_replaced: {horizons_ok}/{len(result.get('horizons', {}))}\n"
                f"t_load_s: {t_load:.1f}\n"
                f"t_retrain_s: {t_retrain:.1f}\n"
                f"t_total_s: {t_total:.1f}\n"
            )
        log.info("완료 마커 저장: %s", _MARKER_PATH)

        # RegimeFingerprint 학습분포 갱신 — 이번 EOD(26주) 재학습에 실제 사용된
        # CORE 3피처(cvd_divergence/vwap_position/ofi_norm) 분포를 PSI 기준선으로 저장.
        # 299차가 만든 "_try_bootstrap_baseline() 당일 50분 스냅샷" 임시방편을
        # 실제 WFA 학습분포로 대체 — main.py는 다음 재기동 시 이 파일을 읽어 사용.
        # [MW0602 423차] 백필 행 제외 — PSI가 7거래일 연속 100% CRITICAL이던 근본원인.
        #   `scripts/backfill_features.py:341`이 소급 생성 행에 박는 마커
        #   `feature_quality_score == 0.3`을 기준으로 걸러낸다. 백필 행은 호가·수급이
        #   없어 미시구조 피처를 0.0으로 채우는데(실측: 백필 24,824행의 ofi_norm이
        #   100.0% 정확히 0.0, 라이브 15,176행은 1.6%), 그 행이 학습 모집단의 62%를
        #   차지해 기준선에 거대한 0.0 점질량을 만든다. 그 결과 라이브 값이 정상
        #   범위여도 그 한 개 빈에서만 PSI 기여가 2.73(임계 0.30의 9배)이 나온다.
        #   371차가 균등폭→분위수 비닝으로 재설계했는데도 CRITICAL이 안 풀린 이유가
        #   이것이다 — 비닝 방식이 아니라 **모집단**이 문제였다.
        #   ⚠ 계측 전용 수정이다. `FP_CRITICAL_GRADE_BLOCK_ENABLED = False`이므로
        #     라이브 진입 판단은 무변경이며, CLAUDE.md 실전전환기준 ⑦의 해제 조건
        #     ("정상 구간에서 PSI가 오르내리는 것을 실측 확인")을 처음으로 시험 가능하게 한다.
        _BACKFILL_QUALITY_MARKER = 0.3
        # [MW0602 424차] 허용오차는 **float32 유효자리에 맞춰야 한다** — 이 한 줄 때문에
        # 423차의 백필 제외가 08-04 EOD에서 "백필 0행 제외"로 아무것도 걸러내지 못했다.
        #   `X`는 learning/batch_retrainer.py:_load_from_db()가 `dtype=np.float32`로 만든다.
        #   float32(0.3) = 0.30000001192092896 → |값 - 0.3| = 1.192e-08.
        #   구 허용오차 1e-9는 그보다 한 자릿수 촘촘해서 **모든 백필 행이 필터를 통과**했다.
        # 왜 423차 오프라인 검증에서는 맞았나: scripts/scan_backfill_exposure.py는 같은
        #   1e-9를 쓰지만 raw_features JSON dict(float64)를 읽어 0.3이 정확히 일치한다.
        #   오프라인 float64 / 프로덕션 float32 — 419·420·421차가 반복 지적한
        #   "오프라인만 검증" 패턴이 같은 형태로 재발한 것이다.
        # 1e-6은 float32 유효자리(≈3e-8)보다 넉넉하면서, 실제로 쓰이는 다른 품질점수
        #   (0.76·0.78·0.82·0.84·0.86·0.88·0.9·0.94·1.0 — 08-04 실측 전수)와는
        #   최소 0.46 떨어져 있어 오분류 여지가 없다.
        _BACKFILL_MARKER_TOL = 1e-6
        try:
            from strategy.regime_fingerprint import (
                get_fingerprint, _CORE_FEATURES, _N_BINS,
            )
            # save_training_fingerprint()가 피처별로 요구하는 최소 표본(_N_BINS * 2)과
            # 같은 기준. 이 아래로 떨어지면 그 피처가 통째로 스킵돼 기준선이 빈다.
            _N_BINS_MIN_ROWS = _N_BINS * 2
            _core_idx = {
                f: feature_names.index(f)
                for f in _CORE_FEATURES
                if f in feature_names
            }
            if len(_core_idx) == len(_CORE_FEATURES):
                _q_idx = (
                    feature_names.index("feature_quality_score")
                    if "feature_quality_score" in feature_names else None
                )
                _all_rows = list(range(X.shape[0]))
                if _q_idx is None:
                    _rows, _excluded = _all_rows, 0
                    log.warning(
                        "[RegimeFingerprint] feature_quality_score 미포함 — 백필 행 제외 불가, "
                        "전체 %d행으로 기준선 생성(PSI가 과대평가될 수 있음)", len(_all_rows),
                    )
                else:
                    _rows = [
                        i for i in _all_rows
                        if abs(float(X[i, _q_idx]) - _BACKFILL_QUALITY_MARKER)
                        > _BACKFILL_MARKER_TOL
                    ]
                    _excluded = len(_all_rows) - len(_rows)
                    # [MW0602 424차] 회귀 가드 — 0행 제외는 구조적으로 불가능하다.
                    # 26주 창의 백필 비중은 08-04 실측 64.7%(44,125행 중 28,564행)이고,
                    # 백필이 정말로 0이 되려면 26주 전체가 라이브 수집이어야 한다.
                    # 그런 날이 실제로 오면 이 WARNING은 "정상인데 시끄러운" 1줄로
                    # 끝나지만, 필터가 또 죽으면(허용오차·dtype·컬럼명 변경 등)
                    # 이 줄이 없으면 이번처럼 **조용히 무효**가 된다.
                    if _excluded == 0:
                        log.warning(
                            "[RegimeFingerprint] 백필 0행 제외 — 필터가 무효일 수 있다. "
                            "%d행 전수가 마커(%.1f±%.0e)와 불일치. "
                            "X.dtype과 허용오차를 확인할 것(424차: float32 회귀).",
                            len(_all_rows), _BACKFILL_QUALITY_MARKER,
                            _BACKFILL_MARKER_TOL,
                        )
                    # 안전판: 백필이 과반이라 필터 후 표본이 히스토그램 최소요건에
                    # 못 미치면 기준선을 아예 못 만든다 — 그 경우 전체로 되돌린다.
                    if len(_rows) < _N_BINS_MIN_ROWS:
                        log.warning(
                            "[RegimeFingerprint] 백필 제외 후 %d행뿐(최소 %d) — "
                            "전체 %d행으로 폴백",
                            len(_rows), _N_BINS_MIN_ROWS, len(_all_rows),
                        )
                        _rows, _excluded = _all_rows, 0
                _wfa_features = [
                    {f: float(X[i, idx]) for f, idx in _core_idx.items()}
                    for i in _rows
                ]
                get_fingerprint().save_training_fingerprint(_wfa_features)
                log.info(
                    "[RegimeFingerprint] 학습분포 갱신 완료 — %d행 기준 "
                    "(전체 %d행 중 백필 %d행 제외, CORE 3피처 전부 확보)",
                    len(_wfa_features), X.shape[0], _excluded,
                )
            else:
                log.warning(
                    "[RegimeFingerprint] CORE 피처 일부 누락(%s) — 학습분포 갱신 스킵",
                    [f for f in _CORE_FEATURES if f not in _core_idx],
                )
        except Exception as _fp_e:
            log.warning("[RegimeFingerprint] 학습분포 갱신 실패 (무해): %s", _fp_e)

        # 재학습 이력 영속화 — main.py 대시보드(자가학습 탭)의 "마지막 재학습"·"재학습 횟수"와
        # 동일한 session_state.json 키를 공유. EOD는 main.py 프로세스 밖(장외 스케줄러)에서
        # 실행되므로 main.py의 _on_gbm_retrain_done()을 거치지 않는다 — 여기서 직접 갱신하지
        # 않으면 매일 15:45 실행되는 full CV 재학습이 대시보드 카운트에 전혀 반영되지 않는다.
        try:
            _ss_path3 = os.path.join(_ROOT, "data", "session_state.json")
            _ss4: dict = {}
            if os.path.exists(_ss_path3):
                with open(_ss_path3, "r", encoding="utf-8") as _f:
                    _ss4 = json.load(_f)
            _prev_cnt = int(_ss4.get("gbm_total_retrain_count", 0) or 0)
            _ss4["gbm_last_retrain"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            _ss4["gbm_total_retrain_count"] = _prev_cnt + 1
            with open(_ss_path3, "w", encoding="utf-8") as _f:
                json.dump(_ss4, _f, ensure_ascii=False)
            log.info(
                "[EOD] 재학습 이력 저장: %s (%d회)",
                _ss4["gbm_last_retrain"], _ss4["gbm_total_retrain_count"],
            )
        except Exception as _hce:
            log.warning("[EOD] 재학습 이력 저장 실패 (무해): %s", _hce)

        # 이전 실패 마커 제거
        if os.path.exists(_FAIL_PATH):
            os.remove(_FAIL_PATH)

        log.info("=" * 55)
        log.info("EOD 재학습 정상 완료 — 합계 %.1fs", t_total)
        log.info("=" * 55)

        # P8: 재학습 완료 직후 스케일러 재적합
        # 26주 기준 스케일러를 500봉 최신으로 덮어써 내일 시초 z-score 안정화
        p8_scaler_refit()

        # EOD 완료 Slack 알림 (재학습 요약 + calibration 역전 상태)
        _notify_eod_done(horizons_ok, len(result.get("horizons", {})), t_total)

        # [333차 후속] §4-1 검증 캠페인 주간 스텝 (금요일 자동)
        if _campaign_due():
            _run_campaign_steps()

        sys.exit(0)

    except Exception as exc:
        t_total = time.perf_counter() - t_start
        tb = traceback.format_exc()
        log.error("EOD 재학습 예외 (%.1fs 경과):\n%s", t_total, tb)

        with open(_FAIL_PATH, "w", encoding="utf-8") as f:
            f.write(
                f"failed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"error: {exc}\n\n{tb}"
            )

        _notify_fail(str(exc))

        # GBM 재학습이 실패해도 캠페인 판정 리포트(읽기 전용)는 실행할 가치가 있다
        if _campaign_due():
            _run_campaign_steps()

        sys.exit(1)


if __name__ == "__main__":
    main()
