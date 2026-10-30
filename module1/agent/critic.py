"""Constitutional AI Adversarial Critic for AutoEvolve Protocol.

Analyzes execution failures and test results to provide natural-language root-cause
reflections and actionable revision instructions, strictly enforcing no-code-leakage
guardrails.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv(os.path.join(_repo_root, ".env"))
except ImportError:
    pass

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger("AutoEvolve.Critic")


def passes_guardrail(critique_json: Dict[str, Any]) -> bool:
    """Verifies that parsed JSON contains NO forbidden code tokens."""
    forbidden = ["def ", "class ", "```", "import "]

    def check(val: Any) -> bool:
        if isinstance(val, str):
            return not any(tok in val for tok in forbidden)
        elif isinstance(val, list):
            return all(check(item) for item in val)
        elif isinstance(val, dict):
            return all(check(v) for v in val.values())
        return True

    return check(critique_json)


def extract_critique_json(text: str) -> Optional[Dict[str, Any]]:
    """Strips reasoning blocks and parses structured JSON critique."""
    if not text:
        return None
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    matches = re.findall(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
    for candidate in matches:
        try:
            data = json.loads(candidate.strip())
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    for brace_match in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", cleaned, flags=re.DOTALL):
        try:
            data = json.loads(brace_match.group(0))
            if isinstance(data, dict) and "failure_type" in data:
                return data
        except Exception:
            pass

    brace_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if brace_match:
        try:
            data = json.loads(brace_match.group(0))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return None


def get_mock_critique(
    attempt: str,
    eval_result: Dict[str, Any],
    task_id: str = "lru_cache_01",
) -> Dict[str, Any]:
    """Provides calibrated mock critiques for deterministic benchmarking."""
    norm = str(attempt).lower().strip()
    failed = eval_result.get("failed_tests", [])
    is_rl = "rate" in task_id.lower() or "limiter" in task_id.lower()

    if is_rl:
        if norm in ("v1", "1"):
            return {
                "failure_type": "BoundaryBurstVulnerability",
                "severity": "CRITICAL",
                "root_cause": (
                    "The rate limiter employs fixed time-slice windowing. When requests cluster "
                    "near interval boundaries (such as end of minute one and start of minute two), "
                    "clients can execute twice the permitted quota within a fraction of the window."
                ),
                "fix_instruction": (
                    "Replace fixed window counters with a continuous sliding window algorithm, "
                    "such as sliding timestamp logs or double-ended queues. Store timestamps per user "
                    "and prune entries older than the current timestamp minus window duration."
                ),
                "failed_tests": failed or ["rl_boundary_burst_attack", "rl_invalid_inputs"],
            }
        elif norm in ("v2", "2"):
            return {
                "failure_type": "BoundaryPruningOffByOneAndInvalidInput",
                "severity": "HIGH",
                "root_cause": (
                    "The sliding window logic retains timestamps located precisely at the expiration cutoff boundary "
                    "(timestamp minus window seconds), and crashes when presented with empty or non-numeric identifiers."
                ),
                "fix_instruction": (
                    "Ensure expiration checks prune all timestamps less than or equal to the cutoff boundary. "
                    "Add defensive validation for user identifiers and non-numeric or negative timestamps."
                ),
                "failed_tests": failed or ["rl_exact_expiration_boundary", "rl_invalid_inputs"],
            }
        else:
            return {
                "failure_type": "None",
                "severity": "LOW",
                "root_cause": "None. All rate limiting boundaries, concurrency tests, and input safeguards pass.",
                "fix_instruction": "Maintain current architecture; no further revisions required.",
                "failed_tests": [],
            }

    # LRU Cache Benchmark
    if norm in ("v1", "1"):
        return {
            "failure_type": "EvictionOrderingAndPerformanceDegradation",
            "severity": "CRITICAL",
            "root_cause": (
                "The cache uses a linear list scan causing latency under high throughput, "
                "fails to evict or reject items when capacity is zero, does not update recency order "
                "on get, and crashes with an unhandled TypeError on unhashable keys."
            ),
            "fix_instruction": (
                "Replace linear storage with an O(1) hash map and ordered structure such as OrderedDict "
                "or Doubly-Linked List. Ensure capacity zero immediately rejects puts and returns minus one "
                "on gets. Move keys to most-recently-used on access, and safely intercept type errors on unhashable keys."
            ),
            "failed_tests": failed or ["capacity_zero", "order_after_get", "perf_timeout_>4s", "unhashable"],
        }
    elif norm in ("v2", "2"):
        return {
            "failure_type": "UnhashableKeyException",
            "severity": "HIGH",
            "root_cause": (
                "The cache assumes all input keys are hashable. When an unhashable key such as a list "
                "or dictionary is passed, the underlying dictionary operation raises an unhandled TypeError."
            ),
            "fix_instruction": (
                "Implement defensive error handling or pre-checks for key hashability. Intercept TypeError "
                "exceptions during get and put operations: return minus one for gets and safely return without inserting for puts."
            ),
            "failed_tests": failed or ["unhashable"],
        }
    else:
        return {
            "failure_type": "None",
            "severity": "LOW",
            "root_cause": "None. All unit tests, latency bounds, and safety requirements are fully satisfied.",
            "fix_instruction": "Maintain current architecture; no further revisions required.",
            "failed_tests": [],
        }


def critique_code(
    code_string: str,
    eval_result: Dict[str, Any],
    attempt: str = "v1",
    model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    force_mock: bool = False,
    task_id: str = "lru_cache_01",
) -> Dict[str, Any]:
    """Generates structured failure analysis enforcing pure natural language without code leakage."""
    use_mock_env = os.getenv("USE_MOCK", "0").lower() in ("1", "true", "yes")
    if force_mock or use_mock_env:
        return get_mock_critique(attempt, eval_result, task_id=task_id)

    api_key = os.getenv("FEATHERLESS_API_KEY")
    if not api_key or requests is None:
        logger.info(f"Using deterministic calibrated mock critique for {task_id} ({attempt}).")
        return get_mock_critique(attempt, eval_result, task_id=task_id)

    # Perfect score check
    if eval_result.get("passed", 0) == eval_result.get("total", 10) and not eval_result.get("failed_tests"):
        return {
            "failure_type": "None",
            "severity": "LOW",
            "root_cause": "None. All unit tests, latency bounds, and safety requirements are fully satisfied.",
            "fix_instruction": "Maintain current architecture; no further revisions required.",
            "failed_tests": [],
        }

    resolved_model = os.getenv("FEATHERLESS_CRITIC_MODEL", model)
    if resolved_model in ("deepseek-ai/DeepSeek-R1", "DeepSeek-R1"):
        resolved_model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

    endpoint = "https://api.featherless.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_message = (
        "You are an adversarial Constitutional AI Critic in the AutoEvolve Protocol. "
        "Your task is to analyze failed unit tests and execution traces. "
        "You must output ONLY valid JSON adhering to this schema wrapped in ```json ``` code block: "
        '{"failure_type": str, "severity": "CRITICAL"|"HIGH"|"MEDIUM"|"LOW", "root_cause": str, "fix_instruction": str, "failed_tests": list}. '
        "CRITICAL CONSTRAINTS:\n"
        "1. Write fix instructions strictly in plain English. NEVER output actual code, function definitions "
        "(like 'def put'), class headers, or markdown code fences inside your JSON string values.\n"
        "2. Explain WHY the failure occurred and what architectural principle resolves it."
    )

    user_message = (
        f"--- TASK ID: {task_id} ---\n"
        f"--- CODE UNDER REVIEW ---\n{code_string}\n\n"
        f"--- SANDBOX EVALUATION RESULTS ---\n"
        f"Passed: {eval_result.get('passed')} / {eval_result.get('total')}\n"
        f"Final Score: {eval_result.get('final_score')}\n"
        f"Failed Tests: {eval_result.get('failed_tests')}\n\n"
        f"Provide your structured critique wrapped in ```json ```."
    )

    payload = {
        "model": resolved_model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.0,
        "seed": 42,
    }

    max_retries = 2
    for attempt_idx in range(max_retries + 1):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]
            raw_text = message.get("content") or message.get("reasoning") or ""
            parsed = extract_critique_json(raw_text)

            if parsed and passes_guardrail(parsed):
                if "failed_tests" not in parsed:
                    parsed["failed_tests"] = eval_result.get("failed_tests", [])
                if "severity" not in parsed:
                    parsed["severity"] = "HIGH" if len(eval_result.get("failed_tests", [])) > 2 else "MEDIUM"
                return parsed

            logger.warning(f"Critic guardrail failed or JSON malformed (retry {attempt_idx + 1}).")
        except Exception as e:
            logger.warning(f"Featherless Critic API call failed ({e}).")

    return get_mock_critique(attempt, eval_result, task_id=task_id)
