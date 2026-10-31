"""
streamlit_app.py - Modern Streamlit Web UI for AutoEvolve Dungeon Crawler.
Features an interactive 60 FPS HTML5 Canvas Auto-Play Simulation alongside
a Step-by-Step Scrubber, live telemetry HUD, multi-version comparison charts,
and JSON contract inspectors.
"""

import os
import json
import time
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

from core.contracts import Policy, TestResult, Critique
from core.map_generator import DungeonMap, load_fixed_maps
from core.engine import simulate
from viz.renderer import draw_dungeon_grid, get_version_style, COLORS


# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & DARK THEME STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AutoEvolve Dungeon Crawler",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 6px;
        padding: 8px 18px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        font-weight: bold;
    }
    .critique-box {
        background-color: #1e1b4b;
        border-left: 5px solid #a855f7;
        padding: 14px;
        border-radius: 6px;
        margin-top: 10px;
        color: #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DATA LOADERS & HELPERS
# -----------------------------------------------------------------------------
def load_all_maps():
    return load_fixed_maps()


def load_evolution_data():
    """Loads all persisted policy, test, and critique JSON files."""
    policies = []
    test_results = []
    critiques = []

    v = 1
    while os.path.exists(f"evolution/V{v}_policy.json"):
        with open(f"evolution/V{v}_policy.json", "r", encoding="utf-8") as f:
            policies.append(Policy.from_dict(json.load(f)))
        if os.path.exists(f"evolution/V{v}_test.json"):
            with open(f"evolution/V{v}_test.json", "r", encoding="utf-8") as f:
                test_results.append(TestResult.from_dict(json.load(f)))
        if os.path.exists(f"evolution/V{v}_critique.json"):
            with open(f"evolution/V{v}_critique.json", "r", encoding="utf-8") as f:
                critiques.append(Critique.from_dict(json.load(f)))
        v += 1

    return policies, test_results, critiques


def generate_canvas_simulation_html(dungeon: DungeonMap, path: list, cause: str, version: int, costs: dict) -> str:
    """
    Generates a standalone, 60 FPS animated HTML5 Canvas simulation component.
    Includes built-in Play/Pause, Step Scrubber, speed slider, animated hazards,
    sub-tile crawler interpolation, and particle explosions.
    """
    v_style = get_version_style(version)
    v_color = v_style["color"]

    sim_data = {
        "width": dungeon.width,
        "height": dungeon.height,
        "grid": dungeon.grid,
        "start": list(dungeon.start),
        "exit": list(dungeon.exit),
        "lava": [list(pos) for pos in dungeon.lava_cells],
        "monsters": [list(pos) for pos in dungeon.monsters],
        "treasures": [list(pos) for pos in dungeon.treasures],
        "path": [list(pos) for pos in path],
        "cause": cause,
        "version": version,
        "vColor": v_color,
        "costs": costs,
    }

    sim_json = json.dumps(sim_data)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{
                box-sizing: border-box;
            }}
            body {{
                margin: 0;
                padding: 4px;
                background-color: #0b1120;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #f8fafc;
                user-select: none;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                min-height: 100vh;
                overflow-x: hidden;
            }}
            #sim-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                max-width: 780px;
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
                padding: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
                position: relative;
                transition: all 0.2s ease-in-out;
            }}
            #controls-bar {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                width: 100%;
                margin-bottom: 10px;
                background: #0f172a;
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #334155;
            }}
            .controls-group {{
                display: flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
            }}
            button {{
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.15s, transform 0.1s;
                font-size: 13px;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }}
            button:hover {{
                background: #1d4ed8;
            }}
            button:active {{
                transform: scale(0.96);
            }}
            #btn-fullscreen {{
                background: #334155;
                border: 1px solid #475569;
            }}
            #btn-fullscreen:hover {{
                background: #475569;
            }}
            .scrubber-slider {{
                flex: 1;
                min-width: 120px;
                cursor: pointer;
                accent-color: #3b82f6;
            }}
            .badge {{
                font-family: monospace;
                font-weight: bold;
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 4px;
                background: #1e293b;
                border: 1px solid #475569;
                white-space: nowrap;
            }}
            #canvas-wrapper {{
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 4px 0;
            }}
            canvas {{
                max-width: 100%;
                height: auto;
                aspect-ratio: 14 / 12;
                border-radius: 8px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6);
                background: #0f172a;
                display: block;
            }}
            #status-banner {{
                margin-top: 8px;
                font-size: 13px;
                font-family: monospace;
                font-weight: bold;
                text-align: center;
                min-height: 22px;
                line-height: 22px;
            }}

            /* Fullscreen styling for container */
            #sim-container:fullscreen, #sim-container:-webkit-full-screen {{
                width: 100vw !important;
                height: 100vh !important;
                max-width: 100vw !important;
                max-height: 100vh !important;
                border-radius: 0 !important;
                border: none !important;
                padding: 16px 24px !important;
                margin: 0 !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
                align-items: center !important;
                background: #060911 !important;
            }}
            #sim-container:fullscreen #canvas-wrapper, #sim-container:-webkit-full-screen #canvas-wrapper {{
                flex: 1;
                min-height: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
            }}
            #sim-container:fullscreen canvas, #sim-container:-webkit-full-screen canvas {{
                max-height: 82vh !important;
                max-width: 92vw !important;
                width: auto !important;
                height: auto !important;
            }}
            #sim-container:fullscreen #controls-bar, #sim-container:-webkit-full-screen #controls-bar {{
                max-width: 1000px;
            }}
        </style>
    </head>
    <body>
        <div id="sim-container">
            <div id="controls-bar">
                <div class="controls-group">
                    <button id="btn-play">▶ Play</button>
                    <button id="btn-reset">🔄 Reset</button>
                </div>
                <input type="range" id="scrubber" class="scrubber-slider" min="0" max="{max(1, len(path)-1)}" value="0">
                <div class="controls-group">
                    <span id="step-label" class="badge">Step 0/{max(1, len(path)-1)}</span>
                    <span id="gold-label" class="badge" style="color: #facc15;">💰 0/{len(dungeon.treasures)}</span>
                    <select id="speed-select" style="background:#1e293b; color:white; border:1px solid #475569; border-radius:4px; padding:4px;">
                        <option value="0.5">0.5x</option>
                        <option value="1" selected>1.0x</option>
                        <option value="2">2.0x</option>
                        <option value="4">4.0x</option>
                    </select>
                    <button id="btn-fullscreen" title="Toggle Fullscreen (F)">⛶ Fullscreen</button>
                </div>
            </div>
            <div id="canvas-wrapper">
                <canvas id="dungeon-canvas"></canvas>
            </div>
            <div id="status-banner"></div>
        </div>

        <script>
            const DATA = {sim_json};
            const canvas = document.getElementById('dungeon-canvas');
            const ctx = canvas.getContext('2d');
            const btnPlay = document.getElementById('btn-play');
            const btnReset = document.getElementById('btn-reset');
            const scrubber = document.getElementById('scrubber');
            const stepLabel = document.getElementById('step-label');
            const goldLabel = document.getElementById('gold-label');
            const speedSelect = document.getElementById('speed-select');
            const statusBanner = document.getElementById('status-banner');
            const btnFullscreen = document.getElementById('btn-fullscreen');
            const simContainer = document.getElementById('sim-container');

            const CELL_SIZE = 42;
            canvas.width = DATA.width * CELL_SIZE;
            canvas.height = DATA.height * CELL_SIZE;

            let isPlaying = false;
            let currentStep = 0;
            let subProgress = 0.0;
            let speedMultiplier = 1.0;
            let particles = [];
            let collectedGold = new Set();

            function triggerParticles(cx, cy, color, count) {{
                for (let i = 0; i < count; i++) {{
                    const angle = Math.random() * Math.PI * 2;
                    const spd = 1.0 + Math.random() * 3.5;
                    particles.push({{
                        x: cx,
                        y: cy,
                        vx: Math.cos(angle) * spd,
                        vy: Math.sin(angle) * spd,
                        color: color,
                        life: 30 + Math.random() * 25,
                        maxLife: 55
                    }});
                }}
            }}

            function drawGrid() {{
                const now = performance.now() * 0.003;
                const pulse = (Math.sin(now) + 1.0) / 2.0;

                // 1. Draw floor and walls
                for (let y = 0; y < DATA.height; y++) {{
                    for (let x = 0; x < DATA.width; x++) {{
                        const px = x * CELL_SIZE;
                        const py = y * CELL_SIZE;

                        if (DATA.grid[y][x] === '#') {{
                            ctx.fillStyle = '#334155';
                            ctx.fillRect(px, py, CELL_SIZE, CELL_SIZE);
                            ctx.strokeStyle = '#475569';
                            ctx.strokeRect(px, py, CELL_SIZE, CELL_SIZE);
                        }} else {{
                            ctx.fillStyle = '#1e293b';
                            ctx.fillRect(px, py, CELL_SIZE, CELL_SIZE);
                            ctx.strokeStyle = '#0f172a';
                            ctx.strokeRect(px, py, CELL_SIZE, CELL_SIZE);
                        }}
                    }}
                }}

                // 2. Glowing Lava
                DATA.lava.forEach(([lx, ly]) => {{
                    const px = lx * CELL_SIZE;
                    const py = ly * CELL_SIZE;
                    const glowVal = Math.floor(180 + 75 * pulse);
                    ctx.fillStyle = `rgb(${{glowVal}}, 40, 40)`;
                    ctx.fillRect(px, py, CELL_SIZE, CELL_SIZE);

                    ctx.fillStyle = `rgba(249, 115, 22, ${{0.7 + 0.3 * pulse}})`;
                    ctx.beginPath();
                    ctx.arc(px + CELL_SIZE/2, py + CELL_SIZE/2, CELL_SIZE * 0.35, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 10px monospace';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('LAVA', px + CELL_SIZE/2, py + CELL_SIZE/2);
                }});

                // 3. Monsters
                DATA.monsters.forEach(([mx, my]) => {{
                    const cx = mx * CELL_SIZE + CELL_SIZE/2;
                    const cy = my * CELL_SIZE + CELL_SIZE/2;
                    const radius = CELL_SIZE * 0.38 + 2 * pulse;

                    ctx.fillStyle = '#a855f7';
                    ctx.beginPath();
                    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = '#f43f5e';
                    ctx.beginPath();
                    ctx.arc(cx, cy, radius * 0.7, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 12px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('M', cx, cy);
                }});

                // 4. Treasures
                DATA.treasures.forEach(([tx, ty]) => {{
                    const px = tx * CELL_SIZE + 6;
                    const py = ty * CELL_SIZE + 6;
                    const size = CELL_SIZE - 12;
                    const isTaken = collectedGold.has(`${{tx}},${{ty}}`);

                    if (isTaken) {{
                        ctx.fillStyle = '#713f12';
                        ctx.fillRect(px, py, size, size);
                        ctx.fillStyle = '#a16207';
                        ctx.font = 'bold 9px monospace';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('OPEN', px + size/2, py + size/2);
                    }} else {{
                        ctx.fillStyle = '#eab308';
                        ctx.fillRect(px, py, size, size);
                        ctx.strokeStyle = '#fef08a';
                        ctx.lineWidth = 2;
                        ctx.strokeRect(px, py, size, size);
                        ctx.fillStyle = '#78350f';
                        ctx.font = 'bold 12px monospace';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('$', px + size/2, py + size/2);
                    }}
                }});

                // 5. Start and Exit
                const [sx, sy] = DATA.start;
                ctx.fillStyle = '#38bdf8';
                ctx.beginPath();
                ctx.arc(sx * CELL_SIZE + CELL_SIZE/2, sy * CELL_SIZE + CELL_SIZE/2, CELL_SIZE * 0.4, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 11px monospace';
                ctx.fillText('S', sx * CELL_SIZE + CELL_SIZE/2, sy * CELL_SIZE + CELL_SIZE/2);

                const [ex, ey] = DATA.exit;
                ctx.fillStyle = '#22c55e';
                ctx.beginPath();
                ctx.arc(ex * CELL_SIZE + CELL_SIZE/2, ey * CELL_SIZE + CELL_SIZE/2, CELL_SIZE * 0.42, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 9px monospace';
                ctx.fillText('EXIT', ex * CELL_SIZE + CELL_SIZE/2, ey * CELL_SIZE + CELL_SIZE/2);

                // 6. Path trail up to current step
                if (DATA.path.length > 0) {{
                    ctx.strokeStyle = DATA.vColor;
                    ctx.lineWidth = 3.5;
                    ctx.beginPath();
                    for (let i = 0; i <= currentStep; i++) {{
                        const [px, py] = DATA.path[i];
                        const cx = px * CELL_SIZE + CELL_SIZE/2;
                        const cy = py * CELL_SIZE + CELL_SIZE/2;
                        if (i === 0) ctx.moveTo(cx, cy);
                        else ctx.lineTo(cx, cy);
                    }}
                    ctx.stroke();

                    // Points on trail
                    for (let i = 0; i <= currentStep; i++) {{
                        const [px, py] = DATA.path[i];
                        ctx.fillStyle = DATA.vColor;
                        ctx.beginPath();
                        ctx.arc(px * CELL_SIZE + CELL_SIZE/2, py * CELL_SIZE + CELL_SIZE/2, 4, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                }}

                // 7. Crawler player (interpolated motion)
                if (DATA.path.length > 0) {{
                    const cur = DATA.path[currentStep];
                    let lx = cur[0];
                    let ly = cur[1];

                    if (isPlaying && currentStep < DATA.path.length - 1) {{
                        const nxt = DATA.path[currentStep + 1];
                        lx = cur[0] + (nxt[0] - cur[0]) * subProgress;
                        ly = cur[1] + (nxt[1] - cur[1]) * subProgress;
                    }}

                    const cx = lx * CELL_SIZE + CELL_SIZE/2;
                    const cy = ly * CELL_SIZE + CELL_SIZE/2;

                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(cx, cy, CELL_SIZE * 0.38, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = DATA.vColor;
                    ctx.beginPath();
                    ctx.arc(cx, cy, CELL_SIZE * 0.30, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 10px monospace';
                    ctx.fillText(`V${{DATA.version}}`, cx, cy);

                    // Termination marker
                    if (currentStep === DATA.path.length - 1) {{
                        if (DATA.cause === 'lava') {{
                            ctx.fillStyle = '#f87171';
                            ctx.font = 'bold 12px monospace';
                            ctx.fillText('☠ BURNED IN LAVA', cx, cy - 26);
                        }} else if (DATA.cause === 'monster') {{
                            ctx.fillStyle = '#c084fc';
                            ctx.font = 'bold 12px monospace';
                            ctx.fillText('☠ SLAIN BY MONSTER', cx, cy - 26);
                        }} else if (DATA.cause === 'success') {{
                            ctx.fillStyle = '#4ade80';
                            ctx.font = 'bold 13px monospace';
                            ctx.fillText('★ DUNGEON CLEARED!', cx, cy - 26);
                        }}
                    }}
                }}

                // 8. Particles
                for (let i = particles.length - 1; i >= 0; i--) {{
                    const p = particles[i];
                    p.x += p.vx;
                    p.y += p.vy;
                    p.life -= 1;
                    if (p.life <= 0) {{
                        particles.splice(i, 1);
                        continue;
                    }}
                    const alpha = p.life / p.maxLife;
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = alpha;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, Math.max(1, 4 * alpha), 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1.0;
                }}
            }}

            function updateUI() {{
                scrubber.value = currentStep;
                stepLabel.textContent = `Step ${{currentStep}}/${{DATA.path.length - 1}}`;

                // Calculate treasures up to currentStep
                collectedGold.clear();
                for (let i = 0; i <= currentStep; i++) {{
                    const [px, py] = DATA.path[i];
                    DATA.treasures.forEach(([tx, ty]) => {{
                        if (px === tx && py === ty) {{
                            collectedGold.add(`${{tx}},${{ty}}`);
                        }}
                    }});
                }}
                goldLabel.textContent = `💰 ${{collectedGold.size}}/${{DATA.treasures.length}}`;

                // Status banner
                if (currentStep === DATA.path.length - 1) {{
                    if (DATA.cause === 'lava') {{
                        statusBanner.innerHTML = '<span style="color:#ef4444;">☠ FAILED: Crawler incinerated in lava shortcut!</span>';
                    }} else if (DATA.cause === 'monster') {{
                        statusBanner.innerHTML = '<span style="color:#a855f7;">☠ FAILED: Crawler greedily entered monster threat zone and was slain!</span>';
                    }} else if (DATA.cause === 'success') {{
                        statusBanner.innerHTML = '<span style="color:#22c55e;">★ SUCCESS: Crawler cleared dungeon alive and reached Exit!</span>';
                    }}
                }} else {{
                    statusBanner.innerHTML = `<span style="color:#38bdf8;">▶ Advancing through dungeon (Step ${{currentStep}} of ${{DATA.path.length - 1}})...</span>`;
                }}
            }}

            function loop() {{
                if (isPlaying) {{
                    if (currentStep < DATA.path.length - 1) {{
                        subProgress += 0.06 * speedMultiplier;
                        if (subProgress >= 1.0) {{
                            subProgress = 0.0;
                            currentStep += 1;
                            updateUI();

                            // Trigger particle effects on events
                            const [cx, cy] = [DATA.path[currentStep][0] * CELL_SIZE + CELL_SIZE/2, DATA.path[currentStep][1] * CELL_SIZE + CELL_SIZE/2];
                            DATA.treasures.forEach(([tx, ty]) => {{
                                if (DATA.path[currentStep][0] === tx && DATA.path[currentStep][1] === ty) {{
                                    triggerParticles(cx, cy, '#eab308', 25);
                                }}
                            }});

                            if (currentStep === DATA.path.length - 1) {{
                                if (DATA.cause === 'lava') triggerParticles(cx, cy, '#f97316', 40);
                                else if (DATA.cause === 'monster') triggerParticles(cx, cy, '#d946ef', 40);
                                else if (DATA.cause === 'success') triggerParticles(cx, cy, '#4ade80', 40);
                                isPlaying = false;
                                btnPlay.textContent = '▶ Play';
                            }}
                        }}
                    }} else {{
                        isPlaying = false;
                        btnPlay.textContent = '▶ Play';
                    }}
                }}

                drawGrid();
                requestAnimationFrame(loop);
            }}

            // Event Listeners
            btnPlay.addEventListener('click', () => {{
                if (currentStep >= DATA.path.length - 1) {{
                    currentStep = 0;
                    subProgress = 0.0;
                }}
                isPlaying = !isPlaying;
                btnPlay.textContent = isPlaying ? '⏸ Pause' : '▶ Play';
            }});

            btnReset.addEventListener('click', () => {{
                isPlaying = false;
                btnPlay.textContent = '▶ Play';
                currentStep = 0;
                subProgress = 0.0;
                particles = [];
                updateUI();
            }});

            scrubber.addEventListener('input', (e) => {{
                isPlaying = false;
                btnPlay.textContent = '▶ Play';
                currentStep = parseInt(e.target.value);
                subProgress = 0.0;
                updateUI();
            }});

            speedSelect.addEventListener('change', (e) => {{
                speedMultiplier = parseFloat(e.target.value);
            }});

            // Fullscreen API Handling
            function toggleFullscreen() {{
                const isFull = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
                if (!isFull) {{
                    const req = simContainer.requestFullscreen || simContainer.webkitRequestFullscreen || simContainer.mozRequestFullScreen || simContainer.msRequestFullscreen;
                    if (req) {{
                        req.call(simContainer).catch(err => {{
                            console.warn("Fullscreen request error:", err);
                        }});
                    }}
                }} else {{
                    const exit = document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen;
                    if (exit) {{
                        exit.call(document);
                    }}
                }}
            }}

            btnFullscreen.addEventListener('click', toggleFullscreen);

            function updateFullscreenBtn() {{
                const isFull = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
                btnFullscreen.textContent = isFull ? '🗗 Exit' : '⛶ Fullscreen';
                btnFullscreen.title = isFull ? 'Exit Fullscreen (Esc or F)' : 'Expand to Fullscreen (F)';
            }}

            document.addEventListener('fullscreenchange', updateFullscreenBtn);
            document.addEventListener('webkitfullscreenchange', updateFullscreenBtn);
            document.addEventListener('mozfullscreenchange', updateFullscreenBtn);
            document.addEventListener('MSFullscreenChange', updateFullscreenBtn);

            // Keyboard shortcuts
            window.addEventListener('keydown', (e) => {{
                if (e.code === 'Space') {{
                    e.preventDefault();
                    btnPlay.click();
                }} else if (e.code === 'KeyR') {{
                    btnReset.click();
                }} else if (e.code === 'KeyF') {{
                    toggleFullscreen();
                }}
            }});

            updateUI();
            requestAnimationFrame(loop);
        </script>
    </body>
    </html>
    """
    return html_code


# -----------------------------------------------------------------------------
# MAIN APP HEADER & INITIALIZATION
# -----------------------------------------------------------------------------
maps = load_all_maps()
policies, test_results, critiques = load_evolution_data()

# Ensure evolution data is available
if not policies:
    st.info("No evolution run detected. Running initial evolution protocol...")
    from main import main as run_main
    run_main()
    policies, test_results, critiques = load_evolution_data()

st.title("⚔️ AutoEvolve Dungeon Crawler: Simulation Lab")
st.markdown("**Dual-Phase Autonomous Policy Evolution**: *Phase 0 Genesis (Seed & Prompt Meta-Evolution)* $\\to$ *Phase 1 G-T-C Closed Loop*")

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🎮 Simulation Controls")

    # Version selection
    ver_options = [p.version for p in policies]
    ver_labels = {
        1: "V1: Chaotic (100% Lava Deaths)",
        2: "V2: Greedy Looter (96% Monster Deaths)",
        3: "V3: Overly Cautious (100% Survival, 0 Gold)",
        4: "V4: Optimal Master (100% Survival, All Gold)",
    }
    selected_ver = st.selectbox(
        "Select Generation to Inspect:",
        options=ver_options,
        format_func=lambda v: ver_labels.get(v, f"Version {v}"),
        index=min(3, len(ver_options) - 1)
    )

    # Map selection
    map_names = [f"Map {m.map_id}: {m.name}" for m in maps]
    selected_map_name = st.selectbox("Select Dungeon Map:", options=map_names, index=0, key="sim_map_selector")
    selected_map_idx = int(selected_map_name.split(":")[0].replace("Map", "").strip())
    active_map = maps[selected_map_idx]

    st.markdown("---")
    st.subheader("⚙️ Meta-Evolution Runner")

    if st.button("🚀 Re-Run AutoEvolve Loop", use_container_width=True):
        with st.spinner("Executing Phase 0 Genesis & Phase 1 G-T-C Evolution Loop..."):
            from main import main as run_main
            run_main()
            st.cache_data.clear()
            st.success("Evolution protocol successfully executed!")
            st.rerun()

    # Featherless status
    api_key = os.getenv("FEATHERLESS_API_KEY", "")
    if api_key and api_key != "your_key_here":
        st.success("🟢 Featherless API Connected")
    else:
        st.warning("🟡 Calibrated Local Fallback Active")

    st.markdown("---")
    st.caption("AutoEvolve Dungeon Crawler v2.0 • Python 3.10+ & Streamlit")


# -----------------------------------------------------------------------------
# ACTIVE VERSION TELEMETRY BANNER
# -----------------------------------------------------------------------------
active_policy = next(p for p in policies if p.version == selected_ver)
active_tr = next((tr for tr in test_results if tr.policy_version == selected_ver), None)
active_cr = next((cr for idx, cr in enumerate(critiques) if idx + 1 == selected_ver), None)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Generation", f"Version {active_policy.version}")
with col2:
    succ_rate = f"{active_tr.success_rate * 100:.0f}%" if active_tr else "N/A"
    st.metric("Survival / Clear Rate", succ_rate)
with col3:
    lava_pct = f"{active_tr.death_by_lava_pct:.0f}%" if active_tr else "N/A"
    st.metric("Lava Incinerations", lava_pct)
with col4:
    monst_pct = f"{active_tr.death_by_monster_pct:.0f}%" if active_tr else "N/A"
    st.metric("Monster Deaths", monst_pct)
with col5:
    score_val = f"{active_cr.score:.3f}" if active_cr else "N/A"
    st.metric("Fitness Score", score_val)

st.markdown("---")

# -----------------------------------------------------------------------------
# MAIN APP TABS
# -----------------------------------------------------------------------------
tab_sim, tab_matrix, tab_genesis, tab_contracts = st.tabs([
    "🕹️ Auto-Play & Scrub Simulation",
    "📈 Evolution Trajectory & Matrix",
    "🧬 Phase 0 Genesis & Prompts",
    "📜 JSON Contracts"
])

# -----------------------------------------------------------------------------
# TAB 1: AUTO-PLAY & SCRUB SIMULATION
# -----------------------------------------------------------------------------
with tab_sim:
    # Compute simulated path for current version and map
    path, cause, collected_gold, total_steps = simulate(active_map, active_policy, run_seed=0)

    header_c1, header_c2 = st.columns([3, 1])
    with header_c1:
        st.subheader(f"🎮 Real-Time Simulation — {active_map.name}")
        st.caption("Press **▶ Play** to watch continuous auto-play, drag the **Scrubber bar** below the canvas, or click **⛶ Fullscreen** / press **[F]**.")
    with header_c2:
        theater_mode = st.toggle("🖥️ Expanded View", value=False, help="Expand the simulation canvas across the full page width.")

    canvas_html = generate_canvas_simulation_html(
        active_map,
        path,
        cause,
        selected_ver,
        active_policy.COSTS
    )

    if theater_mode:
        # Full-width theater view
        components.html(
            canvas_html,
            height=660,
            scrolling=False
        )

        st.markdown("---")
        tel_c1, tel_c2, tel_c3 = st.columns([1, 1, 1.2])
        with tel_c1:
            st.markdown("#### 📋 Run Summary")
            st.markdown(f"""
            - **Map**: `{active_map.name}` (`{active_map.width}x{active_map.height}`)
            - **Steps Taken**: `{len(path)} steps`
            - **Outcome**: `{"100% CLEAR" if cause == "success" else cause.upper()}`
            - **Gold Collected**: `{len(active_map.treasures)} chests`
            """)
        with tel_c2:
            st.markdown("#### ⚙️ Policy Costs")
            st.info(f"**Lava**: `{active_policy.COSTS.get('lava')}` | **Monster**: `{active_policy.COSTS.get('monster')}`\n\n**Treasure**: `{active_policy.COSTS.get('treasure')}` | **Radius**: `{active_policy.avoidance_radius}`")
        with tel_c3:
            st.markdown("#### 🧠 Critique LLM Diagnosis")
            if active_cr:
                st.markdown(f"""
                <div class="critique-box">
                    <b>Directive:</b> <i>"{active_cr.instruction_for_next_generator}"</i>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Split column view
        sim_col_left, sim_col_right = st.columns([1.6, 1])

        with sim_col_left:
            components.html(
                canvas_html,
                height=660,
                scrolling=False
            )

        with sim_col_right:
            st.subheader("📋 Policy Inspector & Telemetry")

            # Telemetry Card
            st.markdown(f"""
            - **Dungeon Map**: `Map {active_map.map_id}: {active_map.name}`
            - **Grid Dimensions**: `{active_map.width} x {active_map.height} tiles`
            - **Total Path Steps**: `{len(path)} steps`
            - **Available Gold**: `{len(active_map.treasures)} chests`
            - **Benchmark Outcome**: `{"100% CLEAR" if cause == "success" else cause.upper()}`
            """)

            # Policy Parameters Card
            st.markdown("#### ⚙️ Policy Subjective Costs")
            p_c1, p_c2 = st.columns(2)
            with p_c1:
                st.info(f"**Lava Penalty**: `{active_policy.COSTS.get('lava')}`\n\n**Monster Penalty**: `{active_policy.COSTS.get('monster')}`")
            with p_c2:
                st.info(f"**Treasure Incentive**: `{active_policy.COSTS.get('treasure')}`\n\n**Avoidance Radius**: `{active_policy.avoidance_radius} tiles`")

            # Critique LLM Feedback Box
            st.markdown("#### 🧠 Critique LLM Diagnosis")
            if active_cr:
                st.markdown(f"""
                <div class="critique-box">
                    <b>Root Cause:</b> {active_cr.root_cause}<br><br>
                    <b>Actionable Directive for Next Version:</b><br>
                    <i>"{active_cr.instruction_for_next_generator}"</i>
                </div>
                """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 2: MULTI-VERSION MATRIX & PROGRESSION CHARTS
# -----------------------------------------------------------------------------
with tab_matrix:
    st.subheader("📊 Multi-Generation Milestone Summary")

    matrix_rows = []
    for p, tr, cr in zip(policies, test_results, critiques):
        matrix_rows.append({
            "Version": f"V{p.version}",
            "Score": cr.score,
            "Clear Rate": f"{tr.success_rate * 100:.0f}%",
            "Lava Deaths": f"{tr.death_by_lava_pct:.0f}%",
            "Monster Deaths": f"{tr.death_by_monster_pct:.0f}%",
            "Avg Gold Looted": tr.avg_treasure,
            "Avg Steps": tr.avg_steps,
            "Changelog": p.changelog
        })
    st.dataframe(matrix_rows, use_container_width=True)

    # Progress Charts
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        st.markdown("#### 🏆 Fitness Score Progression (Goal > 0.900)")
        scores_dict = {f"V{p.version}": cr.score for p, cr in zip(policies, critiques)}
        st.line_chart(scores_dict)

    with c_chart2:
        st.markdown("#### 💀 Hazard Failure Evolution Breakdown")
        hazards_data = {
            "Lava Deaths %": [tr.death_by_lava_pct for tr in test_results],
            "Monster Deaths %": [tr.death_by_monster_pct for tr in test_results],
            "Clear Rate %": [tr.success_rate * 100 for tr in test_results]
        }
        st.bar_chart(hazards_data)

    # 2x2 Comparison Image
    if os.path.exists("evolution/comparison_grid.png"):
        st.markdown("---")
        st.markdown("#### 🖼️ Multi-Generation 2x2 Path Comparison Grid")
        st.image("evolution/comparison_grid.png", use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 3: PHASE 0 GENESIS & META-EVOLVED PROMPTS
# -----------------------------------------------------------------------------
with tab_genesis:
    st.subheader("🧬 Phase 0 Genesis: AutoEvolve Before the Main Loop")
    st.markdown("""
    Before Phase 1 begins, the Meta-Evolution protocol evolves the starting point:
    1. **Seed Tournament**: Evaluates 5 candidate parameter seeds on rapid Genesis maps.
    2. **Meta-Prompt Synthesis**: The Featherless LLM (`meta-llama/Meta-Llama-3.1-70B-Instruct`) rewrites the system prompts for Generator and Critique to make them uncompromisingly strict.
    """)

    if os.path.exists("evolution/evolved_prompts.json"):
        with open("evolution/evolved_prompts.json", "r", encoding="utf-8") as f:
            evolved = json.load(f)

        g_col, c_col = st.columns(2)
        with g_col:
            st.markdown("#### 🤖 Evolved Generator System Prompt")
            st.text_area("Generator System", evolved.get("generator_system", ""), height=220)
        with c_col:
            st.markdown("#### ⚖️ Evolved Critique System Prompt")
            st.text_area("Critique System", evolved.get("critique_system", ""), height=220)


# -----------------------------------------------------------------------------
# TAB 4: JSON CONTRACTS INSPECTOR
# -----------------------------------------------------------------------------
with tab_contracts:
    st.subheader("📜 Communication Protocol: JSON Payloads")
    st.markdown("Inspect the exact data structures exchanged between Generator, Tester, and Critique.")

    v_select = st.radio("Select Payload Version:", [f"V{p.version}" for p in policies], horizontal=True)
    v_idx = int(v_select.replace("V", ""))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Policy {v_select} (Generator $\\to$ Tester)**")
        if os.path.exists(f"evolution/V{v_idx}_policy.json"):
            with open(f"evolution/V{v_idx}_policy.json") as f:
                st.json(json.load(f))

    with c2:
        st.markdown(f"**TestResult {v_select} (Tester $\\to$ Critique)**")
        if os.path.exists(f"evolution/V{v_idx}_test.json"):
            with open(f"evolution/V{v_idx}_test.json") as f:
                st.json(json.load(f))

    with c3:
        st.markdown(f"**Critique {v_select} (Critique $\\to$ Generator)**")
        if os.path.exists(f"evolution/V{v_idx}_critique.json"):
            with open(f"evolution/V{v_idx}_critique.json") as f:
                st.json(json.load(f))
