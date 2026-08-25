---
name: debloat-file
description: "Analyses a single CLAUDE.md, SKILL.md, or .claude/rules/*.md file for token-budget problems: unnecessary length, content that could be tiered to load conditionally instead of always-on, emphasis overuse, and missing progressive disclosure. Use when the user points at one specific file and asks whether it is bloated, too long, or well-tiered. Not for grading documentation completeness or quality, use claude-md-improver for that."
allowed-tools: Read Grep Glob
---

# Debloat: single file

Reviews one file's token budget. For a whole project's surface (CLAUDE.md plus its imports, rules, commands, agents, hooks, skills together), use `debloat-scan` instead, this skill only sees the one file it's pointed at.

## Instructions

1. Read [the checks](../../references/checks.md) and [the report format](../../references/report-format.md). Between them they govern every step below: the scope boundary, the read-only constraint, every check and its severity, the token estimate, and the output shape.
2. Read the target file in full.
3. **Apply every check not marked "needs the whole surface"**, that mark is the only thing that decides applicability here. For the ones it skips, note plainly that they need `debloat-scan` instead, rather than silently omitting them.
