"""
AutoEvolve Protocol - LangGraph Multi-Stage Adversarial Agent Graph
Integrates LangGraph (StateGraph, Checkpointing, Conditional Edges)
and LangChain (ChatPromptTemplate, Constitutional Runnables, Schema Parsers)
for decentralized, ZK-attested self-improving autonomous agents.
"""

from __future__ import annotations

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, TypedDict

# LangChain Core imports
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Ensure imports resolve
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE1_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(MODULE1_DIR)

for p in [CURRENT_DIR, MODULE1_DIR, PROJECT_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from agent.task import TASK_PROMPT
    from agent.evaluator import evaluate_code
    from agent.generator import generate_code
    from agent.critic import critique_code
    from agent.test_case_creator import TestCaseCreator
except ImportError:
    from module1.agent.task import TASK_PROMPT
    from module1.agent.evaluator import evaluate_code
    from module1.agent.generator import generate_code
    from module1.agent.critic import critique_code
    from module1.agent.test_case_creator import TestCaseCreator

logger = logging.getLogger("AutoEvolve.LangGraph")


class AutoEvolveState(TypedDict):
    """LangGraph state representation for the AutoEvolve self-improving loop."""
    task_prompt: str
    custom_prompt: Optional[str]
    active_tests: Optional[List[Dict[str, Any]]]
    iteration: int
    attempt_label: str
    code: str
    previous_code: Optional[str]
    eval_result: Dict[str, Any]
    critique: Optional[Dict[str, Any]]
    history: List[Dict[str, Any]]
    inherited_memory: Optional[Dict[str, Any]]
    force_mock: bool
    output_path: str
    diffs: Dict[str, str]
    changelog: str
    zk_inputs: Dict[str, Any]
    trace_data: Dict[str, Any]
    completed: bool


def compute_unified_diff(code_a: str, code_b: str, from_file: str, to_file: str) -> str:
    """Computes standard unified diff between two code iterations."""
    import difflib
    lines_a = code_a.splitlines(keepends=True)
    lines_b = code_b.splitlines(keepends=True)
    diff = difflib.unified_diff(lines_a, lines_b, fromfile=from_file, tofile=to_file)
    return "".join(diff)


def infer_domain_metadata(
    active_prompt: str,
    code_v1: str,
    code_v2: str,
    code_v3: str,
    v1_eval: Dict[str, Any],
    v2_eval: Dict[str, Any],
    v3_eval: Dict[str, Any],
    critique_1: Dict[str, Any],
    critique_2: Dict[str, Any],
    zk_inputs: Dict[str, Any],
    diff_v1_v2: str,
    diff_v2_v3: str,
) -> Dict[str, Any]:
    """Infers dynamic architecture titles, prompt commitments, and diff summaries tailored to the task."""
    try:
        from agent.loop import infer_domain_metadata as loop_meta
        return loop_meta(
            active_prompt=active_prompt,
            code_v1=code_v1,
            code_v2=code_v2,
            code_v3=code_v3,
            v1_eval=v1_eval,
            v2_eval=v2_eval,
            v3_eval=v3_eval,
            critique_1=critique_1,
            critique_2=critique_2,
            zk_inputs=zk_inputs,
            diff_v1_v2=diff_v1_v2,
            diff_v2_v3=diff_v2_v3,
        )
    except Exception:
        return {
            "arch_v1": "Initial Prototype",
            "arch_v2": "Critique-Guided Revision",
            "arch_v3": "Production Architecture",
            "v1_prompt": active_prompt,
            "v2_prompt": f"Revision guided by: {critique_1.get('failure_type') if critique_1 else 'Critique 1'}",
            "v3_prompt": f"Hardening guided by: {critique_2.get('failure_type') if critique_2 else 'Critique 2'}",
            "v1_diff_stats": "+0 / -0 lines changed",
            "v2_diff_stats": f"+{len(diff_v1_v2.splitlines())} lines modified",
            "v3_diff_stats": f"+{len(diff_v2_v3.splitlines())} lines modified",
        }


def generate_changelog(
    v1_eval: Dict[str, Any],
    v2_eval: Dict[str, Any],
    v3_eval: Dict[str, Any],
    critique_1: Dict[str, Any],
    critique_2: Dict[str, Any],
    arch_v1: str = "Initial Prototype",
    arch_v2: str = "Revised Architecture",
    arch_v3: str = "Production Architecture",
) -> str:
    """Generates human-readable automated changelog documenting version improvements."""
    gain_1 = round(v2_eval['final_score'] - v1_eval['final_score'], 1)
    gain_2 = round(v3_eval['final_score'] - v2_eval['final_score'], 1)

    return f"""# AutoEvolve Protocol - Automated Improvement Changelog
(Orchestrated via LangGraph StateGraph & LangChain Constitutional Workflows)

## Summary of Progression
- **Iteration V1**: Score {v1_eval['final_score']} (Passed {v1_eval['passed']}/{v1_eval['total']}) — {arch_v1}
- **Iteration V2**: Score {v2_eval['final_score']} (Passed {v2_eval['passed']}/{v2_eval['total']}) [Gain: +{gain_1} pts] — {arch_v2}
- **Iteration V3**: Score {v3_eval['final_score']} (Passed {v3_eval['passed']}/{v3_eval['total']}) [Gain: +{gain_2} pts] — {arch_v3}

---

### Phase 1: V1 -> V2 Architectural Refinement (LangGraph: Critic -> Generator)
- **Diagnosed Failure Type**: `{critique_1.get('failure_type')}`
- **Identified Root Cause**: {critique_1.get('root_cause')}
- **Applied Changes**:
  - Re-architected code from {arch_v1} to {arch_v2}.
  - {critique_1.get('fix_instruction')}
- **Verification Metric**: Final score increased from {v1_eval['final_score']} to {v2_eval['final_score']}.

---

### Phase 2: V2 -> V3 Hardening & Constitutional Safety (LangGraph: Critic -> Generator)
- **Diagnosed Failure Type**: `{critique_2.get('failure_type')}`
- **Identified Root Cause**: {critique_2.get('root_cause')}
- **Applied Changes**:
  - Implemented production-grade architecture: {arch_v3}.
  - {critique_2.get('fix_instruction')}
  - Added comprehensive static typing and Google Python style docstrings.
- **Verification Metric**: Final score reached {v3_eval['final_score']} ({v3_eval['passed']}/{v3_eval['total']} tests passed).
"""


# ---------------------------------------------------------------------------
# LangGraph Nodes
# ---------------------------------------------------------------------------

def test_creator_node(state: AutoEvolveState) -> Dict[str, Any]:
    """
    LangGraph Test Creator Node:
    If a custom prompt is provided, synthesizes dynamic unit tests across
    Functional, Boundary, Safety, and Stress suites.
    """
    custom_prompt = state.get("custom_prompt")
    active_prompt = state.get("task_prompt", TASK_PROMPT)
    active_tests = state.get("active_tests")

    if custom_prompt and custom_prompt.strip() and not active_tests:
        print(f"\n[LangGraph TestCaseCreator Node] Analyzing Custom User Prompt...")
        creator = TestCaseCreator(task_prompt=active_prompt)
        active_tests = creator.create_test_suite()
        print(f"[LangGraph TestCaseCreator Node] Created {len(active_tests)} dynamic test cases.")

    return {
        "active_tests": active_tests,
    }


def generator_node(state: AutoEvolveState) -> Dict[str, Any]:
    """
    LangGraph Generator Node:
    Constructs LangChain prompt template and generates or revises candidate code.
    """
    iteration = state.get("iteration", 1)
    attempt_label = f"v{iteration}"
    critique = state.get("critique")
    inherited = state.get("inherited_memory")
    force_mock = state.get("force_mock", True)
    task_prompt = state.get("task_prompt", TASK_PROMPT)
    previous_code = state.get("previous_code") or state.get("code")

    stage_title = {
        1: "[LangGraph Stage 1] Generating V1 Candidate Solution...",
        2: "[LangGraph Stage 2] Generating V2 Revised Solution (guided by Critique 1)...",
        3: "[LangGraph Stage 3] Generating V3 Production-Grade Solution (guided by Critique 2)...",
    }.get(iteration, f"[LangGraph Stage {iteration}] Generating {attempt_label} Solution...")

    print(f"\n{stage_title}")
    code = generate_code(
        task_prompt=task_prompt,
        critique=critique,
        attempt=attempt_label,
        previous_code=previous_code,
        inherited_memory=inherited,
        force_mock=force_mock,
    )

    return {
        "code": code,
        "previous_code": code,
        "attempt_label": attempt_label,
    }


def evaluator_node(state: AutoEvolveState) -> Dict[str, Any]:
    """
    LangGraph Evaluator Node:
    Executes the candidate code in the subprocess sandbox across unit test suites,
    measures pass/fail, throughput latency, and computes 248-bit ZK-safe execution hashes.
    """
    code = state["code"]
    attempt_label = state.get("attempt_label", f"v{state.get('iteration', 1)}")
    active_tests = state.get("active_tests")

    print(f"[LangGraph Sandbox] Executing Subprocess Sandbox Unit-Test Suite on {attempt_label.upper()}...")
    eval_res = evaluate_code(code, tests=active_tests)

    print(f"  --> {attempt_label.upper()} Final Score: {eval_res['final_score']} "
          f"(Passed: {eval_res['passed']}/{eval_res['total']}, Failed: {eval_res['failed_tests']})")

    # Append to trajectory history
    history = list(state.get("history", []))
    history.append({
        "iteration": state.get("iteration", 1),
        "attempt": attempt_label,
        "code": code,
        "eval": eval_res,
        "critique": state.get("critique"),
    })

    return {
        "eval_result": eval_res,
        "history": history,
    }


def critic_node(state: AutoEvolveState) -> Dict[str, Any]:
    """
    LangGraph Adversarial Constitutional Critic Node:
    Submits code and evaluation trace to Constitutional Critic with strict anti-leakage guardrails.
    Advances the iteration counter.
    """
    code = state["code"]
    eval_res = state["eval_result"]
    attempt_label = state.get("attempt_label", f"v{state.get('iteration', 1)}")
    force_mock = state.get("force_mock", True)
    task_prompt = state.get("task_prompt", TASK_PROMPT)

    print(f"[LangGraph Critic] Submitting {attempt_label.upper()} to Adversarial Constitutional Critic (DeepSeek-R1)...")
    critique_data = critique_code(
        code_string=code,
        eval_result=eval_res,
        attempt=attempt_label,
        task_prompt=task_prompt,
        force_mock=force_mock,
    )
    print(f"  --> Critique Failure Type: {critique_data.get('failure_type')}")

    # Advance iteration counter for next generation node
    next_iteration = state.get("iteration", 1) + 1

    return {
        "critique": critique_data,
        "iteration": next_iteration,
        "attempt_label": f"v{next_iteration}",
    }


def attestation_node(state: AutoEvolveState) -> Dict[str, Any]:
    """
    LangGraph Final Attestation Node:
    Generates unified diffs, automated changelog, and BN254 scalar-field safe ZK inputs.
    Saves the final execution_trace.json artifact.
    """
    print("\n[LangGraph Attestation] Generating Unified Diffs and Cryptographic Commitments...")

    history = state.get("history", [])

    # Extract V1, V2, V3 records
    v1_rec = next((h for h in history if h.get("iteration") == 1 or h.get("attempt") == "v1"), None)
    v2_rec = next((h for h in history if h.get("iteration") == 2 or h.get("attempt") == "v2"), None)
    v3_rec = next((h for h in history if h.get("iteration") == 3 or h.get("attempt") == "v3"), None)

    code_v1 = v1_rec["code"] if v1_rec else state.get("code", "")
    code_v2 = v2_rec["code"] if v2_rec else code_v1
    code_v3 = v3_rec["code"] if v3_rec else code_v2

    eval_v1 = v1_rec["eval"] if v1_rec else state["eval_result"]
    eval_v2 = v2_rec["eval"] if v2_rec else eval_v1
    eval_v3 = v3_rec["eval"] if v3_rec else state["eval_result"]

    critique_1 = v2_rec.get("critique") or {}
    critique_2 = v3_rec.get("critique") or {}
    critique_3 = critique_code(code_v3, eval_v3, attempt="v3", task_prompt=state.get("task_prompt", TASK_PROMPT), force_mock=state.get("force_mock", True))

    diff_v1_v2 = compute_unified_diff(code_v1, code_v2, "v1_failing.py", "v2_fixed.py")
    diff_v2_v3 = compute_unified_diff(code_v2, code_v3, "v2_fixed.py", "v3_perfect.py")

    zk_inputs = {
        "score_v1": int(round(eval_v1["final_score"])),
        "score_v2": int(round(eval_v2["final_score"])),
        "score_v3": int(round(eval_v3["final_score"])),
        "log_hash_v1": eval_v1["trace_hash_zk"],
        "log_hash_v2": eval_v2["trace_hash_zk"],
        "log_hash_v3": eval_v3["trace_hash_zk"],
        "hash_v1_hex": eval_v1["trace_hash_hex"],
        "hash_v2_hex": eval_v2["trace_hash_hex"],
        "hash_v3_hex": eval_v3["trace_hash_hex"],
        "score_v1_full": eval_v1["final_score"],
        "score_v2_full": eval_v2["final_score"],
        "score_v3_full": eval_v3["final_score"],
    }

    meta = infer_domain_metadata(
        active_prompt=state.get("task_prompt", TASK_PROMPT),
        code_v1=code_v1,
        code_v2=code_v2,
        code_v3=code_v3,
        v1_eval=eval_v1,
        v2_eval=eval_v2,
        v3_eval=eval_v3,
        critique_1=critique_1,
        critique_2=critique_2,
        zk_inputs=zk_inputs,
        diff_v1_v2=diff_v1_v2,
        diff_v2_v3=diff_v2_v3,
    )

    changelog_text = generate_changelog(
        v1_eval=eval_v1,
        v2_eval=eval_v2,
        v3_eval=eval_v3,
        critique_1=critique_1,
        critique_2=critique_2,
        arch_v1=meta["arch_v1"],
        arch_v2=meta["arch_v2"],
        arch_v3=meta["arch_v3"],
    )

    active_prompt = state.get("task_prompt", TASK_PROMPT)
    custom_prompt = state.get("custom_prompt")

    trace_data = {
        "task_id": "custom_agent_task" if custom_prompt else "lru_cache_01",
        "task_prompt": active_prompt,
        "orchestrator": "LangGraph.StateGraph (v1.2.5)",
        "v1": {
            "code": code_v1,
            "eval": eval_v1,
            "critique": critique_1,
            "architecture": meta["arch_v1"],
            "prompt": meta["v1_prompt"],
            "diff_stats": meta["v1_diff_stats"],
        },
        "v2": {
            "code": code_v2,
            "eval": eval_v2,
            "critique": critique_2,
            "architecture": meta["arch_v2"],
            "prompt": meta["v2_prompt"],
            "diff_stats": meta["v2_diff_stats"],
        },
        "v3": {
            "code": code_v3,
            "eval": eval_v3,
            "critique": critique_3,
            "architecture": meta["arch_v3"],
            "prompt": meta["v3_prompt"],
            "diff_stats": meta["v3_diff_stats"],
        },
        "diffs": {
            "diff_v1_v2": diff_v1_v2,
            "diff_v2_v3": diff_v2_v3,
        },
        "changelog": changelog_text,
        "zk_inputs": zk_inputs,
        "custom_prompt": active_prompt if custom_prompt else None,
        "dynamic_tests": state.get("active_tests"),
    }

    output_path = state.get("output_path", "execution_trace.json")
    if not os.path.isabs(output_path):
        out_file = os.path.join(MODULE1_DIR, output_path)
    else:
        out_file = output_path

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2)

    print(f"\n[Success] LangGraph execution trace successfully exported to: {out_file}")
    print(f"ZK Inputs Verification:")
    print(f"  Score V1: {zk_inputs['score_v1']} (Trace Hash: {zk_inputs['hash_v1_hex'][:16]}...)")
    print(f"  Score V2: {zk_inputs['score_v2']} (Trace Hash: {zk_inputs['hash_v2_hex'][:16]}...)")
    print(f"  Score V3: {zk_inputs['score_v3']} (Trace Hash: {zk_inputs['hash_v3_hex'][:16]}...)")
    print("=" * 72)

    return {
        "diffs": {"diff_v1_v2": diff_v1_v2, "diff_v2_v3": diff_v2_v3},
        "changelog": changelog_text,
        "zk_inputs": zk_inputs,
        "trace_data": trace_data,
        "completed": True,
    }


