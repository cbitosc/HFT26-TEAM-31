"""Contract & DataDAO Memory Registry Interface for Module 3.

Handles on-chain retrieval of IPFS memory CIDs from AutoEvolveRegistry.sol on Base Sepolia
with automatic, seamless fallback to the persistent Local DataDAO registry if the RPC fails
or the contract is un-deployed.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from web3 import Web3

from .config import Config, get_config
from .test_fixtures import get_mock_registry_records

logger = logging.getLogger(__name__)

# Minimal ABI for AutoEvolveRegistry.sol getAllRecords()
AUTO_EVOLVE_REGISTRY_ABI = [
    {
        "inputs": [],
        "name": "getAllRecords",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "agent", "type": "address"},
                    {"internalType": "string", "name": "ipfsCID", "type": "string"},
                    {"internalType": "string", "name": "failureSignature", "type": "string"},
                    {"internalType": "uint256", "name": "logHashV1", "type": "uint256"},
                    {"internalType": "uint256", "name": "logHashV3", "type": "uint256"},
                    {"internalType": "uint256", "name": "promptCommitment", "type": "uint256"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                ],
                "internalType": "struct AutoEvolveRegistry.Record[]",
                "name": "",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    }
]


class ContractInterface:
    """Interface connecting to Base Sepolia contract with Local DataDAO backup."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize the contract interface.

        Args:
            config: Optional Config instance. Defaults to get_config().
        """
        self.config = config or get_config()
        self._registry_file = self.config.cache_dir / "registry_records.json"
        self._local_registry: List[Dict[str, Any]] = self._load_local_registry()

    def _load_local_registry(self) -> List[Dict[str, Any]]:
        """Load persistent records from local cache or seed with default fixtures."""
        if self._registry_file.is_file():
            try:
                with open(self._registry_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    if isinstance(records, list) and records:
                        return records
            except Exception as e:
                logger.warning(f"Could not read local registry file ({e}). Reseeding.")

        initial_records = get_mock_registry_records()
        self._persist_local_registry(initial_records)
        return initial_records

    def _persist_local_registry(self, records: List[Dict[str, Any]]) -> None:
        """Persist current registry records to local cache disk."""
        try:
            with open(self._registry_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist local registry to disk: {e}")

    def add_local_record(self, cid: str, failure_signature: str, agent: str, **kwargs: Any) -> None:
        """Register a memory record in the persistent local DataDAO backup.

        Args:
            cid: The IPFS CID of the uploaded snapshot.
            failure_signature: The failure category identifier.
            agent: The EVM address of the agent submitting the fix.
            **kwargs: Extra metadata such as trace hashes, timestamps, or _payload.
        """
        record = {
            "cid": cid,
            "failure_signature": failure_signature,
            "agent": agent,
            **kwargs,
        }

        # Check if record with matching CID already exists to prevent duplicate entries
        for idx, existing in enumerate(self._local_registry):
            if existing.get("cid") == cid:
                self._local_registry[idx] = record
                self._persist_local_registry(self._local_registry)
                logger.info(f"Updated existing record in Local DataDAO for CID {cid}")
                return

        self._local_registry.append(record)
        self._persist_local_registry(self._local_registry)
        logger.info(f"Registered record in Local DataDAO for CID {cid}")

    def reset_local_registry(self, initial_records: Optional[List[Dict[str, Any]]] = None) -> None:
        """Reset the local DataDAO registry to initial or empty state."""
        records = initial_records if initial_records is not None else get_mock_registry_records()
        self._local_registry = [dict(r) for r in records]
        self._persist_local_registry(self._local_registry)
        logger.info("Reset local DataDAO registry.")

    def check_rpc_connection(self, rpc_url: Optional[str] = None) -> bool:
        """Verify reachability of the configured Base Sepolia RPC endpoint.

        Args:
            rpc_url: Optional RPC endpoint. Defaults to config.evm_rpc_url.

        Returns:
            True if connected and responding, False otherwise.
        """
        target_rpc = rpc_url or self.config.evm_rpc_url
        if not target_rpc:
            return False

        try:
            w3 = Web3(Web3.HTTPProvider(target_rpc, request_kwargs={"timeout": 3}))
            return bool(w3.is_connected())
        except Exception:
            return False

    def fetch_all_cids(
        self,
        contract_address: Optional[str] = None,
        rpc_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch all registered CIDs from Base Sepolia contract with Local DataDAO backup.

        1. If contract_address is provided and reachable, queries contract via Web3.py.
        2. If contract_address is un-deployed, or if RPC connection fails/times out,
           cleanly activates the Local DataDAO backup without throwing unhandled exceptions.

        Args:
            contract_address: Optional hex address of deployed AutoEvolveRegistry.sol.
            rpc_url: Optional Base Sepolia RPC endpoint URL.

        Returns:
            List of dictionaries: [{'cid': str, 'failure_signature': str, 'agent': str, ...}]
        """
        target_contract = contract_address or self.config.registry_contract_address
        target_rpc = rpc_url or self.config.evm_rpc_url

        # Check if on-chain contract should be queried
        should_use_contract = bool(
            self.config.is_contract_configured
            or (contract_address and rpc_url)
        )

        if not should_use_contract or not target_contract or not target_rpc:
            logger.info("On-chain contract not configured yet. Operating in Local DataDAO backup mode.")
            return self._format_mock_records()

        try:
            logger.info(f"Connecting to Base Sepolia RPC ({target_rpc}) to query contract {target_contract}...")
            w3 = Web3(Web3.HTTPProvider(target_rpc, request_kwargs={"timeout": 5}))

            if not w3.is_connected():
                logger.warning(
                    f"Base Sepolia RPC ({target_rpc}) unreachable. "
                    "Cleanly activating Local DataDAO backup mode."
                )
                return self._format_mock_records()

            checksum_address = Web3.to_checksum_address(target_contract.strip())
            contract = w3.eth.contract(address=checksum_address, abi=AUTO_EVOLVE_REGISTRY_ABI)

            raw_records = contract.functions.getAllRecords().call()
            parsed_records: List[Dict[str, Any]] = []

            for record in raw_records:
                if isinstance(record, (list, tuple)):
                    parsed_records.append({
                        "agent": str(record[0]),
                        "cid": str(record[1]),
                        "failure_signature": str(record[2]),
                        "logHashV1": int(record[3]),
                        "logHashV3": int(record[4]),
                        "promptCommitment": int(record[5]),
                        "timestamp": int(record[6]),
                    })
                elif isinstance(record, dict):
                    parsed_records.append({
                        "agent": str(record.get("agent", "")),
                        "cid": str(record.get("ipfsCID", record.get("cid", ""))),
                        "failure_signature": str(record.get("failureSignature", "")),
                        "logHashV1": int(record.get("logHashV1", 0)),
                        "logHashV3": int(record.get("logHashV3", 0)),
                        "promptCommitment": int(record.get("promptCommitment", 0)),
                        "timestamp": int(record.get("timestamp", 0)),
                    })

            logger.info(f"Retrieved {len(parsed_records)} records from on-chain Base Sepolia contract.")
            return parsed_records

        except Exception as e:
            logger.warning(
                f"On-chain contract query failed on {target_rpc} ({e}). "
                "Seamlessly activating Local DataDAO backup mode."
            )
            return self._format_mock_records()

    def _format_mock_records(self) -> List[Dict[str, Any]]:
        """Return formatted local DataDAO records preserving attached payloads."""
        results: List[Dict[str, Any]] = []
        for rec in self._local_registry:
            formatted = {
                "agent": rec.get("agent", "0x0000000000000000000000000000000000000000"),
                "cid": rec.get("cid", ""),
                "failure_signature": rec.get("failure_signature", ""),
                "logHashV1": rec.get("logHashV1", 0),
                "logHashV3": rec.get("logHashV3", 0),
                "promptCommitment": rec.get("promptCommitment", 0),
                "timestamp": rec.get("timestamp", 0),
            }
            if "_payload" in rec:
                formatted["_payload"] = rec["_payload"]
            results.append(formatted)
        return results
