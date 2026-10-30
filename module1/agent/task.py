"""Generic Task Abstraction and Predefined Benchmarks for AutoEvolve Protocol.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class TaskSpecification:
    task_id: str
    name: str
    description: str
    programming_language: str
    class_or_function_name: str
    functional_requirements: List[str]
    input_output_spec: Dict[str, Any]
    constraints: List[str]
    expected_behavior: str
    evaluation_criteria: Dict[str, float]
    reference_solution: Optional[str] = None
    baseline_v1: Optional[str] = None
    baseline_v2: Optional[str] = None
    baseline_v3: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "programming_language": self.programming_language,
            "class_or_function_name": self.class_or_function_name,
            "functional_requirements": self.functional_requirements,
            "input_output_spec": self.input_output_spec,
            "constraints": self.constraints,
            "expected_behavior": self.expected_behavior,
            "evaluation_criteria": self.evaluation_criteria,
            "metadata": self.metadata,
        }


# =====================================================================
# Benchmark 1: LRU Cache (Preserves 100% existing functionality)
# =====================================================================

LRU_CACHE_TASK_PROMPT = """You are an expert algorithmic systems engineer.
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

# Existing 10 hidden unit test suites for LRU Cache
HIDDEN_TESTS: List[Dict[str, Any]] = [
    {
        "id": "basic",
        "description": "Standard LRU insertion, retrieval, and eviction sequence",
        "category": "basic",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("get", 1, 10),
            ("get", 2, 20),
            ("put", 3, 30),
            ("get", 1, -1),
            ("get", 2, 20),
            ("get", 3, 30),
        ],
    },
    {
        "id": "capacity_zero",
        "description": "Edge case where capacity is 0: all puts no-op, all gets return -1",
        "category": "boundary",
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
        "category": "basic",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("put", 3, 30),
            ("get", 1, -1),
            ("get", 2, 20),
            ("get", 3, 30),
        ],
    },
    {
        "id": "overwrite",
        "description": "Overwriting an existing key updates value without altering valid capacity",
        "category": "edge",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("put", 1, 15),
            ("get", 1, 15),
            ("get", 2, 20),
        ],
    },
    {
        "id": "order_after_get",
        "description": "Ensures get(key) updates recency so the other key is evicted first",
        "category": "boundary",
        "capacity": 2,
        "ops": [
            ("put", 1, 10),
            ("put", 2, 20),
            ("get", 1, 10),
            ("put", 3, 30),
            ("get", 2, -1),
            ("get", 1, 10),
            ("get", 3, 30),
        ],
    },
    {
        "id": "single_cap",
        "description": "Capacity of 1: each new insert immediately evicts the previous item",
        "category": "boundary",
        "capacity": 1,
        "ops": [
            ("put", 1, 10),
            ("get", 1, 10),
            ("put", 2, 20),
            ("get", 1, -1),
            ("get", 2, 20),
        ],
    },
    {
        "id": "not_found",
        "description": "Queries for nonexistent keys consistently return -1",
        "category": "invalid_input",
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
        "category": "performance",
        "perf": True,
        "ops_count": 100000,
        "capacity": 1000,
    },
    {
        "id": "unhashable",
        "description": "Graceful handling of unhashable types (e.g. list key) without crashing",
        "category": "invalid_input",
        "capacity": 2,
        "ops": [
            ("put", [1, 2], 1, "no_crash"),
            ("get", [1, 2], -1),
        ],
    },
    {
        "id": "many_puts",
        "description": "Batch put operations (100 inserts) on capacity 50; validates early eviction",
        "category": "regression",
        "capacity": 50,
        "ops": [("put", i, i) for i in range(100)] + [("get", 0, -1)],
    },
]

TASK_PROMPT = LRU_CACHE_TASK_PROMPT


