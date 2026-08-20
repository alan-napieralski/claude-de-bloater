---
name: debloat-scan
description: Analyses a project's entire Claude Code context surface, CLAUDE.md and its @-imports, .claude/rules/*.md, .claude/commands/*.md, .claude/agents/*.md, .claude/hooks/, .claude/settings.json, and .claude/skills/, for token-budget problems, content that is always loaded but could be deferred, redundancy across files, and reference-tiering opportunities. Produces a ranked findings report with an estimated always-loaded token total. Use when the user wants a full audit of a project's Claude Code configuration, asks why their context is so full, or wants to reduce always-loaded overhead across the whole repo. Not for grading CLAUDE.md content quality or completeness, use claude-md-improver for that.
tools: Read, Grep, Glob, Bash
---

# Debloat: whole project

Audits a project's entire Claude Code context surface for token-budget problems. For a single file, use `debloat-file` instead, this skill needs the whole surface to catch cross-file issues.

Advisory only. Read-only, never edit anything, hand findings back for the user to act on.

## Procedure

1. **Enumerate the surface.** Find the project's `CLAUDE.md` (and any nested `CLAUDE.md`/`CLAUDE.local.md`), walk its `@`-import graph fully (following imports up to the depth Claude Code itself resolves), and find `.claude/rules/*.md`, `.claude/commands/*.md`, `.claude/agents/*.md`, `.claude/hooks/`, `.claude/settings.json`, and `.claude/skills/*/SKILL.md`.
2. **Read every file found.** This is the step `debloat-file` can't do on a single file, cross-file checks depend on having all of it in view at once.
3. Apply [the full checklist](references/checks.md), every check, including the ones `debloat-file` has to skip: duplication across files, circular imports, and whether a rules-file glob is actually selective in practice given the project's real file layout.
4. Estimate each file's token cost (`words * 1.3`, rounded) and sum for the headline.

## Reporting

Headline first: total estimated always-loaded tokens across the whole surface, and that as a percentage of a 200k reference window. Then findings grouped exactly as the checklist specifies (**Reduces the always-loaded footprint**, **Redundant or duplicated**, **Signal quality**, **Structural**), most token-impact first, each with file and line, the problem in one sentence, and the concrete fix. If the project is already lean, say so plainly, three findings that matter beat twenty that don't.
