# 🖥️ Personal PC — Device Schema

Folder layout and environment setup for a personal PC (Windows or Linux) under the `life-atlas` system.

See the main [README](../README.md) for Atlas structure and sync topology.

---

## 🗂️ Folder Layout

Atlas is accessed via the **Google Drive for Desktop** app (Windows) or a Drive client (Linux).

### Windows

```
C:\Users\<user>\
├── Atlas\                  # ☁️ Google-Drive-synced via Drive for Desktop
├── workspace\              # 🔨 Code repositories (local, git-managed)
└── Pictures\               # Media (optional; depends on PC's role)
```

### Linux

```
~/
├── Atlas/                  # Mounted via Drive client (rclone, google-drive-ocamlfuse, etc.)
├── workspace/              # 🔨 Code repositories
└── Pictures/               # Media (optional)
```

---

## 🔁 Sync & Backup

| Folder | Method | Notes |
|---|---|---|
| `Atlas/` | Google Drive for Desktop / rclone | Cloud master; see README |
| `workspace/` | Git / GitHub | Per-repo |
| System | TBD (Macrium, rsnapshot, Timeshift, etc.) | To be defined during PC onboarding |

---

## ⚙️ Environment Setup

| Tool | Purpose |
|---|---|
| Google Drive for Desktop (Win) / rclone (Linux) | Atlas sync |
| VS Code | Editor |
| Git | Version control |
| Windows Terminal (Win) / preferred terminal (Linux) | Shell |
| Package manager: `winget` (Win) / `apt` / `pacman` / `brew` (Linux) | Tool installs |

---

## 📝 Notes

- PC is being added to the system. Details will firm up as primary use cases are defined.
- Keep folder names parallel to the Mac schema to minimize cross-platform confusion.
- Add exclusions in the Drive client for OS cruft: `Thumbs.db` and `desktop.ini` (Windows), `.Trash-*` (Linux).
- PC-generated files should not appear inside `Atlas/config/` unless explicitly intended for cross-device sync.
