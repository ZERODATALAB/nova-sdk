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
  #three-container { flex: 1; cursor: grab; }
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
    <div id="three-container"></div>
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
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// State
let nodes3d = [], edgeLines = [];
let useDemo = true;
let scanStartTime = null;
const PARTICLES = 150;

// ─── Three.js setup ──────────────────────────────────────────────
const container = document.getElementById('three-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x060a10);
scene.fog = new THREE.FogExp2(0x060a10, 0.00007);

const camera = new THREE.PerspectiveCamera(50, container.clientWidth/container.clientHeight, 0.5, 200);
camera.position.set(18, 12, 22);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 6;
controls.maxDistance = 70;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.3;
controls.update();

// Lighting
scene.add(new THREE.AmbientLight(0x1a2a3a, 1.8));
const pl1 = new THREE.PointLight(0x7eb8da, 18, 60); pl1.position.set(15, 15, 15); scene.add(pl1);
const pl2 = new THREE.PointLight(0xd4b896, 12, 50); pl2.position.set(-15, -5, -10); scene.add(pl2);

// Subtle grid
const grid = new THREE.PolarGridHelper(18, 32, 24, 128, 0x1a2a3a, 0x1a2a3a);
grid.position.y = -10; scene.add(grid);

// Ambient particles
const pGeo = new THREE.BufferGeometry();
const pPos = new Float32Array(PARTICLES * 3);
for (let i = 0; i < PARTICLES * 3; i += 3) {
  pPos[i] = (Math.random() - 0.5) * 40;
  pPos[i+1] = (Math.random() - 0.5) * 25;
  pPos[i+2] = (Math.random() - 0.5) * 30;
}
pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
const pMat = new THREE.PointsMaterial({ color: 0x7eb8da, size: 0.04, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending });
const particles = new THREE.Points(pGeo, pMat); scene.add(particles);

// Raycaster for hover
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const tooltip = document.getElementById('tooltip');

// ─── Color palette ─────────────────────────────────────────────────
const organColors = {
  gateway:  0xd4b896, server: 0x7eb8da, database: 0x8cc9b8,
  endpoint: 0xc0c8d4, iot: 0xffa94d, storage: 0xb39ddb, unknown: 0x6a7a8a,
};

function orgMat(color) { return new THREE.MeshStandardMaterial({ color, roughness:0.35, metalness:0.1, emissive:color, emissiveIntensity:0.15 }); }
function glowMat(color) { return new THREE.MeshBasicMaterial({ color, transparent:true, opacity:0.07, blending:THREE.AdditiveBlending, depthWrite:false }); }
function synMat() { return new THREE.MeshBasicMaterial({ color:0x7eb8da, transparent:true, opacity:0.16, blending:THREE.AdditiveBlending, depthWrite:false }); }

// ─── Create organ node ──────────────────────────────────────────────
function createOrganNode(organ, index, total) {
  const g = new THREE.Group();
  const color = organColors[organ.type] || organColors.unknown;
  const phi = Math.acos(2 * (index/total) - 1);
  const theta = Math.PI * (1 + Math.sqrt(5)) * index;
  const r = 7 + Math.random() * 4;
  const x = r * Math.sin(phi) * Math.cos(theta);
  const y = r * Math.sin(phi) * Math.sin(theta);
  const z = r * Math.cos(phi);

  const sz = 0.45 + Math.random() * 0.65;

  // Core sphere
  const cell = new THREE.Mesh(new THREE.SphereGeometry(sz, 32, 32), orgMat(color));
  cell.castShadow = cell.receiveShadow = true; g.add(cell);

  // Nucleus
  const nuc = new THREE.Mesh(new THREE.SphereGeometry(sz*0.4, 16, 16),
    new THREE.MeshStandardMaterial({ color:0xffffff, roughness:0.2, emissive:color, emissiveIntensity:0.4 }));
  g.add(nuc);

  // Glow halo
  const halo = new THREE.Mesh(new THREE.SphereGeometry(sz*1.9, 32, 32), glowMat(color)); g.add(halo);

  // Membrane ring
  const ringGeo = new THREE.TorusGeometry(sz*1.15, 0.04, 8, 32);
  const ringMat = new THREE.MeshStandardMaterial({ color, roughness:0.2, emissive:color, emissiveIntensity:0.5 });
  const ring1 = new THREE.Mesh(ringGeo, ringMat); ring1.rotation.x = Math.random()*Math.PI; ring1.rotation.y = Math.random()*Math.PI; g.add(ring1);
  const ring2 = new THREE.Mesh(ringGeo, ringMat.clone()); ring2.rotation.x = Math.random()*Math.PI; ring2.rotation.y = Math.random()*Math.PI;
  ring2.material.emissiveIntensity = 0.3; g.add(ring2);

  g.position.set(x, y, z);
  g.userData = { organ, color, sz, nuc, halo, ring1, ring2, baseY: y, phase: Math.random()*Math.PI*2 };
  scene.add(g);
  return g;
}

// ─── Create synapse edge ────────────────────────────────────────────
function createSynapseEdge(nodeA, nodeB, weight) {
  const g = new THREE.Group();
  const start = nodeA.position.clone(), end = nodeB.position.clone();
  const mid = start.clone().add(end).multiplyScalar(0.5);
  mid.y += start.distanceTo(end) * 0.35 * (Math.random() > 0.5 ? 1 : -1);

  const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
  const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 0.025+weight*0.012, 8, false), synMat());
  g.add(tube);

  const pulse = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8),
    new THREE.MeshBasicMaterial({ color:0x8cc9b8, transparent:true, opacity:0.8, blending:THREE.AdditiveBlending, depthWrite:false }));
  pulse.position.copy(start); g.add(pulse);

  g.userData = { curve, tube, pulse, nodeA, nodeB, start, end, mid, progress: Math.random(), speed: 0.002+weight*0.0007 };
  scene.add(g);
  return g;
}

