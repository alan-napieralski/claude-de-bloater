# Report format

Shared by `debloat-scan` and `debloat-file`. Governs the output only. The checks, and each check's severity default, live in [checks.md](checks.md).

## Shape

```
**Headline: ~1,538 always-loaded tokens (0.8% of a 200k window)**
CLAUDE.md (159 words) + docs/style-guide.md via @-import (790) + .claude/rules/catch-all.md (44) + two skill descriptions (190).

### Issues

**`CLAUDE.md:3`, `@docs/style-guide.md` unconditionally imports styling-only content.**
*Reduces the always-loaded footprint, ~1,030 tokens.* The file's own opening line says it only matters when touching CSS or component markup, yet it loads every session. Convert to a path-scoped `.claude/rules/styling.md` instead.

**`.claude/rules/catch-all.md:2`, `paths: ["**/*"]` makes this a second always-loaded file.**
*Reduces the always-loaded footprint, ~60 tokens.* Narrow the glob to the paths the rule actually governs, or fold it into CLAUDE.md and delete it.

### Warnings

**`CLAUDE.md:12-20`, all 8 bullets carry IMPORTANT or CRITICAL.**
*Signal quality.* Reserve emphasis for the two or three rules that need to override default behaviour.

### Nice to have

**`docs/` holds Claude-facing instructions but is named as human documentation.**
*Structural.* Rename to `references/`, or colocate each file with the item that owns it.

---
The Issues above are the ones that matter: fixing them recovers roughly 1,090 tokens. The rest are judgment calls. Tell me which you want included and I'll work through the agreed set.
```

## Rules

- Those three bands, in that order, at that heading level, under those exact names. No colour, emoji or icons.
- Omit an empty band. An all-clean report has no bands at all.
- Within a band, order findings by estimated token impact, largest first.
- Each finding: file and line, the problem in one line, then a tag line carrying the category, the estimated tokens, and the fix.
- The categories are the four check-section names in [checks.md](checks.md). They tag a finding, they do not group it.
- Never invent a 0-100 score.
- Three findings that matter beat twenty that don't.
- Nothing before the report: no preamble, no restating the task, no narrating this format. Start at the headline, or at the first band where there is no headline.

## Headline

Only when there is something substantial to recover. Skip it when the surface is already lean or the recoverable total is trivial, and open with the findings instead. Skip it silently: never announce that it was skipped, or why.

## Close

One or two sentences, after the findings and separate from them: name the Issues and what they recover, then ask which of the lower bands to include.

- No Issues but some lower-band findings: say so, ask about those.
- Nothing in any band: the whole report is one sentence saying there is nothing worth changing, optionally a second naming what was checked. No headline, no bands, no preamble, no question.

The read-only constraint governs the audit. Acting on findings the user has since agreed to is a later step, not part of the report.

## Severity

Each check carries a default. Depart from it only on what the audited file shows, saying why in the fix line.

- **Tiebreak downwards.** Between two bands, take the lower. Overstating severity makes a whole report easy to dismiss.
- **Magnitude promotes only a large always-loaded cost.** Nonzero is not enough; a few hundred tokens stays where the check puts it. Per-invocation and purely qualitative costs never promote, however extreme.
