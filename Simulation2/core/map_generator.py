"""
core/map_generator.py - Dungeon map generation and fixed benchmark suites.
Generates reproducible maps with walls, lava lakes, monsters, and treasure chests.
Calibrated so that:
- V1 dies to tempting lava shortcuts (lava deaths = 100%, success = 0%).
- V2 avoids lava, but greedily charges into monster threat zones to grab gold (monster deaths = 100%, success = 0%).
- V3 avoids both lava and monsters, reaching the exit for the first time, but skips treasures (gold = 0, score < 0.90).
- V4 maintains safety buffers AND sweeps up all safe treasure alcoves (gold = 3.4+, score > 0.90).
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Set


@dataclass
class DungeonMap:
    """Represents a discrete 2D grid dungeon with hazards and incentives."""
    map_id: int
    name: str
    width: int
    height: int
    grid: List[List[str]]
    start: Tuple[int, int]
    exit: Tuple[int, int]
    lava_cells: Set[Tuple[int, int]] = field(default_factory=set)
    monsters: List[Tuple[int, int]] = field(default_factory=list)
    treasures: List[Tuple[int, int]] = field(default_factory=list)

    def is_wall(self, x: int, y: int) -> bool:
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.grid[y][x] == "#"
        return True


def create_map_from_layout(map_id: int, name: str, layout: List[str]) -> DungeonMap:
    """Parses an ASCII dungeon layout into a DungeonMap object."""
    height = len(layout)
    width = len(layout[0])
    grid = [list(row) for row in layout]

    start = (1, 1)
    exit_pos = (width - 2, height - 2)
    lava = set()
    monsters = []
    treasures = []

    for y in range(height):
        for x in range(width):
            ch = grid[y][x]
            if ch == "S":
                start = (x, y)
            elif ch == "E":
                exit_pos = (x, y)
            elif ch == "L":
                lava.add((x, y))
            elif ch == "M":
                monsters.append((x, y))
            elif ch == "T":
                treasures.append((x, y))

    return DungeonMap(
        map_id=map_id,
        name=name,
        width=width,
        height=height,
        grid=grid,
        start=start,
        exit=exit_pos,
        lava_cells=lava,
        monsters=monsters,
        treasures=treasures
    )


def load_easy_maps() -> List[DungeonMap]:
    """3 smaller, simpler maps for Phase 0 Genesis seed evolution."""
    easy_1 = [
        "##########",
        "#S...#...#",
        "#.LL.#.T.#",
        "#....#.M.#",
        "###.######",
        "#...#....#",
        "#.T.#.LL.#",
        "#...#....#",
        "#.....E..#",
        "##########",
    ]

    easy_2 = [
        "##########",
        "#S.......#",
        "#..LL.T..#",
        "#..LL....#",
        "#....M...#",
        "#.T......#",
        "#....LL..#",
        "#......E.#",
        "#........#",
        "##########",
    ]

    easy_3 = [
        "##########",
        "#S.T.....#",
        "#.##.##..#",
        "#..M..#..#",
        "#.LL..#T.#",
        "#.LL..#..#",
        "#..#.....#",
        "#..#.LL..#",
        "#......E.#",
        "##########",
    ]

    layouts = [
        ("Easy Genesis 1", easy_1),
        ("Easy Genesis 2", easy_2),
        ("Easy Genesis 3", easy_3),
    ]

    return [create_map_from_layout(i, name, layout) for i, (name, layout) in enumerate(layouts)]


def load_fixed_maps() -> List[DungeonMap]:
    """
    10 fixed benchmark dungeon maps for fair, deterministic evaluation in Phase 1.
    Architecture:
    - Tempting Lava shortcut (low lava cost cuts through and burns).
    - Guarded Gold corridor (greedy looter with low monster avoidance charges in and is slain).
    - Safe bypass corridor (allows cautious agent to survive).
    - Separate safe treasure alcoves (rewards optimal balance in V4+).
    """
    maps_raw = [
        # Map 0: Lava Crucible (Pillar Hall with central lava river)
        ("Lava Crucible", [
            "##############",
            "#S...LLLL...E#",
            "#....####....#",
            "#.##......##.#",
            "#.##..M...##.#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#.T...T....T.#",
            "#............#",
            "##############",
        ]),
        # Map 1: Monster Bastion (Courtyard & Archway)
        ("Monster Bastion", [
            "##############",
            "#S....LLLL..E#",
            "#....#####...#",
            "#.#........#.#",
            "#.#...M....#.#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#..T...T..T..#",
            "#............#",
            "##############",
        ]),
        # Map 2: The Catacombs (Crypt Columns)
        ("The Catacombs", [
            "##############",
            "#S..LLLL....E#",
            "#...#####....#",
            "#..#......#..#",
            "#..#..M...#..#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#.T....T...T.#",
            "#............#",
            "##############",
        ]),
        # Map 3: Twin Chasm (Dual Bridges & Central Altar)
        ("Twin Chasm", [
            "##############",
            "#S...LLLL...E#",
            "#..#.####....#",
            "#..#......#..#",
            "#.....M......#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#..T..T...T..#",
            "#............#",
            "#............#",
            "##############",
        ]),
        # Map 4: The Gauntlet (Narrow Defile)
        ("The Gauntlet", [
            "##############",
            "#S.....LLLL.E#",
            "#...######...#",
            "#.#........#.#",
            "#....M.......#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#.T...T...T..#",
            "#............#",
            "##############",
        ]),
        # Map 5: Serpentine Abyss (Staggered Posts)
        ("Serpentine Abyss", [
            "##############",
            "#S..LLLL....E#",
            "#...####.....#",
            "#.##......##.#",
            "#....M.......#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#..T...T...T.#",
            "#............#",
            "##############",
        ]),
        # Map 6: Forgotten Vaults (Divided Chambers)
        ("Forgotten Vaults", [
            "##############",
            "#S...LLLL...E#",
            "##..######...#",
            "#..........#.#",
            "#....M.....#.#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#.T...T....T.#",
            "#............#",
            "##############",
        ]),
        # Map 7: Infernal Labyrinth (Checkered Hall)
        ("Infernal Labyrinth", [
            "##############",
            "#S....LLLL..E#",
            "#.##.#####...#",
            "#.#........#.#",
            "#.#...M....#.#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#.T....T...T.#",
            "#............#",
            "##############",
        ]),
        # Map 8: Shadow Keep (Keep Battlements)
        ("Shadow Keep", [
            "##############",
            "#S..LLLL....E#",
            "###.####.....#",
            "#............#",
            "#.....M......#",
            "#.##########.#",
            "#............#",
            "#.##########.#",
            "#............#",
            "#..T...T..T..#",
            "#............#",
            "##############",
        ]),
        # Map 9: Grand Sanctuary (Cathedral Nave)
        ("Grand Sanctuary", [
            "##############",
            "#S...LLLL...E#",
            "#.#..####....#",
            "#.#........#.#",
            "#.....M......#",
            "#.##########.#",
            "#............#",
            "#............#",
            "#.##########.#",
            "#.T...T....T.#",
            "#............#",
            "##############",
        ]),
    ]

    return [create_map_from_layout(i, name, layout) for i, (name, layout) in enumerate(maps_raw)]
