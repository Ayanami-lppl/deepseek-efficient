import math
import time


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class RateLimiter:
    def __init__(self, limit, window, clock=None):
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("limit must be a positive int")
        if not _is_number(window) or not math.isfinite(window) or window <= 0:
            raise ValueError("window must be a positive finite number")
        if clock is not None and not callable(clock):
            raise ValueError("clock must be callable or None")
        self._limit = limit
        self._window = window
        self._clock = time.monotonic if clock is None else clock
        self._records = {}
        self._last_time = None

    def allow(self, key):
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty str")
        now = self._clock()
        if not _is_number(now) or not math.isfinite(now):
            raise ValueError("clock must return a finite number")
        if self._last_time is not None and now < self._last_time:
            raise ValueError("clock moved backwards")
        cutoff = now - self._window
        records = self._records.get(key)
        if records is None:
            records = self._records[key] = []
        records[:] = [t for t in records if t > cutoff]
        self._last_time = now
        if len(records) < self._limit:
            records.append(now)
            return True
        return False
