"""
nova-spina — Cryptographic Spine — Immune Memory Blockchain
============================================================
Port :5194 — Decentralized, append-only immune memory.
Consensus: PoA (bootstrap) → PoS (maturity).
Merkle proofs for O(log n) verification.

SPINA records every threat signature, every successful anesthesia,
every certification — immutably, verifiably, forever.

Paper: 008 — SPINA — La Colonne Vertébrale Cryptographique
"""

import json
import time
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ed25519
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    # Pure Python fallback: Ed25519 via hashlib only (weaker, demo only)
    print("[SPINA] [!]  'cryptography' not installed — using demo signatures only.")
    print("[SPINA] Install: pip install cryptography")

try:
    from flask import Flask, jsonify, request
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


# ─── Merkle Tree ────────────────────────────────────────────────────

class MerkleTree:
    """Binary Merkle tree for O(log n) proof verification."""

    def __init__(self):
        self.leaves = []          # ordered list of (data_hash, data)
        self.levels = []          # list of levels: [[leaf_hashes], [level1], ..., [root]]

    def add(self, data: bytes):
        """Add a data item and rebuild the tree."""
        data_hash = hashlib.sha256(data).digest()
        self.leaves.append((data_hash, data))
        self._rebuild()

    def _rebuild(self):
        """Rebuild all levels of the Merkle tree."""
        self.levels = [[h for h, _ in self.leaves]]
        while len(self.levels[-1]) > 1:
            level = self.levels[-1]
            next_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else left
                next_level.append(hashlib.sha256(left + right).digest())
            self.levels.append(next_level)

    @property
    def root(self):
        """Merkle root hash."""
        if not self.levels:
            return hashlib.sha256(b"").digest()
        return self.levels[-1][0] if self.levels[-1] else hashlib.sha256(b"").digest()

    @property
    def root_hex(self):
        return self.root.hex()

    @property
    def size(self):
        return len(self.leaves)

    def get_proof(self, index: int) -> list:
        """Generate a Merkle proof for leaf at index."""
        if index < 0 or index >= len(self.leaves):
            return []
        proof = []
        for level_idx in range(len(self.levels) - 1):
            level = self.levels[level_idx]
            sibling_idx = index ^ 1  # XOR 1 flips the last bit
            if sibling_idx < len(level):
                proof.append({
                    "position": "left" if sibling_idx < index else "right",
                    "hash": level[sibling_idx].hex(),
                })
            index //= 2
        return proof

    def verify(self, data: bytes, proof: list) -> bool:
        """Verify a Merkle proof for given data."""
        current_hash = hashlib.sha256(data).digest()
        for step in proof:
            sibling = bytes.fromhex(step["hash"])
            if step["position"] == "left":
                current_hash = hashlib.sha256(sibling + current_hash).digest()
            else:
                current_hash = hashlib.sha256(current_hash + sibling).digest()
        return current_hash == self.root

    def to_dict(self):
        return {
            "size": self.size,
            "root": self.root_hex,
            "leaves": [h.hex() for h, _ in self.leaves],
        }


# ─── SPINA Block ────────────────────────────────────────────────────

class SpinaBlock:
    """A SPINA blockchain block."""

    def __init__(self, prev_hash, payload, validator=None):
        self.prev_hash = prev_hash
        self.timestamp = datetime.utcnow()
        self.payload = payload           # threat signature, anesthesia report, etc.
        self.payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        self.validator = validator       # validator node ID
        self.signature = None            # Ed25519 signature
        self.block_hash = self._compute_hash()

    def _compute_hash(self):
        seed = f"{self.prev_hash}|{self.timestamp.isoformat()}|{self.payload_hash}|{self.validator or ''}"
        return hashlib.sha256(seed.encode()).hexdigest()

    def sign(self, private_key):
        """Sign the block with validator's Ed25519 private key."""
        if HAS_CRYPTO:
            self.signature = private_key.sign(self.block_hash.encode()).hex()
        else:
            # Demo fallback: HMAC-like signature
            self.signature = hashlib.sha256(
                (self.block_hash + str(private_key)).encode()
            ).hexdigest()

    def to_dict(self):
        return {
            "hash": self.block_hash,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "payload_hash": self.payload_hash,
            "validator": self.validator,
            "signature": self.signature,
        }


# ─── SPINA Chain ────────────────────────────────────────────────────

