---
name: debloat-scan
description: Analyses a project's entire Claude Code context surface, CLAUDE.md and its @-imports, .claude/rules/*.md, .claude/commands/*.md, .claude/agents/*.md, .claude/hooks/, .claude/settings.json, and .claude/skills/, for token-budget problems, content that is always loaded but could be deferred, redundancy across files, and reference-tiering opportunities. Produces a ranked findings report with an estimated always-loaded token total. Use when the user wants a full audit of a project's Claude Code configuration, asks why their context is so full, or wants to reduce always-loaded overhead across the whole repo. Not for grading CLAUDE.md content quality or completeness, use claude-md-improver for that.
allowed-tools: Read Grep Glob
---

# Debloat: whole project

Audits a project's entire Claude Code context surface for token-budget problems. For a single file, use `debloat-file` instead, this skill needs the whole surface to catch cross-file issues.

## Instructions

1. Read [the checks](../../references/checks.md) and [the report format](../../references/report-format.md). Between them they govern every step below: the scope boundary, the read-only constraint, every check and its severity, the token estimate, and the output shape.
2. **Enumerate the surface.** Find the project's `CLAUDE.md` (and any nested `CLAUDE.md`/`CLAUDE.local.md`), walk its `@`-import graph fully (Claude Code resolves imports up to 4 hops deep, so that's the full graph, anything past that never loads), and find `.claude/rules/*.md`, `.claude/commands/*.md`, `.claude/agents/*.md`, `.claude/hooks/`, `.claude/settings.json`, and `.claude/skills/*/SKILL.md`. Also pull in any file that one of the above names as its authoritative spec/procedure/checklist and instructs reading in full (a rules file, agent, or command pointing at a plain `docs/*.md`, for example) — it sits outside this standard list and does not count toward the always-loaded headline, but it is needed in view to check the citing file for restated content instead of a genuine reference.
3. **Read every file found.** This is the step `debloat-file` can't do on a single file, cross-file checks depend on having all of it in view at once.
4. **Apply every check**, including the ones marked "needs the whole surface" that `debloat-file` has to skip. Duplication is the check most likely to be under-run on a single read: follow the "Redundant or duplicated" section literally, including its topic-by-topic second pass and its instruction to check any file that cites another as authoritative against what that file actually says, before concluding the project has none.
5. Estimate each file's token cost, and sum them for the headline where the report format calls for one.
