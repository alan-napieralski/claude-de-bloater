#!/usr/bin/env bash
# Bumps the plugin version, commits it, and pushes; CI does the tagging and the release.
set -euo pipefail

cd "$(dirname "$0")/.."

MANIFEST=".claude-plugin/plugin.json"
BUMP="${1:-patch}"

if [ -n "$(git status --porcelain)" ]; then
  echo "error: working tree is dirty, commit or stash first" >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" != "main" ]; then
  echo "error: on branch '$BRANCH', releases are cut from main" >&2
  exit 1
fi

git fetch --quiet origin main --tags
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  echo "error: local main and origin/main have diverged, sync first" >&2
  exit 1
fi

NEW_VERSION="$(BUMP="$BUMP" MANIFEST="$MANIFEST" python3 - <<'PY'
import json, os, re, sys

manifest = os.environ["MANIFEST"]
bump = os.environ["BUMP"]
current = json.load(open(manifest))["version"]

if re.fullmatch(r"\d+\.\d+\.\d+", bump):
    new = bump
elif bump in ("patch", "minor", "major"):
    major, minor, patch = (int(p) for p in current.split("."))
    if bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    new = f"{major}.{minor}.{patch}"
else:
    sys.exit(f"error: expected patch, minor, major, or an explicit X.Y.Z, got '{bump}'")

raw = open(manifest).read()
updated, count = re.subn(r'("version":\s*")%s(")' % re.escape(current), r"\g<1>%s\g<2>" % new, raw, count=1)
if count != 1:
    sys.exit("error: could not rewrite the version field in " + manifest)
open(manifest, "w").write(updated)
print(new)
PY
)"

NAME="$(python3 -c 'import json;print(json.load(open(".claude-plugin/plugin.json"))["name"])')"
TAG="${NAME}--v${NEW_VERSION}"

if git rev-parse -q --verify "refs/tags/$TAG" > /dev/null; then
  git checkout -- "$MANIFEST"
  echo "error: $TAG already exists" >&2
  exit 1
fi

claude plugin validate . --strict

git add "$MANIFEST"
git commit --quiet --message "Release v${NEW_VERSION}"
git push --quiet origin main

echo "Pushed v${NEW_VERSION}. CI will validate, create $TAG, and publish the release."
