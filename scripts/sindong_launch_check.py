# -*- coding: utf-8 -*-
"""[MW0602 Sindong-V4] start_Sindong.bat 기동 전 「신동 주체」 구성 확인.

미륵 휴면 브랜치(Sindong-V4)에서 신동 런처가 미륵 주체 구성(dev 브랜치 · MIREUK_ENGINE="full")으로
main.py 를 띄우는 사고를 막는다. 두 브랜치가 같은 작업 폴더를 쓰므로 `git checkout dev` 뒤에
08:40 예약이 그대로 돌면 미륵이 실계좌로 기동된다 — 그 경로를 런처 입구에서 끊는다.

판정(settings.py 를 import 하지 않고 AST 로 읽는다 — numpy·DLL 경로와 무관하게 빠르고 안전):
    MIREUK_ENGINE  == "off"       (아니면 FATAL)
    PRINCIPAL_LOCK == "SHINDONG"  (아니면 FATAL)
    git 브랜치     == Sindong-V4   (다르면 FATAL · 읽지 못하면 WARN — 미측정 ≠ 불일치, 계측 4원칙 ②)

종료 코드: 0 = 통과 · 3 = 구성 불일치(main.py 실행 금지) · 1 = settings.py 판독 실패

`--mireuk-launcher` [MW0601 724차 이식] — start_mireuk.bat 입구의 **역방향** 판정.
    MIREUK_ENGINE == "off" 이면 미륵 런처는 main.py 를 띄우지 않는다(종료 4).
    2026-10-27 MW0601 08:40 비활성이어야 할 미륵 런처 작업이 다시 켜져 있었고, 같은 main.py·같은 settings 라
    신동 주체로 하나 더 떠 실주문이 두 벌 나갈 수 있었다 — 미륵 런처는 STEP 3.9 를 거치지 않는다.
    종료 코드: 0 = 미륵 엔진 활성(부활) · 4 = 휴면 → 기동 거부 · 1 = 판독 실패(거부 — 런처가 처리)
"""
import ast
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECT = {"MIREUK_ENGINE": "off", "PRINCIPAL_LOCK": "SHINDONG"}
EXPECT_BRANCH = "Sindong-V4"


def read_settings(path):
    """settings.py 최상위 대입 중 EXPECT 키의 마지막 리터럴 값. 리터럴이 아니면 '<non-literal>'."""
    with io.open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id in EXPECT:
                try:
                    found[tgt.id] = ast.literal_eval(node.value)
                except ValueError:
                    found[tgt.id] = "<non-literal>"
    return found


def read_branch(root):
    """.git/HEAD 를 직접 읽는다(예약작업 환경엔 git 이 PATH 에 없을 수 있다). 못 읽으면 None."""
    try:
        with io.open(os.path.join(root, ".git", "HEAD"), encoding="utf-8") as fh:
            head = fh.read().strip()
    except (IOError, OSError):
        return None
    prefix = "ref: refs/heads/"
    return head[len(prefix):] if head.startswith(prefix) else "(detached " + head[:10] + ")"


def main(root=_ROOT):
    try:
        found = read_settings(os.path.join(root, "config", "settings.py"))
    except Exception as exc:  # 판독 실패는 「통과」로 위장하지 않는다
        print("[SindongCheck] FATAL settings.py 판독 실패: {}".format(exc))
        return 1

    bad = 0
    for key, want in EXPECT.items():
        got = found.get(key, "<missing>")
        ok = got == want
        bad += 0 if ok else 1
        print("[SindongCheck] {} {}={!r} (기대 {!r})".format("OK   " if ok else "FATAL", key, got, want))

    branch = read_branch(root)
    if branch is None:
        print("[SindongCheck] WARN  git 브랜치 판독 불가(.git/HEAD) -- 설정값만으로 판정")
    elif branch == EXPECT_BRANCH:
        print("[SindongCheck] OK    branch={}".format(branch))
    else:
        bad += 1
        print("[SindongCheck] FATAL branch={} (기대 {}) -- 미륵 주체 브랜치는 start_mireuk.bat 사용".format(
            branch, EXPECT_BRANCH))

    print("[SindongCheck] result={}".format("pass" if bad == 0 else "mismatch({})".format(bad)))
    return 0 if bad == 0 else 3


RC_MIREUK_DORMANT = 4


def main_mireuk_launcher(root=_ROOT):
    """start_mireuk.bat 입구 — 미륵 엔진이 휴면이면 기동 거부."""
    try:
        found = read_settings(os.path.join(root, "config", "settings.py"))
    except Exception as exc:
        print("[MireukGate] FATAL settings.py 판독 실패: {}".format(exc))
        return 1
    me = found.get("MIREUK_ENGINE", "<missing>")
    if me == "off":
        print("[MireukGate] REFUSE MIREUK_ENGINE='off' -- 미륵 휴면 중. 신동 주체는 start_Sindong.bat 가 기동한다")
        return RC_MIREUK_DORMANT
    print("[MireukGate] OK    MIREUK_ENGINE={!r} -- 미륵 엔진 활성, 미륵 런처 기동 허용".format(me))
    return 0


if __name__ == "__main__":
    if "--mireuk-launcher" in sys.argv[1:]:
        sys.exit(main_mireuk_launcher())
    sys.exit(main())
