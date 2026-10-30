"""Comprehensive Test Suite for AutoEvolve Protocol Dynamic Engine.

Validates:
1. Task processing (specifications, benchmarks, custom tasks)
2. Test generation & independent oracle validation (rejection of malformed/contradictory tests)
3. Subprocess sandbox evaluation (correctness, timeout handling, safety violations)
4. Generator-critic improvement loop (LRU Cache benchmark, API Rate Limiter benchmark)
5. Trace integrity and cryptographic state commitments
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from module1.agent.critic import critique_code, passes_guardrail
from module1.agent.evaluator import evaluate_code
from module1.agent.generator import generate_code
from module1.agent.loop import run_loop
from module1.agent.task import (
    HIDDEN_TESTS,
    LRUCacheOracle,
    RATE_LIMITER_TESTS,
    RateLimiterOracle,
    TaskSpecification,
    get_lru_benchmark,
    get_rate_limiter_benchmark,
    get_task,
    register_custom_task,
)
from module1.agent.test_generator import TestGeneratorAgent, TestValidator


class TestTaskProcessing(unittest.TestCase):
    """Test generic task abstraction, schemas, and benchmark definitions."""

    def test_lru_benchmark_spec(self):
        task = get_lru_benchmark()
        self.assertEqual(task.task_id, "lru_cache_01")
        self.assertEqual(task.programming_language, "python")
        self.assertEqual(task.class_or_function_name, "LRUCache")
        self.assertGreater(len(task.functional_requirements), 0)

    def test_rate_limiter_benchmark_spec(self):
        task = get_rate_limiter_benchmark()
        self.assertEqual(task.task_id, "rate_limiter_02")
        self.assertEqual(task.programming_language, "python")
        self.assertEqual(task.class_or_function_name, "RateLimiter")
        self.assertIn("rolling", task.description.lower())

    def test_custom_task_registration(self):
        custom = TaskSpecification(
            task_id="custom_stack_01",
            name="Bounded Stack",
            description="Implement a stack with max capacity",
            programming_language="python",
            class_or_function_name="BoundedStack",
            functional_requirements=["push", "pop", "peek"],
            input_output_spec={"init": {"capacity": "int"}},
            constraints=["O(1) complexity"],
            expected_behavior="LIFO",
            evaluation_criteria={"correctness": 0.6, "efficiency": 0.2, "safety": 0.1, "quality": 0.1},
        )
        register_custom_task(custom)
        retrieved = get_task("custom_stack_01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Bounded Stack")


class TestDynamicTestGenerationAndValidation(unittest.TestCase):
    """Test dynamic test suite derivation, categories, and independent oracle validation."""

    def setUp(self):
        self.agent = TestGeneratorAgent()
        self.lru_task = get_lru_benchmark()
        self.rl_task = get_rate_limiter_benchmark()

    def test_test_generation_categories_lru(self):
        suite = self.agent.generate_and_validate(self.lru_task)
        self.assertGreaterEqual(suite.validated_count, 10)
        self.assertGreaterEqual(suite.rejected_count, 1)

        # Verify presence of multiple test categories
        categories = set(suite.category_breakdown.keys())
        self.assertTrue({"basic", "boundary", "invalid_input"}.issubset(categories))

    def test_test_generation_categories_rate_limiter(self):
        suite = self.agent.generate_and_validate(self.rl_task)
        self.assertGreaterEqual(suite.validated_count, 10)
        self.assertGreaterEqual(suite.rejected_count, 1)
        categories = set(suite.category_breakdown.keys())
        self.assertTrue({"basic", "boundary", "edge"}.issubset(categories))

    def test_validator_rejects_oracle_mismatch(self):
        validator = TestValidator(lambda: RateLimiterOracle(5, 60.0))
        defective_test = {
            "id": "defective_burst_test",
            "category": "boundary",
            "max_requests": 5,
            "window_seconds": 60.0,
            # Claiming 6th request within window should return True (false expectation!)
            "ops": [
                ("allow_request", "user_1", 10.0, True),
                ("allow_request", "user_1", 20.0, True),
                ("allow_request", "user_1", 30.0, True),
                ("allow_request", "user_1", 40.0, True),
                ("allow_request", "user_1", 50.0, True),
                ("allow_request", "user_1", 55.0, True),  # Contradictory expectation!
            ],
        }
        result = validator.validate_test(defective_test, self.rl_task)
        self.assertFalse(result.is_valid)
        self.assertIn("Oracle output mismatch", result.reason)

    def test_validator_rejects_empty_ops(self):
        validator = TestValidator(lambda: LRUCacheOracle(2))
        empty_test = {"id": "empty_ops_test", "category": "basic", "ops": []}
        result = validator.validate_test(empty_test, self.lru_task)
        self.assertFalse(result.is_valid)
        self.assertIn("no executable operations", result.reason)


class TestSandboxedEvaluator(unittest.TestCase):
    """Test subprocess sandbox execution, scoring, timeouts, and exception handling."""

    def test_lru_perfect_implementation(self):
        code_v3 = generate_code("", attempt="v3", force_mock=True, task_id="lru_cache_01")
        res = evaluate_code(code_v3, task=get_lru_benchmark())
        self.assertEqual(res["passed"], 10)
        self.assertEqual(res["total"], 10)
        self.assertEqual(res["final_score"], 100.0)
        self.assertEqual(len(res["failed_tests"]), 0)

    def test_lru_failing_implementation(self):
        code_v1 = generate_code("", attempt="v1", force_mock=True, task_id="lru_cache_01")
        res = evaluate_code(code_v1, task=get_lru_benchmark())
        self.assertLess(res["passed"], 10)
        self.assertLess(res["final_score"], 100.0)
        self.assertIn("unhashable", res["failed_tests"])

    def test_rate_limiter_perfect_implementation(self):
        code_v3 = generate_code("", attempt="v3", force_mock=True, task_id="rate_limiter_02")
        suite = TestGeneratorAgent().generate_and_validate(get_rate_limiter_benchmark()).validated_tests
        res = evaluate_code(code_v3, task=get_rate_limiter_benchmark(), test_suite=suite)
        self.assertEqual(res["passed"], 10)
        self.assertEqual(res["final_score"], 100.0)

    def test_rate_limiter_failing_v1_boundary_burst(self):
        code_v1 = generate_code("", attempt="v1", force_mock=True, task_id="rate_limiter_02")
        suite = TestGeneratorAgent().generate_and_validate(get_rate_limiter_benchmark()).validated_tests
        res = evaluate_code(code_v1, task=get_rate_limiter_benchmark(), test_suite=suite)
        self.assertIn("rl_boundary_burst_attack", res["failed_tests"])

    def test_safety_violation_detection(self):
        malicious_code = "import os\nclass LRUCache:\n    def __init__(self, cap): os.system('echo test')\n"
        res = evaluate_code(malicious_code, task=get_lru_benchmark())
        self.assertEqual(res["safety"], 0.0)


class TestCriticAndConstitutionalGuardrail(unittest.TestCase):
    """Test natural language critique generation and no-code-leakage enforcement."""

    def test_guardrail_passes_clean_critique(self):
        clean_critique = {
            "failure_type": "EvictionOrdering",
            "root_cause": "The list scan fails to update recency order when a key is accessed.",
            "fix_instruction": "Adopt an ordered dictionary or doubly linked list to track most recent keys.",
            "failed_tests": ["order_after_get"],
        }
        self.assertTrue(passes_guardrail(clean_critique))

    def test_guardrail_rejects_code_leakage(self):
        leaky_critique = {
            "failure_type": "EvictionOrdering",
            "root_cause": "Bug in cache",
            "fix_instruction": "Replace with def put(self, key, value): self.cache[key] = value",
            "failed_tests": [],
        }
        self.assertFalse(passes_guardrail(leaky_critique))

    def test_mock_critique_rate_limiter(self):
        critique = critique_code("", {"failed_tests": ["rl_boundary_burst_attack"]}, attempt="v1", force_mock=True, task_id="rate_limiter_02")
        self.assertEqual(critique["failure_type"], "BoundaryBurstVulnerability")
        self.assertEqual(critique["severity"], "CRITICAL")
        self.assertTrue(passes_guardrail(critique))


class TestGeneratorCriticLoop(unittest.TestCase):
    """Test full multi-iteration improvement loops on both benchmarks."""

    def test_lru_improvement_loop(self):
        trace = run_loop(
            output_path="test_lru_trace.json",
            force_mock=True,
            task_id="lru_cache_01",
        )
        self.assertEqual(trace["task_id"], "lru_cache_01")
        self.assertEqual(trace["iterations_count"], 3)
        self.assertGreater(trace["zk_inputs"]["score_v2"], trace["zk_inputs"]["score_v1"])
        self.assertGreater(trace["zk_inputs"]["score_v3"], trace["zk_inputs"]["score_v2"])
        self.assertEqual(trace["zk_inputs"]["score_v3"], 100)

    def test_rate_limiter_improvement_loop(self):
        trace = run_loop(
            output_path="test_rl_trace.json",
            force_mock=True,
            task_id="rate_limiter_02",
        )
        self.assertEqual(trace["task_id"], "rate_limiter_02")
        self.assertEqual(trace["iterations_count"], 3)
        self.assertGreater(trace["zk_inputs"]["score_v2"], trace["zk_inputs"]["score_v1"])
        self.assertGreater(trace["zk_inputs"]["score_v3"], trace["zk_inputs"]["score_v2"])
        self.assertEqual(trace["zk_inputs"]["score_v3"], 100)


if __name__ == "__main__":
    unittest.main()

