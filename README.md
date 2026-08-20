# claude-de-bloater

A Claude Code plugin that analyses a project's Claude Code context surface (CLAUDE.md and its `@`-imports, `.claude/rules/`, `.claude/commands/`, `.claude/agents/`, `.claude/hooks/`, `.claude/skills/`) for token-budget problems, and empirically measures whether a proposed fix actually helps.

It answers a different question to Anthropic's own `claude-md-management` plugin: that one grades whether your CLAUDE.md is good *documentation* (complete, current, actionable). This one asks whether your setup is a good *token budget*: what's always loaded that could instead load on demand, what's duplicated across files, and whether a fix actually measurably reduces context usage rather than just looking tidier.

## Why this exists

Every serious tool in this space converges on the same idea: split what's always loaded from what loads on demand, and treat that split as a budget to manage, not an afterthought. Two things set this plugin apart from just "shortening your CLAUDE.md":

- **Structure and reference-tiering beat prose-cutting.** The biggest measured wins come from moving unconditional `@`-imports into path-scoped rules, not from trimming sentences.
- **Every claim gets checked against a real number, not asserted.** Suggestions are validated with measured before/after token counts, not just theory.

## The standard structure this tool checks against

There's no single mandated layout, but the checks in `debloat-scan`/`debloat-file` all point at the same shape. This is what a project that would score cleanly looks like:

```
my-project/
├── CLAUDE.md                     # short, project-wide only; content Claude can't infer from the code
├── .claude/
│   ├── rules/
│   │   └── frontend-styles.md    # paths: ["src/styles/**"] frontmatter, loads only when touched
│   ├── agents/
│   │   ├── deployer.md
│   │   └── deployer/
│   │       └── references/
│   │           └── rollout-steps.md   # this agent's own detail, colocated next to it
│   ├── commands/
│   │   └── release.md
│   └── skills/
│       └── changelog-writer/
│           ├── SKILL.md          # short body; detail pushed out, not inlined
│           ├── references/
│           │   └── format-guide.md
│           └── scripts/
│               └── generate.py
├── references/
│   └── conventions.md            # general "good to know" material, not owned by any one item above
├── docs/
│   └── architecture.md           # genuine human-facing documentation, untouched by Claude Code
└── src/
    └── ...
```

A few things this layout deliberately gets right:

- **`CLAUDE.md` stays lean and does its own `@`-importing sparingly.** Only content genuinely needed on every task lives here or in an unconditional import; anything domain-specific moves to a rule instead.
- **`.claude/rules/*.md` carry a narrow `paths:` glob**, never `["**/*"]` or `["*"]`, so they load only when relevant rather than acting as a second always-loaded CLAUDE.md.
- **An agent's own long reference material sits beside it** as `<name>/references/*.md`, not in a shared folder, so ownership stays unambiguous.
- **A `SKILL.md` body stays short**, with real detail pushed into its own `references/*.md` (loaded progressively) and `scripts/*`, matching Claude Code's own skill format.
- **A root-level `references/*.md` folder holds only material no single rule, agent, skill, or command owns.** Anything narrower belongs colocated instead.
- **`docs/` or `notes/` are left alone when they're genuinely human-facing.** A generic folder name isn't a problem by itself; it's only worth a flag if what's actually inside is Claude-facing instruction material wearing a docs folder as a disguise.

## Before you start

**`debloat-scan` and `debloat-file` need nothing.** They read files directly and estimate token cost from word count, no auth, no setup, no dependency on the point below.

**`debloat-verify` needs a one-time auth step, for *every* mode it runs, not just real-turn.** It shells out to `claude -p` to run `/context` and, optionally, real prompted turns. Confirmed directly: without a valid long-lived token, `/context` silently reports Memory Files and Custom Agents as `0` regardless of their real size, even though the command makes no real API call and reports success either way. Since Memory Files is CLAUDE.md content, the thing this whole plugin is about, an unauthenticated run can produce a report that looks complete but is quietly wrong about the number that matters most. One-time fix:

```bash
claude setup-token
```

This prints a token. Export it from `~/.zshenv` specifically, **not** `~/.zshrc` (confirmed the hard way: non-interactive shells, which is what this harness uses, only load `.zshenv`):

```bash
echo 'export CLAUDE_CODE_OAUTH_TOKEN="paste-the-token-here"' >> ~/.zshenv
```

