#!/usr/bin/env python3
"""
NOVA CLI — Digital Organism Command Line Interface.

Usage:
    nova scan              Start passive network discovery
    nova status            Show current topology and stats
    nova dashboard         Start web dashboard (port :8080)
    nova spina add ...     Add a block to SPINA
    nova spina search ...  Search SPINA chain
    nova alerts            Show active immune alerts
"""

import argparse
import sys
import json
import time
from pathlib import Path

from nova_synapse.engine import SynapseEngine, get_engine
from nova_cytokine.engine import CytokineEngine, AnesthesiaSandbox
from nova_spina.chain import SpinaChain, get_chain


def cmd_scan(args):
    """Start passive network discovery."""
    engine = get_engine()
    print("[NOVA] [NOVA] Synapse Engine starting...")
    print("[NOVA] Passive network discovery — zero packets emitted.")
    print(f"[NOVA] Interface: {args.interface or 'auto-detect'}")
    print(f"[NOVA] Duration: {args.duration or 'indefinite (Ctrl+C to stop)'}")
    print()

    try:
        engine.start_passive(interface=args.interface, duration=args.duration)

        if args.duration:
            time.sleep(args.duration + 2)
        else:
            # Wait for Ctrl+C
            while engine.running:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n[NOVA] Stopping...")
        engine.stop()

    # Show results
    stats = engine.get_stats()
    print(f"\n[NOVA] Scan complete.")
    print(f"  Organs discovered: {len(engine.organs)}")
    print(f"  Synapses formed:   {len(engine.synapses)}")
    print(f"  Packets seen:      {stats['packets_seen']}")
    print(f"  Baseline ready:    {engine.is_baseline_ready()}")


def cmd_status(args):
    """Show current topology."""
    engine = get_engine()
    stats = engine.get_stats()

    print("[NOVA] [NOVA] Infrastructure Status")
    print(f"  Uptime:      {stats['uptime_seconds']:.0f}s")
    print(f"  Organs:      {len(engine.organs)}")
    print(f"  Synapses:    {len(engine.synapses)}")
    print(f"  Baseline:    {'[OK] ready' if engine.baseline_ready else '⏳ observing...'}")
    print()

    if args.verbose:
        print("ORGANS:")
        for organ in engine.organs.values():
            d = organ.to_dict()
            print(f"  {d['ip']:15s} {d['mac']:17s} {d['hostname'] or '(no hostname)':20s} dna={d['dna']}")

        print("\nSYNAPSES (last 20):")
        syns = list(engine.synapses.values())
        for syn in syns[-20:]:
            print(f"  {syn.a.ip} → {syn.b.ip}  {syn.protocol:5s}  port={syn.port or '-':5s}  w={syn.weight:.2f}")


def cmd_dashboard(args):
    """Start the web dashboard."""
    from nova_cockpit.dashboard import start_dashboard
    print(f"[NOVA] [NOVA] Cockpit starting on http://localhost:{args.port}")
    start_dashboard(port=args.port)


def cmd_spina(args):
    """SPINA blockchain operations."""
    chain = get_chain()

    if args.spina_action == "info":
        info = chain.get_info()
        print(json.dumps(info, indent=2))

    elif args.spina_action == "add":
        payload = {"type": args.type, "data": args.data}
        if args.tags:
            payload["tags"] = args.tags.split(",")
        block = chain.add_block(payload)
        print(f"[SPINA] ∞ Block added: {block.block_hash[:16]}...")

    elif args.spina_action == "search":
        results = chain.search(args.query)
        print(f"[SPINA] Found {len(results)} blocks matching '{args.query}':")
        for r in results[:10]:
            print(f"  {r['hash'][:16]}... {r['payload']['type']}: {r['payload'].get('data', '')[:60]}")

    elif args.spina_action == "verify":
        ok = chain.verify_block(args.block_hash)
        print(f"[SPINA] Block {args.block_hash[:16]}... verified: {ok}")

    elif args.spina_action == "list":
        blocks = chain.get_all_blocks(limit=args.limit)
        print(f"[SPINA] Chain length: {blocks['total']}")
        for b in blocks["blocks"]:
            print(f"  {b['hash'][:16]}... [{b['payload']['type']}] {b['payload'].get('data', '')[:50]}")


def cmd_alerts(args):
    """Show active immune alerts."""
    engine = get_engine()
    cyto = CytokineEngine(engine)
    cyto.check()
    alerts = cyto.get_active()

    print(f"[NOVA] [DEF]  Active Alerts: {len(alerts)}")
    for a in alerts:
        icon = {"info": "ℹ", "low": "[LOW]", "medium": "[MED]", "high": "[HIGH]", "critical": "[CRIT]"}.get(a["severity"], "[!]")
        print(f"  {icon} [{a['severity'].upper()}] {a['message']}")
        if a.get("organ_ip"):
            print(f"     Organ: {a['organ_ip']} ({a.get('organ_mac', '?')})")
        print(f"     {a['timestamp'][:19]}")


def main():
    parser = argparse.ArgumentParser(
        description="NOVA — Digital Organism SDK",
        epilog="0DATA Lab · https://0data.fr"
    )
    sub = parser.add_subparsers(dest="command")

    # nova scan
    p_scan = sub.add_parser("scan", help="Passive network discovery")
    p_scan.add_argument("-i", "--interface", help="Network interface")
    p_scan.add_argument("-d", "--duration", type=int, help="Scan duration (seconds)")

    # nova status
    p_status = sub.add_parser("status", help="Show topology")
    p_status.add_argument("-v", "--verbose", action="store_true", help="Show all organs/synapses")

    # nova dashboard
    p_dash = sub.add_parser("dashboard", help="Web dashboard")
    p_dash.add_argument("-p", "--port", type=int, default=8080, help="Dashboard port (default: 8080)")

    # nova spina
    p_spina = sub.add_parser("spina", help="SPINA blockchain operations")
    p_spina_sub = p_spina.add_subparsers(dest="spina_action")

    p_spina_info = p_spina_sub.add_parser("info", help="Chain info")
    p_spina_add = p_spina_sub.add_parser("add", help="Add a block")
    p_spina_add.add_argument("--type", required=True, help="Block type (threat_signature, anesthesia_report, etc.)")
    p_spina_add.add_argument("--data", required=True, help="Block data")
    p_spina_add.add_argument("--tags", help="Comma-separated tags")
    p_spina_search = p_spina_sub.add_parser("search", help="Search blocks")
    p_spina_search.add_argument("query", help="Search query")
    p_spina_verify = p_spina_sub.add_parser("verify", help="Verify a block")
    p_spina_verify.add_argument("block_hash", help="Block hash to verify")
    p_spina_list = p_spina_sub.add_parser("list", help="List blocks")
    p_spina_list.add_argument("--limit", type=int, default=20, help="Max blocks")

    # nova alerts
    sub.add_parser("alerts", help="Show active immune alerts")

    args = parser.parse_args()

    commands = {
        "scan": cmd_scan,
        "status": cmd_status,
        "dashboard": cmd_dashboard,
        "spina": cmd_spina,
        "alerts": cmd_alerts,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
