# Debloat checks

Shared by `debloat-scan` (whole project) and `debloat-file` (one file). Every check reports its estimated token cost using the same tokens-per-word approximation: `words * 1.3`, rounded, and states it as an estimate, not an exact count. Where the real number matters, defer to a `/context` reading instead of the estimate.

Every finding must name the file and line, the problem in one line, and the concrete fix. Group findings under **Reduces the always-loaded footprint**, **Redundant or duplicated**, **Signal quality**, and **Structural**, most token-impact first. Report a headline number before the findings: total estimated always-loaded tokens across the whole surface, and that as a percentage of a 200k reference window. Do not invent a 0-100 score, the headline is the token estimate itself.

## Reduces the always-loaded footprint

**Line and size caps.** A CLAUDE.md, rules file, or any always-loaded file over roughly 200 lines or 25KB is a candidate for trimming or splitting, this threshold comes from Anthropic's own documented guidance and matches what other tools in this space use independently. Flag it, do not assume it is wrong on its own, some content genuinely needs that length.

**Unconditional `@`-imports of content that is not universally needed.** `@`-imports load in full, unconditionally, at launch, regardless of whether the current task touches that content. If an imported file is domain-specific (styling, a particular framework, a particular language) rather than genuinely relevant to every single task, it is a candidate for converting into a path-scoped `.claude/rules/*.md` file with `paths:` frontmatter instead, which only loads when a matching file is touched. Do not flag an import of content that is genuinely needed on every task (project overview, core conventions), that is what imports are for.

**Circular `@`-imports.** Walk the import graph from each CLAUDE.md: file A imports file B imports file A (or a longer cycle). This wastes nothing by itself (Claude Code presumably resolves it safely) but signals a structural mistake worth fixing, and is cheap to detect: build the graph, check for cycles.

**An unselective `paths:` glob in a rules file** (for example `paths: ["**/*"]` or `paths: ["*"]`). This behaves exactly like an always-loaded file despite living in the mechanism meant to load conditionally. Flag it and suggest a narrower glob matching the file's actual subject.

**A custom agent's prompt that duplicates CLAUDE.md content wholesale instead of referencing it.** This does not cost anything in the parent session (agents only load their full body in their own isolated context window when invoked), but it does mean that isolated window carries redundant content every time the agent runs. Flag it as a finding, note explicitly that its cost is invisible to a parent-session `/context` reading and only shows up when the agent is actually used.

## Redundant or duplicated

**The same instruction, substantively repeated across two or more files** (CLAUDE.md, a rules file, an agent prompt, a command). Near-verbatim repetition, not just a shared theme, if two files independently explain the same convention in different words that is not automatically redundant. Flag each duplicate location, suggest keeping the fullest version in the most-loaded-by-default location and having the others reference it instead.

## Signal quality

**Emphasis-word overuse.** Anthropic's own guidance confirms emphasis (IMPORTANT, YOU MUST, CRITICAL) measurably tunes adherence, but their model-specific guidance for newer models also warns this can overtrigger when overused, and using it on nearly every line dilutes it back down to no signal at all. Flag a file where most lines carry emphasis markers, since that is a sign none of them are actually being treated as more important than the rest. This is a quality finding, not a token-count one, report it separately from the always-loaded-footprint findings.

## Structural (file-level, for `debloat-file` especially)

**An oversized SKILL.md with no sibling reference files, scripts, or assets.** Real Claude Code skills push detail into `references/*.md` (linked inline from the body) or `scripts/*` once the body would otherwise run long or cover more than one distinct concern. Judge this on estimated tokens and distinct-concern count together, not raw line count, a prose-paragraph body can pack several hundred words into fifty short-looking lines. As a rough guide: a body estimated over roughly 600-700 tokens *and* covering more than two or three genuinely independent concerns (each a candidate for its own reference file) is a real violation, not a near-miss. A shorter body, or one covering a single concern in depth, is fine at any line count, depth on one topic is what a skill body is for.

**A SKILL.md description that is narrative rather than trigger-shaped, or near the 1024-character cap.** The description is the only thing loaded at rest and the only signal Claude has for choosing this skill over another. It should read as: what it does, in one sentence, then "Use when [specific, concrete triggers]." A long, story-like description wastes always-loaded tokens without actually improving triggering, and a description near the character cap is worth double-checking for the same reason a long always-loaded file is.
