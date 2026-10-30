"""RateLimiter V2: Sliding window implementation.
Addresses boundary bursts with timestamp log, but fails boundary edge cases and invalid inputs.
"""
import time


class RateLimiter:
    """Sliding window log rate limiter with basic pruning."""

    def __init__(self, max_requests: int = 5, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def allow_request(self, user_id: str, timestamp: float = None) -> bool:
        if timestamp is None:
            timestamp = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []

        # Bug: Strict < retains items at the exact cutoff boundary instead of expiring them
        cutoff = timestamp - self.window_seconds
        self.requests[user_id] = [t for t in self.requests[user_id] if t > cutoff]

        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(timestamp)
            return True
        return False

    def get_remaining_tokens(self, user_id: str, timestamp: float = None) -> int:
        if timestamp is None:
            timestamp = time.time()
        if user_id not in self.requests:
            return self.max_requests
        cutoff = timestamp - self.window_seconds
        valid = [t for t in self.requests[user_id] if t > cutoff]
        return max(0, self.max_requests - len(valid))

