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

# 2. Restore shell config from Atlas (three zsh files + p10k theme)
cp ~/Atlas/config/shell/zprofile ~/.zprofile   # login-shell env (PATH, brew shellenv)
cp ~/Atlas/config/shell/zshrc    ~/.zshrc      # interactive UX (prompt, completion, aliases)
cp ~/Atlas/config/shell/zshenv   ~/.zshenv     # every-shell env (LANG, EDITOR)
cp ~/Atlas/config/shell/p10k.zsh ~/.p10k.zsh

# 3. Restore git + ssh config from Atlas
#    Keys + known_hosts are NOT snapshotted — generate fresh on each machine.
cp ~/Atlas/config/shell/gitconfig  ~/.gitconfig
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cp ~/Atlas/config/shell/ssh-config ~/.ssh/config
chmod 600 ~/.ssh/config

# 4. Restore terminal config from Atlas
mkdir -p ~/.config/ghostty
cp ~/Atlas/config/terminal/ghostty-config ~/.config/ghostty/config

# 5. Reload
exec zsh
```

## Per-machine bootstrap (not snapshotted)

Keys and signing material never leave the host, so each new workstation generates them fresh after the restore above. The gitconfig snapshot assumes the paths below.

```sh
# SSH key for GitHub + commit signing
ssh-keygen -t ed25519 -C "<your-email>" -f ~/.ssh/id_ed25519
ssh-add --apple-use-keychain ~/.ssh/id_ed25519

# allowed_signers — needed for `git log --show-signature` to verify SSH-signed commits
echo "<your-email> $(cat ~/.ssh/id_ed25519.pub)" > ~/.ssh/allowed_signers

# Add the .pub key to GitHub (both Authentication AND Signing key types)
gh ssh-key add ~/.ssh/id_ed25519.pub --type authentication
gh ssh-key add ~/.ssh/id_ed25519.pub --type signing
```

If the `~/.gitconfig` snapshot has hardcoded `/Users/<other-user>/...` paths in `signingkey` or `allowedSignersFile`, update them to point at this machine's `$HOME`.

## Verification

- Open a new Ghostty window (Cmd+Q then relaunch the first time, so font is picked up).
- Prompt renders in two lines, rainbow segments, with `<user>@<host>` visually distinct from the command.
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
