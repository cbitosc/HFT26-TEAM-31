"""
simulate.py - Direct entry point to launch the real-time Pygame dungeon simulation.
Loads evolved policies (V1-V4) and opens the interactive visualizer window.
"""

import os
import json
import sys
from typing import List

from core.contracts import Policy, TestResult, Critique
from viz.gui_simulation import launch_simulation


def load_evolution_artifacts():
    """Loads all evolved policies, test results, and critiques from the evolution directory."""
    policies = []
    test_results = []
    critiques = []

    version = 1
    while os.path.exists(f"evolution/V{version}_policy.json"):
        with open(f"evolution/V{version}_policy.json", "r", encoding="utf-8") as f:
            policies.append(Policy.from_dict(json.load(f)))

        if os.path.exists(f"evolution/V{version}_test.json"):
            with open(f"evolution/V{version}_test.json", "r", encoding="utf-8") as f:
                test_results.append(TestResult.from_dict(json.load(f)))

        if os.path.exists(f"evolution/V{version}_critique.json"):
            with open(f"evolution/V{version}_critique.json", "r", encoding="utf-8") as f:
                critiques.append(Critique.from_dict(json.load(f)))

        version += 1

    return policies, test_results, critiques


def main():
    print("=" * 70)
    print("      LAUNCHING LIVE INTERACTIVE DUNGEON SIMULATION (PYGAME)")
    print("=" * 70)

    policies, test_results, critiques = load_evolution_artifacts()

    if not policies:
        print("[!] No evolution artifacts found in evolution/. Running evolution protocol first...")
        from main import main as run_evolution
        run_evolution()
        policies, test_results, critiques = load_evolution_artifacts()

    print(f"[✓] Loaded {len(policies)} evolved generations (V1 to V{len(policies)}).")
    print("\nStarting visual window...")
    print("Controls in window:")
    print("  [1, 2, 3, 4] : Switch between versions V1, V2, V3, V4 in real time")
    print("  [SPACE]      : Pause / Resume simulation")
    print("  [A]          : Toggle Cinematic Auto-Evolve mode")
    print("  [M]          : Cycle through all 10 dungeon benchmark maps")
    print("  [R]          : Replay active run")
    print("  [LEFT/RIGHT] : Adjust animation speed (0.5x to 4.0x)")
    print("  [ESC]        : Close simulation")

    launch_simulation(policies, test_results, critiques)


if __name__ == "__main__":
    main()

