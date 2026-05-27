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

The pattern is implementation-agnostic. The concrete pattern→device bindings (which physical box IS the NAS, which workstation IS the primary, etc.) live **outside this repo** — in `~/Atlas/config/atlas/reference-implementation.md`. Read that file on demand when a task needs a specific name; it's cloud-synced across the user's devices.

**Language rule:** when docs in this repo describe the *pattern*, use abstract terms only ("cloud drive folder," "primary workstation," "NAS," "mobile device"). Specifics belong in the private reference-implementation file, not here.

---

## Ground-truth structure of the cloud drive folder

```
~/Atlas/
├── archive/    # Completed or reference-only projects
├── config/     # Cross-device config (ai, apps, desktop-images, keys,
│               # settings, shortcuts, templates, themes)
├── docs/       # Personal documents (identity, health, finance, legal,
│               # auto, housing, travel, events, gear, music,
│               # personality, recovery codes, reference)
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
| Separate consulting/employer cloud | Consulting/work content | Separate account, separate ownership |

---

## The "workspace" pattern

`workspace` is a **role, not a single path.** It means "a folder that holds projects." A workspace exists in multiple places:

| Role | Where (reference) | Contents | Reason |
|---|---|---|---|
| Cloud drive workspace | `~/Atlas/workspace/` | Non-code projects (planning, writing, personal) | Shareable via cloud |
| Local code workspace | `~/workspace/` | Code repositories under git | Version-controlled, binary-heavy |
| Company cloud workspace | Separate consulting/employer cloud | Consulting/work content | Separate account |

When the user says "workspace" and context is ambiguous, ask which one.

---

## Repo structure

```
life-atlas/
├── .claude/                # Skills, commands, settings for Claude Code
├── device-schemas/         # Device-inventory yaml schema + README
├── folder-schemas/         # Conceptual schemas per top-level folder
├── environment/            # Shell scripts and environment config
├── scripts/                # Personal-data lint + git-hook installer
├── bookmarks/              # Bookmark strategy (not bookmark data)
├── docs/                   # Plans, session scratch (scratch is gitignored)
├── CLAUDE.md               # This file
└── README.md               # Public-facing overview
```

---

## Conventions

### Tone
- **README, schema docs, bookmarks README: external.** Pattern language only; specifics belong in the private reference-implementation file.
- **CLAUDE.md: internal.** First-person OK. Still pattern-language — this file is in the public repo too (per plan 0009). Specific device names, emails, employer references live in `~/Atlas/config/atlas/reference-implementation.md`.

### Platform-neutral language (rule)

When docs describe the *pattern*, use abstract terms:

- "cloud drive folder" — not the vendor name
- "primary workstation" / "local workstation" — not "Mac" (in pattern context)
- "NAS" / "network-attached storage" — not the vendor or device codename
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

### Atlas read/write boundaries
Atlas is the operational config store, not a no-go zone. The boundary is by subtree (reconciled with `.claude/settings.json` per plan 0009):

- **`~/Atlas/config/atlas/`** — read and write OK. Cross-device pattern→reference bindings (`reference-implementation.md`) and the lint deny-list (`lint-denylist.txt`) live here. Cloud-synced across the user's devices.
- **`~/Atlas/config/keys/`** — **never** read or write. Secrets only. Segregation is structural (no allow rule covers it) — not a fragile deny-below-allow.
- **Rest of `~/Atlas/config/`** — never read or write without explicit per-task approval.
- **`~/Atlas/docs/gear/`** — read and write OK. Device inventory (`inventory.yaml`) — the single source of truth for AI-context use cases, analogous to the Brewfile for tools.
- **Rest of `~/Atlas/docs/`** — never read or write. Personal documents (identity, health, finance, legal, etc.). Owned by the cloud drive app and the human.
- **`~/Atlas/workspace/atlas-ops/`** — read and write OK. The user's personal execution plans (formerly in this repo's `docs/plans/`).
- **Rest of `~/Atlas/workspace/`, `~/Atlas/archive/`, `~/Atlas/share/`** — never read or write without explicit per-task approval. These hold user-owned content.
- **Never commit** any content from `~/Atlas/docs/` (other than the inventory schema template), `~/Atlas/config/keys/`, or any other personal-data path into this repo.
- **Cloud-sync etiquette:** when writing to `~/Atlas/config/atlas/` or `~/Atlas/docs/gear/`, write to a scratch path first then `mv` into place (atomic from Drive's perspective). Avoid in-place edits during active sync.
- Don't assume a `~/Kit/` path exists — "Kit" was an earlier design that Atlas superseded.

---

## Session workflow

This repo uses these skills and commands:

| Invocation | What it does |
|---|---|
| `/session-start` | Review git state, open issues, active plans in `docs/plans/`; initialize `docs/session-scratch.md` |
| `/session-end` | Process scratch into GitHub issues; stage, commit, push |
| `/audit` | Scan the repo for drift (empty stubs, broken links, legacy references, cruft) |
| `/sync-check` | Verify on-disk reality on this workstation matches the schemas |
| `/plan-new <name> "<title>"` | Scaffold a new plan file in `docs/plans/` |

Skills live in `.claude/skills/`; commands live in `.claude/commands/`.

### Required GitHub labels

Session-end assumes these labels exist on `andrewhml/life-atlas`. Create with `gh label create` if missing:

- Type: `ready`, `idea`, `bug`, `feature`, `chore`, `docs`
- Priority: `priority/high`, `priority/medium`, `priority/low`
- Area: `area/device-schemas`, `area/folder-schemas`, `area/environment`, `area/bookmarks`, `area/docs`, `area/meta`, `area/drift`

---

## Permissions & constraints

Claude Code's permissions for this repo are configured in `.claude/settings.json`. The allowlist is intentionally narrow:

- **Write access (repo):** `.claude/*`, `docs/*`, plus targeted top-level paths needed for the public-guide surface: `CLAUDE.md`, `README.md`, `device-schemas/*`, `environment/*`, `scripts/*`
- **Write access (Atlas):** three narrow subtrees only:
  - `~/Atlas/config/atlas/*` — cross-device pattern→reference bindings + the lint deny-list (see "Pattern→reference bindings" below)
  - `~/Atlas/docs/gear/*` — device inventory (the filled-in `inventory.yaml` lives here; public repo holds only the template)
  - `~/Atlas/workspace/atlas-ops/*` — operational plans (the user's personal execution logs)
- **Bash allowed:** read-only git (`status`, `log`, `branch`, `diff`, `stash`, `show`), plus `gh issue`/`gh label` for session workflow
- **No write access** to any other repo path without explicit user approval
- **No access** to `~/Atlas/config/keys/` under any circumstances (segregation is structural — no allow rule covers it, not a deny-below-allow)
- **No access** to the rest of `~/Atlas/docs/` (`identity/`, `health/`, `finance/`, etc.), `~/Atlas/archive/`, `~/Atlas/share/`, or the rest of `~/Atlas/workspace/` without explicit per-task approval (personal content lives there)

If a task requires broader permissions, ask the user first. Don't silently expand the allowlist.

### Pattern→reference bindings (post-plan-0009)

The "Reference implementation" table lives in `~/Atlas/config/atlas/reference-implementation.md` (out of this repo, cloud-synced privately). When a task needs a specific name — which physical box IS the NAS, which workstation IS the primary, what's the user's email — read that file on demand. No session-start auto-load.

### Hook install on every clone

After cloning life-atlas on a new device, run `bash scripts/install-hooks.sh` to wire the personal-data lint into `.git/hooks/pre-commit`. The real deny-list lives at `~/Atlas/config/atlas/lint-denylist.txt` (cloud-synced via Atlas); confirm it's present before relying on the hook.

---

## Known drift (pending cleanup)

The repo is mid-reconciliation. Items tracked in GitHub issues:

- **`environment/macos_environment_init.sh`** — creates demo dirs from an earlier design. [#1]
- **`~/Atlas/README.md` on disk** — stale demo text. [#6]
- **Legacy `~/System/` on personal Mac** — pre-Atlas; migrate into `~/Atlas/config/`. [#5]
- **Empty environment stubs** — pending real content. [#2]
- **Obsidian vaults** — pending strategy decision. [#3]

Check `gh issue list --label area/drift` for current status.
