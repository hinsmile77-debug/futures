# utils/slack_queue.py — Slack 비동기 큐 (싱글톤 워커 스레드)
"""
단일 워커 스레드가 큐를 순차 처리하여 COM 이벤트 루프 간섭 없이
Slack 메시지를 안정적으로 발송한다.
"""
import json
import queue
import threading
import logging
import time
import requests
from typing import Optional

logger = logging.getLogger("SLACK")


class SlackQueueManager:
    """Slack 메시지 큐 — 프로세스 내 싱글톤."""

    _instance: Optional["SlackQueueManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, token: str = None, default_channel: str = None):
        if getattr(self, "_initialized", False):
            return
        self.token           = token
        self.default_channel = default_channel
        self._queue          = queue.Queue()
        self._stop           = threading.Event()
        self._worker         = threading.Thread(target=self._run, daemon=True, name="slack-worker")
        self._worker.start()
        self._initialized    = True
        logger.debug("[SlackQueue] 워커 스레드 시작")

    def enqueue(self, message: str, channel: Optional[str] = None) -> None:
        """메시지를 큐에 추가 (즉시 반환)."""
        self._queue.put({
            "text":    message,
            "channel": channel or self.default_channel,
        })

    def _run(self) -> None:
        """큐 워커 루프 — 데몬 스레드."""
        url = "https://slack.com/api/chat.postMessage"
        while not self._stop.is_set():
            try:
                try:
                    item = self._queue.get(timeout=1)
                except queue.Empty:
                    continue

                if not self.token:
                    logger.warning("[SlackQueue] 토큰 없음 — 메시지 스킵")
                    self._queue.task_done()
                    continue

                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type":  "application/json; charset=utf-8",
                }
                payload = {"channel": item["channel"], "text": item["text"]}

                try:
                    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                    resp = requests.post(url, headers=headers, data=body, timeout=5)
                    res  = resp.json()
                    if res.get("ok"):
                        time.sleep(1.0)   # Slack rate-limit: 1 req/sec per channel
                    else:
                        logger.warning("[SlackQueue] API 오류: %s", res.get("error", res))
                except Exception as e:
                    logger.warning("[SlackQueue] 전송 예외: %s", e)
                    time.sleep(5)

                self._queue.task_done()

            except Exception:
                logger.exception("[SlackQueue] 워커 루프 예외")
                time.sleep(1)

    def stop(self) -> None:
        self._stop.set()
        if self._worker.is_alive():
            self._worker.join(timeout=2)


def get_slack_queue(token: str = None, default_channel: str = None) -> SlackQueueManager:
    """전역 싱글톤 인스턴스 반환."""
    return SlackQueueManager(token, default_channel)
