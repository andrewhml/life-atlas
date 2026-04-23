# Plan 0003 — zsh prompt setup (Powerlevel10k + Atlas sync)

**Status:** In Progress
**Issue:** — (create on session-end)
**Created:** 2026-04-22

---

## Goal

Replace the default macOS zsh prompt (uncolored, hard to visually separate prompt from command) with a Powerlevel10k two-line prompt that:

- Makes `andrewlee@AM2` visually distinct from the command being typed
- Uses unique-prefix path truncation for scannable directory context
- Uses an emoji prompt character so the cursor location is instantly findable
- Surfaces git state, exit codes, and command timing automatically
- Lives in `~/Atlas/config/shell/` via symlink, so it survives machine swaps

## Background

User previously had a p10k config on an old Mac, lost in a machine transition — no backup surfaced. Starting from scratch is fine; the shell config needs to live in Atlas from the start so this doesn't recur.

Current prompt is literally the zsh default (`%n@%m %1~ %#`) — emits zero color codes. No terminal theme will make it more legible; the fix is shell-side.

## Current state (as of 2026-04-22, pause point)

**Done (Phase 1 complete):**
- Powerlevel10k installed at `/opt/homebrew/share/powerlevel10k/powerlevel10k.zsh-theme` (was already there from earlier session)
- Meslo Nerd Font installed via `brew install --cask font-meslo-lg-nerd-font`; `fc-list` confirms `MesloLGS Nerd Font` available
- `~/.zshrc` wired with two lines (see deviation below):
  ```zsh
  source /opt/homebrew/share/powerlevel10k/powerlevel10k.zsh-theme
  [[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
  ```
- Ghostty config at `~/.config/ghostty/config` matches canonical content in Phase 1e

**Deviation from original Phase 1d:** The plan specified only the first `source` line. The second line (guard-source of `~/.p10k.zsh`) was added per the official p10k README — without it, wizard output goes to `~/.p10k.zsh` but is never loaded. The guard makes it safe before the wizard runs. Do NOT re-append on resume.

**Not yet done:**
- Restart Ghostty + walk wizard (Phase 1f + Phase 2)
- Post-wizard customize: unique path + emoji prompt char (Phase 3)
- Move zshrc + p10k.zsh + ghostty config to `~/Atlas/config/` and symlink (Phase 4)
- Update `folder-schemas/config.md` (Phase 5)
- Document new-machine setup (Phase 6)

**Resume here** — Cmd+Q Ghostty, relaunch, verify Nerd Font icons render (`echo ''` should show GitHub icon not tofu), then walk the wizard per Phase 2. If wizard doesn't auto-launch, run `p10k configure`. Note the wizard will prepend an "instant prompt" block to `~/.zshrc` — expected.

## Phases

### Phase 1 — Install

#### 1a. Verify (run first on resume — skip steps already done)

```sh
# Confirms font cask installed
fc-list | grep -i meslo
# Confirms p10k installed
ls /opt/homebrew/share/powerlevel10k/powerlevel10k.zsh-theme
# Confirms zshrc sources p10k
grep powerlevel10k ~/.zshrc
# Confirms Ghostty config exists and has font/theme
cat ~/.config/ghostty/config
```

If `fc-list | grep -i meslo` is empty → run step 1b.
If the `ls` fails → run step 1c.
If `grep powerlevel10k` is empty → run step 1d.
If the `cat` fails → run step 1e (recreate config from the canonical content below).

#### 1b. Install font

```sh
brew install --cask font-meslo-lg-nerd-font
```

#### 1c. Install Powerlevel10k

```sh
brew install powerlevel10k
```

#### 1d. Wire p10k into zsh

```sh
echo 'source /opt/homebrew/share/powerlevel10k/powerlevel10k.zsh-theme' >> ~/.zshrc
```

(Do not `exec zsh` yet — do that after Ghostty is restarted with the right font.)

#### 1e. Canonical Ghostty config

