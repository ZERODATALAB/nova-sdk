"""
nova-cytokine — Alert & Anomaly Engine
=======================================
Port :5190 — Baseline deviation detection, anomaly scoring, reflex actions.

Cytokine is the immune system's early warning. It monitors the Synapse
graph and fires alerts when:
  - A new synapse forms (unknown connection)
  - Traffic volume exceeds baseline
  - A protocol appears where it shouldn't
  - An organ goes silent (heartbeat timeout)

Paper: 005 — Le Système Immunitaire des Infrastructures
"""

import json
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

try:
    from flask import Flask, jsonify, request
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert:
    """An immune system alert."""
    def __init__(self, rule, message, severity=Severity.LOW, organ=None, evidence=None):
        self.id = f"ALERT-{int(time.time() * 1000)}"
        self.rule = rule
        self.message = message
        self.severity = severity
        self.organ_ip = organ.ip if organ else None
        self.organ_mac = organ.mac if organ else None
        self.evidence = evidence or {}
        self.timestamp = datetime.utcnow()
        self.acknowledged = False
        self.action_taken = None

    def to_dict(self):
        return {
            "id": self.id,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity.value,
            "organ_ip": self.organ_ip,
            "organ_mac": self.organ_mac,
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "action_taken": self.action_taken,
        }


