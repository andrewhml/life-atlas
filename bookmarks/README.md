# 🔖 Bookmarks

Strategy for browser bookmarks across devices.

---

## 🎯 Approach

**Live sync:** Browser-native sync (e.g., Brave Sync, Chrome Sync, Firefox Sync) keeps bookmarks current across installations on desktop and mobile.

**Snapshots:** Periodic HTML exports go to the cloud drive at `config/bookmarks_<MM_DD_YY>.html` for:

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
├── Consulting/        # Client / consulting work (if applicable)
└── Reading List/      # Queued articles, long-form
```

Nested folders within each context are fine; keep the top-level consistent across browsers and devices.

---

## 🔁 Export Workflow

When bookmarks reach a meaningful state (after a big cleanup, before switching browsers, quarterly):

1. Export from the browser as HTML: `bookmarks_MM_DD_YY.html`
2. Save to the cloud drive `config/` folder
3. Remove the previous export, or keep it for rollback

---

## 🔧 Reference implementation

- Primary browser: Brave (desktop + mobile)
- Live sync: Brave Sync
- Snapshot location: `~/Atlas/config/bookmarks_<MM_DD_YY>.html`
- Most recent snapshot: `bookmarks_4_21_26.html`

---

## ❓ Open Questions

- Single HTML export vs per-context JSON — which is easier to port between browsers?
- Is there value in also maintaining a parsed / structured copy (e.g., Markdown list) alongside the HTML?
- Cross-browser import fidelity — test before committing to a single path.

---

## 📝 Notes

- This repo does **not** hold bookmark data. Actual exports live in the cloud drive `config/`.
- Mobile browsers sync via the browser's native mechanism; each major browser has its own solution.
- "Bookmarks well organized and easily ported" is a project completion criterion — track via `area/bookmarks` GitHub issues.