The Ghostty config at `~/.config/ghostty/config` should contain the following. If missing, recreate with `open -e ~/.config/ghostty/config` and paste:

```
# ── Font ──────────────────────────────────────────
font-family = MesloLGS Nerd Font
font-size = 14

# ── Theme ─────────────────────────────────────────
# Run `ghostty +list-themes` to browse. Swap freely.
theme = Horizon

# ── Cursor ────────────────────────────────────────
cursor-style = block
cursor-style-blink = true

# ── Window ────────────────────────────────────────
window-padding-x = 8
window-padding-y = 8
window-save-state = always
background-opacity = 1.0
macos-titlebar-style = tabs

# ── Quality of life ───────────────────────────────
copy-on-select = clipboard
mouse-hide-while-typing = true
confirm-close-surface = false

# ── Scrollback ────────────────────────────────────
scrollback-limit = 10000000

# ── macOS behavior ────────────────────────────────
macos-option-as-alt = true
macos-non-native-fullscreen = visible-menu
quit-after-last-window-closed = true

# ── Readability ───────────────────────────────────
adjust-cell-height = 10%

# ── Splits ────────────────────────────────────────
unfocused-split-opacity = 0.7
```

#### 1f. Restart Ghostty

Cmd+Q to fully quit (not just close window), then relaunch. Verify icons render (not tofu/boxes) by running `echo $''` — should show a GitHub icon, not a rectangle.

Wizard launches automatically on next shell load; if not, run `p10k configure`.

### Phase 2 — Wizard choices

Walk the wizard with these answers (optimized for legibility + the stated preferences):

| Question | Answer |
|---|---|
| Glyph tests (diamond, lock, debian, etc.) | Yes to all |
| Prompt Style | Rainbow |
| Character set | Unicode |
| Show current time | User choice (24-hour or none) |
| Prompt Separators | Angled |
| Prompt Heads | Sharp |
| Prompt Tails | Flat |
| Prompt Height | **Two lines** (critical — command gets its own line) |
| Prompt Connection | Disconnected or Dotted |
| Prompt Frame | No frame |
| Prompt Spacing | Sparse |
| Icons | Many icons |
| Prompt Flow | Fluent |
| Enable Transient Prompt | **Yes** (old prompts collapse on scrollback) |
| Instant Prompt | Verbose |
| Overwrite `~/.p10k.zsh`? | Yes |

### Phase 3 — Post-wizard customizations

Edit `~/.p10k.zsh` (not yet symlinked to Atlas — do that in Phase 4):

**Unique-prefix path truncation** — find `POWERLEVEL9K_SHORTEN_STRATEGY`, set:
```zsh
typeset -g POWERLEVEL9K_SHORTEN_STRATEGY=truncate_to_unique
```
Result: `~/workspace/personal/life-atlas` → `~/w/p/life-atlas`. Leaf stays full. Parents shorten to shortest unique prefix within their directory.

**Emoji prompt character** — find the `POWERLEVEL9K_PROMPT_CHAR_*_CONTENT_EXPANSION` block (~8 lines), replace with:
```zsh
typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_VIINS_CONTENT_EXPANSION='🚀'
typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_VIINS_CONTENT_EXPANSION='💥'
typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_VICMD_CONTENT_EXPANSION='🛸'
typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_VICMD_CONTENT_EXPANSION='👾'
typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_VIVIS_CONTENT_EXPANSION='🔭'
typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_VIVIS_CONTENT_EXPANSION='🔭'
typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_VIOWR_CONTENT_EXPANSION='🛰️'
typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_VIOWR_CONTENT_EXPANSION='🛰️'
typeset -g POWERLEVEL9K_PROMPT_CHAR_LEFT_PROMPT_LAST_SEGMENT_END_SYMBOL=''
```
Choose any emoji pair — success≠error is the key invariant so failed commands are visually obvious. Alternatives: ✨/🔥, 🌊/🌋, 🌱/🍂.

Reload: `exec zsh`.

