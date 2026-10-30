"use client";

import React from "react";
import {
  GitCommit,
  CheckCircle2,
  Clock,
  RotateCcw,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  BrainCircuit,
  TestTube2,
  Code2,
  Terminal,
  Activity,
} from "lucide-react";

export type StageStatus = "WAITING" | "RUNNING" | "COMPLETED" | "FAILED" | "BLOCKED";

export interface WorkflowStage {
  id: string;
  name: string;
  description: string;
  iconName: string;
  status: StageStatus;
  meta?: string;
}

interface WorkflowDAGProps {
  currentStageId?: string;
  currentVersion?: string;
  stages?: WorkflowStage[];
}

const DEFAULT_STAGES: WorkflowStage[] = [
  {
    id: "task_spec",
    name: "Task Analyzer",
    description: "Ingests requirements & constraints",
    iconName: "BrainCircuit",
    status: "COMPLETED",
  },
  {
    id: "test_gen",
    name: "Test Generation",
    description: "Derives 6 functional test categories",
    iconName: "TestTube2",
    status: "COMPLETED",
  },
  {
    id: "test_val",
    name: "Test Validator",
    description: "Verifies test oracle & invariants",
    iconName: "ShieldCheck",
    status: "COMPLETED",
  },
  {
    id: "generator",
    name: "Code Generator",
    description: "Synthesizes candidate implementation",
    iconName: "Code2",
    status: "COMPLETED",
  },
  {
    id: "evaluator",
    name: "Sandbox Evaluator",
    description: "Runs subprocess tests with timeouts",
    iconName: "Terminal",
    status: "COMPLETED",
  },
  {
    id: "critic",
    name: "Constitutional Critic",
    description: "Diagnoses failures without code leaks",
    iconName: "Activity",
    status: "COMPLETED",
  },
];

export default function WorkflowDAG({
  currentStageId,
  currentVersion,
  stages = DEFAULT_STAGES,
}: WorkflowDAGProps) {
  const getStatusBadge = (status: StageStatus) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span className="flex items-center space-x-1 text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Completed</span>
          </span>
        );
      case "RUNNING":
        return (
          <span className="flex items-center space-x-1 text-[10px] font-mono text-cyan-300 bg-cyan-950/80 border border-cyan-700 px-2 py-0.5 rounded-full animate-pulse">
            <RotateCcw className="w-3 h-3 animate-spin text-cyan-400" />
            <span>Running</span>
          </span>
        );
      case "FAILED":
        return (
          <span className="flex items-center space-x-1 text-[10px] font-mono text-rose-400 bg-rose-950/60 border border-rose-800/60 px-2 py-0.5 rounded-full">
            <AlertTriangle className="w-3 h-3 text-rose-400" />
            <span>Failed</span>
          </span>
        );
      case "BLOCKED":
        return (
          <span className="flex items-center space-x-1 text-[10px] font-mono text-amber-400 bg-amber-950/60 border border-amber-800/60 px-2 py-0.5 rounded-full">
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            <span>Blocked</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center space-x-1 text-[10px] font-mono text-slate-500 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full">
            <Clock className="w-3 h-3 text-slate-500" />
            <span>Waiting</span>
          </span>
        );
    }
  };

  const getStageIcon = (name: string) => {
    switch (name) {
      case "BrainCircuit":
        return <BrainCircuit className="w-4 h-4 text-cyan-400" />;
      case "TestTube2":
        return <TestTube2 className="w-4 h-4 text-purple-400" />;
      case "ShieldCheck":
        return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      case "Code2":
        return <Code2 className="w-4 h-4 text-blue-400" />;
      case "Terminal":
        return <Terminal className="w-4 h-4 text-amber-400" />;
      default:
        return <Activity className="w-4 h-4 text-violet-400" />;
    }
  };

  return (
    <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <GitCommit className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Agent Workflow Pipeline
          </h3>
        </div>
        {currentVersion && (
          <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/60 px-2.5 py-0.5 rounded-md">
            Active Cycle: {currentVersion}
          </span>
        )}
      </div>

      {/* Responsive Horizontal Workflow Pipeline */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
        {stages.map((stage, idx) => {
          const isCurrent = stage.id === currentStageId;
          return (
            <div
              key={stage.id}
              className={`relative rounded-xl p-3.5 border transition flex flex-col justify-between ${
                isCurrent
                  ? "bg-cyan-950/30 border-cyan-500 shadow-md shadow-cyan-950/50"
                  : stage.status === "COMPLETED"
                  ? "bg-slate-900/60 border-slate-800/90"
                  : "bg-slate-900/30 border-slate-800/50 opacity-70"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="w-7 h-7 rounded-lg bg-slate-800/90 border border-slate-700/60 flex items-center justify-center">
                    {getStageIcon(stage.iconName)}
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">0{idx + 1}</span>
                </div>

                <h4 className="text-xs font-semibold text-slate-100 truncate mb-1">
                  {stage.name}
                </h4>
                <p className="text-[11px] text-slate-400 leading-tight line-clamp-2">
                  {stage.description}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between">
                {getStatusBadge(stage.status)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

