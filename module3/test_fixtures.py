"""Test fixtures and mock datasets for Module 3: Semantic Memory & Skill Registry.

Contains realistic agent run snapshots, unified diffs, failure critiques,
and pre-configured mock registry records.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List

# Unified diff for LRU Cache with TTL fix (V1 -> V3)
LRU_CACHE_UNIFIED_DIFF = """--- a/lru_cache.py
+++ b/lru_cache.py
@@ -10,7 +10,12 @@
     def __init__(self, capacity: int, ttl_seconds: float = 60.0):
-        self.capacity = capacity
+        if capacity <= 0:
+            # Guard against invalid or zero capacity to prevent index and modulo errors
+            self.capacity = 0
+            self.cache = {}
+            return
+        self.capacity = capacity
         self.ttl = ttl_seconds
         self.cache = {}
         self.expiry_tracker = OrderedDict()
@@ -25,6 +30,8 @@
     def put(self, key: str, value: Any) -> None:
+        if self.capacity <= 0:
+            return
         now = time.time()
         if key in self.cache:
             del self.cache[key]
"""

# Realistic cryptographic trace hashes
V1_LOG_HASH = int(hashlib.sha256(b"AGENT_LOOP_V1_FAILED_RUN_LRU_CACHE_ZERO_CAP").hexdigest()[:16], 16)
V3_LOG_HASH = int(hashlib.sha256(b"AGENT_LOOP_V3_SUCCESSFUL_VERIFIED_LRU_CACHE").hexdigest()[:16], 16)
PROMPT_COMMITMENT = int(hashlib.sha256(b"PROMPT_COMMITMENT_ZK_VERIFIED_V3").hexdigest()[:16], 16)
TRACE_HASH = hashlib.sha256(b"TRACE_EVM_EXECUTION_LRU_CACHE_PASS").hexdigest()

# Canonical LRU Cache with TTL mock snapshot
LRU_CACHE_MOCK_SNAPSHOT: Dict[str, Any] = {
    "task_id": "task_lru_cache_ttl_v3",
    "task_type": "data_structure_optimization",
    "failure_signature": "edge_case_capacity_zero",
    "root_cause": "Missing early guard for capacity <= 0 causing IndexError",
    "fix_strategy": "Return immediately on capacity <= 0 or initialize with None guard",
    "code_diff": LRU_CACHE_UNIFIED_DIFF,
    "trace_hash": TRACE_HASH,
    "log_hash_v1": hex(V1_LOG_HASH),
    "log_hash_v3": hex(V3_LOG_HASH),
    "prompt_commitment": hex(PROMPT_COMMITMENT),
    "agent_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "timestamp": int(time.time()),
    "framework": "AutoEvolve-Protocol-v1",
}

# Secondary snapshot: Rate Limiter Token Bucket (used for negative / cross-domain similarity tests)
RATE_LIMITER_DIFF = """--- a/rate_limiter.py
+++ b/rate_limiter.py
@@ -5,3 +5,6 @@
     def consume(self, tokens: int = 1) -> bool:
+        now = time.monotonic()
+        self._refill(now)
+        if self.available_tokens < tokens:
+            return False
"""
RATE_LIMITER_MOCK_SNAPSHOT: Dict[str, Any] = {
    "task_id": "task_rate_limiter_token_bucket",
    "task_type": "networking_concurrency",
    "failure_signature": "concurrency_token_exhaustion_deadlock",
    "root_cause": "Race condition in thread lock release during bucket refill under load",
    "fix_strategy": "Wrap refill calculation inside atomic reentrant lock context",
    "code_diff": RATE_LIMITER_DIFF,
    "trace_hash": hashlib.sha256(b"TRACE_RATE_LIMITER_PASS").hexdigest(),
    "log_hash_v1": hex(int(hashlib.sha256(b"V1_FAIL_LIMIT").hexdigest()[:16], 16)),
    "log_hash_v3": hex(int(hashlib.sha256(b"V3_PASS_LIMIT").hexdigest()[:16], 16)),
    "prompt_commitment": hex(int(hashlib.sha256(b"PROMPT_LIMIT").hexdigest()[:16], 16)),
    "agent_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "timestamp": int(time.time()),
    "framework": "AutoEvolve-Protocol-v1",
}

# Scenario: JWT Token Expiration and Clock Skew
JWT_AUTH_DIFF = """--- a/auth_service.py
+++ b/auth_service.py
@@ -42,3 +42,5 @@
     try:
