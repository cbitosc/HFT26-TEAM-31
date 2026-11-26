# Module 3: Decentralized Skill Library & Semantic Memory

The collective semantic memory layer of the **AutoEvolve Protocol** (Voyager / MemGPT-style cross-agent memory).

Module 3 enables autonomous agents to persist post-mortem failure critiques, root causes, and verified code diffs into a decentralized skill library (IPFS/Filecoin via Lighthouse), register cryptographic commitments and CIDs on Base Sepolia, and inherit solutions across execution loops using dense vector semantic search ($\ge 80\%$ similarity cutoff).

---

## Architecture Overview

```
Agent 1 (Success) ──> Dense Embedding (all-MiniLM-L6-v2) ──> IPFS Pinning (Lighthouse) ──> Registry Ledger (Base Sepolia / DataDAO)
                                                                                                    │
Agent 2 (Failing) ──> Semantic Query Match (>= 80% Cosine Similarity) <─────────────────────────────┘
          │
          └──> Inherited Memory Prompt Injection (Verified Code Diff + Strategy)
```

1. **Vector Engine** (`memory_engine.py`):
   - Uses HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`) to generate 384-dimensional dense semantic vectors.
   - Computes fast cosine similarity using normalized dot products.
2. **Decentralized Storage** (`storage_uploader.py`):
   - Pins complete agent execution snapshots (task ID, failure signature, root cause, fix strategy, unified diff, trace hashes, embedding) to IPFS/Filecoin via Lighthouse.
   - Transparent local cache layer (`.cache/`) ensures sub-millisecond retrieval and offline tolerance.
3. **EVM Contract Interface** (`contract_interface.py`):
   - Interfaces with `AutoEvolveRegistry.sol` on Base Sepolia (`https://base-sepolia-rpc.publicnode.com`).
   - Automatically activates a zero-gas, persistent **Local DataDAO backup ledger** (`.cache/registry_records.json`) if the contract is un-deployed or RPC is offline.
4. **Unified Memory Service** (`memory_service.py`):
   - High-level orchestration for storing runs (`store_agent_run`), querying inherited memory (`retrieve_inherited_memory`), and formatting structured prompt injections (`format_agent_prompt`).

---

## Directory Layout

```
module3/
├── AutoEvolveRegistry.json     # ABI definition for registry contract
├── __init__.py                 # Clean public API exports
├── config.py                   # Environment configuration & fallbacks
├── contract_interface.py       # Base Sepolia Web3 & Local DataDAO ledger
├── memory_engine.py            # 384-d SentenceTransformer vector engine
├── memory_service.py           # Unified cross-agent memory orchestrator
├── storage_uploader.py         # Lighthouse IPFS uploader & gateway retriever
├── test_fixtures.py            # Canonical datasets across diverse domains
├── test_multi_scenarios.py     # 5-domain precision & negative discrimination suite
├── test_standalone.py          # End-to-end dry run verification CLI
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variable template
├── .gitignore                  # Git exclusions (.env, .cache, __pycache__, venv)
└── README.md                   # Documentation
```

---

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r module3/requirements.txt
   ```

2. **Configure Environment (`.env`)**:
   Copy `.env.example` to `.env` inside `module3/` (or repository root):
   ```bash
   cp module3/.env.example module3/.env
   ```
   Add your Lighthouse API key from [Lighthouse Storage](https://files.lighthouse.storage):
   ```env
   LIGHTHOUSE_API_KEY=your_lighthouse_api_key_here
   BASE_SEPOLIA_RPC_URL=https://base-sepolia-rpc.publicnode.com
   # REGISTRY_CONTRACT_ADDRESS=0x... (optional)
   ```

---

## Running Verification

### 1. Canonical End-to-End Test (LRU Cache)
Runs the full memory store, IPFS upload, Base Sepolia connectivity check, Agent 2 query, $\ge 80\%$ similarity evaluation, and prompt injection:
```bash
python module3/test_standalone.py
```

### 2. Multi-Scenario & Negative Discrimination Suite
Validates precision across 5 distinct engineering domains (concurrency, security/JWT, database connection pooling, algorithms, and data structures) and verifies strict rejection of unrelated queries (CSS, Kubernetes, Docker):
```bash
python module3/test_multi_scenarios.py
```

### 3. Run All via Pytest
```bash
pytest module3/test_standalone.py module3/test_multi_scenarios.py -v
```

---

## Security & Privacy Notice
* Secrets in `.env` are strictly excluded via `.gitignore`.
* Sensitive local cache files (`.cache/`) and virtual environments (`venv/`, `.venv/`) are ignored and never committed.

