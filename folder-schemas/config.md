# ⚙️ Config — Folder Schema

`~/Atlas/config/` holds cross-device configuration — the settings, themes, shortcuts, and dotfile snapshots that make a new workstation feel like a known one.

**Sync models, picked per file:**

- **Snapshot** (one-way copy `$HOME → Atlas`) — for files something *writes back to* at runtime, or where a startup-path dependency on Drive is unacceptable. Shell dotfiles, git/ssh config, terminal emulator config.
- **Read-at-setup** — files copied from Atlas to live paths once during new-machine bring-up. Wallpapers, templates, themes.

The per-section tables below say which model applies to what. Atlas does NOT sync everything — Claude Code's `~/.claude/` is the notable exception, managed out-of-band via a dedicated git repo (see [Claude Code section](#claude-code-out-of-band) below).

---

## 📂 Subfolders

| Subfolder | Contents | Sync model |
|---|---|---|
| `ai/` | Prompts, persona files, model configs | Snapshot / manual |
| `apps/` | App-specific exports (settings bundles, preference plists) | Snapshot / manual per app |
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

## 🤖 Claude Code (out-of-band)

Claude Code's `~/.claude/` config does NOT live under Atlas. It's a git clone of a private `claude-harness` repo, kept in sync across machines via a shell wrapper that runs `git pull --rebase --autostash` before launching Claude Code. Secrets live in macOS Keychain (referenced by per-server wrappers under `mcp-wrappers/`); per-machine runtime state (`sessions/`, `history.jsonl`, `cache/`, `settings.local.json`, telemetry, MCP auth, file-history) is gitignored and never travels.

### Why out-of-band

- **`settings.json` is rewritten by Claude Code's runtime** (theme toggles, `/model`, MCP server adds, permission grants). A symlink into Atlas would race against Drive's sync daemon and produce `(Conflict)` files; a snapshot would lag every edit until the sync script runs.
- **Skill and MCP-registry edits need a hard secret-audit boundary.** A dedicated git repo runs `gitleaks` on every commit; Drive sync can't gate on that.
- **Per-machine runtime state is large and noisy.** A git `.gitignore` filters it cleanly; Drive sync would churn on every Claude session.

### Where to go for details

| Topic | File |
|---|---|
| Initial seeding, new-device clone, daily ops, wrapper, secret model | [`environment/claude-setup.md`](../environment/claude-setup.md) |
| Per-machine Keychain provisioning script | [`environment/setup-claude-secrets.sh`](../environment/setup-claude-secrets.sh) |

The shell side of new-machine bring-up (zsh + git + ssh + terminal) lives in [`environment/shell-setup.md`](../environment/shell-setup.md); it precedes the Claude harness clone.

---

## 🚫 Anti-patterns

- Do not symlink **shell startup files** (`.zprofile`, `.zshrc`, `.zshenv`) into `~/Atlas/`. Drive sync sits on shell startup — adds latency and creates a hard dependency on Atlas being mounted. Snapshot pattern only for shell.
- Do not symlink **files that get written by their owning runtime** into `~/Atlas/`. Write races against Drive's sync daemon produce `(Conflict)` files. Snapshot only — or, when the writer is too active even for snapshot (and the audit surface is wide enough to justify the cost), move the config out of Atlas entirely into a dedicated git repo. That's the route taken for `~/.claude/`.
- Do not edit snapshots in `~/Atlas/config/shell/` or `~/Atlas/config/terminal/` directly — the next sync will overwrite them. Edit under `$HOME` and run the relevant sync script.
- Do not put secrets anywhere except `keys/`, and never let automation read `keys/`.
