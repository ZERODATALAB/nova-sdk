#!/usr/bin/env python3
"""
NOVA SDK — End-to-End Demo: Passive Scan → Discover → Alert → SPINA Block
==========================================================================

This script demonstrates the complete NOVA workflow:
  1. Start passive network discovery for 30 seconds
  2. Print all discovered organs and their synapses
  3. Run the Cytokine immune check and display active alerts
  4. Add a threat signature block to the SPINA chain
  5. Verify the block with a Merkle proof

Requirements:
  - Root privileges (or CAP_NET_RAW) for packet capture
  - pip install nova-sdk (or pip install -e . from repo root)
  - Optional: pip install scapy cryptography networkx

Usage:
  sudo python examples/demo_scan.py
  sudo python examples/demo_scan.py --duration 60
  sudo python examples/demo_scan.py --interface eth0 --duration 120

The script handles missing dependencies gracefully and provides
clear error messages with installation instructions.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path


# ─── Dependency Checks ────────────────────────────────────────────────

def check_dependencies():
    """Check that all required and optional dependencies are available.

    Returns:
        dict: Status of each dependency with 'available' and 'message' keys.
    """
    deps = {}

    # Core dependency: the SDK itself
    try:
        from nova_synapse.engine import SynapseEngine, get_engine
        deps["nova-sdk"] = {"available": True, "message": "OK"}
    except ImportError:
        deps["nova-sdk"] = {
            "available": False,
            "message": "Install: pip install nova-sdk  (or: pip install -e . from repo root)",
        }

    # scapy — needed for packet capture
    try:
        import scapy  # noqa: F401
        deps["scapy"] = {"available": True, "message": "OK"}
    except ImportError:
        deps["scapy"] = {"available": False, "message": "Install: pip install scapy"}

    # cryptography — needed for Ed25519 signatures in SPINA
    try:
        import cryptography  # noqa: F401
        deps["cryptography"] = {"available": True, "message": "OK"}
    except ImportError:
        deps["cryptography"] = {
            "available": False,
            "message": "Install: pip install cryptography (SPINA will use demo signatures without it)",
        }

    # networkx — needed for topology graph export
    try:
        import networkx  # noqa: F401
        deps["networkx"] = {"available": True, "message": "OK"}
    except ImportError:
        deps["networkx"] = {
            "available": False,
            "message": "Install: pip install networkx (graph features will be limited)",
        }

    return deps


def print_dependency_status(deps):
    """Print a friendly dependency status table."""
    print("=" * 60)
    print("  DEPENDENCY CHECK")
    print("=" * 60)
    all_ok = True
    for name, info in deps.items():
        icon = "[OK]" if info["available"] else "[!] "
        print(f"  {icon} {name:<20s} {info['message']}")
        if not info["available"] and name == "nova-sdk":
            all_ok = False
    print("=" * 60)
    print()
    return all_ok


# ─── Main Demo ────────────────────────────────────────────────────────

def run_demo(interface=None, duration=30, data_dir="/tmp/nova-demo"):
    """Run the complete NOVA demo workflow.

    Args:
        interface: Network interface name (e.g., 'eth0'). None for auto-detect.
        duration: Passive capture duration in seconds.
        data_dir: Directory for temporary engine/chain data.
    """
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  NOVA SDK — End-to-End Demo".center(58) + "║")
    print("║" + "  Digital Organism: Scan → Discover → Alert → Remember".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print(f"  Interface: {interface or 'auto-detect'}")
    print(f"  Duration:  {duration} seconds")
    print(f"  Data dir:  {data_dir}")
    print()

    # ── Step 1: Import engines ────────────────────────────────────
    print("─" * 60)
    print("  STEP 1: Initializing NOVA engines...")
    print("─" * 60)

    try:
        from nova_synapse.engine import SynapseEngine, get_engine
        from nova_cytokine.engine import CytokineEngine, Alert, Severity
        from nova_spina.chain import SpinaChain, get_chain

        # Override data directories to avoid polluting /opt/nova
        engine = SynapseEngine(data_dir=f"{data_dir}/synapse")
        chain = SpinaChain(data_dir=f"{data_dir}/spina")

        print("  [OK] Synapse Engine   — initialized")
        print("  [OK] SPINA Chain      — initialized")
        print("  [OK] Cytokine Engine  — ready (will connect after scan)")
        print()
    except Exception as e:
        print(f"  [KO] Engine initialization failed: {e}")
        print()
        print("  Make sure you've installed the SDK:")
        print("    pip install -e /opt/nova-sdk")
        sys.exit(1)

    # ── Step 2: Start passive scan ────────────────────────────────
    print("─" * 60)
    print(f"  STEP 2: Passive network discovery ({duration}s)...")
    print("─" * 60)
    print("  [SCAN] Listening passively — ZERO packets emitted.")
    print("  [NET] Detecting organs and forming synapses...")
    print()

    try:
        engine.start_passive(interface=interface, duration=duration)

        # Show a simple progress indicator
        start_time = time.time()
        while time.time() - start_time < duration and engine.running:
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            bar_len = 30
            filled = int(bar_len * elapsed / duration)
            bar = "█" * filled + "░" * (bar_len - filled)
            stats = engine.get_stats()
            print(
                f"\r  [{bar}] {elapsed:3d}s / {duration}s  "
                f"|  Organs: {len(engine.organs):3d}  "
                f"|  Synapses: {len(engine.synapses):3d}  "
                f"|  Packets: {stats['packets_seen']:6d}",
                end="",
                flush=True,
            )
            time.sleep(0.5)

        # Wait for sniff thread to finish
        time.sleep(1)
        print()
        print()
        print(f"  [OK] Scan complete!")
        print()
    except PermissionError:
        print()
        print("  [KO] Permission denied!")
        print()
        print("  Packet capture requires root privileges. Run with sudo:")
        print("    sudo python examples/demo_scan.py")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"  [KO] Scan failed: {e}")
        print()
        print("  Troubleshooting:")
        print("    - Try specifying an interface: --interface eth0")
        print("    - Make sure scapy is installed: pip install scapy")
        print("    - Check: sudo setcap cap_net_raw=eip $(which python3)")
        sys.exit(1)

    # ── Step 3: Print discovered organs ───────────────────────────
    print("─" * 60)
    print("  STEP 3: Discovered Organs")
    print("─" * 60)

    if not engine.organs:
        print("  [!]  No organs discovered.")
        print()
        print("  This can happen if:")
        print("    - The network is very quiet (try a longer duration)")
        print("    - The interface is wrong (try --interface eth0)")
        print("    - You're on an isolated VM with no traffic")
        print()
        print("  Continuing with remaining steps anyway...")
        print()
    else:
        print(f"  {'IP':<16s} {'MAC':<18s} {'Hostname':<20s} {'DNA':<18s}")
        print(f"  {'─'*16} {'─'*18} {'─'*20} {'─'*18}")
        for organ in engine.organs.values():
            d = organ.to_dict()
            print(
                f"  {d['ip']:<16s} "
                f"{d['mac']:<18s} "
                f"{(d['hostname'] or '(none)'):<20s} "
                f"{d['dna']:<18s}"
            )
        print()
        print(f"  Total organs:    {len(engine.organs)}")
        print(f"  Total synapses:  {len(engine.synapses)}")
        print()

    # ── Step 4: Print synapses ─────────────────────────────────────
    if engine.synapses:
        print("─" * 60)
        print("  STEP 4: Formed Synapses")
        print("─" * 60)
        print(f"  {'Source':<16s} {'→ Dest':<16s} {'Proto':<6s} {'Port':<6s} {'Weight':<8s} {'Volume':<10s}")
        print(f"  {'─'*16} {'─'*16} {'─'*6} {'─'*6} {'─'*8} {'─'*10}")
        for syn in engine.synapses.values():
            d = syn.to_dict()
            port_str = str(d["port"]) if d["port"] else "-"
            print(
                f"  {d['a']:<16s} "
                f"→ {d['b']:<15s} "
                f"{d['protocol']:<6s} "
                f"{port_str:<6s} "
                f"{d['weight']:<8.2f} "
                f"{d['volume_bytes']:<10d}"
            )
        print()

    # ── Step 5: Show engine stats ──────────────────────────────────
    print("─" * 60)
    print("  STEP 5: Synapse Engine Statistics")
    print("─" * 60)
    stats = engine.get_stats()
    print(f"  Packets processed:  {stats['packets_seen']:>8d}")
    print(f"  Organs discovered:  {stats['organs_discovered']:>8d}")
    print(f"  Synapses formed:    {stats['synapses_formed']:>8d}")
    print(f"  Uptime:             {stats['uptime_seconds']:>8.0f}s")
    print(f"  Baseline ready:     {'[OK] Yes' if engine.baseline_ready else '⏳ No (requires 7 days)'}")
    print()

    # ── Step 6: Run Cytokine immune check ─────────────────────────
    print("─" * 60)
    print("  STEP 6: Immune System Check (Cytokine)")
    print("─" * 60)

    active_alerts = []  # Initialize in case try block fails
    try:
        cyto = CytokineEngine(engine)
        new_alerts = cyto.check()
        active_alerts = cyto.get_active()

        if active_alerts:
            severity_icons = {
                "info": "ℹ ",
                "low": "[LOW]",
                "medium": "[MED]",
                "high": "[HIGH]",
                "critical": "[CRIT]",
            }
            print(f"  Active Alerts: {len(active_alerts)}")
            print()
            for alert in active_alerts:
                icon = severity_icons.get(alert["severity"], "[!] ")
                print(f"  {icon} [{alert['severity'].upper():<8s}] {alert['message']}")
                if alert.get("organ_ip"):
                    print(f"     Organ: {alert['organ_ip']} ({alert.get('organ_mac', '?')})")
                print(f"     Rule:  {alert['rule']}")
                print(f"     Time:  {alert['timestamp'][:19]}")
                if alert.get("evidence"):
                    print(f"     Evidence: {json.dumps(alert['evidence'])}")
                print()
        else:
            print("  [OK] No active alerts — infrastructure appears healthy.")
            print()
            print("  Note: This is expected during short demo scans.")
            print("  Alerts become more meaningful with a baseline (7 days).")
            print()

        # Show rule statistics
        rules = cyto.rules_fired
        if rules:
            print(f"  Rules Fired This Session:")
            for rule, count in rules.items():
                print(f"    • {rule}: {count}")
            print()

    except Exception as e:
        print(f"  [KO] Immune check failed: {e}")
        print()

    # ── Step 7: Add a block to SPINA ──────────────────────────────
    print("─" * 60)
    print("  STEP 7: SPINA — Writing to Immune Memory")
    print("─" * 60)

    try:
        # Build a threat signature payload from any active alerts
        if active_alerts:
            # Use the first CRITICAL or HIGH alert as a threat signature
            threat_alert = None
            for a in active_alerts:
                if a["severity"] in ("critical", "high"):
                    threat_alert = a
                    break
            if not threat_alert:
                threat_alert = active_alerts[0]

            payload = {
                "type": "threat_signature",
                "source": "demo_scan.py",
                "alert_id": threat_alert["id"],
                "rule": threat_alert["rule"],
                "severity": threat_alert["severity"],
                "organ_ip": threat_alert.get("organ_ip"),
                "behaviors": [threat_alert["rule"]],
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            # Demo payload when no alerts are present
            payload = {
                "type": "threat_signature",
                "source": "demo_scan.py",
                "malware": "demo_ransomware_sample",
                "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "behaviors": ["c2_beacon", "lateral_scan", "credential_dump"],
                "severity": "critical",
                "timestamp": datetime.utcnow().isoformat(),
            }

        block = chain.add_block(payload)
        print(f"  [OK] Block added to SPINA chain!")
        print(f"     Block hash:  {block.block_hash[:32]}...")
        print(f"     Type:        {payload['type']}")
        print(f"     Chain length: {chain.length}")
        print()

        # Show chain info
        info = chain.get_info()
        print(f"  SPINA Chain Summary:")
        print(f"     Total blocks:   {info['length']}")
        print(f"     Merkle root:    {info['merkle_root'][:32]}...")
        print(f"     Consensus:      {info['consensus']}")
        print()

        # Verify the block we just added
        verified = chain.verify_block(block.block_hash)
        if verified:
            print(f"  [OK] Merkle proof verified — block integrity confirmed (O(log n)).")
        else:
            print(f"  [KO] Merkle proof FAILED — possible tampering detected!")
        print()

    except Exception as e:
        print(f"  [KO] SPINA block creation failed: {e}")
        print()

    # ── Step 8: Show final summary ────────────────────────────────
    print("╔" + "═" * 58 + "╗")
    print("║" + "  DEMO COMPLETE".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Organs discovered:     {len(engine.organs):<25d} ║")
    print(f"║  Synapses formed:       {len(engine.synapses):<25d} ║")
    print(f"║  Active alerts:         {len(active_alerts) if 'active_alerts' in dir() else 0:<25d} ║")
    print(f"║  SPINA blocks:          {chain.length:<25d} ║")
    print("╠" + "═" * 58 + "╣")
    print("║  Next Steps:                                          ║")
    print("║    nova dashboard           — Molecular Cockpit       ║")
    print("║    nova status -v           — Full topology           ║")
    print("║    nova alerts              — Active immune alerts    ║")
    print("║    nova spina info          — Chain status            ║")
    print("║    nova spina search <q>    — Search threat memory    ║")
    print("╚" + "═" * 58 + "╝")
    print()

    # ── Bonus: Save results ───────────────────────────────────────
    results_file = Path(data_dir) / "demo_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    results = {
        "demo_timestamp": datetime.utcnow().isoformat(),
        "duration_seconds": duration,
        "synapse": {
            "organ_count": len(engine.organs),
            "synapse_count": len(engine.synapses),
            "organs": [o.to_dict() for o in engine.organs.values()],
            "synapses": [s.to_dict() for s in engine.synapses.values()],
            "stats": engine.get_stats(),
        },
        "spina": {
            "chain_length": chain.length,
            "info": chain.get_info(),
        },
    }

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"  [FILE] Full results saved to: {results_file}")
    print()


# ─── Entry Point ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="NOVA SDK — End-to-End Demo: Scan → Discover → Alert → Remember",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python demo_scan.py
  sudo python demo_scan.py --duration 60
  sudo python demo_scan.py --interface eth0 --duration 120
  sudo python demo_scan.py --data-dir /var/lib/nova-demo
        """,
    )
    parser.add_argument(
        "-i", "--interface",
        help="Network interface to capture on (e.g., eth0, enp0s3). Auto-detect if not specified.",
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=30,
        help="Passive capture duration in seconds (default: 30).",
    )
    parser.add_argument(
        "--data-dir",
        default="/tmp/nova-demo",
        help="Directory for temporary engine/chain data (default: /tmp/nova-demo).",
    )

    args = parser.parse_args()

    # Check dependencies first
    deps = check_dependencies()
    core_ok = print_dependency_status(deps)

    if not core_ok:
        print("  [KO] Core dependency 'nova-sdk' is not installed.")
        print()
        print("  Install it with one of:")
        print("    pip install nova-sdk")
        print("    pip install -e /opt/nova-sdk")
        sys.exit(1)

    if not deps["scapy"]["available"]:
        print("  [!]  scapy is required for packet capture but not installed.")
        print("  Install: pip install scapy")
        print()
        response = input("  Continue anyway? (will fail at scan step) [y/N]: ")
        if response.lower() != "y":
            sys.exit(0)
        print()

    # Run the demo
    try:
        run_demo(
            interface=args.interface,
            duration=args.duration,
            data_dir=args.data_dir,
        )
    except KeyboardInterrupt:
        print()
        print("  [!]  Demo interrupted by user.")
        print()
        sys.exit(0)
    except Exception as e:
        print()
        print(f"  [KO] Unexpected error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
