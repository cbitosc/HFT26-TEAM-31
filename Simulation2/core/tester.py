"""
core/tester.py - Deterministic test harness and ground-truth evaluation.
Simulates policies over a suite of maps without any LLM dependencies.
"""

from typing import List, Optional
from core.contracts import Policy, TestResult
from core.map_generator import DungeonMap, load_fixed_maps
from core.engine import simulate


def tester(
    policy: Policy,
    maps: Optional[List[DungeonMap]] = None,
    max_failure_traces: Optional[int] = 50,
    record_all_runs: bool = False
) -> TestResult:
    """
    Evaluates a Policy against dungeon maps (default 10 fixed maps x 5 runs = 50 runs).
    Returns an empirical TestResult object with ground-truth survival statistics.
    Records failure traces up to max_failure_traces (or all runs if record_all_runs=True).
    """
    test_maps = maps if maps is not None else load_fixed_maps()
    runs_per_map = 5 if maps is None else 1  # 50 runs for standard benchmark, fast for Phase 0

    total_runs = len(test_maps) * runs_per_map
    successes = 0
    lava_deaths = 0
    monster_deaths = 0
    total_treasure = 0
    total_steps = 0
    failure_traces = []

    for m in test_maps:
        for run_idx in range(runs_per_map):
            path, cause, treasure, steps = simulate(m, policy, run_seed=run_idx)

            total_treasure += treasure
            total_steps += steps

            if cause == "success":
                successes += 1
                if record_all_runs and (max_failure_traces is None or len(failure_traces) < max_failure_traces):
                    failure_traces.append({
                        "map_id": m.map_id,
                        "map_name": m.name,
                        "path": path,
                        "cause": "success",
                        "died_at": None,
                        "run_seed": run_idx,
                        "treasure": treasure,
                        "steps": steps
                    })
            else:
                died_at = path[-1] if path else m.start
                if cause == "lava":
                    lava_deaths += 1
                elif cause == "monster":
                    monster_deaths += 1

                # Record failure traces
                if max_failure_traces is None or len(failure_traces) < max_failure_traces:
                    failure_traces.append({
                        "map_id": m.map_id,
                        "map_name": m.name,
                        "path": path,
                        "cause": cause,
                        "died_at": died_at,
                        "run_seed": run_idx
                    })

    success_rate = round(successes / total_runs, 3) if total_runs > 0 else 0.0
    death_by_lava_pct = round((lava_deaths / total_runs) * 100.0, 1) if total_runs > 0 else 0.0
    death_by_monster_pct = round((monster_deaths / total_runs) * 100.0, 1) if total_runs > 0 else 0.0
    avg_treasure = round(total_treasure / total_runs, 2) if total_runs > 0 else 0.0
    avg_steps = int(round(total_steps / total_runs)) if total_runs > 0 else 0

    return TestResult(
        policy_version=policy.version,
        success_rate=success_rate,
        death_by_lava_pct=death_by_lava_pct,
        death_by_monster_pct=death_by_monster_pct,
        avg_treasure=avg_treasure,
        avg_steps=avg_steps,
        failure_traces=failure_traces
    )

