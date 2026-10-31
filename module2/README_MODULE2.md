# AutoEvolve Protocol — Module 2: Zero-Knowledge Improvement Attestation

## 1. Executive Summary & Objective

**AutoEvolve Protocol Module 2** provides cryptographic guarantees that an autonomous self-improving agent truly achieved measurable performance gains during its Generate $\rightarrow$ Critique $\rightarrow$ Revise cycle ($V_1 \rightarrow V_2 \rightarrow V_3$), without leaking sensitive reasoning prompts or proprietary code implementations.

By leveraging **Circom 2.1.x**, **snarkjs**, and **Groth16 zk-SNARKs** on the BN254 (alt_bn128) elliptic curve, Module 2 binds arithmetic proof verification directly to deterministic execution trace hashes.

---

## 2. Pipeline Position & End-to-End Workflow

Module 2 operates as a self-contained, trustless proving engine situated between Module 1 (evaluation) and Module 3/4 (storage and on-chain settlement):

```
+-------------------------------------------------------------+
| MODULE 1: Deterministic Agent Execution & Scoring           |
| (LRU Cache benchmark: 10 test vectors, yields execution_trace)|
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| MODULE 2: Zero-Knowledge Proving Pipeline (THIS MODULE)     |
| 1. Discovers & ingests agent/execution_trace.json           |
| 2. Extracts zk_inputs (scores & 248-bit BN254 field hashes) |
| 3. Writes inputs/input_v1_v2.json & input_v2_v3.json        |
| 4. Compiles circuits/improvement.circom (R1CS, WASM, SYM)   |
| 5. Executes Groth16 Trusted Setup (PTAU -> ZKEY -> VKEY)    |
| 6. Generates witnesses & proofs for V1->V2 and V2->V3       |
| 7. Cryptographically verifies proofs via snarkjs (OK!)      |
| 8. Exports on-chain Verifier.sol (>500 lines)               |
| 9. Enriches trace -> build/execution_trace_with_proofs.json |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| MODULE 3: Decentralized Memory Registry (DataDAO / IPFS)    |
| (Publishes enriched trace + proof JSON to IPFS/Filecoin)    |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| MODULE 4: Smart Contract Verification & Reward Escrow       |
| (On-chain Verifier checks proof & releases micro-rewards)   |
+-------------------------------------------------------------+
```

---

## 3. Current 12-Step Build Workflow (`scripts/build.js`)

When executing `node scripts/build.js`, Module 2 performs a 12-step real shell execution pipeline:

```
[execution_trace.json] 
        │
        ▼ (Step 1-2: Validate & Parse zk_inputs)
[input_v1_v2.json]  ───┐
[input_v2_v3.json]  ───┤
                       ▼ (Step 3-5: Circom 2.1.x Compilation)
              [improvement.r1cs] + [improvement.wasm]
                       │
                       ▼ (Step 6: Phase 2 Powers of Tau Setup)
              [improvement.zkey] + [verification_key.json]
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
(Step 7-9: V1 -> V2)          (Step 10: V2 -> V3)
[witness_v1_v2.wtns]          [witness_v2_v3.wtns]
        │                             │
[proof_v1_v2.json]            [proof_v2_v3.json]
[public_v1_v2.json]           [public_v2_v3.json]
        │                             │
snarkjs verify (OK!)          snarkjs verify (OK!)
        └──────────────┬──────────────┘
                       │
                       ▼ (Step 11: Solidity Verifier Export)
              [contracts/Verifier.sol] (512 lines)
                       │
                       ▼ (Step 12: Trace Enrichment)
    [build/execution_trace_with_proofs.json]
```

### Detailed Execution Steps:
1. **Trace Discovery & Validation**:
   Checks for the existence of `execution_trace.json` across known candidate paths (`agent/execution_trace.json` or root `execution_trace.json`). If absent, it immediately halts with exit code 1 to enforce real execution provenance.