def get_lru_benchmark() -> TaskSpecification:
    return TaskSpecification(
        task_id="lru_cache_01",
        name="Least Recently Used (LRU) Cache",
        description=(
            "Design and implement a high-performance Least Recently Used (LRU) Cache data structure "
            "supporting get and put in O(1) average time complexity, deterministic eviction, "
            "and defensive handling of non-hashable inputs."
        ),
        programming_language="python",
        class_or_function_name="LRUCache",
        functional_requirements=[
            "get(key) returns cached value or -1 if missing.",
            "put(key, value) updates value if key exists, or inserts new key.",
            "When capacity is exceeded, evicts the least recently used item.",
            "Capacity <= 0: put is a no-op, get always returns -1.",
            "Unhashable keys safely ignored or rejected without unhandled TypeError crashes.",
            "Strict O(1) amortized throughput under high concurrency.",
        ],
        input_output_spec={
            "init": {"capacity": "int"},
            "get": {"params": ["key: Any"], "returns": "int"},
            "put": {"params": ["key: Any", "value: int"], "returns": "None"},
        },
        constraints=[
            "Time complexity: O(1) for both get and put operations.",
            "Space complexity: O(capacity).",
            "Must not crash on invalid/unhashable types.",
        ],
        expected_behavior="Cache evicts oldest accessed keys while maintaining O(1) lookup.",
        evaluation_criteria={
            "correctness": 0.60,
            "efficiency": 0.20,
            "safety": 0.10,
            "quality": 0.10,
        },
    )


# =====================================================================
# Benchmark 2: API Rate Limiter (Rolling 60s Window, Max 5 requests)
# =====================================================================

RATE_LIMITER_TASK_PROMPT = """You are an expert backend infrastructure engineer.
Implement an industrial-grade, thread-safe API Rate Limiter class named `RateLimiter`.

Class Signature:
```python
class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: float = 60.0) -> None:
        ...

    def allow_request(self, user_id: str, timestamp: float = None) -> bool:
        ...

    def get_remaining_tokens(self, user_id: str, timestamp: float = None) -> int:
        ...
```

Requirements:
1. Rolling Window Policy:
   - Allow a maximum of `max_requests` requests per `user_id` within any rolling `window_seconds` window.
   - Do NOT use a fixed window that resets at fixed intervals (which allows double-capacity boundary bursts).
2. Timestamp Handling:
   - If `timestamp` is None, use `time.time()`.
   - Timestamps strictly older than `timestamp - window_seconds` must expire and not count towards the quota.
   - Requests occurring exactly at the expiration boundary `timestamp - window_seconds` must be expired.
3. Multi-User Isolation:
   - Quotas and timestamps must be tracked independently per `user_id`. One user's requests must never affect another user.
4. Edge Case - Non-positive Parameters:
   - If initialized with `max_requests <= 0` or `window_seconds <= 0`, `allow_request` must return False.
5. Edge Case - Input Sanitization:
   - If `user_id` is empty, None, or not a string, `allow_request` must return False without crashing.
   - If `timestamp` is negative or non-numeric, `allow_request` must return False without crashing.
6. Code Quality & Performance:
   - Clean architecture, sliding log / sliding window algorithm using deque/timestamps, type annotations, and docstrings.
"""

