"""
core/critique.py - Evaluates test results and generates actionable instructions.
Uses Featherless LLM (meta-llama/Meta-Llama-3.1-70B-Instruct) with deterministic fallback.
"""

from core.contracts import Policy, TestResult, Critique
from core.featherless_client import call_featherless, extract_json

CRITIQUE_SYSTEM_DEFAULT = """
You are AutoEvolve Critique. Return ONLY valid JSON:
{"score": float, "failure_modes": ["string"], "root_cause": "string", "instruction_for_next_generator": "string"}
Score formula: score = success_rate * 0.6 + (avg_treasure / 6.0) * 0.3 + (1.0 / max(avg_steps, 1)) * 0.1
Your instruction_for_next_generator MUST start with 'For V{next}: You must...' and prescribe exact COSTS values referencing empirical failure percentages.
Example: 'For V3: You must increase COSTS["lava"] from 1 to 100. V2 died 68% in lava at (5,8) because lava penalty was 1 so A* cut through lava.'
""".strip()


def call_critique(policy: Policy, test_result: TestResult, critique_system: str) -> Critique:
    """
    Critiques policy performance based on empirical test results.
    Produces root cause diagnosis and precise numerical instructions for the Generator.
    """
    next_ver = policy.version + 1
    sample_failures = test_result.failure_traces[:3]

    user_prompt = f"""
Policy V{policy.version} COSTS={policy.COSTS}, avoidance_radius={policy.avoidance_radius}
Tester Results (50 runs):
- success_rate: {test_result.success_rate}
- death_by_lava_pct: {test_result.death_by_lava_pct}%
- death_by_monster_pct: {test_result.death_by_monster_pct}%
- avg_treasure: {test_result.avg_treasure}/6
- avg_steps: {test_result.avg_steps}
- computed_score: {test_result.score}
Sample failure traces: {sample_failures}

Next policy is V{next_ver}.
Diagnose root cause and write instruction_for_next_generator starting with 'For V{next_ver}: You must...'.
Return ONLY JSON with keys: score, failure_modes, root_cause, instruction_for_next_generator.
"""

    try:
        raw = call_featherless(critique_system, user_prompt, temp=0.1)
        data = extract_json(raw)
        return Critique(
            score=float(data.get("score", test_result.score)),
            failure_modes=list(data.get("failure_modes", ["Observed failures"])),
            root_cause=str(data.get("root_cause", "Unbalanced cost parameters")),
            instruction_for_next_generator=str(data.get("instruction_for_next_generator", ""))
        )
    except Exception:
        # Robust deterministic fallback logic preserving the exact protocol
        score = test_result.score
        if test_result.death_by_lava_pct >= 25.0:
            lava_now = policy.COSTS.get("lava", 1)
            died_coords = sample_failures[0].get("died_at", (4, 3)) if sample_failures else (4, 3)
            instr = (
                f"For V{next_ver}: You must increase COSTS['lava'] from {lava_now} to 100. "
                f"V{policy.version} died {test_result.death_by_lava_pct:.0f}% in lava near {died_coords} "
                f"because lava penalty was {lava_now} so A* cut through lava."
            )
            failure_modes = ["Lethal lava burns", "Direct path shortcutting into hazards"]
            root_cause = f"COSTS['lava'] is {lava_now}, making lava cells appear cheaper than corridors."

        elif test_result.death_by_monster_pct >= 20.0:
            monster_now = policy.COSTS.get("monster", 1)
            instr = (
                f"For V{next_ver}: You must increase COSTS['monster'] to 50 and avoidance_radius to 2. "
                f"V{policy.version} died {test_result.death_by_monster_pct:.0f}% to monsters because "
                f"it goes greedy to treasure ignoring monsters."
            )
            failure_modes = ["Monster ambushes", "Greedy pathing into threat zones"]
            root_cause = "Agent greedily cut close to monsters with low avoidance radius and low monster penalty."

        elif test_result.avg_treasure < 2.5 and test_result.success_rate >= 0.6:
            instr = (
                f"For V{next_ver}: You are too safe, treasure only {test_result.avg_treasure:.2f}. "
                f"Decrease COSTS['treasure'] to -15 while keeping lava 100."
            )
            failure_modes = ["Suboptimal treasure acquisition", "Overly timid exploration"]
            root_cause = "Treasure reward incentive is too weak to motivate safe alcove detours."

        else:
            instr = (
                f"For V{next_ver}: Optimize efficiency, reduce step cost, keep lava 100, monster 50, and treasure -15."
            )
            failure_modes = ["Minor efficiency loss"]
            root_cause = "Agent policy is near-optimal; fine-tuning completed."

        return Critique(
            score=score,
            failure_modes=failure_modes,
            root_cause=root_cause,
            instruction_for_next_generator=instr
        )
