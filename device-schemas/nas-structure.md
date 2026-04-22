# 📦 UGREEN NAS (Peddocks2) — Device Schema

Folder structure and role of the NAS in the `life-atlas` system.

See the main [README](../README.md) for Atlas structure and sync topology.
See [`nas-services.md`](./nas-services.md) for Docker services, version pins, and known issues.

---

## 🔧 NAS Paths

- **Hostname:** `Peddocks2`
- **Atlas mirror (from Mac, via SMB):** `/Volumes/personal_folder/Atlas`
- **Shared media, docker, Time Machine:** exposed as separate SMB shares

> Internal NAS paths (e.g., `/volume1/...`) depend on the UGREEN volume layout. Confirm via the NAS admin panel before scripting against them.

---

## ☁️ Atlas Mirror

`/Volumes/personal_folder/Atlas` mirrors `~/Atlas/` (Google Drive) via UGREEN Cloud Drive.

- **Role:** Local-network backup of Atlas content
- **Direction:** Bidirectional with Google Drive (cloud remains master)
- **Why it exists:** Faster-than-internet restore, offline access during outages

See main README for the content layout.

---

## 🎞️ Media Library

Separate from Atlas. Holds Plex-readable content and archived photo/video originals.

```
Media/
├── books/           # PDFs, eBooks
├── downloads/       # Staging / incoming
├── movies/          # Plex movies
├── music/           # Plex music
├── photos/          # Archived DSLR/drone content (moved from ~/Pictures/)
└── tvshows/         # Plex TV
```

---

## 🛠️ Services

Hosted via Docker on the NAS:

- **Plex** — media server for `Media/`
- **Immich** — self-hosted photo management
- **Nginx Proxy Manager** — reverse proxy / TLS
- **Portainer** — container management UI

---

## 🔁 Sync Strategy Summary

| Source | Destination | Method | Direction |
|---|---|---|---|
| Google Drive (cloud) | Mac `~/Atlas/` | Google Drive desktop app | ↔ |
| Mac `~/Atlas/` | NAS `/Volumes/personal_folder/Atlas/` | UGREEN Cloud Drive | ↔ |
| Mac `~/` (entire system) | NAS Time Machine share | Time Machine | → |
| Mac `~/Pictures/YYYY-Photos/` (archived) | NAS `Media/photos/` | Manual rsync | → |

---

## ✅ Permissions

- **Media share** — group-readable by Plex and household users
- **personal_folder** — user-only (`andrewhml`)
- Use separate service accounts for automation rather than the primary user

---

## 📝 Notes

- Atlas on the NAS is a **mirror**, not the source of truth. Google Drive is the master.
- Time Machine covers `~/Atlas/` redundantly with Google Drive — intentional (different failure modes).
- Archival from `~/Pictures/` to `Media/photos/` is manual, performed when a year's content is considered complete.
- Internal volume paths (`/volume1/...`) are not enumerated here because they vary by NAS configuration; refer to the UGREEN admin UI when scripting.
