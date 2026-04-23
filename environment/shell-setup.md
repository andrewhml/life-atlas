# Shell + Terminal Setup (new workstation)

Bring a new macOS workstation to parity with the reference shell / terminal setup: Powerlevel10k on zsh, Ghostty with MesloLGS Nerd Font, two-line rainbow prompt with unique-prefix path truncation.

Config lives as snapshots under `~/Atlas/config/`; this doc is the restore direction (Atlas → `$HOME`).

## Prerequisites

- Homebrew installed
- `~/Atlas/` mounted (Google Drive for Desktop running and synced)
- Ghostty installed (from [ghostty.org](https://ghostty.org) — not reliably brew-cask-available)

## Steps

```sh
# 1. Theme + font
brew install powerlevel10k
brew install --cask font-meslo-lg-nerd-font

# 2. Restore shell config from Atlas
cp ~/Atlas/config/shell/zshrc ~/.zshrc
cp ~/Atlas/config/shell/p10k.zsh ~/.p10k.zsh

# 3. Restore terminal config from Atlas
mkdir -p ~/.config/ghostty
cp ~/Atlas/config/terminal/ghostty-config ~/.config/ghostty/config

# 4. Reload
exec zsh
```

## Verification

- Open a new Ghostty window (Cmd+Q then relaunch the first time, so font is picked up).
- Prompt renders in two lines, rainbow segments, with `andrewlee@<host>` visually distinct from the command.
- Path truncates as `~/w/p/life-atlas`-style (unique-prefix).
- `echo $''` shows a GitHub glyph, not a tofu rectangle — confirms the Nerd Font loaded.

## Ongoing sync

After editing any tracked dotfile on a workstation, snapshot forward into Atlas:

```sh
./environment/sync-shell-config.sh
```

To check drift without writing:

```sh
./environment/sync-shell-config.sh --check
```

The script is one-way (`$HOME` → Atlas). The restore direction above is manual by design — moving snapshots onto a new machine is a deliberate, first-time-only operation.

## Notes

- Do not symlink. Atlas lives on a cloud-sync daemon; shell startup should not depend on it.
- If `~/.zshrc` already has user-specific content on the target machine, merge by hand — the snapshot is a known-good baseline, not an overwrite.
- Non-macOS workstations need their own adaptation — the snapshots assume macOS paths (`/opt/homebrew/share/powerlevel10k/...`).
