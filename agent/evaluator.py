"""
AutoEvolve Protocol - Sandboxed Subprocess Unit-Test Evaluator
"""

import os
import sys
import time
import hashlib
import tempfile
import subprocess
from typing import Dict, Any, List

try:
    from agent.task import HIDDEN_TESTS
except ImportError:
    from task import HIDDEN_TESTS


def evaluate_code(code_string: str) -> Dict[str, Any]:
    """
    Executes unit tests against the provided code string in an isolated subprocess sandbox.
    Calculates sub-scores (correctness, efficiency, safety, quality) and computes
    cryptographic commitments for ZK proof generation.
    """
    passed = 0
    failed_tests: List[str] = []
    test_details: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as temp_dir:
        # Write solution to isolated temporary directory
        solution_path = os.path.join(temp_dir, "solution.py")
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code_string)

        runner_path = os.path.join(temp_dir, "test_runner.py")

        for test in HIDDEN_TESTS:
            test_id = test["id"]

            if test.get("perf"):
                # High-throughput performance benchmark (100k operations)
                perf_code = """import sys
import time
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
                    if proc.returncode != 0:
                        failed_tests.append(f"perf_crash_{proc.returncode}")
                        test_details.append({"id": test_id, "status": "failed", "error": proc.stderr.strip()})
                    else:
                        elapsed_val = None
                        for line in proc.stdout.splitlines():
                            if line.startswith("ELAPSED:"):
                                elapsed_val = float(line.split(":")[1])
                                break
                        if elapsed_val is not None:
                            if elapsed_val < 0.85:
                                passed += 1
                                test_details.append({"id": test_id, "status": "passed", "elapsed": elapsed_val})
                            else:
                                fail_reason = f"perf_{elapsed_val:.4f}s"
                                failed_tests.append(fail_reason)
                                test_details.append({"id": test_id, "status": "failed", "reason": fail_reason})
                        else:
                            failed_tests.append("perf_no_elapsed_output")
                            test_details.append({"id": test_id, "status": "failed", "reason": "missing output"})
                except subprocess.TimeoutExpired:
                    fail_reason = "perf_timeout_>4s"
                    failed_tests.append(fail_reason)
                    test_details.append({"id": test_id, "status": "failed", "reason": fail_reason})
                except Exception as e:
                    failed_tests.append(f"perf_error_{str(e)}")
                    test_details.append({"id": test_id, "status": "failed", "reason": str(e)})

            else:
                # Standard functional & edge-case test
                cap = test.get("capacity", 2)
                ops = test["ops"]

                test_runner_code = f"""import sys
sys.path.insert(0, ".")
from solution import LRUCache

cap = {cap}
cache = LRUCache(cap)
ops = {repr(ops)}

for op in ops:
    action = op[0]
    if action == "put":
        # Notice: intentionally unhandled try/except to catch unhashable crash
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
                    if proc.returncode == 0:
                        passed += 1
                        test_details.append({"id": test_id, "status": "passed"})
                    else:
                        failed_tests.append(test_id)
                        test_details.append({
                            "id": test_id,
                            "status": "failed",
                            "exit_code": proc.returncode,
                            "stderr": proc.stderr.strip()[:200]
                        })
                except subprocess.TimeoutExpired:
                    failed_tests.append(f"{test_id}_timeout")
                    test_details.append({"id": test_id, "status": "failed", "reason": "timeout"})
                except Exception as e:
                    failed_tests.append(f"{test_id}_error")
                    test_details.append({"id": test_id, "status": "failed", "reason": str(e)})

    # Sub-scores computation as specified by protocol
    total_tests = len(HIDDEN_TESTS)
    correctness = (passed / total_tests) * 100.0

    efficiency = 100.0 if not any(f.startswith("perf") for f in failed_tests) else 30.0

    if "eval(" in code_string or "os.system" in code_string:
        safety = 0.0
    elif any("unhashable" in f for f in failed_tests):
        safety = 50.0
    else:
        safety = 100.0

    quality = 50.0
    if '"""' in code_string or "'''" in code_string:
        quality += 20.0
    if "class Node" in code_string:
        quality += 20.0
    if "->" in code_string:
        quality += 10.0
    quality = min(quality, 100.0)

    final_score = round(correctness * 0.6 + efficiency * 0.2 + safety * 0.1 + quality * 0.1, 1)

    # Deterministic Cryptographic Hashes (ZK-ready BN254 scalar field safe)
    # 62 hex chars = 248 bits, strictly less than BN254 scalar field order r (~2^253.7)
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

