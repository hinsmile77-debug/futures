# -*- coding: utf-8 -*-
"""[MW0602 468차 G-1] 모델 사이드카(`gbm_{h}_meta.json`) 판독 — 순수 함수.

**왜 별도 모듈인가.** 이 판정은 라이브 사이즈 배수를 푸는 근거라 회귀 테스트가 필수인데,
`main.py`에 두면 PyQt/COM 의존 때문에 테스트에서 import할 수 없다. 파일 I/O와 비교
로직만 떼어내 COM 없이 검증할 수 있게 한다.

사이드카는 `learning/batch_retrainer.py:_save_model()`이 쓴다(457차 신설, 468차에
`label_scheme`·`label_param` 추가).
"""
import io
import json
import os

__all__ = ["read_label_state", "wants_from_settings"]


def wants_from_settings(settings):
    """[MW0602 488차 계획 C] 설정에서 **현행 레이블 기대치**를 뽑는다.

    Args:
        settings: `config.settings` 모듈(또는 같은 속성을 가진 객체).

    Returns:
        (want_scheme, want_param_of) — 그대로 `read_label_state()` 에 넘긴다.

    **왜 여기로 옮겼나.** 이 구성 로직은 `main.py:_model_label_scheme_current()` 안에만
    있었는데, EOD 재학습 자체 사후검증(`retrain_eod.py`)도 **똑같은 기대치**를 만들어야
    한다. 복제하면 레이블 체계를 바꿀 때 한쪽만 고쳐져 조용히 갈라진다 — 그때
    재학습 쪽 SelfCheck 는 "이상 없음"을 계속 찍으면서 실제로는 다른 기준을 본다.
    단일 진실원천으로 둔다. `main.py` 는 이 함수를 부르는 **어댑터**로 남는다.

    ⚠ 순수 함수다 — 파일 I/O·COM·PyQt 의존이 없어 테스트에서 그대로 부를 수 있다.
    """
    want_scheme = "fixed" if getattr(
        settings, "USE_FIXED_LABEL_THRESHOLD", True) else (
        "rolling_sigma" if getattr(
            settings, "USE_ROLLING_SIGMA_THRESHOLD", True) else "atr")

    def _want_param_of(hz):
        if want_scheme == "fixed":
            return float(getattr(settings, "HORIZON_THRESHOLDS", {}).get(hz, 0.0003))
        if want_scheme == "rolling_sigma":
            return float(getattr(settings, "SIGMA_K_PER_HORIZON", {}).get(
                hz, getattr(settings, "SIGMA_K", 1.0)))
        return None

    return want_scheme, _want_param_of


def read_label_state(model_dir, horizons, want_scheme, want_param_of=None, tol=1e-9):
    """적재된 모델들이 **현행 레이블 규칙 학습본인가**를 사이드카로 판정한다.

    Args:
        model_dir:     `gbm_{h}_meta.json`이 있는 폴더.
        horizons:      검사할 호라이즌 키들(순서 무관, 전부 통과해야 True).
        want_scheme:   현행 레이블 스키마 — "fixed" / "rolling_sigma" / "atr".
        want_param_of: hz → 기대 파라미터(float) 또는 None인 콜러블.
                       None을 반환하면 그 호라이즌의 파라미터는 비교하지 않는다.
        tol:           파라미터 비교 허용 오차.

    Returns:
        (ok: bool, detail: str)

    ⚠ **모르면 False다.** 폴더/파일 없음, `label_scheme` 키 없음(468차 이전 사이드카),
      키는 있으나 `null`(기록 경로 결함 — 476차 F-3에서 문구 분리), JSON 파싱 실패는
      전부 "모른다"이며 False로 떨어진다. 이 함수의 True는
      "6개 전부 확인했고 전부 현행"이라는 뜻이어야 한다 — "문제를 못 찾았다"가 아니다.
    """
    hz_list = list(horizons or [])
    if not model_dir or not hz_list:
        return False, "model_dir/horizons 미지정"
    if not os.path.isdir(model_dir):
        return False, "model_dir 없음: %s" % model_dir

    stale = []
    for hz in hz_list:
        path = os.path.join(model_dir, "gbm_%s_meta.json" % hz)
        if not os.path.exists(path):
            stale.append("%s:사이드카없음" % hz)
            continue
        try:
            with io.open(path, encoding="utf-8") as f:
                meta = json.load(f)
        except (ValueError, IOError, OSError) as e:
            stale.append("%s:판독실패(%s)" % (hz, type(e).__name__))
            continue
        # [MW0602 476차 F-3] "키 부재"(진짜 468차 이전 구버전)와 "키는 있으나 null"
        # (기록 경로 결함 — 0819 P1-1: 어제 새로 쓴 사이드카를 "구버전"이라 불러
        # 원인 추적을 늦출 뻔했다)을 구분한다. 셋 다 False(모른다)인 것은 그대로다.
        if "label_scheme" not in meta:
            stale.append("%s:사이드카 구버전(키없음)" % hz)
            continue
        scheme = meta.get("label_scheme")
        if scheme is None:
            stale.append("%s:label_scheme=null(기록경로 결함)" % hz)
            continue
        if not scheme:
            stale.append("%s:label_scheme 빈값" % hz)
            continue
        if scheme != want_scheme:
            stale.append("%s:%s!=%s" % (hz, scheme, want_scheme))
            continue
        # 임계값까지 본다 — 387차처럼 HORIZON_THRESHOLDS를 재보정하면 스키마는 같아도
        # **레이블 체계가 바뀐 것**이라 구모델은 낡은 것이다. 그때는 재학습 전까지
        # 보수 사이즈가 유지되는 편이 옳다.
        want_p = want_param_of(hz) if callable(want_param_of) else None
        if want_p is None:
            continue
        got_p = meta.get("label_param")
        if got_p is None:
            stale.append("%s:label_param없음" % hz)
        else:
            try:
                if abs(float(got_p) - float(want_p)) > tol:
                    stale.append("%s:임계 %.6g!=%.6g" % (hz, float(got_p), float(want_p)))
            except (TypeError, ValueError):
                stale.append("%s:label_param 형식오류" % hz)

    if stale:
        return False, "불일치 %d/%d — %s%s" % (
            len(stale), len(hz_list), ", ".join(stale[:3]),
            " …" if len(stale) > 3 else "")
    return True, "%d/%d 호라이즌 현행 레이블(%s) 학습본" % (
        len(hz_list), len(hz_list), want_scheme)
