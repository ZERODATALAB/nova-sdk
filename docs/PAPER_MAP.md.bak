# NOVA SDK — 0DATA Paper Mapping

This document maps each [0DATA paper](https://0data.fr/paper/) to its corresponding NOVA SDK module, lists what is implemented, and catalogs what remains to be built. Use this as a roadmap for contributions.

---

## Paper Index

| Paper | Title | Theme | Status in SDK |
|---|---|---|---|
| 000 | La Loi | Theoretical foundation | 📖 Referenced (no code) |
| 001 | La Discipline | Operational framework | 📖 Referenced (no code) |
| 002 | Synthética | Synthetic digital life | ❌ Not yet |
| 003 | Le Système Nerveux | Nervous system for infrastructure | ✅ **Core** — Synapse + Cockpit |
| 004 | Greffe Numérique | Digital grafting | 🔶 Partially (passive mode) |
| 005 | Le Système Immunitaire | Immune system | ✅ **Core** — Cytokine + Anesthesia |
| 006 | RESILIENCE | Self-healing infrastructure | ❌ Not yet |
| 007 | Convergence | Network convergence theory | ❌ Not yet |
| 008 | SPINA | Cryptographic spine | ✅ **Core** — Chain + Merkle |
| 009 | Symbiotic Internet | Symbiotic network vision | ❌ Not yet |

---

## Paper 003 — Le Système Nerveux des Infrastructures

> *"The nervous system is the first organ. Before you can defend a body, you must feel it."*

### Implemented ✅

| Concept | Module | Location |
|---|---|---|
| Passive network discovery | Synapse Engine | `nova_synapse/engine.py` — `start_passive()` |
| Organ (device) model | Synapse Engine | `nova_synapse/engine.py` — `Organ` class |
| Synapse (connection) model | Synapse Engine | `nova_synapse/engine.py` — `Synapse` class |
| Hebbian learning (weight reinforcement) | Synapse Engine | `Synapse.activate()` — weight += 0.01 |
| Synaptic pruning (decay) | Synapse Engine | `Synapse.decay()` — weight -= 0.1 |
| Cryptographic DNA (organ fingerprint) | Synapse Engine | `Organ._compute_dna()` — SHA256 |
| Topology graph (networkx) | Synapse Engine | `get_graph()` — nodes + edges |
| Baseline period (7-day observation) | Synapse Engine | `baseline_period`, `is_baseline_ready()` |
| REST API for topology | Synapse Engine | `start_api()` — port :5191 |
| Molecular Cockpit (dashboard) | Cockpit | `nova_cockpit/dashboard.py` — port :8080 |
| Real-time organ vitals | Cockpit | Canvas visualization |

### NOT Yet Implemented ❌

| Concept | Description | Priority |
|---|---|---|
| **Multi-protocol passive discovery** | LLDP, CDP, SSDP, mDNS, DHCP fingerprinting | High |
| **Service fingerprinting** | Identify services by port/behavior (nginx, postgres, redis, etc.) | High |
| **OS fingerprinting** | Passive OS detection via TCP/IP stack analysis (p0f-style) | Medium |
| **DNS-based hostname resolution** | Resolve hostnames from captured DNS queries | Medium |
| **Vendor OUI lookup** | Resolve MAC → vendor using IEEE OUI database | Low |
| **Topology layout algorithms** | Force-directed, hierarchical, geographic layouts | Medium |
| **3D/WebGL Cockpit** | Paper describes a 3D molecular cockpit; currently 2D Canvas | Low |
| **Time-series baseline** | Statistical baseline per organ/protocol (volume, frequency, burstiness) | High |
| **Anomaly scoring** | Quantitative deviation score per synapse, not just boolean rules | Medium |
| **Historical graph snapshots** | Store and replay past topology states | Low |
| **Packet-level replay** | Record and replay captured traffic for training/demo | Low |

---

## Paper 005 — Le Système Immunitaire des Infrastructures

> *"The immune system does not know what is dangerous. It knows what is self."*

### Implemented ✅

| Concept | Module | Location |
|---|---|---|
| Detection rule engine | Cytokine Engine | `nova_cytokine/engine.py` — `CytokineEngine.check()` |
| New synapse detection | Cytokine — Rule 1 | Age < 300s → severity LOW |
| Silent organ detection | Cytokine — Rules 2-3 | Idle > 24h/7d → LOW/MEDIUM |
| External connection detection | Cytokine — Rule 4 | Non-RFC1918 dest → HIGH |
| RFC 1918 private IP detection | Cytokine | `_is_external()` |
| Alert model | Cytokine | `Alert` class with severity, evidence, acknowledgment |
| Severity levels | Cytokine | `Severity` enum: INFO, LOW, MEDIUM, HIGH, CRITICAL |
| Alert deduplication | Cytokine | Skip if message already in active_alerts |
| Acknowledgment | Cytokine | `acknowledge()` removes from active list |
| Rule fire statistics | Cytokine | `rules_fired` counter |
| REST API for alerts | Cytokine | `start_api()` — port :5190 |
| Digital anesthesia (sandbox) | Cytokine | `AnesthesiaSandbox.isolate()`, `release()`, `report()` |

### NOT Yet Implemented ❌

| Concept | Description | Priority |
|---|---|---|
| **Volume baseline computation** | Calculate per-organ/per-protocol volume averages over baseline period | Critical |
| **Volume spike detection** | Rules defined (`volume_spike_x5`, `volume_spike_x10`) but thresholds are not computed | Critical |
| **Unknown protocol detection** | Rule defined but no implementation — needs baseline of expected protocols per organ | High |
| **Port scan pattern detection** | Rule defined as CRITICAL but no implementation | High |
| **Automated reflex actions** | Auto-isolate via Anesthesia when alert severity ≥ HIGH | Medium |
| **Network-level anesthesia** | Actual VLAN redirection / iptables integration (currently simulation only) | High |
| **Auto-acknowledge rules** | Time-based or condition-based auto-ack for LOW severity alerts | Low |
| **Alert correlation** | Link related alerts (e.g., new synapse + external connection on same organ) | Medium |
| **Alert persistence** | Save alerts to disk (currently in-memory only, lost on restart) | High |
| **Alert notification channels** | Webhook, Slack, email, syslog integrations | Low |
| **Distributed Cytokine** | Cross-node correlation — "herd immunity" across multiple NOVA instances | High |
| **T-cell analog** | Learned immune memory — patterns that caused alerts get prioritized | Medium |
| **B-cell analog** | Auto-generate detection rules from SPINA threat signatures | Medium |
| **Autoimmune suppression** | Detect and suppress false-positive cascades | Low |
| **Baseline anomaly scoring** | Statistical models (z-score, isolation forest, moving average) | High |

---

## Paper 008 — SPINA — La Colonne Vertébrale Cryptographique

> *"The spine remembers what the brain forgets."*

### Implemented ✅

| Concept | Module | Location |
|---|---|---|
| Blockchain data structure | SPINA Chain | `nova_spina/chain.py` — `SpinaChain` class |
| Block model | SPINA Chain | `SpinaBlock` class — hash, prev_hash, payload, signature |
| Merkle tree | SPINA Chain | `MerkleTree` class — `add()`, `get_proof()`, `verify()` |
| Merkle proof verification | SPINA Chain | `verify_block()` — O(log n) via Merkle proof |
| Ed25519 signatures | SPINA Chain | `cryptography` library — `block.sign(private_key)` |
| Demo fallback (no crypto) | SPINA Chain | HMAC-style fallback when `cryptography` not installed |
| Genesis block | SPINA Chain | `GENESIS_HASH = "0" * 64` |
| Append-only guarantee | SPINA Chain | Chain is a Python list — no deletion API |
| Content search | SPINA Chain | `search(query)` — substring match on payloads |
| Type-based search | SPINA Chain | `search_by_type(type)` |
| Chain persistence | SPINA Chain | `_save()` / `_load()` to `chain.json` |
| Paginated block listing | SPINA Chain | `get_all_blocks(limit, offset)` |
| REST API | SPINA Chain | `SpinaAPI.start()` — port :5194 |
| PoA consensus (bootstrap) | SPINA Chain | `consensus = "PoA"` — validator signs blocks |

### NOT Yet Implemented ❌

| Concept | Description | Priority |
|---|---|---|
| **PoS consensus (maturity)** | Proof of Stake — any node can validate proportionally | Critical |
| **Peer-to-peer block propagation** | Gossip protocol between SPINA nodes | Critical |
| **Validator registration** | On-chain validator identity, stake management | High |
| **Multi-node chain sync** | New nodes download and verify entire chain from peers | High |
| **Fork resolution** | Longest-chain / heaviest-chain rule for conflict resolution | High |
| **Block reward / incentive** | Tokenomics for validators | Medium |
| **Smart contract layer** | Programmable rules on-chain (e.g., auto-block on threat match) | Medium |
| **SPINA light client** | Verify blocks without storing full chain (Merkle proofs only) | Medium |
| **Zero-knowledge proofs** | Prove block inclusion without revealing payload | Low |
| **Encrypted payloads** | Payloads encrypted with recipient's public key | Low |
| **Cross-chain anchoring** | Anchor SPINA Merkle roots to Ethereum/Bitcoin for ultimate immutability | Low |
| **Bloom filters** | Efficient "is this hash in the chain?" without full scan | Medium |
| **State proofs** | Prove chain state at a given block height | Low |
| **Validator rotation** | Periodic validator set changes for security | Medium |
| **Slashing conditions** | Penalize malicious validators | Medium |

---

## Paper 004 — Greffe Numérique (Digital Graft)

### Implemented ✅

| Concept | Module | Location |
|---|---|---|
| Passive-only mode (no packet emission) | Synapse Engine | `start_passive()` — sniff only, no probes |
| Graft metaphor | Architecture | The entire SDK is designed to attach without replacing |

### NOT Yet Implemented ❌

| Concept | Description | Priority |
|---|---|---|
| **Active discovery mode** | Optional ARP/ICMP probes after baseline is established | Medium |
| **Auto-graft detection** | Detect when NOVA is attached to a new infrastructure segment | Low |
| **Graft compatibility check** | Validate that the target infrastructure can support the graft | Low |
| **Multi-graft coordination** | Multiple NOVA instances coordinating on the same infrastructure | Medium |

---

## Papers with No SDK Implementation Yet

### Paper 002 — Synthética
- **Theme:** Synthetic digital life, self-replicating security
- **Potential modules:** Auto-scaling NOVA, self-healing network topologies, digital organism reproduction
- **Priority:** Low — foundational research, not actionable yet

### Paper 006 — RESILIENCE
- **Theme:** Self-healing infrastructure
- **Potential modules:** Automated remediation, traffic rerouting, graceful degradation
- **Priority:** Medium — builds on Cytokine reflex actions

### Paper 007 — Convergence
- **Theme:** Network convergence theory
- **Potential modules:** Optimal topology convergence, routing optimization
- **Priority:** Low

### Paper 009 — Symbiotic Internet
- **Theme:** Vision of a symbiotic internet
- **Potential modules:** Federation protocol, inter-NOVA communication
- **Priority:** Medium — requires SPINA P2P first

### Papers 000 & 001
- These are theoretical/philosophical papers. They inform all modules but have no direct code. Their principles (the void, presence, discipline, observation without interference) are embedded in the architecture.

---

## Implementation Priority Matrix

```
                    Impact
                 Low    Medium   High
             ┌────────┬────────┬────────┐
        High │ Volume │ SPINA  │ Multi- │
             │baseline│  P2P   │protocol│
             │        │        │ disc.  │
             ├────────┼────────┼────────┤
Effort Medium│3D Cpit │ Reflex │Alert   │
             │        │ actions│persist │
             ├────────┼────────┼────────┤
        Low  │ OUI    │Webhooks│Service │
             │lookup  │        │finger. │
             └────────┴────────┴────────┘

Start here → Top-right quadrant (high impact, high effort)
Quick wins → Bottom-left (low effort, low impact)
```

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to contribute implementations of the missing features listed above. Each "Not Yet Implemented" item is a potential contribution — pick one, open an issue to discuss, and start building.

---

> *See [ARCHITECTURE.md](ARCHITECTURE.md) for system design and [API.md](API.md) for the REST reference.*