It's a real standing credential, treat it like a password. It draws on your existing account/subscription, not a separate pay-per-use key.

If you'd rather not set this up, `debloat-verify` still runs and still reports Skills/plugin numbers correctly, but every report is stamped `"auth_available": false` with an explicit warning, and Memory Files numbers in that report should not be trusted. It won't fail silently or pretend those numbers are real.

Real-turn mode specifically (`--mode real-turn`/`both`, a small real cost per call) is a cross-check once auth is set up, and the only way to see the actual cost of a custom agent that duplicates CLAUDE.md content instead of referencing it, a cost that never shows up in the parent session's `/context` at all.

## Skills

- **`debloat-scan`**: audits a whole project's Claude Code surface. Advisory only, read-only.
- **`debloat-file`**: audits a single CLAUDE.md, SKILL.md, or rules file. Advisory only, read-only.
- **`debloat-verify`**: measures the real before/after impact of a proposed change, in an isolated scratch copy, never the live project.

## Installing for local development

```bash
claude --plugin-dir /path/to/claude-de-bloater
```

If you're testing the plugin against a fixture or project that sits inside this repo's own directory tree, also pass `--add-dir /path/to/claude-de-bloater`, otherwise the skills can't read their own bundled reference files (confirmed directly: Claude Code's file-access sandbox for a `--plugin-dir`-loaded plugin defaults to just the working directory, not the plugin's own install path).

## Tests

`tests/fixtures/` holds small, purpose-built projects for validating the plugin itself, not real client work:

- **`bloated-sample`**: seven independent bloat patterns, ground truth in `EXPECTED_FINDINGS.md`.
- **`severe-bloat`**: the worst case, every pattern from `bloated-sample` intensified, plus a circular `@`-import (not present in `bloated-sample`). Ground truth in `EXPECTED_FINDINGS.md`.
- **`lean-baseline`**: the best case, a small, already-disciplined project with nothing to flag. Exists to catch false positives, if a skill invents a problem here, that is a bug.
- **`self-citing-duplication`**: one isolated pattern, an agent that names another file as its authoritative spec and then restates that file's procedure and reporting format anyway, paraphrased so no sentence matches identically. Exists to catch under-running the "Redundant or duplicated" check: this pattern is invisible to a plain string diff and was missed on a first real-world scan before the check's method was tightened.
- **`one-shot-small-app`**: a genuinely tiny, complete app (a single-page tip calculator), used to give the one-shot/brief canary prompts something realistic to measure against.
- **`multi-workflow-app`**: a small static blog with a skill, an agent, and a command chained across a real three-step workflow (draft, review, publish), used to give the workflow canary prompt something realistic and multi-step to act on.

None of the fixtures need to be git repos themselves, `debloat-verify` exercises its plain-directory-copy path against them; its git-worktree path is exercised against real external projects instead (see `references/isolation.md`).

## Research and background

The design choices above did not come from guessing. This section is the research behind them: how Claude Code actually loads context, what Anthropic itself documents, and how this plugin compares to the rest of the field. Findings marked **verified** were confirmed first-hand against live data on a real machine, not taken on trust.

### How Claude Code actually loads context

**Skills use progressive disclosure, verified directly.** Every installed skill's name and description sit in context at rest; the full body and any bundled resources load only on invocation. Running with `--bare` (which skips CLAUDE.md auto-discovery and auto-memory) drops the reported skills cost to exactly zero and removes the whole Skills table from `/context`'s output, rather than showing zeroes, confirming the descriptions are a discoverability cost Claude Code chooses to pay, not an architectural requirement.

**`@`-imports load unconditionally, regardless of relevance.** Anthropic's own [memory documentation](https://code.claude.com/docs/en/memory#import-additional-files) states this twice: splitting content into an `@`-imported file aids organisation but does not reduce context, every imported file is expanded and loaded at launch alongside the file that references it. Imports resolve up to four hops deep and skip fenced code blocks and inline code spans. The mechanisms that actually load conditionally are different ones entirely: nested `CLAUDE.md`/`CLAUDE.local.md` files (load only when a file in that directory is read), `.claude/rules/*.md` with `paths:` frontmatter (load only when a matching file is touched), and skill bodies (load only on invocation).

