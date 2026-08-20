# Publish checklist

**This is the spec for the `publish-reviewer` agent.** Read it in full before every review and apply
it exactly.

## How to review

1. Read `manifest.json` for the list of pages due to publish.
2. Run `npm run build` and confirm it exits clean.
3. Check every page in the manifest has a title, a meta description, and at least one internal link.
4. Confirm no page links to a draft still under `content/drafts/`.

## Reporting

List every page that fails a check, one line each, with the check it failed and the fix. End with a
single verdict: ready to publish, yes or no.

Be thorough: a page that looks fine visually can still fail silently on a missing meta description,
so check every item on every page rather than spot-checking a few.
