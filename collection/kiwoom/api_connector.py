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
from typing import Dict, Optional, Callable, List, Any

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication

from config import settings
from config import secrets as _secrets
from config.constants import (
    FID_FUTURES_PRICE, FID_FUTURES_VOL,
    FID_BID_PRICE, FID_ASK_PRICE,
    FID_BID_QTY, FID_ASK_QTY, FID_OI,
    FUTURES_BID_PRICE_FIDS, FUTURES_ASK_PRICE_FIDS,
    FUTURES_BID_QTY_FIDS, FUTURES_ASK_QTY_FIDS,
    RT_FUTURES, RT_FUTURES_HOGA,
)

logger    = logging.getLogger(__name__)
sys_log   = logging.getLogger("SYSTEM")   # 실시간 콜백 추적 → SYSTEM.log
probe_log = logging.getLogger("PROBE")    # 투자자ticker 진단 전용

# ── 키움 OCX ProgID ────────────────────────────────────────────
KIWOOM_OCX = "KHOPENAPI.KHOpenAPICtrl.1"

# 실시간 등록 시 기본 FID 목록
DEFAULT_REAL_FIDS = ";".join(str(f) for f in [
    FID_FUTURES_PRICE, FID_FUTURES_VOL,
    *FUTURES_BID_PRICE_FIDS,
    *FUTURES_ASK_PRICE_FIDS,
    *FUTURES_BID_QTY_FIDS,
    *FUTURES_ASK_QTY_FIDS,
    FID_OI,
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
        self._chejan_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._msg_callbacks: List[Callable[[Dict[str, str]], None]] = []

        self.OnEventConnect.connect(self._on_event_connect)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.OnReceiveRealData.connect(self._on_receive_real_data)
        self.OnReceiveChejanData.connect(self._on_receive_chejan_data)
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
            "record_name": actual_record,
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
        sopt_type: str = "0",
    ) -> None:
        """
        실시간 데이터 수신 등록.

        Parameters
        ----------
        code       종목 코드 (예: "A0166000")
        real_type  실시간 타입 (예: RT_FUTURES = "선물시세")
        screen_no  화면 번호 (4자리)
        fid_list   FID 문자열 (기본값: DEFAULT_REAL_FIDS)
        callback   (code, real_type, real_data) → None
        sopt_type  "0" = 기존 등록 초기화 후 등록, "1" = 기존 유지 추가
        """
        fids = fid_list or DEFAULT_REAL_FIDS
        ret = self.dynamicCall(
            "SetRealReg(QString, QString, QString, QString)",
            screen_no, code, fids, sopt_type,
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

    # ── 투자자ticker 진단 ─────────────────────────────────────
    def probe_investor_ticker(self, extra_codes: Optional[List[str]] = None) -> None:
        """투자자ticker 실시간 타입 FID·코드 탐색 (진단용).

        SetRealReg로 후보 코드 전부 등록 → 콜백에서 FID 값 상세 로그.
        PROBE.log 및 콘솔에서 결과 확인.
        KOA Studio에서 '투자자ticker' 실시간 목록 화면과 대조할 것.

        개발가이드 8.18절 표기 기준으로 공백 포함("투자자 ticker")·없는 버전
        두 가지를 모두 등록.
        """
        # 후보 RT 타입명: 공백 없는 버전과 공백 있는 버전 모두 시도
        RT_TYPES = ["투자자ticker", "투자자 ticker"]

        # 시장 전체 데이터형 후보 코드
        # "0" = KOSPI 전체(장시작시간 등록에 사용되는 코드)
        # "001" = 코스피지수코드
        # "K200" = KOSPI200
        # extra_codes 선물 근월물 등 호출 측 추가
        base_codes = ["0", "001", "K200"]
        if extra_codes:
            base_codes = list(extra_codes) + base_codes

        seen = set()
        candidate_codes = []
        for c in base_codes:
            if c not in seen:
                seen.add(c)
                candidate_codes.append(c)

        probe_log.info(
            "[PROBE] probe_investor_ticker 시작 — 후보코드=%s RT타입=%s",
            candidate_codes, RT_TYPES,
        )

        screen_idx = 0
        for rt_type in RT_TYPES:
            for code in candidate_codes:
                screen = "99%02d" % screen_idx
                screen_idx += 1
                ret = self.dynamicCall(
                    "SetRealReg(QString, QString, QString, QString)",
                    screen, code, "216", "0",
                )
                probe_log.info(
                    "[PROBE] SetRealReg rt=%r code=%r screen=%s ret=%d",
                    rt_type, code, screen, ret,
                )
                print(
                    f"[PROBE] SetRealReg rt={rt_type!r} code={code!r} screen={screen} ret={ret}",
                    flush=True,
                )
                self._real_callbacks.setdefault((code, rt_type), []).append(
                    self._on_probe_ticker_cb
                )

        probe_log.info(
            "[PROBE] 등록 완료. 데이터 수신 시 [PROBE-TICKER] 라인 출력됨. "
            "수신 없으면 모의투자 미지원 가능성 → [PROBE-ALLRT] 로 수신 타입 전수 확인"
        )

    def _on_probe_ticker_cb(self, code: str, real_type: str, real_data: str) -> None:
        """투자자ticker 콜백 — 진단용.

        COM 콜백 내부: GetCommRealData(단순 읽기)만 허용.
        QEventLoop·CommRqData·dynamicCall 블로킹 호출 금지.
        """
        fid216 = self.dynamicCall("GetCommRealData(QString, int)", code, 216).strip()

        # FID 200~230 전수 조사 (비공백 값만 수집)
        discovered = {}
        for fid in range(200, 231):
            v = self.dynamicCall("GetCommRealData(QString, int)", code, fid).strip()
            if v:
                discovered[fid] = v
        # 추가로 10·11·12·13·15·20·216도 체크
        for fid in (10, 11, 12, 13, 15, 20):
            v = self.dynamicCall("GetCommRealData(QString, int)", code, fid).strip()
            if v:
                discovered[fid] = v

        probe_log.warning(
            "[PROBE-TICKER] code=%r type=%r | FID216=%r | real_data=%r | 비공백FID=%s",
            code, real_type, fid216, real_data[:300], discovered,
        )
        print(
            f"[PROBE-TICKER] code={code!r} type={real_type!r} "
            f"FID216={fid216!r} real_data={real_data[:200]!r} "
            f"비공백FID={discovered}",
            flush=True,
        )

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

        # ── [PROBE-ALLRT] 수신 타입 전수 감시 + 신규 타입 FID 스캔 ──
        if not hasattr(self, "_probe_allrt_seen"):
            self._probe_allrt_seen = set()
        rt_stripped = real_type.strip()
        if rt_stripped not in self._probe_allrt_seen:
            self._probe_allrt_seen.add(rt_stripped)
            probe_log.info(
                "[PROBE-ALLRT] 신규타입 code=%r type=%r → FID 스캔 시작",
                code, real_type,
            )
            print(f"[PROBE-ALLRT] 신규타입 code={code!r} type={real_type!r}", flush=True)

            # FID 전수 스캔 — 신규 타입 첫 수신 시 1회만 실행
            # GetCommRealData는 단순 동기 읽기 → COM 콜백 내 호출 안전
            discovered = {}
            # 주요 범위: 1~99 (공통·호가), 100~400 (수급·프로그램?), 900~960 (주문)
            _scan = (
                list(range(1, 100))
                + list(range(100, 201))
                + list(range(201, 401))
                + list(range(900, 961))
            )
            for fid in _scan:
                v = self.dynamicCall(
                    "GetCommRealData(QString, int)", code, fid
                ).strip()
                if v:
                    discovered[fid] = v
            probe_log.warning(
                "[PROBE-ALLRT-FIDS] type=%r code=%r 비공백FID=%s",
                rt_stripped, code, discovered,
            )
            print(
                f"[PROBE-ALLRT-FIDS] type={rt_stripped!r} code={code!r} FIDs={discovered}",
                flush=True,
            )

        # ── 투자자ticker 전용 캐치 ─────────────────────────────
        # probe_investor_ticker()의 콜백 등록 코드와 실제 수신 코드가
        # 다를 수 있으므로, real_type 기준으로 직접 탐지
        if rt_stripped in ("투자자ticker", "투자자 ticker"):
            self._on_probe_ticker_cb(code, real_type, real_data)

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
        tc = tr_code.upper()
        if tc == "OPT50029":
            fields = ["체결시간", "현재가", "시가", "고가", "저가", "거래량"]
        elif tc == "OPT10059":
            # 선물 투자자별 매매 — 행별 투자자 그룹 순매수
            fields = ["순매수"]
        elif tc == "OPT50008":
            # 프로그램매매추이차트요청 — 투자자별 순매수금액(KRW)
            # INPUT: 종목코드=P0010I(코스피), 시간구분=1, 거래소구분=1
            # 행 구조(투자자별 vs 시간별)는 TR-DISCOVER 로그로 확인 중
            fields = ["투자자별순매수금액", "체결시간"]
        elif tc == "OPT10060":
            # 프로그램 매매 합계 — 차익/비차익 순매수 (단일 행)
            fields = ["차익순매수", "비차익순매수"]
        elif tc == "OPW20006":
            fields = [
                "종목코드", "종목명", "매매일자", "매매구분",
                "잔고수량", "매입단가", "매매금액",
                "현재가", "평가손익", "손익율", "평가금액",
            ]
        else:
            fields = []
        result = {
            f: self.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                tr_code, rq_name, index, f,
            ).strip()
            for f in fields
        }
        # OPW20006 싱글행(합계)은 여기서 처리 불필요 — 멀티레코드는 request_futures_balance에서 별도 조회
        if tc == "OPW20006":
            return result
        # 알 수 없는 TR이거나 모든 필드가 비어 있으면 discovery 로그 출력
        if not fields or all(v == "" for v in result.values()):
            _DISCOVERY_FIELDS = [
                "투자자별순매수금액", "투자자별매수금액", "투자자별매도수금액",
                "순매수금액", "매수금액", "매도금액",
                "순매수", "순매수수량", "체결시간",
            ]
            discovered = {
                f: self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)",
                    tr_code, rq_name, index, f,
                ).strip()
                for f in _DISCOVERY_FIELDS
            }
            non_empty = {k: v for k, v in discovered.items() if v}
            logger.warning(
                "[TR-DISCOVER] tr=%s rq=%s row=%d 비어있는 필드셋 → 후보 비공백: %s",
                tr_code, rq_name, index, non_empty or "(전부 공백)",
            )
        return result

    # ── 주문 전송 ─────────────────────────────────────────────

    def send_order(
        self,
        rqname: str,
        screen_no: str,
        acc_no: str,
        order_type: int,
        code: str,
        qty: int,
        price: int,
        hoga_gb: str,
        org_order: str,
    ) -> int:
        """
        키움 주문 전송 (SendOrder).

        order_type: 1=신규매수, 2=신규매도
        hoga_gb:    "03"=시장가
        반환값:     0=접수 성공, 음수=오류코드
        실제 체결번호는 OnReceiveChejanData 콜백에서 수신
        """
        args = [
            rqname,
            screen_no,
            acc_no,
            int(order_type),
            code,
            int(qty),
            int(price),
            hoga_gb,
            org_order,
        ]
        logger.warning(
            "[OrderDiag] SendOrder request rq=%s screen=%s acc=%s type=%s code=%s qty=%s price=%s hoga=%s org=%s connected=%s",
            rqname, screen_no, acc_no, order_type, code, qty, price, hoga_gb, org_order, self.is_connected,
        )
        ret = int(self.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            args,
        ))
        if ret == 0:
            logger.info(
                "SendOrder 접수 rq=%s type=%d code=%s qty=%d acc=%s",
                rqname, order_type, code, qty, acc_no,
            )
        else:
            logger.error(
                "SendOrder 실패 ret=%d rq=%s type=%d code=%s qty=%d",
                ret, rqname, order_type, code, qty,
            )
        return ret

    def send_order_fo(
        self,
        rqname: str,
        screen_no: str,
        acc_no: str,
        code: str,
        trade_type: int,    # lOrdKind: 1=신규매매, 2=정정, 3=취소
        qty: int,
        price: float = 0.0,
        hoga_gb: str = "3",  # "1"=지정가, "3"=시장가
        org_order_no: int = 0,
        slby_tp: str = "",   # sSlbyTp: "1"=매도, "2"=매수, ""=미지정(lOrdKind에 종속)
    ) -> int:
        """선물/옵션 주문 전송 (SendOrderFO). 선물 주문은 반드시 이 메서드 사용."""
        args = [
            rqname,
            screen_no,
            acc_no,
            code,
            int(trade_type),
            slby_tp,         # sSlbyTp: 매도/매수 방향 (신규매매 시 필수)
            hoga_gb,
            int(qty),
            float(price),
            int(org_order_no),
        ]
        logger.warning(
            "[OrderDiag] SendOrderFO request rq=%s screen=%s acc=%s code=%s type=%s qty=%s price=%s hoga=%s connected=%s",
            rqname, screen_no, acc_no, code, trade_type, qty, price, hoga_gb, self.is_connected,
        )
        ret = int(self.dynamicCall(
            "SendOrderFO(QString, QString, QString, QString, int, QString, QString, int, double, int)",
            args,
        ))
        if ret == 0:
            logger.info(
                "SendOrderFO 접수 rq=%s type=%d code=%s qty=%d acc=%s",
                rqname, trade_type, code, qty, acc_no,
            )
        else:
            logger.error(
                "SendOrderFO 실패 ret=%d rq=%s type=%d code=%s qty=%d",
                ret, rqname, trade_type, code, qty,
            )
        return ret

    # ── 연결 상태 ─────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        state = int(self.dynamicCall("GetConnectState()"))
        return state == 1


