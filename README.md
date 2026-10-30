# 🚀 AutoEvolve Protocol
### Decentralized, ZK-Attested Self-Improving Autonomous Agent with Immutable Cross-Agent Memory

> **CBIT Hacktoberfest '26 — Official Submission**  
> **Track**: Agentic AI, Zero-Knowledge Cryptography & Decentralized Infrastructure  
> **Team**: VignanaSarathi (`TEAM-31`) &bull; Registration ID: `HFEST26-DVML5WNY`

---

## 👥 Team Information

| Role | Name | Email | Institution |
| :--- | :--- | :--- | :--- |
| **Team Leader** | SARIPILLY RAKESH | rakeshsaripilly@gmail.com | CBIT |
| **Team Member** | SARIPILLY LOKESH | lokeshsaripilly@gmail.com | CBIT |
| **Team Member** | TEKULA NAVDEEP | navdeeptekula07@gmail.com | CBIT |
| **Team Member** | DONTHULA VEDANTH | vedanth1024@gmail.com | CBIT |

---

## 📌 Architecture Overview

Current self-improving AI agents operate inside isolated, opaque environments with no cryptographic guarantees that improvements were not hallucinated or achieved by weakening test suites. Hard-won failure insights are discarded rather than shared across the agent ecosystem.

**AutoEvolve Protocol** solves this by combining:
1. Dynamic Task Processing & Independent Oracle Test Validation.
2. Adversarial Generator-Critic-Evaluator Self-Improvement Loops.
3. Zero-Knowledge Arithmetic Circuits (Circom + Groth16 on BN254) proving non-falsifiable score improvement.
4. Decentralized DataDAO & Cross-Agent Semantic Memory (sentence-transformers `all-MiniLM-L6-v2` + IPFS / Base Sepolia).
5. AutoEvolve Control Room: An interactive, real-time developer workspace and observability dashboard.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       AUTOEVOLVE PROTOCOL ARCHITECTURE                                │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘

  [ TASK WORKSPACE & INDEPENDENT TEST GENERATION ]
  Task Specification (LRU Cache / API Rate Limiter / Custom Task)
        │
        ▼
  Test Generator Agent ──> Categories: Basic | Boundary | Edge | Invalid Input | Perf | Regression
        │
        ▼
  Independent Test Validator ──> Reference Oracle / Invariant Attestation (Rejects defective tests)

  [ ADVERSARIAL GENERATOR-CRITIC-EVALUATOR ENGINE ]
  Validated Tests ──> Generator (Qwen 2.5 Coder) ──> Subprocess Sandbox
                            ▲                              │ Eval Trace (Passed, Failed, Sub-scores)
                            │                              ▼
                       Constitutional Critic <─── DeepSeek-R1 (Strictly No Code Leakage)
                            │
                            └──> [V1] ──> [V2] ──> [V3] ──> execution_trace.json
                                                                    │
                                                                    ▼
  [ ZERO-KNOWLEDGE PROVING PIPELINE (Circom 2.1 + Groth16 BN254) ]
  Circom Circuit ──> R1CS Constraints ──> Powers-of-Tau BN254 ──> ZKey + VKey
        ├── Proof 1: Score(V2) > Score(V1) [Public signals: diff, 1, H1, H2]
        ├── Proof 2: Score(V3) > Score(V2) [Public signals: diff, 1, H2, H3]
        └── Chained Trace Continuity: Step1.EndHash == Step2.StartHash

  [ DECENTRALIZED DATADAO & CROSS-AGENT SEMANTIC MEMORY ]
  Verified Snapshot ──> Dense Embedding (all-MiniLM-L6-v2, 384-d) ──> IPFS / Filecoin Pinning
        │
        ▼
  Base Sepolia Registry Contract / Local DataDAO Ledger
        │
        ▼
  Agent 2 Encountering Failure ──> Cosine Similarity (>= 80% Cutoff) ──> Verified Fix Hydration
        └──> First-Attempt Score Jump: 52.0 ──> 100.0 (Failure Loops Bypassed!)

  [ AUTOEVOLVE CONTROL ROOM (Next.js 14 App Router + Tailwind CSS) ]
  ├── Task Console: Benchmark Selection (LRU Cache, API Rate Limiter, Custom Task)
  ├── Agent Workflow Pipeline: Real-time animated state DAG (Waiting, Running, Completed)
  ├── Evolution History: Interactive version milestones, code viewer, and cryptographic commitments
  ├── Code Comparison: Side-by-side & unified syntax diff viewer with automated changelogs
  ├── Test Generation & Runner: Categorized test execution logs & oracle validation diagnostics
  ├── Critic Analysis: Root-cause reflection, severity classification, and revision directives
  ├── Evolution Analytics: Verified trajectory, pass rates, and failure elimination metrics
  ├── Verification Status: Groth16 zk-SNARK public signals, curve points, and verifier contracts
  └── Agent Network: Cross-agent memory query, cosine similarity gauge, and score jump visualizer
