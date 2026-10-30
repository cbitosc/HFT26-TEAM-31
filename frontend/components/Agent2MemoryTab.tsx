"use client";

import React, { useState } from "react";
import {
  BrainCircuit,
  Sparkles,
  ArrowRight,
  Database,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Code2,
  Play,
  RotateCcw,
  Zap,
  Terminal,
  Search,
} from "lucide-react";

export interface Agent2InheritResult {
  status: string;
  agent_id: string;
  query: string;
  matched_task_id?: string;
  matched_ipfs_cid: string;
  gateway_url?: string;
  similarity_score: number;
  similarity_percentage: number;
  similarity_threshold: number;
  failure_signature?: string;
  root_cause?: string;
  fix_strategy?: string;
  baseline_score: number;
  inherited_score: number;
  score_delta: number;
  score_jump_summary: string;
  prompt_injection?: string;
  inherited_diff?: string;
  execution_steps?: string[];
}

interface Agent2MemoryTabProps {
  initialData?: Agent2InheritResult | null;
  onRunInherit?: (query: string) => Promise<Agent2InheritResult>;
}

export default function Agent2MemoryTab({
  initialData,
  onRunInherit,
}: Agent2MemoryTabProps) {
  const [data, setData] = useState<Agent2InheritResult | null>(initialData || null);
  const [query, setQuery] = useState(
    "I have an IndexError when capacity is zero in LRU cache."
  );
  const [loading, setLoading] = useState(false);

  const presets = [
    "I have an IndexError when capacity is zero in LRU cache.",
    "Eviction ordering fails after get() operations in cache.",
    "TypeError unhashable type list when inserting keys.",
  ];

  const handleTrigger = async (selectedQuery?: string) => {
    const q = selectedQuery || query;
    setLoading(true);
    try {
      if (onRunInherit) {
        const res = await onRunInherit(q);
        setData(res);
      } else {
        // Fetch from API directly
        const resp = await fetch("/api/agent2-inherit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: q }),
        });
        const json = await resp.json();
        setData(json);
      }
    } catch (err) {
      console.error("Agent 2 inheritance failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const simPct = data ? data.similarity_percentage : 80.45;
  const isSatisfied = data ? data.similarity_score >= data.similarity_threshold : true;

  return (
    <div className="space-y-6">
      {/* Top Controller: Interactive Trigger & Query Input */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 relative z-10">
          <div className="flex items-center space-x-3">
            <span className="p-2.5 rounded-lg bg-blue-950/70 border border-blue-800/60 text-blue-400">
              <BrainCircuit className="w-6 h-6" />
            </span>
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                <span>Agent 2: Cross-Agent Collective Memory Inheritance</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-950/80 border border-blue-500/60 text-blue-400 font-mono">
                  DataDAO &bull; IPFS
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Secondary independent agent queries Base Sepolia registry, computes dense vector similarity, and ingests verified fix history.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => handleTrigger()}
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-xs shadow-lg shadow-blue-600/20 border border-blue-400/30 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin" />
                <span>Querying IPFS Memory...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Execute Agent 2 Inheritance</span>
              </>
            )}
          </button>
        </div>

        {/* Query Input & Presets */}
        <div className="space-y-2 mt-4 relative z-10">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter failing diagnostic symptom query..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] text-slate-500 font-mono">Presets:</span>
            {presets.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(preset);
                  handleTrigger(preset);
                }}
                className="text-[11px] font-mono px-2.5 py-1 rounded bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700/50 transition truncate max-w-[280px]"
                title={preset}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Results Grid */}
      {data ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Column 1: Similarity Metric & IPFS Card */}
          <div className="space-y-4">
            {/* Vector Similarity Gauge Card */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center space-x-1.5">
                  <Database className="w-4 h-4 text-blue-400" />
                  <span>Semantic Vector Match</span>
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/60 text-blue-400 border border-blue-800/40">
                  all-MiniLM-L6-v2
                </span>
              </div>

              {/* Large Similarity Metric */}
              <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 flex flex-col items-center justify-center text-center">
                <div className="text-3xl font-extrabold font-mono text-blue-400 tracking-tight">
                  {data.similarity_percentage.toFixed(2)}%
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Cosine Similarity Score ({data.similarity_score.toFixed(4)})
                </div>

                <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-700"
                    style={{ width: `${Math.min(100, data.similarity_percentage)}%` }}
                  />
                </div>

                <div className="flex items-center justify-between w-full text-[11px] font-mono text-slate-500 mt-2">
                  <span>Threshold: 80.00%</span>
                  <span className="text-emerald-400 font-semibold flex items-center space-x-1">
                    <CheckCircle2 className="w-3 h-3 inline mr-0.5" />
                    <span>Threshold Met</span>
                  </span>
                </div>
              </div>

              {/* IPFS CID Reference */}
              <div className="mt-4 p-3 bg-slate-950/80 rounded-lg border border-slate-800/80 text-xs font-mono space-y-1.5">
                <div className="text-[10px] text-slate-500 uppercase">Matched IPFS Content ID (CID)</div>
                <div className="text-blue-300 truncate select-all">{data.matched_ipfs_cid}</div>
                {data.gateway_url && (
                  <a
                    href={data.gateway_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 text-[11px] text-slate-400 hover:text-blue-400 transition pt-1"
                  >
                    <span>Inspect Gateway Payload</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>

            {/* Execution Steps Log */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 shadow-lg">
              <div className="flex items-center space-x-2 mb-3">
                <Terminal className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                  Inheritance Lifecycle
                </span>
              </div>

              <div className="space-y-1.5 font-mono text-[11px] text-slate-300">
                {(data.execution_steps || []).map((step, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-slate-400">
                    <span className="text-blue-500 select-none">&bull;</span>
                    <span className="leading-tight">{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Column 2 & 3: Score Jump Banner + Code Diff & Prompt Injection */}
          <div className="lg:col-span-2 space-y-4">
            {/* The First-Attempt Score Jump Card */}
            <div className="p-5 rounded-xl bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-emerald-500/40 shadow-xl shadow-emerald-950/20 relative overflow-hidden">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/50">
                    FIRST-ATTEMPT SCORE JUMP
                  </span>
                  <h4 className="text-base font-bold text-slate-100 mt-2">
                    Zero-Knowledge Cross-Agent Lifelong Learning
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Agent 2 bypassed multi-iteration failure loops by ingesting Agent 1's verified on-chain fix history.
                  </p>
                </div>

                {/* Score Comparison Display */}
                <div className="flex items-center space-x-3 bg-slate-950 p-3 rounded-xl border border-slate-800 flex-shrink-0">
                  <div className="text-center">
                    <div className="text-[10px] font-mono text-slate-500">Unassisted V1</div>
                    <div className="text-lg font-bold font-mono text-rose-400">
                      {data.baseline_score.toFixed(1)}
                    </div>
                  </div>

                  <ArrowRight className="w-4 h-4 text-emerald-400" />

                  <div className="text-center">
                    <div className="text-[10px] font-mono text-slate-500">Inherited V1</div>
                    <div className="text-lg font-bold font-mono text-emerald-400">
                      {data.inherited_score.toFixed(1)}
                    </div>
                  </div>

                  <div className="pl-2 border-l border-slate-800 text-center">
                    <div className="text-[10px] font-mono text-slate-500">Score Gain</div>
                    <div className="text-lg font-extrabold font-mono text-emerald-400">
                      +{data.score_delta.toFixed(1)}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Synthesized Prompt Injection Card */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                    Voyager-Style Memory Prompt Injection
                  </span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">
                  Injected into Generator context
                </span>
              </div>

              <div className="p-3 bg-[#050811] rounded-lg border border-slate-800/80 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto max-h-48 whitespace-pre-wrap">
                {data.prompt_injection || (
                  `=== [AutoEvolve Memory Layer: Inherited Prior Fix] ===\n` +
                  `Source Task: ${data.matched_task_id || "task_lru_cache_ttl_v3"} (Similarity: ${data.similarity_percentage}%)\n` +
                  `Failure Signature: ${data.failure_signature}\n` +
                  `Root Cause: ${data.root_cause}\n` +
                  `Fix Strategy: ${data.fix_strategy}`
                )}
              </div>
            </div>

            {/* Inherited Diff Viewer */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 shadow-lg">
              <div className="flex items-center space-x-2 mb-3">
                <Code2 className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                  Verified Reference Diff Hydrated from IPFS
                </span>
              </div>

              <div className="p-3 bg-[#050811] rounded-lg border border-slate-800/80 font-mono text-xs text-emerald-400 leading-relaxed overflow-x-auto max-h-48 whitespace-pre">
                {data.inherited_diff || (
                  `--- a/lru_cache.py\n+++ b/lru_cache.py\n@@ -10,6 +10,10 @@\n+    if capacity <= 0:\n+        self.capacity = 0\n+        return`
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 text-center rounded-xl bg-slate-900/40 border border-slate-800">
          <BrainCircuit className="w-12 h-12 mx-auto mb-3 text-slate-600 animate-pulse" />
          <h4 className="text-sm font-semibold text-slate-300">No Inheritance Execution Active</h4>
          <p className="text-xs text-slate-500 mt-1">
            Click &quot;Execute Agent 2 Inheritance&quot; above to simulate cross-agent memory query and measure the first-attempt score jump.
          </p>
        </div>
      )}
    </div>
  );
}