-        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
+        # Allow 60 seconds clock skew tolerance for distributed token verification
+        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], leeway=60)
         return payload
"""
JWT_AUTH_MOCK_SNAPSHOT: Dict[str, Any] = {
    "task_id": "task_jwt_auth_clock_drift",
    "task_type": "security_authentication",
    "failure_signature": "jwt_signature_expired_clock_skew",
    "root_cause": "ExpiredSignatureError raised when server and client clocks differ by a few seconds without leeway",
    "fix_strategy": "Add leeway parameter of 60 seconds to jwt.decode to tolerate clock drift across distributed services",
    "code_diff": JWT_AUTH_DIFF,
    "trace_hash": hashlib.sha256(b"TRACE_JWT_AUTH_PASS").hexdigest(),
    "log_hash_v1": hex(int(hashlib.sha256(b"V1_FAIL_JWT").hexdigest()[:16], 16)),
    "log_hash_v3": hex(int(hashlib.sha256(b"V3_PASS_JWT").hexdigest()[:16], 16)),
    "prompt_commitment": hex(int(hashlib.sha256(b"PROMPT_JWT").hexdigest()[:16], 16)),
    "agent_address": "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
    "timestamp": int(time.time()),
    "framework": "AutoEvolve-Protocol-v1",
}

# Scenario: Redis Distributed Lock Deadlock
REDIS_LOCK_DIFF = """--- a/distributed_lock.py
+++ b/distributed_lock.py
@@ -25,4 +25,8 @@
-    def acquire(self, key: str) -> bool:
-        return bool(self.redis.set(key, self.owner_id, nx=True))
+    def acquire(self, key: str, ttl_ms: int = 5000) -> bool:
+        # Atomic SET with NX and PX prevents orphaned locks on worker crash
+        return bool(self.redis.set(key, self.owner_id, nx=True, px=ttl_ms))
+
+    def release(self, key: str) -> bool:
+        # Atomic Lua script ensures token is only released by the true owner
+        LUA_RELEASE = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
+        return bool(self.redis.eval(LUA_RELEASE, 1, key, self.owner_id))
"""
REDIS_LOCK_MOCK_SNAPSHOT: Dict[str, Any] = {
    "task_id": "task_redis_lock_crash_resilience",
    "task_type": "distributed_systems_concurrency",
    "failure_signature": "redis_distributed_lock_deadlock",
    "root_cause": "Worker process crashed while holding lock without TTL auto-expiration or release guard",
    "fix_strategy": "Set atomic key expiration with SET NX PX and use Lua script for atomic token release",
    "code_diff": REDIS_LOCK_DIFF,
    "trace_hash": hashlib.sha256(b"TRACE_REDIS_LOCK_PASS").hexdigest(),
    "log_hash_v1": hex(int(hashlib.sha256(b"V1_FAIL_REDIS").hexdigest()[:16], 16)),
    "log_hash_v3": hex(int(hashlib.sha256(b"V3_PASS_REDIS").hexdigest()[:16], 16)),
    "prompt_commitment": hex(int(hashlib.sha256(b"PROMPT_REDIS").hexdigest()[:16], 16)),
    "agent_address": "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
    "timestamp": int(time.time()),
    "framework": "AutoEvolve-Protocol-v1",
}

# Scenario: Database Connection Pool Exhaustion
SQL_POOL_DIFF = """--- a/db_session.py
+++ b/db_session.py
@@ -18,5 +18,8 @@
-    def get_db():
-        db = SessionLocal()
-        return db
+    from contextlib import asynccontextmanager
+    @asynccontextmanager
+    async def get_db():
+        async with AsyncSessionLocal() as session:
+            try:
+                yield session
+            finally:
+                await session.close()
"""
SQL_POOL_MOCK_SNAPSHOT: Dict[str, Any] = {
    "task_id": "task_sqlalchemy_pool_leak",
    "task_type": "database_resource_management",
    "failure_signature": "sqlalchemy_connection_pool_exhaustion",
    "root_cause": "Unclosed session in exception handler leaves connection checked out until pool runs dry",
    "fix_strategy": "Enforce context manager with try-finally to guarantee session.close() returning conn to pool",
    "code_diff": SQL_POOL_DIFF,
    "trace_hash": hashlib.sha256(b"TRACE_SQL_POOL_PASS").hexdigest(),
    "log_hash_v1": hex(int(hashlib.sha256(b"V1_FAIL_SQL").hexdigest()[:16], 16)),
    "log_hash_v3": hex(int(hashlib.sha256(b"V3_PASS_SQL").hexdigest()[:16], 16)),
    "prompt_commitment": hex(int(hashlib.sha256(b"PROMPT_SQL").hexdigest()[:16], 16)),
    "agent_address": "0x9965507D1a55bcC2695C58ba16FB37d819B0A4df",
    "timestamp": int(time.time()),
    "framework": "AutoEvolve-Protocol-v1",
}

# Scenario: Binary Search Midpoint Overflow
BINARY_SEARCH_DIFF = """--- a/binary_search.py
+++ b/binary_search.py
@@ -12,3 +12,4 @@
     while low <= high:
-        mid = (low + high) // 2
+        # Avoid integer overflow on large sequences by computing offset from low
+        mid = low + ((high - low) // 2)
         if arr[mid] == target:
"""
BINARY_SEARCH_MOCK_SNAPSHOT: Dict[str, Any] = {
    "task_id": "task_binary_search_overflow",
    "task_type": "algorithmic_numerical_precision",
    "failure_signature": "binary_search_integer_overflow",
    "root_cause": "Standard midpoint calculation (low + high) // 2 causes integer overflow or rounding inaccuracies",
    "fix_strategy": "Compute midpoint as low + (high - low) // 2 to prevent overflow in index calculation",
    "code_diff": BINARY_SEARCH_DIFF,
    "trace_hash": hashlib.sha256(b"TRACE_BIN_SEARCH_PASS").hexdigest(),
    "log_hash_v1": hex(int(hashlib.sha256(b"V1_FAIL_BIN").hexdigest()[:16], 16)),
    "log_hash_v3": hex(int(hashlib.sha256(b"V3_PASS_BIN").hexdigest()[:16], 16)),
    "prompt_commitment": hex(int(hashlib.sha256(b"PROMPT_BIN").hexdigest()[:16], 16)),
    "agent_address": "0x976EA74026E726554dB657fA54763abd0C3a0aa9",
    "timestamp": int(time.time()),
    "framework": "AutoEvolve-Protocol-v1",
}

# Default Mock CIDs (deterministic IPFS v1 CID format)
MOCK_LRU_CID = "bafybeicg2k3p6h4f5q7y3x8w9z0lrucachezeroedgecase0001"
MOCK_RATE_LIMITER_CID = "bafybeih5a2m4b8v1c9x7z6w5e3r1ratelimitertoken0002"

# Mock registry records mirroring AutoEvolveRegistry.getAllRecords()
MOCK_REGISTRY_RECORDS: List[Dict[str, Any]] = [
    {
        "agent": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        "cid": MOCK_LRU_CID,
        "failure_signature": "edge_case_capacity_zero",
        "logHashV1": V1_LOG_HASH,
        "logHashV3": V3_LOG_HASH,
        "promptCommitment": PROMPT_COMMITMENT,
        "timestamp": int(time.time()) - 3600,
        "_payload": LRU_CACHE_MOCK_SNAPSHOT,
    },
    {
        "agent": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        "cid": MOCK_RATE_LIMITER_CID,
        "failure_signature": "concurrency_token_exhaustion_deadlock",
        "logHashV1": int(hashlib.sha256(b"V1_FAIL_LIMIT").hexdigest()[:16], 16),
        "logHashV3": int(hashlib.sha256(b"V3_PASS_LIMIT").hexdigest()[:16], 16),
        "promptCommitment": int(hashlib.sha256(b"PROMPT_LIMIT").hexdigest()[:16], 16),
        "timestamp": int(time.time()) - 1800,
        "_payload": RATE_LIMITER_MOCK_SNAPSHOT,
    },
]


def get_lru_cache_fixture() -> Dict[str, Any]:
    """Return a fresh copy of the canonical LRU cache failure snapshot."""
    return dict(LRU_CACHE_MOCK_SNAPSHOT)


def get_all_domain_fixtures() -> List[Dict[str, Any]]:
    """Return a fresh list of realistic failure snapshots across diverse domains."""
    return [
        dict(LRU_CACHE_MOCK_SNAPSHOT),
        dict(JWT_AUTH_MOCK_SNAPSHOT),
        dict(REDIS_LOCK_MOCK_SNAPSHOT),
        dict(SQL_POOL_MOCK_SNAPSHOT),
        dict(BINARY_SEARCH_MOCK_SNAPSHOT),
    ]


def get_mock_registry_records() -> List[Dict[str, Any]]:
    """Return a fresh list of pre-configured mock registry records."""
    return [dict(rec) for rec in MOCK_REGISTRY_RECORDS]