def _kiwoom_register_chejan_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
    if callback not in self._chejan_callbacks:
        self._chejan_callbacks.append(callback)


def _kiwoom_register_msg_callback(self, callback: Callable[[Dict[str, str]], None]) -> None:
    if callback not in self._msg_callbacks:
        self._msg_callbacks.append(callback)


def _kiwoom_get_chejan_data(self, fid: int) -> str:
    return self.dynamicCall("GetChejanData(int)", fid).strip()


def _kiwoom_build_chejan_payload(self, gubun: str, item_cnt: int, fid_list: str) -> Dict[str, Any]:
    def _to_int(text: str) -> int:
        s = str(text or "").strip().replace(",", "")
        if not s:
            return 0
        s = s.lstrip("+")
        try:
            return int(s)
        except ValueError:
            return 0

    def _to_float(text: str) -> float:
        s = str(text or "").strip().replace(",", "")
        if not s:
            return 0.0
        s = s.lstrip("+")
        try:
            return float(s)
        except ValueError:
            return 0.0

    fids = [int(fid) for fid in fid_list.split(";") if fid.strip().isdigit()]
    raw = {fid: self.get_chejan_data(fid) for fid in fids}
    code = raw.get(9001, "").strip()
    if code.startswith(("A", "J")) and len(code) > 1:
        code = code[1:]

    return {
        "gubun": str(gubun).strip(),
        "item_cnt": int(item_cnt),
        "fid_list": fids,
        "raw": raw,
        "account_no": raw.get(9201, "").strip(),
        "order_no": raw.get(9203, "").strip(),
        "original_order_no": raw.get(904, "").strip(),
        "code": code,
        "name": raw.get(302, "").strip(),
        "order_status": raw.get(913, "").strip(),
        "order_gubun": raw.get(905, "").strip(),
        "trade_gubun": raw.get(907, "").strip(),
        "order_qty": _to_int(raw.get(900, "")),
        "order_price": _to_float(raw.get(901, "")),
        "unfilled_qty": _to_int(raw.get(902, "")),
        "filled_qty": _to_int(raw.get(911, "") or raw.get(915, "")),
        "fill_price": _to_float(raw.get(910, "") or raw.get(914, "")),
        "order_time": raw.get(908, "").strip(),
        "fill_no": raw.get(909, "").strip(),
        "current_price": _to_float(raw.get(10, "")),
        "best_ask": _to_float(raw.get(27, "")),
        "best_bid": _to_float(raw.get(28, "")),
        "holding_qty": _to_int(raw.get(930, "")),
        "avg_price": _to_float(raw.get(931, "")),
        "available_qty": _to_int(raw.get(933, "")),
        "balance_side": raw.get(946, "").strip(),
    }


