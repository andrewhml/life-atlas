# Plan 0006 — Photo coverage validation and iCloud drain

**Status:** Draft (pending /pong-review)
**planpong:** R2/10 | claude → codex | risk | 1P1 3P2 1P3 → 4P1 3P2 | Accepted: 5 | +39/-0 lines | 15m 13s | Reviewed — 7 issues
**Issue:** — (create on session-end)
**Created:** 2026-04-24
**Depends on:** Plan 0002 (Phase 2 dedup soak until ~2026-04-30)
**Supersedes:** Plan 0002 Phase 3 (this plan is the concrete execution)
**Related:** Plan 0005 (photo + project lifecycle)

---

## Goal

Drain iCloud Photos from 150 GB → ~0 GB. Do it by proving, not assuming, that Immich preserves every asset the user wants to keep — at the level of fidelity the user requires. Use vendor-provided surfaces (Immich iOS app, Apple Photos download) wherever possible; write custom code only when vendor tools cannot answer a specific question that blocks the drain.

## Preservation contract (decide first)

This plan's success depends on what "preserve" means. Three levels — user picks one in Phase 0 before any other work:

| Level | What's preserved | What Phase A/D must verify | Drain posture |
|---|---|---|---|
| **L1 — Originals only** | Every photo/video file (full-res bytes), Live Photo pairs intact | Count + sample-render parity | Bulk delete OK once verified |
| **L2 — Originals + core metadata** | L1 + EXIF date/location, favorites, captions | L1 + metadata spot-check in Immich | Bulk delete OK once verified |
| **L3 — Apple Photos experience** | L2 + albums, hidden state, edits-as-applied, shared albums | Requires Mac hydration + richer diff; likely can't fully round-trip into Immich | Drain may need to be partial; some state stays in Apple |

**Default assumption:** L1 unless the user explicitly asks for more. **The chosen level determines whether Phases B–D are needed at all** (see Phase A exit).

## Scope

- **In:**
  - Choosing the preservation level (L1/L2/L3) and making every downstream step match
  - Verifying iPhone → Immich coverage via the Immich iOS app's own UI (Phase A — the primary proof path)
  - **Conditional:** Mac-local hydration + custom coverage diff, only if Phase A leaves a material gap or the preservation level requires it
  - Closing any coverage gap found
  - Provisional steady-state decision (Immich-only vs. curated iCloud subset) before drain
  - Draining iCloud Photos in the shape the steady-state decision implies

- **Out:**
  - Ongoing sync daemon (iOS auto-backup already covers forward sync)
  - Duplicating the Immich iOS app's built-in backup-status screen
  - **Lightroom masters / 2025-Photos relocation / catalog relink** (plan 0005 owns this; not a prerequisite for this plan)
  - "1:1 album" reconciler between Immich and Apple Photos (revisit post-drain if still wanted)
  - Non-photo iCloud categories (plan 0002 phase 7)
  - Obsidian vault migration (plan 0002 phase 5)

---

## Ground truth (2026-04-24)

- **Immich iOS auto-backup: ACTIVE.** Enabled on iPhone since 2026-04-22 (plan 0002 phase 1). Pulls from iPhone's Apple Photos library over Tailscale.
- **Apple Photos (iPhone) ⊃ iCloud Photos.** More content on iPhone than in iCloud; iCloud is full (200 / 200 GB) so new content stalls at iPhone. User-confirmed 2026-04-24.
- **Transitivity consequence:** If iPhone → Immich coverage is 100% at L1 or L2, then Immich ⊇ iCloud for that level by transitivity, without any Mac hydration.
- **Mac Apple Photos library is effectively empty** (0.5 GB) — iCloud Photos not enabled on Mac.
- **Mac disk pressure: tight.** 54 GiB free of 926 GiB (94% full, as of 2026-04-24). Full iCloud hydration would require staging; not needed if Phase A closes the question.
- **Immich: Phase 2 dedup in trash-soak** through ~2026-04-30. Immich library is still mutating; authoritative coverage work must not start until soak closes.

