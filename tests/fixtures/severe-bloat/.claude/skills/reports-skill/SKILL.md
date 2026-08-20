---
name: financial-reports
description: Generates financial reports for Fintrack, spending breakdowns, budget progress, tax summaries, and net worth over time, in PDF, CSV, or on-screen form. Use when the user asks for a report, export, or summary of their finances.
tools: Read, Grep, Glob, Bash
---

# Financial reports

Generates every report type Fintrack offers.

## Spending breakdown

Groups transactions by category over a date range, defaulting to the current calendar month if none is given. Categories with no transactions in the range are omitted rather than shown as zero, a zero-row clutters the chart without adding information. Transfers between the user's own accounts are always excluded from spending, they are not spending, and including them double-counts money moving within the household.

Sort order is largest category first, unless the user asks for alphabetical. Show a percentage of total alongside the raw amount for every row.

## Budget progress

Compares actual spending per category against the budgeted amount for the current period. A category with no budget set is shown separately, under "unbudgeted", never silently folded into a catch-all. Over-budget categories are flagged, but never with alarming language, a calm "12% over" reads better than "WARNING: OVER BUDGET".

Carry-over budgets (where an unspent amount rolls into next month) need the carry-over amount added to the current period's budget before comparing, forgetting this step is the single most common mistake when building this report by hand.

## Tax summary

Groups transactions tagged as tax-deductible by their tax category (not their spending category, these are different taxonomies and a transaction can belong to only one tax category but any spending category). Always includes the transaction date, amount, tax category, and a note field if present, since a tax preparer needs the note for anything ambiguous.

Only transactions within the selected tax year are included, and the tax year boundary is configurable per user (not always the calendar year, some jurisdictions differ), read it from the user's settings rather than assuming January to December.

## Net worth over time

Sums all account balances (assets minus liabilities) at regular intervals across a date range, weekly for ranges under six months, monthly otherwise, to keep the chart readable. A closed account's balance is treated as zero from its closure date onward, not simply omitted, since omitting it would make net worth jump discontinuously at the boundary.

Currency conversion for multi-currency accounts happens at report-generation time using the current exchange rate, historical exchange rates are not tracked, so a net-worth-over-time chart is an approximation for users with foreign-currency accounts, and the report should say so in a footnote.

## Export formats

### PDF

Generated from an HTML template rendered server-side, never client-side, so the output is identical regardless of the user's browser. Includes the Fintrack logo, the report title, the date range, and a generation timestamp in the footer.

### CSV

One row per transaction (never per category or per period, even for a "summary" report, since CSV is for further processing in a spreadsheet, and a spreadsheet user wants the raw rows to pivot themselves). Column headers are always the first row, never omitted.

### On-screen

Interactive: category rows are expandable to show individual transactions, and every chart supports hovering for exact values. Loads incrementally for large date ranges rather than blocking on the full dataset.

## Scheduling

A user can schedule a report to be generated and emailed on a recurring basis (weekly, monthly). Scheduled reports always use PDF, never CSV or on-screen, since they need to render without a live session. A scheduled report that fails to generate (for example, a temporary database issue) is retried once after five minutes before notifying the user of the failure, silent retries beyond that would delay the user finding out something is actually wrong.

## Common mistakes to avoid

Do not include pending (not yet cleared) transactions in any report unless explicitly asked, they can still change or be reversed. Do not assume a household has only one currency. Do not forget that a refund is a negative transaction in the same category as the original purchase, not a separate "refunds" category, unless the user has explicitly configured refund tracking that way.