def _kiwoom_on_receive_chejan_data(self, gubun: str, item_cnt: int, fid_list: str) -> None:
    payload = self._build_chejan_payload(gubun, item_cnt, fid_list)
    logger.info(
        "[Chejan] gubun=%s order_no=%s status=%s code=%s filled=%s@%s unfilled=%s",
        payload.get("gubun"),
        payload.get("order_no"),
        payload.get("order_status"),
        payload.get("code"),
        payload.get("filled_qty"),
        payload.get("fill_price"),
        payload.get("unfilled_qty"),
    )
    logger.warning(
        "[ChejanDiag] gubun=%s account=%s order_no=%s original=%s code=%s order_side=%s trade_side=%s balance_side=%s order_qty=%s filled_qty=%s holding_qty=%s available_qty=%s order_price=%s fill_price=%s avg_price=%s raw=%s",
        payload.get("gubun"),
        payload.get("account_no"),
        payload.get("order_no"),
        payload.get("original_order_no"),
        payload.get("code"),
        payload.get("order_gubun"),
        payload.get("trade_gubun"),
        payload.get("balance_side"),
        payload.get("order_qty"),
        payload.get("filled_qty"),
        payload.get("holding_qty"),
        payload.get("available_qty"),
        payload.get("order_price"),
        payload.get("fill_price"),
        payload.get("avg_price"),
        payload.get("raw"),
    )
    for cb in self._chejan_callbacks:
        try:
            cb(payload)
        except Exception:
            logger.exception("chejan callback error order_no=%s", payload.get("order_no"))


