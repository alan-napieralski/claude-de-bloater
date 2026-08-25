# Expected findings

This is the best-case fixture: a small, already-disciplined project with no deliberate bloat patterns. `debloat-scan` and `debloat-file` should report **no significant findings**. This fixture exists specifically to catch false positives, if either skill invents a problem here, that is a bug in the skill, not a real issue in the project.

What it does right, for reference: CLAUDE.md is short (under 20 lines) and defers detail to a path-scoped rule rather than inlining it; the rule's `paths:` glob is narrowly scoped to the one file it actually governs; there is no duplication between CLAUDE.md and the rule; no emphasis markers at all, let alone overused ones; no skills, agents, hooks, or commands to be oversized or duplicated.

## Expected report shape

All three severity bands are empty, so per the reporting spec in
[`references/checks.md`](../../../references/checks.md) this report is a headline token estimate,
a plain statement that the surface is already lean, and a one-sentence close saying there is
nothing worth changing. Three specific failures to watch for, each a bug in the skill rather than
a finding about this project:

- **An empty band printed as a heading.** `Issues`, `Warnings`, and `Nice to have` should all be
  omitted, not rendered with nothing under them.
- **A manufactured question.** With nothing in any band, the close must not ask which items to
  include, there are none to offer.
- **A demoted false positive.** A skill that half-recognises this fixture as clean but files
  something under `Nice to have` to avoid an empty report is still returning a false positive.
  The lower band is not a safe place to put a finding that should not exist.
