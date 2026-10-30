"""
AutoEvolve Protocol - Adversarial Iterative Agent Engine & Real Unit-Test Sandbox (Module 1)
"""

import os
import sys

# Ensure module1 directory and project root are on sys.path
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE1_DIR = os.path.dirname(AGENT_DIR)
PROJECT_ROOT = os.path.dirname(MODULE1_DIR)

for path in [MODULE1_DIR, PROJECT_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    load_dotenv(os.path.join(MODULE1_DIR, ".env"))
except ImportError:
    pass

try:
    from agent.task import TASK_PROMPT, HIDDEN_TESTS
    from agent.evaluator import evaluate_code
    from agent.generator import generate_code, extract_python_code
    from agent.critic import critique_code
    from agent.loop import run_loop
except ImportError:
    from module1.agent.task import TASK_PROMPT, HIDDEN_TESTS
    from module1.agent.evaluator import evaluate_code
    from module1.agent.generator import generate_code, extract_python_code
    from module1.agent.critic import critique_code
    from module1.agent.loop import run_loop

__all__ = [
    "TASK_PROMPT",
    "HIDDEN_TESTS",
    "evaluate_code",
    "generate_code",
    "extract_python_code",
    "critique_code",
    "run_loop",
]

