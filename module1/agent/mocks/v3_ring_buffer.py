import threading
from typing import Any, Optional


class RingBuffer:
    """Production-grade thread-safe circular ring buffer.

    Attributes:
        capacity: Maximum number of elements retained.
    """

    def __init__(self, capacity: int) -> None:
        """Initializes RingBuffer with capacity bounds."""
        self.capacity = max(0, capacity)
        self.buffer = [None] * self.capacity if self.capacity > 0 else []
        self._head = 0
        self._tail = 0
        self._size = 0
        self._lock = threading.RLock()

    def push(self, item: Any) -> None:
        """Pushes an element into the buffer, overwriting the oldest element if full."""
        with self._lock:
            if self.capacity <= 0:
                return
            self.buffer[self._tail] = item
            self._tail = (self._tail + 1) % self.capacity
            if self._size < self.capacity:
                self._size += 1
            else:
                self._head = (self._head + 1) % self.capacity

    def pop(self) -> Optional[Any]:
        """Pops and returns the oldest element in FIFO order, or None if empty."""
        with self._lock:
            if self.capacity <= 0 or self._size == 0:
                return None
            item = self.buffer[self._head]
            self.buffer[self._head] = None
            self._head = (self._head + 1) % self.capacity
            self._size -= 1
            return item

    def is_empty(self) -> bool:
        """Checks if the buffer contains zero elements."""
        with self._lock:
            return self._size == 0

    def is_full(self) -> bool:
        """Checks if the buffer is at full capacity."""
        with self._lock:
            return self.capacity > 0 and self._size >= self.capacity

