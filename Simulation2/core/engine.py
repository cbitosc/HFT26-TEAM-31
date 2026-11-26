"""
core/engine.py - Dungeon simulation and A* pathfinding engine based on Policy COSTS.
Calculates subjective agent paths and executes them against physical dungeon hazards.
"""

import heapq
import random
from typing import List, Tuple, Dict, Set, Optional
from core.contracts import Policy
from core.map_generator import DungeonMap


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic for grid navigation."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(pos: Tuple[int, int], dungeon: DungeonMap) -> List[Tuple[int, int]]:
    """Returns valid cardinal adjacent coordinates that are not solid walls."""
    x, y = pos
    neighbors = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < dungeon.width and 0 <= ny < dungeon.height:
            if not dungeon.is_wall(nx, ny):
                neighbors.append((nx, ny))
    return neighbors


def calculate_step_cost(
    from_pos: Tuple[int, int],
    to_pos: Tuple[int, int],
    dungeon: DungeonMap,
    policy: Policy
) -> float:
    """
    Computes the subjective cost of traversing into cell `to_pos` according to
    the policy's COSTS dictionary and avoidance_radius.
    """
    costs = policy.COSTS
    base_step = costs.get("step", 1)
    lava_penalty = costs.get("lava", 1)
    monster_penalty = costs.get("monster", 1)
    radius = policy.avoidance_radius

    total_cost = float(base_step)

    # Lava cost evaluation
    if to_pos in dungeon.lava_cells:
        total_cost += float(lava_penalty)

    # Monster proximity evaluation
    for mx, my in dungeon.monsters:
        dist = abs(to_pos[0] - mx) + abs(to_pos[1] - my)
        if dist == 0:
            # Entering monster tile directly
            total_cost += float(monster_penalty * 4)
        elif dist <= radius:
            # Within avoidance zone: penalty scales with proximity
            proximity_factor = radius - dist + 1
            total_cost += float(monster_penalty * proximity_factor)

    return total_cost


def find_path_astar(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    dungeon: DungeonMap,
    policy: Policy
) -> Optional[List[Tuple[int, int]]]:
    """
    Standard A* search from start to goal guided by the agent's subjective COSTS.
    """
    if start == goal:
        return [start]

    frontier = []
    # (f_cost, g_cost, current_node, path)
    heapq.heappush(frontier, (heuristic(start, goal), 0.0, start, [start]))
    visited_cost: Dict[Tuple[int, int], float] = {start: 0.0}

    while frontier:
        f_cost, g_cost, current, path = heapq.heappop(frontier)

        if current == goal:
            return path

        if g_cost > visited_cost.get(current, float("inf")):
            continue

        for neighbor in get_neighbors(current, dungeon):
            step_cost = calculate_step_cost(current, neighbor, dungeon, policy)
            tentative_g = g_cost + step_cost

            if tentative_g < visited_cost.get(neighbor, float("inf")):
                visited_cost[neighbor] = tentative_g
                priority = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, tentative_g, neighbor, path + [neighbor]))

    return None