---

## Approach

Each phase:
- Delivers one testable outcome
- Can be paused at after completion without stranding the system
- Prefers vendor-provided tools over custom builds
- Skipped when the preservation contract or a prior phase's outcome makes it unnecessary

### Phase 0 — Choose preservation level (no build)

**Outcome:** User picks L1, L2, or L3 from the preservation contract table. Recorded in status log. This choice drives every subsequent decision.

**Exit:** Level chosen and written down.

### Phase A — iPhone → Immich coverage audit (no build)

**Outcome:** Quantified confidence that Immich reflects the iPhone's Apple Photos library at L2.

**Pre-check (R2 F2 — transitivity requires originals, not placeholders):**
- iPhone: Settings → Photos → confirm **"Download and Keep Originals"** is selected (not "Optimize iPhone Storage"). If Optimize is on, the iPhone may hold thumbnails for older iCloud-offloaded assets, meaning Immich's backup of those assets is a placeholder — not the original bytes. If Optimize is currently on, switch to Download and Keep Originals and wait for the iPhone to re-pull full-res originals before running the rest of this phase.

**Steps:**

1. **Count parity.** Immich iOS app → backup status. Record `backed_up / total`. Cross-check against iOS Settings → General → iPhone Storage → Photos (asset count). Immich's `total` should match iOS within a small delta (Hidden + Recently Deleted are not expected to back up).

2. **Second parity channel (R2 F1).** Immich web UI → Library → total asset count. Compare to iPhone's iOS count from step 1. Two independent counts must line up — catches "Immich app UI says 100% but backup actually stalled on a subset" failure mode.

3. **Edge-class enumeration (R2 F1).** For each class, confirm presence in Immich by searching/filtering. Don't trust the aggregate count; a systematic miss of one class can hide inside a correct total.
   - Live Photos: sample 5 known Live Photos on iPhone. Each should appear as HEIC + MOV in Immich (stacked or paired).
   - Videos: distinct video count. iPhone Photos app → Media Types → Videos. Compare to Immich's video filter.
   - Screenshots / screen recordings: similar, via Media Types filters on both sides.
   - RAW + JPEG pairs (if any): confirm both halves present.
   - Bursts: Immich should show the burst stack or keeper.
   - Hidden album: is Immich iOS app set to include or exclude Hidden? Note the setting. If including, verify count.
   - Recently Deleted: NOT expected in Immich; note count for awareness only.

4. **Original-bytes spot check (R2 F2).** Pick 10 random pre-2024 photos + 10 random recent on iPhone. For each, open in Immich web and:
   - Press `i` (info) → file size and dimensions should match iPhone's (within codec rounding)
   - Confirm the asset downloads/renders at full resolution, not as a broken placeholder

5. **L2 metadata field-by-field (R2 F7).** 10 sample assets with known-good metadata on iPhone. For each, check EACH field independently in Immich:
   - EXIF DateTimeOriginal matches iPhone's capture date
   - EXIF GPS latitude/longitude present for geotagged shots
   - Favorite flag: an asset starred on iPhone shows as favorited in Immich
   - Caption: a captioned asset shows the caption in Immich
   Record per-field pass count (e.g., "date 10/10, GPS 9/10, favorite 10/10, caption 7/10"). Any field below 9/10 is a systematic issue, not a sample error.

6. Record all results in status log.

**Exit gate (decides whether Phases B–D run):**
- Optimize iPhone Storage is OFF (originals resident)
- Immich iOS app shows no pending/failed backup items
- **Containment**: Immich total ≥ iPhone library total (Immich ⊇ iPhone, not strict equality — Immich legitimately holds more if older captures are retained beyond iPhone)
- Original-bytes spot check: at least 10/10 assets download at full original size from Immich (thumbnails failing is acceptable — originals are what L2 requires)
- L2 metadata: each of the 4 fields ≥ 9/10 on per-field samples

