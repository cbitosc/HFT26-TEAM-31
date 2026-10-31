"use client";

import React, { useState, useEffect } from "react";
import { RefreshCw, AlertTriangle, Compass, Sparkles, Swords, BrainCircuit } from "lucide-react";
import Agent1DungeonComponent from "./Agent1DungeonComponent";
import Agent2DungeonComponent from "./Agent2DungeonComponent";

export default function SimulationTab() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeSubTab, setActiveSubTab] = useState<"agent1" | "agent2">("agent2");

  useEffect(() => {
    fetchSimulationData();
  }, []);

  const fetchSimulationData = async () => {
    try {
      const res = await fetch("/api/simulation");
      if (res.ok) {
        const json = await res.json();
        setData(json);
      } else {
        const staticRes = await fetch("/simulation_data.json");
        if (staticRes.ok) {
          const json = await staticRes.json();
          setData(json);
        }
      }
    } catch (e) {
      console.error("Failed to load simulation data:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAgent2 = async () => {
    try {
      const res = await fetch("/api/simulation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "task2" }),
      });
      if (res.ok) {
        await fetchSimulationData();
      }
    } catch (e) {
      console.error("Failed to execute Agent 2:", e);
    }
  };

  const handleReRunTask1 = async () => {
    try {
      const res = await fetch("/api/simulation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "task1" }),
      });
      if (res.ok) {
        await fetchSimulationData();
      }
    } catch (e) {
      console.error("Failed to execute Task 1:", e);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-sm font-mono text-slate-400">Loading Dungeon Simulation Engine & Memory Ledger...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto" />
        <h3 className="text-lg font-bold text-slate-200">Simulation Ledger Not Found</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Please run Task 1 first to synthesize the initial memory ledger.
        </p>
        <button
          onClick={handleRunAgent2}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold transition"
        >
          Initialize Dungeon Pipeline
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sub-Tabs: Agent 1 (Task 1) vs Agent 2 (Task 2) */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveSubTab("agent2")}
          className={`flex items-center space-x-2 py-2 px-4 text-xs font-bold rounded-lg transition ${activeSubTab === "agent2"
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
        >
          <BrainCircuit className="w-4 h-4 text-emerald-300" />
          <span>Task 2: Agent 2 (Single-Shot Memory Learner)</span>
          <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Pillar 4
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab("agent1")}
          className={`flex items-center space-x-2 py-2 px-4 text-xs font-bold rounded-lg transition ${activeSubTab === "agent1"
              ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
        >
          <Swords className="w-4 h-4 text-blue-300" />
          <span>Task 1: Agent 1 (Generations V1 &rarr; V4)</span>
          <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Genesis + G-T-C
          </span>
        </button>
      </div>

      {activeSubTab === "agent2" ? (
        <Agent2DungeonComponent
          maps={data.maps}
          agent2={data.agent2}
          totalFailureTraces={data.total_failure_traces_loaded}
          comparisonImage={data.v1_vs_agent2_image}
          onRunAgent2={handleRunAgent2}
        />
      ) : (
        <Agent1DungeonComponent
          maps={data.maps}
          generations={data.task1_generations}
          onReRunTask1={handleReRunTask1}
        />
      )}
    </div>
  );
}
