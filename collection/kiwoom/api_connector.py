# collection/kiwoom/api_connector.py — 키움 OpenAPI+ 연결 관리
"""
키움 OpenAPI+ COM/OCX 래퍼.
- Python 3.7 32-bit + PyQt5 환경 전용
- 로그인 / TR 요청 / 실시간 등록·해제
- TR 요청은 QEventLoop로 블로킹 → 호출 측에서 쓰레드 고려 필요 없음
"""

import datetime
import logging
import time
from typing import Dict, Optional, Callable, List

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication

from config import settings
from config.constants import (
    FID_FUTURES_PRICE, FID_FUTURES_VOL,
    FID_BID_PRICE, FID_ASK_PRICE,
    FID_BID_QTY, FID_ASK_QTY, FID_OI,
    RT_FUTURES, RT_FUTURES_HOGA,
)

logger  = logging.getLogger(__name__)
sys_log = logging.getLogger("SYSTEM")   # 실시간 콜백 추적 → SYSTEM.log

# ── 키움 OCX ProgID ────────────────────────────────────────────
KIWOOM_OCX = "KHOPENAPI.KHOpenAPICtrl.1"

# 실시간 등록 시 기본 FID 목록
DEFAULT_REAL_FIDS = ";".join(str(f) for f in [
    FID_FUTURES_PRICE, FID_FUTURES_VOL,
    FID_BID_PRICE, FID_ASK_PRICE,
    FID_BID_QTY, FID_ASK_QTY, FID_OI,
])

# TR 요청 간 최소 간격 (키움 제한: 초당 5회 이하)
TR_REQUEST_INTERVAL = 0.22   # 220 ms


