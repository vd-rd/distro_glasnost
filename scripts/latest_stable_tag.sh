#!/usr/bin/env bash
# Find the latest stable tag (no pre-release suffixes) in a remote git repo.
# Usage:
#   latest_stable_tag.sh <repo_url>
# Prints the tag to stdout; exits non-zero on failure.

set -euo pipefail

if [[ ${#} -lt 1 ]]; then
  echo "Usage: $0 <repo_url>" >&2
  exit 2
fi

REPO_URL="$1"

# Fetch all tags and normalize:
# - Take the second column (ref name)
# - Strip 'refs/tags/' prefix
# - Strip '^{}' (dereferenced annotated tags)
# - De-duplicate
# - Keep only tags starting with 'v' followed by numeric dot segments
#   Examples: v2025.01, v2023.07.01, v6.6.10, v6.7
#   Excludes: v2025.01-rc3, v6.7-rc4, v6.7-rc4^{}
LATEST_TAG=$(git ls-remote --tags "$REPO_URL" \
  | awk '{print $2}' \
  | sed 's#refs/tags/##' \
  | sed 's#\^\{\}##' \
  | sort -u \
  | grep -E '^v[0-9]+(\.[0-9]+)+$' \
  | sort -V \
  | tail -n1)

if [[ -z "${LATEST_TAG}" ]]; then
  echo "No stable tag found for repo: ${REPO_URL}" >&2
  exit 1
fi

printf "%s\n" "${LATEST_TAG}"