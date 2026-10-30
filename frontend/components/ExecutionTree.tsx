"use client";

import React, { useState } from "react";
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
} from "lucide-react";

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
  logs?: string[];
}

interface ExecutionTreeProps {
  iterations: IterationData[];
  onSelectIteration?: (version: string) => void;
  selectedVersion?: string;
}

export default function ExecutionTree({
  iterations,
  onSelectIteration,
  selectedVersion: controlledSelected,
}: ExecutionTreeProps) {
  const [internalSelected, setInternalSelected] = useState<string>(
    iterations[iterations.length - 1]?.version || "V3"
  );

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

  return (
    <div className="flex flex-col space-y-6">
      {/* DAG / Step-by-Step Flowchart */}
      <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-5 shadow-2xl backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <GitCommit className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              Evolution History & Milestone Trajectory
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800">
            {iterations.length} Cycles Recorded
          </span>
        </div>

        {/* Node DAG Timeline (Dynamically responsive for any number of versions) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 relative">
          {iterations.map((item, index) => {
            const isSelected = item.version === activeVersion;
            const isLast = index === iterations.length - 1;
            const failureType =
              item.critique?.failure_type ||
              (item.failed_tests && item.failed_tests.length > 0
                ? item.failed_tests[0]
                : "Verified Clean");

            return (
              <div key={item.version} className="relative">
                <button
                  type="button"
                  onClick={() => handleSelect(item.version)}
                  className={`w-full text-left transition-all duration-200 rounded-xl p-4 border ${
                    isSelected
                      ? "bg-slate-800/90 border-cyan-500 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-500/50"
                      : "bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-850"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs px-2 py-0.5 rounded font-bold bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
                        {item.version}
                      </span>
                      <span className="text-xs font-medium text-slate-300 truncate max-w-[130px]">
                        {item.label || `Iteration ${item.version}`}
                      </span>
                    </div>
                    <span
                      className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full border ${getScoreColor(
                        item.score
                      )}`}
                    >
                      {item.score.toFixed(1)}
                    </span>
                  </div>

                  <div className="w-full bg-slate-800 rounded-full h-1.5 mb-3 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 rounded-full ${getScoreBarColor(
                        item.score
                      )}`}
                      style={{ width: `${Math.min(100, item.score)}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
                    <div className="flex items-center space-x-1.5 truncate">
                      {item.failed_tests && item.failed_tests.length > 0 ? (
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                      ) : (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      )}
                      <span
                        className="font-mono text-[11px] truncate text-slate-300 max-w-[140px]"
                        title={failureType}
                      >
                        {failureType}
                      </span>
                    </div>
                    <span className="text-[11px] font-mono text-slate-400">
                      {item.passed}/{item.total} tests
                    </span>
                  </div>
                </button>

                {!isLast && (
                  <div className="hidden lg:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10 text-slate-600 bg-slate-900 rounded-full p-1 border border-slate-800">
                    <ArrowRight className="w-3 h-3 text-cyan-400" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Iteration Detail Inspector */}
      {activeData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Critic Diagnostic */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-4 shadow-xl">
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
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">
                    Detected Failure Signature
                  </span>
                  <p className="font-mono text-rose-400 font-semibold text-xs mt-0.5">
                    {activeData.critique?.failure_type || "None (All Constraints Satisfied)"}
                  </p>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">
                    Root Cause Diagnosis
                  </span>
                  <p className="text-slate-300 mt-1 leading-relaxed text-[11px]">
                    {activeData.critique?.root_cause || "Complete correctness achieved across test suites."}
                  </p>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">
                    Actionable Directive
                  </span>
                  <p className="text-cyan-300/90 mt-1 leading-relaxed text-[11px] bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 font-mono">
                    {activeData.critique?.fix_instruction || "Maintain current architecture; ready for on-chain settlement."}
                  </p>
                </div>
              </div>
            </div>

            {/* Cryptographic Trace Commitment */}
            <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-4 shadow-xl text-xs space-y-2">
              <div className="flex items-center space-x-2 text-slate-300 font-semibold mb-1">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>Cryptographic State Commitment</span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-500 block">SHA-256 State Hash</span>
                <p className="font-mono text-[10px] text-cyan-400 break-all bg-slate-950 p-1.5 rounded border border-slate-800 mt-0.5">
                  {activeData.trace_hash_hex || "0xca23d830af80f18911a97644..."}
                </p>
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-500 block">BN254 Scalar Commitment</span>
                <p className="font-mono text-[10px] text-purple-400 break-all bg-slate-950 p-1.5 rounded border border-slate-800 mt-0.5 truncate">
                  {activeData.trace_hash_zk || "248-bit scalar safe integer"}
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Candidate Code Viewer */}
          <div className="lg:col-span-2 bg-[#0b0f17] border border-slate-800/80 rounded-xl p-4 shadow-xl flex flex-col">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Code2 className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                  Candidate Implementation ({activeData.version})
                </span>
              </div>
              <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                Score: {activeData.score.toFixed(1)} / 100
              </span>
            </div>

            <div className="flex-1 bg-slate-950 rounded-lg p-3 border border-slate-800/80 font-mono text-[11px] text-slate-200 overflow-x-auto max-h-[500px]">
              <pre className="whitespace-pre">
                <code>{activeData.code || "# No code recorded for this iteration"}</code>
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
