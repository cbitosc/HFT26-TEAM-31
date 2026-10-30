"use client";

import React, { useState, useRef } from "react";
import {
  GitCommit,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  Code2,
  Terminal,
  Cpu,
  ShieldCheck,
  ChevronRight,
  Layers,
  Sparkles,
  TrendingUp,
  FileCode2,
  Info,
  ExternalLink,
  Zap,
  Activity,
  RotateCcw,
  MousePointerClick,
} from "lucide-react";

export interface PromptData {
  system_role?: string;
  directive?: string;
  commitment_hash?: string;
  temperature?: number;
  target_constraints?: string[];
}

export interface DiffStatsData {
  added: number;
  removed: number;
  summary: string;
}

export interface IterationData {
  version: string;
  label?: string;
  architecture?: string;
  score: number;
  passed: number;
  total: number;
  failed_tests?: string[];
  code?: string;
  trace_hash_hex?: string;
  trace_hash_zk?: string;
  prompt?: PromptData;
  critique?: {
    failure_type?: string;
    severity?: string;
    root_cause?: string;
    fix_instruction?: string;
    failed_tests?: string[];
  };
  sub_scores?: {
    correctness?: number;
    efficiency?: number;
    safety?: number;
    quality?: number;
  };
  test_details?: any[];
  diff_stats?: DiffStatsData;
  logs?: string[];
}

interface ExecutionTreeProps {
  iterations: IterationData[];
  onSelectIteration?: (version: string) => void;
  selectedVersion?: string;
}

interface HoveredNode {
  type: "prompt" | "version" | "critique";
  iteration: IterationData;
  nodeName: string;
  position: { x: number; y: number };
}

interface HoveredEdge {
  type: "feedforward" | "feedback";
  from: string;
  to: string;
  summary: string;
  details: string;
  scoreDelta?: number;
  position: { x: number; y: number };
}

