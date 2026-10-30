"""RateLimiter V3: Production-grade sliding window with collections.deque.
Robust edge cases, strict boundary expiration, defensive type validation, and high throughput.
"""
from __future__ import annotations

import time
from collections import deque
from typing import Any, Dict, Optional


class RateLimiter:
    """Industrial-grade, rolling-window rate limiter.

    Tracks request timestamps within a continuous rolling window using double-ended queues.
    Guarantees strict quota adherence without boundary burst vulnerabilities.
    """

    def __init__(self, max_requests: int = 5, window_seconds: float = 60.0) -> None:
        """Initialize the rate limiter with quota and window limits.

        Args:
            max_requests: Maximum requests allowed in the rolling window.
            window_seconds: Window duration in seconds.
        """
        self.max_requests = max_requests if max_requests > 0 else 0
        self.window_seconds = window_seconds if window_seconds > 0 else 0.0
        self.user_timestamps: Dict[str, deque[float]] = {}

    def _sanitize(self, user_id: Any, timestamp: Any) -> Optional[tuple[str, float]]:
        """Validate and sanitize user identity and timestamp inputs."""
        if not user_id or not isinstance(user_id, str):
            return None
        if timestamp is None:
            ts = time.time()
        else:
            try:
                ts = float(timestamp)
            except (ValueError, TypeError):
                return None
        if ts < 0:
            return None
        return user_id, ts

    def allow_request(self, user_id: str, timestamp: Optional[float] = None) -> bool:
        """Determine whether an incoming request from user_id should be permitted.

        Args:
            user_id: Identifier of the requesting client.
            timestamp: Optional epoch timestamp of the request.

        Returns:
            True if request is permitted under the current quota, False otherwise.
        """
        if self.max_requests <= 0 or self.window_seconds <= 0:
            return False

        sanitized = self._sanitize(user_id, timestamp)
        if sanitized is None:
            return False
        uid, ts = sanitized

        if uid not in self.user_timestamps:
            self.user_timestamps[uid] = deque()

        q = self.user_timestamps[uid]
        cutoff = ts - self.window_seconds

        # Prune all entries strictly older than or equal to expiration boundary
        while q and q[0] <= cutoff:
            q.popleft()

        if len(q) < self.max_requests:
            q.append(ts)
            return True
        return False

    def get_remaining_tokens(self, user_id: str, timestamp: Optional[float] = None) -> int:
        """Return the count of remaining available request tokens for user_id.

        Args:
            user_id: Identifier of the requesting client.
            timestamp: Optional reference timestamp.

        Returns:
            Integer token count in [0, max_requests].
        """
        if self.max_requests <= 0 or self.window_seconds <= 0:
            return 0

        sanitized = self._sanitize(user_id, timestamp)
        if sanitized is None:
            return 0
        uid, ts = sanitized

        if uid not in self.user_timestamps:
            return self.max_requests

        q = self.user_timestamps[uid]
        cutoff = ts - self.window_seconds
        while q and q[0] <= cutoff:
            q.popleft()

        return max(0, self.max_requests - len(q))

