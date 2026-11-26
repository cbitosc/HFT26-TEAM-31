"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  TrendingUp,
  Skull,
  Coins,
  Compass,
  CheckCircle2,
  Flame,
  BrainCircuit,
  RefreshCw,
  GitCommit,
} from "lucide-react";

interface SimulationMap {
  map_id: number;
  name: string;
  width: number;
  height: number;
  grid: string[][];
  start: [number, number];
  exit: [number, number];
  lava: [number, number][];
  monsters: [number, number][];
  treasures: [number, number][];
  simulations: {
    [versionKey: string]: {
      path: [number, number][];
      cause: string;
      gold: number;
      steps: number;
    };
  };
}

interface GenerationData {
  version: number;
  policy: {
    version: number;
    COSTS: Record<string, number>;
    avoidance_radius: number;
    changelog: string;
  };
  test_result: {
    policy_version: number;
    success_rate: number;
    death_by_lava_pct: number;
    death_by_monster_pct: number;
    avg_treasure: number;
    avg_steps: number;
    score: number;
  };
  critique: {
    score: number;
    failure_modes: string[];
    root_cause: string;
    instruction_for_next_generator: string;
  };
}

interface Agent1Props {
  maps: SimulationMap[];
  generations: GenerationData[];
  onReRunTask1?: () => Promise<void>;
}

