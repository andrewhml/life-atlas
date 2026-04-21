#!/bin/bash

# macOS Defaults Settings
#
# Status: pending. Applies preferred macOS system defaults.
# See macos_defaults.md for the documented list and rationale.
#
# Script must be idempotent: `defaults write` is idempotent by nature,
# but any filesystem operations added here must use `mkdir -p`,
# existence checks, etc.

set -e

echo "defaults_settings.sh is a stub. Populate with defaults write commands."
exit 0

# TODO
# - Dock: autohide, tilesize, orientation
# - Finder: show hidden files, path bar, status bar, default view
# - Keyboard: key repeat, initial repeat delay
# - Trackpad: tap to click, three-finger drag
# - Screenshots: default location, format, disable shadow
# - Global: dark mode, accent color, menu bar settings
