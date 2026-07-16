"""
nova-cockpit — Molecular Cockpit Dashboard
============================================
Web dashboard showing the infrastructure as a living organism.
Real-time topology visualization, organ vitals, synapse activity.

Paper: 003, Section 3.3 — Le Cockpit Moléculaire
"""

from flask import Flask, render_template_string, jsonify, request
from nova_synapse.engine import get_engine
from nova_cytokine.engine import CytokineEngine
from nova_spina.chain import get_chain


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NOVA — Molecular Cockpit</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',-apple-system,sans-serif;background:#060a10;color:#c0c8d4;overflow:hidden}
#app{display:flex;height:100vh}
.sidebar{width:280px;background:rgba(12,20,28,.95);border-right:1px solid rgba(255,255,255,.04);padding:20px;overflow-y:auto}
.sidebar h1{font-size:1.1rem;font-weight:700;margin-bottom:4px;background:linear-gradient(135deg,#d4b896,#7eb8da);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sidebar .sub{font-size:.65rem;color:#6a7a8a;margin-bottom:20px;font-family:'Share Tech Mono',monospace}
.stat{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.03);border-radius:10px;padding:12px;margin-bottom:8px}
.stat .label{font-size:.52rem;color:#7eb8da;text-transform:uppercase;letter-spacing:1px;font-family:'Share Tech Mono',monospace}
.stat .value{font-size:1.4rem;font-weight:700;color:#e0e4ec;margin-top:2px}
.stat .unit{font-size:.6rem;color:#6a7a8a}
.main{flex:1;display:flex;flex-direction:column}
.toolbar{background:rgba(12,20,28,.8);border-bottom:1px solid rgba(255,255,255,.04);padding:10px 20px;display:flex;gap:12px;align-items:center}
.toolbar .dot{width:8px;height:8px;border-radius:50%;background:#8cc9b8;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
canvas{flex:1;cursor:grab}
.alerts{border-top:1px solid rgba(255,255,255,.04);padding:10px 20px;max-height:150px;overflow-y:auto;background:rgba(12,20,28,.9)}
.alert{padding:4px 0;font-size:.7rem;font-family:'Share Tech Mono',monospace;border-bottom:1px solid rgba(255,255,255,.02)}
.alert.critical{color:#ff6b6b}
.alert.high{color:#ffa94d}
.alert.medium{color:#ffd43b}
.alert.low{color:#7eb8da}
</style>
</head>
<body>
<div id="app">
  <div class="sidebar">
    <h1>NOVA</h1>
    <div class="sub">Molecular Cockpit · Port 5191</div>
    <div class="stat"><div class="label">Organs</div><div class="value" id="organs">--</div></div>
    <div class="stat"><div class="label">Synapses</div><div class="value" id="synapses">--</div></div>
    <div class="stat"><div class="label">Baseline</div><div class="value" id="baseline" style="font-size:.9rem">--</div></div>
    <div class="stat"><div class="label">Uptime</div><div class="value" id="uptime">--<span class="unit">s</span></div></div>
    <div class="stat"><div class="label">SPINA Chain</div><div class="value" id="spina" style="font-size:.9rem">--</div></div>
  </div>
  <div class="main">
    <div class="toolbar">
      <div class="dot"></div>
      <span style="font-size:.7rem;color:#6a7a8a;font-family:'Share Tech Mono',monospace">LIVE · Passive Mode</span>
    </div>
    <canvas id="canvas"></canvas>
    <div class="alerts" id="alerts"></div>
  </div>
</div>
<script>
let organs=[],synapses=[];
const canvas=document.getElementById('canvas');
const ctx=canvas.getContext('2d');
let nodes=[];

function resize(){canvas.width=canvas.parentElement.clientWidth;canvas.height=canvas.parentElement.clientHeight-70}
window.addEventListener('resize',resize);
resize();

async function fetchData(){
  try{
    const r=await fetch('/api/health');
    const d=await r.json();
    document.getElementById('organs').textContent=d.organs;
    document.getElementById('synapses').textContent=d.synapses;
    document.getElementById('baseline').textContent=d.baseline_ready?'[OK] Ready':'⏳ Observing...';
    document.getElementById('baseline').style.color=d.baseline_ready?'#8cc9b8':'#d4b896';
    document.getElementById('uptime').innerHTML=Math.floor(d.uptime_seconds)+'<span class="unit">s</span>';
  }catch(e){}

  try{
    const r=await fetch('http://localhost:5194/health');
    const d=await r.json();
    document.getElementById('spina').textContent=d.chain_length+' blocks';
  }catch(e){document.getElementById('spina').textContent='--';}

  try{
    const r=await fetch('/api/graph');
    const d=await r.json();
    organs=d.organs||[];
    synapses=d.synapses||[];
    updateGraph();
  }catch(e){}

  try{
    const r=await fetch('http://localhost:5190/alerts');
    const alerts=await r.json();
    const div=document.getElementById('alerts');
    div.innerHTML=alerts.slice(0,5).map(a=>
      `<div class="alert ${a.severity}">[${a.severity.toUpperCase()}] ${a.message} — ${a.timestamp.slice(11,19)}</div>`
    ).join('')||'<div class="alert" style="color:#3a4a5a">No active alerts</div>';
  }catch(e){}
}

function updateGraph(){
  nodes=organs.map((o,i)=>({...o,x:100+Math.random()*(canvas.width-200),y:100+Math.random()*(canvas.height-200),vx:0,vy:0}));
}

function draw(){
  ctx.fillStyle='#060a10';ctx.fillRect(0,0,canvas.width,canvas.height);
  // Synapses
  synapses.forEach(s=>{
    const a=nodes.find(n=>n.ip===s.a);
    const b=nodes.find(n=>n.ip===s.b);
    if(!a||!b)return;
    ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
    ctx.strokeStyle=`rgba(126,184,218,${Math.min(s.weight/10,.3)})`;ctx.lineWidth=Math.max(.5,s.weight*.5);
    ctx.stroke();
  });
  // Organs
  nodes.forEach(n=>{
    ctx.beginPath();ctx.arc(n.x,n.y,6+Math.random()*3,0,Math.PI*2);
    ctx.fillStyle='rgba(212,184,150,.6)';ctx.fill();
    ctx.fillStyle='rgba(192,200,212,.4)';ctx.font='9px mono';ctx.fillText(n.ip||n.mac,n.x-20,n.y-12);
  });
}

function animate(){draw();requestAnimationFrame(animate)}
setInterval(fetchData,3000);
fetchData();
animate();
</script>
</body>
</html>"""


def start_dashboard(host="0.0.0.0", port=8080):
    """Start the Molecular Cockpit web dashboard."""
    engine = get_engine()
    cyto = CytokineEngine(engine)

    app = Flask(__name__)

    @app.route("/")
    def index():
        return DASHBOARD_HTML

    @app.route("/api/health")
    def api_health():
        stats = engine.get_stats()
        return jsonify({
            "status": "ok",
            "organs": len(engine.organs),
            "synapses": len(engine.synapses),
            "baseline_ready": engine.baseline_ready,
            "uptime_seconds": stats["uptime_seconds"],
            "packets_seen": stats["packets_seen"],
        })

    @app.route("/api/graph")
    def api_graph():
        return jsonify(engine.get_graph())

    import threading
    def _run():
        app.run(host=host, port=port, debug=False, use_reloader=False)

    thread = threading.Thread(target=_run, daemon=False)
    thread.start()
    return True
