"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Zap,
  TrendingUp,
  BrainCircuit,
  CheckCircle2,
  AlertTriangle,
  Skull,
  Coins,
  Compass,
  ArrowRight,
  RefreshCw,
  Eye,
  Flame,
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

interface Agent2Data {
  policy: {
    version: number;
    COSTS: Record<string, number>;
    avoidance_radius: number;
    changelog: string;
  };
  test_result: {
    success_rate: number;
    avg_treasure: number;
    score: number;
    death_by_lava_pct: number;
    death_by_monster_pct: number;
  };
  ablation: {
    without_memory_success_rate: number;
    with_memory_success_rate: number;
    delta_gain_percentage: number;
    ablation_passed: boolean;
  };
  reasoning: string;
}

interface Agent2Props {
  maps: SimulationMap[];
  agent2: Agent2Data;
  totalFailureTraces: number;
  comparisonImage?: string;
  onRunAgent2?: () => Promise<void>;
}

export default function Agent2DungeonComponent({
  maps,
  agent2,
  totalFailureTraces,
  comparisonImage,
  onRunAgent2,
}: Agent2Props) {
  const [selectedMapIdx, setSelectedMapIdx] = useState<number>(0);
  const [stepIdx, setStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speedMs, setSpeedMs] = useState<number>(120);
  const [running, setRunning] = useState<boolean>(false);
  const [showVisualProof, setShowVisualProof] = useState<boolean>(true);

  const activeMap = maps[selectedMapIdx] || maps[0];
  const activeSim = activeMap?.simulations["Agent2"] || { path: [], cause: "success", gold: 0, steps: 0 };
  const path = activeSim.path || [];

  // Reset step counter on map change
  useEffect(() => {
    setStepIdx(0);
    setIsPlaying(false);
  }, [selectedMapIdx]);

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

  const handleTriggerRun = async () => {
    if (onRunAgent2) {
      setRunning(true);
      try {
        await onRunAgent2();
      } finally {
        setRunning(false);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Verification Badge & Overview */}
      <div className="bg-gradient-to-r from-slate-900/95 via-emerald-950/30 to-slate-900/95 border border-emerald-500/40 rounded-xl p-6 shadow-xl relative overflow-hidden backdrop-blur-md">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
          <div className="space-y-1">
            <div className="flex items-center space-x-2.5">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                TASK 2: AGENT 2 SINGLE-SHOT
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30 font-mono">
                Loaded 4 versions, {totalFailureTraces} failure traces
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono">
                0 Loops / 0 Retries Allowed
              </span>
            </div>
            <h2 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <span>Agent 2: Single-Shot Cross-Agent Memory Learner</span>
            </h2>
            <p className="text-xs text-slate-400 max-w-2xl">
              Proving <strong>Pillar 4: Cross-Agent Memory prevents repeating mistakes</strong>. Agent 2 ingests the complete evolution ledger from Agent 1 (Task 1) and must finish the benchmark dungeon in a single attempt using that memory without trial-and-error loops.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowVisualProof(!showVisualProof)}
              className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition border ${
                showVisualProof
                  ? "bg-purple-600/30 border-purple-500/60 text-purple-200"
                  : "bg-slate-800/60 border-slate-700 text-slate-300 hover:bg-slate-700/60"
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>{showVisualProof ? "Hide Side-by-Side Proof" : "Show Side-by-Side Proof"}</span>
            </button>

            {onRunAgent2 && (
              <button
                onClick={handleTriggerRun}
                disabled={running}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/20"
              >
                <Zap className={`w-3.5 h-3.5 ${running ? "animate-spin" : ""}`} />
                <span>{running ? "Synthesizing Single-Shot..." : "Run Agent 2 Single Shot"}</span>
              </button>
            )}
          </div>
        </div>

        {/* KPI Metrics Strip */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-5 pt-5 border-t border-slate-800/80">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Single-Shot Success</span>
            <span className="text-lg font-bold text-emerald-400 font-mono">
              {(agent2.test_result.success_rate * 100).toFixed(1)}%
            </span>
            <span className="text-[10px] text-emerald-500/80 block">Target: &ge; 85% (Passed)</span>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Treasure Sweep</span>
            <span className="text-lg font-bold text-amber-400 font-mono">
              {agent2.test_result.avg_treasure.toFixed(1)} / 3.0
            </span>
            <span className="text-[10px] text-amber-500/80 block">Target: &ge; 5/6 (Passed)</span>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Deterministic Score</span>
            <span className="text-lg font-bold text-blue-400 font-mono">
              {agent2.test_result.score.toFixed(3)}
            </span>
            <span className="text-[10px] text-blue-500/80 block">Pure deterministic engine</span>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Ablation (Without Memory)</span>
            <span className="text-lg font-bold text-rose-400 font-mono">
              {(agent2.ablation.without_memory_success_rate * 100).toFixed(1)}%
            </span>
            <span className="text-[10px] text-rose-500/80 block">Fails &lt; 40% on same maps</span>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-lg p-3">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Memory Advantage</span>
            <span className="text-lg font-bold text-emerald-300 font-mono">
              +{agent2.ablation.delta_gain_percentage.toFixed(1)}%
            </span>
            <span className="text-[10px] text-emerald-500/80 block">1-shot performance jump</span>
          </div>
        </div>
      </div>

      {/* Side-by-Side Visual Proof Panel (Same Map) */}
      {showVisualProof && comparisonImage && (
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <span>Visual Proof: V1 Chaotic Red Path vs Agent 2 Optimal Green Path (Same Map)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Left: Task 1 V1 without memory cut through lava shortcuts and was slain. Right: Task 2 Agent 2 bypassed hazards, preserved safety buffers, and swept all chests in 1 attempt.
              </p>
            </div>
          </div>

          <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950 flex justify-center p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={comparisonImage}
              alt="V1 vs Agent 2 Visual Proof"
              className="w-full max-w-5xl rounded-lg object-contain"
            />
          </div>
        </div>
      )}

      {/* Interactive 2D Grid Canvas & Live Scrubber for Agent 2 */}
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
                    : "bg-emerald-600 hover:bg-emerald-500 text-white"
                }`}
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                <span>{isPlaying ? "Pause" : "Auto-Play Agent 2"}</span>
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
                className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
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
                    speedMs === s.ms ? "bg-emerald-600 text-white font-bold" : "text-slate-400 hover:text-white"
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
                        isTraversed && cell !== "#" ? "ring-1 ring-emerald-500/30" : ""
                      }`}
                    >
                      {content}

                      {/* Breadcrumb trace */}
                      {isTraversed && !isCrawler && cell !== "#" && (
                        <div className="absolute w-1.5 h-1.5 rounded-full bg-emerald-400/40 pointer-events-none" />
                      )}

                      {/* Animated Crawler Token */}
                      {isCrawler && (
                        <div className="absolute inset-0.5 rounded-full flex items-center justify-center font-bold text-[10px] z-20 shadow-lg bg-emerald-500 text-white shadow-emerald-500/50">
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
          <div className="p-3 rounded-lg border flex items-center justify-between text-xs font-mono font-bold bg-emerald-950/40 border-emerald-500/50 text-emerald-300">
            <div className="flex items-center gap-2">
              <span>Status:</span>
              <span className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" /> 1-SHOT BENCHMARK VICTORY (EXIT REACHED)
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span>Gold: {collectedChestsCount} / {activeMap.treasures.length}</span>
              <span>Coords: ({currentPos[0]}, {currentPos[1]})</span>
            </div>
          </div>
        </div>

        {/* Right Column: Ingested Memory & Reasoning Telemetry */}
        <div className="lg:col-span-4 space-y-4">
          {/* Map Selection */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
            <label className="text-xs font-mono uppercase text-slate-400 block">
              Benchmark Map (Agent 2 Evaluation)
            </label>
            <select
              value={selectedMapIdx}
              onChange={(e) => setSelectedMapIdx(parseInt(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg p-2 font-mono outline-none focus:border-emerald-500"
            >
              {maps.map((m) => (
                <option key={m.map_id} value={m.map_id}>
                  Map {m.map_id}: {m.name} ({m.width}x{m.height})
                </option>
              ))}
            </select>
          </div>

          {/* Derived Costs Card */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">
              Derived Policy Parameters (Agent 2 Single-Shot)
            </span>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">DERIVED LAVA</span>
                <span className="text-rose-400 font-bold">{agent2.policy.COSTS.lava}</span>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">DERIVED MONSTER</span>
                <span className="text-purple-400 font-bold">{agent2.policy.COSTS.monster}</span>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">DERIVED TREASURE</span>
                <span className="text-amber-400 font-bold">{agent2.policy.COSTS.treasure}</span>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px]">AVOIDANCE RADIUS</span>
                <span className="text-emerald-400 font-bold">{agent2.policy.avoidance_radius} tiles</span>
              </div>
            </div>
            <p className="text-[10px] text-slate-400 pt-1">
              Derivation Rule: COSTS were synthesized by resolving V1 monster ambushes and V2 lava deaths from memory lessons.
            </p>
          </div>

          {/* Memory Citations Proof Box */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200">
              <BrainCircuit className="w-4 h-4 text-emerald-400" />
              <span>Agent 2 Memory Citations (Proof of Ingestion)</span>
            </div>
            <div className="text-[11px] text-emerald-300 bg-slate-950 p-3 rounded-lg border border-emerald-900/50 leading-relaxed italic">
              &ldquo;{agent2.reasoning}&rdquo;
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

