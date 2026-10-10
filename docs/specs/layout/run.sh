#!/usr/bin/env bash
# Runs a layout/lighthouse checker in the pinned Playwright image as the calling user.
# Usage: bash docs/specs/layout/run.sh check_layout.mjs [args...]
#        bash docs/specs/layout/run.sh lighthouse.mjs [args...]
# The site root (repo root) is mounted at /site; node_modules must already be
# installed in docs/specs/layout (npm ci, see the spec).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../.." && pwd)
test -d "$here/node_modules/playwright" || { echo "нет $here/node_modules — npm ci не выполнен" >&2; exit 2; }
script=$1; shift
exec docker run --rm --init --ipc=host -u "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$repo":/site -w /site/docs/specs/layout \
  mcr.microsoft.com/playwright:v1.64.0-noble node "$script" --root /site "$@"
