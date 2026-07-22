# NOVA SDK

**Digital Organism Toolkit. Graft, don't replace.**

NOVA ne remplace pas votre infrastructure — elle s'y greffe. Comme un symbiote, elle observe passivement le reseau (SPINA), detecte les anomalies avant qu'elles ne deviennent des pannes (Cytokine), connecte les agents entre eux (Synapse), et visualise l'ensemble comme un organisme vivant en 3D (Cockpit).

> *"The void is an invitation. Presence is immunity."* — NOVA, Paper 005

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![0DATA Lab](https://img.shields.io/badge/0DATA-Lab-dark.svg)](https://0data.fr)

---

## Quick Start

```bash
git clone https://github.com/ZERODATALAB/nova-sdk.git
cd nova-sdk
pip install -e .
nova demo
```

Open **http://localhost:8080** — the molecular cockpit appears instantly with demo data. Passive scan starts in background, replacing simulated organs with real ones as they are discovered.

**One command. Zero configuration. Works immediately.**

---

## Architecture

```
                    NOVA SDK
   +----------+----------+----------+----------+
   |  SPINA   | CYTOKINE | SYNAPSE  | COCKPIT  |
   |  Memoire | Immunite | Connexion|  Vue 3D  |
   | Blockchain|Anomalies| Inter-agents| Moleculaire|
   +----------+----------+----------+----------+
```

| Module | Role | Biological Inspiration |
|--------|------|----------------------|
| **SPINA** | Immutable blockchain memory of the network | Spinal cord — information backbone |
| **Cytokine** | Anomaly detection, immune scoring | Immune system — self/non-self recognition |
| **Synapse** | Inter-agent connection, topology discovery | Synaptic junction — signal transmission |
| **Cockpit** | Real-time 3D molecular visualization | Visual cortex — state representation |

---

## Demo vs Commercial

The demo (`nova demo`) includes the **full visual experience** — 3D molecular cockpit, live passive scanning, animated synapses, breathing cell nodes. It is functionally identical to the commercial version with these limits:

| Feature | Demo | Commercial |
|---------|------|------------|
| 3D Molecular Cockpit | Full | Full |
| Passive Scan Duration | 5 minutes | Unlimited |
| Max Organs Tracked | 10 | Unlimited |
| SPINA Blockchain | Read-only | Read/Write |
| Cytokine Alerts | 3 rules | Full rule engine |
| Synapse Weight Learning | Frozen | Hebbian (live) |
| Data Export (JSON/CSV) | --- | Included |
| Multi-Instance Sync | --- | Included |
| REST API | Local only | Network + Auth |

To license: https://0data.fr/products/nova

---

## Commands

```bash
nova demo                  # Cockpit + live scan (one command)
nova scan                  # Passive network discovery
nova status -v             # Full topology report
nova dashboard             # Cockpit only (no scan)
nova spina add|search|list # SPINA blockchain
nova alerts                # Active immune alerts
```

---

## Python API

```python
from nova_synapse.engine import SynapseEngine
from nova_cytokine.engine import CytokineEngine
from nova_spina.chain import SpinaChain
from nova_cockpit.dashboard import start_dashboard

# Discovery (passive — zero packets emitted)
engine = SynapseEngine()
engine.start_passive()           # background scan

# Immune analysis
cyto = CytokineEngine(engine)
alerts = cyto.check()

# Immutable audit trail
chain = SpinaChain()
chain.add_block({"type": "scan", "organs_found": 5})

# 3D cockpit
start_dashboard(port=8080)       # http://localhost:8080
```

---

## Requirements

Python 3.10+, Flask >=3.0, Scapy >=2.5, NetworkX >=3.0, Cryptography >=41.0.

---

## Paper Map

Every NOVA module corresponds to a peer-reviewed paper available on Zenodo:

| Module | Paper | Zenodo |
|--------|-------|--------|
| SPINA | 006 — SPINA: Spinal Column of Digital Infrastructure | DOI pending |
| Cytokine | 005 — Resilience: Digital Immune System | DOI pending |
| Synapse | 003 — The Nervous System of Infrastructure | DOI pending |
| Cockpit | 003 — Section 3.3: The Molecular Cockpit | DOI pending |

Papers: https://0data.fr/papers

---

## Support

NOVA is open source and independent. Two ways to help:

| You want to... | → |
|---|---|
| **Offrir un café** ☕ | [Soutenir financièrement](https://buy.stripe.com/cNi14g7pP2Rpg8Sg6F14402) — chaque geste compte |
| **Contribuer au code** 🧬 | [Issues](https://github.com/ZERODATALAB/nova-sdk/issues) · [Pull Requests](https://github.com/ZERODATALAB/nova-sdk/pulls) · [Discussions](https://github.com/ZERODATALAB/nova-sdk/discussions) |

Le labo lit chaque PR. Les bonnes idées finissent greffées.

---

## License

MIT License — see [LICENSE](LICENSE).

NOVA is open source. The molecular cockpit, passive discovery, and core SDK are free to use, modify, and distribute. Commercial features (unlimited scanning, multi-instance, data export) require a license.

0DATA Lab — https://0data.fr
