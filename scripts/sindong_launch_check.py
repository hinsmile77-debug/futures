# -*- coding: utf-8 -*-
"""[MW0601 713차 P4 / Sindong2-V4] start_Sindong2.bat 기동 전 「신동 주체」 구성 확인.

원본: MW0602 Sindong-V4 scripts/sindong_launch_check.py(f5c2a21) — 이 브랜치는 주체를 **고정하지 않고**
허용 집합(신동·피터)으로 두므로 판정 항목이 다르다.

미륵 보존 브랜치(v9-dev)와 같은 작업 폴더를 쓰므로 `git checkout v9-dev` 뒤에 08:40 예약이 그대로 돌면
미륵이 실계좌로 기동된다 — 그 경로를 런처 입구에서 끊는다.

판정(settings.py 를 import 하지 않고 AST 로 읽는다 — numpy·DLL 경로와 무관하게 빠르고 안전):
    MIREUK_ENGINE      == "off"                        (아니면 FATAL)
    PRINCIPAL_ALLOWED  에 "MIREUK" 없음 · "SHINDONG" 있음 (아니면 FATAL — None 은 3주체 전부라 FATAL)
    PRINCIPAL_DEFAULT  == "SHINDONG"                   (아니면 FATAL)
    LIGHT_PASS_DRY_RUN                                  (참고만 — off 에서는 의미 없음, 출력만)
    git 브랜치          == Sindong2-V4                  (다르면 FATAL · 읽지 못하면 WARN — 미측정 ≠ 불일치, 계측 4원칙 ②)

종료 코드: 0 = 통과 · 3 = 구성 불일치(main.py 실행 금지) · 1 = settings.py 판독 실패

`--mireuk-launcher` [MW0601 724차] — start_mireuk.bat 입구의 **역방향** 판정.
    MIREUK_ENGINE == "off" 이면 미륵 런처는 main.py 를 띄우지 않는다(종료 4).
    2026-10-27 08:40 비활성이어야 할 `\\미륵이` 작업이 다시 켜져 있었고, 같은 main.py·같은 settings 라
    신동 주체로 하나 더 떠 신동 실주문이 두 벌 나갈 수 있었다 — 그 런처는 STEP 3.9 를 거치지 않는다.
    종료 코드: 0 = 미륵 엔진 활성(부활) · 4 = 휴면 → 기동 거부 · 1 = 판독 실패(거부 — 런처가 처리)
"""
import ast
import io
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ("MIREUK_ENGINE", "PRINCIPAL_ALLOWED", "PRINCIPAL_DEFAULT", "LIGHT_PASS_DRY_RUN")
EXPECT_BRANCH = "Sindong2-V4"


def read_settings(path):
    """settings.py 최상위 대입 중 KEYS 의 마지막 리터럴 값. 리터럴이 아니면 '<non-literal>'."""
    with io.open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id in KEYS:
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


def _allowed_set(v):
    if isinstance(v, str):
        v = (v,)
    try:
        return {str(x or "").upper() for x in v}
    except TypeError:
        return None


def judge(found):
    """→ [(ok, 문장)]. 판정 규칙의 단일 출처(테스트가 직접 부른다)."""
    out = []
    me = found.get("MIREUK_ENGINE", "<missing>")
    out.append((me == "off", "MIREUK_ENGINE=%r (기대 'off')" % (me,)))
    al = found.get("PRINCIPAL_ALLOWED", "<missing>")
    s = None if al in (None, "<missing>", "<non-literal>") else _allowed_set(al)
    ok_al = bool(s) and "MIREUK" not in s and "SHINDONG" in s
    out.append((ok_al, "PRINCIPAL_ALLOWED=%r (기대: 미륵 없음 · 신동 포함, 예 ('SHINDONG', 'PETER'))" % (al,)))
    dp = found.get("PRINCIPAL_DEFAULT", "<missing>")
    out.append((str(dp).upper() == "SHINDONG", "PRINCIPAL_DEFAULT=%r (기대 'SHINDONG')" % (dp,)))
    return out


def main(root=_ROOT):
    try:
        found = read_settings(os.path.join(root, "config", "settings.py"))
    except Exception as exc:  # 판독 실패는 「통과」로 위장하지 않는다
        print("[SindongCheck] FATAL settings.py 판독 실패: {}".format(exc))
        return 1

    bad = 0
    for ok, line in judge(found):
        bad += 0 if ok else 1
        print("[SindongCheck] {} {}".format("OK   " if ok else "FATAL", line))
    print("[SindongCheck] INFO  LIGHT_PASS_DRY_RUN={!r} (off 에서는 무의미 — 전환일엔 False 권장)".format(
        found.get("LIGHT_PASS_DRY_RUN", "<missing>")))

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
        print("[MireukGate] REFUSE MIREUK_ENGINE='off' -- 미륵 휴면 중. 신동 주체는 start_Sindong2.bat 가 기동한다")
        return RC_MIREUK_DORMANT
    print("[MireukGate] OK    MIREUK_ENGINE={!r} -- 미륵 엔진 활성, 미륵 런처 기동 허용".format(me))
    return 0


if __name__ == "__main__":
    if "--mireuk-launcher" in sys.argv[1:]:
        sys.exit(main_mireuk_launcher())
    sys.exit(main())