export default function ExecutionTree({
  iterations,
  onSelectIteration,
  selectedVersion: controlledSelected,
}: ExecutionTreeProps) {
  const [internalSelected, setInternalSelected] = useState<string>(
    iterations[iterations.length - 1]?.version || "V3"
  );
  const [hoveredNode, setHoveredNode] = useState<HoveredNode | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<HoveredEdge | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  const activeVersion = controlledSelected || internalSelected;
  const activeData =
    iterations.find((it) => it.version === activeVersion) || iterations[0];

  const handleSelect = (ver: string) => {
    setInternalSelected(ver);
    if (onSelectIteration) onSelectIteration(ver);
  };

  const getScoreColor = (score: number) => {
    if (score >= 95) return "text-emerald-400 bg-emerald-950/60 border-emerald-500/50";
    if (score >= 80) return "text-amber-400 bg-amber-950/60 border-amber-500/50";
    return "text-rose-400 bg-rose-950/60 border-rose-500/50";
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 95) return "bg-emerald-500";
    if (score >= 80) return "bg-amber-500";
    return "bg-rose-500";
  };

  if (!iterations || iterations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-slate-900/40 rounded-xl border border-slate-800 text-slate-400">
        <Layers className="w-12 h-12 mb-3 text-slate-600 animate-pulse" />
        <p className="text-base font-medium">No execution trace data loaded</p>
        <p className="text-xs text-slate-500 mt-1">
          Trigger an agent loop run to visualize the dynamic execution DAG.
        </p>
      </div>
    );
  }

  const getPromptForIteration = (it: IterationData, idx: number): PromptData => {
    return it.prompt || {
      system_role: idx === 0 ? "Software Engineer (Prototype)" : idx === 1 ? "Algorithmic Systems Engineer" : "Principal Architect",
      directive: idx === 0
        ? "Implement initial working prototype with core functional requirements."
        : idx === 1
        ? "Address V1 failure critique: eliminate boundary bottlenecks and handle unhashable types."
        : "Deliver production architecture with full type annotations, defensive guards, and complete invariants.",
      commitment_hash: it.trace_hash_hex ? `0x${it.trace_hash_hex.slice(0, 16)}...` : `0xprompt_${idx + 1}`,
      temperature: 0.0,
      target_constraints: idx === 0 ? ["Basic storage", "Handle operations"] : idx === 1 ? ["O(1) Throughput", "Type defensive check"] : ["Production Class", "100% Type Safety"],
    };
  };

  const getCritiqueForIteration = (it: IterationData) => {
    return it.critique || {
      failure_type: it.failed_tests && it.failed_tests.length > 0 ? it.failed_tests[0] : "Verified Clean",
      root_cause: it.failed_tests && it.failed_tests.length > 0
        ? `Failed tests: ${it.failed_tests.join(", ")}`
        : "All hidden invariant test suites passed successfully with O(1) complexity.",
      fix_instruction: "No further revisions needed. Code ready for ZK attestation.",
    };
  };

  const getDiffStatsForIteration = (it: IterationData, idx: number): DiffStatsData => {
    return it.diff_stats || {
      added: idx === 0 ? 26 : idx === 1 ? 18 : 42,
      removed: idx === 0 ? 0 : idx === 1 ? 12 : 15,
      summary: idx === 0
        ? "Initial baseline prototype"
        : idx === 1
        ? "Refactored storage and boundary handling (+34 pts)"
        : "Engineered production architecture with strict typing and complete invariant safety (+14 pts)",
    };
  };

  return (
    <div className="flex flex-col space-y-6" ref={containerRef}>
      {/* Visual Execution DAG Tree Container */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-2xl backdrop-blur-md relative">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-blue-950/80 border border-blue-800/60 text-blue-400">
              <GitCommit className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100 flex items-center space-x-2">
                <span>Interactive Agent Execution DAG & Feedback Cycles</span>
                <span className="text-[10px] font-mono font-normal px-2 py-0.5 rounded-full bg-blue-950 text-blue-300 border border-blue-800/80">
                  Panel 1 &bull; Live Telemetry
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Hover over Prompt Nodes (<span className="text-blue-400 font-mono">P</span>), Version Nodes (<span className="text-emerald-400 font-mono">V</span>), or Critique Nodes (<span className="text-purple-400 font-mono">C</span>) to inspect live inputs and transitions.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs font-mono">
            <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>{iterations.length} Iterations</span>
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
              Score Gain: +{(iterations[iterations.length - 1].score - iterations[0].score).toFixed(1)} pts
            </span>
          </div>
        </div>

        {/* The Multi-Stage Progression Timeline */}
        <div className="space-y-6">
          {iterations.map((item, idx) => {
            const isSelected = item.version === activeVersion;
            const prompt = getPromptForIteration(item, idx);
            const critique = getCritiqueForIteration(item);
            const diffStats = getDiffStatsForIteration(item, idx);
            const isLast = idx === iterations.length - 1;
            const nextItem = !isLast ? iterations[idx + 1] : null;
            const scoreDelta = nextItem ? Math.round(nextItem.score - item.score) : 0;

            return (
              <div key={item.version} className="relative">
                {/* Horizontal Step Grid */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all">

                  {/* COLUMN 1: PROMPT NODE (P) */}
                  <div className="md:col-span-3 flex items-center space-x-3">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredNode({
                          type: "prompt",
                          iteration: item,
                          nodeName: `Prompt Node (P${idx + 1})`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredNode(null)}
                      className="cursor-pointer group flex-shrink-0"
                    >
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-950 to-indigo-900 border border-blue-600/60 group-hover:border-blue-400 group-hover:scale-105 transition flex items-center justify-center text-blue-300 font-mono font-bold text-xs shadow-md shadow-blue-900/40">
                        P{idx + 1}
                      </div>
                    </div>

                    <div className="truncate">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-xs font-semibold text-slate-200 truncate">
                          {prompt.system_role}
                        </span>
                      </div>
                      <div className="text-[10px] font-mono text-slate-500 truncate max-w-[150px]">
                        {prompt.commitment_hash}
                      </div>
                    </div>
                  </div>

                  {/* EDGE 1: P -> V CONNECTOR */}
                  <div className="md:col-span-1 flex flex-col items-center justify-center">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredEdge({
                          type: "feedforward",
                          from: `P${idx + 1}`,
                          to: item.version,
                          summary: "Prompt Ingestion & LLM Code Generation",
                          details: `Model takes directive "${prompt.directive?.slice(0, 70)}..." and synthesizes candidate code.`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredEdge(null)}
                      className="w-full flex flex-col items-center cursor-pointer group"
                    >
                      <span className="text-[9px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 mb-1 whitespace-nowrap group-hover:border-blue-500 group-hover:text-blue-300 transition">
                        CodeGen
                      </span>
                      <div className="w-full h-[2px] bg-gradient-to-r from-blue-500 via-slate-600 to-emerald-500 relative flex items-center justify-end">
                        <ArrowRight className="w-3.5 h-3.5 text-emerald-400 -mr-1" />
                      </div>
                      <span className="text-[9px] font-mono text-slate-500 mt-1">
                        temp: 0.0
                      </span>
                    </div>
                  </div>

                  {/* COLUMN 2: VERSION CIRCLE (V) */}
                  <div className="md:col-span-3 flex flex-col items-center">
                    <button
                      type="button"
                      onClick={() => handleSelect(item.version)}
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredNode({
                          type: "version",
                          iteration: item,
                          nodeName: item.version,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredNode(null)}
                      className={`w-full p-2.5 rounded-xl border text-left transition-all ${
                        isSelected
                          ? "bg-slate-800/90 border-blue-500 ring-2 ring-blue-500/30 shadow-lg shadow-blue-500/10"
                          : "bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-850"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs px-2 py-0.5 rounded font-bold bg-blue-950/80 text-blue-400 border border-blue-800/60">
                            {item.version}
                          </span>
                          <span className="text-xs font-semibold text-slate-200">
                            {item.architecture || `Cycle ${item.version}`}
                          </span>
                        </div>
                        <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full border ${getScoreColor(item.score)}`}>
                          {item.score.toFixed(1)}
                        </span>
                      </div>

                      <div className="w-full bg-slate-800 rounded-full h-1.5 mb-1.5 overflow-hidden">
                        <div
                          className={`h-full transition-all duration-500 rounded-full ${getScoreBarColor(item.score)}`}
                          style={{ width: `${Math.min(100, item.score)}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                        <span className="flex items-center space-x-1">
                          {item.passed === item.total ? (
                            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <AlertTriangle className="w-3 h-3 text-rose-400" />
                          )}
                          <span>{item.passed}/{item.total} tests passed</span>
                        </span>
                        <span className="text-[10px] text-slate-500">Click to view code</span>
                      </div>
                    </button>
                  </div>

                  {/* EDGE 2: V -> C CONNECTOR */}
                  <div className="md:col-span-1 flex flex-col items-center justify-center">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredEdge({
                          type: "feedforward",
                          from: item.version,
                          to: `C${idx + 1}`,
                          summary: "Subprocess Sandbox Evaluation -> Critic Analysis",
                          details: `Evaluates 10 hidden unit test suites in temporary directory sandbox. Score: ${item.score.toFixed(1)}. Failure traces delivered to Critic.`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredEdge(null)}
                      className="w-full flex flex-col items-center cursor-pointer group"
                    >
                      <span className="text-[9px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 mb-1 whitespace-nowrap group-hover:border-purple-500 group-hover:text-purple-300 transition">
                        Sandbox
                      </span>
                      <div className="w-full h-[2px] bg-gradient-to-r from-emerald-500 via-slate-600 to-purple-500 relative flex items-center justify-end">
                        <ArrowRight className="w-3.5 h-3.5 text-purple-400 -mr-1" />
                      </div>
                      <span className="text-[9px] font-mono text-slate-500 mt-1">
                        10 tests
                      </span>
                    </div>
                  </div>

                  {/* COLUMN 3: CRITIQUE NODE (C) */}
                  <div className="md:col-span-4 flex items-center space-x-3">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredNode({
                          type: "critique",
                          iteration: item,
                          nodeName: `Critic Node (C${idx + 1})`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredNode(null)}
                      className="cursor-pointer group flex-shrink-0"
                    >
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-950 to-violet-900 border border-purple-600/60 group-hover:border-purple-400 group-hover:scale-105 transition flex items-center justify-center text-purple-300 font-mono font-bold text-xs shadow-md shadow-purple-900/40">
                        C{idx + 1}
                      </div>
                    </div>

                    <div className="truncate flex-1">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-xs font-semibold text-rose-300 truncate font-mono">
                          {critique.failure_type || "Verified Invariants"}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 line-clamp-1">
                        {critique.root_cause}
                      </div>
                    </div>
                  </div>
                </div>

                {/* FEEDBACK LOOP CURVE (C_n -> P_n+1) */}
                {!isLast && (
                  <div className="flex items-center justify-center my-2 relative">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredEdge({
                          type: "feedback",
                          from: `C${idx + 1}`,
                          to: `P${idx + 2}`,
                          summary: `Critic Feedback Loop -> Directive Injection (+${scoreDelta} pts Gain)`,
                          details: `Critic diagnoses "${critique.failure_type}" and generates fix directive. Generator ingests advice into next prompt P${idx + 2}. Score advances from ${item.score.toFixed(1)} to ${nextItem?.score.toFixed(1)}.`,
                          scoreDelta: scoreDelta,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredEdge(null)}
                      className="cursor-pointer group flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-950 border border-slate-800 hover:border-purple-500 transition shadow-md"
                    >
                      <RotateCcw className="w-3.5 h-3.5 text-purple-400 animate-spin" style={{ animationDuration: "8s" }} />
                      <span className="text-[10px] font-mono text-purple-300 font-semibold">
                        Feedback Loop: C{idx + 1} &rarr; P{idx + 2} (+{scoreDelta} pts gain)
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">
                        &bull; Diff: +{diffStats.added}/-{diffStats.removed} lines
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* FLOATING HOVER CARD FOR NODES */}
        {hoveredNode && (
          <div
            className="fixed z-50 pointer-events-none transform -translate-x-1/2 -translate-y-full mb-3 w-80 bg-slate-900 border border-blue-500/80 rounded-xl p-3.5 shadow-2xl backdrop-blur-md text-xs transition-opacity duration-150 animate-in fade-in zoom-in-95"
            style={{
              left: `${hoveredNode.position.x}px`,
              top: `${hoveredNode.position.y - 10}px`,
            }}
          >
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
              <span className="font-mono font-bold text-blue-400 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                <span>{hoveredNode.nodeName}</span>
              </span>
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/60">
                {hoveredNode.type}
              </span>
            </div>

            {hoveredNode.type === "prompt" && (
              <div className="space-y-1.5 text-slate-300">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 block">System Role:</span>
                  <p className="font-semibold">{hoveredNode.iteration.prompt?.system_role || "Algorithmic Systems Engineer"}</p>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-slate-500 block">Injected Directive:</span>
                  <p className="text-[11px] text-slate-300 leading-snug font-sans">
                    {hoveredNode.iteration.prompt?.directive || "Address failure critique from sandbox."}
                  </p>
                </div>
                <div className="pt-1 text-[10px] font-mono text-slate-400 flex justify-between">
                  <span>Temperature: 0.0</span>
                  <span className="text-blue-400">Seed: 42</span>
                </div>
              </div>
            )}

            {hoveredNode.type === "version" && (
              <div className="space-y-1.5 text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-500">Benchmark Score:</span>
                  <span className="font-mono font-bold text-emerald-400">{hoveredNode.iteration.score.toFixed(1)} / 100</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-500">Unit Tests Passed:</span>
                  <span className="font-mono">{hoveredNode.iteration.passed} / {hoveredNode.iteration.total}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-500">Architecture:</span>
                  <span className="font-mono text-slate-200">{hoveredNode.iteration.architecture || "Custom"}</span>
                </div>
              </div>
            )}

            {hoveredNode.type === "critique" && (
              <div className="space-y-1.5 text-slate-300">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 block">Failure Type:</span>
                  <p className="font-mono text-rose-300 font-semibold">{hoveredNode.iteration.critique?.failure_type || "None"}</p>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-slate-500 block">Root Cause Diagnosis:</span>
                  <p className="text-[11px] text-slate-300 leading-snug">
                    {hoveredNode.iteration.critique?.root_cause || "All tests satisfied."}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* FLOATING HOVER CARD FOR EDGES */}
        {hoveredEdge && (
          <div
            className="fixed z-50 pointer-events-none transform -translate-x-1/2 -translate-y-full mb-3 w-88 max-w-sm bg-slate-900 border border-purple-500/80 rounded-xl p-3.5 shadow-2xl backdrop-blur-md text-xs transition-opacity duration-150 animate-in fade-in zoom-in-95"
            style={{
              left: `${hoveredEdge.position.x}px`,
              top: `${hoveredEdge.position.y - 10}px`,
            }}
          >
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
              <span className="font-mono font-bold text-purple-400 flex items-center space-x-1.5">
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{hoveredEdge.from} &rarr; {hoveredEdge.to}</span>
              </span>
              {hoveredEdge.scoreDelta !== undefined && hoveredEdge.scoreDelta > 0 && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                  +{hoveredEdge.scoreDelta} pts
                </span>
              )}
            </div>
            <p className="font-semibold text-slate-200 mb-1">{hoveredEdge.summary}</p>
            <p className="text-[11px] text-slate-300 leading-relaxed font-sans">{hoveredEdge.details}</p>
          </div>
        )}
      </div>

      {/* Selected Iteration Detail Inspector */}
      {activeData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Critic Diagnostic & Sandbox Output */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-purple-300">
                    Constitutional Critic Diagnosis
                  </span>
                </div>
                <span className="text-[10px] font-mono bg-purple-950/80 text-purple-400 px-2 py-0.5 rounded border border-purple-800/60 font-semibold">
                  Zero Code Leakage
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-slate-500 font-mono text-[11px]">Failure Type:</span>
                  <div className="mt-0.5 font-mono text-rose-300 bg-rose-950/30 px-2 py-1 rounded border border-rose-900/40">
                    {activeData.critique?.failure_type || "No unhandled failure detected"}
                  </div>
                </div>

                <div>
                  <span className="text-slate-500 font-mono text-[11px]">Root Cause:</span>
                  <p className="mt-0.5 text-slate-300 leading-relaxed bg-slate-950/50 p-2 rounded border border-slate-800/60 font-sans">
                    {activeData.critique?.root_cause || "All test invariants satisfied in sandbox environment."}
                  </p>
                </div>

                <div>
                  <span className="text-slate-500 font-mono text-[11px]">Fix Instruction:</span>
                  <p className="mt-0.5 text-slate-300 leading-relaxed bg-slate-950/50 p-2 rounded border border-slate-800/60 font-sans">
                    {activeData.critique?.fix_instruction || "No revision required. Ready for ZK attestation."}
                  </p>
                </div>
              </div>
            </div>

            {/* Test Runner Output */}
            <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Terminal className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                    Subprocess Sandbox Runner
                  </span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">
                  {activeData.passed} passed / {activeData.total} total
                </span>
              </div>

              <div className="space-y-1.5 font-mono text-[11px] max-h-48 overflow-y-auto pr-1">
                {activeData.logs && activeData.logs.length > 0 ? (
                  activeData.logs.map((log, idx) => {
                    const isPass = log.startsWith("PASS");
                    return (
                      <div
                        key={idx}
                        className={`flex items-center space-x-2 px-2 py-1 rounded ${
                          isPass
                            ? "bg-emerald-950/30 text-emerald-400 border border-emerald-900/30"
                            : "bg-rose-950/30 text-rose-300 border border-rose-900/40"
                        }`}
                      >
                        {isPass ? (
                          <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0" />
                        ) : (
                          <XCircle className="w-3 h-3 text-rose-400 flex-shrink-0" />
                        )}
                        <span className="truncate">{log}</span>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-slate-500 italic p-2 font-mono">
                    All tests evaluated in sandbox environment.
                  </div>
                )}
              </div>
            </div>

            {/* Cryptographic State Hashes */}
            <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-sm">
              <div className="flex items-center space-x-2 mb-2">
                <Cpu className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                  BN254 Scalar Field Hash
                </span>
              </div>
              <div className="space-y-1 text-xs">
                <div className="text-slate-400 text-[11px]">Hex Hash (SHA-256):</div>
                <div className="font-mono text-[10px] text-blue-300 bg-slate-950 p-2 rounded border border-slate-800 truncate select-all">
                  {activeData.trace_hash_hex || "0xca23d830af80f189..."}
                </div>
                <div className="text-slate-400 text-[11px] pt-1">Circom 248-Bit Safe Input:</div>
                <div className="font-mono text-[10px] text-purple-300 bg-slate-950 p-2 rounded border border-slate-800 truncate select-all">
                  {activeData.trace_hash_zk || "3492108783281738886631..."}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Candidate Code Viewer */}
          <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 shadow-xl backdrop-blur-sm flex flex-col">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Code2 className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                  Candidate Implementation ({activeData.version})
                </span>
                <span className="text-xs font-mono text-slate-400">
                  &bull; {activeData.architecture || "Class Solution"}
                </span>
              </div>
              <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${getScoreColor(activeData.score)}`}>
                Score: {activeData.score.toFixed(1)} / 100
              </span>
            </div>

            <div className="flex-1 bg-slate-950 p-4 rounded-xl border border-slate-800/80 font-mono text-xs text-slate-200 overflow-x-auto max-h-[560px]">
              <pre className="whitespace-pre">
                <code>{activeData.code || "# No code candidate recorded for this iteration"}</code>
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
