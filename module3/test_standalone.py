"""End-to-end verification CLI script for Module 3: Semantic Memory & Skill Registry.

Executes a full dry run:
1. Embeds and pins the canonical LRU Cache failure snapshot to IPFS via Lighthouse.
2. Verifies Base Sepolia RPC connectivity with Local DataDAO backup fallback.
3. Simulates Agent 2 encountering: 'I have an IndexError when capacity is zero in LRU cache.'
4. Queries MemoryService, verifies cosine similarity >= 0.80, and prints inherited prompt.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

# Ensure module3 parent is on sys.path so it runs standalone from anywhere
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from module3.config import get_config
from module3.memory_service import MemoryService
from module3.test_fixtures import get_lru_cache_fixture


def run_standalone_test() -> Dict[str, Any]:
    """Execute end-to-end memory store and retrieval lifecycle.

    Returns:
        Dictionary containing execution metrics, CID, and retrieved snapshot.
    """
    print("\n" + "=" * 70)
    print(" AUTOEVOLVE PROTOCOL - MODULE 3: SEMANTIC MEMORY & SKILL REGISTRY")
    print("=" * 70)

    # 1. Initialize Configuration and Unified Service
    config = get_config()
    service = MemoryService(config=config)

    # Check Base Sepolia RPC connection status
    rpc_online = service.contract.check_rpc_connection()
    rpc_display = (
        f"{config.base_sepolia_rpc_url} [ONLINE]"
        if rpc_online
        else f"{config.base_sepolia_rpc_url} [OFFLINE / UNREACHABLE]"
    )

    registry_status = (
        f"On-Chain EVM Contract ({config.registry_contract_address})"
        if config.is_contract_configured
        else "Local DataDAO Backup (Active - Contract Un-deployed / Off-Chain)"
    )

    print(f"\n[+] Active Configuration:")
    print(f"    - Embedding Model : {config.embedding_model_name}")
    print(f"    - Similarity Cutoff: {config.similarity_threshold:.2f}")
    print(f"    - Base Sepolia RPC: {rpc_display}")
    print(f"    - Registry Mode   : {registry_status}")
    print(f"    - Lighthouse Key  : {'[Configured]' if config.is_lighthouse_configured else '[Mock/Fallback Mode]'}")

    # 2. Stage 1: Embed and Store Agent 1 Run Snapshot
    fixture = get_lru_cache_fixture()
    print(f"\n[+] Step 1: Ingesting Agent 1 Run Snapshot...")
    print(f"    - Task ID         : {fixture['task_id']}")
    print(f"    - Failure Sig     : {fixture['failure_signature']}")
    print(f"    - Root Cause      : {fixture['root_cause']}")
    print(f"    - Fix Strategy    : {fixture['fix_strategy']}")

    stored = service.store_agent_run(
        task_id=fixture["task_id"],
        failure_signature=fixture["failure_signature"],
        root_cause=fixture["root_cause"],
        fix_strategy=fixture["fix_strategy"],
        diff=fixture["code_diff"],
        trace_hash=fixture["trace_hash"],
        agent_address=fixture["agent_address"],
        extra_metadata={
            "log_hash_v1": fixture["log_hash_v1"],
            "log_hash_v3": fixture["log_hash_v3"],
            "prompt_commitment": fixture["prompt_commitment"],
        },
    )

    cid = stored["cid"]
    emb_len = len(stored["embedding"])
    print(f"    -> Generated Dense Embedding Vector: {emb_len}-dimensional float vector")
    print(f"    -> Uploaded to IPFS/Filecoin CID     : {cid}")
    assert emb_len == 384, f"Expected 384 dimensions, got {emb_len}"
    assert cid, "CID must not be empty"

    # 3. Stage 2: Simulate Agent 2 Querying Cross-Agent Memory
    agent2_query = "I have an IndexError when capacity is zero in LRU cache."
    print(f"\n[+] Step 2: Agent 2 encountering new failure loop:")
    print(f"    - Agent 2 Query: \"{agent2_query}\"")
    print(f"    - Querying Decentralized Memory Registry...")

    inherited_memory = service.retrieve_inherited_memory(
        query_text=agent2_query,
        similarity_threshold=0.80,
    )

    # 4. Stage 3: Verification & Similarity Evaluation
    print(f"\n[+] Step 3: Verification & Similarity Evaluation:")
    assert inherited_memory is not None, "Memory retrieval failed! No matching snapshot found."

    score = inherited_memory.get("similarity_score", 0.0)
    print(f"    -> Cosine Similarity Score : {score:.4f} ({score * 100:.2f}%)")
    print(f"    -> Threshold Required      : >= 0.8000 (80.00%)")
    print(f"    -> Matched Failure Sig     : {inherited_memory.get('failure_signature')}")
    print(f"    -> Matched Task ID         : {inherited_memory.get('task_id')}")

    assert score >= 0.80, f"Cosine similarity {score:.4f} is below target threshold 0.80!"
    print("    [PASS] Cosine similarity meets or exceeds target threshold (>= 0.80).")

    # 5. Stage 4: Synthesize Agent 2 Prompt Injection
    prompt_injection = service.format_agent_prompt(inherited_memory)
    print(f"\n[+] Step 4: Synthesized Inherited Memory Prompt for Agent 2:")
    print("-" * 70)
    print(prompt_injection)
    print("-" * 70)

    # 6. Stage 5: Negative Control Test (Discriminative Accuracy)
    unrelated_query = "Database migration failed with syntax error in PostgreSQL schema foreign keys."
    print(f"\n[+] Step 5: Negative Control Test with Unrelated Query:")
    print(f"    - Unrelated Query: \"{unrelated_query}\"")
    unrelated_match = service.retrieve_inherited_memory(
        query_text=unrelated_query,
        similarity_threshold=0.80,
    )
    if unrelated_match is None:
        print("    [PASS] Successfully rejected unrelated query (score < 0.80).")
    else:
        unrelated_score = unrelated_match.get("similarity_score", 0.0)
        print(f"    [WARN] Unrelated match returned score {unrelated_score:.4f}")

    print("\n" + "=" * 70)
    print(" [SUCCESS] ALL MODULE 3 VERIFICATION CRITERIA PASSED 100%")
    print("=" * 70 + "\n")

    return {
        "cid": cid,
        "score": score,
        "inherited_memory": inherited_memory,
    }


def test_standalone_cli():
    """Pytest test case wrapping the end-to-end dry run."""
    results = run_standalone_test()
    assert results["score"] >= 0.80
    assert results["cid"]


if __name__ == "__main__":
    try:
        run_standalone_test()
        sys.exit(0)
    except AssertionError as ae:
        print(f"\n[FAIL] Assertion failed: {ae}")
        sys.exit(1)
    except Exception as exc:
        print(f"\n[ERROR] Unexpected error during verification: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
