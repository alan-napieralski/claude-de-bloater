---
name: debloat-scan
description: Analyses a project's entire Claude Code context surface, CLAUDE.md and its @-imports, .claude/rules/*.md, .claude/commands/*.md, .claude/agents/*.md, .claude/hooks/, .claude/settings.json, and .claude/skills/, for token-budget problems, content that is always loaded but could be deferred, redundancy across files, and reference-tiering opportunities. Produces a ranked findings report with an estimated always-loaded token total. Accepts an optional directory (a specific `.claude/skills/<name>` folder, `.claude/rules/`, or any other subdirectory) to scope the scan to, defaulting to the whole project when none is given. Use when the user wants a full audit of a project's Claude Code configuration, asks why their context is so full, or wants to reduce always-loaded overhead across the whole repo or one part of it. Not for grading CLAUDE.md content quality or completeness, use claude-md-improver for that.
argument-hint: "[optional: directory to scope the scan to, e.g. .claude/skills/my-skill — defaults to the whole project]"
allowed-tools: Read Grep Glob
---

# Debloat: whole project

Audits a project's entire Claude Code context surface for token-budget problems. For a single file, use `debloat-file` instead, this skill needs the whole surface to catch cross-file issues.

**Scope directory:** $ARGUMENTS

## Instructions

1. Read [the checks](../../references/checks.md) and [the reporting spec](../../references/reporting.md). Between them they govern the scope boundary, the read-only constraint, the token estimate, every check with its severity default, and the output.
2. **Resolve the scope.** If a directory was given above, resolve it relative to the project root and confirm it exists and sits inside the project, this becomes the scan root for step 3 instead of the whole project; state the resolved path at the top of the report. If it's empty or not given, the scan root is the whole project (previous default behaviour), continue as before.
3. **Enumerate the surface within the scan root.**
   - Whole-project root: find the project's `CLAUDE.md` (and any nested `CLAUDE.md`/`CLAUDE.local.md`), walk its `@`-import graph fully (Claude Code resolves imports up to 4 hops deep, so that's the full graph, anything past that never loads), and find `.claude/rules/*.md`, `.claude/commands/*.md`, `.claude/agents/*.md`, `.claude/hooks/`, `.claude/settings.json`, and `.claude/skills/*/SKILL.md`. Stay inside the project directory per the scope boundary, do not walk an `@`-import that leads outside it.
   - A specific skill directory (contains a `SKILL.md`): treat that `SKILL.md` plus its `references/`, `scripts/`, and `assets/` as the surface. Skip the other standard locations entirely, this is a targeted audit of one skill, not the project.
   - Any other subdirectory (e.g. `.claude/rules/`, `.claude/agents/`): find every matching file inside it only (`*.md` for rules/agents/commands, `*/SKILL.md` under `.claude/skills/`, etc.), and skip locations outside it.
   - In every case, also pull in any file inside the scan root that names another file as its authoritative spec/procedure/checklist and instructs reading it in full (a rules file, agent, or command pointing at a plain `docs/*.md`, for example) — it sits outside the standard list and does not count toward the always-loaded headline, but it is needed in view to check the citing file for restated content instead of a genuine reference. Follow such a pointer even if the file it names lives outside the scan root.
4. **Read every file found.** This is the step `debloat-file` can't do on a single file, cross-file checks depend on having all of it in view at once.
5. **Apply every check**, including the ones marked "needs the whole surface" that `debloat-file` has to skip. When scoped to a subdirectory, judge cross-file checks (duplication, redundant citations) only across the files actually enumerated in step 3, not the rest of the project. Duplication is the check most likely to be under-run on a single read: follow the "Redundant or duplicated" section literally, including its topic-by-topic second pass and its instruction to check any file that cites another as authoritative against what that file actually says, before concluding the scope has none.
6. Estimate each file's token cost and sum them for the headline.
