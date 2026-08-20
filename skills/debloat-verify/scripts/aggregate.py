#!/usr/bin/env python3
"""Diffs two run_harness.sh JSON reports (baseline vs candidate) and prints a plain summary."""

import json
import sys


def fmt_delta(before, after):
    if before is None or after is None:
        return "n/a"
    delta = after - before
    pct = (delta / before * 100) if before else 0
    sign = "+" if delta >= 0 else ""
    return f"{before} -> {after} ({sign}{delta}, {sign}{pct:.1f}%)"


def main():
    if len(sys.argv) != 3:
        print("Usage: aggregate.py <baseline_report.json> <candidate_report.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        baseline = json.load(f)
    with open(sys.argv[2]) as f:
        candidate = json.load(f)

    print(f"Comparing '{baseline.get('config', 'baseline')}' vs '{candidate.get('config', 'candidate')}'\n")

    b_ctx = baseline.get("context_probe", {})
    c_ctx = candidate.get("context_probe", {})
    if b_ctx or c_ctx:
        print("## /context (free)")
        print(f"Total tokens: {fmt_delta(b_ctx.get('total_tokens'), c_ctx.get('total_tokens'))}")
        all_categories = set(b_ctx.get("categories", {})) | set(c_ctx.get("categories", {}))
        for cat in sorted(all_categories):
            b_val = b_ctx.get("categories", {}).get(cat, {}).get("tokens")
            c_val = c_ctx.get("categories", {}).get(cat, {}).get("tokens")
            if b_val != c_val:
                print(f"  {cat}: {fmt_delta(b_val, c_val)}")
        print()

    b_rt = baseline.get("real_turn", {})
    c_rt = candidate.get("real_turn", {})
    if b_rt or c_rt:
        print("## Real turn (usage.input_tokens + cache_creation + cache_read)")
        for cell in sorted(set(b_rt) | set(c_rt)):
            b_cell = b_rt.get(cell, {})
            c_cell = c_rt.get(cell, {})
            if b_cell.get("status") != "OK" or c_cell.get("status") != "OK":
                print(f"  {cell}: baseline={b_cell.get('status', 'not run')}, candidate={c_cell.get('status', 'not run')}")
                continue
            print(f"  {cell}: {fmt_delta(b_cell.get('total_tokens_mean'), c_cell.get('total_tokens_mean'))}")
        b_cost = sum(c.get("total_cost_usd_sum", 0) for c in b_rt.values() if c.get("status") == "OK")
        c_cost = sum(c.get("total_cost_usd_sum", 0) for c in c_rt.values() if c.get("status") == "OK")
        print(f"  (measurement cost: baseline ${b_cost:.4f}, candidate ${c_cost:.4f})")


if __name__ == "__main__":
    main()
