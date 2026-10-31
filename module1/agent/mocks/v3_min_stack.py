from typing import Optional


class MinStack:
    """Production-grade MinStack providing strict O(1) time complexity for all operations.

    Maintains constant-time access to the minimum element using paired invariant tracking.
    """

    def __init__(self) -> None:
        """Initializes empty MinStack."""
        self._stack: list[tuple[int, int]] = []

    def push(self, val: int) -> None:
        """Pushes an integer onto the stack while updating the running minimum."""
        try:
            int_val = int(val)
        except (TypeError, ValueError):
            return
        current_min = int_val if not self._stack else min(int_val, self._stack[-1][1])
        self._stack.append((int_val, current_min))

    def pop(self) -> Optional[int]:
        """Pops and returns the top element, or returns None if the stack is empty."""
        if not self._stack:
            return None
        val, _ = self._stack.pop()
        return val

    def top(self) -> Optional[int]:
        """Returns the top element without removing it, or None if the stack is empty."""
        if not self._stack:
            return None
        return self._stack[-1][0]

    def getMin(self) -> Optional[int]:
        """Retrieves the minimum element in O(1) time complexity."""
        if not self._stack:
            return None
        return self._stack[-1][1]

    def size(self) -> int:
        """Returns total number of elements currently stored on the stack."""
        return len(self._stack)

