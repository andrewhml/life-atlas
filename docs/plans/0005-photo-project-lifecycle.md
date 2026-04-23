# Plan 0005 — Photo + project lifecycle operating model

**Status:** In Progress
**Issue:** — (create on session-end)
**Created:** 2026-04-22
**Depends on:** Plan 0002 (data 3-2-1 consolidation) — complementary, not blocking

---

## Goal

Establish a durable, automated operating model for photos and project files: continuous backup off the Mac, automated mirror to the external SSDs, a real offsite copy at brother's UGREEN DXP6800 in Vermont, and a year-close gate that uses Immich indexing as the forcing function. Plan 0002 addresses the iCloud/Immich crisis; this plan addresses the day-to-day pipeline that keeps the crisis from recurring.

## Scope

- **In:**
  - Offsite replication Peddocks2 → brother's UGREEN DXP6800 over Tailscale
  - Noisy Cricket physical rotation to brother's (bootstrap + standing redundant offsite)
  - Continuous (hourly or on-change) Mac → NAS backup of `~/Pictures/` and project paths, beyond Time Machine
  - Carbon Copy Cloner automation (on-mount or scheduled)
  - Year-close gate: archived only when Carbonizer + Noisy Cricket + NAS + brother's UGREEN + Immich all have verified copies
  - Carbonizer Apple Photos library disposal (201 GB reclaim on each SSD)
  - exFAT hygiene playbook (eject discipline, monthly First Aid, cruft cleanup)
  - Mac ↔ Carbonizer authority reconciliation (Carbonizer currently has content Mac does not)
  - Project files as first-class archive target (same tiers as photos)
  - Post-M5-upgrade adjustments
- **Out:**
  - Immich dedup / iCloud unblock (Plan 0002)
  - NAS RAID rebuild (Plan 0002 Phase 4)
  - Obsidian vault sync (Plan 0002 Phase 5)
  - Filesystem migration off exFAT — user declined (Windows read compatibility required)
  - Project workflow / "shipping" process itself (tooling, deadlines, publish flow) — separate concern

---

## Inventory snapshot (2026-04-22)

### Disk usage

| Path | Size | Notes |
|---|---|---|
| MacBook internal SSD (Data volume) | 805 / 926 GB used, **69 GB free (93% full)** | Blocks Finder iOS backups; forces aggressive archival until M5 upgrade |
| `~/Pictures/2025 Photos/` | 246 GB | Mac copy of current year; 38 GB behind Carbonizer |
| `~/Pictures/2026 Photos/` | 7.3 GB | Current year in progress |
| `~/Pictures/Lightroom Library.lrlibrary/` | 6.2 GB | Lightroom catalog |
| `~/Pictures/Photos Library.photoslibrary/` | ~0.5 GB | Effectively empty; not used as creative surface |
| `~/Pictures/YYYY Photos/` | 32 KB | Template stub — delete |
| Carbonizer (SanDisk 2TB exFAT) | **1.3 TB used / 502 GB free (74%)** | Primary external working mirror |
| `/Volumes/Carbonizer/Photos/Photo Files/2024 Photos/` | 546 GB | **Only on Carbonizer + Noisy Cricket — single-location risk** |
| `/Volumes/Carbonizer/Photos/Photo Files/2025 Photos/` | 284 GB | 38 GB more than Mac — authority drift |
| `/Volumes/Carbonizer/Photos/Photos Library.photoslibrary/` | 201 GB | Old Apple Photos library; disposable per user |
| `/Volumes/Carbonizer/Photos/Remote Year/` | 106 GB | Travel archive |
| `/Volumes/Carbonizer/Remote Year/` (root) | 94 GB | Duplicate of the above? — verify |
| `/Volumes/Carbonizer/Photos/Drone/` | 16 GB | Drone archive |
| `/Volumes/Carbonizer/Music/` | 97 GB | |
| `/Volumes/Carbonizer/Projects/` | 1 GB | Currently tiny; will grow as project focus increases |
| `/Volumes/Carbonizer/Photos/_CCC SafetyNet/` | 1.2 GB | CCC's quarantine; periodically purge |
| `/Volumes/Carbonizer/Photos/Photos Library.photoslibrary/resources_AM2.local_*_CaseConflict` | ~21 GB (8 dirs) | Cruft from exFAT case-insensitive collision during a 2024-07-01 sync; delete |
| Noisy Cricket | unknown; 1:1 clone assumed | Not currently mounted |

