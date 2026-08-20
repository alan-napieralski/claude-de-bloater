# Expected findings

This is the best-case fixture: a small, already-disciplined project with no deliberate bloat patterns. `debloat-scan` and `debloat-file` should report **no significant findings**. This fixture exists specifically to catch false positives, if either skill invents a problem here, that is a bug in the skill, not a real issue in the project.

What it does right, for reference: CLAUDE.md is short (under 20 lines) and defers detail to a path-scoped rule rather than inlining it; the rule's `paths:` glob is narrowly scoped to the one file it actually governs; there is no duplication between CLAUDE.md and the rule; no emphasis markers at all, let alone overused ones; no skills, agents, hooks, or commands to be oversized or duplicated.
