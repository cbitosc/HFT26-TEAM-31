"""
AutoEvolve Protocol - Task Definition & Unit-Test Specifications
"""

TASK_PROMPT = """You are an expert algorithmic systems engineer.
Implement an industrial-grade, highly efficient Least Recently Used (LRU) Cache class named `LRUCache`.

Class Signature:
```python
class LRUCache:
    def __init__(self, capacity: int) -> None:
        ...

    def get(self, key: int) -> int:
        ...

    def put(self, key: int, value: int) -> None:
        ...
```

Requirements:
1. Time Complexity:
   - Both `get` and `put` operations MUST achieve O(1) average time complexity.
2. Eviction Policy:
   - When the cache reaches its maximum capacity, adding a new key must evict the Least Recently Used (LRU) item.
   - Accessing a key via `get` or updating an existing key via `put` must mark that key as the Most Recently Used (MRU).
3. Overwrite Handling:
   - If an existing key is inserted with `put`, update its value and move it to the MRU position without increasing the cache size.
4. Edge Case - Zero or Negative Capacity:
   - If initialized with `capacity <= 0`, all `put` operations must be safe no-ops, and all `get` operations must return -1.
5. Edge Case - Unhashable Keys:
   - If an unhashable key (such as a list or dictionary) is passed, `put` must safely ignore the operation (no-op)
     and `get` must return -1, without raising an unhandled `TypeError` or crashing the execution environment.
6. Code Quality:
   - Provide clean docstrings, clear class architecture (e.g. Doubly Linked List with `class Node`), and type annotations (`-> int`, `-> None`).
"""

# HIDDEN_TESTS: 10 explicit benchmark test suites designed for subprocess sandbox execution.
HIDDEN_TESTS = [
    {
        "id": "basic",
        "description": "Standard LRU insertion, retrieval, and eviction sequence",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("get", 1, 10),
            ("get", 2, 20),
            ("put", 3, 30),  # Evicts key 1 (LRU)
            ("get", 1, -1),
            ("get", 2, 20),
            ("get", 3, 30),
        ],
    },
    {
        "id": "capacity_zero",
        "description": "Edge case where capacity is 0: all puts no-op, all gets return -1",
        "capacity": 0,
        "ops": [
            ("put", 1, 1),
            ("get", 1, -1),
            ("put", 2, 2),
            ("get", 2, -1),
        ],
    },
    {
        "id": "eviction",
        "description": "Deterministic eviction of oldest item upon reaching capacity",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("put", 3, 30),  # Evicts key 1
            ("get", 1, -1),
            ("get", 2, 20),
            ("get", 3, 30),
        ],
    },
    {
        "id": "overwrite",
        "description": "Overwriting an existing key updates value without altering valid capacity",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("put", 1, 15),  # Overwrite key 1
            ("get", 1, 15),
            ("get", 2, 20),
        ],
    },
    {
        "id": "order_after_get",
        "description": "Ensures get(key) updates recency so the other key is evicted first",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("get", 1, 10),  # Key 1 becomes MRU, Key 2 becomes LRU
            ("put", 3, 30),  # Must evict Key 2, NOT Key 1
            ("get", 2, -1),
            ("get", 1, 10),
            ("get", 3, 30),
        ],
    },
    {
        "id": "single_cap",
        "description": "Capacity of 1: each new insert immediately evicts the previous item",
        "capacity": 1,
        "ops": [
            ("put", 1, 10),
            ("get", 1, 10),
            ("put", 2, 20),  # Evicts 1
            ("get", 1, -1),
            ("get", 2, 20),
        ],
    },
    {
        "id": "not_found",
        "description": "Queries for nonexistent keys consistently return -1",
        "capacity": 2,
        "ops": [
            ("get", 99, -1),
            ("put", 1, 1),
            ("get", 2, -1),
            ("get", 1, 1),
        ],
    },
    {
        "id": "perf_100k",
        "description": "High-throughput O(1) performance stress test: 100k operations in <0.85s",
        "perf": True,
        "ops_count": 100000,
        "capacity": 1000,
    },
    {
        "id": "unhashable",
        "description": "Graceful handling of unhashable types (e.g. list key) without crashing",
        "capacity": 2,
        "ops": [
            ("put", [1, 2], 1, "no_crash"),
            ("get", [1, 2], -1),
        ],
    },
    {
        "id": "many_puts",
        "description": "Batch put operations (100 inserts) on capacity 50; validates early eviction",
        "capacity": 50,
        "ops": [("put", i, i) for i in range(100)] + [("get", 0, -1)],
    },
]

