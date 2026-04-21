# 🧭 Life Atlas

A personal digital-organization system built around **Atlas** — a Google-Drive-synced folder that holds important documents, cross-device config, and shareable material, backed up to a home NAS.

---

## ✨ Purpose

Atlas helps you:

- Keep important documents (IDs, health, finance, legal) accessible from any device
- Share cross-device configuration: app settings, shortcuts, templates
- Maintain a consistent structure across Mac, iPad, iPhone, and NAS
- Separate cloud-synced material from local-only work (code, large media)

---

## 💻 Devices covered

- MacBook Pro (Personal)
- MacBook Pro (Work)
- Personal PC (Windows or Linux)
- UGREEN NAS (Peddocks2)
- iPad (2024)
- iPhone 16 Pro

See `device-schemas/` for per-device folder layout and setup.

---

## 🗂️ Atlas structure

Atlas lives at `~/Atlas/` on macOS and mirrors to `/Volumes/personal_folder/Atlas` on the `Peddocks2` NAS.

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
└── workspace/  # Non-code projects that fit in Google Drive
```

---

## 🏠 What lives outside Atlas

Not everything belongs in Google Drive. Some paths stay local on the Mac, managed by other tools:

| Path | Purpose | Why not in Atlas |
|---|---|---|
| `~/workspace/` | Code repositories | Managed by git / GitHub |
| `~/Pictures/` | DSLR / drone originals, editing libraries | Too large, too volatile |
| Syntheus Google Drive | Consulting work | Separate company account |

The pattern: **Atlas for anything shareable, searchable, and cloud-friendly. Local for anything that is tool-managed, binary-heavy, or workflow-specific.**

---

## 🔁 Sync topology

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Google Drive    │ <===> │  Mac ~/Atlas/    │ <===> │  NAS Peddocks2   │
│  (cloud master)  │       │  (local working) │       │  /Volumes/       │
│                  │       │                  │       │  personal_folder │
└──────────────────┘       └──────────────────┘       │  /Atlas          │
                                                       └──────────────────┘
```

| Link | Method | Direction |
|---|---|---|
| Cloud ↔ Mac | Google Drive desktop app | Bidirectional |
| Mac ↔ NAS | UGREEN Cloud Drive (Google Drive integration) | Bidirectional |
| Mac → NAS | Time Machine | System backup |

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
├── environment/          # macOS setup scripts, Brewfile docs
├── bookmarks/            # Browser bookmarks by context
├── CLAUDE.md             # Project guide for Claude Code
└── README.md             # This file
```

---

## 🚀 Getting started

1. **Install Google Drive desktop app** on your Mac. Sign in with the account that hosts your Atlas folder.
2. **Create `~/Atlas/`** in Google Drive (or mirror the structure above in your existing Drive root).
3. **Configure NAS sync** via UGREEN Cloud Drive → Google Drive, pointed at `/Volumes/personal_folder/Atlas` (or equivalent NAS share).
4. **Clone this repo** into `~/workspace/personal/life-atlas` for access to scripts and schema docs.
5. **Run setup scripts** from `environment/` as needed (see per-device schema for specifics).

---

## 📝 Notes

- Atlas is the cloud-synced portion. Local-only paths exist for things Google Drive is poorly suited to hold.
- The NAS (`Peddocks2`) is a **backup mirror**, not a primary source of truth. Google Drive is the master.
- This repo holds documentation and setup scripts. It does not contain Atlas data.
- Structures shown here are recommendations. Adapt folder names and nesting to your workflow.
