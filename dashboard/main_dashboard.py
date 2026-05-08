# dashboard/main_dashboard.py
# 미륵이 v7.0 — 풀 통합 대시보드
# PyQt5 기반 7개 패널 완전 구현
"""
구현 패널:
  1. 멀티 호라이즌 예측 + 파라미터 분석
  2. 다이버전스 지수 + 포지션 매트릭스
  3. 동적 피처 관리 패널 (SHAP)
  4. 청산 관리 패널
  5. 진입 관리 패널
  6. 알파 리서치 봇 패널
  7. 5층 로그 시스템
"""

import os
import logging
import subprocess
import sys
import random
import math
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QProgressBar, QTabWidget,
    QTextEdit, QFrame, QSplitter, QScrollArea, QGroupBox,
    QComboBox, QSlider, QCheckBox, QSizePolicy, QDesktopWidget,
    QToolTip, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QSpinBox, QFormLayout,
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QObject
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QBrush, QPen,
    QLinearGradient, QFontDatabase, QIcon,
    QTextCursor, QTextBlockFormat,
)

from config.constants import FUTURES_PT_VALUE

logger = logging.getLogger("SYSTEM")


class UiAutoTabController(QObject):
    """운영 상태에 맞춰 우측/가운데 탭 포커스를 자동 복귀시킨다."""

    MANUAL_RETURN_MS = 20_000

    def __init__(self, right_tabs: QTabWidget, mid_tabs: QTabWidget):
        super().__init__(right_tabs)
        self.right_tabs = right_tabs
        self.mid_tabs = mid_tabs
        self._desired_right = 0
        self._desired_mid = 0
        self._suspend_manual_detect = False
        self._manual_override = False
        self._manual_idle_since = None

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick_manual_override)
        self._timer.start()

        self.right_tabs.currentChanged.connect(lambda _: self._on_user_tab_changed())
        self.mid_tabs.currentChanged.connect(lambda _: self._on_user_tab_changed())

    def set_startup_mode(self) -> None:
        self._desired_right = 0
        self._desired_mid = self._find_tab_index(self.mid_tabs, "진입 관리")
        self._apply_tabs(force=True)

    def set_ready_mode(self) -> None:
        self._desired_right = self._find_tab_index(self.right_tabs, "3 ")
        self._desired_mid = self._find_tab_index(self.mid_tabs, "진입 관리")
        self._apply_tabs(force=True)

    def set_position_mode(self) -> None:
        self._desired_right = self._find_tab_index(self.right_tabs, "3 ")
        self._desired_mid = self._find_tab_index(self.mid_tabs, "청산 관리")
        self._apply_tabs(force=True)

    def _find_tab_index(self, tabs: QTabWidget, keyword: str) -> int:
        for idx in range(tabs.count()):
            if keyword in tabs.tabText(idx):
                return idx
        return 0

    def _set_current_index(self, tabs: QTabWidget, index: int) -> None:
        index = max(0, min(index, tabs.count() - 1))
        self._suspend_manual_detect = True
        try:
            tabs.setCurrentIndex(index)
        finally:
            self._suspend_manual_detect = False

    def _apply_tabs(self, force: bool = False) -> None:
        if self._manual_override and not force:
            return
        self._manual_override = False
        self._manual_idle_since = None
        self._set_current_index(self.right_tabs, self._desired_right)
        self._set_current_index(self.mid_tabs, self._desired_mid)

    def _on_user_tab_changed(self) -> None:
        if self._suspend_manual_detect:
            return
        self._manual_override = True
        self._manual_idle_since = None

    def _managed_widgets_under_mouse(self) -> bool:
        widgets = [
            self.right_tabs,
            self.right_tabs.tabBar(),
            self.mid_tabs,
            self.mid_tabs.tabBar(),
        ]
        return any(w.underMouse() for w in widgets if w is not None)

    def _tick_manual_override(self) -> None:
        if not self._manual_override:
            return
        if self._managed_widgets_under_mouse():
            self._manual_idle_since = None
            return
        now_ms = int(datetime.now().timestamp() * 1000)
        if self._manual_idle_since is None:
            self._manual_idle_since = now_ms
            return
        if now_ms - self._manual_idle_since >= self.MANUAL_RETURN_MS:
            self._apply_tabs(force=True)


# ────────────────────────────────────────────────────────────
# 해상도 감지 + 동적 폰트·여백 스케일링
# ────────────────────────────────────────────────────────────
class ScreenScale:
    """
    화면 해상도와 OS DPI 배율을 감지해 폰트/여백을 자동 조정

    스케일 산정 방식:
      1. fit_scale  = min(논리W / 1680, 논리H / 1000)
                      창(1680×1000 기준)이 논리 화면에 꽉 차는 최대 배율
      2. dpi_bonus  = (devicePixelRatio - 1.0) × 0.10
                      고DPI 환경에서 물리 픽셀 여유만큼 소폭 추가 확대
      3. scale      = clamp(fit_scale + dpi_bonus, 0.80, 2.20)

    해상도별 예상 스케일 (OS DPI 배율 포함):
      FHD  1920×1080  DPI 100% (dpr=1.0) → scale ≈ 1.04
      QHD  2560×1440  DPI 100% (dpr=1.0) → scale ≈ 1.40
      4K   3840×2160  DPI 150% (dpr=1.5) → scale ≈ 1.45  ← 논리 2560×1440
      4K   3840×2160  DPI 100% (dpr=1.0) → scale ≈ 2.16
    """
    _scale:  float = 1.0
    _sw:     int   = 1920   # 논리 가용 폭  (OS DPI 반영)
    _sh:     int   = 1080   # 논리 가용 높이
    _phys_w: int   = 1920   # 물리 픽셀 폭
    _phys_h: int   = 1080   # 물리 픽셀 높이
    _dpr:    float = 1.0    # OS DPI 배율 (100%→1.0, 150%→1.5, 200%→2.0)

    _BASE_W: int = 1680     # 창 기준 폭  (resize(S.p(1680), ...) 와 일치)
    _BASE_H: int = 1000     # 창 기준 높이

    @classmethod
    def init(cls):
        app = QApplication.instance()
        if app is None:
            return
        screen = app.primaryScreen()
        if screen is None:
            return

        geo      = screen.availableGeometry()   # 태스크바 제외 — 창 크기 계산용
        cls._sw  = geo.width()
        cls._sh  = geo.height()
        cls._dpr = screen.devicePixelRatio()

        # 물리 해상도 = 전체 스크린(태스크바 포함) × DPI 배율
        full = screen.geometry()               # 전체 스크린 논리 픽셀
        cls._phys_w = round(full.width()  * cls._dpr)
        cls._phys_h = round(full.height() * cls._dpr)

        # ① 창이 논리 화면에 꽉 차는 최대 배율
        fit_scale = min(cls._sw / cls._BASE_W, cls._sh / cls._BASE_H)

        # ② 고DPI 보너스: dpr=1.0→+0.00, dpr=1.5→+0.05, dpr=2.0→+0.10
        dpi_bonus = (cls._dpr - 1.0) * 0.10

        raw = fit_scale + dpi_bonus
        cls._scale = max(0.80, min(2.20, raw))

        print(
            f"[Dashboard] 물리={cls._phys_w}×{cls._phys_h}"
            f"  논리={cls._sw}×{cls._sh}"
            f"  DPI={cls._dpr:.2f}×"
            f"  UI스케일={cls._scale:.2f}×"
        )

    @classmethod
    def f(cls, size: int) -> int:
        """폰트 사이즈 스케일 적용 (최소 8px)"""
        return max(8, round(size * cls._scale))

    @classmethod
    def p(cls, px: int) -> int:
        """여백·위젯 크기 스케일 적용 (최소 2px)"""
        return max(2, round(px * cls._scale))

    @classmethod
    def info(cls) -> str:
        return (
            f"{cls._phys_w}×{cls._phys_h}"
            f" (DPI {cls._dpr:.2f}×  UI {cls._scale:.2f}×)"
        )


S = ScreenScale   # 짧은 별칭으로 사용


def _get_commit_hash() -> str:
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        h = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root, stderr=subprocess.DEVNULL,
        ).decode().strip()
        return f"#{h}"
    except Exception:
        return "#??????"


COMMIT_HASH: str = _get_commit_hash()


def _calc_cycle_badge() -> tuple:
    """다음 목요일 만기(KOSPI200 위클리/월간)까지 D-days 계산 → (text, color).

    - 만기일: 매주 목요일
    - 월간 만기: 이달의 두 번째 목요일 (2nd Thursday)
    - 오늘이 목요일이면 D-0 (만기일)
    """
    import datetime as _dt
    today = _dt.date.today()
    wd    = today.weekday()            # 0=Mon, 3=Thu, 4=Fri …
    days  = (3 - wd) % 7              # 오늘→다음 목요일 일수 (0 = 오늘이 목요일)
    target = today + _dt.timedelta(days=days)

    # 해당 목요일이 이달 몇 번째 목요일인지 (1~5)
    nth = (target.day - 1) // 7 + 1
    is_monthly = (nth == 2)            # 2nd Thursday = 월간 만기

    tag   = "월간" if is_monthly else "위클리"
    if days == 0:
        text  = f"● {tag} 만기일"
        col   = "#FF5252"              # 빨강 — 오늘 만기
    elif days == 1:
        text  = f"{tag} D-1"
        col   = "#FFB74D"              # 주황 — 내일 만기
    elif days <= 3:
        text  = f"{tag} D-{days}"
        col   = "#FFD54F"              # 노랑 — 이번 주 내
    else:
        text  = f"{tag} D-{days}"
        col   = "#CE93D8"              # 연보라 — 여유
    return text, col


# ── 색상 팔레트 (다크 테마) ──────────────────────────────────
C = {
    "bg":       "#0D1117",
    "bg2":      "#161B22",
    "bg3":      "#21262D",
    "border":   "#30363D",
    "text":     "#E6EDF3",
    "text2":    "#8B949E",
    "green":    "#3FB950",
    "red":      "#F85149",
    "blue":     "#58A6FF",
    "orange":   "#D29922",
    "purple":   "#A371F7",
    "cyan":     "#39D3BB",
    "yellow":   "#E3B341",
}


# ── 주문/체결 탭 툴팁 — 진입·청산 전체 흐름 ─────────────────
_ORDER_TAB_TIP = (
    "<div style='font-family:Consolas,monospace;font-size:12px;line-height:1.6'>"

    "<b style='color:#58A6FF'>▶ 진입 흐름 (매분 실행)</b><br>"

    "<b>①&nbsp;시간 필터</b>&nbsp;"
    "OPEN_VOLATILE(09:05~10:30)&nbsp;/&nbsp;STABLE_TREND(10:30~11:50)"
    "&nbsp;/&nbsp;LUNCH_RECOVERY(13:00~14:00)&nbsp;/&nbsp;CLOSE_VOLATILE(14:00~15:00)"
    "&nbsp;— 이외 구간 진입 금지<br>"

    "<b>②&nbsp;레짐 최소 신뢰도</b>&nbsp;"
    "RISK_ON&nbsp;52%&nbsp;/&nbsp;NEUTRAL&nbsp;58%&nbsp;/&nbsp;RISK_OFF&nbsp;65%<br>"

    "<b>③&nbsp;9개 체크리스트 → 등급</b><br>"
    "&nbsp;&nbsp;✔&nbsp;앙상블 방향 non-FLAT<br>"
    "&nbsp;&nbsp;✔&nbsp;신뢰도 ≥ 레짐 기준<br>"
    "&nbsp;&nbsp;✔&nbsp;VWAP 위치 (LONG=가격&gt;VWAP)<br>"
    "&nbsp;&nbsp;✔&nbsp;CVD 방향 일치<br>"
    "&nbsp;&nbsp;✔&nbsp;OFI 압력 일치<br>"
    "&nbsp;&nbsp;✔&nbsp;외인 방향 일치 (콜/풋 순매수)<br>"
    "&nbsp;&nbsp;✔&nbsp;직전 봉 방향 일치<br>"
    "&nbsp;&nbsp;✔&nbsp;시간대 EXIT_ONLY 아님<br>"
    "&nbsp;&nbsp;✔&nbsp;일일 누적 손실 &lt; 2%<br>"
    "&nbsp;&nbsp;&nbsp;&nbsp;"
    "<b style='color:#39D3BB'>A급</b>(6↑) ×1.5 100% 즉시&nbsp;|&nbsp;"
    "<b style='color:#58A6FF'>B급</b>(4~5) ×1.0 50%→1분후50%&nbsp;|&nbsp;"
    "<b style='color:#D29922'>C급</b>(2~3) ×0.6 50%만&nbsp;|&nbsp;"
    "<b style='color:#F85149'>X급</b>(1↓) 금지<br>"

    "<b>④&nbsp;켈리 사이즈</b>&nbsp;"
    "= 계좌×1% × 신뢰도배수(0.6~1.5) × 레짐배수(0.5~1.0) × 등급배수"
    "&nbsp;÷&nbsp;(ATR×1.5×250,000×20)<br>"
    "&nbsp;&nbsp;→ max(1, min(결과, 10계약))<br>"

    "<b>⑤&nbsp;시장가 주문</b>&nbsp;신규매수/신규매도 hoga_gb=03<br>"

    "<hr style='border:0;border-top:1px solid #30363D;margin:5px 0'>"

    "<b style='color:#F85149'>▶ 청산 흐름 (우선순위 순, 매분 점검)</b><br>"

    "<b style='color:#F85149'>P1</b>&nbsp;15:10 강제청산 — 오버나이트 절대금지<br>"
    "<b style='color:#F85149'>P2</b>&nbsp;하드스톱&nbsp;ATR×1.5 도달 → 전량<br>"
    "<b style='color:#3FB950'>P3</b>&nbsp;TP1&nbsp;ATR×1.0 → 33% 부분청산<br>"
    "<b style='color:#3FB950'>P4</b>&nbsp;TP2&nbsp;ATR×1.5 → 33% 부분청산<br>"
    "<b style='color:#D29922'>P5</b>&nbsp;트레일링스톱 업데이트 후 히트 → 잔여 전량<br>"
    "<b style='color:#A371F7'>P6</b>&nbsp;CB/KillSwitch 긴급청산 (외부 직접 호출)"

    "</div>"
)

_VAR_TIP = (
    "<div style='font-family:Consolas,monospace;font-size:12px;line-height:1.7;"
    "min-width:360px;'>"

    "<b style='color:#FFB74D;font-size:13px;'>VaR 95%&nbsp;&nbsp;위험가치 (Value at Risk)</b>"
    "<hr style='border:0;border-top:1px solid #30363D;margin:4px 0 6px 0'>"

    "<b style='color:#58A6FF'>① 의미</b><br>"
    "&nbsp;&nbsp;오늘 하루 기준 <b>95% 신뢰구간 최대 손실 추정치</b><br>"
    "&nbsp;&nbsp;→ 하루 중 95%의 날은 손실이 이 금액 이내로 그친다<br>"
    "&nbsp;&nbsp;→ 나머지 <b style='color:#F85149'>5%</b>의 날은 이보다 큰 손실"
    "&nbsp;(<b>꼬리 리스크</b>)이 발생할 수 있음<br><br>"

    "<b style='color:#58A6FF'>② 계산 공식</b><br>"
    "&nbsp;&nbsp;<b style='color:#39D3BB'>VaR 95%</b>"
    "&nbsp;=&nbsp;ATR × 1.65σ × 계약수 × 500,000원<br><br>"

    "<b style='color:#58A6FF'>③ 공식 해설</b><br>"
    "&nbsp;&nbsp;<b>ATR</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;최근 1분봉 평균 변동폭 — 하루 변동성 대리지표<br>"
    "&nbsp;&nbsp;<b>1.65σ</b>&nbsp;&nbsp;&nbsp;&nbsp;95% 신뢰수준 z-score (정규분포 단측)<br>"
    "&nbsp;&nbsp;<b style='color:#A371F7'>참고</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    "VaR 99% 라면 z = 2.33σ (더 보수적, 더 큰 숫자)<br>"
    "&nbsp;&nbsp;<b>500,000원</b>&nbsp;KOSPI 200 선물 1pt = 50만원<br><br>"

    "<b style='color:#F85149'>④ 한계</b><br>"
    "&nbsp;&nbsp;ATR은 1분봉 기준 → <b>하루 전체 VaR 과소추정</b> 가능성 있음<br>"
    "&nbsp;&nbsp;정확한 산출은 일별 수익률 표준편차(σ_daily) 사용 권장<br>"
    "&nbsp;&nbsp;실시간 단일 포지션 모니터링 용도로는 ATR 기반도 실용적"

    "</div>"
)

_CANDLE_MONITOR_TIP = (
    "<div style='font-family:Consolas,monospace;font-size:12px;line-height:1.75;"
    "min-width:400px;'>"

    "<b style='color:#39D3BB;font-size:13px;'>분봉 모니터&nbsp;&nbsp;캔들 진행 타이머</b>"
    "<hr style='border:0;border-top:1px solid #30363D;margin:5px 0 7px 0'>"

    "<b style='color:#58A6FF'>① 다음 분봉 ▷ [바] N초</b><br>"
    "&nbsp;&nbsp;현재 1분봉이 <b>마감될 때까지 남은 초</b><br>"
    "&nbsp;&nbsp;= <b style='color:#39D3BB'>60 − 현재 시각의 초(second)</b>"
    "&nbsp;&nbsp;(시계 기준, 500ms 주기 갱신)<br>"
    "&nbsp;&nbsp;분봉이 확정되는 순간 9단계 파이프라인이 즉시 실행됨<br><br>"

    "<b style='color:#58A6FF'>② 막대 색상 기준</b><br>"
    "<table style='margin-left:14px;border-collapse:collapse;'>"
    "<tr><td style='color:#39D3BB;font-weight:bold;padding-right:8px;'>■ 초록</td>"
    "<td>20초 이상&nbsp;&nbsp;—&nbsp;&nbsp;여유 있음</td></tr>"
    "<tr><td style='color:#FFB74D;font-weight:bold;padding-right:8px;'>■ 황색</td>"
    "<td>10 ~ 19초&nbsp;&nbsp;—&nbsp;&nbsp;분봉 마감 임박</td></tr>"
    "<tr><td style='color:#F85149;font-weight:bold;padding-right:8px;'>■ 빨강</td>"
    "<td>5초 이하&nbsp;&nbsp;—&nbsp;&nbsp;파이프라인 진입 직전</td></tr>"
    "</table><br>"

    "<b style='color:#58A6FF'>③ ↑ 마지막 갱신 N초 전</b><br>"
    "&nbsp;&nbsp;<b>9단계 파이프라인이 마지막으로 완료된 시각</b>으로부터 경과한 시간<br>"
    "&nbsp;&nbsp;로그 패널에 메시지가 마지막으로 기록된 시각을 기준으로 함<br><br>"

    "<b style='color:#58A6FF'>④ 두 값이 비슷한 이유</b><br>"
    "&nbsp;&nbsp;파이프라인은 분봉 시작 직후(~0초)에 실행됨<br>"
    "&nbsp;&nbsp;→ 분봉 중반(33초)에는 마지막 갱신도 약 33초 전으로 나타남<br><br>"

    "<b style='color:#F85149'>⑤ 이상 신호 감지</b><br>"
    "&nbsp;&nbsp;다음 분봉까지 <b>5초</b> 남았는데 마지막 갱신이 <b>120초 전</b>이면<br>"
    "&nbsp;&nbsp;→ 직전 분봉에서 파이프라인이 <b>누락</b>된 것<br>"
    "&nbsp;&nbsp;→ <b>2 경보 ⚠</b> 탭에서 STEP 오류 확인 권장"

    "</div>"
)

_PIPE_HEALTH_TIP = (
    "<div style='font-family:Consolas,monospace;font-size:12px;line-height:1.75;"
    "min-width:420px;'>"

    "<b style='color:#39D3BB;font-size:13px;'>분봉 파이프라인 심박</b>"
    "<hr style='border:0;border-top:1px solid #30363D;margin:5px 0 7px 0'>"

    "<b style='color:#58A6FF'>① 막대 의미</b><br>"
    "&nbsp;&nbsp;마지막 1분봉이 <b>9단계 파이프라인을 통과한 시각</b>으로부터 경과한 시간<br>"
    "&nbsp;&nbsp;파이프라인 정상 완료 시 막대가 왼쪽으로 리셋됨<br><br>"

    "<b style='color:#58A6FF'>② 막대 색상</b><br>"
    "<table style='margin-left:14px;border-collapse:collapse;'>"
    "<tr><td style='color:#39D3BB;font-weight:bold;padding-right:8px;'>■ 청록</td>"
    "<td>60초 이내&nbsp;&nbsp;—&nbsp;&nbsp;<b>정상</b> (매분 파이프라인 동작 중)</td></tr>"
    "<tr><td style='color:#FFB74D;font-weight:bold;padding-right:8px;'>■ 주황</td>"
    "<td>60 ~ 120초&nbsp;&nbsp;—&nbsp;&nbsp;<b>경보</b> 발송됨</td></tr>"
    "<tr><td style='color:#F85149;font-weight:bold;padding-right:8px;'>■ 빨강</td>"
    "<td>120초 초과&nbsp;&nbsp;—&nbsp;&nbsp;<b>슬랙 + 긴급복구</b> 실행됨</td></tr>"
    "</table><br>"

    "<b style='color:#58A6FF'>③ 미실행 경과 시 자동 조치</b><br>"
    "<table style='margin-left:14px;border-collapse:collapse;line-height:1.9;'>"
    "<tr><td style='color:#FFB74D;padding-right:8px;'>60초</td>"
    "<td>⚠ <b>2 경보 탭</b> 로그 — 분봉 수신 지연 의심, 장 시간 확인 안내</td></tr>"
    "<tr><td style='color:#FFB74D;padding-right:8px;'>120초</td>"
    "<td>⚠ <b>경보 탭 + 슬랙</b> 알림 — 60초 내 미복구 시 자동 조치 예고</td></tr>"
    "<tr><td style='color:#F85149;padding-right:8px;'>180초</td>"
    "<td>⛔ <b>경보 탭 + 슬랙 + 긴급 복구</b> 자동 실행</td></tr>"
    "</table><br>"

    "<b style='color:#58A6FF'>④ 긴급 복구 루틴 (180초 초과)</b><br>"
    "<table style='margin-left:14px;border-collapse:collapse;line-height:1.9;'>"
    "<tr><td style='color:#39D3BB;padding-right:8px;'>DB 분봉 없음</td>"
    "<td>경보 로그 후 종료</td></tr>"
    "<tr><td style='color:#39D3BB;padding-right:8px;'>&gt; 10분 전 데이터</td>"
    "<td>복구 포기 — 장외 시간 판단</td></tr>"
    "<tr><td style='color:#39D3BB;padding-right:8px;'>≤ 10분 전 데이터</td>"
    "<td>raw_candles 최신 분봉으로 파이프라인 강제 재실행</td></tr>"
    "</table><br>"

    "<b style='color:#F85149'>⑤ 가능한 원인</b><br>"
    "&nbsp;&nbsp;① 키움 API 무응답&nbsp;&nbsp;"
    "② on_candle_closed 미호출&nbsp;&nbsp;"
    "③ STEP 내 예외&nbsp;&nbsp;"
    "④ 장외 시간"

    "</div>"
)

_CB_TIP = (
    "<div style='font-family:Consolas,monospace;font-size:12px;line-height:1.75;"
    "min-width:440px;'>"

    "<b style='color:#F85149;font-size:13px;'>⛔ Circuit Breaker — 5종 비상 정지</b>"
    "<hr style='border:0;border-top:1px solid #30363D;margin:5px 0 7px 0'>"

    # ── 상태 3종 ──────────────────────────────────────────────────────
    "<b style='color:#58A6FF'>① 3가지 상태</b><br>"
    "<table style='margin-left:10px;border-collapse:collapse;line-height:2.0;'>"
    "<tr>"
    "<td style='color:#3FB950;font-weight:bold;padding-right:10px;'>NORMAL</td>"
    "<td>진입 허용 — 파이프라인 정상 동작</td>"
    "</tr><tr>"
    "<td style='color:#D29922;font-weight:bold;padding-right:10px;'>PAUSED</td>"
    "<td>시간 제한 진입 정지 → <b>시간 경과 시 자동 NORMAL 복귀</b></td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:10px;'>HALTED</td>"
    "<td>당일 영구 정지 → <b>재시작 또는 15:40 이후에만 해제</b></td>"
    "</tr>"
    "</table>"
    "<br>"

    # ── 발동 조건 5종 ─────────────────────────────────────────────────
    "<b style='color:#58A6FF'>② 발동 조건 5종</b><br>"
    "<table style='margin-left:10px;border-collapse:collapse;line-height:1.9;'>"
    "<tr>"
    "<td style='color:#A371F7;font-weight:bold;padding-right:8px;'>①</td>"
    "<td>1분 내 신호 <b>5번 이상 반전</b></td>"
    "<td style='padding-left:12px;color:#D29922;'>→ PAUSED 15분</td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:8px;'>②</td>"
    "<td>5분 내 <b>손절 3연속</b></td>"
    "<td style='padding-left:12px;color:#F85149;'>→ HALTED 당일 정지</td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:8px;'>③</td>"
    "<td>30분 이동정확도 <b>&lt; 35%</b></td>"
    "<td style='padding-left:12px;color:#F85149;'>→ HALTED 당일 정지</td>"
    "</tr><tr>"
    "<td style='color:#D29922;font-weight:bold;padding-right:8px;'>④</td>"
    "<td>현재 ATR ≥ 30분 평균 × <b>3배</b></td>"
    "<td style='padding-left:12px;color:#D29922;'>→ PAUSED 5분</td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:8px;'>⑤</td>"
    "<td>API 응답 지연 <b>≥ 5초</b></td>"
    "<td style='padding-left:12px;color:#F85149;'>→ 즉시 청산 + PAUSED</td>"
    "</tr>"
    "</table>"
    "<br>"

    # ── 해제 방법 ─────────────────────────────────────────────────────
    "<b style='color:#58A6FF'>③ 해제 방법 및 조건</b><br>"
    "<table style='margin-left:10px;border-collapse:collapse;line-height:1.9;'>"
    "<tr>"
    "<td style='color:#D29922;font-weight:bold;padding-right:10px;'>PAUSED</td>"
    "<td>설정된 정지 시간 자동 만료 → <b>별도 조작 불필요</b></td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:10px;'>HALTED</td>"
    "<td>"
    "<b style='color:#39D3BB'>프로그램 재시작</b>&nbsp;(상태 파일 없음 — 메모리 초기화)<br>"
    "&nbsp;&nbsp;&nbsp;또는&nbsp;&nbsp;"
    "<b style='color:#39D3BB'>15:40 자동 리셋</b>&nbsp;(daily_close → reset_daily)"
    "</td>"
    "</tr>"
    "</table>"
    "<hr style='border:0;border-top:1px solid #30363D;margin:7px 0 5px 0'>"
    "<span style='color:#8B949E;font-size:11px;'>"
    "▸ 상태는 매분 [DBG-CB] 로그로 확인 가능 &nbsp;|&nbsp; "
    "당일 HALTED 상태에서 재시작하면 즉시 NORMAL 복귀"
    "</span>"

    "</div>"
)