class KiwoomAPI(QAxWidget):
    """
    키움 OpenAPI+ OCX 래퍼.

    사용 예::

        app = QApplication(sys.argv)
        api = KiwoomAPI()
        api.login()          # 블로킹 — 로그인 완료까지 대기
        data = api.request_tr(
            tr_code="OPT50029",
            rq_name="1min_candle",
            inputs={"종목코드": "A0166000", "시간단위": "1"},
            screen_no="2000",
        )
    """

    # ── 공개 시그널 ────────────────────────────────────────────
    # login_event: QAxWidget 메타클래스가 COM OCX 시그널과 충돌 → 제거
    # 로그인 결과는 login() 반환값 및 is_connected 프로퍼티로 확인
    # 외부에서 로그인 이벤트 필요 시 OnEventConnect 직접 연결
    tr_data_event    = pyqtSignal(str, str, str, str, str, int, str, str, str)
    real_data_event  = pyqtSignal(str, str, str)  # sCode, sRealType, sRealData
    msg_event        = pyqtSignal(str, str, str, str)  # sScreenNo, sRQName, sTrCode, sMsg

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setControl(KIWOOM_OCX)

        self._connected: bool = False
        self._login_err_code: int = -1
        self._last_tr_time: float = 0.0
        self._tr_data_buffer: Dict = {}
        self._tr_loop: Optional[QEventLoop] = None
        self._login_loop: Optional[QEventLoop] = None
        self._real_callbacks: Dict[tuple, List[Callable]] = {}

        self.OnEventConnect.connect(self._on_event_connect)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.OnReceiveRealData.connect(self._on_receive_real_data)
        self.OnReceiveMsg.connect(self._on_receive_msg)

        logger.info("KiwoomAPI 초기화 완료")

    # ── 로그인 ─────────────────────────────────────────────────

    def login(self, timeout_sec: int = 60) -> bool:
        """
        로그인 창을 띄우고 완료까지 블로킹.
        이미 연결된 경우 즉시 True 반환.
        """
        if self._connected:
            logger.info("이미 로그인 상태")
            return True

        self._login_loop = QEventLoop()

        ret = self.dynamicCall("CommConnect()")
        if ret != 0:
            logger.error("CommConnect 실패: %d", ret)
            self._login_loop = None
            return False

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._login_loop.quit)
        timer.start(timeout_sec * 1000)

        self._login_loop.exec_()
        timer.stop()
        self._login_loop = None

        # COM 이벤트 완전 복귀 후 안전하게 dynamicCall 호출
        if self._connected:
            user   = self.get_login_info("USER_NAME")
            server = self.get_login_info("GetServerGubun")
            server_label = "모의투자" if server == "1" else "실서버"
            logger.info("로그인 성공 — 사용자: %s  서버: %s", user, server_label)
            print(f"[DBG LOGIN] user={user!r} server_gubun={server!r} ({server_label})", flush=True)
            if server == "1":
                print("[DBG LOGIN] ★★★ 모의투자 서버 — 선물 SetRealReg 실시간 틱 수신 불가 ★★★", flush=True)
                logger.warning("[서버] 모의투자 서버 접속 — 선물 실시간 틱(SetRealReg) 미지원. OPT50029 폴링 필요")
        else:
            err = getattr(self, "_login_err_code", -1)
            if err == -1:
                logger.error("로그인 타임아웃 (%ds)", timeout_sec)
            else:
                logger.error("로그인 실패 — 에러코드: %d", err)
        return self._connected

    def logout(self) -> None:
        """실시간 등록 전체 해제 후 연결 종료."""
        self.dynamicCall("SetRealRemoveAll()")
        self._connected = False
        logger.info("로그아웃 완료")

    # ── 계좌 조회 ──────────────────────────────────────────────

    def get_login_info(self, tag: str) -> str:
        """
        로그인 정보 조회.
        tag: ACCOUNT_CNT, ACCNO, USER_ID, USER_NAME, GetServerGubun 등
        """
        return self.dynamicCall("GetLoginInfo(QString)", tag).strip()

    def get_account_list(self) -> List[str]:
        """보유 계좌 목록 반환."""
        raw = self.get_login_info("ACCNO")
        return [a for a in raw.split(";") if a]

    # ── TR 요청 ────────────────────────────────────────────────

    def request_tr(
        self,
        tr_code: str,
        rq_name: str,
        inputs: Dict[str, str],
        screen_no: str = "2000",
        prev_next: int = 0,
        timeout_sec: int = 10,
    ) -> Optional[Dict]:
        """
        TR 요청 → 응답까지 블로킹.

        Returns
        -------
        dict  키: "rows" → list[dict]  (각 행의 {필드명: 값})
              None  타임아웃 또는 오류
        """
        self._throttle_tr()

        for key, val in inputs.items():
            self.dynamicCall("SetInputValue(QString, QString)", key, val)

        self._tr_data_buffer[rq_name] = None
        self._tr_loop = QEventLoop()

        print(f"[DBG TR-1] CommRqData 직전 tr={tr_code} rq={rq_name}", flush=True)
        ret = self.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            rq_name, tr_code, prev_next, screen_no,
        )
        print(f"[DBG TR-2] CommRqData 반환={ret}", flush=True)
        if ret != 0:
            logger.error("CommRqData 실패 [%s/%s]: %d", tr_code, rq_name, ret)
            self._tr_loop = None
            return None

        print(f"[DBG TR-3] TR QEventLoop.exec_() 진입", flush=True)
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._tr_loop.quit)
        timer.start(timeout_sec * 1000)

        self._tr_loop.exec_()
        timer.stop()
        self._tr_loop = None
        print(f"[DBG TR-4] TR QEventLoop 종료", flush=True)

        # 메타데이터만 저장된 버퍼를 pop — None이면 타임아웃
        meta = self._tr_data_buffer.pop(rq_name, None)
        if meta is None:
            logger.warning("TR 타임아웃 [%s/%s]", tr_code, rq_name)
            print(f"[DBG TR-5] request_tr 타임아웃", flush=True)
            return None

        # COM 이벤트 완전 복귀 후 — GetRepeatCnt/GetCommData 안전하게 호출
        # GetRepeatCnt(sTrCode, sRecordName) — record_name은 콜백에서 수신한 값
        # GetCommData(sTrCode, sRQName, nIndex, sItem) — rq_name 사용
        actual_tr     = meta.get("tr_code", tr_code)
        actual_record = meta.get("record_name", "")   # 빈 문자열 그대로 전달 (OPT50029 등)
        n_rows = self.get_repeat_cnt(actual_tr, actual_record)
        print(f"[DBG TR-5] GetRepeatCnt={n_rows} tr={actual_tr} record={actual_record!r}", flush=True)
        rows = [self._parse_tr_row(actual_tr, rq_name, i) for i in range(n_rows)]
        result = {
            "rows":      rows,
            "prev_next": meta.get("prev_next", "0"),
            "tr_code":   actual_tr,
        }
        print(f"[DBG TR-6] request_tr 완료 rows={len(rows)}", flush=True)
        return result

    # ── 실시간 등록 ────────────────────────────────────────────

    def register_realtime(
        self,
        code: str,
        real_type: str,
        screen_no: str = "3000",
        fid_list: Optional[str] = None,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        실시간 데이터 수신 등록.

        Parameters
        ----------
        code       종목 코드 (예: "101W06")
        real_type  실시간 타입 (예: RT_FUTURES = "FC0")
        screen_no  화면 번호 (4자리)
        fid_list   FID 문자열 (기본값: DEFAULT_REAL_FIDS)
        callback   (code, real_type, real_data) → None
        """
        fids = fid_list or DEFAULT_REAL_FIDS
        # sOptType "0" = 기존 등록 초기화 후 등록, "1" = 기존 유지 추가
        ret = self.dynamicCall(
            "SetRealReg(QString, QString, QString, QString)",
            screen_no, code, fids, "0",
        )
        print(f"[DBG RT-REG] SetRealReg ret={ret} code={code!r} type={real_type!r} screen={screen_no!r} fids={fids}", flush=True)
        if callback is not None:
            key = (code.strip(), real_type.strip())
            self._real_callbacks.setdefault(key, []).append(callback)
            print(f"[DBG RT-REG] 콜백 등록 key={key!r}  전체등록키={list(self._real_callbacks.keys())}", flush=True)
        logger.info("실시간 등록: code=%s type=%s screen=%s ret=%s", code, real_type, screen_no, ret)

    def unregister_realtime(self, code: str, screen_no: str = "3000") -> None:
        """특정 종목 실시간 해제."""
        self.dynamicCall("SetRealRemove(QString, QString)", screen_no, code)
        # 콜백도 정리
        keys_to_del = [k for k in self._real_callbacks if k[0] == code]
        for k in keys_to_del:
            del self._real_callbacks[k]
        logger.info("실시간 해제: code=%s screen=%s", code, screen_no)

    # ── 실시간 데이터 조회 ────────────────────────────────────

    def get_real_data(self, code: str, fid: int) -> str:
        """OnReceiveRealData 콜백 내부에서 호출."""
        return self.dynamicCall("GetCommRealData(QString, int)", code, fid).strip()

    # ── TR 응답 데이터 파싱 ───────────────────────────────────

    def get_comm_data(
        self,
        tr_code: str,
        rq_name: str,
        index: int,
        item: str,
    ) -> str:
        return self.dynamicCall(
            "GetCommData(QString, QString, int, QString)",
            tr_code, rq_name, index, item,
        ).strip()

    def get_repeat_cnt(self, tr_code: str, rq_name: str) -> int:
        return int(self.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, rq_name))

    # ── 종목 코드 유틸 ────────────────────────────────────────

    def get_nearest_futures_code(self) -> str:
        """KOSPI200 선물 근월물 코드 반환.

        우선순위:
          0. GetFutureCodeByIndex(0) — KOA 공식 근월물 직접 반환
          1. GetFutureList()         — 선물 전용 API (전체 목록)
          2. GetMasterCodeList("10") — 구형 방식, 모의투자에서 빈값 가능
          3. 날짜 계산               — 항상 성공 (fallback)
        """
        # 0순위: GetFutureCodeByIndex(0) — 근월물 직접 반환
        try:
            code = self.dynamicCall("GetFutureCodeByIndex(int)", 0).strip()
            print(f"[DBG FC] GetFutureCodeByIndex(0)='{code}'", flush=True)
            if code:
                logger.info("근월물 코드 (GetFutureCodeByIndex): %s", code)
                return code
        except Exception as e:
            print(f"[DBG FC] GetFutureCodeByIndex 예외: {e}", flush=True)

        # 1순위: GetFutureList()
        raw = self.dynamicCall("GetFutureList()")
        raw_preview = (raw[:300] if raw else "")
        print(f"[DBG FC] GetFutureList() raw='{raw_preview}'", flush=True)
        if raw:
            all_codes  = [c for c in raw.strip().split(";") if c]
            w_codes    = sorted(c for c in all_codes if c.startswith("101W"))
            first5     = all_codes[:5]
            print(f"[DBG FC] GetFutureList 전체앞5={first5}  101W*={w_codes}", flush=True)
            if w_codes:
                logger.info("근월물 코드 (GetFutureList): %s", w_codes[0])
                return w_codes[0]

        # 2순위: GetMasterCodeList("10")
        raw = self.dynamicCall("GetMasterCodeList(QString)", "10")
        raw_preview = (raw[:300] if raw else "")
        print(f"[DBG FC] GetMasterCodeList('10') raw='{raw_preview}'", flush=True)
        if raw:
            all_codes = [c for c in raw.strip().split(";") if c]
            w_codes   = sorted(c for c in all_codes if c.startswith("101W"))
            first5    = all_codes[:5]
            print(f"[DBG FC] GetMasterCodeList 전체앞5={first5}  101W*={w_codes}", flush=True)
            if w_codes:
                logger.info("근월물 코드 (GetMasterCodeList): %s", w_codes[0])
                return w_codes[0]

        # 3순위: 날짜 계산 — fallback
        code = self._nearest_futures_code_by_date()
        print(f"[DBG FC] 날짜계산 fallback code='{code}'", flush=True)
        logger.info("근월물 코드 (날짜계산): %s", code)
        return code

    def get_realtime_futures_code(self) -> str:
        """SetRealReg 실시간 구독용 101W 형식 코드.

        OPT50029(분봉 TR)는 A0166000 형식, SetRealReg는 101W 형식이 필요하다.
        날짜 계산으로 항상 101W 형식을 반환한다.
        """
        code = self._nearest_futures_code_by_date()
        print(f"[DBG FC] 실시간코드(101W 형식)='{code}'", flush=True)
        logger.info("실시간 구독 코드: %s", code)
        return code

    def _nearest_futures_code_by_date(self) -> str:
        """현재 날짜 기준 KOSPI200 선물 근월물 코드.

        만기: 3·6·9·12월 두 번째 목요일.
        코드 형식: 101W + MM (예: 101W06 = 6월물).
        """
        today = datetime.date.today()
        for month in (3, 6, 9, 12):
            if month < today.month:
                continue
            expiry = self._second_thursday(today.year, month)
            if today <= expiry:
                return f"101W{month:02d}"
        # 12월 만기일 이후 → 내년 3월물
        return "101W03"

    @staticmethod
    def _second_thursday(year: int, month: int) -> datetime.date:
        """해당 연월의 두 번째 목요일 반환 (KOSPI200 선물 만기일)."""
        first = datetime.date(year, month, 1)
        offset = (3 - first.weekday()) % 7   # 첫 번째 목요일까지 일수
        return first + datetime.timedelta(days=offset + 7)

    # ── 내부 이벤트 핸들러 ────────────────────────────────────

    def _on_event_connect(self, err_code: int) -> None:
        # COM 콜백 내부: 상태 저장만, dynamicCall/pyqtSignal.emit 금지 (스택 오버런)
        self._connected = (err_code == 0)
        self._login_err_code = err_code
        if self._login_loop is not None:
            self._login_loop.quit()

    def _on_receive_tr_data(
        self,
        screen_no: str,
        rq_name: str,
        tr_code: str,
        record_name: str,
        prev_next: str,
        data_len: int,
        _error_code: str,
        _message: str,
        _splm_message: str,
    ) -> None:
        print(f"[DBG CB-TR] _on_receive_tr_data 진입 tr={tr_code} rq={rq_name} record={record_name!r} prev_next={prev_next!r}", flush=True)
        # COM 콜백: 상태 저장만, dynamicCall/emit 금지
        self._tr_data_buffer[rq_name] = {
            "tr_code":     tr_code,
            "prev_next":   prev_next,
            "screen_no":   screen_no,
            "record_name": record_name,
            "data_len":    data_len,
        }
        print(f"[DBG CB-TR] _tr_data_buffer 저장 완료, loop.quit 직전", flush=True)
        if self._tr_loop is not None:
            self._tr_loop.quit()
        print(f"[DBG CB-TR] _on_receive_tr_data 완료", flush=True)

    def _on_receive_real_data(
        self, code: str, real_type: str, real_data: str
    ) -> None:
        # 처음 수신되는 (code, real_type) 조합을 SYSTEM.log에 1회 기록
        key_stripped = (code.strip(), real_type.strip())
        if not hasattr(self, "_logged_rt_keys"):
            self._logged_rt_keys = set()
        if key_stripped not in self._logged_rt_keys:
            sys_log.info("[RT-CB] 새 실시간 키 수신 code=%r type=%r | 등록키=%s",
                         code, real_type, list(self._real_callbacks.keys()))
            self._logged_rt_keys.add(key_stripped)

        key_raw = (code, real_type)
        cbs = self._real_callbacks.get(key_raw) or self._real_callbacks.get(key_stripped, [])
        for cb in cbs:
            try:
                cb(code, real_type, real_data)
            except Exception:
                logger.exception("실시간 콜백 오류 [%s/%s]", code, real_type)
        print(f"[DBG CB-RT] 완료", flush=True)

    def _on_receive_msg(
        self, _screen_no: str, rq_name: str, tr_code: str, msg: str
    ) -> None:
        print(f"[DBG CB-MSG] _on_receive_msg tr={tr_code} msg={msg[:40]}", flush=True)
        logger.debug("TR 메시지 [%s/%s]: %s", tr_code, rq_name, msg)

    # ── 헬퍼 ──────────────────────────────────────────────────

    def _throttle_tr(self) -> None:
        """TR 요청 간격 강제 준수 (키움 초당 5회 제한)."""
        elapsed = time.time() - self._last_tr_time
        if elapsed < TR_REQUEST_INTERVAL:
            time.sleep(TR_REQUEST_INTERVAL - elapsed)
        self._last_tr_time = time.time()

    def _parse_tr_row(self, tr_code: str, rq_name: str, index: int) -> Dict[str, str]:
        """TR 응답 한 행을 {항목명: 값} dict로 반환."""
        if tr_code.upper() == "OPT50029":
            # 선물분차트요청 출력 필드
            fields = ["체결시간", "현재가", "시가", "고가", "저가", "거래량"]
        else:
            fields = []
        return {
            f: self.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                tr_code, rq_name, index, f,
            ).strip()
            for f in fields
        }

    # ── 연결 상태 ─────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        state = int(self.dynamicCall("GetConnectState()"))
        return state == 1
