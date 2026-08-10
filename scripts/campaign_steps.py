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
      3) 피처셋 건강 리포트 (읽기 전용, 410차 Phase A)
      4) 섀도우 TB 재학습 (다음 주 평가용 모델 갱신)
      5) 분위 회귀 재학습
      6) 격주(짝수 ISO 주차): MAE/MFE 배리어 적정성 분석
    """
    steps = [
        ("게이트 ablation 리포트", ["generate_gate_ablation_report.py", "--days", "7"]),
        # [MW0601 455차 / 07-30 실행계획 1단계] L4 conf-층화 z-test — 311차 후속5 방법론
        # 상시화. 읽기 전용 + data/horizon_conf_stratified_latest.json 갱신(피처셋 건강
        # 리포트의 L4 입력 계약). 판정 리포트 **앞**(07-30 계획 §2-4 위치 규약).
        ("호라이즌 conf-층화 검정", ["horizon_conf_stratified_test.py", "--days", "20"]),
        ("검증 캠페인 판정 리포트", ["generate_validation_campaign_report.py"]),
        # [MW0601 410차 / 피처셋 주기점검 Phase A] 호라이즌별 피처셋 L0 건강도 +
        # 후보 파이프라인 현황판. 읽기 전용이라 순서에 민감하지 않지만, 재학습
        # **앞**에 두어 이번 주 리포트가 "이번 주 내내 라이브였던 pkl"의 상태를
        # 기록하게 한다(재학습 뒤면 오늘 갱신된 pkl을 지난 한 주의 근거로 오독하게 된다).
        ("피처셋 건강 리포트", ["generate_featureset_health_report.py"]),
        # [MW0601 453차 / QDQ Phase 2] CVD 앵커 대조 — 서버 정답지(FutureCurOnly
        # 22/23)와 자체 분류를 3축으로 대조하고 Phase 3(CVD 전환) 착수 여부를 판정한다.
        # 읽기 전용이라 순서에 민감하지 않지만 재학습 **앞**에 둔다(410차 규약과 동일 —
        # 이번 주 내내 라이브였던 상태를 기록해야 한다). 게이팅 없음: 판정 결과와
        # 무관하게 종료코드 0이라 후속 스텝을 막지 않는다.
        ("CVD 앵커 대조 리포트", ["generate_cvd_anchor_report.py", "--days", "5"]),
        # [MW0602 458차 / 3-B] §49 조기청산 반사실 — TP1 도달 전 익절성 틱스톱의
        # "유지했다면". 읽기 전용 stdout 판정(사전등록 early_trail_exit_watch).
        # 판정 리포트 **앞**(읽기 전용 채널 공통 규약). TRADE 로그를 파싱하므로
        # 각 PC가 자기 로그 표본으로 돌린다 — PC간 대조는 stdout 로그로.
        ("조기청산 반사실 [49]", ["early_trail_exit_counterfactual.py"]),
        # [MW0602 458차 / 3-A] §40-B 방향 처분 실험 — 실제 vs 자기 반대.
        # 어떤 결과도 역방향 매매로 이어지지 않는다(처분 판단 재료, 사전등록
        # direction_disposal_watch). [40]과 같은 시뮬레이터라 비용 무시 — 비교만 유효.
        ("방향 처분 실험 [40-B]", ["random_entry_control.py", "--inverse"]),
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
    # ── [MW0601 448차] 🔴 조용한 실패 차단 ──────────────────────────────────────
    # 종전에는 리포트 스텝이 죽어도 아래에서 **가장 최근 파일**을 "판정 리포트"로
    # 안내했다. 08-07 EOD 로그가 실제로 **6일 묵은 20260801_pre405**를 그렇게 찍었고,
    # 그 조합(조용한 크래시 + 낡은 파일 안내) 때문에 2주간 결번을 아무도 못 알아챘다.
    # 이제 그 스텝의 성패를 확인해 **실패면 경로를 안내하지 않고 ERROR로 알린다.**
    _report_step_ok = None
    for _n, _s in summary:
        if "판정 리포트" in _n:
            _report_step_ok = (_s == "OK")
            break
    if _report_step_ok is False:
        logger.error(
            "[검증 캠페인] 🔴 판정 리포트 생성 실패 — **이번 주 산출물이 없다.** "
            "아래에 경로를 안내하지 않는다(낡은 파일을 이번 주 것으로 오독하는 사고 방지). "
            "rc가 -1066598273/3228369023(0xC06D007F)이면 BLAS DLL 문제이며 "
            "utils/dll_bootstrap.py 자가진단을 먼저 돌릴 것: "
            "python -m utils.dll_bootstrap")
    try:
        from scripts.campaign_report_paths import latest as _cr_latest
        from utils.db_utils import pc_id as _cr_pc
        _pc = _cr_pc()
        if _report_step_ok is False:
            raise RuntimeError("리포트 스텝 실패 — 경로 안내 생략")
        _rp = _cr_latest(_pc, "report")
        # 파일명의 날짜본이 오늘이 아니면 **이번 주 것이 아니다**. 스텝이 OK로 보고돼도
        # (예: 생성기가 rc=0인데 파일을 못 쓴 경우) 여기서 한 번 더 걸린다.
        _today = datetime.date.today().strftime("%Y%m%d")
        if _today not in os.path.basename(_rp):
            logger.error("[검증 캠페인] 🔴 판정 리포트가 오늘(%s) 것이 아니다: %s "
                         "— 이번 주 산출물로 인용하지 말 것.", _today, _rp)
        else:
            logger.info("판정 리포트: %s", _rp)
        # [410차] 계열마다 stem이 다르다 — 하나가 없어도 나머지 경로는 찍어야 한다.
        try:
            logger.info("피처셋 건강 리포트: %s",
                        _cr_latest(_pc, "report", stem="featureset_health"))
        except Exception as _fs_e:
            logger.info("피처셋 건강 리포트: 없음 (%s)", _fs_e)
    except Exception as _cr_e:
        logger.info("판정 리포트: docs/정기점검/금요일점검/<PC명>/ (경로 조회 실패: %s)", _cr_e)
    logger.info("=" * 55)
