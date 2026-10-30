"""Configuration module for Module 3: Decentralized Skill Library & Semantic Memory.

Handles environment variable loading from .env, prioritizing Base Sepolia RPC
with automatic Local DataDAO fallback when the contract is un-deployed or RPC fails.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Base paths
MODULE_DIR = Path(__file__).resolve().parent
ENV_PATH = MODULE_DIR / ".env"
CACHE_DIR = MODULE_DIR / ".cache"

# Ensure local cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from root .env and module3/.env
ROOT_ENV_PATH = MODULE_DIR.parent / ".env"
if ROOT_ENV_PATH.is_file():
    load_dotenv(dotenv_path=ROOT_ENV_PATH, override=True)
if ENV_PATH.is_file():
    load_dotenv(dotenv_path=ENV_PATH, override=True)


@dataclass(frozen=True)
class Config:
    """Immutable application configuration dataclass."""

    # Lighthouse IPFS Configuration
    lighthouse_api_key: str
    lighthouse_gateway_url: str

    # Blockchain / EVM Configuration (Base Sepolia with Local DataDAO Fallback)
    evm_rpc_url: str
    registry_contract_address: Optional[str]
    use_onchain_registry: bool

    # Semantic Memory & Embedding Configuration
    embedding_model_name: str
    similarity_threshold: float

    # Local Storage & Caching
    cache_dir: Path

    @property
    def base_sepolia_rpc_url(self) -> str:
        """Base Sepolia RPC endpoint."""
        return self.evm_rpc_url

    @property
    def is_contract_configured(self) -> bool:
        """Check whether on-chain contract retrieval should be attempted."""
        return bool(
            self.registry_contract_address
            and self.registry_contract_address.strip()
            and self.registry_contract_address.strip() != "0x0000000000000000000000000000000000000000"
            and self.evm_rpc_url
        )

    @property
    def is_lighthouse_configured(self) -> bool:
        """Check whether a valid Lighthouse API key is configured."""
        return bool(
            self.lighthouse_api_key
            and self.lighthouse_api_key.strip()
            and not self.lighthouse_api_key.strip().startswith("mock_")
        )


def get_config() -> Config:
    """Retrieve and construct the application configuration from environment variables.

    Reads BASE_SEPOLIA_RPC_URL and LIGHTHOUSE_API_KEY from .env.
    Keeps Local DataDAO mode as resilient backup if RPC fails or contract is un-deployed.
    """
    api_key = os.getenv("LIGHTHOUSE_API_KEY", "").strip()
    contract_addr = os.getenv("REGISTRY_CONTRACT_ADDRESS", "").strip() or None

    # Prioritize BASE_SEPOLIA_RPC_URL from .env
    rpc_url = (
        os.getenv("BASE_SEPOLIA_RPC_URL", "").strip()
        or os.getenv("EVM_RPC_URL", "").strip()
        or os.getenv("RPC_URL", "").strip()
        or "https://base-sepolia-rpc.publicnode.com"
    )

    onchain_flag = os.getenv("USE_ONCHAIN_REGISTRY", "").strip().lower()
    if onchain_flag in ("1", "true", "yes"):
        use_onchain = True
    elif onchain_flag in ("0", "false", "no"):
        use_onchain = False
    else:
        # Default to True if contract address is present, else False (Local DataDAO backup)
        use_onchain = bool(contract_addr)

    gateway_url = os.getenv(
        "LIGHTHOUSE_GATEWAY_URL",
        "https://gateway.lighthouse.storage/ipfs/",
    ).strip()
    if not gateway_url.endswith("/"):
        gateway_url += "/"

    model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2").strip()

    try:
        threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.80"))
    except ValueError:
        threshold = 0.80

    return Config(
        lighthouse_api_key=api_key,
        lighthouse_gateway_url=gateway_url,
        evm_rpc_url=rpc_url,
        registry_contract_address=contract_addr,
        use_onchain_registry=use_onchain,
        embedding_model_name=model_name,
        similarity_threshold=threshold,
        cache_dir=CACHE_DIR,
    )
