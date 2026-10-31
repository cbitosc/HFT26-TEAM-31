"""
core/genesis.py - Phase 0 Genesis: Meta-Evolution before the main loop.
Evolves starting seeds on quick maps and meta-evolves system prompts via Featherless.
"""

import os
import json
import random
from typing import Tuple, Callable
from core.contracts import Policy, TestResult
from core.map_generator import load_easy_maps
from core.featherless_client import call_featherless, extract_json

DEFAULT_GENERATOR_SYSTEM = """
You are AutoEvolve Generator. Output ONLY valid JSON:
{"COSTS": {"lava": int, "monster": int, "treasure": int, "step": int}, "avoidance_radius": int, "changelog": "string"}
You MUST obey instruction_for_next_generator from Critique. Your changelog must explicitly cite the exact numeric COSTS modifications you made and why.
""".strip()

DEFAULT_CRITIQUE_SYSTEM = """
You are AutoEvolve Critique. Return ONLY valid JSON:
{"score": float, "failure_modes": ["string"], "root_cause": "string", "instruction_for_next_generator": "string"}
Score formula: score = success_rate * 0.6 + (avg_treasure / 6.0) * 0.3 + (1.0 / max(avg_steps, 1)) * 0.1
Your instruction_for_next_generator MUST start with 'For V{next}: You must...' and prescribe exact COSTS values referencing empirical failure percentages.
""".strip()


def phase0_genesis(tester_func: Callable[[Policy, list], TestResult]) -> Tuple[Policy, str, str]:
    """
    Executes Phase 0 Genesis:
    1. Evaluates 5 random V0 seed policies against 3 easy maps.
    2. Selects the most promising seed as Policy V1.
    3. Uses Featherless API to meta-evolve stricter Generator & Critique system prompts.
    4. Falls back gracefully to reinforced defaults if API is offline.
    """
    print("\n" + "=" * 65)
    print(" [PHASE 0] GENESIS: META-EVOLVING SEEDS & SYSTEM PROMPTS")
    print("=" * 65)

    os.makedirs("evolution", exist_ok=True)
    easy_maps = load_easy_maps()

    # Part A: Seed Evolution
    print("\n[Genesis Part A] Evaluating 5 candidate seed policies on fast maps...")
    candidates = []
    # Candidate seeds include low-cost baseline (V1 {1, 1, -1, 1}) and exploratory variants
    seed_archetypes = [
        {"lava": 1, "monster": 1, "treasure": -1, "step": 1},
        {"lava": 2, "monster": 2, "treasure": -2, "step": 1},
        {"lava": 1, "monster": 3, "treasure": -3, "step": 1},
        {"lava": 2, "monster": 1, "treasure": -1, "step": 1},
        {"lava": 3, "monster": 2, "treasure": -4, "step": 1},
    ]

    for i in range(5):
        costs = seed_archetypes[i]
        p = Policy(
            version=0,
            COSTS=costs,
            avoidance_radius=1,
            changelog=f"Random Genesis Seed #{i}"
        )
        tr = tester_func(p, easy_maps)
        candidates.append((p, tr))
        print(f"  > Seed #{i}: COSTS={costs} -> Score: {tr.score:.3f} | Success: {tr.success_rate * 100:.0f}% | Lava Deaths: {tr.death_by_lava_pct:.0f}%")

    # Select the baseline seed (or highest scoring exploratory seed) as V1
    best_policy, best_result = max(candidates, key=lambda x: (x[1].score, -x[0].COSTS["lava"]))
    best_policy.version = 1
    best_policy.changelog = f"Genesis Seed (Success: {best_result.success_rate * 100:.0f}%, Fitness: {best_result.score:.3f})"

    print(f"\n[Genesis Selected] Promoted to V1: COSTS={best_policy.COSTS} | Baseline Lava Death={best_result.death_by_lava_pct:.0f}%")

    # Part B: Prompt Meta-Evolution via Featherless
    print("\n[Genesis Part B] Meta-evolving Generator & Critique prompts via Featherless LLM...")
    META_SYSTEM = (
        "You are Meta-AutoEvolve. You specialize in evolving AI agent prompts. "
        "Your task is to refine and strengthen system prompts for both the Generator and Critique agents, "
        "making them uncompromisingly strict, quantitative, and actionable."
    )

    META_USER = f"""
Current Generator System: 'You generate Policy JSON with COSTS...'
Current Critique System: 'You are evaluator returning JSON...'
Problem Observed: Generator frequently ignores lava deaths, and Critique instructions are often too vague.
Best seed from Phase 0: {best_policy.COSTS} with {best_result.success_rate * 100}% success, lava deaths {best_result.death_by_lava_pct}%.
Task: Rewrite both system prompts to be strict and actionable.
- Generator prompt must enforce obeying instruction_for_next_generator and mutating numeric COSTS.
- Critique prompt must enforce diagnosing root causes and giving exact COSTS numbers in 'For V{{next}}: You must...'.
Return ONLY JSON with schema:
{{"generator_system": "...", "critique_system": "..."}}
"""

    generator_system = DEFAULT_GENERATOR_SYSTEM
    critique_system = DEFAULT_CRITIQUE_SYSTEM

    try:
        raw_response = call_featherless(META_SYSTEM, META_USER, temp=0.3)
        evolved_prompts = extract_json(raw_response)
        generator_system = evolved_prompts.get("generator_system", generator_system)
        critique_system = evolved_prompts.get("critique_system", critique_system)

        with open("evolution/evolved_prompts.json", "w", encoding="utf-8") as f:
            json.dump({
                "phase": 0,
                "meta_model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                "generator_system": generator_system,
                "critique_system": critique_system
            }, f, indent=2)

        print("  [Featherless OK] System prompts evolved and saved to evolution/evolved_prompts.json")
    except Exception as e:
        print(f"  [Prompt Fallback] Featherless API ({e}) - Utilizing calibrated strict default prompts.")
        with open("evolution/evolved_prompts.json", "w", encoding="utf-8") as f:
            json.dump({
                "phase": 0,
                "meta_model": "fallback_default",
                "generator_system": generator_system,
                "critique_system": critique_system
            }, f, indent=2)

    print("=" * 65 + "\n")
    return best_policy, generator_system, critique_system
