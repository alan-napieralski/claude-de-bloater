# Acme Storefront — Claude Context

@docs/style-guide.md

## What this is

A small e-commerce storefront: a product catalogue, a cart, and a checkout flow. Node backend, a
lightweight frontend, no framework lock-in.

## Rules that apply everywhere

- IMPORTANT: You MUST always reference the semantic colour token `bg-surface-primary` instead of a
  raw hex value in every CSS file.
- IMPORTANT: You MUST run `npm run lint` before considering any change complete.
- CRITICAL: You MUST never commit directly to `main`, always open a pull request.
- IMPORTANT: You MUST write tests for any new API route.
- CRITICAL: You MUST use 2-space indentation in every file.
- IMPORTANT: You MUST keep commit messages under 72 characters on the first line.
- CRITICAL: You MUST never log a customer's full card number, even in development.
- IMPORTANT: You MUST update `CHANGELOG.md` for any user-facing change.

## Commands

```bash
npm install
npm run dev
npm run build
npm run lint
```
