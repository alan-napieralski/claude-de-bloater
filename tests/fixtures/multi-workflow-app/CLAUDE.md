# Notebook — a tiny static blog

Markdown posts in `posts/`, built into static HTML with `node build.js`, served from `dist/`. No CMS, no database, no client-side framework.

## Workflow

Drafting, reviewing, and publishing a post are three distinct steps, each with its own tooling: the `draft-post` skill for writing, the `editor` agent for review, and the `/publish` command for the actual build-and-deploy step. Do not skip straight to publishing without a draft existing in `posts/drafts/`.

## Commands

```bash
node build.js        # builds dist/ from posts/
node build.js --watch
```

## Front matter

Every post starts with YAML front matter: `title`, `date`, `tags` (an array, can be empty), `draft` (boolean). `build.js` skips any post with `draft: true`.
