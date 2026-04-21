# 💻 MacBook Pro (Personal) — Device Schema

Folder layout and environment setup for a personal MacBook Pro under the `life-atlas` system.

See the main [README](../README.md) for Atlas structure and sync topology.

---

## 🗂️ Folder Layout (Rooted at `~/`)

```
~/
├── Applications/             # App-specific config/data
├── Atlas/                    # ☁️ Google-Drive-synced (see README)
├── Desktop/                  # Ephemeral, cleared weekly
├── Documents/                # Default macOS folder (mostly unused)
├── Downloads/                # Inbound items, triaged regularly
├── Library/                  # macOS default
├── Movies/                   # macOS default
├── Music/                    # macOS default
├── Pictures/                 # 🖼️ DSLR + drone imports, editing libraries
└── workspace/                # 🔨 Code repositories (local, git-managed)
```

> `~/Atlas/` is managed by the Google Drive desktop app. Do not edit scripts or schemas as if this repo manages Atlas contents directly — it does not.

---

## 🖼️ Pictures (Photo & Video)

Local only. Not synced to Atlas due to size and volatility. Archived to NAS manually when a year is complete.

```
Pictures/
├── YYYY-Photos/                 # Yearly photo structure
│   ├── RAW/
│   │   └── YYYY-MM/             # Monthly import folders
│   ├── Processed/               # Lightroom exports
│   └── Video/
├── Lightroom-Library/           # .lrcat and previews
└── Photos Library.photoslibrary # Apple Photos (macOS default)
```

> Run `environment/macos_create_photo_year.sh YYYY` to scaffold a new year folder.

---

## 🔨 workspace

Local code repositories. Managed by git / GitHub.

```
workspace/
├── personal/        # Personal projects (this repo, kitted, etc.)
└── work/            # Work-adjacent projects
```

> Separate from `~/Atlas/workspace/`, which holds non-code projects in Google Drive. Syntheus consulting code lives in the Syntheus company Google Drive, not here.

---

## 🔁 Sync & Backup Strategy

| Folder | Method | Notes |
|---|---|---|
| `~/Atlas/` | Google Drive + NAS mirror | See main README |
| `~/workspace/` | Git / GitHub | Per-repo |
| `~/Pictures/` | Time Machine + manual NAS archive | Local-only until archived |
| `~/` (entire system) | Time Machine → Peddocks2 | Automatic |

---

## ⚙️ Environment Setup

| Tool | Purpose |
|---|---|
| VS Code | Primary editor |
| Claude Code | AI coding assistant (CLI + IDE integration) |
| Homebrew | Package manager |
| Warp Terminal | AI-powered terminal |
| Zsh + Oh My Zsh | Shell + aliases |
| Git + GitHub CLI | Version control |
| Raycast | Productivity + AI |
| Lightroom / Photoshop | Media post-processing |

---

## 🤖 AI Tooling

| Tool | Integration |
|---|---|
| Claude Code | Claude's coding assistant, this repo's primary AI surface |
| GitHub Copilot | Inline suggestions in VS Code |
| Raycast AI | Quick lookup, summarization |
| Warp Terminal AI | Claude-powered terminal blocks |
| ChatGPT | Prompt-based planning and drafting |

---

## 🔐 Security & Backup Layers

| Tool / Method | Use |
|---|---|
| Bitwarden | Secrets and 2FA |
| Google Drive | Atlas sync (cloud master) |
| Time Machine | Full local backup to NAS |
| Peddocks2 NAS | Time Machine destination + Atlas backup mirror |

---

## 📝 Notes

- For new-device setup, install the Google Drive desktop app first so `~/Atlas/` populates before running any scripts.
- DSLR / drone originals stay in `~/Pictures/` until a year is archived to the NAS Media share.
- Any configuration meant to travel between devices should live in `~/Atlas/config/`, not in local dotfiles alone.
