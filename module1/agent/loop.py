"""Adversarial Agent Loop & ZK Attestation Engine for AutoEvolve Protocol.

Orchestrates the dynamic pipeline:
Task Analyzer -> Test Generator -> Test Validator -> Code Generator ->
Sandboxed Evaluator -> Critic Analysis -> Iterative Revision -> Verification Trace.
"""

from __future__ import annotations

import difflib
import json
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Optional

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE1_DIR = os.path.dirname(AGENT_DIR)
PROJECT_ROOT = os.path.dirname(MODULE1_DIR)

for path in [MODULE1_DIR, PROJECT_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

from module1.agent.critic import critique_code
from module1.agent.evaluator import evaluate_code
from module1.agent.generator import generate_code
from module1.agent.task import (
    HIDDEN_TESTS,
    RATE_LIMITER_TESTS,
    TaskSpecification,
    get_task,
)
from module1.agent.test_generator import TestGeneratorAgent

logger = logging.getLogger("AutoEvolve.Loop")


def compute_unified_diff(code_a: str, code_b: str, from_file: str, to_file: str) -> str:
    """Computes standard unified diff between two code iterations."""
    lines_a = code_a.splitlines(keepends=True)
    lines_b = code_b.splitlines(keepends=True)
    diff = difflib.unified_diff(lines_a, lines_b, fromfile=from_file, tofile=to_file)
    return "".join(diff)


def generate_changelog(iterations: List[Dict[str, Any]]) -> str:
    """Generates human-readable automated changelog documenting improvements across iterations."""
    lines = ["# AutoEvolve Protocol - Automated Improvement Changelog\n", "## Progression Summary\n"]
    for i, it in enumerate(iterations):
        lines.append(f"- **Iteration {it['version']}**: Score {it['eval']['final_score']} (Passed {it['eval']['passed']}/{it['eval']['total']})")

    lines.append("\n---\n")
    for i in range(1, len(iterations)):
        prev = iterations[i - 1]
        curr = iterations[i]
        diff_gain = round(curr['eval']['final_score'] - prev['eval']['final_score'], 1)
        critique = prev.get("critique", {})
        lines.append(f"### Phase {i}: {prev['version']} -> {curr['version']} Revision")
        lines.append(f"- **Diagnosed Failure**: `{critique.get('failure_type', 'None')}` (Severity: {critique.get('severity', 'MEDIUM')})")
        lines.append(f"- **Identified Root Cause**: {critique.get('root_cause', 'N/A')}")
        lines.append(f"- **Actionable Directive**: {critique.get('fix_instruction', 'N/A')}")
        lines.append(f"- **Observed Score Delta**: {diff_gain:+} points\n")

    return "\n".join(lines)


def run_loop(
    output_path: str = "execution_trace.json",
    inherited_memory: Optional[Dict[str, Any]] = None,
    force_mock: bool = True,
    task_id: str = "lru_cache_01",
    custom_task: Optional[TaskSpecification] = None,
    max_iterations: int = 3,
    on_event: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """Executes the dynamic generator-critic-evaluator improvement loop.

    Args:
        output_path: Destination JSON path for the execution trace.
        inherited_memory: DataDAO memory trace for Agent 2 skill inheritance.
        force_mock: If True, uses calibrated deterministic benchmark trajectories.
        task_id: Target task ID (defaults to 'lru_cache_01').
        custom_task: Optional custom TaskSpecification instance.
        max_iterations: Maximum revision attempts.
        on_event: Optional callback receiving event type and payload.

    Returns:
        Structured execution trace dictionary.
    """
    task = custom_task or get_task(task_id) or get_task("lru_cache_01")
    mode_label = "Calibrated Deterministic Mock" if force_mock else "Live API Evaluation"

    def emit(event_type: str, data: Dict[str, Any]):
        if on_event:
            on_event(event_type, data)

    emit("SIMULATION_STARTED", {"task_id": task.task_id, "mode": mode_label})

    # Stage 1: Dynamic Test Generation and Independent Validation
    emit("STAGE_CHANGED", {"stage": "TEST_GENERATION", "status": "RUNNING"})
    test_agent = TestGeneratorAgent()
    generated_suite = test_agent.generate_and_validate(task)
    validated_tests = generated_suite.validated_tests

    emit("TESTS_VALIDATED", {
        "total_generated": generated_suite.total_generated,
        "validated_count": len(validated_tests),
        "rejected_count": len(generated_suite.rejected_tests),
        "breakdown": generated_suite.category_breakdown,
    })
    emit("STAGE_CHANGED", {"stage": "TEST_GENERATION", "status": "COMPLETED"})

    iterations: List[Dict[str, Any]] = []
    current_critique: Optional[Dict[str, Any]] = None
    task_prompt = task.description

    for iter_idx in range(1, max_iterations + 1):
        version_label = f"V{iter_idx}"
        emit("STAGE_CHANGED", {"stage": "CODE_GENERATION", "version": version_label, "status": "RUNNING"})

        # Code Generation
        code = generate_code(
            task_prompt=task_prompt,
            critique=current_critique,
            attempt=version_label,
            inherited_memory=inherited_memory if iter_idx == 1 else None,
            force_mock=force_mock,
            task_id=task.task_id,
        )
        emit("STAGE_CHANGED", {"stage": "CODE_GENERATION", "version": version_label, "status": "COMPLETED"})

        # Sandboxed Subprocess Evaluation
        emit("STAGE_CHANGED", {"stage": "EVALUATION", "version": version_label, "status": "RUNNING"})
        eval_result = evaluate_code(code, task=task, test_suite=validated_tests)
        emit("EVALUATION_COMPLETED", {
            "version": version_label,
            "score": eval_result["final_score"],
            "passed": eval_result["passed"],
            "total": eval_result["total"],
        })
        emit("STAGE_CHANGED", {"stage": "EVALUATION", "version": version_label, "status": "COMPLETED"})

        # Adversarial Critique
        emit("STAGE_CHANGED", {"stage": "CRITIC_ANALYSIS", "version": version_label, "status": "RUNNING"})
        critique = critique_code(
            code_string=code,
            eval_result=eval_result,
            attempt=version_label,
            force_mock=force_mock,
            task_id=task.task_id,
        )
        current_critique = critique
        emit("CRITIQUE_COMPLETED", {"version": version_label, "critique": critique})
        emit("STAGE_CHANGED", {"stage": "CRITIC_ANALYSIS", "version": version_label, "status": "COMPLETED"})

        iterations.append({
            "version": version_label,
            "code": code,
            "eval": eval_result,
            "critique": critique,
        })

        # Stopping conditions: all tests pass or perfect score
        if eval_result["passed"] == eval_result["total"] and len(eval_result["failed_tests"]) == 0:
            break

    # Compute incremental diffs
    diffs: Dict[str, str] = {}
    for i in range(1, len(iterations)):
        v_prev = iterations[i - 1]["version"].lower()
        v_curr = iterations[i]["version"].lower()
        diff_key = f"diff_{v_prev}_{v_curr}"
        diffs[diff_key] = compute_unified_diff(
            iterations[i - 1]["code"],
            iterations[i]["code"],
            f"{v_prev}.py",
            f"{v_curr}.py",
        )

    changelog_text = generate_changelog(iterations)

    v1_eval = iterations[0]["eval"]
    v_last_eval = iterations[-1]["eval"]
    v_mid_eval = iterations[1]["eval"] if len(iterations) > 2 else v_last_eval

    zk_inputs = {
        "score_v1": int(round(v1_eval["final_score"])),
        "score_v2": int(round(v_mid_eval["final_score"])),
        "score_v3": int(round(v_last_eval["final_score"])),
        "log_hash_v1": v1_eval["trace_hash_zk"],
        "log_hash_v2": v_mid_eval["trace_hash_zk"],
        "log_hash_v3": v_last_eval["trace_hash_zk"],
        "hash_v1_hex": v1_eval["trace_hash_hex"],
        "hash_v2_hex": v_mid_eval["trace_hash_hex"],
        "hash_v3_hex": v_last_eval["trace_hash_hex"],
        "score_v1_full": v1_eval["final_score"],
        "score_v2_full": v_mid_eval["final_score"],
        "score_v3_full": v_last_eval["final_score"],
    }

    # Format trace data compatible with legacy module1/module2 expectations
    trace_data: Dict[str, Any] = {
        "task_id": task.task_id,
        "task_name": task.name,
        "programming_language": task.programming_language,
        "iterations_count": len(iterations),
        "validated_tests_count": len(validated_tests),
        "test_generation": generated_suite.to_dict(),
        "diffs": diffs,
        "changelog": changelog_text,
        "zk_inputs": zk_inputs,
    }

    for it in iterations:
        trace_data[it["version"].lower()] = {
            "code": it["code"],
            "eval": it["eval"],
            "critique": it["critique"],
        }

    # Ensure backwards compatibility keys exist
    if "v1" not in trace_data and iterations:
        trace_data["v1"] = iterations[0]
    if "v2" not in trace_data and len(iterations) > 1:
        trace_data["v2"] = iterations[1]
    if "v3" not in trace_data and len(iterations) > 2:
        trace_data["v3"] = iterations[2]

    # Save to disk
    if not os.path.isabs(output_path):
        out_file = os.path.join(MODULE1_DIR, output_path)
    else:
        out_file = output_path

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2)

    emit("SIMULATION_COMPLETED", {"task_id": task.task_id, "iterations": len(iterations)})
    return trace_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AutoEvolve Protocol - Adversarial Iterative Engine")
    parser.add_argument("--live", action="store_true", help="Execute live multi-agent loop with LLMs")
    parser.add_argument("--mock", action="store_true", help="Execute deterministic calibrated mock trajectory")
    parser.add_argument("--task", type=str, default="lru_cache_01", help="Task ID (e.g. lru_cache_01, rate_limiter_02)")
    parser.add_argument("--output", type=str, default="execution_trace.json", help="Path for generated trace JSON")
    args = parser.parse_args()

    force_mock = not args.live
    run_loop(output_path=args.output, force_mock=force_mock, task_id=args.task)
