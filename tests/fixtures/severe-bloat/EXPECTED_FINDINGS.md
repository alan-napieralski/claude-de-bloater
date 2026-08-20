# Expected findings

The worst-case fixture: every pattern from `bloated-sample`, more of them, plus one new mechanism (circular imports) not seeded there.

1. **Two unconditional `@`-imports**, `docs/styles.md` and `docs/backend.md`, both domain-specific (styling, backend) rather than universal, both candidates for path-scoped rules instead.
2. **A circular `@`-import**: `docs/backend.md` imports `docs/db-conventions.md`, which imports `docs/backend.md` back. Neither file needs the other's full content inline, this is a structural mistake, not a token-cost issue by itself.
3. **The colour-token instruction duplicated across five surfaces**: `CLAUDE.md`, `docs/backend.md` (inside an unrelated "Currency" section, easy to miss), `.claude/rules/general.md`, `.claude/agents/reviewer.md`, and `.claude/agents/deployer.md`. Several other instructions (lint before complete, never commit to `main`, 2-space indentation) are duplicated across three or more of these same surfaces too.
4. **Two unselective rules globs**: `.claude/rules/general.md` (`paths: ["**/*"]`) and `.claude/rules/quality.md` (`paths: ["*"]`), both behaving as always-on.
5. **Two agents duplicating CLAUDE.md content wholesale**: `reviewer.md` and `deployer.md`, both restating rules instead of relying on the parent session's CLAUDE.md.
6. **Near-total emphasis overuse in CLAUDE.md**: 10 of 12 rules carry CRITICAL or IMPORTANT, more saturated than `bloated-sample`'s equivalent.
7. **An oversized skill with no sibling files**: `reports-skill/SKILL.md` (`financial-reports`), 696 words across seven genuinely independent concerns (spending, budget, tax, net worth, three export formats, scheduling, common mistakes), a clear violation under the corrected token-and-concern-based check, not a near-miss like `bloated-sample`'s comparable fixture.
8. **A bloated, narrative skill description**: `billing-skill/SKILL.md` (`invoice-helper`), written as a single flowing sentence rather than trigger-shaped.
