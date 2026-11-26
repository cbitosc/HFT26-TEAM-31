"use client";

import React, { useState } from "react";
import {
  GitCompare,
  FileCode,
  Sparkles,
  ArrowRight,
  Plus,
  Minus,
  CheckCircle,
  Copy,
  Check,
} from "lucide-react";

export interface DiffViewerProps {
  diffs?: {
    v1_v2?: string;
    v2_v3?: string;
    [key: string]: string | undefined;
  };
  changelog?: string;
  v1Code?: string;
  v2Code?: string;
  v3Code?: string;
  v1Score?: number;
  v2Score?: number;
  v3Score?: number;
  v1Architecture?: string;
  v2Architecture?: string;
  v3Architecture?: string;
}

export default function DiffViewer({
  diffs,
  changelog,
  v1Code = "",
  v2Code = "",
  v3Code = "",
  v1Score = 52,
  v2Score = 86,
  v3Score = 100,
  v1Architecture,
  v2Architecture,
  v3Architecture,
}: DiffViewerProps) {
  const [activeDiffKey, setActiveDiffKey] = useState<"v1_v2" | "v2_v3">("v1_v2");
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<"side-by-side" | "unified">("side-by-side");

  const leftCode = activeDiffKey === "v1_v2" ? v1Code : v2Code;
  const rightCode = activeDiffKey === "v1_v2" ? v2Code : v3Code;
  const leftVer = activeDiffKey === "v1_v2" ? "V1" : "V2";
  const rightVer = activeDiffKey === "v1_v2" ? "V2" : "V3";
  const leftScore = activeDiffKey === "v1_v2" ? v1Score : v2Score;
  const rightScore = activeDiffKey === "v1_v2" ? v2Score : v3Score;
  const scoreGain = (rightScore - leftScore).toFixed(1);

  const rawDiff =
    activeDiffKey === "v1_v2"
      ? diffs?.v1_v2 || "# No diff generated for V1 -> V2"
      : diffs?.v2_v3 || "# No diff generated for V2 -> V3";

  const handleCopy = () => {
    navigator.clipboard.writeText(rawDiff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to render side-by-side line pairs
  const renderSideBySide = () => {
    const leftLines = leftCode ? leftCode.split("\n") : [];
    const rightLines = rightCode ? rightCode.split("\n") : [];
    const maxLines = Math.max(leftLines.length, rightLines.length);

    const rows = [];
    for (let i = 0; i < maxLines; i++) {
      const leftLine = leftLines[i] ?? "";
      const rightLine = rightLines[i] ?? "";
      const isDiff = leftLine !== rightLine;

      rows.push(
        <div key={i} className="grid grid-cols-2 text-[11px] font-mono hover:bg-slate-800/30">
          {/* Left Column (Older Version) */}
          <div
            className={`flex items-start border-r border-slate-800 px-3 py-0.5 ${
              isDiff && leftLine
                ? "bg-rose-950/20 text-rose-300"
                : "text-slate-400"
            }`}
          >
            <span className="w-8 select-none text-slate-600 text-right pr-3 font-mono text-[10px]">
              {i < leftLines.length ? i + 1 : ""}
            </span>
            <span className="w-4 select-none text-center">
              {isDiff && leftLine ? "-" : " "}
            </span>
            <span className="whitespace-pre overflow-x-auto flex-1">{leftLine}</span>
          </div>

          {/* Right Column (Refined Version) */}
          <div
            className={`flex items-start px-3 py-0.5 ${
              isDiff && rightLine
                ? "bg-emerald-950/20 text-emerald-300 font-semibold"
                : "text-slate-300"
            }`}
          >
            <span className="w-8 select-none text-slate-600 text-right pr-3 font-mono text-[10px]">
              {i < rightLines.length ? i + 1 : ""}
            </span>
            <span className="w-4 select-none text-center text-emerald-400">
              {isDiff && rightLine ? "+" : " "}
            </span>
            <span className="whitespace-pre overflow-x-auto flex-1">{rightLine}</span>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-[#050811] divide-y divide-slate-900 overflow-x-auto max-h-[520px]">
        {rows}
      </div>
    );
  };

  // Helper to render unified diff
  const renderUnified = () => {
    const lines = rawDiff.split("\n");
    return (
      <div className="bg-[#050811] p-4 font-mono text-xs overflow-x-auto max-h-[520px]">
        {lines.map((line, idx) => {
          let lineStyle = "text-slate-300";
          let bgStyle = "";
          let icon = null;

          if (line.startsWith("+") && !line.startsWith("+++")) {
            lineStyle = "text-emerald-400 font-medium";
            bgStyle = "bg-emerald-950/25";
            icon = <Plus className="w-3 h-3 text-emerald-400 mr-2 inline" />;
          } else if (line.startsWith("-") && !line.startsWith("---")) {
            lineStyle = "text-rose-400";
            bgStyle = "bg-rose-950/25";
            icon = <Minus className="w-3 h-3 text-rose-400 mr-2 inline" />;
          } else if (line.startsWith("@")) {
            lineStyle = "text-blue-400 font-semibold";
            bgStyle = "bg-blue-950/20";
          }

          return (
            <div key={idx} className={`py-0.5 px-2 rounded-sm flex items-center ${bgStyle} ${lineStyle}`}>
              <span className="w-8 text-slate-600 text-right pr-2 select-none text-[10px]">
                {idx + 1}
              </span>
              <span className="font-mono whitespace-pre">{line}</span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Version Switcher */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-xl backdrop-blur-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <GitCompare className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                Incremental Code Diff & Critic Changelog
              </h3>
              <p className="text-xs text-slate-400">
                Side-by-side syntax comparison between progressive agent iterations
              </p>
            </div>
          </div>

          {/* Action Tabs & Controls */}
          <div className="flex items-center space-x-2">
            <div className="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              <button
                type="button"
                onClick={() => setActiveDiffKey("v1_v2")}
                className={`text-xs px-3 py-1.5 rounded-md font-mono font-medium transition-all ${
                  activeDiffKey === "v1_v2"
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                V1 vs V2
              </button>
              <button
                type="button"
                onClick={() => setActiveDiffKey("v2_v3")}
                className={`text-xs px-3 py-1.5 rounded-md font-mono font-medium transition-all ${
                  activeDiffKey === "v2_v3"
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                V2 vs V3
              </button>
            </div>

            <div className="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              <button
                type="button"
                onClick={() => setViewMode("side-by-side")}
                className={`text-xs px-2.5 py-1.5 rounded-md font-medium transition-all ${
                  viewMode === "side-by-side"
                    ? "bg-slate-800 text-slate-200"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Split
              </button>
              <button
                type="button"
                onClick={() => setViewMode("unified")}
                className={`text-xs px-2.5 py-1.5 rounded-md font-medium transition-all ${
                  viewMode === "unified"
                    ? "bg-slate-800 text-slate-200"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Unified
              </button>
            </div>

            <button
              type="button"
              onClick={handleCopy}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
              title="Copy Unified Diff"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Score Delta Pill */}
        <div className="mt-4 flex items-center justify-between p-3 rounded-lg bg-slate-950/70 border border-slate-800/80">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs font-bold text-slate-400">
              {leftVer} (Score: {leftScore.toFixed(1)})
            </span>
            <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
            <span className="font-mono text-xs font-bold text-emerald-400">
              {rightVer} (Score: {rightScore.toFixed(1)})
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">Measurable Gain:</span>
            <span className="font-mono text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-500/50 text-emerald-400">
              +{scoreGain} pts
            </span>
          </div>
        </div>
      </div>

      {/* Main Diff Code Viewer */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl shadow-lg overflow-hidden">
        {/* Header bar */}
        <div className="grid grid-cols-2 px-4 py-2.5 bg-slate-950 border-b border-slate-800 text-xs font-mono font-medium text-slate-400">
          <div className="flex items-center space-x-2">
            <FileCode className="w-4 h-4 text-rose-400" />
            <span>
              {leftVer} Candidate ({activeDiffKey === "v1_v2" ? (v1Architecture || "Initial Prototype") : (v2Architecture || "Refined Architecture")})
            </span>
          </div>
          <div className="flex items-center space-x-2 border-l border-slate-800 pl-4">
            <FileCode className="w-4 h-4 text-emerald-400" />
            <span>
              {rightVer} Candidate ({activeDiffKey === "v1_v2" ? (v2Architecture || "Refined Architecture") : (v3Architecture || "Production Target")})
            </span>
          </div>
        </div>

        {/* Code Content */}
        {viewMode === "side-by-side" ? renderSideBySide() : renderUnified()}
      </div>

      {/* Automated Critic Changelog Section */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg">
        <div className="flex items-center space-x-2 mb-3">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Automated Critic Changelog & Architectural Reflection
          </h4>
        </div>

        <div className="p-4 bg-slate-950 rounded-lg border border-slate-800/80 font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
          {changelog || (
            `### AutoEvolve Multi-Stage Evolution Changelog\n\n` +
            `* **V1 -> V2 (Eviction & Recency Refactoring)**:\n` +
            `  - Replaced O(N) list-based key storage with collections.OrderedDict\n` +
            `  - Implemented automatic MRU promotion on cache.get(key) via move_to_end()\n` +
            `  - Added initial capacity <= 0 safety boundary guard\n\n` +
            `* **V2 -> V3 (Type Safety & Doubly Linked List Architecture)**:\n` +
            `  - Engineered explicit class Node doubly linked list with head/tail sentinels\n` +
            `  - Defensively guarded against mutable/unhashable inputs (lists, dicts) with try/except hash(key)\n` +
            `  - Added Google-style docstrings and complete static typing annotations\n` +
            `  - Satisfied all 10 hidden unit test suites within <0.08s throughput latency`
          )}
        </div>
      </div>
    </div>
  );
}

