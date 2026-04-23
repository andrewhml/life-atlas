# Plan 0002 — Data 3-2-1 consolidation and iCloud unblock

**Status:** In Progress
**Issue:** — (create on session-end)
**Created:** 2026-04-22

---

## Goal

Get the personal-data ecosystem into a 3-2-1-aligned state (3 copies, 2 media types, 1 offsite) without buying new hardware or services, while simultaneously unblocking iCloud (currently at 200/200 GB, blocking iPhone photo backup and iCloud Drive Obsidian sync). The iPhone-photos-locked-on-device situation is the single biggest risk today and must be addressed first.

## Scope

- **In:**
  - Free iCloud by moving photos to Immich as master
  - Unblock iPhone photo backup immediately (Immich-first, iCloud-second)
  - Move Obsidian vault off iCloud Drive to a cross-OS sync mechanism
  - Repurpose Synology DS1019+ as a local secondary backup of UGREEN DXP6800
  - Deduplicate Immich (100–200 GB of known dupes/trash)
  - Decide how iPad and iPhone tie into the backup story
  - Document the offsite gap and a path forward (even if deferred)
- **Out:**
  - New hardware purchases
  - New paid services (Obsidian Sync, B2, Backblaze, etc.)
  - Migrating Syntheus/work data — already clean, hard boundary
  - Mac Time Machine strategy (separate concern)
  - Plex/media library reorganization
  - Turning this into a product for others — out of scope; solve personal ecosystem first

---

## Inventory snapshot (reference)

### Storage capacity

| Device / Service | Used / Total | Redundancy | Notes |
|---|---|---|---|
| MacBook Pro M2 Pro | 875 / 1000 GB | — | Primary work + creative; 88% full |
| Windows PC (Ryzen 7 9800X3D, RTX 5080) | 1.5 / 4 TB | — | Gaming + PC dev + light video edit |
| UGREEN DXP6800 | 10.2 / 21.7 TB | RAID 5, 4× ~10 TB (1-drive fault tolerance); 2 empty bays; 1 TB SSD pool, Basic, idle | Primary NAS; Plex + Immich + Mac backup + services |
| Synology DS1019+ | 9.6 / 11.4 TB (current); will be wiped | SHR-2, 5× 7.3 TB (2-drive fault tolerance), 21.8 TB usable target after wipe | Old NAS; goal = UGREEN backup target |
| iPad Pro M4 | 151 / 1000 GB | — | Mobile + Lightroom + drawing |
| iPhone 16 Pro | 281 / 512 GB | — | Comms + photo capture |
| Boox Palma 2 | — | — | Calibre-fed e-reader |
| iCloud | **200 / 200 GB (FULL)** | — | Photos 150.2 GB, Backup 38.3 GB, Messages 7.3 GB, Docs 4.1 GB, Mail 26 MB |
| Google Drive Personal | 26 / 100 GB | — | Atlas canonical |
| Google Drive Syntheus | 23 / 60 GB | — | Client work, hard boundary |
| SanDisk `Carbonizer` (2 TB exFAT SSD) | 1.3 / 1.8 TB | — | Mobile primary photo + projects mirror; Mac ↔ SSD via CCC |
| SanDisk `Noisy Cricket` (2 TB exFAT SSD) | ~same (1:1 clone) | — | CCC clone of Carbonizer; currently onsite — offsite path in Plan 0005 |

### Irreplaceable vs replaceable data

- **Irreplaceable:** Photos and videos (life originals), Obsidian vault, Atlas docs, Mac creative project files (Adobe, Lightroom), iPhone-only captures (right now locked on device), Syntheus client work
- **Replaceable:** Plex media library, Steam/games, OS installs, application binaries

---

## 3-2-1 target state

| Data class | Copy 1 (source) | Copy 2 (local) | Copy 3 (offsite) |
|---|---|---|---|
| Photos/videos | iPhone/camera | UGREEN (Immich master) | Synology (local 2nd), offsite = **GAP** |
| Obsidian vault | Device working copy | UGREEN (LiveSync CouchDB) | Synology replica, offsite = **GAP** |
| Atlas docs | Local Mac mirror | Google Drive Personal (canonical) | Google Drive IS offsite (cloud) |
| Syntheus | Local | Syntheus Google Drive | Cloud = offsite (OK) |
| Plex media | UGREEN | Synology (partial) | Replaceable; offsite not required |
| Mac creative projects | MacBook | UGREEN (Mac backup) | Synology (via UGREEN replication), offsite = **GAP** |

