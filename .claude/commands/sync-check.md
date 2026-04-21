---
description: Verify the current workstation's filesystem matches life-atlas schemas. Use when setting up a new device, after reconfiguring a sync tool, or when the user asks "is everything in the right place." Checks cloud drive subfolders, local workspace and pictures paths, NAS mount, and flags legacy paths.
---

# /sync-check

Verify the on-disk reality matches what life-atlas documents.

## Usage

```
/sync-check
```

No arguments. Runs against the current workstation.

Life-atlas describes *target* structure. Actual filesystem state can drift. This command checks, without touching user data.

## What to check

1. **Cloud drive root** — does the described cloud-drive mount path exist? (Reference: `~/Atlas/`.)

2. **Cloud drive subfolders** — from README's folder tree, which described subfolders exist at the cloud drive root? Missing ones are flagged.

3. **Local outside-Atlas paths** — do described local paths exist? (Reference: `~/workspace/`, `~/Pictures/`.)

4. **NAS mount** — does the described NAS mount path exist? (Reference: `/Volumes/personal_folder/Atlas`.)

5. **Legacy paths** — does `~/System/`, `~/Kit/`, or any `~/*-Example/` directory exist? These are legacy / leftover and flagged for cleanup.

6. **Repo's own expected paths** — `docs/` exists (session-scratch location); `.claude/skills/` contains at least one `SKILL.md`; `.claude/commands/` contains at least one command file.

## How to run

Use `Bash` for filesystem existence checks. **Do not `ls` contents or Read files inside user data paths** — only check for directory existence.

Parallelize checks (one Bash call per path):

```bash
test -d ~/Atlas && echo "✓ ~/Atlas" || echo "✗ ~/Atlas (MISSING)"
test -d ~/Atlas/config && echo "✓ ~/Atlas/config" || echo "✗ ~/Atlas/config"
test -d ~/Atlas/docs && echo "✓ ~/Atlas/docs" || echo "✗ ~/Atlas/docs"
# ... etc
```

For legacy paths, presence is a **warning**:

```bash
test -d ~/System && echo "⚠ ~/System (legacy; issue #5)"
test -d ~/Kit && echo "⚠ ~/Kit (pre-Atlas; should not exist)"
```

## Report format

```
Sync-check: reference implementation

Cloud drive root:
  ✓ ~/Atlas/
  ✓ ~/Atlas/archive/
  ✓ ~/Atlas/config/
  ✓ ~/Atlas/docs/
  ✗ ~/Atlas/share/     (missing; README lists this)

Outside Atlas:
  ✓ ~/workspace/
  ✓ ~/Pictures/

NAS:
  ✓ /Volumes/personal_folder/Atlas

Legacy:
  ⚠ ~/System/                   (legacy; GH issue #5)
  ⚠ ~/Atlas-Example-Aliases.txt (leftover from init-script; GH issue #1)

Repo infra:
  ✓ docs/
  ✓ .claude/skills/

Summary: 1 missing (Atlas/share), 2 legacy warnings.

Recommendations:
  - Create ~/Atlas/share/ in Google Drive, or update README if intentionally absent
  - Clean up ~/Atlas-Example-Aliases.txt (issue #1 covers the rewrite)
```

## When to run

- After setting up a new device
- When `/audit` or conversation suggests drift between docs and reality
- Before starting work that assumes the described structure

## Do NOT

- Don't list contents of `~/Atlas/` or any subfolder — that's user data
- Don't Read files inside the cloud drive or NAS mount
- Don't create missing folders without explicit user approval (just report)