def plan_journey(dungeon: DungeonMap, policy: Policy) -> List[Tuple[int, int]]:
    """
    Plans full dungeon route from Start -> (Optional Treasures) -> Exit.
    Decides whether to visit treasures based on COSTS['treasure'] reward utility.
    """
    costs = policy.COSTS
    treasure_reward = abs(costs.get("treasure", -1))  # E.g. 1 (negligible) vs 15 (high value)

    # Base direct path to exit
    direct_path = find_path_astar(dungeon.start, dungeon.exit, dungeon, policy)
    if not direct_path:
        return [dungeon.start]

    # Evaluate which treasures are worth detour given perceived reward
    available_treasures = list(dungeon.treasures)
    waypoints = [dungeon.start]
    current_pos = dungeon.start

    # Greedily consider reachable treasures
    unvisited = available_treasures.copy()
    while unvisited:
        best_candidate = None
        best_net_utility = 0.0
        best_path_to_candidate = None

        # Direct path to exit from current position
        direct_to_exit = find_path_astar(current_pos, dungeon.exit, dungeon, policy)
        direct_cost = len(direct_to_exit) if direct_to_exit else 999

        for candidate in unvisited:
            path_to_t = find_path_astar(current_pos, candidate, dungeon, policy)
            if not path_to_t:
                continue

            path_t_to_exit = find_path_astar(candidate, dungeon.exit, dungeon, policy)
            if not path_t_to_exit:
                continue

            # Perceived detour cost
            subjective_detour_cost = 0.0
            for i in range(len(path_to_t) - 1):
                subjective_detour_cost += calculate_step_cost(path_to_t[i], path_to_t[i+1], dungeon, policy)

            for i in range(len(path_t_to_exit) - 1):
                subjective_detour_cost += calculate_step_cost(path_t_to_exit[i], path_t_to_exit[i+1], dungeon, policy)

            # Net utility = subjective treasure reward - perceived detour cost
            # Strong reward (-15) motivates visiting; weak reward (-1) rarely justifies detour
            net_utility = float(treasure_reward * 2.5) - (subjective_detour_cost * 0.4)

            if net_utility > best_net_utility:
                best_net_utility = net_utility
                best_candidate = candidate
                best_path_to_candidate = path_to_t

        if best_candidate and best_net_utility > 2.0:
            waypoints.append(best_candidate)
            current_pos = best_candidate
            unvisited.remove(best_candidate)
        else:
            break

    waypoints.append(dungeon.exit)

    # Stitch the full planned path through all waypoints
    full_path: List[Tuple[int, int]] = []
    for i in range(len(waypoints) - 1):
        segment = find_path_astar(waypoints[i], waypoints[i+1], dungeon, policy)
        if not segment:
            break
        if full_path:
            full_path.extend(segment[1:])
        else:
            full_path.extend(segment)

    return full_path if full_path else direct_path


def simulate(
    dungeon: DungeonMap,
    policy: Policy,
    run_seed: int = 0
) -> Tuple[List[Tuple[int, int]], str, int, int]:
    """
    Executes the planned path inside the real dungeon physics.
    Returns:
      (executed_path, cause_of_termination, collected_treasures_count, step_count)
    Termination causes:
      - 'success': reached Exit
      - 'lava': stepped on a lethal lava tile
      - 'monster': intercepted/killed by monster
      - 'timeout': exceeded step limit without reaching exit
    """
    planned_path = plan_journey(dungeon, policy)
    rng = random.Random(dungeon.map_id * 1000 + run_seed)

    executed_path: List[Tuple[int, int]] = []
    collected_treasures: Set[Tuple[int, int]] = set()
    step_count = 0
    cause = "timeout"

    for step_idx, pos in enumerate(planned_path):
        step_count = step_idx
        executed_path.append(pos)

        # 1. Lethal Lava Hazard Check
        if pos in dungeon.lava_cells:
            cause = "lava"
            return executed_path, cause, len(collected_treasures), step_count

        # 2. Monster Ambush Hazard Check
        for mx, my in dungeon.monsters:
            dist = abs(pos[0] - mx) + abs(pos[1] - my)
            if dist == 0:
                cause = "monster"
                return executed_path, cause, len(collected_treasures), step_count
            elif dist == 1:
                # Close proximity hazard: monster strikes with 85% probability
                # Slight RNG variance across runs captures patrol timing
                if rng.random() < 0.85:
                    cause = "monster"
                    return executed_path, cause, len(collected_treasures), step_count

        # 3. Treasure Collection Check
        if pos in dungeon.treasures:
            collected_treasures.add(pos)

        # 4. Goal / Exit Check
        if pos == dungeon.exit:
            cause = "success"
            return executed_path, cause, len(collected_treasures), step_count

    return executed_path, cause, len(collected_treasures), step_count

