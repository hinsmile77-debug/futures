# dashboard/panels/conf_trend_widget.py
"""
금일 conf → 진입단계 추적 위젯 (독립 임베드용).

DynamicMcPanel 내 같은 카드의 독립 사본 — 동일 DB를 읽어 30초마다 자동 갱신.
DynamicMcPanel 코드를 일절 변경하지 않는다.
"""
import datetime
import json
import logging
import os
import re
import sqlite3

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config.settings import DB_DIR, LOG_DIR, PREDICTIONS_DB, TRADES_DB

logger = logging.getLogger("SYSTEM")
_MC_HISTORY_DB = os.path.join(DB_DIR, "mc_history.db")

_COL = {
    "bg": "#0d1117", "bg2": "#161b22", "bg3": "#1c2128",
    "border": "#30363d", "text": "#e6edf3", "muted": "#8b949e",
    "green": "#3fb950", "yellow": "#e3b341", "orange": "#d29922",
    "red": "#f85149", "blue": "#58a6ff", "purple": "#bc8cff",
}

_TABLE_STYLE = (
    "QTableWidget {"
    " background:%s; color:%s; gridline-color:%s;"
    " border:1px solid %s; font-size:11px;"
    " selection-background-color:%s; selection-color:%s; }"
    "QHeaderView::section {"
    " background:%s; color:%s; border:none;"
    " padding:4px 6px; font-size:11px; font-weight:bold; }"
) % (
    _COL["bg2"], _COL["text"], _COL["border"], _COL["border"],
    _COL["bg3"], _COL["text"], _COL["bg3"], _COL["muted"],
)

_GATE_CHECK_LABELS = {
    "cb_normal":        "Circuit Breaker 정상",
    "hc_ok":            "고신뢰 연속오답 차단 없음",
    "new_entry_time":   "신규진입 시간대 (15:00 이전)",
    "broker_sync_ok":   "브로커 sync 검증됨",
    "cooldown_ok":      "ENTRY 타임아웃 쿨다운 해제",
    "exit_cooldown_ok": "청산 후 쿨다운 해제",
    "armistice_ok":     "재시작 유예(Armistice) 해제",
    "integrity_ok":     "포지션 무결성 정상",
    "reverse_clamp_ok": "역방향 클램프 해제",
    "hurst_ok":         "Hurst ≥ 0.45 (추세장)",
    "atr_ok":           "ATR ≥ 최소 변동성",
    "mode_filter_ok":   "등급-진입모드 필터 통과",
    "qty_ok":           "산출수량 > 0",
    "bar_volume_ok":    "분봉 거래량 ≠ 0",
    "intraday_ok":      "IntradayRegime(L2) 허용",
    "kill_switch_ok":   "Early Kill Switch 비활성",
}


