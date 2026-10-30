"use client";

import React from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Layers,
} from "lucide-react";

export interface CriticPayload {
  failure_type?: string;
  severity?: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  root_cause?: string;
  fix_instruction?: string;
  failed_tests?: string[];
}

interface CriticIntelligencePanelProps {
  critique?: CriticPayload;
  versionLabel?: string;
  isResolvedInNext?: boolean;
  nextVersionLabel?: string;
}

export default function CriticIntelligencePanel({
  critique,
  versionLabel = "V1",
  isResolvedInNext = false,
  nextVersionLabel = "V2",
}: CriticIntelligencePanelProps) {
  if (!critique) {
    return (
      <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-5 shadow-2xl backdrop-blur-md text-slate-400 text-xs">
        No critic analysis available for {versionLabel}.
      </div>
    );
  }

  const isNone = critique.failure_type === "None" || !critique.failure_type;
  const severity = (critique.severity || "MEDIUM").toUpperCase();

  const getSeverityBadge = () => {
    switch (severity) {
      case "CRITICAL":
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-950 text-rose-400 border border-rose-800 font-bold">
            CRITICAL SEVERITY
          </span>
        );
      case "HIGH":
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-950 text-amber-400 border border-amber-800 font-bold">
            HIGH SEVERITY
          </span>
        );
      case "MEDIUM":
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-950 text-blue-400 border border-blue-800 font-bold">
            MEDIUM SEVERITY
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
            RESOLVED
          </span>
        );
    }
  };

  return (
    <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/60">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-violet-950/80 border border-violet-800/60 flex items-center justify-center text-violet-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-100 flex items-center gap-2">
              Constitutional Critic Diagnosis
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Target: {versionLabel}
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Natural-language architectural reflection strictly preserving zero code leakage
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {getSeverityBadge()}
          {isResolvedInNext && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              <span>Resolved in {nextVersionLabel}</span>
            </span>
          )}
        </div>
      </div>

      {isNone ? (
        <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-800/40 text-emerald-200 text-xs flex items-center space-x-3">
          <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          <div>
            <span className="font-bold block">All Constraints & Tests Satisfied</span>
            <p className="text-[11px] text-emerald-300/80 mt-0.5">
              The candidate implementation achieved full unit-test correctness, O(1) efficiency bounds, and robust type safety. No architectural revisions required.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Diagnostic Root Cause */}
          <div className="bg-slate-900/40 border border-slate-800/90 rounded-lg p-3.5 space-y-2">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-rose-300">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Diagnosed Failure: {critique.failure_type}</span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {critique.root_cause}
            </p>

            {critique.failed_tests && critique.failed_tests.length > 0 && (
              <div className="pt-2 border-t border-slate-800/60">
                <span className="text-[10px] font-mono text-slate-400 block mb-1">
                  Triggering Failing Tests:
                </span>
                <div className="flex flex-wrap gap-1">
                  {critique.failed_tests.map((ft, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-rose-950/60 border border-rose-900/60 text-[10px] font-mono text-rose-300"
                    >
                      {ft}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Actionable Revision Directive */}
          <div className="bg-slate-900/40 border border-slate-800/90 rounded-lg p-3.5 space-y-2">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-cyan-300">
              <Lightbulb className="w-4 h-4 text-cyan-400" />
              <span>Actionable Revision Directive</span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {critique.fix_instruction}
            </p>

            <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
              <span>Guardrail Status:</span>
              <span className="text-emerald-400 font-mono text-[10px] font-semibold">
                PURE VERBAL REFLECTION (NO CODE LEAKAGE)
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

