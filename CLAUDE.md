# Life Atlas — Project Guide

This repo documents and automates a personal digital-organization system called **Atlas** — a cross-device pattern for keeping important documents, cross-device config, shareable material, and daily working state organized across desktops, laptops, phones, tablets, and network storage.

---

## The Atlas pattern (abstract)

Atlas is a set of folder and sync conventions that span these roles:

- **Canonical cloud drive folder** — source of truth for important documents, cross-device config, and shareable material. Accessible from any device with a browser or cloud app.
- **Primary workstation** — laptop or desktop where most active work happens. Atlas is mirrored locally; code and large media live in separate local paths.
- **Secondary workstation** — additional desktop (different OS or role, e.g., GPU work).
- **Company workstation** — work-issued device, subject to company policy. Personal Atlas is NOT synced here.
- **Network-attached storage (NAS)** — local-network backup of the cloud folder, Time Machine target, and shared media library host.
- **Mobile devices (phones, tablets)** — read-often access to Atlas via native cloud apps; capture surface for shortcuts, quick notes, travel documents.

The pattern's purpose is comprehensive: **one mental model for where anything lives, regardless of which device is at hand.**

---

## Reference implementation (this user's setup)

The pattern is implementation-agnostic. This user's concrete choices:

| Pattern role | Reference implementation |
|---|---|
| Canonical cloud drive | Google Drive, mounted at `~/Atlas/` |
| Primary workstation | MacBook Pro (personal, macOS) |
| Secondary workstation | Personal PC (Windows 11 Pro, NVIDIA RTX 5080) |
| Company workstation | MacBook Pro (work, macOS) |
| Network-attached storage | UGREEN NAS named `Peddocks2` at `/Volumes/personal_folder/Atlas` |
| Phone | iPhone 16 Pro (Google Drive iOS app) |
| Tablet | iPad 2024 (Google Drive iOS app) |
| Consulting cloud | Separate Syntheus Google Drive |

**Language rule:** when docs describe the *pattern*, use abstract terms ("cloud drive folder," "primary workstation," "NAS," "mobile device"). When describing the *reference implementation*, specific names are fine. Device-schema files name specific devices because they ARE specific; that's expected.

---

## Ground-truth structure of the cloud drive folder

```
~/Atlas/
├── archive/    # Completed or reference-only projects
├── config/     # Cross-device config (ai, apps, desktop-images, keys,
│               # settings, shortcuts, templates, themes)
├── docs/       # Personal documents (Identity, Health, Finance, Legal,
│               # Auto, Housing, Travel, Events, Gear, Music,
│               # Personality, Recovery Codes, Reference)
├── share/      # Material shared with specific people
└── workspace/  # Non-code projects that fit in the cloud drive
```

The `life-atlas` repo contains **documentation and setup scripts about Atlas — not Atlas data itself.** Never commit personal documents, identity docs, keys, or anything from `~/Atlas/docs/` or `~/Atlas/config/keys/` into this repo.

---

## What lives outside Atlas (and why)

Not everything belongs in a cloud drive. These paths stay on a workstation, managed by other tools:

| Path (reference impl.) | Role | Why outside Atlas |
|---|---|---|
| `~/workspace/` | Code repositories | Managed by git; `.git/` and large `node_modules/` degrade cloud sync |
| `~/Pictures/` | DSLR / drone originals, editing libraries | Too large, too volatile for cloud sync |
| Syntheus cloud drive | Consulting work | Separate account, separate ownership |

---

## The "workspace" pattern

`workspace` is a **role, not a single path.** It means "a folder that holds projects." A workspace exists in multiple places:

| Role | Where (reference) | Contents | Reason |
|---|---|---|---|
| Cloud drive workspace | `~/Atlas/workspace/` | Non-code projects (planning, writing, personal) | Shareable via cloud |
| Local code workspace | `~/workspace/` | Code repositories under git | Version-controlled, binary-heavy |
| Company cloud workspace | Syntheus cloud drive | Consulting work | Separate account |