```

---

## 🧩 Four Core Modules

### 1. Module 1: Dynamic Task Processing & Adversarial Improvement Loop
- **Generic Task Abstraction**: Supports arbitrary programming tasks defined by signature, description, functional requirements, and constraints.
  - **Benchmark 1**: Least Recently Used (LRU) Cache — O(1) throughput, capacity boundary guards, and defensive handling of unhashable types.
  - **Benchmark 2**: API Rate Limiter — Rolling 60-second window, maximum 5 requests per user, boundary-burst elimination, and input sanitization.
  - **Custom Programming Tasks**: Interactive task submission through the Control Room console.
- **Dynamic Test Generation & Independent Oracle Validation**: Dedicated `TestGeneratorAgent` derives categorized tests across 6 classes (Basic, Boundary, Edge, Invalid Input, Performance, Regression). The `TestValidator` verifies tests against reference oracles (`LRUCacheOracle`, `RateLimiterOracle`), rejecting defective or ambiguous tests before admitting them into the trusted test suite.
- **Sandboxed Subprocess Execution**: Evaluates candidate solutions in isolated temporary directories with strict per-test timeouts (3-4 seconds), capturing stdout, stderr, execution time, and sub-scores (Correctness, Efficiency, Safety, Quality).
- **Constitutional Critic**: DeepSeek-R1 reflects on failure traces in natural language, classifying issues by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) while strictly enforcing no-code-leakage guardrails.
- **248-Bit Scalar Field Commitments**: Trace hashes are truncated to 62 hexadecimal characters (248 bits), ensuring mathematical safety against BN254 elliptic curve modulus overflow ($r \approx 2^{253.7}$).

### 2. Module 2: Zero-Knowledge Improvement Attestation
- **Circom Arithmetic Circuits**: `circuits/improvement.circom` enforces:
  $$\text{diff} = s_2 - s_1$$
  $$s_2 > s_1 \implies \text{GreaterThan}(32).\text{out} == 1$$
- **Non-Falsifiable Constraint**: If scores stagnate or regress, witness calculation fails with `Assert Failed`.
- **Chained Trace Continuity**: Public signals bind $[ \Delta s, 1, H_{\text{start}}, H_{\text{end}} ]$. The smart contract verifies that the ending hash of Step 1 matches the starting hash of Step 2, preventing proof splicing or replay attacks.
- **Solidity Verifier Contract**: Exports `contracts/Verifier.sol` combining the Groth16 pairings verifier with the on-chain escrow engine.

### 3. Module 3: Decentralized DataDAO & Cross-Agent Semantic Memory
- **Dense Vector Embeddings**: Ingests failure signatures, root causes, and fix strategies through `sentence-transformers` (`all-MiniLM-L6-v2`) to produce 384-dimensional normalized float vectors.
- **IPFS / Filecoin Persistence**: Pins full agent snapshots via Lighthouse Storage with local DataDAO ledger fallback.
- **Cross-Agent Lifelong Inheritance**: When Agent 2 encounters a runtime error, it queries the memory registry. Upon finding a cosine similarity match ($\ge 80\%$), it injects the verified code diff, achieving an instant $100\%$ score on Attempt V1.

### 4. Module 4: AutoEvolve Control Room (Interactive Dashboard)
- **Next.js 14 App Router + Tailwind CSS + Lucide React**: Dark technical control room (`#07090e`), responsive layout, cyan, violet, and emerald accents.
- **Simulation Controls**: Start Evolution, Pause, Resume, Step-by-Step execution, Run Again, and Reset.
- **Execution Modes**:
  - **Live Mode**: Queries open-weight LLMs via Featherless API with genuine model output.
  - **Deterministic Offline Mock Mode**: Deterministic calibrated progression for offline demonstrations.
  - **Replay Mode**: Replays previously saved execution traces step-by-step.

