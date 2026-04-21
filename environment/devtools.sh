#!/bin/bash

# Developer Tools Bootstrap
#
# Status: pending. Installs developer tools and CLI utilities.
# Complements `Brewfile` (see brewfile.md). This script covers what
# cannot be expressed as a Homebrew formula (e.g., direct curl installs,
# version managers, vscode extension bulk install outside the Brewfile).
#
# Script must be idempotent: check-before-install for every step.

set -e

echo "devtools.sh is a stub. Populate with non-Brewfile dev-tool installs."
exit 0

# TODO
# - Node version manager (nvm / fnm / volta) — bootstrap
# - Python version manager (pyenv / uv)
# - Rust (rustup)
# - Global npm / pnpm / pip tools not already in Brewfile
# - VS Code extensions not captured in Brewfile (if any)
# - Git global config and hooks
# - Shell completions
