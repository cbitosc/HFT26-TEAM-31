"""Lighthouse IPFS Storage Uploader and Gateway Retrieval for Module 3.

Pins agent execution snapshots (diffs, critiques, embeddings, and metadata)
to IPFS/Filecoin via Lighthouse Storage with automatic local cache fallbacks.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
import requests

from .config import Config, get_config

logger = logging.getLogger(__name__)


class StorageUploader:
    """Handles snapshot persistence to IPFS via Lighthouse SDK or HTTP API."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize the storage uploader with configuration.

        Args:
            config: Optional Config instance. Defaults to get_config().
        """
        self.config = config or get_config()
        self.cache_dir = self.config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def upload_snapshot_to_ipfs(self, snapshot_payload: Dict[str, Any]) -> str:
        """Upload a memory snapshot JSON to IPFS via Lighthouse.

        Writes the snapshot to a temporary file, attempts upload via Lighthouse SDK
        or direct REST API. If the API key is empty, invalid, or network upload fails,
        it cleanly falls back to generating a deterministic mock CID and persisting
        to local cache.

        Args:
            snapshot_payload: JSON-serializable dictionary containing agent run details.

        Returns:
            The IPFS Content Identifier (CID) string (e.g. 'bafy...').
        """
        payload_bytes = json.dumps(snapshot_payload, sort_keys=True, indent=2).encode("utf-8")
        cid: Optional[str] = None

        # Attempt remote upload if API key is present
        if self.config.is_lighthouse_configured:
            try:
                cid = self._upload_via_sdk(payload_bytes)
            except Exception as e_sdk:
                logger.warning(f"Lighthouse SDK upload failed: {e_sdk}. Trying REST API fallback.")
                try:
                    cid = self._upload_via_rest_api(payload_bytes)
                except Exception as e_rest:
                    logger.warning(f"Lighthouse REST API upload failed: {e_rest}. Using local fallback.")

        # Fallback to deterministic mock CID if remote upload did not succeed
        if not cid:
            content_hash = hashlib.sha256(payload_bytes).hexdigest()[:24]
            cid = f"bafy_mock_{content_hash}"
            logger.info(f"Generated deterministic mock CID for snapshot: {cid}")

        # Always cache snapshot locally to guarantee fast, offline-tolerant retrieval
        self._save_to_cache(cid, snapshot_payload)
        return cid

    def _upload_via_sdk(self, payload_bytes: bytes) -> str:
        """Upload using the official lighthouseweb3 Python SDK."""
        with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as tmp_file:
            tmp_file.write(payload_bytes)
            tmp_path = tmp_file.name

        try:
            from lighthouseweb3 import Lighthouse
            lh = Lighthouse(token=self.config.lighthouse_api_key)
            response = lh.upload(tmp_path)

            if isinstance(response, dict):
                if "data" in response and isinstance(response["data"], dict) and "Hash" in response["data"]:
                    return str(response["data"]["Hash"])
                if "Hash" in response:
                    return str(response["Hash"])

            raise ValueError(f"Unrecognized Lighthouse SDK response format: {response}")
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def _upload_via_rest_api(self, payload_bytes: bytes) -> str:
        """Upload snapshot directly using Lighthouse HTTP REST API endpoint."""
        url = "https://node.lighthouse.storage/api/v0/add"
        headers = {"Authorization": f"Bearer {self.config.lighthouse_api_key}"}
        files = {"file": ("snapshot.json", payload_bytes, "application/json")}

        resp = requests.post(url, headers=headers, files=files, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, dict):
            if "Hash" in data:
                return str(data["Hash"])
            if "data" in data and isinstance(data["data"], dict) and "Hash" in data["data"]:
                return str(data["data"]["Hash"])

        raise ValueError(f"Unexpected response from Lighthouse REST API: {data}")

    def fetch_snapshot_from_ipfs(self, cid: str, timeout: int = 4) -> Dict[str, Any]:
        """Fetch snapshot payload given an IPFS CID.

        Checks local cache first, then built-in fixtures, and finally queries Lighthouse IPFS gateway.

        Args:
            cid: IPFS Content Identifier.
            timeout: Gateway request timeout in seconds.

        Returns:
            Snapshot dictionary.

        Raises:
            FileNotFoundError: If snapshot cannot be located locally or via gateway.
        """
        # 1. Check local cache
        cached_data = self._read_from_cache(cid)
        if cached_data is not None:
            return cached_data

        # 2. Check fixture fallbacks if standard mock CIDs are queried
        from .test_fixtures import (
            MOCK_LRU_CID,
            MOCK_RATE_LIMITER_CID,
            LRU_CACHE_MOCK_SNAPSHOT,
            RATE_LIMITER_MOCK_SNAPSHOT,
        )
        if cid == MOCK_LRU_CID:
            self._save_to_cache(cid, LRU_CACHE_MOCK_SNAPSHOT)
            return LRU_CACHE_MOCK_SNAPSHOT
        if cid == MOCK_RATE_LIMITER_CID:
            self._save_to_cache(cid, RATE_LIMITER_MOCK_SNAPSHOT)
            return RATE_LIMITER_MOCK_SNAPSHOT

        # 3. Try fetching from IPFS Gateway
        gateway_url = f"{self.config.lighthouse_gateway_url}{cid}"
        try:
            logger.info(f"Fetching CID from IPFS Gateway: {gateway_url}")
            resp = requests.get(gateway_url, timeout=timeout)
            if resp.status_code == 200:
                payload = resp.json()
                self._save_to_cache(cid, payload)
                return payload
        except Exception as e:
            logger.warning(f"Failed to fetch {cid} from IPFS Gateway: {e}")

        raise FileNotFoundError(f"Snapshot with CID {cid} could not be retrieved from cache or IPFS gateway.")

    def _save_to_cache(self, cid: str, payload: Dict[str, Any]) -> None:
        """Persist snapshot JSON into local cache."""
        cache_file = self.cache_dir / f"{cid}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def _read_from_cache(self, cid: str) -> Optional[Dict[str, Any]]:
        """Read snapshot JSON from local cache if present."""
        cache_file = self.cache_dir / f"{cid}.json"
        if cache_file.is_file():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Corrupt cache file for {cid}: {e}")
        return None
