# Atlas Dashboard — Cross-device storage visibility + AI-assisted planning

**Status:** Idea. Not committed to build.
**Origin:** 2026-04-22 session while consolidating personal data across UGREEN NAS, Synology, Mac, PC, iPhone, iPad, iCloud, and Google Drive. The planning itself was high-quality once full context was captured — but capturing that context took two hours of interactive Q&A. An ordinary, less patient user would have abandoned the effort halfway through.

---

## Problem

Most people's data is scattered across 5–10 devices and 2–3 cloud services. They don't have a single mental model for "where does my stuff actually live." Symptoms:

- iCloud fills up and photo backup silently stops; photos accumulate undurably on the device
- A vendor changes plans or raises prices and migration feels impossible
- A drive fails and they discover half their "backup" was never complete
- They want to consolidate or simplify and can't figure out where to start
- They ask an AI for help and spend most of the conversation answering "what hardware do you have, what's on it, what's your current state?"

Existing tools address slices:
- DaisyDisk / WinDirStat — per-device visualization, no planning
- Time Machine / Windows Backup — single-vendor, single-machine
- Vendor cloud apps (iCloud, Google Drive, Dropbox) — trap within their own ecosystem, no visibility across
- Duplicati / Restic / Syncthing — execution tools, require the user to already have a plan
- Backup-as-a-service (Backblaze, IDrive) — opinionated backup, not a full data-operations view

**Nothing I know of combines:** (a) cross-device + cross-cloud inventory, (b) a readable visualization, (c) an AI planning layer that speaks the user's goals, (d) runs with privacy-first defaults.

---

## Key insight from this session

AI reasoning quality scales sharply once it has:

1. **Hardware inventory** — what devices exist, their capacity, CPU/GPU/RAM, network fabric
2. **Storage inventory** — what's used where, at folder-summary granularity (not every file)
3. **Service inventory** — what apps are running where, what data each owns
4. **Network + redundancy posture** — how devices connect, what's redundant vs single-point-of-failure
5. **Explicit goals + constraints** — "unblock iCloud", "no new hardware", etc.

Without this, every recommendation is generic. With this, the recommendations become specific, actionable, and contextually correct (e.g., "your iGPU is present but unused — wire it into Immich" vs. "consider hardware acceleration").

**Gathering this context is the real work.** Once captured, the planning is fast. The product opportunity is in closing the context-gathering gap for users who won't spend two hours answering questions in a terminal.

---

## Vision — what the product does

A dashboard that:

1. Runs lightweight agents on the user's devices (opt-in, per-device installs)
2. Aggregates inventory locally (not shipped to a third-party cloud by default)
3. Renders a single-pane view of the whole ecosystem: capacity, usage, duplication, backup coverage, gaps vs. a 3-2-1 target
4. Offers a chat/planner mode where the user states a goal ("free iCloud", "set up offsite", "consolidate photos") and the AI produces a specific, step-by-step plan against their actual environment
5. Optionally generates the config / scripts / commands to execute the plan (with preview + approval)

The experience target: a non-technical user who's been getting "iCloud almost full" warnings for a year sees their whole stack laid out in 5 minutes, picks "help me unblock iCloud," and walks through a guided migration.

---

## Design inspiration — DaisyDisk

DaisyDisk for macOS has sold $9.99 copies for 15+ years by doing one thing exceptionally well: a **sunburst visualization** of disk usage that answers "where did my storage go?" in 30 seconds. The entire product is a single, tightly-scoped UX bet, and it works. Worth understanding deeply before designing anything adjacent.

### What DaisyDisk gets right (to preserve)

- **Sunburst diagram.** Hierarchical, color-coded, size-proportional. Folders are colored petals, files are gray. Click to drill in, breadcrumbs to back out. Spatial pattern recognition — the brain grasps "that big red wedge is eating my disk" instantly, without parsing a table.
- **Sub-minute scans via cached metadata.** The visualization feels alive, not like a batch report.
- **Hover for details, drag-to-delete for action, Quick Look for preview.** Low-friction inspection and cleanup in the same surface.
- **One-time $9.99 pricing.** No subscription fatigue. Users pay once and recommend to friends — a social graph effect that subscriptions suppress.
- **Scope discipline.** It does one thing (local disk analysis) and does it beautifully. Never grew into "cloud backup manager" or "system optimizer."

