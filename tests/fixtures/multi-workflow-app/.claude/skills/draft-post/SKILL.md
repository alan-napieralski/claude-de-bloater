---
name: draft-post
description: Drafts a new blog post for Notebook as a markdown file with correct front matter, in posts/drafts/. Use when the user wants to write, start, or draft a new blog post.
tools: Read, Write, Glob
---

# Draft a post

Create `posts/drafts/<slug>.md`, slug is the title lowercased with spaces replaced by hyphens.

Front matter first: `title`, `date` (today), `tags` (ask if unclear, default to an empty array), `draft: true`. Body follows a blank line after the closing `---`.

Write in the author's usual voice: short paragraphs, no more than one idea per paragraph, a concrete example over an abstract claim wherever possible.
