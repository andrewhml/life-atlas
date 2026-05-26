# Plan 0008 — Display config sync (display_switch + BetterDisplay layouts) under Atlas

**Status:** Substantially complete — Phase 1 audit closed; Phase 2 end-to-end on both machines (`/opt/homebrew/bin/betterdisplaycli` from formula on AM2 + AM5, Atlas .ini cutover, both services running and parsing through the symlink, AM5 verified live with USB device connected). Phase 3 abandoned. Open follow-ups: AM5 USB-disconnect verification (passive — next time the watched device unplugs), optional AM2 cleanup of legacy `/usr/local/bin/betterdisplaycli` (Phase 2 step 10).
**Issue:** _(none — completed end-to-end within plan scope without standalone issue tracking)_
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

AM2 state: see [Audit results](#audit-results) below.

What we already know about the file-format constraints:

- `display_switch` config is a plain INI — safe to relocate + symlink
- BetterDisplay `.padl` / `.spadl` are regular files the app reads/writes directly (not cfprefsd-managed) — safe to symlink
- The main BetterDisplay `.plist` lives in the macOS Preferences store managed by `cfprefsd`, which atomic-renames on write and will break a symlink. If we want it portable, the right pattern is periodic `defaults export` snapshots, not a symlink.

## Audit results

Audit run on AM2 on 2026-05-25. Phase 1 step 1 inspections below.

### `display_switch`

- Binary at `/opt/homebrew/bin/display_switch` (Brewfile-installed)
- LaunchAgent at `~/Library/LaunchAgents/homebrew.mxcl.display_switch.plist`; `brew services list` reports `started`; process running (pid 1468 at audit time)
- LaunchAgent plist hard-codes only the binary path (`/opt/homebrew/opt/display_switch/bin/display_switch`); no `-c` flag, no env vars — the binary discovers its config file via its own search algorithm
- **Config found at non-standard path**: `~/Library/Preferences/display-switch.ini` (NOT at `~/Library/Application Support/display-switch/` or `~/.config/display-switch/` as Phase 1 expected). 3 lines:

  ```ini
  usb_device = "05e3:0610"
  on_usb_connect_execute = "/usr/local/bin/betterdisplaycli set -namelike=LG -ddcAlt -vcp=inputSelectAlt -value=209"
  on_usb_disconnect_execute = "/usr/local/bin/betterdisplaycli set -namelike=LG -ddcAlt -vcp=inputSelectAlt -value=208"
  ```

- Log at `~/Library/Logs/display-switch/display-switch.log` confirms the service is actively reacting to USB events on the laptop alone (USB device disconnected → "Did not detect any DDC-compatible displays" — expected when the external setup is detached)
- `betterdisplaycli` lives at `/usr/local/bin/betterdisplaycli` (owner `root:wheel`, ~218 KB) — installed by the BetterDisplay app's "Install CLI tool" action, **not** by Homebrew. The Apple Silicon Homebrew prefix `/opt/homebrew/bin/` has no symlink for it

**Verdict: PORT.** Config is small, intentional, and used. Atlas-backed symlink is straightforward provided Phase 2 confirms `/usr/local/bin/betterdisplaycli` exists on AM5 (likely fine since BetterDisplay is installed on both — but verify before the move).

**Phase 2 amendments needed:**
- Source path is `~/Library/Preferences/display-switch.ini`, not the App Support / `.config` paths the original draft mentioned
- Phase 2 step 4 should additionally verify `betterdisplaycli` path is identical on AM5 before/after move

### BetterDisplay plist

- `~/Library/Preferences/pro.betterdisplay.BetterDisplay.plist`: 61,428 bytes; `defaults read` produces 805 lines (vs AM5's ~166)
- 11 tagged displays in `displayTagIDs = "[2,3,4,28,31,32,41,45,52,53,57]"` (vs AM5's 2) — AM2 has accumulated per-display state for many more monitors over time
- License-ID `762421` matches AM5 (Paddle ID is per-account, not per-machine). Activation hash: `Paddle-BetterDisplay-762421-SD = 0c07c1953422a66d40c9ddb1376d08bf3e33846b61b7476eb35ac74c315560c3`
- Real user-configured settings present (filtered for non-auto-discovered keys):
  - **Custom resolution override for display `v9747m8227`**: `manualResolutionList = "[[1920,550,3]]"`, `overrideDefaultResolution = 1`, `overridesEnabled = 1`, default resolution 3840×1100@60Hz. This is meaningful config, not auto-discovery.
  - Customized menu density across ~30 `menuLevel*` keys (mix of `more`/`less`/`hide`)
  - `showAdvancedDisplaysSettings = 1`, `showAdvancedMenuAppearance = 1`, `showAdvancedVirtualScreensSettings = 1`

**Verdict: SKIP per plan** (cfprefsd-unsafe — plan already excluded). Worth flagging: the resolution override above is the only meaningful piece of cross-machine-portable config in the plist; it will not propagate to AM5 unless a future plan revisits the cfprefsd-export approach. Not in scope for 0008.

### BetterDisplay layout files (`.padl` / `.spadl`)

- `~/Library/Application Support/BetterDisplay/762421.padl` (1,673 bytes) and `762421.spadl` (1,017 bytes)
- Both are NSKeyedArchiver-wrapped binary plists (`Apple binary property list` per `file(1)`)
- `.padl` schema: `file_version=1`, `sdk_version=4`, `file_platform=mac`, `product_data` (1,280-byte opaque blob)
- `.spadl` schema: `file_version=1`, `sdk_version=4`, `file_platform=mac`, `license_data` (624-byte opaque blob)
- Same license-ID `762421` as AM5; AM5's files are similar size (~1,700 / ~1,000 bytes per the original recon) — both machines appear to already have functional license activation independently

**Verdict: SKIP recommended.** Contents are opaque license/activation blobs (no layout/display-arrangement payload visible in the unwrapped structure). AM5 already has equivalent-size files; syncing would gain nothing demonstrable and risks license-activation flakiness. The plan's Phase 3 open question ("does the user actively rely on BetterDisplay pinning today") resolves to "no observable cross-machine value worth porting."

If the user later finds AM5 needs a layout state AM2 has and AM5 doesn't, revisit with concrete evidence — but absent that, leave both machines machine-local.

### Summary

| App | Verdict | Action |
|---|---|---|
| `display_switch` | **Port** | Proceed with Phase 2 (with source-path amendment noted above; betterdisplaycli must be installed on AM5 first — not yet done) |
| BetterDisplay plist | Skip | Out of scope per plan (cfprefsd-unsafe) |
| BetterDisplay `.padl` / `.spadl` | **Abandoned** | Phase 3 abandoned — no demonstrable cross-machine value |

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

**Goal:** Make AM2's working `display_switch` config the cross-device source of truth via Atlas; bring AM5 from half-install to fully configured. Both machines converge on a single Homebrew-managed `betterdisplaycli` install path.

**Strategy pivot 2026-05-26 (Option B).** Initial plan called for the BetterDisplay GUI "Install CLI tool" menu action on AM5 to mirror AM2's `/usr/local/bin/betterdisplaycli` (a ~218 KB launcher owned `root:wheel`). User decision: drop the GUI step in favor of the Homebrew formula `waydabber/betterdisplay/betterdisplaycli`, which installs a real CLI binary to `/opt/homebrew/bin/betterdisplaycli` via `brew bundle`. Trade-off accepted: formula has no published bottle (`brew info` shows none), so it compiles from source via Swift and requires full Xcode ≥14 on each machine — both AM5 and AM2 were missing it pre-pivot and have since installed Xcode 26.5. The Homebrew **cask** shim at `/opt/homebrew/bin/betterdisplaycli` from `waydabber/betterdisplay/betterdisplay` is a different artifact (bare `exec` to the GUI app binary) and is NOT a substitute — installing the formula overwrites/replaces it with the real binary. Empirical test of the cask shim:

```
$ /opt/homebrew/bin/betterdisplaycli version
Some uninterpreted or system arguments are present - proceeding with app launch.
Please note that the app already had 2 running instances and now an additional instance was started.
```

**State after AM2 block (Step 2 below, complete 2026-05-25 pre-pivot):**
- AM2: `display_switch` running. `~/Library/Preferences/display-switch.ini` symlinked → `~/Atlas/config/apps/display-switch/display-switch.ini`. .ini currently calls `/usr/local/bin/betterdisplaycli` (the GUI-installed one).
- AM5: Atlas .ini visible (synced). No symlink, service not started. `display_switch` half-installed (binary present, LaunchAgent unloaded).
- Both: `/opt/homebrew/bin/betterdisplaycli` shim from the cask is present (do not rely on it).

**Steps:**

1. ~~Create `~/Atlas/config/apps/display-switch/` with a short `README.md`~~ **DONE 2026-05-25.**

2. ~~**On AM2** (move config into Atlas without dropping service): move .ini → Atlas, symlink back, restart service.~~ **DONE 2026-05-25.**

3. **Update Brewfile** to add the `betterdisplaycli` formula. **DONE 2026-05-26.** Brewfile now declares `brew "waydabber/betterdisplay/betterdisplaycli"` and the tap comment is updated to reflect its real consumer.

4. **Install Xcode ≥14 on each machine that doesn't have it.** **DONE 2026-05-26.** Required for the formula to compile (no bottle). User-driven; App Store install, multi-GB. AM5 and AM2 were both verified missing (`xcode-select -p` reported CLT only); both installed Xcode 26.5 (build 17F42).

5. **Run `brew bundle` on each machine** (from `environment/` in the life-atlas repo) to install the formula. **DONE 2026-05-26.** Verify after each run:
   ```
   file /opt/homebrew/bin/betterdisplaycli   # should report "Mach-O 64-bit executable arm64"
   betterdisplaycli help                      # should print CLI help, not spawn the GUI
   ```
   - **AM5:** hit a cask-shim link conflict; resolved with `brew link --overwrite betterdisplaycli`. (Don't `brew uninstall --cask betterdisplay` — that removes the BetterDisplay GUI app entirely. Use `--overwrite` to keep both installed with the formula's real binary winning at `/opt/homebrew/bin/betterdisplaycli`.)
   - **AM2:** linked cleanly without intervention — the cask shim was overwritten by `brew bundle` automatically. Did not need `--overwrite`. Reason for the AM2/AM5 divergence is not understood; documented for next time.
   - Both machines verified: `file` reports `Mach-O 64-bit executable arm64`; `brew info` shows `[Linked]`; `betterdisplaycli help` returns CLI help text.

6. **Coordinated `.ini` cutover.** **DONE 2026-05-26.** Edited `~/Atlas/config/apps/display-switch/display-switch.ini` via scratch+mv (cloud-sync etiquette); both `on_usb_*_execute` lines now call `/opt/homebrew/bin/betterdisplaycli`. Diff-verified the change was exactly 2 path replacements and nothing else.

7. **AM2: restart service** to pick up the new path. **DONE 2026-05-26.** `brew services restart display_switch` ran cleanly; log shows `Configuration loaded` with both `on_usb_*_execute` values now pointing at `/opt/homebrew/bin/betterdisplaycli`. USB-event verification deferred — the laptop is currently detached from the external setup and the existing `Did not detect any DDC-compatible displays` log line is the expected no-displays-attached condition, not a `betterdisplaycli` failure. Verify on next LG monitor reconnect.

8. **AM5: wire up and start.** **DONE 2026-05-26.**
   1. ~~`ln -s ~/Atlas/config/apps/display-switch/display-switch.ini ~/Library/Preferences/display-switch.ini`.~~ Done; `readlink` confirms target.
   2. ~~`brew services start display_switch`.~~ Done; `brew services list` reports `started` (LaunchAgent loaded successfully on first start, no restart needed).
   3. ~~USB-event verification.~~ Got it automatically — device `05e3:0610` was already connected at service-start time, so `display_switch` ran the connect path immediately: `External command '/opt/homebrew/bin/betterdisplaycli set -namelike=LG -ddcAlt -vcp=inputSelectAlt -value=209' executed successfully` (twice — once for each connected display). No `Exited with status 1`. Two transient `Failed to get current input` errors at init are standard DDC polling noise unrelated to the cutover. **Open follow-up:** USB-disconnect path is still passive-unverified — will exercise next time the watched device unplugs.

9. **Documentation.** **DONE 2026-05-26.** `environment/apps-manual.md` reworked under this PR: BetterDisplay setup notes point at the formula; the `betterdisplaycli` formula entry documents the Xcode ≥14 prereq, the cask-shim trap, and the empirically-observed `brew link --overwrite betterdisplaycli` fix (added post-Option-B after AM5 hit it). The GUI install + cask shim remain documented as historical/alternative paths.

10. **AM2 cleanup (optional, low-priority).** AM2 still has `/usr/local/bin/betterdisplaycli` from the original GUI install. Harmless to leave; if cleanliness is preferred, remove it after step 7 verifies the formula path works (`sudo rm /usr/local/bin/betterdisplaycli`).

**Exit criteria:** Both machines run `display_switch` reading from Atlas, with `betterdisplaycli` resolved through `/opt/homebrew/bin/` from the Homebrew formula. Editing the .ini on either machine takes effect on the other after a service restart.

### Phase 3 — BetterDisplay layout sync (conditional on Phase 1)

**Status: Abandoned (2026-05-25).** Phase 1 audit resolved this: `.padl` / `.spadl` files on AM2 contain only opaque license/activation blobs (no layout/display-arrangement payload visible), and AM5 already has equivalent-size files from its own independent activation. No demonstrable cross-machine value. Leaving both machines machine-local. If concrete evidence later surfaces that AM5 is missing layout state AM2 has, reopen with that evidence.

Original goal (retained for reference):

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
- 2026-05-25 — Phase 1 audit complete on AM2. Results recorded above. Verdicts: `display_switch` → port (Phase 2 ready with source-path amendment); BetterDisplay plist → skip (per plan); BetterDisplay `.padl`/`.spadl` → skip recommended (no demonstrable cross-machine value).
- 2026-05-25 — Phase 3 marked **Abandoned** following audit. Phase 2 amended with explicit AM5 prereq: install `betterdisplaycli` (not yet done) before symlinking the .ini.
- 2026-05-25 — Phase 2 rewritten with per-machine step blocks. AM2 (move config into Atlas, symlink back, restart service) + AM5 (half-install → install betterdisplaycli → symlink → first-start LaunchAgent → verify on next USB event). Ordering preserved so AM5 first-time setup can't hit `Exited with status 1` from missing `betterdisplaycli`.
- 2026-05-25 — **Phase 2 Step 1 + AM2 block complete.** Created `~/Atlas/config/apps/display-switch/` with README. Moved `display-switch.ini` into Atlas via scratch+mv (cloud-sync etiquette), diff-verified, removed original, symlinked back to `~/Library/Preferences/display-switch.ini`. `brew services restart display_switch` clean; new pid 15713; log confirms `Configuration loaded ("/Users/andrewlee/Library/Preferences/display-switch.ini")` reads through the symlink and parses all 3 keys. AM5 block remains; documentation step waits for AM5 completion.
- 2026-05-26 — **Strategy pivot to Option B.** User-directed switch from GUI "Install CLI tool" (`/usr/local/bin/betterdisplaycli`) to Homebrew formula `waydabber/betterdisplay/betterdisplaycli` (`/opt/homebrew/bin/betterdisplaycli`). Confirmed: formula has no bottle → full Xcode ≥14 required on each machine. Cask shim from `waydabber/betterdisplay/betterdisplay` proven non-equivalent via empirical test (spawns extra GUI instance instead of returning a version string). Phase 2 rewritten with new step ordering: Brewfile update → Xcode install → `brew bundle` on each machine → coordinated `.ini` path cutover → AM2 restart → AM5 symlink + start. Brewfile updated on this date.
- 2026-05-26 — **AM2 Phase 2 steps 4–7 complete.** Xcode 26.5 installed; `brew bundle install` succeeded with no cask-shim conflict (AM2 linked cleanly without `--overwrite`, unlike AM5); `betterdisplaycli` verified as real Mach-O arm64 at `/opt/homebrew/bin/`; `.ini` cutover applied to `~/Atlas/config/apps/display-switch/display-switch.ini` via scratch+mv (diff-verified, exactly 2 path replacements); `brew services restart display_switch` clean, log confirms new path loaded into memory. README on Atlas refreshed to match. `apps-manual.md` reworked in this commit to add the `brew link --overwrite betterdisplaycli` fix observed on AM5. Remaining: AM5 step 8 (symlink + first-start), USB-event verification on next LG reconnect, optional AM2 cleanup of legacy `/usr/local/bin/betterdisplaycli` (step 10).
- 2026-05-26 — **AM5 Phase 2 step 8 complete — Phase 2 substantially closed.** Symlinked `~/Library/Preferences/display-switch.ini` → Atlas, `brew services start display_switch` clean on first start, log shows `Configuration loaded` reading the new path with both `betterdisplaycli` invocations resolving to `/opt/homebrew/bin/`. USB device `05e3:0610` was already connected, so the connect path ran immediately and the formula binary executed cleanly twice (once per attached display) with no `Exited with status 1`. End-to-end verified. Plan status promoted to **Substantially complete**. Open follow-ups (low priority): AM5 disconnect-path verification on next unplug; optional AM2 cleanup of legacy `/usr/local/bin/betterdisplaycli`.
