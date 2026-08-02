"""
[260705 검증 캠페인] §4-1 주간 검증 스텝 체인 — 공용 모듈.

`retrain_eod.py`(루트, Windows 작업 스케줄러 `Maitreya_EODretrain`이 실제 호출하는
자동 경로)와 `scripts/eod_retrain.py`(수동/백업용, `EOD_RETRAIN.bat` 대상, Phase 2
호라이즌별 재학습 등 별개 기능 보유) 양쪽에서 동일하게 쓰던 `_campaign_due()`/
`_run_campaign_steps()`가 두 파일에 복사돼 있어 수정할 때마다 양쪽을 손으로 동기화
해야 했다(333차 후속3의 휴장일 보정이 실제로 두 번 적용됨) — 이 중복을 없애기 위해
공용 모듈로 분리(333차 후속4).
"""
import datetime
import os
import sys
import subprocess


def week_last_trading_day(friday: datetime.date) -> datetime.date:
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


def campaign_due(flag=None) -> bool:
    """--campaign 명시 > 금요일(휴장 시 그 주 마지막 거래일) 자동. None=자동 판단."""
    if flag is not None:
        return bool(flag)
    from config.krx_holidays import is_krx_holiday

    today = datetime.date.today()
    if today.weekday() >= 5 or is_krx_holiday(today):
        return False  # 오늘 자체가 휴장일이면 실행하지 않음
    this_friday = today + datetime.timedelta(days=4 - today.weekday())
    return week_last_trading_day(this_friday) == today


def run_campaign_steps(logger, base_dir: str) -> None:
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
        # [357차] 메타라벨 분류기(entry_quality_prob 스코어러)가 어떤 스케줄에도
        # 연결돼 있지 않아 [2] Meta-Gate 채널이 갱신 불가였던 결함 수정 —
        # 분위 회귀와 동일하게 리포트 생성 **뒤**에 재학습(§3-1 OOS 보장 순서).
        ("메타라벨 분류기 재학습", ["train_meta_label_classifier.py"]),
    ]
    if datetime.date.today().isocalendar()[1] % 2 == 0:
        steps.append(("MAE/MFE 분석", ["analyze_mae_mfe.py"]))

    script_dir = os.path.join(base_dir, "scripts")
    logger.info("=" * 55)
    logger.info("[검증 캠페인] 주간 스텝 %d개 실행 (§4-1)", len(steps))
    summary = []
    for name, cmd in steps:
        script_path = os.path.join(script_dir, cmd[0])
        if not os.path.exists(script_path):
            logger.warning("[검증 캠페인] %s — 스크립트 없음: %s", name, script_path)
            summary.append((name, "MISSING"))
            continue
        try:
            proc = subprocess.run(
                [sys.executable, script_path] + cmd[1:],
                cwd=base_dir,
                timeout=1800,  # 스텝당 최대 30분
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            ok = proc.returncode == 0
            tail = (proc.stdout or b"")[-2000:].decode("utf-8", errors="replace")
            logger.info("[검증 캠페인] %s → %s (rc=%d)\n%s",
                         name, "완료" if ok else "실패", proc.returncode, tail)
            summary.append((name, "OK" if ok else "FAIL(rc=%d)" % proc.returncode))
        except subprocess.TimeoutExpired:
            logger.error("[검증 캠페인] %s — 30분 타임아웃", name)
            summary.append((name, "TIMEOUT"))
        except Exception as e:
            logger.error("[검증 캠페인] %s — 실행 오류: %s", name, e)
            summary.append((name, "ERROR"))

    logger.info("[검증 캠페인] 요약: %s",
                 " | ".join("%s=%s" % (n, s) for n, s in summary))
    # [MW0601 407차] 출력이 data/ 고정파일명 → docs/정기점검/금요일점검/<PC>/ 날짜본으로
    # 바뀌었다. 로그가 옛 경로를 가리키면 EOD 로그만 보고 파일을 찾다 헤매게 된다.
    try:
        from scripts.campaign_report_paths import latest as _cr_latest
        from utils.db_utils import pc_id as _cr_pc
        logger.info("판정 리포트: %s", _cr_latest(_cr_pc(), "report"))
    except Exception as _cr_e:
        logger.info("판정 리포트: docs/정기점검/금요일점검/<PC명>/ (경로 조회 실패: %s)", _cr_e)
    logger.info("=" * 55)
