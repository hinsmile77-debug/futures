# -*- coding: utf-8 -*-
"""
매매 모드(모의/실거래) 단일 출처 — machine.cfg 의 TRADE_MODE.

    TRADE_MODE=mock   (기본값 — 키가 없거나 값이 이상하면 mock)
    TRADE_MODE=real

읽는 곳: scripts/cybos_autologin.py(로그인 경로·자격증명 선택),
config/secrets.py(계좌 선택). 환경변수 TRADE_MODE 가 있으면 그것이 우선한다.

⚠ 판정 불능 시 기본값이 **mock** 인 이유: 이 값은 "어느 세션으로 로그인할지"를
고르는 의도값이다. 실제 접속 서버는 로그인 직후 ServerType 으로 다시 대조하므로
(cybos_autologin.verify_server_type), 의도값을 보수적으로 두어도 실자금 쪽으로
새는 경로는 없다. 반대로 preflight 의 ServerType 판정 불능은 실서버로 간주한다
(그쪽은 "실제 상태"이므로 위험한 쪽으로 가정하는 것이 맞다).

이 모듈은 의존성이 없어야 한다 — 로그인 스크립트가 numpy 등을 import 하기 전에 부른다.
"""
import io
import os

MOCK = "mock"
REAL = "real"
_VALID = (MOCK, REAL)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MACHINE_CFG = os.path.join(_ROOT, "machine.cfg")


def _read_cfg_value(key, path=MACHINE_CFG):
    """machine.cfg 에서 KEY=VALUE 한 줄을 읽는다. 없으면 None."""
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                if k.strip().upper() == key.upper():
                    v = v.split("#", 1)[0].strip()
                    return v or None
    except (IOError, OSError):
        return None
    return None


def get_trade_mode(path=MACHINE_CFG):
    """(mode, source) 반환. mode ∈ {"mock","real"}, source ∈ {"env","machine.cfg","default"}.

    source 를 함께 돌려주는 것은 계측 4원칙 ④(폴백 가시화) 때문이다 — 기본값으로
    mock 이 쓰였는지, 명시적으로 mock 인지 구분할 수 있어야 한다.
    """
    env = (os.environ.get("TRADE_MODE") or "").strip().lower()
    if env in _VALID:
        return env, "env"
    cfg = (_read_cfg_value("TRADE_MODE", path) or "").strip().lower()
    if cfg in _VALID:
        return cfg, "machine.cfg"
    return MOCK, "default"


def is_real(path=MACHINE_CFG):
    return get_trade_mode(path)[0] == REAL
