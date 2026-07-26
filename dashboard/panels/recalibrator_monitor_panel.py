# dashboard/panels/recalibrator_monitor_panel.py — 재보정 모니터 통합 패널
"""
RecalibratorMonitorPanel:
  이 프로젝트의 "제안만, 자동반영 없음" 원칙을 공유하는 재보정/재검증 모니터를
  하위 탭으로 묶어 한 화면에서 확인한다.

    - 임계값(HORIZON_THRESHOLDS)        — ThresholdRecalibrator      (기존 ThresholdMonitorPanel 재사용)
    - ATR 상/하한(ATR_MAX_ENTRY 등)     — ATRCeilingRecalibrator     (ATRCeilingMonitorPanel)
    - 진입호라이즌(ENTRY_HORIZON_B1/B2) — EntryHorizonRecalibrator   (EntryHorizonMonitorPanel)
    - ATR배수 3종 발동률 드리프트       — ATRMultipleRecalibrator    (ATRMultipleMonitorPanel)
    - 26주 WFA 재검증 알림(Hurst/PSI)   — 캘린더 알림, DB 미사용     (WFARecheckPanel)

앞 4개는 daily_close() 에서 매주 금요일(또는 마지막 실행 후 N일 경과 시) 실행되어
각자의 DB에 "제안값"/"발동률"만 기록하고, 실제 config/settings.py 반영은 사람이
수동으로 검토·결정한다. 마지막(WFA 재검증 알림)은 26주 캘린더 카운트다운만 표시.
"""
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

logger = logging.getLogger("SYSTEM")


class RecalibratorMonitorPanel(QWidget):
    """3개 재보정 모니터(threshold/atr_ceiling/entry_horizon) 통합 컨테이너."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        tabs = QTabWidget(self)
        tabs.setStyleSheet(
            "QTabWidget::pane{border:1px solid #30363d;}"
            "QTabBar::tab{background:#161b22;color:#8b949e;padding:6px 14px;}"
            "QTabBar::tab:selected{background:#0d1117;color:#e6edf3;}"
        )

        try:
            from dashboard.panels.threshold_monitor_panel import ThresholdMonitorPanel
            tabs.addTab(ThresholdMonitorPanel(), "임계값 (HORIZON_THRESHOLDS)")
        except Exception as exc:
            logger.warning("[RecalibratorMonitor] ThresholdMonitorPanel 로드 실패: %s", exc)

        try:
            from dashboard.panels.atr_ceiling_monitor_panel import ATRCeilingMonitorPanel
            tabs.addTab(ATRCeilingMonitorPanel(), "ATR 상/하한 (ATR_MAX_ENTRY)")
        except Exception as exc:
            logger.warning("[RecalibratorMonitor] ATRCeilingMonitorPanel 로드 실패: %s", exc)

        try:
            from dashboard.panels.entry_horizon_monitor_panel import EntryHorizonMonitorPanel
            tabs.addTab(EntryHorizonMonitorPanel(), "진입호라이즌 (ENTRY_HORIZON_B1/B2)")
        except Exception as exc:
            logger.warning("[RecalibratorMonitor] EntryHorizonMonitorPanel 로드 실패: %s", exc)

        try:
            from dashboard.panels.atr_multiple_monitor_panel import ATRMultipleMonitorPanel
            tabs.addTab(ATRMultipleMonitorPanel(), "ATR배수 3종 (CHASE/COUNTERTREND/탈진)")
        except Exception as exc:
            logger.warning("[RecalibratorMonitor] ATRMultipleMonitorPanel 로드 실패: %s", exc)

        try:
            from dashboard.panels.wfa_recheck_panel import WFARecheckPanel
            tabs.addTab(WFARecheckPanel(), "26주 WFA 재검증 (Hurst/PSI)")
        except Exception as exc:
            logger.warning("[RecalibratorMonitor] WFARecheckPanel 로드 실패: %s", exc)

        root.addWidget(tabs)
