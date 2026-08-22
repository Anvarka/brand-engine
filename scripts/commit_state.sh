#!/usr/bin/env bash
# Commit whatever the pipeline changed. Workflows run concurrently only by accident
# (manual dispatch during a scheduled run), so a rebase retry is enough.
set -euo pipefail

message="${1:-brand-engine: state update}"

git config user.name "brand-engine[bot]"
git config user.email "brand-engine@users.noreply.github.com"

git add -A content data
if git diff --cached --quiet; then
  echo "nothing to commit"
  exit 0
fi

git commit -m "$message"

for attempt in 1 2 3; do
  if git push; then
    echo "pushed on attempt $attempt"
    exit 0
  fi
  echo "push rejected, rebasing (attempt $attempt)"
  git pull --rebase --autostash
done

echo "could not push after 3 attempts" >&2
exit 1