---

## 📁 Repository Directory Structure

```
HFT26-TEAM-31/
├── README.md                          # System specification & technical documentation
├── problem_statement.md               # Official hackathon problem track requirements
├── setup.md                           # Environment setup and tooling guide
├── pipeline.py                        # Unified end-to-end integration orchestrator
├── dashboard_runtime.json             # Live runtime execution telemetry consumed by Dashboard
├── execution_trace.json               # Output artifact from multi-stage agent loop
├── .env.example                       # Environment variable configuration template
│
├── module1/                           # Module 1: Adversarial Iterative Engine & Sandbox
│   ├── README.md                      # Detailed technical guide for Module 1
│   ├── execution_trace.json           # Module 1 output artifact
│   └── agent/
│       ├── task.py                    # Generic TaskSpecification, benchmarks & oracles
│       ├── test_generator.py          # Dynamic Test Generator & Independent Validator
│       ├── evaluator.py               # Subprocess test sandbox, scoring & 248-bit ZK hashes
│       ├── generator.py               # Dynamic code generator & calibrated progression mocks
│       ├── critic.py                  # Constitutional critic & severity classification
│       ├── loop.py                    # Dynamic orchestration pipeline & event callbacks
│       ├── simulation_manager.py      # Stateful simulation runner & step execution engine
│       └── mocks/
│           ├── v1_failing.py          # LRU baseline mock (Score: 52.0)
│           ├── v2_fixed.py            # LRU revision mock (Score: 86.0)
│           ├── v3_perfect.py          # LRU production mock (Score: 100.0)
│           ├── v1_failing_rl.py       # Rate Limiter fixed-window baseline mock
│           ├── v2_fixed_rl.py         # Rate Limiter sliding window boundary flaw mock
│           └── v3_perfect_rl.py       # Rate Limiter production deque mock (Score: 100.0)
│
├── module2/                           # Module 2: Zero-Knowledge Proving Pipeline (Circom + Groth16)
│   ├── package.json                   # snarkjs & circomlib dependencies
│   ├── circuits/
│   │   ├── improvement.circom         # Circom arithmetic score comparator & trace binder
│   │   └── safety.circom              # Safety constraint circuit
│   ├── build/
│   │   ├── improvement.r1cs           # Compiled R1CS constraint matrix
│   │   ├── improvement.zkey           # Groth16 circuit proving key
│   │   ├── verification_key.json      # Groth16 verification key
│   │   ├── proof_v1_v2.json           # Real Groth16 proof for V1 -> V2
│   │   └── execution_trace_with_proofs.json # Enriched execution trace with ZK proofs
│   └── contracts/
│       └── Verifier.sol               # Groth16 Solidity Verifier & Escrow suite
│
├── module3/                           # Module 3: Decentralized DataDAO & Cross-Agent Memory
│   ├── requirements.txt               # Python dependencies (sentence-transformers, web3, etc.)
│   ├── memory_engine.py               # 384-d dense vector encoder & cosine similarity engine
│   ├── storage_uploader.py             # Lighthouse IPFS/Filecoin uploader & cache layer
│   ├── contract_interface.py           # Base Sepolia Web3 client & Local DataDAO fallback
│   ├── memory_service.py              # Unified cross-agent memory orchestrator
│   ├── test_standalone.py             # End-to-end memory store & retrieval verification CLI
│   └── test_multi_scenarios.py        # 5-domain precision & negative discrimination test suite
│
├── frontend/                          # Module 4: AutoEvolve Control Room (Next.js Dashboard)
│   ├── package.json                   # Next.js 14, React 18, Tailwind CSS, Lucide React
│   ├── app/
│   │   ├── page.tsx                   # Main entrypoint
│   │   └── api/
│   │       ├── run-agent/route.ts     # Telemetry & execution runner endpoint
│   │       ├── tasks/route.ts         # Task listing & custom task submission endpoint
│   │       └── agent2-inherit/route.ts# Agent 2 memory inheritance endpoint
│   └── components/
│       ├── Dashboard.tsx              # Control Room main dashboard & navigation
│       ├── TaskConsole.tsx            # Task Workspace, custom submission & simulation controls
│       ├── WorkflowDAG.tsx            # Real-time backend-driven agent workflow pipeline
│       ├── ExecutionTree.tsx          # Evolution history, milestone nodes & code viewer
│       ├── DiffViewer.tsx             # Side-by-side & unified syntax diff viewer
│       ├── TestExecutionPanel.tsx     # Categorized test execution logs & oracle validation
│       ├── CriticIntelligencePanel.tsx# Structured diagnostic reflections & severity ratings
│       ├── EvolutionAnalytics.tsx     # Score trajectories, pass rates & defect elimination
│       ├── ZkTelemetryPanel.tsx       # Groth16 verification status & contract telemetry
│       └── Agent2MemoryTab.tsx        # Cross-agent memory retrieval & score jump visualizer
│
└── tests/
    └── test_dynamic_engine.py         # 17-test verification suite covering all dynamic modules
```

