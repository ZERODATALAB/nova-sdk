# NOVA SDK

**Digital Organism Toolkit. Graft, don't replace.**

NOVA ne remplace pas votre infrastructure — elle s'y greffe. Comme un symbiote, elle observe passivement le réseau (SPINA), détecte les anomalies avant qu'elles ne deviennent des pannes (Cytokine), connecte les agents entre eux (Synapse), et grave chaque événement dans une mémoire immutable.

> *"The void is an invitation. Presence is immunity."* — NOVA, Paper 005

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![0DATA Lab](https://img.shields.io/badge/0DATA-Lab-dark.svg)](https://0data.fr)

---

## Architecture

```
┌──────────────────────────────────────────┐
│                 NOVA SDK                  │
├──────────┬──────────┬──────────┬─────────┤
│  SPINA   │ CYTOKINE │ SYNAPSE  │ COCKPIT │
│  Mémoire │ Immunité │ Connexion│  Vue 3D │
│ Blockchain│Anomalies │ Inter-agents│       │
└──────────┴──────────┴──────────┴─────────┘
```

| Module | Rôle | Inspiration biologique |
|--------|------|----------------------|
| **SPINA** | Mémoire blockchain du réseau | Moelle épinière — colonne vertébrale de l'information |
| **Cytokine** | Détection d'anomalies, scoring | Système immunitaire — reconnaît le soi du non-soi |
| **Synapse** | Connexion inter-agents, dispatch | Jonction synaptique — transmission de signal |
| **Cockpit** | Visualisation 3D temps réel | Cortex visuel — représentation de l'état |

---

## Installation

```bash
git clone https://github.com/ZERODATALAB/nova-sdk.git
cd nova-sdk
pip install -e .
```

Requirements: Python 3.10+, Flask ≥3.0, Scapy ≥2.5, Cryptography ≥41.0

---

## Quick Start

```bash
# Passive network scan — no packets sent, zero footprint
nova scan --subnet 192.168.1.0/24

# Start the immune engine on discovered hosts
nova immune --watch

# Launch the 3D cockpit
nova cockpit --port 8080
```

Or programmatically:

```python
from nova_spina.chain import SpinaChain
from nova_cytokine.engine import CytokineEngine

# Initialize the memory chain
spina = SpinaChain()

# Passive scan — reads ARP tables, DHCP leases, LLDP neighbors
devices = spina.scan(subnet="192.168.1.0/24")

# Run immune analysis
cytokine = CytokineEngine()
for device in devices:
    score = cytokine.analyze(device)
    if score > 0.8:
        print(f"[!] Anomaly: {device.name} — score {score}")
```

---

## Deep Dive

### SPINA — Blockchain Memory

Every network event is hashed into a block, chained cryptographically. The chain is append-only, immutable, and verifiable. SPINA builds a temporal graph of your infrastructure — you can replay the last hour, day, or month to understand exactly what changed.

```python
from nova_spina.chain import SpinaChain

chain = SpinaChain()
chain.append({"event": "device_joined", "mac": "aa:bb:cc:dd:ee:ff"})
chain.verify()  # True — the chain is intact
```

### Cytokine — Immune System

Cytokine watches baseline behavior and scores deviations. It doesn't need rules — it learns what "normal" looks like from passive observation and flags the unfamiliar.

- **Zero configuration**: no thresholds to set, no signatures to maintain
- **Self/Non-self**: distinguishes legitimate topology changes from intrusion
- **Continuous learning**: adapts as your infrastructure evolves

### Synapse — Inter-Agent Connection

Synapse lets NOVA agents discover each other and share intelligence. One agent detects an anomaly → all agents are immunized. Built on a lightweight pub/sub mesh with cryptographic identity.

---

## Paper Map

Every module maps to a 0DATA academic paper:

| SDK Module | Paper | Title |
|-----------|-------|-------|
| SPINA | [Paper 003](https://0data.fr/paper/003) | Spinal Memory — Append-Only Infrastructure Graph |
| Cytokine | [Paper 004](https://0data.fr/paper/004) | Digital Immune System — Anomaly Detection Without Signatures |
| Synapse | [Paper 005](https://0data.fr/paper/005) | Synaptic Grafting — Inter-Agent Communication Protocol |
| Cockpit | [Paper 006](https://0data.fr/paper/006) | 3D Organism Visualization |

Full mapping: [docs/PAPER_MAP.md](docs/PAPER_MAP.md)

---

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) — design principles, data flow
- [API Reference](docs/API.md) — complete REST endpoint documentation
- [Paper Map](docs/PAPER_MAP.md) — academic paper → code mapping
- [Contributing](CONTRIBUTING.md) — how to graft your own modules

---

## Philosophy

NOVA is built on a simple principle: **the network is already alive**. We don't impose structure — we read the structure that's already there. Like a physician who observes before intervening, NOVA listens first.

- **Passive by default** — zero packets sent during discovery
- **Graft, don't replace** — works alongside existing tooling
- **Immutable memory** — blockchain-backed audit trail
- **Open source** — MIT license, no strings attached

---

## License

MIT © [0DATA Lab](https://0data.fr)

---

<p align="center">
  <sub>Part of the <a href="https://0data.fr">0DATA</a> ecosystem — Know &middot; Protect &middot; Remember</sub><br>
  <sub><a href="docs/">Documentation Site</a> with pastel glassmorphism design</sub>
</p>
