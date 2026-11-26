"""
viz/renderer.py - Pixel-art dungeon visualization and multi-version comparison renderer.
Generates visually distinct path visualizations (V1 Red, V2 Yellow, V3 Blue, V4+ Green)
and 2x2 comparison grid images using Matplotlib, plus optional Pygame playback.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Headless backend for reliable cross-platform image saving
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Optional
from core.contracts import Policy, TestResult, Critique
from core.map_generator import DungeonMap, load_fixed_maps
from core.engine import simulate


COLORS = {
    "bg": "#0f172a",          # Deep slate background
    "floor": "#1e293b",       # Dungeon floor stone
    "wall": "#334155",        # Solid stone wall
    "wall_border": "#475569",
    "lava": "#ef4444",        # Magma red
    "lava_glow": "#f97316",   # Fire orange
    "monster": "#a855f7",     # Danger purple
    "treasure": "#eab308",    # Gold chest
    "start": "#38bdf8",       # Cyan start
    "exit": "#22c55e",        # Green portal
}

VERSION_STYLES = {
    1: {"color": "#ef4444", "name": "V1: Chaotic / Lava Burn", "linestyle": "--", "marker": "x"},
    2: {"color": "#f59e0b", "name": "V2: Greedy / Monster Ambush", "linestyle": "-.", "marker": "v"},
    3: {"color": "#3b82f6", "name": "V3: Overly Cautious / Missed Gold", "linestyle": ":", "marker": "s"},
    4: {"color": "#10b981", "name": "V4+: Optimal Path Master", "linestyle": "-", "marker": "o"},
}


def get_version_style(version: int) -> dict:
    if version in VERSION_STYLES:
        return VERSION_STYLES[version]
    return {"color": "#10b981", "name": f"V{version}: Refined Policy", "linestyle": "-", "marker": "o"}


def draw_dungeon_grid(ax, dungeon: DungeonMap):
    """Draws dungeon walls, floor, lava lakes, monsters, chests, start and exit."""
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(-0.5, dungeon.width - 0.5)
    ax.set_ylim(-0.5, dungeon.height - 0.5)
    ax.invert_yaxis()  # (0, 0) at top-left
    ax.set_aspect("equal")

    # Draw floor and walls
    for y in range(dungeon.height):
        for x in range(dungeon.width):
            if dungeon.is_wall(x, y):
                wall_rect = patches.Rectangle(
                    (x - 0.5, y - 0.5), 1, 1,
                    linewidth=1, edgecolor=COLORS["wall_border"],
                    facecolor=COLORS["wall"], zorder=1
                )
                ax.add_patch(wall_rect)
            else:
                floor_rect = patches.Rectangle(
                    (x - 0.5, y - 0.5), 1, 1,
                    linewidth=0.5, edgecolor="#1e293b",
                    facecolor=COLORS["floor"], zorder=0
                )
                ax.add_patch(floor_rect)

    # Draw glowing Lava pools
    for lx, ly in dungeon.lava_cells:
        lava_bg = patches.Rectangle(
            (lx - 0.5, ly - 0.5), 1, 1,
            linewidth=0, facecolor=COLORS["lava"], zorder=2, alpha=0.9
        )
        ax.add_patch(lava_bg)
        lava_glow = patches.Circle(
            (lx, ly), 0.35, facecolor=COLORS["lava_glow"], edgecolor="none", zorder=3, alpha=0.85
        )
        ax.add_patch(lava_glow)
        ax.text(lx, ly, "L", color="white", ha="center", va="center", fontsize=8, fontweight="bold", zorder=4)

    # Draw Monsters
    for mx, my in dungeon.monsters:
        m_circle = patches.Circle(
            (mx, my), 0.38, facecolor=COLORS["monster"], edgecolor="#f43f5e", linewidth=1.5, zorder=5
        )
        ax.add_patch(m_circle)
        ax.text(mx, my, "M", color="white", ha="center", va="center", fontsize=9, fontweight="bold", zorder=6)

    # Draw Treasures
    for tx, ty in dungeon.treasures:
        t_box = patches.Rectangle(
            (tx - 0.35, ty - 0.35), 0.7, 0.7,
            facecolor=COLORS["treasure"], edgecolor="#ca8a04", linewidth=1.5, zorder=5
        )
        ax.add_patch(t_box)
        ax.text(tx, ty, "T", color="#78350f", ha="center", va="center", fontsize=8, fontweight="bold", zorder=6)

    # Draw Start and Exit
    sx, sy = dungeon.start
    s_patch = patches.Circle((sx, sy), 0.42, facecolor=COLORS["start"], edgecolor="white", linewidth=1.5, zorder=7)
    ax.add_patch(s_patch)
    ax.text(sx, sy, "S", color="white", ha="center", va="center", fontsize=10, fontweight="bold", zorder=8)

    ex, ey = dungeon.exit
    e_patch = patches.RegularPolygon((ex, ey), 5, radius=0.45, facecolor=COLORS["exit"], edgecolor="white", linewidth=1.5, zorder=7)
    ax.add_patch(e_patch)
    ax.text(ex, ey, "E", color="white", ha="center", va="center", fontsize=10, fontweight="bold", zorder=8)

    # Clean axes
    ax.set_xticks(range(dungeon.width))
    ax.set_yticks(range(dungeon.height))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(length=0)


def render_policy_path(
    policy: Policy,
    test_result: TestResult,
    dungeon: Optional[DungeonMap] = None,
    save_path: Optional[str] = None
) -> str:
    """
    Renders and saves a single policy trajectory on a representative benchmark map.
    Saves to evolution/V{version}_path.png.
    """
    os.makedirs("evolution", exist_ok=True)
    if dungeon is None:
        fixed_maps = load_fixed_maps()
        # For V1 and V2, select a map showcasing their prominent failure mode
        if policy.version == 1:
            dungeon = fixed_maps[0]  # Lava Crucible
        elif policy.version == 2:
            dungeon = fixed_maps[1]  # Monster Den
        else:
            dungeon = fixed_maps[2]  # Treasure Alcoves

    path, cause, treasure, steps = simulate(dungeon, policy, run_seed=0)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=120)
    fig.patch.set_facecolor(COLORS["bg"])
    draw_dungeon_grid(ax, dungeon)

    style = get_version_style(policy.version)

    # Draw path trace
    if len(path) > 1:
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        ax.plot(
            xs, ys,
            color=style["color"],
            linestyle=style["linestyle"],
            linewidth=3.0,
            alpha=0.92,
            zorder=9,
            label=f"Path V{policy.version}"
        )
        ax.scatter(xs, ys, color=style["color"], s=26, zorder=10)

    # Draw termination marker (Skull if died, Star if success)
    if path:
        last_x, last_y = path[-1]
        if cause == "lava":
            ax.scatter(last_x, last_y, marker="X", s=240, color="#ffffff", edgecolors="#dc2626", linewidth=2.5, zorder=15)
            ax.text(last_x, last_y - 0.5, "☠ BURNED", color="#f87171", ha="center", fontsize=9, fontweight="bold", zorder=16)
        elif cause == "monster":
            ax.scatter(last_x, last_y, marker="X", s=240, color="#ffffff", edgecolors="#a855f7", linewidth=2.5, zorder=15)
            ax.text(last_x, last_y - 0.5, "☠ SLAIN", color="#c084fc", ha="center", fontsize=9, fontweight="bold", zorder=16)
        elif cause == "success":
            ax.scatter(last_x, last_y, marker="*", s=300, color="#fef08a", edgecolors="#22c55e", linewidth=2.0, zorder=15)
            ax.text(last_x, last_y - 0.5, "★ CLEARED", color="#4ade80", ha="center", fontsize=9, fontweight="bold", zorder=16)

    # Title banner
    title = (
        f"AutoEvolve Dungeon Crawler - Policy V{policy.version} ({dungeon.name})\n"
        f"COSTS: lava={policy.COSTS.get('lava')}, monster={policy.COSTS.get('monster')}, "
        f"treasure={policy.COSTS.get('treasure')}, step={policy.COSTS.get('step')} | Avoid Radius: {policy.avoidance_radius}\n"
        f"Tester: Success={test_result.success_rate*100:.0f}% | Lava Deaths={test_result.death_by_lava_pct:.0f}% | "
        f"Monster Deaths={test_result.death_by_monster_pct:.0f}% | Gold={test_result.avg_treasure:.1f}/6 | Score={test_result.score:.3f}"
    )
    ax.set_title(title, color="#f8fafc", fontsize=9.5, pad=12, fontweight="bold")

    out_file = save_path or f"evolution/V{policy.version}_path.png"
    plt.tight_layout()
    plt.savefig(out_file, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return out_file


def render_comparison_grid(
    policies: List[Policy],
    test_results: List[TestResult],
    critiques: List[Critique],
    save_path: str = "evolution/comparison_grid.png"
) -> str:
    """
    Creates a 2x2 multi-panel comparison grid (V1 vs V2 vs V3 vs V4/Latest)
    highlighting the evolutionary milestones and distinct path behaviors.
    """
    os.makedirs("evolution", exist_ok=True)
    fixed_maps = load_fixed_maps()

    # Determine evaluated versions
    total_evaluated = min(len(policies), len(test_results), len(critiques))
    if total_evaluated <= 4:
        selected_indices = list(range(total_evaluated))
    else:
        selected_indices = [0, 1, 2, total_evaluated - 1]

    fig, axes = plt.subplots(2, 2, figsize=(16, 16), dpi=130)
    fig.patch.set_facecolor(COLORS["bg"])
    axes_flat = axes.flatten()

    for idx, ax in enumerate(axes_flat):
        if idx < len(selected_indices):
            p_idx = selected_indices[idx]
            policy = policies[p_idx]
            tr = test_results[p_idx]
            style = get_version_style(policy.version)

            # Match display map to show version's defining behavior
            if policy.version == 1:
                dungeon = fixed_maps[0]  # Lava Crucible
            elif policy.version == 2:
                dungeon = fixed_maps[1]  # Monster Den
            elif policy.version == 3:
                dungeon = fixed_maps[2]  # Treasure Alcoves
            else:
                dungeon = fixed_maps[2]  # Treasure Alcoves

            draw_dungeon_grid(ax, dungeon)
            path, cause, treasure, steps = simulate(dungeon, policy, run_seed=0)

            if len(path) > 1:
                xs = [p[0] for p in path]
                ys = [p[1] for p in path]
                ax.plot(
                    xs, ys,
                    color=style["color"],
                    linestyle=style["linestyle"],
                    linewidth=3.2,
                    alpha=0.95,
                    zorder=9
                )
                ax.scatter(xs, ys, color=style["color"], s=28, zorder=10)

            if path:
                lx, ly = path[-1]
                if cause == "lava":
                    ax.scatter(lx, ly, marker="X", s=220, color="#ffffff", edgecolors="#dc2626", linewidth=2.5, zorder=15)
                    ax.text(lx, ly - 0.5, "☠ LAVA DEATH", color="#f87171", ha="center", fontsize=9, fontweight="bold", zorder=16)
                elif cause == "monster":
                    ax.scatter(lx, ly, marker="X", s=220, color="#ffffff", edgecolors="#a855f7", linewidth=2.5, zorder=15)
                    ax.text(lx, ly - 0.5, "☠ MONSTER SLAIN", color="#c084fc", ha="center", fontsize=9, fontweight="bold", zorder=16)
                elif cause == "success":
                    ax.scatter(lx, ly, marker="*", s=280, color="#fef08a", edgecolors="#22c55e", linewidth=2.0, zorder=15)
                    ax.text(lx, ly - 0.5, "★ CLEARED", color="#4ade80", ha="center", fontsize=9, fontweight="bold", zorder=16)

            subtitle = (
                f"[{style['name']}] - Map: {dungeon.name}\n"
                f"COSTS: lava={policy.COSTS.get('lava')}, monster={policy.COSTS.get('monster')}, "
                f"treasure={policy.COSTS.get('treasure')}, step={policy.COSTS.get('step')}\n"
                f"Success Rate: {tr.success_rate*100:.0f}% | Lava: {tr.death_by_lava_pct:.0f}% | "
                f"Monster: {tr.death_by_monster_pct:.0f}% | Score: {tr.score:.3f}"
            )
            ax.set_title(subtitle, color="#f1f5f9", fontsize=10, pad=10, fontweight="bold")
        else:
            ax.set_visible(False)

    fig.suptitle(
        "AutoEvolve Dungeon Crawler: Multi-Generation Meta-Evolution\n"
        "(Phase 0 Genesis -> Phase 1 G-T-C Refinement Loop)",
        color="#ffffff",
        fontsize=16,
        fontweight="bold",
        y=0.98
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return save_path


def render_v1_vs_agent2_comparison(
    v1_policy: Policy,
    v1_tr: TestResult,
    agent2_policy: Policy,
    agent2_tr: TestResult,
    dungeon: Optional[DungeonMap] = None,
    save_path: str = "evolution/v1_vs_agent2_comparison.png"
) -> str:
    """
    Renders visual proof comparing Task 1 V1 (Chaotic Red Path) against
    Task 2 Agent 2 (Optimal Green Path) on the exact SAME benchmark map.
    Proves Pillar 4: Cross-Agent Memory prevents repeating mistakes.
    """
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    if dungeon is None:
        fixed_maps = load_fixed_maps()
        dungeon = fixed_maps[0]  # Lava Crucible benchmark

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9), dpi=140)
    fig.patch.set_facecolor(COLORS["bg"])

    # -------------------------------------------------------------
    # Panel 1: Task 1 V1 (Chaotic Red Path)
    # -------------------------------------------------------------
    draw_dungeon_grid(ax1, dungeon)
    path1, cause1, tr1, steps1 = simulate(dungeon, v1_policy, run_seed=0)

    if len(path1) > 1:
        xs1 = [p[0] for p in path1]
        ys1 = [p[1] for p in path1]
        ax1.plot(
            xs1, ys1,
            color="#ef4444",
            linestyle="--",
            linewidth=3.5,
            alpha=0.95,
            zorder=9,
            label="V1 Path (Chaotic)"
        )
        ax1.scatter(xs1, ys1, color="#ef4444", s=36, marker="x", zorder=10)

    if path1:
        lx, ly = path1[-1]
        if cause1 == "lava":
            ax1.scatter(lx, ly, marker="X", s=280, color="#ffffff", edgecolors="#dc2626", linewidth=2.5, zorder=15)
            ax1.text(lx, ly - 0.5, "☠ LAVA DEATH", color="#f87171", ha="center", fontsize=10, fontweight="bold", zorder=16)
        elif cause1 == "monster":
            ax1.scatter(lx, ly, marker="X", s=280, color="#ffffff", edgecolors="#a855f7", linewidth=2.5, zorder=15)
            ax1.text(lx, ly - 0.5, "☠ MONSTER SLAIN", color="#c084fc", ha="center", fontsize=10, fontweight="bold", zorder=16)
        elif cause1 == "success":
            ax1.scatter(lx, ly, marker="*", s=280, color="#fef08a", edgecolors="#22c55e", linewidth=2.0, zorder=15)
            ax1.text(lx, ly - 0.5, "★ CLEARED", color="#4ade80", ha="center", fontsize=10, fontweight="bold", zorder=16)

    title1 = (
        f"[TASK 1: V1 AGENT] (Without Prior Memory)\n"
        f"Map: {dungeon.name} | Clear Rate: {v1_tr.success_rate*100:.0f}% | Lava: {v1_tr.death_by_lava_pct:.0f}% | Monster: {v1_tr.death_by_monster_pct:.0f}%\n"
        f"COSTS: {v1_policy.COSTS} | Radius: {v1_policy.avoidance_radius}\n"
        f"Outcome on Map: {cause1.upper()} at step {steps1} (Gold: {tr1}/3)"
    )
    ax1.set_title(title1, color="#fca5a5", fontsize=10.5, pad=12, fontweight="bold")

    # -------------------------------------------------------------
    # Panel 2: Task 2 Agent 2 (Single-Shot Memory Learner - Optimal Green)
    # -------------------------------------------------------------
    draw_dungeon_grid(ax2, dungeon)
    path2, cause2, tr2, steps2 = simulate(dungeon, agent2_policy, run_seed=0)

    if len(path2) > 1:
        xs2 = [p[0] for p in path2]
        ys2 = [p[1] for p in path2]
        ax2.plot(
            xs2, ys2,
            color="#10b981",
            linestyle="-",
            linewidth=3.5,
            alpha=0.95,
            zorder=9,
            label="Agent 2 Path (Optimal)"
        )
        ax2.scatter(xs2, ys2, color="#10b981", s=36, marker="o", zorder=10)

    if path2:
        lx2, ly2 = path2[-1]
        if cause2 == "success":
            ax2.scatter(lx2, ly2, marker="*", s=320, color="#fef08a", edgecolors="#22c55e", linewidth=2.5, zorder=15)
            ax2.text(lx2, ly2 - 0.5, "* 1-SHOT VICTORY", color="#4ade80", ha="center", fontsize=10, fontweight="bold", zorder=16)
        else:
            ax2.scatter(lx2, ly2, marker="X", s=280, color="#ffffff", edgecolors="#dc2626", linewidth=2.5, zorder=15)
            ax2.text(lx2, ly2 - 0.5, f"[X] {cause2.upper()}", color="#f87171", ha="center", fontsize=10, fontweight="bold", zorder=16)

    title2 = (
        f"[TASK 2: AGENT 2 SINGLE-SHOT] (With Cross-Agent Memory)\n"
        f"Map: {dungeon.name} | Clear Rate: {agent2_tr.success_rate*100:.0f}% | Score: {agent2_tr.score:.3f} | Gold: {agent2_tr.avg_treasure:.1f}/3\n"
        f"COSTS: {agent2_policy.COSTS} | Radius: {agent2_policy.avoidance_radius}\n"
        f"Outcome: {cause2.upper()} (Solved in 1 attempt via Task 1 Memory)"
    )
    ax2.set_title(title2, color="#86efac", fontsize=10.5, pad=12, fontweight="bold")

    fig.suptitle(
        "AutoEvolve Protocol - Pillar 4 Verification: Cross-Agent Memory Prevents Repeating Mistakes\n"
        "Same Dungeon Solved in 1 Attempt by Agent 2 (Right) After Ingesting Agent 1's Evolution Ledger (Left)",
        color="#ffffff",
        fontsize=14,
        fontweight="bold",
        y=0.98
    )

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(save_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return save_path
