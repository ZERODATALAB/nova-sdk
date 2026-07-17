"""
nova-cockpit — Molecular Cockpit 3D
====================================
Web dashboard showing infrastructure as a living organism.
Three.js 3D rendering: organic cells, animated synapses, camera controls.

One command: nova demo  -> cockpit + live scan + immune engine
"""

import time
import threading
from flask import Flask, render_template_string, jsonify
from nova_synapse.engine import get_engine
from nova_cytokine.engine import CytokineEngine

# Feature gate — demo is visually complete but functionally capped
DEMO_CONFIG = {
    "max_organs": 10,
    "max_scan_duration": 300,       # 5 min
    "export_enabled": False,
    "hebbian_learning": False,
    "multi_instance": False,
    "max_alert_rules": 3,
}

# =============================================================================
# DEMO DATA — shown when no real organs exist yet (first launch)
# =============================================================================
DEMO_ORGANS = [
    {"ip": "10.0.0.1",    "mac": "aa:bb:cc:dd:ee:01", "hostname": "core-router",      "dna": "d3adf00d00000001", "type": "gateway"},
    {"ip": "10.0.0.10",   "mac": "aa:bb:cc:dd:ee:02", "hostname": "web-01",            "dna": "c0ffee0000000002", "type": "server"},
    {"ip": "10.0.0.11",   "mac": "aa:bb:cc:dd:ee:03", "hostname": "db-01",             "dna": "b00b1e0000000003", "type": "database"},
    {"ip": "10.0.0.20",   "mac": "aa:bb:cc:dd:ee:04", "hostname": "workstation-04",    "dna": "f00dface00000004", "type": "endpoint"},
    {"ip": "10.0.0.21",   "mac": "aa:bb:cc:dd:ee:05", "hostname": "printer-01",        "dna": "deadbeef00000005", "type": "iot"},
    {"ip": "10.0.0.30",   "mac": "aa:bb:cc:dd:ee:06", "hostname": "nas-storage",       "dna": "facade0000000006", "type": "storage"},
    {"ip": "10.0.0.40",   "mac": "aa:bb:cc:dd:ee:07", "hostname": "camera-garage",     "dna": "a1b2c3d400000007", "type": "iot"},
    {"ip": "10.0.0.50",   "mac": "aa:bb:cc:dd:ee:08", "hostname": "tv-living",         "dna": "e5f6a7b800000008", "type": "iot"},
]

DEMO_SYNAPSES = [
    {"a": "10.0.0.1",  "b": "10.0.0.10", "protocol": "TCP",  "port": 443,  "weight": 8.5},
    {"a": "10.0.0.1",  "b": "10.0.0.11", "protocol": "TCP",  "port": 5432, "weight": 6.2},
    {"a": "10.0.0.10", "b": "10.0.0.11", "protocol": "TCP",  "port": 5432, "weight": 9.1},
    {"a": "10.0.0.1",  "b": "10.0.0.20", "protocol": "TCP",  "port": 443,  "weight": 3.7},
    {"a": "10.0.0.1",  "b": "10.0.0.21", "protocol": "UDP",  "port": 631,  "weight": 1.5},
    {"a": "10.0.0.1",  "b": "10.0.0.30", "protocol": "TCP",  "port": 445,  "weight": 5.0},
    {"a": "10.0.0.1",  "b": "10.0.0.40", "protocol": "TCP",  "port": 554,  "weight": 2.1},
    {"a": "10.0.0.1",  "b": "10.0.0.50", "protocol": "UDP",  "port": 1900, "weight": 0.8},
    {"a": "10.0.0.10", "b": "10.0.0.30", "protocol": "TCP",  "port": 445,  "weight": 4.3},
]

