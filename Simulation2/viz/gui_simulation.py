"""
viz/gui_simulation.py - Interactive real-time Pygame simulation of AutoEvolve Dungeon Crawler.
Features smooth sub-tile movement interpolation, animated lava glow, particle effects,
interactive version switching (V1-V4), live telemetry, and cinematic Auto-Evolve mode.
"""

import sys
import time
import math
import random
import pygame
from typing import List, Tuple, Dict, Any, Optional

from core.contracts import Policy, TestResult, Critique
from core.map_generator import DungeonMap, load_fixed_maps
from core.engine import simulate, plan_journey


# Palette definitions
BG_COLOR = (15, 23, 42)          # Deep slate
PANEL_BG = (30, 41, 59)          # Card slate
PANEL_BORDER = (51, 65, 85)      # Slate border
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
GOLD_COLOR = (234, 179, 8)
LAVA_RED = (239, 68, 68)
LAVA_GLOW = (249, 115, 22)
MONSTER_PURPLE = (168, 85, 247)
EXIT_GREEN = (34, 197, 94)
START_CYAN = (56, 189, 248)

VERSION_META = {
    1: {"name": "V1: Chaotic Seed", "color": (239, 68, 68), "subtitle": "Low Lava Penalty (cuts into lethal lava)"},
    2: {"name": "V2: Greedy Looter", "color": (245, 158, 11), "subtitle": "Lava Fixed, Greedy for Gold (slain by monster)"},
    3: {"name": "V3: Overly Cautious", "color": (59, 130, 246), "subtitle": "High Avoidance, Low Gold (skips safe alcoves)"},
    4: {"name": "V4: Optimal Master", "color": (16, 185, 129), "subtitle": "Balanced Avoidance & Optimal Treasure Sweep"},
}