**Offsite gap is explicit and accepted for now.** Paths forward (any one, post-plan):
- Rotate an existing external drive to Syntheus office / family home (zero cost if drive exists)
- Small paid tier later (Backblaze B2 ~$6/TB/mo) for a critical subset (photos + Obsidian + Atlas ≈ 1 TB max)
- Friend-hosted drive with reverse Tailscale

---

## Approach

### Phase 1 — Stop the bleeding: iPhone photo backup to Immich

**Goal:** iPhone photos reach durable storage within minutes of capture, regardless of iCloud state.

**Steps:**
1. On iPhone: install Immich iOS app and Tailscale iOS (if not already installed; UGREEN Tailscale exit node is set up)
2. Log into Immich; point to UGREEN over Tailscale
3. Enable auto-backup for Photos and Videos; background refresh on
4. Verify: take a test photo, confirm upload appears in Immich within 2 minutes
5. Repeat on iPad Pro (Lightroom masters there too)
6. Leave iCloud Photos enabled but accept that new captures are only reaching iCloud when space allows — Immich is now the durable path

**Exit criteria:** New iPhone/iPad photos land in Immich automatically. Test photos verified. No longer dependent on iCloud space for photo durability.

**Status:** ✅ Complete 2026-04-22. iPhone auto-backup via Tailscale active (`http://dxp6800:8212`); new captures verified landing in Immich. iPad Tailscale connectivity verified, backup deferred (no iPad-unique content today). Hardened public URL via SQLite-level Access List attachment to "Admin Utilities" (home IP only, others 403). Enabled Immich iGPU (OpenVINO ML image + /dev/dri mapping on both server and ML containers).

### Phase 2 — Dedup Immich and establish it as photo master

**Goal:** Immich library is clean, deduplicated, and the declared source of truth before emptying iCloud.

**Scale as of 2026-04-22:** Immich reports 24,767 total assets across duplicate groups. Manual review is off the table; triage requires tooling.

**Tool:** `tools/immich-dedup/classify.py` (added 2026-04-22 on branch `feat/immich-dedup`). Read-only classifier that buckets the `/duplicates` output by handling type (`bit_identical`, `heic_jpeg_pair`, `live_photo_pair`, `burst`, `screenshots`, `edge_case`). Writes nothing. Designed to be extracted into its own repo / submitted to the Immich community if v0 earns its keep.

**Steps:**
1. **Postgres + config backup FIRST** — before any destructive action, on UGREEN: `docker exec immich_postgres pg_dumpall -U postgres | gzip > /volume1/backups/immich-predoc-dedup/pg-$(date +%Y%m%d-%H%M%S).sql.gz`. Only rollback path if the dedup script misbehaves against 24k+ assets.
2. **Run `classify.py`** to get the bucket breakdown. Output is a markdown report.
3. **Decide handling per bucket:**
   - `bit_identical` / `heic_jpeg_pair` / `screenshots`: bulk-accept Immich's `suggestedKeepAssetIds` via `POST /api/duplicates/resolve` (or Immich's UI "Duplicate all" with a spot-check).
   - `burst`: bulk-accept with 5% human sample-check.
   - `live_photo_pair`: consider stacking via Immich's stack feature instead of deleting.
   - `edge_case`: human review. If this bucket is large, build a lightweight review UI (10 groups at a time) as a second phase of the tool.
4. **Execute to trash** (soft delete; 30-day recovery). Log every action.
5. **7-day soak in trash** — chance to spot regrets before hard delete.
6. **Empty trash, verify, declare Immich = master-of-record.**

**Exit criteria:** Immich dedup pass complete. Postgres + config backup taken. Library size documented in plan status log.

### Phase 3 — Empty iCloud Photos

**Goal:** iCloud drops from 200 GB → ~50 GB, photo space reclaimed, plan downgradable to 50 GB tier.

**Approach:** Stage migration. Do NOT just flip "Disable iCloud Photos" — that risks deleting masters on devices. Instead:

