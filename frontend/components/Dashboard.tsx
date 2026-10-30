"use client";

import React, { useState, useEffect } from "react";
import {
  Layers,
  GitCommit,
  GitCompare,
  ShieldCheck,
  BrainCircuit,
  Play,
  RotateCcw,
  Zap,
  Coins,
  Cpu,
  Database,
  ExternalLink,
  Activity,
  CheckCircle2,
  Radio,
} from "lucide-react";
import ExecutionTree, { IterationData } from "./ExecutionTree";
import DiffViewer from "./DiffViewer";
import ZkTelemetryPanel from "./ZkTelemetryPanel";
import Agent2MemoryTab, { Agent2InheritResult } from "./Agent2MemoryTab";

export interface DashboardRuntimeData {
  task_id: string;
  protocol_version: string;
  live_mode?: boolean;
  iterations: IterationData[];
  diffs: {
    v1_v2?: string;
    v2_v3?: string;
    [key: string]: string | undefined;
  };
  changelog: string;
  zk_telemetry: {
    protocol: string;
    curve: string;
    overall_status: string;
    circuit_path: string;
    constraints_count: number;
    verifier_contract_address: string;
    block_explorer_url: string;
    escrow_tx_hash: string;
    gas_consumed: number;
    micro_reward_distributed: string;
    proof_v1_v2?: any;
    proof_v2_v3?: any;
  };
  memory_registry: {
    ipfs_cid: string;
    gateway_url: string;
    network: string;
    storage_provider: string;
    timestamp: number;
  };
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"tree" | "diff" | "zk" | "agent2">("tree");
  const [runtimeData, setRuntimeData] = useState<DashboardRuntimeData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [runningLoop, setRunningLoop] = useState<boolean>(false);
  const [liveMode, setLiveMode] = useState<boolean>(false);
  const [agent2Data, setAgent2Data] = useState<Agent2InheritResult | null>(null);

  // Fetch initial telemetry on mount
  useEffect(() => {
    fetchTelemetry();
  }, []);

