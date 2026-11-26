import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import path from "path";
import fs from "fs";
import { promisify } from "util";

const execAsync = promisify(exec);

function getRepoRoot(): string {
  if (fs.existsSync(path.join(process.cwd(), "pipeline.py"))) {
    return process.cwd();
  }
  return path.resolve(process.cwd(), "..");
}

const REPO_ROOT = getRepoRoot();
const SIM_DATA_FILE = path.join(REPO_ROOT, "frontend", "public", "simulation_data.json");
const SIM_DASHBOARD_FILE = path.join(REPO_ROOT, "Simulation2", "evolution", "simulation_dashboard.json");

function getPythonExecutable(): string {
  if (process.env.PYTHON_PATH) {
    return process.env.PYTHON_PATH;
  }
  const venvPythonWin = path.join(REPO_ROOT, ".venv", "Scripts", "python.exe");
  if (fs.existsSync(venvPythonWin)) {
    return `"${venvPythonWin}"`;
  }
  const venvPythonPosix = path.join(REPO_ROOT, ".venv", "bin", "python");
  if (fs.existsSync(venvPythonPosix)) {
    return `"${venvPythonPosix}"`;
  }
  return "python";
}

function loadSimulationData() {
  for (const f of [SIM_DATA_FILE, SIM_DASHBOARD_FILE]) {
    if (fs.existsSync(f)) {
      try {
        const raw = fs.readFileSync(f, "utf-8");
        return JSON.parse(raw);
      } catch (err) {
        console.error("Error parsing simulation data:", err);
      }
    }
  }
  return null;
}

export async function GET() {
  const data = loadSimulationData();
  if (!data) {
    return NextResponse.json({ error: "Run Task 1 first" }, { status: 404 });
  }
  return NextResponse.json(data);
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const action = body.action || "task2"; // "task1", "task2", "dungeon"
    const py = getPythonExecutable();

    let flag = "--task2";
    if (action === "task1") flag = "--task1";
    if (action === "dungeon") flag = "--dungeon";

    const cmd = `${py} "${path.join(REPO_ROOT, "pipeline.py")}" ${flag}`;
    console.log(`[API /simulation] Executing: ${cmd}`);

    const { stdout } = await execAsync(cmd, {
      cwd: REPO_ROOT,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
      timeout: 120000,
    });

    console.log("[API /simulation] Output:", stdout);

    // Refresh simulation_data.json
    const data = loadSimulationData();
    return NextResponse.json({
      success: true,
      data,
      stdout,
    });
  } catch (err: any) {
    console.error("[API /simulation] Execution failed:", err);
    return NextResponse.json(
      {
        error: err.message || "Simulation execution failed",
        output: err.stdout || "",
      },
      { status: 500 }
    );
  }
}
