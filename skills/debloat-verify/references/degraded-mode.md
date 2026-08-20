# Auth setup, and what breaks without it

The one-time `claude setup-token` step matters for **every** mode, not just real-turn. Confirmed directly, twice: without a valid `CLAUDE_CODE_OAUTH_TOKEN`, `/context`'s Memory Files and Custom Agents categories silently report `0` regardless of their real size, even though `/context` itself makes no real API call, costs nothing, and reports success either way. This isn't a display quirk that settles down, it was reproduced on demand by unsetting the token and reproduced again by setting it back. Since Memory Files is CLAUDE.md content, the single thing this whole plugin cares most about, an unauthenticated run can silently produce a report that looks complete but is wrong about the one number that matters most.

## One-time setup

```bash
claude setup-token
```

This prints a long-lived token. Export it from `~/.zshenv` specifically, not `~/.zshrc`:

```bash
echo 'export CLAUDE_CODE_OAUTH_TOKEN="paste-the-token-here"' >> ~/.zshenv
```

Confirmed directly why it has to be `~/.zshenv`: `~/.zshrc` is only loaded by interactive shells, and the non-interactive `claude -p` calls this harness makes don't load it, so the token stays invisible to them even after being correctly added to `~/.zshrc`. `~/.zshenv` is loaded unconditionally, by every shell invocation.

This is a real standing credential, not scoped to read-only use and not expiring the way a normal session does. Treat it like a password: don't share it, don't commit it anywhere. It draws on the same account/subscription as normal use, not a separate pay-per-use key.

## What happens without it

`run_harness.sh` checks for `CLAUDE_CODE_OAUTH_TOKEN` before doing anything, in every mode. Without it: Skills and plugin numbers are still reliable (confirmed, those categories are unaffected), but the report is stamped `"auth_available": false` with an explicit warning, and Memory Files/Custom Agents numbers should not be trusted. `--mode real-turn` fails outright rather than proceeding with numbers that would be meaningless without a real call. `--mode both` falls back to context-only, still carrying the same warning.

If you see `"auth_available": false` on a report you already have, don't try to salvage it, re-run after `claude setup-token`.

## Why real-turn mode still earns its (small, real) cost

Once auth is set up, `/context` alone is reliable for most measurements. Real-turn mode remains useful as a cross-check, and it's still the only way to see the actual cost of a custom agent duplicating content instead of referencing it, that cost only shows up inside the agent's own isolated context window when it's invoked, never in the parent session's `/context`.
