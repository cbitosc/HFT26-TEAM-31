"""
main.py - AutoEvolve Dungeon Crawler with Meta-Evolution.
Orchestrates Phase 0 Genesis and Phase 1 Generator-Tester-Critique (G-T-C) loop.
Optionally launches real-time Pygame simulation via --simulate or --gui.
"""

import os
import sys
import json
from dotenv import load_dotenv

from core.contracts import Policy
from core.genesis import phase0_genesis
from core.tester import tester
from core.critique import call_critique
from core.generator import call_generator
from viz.renderer import render_policy_path, render_comparison_grid

# Load environment configuration (.env)
load_dotenv()


def main():
    print("=" * 70)
    print("       AUTOEVOLVE DUNGEON CRAWLER: META-EVOLUTION PROTOCOL")
    print("      (Featherless API + Ground-Truth Simulation Harness)")
    print("=" * 70)

    os.makedirs("evolution", exist_ok=True)

    # -------------------------------------------------------------
    # PHASE 0: GENESIS (AutoEvolve Before the Main Loop)
    # -------------------------------------------------------------
    # Evolves initial seed candidates and meta-evolves system prompts
    best_V1, gen_system, crit_system = phase0_genesis(tester)

    policies = [best_V1]
    test_results = []
    critiques = []

    print("\n" + "=" * 70)
    print(" [PHASE 1] MAIN G-T-C EVOLUTION LOOP (Generator -> Tester -> Critique)")
    print(" Target: Open-ended evolution until Fitness Score > 0.900 (Max 15 iterations)")
    print("=" * 70 + "\n")

    MAX_ITERATIONS = 15
    iteration = 0

    while iteration < MAX_ITERATIONS:
        current_policy = policies[-1]
        v_num = current_policy.version
        print(f"\n--- [CYCLE V{v_num}] ---")
        print(f"Policy V{v_num} Parameters: COSTS={current_policy.COSTS} | Radius={current_policy.avoidance_radius}")
        print(f"Policy Changelog: {current_policy.changelog}")

        # 1. TESTER: Deterministic ground-truth evaluation across 50 runs
        tr = tester(current_policy)
        test_results.append(tr)
        print(f"  [Tester Output] Success: {tr.success_rate*100:.1f}% | Lava Deaths: {tr.death_by_lava_pct:.1f}% | Monster Deaths: {tr.death_by_monster_pct:.1f}% | Avg Gold: {tr.avg_treasure:.2f}/6 | Steps: {tr.avg_steps}")

        # 2. CRITIQUE: Root cause analysis and actionable directive synthesis
        cr = call_critique(current_policy, tr, crit_system)
        critiques.append(cr)
        print(f"  [Critique Score] {cr.score:.3f} / 1.000")
        print(f"  [Critique Root Cause] {cr.root_cause}")
        print(f"  [Critique Directive] {cr.instruction_for_next_generator}")

        # 3. PERSIST ARTIFACTS: Save JSON contracts and visualization PNGs
        with open(f"evolution/V{v_num}_policy.json", "w", encoding="utf-8") as f:
            json.dump(current_policy.to_dict(), f, indent=2)

        with open(f"evolution/V{v_num}_test.json", "w", encoding="utf-8") as f:
            json.dump(tr.to_dict(), f, indent=2)

        with open(f"evolution/V{v_num}_critique.json", "w", encoding="utf-8") as f:
            json.dump(cr.to_dict(), f, indent=2)

        img_path = render_policy_path(current_policy, tr)
        print(f"  [Visualization] Saved path render to {img_path}")

        # 4. TERMINATION CHECK
        if cr.score > 0.900:
            print(f"\n>>> EVOLUTION GOAL ACHIEVED: Score {cr.score:.3f} > 0.900 at Version V{v_num}! <<<")
            break

        # 5. GENERATOR: Synthesize mutated Policy V_{N+1} obeying Critique instructions
        if iteration + 1 < MAX_ITERATIONS:
            next_policy = call_generator(current_policy, tr, cr, gen_system)
            policies.append(next_policy)

        iteration += 1

    # -------------------------------------------------------------
    # FINALIZATION: Multi-Generation Comparison Grid
    # -------------------------------------------------------------
    evaluated_policies = policies[:len(test_results)]
    grid_img = render_comparison_grid(evaluated_policies, test_results, critiques)
    print("\n" + "=" * 70)
    print(f" [COMPLETE] Evolution finished across {len(test_results)} generations.")
    print(f" Comparison grid generated at: {grid_img}")
    print("=" * 70)

    # Print evolution trajectory summary table
    print("\nEVOLUTION MILESTONE SUMMARY:")
    print(f"{'Version':<10} | {'Score':<8} | {'Success':<10} | {'Lava %':<10} | {'Monster %':<12} | {'Gold':<8} | {'Changelog'}")
    print("-" * 110)
    for p, tr, cr in zip(evaluated_policies, test_results, critiques):
        print(f"V{p.version:<9} | {cr.score:<8.3f} | {tr.success_rate*100:<9.1f}% | {tr.death_by_lava_pct:<9.1f}% | {tr.death_by_monster_pct:<11.1f}% | {tr.avg_treasure:<7.2f} | {p.changelog[:40]}")
    print("-" * 110)

    # Optional Live GUI simulation trigger
    if "--simulate" in sys.argv or "--gui" in sys.argv:
        print("\n[Launching Live Pygame Simulation Window...]")
        from viz.gui_simulation import launch_simulation
        launch_simulation(evaluated_policies, test_results, critiques)


if __name__ == "__main__":
    main()