### Current copy topology (photos)

```
Mac ~/Pictures/                    (2025-2026 only; 2024 not present)
  └─ Carbonizer (onsite SSD)       (ALL years + Remote Year + old Apple Photos library)
       └─ Noisy Cricket            (1:1 clone, onsite)

NAS Media/photos/                  (not yet populated for 2024 or 2025)
Immich                             (partial; Plan 0002 Phase 2 dedup in progress)
Brother's UGREEN DXP6800           (not yet connected)
```

Everything physically onsite except Immich (still onsite — same NAS). **Zero true offsite copies today.**

---

## Approach

### Phase 1 — Baseline, reconciliation, and drift cleanup

**Goal:** Know what exists where; resolve authority ambiguity; remove known cruft.

**Steps:**
1. **Measure `Carbonizer_BU`.** `sudo du -sh /Volumes/Carbonizer_BU` (current shell has permission denied; needs sudo). Then `du -h -d 2 /Volumes/Carbonizer_BU 2>/dev/null | sort -h` for subfolder breakdown. This is the actual CCC UGREEN backup target; we've never seen its contents.
2. **Reconcile `Media/photos/` vs `Carbonizer_BU` on NAS.** Two parallel NAS photo locations exist. `Media/photos/` has ~612 GB (including 233 GB of 2024, 93 GB Remote Year, 187 GB `archive/`) put there by some non-CCC process. `Carbonizer_BU` is CCC's target. Decide which is authoritative and consolidate, or document why both must persist.
3. **Reconcile 2025 Photos authority.** Diff Mac `~/Pictures/2025 Photos/` (246 GB) vs. Carbonizer `Photo Files/2025 Photos/` (284 GB). The 38 GB extra on Carbonizer is likely retained-deletion content (pre-Mac-cleanup state). Decide: delete from Carbonizer to match Mac, or keep as extra safety layer? User preference.
4. **Audit the 313 GB `_CCC SafetyNet/` inside Carbonizer's 2024 Photos.** List the dated subfolders; spot-check whether content is intentional-cull (bad shots culled from Mac) or accidental-deletion (content user wants back). If all intentional culls, safe to purge to reclaim 313 GB on Carbonizer.
5. **Audit Cricket's 195 GB root-level `_CCC SafetyNet/`.** Same question — historical orphans worth keeping or safe to reclaim?
6. **Verify `Remote Year/` duplication** on Carbonizer (root 94 GB vs. Photos/ 106 GB). Likely one is stale. Delete the stale copy.
7. **Investigate `/Volumes/NoisyCrick/Media to Sort/`** (192 GB, not on Carbonizer). Decide: integrate into Carbonizer workflow, archive to NAS, or delete.
8. **Delete `~/Pictures/YYYY Photos/`** template stub (32 KB, no content).
9. **Rename `2025 Photos` → `2025-Photos`** and `2026 Photos` → `2026-Photos` on Mac to match schema and `macos_create_photo_year.sh` output. Update CCC source path in the Mac → Carbonizer task.
10. **Delete case-conflict cruft on Carbonizer** (`resources_AM2.local_*_CaseConflict` — 8 dirs, ~21 GB). Same on Cricket.
11. **Bound `_CCC SafetyNet/` retention** in CCC UI (reduce from default 30 days to 7 days) for all four tasks. After retention cap takes effect, audit whether SafetyNet folders shrink as expected.

**Exit criteria:** `Carbonizer_BU` contents documented and reconciled with `Media/photos/`. 2025 Photos authority decided. SafetyNet folders audited for keep-vs-purge decisions. Drift folders resolved. `du -sh` across all tiers recorded in Status log.

### Phase 2 — Reclaim Carbonizer Apple Photos (201 GB)

**Goal:** Free 201 GB per SSD by removing the disposable Apple Photos library clone.

