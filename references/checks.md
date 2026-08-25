# Debloat checks

Shared by `debloat-scan` (whole project) and `debloat-file` (one file). The output shape lives in [report-format.md](report-format.md).

Run every check below. Each carries a severity default and a note on why it matters; use both when writing the finding. A check marked **(needs the whole surface)** can't be judged from one file alone; `debloat-file` skips those and says so.

## Scope

Advisory only. Read-only, never edit anything.

Audit only what the skill was pointed at: the project directory for `debloat-scan`, the single file for `debloat-file`. Never follow an `@`-import out of it.

The user's global `~/.claude/CLAUDE.md` and its imports load in every session and belong to none of this. Keep them out of the output entirely, headline and findings and asides alike. Where the audited file duplicates global config, judge it on its own merits and say nothing about the global side. Surface global config only if the user asks.

## Token estimate

`words * 1.3`, rounded, always stated as an estimate. Defer to `/context` where the real number matters.

A skill's `description` counts toward the always-loaded total; its body does not. Skill bodies, agent prompts and command prompts load only when the item runs, so price those per-invocation and keep them out of the headline.

## Reduces the always-loaded footprint

**Line cap.** A CLAUDE.md or rules file over roughly 200 lines. This is Anthropic's own guidance, not a house rule: "target under 200 lines per CLAUDE.md file... longer files consume more context and reduce adherence." Some content earns the length, so flag it as a candidate rather than a defect. Claude Code only hard-skips a CLAUDE.md past 4 MiB, so never report a smaller one as dropped.
*Severity: Warnings, rising to Issues once the excess is large and mostly domain-specific. Length costs adherence to the file's own contents, not only tokens.*

**Unconditional `@`-imports of content that is not universally needed.** Imports load in full at launch whatever the task ("splitting into `@path` imports helps organization but doesn't reduce context"). A domain-specific import (styling, one framework, one language) belongs in a path-scoped `.claude/rules/*.md` with `paths:` frontmatter instead. Leave alone imports genuinely needed on every task.
*Severity: Issues. Usually the largest recoverable number in a scan, since the whole file is paid on every turn.*

**Circular `@`-imports (needs the whole surface).** File A imports B imports A, or any longer cycle. Build the graph and check it for cycles. Imports resolve four hops deep, so a chain deeper than that silently never loads.
*Severity: Issues. The mechanism is broken rather than merely wasteful, and a graph-and-cycle check is cheap.*

**An unselective `paths:` glob in a rules file**, `["**/*"]` or `["*"]`. Behaves exactly like an always-loaded file while sitting in the mechanism meant to load conditionally. Suggest a glob matching the file's actual subject.
*Severity: Issues. The file defeats the only reason it is a rule and not part of CLAUDE.md.*

**An agent prompt that duplicates CLAUDE.md wholesale instead of referencing it (needs the whole surface).** Free in the parent session, since an agent only loads its body in its own window on invocation, but that window then carries the redundant copy on every run.
*Severity: Warnings, the cost is per-invocation. Say explicitly that a parent-session `/context` reading cannot see it.*

**Human-facing maintainer notes written as visible prose.** Block HTML comments (`<!-- -->`) are stripped before injection and cost nothing, so a "why we did it this way" aside, a TODO, or a note about who owns a section is a free move into one. Not for content Claude also acts on.
*Severity: Nice to have. Small, but the rare finding that costs nothing at all to apply.*

**An ancestor CLAUDE.md or rules directory belonging to a different team or package (needs the whole surface).** In a monorepo these load for every session anywhere below them. `claudeMdExcludes` in `.claude/settings.local.json` skips named files or globs. Only for a surface that genuinely holds several teams' instructions, not a normal single package.
*Severity: Issues where it genuinely applies. The cost is unbounded and invisible to whoever owns the subdirectory.*

## Redundant or duplicated (needs the whole surface)

**The same instruction repeated across two or more files.** Reworded restatement counts, not only matching strings: the same items in the same order, the same steps in the same sequence, the same qualifier on the same rule. Two files explaining one convention from genuinely different angles is not redundant. Flag each location, keep the fullest version in the most-loaded place, reference it from the rest.
*Severity: Issues. Every copy is paid for separately, and copies drift apart into contradictions.*

**Do not conclude "no duplication" from one read per file.** The copies are rarely adjacent or worded alike. Do a second pass keyed by topic rather than by file: list every distinct instruction, procedure and fixed set of items anywhere in the surface, then check each against every other file. A convention recurring three or more times is common wherever a project has several documentation tiers, so treat a clean first pass as a reason to look harder.

**A file that cites another as authoritative and then restates it anyway.** "See `docs/X` for the full procedure", or "`X` is the spec, read it in full", followed by that same procedure reproduced in the body, paraphrased. The citation makes what follows easy to skim past, but citing the canonical copy does not cancel restating it. Pull the cited file into the surface even when it is a plain `docs/*.md` nothing `@`-imports, and diff it section by section against the citing file.
*Severity: Issues. In an agent or command the waste compounds rather than doubles: the cited file is read in full on every run and the restated copy sits in the prompt permanently. This is the most common way real duplication hides.*

## Signal quality

**Emphasis-word overuse.** Emphasis does tune adherence, but newer-model guidance warns it overtriggers when overused, and marking nearly every line dilutes it back to nothing. Flag a file where most lines carry IMPORTANT, CRITICAL or YOU MUST.
*Severity: Warnings, the cost is qualitative. Saturation means the rules that genuinely need to override default behaviour no longer stand out.*

## Structural (file-level, for `debloat-file` especially)

**An oversized SKILL.md with no sibling reference files, scripts or assets.** Real skills push detail into `references/*.md` linked from the body, or into `scripts/*`. Judge on estimated tokens and distinct-concern count together, never line count: a body over roughly 600-700 tokens *and* covering more than two or three independent concerns is a real violation. One concern in depth is fine at any length, that is what a body is for.
*Severity: Warnings. The body loads whole on invocation, so a task needing one concern pays for all of them.*

**A SKILL.md description that is narrative rather than trigger-shaped, or near the 1024-character cap.** It should read as what it does in one sentence, then "Use when [concrete triggers]".
*Severity: Warnings, or Nice to have where the description is well short of the cap and only its shape is wrong. The description is the only part loaded at rest and the only signal for choosing this skill over another.*

**Reference material that doesn't follow the `references/` colocation convention.** Material owned by one rule, agent, skill or command belongs beside it as `.claude/<type>/<name>/references/*.md`, a plain sibling folder its own file points at by relative path. Agents and rules are discovered by frontmatter and glob rather than by filename, so the item's file stays flat with a same-named `references/` folder added next to it. Material no single item owns belongs in one root-level `references/`.

A generic top-level folder (`docs/`, `notes/`) is fine when it holds genuine human-facing documentation. Raise it only when the contents are a CLAUDE.md extension in disguise: instructions written for Claude that some rule or agent depends on. Anything reached by `@`-import qualifies by definition. The other clear tell is the material's own text ("this is the spec for the X agent") while it sits somewhere nothing points at exclusively. Suggest renaming to `references/`, or colocating with the owning item, rather than treating the folder name as the defect.
*Severity: Nice to have. Claude Code does not auto-load `references/*.md` outside a skill, so this costs nothing by itself, but poor colocation is what leads to the token findings above: shared-folder material gets swept into an unconditional import, or its ownership goes unclear and it gets duplicated instead of referenced.*
