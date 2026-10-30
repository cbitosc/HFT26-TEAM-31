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
  TestTube2,
  TrendingUp,
  FileCode,
} from "lucide-react";
import TaskConsole, { TaskOption } from "./TaskConsole";
import WorkflowDAG, { WorkflowStage } from "./WorkflowDAG";
import TestExecutionPanel from "./TestExecutionPanel";
import CriticIntelligencePanel from "./CriticIntelligencePanel";
import EvolutionAnalytics from "./EvolutionAnalytics";
import ExecutionTree, { IterationData } from "./ExecutionTree";
import DiffViewer from "./DiffViewer";
import ZkTelemetryPanel from "./ZkTelemetryPanel";
import Agent2MemoryTab, { Agent2InheritResult } from "./Agent2MemoryTab";

export interface DashboardRuntimeData {
  task_id: string;
  task_name?: string;
  task_description?: string;
  programming_language?: string;
  protocol_version: string;
  execution_mode?: "LIVE" | "OFFLINE_DEMO" | "REPLAY" | string;
  live_mode?: boolean;
  test_generation?: any;
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

const DEFAULT_BENCHMARKS: TaskOption[] = [
  {
    task_id: "lru_cache_01",
    name: "Least Recently Used (LRU) Cache",
    description:
      "Design and implement a high-performance Least Recently Used (LRU) Cache supporting get and put in O(1) average time complexity, deterministic eviction, and defensive handling of non-hashable inputs.",
    programming_language: "python",
    class_or_function_name: "LRUCache",
    functional_requirements: [
      "get(key) returns cached value or -1 if missing.",
      "put(key, value) updates value if key exists, or inserts new key.",
      "When capacity is exceeded, evicts the least recently used item.",
      "Capacity <= 0: put is a no-op, get always returns -1.",
      "Unhashable keys safely ignored without unhandled TypeError crashes.",
      "Strict O(1) amortized throughput under high concurrency.",
    ],
  },
  {
    task_id: "rate_limiter_02",
    name: "API Rate Limiter (Rolling 60s Window)",
    description:
      "Implement a production-grade API Rate Limiter allowing a maximum of 5 requests per user within a rolling 60-second window. Eliminates boundary-burst vulnerabilities and prunes expired timestamps.",
    programming_language: "python",
    class_or_function_name: "RateLimiter",
    functional_requirements: [
      "allow_request(user_id, timestamp) returns True if quota is available, else False.",
      "Enforce rolling sliding window of 60 seconds (not a fixed reset window).",
      "get_remaining_tokens(user_id, timestamp) returns count of available slots.",
      "Prunes timestamps older than or equal to (timestamp - window_seconds).",
      "Handle non-positive parameters and invalid identifiers defensively.",
      "Sub-millisecond amortized latency under high traffic.",
    ],
  },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "tree" | "diff" | "tests" | "critic" | "zk" | "agent2"
  >("overview");
  const [runtimeData, setRuntimeData] = useState<DashboardRuntimeData | null>(null);
  const [tasks, setTasks] = useState<TaskOption[]>(DEFAULT_BENCHMARKS);
  const [selectedTaskId, setSelectedTaskId] = useState<string>("lru_cache_01");
  const [executionMode, setExecutionMode] = useState<"LIVE" | "OFFLINE_DEMO" | "REPLAY">("OFFLINE_DEMO");
  const [loading, setLoading] = useState<boolean>(true);
  const [runningLoop, setRunningLoop] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [stepMode, setStepMode] = useState<boolean>(false);
  const [selectedVersion, setSelectedVersion] = useState<string>("V1");
  const [agent2Data, setAgent2Data] = useState<Agent2InheritResult | null>(null);

  useEffect(() => {
    fetchTelemetry();
  }, []);

  useEffect(() => {
    if (runtimeData?.iterations && runtimeData.iterations.length > 0) {
      setSelectedVersion(runtimeData.iterations[0].version);
    }
  }, [runtimeData]);

  const fetchTelemetry = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/run-agent");
      if (res.ok) {
        const json = await res.json();
        setRuntimeData(json);
        if (json.task_id) setSelectedTaskId(json.task_id);
      }
    } catch (err) {
      console.error("Failed to fetch dashboard telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartEvolution = async () => {
    setRunningLoop(true);
    setIsPaused(false);
    try {
      const res = await fetch("/api/run-agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: selectedTaskId,
          live: executionMode === "LIVE",
          replay: executionMode === "REPLAY",
        }),
      });
      if (res.ok) {
        const json = await res.json();
        setRuntimeData(json);
      }
    } catch (err) {
      console.error("Evolution run failed:", err);
    } finally {
      setRunningLoop(false);
    }
  };

  const handlePause = () => {
    setIsPaused(true);
  };

  const handleResume = () => {
    setIsPaused(false);
  };

  const handleStep = () => {
    // In step mode, cycle to the next iteration in the recorded sequence
    if (!runtimeData?.iterations || runtimeData.iterations.length <= 1) return;
    const currentIdx = runtimeData.iterations.findIndex((it) => it.version === selectedVersion);
    const nextIdx = (currentIdx + 1) % runtimeData.iterations.length;
    setSelectedVersion(runtimeData.iterations[nextIdx].version);
  };

  const handleReset = () => {
    fetchTelemetry();
    setIsPaused(false);
  };

  const handleCustomTaskSubmit = (newTask: TaskOption) => {
    setTasks((prev) => [...prev, newTask]);
    setSelectedTaskId(newTask.task_id);
  };

  const currentIteration =
    runtimeData?.iterations.find((it) => it.version === selectedVersion) ||
    runtimeData?.iterations[0];

  const currentIterIndex = runtimeData?.iterations.findIndex((it) => it.version === selectedVersion) ?? 0;
  const nextIteration = runtimeData?.iterations[currentIterIndex + 1];

  const v1 = runtimeData?.iterations?.[0];
  const vLast = runtimeData?.iterations?.[runtimeData?.iterations?.length - 1];
  const initialScore = v1?.score ?? 52.0;
  const finalScore = vLast?.score ?? 100.0;
  const scoreDelta = (finalScore - initialScore).toFixed(1);

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col font-sans">
      {/* Top Protocol Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Brand Title */}
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-base font-bold tracking-tight text-white">
                    AutoEvolve Protocol
                  </h1>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-semibold">
                    Control Room v2.0
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Decentralized, ZK-Attested Self-Improving Autonomous Agent Platform
                </p>
              </div>
            </div>

            {/* Protocol Status Badges */}
            <div className="flex flex-wrap items-center gap-2.5">
              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Base Sepolia</span>
              </div>

              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-purple-400">
                <Cpu className="w-3.5 h-3.5" />
                <span>Groth16 (BN254)</span>
              </div>

              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono text-cyan-400">
                <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                <span>Mode: {executionMode}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Task Console Section */}
        <TaskConsole
          tasks={tasks}
          selectedTaskId={selectedTaskId}
          onSelectTask={(id) => {
            setSelectedTaskId(id);
          }}
          executionMode={executionMode}
          onSelectMode={(mode) => setExecutionMode(mode)}
          isRunning={runningLoop}
          isPaused={isPaused}
          stepMode={stepMode}
          onStart={handleStartEvolution}
          onPause={handlePause}
          onResume={handleResume}
          onStep={handleStep}
          onReset={handleReset}
          onCustomTaskSubmit={handleCustomTaskSubmit}
        />

        {/* Real-time Agent Workflow DAG */}
        <WorkflowDAG
          currentStageId={runningLoop ? "evaluator" : "critic"}
          currentVersion={selectedVersion}
        />

        {/* Navigation Tabs Bar */}
        <div className="border-b border-slate-800/90 flex items-center justify-between">
          <nav className="flex space-x-2 sm:space-x-4 overflow-x-auto pb-1">
            <button
              type="button"
              onClick={() => setActiveTab("overview")}
              className={`flex items-center space-x-2 py-2.5 px-3 border-b-2 text-xs font-medium font-mono uppercase tracking-wider transition ${
                activeTab === "overview"
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Workspace Overview</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("tree")}
              className={`flex items-center space-x-2 py-2.5 px-3 border-b-2 text-xs font-medium font-mono uppercase tracking-wider transition ${
                activeTab === "tree"
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <GitCommit className="w-4 h-4" />
              <span>Evolution History</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("diff")}
              className={`flex items-center space-x-2 py-2.5 px-3 border-b-2 text-xs font-medium font-mono uppercase tracking-wider transition ${
                activeTab === "diff"
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <GitCompare className="w-4 h-4" />
              <span>Code Comparison</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("tests")}
              className={`flex items-center space-x-2 py-2.5 px-3 border-b-2 text-xs font-medium font-mono uppercase tracking-wider transition ${
                activeTab === "tests"
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <TestTube2 className="w-4 h-4" />
              <span>Test Generation & Runner</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("critic")}
              className={`flex items-center space-x-2 py-2.5 px-3 border-b-2 text-xs font-medium font-mono uppercase tracking-wider transition ${
                activeTab === "critic"
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Critic Analysis</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("zk")}
              className={`flex items-center space-x-2 py-2.5 px-3 border-b-2 text-xs font-medium font-mono uppercase tracking-wider transition ${
                activeTab === "zk"
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Verification Status</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("agent2")}
              className={`flex items-center space-x-2 py-2.5 px-3 border-b-2 text-xs font-medium font-mono uppercase tracking-wider transition ${
                activeTab === "agent2"
                  ? "border-cyan-400 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <BrainCircuit className="w-4 h-4" />
              <span>Agent Network & Memory</span>
            </button>
          </nav>
        </div>

        {/* Tab 1: Overview Tab */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Analytics Summary */}
            {runtimeData?.iterations && (
              <EvolutionAnalytics iterations={runtimeData.iterations} />
            )}

            {/* Test Execution Panel & Critic Intelligence Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TestExecutionPanel
                testDetails={currentIteration?.test_details || []}
                generationMeta={runtimeData?.test_generation}
                activeVersionLabel={selectedVersion}
              />

              <div className="space-y-6">
                <CriticIntelligencePanel
                  critique={currentIteration?.critique}
                  versionLabel={selectedVersion}
                  isResolvedInNext={!!nextIteration && (!nextIteration.critique?.failure_type || nextIteration.critique?.failure_type === "None")}
                  nextVersionLabel={nextIteration?.version || "Next"}
                />

                {/* Quick Version Selector Pill Row */}
                {runtimeData?.iterations && runtimeData.iterations.length > 0 && (
                  <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-4 shadow-xl">
                    <span className="text-[10px] font-mono uppercase text-slate-400 block mb-2">
                      Select Iteration To Inspect:
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {runtimeData.iterations.map((it) => (
                        <button
                          key={it.version}
                          type="button"
                          onClick={() => setSelectedVersion(it.version)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition border ${
                            selectedVersion === it.version
                              ? "bg-cyan-950 text-cyan-300 border-cyan-500 shadow-sm"
                              : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
                          }`}
                        >
                          {it.version} &bull; Score: {it.score.toFixed(1)}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Evolution History Tree Tab */}
        {activeTab === "tree" && (
          <ExecutionTree
            iterations={runtimeData?.iterations || []}
            selectedVersion={selectedVersion}
            onSelectIteration={(ver) => setSelectedVersion(ver)}
          />
        )}

        {/* Tab 3: Code Comparison Tab */}
        {activeTab === "diff" && (
          <DiffViewer
            diffs={runtimeData?.diffs}
            changelog={runtimeData?.changelog}
            v1Code={runtimeData?.iterations?.[0]?.code || ""}
            v2Code={runtimeData?.iterations?.[1]?.code || ""}
            v3Code={runtimeData?.iterations?.[2]?.code || ""}
            v1Score={runtimeData?.iterations?.[0]?.score || 52}
            v2Score={runtimeData?.iterations?.[1]?.score || 86}
            v3Score={runtimeData?.iterations?.[2]?.score || 100}
          />
        )}

        {/* Tab 4: Test Generation & Runner Tab */}
        {activeTab === "tests" && (
          <TestExecutionPanel
            testDetails={currentIteration?.test_details || []}
            generationMeta={runtimeData?.test_generation}
            activeVersionLabel={selectedVersion}
          />
        )}

        {/* Tab 5: Critic Analysis Tab */}
        {activeTab === "critic" && (
          <CriticIntelligencePanel
            critique={currentIteration?.critique}
            versionLabel={selectedVersion}
            isResolvedInNext={!!nextIteration && (!nextIteration.critique?.failure_type || nextIteration.critique?.failure_type === "None")}
            nextVersionLabel={nextIteration?.version || "Next"}
          />
        )}

        {/* Tab 6: Zero-Knowledge Verification Status Tab */}
        {activeTab === "zk" && (
          <ZkTelemetryPanel zkTelemetry={runtimeData?.zk_telemetry} />
        )}

        {/* Tab 7: Agent Network & Collective Memory Tab */}
        {activeTab === "agent2" && (
          <Agent2MemoryTab initialData={agent2Data} />
        )}
      </main>
    </div>
  );
}