### What DaisyDisk explicitly doesn't do (the gap to fill)

- Single device only — no cross-Mac, no iOS, no NAS, no cloud
- No concept of "this file also exists over there" (duplication detection across surfaces)
- No backup-coverage awareness (every wedge is equal — no "this is your only copy" warning)
- No planning layer ("I see the problem, now what?" is left to the user)
- No projection over time ("you'll be out of space in N months at this rate")

---

## Extending DaisyDisk's model to a cross-device hub

Preserve the sunburst as the core UX. Add:

### Surface picker

Dropdown or tab row above the diagram: "UGREEN NAS", "MacBook Pro", "iPhone", "iCloud", "Google Drive", plus an aggregate **"Everything"** view that flattens all surfaces into a single unified sunburst with color-coded outer rings indicating origin device/cloud. The DaisyDisk visual grammar extends naturally — one more dimension encoded by the outer color.

### Cross-surface duplication overlay

Toggleable. When on, wedges representing content duplicated on ≥2 surfaces get a distinct visual marker (cross-hatch pattern, brighter border). Click to see the full set of locations: "this 40 GB 2019 photo archive lives on Mac `~/Pictures/2019/` AND UGREEN `/volume1/Media/photos/2019/` AND iCloud Photos." The user picks where it should stay; the dashboard executes the plan (or generates the scripts).

### 3-2-1 coverage layer

Each wedge scored and shown via outer-border color:

- ✓✓✓ green border — 3 copies, 2 media types, 1 offsite
- ✓✓ yellow border — 2 copies, no offsite
- ✓ red border — single copy — **this is what gets lost in a drive failure**
- ? gray border — unknown / not yet scanned

At-a-glance: "how much of my life is single-copy?" The red border is the call to action.

### Goal-aware highlighting

Chat-driven or menu-selected. User says "free up iCloud" → sunburst highlights candidate wedges (duplicates with safe copies elsewhere, regenerable caches, replaceable media). Other wedges dim. Side panel shows:

- Total reclaimable storage
- The step-by-step plan
- A preview of what will be deleted / moved / migrated, with explicit per-step confirmation

### Growth trajectory

Second view mode: sparklines inside each wedge showing "size over time" instead of current state. "Your Photos library grew 4 GB/month for the last year. At this rate you'll hit 200 GB iCloud in 7 months." Turns the tool from reactive (after the alarm) to predictive (before the alarm).

### Coverage timeline

When a backup last touched each wedge. Detects "backup said it's working but this folder hasn't been copied since 2023." That's the failure mode that eats people's data when a drive fails.

---

## Per-platform agent design

Each agent is read-only, permission-scoped, and ships only summary data (sizes, paths, metadata) — not file contents.

### macOS / Windows / Linux desktop

- Native menubar app (electron/tauri or fully native)
- Reads `~/Documents`, `~/Pictures`, `~/Movies`, `~/Music`, mounted drives
- Reports per-folder: size, last-modified, file-count distribution by extension
- Optional opt-in: file-path hash inventory for cross-device dedup detection (SHA-256 of path + size, not content)
- Watches for changes; periodic resync rather than real-time

### iPhone / iPad

- Native iOS app using PhotoKit (Photos framework), Files app, and built-in storage API
- Reports: Photos library size breakdown (originals vs. optimized, Live Photos, RAW, video), Files app totals, top-level iCloud Drive folders
- Cannot see other apps' sandboxed containers — that's an iOS limitation, not a bug to solve
- iCloud Photos specifically: distinguish "originals on device" vs "cloud-only" vs "optimized cached"

### NAS (Synology, UGREEN, QNAP, TrueNAS, generic Linux)

