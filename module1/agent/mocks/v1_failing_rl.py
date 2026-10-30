"""RateLimiter V1: Naive fixed-window implementation.
Vulnerable to boundary bursts and lacks input sanitization.
"""
import time


class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows = {}

    def allow_request(self, user_id: str, timestamp: float = None) -> bool:
        if timestamp is None:
            timestamp = time.time()
        # Bug: Fixed window bucket allows 2x burst across window boundaries
        current_window = int(timestamp / self.window_seconds)
        key = (user_id, current_window)
        count = self.windows.get(key, 0)
        if count < self.max_requests:
            self.windows[key] = count + 1
            return True
        return False

    def get_remaining_tokens(self, user_id: str, timestamp: float = None) -> int:
        if timestamp is None:
            timestamp = time.time()
        current_window = int(timestamp / self.window_seconds)
        key = (user_id, current_window)
        count = self.windows.get(key, 0)
        return max(0, self.max_requests - count)

