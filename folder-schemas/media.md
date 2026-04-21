# 🖼️ Media — Folder Schema

Media is **local-first, NAS-archived.** It does not sync to Atlas because:

- DSLR / drone originals are too large for Drive quotas
- Lightroom / Photoshop libraries are volatile and tool-managed
- Re-upload on sync conflict can be destructive to catalog state

---

## 📍 Locations

| Location | Contents | Purpose |
|---|---|---|
| `~/Pictures/` on Mac | Working originals, editing libraries | Active photo / video work |
| NAS `Media/photos/` | Archived yearly content | Long-term storage; Plex / Immich serving |
| NAS `Media/{movies, music, tvshows, books}/` | Family media libraries | Plex serving |
| iPhone Camera Roll / iCloud Photos | iPhone captures | Separate flow; not part of DSLR pipeline |

---

## 📂 Mac `~/Pictures/` Structure

```
Pictures/
├── YYYY-Photos/                    # One per year
│   ├── RAW/
│   │   └── YYYY-MM/                # Monthly imports
│   ├── Processed/                  # Lightroom / export output
│   └── Video/
├── Lightroom-Library/              # Lightroom catalog + previews
└── Photos Library.photoslibrary    # Apple Photos (macOS default)
```

Scaffold a new year with `environment/macos_create_photo_year.sh YYYY`.

---

## 🔁 Lifecycle

1. **Import** — DSLR / drone card → `~/Pictures/YYYY-Photos/RAW/YYYY-MM/`
2. **Edit** — Lightroom / Photoshop; catalog stays in `~/Pictures/Lightroom-Library/`
3. **Export** — Processed output to `~/Pictures/YYYY-Photos/Processed/`
4. **Review period** — Material stays local while the year is active
5. **Archive** — When the year is complete, rsync `YYYY-Photos/` to NAS `Media/photos/`; optionally thin from Mac after verification

---

## 🎞️ NAS Media Library

See [`device-schemas/nas-structure.md`](../device-schemas/nas-structure.md) for the shared `Media/` share structure (`books`, `movies`, `music`, `photos`, `tvshows`).

---

## 📝 Notes

- iPhone photos do not flow through this pipeline. They live in iCloud Photos.
- Videos from iPhone needing editing should be exported to `~/Pictures/YYYY-Photos/Video/` manually.
- Do not mount NAS `Media/photos/` as a primary Lightroom catalog location — network latency harms editing.
