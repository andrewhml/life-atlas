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

This repo is currently developed against one concrete setup. Adapt as needed:

| Role | Reference choice |
|---|---|
| Cloud drive folder | Google Drive (`~/Atlas/`) |
| Primary workstation | MacBook Pro (macOS, personal) |
| Secondary workstation | Windows 11 Pro PC |
| Company workstation | MacBook Pro (macOS, work) |
| NAS | UGREEN (`Peddocks2` at `/Volumes/personal_folder/Atlas`) |
| External photo SSDs | SanDisk 2TB × 2 (`Carbonizer` + 1:1 clone `Noisy Cricket`) |
| Phone | iPhone 16 Pro |
| Tablet | iPad 2024 |
| Consulting cloud | Separate Syntheus Google Drive |

See `device-schemas/` for per-device folder layout and setup.

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
│   ├── Auto/
│   ├── Events/
│   ├── Finance/
│   ├── Gear/
│   ├── Health/
│   ├── Housing/
│   ├── Identity/
│   ├── Legal/
│   ├── Music/
│   ├── Personality/
│   ├── Recovery Codes/
│   ├── Reference/
│   └── Travel/
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
| Primary workstation ↔ NAS | NAS cloud-drive integration (UGREEN Cloud Drive) | Bidirectional |
| Primary workstation → NAS | Time Machine | System backup |
| Cloud ↔ Mobile | Cloud drive native app | Bidirectional |

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
