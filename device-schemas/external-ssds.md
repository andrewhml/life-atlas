# 💾 External Photo SSDs — Device Schema

Folder layout and role of the external photo-backup SSDs in the `life-atlas` system.

See the main [README](../README.md) for Atlas structure and sync topology.

---

## 🧾 Hardware

| Drive | Model | Capacity | Filesystem | Connection |
|---|---|---|---|---|
| **Carbonizer** | SanDisk 2TB external SSD | 1.8 TB usable | exFAT | USB-C, direct to MacBook |
| **Noisy Cricket** | SanDisk 2TB external SSD | 1.8 TB usable | exFAT | USB-C via iVanky dock when MacBook is docked; direct USB-C when mobile |

---

## 🎯 Role

- **Carbonizer** — mobile working copy of the full photo library and active project files. Primary external drive; stays with the MacBook whether docked or mobile.
- **Noisy Cricket** — 1:1 clone of Carbonizer. Disaster-recovery copy; never the drive worked off of directly.

Photo and project content on these drives is **authoritative in the moment** (roughly the current year and recent past). The NAS is authoritative for anything older; see [Authority rules](#authority-rules-target-state).

---

## 🗂️ Folder Layout (Carbonizer; Noisy Cricket is a clone)

```
/Volumes/Carbonizer/
├── Music/                              # Music files
├── Photos/
│   ├── _CCC SafetyNet/                 # Carbon Copy Cloner quarantine (replaced/deleted files)
│   ├── Drone/                          # Drone archives
│   ├── Photo Files/                    # Primary photo archive
│   ├── Photos Library.photoslibrary/   # Apple Photos library (clone of Mac's — verify)
│   └── Remote Year/                    # Travel photos
├── Projects/                           # Active and near-active project files
└── Remote Year/                        # Additional travel content outside Photos/ (verify whether dupe)
```

---

## 🔁 Sync & Backup Strategy

| Pair | Tool | Direction | Trigger |
|---|---|---|---|
| MacBook `~/Pictures/` → Carbonizer | Carbon Copy Cloner | → | Manual; when both connected and CCC is open |
| Carbonizer → Noisy Cricket | Carbon Copy Cloner | → | Manual; when both connected and CCC is open |
| Carbonizer (or Noisy Cricket) → NAS `Media/photos/` | Manual rsync | → | At year close (target state; not consistently executed) |

### Authority rules (target state)

- **Current year:** MacBook `~/Pictures/` and Carbonizer hold the working copies; Noisy Cricket is the offline backup.
- **Older than ~1 year:** NAS `Media/photos/` is authoritative; SSDs may hold a cached copy but are not the master.
- **Immich** indexes the NAS archive. Not all older content imported yet; tracked in Plan 0002.

---

## ⚠️ Known Issues / Drift

- **Manual CCC triggering.** Clone runs only when the user remembers to open CCC with both drives mounted. Noisy Cricket can drift behind Carbonizer for unknown stretches.
- **Both SSDs live onsite.** No offsite rotation — single location = single failure mode (fire, flood, theft).
- **exFAT filesystem.** No journaling, no POSIX permissions, susceptible to corruption on unclean ejects. Acceptable for Mac/Windows interop but not ideal as a long-term photo archive filesystem.
- **Year-close archival to NAS.** Documented rule but not executed for 2025; `~/Pictures/2025 Photos/` and Carbonizer both still hold 2025 content.
- **Apple Photos library duplication.** A `Photos Library.photoslibrary` exists on both MacBook and Carbonizer. Whether Carbonizer's copy is an active CCC clone or a stale snapshot needs verification.
- **`Remote Year/` appears twice** on Carbonizer (root and under `Photos/`). Verify which is current.

Overall strategy tracked in Plan 0002 (3-2-1 consolidation).

---

## 📝 Notes

- Carbonizer should be mounted whenever the MacBook is docked or in active use.
- Noisy Cricket mounts via the iVanky dock (docked) or direct USB (mobile).
- CCC's `_CCC SafetyNet/` folder grows over time; purge periodically when free space tightens.
