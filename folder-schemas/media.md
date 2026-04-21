# 🖼️ Media — Folder Schema

Media is **local-first, NAS-archived.** It does not sync to the cloud drive because:

- Camera / drone originals are too large for typical cloud-drive quotas
- Editing libraries (Lightroom catalogs, Photoshop files) are volatile and tool-managed
- Cloud sync on catalog state can be destructive

---

## 📍 Roles

| Role | Where it lives (reference) | Purpose |
|---|---|---|
| Working media folder | `~/Pictures/` on the primary workstation | Active photo / video work |
| Archive on NAS | NAS `Media/photos/` | Long-term storage; Plex / Immich serving |
| Family media library | NAS `Media/{movies, music, tvshows, books}/` | Plex serving |
| Phone captures | Phone-native cloud (iCloud Photos / Google Photos) | Separate flow; not part of the camera pipeline |

---

## 📂 Working Media Folder Structure

```
Pictures/
├── YYYY-Photos/                    # One per year
│   ├── RAW/
│   │   └── YYYY-MM/                # Monthly imports
│   ├── Processed/                  # Lightroom / export output
│   └── Video/
├── Lightroom-Library/              # Lightroom catalog + previews
└── Photos Library.photoslibrary    # OS-native photo library (if used)
```

Scaffold a new year with `environment/macos_create_photo_year.sh YYYY`.

---

## 🔁 Lifecycle

1. **Import** — camera / drone card → `Pictures/YYYY-Photos/RAW/YYYY-MM/`
2. **Edit** — Lightroom / Photoshop; catalog stays in `Pictures/Lightroom-Library/`
3. **Export** — Processed output to `Pictures/YYYY-Photos/Processed/`
4. **Review period** — Material stays local while the year is active
5. **Archive** — When the year is complete, rsync `YYYY-Photos/` to NAS `Media/photos/`; optionally thin from workstation after verification

---

## 🎞️ NAS Media Library

See [`device-schemas/nas-structure.md`](../device-schemas/nas-structure.md) for the shared `Media/` share structure (`books`, `movies`, `music`, `photos`, `tvshows`).

---

## 📝 Notes

- Phone photos do not flow through this pipeline. They live in the phone's native cloud service.
- Phone videos that need editing should be exported to the workstation's `Pictures/YYYY-Photos/Video/` manually.
- Do not mount NAS `Media/photos/` as a primary Lightroom catalog location — network latency harms editing.
