# Fintrack — Claude Context

@docs/styles.md
@docs/backend.md

## What this is

Fintrack is a personal finance dashboard: accounts, transactions, budgets, reports.

## Rules that apply everywhere

- CRITICAL: You MUST always reference the semantic colour token `bg-surface-primary`, never a raw hex value.
- CRITICAL: You MUST run `npm run lint` before considering any change complete.
- CRITICAL: You MUST never commit directly to `main`.
- IMPORTANT: You MUST write tests for any new API route.
- CRITICAL: You MUST use 2-space indentation everywhere.
- IMPORTANT: You MUST keep commit messages under 72 characters.
- CRITICAL: You MUST never log a customer's account number, even in development.
- IMPORTANT: You MUST update `CHANGELOG.md` for any user-facing change.
- CRITICAL: You MUST validate every currency amount as an integer of minor units (cents), never a float.
- IMPORTANT: You MUST paginate any endpoint that could return more than 50 rows.
- CRITICAL: You MUST never round a currency amount before it reaches the database.
- IMPORTANT: You MUST prefix a feature branch with the ticket number.

## Commands

```bash
npm install
npm run dev
npm run build
npm run lint
```