**Steps:**
1. On Mac: turn OFF "Optimize Mac Storage" in Photos preferences — force Mac to download full originals from iCloud (requires free space on Mac — Mac is 88% full, so this needs a parking spot)
2. Parking spot: export iCloud Photos originals directly to UGREEN over SMB or local Mac temp folder. Use Photos.app "Export Unmodified Original" OR `osxphotos` CLI for a scripted export.
3. Ingest exported originals into Immich using external library import
4. Run dedup again; verify no net-new unique photos vs. Phase 2 Immich state
5. Once all iCloud-originals confirmed present in Immich: go to iCloud.com → delete originals from iCloud Photos in batches (recently deleted auto-purges in 30 days; can empty manually)
6. Keep iCloud Photos enabled with only a curated recent subset (e.g., last 30 days) via Photos.app — or fully disable if not needed
7. Optionally downgrade iCloud plan from 200 GB → 50 GB once settled (saves money monthly; not required for plan)

**Exit criteria:** iCloud Photos ≤ 50 GB. All original photo data confirmed in Immich. Master-of-record clearly Immich.

**Risk:** Photo loss during migration. Mitigation: do not delete from iCloud until Immich has verified equivalent-or-better copy. Use `osxphotos` to export with metadata intact. Spot-check random photos across years.

### Phase 4 — Wipe Synology, expand + rebuild UGREEN as RAID 6, set up Synology as backup target

**Goal:** Second on-site copy of UGREEN's irreplaceable data AND upgrade UGREEN fault tolerance from 1-drive to 2-drive. Not offsite, but satisfies "2nd local copy" in 3-2-1. The Synology wipe/backup dual-purposes as migration staging area.

**Hardware additions (user committed 2026-04-22):**
- 2× Seagate IronWolf 12 TB drives (to match existing 4) — populates UGREEN's 2 empty bays, total 6 drives
- 5-port 2.5 GbE unmanaged switch (e.g., TP-Link TL-SG105-M2) — replaces 15-20yr old gigabit switch
- Cat 5e or Cat 6 patch cables for NAS-to-switch runs — Cat 5 in-wall runs may still cap at 1 GbE, but local patches are easy wins

**Steps (sequenced to use Synology as migration staging for the RAID rebuild):**

1. **Baseline SMART on both NAS.** UGREEN done 2026-04-22 (all 4 drives PASSED, 8900 hrs, zero errors). Synology drives still pending — 7-year-old drives must be checked via DSM UI or SSH before committing them as the backup target. If any drive is weak, descope or replace before continuing.
2. **Confirm nothing unique on Synology** (user already verified: "nothing special, all migrated to UGREEN").
3. **Install network switch upgrade first.** Swap in 5-port 2.5 GbE switch; replace UGREEN patch cable with Cat 6. Confirm UGREEN negotiates 2.5 GbE via `sudo /usr/sbin/ethtool eth0 | grep Speed`. Doing this before the big rsync avoids waiting on the 1 GbE bottleneck.
4. **Wipe Synology pool; rebuild as SHR-2** (2-drive fault tolerance). If Synology supports it, format pool as Btrfs to enable `btrfs send/receive` efficiency later.
5. **Full replication UGREEN → Synology — pre-migration safety net.** Methods:
   - rsync over SSH — cross-brand, simple, scriptable
   - `btrfs send/receive` — more efficient for Btrfs-to-Btrfs, requires Btrfs on Synology
   - Start with rsync for simplicity; revisit btrfs send/receive for ongoing deltas
6. **Verify the backup.** Sample-restore 10+ files from different tiers, verify hashes match source. **DO NOT proceed to step 7 without this verification — this copy is your only safety net during the rebuild.**
7. **Install 2 new IronWolf 12 TB drives** in UGREEN's empty bays. Verify via `lsblk`.
8. **Migrate UGREEN RAID 5 → RAID 6.** Two paths:
   - **(Recommended — safe) Destroy and rebuild:** tear down the RAID 5 pool; create 6-drive RAID 6 from scratch. Total pool re-init < 1 hour; data is safe on Synology. End state: clean 44 TB Btrfs volume1.
   - **(Faster but riskier) In-place mdadm reshape:** `mdadm --grow --level=6 --raid-devices=6 /dev/md1`. Multi-day operation; any disruption risks data loss. With a verified backup already staged, the safe rebuild is the right call.
