# V2 Revised RingBuffer: Addresses Critique 1
# Fixes empty pop boundary and zero-capacity guard
class RingBuffer:
    """Circular ring buffer with fixed capacity and boundary guards."""

    def __init__(self, capacity: int):
        self.capacity = max(0, capacity)
        self.buffer = []

    def push(self, item):
        """Pushes an element into the buffer, overwriting oldest if full."""
        if self.capacity <= 0:
            return
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(item)

    def pop(self):
        """Pops the oldest element, returning None if empty."""
        if self.capacity <= 0 or not self.buffer:
            return None
        return self.buffer.pop(0)

    def is_empty(self) -> bool:
        return len(self.buffer) == 0

    def is_full(self) -> bool:
        return self.capacity > 0 and len(self.buffer) >= self.capacity

