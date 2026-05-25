#!/usr/bin/env bash
# setup-claude-secrets.sh — populate macOS Keychain with Claude harness secrets.
#
# Reads a manifest of Keychain item names (one per line, blank lines and `#` comments
# skipped) and, for each item not already present, prompts interactively for the secret
# value and stores it via `security add-generic-password`.
#
# Idempotent: re-running only prompts for items that are still missing.
#
# Usage:
#   ./environment/setup-claude-secrets.sh <manifest-path>
#
# Example:
#   ./environment/setup-claude-secrets.sh ~/.claude/secrets-manifest.txt
#
# Each manifest entry is the `service` name passed to `security`; the account is the
# current user. Naming convention is `claude-mcp-<server>-<credential>` (e.g.
# `claude-mcp-notion-token`); see environment/claude-setup.md > Secret provisioning model.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <manifest-path>" >&2
  exit 2
fi

MANIFEST="$1"

if [[ ! -f "$MANIFEST" ]]; then
  echo "manifest not found: $MANIFEST" >&2
  exit 2
fi

# Tallies for the summary line.
already=0
added=0
skipped=0
failed=0

# Use process-substitution to keep the counters in the parent shell (a pipe would
# fork the loop into a subshell and discard the totals).
while IFS= read -r raw; do
  # Strip surrounding whitespace, then skip blanks and #-comments.
  item="${raw#"${raw%%[![:space:]]*}"}"
  item="${item%"${item##*[![:space:]]}"}"
  [[ -z "$item" || "$item" =~ ^# ]] && continue

  if security find-generic-password -s "$item" -a "$USER" >/dev/null 2>&1; then
    echo "  already present: $item"
    already=$((already + 1))
    continue
  fi

  # Missing — prompt the user. Read directly from the terminal so this works when
  # the script's stdin is the manifest file.
  if [[ -t 0 ]]; then
    prompt_src=/dev/tty
  else
    # Stdin isn't a terminal (rare; e.g. piped invocation). Fall back to /dev/tty
    # if available; otherwise skip with a clear message.
    if [[ -e /dev/tty ]]; then
      prompt_src=/dev/tty
    else
      echo "  SKIPPED (no terminal for prompt): $item" >&2
      skipped=$((skipped + 1))
      continue
    fi
  fi

  printf 'Enter value for %s (input hidden, blank to skip): ' "$item" > /dev/tty
  IFS= read -rs value < "$prompt_src" || value=""
  printf '\n' > /dev/tty

  if [[ -z "$value" ]]; then
    echo "  SKIPPED (no value entered): $item"
    skipped=$((skipped + 1))
    continue
  fi

  if security add-generic-password -s "$item" -a "$USER" -w "$value" -U >/dev/null 2>&1; then
    echo "  added: $item"
    added=$((added + 1))
  else
    echo "  FAILED to store: $item" >&2
    failed=$((failed + 1))
  fi

  # Scrub the value from the shell var as a small defense-in-depth measure.
  unset value
done < "$MANIFEST"

echo
echo "Summary: $already already present, $added added, $skipped skipped, $failed failed."

if (( failed > 0 )); then
  exit 1
fi
