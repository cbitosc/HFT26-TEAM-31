"""
tests/test_task2_extension.py - Comprehensive Unit Tests for Task 2 Extension (Simulation2 Integration).

Validates:
1. Cross-Agent Memory Loading and failure trace counting.
2. Graceful failure when Task 1 memory is missing ("Run Task 1 first").
3. Agent 2 single-shot generation citing past failures.
4. Deterministic evaluation meeting single-attempt thresholds (>= 85% success, >= 5/6 treasure).
5. Ablation verification (< 40% success rate without memory).
6. Demo proof visual rendering on identical benchmark map.
"""

import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIM2_DIR = REPO_ROOT / "Simulation2"
MODULE1_DIR = REPO_ROOT / "module1"

for p in [str(REPO_ROOT), str(SIM2_DIR), str(MODULE1_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from module1.agent.task2_dungeon_agent import (
    Task1MemoryLoader,
    Agent2SingleShotGenerator,
    run_task2_dungeon,
    evaluate_agent2,
    run_ablation,
    load_fixed_maps,
    Policy,
    TestResult,
)


class TestTask2Extension(unittest.TestCase):

    def test_memory_loader_missing_ledger(self):
        """Verifies that attempting to load a missing memory ledger raises 'Run Task 1 first'."""
        with self.assertRaises(RuntimeError) as ctx:
            Task1MemoryLoader.load("nonexistent_path_xyz_123")
        self.assertEqual(str(ctx.exception), "Run Task 1 first")

    def test_memory_loader_success(self):
        """Verifies memory loader loads all versions and counts 200 failure traces."""
        evo_dir = SIM2_DIR / "evolution"
        memory = Task1MemoryLoader.load(evo_dir)

        self.assertGreaterEqual(memory.version_count, 4)
        self.assertGreaterEqual(memory.total_failure_traces, 200)
        self.assertGreaterEqual(len(memory.policies), 4)
        self.assertGreaterEqual(len(memory.test_results), 4)
        self.assertGreaterEqual(len(memory.critiques), 4)
        self.assertIn("generator_system", memory.evolved_prompts)

    def test_agent2_single_shot_derivation(self):
        """Verifies Agent 2 generates a valid Policy in a single shot citing past failures."""
        evo_dir = SIM2_DIR / "evolution"
        memory = Task1MemoryLoader.load(evo_dir)

        policy = Agent2SingleShotGenerator.generate(memory, live=False)

        self.assertEqual(type(policy).__name__, "Policy")
        self.assertEqual(policy.version, 1)  # Agent 2's single attempt
        self.assertEqual(set(policy.COSTS.keys()), {"lava", "monster", "treasure", "step"})
        self.assertGreaterEqual(policy.avoidance_radius, 2)

        # Verify changelog cites past failures
        changelog_lower = policy.changelog.lower()
        self.assertTrue("v1" in changelog_lower or "monster" in changelog_lower)
        self.assertTrue("v2" in changelog_lower or "lava" in changelog_lower)
        self.assertTrue("derived from" in changelog_lower or "memory" in changelog_lower)

    def test_deterministic_tester_single_attempt(self):
        """Verifies deterministic Tester evaluates Agent 2 policy with >= 85% success and >= 5/6 treasure."""
        policy = Policy(
            version=1,
            COSTS={"lava": 100, "monster": 50, "treasure": -15, "step": 1},
            avoidance_radius=2,
            changelog="Optimal derived policy"
        )

        tr = evaluate_agent2(policy)

        self.assertGreaterEqual(tr.success_rate, 0.85, f"Expected success rate >= 85%, got {tr.success_rate*100}%")
        self.assertGreaterEqual(tr.avg_treasure, 2.5, f"Expected treasure >= 2.5/3 (>= 5/6), got {tr.avg_treasure}")
        self.assertEqual(tr.death_by_lava_pct, 0.0)
        self.assertEqual(tr.death_by_monster_pct, 0.0)
        self.assertGreater(tr.score, 0.900)

    def test_ablation_without_memory(self):
        """Verifies ablation check: Agent 2 without memory fails (< 40% success)."""
        baseline_policy, ablation_tr = run_ablation()

        self.assertLess(ablation_tr.success_rate, 0.40, f"Expected ablation success < 40%, got {ablation_tr.success_rate*100}%")
        self.assertLess(ablation_tr.score, 0.35)

    def test_task2_end_to_end_payload(self):
        """Verifies full Task 2 run returns complete payload and writes artifacts."""
        evo_dir = SIM2_DIR / "evolution"
        res = run_task2_dungeon(live=False, evolution_dir=evo_dir)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res["single_attempt_passed"])
        self.assertTrue(res["ablation"]["ablation_passed"])
        self.assertGreaterEqual(res["test_result"]["success_rate"], 0.85)
        self.assertTrue((evo_dir / "Agent2_policy.json").exists())
        self.assertTrue((evo_dir / "Agent2_test.json").exists())
        self.assertTrue((evo_dir / "v1_vs_agent2_comparison.png").exists())
        self.assertGreater(os.path.getsize(evo_dir / "v1_vs_agent2_comparison.png"), 10000)


if __name__ == "__main__":
    unittest.main()
