# V1 Failing RateLimiter prototype: lacks zero-capacity guard, time precision, and thread safety.
class RateLimiter:
    def __init__(self, capacity, refill_rate=1.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_time = 0

    def allow_request(self):
        # Naive check: doesn't handle capacity <= 0 and misses continuous refill
        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False