**Steps:**
1. Confirm no unique data in `/Volumes/Carbonizer/Photos/Photos Library.photoslibrary/` — spot-check exported originals vs. Immich / Carbonizer `Photo Files/`.
2. Delete `/Volumes/Carbonizer/Photos/Photos Library.photoslibrary/`.
3. Update CCC task to exclude `.photoslibrary` sources going forward (no chance of re-clone on next Mac → Carbonizer run).
4. Run CCC Carbonizer → Noisy Cricket so Cricket also reclaims 201 GB. Requires both drives mounted.

**Exit criteria:** 201 GB free on Carbonizer and Noisy Cricket. CCC excludes prevent re-copy. No user-visible loss.

### Phase 3 — CCC automation

**Goal:** Remove "when the user remembers" as the trigger for SSD backups.

**Steps:**
1. Audit existing CCC task definitions (source/destination, excludes, schedule).
2. Configure Mac → Carbonizer to run **on volume mount** (CCC supports this — "When the destination is reattached") or on a fixed schedule (e.g., every 2 hours when connected). On-mount is better for the "mobile workflow."
3. Configure Carbonizer → Noisy Cricket to run **when both volumes are attached**. Gate with a pre-flight check so it doesn't run mid-Carbonizer-write.
4. Configure CCC email/notification on task failure (CCC's built-in feature).
5. Disable the "SafetyNet" retention default of 30 days; reduce to 7 days to cap growth.
6. Test: mount Carbonizer → confirm Mac → Carbonizer triggers within a few minutes; mount Cricket → confirm Carbonizer → Cricket triggers.

**Exit criteria:** Both CCC tasks run automatically on drive mount. Notifications configured. SafetyNet retention bounded. Dry-run succeeded.

### Phase 4 — Continuous Mac → NAS backup

**Goal:** Photos and projects reach the NAS within an hour of creation, independent of Time Machine's schedule.

**Options:**

| Approach | Direction | Real-time? | Setup | Notes |
|---|---|---|---|---|
| **rsync + launchd** (Mac-side scheduled) | Mac → NAS, one-way | Hourly / on-change with `fswatch` | Low | Simple, proven, no state. Preferred |
| **Syncthing** (Mac + UGREEN clients) | Bidirectional | Yes (real-time) | Medium | More moving parts; reconciliation complexity; overkill for one-way |
| **UGREEN native SMB + Time Machine-frequency tweak** | — | No | Low | TM is hourly; insufficient granularity and no photo-specific tiering |
| **rclone → NAS SMB** | One-way | Scheduled | Low | Works; no advantage over rsync |

**Recommendation: rsync + launchd.**

**Steps:**
1. Confirm NAS Media share mount persistence (auto-mount on login via keychain-saved SMB credentials).
2. Define source paths:
   - `~/Pictures/*-Photos/` → `NAS/Media/photos-wip/<year>/`
   - Project paths (see Phase 8) → `NAS/Media/projects/` or similar
3. Write rsync wrapper script in `environment/` — idempotent, honors `--dry-run`, logs to a rotating file, exits non-zero on failure.
4. Create launchd plist to run hourly (or use `fswatch` for on-change).
5. Test with a small path first; then full `~/Pictures/`.
6. Add a health check: weekly job that compares file counts Mac vs. NAS and alerts on divergence.

**Exit criteria:** New photos in `~/Pictures/` reach NAS within 1 hour. launchd job runs unattended. Weekly health check passes. Failures surface via notification.

### Phase 5 — Offsite via brother's UGREEN DXP6800

**Goal:** Real offsite. Photos + projects replicated to a NAS in a different physical location (VT).

**Dependencies:** Brother's buy-in. Tailscale account on his side (or shared tailnet). Gigabit up/down confirmed (user reports yes).

**Steps:**
1. Brother sets up Tailscale on his DXP6800 (UGREEN UGOS supports Tailscale natively or via Docker). He joins your tailnet OR you share a tailnet via Tailscale Share.
2. Establish rsync-over-SSH from Peddocks2 to brother's DXP6800. Test with small sample first.
3. **Seed via Noisy Cricket physical ship.** Rather than grinding the initial ~1 TB over gigabit, physically ship Noisy Cricket to brother (USPS Priority Mail Express with signature + insurance, or deliver in person on next visit). He copies from Cricket into his UGREEN. This saves ~3 hours of transfer time and ~1 TB of his uplink.
4. After seed: incremental rsync nightly (Peddocks2 → brother's UGREEN).
5. Restore drill: request a file from brother's UGREEN, verify content matches Peddocks2.
6. Document the failure-mode matrix: what happens if Tailscale goes down, brother's NAS dies, Cricket is lost in transit.

**Alternative (if brother declines / delays):** Fall back to **physical Noisy Cricket rotation only** — Cricket lives at brother's, gets swapped quarterly on visits. Less automated but still closes the offsite gap.

**Exit criteria:** Brother's DXP6800 holds a verified copy of Peddocks2 photo + project trees. Nightly incremental rsync running. One restore drill completed.

### Phase 6 — Noisy Cricket rotation policy

**Goal:** Define the steady-state role of Noisy Cricket after Phase 5 seed.

**Options:**
- **(A) Cricket stays at brother's permanently** as a cold offsite; brother's NAS is the warm offsite. Belt-and-suspenders.
- **(B) Cricket rotates** — travels back home periodically, gets re-cloned from Carbonizer, travels back to brother's. Cadence matches visit cadence.

**Recommendation: (A).** Cricket becomes a cold disaster-recovery drive at brother's. If both Peddocks2 and brother's UGREEN were to fail simultaneously, Cricket is the last-resort seed. No rotation = no in-transit risk after initial ship. If the user visits often enough that rotation is trivial, (B) is also fine.

**Exit criteria:** Written policy in `device-schemas/external-ssds.md`. User committed to a choice.

### Phase 7 — Year-close gate

**Goal:** Formalize the rule for when `YYYY-Photos/` can be removed from Mac.

**Gate criteria (all must be true):**
- Full copy verified on Carbonizer
- Full copy verified on Noisy Cricket (or brother's UGREEN post-seed)
- Full copy verified on NAS `Media/photos/YYYY/`
- Fully indexed in Immich (all files searchable; per-asset count matches source)
- Verified via checksum sample (random 5% of files, hashes match across tiers)

**Steps:**
1. Write `environment/year-close-check.sh` — takes a year, walks the gate criteria, reports pass/fail per tier.
2. Pilot on 2024 Photos first (already off Mac; verify it satisfies the gate against current NAS + Immich state, or surface the gap).
3. Once 2024 verified, pilot on 2025 Photos (this year becomes the first "archive in flight" to remove from Mac).
4. Document as a runbook in `environment/` or `docs/`.

**Exit criteria:** `year-close-check.sh` exists and is idempotent. 2024 Photos passes or gap is documented. 2025 Photos ready for archival when the year closes.

### Phase 8 — Projects as first-class archive

**Goal:** Project files get the same backup tiers as photos.

**Steps:**
1. Identify project home paths on Mac (TBD — likely `~/workspace/` for code, and something else for creative projects). Open question below.
2. Decide NAS target path (`Media/projects/`, `personal_folder/projects/`, or a new share).
3. Fold into Phase 4 continuous backup (rsync includes project paths).
4. Fold into Phase 5 offsite (brother's UGREEN includes project paths).
5. Update `folder-schemas/` to document the project backup topology.

**Exit criteria:** Project paths reach NAS and brother's UGREEN on the same schedule as photos. Documented.

### Phase 9 — exFAT hygiene playbook

**Goal:** Minimize corruption risk on exFAT SSDs given the user's filesystem choice.

**Steps:**
1. Add to `device-schemas/external-ssds.md`:
   - **Eject discipline:** always `diskutil eject` (or Finder eject) before unplug. Never yank mid-write.
   - **Monthly Disk Utility First Aid** on each SSD.
   - **Monthly CCC SafetyNet purge** when free space drops below 300 GB.
   - **Post-power-loss check:** run First Aid after any unclean shutdown.
2. Consider a launchd reminder for monthly First Aid.
3. Document symptoms of exFAT corruption and recovery steps (restore from Cricket; if Cricket also corrupted, restore from NAS).

**Exit criteria:** Hygiene section added to external-ssds.md. Recovery runbook exists.

### Phase 10 — Post-M5 adjustments

**Goal:** Take advantage of the 2 TB M5 Mac when it arrives.

**Steps:**
1. Revise "current year only on Mac" → "rolling 2-year window on Mac" (Mac becomes more authoritative, less archival pressure).
2. Re-evaluate whether Carbonizer still needs to hold the full library, or can shrink to a rolling window too.
3. Consider moving Lightroom Library off external and onto internal (performance win).
4. Verify all phases above still work with the new disk topology.

**Exit criteria:** Documented revision to authority rules in `device-schemas/macbook-personal.md` and `external-ssds.md`.

---

## Risks

- **~~2024 Photos single-device risk — CONFIRMED ACUTE.~~** [RETRACTED 2026-04-22]. Per-subfolder du and find showed live content identical across Carbonizer and Cricket (233 GB, same month/file counts in RAW, JPG, DNG, Video). The 336 GB apparent gap was a `_CCC SafetyNet/` folder nested inside `Carbonizer/Photos/Photo Files/2024 Photos/` — orphans from Mac → Carbonizer task runs, which CCC correctly excludes from Carbonizer → Cricket replication. No acute risk; Cricket is a current live-content copy.
- **SafetyNet nested inside active data path inflates totals.** `du`/Finder item counts of a folder that contains a `_CCC SafetyNet/` subfolder report a size that includes the SafetyNet content. When comparing two CCC-managed drives, compare LIVE CONTENT directly (measure per subfolder, exclude SafetyNet paths), not root totals.
- **2025 Photos authority drift (38 GB).** Mac and Carbonizer disagree; need reconciliation in Phase 1 before automating CCC. If automation runs first, the drift could be erased in the wrong direction.
- **exFAT corruption on unclean eject.** Residual risk; hygiene playbook (Phase 9) reduces but doesn't eliminate. Belt-and-suspenders via NAS + brother's UGREEN.
- **Noisy Cricket loss in transit** during Phase 5 seed ship. Mitigation: insured shipping; or in-person delivery on next VT visit.
- **Brother's NAS reliability** — his hardware is a single point of failure for offsite. Mitigation: Cricket stays at his house as cold DR (Phase 6 Option A).
- **launchd job silent failure.** Mitigation: weekly health check (Phase 4) + CCC email on task failure (Phase 3).
- **Tailscale connectivity** interruption between NAS pair. Mitigation: rsync resumes on next run; no partial-state loss.
- **Mac disk pressure (69 GB free)** may force archival before gates are ready. Mitigation: Phase 2 reclaims nothing on Mac but Phase 4's continuous NAS backup enables safe early archival of 2024-only-on-Carbonizer content to NAS, reducing dependence on Mac-held working copies.

## Open questions

- [ ] **Project paths on Mac** — where do creative/project files live today? `~/workspace/` is code only; where are non-code projects? Answer drives Phase 8 scope.
- [ ] **NAS path for projects** — new share, or reuse `Media/`? User preference.
- [ ] **Brother's timeline** — when can he set up Tailscale on his DXP6800? Gates Phase 5 execution.
- [ ] **Cricket ship method** — USPS Priority Mail Express with insurance, or in-person delivery? Affects Phase 5 seed sequencing.
- [x] **CCC task inventory** (answered 2026-04-22): Four tasks wired — `2025 to Carbonizer` (Mac → Carbonizer, current year), `2026 to Carbonizer` (Mac → Carbonizer, current year), `Carbonizer backup` (Carbonizer → Noisy Cricket), `Carbonizer UGREEN Backup` (Carbonizer → NAS). Additive mode (not mirror). Cadence gap, not coverage gap. Phase 3 automates the cadence.
- [ ] **launchd vs. cron vs. third-party scheduler** on Mac — user preference. launchd is macOS-native.
- [ ] **Reconciliation of 2025 Photos drift** — if Carbonizer has 38 GB Mac doesn't, where did those files originate and should they go back to Mac?
- [ ] **Music on Carbonizer (97 GB)** — in or out of scope? Currently not backed up elsewhere.

## Sequencing

```
Phase 1 (baseline + drift)          ← start here; blocking for most downstream
    ↓
Phase 2 (reclaim 201 GB on SSDs)    ← independent; can run in parallel with P1
    ↓
Phase 3 (CCC automation)            ← depends on P1 reconciliation
    ↓
Phase 4 (continuous Mac → NAS)      ← depends on NAS Media share mounted (P1 step 5)
    ↓
Phase 8 (projects into P4 pipeline) ← merges into P4 scope; requires project paths decided
    ↓
Phase 5 (offsite to brother)        ← gated on brother's Tailscale setup
    ↓
Phase 6 (Cricket rotation policy)   ← after P5 seed lands
    ↓
Phase 7 (year-close gate)           ← requires P4 + P5 running for 2024 verification
    ↓
Phase 9 (exFAT hygiene)             ← can run in parallel, ongoing
    ↓
Phase 10 (post-M5 adjustments)      ← future; gated on hardware
```

## Status log

- 2026-04-22 — Plan drafted. Device schema `device-schemas/external-ssds.md` created. Inventory baseline captured in this plan.
- 2026-04-22 — Full 5-tier scan (Mac / Carbonizer / Cricket / NAS / [brother's pending]). Identified 313 GB of 2024 Photos existing only on Carbonizer. User triggered all CCC tasks; `Carbonizer backup` (→ Cricket) and `Carbonizer UGREEN Backup` (→ NAS) running. Closes single-device exposure onsite once complete. Offsite still pending Phase 5.
- 2026-04-22 — NAS Media share mounted (`/Volumes/Media`, SMB). 10 TB used / 12 TB free. Existing photo archive: ~612 GB (2024 Photos 233 GB, Remote Year 93 GB, archive/ 187 GB, plus older trip folders). Typo drift: `Portalnd Trip` (should be `Portland`). NAS `backup` share exists but empty.
- 2026-04-22 — Cricket anomalies captured: 195 GB `_CCC SafetyNet/` (vs Carbonizer's 1.2 GB), 192 GB `Media to Sort/` (not present on Carbonizer — investigate before touching). Cricket pre-run sizes: Photos 815 GB (vs Carbonizer 1.1 TB); 2024 Photos 233 GB (vs Carbonizer 546 GB) — Cricket and NAS matched pre-run, implying same lineage CCC snapshot.
- 2026-04-22 — CCC log + Finder Get Info initially suggested Cricket stale: `Carbonizer Backup` task ran in 83 seconds; Finder showed Carbonizer 2024 Photos at 12,440 items / 586 GB vs Cricket at 5,542 items / 250 GB. Hypothesis was narrow CCC source scope.
- 2026-04-22 — **RETRACTED.** Per-subfolder du + find confirmed Carbonizer and Cricket live 2024 Photos are identical (233 GB each, matching file counts per month folder: 2024-01 = 113, 2024-08 = 2017, 2024-12 = 280, etc.). The 336 GB gap was a nested `_CCC SafetyNet/` folder inside `Carbonizer/Photos/Photo Files/2024 Photos/` (313 GB of Mac-deletion orphans). CCC correctly excludes SafetyNet folders from source-to-destination replication, so Cricket correctly lacks this folder. The 83-second Carbonizer → Cricket run was correct no-op, not misconfiguration. CCC task config does NOT need to be recreated.
- 2026-04-22 — `Carbonizer UGREEN Backup` writes to a separate NAS share `Carbonizer_BU` (not the `Media/photos/` measured earlier — two parallel NAS photo locations). `Carbonizer_BU` contents still need baseline measurement.
- 2026-04-23 — `Carbonizer UGREEN Backup` run verified: 04/22 23:07:40 → 23:23:51 (16 min, exit 0). `Carbonizer_BU` 2024 Photos live content measured (via sudo over SMB) and matches Carbonizer 1:1: RAW 223G, JPG 9.8G, DNG empty, Video 407M. Three verified onsite copies of 2024 Photos live content (Carbonizer + Cricket + `Carbonizer_BU`); `Media/photos/2024 Photos/` holds a fourth independent copy from a prior non-CCC process. Onsite redundancy is solid; offsite still pending Phase 5.