def make_style() -> str:
    """해상도 감지 후 동적 폰트 사이즈 적용 스타일시트 생성"""
    return f"""
    QMainWindow, QWidget {{
        background-color: {C['bg']};
        color: {C['text']};
        font-family: 'D2Coding', 'Consolas', 'Malgun Gothic', monospace;
        font-size: {S.f(12)}px;
    }}
    QGroupBox {{
        border: 1px solid {C['border']};
        border-radius: {S.p(6)}px;
        margin-top: {S.p(8)}px;
        padding: {S.p(6)}px;
        font-weight: bold;
        color: {C['text2']};
        font-size: {S.f(11)}px;
        letter-spacing: 1px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {S.p(8)}px;
        padding: 0 {S.p(4)}px;
    }}
    QTabWidget::pane {{
        border: 1px solid {C['border']};
        background: {C['bg2']};
    }}
    QTabBar::tab {{
        background: {C['bg3']};
        color: {C['text2']};
        padding: {S.p(7)}px {S.p(16)}px;
        border: none;
        font-size: {S.f(11)}px;
        letter-spacing: 0.5px;
    }}
    QTabBar::tab:selected {{
        background: {C['bg2']};
        color: {C['text']};
        border-bottom: 2px solid {C['blue']};
    }}
    QTextEdit {{
        background: {C['bg']};
        color: {C['text']};
        border: 1px solid {C['border']};
        border-radius: {S.p(4)}px;
        font-family: 'D2Coding', 'Consolas', monospace;
        font-size: {S.f(11)}px;
    }}
    QPushButton {{
        background: {C['bg3']};
        color: {C['text']};
        border: 1px solid {C['border']};
        border-radius: {S.p(4)}px;
        padding: {S.p(6)}px {S.p(14)}px;
        font-size: {S.f(11)}px;
    }}
    QPushButton:hover {{
        background: {C['border']};
    }}
    QProgressBar {{
        background: {C['bg3']};
        border: none;
        border-radius: {S.p(3)}px;
        height: {S.p(6)}px;
    }}
    QProgressBar::chunk {{
        border-radius: {S.p(3)}px;
    }}
    QScrollBar:vertical {{
        background: {C['bg']};
        width: {S.p(7)}px;
    }}
    QScrollBar::handle:vertical {{
        background: {C['border']};
        border-radius: {S.p(3)}px;
    }}
    QLabel {{
        font-size: {S.f(12)}px;
    }}
    QToolTip {{
        background: {C['bg2']};
        color: {C['text']};
        border: 1px solid {C['blue']};
        border-radius: {S.p(4)}px;
        padding: {S.p(8)}px;
        font-family: 'D2Coding', 'Consolas', monospace;
        font-size: {S.f(10)}px;
    }}
"""


# ────────────────────────────────────────────────────────────
# 공통 위젯 헬퍼 (모두 S.f() 로 동적 스케일)
# ────────────────────────────────────────────────────────────
def mk_label(text, color=None, size=12, bold=False, align=Qt.AlignLeft):
    lb = QLabel(text)
    lb.setAlignment(align)
    style = f"font-size:{S.f(size)}px;"
    if color:
        style += f"color:{color};"
    if bold:
        style += "font-weight:bold;"
    lb.setStyleSheet(style)
    return lb


def mk_val_label(text="——", color=C['text'], size=15, bold=True, align=None):
    lb = QLabel(text)
    a  = align if align else (Qt.AlignRight | Qt.AlignVCenter)
    lb.setAlignment(a)
    lb.setStyleSheet(
        f"font-size:{S.f(size)}px;color:{color};"
        f"font-weight:{'bold' if bold else 'normal'};"
    )
    return lb


def mk_badge(text, bg, fg="#ffffff", size=10):
    lb = QLabel(f"  {text}  ")
    lb.setStyleSheet(
        f"background:{bg};color:{fg};border-radius:{S.p(3)}px;"
        f"font-size:{S.f(size)}px;font-weight:bold;"
        f"padding:{S.p(1)}px {S.p(3)}px;"
    )
    return lb


def mk_sep():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color:{C['border']};")
    return line


def mk_prog(color=C['green'], h=6):
    pb = QProgressBar()
    pb.setFixedHeight(S.p(h))
    pb.setTextVisible(False)
    pb.setStyleSheet(f"QProgressBar::chunk{{background:{color};}}")
    return pb


def card(title, widget, color=C['blue'], header_widget=None):
    gb = QGroupBox("" if header_widget else f"● {title}")
    gb.setStyleSheet(
        f"QGroupBox{{border:1px solid {C['border']};border-radius:{S.p(6)}px;"
        f"margin-top:{S.p(8)}px;padding:{S.p(8)}px;color:{color};"
        f"font-size:{S.f(11)}px;font-weight:bold;letter-spacing:1px;}}"
        f"QGroupBox::title{{subcontrol-origin:margin;"
        f"left:{S.p(8)}px;padding:0 {S.p(4)}px;}}"
    )
    lay = QVBoxLayout(gb)
    if header_widget:
        lay.setContentsMargins(S.p(8), S.p(8), S.p(8), S.p(6))
        lay.setSpacing(S.p(6))
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(S.p(8))
        header.addWidget(mk_label(f"● {title}", color, 11, True))
        header.addStretch()
        header.addWidget(header_widget)
        lay.addLayout(header)
    else:
        lay.setContentsMargins(S.p(4), S.p(14), S.p(4), S.p(4))
        lay.setSpacing(S.p(4))
    lay.addWidget(widget)
    return gb


# ────────────────────────────────────────────────────────────
# 패널 1: 멀티 호라이즌 예측 + 파라미터 분석
# ────────────────────────────────────────────────────────────
class PredictionPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._hz_labels = {}
        self._param_bars = {}
        self._param_vals = {}
        self._build()

    def _make_report_tab(self, title: str, accent: str):
        frame = QFrame()
        frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(S.p(10), S.p(8), S.p(10), S.p(8))
        lay.setSpacing(S.p(4))
        lay.addWidget(mk_label(title, accent, 9, True))
        value = mk_val_label("--", accent, 18, True)
        detail = mk_label("--", C['text2'], 8)
        spark = mk_label("?" * 16, accent, 8)
        spark.setFont(__import__('PyQt5.QtGui', fromlist=['QFont']).QFont("Consolas", S.f(8)))
        lay.addWidget(value)
        lay.addWidget(detail)
        lay.addWidget(spark)
        lay.addStretch()
        return frame, value, detail, spark

    def _history_series(self, history: list, key: str) -> list:
        vals = []
        for item in history[-24:]:
            try:
                if key not in item or item[key] is None:
                    continue
                vals.append(float(item[key]))
            except Exception:
                continue
        return vals

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # 상단: 현재가 + 신호
        top = QHBoxLayout()
        self.lbl_price   = mk_val_label("——.——", C['text'], 20)
        self.lbl_signal  = mk_val_label("대기중", C['text2'], 16)
        self.lbl_conf    = mk_label("신뢰도 — %", C['text2'])
        top.addWidget(mk_label("현재가", C['text2']))
        top.addWidget(self.lbl_price, 2)
        top.addWidget(self.lbl_signal, 2)
        top.addWidget(self.lbl_conf, 1)
        lay.addLayout(top)
        lay.addWidget(mk_sep())

        # 모델 상태 행 (학습 대기 / 재학습중) — model.is_ready() 시 숨김
        self._model_row = QWidget()
        _mrow = QHBoxLayout(self._model_row)
        _mrow.setContentsMargins(0, 2, 0, 2)
        _mrow.setSpacing(6)
        self._lbl_model_state  = mk_label("모델 학습 대기", C['orange'], 10, True)
        self._model_prog       = mk_prog(C['orange'], 8)
        self._model_prog.setRange(0, 100)
        self._model_prog.setValue(0)
        self._lbl_model_detail = mk_label("", C['text2'], 9)
        _mrow.addWidget(self._lbl_model_state)
        _mrow.addWidget(self._model_prog, 2)
        _mrow.addWidget(self._lbl_model_detail, 1)
        lay.addWidget(self._model_row)
        lay.addSpacing(8)   # 모델 상태 행 ↔ 섹션 타이틀 여백

        # ── 섹션: 멀티 호라이즌 예측 ─────────────────────────────
        hz_title = mk_label("멀티 호라이즌 예측 ( 1 · 3 · 5 · 10 · 15 · 30분 )", C['blue'], 10, True)
        lay.addWidget(hz_title)
        hgrid = QGridLayout()
        hgrid.setSpacing(4)
        for i, hname in enumerate(["1분","3분","5분","10분","15분","30분"]):
            frame = QFrame()
            frame.setFixedHeight(72)
            frame.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
                f"border-radius:6px;}}"
            )
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(6, 4, 6, 4)
            hl = mk_label(hname, C['text2'], 10, align=Qt.AlignCenter)
            arr = mk_label("—", C['text2'], 22, True, Qt.AlignCenter)
            pct = mk_label("—%", C['text2'], 10, align=Qt.AlignCenter)
            fl.addWidget(hl)
            fl.addWidget(arr)
            fl.addWidget(pct)
            self._hz_labels[hname] = (frame, arr, pct)
            hgrid.addWidget(frame, 0, i)
        lay.addLayout(hgrid)

        # ── 섹션 구분 ─────────────────────────────────────────────
        lay.addSpacing(16)
        lay.addWidget(mk_sep())
        lay.addSpacing(12)

        # ── 섹션: 파라미터 중요도 ────────────────────────────────
        param_title = mk_label("파라미터 중요도 (SHAP 실시간)", C['purple'], 10, True)
        param_title.setToolTip(
            "각 피처가 현재 GBM 예측에 얼마나 기여하는지 나타내는 중요도 지표입니다.\n"
            "\n"
            "【SHAP 실시간의 의미】\n"
            "  • SHAP = SHapley Additive exPlanations\n"
            "    '이번 예측이 왜 이 방향인지'를 피처별 기여도로 분해한 값입니다.\n"
            "  • '실시간' = GBM 배치 재학습 직후 최신 모델 가중치로 자동 갱신됩니다.\n"
            "    매 분봉마다 화면이 새로 그려지지만, 재학습 전까지는 같은 값이 유지됩니다.\n"
            "\n"
            "【업데이트 조건】\n"
            "  • GBM 최초 학습 전: 모든 항목 0.0% (GBM 미학습 상태)\n"
            "  • GBM 배치 재학습 완료 시 자동 갱신\n"
            "    - 주간: 매주 월요일 08:50~09:00\n"
            "    - 월간: 매월 재학습 스케줄 도래 시\n"
            "    - 학습 최소 데이터: 5,000분봉 (약 13거래일)\n"
            "  • CORE 3종(CVD·VWAP·OFI)은 절대 교체 불가 피처입니다."
        )
        lay.addWidget(param_title)
        params = [
            ("CVD 다이버전스", "CORE", C['cyan']),
            ("VWAP 위치",      "CORE", C['cyan']),
            ("OFI 불균형",     "CORE", C['cyan']),
            ("외인 콜순매수",  "SHAP", C['purple']),
            ("다이버전스 지수","SHAP", C['purple']),
            ("프로그램 비차익","SHAP", C['purple']),
        ]
        pgrid = QGridLayout()
        pgrid.setSpacing(3)
        for i, (name, tag, col) in enumerate(params):
            badge = mk_badge(tag, col if tag=="CORE" else C['bg3'],
                             C['bg'] if tag=="CORE" else C['purple'])
            nlab  = mk_label(name, C['text'], 10)
            bar   = mk_prog(col, 8)
            vlab  = mk_val_label("—%", col, 11)
            pgrid.addWidget(badge, i, 0)
            pgrid.addWidget(nlab,  i, 1)
            pgrid.addWidget(bar,   i, 2)
            pgrid.addWidget(vlab,  i, 3)
            self._param_bars[name] = bar
            self._param_vals[name] = vlab
        lay.addLayout(pgrid)

        # ── 섹션 구분 ─────────────────────────────────────────────
        lay.addSpacing(16)
        lay.addWidget(mk_sep())
        lay.addSpacing(12)

        # ── 섹션: 파라미터 상관계수 ──────────────────────────────
        corr_title = mk_label("파라미터 상관계수", C['orange'], 10, True)
        corr_title.setToolTip(
            "GBM 피처 중요도 상위 항목을 요약한 레이블입니다.\n"
            "\n"
            "【표시 형식】\n"
            "  중요도가 높은 순으로 '피처이름+기여도' 형태로 나열합니다.\n"
            "  예) CVD+0.31  VWAP+0.22  OFI+0.18\n"
            "\n"
            "【업데이트 조건】\n"
            "  • GBM 최초 학습 전: '—' (데이터 부족 또는 미학습)\n"
            "  • GBM 배치 재학습 완료 시 자동 갱신\n"
            "    - 주간: 매주 월요일 08:50~09:00\n"
            "    - 학습 최소 데이터: 5,000분봉 (약 13거래일)\n"
            "  • 기여도 0인 항목은 표시되지 않습니다."
        )
        lay.addWidget(corr_title)
        self.corr_label = mk_label("—", C['text2'], 9)
        lay.addWidget(self.corr_label)
        lay.addStretch(1)

    def update_data(self, price, preds, params, conf=None, corr=""):
        self._model_row.setVisible(False)
        self.lbl_price.setText(f"{price:.2f}")

        # 앙상블 신뢰도 (실거래 데이터가 들어올 때만 갱신)
        if conf is not None:
            self.lbl_conf.setText(f"신뢰도 {conf*100:.1f}%")
            self.lbl_conf.setStyleSheet(
                f"color:{C['green'] if conf>=0.7 else C['orange'] if conf>=0.58 else C['red']};"
                f"font-size:{S.f(13)}px;font-weight:bold;"
            )

        # 앙상블 방향
        ups = sum(1 for v in preds.values() if v['signal'] == 1)
        dns = sum(1 for v in preds.values() if v['signal'] == -1)
        if ups >= 4:
            self.lbl_signal.setText("▲ 매수")
            self.lbl_signal.setStyleSheet(f"color:{C['green']};font-size:{S.f(16)}px;font-weight:bold;")
        elif dns >= 4:
            self.lbl_signal.setText("▼ 매도")
            self.lbl_signal.setStyleSheet(f"color:{C['red']};font-size:{S.f(16)}px;font-weight:bold;")
        else:
            self.lbl_signal.setText("— 관망")
            self.lbl_signal.setStyleSheet(f"color:{C['text2']};font-size:{S.f(16)}px;font-weight:bold;")

        # 호라이즌 카드
        for hname, pred in preds.items():
            if hname not in self._hz_labels:
                continue
            frame, arr, pct = self._hz_labels[hname]
            if pred['signal'] == 1:
                col = C['green']
                arr.setText("▲")
                pct.setText(f"{pred['up']*100:.1f}%")
                frame.setStyleSheet(
                    f"QFrame{{background:#0D2818;border:1px solid {C['green']};border-radius:6px;}}")
            elif pred['signal'] == -1:
                col = C['red']
                arr.setText("▼")
                pct.setText(f"{pred['dn']*100:.1f}%")
                frame.setStyleSheet(
                    f"QFrame{{background:#2D0D0D;border:1px solid {C['red']};border-radius:6px;}}")
            else:
                col = C['text2']
                arr.setText("—")
                pct.setText("횡보")
                frame.setStyleSheet(
                    f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};border-radius:6px;}}")
            arr.setStyleSheet(f"color:{col};font-size:{S.f(22)}px;font-weight:bold;")
            pct.setStyleSheet(f"color:{col};font-size:{S.f(12)}px;")

        # SHAP 바
        for name, val in params.items():
            if name in self._param_bars:
                self._param_bars[name].setValue(int(val * 100))
                self._param_vals[name].setText(f"{val*100:.1f}%")

        # 상관계수 레이블 (GBM 중요도 기반, 없으면 —)
        self.corr_label.setText(corr if corr else "—")

    def set_model_status(self, state, detail="", progress=-1, price=None,
                         update_signal=True):
        """모델 상태 행 업데이트 (학습 대기 / 재학습중 / 완료).

        Args:
            state:    표시할 상태 문자열
            detail:   우측 보조 텍스트 (예: "데이터 416/5000행 (8%)")
            progress: 0~100 진행률, -1이면 프로그레스바 숨김
            price:    현재가 (None이면 미갱신)
        """
        _COL = {
            "모델 학습 대기":  C['orange'],
            "GBM 재학습중":   C['yellow'],
            "GBM 재학습 완료": C['green'],
            "데이터 축적중":   C['orange'],
            "SGD 예측중":     C['blue'],
        }
        col = _COL.get(state, C['text2'])

        if price is not None:
            self.lbl_price.setText(f"{price:.2f}")

        # lbl_signal에 상태 표시 (SGD-only 모드에서는 예측 신호 유지)
        if update_signal:
            self.lbl_signal.setText(state)
            self.lbl_signal.setStyleSheet(
                f"color:{col};font-size:{S.f(13)}px;font-weight:bold;"
            )

        # 모델 상태 행
        self._model_row.setVisible(True)
        self._lbl_model_state.setText(state)
        self._lbl_model_state.setStyleSheet(
            f"color:{col};font-size:{S.f(10)}px;font-weight:bold;"
        )
        self._lbl_model_detail.setText(detail)

        if progress >= 0:
            self._model_prog.setVisible(True)
            self._model_prog.setValue(progress)
            self._model_prog.setStyleSheet(
                f"QProgressBar::chunk{{background:{col};}}"
            )
        else:
            self._model_prog.setVisible(False)


