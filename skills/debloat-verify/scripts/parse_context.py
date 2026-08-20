#!/usr/bin/env python3
"""Parses raw claude -p JSON output into a structured debloat-verify report."""

import json
import re
import statistics
import sys
from pathlib import Path

AUTH_ERROR_MARKER = "OAuth access token has expired"


def parse_context_probe(raw_text):
    try:
        envelope = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "could not parse claude -p output as JSON", "raw": raw_text[:500]}

    if envelope.get("is_error"):
        result = envelope.get("result", "")
        if AUTH_ERROR_MARKER in result:
            return {"error": "auth"}
        return {"error": result[:500]}

    result = envelope.get("result", "")
    total_match = re.search(r"\*\*Tokens:\*\*\s*([\d.]+)k?\s*/\s*200k\s*\(([\d.]+)%\)", result)
    total_tokens = None
    if total_match:
        raw_num = total_match.group(1)
        total_tokens = int(float(raw_num) * 1000) if "k" in total_match.group(0) else int(float(raw_num))

    categories = {}
    for line in result.splitlines():
        m = re.match(r"\|\s*([A-Za-z][A-Za-z \(\)/]+?)\s*\|\s*([\d.]+)k?\s*\|\s*([\d.]+)%\s*\|", line)
        if m:
            name, tokens_raw, pct = m.groups()
            tokens = float(tokens_raw)
            if "k" in m.group(0).split("|")[2]:
                tokens *= 1000
            categories[name.strip()] = {"tokens": int(tokens), "percentage": float(pct)}

    return {"total_tokens": total_tokens, "categories": categories, "cli_version_note": "parsed from markdown, verify shape if this comes back empty on a future CLI version"}


def parse_real_turn(raw_text):
    try:
        envelope = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "could not parse claude -p output as JSON", "raw": raw_text[:500]}

    if envelope.get("is_error"):
        result = envelope.get("result", "")
        if AUTH_ERROR_MARKER in result:
            return {"error": "auth"}
        return {"error": result[:500]}

    usage = envelope.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    cache_creation = usage.get("cache_creation_input_tokens", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    total_tokens = input_tokens + cache_creation + cache_read

    model_usage = envelope.get("modelUsage", {})
    total_cost = sum(m.get("costUSD", 0) for m in model_usage.values())
    if not total_cost:
        total_cost = envelope.get("total_cost_usd", 0)

    return {
        "total_tokens": total_tokens,
        "input_tokens": input_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "total_cost_usd": round(total_cost, 6),
    }


def main():
    if len(sys.argv) not in (5, 6):
        print("Usage: parse_context.py <raw_dir> <config_label> <mode> <out_path> [auth_available]", file=sys.stderr)
        sys.exit(1)

    raw_dir, config_label, mode, out_path = sys.argv[1:5]
    auth_available = sys.argv[5] == "1" if len(sys.argv) == 6 else None
    raw_dir = Path(raw_dir)
    report = {"config": config_label, "mode": mode}
    if auth_available is not None:
        report["auth_available"] = auth_available
        if not auth_available:
            report["warning"] = (
                "CLAUDE_CODE_OAUTH_TOKEN was not set for this run. Memory Files and Custom Agents "
                "figures below will read as 0 regardless of their real size, confirmed directly, "
                "not a display quirk. Do not trust this report's Memory Files numbers, re-run after "
                "'claude setup-token' (see references/degraded-mode.md)."
            )

    context_file = raw_dir / "context.json"
    if context_file.exists():
        report["context_probe"] = parse_context_probe(context_file.read_text())

    real_turn = {}
    for f in sorted(raw_dir.glob("realturn_*.json")):
        m = re.match(r"realturn_(.+)_(\d+)\.json", f.name)
        if not m:
            continue
        cell, repeat_num = m.group(1), int(m.group(2))
        parsed = parse_real_turn(f.read_text())
        real_turn.setdefault(cell, []).append(parsed)

    if real_turn:
        report["real_turn"] = {}
        for cell, repeats in real_turn.items():
            ok = [r for r in repeats if "error" not in r]
            errors = [r for r in repeats if "error" in r]
            entry = {"repeats_run": len(repeats), "repeats_ok": len(ok)}
            if errors and not ok:
                entry["status"] = "SKIPPED (auth)" if any(r.get("error") == "auth" for r in errors) else "FAILED"
                entry["error"] = errors[0].get("error")
            elif ok:
                totals = [r["total_tokens"] for r in ok]
                entry["status"] = "OK"
                entry["total_tokens_mean"] = round(statistics.mean(totals), 1)
                entry["total_tokens_stdev"] = round(statistics.stdev(totals), 1) if len(totals) > 1 else 0.0
                entry["total_cost_usd_sum"] = round(sum(r["total_cost_usd"] for r in ok), 6)
            report["real_turn"][cell] = entry

    Path(out_path).write_text(json.dumps(report, indent=2)) if out_path != "/dev/stdout" else print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
