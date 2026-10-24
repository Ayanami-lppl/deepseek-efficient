import copy
import math
import time


class TTLCache:
    def __init__(self, ttl_seconds, clock=None):
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, (int, float)):
            raise ValueError("ttl_seconds must be a finite non-negative number")
        if not math.isfinite(ttl_seconds) or ttl_seconds < 0:
            raise ValueError("ttl_seconds must be a finite non-negative number")
        self.ttl_seconds = ttl_seconds
        self.clock = clock or time.monotonic
        self.data = {}

    def set(self, key, value):
        self.data[key] = (copy.deepcopy(value), self.clock() + self.ttl_seconds)

    def get(self, key, default=None):
        if key not in self.data:
            return default
        value, deadline = self.data[key]
        if self.clock() >= deadline:
            return default
        return copy.deepcopy(value)