# =============================================================================
# 3D MOLECULAR COCKPIT HTML
# =============================================================================
COCKPIT_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NOVA — Molecular Cockpit</title>
<style>
  :root {
    --bg: #060a10;
    --surface: rgba(12,20,28,0.95);
    --border: rgba(255,255,255,0.04);
    --text: #c0c8d4;
    --muted: #6a7a8a;
    --accent: #7eb8da;
    --gold: #d4b896;
    --mint: #8cc9b8;
    --warn: #ffa94d;
    --crit: #ff6b6b;
    --lav: #b39ddb;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    overflow: hidden;
  }
  #app { display: flex; height: 100vh; }
  /* Sidebar */
  .sidebar {
    width: 320px;
    min-width: 320px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    z-index: 10;
  }
  .sidebar-header {
    padding: 24px 20px 16px;
    border-bottom: 1px solid var(--border);
  }
  .sidebar-header h1 {
    font-size: 1.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--gold), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
  }
  .sidebar-header .sub {
    font-size: 0.58rem;
    color: var(--muted);
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    margin-top: 2px;
  }
  .mode-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.55rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    margin-top: 6px;
  }
  .mode-badge.demo { background: rgba(255,169,77,0.15); color: var(--warn); }
  .mode-badge.live { background: rgba(140,201,184,0.15); color: var(--mint); }
  .stats { flex: 1; padding: 12px; overflow-y: auto; }
  .stat-card {
    background: rgba(255,255,255,0.015);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 8px;
  }
  .stat-card .label {
    font-size: 0.5rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
  }
  .stat-card .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #e0e4ec;
    margin-top: 4px;
  }
  .stat-card .unit { font-size: 0.6rem; color: var(--muted); font-weight: 400; }
  .stat-card .locked {
    font-size: 0.55rem;
    color: var(--warn);
    margin-top: 4px;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    display: none;
  }
  .stat-card .locked.visible { display: block; }
  .upgrade-banner {
    margin: 12px;
    padding: 12px;
    background: rgba(212,184,150,0.06);
    border: 1px solid rgba(212,184,150,0.15);
    border-radius: 10px;
    text-align: center;
  }
  .upgrade-banner a {
    color: var(--gold);
    text-decoration: none;
    font-size: 0.62rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
  }
  .upgrade-banner a:hover { text-decoration: underline; }
  /* Main viewport */
  .main { flex: 1; display: flex; flex-direction: column; position: relative; }
  .toolbar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 5;
  }
  .pulse-dot {
    width: 9px; height: 9px; border-radius: 50%;
    animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--mint); } 50% { opacity: 0.3; box-shadow: none; } }
  .toolbar span { font-size: 0.65rem; color: var(--muted); font-family: 'JetBrains Mono', 'Courier New', monospace; }
  #three-container { flex: 1; cursor: grab; position: relative; }
  #three-container canvas { display: block; width: 100%; height: 100%; }
  #three-container:active { cursor: grabbing; }
  /* Alerts footer */
  .alerts {
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 6px 16px;
    max-height: 100px;
    overflow-y: auto;
    z-index: 5;
  }
  .alert-line {
    font-size: 0.6rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    padding: 3px 0;
  }
  .alert-line.critical { color: var(--crit); }
  .alert-line.high { color: var(--warn); }
  .alert-line.medium { color: #ffd43b; }
  .alert-line.low { color: var(--accent); }
  .alert-line.info { color: var(--mint); }
  /* Tooltip */
  .tooltip {
    position: absolute;
    background: rgba(12,20,28,0.97);
    border: 1px solid rgba(126,184,218,0.3);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    pointer-events: none;
    display: none;
    z-index: 20;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  }
  .tooltip .tt-ip { color: var(--accent); font-weight: 700; }
  .tooltip .tt-host { color: var(--gold); }
  .tooltip .tt-dna { color: var(--muted); font-size: 0.55rem; }
  #loading {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    z-index: 2;
  }
  .loading-text {
    font-size: 0.7rem; color: var(--muted);
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    animation: blink 1.5s infinite;
  }
  @keyframes blink { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }
