# 📱 iPad — Device Schema

Atlas access and workflow for iPad (2024).

See the main [README](../README.md) for Atlas structure and sync topology.

---

## ☁️ Atlas Access

Atlas is accessed via the **Google Drive iOS app** with selective offline sync for frequently used folders.

Recommended offline-enabled paths:

- `docs/Identity/`, `docs/Health/`, `docs/Recovery Codes/`
- `config/templates/` for quick authoring starts

Other folders stream on demand.

> Do not open or edit files in `Atlas/config/keys/` on iPad.

---

## 📲 Shortcuts

The iPad pulls shortcut definitions from `Atlas/config/shortcuts/iOS-Shortcuts/`. When a shortcut is created or updated on iOS, export the updated definition back to that folder so other Apple devices can import the current version.

---

## 📝 Notes

- iPad is a **read-often, write-rarely** surface for Atlas content. Heavy authoring happens on Mac.
- No code repositories on iPad; `~/workspace/` is Mac-only.
- No DSLR / drone originals on iPad.
