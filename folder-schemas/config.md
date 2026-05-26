# ⚙️ Config — Folder Schema

`~/Atlas/config/` holds cross-device configuration — the settings, themes, shortcuts, and dotfile snapshots that make a new workstation feel like a known one.

**Two sync models, picked per file:**

- **Snapshot** (one-way copy `$HOME → Atlas`) — for files something *writes back to* at runtime, or where a startup-path dependency on Drive is unacceptable. Shell dotfiles (zsh sources them on every interactive shell), Claude Code's `settings.json` (runtime writes), git/ssh config.
- **Symlink** (`$HOME` entry points into Atlas) — for files you edit deliberately and infrequently, where zero-friction cross-device propagation matters more than write-race safety. Claude Code's `CLAUDE.md`, `statusline.sh`, and skill library.

The per-section tables below say which model applies to what.

---

## 📂 Subfolders

| Subfolder | Contents | Sync model |
|---|---|---|
| `ai/` | Prompts, persona files, model configs | Snapshot / manual |
| `apps/` | App-specific exports (settings bundles, preference plists, Claude Code config) | Snapshot / manual; `apps/claude/` via `environment/sync-claude-config.sh` |
| `desktop-images/` | Wallpapers set across devices | Read-at-setup |
| `keys/` | SSH keys, GPG keys, recovery material | **Never** accessed by automation |
| `settings/` | OS-level settings exports | Snapshot |
| `shell/` | Shell + git + ssh dotfile snapshots (`zprofile`, `zshrc`, `zshenv`, `p10k.zsh`, `gitconfig`, `ssh-config`) | Periodic snapshot via `environment/sync-shell-config.sh` |
| `shortcuts/` | Keyboard / app shortcut definitions | Snapshot |
| `templates/` | Reusable document / project templates | Read-at-setup |
| `terminal/` | Terminal emulator config snapshots (e.g., `ghostty-config`) | Periodic snapshot via `environment/sync-shell-config.sh` |
| `themes/` | Editor / terminal color themes | Read-at-setup |

---

## 🔁 Shell + Terminal Snapshots

Live dotfiles stay in their canonical `$HOME` paths. Atlas holds copies, refreshed by running `environment/sync-shell-config.sh` after edits.

| Live path | Atlas snapshot |
|---|---|
| `~/.zprofile` | `~/Atlas/config/shell/zprofile` |
| `~/.zshrc` | `~/Atlas/config/shell/zshrc` |
| `~/.zshenv` | `~/Atlas/config/shell/zshenv` |
| `~/.p10k.zsh` | `~/Atlas/config/shell/p10k.zsh` |
| `~/.gitconfig` | `~/Atlas/config/shell/gitconfig` |
| `~/.ssh/config` | `~/Atlas/config/shell/ssh-config` |
| `~/.config/ghostty/config` | `~/Atlas/config/terminal/ghostty-config` |

Direction is one-way: `$HOME` is the source of truth. The sync script copies forward and refuses to clobber anything else. To verify drift without writing: `./environment/sync-shell-config.sh --check`.

**Why three zsh files instead of one.** Login shells source `~/.zprofile` once (PATH and tool init go here so Homebrew etc. resolve early); interactive shells source `~/.zshrc` every time (keep this for prompt, completion, aliases — fast); every zsh invocation including scripts sources `~/.zshenv` (keep this minimal — just `LANG`, `EDITOR`).

**Why `~/.ssh/config` only.** Keys (`id_*`), `known_hosts`, and `allowed_signers` are per-machine and must never leave the host. The sync script refuses any path under `~/.ssh/` other than `config` — allowlist, not blocklist.

---

## 🤖 Claude Code (hybrid: symlink + snapshot)

Live config under `~/.claude/` is mostly per-machine runtime state (conversation history, sessions, telemetry, cache, MCP auth, file-history, machine-scoped permission grants). None of that travels. Only four kinds of content do, and they travel via two different mechanisms depending on whether Claude Code *writes back* to the file.

### Symlinked (read-mostly content)

These are edited deliberately and infrequently by you, not by Claude Code's runtime. Symlinks make Drive the bus — edit on any machine, the other sees it within the next Drive sync. No manual sync step.

| Live path | Atlas target |
|---|---|
| `~/.claude/CLAUDE.md` | `~/Atlas/config/apps/claude/CLAUDE.md` |
| `~/.claude/statusline.sh` | `~/Atlas/config/apps/claude/statusline.sh` |
| `~/.claude/skills/<name>` | `~/Atlas/config/ai/claude-skills/skills/<name>` (one symlink per skill) |

### Snapshotted (write-back content)

`settings.json` is rewritten by Claude Code's runtime when you toggle themes, change `/model`, add MCP servers, grant permissions. Symlinking it would race against Drive's sync daemon and risk `settings (Conflict).json`. Snapshot keeps Claude Code's write path local and propagation explicit.

| Live path | Atlas snapshot |
|---|---|
| `~/.claude/settings.json` | `~/Atlas/config/apps/claude/settings.json` |

Direction is one-way: `$HOME` is the source of truth. The sync script (`environment/sync-claude-config.sh`) carries an **allowlist guard** — refuses any path under `~/.claude/` other than `settings.json`. New-machine restore (including the symlink steps for the read-mostly files) lives in [`environment/claude-setup.md`](../environment/claude-setup.md).

### Why two Atlas locations (`apps/claude/` and `ai/claude-skills/`)

`apps/claude/` holds Claude-Code-specific user config. `ai/claude-skills/` holds the shared skill library — conceptually product-agnostic, could back any AI app's skill system. The split predates the apps/claude/ section; consolidating it later is optional, not required.

### Never travels

- `~/.claude/settings.local.json` — machine-scoped permission grants. Each device grows its own.
- Everything else under `~/.claude/` — history, sessions, projects, cache, MCP auth, telemetry, file-history, shell-snapshots, session-env, tasks, backups, ide, downloads, paste-cache, plugins. All runtime state.

New-machine setup steps live in [`environment/shell-setup.md`](../environment/shell-setup.md) (shell + git + ssh + terminal) and [`environment/claude-setup.md`](../environment/claude-setup.md) (Claude Code).

---

## 🚫 Anti-patterns

- Do not symlink **shell startup files** (`.zprofile`, `.zshrc`, `.zshenv`) into `~/Atlas/`. Drive sync sits on shell startup — adds latency and creates a hard dependency on Atlas being mounted. Snapshot pattern only for shell.
- Do not symlink **files that get written by their owning runtime** (e.g., Claude Code's `settings.json`) into `~/Atlas/`. Write races against Drive's sync daemon produce `(Conflict)` files. Snapshot only.
- Do not edit snapshots in `~/Atlas/config/shell/`, `~/Atlas/config/terminal/`, or `~/Atlas/config/apps/claude/settings.json` directly — the next sync will overwrite them. Edit under `$HOME` and run the relevant sync script.
- Do not put secrets anywhere except `keys/`, and never let automation read `keys/`.
