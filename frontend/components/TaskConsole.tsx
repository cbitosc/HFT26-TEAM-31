"use client";

import React, { useState } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  StepForward,
  Layers,
  Settings2,
  Code2,
  Plus,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Radio,
  Clock,
  Sparkles,
} from "lucide-react";

export interface TaskOption {
  task_id: string;
  name: string;
  description: string;
  programming_language: string;
  class_or_function_name: string;
  functional_requirements: string[];
}

interface TaskConsoleProps {
  tasks: TaskOption[];
  selectedTaskId: string;
  onSelectTask: (taskId: string) => void;
  executionMode: "LIVE" | "OFFLINE_DEMO" | "REPLAY";
  onSelectMode: (mode: "LIVE" | "OFFLINE_DEMO" | "REPLAY") => void;
  isRunning: boolean;
  isPaused: boolean;
  stepMode: boolean;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onStep: () => void;
  onReset: () => void;
  onCustomTaskSubmit?: (task: any) => void;
}

export default function TaskConsole({
  tasks,
  selectedTaskId,
  onSelectTask,
  executionMode,
  onSelectMode,
  isRunning,
  isPaused,
  stepMode,
  onStart,
  onPause,
  onResume,
  onStep,
  onReset,
  onCustomTaskSubmit,
}: TaskConsoleProps) {
  const [showCustomModal, setShowCustomModal] = useState(false);
  const [customName, setCustomName] = useState("");
  const [customDesc, setCustomDesc] = useState("");
  const [customClass, setCustomClass] = useState("");
  const [customReqs, setCustomReqs] = useState("");

  const activeTask = tasks.find((t) => t.task_id === selectedTaskId) || tasks[0];

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customName || !customDesc || !customClass) return;

    const reqsList = customReqs
      .split("\n")
      .map((r) => r.trim())
      .filter(Boolean);

    const customTaskData = {
      task_id: `custom_${Date.now()}`,
      name: customName,
      description: customDesc,
      class_or_function_name: customClass,
      programming_language: "python",
      functional_requirements: reqsList,
    };

    if (onCustomTaskSubmit) {
      onCustomTaskSubmit(customTaskData);
    }
    setShowCustomModal(false);
  };

  return (
    <div className="bg-[#0b0f17] border border-slate-800/80 rounded-xl p-5 shadow-2xl backdrop-blur-md">
      {/* Header & Controls Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-800/60">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-slate-100 flex items-center gap-2">
              Task Workspace & Control
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                v2.0
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Select verified benchmark specifications or submit custom algorithmic tasks
            </p>
          </div>
        </div>

        {/* Execution Mode Selector */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center bg-slate-900/90 border border-slate-800 rounded-lg p-1 text-xs">
            <button
              type="button"
              onClick={() => onSelectMode("OFFLINE_DEMO")}
              className={`px-3 py-1 rounded-md font-mono text-[11px] transition ${executionMode === "OFFLINE_DEMO"
                ? "bg-cyan-950 text-cyan-300 border border-cyan-700/60 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
                }`}
              title="Deterministic mock trajectory for offline execution"
            >
              Deterministic Mock
            </button>
            <button
              type="button"
              onClick={() => onSelectMode("LIVE")}
              className={`px-3 py-1 rounded-md font-mono text-[11px] transition ${executionMode === "LIVE"
                ? "bg-purple-950 text-purple-300 border border-purple-700/60 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
                }`}
              title="Live LLM generation & critique via API"
            >
              Live Model
            </button>
            <button
              type="button"
              onClick={() => onSelectMode("REPLAY")}
              className={`px-3 py-1 rounded-md font-mono text-[11px] transition ${executionMode === "REPLAY"
                ? "bg-emerald-950 text-emerald-300 border border-emerald-700/60 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
                }`}
              title="Replay historical execution traces"
            >
              Replay Trace
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {!isRunning ? (
              <button
                type="button"
                onClick={onStart}
                className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs shadow-lg shadow-cyan-600/20 border border-cyan-400/30 transition"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>Start Evolution</span>
              </button>
            ) : isPaused ? (
              <button
                type="button"
                onClick={onResume}
                className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-lg shadow-emerald-600/20 border border-emerald-400/30 transition"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>Resume</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={onPause}
                className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs shadow-lg shadow-amber-600/20 border border-amber-400/30 transition"
              >
                <Pause className="w-3.5 h-3.5 fill-white" />
                <span>Pause</span>
              </button>
            )}

            {stepMode && (
              <button
                type="button"
                onClick={onStep}
                disabled={!isRunning || !isPaused}
                className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs border border-slate-700 transition disabled:opacity-40"
              >
                <StepForward className="w-3.5 h-3.5" />
                <span>Step</span>
              </button>
            )}

            <button
              type="button"
              onClick={onReset}
              className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 text-slate-400 hover:text-slate-200 transition"
              title="Reset workspace"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Task Selector & Description Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
        {/* Task Selection Column */}
        <div className="space-y-2">
          <label className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block">
            Target Benchmark
          </label>
          <div className="space-y-1.5">
            {tasks.map((task) => {
              const isSelected = task.task_id === selectedTaskId;
              return (
                <button
                  key={task.task_id}
                  type="button"
                  onClick={() => onSelectTask(task.task_id)}
                  disabled={isRunning}
                  className={`w-full text-left px-3 py-2.5 rounded-lg border transition flex items-center justify-between text-xs ${isSelected
                    ? "bg-slate-800/90 border-cyan-500/60 text-white shadow-sm"
                    : "bg-slate-900/40 border-slate-800 text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                    } disabled:opacity-60`}
                >
                  <div className="truncate">
                    <span className="font-semibold block truncate">{task.name}</span>
                    <span className="text-[10px] font-mono text-slate-400">{task.task_id}</span>
                  </div>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 ml-2" />}
                </button>
              );
            })}

            <button
              type="button"
              onClick={() => setShowCustomModal(true)}
              disabled={isRunning}
              className="w-full text-left px-3 py-2 rounded-lg border border-dashed border-slate-700 hover:border-slate-500 text-slate-400 hover:text-slate-200 text-xs flex items-center justify-center space-x-1.5 transition disabled:opacity-50"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Submit Custom Task</span>
            </button>
          </div>
        </div>

        {/* Task Specification Details */}
        <div className="lg:col-span-2 bg-slate-900/40 border border-slate-800/80 rounded-lg p-3.5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-200">{activeTask?.name}</span>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Language: Python
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                Class: {activeTask?.class_or_function_name}
              </span>
            </div>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            {activeTask?.description}
          </p>

          {activeTask?.functional_requirements && activeTask.functional_requirements.length > 0 && (
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                Functional Requirements:
              </span>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-[11px] text-slate-400 list-disc list-inside">
                {activeTask.functional_requirements.slice(0, 4).map((req, i) => (
                  <li key={i} className="truncate" title={req}>
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Custom Task Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Code2 className="w-4 h-4 text-cyan-400" />
                Submit Custom Programming Task
              </h3>
              <button
                type="button"
                onClick={() => setShowCustomModal(false)}
                className="text-slate-400 hover:text-white text-xs font-mono"
              >
                [ESC]
              </button>
            </div>

            <form onSubmit={handleCustomSubmit} className="space-y-3 text-xs">
              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">
                  Task Name
                </label>
                <input
                  type="text"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  placeholder="e.g. Circular Queue Buffer"
                  className="w-full bg-slate-950 border border-slate-700 rounded-md px-3 py-1.5 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">
                  Target Class Name
                </label>
                <input
                  type="text"
                  value={customClass}
                  onChange={(e) => setCustomClass(e.target.value)}
                  placeholder="e.g. CircularQueue"
                  className="w-full bg-slate-950 border border-slate-700 rounded-md px-3 py-1.5 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">
                  Problem Description
                </label>
                <textarea
                  value={customDesc}
                  onChange={(e) => setCustomDesc(e.target.value)}
                  rows={3}
                  placeholder="Detailed functional specification, complexity requirements, and edge cases..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-md px-3 py-1.5 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-400 block mb-1">
                  Functional Requirements (One per line)
                </label>
                <textarea
                  value={customReqs}
                  onChange={(e) => setCustomReqs(e.target.value)}
                  rows={3}
                  placeholder="enQueue(val) returns bool&#10;deQueue() returns bool&#10;Front() returns int or -1"
                  className="w-full bg-slate-950 border border-slate-700 rounded-md px-3 py-1.5 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCustomModal(false)}
                  className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs shadow-md"
                >
                  Register Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

