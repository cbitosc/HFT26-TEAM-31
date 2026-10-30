"""
AutoEvolve Protocol - Adversarial Iterative Agent Engine & Real Unit-Test Sandbox (Module 1)
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agent.task import TASK_PROMPT, HIDDEN_TESTS
from agent.evaluator import evaluate_code
from agent.generator import generate_code, extract_python_code
from agent.critic import critique_code
from agent.loop import run_loop

__all__ = [
    "TASK_PROMPT",
    "HIDDEN_TESTS",
    "evaluate_code",
    "generate_code",
    "extract_python_code",
    "critique_code",
    "run_loop",
]