- Docker container or systemd-installable agent (SSH access can be an alternative for power users)
- Reads — capacity and layout:
  - `lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE` — full disk/partition tree
  - `df -hT` — mount state + filesystem types
  - Btrfs: `btrfs subvolume list`, `btrfs filesystem df`, snapshot inventory
  - ZFS: `zpool status`, `zfs list`
  - LVM: `pvs`, `vgs`, `lvs` — identify caches, thin pools, weird configurations
  - MD RAID: `cat /proc/mdstat` — detects degraded arrays, rebuilds in progress
- Reads — health (the piece most invisible to users):
  - `smartctl -a /dev/sdX` for each drive — model, serial, power-on hours, reallocated/pending/uncorrectable sectors, UDMA CRC errors, temperature
  - Flag drives >40,000 hours (approaching 5-year mark), any non-zero Reallocated_Sector_Ct, Current_Pending_Sector, or Offline_Uncorrectable
  - Detect asymmetric wear patterns (one drive dramatically more written/read than siblings — early indicator of cache hotspot or pending failure)
- Reads — hardware capability:
  - `cat /proc/cpuinfo` — CPU generation (relevant for hardware acceleration capability)
  - `free -h` + `cat /proc/meminfo` — RAM total, swap in use (detects memory pressure)
  - `ls /dev/dri/`, `lspci | grep -iE "vga|display|3d"` — iGPU/discrete GPU presence
  - `ethtool <iface>` per physical NIC — real negotiated speed (not wishful thinking)
- Reads — power resilience:
  - `upsc <ups>` if UPS configured — battery charge, runtime estimate, load, status (OL/OB/LB)
  - Flag systems without UPS → database/SQLite corruption risk on power loss
- Reads — running services:
  - `docker ps`, `docker stats --no-stream` for RAM/CPU per container
  - `docker inspect <container>` → detect `/dev/dri` mapping, device cgroup rules, resource limits
  - Detect service type (Plex, Immich, Postgres, MariaDB, NextCloud, Sonarr, etc.) and where its data volumes live
  - Detect misconfigurations: unused iGPU passthrough, services doing heavy work on spinning rust when cache pool is idle, etc.
- Reads — network topology hints:
  - Physical NIC speed (not virtual bridge "speed" which is cosmetic 10 Gbps on all)
  - Tailscale presence, exit-node status, connected peers
  - DDNS subdomain hints from reverse-proxy configs (`/etc/nginx/`, NPM SQLite, Caddyfile)
- Reads — package manager state:
  - `apt list --installed` / equivalent — detect missing expected tools (smartmontools, intel-gpu-tools, rsync)
  - Flag orphan/broken-dep states without recommending auto-fix (often vendor-customized NAS OS artifacts)

### Cloud services

- OAuth connectors, read-only scopes where possible
- Google Drive, iCloud (via CloudKit where permissions allow), Dropbox, OneDrive, Google Photos
- Reports per-service: total used, breakdown by category (Photos / Drive / Backups / etc.), file-count summary
- Does not pull file contents unless the user opts into specific actions

### Network / router

- Optional: LAN-scan for NAS discovery (with user consent)
- Speedtest integration for upload/download baseline (the number that gates cloud-backup feasibility)

---

## Why comprehensive telemetry matters — evidence from a real session

This dashboard concept was triggered by a ~2 hour session where an AI + user iteratively discovered the user's NAS state. The specific information that changed the plan at each step — none of which a storage-size-only tool would have surfaced:

