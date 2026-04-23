# ⚙️ Config — Folder Schema

`~/Atlas/config/` holds cross-device configuration — the settings, themes, shortcuts, and dotfile snapshots that make a new workstation feel like a known one.

**Config is snapshot-synced, not live.** Most entries are either (a) read-at-setup-time material (themes, desktop images) or (b) periodic snapshots of live state that lives under `$HOME`. Dotfiles in particular are copied, not symlinked — cloud sync daemons should not sit in the critical path of a shell starting up.

---

## 📂 Subfolders

| Subfolder | Contents | Sync model |
|---|---|---|
| `ai/` | Prompts, persona files, model configs | Snapshot / manual |
| `apps/` | App-specific exports (settings bundles, preference plists) | Snapshot / manual |
| `desktop-images/` | Wallpapers set across devices | Read-at-setup |
| `keys/` | SSH keys, GPG keys, recovery material | **Never** accessed by automation |
| `settings/` | OS-level settings exports | Snapshot |
| `shell/` | Shell dotfile snapshots (`zshrc`, `p10k.zsh`) | Periodic snapshot via `environment/sync-shell-config.sh` |
| `shortcuts/` | Keyboard / app shortcut definitions | Snapshot |
| `templates/` | Reusable document / project templates | Read-at-setup |
| `terminal/` | Terminal emulator config snapshots (e.g., `ghostty-config`) | Periodic snapshot via `environment/sync-shell-config.sh` |
| `themes/` | Editor / terminal color themes | Read-at-setup |

---

## 🔁 Shell + Terminal Snapshots

Live dotfiles stay in their canonical `$HOME` paths. Atlas holds copies, refreshed by running `environment/sync-shell-config.sh` after edits.

| Live path | Atlas snapshot |
|---|---|
| `~/.zshrc` | `~/Atlas/config/shell/zshrc` |
| `~/.p10k.zsh` | `~/Atlas/config/shell/p10k.zsh` |
| `~/.config/ghostty/config` | `~/Atlas/config/terminal/ghostty-config` |

Direction is one-way: `$HOME` is the source of truth. The sync script copies forward and refuses to clobber anything else. To verify drift without writing: `./environment/sync-shell-config.sh --check`.

New-machine setup flows the other direction — see [`environment/shell-setup.md`](../environment/shell-setup.md).

---

## 🚫 Anti-patterns

- Do not symlink live dotfiles into `~/Atlas/` subfolders. Cloud sync shouldn't sit on a shell's startup path.
- Do not edit snapshots in `~/Atlas/config/shell/` or `~/Atlas/config/terminal/` directly — the next sync will overwrite them. Edit under `$HOME` and run the sync script.
- Do not put secrets anywhere except `keys/`, and never let automation read `keys/`.
