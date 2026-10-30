"""Sandboxed Subprocess Unit-Test Evaluator for AutoEvolve Protocol.

Executes candidate implementations against validated test suites in an isolated
temporary directory. Evaluates correctness, amortized efficiency, safety against
crashes, and code quality while generating deterministic ZK-ready cryptographic
commitments.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional

try:
    from module1.agent.task import HIDDEN_TESTS, TaskSpecification, get_task
except ImportError:
    from agent.task import HIDDEN_TESTS, TaskSpecification, get_task

logger = logging.getLogger("AutoEvolve.Evaluator")


def evaluate_code(
    code_string: str,
    task: Optional[TaskSpecification] = None,
    test_suite: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Execute unit tests against code in an isolated subprocess sandbox.

    Args:
        code_string: Python source code of the candidate implementation.
        task: Optional TaskSpecification (defaults to LRU Cache if omitted).
        test_suite: Optional list of validated test dicts.

    Returns:
        Structured evaluation metrics including passed/total, failure lists,
        sub-scores, and cryptographic trace commitments.
    """
    if task is None:
        task = get_task("lru_cache_01")
    if test_suite is None:
        test_suite = HIDDEN_TESTS

    task_id = task.task_id if task else "lru_cache_01"
    is_rate_limiter = "rate" in task_id.lower() or "limiter" in task_id.lower()

    passed = 0
    failed_tests: List[str] = []
    test_details: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as temp_dir:
        solution_path = os.path.join(temp_dir, "solution.py")
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code_string)

        runner_path = os.path.join(temp_dir, "test_runner.py")

        for test in test_suite:
            test_id = test.get("id", "unnamed_test")
            category = test.get("category", "general")
            t_start = time.perf_counter()

            if test.get("perf"):
                # Performance stress test
                if is_rate_limiter:
                    perf_code = """import sys, time
sys.path.insert(0, ".")
from solution import RateLimiter

limiter = RateLimiter(max_requests=1000, window_seconds=60.0)
t0 = time.perf_counter()
for i in range(50000):
    limiter.allow_request(f"user_{i % 10}", float(i))
elapsed = time.perf_counter() - t0
print(f"ELAPSED:{elapsed:.4f}")
"""
                else:
                    perf_code = """import sys, time
sys.path.insert(0, ".")
from solution import LRUCache

cache = LRUCache(1000)
t0 = time.perf_counter()
for i in range(100000):
    cache.put(i % 1000, i)
    cache.get(i % 1000)
elapsed = time.perf_counter() - t0
print(f"ELAPSED:{elapsed:.4f}")
"""
                with open(runner_path, "w", encoding="utf-8") as rf:
                    rf.write(perf_code)

                try:
                    proc = subprocess.run(
                        [sys.executable, runner_path],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=4,
                    )
                    t_exec = time.perf_counter() - t_start

                    if proc.returncode != 0:
                        failed_tests.append(f"perf_crash_{proc.returncode}")
                        test_details.append({
                            "id": test_id,
                            "category": category,
                            "status": "failed",
                            "error": proc.stderr.strip()[:200],
                            "elapsed": round(t_exec, 4),
                        })
                    else:
                        elapsed_val = None
                        for line in proc.stdout.splitlines():
                            if line.startswith("ELAPSED:"):
                                elapsed_val = float(line.split(":")[1])
                                break

                        threshold = 1.0 if is_rate_limiter else 0.85
                        if elapsed_val is not None and elapsed_val < threshold:
                            passed += 1
                            test_details.append({
                                "id": test_id,
                                "category": category,
                                "status": "passed",
                                "elapsed": elapsed_val,
                            })
                        else:
                            fail_reason = f"perf_{elapsed_val:.4f}s" if elapsed_val else "perf_no_elapsed_output"
                            failed_tests.append(fail_reason)
                            test_details.append({
                                "id": test_id,
                                "category": category,
                                "status": "failed",
                                "reason": fail_reason,
                                "elapsed": elapsed_val or t_exec,
                            })
                except subprocess.TimeoutExpired:
                    failed_tests.append("perf_timeout_>4s")
                    test_details.append({
                        "id": test_id,
                        "category": category,
                        "status": "failed",
                        "reason": "Execution timed out (>4.0s)",
                        "elapsed": 4.0,
                    })
                except Exception as e:
                    failed_tests.append(f"perf_error_{str(e)}")
                    test_details.append({
                        "id": test_id,
                        "category": category,
                        "status": "failed",
                        "reason": str(e),
                        "elapsed": 0.0,
                    })

            else:
                # Functional & boundary tests
                if is_rate_limiter:
                    max_req = test.get("max_requests", 5)
                    win_sec = test.get("window_seconds", 60.0)
                    ops = test.get("ops", [])

                    test_runner_code = f"""import sys
sys.path.insert(0, ".")
from solution import RateLimiter

max_req = {max_req}
win_sec = {win_sec}
limiter = RateLimiter(max_req, win_sec)
ops = {repr(ops)}

for op in ops:
    method = op[0]
    if method == "allow_request":
        user_id = op[1]
        ts = op[2]
        expected = op[3]
        res = limiter.allow_request(user_id, ts)
        if res != expected:
            sys.exit(2)
    elif method == "get_remaining_tokens":
        user_id = op[1]
        ts = op[2]
        expected = op[3]
        res = limiter.get_remaining_tokens(user_id, ts)
        if res != expected:
            sys.exit(3)
sys.exit(0)
"""
                else:
                    # LRUCache test harness
                    cap = test.get("capacity", 2)
                    ops = test.get("ops", [])

                    test_runner_code = f"""import sys
sys.path.insert(0, ".")
from solution import LRUCache

cap = {cap}
cache = LRUCache(cap)
ops = {repr(ops)}

for op in ops:
    action = op[0]
    if action == "put":
        cache.put(op[1], op[2])
    elif action == "get":
        key = op[1]
        expected = op[2]
        res = cache.get(key)
        if res != expected:
            sys.exit(2)
sys.exit(0)
"""
                with open(runner_path, "w", encoding="utf-8") as rf:
                    rf.write(test_runner_code)

                try:
                    proc = subprocess.run(
                        [sys.executable, runner_path],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=3,
                    )
                    t_exec = time.perf_counter() - t_start

                    if proc.returncode == 0:
                        passed += 1
                        test_details.append({
                            "id": test_id,
                            "category": category,
                            "description": test.get("description", ""),
                            "status": "passed",
                            "elapsed": round(t_exec, 4),
                        })
                    else:
                        failed_tests.append(test_id)
                        test_details.append({
                            "id": test_id,
                            "category": category,
                            "description": test.get("description", ""),
                            "status": "failed",
                            "exit_code": proc.returncode,
                            "stderr": proc.stderr.strip()[:200],
                            "elapsed": round(t_exec, 4),
                        })
                except subprocess.TimeoutExpired:
                    failed_tests.append(f"{test_id}_timeout")
                    test_details.append({
                        "id": test_id,
                        "category": category,
                        "description": test.get("description", ""),
                        "status": "failed",
                        "reason": "timeout",
                        "elapsed": 3.0,
                    })
                except Exception as e:
                    failed_tests.append(f"{test_id}_error")
                    test_details.append({
                        "id": test_id,
                        "category": category,
                        "description": test.get("description", ""),
                        "status": "failed",
                        "reason": str(e),
                        "elapsed": 0.0,
                    })

    total_tests = len(test_suite)
    correctness = (passed / total_tests) * 100.0 if total_tests > 0 else 0.0

    efficiency = 100.0 if not any(f.startswith("perf") for f in failed_tests) else 30.0

    # Defensive safety checks
    if "eval(" in code_string or "os.system" in code_string or "__import__" in code_string:
        safety = 0.0
    elif any("unhashable" in f or "invalid_input" in f for f in failed_tests):
        safety = 50.0
    else:
        safety = 100.0

    quality = 50.0
    if '"""' in code_string or "'''" in code_string:
        quality += 20.0
    if "class " in code_string:
        quality += 15.0
    if "->" in code_string:
        quality += 15.0
    quality = min(quality, 100.0)

    final_score = round(correctness * 0.6 + efficiency * 0.2 + safety * 0.1 + quality * 0.1, 1)

    # Deterministic Cryptographic Hashes (ZK-ready BN254 scalar field safe)
    trace_hash_hex = hashlib.sha256(f"{code_string.strip()}|{passed}|{final_score}".encode("utf-8")).hexdigest()
    trace_hash_zk = str(int(trace_hash_hex[:62], 16))

    return {
        "passed": passed,
        "total": total_tests,
        "failed_tests": failed_tests,
        "correctness": round(correctness, 1),
        "efficiency": round(efficiency, 1),
        "safety": round(safety, 1),
        "quality": round(quality, 1),
        "final_score": final_score,
        "trace_hash_hex": trace_hash_hex,
        "trace_hash_zk": trace_hash_zk,
        "test_details": test_details,
    }
