---
name: debloat-file
description: Analyses a single CLAUDE.md, SKILL.md, or .claude/rules/*.md file for token-budget problems: unnecessary length, content that could be tiered to load conditionally instead of always-on, emphasis overuse, and missing progressive disclosure. Use when the user points at one specific file and asks whether it is bloated, too long, or well-tiered. Not for grading documentation completeness or quality, use claude-md-improver for that.
tools: Read, Grep, Glob, Bash
---

# Debloat: single file

Reviews one file's token budget. For a whole project's surface (CLAUDE.md plus its imports, rules, commands, agents, hooks, skills together), use `debloat-scan` instead, this skill only sees the one file it's pointed at.

Advisory only. Read-only, never edit the file, hand findings back for the user to act on.

## Procedure

1. Read the target file in full.
2. Read [the shared checklist](../debloat-scan/references/checks.md) and apply every check that can be judged from this one file alone: line and size caps, unconditional-import candidates, unselective rules globs, emphasis overuse, oversized-SKILL.md-with-no-siblings, description quality. Skip checks that need other files to judge (duplication across files, circular imports, whole-project redundancy), note plainly that those need `debloat-scan` instead rather than silently omitting them.
3. Estimate the file's token cost (`words * 1.3`, rounded) and report it as an estimate.

## Reporting

Headline first: estimated tokens for this file, and that as a percentage of a 200k reference window. Then findings grouped as the checklist specifies, most token-impact first, each with the line, the problem in one sentence, and the concrete fix. If nothing is wrong, say so plainly rather than padding the list.
