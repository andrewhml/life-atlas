---
description: Find repo drift — empty stubs, broken links, legacy term references, OS cruft
---

# /audit

Scan the life-atlas repo for drift.

## Usage

```
/audit
```

No arguments. Scans the whole repo.

## What to check

1. **Empty or near-empty files** — any `.md` or `.sh` file under 100 bytes that isn't a legitimate stub (stubs have a header + TODO list). Flag with path and size.

2. **TODO-only stubs** — files with a `**Status:** pending` header. Report as informational (they're intentional), but flag if the repo's age suggests they should be filled by now.

3. **Broken cross-references** — markdown links `](path)` to other files in the repo that don't exist. Use Grep with pattern `\]\([^http][^)]+\)` in `.md` files; verify each target exists.

4. **README vs filesystem drift** — paths mentioned in `README.md` folder trees vs what actually exists in the repo. Flag missing files and orphans.

5. **Legacy concept references** — Grep across the repo for `Kit/`, `LiveDocs/`, `~/Vault/` (these were earlier designs). Flag matches in any `.md` or `.sh` file that isn't a `CHANGELOG` or history record.

6. **Editor / OS cruft in the working tree** — `.DS_Store`, `Thumbs.db`, `*.swp` that `.gitignore` should catch. Use `git status --short --ignored` to see what's on disk but ignored, and `git ls-files` for tracked.

## How to run

Parallelize where possible. Each check is independent:

- Glob `**/*.md` and `**/*.sh` — get the candidate set
- Use Bash `wc -c` on each for size (or batch with `find` / `stat`)
- Grep for legacy terms: `Kit/|LiveDocs/|~/Vault/`
- Grep for broken-link patterns
- Run `git status --short` for cruft check

## Report format

Single summary, grouped by severity:

```
Audit: life-atlas

🚨 Broken cross-references (N):
  - CLAUDE.md:42 → ../missing.md
  - README.md:88 → device-schemas/typo.md

⚠️  Legacy references (N):
  - some-file.md:12 → "Kit/"

ℹ️  TODO stubs (N) — intentional:
  - environment/defaults_settings.sh
  - environment/devtools.sh
  ...

ℹ️  Empty / near-empty files (N):
  - none

ℹ️  Cruft in working tree (N):
  - none

Recommendations:
  - Fix broken links in CLAUDE.md:42 and README.md:88
  - Legacy "Kit/" reference in some-file.md is likely stale — update to Atlas language
```

Keep the output focused. Don't list every clean file; list violations.

## When to run

- At the start of a session (optional — session-start can call it on demand)
- Before a major commit to verify nothing drifted
- When the repo "feels off"
