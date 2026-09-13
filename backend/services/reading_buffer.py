"""
Keeps a rolling window of the most recent sensor readings per motor,
in memory, for the CNN+LSTM model (which needs a sequence, not a single
snapshot). Not persisted to DB - resets on backend restart, which is
fine since it just needs to refill from live readings.
"""
from collections import deque
import threading

WINDOW_SIZE = 200


class ReadingBuffer:
    def __init__(self, maxlen: int = WINDOW_SIZE):
        self._buffers: dict[str, deque] = {}
        self._lock = threading.Lock()
        self.maxlen = maxlen

    def add(self, motor_id: str, reading: dict):
        with self._lock:
            buf = self._buffers.setdefault(motor_id, deque(maxlen=self.maxlen))
            buf.append(reading)

    def get_window(self, motor_id: str):
        with self._lock:
            buf = self._buffers.get(motor_id)
            if buf is None or len(buf) < self.maxlen:
                return None
            return list(buf)

    def fill_ratio(self, motor_id: str) -> float:
        with self._lock:
            buf = self._buffers.get(motor_id)
            return (len(buf) / self.maxlen) if buf else 0.0


reading_buffer = ReadingBuffer()