# utils/exit_flags.py — 종료 의도 기록 [MW0601 618차]
#
# 무엇이 문제였나
# ---------------
# 종료 의도는 **3종**인데 표현 수단은 `data/_exit_normally` 파일의 존재/부재
# **2상태**였다. 그래서 다음 둘이 같은 흔적으로 뭉개졌다:
#
#   · X → **재시작**  — 정상 종료지만 런처가 다시 띄워야 한다 → 플래그 미기록
#   · 강제 종료·크래시 — 비정상 종료                          → 플래그 미기록
#
# 실측 2026-09-22 15:08: `crash_fault.log` 는 `[CLEAN EXIT] PID=27016` 인데
# 런처 로그는 **「일시적 크래시」**였다. 사용자가 X → 재시작을 누른 것이다.
# 같은 날 09:42 종료는 CLEAN EXIT 조차 없다(하드킬) — 이쪽은 애초에 어떤
# 파일로도 포착할 수 없는 경로다.
#
# 무엇을 하는가 — 그리고 **하지 않는가**
# --------------------------------------
# 파일 규약은 **그대로 둔다**(`_exit_normally` · `shutdown_normal_*.txt`).
# 런처(`start_mireuk.bat`)는 손대지 않는다 — 그 파일은 GOTO/괄호 블록 오염
# 사고 이력이 있고(자체 주석), 라벨은 장식이지 안전장치가 아니다.
#
# 대신 **의도를 로그로 남긴다**: `[Shutdown] intent=<reason> keep_alive=<bool>`.
# 사후 점검은 파일(런처가 읽은 직후 지운다)이 아니라 로그를 읽으므로, 이 한
# 줄이면 세 경로가 구분된다. 종전에 X → 재시작 경로는 **아무 로그도 남기지
# 않았다** — 그것이 실제 결손이었다.
#
#   | reason         | keep_alive | _exit_normally | shutdown_normal_* | 런처   |
#   |----------------|-----------|----------------|-------------------|--------|
#   | daily_close    | False     | 기록           | 기록              | 정지   |
#   | auto_shutdown  | False     | 기록           | 기록              | 정지   |
#   | user_close     | False     | 기록           | 기록              | 정지   |
#   | user_restart   | True      | 미기록         | 미기록            | 재시작 |
#   | (하드킬)       | —         | 미기록         | 미기록            | 재시작 |

import datetime
import logging
import os

logger = logging.getLogger(__name__)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _data_dir(root=None):
    return os.path.join(root or _ROOT, "data")


def write_exit_flags(reason, keep_alive=False, root=None, log_fn=None):
    """종료 의도를 기록한다 — 반환: 실제로 쓴 경로 목록.

    `keep_alive=True` 면 **파일을 하나도 쓰지 않는다**. 런처가 재시작해야 하기
    때문이다. 의도는 로그로만 전달한다 — 아무도 읽지 않는 파일을 남기면
    그 자체가 죽은 산출물이 된다(FP-CRITICAL 계열).

    `log_fn(msg, level)` 을 주면 그쪽으로도 한 줄 보낸다(`log_manager.system`).
    """
    written = []
    now = datetime.datetime.now()

    if not keep_alive:
        d = _data_dir(root)
        try:
            flag = os.path.join(d, "_exit_normally")
            with open(flag, "w", encoding="utf-8") as f:
                f.write("%s\n%s\n" % (reason, now.isoformat()))
            written.append(flag)
            # 🔴 이 문구는 **바꾸지 말 것** — 운영 점검이 문자열로 센다.
            #   `dev_memory/NEXT_TODO.md`: 정상 마감일이면 이 줄이 「매번 정확히
            #   2회」(daily_close + auto_shutdown) 나온다는 것이 건강 신호다.
            #   618차가 본문을 이 모듈로 옮기면서 하마터면 없앨 뻔했다.
            logger.info("[Shutdown] 정상 종료 플래그 기록: %s (%s)", flag, reason)
        except Exception as e:
            logger.warning("[Shutdown] 정상 종료 플래그 기록 실패 (무해): %s", e)

        # 🔴 [MW0601 513차 / FZ-2 오탐 차단 · MW0602 524차 이식] 런처가
        #   **지우지 않는** 날짜본 종료 마커.
        #   `_exit_normally` 는 런처가 읽은 직후 삭제하므로 프로세스 밖 센티넬이
        #   판정할 시점에는 항상 없고, 그 축이 매번 「미측정」 → 정상 마감한
        #   날에도 가짜 CRITICAL 이 쏟아졌다.
        #
        #   ⚠ **두 PC 가 각자 실측했다 — 어느 쪽도 지우지 말 것.**
        #     · MW0601: 2026-08-25~09-01 매일 45회(팝업 포함).
        #     · MW0602(523차): `--at-time` 재생에서 16:00·16:29 **둘 다 CRITICAL**.
        #       그때는 감시 창을 15:45 로 좁혀 피했는데, 이 마커가 생기면서
        #       그 우회가 필요 없어졌다.
        #     [MW0601 618차] 본문이 main.py 에서 이 모듈로 옮겨왔다. dev 쪽
        #     주석에만 있던 MW0602 실측을 여기로 합쳐 둔다 — 근거는 브랜치가
        #     아니라 코드를 따라가야 한다.
        #
        #   ⚠ 마감 완료 시각이 아니라 **종료 시각**을 담는 것이 핵심이다.
        try:
            marker = os.path.join(d, "shutdown_normal_%s.txt" % now.strftime("%Y%m%d"))
            with open(marker, "w", encoding="utf-8") as f:
                f.write("%s\n%s\n" % (reason, now.isoformat()))
            written.append(marker)
        except Exception as e:
            logger.warning("[Shutdown] 날짜본 종료 마커 기록 실패 (무해): %s", e)

    # 618차 신설 — 세 경로를 가르는 줄. 위 레거시 문구는 정상 종료 때만 나오므로
    # 「재시작이었나 하드킬이었나」를 구분하지 못한다. 이쪽이 그 질문에 답한다.
    msg = "[Shutdown] intent=%s keep_alive=%s files=%d" % (
        reason, bool(keep_alive), len(written))
    logger.info(msg)
    if log_fn is not None:
        try:
            log_fn(msg, "INFO")
        except Exception:
            pass
    return written
