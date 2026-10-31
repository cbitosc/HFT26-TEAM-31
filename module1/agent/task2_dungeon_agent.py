"""
module1/agent/task2_dungeon_agent.py - Module 1 Task 2 Extension (Simulation2 Integration).

Implements Cross-Agent Memory Integration for AutoEvolve Protocol:
- Task 1: Agent 1 Genesis + G-T-C iterative loop, generating the full evolution ledger.
- Task 2: Agent 2 Single-Shot solver consuming Task 1's complete memory ledger.
- Reuses Simulation2's deterministic physics simulator and Tester without rewriting logic.
- Verifies Pillar 4: Cross-Agent Memory prevents repeating mistakes.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Locate repo root and Simulation2
MODULE1_AGENT_DIR = Path(__file__).resolve().parent
MODULE1_DIR = MODULE1_AGENT_DIR.parent
REPO_ROOT = MODULE1_DIR.parent
SIM2_DIR = REPO_ROOT / "Simulation2"

for p in [str(REPO_ROOT), str(MODULE1_DIR), str(SIM2_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from Simulation2.core.contracts import Policy, TestResult, Critique
    from Simulation2.core.agent2 import (
        Task1Memory,
        Task1MemoryLoader,
        Agent2SingleShotGenerator,
        evaluate_agent2,
        run_ablation,
        run_task2 as _sim2_run_task2,
    )
    from Simulation2.core.tester import tester
    from Simulation2.core.map_generator import load_fixed_maps
    from Simulation2.main import run_task1 as _sim2_run_task1
except ImportError:
    # If Simulation2 folder is on sys.path directly
    from core.contracts import Policy, TestResult, Critique
    from core.agent2 import (
        Task1Memory,
        Task1MemoryLoader,
        Agent2SingleShotGenerator,
        evaluate_agent2,
        run_ablation,
        run_task2 as _sim2_run_task2,
    )
    from core.tester import tester
    from core.map_generator import load_fixed_maps
    from main import run_task1 as _sim2_run_task1


def get_default_evolution_dir() -> Path:
    """Returns canonical evolution directory path."""
    candidates = [
        SIM2_DIR / "evolution",
        REPO_ROOT / "evolution",
        MODULE1_DIR / "evolution",
    ]
    for c in candidates:
        if c.is_dir() and (c / "V1_policy.json").exists():
            return c
    return SIM2_DIR / "evolution"


def load_task1_memory(evolution_dir: Optional[str | Path] = None) -> Task1Memory:
    """Memory loader that reads the entire evolution ledger from Task 1.

    Fails with 'Run Task 1 first' if ledger is not present.
    """
    target_dir = Path(evolution_dir) if evolution_dir else get_default_evolution_dir()
    return Task1MemoryLoader.load(target_dir)


def run_task1_dungeon(live: bool = False) -> Dict[str, Any]:
    """Executes Task 1 (Agent 1): Phase 0 Genesis + Phase 1 G-T-C loop until convergence.

    Builds the full memory ledger with failure traces, critiques, and evolved prompts.
    """
    old_cwd = os.getcwd()
    try:
        os.chdir(str(SIM2_DIR))
        policies, test_results, critiques = _sim2_run_task1()
        return {
            "status": "TASK_1_CONVERGED",
            "version_count": len(policies),
            "final_score": critiques[-1].score if critiques else 0.0,
            "final_success_rate": test_results[-1].success_rate if test_results else 0.0,
            "ledger_path": str(SIM2_DIR / "evolution" / "memory_ledger.json")
        }
    finally:
        os.chdir(old_cwd)


def run_task2_dungeon(live: bool = False, evolution_dir: Optional[str | Path] = None) -> Dict[str, Any]:
    """Executes Task 2 (Agent 2): Single-shot dungeon solve using Task 1 memory.

    - Exactly ONE attempt, no iterative loop, no retry.
    - Explicitly cites >= 2 past failures in reasoning.
    - Evaluated deterministically with the same 10 fixed maps.
    - Performs ablation check (< 40% without memory).
    - Fails gracefully with 'Run Task 1 first' if memory is missing.
    """
    target_dir = Path(evolution_dir) if evolution_dir else get_default_evolution_dir()
    old_cwd = os.getcwd()
    try:
        os.chdir(str(SIM2_DIR))
        return _sim2_run_task2(evolution_dir=target_dir, live=live, run_ablation_check=True)
    finally:
        os.chdir(old_cwd)


__all__ = [
    "Task1Memory",
    "Task1MemoryLoader",
    "Agent2SingleShotGenerator",
    "load_task1_memory",
    "run_task1_dungeon",
    "run_task2_dungeon",
    "evaluate_agent2",
    "run_ablation",
    "tester",
    "load_fixed_maps",
]

