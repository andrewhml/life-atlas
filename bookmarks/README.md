# 🔖 Bookmarks

Strategy and schema for browser bookmarks across devices.

---

## 🎯 Current Approach

**Live sync:** Brave Sync keeps bookmarks current across Brave installations (Mac, PC, mobile).

**Snapshots:** Periodic HTML exports go to `~/Atlas/config/bookmarks_<MM_DD_YY>.html` for:

- Portability if switching browsers
- Rollback if sync goes wrong
- Cross-browser reference

---

## 📂 Organization

Bookmarks in the browser should be organized by context. Recommended top-level folders:

```
Bookmarks Bar/
├── Personal/          # Personal reading, tools, accounts
├── Work/              # Employer-related
├── Syntheus/          # Consulting work
└── Reading List/      # Queued articles, long-form
```

Nested folders within each context are fine; keep the top-level consistent.

---

## 🔁 Export Workflow

When bookmarks reach a meaningful state (big cleanup, before switching browsers, quarterly):

1. Export from the browser as HTML: `bookmarks_MM_DD_YY.html`
2. Save to `~/Atlas/config/` (auto-syncs to Drive + NAS)
3. Remove the previous export, or keep it for rollback

---

## ❓ Open Questions

- Single HTML export vs per-context JSON — which is easier to port between browsers?
- Is there value in also maintaining a parsed / structured copy (e.g., Markdown list) alongside the HTML?
- Cross-browser import fidelity (Brave → Firefox → Safari) — test before committing to a single path.

---

## 📝 Notes

- This repo does **not** hold bookmark data. Actual exports live in `~/Atlas/config/` (Drive-synced).
- Mobile browsers sync via browser-native mechanisms; Brave Sync extends to mobile when signed in.
- "Bookmarks well organized and easily ported" is a project completion criterion — track progress via `area/bookmarks` GitHub issues.