**Custom agent definitions cost almost nothing in the parent session, and that is correct behaviour, not a bug.** A deliberately large (1,694-word) test agent file consistently showed only around 30 tokens in `/context`. This makes sense architecturally: an agent only gets its own isolated context window when actually invoked as a subagent, so the parent session correctly never pays its full body cost. The practical consequence: a custom agent that duplicates CLAUDE.md content instead of referencing it wastes tokens every time it runs, but that cost is invisible to a `/context` reading of the parent session, with or without a real prompted turn on the parent. Seeing it requires measuring the agent's own context, out of scope for this plugin's harness in its current form.

**`/context`'s Memory Files and Custom Agents accounting depends entirely on valid auth being available, confirmed by a direct A/B test.** This took two wrong explanations before landing on the right one. The first pass at this research saw Memory Files consistently report `0` regardless of real file size and called it a permanent measurement gap. A retest with controlled, proportional test files later the same day showed correct, proportional numbers and that finding was walked back as a "cold-start anomaly." Neither was right. The actual cause: running `env -u CLAUDE_CODE_OAUTH_TOKEN` against an *unchanged* directory reproduces `0` for Memory Files on demand, and removing the `env -u` makes the correct number reappear, four repeats each way. `/context` makes no real API call and reports success either way, so this failure is completely silent, a report can look complete while being quietly wrong about the one number this plugin cares about most. `debloat-verify`'s harness checks for a valid token before trusting any mode because of this, and stamps every report with `auth_available` plus an explicit warning when it's missing. The lesson generalises past this one command: a finding "verified, reproduced three times" can still have the wrong explanation if an obvious confound, here, auth state, which had also just changed between tests, isn't controlled for.

**The isolation recipe for measuring a target project without the operator's personal setup leaking in is `--setting-sources project` alone, not `--bare`.** `--bare --add-dir <target>` was tried first and suppresses everything, including the target project's own skills, agents, and CLAUDE.md, reporting a flat `0/200k` with no breakdown at all. `--setting-sources project` alone, tested against a scratch project with a deliberate project-level skill, agent, and CLAUDE.md run alongside the operator's normal global config, correctly excluded the operator's personal user-level skills and agents while keeping the target's own. A handful of "undefined"-source skills still appear regardless, Claude Code's own built-in skills, present on any installation, not contamination.

**A real prompted turn's cost accounting is cache-aware, and the useful metric is a sum, not `input_tokens` alone.** Two identical real canary calls back to back: the first showed `input_tokens: 3, cache_creation_input_tokens: 19505, cache_read_input_tokens: 0`; the second, same prompt, showed `input_tokens: 3, cache_creation_input_tokens: 5508, cache_read_input_tokens: 13997`. Cost dropped by roughly two-thirds between the calls (cache reads are billed far cheaper than cache writes), but `input_tokens + cache_creation_input_tokens + cache_read_input_tokens` was exactly 19,508 both times. That sum, not `input_tokens` alone (which was a nearly meaningless `3` either time), is what the harness uses as its real-turn size metric. It also settles the repeats question: a single call already gives a deterministic total for a fixed configuration, so repeats only matter for the multi-step workflow scenario, where the model's actual behaviour, not just tokenisation, can genuinely vary run to run.

### Official Anthropic guidance on structuring CLAUDE.md

Sourced from Anthropic's own [memory docs](https://code.claude.com/docs/en/memory) and [best-practices guide](https://code.claude.com/docs/en/best-practices).

- **Structure.** Keep a CLAUDE.md under roughly 200 lines; longer files consume more context and measurably reduce adherence to what's in them. Apply a strict inclusion test: keep only what Claude cannot infer from the code itself, cut anything it could derive on its own, anything that changes frequently, or anything self-evident. The documented failure mode is the over-specified file, where excess length buries the rules that actually matter in noise.
- **Signalling importance.** Genuinely contested territory. Anthropic's docs confirm emphasis (IMPORTANT, YOU MUST) does tune adherence and should be reserved for genuinely critical rules, that is not folklore. But their own model-specific guidance for newer Opus models warns that models are now responsive enough to the system prompt that aggressive phrasing causes overtriggering. More importantly for anything safety-critical: Anthropic states outright that CLAUDE.md is context, not enforced configuration, with no guarantee of compliance, their documented fix for anything that must always happen is a deterministic `PreToolUse` or `Stop` hook, not stronger wording. No specific severity-tier vocabulary (MUST/SHOULD/MAY, P0/P1/P2, or similar) appears in Anthropic's own documentation, it is a practitioner convention where it appears, not an Anthropic-endorsed standard.
- **General context management.** Framed by Anthropic as an ongoing discipline ("context engineering"), not a one-off authoring task: curate what is in the window every turn, not just at the start. Concrete mitigations include pitching instructions at the right altitude (specific enough to act on, not so brittle it hardcodes every case), compaction for a near-full window, structured note-taking so an agent can persist progress outside the window, and delegating exploration to subagents that return a condensed summary rather than their full working context.
- **Imports versus conditional loading.** `@`-imports flatten and always load, useful for one canonical shared source, not for lazy loading. Nested directory-level CLAUDE.md files, path-scoped `.claude/rules/*.md`, and skills are the three mechanisms that actually keep tokens out of the window until they are relevant.