class Particle:
    """Visual particle effect for deaths and treasure collections."""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], vx: float, vy: float, life: int):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface: pygame.Surface):
        if self.life > 0:
            alpha_ratio = self.life / self.max_life
            radius = max(1, int(4 * alpha_ratio))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class DungeonSimulationApp:
    def __init__(self, policies: List[Policy], test_results: List[TestResult], critiques: List[Critique]):
        pygame.init()
        pygame.display.set_caption("AutoEvolve Dungeon Crawler - Live Simulation")

        self.width = 1120
        self.height = 680
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_header = pygame.font.SysFont("segoeui", 17, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 14)
        self.font_mono = pygame.font.SysFont("consolas", 13)
        self.font_small = pygame.font.SysFont("segoeui", 12)

        # Simulation data
        self.policies = {p.version: p for p in policies}
        self.test_results = {tr.policy_version: tr for tr in test_results}
        self.critiques = {i + 1: cr for i, cr in enumerate(critiques)}
        self.all_maps = load_fixed_maps()

        # State
        self.current_version = 1
        self.current_map_idx = 0
        self.paused = False
        self.auto_evolve_mode = False
        self.speed_multiplier = 1.0
        self.particles: List[Particle] = []

        # Motion & path execution state
        self.cell_size = 42
        self.grid_offset_x = 24
        self.grid_offset_y = 70
        self.step_idx = 0
        self.step_progress = 0.0  # 0.0 to 1.0 interpolation between current and next cell
        self.path: List[Tuple[int, int]] = []
        self.cause = "in_progress"
        self.collected_gold: Set[Tuple[int, int]] = set()
        self.trail_positions: List[Tuple[int, int]] = []
        self.auto_pause_timer = 0

        self.load_simulation_run()

    @property
    def current_map(self) -> DungeonMap:
        return self.all_maps[self.current_map_idx]

    @property
    def current_policy(self) -> Policy:
        return self.policies.get(self.current_version, self.policies[1])

    def load_simulation_run(self):
        """Prepares path and state for the active version and map."""
        dungeon = self.current_map
        policy = self.current_policy
        self.path, self.cause, self.total_treasure, self.total_steps = simulate(dungeon, policy, run_seed=0)
        self.step_idx = 0
        self.step_progress = 0.0
        self.collected_gold = set()
        self.trail_positions = [self.path[0]] if self.path else []
        self.particles.clear()
        self.auto_pause_timer = 0

    def trigger_death_particles(self, px: float, py: float, p_type: str):
        color = LAVA_GLOW if p_type == "lava" else (217, 70, 239)
        for _ in range(40):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 4.5)
            self.particles.append(Particle(
                px, py, color,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(25, 45)
            ))

    def trigger_gold_particles(self, px: float, py: float):
        for _ in range(25):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 3.0)
            self.particles.append(Particle(
                px, py, GOLD_COLOR,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(20, 35)
            ))

    def update(self):
        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        if self.paused:
            return

        if not self.path:
            return

        # Advance crawler motion
        if self.step_idx < len(self.path) - 1:
            step_speed = 0.06 * self.speed_multiplier
            self.step_progress += step_speed

            if self.step_progress >= 1.0:
                self.step_progress = 0.0
                self.step_idx += 1
                curr_pos = self.path[self.step_idx]
                self.trail_positions.append(curr_pos)

                # Check treasure collection
                if curr_pos in self.current_map.treasures and curr_pos not in self.collected_gold:
                    self.collected_gold.add(curr_pos)
                    cx = self.grid_offset_x + curr_pos[0] * self.cell_size + self.cell_size // 2
                    cy = self.grid_offset_y + curr_pos[1] * self.cell_size + self.cell_size // 2
                    self.trigger_gold_particles(cx, cy)

                # If reached terminal point of path
                if self.step_idx == len(self.path) - 1:
                    cx = self.grid_offset_x + curr_pos[0] * self.cell_size + self.cell_size // 2
                    cy = self.grid_offset_y + curr_pos[1] * self.cell_size + self.cell_size // 2
                    if self.cause in ["lava", "monster"]:
                        self.trigger_death_particles(cx, cy, self.cause)
                    elif self.cause == "success":
                        self.trigger_gold_particles(cx, cy)
        else:
            # Reached end of trajectory
            if self.auto_evolve_mode:
                self.auto_pause_timer += 1
                # Wait ~2 seconds, then evolve to next version
                if self.auto_pause_timer > 90:
                    self.auto_pause_timer = 0
                    if self.current_version < 4:
                        self.current_version += 1
                        self.load_simulation_run()
                    else:
                        self.current_version = 1
                        self.load_simulation_run()

    def draw_dungeon(self, surface: pygame.Surface):
        dungeon = self.current_map
        pulse = (math.sin(time.time() * 4.0) + 1.0) / 2.0  # 0.0 to 1.0

        for y in range(dungeon.height):
            for x in range(dungeon.width):
                rect = pygame.Rect(
                    self.grid_offset_x + x * self.cell_size,
                    self.grid_offset_y + y * self.cell_size,
                    self.cell_size, self.cell_size
                )

                if dungeon.is_wall(x, y):
                    pygame.draw.rect(surface, (51, 65, 85), rect)
                    pygame.draw.rect(surface, (71, 85, 105), rect, 1)
                else:
                    pygame.draw.rect(surface, (30, 41, 59), rect)
                    pygame.draw.rect(surface, (40, 53, 72), rect, 1)

                # Lava tile with animated bubbling glow
                if (x, y) in dungeon.lava_cells:
                    glow_intensity = int(180 + 75 * pulse)
                    lava_c = (glow_intensity, 40, 40)
                    pygame.draw.rect(surface, lava_c, rect)
                    center = rect.center
                    pygame.draw.circle(surface, (255, 130 + int(60 * pulse), 30), center, int(self.cell_size * 0.35))
                    lbl = self.font_mono.render("LAVA", True, (255, 255, 255))
                    surface.blit(lbl, lbl.get_rect(center=center))

                # Monster tile with animated warning pulse
                if (x, y) in dungeon.monsters:
                    m_center = rect.center
                    aura_r = int(self.cell_size * 0.42 + 2 * pulse)
                    pygame.draw.circle(surface, (168, 85, 247), m_center, aura_r)
                    pygame.draw.circle(surface, (244, 63, 94), m_center, int(aura_r * 0.75))
                    lbl = self.font_header.render("M", True, (255, 255, 255))
                    surface.blit(lbl, lbl.get_rect(center=m_center))

                # Treasure tile
                if (x, y) in dungeon.treasures:
                    is_collected = (x, y) in self.collected_gold
                    t_rect = rect.inflate(-12, -12)
                    if is_collected:
                        pygame.draw.rect(surface, (113, 63, 18), t_rect)
                        lbl = self.font_small.render("EMPTY", True, (161, 98, 7))
                    else:
                        pygame.draw.rect(surface, GOLD_COLOR, t_rect)
                        pygame.draw.rect(surface, (254, 240, 138), t_rect, 2)
                        lbl = self.font_mono.render("$", True, (113, 63, 18))
                    surface.blit(lbl, lbl.get_rect(center=rect.center))

                # Start
                if (x, y) == dungeon.start:
                    pygame.draw.circle(surface, START_CYAN, rect.center, int(self.cell_size * 0.4))
                    lbl = self.font_mono.render("S", True, (255, 255, 255))
                    surface.blit(lbl, lbl.get_rect(center=rect.center))

                # Exit
                if (x, y) == dungeon.exit:
                    pygame.draw.circle(surface, EXIT_GREEN, rect.center, int(self.cell_size * 0.42))
                    lbl = self.font_mono.render("EXIT", True, (255, 255, 255))
                    surface.blit(lbl, lbl.get_rect(center=rect.center))

        # Draw path trail
        v_meta = VERSION_META.get(self.current_version, VERSION_META[1])
        trail_color = v_meta["color"]
        if len(self.trail_positions) > 1:
            points = []
            for tx, ty in self.trail_positions:
                px = self.grid_offset_x + tx * self.cell_size + self.cell_size // 2
                py = self.grid_offset_y + ty * self.cell_size + self.cell_size // 2
                points.append((px, py))
            pygame.draw.lines(surface, trail_color, False, points, 3)
            for pt in points:
                pygame.draw.circle(surface, trail_color, pt, 4)

        # Draw crawler player with smooth interpolation
        if self.path:
            curr_pos = self.path[self.step_idx]
            if self.step_idx < len(self.path) - 1:
                next_pos = self.path[self.step_idx + 1]
                lerp_x = curr_pos[0] + (next_pos[0] - curr_pos[0]) * self.step_progress
                lerp_y = curr_pos[1] + (next_pos[1] - curr_pos[1]) * self.step_progress
            else:
                lerp_x, lerp_y = float(curr_pos[0]), float(curr_pos[1])

            agent_cx = int(self.grid_offset_x + lerp_x * self.cell_size + self.cell_size / 2)
            agent_cy = int(self.grid_offset_y + lerp_y * self.cell_size + self.cell_size / 2)

            # Draw glowing knight / agent sphere
            pygame.draw.circle(surface, (255, 255, 255), (agent_cx, agent_cy), int(self.cell_size * 0.38))
            pygame.draw.circle(surface, trail_color, (agent_cx, agent_cy), int(self.cell_size * 0.32))
            tag = f"V{self.current_version}"
            lbl = self.font_small.render(tag, True, (255, 255, 255))
            surface.blit(lbl, lbl.get_rect(center=(agent_cx, agent_cy)))

            # If simulation ended at terminal cell, draw skull or clear banner
            if self.step_idx == len(self.path) - 1:
                if self.cause == "lava":
                    skull = self.font_header.render("☠ LAVA BURN", True, (248, 113, 113))
                    surface.blit(skull, skull.get_rect(center=(agent_cx, agent_cy - 28)))
                elif self.cause == "monster":
                    skull = self.font_header.render("☠ MONSTER SLAIN", True, (216, 180, 254))
                    surface.blit(skull, skull.get_rect(center=(agent_cx, agent_cy - 28)))
                elif self.cause == "success":
                    star = self.font_header.render("★ CLEARED!", True, (74, 222, 128))
                    surface.blit(star, star.get_rect(center=(agent_cx, agent_cy - 28)))

        # Draw particles
        for p in self.particles:
            p.draw(surface)

    def draw_hud(self, surface: pygame.Surface):
        # Header bar
        header_rect = pygame.Rect(self.grid_offset_x, 15, 600, 45)
        map_title = f"Map {self.current_map_idx}: {self.current_map.name}"
        title_surf = self.font_title.render(map_title, True, TEXT_WHITE)
        surface.blit(title_surf, header_rect.topleft)

        mode_str = "[AUTO-EVOLVE ON]" if self.auto_evolve_mode else "[MANUAL CONTROLS]"
        mode_color = (74, 222, 128) if self.auto_evolve_mode else (148, 163, 184)
        mode_lbl = self.font_mono.render(mode_str, True, mode_color)
        surface.blit(mode_lbl, (header_rect.left + 350, header_rect.top + 6))

        # Right side panel (Telemetry & Evolution Inspector)
        panel_x = 640
        panel_y = 15
        panel_w = 455
        panel_h = 650

        # Background card
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(surface, PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, panel_rect, 2, border_radius=8)

        v_meta = VERSION_META.get(self.current_version, VERSION_META[1])
        policy = self.current_policy
        tr = self.test_results.get(self.current_version)
        critique = self.critiques.get(self.current_version)

        # 1. Version Badge
        badge_rect = pygame.Rect(panel_x + 16, panel_y + 16, panel_w - 32, 42)
        pygame.draw.rect(surface, (15, 23, 42), badge_rect, border_radius=6)
        v_title = self.font_header.render(v_meta["name"].upper(), True, v_meta["color"])
        surface.blit(v_title, (badge_rect.x + 12, badge_rect.y + 10))

        sub = self.font_small.render(v_meta["subtitle"], True, TEXT_MUTED)
        surface.blit(sub, (panel_x + 20, panel_y + 64))

        # 2. Policy COSTS & Parameters Card
        card1_y = panel_y + 90
        card1_rect = pygame.Rect(panel_x + 16, card1_y, panel_w - 32, 110)
        pygame.draw.rect(surface, (15, 23, 42), card1_rect, border_radius=6)

        c_header = self.font_header.render("AGENT POLICY PARAMETERS (COSTS)", True, TEXT_WHITE)
        surface.blit(c_header, (card1_rect.x + 12, card1_rect.y + 8))

        costs = policy.COSTS
        params_line1 = f"Lava Penalty:     {costs.get('lava', 1):<4}  | Monster Penalty:  {costs.get('monster', 1)}"
        params_line2 = f"Treasure Value:   {costs.get('treasure', -1):<4}  | Base Step Cost:   {costs.get('step', 1)}"
        params_line3 = f"Avoidance Radius: {policy.avoidance_radius} tiles"

        surface.blit(self.font_mono.render(params_line1, True, (248, 113, 113)), (card1_rect.x + 12, card1_rect.y + 36))
        surface.blit(self.font_mono.render(params_line2, True, (250, 204, 21)), (card1_rect.x + 12, card1_rect.y + 58))
        surface.blit(self.font_mono.render(params_line3, True, (56, 189, 248)), (card1_rect.x + 12, card1_rect.y + 80))

        # 3. Live Simulation Telemetry Card
        card2_y = card1_y + 125
        card2_rect = pygame.Rect(panel_x + 16, card2_y, panel_w - 32, 120)
        pygame.draw.rect(surface, (15, 23, 42), card2_rect, border_radius=6)

        t_header = self.font_header.render("LIVE TELEMETRY & RESULTS", True, TEXT_WHITE)
        surface.blit(t_header, (card2_rect.x + 12, card2_rect.y + 8))

        curr_cell = self.path[self.step_idx] if self.path else (1, 1)
        tot_cells = len(self.path) if self.path else 0
        gold_now = len(self.collected_gold)
        gold_tot = len(self.current_map.treasures)

        status_text = "ADVANCING"
        status_color = (56, 189, 248)
        if self.step_idx == len(self.path) - 1:
            if self.cause == "lava":
                status_text = "LETHAL BURN (LAVA)"
                status_color = LAVA_RED
            elif self.cause == "monster":
                status_text = "SLAIN (MONSTER AMBUSH)"
                status_color = (216, 180, 254)
            elif self.cause == "success":
                status_text = "EXIT REACHED (CLEARED)"
                status_color = (74, 222, 128)

        t_line1 = f"Status:      {status_text}"
        t_line2 = f"Position:    (X: {curr_cell[0]}, Y: {curr_cell[1]})  |  Step: {self.step_idx}/{max(1, tot_cells - 1)}"
        t_line3 = f"Treasure:    {gold_now}/{gold_tot} chests acquired"
        t_line4 = f"Benchmark:   Success: {tr.success_rate*100:.0f}% | Score: {tr.score:.3f}" if tr else ""

        surface.blit(self.font_mono.render(t_line1, True, status_color), (card2_rect.x + 12, card2_rect.y + 32))
        surface.blit(self.font_mono.render(t_line2, True, TEXT_WHITE), (card2_rect.x + 12, card2_rect.y + 52))
        surface.blit(self.font_mono.render(t_line3, True, GOLD_COLOR), (card2_rect.x + 12, card2_rect.y + 72))
        surface.blit(self.font_mono.render(t_line4, True, (148, 163, 184)), (card2_rect.x + 12, card2_rect.y + 92))

        # 4. Critique Evolutionary Directive Card
        card3_y = card2_y + 135
        card3_rect = pygame.Rect(panel_x + 16, card3_y, panel_w - 32, 130)
        pygame.draw.rect(surface, (15, 23, 42), card3_rect, border_radius=6)

        c_title = self.font_header.render("CRITIQUE LLM FEEDBACK & DIRECTIVE", True, (244, 114, 182))
        surface.blit(c_title, (card3_rect.x + 12, card3_rect.y + 8))

        if critique:
            instr = critique.instruction_for_next_generator
            words = instr.split()
            lines = []
            cur_line = []
            for w in words:
                cur_line.append(w)
                if len(" ".join(cur_line)) > 42:
                    lines.append(" ".join(cur_line))
                    cur_line = []
            if cur_line:
                lines.append(" ".join(cur_line))

            for l_idx, line in enumerate(lines[:4]):
                surface.blit(self.font_body.render(line, True, TEXT_WHITE), (card3_rect.x + 12, card3_rect.y + 32 + l_idx * 20))
        else:
            surface.blit(self.font_body.render("Optimal fitness target achieved.", True, TEXT_MUTED), (card3_rect.x + 12, card3_rect.y + 35))

        # 5. Interactive Keyboard Controls Box
        ctrl_y = card3_y + 145
        ctrl_rect = pygame.Rect(panel_x + 16, ctrl_y, panel_w - 32, 100)
        pygame.draw.rect(surface, (15, 23, 42), ctrl_rect, border_radius=6)

        surface.blit(self.font_small.render("INTERACTIVE CONTROLS:", True, (250, 204, 21)), (ctrl_rect.x + 12, ctrl_rect.y + 6))
        c_lines = [
            "[1, 2, 3, 4]: Select Version (V1 - V4)   |   [SPACE]: Pause / Resume",
            "[A]: Toggle Auto-Evolve Playback         |   [R]: Replay Active Run",
            "[M]: Switch Dungeon Benchmark Map        |   [LEFT / RIGHT]: Speed (0.5x - 4x)",
        ]
        for idx, cl in enumerate(c_lines):
            surface.blit(self.font_small.render(cl, True, TEXT_MUTED), (ctrl_rect.x + 12, ctrl_rect.y + 26 + idx * 22))

    def handle_input(self) -> bool:
        """Processes keyboard and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key in [pygame.K_1, pygame.K_KP1]:
                    self.current_version = 1
                    self.auto_evolve_mode = False
                    self.load_simulation_run()
                elif event.key in [pygame.K_2, pygame.K_KP2]:
                    self.current_version = 2
                    self.auto_evolve_mode = False
                    self.load_simulation_run()
                elif event.key in [pygame.K_3, pygame.K_KP3]:
                    self.current_version = 3
                    self.auto_evolve_mode = False
                    self.load_simulation_run()
                elif event.key in [pygame.K_4, pygame.K_KP4]:
                    self.current_version = 4
                    self.auto_evolve_mode = False
                    self.load_simulation_run()
                elif event.key == pygame.K_a:
                    self.auto_evolve_mode = not self.auto_evolve_mode
                    if self.auto_evolve_mode:
                        self.current_version = 1
                        self.load_simulation_run()
                elif event.key == pygame.K_r:
                    self.load_simulation_run()
                elif event.key == pygame.K_m:
                    self.current_map_idx = (self.current_map_idx + 1) % len(self.all_maps)
                    self.load_simulation_run()
                elif event.key == pygame.K_RIGHT:
                    self.speed_multiplier = min(4.0, self.speed_multiplier * 1.5)
                elif event.key == pygame.K_LEFT:
                    self.speed_multiplier = max(0.5, self.speed_multiplier / 1.5)

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()

            self.screen.fill(BG_COLOR)
            self.draw_dungeon(self.screen)
            self.draw_hud(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def launch_simulation(policies: List[Policy], test_results: List[TestResult], critiques: List[Critique]):
    """Launches the Pygame visual simulation window."""
    app = DungeonSimulationApp(policies, test_results, critiques)
    app.run()

