"""Unified Memory Service for Module 3.

Coordinates vector encoding, IPFS decentralized storage, and on-chain contract
retrieval to empower autonomous agents with cross-run collective memory inheritance.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from .config import Config, get_config
from .contract_interface import ContractInterface
from .memory_engine import MemoryEngine
from .storage_uploader import StorageUploader

logger = logging.getLogger(__name__)


class MemoryService:
    """Unified service orchestrating Embeddings, IPFS storage, and on-chain querying."""

    def __init__(
        self,
        config: Optional[Config] = None,
        engine: Optional[MemoryEngine] = None,
        uploader: Optional[StorageUploader] = None,
        contract: Optional[ContractInterface] = None,
    ) -> None:
        """Initialize the unified memory service with sub-components.

        Args:
            config: Optional Config instance.
            engine: Optional MemoryEngine instance.
            uploader: Optional StorageUploader instance.
            contract: Optional ContractInterface instance.
        """
        self.config = config or get_config()
        self.engine = engine or MemoryEngine(model_name=self.config.embedding_model_name)
        self.uploader = uploader or StorageUploader(config=self.config)
        self.contract = contract or ContractInterface(config=self.config)

    def store_agent_run(
        self,
        task_id: str,
        failure_signature: str,
        root_cause: str,
        fix_strategy: str,
        diff: str,
        trace_hash: str,
        agent_address: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store an agent's failure critique and verified code diff in decentralized memory.

        1. Generates 384-dimensional dense semantic embedding.
        2. Builds structured snapshot payload.
        3. Pins JSON snapshot to IPFS via Lighthouse.
        4. Registers CID in the local/on-chain contract interface.

        Args:
            task_id: Unique identifier for the agent task.
            failure_signature: Categorical failure identifier (e.g. 'edge_case_capacity_zero').
            root_cause: Explanation of the failure etiology.
            fix_strategy: Algorithmic or structural fix strategy.
            diff: Unified diff string of the successful revision.
            trace_hash: Cryptographic hash of the execution trace.
            agent_address: Optional EVM address of the executing agent.
            extra_metadata: Optional additional metadata fields.

        Returns:
            Dictionary containing {'cid': cid, 'embedding': embedding, 'payload': payload}.
        """
        logger.info(f"Generating semantic embedding for task: {task_id}")
        embedding = self.engine.generate_embedding(
            failure_signature=failure_signature,
            root_cause=root_cause,
            fix_strategy=fix_strategy,
        )

        agent = agent_address or "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        timestamp = int(time.time())

        payload: Dict[str, Any] = {
            "task_id": task_id,
            "failure_signature": failure_signature,
            "root_cause": root_cause,
            "fix_strategy": fix_strategy,
            "code_diff": diff,
            "trace_hash": trace_hash,
            "embedding": embedding,
            "agent_address": agent,
            "timestamp": timestamp,
        }

        if extra_metadata:
            payload.update(extra_metadata)

        logger.info(f"Uploading snapshot to IPFS for task: {task_id}")
        cid = self.uploader.upload_snapshot_to_ipfs(payload)

        # Register CID in local fallback contract registry
        self.contract.add_local_record(
            cid=cid,
            failure_signature=failure_signature,
            agent=agent,
            timestamp=timestamp,
            _payload=payload,
        )

        logger.info(f"Successfully stored agent memory. CID: {cid}")
        return {
            "cid": cid,
            "embedding": embedding,
            "payload": payload,
        }

    def retrieve_inherited_memory(
        self,
        query_text: str,
        similarity_threshold: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve highest-scoring inherited memory snapshot matching an agent's failure.

        1. Fetches registered CIDs from smart contract (or fallback registry).
        2. Retrieves snapshot payloads from cache or IPFS gateway.
        3. Computes semantic similarity matching query against candidate failure representations.
        4. Returns top match if similarity >= threshold, else None.

        Args:
            query_text: Natural language or error description from Agent 2.
            similarity_threshold: Cosine similarity cutoff (defaults to config.similarity_threshold).

        Returns:
            Top-matching snapshot dict augmented with 'similarity_score', or None.
        """
        threshold = similarity_threshold if similarity_threshold is not None else self.config.similarity_threshold

        logger.info(f"Retrieving inherited memory for query: '{query_text}' (threshold: {threshold})")

        # 1. Fetch registered records
        records = self.contract.fetch_all_cids()
        if not records:
            logger.warning("No records found in contract or fallback registry.")
            return None

        # 2. Fetch payloads for each CID
        snapshots: List[Dict[str, Any]] = []

        for rec in records:
            cid = rec.get("cid")
            if not cid:
                continue

            payload: Optional[Dict[str, Any]] = None

            # Check if payload was already attached in mock record
            if "_payload" in rec and isinstance(rec["_payload"], dict):
                payload = rec["_payload"]
            else:
                try:
                    payload = self.uploader.fetch_snapshot_from_ipfs(cid)
                except Exception as e:
                    logger.debug(f"Could not load snapshot for CID {cid}: {e}")
                    continue

            if not payload:
                continue

            # Ensure embedding exists in snapshot; generate if absent
            emb = payload.get("embedding")
            if not emb or not isinstance(emb, list) or len(emb) != 384:
                emb = self.engine.generate_embedding(
                    failure_signature=payload.get("failure_signature", ""),
                    root_cause=payload.get("root_cause", ""),
                    fix_strategy=payload.get("fix_strategy", ""),
                )
                payload["embedding"] = emb

            snapshots.append(payload)

        if not snapshots:
            logger.warning("No valid snapshots could be loaded for comparison.")
            return None

        # 3. Compute cosine similarities
        query_vec = self.engine.encode_text(query_text)
        scored_pairs: List[Tuple[float, Dict[str, Any]]] = []

        for snap in snapshots:
            target_emb = snap["embedding"]
            cand_sig = snap.get("failure_signature", "")

            # Direct query similarity
            sim_raw = self.engine.compute_similarity(query_vec, [target_emb])[0]

            # Contextualized query similarity (matching against failure signature schema)
            if cand_sig and not query_text.startswith("Failure:"):
                ctx_query = f"Failure: {cand_sig}. Cause: {query_text}"
                ctx_vec = self.engine.encode_text(ctx_query)
                sim_ctx = self.engine.compute_similarity(ctx_vec, [target_emb])[0]

                natural_sig = cand_sig.replace("_", " ")
                ctx2_query = f"Failure: {natural_sig}. Cause: {query_text}"
                ctx2_vec = self.engine.encode_text(ctx2_query)
                sim_ctx2 = self.engine.compute_similarity(ctx2_vec, [target_emb])[0]

                best_sim = max(sim_raw, sim_ctx, sim_ctx2)
            else:
                best_sim = sim_raw

            scored_pairs.append((best_sim, snap))

        # 4. Rank candidates by descending similarity
        scored_pairs.sort(key=lambda pair: pair[0], reverse=True)

        top_score, top_snapshot = scored_pairs[0]
        logger.info(f"Top matching memory CID: {top_snapshot.get('task_id')} | Score: {top_score:.4f}")

        if top_score >= threshold:
            result = dict(top_snapshot)
            result["similarity_score"] = float(top_score)
            return result

        logger.info(f"Top score {top_score:.4f} did not meet threshold {threshold:.4f}.")
        return None

    def format_agent_prompt(self, snapshot: Dict[str, Any]) -> str:
        """Format an inherited memory snapshot into a structured prompt injection.

        Args:
            snapshot: Memory snapshot dictionary returned from retrieve_inherited_memory.

        Returns:
            Clean markdown prompt string for Agent 2.
        """
        score = snapshot.get("similarity_score", 1.0)
        task_id = snapshot.get("task_id", "unknown")
        sig = snapshot.get("failure_signature", "unknown")
        cause = snapshot.get("root_cause", "unspecified")
        strategy = snapshot.get("fix_strategy", "unspecified")
        diff = snapshot.get("code_diff", "").strip()

        prompt_str = (
            f"=== [AutoEvolve Memory Layer: Inherited Prior Fix] ===\n"
            f"Source Task: {task_id} (Semantic Match Score: {score:.2%})\n"
            f"Identified Failure Signature: {sig}\n"
            f"Root Cause: {cause}\n"
            f"Recommended Fix Strategy: {strategy}\n"
            f"Verified Reference Code Diff:\n"
            f"```diff\n{diff}\n```\n"
            f"======================================================"
        )
        return prompt_str
