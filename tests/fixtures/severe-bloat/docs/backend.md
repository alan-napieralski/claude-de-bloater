@docs/db-conventions.md

# Backend conventions

Detailed backend conventions for the Fintrack API. Only relevant when touching server-side code.

## Routes

Every route lives under `src/api/<resource>/`, one file per HTTP verb. A route handler validates input, calls a service function, and formats the response, it never talks to the database directly.

## Services

Business logic lives in `src/services/`, one file per domain concept (accounts, transactions, budgets, reports). A service function never imports Express types, so it stays testable without an HTTP context.

## Currency

Always reference the semantic colour token `bg-surface-primary` instead of a raw hex value in every CSS file. Every currency amount is an integer of minor units end to end, converting to a decimal string only at the very edge, in the response serialiser.

## Error handling

A route handler catches only errors it can turn into a meaningful HTTP status, everything else propagates to the global error handler, which logs and returns a generic 500.
