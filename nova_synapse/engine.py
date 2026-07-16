"""
nova-synapse — Network Discovery Engine
=========================================
Port :5191 — Passive network discovery, topology graph, baseline.

The Synapse Engine is the nervous system of NOVA. It listens passively
to network traffic (ARP, mDNS, SSDP, LLDP, DHCP) and builds a real-time
topology graph of the infrastructure — without emitting a single packet
during discovery phase.

Architecture:
  - Scanner: passive packet capture (scapy)
  - Graph: network topology (networkx)
  - Baseline: statistical normal behavior (numpy)
  - API: REST interface (Flask, port :5191)

Paper: 003 — Le Système Nerveux des Infrastructures
"""

import json
import time
import threading
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Optional dependencies — graceful degradation
try:
    from scapy.all import sniff, ARP, IP, Ether, UDP, DNS
    HAS_SCAPY = True
except ImportError:
    HAS_SCAPY = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    from flask import Flask, jsonify, request
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


# ─── Data Structures ────────────────────────────────────────────────

class Organ:
    """An organ (device) in the infrastructure."""
    def __init__(self, ip, mac, hostname="", vendor=""):
        self.ip = ip
        self.mac = mac
        self.hostname = hostname
        self.vendor = vendor
        self.first_seen = datetime.utcnow()
        self.last_seen = datetime.utcnow()
        self.services = {}       # port -> service name
        self.protocols = set()   # protocols seen
        self.tags = set()        # auto-discovered tags
        self.dna = self._compute_dna()

    def _compute_dna(self):
        """Unique cryptographic DNA fingerprint."""
        seed = f"{self.mac}|{sorted(self.protocols)}|{sorted(self.services.keys())}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    def heartbeat(self):
        self.last_seen = datetime.utcnow()

    def to_dict(self):
        return {
            "ip": self.ip,
            "mac": self.mac,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "dna": self.dna,
            "services": self.services,
            "protocols": list(self.protocols),
            "tags": list(self.tags),
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "age_seconds": (datetime.utcnow() - self.first_seen).total_seconds(),
        }


class Synapse:
    """A connection between two organs."""
    def __init__(self, organ_a, organ_b, protocol, port=None, volume=0):
        self.a = organ_a
        self.b = organ_b
        self.protocol = protocol
        self.port = port
        self.volume = volume          # bytes seen
        self.weight = 1.0             # reinforcement by usage
        self.first_seen = datetime.utcnow()
        self.last_seen = datetime.utcnow()

    def activate(self, volume=0):
        """Hebbian reinforcement: synapses that fire together, wire together."""
        self.weight = min(10.0, self.weight + 0.01)
        self.volume += volume
        self.last_seen = datetime.utcnow()

    def decay(self):
        """Synaptic pruning: unused synapses weaken."""
        idle = (datetime.utcnow() - self.last_seen).total_seconds()
        if idle > 86400 * 7:  # 7 days idle
            self.weight = max(0.1, self.weight - 0.1)

    def to_dict(self):
        return {
            "a": self.a.ip,
            "b": self.b.ip,
            "protocol": self.protocol,
            "port": self.port,
            "volume_bytes": self.volume,
            "weight": round(self.weight, 4),
            "last_seen": self.last_seen.isoformat(),
        }


# ─── Engine ─────────────────────────────────────────────────────────

