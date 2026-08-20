# Tip Calculator

A single static HTML page: enter a bill amount and a tip percentage, see the tip and total. No build step, no framework, no backend.

## Files

- `index.html`: markup and the calculation script, inline, since the whole app is small enough that splitting it out would be the actual over-engineering.
- `style.css`: styling.

## Conventions

Round the tip and total to two decimal places for display, but keep the underlying calculation unrounded until the final display step, so splitting the bill across several people doesn't compound rounding error.