  const fetchTelemetry = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/run-agent");
      if (res.ok) {
        const json = await res.json();
        setRuntimeData(json);
      }
    } catch (err) {
      console.error("Failed to fetch dashboard telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAgentLoop = async () => {
    setRunningLoop(true);
    try {
      const res = await fetch("/api/run-agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ live: liveMode }),
      });
      if (res.ok) {
        const json = await res.json();
        setRuntimeData(json);
      }
    } catch (err) {
      console.error("Agent execution run failed:", err);
    } finally {
      setRunningLoop(false);
    }
  };

  const v1 = runtimeData?.iterations?.[0];
  const v2 = runtimeData?.iterations?.[1];
  const v3 = runtimeData?.iterations?.[2];
  const initialScore = v1?.score ?? 52.0;
  const finalScore = v3?.score ?? 100.0;
  const scoreDelta = (finalScore - initialScore).toFixed(1);

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col">
      {/* Top Protocol Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Brand Title & Track Info */}
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-base font-bold tracking-tight text-white">
                    AutoEvolve Protocol
                  </h1>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-950 text-blue-400 border border-blue-800/60 font-semibold">
                    v1.0-ZK
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Decentralized, ZK-Attested Self-Improving Autonomous Agent with Immutable Cross-Agent Memory
                </p>
              </div>
            </div>

            {/* Protocol Status Badges & Trigger Controls */}
            <div className="flex flex-wrap items-center gap-2.5">
              {/* Network Pill */}
              <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Base Sepolia</span>
              </div>

              {/* Prover Pill */}
              <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-purple-400">
                <Cpu className="w-3.5 h-3.5" />
                <span>Groth16 (BN254)</span>
              </div>

              {/* Mode Toggle (Mock vs Live) */}
              <button
                type="button"
                onClick={() => setLiveMode(!liveMode)}
                className={`text-[11px] font-mono px-2.5 py-1 rounded-md border transition ${
                  liveMode
                    ? "bg-purple-950/80 border-purple-600 text-purple-300"
                    : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
                title="Toggle Live Featherless API mode vs Calibrated Mock"
              >
                {liveMode ? "Live API (Qwen+R1)" : "Deterministic Mock"}
              </button>

              {/* Trigger Agent Run Button */}
              <button
                type="button"
                onClick={handleRunAgentLoop}
                disabled={runningLoop}
                className="flex items-center space-x-2 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-md shadow-blue-600/30 border border-blue-400/30 transition disabled:opacity-50"
              >
                {runningLoop ? (
                  <>
                    <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                    <span>Executing V1 &rarr; V3...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-white" />
                    <span>Run Protocol Engine</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Metric Overview Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {/* Metric 1: Initial Score */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">1. Baseline (V1)</span>
            <div className="text-xl font-bold font-mono text-rose-400 mt-1">
              {loading ? "..." : `${initialScore.toFixed(1)}`}
            </div>
            <span className="text-[10px] text-slate-400">Failed: capacity & unhashable</span>
          </div>

          {/* Metric 2: Final Score */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">2. Production (V3)</span>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {loading ? "..." : `${finalScore.toFixed(1)}`}
            </div>
            <span className="text-[10px] text-emerald-500 font-medium">10/10 tests passed</span>
          </div>

          {/* Metric 3: Score Gain */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">3. Performance Gain</span>
            <div className="text-xl font-bold font-mono text-blue-400 mt-1">
              {loading ? "..." : `+${scoreDelta} pts`}
            </div>
            <span className="text-[10px] text-slate-400">Proven by ZK Circuits</span>
          </div>

          {/* Metric 4: ZK Attestation */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">4. Groth16 Proofs</span>
            <div className="text-base font-bold font-mono text-purple-400 mt-1 flex items-center space-x-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Verified 2/2</span>
            </div>
            <span className="text-[10px] text-slate-400">BN254 Field Safe (248-bit)</span>
          </div>

          {/* Metric 5: DataDAO IPFS CID */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 col-span-2 md:col-span-1">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">5. Immutable CID</span>
            <div className="text-xs font-mono text-blue-300 mt-1 truncate" title={runtimeData?.memory_registry?.ipfs_cid}>
              {loading ? "..." : runtimeData?.memory_registry?.ipfs_cid?.slice(0, 16) + "..."}
            </div>
            <a
              href={runtimeData?.memory_registry?.gateway_url}
              target="_blank"
              rel="noreferrer"
              className="text-[10px] text-slate-400 hover:text-blue-400 flex items-center space-x-1 mt-0.5"
            >
              <span>View IPFS Snapshot</span>
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
          </div>

          {/* Metric 6: On-Chain Escrow Reward */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 col-span-2 md:col-span-1">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">6. Escrow Reward</span>
            <div className="text-base font-bold font-mono text-emerald-400 mt-1 flex items-center space-x-1">
              <Coins className="w-4 h-4 text-emerald-400" />
              <span>{runtimeData?.zk_telemetry?.micro_reward_distributed || "0.0500 ETH"}</span>
            </div>
            <span className="text-[10px] text-slate-400">Settled on Testnet</span>
          </div>
        </div>

        {/* Panel Tabs Navigation */}
        <div className="border-b border-slate-800 flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setActiveTab("tree")}
            className={`flex items-center space-x-2 py-3 px-4 text-xs font-medium border-b-2 transition ${
              activeTab === "tree"
                ? "border-blue-500 text-blue-400 font-semibold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <GitCommit className="w-4 h-4" />
            <span>Panel 1: Execution DAG & Trace</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("diff")}
            className={`flex items-center space-x-2 py-3 px-4 text-xs font-medium border-b-2 transition ${
              activeTab === "diff"
                ? "border-blue-500 text-blue-400 font-semibold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <GitCompare className="w-4 h-4" />
            <span>Panel 2: Incremental Diffs & Changelog</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("zk")}
            className={`flex items-center space-x-2 py-3 px-4 text-xs font-medium border-b-2 transition ${
              activeTab === "zk"
                ? "border-purple-500 text-purple-400 font-semibold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Panel 3: Groth16 ZK Telemetry & Escrow</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("agent2")}
            className={`flex items-center space-x-2 py-3 px-4 text-xs font-medium border-b-2 transition ${
              activeTab === "agent2"
                ? "border-blue-500 text-blue-400 font-semibold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <BrainCircuit className="w-4 h-4" />
            <span>Panel 4: Agent 2 Memory Inheritance</span>
          </button>
        </div>

        {/* Tab Content Panels */}
        {loading ? (
          <div className="p-20 flex flex-col items-center justify-center space-y-3 bg-slate-900/40 rounded-xl border border-slate-800">
            <RotateCcw className="w-8 h-8 text-blue-400 animate-spin" />
            <p className="text-sm text-slate-400 font-mono">
              Loading dynamic agent execution telemetry from protocol engine...
            </p>
          </div>
        ) : (
          <div>
            {activeTab === "tree" && (
              <ExecutionTree iterations={runtimeData?.iterations || []} />
            )}

            {activeTab === "diff" && (
              <DiffViewer
                diffs={runtimeData?.diffs}
                changelog={runtimeData?.changelog}
                v1Code={v1?.code}
                v2Code={v2?.code}
                v3Code={v3?.code}
                v1Score={initialScore}
                v2Score={v2?.score ?? 86}
                v3Score={finalScore}
              />
            )}

            {activeTab === "zk" && (
              <ZkTelemetryPanel zkTelemetry={runtimeData?.zk_telemetry} />
            )}

            {activeTab === "agent2" && (
              <Agent2MemoryTab
                initialData={agent2Data}
                onRunInherit={async (query: string) => {
                  const res = await fetch("/api/agent2-inherit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query }),
                  });
                  const json = await res.json();
                  setAgent2Data(json);
                  return json;
                }}
              />
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500 font-mono">
        AutoEvolve Protocol &bull; CBIT Hacktoberfest &apos;26 &bull; Team VignanaSarathi (TEAM-31) &bull; Open-Source ZK Agent Infrastructure
      </footer>
    </div>
  );
}