class PositionRestoreDialog(QDialog):
    """포지션 수동 복원 다이얼로그 (모의투자 TR blank 대응)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("포지션 수동 복원")
        self.setModal(True)
        self.setFixedWidth(S.p(320))
        self.setStyleSheet(
            f"QDialog{{background:{C['bg2']};color:{C['text']};}}"
            f"QLabel{{color:{C['text']};font-size:{S.f(10)}px;}}"
            f"QDoubleSpinBox,QSpinBox{{background:{C['bg3']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:3px;padding:2px 6px;"
            f"font-size:{S.f(10)}px;}}"
            f"QComboBox{{background:{C['bg3']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:3px;padding:2px 6px;"
            f"font-size:{S.f(10)}px;}}"
            f"QComboBox QAbstractItemView{{background:{C['bg2']};color:{C['text']};"
            f"selection-background-color:{C['blue']};}}"
            f"QPushButton{{background:{C['blue']};color:#fff;border:none;"
            f"border-radius:4px;padding:4px 12px;font-size:{S.f(10)}px;font-weight:bold;}}"
            f"QPushButton[text='취소']{{background:{C['bg3']};color:{C['text2']};}}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.p(16), S.p(12), S.p(16), S.p(12))
        lay.setSpacing(S.p(10))

        warn = mk_label(
            "⚠ 모의투자 서버 TR blank 시 사용. 실제 HTS 잔고를 직접 입력하세요.",
            C['orange'], 9,
        )
        warn.setWordWrap(True)
        lay.addWidget(warn)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(S.p(8))
        form.setLabelAlignment(Qt.AlignRight)

        self.cmb_direction = QComboBox()
        self.cmb_direction.addItems(["LONG (매수)", "SHORT (매도)"])
        form.addRow("방향:", self.cmb_direction)

        self.spn_price = QDoubleSpinBox()
        self.spn_price.setRange(100.0, 9999.99)
        self.spn_price.setDecimals(2)
        self.spn_price.setSingleStep(0.05)
        self.spn_price.setValue(0.0)
        form.addRow("진입가(pt):", self.spn_price)

        self.spn_qty = QSpinBox()
        self.spn_qty.setRange(1, 99)
        self.spn_qty.setValue(1)
        form.addRow("수량(계약):", self.spn_qty)

        self.spn_atr = QDoubleSpinBox()
        self.spn_atr.setRange(0.5, 50.0)
        self.spn_atr.setDecimals(2)
        self.spn_atr.setSingleStep(0.1)
        self.spn_atr.setValue(5.0)
        form.addRow("ATR(pt):", self.spn_atr)

        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("복원")
        btns.button(QDialogButtonBox.Cancel).setText("취소")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def get_values(self):
        direction = "LONG" if self.cmb_direction.currentIndex() == 0 else "SHORT"
        return direction, self.spn_price.value(), self.spn_qty.value(), self.spn_atr.value()


class AccountInfoPanel(QWidget):
    sig_position_restore = pyqtSignal(str, float, int, float)  # direction, price, qty, atr

    def __init__(self):
        super().__init__()
        self._summary_values = {}
        self._live_tick = 0
        self._balance_last_update_dt = None
        self._balance_last_source = ""
        self._balance_active = False
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.p(8), S.p(4), S.p(8), S.p(8))
        lay.setSpacing(S.p(8))

        live_box = QWidget()
        live_row = QHBoxLayout(live_box)
        live_row.setContentsMargins(0, 0, 0, 0)
        live_row.setSpacing(S.p(6))
        self.lbl_balance_live = mk_label("LIVE", C['cyan'], 9, True, Qt.AlignRight)
        self.pb_balance_live = mk_prog(C['cyan'], 7)
        self.pb_balance_live.setFixedWidth(S.p(108))
        self.pb_balance_live.setRange(0, 100)
        self.pb_balance_live.setValue(0)
        self.lbl_balance_stamp = mk_label("awaiting balance", C['text2'], 8, False, Qt.AlignLeft)
        self.lbl_balance_stamp.setMinimumWidth(S.p(124))
        self.lbl_balance_stamp.setStyleSheet(
            f"color:{C['text2']};font-size:{S.f(8)}px;"
            f"font-family:Consolas,D2Coding,monospace;"
        )
        self.btn_position_restore = QPushButton("포지션 복원")
        self.btn_position_restore.setFixedWidth(S.p(80))
        self.btn_position_restore.setCursor(Qt.PointingHandCursor)
        self.btn_position_restore.setStyleSheet(
            f"QPushButton{{background:{C['orange']};color:#fff;border:none;"
            f"border-radius:3px;padding:2px 6px;font-size:{S.f(8)}px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#d4890a;}}"
        )
        self.btn_position_restore.setToolTip(
            "<html><body style='background:#1e1e2e;color:#cdd6f4;"
            "font-size:12px;padding:6px;min-width:340px;'>"
            "<p style='color:#fab387;font-weight:bold;margin:0 0 6px 0;'>"
            "&#9888; 포지션 수동 복원</p>"

            "<p style='color:#89b4fa;font-weight:bold;margin:0 0 3px 0;'>"
            "&#9654; 사용 목적</p>"
            "<p style='margin:0 0 8px 8px;'>"
            "모의투자 서버에서 <b>OPW20006 TR이 공란</b>을 반환할 때,<br>"
            "또는 미륵이 <b>재시작 후 실제 보유 포지션이 대시보드에 표시되지 않을 때</b><br>"
            "HTS 실제 잔고를 직접 입력해 UI를 동기화합니다.<br>"
            "<span style='color:#f38ba8;'>&#8251; 실서버 정상 가동 중에는 사용하지 마세요.</span>"
            "</p>"

            "<p style='color:#89b4fa;font-weight:bold;margin:0 0 3px 0;'>"
            "&#9654; 사용 방법</p>"
            "<ol style='margin:0 0 8px 16px;padding:0;'>"
            "<li>HTS 실시간잔고 화면 확인</li>"
            "<li>방향(매수=LONG / 매도=SHORT) 선택</li>"
            "<li>진입가: HTS <b>매입가(원)</b>를 <b>1,000으로 나눈 값</b> 입력<br>"
            "<span style='color:#a6e3a1;'>"
            "예) HTS 1,153,000원 &rarr; 1153.00pt 입력</span></li>"
            "<li>수량: HTS 보유량(계약수) 입력</li>"
            "<li>ATR 입력 후 <b>[복원]</b> 클릭</li>"
            "<li>잔고 UI 자동 갱신 + position_state.json 저장</li>"
            "</ol>"

            "<p style='color:#89b4fa;font-weight:bold;margin:0 0 3px 0;'>"
            "&#9654; ATR 수치 참조 방법</p>"
            "<p style='margin:0 0 4px 8px;'>"
            "ATR = 최근 1분봉 평균 변동폭 (포인트 단위)<br>"
            "손절라인 = 진입가 &plusmn; ATR&times;1.5 &nbsp;|&nbsp; "
            "TP1 = &plusmn; ATR&times;1.0</p>"
            "<ul style='margin:0 0 4px 16px;padding:0;'>"
            "<li>로그 탭 검색: <code>[DBG-F4]</code> &rarr; <code>ATR floor=X.XXpt</code></li>"
            "<li>WARN 로그 파일: <code>logs/YYYYMMDD_WARN.log</code> 에서 <code>atr=</code> 검색</li>"
            "<li>ATR 모를 경우 <b>기본값 5.0pt 사용</b> 권장<br>"
            "<span style='color:#cba6f7;'>"
            "(평온한 장 2~4pt | 보통 4~7pt | 고변동 7~15pt)</span></li>"
            "</ul>"
            "</body></html>"
        )
        self.btn_position_restore.clicked.connect(self._on_position_restore_clicked)
        live_row.addWidget(self.lbl_balance_live)
        live_row.addWidget(self.pb_balance_live)
        live_row.addWidget(self.lbl_balance_stamp)
        live_row.addStretch()
        live_row.addWidget(self.btn_position_restore)
        self.live_header_widget = live_box

        lay.addWidget(mk_sep())

        summary_grid = QGridLayout()
        summary_grid.setContentsMargins(0, 0, 0, 0)
        summary_grid.setHorizontalSpacing(S.p(18))
        summary_grid.setVerticalSpacing(S.p(10))
        for text, row, col in [
            ("총매매", 0, 0),
            ("총평가손익", 0, 1),
            ("실현손익", 0, 2),
            ("총평가", 1, 0),
            ("총평가수익률", 1, 1),
            ("추정자산", 1, 2),
        ]:
            cell = QHBoxLayout()
            cell.setContentsMargins(0, 0, 0, 0)
            cell.setSpacing(S.p(6))
            label = mk_label(f"{text}:", C['text'], 10, True)
            value = mk_label("", C['text2'], 10, align=Qt.AlignLeft)
            value.setMinimumWidth(S.p(104))
            value.setStyleSheet(
                f"font-size:{S.f(10)}px;color:{C['text2']};"
                f"padding:{S.p(4)}px {S.p(8)}px;"
                f"background:{C['bg3']};border:1px solid {C['border']};"
                f"border-radius:{S.p(4)}px;"
            )
            cell.addWidget(label)
            cell.addWidget(value, 1)
            summary_grid.addLayout(cell, row, col)
            self._summary_values[text] = value
        lay.addLayout(summary_grid)
        lay.addWidget(mk_sep())

        self.tbl_balance = QTableWidget(0, 9)
        self.tbl_balance.setHorizontalHeaderLabels([
            "종목코드", "구분", "보유량", "청산가능", "평가손익",
            "평가수익률", "매입가", "현재가", "평가금액"
        ])
        self.tbl_balance.setMinimumHeight(S.p(250))
        self.tbl_balance.verticalHeader().setVisible(False)
        self.tbl_balance.setAlternatingRowColors(False)
        self.tbl_balance.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_balance.setSelectionMode(QTableWidget.NoSelection)
        self.tbl_balance.setFocusPolicy(Qt.NoFocus)
        self.tbl_balance.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_balance.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.tbl_balance.setStyleSheet(
            f"QTableWidget{{background:{C['bg']};border:1px solid {C['border']};"
            f"border-radius:{S.p(4)}px;gridline-color:{C['border']};}}"
            f"QHeaderView::section{{background:{C['bg2']};color:{C['text']};"
            f"padding:{S.p(6)}px;border:none;border-bottom:1px solid {C['blue']};"
            f"font-size:{S.f(9)}px;font-weight:bold;}}"
            f"QTableWidget::item{{padding:{S.p(4)}px;color:{C['text2']};"
            f"font-size:{S.f(9)}px;}}"
        )
        lay.addWidget(self.tbl_balance, 1)

    def tick_live(self):
        self._refresh_live_status()

    def notify_balance_update(self, source: str = "broker", active: bool = True):
        self._balance_last_update_dt = datetime.now()
        self._balance_last_source = str(source or "broker").strip()
        self._balance_active = bool(active)
        self._live_tick = 0
        self._refresh_live_status(just_updated=True)

    def _refresh_live_status(self, just_updated: bool = False):
        now = datetime.now()
        if not self._balance_last_update_dt:
            self.lbl_balance_live.setText("WAIT --:--")
            self.lbl_balance_live.setStyleSheet(
                f"color:{C['orange']};font-size:{S.f(9)}px;font-weight:bold;"
            )
            self.lbl_balance_stamp.setText("awaiting first sync")
            self.lbl_balance_stamp.setStyleSheet(
                f"color:{C['text2']};font-size:{S.f(8)}px;"
                f"font-family:Consolas,D2Coding,monospace;"
            )
            self.pb_balance_live.setStyleSheet(
                f"QProgressBar{{background:{C['bg3']};border:none;border-radius:3px;}}"
                f"QProgressBar::chunk{{background:{C['orange']};border-radius:3px;}}"
            )
            self.pb_balance_live.setValue(8)
            return

        if not self._balance_active:
            self.lbl_balance_live.setText("SLEEP")
            self.lbl_balance_live.setStyleSheet(
                f"color:{C['text2']};font-size:{S.f(9)}px;font-weight:bold;"
            )
            self.lbl_balance_stamp.setText(
                f"flat {self._balance_last_update_dt.strftime('%H:%M:%S')}"
            )
            self.lbl_balance_stamp.setStyleSheet(
                f"color:{C['text2']};font-size:{S.f(8)}px;"
                f"font-family:Consolas,D2Coding,monospace;"
            )
            self.pb_balance_live.setStyleSheet(
                f"QProgressBar{{background:{C['bg3']};border:none;border-radius:3px;}}"
                f"QProgressBar::chunk{{background:{C['border']};border-radius:3px;}}"
            )
            self.pb_balance_live.setValue(0)
            return

        elapsed_s = max(0, int((now - self._balance_last_update_dt).total_seconds()))
        mm, ss = divmod(elapsed_s, 60)
        lap = f"{mm:02d}:{ss:02d}"
        source = self._balance_last_source.upper() if self._balance_last_source else "SYNC"

        if elapsed_s <= 3:
            state = "LIVE"
            col = C['cyan']
            bar = 100 if just_updated else 92 - (elapsed_s * 4)
        elif elapsed_s <= 10:
            state = "FRESH"
            col = C['green']
            bar = 78 - ((elapsed_s - 3) * 4)
        elif elapsed_s <= 30:
            state = "WARM"
            col = C['orange']
            bar = 48 - int((elapsed_s - 10) * 1.2)
        else:
            state = "STALE"
            col = C['red']
            bar = max(10, 24 - min(14, (elapsed_s - 30) // 10))

        self.lbl_balance_live.setText(f"{state} {lap}")
        self.lbl_balance_live.setStyleSheet(
            f"color:{col};font-size:{S.f(9)}px;font-weight:bold;"
        )
        self.lbl_balance_stamp.setText(
            f"{source} {self._balance_last_update_dt.strftime('%H:%M:%S')}"
        )
        self.lbl_balance_stamp.setStyleSheet(
            f"color:{col if elapsed_s <= 30 else C['text2']};font-size:{S.f(8)}px;"
            f"font-family:Consolas,D2Coding,monospace;"
        )
        self.pb_balance_live.setStyleSheet(
            f"QProgressBar{{background:{C['bg3']};border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{col};border-radius:3px;}}"
        )
        self.pb_balance_live.setValue(max(8, min(100, int(bar))))

    @staticmethod
    def _to_number(value):
        text = str(value or "").replace(",", "").replace("%", "").strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _format_value(value, is_percent=False):
        if value is None or str(value).strip() == "":
            return ""
        num = AccountInfoPanel._to_number(value)
        if num is None:
            return str(value).strip()
        if is_percent:
            return f"{num:,.2f}%"
        if abs(num) >= 1000:
            return f"{num:,.0f}"
        return f"{num:,.2f}"

    def update_summary(self, summary: dict):
        summary = dict(summary or {})
        total_eval = self._to_number(summary.get("총평가"))
        total_pnl = self._to_number(summary.get("총평가손익"))
        total_rate = summary.get("총평가수익률")
        if (total_rate is None or str(total_rate).strip() == "") and total_eval not in (None, 0) and total_pnl is not None:
            total_rate = (total_pnl / max(abs(total_eval - total_pnl), 1e-9)) * 100.0
        for key, label in self._summary_values.items():
            label.setText(self._format_value(summary.get(key), is_percent=(key == "총평가수익률")))
        if total_rate is not None:
            self._summary_values["총평가수익률"].setText(self._format_value(total_rate, is_percent=True))

    def update_rows(self, rows):
        rows = list(rows or [])
        self.tbl_balance.setRowCount(len(rows))
        columns = [
            ("종목코드", False),
            ("매매구분", False),
            ("잔고수량", False),
            ("주문가능수량", False),
            ("평가손익", False),
            ("손익율", True),
            ("매입단가", False),
            ("현재가", False),
            ("평가금액", False),
        ]
        for r, row in enumerate(rows):
            for c, (field, is_percent) in enumerate(columns):
                raw = row.get(field, "")
                text = self._format_value(raw, is_percent=is_percent) if c >= 2 else str(raw or "").strip()
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.tbl_balance.setItem(r, c, item)

    def _on_position_restore_clicked(self):
        dlg = PositionRestoreDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            direction, price, qty, atr = dlg.get_values()
            if price > 0 and qty > 0:
                self.sig_position_restore.emit(direction, price, qty, atr)


# ────────────────────────────────────────────────────────────
# 패널 2: 다이버전스 지수 + 포지션 매트릭스
# ────────────────────────────────────────────────────────────
class DivergencePanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("외인-개인 다이버전스 지수 (역발상 핵심 신호)", C['orange'], 10, True))

        # 바이어스 미터
        for label, attr_prefix, lcol, rcol, ltext, rtext in [
            ("개인 방향", "rt", C['green'], C['red'], "풋↑", "콜↑"),
            ("외인 방향", "fi", C['red'],   C['green'], "풋↑", "콜↑"),
        ]:
            row = QHBoxLayout()
            row.addWidget(mk_label(label, C['text2'], 9))
            row.addWidget(mk_label(ltext, lcol, 9))
            bar_l = mk_prog(lcol, 12)
            bar_r = mk_prog(rcol, 12)
            setattr(self, f"{attr_prefix}_put_bar", bar_l)
            setattr(self, f"{attr_prefix}_call_bar", bar_r)
            mid_frame = QFrame()
            mid_lay = QHBoxLayout(mid_frame)
            mid_lay.setContentsMargins(0, 0, 0, 0)
            mid_lay.setSpacing(1)
            mid_lay.addWidget(bar_l)
            mid_lay.addWidget(bar_r)
            row.addWidget(mid_frame, 3)
            row.addWidget(mk_label(rtext, rcol, 9))
            lay.addLayout(row)

        lay.addWidget(mk_sep())

        # 포지션 카드 (2×4 그리드)
        lay.addWidget(mk_label("투자자 포지션 매트릭스", C['blue'], 10, True))
        pos_grid = QGridLayout()
        pos_grid.setSpacing(4)
        positions = [
            ("개인 콜매수",   "rt_call",   C['red']),
            ("개인 풋매수",   "rt_put",    C['green']),
            ("개인 양매수",   "rt_strd",   C['text2']),
            ("역발상 신호",   "contrarian",C['orange']),
            ("외인 콜순매수", "fi_call",   C['green']),
            ("외인 풋순매수", "fi_put",    C['red']),
            ("외인 양매도",   "fi_strangle",C['text2']),
            ("다이버전스",    "div_score", C['orange']),
        ]
        for i, (title, attr, col) in enumerate(positions):
            f = QFrame()
            f.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
                f"border-radius:5px;padding:4px;}}"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6, 4, 6, 4)
            fl.setSpacing(1)
            t = mk_label(title, C['text2'], 9)
            v = mk_val_label("——", col, 13)
            fl.addWidget(t)
            fl.addWidget(v)
            setattr(self, f"pos_{attr}_val", v)
            pos_grid.addWidget(f, i // 4, i % 4)
        lay.addLayout(pos_grid)

        lay.addWidget(mk_sep())
        # 옵션 구간별 거래량
        lay.addWidget(mk_label("옵션 구간별 거래량 — 외인/개인/기관 분리 (ITM·ATM·OTM)", C['cyan'], 10, True))
        zone_lay = QHBoxLayout()
        for zone in ["ITM", "ATM", "OTM"]:
            zf = QFrame()
            zf.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;")
            zfl = QVBoxLayout(zf)
            zfl.setContentsMargins(6, 6, 6, 6)
            zfl.addWidget(mk_label(zone, C['text'], 11, True, Qt.AlignCenter))
            for inv, col in [("외인",C['blue']),("개인",C['red']),("기관",C['purple'])]:
                hr = QHBoxLayout()
                hr.addWidget(mk_label(inv, C['text2'], 9))
                b = mk_prog(col, 7)
                b.setValue(0)
                hr.addWidget(b, 2)
                vl = mk_label("—%", col, 9)
                setattr(self, f"oz_{zone}_{inv}", (b, vl))
                hr.addWidget(vl)
                zfl.addLayout(hr)
            zone_lay.addWidget(zf)
        lay.addLayout(zone_lay)

    def update_data(self, div):
        self.rt_put_bar.setValue(int(max(0, -div['rt_bias']) * 50))
        self.rt_call_bar.setValue(int(max(0, div['rt_bias']) * 50))
        self.fi_put_bar.setValue(int(max(0, -div['fi_bias']) * 50))
        self.fi_call_bar.setValue(int(max(0, div['fi_bias']) * 50))

        self.pos_rt_call_val.setText(f"{div.get('rt_call',0):,}")
        self.pos_rt_put_val.setText(f"{div.get('rt_put',0):,}")
        self.pos_rt_strd_val.setText(f"{div.get('rt_strd',0):,}")
        self.pos_fi_call_val.setText(f"{div.get('fi_call',0):+,}")
        self.pos_fi_put_val.setText(f"{div.get('fi_put',0):+,}")
        self.pos_fi_strangle_val.setText(f"{div.get('fi_strangle',0):+,}")
        contrarian = div.get('contrarian','중립')
        col = C['red'] if '하락' in contrarian else C['green'] if '상승' in contrarian else C['text2']
        self.pos_contrarian_val.setText(contrarian)
        self.pos_contrarian_val.setStyleSheet(f"color:{col};font-size:{S.f(13)}px;font-weight:bold;")

        score = div.get('div_score', 0)
        col2  = C['green'] if score > 10 else C['red'] if score < -10 else C['text2']
        self.pos_div_score_val.setText(f"{score:+.0f}")
        self.pos_div_score_val.setStyleSheet(f"color:{col2};font-size:{S.f(14)}px;font-weight:bold;")

        # 옵션 구간별 거래량 갱신
        # zones = {"ITM": {"외인": pct, "개인": pct, "기관": pct}, "ATM": {...}, "OTM": {...}}
        zones = div.get("zones", {})
        for zone in ["ITM", "ATM", "OTM"]:
            zd = zones.get(zone, {})
            for inv in ["외인", "개인", "기관"]:
                widget = getattr(self, f"oz_{zone}_{inv}", None)
                if widget is None:
                    continue
                b, vl = widget
                pct = zd.get(inv, 0)
                b.setValue(pct)
                vl.setText(f"{pct}%")


# ────────────────────────────────────────────────────────────
# 패널 3: 동적 피처 관리 (SHAP)
# ────────────────────────────────────────────────────────────
class FeaturePanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("채용 파라미터 TOP 6 — SHAP 기여도 실시간", C['purple'], 10, True))

        # 고정 CORE
        lay.addWidget(mk_label("▐ 고정 CORE 3개 — 절대 교체 불가", C['cyan'], 9, True))
        self.core_rows = []
        for i, name in enumerate(["CVD 다이버전스", "VWAP 위치", "OFI 불균형"]):
            row = QHBoxLayout()
            medal_colors = [C['orange'], "#888", "#639922"]
            rank = mk_badge(str(i+1), medal_colors[i], "#fff", 9)
            badge = mk_badge("CORE", C['cyan'], C['bg'], 8)
            nlab  = mk_label(name, C['text'], 10)
            bar   = mk_prog(C['cyan'], 10)
            bar.setValue(random.randint(55, 90))
            vlab  = mk_val_label("—%", C['cyan'], 10)
            slab  = mk_label("안정", C['green'], 9)
            row.addWidget(rank)
            row.addWidget(badge)
            row.addWidget(nlab, 2)
            row.addWidget(bar, 3)
            row.addWidget(vlab)
            row.addWidget(slab)
            lay.addLayout(row)
            self.core_rows.append((bar, vlab))

        lay.addWidget(mk_sep())

        # 동적 SHAP
        lay.addWidget(mk_label("▐ 동적 SHAP TOP 3 — 매일 심사", C['purple'], 9, True))
        # 쿨다운
        cdlay = QHBoxLayout()
        cdlay.addWidget(mk_label("쿨다운:", C['text2'], 9))
        self.cooldown_bar = mk_prog(C['orange'], 6)
        self.cooldown_bar.setValue(0)
        cdlay.addWidget(self.cooldown_bar, 3)
        self.cooldown_lbl = mk_label("없음", C['text2'], 9)
        cdlay.addWidget(self.cooldown_lbl)
        lay.addLayout(cdlay)

        self.dynamic_rows = []
        for i in range(3):
            row = QHBoxLayout()
            rank = mk_badge("—", C['bg3'], C['purple'], 9)
            badge = mk_badge("SHAP", C['bg3'], C['purple'], 8)
            nlab  = mk_label("——", C['text'], 10)
            bar   = mk_prog(C['purple'], 10)
            vlab  = mk_val_label("—%", C['purple'], 10)
            slab  = mk_label("——", C['text2'], 9)
            row.addWidget(rank)
            row.addWidget(badge)
            row.addWidget(nlab, 2)
            row.addWidget(bar, 3)
            row.addWidget(vlab)
            row.addWidget(slab)
            lay.addLayout(row)
            self.dynamic_rows.append((rank, nlab, bar, vlab, slab))

        lay.addWidget(mk_sep())

        # SHAP 전체 가로 차트 (간이)
        lay.addWidget(mk_label("전체 피처 순위 (SHAP 200분 누적)", C['blue'], 9, True))
        self.rank_labels = []
        all_params = [
            ("외인 콜순매수", C['green']),("CVD 다이버전스", C['cyan']),
            ("다이버전스",    C['orange']),("VWAP 위치",      C['cyan']),
            ("프로그램 비차익",C['purple']),("OFI 불균형",    C['cyan']),
        ]
        for name, col in all_params:
            r = QHBoxLayout()
            nl = mk_label(name[:8], C['text2'], 9)
            nl.setFixedWidth(70)
            b  = mk_prog(col, 8)
            b.setValue(random.randint(20, 85))
            vl = mk_val_label("—%", col, 9)
            vl.setFixedWidth(34)
            r.addWidget(nl)
            r.addWidget(b, 3)
            r.addWidget(vl)
            lay.addLayout(r)
            self.rank_labels.append((b, vl))

        lay.addWidget(mk_sep())
        # 교체 이력
        lay.addWidget(mk_label("교체 이력", C['text2'], 9, True))
        self.change_log = QTextEdit()
        self.change_log.setReadOnly(True)
        self.change_log.setFixedHeight(55)
        self.change_log.setStyleSheet(
            f"background:{C['bg']};color:{C['text2']};border:1px solid {C['border']};"
            f"font-size:{S.f(11)}px;font-family:Consolas;"
        )
        self.change_log.setText(
            "01-12  교체  베이시스 → 프로그램비차익  +1.4%  [성공]\n"
            "01-09  교체  PCR → 다이버전스지수        +2.1%  [성공]\n"
            "01-05  교체  원달러 → 외인콜순매수       +0.8%  [성공]"
        )
        lay.addWidget(self.change_log)

    def update_shap(self, core_vals, dynamic_items, rank_vals):
        for (bar, vlab), val in zip(self.core_rows, core_vals):
            bar.setValue(int(val*100))
            vlab.setText(f"{val*100:.1f}%")

        for i, (rank, nlab, bar, vlab, slab) in enumerate(self.dynamic_rows):
            if i < len(dynamic_items):
                d = dynamic_items[i]
                rank.setText(str(d.get('rank', i+1)))
                nlab.setText(d.get('name','——'))
                bar.setValue(int(d.get('shap',0)*100))
                vlab.setText(f"{d.get('shap',0)*100:.1f}%")
                slab.setText(d.get('status','유지'))

        for (b, vl), val in zip(self.rank_labels, rank_vals):
            b.setValue(int(val*100))
            vl.setText(f"{val*100:.0f}%")


# ────────────────────────────────────────────────────────────
# 패널 4: 청산 관리 패널
# ────────────────────────────────────────────────────────────
class ExitPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # 상단: 포지션 상태
        lay.addWidget(mk_label("포지션 청산 관리", C['red'], 10, True))
        top = QGridLayout()
        top.setSpacing(6)
        info = [
            ("진입가", "entry_price", "——"),
            ("현재가", "cur_price", "——"),
            ("미실현 손익", "unreal_pnl", "——"),
            ("보유 시간", "hold_time", "——"),
        ]
        for i, (lbl, attr, init) in enumerate(info):
            col = i % 2
            row_i = i // 2
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6, 3, 6, 3)
            fl.addWidget(mk_label(lbl, C['text2'], 9))
            vl = mk_val_label(init, C['text'], 13)
            setattr(self, attr, vl)
            fl.addWidget(vl)
            top.addWidget(f, row_i, col)
        lay.addLayout(top)

        lay.addWidget(mk_sep())

        # 가격 레벨
        lay.addWidget(mk_label("가격 구조 (손절 → 목표)", C['text2'], 9, True))
        levels = [
            ("하드 손절",    "hard_stop",  C['red'],    "●"),
            ("구조적 손절",  "struct_stop",C['red'],    "●"),
            ("트레일링 스톱","trail_stop", C['orange'], "●"),
            ("본전 (진입가)","breakeven",  C['text2'],  "●"),
            ("1차 목표 33%","target1",    C['green'],  "●"),
            ("2차 목표 33%","target2",    C['green'],  "●"),
            ("3차 목표 34%","target3",    "#085041",   "●"),
        ]
        for lbl, attr, col, dot in levels:
            r = QHBoxLayout()
            r.addWidget(mk_label(f"{dot} {lbl}", col, 9))
            vl = mk_val_label("——.——", col, 10)
            setattr(self, f"lv_{attr}", vl)
            r.addWidget(vl)
            lay.addLayout(r)

        lay.addWidget(mk_sep())

        # 청산 트리거 모니터
        lay.addWidget(mk_label("청산 트리거 모니터 (우선순위 감시)", C['orange'], 9, True))
        triggers = [
            ("1", "하드 스톱 초과",     "hard_trig"),
            ("1", "앙상블 반대 신호",   "signal_trig"),
            ("1", "CVD+VWAP 동시 역전", "cvd_trig"),
            ("2", "SHAP 피처 붕괴",     "shap_trig"),
            ("2", "옵션 플로우 역전",   "opt_trig"),
            ("2", "트레일링 스톱",      "trail_trig"),
            ("3", "1차 목표 도달",      "t1_trig"),
            ("3", "시간 청산 (15:10)", "time_trig"),
        ]
        for pri, name, attr in triggers:
            r = QHBoxLayout()
            pri_col = C['red'] if pri == "1" else C['orange'] if pri == "2" else C['blue']
            r.addWidget(mk_badge(pri, pri_col, "#fff", 8))
            r.addWidget(mk_label(name, C['text'], 9), 2)
            st = mk_badge("감시중", C['bg3'], C['text2'], 8)
            setattr(self, f"st_{attr}", st)
            r.addWidget(st)
            lay.addLayout(r)

        lay.addWidget(mk_sep())

        # 부분 청산 진행
        lay.addWidget(mk_label("부분 청산 (33% · 33% · 34%)", C['green'], 9, True))
        self.partial_bars = []
        for i, (lbl, pct) in enumerate([("1차", 33), ("2차", 33), ("3차", 34)]):
            r = QHBoxLayout()
            r.addWidget(mk_label(f"{lbl} ({pct}%)", C['text2'], 9))
            b = mk_prog(C['green'], 8)
            r.addWidget(b, 3)
            st = mk_label("대기", C['text2'], 9)
            r.addWidget(st)
            lay.addLayout(r)
            self.partial_bars.append((b, st))

        # 수동 청산 버튼
        btn_lay = QHBoxLayout()
        for label, pct, col in [("33% 청산", 33, C['green']),
                                  ("50% 청산", 50, C['orange']),
                                  ("전량 청산", 100, C['red'])]:
            btn = QPushButton(label)
            btn.setStyleSheet(
                f"QPushButton{{background:{C['bg3']};color:{col};"
                f"border:1px solid {col};border-radius:4px;padding:4px 8px;}}"
                f"QPushButton:hover{{background:{col};color:#000;}}"
            )
            btn_lay.addWidget(btn)
        lay.addLayout(btn_lay)

    def _reset_display(self):
        """포지션 FLAT 상태: 모든 필드를 '——' 로 초기화"""
        for w in (self.entry_price, self.cur_price, self.unreal_pnl, self.hold_time):
            w.setText("——")
        self.unreal_pnl.setStyleSheet(
            f"color:{C['text2']};font-size:{S.f(14)}px;font-weight:bold;"
        )
        for attr in ("hard_stop", "struct_stop", "trail_stop",
                     "breakeven", "target1", "target2", "target3"):
            getattr(self, f"lv_{attr}").setText("——.——")
        _badge_reset_ss = (
            f"background:{C['bg3']};color:{C['text2']};"
            f"border-radius:3px;font-size:{S.f(10)}px;padding:1px 5px;"
        )
        for attr in ("hard_trig", "signal_trig", "cvd_trig",
                     "shap_trig", "opt_trig", "trail_trig", "t1_trig", "time_trig"):
            b = getattr(self, f"st_{attr}")
            b.setText("감시중")
            b.setStyleSheet(_badge_reset_ss)
        for bar_w, lbl_w in self.partial_bars:
            bar_w.setValue(0)
            lbl_w.setText("대기")
            lbl_w.setStyleSheet(f"color:{C['text2']};font-size:{S.f(11)}px;")

    def update_data(self, pos_data):
        if not pos_data:
            self._reset_display()
            return

        status = pos_data.get('status', 'FLAT')
        if status == 'FLAT':
            self._reset_display()
            return

        entry  = pos_data.get('entry', 0.0)
        cur    = pos_data.get('current', entry)
        qty    = pos_data.get('qty', 0)
        atr    = pos_data.get('atr', 1.0)
        # stop = 현재 트레일링 스톱 (PositionTracker.stop_price)
        mult   = 1 if status == 'LONG' else -1
        stop   = pos_data.get('stop',  entry - mult * atr * 1.5)
        tp1    = pos_data.get('tp1',   entry + mult * atr * 1.0)
        tp2    = pos_data.get('tp2',   entry + mult * atr * 1.5)

        # 진입가 / 현재가
        self.entry_price.setText(f"{entry:.2f}")
        self.cur_price.setText(f"{cur:.2f}")

        pnl_pts = (cur - entry) * mult
        pnl_krw = pnl_pts * qty * FUTURES_PT_VALUE
        col = C['green'] if pnl_krw >= 0 else C['red']
        self.unreal_pnl.setText(f"{pnl_krw:+,.0f}원")
        self.unreal_pnl.setStyleSheet(f"color:{col};font-size:{S.f(14)}px;font-weight:bold;")

        # 보유 시간
        entry_time = pos_data.get('entry_time')
        if entry_time:
            mins = int((datetime.now() - entry_time).total_seconds() // 60)
            self.hold_time.setText(f"{mins}분")
        else:
            self.hold_time.setText("——")

        # 가격 구조 (실제 PositionTracker 값 기반)
        hard_stop   = entry - mult * atr * 1.5   # 최초 설정 하드스톱
        struct_stop = entry - mult * atr * 1.2   # 구조적 손절 (소프트)
        tp3         = entry + mult * atr * 2.5
        self.lv_hard_stop.setText(f"{hard_stop:.2f}")
        self.lv_struct_stop.setText(f"{struct_stop:.2f}")
        self.lv_trail_stop.setText(f"{stop:.2f}")   # 트레일링으로 이동된 현재 스톱
        self.lv_breakeven.setText(f"{entry:.2f}")
        self.lv_target1.setText(f"{tp1:.2f}")
        self.lv_target2.setText(f"{tp2:.2f}")
        self.lv_target3.setText(f"{tp3:.2f}")

        # 부분 청산 진행
        p1 = pos_data.get('partial1', False)
        p2 = pos_data.get('partial2', False)
        for i, (bar_w, lbl_w) in enumerate(self.partial_bars):
            done = (i == 0 and p1) or (i == 1 and p2)
            bar_w.setValue(100 if done else 0)
            lbl_w.setText("완료" if done else "대기")
            lbl_w.setStyleSheet(
                f"color:{C['green'] if done else C['text2']};font-size:{S.f(11)}px;"
            )


# ────────────────────────────────────────────────────────────
# 패널 5: 진입 관리 패널
# ────────────────────────────────────────────────────────────
class EntryPanel(QWidget):
    sig_reverse_entry_toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.current_mode = "hybrid"
        self._reverse_entry_enabled = False
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("진입 관리 패널 — 하이브리드 시스템", C['green'], 10, True))

        # 모드 선택
        mode_lay = QHBoxLayout()
        self.mode_btns = {}
        for mode, label in [("auto","자동 진입"), ("hybrid","하이브리드 (권장)"), ("manual","수동 진입")]:
            btn = QPushButton(label)
            col = C['green'] if mode == "hybrid" else C['text2']
            btn.setStyleSheet(
                f"QPushButton{{background:{C['bg2'] if mode=='hybrid' else C['bg3']};"
                f"color:{col};border:{'2' if mode=='hybrid' else '1'}px solid {col};"
                f"border-radius:4px;padding:5px 8px;font-size:{S.f(12)}px;}}"
            )
            btn.clicked.connect(lambda checked, m=mode: self._set_mode(m))
            self.mode_btns[mode] = btn
            mode_lay.addWidget(btn)
        self.reverse_btn = QPushButton("역방향 진입")
        self.reverse_btn.setCheckable(True)
        self.reverse_btn.setToolTip(
            "미륵이 자동 판단 신호를 반대로 실행합니다.\n"
            "수동 진입 버튼에는 적용되지 않습니다."
        )
        self.reverse_btn.toggled.connect(self._set_reverse_entry_enabled)
        self._sync_reverse_button_style()
        mode_lay.addWidget(self.reverse_btn)
        lay.addLayout(mode_lay)

        self.mode_desc = mk_label(
            "하이브리드: 신뢰도 70%+ + 외인 일치 → 자동 / 58~70% → 알림 후 수동",
            C['blue'], 9
        )
        lay.addWidget(self.mode_desc)
        lay.addWidget(mk_sep())

        # 앙상블 + 신뢰도
        info_lay = QGridLayout()
        info_lay.setSpacing(4)
        kv = [("원신호","signal","대기"),("실행 신호","final_signal","대기"),
              ("신뢰도","conf","대기"),("진입 등급","grade","대기"),
              ("산출 수량","qty","대기")]
        for i, (lbl, attr, init) in enumerate(kv):
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6,3,6,3)
            fl.addWidget(mk_label(lbl, C['text2'], 9))
            vl = mk_val_label(init, C['text'], 13)
            setattr(self, f"e_{attr}", vl)
            fl.addWidget(vl)
            info_lay.addWidget(f, i//2, i%2)
        lay.addLayout(info_lay)
        lay.addWidget(mk_sep())

        # 9개 체크리스트
        lay.addWidget(mk_label("진입 전 체크리스트 (Pre-flight 9개)", C['orange'], 9, True))
        checks = [
            ("앙상블 신호 방향","signal_chk"),
            ("신뢰도 ≥ 58%",   "conf_chk"),
            ("VWAP 위치 확인", "vwap_chk"),
            ("CVD 방향 일치",  "cvd_chk"),
            ("OFI 압력 확인",  "ofi_chk"),
            ("외인 방향 일치", "fi_chk"),
            ("직전 봉 확인",   "candle_chk"),
            ("시간 필터 통과", "time_chk"),
            ("리스크 한도 여유","risk_chk"),
        ]
        check_tooltips = {
            "signal_chk": (
                "목적: 시스템이 현재 LONG, SHORT, FLAT 중 어느 방향인지 먼저 확정합니다.\n"
                "의의: 이후 VWAP, CVD, OFI, 외인, 직전 봉 해석의 기준축이 되는 출발점입니다.\n"
                "진입 조건: 1·3·5·10·15·30분 호라이즌의 상승/하락 확률을 가중합한 결과가 "
                "LONG(+1) 또는 SHORT(-1)로 확정되어야 합니다. FLAT(0)이면 실패합니다."
            ),
            "conf_chk": (
                "목적: 예측 신호의 최소 품질을 확보해 애매한 진입을 걸러냅니다.\n"
                "의의: 낮은 신뢰도 구간에서 발생하는 헛진입을 초기에 차단하는 핵심 방어선입니다.\n"
                "진입 조건: 앙상블 신뢰도(confidence)가 현재 시간대·레짐 기준 최소 신뢰도 이상이어야 합니다."
            ),
            "vwap_chk": (
                "목적: 현재가가 기관 평균 체결 기준선(VWAP) 대비 어느 편에 있는지 확인합니다.\n"
                "의의: 롱은 평균보다 강해야 하고 숏은 평균보다 약해야 한다는 추세 확인 필터입니다.\n"
                "진입 조건: LONG이면 현재가가 VWAP 위(vwap_position > 0), SHORT이면 VWAP 아래(vwap_position < 0)여야 합니다."
            ),
            "cvd_chk": (
                "목적: 누적 체결량 델타(CVD)가 진입 방향과 같은지 확인합니다.\n"
                "의의: 가격만 움직이고 실제 체결 주도권이 반대인 허수 돌파를 걸러냅니다.\n"
                "진입 조건: LONG이면 CVD 방향이 상승(cvd_direction >= 0), SHORT이면 하락(cvd_direction <= 0)이어야 합니다."
            ),
            "ofi_chk": (
                "목적: 호가창의 매수/매도 압력 불균형(OFI)이 어느 쪽인지 확인합니다.\n"
                "의의: 체결 결과인 CVD보다 한발 앞선 주문 압력을 확인하는 선행 필터입니다.\n"
                "진입 조건: LONG이면 OFI 압력이 양수 또는 중립(ofi_pressure >= 0), SHORT이면 음수 또는 중립(ofi_pressure <= 0)이어야 합니다."
            ),
            "fi_chk": (
                "목적: 외국인 옵션 흐름이 진입 방향과 같은지 확인합니다.\n"
                "의의: 단기 방향성의 강한 확인 신호이며 자동 진입 판단에도 중요한 보조축입니다.\n"
                "진입 조건: LONG이면 외인 콜 순매수가 양수이거나 콜 순매수가 풋 순매수보다 커야 합니다. "
                "SHORT이면 외인 풋 순매수가 양수이거나 풋 순매수가 콜 순매수보다 커야 합니다."
            ),
            "candle_chk": (
                "목적: 직전 1개 봉이 진입 방향과 같은 마감인지 확인합니다.\n"
                "의의: 막 역행하는 순간의 진입을 줄이고 최소한의 단기 모멘텀 동조를 봅니다.\n"
                "진입 조건: LONG이면 직전 봉이 양봉, SHORT이면 직전 봉이 음봉이어야 합니다."
            ),
            "time_chk": (
                "목적: 신규 진입이 허용되는 시간대인지 확인합니다.\n"
                "의의: 신호가 좋아도 시간대가 나쁘면 성과가 급격히 저하될 수 있어 시간 자체를 필터링합니다.\n"
                "진입 조건: 현재 time_zone이 EXIT_ONLY나 OTHER가 아니어야 합니다."
            ),
            "risk_chk": (
                "목적: 당일 손실이 커진 상태에서의 추가 진입을 차단합니다.\n"
                "의의: 전략 판단과 별개로 계좌를 보호하는 최종 브레이크 역할입니다.\n"
                "진입 조건: 일일 손실률(daily_loss_pct)이 2% 미만이어야 합니다."
            ),
        }
        self.check_labels = {}
        for i, (name, attr) in enumerate(checks):
            r = QHBoxLayout()
            icon = mk_badge("—", C['bg3'], C['text2'], 10)
            icon.setFixedWidth(22)
            nl   = mk_label(name, C['text'], 11)
            vl   = mk_val_label("——", C['text2'], 11)
            tooltip = check_tooltips.get(attr)
            if tooltip:
                nl.setToolTip(tooltip)
            r.addWidget(icon)
            r.addWidget(nl, 2)
            r.addWidget(vl)
            self.check_labels[attr] = (icon, vl)
            lay.addLayout(r)

        lay.addWidget(mk_sep())

        # 진입 버튼
        lay.addWidget(mk_label("진입 실행", C['text2'], 11, True))
        self.entry_alert = mk_label("신호 대기 중...", C['text2'], 12)
        self.entry_alert.setStyleSheet(
            f"background:{C['bg3']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:5px;color:{C['text2']};font-size:{S.f(12)}px;"
        )
        lay.addWidget(self.entry_alert)

        btn_lay = QHBoxLayout()
        self.buy_btn  = QPushButton("▲ 매수 진입 (Long)")
        self.sell_btn = QPushButton("▼ 매도 진입 (Short)")
        self.skip_btn = QPushButton("신호 스킵")

        self.buy_btn.setStyleSheet(
            f"QPushButton{{background:#0D2818;color:{C['green']};"
            f"border:1px solid {C['green']};border-radius:4px;padding:7px;"
            f"font-size:{S.f(13)}px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{C['green']};color:#000;}}"
        )
        self.sell_btn.setStyleSheet(
            f"QPushButton{{background:#2D0D0D;color:{C['red']};"
            f"border:1px solid {C['red']};border-radius:4px;padding:7px;"
            f"font-size:{S.f(13)}px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{C['red']};color:#000;}}"
        )
        self.skip_btn.setStyleSheet(
            f"QPushButton{{background:{C['bg3']};color:{C['text2']};"
            f"border:1px solid {C['border']};border-radius:4px;padding:7px;}}"
        )
        btn_lay.addWidget(self.buy_btn, 2)
        btn_lay.addWidget(self.sell_btn, 2)
        btn_lay.addWidget(self.skip_btn, 1)
        lay.addLayout(btn_lay)

        # 당일 통계
        lay.addWidget(mk_sep())
        lay.addWidget(mk_label("당일 진입 통계", C['text2'], 11, True))
        self.stat_label = mk_label("진입 0회 | 자동 0 | 수동 0 | 승률 —% | 손익 ——pt", C['text2'], 11)
        lay.addWidget(self.stat_label)

    def update_stats(self, trades: int, wins: int, pnl_pts: float):
        """당일 진입 통계 라벨 갱신"""
        losses   = trades - wins
        win_rate = f"{wins/max(trades,1)*100:.0f}%" if trades > 0 else "—%"
        pnl_col  = C['green'] if pnl_pts >= 0 else C['red']
        pnl_str = f"{pnl_pts:+.2f}pt" if trades > 0 else "——pt"
        self.stat_label.setText(
            f"진입 {trades}회 | 승 {wins} 패 {losses} | 승률 {win_rate} | 손익 {pnl_str}"
        )
        self.stat_label.setStyleSheet(f"color:{pnl_col};font-size:{S.f(11)}px;")

    def _sync_reverse_button_style(self):
        col = C['orange'] if self._reverse_entry_enabled else C['text2']
        bg = "#2B1A07" if self._reverse_entry_enabled else C['bg3']
        self.reverse_btn.setStyleSheet(
            f"QPushButton{{background:{bg};color:{col};border:"
            f"{'2px' if self._reverse_entry_enabled else '1px'} solid {col};"
            f"border-radius:4px;padding:5px 8px;font-size:{S.f(12)}px;font-weight:bold;}}"
        )
        self.reverse_btn.setText(
            "역방향 진입 ON" if self._reverse_entry_enabled else "역방향 진입"
        )

    def _set_mode(self, mode):
        self.current_mode = mode
        for m, btn in self.mode_btns.items():
            col = C['green'] if m == mode else C['text2']
            bw  = "2px" if m == mode else "1px"
            btn.setStyleSheet(
                f"QPushButton{{background:{C['bg2'] if m==mode else C['bg3']};"
                f"color:{col};border:{bw} solid {col};"
                f"border-radius:4px;padding:5px 8px;font-size:{S.f(12)}px;}}"
            )

    def _set_reverse_entry_enabled(self, enabled: bool):
        self._reverse_entry_enabled = bool(enabled)
        self._sync_reverse_button_style()
        self.sig_reverse_entry_toggled.emit(self._reverse_entry_enabled)

    def set_reverse_entry_enabled(self, enabled: bool, emit_signal: bool = False):
        enabled = bool(enabled)
        self._reverse_entry_enabled = enabled
        self.reverse_btn.blockSignals(True)
        try:
            self.reverse_btn.setChecked(enabled)
        finally:
            self.reverse_btn.blockSignals(False)
        self._sync_reverse_button_style()
        if emit_signal:
            self.sig_reverse_entry_toggled.emit(self._reverse_entry_enabled)

    def is_reverse_entry_enabled(self) -> bool:
        return self._reverse_entry_enabled

    def get_entry_mode(self) -> str:
        return self.current_mode

    def update_data(self, signal, conf, grade, checks, qty=0, final_signal=None,
                    reverse_enabled=False):
        final_signal = final_signal or signal
        col = C['green'] if signal == "매수" else C['red'] if signal == "매도" else C['text2']
        final_col = C['green'] if final_signal == "매수" else C['red'] if final_signal == "매도" else C['text2']
        self.e_signal.setText(signal)
        self.e_signal.setStyleSheet(f"color:{col};font-size:{S.f(14)}px;font-weight:bold;")
        self.e_final_signal.setText(final_signal)
        self.e_final_signal.setStyleSheet(f"color:{final_col};font-size:{S.f(14)}px;font-weight:bold;")
        self.e_conf.setText(f"{conf*100:.1f}%")
        self.e_conf.setStyleSheet(
            f"color:{C['green'] if conf>=0.7 else C['orange'] if conf>=0.58 else C['red']};"
            f"font-size:{S.f(14)}px;font-weight:bold;"
        )

        grade_colors = {"A": C['cyan'], "B": C['blue'], "C": C['orange'], "X": C['red']}
        self.e_grade.setText(f"{grade}급")
        self.e_grade.setStyleSheet(f"color:{grade_colors.get(grade,C['text'])};"
                                    f"font-size:{S.f(14)}px;font-weight:bold;")

        # 산출 수량
        if qty > 0:
            self.e_qty.setText(f"{qty}계약")
            self.e_qty.setStyleSheet(f"color:{C['cyan']};font-size:{S.f(14)}px;font-weight:bold;")
        else:
            self.e_qty.setText("——")
            self.e_qty.setStyleSheet(f"color:{C['text2']};font-size:{S.f(14)}px;font-weight:bold;")

        # 체크리스트 아이콘
        # checks={} → 미평가(—), True → V(green), False → X(red)
        for attr, (icon, vl) in self.check_labels.items():
            val = checks.get(attr, None)
            if val is None:
                icon.setText("—")
                icon.setStyleSheet(
                    f"background:{C['bg3']};color:{C['text2']};"
                    f"border-radius:3px;font-size:{S.f(10)}px;font-weight:bold;padding:1px 4px;"
                )
            elif val:
                icon.setText("V")
                icon.setStyleSheet(
                    f"background:{C['green']};color:#fff;"
                    f"border-radius:3px;font-size:{S.f(10)}px;font-weight:bold;padding:1px 4px;"
                )
            else:
                icon.setText("X")
                icon.setStyleSheet(
                    f"background:{C['red']};color:#fff;"
                    f"border-radius:3px;font-size:{S.f(10)}px;font-weight:bold;padding:1px 4px;"
                )

        if signal == "매수":
            self.entry_alert.setStyleSheet(
                f"background:#0D2818;border:1px solid {C['green']};"
                f"border-radius:4px;padding:5px;color:{C['green']};font-size:{S.f(12)}px;"
            )
            reverse_tag = " | 역방향진입=ON" if reverse_enabled else ""
            self.entry_alert.setText(
                f"▲ 원신호: {signal} / 실행신호: {final_signal} | {grade}급 — {conf*100:.1f}% 신뢰도{reverse_tag}"
            )
        elif signal == "매도":
            self.entry_alert.setStyleSheet(
                f"background:#2D0D0D;border:1px solid {C['red']};"
                f"border-radius:4px;padding:5px;color:{C['red']};font-size:{S.f(12)}px;"
            )
            reverse_tag = " | 역방향진입=ON" if reverse_enabled else ""
            self.entry_alert.setText(
                f"▼ 원신호: {signal} / 실행신호: {final_signal} | {grade}급 — {conf*100:.1f}% 신뢰도{reverse_tag}"
            )
        else:
            self.entry_alert.setStyleSheet(
                f"background:{C['bg3']};border:1px solid {C['border']};"
                f"border-radius:4px;padding:5px;color:{C['text2']};font-size:{S.f(12)}px;"
            )
            self.entry_alert.setText("— 관망 | 신호 대기 중")


# ────────────────────────────────────────────────────────────
# 패널 6: 🧠 자가학습 모니터
# ────────────────────────────────────────────────────────────
class LearningPanel(QWidget):
    """SGD 온라인 / GBM 배치 / 예측 버퍼 자가학습 현황 통합 뷰"""

    HORIZONS  = ["1m", "3m", "5m", "10m", "15m", "30m"]
    H_LABELS  = ["1분", "3분", "5분", "10분", "15분", "30분"]
    RAW_NEEDED = 5_000

    def __init__(self):
        super().__init__()
        self._prev_accs = {hz: 0.5 for hz in self.HORIZONS}
        self._build()

    @staticmethod
    def _acc_col(acc: float) -> str:
        if acc >= 0.62:  return C['green']
        if acc >= 0.55:  return C['cyan']
        if acc >= 0.48:  return C['orange']
        return C['red']

    def _make_report_tab(self, title: str, accent: str):
        frame = QFrame()
        frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(S.p(10), S.p(8), S.p(10), S.p(8))
        lay.setSpacing(S.p(4))
        lay.addWidget(mk_label(title, accent, 9, True))
        value = mk_val_label("--", accent, 18, True)
        detail = mk_label("--", C['text2'], 8)
        spark = mk_label("--", accent, 8)
        lay.addWidget(value)
        lay.addWidget(detail)
        lay.addWidget(spark)
        lay.addStretch()
        return frame, value, detail, spark

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(S.p(8), S.p(8), S.p(8), S.p(8))
        root.setSpacing(S.p(8))

        # ── 타이틀 + 최근 이벤트 ─────────────────────────────
        hdr = QHBoxLayout()
        hdr.addWidget(mk_label("🧠  자가학습 모니터", C['purple'], 11, True))
        hdr.addStretch()
        self._lbl_last_ev = mk_label("최근 이벤트 없음", C['text2'], 8)
        hdr.addWidget(self._lbl_last_ev)
        root.addLayout(hdr)

        # ── 요약 카드 4개 ─────────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(S.p(6))
        summary_defs = [
            ("오늘 검증 건수",     "0",       C['cyan'],   "verified"),
            ("SGD 50분 정확도",   "——",      C['green'],  "sgd_acc"),
            ("GBM 마지막 재학습", "미실행",   C['blue'],   "retrain"),
            ("데이터 축적",        "0%",      C['yellow'], "raw_pct"),
        ]
        self._sum_lbls = {}
        for title, init_val, col, key in summary_defs:
            f = QFrame()
            f.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {col}44;"
                f"border-top:2px solid {col};border-radius:5px;}}"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(S.p(8), S.p(5), S.p(8), S.p(6))
            fl.setSpacing(S.p(2))
            fl.addWidget(mk_label(title, col, 8, align=Qt.AlignCenter))
            sz = 12 if key == "retrain" else 18
            v = mk_val_label(init_val, col, sz, True, Qt.AlignCenter)
            fl.addWidget(v)
            self._sum_lbls[key] = v
            top_row.addWidget(f)
        root.addLayout(top_row)
        root.addWidget(mk_sep())

        self._report_tabs = QTabWidget()
        self._report_tabs.setStyleSheet(
            f"QTabBar::tab{{background:{C['bg2']};color:{C['text2']};"
            f"padding:{S.p(4)}px {S.p(10)}px;font-size:{S.f(8)}px;}}"
            f"QTabBar::tab:selected{{background:{C['bg3']};color:{C['yellow']};"
            f"border-bottom:2px solid {C['yellow']};}}"
        )
        tab_tooltips = {
            "ab": (
                "Baseline ensemble(A)와 microstructure-enhanced ensemble(B)를 같은 구간에서 비교합니다.\n"
                "표시값은 enhanced - baseline 총손익 차이이며, detail에는 정확도 차이와 변경 건수가 표시됩니다."
            ),
            "calibration": (
                "모델 confidence가 실제 적중률과 얼마나 일치하는지 보는 탭입니다.\n"
                "ECE는 confidence와 실제 정확도의 평균 차이이며, 0에 가까울수록 좋습니다."
            ),
            "meta": (
                "방향 예측 위에 take / reduce / skip을 결정하는 2차 필터 성능입니다.\n"
                "표시값은 현재 best grid의 match rate이며, labels는 누적 meta 표본 수입니다."
            ),
            "rollout": (
                "업그레이드 시스템을 실전에 어느 단계까지 올릴 수 있는지 보여주는 운영 승인 상태입니다.\n"
                "shadow -> alert_only -> small_size -> full 순서로 승격하며, meta 표본과 calibration 상태를 함께 봅니다."
            ),
        }
        self._report_widgets = {}
        for key, title, accent in [
            ("ab", "A/B", C['cyan']),
            ("calibration", "Calibration", C['blue']),
            ("meta", "Meta Gate", C['purple']),
            ("rollout", "Rollout", C['orange']),
        ]:
            frame, value, detail, spark = self._make_report_tab(title, accent)
            self._report_widgets[key] = {"value": value, "detail": detail, "spark": spark}
            idx = self._report_tabs.addTab(frame, title)
            self._report_tabs.tabBar().setTabToolTip(idx, tab_tooltips.get(key, ""))
            frame.setToolTip(tab_tooltips.get(key, ""))
            value.setToolTip(tab_tooltips.get(key, ""))
            detail.setToolTip(tab_tooltips.get(key, ""))
            spark.setToolTip(tab_tooltips.get(key, ""))
        root.addWidget(self._report_tabs)
        root.addWidget(mk_sep())

        # ── SGD 온라인 학습 섹션 ──────────────────────────────
        root.addWidget(mk_label(
            "⚡  SGD 온라인 자가학습  ·  매 검증건 즉시 partial_fit",
            C['purple'], 9, True,
        ))

        # GBM ←→ SGD 블렌딩 비율 바
        bf = QFrame()
        bf.setStyleSheet(
            f"background:{C['bg3']};border:1px solid {C['border']};border-radius:5px;"
        )
        bl = QHBoxLayout(bf)
        bl.setContentsMargins(S.p(10), S.p(7), S.p(10), S.p(7))
        bl.setSpacing(S.p(10))
        bl.addWidget(mk_label("GBM", C['blue'], 9, True))
        self._blend_bar = QProgressBar()
        self._blend_bar.setRange(0, 100)
        self._blend_bar.setValue(70)
        self._blend_bar.setTextVisible(False)
        self._blend_bar.setFixedHeight(S.p(14))
        self._blend_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg']};border:none;border-radius:4px;}}"
            f"QProgressBar::chunk{{background:qlineargradient("
            f"x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {C['blue']},stop:0.5 #7057F5,stop:1 {C['purple']});}}"
        )
        bl.addWidget(self._blend_bar, 1)
        self._lbl_blend = mk_label(
            "GBM 70%    SGD 30%", C['text2'], 9, align=Qt.AlignCenter,
        )
        bl.addWidget(self._lbl_blend)
        bl.addWidget(mk_label("SGD", C['purple'], 9, True))
        root.addWidget(bf)

        # 호라이즌 카드 2행 × 3열
        grid = QGridLayout()
        grid.setSpacing(S.p(5))
        self._hz_cards = {}
        for i, (hz, hlbl) in enumerate(zip(self.HORIZONS, self.H_LABELS)):
            f = QFrame()
            f.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
                f"border-radius:6px;}}"
            )
            vl = QVBoxLayout(f)
            vl.setContentsMargins(S.p(8), S.p(6), S.p(8), S.p(7))
            vl.setSpacing(S.p(3))
            hr = QHBoxLayout()
            hr.addWidget(mk_label(hlbl, C['text'], 9, True))
            hr.addStretch()
            badge = mk_badge("미학습", C['bg3'], C['text2'], 7)
            hr.addWidget(badge)
            vl.addLayout(hr)
            acc_lbl = mk_val_label("—.—%", C['text2'], 16, True, Qt.AlignCenter)
            vl.addWidget(acc_lbl)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(S.p(5))
            bar.setStyleSheet(
                f"QProgressBar{{background:{C['bg']};border:none;border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{C['text2']};}}"
            )
            vl.addWidget(bar)
            cnt_lbl = mk_label("학습 0건", C['text2'], 8, align=Qt.AlignCenter)
            vl.addWidget(cnt_lbl)
            self._hz_cards[hz] = (acc_lbl, cnt_lbl, badge, bar)
            grid.addWidget(f, i // 3, i % 3)
        root.addLayout(grid)
        root.addWidget(mk_sep())

        # ── GBM 배치 재학습 섹션 ──────────────────────────────
        root.addWidget(mk_label(
            "🔄  GBM 배치 재학습  ·  주간 월요일 08:50  /  일일 15:40 마감",
            C['blue'], 9, True,
        ))
        gbm_row = QHBoxLayout()
        gbm_row.setSpacing(S.p(6))
        for title, init, col, attr in [
            ("마지막 재학습",  "미실행",   C['blue'],   "_gbm_last"),
            ("재학습 횟수",    "0회",      C['cyan'],   "_gbm_cnt"),
            ("다음 스케줄",    "월 08:50", C['text2'],  "_gbm_next"),
        ]:
            f = QFrame()
            f.setStyleSheet(
                f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;"
            )
            vl = QVBoxLayout(f)
            vl.setContentsMargins(S.p(8), S.p(5), S.p(8), S.p(6))
            vl.setSpacing(S.p(2))
            vl.addWidget(mk_label(title, C['text2'], 8, align=Qt.AlignCenter))
            lbl = mk_val_label(init, col, 13, True, Qt.AlignCenter)
            vl.addWidget(lbl)
            setattr(self, attr, lbl)
            gbm_row.addWidget(f)
        root.addLayout(gbm_row)

        # 데이터 축적 진행 바
        rawf = QFrame()
        rawf.setStyleSheet(
            f"background:{C['bg3']};border:1px solid {C['border']};border-radius:5px;"
        )
        rawl = QHBoxLayout(rawf)
        rawl.setContentsMargins(S.p(10), S.p(7), S.p(10), S.p(7))
        rawl.setSpacing(S.p(10))
        rawl.addWidget(mk_label("학습 데이터 축적", C['yellow'], 9, True))
        self._raw_bar = QProgressBar()
        self._raw_bar.setRange(0, self.RAW_NEEDED)
        self._raw_bar.setValue(0)
        self._raw_bar.setTextVisible(False)
        self._raw_bar.setFixedHeight(S.p(14))
        self._raw_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg']};border:none;border-radius:4px;}}"
            f"QProgressBar::chunk{{background:qlineargradient("
            f"x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {C['yellow']},stop:1 {C['green']});}}"
        )
        rawl.addWidget(self._raw_bar, 1)
        self._lbl_raw_cnt = mk_label(f"0 / {self.RAW_NEEDED:,}", C['text2'], 9)
        rawl.addWidget(self._lbl_raw_cnt)
        root.addWidget(rawf)
        root.addWidget(mk_sep())

        # ── 예측 버퍼 정확도 테이블 ──────────────────────────
        root.addWidget(mk_label(
            "📊  호라이즌별 예측 정확도  ·  최근 50회 검증 기준",
            C['cyan'], 9, True,
        ))
        acc_frame = QFrame()
        acc_frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        acc_grid = QGridLayout(acc_frame)
        acc_grid.setContentsMargins(S.p(8), S.p(6), S.p(8), S.p(6))
        acc_grid.setSpacing(S.p(5))
        for j, htxt in enumerate(["호라이즌", "정확도", "게이지", "추세"]):
            acc_grid.addWidget(mk_label(htxt, C['text2'], 8, True), 0, j)
        acc_grid.setColumnStretch(2, 1)
        self._buf_rows = {}
        for i, (hz, hlbl) in enumerate(zip(self.HORIZONS, self.H_LABELS)):
            row = i + 1
            acc_grid.addWidget(mk_badge(hlbl, C['bg3'], C['text'], 8), row, 0)
            acc_lbl = mk_val_label("——", C['text2'], 11, True)
            acc_grid.addWidget(acc_lbl, row, 1)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(S.p(7))
            bar.setStyleSheet(
                f"QProgressBar{{background:{C['bg']};border:none;border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{C['text2']};}}"
            )
            acc_grid.addWidget(bar, row, 2)
            trend = mk_label("━", C['text2'], 12)
            trend.setAlignment(Qt.AlignCenter)
            acc_grid.addWidget(trend, row, 3)
            self._buf_rows[hz] = (acc_lbl, bar, trend)
        root.addWidget(acc_frame)
        root.addStretch()

    # ── 업데이트 ──────────────────────────────────────────────
    def update_data(self, data: dict):
        import datetime as _dt

        report_history = data.get("report_history") or []
        ab_metrics = data.get("ab_metrics") or {}
        calibration_metrics = data.get("calibration_metrics") or {}
        meta_metrics = data.get("meta_metrics") or {}
        rollout_metrics = data.get("rollout_metrics") or {}

        # 요약 카드
        self._sum_lbls["verified"].setText(str(data.get("verified_today", 0)))

        sgd_acc = float(data.get("sgd_accuracy_50m", 0.5))
        col_sgd = self._acc_col(sgd_acc)
        self._sum_lbls["sgd_acc"].setText(f"{sgd_acc:.1%}")
        self._sum_lbls["sgd_acc"].setStyleSheet(
            f"color:{col_sgd};font-size:{S.f(18)}px;font-weight:bold;"
        )

        retrain_ts = str(data.get("gbm_last_retrain", "——") or "——")
        rt_disp = "미실행"
        if retrain_ts not in ("——", "없음", ""):
            try:
                rt_disp = _dt.datetime.strptime(
                    retrain_ts, "%Y-%m-%d %H:%M"
                ).strftime("%m/%d %H:%M")
            except Exception:
                rt_disp = retrain_ts[:11]
        self._sum_lbls["retrain"].setText(rt_disp)

        raw_cnt = max(int(data.get("raw_candles_count", 0)), 0)
        raw_pct = min(raw_cnt / self.RAW_NEEDED, 1.0)
        col_raw = C['green'] if raw_pct >= 1.0 else C['yellow']
        self._sum_lbls["raw_pct"].setText(f"{raw_pct:.0%}")
        self._sum_lbls["raw_pct"].setStyleSheet(
            f"color:{col_raw};font-size:{S.f(18)}px;font-weight:bold;"
        )

        # SGD 블렌딩 비율
        gbm_w = max(0.0, min(1.0, float(data.get("gbm_weight", 0.70))))
        sgd_w = 1.0 - gbm_w
        self._blend_bar.setValue(int(gbm_w * 100))
        self._lbl_blend.setText(f"GBM {gbm_w:.0%}    SGD {sgd_w:.0%}")

        # SGD 호라이즌 카드
        fitted = data.get("sgd_fitted", {})
        h_accs = data.get("horizon_accuracy", {})
        h_cnts = data.get("sgd_sample_counts", {})
        for hz, (acc_lbl, cnt_lbl, badge, bar) in self._hz_cards.items():
            is_fit = fitted.get(hz, False)
            acc = float(h_accs.get(hz, 0.5))
            cnt = int(h_cnts.get(hz, 0))
            col = self._acc_col(acc) if is_fit else C['text2']
            acc_lbl.setText(f"{acc:.1%}" if is_fit else "—.—%")
            acc_lbl.setStyleSheet(
                f"color:{col};font-size:{S.f(16)}px;font-weight:bold;"
            )
            bar.setValue(int(acc * 100) if is_fit else 0)
            bar.setStyleSheet(
                f"QProgressBar{{background:{C['bg']};border:none;border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{col};}}"
            )
            cnt_lbl.setText(f"학습 {cnt}건")
            cnt_lbl.setStyleSheet(f"color:{C['text2']};font-size:{S.f(8)}px;")
            if is_fit:
                badge.setText("학습됨")
                badge.setStyleSheet(
                    f"background:{col}33;color:{col};border-radius:3px;"
                    f"font-size:{S.f(7)}px;font-weight:bold;padding:1px 5px;"
                )
            else:
                badge.setText("미학습")
                badge.setStyleSheet(
                    f"background:{C['bg3']};color:{C['text2']};border-radius:3px;"
                    f"font-size:{S.f(7)}px;padding:1px 5px;"
                )

        # GBM 재학습 상태
        self._gbm_last.setText(rt_disp)
        self._gbm_cnt.setText(f"{int(data.get('gbm_retrain_count', 0))}회")
        now = _dt.datetime.now()
        days_to_mon = (7 - now.weekday()) % 7
        if days_to_mon == 0 and now.hour >= 9:
            days_to_mon = 7
        self._gbm_next.setText(
            (now + _dt.timedelta(days=days_to_mon)).strftime("%m/%d") + " 08:50"
        )

        # 데이터 축적 바
        self._raw_bar.setValue(min(raw_cnt, self.RAW_NEEDED))
        col_rb = C['green'] if raw_cnt >= self.RAW_NEEDED else C['yellow']
        self._lbl_raw_cnt.setText(f"{raw_cnt:,} / {self.RAW_NEEDED:,} 행")
        self._lbl_raw_cnt.setStyleSheet(f"color:{col_rb};font-size:{S.f(9)}px;")

        # 예측 버퍼 정확도 테이블
        buf_accs = data.get("buffer_accuracy", {})
        for hz, (acc_lbl, bar, trend) in self._buf_rows.items():
            acc  = float(buf_accs.get(hz, 0.5))
            prev = self._prev_accs.get(hz, 0.5)
            col  = self._acc_col(acc)
            acc_lbl.setText(f"{acc:.1%}")
            acc_lbl.setStyleSheet(
                f"color:{col};font-size:{S.f(11)}px;font-weight:bold;"
            )
            bar.setValue(int(acc * 100))
            bar.setStyleSheet(
                f"QProgressBar{{background:{C['bg']};border:none;border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{col};}}"
            )
            if acc > prev + 0.005:
                trend.setText("▲")
                trend.setStyleSheet(f"color:{C['green']};font-size:{S.f(12)}px;")
            elif acc < prev - 0.005:
                trend.setText("▼")
                trend.setStyleSheet(f"color:{C['red']};font-size:{S.f(12)}px;")
            else:
                trend.setText("━")
                trend.setStyleSheet(f"color:{C['text2']};font-size:{S.f(12)}px;")
            self._prev_accs[hz] = acc

        ev = str(data.get("last_event", "") or "")
        if ev:
            self._lbl_last_ev.setText(ev[-70:] if len(ev) > 70 else ev)


# ────────────────────────────────────────────────────────────
# 패널 7: 🎯 학습 효과 검증기
# ────────────────────────────────────────────────────────────
class EfficacyPanel(QWidget):
    """자가학습이 실제로 돈을 버는가? — 4-section 효과 검증 패널

    Section 1: 신뢰도 캘리브레이션   — 70% 예측이 진짜 70% 적중하는가?
    Section 2: 등급별 매매 성과       — 등급 A가 등급 C보다 실제로 수익?
    Section 3: 학습 성장 곡선         — 시간이 갈수록 정확도가 올라가는가?
    Section 4: 레짐별 성과            — 어떤 시장 환경이 가장 효과적?
    """

    _SPARK_BLOCKS = "▁▂▃▄▅▆▇█"
    _GRADE_ORDER  = ["A", "B", "C", "X", "?"]
    _REGIME_ORDER = ["RISK_ON", "NEUTRAL", "RISK_OFF"]

    def __init__(self):
        super().__init__()
        self._build()

    def _make_report_tab(self, title: str, accent: str):
        frame = QFrame()
        frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(S.p(10), S.p(8), S.p(10), S.p(8))
        lay.setSpacing(S.p(4))
        lay.addWidget(mk_label(title, accent, 9, True))
        value = mk_val_label("--", accent, 18, True)
        detail = mk_label("--", C['text2'], 8)
        spark = mk_label("?" * 16, accent, 8)
        spark.setFont(__import__('PyQt5.QtGui', fromlist=['QFont']).QFont("Consolas", S.f(8)))
        lay.addWidget(value)
        lay.addWidget(detail)
        lay.addWidget(spark)
        lay.addStretch()
        return frame, value, detail, spark

    def _history_series(self, history: list, key: str) -> list:
        vals = []
        for item in history[-24:]:
            try:
                if key not in item or item[key] is None:
                    continue
                vals.append(float(item[key]))
            except Exception:
                continue
        return vals

    # ── helper: confidence quality badge ─────────────────────
    @staticmethod
    def _calib_badge(conf_f: float, acc_f: float) -> tuple:
        """(text, color) — 신뢰도 대비 실제 정확도 품질"""
        gap = acc_f - conf_f
        if abs(gap) <= 0.04:
            return "✓ 우수", C['green']
        if gap > 0.04:
            return "▲ 과소신뢰", C['cyan']
        if gap < -0.08:
            return "▼ 과신", C['red']
        return "≈ 양호", C['orange']

    @staticmethod
    def _win_col(wr: float) -> str:
        if wr >= 0.60: return C['green']
        if wr >= 0.53: return C['cyan']
        if wr >= 0.45: return C['orange']
        return C['red']

    @staticmethod
    def _pnl_col(pnl: float) -> str:
        return C['green'] if pnl > 0 else (C['red'] if pnl < 0 else C['text2'])

    @staticmethod
    def _spark(values, width: int = 18) -> str:
        """0~1 float 리스트 → 유니코드 스파크라인 (고정 width)"""
        if not values:
            return "─" * width
        blk = "▁▂▃▄▅▆▇█"
        mn, mx = min(values), max(values)
        span = mx - mn if mx != mn else 1.0
        chars = [blk[min(7, int((v - mn) / span * 7.99))] for v in values]
        # 다운샘플 or 패딩
        while len(chars) > width:
            step = len(chars) / width
            chars = [chars[int(i * step)] for i in range(width)]
        while len(chars) < width:
            chars.append("─")
        return "".join(chars)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(S.p(8), S.p(8), S.p(8), S.p(8))
        root.setSpacing(S.p(8))

        # ── 헤더 ─────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.addWidget(mk_label("🎯  학습 효과 검증기", C['yellow'], 11, True))
        hdr.addStretch()
        self._lbl_updated = mk_label("마지막 갱신: ——", C['text2'], 8)
        hdr.addWidget(self._lbl_updated)
        root.addLayout(hdr)

        # ── 핵심 지표 배지 4개 ───────────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(S.p(6))
        kpi_defs = [
            ("전체 승률",      "——",  C['cyan'],   "_kpi_total_wr"),
            ("A등급 승률",     "——",  C['green'],  "_kpi_a_wr"),
            ("캘리브레이션",   "——",  C['blue'],   "_kpi_calib"),
            ("학습 효과 Δ",    "——",  C['purple'], "_kpi_delta"),
        ]
        for title, init, col, attr in kpi_defs:
            f = QFrame()
            f.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {col}44;"
                f"border-top:2px solid {col};border-radius:5px;}}"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(S.p(8), S.p(5), S.p(8), S.p(6))
            fl.setSpacing(S.p(2))
            fl.addWidget(mk_label(title, col, 8, align=Qt.AlignCenter))
            lbl = mk_val_label(init, col, 18, True, Qt.AlignCenter)
            fl.addWidget(lbl)
            setattr(self, attr, lbl)
            kpi_row.addWidget(f)
        root.addLayout(kpi_row)
        root.addWidget(mk_sep())

        # ── 2열 레이아웃 (섹션 1+2 | 섹션 3+4) ─────────────
        self._report_tabs = QTabWidget()
        self._report_tabs.setStyleSheet(
            f"QTabBar::tab{{background:{C['bg2']};color:{C['text2']};"
            f"padding:{S.p(4)}px {S.p(10)}px;font-size:{S.f(8)}px;}}"
            f"QTabBar::tab:selected{{background:{C['bg3']};color:{C['yellow']};"
            f"border-bottom:2px solid {C['yellow']};}}"
        )
        tab_tooltips = {
            "ab": (
                "Baseline ensemble(A)와 microstructure-enhanced ensemble(B)를 같은 구간에서 비교합니다.\n"
                "표시값은 enhanced - baseline 총손익 차이이며, detail에는 정확도 차이와 변경 건수가 표시됩니다."
            ),
            "calibration": (
                "모델 confidence가 실제 적중률과 얼마나 일치하는지 보는 탭입니다.\n"
                "ECE는 confidence와 실제 정확도의 평균 차이이며, 0에 가까울수록 좋습니다."
            ),
            "meta": (
                "방향 예측 위에 take / reduce / skip을 결정하는 2차 필터 성능입니다.\n"
                "표시값은 현재 best grid의 match rate이며, labels는 누적 meta 표본 수입니다."
            ),
            "rollout": (
                "업그레이드 시스템을 실전에 어느 단계까지 올릴 수 있는지 보여주는 운영 승인 상태입니다.\n"
                "shadow -> alert_only -> small_size -> full 순서로 승격하며, meta 표본과 calibration 상태를 함께 봅니다."
            ),
        }
        self._report_widgets = {}
        for key, title, accent in [
            ("ab", "A/B", C['cyan']),
            ("calibration", "Calibration", C['blue']),
            ("meta", "Meta Gate", C['purple']),
            ("rollout", "Rollout", C['orange']),
        ]:
            frame, value, detail, spark = self._make_report_tab(title, accent)
            self._report_widgets[key] = {"value": value, "detail": detail, "spark": spark}
            idx = self._report_tabs.addTab(frame, title)
            self._report_tabs.tabBar().setTabToolTip(idx, tab_tooltips.get(key, ""))
            frame.setToolTip(tab_tooltips.get(key, ""))
            value.setToolTip(tab_tooltips.get(key, ""))
            detail.setToolTip(tab_tooltips.get(key, ""))
            spark.setToolTip(tab_tooltips.get(key, ""))
        root.addWidget(self._report_tabs)
        root.addWidget(mk_sep())

        cols = QHBoxLayout()
        cols.setSpacing(S.p(8))
        left_col  = QVBoxLayout()
        right_col = QVBoxLayout()
        left_col.setSpacing(S.p(8))
        right_col.setSpacing(S.p(8))

        # ── Section 1: 신뢰도 캘리브레이션 ──────────────────
        left_col.addWidget(mk_label(
            "① 신뢰도 캘리브레이션  ·  예측 신뢰도 vs 실제 적중률",
            C['blue'], 9, True,
        ))
        calib_frame = QFrame()
        calib_frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        calib_grid = QGridLayout(calib_frame)
        calib_grid.setContentsMargins(S.p(8), S.p(6), S.p(8), S.p(6))
        calib_grid.setSpacing(S.p(4))
        for j, hdr_txt in enumerate(["신뢰도", "건수", "실적중률", "품질"]):
            calib_grid.addWidget(mk_label(hdr_txt, C['text2'], 8, True), 0, j)
        calib_grid.setColumnStretch(0, 1)
        calib_grid.setColumnStretch(1, 1)
        calib_grid.setColumnStretch(2, 1)
        calib_grid.setColumnStretch(3, 2)

        self._calib_rows = []
        for i in range(10):    # 최대 10개 구간 (50~95% 등)
            conf_lbl = mk_label("——", C['text2'], 9, align=Qt.AlignCenter)
            cnt_lbl  = mk_label("——", C['text2'], 9, align=Qt.AlignCenter)
            acc_lbl  = mk_label("——", C['text2'], 9, True, Qt.AlignCenter)
            qual_lbl = mk_label("——", C['text2'], 9, True, Qt.AlignCenter)
            for col_idx, w in enumerate([conf_lbl, cnt_lbl, acc_lbl, qual_lbl]):
                calib_grid.addWidget(w, i + 1, col_idx)
            self._calib_rows.append((conf_lbl, cnt_lbl, acc_lbl, qual_lbl))
        left_col.addWidget(calib_frame)

        # ── Section 2: 등급별 성과 ──────────────────────────
        left_col.addWidget(mk_label(
            "② 등급별 매매 성과  ·  A등급이 실제로 더 수익적인가?",
            C['green'], 9, True,
        ))
        grade_frame = QFrame()
        grade_frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        grade_grid = QGridLayout(grade_frame)
        grade_grid.setContentsMargins(S.p(8), S.p(6), S.p(8), S.p(6))
        grade_grid.setSpacing(S.p(4))
        for j, hdr_txt in enumerate(["등급", "건수", "승률", "평균pts", "합계pts"]):
            grade_grid.addWidget(mk_label(hdr_txt, C['text2'], 8, True), 0, j)

        self._grade_rows = {}
        for i, g in enumerate(self._GRADE_ORDER):
            col_map = {"A": C['green'], "B": C['cyan'], "C": C['orange'],
                       "X": C['red'], "?": C['text2']}
            gcol = col_map.get(g, C['text2'])
            badge = mk_badge(g, C['bg3'], gcol, 9)
            cnt_l = mk_label("—", C['text2'], 9, align=Qt.AlignCenter)
            wr_l  = mk_label("—", C['text2'], 9, True, Qt.AlignCenter)
            ap_l  = mk_label("—", C['text2'], 9, True, Qt.AlignCenter)
            tp_l  = mk_label("—", C['text2'], 9, True, Qt.AlignCenter)
            for col_idx, w in enumerate([badge, cnt_l, wr_l, ap_l, tp_l]):
                grade_grid.addWidget(w, i + 1, col_idx)
            self._grade_rows[g] = (cnt_l, wr_l, ap_l, tp_l)
        left_col.addWidget(grade_frame)
        left_col.addStretch()

        # ── Section 3: 학습 성장 곡선 ────────────────────────
        right_col.addWidget(mk_label(
            "③ 학습 성장 곡선  ·  시간에 따라 예측이 개선되는가?",
            C['purple'], 9, True,
        ))
        spark_frame = QFrame()
        spark_frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        spark_lay = QVBoxLayout(spark_frame)
        spark_lay.setContentsMargins(S.p(12), S.p(10), S.p(12), S.p(10))
        spark_lay.setSpacing(S.p(6))

        self._lbl_spark = QLabel("─" * 18)
        self._lbl_spark.setStyleSheet(
            f"color:{C['purple']};font-family:Consolas,monospace;"
            f"font-size:{S.f(18)}px;letter-spacing:1px;"
        )
        self._lbl_spark.setAlignment(Qt.AlignCenter)
        spark_lay.addWidget(self._lbl_spark)

        spark_stats = QHBoxLayout()
        spark_stats.setSpacing(S.p(12))
        for title, attr, col in [
            ("초기 50회 정확도",  "_lbl_spark_early",  C['text2']),
            ("최근 50회 정확도",  "_lbl_spark_recent", C['cyan']),
            ("학습 개선 Δ",       "_lbl_spark_delta",  C['purple']),
        ]:
            vb = QVBoxLayout()
            vb.addWidget(mk_label(title, C['text2'], 8, align=Qt.AlignCenter))
            lbl = mk_val_label("——", col, 15, True, Qt.AlignCenter)
            vb.addWidget(lbl)
            setattr(self, attr, lbl)
            spark_stats.addLayout(vb)
        spark_lay.addLayout(spark_stats)

        # 50개 구간 이동 정확도 미니 차트 (롤링)
        self._lbl_spark_sub = mk_label(
            "← 오래된 예측  ─────────────────  최신 예측 →",
            C['text2'], 7, align=Qt.AlignCenter,
        )
        spark_lay.addWidget(self._lbl_spark_sub)
        right_col.addWidget(spark_frame)

        # ── Section 4: 레짐별 성과 ──────────────────────────
        right_col.addWidget(mk_label(
            "④ 시장 레짐별 성과  ·  어떤 환경에서 전략이 통하는가?",
            C['orange'], 9, True,
        ))
        regime_frame = QFrame()
        regime_frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        regime_lay = QVBoxLayout(regime_frame)
        regime_lay.setContentsMargins(S.p(10), S.p(8), S.p(10), S.p(8))
        regime_lay.setSpacing(S.p(6))

        self._regime_rows = {}
        regime_colors = {
            "RISK_ON":   C['green'],
            "NEUTRAL":   C['orange'],
            "RISK_OFF":  C['red'],
        }
        for r in self._REGIME_ORDER:
            rcol = regime_colors[r]
            rf = QFrame()
            rf.setStyleSheet(
                f"background:{C['bg3']};border:1px solid {rcol}44;border-radius:4px;"
            )
            rl = QHBoxLayout(rf)
            rl.setContentsMargins(S.p(8), S.p(5), S.p(8), S.p(5))
            rl.setSpacing(S.p(8))
            badge = mk_badge(r, C['bg'], rcol, 8)
            rl.addWidget(badge)
            cnt_l = mk_label("0건", C['text2'], 8)
            rl.addWidget(cnt_l)
            rl.addStretch()
            wr_l  = mk_val_label("——", rcol, 14, True)
            rl.addWidget(wr_l)
            rl.addWidget(mk_label("승률", C['text2'], 8))
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(S.p(10))
            bar.setFixedWidth(S.p(80))
            bar.setStyleSheet(
                f"QProgressBar{{background:{C['bg']};border:none;border-radius:3px;}}"
                f"QProgressBar::chunk{{background:{rcol};}}"
            )
            rl.addWidget(bar)
            ap_l = mk_label("avg ——pt", C['text2'], 8)
            rl.addWidget(ap_l)
            regime_lay.addWidget(rf)
            self._regime_rows[r] = (cnt_l, wr_l, bar, ap_l)
        right_col.addWidget(regime_frame)

        # ── 종합 평가 배너 ──────────────────────────────────
        self._lbl_verdict = QLabel("데이터 수집 중 — 체결 완료 거래 10건 이상 시 분석 시작")
        self._lbl_verdict.setWordWrap(True)
        self._lbl_verdict.setStyleSheet(
            f"background:{C['bg3']};color:{C['text2']};border:1px solid {C['border']};"
            f"border-left:3px solid {C['yellow']};border-radius:4px;"
            f"padding:6px 10px;font-size:{S.f(10)}px;"
        )
        right_col.addWidget(self._lbl_verdict)
        right_col.addStretch()

        left_w  = QWidget(); left_w.setLayout(left_col)
        right_w = QWidget(); right_w.setLayout(right_col)
        cols.addWidget(left_w,  45)
        cols.addWidget(right_w, 55)
        root.addLayout(cols)

    # ── 업데이트 ──────────────────────────────────────────────
    def update_data(self, data: dict):
        """
        data 키:
            calibration_bins  list[dict]  conf_bin/cnt/accuracy
            grade_stats       list[dict]  grade/cnt/win_rate/avg_pnl/total_pnl
            regime_stats      list[dict]  regime/cnt/win_rate/avg_pnl
            accuracy_history  list[int]   0/1 리스트 (최신→오래된 순)
            updated_at        str         "HH:MM"
        """
        import datetime as _dt

        now_str = data.get("updated_at") or _dt.datetime.now().strftime("%H:%M")
        self._lbl_updated.setText(f"마지막 갱신: {now_str}")

        # ── 섹션 1: 캘리브레이션 ─────────────────────────────
        report_history = data.get("report_history") or []
        ab_metrics = data.get("ab_metrics") or {}
        calibration_metrics = data.get("calibration_metrics") or {}
        meta_metrics = data.get("meta_metrics") or {}
        rollout_metrics = data.get("rollout_metrics") or {}

        baseline = ab_metrics.get("baseline", {})
        enhanced = ab_metrics.get("enhanced", {})
        ab_delta = float(enhanced.get("total_pnl_pts", 0.0) or 0.0) - float(baseline.get("total_pnl_pts", 0.0) or 0.0)
        ab_acc_delta = float(enhanced.get("directional_accuracy", 0.0) or 0.0) - float(baseline.get("directional_accuracy", 0.0) or 0.0)
        self._report_widgets["ab"]["value"].setText(f"{ab_delta:+.2f}pt")
        self._report_widgets["ab"]["detail"].setText(
            f"acc {ab_acc_delta:+.2%} | changed {int(ab_metrics.get('changed_count', 0) or 0)}"
        )
        self._report_widgets["ab"]["spark"].setText(self._spark(self._history_series(report_history, "ab_pnl_delta"), 16))

        overall_cal = calibration_metrics.get("overall", {})
        calib_ece = float(overall_cal.get("ece", 0.0) or 0.0)
        self._report_widgets["calibration"]["value"].setText(f"ECE {calib_ece:.3f}")
        self._report_widgets["calibration"]["detail"].setText(
            f"brier {float(overall_cal.get('brier', 0.0) or 0.0):.3f} | n {int(overall_cal.get('count', 0) or 0)}"
        )
        self._report_widgets["calibration"]["spark"].setText(self._spark(self._history_series(report_history, "calibration_ece"), 16))

        best_grid = meta_metrics.get("best_grid", {})
        meta_count = int(meta_metrics.get("count", 0) or 0)
        meta_match = float(best_grid.get("match_rate", 0.0) or 0.0)
        self._report_widgets["meta"]["value"].setText(f"{meta_match:.1%}")
        self._report_widgets["meta"]["detail"].setText(
            f"labels {meta_count} | take>={float(best_grid.get('take_threshold', 0.0) or 0.0):.2f}"
        )
        self._report_widgets["meta"]["spark"].setText(self._spark(self._history_series(report_history, "meta_match_rate"), 16))

        rollout_stage = str(rollout_metrics.get("recommended_stage", "shadow") or "shadow")
        self._report_widgets["rollout"]["value"].setText(rollout_stage.upper())
        self._report_widgets["rollout"]["detail"].setText(
            f"meta {int((rollout_metrics.get('gate_stats') or {}).get('meta_labels', 0) or 0)} | ece {float(rollout_metrics.get('ece', 0.0) or 0.0):.3f}"
        )
        rollout_hist = [1.0 if str(item.get("rollout_stage", "shadow")) != "shadow" else 0.0 for item in report_history[-24:]]
        self._report_widgets["rollout"]["spark"].setText(self._spark(rollout_hist, 16))

        bins = data.get("calibration_bins") or []
        for i, row_w in enumerate(self._calib_rows):
            conf_lbl, cnt_lbl, acc_lbl, qual_lbl = row_w
            if i < len(bins):
                b = bins[i]
                cf  = float(b.get("conf_bin", 0)) / 100.0
                cnt = int(b.get("cnt", 0))
                acc = float(b.get("accuracy") or 0)
                qtxt, qcol = self._calib_badge(cf, acc)
                conf_lbl.setText(f"{cf:.0%}")
                conf_lbl.setStyleSheet(f"color:{C['text']};font-size:{S.f(9)}px;")
                cnt_lbl.setText(str(cnt))
                acc_lbl.setText(f"{acc:.1%}")
                acc_col = self._win_col(acc)
                acc_lbl.setStyleSheet(f"color:{acc_col};font-size:{S.f(9)}px;font-weight:bold;")
                qual_lbl.setText(qtxt)
                qual_lbl.setStyleSheet(f"color:{qcol};font-size:{S.f(9)}px;font-weight:bold;")
            else:
                for w in row_w:
                    w.setText("——")
                    w.setStyleSheet(f"color:{C['text2']};font-size:{S.f(9)}px;")

        # ── 섹션 2: 등급별 성과 ──────────────────────────────
        grade_map = {r.get("grade", "?"): r for r in (data.get("grade_stats") or [])}
        total_cnt = sum(int(r.get("cnt", 0)) for r in (data.get("grade_stats") or []))
        total_wins = sum(
            int(r.get("cnt", 0)) * float(r.get("win_rate") or 0)
            for r in (data.get("grade_stats") or [])
        )
        overall_wr = (total_wins / total_cnt) if total_cnt > 0 else 0.0
        self._kpi_total_wr.setText(f"{overall_wr:.1%}")
        self._kpi_total_wr.setStyleSheet(
            f"color:{self._win_col(overall_wr)};font-size:{S.f(18)}px;font-weight:bold;"
        )

        for g, (cnt_l, wr_l, ap_l, tp_l) in self._grade_rows.items():
            r = grade_map.get(g)
            if r:
                cnt  = int(r.get("cnt", 0))
                wr   = float(r.get("win_rate") or 0)
                apnl = float(r.get("avg_pnl") or 0)
                tpnl = float(r.get("total_pnl") or 0)
                wrcol  = self._win_col(wr)
                pnlcol = self._pnl_col(apnl)
                cnt_l.setText(str(cnt))
                wr_l.setText(f"{wr:.1%}")
                wr_l.setStyleSheet(f"color:{wrcol};font-size:{S.f(9)}px;font-weight:bold;")
                ap_l.setText(f"{apnl:+.2f}")
                ap_l.setStyleSheet(f"color:{pnlcol};font-size:{S.f(9)}px;font-weight:bold;")
                tp_l.setText(f"{tpnl:+.1f}")
                tp_l.setStyleSheet(f"color:{self._pnl_col(tpnl)};font-size:{S.f(9)}px;font-weight:bold;")
                # A등급 KPI
                if g == "A":
                    self._kpi_a_wr.setText(f"{wr:.1%}")
                    self._kpi_a_wr.setStyleSheet(
                        f"color:{wrcol};font-size:{S.f(18)}px;font-weight:bold;"
                    )
            else:
                cnt_l.setText("—");  wr_l.setText("—");  ap_l.setText("—");  tp_l.setText("—")
                for w in [cnt_l, wr_l, ap_l, tp_l]:
                    w.setStyleSheet(f"color:{C['text2']};font-size:{S.f(9)}px;")

        # ── 섹션 3: 학습 성장 곡선 ───────────────────────────
        hist = list(data.get("accuracy_history") or [])  # 최신→오래된 순
        if hist:
            hist_rev = list(reversed(hist))   # 오래된→최신 순
            n = len(hist_rev)
            early_n  = min(50, n // 2)
            recent_n = min(50, n // 2)
            early_acc  = (sum(hist_rev[:early_n])  / early_n)  if early_n  else 0.5
            recent_acc = (sum(hist_rev[-recent_n:]) / recent_n) if recent_n else 0.5
            delta = recent_acc - early_acc

            # 롤링 20구간 스파크라인
            chunk = max(1, n // 20)
            roll_accs = []
            for i in range(0, n, chunk):
                sl = hist_rev[i: i + chunk]
                roll_accs.append(sum(sl) / len(sl))
            spark_str = self._spark(roll_accs, 18)

            self._lbl_spark.setText(spark_str)
            early_col  = self._win_col(early_acc)
            recent_col = self._win_col(recent_acc)
            self._lbl_spark_early.setText(f"{early_acc:.1%}")
            self._lbl_spark_early.setStyleSheet(
                f"color:{early_col};font-size:{S.f(15)}px;font-weight:bold;"
            )
            self._lbl_spark_recent.setText(f"{recent_acc:.1%}")
            self._lbl_spark_recent.setStyleSheet(
                f"color:{recent_col};font-size:{S.f(15)}px;font-weight:bold;"
            )
            delta_col = C['green'] if delta >= 0 else C['red']
            self._lbl_spark_delta.setText(f"{delta:+.1%}")
            self._lbl_spark_delta.setStyleSheet(
                f"color:{delta_col};font-size:{S.f(15)}px;font-weight:bold;"
            )
            self._lbl_spark_sub.setText(
                f"← 오래된 예측  {spark_str}  최신 예측 →"
            )

            # 캘리브레이션 KPI
            if bins:
                valid = [b for b in bins if int(b.get("cnt", 0)) >= 5]
                if valid:
                    avg_gap = sum(
                        abs(float(b.get("accuracy") or 0) - float(b.get("conf_bin", 0)) / 100.0)
                        for b in valid
                    ) / len(valid)
                    calib_score = max(0.0, 1.0 - avg_gap * 5)
                    calib_col = C['green'] if calib_score >= 0.7 else (
                        C['orange'] if calib_score >= 0.4 else C['red']
                    )
                    self._kpi_calib.setText(f"{calib_score:.0%}")
                    self._kpi_calib.setStyleSheet(
                        f"color:{calib_col};font-size:{S.f(18)}px;font-weight:bold;"
                    )

            # 학습 효과 KPI
            self._kpi_delta.setText(f"{delta:+.1%}")
            self._kpi_delta.setStyleSheet(
                f"color:{delta_col};font-size:{S.f(18)}px;font-weight:bold;"
            )

        # ── 섹션 4: 레짐별 성과 ──────────────────────────────
        regime_map = {r.get("regime", "NEUTRAL"): r
                      for r in (data.get("regime_stats") or [])}
        for regime, (cnt_l, wr_l, bar, ap_l) in self._regime_rows.items():
            r = regime_map.get(regime)
            if r:
                cnt  = int(r.get("cnt", 0))
                wr   = float(r.get("win_rate") or 0)
                apnl = float(r.get("avg_pnl") or 0)
                wrcol = self._win_col(wr)
                cnt_l.setText(f"{cnt}건")
                wr_l.setText(f"{wr:.1%}")
                wr_l.setStyleSheet(f"color:{wrcol};font-size:{S.f(14)}px;font-weight:bold;")
                bar.setValue(int(wr * 100))
                ap_l.setText(f"avg {apnl:+.2f}pt")
                ap_l.setStyleSheet(f"color:{self._pnl_col(apnl)};font-size:{S.f(8)}px;")
            else:
                cnt_l.setText("0건")
                wr_l.setText("——")
                bar.setValue(0)
                ap_l.setText("avg ——pt")

        # ── 종합 평가 배너 ────────────────────────────────────
        if total_cnt < 10:
            self._lbl_verdict.setText(
                f"데이터 수집 중 ({total_cnt}건 체결) — 10건 이상 시 분석 시작"
            )
            self._lbl_verdict.setStyleSheet(
                f"background:{C['bg3']};color:{C['text2']};border:1px solid {C['border']};"
                f"border-left:3px solid {C['text2']};border-radius:4px;"
                f"padding:6px 10px;font-size:{S.f(10)}px;"
            )
        else:
            # 종합 판단
            grade_a = grade_map.get("A")
            a_wr = float(grade_a.get("win_rate", 0) if grade_a else 0)
            if a_wr >= 0.60 and overall_wr >= 0.53:
                verdict = f"✅  학습 효과 확인 — A등급 승률 {a_wr:.1%} / 전체 승률 {overall_wr:.1%}"
                v_col = C['green']
            elif overall_wr >= 0.50:
                verdict = f"⚡  개선 중 — 전체 승률 {overall_wr:.1%} | A등급 추가 데이터 필요"
                v_col = C['cyan']
            else:
                verdict = f"⚠️  학습 효과 미확인 — 전체 승률 {overall_wr:.1%} | 모델 재점검 권장"
                v_col = C['orange']
            self._lbl_verdict.setText(verdict)
            self._lbl_verdict.setStyleSheet(
                f"background:{C['bg3']};color:{C['text']};border:1px solid {v_col}44;"
                f"border-left:3px solid {v_col};border-radius:4px;"
                f"padding:6px 10px;font-size:{S.f(10)}px;font-weight:bold;"
            )


# ────────────────────────────────────────────────────────────
# 패널 8: 📈 학습 성장 추이 (일/주/월/연간)
# ────────────────────────────────────────────────────────────
class TrendPanel(QWidget):
    """자가학습 성과의 일/주/월/연간 추이 대시보드"""

    _SPARK = "▁▂▃▄▅▆▇█"

    # ── 컬럼 정의 ──────────────────────────────────────────
    _DAILY_COLS   = ["날짜",  "거래", "승/패", "승률", "PnL (원)",   "SGD정확도"]
    _WEEKLY_COLS  = ["주차",  "거래", "승/패", "승률", "PnL (원)"]
    _MONTHLY_COLS = ["월",    "거래", "승/패", "승률", "PnL (원)"]
    _YEARLY_COLS  = ["연도",  "거래", "승/패", "승률", "PnL (원)"]

    _PERIOD_COLS = {
        "일별": _DAILY_COLS,
        "주별": _WEEKLY_COLS,
        "월별": _MONTHLY_COLS,
        "연간": _YEARLY_COLS,
    }

    def __init__(self):
        super().__init__()
        self._row_widgets: dict = {"일별": [], "주별": [], "월별": [], "연간": []}
        self._build()

    # ── 스파크라인 유틸 ────────────────────────────────────
    @staticmethod
    def _spark_line(values, width: int = 20) -> str:
        blk = "▁▂▃▄▅▆▇█"
        if not values:
            return "─" * width
        mn, mx = min(values), max(values)
        span = (mx - mn) or 1.0
        chars = [blk[min(7, int((v - mn) / span * 7.99))] for v in values]
        while len(chars) > width:
            step = len(chars) / width
            chars = [chars[int(i * step)] for i in range(width)]
        while len(chars) < width:
            chars.append("─")
        return "".join(chars)

    @staticmethod
    def _wr_col(wr: float) -> str:
        if wr >= 0.60: return C['green']
        if wr >= 0.53: return C['cyan']
        if wr >= 0.45: return C['orange']
        return C['red']

    @staticmethod
    def _pnl_col(pnl: float) -> str:
        return C['green'] if pnl > 0 else (C['red'] if pnl < 0 else C['text2'])

    @staticmethod
    def _acc_col(acc) -> str:
        if acc is None: return C['text2']
        if acc >= 0.62: return C['green']
        if acc >= 0.55: return C['cyan']
        if acc >= 0.48: return C['orange']
        return C['red']

    # ── UI 빌드 ──────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(S.p(8), S.p(8), S.p(8), S.p(8))
        root.setSpacing(S.p(8))

        # 헤더
        hdr = QHBoxLayout()
        hdr.addWidget(mk_label("📈  학습 성장 추이", C['cyan'], 11, True))
        hdr.addStretch()
        self._lbl_updated = mk_label("마지막 갱신: ——", C['text2'], 8)
        hdr.addWidget(self._lbl_updated)
        root.addLayout(hdr)

        # 스파크라인 요약 바
        spark_frame = QFrame()
        spark_frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        sl = QHBoxLayout(spark_frame)
        sl.setContentsMargins(S.p(10), S.p(7), S.p(10), S.p(7))
        sl.setSpacing(S.p(16))
        self._lbl_pnl_spark = mk_label("PnL  ─────────────────────", C['cyan'],  9)
        self._lbl_wr_spark  = mk_label("승률  ─────────────────────", C['green'], 9)
        self._lbl_acc_spark = mk_label("SGD  ─────────────────────", C['purple'],9)
        for lbl in (self._lbl_pnl_spark, self._lbl_wr_spark, self._lbl_acc_spark):
            lbl.setFont(__import__('PyQt5.QtGui', fromlist=['QFont']).QFont("Consolas", S.f(9)))
            sl.addWidget(lbl)
        sl.addStretch()
        root.addWidget(spark_frame)
        root.addWidget(mk_sep())

        # 4-탭 (일별/주별/월별/연간)
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            f"QTabBar::tab{{background:{C['bg2']};color:{C['text2']};"
            f"padding:{S.p(4)}px {S.p(10)}px;font-size:{S.f(9)}px;}}"
            f"QTabBar::tab:selected{{background:{C['bg3']};color:{C['cyan']};"
            f"border-bottom:2px solid {C['cyan']};}}"
        )
        self._content_widgets: dict = {}
        for period in ("일별", "주별", "월별", "연간"):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setStyleSheet(
                "QScrollArea{border:none;background:transparent;}"
                f"QScrollBar:vertical{{background:{C['bg2']};width:6px;}}"
                f"QScrollBar::handle:vertical{{background:{C['border']};border-radius:3px;}}"
            )
            inner = QWidget()
            inner.setStyleSheet("background:transparent;")
            vl = QVBoxLayout(inner)
            vl.setContentsMargins(0, 0, S.p(4), 0)
            vl.setSpacing(0)
            vl.addStretch()
            scroll.setWidget(inner)
            self._content_widgets[period] = vl
            self._tabs.addTab(scroll, period)

        root.addWidget(self._tabs, 1)

    # ── 헤더 행 생성 ────────────────────────────────────────
    def _make_header(self, cols: list) -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"background:{C['bg3']};border-bottom:1px solid {C['border']};"
        )
        hl = QHBoxLayout(f)
        hl.setContentsMargins(S.p(8), S.p(4), S.p(8), S.p(4))
        hl.setSpacing(0)
        for i, col in enumerate(cols):
            lbl = mk_label(col, C['text2'], 8, True)
            stretch = 2 if col in ("PnL (원)", "날짜", "월", "주차", "연도") else 1
            hl.addWidget(lbl, stretch)
        return f

    # ── 데이터 행 생성 ──────────────────────────────────────
    def _make_row(self, cells: list, cols: list, is_alt: bool) -> QFrame:
        f = QFrame()
        bg = C['bg2'] if is_alt else C['bg']
        f.setStyleSheet(
            f"QFrame{{background:{bg};border-bottom:1px solid {C['border']}33;}}"
        )
        hl = QHBoxLayout(f)
        hl.setContentsMargins(S.p(8), S.p(4), S.p(8), S.p(4))
        hl.setSpacing(0)
        for i, (text, col) in enumerate(cells):
            stretch = 2 if cols[i] in ("PnL (원)", "날짜", "월", "주차", "연도") else 1
            lbl = mk_label(text, col, 9, align=Qt.AlignLeft if i == 0 else Qt.AlignCenter)
            hl.addWidget(lbl, stretch)
        return f

    # ── 탭 내용 갱신 ────────────────────────────────────────
    def _refresh_tab(self, period: str, rows: list):
        cols = self._PERIOD_COLS[period]
        vl = self._content_widgets[period]

        # 기존 위젯 제거 (stretch 유지)
        while vl.count() > 1:
            item = vl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not rows:
            empty = mk_label("데이터 없음 (체결 완료 거래가 없습니다)", C['text2'], 9,
                             align=Qt.AlignCenter)
            vl.insertWidget(0, empty)
            return

        vl.insertWidget(0, self._make_header(cols))

        for idx, row in enumerate(rows):
            cells = self._row_cells(row, period, cols)
            vl.insertWidget(idx + 1, self._make_row(cells, cols, idx % 2 == 0))

    def _row_cells(self, row: dict, period: str, cols: list) -> list:
        trades   = int(row.get("trades",   0))
        wins     = int(row.get("wins",     0))
        losses   = int(row.get("losses",   0))
        win_rate = float(row.get("win_rate", 0.0))
        pnl_krw  = float(row.get("pnl_krw", 0.0))
        sgd_acc  = row.get("sgd_accuracy")  # None if not available

        # 기간 키
        if period == "일별":
            date_raw = str(row.get("date", ""))
            label = date_raw[5:] if len(date_raw) >= 7 else date_raw   # MM-DD
        elif period == "주별":
            label = str(row.get("week", ""))
        elif period == "월별":
            label = str(row.get("month", ""))
        else:
            label = str(row.get("year", ""))

        wr_col  = self._wr_col(win_rate)
        pnl_col = self._pnl_col(pnl_krw)
        pnl_str = f"{'+' if pnl_krw > 0 else ''}{pnl_krw:,.0f}"

        cells = [
            (label,                      C['text']),
            (str(trades),                C['text2']),
            (f"{wins}/{losses}",         wr_col),
            (f"{win_rate:.0%}",          wr_col),
            (pnl_str,                    pnl_col),
        ]
        if period == "일별":
            if sgd_acc is not None:
                acc_str = f"{sgd_acc:.1%}"
            else:
                acc_str = "——"
            cells.append((acc_str, self._acc_col(sgd_acc)))
        return cells

    # ── 전체 갱신 (외부 호출) ───────────────────────────────
    def update_data(self, data: dict):
        import datetime as _dt
        self._lbl_updated.setText(
            f"마지막 갱신: {data.get('updated_at', _dt.datetime.now().strftime('%H:%M'))}"
        )

        for period in ("일별", "주별", "월별", "연간"):
            self._refresh_tab(period, data.get(period, []))

        # 스파크라인 (일별 최근 20일, 오래된→최신 순)
        daily = list(reversed(data.get("일별", [])))
        if daily:
            pnl_vals = [float(r.get("pnl_krw", 0)) for r in daily]
            wr_vals  = [float(r.get("win_rate", 0.5)) for r in daily]
            acc_vals = [float(r["sgd_accuracy"]) for r in daily
                        if r.get("sgd_accuracy") is not None]
            self._lbl_pnl_spark.setText(
                f"PnL  {self._spark_line(pnl_vals, 20)}"
                f"  {pnl_vals[-1]:+,.0f}원"
            )
            self._lbl_wr_spark.setText(
                f"승률  {self._spark_line(wr_vals, 20)}"
                f"  {wr_vals[-1]:.0%}"
            )
            if acc_vals:
                self._lbl_acc_spark.setText(
                    f"SGD   {self._spark_line(acc_vals, 20)}"
                    f"  {acc_vals[-1]:.1%}"
                )


# ────────────────────────────────────────────────────────────
# 패널 9: 알파 리서치 봇
# ────────────────────────────────────────────────────────────
class AlphaPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("알파 리서치 봇 — 자율 진화 시스템", C['yellow'], 10, True))

        # 카운터
        ctr = QHBoxLayout()
        for lbl, val, col in [("검색 논문",147,C['text']),
                               ("고품질 후보",8,C['green']),
                               ("검토 중",3,C['orange']),
                               ("통합 완료",12,C['blue'])]:
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6,3,6,3)
            fl.addWidget(mk_label(lbl, C['text2'], 9, align=Qt.AlignCenter))
            fl.addWidget(mk_val_label(str(val), col, 16, align=Qt.AlignCenter))
            ctr.addWidget(f)
        lay.addLayout(ctr)
        lay.addWidget(mk_sep())

        # 신규 알림 배너
        self.alert_box = QLabel("🔬 [대기] 알파 리서치 봇 활성 — 신규 발견 시 알림")
        self.alert_box.setWordWrap(True)
        self.alert_box.setStyleSheet(
            f"background:{C['bg3']};color:{C['text2']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:6px;font-size:{S.f(12)}px;"
        )
        lay.addWidget(self.alert_box)
        lay.addWidget(mk_sep())

        # 논문 TOP 5
        lay.addWidget(mk_label("신규 알파 후보 TOP (AI 평가 순위)", C['blue'], 9, True))
        papers = [
            ("Liquidity-Adjusted OFI for KOSPI",     "JoF",  95, "즉시"),
            ("Transformer Multi-Horizon Forecasting", "arXiv",87, "즉시"),
            ("Retail Investor Herding in Options",    "한국", 82, "즉시"),
            ("PPO Reinforcement Learning Sizing",     "SSRN", 78, "보통"),
            ("Volatility Surface Weekly Expiry",      "arXiv",71, "보통"),
        ]
        for i, (title, src, score, pri) in enumerate(papers):
            f = QFrame()
            f.setStyleSheet(
                f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(8, 5, 8, 5)
            fl.setSpacing(3)
            head = QHBoxLayout()
            rank_col = ["#BA7517","#888","#639922",C['text2'],C['text2']][i]
            head.addWidget(mk_badge(str(i+1), rank_col, "#fff", 8))
            src_map = {"JoF":C['green'],"arXiv":C['orange'],"한국":C['red'],"SSRN":C['purple']}
            head.addWidget(mk_badge(src, src_map.get(src,C['blue']), "#fff", 8))
            head.addWidget(mk_label(title, C['text'], 10), 2)
            sc_col = C['green'] if score >= 90 else C['orange'] if score >= 80 else C['text2']
            head.addWidget(mk_label(f"{score}점", sc_col, 9))
            pri_col = C['red'] if pri == "즉시" else C['orange']
            head.addWidget(mk_badge(pri, pri_col, "#fff", 8))
            fl.addLayout(head)

            sb = mk_prog(sc_col, 5)
            sb.setValue(score)
            fl.addWidget(sb)

            btn_row = QHBoxLayout()
            for blbl, bcol in [("코드생성",C['cyan']),("백테스트",C['blue']),("기각",C['red'])]:
                b = QPushButton(blbl)
                b.setStyleSheet(
                    f"background:{C['bg3']};color:{bcol};border:1px solid {bcol};"
                    f"border-radius:3px;padding:2px 8px;font-size:{S.f(11)}px;"
                )
                btn_row.addWidget(b)
            btn_row.addStretch()
            fl.addLayout(btn_row)
            lay.addWidget(f)

        lay.addWidget(mk_sep())

        # 검색 일정
        lay.addWidget(mk_label("검색 일정", C['text2'], 9, True))
        for cycle, time_s, src in [
            ("일간","09:00","헤지펀드 블로그·뉴스"),
            ("주간","월 08:30","arXiv·SSRN"),
            ("월간","1일 08:00","전체 학술지 정밀 평가"),
        ]:
            r = QHBoxLayout()
            r.addWidget(mk_badge(cycle, C['blue'], "#fff", 8))
            r.addWidget(mk_label(time_s, C['text2'], 9))
            r.addWidget(mk_label(src, C['text'], 9), 2)
            lay.addLayout(r)

    def show_alert(self, title, score):
        self.alert_box.setText(
            f"⚡ 긴급 — ★★★★★ 신규 알파 발견 ({score}점)\n"
            f"「{title}」 → 코드 자동 생성 권장"
        )
        self.alert_box.setStyleSheet(
            f"background:#2D0D0D;color:{C['red']};border:1px solid {C['red']};"
            f"border-radius:4px;padding:6px;font-size:{S.f(12)}px;font-weight:bold;"
        )


# ────────────────────────────────────────────────────────────
# 패널 7: 5층 로그 시스템
# ────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────
# 손익 추이 패널 — 일별·주별·월별 누적 P&L 테이블
# ────────────────────────────────────────────────────────────
class PnlHistoryPanel(QWidget):
    """전문 트레이더용 손익 추이 — 일별·주별·월별 누적 테이블"""

    _DAILY_HEADERS   = ["날짜",  "거래", "승", "패", "승률", "P/L pt(실행/순)", "P/L 원(실행/순)",   "누적 원(실행/순)"]
    _WEEKLY_HEADERS  = ["주간",  "거래", "승", "패", "승률", "P/L pt(실행/순)", "P/L 원(실행/순)",   "누적 원(실행/순)", "MDD 원(실행/순)"]
    _MONTHLY_HEADERS = ["월",    "거래", "승", "패", "승률", "P/L pt(실행/순)", "P/L 원(실행/순)",   "누적 원(실행/순)", "샤프(실행/순)"]

    def __init__(self):
        super().__init__()
        self._rows = []
        self._build()

    # ── UI 구성 ────────────────────────────────────────────────

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(4)

        # 요약 카드 행
        sf = QFrame()
        sf.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;"
        )
        sf_lay = QHBoxLayout(sf)
        sf_lay.setContentsMargins(6, 4, 6, 4)
        sf_lay.setSpacing(4)
        self._sum = {}
        for key, label, col in [
            ("days",    "거래일",    C['blue']),
            ("trades",  "총 거래",   C['text']),
            ("winrate", "총 승률",   C['cyan']),
            ("total",   "총 손익",   C['green']),
            ("mdd",     "최대 MDD",  C['orange']),
            ("streak",  "최장 연승", C['yellow']),
        ]:
            f = QFrame()
            f.setStyleSheet(
                f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6, 3, 6, 3)
            fl.setSpacing(1)
            fl.addWidget(mk_label(label, C['text2'], 9, align=Qt.AlignCenter))
            vl = mk_val_label("—", col, 12, align=Qt.AlignCenter)
            fl.addWidget(vl)
            sf_lay.addWidget(f)
            self._sum[key] = vl
        lay.addWidget(sf)

        # 일별·주별·월별 내부 탭
        inner = QTabWidget()
        inner.setStyleSheet(
            f"QTabWidget::pane{{background:{C['bg']};border:none;}}"
            f"QTabBar::tab{{background:{C['bg2']};color:{C['text2']};"
            f"padding:3px 12px;font-size:{S.f(10)}px;border:none;}}"
            f"QTabBar::tab:selected{{color:{C['cyan']};"
            f"border-bottom:2px solid {C['cyan']};}}"
            f"QTabBar::tab:hover{{color:{C['text']};}}"
        )

        self.tbl_daily   = self._make_tbl(self._DAILY_HEADERS)
        self.tbl_weekly  = self._make_tbl(self._WEEKLY_HEADERS)
        self.tbl_monthly = self._make_tbl(self._MONTHLY_HEADERS)

        inner.addTab(self.tbl_daily,   "일별 (60일)")
        inner.addTab(self.tbl_weekly,  "주별 (13주)")
        inner.addTab(self.tbl_monthly, "월별")
        lay.addWidget(inner, 1)

    def _make_tbl(self, headers):
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.verticalHeader().setVisible(False)
        tbl.setShowGrid(True)
        tbl.setSortingEnabled(False)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.horizontalHeader().setHighlightSections(False)
        tbl.setStyleSheet(
            f"QTableWidget{{background:{C['bg']};color:{C['text']};border:none;"
            f"gridline-color:{C['border']};font-size:{S.f(11)}px;outline:none;}}"
            f"QTableWidget::item{{padding:2px 5px;}}"
            f"QHeaderView::section{{background:{C['bg2']};color:{C['text2']};"
            f"border:none;border-bottom:1px solid {C['border']};"
            f"border-right:1px solid {C['border']};"
            f"font-size:{S.f(10)}px;font-weight:bold;padding:3px 5px;}}"
            f"QTableWidget::item:selected{{background:{C['bg3']};color:{C['text']};}}"
        )
        return tbl

    # ── 셀 팩토리 ──────────────────────────────────────────────

    def _item(self, text, fg=None, bg=None, bold=False, align=Qt.AlignCenter):
        it = QTableWidgetItem(str(text))
        it.setTextAlignment(align | Qt.AlignVCenter)
        it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        if fg:
            it.setForeground(QColor(fg))
        if bg:
            it.setBackground(bg)
        if bold:
            ft = it.font()
            ft.setBold(True)
            it.setFont(ft)
        return it

    def _row_bg(self, pnl_krw):
        if pnl_krw > 0:
            return QColor(15, 45, 25)
        if pnl_krw < 0:
            return QColor(50, 18, 18)
        return QColor(C['bg'])

    def _pcol(self, val):
        return C['green'] if val > 0 else (C['red'] if val < 0 else C['text2'])

    # ── 갱신 진입점 ────────────────────────────────────────────

    def refresh(self, rows):
        """trades.db 행 목록으로 전체 갱신. rows: sqlite3.Row list."""
        self._rows = []
        for r in rows:
            try:
                trade_ts = r["exit_ts"] or r["entry_ts"] or ""
                self._rows.append({
                    "entry_ts": trade_ts,
                    "pnl_pts":  float(r["pnl_pts"]  or 0),
                    "pnl_krw":  float(r["pnl_krw"]  or 0),
                    "forward_pnl_pts": float(r["forward_pnl_pts"] or r["pnl_pts"] or 0),
                    "forward_pnl_krw": float(r["forward_pnl_krw"] or r["pnl_krw"] or 0),
                    "quantity": int(r["quantity"]    or 1),
                })
            except Exception:
                pass
        self._build_daily()
        self._build_weekly()
        self._build_monthly()
        self._build_summary()

    # ── 그룹화 유틸 ────────────────────────────────────────────

    def _group(self, key_fn):
        from collections import defaultdict
        d = defaultdict(list)
        for r in self._rows:
            k = key_fn(r["entry_ts"])
            if k:
                d[k].append(r)
        return sorted(d.items())

    @staticmethod
    def _week_key(ts):
        try:
            import datetime as _dt
            d   = _dt.date.fromisoformat(ts[:10])
            iso = d.isocalendar()
            return f"{iso[0]}-W{iso[1]:02d}"
        except Exception:
            return ""

    def _stats(self, rows, pts_key="pnl_pts", krw_key="pnl_krw"):
        n     = len(rows)
        wins  = sum(1 for r in rows if r[pts_key] > 0)
        ppts  = sum(r[pts_key] * r["quantity"] for r in rows)
        pkrw  = sum(r[krw_key] for r in rows)
        return n, wins, n - wins, round(ppts, 2), round(pkrw, 0)

    def _mdd(self, rows, krw_key="pnl_krw"):
        eq, peak, mdd = 0.0, 0.0, 0.0
        for r in sorted(rows, key=lambda x: x["entry_ts"]):
            eq  += r[krw_key]
            peak = max(peak, eq)
            mdd  = min(mdd, eq - peak)
        return round(mdd, 0)

    @staticmethod
    def _dual_text(executed, forward, decimals=0, suffix=""):
        if decimals == 0:
            exec_txt = f"{executed:+,.0f}{suffix}"
            fwd_txt = f"{forward:+,.0f}{suffix}"
        else:
            exec_txt = f"{executed:+,.{decimals}f}{suffix}"
            fwd_txt = f"{forward:+,.{decimals}f}{suffix}"
        return f"실행 {exec_txt} / 순 {fwd_txt}"

    def _sharpe(self, daily_pnls):
        n = len(daily_pnls)
        if n < 2:
            return 0.0
        mean = sum(daily_pnls) / n
        var  = sum((x - mean) ** 2 for x in daily_pnls) / (n - 1)
        std  = var ** 0.5 if var > 0 else 0.0
        return round(mean / std * (252 ** 0.5), 2) if std else 0.0

    # ── 일별 테이블 ────────────────────────────────────────────

    def _build_daily(self):
        today  = datetime.now().strftime("%Y-%m-%d")
        groups = self._group(lambda ts: ts[:10])[-60:]
        # 누적 맵 (오름차순 기준)
        cum_map, c = {}, 0.0
        forward_cum_map, fc = {}, 0.0
        for date_str, grp in groups:
            _, _, _, _, pkrw = self._stats(grp)
            _, _, _, _, forward_pkrw = self._stats(grp, "forward_pnl_pts", "forward_pnl_krw")
            c += pkrw
            fc += forward_pkrw
            cum_map[date_str] = c
            forward_cum_map[date_str] = fc

        tbl = self.tbl_daily
        tbl.setRowCount(len(groups))
        for r_idx, (date_str, grp) in enumerate(reversed(groups)):
            n, wins, losses, ppts, pkrw = self._stats(grp)
            _, _, _, forward_ppts, forward_pkrw = self._stats(grp, "forward_pnl_pts", "forward_pnl_krw")
            cum  = cum_map[date_str]
            forward_cum = forward_cum_map[date_str]
            wr   = f"{wins/n*100:.0f}%" if n else "—"
            bg   = self._row_bg(pkrw)
            pc   = self._pcol(pkrw)
            cc   = self._pcol(cum)
            is_t = (date_str == today)
            cells = [
                self._item(date_str,         fg=C['yellow'] if is_t else None, bg=bg, bold=is_t),
                self._item(str(n),           bg=bg, align=Qt.AlignRight),
                self._item(str(wins),        fg=C['green'], bg=bg, align=Qt.AlignRight),
                self._item(str(losses),      fg=C['red'],   bg=bg, align=Qt.AlignRight),
                self._item(wr,               fg=C['cyan'],  bg=bg),
                self._item(self._dual_text(ppts, forward_ppts, decimals=2, suffix="pt"), fg=pc, bg=bg, align=Qt.AlignRight),
                self._item(self._dual_text(pkrw, forward_pkrw, suffix="원"),  fg=pc, bg=bg, align=Qt.AlignRight, bold=True),
                self._item(self._dual_text(cum, forward_cum, suffix="원"),   fg=cc, bg=bg, align=Qt.AlignRight),
            ]
            for c_idx, it in enumerate(cells):
                tbl.setItem(r_idx, c_idx, it)

    # ── 주별 테이블 ────────────────────────────────────────────

    def _build_weekly(self):
        groups  = self._group(self._week_key)[-13:]
        cum_map, c = {}, 0.0
        forward_cum_map, fc = {}, 0.0
        for wk, grp in groups:
            _, _, _, _, pkrw = self._stats(grp)
            _, _, _, _, forward_pkrw = self._stats(grp, "forward_pnl_pts", "forward_pnl_krw")
            c += pkrw
            fc += forward_pkrw
            cum_map[wk] = c
            forward_cum_map[wk] = fc

        tbl = self.tbl_weekly
        tbl.setRowCount(len(groups))
        for r_idx, (wk, grp) in enumerate(reversed(groups)):
            n, wins, losses, ppts, pkrw = self._stats(grp)
            _, _, _, forward_ppts, forward_pkrw = self._stats(grp, "forward_pnl_pts", "forward_pnl_krw")
            mdd  = self._mdd(grp)
            forward_mdd = self._mdd(grp, "forward_pnl_krw")
            cum  = cum_map[wk]
            forward_cum = forward_cum_map[wk]
            wr   = f"{wins/n*100:.0f}%" if n else "—"
            bg   = self._row_bg(pkrw)
            pc   = self._pcol(pkrw)
            cc   = self._pcol(cum)
            mc   = self._pcol(mdd)
            cells = [
                self._item(wk,               bg=bg, bold=True),
                self._item(str(n),           bg=bg, align=Qt.AlignRight),
                self._item(str(wins),        fg=C['green'], bg=bg, align=Qt.AlignRight),
                self._item(str(losses),      fg=C['red'],   bg=bg, align=Qt.AlignRight),
                self._item(wr,               fg=C['cyan'],  bg=bg),
                self._item(self._dual_text(ppts, forward_ppts, decimals=2, suffix="pt"),   fg=pc, bg=bg, align=Qt.AlignRight),
                self._item(self._dual_text(pkrw, forward_pkrw, suffix="원"),  fg=pc, bg=bg, align=Qt.AlignRight, bold=True),
                self._item(self._dual_text(cum, forward_cum, suffix="원"),   fg=cc, bg=bg, align=Qt.AlignRight),
                self._item(self._dual_text(mdd, forward_mdd, suffix="원"),   fg=mc, bg=bg, align=Qt.AlignRight),
            ]
            for c_idx, it in enumerate(cells):
                tbl.setItem(r_idx, c_idx, it)

    # ── 월별 테이블 ────────────────────────────────────────────

    def _build_monthly(self):
        groups  = self._group(lambda ts: ts[:7])
        cum_map, c = {}, 0.0
        forward_cum_map, fc = {}, 0.0
        for mon, grp in groups:
            _, _, _, _, pkrw = self._stats(grp)
            _, _, _, _, forward_pkrw = self._stats(grp, "forward_pnl_pts", "forward_pnl_krw")
            c += pkrw
            fc += forward_pkrw
            cum_map[mon] = c
            forward_cum_map[mon] = fc

        tbl = self.tbl_monthly
        tbl.setRowCount(len(groups))
        for r_idx, (mon, grp) in enumerate(reversed(groups)):
            n, wins, losses, ppts, pkrw = self._stats(grp)
            _, _, _, forward_ppts, forward_pkrw = self._stats(grp, "forward_pnl_pts", "forward_pnl_krw")
            cum  = cum_map[mon]
            forward_cum = forward_cum_map[mon]
            # 월 내 일별 PnL → 샤프
            dp = {}
            forward_dp = {}
            for r in grp:
                d = r["entry_ts"][:10]
                dp[d] = dp.get(d, 0) + r["pnl_krw"]
                forward_dp[d] = forward_dp.get(d, 0) + r["forward_pnl_krw"]
            sharpe = self._sharpe(list(dp.values()))
            forward_sharpe = self._sharpe(list(forward_dp.values()))
            wr   = f"{wins/n*100:.0f}%" if n else "—"
            bg   = self._row_bg(pkrw)
            pc   = self._pcol(pkrw)
            cc   = self._pcol(cum)
            sc   = (C['green'] if sharpe >= 1.0
                    else C['yellow'] if sharpe >= 0.5
                    else C['red']    if sharpe < 0
                    else C['text2'])
            sstr = self._dual_text(sharpe, forward_sharpe, decimals=2)
            cells = [
                self._item(mon,              bg=bg, bold=True),
                self._item(str(n),           bg=bg, align=Qt.AlignRight),
                self._item(str(wins),        fg=C['green'], bg=bg, align=Qt.AlignRight),
                self._item(str(losses),      fg=C['red'],   bg=bg, align=Qt.AlignRight),
                self._item(wr,               fg=C['cyan'],  bg=bg),
                self._item(self._dual_text(ppts, forward_ppts, decimals=2, suffix="pt"),   fg=pc, bg=bg, align=Qt.AlignRight),
                self._item(self._dual_text(pkrw, forward_pkrw, suffix="원"),  fg=pc, bg=bg, align=Qt.AlignRight, bold=True),
                self._item(self._dual_text(cum, forward_cum, suffix="원"),   fg=cc, bg=bg, align=Qt.AlignRight),
                self._item(sstr,             fg=sc, bg=bg),
            ]
            for c_idx, it in enumerate(cells):
                tbl.setItem(r_idx, c_idx, it)

    # ── 요약 카드 갱신 ─────────────────────────────────────────

    def _build_summary(self):
        if not self._rows:
            for v in self._sum.values():
                v.setText("—")
            return

        days   = len(set(r["entry_ts"][:10] for r in self._rows if r["entry_ts"]))
        trades = len(self._rows)
        wins   = sum(1 for r in self._rows if r["pnl_pts"] > 0)
        wr     = wins / trades * 100 if trades else 0
        total  = sum(r["pnl_krw"] for r in self._rows)
        forward_total = sum(r["forward_pnl_krw"] for r in self._rows)

        # 전체 MDD
        eq, peak, mdd = 0.0, 0.0, 0.0
        forward_eq, forward_peak, forward_mdd = 0.0, 0.0, 0.0
        for r in sorted(self._rows, key=lambda x: x["entry_ts"]):
            eq  += r["pnl_krw"]
            peak = max(peak, eq)
            mdd  = min(mdd, eq - peak)
            forward_eq += r["forward_pnl_krw"]
            forward_peak = max(forward_peak, forward_eq)
            forward_mdd = min(forward_mdd, forward_eq - forward_peak)

        # 최장 연승
        best, cur = 0, 0
        for r in sorted(self._rows, key=lambda x: x["entry_ts"]):
            if r["pnl_pts"] > 0:
                cur  += 1
                best  = max(best, cur)
            else:
                cur = 0

        pc = C['green'] if total >= 0 else C['red']
        wc = '#4CAF50' if wr >= 55 else (C['yellow'] if wr >= 50 else C['red'])

        def _set(key, text, col):
            lbl = self._sum[key]
            lbl.setText(text)
            lbl.setStyleSheet(
                f"color:{col};font-size:{S.f(12)}px;font-weight:bold;"
            )

        _set("days",    f"{days}일",          C['blue'])
        _set("trades",  f"{trades}건",         C['text'])
        _set("winrate", f"{wr:.1f}%",          wc)
        _set("total",   self._dual_text(total, forward_total, suffix="원"),    pc)
        _set("mdd",     self._dual_text(mdd, forward_mdd, suffix="원"),      C['orange'])
        _set("streak",  f"{best}연승",         C['yellow'])


class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    # ── 수직 구분선 헬퍼 ────────────────────────────────────────
    @staticmethod
    def _vsep():
        s = QLabel("│")
        s.setStyleSheet(f"color:{C['border']};font-size:13px;padding:0 2px;")
        return s

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── 라이브 상태 바 ──────────────────────────────────────
        sb = QFrame()
        sb.setStyleSheet(
            f"background:{C['bg2']};border-bottom:1px solid {C['border']};"
        )
        sb.setFixedHeight(S.p(28))
        sl = QHBoxLayout(sb)
        sl.setContentsMargins(S.p(8), 0, S.p(8), 0)
        sl.setSpacing(S.p(5))

        # ● 라이브 도트 + LIVE 텍스트
        self._dot = QLabel("●")
        self._dot.setStyleSheet(
            f"color:{C['green']};font-size:{S.f(12)}px;"
            f"font-family:Consolas,monospace;"
        )
        sl.addWidget(self._dot)
        lbl_live = QLabel("LIVE")
        lbl_live.setStyleSheet(
            f"color:{C['green']};font-size:{S.f(9)}px;"
            f"font-weight:bold;letter-spacing:1px;"
        )
        sl.addWidget(lbl_live)
        sl.addWidget(self._vsep())

        # 현재 시각
        self._lbl_time = QLabel("--:--:--")
        self._lbl_time.setStyleSheet(
            f"color:{C['text']};font-size:{S.f(12)}px;font-weight:bold;"
            f"font-family:Consolas,monospace;"
        )
        sl.addWidget(self._lbl_time)
        sl.addWidget(self._vsep())

        # 다음 분봉 카운트다운
        lbl_next_candle = mk_label("다음 분봉 ▷", C['text2'], 9)
        lbl_next_candle.setToolTip(_CANDLE_MONITOR_TIP)
        lbl_next_candle.setStyleSheet(
            lbl_next_candle.styleSheet()
            + "text-decoration:underline dotted;"
        )
        sl.addWidget(lbl_next_candle)

        self._cd_bar = QProgressBar()
        self._cd_bar.setRange(0, 60)
        self._cd_bar.setValue(60)
        self._cd_bar.setFixedHeight(S.p(7))
        self._cd_bar.setFixedWidth(S.p(60))
        self._cd_bar.setTextVisible(False)
        self._cd_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg3']};border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{C['cyan']};border-radius:3px;}}"
        )
        self._cd_bar.setToolTip(_CANDLE_MONITOR_TIP)
        sl.addWidget(self._cd_bar)

        self._lbl_cd = QLabel("60초")
        self._lbl_cd.setFixedWidth(S.p(38))
        self._lbl_cd.setStyleSheet(
            f"color:{C['cyan']};font-size:{S.f(12)}px;font-weight:bold;"
            f"font-family:Consolas,monospace;"
        )
        self._lbl_cd.setToolTip(_CANDLE_MONITOR_TIP)
        sl.addWidget(self._lbl_cd)
        sl.addWidget(self._vsep())

        # 마지막 갱신 경과
        lbl_last_update = mk_label("↑ 마지막 갱신", C['text2'], 9)
        lbl_last_update.setToolTip(_CANDLE_MONITOR_TIP)
        lbl_last_update.setStyleSheet(
            lbl_last_update.styleSheet()
            + "text-decoration:underline dotted;"
        )
        sl.addWidget(lbl_last_update)

        self._lbl_elapsed = QLabel("—")
        self._lbl_elapsed.setFixedWidth(S.p(70))
        self._lbl_elapsed.setStyleSheet(
            f"color:{C['text2']};font-size:{S.f(12)}px;font-weight:bold;"
            f"font-family:Consolas,monospace;"
        )
        self._lbl_elapsed.setToolTip(_CANDLE_MONITOR_TIP)
        sl.addWidget(self._lbl_elapsed)

        sl.addStretch()
        lay.addWidget(sb)
        lay.addSpacing(S.p(3))

        # ── 상태 바 타이머 (500ms) ──────────────────────────────
        self._last_update_time = None
        self._dot_phase        = 0
        self._status_timer     = QTimer()
        self._status_timer.setInterval(500)
        self._status_timer.timeout.connect(self._tick_status)
        self._status_timer.start()

        # ── 탭 ─────────────────────────────────────────────────
        self.tabs = QTabWidget()
        log_configs = [
            ("1 시스템",  C['blue'],   "all"),
            ("2 경보 ⚠",  C['orange'], "warn"),
            ("3 주문/체결",C['green'],  "order"),
            ("4 손익 PnL", C['cyan'],   "pnl"),
            ("5 모델 AI",  C['purple'], "model"),
        ]
        self.log_boxes = {}
        for title, col, key in log_configs:
            page = QWidget()
            pl   = QVBoxLayout(page)
            pl.setContentsMargins(4, 4, 4, 4)

            # 상단 메트릭 (창3, 4, 5 전용)
            if key == "order":
                mrow = QHBoxLayout()
                self._order_vals = {}
                for om_lbl, om_attr, om_init in [
                    ("당일 거래",  "trades",   "0건"),
                    ("평균 지연",  "avg_lat",  "——ms"),
                    ("최대 지연",  "peak_lat", "——ms"),
                    ("수신 횟수",  "samples",  "0회"),
                ]:
                    mf = QFrame()
                    mf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    mfl = QVBoxLayout(mf); mfl.setContentsMargins(5,3,5,3)
                    mfl.addWidget(mk_label(om_lbl, C['text2'], 10, align=Qt.AlignCenter))
                    vl = mk_val_label(om_init, col, 13, align=Qt.AlignCenter)
                    mfl.addWidget(vl)
                    mrow.addWidget(mf)
                    self._order_vals[om_attr] = vl
                pl.addLayout(mrow)

            elif key == "pnl":
                mrow = QHBoxLayout()
                self._pnl_vals = {}   # 업데이트용 라벨 참조
                self._pnl_bars = {}
                for mk_lbl, attr, mc in [
                    ("미실현 손익", "unrealized", C['cyan']),
                    ("일일 누적",   "daily",      C['green']),
                    ("VaR 95%",    "var",         C['orange']),
                ]:
                    mf = QFrame()
                    mf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    mfl = QVBoxLayout(mf); mfl.setContentsMargins(5,3,5,3)
                    title_lbl = mk_label(mk_lbl, C['text2'], 10, align=Qt.AlignCenter)
                    if attr == "var":
                        mf.setToolTip(_VAR_TIP)
                        title_lbl.setToolTip(_VAR_TIP)
                        title_lbl.setStyleSheet(
                            f"color:{C['text2']};font-size:{S.f(10)}px;"
                            f"text-decoration:underline dotted;"
                        )
                    mfl.addWidget(title_lbl)
                    pb = mk_prog(mc, 4)
                    pb.setValue(0)
                    vl = mk_val_label("——원", mc, 13, align=Qt.AlignCenter)
                    mfl.addWidget(vl)
                    mfl.addWidget(pb)
                    mrow.addWidget(mf)
                    self._pnl_vals[attr] = vl
                    self._pnl_bars[attr] = pb
                pl.addLayout(mrow)

            elif key == "model":
                mrow = QHBoxLayout()
                for mk_lbl, mk_val, mc in [("정확도(50분)","61.4%",C['green']),
                                             ("SGD 비중","34%",C['purple']),
                                             ("자가학습","● 활성",C['green'])]:
                    mf = QFrame()
                    mf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    mfl = QVBoxLayout(mf); mfl.setContentsMargins(5,3,5,3)
                    mfl.addWidget(mk_label(mk_lbl, C['text2'], 10, align=Qt.AlignCenter))
                    mfl.addWidget(mk_val_label(mk_val, mc, 13, align=Qt.AlignCenter))
                    mrow.addWidget(mf)
                pl.addLayout(mrow)

            tb = QTextEdit()
            tb.setReadOnly(True)
            tb.setStyleSheet(
                f"background:{C['bg']};color:{C['text']};border:none;"
                f"font-family:Consolas,D2Coding,monospace;font-size:{S.f(12)}px;"
            )
            pl.addWidget(tb)
            self.log_boxes[key] = tb
            self.tabs.addTab(page, title)
            # 탭 색상
            self.tabs.tabBar().setTabTextColor(
                self.tabs.count()-1, QColor(col)
            )
            if key == "order":
                self.tabs.setTabToolTip(self.tabs.count()-1, _ORDER_TAB_TIP)

        # 6번째 탭: 손익 추이 (일별·주별·월별 누적 테이블)
        self.pnl_history = PnlHistoryPanel()
        self.tabs.addTab(self.pnl_history, "📊 손익 추이")
        self.tabs.tabBar().setTabTextColor(self.tabs.count() - 1, QColor(C['cyan']))

        lay.addWidget(self.tabs)

    def refresh_pnl_history(self, rows):
        """손익 추이 탭 전체 갱신 (trades.db rows)."""
        self.pnl_history.refresh(rows)

    def update_order_metrics(self, trades: int, avg_lat_ms: float, peak_lat_ms: float, samples: int):
        """창3 주문/체결 탭 상단 지표 갱신."""
        if not hasattr(self, "_order_vals"):
            return
        self._order_vals["trades"].setText(f"{trades}건")
        for attr, val_ms, warn_ms in [
            ("avg_lat",  avg_lat_ms,  500),
            ("peak_lat", peak_lat_ms, 1000),
        ]:
            lbl = self._order_vals[attr]
            if val_ms > 0:
                text = f"{val_ms:.0f}ms"
                c = C['green'] if val_ms < warn_ms else C['orange']
            else:
                text = "——ms"
                c = C['text2']
            lbl.setText(text)
            lbl.setStyleSheet(f"color:{c};font-size:{S.f(13)}px;font-weight:bold;")
        self._order_vals["samples"].setText(f"{samples}회")

    def update_pnl_metrics(self, unrealized_krw: float, daily_pnl_krw: float, var_krw: float,
                           forward_unrealized_krw: float = None, forward_daily_pnl_krw: float = None):
        """미실현 손익·일일 누적·VaR 95% 수치 갱신."""
        forward_unrealized_krw = unrealized_krw if forward_unrealized_krw is None else forward_unrealized_krw
        forward_daily_pnl_krw = daily_pnl_krw if forward_daily_pnl_krw is None else forward_daily_pnl_krw
        data = {
            "unrealized": ((unrealized_krw, forward_unrealized_krw), C['green'] if unrealized_krw >= 0 else C['red']),
            "daily": ((daily_pnl_krw, forward_daily_pnl_krw), C['green'] if daily_pnl_krw >= 0 else C['red']),
            "var": (var_krw, C['orange']),
        }
        for attr, (val, col) in data.items():
            lbl = self._pnl_vals.get(attr)
            pb = self._pnl_bars.get(attr)
            if lbl:
                if attr == "var":
                    lbl.setText(f"{val:+,.0f}원")
                else:
                    lbl.setText(f"실행 {val[0]:+,.0f}원\n순방향 {val[1]:+,.0f}원")
                lbl.setStyleSheet(f"color:{col};font-size:{S.f(13)}px;font-weight:bold;")
            if pb and attr != "var":
                pct = min(100, max(0, int(abs(val[0]) / 50_000 * 50 + 50)))
                pb.setValue(pct)

    @staticmethod
    def _insert_html_left(tb: QTextEdit, html: str) -> None:
        """QTextEdit에 HTML을 좌측 정렬 블록으로 삽입.

        tb.append()는 이전 블록의 alignment를 상속하므로
        QTextCursor로 블록 포맷을 명시적으로 Qt.AlignLeft로 지정한다.
        """
        fmt = QTextBlockFormat()
        fmt.setAlignment(Qt.AlignLeft)

        cursor = tb.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock(fmt)
        cursor.insertHtml(html)

        tb.setTextCursor(cursor)
        tb.verticalScrollBar().setValue(tb.verticalScrollBar().maximum())

    @staticmethod
    def _insert_html_center(tb: QTextEdit, html: str) -> None:
        """HTML을 가운데 정렬 블록으로 삽입 (구분선용)."""
        fmt = QTextBlockFormat()
        fmt.setAlignment(Qt.AlignCenter)

        cursor = tb.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock(fmt)
        cursor.insertHtml(html)

        tb.setTextCursor(cursor)
        tb.verticalScrollBar().setValue(tb.verticalScrollBar().maximum())

    def append(self, key, tag, msg, val=""):
        self._last_update_time = datetime.now()
        tb = self.log_boxes.get(key)
        if not tb:
            return

        # WARN/ERROR/CRITICAL → 경보탭 전용 (1 시스템 탭에는 기록하지 않음)
        if key == "all" and tag in ("WARN", "ERROR", "CRITICAL"):
            self.append("warn", tag, msg, val)
            return

        ts  = self._last_update_time.strftime("%H:%M:%S")
        TAG_COLORS = {
            "INFO":   C['blue'],   "DEBUG": C['text2'], "SYSTEM": C['purple'],
            "WARN":   C['orange'], "ERROR": C['red'],   "CRITICAL": C['red'],
            "TRADE":  C['green'],  "FILL":  C['green'], "PENDING": C['orange'],
            "CANCEL": C['red'],    "PNL":   C['cyan'],  "MODEL":  C['purple'],
            "SHAP":   C['yellow'],
        }
        col = TAG_COLORS.get(tag, C['text2'])
        html = (
            f'<span style="color:{C["text2"]}">[{ts}]</span> '
            f'<span style="color:{col};font-weight:bold">[{tag}]</span> '
            f'<span style="color:{C["text"]}">{msg}</span>'
        )
        if val:
            html += f' <span style="color:{C["text2"]};font-size:{S.f(11)}px;">{val}</span>'

        self._insert_html_left(tb, html)

    def append_restore(self, key: str, msg: str, ts: str = "", val: str = ""):
        """재시작 복원 항목 — 이탤릭·회색으로 실시간 항목과 시각 구분."""
        tb = self.log_boxes.get(key)
        if not tb:
            return
        ts_disp = ts if ts else datetime.now().strftime("%H:%M:%S")
        val_html = (
            f' <span style="color:{C["text2"]};font-size:{S.f(11)}px;">{val}</span>'
            if val else ""
        )
        html = (
            f'<span style="color:{C["text2"]};font-style:italic;">'
            f'[{ts_disp}]'
            f' <span style="color:{C["yellow"]};font-weight:bold;">[복원]</span>'
            f' {msg}'
            f'{val_html}'
            f'</span>'
        )
        self._insert_html_left(tb, html)

    def append_separator(self, key: str, msg: str = ""):
        """탭 내 수평선 구분자 (복원 이력 / 신규 세션 경계 등)."""
        tb = self.log_boxes.get(key)
        if not tb:
            return
        html = (
            f'<span style="color:{C["border"]};">───────────────────────────────────────</span>'
            f'<br><span style="color:{C["text2"]};font-size:{S.f(10)}px;font-style:italic;">'
            f'{msg}</span>'
        )
        self._insert_html_center(tb, html)

    # ── 상태 바 틱 (500ms) ─────────────────────────────────────

    def _tick_status(self):
        now = datetime.now()

        # ● 도트 깜빡임
        self._dot_phase ^= 1
        dot_col = C['green'] if self._dot_phase == 0 else C['bg3']
        self._dot.setStyleSheet(
            f"color:{dot_col};font-size:{S.f(12)}px;font-family:Consolas,monospace;"
        )

        # 현재 시각
        self._lbl_time.setText(now.strftime("%H:%M:%S"))

        # 카운트다운 — 다음 분봉까지 남은 초
        remaining = 60 - now.second
        self._cd_bar.setValue(remaining)
        self._lbl_cd.setText(f"{remaining:2d}초")

        if remaining <= 5:
            cd_col = C['red']
        elif remaining <= 15:
            cd_col = C['yellow']
        else:
            cd_col = C['cyan']
        self._lbl_cd.setStyleSheet(
            f"color:{cd_col};font-size:{S.f(12)}px;font-weight:bold;"
            f"font-family:Consolas,monospace;"
        )
        self._cd_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg3']};border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{cd_col};border-radius:3px;}}"
        )

        # 마지막 갱신 경과
        if self._last_update_time:
            elapsed = int((now - self._last_update_time).total_seconds())
            if elapsed < 60:
                elapsed_str = f"{elapsed}초 전"
            elif elapsed < 3600:
                m, s = divmod(elapsed, 60)
                elapsed_str = f"{m}분 {s:02d}초"
            else:
                elapsed_str = f"{elapsed // 3600}시간+"
            if elapsed < 90:
                el_col = C['green']
            elif elapsed < 300:
                el_col = C['yellow']
            else:
                el_col = C['red']
            self._lbl_elapsed.setText(elapsed_str)
            self._lbl_elapsed.setStyleSheet(
                f"color:{el_col};font-size:{S.f(12)}px;font-weight:bold;"
                f"font-family:Consolas,monospace;"
            )

    def notify_update(self):
        """파이프라인 실행 완료 시 마지막 갱신 시각을 명시적으로 리셋."""
        self._last_update_time = datetime.now()


# ────────────────────────────────────────────────────────────
# 메인 윈도우
# ────────────────────────────────────────────────────────────
class MireukDashboard(QMainWindow):
    """미륵이 v7.0 풀 대시보드"""

    def __init__(self, kiwoom=None):
        super().__init__()
        self.kiwoom    = kiwoom
        self._start_dt = datetime.now()        # 프로그램 시작 시각 (불변)
        # ── 해상도 감지 (UI 빌드 전에 반드시 먼저) ──────────────
        S.init()
        self.setWindowTitle("미륵이 v7.0  |  KOSPI 200 선물 예측 시스템")
        # availableGeometry 기준으로 창 크기/위치 고정 — 태스크바 잘림 방지
        _avail = QApplication.instance().primaryScreen().availableGeometry()
        _win_w = min(S.p(1680), _avail.width())
        _win_h = min(S.p(1000), _avail.height())
        self.setGeometry(_avail.x(), _avail.y(), _win_w, _win_h)
        self.setStyleSheet(make_style())
        self._build_ui()

        # ── 헤더 시계 (1초 갱신) ─────────────────────────────────
        self._header_timer = QTimer(self)
        self._header_timer.setInterval(1000)
        self._header_timer.timeout.connect(self._tick_header)
        self._header_timer.start()

        # ── 위클리 배지 (1분 갱신 — 날짜 전환 대비) ─────────────
        self._cycle_timer = QTimer(self)
        self._cycle_timer.setInterval(60_000)
        self._cycle_timer.timeout.connect(self._refresh_cycle_badge)
        self._cycle_timer.start()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(6)

        # ── 상단 헤더 ──────────────────────────────────────────
        header = QHBoxLayout()
        title = mk_label("⚡ 미륵이  v7.0", C['text'], 16, True)
        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(S.p(4))

        # ── 실시간 현재가 (키움 API 연동 핵심) ──────────────────
        self.lbl_realtime_price = mk_label("——.——", C['cyan'], 22, True)
        self.lbl_price_change   = mk_label("——", C['text2'], 14, True)
        self.lbl_futures_code   = mk_label("F202606", C['text2'], 11)

        price_box = QHBoxLayout()
        price_box.setSpacing(S.p(6))
        price_box.addWidget(self.lbl_futures_code)
        price_box.addWidget(self.lbl_realtime_price)
        price_box.addWidget(self.lbl_price_change)

        # 상태 배지
        self.lbl_regime = mk_badge("NEUTRAL", C['orange'], "#fff", 11)
        _cyc_text, _cyc_col = _calc_cycle_badge()
        self.lbl_cycle  = mk_badge(_cyc_text, _cyc_col, "#fff", 11)
        self.lbl_gamma  = mk_badge("감마스퀴즈", C['orange'], "#fff", 11)
        self.lbl_pos    = mk_badge("FLAT", C['text2'], "#fff", 11)

        # ── 우측 시계 블록 ─────────────────────────────────────
        clk_frame = QFrame()
        clk_frame.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};"
            f"border-radius:5px;padding:2px 6px;"
        )
        clk_lay = QVBoxLayout(clk_frame)
        clk_lay.setContentsMargins(6, 2, 6, 2)
        clk_lay.setSpacing(1)

        # 시작 시각 (소형, 고정)
        start_row = QHBoxLayout()
        start_row.setSpacing(4)
        start_row.addWidget(mk_label("시작", C['text2'], 9))
        self.lbl_start = mk_label(
            self._start_dt.strftime("%H:%M:%S"), C['text2'], 10,
            align=Qt.AlignRight
        )
        start_row.addWidget(self.lbl_start)
        clk_lay.addLayout(start_row)

        # 가동 경과 (중형, 실시간 갱신 — 현재시각은 하단 상태 바와 중복이므로 제거)
        run_row = QHBoxLayout()
        run_row.setSpacing(4)
        run_row.addWidget(mk_label("가동", C['cyan'], 9))
        self.lbl_elapsed_run = mk_label(
            "0m 00s", C['text'], S.f(13), bold=True, align=Qt.AlignRight
        )
        self.lbl_elapsed_run.setStyleSheet(
            f"color:{C['text']};font-size:{S.f(13)}px;"
            f"font-weight:bold;font-family:Consolas,monospace;"
        )
        run_row.addWidget(self.lbl_elapsed_run)
        clk_lay.addLayout(run_row)

        # ── 파이프라인 생존 표시 (1초 갱신) ──────────────────────
        pipe_row = QHBoxLayout()
        pipe_row.setSpacing(4)
        lbl_pipe = mk_label("분봉", C['text2'], 9)
        lbl_pipe.setToolTip(_PIPE_HEALTH_TIP)
        lbl_pipe.setStyleSheet(
            lbl_pipe.styleSheet() + "text-decoration:underline dotted;"
        )
        pipe_row.addWidget(lbl_pipe)
        self._pipe_bar = QProgressBar()
        self._pipe_bar.setRange(0, 120)          # 최대 2분 표시
        self._pipe_bar.setValue(0)
        self._pipe_bar.setTextVisible(False)
        self._pipe_bar.setFixedHeight(S.p(6))
        self._pipe_bar.setFixedWidth(S.p(56))
        self._pipe_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg']};border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{C['cyan']};border-radius:3px;}}"
        )
        self._pipe_bar.setToolTip(_PIPE_HEALTH_TIP)
        pipe_row.addWidget(self._pipe_bar)
        self._lbl_pipe_ago = mk_label("── 대기", C['text2'], 9, align=Qt.AlignRight)
        self._lbl_pipe_ago.setToolTip(_PIPE_HEALTH_TIP)
        pipe_row.addWidget(self._lbl_pipe_ago)
        clk_lay.addLayout(pipe_row)

        self._pipe_elapsed_s: int = 0            # 마지막 파이프라인 이후 경과초
        self._watchdog_alerted: set = set()    # 이미 발동한 임계값 (60/120/180s)
        self._pipeline_recovery_cb = None      # main.py가 등록하는 복구 콜백

        self.lbl_clock = None   # 제거됨 — _tick_header() 참조용 유지

        # ── 해상도·커밋 블록 ───────────────────────────────────
        self.lbl_scale  = mk_label(S.info(),    C['text2'], 9, align=Qt.AlignRight)
        self.lbl_commit = mk_label(COMMIT_HASH, C['text2'], 9, align=Qt.AlignRight)
        header_label_w = S.p(58)
        header_combo_w = S.p(188)
        header_btn_w = S.p(54)
        acct_row = QHBoxLayout()
        acct_row.setContentsMargins(0, 0, 0, 0)
        acct_row.setSpacing(S.p(4))
        self.lbl_account = mk_label("계좌번호:", C['text2'], 9, align=Qt.AlignRight)
        self.lbl_account.setFixedWidth(header_label_w)
        self.cmb_account = QComboBox()
        self.cmb_account.setFixedWidth(header_combo_w)
        self.cmb_account.setStyleSheet(
            f"QComboBox{{background:{C['bg2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;"
            f"padding:2px 6px;font-size:{S.f(9)}px;}}"
            f"QComboBox QAbstractItemView{{background:{C['bg2']};color:{C['text']};"
            f"selection-background-color:{C['blue']};}}"
        )
        self.btn_save_account = QPushButton("저장")
        self.btn_save_account.setFixedWidth(header_btn_w)
        self.btn_save_account.setCursor(Qt.PointingHandCursor)
        self.btn_save_account.setStyleSheet(
            f"QPushButton{{background:{C['blue']};color:#fff;border:none;"
            f"border-radius:4px;padding:3px 8px;font-size:{S.f(9)}px;font-weight:bold;}}"
            f"QPushButton:disabled{{background:{C['bg']};color:{C['text2']};}}"
        )
        acct_row.addWidget(self.lbl_account)
        acct_row.addWidget(self.cmb_account)
        acct_row.addWidget(self.btn_save_account)
        acct_row.addStretch()
        strat_row = QHBoxLayout()
        strat_row.setContentsMargins(0, 0, 0, 0)
        strat_row.setSpacing(S.p(4))
        self.lbl_strategy = mk_label("전략명:", C['text2'], 9, align=Qt.AlignRight)
        self.lbl_strategy.setFixedWidth(header_label_w)
        self.cmb_strategy = QComboBox()
        self.cmb_strategy.setFixedWidth(header_combo_w)
        self.cmb_strategy.setStyleSheet(
            f"QComboBox{{background:{C['bg2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;"
            f"padding:2px 6px;font-size:{S.f(9)}px;}}"
            f"QComboBox QAbstractItemView{{background:{C['bg2']};color:{C['text']};"
            f"selection-background-color:{C['blue']};}}"
        )
        self.cmb_strategy.addItem("")
        self.btn_save_strategy = QPushButton("저장")
        self.btn_save_strategy.setFixedWidth(header_btn_w)
        self.btn_save_strategy.setCursor(Qt.PointingHandCursor)
        self.btn_save_strategy.setStyleSheet(
            f"QPushButton{{background:{C['blue']};color:#fff;border:none;"
            f"border-radius:4px;padding:3px 8px;font-size:{S.f(9)}px;font-weight:bold;}}"
            f"QPushButton:disabled{{background:{C['bg']};color:{C['text2']};}}"
        )
        strat_row.addWidget(self.lbl_strategy)
        strat_row.addWidget(self.cmb_strategy)
        strat_row.addWidget(self.btn_save_strategy)
        strat_row.addStretch()
        title_box.addWidget(title)
        title_box.addLayout(acct_row)
        title_box.addLayout(strat_row)
        res_box = QVBoxLayout()
        res_box.setSpacing(0)
        res_box.setContentsMargins(0, 0, 0, 0)
        res_box.addWidget(self.lbl_scale)
        res_box.addWidget(self.lbl_commit)

        header.addLayout(title_box)
        header.addLayout(price_box)
        header.addStretch()
        for w in [self.lbl_regime, self.lbl_cycle, self.lbl_gamma, self.lbl_pos]:
            header.addWidget(w)
        header.addWidget(clk_frame)
        header.addLayout(res_box)
        root.addLayout(header)
        root.addWidget(mk_sep())

        # ── 3열 메인 레이아웃 ──────────────────────────────────
        main_split = QSplitter(Qt.Horizontal)
        main_split.setHandleWidth(3)
        main_split.setStyleSheet(f"QSplitter::handle{{background:{C['border']};}}")

        # 좌측 컬럼
        left = QWidget()
        ll   = QVBoxLayout(left)
        ll.setContentsMargins(0,0,0,0)
        ll.setSpacing(6)
        left_split = QSplitter(Qt.Vertical)
        left_split.setHandleWidth(3)
        left_split.setStyleSheet(f"QSplitter::handle{{background:{C['border']};}}")
        self.account_info_panel = AccountInfoPanel()
        self.pred_panel = PredictionPanel()
        left_split.addWidget(card("실시간 잔고",
                                  self.account_info_panel, C['cyan'],
                                  header_widget=self.account_info_panel.live_header_widget))
        left_split.addWidget(card("멀티 호라이즌 예측 + 파라미터 분석",
                                  self.pred_panel, C['blue']))
        left_split.setSizes([420, 520])
        ll.addWidget(left_split, 1)

        # 중앙 컬럼 (탭)
        mid  = QWidget()
        ml   = QVBoxLayout(mid)
        ml.setContentsMargins(0,0,0,0)
        ml.setSpacing(6)
        self.mid_tabs = QTabWidget()
        self.mid_tabs.setStyleSheet(f"QTabBar::tab:selected{{border-bottom:2px solid {C['orange']};}}")

        self.div_panel      = DivergencePanel()
        self.feat_panel     = FeaturePanel()
        self.exit_panel     = ExitPanel()
        self.entry_panel    = EntryPanel()
        self.learn_panel    = LearningPanel()
        self.efficacy_panel = EfficacyPanel()
        self.trend_panel    = TrendPanel()
        self.alpha_panel    = AlphaPanel()

        # 🧭 전략 운용현황 패널 (strategy_registry + drift_detector 연동)
        try:
            from dashboard.strategy_dashboard_tab import StrategyPanel
            self.strategy_panel = StrategyPanel()
        except Exception as _e:
            logger.warning("[Dashboard] StrategyPanel 로드 실패: %s", _e)
            self.strategy_panel = None

        self.mid_tabs.addTab(self._wrap(self.div_panel),      "다이버전스 + 포지션")
        self.mid_tabs.addTab(self._wrap(self.feat_panel),     "동적 피처 (SHAP)")
        self.mid_tabs.addTab(self._wrap(self.exit_panel),     "청산 관리")
        self.mid_tabs.addTab(self._wrap(self.entry_panel),    "진입 관리")
        self.mid_tabs.setTabToolTip(self.mid_tabs.count() - 1, _CB_TIP)
        self.mid_tabs.addTab(self._wrap(self.learn_panel),    "🧠 자가학습")
        self.mid_tabs.addTab(self._wrap(self.efficacy_panel), "🎯 효과 검증")
        self.mid_tabs.addTab(self._wrap(self.trend_panel),    "📈 성장 추이")
        self.mid_tabs.addTab(self._wrap(self.alpha_panel),    "알파 리서치 봇")
        if self.strategy_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.strategy_panel), "🧭 전략 운용현황")
        ml.addWidget(self.mid_tabs)

        # 우측: 5층 로그
        right = QWidget()
        rl    = QVBoxLayout(right)
        rl.setContentsMargins(0,0,0,0)
        self.log_panel = LogPanel()
        rl.addWidget(card("5층 모니터링 로그", self.log_panel, C['text2']))

        main_split.addWidget(left)
        main_split.addWidget(mid)
        main_split.addWidget(right)
        main_split.setSizes([520, 680, 440])
        root.addWidget(main_split, 1)

        self.ui_auto_tabs = UiAutoTabController(self.log_panel.tabs, self.mid_tabs)
        self.ui_auto_tabs.set_startup_mode()

    def _wrap(self, widget):
        sc = QScrollArea()
        sc.setWidget(widget)
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.NoFrame)
        widget.setMinimumWidth(S.p(500))
        return sc

    def update_price(self, price: float, change: float = 0.0,
                     code: str = "F202606"):
        """
        키움 API 실시간 현재가 반영
        main.py 의 _on_candle_closed 콜백에서 호출

        Args:
            price:  현재가 (예: 1003.30)
            change: 전일 대비 등락 (예: +3.10)
            code:   선물 코드 (예: F202606, A0166000)
        """
        self.lbl_realtime_price.setText(f"{price:,.2f}")
        col = C['green'] if change >= 0 else C['red']
        sign = "▲" if change >= 0 else "▼"
        self.lbl_price_change.setText(f"{sign} {abs(change):.2f}")
        self.lbl_price_change.setStyleSheet(
            f"font-size:{S.f(14)}px;color:{col};font-weight:bold;"
        )
        self.lbl_realtime_price.setStyleSheet(
            f"font-size:{S.f(22)}px;color:{col};font-weight:bold;"
        )
        self.lbl_futures_code.setText(code)
        # 예측 패널 현재가도 동기화
        self.pred_panel.lbl_price.setText(f"{price:,.2f}")
        self.pred_panel.lbl_price.setStyleSheet(
            f"font-size:{S.f(20)}px;color:{col};font-weight:bold;"
        )

    # ── 시뮬레이션 타이머 ──────────────────────────────────────
    # ── 헤더 시계·위클리 배지 갱신 ────────────────────────────

    def _tick_header(self):
        """1초마다 헤더 가동 경과시간 + 파이프라인 생존 바 갱신."""
        if hasattr(self, "account_info_panel"):
            self.account_info_panel.tick_live()
        now     = datetime.now()
        total_s = int((now - self._start_dt).total_seconds())
        h, rem  = divmod(total_s, 3600)
        m, s    = divmod(rem, 60)

        if h > 0:
            elapsed_str = f"{h}h {m:02d}m {s:02d}s"
        else:
            elapsed_str = f"{m}m {s:02d}s"
        self.lbl_elapsed_run.setText(elapsed_str)

        # ── 파이프라인 생존 바 ──────────────────────────────────
        self._pipe_elapsed_s += 1
        ps = self._pipe_elapsed_s

        # 색상: 60초 이내=cyan, 60~120초=orange, 120초 초과=red
        if ps <= 60:
            chunk_col = C['cyan']
        elif ps <= 120:
            chunk_col = C['orange']
        else:
            chunk_col = C['red']

        self._pipe_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg']};border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{chunk_col};border-radius:3px;}}"
        )
        self._pipe_bar.setValue(min(ps, 120))

        # 텍스트: "Xs 전" or "Xm Ys 전"
        if ps < 60:
            ago_str = f"{ps}s 전"
            ago_col = C['cyan']
        elif ps < 3600:
            ago_str = f"{ps // 60}m {ps % 60:02d}s 전"
            ago_col = C['orange'] if ps < 120 else C['red']
        else:
            ago_str = "1h+ 전"
            ago_col = C['red']

        self._lbl_pipe_ago.setText(ago_str)
        self._lbl_pipe_ago.setStyleSheet(
            f"color:{ago_col};font-size:{S.f(9)}px;"
        )

        # ── 파이프라인 감시 — 임계값 초과 시 복구 콜백 발동 (1회씩) ──
        # 1분봉 주기=60s이므로 첫 경보 임계값을 90s로 설정 (race condition 방지)
        # 콜백 실행 후에만 임계값 소비 — 콜백 미등록 시 threshold를 소비하면
        # 나중에 콜백이 등록돼도 해당 임계값이 영구 누락되는 버그 방지
        for threshold in (90, 150, 240):
            if ps >= threshold and threshold not in self._watchdog_alerted:
                if self._pipeline_recovery_cb:
                    self._pipeline_recovery_cb(ps)
                    self._watchdog_alerted.add(threshold)  # 실행 확인 후 소비
                break  # 한 틱에 하나씩만 처리

    def _refresh_cycle_badge(self):
        """위클리/월간 D-days 배지를 날짜 변화에 맞춰 갱신."""
        text, col = _calc_cycle_badge()
        self.lbl_cycle.setText(text)
        self.lbl_cycle.setStyleSheet(
            f"background:{col};color:#fff;border-radius:3px;"
            f"padding:1px {S.p(5)}px;font-size:{S.f(11)}px;font-weight:bold;"
        )



# ────────────────────────────────────────────────────────────
# main.py 인터페이스 어댑터
# ────────────────────────────────────────────────────────────
class DashboardAdapter:
    """
    main.py 가 사용하는 메서드를 MireukDashboard 에 연결하는 어댑터

    main.py 호출 패턴:
        self.dashboard = create_dashboard()
        self.dashboard.show()
        self.dashboard.append_sys_log(msg)
        self.dashboard.update_supply_macro(vix, sp500_chg, regime)
        self.dashboard.update_system_status(cb_state, latency_ms)
        self.dashboard.btn_kill  (QPushButton 참조)
    """

    def __init__(self):
        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyle("Fusion")
        self._win = MireukDashboard()
        # 긴급 정지 버튼을 외부에서 접근할 수 있도록 노출
        self.btn_kill = self._win._make_kill_btn()
        self.btn_save_account = self._win.btn_save_account
        self.sig_position_restore = self._win.account_info_panel.sig_position_restore
        self.sig_reverse_entry_toggled = self._win.entry_panel.sig_reverse_entry_toggled

    # ── 필수 메서드 ────────────────────────────────────────────
    def show(self):
        self._win.showMaximized()

    def append_sys_log(self, msg: str):
        """창1 시스템 로그에 메시지 추가"""
        self._win.log_panel.append("all", "SYSTEM", msg)

    def set_ui_startup_mode(self) -> None:
        self._win.ui_auto_tabs.set_startup_mode()

    def set_ui_ready_mode(self) -> None:
        self._win.ui_auto_tabs.set_ready_mode()

    def set_ui_position_mode(self) -> None:
        self._win.ui_auto_tabs.set_position_mode()

    def set_account_options(self, accounts, selected: str = ""):
        combo = self._win.cmb_account
        cur = selected or combo.currentText().strip()
        vals = [str(a).strip() for a in accounts if str(a).strip()]
        if cur and cur not in vals and not vals:
            vals.insert(0, cur)
        combo.blockSignals(True)
        combo.clear()
        if vals:
            combo.addItems(vals)
            if selected and selected in vals:
                combo.setCurrentText(selected)
            else:
                combo.setCurrentIndex(0)
        else:
            combo.addItem(cur or "")
        combo.blockSignals(False)

    def get_selected_account(self) -> str:
        return self._win.cmb_account.currentText().strip()

    def update_account_balance(self, summary: dict, rows, quiet: bool = False, mark_fresh: bool = True, source: str = "broker", balance_active: bool = True):
        if not quiet:
            logger.warning(
                "[BalanceUI] dashboard receive rows=%d summary_nonblank=%s preview=%s summary=%s",
                len(rows or []),
                any(str(v).strip() for v in (summary or {}).values()),
                list(rows or [])[:3],
                summary or {},
            )
        self._win.account_info_panel.update_summary(summary)
        self._win.account_info_panel.update_rows(rows)
        if mark_fresh:
            self._win.account_info_panel.notify_balance_update(source=source, active=balance_active)

    def update_supply_macro(
        self,
        vix: float = 0.0,
        sp500_chg: float = 0.0,
        usd_krw: float = 0.0,
        regime: str = "NEUTRAL",
    ):
        """수급/매크로 섹션 업데이트"""
        # 헤더 레짐 배지 갱신
        col_map = {
            "RISK_ON":  C['green'],
            "NEUTRAL":  C['orange'],
            "RISK_OFF": C['red'],
        }
        col = col_map.get(regime, C['orange'])
        self._win.lbl_regime.setText(regime)
        self._win.lbl_regime.setStyleSheet(
            f"background:{col};color:#fff;border-radius:3px;"
            f"font-size:{S.f(11)}px;font-weight:bold;padding:1px 6px;"
        )
        # 로그에도 기록
        self._win.log_panel.append(
            "all", "INFO",
            f"[Regime] {regime} | VIX={vix:.1f} | SP500={sp500_chg:+.2%} | USD/KRW={usd_krw:+.2f}"
        )

    def update_system_status(
        self,
        cb_state: str = "NORMAL",
        latency_ms: float = 0.0,
        accuracy: float = 0.0,
    ):
        """시스템 상태 (Circuit Breaker, 지연, 정확도) 업데이트"""
        col = C['green'] if cb_state == "NORMAL" else C['red']
        self._win.log_panel.append(
            "model", "SYSTEM",
            f"CB={cb_state} | API지연={latency_ms:.0f}ms | 정확도={accuracy:.1%}"
        )

    def update_position(self, pos_data: dict):
        """청산 패널 포지션 데이터 업데이트"""
        self._win.exit_panel.update_data(pos_data)

    def update_price(self, price: float, change: float = 0.0,
                     code: str = "F202606"):
        """
        키움 실시간 현재가 → 헤더 + 예측 패널 동시 반영

        main.py _on_candle_closed 콜백에서 호출:
            self.dashboard.update_price(
                price  = bar['close'],
                change = bar['close'] - bar.get('prev_close', bar['close']),
                code   = self.realtime_data.code,
            )
        """
        self._win.update_price(price, change, code)

    def update_prediction(self, price: float, preds: dict, params: dict,
                          conf: float = None, corr: str = ""):
        """멀티 호라이즌 예측 패널 업데이트"""
        self._win.pred_panel.update_data(price, preds, params, conf, corr)

    def update_entry(self, signal: str, conf: float, grade: str, checks: dict,
                     qty: int = 0, final_signal: str = None,
                     reverse_enabled: bool = False):
        """진입 관리 패널 업데이트"""
        self._win.entry_panel.update_data(
            signal, conf, grade, checks, qty=qty,
            final_signal=final_signal,
            reverse_enabled=reverse_enabled,
        )

    def set_reverse_entry_enabled(self, enabled: bool, emit_signal: bool = False) -> None:
        self._win.entry_panel.set_reverse_entry_enabled(enabled, emit_signal=emit_signal)

    def is_reverse_entry_enabled(self) -> bool:
        return self._win.entry_panel.is_reverse_entry_enabled()

    def get_entry_mode(self) -> str:
        return self._win.entry_panel.get_entry_mode()

    def update_entry_stats(self, trades: int, wins: int, pnl_pts: float):
        """당일 진입 통계 갱신"""
        self._win.entry_panel.update_stats(trades, wins, pnl_pts)

    def update_divergence(self, div_data: dict):
        """다이버전스 패널 업데이트"""
        self._win.div_panel.update_data(div_data)

    def update_strategy_ops(self, data: dict) -> None:
        """
        🧭 전략 운용현황 탭 데이터 주입 (§11 Phase 4 adapter).

        data keys:
          drift_level : int   — CUSUM DriftLevel (0~3)
          psi_val     : float — RegimeFingerprint PSI 값
          psi_level   : int   — RegimeFingerprint DriftLevel (0~3)
        """
        sp = getattr(self._win, "strategy_panel", None)
        if sp is None:
            return
        try:
            sp.set_drift_level(data.get("drift_level", 0))
            sp.set_fingerprint_level(
                float(data.get("psi_val", 0.0)),
                int(data.get("psi_level", 0)),
            )
        except Exception:
            pass

    def update_shap(self, core_vals, dynamic_items, rank_vals):
        """SHAP 피처 패널 업데이트"""
        self._win.feat_panel.update_shap(core_vals, dynamic_items, rank_vals)

    def set_model_status(self, state, detail="", progress=-1, price=None,
                         update_signal=True):
        """모델 학습 상태를 예측 패널에 표시."""
        self._win.pred_panel.set_model_status(
            state, detail, progress, price, update_signal
        )

    def append_trade_log(self, msg: str, val: str = ""):
        """창3 주문/체결 로그"""
        self._win.log_panel.append("order", "TRADE", msg, val)

    def update_order_metrics(self, trades: int, avg_lat_ms: float, peak_lat_ms: float, samples: int):
        """창3 주문/체결 탭 상단 지표 갱신"""
        self._win.log_panel.update_order_metrics(trades, avg_lat_ms, peak_lat_ms, samples)

    def update_pnl_metrics(self, unrealized_krw: float, daily_pnl_krw: float, var_krw: float = 0.0,
                           forward_unrealized_krw: float = None, forward_daily_pnl_krw: float = None):
        """창4 손익 PnL 수치 패널 갱신"""
        self._win.log_panel.update_pnl_metrics(
            unrealized_krw,
            daily_pnl_krw,
            var_krw,
            forward_unrealized_krw=forward_unrealized_krw,
            forward_daily_pnl_krw=forward_daily_pnl_krw,
        )

    def append_pnl_log(self, msg: str, val: str = ""):
        """창4 손익 로그"""
        self._win.log_panel.append("pnl", "PNL", msg, val)

    def update_pnl_history(self, rows):
        """📊 손익 추이 탭 갱신 (trades.db rows)."""
        self._win.log_panel.refresh_pnl_history(rows)

    def notify_pipeline_ran(self):
        """분봉 파이프라인 완료 시 상태 바 + 헤더 생존 바 동시 리셋."""
        self._win.log_panel.notify_update()
        self._win._pipe_elapsed_s = 0
        self._win._watchdog_alerted.clear()  # 복구 시 경보 플래그 초기화

    def set_pipeline_watchdog_cb(self, cb):
        """파이프라인 지연 감지 시 호출될 콜백 등록 (main.py → dashboard)."""
        self._win._pipeline_recovery_cb = cb

    def append_restore_trade(self, msg: str, ts: str = "", val: str = ""):
        """재시작 복원: 창3 주문/체결 탭에 이탤릭·회색으로 표시"""
        self._win.log_panel.append_restore("order", msg, ts, val)

    def append_restore_pnl(self, msg: str, ts: str = "", val: str = ""):
        """재시작 복원: 창4 손익 탭에 이탤릭·회색으로 표시"""
        self._win.log_panel.append_restore("pnl", msg, ts, val)

    def append_trade_separator(self, msg: str = ""):
        """창3 주문/체결 탭 구분선"""
        self._win.log_panel.append_separator("order", msg)

    def append_pnl_separator(self, msg: str = ""):
        """창4 손익 탭 구분선"""
        self._win.log_panel.append_separator("pnl", msg)

    def update_learning(self, data: dict):
        """🧠 자가학습 모니터 패널 업데이트

        data 키:
            verified_today      int    오늘 검증 건수
            sgd_accuracy_50m    float  SGD 50분 이동 정확도
            sgd_weight          float  현재 SGD 블렌딩 비중
            gbm_weight          float  현재 GBM 블렌딩 비중
            sgd_fitted          dict   {horizon: bool}
            sgd_sample_counts   dict   {horizon: int}
            horizon_accuracy    dict   {horizon: float}  — SGD 내부
            buffer_accuracy     dict   {horizon: float}  — 예측 버퍼 기준
            gbm_last_retrain    str    "YYYY-MM-DD HH:MM" 또는 "없음"
            gbm_retrain_count   int
            raw_candles_count   int
            last_event          str    최근 자가학습 이벤트 요약
        """
        self._win.learn_panel.update_data(data)

    def update_efficacy(self, data: dict):
        """🎯 학습 효과 검증기 패널 업데이트

        data 키:
            calibration_bins  list[dict]  conf_bin/cnt/accuracy
            grade_stats       list[dict]  grade/cnt/win_rate/avg_pnl/total_pnl
            regime_stats      list[dict]  regime/cnt/win_rate/avg_pnl
            accuracy_history  list[int]   0/1 리스트 (최신→오래된 순)
            updated_at        str         "HH:MM"
        """
        self._win.efficacy_panel.update_data(data)

    def update_trend(self, data: dict):
        """📈 학습 성장 추이 패널 업데이트

        data 키:
            일별  list[dict]  date/trades/wins/losses/win_rate/pnl_krw/sgd_accuracy
            주별  list[dict]  week/trades/wins/losses/win_rate/pnl_krw
            월별  list[dict]  month/trades/wins/losses/win_rate/pnl_krw
            연간  list[dict]  year/trades/wins/losses/win_rate/pnl_krw
            updated_at  str  "HH:MM"
        """
        self._win.trend_panel.update_data(data)

    def append_model_log(self, msg: str):
        """창5 모델 로그"""
        self._win.log_panel.append("model", "MODEL", msg)

    def append_warn_log(self, msg: str):
        """창2 경보 로그 (WARN 태그 → 1 시스템 + 2 경보 탭 동시 기록)"""
        self._win.log_panel.append("all", "WARN", msg)

    def append_sys_log_tagged(self, msg: str, level: str = "INFO"):
        """레벨 명시 시스템 로그 — WARN/WARNING/ERROR/CRITICAL 은 2 경보 탭에도 복사"""
        # Python logging 표준("WARNING")과 단축형("WARN") 모두 허용
        tag = {"WARNING": "WARN"}.get(level, level)
        tag = tag if tag in ("WARN", "ERROR", "CRITICAL") else "SYSTEM"
        self._win.log_panel.append("all", tag, msg)


# ────────────────────────────────────────────────────────────
# MireukDashboard 에 긴급 정지 버튼 생성 메서드 추가
# ────────────────────────────────────────────────────────────
def _make_kill_btn(self):
    """외부(main.py)가 clicked 시그널을 연결할 수 있는 버튼 반환"""
    if not hasattr(self, '_kill_btn'):
        self._kill_btn = QPushButton("⛔ 긴급 정지 (Ctrl+Alt+K)")
        self._kill_btn.setStyleSheet(
            f"QPushButton{{background:#A32D2D;color:#fff;"
            f"border:none;border-radius:4px;padding:8px;"
            f"font-size:{S.f(13)}px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#C0392B;}}"
        )
    return self._kill_btn

MireukDashboard._make_kill_btn = _make_kill_btn


# ────────────────────────────────────────────────────────────
# 진입점 함수들
# ────────────────────────────────────────────────────────────
def create_dashboard() -> DashboardAdapter:
    """
    main.py 에서 호출하는 팩토리 함수

    사용법 (main.py):
        self.dashboard = create_dashboard()
        self.dashboard.show()
        self.dashboard.append_sys_log("시스템 시작")
        self.dashboard.btn_kill.clicked.connect(...)
    """
    return DashboardAdapter()


def launch_dashboard(kiwoom=None):
    """단독 실행 또는 테스트용"""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MireukDashboard(kiwoom=kiwoom)
    win.show()
    return app, win


if __name__ == "__main__":
    app, win = launch_dashboard()
    sys.exit(app.exec_())
