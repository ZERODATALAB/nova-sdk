# Contributing to NOVA SDK

Thank you for your interest in contributing to NOVA — the first digital organism. This guide covers everything you need to get started: environment setup, code style, how to add features, and where to find tasks.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Testing](#testing)
- [How to Add...](#how-to-add)
  - [A new detection rule](#a-new-detection-rule)
  - [A new SPINA consensus mechanism](#a-new-spina-consensus-mechanism)
  - [A new passive discovery protocol](#a-new-passive-discovery-protocol)
  - [A new CLI command](#a-new-cli-command)
  - [A new Cockpit visualization](#a-new-cockpit-visualization)
- [Pull Request Process](#pull-request-process)
- [Issue Tracker](#issue-tracker)
- [Release Process](#release-process)
- [License](#license)

---

## Code of Conduct

NOVA is built on the [0DATA principles](https://0data.fr/paper/000-la-loi.html): observation without interference, memory as immunity, and the void as an invitation. In practice:

- Be curious. Ask questions. Challenge assumptions.
- Be constructive. Every critique should come with a suggested path forward.
- Be respectful. Everyone here is building something unprecedented.
- **No AI-generated spam.** Thoughtful use of AI tools is fine. Mass-generated PRs are not.

---

## Development Environment

### Prerequisites

- **Python 3.10+** (required — uses structural pattern matching and type hints)
- **Linux** (packet capture requires raw socket access; macOS works for non-capture development)
- **pip 23.0+**

### Setup

```bash
# Clone the repository
git clone https://github.com/0data-lab/nova-sdk.git
cd nova-sdk

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in editable mode with all development dependencies
pip install -e ".[dev]"

# Install optional dependencies individually as needed
pip install scapy        # Packet capture
pip install networkx     # Topology graphs
pip install cryptography # Ed25519 signatures (SPINA)
```

If `[dev]` extras aren't defined yet in `setup.py`, install manually:

```bash
pip install -e .
pip install black ruff pytest pytest-cov
```

### Verify Installation

```bash
# Check that the CLI works
nova --help

# Run a quick smoke test
python -c "from nova_synapse import get_engine; e = get_engine(); print('Synapse engine OK')"
python -c "from nova_cytokine import CytokineEngine, Alert, Severity; print('Cytokine engine OK')"
python -c "from nova_spina import get_chain; c = get_chain(); print('SPINA chain OK')"
python -c "from nova_cockpit import start_dashboard; print('Cockpit OK')"
```

---

## Project Structure

```
nova-sdk/
├── nova_synapse/           # Nervous system — network discovery
│   ├── __init__.py         #   Exports: SynapseEngine, get_engine
│   └── engine.py           #   Organ, Synapse, SynapseEngine, API
│
├── nova_cytokine/          # Immune system — alerts & detection
│   ├── __init__.py         #   Exports: CytokineEngine, Alert, Severity, AnesthesiaSandbox
│   └── engine.py           #   Alert, CytokineEngine, AnesthesiaSandbox, API
│
├── nova_spina/             # Cryptographic spine — blockchain memory
│   ├── __init__.py         #   Exports: SpinaChain, SpinaBlock, MerkleTree, SpinaAPI, get_chain
│   └── chain.py            #   MerkleTree, SpinaBlock, SpinaChain, SpinaAPI
│
├── nova_cockpit/           # Consciousness — web dashboard
│   ├── __init__.py         #   Exports: start_dashboard
│   └── dashboard.py        #   Flask app, HTML5 Canvas dashboard
│
├── cli/                    # Command-line interface
│   ├── __init__.py
│   └── main.py             #   nova scan, status, dashboard, alerts, spina
│
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     #   Deep architecture overview
│   ├── API.md              #   Complete REST API reference
│   └── PAPER_MAP.md        #   Paper → module mapping, gap analysis
│
├── examples/               # Runnable demo scripts
│   └── demo_scan.py        #   End-to-end scan demo
│
├── tests/                  # Test suite (create this!)
│   ├── test_synapse.py
│   ├── test_cytokine.py
│   ├── test_spina.py
│   └── test_cli.py
│
├── setup.py                # Package definition
├── README.md               # Project overview
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT
└── .gitignore
```

---

## Code Style

NOVA SDK follows strict formatting rules. Consistency is non-negotiable.

### Formatter: Black

```bash
# Format all Python files
black nova_synapse/ nova_cytokine/ nova_spina/ nova_cockpit/ cli/ examples/ tests/

# Check formatting without changing files (CI mode)
black --check .
```

**Black configuration** (in `pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py310']
```

### Linter: Ruff

```bash
# Lint all Python files
ruff check .

# Auto-fix where possible
ruff check --fix .
```

**Ruff configuration** (in `pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
```

### Style Guidelines

1. **Docstrings are mandatory.** Every public class and function must have a docstring. Use Google-style:

```python
def discover_organ(self, ip: str, mac: str, hostname: str = "", vendor: str = "") -> Organ:
    """Register or update an organ in the topology.

    If the organ already exists (by MAC), its heartbeat is updated.
    Otherwise, a new Organ is created with a cryptographic DNA fingerprint.

    Args:
        ip: IPv4 address of the organ.
        mac: MAC address in xx:xx:xx:xx:xx:xx format.
        hostname: Optional discovered hostname.
        vendor: Optional OUI vendor name.

    Returns:
        The discovered or updated Organ instance.
    """
```

2. **Type hints** are encouraged but not enforced on internal methods. Public API methods should be fully typed.

3. **Thread safety:** Any code that touches shared engine state (`organs`, `synapses`, `stats`) must hold `self._lock`. Follow the existing pattern:

```python
with self._lock:
    # mutate shared state
```

4. **Imports:** Standard library → third-party → local. Separate groups with a blank line.

5. **Naming:**
   - Classes: `PascalCase` (`SynapseEngine`, `MerkleTree`)
   - Functions/methods: `snake_case` (`discover_organ`, `get_graph`)
   - Constants: `UPPER_SNAKE_CASE` (`HAS_SCAPY`, `GENESIS_HASH`)
   - Private methods: `_leading_underscore` (`_packet_handler`, `_save_state`)

6. **Optional dependencies:** Follow the pattern of graceful degradation with `HAS_*` flags:

```python
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
```

---

## Testing

Tests live in the `tests/` directory. Run them with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nova_synapse --cov=nova_cytokine --cov=nova_spina --cov-report=term-missing

# Run a specific test file
pytest tests/test_spina.py -v
```

### Test Principles

- **Unit tests** for all data structures (Organ, Synapse, Alert, SpinaBlock, MerkleTree)
- **Integration tests** for engine interactions (e.g., Cytokine reading from Synapse)
- **No live network tests** — mock scapy and network calls
- SPINA tests should verify Merkle proof integrity

### Example Test Structure

```python
# tests/test_spina.py
import pytest
from nova_spina.chain import SpinaChain, MerkleTree

def test_genesis_hash():
    chain = SpinaChain(data_dir="/tmp/nova-test-spina")
    assert chain.length == 0
    assert chain.GENESIS_HASH == "0" * 64

def test_add_block():
    chain = SpinaChain(data_dir="/tmp/nova-test-spina")
    block = chain.add_block({"type": "test", "value": 42})
    assert chain.length == 1
    assert block.payload["type"] == "test"

def test_merkle_verify():
    chain = SpinaChain(data_dir="/tmp/nova-test-spina")
    chain.add_block({"type": "a"})
    chain.add_block({"type": "b"})
    chain.add_block({"type": "c"})
    # Verify each block
    for block in chain.chain:
        assert chain.verify_block(block.block_hash) is True
    # Verify non-existent block
    assert chain.verify_block("nonexistent") is False
```

---

## How to Add...

### A new detection rule

Detection rules are the immune system's pattern recognition. To add one:

1. **Add the threshold** in `CytokineEngine.__init__()` in `nova_cytokine/engine.py`:

```python
self.thresholds = {
    # ... existing rules ...
    "dns_tunneling": Severity.CRITICAL,  # NEW
}
```

2. **Add the detection logic** in `CytokineEngine.check()`:

```python
# Rule N: DNS tunneling detection
for syn in self.synapse.synapses.values():
    if syn.port == 53 and syn.protocol == "UDP":
        # Heuristic: DNS packets > 512 bytes are suspicious
        avg_packet_size = syn.volume / max(syn.weight * 10, 1)
        if avg_packet_size > 512:
            a = self._create_alert(
                "dns_tunneling",
                f"Possible DNS tunnel: {syn.a.ip} → {syn.b.ip} (avg pkt: {avg_packet_size:.0f}B)",
                syn.a,
                severity=Severity.CRITICAL,
                evidence={"avg_packet_size": avg_packet_size},
            )
            alerts_this_cycle.append(a)
```

3. **Document the rule** in the Cytokine module docstring and in `docs/API.md`.

4. **Add a test** in `tests/test_cytokine.py`.

### A new SPINA consensus mechanism

SPINA is designed to transition from PoA (bootstrap) to PoS (maturity). To add a new consensus:

1. **Create a consensus module** in `nova_spina/consensus.py`:

```python
class ProofOfStake:
    def __init__(self, chain):
        self.chain = chain
        self.stakes = {}  # validator_id → stake_amount

    def select_validator(self) -> str:
        """Weighted random selection based on stake."""
        # Implementation here
        pass

    def validate_block(self, block, validator) -> bool:
        """Check that the validator is authorized."""
        # Implementation here
        pass
```

2. **Integrate into SpinaChain**:

```python
class SpinaChain:
    def __init__(self, ...):
        # ... existing init ...
        self.consensus_engine = None  # Assigned when maturity reached

    def transition_to_pos(self):
        self.consensus = "PoS"
        self.consensus_engine = ProofOfStake(self)
```

3. **Update the API** to expose consensus state.

4. **Document** in `docs/ARCHITECTURE.md` and `docs/PAPER_MAP.md`.

### A new passive discovery protocol

NOVA currently discovers organs via ARP and IP. To add a new protocol (e.g., LLDP):

1. **Add protocol parsing** in `SynapseEngine._packet_handler()`:

```python
# LLDP discovery
if pkt.haslayer(LLDP):
    # Extract chassis ID, port ID, system name
    organ = self.discover_organ(
        ip=pkt[IP].src,
        mac=pkt[Ether].src,
        hostname=lldp_system_name,
    )
    organ.protocols.add("LLDP")
```

2. **Add filter** in `start_passive()` — update the BPF filter or add protocol-specific sniffing.

3. **Update the Organ model** if the protocol provides new fields.

4. **Document** the new protocol's discovery capabilities.

### A new CLI command

1. **Add the subparser** in `cli/main.py`:

```python
# nova topology
p_topo = sub.add_parser("topology", help="Export topology to file")
p_topo.add_argument("-o", "--output", default="topology.json", help="Output file")
p_topo.add_argument("--format", choices=["json", "dot", "gexf"], default="json")
```

2. **Implement the handler**:

```python
def cmd_topology(args):
    engine = get_engine()
    graph = engine.get_graph()

    if args.format == "json":
        with open(args.output, "w") as f:
            json.dump(graph, f, indent=2)
    elif args.format == "dot":
        # Export to Graphviz DOT format
        pass

    print(f"[NOVA] Topology exported to {args.output}")
```

3. **Register in the command map**:

```python
commands = {
    # ... existing ...
    "topology": cmd_topology,
}
```

### A new Cockpit visualization

The Cockpit uses HTML5 Canvas. To add a visualization:

1. **Edit the JavaScript** in `nova_cockpit/dashboard.py` — the `draw()` function:

```javascript
// Add a heatmap overlay
function drawHeatmap() {
    const gradient = ctx.createRadialGradient(...);
    // ... heatmap logic ...
}
```

2. **Add a new API endpoint** if you need additional data:

```python
@app.route("/api/heatmap")
def api_heatmap():
    # Compute traffic density per organ
    return jsonify({...})
```

3. **Keep the dashboard self-contained** in `DASHBOARD_HTML`. Avoid external CSS/JS dependencies.

---

## Pull Request Process

1. **Open an issue first.** Discuss what you want to build before writing code. This prevents wasted effort.

2. **Branch naming:** `feature/short-description` or `fix/short-description`.

3. **Keep PRs focused.** One feature or fix per PR. If you're adding a detection rule and refactoring the engine, those are two PRs.

4. **Update documentation.** If you change behavior, update the relevant docs in `docs/`.

5. **Add tests.** New features must include tests. Bug fixes should include regression tests.

6. **Run the full check:**

```bash
black --check .
ruff check .
pytest
```

7. **Write a clear PR description:**
   - What problem does this solve?
   - What approach did you take?
   - What are the trade-offs?
   - How was it tested?

8. **Respond to review.** Code review is collaborative, not adversarial. Expect questions and suggestions.

---

## Issue Tracker

Issues are tracked on the [GitHub repository](https://github.com/0data-lab/nova-sdk/issues).

### Issue Labels

| Label | Meaning |
|---|---|
| `good first issue` | Beginner-friendly, well-scoped tasks |
| `help wanted` | Open for community contributions |
| `bug` | Something is broken |
| `enhancement` | New feature or improvement |
| `documentation` | Docs, comments, examples |
| `paper-003` / `paper-005` / `paper-008` | Relates to a specific 0DATA paper |
| `engine/synapse` / `engine/cytokine` / `engine/spina` / `cockpit` | Component-specific |

### Good First Issues

Look for issues labeled `good first issue`. These are designed to be completable in a few hours:

- Adding a vendor OUI lookup to Organ discovery
- Implementing alert persistence (save/load to disk)
- Adding a new CLI output format (CSV, DOT, etc.)
- Writing docstring examples in the codebase
- Adding unit tests for existing code

---

## Release Process

NOVA SDK follows [Semantic Versioning](https://semver.org/):

- **Major (X.0.0):** Breaking API changes, consensus changes
- **Minor (0.X.0):** New features, new detection rules, new protocols
- **Patch (0.0.X):** Bug fixes, documentation, performance

Releases are published to PyPI as `nova-sdk`.

---

## License

NOVA SDK is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full text.

**SPINA is a public good.** The SPINA protocol — the design of the cryptographic spine, its consensus rules, and its Merkle proof format — belongs to everyone who runs a node. The SDK implementation is MIT-licensed, meaning you can use it in commercial products, but the protocol itself is unencumbered by any patent or proprietary claim.

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

- **Documentation:** Start with [ARCHITECTURE.md](docs/ARCHITECTURE.md) and [API.md](docs/API.md)
- **Papers:** [0DATA Corpus](https://0data.fr/paper/)
- **Issues:** [GitHub Issues](https://github.com/0data-lab/nova-sdk/issues)
- **Discussion:** [GitHub Discussions](https://github.com/0data-lab/nova-sdk/discussions)

---

> *"The void is an invitation. Presence is immunity."* — NOVA, Paper 005
