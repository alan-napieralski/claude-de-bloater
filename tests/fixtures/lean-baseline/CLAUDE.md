# Weather CLI

A small command-line tool that fetches and formats weather data for a given city. Node, no build step, single entry point at `src/cli.js`.

## Commands

```bash
npm install
npm test
node src/cli.js "London"
```

## Conventions

- Errors from the weather API are caught and printed as a plain one-line message, never a raw stack trace, since this is a CLI a non-developer might run.
- The API key comes from the `WEATHER_API_KEY` environment variable, never hard-coded, and the CLI exits with a clear message if it's missing.

Detailed formatting rules load only when touching the formatter: see `.claude/rules/formatting.md`.
