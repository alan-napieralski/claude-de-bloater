---
name: debloat-verify
description: Empirically measures the token-budget impact of a proposed Claude Code configuration change (a CLAUDE.md edit, moving content to a path-scoped rule, etc.) using the free /context breakdown and, optionally, real usage.input_tokens from a canary prompt. Builds baseline and candidate copies (a git worktree when the target is a git repo, a plain directory copy otherwise), applies the candidate change there, and reports a before/after delta, never touching the live project. Use when a specific change needs measured proof rather than a heuristic estimate, typically after debloat-scan or debloat-file has proposed something.
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
2. Build a baseline and a candidate copy under a temp path, never the live project tree:
   - **If the target is a git repo** (`git -C <target> rev-parse --is-inside-work-tree` succeeds): use a worktree for each, `git -C <target> worktree add --detach <baseline-dir> HEAD` and the same for `<candidate-dir>`. `--detach` avoids creating a new branch. This checks out only tracked files, respecting `.gitignore` automatically, so `node_modules`/build output are never dragged along unless already tracked, and gives the workflow canary real source files to act on (needed to test whether a path-scoped rule's glob actually matches anything real).
   - **If it isn't a git repo**: fall back to a plain recursive copy of the whole directory, excluding common heavy/irrelevant directories (`node_modules`, `.git`, `dist`, `build`, `.next`, `vendor`) if present.
3. Apply the proposed change to the candidate copy only. Leave the baseline untouched.
4. `--mode both`'s default matrix (`one-shot,brief,workflow`) only exercises the *always-loaded*
   surface, since its canary prompts are generic and never name a specific skill or command. If the
   change under test touches something on-demand (a skill body, a path-scoped rule, a slash command),
   generate a `manual-context-invoke` canary that forces all of it to load, for each side separately,
   as its own cell kept separate from the always-loaded matrix rather than merged into it:
   ```bash
   python3 scripts/gen_manual_context_invoke.py <baseline-dir> /tmp/debloat-canary-baseline
   python3 scripts/gen_manual_context_invoke.py <candidate-dir> /tmp/debloat-canary-candidate
   ```
   Each prints `manual-context-invoke` to stdout (or an empty string if the target has no on-demand
   `.md` content) — append it to `--matrix` below. This only ever reads the discovered files, it
   never invokes a skill or runs a command, precisely so the number reflects what would load, not the
   cost of whatever that content goes on to do — and it is a forced, manual load, not a test of
   whether Claude would ever organically choose to invoke a given skill on its own. See
   [references/manual-context-invoke.md](references/manual-context-invoke.md) for what gets
   discovered, why agents are excluded, and why an earlier invoke-based version of this had to be
   replaced.
5. Run the harness against each, adding the generated cell from step 4 (if any) to `--matrix` and
   pointing `--canary-dir` at that side's generated directory:
   ```bash
   scripts/run_harness.sh --target <baseline-dir> --config baseline --mode both \
     --matrix one-shot,brief,workflow,manual-context-invoke --canary-dir /tmp/debloat-canary-baseline \
     --out /tmp/debloat-baseline.json
   scripts/run_harness.sh --target <candidate-dir> --config candidate --mode both \
     --matrix one-shot,brief,workflow,manual-context-invoke --canary-dir /tmp/debloat-canary-candidate \
     --out /tmp/debloat-candidate.json
   ```
   Skip `--matrix`/`--canary-dir` entirely for a plain always-loaded-only comparison. Use
   `--mode context-only` instead of `both` if step 1 (auth check) found real-turn unavailable.
6. Compare: `python3 scripts/aggregate.py /tmp/debloat-baseline.json /tmp/debloat-candidate.json`
7. Clean up: `git -C <target> worktree remove <dir>` for each worktree (or `rm -rf` for a plain copy). Removing a worktree only detaches it, it never touches the target's actual branches or history.

See [references/isolation.md](references/isolation.md) for the full worktree-vs-plain-copy reasoning, and why `--setting-sources project` is used for measurement isolation regardless of which one built the copy.

## Boundaries

Only ever writes inside the baseline/candidate copies created in step 2, never the live project. A worktree add/remove only affects the copy it created, never the target's actual branches, HEAD, or history. If asked to also apply the change for real once it's proven to help, that's a separate step, this skill measures, it doesn't commit to anything.

`gen_manual_context_invoke.py` only ever reads discovered files, it never invokes a skill or runs a command — an earlier version did, and invoking a build-oriented command cold measured over 1M cumulative tokens and $0.54 in a single cell, confirmed directly, because invoking something hands Claude instructions to act on rather than just loading its size. Read is the only mechanism used now, so this risk no longer applies; see [references/manual-context-invoke.md](references/manual-context-invoke.md) for the full story.