Thumbnail/preview render failures in the Immich web UI do NOT fail the gate as long as the original bytes are retrievable via download. Thumbnail generation is cosmetic; L2 is about preservation of bytes + metadata.

If **all** pass → **skip Phases B–D**, proceed to Phase F̂ then Phase G.
If **any** fail → proceed to Phase B; the failing class/field scopes what the coverage tool in Phase D must recover.

**Value delivered:** For a clean iOS-backup case at L2, resolves the verification question in ~20 minutes of on-phone/on-Immich-web work. Obviates ~200 GB of local staging if the gate passes.

### Phase B — Prepare isolated staging (only if Phase A didn't close it)

**Outcome:** A place to hydrate iCloud originals for local enumeration without disturbing existing Mac state.

**Default path (isolated):**
1. Use a small external SSD (~500 GB) as a dedicated staging volume, OR leverage Photos.app's "Optimize Mac Storage" + targeted `osxphotos` pulls rather than a full local mirror.
2. Confirm staging volume has ≥ 200 GB free.

**Explicitly NOT in this phase:** relocating `~/Pictures/2025-Photos/`, touching Lightroom catalog, or any authority-drift work. That belongs to plan 0005 and is not a prerequisite here.

**Exit:** Staging surface exists with ≥ 200 GB free.

### Phase C — Hydrate iCloud originals into staging (only if Phase A didn't close it)

**Outcome:** iCloud Photos contents locally enumerable (either as a full Photos library on the staging volume, or via `osxphotos` streaming pulls).

**Steps:**
1. If full hydration: System Settings → Apple ID → iCloud → Photos ON; Photos.app → Settings → Library → Download Originals, with library on the staging volume.
2. Wait. ~150 GB over 755 Mbps down = 1–2 hours realistic.
3. Verify hydrated size ≈ expected iCloud size within ~5%.
4. Spot-open 10 random assets; confirm full-resolution render.

**Risk:** Staging volume fills mid-download. Mitigation: monitor progress; abort before cap.

**Exit:** Local iCloud mirror is addressable by `osxphotos`.

### Phase D — One-shot coverage tool (only if Phase A didn't close it)

**Gate:** Plan 0002 Phase 2 dedup soak MUST be closed (Immich trash empty, no pending merges) before this phase starts. A moving Immich baseline invalidates the scan.

**Outcome:** A report classifying every iCloud asset into one of four buckets. Phase A findings on 2026-04-24 expanded this scope — the original `apple_only` framing was not sufficient because Immich's import history (notably Google Takeout) produced systematically degraded assets.

| Bucket | Meaning | Action in Phase E |
|---|---|---|
| `in_both_clean` | SHA1 match or size+metadata match; Immich bytes are the iPhone/iCloud original | Safe; no action |
| `in_both_degraded_bytes` | Matched by filename/capture-time, but Immich's file size is ≪ iPhone's (e.g., 841 KB DNG vs. 8.2 MB original) | Re-import from iCloud/iPhone to replace Immich's degraded copy |
| `in_both_degraded_metadata` | Bytes clean, but Immich's `DateTimeOriginal` / location / favorite / caption doesn't match iPhone/iCloud | Re-extract metadata; if that fails (sidecar-dependent), re-import |
| `apple_only` | Not in Immich at all | Import |

**Tool:** `tools/photo-coverage/` — follows the same skeleton as `tools/immich-dedup/`.

| Script | Role |
|---|---|
| `scan.py` | Enumerate via `osxphotos` (local hydration) + Immich REST API. Write SQLite manifest of Apple UUID ↔ Immich asset ID ↔ match confidence ↔ degradation flags. |
| `report.py` | Render the four-bucket report as Markdown + HTML galleries per bucket. |

