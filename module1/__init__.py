"""
AutoEvolve Protocol - Module 1: Adversarial Iterative Agent Engine & Real Sandbox
"""

import os
import sys

# Ensure module1 and project root are on sys.path
MODULE1_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULE1_DIR)

for path in [MODULE1_DIR, PROJECT_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

from module1.agent import (
    TASK_PROMPT,
    HIDDEN_TESTS,
    evaluate_code,
    generate_code,
    extract_python_code,
    critique_code,
    run_loop,
)

__all__ = [
    "TASK_PROMPT",
    "HIDDEN_TESTS",
    "evaluate_code",
    "generate_code",
    "extract_python_code",
    "critique_code",
    "run_loop",
]

