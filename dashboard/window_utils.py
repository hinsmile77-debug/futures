# dashboard/window_utils.py
"""보조 창 공통 유틸 — [MW0601 621차 후속4].

부모가 있는 최상위 창(`QDialog(parent)` + `Qt.Window`)은 Windows 에서 **소유(owned)
창**이 되어 작업표시줄 단추가 없다. 그 상태로 최소화 단추만 달면, 최소화한 창이
화면 왼쪽 아래 **160×28px 막대**로 쪼그라들어 되찾기 어렵다(2026-09-23 실측:
owner=True · WS_EX_APPWINDOW=False · 최소화 rect (480,1372)-(640,1400)).

`WS_EX_APPWINDOW` 를 켜면 소유 관계는 그대로 둔 채(부모 위에 뜨는 성질 유지)
작업표시줄 단추가 생긴다.
"""
from __future__ import annotations

import logging
import sys

logger = logging.getLogger("SYSTEM")

_GWL_EXSTYLE = -20
_WS_EX_APPWINDOW = 0x00040000


# ── 32-bit 창 크기 예산 — [621차 후속5] ────────────────────────────────────
# 217차(2026-06-22) 크래시: 150% 모니터에 복원한 3030×1460 창이 Windows DPI 가상화로
# 4547×2124(38.6MB) DIB 를 요구 → 장시간 운용 뒤 32-bit 주소공간 단편화로
# CreateDIBSection FAILED. 그때 「논리 1920×1060 = 150% 에서 물리 약 18MB」를 안전값으로
# 잡고 **가로·세로를 각각** 고정 상한으로 막았다.
# 🔴 그 고정 상한은 모니터 배율을 무시해 100% 모니터에서도 1920×1060 을 넘는 창을
#   복원하지 못했다(2026-09-23 사용자 보고 「크기조정 후 다시 열면 이전 크기가 안 온다」 —
#   저장값이 정확히 1920×1060 이었다). 예산은 **그 18MB 를 그대로** 두고, 대상 모니터
#   배율로 환산한다 → 150% 모니터의 상한은 종전과 같고(위험 증가 0), 100% 모니터에서만
#   풀린다(2560×1400 전체화면 ≈ 14MB).
DIB_BUDGET_BYTES = 1920 * 1060 * 4 * 1.5 * 1.5      # ≈ 18.3MB


def fits_desktop(x: int, y: int, w: int, h: int, inset: int = 8) -> bool:
    """사각형 네 모서리가 **모두 어떤 모니터 위에** 있는가 — 여러 모니터에 걸친 창 포함.

    [621차 후속7] 창 중심의 모니터 하나로만 자르면, 두 모니터에 걸쳐 둔 창이 그 모니터
    폭으로 줄어든다(재기동 실측 11:52:46 — 1019×598 → 768×598, 세로형 768px 모니터).
    """
    try:
        from PyQt5.QtCore import QPoint
        from PyQt5.QtWidgets import QApplication
        for px, py in ((x + inset, y + inset), (x + w - inset, y + inset),
                       (x + inset, y + h - inset), (x + w - inset, y + h - inset)):
            if QApplication.screenAt(QPoint(int(px), int(py))) is None:
                return False
        return True
    except Exception:                                           # noqa: BLE001
        return False


def dib_safe_size(screen, w: int, h: int,
                  budget: float = DIB_BUDGET_BYTES, clip_to_screen: bool = True):
    """(w, h, 줄었나) — 대상 모니터에서 물리 DIB 가 예산 안에 들도록 **비율 유지** 축소하고,
    그 모니터 가용 크기로 자른다.

    배율 = logicalDotsPerInch / 96 (144dpi → 1.5, 217차 크래시 계산과 같은 식).
    모니터를 모르면 1.5 로 가정한다(보수적).
    """
    ow, oh = int(w), int(h)
    try:
        scale = (max(1.0, float(screen.logicalDotsPerInch()) / 96.0)
                 if screen is not None else 1.5)
    except Exception:                                           # noqa: BLE001
        scale = 1.5
    max_px = budget / (4.0 * scale * scale)
    w, h = ow, oh
    if w > 0 and h > 0 and w * h > max_px:
        k = (max_px / float(w * h)) ** 0.5
        w, h = int(w * k), int(h * k)
    if screen is not None and clip_to_screen:
        try:
            av = screen.availableGeometry()
            w, h = min(w, av.width()), min(h, av.height())
        except Exception:                                       # noqa: BLE001
            pass
    return w, h, (w, h) != (ow, oh)


def force_taskbar_button(widget) -> bool:
    """창에 작업표시줄 단추를 붙인다. 성공(또는 이미 켜짐)이면 True.

    ⚠ **show() 전에, 위치를 잡은 뒤** 부른다. `winId()` 가 네이티브 창을 그 자리에
      만든다 — 1분봉 차트 창이 보조 모니터 DPI 로 HWND 를 만들려고 show() 전에
      위치를 복원하는 순서(`restore_saved_geometry`)를 깨지 않기 위해서다.
    ⚠ Windows 네이티브 플랫폼에서만 동작한다(offscreen 테스트에서는 아무것도 안 한다).
    """
    if sys.platform != "win32":
        return False
    try:
        from PyQt5.QtGui import QGuiApplication
        if QGuiApplication.platformName() != "windows":
            return False
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = int(widget.winId())
        ex = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
        if ex & _WS_EX_APPWINDOW:
            return True
        user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, ex | _WS_EX_APPWINDOW)
        return True
    except Exception as exc:                                    # noqa: BLE001
        # 실패해도 창은 뜬다 — 최소화 시 작업표시줄 단추가 없을 뿐이다. 조용히
        # 넘기지는 않는다(계측 4원칙 ④).
        logger.warning("[Window] 작업표시줄 단추 설정 실패 — 최소화하면 화면 "
                       "왼쪽 아래 막대로 남는다: %s", exc)
        return False