class SynapseEngine:
    """
    The Synapse Engine — NOVA's nervous system.

    Usage:
        engine = SynapseEngine()
        engine.start_passive()       # start sniffing
        engine.start_api()           # REST API on :5191
    """

    def __init__(self, data_dir="/opt/nova/synapse"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Core state
        self.organs = {}          # mac -> Organ
        self.synapses = {}        # (a.dna, b.dna) -> Synapse
        self.graph = None         # networkx DiGraph
        self.baseline_period = timedelta(days=7)
        self.baseline_ready = False
        self.running = False
        self.start_time = datetime.utcnow()

        # Statistics
        self.stats = {
            "packets_seen": 0,
            "organs_discovered": 0,
            "synapses_formed": 0,
            "alerts": 0,
            "uptime_seconds": 0,
        }

        # Thread safety
        self._lock = threading.Lock()

    # ── Discovery ────────────────────────────────────────────────

    def discover_organ(self, ip, mac, hostname="", vendor=""):
        """Register or update an organ."""
        with self._lock:
            if mac in self.organs:
                organ = self.organs[mac]
                organ.heartbeat()
                if hostname:
                    organ.hostname = hostname
                if vendor:
                    organ.vendor = vendor
            else:
                organ = Organ(ip, mac, hostname, vendor)
                self.organs[mac] = organ
                self.stats["organs_discovered"] += 1
            return organ

    def form_synapse(self, organ_a, organ_b, protocol, port=None, volume=0):
        """Create or reinforce a synapse between two organs."""
        with self._lock:
            key = tuple(sorted([organ_a.dna, organ_b.dna])) + (protocol, port or 0)
            if key in self.synapses:
                syn = self.synapses[key]
                syn.activate(volume)
            else:
                syn = Synapse(organ_a, organ_b, protocol, port, volume)
                self.synapses[key] = syn
                self.stats["synapses_formed"] += 1
            return syn

    # ── Passive Capture ───────────────────────────────────────────

    def _packet_handler(self, pkt):
        """Process a captured packet (called by scapy sniff)."""
        self.stats["packets_seen"] += 1

        if not pkt.haslayer(IP):
            return

        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        src_mac = pkt[Ether].src if pkt.haslayer(Ether) else "unknown"
        dst_mac = pkt[Ether].dst if pkt.haslayer(Ether) else "unknown"
        proto = pkt[IP].proto

        # Skip broadcast/multicast for organ discovery
        if dst_ip.startswith("224.") or dst_ip.startswith("239."):
            return
        if dst_ip == "255.255.255.255":
            return

        # Discover organs
        if src_mac != "unknown" and src_mac != "00:00:00:00:00:00":
            a = self.discover_organ(src_ip, src_mac)
        else:
            return

        if dst_mac != "unknown" and dst_mac != "00:00:00:00:00:00":
            b = self.discover_organ(dst_ip, dst_mac)
        else:
            return

        # Detect protocol
        proto_name = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(proto, f"IP-{proto}")

        # Check for specific ports
        port = None
        if pkt.haslayer(TCP):
            port = pkt[TCP].dport
        elif pkt.haslayer(UDP):
            port = pkt[UDP].dport

        # Form synapse
        pkt_len = len(pkt)
        self.form_synapse(a, b, proto_name, port, pkt_len)

    def start_passive(self, interface=None, duration=None):
        """
        Start passive network discovery.

        Args:
            interface: Network interface (e.g., 'eth0'). Auto-detect if None.
            duration: Capture duration in seconds. None = indefinite.
        """
        if not HAS_SCAPY:
            raise ImportError("scapy required. Install: pip install scapy")

        self.running = True
        self.start_time = datetime.utcnow()

        def _sniff():
            try:
                sniff(
                    iface=interface,
                    prn=self._packet_handler,
                    store=False,
                    timeout=duration,
                    filter="ip",
                )
            except PermissionError:
                print("[NOVA] ⚠️  Root privileges required for packet capture.")
                print("[NOVA] Run: sudo nova scan")
            except Exception as e:
                print(f"[NOVA] Capture error: {e}")
            finally:
                self.running = False

        self._sniff_thread = threading.Thread(target=_sniff, daemon=True)
        self._sniff_thread.start()

        # Start baseline evaluator
        self._baseline_thread = threading.Thread(target=self._baseline_loop, daemon=True)
        self._baseline_thread.start()

        return True

    def stop(self):
        """Stop the engine."""
        self.running = False

    # ── Baseline ──────────────────────────────────────────────────

    def _baseline_loop(self):
        """Periodically evaluate whether baseline is ready."""
        while self.running:
            time.sleep(60)  # Check every minute
            if not self.baseline_ready:
                elapsed = datetime.utcnow() - self.start_time
                if elapsed >= self.baseline_period:
                    self.baseline_ready = True
                    self._save_state()

    def is_baseline_ready(self):
        """Has the 7-day observation period elapsed?"""
        return self.baseline_ready

    # ── Topology Graph ────────────────────────────────────────────

    def get_graph(self):
        """Return the topology graph as JSON."""
        if not HAS_NETWORKX:
            return {"error": "networkx required. Install: pip install networkx"}

        G = nx.Graph()
        for organ in self.organs.values():
            G.add_node(
                organ.dna,
                ip=organ.ip,
                mac=organ.mac,
                hostname=organ.hostname,
                vendor=organ.vendor,
                services=list(organ.services.keys()),
            )

        for syn in self.synapses.values():
            G.add_edge(
                syn.a.dna, syn.b.dna,
                protocol=syn.protocol,
                port=syn.port,
                weight=syn.weight,
                volume=syn.volume,
            )

        return {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "organs": [o.to_dict() for o in self.organs.values()],
            "synapses": [s.to_dict() for s in self.synapses.values()],
        }

    def get_organ_neighborhood(self, ip_or_mac):
        """Get an organ and its immediate neighbors."""
        organ = None
        for o in self.organs.values():
            if o.ip == ip_or_mac or o.mac == ip_or_mac:
                organ = o
                break

        if not organ:
            return {"error": f"Organ not found: {ip_or_mac}"}

        neighbors = []
        for syn in self.synapses.values():
            if syn.a.dna == organ.dna:
                neighbors.append({"organ": syn.b.to_dict(), "relation": "outbound"})
            elif syn.b.dna == organ.dna:
                neighbors.append({"organ": syn.a.to_dict(), "relation": "inbound"})

        return {
            "organ": organ.to_dict(),
            "neighbors": neighbors,
            "synapse_count": len(neighbors),
        }

    # ── Persistence ───────────────────────────────────────────────

    def _save_state(self):
        """Persist current state to disk."""
        state = {
            "updated": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "organs": [o.to_dict() for o in self.organs.values()],
            "synapses": [s.to_dict() for s in self.synapses.values()],
            "stats": self.stats,
            "baseline_ready": self.baseline_ready,
        }
        state_file = self.data_dir / "state.json"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def get_stats(self):
        """Return engine statistics."""
        self.stats["uptime_seconds"] = (datetime.utcnow() - self.start_time).total_seconds()
        return self.stats

    # ── API ───────────────────────────────────────────────────────

    def start_api(self, host="0.0.0.0", port=5191):
        """Start the REST API server."""
        if not HAS_FLASK:
            raise ImportError("flask required. Install: pip install flask")

        app = Flask(__name__)
        engine = self

        @app.route("/graph")
        def api_graph():
            return jsonify(engine.get_graph())

        @app.route("/node/<identifier>")
        def api_node(identifier):
            return jsonify(engine.get_organ_neighborhood(identifier))

        @app.route("/stats")
        def api_stats():
            return jsonify(engine.get_stats())

        @app.route("/health")
        def api_health():
            return jsonify({
                "status": "ok",
                "organs": len(engine.organs),
                "synapses": len(engine.synapses),
                "baseline_ready": engine.baseline_ready,
                "uptime_seconds": (datetime.utcnow() - engine.start_time).total_seconds(),
            })

        @app.route("/feed")
        def api_feed():
            """Stream of recent synapses (last 60 seconds)."""
            recent = []
            cutoff = datetime.utcnow() - timedelta(seconds=60)
            for syn in engine.synapses.values():
                if syn.last_seen >= cutoff:
                    recent.append(syn.to_dict())
            return jsonify({"recent_count": len(recent), "synapses": recent})

        def _run():
            app.run(host=host, port=port, debug=False, use_reloader=False)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return True


# ─── Singleton ──────────────────────────────────────────────────────

_engine = None

def get_engine():
    """Get or create the global SynapseEngine singleton."""
    global _engine
    if _engine is None:
        _engine = SynapseEngine()
    return _engine
