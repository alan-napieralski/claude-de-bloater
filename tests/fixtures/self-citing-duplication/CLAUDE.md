# PageForge — Claude Context

A small static-site publishing tool. Pages are authored in `content/`, built with `npm run build`,
and pushed live by a `publish` script once approved.

## Before publishing

Every batch is checked against `docs/publish-checklist.md` by the `publish-reviewer` agent before
the publish script runs. See that file for the actual review standard.

## Commands

```bash
npm install
npm run build
npm run publish
```
