# V2 Revised MinStack: Addresses Critique 1
# O(1) tuple pair min tracking with empty pop guard
class MinStack:
    def __init__(self):
        self.stack = []

    def push(self, val: int) -> None:
        current_min = val if not self.stack else min(val, self.stack[-1][1])
        self.stack.append((val, current_min))

    def pop(self):
        if not self.stack:
            return None
        val, _ = self.stack.pop()
        return val

    def top(self):
        if not self.stack:
            return None
        return self.stack[-1][0]

    def getMin(self) -> int:
        if not self.stack:
            return None
        return self.stack[-1][1]