# ---------------------------------------------------------------------------
# LangGraph Conditional Routing Logic
# ---------------------------------------------------------------------------

def should_continue(state: AutoEvolveState) -> str:
    """
    LangGraph Conditional Edge Router:
    - If score is 100.0 or maximum iteration limit (iteration >= 3) reached -> route to 'attestation'
    - Otherwise -> route to 'critic' to evaluate failures and guide next revision.
    """
    iteration = state.get("iteration", 1)
    eval_result = state.get("eval_result", {})
    score = eval_result.get("final_score", 0.0)

    if score >= 100.0 or iteration >= 3:
        return "attestation"
    return "critic"


# ---------------------------------------------------------------------------
# LangGraph StateGraph Construction
# ---------------------------------------------------------------------------

def build_autoevolve_graph(checkpointer: Optional[Any] = None) -> Any:
    """
    Builds the cyclical, state-driven LangGraph workflow for AutoEvolve:
    START -> test_creator -> generator -> evaluator -> (conditional edge: critic or attestation)
    critic -> generator
    attestation -> END
    """
    workflow = StateGraph(AutoEvolveState)

    # Add Nodes
    workflow.add_node("test_creator", test_creator_node)
    workflow.add_node("generator", generator_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("attestation", attestation_node)

    # Add Directed Edges
    workflow.add_edge(START, "test_creator")
    workflow.add_edge("test_creator", "generator")
    workflow.add_edge("generator", "evaluator")

    # Add Conditional Routing
    workflow.add_conditional_edges(
        "evaluator",
        should_continue,
        {
            "critic": "critic",
            "attestation": "attestation",
        },
    )

    workflow.add_edge("critic", "generator")
    workflow.add_edge("attestation", END)

    return workflow.compile(checkpointer=checkpointer)


def export_graph_mermaid() -> str:
    """Exports the LangGraph StateGraph topology as a Mermaid diagram."""
    app = build_autoevolve_graph()
    try:
        return app.get_graph().draw_mermaid()
    except Exception:
        return """graph TD
    START --> test_creator
    test_creator --> generator
    generator --> evaluator
    evaluator -->|score < 100 & iter < 3| critic
    evaluator -->|score == 100 or iter >= 3| attestation
    critic --> generator
    attestation --> END
"""


def run_graph_loop(
    output_path: str = "execution_trace.json",
    inherited_memory: Optional[Dict[str, Any]] = None,
    force_mock: bool = True,
    custom_prompt: Optional[str] = None,
    thread_id: str = "autoevolve_main_thread",
) -> Dict[str, Any]:
    """
    Compiles and executes the LangGraph StateGraph pipeline for the agent loop.
    Returns the complete trace_data dictionary.
    """
    mode_label = "Calibrated Deterministic Mock" if force_mock else "Live Featherless API (Qwen 2.5 Coder + DeepSeek-R1)"
    print("=" * 72)
    print("  AutoEvolve Protocol - LangGraph Cyclical Adversarial Engine")
    print(f"  Mode: {mode_label}")
    print("=" * 72)

    # Initialize in-memory checkpointer for state isolation & time travel
    memory_saver = MemorySaver()
    app = build_autoevolve_graph(checkpointer=memory_saver)

    active_prompt = custom_prompt.strip() if custom_prompt and custom_prompt.strip() else TASK_PROMPT

    initial_state: AutoEvolveState = {
        "task_prompt": active_prompt,
        "custom_prompt": custom_prompt,
        "active_tests": None,
        "iteration": 1,
        "attempt_label": "v1",
        "code": "",
        "previous_code": None,
        "eval_result": {},
        "critique": None,
        "history": [],
        "inherited_memory": inherited_memory,
        "force_mock": force_mock,
        "output_path": output_path,
        "diffs": {},
        "changelog": "",
        "zk_inputs": {},
        "trace_data": {},
        "completed": False,
    }

    config = {"configurable": {"thread_id": thread_id}}
    final_state = app.invoke(initial_state, config=config)
    return final_state["trace_data"]


if __name__ == "__main__":
    run_graph_loop(force_mock=True)

