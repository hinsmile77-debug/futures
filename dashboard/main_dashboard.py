# dashboard/main_dashboard.py
# 미륵이 v8.0 — 풀 통합 대시보드
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

import json
import os
import logging
import subprocess
import sys
import random
import math
from enum import Enum
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QProgressBar, QTabWidget,
    QTextEdit, QFrame, QSplitter, QScrollArea, QGroupBox,
    QComboBox, QSlider, QCheckBox, QSizePolicy, QDesktopWidget,
    QToolTip, QTableWidget, QTableWidgetItem, QHeaderView, QShortcut,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QSpinBox, QFormLayout,
    QRadioButton, QButtonGroup,
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QRectF, QPointF, QObject
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QBrush, QPen,
    QLinearGradient, QFontDatabase, QIcon, QKeySequence, QPainterPath, QPolygonF,
    QTextCursor, QTextBlockFormat,
)

from config.constants import FUTURES_PT_VALUE
from config.settings import (
    RAW_DATA_DB, DATA_DIR, TIME_ZONES, ENTRY_GRADE, MAX_CONTRACTS,
    HEALTH_LATENCY_WARN_MS, HEALTH_LATENCY_CRIT_MS,
    HEALTH_QUALITY_WARN, HEALTH_QUALITY_CRIT,
    HEALTH_CACHE_AGE_WARN_SEC, HEALTH_CACHE_AGE_CRIT_SEC,
    HEALTH_EXCEPTION_DENSITY_WARN_10M, HEALTH_EXCEPTION_DENSITY_CRIT_10M,
    ATR_MIN_ENTRY, ATR_MAX_ENTRY, ATR_OPEN_GAP_MULT,
    ATR_ADAPTIVE_MAX_CEILING, ATR_EXPIRY_CEILING_MULT,
    ATR_EXPIRY_CEILING_DAYS_BEFORE, ATR_EXPIRY_CEILING_DAYS_AFTER,
    CB_ACC30M_MIN_SAMPLES, SGD_BLEND_DISABLED_HORIZONS, HORIZON_ENABLED,
    TP1_PROTECT_PLUS_ALPHA_PTS, TP1_PROTECT_ATR_LOCK_MULT,   # [432차] 3중 정의 단일화
)
from strategy.entry.time_strategy_router import TimeStrategyRouter
from utils.time_utils import get_time_zone, now_kst
from utils.db_utils import fetch_today_trades, fetchall, fetch_regime_today, fetch_direction_today

# [432차] TP1_PROTECT_* 는 config/settings.py가 정본 — 위 import 블록에서 가져온다.
# 예전에는 여기 리터럴 사본이 있어, 라이브(main.py)만 바뀌면 이 툴팁이 조용히
# 거짓을 말했다. 경위는 settings.py의 해당 상수 주석 참조.

logger = logging.getLogger("SYSTEM")


class TriggerBadgeState(str, Enum):
    MONITORING = "감시중"
    WAIT = "대기"
    CALCULATING = "산정중"
    HIT = "도달"
    DONE = "완료"
    WARNING = "주의"
    EXECUTING = "주문중"
    PROTECT = "보호전환"

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
        self._mid_auto = True
        self._right_auto = True

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

    def set_mid_auto(self, enabled: bool) -> None:
        self._mid_auto = enabled

    def set_right_auto(self, enabled: bool) -> None:
        self._right_auto = enabled

    def _apply_tabs(self, force: bool = False) -> None:
        if self._manual_override and not force:
            return
        self._manual_override = False
        self._manual_idle_since = None
        if self._right_auto:
            self._set_current_index(self.right_tabs, self._desired_right)
        if self._mid_auto:
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
        if any(w.underMouse() for w in widgets if w is not None):
            return True

        # 키보드 포커스 활동도 유휴 리셋으로 간주
        if any(w.hasFocus() for w in widgets if w is not None):
            return True

        app = QApplication.instance()
        fw = app.focusWidget() if app is not None else None
        if fw is None:
            return False
        return any(
            (w is not None) and (fw is w or w.isAncestorOf(fw))
            for w in widgets
        )

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
    """KOSPI200 옵션 다음 만기까지 D-days 계산 → (text, color).

    만기 구조:
      - [월]위클리 : 매주 월요일 만기
      - [목]위클리 : 매주 목요일 만기
      - [목]월간   : 이달 두 번째 목요일 (월간 만기)
    가장 가까운 다음 만기일(월/목 중 먼저 도래)을 기준으로 배지 생성.
    """
    import datetime as _dt
    today = _dt.date.today()
    wd = today.weekday()               # 0=월 1=화 2=수 3=목 4=금 5=토 6=일

    days_to_mon = (0 - wd) % 7        # 다음 월요일까지 (0 = 오늘이 월요일)
    days_to_thu = (3 - wd) % 7        # 다음 목요일까지 (0 = 오늘이 목요일)

    # 더 가까운 만기일 선택
    if days_to_mon <= days_to_thu:
        days   = days_to_mon
        target = today + _dt.timedelta(days=days)
        tag    = "[월]위클리"
    else:
        days   = days_to_thu
        target = today + _dt.timedelta(days=days)
        # 이달 두 번째 목요일이면 월간 만기
        nth       = (target.day - 1) // 7 + 1
        tag       = "[목]월간" if nth == 2 else "[목]위클리"

    if days == 0:
        text = f"● {tag} 만기일"
        col  = "#FF5252"               # 빨강 — 오늘 만기
    elif days == 1:
        text = f"{tag} D-1"
        col  = "#FFB74D"               # 주황 — 내일 만기
    elif days <= 3:
        text = f"{tag} D-{days}"
        col  = "#FFD54F"               # 노랑 — 이번 주 내
    else:
        text = f"{tag} D-{days}"
        col  = "#CE93D8"               # 연보라 — 여유
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

_EV20_TIP = (
    "<div style='font-family:Consolas,monospace;font-size:12px;line-height:1.7;"
    "min-width:360px;'>"

    "<b style='color:#FFB74D;font-size:13px;'>최근20건 순EV&nbsp;&nbsp;거래당 순기대값</b>"
    "<hr style='border:0;border-top:1px solid #30363D;margin:4px 0 6px 0'>"

    "<b style='color:#58A6FF'>① 의미</b><br>"
    "&nbsp;&nbsp;가장 최근 체결 완료 20건의 <b>수수료 차감 후 평균 손익</b><br>"
    "&nbsp;&nbsp;'방향 적중률'이 아니라 <b>실제로 돈이 되는가</b>를 보는 지표<br>"
    "&nbsp;&nbsp;(260704 감사: 적중률 55%여도 EV 음수, 45%여도 EV 양수인 셋업이 존재)<br><br>"

    "<b style='color:#58A6FF'>② 데이터 출처</b><br>"
    "&nbsp;&nbsp;trades.db → net_pnl_krw (왕복 수수료 반영, 실집행 기준)<br>"
    "&nbsp;&nbsp;체결 20건 미만이면 있는 만큼만 집계<br><br>"

    "<b style='color:#F85149'>③ 참고</b><br>"
    "&nbsp;&nbsp;등급별·호라이즌별 세부 EV는 EOD 일일 리포트"
    "(strategy/ops/daily_exporter.py)에서 확인"

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

    # ── 슬랙 알림 내용 ───────────────────────────────────────────────
    "<b style='color:#58A6FF'>③ 슬랙 알림 내용 (CB 발동 시)</b><br>"
    "<div style='margin-left:10px;'>"
    "<div style='background:#161B22;border:1px solid #30363D;border-radius:4px;"
    "padding:6px 10px;margin:4px 0 8px 0;font-size:11px;color:#E6EDF3;line-height:1.7;'>"
    "🚨 [HH:MM:SS] [미륵이] Circuit Breaker 발동!<br>"
    "트리거: &lt;조건&gt;<br>"
    "조치: &lt;조치&gt;"
    "</div>"
    "<table style='border-collapse:collapse;line-height:1.85;font-size:11px;'>"
    "<tr style='color:#8B949E;'>"
    "<td style='padding-right:6px;'>#</td>"
    "<td style='padding-right:14px;'>트리거 텍스트</td>"
    "<td>조치 텍스트</td>"
    "</tr>"
    "<tr>"
    "<td style='color:#A371F7;font-weight:bold;padding-right:6px;'>①</td>"
    "<td style='color:#E6EDF3;padding-right:14px;'>신호 반전 N회/분</td>"
    "<td style='color:#D29922;'>15분 진입 정지</td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:6px;'>②</td>"
    "<td style='color:#E6EDF3;padding-right:14px;'>연속 손절 3회 — 당일 정지</td>"
    "<td style='color:#F85149;'>당일 시스템 정지</td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:6px;'>③</td>"
    "<td style='color:#E6EDF3;padding-right:14px;'>30분 정확도 XX% &lt; 35% (2회 연속 미달)</td>"
    "<td style='color:#F85149;'>당일 시스템 정지</td>"
    "</tr><tr>"
    "<td style='color:#D29922;font-weight:bold;padding-right:6px;'>④</td>"
    "<td style='color:#E6EDF3;padding-right:14px;'>ATR X.X배 급등 (순간/지속)</td>"
    "<td style='color:#D29922;'>5분 진입 정지</td>"
    "</tr><tr>"
    "<td style='color:#F85149;font-weight:bold;padding-right:6px;'>⑤</td>"
    "<td style='color:#E6EDF3;padding-right:14px;'>API 지연 X.X초</td>"
    "<td style='color:#F85149;'>전 포지션 즉시 청산</td>"
    "</tr>"
    "</table>"
    "<div style='color:#8B949E;font-size:11px;margin-top:4px;'>"
    "▸ CB③ 경고(1/2) 시에도 별도 슬랙 경고 메시지 발송"
    "</div>"
    "</div>"
    "<br>"

    # ── 해제 방법 ─────────────────────────────────────────────────────
    "<b style='color:#58A6FF'>④ 해제 방법 및 조건</b><br>"
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

_HZ_TIP = (
    "<div style='font-family:Consolas,monospace;font-size:12px;line-height:1.75;min-width:520px;'>"

    "<b style='color:#58A6FF;font-size:13px;'>🔭 멀티 호라이즌 예측 ( 1·3·5·10·15·30분 )</b>"
    "<hr style='border:0;border-top:1px solid #30363D;margin:5px 0 7px 0'>"

    # ── 호라이즌 의미 ─────────────────────────────────────────────
    "<b style='color:#58A6FF'>① 호라이즌(Horizon)이란</b><br>"
    "<div style='margin-left:10px;line-height:1.9;'>"
    "• <b>지금 이 1분봉 시점에서 N분 뒤 가격 방향을 예측</b>한다는 뜻<br>"
    "• 매 1분봉마다 6개 예측이 <b>동시에</b> 생성됨<br>"
    "• 각 예측은 해당 시간이 경과한 뒤 하나씩 자동 검증<br>"
    "<table style='margin:4px 0 0 0;border-collapse:collapse;font-size:11px;'>"
    "<tr style='color:#8B949E;'><td style='padding-right:14px;'>호라이즌</td><td>예측 내용</td><td style='padding-left:12px;'>검증 시점</td></tr>"
    "<tr><td style='color:#58A6FF;'>1분</td><td>1분 뒤 UP/DOWN/FLAT</td><td style='padding-left:12px;color:#8B949E;'>1분 후 분봉 수신 시</td></tr>"
    "<tr><td style='color:#58A6FF;'>15분</td><td>15분 뒤 UP/DOWN/FLAT</td><td style='padding-left:12px;color:#8B949E;'>15분 후 분봉 수신 시</td></tr>"
    "<tr><td style='color:#58A6FF;'>30분</td><td>30분 뒤 UP/DOWN/FLAT</td><td style='padding-left:12px;color:#8B949E;'>30분 후 분봉 수신 시</td></tr>"
    "</table>"
    "</div><br>"

    # ── 예측 입력 데이터 ──────────────────────────────────────────
    "<b style='color:#58A6FF'>② 예측에 사용되는 입력 데이터 (4가지 범주)</b><br>"
    "<table style='margin-left:10px;border-collapse:collapse;line-height:1.85;font-size:11px;'>"
    "<tr>"
    "<td style='color:#39D3BB;font-weight:bold;padding-right:12px;vertical-align:top;'>분봉 OHLCV</td>"
    "<td style='color:#E6EDF3;'>종가·고가·저가·거래량·매수/매도 거래량 (매분 확정)</td>"
    "</tr><tr>"
    "<td style='color:#39D3BB;font-weight:bold;padding-right:12px;vertical-align:top;'>미시구조</td>"
    "<td style='color:#E6EDF3;'>"
    "CVD·VWAP·OFI — 단기 CORE(1~5m) | VWAP·macro_vix — 중기 CORE(10~15m) | GEX·PCR·macro_vix — 장기 CORE(30m)<br>"
    "<span style='color:#8B949E;'>+ ATR(14분봉)·Microprice·MLOFI·Queue·Toxicity</span>"
    "</td>"
    "</tr><tr>"
    "<td style='color:#D29922;font-weight:bold;padding-right:12px;vertical-align:top;'>수급·옵션</td>"
    "<td style='color:#E6EDF3;'>외국인·기관 순매수 / 풋콜비율 등</td>"
    "</tr><tr>"
    "<td style='color:#D29922;font-weight:bold;padding-right:12px;vertical-align:top;'>매크로</td>"
    "<td style='color:#E6EDF3;'>환율·국채금리·VIX 등 거시 지표</td>"
    "</tr>"
    "</table>"
    "<br>"

    # ── 예측 방법 ─────────────────────────────────────────────────
    "<b style='color:#58A6FF'>③ 예측 방법</b><br>"
    "<div style='margin-left:10px;line-height:1.9;'>"
    "• <b>GBM</b> (GradientBoostingClassifier) — 호라이즌별 독립 모델 6개<br>"
    "&nbsp;&nbsp;매주 월요일 08:50 배치 재학습 (최소 5,000분봉 필요)<br>"
    "• <b>SGD</b> 온라인 학습기 — 매 검증 결과마다 즉시 가중치 업데이트<br>"
    "• 두 모델 확률을 <b>블렌딩(가중합)</b> → UP/DOWN/FLAT 확률 산출<br>"
    "• 가장 높은 확률 방향 = 예측 방향,&nbsp; 그 확률값 = confidence<br>"
    "<div style='background:#161B22;border:1px solid #30363D;border-radius:4px;"
    "padding:5px 10px;margin:4px 0;font-size:11px;color:#E6EDF3;line-height:1.7;'>"
    "피처 벡터 → GBM + SGD → 블렌딩<br>"
    "→ UP 62% / DOWN 25% / FLAT 13%&nbsp; ← 대시보드 카드 표시값<br>"
    "→ 방향=UP,&nbsp; confidence=62%"
    "</div>"
    "</div><br>"

    # ── 검증 기준 (Threshold) ─────────────────────────────────────
    "<b style='color:#58A6FF'>④ 검증 기준 — Horizon Threshold</b><br>"
    "<div style='margin-left:10px;line-height:1.9;font-size:11px;'>"
    "• threshold = 예측 맞고 틀림 채점 기준 (대시보드 카드 숫자와 무관)<br>"
    "• <b>실제 변화율 &gt; +threshold → UP,&nbsp; &lt; −threshold → DOWN,&nbsp; 그 사이 → FLAT</b><br>"
    "• 1틱 = 0.05pt &nbsp;|&nbsp; 기준 지수: KOSPI200 선물 ~1200pt"
    "</div>"
    "<table style='margin-left:10px;border-collapse:collapse;line-height:1.85;font-size:11px;margin-top:4px;'>"
    "<tr style='color:#8B949E;'>"
    "<td style='padding-right:10px;'>호라이즌</td>"
    "<td style='padding-right:10px;'>비율</td>"
    "<td style='padding-right:10px;'>pt환산</td>"
    "<td>틱환산</td>"
    "</tr>"
    "<tr><td style='color:#58A6FF;padding-right:10px;'>1분</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.05%</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.60pt</td>"
    "<td style='color:#8B949E;'>12틱</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:10px;'>3분</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.08%</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.96pt</td>"
    "<td style='color:#8B949E;'>19틱</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:10px;'>5분</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.11%</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>1.32pt</td>"
    "<td style='color:#8B949E;'>26틱</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:10px;'>10분</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.16%</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>1.92pt</td>"
    "<td style='color:#8B949E;'>38틱</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:10px;'>15분</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.22%</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>2.64pt</td>"
    "<td style='color:#8B949E;'>53틱</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:10px;'>30분</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>0.32%</td>"
    "<td style='color:#E6EDF3;padding-right:10px;'>3.84pt</td>"
    "<td style='color:#8B949E;'>77틱</td></tr>"
    "</table>"
    "<div style='margin-left:10px;color:#8B949E;font-size:11px;margin-top:3px;'>"
    "▸ config/settings.py HORIZON_THRESHOLDS 참조&nbsp;|&nbsp;"
    "2026-05-16 재보정 (기존 대비 약 1.6× 상향)"
    "</div><br>"

    # ── acc 정확도 ────────────────────────────────────────────────
    "<b style='color:#58A6FF'>⑤ acc (이동 정확도)</b><br>"
    "<div style='margin-left:10px;line-height:1.9;font-size:11px;'>"
    "• 최근 N개 분봉에서 생성된 N분 호라이즌 예측 중 <b>맞힌 비율</b><br>"
    "• CB③ 감시 대상: <b>30분 호라이즌 전용</b> (버퍼 30개, 최소 20개부터 집계)<br>"
    "<div style='background:#161B22;border:1px solid #30363D;border-radius:4px;"
    "padding:5px 10px;margin:4px 0;font-size:11px;color:#E6EDF3;line-height:1.7;'>"
    "acc = 맞힌 수 / 버퍼 크기&nbsp; (예: 18/30 = 60%)<br>"
    "기준선: 랜덤 3택 ≈ 33.3%&nbsp;|&nbsp; CB③ 발동 임계값: <b style='color:#F85149;'>35% 미만 2회 연속</b>"
    "</div>"
    "</div><br>"

    # ── 모델 AI탭 모니터링 ────────────────────────────────────────
    "<b style='color:#58A6FF'>⑥ 모델 AI탭 모니터링 (5 모델 AI)</b><br>"
    "<div style='margin-left:10px;line-height:1.9;font-size:11px;'>"
    "• <b>GBM 재학습 완료 시</b> + <b>30분 주기</b>로 자동 기록<br>"
    "• 기록 항목: 현재 ATR·지수·Static threshold·ATR동적 threshold 비교<br>"
    "• <b style='color:#3FB950;'>✅ 안정</b>: ATR 동적값 ≤ Static (현행 유지)<br>"
    "• <b style='color:#F85149;'>⚠ 초과</b>: ATR 동적값 &gt; Static → threshold 재조정 또는<br>"
    "&nbsp;&nbsp;<b>HORIZON_THRESHOLDS_BASE + ATR 동적 방식 전환 검토 권장</b>"
    "</div>"

    # ── 황색 점선 테두리 ──────────────────────────────────────────────
    "<b style='color:#D29922'>⑦ 황색(오렌지) 점선 테두리 — 완성봉 스태일(Stale) 경고</b><br>"
    "<div style='margin-left:10px;line-height:1.9;font-size:11px;'>"
    "• 해당 호라이즌의 <b>마지막 완성봉이 오래된 경우</b> 발동 (1·3분봉 제외)<br>"
    "• 발동 조건: <b>경과 분(bar_age) &gt; 호라이즌 절반</b><br>"
    "<table style='margin:4px 0 4px 0;border-collapse:collapse;font-size:11px;'>"
    "<tr style='color:#8B949E;'>"
    "<td style='padding-right:14px;'>호라이즌</td>"
    "<td style='padding-right:14px;'>황색 발동 기준</td>"
    "<td>예 (스크린샷)</td>"
    "</tr>"
    "<tr><td style='color:#58A6FF;padding-right:14px;'>5분봉</td>"
    "<td style='color:#D29922;padding-right:14px;'>age &gt; 2.5분</td>"
    "<td style='color:#8B949E;'>횡보 4m전 → 발동</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:14px;'>10분봉</td>"
    "<td style='color:#D29922;padding-right:14px;'>age &gt; 5분</td>"
    "<td style='color:#8B949E;'>35.9% 9m전 → 발동</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:14px;'>15분봉</td>"
    "<td style='color:#D29922;padding-right:14px;'>age &gt; 7.5분</td>"
    "<td style='color:#8B949E;'>50.1% 9m전 → 발동</td></tr>"
    "<tr><td style='color:#58A6FF;padding-right:14px;'>30분봉</td>"
    "<td style='color:#D29922;padding-right:14px;'>age &gt; 15분</td>"
    "<td style='color:#8B949E;'>횡보 9m전 → 미발동</td></tr>"
    "</table>"
    "• 카드 숫자 뒤 <b style='color:#D29922;'>Xm전</b> = 완성봉 확정 후 경과 분<br>"
    "• 예측값 자체는 유효하나 <b>입력 데이터 신선도 저하</b> — 진입 시 주의"
    "</div><br>"

    "<hr style='border:0;border-top:1px solid #30363D;margin:7px 0 5px 0'>"
    "<span style='color:#8B949E;font-size:11px;'>"
    "▸ 카드 % 수치 = GBM·SGD 확률 출력 (threshold 무관)&nbsp;|&nbsp;"
    "▸ 단기CORE(CVD·VWAP·OFI) / 중기CORE(VWAP·VIX) / 장기CORE(GEX·PCR·VIX) — 호라이즌별 분리&nbsp;|&nbsp;"
    "▸ 15:10 이후 신규 진입 없음"
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
    gb = QGroupBox("" if (header_widget or not title) else f"● {title}")
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
    _HZ_KEY_MAP = {
        "1분": "1m", "3분": "3m", "5분": "5m",
        "10분": "10m", "15분": "15m", "30분": "30m",
    }

    def __init__(self):
        super().__init__()
        self._build()

    def get_enabled_horizons(self) -> set:
        """config/settings.py:HORIZON_ENABLED 기준 — False인 호라이즌은 앙상블 투표 제외."""
        return {h for h, enabled in HORIZON_ENABLED.items() if enabled}

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

        # 현재가·신호·신뢰도 위젯 — 화면 미표시, 외부 참조 유지용
        self.lbl_price  = mk_val_label("——.——", C['text'], 20)
        self.lbl_signal = mk_val_label("대기중", C['text2'], 16)
        self.lbl_conf   = mk_label("신뢰도 — %", C['text2'])

        # ── 1. 앙상블 판단 (최상단 — lamp·차트·hz strip) ──────────
        from dashboard.panels.direction_indicator_dialog import DirectionIndicatorWidget
        self._dir_indicator = DirectionIndicatorWidget()
        lay.addWidget(self._dir_indicator)
        lay.addWidget(mk_sep())

        # ── 2. 모델 상태 행 (학습 대기 / 재학습중) — model.is_ready() 시 숨김 ──
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

        lay.addStretch(1)

    def update_data(self, price, preds, params, conf=None, corr="", min_conf: float = 0.58,
                    bar_ages: dict = None):
        self._model_row.setVisible(False)
        self.lbl_price.setText(f"{price:.2f}")

        # 앙상블 신뢰도 (실거래 데이터가 들어올 때만 갱신)
        if conf is not None:
            self.lbl_conf.setText(f"신뢰도 {conf*100:.1f}%")
            self.lbl_conf.setStyleSheet(
                f"color:{C['green'] if conf>=0.7 else C['orange'] if conf>=min_conf else C['red']};"
                f"font-size:{S.f(13)}px;font-weight:bold;"
            )

        # 앙상블 방향 (config/settings.py:HORIZON_ENABLED 기준으로 투표)
        # preds는 한글 호라이즌명("1분" 등) 키 — _HZ_KEY_MAP으로 영문 키 변환 후 대조
        _enabled_ui = self.get_enabled_horizons()
        _threshold = max(1, len(_enabled_ui) // 2 + 1)
        ups = sum(1 for h, v in preds.items()
                  if self._HZ_KEY_MAP.get(h, h) in _enabled_ui and v['signal'] == 1)
        dns = sum(1 for h, v in preds.items()
                  if self._HZ_KEY_MAP.get(h, h) in _enabled_ui and v['signal'] == -1)
        if ups >= _threshold:
            self.lbl_signal.setText("▲ 매수")
            self.lbl_signal.setStyleSheet(f"color:{C['green']};font-size:{S.f(16)}px;font-weight:bold;")
        elif dns >= _threshold:
            self.lbl_signal.setText("▼ 매도")
            self.lbl_signal.setStyleSheet(f"color:{C['red']};font-size:{S.f(16)}px;font-weight:bold;")
        else:
            self.lbl_signal.setText("— 관망")
            self.lbl_signal.setStyleSheet(f"color:{C['text2']};font-size:{S.f(16)}px;font-weight:bold;")


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
        # 하한을 0.0으로 둬야 아래 setValue(0.0)이 실제로 0.00으로 보인다.
        # 이전엔 하한이 100.0이라 Qt가 setValue(0.0)을 100.0으로 조용히 clamp —
        # 사용자가 가격을 입력하지 않고 [복원]을 눌러도 "100.00"이 실제 값처럼 보내져
        # _on_position_restore_clicked()의 `price > 0` 가드를 무력화하고 포지션이
        # 진입가 100.00으로 그대로 복원되는 사고로 이어졌다(대시보드 실잔고에서 확인).
        self.spn_price.setRange(0.0, 9999.99)
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
    sig_balance_refresh_requested = pyqtSignal()

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
        self.btn_balance_refresh = QPushButton("잔고 새로고침")
        self.btn_balance_refresh.setFixedWidth(S.p(92))
        self.btn_balance_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_balance_refresh.setStyleSheet(
            f"QPushButton{{background:{C['orange']};color:#fff;border:none;"
            f"border-radius:3px;padding:2px 6px;font-size:{S.f(8)}px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#d4890a;}}"
        )
        self.btn_balance_refresh.setToolTip(
            "<html><body style='background:#1e1e2e;color:#cdd6f4;"
            "font-size:12px;padding:6px;min-width:280px;'>"
            "<p style='color:#fab387;font-weight:bold;margin:0 0 6px 0;'>"
            "&#8635; 잔고 재조회</p>"
            "<p style='color:#89b4fa;font-weight:bold;margin:0 0 3px 0;'>"
            "&#9654; 사용 목적</p>"
            "<p style='margin:0 0 8px 8px;'>"
            "사이보스 잔고 TR을 다시 호출해<br>"
            "<b>메인 대시보드 잔고/요약 카드만</b> 즉시 갱신합니다."
            "</p>"
            "<p style='color:#89b4fa;font-weight:bold;margin:0 0 3px 0;'>"
            "&#9654; 사용 방법</p>"
            "<ul style='margin:0 0 4px 16px;padding:0;'>"
            "<li>버튼 클릭 또는 <b>F5</b> 입력</li>"
            "<li>차트/포지션 상태는 건드리지 않고 잔고 패널만 갱신</li>"
            "</ul>"
            "</body></html>"
        )
        self.btn_balance_refresh.clicked.connect(self._on_balance_refresh_clicked)
        live_row.addWidget(self.lbl_balance_live)
        live_row.addWidget(self.pb_balance_live)
        live_row.addWidget(self.lbl_balance_stamp)
        live_row.addStretch()
        live_row.addWidget(self.btn_balance_refresh)
        self.live_header_widget = live_box

        lay.addWidget(mk_sep())

        # 제거된 필드 더미 레이블 — update_summary 호환성 유지
        for _k in ("총매매", "총평가손익", "총평가수익률"):
            self._summary_values[_k] = mk_label("", C['text2'], 10)

        # 핵심 3필드 compact 스트립: 금일손익 · 수익율(%) · 전일손익
        strip = QHBoxLayout()
        strip.setContentsMargins(0, 0, 0, 0)
        strip.setSpacing(S.p(8))
        for key, title in [
            ("실현손익", "금일손익"),
            ("총평가",   "수익율(%)"),
            ("추정자산", "전일손익"),
        ]:
            cell = QHBoxLayout()
            cell.setContentsMargins(0, 0, 0, 0)
            cell.setSpacing(S.p(5))
            lbl = mk_label(f"{title}:", C['text2'], 9, True)
            value = mk_label("", C['text2'], 11, align=Qt.AlignLeft)
            value.setMinimumWidth(S.p(80))
            value.setStyleSheet(
                f"font-size:{S.f(11)}px;color:{C['text2']};"
                f"padding:{S.p(3)}px {S.p(6)}px;"
                f"background:{C['bg3']};border:1px solid {C['border']};"
                f"border-radius:{S.p(3)}px;"
            )
            cell.addWidget(lbl)
            cell.addWidget(value, 1)
            strip.addLayout(cell)
            self._summary_values[key] = value
        lay.addLayout(strip)
        lay.addWidget(mk_sep())

        self.tbl_balance = QTableWidget(3, 5)
        self.tbl_balance.setHorizontalHeaderLabels([
            "구분", "보유량", "매입가", "현재가", "평가손익"
        ])
        self.tbl_balance.verticalHeader().setVisible(False)
        self.tbl_balance.verticalHeader().setDefaultSectionSize(S.p(22))
        self.tbl_balance.horizontalHeader().setFixedHeight(S.p(26))
        self.tbl_balance.setFixedHeight(3 * S.p(22) + S.p(26))
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
        )
        lay.addWidget(self.tbl_balance)

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
        for key, label in self._summary_values.items():
            label.setText(self._format_value(summary.get(key), is_percent=(key == "총평가")))

    def update_rows(self, rows):
        rows = list(rows or [])
        self.tbl_balance.clearSpans()  # 이전 FLAT span 해제
        self.tbl_balance.setRowCount(max(3, len(rows)))
        if not rows:
            flat = QTableWidgetItem("FLAT")
            flat.setTextAlignment(Qt.AlignCenter)
            flat.setForeground(QColor(C['text2']))
            self.tbl_balance.setItem(0, 0, flat)
            self.tbl_balance.setSpan(0, 0, 1, 5)
            return
        columns = [
            (("매매구분", "구분"), False),
            (("잔고수량", "보유수량"), False),
            (("매입단가", "평균가"), False),
            (("현재가",), False),
            (("평가손익(원)", "평가손익"), False),
        ]
        for r, row in enumerate(rows):
            for c, (fields, is_percent) in enumerate(columns):
                raw = ""
                for field in fields:
                    raw = row.get(field, "")
                    if str(raw or "").strip():
                        break
                text = self._format_value(raw, is_percent=is_percent) if c >= 1 else str(raw or "").strip()
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.tbl_balance.setItem(r, c, item)

    def _on_position_restore_clicked(self):
        dlg = PositionRestoreDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            direction, price, qty, atr = dlg.get_values()
            if price > 0 and qty > 0:
                self.sig_position_restore.emit(direction, price, qty, atr)

    def _on_balance_refresh_clicked(self):
        self.sig_balance_refresh_requested.emit()


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
        lay.setSpacing(3)
        self.panel_status_label = mk_label("", C['text2'], 8)
        self.option_status_label = mk_label("", C['text2'], 8)

        lay.addWidget(mk_label("외인-개인 다이버전스 지수 (역발상 핵심 신호)", C['orange'], 9, True))
        lay.addWidget(self.panel_status_label)

        # 바이어스 미터
        for label, attr_prefix, lcol, rcol, ltext, rtext in [
            ("개인 방향", "rt", C['green'], C['red'], "풋↑", "콜↑"),
            ("외인 방향", "fi", C['red'],   C['green'], "풋↑", "콜↑"),
        ]:
            row = QHBoxLayout()
            row.addWidget(mk_label(label, C['text2'], 9))
            row.addWidget(mk_label(ltext, lcol, 9))
            bar_l = mk_prog(lcol, 10)
            bar_r = mk_prog(rcol, 10)
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

        # 선물 투자자 수급 섹션 (Cybos Plus 네이티브 — 계약수/미결제)
        lay.addWidget(mk_label("선물 투자자 수급 (계약수)", C['cyan'], 9, True))
        fut_grid = QGridLayout()
        fut_grid.setSpacing(2)
        _fut_cards = [
            ("외인 선물 순매수", "fut_fi",   C['blue']),
            ("개인 선물 순매수", "fut_rt",   C['red']),
            ("기관 선물 순매수", "fut_inst", C['purple']),
            ("프로그램 차익",    "prog_arb",    C['green']),
            ("프로그램 비차익",  "prog_nonarb", C['orange']),
            ("미결제약정",       "open_int",    C['cyan']),
        ]
        for i, (title, attr, col) in enumerate(_fut_cards):
            ff = QFrame()
            ff.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};"
                f"border-radius:4px;}}"
            )
            ffl = QVBoxLayout(ff)
            ffl.setContentsMargins(4, 2, 4, 2)
            ffl.setSpacing(0)
            ffl.addWidget(mk_label(title, C['text2'], 8))
            fv = mk_val_label("——", col, 12)
            ffl.addWidget(fv)
            setattr(self, f"fut_{attr}_val", fv)
            fut_grid.addWidget(ff, i // 3, i % 3)
        lay.addLayout(fut_grid)

        lay.addWidget(mk_sep())

        # 포지션 카드 (2×4 그리드)
        lay.addWidget(mk_label("투자자 포지션 매트릭스", C['blue'], 9, True))
        pos_grid = QGridLayout()
        pos_grid.setSpacing(2)
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
                f"border-radius:4px;}}"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(4, 2, 4, 2)
            fl.setSpacing(0)
            t = mk_label(title, C['text2'], 8)
            v = mk_val_label("——", col, 12)
            fl.addWidget(t)
            fl.addWidget(v)
            setattr(self, f"pos_{attr}_val", v)
            pos_grid.addWidget(f, i // 4, i % 4)
        lay.addLayout(pos_grid)

        lay.addWidget(mk_sep())
        # 옵션 구간별 거래량
        lay.addWidget(mk_label("옵션 구간별 거래량 (ITM·ATM·OTM)", C['cyan'], 9, True))
        lay.addWidget(self.option_status_label)
        lay.addWidget(mk_label(
            "※ ITM/OTM 투자자별 구간 데이터는 Cybos API가 행사가 단위로 제공하지 않아 수집 불가 "
            "(전량 ATM으로 집계) — N/A 표시",
            C['text2'], 7,
        ))
        zone_lay = QHBoxLayout()
        zone_lay.setSpacing(2)
        for zone in ["ITM", "ATM", "OTM"]:
            zf = QFrame()
            zf.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            zfl = QVBoxLayout(zf)
            zfl.setContentsMargins(4, 3, 4, 3)
            zfl.setSpacing(1)
            zfl.addWidget(mk_label(zone, C['text'], 10, True, Qt.AlignCenter))
            for inv, col in [("외인",C['blue']),("개인",C['red']),("기관",C['purple'])]:
                hr = QHBoxLayout()
                hr.setSpacing(2)
                hr.addWidget(mk_label(inv, C['text2'], 8))
                b = mk_prog(col, 6)
                b.setValue(0)
                hr.addWidget(b, 2)
                vl = mk_label("—%", col, 8)
                setattr(self, f"oz_{zone}_{inv}", (b, vl))
                hr.addWidget(vl)
                zfl.addLayout(hr)
            zone_lay.addWidget(zf)
        lay.addLayout(zone_lay)

        lay.addWidget(mk_sep())

        # ── 옵션 체인 스냅샷 (OptionMst 5분 폴링) ─────────────────
        self._chain_refresh_ts = 0.0
        self._chain_interval_sec = 300  # 5분

        hdr_row = QHBoxLayout()
        hdr_row.addWidget(mk_label("옵션 체인 스냅샷  (OptionMst 5분 폴링)", C['green'], 9, True))
        hdr_row.addStretch()
        self.chain_time_lbl   = mk_label("갱신: ——", C['text2'], 8)
        self.chain_status_lbl = mk_label("● 미수집", C['text2'], 8)
        hdr_row.addWidget(self.chain_time_lbl)
        hdr_row.addWidget(self.chain_status_lbl)
        lay.addLayout(hdr_row)

        # freshness bar: 5분(300s) 카운트다운 — 가득 찰수록 신선
        fresh_row = QHBoxLayout()
        fresh_row.addWidget(mk_label("신선도", C['text2'], 8))
        self.chain_fresh_bar = QProgressBar()
        self.chain_fresh_bar.setRange(0, self._chain_interval_sec)
        self.chain_fresh_bar.setValue(0)
        self.chain_fresh_bar.setTextVisible(False)
        self.chain_fresh_bar.setFixedHeight(6)
        self.chain_fresh_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg2']};border:1px solid {C['border']};"
            f"border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{C['text2']};border-radius:3px;}}"
        )
        fresh_row.addWidget(self.chain_fresh_bar, 1)
        self.chain_fresh_lbl = mk_label("——", C['text2'], 8)
        fresh_row.addWidget(self.chain_fresh_lbl)
        lay.addLayout(fresh_row)

        chain_grid = QGridLayout()
        chain_grid.setSpacing(2)

        # 1행: 체인 PCR | ATM PCR | GEX
        _row0 = [
            ("체인 PCR",  "chain_pcr",  C['orange'], "풋/콜 OI"),
            ("ATM PCR",   "atm_pcr",    C['blue'],   "ATM 행사가"),
            ("GEX",       "gex_bn",     C['purple'], "딜러 감마"),
        ]
        # 2행: ATM 콜 OI | ATM 풋 OI | (빈칸)
        _row1 = [
            ("ATM 콜 OI", "atm_call_oi", C['green'], ""),
            ("ATM 풋 OI", "atm_put_oi",  C['red'],   ""),
        ]
        for col_i, (title, attr, col, sub) in enumerate(_row0):
            cf = QFrame()
            cf.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;}}"
            )
            cfl = QVBoxLayout(cf)
            cfl.setContentsMargins(4, 2, 4, 2)
            cfl.setSpacing(0)
            cfl.addWidget(mk_label(title, C['text2'], 8))
            cv = mk_val_label("——", col, 12)
            cfl.addWidget(cv)
            if sub:
                cfl.addWidget(mk_label(sub, C['text2'], 7))
            setattr(self, f"chain_{attr}_val", cv)
            chain_grid.addWidget(cf, 0, col_i)

        for col_i, (title, attr, col, sub) in enumerate(_row1):
            cf = QFrame()
            cf.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;}}"
            )
            cfl = QVBoxLayout(cf)
            cfl.setContentsMargins(4, 2, 4, 2)
            cfl.setSpacing(0)
            cfl.addWidget(mk_label(title, C['text2'], 8))
            cv = mk_val_label("——", col, 12)
            cfl.addWidget(cv)
            setattr(self, f"chain_{attr}_val", cv)
            chain_grid.addWidget(cf, 1, col_i)

        # 3행: 실현변동성(RV) | VKOSPI(IV) | RV-IV 스프레드 (328차)
        _row2 = [
            ("실현변동성(RV)", "rv_ann",       C['cyan'],   "연율화 %"),
            ("VKOSPI(IV)",     "iv_vkospi",    C['orange'], "KRX 지수"),
            ("RV-IV 스프레드", "rv_iv_spread", C['text2'],  "RV−IV"),
        ]
        for col_i, (title, attr, col, sub) in enumerate(_row2):
            cf = QFrame()
            cf.setStyleSheet(
                f"QFrame{{background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;}}"
            )
            cfl = QVBoxLayout(cf)
            cfl.setContentsMargins(4, 2, 4, 2)
            cfl.setSpacing(0)
            cfl.addWidget(mk_label(title, C['text2'], 8))
            cv = mk_val_label("——", col, 12)
            cfl.addWidget(cv)
            if sub:
                cfl.addWidget(mk_label(sub, C['text2'], 7))
            setattr(self, f"chain_{attr}_val", cv)
            chain_grid.addWidget(cf, 2, col_i)

        lay.addLayout(chain_grid)

    def update_data(self, div):
        self.panel_status_label.setText(div.get("panel_status_text", ""))
        option_supported = bool(div.get("option_flow_supported", True))
        self.option_status_label.setText(
            "" if option_supported else div.get("option_flow_reason", "Option flow unavailable")
        )
        self.rt_put_bar.setValue(int(max(0, -div['rt_bias']) * 50))
        self.rt_call_bar.setValue(int(max(0, div['rt_bias']) * 50))
        self.fi_put_bar.setValue(int(max(0, -div['fi_bias']) * 50))
        self.fi_call_bar.setValue(int(max(0, div['fi_bias']) * 50))

        # ── 선물 투자자 수급 갱신 ────────────────────────────────
        def _fmt_contracts(v):
            if v is None:
                return "——"
            return f"{int(v):+,}" if v != 0 else "0"

        fi_fut   = div.get("foreign_futures_net")
        rt_fut   = div.get("retail_futures_net")
        inst_fut = div.get("institution_futures_net")
        arb      = div.get("program_arb_net")
        nonarb   = div.get("program_nonarb_net")
        oi       = div.get("open_interest")

        fut_supported = div.get("futures_supported", False)

        if fut_supported or fi_fut or rt_fut or inst_fut:
            self.fut_fut_fi_val.setText(_fmt_contracts(fi_fut))
            self.fut_fut_rt_val.setText(_fmt_contracts(rt_fut))
            self.fut_fut_inst_val.setText(_fmt_contracts(inst_fut))
            fi_col  = C['green'] if (fi_fut or 0) > 0 else C['red'] if (fi_fut or 0) < 0 else C['text2']
            rt_col  = C['green'] if (rt_fut or 0) > 0 else C['red'] if (rt_fut or 0) < 0 else C['text2']
            self.fut_fut_fi_val.setStyleSheet(
                f"color:{fi_col};font-size:{S.f(13)}px;font-weight:bold;"
            )
            self.fut_fut_rt_val.setStyleSheet(
                f"color:{rt_col};font-size:{S.f(13)}px;font-weight:bold;"
            )
        else:
            self.fut_fut_fi_val.setText("대기")
            self.fut_fut_rt_val.setText("대기")
            self.fut_fut_inst_val.setText("대기")

        prog_supported = div.get("program_supported", False)
        if prog_supported or arb is not None:
            self.fut_prog_arb_val.setText(_fmt_contracts(arb))
            self.fut_prog_nonarb_val.setText(_fmt_contracts(nonarb))
        else:
            self.fut_prog_arb_val.setText("대기")
            self.fut_prog_nonarb_val.setText("대기")

        if oi:
            self.fut_open_int_val.setText(f"{int(oi):,}")
        else:
            self.fut_open_int_val.setText("——")

        # ── 옵션 기반 포지션 매트릭스 ────────────────────────────
        if option_supported:
            self.pos_rt_call_val.setText(f"{div.get('rt_call',0):,}")
            self.pos_rt_put_val.setText(f"{div.get('rt_put',0):,}")
            self.pos_rt_strd_val.setText(f"{div.get('rt_strd',0):,}")
            self.pos_fi_call_val.setText(f"{div.get('fi_call',0):+,}")
            self.pos_fi_put_val.setText(f"{div.get('fi_put',0):+,}")
            self.pos_fi_strangle_val.setText(f"{div.get('fi_strangle',0):+,}")
        else:
            self.pos_rt_call_val.setText("--")
            self.pos_rt_put_val.setText("--")
            self.pos_rt_strd_val.setText("--")
            self.pos_fi_call_val.setText("--")
            self.pos_fi_put_val.setText("--")
            self.pos_fi_strangle_val.setText("--")
        contrarian = div.get('contrarian','중립')
        # 역발상: 개인 매수 우위 → 하락신호(빨간), 개인 매도 우위 → 상승신호(초록)
        col = C['green'] if '매도' in contrarian else C['red'] if '매수' in contrarian else C['text2']
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
                if not option_supported:
                    b.setValue(0)
                    vl.setText("--")
                elif zone in ("ITM", "OTM"):
                    # Cybos CpSvrNew7212는 투자자별 콜/풋 순매수를 행사가 단위로
                    # 세분화하지 않음 — 구조적으로 항상 0이라 "0%"로 표시하면
                    # 실측 데이터처럼 오인될 수 있어 N/A로 구분 표시.
                    b.setValue(0)
                    vl.setText("N/A")
                else:
                    pct = zd.get(inv, 0)
                    b.setValue(pct)
                    vl.setText(f"{pct}%")

        # freshness 게이지 매분 갱신
        self._tick_chain_freshness()

    def _tick_chain_freshness(self) -> None:
        import time as _time
        if self._chain_refresh_ts <= 0:
            return
        elapsed = _time.time() - self._chain_refresh_ts
        remaining = max(0.0, self._chain_interval_sec - elapsed)
        self.chain_fresh_bar.setValue(int(remaining))

        pct = remaining / self._chain_interval_sec
        if pct > 0.6:
            chunk_col = C['green']
        elif pct > 0.25:
            chunk_col = C['orange']
        else:
            chunk_col = C['red']
        self.chain_fresh_bar.setStyleSheet(
            f"QProgressBar{{background:{C['bg2']};border:1px solid {C['border']};"
            f"border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{chunk_col};border-radius:3px;}}"
        )
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        if mins > 0:
            self.chain_fresh_lbl.setText(f"{mins}분 {secs:02d}초 전")
        else:
            self.chain_fresh_lbl.setText(f"{secs}초 전")
        self.chain_fresh_lbl.setStyleSheet(f"color:{chunk_col};font-size:{S.f(8)}px;")

    def update_option_chain(self, chain_feats: dict) -> None:
        import time as _time
        import datetime as _dt
        avail = bool(chain_feats.get("opt_chain_available", 0))

        if avail:
            self._chain_refresh_ts = _time.time()
            now_str = _dt.datetime.now().strftime("%H:%M")
            self.chain_time_lbl.setText(f"갱신: {now_str}")
            self.chain_status_lbl.setText("● 수집완료")
            self.chain_status_lbl.setStyleSheet(
                f"color:{C['green']};font-size:{S.f(8)}px;font-weight:bold;"
            )
            # freshness 바 즉시 풀로 채우기
            self.chain_fresh_bar.setValue(self._chain_interval_sec)
            self.chain_fresh_bar.setStyleSheet(
                f"QProgressBar{{background:{C['bg2']};border:1px solid {C['border']};"
                f"border-radius:3px;}}"
                f"QProgressBar::chunk{{background:{C['green']};border-radius:3px;}}"
            )
            self.chain_fresh_lbl.setText("방금")
            self.chain_fresh_lbl.setStyleSheet(
                f"color:{C['green']};font-size:{S.f(8)}px;"
            )

            pcr     = float(chain_feats.get("opt_chain_pcr", 0) or 0)
            atm_pcr = float(chain_feats.get("opt_atm_pcr",   0) or 0)
            gex_bn  = float(chain_feats.get("opt_gex_bn",    0) or 0)
            gex_sgn = float(chain_feats.get("opt_gex_sign",  0) or 0)
            c_oi    = int(chain_feats.get("opt_atm_call_oi", 0) or 0)
            p_oi    = int(chain_feats.get("opt_atm_put_oi",  0) or 0)

            pcr_col = C['red'] if pcr > 1.2 else (C['green'] if pcr < 0.8 else C['orange'])
            self.chain_chain_pcr_val.setText(f"{pcr:.3f}")
            self.chain_chain_pcr_val.setStyleSheet(
                f"color:{pcr_col};font-size:{S.f(12)}px;font-weight:bold;"
            )

            atm_col = C['red'] if atm_pcr > 1.2 else (C['green'] if atm_pcr < 0.8 else C['blue'])
            self.chain_atm_pcr_val.setText(f"{atm_pcr:.3f}")
            self.chain_atm_pcr_val.setStyleSheet(
                f"color:{atm_col};font-size:{S.f(12)}px;font-weight:bold;"
            )

            gex_col = C['green'] if gex_sgn > 0 else (C['red'] if gex_sgn < 0 else C['text2'])
            gex_txt = f"{gex_bn:+.1f}B"
            self.chain_gex_bn_val.setText(gex_txt)
            self.chain_gex_bn_val.setStyleSheet(
                f"color:{gex_col};font-size:{S.f(12)}px;font-weight:bold;"
            )

            self.chain_atm_call_oi_val.setText(f"{c_oi:,}")
            self.chain_atm_put_oi_val.setText(f"{p_oi:,}")
        else:
            self.chain_status_lbl.setText("● 미수집")
            self.chain_status_lbl.setStyleSheet(
                f"color:{C['text2']};font-size:{S.f(8)}px;"
            )

    def update_rv_iv(self, features: dict) -> None:
        """RV(실현변동성)-VKOSPI(IV) 스프레드 카드 갱신 (328차).

        features는 feature_builder.build() 반환값 그대로 — "vkospi"/"vkospi_ready"는
        basis_data 병합으로, "realized_vol_ann"/"rv_iv_spread"/"rv_iv_spread_ready"는
        feature_builder.py의 RV-IV 계산 블록에서 채워진다.
        """
        rv_ann  = float(features.get("realized_vol_ann", 0.0) or 0.0)
        vkospi  = float(features.get("vkospi", 0.0) or 0.0)
        spread  = float(features.get("rv_iv_spread", 0.0) or 0.0)
        ready   = bool(features.get("rv_iv_spread_ready", False))

        self.chain_rv_ann_val.setText(f"{rv_ann:.2f}%" if ready else "——")
        self.chain_iv_vkospi_val.setText(f"{vkospi:.2f}" if vkospi > 0 else "——")

        if ready:
            # RV > IV: 시장이 변동성을 과소평가(저평가) → green. RV < IV: 과대평가(고평가) → red.
            spread_col = C['green'] if spread > 0 else (C['red'] if spread < 0 else C['text2'])
            self.chain_rv_iv_spread_val.setText(f"{spread:+.2f}")
            self.chain_rv_iv_spread_val.setStyleSheet(
                f"color:{spread_col};font-size:{S.f(12)}px;font-weight:bold;"
            )
        else:
            self.chain_rv_iv_spread_val.setText("——")
            self.chain_rv_iv_spread_val.setStyleSheet(
                f"color:{C['text2']};font-size:{S.f(12)}px;font-weight:bold;"
            )


# ────────────────────────────────────────────────────────────
# 패널 3: 동적 피처 관리 (SHAP)
# ────────────────────────────────────────────────────────────
class FeaturePanel(QWidget):
    """호라이즌 그룹별 CORE SHAP 드라이버 패널.

    단기(1m~5m) / 중기(10m~15m) / 장기(30m) CORE를 분리 표시.
    현재 진입 호라이즌 강조 + 실측값(VIX·PCR) 인라인 표시.
    """
    sig_apply_candidate_requested = pyqtSignal()
    sig_force_retrain_requested = pyqtSignal()
    sig_reset_feature_set_requested = pyqtSignal()

    # 그룹별 테마 색상
    _GRP_COLOR = {
        "short": "#39d3bb",   # 청록 — 단기
        "mid":   "#e3b341",   # 황색 — 중기
        "long":  "#a371f7",   # 보라 — 장기
    }
    _GRP_BG = {
        "short": "#0B2B24",
        "mid":   "#2B1F00",
        "long":  "#1A0D2B",
    }

    def __init__(self):
        super().__init__()
        # 헤더
        self._lbl_hz     = None   # 진입 호라이즌 배지
        self._lbl_summary = None  # 그룹별 CORE 요약
        # 그룹별 CORE 행: {group: [(nlab, bar, vlab, slab, xlab), ...]}
        self._core_rows  = {"short": [], "mid": [], "long": []}
        # 그룹별 GroupBox (강조 테두리 제어)
        self._grp_boxes  = {}
        # 동적 TOP3 행
        self.dynamic_rows = []
        # 전체 순위 행
        self.rank_labels  = []
        # 운영
        self.cooldown_bar = None
        self.cooldown_lbl = None
        self.review_summary = None
        self.btn_apply_candidate = None
        self.btn_force_retrain   = None
        self.btn_reset_feature_set = None
        self.change_log = None
        self._build()

    # ── 내부 헬퍼 ────────────────────────────────────────────────
    @staticmethod
    def _grp_box_style(color: str, bg: str) -> str:
        return (
            f"QGroupBox{{color:{color};border:2px solid {color};"
            f"border-radius:6px;margin-top:6px;font-size:{S.f(9)}px;font-weight:bold;"
            f"background:{bg};}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;"
            f"padding:0 4px;background:{C['bg']};}}"
        )

    @staticmethod
    def _grp_box_style_dim(color: str) -> str:
        """비활성 그룹 — 테두리 흐리게"""
        dim = color + "55"
        return (
            f"QGroupBox{{color:{dim};border:1px solid {dim};"
            f"border-radius:6px;margin-top:6px;font-size:{S.f(9)}px;"
            f"background:{C['bg2']};}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;"
            f"padding:0 4px;background:{C['bg']};}}"
        )

    def _make_core_row(self, bar_color: str):
        """(nlab, bar, vlab, slab, xlab) 위젯 튜플 생성."""
        row = QHBoxLayout()
        row.setSpacing(4)
        nlab = mk_label("——", C['text'], S.f(10))
        bar  = mk_prog(bar_color, S.f(9))
        bar.setFixedHeight(S.p(8))
        vlab = mk_val_label("—%", bar_color, S.f(9))
        vlab.setFixedWidth(S.p(34))
        slab = mk_label("——", C['text2'], S.f(8))
        slab.setFixedWidth(S.p(42))
        xlab = mk_label("", "#e3b341", S.f(8))   # [★강제X] 또는 실측값
        xlab.setFixedWidth(S.p(80))
        row.addWidget(nlab, 3)
        row.addWidget(bar, 4)
        row.addWidget(vlab)
        row.addWidget(slab)
        row.addWidget(xlab)
        return row, (nlab, bar, vlab, slab, xlab)

    def _build(self):
        from PyQt5.QtWidgets import QGroupBox, QScrollArea

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # ── 헤더: 진입 호라이즌 + 전체 CORE 상태 ───────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(8)

        hz_box = QFrame()
        hz_box.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:5px;"
        )
        hz_lay = QHBoxLayout(hz_box)
        hz_lay.setContentsMargins(6, 3, 6, 3)
        hz_lay.setSpacing(4)
        hz_lay.addWidget(mk_label("진입", C['text2'], S.f(8)))
        self._lbl_hz = mk_val_label("—m", C['cyan'], S.f(11))
        self._lbl_hz.setToolTip(
            "ATR 기반 select_entry_horizon() 결과.\n"
            "현재 변동성 레짐에서 수익 실현 가능한 최적 보유 호라이즌.\n"
            "해당 그룹의 CORE 섹션이 강조됩니다."
        )
        hz_lay.addWidget(self._lbl_hz)
        hdr.addWidget(hz_box)

        self._lbl_summary = mk_label("단기 —/3  중기 —/2  장기 —/2", C['text2'], S.f(8))
        self._lbl_summary.setToolTip("각 호라이즌 그룹의 CORE 통과 수 / 전체 수")
        hdr.addWidget(self._lbl_summary, 1)
        root.addLayout(hdr)

        # ── 스크롤 영역 (CORE 3개 섹션 + 동적 TOP3 + 순위) ─────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea{border:none;background:transparent;}"
            "QScrollBar:vertical{width:5px;background:transparent;}"
            "QScrollBar::handle:vertical{background:#30363d;border-radius:2px;}"
        )
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 2, 0)
        lay.setSpacing(5)

        # ── 단기 CORE 섹션 ──────────────────────────────────────────
        short_grp = QGroupBox("▶ 단기 CORE  1m · 3m · 5m   CVD · VWAP★ · OFI")
        short_grp.setStyleSheet(self._grp_box_style(self._GRP_COLOR["short"], self._GRP_BG["short"]))
        short_grp.setToolTip(
            "단기 CORE (1m~5m) — 마이크로구조 주도 신호\n"
            "CVD 다이버전스: 가격-누적체결 역행 → 반전 선행\n"
            "VWAP 위치(★): 기관 알고리즘 기준선 — 미통과 시 강제X등급\n"
            "OFI 불균형: 1~3분 호가 압력 선행"
        )
        short_inner = QVBoxLayout(short_grp)
        short_inner.setContentsMargins(6, 8, 6, 6)
        short_inner.setSpacing(3)
        for _ in range(3):
            row_lay, widgets = self._make_core_row(self._GRP_COLOR["short"])
            short_inner.addLayout(row_lay)
            self._core_rows["short"].append(widgets)
        lay.addWidget(short_grp)
        self._grp_boxes["short"] = short_grp

        # ── 중기 CORE 섹션 ──────────────────────────────────────────
        mid_grp = QGroupBox("▶ 중기 CORE  10m · 15m   VWAP★ · macro_vix")
        mid_grp.setStyleSheet(self._grp_box_style_dim(self._GRP_COLOR["mid"]))
        mid_grp.setToolTip(
            "중기 CORE (10m~15m) — VWAP 구조 + 매크로 레짐\n"
            "VWAP 위치(★): 기관 기준선 — 미통과 시 강제X등급\n"
            "macro_vix: VIX 레벨 — 저공포(낮음) → LONG 유호, 고공포(높음) → SHORT 유호\n"
            "CVD·OFI는 10m+ 에서 틱 잡음화 → 체크 면제"
        )
        mid_inner = QVBoxLayout(mid_grp)
        mid_inner.setContentsMargins(6, 8, 6, 6)
        mid_inner.setSpacing(3)
        for _ in range(2):
            row_lay, widgets = self._make_core_row(self._GRP_COLOR["mid"])
            mid_inner.addLayout(row_lay)
            self._core_rows["mid"].append(widgets)
        lay.addWidget(mid_grp)
        self._grp_boxes["mid"] = mid_grp

        # ── 장기 CORE 섹션 ──────────────────────────────────────────
        long_grp = QGroupBox("▶ 장기 CORE  30m   opt_chain_pcr · macro_vix")
        long_grp.setStyleSheet(self._grp_box_style_dim(self._GRP_COLOR["long"]))
        long_grp.setToolTip(
            "장기 CORE (30m) — 딜러 감마 + 옵션 체인 + 매크로\n"
            "opt_chain_pcr: PCR<1.0=콜우세=LONG 구조, >1.0=풋우세=SHORT 구조\n"
            "macro_vix: VIX 레짐 — 장기 방향 배경\n"
            "VWAP 강제X 해제(장기는 구조적 힘이 우선) — CVD·OFI 완전 면제"
        )
        long_inner = QVBoxLayout(long_grp)
        long_inner.setContentsMargins(6, 8, 6, 6)
        long_inner.setSpacing(3)
        for _ in range(2):
            row_lay, widgets = self._make_core_row(self._GRP_COLOR["long"])
            long_inner.addLayout(row_lay)
            self._core_rows["long"].append(widgets)
        lay.addWidget(long_grp)
        self._grp_boxes["long"] = long_grp

        # ── Phase C: CORE × 호라이즌 매트릭스 ──────────────────────
        self._build_matrix(lay)

        lay.addWidget(mk_sep())

        # ── 동적 SHAP TOP3 ──────────────────────────────────────────
        dyn_hdr = QHBoxLayout()
        dyn_hdr.addWidget(mk_label("▐ 동적 SHAP TOP 3", C['purple'], S.f(9), True))
        cdlay = QHBoxLayout()
        cdlay.setSpacing(4)
        cdlay.addWidget(mk_label("쿨다운:", C['text2'], S.f(8)))
        self.cooldown_bar = mk_prog(C['orange'], S.f(6))
        self.cooldown_bar.setFixedHeight(S.p(6))
        cdlay.addWidget(self.cooldown_bar, 2)
        self.cooldown_lbl = mk_label("없음", C['text2'], S.f(8))
        cdlay.addWidget(self.cooldown_lbl)
        dyn_hdr.addLayout(cdlay)
        lay.addLayout(dyn_hdr)

        self.dynamic_rows = []
        for _ in range(3):
            row = QHBoxLayout()
            row.setSpacing(4)
            rank = mk_badge("—", C['bg3'], C['purple'], S.f(8))
            rank.setFixedWidth(S.p(24))
            nlab = mk_label("——", C['text'], S.f(9))
            bar  = mk_prog(C['purple'], S.f(8))
            bar.setFixedHeight(S.p(7))
            vlab = mk_val_label("—%", C['purple'], S.f(9))
            vlab.setFixedWidth(S.p(30))
            slab = mk_label("——", C['text2'], S.f(8))
            slab.setFixedWidth(S.p(52))
            row.addWidget(rank)
            row.addWidget(nlab, 3)
            row.addWidget(bar, 4)
            row.addWidget(vlab)
            row.addWidget(slab)
            lay.addLayout(row)
            self.dynamic_rows.append((rank, nlab, bar, vlab, slab))

        lay.addWidget(mk_sep())

        # ── 전체 순위 (상위 6개) ────────────────────────────────────
        lay.addWidget(mk_label("전체 피처 순위  SHAP 누적", C['blue'], S.f(9), True))
        self.rank_labels = []
        _rank_colors = [C['cyan'], C['cyan'], C['orange'], C['cyan'], C['purple'], C['cyan']]
        for col in _rank_colors:
            r = QHBoxLayout()
            r.setSpacing(4)
            nl = mk_label("——", C['text2'], S.f(8))
            nl.setFixedWidth(S.p(70))
            b  = mk_prog(col, S.f(7))
            b.setFixedHeight(S.p(6))
            vl = mk_val_label("—%", col, S.f(8))
            vl.setFixedWidth(S.p(30))
            r.addWidget(nl)
            r.addWidget(b, 3)
            r.addWidget(vl)
            lay.addLayout(r)
            self.rank_labels.append((nl, b, vl))

        lay.addWidget(mk_sep())

        # ── 교체 이력 ───────────────────────────────────────────────
        lay.addWidget(mk_label("교체 이력", C['text2'], S.f(9), True))
        self.change_log = QTextEdit()
        self.change_log.setReadOnly(True)
        self.change_log.setFixedHeight(S.p(50))
        self.change_log.setStyleSheet(
            f"background:{C['bg']};color:{C['text2']};border:1px solid {C['border']};"
            f"font-size:{S.f(9)}px;font-family:Consolas;"
        )
        lay.addWidget(self.change_log)
        self.change_log.setPlainText("기록 없음")

        lay.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

        # ── 운영 액션 (고정 하단) ────────────────────────────────────
        action_box = QFrame()
        action_box.setStyleSheet(
            f"background:{C['bg2']};border:1px solid {C['border']};border-radius:6px;"
        )
        action_lay = QVBoxLayout(action_box)
        action_lay.setContentsMargins(6, 6, 6, 6)
        action_lay.setSpacing(4)
        act_hdr = QHBoxLayout()
        act_hdr.addWidget(mk_label("운영 플로우", C['yellow'], S.f(9), True))
        self.review_summary = mk_label("추천 후보를 점검하는 중", C['text2'], S.f(8))
        self.review_summary.setWordWrap(True)
        act_hdr.addWidget(self.review_summary, 1)
        action_lay.addLayout(act_hdr)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        self.btn_apply_candidate = QPushButton("추천 적용")
        self.btn_apply_candidate.setCursor(Qt.PointingHandCursor)
        self.btn_apply_candidate.setStyleSheet(
            f"QPushButton{{background:{C['green']};color:#04110C;border:none;"
            f"border-radius:5px;padding:5px 8px;font-size:{S.f(9)}px;font-weight:bold;}}"
            f"QPushButton:disabled{{background:{C['bg3']};color:{C['text2']};}}"
        )
        self.btn_force_retrain = QPushButton("세트 재학습")
        self.btn_force_retrain.setCursor(Qt.PointingHandCursor)
        self.btn_force_retrain.setStyleSheet(
            f"QPushButton{{background:{C['bg3']};color:{C['text']};border:1px solid {C['border']};"
            f"border-radius:5px;padding:5px 8px;font-size:{S.f(9)}px;font-weight:bold;}}"
            f"QPushButton:disabled{{color:{C['text2']};}}"
        )
        self.btn_reset_feature_set = QPushButton("원복")
        self.btn_reset_feature_set.setCursor(Qt.PointingHandCursor)
        self.btn_reset_feature_set.setStyleSheet(
            f"QPushButton{{background:{C['bg']};color:{C['orange']};"
            f"border:1px solid {C['orange']};border-radius:5px;padding:5px 8px;"
            f"font-size:{S.f(9)}px;font-weight:bold;}}"
            f"QPushButton:disabled{{color:{C['text2']};border-color:{C['border']};}}"
        )
        btn_row.addWidget(self.btn_apply_candidate, 2)
        btn_row.addWidget(self.btn_force_retrain, 2)
        btn_row.addWidget(self.btn_reset_feature_set, 1)
        action_lay.addLayout(btn_row)
        root.addWidget(action_box)
        self.btn_apply_candidate.clicked.connect(self.sig_apply_candidate_requested.emit)
        self.btn_force_retrain.clicked.connect(self.sig_force_retrain_requested.emit)
        self.btn_reset_feature_set.clicked.connect(self.sig_reset_feature_set_requested.emit)

    # ── 상태 색상 결정 헬퍼 ─────────────────────────────────────
    @staticmethod
    def _status_color(status: str) -> str:
        return {
            "핵심":     "#3fb950",
            "안정":     "#58a6ff",
            "주의":     "#e3b341",
            "약화":     "#f85149",
            "모니터":   "#8b949e",
            "교체후보": "#a371f7",
            "유지":     "#58a6ff",
            "복원":     "#8b949e",
        }.get(status, "#8b949e")

    def _update_core_group(self, group: str, items: list) -> int:
        """그룹별 CORE 행 업데이트. 통과 수 반환."""
        rows  = self._core_rows[group]
        color = self._GRP_COLOR[group]
        ok_count = 0
        for i, (nlab, bar, vlab, slab, xlab) in enumerate(rows):
            if i < len(items):
                item  = items[i]
                val   = float(item.get("shap", 0.0) or 0.0)
                stat  = str(item.get("status", "모니터"))
                scol  = self._status_color(stat)
                xcol  = "#e3b341"
                xtxt  = item.get("extra", "")
                nlab.setText(str(item.get("name", "——"))[:14])
                bar.setValue(min(int(val * 100), 100))
                bar.setStyleSheet(
                    f"QProgressBar::chunk{{background:{scol};}}"
                    f"QProgressBar{{border:none;background:{C['bg3']};border-radius:2px;}}"
                )
                vlab.setText(f"{val*100:.1f}%")
                vlab.setStyleSheet(f"color:{scol};font-size:{S.f(9)}px;font-weight:bold;")
                slab.setText(stat)
                slab.setStyleSheet(f"color:{scol};font-size:{S.f(8)}px;")
                if item.get("forced_x"):
                    xtxt = "★강제X"
                    xcol = "#39d3bb"
                xlab.setText(xtxt)
                xlab.setStyleSheet(f"color:{xcol};font-size:{S.f(8)}px;")
                if stat not in ("약화", "모니터"):
                    ok_count += 1
            else:
                nlab.setText("——"); bar.setValue(0); vlab.setText("—%")
                slab.setText("——"); xlab.setText("")
        return ok_count

    # ── Phase C: CORE × 호라이즌 매트릭스 ──────────────────────────
    # 표시할 CORE 피처 (내부키, 표시명) — 행 순서
    _MATRIX_FEATS = [
        ("cvd_divergence", "CVD"),
        ("vwap_position",  "VWAP"),
        ("ofi_norm",       "OFI"),
        ("macro_vix",      "VIX"),
        ("opt_chain_pcr",  "PCR"),
    ]
    _MATRIX_HZ    = ["1m", "3m", "5m", "10m", "15m", "30m"]
    _HZ_COLOR_MAP = {
        "1m": "#39d3bb", "3m": "#39d3bb", "5m": "#39d3bb",
        "10m": "#e3b341", "15m": "#e3b341",
        "30m": "#a371f7",
    }

    def _build_matrix(self, parent_lay: "QVBoxLayout") -> None:
        """CORE × 호라이즌 신호 매트릭스 위젯 생성 후 parent_lay에 추가."""
        from PyQt5.QtWidgets import QGridLayout, QGroupBox

        try:
            from features.horizon_feature_registry import get_feature_set, get_exclude_set
        except Exception:
            return  # 레지스트리 미로드 시 스킵

        mat_grp = QGroupBox("▶ CORE × 호라이즌 신호 매트릭스")
        mat_grp.setStyleSheet(
            f"QGroupBox{{color:{C['text2']};border:1px solid {C['border']};"
            f"border-radius:5px;margin-top:4px;font-size:{S.f(8)}px;}}"
            f"QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 4px;"
            f"background:{C['bg']};}}"
        )
        mat_grp.setToolTip(
            "● include — 해당 호라이즌 모델에 포함\n"
            "○ pending — 검증 완료 후 추가 예정\n"
            "✕ exclude — 명시적 제거 (잡음·무효)\n"
            "— 미해당 — 포함/제거 명시 없음\n\n"
            "현재 진입 호라이즌 열이 밝게 강조됩니다."
        )

        grid = QGridLayout(mat_grp)
        grid.setSpacing(2)
        grid.setContentsMargins(4, 12, 4, 6)

        # 열 헤더
        self._hz_col_headers = {}
        for col, hz in enumerate(self._MATRIX_HZ):
            col_color = self._HZ_COLOR_MAP[hz]
            lbl = mk_label(hz, col_color, S.f(8), True)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedWidth(S.p(32))
            grid.addWidget(lbl, 0, col + 1)
            self._hz_col_headers[hz] = lbl

        # 행 헤더 + 셀
        self._matrix_cells = {}
        for row, (feat, short_name) in enumerate(self._MATRIX_FEATS):
            row_hdr = mk_label(short_name, C['text2'], S.f(8))
            row_hdr.setFixedWidth(S.p(44))
            row_hdr.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid.addWidget(row_hdr, row + 1, 0)

            for col, hz in enumerate(self._MATRIX_HZ):
                inc_set   = set(get_feature_set(hz) or [])
                pend_all  = set(get_feature_set(hz, include_pending=True) or [])
                pend_only = pend_all - inc_set
                exc_set   = get_exclude_set(hz)
                col_color = self._HZ_COLOR_MAP[hz]

                if feat in inc_set:
                    symbol, color = "●", col_color
                    tooltip = f"{feat} — {hz} 모델 포함"
                elif feat in pend_only:
                    symbol, color = "○", col_color + "99"
                    tooltip = f"{feat} — {hz} pending (검증 후 추가)"
                elif feat in exc_set:
                    symbol, color = "✕", "#f85149"
                    tooltip = f"{feat} — {hz} 명시 제거 (잡음·무효)"
                else:
                    symbol, color = "—", "#383f47"
                    tooltip = f"{feat} — {hz} 미해당"

                cell = mk_label(symbol, color, S.f(11), symbol in ("●", "○"))
                cell.setAlignment(Qt.AlignCenter)
                cell.setFixedWidth(S.p(32))
                cell.setToolTip(tooltip)
                grid.addWidget(cell, row + 1, col + 1)
                self._matrix_cells[(feat, hz)] = (cell, symbol, color)

        # 범례 한 줄
        leg = QHBoxLayout()
        leg.setSpacing(10)
        leg.setContentsMargins(4, 2, 4, 0)
        for sym, label, col in [
            ("●", "포함",    "#39d3bb"),
            ("○", "pending", "#8b949e"),
            ("✕", "제거",    "#f85149"),
            ("—", "미해당",  "#383f47"),
        ]:
            leg.addWidget(mk_label(f"{sym} {label}", col, S.f(7)))
        leg.addStretch()
        leg_w = QWidget()
        leg_w.setLayout(leg)
        leg_w.setStyleSheet("background:transparent;")

        wrap = QVBoxLayout()
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.setSpacing(2)
        wrap.addWidget(mat_grp)
        wrap.addWidget(leg_w)
        parent_lay.addLayout(wrap)

    def update_entry_horizon(self, hz: str = "1m") -> None:
        """매분 진입 호라이즌 배지 + 그룹 강조 + 매트릭스 열 강조 업데이트."""
        from config.settings import HORIZON_CORE_GROUP
        grp = HORIZON_CORE_GROUP.get(hz, "short")
        hz_display = hz if hz else "—"
        if self._lbl_hz is not None:
            self._lbl_hz.setText(hz_display)
            col = self._GRP_COLOR.get(grp, C['cyan'])
            self._lbl_hz.setStyleSheet(
                f"color:{col};font-size:{S.f(11)}px;font-weight:bold;"
            )
        # 해당 그룹 섹션 강조, 나머지 흐리게
        for g, box in self._grp_boxes.items():
            if g == grp:
                box.setStyleSheet(self._grp_box_style(self._GRP_COLOR[g], self._GRP_BG[g]))
            else:
                box.setStyleSheet(self._grp_box_style_dim(self._GRP_COLOR[g]))

        # 매트릭스 열 헤더 강조
        for col_hz, lbl in getattr(self, "_hz_col_headers", {}).items():
            base = self._HZ_COLOR_MAP.get(col_hz, C['text2'])
            if col_hz == hz:
                lbl.setStyleSheet(
                    f"color:#ffffff;background:{base}55;border-radius:3px;"
                    f"font-size:{S.f(8)}px;font-weight:bold;padding:1px 2px;"
                )
            else:
                lbl.setStyleSheet(
                    f"color:{base};font-size:{S.f(8)}px;font-weight:bold;"
                )

        # 매트릭스 셀 강조: 현재 호라이즌 열의 포함(●) 셀만 배경 밝게
        for (feat, cell_hz), (cell, symbol, orig_col) in \
                getattr(self, "_matrix_cells", {}).items():
            if cell_hz == hz and symbol in ("●", "○"):
                cell.setStyleSheet(
                    f"color:#ffffff;background:{orig_col}44;border-radius:2px;"
                    f"font-size:{S.f(11)}px;font-weight:bold;"
                )
            else:
                cell.setStyleSheet(
                    f"color:{orig_col};font-size:{S.f(11)}px;"
                    + ("font-weight:bold;" if symbol in ("●",) else "")
                )

    def update_shap(
        self,
        core_items,                 # 단기 CORE 아이템 목록 (하위 호환)
        dynamic_items,
        rank_items,
        cooldown=None,
        change_lines=None,
        action_state=None,
        mid_core_items=None,        # 중기 CORE 아이템 (Phase A·B 신규)
        long_core_items=None,       # 장기 CORE 아이템
        entry_horizon="1m",         # 현재 진입 호라이즌
    ):
        # ① 호라이즌 배지 + 그룹 강조
        self.update_entry_horizon(entry_horizon)

        # ② 단기 CORE
        short_ok = self._update_core_group("short", list(core_items or []))

        # ③ 중기 CORE
        mid_items_use = list(mid_core_items or [])
        mid_ok = self._update_core_group("mid", mid_items_use)

        # ④ 장기 CORE
        long_items_use = list(long_core_items or [])
        long_ok = self._update_core_group("long", long_items_use)

        # ⑤ 요약 라벨 업데이트
        short_total = len(self._core_rows["short"])
        mid_total   = len(self._core_rows["mid"])
        long_total  = len(self._core_rows["long"])
        def _dot(ok, total):
            return ("●" if ok == total else "⚠") + f" {ok}/{total}"
        summary = (
            f"단기 {_dot(short_ok, short_total)}  "
            f"중기 {_dot(mid_ok, mid_total)}  "
            f"장기 {_dot(long_ok, long_total)}"
        )
        all_ok = (short_ok == short_total and mid_ok == mid_total and long_ok == long_total)
        if self._lbl_summary is not None:
            self._lbl_summary.setText(summary)
            self._lbl_summary.setStyleSheet(
                f"color:{'#3fb950' if all_ok else '#e3b341'};font-size:{S.f(8)}px;"
            )

        # ⑥ 동적 TOP3
        for i, (rank, nlab, bar, vlab, slab) in enumerate(self.dynamic_rows):
            if i < len(dynamic_items):
                item = dynamic_items[i]
                stat = str(item.get("status", "——"))
                scol = self._status_color(stat)
                rank.setText(f"#{item.get('rank', i+1)}")
                nlab.setText(str(item.get("name", "-"))[:14])
                val = float(item.get("shap", 0.0) or 0.0)
                bar.setValue(min(int(val * 100), 100))
                bar.setStyleSheet(
                    f"QProgressBar::chunk{{background:{scol};}}"
                    f"QProgressBar{{border:none;background:{C['bg3']};border-radius:2px;}}"
                )
                vlab.setText(f"{val*100:.1f}%")
                vlab.setStyleSheet(f"color:{scol};font-size:{S.f(9)}px;")
                slab.setText(stat)
                slab.setStyleSheet(f"color:{scol};font-size:{S.f(8)}px;")
            else:
                rank.setText("—"); nlab.setText("-")
                bar.setValue(0); vlab.setText("—%"); slab.setText("——")

        # ⑦ 전체 순위
        for i, (nl, bar, vlab) in enumerate(self.rank_labels):
            if i < len(rank_items):
                item = rank_items[i]
                nl.setText(str(item.get("name", "-"))[:10])
                val = float(item.get("shap", 0.0) or 0.0)
                bar.setValue(min(int(val * 100), 100))
                vlab.setText(f"{val*100:.1f}%")
            else:
                nl.setText("-"); bar.setValue(0); vlab.setText("—%")

        # ⑧ 쿨다운
        cooldown = cooldown or {}
        self.cooldown_bar.setValue(int(cooldown.get("progress", 0) or 0))
        self.cooldown_lbl.setText(str(cooldown.get("label", "없음")))

        # ⑨ 교체 이력
        lines = list(change_lines or [])
        self.change_log.setPlainText("\n".join(lines) if lines else "기록 없음")

        # ⑩ 운영 액션
        action_state = action_state or {}
        self.review_summary.setText(str(action_state.get("summary", "추천 후보를 점검하는 중")))
        self.btn_apply_candidate.setEnabled(bool(action_state.get("can_apply", False)))
        self.btn_force_retrain.setEnabled(bool(action_state.get("can_retrain", True)))
        self.btn_reset_feature_set.setEnabled(bool(action_state.get("can_reset", False)))

class ExitPanel(QWidget):
    sig_tp1_protect_mode_changed = pyqtSignal(str)
    sig_manual_exit_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._tp1_protect_mode = "atr_profit"
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
        lay.addWidget(mk_label("가격 구조 (실행 스톱 → 목표)", C['text2'], 9, True))
        level_tooltips = {
            "hard_stop": (
                "초기 하드 스톱\n"
                "진입 직후 최초로 설정되는 기본 손절선입니다.\n"
                "현재 기준: 진입가 ± ATR x 1.5"
            ),
            "struct_stop": (
                "현재 실행 스톱\n"
                "지금 실제 청산 판단에 사용하는 스톱 가격입니다.\n"
                "트레일링이 발동하면 이 값이 함께 이동합니다."
            ),
            "trail_stop": (
                "트레일링 기준 (4단계)\n"
                "수익 구간에 따라 스톱이 단계적으로 이동합니다.\n"
                "\n"
                "  1단계 ≥ 0.5 ATR → 손절 -0.75 ATR (무방비 지대 보호)\n"
                "  2단계 ≥ 1.0 ATR → 손절 = 진입가 (본전 보호)\n"
                "  3단계 ≥ 1.5 ATR → 손절 +0.5 ATR (최소 이익 확보)\n"
                "  4단계 ≥ 2.0 ATR → 최고점(앵커) - 1.0 ATR 추적"
            ),
        }
        levels = [
            ("초기 하드 스톱", "hard_stop",  C['red'],    "●"),
            ("현재 실행 스톱", "struct_stop",C['red'],    "●"),
            ("트레일링 기준",  "trail_stop", C['orange'], "●"),
            ("본전 (진입가)","breakeven",  C['text2'],  "●"),
            ("1차 목표 33%","target1",    C['green'],  "●"),
            ("2차 목표 33%","target2",    C['green'],  "●"),
            ("3차 목표 34%","target3",    "#085041",   "●"),
        ]
        for lbl, attr, col, dot in levels:
            r = QHBoxLayout()
            name_w = mk_label(f"{dot} {lbl}", col, 9)
            vl = mk_val_label("——.——", col, 10)
            tooltip = level_tooltips.get(attr, "")
            if tooltip:
                name_w.setToolTip(tooltip)
                vl.setToolTip(tooltip)
            setattr(self, f"lv_{attr}", vl)
            r.addWidget(name_w)
            r.addWidget(vl)
            if attr == "struct_stop":
                _reason_badge = mk_badge("초기스톱", C['bg3'], C['text2'], 8)
                self.lbl_stop_reason = _reason_badge
                r.addWidget(_reason_badge)
            elif attr == "trail_stop":
                _stage_lbl = mk_label("", C['text2'], 8)
                self.lbl_trail_stage = _stage_lbl
                r.addWidget(_stage_lbl)
            lay.addLayout(r)
            if attr == "struct_stop":
                _dist_lbl = mk_label("", C['text2'], 8)
                self.lbl_stop_distance = _dist_lbl
                lay.addWidget(_dist_lbl)

        lay.addWidget(mk_sep())

        # 청산 트리거 모니터
        lay.addWidget(mk_label("청산 실행 상태 모니터", C['orange'], 9, True))
        triggers = [
            ("1", "실행 스톱 감시",      "hard_trig"),
            ("2", "1계약 TP1 보호전환", "signal_trig"),
            ("3", "1차 목표 33%",       "cvd_trig"),
            ("3", "2차 목표 33%",       "shap_trig"),
            ("3", "3차 목표 34%",       "opt_trig"),
            ("2", "현재 스톱 가격",     "trail_trig"),
            ("3", "부분청산 진행",      "t1_trig"),
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
            if attr == "hard_trig":
                intra_st = mk_badge("인트라바-", C['bg3'], C['text2'], 8)
                self.st_intrabar_trig = intra_st
                r.addWidget(intra_st)
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
        lay.addWidget(mk_sep())

        lay.addWidget(mk_label("TP1 1\uacc4\uc57d \ubcf4\ud638\uc804\ud658 \uc124\uc815", C['cyan'], 9, True))
        self.tp1_mode_tips = {
            "breakeven": (
                "TP1 \ubcf8\uc808\ubcf4\ud638",
                "TP1 \ub3c4\ub2ec \uc2dc \uc2a4\ud1b1\uc744 \uc9c4\uc785\uac00\ub85c \uc62c\ub9bd\ub2c8\ub2e4.\n"
                "\uc190\uc2e4 \ud655\uc7a5\uc744 \ub9c9\ub294 \uac00\uc7a5 \ubcf4\uc218\uc801\uc778 1\uacc4\uc57d \ubcf4\ud638\ubaa8\ub4dc\uc785\ub2c8\ub2e4.",
            ),
            "breakeven_plus": (
                "\ubcf8\uc808+alpha",
                f"TP1 \ub3c4\ub2ec \uc2dc \uc2a4\ud1b1\uc744 \uc9c4\uc785\uac00\ubcf4\ub2e4 {TP1_PROTECT_PLUS_ALPHA_PTS:.2f}pt \uc720\ub9ac\ud558\uac8c \uc62c\ub9bd\ub2c8\ub2e4.\n"
                "\uc9e7\uc740 \uc774\uc775\uc774\ub77c\ub3c4 \uc7a0\uadf8\uace0 \uc2f6\uc744 \ub54c \uc4f0\ub294 \uc635\uc158\uc785\ub2c8\ub2e4.",
            ),
            "atr_profit": (
                "ATR \uae30\ubc18 \ubcf4\ud638\uc774\uc775",
                f"TP1 \ub3c4\ub2ec \uc2dc \uc2a4\ud1b1\uc744 ATR x {TP1_PROTECT_ATR_LOCK_MULT:.2f} \ub9cc\ud07c \uc720\ub9ac\ud558\uac8c \uc62c\ub9bd\ub2c8\ub2e4.\n"
                "\ubcc0\ub3d9\uc131\uc5d0 \ub9de\ucdb0 \ubcf4\ud638\ud3ed\uc744 \uc790\ub3d9 \uc870\uc815\ud558\ub294 \uc635\uc158\uc785\ub2c8\ub2e4.",
            ),
        }
        mode_title = mk_label("\uc120\ud0dd \uc635\uc158", C['text2'], 8)
        mode_title.setToolTip(
            "1\uacc4\uc57d \uc6b4\uc6a9\uc5d0\uc11c TP1 \ub3c4\ub2ec \ud6c4 \uc989\uc2dc \uc804\ub7c9\uccad\uc0b0\ud558\uc9c0 \uc54a\uace0,\n"
            "\ubcf4\ud638\uc804\ud658 \ubc29\uc2dd\ub9cc \ubc14\uafd4 \ud544\uc694\ud560 \ub54c \ud074\ub9ad\ud574\uc11c \uc0ac\uc6a9\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4."
        )
        lay.addWidget(mode_title)
        self.tp1_mode_btns = {}
        mode_lay = QHBoxLayout()
        for mode, (label, tooltip) in self.tp1_mode_tips.items():
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, m=mode: self.set_tp1_protect_mode(m))
            self.tp1_mode_btns[mode] = btn
            mode_lay.addWidget(btn)
        lay.addLayout(mode_lay)
        self._sync_tp1_mode_buttons()


        btn_lay = QHBoxLayout()
        self.manual_exit_btns = {}
        self.manual_exit_tooltips = {
            33: "\ud604\uc7ac \ubcf4\uc720 \ud3ec\uc9c0\uc158\uc758 33%\ub97c \uc2dc\uc7a5\uac00\ub85c \uccad\uc0b0\ud569\ub2c8\ub2e4.\n1\uacc4\uc57d \ubcf4\uc720 \uc2dc\uc5d0\ub294 \uc804\ub7c9 \uccad\uc0b0\uc73c\ub85c \ucc98\ub9ac\ub429\ub2c8\ub2e4.",
            50: "\ud604\uc7ac \ubcf4\uc720 \ud3ec\uc9c0\uc158\uc758 50%\ub97c \uc2dc\uc7a5\uac00\ub85c \uccad\uc0b0\ud569\ub2c8\ub2e4.\n1\uacc4\uc57d \ubcf4\uc720 \uc2dc\uc5d0\ub294 \uc804\ub7c9 \uccad\uc0b0\uc73c\ub85c \ucc98\ub9ac\ub429\ub2c8\ub2e4.",
            100: "\ud604\uc7ac \ubcf4\uc720 \ud3ec\uc9c0\uc158\uc744 \uc804\ub7c9 \uc2dc\uc7a5\uac00\ub85c \uccad\uc0b0\ud569\ub2c8\ub2e4.",
        }
        for label, pct, col in [("33% 청산", 33, C['green']),
                                  ("50% 청산", 50, C['orange']),
                                  ("전량 청산", 100, C['red'])]:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setEnabled(False)
            btn.setToolTip(self.manual_exit_tooltips.get(pct, ""))
            btn.clicked.connect(lambda checked, p=pct: self.sig_manual_exit_requested.emit(p))
            btn.setStyleSheet(
                f"QPushButton{{background:{C['bg3']};color:{col};"
                f"border:1px solid {col};border-radius:4px;padding:4px 8px;}}"
                f"QPushButton:hover{{background:{col};color:#000;}}"
            )
            self.manual_exit_btns[pct] = btn
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
        self.st_intrabar_trig.setText("인트라바-")
        self.st_intrabar_trig.setStyleSheet(_badge_reset_ss)
        self.lbl_stop_reason.setText("——")
        self.lbl_stop_reason.setStyleSheet(_badge_reset_ss)
        self.lbl_stop_distance.setText("")
        self.lbl_trail_stage.setText("")
        for bar_w, lbl_w in self.partial_bars:
            bar_w.setValue(0)
            lbl_w.setText("대기")
            lbl_w.setStyleSheet(f"color:{C['text2']};font-size:{S.f(11)}px;")

        for btn in getattr(self, "manual_exit_btns", {}).values():
            btn.setEnabled(False)

    def _sync_tp1_mode_buttons(self):
        for mode, btn in self.tp1_mode_btns.items():
            selected = mode == self._tp1_protect_mode
            col = C['cyan'] if selected else C['text2']
            bw = "2px" if selected else "1px"
            bg = C['bg2'] if selected else C['bg3']
            btn.setStyleSheet(
                f"QPushButton{{background:{bg};color:{col};"
                f"border:{bw} solid {col};border-radius:4px;padding:5px 8px;"
                f"font-size:{S.f(11)}px;}}"
                f"QPushButton:hover{{border:2px solid {C['cyan']};}}"
            )

        tip = self.tp1_mode_tips.get(self._tp1_protect_mode, ("", ""))[1]
        for btn in self.tp1_mode_btns.values():
            btn.setStatusTip(tip)

    def set_tp1_protect_mode(self, mode: str, emit_signal: bool = True):
        mode = str(mode or "atr_profit").strip().lower()
        if mode not in getattr(self, "tp1_mode_btns", {}):
            mode = "atr_profit"
        self._tp1_protect_mode = mode
        self._sync_tp1_mode_buttons()
        if emit_signal:
            self.sig_tp1_protect_mode_changed.emit(self._tp1_protect_mode)

    def get_tp1_protect_mode(self) -> str:
        return self._tp1_protect_mode

    def update_data(self, pos_data):
        if not pos_data:
            self._reset_display()
            return

        def _as_float(value, default=0.0):
            try:
                text = str(value).replace(",", "").strip()
                if not text:
                    return float(default)
                return float(text)
            except Exception:
                return float(default)

        def _as_int(value, default=0):
            try:
                text = str(value).replace(",", "").strip()
                if not text:
                    return int(default)
                return int(float(text))
            except Exception:
                return int(default)

        def _as_datetime(value):
            if value is None or value == "":
                return None
            if isinstance(value, datetime):
                return value
            try:
                return datetime.fromisoformat(str(value).strip())
            except Exception:
                return None

        status = str(pos_data.get('status', 'FLAT') or 'FLAT').strip().upper()
        if status == 'FLAT':
            self._reset_display()
            return

        entry  = _as_float(pos_data.get('entry', 0.0), 0.0)
        cur    = _as_float(pos_data.get('current', entry), entry)
        qty    = max(0, _as_int(pos_data.get('qty', 0), 0))
        atr    = max(0.0, _as_float(pos_data.get('atr', 1.0), 1.0))
        pt_value = max(0.0, _as_float(pos_data.get('pt_value', FUTURES_PT_VALUE), FUTURES_PT_VALUE))
        # stop = 현재 트레일링 스톱 (PositionTracker.stop_price)
        mult   = 1 if status == 'LONG' else -1
        stop   = _as_float(pos_data.get('stop',  entry - mult * atr * 1.5), entry - mult * atr * 1.5)
        trail_basis = _as_float(pos_data.get('trail_basis', stop), stop)
        tp1    = _as_float(pos_data.get('tp1',   entry + mult * atr * 1.0), entry + mult * atr * 1.0)
        tp2    = _as_float(pos_data.get('tp2',   entry + mult * atr * 1.5), entry + mult * atr * 1.5)
        tp3    = _as_float(pos_data.get('tp3',   entry + mult * atr * 2.5), entry + mult * atr * 2.5)
        # 방어로직: 체결 직후/동기화 경계에서 tp 값이 0으로 들어오면 오표시를 유발한다.
        # (예: LONG에서 cur>=0.0 이 항상 참이 되어 "3차 목표 도달"로 보임)
        if tp1 <= 0:
            tp1 = entry + mult * atr * 1.0
        if tp2 <= 0:
            tp2 = entry + mult * atr * 1.5
        if tp3 <= 0:
            tp3 = entry + mult * atr * 2.5
        stage_plan = tuple(pos_data.get('stage_plan', (0, 0, 0)) or (0, 0, 0))
        stop_move_reason = str(pos_data.get('stop_move_reason', '') or '')
        bar_low  = _as_float(pos_data.get('bar_low',  0.0), 0.0)
        bar_high = _as_float(pos_data.get('bar_high', 0.0), 0.0)

        # 진입가 / 현재가
        self.entry_price.setText(f"{entry:.2f}")
        self.cur_price.setText(f"{cur:.2f}")

        pnl_pts = (cur - entry) * mult
        pnl_krw = pnl_pts * qty * pt_value
        col = C['green'] if pnl_krw >= 0 else C['red']
        self.unreal_pnl.setText(f"{pnl_krw:+,.0f}원")
        self.unreal_pnl.setStyleSheet(f"color:{col};font-size:{S.f(14)}px;font-weight:bold;")

        # 보유 시간
        entry_time = _as_datetime(pos_data.get('entry_time'))
        if entry_time:
            mins = max(0, int((datetime.now() - entry_time).total_seconds() // 60))
            self.hold_time.setText(f"{mins}분")
        else:
            self.hold_time.setText("——")

        # 가격 구조 (실제 PositionTracker 값 기반)
        hard_stop   = entry - mult * atr * 1.5   # 최초 설정 하드스톱
        struct_stop = stop
        self.lv_hard_stop.setText(f"{hard_stop:.2f}")
        self.lv_struct_stop.setText(f"{struct_stop:.2f}")
        self.lv_trail_stop.setText(f"{trail_basis:.2f}")
        self.lv_breakeven.setText(f"{entry:.2f}")
        self.lv_target1.setText(f"{tp1:.2f}")
        self.lv_target2.setText(f"{tp2:.2f}")
        self.lv_target3.setText(f"{tp3:.2f}")

        # ── T2-2: 손절 이동 이유 배지 ────────────────────────────────
        _badge_ss = (
            f"border-radius:3px;font-size:{S.f(8)}px;padding:1px 5px;"
        )
        if stop_move_reason == "tp1_breakeven":
            self.lbl_stop_reason.setText("TP1→손익분기")
            self.lbl_stop_reason.setStyleSheet(
                f"background:{C['cyan']};color:#000;" + _badge_ss
            )
        elif stop_move_reason.startswith("open_position") or stop_move_reason in ("init", ""):
            self.lbl_stop_reason.setText("초기스톱")
            self.lbl_stop_reason.setStyleSheet(
                f"background:{C['bg3']};color:{C['text2']};" + _badge_ss
            )
        else:
            _short = stop_move_reason.split(":")[0][:10]
            self.lbl_stop_reason.setText(_short)
            self.lbl_stop_reason.setStyleSheet(
                f"background:{C['bg3']};color:{C['text2']};" + _badge_ss
            )

        # ── T2-4: 스톱까지 거리 ──────────────────────────────────────
        if stop > 0 and atr > 0:
            _dist_pts = abs(cur - stop)
            _dist_atr = _dist_pts / atr
            _dist_col = (
                C['red'] if _dist_atr < 0.5
                else (C['orange'] if _dist_atr < 1.0 else C['text2'])
            )
            self.lbl_stop_distance.setText(
                f"  스톱까지 {_dist_pts:.1f}pt ({_dist_atr:.1f} ATR)"
            )
            self.lbl_stop_distance.setStyleSheet(
                f"color:{_dist_col};font-size:{S.f(8)}px;"
            )
        else:
            self.lbl_stop_distance.setText("")

        # ── T2-3: 트레일링 단계 표시 ────────────────────────────────
        if atr > 0:
            _unreal_pts = (cur - entry) * mult
            if _unreal_pts >= atr * 2.0:
                _stage_text, _stage_col = "4단계(앵커)", C['green']
            elif _unreal_pts >= atr * 1.5:
                _stage_text, _stage_col = "3단계(+0.5ATR)", C['green']
            elif _unreal_pts >= atr * 1.0:
                _stage_text, _stage_col = "2단계(본전)", C['cyan']
            elif _unreal_pts >= atr * 0.5:
                _stage_text, _stage_col = "1단계(-0.75ATR)", C['orange']
            else:
                _stage_text, _stage_col = "초기(-1.5ATR)", C['text2']
            self.lbl_trail_stage.setText(_stage_text)
            self.lbl_trail_stage.setStyleSheet(
                f"color:{_stage_col};font-size:{S.f(8)}px;"
            )
        else:
            self.lbl_trail_stage.setText("")

        # 부분 청산 진행
        p1 = pos_data.get('partial1', False)
        p2 = pos_data.get('partial2', False)
        p3 = pos_data.get('partial3', False)
        for i, (bar_w, lbl_w) in enumerate(self.partial_bars):
            done = (i == 0 and p1) or (i == 1 and p2) or (i == 2 and p3)
            bar_w.setValue(100 if done else 0)
            planned_qty = stage_plan[i] if i < len(stage_plan) else 0
            base_text = "완료" if done else "대기"
            lbl_w.setText(f"{base_text} ({planned_qty}계약)" if planned_qty > 0 else base_text)
            lbl_w.setStyleSheet(
                f"color:{C['green'] if done else C['text2']};font-size:{S.f(11)}px;"
            )

        def _set_trigger_badge(widget, text, bg, fg):
            widget.setText(text)
            widget.setStyleSheet(
                f"background:{bg};color:{fg};border-radius:3px;font-size:{S.f(10)}px;padding:1px 5px;"
            )

        def _set_trigger_state(widget, state: TriggerBadgeState, text: str = ""):
            label = text or state.value
            if state == TriggerBadgeState.DONE:
                _set_trigger_badge(widget, label, C['green'], "#000")
            elif state == TriggerBadgeState.CALCULATING:
                _set_trigger_badge(widget, label, C['blue'], "#000")
            elif state == TriggerBadgeState.HIT:
                _set_trigger_badge(widget, label, C['green'], "#000")
            elif state == TriggerBadgeState.WARNING:
                _set_trigger_badge(widget, label, C['red'], "#fff")
            elif state == TriggerBadgeState.EXECUTING:
                _set_trigger_badge(widget, label, C['orange'], "#000")
            elif state == TriggerBadgeState.PROTECT:
                _set_trigger_badge(widget, label, C['cyan'], "#000")
            elif state == TriggerBadgeState.WAIT:
                _set_trigger_badge(widget, label, C['bg3'], C['text2'])
            else:
                _set_trigger_badge(widget, label, C['bg3'], C['text2'])

        hit_stop = (cur <= stop) if status == 'LONG' else (cur >= stop)
        hit_tp1 = (cur >= tp1) if status == 'LONG' else (cur <= tp1)
        hit_tp2 = (cur >= tp2) if status == 'LONG' else (cur <= tp2)
        hit_tp3 = (cur >= tp3) if status == 'LONG' else (cur <= tp3)

        pending_active = bool(pos_data.get('pending_active', False))
        pending_kind = str(pos_data.get('pending_kind', '') or '').upper()
        pending_reason = str(pos_data.get('pending_reason', '') or '')
        pending_filled = _as_int(pos_data.get('pending_filled', 0), 0)
        pending_qty = _as_int(pos_data.get('pending_qty', 0), 0)
        pending_progress = f" {pending_filled}/{pending_qty}" if pending_qty > 0 else ""

        # ENTRY 체결 진행중에는 목표 도달 판정을 잠가 오표시를 방지한다.
        # (분할체결 중 평균가/TP가 재계산되는 경계에서 일시적인 false positive 방지)
        if pending_active and pending_kind == "ENTRY":
            hit_tp1 = False
            hit_tp2 = False
            hit_tp3 = False

        # ── T2-1: 인트라바 스톱 배지 ────────────────────────────────
        if bar_low > 0 and bar_high > 0 and stop > 0:
            if status == 'LONG':
                _intra_hit = bar_low <= stop
                _intra_gap = bar_low - stop      # 음수 = 히트
            else:
                _intra_hit = bar_high >= stop
                _intra_gap = stop - bar_high     # 음수 = 히트
            if _intra_hit:
                _set_trigger_badge(self.st_intrabar_trig, "인트라바↓", C['red'], "#fff")
            elif atr > 0 and abs(_intra_gap) < atr * 0.3:
                _set_trigger_badge(self.st_intrabar_trig,
                                   f"근접{_intra_gap:.1f}", C['orange'], "#000")
            else:
                _set_trigger_badge(self.st_intrabar_trig,
                                   f"여유{_intra_gap:.1f}", C['bg3'], C['text2'])
        else:
            _set_trigger_badge(self.st_intrabar_trig, "—", C['bg3'], C['text2'])

        # 기본 상태
        _set_trigger_state(self.st_hard_trig, TriggerBadgeState.WARNING if hit_stop else TriggerBadgeState.MONITORING)
        _set_trigger_state(self.st_signal_trig, TriggerBadgeState.PROTECT if (qty == 1 and p1) else TriggerBadgeState.WAIT)
        if pending_active and pending_kind == "ENTRY":
            _set_trigger_state(self.st_cvd_trig, TriggerBadgeState.CALCULATING)
            _set_trigger_state(self.st_shap_trig, TriggerBadgeState.CALCULATING)
            _set_trigger_state(self.st_opt_trig, TriggerBadgeState.CALCULATING)
        else:
            _set_trigger_state(self.st_cvd_trig, TriggerBadgeState.DONE if p1 else (TriggerBadgeState.HIT if hit_tp1 else TriggerBadgeState.MONITORING))
            _set_trigger_state(self.st_shap_trig, TriggerBadgeState.DONE if p2 else (TriggerBadgeState.HIT if hit_tp2 else TriggerBadgeState.MONITORING))
            _set_trigger_state(self.st_opt_trig, TriggerBadgeState.DONE if p3 else (TriggerBadgeState.HIT if hit_tp3 else TriggerBadgeState.MONITORING))
        _set_trigger_badge(self.st_trail_trig, f"{stop:.2f}", C['orange'], "#000")
        _set_trigger_state(self.st_t1_trig, TriggerBadgeState.DONE if p1 else TriggerBadgeState.WAIT)

        # 시간청산 카운트다운
        time_left_sec = _as_int(pos_data.get('time_exit_countdown_sec', -1), -1)
        if time_left_sec < 0:
            _set_trigger_state(self.st_time_trig, TriggerBadgeState.MONITORING)
        elif time_left_sec == 0:
            _set_trigger_state(self.st_time_trig, TriggerBadgeState.WARNING, "발동")
        else:
            mm, ss = divmod(time_left_sec, 60)
            if time_left_sec <= 300:
                _set_trigger_state(self.st_time_trig, TriggerBadgeState.WARNING, f"임박 {mm:02d}:{ss:02d}")
            else:
                _set_trigger_state(self.st_time_trig, TriggerBadgeState.MONITORING, f"T-{mm:02d}:{ss:02d}")

        # pending 주문중 상태를 우선 반영
        if pending_active and pending_kind.startswith("EXIT"):
            _set_trigger_state(self.st_hard_trig, TriggerBadgeState.EXECUTING, f"주문중{pending_progress}")
            if pending_kind in ("EXIT_PARTIAL", "EXIT_MANUAL_PARTIAL"):
                _p_stage = int(pos_data.get('pending_stage', 0))
                # 현재 주문 중인 TP 행에 "주문중" 오버레이
                if _p_stage == 1:
                    _set_trigger_state(self.st_cvd_trig, TriggerBadgeState.EXECUTING, f"주문중{pending_progress}")
                    # TP1 처리 중 — 상위 TP의 "도달" 오표시를 "대기"로 교체
                    if not p2:
                        _set_trigger_state(self.st_shap_trig, TriggerBadgeState.WAIT, "대기")
                    if not p3:
                        _set_trigger_state(self.st_opt_trig, TriggerBadgeState.WAIT, "대기")
                elif _p_stage == 2:
                    _set_trigger_state(self.st_shap_trig, TriggerBadgeState.EXECUTING, f"주문중{pending_progress}")
                    # TP2 처리 중 — TP3의 "도달" 오표시를 "대기"로 교체
                    if not p3:
                        _set_trigger_state(self.st_opt_trig, TriggerBadgeState.WAIT, "대기")
                elif _p_stage == 3:
                    _set_trigger_state(self.st_opt_trig, TriggerBadgeState.EXECUTING, f"주문중{pending_progress}")
                _set_trigger_state(self.st_t1_trig, TriggerBadgeState.EXECUTING, f"주문중{pending_progress}")
            if "15:10" in pending_reason or "시간청산" in pending_reason:
                _set_trigger_state(self.st_time_trig, TriggerBadgeState.EXECUTING, f"주문중{pending_progress}")

        # EXIT_FULL 주문 진행 중에는 수동 버튼 비활성화 (중복 주문 방지)
        # EXIT_PARTIAL / EXIT_MANUAL_PARTIAL은 허용 — 긴급 전량 청산이 필요할 수 있음
        _full_exit_pending = pending_active and pending_kind == "EXIT_FULL"
        for btn in getattr(self, "manual_exit_btns", {}).values():
            btn.setEnabled(not _full_exit_pending)


# ────────────────────────────────────────────────────────────
# 패널 5: 진입 관리 패널
# ────────────────────────────────────────────────────────────
class EntryPanel(QWidget):
    sig_reverse_entry_toggled    = pyqtSignal(bool)
    sig_manual_entry_requested   = pyqtSignal(str)   # "LONG" or "SHORT"
    sig_instant_exit_requested   = pyqtSignal()      # 즉시 전량청산
    sig_auto_mode_changed        = pyqtSignal(bool)  # True=Auto ON, False=Auto OFF
    sig_max_qty_changed          = pyqtSignal(int)   # 최대허용수량 변경
    sig_layer2_gate_toggled      = pyqtSignal(bool)  # Layer 2 게이트 ON/OFF

    _TIME_ZONE_DESC = {
        "GAP_OPEN": "시초가 급변 - 고신뢰·소규모 진입만 허용",
        "OPEN_VOLATILE": "변동성 高 - 추세추종, 신뢰도 상향",
        "STABLE_TREND": "안정 추세 - 표준 앙상블",
        "LUNCH_RECOVERY": "외인 재진입 감지",
        "CLOSE_VOLATILE": "마감 가속/청산 구간",
        "EXIT_ONLY": "신규 진입 금지",
        "OTHER": "장외/비허용 구간 - 신규 진입 차단",
    }
    _TIME_ZONE_LABEL = {
        "GAP_OPEN": "GAP OPEN",
        "OPEN_VOLATILE": "OPEN VOL",
        "STABLE_TREND": "STABLE",
        "LUNCH_RECOVERY": "LUNCH",
        "CLOSE_VOLATILE": "CLOSE VOL",
        "EXIT_ONLY": "EXIT ONLY",
    }
    _TIME_ZONE_ORDER = [
        "GAP_OPEN",
        "OPEN_VOLATILE",
        "STABLE_TREND",
        "LUNCH_RECOVERY",
        "CLOSE_VOLATILE",
        "EXIT_ONLY",
    ]
    _TIME_ZONE_COLOR = {
        "GAP_OPEN": "#E6C15A",
        "OPEN_VOLATILE": "#F39C12",
        "STABLE_TREND": "#2ECC71",
        "LUNCH_RECOVERY": "#58A6FF",
        "CLOSE_VOLATILE": "#FF8C42",
        "EXIT_ONLY": "#FF6B6B",
        "OTHER": "#7F8C8D",
    }

    def __init__(self):
        super().__init__()
        self.current_mode = "hybrid"
        self._reverse_entry_enabled = False
        self._auto_enabled = True
        self._layer2_gate_enabled: bool = True
        self._contrarian_hint: bool = False
        self._contrarian_direction: str = ""
        self._blink_on: bool = False
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(500)
        self._blink_timer.timeout.connect(self._on_blink_tick)
        self._entry_blink_on: bool = False
        self._entry_blink_timer = QTimer(self)
        self._entry_blink_timer.setInterval(600)
        self._entry_blink_timer.timeout.connect(self._on_entry_blink_tick)
        # 추세 지속 게이트 깜빡임 (UP=녹색 / DN=오렌지)
        self._trend_gate_mode: str = ""    # "" / "UP" / "DN"
        self._trend_blink_on:  bool = False
        self._trend_blink_timer = QTimer(self)
        self._trend_blink_timer.setInterval(600)
        self._trend_blink_timer.timeout.connect(self._on_trend_blink_tick)
        self._time_router = TimeStrategyRouter()
        self._mode_button_labels = {
            "auto": "A 등급진입",
            "hybrid": "B 등급진입",
            "manual": "C 등급진입",
        }
        self._max_qty = self._load_max_qty()
        self._build()
        self._load_entry_mode()         # _build() 완료 후 위젯 존재 보장 상태에서 복원
        self._setup_time_zone_timer()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(mk_label("자동 진입관리 패널", C['green'], 10, True))

        # Auto On/Off + 모드 선택
        mode_lay = QHBoxLayout()

        self.auto_toggle_btn = QPushButton("Auto ON")
        self.auto_toggle_btn.setCheckable(True)
        self.auto_toggle_btn.setChecked(True)
        self.auto_toggle_btn.toggled.connect(self._set_auto_enabled)
        self._sync_auto_toggle_style()
        mode_lay.addWidget(self.auto_toggle_btn)

        self.mode_btns = {}
        for mode, label in self._mode_button_labels.items():
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
        self._sync_mode_button_styles()

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
            "",
            C['blue'], 9
        )
        self.mode_desc.setWordWrap(True)
        lay.addWidget(self.mode_desc)

        zone_grid = QGridLayout()
        zone_grid.setHorizontalSpacing(6)
        zone_grid.setVerticalSpacing(4)
        self.time_zone_btns = {}
        for idx, zone in enumerate(self._TIME_ZONE_ORDER):
            btn = QPushButton()
            btn.setEnabled(False)
            btn.setMinimumHeight(30)
            btn.setCursor(Qt.ArrowCursor)
            self.time_zone_btns[zone] = btn
            zone_grid.addWidget(btn, idx // 3, idx % 3)
        lay.addLayout(zone_grid)

        self._update_mode_desc()
        lay.addWidget(mk_sep())


        # 앙상블 + 신뢰도 (row0: 2카드, row1: 3카드, row2: 수량)
        info_vlay = QVBoxLayout()
        info_vlay.setSpacing(4)
        info_row0 = QHBoxLayout()
        info_row0.setSpacing(4)
        info_row1 = QHBoxLayout()
        info_row1.setSpacing(4)
        _TIP_META_GATE = (
            "  ③ 메타 게이트 (MetaGate)\n"
            "     '지금 상황이 예측하기 좋은 상황인가'를 별도 추정\n"
            "\n"
            "     [STEP 1] 9개 컨텍스트 피처 벡터 구성\n"
            "       미시레짐   : 추세장=1.0 / 횡보장=-1.0 / 급변장=-2.0 / 혼합=0.0\n"
            "       Hurst 지수 : 0.6↑ 추세성 강함 / 0.45↓ 랜덤 워크\n"
            "       ATR 비율   : 현재ATR / 평균ATR (2.0↑이면 -0.20 패널티)\n"
            "       시간대     : <10:30=1.0 / <14:00=0.0 / <15:00=-0.5 / 이후=-1.0\n"
            "       LOB 불균형 : mlofi_norm (-1~+1)\n"
            "       VPIN 프록시: cancel_add_ratio 기반 (0~1, 0.7↑이면 +0.05)\n"
            "       최근 정확도: 최근 20회 정답률\n"
            "       신호 강도  : 앙상블 confidence\n"
            "       정확도 추세: 최근 5분 평균 − 이전 5분 평균\n"
            "\n"
            "     [STEP 2] 메타 신뢰도 예측\n"
            "       샘플≥50건: SGD Classifier → P(이번 예측이 정답)\n"
            "       미학습 fallback: 규칙 기반 점수 합산 (기본 0.6)\n"
            "       메타 사이즈 배율: conf≥0.7→1.0~1.5× / 0.5~0.7→0.5~1.0× / <0.5→0×\n"
            "\n"
            "     [STEP 3] 블렌딩 + 액션 결정\n"
            "       blended = 앙상블×0.6 + 메타×0.4\n"
            "       blended ≥0.67 → take   (size 0.90~1.25×)\n"
            "       0.56~0.67     → reduce (size 0.35~0.75×)\n"
            "       <0.56         → skip   (차단)\n"
            "       매분 결과 피드백으로 온라인 자가학습 (50건 후 SGD 전환)"
        )
        _TIP_RAW_SIGNAL = (
            "【원신호】\n"
            "앙상블이 계산한 순수 방향 예측값 (필터 적용 전)\n"
            "\n"
            "생성 흐름:\n"
            "  6개 호라이즌(1·3·5·10·15·30분) 예측\n"
            "  → 상관관계 역수 가중합 (15분마다 재계산)\n"
            "  → 레짐별 최소 신뢰도 미달 시 FLAT 처리\n"
            "     RISK_ON 52% / NEUTRAL 58% / RISK_OFF 65%\n"
            "\n"
            "역방향진입 ON 상태에서도 원신호는 미륵이의\n"
            "순방향 판단 그대로 표시됨 (학습·통계 기준값)\n"
            "\n"
            "※ 이 값이 실행신호로 확정되려면 아래 3개 필터 통과 필요\n"
            "  ① 시간대 필터  ② 9개 체크리스트  ③ 메타 게이트\n"
            "\n"
            + _TIP_META_GATE
        )
        _TIP_FINAL_SIGNAL = (
            "【실행신호】\n"
            "원신호가 아래 필터를 모두 통과한 뒤 최종 확정된 주문 방향\n"
            "\n"
            "필터 순서:\n"
            "  ① 시간대 필터 (TimeStrategyRouter)\n"
            "     EXIT_ONLY(15:00~15:10) · OTHER → 차단\n"
            "     LUNCH_RECOVERY(13:00~14:00) → conf≥60% · size×0.90\n"
            "\n"
            "  ② 9개 체크리스트 → 등급 판정\n"
            "     VWAP위치 · CVD방향 · OFI압력 · 외인방향\n"
            "     직전봉방향 · 신뢰도 · 시간대 · 일일손실<2%\n"
            "     A(6↑) / B(4~5) / C(2~3) / X(1↓)\n"
            "     ※ 단기(1~5m): VWAP ✗ → 강제 X | CVD·OFI ✗ → 등급 하락\n     ※ 중기(10~15m): VWAP ✗ → 강제 X | macro_vix 대체\n     ※ 장기(30m): VWAP 강제X 해제, GEX·PCR 대체\n"
            "\n"
            + _TIP_META_GATE + "\n"
            "\n"
            "역방향진입 ON 시: 원신호 방향을 뒤집어 주문\n"
            "  (원신호=매수 → 실행신호=매도, 반대도 동일)"
        )
        _TIP_ENS_GRADE = (
            "【앙상블 등급】\n"
            "6개 호라이즌(1/3/5/10/15/30분) 예측의 앙상블 결과 등급\n"
            "(EnsembleDecision.compute() 직접 반환값)\n"
            "\n"
            "  A : 신뢰도 ≥ 70%  — 강한 방향성\n"
            "  B : 신뢰도 ≥ 레짐 임계값  — 진입 가능\n"
            "  C : 신뢰도 ≥ 레짐 임계값  — 약한 방향성\n"
            "  X : 아래 조건 중 하나라도 해당 시 차단\n"
            "\n"
            "  X 등급 발생 조건 (우선순위 순)\n"
            "  ① CoherenceGate 차단\n"
            "       방향성 호라이즌 중 동방향 비율 < 60%\n"
            "       (FLAT 예측 호라이즌 제외 후 계산)\n"
            "       예: DN=3, UP=1, FL=2 → FLAT 제외 후 3/4=75% → 통과\n"
            "           DN=2, UP=2, FL=2 → FLAT 제외 후 2/4=50% → 차단\n"
            "  ② 레짐 임계값 미달\n"
            "       confidence < REGIME_MIN_CONFIDENCE[regime]\n"
            "  ③ FLAT 방향\n"
            "\n"
            "  레짐별 임계값 (동적 갱신 — mc_history.db 기반)\n"
            "    RISK_ON  → 동적 base_mc\n"
            "    NEUTRAL  → 동적 base_mc  (기존 고정값 대비 낮아짐)\n"
            "    RISK_OFF → 0.65 (고정)\n"
            "\n"
            "  F1 적응형 가중치 (HorizonF1AdaptiveWeight)\n"
            "    최근 예측 결과로 각 호라이즌의 EMA 정확도 추적\n"
            "    F1이 낮은 호라이즌 가중치 자동 감소 (f1² 비례)"
        )
        _TIP_CONF = (
            "【진입 등급 (체크리스트)】\n"
            "9개 체크리스트 통과 수 기반 등급\n"
            "\n"
            "  A : 6개↑ 통과 → ×1.5 자동진입\n"
            "  B : 4~5개 통과 → ×1.0 자동진입\n"
            "  C : 2~3개 통과 → ×0.6 수동확인\n"
            "  X : 1개↓ 통과 → 진입금지\n"
            "\n"
            "  ※ CORE 3개(VWAP·CVD·OFI) 중 하나라도 ✗ → 강제 X등급\n"
            "  ※ 각종 게이트(Health·ExecutionGovernor·MetaGate·ToxicityGate\n"
            "     ProfitGuard·IntradayRegime) 차단 시 X로 강제 변경"
        )
        _TIP_FINAL_ENTRY = (
            "【최종진입 판정】\n"
            "앙상블 등급 + 체크리스트 등급을 종합한 최종 진입 여부\n"
            "\n"
            "  진입    : 최종 등급 A 또는 B → 자동진입 실행 조건 충족\n"
            "  진입대기 : 등급 C·X 또는 신호 없음\n"
            "\n"
            "  '진입' 상태 시 테두리가 녹색으로 깜빡입니다."
        )
        # 차단사유 + 레짐 카드 (구 원신호 카드 자리) — row0 좌측을 채움 (stretch=2)
        _f_status = QFrame()
        _f_status.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
        _fl_status = QVBoxLayout(_f_status)
        _fl_status.setContentsMargins(6, 3, 6, 3)
        _fl_status.setSpacing(1)
        _lbl_block_reason = mk_label("", C['text2'], 10)
        _lbl_block_reason.setWordWrap(True)
        _lbl_regime = mk_label("", C['text2'], 10)
        _lbl_regime.setWordWrap(True)
        self.e_block_reason = _lbl_block_reason
        self.e_regime = _lbl_regime
        _fl_status.addWidget(_lbl_block_reason)
        _fl_status.addWidget(_lbl_regime)
        info_row0.addWidget(_f_status, 2)

        kv_top = [
            ("원신호",    "signal",      "대기", info_row0, _TIP_RAW_SIGNAL, 1),
            ("실행 신호", "final_signal","대기", info_row0, _TIP_FINAL_SIGNAL, 1),
            ("앙상블 등급","ens_grade",  "대기", info_row1, _TIP_ENS_GRADE, 0),
            ("체크리스트 등급", "chk_grade",  "대기", info_row1, _TIP_CONF, 0),
        ]
        for lbl, attr, init, row_lay, tip, stretch in kv_top:
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6,3,6,3)
            fl.addWidget(mk_label(lbl, C['text2'], 9))
            vl = mk_val_label(init, C['text'], 13)
            setattr(self, f"e_{attr}", vl)
            fl.addWidget(vl)
            if tip:
                f.setToolTip(tip)
                vl.setToolTip(tip)
            # 추세 게이트 깜빡임 대상 프레임 참조 저장
            if attr in ("ens_grade", "chk_grade"):
                setattr(self, f"_{attr}_frame", f)
            row_lay.addWidget(f, stretch)

        # 최종진입 카드 (row1 우측 끝) — 앙상블+체크리스트 종합 진입 판정
        _f_final = QFrame()
        _f_final.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
        _f_final.setToolTip(_TIP_FINAL_ENTRY)
        self._final_entry_frame = _f_final
        _fl_final = QVBoxLayout(_f_final)
        _fl_final.setContentsMargins(6,3,6,3)
        _fl_final.addWidget(mk_label("최종진입", C['text2'], 9))
        _vl_final = mk_val_label("대기", C['text2'], 13)
        _vl_final.setToolTip(_TIP_FINAL_ENTRY)
        self.e_final_entry = _vl_final
        _fl_final.addWidget(_vl_final)
        info_row1.addWidget(_f_final)

        info_vlay.addLayout(info_row0)
        info_vlay.addLayout(info_row1)

        # 하단 3카드: 산출수량 | 진입수량 | 최대허용수량
        _TIP_QTY = (
            "【산출수량 계산 흐름】\n"
            "\n"
            "STEP 1  잔고 기준\n"
            "  익일가예탁현금 (Cybos CpTd6197 next_day_deposit_cash)\n"
            "  fallback 순서: 예탁현금 → 익일가예탁현금 → 전일손익\n"
            "\n"
            "STEP 2  PositionSizer — 켈리 기반 기본 수량\n"
            "  기본리스크  = 잔고 × 1%\n"
            "  신뢰도배수  = 58%→0.6 / 60%→1.0 / 65%→1.2 / 70%→1.5\n"
            "  레짐배수    = RISK_ON=1.0 / NEUTRAL=0.8 / RISK_OFF=0.5\n"
            "  손절거리    = ATR × 1.5\n"
            "  stop_risk   = 손절거리 × pt단위가치 (250,000원/pt)\n"
            "  raw_qty     = (기본리스크 × 신뢰도배수 × 레짐배수\n"
            "                 × 등급배수 × 적응형켈리배수) ÷ stop_risk\n"
            "\n"
            "STEP 3  적응형 켈리 배수 (AdaptiveKelly)\n"
            "  f* = (p × (b+1) − 1) / b\n"
            "  p: 최근 20회 실전 승률\n"
            "  b: 평균수익 / 평균손실 (손익비)\n"
            "  하프 켈리 적용 후 0.10 ~ 1.50 클리핑\n"
            "  데이터 5회 미만 → 보수적 0.6 고정\n"
            "\n"
            "STEP 4  게이트 보정 (순서대로 적용)\n"
            "  ① HealthPolicy  : Degraded 모드 시 사이즈 축소 / 차단\n"
            "  ② ExecutionGovernor: confidence·품질·지연 기반 reduce / block (toxicity 제외)\n"
            "  ③ MetaGate      : 메타 신뢰도 기반 사이즈 배수 조정\n"
            "  ④ ToxicityGate  : 독성 스코어 기반 reduce / block\n"
            "  각 게이트: block → 0 / reduce → 배수 등록 / pass → 유지\n"
            "  [431차] 품질군(Exec·Meta·Toxicity·Hurst)은 곱셈이 아니라 min() 합성 —\n"
            "  가장 강한 축소 하나가 지배하고, 반올림은 마지막에 한 번만 한다.\n"
            "  [433차] pre_retrain(GBM 첫 재학습 전)도 품질군으로 이동 — 모델 최신성은\n"
            "  신호 품질 축이라 Meta·Hurst와 중복 계상됐다(431차 '발동 0건'은 오기).\n"
            "  안전군(Degraded·VolBurst·L2)만 종전대로 곱셈.\n"
            # ⚠ 이 툴팁 본문에는 "잔고 × 1%", "58%→0.6" 등 리터럴 %가 들어 있다.
            #    인접 문자열은 컴파일 시 하나로 합쳐지므로 여기에 % 포매팅을 쓰면
            #    그 리터럴 %까지 변환지정자로 해석돼 ValueError가 난다(431차 기동실패).
            #    → 문자열 결합으로만 값을 끼워 넣을 것.
            "  상한: MAX_CONTRACTS (" + str(MAX_CONTRACTS) + "계약) / 하한: 1계약"
        )
        _TIP_ENTRY = (
            "【진입수량 계산 흐름】\n"
            "\n"
            "산출수량 = 0 (X급 · CB차단 · 게이트 block) 인 경우\n"
            "  → 진입수량 = ——  (진입 없음, 클리핑 미적용)\n"
            "\n"
            "산출수량 > 0 인 경우\n"
            "  진입수량 = max(1, min(산출수량, 최대허용수량))\n"
            "  ① min(산출수량, 최대허용수량) → 상한 클리핑\n"
            "  ② max(1, …) → 최소 1계약 보장\n"
            "\n"
            "실행 일치 보장\n"
            "  _execute_entry 직전 동일한 클리핑 적용\n"
            "  → 대시보드 표시값 = 실제 주문수량 항상 일치\n"
            "\n"
            "최대허용수량 설정\n"
            "  ▲ / ▼ 버튼으로 1 ~ MAX_CONTRACTS 범위에서 즉시 변경\n"
            "  변경값은 ui_prefs.json에 저장되어 재시작 시 복원됨"
        )

        def _mk_info_card(label_text, val_attr, init_text, tooltip=""):
            f = QFrame()
            f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
            if tooltip:
                f.setToolTip(tooltip)
            fl = QVBoxLayout(f)
            fl.setContentsMargins(6,3,6,3)
            fl.addWidget(mk_label(label_text, C['text2'], 9))
            vl = mk_val_label(init_text, C['text'], 13)
            setattr(self, val_attr, vl)
            fl.addWidget(vl)
            return f

        qty_row_lay = QHBoxLayout()
        qty_row_lay.setSpacing(4)
        qty_row_lay.addWidget(_mk_info_card("산출 수량", "e_qty", "대기", _TIP_QTY), 1)
        qty_row_lay.addWidget(_mk_info_card("진입 수량", "e_entry_qty", "대기", _TIP_ENTRY), 1)

        # [311차 후속] 켈리 스킵 권고 배지 — 목표자본(SIZING_TARGET_CAPITAL_KRW) 기준
        # raw_qty<1(켈리가 "1계약도 부적절"이라 판단)이었지만 최소계약으로 진입한 경우 표시.
        # 진입 자체는 스킵하지 않고 데이터만 축적 — 근거: dev_memory/NEXT_TODO.md 311차.
        self.e_kelly_skip_badge = QLabel("")
        self.e_kelly_skip_badge.setAlignment(Qt.AlignCenter)
        self.e_kelly_skip_badge.setFixedWidth(46)
        self.e_kelly_skip_badge.setToolTip(
            "켈리(최근 20건 실적 기준)가 목표자본 대비 이 진입은 1계약도 적절하지 "
            "않다고 판단했지만, 최소 계약수로 진입했습니다."
        )
        self.e_kelly_skip_badge.setVisible(False)
        qty_row_lay.addWidget(self.e_kelly_skip_badge, 0)

        max_f = QFrame()
        max_f.setStyleSheet(f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;")
        max_fl = QVBoxLayout(max_f)
        max_fl.setContentsMargins(6,3,6,3)
        max_fl.addWidget(mk_label("최대허용수량", C['text2'], 9))
        max_inner = QHBoxLayout()
        max_inner.setSpacing(2)
        self.e_max_qty = mk_val_label(f"{self._max_qty}계약", C['orange'], 13)
        max_inner.addWidget(self.e_max_qty, 1)
        _btn_ss = (
            f"QPushButton{{background:{C['bg3']};color:{C['text2']};"
            f"border:1px solid {C['border']};border-radius:3px;"
            f"font-size:{S.f(10)}px;padding:0px 4px;}}"
            f"QPushButton:hover{{background:{C['border']};color:{C['text']};}}"
        )
        btn_up = QPushButton("▲")
        btn_dn = QPushButton("▼")
        btn_up.setStyleSheet(_btn_ss)
        btn_dn.setStyleSheet(_btn_ss)
        btn_up.setFixedWidth(22)
        btn_dn.setFixedWidth(22)
        btn_up.clicked.connect(self._on_max_qty_up)
        btn_dn.clicked.connect(self._on_max_qty_dn)
        btn_col = QVBoxLayout()
        btn_col.setSpacing(1)
        btn_col.addWidget(btn_up)
        btn_col.addWidget(btn_dn)
        max_inner.addLayout(btn_col)
        max_fl.addLayout(max_inner)
        qty_row_lay.addWidget(max_f, 1)

        qty_row_widget = QWidget()
        qty_row_widget.setLayout(qty_row_lay)
        info_vlay.addWidget(qty_row_widget)

        lay.addLayout(info_vlay)
        lay.addWidget(mk_sep())

        # ─── 양분 레이아웃: 왼쪽=Pre-flight 체크리스트, 오른쪽=Layer2 패널 ───
        split_lay = QHBoxLayout()
        split_lay.setSpacing(6)
        split_lay.setContentsMargins(0, 0, 0, 0)

        # ── 왼쪽: 9개 체크리스트 ──
        left_w = QWidget()
        left_lay = QVBoxLayout(left_w)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(3)
        left_lay.addWidget(mk_label("Pre-flight 체크 (9개)", C['orange'], 9, True))
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
                "【앙상블 신호 방향 결정 흐름】\n"
                "\n"
                "STEP 1  멀티호라이즌 입력\n"
                "  GBM + SGD + RF 이종 앙상블 (GBM 0.50 × SGD 0.20 × RF 0.30)\n"
                "  → 1·3·5·10·15·30분 호라이즌별 up/down/flat 확률 반환\n"
                "\n"
                "STEP 2  적응형 가중합 (HorizonDecorrelator + F1 적응형)\n"
                "  상관계수 기반: 60분 롤링으로 호라이즌 간 Pearson ρ 추적 → 이중 가중 완화\n"
                "  F1 적응형 (HorizonF1AdaptiveWeight): 최근 예측 EMA 정확도 추적\n"
                "    F1 낮은 호라이즌 가중치 자동 감소 (f1² 비례, floor=30%)\n"
                "  min_conf 2D 필터: 시간대×호라이즌 기준 미달 호라이즌 제외 (최소 2개 유지)\n"
                "\n"
                "STEP 3  원시 방향 판정\n"
                "  up/down/flat score 가중합 → 최댓값이 방향 확정\n"
                "\n"
                "STEP 4  미시구조 게이팅 (AdaptiveEnsembleGater)\n"
                "  microprice_bias / mlofi_norm / queue_signal 등 6개 신호로 점수 조정\n"
                "  gate_strength ≤ −0.28 & 역신호 2개↑ → 최대 −12% 패널티\n"
                "\n"
                "STEP 4.5  CoherenceGate\n"
                "  방향성 호라이즌(FLAT 제외) 중 동방향 비율 < 60% → 즉시 X등급\n"
                "  예: DN=3 UP=1 FL=2 → 제외 후 3/4=75% → 통과\n"
                "      DN=2 UP=2 FL=2 → 제외 후 2/4=50% → 차단\n"
                "\n"
                "STEP 5  레짐별 최소 신뢰도 필터\n"
                "  REGIME_MIN_CONFIDENCE[regime] (동적 갱신, 현재 NEUTRAL≈0.42)\n"
                "  미충족 시 즉시 X등급\n"
                "\n"
                "STEP 6  등급 판정\n"
                "  confidence ≥ 70% → A  /  ≥ 60% → B  /  ≥ min_conf → C\n"
                "\n"
                "STEP 7  체크리스트 9개 통과 수 → 최종 등급\n"
                "  6개↑ → A (자동, ×1.5)  /  4~5개 → B (자동, ×1.0)\n"
                "  2~3개 → C (수동 확인, ×0.6)  /  1개↓ → X (진입 금지)\n"
                "\n"
                "STEP 8  분할 진입 실행 (StagedEntryManager)\n"
                "  A: 100% 즉시  /  B: 50% → 1분 확인 → 50%  /  C: 50% (2차 없음)\n"
                "\n"
                "※ 이 체크 항목: 방향이 UP(+1) 또는 DOWN(−1)이면 통과, FLAT(0)이면 즉시 X등급"
            ),
            "conf_chk": (
                "목적: 예측 신호의 최소 품질을 확보해 애매한 진입을 걸러냅니다.\n"
                "의의: 낮은 신뢰도 구간에서 발생하는 헛진입을 초기에 차단하는 핵심 방어선입니다.\n"
                "\n"
                "진입 조건:\n"
                "  confidence ≥ actual_min_conf\n"
                "\n"
                "  actual_min_conf = max(\n"
                "    REGIME_MIN_CONFIDENCE[regime],   ← 동적 갱신 (현재 NEUTRAL≈0.42)\n"
                "    get_zone_min_confidence(시간대)  ← 동적 갱신 (mc_history.db 기반)\n"
                "  )\n"
                "\n"
                "  라벨의 숫자(예: '신뢰도 ≥ 46%')는 매분 actual_min_conf로 자동 갱신됩니다.\n"
                "\n"
                "  신뢰도 미달 시 즉시 X등급 반환 (나머지 7개 항목 체크 안 함)"
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
                "진입 조건: LONG이면 직전 봉이 양봉, SHORT이면 직전 봉이 음봉이어야 합니다.\n"
                "\n"
                "[MEAN_REVERSION 모드 완화 — 262차]\n"
                "  MR LONG  : 음봉·도지도 허용 (반전 진입이므로 역봉이 정상)\n"
                "  MR SHORT : 양봉·도지도 허용 (반전 진입이므로 역봉이 정상)\n"
                "  TREND_FOLLOW: 기존 조건 그대로 (동방향 봉만 통과)"
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
        self.check_toggles = {}   # attr → QCheckBox (ON=gate 활성, OFF=무시)
        self._conf_chk_name_label = None
        _TOGGLE_TIP = "체크 ON: 진입 게이트로 작동  /  체크 OFF: 해당 항목 무시 (항상 통과 처리)"
        for i, (name, attr) in enumerate(checks):
            r = QHBoxLayout()
            cb = QCheckBox()
            cb.setChecked(True)
            cb.setFixedWidth(18)
            cb.setToolTip(_TOGGLE_TIP)
            icon = mk_badge("—", C['bg3'], C['text2'], 10)
            icon.setFixedWidth(22)
            nl   = mk_label(name, C['text'], 11)
            vl   = mk_val_label("——", C['text2'], 11)
            tooltip = check_tooltips.get(attr)
            if tooltip:
                nl.setToolTip(tooltip)
            if attr == "conf_chk":
                self._conf_chk_name_label = nl
            r.addWidget(cb)
            r.addWidget(icon)
            r.addWidget(nl, 2)
            r.addWidget(vl)
            self.check_labels[attr] = (icon, vl)
            self.check_toggles[attr] = cb
            left_lay.addLayout(r)

        self._load_gate_toggles()
        for cb in self.check_toggles.values():
            cb.stateChanged.connect(self._save_gate_toggles)

        # ── T3-1: 진입 게이트 필터 섹션 ─────────────────────────────
        left_lay.addWidget(mk_sep())
        left_lay.addWidget(mk_label("진입 게이트 필터", C['blue'], 9, True))
        _gate_filter_items = [
            ("ATR 범위 필터",  "atr_chk",
             f"ATR 범위 필터 (263차, 273차 적응형, 303차 만기예외)\n"
             f"  하한 {ATR_MIN_ENTRY}pt 미만 → 변동성 부족, 휩쏘 위험 → 진입 차단\n"
             f"  상한: 최근 60분 ATR 롤링평균×1.25, 정적하한 {ATR_MAX_ENTRY}pt~절대상한 "
             f"{ATR_ADAPTIVE_MAX_CEILING}pt 사이에서 적응\n"
             f"  만기 D-{ATR_EXPIRY_CEILING_DAYS_BEFORE}~D+{ATR_EXPIRY_CEILING_DAYS_AFTER}: 절대상한 ×"
             f"{ATR_EXPIRY_CEILING_MULT} 일시 확대(→{ATR_ADAPTIVE_MAX_CEILING * ATR_EXPIRY_CEILING_MULT:.1f}pt) "
             f"— 롤오버·프로그램매매 변동성 예외 처리\n"
             f"  값 표시: 현재 ATR pt + OK / ↑고변동 / ↓저변동 상태"),
            ("OPEN_VOL 시가이격", "gap_chk",
             f"OPEN_VOLATILE 시가이격 필터 (263차)\n"
             f"  조건: OPEN_VOLATILE + TREND_FOLLOW 조합 시만 적용\n"
             f"  시가 대비 방향 이탈폭 > ATR × {ATR_OPEN_GAP_MULT} → 낙폭 소진 위험으로 차단\n"
             f"  예: ATR=3.5pt → 이격 상한 {3.5 * ATR_OPEN_GAP_MULT:.1f}pt\n"
             f"  값 표시: 방향이탈 pt (필터 적용 시)\n"
             f"    구간외 = 09:05~10:30 밖 / 모드외 = MR 등 비TREND_FOLLOW\n"
             f"    N/A(시가 미캡처) = GapOffset 캡처 실패 — 이상 신호"),
        ]
        for _gname, _gattr, _gtip in _gate_filter_items:
            _gr = QHBoxLayout()
            _gicon = mk_badge("—", C['bg3'], C['text2'], 10)
            _gicon.setFixedWidth(22)
            _gnl = mk_label(_gname, C['text'], 11)
            _gnl.setToolTip(_gtip)
            _gvl = mk_val_label("——", C['text2'], 11)
            _gr.addWidget(_gicon)
            _gr.addWidget(_gnl, 2)
            _gr.addWidget(_gvl)
            self.check_labels[_gattr] = (_gicon, _gvl)
            left_lay.addLayout(_gr)
            if _gattr == "atr_chk":
                # 303차: ATR 게이트는 두 개의 서로 다른 시간창(14분 현재ATR vs
                # 60분 롤링평균 기반 적응상한)을 함께 보므로, 값만으로는 왜
                # OK/차단인지 알 수 없다 — 계산 근거를 서브라인으로 노출.
                self.atr_gate_detail = mk_label("——", C['text2'], 9, False)
                self.atr_gate_detail.setWordWrap(False)
                self.atr_gate_detail.setContentsMargins(24, 0, 0, 2)
                left_lay.addWidget(self.atr_gate_detail)

        left_lay.addStretch()
        split_lay.addWidget(left_w, 5)

        # ── 오른쪽: Layer 2 Intraday Gate 패널 ──
        right_w = QWidget()
        right_lay = QVBoxLayout(right_w)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(3)

        # 1. Layer 2 상태 카드 + On/Off 버튼
        _l2_gate_tip = (
            "Layer 2 Intraday Gate — 장중 전술 레짐\n\n"
            "  NORMAL        : Layer 1 레짐 그대로 사용\n"
            "  DAY_RISK_OFF  : 신뢰도 +5%p / 사이즈 ×0.5\n"
            "  CRASH         : 신뢰도 +12%p / 사이즈 ×0.3\n\n"
            "━━ CRASH 발동 (3조건 중 하나) ━━\n"
            "  ① |당일 수익률| ≥ 1.8%       (급등/급락 공통)\n"
            "  ② |30분 수익률| ≥ 1.0%\n"
            "       AND ATR ratio ≥ 1.25   (급변동 + 변동성)\n"
            "  ③ z극단 수 ≥ 3              (모델/스케일러 이상)\n\n"
            "━━ DAY_RISK_OFF 발동 (3조건 중 하나) ━━\n"
            "  ① |당일 수익률| ≥ 1.0%       (급등/급락 공통)\n"
            "  ② |당일 수익률| ≥ 0.8%\n"
            "       AND |15분 수익률| ≥ 0.5% (복합 급변동)\n"
            "  ③ Contrarian ACTIVE          (역추세 신호)\n\n"
            "━━ NORMAL 복귀 (2조건 모두) ━━\n"
            "  ① ATR ratio < 1.2            (변동성 안정)\n"
            "  ② z극단 수 < 3              (모델 정상화)\n\n"
            "[Note 2026-06-02] 수익률 조건 abs() 양방향 적용\n"
            "  선물 양방향 특성 반영 — 급등/급락 구분 없이 동일 처리"
        )
        _l2_title = mk_label("Layer 2 Intraday Gate", C['cyan'], 9, True)
        _l2_title.setToolTip(_l2_gate_tip)
        right_lay.addWidget(_l2_title)
        l2_top_lay = QHBoxLayout()
        l2_top_lay.setSpacing(4)
        self.layer2_gate_btn = QPushButton("L2 ON")
        self.layer2_gate_btn.setCheckable(True)
        self.layer2_gate_btn.setChecked(True)
        self.layer2_gate_btn.setFixedWidth(60)
        self.layer2_gate_btn.setToolTip(
            "Layer 2 Intraday Gate 활성/비활성 전환\n"
            "ON: 장중 레짐(NORMAL/DAY_RISK_OFF/CRASH)에 따른 진입 제한 적용\n"
            "OFF: Layer 2 필터 무시 — Layer 1 레짐만 사용"
        )
        self.layer2_gate_btn.toggled.connect(self._on_layer2_gate_toggled)
        self._l2_state_frame = QFrame()
        self._l2_state_frame.setStyleSheet(
            f"background:{C['bg2']};border:2px solid {C['green']};border-radius:4px;"
        )
        _l2_sf_lay = QVBoxLayout(self._l2_state_frame)
        _l2_sf_lay.setContentsMargins(4, 2, 4, 2)
        _l2_sf_lay.setSpacing(0)
        self._l2_state_label = mk_val_label("NORMAL", C['green'], 12)
        self._l2_state_label.setAlignment(Qt.AlignCenter)
        _l2_sf_lay.addWidget(self._l2_state_label)
        self._l2_trans_label = mk_label("", C['text2'], 8)
        self._l2_trans_label.setAlignment(Qt.AlignCenter)
        _l2_sf_lay.addWidget(self._l2_trans_label)
        l2_top_lay.addWidget(self.layer2_gate_btn)
        l2_top_lay.addWidget(self._l2_state_frame, 1)
        right_lay.addLayout(l2_top_lay)
        self._sync_layer2_gate_btn_style()
        self._load_layer2_gate_pref()

        # 2. 발동 지표 표시
        right_lay.addWidget(mk_sep())
        right_lay.addWidget(mk_label("발동 지표", C['text2'], 9, True))
        _l2_inds = [
            ("당일 수익률",  "_l2_day_ret",    "—%",  "±0.8%|±1.0%"),
            ("15분 수익률",  "_l2_ret_15m",    "—%",  "±0.5%"),
            ("30분 수익률",  "_l2_ret_30m",    "—%",  "±1.0%"),
            ("ATR ratio",    "_l2_atr_ratio",  "—",   "≥1.25"),
            ("z극단 수",     "_l2_z_warn",     "—개",  "≥3개"),
            ("Contrarian",   "_l2_contrarian", "—",   "ACTIVE"),
        ]
        for _lbl, _attr, _init, _thresh in _l2_inds:
            _row = QHBoxLayout()
            _row.setSpacing(2)
            _nl = mk_label(_lbl, C['text2'], 9)
            _nl.setFixedWidth(64)
            _vl = mk_val_label(_init, C['text2'], 10)
            _tl = mk_label(_thresh, C['text2'], 8)
            setattr(self, _attr + "_label", _vl)
            _row.addWidget(_nl)
            _row.addWidget(_vl, 1)
            _row.addWidget(_tl)
            right_lay.addLayout(_row)

        # 3. Layer 2 조건 로그
        right_lay.addWidget(mk_sep())
        right_lay.addWidget(mk_label("Layer 2 조건 체크", C['text2'], 9, True))
        self._layer2_log = QTextEdit()
        self._layer2_log.setReadOnly(True)
        self._layer2_log.setFont(QFont("Consolas", S.f(8)))
        self._layer2_log.setStyleSheet(
            f"background:{C['bg3']};color:{C['text2']};"
            f"border:1px solid {C['border']};border-radius:3px;"
        )
        self._layer2_log.setMinimumHeight(100)
        self._layer2_log.setPlainText(
            "진입 허용 체크:   롱/숏 모두 허용\n"
            "신뢰도 강화 체크: 추가 가산 없음\n"
            "사이즈 축소 체크: 사이즈 ×1.0"
        )
        right_lay.addWidget(self._layer2_log, 1)

        split_lay.addWidget(right_w, 6)
        lay.addLayout(split_lay)

        lay.addWidget(mk_sep())

        # 진입 버튼
        lay.addWidget(mk_label("수동 진입관리 패널", C['text2'], 11, True))
        self.entry_alert = mk_label("신호 대기 중...", C['text2'], 12)
        self.entry_alert.setStyleSheet(
            f"background:{C['bg3']};border:1px solid {C['border']};"
            f"border-radius:4px;padding:5px;color:{C['text2']};font-size:{S.f(12)}px;"
        )
        lay.addWidget(self.entry_alert)

        btn_lay = QHBoxLayout()
        self.buy_btn  = QPushButton("▲ 매수 진입 (Long)")
        self.sell_btn = QPushButton("▼ 매도 진입 (Short)")
        self.skip_btn = QPushButton("즉시청산")

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
            f"QPushButton{{background:#2B1A07;color:{C['orange']};"
            f"border:1px solid {C['orange']};border-radius:4px;padding:7px;font-weight:bold;}}"
            f"QPushButton:hover{{background:{C['orange']};color:#000;}}"
        )
        self.buy_btn.clicked.connect(lambda: self.sig_manual_entry_requested.emit("LONG"))
        self.sell_btn.clicked.connect(lambda: self.sig_manual_entry_requested.emit("SHORT"))
        self.skip_btn.clicked.connect(self.sig_instant_exit_requested)
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

    def _setup_time_zone_timer(self):
        self._mode_desc_timer = QTimer(self)
        self._mode_desc_timer.setInterval(30_000)
        self._mode_desc_timer.timeout.connect(self._update_mode_desc)
        self._mode_desc_timer.start()

    def _get_time_zone_guide(self):
        now = now_kst()
        zone = get_time_zone(now)
        start, end = TIME_ZONES.get(zone, ("--:--", "--:--"))
        params = self._time_router.route(now)
        params = self._time_router.apply_expiry_override(params, now)
        params = self._time_router.apply_fomc_override(params, now)
        desc = params.get("desc") or self._TIME_ZONE_DESC.get(zone, self._TIME_ZONE_DESC["OTHER"])
        override_badges = []
        if params.get("_expiry_override") == "EXPIRY_DAY":
            override_badges.append(("만기일 적용중", "#FF8C42"))
        elif params.get("_expiry_override") == "PRE_EXPIRY":
            override_badges.append(("만기 전일 적용중", "#E6C15A"))
        if params.get("_fomc_override"):
            override_badges.append(("FOMC 적용중", "#58A6FF"))
        return zone, start, end, desc, params, override_badges

    def _update_mode_desc(self):
        zone, start, end, desc, params, override_badges = self._get_time_zone_guide()
        legend = "등급 A(6+개 통과) · B(4~5개) · C(2~3개) · X → 진입 차단"
        conf_pct = int(round(float(params.get("min_confidence", 0.0)) * 100.0))
        size_mult = float(params.get("size_mult", 0.0))
        entry_text = "진입허용" if params.get("allow_new_entry", False) else "신규진입금지"
        if zone == "OTHER":
            zone_line = (
                f"현재 시간대: {zone} · conf≥{conf_pct}% · size×{size_mult:.2f} · "
                f"{entry_text} · {desc}"
            )
        else:
            zone_line = (
                f"현재 시간대: {zone} ({start}-{end}) · conf≥{conf_pct}% · "
                f"size×{size_mult:.2f} · {entry_text} · {desc}"
            )
        if override_badges:
            badge_html = " ".join(
                "<span style='background:%s;color:#0B1118;border-radius:4px;padding:1px 6px;font-weight:bold;'>%s</span>"
                % (color, text)
                for text, color in override_badges
            )
            zone_line = "%s &nbsp; %s" % (zone_line, badge_html)
        self.mode_desc.setTextFormat(Qt.RichText)
        self.mode_desc.setText("%s<br>%s" % (legend, zone_line))
        self._sync_time_zone_buttons(zone)
        self._sync_mode_button_styles(self._infer_recommended_mode(params))

    def _infer_recommended_mode(self, params):
        if not params.get("allow_new_entry", False):
            return None
        target = float(params.get("size_mult", 0.0) or 0.0)
        grade_map = {"A": "auto", "B": "hybrid", "C": "manual"}
        grade = min(
            (g for g in ("A", "B", "C")),
            key=lambda g: abs(float(ENTRY_GRADE[g]["size_mult"]) - target)
        )
        return grade_map.get(grade)

    def _sync_mode_button_styles(self, recommended_mode=None):
        accent_map = {
            "auto": "#58A6FF",
            "hybrid": C['green'],
            "manual": C['orange'],
        }
        for mode, btn in self.mode_btns.items():
            is_selected = mode == self.current_mode
            is_recommended = mode == recommended_mode
            accent = accent_map.get(mode, C['text2'])
            base_bg = C['bg2'] if is_selected else C['bg3']
            bg = accent if (is_recommended and not is_selected) else base_bg
            if is_recommended and not is_selected:
                fg = "#0B1118"   # accent 배경 위 어두운 글자
            elif is_selected:
                fg = accent      # 어두운 배경 위 accent 글자
            else:
                fg = C['text2']
            border_col = accent if (is_selected or is_recommended) else C['border']
            border_w = "3px" if is_selected and is_recommended else "2px" if (is_selected or is_recommended) else "1px"
            label = self._mode_button_labels.get(mode, mode)
            btn.setText(label)
            tip = []
            if is_recommended:
                tip.append("시간대 권장 모드")
            if is_selected:
                tip.append("현재 선택")
            btn.setToolTip(" · ".join(tip) if tip else "")
            btn.setStyleSheet(
                f"QPushButton{{background:{bg};color:{fg};border:{border_w} solid {border_col};"
                f"border-radius:4px;padding:5px 8px;font-size:{S.f(12)}px;font-weight:bold;}}"
                f"QPushButton:disabled{{background:{bg};color:{fg};border:{border_w} solid {border_col};opacity:0.72;}}"
            )

    def _sync_time_zone_buttons(self, active_zone):
        for zone, btn in self.time_zone_btns.items():
            start, end = TIME_ZONES.get(zone, ("--:--", "--:--"))
            btn.setText("%s\n%s-%s" % (self._TIME_ZONE_LABEL.get(zone, zone), start, end))
            color = self._TIME_ZONE_COLOR.get(zone, self._TIME_ZONE_COLOR["OTHER"])
            is_active = zone == active_zone
            bg = color if is_active else C['bg3']
            fg = "#0B1118" if is_active else color
            border = "2px" if is_active else "1px"
            weight = "bold" if is_active else "normal"
            opacity = "1.0" if is_active else "0.88"
            btn.setStyleSheet(
                f"QPushButton{{background:{bg};color:{fg};border:{border} solid {color};"
                f"border-radius:5px;padding:4px 6px;font-size:{S.f(9)}px;font-weight:{weight};"
                f"opacity:{opacity};}}"
            )

    def _sync_auto_toggle_style(self):
        on = self._auto_enabled
        col = C['green'] if on else C['text2']
        bg  = C['bg2']   if on else C['bg3']
        bw  = "2px"      if on else "1px"
        self.auto_toggle_btn.setText("Auto ON" if on else "Auto OFF")
        self.auto_toggle_btn.setStyleSheet(
            f"QPushButton{{background:{bg};color:{col};"
            f"border:{bw} solid {col};border-radius:4px;"
            f"padding:5px 8px;font-size:{S.f(12)}px;font-weight:bold;}}"
        )

    def _set_auto_enabled(self, enabled: bool):
        self._auto_enabled = bool(enabled)
        self._sync_auto_toggle_style()
        # 자동 진입관리 버튼 전체 enable/disable
        for btn in self.mode_btns.values():
            btn.setEnabled(self._auto_enabled)
        self._sync_mode_button_styles(self._infer_recommended_mode(self._time_router.apply_fomc_override(self._time_router.apply_expiry_override(self._time_router.route(now_kst()), now_kst()), now_kst())))
        self.reverse_btn.setEnabled(self._auto_enabled)
        self.sig_auto_mode_changed.emit(self._auto_enabled)

    def is_auto_enabled(self) -> bool:
        return self._auto_enabled

    def _sync_reverse_button_style(self):
        if self._reverse_entry_enabled:
            col = C['orange']
            bg  = "#2B1A07"
            border = "2px"
            text = "역방향 진입 ON"
        elif self._contrarian_hint:
            col = "#FFD700" if self._blink_on else "#997700"
            bg  = "#1C1800"
            border = "2px"
            text = "역방향 진입 ★"
        else:
            col = C['text2']
            bg  = C['bg3']
            border = "1px"
            text = "역방향 진입"
        self.reverse_btn.setStyleSheet(
            f"QPushButton{{background:{bg};color:{col};border:{border} solid {col};"
            f"border-radius:4px;padding:5px 8px;font-size:{S.f(12)}px;font-weight:bold;}}"
        )
        self.reverse_btn.setText(text)

    def _on_blink_tick(self):
        self._blink_on = not self._blink_on
        self._sync_reverse_button_style()

    def _on_entry_blink_tick(self):
        self._entry_blink_on = not self._entry_blink_on
        border_col = C['green'] if self._entry_blink_on else C['border']
        self._final_entry_frame.setStyleSheet(
            f"background:{C['bg2']};border:2px solid {border_col};border-radius:4px;"
        )

    def _on_trend_blink_tick(self):
        """추세 지속 게이트 활성 시 등급 카드 테두리 깜빡임.
        UP 상방 원웨이 = 녹색 / DN 하방 원웨이 = 오렌지."""
        self._trend_blink_on = not self._trend_blink_on
        if self._trend_gate_mode == "UP":
            col = C['green'] if self._trend_blink_on else C['border']
        elif self._trend_gate_mode == "DN":
            col = C['orange'] if self._trend_blink_on else C['border']
        else:
            col = C['border']
        style = f"background:{C['bg2']};border:2px solid {col};border-radius:4px;"
        self._ens_grade_frame.setStyleSheet(style)
        self._chk_grade_frame.setStyleSheet(style)

    def set_trend_gate_mode(self, mode: str) -> None:
        """추세 지속 게이트 상태를 등급 카드 테두리 깜빡임으로 표시.

        Args:
            mode: 'UP' (상방 원웨이, 녹색) / 'DN' (하방 원웨이, 오렌지) / '' (해제)
        """
        if mode == self._trend_gate_mode:
            return
        self._trend_gate_mode = mode
        if mode:
            if not self._trend_blink_timer.isActive():
                self._trend_blink_on = True
                self._trend_blink_timer.start()
        else:
            self._trend_blink_timer.stop()
            base = f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;"
            self._ens_grade_frame.setStyleSheet(base)
            self._chk_grade_frame.setStyleSheet(base)

    def set_contrarian_hint(self, active: bool, direction: str = "") -> None:
        """Contrarian ACTIVE 시 역방향 버튼에 황색 깜빡임 힌트 표시."""
        self._contrarian_hint = active
        self._contrarian_direction = direction
        if active:
            if not self._blink_timer.isActive():
                self._blink_on = True
                self._blink_timer.start()
            dir_ko = "LONG(매수)" if direction == "LONG" else "SHORT(매도)" if direction == "SHORT" else direction
            self.reverse_btn.setToolTip(
                f"⚠ Contrarian ACTIVE — 역베팅 방향: {dir_ko}\n"
                "모델이 반복적으로 틀리고 있어 역방향 베팅이 유리할 수 있습니다.\n"
                "수동으로 판단 후 클릭하세요.\n\n"
                "미륵이 자동 판단 신호를 반대로 실행합니다.\n"
                "수동 진입 버튼에는 적용되지 않습니다."
            )
        else:
            self._blink_timer.stop()
            self._blink_on = False
            self.reverse_btn.setToolTip(
                "미륵이 자동 판단 신호를 반대로 실행합니다.\n"
                "수동 진입 버튼에는 적용되지 않습니다."
            )
        self._sync_reverse_button_style()

    def _set_mode(self, mode):
        self.current_mode = mode
        self._save_entry_mode()
        self._update_mode_desc()

    def _save_entry_mode(self):
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            p = {}
            if os.path.exists(_f):
                with open(_f, "r", encoding="utf-8") as fp:
                    p = json.load(fp)
            p["entry_mode"] = self.current_mode
            with open(_f, "w", encoding="utf-8") as fp:
                json.dump(p, fp, ensure_ascii=False)
        except Exception as e:
            import logging
            logging.getLogger("SYSTEM").warning("[EntryPanel] entry_mode 저장 실패: %s", e)

    def _load_entry_mode(self):
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            if not os.path.exists(_f):
                return
            with open(_f, "r", encoding="utf-8") as fp:
                mode = json.load(fp).get("entry_mode", "hybrid")
            if mode not in self._mode_button_labels:
                return
            self.current_mode = mode
            self._sync_mode_button_styles()
        except Exception as e:
            import logging
            logging.getLogger("SYSTEM").warning("[EntryPanel] entry_mode 복원 실패: %s", e)

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
                    reverse_enabled=False, min_conf: float = 0.58,
                    ensemble_grade: str = None, checklist_grade: str = None,
                    final_entry: bool = False, check_values: dict = None,
                    entry_block_reason: str = "", qty_entry_final: int = None,
                    hurst: float = None, atr: float = None, regime: str = None,
                    kelly_advised_skip: bool = False):
        self._last_entry_block_reason = entry_block_reason
        final_signal = final_signal or signal

        # 차단사유 + 레짐
        if entry_block_reason:
            _reason = entry_block_reason.replace("[차단] ", "").replace("[blocked] ", "")[:60]
            self.e_block_reason.setText(f"차단: {_reason}")
            self.e_block_reason.setStyleSheet(f"color:{C['orange']};font-size:{S.f(10)}px;")
        else:
            self.e_block_reason.setText("")
        _hurst_txt = f"Hurst {float(hurst):.2f}" if hurst is not None else "Hurst ——"
        _atr_txt = f"ATR {float(atr):.1f}pt" if atr is not None else "ATR ——"
        self.e_regime.setText(f"레짐: {regime or '——'} · {_hurst_txt} · {_atr_txt}")
        self.e_regime.setStyleSheet(f"color:{C['text2']};font-size:{S.f(10)}px;")
        col = C['green'] if signal == "매수" else C['red'] if signal == "매도" else C['text2']
        final_col = C['green'] if final_signal == "매수" else C['red'] if final_signal == "매도" else C['text2']
        self.e_signal.setText(signal)
        self.e_signal.setStyleSheet(f"color:{col};font-size:{S.f(14)}px;font-weight:bold;")
        self.e_final_signal.setText(final_signal)
        self.e_final_signal.setStyleSheet(f"color:{final_col};font-size:{S.f(14)}px;font-weight:bold;")

        # 앙상블 등급 카드 (신뢰도 퍼센트 대신 A/B/C/X 등급 표시)
        grade_colors = {"A": C['cyan'], "B": C['blue'], "C": C['orange'], "X": C['red']}
        _ens_g = ensemble_grade or grade
        self.e_ens_grade.setText(f"{_ens_g}급")
        self.e_ens_grade.setStyleSheet(f"color:{grade_colors.get(_ens_g, C['text'])};"
                                       f"font-size:{S.f(14)}px;font-weight:bold;")

        # 진입 등급 카드 (체크리스트 grade 표시)
        _chk_g = checklist_grade or grade
        self.e_chk_grade.setText(f"{_chk_g}급")
        self.e_chk_grade.setStyleSheet(f"color:{grade_colors.get(_chk_g, C['text'])};"
                                       f"font-size:{S.f(14)}px;font-weight:bold;")

        # 최종진입 카드
        if final_entry:
            self.e_final_entry.setText("진입")
            self.e_final_entry.setStyleSheet(f"color:{C['green']};font-size:{S.f(14)}px;font-weight:bold;")
            if not self._entry_blink_timer.isActive():
                self._entry_blink_on = True
                self._entry_blink_timer.start()
        else:
            self.e_final_entry.setText("진입대기")
            self.e_final_entry.setStyleSheet(f"color:{C['text2']};font-size:{S.f(14)}px;font-weight:bold;")
            if self._entry_blink_timer.isActive():
                self._entry_blink_timer.stop()
            self._final_entry_frame.setStyleSheet(
                f"background:{C['bg2']};border:1px solid {C['border']};border-radius:4px;"
            )

        # 산출 수량
        if qty > 0:
            self.e_qty.setText(f"{qty}계약")
            self.e_qty.setStyleSheet(f"color:{C['cyan']};font-size:{S.f(14)}px;font-weight:bold;")
        else:
            self.e_qty.setText("——")
            self.e_qty.setStyleSheet(f"color:{C['text2']};font-size:{S.f(14)}px;font-weight:bold;")

        # [311차 후속] 켈리 스킵 권고 배지
        if kelly_advised_skip:
            self.e_kelly_skip_badge.setText("켈리↓")
            self.e_kelly_skip_badge.setStyleSheet(
                f"background:{C['orange']};color:#fff;border-radius:3px;"
                f"font-size:{S.f(9)}px;font-weight:bold;padding:2px;"
            )
            self.e_kelly_skip_badge.setVisible(True)
        else:
            self.e_kelly_skip_badge.setVisible(False)

        # 진입 수량 — qty_entry_final(최대허용수량+증거금 반영 최종수량)이 있으면 그대로
        # 표시한다. 최대허용수량을 만족해도 증거금이 부족하면 브로커가 주문을 거부하므로
        # (2026-07-03 10:28:59 LONG 3계약 ret=-1 사례) 0으로 캡핑된 경우도 그대로 노출한다
        # — 예전처럼 max(1, ...)로 강제 1계약을 보여주면 실제로는 못 나갈 주문을 나갈
        # 것처럼 표시하게 된다.
        if qty_entry_final is not None:
            if qty_entry_final > 0:
                self.e_entry_qty.setText(f"{qty_entry_final}계약")
                self.e_entry_qty.setStyleSheet(f"color:{C['green']};font-size:{S.f(14)}px;font-weight:bold;")
            elif qty > 0:
                self.e_entry_qty.setText("0(증거금부족)")
                self.e_entry_qty.setStyleSheet(f"color:{C['red']};font-size:{S.f(14)}px;font-weight:bold;")
            else:
                self.e_entry_qty.setText("——")
                self.e_entry_qty.setStyleSheet(f"color:{C['text2']};font-size:{S.f(14)}px;font-weight:bold;")
        elif qty > 0:
            entry_qty = max(1, min(qty, self._max_qty))
            self.e_entry_qty.setText(f"{entry_qty}계약")
            self.e_entry_qty.setStyleSheet(f"color:{C['green']};font-size:{S.f(14)}px;font-weight:bold;")
        else:
            self.e_entry_qty.setText("——")
            self.e_entry_qty.setStyleSheet(f"color:{C['text2']};font-size:{S.f(14)}px;font-weight:bold;")

        # 신뢰도 체크 레이블 — 실제 min_conf 기준을 실시간 반영
        if self._conf_chk_name_label is not None:
            self._conf_chk_name_label.setText(f"신뢰도 ≥ {min_conf:.0%}")

        # 체크리스트 아이콘
        # 체크박스 OFF → SKIP(파란 —), checks=None → 미평가(회색 —),
        # True → V(green), False → X(red)
        _cv = check_values or {}
        for attr, (icon, vl) in self.check_labels.items():
            cb = self.check_toggles.get(attr)
            if cb is not None and not cb.isChecked():
                icon.setText("—")
                icon.setStyleSheet(
                    f"background:#1A3A5C;color:#58A6FF;"
                    f"border-radius:3px;font-size:{S.f(10)}px;font-weight:bold;padding:1px 4px;"
                )
                vl.setText(_cv.get(attr, "——"))
                vl.setStyleSheet(f"color:{C['text2']};font-size:{S.f(10)}px;")
                continue
            val = checks.get(attr, None)
            if val is None:
                icon.setText("—")
                icon.setStyleSheet(
                    f"background:{C['bg3']};color:{C['text2']};"
                    f"border-radius:3px;font-size:{S.f(10)}px;font-weight:bold;padding:1px 4px;"
                )
                vl.setText(_cv.get(attr, "——"))
                vl.setStyleSheet(f"color:{C['text2']};font-size:{S.f(10)}px;")
            elif val:
                icon.setText("V")
                icon.setStyleSheet(
                    f"background:{C['green']};color:#fff;"
                    f"border-radius:3px;font-size:{S.f(10)}px;font-weight:bold;padding:1px 4px;"
                )
                vl.setText(_cv.get(attr, "——"))
                vl.setStyleSheet(f"color:{C['green']};font-size:{S.f(10)}px;")
            else:
                icon.setText("X")
                icon.setStyleSheet(
                    f"background:{C['red']};color:#fff;"
                    f"border-radius:3px;font-size:{S.f(10)}px;font-weight:bold;padding:1px 4px;"
                )
                vl.setText(_cv.get(attr, "——"))
                vl.setStyleSheet(f"color:{C['red']};font-size:{S.f(10)}px;")

        if getattr(self, "atr_gate_detail", None) is not None:
            self.atr_gate_detail.setText(_cv.get("atr_chk_detail", "——"))

        if signal == "매수":
            self.entry_alert.setStyleSheet(
                f"background:#0D2818;border:1px solid {C['green']};"
                f"border-radius:4px;padding:5px;color:{C['green']};font-size:{S.f(12)}px;"
            )
            reverse_tag = " | 역방향진입=ON" if reverse_enabled else ""
            self.entry_alert.setText(
                f"▲ 원신호: {signal} / 실행신호: {final_signal} | {_chk_g}급 — {conf*100:.1f}% 신뢰도{reverse_tag}"
            )
        elif signal == "매도":
            self.entry_alert.setStyleSheet(
                f"background:#2D0D0D;border:1px solid {C['red']};"
                f"border-radius:4px;padding:5px;color:{C['red']};font-size:{S.f(12)}px;"
            )
            reverse_tag = " | 역방향진입=ON" if reverse_enabled else ""
            self.entry_alert.setText(
                f"▼ 원신호: {signal} / 실행신호: {final_signal} | {_chk_g}급 — {conf*100:.1f}% 신뢰도{reverse_tag}"
            )
        else:
            if entry_block_reason:
                _reason_disp = (
                    entry_block_reason
                    .replace("[차단] ", "")
                    .replace("[blocked] ", "")
                )[:90]
                self.entry_alert.setStyleSheet(
                    f"background:#1C1A00;border:1px solid #C8A800;"
                    f"border-radius:4px;padding:5px;color:#C8A800;font-size:{S.f(11)}px;"
                )
                self.entry_alert.setText(f"⊘ {_reason_disp}")
            else:
                self.entry_alert.setStyleSheet(
                    f"background:{C['bg3']};border:1px solid {C['border']};"
                    f"border-radius:4px;padding:5px;color:{C['text2']};font-size:{S.f(12)}px;"
                )
                self.entry_alert.setText("— 관망 | 신호 대기 중")

    # ── 최대허용수량 관련 메서드 ─────────────────────────────────────
    def _load_max_qty(self) -> int:
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            if not os.path.exists(_f):
                return MAX_CONTRACTS
            with open(_f, "r", encoding="utf-8") as fp:
                return max(1, int(json.load(fp).get("max_entry_qty", MAX_CONTRACTS)))
        except Exception:
            return MAX_CONTRACTS

    def _save_max_qty(self):
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            p = {}
            if os.path.exists(_f):
                with open(_f, "r", encoding="utf-8") as fp:
                    p = json.load(fp)
            p["max_entry_qty"] = self._max_qty
            with open(_f, "w", encoding="utf-8") as fp:
                json.dump(p, fp, ensure_ascii=False)
        except Exception:
            pass

    def get_max_qty(self) -> int:
        return self._max_qty

    def _load_gate_toggles(self):
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            if not os.path.exists(_f):
                return
            with open(_f, "r", encoding="utf-8") as fp:
                saved = json.load(fp).get("gate_toggles", {})
            for attr, cb in self.check_toggles.items():
                if attr in saved:
                    cb.blockSignals(True)
                    cb.setChecked(bool(saved[attr]))
                    cb.blockSignals(False)
        except Exception:
            pass

    def _save_gate_toggles(self):
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            p = {}
            if os.path.exists(_f):
                with open(_f, "r", encoding="utf-8") as fp:
                    p = json.load(fp)
            p["gate_toggles"] = {attr: cb.isChecked() for attr, cb in self.check_toggles.items()}
            with open(_f, "w", encoding="utf-8") as fp:
                json.dump(p, fp, ensure_ascii=False)
        except Exception:
            pass

    _ATTR_TO_INTERNAL = {
        "signal_chk": "1_signal",   "conf_chk": "2_confidence",
        "vwap_chk":   "3_vwap",     "cvd_chk":  "4_cvd",
        "ofi_chk":    "5_ofi",      "fi_chk":   "6_foreign",
        "candle_chk": "7_prev_bar", "time_chk": "8_time",
        "risk_chk":   "9_risk",
    }

    def get_disabled_gates(self) -> set:
        """체크박스 OFF 항목의 내부 키 집합 반환 (checklist.evaluate 의 disabled_gates 인수용)"""
        disabled = set()
        for attr, cb in self.check_toggles.items():
            if not cb.isChecked():
                internal = self._ATTR_TO_INTERNAL.get(attr)
                if internal:
                    disabled.add(internal)
        return disabled

    def _refresh_max_qty_display(self):
        self.e_max_qty.setText(f"{self._max_qty}계약")

    def _on_max_qty_up(self):
        if self._max_qty < MAX_CONTRACTS:
            self._max_qty += 1
            self._refresh_max_qty_display()
            self._save_max_qty()
            self.sig_max_qty_changed.emit(self._max_qty)

    def _on_max_qty_dn(self):
        if self._max_qty > 1:
            self._max_qty -= 1
            self._refresh_max_qty_display()
            self._save_max_qty()
            self.sig_max_qty_changed.emit(self._max_qty)

    # ── Layer 2 Intraday Gate 메서드 ──────────────────────────────────────

    def _sync_layer2_gate_btn_style(self):
        on = self._layer2_gate_enabled
        col = C['cyan'] if on else C['text2']
        bg  = C['bg2']  if on else C['bg3']
        bw  = "2px"     if on else "1px"
        self.layer2_gate_btn.setText("L2 ON" if on else "L2 OFF")
        self.layer2_gate_btn.setStyleSheet(
            f"QPushButton{{background:{bg};color:{col};"
            f"border:{bw} solid {col};border-radius:4px;"
            f"padding:4px 6px;font-size:{S.f(10)}px;font-weight:bold;}}"
        )

    def _save_layer2_gate_pref(self):
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            p = {}
            if os.path.exists(_f):
                with open(_f, "r", encoding="utf-8") as fp:
                    p = json.load(fp)
            p["layer2_gate_enabled"] = self._layer2_gate_enabled
            with open(_f, "w", encoding="utf-8") as fp:
                json.dump(p, fp, ensure_ascii=False)
        except Exception:
            pass

    def _load_layer2_gate_pref(self):
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            if not os.path.exists(_f):
                return
            with open(_f, "r", encoding="utf-8") as fp:
                saved = json.load(fp).get("layer2_gate_enabled", True)
            if not bool(saved):
                self.layer2_gate_btn.blockSignals(True)
                try:
                    self.layer2_gate_btn.setChecked(False)
                finally:
                    self.layer2_gate_btn.blockSignals(False)
                self._layer2_gate_enabled = False
                self._sync_layer2_gate_btn_style()
        except Exception:
            pass

    def _on_layer2_gate_toggled(self, enabled: bool):
        self._layer2_gate_enabled = bool(enabled)
        self._sync_layer2_gate_btn_style()
        self._save_layer2_gate_pref()
        self.sig_layer2_gate_toggled.emit(self._layer2_gate_enabled)

    def is_layer2_gate_enabled(self) -> bool:
        return self._layer2_gate_enabled

    def update_layer2(self, status_dict: dict, min_conf_base: float = 0.58):
        """Layer 2 Intraday Gate 패널 갱신."""
        regime    = status_dict.get("regime",      "NORMAL")
        prev      = status_dict.get("prev_regime", "NORMAL")
        factors   = status_dict.get("factors",     {})
        policy    = status_dict.get("policy",      {})

        # 상태 카드
        _l2_col = {"NORMAL": C['green'], "DAY_RISK_OFF": C['orange'], "CRASH": C['red']}
        col = _l2_col.get(regime, C['text2'])
        self._l2_state_label.setText(regime)
        self._l2_state_label.setStyleSheet(
            f"color:{col};font-size:{S.f(12)}px;font-weight:bold;"
        )
        self._l2_state_frame.setStyleSheet(
            f"background:{C['bg2']};border:2px solid {col};border-radius:4px;"
        )
        if regime != prev:
            self._l2_trans_label.setText(f"{prev} → {regime}")
            self._l2_trans_label.setStyleSheet(f"color:{col};font-size:{S.f(8)}px;")
        else:
            self._l2_trans_label.setText("")

        # 지표 갱신
        day_ret    = factors.get("day_ret",      0.0)
        ret_15m    = factors.get("ret_15m",      0.0)
        ret_30m    = factors.get("ret_30m",      0.0)
        atr_ratio  = factors.get("atr_ratio",    0.0)
        z_warn     = int(factors.get("z_warn_count", 0))
        contrarian = bool(factors.get("contrarian",  False))
        bounce     = factors.get("bounce",      0.0)
        ofi_15m    = factors.get("ofi_15m_avg", 0.0)

        def _ind(attr, text, triggered):
            lbl = getattr(self, attr + "_label", None)
            if lbl is None:
                return
            lbl.setText(text)
            lbl.setStyleSheet(
                f"color:{C['red'] if triggered else C['text']};"
                f"font-size:{S.f(10)}px;font-weight:bold;"
            )

        _day_col = C['red'] if abs(day_ret) >= 0.010 else (C['orange'] if abs(day_ret) >= 0.008 else C['text'])
        day_lbl = getattr(self, "_l2_day_ret_label", None)
        if day_lbl is not None:
            day_lbl.setText(f"{day_ret*100:+.2f}%")
            day_lbl.setStyleSheet(
                f"color:{_day_col};font-size:{S.f(10)}px;font-weight:bold;"
            )
        _ind("_l2_ret_15m",   f"{ret_15m*100:+.2f}%", abs(ret_15m) >= 0.005)
        _ind("_l2_ret_30m",   f"{ret_30m*100:+.2f}%", abs(ret_30m) >= 0.010)
        _ind("_l2_atr_ratio", f"{atr_ratio:.3f}",     atr_ratio >= 1.25)
        _ind("_l2_z_warn",    f"{z_warn}개",           z_warn >= 3)
        con_lbl = getattr(self, "_l2_contrarian_label", None)
        if con_lbl is not None:
            con_lbl.setText("ACTIVE" if contrarian else "비활성")
            con_lbl.setStyleSheet(
                f"color:{C['orange'] if contrarian else C['text2']};"
                f"font-size:{S.f(10)}px;font-weight:bold;"
            )

        # 조건 로그
        if regime == "NORMAL":
            entry_txt = "롱/숏 모두 허용"
            conf_txt  = "추가 가산 없음"
            size_txt  = "사이즈 ×1.0"
        elif regime == "DAY_RISK_OFF":
            entry_txt = "신규 롱 금지,  숏만 허용"
            conf_txt  = "최소 신뢰도 +5%p"
            size_txt  = "사이즈 ×0.5"
        else:  # CRASH
            entry_txt = "원칙적으로 신규 진입 전부 금지"
            conf_txt  = "최소 신뢰도 +12%p"
            size_txt  = "사이즈 ×0.3"

        lines = [
            f"진입 허용 체크:   {entry_txt}",
            f"신뢰도 강화 체크: {conf_txt}",
            f"사이즈 축소 체크: {size_txt}",
        ]

        if regime != "NORMAL":
            # 방향 중립 2조건만 사용 (bounce·OFI 제거 — 양방향 선물 설계)
            z_ok = z_warn    < 3
            a_ok = atr_ratio < 1.2
            lines += [
                "",
                "복귀 조건 체크 (→ NORMAL)",
                f"  ATR ratio {atr_ratio:.3f} < 1.2:  {'✔' if a_ok else '✘'}",
                f"  z극단 {z_warn}개 < 3:  {'✔' if z_ok else '✘'}",
            ]

        self._layer2_log.setPlainText("\n".join(lines))


# ────────────────────────────────────────────────────────────
# 패널 6: 🧠 자가학습 모니터
# ────────────────────────────────────────────────────────────
class LearningPanel(QWidget):
    """SGD 온라인 / GBM 배치 / 예측 버퍼 자가학습 현황 통합 뷰"""

    HORIZONS  = ["1m", "3m", "5m", "10m", "15m", "30m"]
    H_LABELS  = ["1분", "3분", "5분", "10분", "15분", "30분"]
    RAW_NEEDED = 15_000

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

    @staticmethod
    def _spark(values, width: int = 18) -> str:
        """0~1 float 리스트 → 유니코드 스파크라인 (고정 width)"""
        if not values:
            return "─" * width
        blk = "▁▂▃▄▅▆▇█"
        mn, mx = min(values), max(values)
        span = mx - mn if mx != mn else 1.0
        chars = [blk[min(7, int((v - mn) / span * 7.99))] for v in values]
        while len(chars) > width:
            step = len(chars) / width
            chars = [chars[int(i * step)] for i in range(width)]
        while len(chars) < width:
            chars.append("─")
        return "".join(chars)

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
            ("SGD 정확도 S·L",   "——",      C['green'],  "sgd_acc"),
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
            # SGD 카드: short / long 버킷 정확도 detail 행
            if key == "sgd_acc":
                self._lbl_sgd_detail = mk_label("S: ——  L: ——", C['text2'], 8, align=Qt.AlignCenter)
                fl.addWidget(self._lbl_sgd_detail)
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

        # CB③ 정확도 + 고신뢰 연속오답 streak 표시
        self._lbl_cb_acc = mk_label(
            "CB③ 30m 정확도: ——  (샘플 0건)  |  과신 오답 연속: 0회",
            C['text2'], 8, align=Qt.AlignCenter,
        )
        root.addWidget(self._lbl_cb_acc)

        # DriftAdjuster — SGD alpha 조정 상태(DRIFT_UP/RECOVERY_DOWN/HOLD/SKIP_LOW_SAMPLE)
        self._lbl_drift = mk_label(
            "SGD alpha: ——  |  이력: ──────────────────",
            C['text2'], 8, align=Qt.AlignCenter,
        )
        self._lbl_drift.setToolTip(
            "5일 롤링 정확도 추이로 SGD 학습률(alpha)을 자동 조정합니다.\n"
            "DRIFT_UP: 정확도 하락 감지 → alpha 상향(빠른 적응) | "
            "RECOVERY_DOWN: 정확도 회복 → alpha 하향(과적합 방지)\n"
            "SKIP_LOW_SAMPLE: 당일 표본 부족(<15건) — 극단값 반영 스킵, 기존 alpha 유지"
        )
        root.addWidget(self._lbl_drift)

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

        # A/B · Calibration · Meta Gate · Rollout 리포트 탭
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
        _conf_inv = calibration_metrics.get("conf_inversion") or {}
        _cal_val_w = self._report_widgets["calibration"]["value"]
        _cal_det_w = self._report_widgets["calibration"]["detail"]
        if _conf_inv.get("inverted"):
            _hi = float(_conf_inv.get("high_acc", 0.0) or 0.0)
            _lo = float(_conf_inv.get("low_acc",  0.0) or 0.0)
            _cal_val_w.setText(f"ECE {calib_ece:.3f}  ⚠역전")
            _cal_val_w.setStyleSheet(
                f"font-size:{S.f(11)}px;color:{C['red']};"
                f"padding:{S.p(3)}px {S.p(6)}px;"
                f"background:#2D0D0D;border:1px solid {C['red']};"
            )
            _cal_det_w.setText(
                f"고신뢰 acc {_hi:.1%} < 저신뢰 {_lo:.1%} | HCGuard 차단중"
            )
        else:
            _cal_val_w.setText(f"ECE {calib_ece:.3f}")
            _cal_val_w.setStyleSheet(
                f"font-size:{S.f(11)}px;color:{C['text2']};"
                f"padding:{S.p(3)}px {S.p(6)}px;"
                f"background:{C['bg3']};border:1px solid {C['border']};"
            )
            _cal_det_w.setText(
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

        # 요약 카드
        self._sum_lbls["verified"].setText(str(data.get("verified_today", 0)))

        sgd_acc = float(data.get("sgd_accuracy_50m", 0.5))
        col_sgd = self._acc_col(sgd_acc)
        self._sum_lbls["sgd_acc"].setText(f"{sgd_acc:.1%}")
        self._sum_lbls["sgd_acc"].setStyleSheet(
            f"color:{col_sgd};font-size:{S.f(18)}px;font-weight:bold;"
        )
        # short / long 버킷 정확도 detail
        s_acc = float(data.get("sgd_acc_short", 0.5))
        l_acc = float(data.get("sgd_acc_long",  0.5))
        self._lbl_sgd_detail.setText(f"S: {s_acc:.1%}  L: {l_acc:.1%}")
        self._lbl_sgd_detail.setStyleSheet(
            f"color:{self._acc_col(s_acc)};font-size:{S.f(8)}px;"
        )

        # CB③ 정확도
        cb_acc  = float(data.get("cb_accuracy_30m", 0.0))
        cb_n    = int(data.get("cb_samples", 0))
        cb_stk  = int(data.get("cb_streak", 0))
        # HALT 판정 최소 표본(CB_ACC30M_MIN_SAMPLES=30) 미만이면 통계적으로 무의미하므로
        # 강조색 대신 회색으로 표시 — 판정에 실제 영향 없는 5~29건 구간의 과장 표시 방지
        cb_col  = self._acc_col(cb_acc) if cb_n >= CB_ACC30M_MIN_SAMPLES else C['text2']
        stk_col = C['red'] if cb_stk >= 3 else C['text2']
        stk_txt = f"<span style='color:{stk_col};font-weight:bold;'>{cb_stk}회</span>"
        self._lbl_cb_acc.setText(
            f"CB③ 30m 정확도: <span style='color:{cb_col};font-weight:bold;'>"
            f"{cb_acc:.1%}</span>  (샘플 {cb_n}건)  |  과신 오답 연속: {stk_txt}"
        )
        self._lbl_cb_acc.setTextFormat(__import__('PyQt5.QtCore', fromlist=['Qt']).Qt.RichText)

        # DriftAdjuster — SGD alpha 조정 상태
        drift_alpha  = float(data.get("drift_alpha", 0.001))
        drift_action = str(data.get("drift_action", "HOLD") or "HOLD")
        drift_hist   = data.get("drift_history", []) or []
        _DRIFT_LABELS = {
            "DRIFT_UP":       ("정확도 하락→alpha↑", C['orange']),
            "RECOVERY_DOWN":  ("정확도 회복→alpha↓", C['green']),
            "HOLD":           ("유지", C['text2']),
            "SKIP_LOW_SAMPLE": ("표본부족→스킵", C['yellow']),
        }
        action_txt, action_col = _DRIFT_LABELS.get(drift_action, (drift_action, C['text2']))
        drift_spark = self._spark([float(v) for v in drift_hist[-24:]], 18)
        self._lbl_drift.setText(
            f"SGD alpha: <span style='color:{C['purple']};font-weight:bold;'>"
            f"{drift_alpha:.5f}</span>  "
            f"<span style='color:{action_col};font-weight:bold;'>{action_txt}</span>"
            f"  |  이력: {drift_spark}"
        )
        self._lbl_drift.setTextFormat(__import__('PyQt5.QtCore', fromlist=['Qt']).Qt.RichText)

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
        h_acc_n = data.get("horizon_acc_samples", {})
        # [P5] 블렌딩 비활성 호라이즌 — 학습은 계속되지만 앙상블 확률에 반영 안 됨.
        # 배지에 "OFF"를 병기해 "학습됨=기여 중"으로 오인하지 않도록 함.
        for hz, (acc_lbl, cnt_lbl, badge, bar) in self._hz_cards.items():
            is_fit = fitted.get(hz, False)
            acc    = float(h_accs.get(hz, 0.5))
            n_acc  = int(h_acc_n.get(hz, 0))
            cnt    = int(h_cnts.get(hz, 0))
            # is_fit(현재 모델 학습여부)와 별개로 acc_buf 표본이 5건 미만이면
            # horizon_accuracy()가 방어적으로 0.0을 반환한다 — "정확도 0%"가 아니라
            # "판정 불가(표본부족)" 상태이므로 구분 표시 (버그2)
            acc_ready = is_fit and n_acc >= 5
            col = self._acc_col(acc) if acc_ready else C['text2']
            acc_lbl.setText(f"{acc:.1%}" if acc_ready else (f"—.—%(n{n_acc})" if is_fit else "—.—%"))
            acc_lbl.setStyleSheet(
                f"color:{col};font-size:{S.f(16)}px;font-weight:bold;"
            )
            bar.setValue(int(acc * 100) if acc_ready else 0)
            bar.setStyleSheet(
                f"QProgressBar{{background:{C['bg']};border:none;border-radius:2px;}}"
                f"QProgressBar::chunk{{background:{col};}}"
            )
            # sgd_sample_counts(_horizon_counts)는 BiasReset 등 부분 리셋 시에도
            # 초기화되지 않는 누적(lifetime) 카운터 — is_fit과 별도 축이므로
            # "누적"임을 명시해 "미학습인데 건수 있음" 오인을 방지 (버그1)
            cnt_lbl.setText(f"누적 {cnt}건")
            cnt_lbl.setStyleSheet(f"color:{C['text2']};font-size:{S.f(8)}px;")
            if is_fit:
                _badge_txt, _badge_col, _badge_bold = "학습됨", col, True
            elif cnt > 0:
                # 모델이 리셋(BiasReset/SGD 붕괴복구)되어 현재는 미학습이지만
                # 과거 누적 학습 이력은 남아있는 상태 — 순수 "미학습"과 구분
                _badge_txt, _badge_col, _badge_bold = "리셋됨", C['orange'], True
            else:
                _badge_txt, _badge_col, _badge_bold = "미학습", C['text2'], False

            if hz in SGD_BLEND_DISABLED_HORIZONS:
                # [P5] 학습 상태는 참고용으로 계속 표기하되, 회색조로 통일해
                # "블렌딩엔 반영 안 됨"을 시각적으로 명확히 함 (정직한 손절)
                badge.setText(f"OFF·{_badge_txt}")
                badge.setStyleSheet(
                    f"background:{C['bg3']};color:{C['text2']};border-radius:3px;"
                    f"font-size:{S.f(7)}px;padding:1px 5px;"
                )
            else:
                badge.setText(_badge_txt)
                _weight = "font-weight:bold;" if _badge_bold else ""
                badge.setStyleSheet(
                    f"background:{_badge_col}33;color:{_badge_col};border-radius:3px;"
                    f"font-size:{S.f(7)}px;{_weight}padding:1px 5px;"
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
        _conf_inv = calibration_metrics.get("conf_inversion") or {}
        _cal_val_w = self._report_widgets["calibration"]["value"]
        _cal_det_w = self._report_widgets["calibration"]["detail"]
        if _conf_inv.get("inverted"):
            _hi = float(_conf_inv.get("high_acc", 0.0) or 0.0)
            _lo = float(_conf_inv.get("low_acc",  0.0) or 0.0)
            _cal_val_w.setText(f"ECE {calib_ece:.3f}  ⚠역전")
            _cal_val_w.setStyleSheet(
                f"font-size:{S.f(11)}px;color:{C['red']};"
                f"padding:{S.p(3)}px {S.p(6)}px;"
                f"background:#2D0D0D;border:1px solid {C['red']};"
            )
            _cal_det_w.setText(
                f"고신뢰 acc {_hi:.1%} < 저신뢰 {_lo:.1%} | HCGuard 차단중"
            )
        else:
            _cal_val_w.setText(f"ECE {calib_ece:.3f}")
            _cal_val_w.setStyleSheet(
                f"font-size:{S.f(11)}px;color:{C['text2']};"
                f"padding:{S.p(3)}px {S.p(6)}px;"
                f"background:{C['bg3']};border:1px solid {C['border']};"
            )
            _cal_det_w.setText(
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
# 패널 8.5: 운영 헬스
# ────────────────────────────────────────────────────────────
class HealthPanel(QWidget):
    """운영 헬스 모니터링 패널: 처리시간(CB⑤), 피처 품질, 캐시 나이, 예외 밀도 추적."""

    def __init__(self):
        super().__init__()
        self._health_vals = {}
        self._health_trend_values = []
        self._health_latency_trend_values = []
        self._health_quality_trend_values = []
        self._thresholds = {
            "latency_warn_ms": 1000,   # CB_PIPE_WARN_MS 와 동일
            "latency_crit_ms": 5000,   # CB_PIPE_PAUSE_MS 와 동일
            "quality_warn": 0.85,
            "quality_crit": 0.70,
            "cache_age_warn_sec": 300,
            "cache_age_crit_sec": 600,
            "exception_density_warn_10m": 5,
            "exception_density_crit_10m": 10,
        }
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(S.p(12), S.p(12), S.p(12), S.p(12))
        lay.setSpacing(S.p(10))

        # ── 상단: 4개 메트릭 박스 ─────────────────────────────────
        _PIPE_TIP = (
            "파이프라인 처리시간 (CB⑤ 대체 지표)\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "≤ 1000ms  정상 (green)\n"
            "≤ 4999ms  경고 로그 [CB⑤] (orange)\n"
            "≥ 5000ms  5분 진입 정지 + Slack (red)\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Cybos Plus는 COM 콜백 기반으로\n"
            "네트워크 RTT 측정 불가 — 파이프라인\n"
            "실행시간을 API 지연 대체 지표로 사용"
        )
        mrow = QHBoxLayout()
        mrow.setSpacing(S.p(8))
        for hk_lbl, hk_attr, hk_val, hk_col, hk_tip in [
            ("처리시간", "latency",   "0ms",  C['green'],  _PIPE_TIP),
            ("피처 품질", "quality",   "1.00", C['green'],  None),
            ("캐시 나이", "cache_age", "0s",   C['blue'],   None),
            ("예외/10m", "exception", "0",    C['text2'],  None),
        ]:
            hf = QFrame()
            hf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:{S.p(3)}px;")
            hfl = QVBoxLayout(hf)
            hfl.setContentsMargins(S.p(6), S.p(4), S.p(6), S.p(4))
            hfl.setSpacing(S.p(2))
            hk_title = mk_label(hk_lbl, C['text2'], 10, align=Qt.AlignCenter)
            if hk_tip:
                hf.setToolTip(hk_tip)
                hk_title.setToolTip(hk_tip)
                hk_title.setStyleSheet(
                    f"color:{C['text2']};font-size:{S.f(10)}px;"
                    f"text-decoration:underline dotted;"
                )
            hfl.addWidget(hk_title)
            hv = mk_val_label(hk_val, hk_col, 13, align=Qt.AlignCenter)
            if hk_tip:
                hv.setToolTip(hk_tip)
            hfl.addWidget(hv)
            mrow.addWidget(hf)
            self._health_vals[hk_attr] = hv
        lay.addLayout(mrow)

        # ── 중단: 상태 + 모드 라벨 ────────────────────────────────
        self._health_mode_lbl = mk_label("상태: INFO | Mode: NORMAL", C['text2'], 10, bold=True)
        lay.addWidget(self._health_mode_lbl)
        lay.addWidget(mk_sep())

        # ── 하단: 3라인 스파크라인 ────────────────────────────────
        self._health_spark_lbl = mk_label("Health Score:  ─────────────────", C['yellow'], 10)
        self._health_latency_spark_lbl = mk_label("처리시간 추이:    ─────────────────", C['orange'], 10)
        self._health_quality_spark_lbl = mk_label("피처 품질 추이:    ─────────────────", C['cyan'], 10)
        self._health_spark_meta = mk_label("최근 30분 추이", C['text2'], 9)
        
        self._health_spark_lbl.setStyleSheet(
            f"color:{C['yellow']};font-size:{S.f(11)}px;font-family:Consolas,monospace;font-weight:bold;"
        )
        self._health_latency_spark_lbl.setStyleSheet(
            f"color:{C['orange']};font-size:{S.f(11)}px;font-family:Consolas,monospace;font-weight:bold;"
        )
        self._health_quality_spark_lbl.setStyleSheet(
            f"color:{C['cyan']};font-size:{S.f(11)}px;font-family:Consolas,monospace;font-weight:bold;"
        )
        
        lay.addWidget(self._health_spark_lbl)
        lay.addWidget(self._health_latency_spark_lbl)
        lay.addWidget(self._health_quality_spark_lbl)
        lay.addWidget(self._health_spark_meta)
        lay.addStretch()

    def _spark_line(self, values: list, width: int = 20) -> str:
        """수치 값 배열을 ASCII 스파크라인으로 변환."""
        if not values or all(v is None for v in values):
            return "─" * width
        vals = [v for v in values if v is not None]
        if len(vals) < 2:
            return "─" * width
        minv, maxv = min(vals), max(vals)
        if minv == maxv:
            return "━" * width
        
        chars = "▁▂▃▄▅▆▇█"
        line = ""
        for v in vals[-width:]:
            idx = max(0, min(7, int((v - minv) / (maxv - minv) * 8)))
            line += chars[idx]
        return line if len(line) == width else "─" * width

    def update_health_metrics(self, health_score: float = None, latency_ms: float = None,
                              quality: float = None, cache_age_sec: float = None,
                              exception_count_10m: int = None, mode_str: str = None,
                              thresholds: dict = None):
        """운영 헬스 메트릭 갱신.
        
        Args:
            health_score: 0~1 범위 헬스 스코어
            latency_ms: API 지연 (ms)
            quality: 피처 품질 0~1 (1=최고)
            cache_age_sec: 캐시 나이 (초)
            exception_count_10m: 10분당 예외 수
            mode_str: 상태 문자열 (예: "INFO", "WARN", "CRITICAL")
            thresholds: 임계값 dict (업데이트할 경우)
        """
        if thresholds:
            self._thresholds.update(thresholds)

        # 메트릭 값 갱신
        if latency_ms is not None:
            col = C['green']
            if latency_ms > self._thresholds.get("latency_crit_ms", 1000):
                col = C['red']
            elif latency_ms > self._thresholds.get("latency_warn_ms", 500):
                col = C['orange']
            self._health_vals["latency"].setText(f"{latency_ms:.0f}ms")
            self._health_vals["latency"].setStyleSheet(f"color:{col};font-size:{S.f(13)}px;font-weight:bold;")
            self._health_latency_trend_values.append(latency_ms)
            if len(self._health_latency_trend_values) > 30:
                self._health_latency_trend_values.pop(0)

        if quality is not None:
            col = C['green']
            if quality < self._thresholds.get("quality_crit", 0.70):
                col = C['red']
            elif quality < self._thresholds.get("quality_warn", 0.85):
                col = C['orange']
            self._health_vals["quality"].setText(f"{quality:.2f}")
            self._health_vals["quality"].setStyleSheet(f"color:{col};font-size:{S.f(13)}px;font-weight:bold;")
            self._health_quality_trend_values.append(quality)
            if len(self._health_quality_trend_values) > 30:
                self._health_quality_trend_values.pop(0)

        if cache_age_sec is not None:
            col = C['green']
            if cache_age_sec > self._thresholds.get("cache_age_crit_sec", 600):
                col = C['red']
            elif cache_age_sec > self._thresholds.get("cache_age_warn_sec", 300):
                col = C['orange']
            self._health_vals["cache_age"].setText(f"{cache_age_sec:.0f}s")
            self._health_vals["cache_age"].setStyleSheet(f"color:{col};font-size:{S.f(13)}px;font-weight:bold;")

        if exception_count_10m is not None:
            col = C['text2']
            if exception_count_10m >= self._thresholds.get("exception_density_crit_10m", 10):
                col = C['red']
            elif exception_count_10m >= self._thresholds.get("exception_density_warn_10m", 5):
                col = C['orange']
            self._health_vals["exception"].setText(f"{exception_count_10m}")
            self._health_vals["exception"].setStyleSheet(f"color:{col};font-size:{S.f(13)}px;font-weight:bold;")

        if health_score is not None:
            self._health_trend_values.append(health_score)
            if len(self._health_trend_values) > 30:
                self._health_trend_values.pop(0)

        # 상태 라벨 갱신
        if mode_str:
            self._health_mode_lbl.setText(mode_str)

        # 스파크라인 갱신
        spark_score = self._spark_line(self._health_trend_values, 20)
        spark_latency = self._spark_line(self._health_latency_trend_values, 20)
        spark_quality = self._spark_line(self._health_quality_trend_values, 20)

        self._health_spark_lbl.setText(f"Health Score:  {spark_score}")
        self._health_latency_spark_lbl.setText(f"처리시간 추이:    {spark_latency}")
        self._health_quality_spark_lbl.setText(f"피처 품질 추이:    {spark_quality}")


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

    _DAILY_HEADERS   = ["날짜",  "거래", "승", "패", "승률", "P/L pt", "P/L 원",   "누적 원"]
    _WEEKLY_HEADERS  = ["주간",  "거래", "승", "패", "승률", "P/L pt", "P/L 원",   "누적 원", "MDD 원"]
    _MONTHLY_HEADERS = ["월",    "거래", "승", "패", "승률", "P/L pt", "P/L 원",   "누적 원", "샤프"]

    def __init__(self):
        super().__init__()
        self._rows = []
        self._broker_pnl: dict = {}  # date → broker settled KRW
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

        # 소스 선택 체크박스 (탭바 우측 코너)
        _cb_style = (
            f"QCheckBox{{color:{C['text2']};font-size:{S.f(9)}px;spacing:{S.p(3)}px;}}"
            f"QCheckBox::indicator{{width:{S.p(11)}px;height:{S.p(11)}px;"
            f"border:1px solid {C['border']};border-radius:2px;}}"
            f"QCheckBox::indicator:checked{{background:{C['cyan']};"
            f"border:1px solid {C['cyan']};}}"
            f"QCheckBox::indicator:unchecked{{background:{C['bg3']};}}"
        )
        self._cb_forward = QCheckBox("순방향")
        self._cb_reverse = QCheckBox("역방향")
        # 저장된 체크 상태 복원 (기본값: 둘 다 True)
        _saved_fwd, _saved_rev = self._load_cb_prefs()
        self._cb_forward.setChecked(_saved_fwd)
        self._cb_reverse.setChecked(_saved_rev)
        self._cb_forward.setStyleSheet(_cb_style)
        self._cb_reverse.setStyleSheet(_cb_style)
        self._cb_forward.stateChanged.connect(self._on_source_changed)
        self._cb_reverse.stateChanged.connect(self._on_source_changed)
        _corner = QWidget()
        _cl = QHBoxLayout(_corner)
        _cl.setContentsMargins(0, 0, 6, 0)
        _cl.setSpacing(10)
        _cl.addWidget(self._cb_forward)
        _cl.addWidget(self._cb_reverse)
        inner.setCornerWidget(_corner, Qt.TopRightCorner)

        lay.addWidget(inner, 1)

    # 날짜/주간/월(0) · 거래(1) · 승(2) · 패(3) · 승률(4) → Fixed 고정폭
    # 나머지 값 열(5+) → Stretch
    _NARROW_WIDTHS = {0: 72, 1: 36, 2: 30, 3: 30, 4: 44}

    def _make_tbl(self, headers):
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.verticalHeader().setVisible(False)
        tbl.setShowGrid(True)
        tbl.setSortingEnabled(False)
        tbl.horizontalHeader().setHighlightSections(False)
        tbl.setStyleSheet(
            f"QTableWidget{{background:{C['bg']};color:{C['text']};border:none;"
            f"gridline-color:{C['border']};font-size:{S.f(11)}px;}}"
            f"QTableWidget::item{{padding:2px 5px;}}"
            f"QHeaderView::section{{background:{C['bg2']};color:{C['text2']};"
            f"border:none;border-bottom:1px solid {C['border']};"
            f"border-right:1px solid {C['border']};"
            f"font-size:{S.f(10)}px;font-weight:bold;padding:3px 5px;}}"
            f"QTableWidget::item:selected{{background:{C['bg3']};color:{C['text']};}}"
        )
        hdr = tbl.horizontalHeader()
        # 값 열 기본 모드: Stretch
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        # 좁은 열(날짜·거래·승·패·승률)은 Fixed 고정폭
        for col, w in self._NARROW_WIDTHS.items():
            if col < len(headers):
                hdr.setSectionResizeMode(col, QHeaderView.Fixed)
                tbl.setColumnWidth(col, S.p(w))
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
        try:
            from utils.db_utils import fetch_broker_daily_pnl_map
            self._broker_pnl = fetch_broker_daily_pnl_map(90)
        except Exception:
            self._broker_pnl = {}
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
                    "reverse_entry_enabled": int(r["reverse_entry_enabled"] or 0),
                })
            except Exception:
                pass
        self._build_daily()
        self._build_weekly()
        self._build_monthly()
        self._build_summary()

    # ── 그룹화 유틸 ────────────────────────────────────────────

    def _active_rows(self):
        """체크박스 상태에 따라 self._rows 필터링.
        순방향=reverse_entry_enabled==0, 역방향=reverse_entry_enabled==1.
        """
        fwd = self._cb_forward.isChecked()
        rev = self._cb_reverse.isChecked()
        if fwd and rev:
            return self._rows
        if fwd:
            return [r for r in self._rows if not r["reverse_entry_enabled"]]
        if rev:
            return [r for r in self._rows if r["reverse_entry_enabled"]]
        return []

    def _group(self, key_fn):
        from collections import defaultdict
        d = defaultdict(list)
        for r in self._active_rows():
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

    def _daily_bucket(self, rows):
        """거래 목록을 날짜(YYYY-MM-DD) → 거래 리스트로 묶는다."""
        from collections import defaultdict
        d = defaultdict(list)
        for r in rows:
            d[r["entry_ts"][:10]].append(r)
        return d

    def _effective_day_krw(self, date_str, day_rows):
        """해당 날짜의 브로커 정산 실현손익이 있으면 그 값을, 없으면 거래 원시
        pnl_krw 합계를 반환. 일별/주별/월별/요약 카드가 모두 이 값을 기준으로
        삼아야 누적·MDD·샤프가 서로 어긋나지 않는다."""
        broker_krw = self._broker_pnl.get(date_str)
        if broker_krw is not None:
            return broker_krw
        return sum(r["pnl_krw"] for r in day_rows)

    def _group_effective_krw(self, grp):
        """grp(여러 날짜에 걸친 거래 목록)의 날짜별 브로커 정산 우선 합계."""
        day_rows = self._daily_bucket(grp)
        return sum(self._effective_day_krw(d, rs) for d, rs in day_rows.items())

    def _mdd(self, rows, krw_key="pnl_krw"):
        """전체 거래의 날짜별 브로커 정산 우선 손익 기준 MDD."""
        day_rows = self._daily_bucket(rows)
        eq, peak, mdd = 0.0, 0.0, 0.0
        for date_str in sorted(day_rows):
            eq  += self._effective_day_krw(date_str, day_rows[date_str])
            peak = max(peak, eq)
            mdd  = min(mdd, eq - peak)
        return round(mdd, 0)

    def _mdd_daily(self, grp) -> float:
        """일별 손익(브로커 정산 우선) 기준 MDD — 거래 단위 진동 제거."""
        day_rows = self._daily_bucket(grp)
        eq, peak, mdd = 0.0, 0.0, 0.0
        for date_str in sorted(day_rows):
            v = self._effective_day_krw(date_str, day_rows[date_str])
            eq += v
            peak = max(peak, eq)
            mdd = min(mdd, eq - peak)
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

    def _sel_val(self, exec_val, fwd_val):
        """체크박스 선택에 따라 표시할 값 반환 (순방향=exec, 역방향=forward)."""
        fwd = self._cb_forward.isChecked()
        rev = self._cb_reverse.isChecked()
        if fwd and rev:
            return exec_val + fwd_val
        if fwd:
            return exec_val
        if rev:
            return fwd_val
        return 0.0

    def _fmt_val(self, exec_val, fwd_val, decimals=0, suffix=""):
        val = self._sel_val(exec_val, fwd_val)
        if decimals == 0:
            return f"{val:+,.0f}{suffix}"
        return f"{val:+,.{decimals}f}{suffix}"

    def _fmt_single(self, val, decimals=0, suffix=""):
        if decimals == 0:
            return f"{val:+,.0f}{suffix}"
        return f"{val:+,.{decimals}f}{suffix}"

    def _mdd_sel(self, rows):
        eq, peak, mdd = 0.0, 0.0, 0.0
        for r in sorted(rows, key=lambda x: x["entry_ts"]):
            eq += self._sel_val(r["pnl_krw"], r["forward_pnl_krw"])
            peak = max(peak, eq)
            mdd = min(mdd, eq - peak)
        return round(mdd, 0)

    def _sharpe_sel(self, grp):
        dp = {}
        for r in grp:
            d = r["entry_ts"][:10]
            dp[d] = dp.get(d, 0) + self._sel_val(r["pnl_krw"], r["forward_pnl_krw"])
        return self._sharpe(list(dp.values()))

    def _sharpe_grp(self, grp):
        day_rows = self._daily_bucket(grp)
        dp = {d: self._effective_day_krw(d, rs) for d, rs in day_rows.items()}
        return self._sharpe(list(dp.values()))

    def _load_cb_prefs(self):
        """ui_prefs.json에서 순방향/역방향 체크 상태 복원. 기본값: (True, True)."""
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            if not os.path.exists(_f):
                return True, True
            with open(_f, "r", encoding="utf-8") as _fp:
                _p = json.load(_fp)
            return bool(_p.get("pnl_cb_forward", True)), bool(_p.get("pnl_cb_reverse", True))
        except Exception:
            return True, True

    def _save_cb_prefs(self):
        """현재 체크 상태를 ui_prefs.json에 저장."""
        try:
            _f = os.path.join(DATA_DIR, "ui_prefs.json")
            _p = {}
            if os.path.exists(_f):
                with open(_f, "r", encoding="utf-8") as _fp:
                    _p = json.load(_fp)
            _p["pnl_cb_forward"] = self._cb_forward.isChecked()
            _p["pnl_cb_reverse"] = self._cb_reverse.isChecked()
            with open(_f, "w", encoding="utf-8") as _fp:
                json.dump(_p, _fp, ensure_ascii=False)
        except Exception:
            pass

    def _on_source_changed(self):
        self._save_cb_prefs()
        if self._rows:
            self._build_daily()
            self._build_weekly()
            self._build_monthly()
            self._build_summary()

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
        cum_map, c = {}, 0.0
        for date_str, grp in groups:
            _, _, _, _, pkrw = self._stats(grp)
            broker_krw = self._broker_pnl.get(date_str)
            day_krw = broker_krw if broker_krw is not None else pkrw
            c += day_krw
            cum_map[date_str] = c

        tbl = self.tbl_daily
        tbl.setRowCount(len(groups))
        for r_idx, (date_str, grp) in enumerate(reversed(groups)):
            n, wins, losses, ppts, pkrw = self._stats(grp)
            cum       = cum_map[date_str]
            broker_krw = self._broker_pnl.get(date_str)
            if broker_krw is not None:
                disp_krw = broker_krw
                krw_text = f"{broker_krw:+,.0f}원"
            else:
                disp_krw = pkrw
                krw_text = self._fmt_single(pkrw, suffix="원")
            wr   = f"{wins/n*100:.0f}%" if n else "—"
            bg   = self._row_bg(disp_krw)
            pc   = self._pcol(disp_krw)
            cc   = self._pcol(cum)
            is_t = (date_str == today)
            cells = [
                self._item(date_str,                                            fg=C['yellow'] if is_t else None, bg=bg, bold=is_t),
                self._item(str(n),                                              bg=bg, align=Qt.AlignRight),
                self._item(str(wins),                                           fg=C['green'], bg=bg, align=Qt.AlignRight),
                self._item(str(losses),                                         fg=C['red'],   bg=bg, align=Qt.AlignRight),
                self._item(wr,                                                  fg=C['cyan'],  bg=bg),
                self._item(self._fmt_single(ppts, decimals=2, suffix="pt"),     fg=pc, bg=bg, align=Qt.AlignRight),
                self._item(krw_text,                                            fg=pc, bg=bg, align=Qt.AlignRight, bold=True),
                self._item(self._fmt_single(cum, suffix="원"),                  fg=cc, bg=bg, align=Qt.AlignRight),
            ]
            for c_idx, it in enumerate(cells):
                tbl.setItem(r_idx, c_idx, it)

    # ── 주별 테이블 ────────────────────────────────────────────

    def _build_weekly(self):
        groups  = self._group(self._week_key)[-13:]
        cum_map, c = {}, 0.0
        for wk, grp in groups:
            eff_krw = self._group_effective_krw(grp)
            c += eff_krw
            cum_map[wk] = c

        tbl = self.tbl_weekly
        tbl.setRowCount(len(groups))
        for r_idx, (wk, grp) in enumerate(reversed(groups)):
            n, wins, losses, ppts, _ = self._stats(grp)
            pkrw      = self._group_effective_krw(grp)
            mdd       = self._mdd_daily(grp)
            cum       = cum_map[wk]
            disp_krw  = pkrw
            wr   = f"{wins/n*100:.0f}%" if n else "—"
            bg   = self._row_bg(disp_krw)
            pc   = self._pcol(disp_krw)
            cc   = self._pcol(cum)
            mc   = self._pcol(mdd)
            cells = [
                self._item(wk,                                                  bg=bg, bold=True),
                self._item(str(n),                                              bg=bg, align=Qt.AlignRight),
                self._item(str(wins),                                           fg=C['green'], bg=bg, align=Qt.AlignRight),
                self._item(str(losses),                                         fg=C['red'],   bg=bg, align=Qt.AlignRight),
                self._item(wr,                                                  fg=C['cyan'],  bg=bg),
                self._item(self._fmt_single(ppts, decimals=2, suffix="pt"),     fg=pc, bg=bg, align=Qt.AlignRight),
                self._item(self._fmt_single(pkrw, suffix="원"),                 fg=pc, bg=bg, align=Qt.AlignRight, bold=True),
                self._item(self._fmt_single(cum, suffix="원"),                  fg=cc, bg=bg, align=Qt.AlignRight),
                self._item(self._fmt_single(mdd, suffix="원"),                  fg=mc, bg=bg, align=Qt.AlignRight),
            ]
            for c_idx, it in enumerate(cells):
                tbl.setItem(r_idx, c_idx, it)

    # ── 월별 테이블 ────────────────────────────────────────────

    def _build_monthly(self):
        groups  = self._group(lambda ts: ts[:7])
        cum_map, c = {}, 0.0
        for mon, grp in groups:
            eff_krw = self._group_effective_krw(grp)
            c += eff_krw
            cum_map[mon] = c

        tbl = self.tbl_monthly
        tbl.setRowCount(len(groups))
        for r_idx, (mon, grp) in enumerate(reversed(groups)):
            n, wins, losses, ppts, _ = self._stats(grp)
            pkrw      = self._group_effective_krw(grp)
            cum       = cum_map[mon]
            disp_krw  = pkrw
            sharpe    = self._sharpe_grp(grp)
            wr   = f"{wins/n*100:.0f}%" if n else "—"
            bg   = self._row_bg(disp_krw)
            pc   = self._pcol(disp_krw)
            cc   = self._pcol(cum)
            sc   = (C['green'] if sharpe >= 1.0
                    else C['yellow'] if sharpe >= 0.5
                    else C['red']    if sharpe < 0
                    else C['text2'])
            cells = [
                self._item(mon,                                                 bg=bg, bold=True),
                self._item(str(n),                                              bg=bg, align=Qt.AlignRight),
                self._item(str(wins),                                           fg=C['green'], bg=bg, align=Qt.AlignRight),
                self._item(str(losses),                                         fg=C['red'],   bg=bg, align=Qt.AlignRight),
                self._item(wr,                                                  fg=C['cyan'],  bg=bg),
                self._item(self._fmt_single(ppts, decimals=2, suffix="pt"),     fg=pc, bg=bg, align=Qt.AlignRight),
                self._item(self._fmt_single(pkrw, suffix="원"),                 fg=pc, bg=bg, align=Qt.AlignRight, bold=True),
                self._item(self._fmt_single(cum, suffix="원"),                  fg=cc, bg=bg, align=Qt.AlignRight),
                self._item(self._fmt_single(sharpe, decimals=2),                fg=sc, bg=bg),
            ]
            for c_idx, it in enumerate(cells):
                tbl.setItem(r_idx, c_idx, it)

    # ── 요약 카드 갱신 ─────────────────────────────────────────

    def _build_summary(self):
        active = self._active_rows()
        if not active:
            for v in self._sum.values():
                v.setText("—")
            return

        days   = len(set(r["entry_ts"][:10] for r in active if r["entry_ts"]))
        trades = len(active)
        wins   = sum(1 for r in active if r["pnl_pts"] > 0)
        wr     = wins / trades * 100 if trades else 0
        # 총 손익: 브로커 정산값이 있는 날은 그 합계 사용 (일별/주별/월별과 동일 기준)
        disp_total = self._group_effective_krw(active)

        mdd = self._mdd(active)

        # 최장 연승
        best, cur = 0, 0
        for r in sorted(active, key=lambda x: x["entry_ts"]):
            if r["pnl_pts"] > 0:
                cur  += 1
                best  = max(best, cur)
            else:
                cur = 0

        pc = C['green'] if disp_total >= 0 else C['red']
        wc = '#4CAF50' if wr >= 55 else (C['yellow'] if wr >= 50 else C['red'])

        def _set(key, text, col):
            lbl = self._sum[key]
            lbl.setText(text)
            lbl.setStyleSheet(
                f"color:{col};font-size:{S.f(12)}px;font-weight:bold;"
            )

        _set("days",    f"{days}일",                              C['blue'])
        _set("trades",  f"{trades}건",                             C['text'])
        _set("winrate", f"{wr:.1f}%",                              wc)
        _set("total",   self._fmt_single(disp_total, suffix="원"), pc)
        _set("mdd",     self._fmt_single(mdd, suffix="원"),        C['orange'])
        _set("streak",  f"{best}연승",                             C['yellow'])


class LogPanel(QWidget):
    _SPARK_BLOCKS = "▁▂▃▄▅▆▇█"
    # [402차 후속7 P2-8] 탭별 로그 QTextEdit 보관 블록 상한.
    # QTextEdit은 QPlainTextEdit과 달리 setMaximumBlockCount()가 없어 문서가
    # 무제한으로 자란다 — 세션이 길어질수록 리치텍스트 문서 메모리가 단조 증가한다.
    # 2000줄이면 어느 탭이든 반나절 이력을 덮으며, 그보다 오래된 것은 어차피
    # logs/*.log 파일에서 봐야 한다(대시보드는 실시간 관찰용).
    # 주: 2026-07-30 실측에서 Qt 연산시간 자체는 종일 평탄했으므로 이 항목은
    #     당일 지연의 원인이 아니라 장시간 세션의 메모리 누적 대비다.
    _MAX_LOG_BLOCKS = 2000

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
            ("6 운영 헬스", C['yellow'], "health"),
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
                    ("최근20건 순EV", "ev20",     C['yellow']),
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
                    elif attr == "ev20":
                        mf.setToolTip(_EV20_TIP)
                        title_lbl.setToolTip(_EV20_TIP)
                        title_lbl.setStyleSheet(
                            f"color:{C['text2']};font-size:{S.f(10)}px;"
                            f"text-decoration:underline dotted;"
                        )
                    mfl.addWidget(title_lbl)
                    vl = mk_val_label("——원", mc, 13, align=Qt.AlignCenter)
                    mfl.addWidget(vl)
                    if attr != "ev20":
                        pb = mk_prog(mc, 4)
                        pb.setValue(0)
                        mfl.addWidget(pb)
                        self._pnl_bars[attr] = pb
                    mrow.addWidget(mf)
                    self._pnl_vals[attr] = vl
                pl.addLayout(mrow)

            elif key == "model":
                mrow = QHBoxLayout()
                self._model_vals = {}
                for mk_lbl, mk_attr, mk_val, mc in [
                    ("정확도(50분)", "accuracy", "——%",   C['text2']),
                    ("SGD 비중",     "sgd_w",    "——%",   C['purple']),
                    ("자가학습",     "active",   "○ 대기", C['text2']),
                ]:
                    mf = QFrame()
                    mf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    mfl = QVBoxLayout(mf); mfl.setContentsMargins(5,3,5,3)
                    mfl.addWidget(mk_label(mk_lbl, C['text2'], 10, align=Qt.AlignCenter))
                    vl = mk_val_label(mk_val, mc, 13, align=Qt.AlignCenter)
                    mfl.addWidget(vl)
                    mrow.addWidget(mf)
                    self._model_vals[mk_attr] = vl
                pl.addLayout(mrow)

            elif key == "health":
                mrow = QHBoxLayout()
                self._health_vals = {}
                self._health_trend_values = []
                self._health_latency_trend_values = []
                self._health_quality_trend_values = []
                _PIPE_TIP = (
                    "파이프라인 처리시간 (CB⑤ 대체 지표)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "≤ 1000ms  정상 (green)\n"
                    "≤ 4999ms  경고 로그 [CB⑤] (orange)\n"
                    "≥ 5000ms  5분 진입 정지 + Slack (red)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Cybos Plus는 COM 콜백 기반으로\n"
                    "네트워크 RTT 측정 불가 — 파이프라인\n"
                    "실행시간을 API 지연 대체 지표로 사용"
                )
                for hk_lbl, hk_attr, hk_val, hk_col, hk_tip in [
                    ("처리시간", "latency",   "0ms",  C['green'],  _PIPE_TIP),
                    ("피처 품질", "quality",   "1.00", C['green'],  None),
                    ("캐시 나이", "cache_age", "0s",   C['blue'],   None),
                    ("예외/10m", "exception", "0",    C['text2'],  None),
                ]:
                    hf = QFrame()
                    hf.setStyleSheet(f"background:{C['bg3']};border:1px solid {C['border']};border-radius:3px;")
                    hfl = QVBoxLayout(hf); hfl.setContentsMargins(5,3,5,3)
                    hk_title = mk_label(hk_lbl, C['text2'], 10, align=Qt.AlignCenter)
                    if hk_tip:
                        hf.setToolTip(hk_tip)
                        hk_title.setToolTip(hk_tip)
                        hk_title.setStyleSheet(
                            f"color:{C['text2']};font-size:{S.f(10)}px;"
                            f"text-decoration:underline dotted;"
                        )
                    hfl.addWidget(hk_title)
                    hv = mk_val_label(hk_val, hk_col, 13, align=Qt.AlignCenter)
                    if hk_tip:
                        hv.setToolTip(hk_tip)
                    hfl.addWidget(hv)
                    mrow.addWidget(hf)
                    self._health_vals[hk_attr] = hv
                pl.addLayout(mrow)

                self._health_mode_lbl = mk_label("상태: INFO | Mode: NORMAL", C['text2'], 10, bold=True)
                self._health_spark_lbl = mk_label("트렌드: ─────────────────", C['yellow'], 10)
                self._health_latency_spark_lbl = mk_label("지연:   ─────────────────", C['orange'], 10)
                self._health_quality_spark_lbl = mk_label("품질:   ─────────────────", C['cyan'], 10)
                self._health_spark_meta = mk_label("최근 30분 Health Score", C['text2'], 9)
                self._health_spark_lbl.setStyleSheet(
                    f"color:{C['yellow']};font-size:{S.f(11)}px;font-family:Consolas,monospace;font-weight:bold;"
                )
                self._health_latency_spark_lbl.setStyleSheet(
                    f"color:{C['orange']};font-size:{S.f(11)}px;font-family:Consolas,monospace;font-weight:bold;"
                )
                self._health_quality_spark_lbl.setStyleSheet(
                    f"color:{C['cyan']};font-size:{S.f(11)}px;font-family:Consolas,monospace;font-weight:bold;"
                )
                pl.addWidget(self._health_mode_lbl)
                pl.addWidget(self._health_spark_lbl)
                pl.addWidget(self._health_latency_spark_lbl)
                pl.addWidget(self._health_quality_spark_lbl)
                pl.addWidget(self._health_spark_meta)

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

    def update_model_cards(self, accuracy: float, sgd_weight: float, is_active: bool):
        """창5 모델 AI 카드 갱신 (정확도·SGD비중·자가학습)."""
        if not hasattr(self, "_model_vals"):
            return
        # 정확도
        acc_lbl = self._model_vals["accuracy"]
        acc_lbl.setText(f"{accuracy:.1%}")
        acc_col = (C['green'] if accuracy >= 0.55
                   else C['yellow'] if accuracy >= 0.45
                   else C['orange'])
        acc_lbl.setStyleSheet(f"color:{acc_col};font-size:{S.f(13)}px;font-weight:bold;")
        # SGD 비중
        sgd_lbl = self._model_vals["sgd_w"]
        sgd_lbl.setText(f"{sgd_weight:.0%}")
        sgd_lbl.setStyleSheet(f"color:{C['purple']};font-size:{S.f(13)}px;font-weight:bold;")
        # 자가학습 활성
        act_lbl = self._model_vals["active"]
        if is_active:
            act_lbl.setText("● 활성")
            act_lbl.setStyleSheet(f"color:{C['green']};font-size:{S.f(13)}px;font-weight:bold;")
        else:
            act_lbl.setText("○ 대기")
            act_lbl.setStyleSheet(f"color:{C['text2']};font-size:{S.f(13)}px;font-weight:bold;")

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

    def update_recent_ev(self, cnt: int, avg_net_pnl_krw: float, win_rate: float) -> None:
        """[260704 감사 P0] 최근 N건 순EV(수수료 차감 후) 타일 갱신.
        trades.db 기록 직후 호출 — utils.db_utils.fetch_recent_ev() 결과를 그대로 전달.
        """
        lbl = self._pnl_vals.get("ev20")
        if not lbl:
            return
        col = C['green'] if avg_net_pnl_krw >= 0 else C['red']
        if cnt <= 0:
            lbl.setText("——원")
            lbl.setStyleSheet(f"color:{C['text2']};font-size:{S.f(13)}px;font-weight:bold;")
            return
        lbl.setText(f"{avg_net_pnl_krw:+,.0f}원 ({cnt}건,승{win_rate*100:.0f}%)")
        lbl.setStyleSheet(f"color:{col};font-size:{S.f(13)}px;font-weight:bold;")

    @classmethod
    def _trim_log_blocks(cls, tb: QTextEdit) -> None:
        """[402차 후속7 P2-8] 문서가 _MAX_LOG_BLOCKS를 넘으면 오래된 블록부터 삭제.

        QTextEdit에는 QPlainTextEdit.setMaximumBlockCount()에 해당하는 기능이
        없어 직접 잘라낸다. 삽입은 1줄씩 일어나므로 통상 1블록만 제거된다.
        스크롤은 삽입부에서 항상 맨 아래로 보정하므로 위치가 튀지 않는다.
        """
        try:
            doc = tb.document()
            extra = doc.blockCount() - cls._MAX_LOG_BLOCKS
            if extra <= 0:
                return
            cursor = QTextCursor(doc)
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor, extra)
            cursor.removeSelectedText()
            cursor.deleteChar()   # 선택 삭제 후 남는 빈 블록 제거
        except Exception:
            pass

    @classmethod
    def _insert_html_left(cls, tb: QTextEdit, html: str) -> None:
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

        cls._trim_log_blocks(tb)
        cursor.movePosition(QTextCursor.End)
        tb.setTextCursor(cursor)
        tb.verticalScrollBar().setValue(tb.verticalScrollBar().maximum())

    @classmethod
    def _insert_html_center(cls, tb: QTextEdit, html: str) -> None:
        """HTML을 가운데 정렬 블록으로 삽입 (구분선용)."""
        fmt = QTextBlockFormat()
        fmt.setAlignment(Qt.AlignCenter)

        cursor = tb.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock(fmt)
        cursor.insertHtml(html)

        cls._trim_log_blocks(tb)
        cursor.movePosition(QTextCursor.End)
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
            "SHAP":   C['yellow'], "HEALTH": C['yellow'],
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

    def update_health_metrics(
        self,
        latency_ms: float,
        quality_score: float,
        cache_age_sec: float,
        exception_density_10m: float,
        trend_window_min: int = 30,
        health_level: str = "INFO",
        degraded_mode: bool = False,
        thresholds: dict = None,
    ):
        """운영 헬스 탭 상단 지표 갱신."""
        if not hasattr(self, "_health_vals"):
            return

        th = thresholds or {}
        latency_warn_ms = float(th.get("latency_warn_ms", HEALTH_LATENCY_WARN_MS))
        latency_crit_ms = float(th.get("latency_crit_ms", HEALTH_LATENCY_CRIT_MS))
        quality_warn = float(th.get("quality_warn", HEALTH_QUALITY_WARN))
        quality_crit = float(th.get("quality_crit", HEALTH_QUALITY_CRIT))
        cache_warn_sec = float(th.get("cache_age_warn_sec", HEALTH_CACHE_AGE_WARN_SEC))
        cache_crit_sec = float(th.get("cache_age_crit_sec", HEALTH_CACHE_AGE_CRIT_SEC))
        exc_warn_10m = float(th.get("exception_warn_10m", HEALTH_EXCEPTION_DENSITY_WARN_10M))
        exc_crit_10m = float(th.get("exception_crit_10m", HEALTH_EXCEPTION_DENSITY_CRIT_10M))

        lat_col = C['green'] if latency_ms < latency_warn_ms else (C['orange'] if latency_ms < latency_crit_ms else C['red'])
        self._health_vals["latency"].setText(f"{latency_ms:.0f}ms")
        self._health_vals["latency"].setStyleSheet(f"color:{lat_col};font-size:{S.f(13)}px;font-weight:bold;")

        q_col = C['green'] if quality_score >= quality_warn else (C['orange'] if quality_score >= quality_crit else C['red'])
        self._health_vals["quality"].setText(f"{quality_score:.2f}")
        self._health_vals["quality"].setStyleSheet(f"color:{q_col};font-size:{S.f(13)}px;font-weight:bold;")

        c_col = C['green'] if cache_age_sec < cache_warn_sec else (C['yellow'] if cache_age_sec < cache_crit_sec else C['red'])
        self._health_vals["cache_age"].setText(f"{cache_age_sec:.0f}s")
        self._health_vals["cache_age"].setStyleSheet(f"color:{c_col};font-size:{S.f(13)}px;font-weight:bold;")

        e_col = C['green'] if exception_density_10m < exc_warn_10m else (C['orange'] if exception_density_10m < exc_crit_10m else C['red'])
        self._health_vals["exception"].setText(f"{exception_density_10m:.0f}")
        self._health_vals["exception"].setStyleSheet(f"color:{e_col};font-size:{S.f(13)}px;font-weight:bold;")

        level_col = C['green'] if health_level == "INFO" else (C['orange'] if health_level == "WARNING" else C['red'])
        self._health_mode_lbl.setText(
            f"상태: {health_level} | Mode: {'DEGRADED' if degraded_mode else 'NORMAL'}"
        )
        self._health_mode_lbl.setStyleSheet(f"color:{level_col};font-size:{S.f(10)}px;font-weight:bold;")

        max_exc = max(1.0, float(exc_crit_10m))
        health_score = (
            quality_score * 0.45
            + (1.0 - min(max(latency_ms, 0.0) / max(1.0, float(latency_crit_ms)), 1.0)) * 0.25
            + (1.0 - min(max(cache_age_sec, 0.0) / max(1.0, float(cache_crit_sec)), 1.0)) * 0.15
            + (1.0 - min(max(exception_density_10m, 0.0) / max_exc, 1.0)) * 0.15
        )
        health_score = max(0.0, min(1.0, float(health_score)))
        self._health_trend_values.append(health_score)
        self._health_latency_trend_values.append(float(latency_ms))
        self._health_quality_trend_values.append(float(quality_score))
        width = max(6, int(trend_window_min))
        if len(self._health_trend_values) > width:
            self._health_trend_values = self._health_trend_values[-width:]
        if len(self._health_latency_trend_values) > width:
            self._health_latency_trend_values = self._health_latency_trend_values[-width:]
        if len(self._health_quality_trend_values) > width:
            self._health_quality_trend_values = self._health_quality_trend_values[-width:]
        self._health_spark_lbl.setText(f"트렌드: {self._spark_line(self._health_trend_values, width=width)}")
        self._health_latency_spark_lbl.setText(
            f"지연:   {self._spark_line(self._health_latency_trend_values, width=width)}"
        )
        self._health_quality_spark_lbl.setText(
            f"품질:   {self._spark_line(self._health_quality_trend_values, width=width)}"
        )
        self._health_spark_meta.setText(f"최근 {width}분 Health Score")

    @classmethod
    def _spark_line(cls, values, width: int = 20) -> str:
        if not values:
            return "─" * max(1, int(width))
        vals = [float(v) for v in values[-width:]]
        vmin, vmax = min(vals), max(vals)
        if abs(vmax - vmin) < 1e-9:
            return cls._SPARK_BLOCKS[-1] * len(vals)
        out = []
        for v in vals:
            idx = int((v - vmin) / (vmax - vmin) * (len(cls._SPARK_BLOCKS) - 1))
            idx = max(0, min(len(cls._SPARK_BLOCKS) - 1, idx))
            out.append(cls._SPARK_BLOCKS[idx])
        return "".join(out)


# ────────────────────────────────────────────────────────────
# 메인 윈도우
# ────────────────────────────────────────────────────────────
# 레짐 배지 fg 색상 (regime_panel._MICRO_COLOR의 텍스트 색상과 동일)
_REGIME_BAR_COLOR = {
    "추세장": "#00c878",
    "횡보장": "#ffee58",
    "급변장": "#ff4444",
    "혼합":   "#8888ff",
    "탈진":   "#ce93d8",
}
_REGIME_BAR_H = 4   # x축 라인 위 레짐 바 높이(px)
_DIR_BAR_H    = 4   # 레짐 바 바로 위 방향예측 바 높이(px)
_DIR_BAR_COLOR = {
    1:  "#3fb950",   # UP   (녹색)
    -1: "#f85149",   # DOWN (적색)
    0:  "#444c56",   # FLAT (회색)
}


class MinuteChartCanvas(QWidget):
    RIGHT_PADDING_BARS = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._closed_candles = []
        self._live_candle = None
        self._completed_trades = []
        self._active_trade = None
        self._exit_markers = []
        self._visible_count = 0
        self._min_visible_count = 20
        self._view_offset = 0
        self._hover_pos = None
        self._dragging = False
        self._drag_start_pos = None
        self._drag_start_offset = 0
        self._last_step_px = 0.0
        self._last_plot_rect = QRectF()
        self._instrument_code = ""   # 현재 표시 중인 종목코드
        self._regime_map = {}        # {ts_key: regime_str} 봉별 레짐 히스토리
        self._dir_map    = {}        # {ts_key: direction_int} 봉별 방향예측 히스토리
        self._last_tick_update_ms: float = 0.0   # update() throttle용 타임스탬프
        self._last_mouse_update_ms: float = 0.0  # mouseMoveEvent throttle용
        # ── 디버그: 응답없음 분석용 ─────────────────────────────
        self._dbg_paint_count: int = 0
        self._dbg_paint_slow_count: int = 0
        self._dbg_mouse_event_count: int = 0
        self._dbg_mouse_log_ts: float = 0.0  # 마지막 빈도 로그 시각
        self.setMinimumHeight(S.p(420))
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setStyleSheet(f"background:{C['bg']};border:1px solid {C['border']};border-radius:6px;")

    def reset_session(self, candles, completed_trades, exit_markers=None):
        normalized = []
        for candle in candles:
            row = self._normalize_candle(candle)
            if row:
                normalized.append(row)
        self._closed_candles = normalized
        self._completed_trades = [dict(t) for t in completed_trades]
        self._live_candle = None
        self._active_trade = None
        self._exit_markers = list(exit_markers) if exit_markers else []
        total = len(self._closed_candles)
        self._visible_count = max(total, self._min_visible_count)
        self._view_offset = 0
        self._hover_pos = None
        self._dragging = False
        self._regime_map.clear()
        self._dir_map.clear()
        self.update()

    def set_regime_at(self, ts_key: str, regime: str):
        """봉 완성 후 레짐 기록. run_minute_pipeline 완료 시점에 호출."""
        if not ts_key or not regime:
            return
        self._regime_map[ts_key] = regime
        # 오래된 항목 정리 (최대 400봉)
        if len(self._regime_map) > 400:
            for k in sorted(self._regime_map)[:50]:
                del self._regime_map[k]
        self.update()

    def set_direction_at(self, ts_key: str, direction: int):
        """매분 앙상블 방향 기록. 닫힌 봉에 방향예측 색상 바로 표시.

        현재봉은 삼각형 마커가 예측을 표시하므로 _draw_direction_bar에서 제외.
        """
        if not ts_key:
            return
        self._dir_map[ts_key] = int(direction)
        if len(self._dir_map) > 400:
            for k in sorted(self._dir_map)[:50]:
                del self._dir_map[k]
        self.update()

    def update_tick(self, price: float, ts=None):
        price = float(price or 0.0)
        if price <= 0:
            return
        dt = self._coerce_dt(ts) or datetime.now()
        minute_dt = dt.replace(second=0, microsecond=0)
        key = minute_dt.strftime("%Y-%m-%d %H:%M:%S")

        if self._closed_candles and self._closed_candles[-1]["ts"] == key:
            self._closed_candles[-1]["close"] = price
            self._closed_candles[-1]["high"] = max(self._closed_candles[-1]["high"], price)
            self._closed_candles[-1]["low"] = min(self._closed_candles[-1]["low"], price)
        elif self._live_candle and self._live_candle["ts"] == key:
            self._live_candle["close"] = price
            self._live_candle["high"] = max(self._live_candle["high"], price)
            self._live_candle["low"] = min(self._live_candle["low"], price)
        else:
            self._live_candle = {
                "ts": key,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": 0,
            }
        # 틱 update() throttle: 200ms 이내 중복 요청 무시 (초당 수십 틱 × paintEvent 방지)
        import time as _time
        _now_ms = _time.monotonic() * 1000
        if _now_ms - self._last_tick_update_ms >= 200:
            self._last_tick_update_ms = _now_ms
            self.update()

    def on_candle_closed(self, candle: dict):
        normalized = self._normalize_candle(candle)
        if not normalized:
            return

        # 종목코드 전환 감지 — 코드가 바뀌면 차트 전체 초기화
        incoming_code = str(candle.get("code") or "").strip()
        if incoming_code and self._instrument_code and incoming_code != self._instrument_code:
            self._closed_candles = []
            self._live_candle = None
            self._exit_markers = []
            self._active_trade = None
        if incoming_code:
            self._instrument_code = incoming_code

        if self._closed_candles and self._closed_candles[-1]["ts"] == normalized["ts"]:
            self._closed_candles[-1] = normalized
        else:
            self._closed_candles.append(normalized)
        if self._live_candle and self._live_candle["ts"] == normalized["ts"]:
            self._live_candle = None
        self.update()

    def sync_active_trade(self, direction: str, price: float, ts=None):
        direction = str(direction or "").upper()
        price = float(price or 0.0)
        if direction not in ("LONG", "SHORT") or price <= 0:
            return
        dt = self._coerce_dt(ts) or datetime.now()
        existing = self._active_trade or {}
        if existing and str(existing.get("direction") or "").upper() == direction:
            entry_ts = self._coerce_dt(existing.get("entry_ts")) or dt
            if dt and entry_ts:
                entry_ts = min(entry_ts, dt)
            self._active_trade = {
                "direction": direction,
                "entry_price": price,
                "entry_ts": entry_ts,
            }
        else:
            self._active_trade = {
                "direction": direction,
                "entry_price": price,
                "entry_ts": dt,
            }
        self.update()

    def clear_active_trade(self):
        self._active_trade = None
        self.update()

    def record_entry(self, direction: str, price: float, ts=None):
        self.sync_active_trade(direction, price, ts=ts)

    def record_exit(
        self,
        price: float,
        ts=None,
        finalize: bool = True,
        pnl_pts: float = None,
        reason: str = "",
        direction: str = "",
    ):
        price = float(price or 0.0)
        dt = self._coerce_dt(ts) or datetime.now()
        if price <= 0:
            return

        outcome = self._infer_exit_outcome(finalize, pnl_pts, reason)
        self._exit_markers.append({
            "price": price,
            "ts": dt,
            "kind": "EXIT",
            "finalize": bool(finalize),
            "pnl_pts": pnl_pts,
            "reason": str(reason or ""),
            "direction": str(direction or (self._active_trade or {}).get("direction") or "").upper(),
            "outcome": outcome,
        })
        if finalize and self._active_trade:
            trade = dict(self._active_trade)
            trade["exit_price"] = price
            trade["exit_ts"] = dt
            trade["exit_reason"] = str(reason or "")
            trade["pnl_pts"] = pnl_pts
            trade["outcome"] = outcome
            self._completed_trades.append(trade)
            self._active_trade = None
        elif finalize and not self._active_trade:
            # [Fix3] entry 없이 finalize=True 호출 — exit_marker는 위에서 추가됐지만
            # completed_trades에 span이 없음. stuck_exit_flat 경로에서는 Fix1이 이를 방지하며,
            # 다른 경로에서 발생하면 WARN 로그로 감지한다.
            import logging as _log_fix3
            _log_fix3.getLogger(__name__).warning(
                "[ChartWarn] record_exit(finalize=True) called with no active_trade — "
                "exit_marker only @ %.2f reason=%s", price, reason or ""
            )
        self.update()

    def paintEvent(self, event):
        import time as _t
        _t0 = _t.monotonic()
        del event
        # 비정상 거대 캔버스 가드 — GDI 단편화 크래시 2차 방어
        # restore_saved_geometry에서 _CHART_MAX_LOGICAL_W/H로 1차 차단되므로
        # 여기는 세션 중 수동 리사이즈 후 단편화 크래시 대비 안전망
        # 3000×2000: DPI 150% → 4500×3000×4=54MB — 이 이상은 32-bit에서 unsafe
        if self.width() > 3000 or self.height() > 2000:
            logger.warning(
                "[ChartDBG] paintEvent 거대 캔버스 차단: %dx%d candles=%d",
                self.width(), self.height(), len(self._closed_candles),
            )
            QPainter(self).fillRect(self.rect(), QColor(C["bg"]))
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor(C["bg"]))

        candles = list(self._closed_candles)
        if self._live_candle:
            candles.append(dict(self._live_candle))

        if not candles:
            painter.setPen(QColor(C["text2"]))
            painter.drawText(self.rect(), Qt.AlignCenter, "당일 1분봉 데이터가 아직 없습니다.")
            return

        total_count = len(candles)
        visible_count = min(max(self._visible_count or total_count, self._min_visible_count), total_count)
        self._view_offset = self._clamp_view_offset(self._view_offset, total_count, visible_count)
        end_idx = total_count - self._view_offset
        start_idx = max(0, end_idx - visible_count)
        candles = candles[start_idx:end_idx]
        padded_count = max(len(candles) + self.RIGHT_PADDING_BARS, 1)

        left = S.p(58)
        top = S.p(22)
        right = S.p(18)
        bottom = S.p(34)
        plot = QRectF(left, top, max(10, self.width() - left - right), max(10, self.height() - top - bottom))
        self._last_plot_rect = plot

        prices = []
        for candle in candles:
            prices.extend([candle["open"], candle["high"], candle["low"], candle["close"]])
        for trade in self._completed_trades:
            prices.append(float(trade.get("entry_price") or 0.0))
            prices.append(float(trade.get("exit_price") or 0.0))
        if self._active_trade:
            prices.append(float(self._active_trade.get("entry_price") or 0.0))
        for marker in self._exit_markers:
            prices.append(float(marker.get("price") or 0.0))
        prices = [p for p in prices if p > 0]
        lo = min(prices)
        hi = max(prices)
        if hi <= lo:
            hi = lo + 1.0
        pad = max((hi - lo) * 0.08, 0.2)
        lo -= pad
        hi += pad

        import time as _t2
        _t_grid = _t2.monotonic(); self._draw_grid(painter, plot, lo, hi)
        _t_spans = _t2.monotonic()
        index_map = {c["ts"]: i for i, c in enumerate(candles)}
        self._draw_trade_spans(painter, plot, candles, index_map, lo, hi, padded_count)
        _t_candles = _t2.monotonic(); self._draw_candles(painter, plot, candles, lo, hi, padded_count)
        _t_dir    = _t2.monotonic();  self._draw_direction_bar(painter, plot, candles, padded_count)
        _t_regime = _t2.monotonic();  self._draw_regime_bar(painter, plot, candles, padded_count)
        _t_markers = _t2.monotonic(); self._draw_markers(painter, plot, candles, index_map, lo, hi, padded_count)
        _t_axes = _t2.monotonic();   self._draw_axes(painter, plot, candles, lo, hi, padded_count)
        _t_cross = _t2.monotonic();  self._draw_crosshair_and_tooltip(painter, plot, candles, lo, hi)
        _t_end = _t2.monotonic()

        self._dbg_paint_count += 1
        _elapsed_ms = (_t_end - _t0) * 1000
        if _elapsed_ms > 30:
            self._dbg_paint_slow_count += 1
            logger.warning(
                "[ChartDBG] paintEvent slow %.1fms | size=%dx%d candles=%d "
                "grid=%.1f spans=%.1f candles=%.1f dir=%.1f regime=%.1f markers=%.1f axes=%.1f cross=%.1f | "
                "slow_cnt=%d total_cnt=%d",
                _elapsed_ms, self.width(), self.height(), len(candles),
                (_t_spans  - _t_grid)    * 1000,
                (_t_candles- _t_spans)   * 1000,
                (_t_dir    - _t_candles) * 1000,
                (_t_regime - _t_dir)     * 1000,
                (_t_markers- _t_regime)  * 1000,
                (_t_axes   - _t_markers) * 1000,
                (_t_cross  - _t_axes)    * 1000,
                (_t_end    - _t_cross)   * 1000,
                self._dbg_paint_slow_count, self._dbg_paint_count,
            )

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        total = len(self._closed_candles) + (1 if self._live_candle else 0)
        if total <= 0 or delta == 0:
            event.ignore()
            return

        current = min(max(self._visible_count or total, self._min_visible_count), max(total, self._min_visible_count))
        if delta > 0:
            new_count = max(self._min_visible_count, int(current * 0.82))
        else:
            new_count = min(total, int(current * 1.22) + 1)

        self._visible_count = max(self._min_visible_count, min(new_count, total))
        self._view_offset = self._clamp_view_offset(self._view_offset, total, self._visible_count)
        self.update()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.pos()
            self._drag_start_offset = self._view_offset
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        import time as _time
        _now_ms = _time.monotonic() * 1000
        pos = event.pos()
        self._hover_pos = pos
        if self._dragging and self._drag_start_pos is not None and self._last_step_px > 0:
            dx = pos.x() - self._drag_start_pos.x()
            candle_shift = int(round(dx / self._last_step_px))
            total = len(self._closed_candles) + (1 if self._live_candle else 0)
            visible_count = min(max(self._visible_count or total, self._min_visible_count), max(total, 1))
            self._view_offset = self._clamp_view_offset(self._drag_start_offset - candle_shift, total, visible_count)
        if _now_ms - self._last_mouse_update_ms >= 16:
            self._last_mouse_update_ms = _now_ms
            self.update()
        # 디버그: 10초마다 이벤트 빈도 요약 로그
        self._dbg_mouse_event_count += 1
        if _now_ms - self._dbg_mouse_log_ts >= 10_000:
            if self._dbg_mouse_log_ts > 0:
                _hz = self._dbg_mouse_event_count / 10.0
                logger.debug(
                    "[ChartDBG] mouseMoveEvent %.0f ev/s | size=%dx%d paint_slow=%d/%d",
                    _hz, self.width(), self.height(),
                    self._dbg_paint_slow_count, self._dbg_paint_count,
                )
                if _hz > 200:
                    logger.warning(
                        "[ChartDBG] mouseMoveEvent 과부하 %.0f ev/s — throttle 점검 필요", _hz,
                    )
            self._dbg_mouse_event_count = 0
            self._dbg_mouse_log_ts = _now_ms
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self._drag_start_pos = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            total = len(self._closed_candles) + (1 if self._live_candle else 0)
            self._visible_count = max(total, self._min_visible_count)
            self._view_offset = 0
            self.update()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def leaveEvent(self, event):
        import time as _t
        _t0 = _t.monotonic()
        self._hover_pos = None
        self._dragging = False
        self._drag_start_pos = None
        self.update()
        _elapsed_ms = (_t.monotonic() - _t0) * 1000
        logger.debug(
            "[ChartDBG] leaveEvent → update() 예약 %.2fms | size=%dx%d visible=%s",
            _elapsed_ms, self.width(), self.height(),
            self.isVisible(),
        )
        super().leaveEvent(event)

    def _draw_grid(self, painter: QPainter, plot: QRectF, lo: float, hi: float):
        # 수평 6단계 미세 그리드
        grid_col = QColor(C["border"])
        grid_col.setAlpha(90)
        grid_pen = QPen(grid_col)
        grid_pen.setStyle(Qt.DotLine)
        grid_pen.setWidthF(0.8)
        painter.setPen(grid_pen)
        N_H = 6
        for idx in range(N_H + 1):
            y = plot.top() + plot.height() * idx / N_H
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))

        # 수직 시간 구분선 (더 연하게)
        v_col = QColor(C["border"])
        v_col.setAlpha(55)
        v_pen = QPen(v_col)
        v_pen.setStyle(Qt.DotLine)
        v_pen.setWidthF(0.6)
        painter.setPen(v_pen)
        for idx in range(7):
            x = plot.left() + plot.width() * idx / 6.0
            painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))

        # 가격 레이블
        f = painter.font()
        f.setPointSizeF(S.f(8))
        painter.setFont(f)
        lbl_col = QColor(C["text2"])
        lbl_col.setAlpha(200)
        painter.setPen(lbl_col)
        for idx in range(N_H + 1):
            price = hi - (hi - lo) * idx / N_H
            y = plot.top() + plot.height() * idx / N_H
            painter.drawText(QRectF(0, y - 10, plot.left() - 6, 20),
                             Qt.AlignRight | Qt.AlignVCenter, f"{price:.2f}")

    def _draw_candles(self, painter: QPainter, plot: QRectF, candles, lo: float, hi: float, padded_count: int):
        count = max(padded_count, 1)
        step = plot.width() / count
        self._last_step_px = step
        body_w   = max(3.0, min(18.0, step * 0.68))
        wick_w   = max(1.0, min(2.0, body_w * 0.14))
        corner_r = min(2.5, body_w * 0.20)

        # 색상 — 상승: 밝은 초록 테두리 + 반투명 채움 / 하락: 밝은 적색 + 반투명
        UP_BORDER   = QColor("#3FCF8E")
        UP_FILL     = QColor(14, 52, 32, 210)
        UP_WICK     = QColor("#3FCF8E")
        DOWN_BORDER = QColor("#F05454")
        DOWN_FILL   = QColor(60, 16, 18, 220)
        DOWN_WICK   = QColor("#F05454")

        for idx, candle in enumerate(candles):
            x = plot.left() + step * (idx + 0.5)
            high_y  = self._price_to_y(candle["high"],  plot, lo, hi)
            low_y   = self._price_to_y(candle["low"],   plot, lo, hi)
            open_y  = self._price_to_y(candle["open"],  plot, lo, hi)
            close_y = self._price_to_y(candle["close"], plot, lo, hi)
            rising  = candle["close"] >= candle["open"]

            border_col = UP_BORDER  if rising else DOWN_BORDER
            fill_col   = UP_FILL    if rising else DOWN_FILL
            wick_col   = UP_WICK    if rising else DOWN_WICK

            # 심지 (wick) — 몸통 아래에 먼저 그려 몸통이 위로 덮임
            wick_pen = QPen(wick_col)
            wick_pen.setWidthF(wick_w)
            painter.setPen(wick_pen)
            painter.drawLine(QPointF(x, high_y), QPointF(x, low_y))

            # 몸통
            top_y  = min(open_y, close_y)
            height = max(abs(close_y - open_y), 2.0)
            rect   = QRectF(x - body_w / 2.0, top_y, body_w, height)
            painter.setBrush(fill_col)
            painter.setPen(QPen(border_col, 1.3))
            if corner_r >= 1.0:
                painter.drawRoundedRect(rect, corner_r, corner_r)
            else:
                painter.drawRect(rect)

    def _draw_direction_bar(self, painter: QPainter, plot: QRectF, candles, padded_count: int):
        """레짐 바 바로 위에 봉별 방향예측 색상 바 (높이 _DIR_BAR_H px) 표시.

        현재봉(live_candle)은 건너뜀 — 삼각형 마커가 예측 표시 중이므로.
        """
        if not self._dir_map:
            return
        count   = max(padded_count, 1)
        step    = plot.width() / count
        bar_y   = plot.bottom() - _REGIME_BAR_H - _DIR_BAR_H  # 레짐 바 바로 위
        live_ts = self._live_candle["ts"] if self._live_candle else None
        painter.setPen(Qt.NoPen)
        prev_dir   = None
        for idx, candle in enumerate(candles):
            if candle["ts"] == live_ts:   # 현재봉: 삼각형 마커로 예측 중 → 건너뜀
                prev_dir = None
                continue
            direction = self._dir_map.get(candle["ts"])
            if direction is None:
                prev_dir = None
                continue
            color_hex = _DIR_BAR_COLOR.get(int(direction))
            if not color_hex:
                prev_dir = None
                continue
            if direction != prev_dir:
                col = QColor(color_hex)
                col.setAlpha(210)
                painter.setBrush(col)
                prev_dir = direction
            x = plot.left() + step * idx
            painter.drawRect(QRectF(x, bar_y, step - 1, _DIR_BAR_H))

    def _draw_regime_bar(self, painter: QPainter, plot: QRectF, candles, padded_count: int):
        """X축 라인 바로 위에 봉별 레짐 색상 바 (높이 _REGIME_BAR_H px) 표시."""
        if not self._regime_map:
            return
        count  = max(padded_count, 1)
        step   = plot.width() / count
        bar_y  = plot.bottom() - _REGIME_BAR_H  # x축 위로 밀착
        painter.setPen(Qt.NoPen)
        prev_regime = None
        prev_color  = None
        for idx, candle in enumerate(candles):
            regime = self._regime_map.get(candle["ts"])
            if not regime:
                prev_regime = None
                continue
            color_hex = _REGIME_BAR_COLOR.get(regime)
            if not color_hex:
                prev_regime = None
                continue
            # 레짐이 바뀔 때만 setBrush (성능 최적화)
            if regime != prev_regime:
                col = QColor(color_hex)
                col.setAlpha(210)
                painter.setBrush(col)
                prev_regime = regime
                prev_color  = col
            x = plot.left() + step * idx
            painter.drawRect(QRectF(x, bar_y, step - 1, _REGIME_BAR_H))

    def _draw_trade_spans(self, painter: QPainter, plot: QRectF, candles, index_map, lo: float, hi: float, padded_count: int):
        count = max(padded_count, 1)
        step = plot.width() / count
        for trade in self._completed_trades:
            entry_dt = self._coerce_dt(trade.get("entry_ts"))
            exit_dt = self._coerce_dt(trade.get("exit_ts"))
            if not entry_dt or not exit_dt:
                continue
            start_idx = self._resolve_index(index_map, candles, entry_dt)
            end_idx = self._resolve_index(index_map, candles, exit_dt)
            if start_idx is None or end_idx is None:
                continue
            y = self._price_to_y(float(trade.get("entry_price") or 0.0), plot, lo, hi)
            x1 = plot.left() + step * (start_idx + 0.5)
            x2 = plot.left() + step * (end_idx + 0.5)
            pnl_pts = float(trade.get("pnl_pts") or 0.0)
            if pnl_pts > 0:
                pen = QPen(QColor("#2FBF71"))
            elif pnl_pts < 0:
                pen = QPen(QColor("#FF5D73"))
            else:
                pen = QPen(QColor("#8B949E"))
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y), int(x2), int(y))

        if self._active_trade:
            entry_dt = self._coerce_dt(self._active_trade.get("entry_ts"))
            start_idx = self._resolve_index(index_map, candles, entry_dt)
            end_idx = len(candles) - 1 if candles else None
            if start_idx is not None and end_idx is not None:
                y = self._price_to_y(float(self._active_trade.get("entry_price") or 0.0), plot, lo, hi)
                x1 = plot.left() + step * (start_idx + 0.5)
                x2 = plot.left() + step * (end_idx + 0.5)
                color = C["green"] if self._active_trade.get("direction") == "LONG" else C["red"]
                pen = QPen(QColor(color))
                pen.setWidth(2)
                pen.setStyle(Qt.DashLine)
                painter.setPen(pen)
                painter.drawLine(int(x1), int(y), int(x2), int(y))

    def _draw_markers(self, painter: QPainter, plot: QRectF, candles, index_map, lo: float, hi: float, padded_count: int):
        count = max(padded_count, 1)
        step = plot.width() / count
        occupied = []

        if self._active_trade:
            marker = {
                "ts": self._active_trade.get("entry_ts"),
                "price": self._active_trade.get("entry_price"),
                "kind": self._active_trade.get("direction"),
            }
            self._draw_one_marker(painter, plot, candles, index_map, lo, hi, step, marker, occupied)

        for trade in self._completed_trades:
            entry_marker = {
                "ts": trade.get("entry_ts"),
                "price": trade.get("entry_price"),
                "kind": trade.get("direction"),
            }
            exit_marker = {
                "ts": trade.get("exit_ts"),
                "price": trade.get("exit_price"),
                "kind": "EXIT",
                "pnl_pts": trade.get("pnl_pts"),
                "reason": trade.get("exit_reason", ""),
                "direction": trade.get("direction", ""),
                "outcome": trade.get("outcome", "EXIT"),
            }
            self._draw_one_marker(painter, plot, candles, index_map, lo, hi, step, entry_marker, occupied)
            self._draw_one_marker(painter, plot, candles, index_map, lo, hi, step, exit_marker, occupied)

        for marker in self._exit_markers:
            if not marker.get("finalize"):
                self._draw_one_marker(painter, plot, candles, index_map, lo, hi, step, marker, occupied)

    def _draw_one_marker(self, painter, plot, candles, index_map, lo, hi, step, marker, occupied):
        dt = self._coerce_dt(marker.get("ts"))
        price = float(marker.get("price") or 0.0)
        kind = str(marker.get("kind") or "")
        if not dt or price <= 0 or not candles:
            return
        idx = self._resolve_index(index_map, candles, dt)
        if idx is None:
            return

        x = plot.left() + step * (idx + 0.5)
        y = self._price_to_y(price, plot, lo, hi)
        x, y = self._resolve_marker_overlap(x, y, occupied, kind)
        if kind == "LONG":
            color = QColor(C["green"])
            label = dt.strftime("L %H:%M")
            dy = -S.p(26)
            self._draw_entry_marker(painter, x, y, color, up=True)
        elif kind == "SHORT":
            color = QColor(C["red"])
            label = dt.strftime("S %H:%M")
            dy = S.p(26)
            self._draw_entry_marker(painter, x, y, color, up=False)
        else:
            pnl_pts = marker.get("pnl_pts")
            reason = str(marker.get("reason") or "")
            outcome = str(marker.get("outcome") or "EXIT")
            self._draw_exit_marker(painter, x, y, dt, outcome, pnl_pts, reason)
            return

        painter.setPen(color)
        text_rect = QRectF(x - S.p(28), y + dy, S.p(72), S.p(14))
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, label)

    def _resolve_marker_overlap(self, x: float, y: float, occupied, kind: str):
        min_dx = S.p(18)
        min_dy = S.p(18)
        vertical_step = S.p(16)
        horizontal_step = S.p(8)
        prefer_up = kind == "LONG"
        slot = 0

        while True:
            if slot == 0:
                cand_x, cand_y = x, y
            else:
                direction = -1 if prefer_up else 1
                cand_y = y + direction * vertical_step * slot
                cand_x = x + horizontal_step * slot

            overlapped = False
            for ox, oy in occupied:
                if abs(cand_x - ox) < min_dx and abs(cand_y - oy) < min_dy:
                    overlapped = True
                    break
            if not overlapped:
                occupied.append((cand_x, cand_y))
                return cand_x, cand_y
            slot += 1

    def _draw_entry_marker(self, painter: QPainter, x: float, y: float, color: QColor, up: bool):
        glow = QColor(color)
        glow.setAlpha(70)
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QRectF(x - 10.0, y - 10.0, 20.0, 20.0))

        painter.setBrush(QColor(15, 23, 32, 230))
        painter.setPen(QPen(color.lighter(130), 1.8))
        painter.drawRoundedRect(QRectF(x - 8.0, y - 8.0, 16.0, 16.0), 5, 5)

        painter.setPen(QPen(QColor("#F8FAFC"), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if up:
            painter.drawLine(QPointF(x, y + 4.8), QPointF(x, y - 2.0))
        else:
            painter.drawLine(QPointF(x, y - 4.8), QPointF(x, y + 2.0))

        painter.setBrush(color)
        painter.setPen(QPen(QColor("#F8FAFC"), 1.1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if up:
            poly = QPolygonF([
                QPointF(x, y - 6.2),
                QPointF(x - 5.0, y + 0.8),
                QPointF(x + 5.0, y + 0.8),
            ])
        else:
            poly = QPolygonF([
                QPointF(x, y + 6.2),
                QPointF(x - 5.0, y - 0.8),
                QPointF(x + 5.0, y - 0.8),
            ])
        painter.drawPolygon(poly)

    def _draw_exit_marker(
        self,
        painter: QPainter,
        x: float,
        y: float,
        dt: datetime,
        outcome: str,
        pnl_pts,
        reason: str,
    ):
        pnl_val = None if pnl_pts is None else float(pnl_pts)
        # 청산 시인성 개선: 아이콘 배지를 제거하고 텍스트 정보만 표시.
        # TP는 녹색, SL은 적색으로 통일해 한눈에 구분되도록 한다.
        if outcome == "WIN":
            col = QColor("#43C17A")
            marker_bg = QColor("#0F2F1F")
            marker_border = QColor("#6BE3A1")
            marker_glyph = "T"
            tag = "TP"
            sign = "+" if pnl_val is not None else ""
            pnl_text = f"{sign}{pnl_val:.2f}pt" if pnl_val is not None else "WIN"
            label = f"{tag} {pnl_text}  {dt.strftime('%H:%M')}"
            text_y = y - S.p(16)
        elif outcome == "LOSS":
            col = QColor("#E35D6A")
            marker_bg = QColor("#3B141A")
            marker_border = QColor("#FF8A98")
            marker_glyph = "S"
            tag = "SL"
            pnl_text = f"{pnl_val:.2f}pt" if pnl_val is not None else "LOSS"
            label = f"{tag} {pnl_text}  {dt.strftime('%H:%M')}"
            text_y = y + S.p(18)
        else:
            col = QColor("#8B949E")
            marker_bg = QColor("#1F2937")
            marker_border = QColor("#C0CAD5")
            marker_glyph = "P"
            tag = "PX"
            short_reason = reason[:4] if reason else "PART"
            label = f"{tag} {short_reason}  {dt.strftime('%H:%M')}"
            text_y = y - S.p(14)

        self._draw_exit_stamp(
            painter,
            x,
            y,
            marker_bg,
            marker_border,
            marker_glyph,
            col,
        )

        # 다크 배경에서 가독성을 높이기 위한 얇은 그림자 레이어
        painter.setPen(QColor(0, 0, 0, 170))
        painter.drawText(QPointF(x + S.p(19), text_y + 1), label)
        painter.setPen(col)
        painter.drawText(QPointF(x + S.p(18), text_y), label)

    def _draw_exit_stamp(
        self,
        painter: QPainter,
        x: float,
        y: float,
        bg: QColor,
        border: QColor,
        glyph: str,
        glow_col: QColor,
    ):
        glow = QColor(glow_col)
        glow.setAlpha(75)
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QRectF(x - 8.0, y - 8.0, 16.0, 16.0))

        painter.setBrush(bg)
        painter.setPen(QPen(border, 1.4))
        painter.drawRoundedRect(QRectF(x - 6.0, y - 6.0, 12.0, 12.0), 3, 3)

        painter.setPen(QColor("#F8FAFC"))
        painter.drawText(QRectF(x - 6.0, y - 6.0, 12.0, 12.0), Qt.AlignCenter, glyph)

    def _draw_diamond_badge(self, painter: QPainter, x: float, y: float, fill: QColor, stroke: QColor, glyph: str):
        glow = QColor(fill)
        glow.setAlpha(70)
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QRectF(x - 8.0, y - 8.0, 16.0, 16.0))

        poly = QPolygonF([
            QPointF(x, y - 5.5),
            QPointF(x + 5.5, y),
            QPointF(x, y + 5.5),
            QPointF(x - 5.5, y),
        ])
        painter.setBrush(fill)
        painter.setPen(QPen(stroke, 1.5))
        painter.drawPolygon(poly)
        painter.setPen(QColor("#F9FAFB"))
        painter.drawText(QRectF(x - 5, y - 6, 10, 12), Qt.AlignCenter, glyph)

    def _draw_cut_badge(self, painter: QPainter, x: float, y: float, fill: QColor, stroke: QColor):
        glow = QColor(stroke)
        glow.setAlpha(60)
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QRectF(x - 8.0, y - 8.0, 16.0, 16.0))

        painter.setBrush(fill)
        painter.setPen(QPen(stroke, 1.5))
        painter.drawRoundedRect(QRectF(x - 5.5, y - 5.5, 11.0, 11.0), 3, 3)
        painter.setPen(QPen(QColor("#F9FAFB"), 1.6))
        painter.drawLine(QPointF(x - 2.8, y - 2.8), QPointF(x + 2.8, y + 2.8))
        painter.drawLine(QPointF(x - 2.8, y + 2.8), QPointF(x + 2.8, y - 2.8))

    def _draw_partial_badge(self, painter: QPainter, x: float, y: float, fill: QColor, stroke: QColor):
        painter.setBrush(fill)
        painter.setPen(QPen(stroke, 1.5))
        painter.drawRoundedRect(QRectF(x - 5.5, y - 4.5, 11.0, 9.0), 3, 3)
        painter.setPen(QColor("#F9FAFB"))
        painter.drawText(QRectF(x - 5.5, y - 4.5, 11.0, 9.0), Qt.AlignCenter, "P")

    def _draw_label_chip(
        self,
        painter: QPainter,
        x: float,
        y: float,
        text: str,
        fill: QColor,
        stroke: QColor,
        upward: bool,
    ):
        metrics = painter.fontMetrics()
        width = max(S.p(84), metrics.horizontalAdvance(text) + S.p(12))
        height = S.p(18)
        rect = QRectF(x, y, width, height)

        bg = QColor(fill)
        bg.setAlpha(205)
        painter.setPen(QPen(stroke, 1.2))
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, 6, 6)

        painter.setPen(QColor("#F8FAFC"))
        painter.drawText(rect.adjusted(S.p(6), 0, -S.p(6), 0), Qt.AlignVCenter | Qt.AlignLeft, text)

        painter.setPen(QPen(stroke, 1.2))
        anchor_y = rect.bottom() if upward else rect.top()
        anchor_tip = anchor_y + (S.p(5) if upward else -S.p(5))
        painter.drawLine(QPointF(x, anchor_y), QPointF(x - S.p(5), anchor_tip))

    def _infer_exit_outcome(self, finalize: bool, pnl_pts, reason: str) -> str:
        if not finalize:
            return "PARTIAL"
        if pnl_pts is not None:
            pnl_val = float(pnl_pts)
            if pnl_val > 0:
                return "WIN"
            if pnl_val < 0:
                return "LOSS"
        reason_l = str(reason or "").lower()
        if "tp" in reason_l or "익절" in reason_l:
            return "WIN"
        if "stop" in reason_l or "손절" in reason_l:
            return "LOSS"
        return "EXIT"

    def _draw_crosshair_and_tooltip(self, painter: QPainter, plot: QRectF, candles, lo: float, hi: float):
        if self._hover_pos is None or not plot.contains(QPointF(self._hover_pos)):
            return
        if not candles:
            return

        count = len(candles)
        padded_count = max(count + self.RIGHT_PADDING_BARS, 1)
        step = plot.width() / padded_count
        candle_right = plot.left() + step * count
        if self._hover_pos.x() > candle_right:
            return
        idx = int((self._hover_pos.x() - plot.left()) / max(step, 1e-6))
        idx = max(0, min(idx, len(candles) - 1))
        candle = candles[idx]
        x = plot.left() + step * (idx + 0.5)
        price = hi - ((self._hover_pos.y() - plot.top()) / max(plot.height(), 1e-6)) * (hi - lo)
        y = self._price_to_y(price, plot, lo, hi)

        cross_col = QColor("#A0ACBB")
        cross_col.setAlpha(160)
        h_pen = QPen(cross_col)
        h_pen.setStyle(Qt.DashLine)
        h_pen.setWidthF(0.8)
        painter.setPen(h_pen)
        painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))
        painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))

        dt = self._coerce_dt(candle.get("ts"))
        tooltip_lines = [
            dt.strftime("%H:%M") if dt else str(candle.get("ts", "")),
            f"O {candle['open']:.2f}  H {candle['high']:.2f}",
            f"L {candle['low']:.2f}  C {candle['close']:.2f}",
            f"Y {price:.2f}",
        ]
        self._draw_hover_tooltip(painter, plot, QPointF(x, y), tooltip_lines)

    def _draw_hover_tooltip(self, painter: QPainter, plot: QRectF, anchor: QPointF, lines):
        metrics = painter.fontMetrics()
        width = max(metrics.horizontalAdvance(line) for line in lines) + S.p(14)
        line_h = metrics.height()
        height = len(lines) * line_h + S.p(10)
        x = anchor.x() + S.p(12)
        y = anchor.y() - height - S.p(8)

        if x + width > plot.right():
            x = anchor.x() - width - S.p(12)
        if y < plot.top():
            y = anchor.y() + S.p(8)

        rect = QRectF(x, y, width, height)
        painter.setPen(QPen(QColor("#AAB4C3"), 1))
        painter.setBrush(QColor(12, 17, 24, 228))
        painter.drawRoundedRect(rect, 6, 6)
        painter.setPen(QColor("#F8FAFC"))

        text_y = rect.top() + S.p(6) + metrics.ascent()
        for line in lines:
            painter.drawText(QPointF(rect.left() + S.p(7), text_y), line)
            text_y += line_h

    def _clamp_view_offset(self, offset: int, total_count: int, visible_count: int) -> int:
        max_offset = max(0, total_count - visible_count)
        return max(0, min(int(offset or 0), max_offset))

    def _draw_axes(self, painter: QPainter, plot: QRectF, candles, lo: float, hi: float, padded_count: int):
        del lo, hi
        painter.setPen(QColor(C["text2"]))
        count = len(candles)
        if count == 0:
            return
        step = plot.width() / max(padded_count, 1)
        stride = max(1, count // 8)
        for idx, candle in enumerate(candles):
            if idx % stride != 0 and idx != count - 1:
                continue
            dt = self._coerce_dt(candle["ts"])
            if not dt:
                continue
            x = plot.left() + step * (idx + 0.5)
            text = dt.strftime("%H:%M")
            painter.drawText(QRectF(x - 24, plot.bottom() + 6, 48, 18), Qt.AlignHCenter | Qt.AlignTop, text)

    def _normalize_candle(self, candle):
        if not candle:
            return None
        try:
            dt = self._coerce_dt(candle.get("ts"))
            if dt is None:
                return None
            return {
                "ts": dt.replace(second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S"),
                "open": float(candle.get("open") or 0.0),
                "high": float(candle.get("high") or 0.0),
                "low": float(candle.get("low") or 0.0),
                "close": float(candle.get("close") or 0.0),
                "volume": int(candle.get("volume") or 0),
            }
        except Exception:
            return None

    def _coerce_dt(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        text = str(value).strip()
        if not text:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def _resolve_index(self, index_map, candles, dt):
        if dt is None:
            return None
        key = dt.replace(second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
        if key in index_map:
            return index_map[key]
        if not candles:
            return None
        if key < candles[0]["ts"]:
            return 0
        # Anchor markers to the nearest closed minute at-or-before the trade
        # timestamp instead of drifting to the latest candle when the exact
        # minute key is absent from the visible series.
        for idx in range(len(candles) - 1, -1, -1):
            if candles[idx]["ts"] <= key:
                return idx
        return 0

    def _price_to_y(self, price: float, plot: QRectF, lo: float, hi: float) -> float:
        ratio = 0.5 if hi <= lo else (price - lo) / (hi - lo)
        ratio = min(max(ratio, 0.0), 1.0)
        return plot.bottom() - (plot.height() * ratio)


class MinuteChartDialog(QDialog):
    SHORTCUT_TEXT = "Ctrl+Shift+X"
    # 배경 스레드 → 메인 스레드 안전 전달용 시그널
    # threading.Thread에서 QTimer.singleShot 람다는 Python 3.7 32-bit에서
    # 타이머가 이벤트 루프 없는 스레드에 귀속되어 발동하지 않는다.
    # pyqtSignal은 cross-thread 시 Qt::QueuedConnection으로 자동 처리된다.
    _sig_reload_done = pyqtSignal(list, list, list)  # candles, completed_trades, exit_markers

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle(f"당일 1분봉 차트 ({self.SHORTCUT_TEXT})")
        self.resize(S.p(1180), S.p(700))
        self._session_date = datetime.now().date().isoformat()

        self._chart = MinuteChartCanvas(self)
        self._status = QLabel(
            f"{self.SHORTCUT_TEXT}  |  휠 줌  |  진입 ▲/▼  |  익절 G  |  손절 X  |  부분청산 P"
        )
        self._status.setStyleSheet(f"color:{C['text2']};font-size:{S.f(10)}px;")
        self._status.setText(
            f"{self.SHORTCUT_TEXT}  |  휠 줌  |  드래그 이동  |  더블클릭 전체보기  |  크로스헤어"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(S.p(12), S.p(12), S.p(12), S.p(12))
        root.setSpacing(S.p(8))
        root.addWidget(self._status)
        root.addWidget(self._chart, 1)

        self._toggle_shortcut = QShortcut(QKeySequence(self.SHORTCUT_TEXT), self)
        self._toggle_shortcut.activated.connect(self.close)

        # 배경 스레드 → 메인 스레드 전달: 시그널 연결
        self._sig_reload_done.connect(self._apply_reload_result)

        # 리로드 완료 후 호출될 외부 콜백 (active position 재동기화 등)
        # main.py에서 set_minute_chart_post_reload_hook()으로 주입
        self._post_reload_hook = None

        # Qt 이벤트 루프 진입 후 첫 틱에 백그라운드 로드 시작
        # (이벤트 루프 이전에 스레드를 시작하면 QTimer.singleShot 람다가
        #  Python 3.7 32-bit에서 레퍼런스 카운팅 오류로 크래시)
        QTimer.singleShot(0, self._start_reload_thread)

    @staticmethod
    def _trim_to_last_price_group(candles: list, threshold: float = 0.04) -> list:
        """연속된 최신 가격 그룹만 반환.

        종목 전환(예: A0666 → A0565) 시 이전 종목 캔들을 제거.
        연속 봉 간 close→open 가격 차이가 threshold(4%) 초과 시 그 이전 데이터 버림.
        """
        if len(candles) < 2:
            return candles
        for i in range(len(candles) - 1, 0, -1):
            prev_close = float(candles[i - 1].get("close") or 0)
            cur_open = float(candles[i].get("open") or 0)
            if prev_close > 0 and cur_open > 0:
                if abs(cur_open - prev_close) / prev_close > threshold:
                    return candles[i:]
        return candles

    @staticmethod
    def _is_partial_exit_reason(exit_reason: str) -> bool:
        """부분 청산 여부를 exit_reason 텍스트로 판단."""
        _r = str(exit_reason or "").lower()
        if not _r:
            return False
        return any(kw in _r for kw in ("부분청산", "partial", "부분 익절"))

    def reload_today(self):
        self._session_date = datetime.now().date().isoformat()
        candle_rows = fetchall(
            RAW_DATA_DB,
            """SELECT ts, open, high, low, close, volume
               FROM raw_candles
               WHERE ts LIKE ?
               ORDER BY ts ASC""",
            (f"{self._session_date}%",),
        )
        candles = self._trim_to_last_price_group([dict(row) for row in candle_rows])

        completed_trades = []
        exit_markers = []
        for row in fetch_today_trades(self._session_date):
            entry_ts = self._coerce_dt(row["entry_ts"])
            exit_ts = self._coerce_dt(row["exit_ts"])
            if not entry_ts or not exit_ts:
                continue
            is_partial = self._is_partial_exit_reason(row["exit_reason"])

            if is_partial:
                exit_markers.append({
                    "price": float(row["exit_price"] or 0.0),
                    "ts": exit_ts,
                    "kind": "EXIT",
                    "finalize": False,
                    "pnl_pts": float(row["pnl_pts"] or 0.0),
                    "reason": str(row["exit_reason"] or ""),
                    "direction": str(row["direction"] or "").upper(),
                    "outcome": "PARTIAL",
                })
            else:
                completed_trades.append({
                    "direction": str(row["direction"] or "").upper(),
                    "entry_price": float(row["entry_price"] or 0.0),
                    "exit_price": float(row["exit_price"] or 0.0),
                    "entry_ts": entry_ts,
                    "exit_ts": exit_ts,
                    "exit_reason": str(row["exit_reason"] or ""),
                    "pnl_pts": float(row["pnl_pts"] or 0.0),
                    "outcome": self._chart._infer_exit_outcome(True, row["pnl_pts"], row["exit_reason"]),
                })
        self._chart.reset_session(candles, completed_trades, exit_markers=exit_markers)
        # 재시작 복원: 오늘 레짐·방향예측 히스토리를 _regime_map / _dir_map에 채움
        try:
            regime_map = fetch_regime_today(self._session_date)
            if regime_map:
                self._chart._regime_map.update(regime_map)
        except Exception:
            pass
        try:
            dir_map = fetch_direction_today(self._session_date)
            if dir_map:
                self._chart._dir_map.update(dir_map)
        except Exception:
            pass
        self._chart.update()

    def _start_reload_thread(self):
        import threading as _thr
        if getattr(self, '_reload_running', False):
            logger.debug("[ChartDBG] _start_reload_thread: 이미 실행 중 — 중복 방지")
            return
        self._reload_running = True
        def _run():
            try:
                self._reload_today_bg()
            finally:
                self._reload_running = False
        _thr.Thread(target=_run, daemon=True).start()

    def maybe_roll_session(self):
        today = datetime.now().date().isoformat()
        if today != self._session_date:
            self._start_reload_thread()

    def _reload_today_bg(self):
        """reload_today를 백그라운드 스레드에서 실행 후 _sig_reload_done 시그널로 메인 스레드에 전달."""
        import time as _t
        _t0 = _t.monotonic()
        try:
            self._session_date = datetime.now().date().isoformat()

            _t1 = _t.monotonic()
            candle_rows = fetchall(
                RAW_DATA_DB,
                "SELECT ts, open, high, low, close, volume FROM raw_candles WHERE ts LIKE ? ORDER BY ts ASC",
                (f"{self._session_date}%",),
            )
            _t2 = _t.monotonic()
            candles = self._trim_to_last_price_group([dict(row) for row in candle_rows])

            completed_trades, exit_markers = [], []
            _t3 = _t.monotonic()
            for row in fetch_today_trades(self._session_date):
                entry_ts = self._coerce_dt(row["entry_ts"])
                exit_ts = self._coerce_dt(row["exit_ts"])
                if not entry_ts or not exit_ts:
                    continue
                is_partial = self._is_partial_exit_reason(row["exit_reason"])
                if is_partial:
                    exit_markers.append({"price": float(row["exit_price"] or 0.0), "ts": exit_ts,
                                         "kind": "EXIT", "finalize": False,
                                         "pnl_pts": float(row["pnl_pts"] or 0.0),
                                         "reason": str(row["exit_reason"] or ""),
                                         "direction": str(row["direction"] or "").upper(), "outcome": "PARTIAL"})
                else:
                    completed_trades.append({"direction": str(row["direction"] or "").upper(),
                                             "entry_price": float(row["entry_price"] or 0.0),
                                             "exit_price": float(row["exit_price"] or 0.0),
                                             "entry_ts": entry_ts, "exit_ts": exit_ts,
                                             "exit_reason": str(row["exit_reason"] or ""),
                                             "pnl_pts": float(row["pnl_pts"] or 0.0),
                                             "outcome": self._chart._infer_exit_outcome(True, row["pnl_pts"], row["exit_reason"])})
            _t4 = _t.monotonic()
            _total_ms = (_t4 - _t0) * 1000
            _candle_ms = (_t2 - _t1) * 1000
            _trade_ms  = (_t4 - _t3) * 1000
            logger.debug(
                "[ChartDBG] _reload_today_bg 완료 | total=%.1fms "
                "raw_candles=%.1fms(%d봉) trades=%.1fms(%d건)",
                _total_ms, _candle_ms, len(candles), _trade_ms, len(completed_trades),
            )
            if _total_ms > 3000:
                logger.warning(
                    "[ChartDBG] _reload_today_bg 과도 지연 %.1fms "
                    "— DB 락 경합 가능 (raw_candles=%.1fms trades=%.1fms)",
                    _total_ms, _candle_ms, _trade_ms,
                )
            # 메인 스레드로 결과 전달 — pyqtSignal(QueuedConnection) 사용
            # QTimer.singleShot(lambda)는 threading.Thread에서 발동하지 않음 (Python 3.7 32-bit)
            self._sig_reload_done.emit(candles, completed_trades, exit_markers)
        except Exception as _e:
            logger.warning("[ChartDBG] _reload_today_bg 예외: %s", _e)

    def _apply_reload_result(self, candles, completed_trades, exit_markers):
        """메인 스레드에서 reset_session + regime_map 복원 + active position 재동기화를 원자적으로 처리."""
        self._chart.reset_session(candles, completed_trades, exit_markers=exit_markers)
        try:
            regime_map = fetch_regime_today(self._session_date)
            if regime_map:
                self._chart._regime_map.update(regime_map)
        except Exception as _e:
            logger.debug("[ChartDBG] _apply_reload_result regime 복원 실패: %s", _e)
        try:
            dir_map = fetch_direction_today(self._session_date)
            if dir_map:
                self._chart._dir_map.update(dir_map)
        except Exception as _e:
            logger.debug("[ChartDBG] _apply_reload_result direction 복원 실패: %s", _e)
        self._chart.update()
        # reset_session이 _active_trade를 초기화하므로, 외부 훅으로 재동기화
        if callable(getattr(self, '_post_reload_hook', None)):
            try:
                self._post_reload_hook()
            except Exception as _he:
                logger.debug("[ChartDBG] _apply_reload_result hook 예외: %s", _he)

    def update_tick(self, price: float, ts=None):
        # maybe_roll_session 제거: 매 틱마다 날짜 비교 불필요 — on_candle_closed에서만 체크 (194차)
        self._chart.update_tick(price, ts=ts)

    def on_candle_closed(self, candle: dict):
        self.maybe_roll_session()
        self._chart.on_candle_closed(candle)

    def set_regime_at(self, ts_key: str, regime: str):
        """파이프라인 완료 후 봉 레짐 색상 업데이트."""
        self._chart.set_regime_at(ts_key, regime)

    def set_direction_at(self, ts_key: str, direction: int):
        """파이프라인 완료 후 봉 방향예측 색상 업데이트."""
        self._chart.set_direction_at(ts_key, direction)

    def record_entry(self, direction: str, price: float, ts=None):
        self.maybe_roll_session()
        self._chart.record_entry(direction, price, ts=ts)

    def record_exit(
        self,
        price: float,
        ts=None,
        finalize: bool = True,
        pnl_pts: float = None,
        reason: str = "",
        direction: str = "",
    ):
        self.maybe_roll_session()
        self._chart.record_exit(
            price,
            ts=ts,
            finalize=finalize,
            pnl_pts=pnl_pts,
            reason=reason,
            direction=direction,
        )

    def sync_active_position(self, direction: str, price: float, ts=None):
        self.maybe_roll_session()
        self._chart.sync_active_trade(direction, price, ts=ts)

    def clear_active_position(self):
        self._chart.clear_active_trade()

    def _coerce_dt(self, value):
        return self._chart._coerce_dt(value)

    def closeEvent(self, event):
        import time as _t
        _t0 = _t.monotonic()
        try:
            geo = self.geometry()
            logger.debug(
                "[ChartDBG] closeEvent 시작 | size=%dx%d pos=(%d,%d) "
                "paint_slow=%d/%d",
                geo.width(), geo.height(), geo.x(), geo.y(),
                self._chart._dbg_paint_slow_count, self._chart._dbg_paint_count,
            )
            # ── geometry 저장 스킵 조건 ──────────────────────────────
            # ① Qt maximize 상태 (setGeometry로는 복원 불가)
            if self.isMaximized():
                logger.debug("[ChartDBG] closeEvent isMaximized → 저장 스킵")
                super().closeEvent(event)
                return
            scr = QApplication.screenAt(geo.center()) or QApplication.primaryScreen()
            avail = scr.availableGeometry()
            # ② 화면 크기 초과 — 모니터 분리·DPI 변경 등으로 geometry가 화면 밖인 경우만 스킵
            #    (이전 90% 체크 제거: screenAt이 잘못된 화면 반환 시 오탐 + 사용자 의도 대형창 차단)
            if geo.width() > avail.width() or geo.height() > avail.height():
                logger.warning(
                    "[ChartDBG] closeEvent geometry 초과 — 저장 스킵 "
                    "size=%dx%d avail=%dx%d",
                    geo.width(), geo.height(), avail.width(), avail.height(),
                )
                super().closeEvent(event)
                return
            prefs = {}
            if os.path.exists(_UI_PREFS_FILE):
                try:
                    with open(_UI_PREFS_FILE, "r", encoding="utf-8") as _rf:
                        prefs = json.load(_rf)
                except Exception:
                    prefs = {}
            prefs["chart_dialog_geometry"] = {
                "x": geo.x(), "y": geo.y(),
                "w": min(geo.width(),  _CHART_MAX_LOGICAL_W),
                "h": min(geo.height(), _CHART_MAX_LOGICAL_H),
            }
            with open(_UI_PREFS_FILE, "w", encoding="utf-8") as _wf:
                json.dump(prefs, _wf, ensure_ascii=False)
            _io_ms = (_t.monotonic() - _t0) * 1000
            if _io_ms > 100:
                logger.warning("[ChartDBG] closeEvent I/O slow %.1fms", _io_ms)
        except Exception as _e:
            logger.warning("[ChartDBG] closeEvent 예외: %s", _e)
        _pre_super_ms = (_t.monotonic() - _t0) * 1000
        super().closeEvent(event)
        _total_ms = (_t.monotonic() - _t0) * 1000
        logger.debug(
            "[ChartDBG] closeEvent 완료 | pre_super=%.1fms total=%.1fms",
            _pre_super_ms, _total_ms,
        )
        if _total_ms > 500:
            logger.warning(
                "[ChartDBG] closeEvent 과도 지연 %.1fms — super().closeEvent 블로킹",
                _total_ms,
            )

    def _center_on_second_screen(self):
        """제2모니터 중앙에 최적 크기로 배치. 모니터 1대면 주모니터 중앙."""
        primary = QApplication.primaryScreen()
        non_primary = [s for s in QApplication.screens() if s is not primary]
        screen = non_primary[0] if non_primary else primary
        sg = screen.availableGeometry()
        w = max(900, min(round(sg.width()  * 0.82), 1680))
        h = max(600, min(round(sg.height() * 0.85),  980))
        x = sg.x() + (sg.width()  - w) // 2
        y = sg.y() + (sg.height() - h) // 2
        # y < 0 방지: 보조 모니터가 주모니터 위에 배치된 경우 y가 음수가 될 수 있음
        # 음수 y → Windows가 content+frame이 화면 밖으로 나갔다고 판단
        # → "Unable to set geometry" → DPI 1.5× 강제 확대 (log: 3030→4547)
        y = max(y, 0)
        self.setGeometry(x, y, w, h)
        logger.debug(
            "[ChartDBG] _center_on_second_screen: %dx%d pos=(%d,%d) screen=%s",
            w, h, x, y, screen.name(),
        )

    def restore_saved_geometry(self):
        try:
            geo = None
            if os.path.exists(_UI_PREFS_FILE):
                try:
                    with open(_UI_PREFS_FILE, "r", encoding="utf-8") as _rf:
                        geo = json.load(_rf).get("chart_dialog_geometry")
                except Exception:
                    pass

            if not geo:
                # 저장된 위치 없음 → 제2모니터 중앙 초기 배치
                logger.debug("[ChartDBG] restore_saved_geometry: 저장값 없음 → 제2모니터 중앙")
                self._center_on_second_screen()
                return

            x, y = int(geo["x"]), int(geo["y"])
            w, h = int(geo["w"]), int(geo["h"])

            # 32-bit GDI 보호: 초대형 DIB 방지
            # DPI 150% 환경에서 w×h 논리픽셀 → 물리픽셀 1.5×가 발생,
            # 가상주소 단편화 후 setGeometry로 CreateDIBSection FAILED → crash 방지
            if w > _CHART_MAX_LOGICAL_W or h > _CHART_MAX_LOGICAL_H:
                logger.warning(
                    "[ChartDBG] restore_saved_geometry: 32-bit GDI 상한 초과 "
                    "%dx%d → %dx%d (DPI 스케일 후 물리 DIB 과대 방지)",
                    w, h, min(w, _CHART_MAX_LOGICAL_W), min(h, _CHART_MAX_LOGICAL_H),
                )
                w = min(w, _CHART_MAX_LOGICAL_W)
                h = min(h, _CHART_MAX_LOGICAL_H)

            # 팝업 중심점 기준으로 해당 화면을 탐색
            from PyQt5.QtCore import QPoint
            _cx, _cy = x + w // 2, y + h // 2
            target_screen = QApplication.screenAt(QPoint(_cx, _cy))
            if target_screen is None:
                # 저장된 좌표가 현재 연결된 어떤 화면에도 속하지 않음
                # (모니터 분리·DPI 변경·저장값 오염 등) → 제2모니터 중앙 재배치
                logger.warning(
                    "[ChartDBG] restore_saved_geometry: 저장 화면 없음 "
                    "center=(%d,%d) → 제2모니터 중앙", _cx, _cy,
                )
                self._center_on_second_screen()
                return

            avail = target_screen.availableGeometry()
            orig_w, orig_h = w, h
            # 90% 크기 threshold 제거 — 사용자가 의도적으로 대형 창을 사용하는 경우 허용
            # paintEvent guard를 6000×4000으로 상향해 대형 창에서도 차트가 정상 렌더링됨
            # 위치가 화면 밖으로 나가지 않도록 클램핑
            x = max(avail.left(), min(x, avail.right()  - w))
            y = max(avail.top(),  min(y, avail.bottom() - h))
            # ── 음수 y 방지 (DPI 확대 트리거 차단) ──────────────────────
            # 로그: "Unable to set geometry 3030x1460+3369-8 → Resulting 4547x2124+3372+6"
            # 보조 모니터 avail.top()=-7일 때 content y=-7(=avail.top()) → Qt 프레임 계산 중
            # 1px 감소 → content y=-8 → avail.top()=-7 밖으로 나감 → Windows가 DPI 1.5×
            # 강제 적용 (Python 3.7 32-bit System-DPI-Aware + 보조모니터 150% DPI 조합)
            # y를 0 이상으로 보정하면 content+frame이 항상 가상 데스크탑 양수 영역에 배치됨
            if y < 0:
                logger.warning(
                    "[ChartDBG] restore_saved_geometry: y=%d < 0 → y=0으로 보정 "
                    "(음수 y → Windows DPI 1.5× 확대 방지)", y,
                )
                y = 0
            # 클램핑 후 실제 화면 내에 창이 충분히 들어오는지 최종 확인
            if (x + w > avail.right() + 10 or y + h > avail.bottom() + 10
                    or x < avail.left() - 10 or y < avail.top() - 10):
                logger.warning(
                    "[ChartDBG] restore_saved_geometry 범위 초과 → 제2모니터 중앙 "
                    "pos=(%d,%d) size=%dx%d avail=%s",
                    x, y, w, h, avail,
                )
                self._center_on_second_screen()
                return
            if orig_w != w or orig_h != h:
                logger.warning(
                    "[ChartDBG] restore_saved_geometry 클램핑: %dx%d → %dx%d "
                    "(avail=%dx%d)",
                    orig_w, orig_h, w, h, avail.width(), avail.height(),
                )
            else:
                logger.debug(
                    "[ChartDBG] restore_saved_geometry: %dx%d pos=(%d,%d)",
                    w, h, x, y,
                )
            self.setGeometry(x, y, w, h)
        except Exception as _e:
            logger.warning("[ChartDBG] restore_saved_geometry 예외: %s", _e)


import datetime as _dt


def _nth_thursday(year, month, n):
    """해당 월 n번째 목요일 날짜 반환. n=2 → 두 번째 목요일(선물 만기일)."""
    first = _dt.date(year, month, 1)
    days_to_thu = (3 - first.weekday()) % 7  # Monday=0 … Thursday=3
    return first + _dt.timedelta(days=days_to_thu + (n - 1) * 7)


def _next_valid_contracts(today, quarterly_months=None, n=2):
    """today 기준 만기가 지나지 않은 계약월 n개를 [(year, month), ...] 로 반환.

    quarterly_months: frozenset({3,6,9,12}) → 분기물,  None → 월물(모든 월).
    만기일(2nd Thursday) >= today 인 계약만 포함한다.
    """
    result = []
    year, month = today.year, today.month
    for _ in range(36):  # 최대 3년 스캔
        if quarterly_months is None or month in quarterly_months:
            expiry = _nth_thursday(year, month, 2)
            if expiry >= today:
                result.append((year, month))
                if len(result) >= n:
                    break
        month += 1
        if month > 12:
            month = 1
            year += 1
    return result


def _futures_code8(prefix, year, month):
    """8자리 Cybos 코드: prefix + 연도끝자리 + 월hex대문자 + 000.

    예) prefix='A01', year=2026, month=6  → 'A0166000'
        prefix='A05', year=2026, month=12 → 'A056C000'
    """
    return "{0}{1}{2:X}000".format(prefix, str(year)[-1], month)


_SYMBOL_TAGS = ["근월", "차월", "원월1", "원월2"]


def _build_market_symbols():
    """기동 날짜 기준으로 근월·차월 종목코드 목록을 동적으로 생성한다.

    - KOSPI200 선물:     분기물 (3·6·9·12월), 두 번째 목요일 만기
    - KOSPI200 미니선물: 월물 (모든 월),       두 번째 목요일 만기

    반환 예시 (2026-05-15 기준):
        "KOSPI200 선물":     ["A0166000  F 202606  (근월)", "A0169000  F 202609  (차월)"]
        "KOSPI200 미니선물": ["A0566000  미니 F 202606  (근월)", "A0567000  미니 F 202607  (차월)"]
    """
    today = _dt.date.today()

    normal_contracts = _next_valid_contracts(
        today, quarterly_months=frozenset([3, 6, 9, 12]), n=2
    )
    normal_symbols = []
    for i, (y, m) in enumerate(normal_contracts):
        code = _futures_code8("A01", y, m)
        tag = _SYMBOL_TAGS[i] if i < len(_SYMBOL_TAGS) else "원월"
        normal_symbols.append(
            "{code}  F {y:04d}{m:02d}  ({tag})".format(code=code, y=y, m=m, tag=tag)
        )

    mini_contracts = _next_valid_contracts(today, quarterly_months=None, n=2)
    mini_symbols = []
    for i, (y, m) in enumerate(mini_contracts):
        code = _futures_code8("A05", y, m)
        tag = _SYMBOL_TAGS[i] if i < len(_SYMBOL_TAGS) else "원월"
        mini_symbols.append(
            "{code}  미니 F {y:04d}{m:02d}  ({tag})".format(code=code, y=y, m=m, tag=tag)
        )

    return {
        "KOSPI200 선물": normal_symbols,
        "KOSPI200 미니선물": mini_symbols,
    }


_MARKET_SYMBOLS = _build_market_symbols()

_UI_PREFS_FILE = os.path.join(DATA_DIR, "ui_prefs.json")

# 32-bit GDI 보호: 논리 픽셀 최대 크기 상한
# DPI 150% 환경: 물리 DIB = 2880×1590×4 ≈ 18 MB → 단편화 후에도 alloc 안전
# 배경: w=3030, h=1460 저장값이 DPI 150% 스케일로 4547×2124×4=38.6 MB 요구
#   → 3시간+ 운용 후 32-bit 가상주소 단편화로 CreateDIBSection FAILED → crash
_CHART_MAX_LOGICAL_W = 1920
_CHART_MAX_LOGICAL_H = 1060


def _extract_symbol_code(symbol_text: str) -> str:
    text = str(symbol_text or "").strip()
    parts = text.split(None, 1)
    return parts[0] if parts else ""


def _normalize_code_5(code: str) -> str:
    """8자리(A0567000) → 5자리(A0567) 정규화. 이미 5자리면 그대로."""
    c = str(code or "").strip()
    if len(c) == 8 and c.endswith("000"):
        return c[:-3]
    return c


def _find_symbol_text(market: str, *, symbol_code: str = "", symbol_text: str = "") -> str:
    symbols = _MARKET_SYMBOLS.get(market, [])
    normalized_code = str(symbol_code or "").strip()
    normalized_text = str(symbol_text or "").strip()

    if normalized_code:
        for item in symbols:
            if _extract_symbol_code(item) == normalized_code:
                return item

    if normalized_text and normalized_text in symbols:
        return normalized_text

    return symbols[0] if symbols else ""


class MireukDashboard(QMainWindow):
    """미륵이 v8.0 풀 대시보드"""

    sig_code_change_restart_requested = pyqtSignal()  # [234차] 종목변경 재시작 요청

    def __init__(self, kiwoom=None):
        super().__init__()
        self.kiwoom    = kiwoom
        self._start_dt = datetime.now()        # 프로그램 시작 시각 (불변)
        self._active_futures_code: str = ""    # [234차] 기동 시 확정된 종목코드
        # ── 해상도 감지 (UI 빌드 전에 반드시 먼저) ──────────────
        S.init()
        self.setWindowTitle("미륵이 v8.0  |  KOSPI 200 선물 예측 시스템")
        # WindowStaysOnTopHint 해제 — 일반 창으로 동작
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

        # ── Phase 3 알림 배지 깜박임 (800ms) ─────────────────────
        self._phase3_blink_timer = QTimer(self)
        self._phase3_blink_timer.setInterval(800)
        self._phase3_blink_timer.timeout.connect(self._blink_phase3)
        self._phase3_blink_timer.start()

        self._minute_chart_dialog = MinuteChartDialog(self)
        self._minute_chart_shortcut = QShortcut(QKeySequence(MinuteChartDialog.SHORTCUT_TEXT), self)
        self._minute_chart_shortcut.activated.connect(self.toggle_minute_chart_dialog)
        self._balance_refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        self._balance_refresh_shortcut.activated.connect(
            self.account_info_panel.sig_balance_refresh_requested.emit
        )

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(6)

        # ── 상단 헤더 ──────────────────────────────────────────
        header = QHBoxLayout()
        title = mk_label("⚡ 미륵이  v8.0", C['text'], 16, True)
        title_box = QVBoxLayout()
        title_box.setContentsMargins(0, 0, 0, 0)
        title_box.setSpacing(S.p(4))

        # ── 실시간 현재가 (키움 API 연동 핵심) ──────────────────
        self.lbl_realtime_price = mk_label("——.——", C['cyan'], 22, True)
        self.lbl_price_change   = mk_label("——", C['text2'], 14, True)
        _sym0 = _MARKET_SYMBOLS.get("KOSPI200 선물", [""])[0]
        _code0 = _sym0.split(None, 1)[1] if _sym0 else "——"
        self.lbl_futures_code   = mk_label(_code0, C['text2'], 11)

        price_box = QHBoxLayout()
        price_box.setSpacing(S.p(6))
        price_box.addWidget(self.lbl_futures_code)
        price_box.addWidget(self.lbl_realtime_price)
        price_box.addWidget(self.lbl_price_change)

        # 상태 배지
        # 거래소 CB 상태 배지 — lbl_regime 왼쪽에 위치
        # 정상 시에는 숨김, CB 발동/관망 시에만 표시
        self.lbl_ecb = QLabel("KRX CB\n⏸ --:--")
        self.lbl_ecb.setAlignment(Qt.AlignCenter)
        self.lbl_ecb.setStyleSheet(
            f"background:#7a0000;color:#fff;"
            f"border:2px solid #FF5252;"
            f"border-radius:{S.p(3)}px;"
            f"font-size:{S.f(10)}px;font-weight:bold;"
            f"padding:{S.p(1)}px {S.p(4)}px;"
        )
        self.lbl_ecb.setToolTip(
            "거래소 서킷브레이커 상태\n"
            "  KRX CB ⏸  : 거래소 CB 발동 — 거래 중단 중\n"
            "  관망 중    : CB 해제 후 관망 구간 (신규 진입 차단)\n"
            "  (숨김)     : 정상 거래 중"
        )
        self.lbl_ecb.setVisible(False)

        self.lbl_regime       = mk_badge("NEUTRAL", C['orange'], "#fff", 11)
        self.lbl_regime.setToolTip(
            "매크로 레짐 — 08:55 장전 1회 수집, 당일 고정\n"
            "  RISK_ON  : 위험선호 · 공격적 진입 가능\n"
            "  NEUTRAL  : 중립 · 기본 전략 유지\n"
            "  RISK_OFF : 위험회피 · 보수적 운용"
        )
        self.lbl_micro_regime = mk_badge("혼합",    C['blue'],   "#fff", 11)
        self.lbl_micro_regime.setToolTip(
            "미시 레짐 — 1분봉 기반 단기 시장 구조\n"
            "  추세장 : 방향성 뚜렷 · 모멘텀 전략 유리\n"
            "  횡보장 : 박스권 · 역추세 전략 유리\n"
            "  변동장 : ATR 급등 · 포지션 축소\n"
            "  혼합   : 구조 불명확 · 관망"
        )
        self._micro_warmup_wrap = QWidget()
        self._micro_warmup_wrap.setVisible(False)
        _mw_lay = QVBoxLayout(self._micro_warmup_wrap)
        _mw_lay.setContentsMargins(0, 0, 0, 0)
        _mw_lay.setSpacing(1)
        self.lbl_micro_warmup = mk_label("", C['text2'], 8)
        self.lbl_micro_warmup.setAlignment(Qt.AlignCenter)
        self.pb_micro_warmup = QProgressBar()
        self.pb_micro_warmup.setRange(0, 100)
        self.pb_micro_warmup.setValue(0)
        self.pb_micro_warmup.setTextVisible(False)
        self.pb_micro_warmup.setFixedHeight(max(4, S.p(5)))
        self.pb_micro_warmup.setFixedWidth(S.p(84))
        self.pb_micro_warmup.setStyleSheet(
            f"QProgressBar{{background:{C['bg3']};border:none;border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{C['orange']};border-radius:2px;}}"
        )
        _mw_lay.addWidget(self.lbl_micro_warmup)
        _mw_lay.addWidget(self.pb_micro_warmup)
        self._micro_box = QWidget()
        _mb_lay = QVBoxLayout(self._micro_box)
        _mb_lay.setContentsMargins(0, 0, 0, 0)
        _mb_lay.setSpacing(1)
        _mb_lay.addWidget(self.lbl_micro_regime, 0, Qt.AlignCenter)
        _mb_lay.addWidget(self._micro_warmup_wrap, 0, Qt.AlignCenter)
        _cyc_text, _cyc_col = _calc_cycle_badge()
        self.lbl_cycle  = mk_badge(_cyc_text, _cyc_col, "#fff", 11)
        self.lbl_cycle.setToolTip(
            "옵션 만기 카운트다운 (가장 가까운 만기 기준)\n"
            "  [월]위클리 : 매주 월요일 만기\n"
            "  [목]위클리 : 매주 목요일 만기\n"
            "  [목]월간   : 매월 두 번째 목요일 만기\n"
            "  D-0~D-2 : 만기 근접 → 감마·핀리스크 주의"
        )
        self.lbl_gamma  = mk_badge("감마 —", C['bg3'], C['text2'], 11)
        self.lbl_gamma.setToolTip(
            "옵션 감마 포지션 — 마켓메이커 헷지 방향 추정\n"
            "  감마스퀴즈 : MM 숏감마 · 추세 가속 구간 (GEX < -1B)\n"
            "  감마플립   : GEX 중립선 근접 · 방향 전환 주의 (|GEX| < 1B)\n"
            "  중립       : MM 감마롱 · 변동성 억제 (GEX > +1B)\n"
            "  감마 —     : 옵션 체인 미수집 (5분 갱신)"
        )
        self.lbl_pos    = mk_badge("FLAT", C['text2'], "#fff", 11)
        self.lbl_pos.setToolTip(
            "현재 포지션\n"
            "  LONG  : 매수 보유 중\n"
            "  SHORT : 매도 보유 중\n"
            "  FLAT  : 미보유 (현금)\n"
            "  15:10 강제 청산 후 FLAT 복귀"
        )
        self.lbl_cb = mk_badge("CB NORMAL", C['bg3'], C['text2'], 11)
        self.lbl_cb.setToolTip(_CB_TIP)
        
        # L2 영구중단 배지
        self.lbl_l2_halt = mk_badge("L2 —", C['bg3'], C['text2'], 10)
        self.lbl_l2_halt.setToolTip(
            "L2 Tier Gate — 수익 구간 도달 시 금일 거래 영구 중단\n"
            "  L2 —   : 정상 (중단 임계 미달)\n"
            "  L2 중단 : Tier 4 (누적 +400만원↑) 도달 → 당일 진입 전면 차단\n"
            "  매분 파이프라인마다 ProfitGuard 상태 확인"
        )
        self.lbl_l2_halt.setMinimumWidth(80)  # 크기 고정으로 항상 보임
        self.lbl_l2_halt.setAlignment(Qt.AlignCenter)

        # ── SHS / EKS 배지 ───────────────────────────────────────
        self.lbl_shs = mk_badge("SHS ——", C['bg3'], C['text2'], 11)
        self.lbl_shs.setMinimumWidth(S.p(90))
        self.lbl_shs.setAlignment(Qt.AlignCenter)
        self.lbl_shs.setToolTip(
            "시스템 건강 점수 (SHS: 0~100)\n"
            "  ≥ 80  : 정상 (녹색)\n"
            "  60~79 : 주의 (파랑)\n"
            "  < 60  : 진입 차단 (주황)\n"
            "  EKS   : 일시 관망 (자동 재개 대기) (빨강)\n\n"
            "감점 요소:\n"
            "  재시작 1회 = -8점 (최대 -40)\n"
            "  z경고 피처 1개 = -2.5점 (최대 -25)\n"
            "  CORE 탈락률 × -25점\n"
            "  S2 초과 지연 × -5점 (최대 -10)\n\n"
            "Early Kill Switch (09:05 판정):\n"
            "  GAP_OPEN conf < 45% + CORE 0% → 일시 관망\n"
            "  09:20부터 30분 간격 자동 회복 평가 (마감 11:30)"
        )

        # ── ShadowSession 배지 ───────────────────────────────────
        _ss_tip = (
            "Shadow Session 상태\n\n"
            "  SHADOW  : 실주문 전 관찰 단계\n"
            "            시스템은 신호를 생성하고 내부 평가를 계속하지만\n"
            "            실거래는 차단됩니다.\n\n"
            "  LIVE    : 게이트 조건 통과 → 실주문 허용\n\n"
            "  BLOCKED : 09:40 초과 & 조건 미통과 → 자동 진입 차단\n"
            "            ※ core_health 충족 시 장중 자동 복구\n\n"
            "통과 조건 (단일):\n"
            "  ① 건강점수 ≥ 70    (core_health_score)\n\n"
            "[2026-06-08] acc30m 게이트 제거\n"
            "  이유: 스캘퍼 진입 호라이즌(1m/5m)과 불일치,\n"
            "  30분 채점 지연으로 장초반에 의미 없음.\n"
            "  acc30m은 CB③(30분 정확도<35% → 당일 정지)에서만 관리.\n\n"
            "표시값:\n"
            "  H=core_health  Z=z경고누적"
        )
        self.lbl_shadow = mk_badge("", C['bg3'], C['text2'], 10)
        self.lbl_shadow.setText("SHADOW\nH:-- | Z:-")
        self.lbl_shadow.setMinimumWidth(S.p(110))
        self.lbl_shadow.setAlignment(Qt.AlignCenter)
        self.lbl_shadow.setWordWrap(True)
        self.lbl_shadow.setToolTip(_ss_tip)

        # ── [234차] 종목변경 재시작 배지 ─────────────────────────
        self.lbl_code_change = mk_badge("⚠ 종목변경됨 — 재시작", C['orange'], "#fff", 9)
        self.lbl_code_change.setVisible(False)
        self.lbl_code_change.setCursor(Qt.PointingHandCursor)
        self.lbl_code_change.setToolTip(
            "UI에서 선택한 종목코드가 현재 거래 종목과 다릅니다.\n"
            "클릭하면 포지션 FLAT 조건 확인 후 재시작합니다.\n\n"
            "⚠ 포지션 보유 중에는 재시작 불가 (청산 후 클릭).\n"
            "⚠ 15:10 이후에는 재시작 불가 (오버나이트 방지)."
        )
        self.lbl_code_change.mousePressEvent = (
            lambda _e: self.sig_code_change_restart_requested.emit()
        )

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

        self._pipe_elapsed_s: int = -1           # -1=미실행(대기), 0+=마지막 실행 후 경과초
        self._watchdog_alerted: set = set()    # 이미 발동한 임계값 (60/120/180s)
        self._pipeline_recovery_cb = None      # main.py가 등록하는 복구 콜백

        self.lbl_clock = None   # 제거됨 — _tick_header() 참조용 유지

        # ── 해상도·커밋·슬랙 On/Off 블록 (왼쪽 정렬) ────────────
        self.lbl_scale  = mk_label(S.info(),    C['text2'], 9, align=Qt.AlignLeft)
        self.lbl_commit = mk_label(COMMIT_HASH, C['text2'], 9, align=Qt.AlignLeft)
        _chk_style = (
            f"QCheckBox{{color:{C['text2']};font-size:{S.f(9)}px;spacing:{S.p(4)}px;}}"
            f"QCheckBox::indicator{{width:{S.p(11)}px;height:{S.p(11)}px;"
            f"border-radius:2px;}}"
            f"QCheckBox::indicator:checked{{background:{C['green']};"
            f"border:1px solid {C['green']};}}"
            f"QCheckBox::indicator:unchecked{{background:{C['bg2']};"
            f"border:1px solid {C['border']};}}"
        )
        self.chk_slack  = QCheckBox("슬랙 알림")
        self.chk_slack.setChecked(True)
        self.chk_slack.setCursor(Qt.PointingHandCursor)
        self.chk_slack.setToolTip("슬랙 알림 On/Off (체크 해제 시 모든 슬랙 발송 중단)")
        self.chk_slack.setStyleSheet(_chk_style)
        self.chk_mid_auto = QCheckBox("중패널_Auto")
        self.chk_mid_auto.setChecked(True)
        self.chk_mid_auto.setCursor(Qt.PointingHandCursor)
        self.chk_mid_auto.setToolTip("가운데 패널 탭 자동 이동 On/Off")
        self.chk_mid_auto.setStyleSheet(_chk_style)
        self.chk_right_auto = QCheckBox("우패널_Auto")
        self.chk_right_auto.setChecked(True)
        self.chk_right_auto.setCursor(Qt.PointingHandCursor)
        self.chk_right_auto.setToolTip("오른쪽 패널 탭 자동 이동 On/Off")
        self.chk_right_auto.setStyleSheet(_chk_style)
        self.chk_state_persist = QCheckBox("상태유지")
        self.chk_state_persist.setChecked(True)
        self.chk_state_persist.setCursor(Qt.PointingHandCursor)
        self.chk_state_persist.setToolTip(
            "재시작 시 ProfitGuard·CircuitBreaker 상태 영속화 On/Off\n"
            "개발/디버그 재시작 시 Off → 상태 초기화"
        )
        self.chk_state_persist.setStyleSheet(_chk_style)
        _cmb_chart_style = (
            f"QComboBox{{background:{C['bg2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:3px;"
            f"padding:1px 4px;font-size:{S.f(9)}px;}}"
            f"QComboBox QAbstractItemView{{background:{C['bg2']};color:{C['text']};"
            f"selection-background-color:{C['blue']};}}"
        )
        self.cmb_chart_auto = QComboBox()
        self.cmb_chart_auto.addItems(["수동", "자동팝업"])
        self.cmb_chart_auto.setFixedWidth(S.p(66))
        self.cmb_chart_auto.setCursor(Qt.PointingHandCursor)
        self.cmb_chart_auto.setToolTip("프로그램 시작 시 당일 1분봉 차트를 자동으로 팝업합니다")
        self.cmb_chart_auto.setStyleSheet(_cmb_chart_style)
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
        # Phase 3 알림 배지 (깜박임 — _blink_phase3 타이머로 갱신)
        self.lbl_phase3 = QLabel("Phase 3 예정")
        self.lbl_phase3.setStyleSheet(
            f"color:{C['orange']};font-size:{S.f(9)}px;font-weight:bold;"
            f"border:1px solid {C['orange']};border-radius:3px;padding:1px 5px;"
        )
        self.lbl_phase3.setToolTip(
            "Phase 3 — 모의투자 2주 이상 안정 확인 후 착수 예정\n\n"
            "구현 항목:\n"
            "  ① Platt Scaling 호라이즌별 독립 적용\n"
            "     ECE 측정 후 대상 호라이즌 결정\n"
            "  ② online_learner.py — anti_signal 채널 추가\n"
            "     역신호 학습 채널 (아이디어 C)\n"
            "  ③ MFE 기반 레이블 재설계\n"
            "     Phase 5 실전 전환 이후 착수\n\n"
            "착수 조건:\n"
            "  모의투자 4주 통산 수익률 양수\n"
            "  Circuit Breaker 1회 이상 정상 작동 확인\n"
            "  Walk-Forward 26주 통과 (Sharpe >= 1.5)"
        )
        self._phase3_blink_on = True

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(S.p(8))
        title_row.addWidget(title)
        title_row.addWidget(self.lbl_phase3)
        title_row.addStretch()

        title_box.addLayout(title_row)
        title_box.addLayout(acct_row)
        title_box.addLayout(strat_row)
        # ── 서버 구분 라디오 버튼 ─────────────────────────────────
        _rb_style = (
            f"QRadioButton{{color:{C['text2']};font-size:{S.f(9)}px;spacing:{S.p(3)}px;}}"
            f"QRadioButton::indicator{{width:{S.p(11)}px;height:{S.p(11)}px;"
            f"border-radius:{S.p(6)}px;}}"
            f"QRadioButton::indicator:unchecked{{background:{C['bg2']};"
            f"border:1px solid {C['border']};}}"
            f"QRadioButton::indicator:checked{{border:3px solid {C['bg2']};}}"
        )
        self._actual_server_mode = "unknown"   # 브로커 연결 후 set_server_mode()로 갱신
        self._server_rb_grp = QButtonGroup(self)
        self.rdo_simul = QRadioButton("모의투자")
        self.rdo_real  = QRadioButton("실서버")
        self.rdo_simul.setChecked(True)
        self.rdo_simul.setCursor(Qt.PointingHandCursor)
        self.rdo_real.setCursor(Qt.PointingHandCursor)
        self.rdo_simul.setToolTip("모의투자 서버에서 거래합니다")
        self.rdo_real.setToolTip("실서버에서 거래합니다 — 실제 자금 위험")
        self._server_rb_grp.addButton(self.rdo_simul, 0)
        self._server_rb_grp.addButton(self.rdo_real,  1)
        self.rdo_simul.setStyleSheet(_rb_style + f"QRadioButton::indicator:checked{{background:{C['cyan']};}}")
        self.rdo_real.setStyleSheet(_rb_style  + f"QRadioButton::indicator:checked{{background:{C['orange']};}}")
        self.lbl_server_warn = mk_label("", C['red'], 8, align=Qt.AlignLeft)
        self.lbl_server_warn.setVisible(False)
        # ── DB 초기화 버튼 (잠금해제 체크 후 활성) ────────────────
        self.chk_db_reset_unlock = QCheckBox("🔓")
        self.chk_db_reset_unlock.setChecked(False)
        self.chk_db_reset_unlock.setCursor(Qt.PointingHandCursor)
        self.chk_db_reset_unlock.setToolTip(
            "체크 시 손익추이 DB초기화 버튼 활성\n"
            "초기화 후 자동 잠금 복원"
        )
        self.chk_db_reset_unlock.setStyleSheet(_chk_style)
        self.btn_db_reset = QPushButton("DB초기화")
        self.btn_db_reset.setEnabled(False)
        self.btn_db_reset.setCursor(Qt.PointingHandCursor)
        self.btn_db_reset.setToolTip(
            "손익추이 DB 초기화\n"
            "trades · daily_stats · daily_broker_pnl 전체 삭제\n"
            "신규 체결부터 재집계"
        )
        self.btn_db_reset.setStyleSheet(
            f"QPushButton{{background:{C['bg2']};color:{C['red']};border:1px solid {C['red']};"
            f"border-radius:3px;padding:1px {S.p(6)}px;font-size:{S.f(9)}px;}}"
            f"QPushButton:enabled{{background:{C['red']};color:#fff;}}"
            f"QPushButton:disabled{{color:{C['border']};border-color:{C['border']};}}"
        )
        self.chk_db_reset_unlock.stateChanged.connect(
            lambda s: self.btn_db_reset.setEnabled(bool(s))
        )
        self.btn_db_reset.clicked.connect(self._on_db_reset_clicked)

        _sep = QLabel("|")
        _sep.setStyleSheet(f"color:{C['border']};padding:0 2px;")

        _rdo_row = QHBoxLayout()
        _rdo_row.setSpacing(S.p(8))
        _rdo_row.setContentsMargins(0, 0, 0, 0)
        _rdo_row.addWidget(self.rdo_simul)
        _rdo_row.addWidget(self.rdo_real)
        _rdo_row.addWidget(self.lbl_server_warn)
        _rdo_row.addWidget(self.chk_state_persist)
        _rdo_row.addWidget(_sep)
        _rdo_row.addWidget(self.chk_db_reset_unlock)
        _rdo_row.addWidget(self.btn_db_reset)
        _rdo_row.addStretch()
        self.rdo_simul.toggled.connect(self._on_server_mode_changed)

        res_box = QVBoxLayout()
        res_box.setSpacing(S.p(1))
        res_box.setContentsMargins(0, 0, 0, 0)
        res_box.setAlignment(Qt.AlignLeft)
        _chk_row = QHBoxLayout()
        _chk_row.setContentsMargins(0, 0, 0, 0)
        _chk_row.setSpacing(S.p(8))
        _chk_row.addWidget(self.chk_slack)
        _chk_row.addWidget(self.chk_mid_auto)
        _chk_row.addWidget(self.chk_right_auto)
        _lbl_chart = mk_label("봉차트", C['text2'], 9, align=Qt.AlignRight)
        _chk_row.addWidget(_lbl_chart)
        _chk_row.addWidget(self.cmb_chart_auto)
        _chk_row.addStretch()
        res_box.addWidget(self.lbl_scale)
        res_box.addWidget(self.lbl_commit)
        res_box.addLayout(_chk_row)
        res_box.addLayout(_rdo_row)

        # ── 오른쪽 컬럼: 현재가(상단) + 종목코드 + 시장구분 ─────────
        right_col = QVBoxLayout()
        right_col.setContentsMargins(S.p(8), 0, 0, 0)
        right_col.setSpacing(S.p(4))
        price_box.addStretch()
        right_col.addLayout(price_box)
        sym_row = QHBoxLayout()
        sym_row.setContentsMargins(0, 0, 0, 0)
        sym_row.setSpacing(S.p(4))
        lbl_sym = mk_label("종목코드:", C['text2'], 9, align=Qt.AlignRight)
        lbl_sym.setFixedWidth(header_label_w)
        self.cmb_symbol = QComboBox()
        self.cmb_symbol.setFixedWidth(header_combo_w)
        self.cmb_symbol.setStyleSheet(
            f"QComboBox{{background:{C['bg2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;"
            f"padding:2px 6px;font-size:{S.f(9)}px;}}"
            f"QComboBox QAbstractItemView{{background:{C['bg2']};color:{C['text']};"
            f"selection-background-color:{C['blue']};}}"
        )
        self.cmb_symbol.addItems(_MARKET_SYMBOLS["KOSPI200 선물"])
        self.cmb_symbol.currentTextChanged.connect(self._on_symbol_changed)
        sym_row.addWidget(lbl_sym)
        sym_row.addWidget(self.cmb_symbol)
        sym_row.addStretch()
        right_col.addLayout(sym_row)
        mkt_row = QHBoxLayout()
        mkt_row.setContentsMargins(0, 0, 0, 0)
        mkt_row.setSpacing(S.p(4))
        lbl_mkt = mk_label("시장구분:", C['text2'], 9, align=Qt.AlignRight)
        lbl_mkt.setFixedWidth(header_label_w)
        self.cmb_market = QComboBox()
        self.cmb_market.setFixedWidth(header_combo_w)
        self.cmb_market.setStyleSheet(
            f"QComboBox{{background:{C['bg2']};color:{C['text']};"
            f"border:1px solid {C['border']};border-radius:4px;"
            f"padding:2px 6px;font-size:{S.f(9)}px;}}"
            f"QComboBox QAbstractItemView{{background:{C['bg2']};color:{C['text']};"
            f"selection-background-color:{C['blue']};}}"
        )
        self.cmb_market.addItems(list(_MARKET_SYMBOLS.keys()))
        self.cmb_market.currentTextChanged.connect(self._on_market_changed)
        mkt_row.addWidget(lbl_mkt)
        mkt_row.addWidget(self.cmb_market)
        mkt_row.addStretch()
        right_col.addLayout(mkt_row)
        self._update_symbol_label(self.cmb_symbol.currentText())
        self._restore_ui_prefs()

        header.addLayout(title_box)
        header.addLayout(right_col)
        header.addStretch()
        for w in [self.lbl_ecb, self.lbl_regime, self._micro_box, self.lbl_cycle, self.lbl_gamma, self.lbl_pos, self.lbl_cb]:
            header.addWidget(w)
        header.addWidget(self.lbl_l2_halt)  # L2 halt badge (CB 오른쪽)
        header.addWidget(self.lbl_shs)        # SHS / EKS badge
        header.addWidget(self.lbl_shadow)     # ShadowSession 상태 배지
        header.addWidget(self.lbl_code_change)  # [234차] 종목변경 재시작 배지
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
        left_split.addWidget(card("",
                                  self.pred_panel, C['blue']))

        # 좌측 하단: 금일 conf 진입단계 추적 카드
        try:
            from dashboard.panels.conf_trend_widget import make_conf_trend_card
            self._conf_trend_card = make_conf_trend_card(parent=None)
            left_split.addWidget(self._conf_trend_card)
            # 340차: 호라이즌 on/off 체크박스 그리드 제거로 pred_panel 하단 여백이
            # 늘어난 만큼 진입단계 카드 쪽으로 배분 (500→420, 280→360)
            left_split.setSizes([200, 420, 360])
        except Exception as _cte:
            logger.warning("[Dashboard] ConfTrendCard 로드 실패: %s", _cte)
            left_split.setSizes([200, 740])

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

        # 챔피언-도전자 모니터 패널
        try:
            from dashboard.panels.challenger_panel import ChallengerPanel as _CP
            self.challenger_panel = _CP()  # engine은 나중에 set_challenger_engine()으로 주입
        except Exception as _ce:
            logger.warning("[Dashboard] ChallengerPanel 로드 실패: %s", _ce)
            self.challenger_panel = None
        if self.challenger_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.challenger_panel), "⚔ 도전자 모니터")

        # 수익 보존 가드 패널
        try:
            from dashboard.panels.profit_guard_panel import ProfitGuardPanel as _PGP
            self.profit_guard_panel = _PGP()
        except Exception as _pge:
            logger.warning("[Dashboard] ProfitGuardPanel 로드 실패: %s", _pge)
            self.profit_guard_panel = None
        if self.profit_guard_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.profit_guard_panel), "💰 수익 보존")

        # 셋업 기대값 패널
        try:
            from dashboard.panels.setup_expectancy_panel import SetupExpectancyPanel as _SEP
            self.setup_expectancy_panel = _SEP()
        except Exception as _sepe:
            logger.warning("[Dashboard] SetupExpectancyPanel 로드 실패: %s", _sepe)
            self.setup_expectancy_panel = None
        if self.setup_expectancy_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.setup_expectancy_panel), "📊 셋업 기대값")

        # [6순위] Shadow Session + Contrarian Mode 실험 게이트 패널
        try:
            from dashboard.panels.experiment_gate_panel import ExperimentGatePanel as _EGP
            self.experiment_gate_panel = _EGP()
        except Exception as _ege:
            logger.warning("[Dashboard] ExperimentGatePanel 로드 실패: %s", _ege)
            self.experiment_gate_panel = None
        if self.experiment_gate_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.experiment_gate_panel), "🧪 실험 게이트")

        # 재보정 모니터 통합 패널 — 임계값/ATR상하한/진입호라이즌 3개 재보정기를
        # 하위 탭으로 묶음 (기존 단독 "📐 임계값 모니터" 탭을 대체).
        try:
            from dashboard.panels.recalibrator_monitor_panel import RecalibratorMonitorPanel as _RMP
            self.recalibrator_monitor_panel = _RMP()
        except Exception as _rmpe:
            logger.warning("[Dashboard] RecalibratorMonitorPanel 로드 실패: %s", _rmpe)
            self.recalibrator_monitor_panel = None
        if self.recalibrator_monitor_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.recalibrator_monitor_panel), "📐 재보정 모니터")

        # 섹션 9: 스케일러 상태 모니터 패널
        try:
            from dashboard.panels.scaler_monitor_panel import ScalerMonitorPanel as _SMP
            self.scaler_monitor_panel = _SMP()
        except Exception as _smpe:
            logger.warning("[Dashboard] ScalerMonitorPanel 로드 실패: %s", _smpe)
            self.scaler_monitor_panel = None
        if self.scaler_monitor_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.scaler_monitor_panel), "🔬 스케일러")

        # 레짐 실시간 모니터 패널
        try:
            from dashboard.panels.regime_panel import RegimePanel as _RP
            self.regime_panel = _RP()
        except Exception as _rpe:
            logger.warning("[Dashboard] RegimePanel 로드 실패: %s", _rpe)
            self.regime_panel = None
        if self.regime_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.regime_panel), "🌐 레짐")

        # 동적 min_conf 모니터 패널
        try:
            from dashboard.panels.dynamic_mc_panel import DynamicMcPanel as _DMP
            self.dynamic_mc_panel = _DMP()
        except Exception as _dmpe:
            logger.warning("[Dashboard] DynamicMcPanel 로드 실패: %s", _dmpe)
            self.dynamic_mc_panel = None
        if self.dynamic_mc_panel is not None:
            self.mid_tabs.addTab(self._wrap(self.dynamic_mc_panel), "🎯 신뢰도 게이트")

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
        self.chk_mid_auto.toggled.connect(self.ui_auto_tabs.set_mid_auto)
        self.chk_right_auto.toggled.connect(self.ui_auto_tabs.set_right_auto)
        # _restore_ui_prefs 는 ui_auto_tabs 생성 전 호출 → 복원값을 직접 동기화
        self.ui_auto_tabs.set_mid_auto(self.chk_mid_auto.isChecked())
        self.ui_auto_tabs.set_right_auto(self.chk_right_auto.isChecked())
        # 체크박스 토글 시 즉시 저장 (슬랙 포함 — 종목/서버 변경에만 의존하던 문제 해소)
        self.chk_slack.toggled.connect(lambda _: self._save_ui_prefs())
        self.chk_mid_auto.toggled.connect(lambda _: self._save_ui_prefs())
        self.chk_right_auto.toggled.connect(lambda _: self._save_ui_prefs())
        self.chk_state_persist.toggled.connect(lambda _: self._save_ui_prefs())
        self.cmb_chart_auto.currentIndexChanged.connect(lambda _: self._save_ui_prefs())
        self.ui_auto_tabs.set_startup_mode()

    def toggle_minute_chart_dialog(self, auto_popup=False):
        self._minute_chart_dialog.maybe_roll_session()
        if self._minute_chart_dialog.isVisible():
            self._minute_chart_dialog.close()
            return
        self._minute_chart_dialog._start_reload_thread()  # 재기동 시 DB 새로고침
        # ── geometry 복원 전략 ────────────────────────────────────────
        # 수동 재열기: dialog가 이미 HIDDEN 상태이므로 show()가 마지막 위치 그대로 복원.
        #              singleShot(0) 만으로 충분.
        # 자동팝업 (재시동): dialog HWND가 최초 생성됨. show() 호출 시 Windows가
        #   부모(MireukDashboard, PRIMARY 모니터 최대화) 기준으로 HWND를 PRIMARY에 배치.
        #   이후 singleShot(0)에서 second monitor로 이동하면 WM_DPICHANGED 발생
        #   → Windows가 DPI 비율로 크기 재조정 → 크기 뒤죽박죽.
        # 해결: show() 전에 restore_saved_geometry()를 먼저 호출해 HWND 생성 위치를
        #   second monitor로 지정. Windows가 올바른 DPI 컨텍스트로 HWND를 생성.
        #   show() 이후 singleShot(0)으로 WM_SHOWWINDOW 재배치 보정.
        self._minute_chart_dialog.restore_saved_geometry()   # pre-show: HWND 생성 위치 지정
        self._minute_chart_dialog.show()
        self._minute_chart_dialog.raise_()
        self._minute_chart_dialog.activateWindow()
        QTimer.singleShot(0, self._minute_chart_dialog.restore_saved_geometry)  # post-show: WM_SHOWWINDOW 보정

    def minute_chart_tick(self, price: float, ts=None):
        self._minute_chart_dialog.update_tick(price, ts=ts)

    def minute_chart_candle_closed(self, candle: dict):
        self._minute_chart_dialog.on_candle_closed(candle)

    def minute_chart_set_regime(self, ts_key: str, regime: str):
        """파이프라인 완료 후 봉 레짐 색상 업데이트."""
        self._minute_chart_dialog.set_regime_at(ts_key, regime)

    def minute_chart_set_direction(self, ts_key: str, direction: int):
        """파이프라인 완료 후 봉 방향예측 색상 업데이트."""
        self._minute_chart_dialog.set_direction_at(ts_key, direction)

    def minute_chart_record_entry(self, direction: str, price: float, ts=None):
        self._minute_chart_dialog.record_entry(direction, price, ts=ts)

    def minute_chart_record_exit(
        self,
        price: float,
        ts=None,
        finalize: bool = True,
        pnl_pts: float = None,
        reason: str = "",
        direction: str = "",
    ):
        self._minute_chart_dialog.record_exit(
            price,
            ts=ts,
            finalize=finalize,
            pnl_pts=pnl_pts,
            reason=reason,
            direction=direction,
        )

    def minute_chart_sync_active_position(self, direction: str, price: float, ts=None):
        self._minute_chart_dialog.sync_active_position(direction, price, ts=ts)

    def minute_chart_clear_active_position(self):
        self._minute_chart_dialog.clear_active_position()

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

    def _update_symbol_label(self, text: str) -> None:
        parts = text.strip().split(None, 1)
        name = parts[1] if len(parts) > 1 else text
        self.lbl_futures_code.setText(name)

    def _on_symbol_changed(self, text: str):
        """종목코드 선택 변경 → 상단 종목명 라벨 갱신."""
        self._update_symbol_label(text)
        self._save_ui_prefs()
        self._refresh_code_change_badge()

    def _on_market_changed(self, market: str):
        """시장구분 선택 변경 → 종목코드 콤보 갱신 + 첫 종목명 반영."""
        symbols = _MARKET_SYMBOLS.get(market, [])
        self.cmb_symbol.blockSignals(True)
        self.cmb_symbol.clear()
        self.cmb_symbol.addItems(symbols)
        self.cmb_symbol.blockSignals(False)
        if symbols:
            self._on_symbol_changed(symbols[0])

    # ── [234차] 종목변경 배지 ──────────────────────────────────────

    def set_active_futures_code(self, code: str) -> None:
        """기동 시 확정된 종목코드 등록 — 이후 UI 변경과 비교해 배지를 표시한다."""
        self._active_futures_code = str(code or "").strip()
        self._refresh_code_change_badge()

    def _refresh_code_change_badge(self) -> None:
        """UI 선택 코드 vs 활성 코드 비교 → 불일치 시 재시작 배지 표시."""
        if not getattr(self, "_active_futures_code", ""):
            self.lbl_code_change.setVisible(False)
            return
        selected_raw = _extract_symbol_code(self.cmb_symbol.currentText())
        # 5자리(A0567)·8자리(A0567000) 모두 normalize 후 비교
        selected = _normalize_code_5(selected_raw)
        active = _normalize_code_5(self._active_futures_code)
        self.lbl_code_change.setVisible(bool(selected and selected != active))

    # ── 서버 모드 관리 ─────────────────────────────────────────

    def set_server_mode(self, mode: str) -> None:
        """브로커 연결 후 실제 서버 타입 설정 (mode: 'simul' | 'real').
        main.py connect_broker 성공 후 호출한다.
        """
        self._actual_server_mode = mode
        self._update_server_warn()

    def is_server_match(self) -> bool:
        """라디오 버튼 선택 == 실제 접속 서버 여부 반환. 불일치 시 진입 차단."""
        actual = self._actual_server_mode
        if actual == "unknown":
            return True   # 연결 전: 제한 없음
        selected = "simul" if self.rdo_simul.isChecked() else "real"
        return selected == actual

    def _on_db_reset_clicked(self) -> None:
        """손익추이 DB 3테이블 초기화 — 잠금 해제 후 클릭 시 확인 다이얼로그."""
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("손익추이 DB 초기화")
        msg.setText(
            "trades · daily_stats · daily_broker_pnl\n"
            "3개 테이블을 모두 삭제합니다.\n\n"
            "이 작업은 되돌릴 수 없습니다."
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        if msg.exec_() != QMessageBox.Ok:
            return
        try:
            import datetime as _dt
            import shutil as _sh
            from config.settings import TRADES_DB, DB_DIR
            import os as _os
            # 백업 생성
            bak = _os.path.join(
                DB_DIR,
                f"trades_backup_{_dt.date.today().strftime('%Y%m%d_%H%M%S')}.db"
            )
            _sh.copy2(TRADES_DB, bak)
            # 3테이블 초기화 (VACUUM은 트랜잭션 외부에서 별도 실행)
            import sqlite3 as _sqlite3
            from utils.db_utils import get_conn
            with get_conn(TRADES_DB) as conn:
                conn.execute("DELETE FROM trades")
                conn.execute("DELETE FROM daily_stats")
                conn.execute("DELETE FROM daily_broker_pnl")
                conn.execute("DELETE FROM sqlite_sequence WHERE name='trades'")
            _vc = _sqlite3.connect(TRADES_DB, isolation_level=None)
            try:
                _vc.execute("VACUUM")
            finally:
                _vc.close()
            # 손익추이 패널 갱신
            self.log_panel.refresh_pnl_history([])
            # 자동 잠금 복원
            self.chk_db_reset_unlock.setChecked(False)
            QMessageBox.information(
                self, "완료",
                f"초기화 완료.\n백업: {_os.path.basename(bak)}"
            )
        except Exception as _e:
            from PyQt5.QtWidgets import QMessageBox as _MB
            _MB.critical(self, "오류", f"DB 초기화 실패:\n{_e}")

    def _on_server_mode_changed(self) -> None:
        self._update_server_warn()
        self._save_ui_prefs()

    def _update_server_warn(self) -> None:
        actual = self._actual_server_mode
        if actual == "unknown":
            self.lbl_server_warn.setVisible(False)
            return
        selected = "simul" if self.rdo_simul.isChecked() else "real"
        if selected == actual:
            self.lbl_server_warn.setVisible(False)
        else:
            actual_lbl = "모의투자" if actual == "simul" else "실서버"
            self.lbl_server_warn.setText(f"⚠ 실접속={actual_lbl} · 진입차단")
            self.lbl_server_warn.setStyleSheet(
                f"color:{C['red']};font-size:{S.f(8)}px;font-weight:bold;"
            )
            self.lbl_server_warn.setVisible(True)

    def _save_ui_prefs(self):
        """현재 종목코드·시장구분·슬랙 On/Off를 ui_prefs.json에 저장.
        기존 파일의 다른 키(pnl_cb_* 등)는 읽어서 병합 — 덮어쓰기 금지.
        """
        try:
            prefs = {}
            if os.path.exists(_UI_PREFS_FILE):
                try:
                    with open(_UI_PREFS_FILE, "r", encoding="utf-8") as _rf:
                        prefs = json.load(_rf)
                except Exception:
                    prefs = {}
            symbol_text = self.cmb_symbol.currentText()
            prefs.update({
                "version": 2,
                "market": self.cmb_market.currentText(),
                "symbol_code": _extract_symbol_code(symbol_text),
                "symbol_text": symbol_text,
                "slack_enabled": self.chk_slack.isChecked(),
                "mid_auto_enabled": self.chk_mid_auto.isChecked(),
                "right_auto_enabled": self.chk_right_auto.isChecked(),
                "state_persist_enabled": self.chk_state_persist.isChecked(),
                "server_mode": "simul" if self.rdo_simul.isChecked() else "real",
                "chart_auto_popup": self.cmb_chart_auto.currentText() == "자동팝업",
            })
            with open(_UI_PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump(prefs, f, ensure_ascii=False)
        except Exception:
            pass

    def _restore_ui_prefs(self):
        """ui_prefs.json에서 마지막 선택값을 복원."""
        try:
            if not os.path.exists(_UI_PREFS_FILE):
                return
            with open(_UI_PREFS_FILE, "r", encoding="utf-8") as f:
                prefs = json.load(f)
            market = prefs.get("market", "")
            symbol_code = prefs.get("symbol_code", "")
            symbol_text = prefs.get("symbol_text", prefs.get("symbol", ""))
            if market not in _MARKET_SYMBOLS:
                market = self.cmb_market.currentText()

            symbols = _MARKET_SYMBOLS.get(market, [])
            selected_symbol = _find_symbol_text(
                market,
                symbol_code=symbol_code,
                symbol_text=symbol_text,
            )

            self.cmb_market.blockSignals(True)
            self.cmb_market.setCurrentText(market)
            self.cmb_market.blockSignals(False)

            self.cmb_symbol.blockSignals(True)
            self.cmb_symbol.clear()
            self.cmb_symbol.addItems(symbols)
            if selected_symbol:
                self.cmb_symbol.blockSignals(True)
                self.cmb_symbol.setCurrentText(selected_symbol)
            self.cmb_symbol.blockSignals(False)

            if selected_symbol:
                self._update_symbol_label(selected_symbol)

            # 슬랙 On/Off 복원 (기본 True)
            slack_on = bool(prefs.get("slack_enabled", True))
            self.chk_slack.blockSignals(True)
            self.chk_slack.setChecked(slack_on)
            self.chk_slack.blockSignals(False)

            # 탭 자동 이동 On/Off 복원 (기본 True) — ui_auto_tabs 연결 전이므로 blockSignals
            mid_auto = bool(prefs.get("mid_auto_enabled", True))
            right_auto = bool(prefs.get("right_auto_enabled", True))
            self.chk_mid_auto.blockSignals(True)
            self.chk_mid_auto.setChecked(mid_auto)
            self.chk_mid_auto.blockSignals(False)
            self.chk_right_auto.blockSignals(True)
            self.chk_right_auto.setChecked(right_auto)
            self.chk_right_auto.blockSignals(False)

            # 상태유지 On/Off 복원 (기본 True)
            state_persist = bool(prefs.get("state_persist_enabled", True))
            self.chk_state_persist.blockSignals(True)
            self.chk_state_persist.setChecked(state_persist)
            self.chk_state_persist.blockSignals(False)

            # 서버 모드 복원 (기본 모의투자)
            saved_mode = prefs.get("server_mode", "simul")
            is_real = (saved_mode == "real")
            self.rdo_simul.blockSignals(True)
            self.rdo_real.blockSignals(True)
            self.rdo_real.setChecked(is_real)
            self.rdo_simul.setChecked(not is_real)
            self.rdo_simul.blockSignals(False)
            self.rdo_real.blockSignals(False)

            # 봉차트 자동팝업 복원 (기본 수동)
            chart_auto = bool(prefs.get("chart_auto_popup", False))
            self.cmb_chart_auto.blockSignals(True)
            self.cmb_chart_auto.setCurrentText("자동팝업" if chart_auto else "수동")
            self.cmb_chart_auto.blockSignals(False)
        except Exception:
            pass

    def set_selected_symbol(self, code, market=None):
        """브로커 프로브 결과로 종목 콤보를 업데이트한다 (롤오버 UI 동기화).

        code: 5자리(A0566) 또는 8자리(A0566000) 코드.
        market: 시장구분 명칭. None이면 코드에서 자동 판별.
        콤보에 없는 코드는 동적으로 삽입한다.
        """
        c = str(code or "").strip()
        if len(c) == 5:
            c8 = c + "000"
        elif len(c) == 8 and c.endswith("000"):
            c8 = c
        else:
            c8 = c  # 비표준 길이 — 그대로 사용

        if market is None:
            norm = c[1:] if c.startswith("A") else c
            market = "KOSPI200 미니선물" if norm.startswith("05") else "KOSPI200 선물"

        # 시장구분 콤보 갱신 (변경이 있을 때만)
        if self.cmb_market.currentText() != market:
            symbols = _MARKET_SYMBOLS.get(market, [])
            self.cmb_market.blockSignals(True)
            self.cmb_market.setCurrentText(market)
            self.cmb_market.blockSignals(False)
            self.cmb_symbol.blockSignals(True)
            self.cmb_symbol.clear()
            self.cmb_symbol.addItems(symbols)
            self.cmb_symbol.blockSignals(False)

        # 매칭 항목 선택
        for i in range(self.cmb_symbol.count()):
            item_text = self.cmb_symbol.itemText(i)
            if _extract_symbol_code(item_text) == c8:
                self.cmb_symbol.blockSignals(True)
                self.cmb_symbol.setCurrentIndex(i)
                self.cmb_symbol.blockSignals(False)
                self._update_symbol_label(item_text)
                self._save_ui_prefs()
                return

        # 콤보에 없는 코드 — 동적으로 맨 앞에 삽입
        norm = (c[1:] if c.startswith("A") else c)
        try:
            year_digit = norm[2]
            month_n = int(norm[3:], 16)
            pfx = "미니 F" if market == "KOSPI200 미니선물" else "F"
            label = "{pfx} 20{y}{m:02d}  (롤오버)".format(
                pfx=pfx, y=year_digit, m=month_n
            )
        except (IndexError, ValueError):
            label = code + "  (롤오버)"
        new_text = "{c8}  {label}".format(c8=c8, label=label)
        self.cmb_symbol.blockSignals(True)
        self.cmb_symbol.insertItem(0, new_text)
        self.cmb_symbol.setCurrentIndex(0)
        self.cmb_symbol.blockSignals(False)
        self._update_symbol_label(new_text)
        self._save_ui_prefs()

    def _blink_phase3(self):
        """Phase 3 알림 배지 800ms 깜박임."""
        self._phase3_blink_on = not self._phase3_blink_on
        if self._phase3_blink_on:
            style = (
                f"color:{C['orange']};font-size:{S.f(9)}px;font-weight:bold;"
                f"border:1px solid {C['orange']};border-radius:3px;padding:1px 5px;"
            )
        else:
            style = (
                f"color:{C['bg3']};font-size:{S.f(9)}px;font-weight:bold;"
                f"border:1px solid {C['bg3']};border-radius:3px;padding:1px 5px;"
            )
        self.lbl_phase3.setStyleSheet(style)

    def _tick_header(self):
        """1초마다 헤더 가동 경과시간 + 파이프라인 생존 바 갱신."""
        import time as _t
        _now_mono = _t.monotonic()
        # ── 메인 스레드 블로킹 검출 ─────────────────────────────────
        # _tick_header는 1초마다 호출됨. 직전 호출과 간격이 2s 초과이면
        # 그 사이에 메인 스레드가 블로킹됐다는 직접 증거.
        _prev = getattr(self, "_tick_header_last_mono", None)
        if _prev is not None:
            _gap_ms = (_now_mono - _prev) * 1000
            if _gap_ms > 2000:
                logger.warning(
                    "[LiveDBG] _tick_header 간격 %.0fms — 메인 스레드 블로킹 발생 | "
                    "pipe_elapsed=%d watchdog_alerted=%s",
                    _gap_ms,
                    self._pipe_elapsed_s,
                    sorted(self._watchdog_alerted),
                )
        self._tick_header_last_mono = _now_mono
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
        # _pipe_elapsed_s == -1 : 아직 한 번도 실행되지 않은 상태 (대기)
        if self._pipe_elapsed_s < 0:
            return  # "── 대기" 텍스트·빈 바 유지, 워치독 미발동

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

    def closeEvent(self, event):
        """메인 윈도우 종료 시 '완전 종료 / 재시작' 선택 다이얼로그 표시.

        [229차] X 버튼 클릭 시 의도를 확인:
          - 완전 종료: _exit_normally 플래그 → 런처 RESTART_LOOP 종료
          - 재시작:    플래그 없음 → 런처 AUTO-RESTART 10초 후 재기동
          - 취소:      닫기 취소

        Qt 부모-자식 소멸 경로에서는 자식 closeEvent가 호출되지 않으므로,
        메인 윈도우 closeEvent에서 차트 다이얼로그를 먼저 닫아 geometry를 저장한다.
        """
        from PyQt5.QtWidgets import QMessageBox as _MB
        _dlg = _MB(self)
        _dlg.setWindowTitle("미륵이 종료")
        _dlg.setText("종료 방법을 선택하세요.")
        _dlg.setInformativeText(
            "완전 종료: 런처(배치창)도 함께 종료됩니다.\n"
            "재시작: 10초 후 런처가 자동으로 재기동합니다."
        )
        _btn_full = _dlg.addButton("완전 종료", _MB.DestructiveRole)
        _btn_restart = _dlg.addButton("재시작 (10초 후)", _MB.AcceptRole)
        _btn_cancel = _dlg.addButton("취소", _MB.RejectRole)
        _dlg.setDefaultButton(_btn_cancel)
        _dlg.exec_()
        _clicked = _dlg.clickedButton()

        if _clicked == _btn_cancel:
            event.ignore()
            return

        # 차트 다이얼로그 geometry 저장
        if hasattr(self, '_minute_chart_dialog'):
            try:
                if self._minute_chart_dialog.isVisible():
                    self._minute_chart_dialog.close()
            except Exception:
                pass

        if _clicked == _btn_full:
            # 완전 종료: 플래그 생성 → 런처 재시작 방지
            try:
                import os as _os, datetime as _dt
                _flag = _os.path.join(
                    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                    "data", "_exit_normally",
                )
                with open(_flag, "w", encoding="utf-8") as _f:
                    _f.write(f"user_close\n{_dt.datetime.now().isoformat()}\n")
            except Exception:
                pass
        # 재시작: 플래그 없음 → 런처가 10초 후 AUTO-RESTART

        # super().closeEvent 만으로는 차트 다이얼로그 등 다른 Qt 윈도우가
        # 남아있을 때 quitOnLastWindowClosed 자동 종료가 트리거되지 않아
        # Python 프로세스가 살아있게 된다 → QApplication.quit() 명시 호출 필수.
        # Qt WA_DeleteOnClose 등 기본 처리 보존을 위해 super() 먼저 호출.
        super().closeEvent(event)
        from PyQt5.QtWidgets import QApplication as _QApp
        _QApp.instance().quit()


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
        self._profit_guard = None  # L2 배지 초기화용
        # 긴급 정지 버튼을 외부에서 접근할 수 있도록 노출
        self.btn_kill = self._win._make_kill_btn()
        self.btn_save_account = self._win.btn_save_account
        self.chk_slack = self._win.chk_slack
        self.sig_position_restore = self._win.account_info_panel.sig_position_restore
        self.sig_balance_refresh_requested = self._win.account_info_panel.sig_balance_refresh_requested
        self.sig_reverse_entry_toggled    = self._win.entry_panel.sig_reverse_entry_toggled
        self.sig_manual_entry_requested   = self._win.entry_panel.sig_manual_entry_requested
        self.sig_instant_exit_requested   = self._win.entry_panel.sig_instant_exit_requested
        self.sig_auto_mode_changed        = self._win.entry_panel.sig_auto_mode_changed
        self.sig_tp1_protect_mode_changed = self._win.exit_panel.sig_tp1_protect_mode_changed
        self.sig_manual_exit_requested    = self._win.exit_panel.sig_manual_exit_requested
        self.sig_max_qty_changed          = self._win.entry_panel.sig_max_qty_changed
        self.sig_layer2_gate_toggled      = self._win.entry_panel.sig_layer2_gate_toggled
        self.sig_apply_candidate_requested = self._win.feat_panel.sig_apply_candidate_requested
        self.sig_force_retrain_requested = self._win.feat_panel.sig_force_retrain_requested
        self.sig_reset_feature_set_requested = self._win.feat_panel.sig_reset_feature_set_requested
        # [234차] 종목변경 재시작 요청 시그널
        self.sig_code_change_restart_requested = self._win.sig_code_change_restart_requested

    # ── 필수 메서드 ────────────────────────────────────────────
    def show(self):
        self._win.showMaximized()
        self._win.raise_()
        self._win.activateWindow()
        # [195차] Windows foreground lock 우회 — raise_/activateWindow 만으로는
        # 다른 프로세스(Cybos HTS 등)가 포커스를 쥐고 있으면 foreground 이동 불가.
        # AttachThreadInput으로 현재 foreground 스레드에 붙인 뒤 SetForegroundWindow 호출.
        from PyQt5.QtCore import QTimer as _QTimer
        _QTimer.singleShot(400, self._bring_to_front)
        if self._win.cmb_chart_auto.currentText() == "자동팝업":
            _QTimer.singleShot(600, lambda: self._win.toggle_minute_chart_dialog(auto_popup=True))

    def _bring_to_front(self):
        """Windows API로 창을 강제로 맨 앞(foreground)으로 이동."""
        try:
            import ctypes
            user32   = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            hwnd     = int(self._win.winId())
            # 현재 foreground 창의 스레드에 Attach → SetForegroundWindow 권한 획득
            fg_hwnd = user32.GetForegroundWindow()
            fg_tid  = user32.GetWindowThreadProcessId(fg_hwnd, None)
            my_tid  = kernel32.GetCurrentThreadId()
            if fg_hwnd and fg_tid and fg_tid != my_tid:
                user32.AttachThreadInput(my_tid, fg_tid, True)
                user32.BringWindowToTop(hwnd)
                user32.SetForegroundWindow(hwnd)
                user32.AttachThreadInput(my_tid, fg_tid, False)
            else:
                user32.SetForegroundWindow(hwnd)
            user32.SwitchToThisWindow(hwnd, True)
        except Exception:
            pass

    def _save_ui_prefs(self):
        self._win._save_ui_prefs()

    def set_server_mode(self, mode: str) -> None:
        """실제 접속 서버 타입 전달 (mode: 'simul' | 'real'). connect_broker 후 호출."""
        self._win.set_server_mode(mode)

    def is_server_match(self) -> bool:
        """라디오 선택 == 실제 서버 여부. False 시 진입 차단해야 함."""
        return self._win.is_server_match()


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

    def get_selected_symbol(self) -> str:
        """선택된 종목코드 반환 (예: 'A0166000  F 202606' → 'A0166000')."""
        return _extract_symbol_code(self._win.cmb_symbol.currentText())

    def get_selected_market(self) -> str:
        """선택된 시장구분 반환 (예: '한국장')."""
        return self._win.cmb_market.currentText().strip()

    def set_selected_symbol(self, code, market=None):
        """브로커 프로브 결과로 종목 콤보를 업데이트한다 (롤오버 UI 동기화).

        code: 5자리(A0566) 또는 8자리(A0566000).
        market: None이면 코드에서 자동 판별.
        """
        self._win.set_selected_symbol(code, market=market)

    def set_active_futures_code(self, code: str) -> None:
        """[234차] 기동 시 확정된 종목코드 등록 — UI 변경 시 재시작 배지 활성화 기준."""
        self._win.set_active_futures_code(code)

    def update_account_balance(self, summary: dict, rows, quiet: bool = False, mark_fresh: bool = True, source: str = "broker", balance_active: bool = True):
        if not quiet:
            logger.info(
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
        # 레짐 패널 Layer 1 갱신
        _rp = getattr(self._win, "regime_panel", None)
        if _rp is not None:
            try:
                _rp.update_layer1(regime, f"VIX={vix:.1f} SP500={sp500_chg:+.2%} KRW={usd_krw:+.2f}")
            except Exception:
                pass

    def update_micro_regime(self, micro_regime: str, adx: float = 0.0,
                            atr_ratio: float = 1.0, duration: int = 0):
        """미시 레짐 헤더 배지 + 챌린저 패널 갱신"""
        _col_map = {
            "추세장": C['green'],
            "횡보장": C['blue'],
            "급변장": C['red'],
            "혼합":   C['orange'],
            "탈진":   "#9C27B0",   # 보라색 — 탈진 레짐 전용
        }
        col = _col_map.get(micro_regime, C['orange'])
        self._win.lbl_micro_regime.setText(micro_regime)
        self._win.lbl_micro_regime.setStyleSheet(
            f"background:{col};color:#fff;border-radius:3px;"
            f"font-size:{S.f(11)}px;font-weight:bold;padding:1px 6px;"
        )
        # 챌린저 패널에도 전달
        cp = getattr(self._win, "challenger_panel", None)
        if cp is not None:
            try:
                cp.update_micro_regime(micro_regime, adx, atr_ratio, duration)
            except Exception:
                pass
        # 레짐 패널 Micro 갱신
        _rp = getattr(self._win, "regime_panel", None)
        if _rp is not None:
            try:
                _rp.update_micro(micro_regime, adx, atr_ratio)
            except Exception:
                pass

    def update_micro_regime_warmup(self, warmup: dict):
        wrap = getattr(self._win, "_micro_warmup_wrap", None)
        if wrap is None:
            return

        warmup = warmup or {}
        active = bool(warmup.get("active"))
        if not active:
            wrap.setVisible(False)
            return

        progress = int(warmup.get("progress", 0) or 0)
        remaining = int(warmup.get("remaining_bars", 0) or 0)
        level = str(warmup.get("level", "L?") or "L?")
        adx_progress = int(warmup.get("adx_progress", 0) or 0)
        atr_progress = int(warmup.get("atr_progress", 0) or 0)

        if level == "L1":
            chunk_col = C['red']
        elif level == "L2":
            chunk_col = C['orange']
        else:
            chunk_col = C['blue']

        self._win.lbl_micro_warmup.setText(
            "%s 레짐 워밍업 %d%% · %d분 남음" % (level, progress, remaining)
        )
        self._win.pb_micro_warmup.setValue(progress)
        self._win.pb_micro_warmup.setToolTip(
            "미시 레짐 워밍업\n"
            "ADX: %d%% | ATR avg: %d%%\n"
            "남은 시간: 약 %d분" % (adx_progress, atr_progress, remaining)
        )
        self._win.pb_micro_warmup.setStyleSheet(
            f"QProgressBar{{background:{C['bg3']};border:none;border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{chunk_col};border-radius:2px;}}"
        )
        wrap.setVisible(True)

    def update_system_status(
        self,
        cb_state: str = "NORMAL",
        latency_ms: float = 0.0,
        accuracy: float = 0.0,
        cb3_samples: int = 0,
    ):
        """시스템 상태 (Circuit Breaker, 지연, 정확도) 업데이트"""
        # CB③ 발동 최솟 샘플(25건) 기준으로 표시 분기
        # — 25건 미만은 통계적 의미 없음. "0.0%(1건)" 오표시로 오해 방지
        if cb3_samples >= 25:
            acc_str = f"CB③30m={accuracy:.1%}({cb3_samples}건)"
        elif cb3_samples > 0:
            acc_str = f"CB③30m=집계중({cb3_samples}/25건)"
        else:
            acc_str = "CB③30m=집계중"
        self._win.log_panel.append(
            "model", "SYSTEM",
            f"CB={cb_state} | 처리시간={latency_ms:.0f}ms | {acc_str}"
        )
        # 헤더 CB 배지 갱신
        lbl = getattr(self._win, "lbl_cb", None)
        if lbl is None:
            return
        if cb_state == "HALTED":
            lbl.setText("  ⛔ CB HALT  ")
            lbl.setStyleSheet(
                f"background:#B71C1C;color:#fff;"
                f"border:2px solid #FF5252;"
                f"border-radius:{S.p(3)}px;"
                f"font-size:{S.f(11)}px;font-weight:bold;"
                f"padding:{S.p(1)}px {S.p(3)}px;"
            )
        elif cb_state == "PAUSED":
            lbl.setText("  ⏸ CB PAUSE  ")
            lbl.setStyleSheet(
                f"background:#E65100;color:#fff;"
                f"border:1px solid #FFB74D;"
                f"border-radius:{S.p(3)}px;"
                f"font-size:{S.f(11)}px;font-weight:bold;"
                f"padding:{S.p(1)}px {S.p(3)}px;"
            )
        else:
            lbl.setText("CB NORMAL")
            lbl.setStyleSheet(
                f"background:{C['bg3']};color:{C['text2']};"
                f"border-radius:{S.p(3)}px;"
                f"font-size:{S.f(11)}px;font-weight:bold;"
                f"padding:{S.p(1)}px {S.p(3)}px;"
            )

    def update_exchange_cb_badge(
        self,
        state: str = "NORMAL",
        resume_est: str = "",
        until_dt=None,
    ) -> None:
        """거래소 서킷브레이커 상태 배지 갱신.

        state:
          "NORMAL"    — 정상 거래 중 → 배지 숨김
          "CB_ACTIVE" — 거래소 CB 발동 중 (거래 중단)
          "OBSERVING" — CB 해제 후 관망 기간 (신규 진입 차단)

        resume_est: CB 예상 재개 시각 문자열 (HH:MM)
        until_dt:   관망 종료 datetime (OBSERVING 상태에서 남은 분 계산용)
        """
        import datetime as _dt
        lbl = getattr(self._win, "lbl_ecb", None)
        if lbl is None:
            return

        if state == "CB_ACTIVE":
            _est = resume_est or "--:--"
            lbl.setText(f"KRX CB ⏸\n재개≈{_est}")
            lbl.setStyleSheet(
                f"background:#7a0000;color:#fff;"
                f"border:2px solid #FF5252;"
                f"border-radius:{S.p(3)}px;"
                f"font-size:{S.f(10)}px;font-weight:bold;"
                f"padding:{S.p(1)}px {S.p(4)}px;"
            )
            lbl.setToolTip(
                f"거래소 서킷브레이커 발동 중\n"
                f"KRX: 20분 거래 중단 → 10분 단일가매매\n"
                f"예상 재개: {_est}\n"
                f"분봉 재수신 시 자동 복구"
            )
            lbl.setVisible(True)

        elif state == "OBSERVING":
            if until_dt is not None:
                _remain = max(0, int(
                    (_dt.datetime.now() - until_dt).total_seconds() / -60
                ))
                _until_str = until_dt.strftime("%H:%M")
                _body = f"관망 {_remain}분\n{_until_str} 재개"
            else:
                _body = "관망 중\n진입 차단"
            lbl.setText(_body)
            lbl.setStyleSheet(
                f"background:#7a3800;color:#fff;"
                f"border:2px solid #FFB74D;"
                f"border-radius:{S.p(3)}px;"
                f"font-size:{S.f(10)}px;font-weight:bold;"
                f"padding:{S.p(1)}px {S.p(4)}px;"
            )
            lbl.setToolTip(
                f"거래소 CB 해제 후 관망 구간\n"
                f"단일가매매·급변 안정화 대기 중 신규 진입 차단\n"
                f"{'종료: ' + until_dt.strftime('%H:%M') if until_dt else ''}"
            )
            lbl.setVisible(True)

        else:  # NORMAL
            lbl.setVisible(False)

    def update_shs_badge(
        self, shs: float, entry_blocked: bool, kill_switch: bool, eks_reason: str = ""
    ) -> None:
        """SHS 배지 색상·텍스트 갱신 (매분 파이프라인에서 호출)."""
        lbl = getattr(self._win, "lbl_shs", None)
        if lbl is None:
            return
        if kill_switch:
            # [C3] 원인 있으면 "관망일" 아래 2줄로 표시
            text = f"⛔ 관망일\n{eks_reason}" if eks_reason else "⛔ 관망일"
            bg, fg = C["red"], "#fff"
            tip = "Early Kill Switch 발동 — 자동 진입 차단 중"
            lbl.setWordWrap(True)
            lbl.setMinimumWidth(S.p(90))
        elif entry_blocked:
            # [459차 F2] 경고 상태만 소수 1자리 — `.0f`는 SHS 59.5~59.9를 "60"으로
            # 반올림해 "60점인데 60점 미만 경고"라는 자기모순 표시를 만들었다.
            text, bg, fg = f"⚠ SHS {shs:.1f}", C["orange"], "#fff"
            tip = (
                "시스템 건강 점수 60점 미만 — 경고 표시 전용입니다.\n"
                "이 배지는 신규 진입을 차단하지 않습니다 "
                "(실제 차단은 Early Kill Switch·서킷브레이커)."
            )
            lbl.setWordWrap(False)
        elif shs >= 80:
            text, bg, fg = f"♥ SHS {shs:.0f}", C["green"], "#fff"
            tip = "시스템 건강 점수 양호"
            lbl.setWordWrap(False)
        else:
            text, bg, fg = f"SHS {shs:.0f}", C["blue"], "#fff"
            tip = "시스템 건강 점수 정상 범위"
            lbl.setWordWrap(False)
        lbl.setToolTip(tip)   # [459차 F2] 상태 전환 시 이전 툴팁이 남지 않도록 매번 지정
        lbl.setText(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"background:{bg};color:{fg};"
            f"border-radius:{S.p(4)}px;"
            f"padding:{S.p(1)}px {S.p(5)}px;"
            f"font-size:{S.f(11)}px;font-weight:bold;"
        )

    def update_l2_halt_badge(self, is_halted: bool, threshold: float = 0.0):
        """L2 Tier Gate 영구중단 상태 배지 업데이트"""
        lbl = getattr(self._win, "lbl_l2_halt", None)
        if lbl is None:
            return
        
        if is_halted:
            lbl.setText(f"  🔒 L2 중단  ({threshold/1e6:.1f}M원)")
            lbl.setStyleSheet(
                f"background:#C62828;color:#fff;"
                f"border:2px solid #FF5252;"
                f"border-radius:{S.p(3)}px;"
                f"font-size:{S.f(10)}px;font-weight:bold;"
                f"padding:{S.p(1)}px {S.p(3)}px;"
            )
        else:
            # 비활성 상태: 텍스트 유지, 색상만 회색으로
            lbl.setText("L2 —")
            lbl.setStyleSheet(
                f"background:{C['bg3']};color:{C['text2']};"
                f"border:1px solid {C['border']};"
                f"border-radius:{S.p(3)}px;"
                f"font-size:{S.f(10)}px;"
                f"padding:{S.p(1)}px {S.p(3)}px;"
            )

    def update_shadow_badge(
        self,
        state: str,
        acc30m: float,
        core_health: int,
        z_warn_count: int,
    ) -> None:
        """ShadowSession 배지 갱신 (매분 파이프라인에서 호출).

        Args:
            state:        "SHADOW" / "LIVE" / "BLOCKED"
            acc30m:       30분 정확도 (0.0~1.0) — 표시 전용, 게이트 조건 아님
            core_health:  core_health_score (0~100) — 단일 게이트 조건
            z_warn_count: 최근 5분 z-score 경고 누적 횟수
        """
        lbl = getattr(self._win, "lbl_shadow", None)
        if lbl is None:
            return

        text = f"{state}\nH:{core_health} | Z:{z_warn_count}"

        if state == "LIVE":
            bg, fg = C["green"], "#fff"
        elif state == "BLOCKED":
            bg, fg = C["red"], "#fff"
        else:
            # SHADOW — core_health 통과 직전이면 파랑, 미통과면 회색
            gates_ok = core_health >= 70
            bg, fg = (C["blue"], "#fff") if gates_ok else (C["bg3"], C["text2"])

        lbl.setText(text)
        lbl.setStyleSheet(
            f"background:{bg};color:{fg};"
            f"border-radius:{S.p(3)}px;"
            f"font-size:{S.f(10)}px;font-weight:bold;"
            f"padding:{S.p(1)}px {S.p(3)}px;"
        )

    def update_position(self, pos_data: dict):
        """청산 패널 포지션 데이터 업데이트"""
        self._win.exit_panel.update_data(pos_data)
        # 헤더 포지션 배지 갱신
        lbl = getattr(self._win, "lbl_pos", None)
        if lbl is None:
            return
        status = str((pos_data or {}).get("status", "FLAT") or "FLAT").strip().upper()
        _pos_style = {
            "LONG":  (C["green"], "#fff"),
            "SHORT": (C["red"],   "#fff"),
            "FLAT":  (C["bg3"],   C["text2"]),
        }
        bg, fg = _pos_style.get(status, (C["bg3"], C["text2"]))
        lbl.setText(status)
        lbl.setStyleSheet(
            f"background:{bg};color:{fg};border-radius:{S.p(3)}px;"
            f"font-size:{S.f(11)}px;font-weight:bold;padding:1px 6px;"
        )
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
                          conf: float = None, corr: str = "", min_conf: float = 0.58,
                          bar_ages: dict = None):
        """멀티 호라이즌 예측 패널 업데이트"""
        self._win.pred_panel.update_data(price, preds, params, conf, corr, min_conf=min_conf,
                                         bar_ages=bar_ages)

    def update_entry(self, signal: str, conf: float, grade: str, checks: dict,
                     qty: int = 0, final_signal: str = None,
                     reverse_enabled: bool = False, min_conf: float = 0.58,
                     ensemble_grade: str = None, checklist_grade: str = None,
                     final_entry: bool = False, check_values: dict = None,
                     entry_block_reason: str = "", qty_entry_final: int = None,
                     hurst: float = None, atr: float = None, regime: str = None,
                     kelly_advised_skip: bool = False):
        """진입 관리 패널 업데이트"""
        self._win.entry_panel.update_data(
            signal, conf, grade, checks, qty=qty,
            final_signal=final_signal,
            reverse_enabled=reverse_enabled,
            min_conf=min_conf,
            ensemble_grade=ensemble_grade,
            checklist_grade=checklist_grade,
            final_entry=final_entry,
            check_values=check_values,
            entry_block_reason=entry_block_reason,
            qty_entry_final=qty_entry_final,
            hurst=hurst,
            atr=atr,
            regime=regime,
            kelly_advised_skip=kelly_advised_skip,
        )

    def set_reverse_entry_enabled(self, enabled: bool, emit_signal: bool = False) -> None:
        self._win.entry_panel.set_reverse_entry_enabled(enabled, emit_signal=emit_signal)

    def is_reverse_entry_enabled(self) -> bool:
        return self._win.entry_panel.is_reverse_entry_enabled()

    def set_contrarian_hint(self, active: bool, direction: str = "") -> None:
        """Contrarian ACTIVE 시 역방향 버튼 황색 깜빡임 힌트 전달."""
        self._win.entry_panel.set_contrarian_hint(active, direction)

    def set_trend_gate_mode(self, mode: str) -> None:
        """추세 지속 게이트 활성화 — 등급 카드 테두리 깜빡임.
        mode: 'UP' (상방 원웨이, 녹색) / 'DN' (하방 원웨이, 오렌지) / '' (해제)"""
        self._win.entry_panel.set_trend_gate_mode(mode)

    def update_layer2(self, status_dict: dict, min_conf_base: float = 0.58) -> None:
        """Layer 2 Intraday Gate 패널 갱신 — IntradayTacticalRegime.status_dict() 를 넘겨줌."""
        self._win.entry_panel.update_layer2(status_dict, min_conf_base=min_conf_base)


    def is_layer2_gate_enabled(self) -> bool:
        """Layer 2 게이트 UI 토글 상태 반환."""
        return self._win.entry_panel.is_layer2_gate_enabled()

    def set_tp1_protect_mode(self, mode: str, emit_signal: bool = False) -> None:
        self._win.exit_panel.set_tp1_protect_mode(mode, emit_signal=emit_signal)

    def get_tp1_protect_mode(self) -> str:
        return self._win.exit_panel.get_tp1_protect_mode()

    def get_entry_mode(self) -> str:
        return self._win.entry_panel.get_entry_mode()

    def is_auto_enabled(self) -> bool:
        return self._win.entry_panel.is_auto_enabled()

    def get_max_qty(self) -> int:
        return self._win.entry_panel.get_max_qty()

    def get_disabled_gates(self) -> set:
        """체크박스 OFF 항목의 내부 키 집합 반환"""
        return self._win.entry_panel.get_disabled_gates()

    def update_entry_stats(self, trades: int, wins: int, pnl_pts: float):
        """당일 진입 통계 갱신"""
        self._win.entry_panel.update_stats(trades, wins, pnl_pts)

    def update_divergence(self, div_data: dict):
        """다이버전스 패널 업데이트"""
        self._win.div_panel.update_data(div_data)

    def update_option_chain(self, chain_feats: dict) -> None:
        """옵션 체인 스냅샷 패널 업데이트"""
        try:
            self._win.div_panel.update_option_chain(chain_feats)
        except Exception:
            pass
        self._update_gamma_badge(chain_feats)

    def update_rv_iv_spread(self, features: dict) -> None:
        """RV-IV 스프레드 카드 업데이트 (328차, 매분 STEP4 이후 호출)"""
        try:
            self._win.div_panel.update_rv_iv(features)
        except Exception:
            pass

    # ±1B 이내를 플립 경계(GEX 중립선 근접)로 판정
    _GEX_FLIP_THRESHOLD = 1.0

    def _update_gamma_badge(self, chain_feats: dict) -> None:
        """헤더 감마 배지를 GEX 부호/크기로 갱신.

        상태 판정:
          opt_chain_available == 0  → 미수집, 이전 상태 유지
          |gex_bn| < ±1B            → 감마플립 (GEX 중립선 근처, 방향 전환 주의)
          gex_sign < 0              → 감마스퀴즈 (딜러 숏감마, 추세 가속)
          gex_sign > 0              → 중립 (딜러 감마롱, 변동성 억제)
        """
        lbl = getattr(self._win, "lbl_gamma", None)
        if lbl is None:
            return
        if not chain_feats.get("opt_chain_available"):
            return  # 미수집 시 이전 배지 유지

        gex_bn   = float(chain_feats.get("opt_gex_bn",   0) or 0)
        gex_sign = float(chain_feats.get("opt_gex_sign", 0) or 0)

        if abs(gex_bn) < self._GEX_FLIP_THRESHOLD:
            state, bg, fg = "감마플립",   C["yellow"], "#000"
        elif gex_sign < 0:
            state, bg, fg = "감마스퀴즈", C["orange"], "#fff"
        else:
            state, bg, fg = "중립",       C["bg3"],    C["text2"]

        lbl.setText(state)
        lbl.setStyleSheet(
            f"background:{bg};color:{fg};border-radius:{S.p(3)}px;"
            f"font-size:{S.f(11)}px;font-weight:bold;padding:1px 6px;"
        )

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

    def update_runtime_health(self, data: dict) -> None:
        """운영 헬스 탭 지표 갱신 + 레벨별 로그 append."""
        latency_ms = float(data.get("latency_ms", 0.0) or 0.0)
        quality_score = float(data.get("quality_score", 1.0) or 0.0)
        cache_age_sec = float(data.get("cache_age_sec", 0.0) or 0.0)
        exception_density_10m = float(data.get("exception_density_10m", 0.0) or 0.0)
        trend_window_min = int(data.get("trend_window_min", 30) or 30)
        health_level = str(data.get("health_level", "INFO") or "INFO")
        degraded_mode = bool(data.get("degraded_mode", False))
        thresholds = data.get("thresholds") or {}

        # 로그 패널 업데이트
        self._win.log_panel.update_health_metrics(
            latency_ms, quality_score, cache_age_sec, exception_density_10m,
            trend_window_min, health_level, degraded_mode, thresholds,
        )


    def append_health_log(self, msg: str, level: str = "INFO"):
        """창6 운영 헬스 로그."""
        tag = {"WARNING": "WARN"}.get(level, level)
        tag = tag if tag in ("WARN", "ERROR", "CRITICAL") else "HEALTH"
        self._win.log_panel.append("health", tag, msg)

    def update_shap(self, *args, **kwargs):
        """SHAP 피처 패널 업데이트"""
        self._win.feat_panel.update_shap(*args, **kwargs)

    def set_model_status(self, state, detail="", progress=-1, price=None,
                         update_signal=True):
        """모델 학습 상태를 예측 패널에 표시."""
        self._win.pred_panel.set_model_status(
            state, detail, progress, price, update_signal
        )

    def append_trade_log(self, msg: str, val: str = ""):
        """창3 주문/체결 로그"""
        self._win.log_panel.append("order", "TRADE", msg, val)

    def update_model_cards(self, accuracy: float, sgd_weight: float, is_active: bool):
        """창5 모델 AI 카드 갱신"""
        self._win.log_panel.update_model_cards(accuracy, sgd_weight, is_active)

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

    def update_recent_ev(self, cnt: int, avg_net_pnl_krw: float, win_rate: float):
        """[260704 감사 P0] 창4 최근20건 순EV 타일 갱신"""
        self._win.log_panel.update_recent_ev(cnt, avg_net_pnl_krw, win_rate)

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
            report_history      list[dict]  A/B·calibration·meta·rollout 스냅샷 이력
            ab_metrics          dict   microstructure_ab_metrics.json
            calibration_metrics dict   calibration_metrics.json
            meta_metrics        dict   meta_gate_tuning_metrics.json
            rollout_metrics     dict   rollout_readiness_metrics.json
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

    def set_challenger_engine(self, engine, promotion_manager=None):
        """챔피언-도전자 엔진 주입 (main.py에서 초기화 후 호출)"""
        panel = getattr(self._win, "challenger_panel", None)
        if panel is not None:
            panel._engine = engine
            if promotion_manager is not None:
                panel._promo = promotion_manager
            panel.refresh()

    def set_profit_guard(self, guard):
        """수익 보존 가드 인스턴스 주입 (main.py 초기화 후 호출)"""
        panel = getattr(self._win, "profit_guard_panel", None)
        if panel is not None:
            panel.set_profit_guard(guard)
        
        # L2 배지 초기화
        self._profit_guard = guard
        self._init_l2_halt_badge()

    def _init_l2_halt_badge(self):
        """L2 배지 초기화 (최초 한 번만)"""
        if hasattr(self, '_profit_guard') and self._profit_guard is not None:
            try:
                l2_info = self._profit_guard.get_l2_halt_info()
                self.update_l2_halt_badge(
                    is_halted=l2_info['is_halted'],
                    threshold=l2_info['halt_threshold']
                )
            except Exception:
                pass

    def refresh_profit_guard(self, daily_pnl_krw: float, today_trades: list):
        """매분 파이프라인 완료 후 수익 가드 패널 갱신."""
        panel = getattr(self._win, "profit_guard_panel", None)
        if panel is not None:
            try:
                panel.refresh(daily_pnl_krw, today_trades)
            except Exception:
                pass


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


def _adapter_toggle_minute_chart_dialog(self):
    self._win.toggle_minute_chart_dialog()


def _adapter_minute_chart_tick(self, price: float, ts=None):
    self._win.minute_chart_tick(price, ts=ts)


def _adapter_minute_chart_candle_closed(self, candle: dict):
    self._win.minute_chart_candle_closed(candle)


def _adapter_minute_chart_set_regime(self, ts_key: str, regime: str):
    self._win.minute_chart_set_regime(ts_key, regime)


def _adapter_minute_chart_set_direction(self, ts_key: str, direction: int):
    self._win.minute_chart_set_direction(ts_key, direction)


def _adapter_minute_chart_record_entry(self, direction: str, price: float, ts=None):
    self._win.minute_chart_record_entry(direction, price, ts=ts)


def _adapter_minute_chart_record_exit(
    self,
    price: float,
    ts=None,
    finalize: bool = True,
    pnl_pts: float = None,
    reason: str = "",
    direction: str = "",
):
    self._win.minute_chart_record_exit(
        price,
        ts=ts,
        finalize=finalize,
        pnl_pts=pnl_pts,
        reason=reason,
        direction=direction,
    )


def _adapter_minute_chart_sync_active_position(self, direction: str, price: float, ts=None):
    self._win.minute_chart_sync_active_position(direction, price, ts=ts)


def _adapter_minute_chart_clear_active_position(self):
    self._win.minute_chart_clear_active_position()


def _adapter_set_minute_chart_post_reload_hook(self, hook):
    """리로드 완료 후 호출될 콜백 등록. active position 재동기화 등 외부 상태 복원에 사용."""
    self._win._minute_chart_dialog._post_reload_hook = hook


def _adapter_push_direction_live(self, decision: dict, ts: str) -> None:
    """파이프라인 실시간 앙상블 결과를 방향카드에 즉시 반영 (DB 폴링 우회)."""
    try:
        self._win.pred_panel._dir_indicator.push_live(decision, ts)
    except Exception:
        pass


DashboardAdapter.toggle_minute_chart_dialog = _adapter_toggle_minute_chart_dialog
DashboardAdapter.minute_chart_tick = _adapter_minute_chart_tick
DashboardAdapter.minute_chart_candle_closed = _adapter_minute_chart_candle_closed
DashboardAdapter.minute_chart_set_regime = _adapter_minute_chart_set_regime
DashboardAdapter.minute_chart_set_direction = _adapter_minute_chart_set_direction
DashboardAdapter.minute_chart_record_entry = _adapter_minute_chart_record_entry
DashboardAdapter.minute_chart_record_exit = _adapter_minute_chart_record_exit
DashboardAdapter.minute_chart_sync_active_position = _adapter_minute_chart_sync_active_position
DashboardAdapter.minute_chart_clear_active_position = _adapter_minute_chart_clear_active_position
DashboardAdapter.set_minute_chart_post_reload_hook = _adapter_set_minute_chart_post_reload_hook
DashboardAdapter.push_direction_live = _adapter_push_direction_live


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
