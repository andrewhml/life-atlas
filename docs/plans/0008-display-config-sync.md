# Plan 0008 — Display config sync (display_switch + BetterDisplay layouts) under Atlas

**Status:** Draft
**Issue:** _(none yet — create after audit if scope holds)_
**Created:** 2026-05-25

---

## Goal

Bring AM2's display tooling configuration over to AM5 and establish an Atlas-backed sync model so future edits propagate without manual re-export. Two apps in scope:

- **`display_switch`** — haimgel's DDC/CI input-switch CLI (in `environment/Brewfile`, managed by `brew services`). Drives the external monitors' KVM-style input switch when the active host changes.
- **BetterDisplay** — display management app, primarily for DDC sub-display layouts and per-display brightness/HDR pinning. Cask: `waydabber/betterdisplay/betterdisplay`.

This plan was explicitly carved out of Plan 0007 ("display switch / KVM setup — separate plan") so it stays focused on display tooling only.

## Scope

- **In:**
  - Audit current state on both AM2 and AM5 for `display_switch` and BetterDisplay
  - Define an Atlas folder layout under `~/Atlas/config/apps/` for any portable config
  - One-time port AM2 → AM5 for whatever survives the audit
  - Establish symlink-based sync where safe (regular files), one-shot copy where not (cfprefsd-owned plists)
- **Out:**
  - VS Code / Cursor display-related extensions
  - macOS native display arrangement (`Displays.prefPane`) — Apple-managed, not portable
  - DDC-related Brewfile changes (Brewfile reconciliation lives in Plan 0007)
  - PC (AM5 secondary, Windows) display config — separate concern; this plan is macOS-only

## Background

Reconnaissance on AM5 (this session, host=`AM5`):

- `display_switch` binary present at `/opt/homebrew/bin/display_switch` (Brewfile-installed)
- `brew services list` reports `display_switch  none` — not running, not loaded as a LaunchAgent
- No config at `~/Library/Application Support/display-switch/` or `~/.config/display-switch/`
- BetterDisplay installed; `~/Library/Preferences/pro.betterdisplay.BetterDisplay.plist` exists with 166 entries — mostly auto-discovered display state (Display:2, Display:3 EDID-derived properties), Paddle license activation hash, and a small set of user-configured menu density flags
- BetterDisplay layout files: `~/Library/Application Support/BetterDisplay/762421.padl` (1.7 KB, binary plist) and `762421.spadl` (1.0 KB, binary plist containing `license_data`)

AM2 state: **unknown from this session.** The audit phase resolves this.

What we already know about the file-format constraints:

- `display_switch` config is a plain INI — safe to relocate + symlink
- BetterDisplay `.padl` / `.spadl` are regular files the app reads/writes directly (not cfprefsd-managed) — safe to symlink
- The main BetterDisplay `.plist` lives in the macOS Preferences store managed by `cfprefsd`, which atomic-renames on write and will break a symlink. If we want it portable, the right pattern is periodic `defaults export` snapshots, not a symlink.

## Approach

### Phase 1 — Audit AM2

**Goal:** Establish ground truth on AM2 so the rest of the plan is informed, not speculative.

**Steps:**
1. On AM2, inspect:
   - `~/Library/Application Support/display-switch/` and `~/.config/display-switch/` for any `display-switch.ini` (or equivalent)
   - `brew services list` to see if the LaunchAgent is loaded
   - `~/Library/Preferences/pro.betterdisplay.BetterDisplay.plist` content via `defaults read` — diff the user-configured keys (menu density, tagged displays, anything non-auto-discovered) against AM5's
   - `~/Library/Application Support/BetterDisplay/*.padl` and `*.spadl` — file count, sizes, license-ID suffix
2. Record findings inline in this plan under a new "Audit results" section.
3. Decide go/no-go for each app based on whether there's actually anything worth syncing.

**Exit criteria:** Audit results captured; each app marked **port**, **skip**, or **needs more info**.

### Phase 2 — `display_switch` Atlas sync (conditional on Phase 1)

