import math
import time


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
            raise ValueError("window must be a positive finite int or float")
        if clock is None:
            clock = time.monotonic
        elif not callable(clock):
            raise ValueError("clock must be callable or None")

        self.limit = limit
        self.window = window
        self.clock = clock
        self._allowed = {}
        self._last_time = None

    def allow(self, key):
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty str")

        now = self.clock()
        if (
            isinstance(now, bool)
            or not isinstance(now, (int, float))
            or not math.isfinite(now)
        ):
            raise ValueError("clock must return a finite int or float")
        if self._last_time is not None and now < self._last_time:
            raise ValueError("clock moved backwards")

        self._last_time = now

        times = [t for t in self._allowed.get(key, ()) if t > now - self.window]
        if len(times) < self.limit:
            times.append(now)
            self._allowed[key] = times
            return True

        self._allowed[key] = times
        return False