RATE_LIMITER_TESTS: List[Dict[str, Any]] = [
    {
        "id": "rl_basic_allowance",
        "description": "Allows up to max_requests (5) requests within the permitted window",
        "category": "basic",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            ("allow_request", "user_1", 10.0, True),
            ("allow_request", "user_1", 20.0, True),
            ("allow_request", "user_1", 30.0, True),
            ("allow_request", "user_1", 40.0, True),
            ("allow_request", "user_1", 50.0, True),
        ],
    },
    {
        "id": "rl_sixth_request_rejected",
        "description": "Sixth request within the same 60-second window is strictly denied",
        "category": "boundary",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            ("allow_request", "user_1", 10.0, True),
            ("allow_request", "user_1", 20.0, True),
            ("allow_request", "user_1", 30.0, True),
            ("allow_request", "user_1", 40.0, True),
            ("allow_request", "user_1", 50.0, True),
            ("allow_request", "user_1", 55.0, False),  # 6th request within window
        ],
    },
    {
        "id": "rl_boundary_burst_attack",
        "description": "Fixed-window counter flaw test: prevents boundary-burst doubling across interval edges",
        "category": "boundary",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            # 5 requests at the end of minute 1 (t=55..59)
            ("allow_request", "user_1", 55.0, True),
            ("allow_request", "user_1", 56.0, True),
            ("allow_request", "user_1", 57.0, True),
            ("allow_request", "user_1", 58.0, True),
            ("allow_request", "user_1", 59.0, True),
            # Request at t=62: in a naive fixed-window reset at t=60, this would succeed.
            # In rolling 60s window (window is 2.0 to 62.0), previous 5 are still active!
            ("allow_request", "user_1", 62.0, False),
        ],
    },
    {
        "id": "rl_window_expiry_allows_new",
        "description": "Requests after the rolling window expires are permitted again",
        "category": "basic",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            ("allow_request", "user_1", 0.0, True),
            ("allow_request", "user_1", 10.0, True),
            ("allow_request", "user_1", 20.0, True),
            ("allow_request", "user_1", 30.0, True),
            ("allow_request", "user_1", 40.0, True),
            ("allow_request", "user_1", 45.0, False),  # Full
            # t=61.0: request from t=0.0 is now outside rolling window [1.0, 61.0]
            ("allow_request", "user_1", 61.0, True),
        ],
    },
    {
        "id": "rl_exact_expiration_boundary",
        "description": "Request exactly at timestamp - window_seconds boundary is expired",
        "category": "edge",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            ("allow_request", "user_1", 10.0, True),
            ("allow_request", "user_1", 20.0, True),
            ("allow_request", "user_1", 30.0, True),
            ("allow_request", "user_1", 40.0, True),
            ("allow_request", "user_1", 50.0, True),
            # t=70.0: diff with t=10.0 is exactly 60.0. t=10 is outside the window.
            ("allow_request", "user_1", 70.0, True),
        ],
    },
    {
        "id": "rl_multi_user_isolation",
        "description": "Requests from different users are tracked independently",
        "category": "basic",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            ("allow_request", "user_A", 10.0, True),
            ("allow_request", "user_A", 11.0, True),
            ("allow_request", "user_A", 12.0, True),
            ("allow_request", "user_A", 13.0, True),
            ("allow_request", "user_A", 14.0, True),
            ("allow_request", "user_A", 15.0, False),  # user_A quota full
            ("allow_request", "user_B", 15.0, True),   # user_B has full quota
            ("allow_request", "user_B", 16.0, True),
        ],
    },
    {
        "id": "rl_invalid_inputs",
        "description": "Graceful handling of empty/None user_id and invalid timestamp without crash",
        "category": "invalid_input",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            ("allow_request", "", 10.0, False),
            ("allow_request", None, 10.0, False),
            ("allow_request", "user_1", "not_a_number", False),
            ("allow_request", "user_1", -50.0, False),
        ],
    },
    {
        "id": "rl_zero_capacity",
        "description": "RateLimiter initialized with max_requests=0 rejects all requests",
        "category": "boundary",
        "max_requests": 0,
        "window_seconds": 60.0,
        "ops": [
            ("allow_request", "user_1", 10.0, False),
            ("allow_request", "user_2", 20.0, False),
        ],
    },
    {
        "id": "rl_remaining_tokens_query",
        "description": "Accurately reports remaining available tokens per user",
        "category": "edge",
        "max_requests": 5,
        "window_seconds": 60.0,
        "ops": [
            ("get_remaining_tokens", "user_1", 10.0, 5),
            ("allow_request", "user_1", 10.0, True),
            ("get_remaining_tokens", "user_1", 10.0, 4),
            ("allow_request", "user_1", 12.0, True),
            ("get_remaining_tokens", "user_1", 12.0, 3),
        ],
    },
    {
        "id": "rl_high_throughput_perf",
        "description": "Performance stress test: 50,000 rapid check operations under 1.0 second",
        "category": "performance",
        "perf": True,
        "ops_count": 50000,
        "max_requests": 1000,
        "window_seconds": 60.0,
    },
]