### Phase 4 — Move to Atlas + symlink (do NOT defer)

Three files go to Atlas: `~/.zshrc`, `~/.p10k.zsh`, and `~/.config/ghostty/config`. Different target subfolders because they're conceptually different config surfaces.

```sh
# Shell config
mkdir -p ~/Atlas/config/shell
mv ~/.zshrc ~/Atlas/config/shell/zshrc
mv ~/.p10k.zsh ~/Atlas/config/shell/p10k.zsh
ln -s ~/Atlas/config/shell/zshrc ~/.zshrc
ln -s ~/Atlas/config/shell/p10k.zsh ~/.p10k.zsh

# Terminal (Ghostty) config
mkdir -p ~/Atlas/config/terminal
mv ~/.config/ghostty/config ~/Atlas/config/terminal/ghostty-config
ln -s ~/Atlas/config/terminal/ghostty-config ~/.config/ghostty/config
```

Verify:
```sh
ls -la ~/.zshrc ~/.p10k.zsh ~/.config/ghostty/config
```
All three must show `-> /Users/andrewlee/Atlas/config/...`.

Open a new Ghostty window. Confirm prompt and theme look identical to pre-symlink state. If yes, sync works.

### Phase 5 — Update folder schema

Two new subfolders under `~/Atlas/config/` need to be added to `folder-schemas/config.md`:

- `shell/` — "Shell config (zshrc, p10k.zsh) symlinked into `$HOME` on each workstation"
- `terminal/` — "Terminal emulator config (e.g., Ghostty) symlinked into `~/.config/<app>/` on each workstation"

Slot alongside existing entries: `ai`, `apps`, `desktop-images`, `keys`, `settings`, `shortcuts`, `templates`, `themes`.

### Phase 6 — Document setup for new machines

Add `environment/shell-setup.md` (or section in existing env docs) covering the minimum steps to make a new workstation match this one:

1. `brew install powerlevel10k`
2. `brew install --cask font-meslo-lg-nerd-font`
3. `ln -s ~/Atlas/config/shell/zshrc ~/.zshrc`
4. `ln -s ~/Atlas/config/shell/p10k.zsh ~/.p10k.zsh`
5. `mkdir -p ~/.config/ghostty && ln -s ~/Atlas/config/terminal/ghostty-config ~/.config/ghostty/config`
6. Install Ghostty (from ghostty.org — not brew-cask-available on all setups; worth checking)
7. `exec zsh`

Phases 5 and 6 can be deferred to the next session without blocking the prompt working.

---

## Risks / open questions

- **Font install fails / Ghostty can't find it** — unlikely but check with `fc-list | grep -i meslo` after the cask install. Fallback: download from the p10k repo manually.
- **Existing `~/.zshrc` has user content not just the p10k source line** — the `mv` in Phase 4 preserves everything. Verify with `cat ~/Atlas/config/shell/zshrc` before the symlink if unsure.
- **Secondary workstation is Windows** — symlinks work on WSL but native PowerShell needs a different strategy. Out of scope; p10k on WSL reads the same Atlas-synced config if WSL mounts `~/Atlas/` (Google Drive for Desktop on Windows).
- **Transient prompt + multi-line commands** — occasionally collapses a long edited command awkwardly. If it bothers, set `POWERLEVEL9K_TRANSIENT_PROMPT=same-dir` (collapse only when dir is same) or `off`.

## Exit criteria

- [ ] `exec zsh` shows two-line p10k prompt with rainbow segments
- [ ] `andrewlee@AM2` (or equivalent user@host segment) is visibly colored and distinct from command text
- [ ] Path truncates as `~/w/p/life-atlas` style
- [ ] Emoji prompt char appears; changes between success and error states
- [ ] `ls -la ~/.zshrc ~/.p10k.zsh ~/.config/ghostty/config` shows all three as symlinks into `~/Atlas/config/`
- [ ] Restart Ghostty, open new shell, prompt + theme still work (sync persisted)
