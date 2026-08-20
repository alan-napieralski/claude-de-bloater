# Isolation recipe

Two separate concerns, easy to conflate: keeping the *operator's personal config* out of the numbers (below), and keeping the *baseline/candidate copies* isolated from the live project (see "Building the copies" further down). Both matter, neither implies the other.

## Keeping the operator's personal config out of the numbers

Two things were tried, only one works.

**Does not work: `--bare --add-dir <target>`.** Confirmed directly: `--bare` suppresses everything, including the target project's own skills, agents, and CLAUDE.md, not just the operator's personal config. It reports a flat `0/200k` with no breakdown at all. Not viable.

**Works: `--setting-sources project` alone, no `--bare`.** Confirmed directly against a scratch project with a deliberate project-level skill, agent, and CLAUDE.md, run alongside the operator's normal global config. It correctly excluded every one of the operator's personal user-level agents and roughly forty personal user-level skills, while keeping the target's own project-scoped skill, agent, and a proportionally-sized CLAUDE.md (1,400 words showed as 2.4k tokens). This is what `run_harness.sh` uses.

**A handful of "undefined"-source skills still show up regardless of `--setting-sources`.** These are Claude Code's own built-in skills, present on any installation. Not contamination, not something to filter out, they're a constant baseline every measurement shares.

## Building the baseline/candidate copies: worktree, not a Claude-config-only scratch copy

The original design here copied only the Claude-config surface (`CLAUDE.md`, `.claude/**`, `@`-imported files) into a scratch directory, deliberately excluding the rest of the project. That has a real gap: it can't prove whether a path-scoped rule's `paths:` glob actually matches anything, because there's no real source tree to match against, and it can't support a workflow canary that reads or edits real files.

**Default: a git worktree of the whole target**, `git worktree add --detach <dir> HEAD`, for both baseline and candidate. `--detach` means no new branch is created. This is preferred over a plain `cp -R` of the whole project for a concrete, practical reason: a worktree checks out only git-*tracked* files, respecting `.gitignore` automatically, so `node_modules`, build output, and other generated cruft never get dragged along unless something has gone wrong and they're actually tracked. A naive recursive copy has no such awareness and would need every project's exclude patterns hand-rolled and kept in sync, fragile across different projects' conventions. Removing a worktree (`git worktree remove <dir>`) only detaches that working copy, it never touches the target's real branches, HEAD, or reflog.

**Fallback: a plain recursive copy**, only when the target isn't a git repo at all. Exclude the same common heavy directories (`node_modules`, `.git`, `dist`, `build`, `.next`, `vendor`) if present, since there's no `.gitignore`-driven checkout to do it automatically here.

**Worktrees are not needed for running multiple test fixtures in parallel.** Each fixture under `tests/fixtures/` is already its own independent directory, not a different state of the same repository, so parallel test runs just operate on separate paths. Worktrees solve a different problem: two checkouts of *one* repo's history side by side. Reach for them only when actually measuring a real target project's baseline vs. candidate state.

## A separate gotcha: reading this plugin's own bundled files

This only applies when actually *running* `debloat-scan`/`debloat-file` (not the measurement harness itself, which never invokes them). When the plugin is loaded ad hoc via `--plugin-dir <path>` for testing rather than properly installed, Claude Code's file-access sandbox for a `-p` session defaults to just the working directory. A skill's own bundled `references/checks.md` sits outside that boundary (in the plugin's install location, not the target project's directory) and reads get denied, confirmed directly: the skill ran without ever loading its checklist until `--add-dir <plugin-install-path>` was added alongside `--plugin-dir`. If testing this plugin via `--plugin-dir`, always also pass `--add-dir` pointing at the same path. A properly installed plugin (through a marketplace) may not need this, not independently verified.