class SpinaChain:
    """
    SPINA blockchain — append-only immune memory.

    Usage:
        chain = SpinaChain()
        chain.add_block({"type": "threat_signature", "hash": "abc123", "malware": "ransomware_x"})
        chain.add_block({"type": "anesthesia_report", "organ": "10.0.1.5", "behaviors": ["c2_contact", "lateral_scan"]})
    """

    GENESIS_HASH = "0" * 64  # SPINA Genesis Block

    def __init__(self, data_dir="/opt/nova/spina"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.chain = []               # list of SpinaBlock
        self.merkle = MerkleTree()    # Merkle tree of all blocks
        self.validator_id = None
        self.consensus = "PoA"        # PoA → PoS

        # Node identity
        if HAS_CRYPTO:
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()
        else:
            self.private_key = hashlib.sha256(b"nova-demo-key").hexdigest()
            self.public_key = "demo-public-key"

        # Load existing chain
        self._load()

    # ── Block Operations ─────────────────────────────────────────

    def add_block(self, payload: dict) -> SpinaBlock:
        """Add a new block to the chain."""
        prev_hash = self.chain[-1].block_hash if self.chain else self.GENESIS_HASH
        block = SpinaBlock(prev_hash, payload, self.validator_id)
        block.sign(self.private_key)
        self.chain.append(block)

        # Add to Merkle tree
        self.merkle.add(block.block_hash.encode())

        # Persist
        self._save()

        return block

    def get_block(self, block_hash: str) -> dict:
        """Retrieve a block by its hash."""
        for block in self.chain:
            if block.block_hash == block_hash:
                return block.to_dict()
        return None

    def verify_block(self, block_hash: str) -> bool:
        """Verify a block using Merkle proof."""
        for i, block in enumerate(self.chain):
            if block.block_hash == block_hash:
                proof = self.merkle.get_proof(i)
                return self.merkle.verify(block.block_hash.encode(), proof)
        return False

    # ── Query ─────────────────────────────────────────────────────

    def search(self, query: str) -> list:
        """Search blocks by payload content."""
        results = []
        for block in self.chain:
            payload_str = json.dumps(block.payload).lower()
            if query.lower() in payload_str:
                results.append(block.to_dict())
        return results

    def search_by_type(self, payload_type: str) -> list:
        """Search blocks by payload type."""
        return [b.to_dict() for b in self.chain
                if b.payload.get("type") == payload_type]

    # ── Chain Info ────────────────────────────────────────────────

    @property
    def length(self):
        return len(self.chain)

    @property
    def last_block(self):
        return self.chain[-1].to_dict() if self.chain else None

    def get_info(self):
        """Chain summary."""
        return {
            "length": self.length,
            "genesis": self.GENESIS_HASH,
            "last_block": self.last_block,
            "merkle_root": self.merkle.root_hex,
            "merkle_size": self.merkle.size,
            "consensus": self.consensus,
            "validator_id": self.validator_id,
        }

    def get_all_blocks(self, limit=100, offset=0):
        """Return blocks with pagination."""
        blocks = self.chain[offset:offset + limit]
        return {
            "total": self.length,
            "offset": offset,
            "limit": limit,
            "blocks": [b.to_dict() for b in blocks],
        }

    # ── Persistence ───────────────────────────────────────────────

    def _save(self):
        """Persist the chain to disk."""
        data = {
            "updated": datetime.utcnow().isoformat(),
            "length": self.length,
            "consensus": self.consensus,
            "merkle_root": self.merkle.root_hex,
            "blocks": [b.to_dict() for b in self.chain],
        }
        with open(self.data_dir / "chain.json", "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Load existing chain from disk."""
        chain_file = self.data_dir / "chain.json"
        if chain_file.exists():
            try:
                with open(chain_file) as f:
                    data = json.load(f)
                # Rebuild chain from stored blocks
                for block_data in data.get("blocks", []):
                    block = SpinaBlock(
                        block_data["prev_hash"],
                        block_data["payload"],
                        block_data.get("validator"),
                    )
                    block.block_hash = block_data["hash"]
                    block.signature = block_data.get("signature")
                    block.timestamp = datetime.fromisoformat(block_data["timestamp"])
                    self.chain.append(block)
                    self.merkle.add(block.block_hash.encode())
            except Exception as e:
                print(f"[SPINA] Could not load chain: {e}")


# ─── SPINA API ──────────────────────────────────────────────────────

class SpinaAPI:
    """REST API wrapper for the SPINA chain."""

    def __init__(self, chain):
        self.chain = chain

    def start(self, host="0.0.0.0", port=5194):
        """Start the SPINA REST API server."""
        if not HAS_FLASK:
            raise ImportError("flask required. Install: pip install flask")

        app = Flask(__name__)
        chain = self.chain

        @app.route("/info")
        def api_info():
            return jsonify(chain.get_info())

        @app.route("/blocks")
        def api_blocks():
            limit = request.args.get("limit", 100, type=int)
            offset = request.args.get("offset", 0, type=int)
            return jsonify(chain.get_all_blocks(limit, offset))

        @app.route("/blocks/<block_hash>")
        def api_block(block_hash):
            block = chain.get_block(block_hash)
            if block:
                return jsonify(block)
            return jsonify({"error": "Block not found"}), 404

        @app.route("/blocks", methods=["POST"])
        def api_add():
            data = request.get_json(force=True)
            block = chain.add_block(data)
            return jsonify(block.to_dict()), 201

        @app.route("/search")
        def api_search():
            q = request.args.get("q", "")
            results = chain.search(q)
            return jsonify({"query": q, "results": results})

        @app.route("/verify/<block_hash>")
        def api_verify(block_hash):
            ok = chain.verify_block(block_hash)
            return jsonify({"block_hash": block_hash, "verified": ok})

        @app.route("/merkle")
        def api_merkle():
            return jsonify(chain.merkle.to_dict())

        @app.route("/health")
        def api_health():
            return jsonify({
                "status": "ok",
                "chain_length": chain.length,
                "merkle_root": chain.merkle.root_hex,
            })

        def _run():
            app.run(host=host, port=port, debug=False, use_reloader=False)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return True


# ─── Singleton ──────────────────────────────────────────────────────

_chain = None

def get_chain():
    global _chain
    if _chain is None:
        _chain = SpinaChain()
    return _chain
