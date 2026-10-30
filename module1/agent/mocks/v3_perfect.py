"""
Production-Grade LRU Cache Implementation with Doubly Linked List and Hash Map.
"""
from typing import Any, Optional


class Node:
    """Doubly-linked list node storing key and value."""
    def __init__(self, key: Any = None, value: Any = None) -> None:
        self.key: Any = key
        self.value: Any = value
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None


class LRUCache:
    """
    Industrial-grade O(1) LRU Cache utilizing a Hash Map paired with a
    Doubly Linked List for deterministic eviction order and strict type safety.
    """
    def __init__(self, capacity: int) -> None:
        self.capacity: int = capacity
        self.map: dict = {}
        self.head: Node = Node()
        self.tail: Node = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Unlink node from doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        if prev_node:
            prev_node.next = next_node
        if next_node:
            next_node.prev = prev_node

    def _add_to_tail(self, node: Node) -> None:
        """Append node right before dummy tail (mark as most recently used)."""
        prev_node = self.tail.prev
        if prev_node:
            prev_node.next = node
        node.prev = prev_node
        node.next = self.tail
        self.tail.prev = node

    def get(self, key: Any) -> int:
        """
        Retrieve value associated with key in O(1) time.
        Gracefully handles unhashable keys and returns -1 when key is missing or capacity <= 0.
        """
        try:
            hash(key)
        except TypeError:
            return -1

        if self.capacity <= 0 or key not in self.map:
            return -1

        node = self.map[key]
        self._remove(node)
        self._add_to_tail(node)
        return node.value

    def put(self, key: Any, value: int) -> None:
        """
        Insert or update key-value pair in O(1) time.
        Gracefully ignores unhashable keys and no-ops when capacity <= 0.
        Evicts least recently used node if capacity exceeded.
        """
        try:
            hash(key)
        except TypeError:
            return

        if self.capacity <= 0:
            return

        if key in self.map:
            node = self.map[key]
            node.value = value
            self._remove(node)
            self._add_to_tail(node)
        else:
            if len(self.map) >= self.capacity:
                lru_node = self.head.next
                if lru_node and lru_node != self.tail:
                    self._remove(lru_node)
                    if lru_node.key in self.map:
                        del self.map[lru_node.key]
            new_node = Node(key, value)
            self._add_to_tail(new_node)
            self.map[key] = new_node

