/**
 * AutoEvolve Protocol - Module 2 Prover Script
 * Generates and verifies Groth16 proofs for V1->V2 and V2->V3 improvement
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const MODULE2_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(MODULE2_ROOT, '..');

function getNodeBinary() {
    const localNode = path.join(REPO_ROOT, '.tools', 'node.exe');
    if (fs.existsSync(localNode)) {
        return `"${localNode}"`;
    }
    return 'node';
}

function getSnarkjsCli() {
    const localSnarkjs = path.join(MODULE2_ROOT, 'node_modules', 'snarkjs', 'build', 'cli.cjs');
    if (fs.existsSync(localSnarkjs)) {
        return `${getNodeBinary()} "${localSnarkjs}"`;
    }
    return 'snarkjs';
}

function runCommand(cmd, cwd = MODULE2_ROOT) {
    console.log(`[EXEC] ${cmd}`);
    return execSync(cmd, { cwd, stdio: 'inherit' });
}

async function main() {
    console.log("=== AutoEvolve Module 2: Prover ===");

    const nodeBin = getNodeBinary();
    const snarkjsCli = getSnarkjsCli();
    const buildDir = path.join(MODULE2_ROOT, 'build');
    const inputsDir = path.join(MODULE2_ROOT, 'inputs');

    const wasmPath = path.join(buildDir, 'improvement_js', 'improvement.wasm');
    const zkeyPath = path.join(buildDir, 'improvement.zkey');
    const vkeyPath = path.join(buildDir, 'verification_key.json');

    if (!fs.existsSync(wasmPath) || !fs.existsSync(zkeyPath) || !fs.existsSync(vkeyPath)) {
        console.error("[-] Circuit artifacts missing. Please run `npm run build` first.");
        process.exit(1);
    }

    if (!fs.existsSync(inputsDir)) {
        fs.mkdirSync(inputsDir, { recursive: true });
    }

    // Refresh inputs from execution_trace.json if available
    const traceCandidates = [
        path.join(REPO_ROOT, 'module1', 'execution_trace.json'),
        path.join(MODULE2_ROOT, '..', 'module1', 'execution_trace.json'),
        path.join(MODULE2_ROOT, '..', 'agent', 'execution_trace.json'),
        path.join(REPO_ROOT, 'agent', 'execution_trace.json'),
        path.join(MODULE2_ROOT, '..', 'execution_trace.json'),
        path.join(REPO_ROOT, 'execution_trace.json')
    ];
    const tracePath = traceCandidates.find(p => fs.existsSync(p));
    let traceData = null;

    if (tracePath) {
        traceData = JSON.parse(fs.readFileSync(tracePath, 'utf8'));
        if (traceData && traceData.zk_inputs) {
            const { score_v1, score_v2, score_v3, log_hash_v1, log_hash_v2, log_hash_v3 } = traceData.zk_inputs;
            console.log(`[+] Found execution trace at: ${tracePath}`);
            console.log(`[+] Syncing ZK inputs: V1=${score_v1}, V2=${score_v2}, V3=${score_v3}`);

            fs.writeFileSync(path.join(inputsDir, 'input_v1_v2.json'), JSON.stringify({
                s1: Number(score_v1),
                s2: Number(score_v2),
                log_hash_v1: String(log_hash_v1),
                log_hash_v2: String(log_hash_v2)
            }, null, 2), 'utf8');

            fs.writeFileSync(path.join(inputsDir, 'input_v2_v3.json'), JSON.stringify({
                s1: Number(score_v2),
                s2: Number(score_v3),
                log_hash_v1: String(log_hash_v2),
                log_hash_v2: String(log_hash_v3)
            }, null, 2), 'utf8');
        }
    }

    // V1 -> V2
    console.log("\n[*] Proving V1 -> V2...");
    try {
        runCommand(`${nodeBin} build/improvement_js/generate_witness.js build/improvement_js/improvement.wasm inputs/input_v1_v2.json build/witness_v1_v2.wtns`);
    } catch (e) {
        console.error("[-] FAILED: Witness constraint violated for V1 -> V2. No improvement, no proof, no reward.");
        process.exit(1);
    }
    runCommand(`${snarkjsCli} groth16 prove build/improvement.zkey build/witness_v1_v2.wtns build/proof_v1_v2.json build/public_v1_v2.json`);
    runCommand(`${snarkjsCli} groth16 verify build/verification_key.json build/public_v1_v2.json build/proof_v1_v2.json`);

    // V2 -> V3
    console.log("\n[*] Proving V2 -> V3...");
    try {
        runCommand(`${nodeBin} build/improvement_js/generate_witness.js build/improvement_js/improvement.wasm inputs/input_v2_v3.json build/witness_v2_v3.wtns`);
    } catch (e) {
        console.error("[-] FAILED: Witness constraint violated for V2 -> V3. No improvement, no proof, no reward.");
        process.exit(1);
    }
    runCommand(`${snarkjsCli} groth16 prove build/improvement.zkey build/witness_v2_v3.wtns build/proof_v2_v3.json build/public_v2_v3.json`);
    runCommand(`${snarkjsCli} groth16 verify build/verification_key.json build/public_v2_v3.json build/proof_v2_v3.json`);

    // Update execution_trace_with_proofs.json if trace exists
    if (traceData) {
        const proof_v1_v2 = JSON.parse(fs.readFileSync(path.join(buildDir, 'proof_v1_v2.json'), 'utf8'));
        const public_v1_v2 = JSON.parse(fs.readFileSync(path.join(buildDir, 'public_v1_v2.json'), 'utf8'));
        const proof_v2_v3 = JSON.parse(fs.readFileSync(path.join(buildDir, 'proof_v2_v3.json'), 'utf8'));
        const public_v2_v3 = JSON.parse(fs.readFileSync(path.join(buildDir, 'public_v2_v3.json'), 'utf8'));

        const enrichedTrace = {
            ...traceData,
            zk_proofs: {
                v1_v2: {
                    proof: proof_v1_v2,
                    public: public_v1_v2,
                    verified: true
                },
                v2_v3: {
                    proof: proof_v2_v3,
                    public: public_v2_v3,
                    verified: true
                }
            }
        };

        const enrichedPath = path.join(buildDir, 'execution_trace_with_proofs.json');
        fs.writeFileSync(enrichedPath, JSON.stringify(enrichedTrace, null, 2), 'utf8');
        console.log(`[+] Enriched trace updated at: ${enrichedPath}`);
    }

    console.log("\n[+] All proofs successfully generated and cryptographically verified!");
}

main().catch(err => {
    console.error("[-] Error generating proof:", err);
    process.exit(1);
});
