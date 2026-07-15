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
import subprocess
import traceback

# ── 프로젝트 루트 설정 ────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

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
# (retrain_eod.py)을 실행할 뿐 scripts/eod_retrain.py(캠페인 체인 보유)는 스케줄된 적이
# 없어 §4-1 자동화가 죽어있었음(07-05 단 1회, 0바이트 로그) — 여기로 이식해 실제
# 스케줄에 연결한다. 로직은 scripts/eod_retrain.py의 동명 함수와 동일.
def _week_last_trading_day(friday: datetime.date) -> datetime.date:
    """그 주(월~금) 중 실제 마지막 거래일을 반환.

    금요일이 KRX 휴장일이면 목요일, 목요일도 휴장이면 수요일... 순으로 뒤로
    물러난다(예: 추석 연휴처럼 목·금이 연속 휴장인 주). Windows 작업 스케줄러는
    시장 휴장일을 모르고 요일로만 트리거하므로(월~금 매일 15:45 실행), 파이썬
    레벨에서 "이번 주 실제 마지막 거래일"을 판단해야 한다.
    """
    from config.krx_holidays import is_krx_holiday

    d = friday
    monday = friday - datetime.timedelta(days=4)
    while d >= monday and (d.weekday() >= 5 or is_krx_holiday(d)):
        d -= datetime.timedelta(days=1)
    return d


def _campaign_due(flag=None):
    """--campaign 명시 > 금요일(휴장 시 그 주 마지막 거래일) 자동. None=자동 판단."""
    if flag is not None:
        return bool(flag)
    from config.krx_holidays import is_krx_holiday

    today = datetime.date.today()
    if today.weekday() >= 5 or is_krx_holiday(today):
        return False  # 오늘 자체가 휴장일이면 실행하지 않음
    this_friday = today + datetime.timedelta(days=4 - today.weekday())
    return _week_last_trading_day(this_friday) == today


def _run_campaign_steps():
    """[260705 검증 캠페인] 주간 검증 스텝 체인 자동화 (§4-1).

    각 스텝은 서브프로세스로 격리 — 하나가 실패해도 나머지는 계속 실행한다.
    순서가 중요하다:
      1) 게이트 ablation 리포트 (읽기 전용)
      2) 검증 캠페인 판정 리포트 — 반드시 섀도우 TB 재학습 **전에** 실행해야
         이번 주 데이터가 지난주 모델 기준 OOS로 평가된다(§3-1 OOS 보장: 리포트가
         모델 파일 mtime 이후 ts만 평가하므로, 재학습을 먼저 돌리면 mtime이 오늘로
         갱신돼 평가 표본이 0이 된다)
      3) 섀도우 TB 재학습 (다음 주 평가용 모델 갱신)
      4) 분위 회귀 재학습
      5) 격주(짝수 ISO 주차): MAE/MFE 배리어 적정성 분석
    """
    steps = [
        ("게이트 ablation 리포트", ["generate_gate_ablation_report.py", "--days", "7"]),
        ("검증 캠페인 판정 리포트", ["generate_validation_campaign_report.py"]),
        ("섀도우 TB 재학습", ["run_shadow_triple_barrier_retrain.py"]),
        ("분위 회귀 재학습", ["train_quantile_regressor.py"]),
    ]
    if datetime.date.today().isocalendar()[1] % 2 == 0:
        steps.append(("MAE/MFE 분석", ["analyze_mae_mfe.py"]))

    script_dir = os.path.join(_ROOT, "scripts")
    log.info("=" * 55)
    log.info("[검증 캠페인] 주간 스텝 %d개 실행 (§4-1)", len(steps))
    summary = []
    for name, cmd in steps:
        script_path = os.path.join(script_dir, cmd[0])
        if not os.path.exists(script_path):
            log.warning("[검증 캠페인] %s — 스크립트 없음: %s", name, script_path)
            summary.append((name, "MISSING"))
            continue
        try:
            proc = subprocess.run(
                [sys.executable, script_path] + cmd[1:],
                cwd=_ROOT,
                timeout=1800,  # 스텝당 최대 30분
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            ok = proc.returncode == 0
            tail = (proc.stdout or b"")[-2000:].decode("utf-8", errors="replace")
            log.info("[검증 캠페인] %s → %s (rc=%d)\n%s",
                      name, "완료" if ok else "실패", proc.returncode, tail)
            summary.append((name, "OK" if ok else "FAIL(rc=%d)" % proc.returncode))
        except subprocess.TimeoutExpired:
            log.error("[검증 캠페인] %s — 30분 타임아웃", name)
            summary.append((name, "TIMEOUT"))
        except Exception as e:
            log.error("[검증 캠페인] %s — 실행 오류: %s", name, e)
            summary.append((name, "ERROR"))

    log.info("[검증 캠페인] 요약: %s",
              " | ".join("%s=%s" % (n, s) for n, s in summary))
    log.info("판정 리포트: %s", os.path.join(_ROOT, "data", "validation_campaign_report.md"))
    log.info("=" * 55)


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
        log.info(
            "재학습 시작: force=True, intraday=False, full_cv=True  "
            "(절단 없음, 300그루, 3-fold CV)"
        )
        t2 = time.perf_counter()
        result = retrainer.retrain_now(
            X=X,
            y_dict=y_dict,
            feature_names=feature_names,
            force=True,
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
        log.info(
            "재학습 완료: 호라이즌 교체=%d/%d  재학습=%.1fs  로드=%.1fs  합계=%.1fs",
            horizons_ok,
            len(result.get("horizons", {})),
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
        try:
            from strategy.regime_fingerprint import get_fingerprint, _CORE_FEATURES
            _core_idx = {
                f: feature_names.index(f)
                for f in _CORE_FEATURES
                if f in feature_names
            }
            if len(_core_idx) == len(_CORE_FEATURES):
                _wfa_features = [
                    {f: float(X[i, idx]) for f, idx in _core_idx.items()}
                    for i in range(X.shape[0])
                ]
                get_fingerprint().save_training_fingerprint(_wfa_features)
                log.info(
                    "[RegimeFingerprint] 학습분포 갱신 완료 — %d행 기준 (CORE 3피처 전부 확보)",
                    len(_wfa_features),
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
