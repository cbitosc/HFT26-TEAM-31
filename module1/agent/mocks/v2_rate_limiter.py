# V2 Revised RateLimiter: adds continuous time refill and capacity guards, but lacks threading locks and type validation.
import time

class RateLimiter:
    """Token bucket rate limiter with continuous time refill."""

    def __init__(self, capacity: int, refill_rate: float = 1.0) -> None:
        if not isinstance(capacity, (int, float)) or capacity <= 0:
            self.capacity = 0
            self.tokens = 0
        else:
            self.capacity = float(capacity)
            self.tokens = float(capacity)

        self.refill_rate = max(0.0, float(refill_rate)) if isinstance(refill_rate, (int, float)) else 0.0
        self.last_refill = time.monotonic()

    def allow_request(self) -> bool:
        if self.capacity <= 0:
            return False

        now = time.monotonic()
        elapsed = now - self.last_refill
        self.last_refill = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

