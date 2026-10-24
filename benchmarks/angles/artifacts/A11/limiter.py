import math
import time


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class RateLimiter:
    def __init__(self, limit, window, clock=None):
        if not (isinstance(limit, int) and not isinstance(limit, bool) and limit > 0):
            raise ValueError("limit must be a positive int")
        if not (_is_number(window) and math.isfinite(window) and window > 0):
            raise ValueError("window must be a positive finite number")
        if clock is None:
            clock = time.monotonic
        if not callable(clock):
            raise ValueError("clock must be callable or None")
        self._limit = limit
        self._window = window
        self._clock = clock
        self._records = {}
        self._last_time = None

    def allow(self, key):
        if not (isinstance(key, str) and key):
            raise ValueError("key must be a non-empty str")
        now = self._clock()
        if not (_is_number(now) and math.isfinite(now)):
            raise ValueError("clock must return a finite number")
        if self._last_time is not None and now < self._last_time:
            raise ValueError("clock went backwards")
        self._last_time = now
        self._records[key] = [t for t in self._records.get(key, ()) if t > now - self._window]
        if len(self._records[key]) < self._limit:
            self._records[key].append(now)
            return True
        return False
