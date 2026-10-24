import math
import time
from collections import deque


class RateLimiter:
    def __init__(self, limit, window, clock=None):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive int")
        if (
            isinstance(window, bool)
            or not isinstance(window, (int, float))
            or not math.isfinite(window)
            or window <= 0
        ):
            raise ValueError("window must be a positive finite number")
        if clock is not None and not callable(clock):
            raise ValueError("clock must be callable or None")
        self._limit = limit
        self._window = window
        self._clock = time.monotonic if clock is None else clock
        self._times = {}
        self._last_time = None

    def allow(self, key):
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty str")
        now = self._clock()
        if (
            isinstance(now, bool)
            or not isinstance(now, (int, float))
            or not math.isfinite(now)
        ):
            raise ValueError("clock must return a finite number")
        if self._last_time is not None and now < self._last_time:
            raise ValueError("clock moved backwards")
        cutoff = now - self._window
        records = self._times.get(key)
        if records is None:
            records = deque()
            self._times[key] = records
        while records and records[0] <= cutoff:
            records.popleft()
        allowed = len(records) < self._limit
        if allowed:
            records.append(now)
        self._last_time = now
        return allowed