</style>
</head>
<body>
<div id="app">
  <div class="sidebar">
    <div class="sidebar-header">
      <h1>NOVA Molecular Cockpit</h1>
      <div class="sub">NOVA/v3 &middot; Passive Discovery</div>
      <div class="mode-badge demo" id="mode-badge">DEMO</div>
    </div>
    <div class="stats">
      <div class="stat-card">
        <div class="label">Organs</div>
        <div class="value" id="stat-organs">--</div>
        <div class="locked" id="lock-organs">[LOCKED] Max 10 in demo</div>
      </div>
      <div class="stat-card">
        <div class="label">Synapses</div>
        <div class="value" id="stat-synapses">--</div>
      </div>
      <div class="stat-card">
        <div class="label">Packets Observed</div>
        <div class="value" id="stat-packets">--</div>
      </div>
      <div class="stat-card">
        <div class="label">Baseline</div>
        <div class="value" id="stat-baseline" style="font-size:0.95rem;">--</div>
      </div>
      <div class="stat-card">
        <div class="label">Scan Time Remaining</div>
        <div class="value" id="stat-time" style="font-size:0.95rem;">--</div>
        <div class="locked" id="lock-time">[LOCKED] 5 min limit — upgrade for unlimited</div>
      </div>
      <div class="stat-card">
        <div class="label">Hebbian Learning</div>
        <div class="value" id="stat-hebbian" style="font-size:0.8rem;">Frozen (demo)</div>
        <div class="locked">[LOCKED] Upgrade for adaptive learning</div>
      </div>
    </div>
    <div class="upgrade-banner">
      <a href="https://0data.fr/products/nova" target="_blank">[UPGRADE] Unlimited organs, adaptive learning, multi-instance sync</a>
    </div>
  </div>

  <div class="main">
    <div class="toolbar">
      <div class="pulse-dot" id="pulse-dot" style="background:#ffa94d;"></div>
      <span id="toolbar-status">DEMO MODE — simulation active</span>
    </div>
    <div id="three-container"><canvas></canvas></div>
    <div id="loading"><div class="loading-text">Initializing molecular view...</div></div>
    <div class="alerts" id="alerts">
      <div class="alert-line info">[INFO] Demo mode — start a scan to discover your real infrastructure</div>
    </div>
    <div class="tooltip" id="tooltip"></div>
  </div>
</div>

<script>
  // Demo data — shown immediately before real scan populates
  const DEMO_ORGANS = [
    {ip:"10.0.0.1",mac:"aa:bb:cc:dd:ee:01",hostname:"core-router",dna:"d3adf00d00000001",type:"gateway"},
    {ip:"10.0.0.10",mac:"aa:bb:cc:dd:ee:02",hostname:"web-01",dna:"c0ffee0000000002",type:"server"},
    {ip:"10.0.0.11",mac:"aa:bb:cc:dd:ee:03",hostname:"db-01",dna:"b00b1e0000000003",type:"database"},
    {ip:"10.0.0.20",mac:"aa:bb:cc:dd:ee:04",hostname:"workstation-04",dna:"f00dface00000004",type:"endpoint"},
    {ip:"10.0.0.21",mac:"aa:bb:cc:dd:ee:05",hostname:"printer-01",dna:"deadbeef00000005",type:"iot"},
    {ip:"10.0.0.30",mac:"aa:bb:cc:dd:ee:06",hostname:"nas-storage",dna:"facade0000000006",type:"storage"},
    {ip:"10.0.0.40",mac:"aa:bb:cc:dd:ee:07",hostname:"camera-garage",dna:"a1b2c3d400000007",type:"iot"},
    {ip:"10.0.0.50",mac:"aa:bb:cc:dd:ee:08",hostname:"tv-living",dna:"e5f6a7b800000008",type:"iot"}
  ];
  const DEMO_SYNAPSES = [
    {a:"10.0.0.1",b:"10.0.0.10",protocol:"TCP",port:443,weight:8.5},
    {a:"10.0.0.1",b:"10.0.0.11",protocol:"TCP",port:5432,weight:6.2},
    {a:"10.0.0.10",b:"10.0.0.11",protocol:"TCP",port:5432,weight:9.1},
    {a:"10.0.0.1",b:"10.0.0.20",protocol:"TCP",port:443,weight:3.7},
    {a:"10.0.0.1",b:"10.0.0.21",protocol:"UDP",port:631,weight:1.5},
    {a:"10.0.0.1",b:"10.0.0.30",protocol:"TCP",port:445,weight:5.0},
    {a:"10.0.0.1",b:"10.0.0.40",protocol:"TCP",port:554,weight:2.1},
    {a:"10.0.0.1",b:"10.0.0.50",protocol:"UDP",port:1900,weight:0.8},
    {a:"10.0.0.10",b:"10.0.0.30",protocol:"TCP",port:445,weight:4.3}
  ];
