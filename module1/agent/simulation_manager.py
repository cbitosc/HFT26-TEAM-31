"""Simulation Manager for AutoEvolve Protocol.

Provides stateful management of simulations:
- Benchmark selection & custom task submission
- Live Mode, Offline Demo Mode, Replay Mode
- Step-by-step execution, Pause, Resume, Reset
- Event streaming and trace persistence
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional

from module1.agent.loop import run_loop
from module1.agent.task import (
    PREDEFINED_TASKS,
    TaskSpecification,
    get_task,
    list_available_tasks,
    register_custom_task,
)
from module1.agent.test_generator import TestGeneratorAgent

logger = logging.getLogger("AutoEvolve.SimulationManager")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNTIME_FILE = os.path.join(REPO_ROOT, "dashboard_runtime.json")


class SimulationInstance:
    """Represents an active or completed simulation run."""

    def __init__(
        self,
        sim_id: str,
        task_id: str,
        mode: str = "OFFLINE_DEMO",  # "LIVE", "OFFLINE_DEMO", "REPLAY"
        step_mode: bool = False,
        custom_task: Optional[TaskSpecification] = None,
    ):
        self.sim_id = sim_id
        self.task_id = task_id
        self.mode = mode
        self.step_mode = step_mode
        self.custom_task = custom_task
        self.status = "INITIALIZED"  # INITIALIZED, RUNNING, PAUSED, STEP_READY, COMPLETED, FAILED
        self.current_stage = "IDLE"
        self.current_version = "V0"
        self.events: List[Dict[str, Any]] = []
        self.iterations: List[Dict[str, Any]] = []
        self.test_generation: Optional[Dict[str, Any]] = None
        self.trace_data: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self._lock = threading.Lock()
        self._step_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Unpaused initially

    def add_event(self, event_type: str, payload: Dict[str, Any]):
        evt = {
            "type": event_type,
            "timestamp": time.time(),
            "payload": payload,
        }
        with self._lock:
            self.events.append(evt)

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "sim_id": self.sim_id,
                "task_id": self.task_id,
                "mode": self.mode,
                "step_mode": self.step_mode,
                "status": self.status,
                "current_stage": self.current_stage,
                "current_version": self.current_version,
                "events_count": len(self.events),
                "iterations_count": len(self.iterations),
                "test_generation": self.test_generation,
                "iterations": self.iterations,
                "error": self.error,
                "trace_data": self.trace_data,
            }


class SimulationManager:
    """Singleton simulation registry and orchestrator."""

    _instance: Optional[SimulationManager] = None

    def __new__(cls) -> SimulationManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._simulations = {}
            cls._instance._active_sim_id = None
        return cls._instance

    def create_simulation(
        self,
        task_id: str = "lru_cache_01",
        mode: str = "OFFLINE_DEMO",
        step_mode: bool = False,
        custom_task_dict: Optional[Dict[str, Any]] = None,
    ) -> SimulationInstance:
        sim_id = f"sim_{int(time.time() * 1000)}"
        custom_task = None

        if custom_task_dict:
            custom_task = TaskSpecification(
                task_id=custom_task_dict.get("task_id", f"custom_{sim_id}"),
                name=custom_task_dict.get("name", "Custom Task"),
                description=custom_task_dict.get("description", ""),
                programming_language=custom_task_dict.get("programming_language", "python"),
                class_or_function_name=custom_task_dict.get("class_or_function_name", "Solution"),
                functional_requirements=custom_task_dict.get("functional_requirements", []),
                input_output_spec=custom_task_dict.get("input_output_spec", {}),
                constraints=custom_task_dict.get("constraints", []),
                expected_behavior=custom_task_dict.get("expected_behavior", ""),
                evaluation_criteria=custom_task_dict.get("evaluation_criteria", {
                    "correctness": 0.60,
                    "efficiency": 0.20,
                    "safety": 0.10,
                    "quality": 0.10,
                }),
            )
            register_custom_task(custom_task)
            task_id = custom_task.task_id

        sim = SimulationInstance(
            sim_id=sim_id,
            task_id=task_id,
            mode=mode,
            step_mode=step_mode,
            custom_task=custom_task,
        )
        self._simulations[sim_id] = sim
        self._active_sim_id = sim_id
        return sim

    def get_simulation(self, sim_id: Optional[str] = None) -> Optional[SimulationInstance]:
        target_id = sim_id or self._active_sim_id
        if not target_id:
            return None
        return self._simulations.get(target_id)

    def run_simulation_thread(self, sim: SimulationInstance):
        def _target():
            sim.status = "RUNNING"
            force_mock = sim.mode in ("OFFLINE_DEMO", "REPLAY")

            def on_event_cb(evt_type: str, data: Dict[str, Any]):
                sim.add_event(evt_type, data)
                if evt_type == "STAGE_CHANGED":
                    sim.current_stage = data.get("stage", "IDLE")
                    if data.get("version"):
                        sim.current_version = data.get("version")
                elif evt_type == "TESTS_VALIDATED":
                    sim.test_generation = data

            try:
                # Execute pipeline loop
                trace = run_loop(
                    force_mock=force_mock,
                    task_id=sim.task_id,
                    custom_task=sim.custom_task,
                    on_event=on_event_cb,
                )
                sim.trace_data = trace
                sim.status = "COMPLETED"
                sim.current_stage = "COMPLETED"
            except Exception as e:
                logger.exception(f"Simulation failed: {e}")
                sim.status = "FAILED"
                sim.error = str(e)

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()


manager = SimulationManager()