| Data point discovered | How it changed the plan |
|---|---|
| CPU is 12th-gen Intel with UHD iGPU | Enabled hardware acceleration for Immich ML, cutting face/CLIP/thumbnail times meaningfully |
| 8 GB RAM with 3.2 GB swap in use | Initial concern about adding services; later fact-check showed active container RAM was ~2.1 GB — safe to proceed but tight |
| Btrfs on /volume1 | Changes Phase 4 backup tool choice (btrfs send/receive instead of rsync for Btrfs-to-Btrfs paths) |
| NVMe LVM write-back cache already fronting HDD pool | Reframed "move to SSD for speed" — most hot data is already SSD-cached; moved focus to which workloads actually benefit from dedicated SSD pool |
| UPS present and auto-shutdown configured | Removed a risk class from planning (SQLite/Postgres corruption on power loss) |
| Unknown 3.6 TB USB drive with legacy Plex content + Synology metadata | Revealed a candidate for rotating-offsite storage that would otherwise have been missed |
| NIC speeds negotiated at 1 GbE, cabling is Cat 5 from early 2000s | Reframed backup throughput expectations; surfaced a high-leverage future upgrade (2.5 GbE switch + Cat 6) |
| SMART baseline on 4 drives: 8,900 PowerOnHrs, 0 reallocated sectors | Confirmed Phase 4 replication source is safe; deferred the Synology SMART pass (7-yr-old drives = higher risk) |
| Immich container running as UID 999, GID 10, no /dev/dri mapped | Concrete compose diff to enable iGPU; verified supplementary groups 44 (video) + 105 (render) post-change |
| Plex container already had /dev/dri mapped (PlexHW named for reason) | Found the asymmetry between services with and without hardware accel; only Immich needed the fix |
| Home IP is dynamic (Xfinity), Access List hardcodes current IP | Surfaced an ongoing operational brittleness; added "IP rotated" recipe to runbook |

Every one of these was the difference between a generic recommendation and a specific, correct one. The dashboard's job is to gather all of this automatically on install, so users get specific-correct advice from the first conversation — not after two hours of Q&A.

---

## AI planning layer

The AI has access to the aggregated inventory but NOT raw file contents. It generates plans scoped to the user's goals + constraints.

Modes:

- **Observation** — "explain what I have"
- **Gap analysis** — "where's my 3-2-1 coverage weak? what's not backed up anywhere?"
- **Goal-directed planning** — "I want to free iCloud" or "I want offsite"
- **Migration scripting** — "here's the specific plan, here are the commands to execute it, approve each step"

Every suggestion carries explicit data: "You have X GB on iCloud. Y GB of that is photos. Z GB of those are duplicated in your Immich library. Freeing them reclaims Y GB."

---

## Privacy model

Defaults that matter for trust:

