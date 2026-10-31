# V1 Initial MinStack prototype
# Naive single list that crashes on empty pop and lacks size tracking
class MinStack:
    def __init__(self):
        self.stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)

    def pop(self):
        # Flaw: crashes with IndexError if empty
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def getMin(self) -> int:
        return min(self.stack)

