---
name: debloat-verify
description: Empirically measures the token-budget impact of a proposed Claude Code configuration change (a CLAUDE.md edit, moving content to a path-scoped rule, etc.) using the free /context breakdown and, optionally, real usage.input_tokens from a canary prompt. Copies only the target's Claude-config surface into an isolated scratch directory, applies the candidate change there, and reports a before/after delta, never touching the live project. Use when a specific change needs measured proof rather than a heuristic estimate, typically after debloat-scan or debloat-file has proposed something.
tools: Read, Grep, Glob, Bash, Write
---

# Debloat: verify

Measures whether a proposed change to a project's Claude Code configuration actually reduces its token footprint, using real numbers rather than a heuristic guess.

## First: check auth, every time, every mode

```bash
[ -n "$CLAUDE_CODE_OAUTH_TOKEN" ] && echo "auth available" || echo "auth NOT available"
```

This matters for every mode, not just real-turn: confirmed directly, without a valid token `/context` silently reports Memory Files and Custom Agents as `0` regardless of their real size, even in context-only mode, even though the command itself makes no real API call. `run_harness.sh` checks this itself and stamps every report with `"auth_available"`, but tell the user up front too, before running anything, rather than only in the fine print of a JSON file: if auth isn't available, say plainly that Memory Files numbers won't be trustworthy until `claude setup-token` is run (see [references/degraded-mode.md](references/degraded-mode.md)), and ask whether to proceed anyway (useful for Skills-only findings) or wait.

## Procedure

1. Identify the target project and the specific proposed change (a diff, an edit to apply, a file to move or split).
2. Create two scratch directories under a temp path, copying only the target's Claude-config surface into each, `CLAUDE.md`, `.claude/**`, and anything reachable through an `@`-import, never the whole project. Write only inside these two scratch directories, never the live project tree.
3. Apply the proposed change to the candidate scratch copy only. Leave the baseline copy untouched.
4. Run the harness against each:
   ```bash
   scripts/run_harness.sh --target <baseline-dir> --config baseline --mode both --out /tmp/debloat-baseline.json
   scripts/run_harness.sh --target <candidate-dir> --config candidate --mode both --out /tmp/debloat-candidate.json
   ```
   Use `--mode context-only` instead of `both` if step 1 found real-turn unavailable.
5. Compare: `python3 scripts/aggregate.py /tmp/debloat-baseline.json /tmp/debloat-candidate.json`
6. Delete both scratch directories once done.

See [references/isolation.md](references/isolation.md) for why `--setting-sources project` is used for isolation instead of `--bare`, and why no git worktree is involved.

## Boundaries

Only ever writes inside the two scratch directories created in step 2, hard-coded there, never the live project. If asked to also apply the change for real once it's proven to help, that's a separate step, this skill measures, it doesn't commit to anything.
