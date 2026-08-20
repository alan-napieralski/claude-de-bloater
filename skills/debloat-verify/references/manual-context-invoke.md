# manual-context-invoke: measuring on-demand content, not just always-loaded

The default matrix (`one-shot`, `brief`, `workflow`) only ever exercises what a project loads
unconditionally: the system prompt, `CLAUDE.md`, the skill/agent registry listing, deferred tool
names. Each of those canary prompts is generic on purpose, so none of them ever name a specific
skill, rule, or command. That means a change to a skill's *body*, a path-scoped rule, or a slash
command's content never shows up in the default real-turn numbers, confirmed directly: trimming a
skill's `SKILL.md` by half moved the default matrix by a fraction of a percent, because none of the
three default prompts ever read it.

`gen_manual_context_invoke.py` closes that gap by discovering a target's on-demand `.md` surface —
skills, path-scoped rules, commands, and each skill's own `references/` files — and generating a
canary that reads all of it in one turn, kept as its own separate cell rather than folded into the
default matrix, so the always-loaded and on-demand numbers never get conflated.

## Why "manual"

This forces every discovered file to load by telling Claude exactly what to read — it is not a test
of whether Claude would ever organically choose to invoke a given skill for a normal, on-topic
prompt with no such instruction. That's a real, different question (does this skill's own
`description:` actually get it picked up in practice, or is it dead weight in the registry that
never fires?), and it's not what this measures. `manual-context-invoke` names that distinction
directly: the load here is manual, forced by the prompt, not organic. Whatever the true trigger rate
turns out to be in normal use, this reports the size of everything on-demand *as if* it all fired at
once — a ceiling, not a typical case.

## Read the file, never invoke it — this was a real bug, not a design choice made up front

The first version of this canary told Claude to invoke the Skill tool for each discovered skill and
to literally run `/<command-name>` for each discovered command, on the theory that this was "the
real mechanism" and would capture real invocation overhead. Confirmed directly, this was wrong in a
way that mattered: invoking a build-oriented command cold measured over **1M cumulative tokens and
$0.54** in a single cell, because invoking something doesn't just load its body into context, it
hands Claude instructions to act on, and a command or skill written to build/act rather than answer
in one turn will do exactly that with no fixed cost — the same failure mode as an ordinary agentic
session, just unexpectedly triggered inside a measurement tool. The same risk applies to skills, not
just commands: a skill body that says "create `posts/drafts/<slug>.md`" would plausibly try to do
that the moment it's invoked, whether or not anything downstream needed a draft post.

The fix, and the only mechanism this canary uses now: **read the defining file, the same bounded way
`debloat-verify` already reads a rule's matched file.** A file returned by the Read tool is inert
tool-result content, not an instruction the model is being asked to follow, so there is nothing here
that opens into an unbounded agentic session. The prompt also says explicitly not to act on, follow,
or execute anything found inside the files it lists, as defense in depth even though a plain read
shouldn't need it.

This trades a small amount of fidelity — a real Skill invocation or command expansion may wrap the
content slightly differently than a raw file read — for a measurement that is bounded, deterministic,
and safe to point at anything. For a before/after *delta*, which is what `debloat-verify` actually
reports, that trade is the right one: the same read mechanism runs on both sides, so a change in body
length still shows up correctly even if the absolute number isn't bit-for-bit identical to a live
invocation.

## What it discovers

- **Skills** (`.claude/skills/**/SKILL.md`) — collected by name (frontmatter `name:`, falling back
  to the directory name) for labeling only; the name is never used to invoke anything. Each skill's
  own `references/**/*.md` files are included too: a skill's body typically tells Claude to read
  these only when a specific branch of its instructions is reached, which is exactly the kind of
  on-demand content this canary exists to catch, and it never shows up in the always-loaded registry
  entry the default matrix already measures. Note this is itself a ceiling, not a typical case: a
  real invocation usually only pulls in whichever reference its own instructions branch toward for
  that specific task, not every reference file the skill owns.
- **Path-scoped rules** (`.claude/rules/*.md`) — a rule only loads when a matching file is opened, so
  discovery resolves each rule's `paths:`/`globs:` frontmatter against the real tree (this is exactly
  why `debloat-verify` prefers a git worktree over a Claude-config-only copy, see
  [isolation.md](isolation.md)) and picks one real matching file per rule to read. A rule whose glob
  matches nothing in this particular tree is skipped and reported on stderr rather than silently
  dropped. Two rules that resolve to the same file (e.g. two catch-all `**/*` globs) only get that
  file read once — reading it twice would waste tokens without measuring anything new.
- **Commands** (`.claude/commands/**/*.md`) — their defining `.md` file is read like everything
  else. Nothing here ever runs `/<command-name>`.
- **Agents** (`.claude/agents/**/*.md`) — discovered but deliberately excluded from the file list.
  An agent's body loads into a *separate* subagent context window when spawned, never into the
  parent session's the way a skill/rule/command does — reading it into the session being measured
  here wouldn't reflect anything that actually happens in real use. Excluded agents are still listed
  in `manual-context-invoke-manifest.json` and reported on stderr so nothing silently vanishes from
  the record.

## Generating and comparing

```bash
python3 scripts/gen_manual_context_invoke.py <target-dir> <out-canary-dir>
```

Writes a single `manual-context-invoke.txt` (every discovered file, deduplicated, in one prompt)
into `<out-canary-dir>`, plus `manual-context-invoke-manifest.json` recording exactly what was
discovered, what was excluded, and why. Prints `manual-context-invoke` to stdout when there's
anything to measure (empty string if the target has no on-demand `.md` content at all) — append
that to `run_harness.sh --matrix` and pass the same directory as `--canary-dir`.

Run it once per side (baseline and candidate each get their own `<out-canary-dir>`), since the two
trees can disagree on what skills/rules/commands even exist. `aggregate.py` needs no changes for
this: it already unions cell names across both reports, so a cell present on only one side prints as
"not run" on the other rather than erroring.

## Why this doesn't replace the default matrix

The always-loaded numbers still matter on their own — most sessions never trigger every skill in a
project, so the always-loaded floor is what nearly every turn actually pays.
`manual-context-invoke` is a ceiling: the size of everything on-demand if it all loaded at once. Run
both, and keep them as separate cells rather than merging them — they answer different questions.