9. **Restore Synology → rebuilt UGREEN.** Bulk rsync (or btrfs send/receive).
10. **Establish ongoing one-way replication** UGREEN → Synology. Nightly differential + weekly full-verify. Use systemd timers (cron binary absent on UGREEN).
11. **Replication tiers** (priority order for what gets backed up):
    - Tier 1: Immich library + Postgres + config (photos canonical)
    - Tier 2: **Docker volumes root** — `/volume1/docker/` covers NPM (SQLite + certs), Portainer, Sonarr/Radarr/qbittorrent configs, Immich Postgres, Plex metadata, Calibre, Gluetun, Overseerr. DB-heavy services benefit from pre-snapshot `pg_dump` / stop-container for consistency.
    - Tier 3: Mac backup volume on UGREEN
    - Tier 4: Obsidian vault (once Phase 5 done)
    - Tier 5: Plex media library (replaceable but nice to not re-acquire)
12. **Restore drill.** Pick a file, restore from Synology, verify integrity. Phase 4 isn't done until this passes.

**Exit criteria:**
- UGREEN running as 6-drive RAID 6, ~44 TB usable, 2-drive fault tolerance
- 2.5 GbE switch in place; UGREEN negotiating 2.5 GbE
- Synology holding current one-way backup of UGREEN Tier 1–3 data
- Restore drill passed
- Scheduled replication running unattended

**Risks:**
- 7-year-old Synology drives may fail under the heavy initial full-sync write load. Mitigation: SMART baseline first; if any drive is suspect, reduce pool size or replace before committing.
- UGREEN pool destroyed before backup verified = total data loss. Mitigation: **step 6 is non-optional.** Restore drill against the staged backup before step 8.
- Cat 5 in-wall runs can't reliably carry 2.5 GbE. Realistic outcome: local NAS-to-switch patch upgrades to 2.5 GbE; long in-wall runs to other rooms may still cap at 1 GbE. Plan for Cat 6 re-runs later if numbers disappoint.

### Phase 5 — Obsidian vault off iCloud Drive

**Goal:** Obsidian sync works on all devices (Mac, iPhone, iPad, Windows PC, optionally Boox), not tied to iCloud.

**Options analysis:**

| Approach | Cross-OS? | Real-time? | Cost | Setup complexity | Notes |
|---|---|---|---|---|---|
| **Obsidian Self-hosted LiveSync** (CouchDB on UGREEN Docker) | Yes | Yes | Free | Medium — Docker config + Obsidian plugin on each device | Best match: user already runs Docker/Portainer; Obsidian-native |
| **Syncthing** (UGREEN hub, clients on each device) | Yes (iOS needs Möbius Sync, $5 one-time) | Yes | ~$5 one-time for iOS app (not recurring; acceptable) | Low–medium | General-purpose; also solves other sync needs |
| **Git** (repo on Gitea/GitLab/GitHub) | Yes | No (manual push/pull; or git-autosync plugin) | Free | Low on desktop, medium on iOS (Working Copy) | Not real-time; conflict-prone on mobile |
| **Obsidian Sync** (official) | Yes | Yes | $4/mo | Trivial | Ruled out — new service |

**Recommendation:** **Self-hosted LiveSync on UGREEN.** Obsidian-native, real-time, free, already have the infra.

**Steps:**
1. On UGREEN: create CouchDB Docker container (follow Obsidian LiveSync setup guide)
2. Expose CouchDB through Nginx Proxy Manager (already in stack) with auth
3. Install "Self-hosted LiveSync" plugin on Mac Obsidian; configure; do initial one-time sync of vault
4. Move master vault OUT of iCloud Drive to a local Mac path (e.g., `~/Documents/Obsidian/`)
5. Repeat plugin install on iPhone, iPad, Windows PC
6. On Boox: evaluate — Obsidian on Boox works but LiveSync support is flaky; may fall back to read-only git pull
7. Delete vault from iCloud Drive once all devices verified on LiveSync

**Exit criteria:** Vault syncs real-time across Mac, iPhone, iPad, Windows PC. iCloud Drive no longer contains the vault.

### Phase 6 — Mac local-disk pressure and staging convention

**Goal:** Mac doesn't hit 100% during photo migration and ongoing creative work; clear convention for what lives where.

**Steps:**
1. Before Phase 3 export: free at least 200 GB on Mac by pushing previous-year DSLR/drone/Lightroom archives to UGREEN `~/Atlas`-adjacent path (NOT inside `~/Atlas/` — that's Google Drive's territory; use a separate workspace-ish path on UGREEN SMB share)
2. Formalize the staging convention documented in folder-schemas: "current year + optionally prior year on Mac, older to NAS"
3. Processed JPEGs intended for iCloud-accessibility — route via Immich's shared-album or external link mechanism, OR keep the user's original plan (processed JPEGs → iCloud, originals → Immich only). Decide during Phase 3.

