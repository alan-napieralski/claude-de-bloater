# Expected findings

Ground truth for the seven deliberate patterns seeded in this fixture. Each maps to a mechanism confirmed during research. `debloat-scan` should catch all seven; `debloat-file` should catch the ones judgeable from a single file (marked below).

## 1. Unconditional `@`-import that should be path-scoped

`CLAUDE.md:3` imports `docs/style-guide.md` unconditionally. That file is styling-specific detail, not needed for backend or tooling tasks, and should instead become `.claude/rules/styling.md` with `paths: ["src/css/**", "**/*.html"]` (or similar) frontmatter. Provable with `/context` alone: compare a scenario that never touches a styling file before and after the conversion, the always-loaded total should drop. Judgeable from `CLAUDE.md` alone (file mode).

## 2. The same instruction duplicated across three surfaces

The colour-token instruction ("reference `bg-surface-primary` instead of a raw hex value") appears near-verbatim in three places: `CLAUDE.md` (in "Rules that apply everywhere"), `.claude/rules/catch-all.md`, and `.claude/agents/helper.md`. Needs whole-project context (`debloat-scan`), a single-file pass on any one of the three can't see the other two.

## 3. Emphasis overuse

`CLAUDE.md`'s "Rules that apply everywhere" section prefixes nearly every line with `IMPORTANT` or `CRITICAL`, diluting the signal rather than reinforcing it. Judgeable from `CLAUDE.md` alone (file mode).

## 4. Unselective rules glob

`.claude/rules/catch-all.md` has `paths: ["**/*"]`, behaving exactly like an always-loaded file despite living in the mechanism meant to load conditionally. Judgeable from that file alone (file mode), though confirming it actually behaves as always-on in practice needs the whole-project view.

## 5. Agent duplicating CLAUDE.md content instead of referencing it

`.claude/agents/helper.md` restates several CLAUDE.md rules verbatim in its own prompt instead of relying on the parent session's CLAUDE.md (which the agent inherits automatically). This costs nothing extra in the parent session's `/context`, agents only load their full body in their own isolated window when invoked, but wastes tokens every time `storefront-helper` actually runs. Needs `debloat-scan` to cross-reference against CLAUDE.md; judging the agent file alone can flag "this reads like restated project rules" as a heuristic, but confirming the duplication needs both files.

## 6. Oversized skill with no sibling files

`.claude/skills/big-skill/SKILL.md` (`order-fulfilment`) is 83 lines covering five distinct concerns (order lookup, refunds, shipping labels, customer communications, edge cases) with no `references/`, `scripts/`, or `assets/` directory at all. A real skill this size and breadth would normally push at least the communication templates and edge-case notes into a sibling reference file. Judgeable from that file alone (file mode).

## 7. Bloated, narrative skill description

`.claude/skills/narrative-skill/SKILL.md` (`newsletter-helper`) has a 904-character description written as a flowing sentence rather than "[what it does]. Use when [triggers]." It's the only thing loaded at rest and the only signal Claude has for choosing this skill, a description this long and unstructured wastes always-loaded tokens without actually improving triggering. Judgeable from that file alone (file mode).
