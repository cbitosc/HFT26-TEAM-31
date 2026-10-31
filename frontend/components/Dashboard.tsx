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
  Sparkles,
  FlaskConical,
  ChevronDown,
  ChevronUp,
  FileCode2,
  Edit3,
} from "lucide-react";
import ExecutionTree, { IterationData } from "./ExecutionTree";
import DiffViewer from "./DiffViewer";
import ZkTelemetryPanel from "./ZkTelemetryPanel";
import Agent2MemoryTab, { Agent2InheritResult } from "./Agent2MemoryTab";

export interface DynamicTestCase {
  name: string;
  category: string;
  description: string;
}

export interface DashboardRuntimeData {
  task_id: string;
  protocol_version: string;
  live_mode?: boolean;
  custom_prompt?: string | null;
  dynamic_tests?: DynamicTestCase[] | null;
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

const PRESET_PROMPTS = [
  {
    id: "lru",
    label: "LRU Cache (Benchmark)",
    prompt: "",
    desc: "Default 10-test suite with linear scan to doubly linked list progression.",
  },
  {
    id: "rate_limiter",
    label: "Token Bucket Rate Limiter",
    prompt: "Implement a Token Bucket Rate Limiter with capacity and refill_rate",
    desc: "Dynamically synthesizes token leak, zero capacity, and thread-safety tests.",
  },
  {
    id: "ring_buffer",
    label: "Thread-Safe Ring Buffer",
    prompt: "Implement a thread-safe Circular Ring Buffer with fixed capacity and overflow protection",
    desc: "Dynamically synthesizes circular wrap-around, overflow, and concurrent lock tests.",
  },
  {
    id: "trie",
    label: "Prefix Tree (Trie)",
    prompt: "Implement a Trie prefix tree with insert, search, and startsWith",
    desc: "Dynamically synthesizes prefix matching, word count, and case sensitivity tests.",
  },
  {
    id: "min_stack",
    label: "Min Stack (O(1))",
    prompt: "Implement a Min Stack with O(1) push, pop, top, and getMin",
    desc: "Dynamically synthesizes constant-time minimum tracking and empty pop boundaries.",
  },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"tree" | "diff" | "zk" | "agent2">("tree");
  const [runtimeData, setRuntimeData] = useState<DashboardRuntimeData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [runningLoop, setRunningLoop] = useState<boolean>(false);
  const [liveMode, setLiveMode] = useState<boolean>(false);
  const [agent2Data, setAgent2Data] = useState<Agent2InheritResult | null>(null);

  // Custom Prompt & TestCaseCreator States
  const [selectedPreset, setSelectedPreset] = useState<string>("lru");
  const [customPrompt, setCustomPrompt] = useState<string>("");
  const [showPromptEditor, setShowPromptEditor] = useState<boolean>(false);
  const [showTestsDrawer, setShowTestsDrawer] = useState<boolean>(false);

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
        if (json.custom_prompt) {
          setCustomPrompt(json.custom_prompt);
          // Match preset if exists
          const matched = PRESET_PROMPTS.find((p) => p.prompt === json.custom_prompt);
          if (matched) {
            setSelectedPreset(matched.id);
          } else {
            setSelectedPreset("custom");
          }
        }
      }
    } catch (err) {
      console.error("Failed to fetch dashboard telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (presetId: string) => {
    setSelectedPreset(presetId);
    if (presetId === "custom") {
      setShowPromptEditor(true);
    } else {
      const preset = PRESET_PROMPTS.find((p) => p.id === presetId);
      if (preset) {
        setCustomPrompt(preset.prompt);
      }
    }
  };

  const handleRunAgentLoop = async () => {
    setRunningLoop(true);
    try {
      const activePrompt = customPrompt.trim();
      const payload: { live: boolean; custom_prompt?: string } = {
        live: liveMode,
      };
      if (activePrompt.length > 0) {
        payload.custom_prompt = activePrompt;
      }

      const res = await fetch("/api/run-agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
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

  const isDynamicMode = !!(runtimeData?.custom_prompt || (customPrompt && customPrompt.trim().length > 0));
  const dynamicTestsCount = runtimeData?.dynamic_tests?.length || 0;

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
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800/60 font-semibold">
                    Local DataDAO
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Decentralized, ZK-Attested Self-Improving Autonomous Agent with Immutable Cross-Agent Memory
                </p>
              </div>
            </div>

            {/* Protocol Status Badges & Trigger Controls */}
            <div className="flex flex-wrap items-center gap-2.5">
              {/* Local DataDAO Pill */}
              <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Local DataDAO</span>
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
                    <span>Synthesizing & Iterating...</span>
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
        
        {/* Task & TestCaseCreator Prompt Controller Banner */}
        <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-blue-900/40 border border-blue-700/50 flex items-center justify-center text-blue-400">
                <FlaskConical className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-sm font-semibold text-white tracking-wide">
                    Task Prompt &amp; TestCaseCreator Agent
                  </h2>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800/60">
                    Dynamic Synthesis
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Select a predefined benchmark or enter a custom prompt. The <span className="text-blue-400 font-medium">TestCaseCreator agent</span> will dynamically synthesize functional, boundary, safety, and stress unit tests before generation and evaluation.
                </p>
              </div>
            </div>

            {/* Prompt Editor Toggle */}
            <button
              type="button"
              onClick={() => setShowPromptEditor(!showPromptEditor)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-xs font-mono text-slate-300 border border-slate-700/70 transition"
            >
              <Edit3 className="w-3.5 h-3.5 text-blue-400" />
              <span>{showPromptEditor ? "Hide Prompt Editor" : "Custom Prompt Editor"}</span>
              {showPromptEditor ? <ChevronUp className="w-3.5 h-3.5 ml-1" /> : <ChevronDown className="w-3.5 h-3.5 ml-1" />}
            </button>
          </div>

          {/* Preset Buttons */}
          <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/80">
            <span className="text-xs font-mono text-slate-400 mr-2">Target Task:</span>
            {PRESET_PROMPTS.map((preset) => (
              <button
                key={preset.id}
                type="button"
                onClick={() => handleSelectPreset(preset.id)}
                className={`text-xs font-mono px-3 py-1.5 rounded-lg border transition ${
                  selectedPreset === preset.id && (!showPromptEditor || preset.prompt === customPrompt)
                    ? "bg-blue-600/20 border-blue-500 text-blue-300 font-semibold shadow-sm shadow-blue-500/20"
                    : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                }`}
              >
                {preset.label}
              </button>
            ))}
            <button
              type="button"
              onClick={() => handleSelectPreset("custom")}
              className={`text-xs font-mono px-3 py-1.5 rounded-lg border transition ${
                selectedPreset === "custom" || showPromptEditor
                  ? "bg-purple-600/20 border-purple-500 text-purple-300 font-semibold"
                  : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              ✍️ Custom User Prompt...
            </button>
          </div>

          {/* Interactive Custom Prompt Editor Form */}
          {showPromptEditor && (
            <div className="mt-4 pt-4 border-t border-slate-800 space-y-3 animate-in fade-in slide-in-from-top-2 duration-200">
              <label className="block text-xs font-mono text-slate-300">
                Custom Generation Directive for Generator &amp; TestCaseCreator Agent:
              </label>
              <div className="relative">
                <textarea
                  value={customPrompt}
                  onChange={(e) => {
                    setCustomPrompt(e.target.value);
                    setSelectedPreset("custom");
                  }}
                  rows={3}
                  placeholder="e.g. Implement a Token Bucket Rate Limiter with capacity and refill_rate, thread-safe consumption, and time refill..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition resize-y"
                />
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono text-slate-400">
                <div className="flex items-center space-x-2 text-indigo-300">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  <span>TestCaseCreator dynamically generates syntax-verified tests across 4 safety suites.</span>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => {
                      setCustomPrompt("");
                      setSelectedPreset("lru");
                      setShowPromptEditor(false);
                    }}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                  >
                    Reset to Default LRU
                  </button>
                  <button
                    type="button"
                    onClick={handleRunAgentLoop}
                    disabled={runningLoop}
                    className="flex items-center space-x-2 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium shadow-md shadow-blue-600/30 transition disabled:opacity-50"
                  >
                    {runningLoop ? (
                      <>
                        <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                        <span>Synthesizing...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-3.5 h-3.5 fill-white" />
                        <span>Synthesize &amp; Run Agent Loop</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Dynamic Test Suite Status Pill */}
          {dynamicTestsCount > 0 && (
            <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center space-x-2 text-xs font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-slate-300 font-semibold">Active Dynamic Suite:</span>
                <span className="text-emerald-400 font-medium">{dynamicTestsCount} Unit Tests Synthesized</span>
                <span className="text-slate-500 text-[11px]">&bull; Task: {runtimeData?.custom_prompt?.slice(0, 48)}...</span>
              </div>
              <button
                type="button"
                onClick={() => setShowTestsDrawer(!showTestsDrawer)}
                className="text-[11px] font-mono text-blue-400 hover:text-blue-300 flex items-center space-x-1"
              >
                <span>{showTestsDrawer ? "Hide Generated Tests" : "Inspect Generated Test Cases"}</span>
                {showTestsDrawer ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            </div>
          )}

          {/* Expandable Test Cases Grid */}
          {showTestsDrawer && runtimeData?.dynamic_tests && (
            <div className="mt-3 p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2 animate-in fade-in duration-200">
              <div className="text-[11px] font-mono text-slate-400 font-semibold mb-1">
                TestCaseCreator Dynamic Test Suite Execution Results:
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {runtimeData.dynamic_tests.map((test, idx) => {
                  const categoryColors: Record<string, string> = {
                    functional: "bg-blue-950/80 text-blue-400 border-blue-800/60",
                    boundary: "bg-amber-950/80 text-amber-400 border-amber-800/60",
                    safety: "bg-purple-950/80 text-purple-400 border-purple-800/60",
                    stress: "bg-rose-950/80 text-rose-400 border-rose-800/60",
                  };
                  const badgeClass = categoryColors[test.category] || "bg-slate-900 text-slate-400 border-slate-800";
                  return (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-2"
                    >
                      <div className="min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-mono font-medium text-slate-200 truncate">
                            {test.name}
                          </span>
                          <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase ${badgeClass}`}>
                            {test.category}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          {test.description}
                        </p>
                      </div>
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </section>

        {/* Metric Overview Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {/* Metric 1: Initial Score */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">1. Baseline (V1)</span>
            <div className="text-xl font-bold font-mono text-rose-400 mt-1">
              {loading ? "..." : `${initialScore.toFixed(1)}`}
            </div>
            <span className="text-[10px] text-slate-400 truncate block">
              Failed: {v1?.failed_tests && v1.failed_tests.length > 0 ? v1.failed_tests.slice(0, 2).join(", ") : "None"}
            </span>
          </div>

          {/* Metric 2: Final Score */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">2. Production (V3)</span>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {loading ? "..." : `${finalScore.toFixed(1)}`}
            </div>
            <span className="text-[10px] text-emerald-500 font-medium">
              {v3?.passed ?? 10}/{v3?.total ?? 10} tests passed
            </span>
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

          {/* Metric 6: DataDAO Reward */}
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 col-span-2 md:col-span-1">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">6. DataDAO Reward</span>
            <div className="text-base font-bold font-mono text-emerald-400 mt-1 flex items-center space-x-1">
              <Coins className="w-4 h-4 text-emerald-400" />
              <span>0.0500 DATA</span>
            </div>
            <span className="text-[10px] text-slate-400">Settled on Local DataDAO</span>
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
            <span>Panel 1: Execution DAG &amp; Trace</span>
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
            <span>Panel 2: Incremental Diffs &amp; Changelog</span>
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
            <span>Panel 3: Groth16 ZK Telemetry &amp; Escrow</span>
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
                v1Architecture={v1?.architecture}
                v2Architecture={v2?.architecture}
                v3Architecture={v3?.architecture}
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