When the user says "workspace" and context is ambiguous, ask which one.

---

## Repo structure

```
life-atlas/
├── .claude/                # Skills, commands, settings for Claude Code
├── device-schemas/         # Folder structure per device
├── folder-schemas/         # Conceptual schemas per top-level folder
├── environment/            # Shell scripts and environment config
├── bookmarks/              # Bookmark strategy (not bookmark data)
├── docs/                   # Plans, session scratch (scratch is gitignored)
├── CLAUDE.md               # This file
└── README.md               # Public-facing overview
```

---

## Conventions

### Tone
- **README, schema docs, bookmarks README: external.** Prefer abstract pattern language. Call out the reference implementation as a specific example, not the only path.
- **CLAUDE.md: internal.** First-person OK. Can name specific devices and services freely. Not part of the public surface.

### Platform-neutral language (rule)

When docs describe the *pattern*, use abstract terms:

- "cloud drive folder" — not "Google Drive"
- "primary workstation" / "local workstation" — not "Mac" (in pattern context)
- "NAS" / "network-attached storage" — not "UGREEN NAS"
- "mobile device" — not "iPhone"

When docs describe the reference implementation, concrete names are fine. Device-schema docs name specific devices because they describe specific devices.

### House style for schema docs
- Emoji section headers (🗂️, 📦, 🔁, etc.)
- Folder trees inside fenced code blocks
- Tables for sync strategy / tool mapping
- Kept short; link back to README for rationale

### README is canonical
If README and a device/folder schema disagree, **README wins.** Update the schema to match, not the other way.

### Shell scripts must be idempotent
All scripts in `environment/` must be safe to rerun with the same outcome. Required patterns:

- `mkdir -p <path>` — never bare `mkdir`
- Check-before-write: `if [ ! -f file ]; then ... fi`
- Destructive ops (`rm`, `mv`, overwrites) must prompt or be guarded
- `defaults write` is idempotent — safe to use freely

### Never do
- Don't edit files inside `~/Atlas/` directly from this repo's scripts. The cloud drive app owns that path; this repo describes the structure.
- Don't commit content from `~/Atlas/docs/`, `~/Atlas/config/keys/`, or any other personal-data path.
- Don't assume a `~/Kit/` path exists — "Kit" was an earlier design that Atlas superseded.

---

## Session workflow

This repo uses these skills and commands:

- **`/session-start`** — reviews git state, open issues, active plans in `docs/plans/`, initializes `docs/session-scratch.md`
- **`/session-end`** — processes scratch into GitHub issues with labels, commits, pushes, cleans up
- **`/audit`** — scan the repo for drift (empty stubs, broken links, legacy references)
- **`/sync-check`** — verify on-disk reality matches what the schemas describe
- **`/plan-new <name> "<title>"`** — scaffold a new plan file in `docs/plans/`

### Required GitHub labels

Session-end assumes these labels exist on `andrewhml/life-atlas`. Create with `gh label create` if missing:

- Type: `ready`, `idea`, `bug`, `feature`, `chore`, `docs`
- Priority: `priority/high`, `priority/medium`, `priority/low`
- Area: `area/device-schemas`, `area/folder-schemas`, `area/environment`, `area/bookmarks`, `area/docs`, `area/meta`, `area/drift`

---

## Known drift (pending cleanup)

The repo is mid-reconciliation. Items tracked in GitHub issues:

- **`environment/macos_environment_init.sh`** — creates demo dirs from an earlier design. [#1]
- **`~/Atlas/README.md` on disk** — stale demo text. [#6]
- **Legacy `~/System/` on personal Mac** — pre-Atlas; migrate into `~/Atlas/config/`. [#5]
- **Empty environment stubs** — pending real content. [#2]
- **Obsidian vaults** — pending strategy decision. [#3]

Check `gh issue list --label area/drift` for current status.