// ─── Build graph ────────────────────────────────────────────────────
function buildGraph(organsData, synapsesData) {
  nodes3d.forEach(n => scene.remove(n)); edgeLines.forEach(e => scene.remove(e));
  nodes3d = []; edgeLines = [];
  const total = organsData.length || 1;
  organsData.forEach((o, i) => nodes3d.push(createOrganNode(o, i, total)));
  synapsesData.forEach(syn => {
    const a = nodes3d.find(n => n.userData.organ.ip === syn.a);
    const b = nodes3d.find(n => n.userData.organ.ip === syn.b);
    if (a && b) edgeLines.push(createSynapseEdge(a, b, syn.weight||3));
  });
}

// ─── Fetch + UI update ──────────────────────────────────────────────
async function fetchData() {
  try {
    const r = await fetch('/api/graph'); const d = await r.json();
    const organs = d.organs || [], synapses = d.synapses || [];
    const isDemo = d.demo === true;

    if (isDemo || organs.length === 0) {
      if (!useDemo || nodes3d.length !== DEMO_ORGANS.length) {
        useDemo = true; buildGraph(DEMO_ORGANS, DEMO_SYNAPSES);
      }
    } else {
      useDemo = false;
      if (nodes3d.length !== organs.length) buildGraph(organs, synapses);
    }

    const h = await fetch('/api/health'); const hd = await h.json();
    updateUI({
      organs: isDemo ? DEMO_ORGANS.length : (hd.organs || organs.length),
      synapses: isDemo ? DEMO_SYNAPSES.length : (hd.synapses || synapses.length),
      packets: hd.packets_seen || 0,
      baseline: hd.baseline_ready,
      uptime: hd.uptime_seconds || 0,
      demo: isDemo,
      scan_remaining: hd.scan_remaining,
      at_limit: hd.at_organ_limit || false,
    });
  } catch(e) {
    if (nodes3d.length === 0) { useDemo = true; buildGraph(DEMO_ORGANS, DEMO_SYNAPSES); }
  }
}

