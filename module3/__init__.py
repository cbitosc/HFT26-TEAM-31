"""Module 3: Decentralized Skill Library & Semantic Memory.

The collective memory layer of the AutoEvolve Protocol (Voyager / MemGPT-style memory registry).
"""

from __future__ import annotations

from .config import Config, get_config
from .contract_interface import ContractInterface
from .memory_engine import MemoryEngine
from .memory_service import MemoryService
from .storage_uploader import StorageUploader
from .test_fixtures import (
    LRU_CACHE_MOCK_SNAPSHOT,
    get_all_domain_fixtures,
    get_lru_cache_fixture,
    get_mock_registry_records,
)

__all__ = [
    "Config",
    "get_config",
    "MemoryEngine",
    "StorageUploader",
    "ContractInterface",
    "MemoryService",
    "get_all_domain_fixtures",
    "get_lru_cache_fixture",
    "get_mock_registry_records",
    "LRU_CACHE_MOCK_SNAPSHOT",
]