**Goal:** If AM2 has a working `display_switch` config, make it the cross-device source of truth via Atlas.

**Steps:**
1. Create `~/Atlas/config/apps/display-switch/` with a short `README.md` describing the symlink convention.
2. On AM2: move the existing config into Atlas; symlink it back to the original path.
3. On AM5: install `display_switch` via Brewfile if not already done; symlink `~/Atlas/config/apps/display-switch/display-switch.ini` → expected config path.
4. `brew services restart display_switch` on both machines; confirm the service comes up cleanly and the LaunchAgent picks up the new path.
5. Document the symlink + service-restart step in `environment/apps-manual.md` under the existing `display_switch` mention.

**Exit criteria:** Both machines run `display_switch` reading from Atlas; editing the file on either machine takes effect on the other (after a service restart).

### Phase 3 — BetterDisplay layout sync (conditional on Phase 1)

**Goal:** If AM2's `.padl`/`.spadl` files contain meaningful pinning data not present on AM5, sync them via Atlas. Skip the main plist (cfprefsd-unsafe; menu-density settings are too thin to justify a snapshot script).

**Steps:**
1. Create `~/Atlas/config/apps/betterdisplay/` with a short `README.md` (symlink convention, what's intentionally not synced).
2. On AM2: copy `~/Library/Application Support/BetterDisplay/*.padl` and `*.spadl` into Atlas; replace the originals with symlinks.
3. On AM5: rename the existing local `.padl`/`.spadl` to `*.local-backup` (don't delete — license-ID-keyed; recovery insurance); symlink the Atlas-backed files in.
4. Open BetterDisplay on AM5; confirm displays appear as expected and DDC controls work. If the layout is rejected or AM5's displays don't map cleanly, fall back to the `.local-backup` files and document the incompatibility in this plan.
5. Add a one-paragraph entry to `environment/apps-manual.md` under the existing BetterDisplay section describing the layout symlink and the "plist deliberately not synced" decision.

**Exit criteria:** Either (a) both machines read layouts from Atlas and DDC behavior is preserved, or (b) the attempt failed cleanly with a recorded reason, layouts left machine-local, and Phase 3 marked Abandoned.

## Risks

- **`.padl` files may be license-ID-keyed.** The filename `762421.padl` matches the `Paddle-BetterDisplay-762421-SD` plist key. If the license activates with a different Paddle ID on AM2, the filename diverges and a straight symlink rename strategy collides. Mitigation: Phase 1 audit compares the license-ID suffix between machines before Phase 3 commits.
- **BetterDisplay may rewrite `.padl` via atomic-rename**, breaking the symlink the same way cfprefsd would. We don't know this for sure — the files are regular files in Application Support, which usually means the app does in-place writes, but it's not guaranteed. Mitigation: after symlink setup, change a display setting in the app, then verify the symlink is intact (`readlink` returns the Atlas path).
- **`display_switch` LaunchAgent path resolution.** The Homebrew-generated `.plist` for `display_switch` may hard-code the original config path. If we move the file and symlink it, the LaunchAgent should still read through the symlink — but `brew services restart` may regenerate the plist and could surprise us. Mitigation: confirm the LaunchAgent contents before/after the move.

## Open questions

- Is `display_switch` actually configured and in use on AM2 today? AM5 has it installed but not running; we don't know AM2's state. Phase 1 resolves this.
- Does the user actively rely on BetterDisplay pinning today, or is it mostly cosmetic / passive? If passive, Phase 3 may not be worth doing — even a one-time copy might be unnecessary. The user's prior message ("we may not need the better display configuration as I don't believe it dictates much today") suggests this is plausibly skip-able.
- Should the Atlas folder pattern be `apps/display-switch/` (kebab-case, matches Brewfile name) or `apps/displayswitch/` (matches `display_switch` underscore form)? Lean kebab-case to match `Alfred`, `Raycast`, `Transmit` neighbors.

## Status log

- 2026-05-25 — Plan drafted (Phases 1–3 outlined; AM2 audit needed before Phase 2/3 can start)