function updateUI(d) {
  document.getElementById('stat-organs').textContent = d.organs;
  document.getElementById('stat-synapses').textContent = d.synapses;
  document.getElementById('stat-packets').textContent = d.packets.toLocaleString();
  document.getElementById('stat-baseline').textContent = d.baseline ? 'Baseline Ready' : 'Observing...';
  document.getElementById('stat-baseline').style.color = d.baseline ? '#8cc9b8' : '#d4b896';

  // Scan time
  if (d.scan_remaining !== undefined && d.scan_remaining !== null) {
    const mins = Math.floor(d.scan_remaining/60), secs = Math.floor(d.scan_remaining%60);
    document.getElementById('stat-time').innerHTML = `${mins}m ${secs}s`;
    document.getElementById('lock-time').classList.toggle('visible', true);
  } else if (d.demo) {
    document.getElementById('stat-time').textContent = '--';
    document.getElementById('lock-time').classList.toggle('visible', true);
  }

  // Organ limit warning
  document.getElementById('lock-organs').classList.toggle('visible', d.at_limit);

  // Mode
  const badge = document.getElementById('mode-badge');
  badge.textContent = d.demo ? 'DEMO' : 'LIVE';
  badge.className = d.demo ? 'mode-badge demo' : 'mode-badge live';
  document.getElementById('pulse-dot').style.background = d.demo ? '#ffa94d' : '#8cc9b8';
  document.getElementById('toolbar-status').textContent = d.demo ? 'DEMO MODE — simulation active' : 'LIVE — passive scan engaged';

  document.getElementById('alerts').innerHTML = d.demo
    ? '<div class="alert-line info">[INFO] Demo mode — real data replaces simulation after scan starts</div>'
    : '<div class="alert-line info">[INFO] Passive scan active — zero packets emitted</div>';
}

// ─── Render loop ────────────────────────────────────────────────────
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  controls.update();

  nodes3d.forEach(n => {
    const u = n.userData;
    u.halo.scale.setScalar(1 + Math.sin(t*1.5+u.phase)*0.04);
    u.ring1.rotation.z += 0.003; u.ring2.rotation.x += 0.004;
    u.nuc.material.emissiveIntensity = 0.3 + Math.sin(t*3+u.phase)*0.2;
    n.position.y = u.baseY + Math.sin(t*0.8+u.phase)*0.15;
  });

  edgeLines.forEach(e => {
    const u = e.userData;
    u.progress += u.speed; if (u.progress > 1) u.progress = 0;
    const pt = u.curve.getPoint(u.progress);
    u.pulse.position.copy(pt);
    u.pulse.material.opacity = 0.25 + Math.sin(u.progress*Math.PI)*0.75;
  });

  particles.rotation.y += 0.0002; particles.rotation.x += 0.0001;
  renderer.render(scene, camera);
}

// ─── Hover ──────────────────────────────────────────────────────────
container.addEventListener('mousemove', (e) => {
  const rect = container.getBoundingClientRect();
  mouse.x = ((e.clientX-rect.left)/rect.width)*2-1;
  mouse.y = -((e.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(nodes3d.flatMap(n=>n.children), true);
  if (hits.length > 0) {
    let obj = hits[0].object;
    while (obj && !obj.userData?.organ) obj = obj.parent;
    if (obj?.userData?.organ) {
      const o = obj.userData.organ;
      tooltip.innerHTML = `<div class="tt-ip">${o.ip}</div><div class="tt-host">${o.hostname||'(unnamed)'}</div><div class="tt-dna">DNA: ${o.dna}</div>`;
      tooltip.style.display = 'block';
      tooltip.style.left = (e.clientX-container.getBoundingClientRect().left+16)+'px';
      tooltip.style.top = (e.clientY-container.getBoundingClientRect().top-50)+'px';
      container.style.cursor = 'pointer';
    }
  } else { tooltip.style.display = 'none'; container.style.cursor = 'grab'; }
});

window.addEventListener('resize', () => {
  camera.aspect = container.clientWidth/container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
});

// ─── Init ───────────────────────────────────────────────────────────
function init() {
  buildGraph(DEMO_ORGANS, DEMO_SYNAPSES);
  updateUI({ organs: DEMO_ORGANS.length, synapses: DEMO_SYNAPSES.length, packets: 0, baseline: false, uptime: 0, demo: true, scan_remaining: 300 });
  document.getElementById('loading').style.display = 'none';
  animate();
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