</script>
<script>

// =============================================================================
// NOVA Molecular Cockpit — Canvas 2D (zero dependencies, mobile-first)
// =============================================================================

const container = document.getElementById('three-container');
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

let nodes = [], edges = [];
let useDemo = true;

// Camera
let panX = 0, panY = 0, zoom = 0.8;
let dragStart = null, isDragging = false;

// Touch/mouse
canvas.addEventListener('mousedown', e => { dragStart = {x: e.clientX, y: e.clientY}; isDragging = true; });
canvas.addEventListener('touchstart', e => { const t = e.touches[0]; dragStart = {x: t.clientX, y: t.clientY}; isDragging = true; e.preventDefault(); }, {passive:false});
window.addEventListener('mouseup', () => { isDragging = false; dragStart = null; });
window.addEventListener('touchend', () => { isDragging = false; dragStart = null; });
window.addEventListener('mousemove', e => { if(!isDragging||!dragStart) return; panX += e.clientX - dragStart.x; panY += e.clientY - dragStart.y; dragStart = {x: e.clientX, y: e.clientY}; });
window.addEventListener('touchmove', e => { if(!isDragging||!dragStart) return; const t = e.touches[0]; panX += t.clientX - dragStart.x; panY += t.clientY - dragStart.y; dragStart = {x: t.clientX, y: t.clientY}; }, {passive:false});
canvas.addEventListener('wheel', e => { zoom *= e.deltaY > 0 ? 0.92 : 1.08; zoom = Math.max(0.3, Math.min(3, zoom)); e.preventDefault(); }, {passive:false});

// Organ colors
const COLORS = {
  gateway: '#d4b896', server: '#7eb8da', database: '#8cc9b8',
  endpoint: '#c0c8d4', iot: '#ffa94d', storage: '#b39ddb', unknown: '#6a7a8a'
};

// Build from data
function buildGraph(organs, synapses) {
  nodes = organs.map((o, i) => {
    const phi = Math.acos(2*(i/organs.length)-1);
    const theta = Math.PI*(1+Math.sqrt(5))*i;
    const r = 300 * zoom;
    return {
      ...o,
      x: r*Math.sin(phi)*Math.cos(theta), y: r*Math.sin(phi)*Math.sin(theta),
      color: COLORS[o.type] || COLORS.unknown,
      size: 20 + Math.random()*25,
      phase: Math.random()*Math.PI*2,
      pulse: 0
    };
  });
  edges = synapses.map(s => {
    const a = nodes.find(n => n.ip===s.a), b = nodes.find(n => n.ip===s.b);
    return a && b ? {a, b, weight: s.weight||3, protocol: s.protocol, progress: Math.random()} : null;
  }).filter(Boolean);
}

