"""
agent2.py - Direct entry point to execute Task 2 (Agent 2 Single-Shot Memory Learner).
Consumes Agent 1 memory from Task 1, solves the dungeon in 1 attempt,
evaluates deterministically, and verifies Pillar 4.
"""

import sys
from pathlib import Path

# Ensure Simulation2 root is on path
SIM2_DIR = Path(__file__).resolve().parent
if str(SIM2_DIR) not in sys.path:
    sys.path.insert(0, str(SIM2_DIR))

from core.agent2 import run_task2


def main():
    live = "--live" in sys.argv
    run_ablation = "--no-ablation" not in sys.argv

    try:
        res = run_task2(
            evolution_dir=SIM2_DIR / "evolution",
            live=live,
            run_ablation_check=run_ablation
        )
        print("\n" + "=" * 70)
        print(" TASK 2 EXECUTION SUCCESSFUL")
        print("=" * 70)
        print(f"Agent: {res['agent']}")
        print(f"Versions Loaded from Memory: {res['memory_versions_loaded']}")
        print(f"Total Failure Traces Analyzed: {res['total_failure_traces_loaded']}")
        print(f"Single Attempt Success Rate: {res['test_result']['success_rate']*100:.1f}% (Required >= 85%)")
        print(f"Avg Treasure Collected: {res['test_result']['avg_treasure']:.2f}/3.0 (Required >= 2.5)")
        print(f"Ablation Check (Without Memory): {res['ablation']['without_memory_success_rate']*100:.1f}% (Required < 40%)")
        print(f"Cross-Agent Memory Advantage: +{res['ablation']['delta_gain_percentage']}% gain in single shot!")
        print(f"Agent 2 Reasoning: {res['reasoning']}")
        print("=" * 70)
    except RuntimeError as e:
        if str(e) == "Run Task 1 first":
            print(f"\n[ERROR] {e}")
            sys.exit(1)
        raise


if __name__ == "__main__":
    main()

