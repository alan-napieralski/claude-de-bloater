# Expected findings

Ground truth for the seven deliberate patterns seeded in this fixture. Each maps to a mechanism confirmed during research. `debloat-scan` should catch all seven; `debloat-file` should catch the ones judgeable from a single file (marked below).

Each finding also carries its **expected severity** under the rubric in [`references/checks.md`](../../../references/checks.md), which owns each check's severity default. What is pinned down here is detection and banding, not presentation. A scan passes or fails on whether it finds these patterns and places them in the right band, whatever shape it chooses for the report itself, so treat wording, ordering, and layout differences as noise rather than as failures.

## 1. Unconditional `@`-import that should be path-scoped

**Expected severity: Issues.** An unconditional import of clearly domain-specific content.

`CLAUDE.md:3` imports `docs/style-guide.md` unconditionally. That file is styling-specific detail, not needed for backend or tooling tasks, and should instead become `.claude/rules/styling.md` with `paths: ["src/css/**", "**/*.html"]` (or similar) frontmatter. Provable with `/context` alone: compare a scenario that never touches a styling file before and after the conversion, the always-loaded total should drop. Judgeable from `CLAUDE.md` alone (file mode).

## 2. The same instruction duplicated across three surfaces

**Expected severity: Issues.** The same instruction substantively duplicated across files.

The colour-token instruction ("reference `bg-surface-primary` instead of a raw hex value") appears near-verbatim in three places: `CLAUDE.md` (in "Rules that apply everywhere"), `.claude/rules/catch-all.md`, and `.claude/agents/helper.md`. Needs whole-project context (`debloat-scan`), a single-file pass on any one of the three can't see the other two.

## 3. Emphasis overuse

**Expected severity: Warnings.** Purely qualitative, no token cost, so the band does not move with how saturated the file is.

`CLAUDE.md`'s "Rules that apply everywhere" section prefixes nearly every line with `IMPORTANT` or `CRITICAL`, diluting the signal rather than reinforcing it. Judgeable from `CLAUDE.md` alone (file mode).

## 4. Unselective rules glob

**Expected severity: Issues.** The mechanism defeats its own purpose.

`.claude/rules/catch-all.md` has `paths: ["**/*"]`, behaving exactly like an always-loaded file despite living in the mechanism meant to load conditionally. Judgeable from that file alone (file mode), though confirming it actually behaves as always-on in practice needs the whole-project view.

## 5. Agent duplicating CLAUDE.md content instead of referencing it

**Expected severity: Warnings.** The cost is per-invocation and invisible to a parent-session `/context` reading.

`.claude/agents/helper.md` restates several CLAUDE.md rules verbatim in its own prompt instead of relying on the parent session's CLAUDE.md (which the agent inherits automatically). This costs nothing extra in the parent session's `/context`, agents only load their full body in their own isolated window when invoked, but wastes tokens every time `storefront-helper` actually runs. Needs `debloat-scan` to cross-reference against CLAUDE.md; judging the agent file alone can flag "this reads like restated project rules" as a heuristic, but confirming the duplication needs both files.

## 6. Oversized skill with no sibling files

**Expected severity: Warnings.** 730 words, roughly 950 estimated tokens, across five concerns, so it clears the token-and-concern threshold decisively rather than marginally. It stays a Warning anyway: a skill body loads only on invocation, so none of this is always-loaded, and splitting it is a restructuring call the user can reasonably decline.

`.claude/skills/big-skill/SKILL.md` (`order-fulfilment`) is 83 lines covering five distinct concerns (order lookup, refunds, shipping labels, customer communications, edge cases) with no `references/`, `scripts/`, or `assets/` directory at all. A real skill this size and breadth would normally push at least the communication templates and edge-case notes into a sibling reference file. Judgeable from that file alone (file mode).

## 7. Bloated, narrative skill description

**Expected severity: Warnings.** Genuinely always-loaded, but modest at roughly 200 estimated tokens.

`.claude/skills/narrative-skill/SKILL.md` (`newsletter-helper`) has a 904-character description written as a flowing sentence rather than "[what it does]. Use when [triggers]." It's the only thing loaded at rest and the only signal Claude has for choosing this skill, a description this long and unstructured wastes always-loaded tokens without actually improving triggering. Judgeable from that file alone (file mode).

## 8. Claude-facing material in a generically-named folder

`docs/style-guide.md` is `@`-imported straight into `CLAUDE.md:3`, which makes it Claude-facing configuration rather than the human-facing documentation a `docs/` folder implies. Under the colocation check it belongs in `references/`, or as a path-scoped rule once finding 1 is applied. Needs `debloat-scan`: judging the file alone cannot tell whether anything imports it.

**Expected severity: Nice to have.** A file-organisation observation with no token cost of its own, and the check itself frames it as a soft flag.

This finding was **missed** on a real scan of this fixture, while the structurally identical `docs/` folder in `severe-bloat` was flagged in the same batch of runs. Same check, same pattern, opposite answer, so it is the sharpest determinism test in the suite. A scan that reports findings 1 through 7 and omits this one has not passed.
