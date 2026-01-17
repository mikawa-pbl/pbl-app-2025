#!/usr/bin/env bash

# Migration Integrity Check Script
# Checks if any existing migration files have been modified or deleted compared to the main branch.

set -Eeuo pipefail

TARGET_BRANCH="origin/main"
CURRENT_HEAD=$(git rev-parse HEAD)

# Verify if target branch exists
if ! git rev-parse --verify "$TARGET_BRANCH" >/dev/null 2>&1; then
  echo "Target branch $TARGET_BRANCH not found. Fetching..."
  git fetch origin main:refs/remotes/origin/main
fi

# Find merge base
MERGE_BASE=$(git merge-base "$TARGET_BRANCH" "$CURRENT_HEAD")

echo "Checking for modified or deleted migration files between $MERGE_BASE and $CURRENT_HEAD"

# Get list of Modified (M) or Deleted (D) files in this range
# Filter for paths matching '*/migrations/*.py'
# Exclude __init__.py
CHANGED_MIGRATIONS=$(git diff --name-status "$MERGE_BASE" "$CURRENT_HEAD" | \
  grep -E '^(M|D|R[0-9]{1,3}|C[0-9]{1,3})\s' | \
  grep '/migrations/.*\.py$' | \
  grep -v '__init__.py' || true)

if [ -n "$CHANGED_MIGRATIONS" ]; then
  echo "Error: The following existing migration files have been modified or deleted:"
  echo "$CHANGED_MIGRATIONS"
  echo ""
  echo "It is strictly forbidden to modify or delete migration files that have already been merged."
  echo "Please revert these changes and create a new migration file instead."
  exit 1
else
  echo "Migration integrity check passed. No existing migrations were modified or deleted."
fi