def _kiwoom_on_receive_msg(self, screen_no: str, rq_name: str, tr_code: str, msg: str) -> None:
    print(f"[DBG CB-MSG] _on_receive_msg tr={tr_code} msg={msg[:40]}", flush=True)
    logger.debug("TR 硫붿떆吏 [%s/%s]: %s", tr_code, rq_name, msg)
    logger.warning(
        "[OrderMsgDiag] screen=%s rq=%s tr=%s msg=%s",
        screen_no, rq_name, tr_code, msg,
    )
    payload = {
        "screen_no": screen_no,
        "rq_name": rq_name,
        "tr_code": tr_code,
        "msg": msg,
    }
    for cb in self._msg_callbacks:
        try:
            cb(payload)
        except Exception:
            logger.exception("msg callback error [%s/%s]", tr_code, rq_name)


def _kiwoom_request_futures_balance(
    self,
    account_no: str,
    screen_no: str = "2010",
) -> Optional[Dict]:
    # Keep OPW20006 as the canonical row source and enrich summary values
    # with auxiliary futures TRs that match the HTS balance panel behavior.
    K_CODE = "종목코드"
    K_NAME = "종목명"
    K_DATE = "매매일자"
    K_SIDE = "매매구분"
    K_QTY = "잔고수량"
    K_ORDERABLE_QTY = "주문가능수량"
    K_BUY_PRICE = "매입단가"
    K_TRADE_AMT = "매매금액"
    K_CUR_PRICE = "현재가"
    K_PNL = "평가손익"
    K_PNL_RATE = "손익율"
    K_EVAL_AMT = "평가금액"

    K_SUM_TRADE = "총매매"
    K_SUM_PNL = "총평가손익"
    K_SUM_REALIZED = "실현손익"
    K_SUM_EVAL = "총평가"
    K_SUM_RATE = "총평가수익률"
    K_SUM_ASSET = "추정자산"

    primary_multi_record = "선옵잔고상세현황"
    primary_fields = [
        K_CODE,
        K_NAME,
        K_DATE,
        K_SIDE,
        K_QTY,
        K_BUY_PRICE,
        K_TRADE_AMT,
        K_CUR_PRICE,
        K_PNL,
        K_PNL_RATE,
        K_EVAL_AMT,
    ]

    account_pwd = getattr(_secrets, "ACCOUNT_PWD", "")
    today = datetime.datetime.now().strftime("%Y%m%d")

    def _nonblank_map(data: Dict) -> Dict:
        return {k: v for k, v in (data or {}).items() if str(v).strip()}

    def _preview_rows(rows, limit: int = 3):
        return [_nonblank_map(row) for row in list(rows or [])[:limit]]

    def _normalize_code(value: str) -> str:
        return str(value or "").strip().lstrip("A")

    def _read_comm(tr_code: str, rq_name: str, index: int, item: str) -> str:
        try:
            return self.get_comm_data(tr_code, rq_name, index, item).strip()
        except Exception:
            return ""

    def _request_aux(
        tr_code: str,
        rq_name: str,
        inputs: Dict[str, str],
        single_fields,
        *,
        multi_record: str = "",
        multi_fields=None,
        aux_screen_no: str = "2011",
    ) -> Optional[Dict]:
        logger.warning(
            "[%s-REQ] account=%s screen=%s rq=%s inputs=%s single_fields=%s multi_record=%r multi_fields=%s",
            tr_code,
            account_no,
            aux_screen_no,
            rq_name,
            inputs,
            list(single_fields or []),
            multi_record,
            list(multi_fields or []),
        )
        aux_result = self.request_tr(
            tr_code=tr_code,
            rq_name=rq_name,
            inputs=inputs,
            screen_no=aux_screen_no,
            timeout_sec=10,
        )
        if aux_result is None:
            logger.warning("[BalanceTR] %s query failed account=%s", tr_code, account_no)
            return None

        single = {field: _read_comm(tr_code, rq_name, 0, field) for field in (single_fields or [])}
        rows = []
        repeat_cnt = 0
        if multi_record and multi_fields:
            try:
                repeat_cnt = self.get_repeat_cnt(tr_code, multi_record)
            except Exception:
                repeat_cnt = 0
            for i in range(repeat_cnt):
                rows.append({field: _read_comm(tr_code, rq_name, i, field) for field in multi_fields})

        logger.warning(
            "[%s-RESP] rows=%d repeat_cnt=%d record=%r prev_next=%r single=%s nonblank_single=%s row_preview=%s",
            tr_code,
            len(rows),
            repeat_cnt,
            multi_record or aux_result.get("record_name", ""),
            aux_result.get("prev_next", ""),
            single,
            _nonblank_map(single),
            _preview_rows(rows),
        )
        return {
            "result": aux_result,
            "single": single,
            "rows": rows,
            "repeat_cnt": repeat_cnt,
        }

    def _pick_first(tr_code: str, rq_name: str, probe: Dict[str, str], *candidates: str) -> str:
        for item in candidates:
            value = _read_comm(tr_code, rq_name, 0, item)
            probe[item] = value
            if value:
                logger.warning(
                    "[BalanceTR-PICK] tr=%s rq=%s selected=%r value=%r candidates=%s",
                    tr_code,
                    rq_name,
                    item,
                    value,
                    list(candidates),
                )
                return value
        logger.warning(
            "[BalanceTR-PICK] tr=%s rq=%s selected=None candidates=%s",
            tr_code,
            rq_name,
            list(candidates),
        )
        return ""

    def _ensure_row(row_map: Dict[str, Dict], raw_code: str) -> Dict:
        key = _normalize_code(raw_code)
        row = row_map.get(key)
        if row is None:
            row = {
                K_CODE: raw_code,
                K_NAME: "",
                K_DATE: "",
                K_SIDE: "",
                K_QTY: "",
                K_ORDERABLE_QTY: "",
                K_BUY_PRICE: "",
                K_TRADE_AMT: "",
                K_CUR_PRICE: "",
                K_PNL: "",
                K_PNL_RATE: "",
                K_EVAL_AMT: "",
            }
            row_map[key] = row
        return row

    result = self.request_tr(
        tr_code="OPW20006",
        rq_name="futures_balance",
        inputs={
            "계좌번호": account_no,
            "비밀번호": account_pwd,
            "조회일자": today,
            "비밀번호입력매체구분": "00",
        },
        screen_no=screen_no,
        timeout_sec=10,
    )
    if result is None:
        logger.warning("[BalanceTR] OPW20006 query failed account=%s", account_no)
        return None
    logger.warning(
        "[BalanceTR-BASE] OPW20006 meta record=%r prev_next=%r raw_rows=%d",
        result.get("record_name", ""),
        result.get("prev_next", ""),
        len(result.get("rows") or []),
    )

    summary_probe = {}
    summary = {
        K_SUM_TRADE: _pick_first("OPW20006", "futures_balance", summary_probe, "약정합계", "총약정금액", "총매매금액", "총매매"),
        K_SUM_PNL: _pick_first("OPW20006", "futures_balance", summary_probe, "손익합계", "평가손익합계", "총평가손익"),
        K_SUM_REALIZED: _pick_first("OPW20006", "futures_balance", summary_probe, "청산손익합계", "실현손익", "당일실현손익", "당일실현손익(유가)"),
        K_SUM_EVAL: _pick_first("OPW20006", "futures_balance", summary_probe, "평가금액합계", "총평가금액", "총평가"),
        K_SUM_RATE: _pick_first("OPW20006", "futures_balance", summary_probe, "총평가손익률", "총수익률", "수익률", "손익율"),
        K_SUM_ASSET: _pick_first("OPW20006", "futures_balance", summary_probe, "추정예탁자산", "추정자산", "예탁총액", "예탁자산"),
    }

    query_count_text = _read_comm("OPW20006", "futures_balance", 0, "조회건수")
    try:
        query_count = int(query_count_text or "0")
    except ValueError:
        query_count = -1
    logger.warning(
        "[BalanceTR-BASE-SUMMARY] summary=%s nonblank=%s probe=%s",
        summary,
        _nonblank_map(summary),
        _nonblank_map(summary_probe),
    )
    logger.warning("[BalanceTR-QUERYCOUNT] text=%r parsed=%s", query_count_text, query_count)

    rows = []
    row_map = {}
    try:
        repeat_cnt = self.get_repeat_cnt("OPW20006", primary_multi_record)
    except Exception:
        repeat_cnt = 0
    logger.warning("[BalanceTR-ROWS] primary_record=%r repeat_cnt=%d", primary_multi_record, repeat_cnt)
    for i in range(repeat_cnt):
        row = {field: _read_comm("OPW20006", "futures_balance", i, field) for field in primary_fields}
        row[K_ORDERABLE_QTY] = row.get(K_ORDERABLE_QTY, "")
        rows.append(row)
        row_map[_normalize_code(row.get(K_CODE, ""))] = row
        logger.warning(
            "[BalanceTR-ROW] source=OPW20006 idx=%d normalized_code=%s nonblank=%s",
            i,
            _normalize_code(row.get(K_CODE, "")),
            _nonblank_map(row),
        )

    opw20007 = _request_aux(
        "OPW20007",
        "futures_balance_settle",
        {
            "계좌번호": account_no,
            "비밀번호": account_pwd,
            "비밀번호입력매체구분": "00",
        },
        ["약정금액합계", "평가손익합계", "출력건수"],
        multi_record="선옵잔고현황정산가기준",
        multi_fields=[
            K_CODE,
            K_NAME,
            "매도매수구분",
            "수량",
            K_BUY_PRICE,
            K_CUR_PRICE,
            K_PNL,
            "청산가능수량",
            "약정금액",
            K_EVAL_AMT,
        ],
        aux_screen_no="2011",
    )
    if opw20007:
        single = opw20007["single"]
        summary_probe.update({f"OPW20007.{k}": v for k, v in single.items()})
        if not summary.get(K_SUM_TRADE):
            summary[K_SUM_TRADE] = single.get("약정금액합계", "")
        if not summary.get(K_SUM_PNL):
            summary[K_SUM_PNL] = single.get("평가손익합계", "")

        for aux_row in opw20007["rows"]:
            row = _ensure_row(row_map, aux_row.get(K_CODE, ""))
            before_merge = dict(row)
            row[K_CODE] = row.get(K_CODE) or aux_row.get(K_CODE, "")
            row[K_NAME] = row.get(K_NAME) or aux_row.get(K_NAME, "")
            raw_side = aux_row.get("매도매수구분", "")
            if not row.get(K_SIDE):
                if raw_side == "1":
                    row[K_SIDE] = "매도"
                elif raw_side == "2":
                    row[K_SIDE] = "매수"
                else:
                    row[K_SIDE] = raw_side
            row[K_QTY] = row.get(K_QTY) or aux_row.get("수량", "")
            row[K_ORDERABLE_QTY] = row.get(K_ORDERABLE_QTY) or aux_row.get("청산가능수량", "")
            row[K_BUY_PRICE] = row.get(K_BUY_PRICE) or aux_row.get(K_BUY_PRICE, "")
            row[K_CUR_PRICE] = row.get(K_CUR_PRICE) or aux_row.get(K_CUR_PRICE, "")
            row[K_PNL] = row.get(K_PNL) or aux_row.get(K_PNL, "")
            row[K_TRADE_AMT] = row.get(K_TRADE_AMT) or aux_row.get("약정금액", "")
            row[K_EVAL_AMT] = row.get(K_EVAL_AMT) or aux_row.get(K_EVAL_AMT, "")
            logger.warning(
                "[BalanceTR-MERGE] source=OPW20007 code=%s before=%s aux=%s after=%s",
                _normalize_code(aux_row.get(K_CODE, "")),
                _nonblank_map(before_merge),
                _nonblank_map(aux_row),
                _nonblank_map(row),
            )
        rows = list(row_map.values())

    opw20008 = _request_aux(
        "OPW20008",
        "futures_balance_deposit",
        {
            "계좌번호": account_no,
            "비밀번호": account_pwd,
            "비밀번호입력매체구분": "00",
        },
        [
            "계좌명",
            "예탁총액",
            "추정예탁총액",
            "예탁현금",
            "추정예탁현금",
            "유지증거금총액",
            "옵션잔고평가손익",
        ],
        aux_screen_no="2012",
    )
    if opw20008:
        single = opw20008["single"]
        summary_probe.update({f"OPW20008.{k}": v for k, v in single.items()})
        logger.warning(
            "[BalanceTR-AUX-RAW] source=OPW20008 single=%s",
            _nonblank_map(single),
        )
        if not summary.get(K_SUM_ASSET):
            summary[K_SUM_ASSET] = single.get("추정예탁총액") or single.get("예탁총액", "")

    opw20003 = _request_aux(
        "OPW20003",
        "futures_balance_realized",
        {
            "계좌번호": account_no,
            "시장구분": "0",
            "비밀번호": account_pwd,
            "시작일자": today,
            "종료일자": today,
            "비밀번호입력매체구분": "00",
        },
        ["총손익", "예탁총액", "수익율", "조회건수"],
        aux_screen_no="2013",
    )
    if opw20003:
        single = opw20003["single"]
        summary_probe.update({f"OPW20003.{k}": v for k, v in single.items()})
        logger.warning(
            "[BalanceTR-AUX-RAW] source=OPW20003 single=%s",
            _nonblank_map(single),
        )
        if not summary.get(K_SUM_REALIZED):
            summary[K_SUM_REALIZED] = single.get("총손익", "")
        if not summary.get(K_SUM_RATE):
            summary[K_SUM_RATE] = single.get("수익율", "")
        if not summary.get(K_SUM_ASSET):
            summary[K_SUM_ASSET] = single.get("예탁총액", "")

    nonempty_rows = [row for row in rows if any(str(v).strip() for v in row.values())]
    result["summary"] = summary
    result["summary_probe"] = summary_probe
    result["rows"] = rows
    result["record_name"] = primary_multi_record
    result["query_count"] = query_count
    result["nonempty_rows"] = nonempty_rows
    result["blank_row_count"] = len(rows) - len(nonempty_rows)
    result["all_blank_rows"] = bool(rows) and not nonempty_rows

    logger.warning(
        "[BalanceTR-RESP] rows=%d nonempty=%d query_count=%d record=%r prev_next=%r summary=%s nonblank_summary=%s row_preview=%s",
        len(rows),
        len(nonempty_rows),
        query_count,
        result.get("record_name", ""),
        result.get("prev_next", ""),
        summary,
        _nonblank_map(summary),
        _preview_rows(nonempty_rows or rows),
    )
    logger.warning(
        "[BalanceTR-FINAL] blank_row_count=%d all_blank_rows=%s summary_blank=%s probe_nonblank=%s",
        result.get("blank_row_count", 0),
        result.get("all_blank_rows", False),
        not any(str(v).strip() for v in summary.values()),
        _nonblank_map(summary_probe),
    )
    if not any(str(v).strip() for v in summary.values()):
        logger.warning("[BalanceTR-SUMMARY-BLANK] probe=%s", summary_probe)
    logger.info("[BalanceTR] futures balance rows=%d", len(rows))
    return result


KiwoomAPI.register_chejan_callback = _kiwoom_register_chejan_callback
KiwoomAPI.register_msg_callback = _kiwoom_register_msg_callback
KiwoomAPI.get_chejan_data = _kiwoom_get_chejan_data
KiwoomAPI._build_chejan_payload = _kiwoom_build_chejan_payload
KiwoomAPI._on_receive_chejan_data = _kiwoom_on_receive_chejan_data
KiwoomAPI._on_receive_msg = _kiwoom_on_receive_msg
KiwoomAPI.request_futures_balance = _kiwoom_request_futures_balance
