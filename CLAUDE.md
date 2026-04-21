# Life Atlas — Project Guide

This repo documents and automates the **Atlas system** — a personal digital-organization structure spanning Google Drive, local Macs, and a home NAS.

---

## What Atlas is

**Atlas** is a Google Drive folder (`~/Atlas/` on Mac) that holds important documents, cross-device config, and shareable material. It syncs three ways:

- **Cloud:** Google Drive (primary source of truth)
- **Mac:** `~/Atlas/` via Google Drive desktop app
- **NAS:** `/Volumes/personal_folder/Atlas` on NAS named `Peddocks2` (backup mirror)

The `life-atlas` repo contains **documentation and setup scripts about Atlas — not Atlas data itself.** Never commit personal documents, identity docs, keys, or anything from `~/Atlas/docs/` or `~/Atlas/config/keys/` into this repo.

---

## Ground-truth structure of `~/Atlas/`

```
~/Atlas/
├── archive/    # Completed or reference-only projects
├── config/     # Cross-device config (ai, apps, desktop-images, keys,
│               # settings, shortcuts, templates, themes)
├── docs/       # Personal documents (Identity, Health, Finance, Legal,
│               # Auto, Housing, Travel, Events, Gear, Music, Personality,
│               # Recovery Codes, Reference)
├── share/      # Material shared with specific people
└── workspace/  # Non-code projects that fit in Google Drive
```

---

## What lives outside Atlas (and why)

Not everything belongs in Google Drive. These stay local and are managed by other tools:

| Path | Purpose | Why outside Atlas |
|---|---|---|
| `~/workspace/` | Code repositories | Managed by git/GitHub; binary-heavy |
| `~/Pictures/` | DSLR / drone originals, editing libraries | Too large, too volatile for Drive |
| Syntheus Google Drive | Consulting work | Separate company Drive, different account |

---

## The "workspace" pattern

`workspace` is a **role, not a single path.** It means "a folder that holds projects." A workspace can exist in multiple places based on project characteristics:

| Location | Contents | Reason |
|---|---|---|
| `~/Atlas/workspace/` | Non-code projects (planning, writing, personal) | Shareable via Drive |
| `~/workspace/` | Code repos (this repo, kitted, etc.) | Managed by git |
| Syntheus Drive workspace | Consulting work | Company-owned cloud |

If the user says "workspace" and context is ambiguous, ask which one.

---

## Repo structure

```
life-atlas/
├── .claude/                # Skills, settings for Claude Code
├── device-schemas/         # Folder structure per device
├── folder-schemas/         # Conceptual schemas per top-level folder
├── environment/            # Shell scripts and environment config
├── bookmarks/              # Browser bookmarks (per context)
├── docs/                   # Plans, session scratch (scratch is gitignored)
├── CLAUDE.md               # This file
└── README.md               # Public-facing overview
```

---

## Conventions

### Tone
- **README and schema docs: external.** Write as if for others picking this up. Avoid "I" / "my."
- **CLAUDE.md: internal.** First-person OK. This file is not part of the public surface.

### House style for schema docs
- Emoji section headers (🗂️, 📦, 🔁, etc.)
- Folder trees inside fenced code blocks
- Tables for sync strategy / tool mapping
- Keep short; link back to README for rationale

### README is canonical
If README and a device-schema disagree, **README wins.** Update the schema to match, not the other way.

### Shell scripts must be idempotent
All scripts in `environment/` must be safe to rerun with the same outcome. Required patterns:

- `mkdir -p <path>` — never bare `mkdir`
- Check-before-write: `if [ ! -f file ]; then ... fi`
- Destructive ops (`rm`, `mv`, overwrites) must prompt or be guarded
- `defaults write` is idempotent — safe to use freely

### Never do
- Don't edit files inside `~/Atlas/` directly from this repo's scripts. Google Drive owns that path; this repo describes the structure, users create it in their own Drive.
- Don't commit content from `~/Atlas/docs/`, `~/Atlas/config/keys/`, or any other personal-data path.
- Don't assume a `~/Kit/` path exists — the "Kit" model was an earlier design that Atlas superseded.

---

## Session workflow

This repo uses session-start / session-end skills ported from the `kitted` project.

- **`/session-start`** — checks git state, open issues (`gh issue list`), active plans in `docs/plans/`, initializes `docs/session-scratch.md` for observations
- **`/session-end`** — processes scratch into GitHub issues with labels, commits, pushes, cleans up

### Required GitHub labels

Session-end assumes these labels exist on `andrewhml/life-atlas`. Create with `gh label create` if missing:

- Type: `ready`, `idea`, `bug`, `feature`, `chore`, `docs`
- Priority: `priority/high`, `priority/medium`, `priority/low`
- Area: `area/device-schemas`, `area/folder-schemas`, `area/environment`, `area/bookmarks`, `area/docs`, `area/meta`

---

## Known drift (pending cleanup)

The repo is mid-reconciliation. Items to watch for:

- **`environment/macos_environment_init.sh`** — creates `~/Atlas-Example/` demo dirs from an earlier design; does not match the real Atlas structure.
- **`~/Atlas/README.md` on disk** — calls itself "Atlas Example / feel free to remove," leftover from the init script. Stale.
- **Legacy `~/System/` on personal Mac** — pre-Atlas; contents should migrate to `~/Atlas/config/` over time.
- **Empty stub files** in `device-schemas/`, `folder-schemas/`, `environment/` — pending triage.

Tracked via open GitHub issues. Check `gh issue list --label area/drift` for status.