// Draw
function draw(t) {
  const W = canvas.width, H = canvas.height, cx = W/2+panX, cy = H/2+panY;

  // Background
  ctx.fillStyle = '#060a10'; ctx.fillRect(0,0,W,H);

  // Grid
  ctx.strokeStyle = 'rgba(26,42,58,0.3)';
  for(let i=-400;i<=400;i+=80) {
    const y = cy + i*zoom;
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
    const x = cx + i*zoom;
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
  }

  // Edges (synapses)
  edges.forEach(e => {
    const ax = cx+e.a.x*zoom, ay = cy+e.a.y*zoom;
    const bx = cx+e.b.x*zoom, by = cy+e.b.y*zoom;
    const mx = (ax+bx)/2, my = (ay+by)/2 - 30*zoom;

    // Curve
    ctx.beginPath(); ctx.moveTo(ax, ay);
    ctx.quadraticCurveTo(mx, my, bx, by);
    ctx.strokeStyle = `rgba(126,184,218,${0.08+e.weight*0.02})`;
    ctx.lineWidth = Math.max(0.5, e.weight*0.4);
    ctx.stroke();

    // Pulse
    e.progress += 0.003 + e.weight*0.0008;
    if(e.progress > 1) e.progress = 0;
    const pt = e.progress;
    const px = (1-pt)*(1-pt)*ax + 2*(1-pt)*pt*mx + pt*pt*bx;
    const py = (1-pt)*(1-pt)*ay + 2*(1-pt)*pt*my + pt*pt*by;
    ctx.beginPath(); ctx.arc(px, py, 2.5, 0, Math.PI*2);
    ctx.fillStyle = `rgba(140,201,184,${0.3+Math.sin(pt*Math.PI)*0.7})`;
    ctx.fill();
  });

  // Nodes (organs)
  nodes.forEach(n => {
    const x = cx+n.x*zoom, y = cy+n.y*zoom;
    const breathe = 1+Math.sin(t*0.02+n.phase)*0.06;

    // Halo
    const haloR = n.size*breathe*2.2;
    const haloGrd = ctx.createRadialGradient(x,y,n.size*0.8, x,y,haloR);
    haloGrd.addColorStop(0, n.color+'30');
    haloGrd.addColorStop(1, 'transparent');
    ctx.beginPath(); ctx.arc(x,y,haloR,0,Math.PI*2);
    ctx.fillStyle = haloGrd; ctx.fill();

    // Cell body
    const bodyGrd = ctx.createRadialGradient(x-n.size*0.2, y-n.size*0.2, n.size*0.1, x,y,n.size*breathe);
    bodyGrd.addColorStop(0, n.color+'dd');
    bodyGrd.addColorStop(0.7, n.color+'88');
    bodyGrd.addColorStop(1, n.color+'20');
    ctx.beginPath(); ctx.arc(x,y,n.size*breathe,0,Math.PI*2);
    ctx.fillStyle = bodyGrd; ctx.fill();
    ctx.strokeStyle = n.color+'66';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Ring
    ctx.beginPath(); ctx.arc(x,y,n.size*breathe*1.25,0,Math.PI*2);
    ctx.strokeStyle = n.color+'40';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Nucleus
    ctx.beginPath(); ctx.arc(x,y,n.size*0.35,0,Math.PI*2);
    ctx.fillStyle = '#ffffffdd';
    ctx.fill();

    // Label
    ctx.font = '9px "JetBrains Mono", monospace';
    ctx.fillStyle = '#c0c8d488';
    ctx.fillText(n.ip||n.hostname||'', x-n.size, y-n.size*breathe-8);
  });

  // Auto-rotate (slow drift when not dragging)
  if(!isDragging) panX -= 0.15;
}

// Fetch data
async function fetchData() {
  try {
    const r = await fetch('/api/graph');
    const d = await r.json();
    const organs = d.organs||[], synapses = d.synapses||[];
    const isDemo = d.demo === true;

    if(isDemo || organs.length===0) {
      if(!useDemo||nodes.length!==DEMO_ORGANS.length) { useDemo=true; buildGraph(DEMO_ORGANS, DEMO_SYNAPSES); }
    } else {
      useDemo = false;
      if(nodes.length !== organs.length) buildGraph(organs, synapses);
    }

    const h = await fetch('/api/health'); const hd = await h.json();
    updateUI({
      organs: isDemo?DEMO_ORGANS.length:(hd.organs||organs.length),
      synapses: isDemo?DEMO_SYNAPSES.length:(hd.synapses||synapses.length),
      packets: hd.packets_seen||0, baseline: hd.baseline_ready,
      uptime: hd.uptime_seconds||0, demo: isDemo,
      scan_remaining: hd.scan_remaining, at_limit: hd.at_organ_limit||false
    });
  } catch(e) {
    if(nodes.length===0) { useDemo=true; buildGraph(DEMO_ORGANS, DEMO_SYNAPSES); }
  }
}

