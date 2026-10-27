# -*- coding: utf-8 -*-
"""[MW0602 661차 후속7] 미륵 휴면 중 재학습 진입점 차단 — 판정 한 곳.

왜 있는가
---------
`MIREUK_ENGINE="off"`(Sindong-V4)에서는 앱 안의 재학습 spawn 은 이미 막혀 있다
(`main._start_gbm_retrain_subprocess`). 그러나 **앱 밖 진입점**은 아무 확인도 없었다:
`retrain_eod.py`(예약작업 `\\Maitreya_EODretrain` — 현재 Disabled) · `scripts/eod_retrain.py`
(`EOD_RETRAIN.bat`) · `retrain_intraday.py`. 예약작업이 다시 켜지거나 배치를 손으로 돌리면
휴면 중 미륵 모델·스케일러를 덮어써 「되살림 = 마지막 실가동 상태」 원칙이 깨진다(CLAUDE.md 미륵 휴면 스위치).

규칙
----
- `config.settings.MIREUK_ENGINE` 이 `"off"` 면 차단한다. `dev`(미륵 보존, `"full"`)에서는 아무 영향이 없다.
- 우회: 인자 `--allow-dormant` 또는 환경변수 `MIREUK_ALLOW_DORMANT_RETRAIN=1`(의도적 수동 재학습 — 로그에 남긴다).
- 설정을 읽지 못하면 **차단하지 않는다**(종전 동작) — 대신 그 사실을 남긴다(계측 4원칙 ④).
- numpy 등 무거운 모듈을 import 하지 않는다(진입점 최상단 DLL 부트스트랩 규약과 충돌하지 않게).
"""
import os
import sys

ALLOW_ARG = "--allow-dormant"
ALLOW_ENV = "MIREUK_ALLOW_DORMANT_RETRAIN"


def engine_mode():
    """→ ("off"|"full"|..., None) 또는 (None, 이유) — 설정을 못 읽으면 None."""
    try:
        from config import settings as _s
        return str(getattr(_s, "MIREUK_ENGINE", "full") or "full").strip().lower(), None
    except Exception as e:  # pragma: no cover - 환경 의존
        return None, repr(e)


def allow_requested(argv=None):
    argv = sys.argv if argv is None else argv
    env = str(os.environ.get(ALLOW_ENV, "")).strip().lower() not in ("", "0", "false", "no", "off")
    return (ALLOW_ARG in argv) or env


def should_block(entry, log=None, argv=None):
    """재학습을 막아야 하면 True. 판단 근거를 log(.warning/.info) 에 한 줄 남긴다."""
    mode, why = engine_mode()
    say = (lambda lv, m: getattr(log, lv)(m)) if log is not None else (lambda lv, m: print(m))
    if mode is None:
        say("warning", "[MireukDormant] %s : 설정(MIREUK_ENGINE)을 읽지 못해 차단하지 않는다(종전 동작) - %s" % (entry, why))
        return False
    if mode != "off":
        return False
    if allow_requested(argv):
        say("warning", "[MireukDormant] %s : 미륵 휴면(MIREUK_ENGINE=off)이지만 %s 로 의도적 재학습을 진행한다"
            % (entry, ALLOW_ARG + " / " + ALLOW_ENV))
        return False
    say("warning", "[MireukDormant] %s : 미륵 휴면(MIREUK_ENGINE=off) 중이라 재학습하지 않는다. "
        "휴면 모델은 덮어쓰지 않는다(되살림 = 마지막 실가동 상태). 의도적이면 %s 또는 %s=1"
        % (entry, ALLOW_ARG, ALLOW_ENV))
    return True