export default function Agent1DungeonComponent({
  maps,
  generations,
  onReRunTask1,
}: Agent1Props) {
  const [selectedMapIdx, setSelectedMapIdx] = useState<number>(0);
  const [selectedVersion, setSelectedVersion] = useState<number>(4); // Default to V4 (Optimal Master)
  const [stepIdx, setStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speedMs, setSpeedMs] = useState<number>(120);
  const [reRunning, setReRunning] = useState<boolean>(false);

  const activeMap = maps[selectedMapIdx] || maps[0];
  const activeSimKey = `V${selectedVersion}`;
  const activeSim = activeMap?.simulations[activeSimKey] || { path: [], cause: "timeout", gold: 0, steps: 0 };
  const path = activeSim.path || [];

  const activeGen = generations.find((g) => g.version === selectedVersion) || generations[generations.length - 1];

  // Reset step counter on version or map change
  useEffect(() => {
    setStepIdx(0);
    setIsPlaying(false);
  }, [selectedMapIdx, selectedVersion]);

  // Animation ticker for auto-play
  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;
    if (isPlaying && path.length > 0) {
      timer = setInterval(() => {
        setStepIdx((prev) => {
          if (prev >= path.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, speedMs);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isPlaying, path.length, speedMs]);

  const currentPos = path[Math.min(stepIdx, Math.max(0, path.length - 1))] || (activeMap ? activeMap.start : [1, 1]);
  const isFinished = stepIdx >= path.length - 1 && path.length > 0;
  const cause = activeSim.cause;

  const visitedPositions = new Set(path.slice(0, stepIdx + 1).map(([x, y]) => `${x},${y}`));
  const collectedChestsCount = activeMap ? activeMap.treasures.filter(([tx, ty]) =>
    visitedPositions.has(`${tx},${ty}`)
  ).length : 0;

  const versionLabels: Record<number, { title: string; badge: string; color: string }> = {
    1: { title: "V1: Chaotic Baseline", badge: "100% Lava / 78% Monster", color: "rose" },
    2: { title: "V2: Greedy Looter", badge: "96% Monster Deaths", color: "amber" },
    3: { title: "V3: Overly Cautious", badge: "100% Survival, 0 Gold", color: "blue" },
    4: { title: "V4: Optimal Master", badge: "100% Survival, 3.0/3 Gold", color: "emerald" },
  };

  const handleTriggerReRun = async () => {
    if (onReRunTask1) {
      setReRunning(true);
      try {
        await onReRunTask1();
      } finally {
        setReRunning(false);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner: Agent 1 Generational Overview */}
      <div className="bg-gradient-to-r from-slate-900/95 via-blue-950/40 to-slate-900/95 border border-slate-800/80 rounded-xl p-6 shadow-xl relative overflow-hidden backdrop-blur-md">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
          <div className="space-y-1">
            <div className="flex items-center space-x-2.5">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                TASK 1: AGENT 1
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono">
                Phase 0 Genesis &rarr; Phase 1 G-T-C Loop
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                4 Generations (V1 &rarr; V4)
              </span>
            </div>
            <h2 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <span>Agent 1 Multi-Generation Policy Evolution</span>
            </h2>
            <p className="text-xs text-slate-400 max-w-2xl">
              Agent 1 began as a naive seed during Phase 0 Genesis, dying repeatedly to lava hazards and monster ambushes. Through closed-loop Critique directives, it iteratively adapted across 4 generations (V1 &rarr; V2 &rarr; V3 &rarr; V4) until achieving convergence.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {onReRunTask1 && (
              <button
                onClick={handleTriggerReRun}
                disabled={reRunning}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-blue-600/20"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${reRunning ? "animate-spin" : ""}`} />
                <span>{reRunning ? "Evolving Loop..." : "Re-Run Task 1 Loop"}</span>
              </button>
            )}
          </div>
        </div>

        {/* Generational Quick Switcher Tabs (V1, V2, V3, V4) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-5 pt-5 border-t border-slate-800/80">
          {[1, 2, 3, 4].map((v) => {
            const isSelected = selectedVersion === v;
            const meta = versionLabels[v];
            const g = generations.find((gen) => gen.version === v);
            return (
              <button
                key={v}
                onClick={() => setSelectedVersion(v)}
                className={`p-3 rounded-lg border text-left transition ${
                  isSelected
                    ? "bg-blue-950/70 border-blue-500 shadow-md shadow-blue-600/20"
                    : "bg-slate-900/60 border-slate-800/80 hover:bg-slate-800/50"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold font-mono text-slate-200">
                    Version V{v}
                  </span>
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${
                      v === 4
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                        : v === 3
                        ? "bg-blue-500/10 text-blue-400 border-blue-500/30"
                        : v === 2
                        ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                        : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                    }`}
                  >
                    {v === 4 ? "CONVERGED" : `CYCLE ${v}`}
                  </span>
                </div>
                <div className="text-[11px] text-slate-300 font-semibold truncate">
                  {meta.title}
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-1">
                  Score: {g?.test_result.score.toFixed(3) || "N/A"} | Clear: {g ? (g.test_result.success_rate * 100).toFixed(0) : "0"}%
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Grid Simulator for Agent 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive 2D Dungeon Visualizer */}
        <div className="lg:col-span-8 bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className={`p-2 rounded-lg font-bold text-xs flex items-center gap-1.5 transition ${
                  isPlaying
                    ? "bg-amber-600 hover:bg-amber-500 text-white"
                    : "bg-blue-600 hover:bg-blue-500 text-white"
                }`}
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                <span>{isPlaying ? "Pause" : "Auto-Play"}</span>
              </button>

              <button
                onClick={() => {
                  setStepIdx(0);
                  setIsPlaying(false);
                }}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold flex items-center gap-1"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            </div>

            {/* Scrubber slider */}
            <div className="flex-1 min-w-[160px] flex items-center gap-2 px-2">
              <span className="text-[11px] font-mono text-slate-400 whitespace-nowrap">
                Step {stepIdx} / {Math.max(0, path.length - 1)}
              </span>
              <input
                type="range"
                min="0"
                max={Math.max(0, path.length - 1)}
                value={stepIdx}
                onChange={(e) => {
                  setStepIdx(parseInt(e.target.value));
                  setIsPlaying(false);
                }}
                className="w-full accent-blue-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
            </div>

            {/* Speed selector */}
            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-md border border-slate-800">
              {[
                { label: "1x", ms: 150 },
                { label: "2x", ms: 80 },
                { label: "4x", ms: 35 },
              ].map((s) => (
                <button
                  key={s.label}
                  onClick={() => setSpeedMs(s.ms)}
                  className={`px-2 py-0.5 text-[10px] font-mono rounded ${
                    speedMs === s.ms ? "bg-blue-600 text-white font-bold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Dungeon 2D Grid Render */}
          <div className="relative bg-slate-950 rounded-xl border border-slate-800/80 p-3 flex justify-center items-center overflow-hidden">
            <div
              className="grid gap-1 select-none"
              style={{
                gridTemplateColumns: `repeat(${activeMap.width}, minmax(0, 1fr))`,
                width: "100%",
                maxWidth: "640px",
                aspectRatio: `${activeMap.width} / ${activeMap.height}`,
              }}
            >
              {activeMap.grid.map((row, y) =>
                row.map((cell, x) => {
                  const isStart = activeMap.start[0] === x && activeMap.start[1] === y;
                  const isExit = activeMap.exit[0] === x && activeMap.exit[1] === y;
                  const isLava = activeMap.lava.some(([lx, ly]) => lx === x && ly === y);
                  const isMonster = activeMap.monsters.some(([mx, my]) => mx === x && my === y);
                  const isTreasure = activeMap.treasures.some(([tx, ty]) => tx === x && ty === y);
                  const isCrawler = currentPos[0] === x && currentPos[1] === y;
                  const isTraversed = visitedPositions.has(`${x},${y}`);

                  let bgColor = "bg-slate-900/60";
                  let border = "border-slate-800/40";
                  let content = null;

                  if (cell === "#") {
                    bgColor = "bg-slate-800/90";
                    border = "border-slate-700/60";
                  } else if (isLava) {
                    bgColor = "bg-rose-900/70";
                    border = "border-rose-600/60";
                    content = <Flame className="w-3.5 h-3.5 text-rose-400 animate-pulse" />;
                  } else if (isMonster) {
                    bgColor = "bg-purple-950/80";
                    border = "border-purple-600/70";
                    content = <Skull className="w-3.5 h-3.5 text-purple-400" />;
                  } else if (isTreasure) {
                    const looted = visitedPositions.has(`${x},${y}`);
                    bgColor = looted ? "bg-amber-950/40" : "bg-amber-900/60";
                    border = looted ? "border-amber-600/40" : "border-amber-400/80";
                    content = (
                      <Coins className={`w-3.5 h-3.5 ${looted ? "text-amber-500/50" : "text-amber-400 animate-bounce"}`} />
                    );
                  } else if (isExit) {
                    bgColor = "bg-emerald-950/80";
                    border = "border-emerald-500";
                    content = <span className="text-[10px] font-bold text-emerald-400">EXIT</span>;
                  } else if (isStart) {
                    bgColor = "bg-cyan-950/80";
                    border = "border-cyan-500";
                    content = <span className="text-[10px] font-bold text-cyan-400">START</span>;
                  }

                  return (
                    <div
                      key={`${x}-${y}`}
                      className={`relative aspect-square rounded-sm border ${border} ${bgColor} flex items-center justify-center transition-colors duration-100 ${
                        isTraversed && cell !== "#" ? "ring-1 ring-blue-500/30" : ""
                      }`}
                    >
                      {content}

                      {isTraversed && !isCrawler && cell !== "#" && (
                        <div className="absolute w-1.5 h-1.5 rounded-full bg-blue-400/40 pointer-events-none" />
                      )}

                      {isCrawler && (
                        <div
                          className={`absolute inset-0.5 rounded-full flex items-center justify-center font-bold text-[10px] z-20 shadow-lg ${
                            selectedVersion === 4
                              ? "bg-emerald-500 text-white shadow-emerald-500/50"
                              : selectedVersion === 3
                              ? "bg-blue-500 text-white shadow-blue-500/50"
                              : selectedVersion === 2
                              ? "bg-amber-500 text-white shadow-amber-500/50"
                              : "bg-rose-500 text-white shadow-rose-500/50"
                          }`}
                        >
                          <Compass className="w-3 h-3 animate-spin" style={{ animationDuration: "3s" }} />
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Outcome Status Banner */}
          <div
            className={`p-3 rounded-lg border flex items-center justify-between text-xs font-mono font-bold ${
              isFinished
                ? cause === "success"
                  ? "bg-emerald-950/40 border-emerald-500/50 text-emerald-300"
                  : "bg-rose-950/40 border-rose-500/50 text-rose-300"
                : "bg-slate-900 border-slate-800 text-slate-300"
            }`}
          >
            <div className="flex items-center gap-2">
              <span>Outcome:</span>
              {isFinished ? (
                cause === "success" ? (
                  <span className="flex items-center gap-1 text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> V{selectedVersion} CLEARED (EXIT REACHED)
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-rose-400">
                    <Skull className="w-4 h-4" /> TERMINATED: {cause.toUpperCase()} AT STEP {path.length}
                  </span>
                )
              ) : (
                <span className="text-blue-400">SIMULATING STEP {stepIdx}...</span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <span>Gold: {collectedChestsCount} / {activeMap.treasures.length}</span>
              <span>Coords: ({currentPos[0]}, {currentPos[1]})</span>
            </div>
          </div>
        </div>

        {/* Right Column: Version Inspector & Critique Telemetry */}
        <div className="lg:col-span-4 space-y-4">
          {/* Map Selection */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
            <label className="text-xs font-mono uppercase text-slate-400 block">
              Benchmark Map Selection
            </label>
            <select
              value={selectedMapIdx}
              onChange={(e) => setSelectedMapIdx(parseInt(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg p-2 font-mono outline-none focus:border-blue-500"
            >
              {maps.map((m) => (
                <option key={m.map_id} value={m.map_id}>
                  Map {m.map_id}: {m.name} ({m.width}x{m.height})
                </option>
              ))}
            </select>
          </div>

          {/* Subjective Costs Card */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">
              Policy Parameters (V{selectedVersion})
            </span>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">LAVA COST</span>
                <span className="text-rose-400 font-bold">{activeGen?.policy.COSTS.lava ?? 3}</span>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">MONSTER COST</span>
                <span className="text-purple-400 font-bold">{activeGen?.policy.COSTS.monster ?? 2}</span>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">TREASURE INCENTIVE</span>
                <span className="text-amber-400 font-bold">{activeGen?.policy.COSTS.treasure ?? -4}</span>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">AVOIDANCE RADIUS</span>
                <span className="text-emerald-400 font-bold">{activeGen?.policy.avoidance_radius ?? 1} tiles</span>
              </div>
            </div>
            <div className="text-[10px] text-slate-400 pt-1">
              Changelog: <span className="text-slate-300 italic">{activeGen?.policy.changelog}</span>
            </div>
          </div>

          {/* Critique LLM Feedback Box */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200">
              <BrainCircuit className="w-4 h-4 text-purple-400" />
              <span>Critique Directive for V{selectedVersion}</span>
            </div>
            <div className="text-[11px] text-slate-300 bg-slate-950 p-3 rounded-lg border border-purple-900/40 space-y-2">
              <div>
                <span className="text-purple-400 font-bold block text-[10px] uppercase">Diagnosed Root Cause:</span>
                <p className="italic text-slate-300">{activeGen?.critique.root_cause}</p>
              </div>
              <div>
                <span className="text-purple-400 font-bold block text-[10px] uppercase">Directive for Next Generator:</span>
                <p className="text-slate-200 font-semibold">{activeGen?.critique.instruction_for_next_generator}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Evolution Milestone Summary Table (V1, V2, V3, V4) */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 shadow-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-blue-400" />
          <span>Agent 1 Trajectory Summary (V1 &rarr; V2 &rarr; V3 &rarr; V4)</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase text-[10px]">
              <tr>
                <th className="p-3">Generation</th>
                <th className="p-3">Survival Rate</th>
                <th className="p-3">Lava Deaths</th>
                <th className="p-3">Monster Deaths</th>
                <th className="p-3">Gold Collected</th>
                <th className="p-3">Steps</th>
                <th className="p-3">Fitness Score</th>
                <th className="p-3">Policy Parameters</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {generations.map((g) => {
                const isSelected = selectedVersion === g.version;
                return (
                  <tr
                    key={g.version}
                    onClick={() => setSelectedVersion(g.version)}
                    className={`cursor-pointer transition ${
                      isSelected ? "bg-blue-950/40 font-bold" : "hover:bg-slate-800/30"
                    }`}
                  >
                    <td className="p-3 font-bold text-slate-200">
                      Version V{g.version} {g.version === 4 ? "★ (Target Reached)" : ""}
                    </td>
                    <td className="p-3 text-slate-200">{(g.test_result.success_rate * 100).toFixed(1)}%</td>
                    <td className="p-3 text-rose-400">{g.test_result.death_by_lava_pct.toFixed(0)}%</td>
                    <td className="p-3 text-purple-400">{g.test_result.death_by_monster_pct.toFixed(0)}%</td>
                    <td className="p-3 text-amber-400">{g.test_result.avg_treasure.toFixed(2)} / 3.0</td>
                    <td className="p-3 text-slate-400">{g.test_result.avg_steps}</td>
                    <td className="p-3 font-bold text-blue-400">{g.test_result.score.toFixed(3)}</td>
                    <td className="p-3 text-[11px] text-slate-400 font-mono">
                      lava={g.policy.COSTS.lava}, monster={g.policy.COSTS.monster}, gold={g.policy.COSTS.treasure}, r={g.policy.avoidance_radius}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

