#!/usr/bin/env python3
"""Bumps the plugin version, commits it, and pushes; CI does the tagging and the release."""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"


def run(*args, capture=False):
    result = subprocess.run(args, cwd=REPO_ROOT, capture_output=capture, text=True)
    if result.returncode != 0:
        if capture and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip() if capture else None


def bump_version(current, bump):
    if re.fullmatch(r"\d+\.\d+\.\d+", bump):
        return bump
    if bump not in ("patch", "minor", "major"):
        sys.exit(f"error: expected patch, minor, major, or an explicit X.Y.Z, got '{bump}'")
    major, minor, patch = (int(p) for p in current.split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main():
    bump = sys.argv[1] if len(sys.argv) > 1 else "patch"

    if run("git", "status", "--porcelain", capture=True):
        sys.exit("error: working tree is dirty, commit or stash first")

    branch = run("git", "rev-parse", "--abbrev-ref", "HEAD", capture=True)
    if branch != "main":
        sys.exit(f"error: on branch '{branch}', releases are cut from main")

    run("git", "fetch", "--quiet", "origin", "main", "--tags")
    local = run("git", "rev-parse", "HEAD", capture=True)
    remote = run("git", "rev-parse", "origin/main", capture=True)
    if local != remote:
        local_ahead = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"], cwd=REPO_ROOT
        ).returncode == 0
        remote_ahead = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], cwd=REPO_ROOT
        ).returncode == 0
        if local_ahead:
            sys.exit("error: local main is ahead of origin/main, push first: git push origin main")
        if remote_ahead:
            sys.exit("error: origin/main is ahead of local main, pull first: git pull origin main")
        sys.exit("error: local main and origin/main have diverged, rebase or merge, then push")

    manifest_data = json.loads(MANIFEST.read_text())
    current = manifest_data["version"]
    new = bump_version(current, bump)

    raw = MANIFEST.read_text()
    updated, count = re.subn(
        r'("version":\s*")%s(")' % re.escape(current), r"\g<1>%s\g<2>" % new, raw, count=1
    )
    if count != 1:
        sys.exit(f"error: could not rewrite the version field in {MANIFEST}")

    name = manifest_data["name"]
    tag = f"{name}--v{new}"
    tag_exists = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"], cwd=REPO_ROOT, capture_output=True
    ).returncode == 0
    if tag_exists:
        sys.exit(f"error: {tag} already exists")

    MANIFEST.write_text(updated)
    run("claude", "plugin", "validate", ".", "--strict")

    run("git", "add", str(MANIFEST))
    run("git", "commit", "--quiet", "--message", f"Release v{new}")
    run("git", "push", "--quiet", "origin", "main")

    print(f"Pushed v{new}. CI will validate, create {tag}, and publish the release.")


if __name__ == "__main__":
    main()