### The competing tool landscape

Every figure below was independently checked against live GitHub data or the actual source file, none of it taken on a research pass's word alone.

| Tool | Stars | What it does |
|---|---|---|
| [Oaken AI Workspace Optimizer](https://github.com/Oaken-AI/claude-workspace-optimizer) | 13 | Read-only Python CLI scanner. Scores memory-file visibility against a hardcoded 200-line/25KB cap, flags "inline bloat", outputs a 0-100 health score and a prioritised fix list. Its generated HTML report also embeds consultancy backlinks and a donation link, worth knowing since it was the original reference point for this project. |
| [claudelint](https://claudelint.com/) | 11 | 116 rules across 10 categories covering CLAUDE.md, skills, settings, hooks, MCP servers, and plugins. Has circular-import and size-limit checks, CLI auto-fix, SARIF export. |
| [AgentLinter](https://agentlinter.com/) | 77 | Scores across 8 weighted dimensions into S-to-C letter grades with percentile ranking, runs entirely locally. |
| [AgentLint](https://www.agentlint.app/) | ~50-77 (three unrelated repos share the name) | 33 checks across five categories, built around the idea that most of an agent's effective performance lives in the surrounding configuration and tooling, not the model itself. |
| [claude-context-optimizer ("CCO")](https://github.com/egorfedorov/claude-context-optimizer) | 94 | The most rigorously engineered comparable tool found. A live Claude Code plugin, not a one-shot scanner: per-language token costs calibrated against thousands of real source files, a command that prices system prompt/tools/MCP/CLAUDE.md from first-turn ground-truth API usage, cache-aware cost accounting, and an explicit check on whether its own instrumentation saves more than it costs. |
| [Token Savior](https://github.com/Mibayy/token-savior) | 1,121 | MCP server doing progressive file retrieval (symbol summary before full-file expansion) plus persistent memory. |
| [RTK](https://github.com/rtk-ai/rtk) | 76,740 | Much broader scope: a Rust CLI proxy that compresses terminal/command output generally, not CLAUDE.md-specific. |
| [Context Mode](https://github.com/mksglu/context-mode) | 20,001 | Sandboxes large tool outputs outside the main conversation across 17 platforms via MCP and hooks. |

Recurring themes across the whole landscape: reference tiering (splitting always-on instructions from load-on-demand reference material) is the one universal heuristic every serious tool converges on; a single headline score is now table stakes, followed by a prioritised fix list; nearly everything hands its findings back to Claude for remediation rather than auto-fixing everything itself; and it is a crowded, very young, fast-churning niche, most tools here were created between February and April 2026, with several unrelated projects sharing near-identical names.

### Sources

- [Claude Code memory documentation](https://code.claude.com/docs/en/memory)
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices)
- [Effective context engineering for AI agents (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Equipping agents for the real world with Agent Skills (Anthropic)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Long-context prompting tips (Anthropic)](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/long-context-tips)
- [Context Rot study (Chroma Research)](https://www.trychroma.com/research/context-rot)
- [12-factor-agents (HumanLayer)](https://github.com/humanlayer/12-factor-agents)
- [The rise of context engineering (LangChain)](https://blog.langchain.com/the-rise-of-context-engineering/)
- [Lost in the Middle (Liu et al., arXiv:2307.03172)](https://arxiv.org/abs/2307.03172)
- [The Instruction Hierarchy (arXiv:2404.13208)](https://arxiv.org/abs/2404.13208)
- [Oaken AI Workspace Optimizer](https://github.com/Oaken-AI/claude-workspace-optimizer)