2. **Extraction of `zk_inputs`**:
   Reads deterministic scores (`score_v1`, `score_v2`, `score_v3`) and scalar field execution log hashes (`log_hash_v1`, `log_hash_v2`, `log_hash_v3`).
3. **Generate V1 $\rightarrow$ V2 Input Payload**:
   Writes `inputs/input_v1_v2.json` with `{ s1, s2, log_hash_v1, log_hash_v2 }`.
4. **Generate V2 $\rightarrow$ V3 Input Payload**:
   Writes `inputs/input_v2_v3.json` mapping `{ s1: score_v2, s2: score_v3, log_hash_v1: log_hash_v2, log_hash_v2: log_hash_v3 }` for generic circuit compatibility.
5. **Circuit Compilation**:
   Runs Circom 2.1.x (`circom circuits/improvement.circom -l node_modules -l circuits --r1cs --wasm --sym -o build/`), yielding R1CS constraint matrix and WASM runtime.
6. **Groth16 Setup**:
   Loads or generates `powersOfTau28_hez_final_12.ptau`, executes `snarkjs groth16 setup`, and exports `build/verification_key.json`.
7. **Witness Calculation (V1 $\rightarrow$ V2)**:
   Computes witness using `build/improvement_js/generate_witness.js`. If scores regress or stay flat, Circom's `gt.out === 1` constraint fails here.
8. **Groth16 Prove (V1 $\rightarrow$ V2)**:
   Generates cryptographic proof `build/proof_v1_v2.json` and public signals `build/public_v1_v2.json`.
9. **Local Verification (V1 $\rightarrow$ V2)**:
   Validates proof against `verification_key.json` via snarkjs, asserting `[INFO] snarkJS: OK!`.
10. **Chained Proving (V2 $\rightarrow$ V3)**:
    Repeats witness calculation, Groth16 proving, and verification for the second evolution step ($V_2 \rightarrow V_3$).
11. **On-Chain Verifier Export**:
    Exports the EVM verifier via `snarkjs zkey export solidityverifier` and appends the `AutoEvolveImprovementVerifier` settlement contract to produce a production-grade 512-line contract at `contracts/Verifier.sol`.
12. **Trace Enrichment**:
    Combines the original execution trace with the real cryptographic proofs into `build/execution_trace_with_proofs.json`.

---

## 4. Cryptographic Circuit Architecture

### Public vs. Private Signals

| Signal | Type | Privacy | Description |
| :--- | :---: | :---: | :--- |
| `s1` | Input | **Private** | Score of earlier version $V_n$ ($0 \le s_1 \le 100$). Hidden inside proof. |
| `s2` | Input | **Private** | Score of refined version $V_{n+1}$ ($0 \le s_2 \le 100$). Hidden inside proof. |
| `diff` | Output | **Public** | Verified score gain ($s_2 - s_1$). Visible on-chain to determine rewards. |
| `valid` | Output | **Public** | Comparator boolean flag ($1$). Must be 1 for contract acceptance. |
| `log_hash_v1` | Input | **Public** | 248-bit scalar field commitment to starting execution trace. |
| `log_hash_v2` | Input | **Public** | 248-bit scalar field commitment to ending execution trace. |

### How It Prevents Fake Diffs & Hallucinations

1. **Arithmetic Constraint Enforcement**:
   $$\text{diff} \longleftarrow s_2 - s_1$$
   $$s_2 > s_1 \implies \text{GreaterThan}(32).\text{out} === 1$$
   $$\text{valid} \longleftarrow \text{gt.out}$$

2. **Strict Non-Falsifiability**:
   If an agent hallucinates a higher score or regresses (e.g., $100 \rightarrow 89$):
   * The comparator evaluates to `0`.
   * The constraint `gt.out === 1` fails.
   * Snarkjs witness generation crashes with `Assert Failed`.
   * **Rule Enforced**: *"No improvement, no proof, no reward."*

