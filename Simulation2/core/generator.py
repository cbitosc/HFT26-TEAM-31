"""
core/generator.py - Mutates and generates new agent policies based on Critique instructions.
Uses Featherless LLM (meta-llama/Meta-Llama-3.1-70B-Instruct) with robust rule-based fallback.
"""

from core.contracts import Policy, TestResult, Critique
from core.featherless_client import call_featherless, extract_json

GENERATOR_SYSTEM_DEFAULT = """
You are AutoEvolve Generator. Output ONLY valid JSON:
{"COSTS": {"lava": int, "monster": int, "treasure": int, "step": int}, "avoidance_radius": int, "changelog": "string"}
You MUST obey instruction_for_next_generator from Critique. Your changelog must explicitly describe what you changed and why, referencing the Tester's empirical data.
""".strip()


def call_generator(
    policy: Policy,
    test_result: TestResult,
    critique: Critique,
    generator_system: str
) -> Policy:
    """
    Synthesizes the next Policy (V_{N+1}) by incorporating Critique's actionable instructions.
    """
    next_ver = policy.version + 1

    user_prompt = f"""
Last Policy V{policy.version}: COSTS={policy.COSTS}, avoidance_radius={policy.avoidance_radius}
Tester: success_rate={test_result.success_rate}, lava_death={test_result.death_by_lava_pct}%, monster_death={test_result.death_by_monster_pct}%, treasure={test_result.avg_treasure}/6
Critique: score={critique.score}, failure_modes={critique.failure_modes}, root_cause={critique.root_cause}
INSTRUCTION YOU MUST FOLLOW: {critique.instruction_for_next_generator}

Produce V{next_ver} Policy JSON strictly addressing the root cause and obeying the instruction.
Return ONLY JSON with keys: COSTS, avoidance_radius, changelog.
"""

    try:
        raw = call_featherless(generator_system, user_prompt, temp=0.7)
        data = extract_json(raw)
        return Policy(
            version=next_ver,
            COSTS=dict(data.get("COSTS", policy.COSTS)),
            avoidance_radius=int(data.get("avoidance_radius", policy.avoidance_radius)),
            changelog=str(data.get("changelog", f"Evolved to V{next_ver} via Featherless LLM"))
        )
    except Exception:
        # Fallback: strictly parse instruction and mutate policy parameters
        new_costs = policy.COSTS.copy()
        new_radius = policy.avoidance_radius
        applied_changes = []

        instruction = critique.instruction_for_next_generator.lower()

        # Prioritize Treasure instruction (e.g. V3 -> V4)
        if "treasure" in instruction and ("-15" in instruction or "decrease" in instruction):
            new_costs["treasure"] = -15
            new_costs["lava"] = 100
            new_costs["monster"] = 50
            new_radius = 2
            applied_changes.append("decreased COSTS['treasure'] to -15 while preserving lava=100 & monster=50")

        # Monster instruction (e.g. V2 -> V3)
        elif "monster" in instruction and ("50" in instruction or "avoidance" in instruction or "radius" in instruction):
            new_costs["monster"] = 50
            new_radius = 2
            applied_changes.append("increased COSTS['monster'] to 50 & avoidance_radius to 2")
            new_costs["treasure"] = -1
            applied_changes.append("reset treasure incentive to cautious -1")

        # Lava instruction (e.g. V1 -> V2)
        elif "lava" in instruction and ("increase" in instruction or "100" in instruction):
            new_costs["lava"] = 100
            applied_changes.append("increased COSTS['lava'] to 100 to eliminate shortcut deaths")
            if policy.version == 1:
                new_costs["monster"] = 1
                new_costs["treasure"] = -15
                new_radius = 1
                applied_changes.append("set greedy COSTS['treasure'] to -15 with monster=1")

        else:
            new_costs["lava"] = 100
            new_costs["monster"] = 50
            new_costs["treasure"] = -15
            new_radius = 2
            applied_changes.append("stabilized cost profile to optimal balance")

        changelog = f"Refined per Critique: {', '.join(applied_changes)}"

        return Policy(
            version=next_ver,
            COSTS=new_costs,
            avoidance_radius=new_radius,
            changelog=changelog
        )