**Exit criteria:** Mac < 80% full during migration. Older photo years on UGREEN. Convention documented in `folder-schemas/`.

### Phase 7 — iCloud cleanup (non-photo categories)

**Goal:** Bring iCloud's non-photo categories into a sustainable state.

**Steps:**
1. iCloud Backup (38.3 GB): keep iPhone + iPad backups; delete any backups from devices no longer in use. Check iCloud → Manage Storage → Backups for ghost devices.
2. Messages (7.3 GB): acceptable; keep.
3. Documents (4.1 GB): identify what's in iCloud Drive beyond Obsidian vault; migrate anything Atlas-appropriate to Google Drive, anything Syntheus to Syntheus Drive.
4. Post-Phase-3 + Phase-7: iCloud should be 45–55 GB total. Decide whether to downgrade to 50 GB tier (may not fit; 200 GB gives breathing room).

**Exit criteria:** iCloud ≤ 60 GB used.

---

## Risks

- **Photo loss during iCloud → Immich migration.** Mitigation: never delete from iCloud until Immich confirms presence; use scriptable export with metadata (osxphotos); spot-check samples across years; Phase 2 dedup verification pass.
- **Synology drive failure during backup initialization.** 7-year-old drives. Mitigation: SMART test first; reduce to healthier subset if needed; initial full-sync is write-heavy stress.
- **UGREEN RAID 5 fault tolerance = 1 drive only.** If a drive fails during Phase 4 (large sustained read for replication), risk compounds. Mitigation: do SMART check on UGREEN drives too before kicking off heavy replication.
- **Obsidian LiveSync conflict during initial multi-device onboarding.** Mitigation: do Mac-first one-time sync; verify single source; then bring other devices online one at a time.
- **Offsite gap remains after plan.** Accepted explicitly. Follow-up item.
- **iCloud Drive contains things other than Obsidian** that the user hasn't accounted for. Mitigation: audit iCloud Drive contents before declaring Phase 5 done.

## Open questions

- [ ] Does the Mac currently have enough headroom (~200 GB free target) to temporarily hold exported iCloud originals during Phase 3? If not, export directly to UGREEN SMB from the Photos app / osxphotos.
- [ ] What are the SMART health states of both UGREEN and Synology drives? Plan execution assumes "acceptable" — needs verification before Phase 4.
- [ ] Keep iCloud Photos on as a curated subset post-migration, or disable entirely? User's stated preference: "processed JPEGs in iCloud accessible anywhere" → keep on, curate.
- [ ] Boox Palma 2 Obsidian access: required, or acceptable to stay read-only via git pull?
- [ ] Any data currently ONLY on Windows PC that needs a backup path (video editing project files, 3D models)? User listed these as uses; unclear if durable.
- [ ] UGREEN SSD pool (1 TB idle, Basic, no redundancy): use for LiveSync CouchDB / Immich Postgres / Docker volumes to improve perf? No redundancy = must be replicated to HDD pool if used.
- [ ] Plan to downgrade iCloud 200 GB → 50 GB tier post-cleanup, or keep 200 for breathing room?

## Sequencing summary

```
Phase 1 (iPhone → Immich)     [DO FIRST — risk reduction]
   ↓
Phase 2 (Immich dedup)
   ↓
Phase 3 (iCloud Photos → 0)   [requires Phase 6 for Mac headroom]
   ↓ parallel with
Phase 5 (Obsidian LiveSync)   [independent of photo work]
   ↓
Phase 4 (Synology = UGREEN backup)  [can begin during Phase 2 if drives SMART-pass]
   ↓
Phase 7 (iCloud non-photo cleanup)
   ↓
[Offsite gap — separate future plan]
```

## Status log

- 2026-04-22 — Plan drafted from session inventory and answered blocking questions
- 2026-04-22 — Phase 1 started: iPhone + iPad Immich backup setup
- 2026-04-22 — Phase 1 complete: iPhone backup active, iPad deferred, public URL hardened, Immich iGPU enabled
- 2026-04-22 — Phase 2 scale measured: 24,767 total assets in duplicate groups. Phase 2 tooling drafted: `tools/immich-dedup/classify.py` on branch `feat/immich-dedup`. Framed as a community-submittable improvement to Immich dedup workflow, not just a personal utility.