def get_rate_limiter_benchmark() -> TaskSpecification:
    return TaskSpecification(
        task_id="rate_limiter_02",
        name="API Rate Limiter (Rolling 60s Window)",
        description=(
            "Implement a production-grade API Rate Limiter allowing a maximum of 5 requests per user "
            "within a rolling 60-second window. The limiter must eliminate boundary-burst vulnerabilities, "
            "maintain independent user quotas, and sanitize inputs defensively."
        ),
        programming_language="python",
        class_or_function_name="RateLimiter",
        functional_requirements=[
            "allow_request(user_id, timestamp) returns True if quota is available, else False.",
            "Enforce a rolling sliding window of 60 seconds (not a fixed reset window).",
            "get_remaining_tokens(user_id, timestamp) returns integer count of available slots.",
            "Timestamps older than (timestamp - window_seconds) must be automatically pruned.",
            "Handle non-positive max_requests (reject all) and invalid user_id/timestamp gracefully.",
            "Sub-millisecond amortized latency under high traffic.",
        ],
        input_output_spec={
            "init": {"max_requests": "int = 5", "window_seconds": "float = 60.0"},
            "allow_request": {"params": ["user_id: str", "timestamp: Optional[float]"], "returns": "bool"},
            "get_remaining_tokens": {"params": ["user_id: str", "timestamp: Optional[float]"], "returns": "int"},
        },
        constraints=[
            "Strict rolling window algorithm (sliding log or sliding window counter).",
            "O(1) or O(log N) amortized query time per user.",
            "Independent state per user.",
        ],
        expected_behavior="Strictly bounds burst requests across arbitrary 60-second intervals.",
        evaluation_criteria={
            "correctness": 0.60,
            "efficiency": 0.20,
            "safety": 0.10,
            "quality": 0.10,
        },
    )


# =====================================================================
# Trusted Reference Oracle Implementations (For Test Validation)
# =====================================================================

class LRUCacheOracle:
    """Trusted reference implementation of LRUCache for metamorphic test validation."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity if capacity > 0 else 0
        self.cache: Dict[Any, int] = {}
        self.order: deque = deque()

    def get(self, key: Any) -> int:
        if self.capacity <= 0:
            return -1
        try:
            hash(key)
        except TypeError:
            return -1

        if key in self.cache:
            try:
                self.order.remove(key)
            except ValueError:
                pass
            self.order.append(key)
            return self.cache[key]
        return -1

    def put(self, key: Any, value: int) -> None:
        if self.capacity <= 0:
            return
        try:
            hash(key)
        except TypeError:
            return

        if key in self.cache:
            try:
                self.order.remove(key)
            except ValueError:
                pass
            self.cache[key] = value
            self.order.append(key)
            return

        if len(self.cache) >= self.capacity:
            oldest = self.order.popleft()
            self.cache.pop(oldest, None)

        self.cache[key] = value
        self.order.append(key)


class RateLimiterOracle:
    """Trusted reference implementation of RateLimiter for metamorphic test validation."""

    def __init__(self, max_requests: int = 5, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests if max_requests > 0 else 0
        self.window_seconds = window_seconds if window_seconds > 0 else 0.0
        self.user_timestamps: Dict[str, deque] = {}

    def _sanitize(self, user_id: Any, timestamp: Any) -> Optional[tuple[str, float]]:
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

        # Prune timestamps older than or equal to cutoff
        while q and q[0] <= cutoff:
            q.popleft()

        if len(q) < self.max_requests:
            q.append(ts)
            return True
        return False

    def get_remaining_tokens(self, user_id: str, timestamp: Optional[float] = None) -> int:
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


# =====================================================================
# Task Registry
# =====================================================================

PREDEFINED_TASKS: Dict[str, TaskSpecification] = {
    "lru_cache_01": get_lru_benchmark(),
    "rate_limiter_02": get_rate_limiter_benchmark(),
}


def get_task(task_id: str) -> Optional[TaskSpecification]:
    return PREDEFINED_TASKS.get(task_id)


def list_available_tasks() -> List[Dict[str, Any]]:
    return [task.to_dict() for task in PREDEFINED_TASKS.values()]


def register_custom_task(task_spec: TaskSpecification) -> None:
    PREDEFINED_TASKS[task_spec.task_id] = task_spec
