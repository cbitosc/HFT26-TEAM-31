"""Multi-Scenario Verification Suite for Module 3: Semantic Memory & Skill Registry.

Validates semantic retrieval, decentralized storage, and prompt injection across
multiple diverse software engineering domains (concurrency, auth, db pools, algorithms)
and verifies strict negative discrimination against unrelated issues.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure parent directory is on sys.path for standalone execution
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from module3.config import get_config
from module3.memory_service import MemoryService
from module3.test_fixtures import get_all_domain_fixtures


def run_multi_scenario_verification() -> Dict[str, Any]:
    """Execute end-to-end multi-scenario verification across diverse domains.

    Returns:
        Dictionary containing summary statistics, similarity matrix, and test status.
    """
    print("\n" + "=" * 78)
    print(" AUTOEVOLVE MODULE 3: MULTI-SCENARIO & CROSS-DOMAIN VERIFICATION SUITE")
    print("=" * 78)

    config = get_config()
    service = MemoryService(config=config)

    rpc_online = service.contract.check_rpc_connection()
    rpc_status = f"{config.base_sepolia_rpc_url} [ONLINE]" if rpc_online else "[OFFLINE]"
    print(f"\n[+] Active Infrastructure Status:")
    print(f"    - Base Sepolia RPC       : {rpc_status}")
    print(f"    - IPFS Storage Engine    : {'Lighthouse Node' if config.is_lighthouse_configured else 'Local DataDAO Cache'}")
    print(f"    - Dense Vector Dimension : 384 (all-MiniLM-L6-v2)")
    print(f"    - Acceptance Threshold   : >= {config.similarity_threshold:.2f} (80.00%)")

    # 1. Clean test environment state and Ingest Multiple Diverse Domains
    service.contract.reset_local_registry(initial_records=[])
    fixtures = get_all_domain_fixtures()
    print(f"\n[+] Stage 1: Ingesting {len(fixtures)} Diverse Engineering Failure Snapshots...")
    
    stored_records: List[Dict[str, Any]] = []
    for idx, fix in enumerate(fixtures, 1):
        print(f"    [{idx}/{len(fixtures)}] Ingesting domain: {fix['task_type']} ({fix['task_id']})")
        res = service.store_agent_run(
            task_id=fix["task_id"],
            failure_signature=fix["failure_signature"],
            root_cause=fix["root_cause"],
            fix_strategy=fix["fix_strategy"],
            diff=fix["code_diff"],
            trace_hash=fix["trace_hash"],
            agent_address=fix["agent_address"],
            extra_metadata={
                "task_type": fix["task_type"],
                "log_hash_v1": fix["log_hash_v1"],
                "log_hash_v3": fix["log_hash_v3"],
                "prompt_commitment": fix["prompt_commitment"],
            },
        )
        stored_records.append(res)
        print(f"        -> CID: {res['cid']} | Vector dimensions: {len(res['embedding'])}")

    print(f"\n[+] Ingestion Complete: {len(stored_records)} snapshots successfully vectorized and registered.")

    # 2. Define Real-World Agent Queries Across Every Ingested Domain
    eval_scenarios = [
        {
            "domain": "Data Structures & Memory",
            "expected_task_id": "task_lru_cache_ttl_v3",
            "expected_sig": "edge_case_capacity_zero",
            "query": "I have an IndexError when capacity is zero in LRU cache.",
        },
        {
            "domain": "Security & Authentication",
            "expected_task_id": "task_jwt_auth_clock_drift",
            "expected_sig": "jwt_signature_expired_clock_skew",
            "query": "Users getting ExpiredSignatureError intermittently right after login due to clock desynchronization",
        },
        {
            "domain": "Distributed Systems & Locks",
            "expected_task_id": "task_redis_lock_crash_resilience",
            "expected_sig": "redis_distributed_lock_deadlock",
            "query": "Redis lock is not releasing when worker dies causing permanent deadlock",
        },
        {
            "domain": "Database & Resource Management",
            "expected_task_id": "task_sqlalchemy_pool_leak",
            "expected_sig": "sqlalchemy_connection_pool_exhaustion",
            "query": "SQLAlchemy connection pool exhaustion: QueuePool limit reached due to leaked unclosed database sessions",
        },
        {
            "domain": "Algorithms & Numerical Precision",
            "expected_task_id": "task_binary_search_overflow",
            "expected_sig": "binary_search_integer_overflow",
            "query": "Binary search fails on huge sorted array with index error in midpoint computation",
        },
    ]

    # 3. Execute Semantic Retrieval and Accuracy Evaluation
    print(f"\n[+] Stage 2: Evaluating Retrieval Precision Across Diverse Domains (Cutoff >= 0.80):")
    print("-" * 78)
    print(f"{'Domain':<30} | {'Score':<8} | {'Status':<6} | {'Matched Task ID':<26}")
    print("-" * 78)

    passed_scenarios = 0
    for sc in eval_scenarios:
        match = service.retrieve_inherited_memory(
            query_text=sc["query"],
            similarity_threshold=config.similarity_threshold,
        )

        assert match is not None, f"Failed to retrieve memory for query: {sc['query']}"
        score = match.get("similarity_score", 0.0)
        matched_id = match.get("task_id", "")
        matched_sig = match.get("failure_signature", "")
        correct = (
            (matched_id == sc["expected_task_id"] or matched_sig == sc["expected_sig"])
            and (score >= 0.80)
        )

        status_str = "PASS" if correct else "FAIL"
        if correct:
            passed_scenarios += 1

        print(f"{sc['domain']:<30} | {score*100:>6.2f}% | {status_str:<6} | {matched_id:<26}")
        assert correct, f"Expected {sc['expected_task_id']} ({sc['expected_sig']}) with score >= 0.80, got {matched_id} ({matched_sig}) with score {score:.4f}"

    print("-" * 78)
    print(f"    Retrieval Accuracy: {passed_scenarios}/{len(eval_scenarios)} (100.0% Precision)")

    # 4. Negative Discrimination Controls (Zero False Positives)
    print(f"\n[+] Stage 3: Evaluating Negative Discrimination Controls (Unrelated Bugs):")
    negative_queries = [
        "CSS flexbox layout broken with div overflowing container on mobile viewport",
        "Kubernetes pod in CrashLoopBackOff: OOMKilled container limit exceeded",
        "Docker build failed: apt-get update returned non-zero exit code 100",
    ]

    rejected_count = 0
    for neg_q in negative_queries:
        neg_match = service.retrieve_inherited_memory(
            query_text=neg_q,
            similarity_threshold=config.similarity_threshold,
        )
        if neg_match is None:
            rejected_count += 1
            print(f"    [REJECTED] \"{neg_q[:55]}...\" -> Correctly ignored (score < 0.80)")
        else:
            neg_score = neg_match.get("similarity_score", 0.0)
            print(f"    [FALSE POSITIVE] Matched {neg_match.get('task_id')} with score {neg_score:.4f}")

    assert rejected_count == len(negative_queries), "Some negative queries were falsely matched!"
    print(f"    Negative Discrimination: {rejected_count}/{len(negative_queries)} (100.0% Rejection)")

    # 5. Cross-Domain Separation Matrix (Confusion Matrix)
    print(f"\n[+] Stage 4: Cross-Domain Semantic Confusion Matrix:")
    task_keys = [f["task_id"] for f in fixtures]
    short_names = ["LRU", "JWT", "Redis", "SQLPool", "BinSearch"]
    
    header = f"{'Query Domain':<14} | " + " | ".join(f"{name:>8}" for name in short_names)
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    matrix_rows: List[List[float]] = []
    for i, sc in enumerate(eval_scenarios):
        q_text = sc["query"]
        row_scores: List[float] = []
        for fix in fixtures:
            # Score this specific query against this fixture's embedding
            target_emb = fix.get("embedding")
            if not target_emb:
                target_emb = service.engine.generate_embedding(
                    fix["failure_signature"], fix["root_cause"], fix["fix_strategy"]
                )
            
            cand_sig = fix["failure_signature"]
            q_vec = service.engine.encode_text(q_text)
            sim_raw = service.engine.compute_similarity(q_vec, [target_emb])[0]
            
            ctx1 = service.engine.encode_text(f"Failure: {cand_sig}. Cause: {q_text}")
            sim_ctx1 = service.engine.compute_similarity(ctx1, [target_emb])[0]
            
            ctx2 = service.engine.encode_text(f"Failure: {cand_sig.replace('_', ' ')}. Cause: {q_text}")
            sim_ctx2 = service.engine.compute_similarity(ctx2, [target_emb])[0]
            
            best_s = max(sim_raw, sim_ctx1, sim_ctx2)
            row_scores.append(best_s)

        matrix_rows.append(row_scores)
        formatted_scores = " | ".join(f"{s*100:>7.1f}%" for s in row_scores)
        print(f"{short_names[i]:<14} | {formatted_scores}")

    print("-" * len(header))

    # 6. Verify Formatted Prompt Synthesis for an Ingested Domain
    print(f"\n[+] Stage 5: Verifying Inherited Prompt Synthesis for Redis Lock:")
    redis_match = service.retrieve_inherited_memory(
        query_text=eval_scenarios[2]["query"],
        similarity_threshold=config.similarity_threshold,
    )
    assert redis_match is not None
    redis_prompt = service.format_agent_prompt(redis_match)
    assert "redis_distributed_lock_deadlock" in redis_prompt
    assert "LUA_RELEASE" in redis_prompt
    print("    [PASS] Synthesized Agent 2 prompt successfully with code diff and strategy.")

    print("\n" + "=" * 78)
    print(" [SUCCESS] MULTI-SCENARIO VERIFICATION PASSED WITH 100% PRECISION & RECALL")
    print("=" * 78 + "\n")

    return {
        "passed_scenarios": passed_scenarios,
        "rejected_count": rejected_count,
        "matrix": matrix_rows,
    }


def test_multi_scenario_suite():
    """Pytest entrypoint for multi-scenario verification."""
    res = run_multi_scenario_verification()
    assert res["passed_scenarios"] == 5
    assert res["rejected_count"] == 3


if __name__ == "__main__":
    run_multi_scenario_verification()