function updateUI(d) {
  document.getElementById('stat-organs').textContent = d.organs;
  document.getElementById('stat-synapses').textContent = d.synapses;
  document.getElementById('stat-packets').textContent = d.packets.toLocaleString();
  document.getElementById('stat-baseline').textContent = d.baseline?'Baseline Ready':'Observing...';
  document.getElementById('stat-baseline').style.color = d.baseline?'#8cc9b8':'#d4b896';
  if(d.scan_remaining!==undefined&&d.scan_remaining!==null) {
    const m=Math.floor(d.scan_remaining/60), s=Math.floor(d.scan_remaining%60);
    document.getElementById('stat-time').innerHTML = `${m}m ${s}s`;
    document.getElementById('lock-time').classList.add('visible');
  }
  document.getElementById('lock-organs').classList.toggle('visible', d.at_limit);
  const badge = document.getElementById('mode-badge');
  badge.textContent = d.demo?'DEMO':'LIVE';
  badge.className = d.demo?'mode-badge demo':'mode-badge live';
  document.getElementById('pulse-dot').style.background = d.demo?'#ffa94d':'#8cc9b8';
  document.getElementById('toolbar-status').textContent = d.demo?'DEMO MODE — simulation active':'LIVE — passive scan engaged';
  document.getElementById('alerts').innerHTML = d.demo
    ?'<div class="alert-line info">[INFO] Demo mode — real data replaces simulation after scan starts</div>'
    :'<div class="alert-line info">[INFO] Passive scan active — zero packets emitted</div>';
}

// Resize canvas
function resize() {
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
}
window.addEventListener('resize', resize);
resize();

// Animate
function anim(ts) {
  draw(ts);
  requestAnimationFrame(anim);
}

// Init
function init() {
  buildGraph(DEMO_ORGANS, DEMO_SYNAPSES);
  updateUI({organs:DEMO_ORGANS.length, synapses:DEMO_SYNAPSES.length, packets:0, baseline:false, uptime:0, demo:true, scan_remaining:300});
  document.getElementById('loading').style.display = 'none';
  requestAnimationFrame(anim);
  fetchData();
  setInterval(fetchData, 4000);
}
init();
</script>
</body>
</html>"""

# =============================================================================
# Dashboard module
# =============================================================================


def start_dashboard(host="0.0.0.0", port=8080, is_demo=False):
    """Start the Molecular Cockpit 3D web dashboard."""
    engine = get_engine()
    cyto = CytokineEngine(engine)

    app = Flask(__name__)
    scan_started_at = time.time() if is_demo else None

    # Serve local Three.js static files (no CDN dependency)
    import os as _os
    _static_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "static")

    @app.route("/static/<path:filename>")
    def static_files(filename):
        from flask import send_from_directory
        return send_from_directory(_static_dir, filename)

    @app.route("/")
    def index():
        return COCKPIT_HTML

    @app.route("/api/health")
    def api_health():
        stats = engine.get_stats()
        n_organs = len(engine.organs)
        remaining = None
        if scan_started_at:
            elapsed = time.time() - scan_started_at
            remaining = max(0, DEMO_CONFIG["max_scan_duration"] - elapsed)

        return jsonify({
            "status": "ok",
            "organs": n_organs,
            "synapses": len(engine.synapses),
            "baseline_ready": engine.baseline_ready,
            "uptime_seconds": stats["uptime_seconds"],
            "packets_seen": stats["packets_seen"],
            "scan_remaining": remaining,
            "demo": is_demo,
            "at_organ_limit": is_demo and n_organs >= DEMO_CONFIG["max_organs"],
        })

    @app.route("/api/graph")
    def api_graph():
        data = engine.get_graph()
        organs = data.get("organs", [])
        synapses = data.get("synapses", [])

        # Apply demo caps
        if is_demo:
            organs = organs[:DEMO_CONFIG["max_organs"]]

        # If empty, return demo data so cockpit always shows something
        if not organs and not synapses:
            return jsonify({
                "organs": DEMO_ORGANS,
                "synapses": DEMO_SYNAPSES,
                "demo": is_demo,
            })

        return jsonify({
            "organs": organs,
            "synapses": synapses,
            "demo": is_demo,
        })

    thread = threading.Thread(target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False), daemon=False)
    thread.start()
    return True