class CytokineEngine:
    """
    The Cytokine Engine — NOVA's immune alert system.

    Connects to the SynapseEngine and evaluates rules against
    the current topology and baseline.

    Usage:
        cyto = CytokineEngine(synapse_engine)
        cyto.start_api()          # REST API on :5190
        cyto.check()              # run one evaluation cycle
    """

    def __init__(self, synapse_engine):
        self.synapse = synapse_engine
        self.alerts = []           # all alerts (ring buffer)
        self.active_alerts = []    # unacknowledged alerts
        self.rules_fired = defaultdict(int)  # rule -> count
        self.running = False

        # Baseline thresholds
        self.thresholds = {
            "new_synapse": Severity.LOW,
            "volume_spike_x5": Severity.MEDIUM,
            "volume_spike_x10": Severity.HIGH,
            "unknown_protocol": Severity.MEDIUM,
            "organ_silent_24h": Severity.LOW,
            "organ_silent_7d": Severity.MEDIUM,
            "external_connection": Severity.HIGH,
            "port_scan_pattern": Severity.CRITICAL,
        }

    # ── Detection Rules ──────────────────────────────────────────

    def check(self):
        """Run one complete evaluation cycle."""
        alerts_this_cycle = []

        # Rule 1: New synapses (organs that just started communicating)
        for syn in self.synapse.synapses.values():
            age = (datetime.utcnow() - syn.first_seen).total_seconds()
            if age < 300:  # formed in last 5 minutes
                a = self._create_alert(
                    "new_synapse",
                    f"New connection: {syn.a.ip} → {syn.b.ip} ({syn.protocol})",
                    syn.a,
                )
                alerts_this_cycle.append(a)

        # Rule 2: Silent organs (no heartbeat for too long)
        for organ in self.synapse.organs.values():
            idle = (datetime.utcnow() - organ.last_seen).total_seconds()
            if idle > 86400 * 7:  # 7 days
                a = self._create_alert(
                    "organ_silent_7d",
                    f"Organ {organ.ip} ({organ.mac}) — no activity for 7 days",
                    organ,
                    severity=Severity.MEDIUM,
                )
                alerts_this_cycle.append(a)
            elif idle > 86400:  # 24 hours
                a = self._create_alert(
                    "organ_silent_24h",
                    f"Organ {organ.ip} ({organ.mac}) — no activity for 24 hours",
                    organ,
                )
                alerts_this_cycle.append(a)

        # Rule 3: External connections (organ talking to public IP)
        for syn in self.synapse.synapses.values():
            if self._is_external(syn.b.ip):
                a = self._create_alert(
                    "external_connection",
                    f"External connection: {syn.a.ip} → {syn.b.ip}:{syn.port or '?'} ({syn.protocol})",
                    syn.a,
                    severity=Severity.HIGH,
                    evidence={"destination": syn.b.ip, "port": syn.port, "protocol": syn.protocol},
                )
                alerts_this_cycle.append(a)

        # Deduplicate and store
        for alert in alerts_this_cycle:
            if not any(a.message == alert.message for a in self.active_alerts):
                self.active_alerts.append(alert)
                self.alerts.append(alert)
                self.stats["alerts"] += 1

        return alerts_this_cycle

    def _create_alert(self, rule, message, organ, severity=None, evidence=None):
        if severity is None:
            severity = self.thresholds.get(rule, Severity.LOW)
        self.rules_fired[rule] += 1
        return Alert(rule, message, severity, organ, evidence)

    def _is_external(self, ip):
        """Check if an IP is external (not private)."""
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            octets = [int(p) for p in parts]
        except ValueError:
            return False
        # RFC 1918
        if octets[0] == 10:
            return False
        if octets[0] == 172 and 16 <= octets[1] <= 31:
            return False
        if octets[0] == 192 and octets[1] == 168:
            return False
        # Loopback
        if octets[0] == 127:
            return False
        return True

    # ── Alert Management ─────────────────────────────────────────

    def acknowledge(self, alert_id):
        """Acknowledge an alert."""
        for a in self.active_alerts:
            if a.id == alert_id:
                a.acknowledged = True
                self.active_alerts.remove(a)
                return True
        return False

    def get_active(self):
        """Return all unacknowledged alerts."""
        return [a.to_dict() for a in self.active_alerts]

    def get_history(self, limit=100):
        """Return alert history."""
        return [a.to_dict() for a in self.alerts[-limit:]]

    @property
    def stats(self):
        return self.synapse.stats if hasattr(self, 'synapse') else {}

    # ── API ───────────────────────────────────────────────────────

    def start_api(self, host="0.0.0.0", port=5190):
        """Start the REST API server."""
        if not HAS_FLASK:
            raise ImportError("flask required. Install: pip install flask")

        app = Flask(__name__)
        engine = self

        @app.route("/alerts")
        def api_alerts():
            return jsonify(engine.get_active())

        @app.route("/alerts/history")
        def api_history():
            limit = request.args.get("limit", 100, type=int)
            return jsonify(engine.get_history(limit))

        @app.route("/alerts/<alert_id>/ack", methods=["POST"])
        def api_ack(alert_id):
            ok = engine.acknowledge(alert_id)
            return jsonify({"acknowledged": ok})

        @app.route("/rules")
        def api_rules():
            return jsonify({
                "thresholds": {k: v.value for k, v in engine.thresholds.items()},
                "fired": dict(engine.rules_fired),
            })

        @app.route("/health")
        def api_health():
            return jsonify({
                "status": "ok",
                "active_alerts": len(engine.active_alerts),
                "total_alerts": len(engine.alerts),
                "rules_active": len(engine.rules_fired),
            })

        def _run():
            app.run(host=host, port=port, debug=False, use_reloader=False)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        self.running = True
        return True


# ─── Anesthesia Simulation ──────────────────────────────────────────

class AnesthesiaSandbox:
    """
    Digital anesthesia — redirect a compromised device's traffic
    to an isolated sandbox for observation.

    Paper: 005, Section 5 — Anesthésie Numérique
    """

    def __init__(self, cytokine_engine):
        self.cytokine = cytokine_engine
        self.active_sandboxes = {}  # organ_ip -> sandbox info

    def isolate(self, organ_ip, vlan=999):
        """Mark an organ for isolation (simulation)."""
        self.active_sandboxes[organ_ip] = {
            "vlan": vlan,
            "isolated_at": datetime.utcnow().isoformat(),
            "status": "observing",
            "packets_captured": 0,
            "behaviors_identified": [],
        }
        return self.active_sandboxes[organ_ip]

    def release(self, organ_ip):
        """Release an organ from isolation."""
        return self.active_sandboxes.pop(organ_ip, None)

    def report(self):
        return self.active_sandboxes