class ConfTrendWidget(QWidget):
    """금일 conf → 진입단계 추적 (독립 임베드 위젯)."""

    REFRESH_MS = 30_000
    MAX_ROWS   = 30   # 최근 N봉만 표시 — 전체 표시 시 3310 setItem × setStyleSheet = 73초 블로킹

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(self.REFRESH_MS)
        self._last_pass_style = ""  # setStyleSheet 조건부 적용용
        self._pred_conn = None       # 영구 read 연결 (매 refresh 연결 생성 비용 제거)
        self._log_today  = ""        # 날짜 변경 감지
        self._log_offset = 0         # 마지막 읽은 파일 offset (전체 재읽기 방지)
        self._log_cache  = {}        # 누적 진입완료 맵
        self.refresh()

    def showEvent(self, event):
        """위젯이 표시될 때 즉시 테이블 갱신."""
        super().showEvent(event)
        self.refresh()

    # ── UI 구성 ──────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        self._lbl_today_avg = QLabel("오늘 conf 평균: --")
        self._lbl_today_avg.setStyleSheet("font-size:11px; color:%s;" % _COL["text"])
        self._lbl_today_pass = QLabel("통과율: --")
        self._lbl_today_pass.setStyleSheet("font-size:11px; color:%s;" % _COL["green"])

        sumrow = QHBoxLayout()
        sumrow.addWidget(self._lbl_today_avg)
        sumrow.addStretch()
        sumrow.addWidget(self._lbl_today_pass)
        root.addLayout(sumrow)

        self._table = QTableWidget(0, 10)
        self._table.setHorizontalHeaderLabels([
            "시각", "conf(ema)", "mc", "Δ", "dir", "grade",
            "gate", "meta/tox", "차단사유", "진입단계",
        ])
        hdr = self._table.horizontalHeader()
        for idx in range(7):
            hdr.setSectionResizeMode(idx, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(7, QHeaderView.Stretch)
        hdr.setSectionResizeMode(8, QHeaderView.Stretch)
        hdr.setSectionResizeMode(9, QHeaderView.Stretch)
        self._table.setMinimumHeight(200)
        self._table.setMaximumHeight(16777215)  # 제한 없음 — 부모 레이아웃이 높이 결정
        self._table.setAlternatingRowColors(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setSelectionMode(QTableWidget.NoSelection)
        self._table.setShowGrid(True)
        self._table.verticalHeader().setDefaultSectionSize(22)
        self._table.verticalHeader().setMinimumSectionSize(22)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet(_TABLE_STYLE)
        self._table.setFont(QFont("Consolas", 11))
        root.addWidget(self._table)

    # ── 데이터 갱신 ──────────────────────────────────────────────

    def refresh(self):
        import time as _t, logging as _log
        _t0 = _t.monotonic()
        try:
            self._do_refresh()
        except Exception as e:
            logger.debug("[ConfTrendWidget] refresh error: %s", e)
        _ms = (_t.monotonic() - _t0) * 1000
        if _ms > 200:
            _log.getLogger("SYSTEM").warning("[LiveDBG] ConfTrendWidget.refresh slow %.0fms", _ms)

    def _do_refresh(self):
        import time as _t2, logging as _lg
        _d0 = _t2.monotonic()
        today = datetime.date.today().isoformat()

        try:
            from strategy.entry.time_strategy_router import _ZONE_PARAMS
            fallback_mc = _ZONE_PARAMS.get("STABLE_TREND", {}).get("min_confidence", 0.57)
        except Exception:
            fallback_mc = 0.57
        _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend step1_import %.0fms", (_t2.monotonic()-_d0)*1000)

        _s = _t2.monotonic()
        completed_entries = self._get_completed_entry_map(today)
        _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend step2_completed_map %.0fms", (_t2.monotonic()-_s)*1000)

        rows = []
        try:
            _s = _t2.monotonic()
            _conn = self._get_pred_conn()
            rows = _conn.execute(
                "SELECT ts, direction, confidence, grade, auto_entry, regime_ok, "
                "       min_conf, gate_reason, gate_blocked, meta_action, meta_confidence, "
                "       meta_reason, toxicity_action, toxicity_score, toxicity_reason, "
                "       entry_gate_json, entry_final_ok, entry_qty, entry_mode, "
                "       entry_executed, entry_block_reason, "
                "       checklist_reason "
                "FROM ensemble_decisions "
                "WHERE ts >= ? AND ts < ? ORDER BY ts DESC LIMIT ?",
                (today, today + "Z", self.MAX_ROWS),
            ).fetchall()
            rows = list(reversed(rows))  # 최신 N봉, 오래된 순 정렬
            _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend step3_db_query %.0fms rows=%d", (_t2.monotonic()-_s)*1000, len(rows))
        except Exception as _qe:
            self._pred_conn = None  # 오류 시 재연결 허용
            _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend step3_db_EXCEPTION: %s", _qe)

        if not rows:
            self._table.setRowCount(0)
            return

        confs = [float(r["confidence"]) for r in rows]
        mcs   = [float(r["min_conf"] or fallback_mc) for r in rows]
        avg_c  = sum(confs) / len(confs)
        avg_mc = sum(mcs)   / len(mcs)
        pass_n = sum(1 for r in rows
                     if float(r["confidence"]) >= float(r["min_conf"] or fallback_mc))
        pass_r = pass_n / len(rows) * 100

        self._lbl_today_avg.setText(
            "오늘 conf 평균: <b>%.3f</b>  mc=%.3f  여유:%+.3f"
            % (avg_c, avg_mc, avg_c - avg_mc)
        )
        self._lbl_today_avg.setTextFormat(Qt.RichText)
        self._lbl_today_pass.setText(
            "통과율: <b>%.0f%%</b> (%d/%d봉)" % (pass_r, pass_n, len(rows))
        )
        self._lbl_today_pass.setTextFormat(Qt.RichText)
        _new_style = (
            "font-size:11px; color:%s;"
            % (_COL["green"] if 15 <= pass_r <= 35
               else _COL["yellow"] if pass_r < 15
               else _COL["orange"])
        )
        if _new_style != self._last_pass_style:
            self._lbl_today_pass.setStyleSheet(_new_style)
            self._last_pass_style = _new_style

        # EMA(20) 계산 — 전체 행 대상
        alpha = 2.0 / 21
        ema_val, ema_list = None, []
        for r in rows:
            c = float(r["confidence"])
            ema_val = c if ema_val is None else alpha * c + (1 - alpha) * ema_val
            ema_list.append(ema_val)

        _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend step4_arithmetic %.0fms", (_t2.monotonic()-_d0)*1000)

        # 탭이 보이지 않으면 테이블 업데이트 건너뜀 (600×setItem = 2.4s 블로킹 방지)
        # showEvent에서 다시 refresh()를 호출하므로 데이터 정합성 유지됨
        if not self.isVisible():
            _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend skip_table (not visible) total %.0fms", (_t2.monotonic()-_d0)*1000)
            return

        _s = _t2.monotonic()
        self._table.setUpdatesEnabled(False)
        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            conf  = ema_list[i]
            mc    = float(r["min_conf"] or fallback_mc)
            delta = conf - mc
            ts_str   = r["ts"][11:16]
            direction = self._fmt_direction(r["direction"])
            grade     = str(r["grade"] or "")
            gate      = self._fmt_gate(r["gate_reason"], r["gate_blocked"], conf, mc)
            meta_tox  = self._fmt_meta_tox(
                r["meta_action"], r["meta_confidence"],
                r["toxicity_action"], r["toxicity_score"],
            )
            completed = self._lookup_completed_entry(completed_entries, str(r["ts"]))
            stage, stage_reason = self._resolve_stage(r, conf, mc, completed)
            block_reason = self._resolve_block_reason(r, stage, stage_reason)
            gate_tip = self._entry_gate_tooltip(
                r["entry_gate_json"] if "entry_gate_json" in r.keys() else ""
            )

            conf_bg, conf_fg = self._conf_colors(conf, mc)
            cell_data = [
                (ts_str,              None,                                     conf_bg if False else None, True),
                ("%.3f" % conf,       conf_fg,                                  conf_bg,                   True),
                ("%.3f" % mc,         _COL["text"],                             None,                      True),
                ("%+.3f" % delta,     _COL["green"] if delta >= 0 else _COL["red"], None,                  True),
                (direction,           self._direction_color(direction),         None,                      True),
                (grade,               self._grade_color(grade),                 None,                      True),
                (gate,                self._gate_color(gate),                   None,                      True),
                (meta_tox,            self._meta_color(meta_tox),               None,                      False),
                (block_reason,        self._stage_color(stage),                 None,                      False),
                (stage,               self._stage_color(stage),                 None,                      True),
            ]
            for j, (text, fg, bg, bold) in enumerate(cell_data):
                it = self._table.item(i, j)
                if it is None:
                    # 첫 번째 렌더링: 새 아이템 생성
                    it = self._mk(text, fg=fg, bg=bg, bold=bold)
                    self._table.setItem(i, j, it)
                else:
                    # 이후: 기존 아이템 in-place 업데이트 (setItem() 비용 없음)
                    it.setText(text)
                    if fg:
                        it.setForeground(QColor(fg))
                    if bg is not None:
                        it.setBackground(bg)
                # 툴팁
                if j == 9 and completed:
                    it.setToolTip(self._entry_complete_tooltip(completed))
                elif j in (8, 9) and gate_tip:
                    it.setToolTip(gate_tip)
        self._table.setUpdatesEnabled(True)
        _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend step5_table_update %.0fms", (_t2.monotonic()-_s)*1000)

        # 최신 행(맨 아래)이 항상 보이도록 스크롤
        _s = _t2.monotonic()
        self._table.scrollToBottom()
        _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend step6_scroll %.0fms", (_t2.monotonic()-_s)*1000)
        _lg.getLogger("SYSTEM").warning("[LiveDBG] ConfTrend total %.0fms rows=%d", (_t2.monotonic()-_d0)*1000, len(rows))

    # ── 헬퍼: 영구 read 연결 ─────────────────────────────────────

    def _get_pred_conn(self):
        if self._pred_conn is None:
            conn = sqlite3.connect(PREDICTIONS_DB, timeout=5, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._pred_conn = conn
        return self._pred_conn

    # ── 헬퍼: 진입 완료 맵 ───────────────────────────────────────

    def _get_completed_entry_map(self, today: str) -> dict:
        done = {}
        done.update(self._completed_from_db(today))
        done.update(self._completed_from_log(today))
        return done

    def _completed_from_db(self, today: str) -> dict:
        if not os.path.exists(TRADES_DB):
            return {}
        try:
            conn = sqlite3.connect(TRADES_DB, timeout=5)
            conn.row_factory = sqlite3.Row
            # range 쿼리 사용 — substr() 함수 적용 시 idx_entry_ts 인덱스 미사용 (풀스캔) 방지
            rows = conn.execute(
                "SELECT entry_ts, direction, quantity, grade, had_partial_fill "
                "FROM trades WHERE entry_ts >= ? AND entry_ts < ?",
                (today, today + "Z"),
            ).fetchall()
            conn.close()
        except Exception:
            return {}
        done = {}
        for row in rows:
            ts = row["entry_ts"]
            if not ts:
                continue
            key = str(ts)[:16]
            if not key:
                continue
            done[key] = {
                "direction": row["direction"] or "",
                "quantity": int(row["quantity"] or 0),
                "grade": row["grade"] or "",
                "had_partial_fill": int(row["had_partial_fill"] or 0),
                "source": "trades.db",
                "entry_ts": str(ts),
            }
        return done

    def _completed_from_log(self, today: str) -> dict:
        log_path = os.path.join(LOG_DIR, today.replace("-", "") + "_TRADE.log")
        if not os.path.exists(log_path):
            return {}
        # 날짜가 바뀌면 캐시·offset 초기화
        if today != self._log_today:
            self._log_today  = today
            self._log_offset = 0
            self._log_cache  = {}
        patterns = ("[체결진입]", "[체결진입보정]", "[체결동기화] 외부진입")
        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as fp:
                fp.seek(self._log_offset)          # 마지막으로 읽은 위치부터 시작
                for line in fp:
                    if not any(t in line for t in patterns):
                        continue
                    key = line[:16] if len(line) >= 16 else ""
                    if not key:
                        continue
                    direction, quantity = "", 0
                    if "LONG" in line:
                        direction = "LONG"
                    elif "SHORT" in line:
                        direction = "SHORT"
                    m = re.search(r"(\d+)계약", line)
                    quantity = int(m.group(1)) if m else 0
                    self._log_cache[key] = {
                        "direction": direction,
                        "quantity": quantity,
                        "grade": "",
                        "had_partial_fill": 1 if "보정" in line else 0,
                        "source": os.path.basename(log_path),
                        "entry_ts": line[:19],
                    }
                self._log_offset = fp.tell()       # 다음 호출에서 여기부터 재개
        except Exception:
            pass
        return self._log_cache

    def _lookup_completed_entry(self, completed: dict, ts: str):
        if not completed:
            return None
        try:
            base = datetime.datetime.strptime(str(ts)[:16], "%Y-%m-%d %H:%M")
        except Exception:
            return completed.get(str(ts)[:16])
        for offset in (0, -1, 1, -2, 2):
            key = (base + datetime.timedelta(minutes=offset)).strftime("%Y-%m-%d %H:%M")
            e = completed.get(key)
            if e:
                return e
        return None

    # ── 헬퍼: 포맷 ───────────────────────────────────────────────

    def _fmt_direction(self, d) -> str:
        d = int(d or 0)
        return "UP" if d > 0 else ("DN" if d < 0 else "F")

    def _fmt_gate(self, gate_reason, gate_blocked, conf, mc) -> str:
        if conf < mc:
            return "conf↓"
        if int(gate_blocked or 0):
            return "blocked"
        r = str(gate_reason or "")
        return r[:10] if r and r != "inactive" else "pass"

    def _fmt_meta_tox(self, meta_action, meta_confidence, toxicity_action, toxicity_score) -> str:
        return "%s %.2f / %s %.2f" % (
            str(meta_action or "-"), float(meta_confidence or 0.0),
            str(toxicity_action or "-"), float(toxicity_score or 0.0),
        )

    def _resolve_stage(self, row, conf: float, mc: float, completed=None):
        d       = int(row["direction"] or 0)
        grade   = str(row["grade"] or "")
        gr      = str(row["gate_reason"] or "")
        gb      = int(row["gate_blocked"] or 0)
        ro      = int(row["regime_ok"] or 0)
        ma      = str(row["meta_action"] or "")
        ta      = str(row["toxicity_action"] or "")
        ae      = int(row["auto_entry"] or 0)
        _keys   = row.keys()
        _raw_fo = row["entry_final_ok"] if "entry_final_ok" in _keys else None
        fo      = None if _raw_fo is None else int(_raw_fo)
        ebr     = str(row["entry_block_reason"] or "") if "entry_block_reason" in _keys else ""

        if completed:
            return "10. 진입완료 ✓", ""
        if conf == 0.0 and d == 0 and grade == "X":
            return "0. cold-start 대기", ""
        if conf < mc:
            return "1. conf미달", ""
        if d == 0:
            return "2. Enb Flat", ""
        if grade == "X":
            return "2. Enb X", ""
        if gb or gr == "blocked_by_microstructure":
            return "3. gate차단", ""
        if ro == 0:
            return "4. regime불일치", ""
        if ma == "skip":
            return "5. Meta skip", ""
        if ta == "block":
            return "6. Toxic block", ""
        if ta == "reduce":
            return "6. Toxic reduce", ""
        if ae == 0:
            return "7. Auto 불가", ""
        if fo == 0:
            return "8. STEP7 차단", ebr
        return "9. 진입후보(최종) ▶", ""

    def _resolve_block_reason(self, row, stage: str, detail: str) -> str:
        if stage.startswith("0."):
            return "초기화(cold-start) 대기 중"
        if stage.startswith("1."):
            return "신뢰도 미달 (conf < mc)"
        if stage.startswith("2."):
            _keys = row.keys()
            cr = str(row["checklist_reason"] or "") if "checklist_reason" in _keys else ""
            if "Flat" in stage:
                return "Enb Flat"
            return ("Enb X — " + cr) if cr else "Enb X"
        if stage.startswith("3."):
            gr = str(row["gate_reason"] or "")
            return "마이크로구조 게이트 차단 (%s)" % gr if gr else "마이크로구조 게이트 차단"
        if stage.startswith("4."):
            return "레짐 불일치 (regime_ok=0)"
        if stage.startswith("5."):
            _keys = row.keys()
            mr = str(row["meta_reason"] or "") if "meta_reason" in _keys else ""
            return "MetaGate skip (%s)" % mr if mr else "MetaGate skip"
        if stage.startswith("6."):
            _keys = row.keys()
            tr  = str(row["toxicity_reason"] or "") if "toxicity_reason" in _keys else ""
            ta  = str(row["toxicity_action"] or "")
            return "ToxicityGate %s (%s)" % (ta, tr) if tr else "ToxicityGate %s" % ta
        if stage.startswith("7."):
            return "체크리스트 자동진입 조건 미달 (auto_entry=0)"
        if stage.startswith("8."):
            if detail:
                return detail
            _keys = row.keys()
            cr = str(row["checklist_reason"] or "") if "checklist_reason" in _keys else ""
            return ("Chk X — " + cr) if cr else "STEP7 차단 (상세 미수집)"
        if stage.startswith("9."):
            return "모든 조건 통과 — 진입 대기/실행 중"
        if stage.startswith("10."):
            return "체결 완료"
        return "-"

    def _entry_gate_tooltip(self, gate_json: str) -> str:
        if not gate_json:
            return ""
        try:
            gate = json.loads(gate_json)
        except Exception:
            return ""
        if not gate:
            return ""
        lines = ["STEP7 마스터 게이트 상세"]
        for key, label in _GATE_CHECK_LABELS.items():
            if key in gate:
                lines.append("%s %s" % ("✓" if gate[key] else "✗", label))
        return "\n".join(lines)

    def _entry_complete_tooltip(self, e: dict) -> str:
        return (
            "실제 진입완료 확인\n시각: %s\n방향: %s\n수량: %d계약\n"
            "등급: %s\n부분체결: %s\n근거: %s"
        ) % (
            e.get("entry_ts") or "-", e.get("direction") or "-",
            int(e.get("quantity") or 0), e.get("grade") or "-",
            "예" if int(e.get("had_partial_fill") or 0) else "아니오",
            e.get("source") or "-",
        )

    # ── 헬퍼: 색상 ───────────────────────────────────────────────

    def _conf_colors(self, conf, mc):
        if conf >= mc:
            return QColor("#153624"), _COL["green"]
        if conf >= mc - 0.05:
            return QColor("#3a3012"), _COL["yellow"]
        return QColor("#3a1212"), _COL["red"]

    def _direction_color(self, d: str) -> str:
        return _COL["green"] if d == "UP" else (_COL["blue"] if d == "DN" else _COL["muted"])

    def _grade_color(self, g: str) -> str:
        return _COL["green"] if g in ("A", "B") else (_COL["yellow"] if g == "C" else _COL["red"])

    def _gate_color(self, g: str) -> str:
        if g == "pass":   return _COL["green"]
        if g == "conf↓":  return _COL["red"]
        return _COL["yellow"]

    def _meta_color(self, s: str) -> str:
        if "skip" in s or "block" in s: return _COL["purple"]
        if "reduce" in s:               return _COL["orange"]
        return _COL["muted"]

    def _stage_color(self, s: str) -> str:
        if s.startswith("10.") or s.startswith("9."):  return _COL["green"]
        if s.startswith("8.")  or s.startswith("1."):  return _COL["red"]
        if s.startswith("2."):                          return _COL["orange"]
        if s.startswith("3.")  or s.startswith("4."):  return _COL["yellow"]
        if s.startswith("5.")  or s.startswith("6."):  return _COL["purple"]
        if s.startswith("7."):                          return _COL["blue"]
        return _COL["muted"]

    # ── 헬퍼: 테이블 아이템 ──────────────────────────────────────

    def _mk(self, text: str, fg: str = None, bg: QColor = None, bold: bool = False):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        if fg:
            item.setForeground(QColor(fg))
        if bg is not None:
            item.setBackground(bg)
        if bold:
            f = item.font()
            f.setBold(True)
            item.setFont(f)
        return item


# ── 카드 래퍼 (GroupBox 포함) ─────────────────────────────────────────────────

def make_conf_trend_card(parent=None) -> QGroupBox:
    """제목 GroupBox 포함 카드를 반환한다."""
    box = QGroupBox("금일 conf → 진입단계 추적")
    box.setStyleSheet(
        "QGroupBox { font-size:11px; font-weight:bold; color:#8b949e;"
        " border:1px solid #30363d; border-radius:4px;"
        " margin-top:6px; padding:4px; }"
        "QGroupBox::title { subcontrol-origin:margin; left:8px; padding:0 4px; }"
    )
    lay = QVBoxLayout(box)
    lay.setContentsMargins(4, 6, 4, 4)
    widget = ConfTrendWidget(parent)
    lay.addWidget(widget)
    return box
