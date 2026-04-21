# 📱 iPhone — Device Schema

Atlas access and workflow for iPhone 16 Pro.

See the main [README](../README.md) for Atlas structure and sync topology.

---

## ☁️ Atlas Access

Atlas is accessed via the **Google Drive iOS app** with selective offline sync for lookup-critical content.

Recommended offline-enabled paths:

- `docs/Identity/`, `docs/Health/`, `docs/Recovery Codes/`
- `docs/Travel/` during active trips
- `docs/Auto/` for roadside reference

Other folders stream on demand.

---

## 📲 Shortcuts

iPhone is the primary trigger surface for iOS Shortcuts. Canonical definitions live in `Atlas/config/shortcuts/iOS-Shortcuts/`. Shortcuts sync across Apple devices via iCloud; export back to Atlas periodically to keep the repo copy fresh.

---

## 🖼️ Photos

iPhone photos flow through Apple Photos / iCloud Photos. They do not enter the DSLR / drone pipeline in `~/Pictures/` on Mac.

When an iPhone video or photo needs to join the main media library, export manually to `~/Pictures/YYYY-Photos/` on the Mac.

---

## 📝 Notes

- iPhone is a **quick-access, credential-lookup, trigger** device. Not for authoring.
- No code, no large media, no NAS mounts.
- Before travel, pin `docs/Travel/` and any trip-specific folders for offline access.
