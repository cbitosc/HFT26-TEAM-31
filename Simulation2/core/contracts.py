"""
core/contracts.py - Core data contracts for the AutoEvolve Dungeon Crawler.
Defines the communication primitives between Generator, Tester, and Critique.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class Policy:
    """Agent pathfinding and survival policy parameters."""
    version: int
    COSTS: Dict[str, int]  # e.g., {"lava": int, "monster": int, "treasure": int, "step": int}
    avoidance_radius: int
    changelog: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Policy":
        return cls(
            version=int(data.get("version", 1)),
            COSTS=dict(data.get("COSTS", {"lava": 1, "monster": 1, "treasure": -1, "step": 1})),
            avoidance_radius=int(data.get("avoidance_radius", 1)),
            changelog=str(data.get("changelog", ""))
        )


@dataclass
class TestResult:
    """Empirical test results produced deterministically by the Tester."""
    policy_version: int
    success_rate: float
    death_by_lava_pct: float
    death_by_monster_pct: float
    avg_treasure: float  # Scale 0 - 6
    avg_steps: int
    failure_traces: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def score(self) -> float:
        """
        Normalized fitness evaluation combining:
        - 60% Survival & Clear Success Rate
        - 30% Safe Treasure Acquisition Ratio
        - 10% Step Path Efficiency
        """
        treasure_ratio = min(1.0, self.avg_treasure / 3.2) if self.avg_treasure > 0 else 0.0
        step_efficiency = min(1.0, 24.0 / max(self.avg_steps, 1)) if self.avg_steps > 0 else 0.0
        calculated = (self.success_rate * 0.6) + (treasure_ratio * 0.3) + (step_efficiency * 0.1)
        return round(min(1.0, max(0.0, calculated)), 3)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["score"] = self.score
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResult":
        return cls(
            policy_version=int(data.get("policy_version", 1)),
            success_rate=float(data.get("success_rate", 0.0)),
            death_by_lava_pct=float(data.get("death_by_lava_pct", 0.0)),
            death_by_monster_pct=float(data.get("death_by_monster_pct", 0.0)),
            avg_treasure=float(data.get("avg_treasure", 0.0)),
            avg_steps=int(data.get("avg_steps", 0)),
            failure_traces=list(data.get("failure_traces", []))
        )


@dataclass
class Critique:
    """Evaluator critique containing root cause diagnosis and direct generator instructions."""
    score: float
    failure_modes: List[str]
    root_cause: str
    instruction_for_next_generator: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Critique":
        return cls(
            score=float(data.get("score", 0.0)),
            failure_modes=list(data.get("failure_modes", [])),
            root_cause=str(data.get("root_cause", "")),
            instruction_for_next_generator=str(data.get("instruction_for_next_generator", ""))
        )
