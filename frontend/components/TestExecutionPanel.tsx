"use client";

import React, { useState } from "react";
import {
  TestTube2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Filter,
  ShieldAlert,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

export interface TestCaseDetail {
  id: string;
  category?: string;
  description?: string;
  status: "passed" | "failed";
  elapsed?: number;
  reason?: string;
  error?: string;
  exit_code?: number;
  stderr?: string;
}

export interface TestGenerationMeta {
  task_id?: string;
  total_generated?: number;
  validated_count?: number;
  rejected_count?: number;
  category_breakdown?: Record<string, number>;
  rejected_details?: Array<{
    test_id: string;
    category: string;
    reason: string;
  }>;
}

interface TestExecutionPanelProps {
  testDetails?: TestCaseDetail[];
  generationMeta?: TestGenerationMeta;
  activeVersionLabel?: string;
}

export default function TestExecutionPanel({
  testDetails = [],
  generationMeta,
  activeVersionLabel = "Current",
}: TestExecutionPanelProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [showRejected, setShowRejected] = useState<boolean>(false);

  const categories = ["all", "basic", "boundary", "edge", "invalid_input", "performance", "regression"];

  const filtered = testDetails.filter((t) => {
    if (selectedCategory === "all") return true;
    return (t.category || "general").toLowerCase() === selectedCategory.toLowerCase();
  });

  const passedCount = testDetails.filter((t) => t.status === "passed").length;
  const failedCount = testDetails.filter((t) => t.status === "failed").length;

  return (
    <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/60">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-950/80 border border-purple-800/60 flex items-center justify-center text-purple-400">
            <TestTube2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-100 flex items-center gap-2">
              Live Test Execution & Oracle Validation
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {activeVersionLabel}
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Categorized tests executed in sandboxed subprocess with strict timeouts
            </p>
          </div>
        </div>

        {/* Aggregate Badges */}
        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-2.5 py-1 rounded-md bg-emerald-950/70 border border-emerald-800 text-emerald-400 font-semibold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {passedCount} Passed
          </span>
          <span className="px-2.5 py-1 rounded-md bg-rose-950/70 border border-rose-800 text-rose-400 font-semibold flex items-center gap-1">
            <XCircle className="w-3.5 h-3.5" />
            {failedCount} Failed
          </span>
        </div>
      </div>

      {/* Test Generation & Oracle Validation Metadata Card */}
      {generationMeta && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span className="font-semibold text-slate-200">
                Dynamic Test Generator & Oracle Attestation
              </span>
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              Generated: {generationMeta.total_generated || 12} | Validated:{" "}
              {generationMeta.validated_count || 10} | Rejected:{" "}
              {generationMeta.rejected_count || 2}
            </span>
          </div>

          <div className="flex flex-wrap gap-2 pt-1">
            {generationMeta.category_breakdown &&
              Object.entries(generationMeta.category_breakdown).map(([cat, count]) => (
                <span
                  key={cat}
                  className="px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/60 text-[10px] font-mono text-slate-300"
                >
                  {cat}: {count}
                </span>
              ))}
          </div>

          {generationMeta.rejected_details && generationMeta.rejected_details.length > 0 && (
            <div className="pt-2 border-t border-slate-800/60">
              <button
                type="button"
                onClick={() => setShowRejected(!showRejected)}
                className="text-[11px] text-amber-400 hover:text-amber-300 flex items-center space-x-1 font-mono"
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>
                  {showRejected ? "Hide" : "Inspect"} {generationMeta.rejected_details.length}{" "}
                  Defective Tests Filtered by Oracle
                </span>
              </button>

              {showRejected && (
                <div className="mt-2 space-y-1.5 pl-2">
                  {generationMeta.rejected_details.map((rej, i) => (
                    <div
                      key={i}
                      className="bg-amber-950/30 border border-amber-900/50 rounded p-2 text-[11px] font-mono text-amber-200"
                    >
                      <div className="font-bold flex items-center justify-between">
                        <span>Rejected Test: {rej.test_id}</span>
                        <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-amber-900/60 text-amber-300">
                          {rej.category}
                        </span>
                      </div>
                      <p className="text-amber-300/80 text-[10px] mt-0.5">Reason: {rej.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Category Filter Chips */}
      <div className="flex flex-wrap items-center gap-1.5 pt-1">
        <Filter className="w-3.5 h-3.5 text-slate-500 mr-1" />
        {categories.map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => setSelectedCategory(cat)}
            className={`px-2.5 py-1 rounded text-[10px] font-mono uppercase transition ${
              selectedCategory === cat
                ? "bg-purple-950 text-purple-300 border border-purple-700 font-semibold"
                : "bg-slate-900/80 text-slate-400 border border-slate-800 hover:text-slate-200"
            }`}
          >
            {cat.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Test Execution List */}
      <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
        {filtered.length === 0 ? (
          <p className="text-xs text-slate-500 italic p-4 text-center">
            No test executions match the selected filter category.
          </p>
        ) : (
          filtered.map((t, idx) => {
            const isPass = t.status === "passed";
            return (
              <div
                key={idx}
                className={`p-3 rounded-lg border transition text-xs ${
                  isPass
                    ? "bg-slate-900/40 border-slate-800/80 hover:border-slate-700"
                    : "bg-rose-950/20 border-rose-900/60 hover:border-rose-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {isPass ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                    )}
                    <span className="font-mono font-semibold text-slate-200">{t.id}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 uppercase">
                      {t.category || "test"}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
                    {t.elapsed !== undefined && (
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span>{t.elapsed.toFixed(4)}s</span>
                      </span>
                    )}
                    <span
                      className={`font-semibold ${
                        isPass ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {isPass ? "PASS" : "FAIL"}
                    </span>
                  </div>
                </div>

                {t.description && (
                  <p className="text-[11px] text-slate-400 mt-1 pl-6">{t.description}</p>
                )}

                {!isPass && (t.reason || t.error || t.stderr) && (
                  <div className="mt-2 pl-6">
                    <div className="bg-slate-950 border border-rose-900/40 rounded p-2 text-[10px] font-mono text-rose-300">
                      {t.reason && <div>Failure Reason: {t.reason}</div>}
                      {t.stderr && <div className="text-slate-400 mt-1 truncate">Stderr: {t.stderr}</div>}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

