# 💼 MacBook Pro (Work) — Device Schema

Folder layout and constraints for a company-issued MacBook Pro.

See the main [README](../README.md) for Atlas structure and sync topology.

---

## ⚠️ Constraints

Work Macs are subject to company policy. Before applying any life-atlas setup:

- Confirm company IT policy on cloud-sync tools (Google Drive, Dropbox, etc.)
- Do not sync personal Atlas to a company device unless explicitly permitted
- Do not mount the personal NAS (`Peddocks2`) on company networks
- Keep personal and company credentials strictly separated (no shared keychain items)

---

## 🗂️ Folder Layout (Rooted at `~/`)

```
~/
├── Applications/                  # Company-approved apps
├── Library/                       # macOS default
├── workspace/                     # 🔨 Work code repositories only
└── [Company Cloud Storage]/       # Per company-issued account (Drive, OneDrive, etc.)
```

Personal `~/Atlas/` is **not** synced on the work Mac. For personal-document access on a work device, use the web UI via personal account in a browser profile, after confirming policy compliance.

---

## 🔨 workspace

`~/workspace/` on the work Mac holds **only** company code and projects. Keep it segregated from any personal work.

---

## 🔁 Sync & Backup Strategy

| Folder | Method | Notes |
|---|---|---|
| `~/workspace/` | Company git / GitHub Enterprise / etc. | Per company policy |
| `~/` (system) | Company-managed backup | Per company policy |

---

## 📝 Notes

- Do not install personal Claude Code tooling, dotfiles, or Atlas config on a work device.
- If a single device must serve both work and personal use, prefer **separate macOS user accounts** over folder-level separation.
- Company policy supersedes any schema in this repo.
