# AutoEvolve Protocol — Module 2 Setup & Antigravity Agent Directive

This document serves as both a **human-readable guide** and an **autonomous agent prompt**. If you are using **Google Antigravity**, you can provide this file directly to the agent (or paste the prompt below), and Antigravity will configure your entire environment and run Module 2 automatically.

---

## 🤖 For Antigravity Agents (Copy-Paste Directive)

If a teammate pastes this prompt to Antigravity:

```markdown
ROLE: Environment & ZK Setup Engineer for AutoEvolve Protocol (Module 2).
TASK: Configure this system to execute Module 2 (Circom 2.1.x + snarkjs + Groth16 ZK proving pipeline).

EXECUTION DIRECTIVES:
1. Detect Operating System (Windows, macOS, or Linux).
2. Check for Node.js (v18+) and npm. If missing or path inaccessible in sandbox, locate system node or use `.tools/node.exe`.
3. Check for Circom compiler (v2.1.x). If `circom --version` is not recognized, automatically create `.tools/` in repo root and download the appropriate pre-compiled binary:
   - Windows: https://github.com/iden3/circom/releases/download/v2.1.9/circom-windows-amd64.exe -> .tools/circom.exe
   - Linux: https://github.com/iden3/circom/releases/download/v2.1.9/circom-linux-amd64 -> .tools/circom (chmod +x)
   - macOS: https://github.com/iden3/circom/releases/download/v2.1.9/circom-macos-amd64 -> .tools/circom (chmod +x)
4. Setup Python Virtual Environment in repository root:
   - Create `.venv` using python 3.10+
5. Install Module 2 Node.js dependencies:
   - Run `npm install` inside `module2/` (installs `circomlib` and `snarkjs`).
6. Verify Input Trace:
   - Check if `agent/execution_trace.json` exists. If missing, fail gracefully and notify the user to run Module 1 first.
7. Run the Module 2 Build Pipeline:
   - Execute `node scripts/build.js` inside `module2/`.
8. Verify all acceptance criteria:
   - `build/improvement.r1cs` exists
   - `build/improvement.zkey` and `build/verification_key.json` exist
   - `build/witness_v1_v2.wtns` and `build/witness_v2_v3.wtns` exist
   - `build/proof_v1_v2.json` and `build/proof_v2_v3.json` exist
   - `snarkjs groth16 verify` returns OK
   - `contracts/Verifier.sol` exists (>500 lines)
   - `build/execution_trace_with_proofs.json` contains real ZK proofs linked to trace hashes
```

---

## 📋 Human Operator Guide (Manual Setup)

If you prefer to configure your environment manually without an AI assistant:

### 1. Prerequisites
* **Node.js**: `v18.0.0` or higher
* **npm**: `v9.0.0` or higher
* **Python**: `3.10` or higher
* **Circom Compiler**: `v2.1.x`

---

### 2. Environment Setup Commands

#### A. Install Circom Binary into `.tools/`

* **Windows (PowerShell)**:
  ```powershell
  New-Item -ItemType Directory -Force -Path ".tools"
  curl.exe -L -o ".tools\circom.exe" "https://github.com/iden3/circom/releases/download/v2.1.9/circom-windows-amd64.exe"
  $env:PATH = "$((Get-Item .tools).FullName);" + $env:PATH
  ```

* **Linux (bash)**:
  ```bash
  mkdir -p .tools
  curl -L -o .tools/circom https://github.com/iden3/circom/releases/download/v2.1.9/circom-linux-amd64
  chmod +x .tools/circom
  export PATH="$(pwd)/.tools:$PATH"
  ```

* **macOS (bash / zsh)**:
  ```bash
  mkdir -p .tools
  curl -L -o .tools/circom https://github.com/iden3/circom/releases/download/v2.1.9/circom-macos-amd64
  chmod +x .tools/circom
  export PATH="$(pwd)/.tools:$PATH"
  ```

Verify:
```bash
circom --version
# Expected: circom compiler 2.1.9
```

---

#### B. Setup Python Virtual Environment
* **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
* **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

---

#### C. Install Node Dependencies
```bash
cd module2
npm install
```

---

### 3. Execution & Verification

Run the full end-to-end ZK build pipeline:
```bash
cd module2
npm run build
# Or: node scripts/build.js
```

Or run standalone proof generation:
```bash
npm run prove
# Or: node scripts/prove.js
```

---

### 4. Expected Deliverables Checklist

After running `npm run build`, confirm the following files exist in `module2/`:

| File | Description |
| :--- | :--- |
| `build/improvement.r1cs` | Compiled R1CS constraint system |
| `build/improvement.zkey` | Groth16 circuit-specific proving key |
| `build/verification_key.json` | Verification key exported by snarkjs |
| `build/witness_v1_v2.wtns` | Generated witness for $V_1 \rightarrow V_2$ |
| `build/witness_v2_v3.wtns` | Generated witness for $V_2 \rightarrow V_3$ |
| `build/proof_v1_v2.json` | Real Groth16 proof (pi_a, pi_b, pi_c) for $V_1 \rightarrow V_2$ |
| `build/public_v1_v2.json` | Public inputs: `[diff, valid, log_hash_v1, log_hash_v2]` |
| `build/proof_v2_v3.json` | Real Groth16 proof for $V_2 \rightarrow V_3$ |
| `build/public_v2_v3.json` | Public inputs: `[diff, valid, log_hash_v2, log_hash_v3]` |
| `build/execution_trace_with_proofs.json` | Enriched execution trace with verified cryptographic proofs |
| `contracts/Verifier.sol` | Solidity Groth16 Verifier + AutoEvolve Escrow suite (>500 lines) |

---

### 5. Troubleshooting & Protocol Invariants

* **Missing Trace (`execution_trace.json is missing`)**:
  Module 2 requires deterministic outputs from Module 1 at `agent/execution_trace.json`. If missing, run the Module 1 agent evaluator first.
* **Non-Improving Score Assertion (`Assert Failed in template Improvement`)**:
  By protocol design, score improvements must satisfy $s_2 > s_1$. If scores stagnate or regress, the circuit comparator fails witness calculation: *"No improvement, no proof, no reward"*.
* **Solidity Verifier Contract Requirements**:
  `contracts/Verifier.sol` contains the genuine `Groth16Verifier` along with the AutoEvolve Protocol settlement contract (`AutoEvolveImprovementVerifier`) to verify chained proofs and bind trace hashes on-chain.
