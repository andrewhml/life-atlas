# 🧭 Life Atlas

A personal digital-organization system built around **Atlas** — a cross-device pattern for keeping important documents, cross-device config, shareable material, and daily working state organized across desktops, laptops, phones, tablets, and network storage.

---

## ✨ Purpose

Atlas helps you:

- Keep important documents (IDs, health, finance, legal) accessible from any device
- Share cross-device configuration: app settings, shortcuts, templates, themes
- Maintain a consistent mental model for where anything lives — laptop, phone, tablet, NAS
- Separate cloud-synced material from local-only work (code, large media)
- Back up everything locally on a NAS in addition to cloud storage

---

## 🧩 The Atlas pattern

Atlas is implementation-agnostic. It describes a set of roles:

| Role | Purpose |
|---|---|
| **Cloud drive folder** | Source of truth for documents, config, shareable material |
| **Primary workstation** | Active work; local mirror of the cloud drive |
| **Secondary workstation** | Additional desktop (different OS or role, e.g., GPU work) |
| **Company workstation** | Work-issued device; personal Atlas NOT synced here |
| **Network-attached storage** | Local backup of cloud drive + Time Machine + media library |
| **Mobile devices** | Phones and tablets with read-often access to the cloud drive |

Pick a tool for each role and stay consistent. The schemas and scripts in this repo describe conventions that apply across implementations.

---

## 🔧 Reference implementation

This repo describes the *pattern*. The concrete pattern→device bindings (which physical NAS, which workstation, etc.) live alongside each user's own Atlas — not in this repo — so the pattern stays portable and personal specifics stay private. See `device-schemas/` for the per-device schema templates anyone can fill in for their own setup.

---

## 🗂️ Cloud drive folder structure

```
~/Atlas/
├── archive/    # Completed / reference-only material
├── config/     # Cross-device config
│   ├── ai/
│   ├── apps/
│   ├── desktop-images/
│   ├── keys/
│   ├── settings/
│   ├── shortcuts/
│   ├── templates/
│   └── themes/
├── docs/       # Personal documents
│   ├── auto/
│   ├── events/
│   ├── finance/
│   ├── gear/
│   ├── health/
│   ├── housing/
│   ├── identity/
│   ├── legal/
│   ├── music/
│   ├── personality/
│   ├── recovery codes/
│   ├── reference/
│   └── travel/
├── share/      # Material shared with specific people
└── workspace/  # Non-code projects that fit in the cloud drive
```

---

## 🏠 What lives outside Atlas

Not everything belongs in a cloud drive. These stay local, managed by other tools:

| Path | Role | Why not in Atlas |
|---|---|---|
| Local code workspace | Code repositories | Managed by git; `.git/` and large `node_modules/` trees degrade cloud sync |
| Local media folder | DSLR / drone originals, editing libraries | Too large, too volatile |
| Separate company cloud | Consulting / employer work | Different account, different ownership |

The pattern: **Atlas for anything shareable, searchable, and cloud-friendly. Local for anything tool-managed, binary-heavy, or workflow-specific.**

---

## 🔁 Sync topology

```
┌──────────────────┐       ┌────────────────────┐       ┌──────────────────┐
│  Cloud drive     │ <===> │  Workstation       │ <===> │  NAS             │
│  (source of      │       │  local Atlas dir   │       │  local mirror +  │
│   truth)         │       │                    │       │  media library   │
└──────────────────┘       └────────────────────┘       └──────────────────┘
        ↑                          ↕                              ↑
        └──── Mobile apps          Time Machine ──────────────────┘
                                    (system backup)
```

| Link | Reference method | Direction |
|---|---|---|
| Cloud ↔ Primary workstation | Cloud drive desktop app (Google Drive for Desktop) | Bidirectional |
| Primary workstation ↔ NAS | NAS cloud-drive integration (vendor-specific app) | Bidirectional |
| Primary workstation → NAS | Time Machine | System backup |
| Cloud ↔ Mobile | Cloud drive native app | Bidirectional |

### Mirror vs Stream for cloud drives

Cloud drive desktop apps generally offer two modes for how local copies materialize. The convention here:

| Mode | When to use | Why |
|---|---|---|
| **Mirror** | The primary cloud account (Atlas) on the primary workstation | Full local copy at a predictable path. Offline-by-default — no per-folder "available offline" toggle needed. The local directory IS the canonical Atlas folder, no symlinks. |
| **Stream** | Secondary cloud accounts (e.g., consulting / employer drives) | Saves disk; secondary accounts rarely need full local copies. Access via a `~/<AccountName>` symlink to the platform's CloudStorage path so paths stay stable. |

For Google Drive for Desktop specifically: Mirror mode lets you target a literal path (e.g., `~/Atlas`) directly. Stream keeps files under `~/Library/CloudStorage/GoogleDrive-…/My Drive`, which is the right home for secondary accounts. After switching the primary account to Mirror, Drive maintains a backward-compat symlink at the old CloudStorage path so any tool that hardcoded it still works.

---

## 🗺️ Repo layout

```
life-atlas/
├── device-schemas/       # Folder structure per device
│   ├── macbook-personal.md
│   ├── macbook-work.md
│   ├── nas-structure.md
│   ├── pc-personal.md
│   ├── ipad.md
│   └── iphone.md
├── folder-schemas/       # Conceptual schemas per top-level folder
├── environment/          # Setup scripts, Brewfile docs
├── bookmarks/            # Bookmark strategy
├── CLAUDE.md             # Project guide for Claude Code
└── README.md             # This file
```

---

## 🚀 Getting started

1. **Pick a cloud drive** (Google Drive, iCloud Drive, OneDrive, Dropbox) and install its desktop client on your primary workstation.
2. **Create an Atlas root folder** in the cloud drive using the structure above, or adapt the names to your preference.
3. **Configure NAS mirror** if you have a NAS — most modern NASes (Synology, UGREEN, QNAP) support cloud-drive sync.
4. **Install cloud drive app** on phones and tablets; enable selective offline sync for key folders.
5. **Clone this repo** to your local code workspace for access to scripts and schema docs.
6. **Run setup scripts** from `environment/` for your platform (see per-device schemas).

---

## 📝 Notes

- This repo holds **documentation and setup scripts** about Atlas. It does not contain Atlas data.
- Names and paths shown here are from the reference implementation. Adapt to your tools, accounts, and workflows.
- The cloud drive is the **source of truth**. The NAS is a **mirror**. Mobile devices are **consumers**.
- Atlas is intentionally comprehensive: it covers documents, config, shared material, and mobile access — not just a document archive.