---

## 🛠️ Installation & Setup Instructions

### Prerequisites
- **Python**: Version `3.10` or higher (tested on `3.13`)
- **Node.js**: Version `18.0.0` or higher
- **npm**: Version `9.0.0` or higher

```bash
# Clone the repository
git clone https://github.com/RakeshSaripilly/HFT26-TEAM-31.git
cd HFT26-TEAM-31

# Setup environment configuration
cp .env.example .env

# Install Python dependencies
pip install -r module3/requirements.txt

# Install Module 2 dependencies
cd module2 && npm install && cd ..

# Install Frontend dependencies
cd frontend && npm install && cd ..
```

---

## 🚀 Execution & Verification Guides

### 1. Run Dynamic Engine Automated Tests (17/17 Passed)
Verify task processing, dynamic test generation, oracle validation, sandbox evaluation, and improvement loops:
```bash
python -m unittest tests/test_dynamic_engine.py
```

### 2. Execute Benchmark 1: Least Recently Used (LRU) Cache
```bash
python pipeline.py --run-agent --task lru_cache_01
```

### 3. Execute Benchmark 2: API Rate Limiter (Rolling 60s Window)
```bash
python pipeline.py --run-agent --task rate_limiter_02
```

### 4. Verify Agent 2 Cross-Agent Memory Inheritance
```bash
python pipeline.py --agent2-inherit
```

### 5. Launch AutoEvolve Control Room
```bash
cd frontend
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 🔒 Security Invariants & Cryptographic Guarantees

| Invariant | Guarantee | Architectural Enforcement |
| :--- | :--- | :--- |
| **Non-Falsifiable Improvement** | Agents cannot claim unverified performance gains. | Circom circuit enforces `GreaterThan(32).out === 1`. Witness generation throws `Assert Failed` if scores regress or stay flat. |
| **Trace Continuity Binding** | Proof splicing and replay attacks are prevented. | Public inputs link $H_{2\text{ end}}$ of Step 1 identically to $H_{2\text{ start}}$ of Step 2. Contract rejects discontinuous hashes. |
| **BN254 Scalar Field Safety** | Circuit input signals will never overflow scalar modulus. | State hashes are truncated to 62 hex characters ($248\text{ bits}$), strictly below the curve order $r \approx 2^{253.7}$. |
| **Constitutional Guardrails** | Critic models cannot leak implementation code. | Every critique string is parsed against forbidden code tokens (`def `, `class `, code fences). Violations trigger immediate retry. |
| **Independent Oracle Validation** | Generated unit tests cannot contain invalid expectations. | TestValidator evaluates candidate tests against reference oracles (`LRUCacheOracle`, `RateLimiterOracle`) before admitting them. |
| **Semantic Precision Cutoff** | Irrelevant queries cannot contaminate agent context. | Memory search enforces a strict $\ge 80\%$ cosine similarity threshold ($0.80$), preventing irrelevant memory contamination. |

---

## 📜 License
MIT License &bull; AutoEvolve Protocol &bull; Team VignanaSarathi (CBIT Hacktoberfest '26).
