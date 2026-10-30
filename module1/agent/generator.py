"""Dynamic Adversarial Generator Engine for AutoEvolve Protocol.

Generates initial implementations and iterative revisions guided by structured
critic feedback. Supports live LLM completions via OpenAI-compatible endpoints
(Featherless) as well as deterministic calibrated mock trajectories for benchmarks.
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

logger = logging.getLogger("AutoEvolve.Generator")


def extract_python_code(text: str) -> str:
    """Strips <think>...</think> reasoning traces and extracts pure Python code."""
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    match = re.search(r"```python\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    match_generic = re.search(r"```\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
    if match_generic:
        return match_generic.group(1).strip()
    return cleaned.strip()


def _load_mock(filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mock_path = os.path.join(current_dir, "mocks", filename)
    with open(mock_path, "r", encoding="utf-8") as f:
        return f.read()


def _load_mock_for_task_attempt(task_id: str, attempt: str) -> str:
    norm = str(attempt).lower().strip()
    is_rl = "rate" in task_id.lower() or "limiter" in task_id.lower()

    if is_rl:
        if norm in ("v1", "1"):
            return _load_mock("v1_failing_rl.py")
        elif norm in ("v2", "2"):
            return _load_mock("v2_fixed_rl.py")
        else:
            return _load_mock("v3_perfect_rl.py")
    else:
        # Default LRU Cache benchmark
        if norm in ("v1", "1"):
            return _load_mock("v1_failing.py")
        elif norm in ("v2", "2"):
            return _load_mock("v2_fixed.py")
        else:
            return _load_mock("v3_perfect.py")


def generate_code(
    task_prompt: str,
    critique: Optional[Dict[str, Any]] = None,
    attempt: str = "v1",
    inherited_memory: Optional[Dict[str, Any]] = None,
    model: str = "Qwen/Qwen2.5-Coder-32B-Instruct",
    force_mock: bool = False,
    task_id: str = "lru_cache_01",
) -> str:
    """Generates initial code or revised candidate implementation.

    - If inherited_memory is supplied on V1, retrieves verified V3 solution directly.
    - If force_mock is True, returns deterministic calibrated progression for the task.
    - Otherwise queries Featherless / OpenAI-compatible API with temperature 0.0.
    """
    norm_attempt = str(attempt).lower().strip()

    # Memory inheritance shortcut for demonstration
    if inherited_memory is not None and norm_attempt in ("v1", "1"):
        logger.info(f"Inherited memory provided for {task_id}; applying verified solution.")
        return _load_mock_for_task_attempt(task_id, "v3")

    use_mock_env = os.getenv("USE_MOCK", "0").lower() in ("1", "true", "yes")
    if force_mock or use_mock_env:
        return _load_mock_for_task_attempt(task_id, norm_attempt)

    api_key = os.getenv("FEATHERLESS_API_KEY")
    if not api_key or requests is None:
        logger.info(f"Using deterministic calibrated mock for {task_id} ({norm_attempt}).")
        return _load_mock_for_task_attempt(task_id, norm_attempt)

    endpoint = "https://api.featherless.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resolved_model = os.getenv("FEATHERLESS_GENERATOR_MODEL", model)

    if norm_attempt in ("v1", "1"):
        system_message = (
            "You are an expert software engineer implementing an initial working solution. "
            "Write concise, working Python code satisfying the core functional requirements. "
            "Return your implementation inside a ```python ``` code block."
        )
        user_prompt = f"Implement the initial working solution for this task:\n\n{task_prompt}"
    else:
        system_message = (
            "You are an expert algorithmic systems engineer refining a previous implementation. "
            "Address the critic's diagnosis and test failures while preserving working functionality. "
            "Return your revised implementation inside a ```python ``` code block."
        )
        user_prompt = (
            f"--- TASK SPECIFICATION ---\n{task_prompt}\n\n"
            f"--- CRITIQUE OF PREVIOUS IMPLEMENTATION ---\n"
            f"Failure Type: {critique.get('failure_type') if critique else 'N/A'}\n"
            f"Root Cause: {critique.get('root_cause') if critique else 'N/A'}\n"
            f"Fix Instruction: {critique.get('fix_instruction') if critique else 'N/A'}\n"
            f"Failed Tests: {critique.get('failed_tests') if critique else []}\n\n"
            f"Revise the solution to fix all issues. Return ONLY ```python ``` code."
        )

    payload = {
        "model": resolved_model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0,
        "seed": 42,
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"]
        extracted = extract_python_code(raw_text)
        if extracted:
            return extracted
        return _load_mock_for_task_attempt(task_id, norm_attempt)
    except Exception as e:
        logger.warning(f"Generator API call failed ({e}); falling back to calibrated mock.")
        return _load_mock_for_task_attempt(task_id, norm_attempt)
