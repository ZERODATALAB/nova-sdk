# NOVA SDK — Architecture Overview

> *"The void is an invitation. Presence is immunity."* — NOVA, Paper 005

NOVA is the first digital organism — a symbiote that grafts onto existing infrastructure without replacing it. It observes, learns, detects anomalies, and remembers threats immutably. This document describes the internal architecture, data flow, and design principles of the NOVA SDK.

---

## Table of Contents

- [Biological Metaphor](#biological-metaphor)
- [Four-Engine Architecture](#four-engine-architecture)
- [Data Flow](#data-flow)
- [Port Map & Service Layout](#port-map--service-layout)
- [Component Deep Dives](#component-deep-dives)
  - [Synapse Engine (:5191)](#synapse-engine-5191)
  - [Cytokine Engine (:5190)](#cytokine-engine-5190)
  - [SPINA Chain (:5194)](#spina-chain-5194)
  - [Molecular Cockpit (:8080)](#molecular-cockpit-8080)
- [Persistence Model](#persistence-model)
- [Threading Model](#threading-model)
- [Dependency Graph](#dependency-graph)
- [Security Model](#security-model)
- [What's NOT Yet Implemented](#whats-not-yet-implemented)

---

## Biological Metaphor

NOVA models an infrastructure as a **living body**:

| Biological System | NOVA Equivalent | Role |
|---|---|---|
| **Nervous System** | Synapse Engine | Passive observation, sensory input, topology mapping |
| **Immune System** | Cytokine Engine | Anomaly detection, alerting, digital anesthesia |
| **Spine** | SPINA Chain | Immutable immune memory, cryptographic proofs |
| **Brain/Consciousness** | Cockpit Dashboard | Visualization, situational awareness |

```
                    ┌──────────────────┐
                    │   CONSCIOUSNESS   │
                    │    (Cockpit)      │
                    │     :8080         │
                    └────────┬──────────┘
                             │ reads all
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  NERVOUS SYSTEM  │ │  IMMUNE SYSTEM   │ │      SPINE       │
│   (Synapse)      │ │   (Cytokine)     │ │     (SPINA)      │
│    :5191         │ │    :5190         │ │     :5194        │
│                  │ │                  │ │                  │
│ • Passive sniff  │ │ • Rule engine    │ │ • Append-only    │
│ • Organ discover │ │ • Alert mgmt     │ │ • Merkle tree    │
│ • Topology graph │ │ • Anesthesia     │ │ • Ed25519 sigs   │
│ • Baseline       │ │ • Severities     │ │ • O(log n) proof │
└────────┬─────────┘ └────────▲─────────┘ └────────▲─────────┘
         │                    │                    │
         │                    │ reads              │ writes alerts
         │         ┌──────────┘                    │
         │         │                               │
         ▼         │                               │
    ┌─────────┐    │                   ┌───────────────────┐
    │ Packet  │    │                   │  Threat memory is │
    │ Capture │    └───────────────────│  permanent.       │
    │(scapy)  │       Cytokine checks  │  SPINA never      │
    └─────────┘       Synapse state    │  forgets.         │
                       every cycle      └───────────────────┘
```

---

## Four-Engine Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                         NOVA ORGANISM                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  SYNAPSE ENGINE (:5191)                     │  │
│  │  Nervous system — passive observation, topology, baseline   │  │
│  │                                                             │  │
│  │  Scanner ──► Graph ──► Baseline ──► REST API                │  │
│  │  (scapy)     (networkx) (numpy)     (Flask)                 │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │ topology graph, organ state              │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                 CYTOKINE ENGINE (:5190)                      │  │
│  │  Immune system — anomaly detection, alerting, reflexes      │  │
│  │                                                             │  │
│  │  6 Detection Rules ──► Alert Queue ──► REST API             │  │
│  │  ┌──────────────┐                                          │  │
│  │  │ Anesthesia   │ (digital isolation sandbox)               │  │
│  │  └──────────────┘                                          │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │ threat signatures                        │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                   SPINA CHAIN (:5194)                        │  │
│  │  Cryptographic spine — immutable memory, Merkle proofs      │  │
│  │                                                             │  │
│  │  Blocks ──► Merkle Tree ──► Ed25519 ──► REST API           │  │
│  │  (append)    (O(log n))    (signatures)                     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                MOLECULAR COCKPIT (:8080)                     │  │
│  │  Consciousness layer — real-time 3D viz, organ vitals       │  │
│  │                                                             │  │
│  │  HTML5 Canvas ──► Live polling ──► All engines              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                        CLI (`nova`)                          │  │
│  │  scan | status | dashboard | alerts | spina                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

The complete lifecycle from raw packet to immutable memory block:

```
                           THE DATA FLOW
                           =============

  INTERNET / LAN
       │
       │  Raw IP packets (passive, zero-emission)
       ▼
  ┌──────────┐
  │  scapy   │  Packet capture (sniff, filter="ip")
  │  sniff   │
  └────┬─────┘
       │
       │  _packet_handler() per packet
       ▼
  ┌──────────────────────────────────────────────────┐
  │              SYNAPSE ENGINE                       │
  │                                                   │
  │  1. Parse: src_ip, dst_ip, src_mac, dst_mac,     │
  │            protocol, port, payload_len            │
  │                                                   │
  │  2. discover_organ(ip, mac)                       │
  │     ┌───────────────────────────┐                │
  │     │ New? → Create Organ       │                │
  │     │   • SHA256 DNA fingerprint│                │
  │     │   • first_seen = now      │                │
  │     │                           │                │
  │     │ Existing? → heartbeat()   │                │
  │     │   • last_seen = now       │                │
  │     └───────────────────────────┘                │
  │                                                   │
  │  3. form_synapse(organ_a, organ_b, proto, port)  │
  │     ┌──────────────────────────────┐             │
  │     │ New synapse? → Create        │             │
  │     │   • weight = 1.0             │             │
  │     │                              │             │
  │     │ Existing? → activate()       │             │
  │     │   • weight += 0.01 (Hebbian) │             │
  │     │   • volume += pkt_len        │             │
  │     └──────────────────────────────┘             │
  │                                                   │
  │  4. Build networkx topology graph (on demand)     │
  │  5. Evaluate baseline after 7 days                │
  │                                                   │
  └─────────────┬─────────────────────────────────────┘
                │
                │  CytokineEngine(synapse_engine)
                │  .check() — runs detection rules
                ▼
  ┌──────────────────────────────────────────────────┐
  │              CYTOKINE ENGINE                      │
  │                                                   │
  │  Rule 1: New synapse (< 5 min)        → LOW      │
  │  Rule 2: Silent organ (> 7 days)      → MEDIUM   │
  │  Rule 3: Silent organ (> 24 hours)    → LOW      │
  │  Rule 4: External connection           → HIGH     │
  │  Rule 5: Volume spike 5x baseline     → MEDIUM   │
  │  Rule 6: Volume spike 10x baseline    → HIGH     │
  │  Rule 7: Unknown protocol             → MEDIUM   │
  │  Rule 8: Port scan pattern             → CRITICAL │
  │                                                   │
  │  Deduplication: skip if message already active    │
  │                                                   │
  │  Alerts → active_alerts[] + alerts[]              │
  │                                                   │
  │  Optional: AnesthesiaSandbox.isolate(ip)          │
  │    • Redirects to observation VLAN                │
  │    • Captures behaviors for analysis              │
  │                                                   │
  └─────────────┬─────────────────────────────────────┘
                │
                │  User or automated: adds block to SPINA
                │  chain.add_block({type, hash, malware, behaviors})
                ▼
  ┌──────────────────────────────────────────────────┐
  │                SPINA CHAIN                        │
  │                                                   │
  │  1. Create SpinaBlock:                            │
  │     • prev_hash = last block or GENESIS           │
  │     • payload_hash = SHA256(payload)              │
  │     • block_hash = SHA256(prev|ts|payload|val)    │
  │                                                   │
  │  2. Sign with Ed25519 validator key               │
  │                                                   │
  │  3. Add to chain[] (append only)                   │
  │                                                   │
  │  4. Add to MerkleTree (for O(log n) proofs)       │
  │                                                   │
  │  5. Persist chain.json to disk                    │
  │                                                   │
  └──────────────────────────────────────────────────┘

  Immutable record created. Can be verified by any node.
  Merkle proof: O(log n) verification instead of O(n).
```

---

## Port Map & Service Layout

```
                    NOVA Port Map
                    =============

    External                                  Internal
    ────────                                  ────────

    :8080 ─── Cockpit Dashboard ───► Reads from all engines
              (Flask, HTML5 Canvas)
              Human interface

    :5191 ─── Synapse API ─────────► Exposes topology graph
              GET /graph                Internal state
              GET /health              (read-only)

    :5190 ─── Cytokine API ───────► Exposes alerts
              GET /alerts              Immune system state
              POST /alerts/:id/ack    (read + acknowledge)

    :5194 ─── SPINA API ──────────► Exposes chain
              GET /blocks              Immutable memory
              POST /blocks             (read + write)
              GET /verify/:hash

    Services are independent — each can run on its own
    host, in its own container, or all together locally.
```

---

## Component Deep Dives

### Synapse Engine (:5191)

**Paper:** 003 — Le Système Nerveux des Infrastructures

```
SynapseEngine
├── organs: Dict[mac, Organ]
│   ├── ip, mac, hostname, vendor
│   ├── dna: SHA256 fingerprint (unique per organ)
│   ├── services: Dict[port, service_name]
│   ├── protocols: Set[protocol_name]
│   ├── first_seen, last_seen: datetime
│   └── heartbeat() — updates last_seen
│
├── synapses: Dict[key, Synapse]
│   ├── a, b: Organ references
│   ├── protocol, port, volume
│   ├── weight: 1.0 → 10.0 (Hebbian reinforcement)
│   ├── activate() — weight += 0.01
│   ├── decay() — unused synapses weaken
│   └── key = sorted(dna_a, dna_b) + (protocol, port)
│
├── graph: networkx.Graph (built on demand)
├── baseline_period: timedelta(days=7)
├── baseline_ready: bool
│
└── API endpoints:
    GET  /graph          Full topology (organs + synapses)
    GET  /node/<ip|mac>  Organ + neighborhood
    GET  /stats          Packet count, uptime, etc.
    GET  /feed           Recent synapses (last 60s)
    GET  /health         Status + counts
```

**Key design decisions:**
- **Passive only during discovery** — zero packets emitted. This is the "void" principle from Paper 000.
- **Hebbian learning** — synapses that fire together, wire together (weight increases with use). Unused synapses decay.
- **Cryptographic DNA** — each organ gets a SHA256 fingerprint from MAC + protocols + services. No two organs can have the same DNA.
- **Thread-safe** — all state mutations go through `threading.Lock`.

### Cytokine Engine (:5190)

**Paper:** 005 — Le Système Immunitaire des Infrastructures

```
CytokineEngine (reads SynapseEngine)
├── thresholds: Dict[rule_name, Severity]
│   ├── new_synapse        → LOW
│   ├── volume_spike_x5    → MEDIUM
│   ├── volume_spike_x10   → HIGH
│   ├── unknown_protocol   → MEDIUM
│   ├── organ_silent_24h   → LOW
│   ├── organ_silent_7d    → MEDIUM
│   ├── external_connection → HIGH
│   └── port_scan_pattern   → CRITICAL
│
├── active_alerts: List[Alert] (unacknowledged)
├── alerts: List[Alert] (full history)
├── rules_fired: Dict[rule, count]
│
├── check() — run all detection rules
│   ├── Iterates synapses → checks age, external IP
│   ├── Iterates organs → checks idle time
│   └── Deduplicates against active_alerts
│
├── acknowledge(id) — mark alert as handled
│
└── API endpoints:
    GET  /alerts              Active (unacknowledged) alerts
    GET  /alerts/history      Full history (paginated)
    POST /alerts/<id>/ack     Acknowledge an alert
    GET  /rules               Rule thresholds + fire counts
    GET  /health              Status + counts
```

**AnesthesiaSandbox (also Paper 005):**
```
AnesthesiaSandbox
├── isolate(ip, vlan=999)    Mark organ for isolation
├── release(ip)              Remove from sandbox
└── report()                 All active sandboxes
```

The anesthesia concept is a **digital quarantine**: when Cytokine detects a threat, the compromised organ can be redirected to an isolated VLAN for observation — analogous to medical anesthesia where a body part is numbed/isolated while the immune system works.

**Detection Rules (detailed):**

1. **New synapse** — A connection formed within the last 5 minutes between two known organs that haven't communicated before. Severity: LOW. This happens naturally during scaling, but also during lateral movement.

2. **External connection** — An organ communicating with a non-RFC 1918 IP address. Severity: HIGH. Indicates C2 beaconing or data exfiltration.

3. **Silent organ (24h)** — No heartbeat from an organ for 24 hours. Severity: LOW. Could be powered off, or could indicate compromise.

4. **Silent organ (7d)** — No heartbeat for 7 days. Severity: MEDIUM. The organ may have been taken offline or replaced.

5. **Port scan pattern** — Rapid sequential connections to many ports. Severity: CRITICAL. Classic recon behavior.

6. **Volume spike** — Traffic volume significantly above baseline. 5x = MEDIUM, 10x = HIGH.

### SPINA Chain (:5194)

**Paper:** 008 — SPINA — La Colonne Vertébrale Cryptographique

```
SpinaChain
├── chain: List[SpinaBlock] (append only)
├── merkle: MerkleTree (all block hashes)
├── consensus: "PoA" (bootstrap → PoS maturity)
├── validator_id: Node identity
├── private_key, public_key: Ed25519
│
├── add_block(payload) → SpinaBlock
│   ├── prev_hash = last block or GENESIS (64 zeros)
│   ├── Create block, sign with Ed25519
│   ├── Append to chain[]
│   ├── Add to MerkleTree
│   └── Persist to chain.json
│
├── verify_block(hash) → bool
│   └── O(log n) via Merkle proof (not O(n) scan)
│
├── search(query) → List[dict]
│   └── Linear scan of payloads (demo)
│
├── get_info() → chain summary
├── get_all_blocks(limit, offset) → paginated
│
└── API endpoints:
    GET  /info                Chain summary
    GET  /blocks              All blocks (paginated)
    GET  /blocks/<hash>       Single block
    POST /blocks              Add a new block
    GET  /search?q=<query>    Search payloads
    GET  /verify/<hash>       Merkle proof verification
    GET  /merkle              Merkle tree state
    GET  /health              Status
```

**Merkle Tree:**
```
       Root Hash
      /         \
   Hash(AB)    Hash(CD)
   /    \      /    \
  H(A) H(B)  H(C)  H(D)
   │     │     │     │
 Block0 Block1 Block2 Block3

To verify Block2 (C):
  Need: H(D) + position="right" + Hash(AB) + position="left"
  Compute: H(C) → H(CD) → Root
  Compare with stored root
  O(log n) instead of O(n)
```

**Consensus model:**
- **Bootstrap phase**: Proof of Authority (PoA) — a known validator set approves blocks.
- **Maturity phase**: Proof of Stake (PoS) — any node can validate proportionally. This is designed but not yet implemented in SDK v0.1.

### Molecular Cockpit (:8080)

**Paper:** 003, Section 3.3 — Le Cockpit Moléculaire

```
Cockpit Dashboard
├── HTML5 Canvas (real-time topology viz)
├── Polls Synapse (:5191) for graph data
├── Polls Cytokine (:5190) for alerts
├── Polls SPINA (:5194) for chain length
│
├── GET  /              Dashboard HTML
├── GET  /api/health     Aggregated health
└── GET  /api/graph      Full topology
```

The Cockpit is the **consciousness layer** — it aggregates data from all engines and presents a living visualization. Organs appear as pulsing circles, synapses as weighted edges. The sidebar shows real-time vitals.

---

## Persistence Model

```
/opt/nova/
├── synapse/
│   └── state.json       ← Synapse engine state (organs, synapses, stats)
│
├── spina/
│   └── chain.json       ← SPINA blockchain (all blocks, merkle root)
│
└── (future)
    └── cytokine/
        └── alerts.json  ← Alert history (not yet persisted)
```

Files are written as JSON for portability and human readability. In production, these would be backed by a database.

---

## Threading Model

Each engine runs its own threads:

| Engine | Thread | Purpose |
|---|---|---|
| Synapse | `_sniff_thread` | scapy packet capture (blocking) |
| Synapse | `_baseline_thread` | Periodic baseline evaluation (every 60s) |
| Cytokine | (synchronous) | `.check()` called on-demand or by CLI |
| SPINA | (synchronous) | Block operations are immediate |
| Cockpit | Flask thread | Web server |
| All APIs | Flask thread | Per-engine REST servers |

Thread safety is guaranteed by `threading.Lock` in SynapseEngine for all state mutations.

---

## Dependency Graph

```
                    nova-cockpit
                   /      |      \
                  /       |       \
          nova-synapse  nova-cytokine  nova-spina
              |            |              |
          scapy         flask         cryptography
          networkx                     (optional)
          flask

External dependencies:
  flask          — All REST APIs + Cockpit
  scapy          — Passive packet capture
  networkx       — Topology graph (optional, Synapse)
  cryptography   — Ed25519 signatures (optional, SPINA)
```

---

## Security Model

1. **Zero-emission discovery** — Synapse never sends packets during observation. It is invisible to the infrastructure.

2. **Append-only memory** — SPINA blocks cannot be deleted or modified. The Merkle tree makes tampering detectable in O(log n).

3. **Cryptographic identity** — Each organ has a SHA256 DNA fingerprint. Synapse keys are derived from DNA pairs.

4. **Isolation** — Anesthesia sandbox redirects compromised organs without affecting healthy ones.

5. **No remote shell** — NOVA never opens reverse shells or executes commands on organs. It observes and alerts only. Interventions are manual or via Anesthesia.

---

## What's NOT Yet Implemented

See [PAPER_MAP.md](PAPER_MAP.md) for a detailed paper-by-paper gap analysis. High-level gaps:

- **Peer-to-peer SPINA consensus** (PoS maturity phase, block propagation)
- **Automated reflex actions** (auto-block in firewall via Anesthesia)
- **Cross-node Cytokine correlation** (distributed immune system)
- **Persistent alert storage** (current alerts are in-memory only)
- **LLDP/CDP/SSDP/mDNS** passive discovery (currently ARP + IP only)
- **Volume baseline computation** (thresholds are static, not learned)
- **3D/WebGL Cockpit** (currently 2D Canvas)

---

## Design Principles

1. **Graft, don't replace** — NOVA attaches to existing infrastructure without modifying it.
2. **Observe first, act later** — The 7-day baseline period ensures you know "normal" before flagging "abnormal."
3. **The void is presence** — Silence is data. An organ that stops communicating is as significant as one that starts.
4. **Memory is immunity** — SPINA ensures the organism never forgets a threat. What was seen once is remembered forever.
5. **Biological fidelity** — Every concept maps to a biological analog. This is intentional — biological systems have solved distributed sensing, immunity, and memory over billions of years.

---

> *Next: See [API.md](API.md) for the complete REST API reference, [PAPER_MAP.md](PAPER_MAP.md) for the research paper mapping, and [CONTRIBUTING.md](../CONTRIBUTING.md) for how to contribute.*
