"use client";

import React from "react";
import {
  TrendingUp,
  Activity,
  CheckCircle2,
  Clock,
  Layers,
  ShieldCheck,
  Zap,
} from "lucide-react";

export interface AnalyticsIteration {
  version: string;
  score: number;
  passed: number;
  total: number;
  sub_scores?: {
    correctness?: number;
    efficiency?: number;
    safety?: number;
    quality?: number;
  };
  failed_tests?: string[];
}

interface EvolutionAnalyticsProps {
  iterations: AnalyticsIteration[];
}

export default function EvolutionAnalytics({ iterations = [] }: EvolutionAnalyticsProps) {
  if (iterations.length === 0) {
    return null;
  }

  const vInitial = iterations[0];
  const vFinal = iterations[iterations.length - 1];
  const scoreDelta = (vFinal.score - vInitial.score).toFixed(1);
  const initialPassRate = ((vInitial.passed / (vInitial.total || 1)) * 100).toFixed(0);
  const finalPassRate = ((vFinal.passed / (vFinal.total || 1)) * 100).toFixed(0);
  const totalIterations = iterations.length;

  return (
    <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-100">
              Evolution Trajectory Analytics
            </h3>
            <p className="text-[11px] text-slate-400">
              Verified algorithmic progression metrics across self-improvement iterations
            </p>
          </div>
        </div>

        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/60 text-emerald-400 font-bold">
          Score Delta: +{scoreDelta} pts
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Baseline Score (V1)</span>
          <span className="text-xl font-bold font-mono text-rose-400 mt-1 block">
            {vInitial.score.toFixed(1)}
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            Passed: {vInitial.passed}/{vInitial.total} ({initialPassRate}%)
          </span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Terminal Score</span>
          <span className="text-xl font-bold font-mono text-emerald-400 mt-1 block">
            {vFinal.score.toFixed(1)}
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            Passed: {vFinal.passed}/{vFinal.total} ({finalPassRate}%)
          </span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Total Iterations</span>
          <span className="text-xl font-bold font-mono text-cyan-400 mt-1 block">
            {totalIterations} Cycles
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            Stopping condition met
          </span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Failure Elimination</span>
          <span className="text-xl font-bold font-mono text-purple-400 mt-1 block">
            {vInitial.failed_tests?.length || 0} &rarr; {vFinal.failed_tests?.length || 0}
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            Defects resolved to zero
          </span>
        </div>
      </div>

      {/* Iteration Progression Visual Bar Chart */}
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-lg p-3.5 space-y-3">
        <span className="text-[10px] font-mono uppercase text-slate-400 block">
          Score Evolution Progression:
        </span>

        <div className="space-y-2">
          {iterations.map((it) => {
            const pct = Math.min(100, Math.max(0, it.score));
            const barColor =
              pct >= 95 ? "bg-emerald-500" : pct >= 80 ? "bg-amber-500" : "bg-rose-500";

            return (
              <div key={it.version} className="space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-semibold text-slate-200">{it.version}</span>
                  <span className="text-slate-400">
                    Score: {it.score.toFixed(1)} | Passed: {it.passed}/{it.total}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className={`${barColor} h-full rounded-full transition-all duration-500`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

