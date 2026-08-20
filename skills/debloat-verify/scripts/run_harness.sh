#!/usr/bin/env bash
# Measures a target project's Claude Code context footprint: the free /context breakdown,
# and optionally real usage.input_tokens from canary prompts. See ../references/isolation.md
# for why --setting-sources project is used and ../references/degraded-mode.md for what
# happens when CLAUDE_CODE_OAUTH_TOKEN isn't set.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET=""
CONFIG_LABEL="config"
MATRIX="one-shot,brief,workflow"
REPEATS_WORKFLOW=3
MODE="context-only"
OUT="/dev/stdout"
CANARY_DIR=""

usage() {
  cat >&2 <<'EOF'
Usage: run_harness.sh --target <path> [options]

Options:
  --target <path>            Directory to measure (required). Its own CLAUDE.md/.claude/**
                              are what gets measured, the operator's personal global config
                              is excluded via --setting-sources project.
  --config <label>           A label for this run, e.g. "baseline" or "candidate" (default: config)
  --matrix <cells>           Comma-separated cell names, each read from
                              <canary-dir>/<cell>.txt (default: one-shot,brief,workflow).
                              gen_manual_context_invoke.py prints "manual-context-invoke" to add
                              here once its prompt exists on disk.
  --repeats-workflow <n>     Repeats for the workflow cell only (default: 3). One-shot and
                              brief always run once, a fixed prompt against a fixed config
                              gives a deterministic size reading, repeats only matter where
                              the model's actual behaviour can vary run to run.
  --mode <mode>               context-only | real-turn | both (default: context-only)
  --canary-dir <path>         Directory to read cell prompts from (default: this script's own
                              canary_prompts/). Point this at gen_manual_context_invoke.py's
                              output directory to run generated cells alongside or instead of the
                              bundled ones.
  --out <path>                Where to write the JSON report (default: stdout)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --config) CONFIG_LABEL="$2"; shift 2 ;;
    --matrix) MATRIX="$2"; shift 2 ;;
    --repeats-workflow) REPEATS_WORKFLOW="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --canary-dir) CANARY_DIR="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$CANARY_DIR" ]]; then
  CANARY_DIR="$SCRIPT_DIR/canary_prompts"
fi

if [[ -z "$TARGET" ]]; then
  echo "Error: --target is required" >&2
  usage
  exit 1
fi
if [[ ! -d "$TARGET" ]]; then
  echo "Error: target directory does not exist: $TARGET" >&2
  exit 1
fi

# First-run auth check. Confirmed directly (not just for real-turn mode): /context's Memory
# Files and Custom Agents categories silently report 0, even though the command itself makes
# no real API call and reports success, whenever CLAUDE_CODE_OAUTH_TOKEN isn't set. So this
# check runs regardless of --mode, context-only mode's accuracy depends on it too. See
# ../references/degraded-mode.md for the full explanation and the one-time fix.
AUTH_AVAILABLE=0
if [[ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
  AUTH_AVAILABLE=1
fi

if [[ "$AUTH_AVAILABLE" -eq 0 ]]; then
  if [[ "$MODE" == "real-turn" ]]; then
    echo "Error: real-turn mode needs CLAUDE_CODE_OAUTH_TOKEN set. Run 'claude setup-token'," >&2
    echo "then export the printed token from ~/.zshenv (not ~/.zshrc). See references/degraded-mode.md." >&2
    exit 1
  fi
  echo "Warning: CLAUDE_CODE_OAUTH_TOKEN not set. Skills/plugins numbers are still reliable, but" >&2
  echo "Memory Files and Custom Agents will silently read as 0 regardless of their real size," >&2
  echo "confirmed directly, this is not a display quirk, it will misreport CLAUDE.md content as free." >&2
  echo "Run 'claude setup-token' before trusting any Memory Files number (references/degraded-mode.md)." >&2
  if [[ "$MODE" == "both" ]]; then
    echo "Continuing in context-only mode only (real-turn needs the same token, for a different reason)." >&2
    MODE="context-only"
  fi
fi

TMP_RAW_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_RAW_DIR"' EXIT

IFS=',' read -ra CELLS <<< "$MATRIX"

if [[ "$MODE" == "context-only" || "$MODE" == "both" ]]; then
  (cd "$TARGET" && claude -p "/context" --output-format json --no-session-persistence --setting-sources project) \
    > "$TMP_RAW_DIR/context.json" 2>&1
fi

if [[ "$MODE" == "real-turn" || "$MODE" == "both" ]]; then
  for cell in "${CELLS[@]}"; do
    prompt_file="$CANARY_DIR/${cell}.txt"
    if [[ ! -f "$prompt_file" && "$CANARY_DIR" != "$SCRIPT_DIR/canary_prompts" ]]; then
      # Fall back to the bundled prompts so a generated --canary-dir (e.g.
      # gen_manual_context_invoke.py's output, which only contains manual-context-invoke.txt) can
      # still be combined with the default one-shot/brief/workflow cells without copying those
      # files alongside it.
      prompt_file="$SCRIPT_DIR/canary_prompts/${cell}.txt"
    fi
    if [[ ! -f "$prompt_file" ]]; then
      echo "Warning: no canary prompt for cell '$cell', skipping" >&2
      continue
    fi
    if [[ "$cell" == "workflow" ]]; then
      repeats="$REPEATS_WORKFLOW"
    else
      repeats=1
    fi
    for i in $(seq 1 "$repeats"); do
      (cd "$TARGET" && claude -p "$(cat "$prompt_file")" --output-format json --no-session-persistence --setting-sources project) \
        > "$TMP_RAW_DIR/realturn_${cell}_${i}.json" 2>&1
    done
  done
fi

python3 "$SCRIPT_DIR/parse_context.py" "$TMP_RAW_DIR" "$CONFIG_LABEL" "$MODE" "$OUT" "$AUTH_AVAILABLE"
