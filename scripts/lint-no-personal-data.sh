#!/usr/bin/env bash
# lint-no-personal-data.sh — block personal-data tokens from entering this repo.
#
# Reads regex patterns (one per line, `#` comments and blank lines ignored)
# from the deny-list at
#   ${LINT_DENYLIST:-$HOME/Atlas/config/atlas/lint-denylist.txt}
# and greps repo content for matches.
#
# Patterns are passed straight to `grep -E` — no wrapping. The deny-list
# author picks the right shape per token:
#   - word-like (codenames):  \bWORD\b
#   - path-like (user-home, mount points):  /Users/example
#   - email-like:  example\.user@example\.com
# See scripts/lint-denylist.example.txt for the seed template.
#
# This script intentionally contains NO personal tokens. The real deny-list
# lives outside this repo (cloud-synced via Atlas across the user's devices).
#
# Usage:
#   bash scripts/lint-no-personal-data.sh             # lint the working tree (all tracked files)
#   bash scripts/lint-no-personal-data.sh --staged    # lint staged content (use in pre-commit hook)
#
# Override the deny-list path (e.g. for testing):
#   LINT_DENYLIST=/some/other/file.txt bash scripts/lint-no-personal-data.sh

set -euo pipefail

DENYLIST="${LINT_DENYLIST:-$HOME/Atlas/config/atlas/lint-denylist.txt}"

if [[ ! -f "$DENYLIST" ]]; then
  echo "ERROR: deny-list not found at: $DENYLIST" >&2
  echo "" >&2
  echo "The real deny-list is private (lives in your Atlas cloud-synced config)." >&2
  echo "Seed it from the example template:" >&2
  echo "  mkdir -p \"\$(dirname \"$DENYLIST\")\"" >&2
  echo "  cp scripts/lint-denylist.example.txt \"$DENYLIST\"" >&2
  echo "Then replace the EXAMPLE_* placeholders with your actual tokens." >&2
  exit 1
fi

MODE="working-tree"
if [[ "${1:-}" == "--staged" ]]; then
  MODE="staged"
elif [[ -n "${1:-}" ]]; then
  echo "unknown arg: $1" >&2
  echo "usage: $0 [--staged]" >&2
  exit 2
fi

# Build a single ERE alternation from non-comment, non-blank lines.
# Per-pattern iteration would be cleaner but N× slower on a large tree.
PATTERN=""
while IFS= read -r raw || [[ -n "$raw" ]]; do
  line="${raw#"${raw%%[![:space:]]*}"}"      # ltrim
  [[ -z "$line" ]] && continue
  [[ "${line:0:1}" == "#" ]] && continue     # comment
  line="${line%"${line##*[![:space:]]}"}"    # rtrim
  if [[ -z "$PATTERN" ]]; then
    PATTERN="$line"
  else
    PATTERN="$PATTERN|$line"
  fi
done < "$DENYLIST"

if [[ -z "$PATTERN" ]]; then
  echo "ERROR: deny-list contains no patterns: $DENYLIST" >&2
  exit 1
fi

# Resolve target file list.
if [[ "$MODE" == "staged" ]]; then
  mapfile -t TARGETS < <(git diff --cached --name-only --diff-filter=ACMR)
else
  mapfile -t TARGETS < <(git ls-files)
fi

if (( ${#TARGETS[@]} == 0 )); then
  echo "no files to lint (mode: $MODE)"
  exit 0
fi

# Self-exclude the engine and the example template — both contain regex
# fragments that, while not personal tokens themselves, could occasionally
# create confusion if a future author embeds tokens in a doctest.
HITS=0
for f in "${TARGETS[@]}"; do
  case "$f" in
    scripts/lint-no-personal-data.sh) continue ;;
    scripts/lint-denylist.example.txt) continue ;;
  esac
  if [[ "$MODE" == "staged" ]]; then
    # Read the STAGED blob, not the working tree — closes the partial-stage
    # bypass where a clean working tree could hide a tainted staged version.
    content="$(git show ":$f" 2>/dev/null)" || continue
    matches=$(printf '%s\n' "$content" | grep -nE -e "$PATTERN" || true)
  else
    [[ -f "$f" ]] || continue
    matches=$(grep -nE -e "$PATTERN" "$f" 2>/dev/null || true)
  fi
  if [[ -n "$matches" ]]; then
    while IFS= read -r m; do
      echo "$f:$m"
      HITS=$((HITS + 1))
    done <<< "$matches"
  fi
done

if (( HITS > 0 )); then
  echo "" >&2
  echo "lint failed: $HITS hit(s) against deny-list at $DENYLIST" >&2
  echo "Resolve by either (a) sanitizing the leak, or (b) adjusting the deny-list" >&2
  echo "if the match is a genuine false positive." >&2
  exit 1
fi

echo "lint passed: no deny-list hits across ${#TARGETS[@]} files (mode: $MODE)"
