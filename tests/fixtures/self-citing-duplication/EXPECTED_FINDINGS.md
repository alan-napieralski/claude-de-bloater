# Expected findings

One deliberate pattern, isolated: a custom agent that cites another file as its authoritative spec
and then restates that file's content anyway, in paraphrased wording with no identical sentences.
Seeded after a real project (a Numiko prototype starter) reviewed clean on a first `debloat-scan`
pass and turned out to have exactly this pattern between a review agent and its checklist, missed
because nothing string-matched.

## Self-citing duplication: `publish-reviewer.md` vs `docs/publish-checklist.md`

`.claude/agents/publish-reviewer.md` opens by saying `docs/publish-checklist.md` "is your
specification — read it in full before starting and follow it exactly." It then restates that
file's content, section for section, in different words:

- Its "Procedure" repeats the checklist's four "How to review" steps, same order: read the
  manifest, run the build, check title/meta-description/internal-link, check for links into
  `content/drafts/`.
- Its "Reporting" repeats the checklist's "Reporting": one line per failing page, end with a
  yes/no verdict.
- Its closing line repeats the checklist's "Be thorough" note: check every item rather than
  sampling a few.

No sentence is identical between the two files, so a plain string diff or grep finds nothing. It
only surfaces from the whole-project view, doing the topic-by-topic second pass `debloat-scan`'s
checklist requires for the "Redundant or duplicated" section: list the cited file's own sections
(How to review, Reporting), then check the citing file for each one in turn.

**Cost:** the agent pays for `docs/publish-checklist.md`'s full content on every invocation, per
its own instruction to read it in full, *and* carries a paraphrased copy of most of that same
content permanently in its own prompt. Worse than an agent plainly duplicating `CLAUDE.md`, since
here both copies are paid for on every single run rather than the citation replacing one of them.

`debloat-file` cannot catch this on its own: judging `publish-reviewer.md` alone might flag "this
reads like it's restating something," but confirming the duplication needs
`docs/publish-checklist.md` open side by side, which needs `debloat-scan`.

Everything else here is intentionally clean: `CLAUDE.md` is short, has no `@`-imports, and does not
itself restate anything from the checklist beyond naming it. `debloat-scan` should not report
anything else in this fixture — it isolates the one pattern.
