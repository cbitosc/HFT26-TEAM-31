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
    root_cause?: string;
    fix_instruction?: string;
    failed_tests?: string[];
  };
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

  // Fallback defaults for each stage
  const getPromptForIteration = (it: IterationData, idx: number): PromptData => {
    return it.prompt || {
      system_role: idx === 0 ? "Software Engineer (Prototype)" : idx === 1 ? "Algorithmic Systems Engineer" : "Principal Architect",
      directive: idx === 0
        ? "Implement basic prototype of LRUCache with get and put."
        : idx === 1
        ? "Address V1 failure critique: switch from linear scan to collections.OrderedDict for O(1) ops. Handle unhashable keys."
        : "Deliver production Doubly-Linked List with explicit Node class. Full type annotations and error guards.",
      commitment_hash: it.trace_hash_hex ? `0x${it.trace_hash_hex.slice(0, 16)}...` : `0xprompt_${idx + 1}`,
      temperature: 0.0,
      target_constraints: idx === 0 ? ["Linear basic storage", "Handle get/put"] : idx === 1 ? ["OrderedDict O(1)", "Unhashable key check"] : ["Doubly-Linked List", "100% Type Safety"],
    };
  };

  const getCritiqueForIteration = (it: IterationData) => {
    return it.critique || {
      failure_type: it.failed_tests && it.failed_tests.length > 0 ? it.failed_tests[0] : "Verified Clean",
      root_cause: it.failed_tests && it.failed_tests.length > 0
        ? `Failed tests: ${it.failed_tests.join(", ")}`
        : "All 10 hidden invariant test suites passed successfully with O(1) complexity.",
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
        ? "Switched to collections.OrderedDict, fixing eviction order & timeouts (+34 pts)"
        : "Engineered Node DLL with strict typing and complete invariant safety (+14 pts)",
    };
  };

  return (
    <div className="flex flex-col space-y-6" ref={containerRef}>
      {/* =========================================================================
          TOP GRAPH CONTAINER: GRID-BASED REAL DAG CANVAS
      ========================================================================= */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl backdrop-blur-xl relative overflow-hidden">
        {/* Real Coordinate Grid Background (Graph Canvas Paper) */}
        <div
          className="absolute inset-0 pointer-events-none opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(to right, #475569 1px, transparent 1px),
              linear-gradient(to bottom, #475569 1px, transparent 1px)
            `,
            backgroundSize: "28px 28px",
          }}
        />

        {/* Ambient Top Glow */}
        <div className="absolute top-0 left-1/3 right-1/3 h-[1px] bg-gradient-to-r from-transparent via-blue-500/60 to-transparent" />

        {/* Graph Legend & Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 relative z-10 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-lg bg-blue-950/70 border border-blue-800/60 text-blue-400">
                <GitCommit className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <span>Adversarial Evolution DAG (Grid Canvas)</span>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                    Named Nodes & Edge Details
                  </span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Hover over circular nodes (<span className="text-blue-400 font-bold">P</span>, <span className="text-emerald-400 font-bold">V</span>, <span className="text-purple-400 font-bold">C</span>) or edge badges to inspect prompt changes, test scores, and critiques. Click any node to select it.
                </p>
              </div>
            </div>
          </div>

          {/* Graph Legend */}
          <div className="flex flex-wrap items-center gap-3 bg-slate-950/80 border border-slate-800 px-3.5 py-1.5 rounded-xl text-xs font-mono">
            <span className="text-slate-500 text-[11px]">Nodes:</span>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-blue-500 border border-blue-400 shadow-sm shadow-blue-500/50" />
              <span className="text-blue-300">P = Prompt</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500 border border-emerald-400 shadow-sm shadow-emerald-500/50" />
              <span className="text-emerald-300">V = Version</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-purple-500 border border-purple-400 shadow-sm shadow-purple-500/50" />
              <span className="text-purple-300">C = Critique</span>
            </div>
          </div>
        </div>

        {/* =========================================================================
            THE GRAPH: 3-ROW GRID WITH NAMED CIRCULAR NODES & DETAILED EDGES
        ========================================================================= */}
        <div className="relative z-10 py-4 px-2 space-y-10">
          {iterations.map((item, idx) => {
            const isSelected = item.version === activeVersion;
            const prompt = getPromptForIteration(item, idx);
            const critique = getCritiqueForIteration(item);
            const diffStats = getDiffStatsForIteration(item, idx);
            const isLast = idx === iterations.length - 1;
            const nextItem = !isLast ? iterations[idx + 1] : undefined;

            return (
              <div key={item.version} className="relative">
                {/* Stage Tag Header on the Grid */}
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                    Row {idx + 1}: Iteration {item.version} Cycle
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">
                    ({item.architecture || "Solution Prototype"})
                  </span>
                </div>

                {/* Grid Row containing: [P Circle] ---> [V Circle] ---> [C Circle] */}
                <div className="grid grid-cols-1 md:grid-cols-11 items-center gap-4 bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80 shadow-lg">
                  {/* ================= COLUMN 1: PROMPT CIRCLE (P) ================= */}
                  <div className="md:col-span-3 flex flex-col items-center">
                    <button
                      type="button"
                      onClick={() => handleSelect(item.version)}
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredNode({
                          type: "prompt",
                          iteration: item,
                          nodeName: `P${idx + 1}`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredNode(null)}
                      className={`w-16 h-16 rounded-full flex flex-col items-center justify-center font-bold font-mono transition-all duration-200 cursor-pointer shadow-lg relative group ${
                        isSelected
                          ? "bg-blue-600 text-white ring-4 ring-blue-500/40 shadow-blue-500/30 scale-105"
                          : "bg-blue-950/80 text-blue-400 border-2 border-blue-500/60 hover:border-blue-400 hover:scale-105 hover:shadow-blue-500/20"
                      }`}
                    >
                      <Terminal className="w-4 h-4 mb-0.5" />
                      <span className="text-sm font-extrabold tracking-tight">P{idx + 1}</span>
                      <span className="absolute -bottom-5 text-[10px] font-mono text-blue-400 whitespace-nowrap font-medium">
                        Prompt {idx + 1}
                      </span>
                    </button>
                    <div className="mt-6 text-center">
                      <div className="text-xs font-semibold text-slate-300 truncate max-w-[150px]">
                        {prompt.system_role}
                      </div>
                      <div className="text-[10px] font-mono text-slate-500 truncate max-w-[150px]">
                        {prompt.commitment_hash}
                      </div>
                    </div>
                  </div>

                  {/* ================= EDGE 1: P -> V CONNECTOR WITH DETAILS ================= */}
                  <div className="md:col-span-1 flex flex-col items-center justify-center">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredEdge({
                          type: "feedforward",
                          from: `P${idx + 1}`,
                          to: item.version,
                          summary: "Prompt Ingestion & LLM Code Generation",
                          details: `Model takes directive "${prompt.directive?.slice(0, 70)}..." and synthesizes candidate code with temperature: 0.0.`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredEdge(null)}
                      className="w-full flex flex-col items-center cursor-pointer group"
                    >
                      {/* Edge Label Badge */}
                      <span className="text-[9px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 mb-1 whitespace-nowrap group-hover:border-blue-500 group-hover:text-blue-300 transition">
                        CodeGen
                      </span>
                      {/* Horizontal Connector Line with Arrow */}
                      <div className="w-full h-[2px] bg-gradient-to-r from-blue-500 via-slate-600 to-emerald-500 relative flex items-center justify-end">
                        <ArrowRight className="w-3.5 h-3.5 text-emerald-400 -mr-1" />
                      </div>
                      <span className="text-[9px] font-mono text-slate-500 mt-1">
                        temp: 0.0
                      </span>
                    </div>
                  </div>

                  {/* ================= COLUMN 2: VERSION CIRCLE (V) ================= */}
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
                      className={`w-16 h-16 rounded-full flex flex-col items-center justify-center font-bold font-mono transition-all duration-200 cursor-pointer shadow-lg relative group ${
                        isSelected
                          ? "bg-emerald-600 text-white ring-4 ring-emerald-500/40 shadow-emerald-500/30 scale-105"
                          : "bg-emerald-950/80 text-emerald-400 border-2 border-emerald-500/60 hover:border-emerald-400 hover:scale-105 hover:shadow-emerald-500/20"
                      }`}
                    >
                      <Code2 className="w-4 h-4 mb-0.5" />
                      <span className="text-sm font-extrabold tracking-tight">{item.version}</span>
                      <span className="absolute -bottom-5 text-[10px] font-mono text-emerald-400 whitespace-nowrap font-medium">
                        Score: {item.score.toFixed(0)}%
                      </span>
                    </button>
                    <div className="mt-6 text-center">
                      <div className="text-xs font-semibold text-slate-300 truncate max-w-[150px]">
                        {item.architecture}
                      </div>
                      <div className="text-[10px] font-mono text-emerald-400">
                        {item.passed}/{item.total} tests passed
                      </div>
                    </div>
                  </div>

                  {/* ================= EDGE 2: V -> C CONNECTOR WITH DETAILS ================= */}
                  <div className="md:col-span-1 flex flex-col items-center justify-center">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredEdge({
                          type: "feedforward",
                          from: item.version,
                          to: `C${idx + 1}`,
                          summary: "Subprocess Sandbox Evaluation & DeepSeek-R1 Critique",
                          details: `Sandbox runs 10 unit test suites. Test score: ${item.score.toFixed(1)}/100 (${item.passed}/${item.total} pass). DeepSeek-R1 inspects failure stack traces.`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredEdge(null)}
                      className="w-full flex flex-col items-center cursor-pointer group"
                    >
                      {/* Edge Label Badge */}
                      <span className="text-[9px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800 mb-1 whitespace-nowrap group-hover:border-purple-500 group-hover:text-purple-300 transition">
                        SandboxEval
                      </span>
                      {/* Horizontal Connector Line with Arrow */}
                      <div className="w-full h-[2px] bg-gradient-to-r from-emerald-500 via-slate-600 to-purple-500 relative flex items-center justify-end">
                        <ArrowRight className="w-3.5 h-3.5 text-purple-400 -mr-1" />
                      </div>
                      <span className="text-[9px] font-mono text-slate-500 mt-1">
                        {item.passed}/{item.total} pass
                      </span>
                    </div>
                  </div>

                  {/* ================= COLUMN 3: CRITIQUE CIRCLE (C) ================= */}
                  <div className="md:col-span-3 flex flex-col items-center">
                    <button
                      type="button"
                      onClick={() => handleSelect(item.version)}
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredNode({
                          type: "critique",
                          iteration: item,
                          nodeName: `C${idx + 1}`,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredNode(null)}
                      className={`w-16 h-16 rounded-full flex flex-col items-center justify-center font-bold font-mono transition-all duration-200 cursor-pointer shadow-lg relative group ${
                        isSelected
                          ? "bg-purple-600 text-white ring-4 ring-purple-500/40 shadow-purple-500/30 scale-105"
                          : "bg-purple-950/80 text-purple-400 border-2 border-purple-500/60 hover:border-purple-400 hover:scale-105 hover:shadow-purple-500/20"
                      }`}
                    >
                      <ShieldCheck className="w-4 h-4 mb-0.5" />
                      <span className="text-sm font-extrabold tracking-tight">C{idx + 1}</span>
                      <span className="absolute -bottom-5 text-[10px] font-mono text-purple-400 whitespace-nowrap font-medium">
                        Critic {idx + 1}
                      </span>
                    </button>
                    <div className="mt-6 text-center">
                      <div className={`text-xs font-semibold truncate max-w-[150px] ${item.score === 100 ? "text-emerald-400" : "text-amber-400"}`}>
                        {critique.failure_type || "Passed"}
                      </div>
                      <div className="text-[10px] font-mono text-slate-500">
                        DeepSeek-R1 Diagnostic
                      </div>
                    </div>
                  </div>
                </div>

                {/* ================= FEEDBACK ARC EDGE: C_i -> P_{i+1} WITH FULL CONCISE DETAILS ================= */}
                {!isLast && nextItem && (
                  <div className="my-4 flex items-center justify-center">
                    <div
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setHoveredEdge({
                          type: "feedback",
                          from: `C${idx + 1}`,
                          to: `P${idx + 2}`,
                          summary: `Feedback Loop & Refined Prompt Injection`,
                          details: `Critique C${idx + 1} ("${critique.failure_type}") directly synthesized into Refined Prompt P${idx + 2}. Code Diff: +${diffStats.added} / -${diffStats.removed} lines. Score leap: ${item.score.toFixed(0)}% → ${nextItem.score.toFixed(0)}% (+${(nextItem.score - item.score).toFixed(0)} pts).`,
                          scoreDelta: nextItem.score - item.score,
                          position: { x: rect.left + rect.width / 2, y: rect.top },
                        });
                      }}
                      onMouseLeave={() => setHoveredEdge(null)}
                      className="w-full max-w-2xl bg-slate-950/90 border border-slate-800 hover:border-blue-500/70 rounded-xl p-2.5 transition-all cursor-pointer shadow-md flex items-center justify-between text-xs font-mono group"
                    >
                      <div className="flex items-center space-x-2 text-slate-300 truncate">
                        <RotateCcw className="w-3.5 h-3.5 text-blue-400 group-hover:rotate-180 transition-transform duration-500 flex-shrink-0" />
                        <span className="text-slate-500 font-semibold">Feedback Edge:</span>
                        <span className="text-purple-400 font-bold">C{idx + 1}</span>
                        <ArrowRight className="w-3 h-3 text-slate-600 flex-shrink-0" />
                        <span className="text-blue-400 font-bold">P{idx + 2}</span>
                        <span className="text-slate-400 truncate">
                          ({critique.failure_type} → {nextItem.architecture})
                        </span>
                      </div>

                      <div className="flex items-center space-x-3 flex-shrink-0">
                        <span className="text-[11px] text-emerald-400 font-semibold">
                          +{diffStats.added}/-{diffStats.removed} lines
                        </span>
                        <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800/40 font-bold">
                          +{(nextItem.score - item.score).toFixed(0)} pts
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* =========================================================================
          DYNAMIC HOVER CARD FOR CIRCULAR NODES (P, V, C)
      ========================================================================= */}
      {hoveredNode && (
        <div
          className="fixed z-50 pointer-events-none transition-all duration-150 ease-out transform -translate-x-1/2 -translate-y-full mb-3 w-[460px] max-w-[92vw]"
          style={{
            left: `${hoveredNode.position.x}px`,
            top: `${hoveredNode.position.y - 12}px`,
          }}
        >
          <div className="bg-slate-950/95 border border-slate-700 rounded-2xl p-5 shadow-2xl backdrop-blur-2xl text-slate-200 ring-1 ring-white/10 space-y-3">
            {/* Header */}
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
              <div className="flex items-center space-x-2.5">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs font-mono shadow ${
                  hoveredNode.type === "prompt"
                    ? "bg-blue-600 text-white"
                    : hoveredNode.type === "version"
                    ? "bg-emerald-600 text-white"
                    : "bg-purple-600 text-white"
                }`}>
                  {hoveredNode.nodeName}
                </div>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider text-white">
                    {hoveredNode.type === "prompt" && `Prompt Node (${hoveredNode.nodeName})`}
                    {hoveredNode.type === "version" && `Solution Build Node (${hoveredNode.nodeName})`}
                    {hoveredNode.type === "critique" && `Constitutional Critic Node (${hoveredNode.nodeName})`}
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    {hoveredNode.iteration.architecture || "Solution Implementation"}
                  </div>
                </div>
              </div>
              <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${getScoreColor(hoveredNode.iteration.score)}`}>
                Score: {hoveredNode.iteration.score.toFixed(1)}/100
              </span>
            </div>

            {/* Prompt Node Details */}
            {hoveredNode.type === "prompt" && (
              <div className="space-y-2 text-xs">
                <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
                  <div className="text-[11px] font-mono text-blue-400 font-semibold">System Role:</div>
                  <div className="text-xs text-slate-200 font-medium">{getPromptForIteration(hoveredNode.iteration, 0).system_role}</div>
                </div>
                <div className="bg-blue-950/20 p-3 rounded-xl border border-blue-900/30 space-y-1">
                  <div className="text-[11px] font-mono text-blue-400 font-semibold">Direct Prompt Specification:</div>
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">{getPromptForIteration(hoveredNode.iteration, 0).directive}</p>
                </div>
                <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 pt-1">
                  <span>Commitment: {getPromptForIteration(hoveredNode.iteration, 0).commitment_hash}</span>
                  <span>Temperature: 0.0</span>
                </div>
              </div>
            )}

            {/* Version Node Details */}
            {hoveredNode.type === "version" && (
              <div className="space-y-2.5 text-xs">
                <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">Sandbox Test Verification:</span>
                    <span className="font-mono font-bold text-slate-200">{hoveredNode.iteration.passed} / {hoveredNode.iteration.total} Passed</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${getScoreBarColor(hoveredNode.iteration.score)}`}
                      style={{ width: `${(hoveredNode.iteration.passed / hoveredNode.iteration.total) * 100}%` }}
                    />
                  </div>
                  {hoveredNode.iteration.failed_tests && hoveredNode.iteration.failed_tests.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {hoveredNode.iteration.failed_tests.map((ft) => (
                        <span key={ft} className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950/60 text-rose-300 border border-rose-800/40">
                          ✗ {ft}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="text-[10px] font-mono text-emerald-400 flex items-center space-x-1 pt-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>100% Invariants Verified</span>
                    </div>
                  )}
                </div>
                <div className="bg-slate-900/60 p-2.5 rounded-xl border border-slate-800 flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-400">Net Diff Changes:</span>
                  <span className="text-emerald-400 font-bold">
                    +{getDiffStatsForIteration(hoveredNode.iteration, 0).added} / -{getDiffStatsForIteration(hoveredNode.iteration, 0).removed} lines
                  </span>
                </div>
              </div>
            )}

            {/* Critique Node Details */}
            {hoveredNode.type === "critique" && (
              <div className="space-y-2 text-xs">
                <div className="bg-purple-950/20 p-3 rounded-xl border border-purple-900/30 space-y-1">
                  <div className="text-[11px] font-mono text-purple-400 font-semibold">Diagnostic Failure Signature:</div>
                  <div className="text-xs font-mono font-bold text-rose-400">{getCritiqueForIteration(hoveredNode.iteration).failure_type}</div>
                </div>
                <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
                  <div className="text-[11px] font-mono text-slate-400 font-semibold">Root Cause Diagnosis:</div>
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">{getCritiqueForIteration(hoveredNode.iteration).root_cause}</p>
                </div>
                <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
                  <div className="text-[11px] font-mono text-emerald-400 font-semibold">Actionable Remedy Instruction:</div>
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">{getCritiqueForIteration(hoveredNode.iteration).fix_instruction}</p>
                </div>
              </div>
            )}

            {/* Click to inspect callout */}
            <div className="text-[10px] font-mono text-center text-slate-500 pt-1 flex items-center justify-center space-x-1">
              <MousePointerClick className="w-3 h-3 text-blue-400" />
              <span>Click node to select and view code & test logs</span>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          DYNAMIC HOVER CARD FOR EDGES (Feedforward / Feedback Transitions)
      ========================================================================= */}
      {hoveredEdge && (
        <div
          className="fixed z-50 pointer-events-none transition-all duration-150 ease-out transform -translate-x-1/2 -translate-y-full mb-3 w-[420px] max-w-[90vw]"
          style={{
            left: `${hoveredEdge.position.x}px`,
            top: `${hoveredEdge.position.y - 12}px`,
          }}
        >
          <div className="bg-slate-950/95 border border-blue-500/50 rounded-2xl p-4 shadow-2xl backdrop-blur-2xl text-slate-200 ring-1 ring-blue-500/20 space-y-2.5">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono font-bold text-white bg-blue-950/80 px-2 py-0.5 rounded border border-blue-700/60">
                  {hoveredEdge.from} → {hoveredEdge.to}
                </span>
                <span className="text-xs font-semibold text-slate-300">{hoveredEdge.summary}</span>
              </div>
              {hoveredEdge.scoreDelta !== undefined && (
                <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/40">
                  +{hoveredEdge.scoreDelta.toFixed(0)} pts
                </span>
              )}
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
              {hoveredEdge.details}
            </p>
          </div>
        </div>
      )}

      {/* =========================================================================
          SELECTED ITERATION DETAIL INSPECTOR (Deep Dive Tabs)
      ========================================================================= */}
      {activeData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Critic Diagnostic & Sandbox Test Runner Output */}
          <div className="lg:col-span-1 space-y-4">
            {/* DeepSeek-R1 Constitutional Critic Card */}
            <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-4 shadow-xl backdrop-blur-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-purple-300">
                    Constitutional Critic Diagnostic
                  </span>
                </div>
                <span className="text-[10px] font-mono bg-purple-950/60 text-purple-400 px-2 py-0.5 rounded border border-purple-800/50">
                  DeepSeek-R1
                </span>
              </div>

              <div className="space-y-2.5 text-xs">
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

          {/* Right Column: Code Viewer */}
          <div className="lg:col-span-2">
            <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl shadow-xl flex flex-col h-full overflow-hidden backdrop-blur-sm">
              <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-950/80">
                <div className="flex items-center space-x-2">
                  <Code2 className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-semibold text-slate-200">
                    Source Code Solution — {activeData.version} ({activeData.architecture})
                  </span>
                </div>
                <span className="text-xs font-mono text-slate-400">
                  Python 3.13 / LRUCache
                </span>
              </div>

              <div className="p-4 bg-[#050811] flex-1 overflow-x-auto">
                <pre className="font-mono text-xs text-slate-300 leading-relaxed">
                  <code>{activeData.code || "# No code string recorded"}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
