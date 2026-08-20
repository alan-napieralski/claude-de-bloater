# Isolation recipe

The harness needs to measure a *target* project's own context footprint without the operator's personal global CLAUDE.md, skills, or agents leaking into the numbers. Two things were tried, only one works.

**Does not work: `--bare --add-dir <target>`.** Confirmed directly: `--bare` suppresses everything, including the target project's own skills, agents, and CLAUDE.md, not just the operator's personal config. It reports a flat `0/200k` with no breakdown at all. Not viable.

**Works: `--setting-sources project` alone, no `--bare`.** Confirmed directly against a scratch project with a deliberate project-level skill, agent, and CLAUDE.md, run alongside the operator's normal global config. It correctly excluded every one of the operator's personal user-level agents and roughly forty personal user-level skills, while keeping the target's own project-scoped skill, agent, and a proportionally-sized CLAUDE.md (1,400 words showed as 2.4k tokens). This is what `run_harness.sh` uses.

**A handful of "undefined"-source skills still show up regardless of `--setting-sources`.** These are Claude Code's own built-in skills, present on any installation. Not contamination, not something to filter out, they're a constant baseline every measurement shares.

## A separate gotcha: reading this plugin's own bundled files

This only applies when actually *running* `debloat-scan`/`debloat-file` (not the measurement harness itself, which never invokes them). When the plugin is loaded ad hoc via `--plugin-dir <path>` for testing rather than properly installed, Claude Code's file-access sandbox for a `-p` session defaults to just the working directory. A skill's own bundled `references/checks.md` sits outside that boundary (in the plugin's install location, not the target project's directory) and reads get denied, confirmed directly: the skill ran without ever loading its checklist until `--add-dir <plugin-install-path>` was added alongside `--plugin-dir`. If testing this plugin via `--plugin-dir`, always also pass `--add-dir` pointing at the same path. A properly installed plugin (through a marketplace) may not need this, not independently verified.
