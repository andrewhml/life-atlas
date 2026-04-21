# Plan 0001 — Rewrite macos_environment_init.sh for the Atlas model

**Status:** Draft
**Issue:** #1
**Created:** 2026-04-21

---

## Goal

Replace the existing `environment/macos_environment_init.sh` (which creates `~/Atlas-Example/`, `~/Workspace-Example/`, `~/Media-Example/`, `~/System-Example/` demo directories from an earlier design) with a bootstrap script that correctly sets up a new macOS primary workstation under the real Atlas model.

The script should be safe to run on a machine that already has partial Atlas setup, idempotent across reruns, and opinionated about what it will and won't touch.

## Scope

- **In:**
  - Verify Google Drive for Desktop is installed
  - Verify `~/Atlas/` exists and is being synced (fail loudly if not — don't create it, since the Drive app owns that path)
  - Create local-only outside-Atlas paths: `~/workspace/`, `~/Pictures/` with year-folder scaffolding on request
  - Prompt for NAS mount (`/Volumes/personal_folder/Atlas`) and provide SMB mount helper
  - Install core CLI tooling via Homebrew (via existing Brewfile or inline bootstrap)
  - Configure git global identity if not already set
  - Clean up any leftover `~/*-Example/` directories from previous runs (prompt before deletion)
- **Out:**
  - Creating or mutating anything inside `~/Atlas/` (Drive's territory)
  - Installing every app in the user's ecosystem (that's `devtools.sh` + Brewfile territory)
  - Configuring macOS defaults (that's `defaults_settings.sh`)
  - Setting up the NAS itself (that's `nas-setup.md`)

## Approach

### Phase 1 — Pre-flight checks

**Goal:** Fail fast if the environment isn't ready.

**Steps:**
1. Check macOS version (>= 14)
2. Check Google Drive for Desktop is installed (`/Applications/Google Drive.app`)
3. Check `~/Atlas/` exists and is non-empty
4. Check user confirms this is the primary personal Mac (not a work Mac)

**Exit criteria:** All checks pass or the script exits with a clear message.

### Phase 2 — Local directory scaffolding

**Goal:** Create local-only paths the Atlas model relies on.

**Steps:**
1. `mkdir -p ~/workspace/{personal,work}`
2. `mkdir -p ~/Pictures`
3. Optionally invoke `macos_create_photo_year.sh $(date +%Y)` to scaffold the current year

**Exit criteria:** Paths exist and are writable.

### Phase 3 — Legacy cleanup

**Goal:** Remove leftover example directories from prior runs of this script or the old Kit-based design.

**Steps:**
1. Detect `~/Atlas-Example/`, `~/Workspace-Example/`, `~/Media-Example/`, `~/System-Example/`, `~/Atlas-Example-Aliases.txt`, `~/Kit/`
2. Prompt user with list of detected legacy items
3. On confirmation, delete

**Exit criteria:** No legacy directories remain.

### Phase 4 — Tooling

**Goal:** Core CLI toolchain is present.

**Steps:**
1. Check Homebrew is installed; install if missing
2. Run `brew bundle --file=<path>` if a Brewfile exists in the repo (reference `brewfile.md`)
3. Check `gh`, `git`, `zsh` are on PATH
4. Prompt for git global identity if not set

**Exit criteria:** Required commands work.

### Phase 5 — NAS mount helper (optional)

**Goal:** Make it easy to mount the NAS Atlas mirror when on the home network.

**Steps:**
1. Provide an `alias mount-atlas-nas='mount_smbfs ...'` snippet for `shell-aliases.sh`
2. Optionally create a LaunchAgent to auto-mount on login (prompt first)

**Exit criteria:** Mount works from the alias.

## Risks

- **Google Drive not installed or signed in:** script can't create `~/Atlas/`; user has to do this manually. Script must not attempt to create it. Pre-flight catches this.
- **Running on work Mac:** could sync personal Atlas to a company device. Pre-flight asks the user to confirm primary personal Mac.
- **Destructive cleanup:** user might have put real work in `~/*-Example/` since the init script ran. Prompt before every delete; show contents count.
- **Homebrew install hangs:** first install prompts for sudo and can stall. Document expectations up front.

## Open questions

- Should the NAS mount helper live in this script, or in `nas-setup.md` / a separate `mount-nas.sh`? Favor separation (this script is about the Mac, not the NAS).
- Should the script write a marker file (`~/.life-atlas-initialized`) so reruns are no-ops? Probably yes, but make it optional via `--force`.
- Should the script be interactive-only, or also support non-interactive CI-style runs? Probably interactive for now; revisit if onboarding a new Mac becomes routine.

## Status log

- 2026-04-21 — Plan drafted as part of Phase 3 refinement (issue #1)
