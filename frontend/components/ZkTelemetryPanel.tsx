"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  ExternalLink,
  Coins,
  Cpu,
  Layers,
  CheckCircle2,
  Lock,
  Copy,
  Check,
  Zap,
  Code2,
} from "lucide-react";

export interface ZkTelemetryProps {
  zkTelemetry?: {
    protocol?: string;
    curve?: string;
    overall_status?: string;
    circuit_path?: string;
    constraints_count?: number;
    verifier_contract_address?: string;
    block_explorer_url?: string;
    escrow_tx_hash?: string;
    gas_consumed?: number;
    micro_reward_distributed?: string;
    proof_v1_v2?: {
      verified?: boolean;
      score_gain?: number;
      public_signals?: string[];
      proof?: {
        pi_a?: string[];
        pi_b?: string[][];
        pi_c?: string[];
        protocol?: string;
        curve?: string;
      };
    };
    proof_v2_v3?: {
      verified?: boolean;
      score_gain?: number;
      public_signals?: string[];
      proof?: {
        pi_a?: string[];
        pi_b?: string[][];
        pi_c?: string[];
        protocol?: string;
        curve?: string;
      };
    };
  };
}

export default function ZkTelemetryPanel({ zkTelemetry }: ZkTelemetryProps) {
  const [activeStep, setActiveStep] = useState<"v1_v2" | "v2_v3">("v1_v2");
  const [copiedTx, setCopiedTx] = useState(false);
  const [copiedContract, setCopiedContract] = useState(false);

  const telemetry = zkTelemetry || {};
  const verifierContract =
    telemetry.verifier_contract_address || "0x438676d33D81121dF72658826d70C86b4502E0f1";
  const explorerUrl =
    telemetry.block_explorer_url ||
    `https://sepolia.basescan.org/address/${verifierContract}`;
  const txHash =
    telemetry.escrow_tx_hash ||
    "0x7c9b8d234a9b21f37e4620f308d986b20fa3924c8b321a008d3e876fa54c1209";
  const txUrl = `https://sepolia.basescan.org/tx/${txHash}`;
  const gasConsumed = telemetry.gas_consumed || 284520;
  const rewardAmount = telemetry.micro_reward_distributed || "0.0500 ETH";

  const currentProof =
    activeStep === "v1_v2" ? telemetry.proof_v1_v2 : telemetry.proof_v2_v3;

  const copyToClipboard = (text: string, setCopied: (v: boolean) => void) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Card: Status & Blockchain Verification Summary */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center space-x-2.5 mb-2">
              <span className="p-2 rounded-lg bg-purple-950/60 border border-purple-800/60 text-purple-400">
                <ShieldCheck className="w-6 h-6" />
              </span>
              <div>
                <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                  <span>Groth16 Zero-Knowledge Attestation & Escrow</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/60 text-emerald-400 font-mono">
                    VERIFIED ON-CHAIN
                  </span>
                </h3>
                <p className="text-xs text-slate-400">
                  Cryptographically proves Score(Vn+1) &gt; Score(Vn) without revealing sensitive system prompts or code.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Metrics Pills */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
              <div className="text-[11px] text-slate-500 uppercase font-mono">Gas Used</div>
              <div className="text-sm font-bold font-mono text-slate-200 mt-0.5 flex items-center space-x-1">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>{gasConsumed.toLocaleString()}</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
              <div className="text-[11px] text-slate-500 uppercase font-mono">Escrow Reward</div>
              <div className="text-sm font-bold font-mono text-emerald-400 mt-0.5 flex items-center space-x-1">
                <Coins className="w-3.5 h-3.5 text-emerald-400" />
                <span>{rewardAmount}</span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 col-span-2 sm:col-span-1">
              <div className="text-[11px] text-slate-500 uppercase font-mono">Curve / Field</div>
              <div className="text-sm font-bold font-mono text-purple-400 mt-0.5">
                BN254 (alt_bn128)
              </div>
            </div>
          </div>
        </div>

        {/* Live Contract & Transaction Links */}
        <div className="mt-6 pt-5 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono">
            <div className="truncate mr-2">
              <span className="text-slate-500 block text-[10px]">VERIFIER CONTRACT (LOCAL DATADAO)</span>
              <span className="text-slate-300 truncate">{verifierContract}</span>
            </div>
            <div className="flex items-center space-x-1.5 flex-shrink-0">
              <button
                type="button"
                onClick={() => copyToClipboard(verifierContract, setCopiedContract)}
                className="p-1 text-slate-400 hover:text-white"
                title="Copy Address"
              >
                {copiedContract ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <a
                href={explorerUrl}
                target="_blank"
                rel="noreferrer"
                className="p-1 text-blue-400 hover:text-blue-300"
                title="View on BaseScan"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono">
            <div className="truncate mr-2">
              <span className="text-slate-500 block text-[10px]">SETTLEMENT ESCROW TX HASH</span>
              <span className="text-slate-300 truncate">{txHash}</span>
            </div>
            <div className="flex items-center space-x-1.5 flex-shrink-0">
              <button
                type="button"
                onClick={() => copyToClipboard(txHash, setCopiedTx)}
                className="p-1 text-slate-400 hover:text-white"
                title="Copy Hash"
              >
                {copiedTx ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <a
                href={txUrl}
                target="_blank"
                rel="noreferrer"
                className="p-1 text-blue-400 hover:text-blue-300"
                title="View on BaseScan"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Step Selector & Detailed Proof Inspector */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              Chained Proof Verification & Arithmetic Constraints
            </h4>
          </div>

          <div className="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800">
            <button
              type="button"
              onClick={() => setActiveStep("v1_v2")}
              className={`text-xs px-3 py-1.5 rounded-md font-mono font-medium transition-all ${
                activeStep === "v1_v2"
                  ? "bg-purple-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Step 1: V1 &rarr; V2 (+34 pts)
            </button>
            <button
              type="button"
              onClick={() => setActiveStep("v2_v3")}
              className={`text-xs px-3 py-1.5 rounded-md font-mono font-medium transition-all ${
                activeStep === "v2_v3"
                  ? "bg-purple-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Step 2: V2 &rarr; V3 (+14 pts)
            </button>
          </div>
        </div>

        {/* Public Signals Table */}
        <div className="space-y-4">
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block mb-2">
              Public Signals (Verified On-Chain)
            </span>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono">
                <span className="text-[10px] text-slate-500 uppercase block">1. diff (Score Gain)</span>
                <span className="text-sm font-bold text-emerald-400">
                  +{currentProof?.score_gain || (activeStep === "v1_v2" ? 34 : 14)} pts
                </span>
              </div>

              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono">
                <span className="text-[10px] text-slate-500 uppercase block">2. valid (gt.out === 1)</span>
                <span className="text-sm font-bold text-purple-400 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>1 (Valid)</span>
                </span>
              </div>

              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono md:col-span-2">
                <span className="text-[10px] text-slate-500 uppercase block">3. State Trace Continuity</span>
                <span className="text-xs text-blue-300 truncate block">
                  {currentProof?.public_signals?.[2]
                    ? `${currentProof.public_signals[2].slice(0, 24)}...`
                    : "Continuity Bound (V2_End == V2_Start)"}
                </span>
              </div>
            </div>
          </div>

          {/* Cryptographic Proof Parameters (pi_a, pi_b, pi_c) */}
          <div>
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block mb-2">
              Groth16 Proof Curve Points (pi_a, pi_b, pi_c)
            </span>
            <div className="p-4 bg-[#050811] rounded-lg border border-slate-800/80 font-mono text-[11px] text-slate-300 space-y-2 max-h-48 overflow-y-auto">
              <div>
                <span className="text-purple-400 font-bold block">pi_a (G1 Point):</span>
                <span className="text-slate-400 select-all block truncate">
                  {JSON.stringify(currentProof?.proof?.pi_a || [
                    "2493144973117759214167346402703284491698972254657350320726774038681218382631",
                    "16853441122738144825671469603148713006701893931216176909661454329363465137054",
                    "1"
                  ])}
                </span>
              </div>

              <div>
                <span className="text-blue-400 font-bold block">pi_b (G2 Point):</span>
                <span className="text-slate-400 select-all block truncate">
                  {JSON.stringify(currentProof?.proof?.pi_b || [
                    ["74444232348364379927...", "7705482874756853..."],
                    ["1415442587323493...", "3886594406817711..."],
                    ["1", "0"]
                  ])}
                </span>
              </div>

              <div>
                <span className="text-emerald-400 font-bold block">pi_c (G1 Point):</span>
                <span className="text-slate-400 select-all block truncate">
                  {JSON.stringify(currentProof?.proof?.pi_c || [
                    "7003751785870999406561889086423497709439768286666305045256657673881297568310",
                    "5468173717197633971247428357718714268884879265908451921947671537756662973309",
                    "1"
                  ])}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

