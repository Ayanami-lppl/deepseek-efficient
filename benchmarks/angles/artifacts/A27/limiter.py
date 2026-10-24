import math
import time


class RateLimiter:
    def __init__(self, limit, window, clock=None):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive int")
        if isinstance(window, bool) or not isinstance(window, (int, float)):
            raise ValueError("window must be a positive finite number")
        if isinstance(window, float) and not math.isfinite(window):
            raise ValueError("window must be a positive finite number")
        if window <= 0:
            raise ValueError("window must be a positive finite number")
        if clock is not None and not callable(clock):
            raise ValueError("clock must be callable or None")

        self.limit = limit
        self.window = window
        self.clock = time.monotonic if clock is None else clock
        self._allowed = {}
        self._last_time = None

    def allow(self, key):
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty str")

        now = self.clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise ValueError("clock must return a finite int or float")
        if isinstance(now, float) and not math.isfinite(now):
            raise ValueError("clock must return a finite int or float")
        if self._last_time is not None and now < self._last_time:
            raise ValueError("clock must not move backwards")

        self._last_time = now
        history = self._allowed.setdefault(key, [])
        cutoff = now - self.window
        while history and history[0] <= cutoff:
            history.pop(0)

        if len(history) < self.limit:
            history.append(now)
            return True
        return False