- All inventory processing happens locally (on-prem NAS or user's laptop)
- Agents communicate via user's own network (Tailscale / LAN / local loopback)
- Cloud-service OAuth tokens stored encrypted on user's device, not centralized
- AI planning can be done via local model (Ollama, Lemonade) OR user's own API key — not a shared service
- Opt-in telemetry only; never ship file paths or filenames off the device without explicit consent
- File contents never leave the device; only sizes and metadata

This is the real differentiator vs. any venture-backed product that would want centralized telemetry for model training.

---

## MVP cut

Build the absolute minimum that demonstrates the loop:

1. **Mac menubar agent** — scans `~/` for size breakdown, reports to local dashboard
2. **iPhone companion app** — Photos breakdown + iCloud status
3. **Google Drive + iCloud OAuth connector** — pulls usage breakdown
4. **Web dashboard (local-only)** — single-page view that aggregates the three sources
5. **AI chat integration** — user connects their own Claude/OpenAI key; dashboard exports the inventory as context when asking for planning help

That's shippable in weeks, not months. The NAS agent, Windows agent, and advanced features come in v2+.

---

## Competitive landscape notes

The space has three existing shapes, none at the intersection we're targeting.

### Local visualizers (the UX benchmark, single-surface only)

- **DaisyDisk** (Mac) — see "Design inspiration" above. Single device, no cloud.
- **GrandPerspective / Disk Inventory X** (Mac) — treemap variant. Similar ethos.
- **WinDirStat / Filelight** (Windows / Linux) — platform equivalents.
- **Ente Photos** — privacy-focused photo cloud. Solves photos-only vertically.
- **Immich** — self-hosted photo backup. Nails photos; leaves the rest to the user.

### Vendor-locked NAS dashboards (strong within one ecosystem, blind outside it)

- **QNAP AMIZcloud** — central dashboard for CPU, memory, pools, backup jobs across all your QNAP NAS. QNAP-only.
- **Synology Drive Admin Console** — file access and activity monitoring across Synology DSM devices.
- **Ubiquiti UniFi Drive (UNAS)** — centralized NAS dashboard inside the UniFi ecosystem.

These are well-built for what they do. But if you're mixed-vendor (UGREEN + Synology, in our reference case), or if you want iPhone or iCloud in the same view, they don't help. They also don't plan — they report.

### Cloud-aggregation tools (cloud-only, mostly technical)

- **RcloneView** — GUI over rclone for multi-cloud sync/compare. Requires rclone knowledge.
- **CloudFuze Manage** — enterprise multi-cloud management. Enterprise pricing.
- **FilesVerse / All Cloud Hub** — unified browse across cloud drives. Doesn't see local.
- **NextCloud / Seafile** — file-sync suites. Not planning tools.
- **Backblaze / IDrive / Carbonite** — backup SaaS. Opinionated about what to back up; not about what you should do overall.

### The gap this idea targets

None of the above combines:
- **Cross-vendor + cross-surface** (multiple NAS brands + desktops + mobile + clouds)
- **DaisyDisk-caliber visualization** (spatial pattern recognition, not tables)
- **3-2-1 backup-coverage overlay** (which data is actually at risk)
- **AI planning layer** (goal-directed, not just inventory)
- **Privacy-first default** (inventory stays local)

That's the opening.

### Historical attempt

- **Cozy Cloud** (defunct) — tried to be a personal-data operating system; closed. Confirms the hard part is traction + sustained engineering investment, not vision.

---

## Pricing model learning from DaisyDisk

$9.99 one-time for a sharp, single-purpose tool is a proven model. Subscription isn't the only path — and for a privacy-first product, it may actively hurt trust.

Possible shape:

- **Free tier:** one device + one cloud + BYO AI key. Good enough to evaluate and for light users.
- **Paid one-time ($49–$99):** unlimited agents, cross-surface dedup, 3-2-1 analyzer, 1 year of updates, offline use. Priced at the upper end of DaisyDisk but reflecting real per-user development cost.
- **Optional subscription ($5/mo):** managed AI backend (no BYO key), continuous growth tracking, privacy-preserving aggregate telemetry (opt-in, for the user's own devices only — no data pooling). Subscribers pay for convenience, not capability.

Many users stay on free or one-time and are happy. Subscribers pay for managed infrastructure, not to unlock features. That preserves the "DaisyDisk feeling" — pay once, use forever.

---

## Risks and open questions

- **Privacy vs. AI quality tradeoff.** Better planning usually needs more context; more context needs more scanning. Hard to avoid a middle ground that feels like surveillance to users who don't trust AI yet.
- **iOS limitations.** Apple restricts what a third-party app can see. The iCloud breakdown that was trivial to get in the iOS Settings app is not easy for an app to replicate programmatically.
- **Cloud API terms.** Some providers restrict programmatic read access to aggregate stats or charge for it. Need to validate per-provider.
- **Who pays.** Classic freemium (free for inventory + basic planning, paid for execution / unlimited agents / cloud AI backend)? Or self-hosted FOSS with optional managed cloud? Different users, different monetization. Likely: OSS for the agents + dashboard, paid-optional for the managed AI and sync service.
- **Does the average user want to install agents on 5+ devices?** Friction is real. MVP could be "just Mac + iPhone + one cloud" and already deliver most of the value.
- **Update / maintenance burden.** Every OS update, Apple or cloud provider can break a source. Ongoing engineering cost is non-trivial.

---

## Relationship to life-atlas

This idea is the natural evolution of the `life-atlas` pattern into software. Life-atlas today is a pattern + documentation + scripts for one person's ecosystem. The dashboard idea is: can the pattern generalize into something others can install and benefit from with orders of magnitude less effort.

For now: finish the personal ecosystem, capture what the pattern generalizes into (folder-schemas, device-schemas are already doing this), then revisit this idea as an optional future direction.

---

## Next steps if this idea survives a week

- Validate with 3–5 people who roughly fit the "iCloud overflowing, want help, not deeply technical" profile. Would they install and trust an agent like this?
- Prototype the Mac agent: menubar app, reads `~/`, exports JSON, dashboard renders it. Takes maybe 1–2 weekends to produce something demonstrable.
- Check per-provider cloud API feasibility (iCloud is the hardest; Google Drive is easy).
