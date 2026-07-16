# NOVA SDK — REST API Reference

Complete reference for every REST endpoint exposed by the NOVA engines. All APIs are JSON-based, served by Flask, and run on their respective ports.

---

## Table of Contents

- [Quick Reference](#quick-reference)
- [Synapse API (:5191)](#synapse-api-5191)
  - [GET /health](#get-health)
  - [GET /graph](#get-graph)
  - [GET /node/:identifier](#get-nodeidentifier)
  - [GET /stats](#get-stats)
  - [GET /feed](#get-feed)
- [Cytokine API (:5190)](#cytokine-api-5190)
  - [GET /health](#get-health-1)
  - [GET /alerts](#get-alerts)
  - [GET /alerts/history](#get-alertshistory)
  - [POST /alerts/:id/ack](#post-alertsidack)
  - [GET /rules](#get-rules)
- [SPINA API (:5194)](#spina-api-5194)
  - [GET /health](#get-health-2)
  - [GET /info](#get-info)
  - [GET /blocks](#get-blocks)
  - [GET /blocks/:hash](#get-blockshash)
  - [POST /blocks](#post-blocks)
  - [GET /search](#get-search)
  - [GET /verify/:hash](#get-verifyhash)
  - [GET /merkle](#get-merkle)
- [Cockpit API (:8080)](#cockpit-api-8080)
- [Error Handling](#error-handling)

---

## Quick Reference

| Engine | Port | Base URL | Purpose |
|---|---|---|---|
| Synapse | :5191 | `http://localhost:5191` | Network topology, discovery, baseline |
| Cytokine | :5190 | `http://localhost:5190` | Alerts, detection rules |
| SPINA | :5194 | `http://localhost:5194` | Blockchain memory, Merkle proofs |
| Cockpit | :8080 | `http://localhost:8080` | Web dashboard (HTML + JSON) |

---

## Synapse API (:5191)

The Synapse Engine API exposes the nervous system — topology graph, organ discovery state, baseline readiness, and real-time synapse activity. All endpoints are read-only.

### GET /health

Health check and summary counts.

**Request:**
```bash
curl http://localhost:5191/health
```

**Response (200):**
```json
{
  "status": "ok",
  "organs": 14,
  "synapses": 47,
  "baseline_ready": false,
  "uptime_seconds": 342.15
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | Always `"ok"` when the engine is running |
| `organs` | int | Number of discovered organs (devices) |
| `synapses` | int | Number of formed synapses (connections) |
| `baseline_ready` | bool | Whether the 7-day baseline period has elapsed |
| `uptime_seconds` | float | Seconds since engine started |

---

### GET /graph

Full topology — all organs and their synapses.

**Request:**
```bash
curl http://localhost:5191/graph
```

**Response (200):**
```json
{
  "nodes": 14,
  "edges": 47,
  "organs": [
    {
      "ip": "10.0.1.5",
      "mac": "aa:bb:cc:dd:ee:ff",
      "hostname": "db-primary",
      "vendor": "",
      "dna": "a1b2c3d4e5f6a7b8",
      "services": {"5432": "postgresql"},
      "protocols": ["TCP", "UDP"],
      "tags": [],
      "first_seen": "2026-07-09T12:00:00.123456",
      "last_seen": "2026-07-16T14:30:05.654321",
      "age_seconds": 604800.0
    }
  ],
  "synapses": [
    {
      "a": "10.0.1.5",
      "b": "10.0.1.10",
      "protocol": "TCP",
      "port": 5432,
      "volume_bytes": 1048576,
      "weight": 2.3456,
      "last_seen": "2026-07-16T14:30:05.654321"
    }
  ]
}
```

**Organ fields:**

| Field | Type | Description |
|---|---|---|
| `ip` | string | IPv4 address |
| `mac` | string | MAC address (BSSID format) |
| `hostname` | string | Discovered hostname (or empty) |
| `vendor` | string | OUI vendor (or empty) |
| `dna` | string | SHA256 fingerprint (16 hex chars) — unique per organ |
| `services` | object | `{port: "service_name"}` mapping |
| `protocols` | [string] | Protocols seen on this organ |
| `tags` | [string] | Auto-discovered tags |
| `first_seen` | string | ISO 8601 timestamp of discovery |
| `last_seen` | string | ISO 8601 timestamp of last heartbeat |
| `age_seconds` | float | Seconds since first_seen |

**Synapse fields:**

| Field | Type | Description |
|---|---|---|
| `a` | string | Source organ IP |
| `b` | string | Destination organ IP |
| `protocol` | string | TCP, UDP, ICMP, etc. |
| `port` | int\|null | Destination port (if TCP/UDP) |
| `volume_bytes` | int | Total bytes transferred |
| `weight` | float | Synapse strength (1.0–10.0, Hebbian) |
| `last_seen` | string | ISO 8601 timestamp of last activation |

---

### GET /node/:identifier

Get a specific organ and its immediate neighborhood.

**Request:**
```bash
# By IP
curl http://localhost:5191/node/10.0.1.5

# By MAC
curl http://localhost:5191/node/aa:bb:cc:dd:ee:ff
```

**Response (200):**
```json
{
  "organ": {
    "ip": "10.0.1.5",
    "mac": "aa:bb:cc:dd:ee:ff",
    "hostname": "db-primary",
    "dna": "a1b2c3d4e5f6a7b8",
    "services": {"5432": "postgresql"},
    "protocols": ["TCP"],
    "tags": [],
    "first_seen": "2026-07-09T12:00:00",
    "last_seen": "2026-07-16T14:30:05",
    "age_seconds": 604800.0
  },
  "neighbors": [
    {
      "organ": { /* Organ object */ },
      "relation": "outbound"
    },
    {
      "organ": { /* Organ object */ },
      "relation": "inbound"
    }
  ],
  "synapse_count": 5
}
```

**Response (404, organ not found):**
```json
{
  "error": "Organ not found: 10.0.99.99"
}
```

---

### GET /stats

Engine statistics since startup.

**Request:**
```bash
curl http://localhost:5191/stats
```

**Response (200):**
```json
{
  "packets_seen": 45231,
  "organs_discovered": 14,
  "synapses_formed": 47,
  "alerts": 0,
  "uptime_seconds": 342.15
}
```

| Field | Type | Description |
|---|---|---|
| `packets_seen` | int | Total IP packets processed |
| `organs_discovered` | int | Cumulative organs found (since start) |
| `synapses_formed` | int | Cumulative synapses formed (since start) |
| `alerts` | int | Alerts generated (mirrors Cytokine) |
| `uptime_seconds` | float | Seconds since engine.start_passive() |

---

### GET /feed

Recent synapse activity — last 60 seconds only. Useful for real-time dashboards and streaming.

**Request:**
```bash
curl http://localhost:5191/feed
```

**Response (200):**
```json
{
  "recent_count": 3,
  "synapses": [
    {
      "a": "10.0.1.5",
      "b": "10.0.1.10",
      "protocol": "TCP",
      "port": 5432,
      "volume_bytes": 4096,
      "weight": 1.02,
      "last_seen": "2026-07-16T14:30:05.654321"
    }
  ]
}
```

An empty feed indicates no traffic in the last 60 seconds:
```json
{
  "recent_count": 0,
  "synapses": []
}
```

---

## Cytokine API (:5190)

The Cytokine Engine API exposes the immune system — active alerts, detection rules, and alert management.

### GET /health

Immune system health.

**Request:**
```bash
curl http://localhost:5190/health
```

**Response (200):**
```json
{
  "status": "ok",
  "active_alerts": 2,
  "total_alerts": 15,
  "rules_active": 3
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | Always `"ok"` when running |
| `active_alerts` | int | Unacknowledged alerts |
| `total_alerts` | int | All alerts ever generated (ring buffer) |
| `rules_active` | int | Number of distinct rules that have fired |

---

### GET /alerts

All unacknowledged (active) alerts.

**Request:**
```bash
curl http://localhost:5190/alerts
```

**Response (200):**
```json
[
  {
    "id": "ALERT-1752671405123",
    "rule": "external_connection",
    "message": "External connection: 10.0.1.5 → 142.250.185.78:443 (TCP)",
    "severity": "high",
    "organ_ip": "10.0.1.5",
    "organ_mac": "aa:bb:cc:dd:ee:ff",
    "evidence": {
      "destination": "142.250.185.78",
      "port": 443,
      "protocol": "TCP"
    },
    "timestamp": "2026-07-16T14:30:05.123456",
    "acknowledged": false,
    "action_taken": null
  }
]
```

**Alert fields:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique alert ID (ALERT-{epoch_ms}) |
| `rule` | string | Detection rule that fired |
| `message` | string | Human-readable description |
| `severity` | string | One of: info, low, medium, high, critical |
| `organ_ip` | string\|null | IP of relevant organ |
| `organ_mac` | string\|null | MAC of relevant organ |
| `evidence` | object | Rule-specific evidence data |
| `timestamp` | string | ISO 8601 when alert was generated |
| `acknowledged` | bool | Whether alert has been acknowledged |
| `action_taken` | string\|null | Action taken in response |

**Empty state:**
```json
[]
```

---

### GET /alerts/history

Full alert history with optional pagination.

**Request:**
```bash
# Default: last 100 alerts
curl http://localhost:5190/alerts/history

# Custom limit
curl "http://localhost:5190/alerts/history?limit=50"
```

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 100 | Max alerts to return |

**Response (200):**
```json
[
  {
    "id": "ALERT-1752671405123",
    "rule": "external_connection",
    "message": "External connection: 10.0.1.5 → 142.250.185.78:443 (TCP)",
    "severity": "high",
    "organ_ip": "10.0.1.5",
    "organ_mac": "aa:bb:cc:dd:ee:ff",
    "evidence": {
      "destination": "142.250.185.78",
      "port": 443,
      "protocol": "TCP"
    },
    "timestamp": "2026-07-16T14:30:05.123456",
    "acknowledged": true,
    "action_taken": null
  }
]
```

---

### POST /alerts/:id/ack

Acknowledge an alert, removing it from the active list.

**Request:**
```bash
curl -X POST http://localhost:5190/alerts/ALERT-1752671405123/ack
```

**Response (200, success):**
```json
{
  "acknowledged": true
}
```

**Response (200, alert not found or already acknowledged):**
```json
{
  "acknowledged": false
}
```

---

### GET /rules

Detection rule configuration and firing statistics.

**Request:**
```bash
curl http://localhost:5190/rules
```

**Response (200):**
```json
{
  "thresholds": {
    "new_synapse": "low",
    "volume_spike_x5": "medium",
    "volume_spike_x10": "high",
    "unknown_protocol": "medium",
    "organ_silent_24h": "low",
    "organ_silent_7d": "medium",
    "external_connection": "high",
    "port_scan_pattern": "critical"
  },
  "fired": {
    "new_synapse": 12,
    "external_connection": 3
  }
}
```

| Field | Type | Description |
|---|---|---|
| `thresholds` | object | Rule name → default severity mapping |
| `fired` | object | Rule name → count of times fired |

---

## SPINA API (:5194)

The SPINA API exposes the cryptographic spine — the append-only blockchain of threat memory. This is the only API that accepts writes (POST /blocks).

### GET /health

Chain health check.

**Request:**
```bash
curl http://localhost:5194/health
```

**Response (200):**
```json
{
  "status": "ok",
  "chain_length": 7,
  "merkle_root": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b"
}
```

---

### GET /info

Full chain summary.

**Request:**
```bash
curl http://localhost:5194/info
```

**Response (200):**
```json
{
  "length": 7,
  "genesis": "0000000000000000000000000000000000000000000000000000000000000000",
  "last_block": {
    "hash": "a1b2c3d4e5f6a7b8...",
    "prev_hash": "b2c3d4e5f6a7b8c9...",
    "timestamp": "2026-07-16T14:30:05.123456",
    "payload": {
      "type": "threat_signature",
      "hash": "abc123def",
      "malware": "ransomware_x",
      "behaviors": ["c2_contact", "lateral_scan", "encryption"]
    },
    "payload_hash": "d4e5f6a7b8c9d0e1...",
    "validator": null,
    "signature": "e5f6a7b8c9d0e1f2..."
  },
  "merkle_root": "1a2b3c4d...",
  "merkle_size": 7,
  "consensus": "PoA",
  "validator_id": null
}
```

| Field | Type | Description |
|---|---|---|
| `length` | int | Number of blocks in the chain |
| `genesis` | string | Genesis block hash (64 zeros) |
| `last_block` | object | Most recent block (or null if empty) |
| `merkle_root` | string | Current Merkle tree root (64 hex) |
| `merkle_size` | int | Number of leaves in Merkle tree (= length) |
| `consensus` | string | Current consensus: `"PoA"` (bootstrap) → `"PoS"` (future) |
| `validator_id` | string\|null | This node's validator identity |

---

### GET /blocks

Paginated block listing.

**Request:**
```bash
# Default: first 100 blocks
curl http://localhost:5194/blocks

# Paginated
curl "http://localhost:5194/blocks?limit=10&offset=20"
```

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 100 | Max blocks to return |
| `offset` | int | 0 | Number of blocks to skip |

**Response (200):**
```json
{
  "total": 7,
  "offset": 0,
  "limit": 100,
  "blocks": [
    {
      "hash": "a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8",
      "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
      "timestamp": "2026-07-16T14:30:05.123456",
      "payload": {
        "type": "threat_signature",
        "hash": "abc123def",
        "malware": "ransomware_x",
        "behaviors": ["c2_contact", "lateral_scan"]
      },
      "payload_hash": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
      "validator": null,
      "signature": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"
    }
  ]
}
```

---

### GET /blocks/:hash

Retrieve a single block by its hash.

**Request:**
```bash
curl http://localhost:5194/blocks/a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8
```

**Response (200):**
```json
{
  "hash": "a1b2c3d4...",
  "prev_hash": "0000000000...",
  "timestamp": "2026-07-16T14:30:05.123456",
  "payload": {
    "type": "threat_signature",
    "hash": "abc123def",
    "malware": "ransomware_x"
  },
  "payload_hash": "d4e5f6a7...",
  "validator": null,
  "signature": "e5f6a7b8..."
}
```

**Response (404):**
```json
{
  "error": "Block not found"
}
```

---

### POST /blocks

Add a new block to the SPINA chain. **This is the only write endpoint in the entire NOVA API.**

**Request:**
```bash
curl -X POST http://localhost:5194/blocks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "threat_signature",
    "hash": "abc123def456",
    "malware": "ransomware_x",
    "behaviors": ["c2_contact", "lateral_scan", "encryption"],
    "severity": "critical"
  }'
```

**Payload conventions:**

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | Recommended | Block type: `threat_signature`, `anesthesia_report`, `certification`, etc. |
| Any other fields | any | No | Arbitrary payload data — stored as-is |

**Response (201 Created):**
```json
{
  "hash": "f1e2d3c4b5a69788796a5b4c3d2e1f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
  "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "timestamp": "2026-07-16T14:30:05.123456",
  "payload": {
    "type": "threat_signature",
    "hash": "abc123def456",
    "malware": "ransomware_x",
    "behaviors": ["c2_contact", "lateral_scan", "encryption"],
    "severity": "critical"
  },
  "payload_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
  "validator": null,
  "signature": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"
}
```

**Common payload types:**

| Type | Description | Example fields |
|---|---|---|
| `threat_signature` | Malware or attack signature | `hash`, `malware`, `behaviors`, `severity` |
| `anesthesia_report` | Digital anesthesia outcome | `organ`, `vlan`, `behaviors_identified` |
| `certification` | Infrastructure certification | `certificate_hash`, `issuer`, `valid_until` |
| `node_registration` | Validator node registration | `public_key`, `node_id`, `stake` |

---

### GET /search

Search blocks by payload content (case-insensitive substring match).

**Request:**
```bash
# Search for ransomware blocks
curl "http://localhost:5194/search?q=ransomware"

# Search by behavior
curl "http://localhost:5194/search?q=c2_contact"
```

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `q` | string | (required) | Search query — matches against JSON-serialized payloads |

**Response (200):**
```json
{
  "query": "ransomware",
  "results": [
    {
      "hash": "a1b2c3d4...",
      "prev_hash": "00000000...",
      "timestamp": "2026-07-16T14:30:05.123456",
      "payload": {
        "type": "threat_signature",
        "malware": "ransomware_x"
      },
      "payload_hash": "d4e5f6a7...",
      "validator": null,
      "signature": "e5f6a7b8..."
    }
  ]
}
```

---

### GET /verify/:hash

Verify a block's integrity using a Merkle proof. Returns O(log n) verification — does not scan the entire chain.

**Request:**
```bash
curl http://localhost:5194/verify/a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8
```

**Response (200):**
```json
{
  "block_hash": "a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8",
  "verified": true
}
```

A `"verified": false` response means either:
- The block hash doesn't exist in the chain
- Tampering has been detected (Merkle proof mismatch)

---

### GET /merkle

Merkle tree state — root, leaves, and tree structure.

**Request:**
```bash
curl http://localhost:5194/merkle
```

**Response (200):**
```json
{
  "size": 7,
  "root": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
  "leaves": [
    "a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8",
    "b2c3d4e5f6a7b8c9b2c3d4e5f6a7b8c9b2c3d4e5f6a7b8c9b2c3d4e5f6a7b8c9"
  ]
}
```

---

## Cockpit API (:8080)

The Cockpit is primarily an HTML dashboard, but it also exposes JSON endpoints for its own polling.

### GET /

The Molecular Cockpit dashboard (HTML page).

**Request:**
```bash
curl http://localhost:8080/
# Or open in browser:
# http://localhost:8080
```

Returns an HTML5 page with a canvas-based topology visualization.

---

### GET /api/health

Aggregated health from the Synapse engine.

**Request:**
```bash
curl http://localhost:8080/api/health
```

**Response (200):**
```json
{
  "status": "ok",
  "organs": 14,
  "synapses": 47,
  "baseline_ready": false,
  "uptime_seconds": 342.15,
  "packets_seen": 45231
}
```

---

### GET /api/graph

Full topology (proxied from Synapse :5191).

**Request:**
```bash
curl http://localhost:8080/api/graph
```

**Response (200):** Same as [Synapse GET /graph](#get-graph).

---

## Error Handling

All NOVA APIs follow consistent error conventions:

**404 Not Found:**
```json
{
  "error": "Organ not found: 10.0.99.99"
}
```
```json
{
  "error": "Block not found"
}
```

**Import errors (engine not fully installed):**
```json
{
  "error": "networkx required. Install: pip install networkx"
}
```

**HTTP status codes used:**

| Code | Meaning |
|---|---|
| 200 | Success (GET, POST ack) |
| 201 | Created (POST /blocks) |
| 404 | Resource not found |
| 500 | Internal error (unhandled exception) |

**Note:** The APIs do not currently implement authentication or rate limiting. In production deployments, place them behind a reverse proxy (nginx, Caddy) with appropriate access controls.

---

## Cross-Engine Workflow Example

A complete workflow using all four APIs:

```bash
# 1. Start all services (in separate terminals or background)
python -c "from nova_synapse import get_engine; e=get_engine(); e.start_passive(duration=60); e.start_api()"
python -c "from nova_synapse import get_engine; from nova_cytokine import CytokineEngine; c=CytokineEngine(get_engine()); c.start_api()"
python -c "from nova_spina import get_chain, SpinaAPI; SpinaAPI(get_chain()).start()"
python -c "from nova_cockpit import start_dashboard; start_dashboard()"

# 2. Check if all services are up
curl -s http://localhost:5191/health | jq .
curl -s http://localhost:5190/health | jq .
curl -s http://localhost:5194/health | jq .
curl -s http://localhost:8080/api/health | jq .

# 3. View topology
curl -s http://localhost:5191/graph | jq '.organs[] | {ip, hostname, dna}'

# 4. Run immune check
# (Cytokine reads from Synapse — must be done programmatically or via CLI)
nova alerts

# 5. Check active alerts
curl -s http://localhost:5190/alerts | jq .

# 6. Add a threat to SPINA memory
curl -s -X POST http://localhost:5194/blocks \
  -H "Content-Type: application/json" \
  -d '{"type":"threat_signature","hash":"abc123","malware":"trojan_y","behaviors":["c2","keylogger"]}' | jq .

# 7. Verify the block was stored
curl -s http://localhost:5194/info | jq '{length, merkle_root, last_block: .last_block.payload}'

# 8. Search for the threat
curl -s "http://localhost:5194/search?q=trojan_y" | jq .

# 9. Verify block integrity
BLOCK_HASH=$(curl -s http://localhost:5194/info | jq -r .last_block.hash)
curl -s "http://localhost:5194/verify/$BLOCK_HASH" | jq .

# 10. View everything in the Cockpit
# Open http://localhost:8080 in a browser
```

---

> *See [ARCHITECTURE.md](ARCHITECTURE.md) for the system design, [PAPER_MAP.md](PAPER_MAP.md) for the research paper mapping, and the [examples/](../examples/) directory for runnable demo scripts.*
