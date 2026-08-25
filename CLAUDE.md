# claude-de-bloater

A Claude Code plugin (pure markdown skills, no runtime dependencies) that audits a project's Claude Code context surface for token-budget problems. See [README.md](README.md) for what it does and how it's structured.

## Commit messages are load-bearing

Releases are automated by [release-please](https://github.com/googleapis/release-please): it parses commit messages on `main` to decide the version bump and to write `CHANGELOG.md`. Every commit merged to `main` must be [Conventional Commits](https://www.conventionalcommits.org/), or it silently produces the wrong version or no release at all.

| Prefix | Bump | Changelog section |
|---|---|---|
| `fix:` | patch | Bug Fixes |
| `feat:` | minor | Features |
| `feat!:` / `fix!:` / a `BREAKING CHANGE:` footer | major | ⚠ BREAKING CHANGES |
| `chore:`, `docs:`, `refactor:`, `style:`, `test:`, `build:`, `ci:` | none | not shown |

Rules:

- One logical change per commit, prefix matches the change's actual user-facing effect, not what's convenient (a behaviour change is `feat`/`fix` even if the diff is one line; a large refactor with no behaviour change is `refactor`, not `feat`).
- Scope is optional: `feat(skills): ...` is fine but not required.
- Subject line is imperative, present tense, no trailing period: `fix: handle missing frontmatter`, not `fixed` or `fixes`.
- Never hand-edit `version.txt`, `.claude-plugin/plugin.json`'s `version` field, `.release-please-manifest.json`, or `CHANGELOG.md` — release-please owns all four. If a version looks wrong, fix the commit history, not these files.

Full release mechanics (the release PR, tagging, CI jobs) are documented in [README.md](README.md#releasing) — don't restate them here.