**Matching:**
- **Primary:** SHA1 — `osxphotos` computes it on Apple's original file; Immich exposes `checksum`.
- **Size sanity check (new from Phase A findings):** if Apple-side file > 2 MB and Immich-side file < 25% of Apple-side → flag as `in_both_degraded_bytes`. Catches DNG proxy issue.
- **Fallback:** `(DateTimeOriginal, camera model, pixel dimensions, file size)` composite when one side re-encoded.
- Live Photos pair (HEIC + MOV) treated as a single unit.
- **L2 metadata comparison (expanded from Phase A findings):** for each match pair, compare `DateTimeOriginal`, GPS lat/long, favorite flag, caption text. Any mismatch → flag as `in_both_degraded_metadata`. This is the check Phase A's per-field sample could not certify at scale.

**Explicitly NOT building:**
- A daemon
- Ongoing sync
- Bidirectional album reconciliation
- A `apply.py` equivalent of immich-dedup (deletion isn't what this tool does)

**Exit:** Report exists; `apple_only` bucket count is Phase E's work list.

### Phase E0 — Google Takeout metadata repair (triggered by 2026-04-24 preflight findings)

**Context:** Preflight on 2026-04-24 found 33,734 Immich assets with no `dateTimeOriginal` and a 45,343-asset single-day import cluster on 2024-07-10 — the Google Takeout ingestion, where Immich's web UI skipped JSON sidecars. This phase targets that specific degradation before general Phase D/E work.

**Outcome:** `dateTimeOriginal` populated for the Takeout-originated subset, via re-import with `immich-go` in Google Photos Takeout mode.

**Prereq:** Fresh Google Takeout export in progress (started 2026-04-24). 4 GB chunks, manual download. `immich-go` installed and dry-run-validated.

**Steps:**
1. Install `immich-go` on Mac (GitHub Releases binary).
2. Generate Immich API key with `asset.upload` + `asset.read` + `album.*` scopes.
3. Stage Takeout zips on Carbonizer (`/Volumes/Carbonizer/takeout-20260424/`).
4. Smoke test: dry-run `immich-go upload from-google-photos` against one small zip.
5. Full dry-run against the whole Takeout archive. Review log for "metadata updated" vs "already exists (skipped)" behavior.
6. **Decision point:**
   - **Path A** (dry-run shows metadata updates on SHA matches): run immich-go against the full archive; existing-records get their sidecar metadata applied.
   - **Path B** (dry-run shows skip-without-update on matches): delete the 2024-07-10 cluster from Immich (45,343 assets, all Takeout-originated), then run immich-go. Deletion script written only if Path B is taken.
7. Re-run `tools/photo-coverage/preflight.py`. Verify "no `dateTimeOriginal`" count drops from 33,734 toward 0.

**Safeguards:**
- Do not start while Immich Phase 2 dedup soak is active — coordinate with `/volume1/docker/immich` state.
- Fresh Immich Postgres snapshot before the real run.
- Dry-run must pass before any destructive action.

**Exit:** Missing-date count near zero in preflight; Immich's UI shows correct capture dates for sampled Takeout-originated assets.

### Phase E — Close the coverage gap (only if Phase D ran)

**Gate:** Same as Phase D — Immich dedup soak closed.

**Outcome:** `apple_only` bucket = 0 after re-scan.

**Steps:**
1. For the `apple_only` set: export via `osxphotos export --download-missing --use-photos-export` to a staging directory.
2. Upload to Immich via API (or `immich-cli upload` for large batches).
3. Re-run `scan.py`. Bucket should be empty.
4. Residual: usually HEIC/JPEG encode mismatch — accept metadata-composite match if spot-check is clean.

**Exit:** Re-scan shows `apple_only` = 0 (or residual is explained and accepted).

### Phase F̂ — Provisional steady-state decision (before drain)

**Outcome:** Recorded provisional choice on iCloud Photos going forward. This shapes whether Phase G is a bulk delete or a selective delete.

**Options:**

| Option | What it means | Drain implication |
|---|---|---|
| **Off** | Disable iCloud Photos across devices post-drain. Immich iOS backup is the only path. | Phase G is a bulk delete of everything currently in iCloud. |
| **Curated subset** | iCloud Photos ON; maintain a ~20 GB subset of "recent + shareable on phone." | Phase G is a selective delete — keep the curated set, drop the rest. Curation happens before or during drain, not after. |

**Decision inputs:** How often the user shares via Apple Photos (AirDrop, iMessage embed, Shared Albums) vs. Immich alternatives.

**Exit:** Provisional decision logged in plan status. Final confirmation re-checked after Phase G.

### Phase G — Drain iCloud Photos

**Outcome:** iCloud Photos usage reduced to the level chosen in Phase F̂ (≤ 5 GB for "Off", ≤ 20 GB for "Curated subset").

**Pre-gate (hard, non-optional):**
- Phase A exit achieved (100% coverage at the chosen level) OR Phase E exit achieved (`apple_only` = 0)
- Preservation contract satisfied at the chosen level
- Immich dedup soak closed (trash empty)
- Fresh Immich Postgres backup taken within 24 hours
- Phase F̂ provisional decision recorded

**Steps:**
1. If curated subset: first mark/export the keep-set explicitly (album, tag, or list), then delete the complement.
2. If off: bulk select + delete.
3. Deletion surface:
   - **iCloud.com** (preferred): bulk select + delete. Deletes propagate to all Apple devices.
   - **Photos.app on Mac**: select all → delete. Same propagation.
4. Work in ≤ 5,000-asset batches. Between batches, wait for sync to finalize (~5 min).
5. 7-day soak in Recently Deleted. Any regret → restore from the same UI.
6. After 7 days: iCloud.com → Recently Deleted → Delete All.
7. Verify iCloud storage breakdown matches the chosen target.

**Exit:** iCloud total at the target.

### Phase H — Confirm steady-state; document

**Outcome:** Final confirmation of the Phase F̂ choice (or revision if the drain revealed new info), and documentation in device schemas.

**Steps:**
1. Confirm or revise the F̂ decision.
2. If "Off": disable iCloud Photos on each device.
3. Document final behavior in `device-schemas/iphone.md` + `device-schemas/macbook-personal.md`.

**Exit:** Decision finalized; schemas updated.

---

## Risks

- **Phase 0 preservation level is wrong.** User picks L1, later realizes albums/edits mattered. Mitigation: explicitly show the L1/L2/L3 table and ask; re-running at a richer level is possible pre-drain.
- **Phase A finds significant backup gap.** Means iOS auto-backup has been stalling; Phase G cannot proceed until Phases B–E complete or auto-backup catches up.
- **Phase D/E run against a still-mutating Immich baseline.** Mitigation: hard gate on dedup soak closure before either phase starts.
- **Phase C hydration stalls near staging-full.** Mitigation: use isolated volume, monitor during download.
- **Phase D SHA1 matches under-count.** Immich may re-encode HEIC to JPEG. Mitigation: metadata-composite fallback.
- **Phase G cascade deletion.** iCloud.com deletion propagates to iPhone and Mac Photos within minutes. Mitigation: Immich's canonical copy is independent of any Apple-library external refs.
- **Live Photos stripping.** Verify HEIC+MOV pair handling before Phase G.
- **L3 may not be fully achievable.** Albums, hidden state, and some edits may not round-trip into Immich. Mitigation: if L3 is required, Phase H may conclude the answer is "keep iCloud Photos on" and skip drain entirely.

## Open questions

- [ ] **Phase 0:** Which preservation level — L1, L2, or L3?
- [ ] **Phase A result:** What's iPhone → Immich coverage today?
- [ ] **Phase F̂:** Off vs. curated subset — provisional call before drain.
- [ ] **Does Immich's iOS client set `deviceAssetId` reliably?** Would give Phase D a third primary key (Apple UUID) alongside SHA1.

## Sequencing

```
Phase 0 (choose preservation level)
   ↓
Phase A (Immich iOS audit — primary proof path)
   ↓
   ├── if L1/L2 & 100% coverage & spot-checks pass → skip to F̂
   │
   └── else ↓
Phase B (isolated staging)
   ↓
Phase C (hydrate iCloud originals)
   ↓  [wait for dedup soak to close]
Phase D (build coverage tool)
   ↓
Phase E (close gaps) ← may loop with D
   ↓
Phase F̂ (provisional steady-state decision)
   ↓  [+ Immich trash empty, fresh PG backup]
Phase G (drain iCloud in the shape F̂ implies)
   ↓
Phase H (confirm steady-state; update schemas)
```

## Status log

- 2026-04-24 — Plan drafted. Next step: /pong-review.
- 2026-04-24 — R1 revision: added preservation contract (L1/L2/L3) as Phase 0; made Phases B–D conditional on Phase A outcome; removed Lightroom/2025-Photos relocation from scope (plan 0005 owns it); gated Phases D/E on dedup soak closure; moved steady-state decision (F̂) before drain.
- 2026-04-24 — R2 feedback surfaced (4 P1 / 3 P2) but revise loop blocked by planner subprocess failure. Partial manual integration of three R2 P1s into Phase A (F1 edge-class + second parity channel, F2 originals-not-placeholders pre-check, F7 field-by-field L2 metadata). Unaddressed R2 items: F3 rollback verification, F4 curated-subset complement-construction, F5 freeze-window before drain batches, F6 Phase D preflight. Revisit before Phase G (drain).
- 2026-04-24 — **Phase 0 complete: L2 chosen** (originals + core metadata: EXIF date/location, favorites, captions).
- 2026-04-24 — Phase A in progress. iPhone library live total: 8,081 photos + 1,870 videos = 9,951 (190 items pending iCloud sync — separate). Immich iOS app selected-album total: 11,647 (Immich ⊇ iPhone by ~1,700 historical assets). Optimize Storage confirmed OFF. DNG thumbnail pipeline broken in web UI — originals retrievable (sampled `IMG_5802.DNG`, downloads at 47.9 MB as expected). "Retry missing" and full thumbnail job both run; DNG previews remain broken. Filed as separate follow-up (Immich server-side issue, not a preservation failure). Remaining Phase A work: 10-sample original-bytes download check + L2 metadata field-by-field verification (can be done via info panel without thumbnails).
- 2026-04-24 — Preflight v1 (`tools/photo-coverage/preflight.py`) run against 102,415 assets. Findings: (a) 92 DNGs under 2 MB, but top-20 are all `._*` AppleDouble shadow junk — real degraded-DNG count ~72; (b) 33,734 assets with no `dateTimeOriginal`; (c) import-day histogram: 2024-07-10 = 45,343 (the Google Takeout event), 2023-10-05 = 10,354, 2025-10-28 = 5,552. Preflight heuristic bugs flagged: shadow-file filter needed, `fileModifiedAt` comparison was wrong field. Phase E0 added to plan targeting the Takeout metadata repair via `immich-go` re-import. Takeout re-export kicked off 2026-04-24 (4 GB chunks, email delivery).
- 2026-04-24 — **Phase A gate: FAILED.** Spot-check at 9/10 samples surfaced two systematic L2 violations:
  1. **Degraded bytes:** `IMG_6272.dng` is 8.2 MB on iPhone but only 841 KB in Immich (~10% size; likely a proxy, not the original). At least one confirmed; scope unknown.
  2. **Wrong `DateTimeOriginal` on a large subset**, likely from Google Photos Takeout import path where JSON sidecars carrying correct dates were not applied to stored originals. User noticed naturally during metadata spot-check.
  R2 reviewer issue F7 predicted exactly this failure mode ("small sample can pass while one metadata class is systematically missing"). Phases B–D now required. Phase D tool scope expanded to four buckets (`in_both_clean` / `in_both_degraded_bytes` / `in_both_degraded_metadata` / `apple_only`) — degraded-bytes and degraded-metadata are new buckets driven by these findings. Next step: lightweight preflight diagnostic (count degraded-byte candidates and suspicious-date candidates) before committing to full Phase B–D build.
