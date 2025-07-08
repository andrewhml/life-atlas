# 💻 MacBook Pro (Personal) — Device Schema

This document defines the folder structure, local vs. NAS-based storage strategy, media handling, and environment setup for my **personal MacBook Pro** under the `life-atlas` system.

---

## 🗂️ Folder Layout (Rooted at `~/`)

```
~/
├── Applications/             # App-specific config/data
├── Desktop/                  # Ephemeral, cleared weekly
├── Documents/                # Default macOS folder (mostly unused)
├── Downloads/                # Inbound items only, triaged regularly
├── Workspace/                # 🔨 Active projects (personal, work, consulting, academic)
├── LiveDocs/                 # 🧩 Frequently accessed important documents
├── Media/
│   └── Photos/               # DSLR + drone imports (see below)
├── System/                   # ⚙️ Dotfiles, scripts, preferences
└── Vault/ → /Volumes/Vault/  # ❄️ NAS-mirrored long-term archive (cold storage)
```

---

## 🔥 LiveDocs

`~/LiveDocs/` is for **time-sensitive or frequently used documents** — it's backed up and kept minimal.

```
LiveDocs/
├── Identity/
├── Health/
├── Finance/
│   ├── 2025 Taxes/
│   └── Statements/
├── Government/
├── Legal/
└── Active Docs/         # Temporary or recent material
```

> Documents here are archived to the NAS (`Vault/DocsArchive/`) when no longer in frequent use.

---

## 🖼️ Media (Photo & Video Ingest)

Only **photography and drone footage** are kept locally. All other media (TV, music, etc.) lives on the NAS.

```
Media/
└── Photos/
    ├── 2025 Photos/              # Template for each year
    │   ├── DNG/
    │   ├── JPG/
    │   ├── RAW/
    │   └── Video/
    ├── 2024 Photos/
    │   └── ...
    ├── Lightroom Library/        # .lrcat and previews
    └── Apple Photos Library/     # macOS library bundle
```

> Year folders can be duplicated as templates. External drives or NAS are used for long-term archival.

---

## 🔁 Sync & Backup Strategy

| Folder        | Method             | Notes |
|---------------|---------------------|-------|
| `Workspace/`  | iCloud Drive + Git  | Active projects; version-controlled where possible |
| `LiveDocs/`   | iCloud Drive        | Critical, frequently used documents |
| `Media/Photos/`| Time Machine + Manual NAS backup | Only DSLR/drone content is local |
| `Vault/`      | NAS-mounted         | Full cold storage archive, synced from Mac periodically |
| `System/`     | GitHub repo         | Dotfiles and setup scripts live in `life-atlas` |

---

## ⚙️ Environment Setup

| Tool                | Purpose |
|---------------------|---------|
| **VS Code**         | Primary editor (w/ ChatGPT, Claude Code, Continue.dev) |
| **Homebrew**        | Package manager |
| **Warp Terminal**   | AI-powered terminal with autocomplete, blocks, and Claude integration |
| **Zsh + Oh My Zsh** | Shell + aliases |
| **Git + GitHub CLI**| Version control |
| **Raycast**         | Productivity + AI |
| **Obsidian** (opt.) | Light note vaulting |
| **Photoshop / Lightroom** | Media post-processing |

---

## 🤖 AI Tooling

| Tool            | Integration |
|------------------|-------------|
| **GitHub Copilot**   | Inline code suggestions in VS Code |
| **Continue.dev**     | Claude & GPT-4 inside VS Code |
| **Claude Code**      | Claude’s AI coding assistant (via web or integrated apps) |
| **ChatGPT**          | Prompt-based support and system planning |
| **Raycast AI**       | Quick lookup, summarization, command building |
| **Warp Terminal AI** | Built-in Claude-powered terminal blocks and suggestions |

---

## 🔐 Security & Backup Layers

| Tool / Method       | Use |
|---------------------|-----|
| **Bitwarden**       | Secrets and 2FA |
| **iCloud Drive**    | Documents, Workspace sync |
| **Time Machine**    | Full local backup to SSD |
| **NAS (UGREEN)**    | Media + vault archive, mounted at `~/Vault/` |
| **Manual Rsync**    | Used for selective syncing to/from NAS if needed |

---

## 📝 Notes

- This schema is customized for creative work, project development, and personal organization.
- DSLR and drone photo/video content are kept locally until processed or archived.
- Vault is **not stored locally** — it’s mounted from the NAS at login via auto-mount or alias.
- For new device setup, follow `environment/mac-setup.md`.
