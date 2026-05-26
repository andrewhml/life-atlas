#!/usr/bin/env bash
# sync-shell-config.sh — snapshot live shell / terminal dotfiles into Atlas.
#
# One-way: $HOME → ~/Atlas/config/{shell,terminal}/
# Run after editing any of the tracked dotfiles.
#
# Usage:
#   ./environment/sync-shell-config.sh          Copy forward (source of truth = $HOME).
#   ./environment/sync-shell-config.sh --check  Report drift only; exit 1 if any file differs.

set -euo pipefail

ATLAS_SHELL="$HOME/Atlas/config/shell"
ATLAS_TERMINAL="$HOME/Atlas/config/terminal"

# src|dest pairs. $HOME is the source of truth.
# ~/.ssh/ is allowlisted to `config` ONLY — never snapshot keys, known_hosts,
# or any other file under ~/.ssh/. Guard below enforces this.
PAIRS=(
  "$HOME/.zprofile|$ATLAS_SHELL/zprofile"
  "$HOME/.zshrc|$ATLAS_SHELL/zshrc"
  "$HOME/.zshenv|$ATLAS_SHELL/zshenv"
  "$HOME/.p10k.zsh|$ATLAS_SHELL/p10k.zsh"
  "$HOME/.gitconfig|$ATLAS_SHELL/gitconfig"
  "$HOME/.ssh/config|$ATLAS_SHELL/ssh-config"
  "$HOME/.config/ghostty/config|$ATLAS_TERMINAL/ghostty-config"
)

# Safety guard: refuse to snapshot anything under ~/.ssh/ other than `config`.
# Allowlist (not blocklist) so a novel sensitive filename can't slip through.
for pair in "${PAIRS[@]}"; do
  src="${pair%%|*}"
  case "$src" in
    "$HOME/.ssh/"*)
      if [[ "$src" != "$HOME/.ssh/config" ]]; then
        echo "REFUSE: $src — only ~/.ssh/config is snapshot-eligible" >&2
        exit 2
      fi
      ;;
  esac
done

CHECK_ONLY=0
if [[ "${1:-}" == "--check" ]]; then
  CHECK_ONLY=1
elif [[ -n "${1:-}" ]]; then
  echo "unknown arg: $1" >&2
  echo "usage: $0 [--check]" >&2
  exit 2
fi

mkdir -p "$ATLAS_SHELL" "$ATLAS_TERMINAL"

drift=0
for pair in "${PAIRS[@]}"; do
  src="${pair%%|*}"
  dest="${pair##*|}"

  if [[ ! -f "$src" ]]; then
    echo "  missing source: $src (skipping)"
    continue
  fi

  if [[ -f "$dest" ]] && cmp -s "$src" "$dest"; then
    echo "  up to date: $dest"
    continue
  fi

  drift=1
  if (( CHECK_ONLY )); then
    if [[ -f "$dest" ]]; then
      echo "  DRIFT: $src differs from $dest"
    else
      echo "  DRIFT: $dest does not exist yet"
    fi
  else
    cp "$src" "$dest"
    echo "  copied: $src → $dest"
  fi
done

if (( CHECK_ONLY )) && (( drift )); then
  echo "drift detected — run without --check to sync"
  exit 1
fi

echo "done."
