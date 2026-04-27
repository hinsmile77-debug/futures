---
name: Kiwoom COM 콜백 안전 규칙
description: 키움 OCX COM 이벤트 콜백 내부에서 절대 금지 사항 및 올바른 패턴
type: feedback
---

COM 콜백(_on_event_connect, _on_receive_tr_data, _on_receive_real_data, _on_receive_msg) 내부에서 `dynamicCall` 또는 `pyqtSignal.emit()` 호출 금지.

**Why:** 0xC0000409 STATUS_STACK_BUFFER_OVERRUN 크래시 발생. 키움 OCX는 COM 이벤트 스택 위에서 재진입(reentrant) dynamicCall을 허용하지 않음.

**How to apply:**
- 콜백 내부: 상태 변수 저장(`self._connected`, `self._tr_data_buffer[rq_name]`) + QEventLoop.quit() 만 수행
- 실제 API 호출(GetRepeatCnt, GetCommData 등)은 반드시 exec_() 복귀 후 정상 이벤트 루프에서 실행
- GetRepeatCnt 두 번째 파라미터: rq_name이 아닌 콜백에서 수신한 record_name 사용
  (`meta.get("record_name") or rq_name` 으로 fallback)
- GetCommData 두 번째 파라미터: rq_name 사용 (record_name 아님)
