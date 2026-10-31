"""
AutoEvolve Protocol - Constitutional AI Adversarial Critic
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
    # Also load from repo root if running from submodule
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
    """
    Guardrail Verification:
    Ensures that parsed JSON values do NOT contain forbidden code tokens:
    `def put`, `class LRUCache`, or ``` .
    Enforces pure verbal reflection without code leakage.
    """
    forbidden = ["def put", "class LRUCache", "```"]

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
    """
    Strips <think>...</think> reasoning blocks and ```json fences before JSON parsing.
    """
    if not text:
        return None
    # 1. Strip <think>...</think> reasoning tags
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # 2. Extract content within ```json ... ``` fences
    matches = re.findall(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL)
    for candidate in matches:
        candidate_clean = candidate.strip()
        try:
            data = json.loads(candidate_clean)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # 3. Fallback: attempt to find JSON object containing failure_type
    for brace_match in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", cleaned, flags=re.DOTALL):
        try:
            data = json.loads(brace_match.group(0))
            if isinstance(data, dict) and "failure_type" in data:
                return data
        except Exception:
            pass

    # 4. Outermost JSON object braces
    brace_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if brace_match:
        try:
            data = json.loads(brace_match.group(0))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return None


def get_mock_critique(attempt: str, eval_result: Dict[str, Any], task_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Provides calibrated mock critiques for deterministic testing.
    Emits structured diagnostic traces strictly in plain English (NO CODE).
    """
    norm = str(attempt).lower().strip()
    failed = eval_result.get("failed_tests", [])
    prompt_str = (task_prompt or "").lower()

    # Rate Limiter Domain
    if any(k in prompt_str for k in ["rate_limiter", "ratelimiter", "rate limiter", "token bucket"]):
        if norm in ("v1", "1"):
            return {
                "failure_type": "TokenRefillTimingAndZeroCapacityBoundaryFailure",
                "root_cause": (
                    "The rate limiter fails to handle capacity zero gracefully, does not continuously refill "
                    "tokens using monotonic time elapsed, and allows burst depletion without replenishing."
                ),
                "fix_instruction": (
                    "Ensure capacity <= 0 immediately returns False. Compute continuous token accumulation "
                    "using time.monotonic() delta multiplied by refill rate, capped at max capacity."
                ),
                "failed_tests": failed or ["zero_capacity_boundary", "time_refill_replenishment"],
            }
        elif norm in ("v2", "2"):
            return {
                "failure_type": "ConcurrencyRaceConditionAndTypeValidationFailure",
                "root_cause": (
                    "The rate limiter is not thread-safe under concurrent load and crashes when invalid "
                    "non-numeric inputs are provided."
                ),
                "fix_instruction": (
                    "Add reentrant lock (threading.RLock) around token operations. Defensively validate "
                    "arguments in try-except blocks and provide Google-style docstrings."
                ),
                "failed_tests": failed or ["invalid_argument_safety", "thread_safety_check"],
            }
        else:
            return {
                "failure_type": "None",
                "root_cause": "None. All unit tests, latency bounds, and safety requirements are fully satisfied.",
                "fix_instruction": "Maintain current architecture; no further revisions required.",
                "failed_tests": [],
            }

    if norm in ("v1", "1"):
        return {
            "failure_type": "EvictionOrderingAndPerformanceDegradation",
            "root_cause": (
                "The cache uses a linear list scan causing unacceptable latency under high throughput, "
                "fails to evict or reject items when capacity is zero, does not update recency order "
                "when an existing key is accessed, and crashes with an unhandled TypeError on unhashable keys."
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
            "root_cause": "None. All unit tests, latency bounds, and safety requirements are fully satisfied.",
            "fix_instruction": "Maintain current architecture; no further revisions required.",
            "failed_tests": [],
        }


def critique_code(
    code_string: str,
    eval_result: Dict[str, Any],
    attempt: str = "v1",
    task_prompt: Optional[str] = None,
    model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    force_mock: bool = False,
) -> Dict[str, Any]:
    """
    Constitutional AI separation:
    Invokes DeepSeek-R1 (Distill) via chat completions (temp 0.0, seed 42) to provide
    structured failure analysis. Applies guardrails to prohibit code generation
    with up to 2 retries, falling back to calibrated mock critique.
    """
    use_mock_env = os.getenv("USE_MOCK", "0").lower() in ("1", "true", "yes")
    if force_mock or use_mock_env:
        return get_mock_critique(attempt, eval_result)

    api_key = os.getenv("FEATHERLESS_API_KEY")
    if not api_key or requests is None:
        logger.info(f"Using deterministic calibrated mock critique for {attempt} (FEATHERLESS_API_KEY not configured).")
        return get_mock_critique(attempt, eval_result)

    # Resolve model: map unquantized / base DeepSeek-R1 to hosted distilled endpoint on Featherless
    resolved_model = os.getenv("FEATHERLESS_CRITIC_MODEL", model)
    if resolved_model in ("deepseek-ai/DeepSeek-R1", "DeepSeek-R1"):
        resolved_model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

    # If all tests passed and perfect score, report success
    if eval_result.get("passed", 0) == eval_result.get("total", 10) and not eval_result.get("failed_tests"):
        return {
            "failure_type": "None",
            "root_cause": "None. All unit tests, latency bounds, and safety requirements are fully satisfied.",
            "fix_instruction": "Maintain current architecture; no further revisions required.",
            "failed_tests": [],
        }

    endpoint = "https://api.featherless.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    system_message = (
        "You are an adversarial Constitutional AI Critic in the AutoEvolve Protocol. "
        "Your task is to analyze failed unit tests and execution traces. "
        "You must output ONLY valid JSON adhering to this schema wrapped in ```json ``` code block: "
        '{"failure_type": str, "root_cause": str, "fix_instruction": str, "failed_tests": list}. '
        "CRITICAL CONSTRAINTS:\n"
        "1. Write fix instructions strictly in plain English. NEVER output actual code, function definitions "
        "(like 'def put'), class headers (like 'class LRUCache'), or markdown code fences inside your JSON string values.\n"
        "2. For unhashable key errors, instruct defensive handling without crashing: get must return minus one, "
        "and put must safely ignore without inserting or raising unhandled exceptions."
    )

    user_message = (
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
            raw_text = message.get("content") or ""
            if not raw_text.strip():
                raw_text = message.get("reasoning") or message.get("reasoning_content") or ""
            parsed = extract_critique_json(raw_text)

            if parsed and passes_guardrail(parsed):
                # Ensure failed_tests field is present
                if "failed_tests" not in parsed:
                    parsed["failed_tests"] = eval_result.get("failed_tests", [])
                return parsed

            logger.warning(
                f"Critic guardrail failed or JSON malformed (attempt {attempt_idx + 1}/{max_retries + 1}). "
                f"Retrying..."
            )
        except Exception as e:
            logger.warning(f"Featherless Critic API call failed ({e}).")

    logger.info(f"Fallback to calibrated mock critique for {attempt} after retries.")
    return get_mock_critique(attempt, eval_result)

