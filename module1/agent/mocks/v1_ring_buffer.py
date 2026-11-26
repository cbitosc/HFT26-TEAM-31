# V1 Initial RingBuffer prototype
# Contains boundary flaws: crashes on empty pop and capacity <= 0
class RingBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []

    def push(self, item):
        if self.capacity <= 0:
            # Flaw: doesn't handle zero capacity properly
            self.buffer.append(item)
            return
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(item)

    def pop(self):
        # Flaw: crashes with IndexError if buffer is empty
        return self.buffer.pop(0)

    def is_empty(self):
        return len(self.buffer) == 0

    def is_full(self):
        return len(self.buffer) >= self.capacity