3. **Chained Trace Binding**:
   * For $V_1 \rightarrow V_2$: Public inputs include `log_hash_v1` and `log_hash_v2`.
   * For $V_2 \rightarrow V_3$: Public inputs include `log_hash_v2` and `log_hash_v3`.
   * `AutoEvolveImprovementVerifier.sol` checks on-chain that the ending hash of Step 1 identically matches the starting hash of Step 2, preventing proof substitution or replay attacks.

---

## 5. Grounding to the LRU Cache Benchmark

The scores ingested by Module 2 come from 10 deterministic test vectors in Module 1:
1. `test_basic`: Fundamental put/get operations.
2. `test_capacity_zero`: Immediate key discard when capacity $\le 0$.
3. `test_eviction`: Least recently used key evicted on capacity breach.
4. `test_overwrite`: Updating existing keys refreshes recency without consuming new capacity.
5. `test_order_after_get`: Accessing keys marks them most recently used.
6. `test_single_cap`: Capacity = 1 edge case.
7. `test_not_found`: Missing keys return -1.
8. `test_perf_100k`: $O(1)$ amortized complexity under load.
9. `test_unhashable`: Graceful handling of mutable/unhashable keys (lists, dicts).
10. `test_many_puts`: Stress test with sequential writes.

### Evolution Results Attested by ZK Proofs:
* **$V_1$**: 3/10 passing $\rightarrow$ Score = **52**
* **$V_2$**: 9/10 passing $\rightarrow$ Score = **86** (gain: **+34**, proven by proof 1)
* **$V_3$**: 10/10 passing $\rightarrow$ Score = **100** (gain: **+14**, proven by proof 2)

---

## 6. Directory Structure & Generated Files

```
module2/
├── circuits/
│   ├── improvement.circom   # Real Circom 2.1.0 score comparator & trace binding circuit
│   └── safety.circom        # Circuit proving banned function count === 0
├── inputs/
│   ├── input_v1_v2.json     # Extracted inputs for V1 -> V2 proving
│   └── input_v2_v3.json     # Extracted inputs for V2 -> V3 proving
├── build/                   # Compilation and cryptographic proof outputs
│   ├── improvement.r1cs     # Compiled R1CS constraint system
│   ├── improvement.sym      # Circuit symbol map
│   ├── improvement_js/      # WASM & witness generator
│   ├── improvement.zkey     # Groth16 circuit-specific proving key
│   ├── verification_key.json# Groth16 verification key
│   ├── witness_v1_v2.wtns   # Generated witness for V1 -> V2
│   ├── witness_v2_v3.wtns   # Generated witness for V2 -> V3
│   ├── proof_v1_v2.json     # Real Groth16 proof (pi_a, pi_b, pi_c) for V1 -> V2
│   ├── public_v1_v2.json    # Public inputs for V1 -> V2 [34, 1, hash1, hash2]
│   ├── proof_v2_v3.json     # Real Groth16 proof for V2 -> V3
│   ├── public_v2_v3.json    # Public inputs for V2 -> V3 [14, 1, hash2, hash3]
│   └── execution_trace_with_proofs.json # Enriched trace with real proofs
├── contracts/
│   └── Verifier.sol         # Groth16 Verifier + AutoEvolve on-chain settlement (512 lines)
├── scripts/
│   ├── build.js             # 12-step automated build and proving pipeline
│   └── prove.js             # Standalone prover script
├── package.json             # NPM dependencies (circomlib, snarkjs)
└── README_MODULE2.md        # Comprehensive technical documentation
```

---

## 7. How to Run & Verify

From the `module2/` directory:

### Run the Full Pipeline:
```bash
node scripts/build.js
# Or with bundled tools:
..\.tools\node.exe scripts/build.js
```

### Run Standalone Proof Generation:
```bash
node scripts/prove.js
# Or with bundled tools:
..\.tools\node.exe scripts/prove.js
```

### Inspect the Verified Output:
```powershell
Get-Content build/execution_trace_with_proofs.json | Select-Object -Last 45
```
